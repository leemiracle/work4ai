# vllm/v1/engine/async_llm.py — AsyncLLM：异步门面与前端的全部生命周期能力

> 源码：`vllm/v1/engine/async_llm.py`（1454 行，vLLM 2026-10-28 @06e172b5cf）｜tags: `async-engine`, `entry-point`, `v1-engine`
> 2026-09 版重写：多客户端准入共享、前端 profiler、checkpoint 三件套、RL 权重传输族为新增主线

## ① 角色定位

`AsyncLLM` 是 v1 引擎在**前端进程侧的异步门面**，实现 `EngineClient` 协议（`vllm/engine/protocol.py:43`），是 OpenAI API server、gRPC server、RL online 路由所依赖的稳定抽象。它自己不算一个 token，职责三件事：把用户输入加工成 `EngineCoreRequest` 发给 EngineCore 进程；用唯一一个后台 task 把输出泵回各请求；承载引擎全部**生命周期能力**——准入控制、abort、pause/resume、睡眠唤醒、LoRA 热加载、elastic EP 扩缩容、进程 checkpoint、在线权重更新。2026-09 以来它明显变"厚"：多 API server 客户端共享一个引擎的部署形态（`client_count/client_index`，`vllm/v1/engine/async_llm.py:108`）让准入统计与输出路由都要跨客户端记账。

## ② 内部结构

单类文件（`InputStreamError` 异常包装在 81 行 + `AsyncLLM`）。`__init__` 组装线（96-247 行）：

1. `renderer_from_config`（167）——tokenizer/多模态预处理/聊天模板统一入口，同时是 MM 共享渲染缓存（P0 sender cache）持有者；
2. `InputProcessor`（170）——EngineInput → EngineCoreRequest；
3. `SharedAdmissionStats`（172-177）——**新增**：多客户端模式经共享内存 `mp_admission_counters` 聚合各 API server 的在途请求计数；
4. `OutputProcessor`（180）——反向转换 + stream_interval 节流 + parent request 聚合；
5. `EngineCoreClient.make_async_mp_client`（193）——spawn EngineCore 进程并建 ZMQ 连接，renderer 随行以便 fork 后再做 MM warmup；
6. `StatLoggerManager`（206）——支持多引擎 rank 与 `aggregate_engine_logging` 聚合日志；
7. 前端 profiler（226-247）——**新增**：`profiler_config.should_profile_frontend` 时自动创建 CPU profiler；多客户端共享引擎时禁用并告警。

关键方法群（行号为当前源码锚）：

| 方法 | 行号 | 说明 |
|---|---|---|
| `check_admission` | 325 | 两级准入：`max_num_queued_reqs`（在途请求数，n>1 计 n 槽）+ `max_num_queued_tokens`（TTFT QoS），超限抛 `QueueOverflowError`/`MaxQueuedTokensError`（HTTP 503 语义，让 LB 重试他机） |
| `add_request` | 397 | 四分支：AsyncGenerator 流式输入（438）、`EngineCoreRequest`（458，**已标废弃**，应传 Renderer 输出）、已渲染 dict（481 同步 `process_inputs`）、raw prompt（500 `process_inputs_async` 丢线程池） |
| `_add_streaming_input_request` | 589 | 流式输入会话：每 chunk 造一个 resumable 请求；`handle_inputs` 收尾发空 final_req 作结束信号（688） |
| `generate`/`encode` | 726/1034 | async generator；`q.get_nowait() or await q.get()` 快路径（795） |
| `_run_output_handler` | 856 | 唯一输出泵 task：分片喂 `process_outputs`、MM 缓存失效联动、stop-string 反向 abort |
| `pause_generation`/`resume_generation` | 989/1026 | abort/wait/keep 三模式 + clear_cache |
| `sleep`/`wake_up`/`release_kv_cache_memory` | 1198/1213/1206 | RL 省电模式，level 0/1/2 |
| `checkpoint_prepare/restore/state` | 1221/1228/1231 | **新增**：进程 checkpoint 生命周期 |
| `scale_elastic_ep` | 1300 | 弹性 EP 扩缩容：retire 标记（1348）与 logger 热替换（1327-1336） |
| `init_weight_transfer_engine` 等权重族 | 1403-1451 | **重构**：在线权重更新统一走 `collective_rpc`，`weight_version` 随输出回传 |

## ③ 外部连接

- **imports**：`input_processor`/`output_processor`/`core_client`/`parallel_sampling`/`renderers`/`admission_control`/`metrics/*`/`elastic_ep/middleware`/`fault_tolerance/utils`/`kv_hints` 等约 40 个模块——门面典型依赖扇入。
- **被 imports**：`vllm/engine/async_llm_engine.py`（V0 命名兼容层 re-export）、`vllm/entrypoints/launchers/api_server/entry.py`、`launchers/grpc_server.py`、`vllm/entrypoints/rl/online/api_router.py`；API server 经由 EngineClient 协议间接依赖。
- **下游**：EngineCoreClient（ZMQ mp 或 Inproc 两形态）；Renderer；OutputProcessor（`RequestOutputCollector`/`StreamingInputOutputCollector`）。

## ④ 数据流

```
HTTP/gRPC 请求 → generate() → add_request()
  → [线程池] InputProcessor.process_inputs_async: tokenize+mm → EngineCoreRequest
  → engine_core.add_request_async() ──ZMQ──▶ EngineCore 进程
输出侧（唯一 task）:
  output_handler(856): await engine_core.get_output_async()
    → 按 VLLM_V1_OUTPUT_PROC_CHUNK_SIZE 分片(891-916)
    → mm_cache_miss_hashes → renderer.queue_mm_cache_invalidations(894-902) # 新增:P0/P1缓存漂移自愈
    → output_processor.process_outputs(905) → push 进各请求 collector
    → processed_outputs.reqs_to_abort → 反向 abort(919-922)
    → weight_version 随 EngineCoreOutputs 透传(909)
  → generate() 循环 q.get() → yield RequestOutput → SSE
```

准入路径：`check_admission` 先查 `admission_stats.get_num_requests()`（355，跨客户端共享计数），无则本地 `get_num_unfinished_requests()`；tokens 侧用 `get_num_queued_tokens()`（373）。docstring 明言这是**保守高估**——chunked prefill 进度与 prefix 命中不扣减（337-341），宁可早拒保 TTFT。

## ⑤ 设计决策

1. **重活零残留**：连 tokenize 都不放事件循环（`process_inputs_async`，500）；事件循环只剩纯 Python 输出分发。分片 + `asyncio.sleep(0)`（916）防一批大输出饿死其他任务。
2. **单泵 + 跨客户端扇出**：一个 `output_handler` 从 ZMQ 拉，`EngineCoreOutputs.client_index` 决定发给哪个 API server。handler 通过 `_logger_ref = [self.logger_manager]` 可变列表持引用（869），既避免 task→AsyncLLM 循环引用阻塞 GC（861 注释），又允许 elastic EP 扩容时热替换 logger（1335）。
3. **异常五分类**（807-851）：CancelledError/GeneratorExit（断连）→ internal abort；EngineDeadError → 直接抛（死了无从 abort）；VLLMClientError 族 → abort 回收 n>1 兄弟请求后原样抛；InputStreamError → 解包 `.cause` 抛（流式输入的用户异常不被吞）；未知 → abort + 包 `EngineGenerateError`。
4. **MM 缓存漂移自愈闭环（新）**：EngineCore 侧发现多模态特征在 P0 sender cache 已失效时回 `mm_cache_miss_hashes`；前端在**发布错误前**先标记失效（902），客户端带数据重发——跨进程缓存一致性的关键顺序。
5. **Elastic EP 优雅退场**：retired rank 的 output_handler 收到 EngineDeadError 不算故障，记 info 后 `propagate_error` 安静退出（937-942）。

## ⑥ 新人提示

- 切入点：`generate()` docstring（746-757）的官方四步图 → `_run_output_handler`（856，约 90 行）→ `add_request` 四分支。
- 易混①：`add_request` 是发起（返回 collector），`generate` 是消费；API 层可分别直调。易混②：`abort(internal=True)` 表示 vLLM 自身发起（断连/stop string），不走用户回调路径。易混③：`stream_interval`（OutputProcessor 节流）与 `VLLM_V1_OUTPUT_PROC_CHUNK_SIZE`（handler 分片）是两层不同的批处理，别混。
- **2026-09→10 变化**：新增 checkpoint 三件套（1221-1232）——resume/sleep/wake 全部受 EngineCore 侧 `CheckpointState` 状态机约束；权重更新重构为 `collective_rpc` + `weight_version` 溯源（1439-1451，draft 模型也有独立入口 1424）；`notify_kv_transfer_request_rejected`（961）把 P 节点预准入 KV 资源回收做成显式的 pre-aborted 请求。
- 想懂 n>1 parallel sampling 看 `parallel_sampling.ParentRequest`（542-564 fan-out 骨架）；想懂流式输入会话看 `handle_inputs` 闭包（637-696）的取消/错误/收尾三分支。
- 关联测试：`tests/v1/engine/test_async_llm.py`、`tests/entrypoints/openai/`（streaming input、checkpoint 用例）。
