# explain-06 · vllm/core.py——vLLM 引擎集成与三种分布式形态

## 角色定位

`xinference/model/llm/vllm/core.py`（2751 行）是 Xinference 最重的引擎适配层：`VLLMModel`（`vllm/core.py:491`，继承 `model/llm/core.py` 的 `LLM`）把 vLLM 的 `AsyncLLMEngine` 包成 Xinference 模型，并额外实现**三种分布式执行形态**——单机多卡原生 mp、跨 worker 的 XinferenceDistributedExecutor、以及 KV 块跨实例迁移的 xavier。文件里三个类呈继承塔：`VLLMModel`（completions）→ `VLLMChatModel`（`:2137`，+ChatModelMixin 处理 messages/工具调用）→ `VLLMMultiModel`（`:2333`，多模态，含 base64 媒体落盘与 video metadata 注入）。

## 内部结构

`__init__`（`:495-527`）从 model_config 弹出五个分布式控制键（`xinference_vllm_executor_backend`/`address`/`n_worker`/`shard`/`driver_info`，`:512-518`）——这些是 Xinference 自己的编排参数，不能漏进 vLLM 的 `AsyncEngineArgs`。加载决策核心是 `_native_mp_route()`（`:576-625`）：一个带理由返回值的路由函数，按序排除 xoscar 显式指定（`:578`）、n_worker>1（`:581`）、xavier 开启（`:589`）、单 GPU（`:594`）、vLLM 缺版本/非 V1/低于 0.28.0（`:600-617`），剩下的 auto 路由目前只对 Qwen4Exp 架构（`_is_qwen4_exp`，`:573`）自动走 native_mp（`:622-624`）。`load()`（`:685-993`）是版本兼容的考古现场：v0.3.1-0.3.3 要把 multiprocessing 切回 fork 修 cupy NCCL（`:727-733`）；LoRARequest 构造参数在 0.14.0 前后不同（`lora_local_path` vs `lora_path`，`:753-770`）；Executor 导入路径在 0.11.1 前后不同（`:692-698`）。引擎创建分三支：xavier 支（`:781-800`，强制开 `enable_prefix_caching`，用 `XavierEngine.from_engine_args`）、native_mp 支（`:801-856`，设 TP/PP 与 `distributed_executor_backend=mp`，spawn 子进程）、xoscar 分布式支（`:857-970`）与单机支（`:971-993`）都放进 `_loading_thread` 后台线程，load 只 `join(1)` 秒即返回——**异步加载**是全文件最重要的结构性决定。

## 外部连接

上游：`create_llm_model_instance` 经 `LLM_ENGINES` 表选到本类；ModelActor（`core/model.py`）在子进程池里调 `load()`/`wait_for_load()`/`async_generate`。worker 侧的配合点：`need_create_pools()`（`:655`）为 True 时 worker 会按 GPU 数追加 per-device 子池（`core/worker.py:4553-4573`），`set_pool_addresses`（`:658`）回填。跨 worker 分片协同：shard 0 在 `_load` 里挂 `_all_worker_ready` 事件等齐所有 worker 的池地址（`:896-899`），非 0 分片通过 actor ref 反向调 driver 的 `set_worker_addresses`（`:880-891`）；随后 v0 用 `XinferenceDistributedExecutor`、v1 用 `XinferenceDistributedExecutorV1`（`distributed_executor*.py`），v1 分支还 monkey-patch `Executor.get_class`（`:960`）并给 ≥0.19.0 打 `supports_async_scheduling`（`:957-958`）。xavier 子系统在 `vllm/xavier/`（engine/scheduler/allocator/block_tracker/collective_manager/transfer 等 13 文件），由 supervisor 的 CollectiveManager actor 编排（`core/supervisor.py:2995-3011`）。

## 数据流

启动流：`load()` 先 `_sanitize_model_config`（`:1301`，剥离/翻译 Xinference 参数成 vLLM 参数）→ 弹出 `reasoning_content`/`enable_thinking` 装配 reasoning parser（`:737-742`）→ GGUF 特殊预处理（`:744-749`）→ 三支建引擎。`wait_for_load`（`:995-1032`）join 线程、重抛 `_loading_error`（`:998-1000`）、读 `max_model_len` 存 `_context_length`（`:1034-1044`），并用 `call_soon_threadsafe`+`create_task` 启动健康检查——注释（`:1007-1018`）解释了两层教训：健康检查曾因线程未 join 完被静默跳过；而 `run_coroutine_threadsafe` 的 Future 异常无人查会被吞，`create_task` 的异常才会被 asyncio 默认 handler 记日志。推理流：`async_generate`（`:1768`）先做 enable_thinking/tools 时不 `skip_special_tokens`（`:1803-1804`，否则思考标签会被剥掉）→ LoRA 按名匹配（`:1811-1818`）→ 流式经 `stream_results`（`:1998`）转 OpenAI CompletionChunk；chat 路径在 `VLLMChatModel.async_chat`（`:2262`）复用 generate，多模态在 `VLLMMultiModel._gen_tokens_prompt`（`:2502`）注入图像 token。

## 设计决策

①**加载线程化+错误延迟重抛**：模型加载动辄分钟级，load() 一秒即返让 worker 不被一个引擎卡死，错误在 `wait_for_load` 统一以原 traceback 重抛（`:998-1000`）；②**路由函数带理由**（`_native_mp_route` 返回 `(bool, str)`，日志 `:829-847` 打全量决策要素），分布式问题排障第一入口就是这段日志；③**版本地窖式兼容**：每个 if 分支都注释版本号，升级 vLLM 时这些就是检查清单；④**auto 路由收窄到 Qwen4Exp**（`:622-625`）——native_mp 是激进路径，默认只对已知受益架构开放，其余要显式 `XINFERENCE_VLLM_EXECUTOR_BACKEND=native_mp`。

## 新人提示

排"模型起不来"先看两处日志：`vLLM executor route:`（`:829`）告诉你走了哪条路、为什么；`Loading ... with following model config`（`:775`）是最终进 `AsyncEngineArgs` 的参数（被 sanitize 改写后的真值）。报 `ImportError: Failed to import module 'vllm'` 大概率是 virtualenv 没装对而非宿主。xavier 排障跨三处：本文件 `:781-800`（引擎侧）、`vllm/xavier/engine.py`、supervisor 的 CollectiveManager。v1 引擎"卡在初始化"经典原因是 `:948-951` 注释那个坑——v1 的 EngineCore 用 fork 创建，不能把主进程 loop 传进去。
