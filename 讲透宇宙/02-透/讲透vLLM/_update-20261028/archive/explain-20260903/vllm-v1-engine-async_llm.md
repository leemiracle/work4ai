# vllm/v1/engine/async_llm.py — AsyncLLM：异步门面与前端的全部生命周期能力

> 源码：`vllm/v1/engine/async_llm.py`（约 1230 行）｜知识图谱 tags: `async-engine`, `entry-point`, `api-handler`, `v1-engine`

## 角色定位

`AsyncLLM` 是 v1 引擎在**前端进程侧的异步门面**（facade）。图谱上它 `implements EngineClient`（`vllm/engine/protocol.py` 定义的协议），也就是说 OpenAI API server、gRPC server 依赖的抽象正是它。它自己不执行任何模型计算，职责是三件事：把用户输入加工成 `EngineCoreRequest` 发给 EngineCore 进程；用一个后台 task 把输出泵回各请求；以及承载引擎的全部**生命周期能力**（准入控制、abort、pause/resume、睡眠唤醒、LoRA 热加载、elastic EP 扩缩容、在线权重更新）。

## 内部结构

图谱 contains：`InputStreamError`（流式输入中断异常）与 `AsyncLLM` 两个符号——本文件是**单类文件**，复杂度在方法与协作对象上。

`__init__` 的组装线：
1. `renderer = renderer_from_config(vllm_config)`——tokenizer/多模态预处理器/聊天模板的统一入口；
2. `InputProcessor(vllm_config, renderer)`——`EngineInput → EngineCoreRequest`（tokenize、mm 预处理）；
3. `OutputProcessor`——反向：`EngineCoreOutputs → RequestOutput`（detokenize、stream_interval 节流、parent request 聚合）；
4. `EngineCoreClient.make_async_mp_client(...)`——**spawn EngineCoreProc 后台进程**并建立 ZMQ 连接；
5. `StatLoggerManager`（指标）；
6. 若已在事件循环内则惰性启动 `output_handler` task。

关键方法群：
- `generate()/encode()`：async generator。`add_request()` 返回 `RequestOutputCollector`，随后循环 `q.get_nowait() or await q.get()`——非阻塞优先，减少高负载下的任务切换；
- `add_request()`（341 行起）三分支：prompt 为 `AsyncGenerator` → 走 `_add_streaming_input_request`（流式输入会话）；已渲染 dict → 同步 `process_inputs`；**raw prompt → `process_inputs_async`（丢线程池，tokenize 绝不阻塞事件循环）**。`n>1` 时用 `ParentRequest` fan-out 出 child requests（parallel sampling）；
- `check_admission()`：`max_num_queued_reqs`（在途请求上限）与 `max_num_queued_tokens`（TTFT QoS：排队 prompt token 总量上限）两级准入，超限抛 503 语义异常，让 LB 重试到别的实例；
- `_run_output_handler()`（733 行）：**唯一的**后台消费 task——`await engine_core.get_output_async()` → 按 `VLLM_V1_OUTPUT_PROC_CHUNK_SIZE` 分片喂给 `output_processor.process_outputs`（结果直接 push 进各请求的 collector，方法本身不返回 outputs）→ 片间 `asyncio.sleep(0)` 让出事件循环 → 处理 stop-string 触发的反向 abort → 记录 scheduler/iteration stats；
- 生命周期族：`pause_generation/resume_generation`（在线权重更新：abort/wait/keep 三模式 + 可选清缓存）、`sleep/wake_up`、`add_lora/pin_lora`、`scale_elastic_ep`（弹性专家并行扩缩容）、`update_weights` 系列。

## 外部连接

- **imports**：`input_processor`、`output_processor`、`core_client`、`parallel_sampling`（n>1 实现）、`renderers`、`metrics/*`、`fault_tolerance/utils`、`elastic_ep/middleware` 等约 35 个模块——典型的门面依赖扇入。
- **被 imports**：`v1/engine/async_llm.py` 被 `engine/async_llm_engine.py` re-export（V0 命名兼容层，`from vllm.engine.async_llm_engine import AsyncLLMEngine` 实际就是 AsyncLLM）；`entrypoints/grpc_server.py` 直接引用。图谱反向边干净，说明 API server 经由 EngineClient 协议间接依赖。

## 数据流

```
HTTP/gRPC 请求
  → generate() → add_request()
      → [线程池] InputProcessor: tokenize + mm 处理 → EngineCoreRequest
      → engine_core.add_request_async() ──ZMQ──▶ EngineCore 进程
  输出侧（独立 task）:
  output_handler: get_output_async() ──ZMQ──◀ EngineCoreOutputs
      → 分片 → OutputProcessor.process_outputs（detokenize/聚合）
      → push RequestOutput 到该请求的 RequestOutputCollector
  → generate() 循环 q.get() → yield RequestOutput → SSE 响应
```

## 关键设计决策

1. **门面 + 协议**：AsyncLLM 把"异步引擎"抽象成 `EngineClient` 协议的稳定实现，entrypoints 只依赖协议——未来换传输（如 gRPC 直连引擎）不动上层。
2. **重活零残留**：连 tokenize 都不放事件循环（`process_inputs_async`）。事件循环里只剩纯 Python 的输出分发，这是 vLLM 能在高 QPS 下保持 SSE 流平滑的关键。
3. **单泵 + 扇出**：只有一个 `output_handler` 从 ZMQ 拉，再由 `OutputProcessor` 扇出到每请求 collector；分片处理 + `sleep(0)` 防"一批大输出饿死其他 asyncio 任务"。collector 用 `get_nowait() or await get()` 的快路径。
4. **异常分类传播**：`generate()` 里 `CancelledError`（客户端断连）→ 内部 abort；`EngineDeadError` → 直接抛（引擎已死无从 abort）；client error → 原样抛给 HTTP 层；其余未知异常 → abort + 包装。output_handler 崩溃时经 `propagate_error` 打进所有活跃 collector，保证每个等待者都能被唤醒并收到错误。
5. **output_handler 惰性启动**：`__init__` 可在事件循环外调用（OpenAI server 启动失败要能优雅返回），首个 `add_request` 才真正起 task。

## 新人提示

- 切入点：`generate()` 的 docstring（923 行起）就是官方架构图，三步 + output_handler，先读它。
- 易混淆点①：`add_request` 是**发起**（返回 collector），`generate` 是**消费**（async generator）；两者都可被 API 层直接调用。
- 易混淆点②：`abort(internal=True)` vs `False`——internal 表示 vLLM 自身（断连/stop string）发起，不触发用户回调路径。
- `stream_interval` 控制输出节流粒度，与 `VLLM_V1_OUTPUT_PROC_CHUNK_SIZE`（handler 分片）是两层不同的批处理，别混。
- 想理解 n>1 parallel sampling，去看 `parallel_sampling.ParentRequest`，AsyncLLM 只做 fan-out 骨架。
