# 精讲：deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d2d.cuh —— SM90 FP8 主力内核

> 原文件：`deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d2d.cuh`（DeepGEMM，454 行）

## 一、角色定位

这是 DeepGEMM 在 Hopper（SM90）上的**旗舰 FP8 GEMM 设备内核**（图谱 tour 第 6 步），也是 DeepSeek-V3 训练中 MoE 密集算量的主力承担者。"1D2D"指缩放因子粒度：A（激活）按 128 通道逐块缩放（1D），B（权重）按 (N/128, K/128) 块级缩放（2D）。文件只含一个 `__global__` 模板函数 `sm90_fp8_gemm_1d2d_impl`，由 JIT 生成的 wrapper 在运行时实例化——约 20 个模板参数（SHAPE_M/N/K 编译期形状、BLOCK_*、swizzle 模式、kNumStages、线程数、multicast、kNumSMs、GemmType、cd_dtype、epilogue）全部由 heuristics 决定。

## 二、内部结构

- **`dispatch_num_former_iters`**：编译期分派模板——动态值 `num_former_iters`（块内 B 缩放交界位置）按 kGap 步进特化为 `cute::Int<N>` 常量，逼编译器生成无分支代码。
- **内核主体**分两大分支：TMA warp 组（生产者）与数学 warp 组（消费者），通过共享内存里的 `full/empty` 双 barrier 阵列握手。
- **共享内存手工布局**：一段 `extern __shared__` 依次摆放 D、各级 A、各级 B、各级 SFA、SFB、barriers，D 区 1024B 对齐以满足 128B swizzle 的 TMA。

## 三、外部连接

include CUTLASS 的 `barrier.h`（`ClusterTransactionBarrier`）、`reg_reconfig.h`（warpgroup 寄存器再分配）、CUTLASS 的 `copy_sm90_tma.hpp`（TMA 拷贝原语）；自家依赖 `mma/sm90.cuh`（`FP8MMASelector` 选 WGMMA 指令形状）、`scheduler/gemm.cuh`（持久化块调度器 `sched::Scheduler`）、`ptx/wgmma.cuh`（WGMMA 内联 PTX）、`epilogue/transform.cuh`、`comm/barrier.cuh`。宿主包装是 `csrc/jit_kernels/impls/sm90_fp8_gemm_1d2d.hpp`，由 `apis/gemm.hpp` 调用。

## 四、数据流

**生产者侧**（`warp_idx >= kNumMathThreads/32`）：寄存器让渡到 40 个；单个 elect warp 循环 `scheduler.get_next_block(m_block_idx, n_block_idx)` 持久化取块，对每个 k 块：等 `empty_barrier`（消费者放行）→ 发 TMA 拷贝 A、SFA、B 到本级共享内存（multicast 有效时 A 或 B 广播到 cluster）→ `arrive_and_expect_tx` 声明字节数。**消费者侧**：寄存器扩到 232/248 个；先把本块需要的 SFB 用 `st_shared` 预载入共享内存；对每个 k 块：读 `scale_b_0/1` → 等 `full_barrier` → 对 BLOCK_M 内多个 wave 各发一组 `WGMMA::wgmma`（`warpgroup_arrive`/`commit_batch`/`wait<0>`）→ 最后一个 wave 到达 `empty_barrier_arrive`（multicast 时精确通知对端 CTA）→ **提升（promotion）**：`final_accum += (scale_a × scale_b) × accum`，用 `i < num_former_iters` 的谓词选择 scale_b_0 或 scale_b_1，避免双循环分支。计算完毕：`SM90_U32x2_STSM_N` 把 float 累加器转 BF16 写回 smem_d（含手工 swizzle 位运算），`tma_store_fence` 后由前若干线程发 2D/3D TMA store 写回全局 D。

## 五、设计决策

- **缩放后置**：WGMMA 在 FP8 原生累加器上跑满 Tensor Core，缩放乘加放在寄存器 promote 阶段——这是 DeepGEMM 相对"先反量化再 GEMM"路线的核心取舍。
- **Warp 组角色分工 + 寄存器再分配**：TMA 组只留 40 寄存器，数学组拿 232/248，`warpgroup_reg_dealloc/alloc` 精确调配。
- **持久化内核**：grid 恒为 numSMs，块由调度器动态领取，消尾部空转；`is_computation_valid` 跳过无效块仍走 barrier 保同步。
- **谓词化提升与编译期分派**：`num_former_iters` 特化 + 谓词选择，注释强调"谓词远快于两个循环"。
- **PDL 支持**：入口 `cudaGridDependencySynchronize()` 等上游内核，`kMustUseUniformedScaleB`（BLOCK_K 整除 BLOCK_N）时省第二次 SFB 读取。
- **防御断言**：`DG_STATIC_ASSERT` 编译期锁定 BLOCK_K==128、CD 仅 BF16、multicast ≤2 等约定。

## 六、新人提示

先读 `scheduler/gemm.cuh` 弄清三种 GemmType 的块遍历差异再看本文件。调试期可对照 `DG_JIT_DUMP_SASS` 产物找 WGMMA 指令密度。两个易踩点：①共享内存布局是硬编码偏移，改 BLOCK 尺寸或加缓冲必须同步改 SMEM_* 常量，否则静默越界；②swizzle 写回的位运算段有注释"改前想三遍"，确实非必要别动。兄弟内核 `sm90_fp8_gemm_1d1d.cuh`（双方都 128 通道缩放）与 `sm90_fp8_gemm_1d1d` 的 SM100 版本可对照阅读。
