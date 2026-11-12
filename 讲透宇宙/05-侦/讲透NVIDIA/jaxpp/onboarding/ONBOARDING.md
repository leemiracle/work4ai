# JaxPP onboarding（讲透 NVIDIa/jaxpp @ d5ff52c，2026-10-15 快照）

> 图谱：903 节点 / 2037 边 / 14 层 / 16 步导览，fingerprints 117 文件基线。
> 本文全部行号锚基于 `d5ff52c37d14735c9d02961434d9a69913d01bf5` 实测核实。

## 1. 一句话定位

JaxPP 是 NVIDIA 开源的 JAX **MPMD（多程序多数据）流水线并行库**：用户只在模型代码里写一行 `mark_stage_end(x)` 注解（`src/jaxpp/pipelining.py:48`），再用 `@mpmd_jit_with_loop` / `@mpmd_jit_by_yield` 装饰（`src/jaxpp/core.py:4013` / `:4047`），JaxPP 就把一个 JAX 函数编译成"每台设备各持一段的独立 jit 程序"，配合 1F1B/ZeroBubble/DualPipeV 等调度器在设备间流水执行。版本 0.11.1（`src/jaxpp/__init__.py:16`），README 明示 API 不稳定、暂不接受 PR。它与 DeepSeek DualPipe 的血缘在源码里写得非常直白——`dualpipev_tasks` 的第一行注释就是 Adapted from deepseek-ai/DualPipe（`src/jaxpp/schedules.py:204`）。

读代码前的三个坐标系：
1. **编程模型轴**：隐式（yield 切分，`mpmd_jit_by_yield`）vs 显式（`experimental/_mpmd.py` 的 task_mpmd/transfer_mpmd，`src/jaxpp/experimental/_mpmd.py:314/:362`）。
2. **编译轴**：用户 Python → jaxpr → 任务方程（TaskEqn）→ 调度重排 → 插传输 → 每设备独立 jit。
3. **硬件轴**：SM90（Hopper）与 SM100（Blackwell）两代 ragged GEMM 内核（`examples/maximoe/src/maximoe/kernels/ragged_dot/sm90.py` / `sm100.py`）。

## 2. 全景：14 层架构地图

- **LL01-LL03 工程壳**：pyproject/CI/Docker/Slurm 脚本。文档站 CI 无 GPU，notebook 页用仓内预渲染副本替代执行（`.github/workflows/documentation.yml:49-51`）；供应链防御做到 `scripts/setup-env.sh:8` 的 UV 安装器 SHA256 硬校验。
- **LL04 公共 API 与类型**：`api.py` 是门面（`src/jaxpp/api.py:26` 汇出 mpmd_jit 两入口）；`types.py:41` 的 MpmdSharding 是带 mpmd 轴的 NamedSharding 子类、`:84` TaskType 枚举（FWD/BWD_I/BWD_W）；`env_vars.py` 集中全部 `JAXPP_*` 开关且默认值即调参档案（`:5` LICM 默认关、`:23` fast sharding 推断默认关）。
- **LL05 编译核心**：`core.py`（4071 行）+ `jax_primitives.py`（1412 行）+ `jaxpr_utils.py`。这是全库心脏。
- **LL06 数组抽象**：`array.py:32` MpmdArray（17 方法）与 SPMD↔MPMD 双向重分片（`:434` / `:558`）；`dlpack.py:230` 把 DLPack capsule 变 NCCL 可传参数。
- **LL07 流水线与调度**：`schedules.py`（1F1B 全家族+DualPipeV/KimiK2）、`training.py`（tscan/treduce）、`dime2.py`（传输层）、`licm.py`/`sharding_inference.py`（两个编译 pass）。
- **LL08 兼容与实验**：`jax_compat/__init__.py` 隔离 JAX 私有 API；`experimental/_mpmd.py`（860 行）显式 MPMD 第二编程模型。
- **LL09-LL13 MaxiMoE 与测试**：DSV3 形状 MoE 参考实现（模型 1676 行、训练 2114 行）+ SM90/SM100 ragged GEMM 内核 + 三层测试金字塔。
- **LL14 主测试套件**：`test_mpmd_api.py` 2116 行最大，`fake_devices.py` 让无 GPU 环境跑通大部分套件。

## 3. 用户编程模型：注解 + 调度器

用户唯一要写的注解只有三个上下文管理器（`src/jaxpp/pipelining.py`）：`yield_scope`（`:29`，激活阶段计数）、`mark_stage_end`（`:48`，把 anchor pytree 绑到 `pipeline_yield_p` 原语上，`src/jaxpp/jax_primitives.py:896`）、已废弃的 `pipeline_enter_stage`（`:39`，转发 DeprecationWarning）。`basic.py` 是最小对照样例：`examples/basic.py:130` 一行 `jaxpp.mark_stage_end(x)` 切出两级流水线，`:139` 用 `mpmd_jit_with_loop` 装饰。

关键机制：`_current_stage` 是模块级全局变量，`mark_stage_end` 在其为 None 时静默直通（`pipelining.py:69-70`）。它只在两处被激活——`mpmd_jit_by_yield` 追踪期（`core.py:3346`，`yield_scope(isinstance(self.strategy, FunctionWithYield))`）和 `training.py` 的 `_pipelined_loop` 二次追踪（`src/jaxpp/training.py:199/:253`）。所以 docstring 说 mark_stage_end "Must be called inside a function passed to treduce/treduce_i"（`pipelining.py:55`）——with_loop 路线的注解实际是在 treduce/tscan 展开的循环追踪里被消费的，两条入口殊途同归。

调度器家族（`src/jaxpp/schedules.py`）：`BaseSchedule`（`src/jaxpp/schedules.py:299`）→ `InterleavedBaseSchedule`（`src/jaxpp/schedules.py:325`）两级抽象；实现有 ZeroBubble（`src/jaxpp/schedules.py:343`）、Interleaved1F1B（`src/jaxpp/schedules.py:379`）、Eager1F1B（`src/jaxpp/schedules.py:473`）、Std1F1B（`src/jaxpp/schedules.py:492`）、KimiK2（`src/jaxpp/schedules.py:547`）、InterleavedGPipe（`src/jaxpp/schedules.py:553`）、GPipe（`src/jaxpp/schedules.py:591`）、DualPipeV（`src/jaxpp/schedules.py:611`）。任务模型是 `Task`/`FusedTask`（`src/jaxpp/schedules.py:26`/`:48`），ZeroBubble 用 `_next_zero_bubble_task_type` 把 BWD 拆成 BWD_I/BWD_W 交替（`src/jaxpp/schedules.py:120`），循环骨架由 SequentialMicrobatchesIterator/ZBSequentialMicrobatchesIterator 驱动（`src/jaxpp/schedules.py:84/:107`）。

## 4. 编译核心管线：core.py 深潜

`mpmd_jit_with_loop` / `mpmd_jit_by_yield` 都只是给 `_mpmd_jit`（`core.py:3984`）喂不同 Strategy；Strategy 是 ABC（`:3252`），两个实现 FunctionWithLoop（`:3267`）与 FunctionWithYield（`:3285`）。编译主链（TraceableFunction `:3316`，compile=trace_and_place→infer_intermediate_shardings→mpmdify）：

1. **追踪**：普通 jax.jit 追出 jaxpr；AllReduceRewriteTracer/Trace（`:167`/`:178`）重写跨设备加法（propagate_and_rewrite_adds `:327`）。
2. **切分**：yield 路线按 pipeline_yield 方程聚类（cluster_by_yield_eqns `:976`、clusters_to_tasks `:1072`、cluster_jaxpr `:1128`）；loop 路线在 scan 循环体内/后包任务（wrap_into_tasks_inside_loop `:1188`、wrap_into_tasks_after_loop `:1434`、统一入口 wrap_into_tasks `:1601`）。
3. **需求分析**：compute_needed（`:526`）做 defs/uses 活性分析，决定每个任务真正需要的输入。
4. **任务化**：make_task_eqn（`:791`）把任务包装成 TaskEqn（`jax_primitives.py:1373`）；CommunicationEffect（`:727`）作为自定义 effect 保证 XLA 不重排跨任务通信。
5. **调度重排**：infer_times（`:2465`）+ reorder_nodes_with_schedule（`:1876`）按调度器生成的时间表重排方程。
6. **插传输**：compute_transfers（`:2035`）/ add_transfers（`:2079`）在设备边界插入 send/recv，bufferize_recvs（`:2688`）做接收缓冲化；check_global_jaxpr（`:2853`）终检 FIFO 语义。
7. **收尾**：to_local_jaxprs（`:2917`）切出每设备独立 jaxpr，deduplicate_task_jaxprs（`:2339`）+ fuse_groups（`:2384`）做任务去重与融合。

两个 pass 决定生成代码质量：`licm.py` 三合一（partial_eval_jaxpr `:323`、partial_eval_loop `:576`、hoist_and_cse_pscan_invariant_equations `:680`，LICM+部分求值+CSE）；`sharding_inference.py` 两代推断（infer_shardings `:548`、fast 版 infer_shardings2 `:486`）+ reconcile_shardings（`:241`）调和显式标注。`docs/compilation.md` 是官方机制讲义。

## 5. 数据面：MpmdArray、重分片与 DIME 传输

MpmdArray（`src/jaxpp/array.py:32`）是跨任务数据的一等公民，通过 `pytype_aval_mappings` 注册进 JAX pytree/aval 体系（`:264-271`，模块导入即生效）使可被 jit 追踪。SPMD↔MPMD 双向重分片：`spmd_to_mpmd_reshard`（`:434`）按工作内存阈值分组并交错排序；`mpmd_to_spmd_reshard`（`:558`）反向。`array_ops.py` 支撑跨任务栈操作（make_array_from_addressable_shards `:27`、stack_shape_and_sharding `:125`、stack_arrays_with_shardings `:260`），api 层的 `cross_mpmd_stack`/`cross_mpmd_all_reduce` 即此（`api.py:48` 起三个薄包装）。

传输层 DIME v2（`src/jaxpp/dime2.py`）：get_or_create_comm（`:87`）基于 NCCL 与 JAX distributed client 建连并缓存 communicator；ShardCapsule（`:131`）+ get_shard_ops_and_capsules（`:137`）把重分片计划编译成 ShardOp 队列异步发起，Capsule/PendingSend 管理发送生命周期与完成回收。底层互操作靠 `dlpack.py` 的 ctypes 结构复刻（DLTensor `:103`、DLManagedTensor `:115`），dlpack_nccl_args（`:230`）把 capsule 转成 NCCL 窗口参数、`_validate_contiguous`（`:210`）校验内存连续性。放置语义由 MpmdMesh（`src/jaxpp/mesh.py:28`）决定：device_mpmd_idx（`:91`）给设备到任务的归属映射，unstack（`:106`）拆出每任务子 mesh，_require_mpmd_indices（`:188`）/_resolve_placement（`:208`）解析放置。

## 6. MaxiMoE：DSV3 形状 MoE 与 ragged GEMM

`examples/maximoe/` 是 jaxpp 能力的最大集成样例（也是读懂它的最佳教材）。模型层（`model.py` 1676 行）：all_to_all（`:75`）专家通信、ring_of_experts（`:562`，`:1443` 处开关默认 False）、dedup_token_routing（`:316`）去重路由计划、RaggedArray（`:160`）变长 token 容器。训练层（`train.py` 2114 行）：BF16 计算+FP32 主权重与 router bias（`:249` 显式断言"expert master compression requires FP32 masters and BF16 compute"）、router_bias_update_rate=0.001（`:218`，auxiliary-loss-free 风格 bias 更新）、host_offload_regex 把状态叶放 pinned host 内存（`:172`/`:852`）。warmup_tasks（`warmup.py:32`）正式训练前逐任务预热编译与 NCCL 建连；profile.py 的 numerical_signatures 做数值签名对比。

内核层是性能主战场，backend.py 的 Implementation 枚举 + resolve（`kernels/backend.py:35/:43`）按环境变量/硬件分派。ragged_dot 家族：ops.py 定义 RaggedOperation 抽象基类（`:95`）与 RaggedDot/RaggedDotSwiGLU/RaggedDotCombine 三算子（`:150/:206/:237`，每个含多后端选择）；sm90.py（1431 行）Hopper 路线——ragged_dot_kernel（`:249`）+ kernel_warp_specialized（`:413`）+ emit_pipeline_warp_specialized（`:456`）warp 特化；sm100.py（1424 行）Blackwell 路线——TuningConfig（`:52`）按形状查表 tile/block 参数、persistent_grid（`:69`）持久线程网格、store_swiglu/store_identity（`:115/:101`）两种写出策略。moe_routing 双后端：mosaic_gpu.py 的 persistent_group_loop（`:118`）+ union_varying_axes（`:83`）处理不规则组形状；xla.py 是纯 XLA 兜底。五份 dsv3 启动脚本对应 h100/16k/dropless/gb64/gb200 五个配置档位（`examples/maximoe/scripts/dsv3-*.sh`）。

## 7. 测试、CI 与工程化

测试三层金字塔：①单元——`tests/fake_devices.py` 以 _FakeClient/_FakeDevice 骗过 JAX 分布式初始化（`:24/:51`），make_mesh（`:77`）让无 GPU 环境跑通大部分套件；②专项——test_mpmd_api.py（2116 行，实验 API 最大）、test_schedules.py（503 行，`:109` 验证 DualPipeV 拒绝 num_stages≠2*mpmd_dim、`:291` KimiK2 参数化）；test_dime2 覆盖 NCCL send/recv 生命周期；③功能——functional_testing/ 的 dropout/passthrough 变量保值对照。scripts/run_tests.sh 还按 JAXPP_FAST_INFER_SHARDINGS/LICM 等 flag 矩阵复跑关键用例。注意反差：test_training.py 仅 52 行，与 training.py 407 行的复杂度不成比例——训练算子的保障主要靠 MaxiMoE 端到端。CI 文档链路（documentation.yml）用 docs/rendered/ 预渲染副本 + sphinx-build -W；Docker 是两层薄结构（Dockerfile.base 装依赖，`Dockerfile:17-20` 只换源码树）；`scripts/jax-run` 单机多进程拉起联调，`scripts/slurm/job.sh` 投集群。AGENTS 协作开发痕迹（CLAUDE.md/AGENTS.md 类工程实践）与 NVIDIA 其他仓一致。

## 8. 图谱构建说明与上手路径

**两缺陷自纠实录**（本图谱 merge 阶段的两处修正，写作时已核实）：
1. **重载去重**：core.py 的 `_get_fused_jaxpr_cached` 是 @overload 三连（`core.py:2218/:2231` 两个签名桩 + `:2244` 真实现；同类还有 `array_ops.py:62/:66`、`utils.py:275/:281`），朴素抽取会产出三个同名 function 节点。批产物按"同文件同名函数去重、保留首个签名段"归一，图谱中该函数仅一个节点（记 L2219-L2228 首段签名）。
2. **孤儿边兜底**：批产物存在端点指向未被任何批次分析符号的边（跨批引用/未抽取目标），merge 默认静默 drop 会丢真实依赖；本次对悬空端点走兜底归位而非一律丢弃，终态校验 0 孤儿边、0 重复 id（validator 0 issues）。

**新手上路路径**（按依赖序）：①`examples/basic.py` 跑通两级流水线 → ②`docs/usage.rst`+`examples/tutorial.ipynb`（31 cell）建立 API 手感 → ③读 `pipelining.py`（81 行全文）+ `schedules.py` 理解调度 → ④啃 `docs/compilation.md` 后精读 core.py 的 `mpmdify` 链路（第 4 节七步）→ ⑤`examples/mpmd.py`（817 行）看 MPMD 全貌 → ⑥MaxiMoE 按 model→kernels/ops→sm90/sm100 顺序读。性能调优先读 PERF_GUIDE.md（核心思想：TP/PP 尽量小、DP 近线性扩展、优化器状态可 offload）。

**速查锚**：编译 `_mpmd_jit` core.py:3984；切分 cluster_by_yield_eqns core.py:976；重排 reorder_nodes_with_schedule core.py:1876；传输 add_transfers core.py:2079；收尾 to_local_jaxprs core.py:2917；调度 DualPipeV schedules.py:611；训练 _pipelined_loop training.py:191；数组 spmd_to_mpmd_reshard array.py:434；传输建连 dime2.py:87；内核分派 backend.py:43。
