# explain-09 · model/scheduler——自研连续批处理调度器（transformers 引擎内核）

## 角色定位

`xinference/model/scheduler/`（batch.py 269 行 + request.py 259 行 + core.py 28 行）是 Xinference 为 **transformers 引擎**自研的 continuous batching 内核——vLLM/SGLang 自带调度，而裸 transformers 没有批处理能力，这套三件套把"逐请求串行推理"改造成"FCFS 合批 + 每步迭代调度 + KV cache 裁剪"。`BatchScheduler`（`scheduler/batch.py:32`）是调度主体，`InferenceRequest`（`scheduler/request.py:20`）是贯穿始终的请求状态对象，`core.py:25-28` 定义四个哨兵字符串（DONE/ERROR/ABORT 的流式与非流式旗标）用于在 asyncio Queue 里传递控制信号。注意它不是通用组件：只有 `model/llm/transformers/core.py:426-428` 实例化它（图像侧另有 Flux 专用调度器 `model/image/stable_diffusion/core.py:415`）。

## 内部结构

`BatchScheduler` 的状态就五件（`batch.py:34-40`）：`_waiting_queue`/`_running_queue` 两个 deque、模型引用、`_id_to_req` 请求索引、`_abort_req_ids` 取消集合，外加 `_run()` 后台任务。调度核心 `_handle_request()`（`:69-106`）每步组装一批：先从 running 队列取存量请求（`:75-80`），空位再从 waiting 补新请求——**批内 prefill 兼容性检查**是亮点：模型若提供 `get_batching_prefill_compatibility_key`，不同 key 的请求不许同批（`:84-99`），注释解释了动机："processor 会对整批应用同一份 chat-template kwargs，混批会把 tools/reasoning 设置泄漏到别人的请求里"。注意返回顺序是 `waiting_list + running_list`——新 prefill 放前面，保证 KV cache 布局里新请求追加在尾部。`step()`（`:149-221`）是完整的一轮：调 `self._model.batch_inference(req_list)`（模型侧钩子，transformers 实现在 `transformers/core.py:982-989`：prepare→`batch_inference_one_step`→结果处理）；随后把流式请求本步产生的 completion 逐个塞进各自 Queue（`:162-166`）；未停的请求回 running 队列（`:168-169`），停了的按四态收尾——aborted 放 ABORT 旗标（`:181-188`）、正常停放结果或 DONE 旗标（`:190-194`）、参数校验失败放 ERROR（`:195-203`）。关键尾部动作：若有请求完成且批未空，调 `build_reduced_kv_cache` 把 KV cache 沿 batch 维裁掉已完成的槽位（`:205-219`，transformers 实现优先用 `batch_select_indices` 原位裁剪，`transformers/core.py:991-1004`）。

## 外部连接

模型侧契约四个钩子（全部由 transformers 引擎实现）：`get_max_num_seqs()`（`transformers/core.py:780-781`，读 pytorch_model_config）、`batch_inference(req_list)`（`:982`）、`build_reduced_kv_cache(cache, skipped_indexes)`（`:991`）、可选 `get_batching_prefill_compatibility_key(req)`。上游是 ModelActor 的 chat/generate 通道（`core/model.py` 调 `add_request`，`batch.py:223-239`：request_id 查重抛 KeyError，然后入 waiting 队列）；abort 通道对应 `abort_request`（`:241-252`，未找到返回 NOT_FOUND 的 no-op 语义）。`InferenceRequest` 同时是数据包和状态机：prompt/full_prompt 双层（原始 messages vs 套模板后，`request.py:30-33`）、`_new_tokens`/`_kv_cache`/`completion` 三块推理状态、`future_or_queue` 二象性（流式是 asyncio.Queue、非流式是 Future，`:74-76` 注释），`get_generate_configs`（`:224-259`）把 sanitized config 一次性拆成九元组（max_tokens/stream_interval/stop 集合/温度/惩罚/top_p/top_k），还带了 `functools.lru_cache`——同一 eos 下重复查询零开销。

## 数据流

一个流式请求的生命周期：ModelActor 收到 chat → 构造 `InferenceRequest`（带 request_id 进 `_id_to_req`）→ `add_request` 入 waiting → `_run` 循环每 10ms 一拍（`batch.py:254-259`）→ `_handle_request` 合批（waiting 前置）→ `batch_inference` 走一步 prefill 或 decode（新请求此步做 tokenize+首 forward，is_prefill 翻转）→ 结果回填 `req.completion` 列表 + `append_new_token` → step 把 completion 转成 chunk 推 Queue → 循环直到 stopped（stop 条件由 `get_generate_configs` 的 stop_token_ids/stop_str/max_new_tokens 在模型侧判定）→ DONE 旗标收尾 → 下一步 `build_reduced_kv_cache` 回收槽位。失败路径双层：batch 级异常走 `_fail_batch_requests`（`:115-147`，把整批请求移出队列、逐个 set_exception 或推 ERROR 旗标、清 KV 引用，注释强调"模型或 cache 故障不能让调用方永远等下去"）+ `_empty_cache` 清显存；调度器自身的意外错误由 `_run` 的兜底 except 接住并继续循环（`:263-269`）——调度器永不退出是设计不变量。

## 设计决策

①**10ms 固定节拍**而非事件驱动唤醒：简单压倒极致延迟，decode 步本身毫秒级，轮询开销可忽略；②**请求对象承载一切**：不搞独立的 batch 结构体，批就是"本步凑出来的请求列表"，KV cache 直接挂在各请求上（`r.kv_cache`），批缩容后统一换新引用（`:218-219`）——这使"批"成为瞬时概念，崩溃恢复粒度天然是请求级；③**prefill 兼容性 key 防串扰**（`:94-99`）是踩坑后的补丁：chat-template 是批级操作，混批等于给所有请求套同一模板参数；④**哨兵字符串而非消息类型**（`core.py:25-28`）：Queue 里混传文本 chunk 与控制旗标，靠字符串前缀区分——不优雅但让转发层零改动。

## 新人提示

改 transformers 引擎的批行为先读 `batch_inference_one_step`（`transformers/utils.py`）再看本文件——调度器只管"何时组批/怎么收尾"，注意力计算全在模型侧。两个易错点：`stopped` 与 `aborted` 是包含关系（aborted 必 stopped，`request.py:54-56` 注释）；流式请求的 completion 是"本轮全部 chunk"的列表语义（`:70-72`），step 清空后模型侧继续 append。调试 batch 维 bug 时记住批内顺序 = waiting(新) 在前 + running(旧) 在后，KV cache 的 batch index 与这个顺序一致——`stopped_batch_indexes` 的 idx 就是 `req_list` 下标。
