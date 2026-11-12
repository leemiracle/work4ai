# 08 FSDP 子树与分布式优化器：vendored 双路、MFSDP v2 与 NVSHMEM 拷贝服务

## 一、角色定位

三条互相咬合的线：**Megatron-FSDP**（ZeRO-1/2/3 级分片库，整体 vendored 进仓）、**DistributedOptimizer**（看家分布式优化器，3393 行）、**NVSHMEM copy service**（resharding/refit 子系统最高吞吐后端，服务 RL 循环训练权重→推理权重的换装）。FSDP v1 的 param_and_grad_buffer 与 DistributedOptimizer 共享桶化分片思想；refit 按并行布局差重排权重，NVSHMEM 是五后端（refit.py:38）中的流水线 GPU-to-GPU 选项。

## 二、内部结构

**vendored 子树与双路导入**：`megatron/core/distributed/fsdp/` 入口文件加完整源码树 `src/megatron_fsdp/`（11275 行，自带 pyproject 可独立安装）。`fsdp/__init__.py:2` 从 adapter 重导出 `FullyShardedDataParallel`；`mcore_fsdp_adapter.py:51-79` try/except 导入 vendored 树并置 `HAVE_MEGATRON_FSDP`，失败时缓存异常、在 V1/V2 构造期（:189、:595）才抛——主路径永远走 vendored 相对导入，缺失降级为延迟报错。仓内其它消费方（training.py:59、checkpointing.py:74、finalize_model_grads.py:9 等）直接 import vendored 路径，不走 try/except。

**V1/V2 分派**：`FullyShardedDataParallelV1`（mcore_fsdp_adapter.py:131）包装生产版 `MegatronFSDP`（megatron_fsdp.py:112，1621 行，自带 unshard/reshard hook 全家）；V2（:554）是 MFSDP v2 包装。同名 `FullyShardedDataParallel` 是**工厂函数而非类**（:895），按 `megatron_fsdp_version == 2` 二选一（:909-912）。

**MFSDP v2 = experimental/ 与设计文档一一对应**：`src/docs/mfsdp_design.md` 的每件东西都落在 `src/megatron_fsdp/experimental/`（17 文件 4056 行）——`fully_shard` API（fully_shard.py:38 `Placements`）、`ParameterGroup` 与 `DBuffer`（dbuffer.py:73）、Muon 需要的 `TensorAtomic(Shard)`（placement.py:70）、`SchedulePolicy`（schedule.py:21）、quantized_dbuffer/checkpoint/owner_planning/module.py（`FsdpModule`）。策略表 `_DATA_PARALLEL_PLACEMENTS`（mcore_fsdp_adapter.py:937-942）把 no_shard/optim/optim_grads/optim_grads_params 四档映射为 (参数,梯度,优化器) 三元 Placement；注释（:925-933）直指设计文档：梯度从不 Replicate（Partial 或 Shard，reduce 须 "avg"）；HSDP=no_shard 外轴×ZeRO-3 内轴，HFSDP=optim 外轴×ZeRO-3 内轴。

**DistributedOptimizer**：`DistributedOptimizer(MixedPrecisionOptimizer)`（distrib_optimizer.py:152），继承链 optimizer.py:187→:685→本类。核心是 `Range`（:117）算术驱动的构建三部曲：`_build_model_gbuf_param_range_map`（:231）切 grad buffer、`_build_optimizer_group_ranges`（:397）、`_build_model_and_main_param_groups`（:444）建 model↔fp32 main param 分片映射。近半体量在检查点兼容：`checkpoint_fully_reshardable_formats`（:165-170）枚举全可重排格式，dp_zero legacy 迁移（`_update_legacy_world_tensors` :2267 处理世界规模变化）；量化贯穿拷贝路径（fp8 :2768、nvfp4 :2820）。入口 `step_with_ready_grads`（:3362）。

**NVSHMEM copy service**：外层 `NVSHMEMCopyService(CopyService)`（copy_services/nvshmem_copy_service.py:22）要求每次传输带全局唯一 task_id（:26-30），同 rank 传输走本地旁路（:66-69）。内层 `RemoteCopyService`（nvshmem_copy_service/service.py:34）组合 planning/core/memory 三组部件。**双缓冲对称内存**：`DoubleBufferManager`（memory/double_buffer_manager.py:22）用 bytetensor 分配 send/recv 各 2 个 slot（:43-50），slot=256MB（nvshmem_types.py:8），合计 4×256MB≈1GB 对称堆，按 `iteration % 2` 轮换（:60-72）。**NVRTC JIT**：`KernelLauncher.load_kernels`（core/kernel_launcher.py:30）运行时读 `kernels/chunked_kernel.cu` 源码，`cp.RawKernel(...)` 即时编译（:35-46），launch 固定 1024 线程/75 块。**双依赖闸门**：`HAVE_NVSHMEM`（service.py:20-25）与 `HAVE_CUPY`（kernel_launcher.py:15-19）两个 try-import 把缺库降级成清晰报错；`compat.py:23-33` 垫 cuda-core>=0.5 私有子模块搬家的 sys.modules shim（nvshmem4py 仍从旧路径导入）。

## 三、外部连接

FSDP adapter 依赖 `torch.distributed.tensor` Placement 体系与 DeviceMesh，V2 强制显式 `ProcessGroupCollection`（:600），默认以 TransformerLayer/MoETransformerLayer/MambaLayer 为 FSDP 单元（:616）。DistributedOptimizer 消费 param_and_grad_buffer 桶布局，向 dist_checkpointing 暴露 `optimizer_state_keys`（:915）。NVSHMEM 服务被 `refit.get_or_create_service`（refit.py:156，nvshmem 分支 :182-183）缓存复用，上游 swap_model_weights 再上游是 RL 线 colocated_inference（见 07 篇）。docker/patches/deepep-nvshmem.patch 是 DeepEP 的另一条消息面，与本服务无关。

## 四、数据流

MFSDP v2 一步：`fully_shard` 挂 FsdpModule → SchedulePolicy 驱动 DBuffer unshard/reshard/prefetch → 梯度按 Placement reduce-scatter → 优化器状态按 Shard 维护。DistributedOptimizer：grads → `_copy_model_grads_to_main_grads`（:2889）入 fp32 main grads → step → `_copy_main_params_to_model_params`（:2935）回写（量化走 :3049）。refit/NVSHMEM：planner 各 rank 确定性重放同一调度 → 注册收发 → `schedule()` 汇总 → GPU 驻留 plan → pack kernel 入 slot → NVSHMEM put 流水线 → unpack 落位 → 双缓冲让第 N 批通信与第 N+1 批重叠。

## 五、设计决策

1. **vendored 而非依赖**：可独立发布的库钉进仓内，主路径相对导入吃 vendored 版本，异常被 try/except 吸收；代价是 1.1 万行与上游同步的负担。
2. **工厂函数隐藏代差**：`:895` 用 `megatron_fsdp_version` 拨 V1/V2，调用方零感知；docstring 警告别拿它做 isinstance。
3. **v2 长在 experimental/ 而非改造 v1**：设计文档明言现有架构难以干净实现，故另起路径、达标后渐迁——目录名就是路线图。
4. **本地旁路 + collective 纪律**：dest==self.rank 留在 wrapper 层本地 stream（copy_services/nvshmem_copy_service.py:113-133），但 schedule()/run() 是 collective，注释强调所有 rank 必须都调用，否则非同置 refit 死锁。
5. **256MB 槽×4 的取舍**：槽大小决定单段上限与流水线粒度，是吞吐与驻留显存的折中，换档只改一个常量。
6. **检查点格式包袱显式管理**：多格式各配 loader，`checkpoint_fully_reshardable_formats` 把"可全重排"收敛成一处判据。

## 六、新人提示

- 改 FSDP 先分清 V1（megatron_fsdp.py）与 V2（experimental/）——钩子机制完全不同，测试也分家（tests/unit_tests/distributed/mfsdp_v1/ 与 mfsdp_v2/）。
- `megatron_fsdp_version` 不设 2 拿到的永远是 V1；V2 拒绝 `disable_bucketing=True`。
- NVSHMEM 后端需同时装 nvshmem 与 cupy；报 `cuda.core.experimental._memory` ImportError 先查 compat shim 是否先于 nvshmem.core 导入（service.py:18 `ensure_nvshmem_compat()`）。
- 对称缓冲是 1GB 级常驻显存，多实例翻倍——所以 refit.py 做服务缓存；`clear_service_cache()`（refit.py:193）前必须先 close 释放。
- 读 DistributedOptimizer 按 Range → 三个 _build → step_with_ready_grads 顺序，检查点大段等真遇格式迁移再看；examples/megatron_fsdp/ 三个脚本是最短可跑起点。
