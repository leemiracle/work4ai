# fp16_bf16_gemm：原生 TIRx kernel 家族的最佳入门样本

> 文件：`tirx_kernels/basic/fp16_bf16_gemm.py`（745 行，注册名 `fp16_bf16_gemm`）
> 知识图谱定位：「原生基础 kernel 层」，complexity=complex；导览第 9 站"kernel 家族 I"的起点。

## 角色定位

这是 TIRx-kernels 里**没有单一上游项目**的原生 kernel 代表：一个完整的 SM100（Blackwell）FP16/BF16 GEMM，计算 `C[M,N] = A[M,K] · B[N,K]^T`（B 按 (N,K) 行主序存放，所以 transB=False）。它对标的对象是 cuBLAS——`run_test` 直接用 `torch.matmul` 做正确性基准，`run_gpu` 里还挂了 deepgemm 的 cublasLt/bf16 两条参考线。整个 basic 家族（fp16_bf16_gemm、nvfp4_gemm、rmsnorm、allgather_gemm、gemm_reduce_scatter）都是这个模式：**用 Kern DSL 从零写出一个能和厂商库掰手腕的算子**，因此它是学习"Kern 写法"的最佳起点——745 行里浓缩了 TMA、tcgen05、TMEM、warp specialization、CLC 调度全部核心设施，但还没有移植 kernel 那些上千行的元数据工程。

## kernel 算法

数学上就是标准分块 GEMM：把输出切成 CTA tile（CTA_M 固定 256，CTA_N 按形状 64~256），K 维按 BLK_K（64 或 128）步进累加。所有计算由 `tcgen05.mma.cta_group::2.kind::f16` 完成——**2-SM 集群 MMA**：一对 CTA（`cbx = K.cta_id_in_cluster([2,1])` 区分偶奇）合起来算一个 256×MMA_N 的 tile，每个 CTA 只出 128 行 A（BLK_M）和 MMA_N/2 行 B，累加器放在 TMEM（tensor memory，512 列）。A/B 各自按 `((m_idx*2+cbx)*NUM_CONSUMER+c)*BLK_M` 计算本 CTA 负责的行段，D 的写出坐标同理按 cbx 展开——集群语义渗透到每一个地址表达式。调度不是静态 grid 轮转，而是 **CLC（Cluster Launch Control）work-stealing**：`K.ClusterLaunchControlScheduler` 按 `l2_group_size` 把 tile 分组成 L2 友好的超组，三个 worker（ld_sched/mma_sched/wb_sched）各自从同一调度流消费坐标，CTA 算完领下一块，天然负载均衡。grid 大小是 `NUM_M_TILES * NUM_N_TILES * 2`（×2 就是集群的两个 CTA），`min_blocks_per_sm=1` 表明这是 persistent 形态。

## 代码结构

单文件五个函数，形状干净：`prepare_data`（固定 CUDA 设备序号生成 A/B/C）→ `_make_device_kernel`（trace 主体，约 530 行）→ `run_test`/`prepare_bench`/`run_gpu`（正确性与基准）。设备代码的组织方式值得背下来：

- **`host_prelude`**：发射前在 host 上用 `runtime.cuTensorMapEncodeTiled` 编码 A/B/D 三个 TMA descriptor（`K.stack_alloca("tensormap")`），BLK_K=128 时 A/B 走 3D map、否则 2D；
- **签名即类型**：`gemm.__annotations__ = {"a": K.gptr[AB_DTYPE,(M,Kdim)], ...}`，最后 `K.kernel(warps=WARPS, arch="sm_100a", grid=..., host_prelude=...)` 包装返回；
- **角色划分**：`K.specialize()` 声明 loader/scheduler/mma/idle（producer 侧）与 consumer（epilogue 侧）五个角色，再用 `sp.register_scope` 给 producer 圈 56 个寄存器、consumer 圈 224 个——同一个 kernel 里不同 warp 组拿不同寄存器预算，这是 `setmaxnreg` 的 DSL 化；
- **双流水线**：`smem_pipe`（full="tma"，empty="tcgen05"）管输入 stage 的借还，`tmem_pipe`（full="tcgen05"，empty="mbar"）管累加器槽位；`K.PipelineState` 在各角色手里独立推进 stage/phase。smem 布局同样有戏：barrier 与 TMEM 地址槽先落在池底，`smem.pool.move_base_to(1024)` 之后再声明 Asmem/PIPE_DEPTH/BLK_M/BLK_K、Bsmem、Dsmem 三个数据缓冲——声明顺序复刻原始字节布局，收尾的 `tmem_fin`（1-arrival 跨 CTA mbarrier）让 overlap 形态的 teardown 比 cluster_sync 更轻；
- `GEMM_CONFIGS` 逐形状调优表：N=1024 用 overlap_epilogue 双 consumer，N≥4096 用深 wb_pipe_depth——**每个 knob 都在 trace 时烘焙成常量**，这是整个仓库"config → 特化"哲学的缩影。

## 性能设计

SM100 特性的教科书式组合拳：① TMA `cp.async.bulk.tensor` 做 2-SM 输入搬运（`cta_group::2` 后缀把完成 mbarrier 路由到集群），完成字节数由 loader 侧 `expect_tx` 一次性预告 `2*(NUM_CONSUMER*BLK_M*BLK_K + BLK_N*BLK_K)*ELEM_BYTES`——注意这是**两个 CTA 合计**的字节数，只有 cbx==0 的 CTA 拥有这条 mbarrier；② tcgen05 f16 MMA 指令级描述符（`encode_instr_descriptor`，M=256/N=MMA_N/K=16）+ `SmemDescriptor` 直接在 smem 上做矩阵操作数，swizzle 一律 SW128B（`_swizzle_for_row_bytes` 按行字节数降级到 64/32B）；③ TMEM 读回（`tcgen05.ld.32x32b.x16/32/64` 按 EPI_N 选宽度）后用打包 `cvt.rn.f16x2.f32` 减半转换开销，`st.shared.v4` 保证每次 128-bit 落在单个 swizzle chunk 内避免 bank conflict；④ epilogue 的 TMA store 挂 **evict-first L2 cache hint**（0x12F0...）——输出流式数据不污染缓存。更珍贵的是注释里留下的**实测教训**：descriptor 步进用平凡 64-bit 加法而不是 `add_16B_offset` helper（实测 ptxas STACK 72→168B、SASS +25%）；`elect_sync()` 必须直接写进 `If` 条件保收敛（G3 hazard）；consumer 正好卡在 255 寄存器天花板，多一个 live register 就 spill。这些"为什么这样写"的论证正是原生家族的价值——没有上游可抄，每个决定都要自己量出来。

## 与其他家族对比

它和移植家族（cudnn/flashinfer/msa）的本质区别在于**对照物**：原生 kernel 的正确性基准是 cuBLAS 这类库，性能基准是公开数字；移植 kernel 则锁定上游 commit 做逐位对照（`reference_requirements`），本文件没有这个字段。有意思的是注释里保留的 `orig:L134-145` 行号引用——说明它虽属"原生"，仍以某个原始实现为锚做翻译对照，这是仓库注释纪律的体现。另外它是唯一同时展示 CLC + 双 consumer overlap + epilogue 三态调优的文件，移植家族因为要贴上游结构，反而很少这么自由地重排。

harness 侧同样值得对照：`run_test` 走 `compile_kernel` → `ex(A, B, C_tvm)` → 与 `torch.matmul(A, B.T)` 比对（rtol=0.001/atol=0.01）；`prepare_bench` 用 `cuda_initialization_guard()` 包住编译——**CPU 阶段完成特化与编译、不碰 CUDA 运行时**，产出 `PreparedBench` 状态对象后再交给 GPU 阶段的 `run_gpu`，这正是 bench_suite 两阶段协议的雏形。BF16 形状还额外挂 deepgemm 的 cublasLt 与 bf16_gemm_nt 两条参考线，让" ours vs 厂商库"的对比有多个锚点。

## 新人提示

推荐阅读顺序：先读 `GEMM_CONFIGS` 和文件头部的 PTX 指令常量区建立词汇表 → `host_prelude` 理解 TMA map 怎么编码 → 角色划分区（`sp.role`）看懂 warp 分工 → `loader_body`/`mma_body`/`consumer_body` 三个角色各读一遍，对照 `K.Pipeline` 的 full/empty 语义 → 最后读 `writeback` 的 overlap 与 no-overlap 两条 epilogue 路径（前者逐 chunk 读写重叠下一 tile 的 MMA，后者先搬空 TMEM 再统一写出——两条路径的取舍本身就是极好的流水线教材）。读懂这个文件，仓库里任何 kernel 的 DSL 用法你都不再陌生；之后带着"这里为什么不用 CLC/为什么单 consumer"的问题去看移植家族，鉴别力会立刻上一个台阶。
