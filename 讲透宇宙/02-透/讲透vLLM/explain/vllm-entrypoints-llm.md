# vllm/entrypoints/llm.py — LLM：离线批量推理的同步门面

> 源码：`vllm/entrypoints/llm.py`（914 行）｜entrypoints 已目录化：common/generate/pooling/rl 四路 mixin｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

位于 **entrypoints（服务入口层）**。`LLM` 是**离线批量推理的同步门面**：一次构造（加载模型+分配 KV cache），随后 `generate()/chat()` 一把梭整批 prompt。2026-09→10 两个结构级变化：一是 entrypoints 目录化后 mixin 从三件套变**四件套**——`class LLM(BeamSearchOfflineMixin, PoolingOfflineMixin, RLOfflineMixin, OfflineInferenceMixin)`（vllm/entrypoints/llm.py:62-64），新面孔 `RLOfflineMixin`（:35）把旧版直接挂在 LLM 上的 weight transfer 系列收编并扩充；二是引擎侧换代——它持有的 `LLMEngine` 如今自称 "Legacy LLMEngine for backwards compatibility"（vllm/v1/engine/llm_engine.py:55），内部同样构建 `EngineCoreClient`（vllm/v1/engine/llm_engine.py:116）。在请求生命周期中它是"用户 API + 驱动循环"双角色：`_run_engine` 自己 step 到全部完成。

## ② 内部结构

`__init__`（vllm/entrypoints/llm.py:177）四段：**参数归一化**——顶层 kwargs 拼 `EngineArgs`（:295-336），dict 自动转 config（`_make_config` :257，`is_init_field` 过滤）；`compilation_config` 收 int 时转 `CompilationConfig(mode=...)`（:265-268）；`kv_transfer_config` dict 经 pydantic 校验转 `KVTransferConfig`，失败给完整报错（:235-252）；`worker_cls` 为类对象时 cloudpickle 序列化（:228-233）。**防御检查**——单进程 `data_parallel_size>1` 报错并指向多进程示例，但 **external_launcher 与 TPU 豁免**（:281-293，旧版无豁免）。**引擎创建**——`LLMEngine.from_engine_args(usage_context=UsageContext.LLM_CLASS)`（:341-343）。**句柄缓存**——`model_config/renderer/input_processor` + `renderer.warmup`（:354-358）；`renderer_num_workers>1` 时明确警告：离线 `LLM` 走同步 renderer 路径、多模态预处理串行，线程池只有 `vllm serve`/`AsyncLLM` 的异步 renderer 才消费（:364-373，issue #42901）。

新参数面孔：`runner`/`convert`（:181-182，RunnerOption/ConvertOption 进 ModelConfig）、`spec_method/spec_model/spec_tokens` 顶层别名（:219-221）、`attention_config` 等四个 config 参数（:210-214）、`kv_cache_memory_bytes` 与 prefetch offloading 四参（:198-201/:215）。

## ③ 外部连接

- **依赖**：`engine/arg_utils.py`（EngineArgs）、`v1/engine/llm_engine.py`（LLMEngine→EngineCoreClient→EngineCore/executor）、`config/*`、`renderers`（ChatParams/chat_utils :42-47）、`outputs.py`。
- **mixin 四路**：骨架 `OfflineInferenceMixin`（vllm/entrypoints/common/offline.py:50，含 `_add_completion_requests`:304/`_run_completion`:340/`_run_chat`:365/`_render_and_add_requests`:539/`_run_engine`:589）；`PoolingOfflineMixin`（entrypoints/pooling/offline.py）管 embed/classify/score；`BeamSearchOfflineMixin`（entrypoints/generate/beam_search/offline.py）；**`RLOfflineMixin`**（vllm/entrypoints/rl/offline.py:11）提供 weight transfer 八连——`init_weight_transfer_engine`:12/`shutdown_weight_transfer_engine`:29/`start_weight_update`:33/`start_draft_weight_update`:37（新，可单独更新投机解码 draft 模型）/`update_weights`:41/`finish_weight_update`:56/`update_weight_version`:62/`get_weight_version`:66。
- **被依赖**：`vllm/__init__.py:21` 以 `".entrypoints.llm:LLM"` 延迟导出；顶层门面无人反向依赖。不 import torch.distributed——并行细节全被引擎封装。

## ④ 数据流

```
prompts（str/TokensPrompt/多模态 dict）
  → renderer 同步预处理（多模态串行 :364）
  → _add_request → engine.add_request（自动连续 request id）
  → _run_engine @vllm/entrypoints/common/offline.py:589:
       while llm_engine.has_unfinished_requests():
           step_outputs = llm_engine.step()   # 引擎内 batching/调度/PagedAttention
           收集 finished 输出 + tqdm 双速统计
       sorted(outputs, key=int(request_id))  # 与输入同序靠 id 排序实现
```

`LLMEngine.step()`（vllm/v1/engine/llm_engine.py:319）从 `engine_core.get_output()` 拉 `EngineCoreOutput` 再交 output_processor——LLM 与 AsyncLLM（async_llm.py:93，经 `make_async_mp_client`:193 起后台 EngineCore 进程）的真正分野只在 client 形态：同步直连 vs 异步多进程，EngineCore 内核共享。`enqueue()/enqueue_chat()`（:483/:718）把"入队"与"驱动"拆开，配合 `sleep(level=0)` + `wake_up(tags=["scheduling"])` 可保证全部入队后才开始调度；`wait_for_completion`（:548）带 overload 类型收窄。

## ⑤ 设计决策

1. **门面薄、引擎厚**：llm.py 里没有一个调度/显存决策；连 weight transfer 都只是 `collective_rpc` 转发（rl/offline.py 全文即证）。离线/在线、同步/异步的差异全部收在 entrypoint 与 client 层。
2. **docstring 滞后是活教材**：:172-173 仍写 "For online serving, use AsyncLLMEngine"——实际类是 `AsyncLLM`，`AsyncLLMEngine` 已不存在；读文档不如读 `__init__.py` 导出表。
3. **sleep/wake 分级 + 精细释放**：level 0 暂停调度、1 权重下 CPU 弃 KV、2 全弃（:839-861）；新增 `release_kv_cache_memory()`（:864）允许 level 0 后单独释放 KV 物理显存，`wake_up(tags=["kv_cache"])` 恢复时 kept 请求靠重算——服务端换模型/腾显存的原语族。
4. **运维面持续加宽**：`collective_rpc`（:573，控制面广播）/`apply_model`（:604，在 worker 的 nn.Module 上直接跑函数，RL 框架取 logits 改权重）/`get_metrics`（:890，Prometheus 快照）/`reset_prefix_cache(reset_running_requests, reset_connector)`（:832）/`reset_mm_cache`（:406）。
5. **默认值即立场**：`disable_log_stats` 强制 True（:225-226，离线不要周期日志）；`gpu_memory_utilization=0.92`（:196）；`__repr__` 经 `collective_rpc("get_model_inspection")` 取回缓存（:903-914），避免重复 RPC。
6. **runner 语义替代 task 探测**：`generate/enqueue/chat` 开头都硬查 `runner_type=="generate"`（:461/:516/:691）并提示 `--runner generate`——pooling 模型走 `PoolingOfflineMixin`，职责切分从运行时探测变为构造期声明。

## ⑥ 新人提示

- 阅读线：`generate()` :417 → `_run_completion`（vllm/entrypoints/common/offline.py:340）→ `_run_engine`:589 一条线理解离线推理；别在 llm.py 里找 batching——它在 EngineCore。
- 易混淆：`LLM` 不是 nn.Module，`llm.llm_engine` 才连引擎；"输出与输入同序"是 `_run_engine` 末尾按 request_id 排序的结果，不是引擎保证。
- RL 集成（verl 等）入口全在 RLOfflineMixin，且 draft 权重可独立更新（`start_draft_weight_update`）；传大对象走 `apply_model` 时记得先搬 CPU（:608-612 警告）。
- `LLM(...)` 收到的大量 kwargs 其实是 EngineArgs 直通参数——查默认值去 `engine/arg_utils.py`，本文件只补了离线专属的 6 个 config 转换。
- 想 swap 引擎做测试：`LLM(worker_cls=...)` 类对象自动 cloudpickle（:228）；`LLM.from_engine_args(engine_args)`（:380）可从现成 EngineArgs 构造。
