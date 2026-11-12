# 06 · Convolution 隐式 GEMM 体系与 transform/reduction 支撑域

## 角色定位

Convolution 是 CUTLASS"隐式 GEMM"哲学的最大受益者：卷积不重新发明 kernel，而是翻译成 GEMM 后复用整条流水线（图谱 L08 域 98 节点+L09 支撑域 71 节点）。决定性证据在 `include/cutlass/conv/kernel/sm90_implicit_gemm_tma_warpspecialized.hpp:60-72`——SM90 卷积 kernel `ConvUniversal` 特化体是**空类**，直接 `: public cutlass::gemm::kernel::GemmUniversal`（66 行），仅靠 65 行 SFINAE 约束入选。"conv kernel 就是 GEMM kernel，只换 ProblemShape 与 mainloop"在此是字面事实。2.x 世代走另一条路：`include/cutlass/conv/threadblock/` 下 20+ 个 `conv2d_fprop/dgrad/wgrad_*_tile_access_iterator_{analytic,optimized}.h` 用软件迭代器在加载侧完成 im2col 坐标重排；SM90 起这活交给硬件 TMA。

## 内部结构

问题形状层：`include/cutlass/conv/conv2d_problem_size.h:64` 的 `Conv2dProblemSize`（2.x）与统一抽象 `include/cutlass/conv/convnd_problem_shape.hpp:57` 的 `ConvProblemShape<ConvOp_, NumSpatialDimensions_>`——一个模板覆盖 1D/2D/3D。枚举三件套在 `include/cutlass/conv/convolution.h:88/96/102`。调度标记层：`include/cutlass/conv/dispatch_policy.hpp:53-55` 定义 `KernelImplicitTmaWarpSpecializedSm90/Cooperative/Pingpong` 三个 tag，53 行 Sm90 tag 显式继承 `gemm::KernelTmaWarpSpecialized`——conv 调度树嫁接在 GEMM 调度树上；`:81-82` static_assert 禁止 Cooperative/Pingpong。mainloop `include/cutlass/conv/collective/sm90_implicit_gemm_gmma_ss_warpspecialized.hpp`（785 行）提供 `:522 load_init`、`:547 load`、`:654 mma` 三段式，与 GEMM mainloop 同构但张量构造走 im2col。

## 外部连接

最值得钉版的跨树依赖：`sm90_implicit_gemm_gmma_ss_warpspecialized.hpp:47` 写着 `#include "cutlass/util/packed_stride.hpp"`，而该头文件物理上位于 `tools/util/include/cutlass/util/packed_stride.hpp`——**主 include 树反向依赖 tools/ 树**，扫描器按目录分批时这类跨树 include 边最易漏网。其 46-49 行的 `make_cute_packed_stride` 把宿主动态 stride 填进 CuTe 静态骨架，conv mainloop `:316-317` 用它转换 `problem_shape.stride_A/B`。另一路 `packed_stride_right_major` 内嵌在 `convnd_problem_shape.hpp:479-487`（右主序紧凑步长的编译期逆序累乘）。上游连接 GEMM：kernel include `gemm/kernel/gemm_universal.hpp` 与 `gemm/kernel/tile_scheduler.hpp`（46 行）；设备接口 `include/cutlass/conv/device/conv_universal_adapter.hpp:61` 的 `ConvUniversalAdapter` 镜像 `GemmUniversalAdapter`。硬件层：`include/cute/arch/copy_sm90_tma.hpp:419` 的 PTX `cp.async.bulk.tensor.3d.shared::cluster.global.im2col.mbarrier::complete_tx::bytes`——TMA 原生 im2col 模式；`include/cute/atom/copy_traits_sm90_im2col.hpp:92` 注释明言 traits 分两层（109 行 desc 版/172 行可执行特化）。

## 数据流

3.x 流程：宿主构造 `ConvProblemShape`（含 padding/dilation 几何）→ `ConvUniversalAdapter` 打包 Arguments → kernel 把 conv 形状投影为 GEMM (G=M*P*Q, N, K=C*R*S) → `load_init` 规整步长，producer warp 用 im2col TMA 按卷积坐标语义搬 A/B 到 smem → `mma` 消费 GMMA → epilogue 按 GEMM D 写回；dgrad/wgrad 靠交换 A/B 角色实现。2.x 相反：迭代器在 gmem 读取阶段做坐标映射，`include/cutlass/transform/threadblock/predicated_tile_iterator.h:143/156` 的谓词化迭代器（特化在 415/633 行）承载边界判定，`include/cutlass/transform/pitch_linear_thread_map.h:69` 定义线程→元素条带映射。支撑域另三条线：`transform/kernel/sparse_gemm_compressor.hpp`（2:4 稀疏压缩）、`transform/collective/sm90_wgmma_transpose.hpp`（转置）、`reduction/device/reduce_split_k.h:51` 的 `ReduceSplitK` 与 `tensor_reduce.h:64`、`tensor_reduce_affine_contiguous.h:66` 的 TensorReduction 家族。

## 设计决策

① 隐式 GEMM 而非独立 conv kernel：一套流水线服务两个算子域，代价是坐标几何压进 ProblemShape 与 TMA descriptor，换零重复维护。② 硬件 im2col 取代软件 im2col：坐标变换下沉 TMA 单元，2.x 迭代器仅服务旧架构。③ `ConvProblemShape` 用秩参数化收敛 1D-3D。④ packed_stride 双轨易混淆：tools/util 版服务 mainloop 动态注入，convnd 内嵌版服务宿主编译期构造，同名不同源。⑤ conv 调度禁 Cooperative/Pingpong（dispatch_policy.hpp:81）：dgrad 的 G 维展开与双 consumer 语义冲突。

## 新人提示

① 先通读 `sm90_implicit_gemm_tma_warpspecialized.hpp` 全文 76 行——"conv=GEMM"最短证明。② `cutlass/util/packed_stride.hpp` 不在主 include 树：独立编译须把 `tools/util/include` 加入 include path，否则 47 行那类核心头直接编译失败。③ 2.x 迭代器命名法 `conv{2d,3d}_{fprop,dgrad,wgrad}_{activation,filter,output_gradient}_*`，按算子×张量角色定位，勿通读。④ `Mode::kConvolution` 与 `kCrossCorrelation` 只差 filter 翻转，深度学习框架默认后者。⑤ wgrad 的 G=K 维度最易 padding 越界，用 kOptimized 与 kAnalytic 对拍。⑥ transform/reduction 当"通用 tile 搬运/归并工具箱"引用；`ReduceSplitK` 是 GEMM split-K 输出到最终 D 的胶水。
