# vllm/v1/worker/gpu_worker.py — Worker：进程与设备生命周期的管理者

> 源码：`vllm/v1/worker/gpu_worker.py`（1735 行）｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

`Worker(WorkerBase)` 是**进程与设备生命周期的管理者**：绑定哪块 GPU、初始化分布式环境、装载权重、显存剖析、KV cache 显存规划、编译预热、sleep/wake、checkpoint、权重热更新、容错与弹性 EP。与 GPUModelRunner 分工清晰：**Worker 管"一次性/低频"事件（启动、休眠、换权重），ModelRunner 管"每步"事件（forward、采样）**。执行器为每 rank 建一个 Worker 进程，EngineCore 经 RPC 驱动；稳态只在 `execute_model`（vllm/v1/worker/gpu_worker.py:1337）与 `sample_tokens`（:1330）露面且都是薄包装。2026-09→10 增量：容错 WorkerSentinel（:226）、弹性 EP（:224）、workspace 多 lane（:122/:564）、startup plan（:661/:1071）、draft 权重热更新（:1555）。

## ② 内部结构

模块级：`_num_workspace_lanes`（:122，V2+DSpark 开 2 条 lane，target/draft 图并发持有视图）；`maybe_rocm_profiling_fallback`（:131，ROCm 剖析测量为负时退回 torch reserved 做下界）。`AsyncIntermediateTensors`（:165）：PP 妙物——张量带 comm handles，覆写 `__getattribute__`（:190）让任何 `.tensors` 访问先惰性 `wait_for_comm()`，通信等待藏进属性访问。

`Worker` 关键成员：`use_v2_model_runner`（:206，V2 强制 Triton :207）；sleep 三份保存 dict——buffers/**parameters（新）**/draft_buffers（:229-231）；`weight_transfer_engine`（:235，load_model 后才建）；`_pp_send_work`（:247，上一步 PP 发送句柄，下一步顶部才 wait :1342）。sleep 家族：`_save_sleep_parameters`（:276，**fnmatch 模式保留参数**）；`sleep`（:301）level 2 存 buffers+参数、KV connector 注销、NCCL 可选挂起（:321）；`wake_up`（:341）按 tags 精细恢复；`discard(tags)`（:369）按 tag 丢池不恢复。另有 checkpoint 协作（:374/:377）、权重校验和（:388）与 `reset_weights`（:393）——RLHF 权重一致性验证的底座。

## ③ 外部连接

- **依赖**：`worker_base.WorkerBase`、`device_allocator`（CuMem 池/SleepModeBackendFactory :259）、distributed 全家（kv_transfer :40、ec_transfer :33、weight_transfer :59、parallel_state :49）、`mem_utils`（memory_profiling）、startup_plan（:107）、WorkerSentinel（:106）、`init_workspace_manager`（:112）、gpu/warmup（:115）。
- **被依赖**：cpu_worker/xpu_worker 继承骨架（xpu 在内存池判断有特判 :404）；`init_worker_distributed_environment`（:1693）被 multiproc/ray worker 入口复用；`elastic_ep_execute`（:1689）是弹性 EP 的 RPC 通道。

## ④ 数据流：启动序列（本文件主叙事）

1. **`init_device()`**（:449）：清 Ray 注入的 NCCL_ASYNC_ERROR_HANDLING（:452）→ DP local rank 换物理 GPU 并发布 assigned_physical_gpu_ids 供 NIC 亲和/P2P 查询（:458，pr45026：ray/external_launcher 跳过 local_world_size 断言）→ **先分布式初始化再拍显存快照**（:500，NCCL buffer 须计入基线）→ **cuBLAS handle 预热**（:526-536，torch 的重试机制看不到 cuBLAS 的直接 CUDA 申请，剖析后首个 cuBLAS 调用会假 OOM）→ gc+empty_cache 后 MemorySnapshot（:539）→ workspace manager 带 num_ubatches（DBO=2）与 lanes（:564，scratch 无跨步状态故 sleep 丢弃）→ `_make_model_runner`（:577）**V2 分叉**：`v1/worker/gpu/model_runner.py`（:585）或本目录 V1（:591）。
2. **`load_model()`**（:601）：三层上下文（weights 内存池、set_current_vllm_config、max_split_size_mb=20 换碎片）→ 按需建 WeightTransferEngine（:613）→ `set_torch_threads_for_runtime`（:624，保 Dynamo guard 有效）。
3. **`determine_available_memory()`**（:648）：先 `maybe_apply_startup_plan`（:661，上次攒的 plan 可跳过试探）；显式 kv_cache_memory_bytes 仍要 profile_run 完成编译（:663）；否则 memory_profiling 里 profile_run（:692）→ `profile_cudagraph_memory`（:720）→ 预估默认计入（envs.py:333），`available = requested − non_kv − cudagraph_estimate`（:756-760）→ 日志教学等效 util 换算（:780）→ `reserve_mm_ipc_gpu_memory` 预留多模态 IPC（:819）。
4. **`initialize_from_config()`**（:869）：回填 num_gpu_blocks；**采纳 engine core 的 kv_cache_layout/hash_block_size**（:878-883，弹性 EP 后 spawn 的 worker 只能从 config 看到）；先 `ensure_kv_transfer_initialized`（:890）→ connector 自带内存池优先（Mooncake NVLink/BAREX :895）→ runtime pool 包 initialize_kv_cache（:903）→ **KV-zero 簿记张量池外初始化**（:915-921，防 sleep/wake 丢弃）。
5. **`_compile_or_warm_up_model()`**（:943）：warmup_sizes 推导（compile_sizes 减 capture sizes+compile_range 补端点 :944-970）→ kernel_warmup（:985）→ V2 的 warmup_kernels（:987，capture 后 workspace resize 会 free 图指向的内存）→ capture_model（:996）→ 图显存实际/估计对比（:999）→ `--kv-cache-memory` 建议含 150MiB 冗余（:1029）+ maybe_save_startup_plan（:1071）→ V1-only dummy sampler run（:1073-1093，刻意放 capture 后防 empty_cache 清掉）→ 重置种子（:1097）→ trigger_inductor_lazy_init（:1109）→ JIT monitor（:1113）→ freeze_gc_heap（:1117）→ **enable_gpu_sync_check（:1122，warmup 完成才激活同步检查闸）**。

稳态 `execute_model`（:1337）：顶部 wait 上一步 `_pp_send_work`（:1342，防覆写仍在读的 buffer）→ 非首 PP rank irecv 得 AsyncIntermediateTensors（:1349）→ runner 执行 → 非 last rank isend 异步发出即返回（:1387）；V2 pooling 的 `pool()` 补丁（:1366/:1393）。

## ⑤ 设计决策

1. **sleep/wake 全面 tags 化**：level 1 弃 KV、level 2 连权重卸载且参数可按 fnmatch 保留；wake/discard 按 weights/kv_cache 标签选择性恢复——"一机多实例分时复用"的成本基石。
2. **显存经济学闭环**：实测 profile + cudagraph 预估（默认计入）+ mm IPC 预留 + startup plan（自动适配 max_model_len，:856）四件套；`--kv-cache-memory` 建议日志本身就是教学。
3. **剖析陷阱前置排除**：NCCL buffer 先分配、cuBLAS handle 先创建再拍快照——都是"torch 看不见的显存申请"，顺序即正确性。
4. **执行最小透传**：execute_model 不碰业务，只做 PP 收发、V2 pooling 补丁与 profiler 注解（`annotate_profile` :1215 的 context/generation 屋顶线指标）。
5. **权重热更新会话化**：start/update*/finish 三段式 + draft 专属会话（经 share_source_lm_heads 走未量化 target head，finish 再 restore_quantized_lm_heads :1584-1590），失败统一回滚（:1587）。
6. **V1/V2 守卫式共存**：所有 V2-only 行为（capture profiler :1143、pool() :1366、jit warmup :987）显式分叉，V1 路径零改动。

## ⑥ 新人提示

- 切入点：按五步启动序列顺读；`_compile_or_warm_up_model` 是"vLLM 启动为什么慢"的地图。
- 易混淆点①：`determine_available_memory` 返回**字节数**，num_blocks 除法在 EngineCore 侧，Worker 只被动接收 config。
- 易混淆点②：profile_run（显存剖析、满 batch）与 _dummy_run（编译预热/图捕获）都是假数据跑模型，语境不同。
- 易混淆点③：V2 runner 是 `v1/worker/gpu/model_runner.py` 的目录化新一代（2547 行），本文件仍是 V1 大本营；共存靠 use_v2_model_runner 分叉。
- 新增面：workspace 的 lane/ubatch 语义（DSpark 双 lane、DBO 双 ubatch）排启动 OOM 时要想到；shutdown 末尾 release_pools()（:1683）为绕过 pytorch#145168 的终期化延迟。
