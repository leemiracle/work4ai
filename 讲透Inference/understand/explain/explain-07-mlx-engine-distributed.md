# explain-07 · mlx/core.py——Apple Silicon 原生引擎：连续批处理与流水线分片

## 角色定位

`xinference/model/llm/mlx/core.py`（2267 行）是 MLX（Apple Silicon 统一内存框架）引擎适配层，也是 Xinference 里**唯一内置自研连续批处理**的引擎：`MLXBatchModel`（`mlx/core.py:101`，docstring 明言"Wrapper around MLX-LM BatchGenerator for continuous batching"）在 mlx-lm 的 BatchGenerator 之上搭了按采样参数分组的后台 worker + 每请求队列。类塔与 vLLM 同构：`MLXModel`（`:642`，LLM+ChatModelMixin）→ `MLXChatModel`（`:1468`）→ `MLXVisionModel`（`:1609`，mlx-vlm，带独立 mlx 线程调度）。分片推理走 `distributed_models/` 目录的**按 model_type 动态导入**（`:970-971`）。

## 内部结构

`MLXBatchModel` 是类级单例式设计（模型/tokenizer/锁全是类属性，`:105-112`）：`_batch_generators` 按 `(temperature, top_p, top_k)` 三元组分桶（`:192`）——同一采样参数的请求进同一个 BatchGenerator 才能合批，每桶存 generator+每请求 asyncio.Queue+active 集合+pending 缓存（`:217-219`）。新 API 判定 `_is_new_mlx_lm`（`:167-182`）以 0.31.2 为界，新 API 才有可复用 prompt cache（`LRUPromptCache`，`:134-145`）。`_background_worker`（`:330-389`）是批处理心脏：死循环调 `batch_generator.next()` 拿**整批**结果，按 `result.uid` 分发到各请求队列（`:358-371`），队列未就绪的结果进 pending 防丢（`:367-374`），finish 的请求移出 active（`:377-382`）。版本分叉：新 API 的 `next()` 返回 `(prompt_results, batch_results)` 二元组并借此存"稳定前缀段缓存"（`:340-345`）。`MLXModel` 侧：`load()`（`:980`）单 worker 直接 `_load_model`，多 worker 起 `_loading_thread` 走 shard 协调；`wait_for_load`（`:1032-1070`）join 后读 context length，**关键开关**：n_worker>1 时强制 `self.allow_batch = False`（`:1047-1052`，分布式不开连续批处理），单机才构造 MLXBatchModel（`:1056-1068`）。

## 外部连接

上游同 vLLM：`LLM_ENGINES` 表注册、ModelActor 调 `load/async_generate`。向 mlx-lm 依赖两代 API（`mlx_lm.generate.BatchGenerator`、`make_sampler`，`:201-205`）；向 mlx-vlm 有个精细补丁 `_ensure_mlx_vlm_thread_local_stream`（`:74-98`）：mlx 的 generation_stream 默认非线程安全，用 `mx.new_thread_local_stream` 替换模块属性，双检锁防并发替换（`_mlx_vlm_stream_lock`，`:69`）。分布式分片的动态加载在 `_get_classes`（`:954-978`）：`config["model_type"]` 先过 mlx-lm 的 `MODEL_REMAPPING` 归一，再 `importlib.import_module("xinference.model.llm.mlx.distributed_models.{model_type}")`，ImportError 转 ValueError。`distributed_models/` 现有 qwen2/qwen3/qwen3_moe/deepseek_v3 四个架构文件，每个都极薄（如 `qwen3_moe.py` 仅 76 行）：`Qwen3MoeModel(_Qwen3MoeModel, DistributedModelMixin)` 只重写 `__call__` 做**流水线接力**——非首 rank 先 `_wait_prev_stage_result()`（`distributed_models/qwen3_moe.py:52-54`），跑完本段层后非尾 rank `_send_stage_result`+`_get_result`，rank0 则 `_broadcast_result`（`:61-65`）；跨 shard 张量传输用 `_to_wire` 把 mx.array 转 numpy 位流（bfloat16 无 numpy 对应，按 uint16 裸位传输，`distributed_models/core.py:27-33` 注释）。

## 数据流

单机推理流：`generate_stream`（`:391`）→ 取/建采样参数桶（`:404`）→ 确保后台 worker（`:408`）→ tokenize 后 `_insert_request` 入批（`:418-423`，带 `prompt_cache_prefix_len` 前缀复用）→ 注册队列与 active（`:436-438`），先倒出 pending 早到结果（`:441-452`）→ 主循环 `await queue.get()`（0.5s 超时轮询，`:464`）逐 token 解码成 CompletionChunk，`token_text.strip("�")` 去残缺 UTF-8（`:475`），usage 里回填 `cached_tokens`（`:487-489`）。分布式加载流：shard0 自报地址（`:1001-1003`），其余 shard 经 driver 的 actor ref 调 `set_shard_info` 并 `get_rank_addresses` 等全员到齐（`:1008-1021`），然后各自 `_load_model_shard` 只实例化本段的层（start_idx 切片见 `distributed_models/qwen3_moe.py:57`）。非 driver shard 的推理由 `_run_non_drivers`（`:1286-1315`）驱动——driver 每步 forward 时其余 shard 在自己的进程里跑同段计算等待接力。

## 设计决策

①**批处理按采样参数分桶**是无奈之举：BatchGenerator 的 sampler 建时就固化，不同 temperature 的请求无法同批，桶多了内存和批效率都掉——调参时意识到这一点很重要；②**类属性单例**（`_model_ref` 等挂在类上）意味着同进程多个 MLX 模型实例会互相覆盖，单模型假设被隐式编码在结构里；③**分布式与批处理互斥**（`:1047-1052`）诚实降级而非硬上；④**wire 格式手工处理 bfloat16**（`core.py:27-33`）是因为 numpy 生态没有 bf16，跨进程传裸位再还原 dtype——改传输协议时最易踩的雷。

## 新人提示

Mac 上调试先分清三代路径：纯文本走 MLXBatchModel、vision 走 `_run_on_mlx_thread`（`:1635`）、分布式走 distributed_models；三者线程模型不同（asyncio 队列 / 专用线程 / 多进程流水线）。"模型不在批处理"最常见原因就是 n_worker>1 或 allow_batch 为 False 的族（`:1060` 检查的是**实例级**属性）。加新架构支持 = 在 distributed_models/ 加一个 76 行的 mixin 子类，`_get_classes` 的动态导入零注册自动生效——这是全仓最友好的扩展点。mlx-lm 升级先跑 `_is_new_mlx_lm` 两套 API 分叉的测试（`tests/` 在同目录）。
