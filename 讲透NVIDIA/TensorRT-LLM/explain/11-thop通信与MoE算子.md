# 11 · thop 通信与 MoE 算子：NVLS 集合通信、mhcOp 与 99 处 TORCH_LIBRARY

## 一、角色定位

`cpp/tensorrt_llm/thop/`（106 文件，约 3.3 万行）是 C++ kernel 世界的 **torch 算子门面**：99 个文件含 TORCH_LIBRARY 注册，把集合通信、MoE、GEMM、注意力、DiT 专属算子全部挂进 `trtllm` 命名空间供 PyTorch 后端调用。注意路径勘误：moeOp.cpp 不在 thop 根下，而在 `thop/moe/cutlass/moeOp.cpp`（2509 行）；mhcOp.cpp 239 行虽小，却是 DeepSeek-V4 mHC 稀疏注意力机制在本仓的暴露面。本主题覆盖 allreduce（NVLS 通信）与 MoE 两大簇，对应图谱 L14 层。

## 二、内部结构

**allreduceOp.cpp（2446 行）三算法面**。① 自研 one/two-shot fusion kernel：MIN_LATENCY 策略下按 `seq_len <= kOneShotMaxToken` 自动选 oneshot（allreduceOp.cpp:697-705）；MNNVL 版 `oneshotAllreduceFusionOp`/`twoshotAllreduceFusionOp` 的切换阈值 `kOneShotSizeThreshold = 64*1024*8*2`（:2192-2200）。② NCCL symmetric memory 路径（:470-500）：拿 raw ncclComm 后用 `NCCLWindowAllocator/createNCCLWindowTensor` 注册窗口，未注册输入需 memcpy——注释（:485-489）给出精算：memcpy 开销与 remote 操作收益都随消息线性增长，但本地 memcpy 更便宜，且 **multimem 把 O(N) 归约压成 O(const.)**，收益随 rank 数放大；切换点用 GB200 上实测回归起点拟合的线性模型（:493-495，a=-4986.43、b=156716.52），可用 `TLLM_NCCL_MIN_REGISTRATION` 环境变量覆盖。③ NVLS 多播内存：包含 `runtime/mcastDeviceMemory.h`（:35），与 multimem 指令族（xqa 线 system_barrier.h）同栈。注册面：`TORCH_LIBRARY_FRAGMENT(trtllm, m)`（allreduceOp.cpp:2312）+ CUDA/CompositeExplicitAutograd 双 IMPL（:2414/:2429）——**函数算子注册三段式是 thop 的统一姿势**。

**moe/ 子树六族**：`cutlass/moeOp.cpp`（2509 行，TORCH_LIBRARY :2499 + `m.class_<FusedMoeRunner>` :2501——全仓唯二的 class_ 注册之一）；`communication/moeAlltoAllOp.cpp`（1091 行，EP 通信）；`trtllmGen/` 三档精度 MoE（mxFp4 814 行/fp4 774 行/fp8 568 行，走 TRT-LLM Gen kernel）；`cuteDsl/cuteDslMoeUtilsOp.cpp`（603 行，CuTe DSL 桥）；另有 loadBalance/、marlin/、routing/。**mhcOp.cpp（239 行）**：`mhcBigFuseOp`（mhcOp.cpp:28）一次性融合 y_acc/r_acc 残差累加、hc_scale/hc_base 双参、post_mix/comb_mix 混合、RMSNorm（rms_eps）与 Sinkhorn 稳定化三参数（hc_sinkhorn_eps/hc_post_mult_value/sinkhorn_repeat）——V4 mHC 压缩器注意力的 φ GEMM 后处理全在这一个 op；`mhcGemmSqrsumFmaOp`（:44）是平方和 FMA 侧翼。注册同三段式（FRAGMENT :178 + IMPL :227/:236）。

**精度与领域 GEMM 家族**：cublasScaledMM/cublasFp4ScaledMM（class_ 注册 `CublasLtFP4GemmRunner`，cublasFp4ScaledMM.cpp:464，内部 AlgoCache 以 shape 为键缓存 cublasLt 算法选择）、cublasScaledMMLut.h 的 inline LUT（HashTuple 异或哈希，注释保留 nvprof 调优命令行）、fp4/fp8 全家族（fp4Gemm、fp8BlockScalingGemm、fp8PerTensorScalingTrtllmGenGemm、fp4xFp8GemmTrtllmGen 等）、cutlassScaledMM。**DiT 四件套**为 VisualGen 线服务：fusedDiTGateResidNormShiftScaleOp（FRAGMENT :262）/fusedDiTQKNormRope/fusedDiTSplitNorm/fusedDiTSplitQKNormRope。

## 三、外部连接

上游 kernel 实现分居 `kernels/`（customAllReduceKernels、mhcKernels、cutlass_kernels/*）与 `cutlass_extensions/`（weight-only、collective builder）；thop 只做张量校验、stream 获取与注册。下游消费者：`tensorrt_llm/_torch/custom_ops/`（Python 侧经 torch.ops.trtllm.* 调用）、FlashInfer/flash-attention 后端共用同一命名空间；attentionOp.cpp（1798 行，enqueueContext 近千行按架构×变体分派）与 mlaPreprocessOp、asyncUlyssesOp（序列并行）、compressorOp（V4 压缩器）共同喂注意力线。allreduce 的 mcast 路径与 MNNVL/DWDP 训练线（modules/dwdp）共享 NVLS 基座。

## 四、数据流

一次 decode 步的通信流：TP 组进 allreduce → 未过注册阈值走普通 NCCL；过阈值且 communicator 支持窗口注册 → symmetric 路径（memcpy 进窗口 + NCCL_SYMMETRIC 原语 + multimem 归约）；fusion 开启时直接 one/two-shot 自研 kernel（可能与 residual add/激活融合）。MoE 一轮：routing 选专家 → alltoAll 分发（moeAlltoAllOp）→ 分档精度 GEMM（trtllmGen fp4/fp8 或 cutlass moeOp 的 FusedMoeRunner）→ 再 alltoAll 聚回。mHC 层：φ GEMM（mhcGemmSqrsumFmaOp）→ Sinkhorn 归一化+混合+RMSNorm 全融合（mhcBigFuseOp）→ 稀疏 top-k 索引。

## 五、设计决策

① **FRAGMENT 而非整库注册**：99 文件共享 `trtllm` 命名空间必须用 TORCH_LIBRARY_FRAGMENT，每个文件自注册避免了单一巨注册点。② **经验拟合的切换阈值入代码**：GB200 实测拟合系数直接硬编码+环境变量逃生门，是"可解释的启发式"写法范本——比拍脑袋常数多了回归依据注释。③ **mhcOp 做"暴露面"而非"实现"**：239 行只做参数转译，kernel 在 mhcKernels——与 DeepSeek 上游 TileKernels 的分工同构，方便算法侧独立演进。④ **class_ 仅两处**（FusedMoeRunner/CublasLtFP4GemmRunner）：有状态 runner（缓存 algo/workspace）才值得类注册，无状态 op 一律函数式——最小化 Python 侧持有的 C++ 对象。⑤ LUT 保留 nvprof 命令行注释：调优数据的可复现性内嵌在代码里。

## 六、新人提示

加新算子的模板：抄 mhcOp.cpp 的三段式（FRAGMENT+CUDA IMPL+Composite IMPL），Python 侧在 custom_ops 配 register_fake。找 MoE 入口别在 thop 根下找 moeOp（路径勘误钉版）。调 allreduce 性能先看 TLLM_NCCL_MIN_REGISTRATION 与策略日志，确认走的是 symmetric 还是 fusion 路径——两条路的调优手段完全不同。cublasScaledMMLut.h 的表是离线调优产物，换 GPU 代际要重跑（注释里的命令就是重跑方法）。mhc 参数名与 V4 论文的 Sinkhorn 节对应关系：hc_sinkhorn_eps/sinkhorn_repeat 即稳定化迭代（论文未写的 max 减法稳定化就在 mhcKernels 实现里）。图谱提示：class_ 注册是 tree-sitter 盲区，两个 Runner 类是手补节点（见 README 勘误）。
