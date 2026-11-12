# vLLM v1 深度解析：GPU Worker（gpu_worker.py）

> 文件：`vllm/v1/worker/gpu_worker.py`（约 1500 行）
> 知识图谱 layer：`gpu-worker`；被 cpu_worker.py / xpu_worker.py 继承（复用其骨架）

## 角色定位

`Worker(WorkerBase)` 是**进程与设备生命周期的管理者**：绑定哪块 GPU、初始化分布式环境、装载权重、显存剖析、KV cache 显存规划、编译与预热、sleep/wake、checkpoint、权重热更新。它与 GPUModelRunner 的分工非常清晰——**Worker 管"一次性"与"低频"事件（启动、休眠、换权重），ModelRunner 管"每步"事件（forward、采样）**。执行器（uniproc/multiproc/ray executor）为每个 rank 创建一个 Worker 进程，EngineCore 通过 RPC 驱动它。

请求生命周期中 Worker 几乎不露面，只在两处：每个 step 的 `execute_model()`（一薄层包装，主要处理 pipeline parallel 的张量收发）与 `sample_tokens()`。

## 内部结构

- **`Worker`** 主类。关键成员：`model_runner`（构造于 `init_device`，含 V2 分支——`use_v2_model_runner` 时改 import `v1/worker/gpu/model_runner.py` 或 mm_encoder_model_runner）、`init_snapshot`（启动时显存快照）、`weight_transfer_engine`（RLHF 权重热更新引擎）、`_sleep_saved_buffers`（level-2 睡眠前抢救的模型 buffer）、`worker_sentinel`（容错哨兵）、`sleep_mode_backend`（惰性创建的休眠后端）。
- **`AsyncIntermediateTensors(IntermediateTensors)`**：PP 场景的妙物——`irecv_tensor_dict` 返回的中间张量带 comm handles，覆写 `__getattribute__` 让任何 `.tensors` 访问都先惰性 `wait_for_comm()`，把通信等待藏进属性访问。
- **`init_worker_distributed_environment()`**（模块级函数）：设 all-reduce 后端、调 `init_distributed_environment` + `ensure_model_parallel_initialized`（TP/PP/PCP/DCP）。
- **`maybe_rocm_profiling_fallback()`**：ROCm 上剖析期间别的进程释放显存导致测量为负时，退回 torch reserved 作为下界。

## 数据流：启动序列（本文件的主叙事）

1. **`init_device()`**：DP local rank 换算物理 GPU（`DP_LOCAL_RANK × TP_PP_WORLD + TP_LOCAL_RANK`）→ `torch.accelerator.set_device_index` → **先 `init_worker_distributed_environment` 再拍显存快照**（顺序刻意的注释：NCCL buffer 必须先分配，否则可用显存测不准）→ `MemorySnapshot` + `request_memory`（`gpu_memory_utilization × total`）→ `init_workspace_manager` → 构造 ModelRunner。
2. **`load_model()`**：包三层上下文——CuMem allocator 内存池（`tag="weights"`，供 sleep 模式）、`set_current_vllm_config`、`max_split_size_mb=20`（用更多 cudaMalloc 换更少碎片）；随后按需创建 `WeightTransferEngine`。
3. **`determine_available_memory()`**：核心显存经济学。`memory_profiling` 上下文里跑 `model_runner.profile_run()`（假数据满 batch forward）测峰值 → 可选 `profile_cudagraph_memory()` 预估图显存（v0.21 起默认计入，日志贴心地给出等效 `--gpu-memory-utilization` 换算）→ `available_kv_cache_memory_bytes = requested − non_kv − cudagraph_estimate`。若用户显式给了 `kv_cache_memory_bytes` 则跳过剖析直接用。EngineCore 拿到这个字节数才能算出 `num_blocks` 并回传。
4. **`initialize_from_config(kv_cache_config)`**：先 `ensure_kv_transfer_initialized`（KV connector 需要先见到 config）→ `model_runner.initialize_kv_cache`（挂 `tag="kv_cache"` 内存池）→ KV-zero 元数据在池外初始化（防 sleep/wake 丢弃簿记 tensor）。
5. **`compile_or_warm_up_model()`**：按 compile_sizes 预热非捕获尺寸（含 compile_range 补端点）→ `kernel_warmup`（防捕获期 JIT）→ `capture_model()` → 对比图显存实际/估计值 → 打出 `--kv-cache-memory` 建议 → `_dummy_sampler_run` 预分配 logits buffer（刻意放在 capture 后避免被 empty_cache 清掉）→ 重置随机种子 → JIT monitor 上岗 → **`freeze_gc_heap()`** 冻结 GC 堆（推理期静态对象不被扫描）。

稳态 `execute_model()`：PP 非首 rank 先 `irecv_tensor_dict` 得 AsyncIntermediateTensors → `model_runner.execute_model` → 非 last rank 把输出 `isend_tensor_dict` 异步发出即返回（self-retained handles 惰性回收）。

## 关键设计决策

- **sleep/wake 两级**：level 1 只弃 KV cache 显存；level 2 连权重也卸载，但先把 `named_buffers` 抢救到 CPU（wake 时 copy 回去，因为 buffer 不随权重重载恢复）；可选 `suspend_device_comms` 挂起 NCCL。这是"一台机器分时跑多实例"的成本基石。
- **权重的内存池隔离**：weights 与 kv_cache 用不同 tag 的 CuMem pool，sleep 时可以只丢其一；且断言 weights 池 usage==0，保证一进程一实例。
- **剖析先行、规划在后**：显存预算 = 实测 profile 而非估算公式；CUDA graph 显存是否预留由 `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS` 开关，形成"图显存 ↔ 可用 KV"的显式权衡并在日志中教学。
- **执行最小透传**：Worker.execute_model 不碰业务逻辑，只做 PP 收发与 profiler 注解（`annotate_profile` 按 context/generation 阶段聚合 seq_len/qk_compute 屋顶线指标）。

## 新人提示

- 切入点：按上面五个启动步骤顺读，每个方法都不长；`compile_or_warm_up_model` 是理解"vLLM 启动为什么慢"的地图。
- 易混淆点①：`determine_available_memory` 返回的是**字节数**，`num_blocks` 的除法发生在 EngineCore 侧（除以 per-block 大小），Worker 只在 `initialize_from_config` 里被动接收。
- 易混淆点②：`profile_run` 与 `_dummy_run` 都是假数据跑模型，前者在显存剖析上下文里、后者用于编译预热/图捕获，别混为一谈。
- 易混淆点③：V2 ModelRunner 分支（`use_v2_model_runner`）是重构中的新一代 runner，旧文件里散落的 `assert not self.use_v2_model_runner` 说明两者共存期兼容是靠限制功能组合实现的。
- 想看真实 forward 细节请跳到 gpu_model_runner 篇；本文件的价值在"资源与生命周期"。
