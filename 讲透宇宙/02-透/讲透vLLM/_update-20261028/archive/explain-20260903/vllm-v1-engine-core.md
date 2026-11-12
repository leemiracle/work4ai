# vllm/v1/engine/core.py — EngineCore：V1 引擎的内循环与进程模型

> 源码：`vllm/v1/engine/core.py`（约 2580 行）｜知识图谱 tags: `engine-core`, `scheduler`, `multiprocessing`, `v1-engine`

## 角色定位

`core.py` 处于 v1 引擎的**核心执行层**。`EngineCore` 类自称 "Inner loop of vLLM's Engine"：它组合 Scheduler（调度）、model executor（GPU 执行）、KV cache 初始化与 structured output 管理，对外提供"一步推理"原语 `step()`。请求生命周期中，它是 EngineCoreProc 独立进程里的 resident 循环：从前端接收 `EngineCoreRequest`，反复 step 直到请求完成，把 `EngineCoreOutputs` 推回。

## 内部结构

图谱 contains 边给出的类层次（两条正交维度）：

```
EngineCore                      # 逻辑核心：scheduler + executor + kv cache
 └─ EngineCoreProc              # + ZMQ IPC 包装，独立进程运行
     └─ DPEngineCoreProc        # + DP 协调（MoE 模型的 DP rank）
         └─ DPMoEEngineCoreActor # + EngineCoreActorMixin → Ray actor 变体
EngineCoreActor                 # = EngineCoreActorMixin + EngineCoreProc（Ray 版）
```

**EngineCore.__init__ 的装配顺序**（105–251 行）值得背下来：
1. 加载 general plugins；
2. `model_executor = executor_class(vllm_config)`——加载模型权重；
3. `_initialize_kv_caches()`——注册 KV cache spec、profile 可用显存、产出 `KVCacheConfig`；
4. `StructuredOutputManager`；
5. **`Scheduler = vllm_config.scheduler_config.get_scheduler_cls()`**——工厂决定用 `Scheduler` 还是 `AsyncScheduler`；
6. 聚合 worker 侧 KV connector 握手元数据（P/D disagg 需要 scheduler 掌握全 worker 的传输拓扑）；
7. `batch_queue`（`deque(maxlen=max_concurrent_batches)`，PP/async scheduling 的在途 batch 队列）；
8. 收尾三板斧：`freeze_gc_heap()`（把启动堆标记为静态，缩短 GC 停顿）、`enable_envs_cache()`（此后环境变量视为只读）。

**两条 step 路径**：`step()`（默认）= `schedule()` → `execute_model(non_block=True)` 拿 Future → grammar bitmask → `sample_tokens` → `update_from_output`；`step_with_batch_queue()`（V2/PP）= 优先把 batch_queue **填满**（在途多批并发，消除流水线气泡），满了才 pop 最老的一批等结果并 update。`self.step_fn` 按配置绑定其一。

**EngineCoreProc（进程壳）**：
- 两条 daemon 线程 `process_input_sockets` / `process_output_sockets` 在 ZMQ socket 与 Python `queue.Queue` 之间搬运——ZMQ IO 释放 GIL，可与 GPU 前向重叠，序列化/反序列化也被推到线程里；
- 主线程 `run_busy_loop()`：`_process_input_queue()`（无工作时**阻塞**在 `input_queue.get()`，空转零 CPU）→ `_process_engine_step()`（step + 输出入队）；
- `_perform_handshakes`：与前端交换 ZMQ 地址；DP>1 时还与 DP Coordinator 握手等待 READY；
- `run_engine_core()`：multiprocessing spawn 的进程入口，注册 SIGTERM/SIGINT → `shutdown_state = REQUESTED`（`EngineShutdownState` 三态：RUNNING/REQUESTED/SHUTTING_DOWN），按 `shutdown_timeout` 选 drain 或 abort。

## 外部连接

- **imports**：`config`、`distributed`、`v1/executor`（MultiprocExecutor 等）、`sched/interface`（只依赖 SchedulerInterface 抽象）、`tensor_ipc`（多模态张量共享内存队列）、`fault_tolerance/engine_core_sentinel`、`kv_cache_utils`。
- **被 imports**：`core_client.py`——注意双向关系：`InprocClient` **直接实例化** EngineCore（单进程模式，无 ZMQ），mp client 则 spawn `run_engine_core`；`elastic_ep/elastic_state.py` 在弹性扩缩容时操作 `DPEngineCoreProc`。

## 数据流

```
前端 EngineCoreClient
  → ZMQ → input 线程 → input_queue
  → _handle_client_request: preprocess_add_request → scheduler.add_request
主循环: step_fn() = scheduler.schedule() → executor.execute_model(Future)
        → sample → scheduler.update_from_output → outputs
  → output_queue → output 线程 → ZMQ → 前端 get_output_async()
```

## 关键设计决策

1. **逻辑与传输分离**：`EngineCore`（纯逻辑）与 `EngineCoreProc`（IPC 壳）分两层，使 `InprocClient` 能零开销内嵌运行（测试、单进程部署），也使 ZMQ 层可以独立演进（如 DP coordinator、多前端握手）。
2. **进程隔离的动机**：前端（API server）是 asyncio 世界，引擎是 CUDA/GIL 世界。分进程后，前端事件循环永不被模型执行阻塞；引擎崩溃（CUDA error、segfault）时前端仍能返回明确的 `EngineDeadError` 而不是陪着挂。
3. **线程化 IO 而非 asyncio**：引擎侧坚持同步线程模型（busy loop + Queue），避免 asyncio 开销与回调解耦复杂度；用"阻塞 get 等工作"实现零开销空闲。
4. **非阻塞 execute + batch_queue**：`execute_model(non_block=True)` 返回 Future，调度与执行在 PP/async scheduling 下重叠——`step_with_batch_queue` 的注释写明"填满队列优先于取结果"。
5. **优雅关闭三态机**：REQUESTED 后按 `shutdown_timeout` 决定 drain（等在途请求）或 abort，最后 `SystemExit`；信号处理里只用 `put_nowait(WAKEUP)` 唤醒，规避信号中断非重入锁的经典坑。

## 新人提示

- 阅读切入点：`step()`（597 行，30 行读完）→ `run_busy_loop()`（1411 行）→ 再看 `EngineCoreProc.__init__` 的线程布局。`step_with_batch_queue` 较绕，配合 PP 文档再看。
- 易混淆点①：`EngineCore.add_request` 收的是已 tokenize 的 `EngineCoreRequest`（tokenize 在前端 InputProcessor），别在这里找 tokenizer。
- 易混淆点②：`has_work()` 包含 `batch_queue` 非空——V2 模式下即使 scheduler 空了，在途 batch 也得取回。
- `sleep()/wake_up()` 是权重换出省电模式（RL 场景），与 `pause_scheduler`（在线更新权重）不是一回事。
