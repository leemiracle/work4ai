# vllm/v1/engine/core.py — EngineCore：V1 引擎的内循环与进程模型

> 源码：`vllm/v1/engine/core.py`（2962 行）｜EngineCore→EngineCoreProc→DPEngineCoreProc 三层+Ray actor 变体｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

`core.py` 处于 v1 引擎的**核心执行层**。`EngineCore`（vllm/v1/engine/core.py:123）自称 "Inner loop of vLLM's Engine"：组合 Scheduler、model executor、KV cache 初始化与 structured output 管理，对外提供"一步推理"原语。请求生命周期中它是 EngineCoreProc 独立进程里的 resident 循环——从前端收 `EngineCoreRequest`，反复 step，把 `EngineCoreOutputs` 推回。与 9 月版相比它管得更宽：KV 初始化膨胀为 165 行编排（non-causal 层探测、布局协商、auto-fit 回写），新增 checkpoint 生命周期、watch dog 与 fault tolerance sentinel。

## ② 内部结构

类层次两条正交维度：`EngineCore`（纯逻辑）→ `EngineCoreProc`（:1207，ZMQ 进程壳）→ `DPEngineCoreProc`（:2383，MoE DP 协调）；Ray 侧 `EngineCoreActorMixin`（:2788）+ `DPMoEEngineCoreActor`（:2914）/`EngineCoreActor`（:2937）。

**`EngineCore.__init__`（:131-255）装配顺序**：plugins → `model_executor`（:157）→ `measure_encoder_output_widths`（:167，EC 传输带宽探测）→ `_initialize_kv_caches`（:170）→ `StructuredOutputManager`（:171）→ **`get_scheduler_cls()` 工厂**（:174；vllm/config/scheduler.py:231：async_scheduling→AsyncScheduler，diffusion 由 vllm/config/vllm.py:2078 改写为 DiffusionScheduler）→ Scheduler 构造注入 kv_cache_config/block_size/hash_block_size（:187-195）→ KV/EC connector 聚合器（:202-204）→ `_set_kv_connector_handshake_metadata`（:209）→ `batch_queue`（:215-221，尺寸=`max_concurrent_batches`）→ `step_fn` 绑定（:239-241）→ `freeze_gc_heap()`（:250）+`enable_envs_cache()`（:255）。`_initialize_kv_caches`（:258-423）：`register_all_kvcache_specs`（:262）→ **non-causal attention 层直接关掉 chunked prefill 与 prefix caching**（:273-287）→ layout 协商（:293）→ 显存 profile（:317）→ auto-fit 缩短 max_model_len 时 `collective_rpc("update_max_model_len")` 同步给已 spawn 的 worker（:337-339）→ hash_block_size/cache_hit_alignment_tokens 双粒度解析（:363-377）。

**两条 step 路径**：`step()`（:674）= `schedule()` → `execute_model(non_block=True)` 拿 Future → **等 future 期间预取 grammar bitmask**（:686）→ `future.result()` 后若 worker 未代采样（model_output 为 None）才引擎侧 `sample_tokens`（:691-693）；`step_with_batch_queue()`（:715，V2/PP 多在途批）docstring 明言"填满队列优先于取结果"（:723-725）；structured output 可延迟采样（:763-766、:809-826）。

**进程壳**：两条 daemon 线程 `process_input_sockets`（:1990，msgspec 解码+张量 IPC+多模态缓存漂移自愈 :2063-2067）/`process_output_sockets`（:2099，buffer 复用+MessageTracker 零拷贝 :2150-2165）；主线程 `run_busy_loop`（:1669，`@fault_tolerant_wrapper` :1668）→ `_process_input_queue`（:1695，无工作阻塞 get，阻塞段用 `watch_dog().disable()` 包住 :1710-1711）→ `_process_engine_step`（:1726；未执行但仍有请求时 `time.sleep(0.001)` 让后台 KV 传输线程推进 :1741-1742）。DP 版 busy loop（:2567-2654）多出 dummy batch（:2607-2609）、`_has_global_unfinished_reqs` all-reduce（:2656-2674）与 wave 通知。

## ③ 外部连接

- **依赖**：`v1/executor`、`sched/interface`（只认 SchedulerInterface 抽象）、`tensor_ipc`、`fault_tolerance/engine_core_sentinel`（:97）、`utils/watch_dog`（:55）、`kv_cache_planning`（:57）。握手是双向写：startup_handshake 用前端 init_message **直接 setattr 改写 parallel_config**（:1499-1505），握手完重跑 `vllm_config.__post_init__()`（:1397）。
- **被依赖**：`core_client.py` 的 `InprocClient` 直接内嵌 EngineCore（单进程零 ZMQ）；`elastic_ep/elastic_state.py` 操作 `DPEngineCoreProc`（`reinitialize_distributed` :2676 是弹性扩缩容入口）；`_make_ready_response`（:1931）把 30+ 项能力（含 dev 模式下全量 VllmConfig dump :1979-1987）打包给前端。

## ④ 数据流

```
前端 EngineCoreClient → ZMQ → input 线程（解码+preprocess_add_request :1168，
  grammar_init 与 Request 构造在 IO 线程内与 GPU 前向重叠）
  → input_queue → busy loop → _handle_client_request :1799
      ADD/ABORT/UTILITY/EXECUTOR_FAILED 四类分发
主循环: step_fn() = scheduler.schedule() → executor.execute_model(Future)
        → grammar 预取 → sample → update_from_output → outputs
  → output_queue → output 线程（零拷贝 buffer 回收）→ ZMQ → 前端
关闭: 信号（:1590-1591，SIGTERM 还要喂 watch dog :1577-1578）
  → REQUESTED → _handle_shutdown :1751 按 shutdown_timeout 选
  abort（:1766）/drain（:1777）→ SHUTTING_DOWN → SystemExit
```

## ⑤ 设计决策

1. **逻辑与传输分离**：EngineCore 纯逻辑、EngineCoreProc 只管 IPC，`InprocClient` 得以零开销内嵌；引擎崩溃时前端拿 `EngineDeadError` 而非陪葬（`_send_engine_dead` :1918 等 output 线程 5s 把死讯真正发出）。
2. **同步线程模型而非 asyncio**：busy loop + Queue，"阻塞 get 等工作"零空转；ZMQ IO 释放 GIL 与 GPU 重叠，序列化也推入线程。
3. **暂停语义三件套**：`pause_scheduler`（:974/:2238 两级实现，Proc 版走 idle 回调 :2274-2280）→ `pause_generation`（:2282，用户暂停额外置 `reject_new_requests`，新请求收到**可重试**的 engine_paused 错误 :1844-1864）→ checkpoint_prepare/restore（:2297/:2324，drain→释放 KV→PREPARED，restore 走 `collective_rpc("checkpoint_restore")`）。`sleep()/wake_up()`（:1019/:1061）是权重换出的 RL 特化，别混。
4. **信号安全窗口**：构造期内信号只记 `shutdown_requested` 标志（:1561-1581），`SignalCallback` 等 input_queue 存在才武装（:1615）——构造中唤醒无处可投是真实踩过的坑（:1586 注释链 PR 52299）。
5. **clean_shutdown 判据全部显式**（:1622-1628）：exit code、SHUTTING_DOWN、`has_work()` 为空、`shutdown_timeout==0` 四项同时成立才算干净，ROCm 还要补一次 `gc.freeze()` 跳过退出期慢 GC（:1647-1651）；常规 shutdown 里 `gc.unfreeze()`（:852）防单进程复用漏显存。

## ⑥ 新人提示

- 读法：`step()`（:674，30 行）→ `run_busy_loop`（:1669）→ `_initialize_kv_caches`（:258）按注释分段啃 → DP 版最后看。
- `add_request`（:525）收的是**已 tokenize** 的 EngineCoreRequest；tokenizer 在前端 InputProcessor。
- `has_work()`（:1656）含 `batch_queue` 非空与 DP 的 `engines_running`——scheduler 空了引擎未必能停。
- 调 DP 负载不均先看 `_should_throttle_prefills`（:2557-2564，cadence 对齐步才放 prefill）与 `_maybe_publish_request_counts`（:2540，带 step_counter/wave 的 LB 统计）。
- abort 走双队列（input 线程塞 aborts_queue :2089-2094 + input_queue 保序），调度器侧 abort 幂等，两路都会收敛。
