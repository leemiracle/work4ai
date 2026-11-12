# 02 · 算子线：CUTLASS 与 GEMM 的第一性原理——张量核心把深度学习变成矩阵乘法，然后呢？

> 《NVIDIA 全栈深讲系列》第 02 篇。主仓 CUTLASS 4.8.0（本地 `/usr-data/data2/repos/agent-repos/NVIDIA/cutlass/`，commit `0b55a2f6`，2026-09-23），辅仓 cudnn-frontend / AMGX / FasterTransformer / MatX / CUDALibrarySamples（deepwiki 全量抓取 2026-10-26）。所有行号锚均从本地源码核实；硬件峰值数字为 NVIDIA 公开 spec 量级（dense、不含稀疏加速）。

## 一、第一性原理设问：为什么"深度学习计算"最后都塌缩成 GEMM？

把任何一个主流模型的 profiler 时间线拉出来，90% 以上的时间都在同一类 kernel 里：**矩阵乘** $C = A \times B$（GEMM，GEneral Matrix Multiply）。这不是巧合，是三次塌缩的结果：

1. **全连接层**天然就是 GEMM：$Y = XW^\top$，输入 $X \in \mathbb{R}^{B \times K}$，权重 $W \in \mathbb{R}^{N \times K}$；
2. **卷积塌缩成 GEMM**（im2col / implicit GEMM）：把每个输出位置感受野内的像素摊成一行，卷积核摊成一行，一次 conv 就是一次 GEMM——CUTLASS 的 `conv/` 目录干脆直接叫 `implicit_gemm`（如 `include/cutlass/conv/kernel/sm100_implicit_gemm_tma_warpspecialized.hpp`）；
3. **注意力塌缩成两步 batched GEMM**：$\mathrm{softmax}(QK^\top)V$ = 一次 $Q \cdot K^\top$ 的 batched GEMM（每个头一批）+ 一次 $\mathrm{score} \cdot V$ 的 batched GEMM，中间夹一个 softmax——这就是 flash attention 要融合的"三明治"，而三明治的两片面包都是 GEMM。

所以 GEMM 的效率就是深度学习的效率。但 GEMM 凭什么能高效？第一性账：

**计算量与访存量的比。** 三个 $N \times N$ 矩阵相乘，需要 $2N^3$ 次浮点运算，但只涉及 $3N^2$ 个数据元素——算术强度（arithmetic intensity，FLOP/字节）为 $O(N)$。N 越大，每个字节能"榨"出的计算越多。对照 roofline：GPU 的**机器平衡点** = 峰值算力 ÷ HBM 带宽。低于这个 FLOP/byte 的 kernel 被带宽卡死（memory-bound），高于它才被算力卡死（compute-bound）。大 GEMM 的 AI 随 N 增长，必然穿过平衡点进入 compute-bound 区——**这是唯一一类"天然吃满算力"的规则计算**，所以它值得用专门的硬件单元（tensor core）去伺候。

再看三代硬件的机器平衡点怎么移动（公开 spec 量级，dense 口径）：

| GPU | 张量核心峰值（dense） | HBM 带宽 | 机器平衡点 (FLOP/B) |
| --- | --- | ---: | ---: |
| A100 80GB SXM | FP16 312 TFLOPS | ~2.0 TB/s | ~153 |
| H100 SXM | BF16 ~990 TFLOPS | ~3.35 TB/s | ~295 |
| B200 | FP8 ~4.5 PFLOPS / FP4 ~9 PFLOPS | ~8 TB/s | ~562（FP8）~1125（FP4） |

规律刺眼：**A100→H100 张量核心峰值 ×3.2、带宽 ×1.6；H100→B200 再 ×4.5 与 ×2.4**。算力涨得永远比带宽快，平衡点每代接近翻倍。两个直接推论，就是本篇后面所有机制的伏笔：

- **推论一（数据复用必须更狠）**：同样的 tile 大小，昨天够用的搬运策略今天就落到 memory-bound 区。分块要更大、层级要更深（Hopper 起 A/B 矩阵直接留在 shared memory 里喂矩阵指令，Blackwell 干脆给 accumulator 单开一块 tensor memory）；
- **推论二（低精度 = 直接对带宽动手）**：FP8→FP4 每砍一半字节，等于把同一个 GEMM 的 AI 翻倍。这就是 B200 平衡点在 FP4 口径下冲到 ~1125 的原因——也是第 05 篇"低精度只放带宽路径"精度策略的硬件根源；
- **推论三（fusion/epilogue 价值上升）**：GEMM 本体 compute-bound、前后处理（量化、激活、归约）memory-bound，把后者塞进 GEMM 出口（epilogue）就能白捡——融合不是炫技，是内存墙的物理压力传导到软件形态。

## 二、直觉层：分块 = 把"每个元素被用 N 次"锁进存储层级

朴素 GEMM kernel（每线程算 C 的一个元素，直接从全局内存读 A、B）慢在哪？$O(N^3)$ 次乘加对应 $O(N^3)$ 次**全局内存搬运**——每个 $a_{ik}$ 被读 $N$ 次、每次都从 HBM 走一遍。而计算只值 $O(N^3)$，搬运也值 $O(N^3)$，两者同阶，于是带宽成了天花板。张量核心峰值再高也救不了：**数据到不了计算单元附近**。

解法只有一个方向：利用 $a_{ik}$ 会被用 $N$ 次这个事实，**读一次、用很多次**——把复用锁进存储层级。这就是分块（tiling）：

1. **第一级（CTA → shared memory）**：把 C 切成 $BM \times BN$ 的 tile，把 A 的 $BM \times K$、B 的 $K \times BN$ 分 $BK$ 一段段搬进 shared memory。搬运量从 $O(N^3)$ 降到 $O(N^3/BM + N^3/BN)$ 级——tile 越大，HBM 流量越省；
2. **第二级（warp → register）**：tile 内再切 warp 级子块，A/B fragment 用 `ldmatrix` 类指令从 shared memory 装进寄存器，每个线程持有一撮碎片；
3. **第三级（MMA 指令）**：一个 warp 发一条矩阵指令，硬件在寄存器 fragment 上打完一整块小 GEMM，accumulator 常驻寄存器，直到 K 维循环结束才落盘。

数据流：**HBM →（TMA 异步搬运）→ shared memory →（swizzled 布局）→ 寄存器 fragment / tensor memory →（MMA）→ accumulator → epilogue → HBM**。每一级箭头都是在对抗"带宽涨不过算力"。

但 shared memory 只有 ~228 KB 且分 32 个 bank（每 bank 4 字节宽）。MMA 的 fragment 装载模式是固定 stride 的——如果 A tile 按行主序原样存放，一列连续元素 stride 恰好 128 字节 = 32 bank 整周期，**所有线程打到同一个 bank**，串行化。解法是 swizzle：在 shared memory 地址上做 XOR 位翻转，把"逻辑连续"与"物理 bank"错开。CUTLASS 把它做成了代数对象：

> `include/cute/atom/mma_traits_sm90_gmma.hpp:75-78`：
> `Layout_MN_INTER_Atom_Bits = ComposedLayout<Swizzle<0,4,3>, smem_ptr_flag, Layout<Shape<_128,_8>,Stride<_1,_128>>>`（以及 `Swizzle<1,4,3>` SW32 / `Swizzle<2,4,3>` SW64 / `Swizzle<3,4,3>` SW128 三档）

`Swizzle<B,M,S>` 三个参数就是"翻转多少位、从哪翻起"——swizzle 在这里不是运行时变换，而是**编译期烙进 layout 的位运算函数**，MMA 硬件（WGMMA/tcgen05）在从 shared memory 取数时按同一个函数解码，两边咬合。这就是 CUTLASS 的核心哲学第一次露脸：**布局是一等公民，用代数（Shape/Stride/Swizzle 的组合）描述，编译期化简**。

## 三、机制层：张量核心三代指令如何改写 kernel 结构，CUTLASS 模板如何跟着走

### 3.1 指令谱系：wmma → mma.sync → WGMMA → tcgen05

张量核心不是一块"更快的乘法器"，每一代指令都改变了**数据在哪个存储层级、由谁搬运、accumulator 放哪**，从而改写了 kernel 的骨架：

| 代 | 指令 | 源码锚（PTX 内联） | 操作数来源 | accumulator | 发起者 | kernel 结构后果 |
| --- | --- | --- | --- | --- | --- | --- |
| Volta/Turing | `wmma` | `include/cutlass/arch/wmma.h`（粗粒度 16×16×16 API） | 寄存器 | 寄存器 | warp 集体 | 简单两级 tiling 即可 |
| Ampere/Ada | `mma.sync.m16n8k16` | `include/cutlass/arch/mma_sm80.h:317` | 寄存器 fragment（`ldmatrix` 装载） | 寄存器 | warp 集体 | smem→寄存器两级装载 + swizzle |
| Hopper | `wgmma.mma_async` | `include/cute/arch/mma_sm90_gmma.hpp:158`（`m64n8k16` 起，N 可至 256） | **A 可直接从 shared memory 读** | 寄存器 | warp 集体但**异步** | producer/consumer warp 特化 + TMA + mbarrier |
| Blackwell | `tcgen05.mma` | `include/cute/arch/mma_sm100_umma.hpp:111`（f16）；`:1277`（`kind::mxf8f6f4.block_scale`，SFA/SFB 缩放因子是显式操作数 `[%5], [%6]`） | shared memory | **tensor memory（TMEM）** | **单个线程发起** | MMA 与 epilogue 彻底解耦，CTA pair / cluster 协同 |

三代的关键跃迁值得展开：

**Ampere（`mma.sync`）**：指令形状固定（如 m16n8k16），warp 里 32 个线程各持 A/B 的碎片和 C 的 4 个累加值。寄存器是唯一的中转站，所以 kernel 的大量代码在干"搬运工"的活：算地址、`ldmatrix`、对齐 fragment。锚点原文：

> `include/cutlass/arch/mma_sm80.h:317`：`asm volatile("mma.sync.aligned.m16n8k16.row.col.f16.f16.f16.f16 {%0,%1}, {%2,%3,%4,%5}, {%6,%7}, {%8,%9};\n" ...`

同文件 385 行起是 BF16 变体、589 行起是 INT8 变体——**一条 PTX 指令对应一个精度档**，这正是 CUTLASS 模板要按 dtype 展开的硬件原因。

**Hopper（`wgmma.mma_async`）**：两个质变。其一，A 操作数可以**不经过寄存器**、由硬件直接从 shared memory 读（描述符编码布局与 swizzle），搬运工代码大幅消失；其二，指令是**异步**的——warp 发出后继续干别的，用 `wgmma.commit_group/wait_group` 收割。配套的搬运也不再是逐 warp 的 `cp.async`，而是 **TMA**（Tensor Memory Accelerator）：

> `include/cute/arch/copy_sm90_tma.hpp:117`：`"cp.async.bulk.tensor.2d.shared::cta.global.mbarrier::complete_tx::bytes.L2::cache_hint"` ——一个线程发一条，硬件把整块 tile 从 HBM 搬进 smem，完成后通过 mbarrier 唤醒消费者。

于是 kernel 骨架从"所有 warp 干一样的活"变成**warp 特化（warp specialization）**：producer warp 只管发 TMA + 挂 barrier，consumer warp 只管发 WGMMA + 等 barrier。多级流水（stage）让第 k+1 块的搬运与第 k 块的计算重叠——这就是 CUTLASS dispatch policy 里 `KernelTmaWarpSpecialized` 一族标签的含义（`include/cutlass/gemm/dispatch_policy.hpp:119-123`：`KernelTmaWarpSpecialized` / `...Pingpong` / `...Cooperative` 三兄弟——Pingpong 让两批 consumer warp 交替掩住 epilogue 的尾巴，Cooperative 让全部 warp 合作一个 tile）。

**Blackwell（`tcgen05.mma`）**：accumulator 搬出寄存器、进**tensor memory**（TMEM，新存储层；几何常量在源码里就是 128 行 × 512 列 × 32bit = 每 SM 256KB——`include/cute/arch/tmem_capacity_sm100.hpp:36-38`，且 Sm107/Rubin 已扩到 576 列）。连锁反应：MMA 指令不再需要 32 个线程凑寄存器，**一个线程**就能发起一整条 tile 级矩阵乘；epilogue 从"各线程算完各自写"变成一个独立的"TMEM→寄存器→HBM"阶段，可由专职 warp 处理，天然与 MMA 重叠。CUTLASS 4.x 的 SM100 mainloop（如 `include/cutlass/gemm/collective/sm100_blockscaled_mma_warpspecialized.hpp`）就是围绕"异步代理（async proxy）+ mbarrier 数组"组织的。更重要的量价：`kind::mxf8f6f4.block_scale` 变体（`mma_sm100_umma.hpp:1277`）把**每 32 个元素一组的缩放因子 SFA/SFB 作为指令操作数**——低精度不再只是"换个 dtype"，缩放本身进了硬件数据通路（§3.3）。

### 3.2 CUTLASS 模板架构：为什么是"编译期 kernel 生成器"

GEMM 的设计空间是**各维度笛卡尔积**：{SM80/90/100/103/107/120} × {FP64…NVFP4 十余档} × {行主/列主 × 对齐度} × {tile 形状} × {schedule} × {epilogue}——组合数百万级。运行期多态（虚函数）在 kernel 里不可接受（每 MMA 循环一次查表就是灾难），唯一出路是**把组合压进模板参数，让编译器各自实例化一份代码**。CUTLASS 因此是"用 C++ 模板写的 kernel 生成器"，而非"kernel 库"。

**2.x 时代（Ampere 及以前）**：分层金字塔 Device → Kernel → Threadblock → Warp → Thread，每层一个模板类，典型入口：

> `include/cutlass/gemm/device/gemm.h:233`：`class Gemm {` —— 模板参数表就是那份著名的十几个参数（`ElementInputA/LayoutInputA/...`），底层由 `DefaultGemmConfiguration` 按 OpClass（`arch::OpClassSimt` / `OpClassTensorOp`）静态分派到各代 mma 实现。布局经 `TensorRef`（`include/cutlass/tensor_ref.h:152`：`class TensorRef`）——指针 + Layout 的组合体，把"数据在哪"与"怎么走"分开。

**3.x/4.x 时代（Hopper 起）**：kernel 被重组成三段拼装：`CollectiveMainloop`（TMA 装载 + MMA 流水）+ `CollectiveEpilogue`（TMEM/寄存器 → 激活 → HBM）+ `TileScheduler`（多 tile 持久化调度）。用户不再直接拼层级，而是各给一个 **CollectiveBuilder**：

> `include/cutlass/gemm/collective/collective_builder_decl.hpp:93`：`struct CollectiveBuilder { static_assert(sizeof(ElementA) == 0, "Could not build a collective for given parameters."); };` ——这是主模板，永远编译失败；真正实现在 builders 目录下**按 ArchTag×OpClass×KernelSchedule 的偏特化**里。例如 SM90 GMMA 偏特化：

> `include/cutlass/gemm/collective/builders/sm90_gmma_builder.inl:209`：`struct CollectiveBuilder<arch::Sm90, arch::OpClassTensorOp, ...>`，`enable_if_t<is_any_of_v<KernelScheduleType, KernelTmaWarpSpecialized, KernelTmaWarpSpecializedCooperative, KernelTmaWarpSpecializedPingpong, ...>>` —— **错误信息即文档**：主模板的 static_assert 保证非法组合在编译期爆炸并给出可读原因；偏特化的 enable_if 就是"该架构支持哪些调度"的机器可读清单。builders/ 目录按代分层（`sm90_*.inl` 2 个、`sm100_*.inl` 16 个、`sm120_*.inl` 7 个、`sm107_*.inl` 5 个——Blackwell 家族变体最多，因为 block-scaled/sparse/mixed-input/planar-complex 各要一份）。

epilogue 侧对称地有第二个 builder（`include/cutlass/epilogue/collective/collective_builder.hpp:70`：`struct CollectiveBuilder`），融合算子（激活、量化、residual 加法）在模板参数里声明，编译期织进出口阶段——回扣 §一推论三：**epilogue 融合在 API 形态上就是"mainloop 与 epilogue 两个 builder 平起平坐"**。

这套架构的代价与回报都极端：回报是零抽象开销、组合自动正确（布局/指令/流水由 builder 咬合）；代价是模板实例化爆炸——CUTLASS Profiler 全量构建要数小时、二进制数 GB，普通用户绝不该全量编译。

**CuTe 与 CuTe DSL（Python）**：3.x 的地基是 CuTe——把布局做成代数对象（`include/cute/layout.hpp:99`：`struct Layout`，由 `Shape` 与 `Stride` 两个编译期向量构成，`Layout<Shape<_128,_8>, Stride<_1,_128>>` 就是一个 128×8 行主 tile），切片、组合、配 swizzle 全是编译期符号运算。CUTLASS 4.x 再把这套东西搬进 Python：**CuTe DSL** 用 MLIR 做运行期 JIT，同一套 tile/MMA atom 概念，但开发循环从"改模板→nvcc 十分钟"变成"改 Python→秒级编译"。官方教学序列在 `examples/python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/`：

> `fp16_gemm_0.py:80`：`@cute.kernel` 装饰器标记 device 函数；`:295`：`@cute.jit` 标记 host 侧入口；`:298`：`op = tcgen05.MmaF16BF16Op(`，随后 `:302-305` 传入 `tcgen05.CtaGroup.ONE` / `OperandSource.SMEM` / `OperandMajorMode.K` —— Python 里声明式选 MMA atom，与 C++ 模板参数一一对应。

教程序列 `fp16_gemm_0..6.py` 逐步加机制（0=裸 kernel，6=完整 warp-specialized 流水，共 6400 余行阶梯），旁边就是 `nvfp4_gemm_0/1.py`——NVFP4 的第一课与 FP16 同层展开。同目录 `hopper/`、`blackwell/`（attention/blockscaled_gemm/grouped_gemm/moe 等十类 kernel）是 DSL 的实战库；TRT-LLM 的 `Sm100MegaMoEKernel` 已用 CuTe DSL 重写（见第 05 篇 §3.3），证明这条 Python 线已进生产。

### 3.3 精度谱：每一档砍的是指数位还是尾数位

浮点数 = 符号位 + 指数位（动态范围）+ 尾数位（相对精度）。低精度谱系不是匀速滑坡，而是**两条独立的轴**：

| 类型 | 位宽 | 指数/尾数 | 动态范围 | 相对精度 | 出现动机 |
| --- | --- | --- | ---: | ---: | --- |
| FP32 | 32 | 8/23 | ~10^±38 | ~1e-7 | 基准 |
| TF32 | 19(存32) | 8/10 | 同 FP32 | ~1e-3 | A100：**只砍尾数**，FP32 代码零改动吃到 TC 加速 |
| BF16 | 16 | 8/7 | 同 FP32 | ~8e-3 | 训练稳定（范围优先） |
| FP16 | 16 | 5/10 | ~65504 | ~1e-3 | 推理传统档，范围小易溢出 |
| FP8 e4m3 | 8 | 4/3 | ±448 | ~6e-2 | 存激活（范围中等精度差） |
| FP8 e5m2 | 8 | 5/2 | ±57344 | ~1.2e-1 | 存梯度（范围优先） |
| MXFP8 | 8+scale | 4/3 + ue8m0/32 元素 | scale 撑开 | 同 e4m3 | OCP MX 标准：块缩放进硬件 |
| MXFP4 | 4+scale | 2/1 + ue8m0/32 元素 | ±6 × scale | ~2.5e-1 | 权重极致压缩 |
| NVFP4 | 4+scale | 2/1 + **ue4m3/16 元素** | ±6 × scale | 同上 | NVIDIA 变体：**浮点缩放、粒度减半** |

为什么 FP8 之后必须上 scaling？e4m3 只有 448 的顶——LLM 激活里的 outlier 动态范围常超千倍，单张量一个 scale 要么头部溢出要么尾部下溢。块缩放（每 32 个元素一组幂次 scale ue8m0）把"跨块的范围差"交给 scale、"块内精度"交给 e4m3——**范围与精度解耦**。NVFP4 再进一步：16 元素一组、scale 本身是 e4m3 浮点（能表达更细的相对修正），量化误差显著低于 MXFP4，这是 Blackwell 上 4-bit 权重能落地的原因。硬件侧对应物就是 §3.1 那条 `kind::mxf8f6f4.block_scale` 指令——SFA/SFB 是 MMA 的正式操作数，缩放计算**零额外 kernel**。软件侧，CUTLASS 提供 `Sm1xxBlockScaledConfig`（layout/scalefactor 配置）与 blockscaled builder（`builders/sm100_blockscaled_umma_builder.inl`），TransformerEngine 提供训练侧配方（第 04 篇展开）。

## 四、程序员实操：先选库，再谈写 kernel

### 4.1 生态位对照——算子线六个仓各自站在哪

| 库 | 定位 | 一句话 | 何时选它 |
| --- | --- | --- | --- |
| **cuBLAS / cuBLASLt**（闭源，样例在 CUDALibrarySamples） | 黑盒标准 GEMM | cuBLASLt 是轻量接口 + 启发式选引擎，**支持 epilogue 融合**（`CUBLASLT_EPILOGUE_GELU/BIAS`，样例 `CUDALibrarySamples/cuBLASLt/LtHSHgemmGroupedSimple/`）与 MXFP8/NVFP4（`LtMxfp8Matmul/`、`LtNvfp4Matmul/`） | 标准形状 GEMM 的**默认答案**，先测它 |
| **CUTLASS** | 白盒模板生成器 | 三代硬件的全部 GEMM 变体，可改任何一层 | cuBLAS 打不赢/形状特殊/要融合自定义 epilogue/学习 |
| **cudnn-frontend** | 图模式算子前端 | 把 conv/norm/attention 写成算子图，自动挑执行计划（execution plan）与引擎启发式 | CNN/归一化/SDPA 这类**多算子组合**，不想手拼 |
| **AMGX** | 稀疏迭代求解器 | AMG 预条件 + Krylov 子空间法，SpMV 为主角 | CFD/隐式非结构网格——**GEMM 世界的对岸**（不规则稀疏，吃带宽不吃 tensor core） |
| **MatX** | 张量表达式 C++ 库 | 惰性求值算子 + 高层 transform（matmul/FFT/einsum） | 信号处理/科学计算的应用层，写法像 NumPy |
| **FasterTransformer** | **已退役** | 2023 年起停止开发，README:1 明言 "development has transitioned to TensorRT-LLM" | 不选。它的历史教训见 §5 |

这张表的第一行最重要：**90% 的 GEMM 需求止步于 cuBLASLt**。它的 epilogue 融合（bias/GELU/relu aux）与 autotune（`LtSgemmCustomFind/LtSgemmSimpleAutoTuning` 样例）覆盖了推理引擎的主流需求；Blackwell 的 MXFP8/NVFP4 也是 day-0 就有。自己写 kernel 的合法理由只有三个：形状/布局 cuBLAS 处理不好（如 decode 侧超小 M、MoE grouped GEMM、weight 采用特殊布局）、要把 GEMM 融进更大的 kernel（如 flash attention、fused MoE）、或者目标就是学。

### 4.2 CUTLASS Profiler：先测量，再决定写不写

CUTLASS 自带微基准全家桶，**编译一次、扫全部组合**：

```bash
# 只编 profiler（别全量编，见 §5）
cmake -DCUTLASS_NVCC_ARCHS=90a -DCUTLASS_BUILD_TESTS=OFF .. && make cutlass_profiler -j

# 单形状；冒号语法=start:stop:step 扫形状区间（deepwiki 10.3 实录）
cutlass_profiler --operation=Gemm --m=1024 --n=1024 --k=128
cutlass_profiler --operation=Gemm --m=1024:4096:256 --n=1024:4096:256 --k=128:8192:128 --beta=0,1,2.5
cutlass_profiler --operation=Gemm --split_k_mode=parallel --split_k_slices=2 --m=1024 --n=1024 --k=128
```

拿到某个 (M,N,K,精度,布局) 组合下 cuBLAS 与 CUTLASS 各 kernel 的 GFLOPs 对照，再判断"我的场景是否有空可捡"。`--operation=Conv2d/Conv3d/SpGEMM/...` 同理。

### 4.3 C++ 路线：CollectiveBuilder 三段式

Hopper+ 的标准写法是两个 builder + 一个 kernel adapter（骨架，按 `examples/49_hopper_gemm_with_collective_builder/`）：

```cpp
using CollectiveMainloop = typename cutlass::gemm::collective::CollectiveBuilder<
    cutlass::arch::Sm90, cutlass::arch::OpClassTensorOp,
    cutlass::bfloat16_t, cutlass::layout::RowMajor, 8,     // A: 元素/布局/对齐
    cutlass::bfloat16_t, cutlass::layout::ColumnMajor, 8,  // B
    float,
    cute::Shape<cute::_128, cute::_128, cute::_64>,        // TileShape
    cute::Shape<cute::_1, cute::_1, cute::_1>,             // ClusterShape
    cutlass::gemm::collective::StageCountAutoCarveout<...>,// 流水级数自动推
    cutlass::gemm::KernelTmaWarpSpecialized                // 调度标签 → 偏特化
>::CollectiveOp;                                          // ← builder 选出的具体 mainloop

using CollectiveEpilogue = typename cutlass::epilogue::collective::CollectiveBuilder<
    cutlass::arch::Sm90, cutlass::arch::OpClassTensorOp,
    /*...同参数序，含 ElementOutput/ElementCompute/融合算子*/>::CollectiveOp;

using GemmKernel = cutlass::gemm::kernel::GemmUniversal<
    cute::Shape<int,int,int,int>, ProblemShape, CollectiveMainloop, CollectiveEpilogue>;
// 外面再包 device::GemmUniversalAdapter 跑 initialize()/run()
```

要点：你只声明"什么硬件、什么数据、什么调度"，**布局代数、smem 指针、TMA 描述符、流水深度全部由 builder 在编译期推出来**。改一个 KernelSchedule 标签就是换一种 kernel 骨架（Pingpong/Cooperative/PtrArray…）；改一个 Element 类型就是换一档精度谱。学习路径按 examples 编号走：48（warp specialized）→ 49（builder）→ 50（epilogue swizzle）→ 54（FP8）→ 61（topk+softmax 融合）；Blackwell 的 blockscaled NVFP4 见 70+ 系列。

### 4.4 CuTe DSL 路线：Python 写，秒级 JIT

不想啃 C++ 模板时走 `examples/python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/`：`fp16_gemm_0.py`（裸 kernel，`@cute.kernel`/`@cute.jit`、`tcgen05.MmaF16BF16Op` 选 atom）→ 逐步加流水/warp 特化 → `fp16_gemm_6.py` 完整版；`nvfp4_gemm_0/1.py` 直接示范 block-scaled 精度。装好 `nvidia-cutlass-dsl` 包即可跑（无需本地编译 C++），同一份代码 JIT 出与 C++ 等价的 kernel——**把"编译期生成"从 nvcc 搬到了运行期**，这与 Triton 的动机同源，但 atom 层直接对齐 PTX 指令。教程配套 `dsl_tutorials/`（cooperative launch、PDL、动态 smem 等)。

### 4.5 调试速查

- **精度对不上先查 scale**：FP8/NVFP4 的误差几乎总在缩放方案（per-tensor vs per-block、amax 时机），不在 kernel 本体；
- **性能差先看 bank conflict / stage 数**：Nsight Compute 的 smem 指标 + `StageCountAutoCarveout` 推导值；warp specialized kernel 看两个 mbarrier 队列的空转；
- **编译报错万字长文**：从**最后一行**往前找 `static_assert`——CUTLASS 的约定是主模板故意爆炸并打印人话原因（见 §3.2 的 decl.hpp:93）；
- **launch 失败 Illegal Instruction**：九成是 arch flag 与运行硬件不匹配（`sm_90a` 的 WGMMA 在 `sm_90` 上不能跑，a 后缀不可省）。

## 五、批判边界：这套东西的坑与适用域

1. **组合爆炸是物理属性，不是可修的 bug**。百万级组合靠模板展开，代价是编译时长与二进制体积——全量构建 CUTLASS 是小时级、GB 级的事。正确姿势永远是：**按目标架构窄化 `CUTLASS_NVCC_ARCHS`、只编需要的 example/profiler**，CI 里全量编属于事故。
2. **三代 API 并存，教程污染严重**。2.x（device::Gemm 金字塔）、3.x/4.x（CollectiveBuilder）、CuTe DSL 三套写法都能跑，网上 2022 年前的文章几乎全是 2.x——对 Hopper/Blackwell 是**错误指导**（2.x 路径没有 TMA/WGMMA/TMEM 支持）。判别法：看到 `DefaultMma`/`MmaTilePolicy` 这类词就是 2.x 时代。
3. **CUTLASS 不保证赢 cuBLAS**。闭源库对高频形状有人工调优兜底；CUTLASS 的价值上限在"标准库不做的事"，标准 GEMM 上常常打平甚至略输。先用 profiler 实测（§4.2），别信仰开源。
4. **CuTe DSL 是活水**。4.x 才成为一等公民，API 仍在快速迭代（版本间 breaking 常见），生产采用要锁版本；换来的开发速度收益对小团队非常真实——TRT-LLM 已在 MegaMoE/NVFP4 线上采用（第 05 篇）。
5. **低精度不是免费午餐**。NVFP4 的硬件缩放解决了"能不能算"，没解决"模型质量掉不掉"——scale 粒度（16 vs 32 元素）、scale dtype、哪些层降档都要按第 05 篇 §3.7 的原则逐层定，并跑基准兜底。训练侧还有 delayed scaling 的历史包袱（第 04 篇）。
6. **FasterTransformer 的教训**。它是"手写算子 + 手拼 runtime"路线的巅峰，也在架构迭代（Hopper 指令换了、attention 形态换了）面前停更退役——**算子库形态追不上硬件代际，引擎形态（编译期生成 + 图调度）才追得上**。cudnn-frontend 选图模式、CUTLASS 选模板生成器、TRT-LLM 选全引擎，是同一教训的三个解。

## 六、费曼检验：不看文章能答出吗？

1. **A100→H100→B200 的机器平衡点为什么每代接近翻倍，这对 GEMM kernel 的结构意味着什么？** 请沿"算力增速>带宽增速"推出三条推论（提示：§一的推论一二三分别对应分块层级、精度谱、epilogue 融合，再对照 §3.1 Hopper 的 warp specialization 与 Blackwell 的 TMEM 是哪条推论的硬件化）。
2. **WGMMA 相比 mma.sync 的两个质变，各自消灭了 kernel 里的哪类代码？** tcgen05 把 accumulator 搬进 TMEM 后，为什么 MMA 和 epilogue 反而"彻底解耦"了（提示：从"指令由谁发起、数据在哪个存储层"两个维度答；对照 §3.1 表格最后一列）。
3. **NVFP4 与 MXFP4 的差别为什么不只是"换个 4-bit 格式"？** 请说出 scale 的粒度/类型差异，以及这个差异如何同时体现在 PTX 指令操作数（`mma_sm100_umma.hpp:1277` 的 SFA/SFB）、cuBLASLt 样例（`LtNvfp4Matmul`）和模型质量三处。

**一句话总结**：GEMM 是深度学习唯一算术强度随规模自然增长的规则计算，所以硬件把最贵的单元（tensor core）全部押在它身上；而张量核心峰值每代 3-4 倍于带宽的增速，逼着软件把复用锁得更深（tiling→smem→TMEM）、把字节压得更少（FP8→block-scaled FP4）、把边界抹得更平（epilogue 融合）——CUTLASS 用 C++ 模板把这套"硬件形态×精度×调度"的百万组合在编译期各自生成一份 kernel，CuTe DSL 再把同一个生成器搬到 Python 运行期，这就是算子线的全部故事。

## 勘误（版本矛盾以源码为准）

1. **"CUTLASS 2.x 已被删除"是讹传**：4.8.0 里 2.x 路径完整保留（`include/cutlass/gemm/device/gemm.h:233` 的 `class Gemm`），只是不获得新硬件能力——正确说法是"维护态"，三代 API 并存（§5.2）。
2. **WGMMA 形状常被误写为固定 m64n256k16**：它是一个家族（`wgmma.mma_async.sync.aligned.m64nNk16`，N=8…256）；CUTLASS atom 定义从 `m64n8k16` 起（`include/cute/arch/mma_sm90_gmma.hpp:158`）。
3. **MXFP4 与 NVFP4 常被混为一谈**：MX=每 32 元素一组 ue8m0（纯幂次）scale（OCP 标准）；NVFP4=每 **16** 元素一组 **ue4m3（浮点）** scale（NVIDIA 变体，量化误差更低）。二者在 CUTLASS 里也是不同的 builder/atom 路径。
4. **FasterTransformer 是"停更退役"不是"删库"**：仓库仍在、README:1 明言转投 TensorRT-LLM；部分老文章仍把它当活跃方案推荐。
5. **B200"9 PFLOPS FP4"是 dense 口径**：稀疏（2:4）口径为 18 PF；引用硬件峰值必须带口径，否则机器平衡点计算会差一倍（本文 §一表格全部用 dense）。
6. **shared memory"228KB"是 Hopper/Blackwell 的每 SM 上限**：A100 是 164KB；且其中还有 1KB 保留——tile/stage 计算请以 CUDA Programming Guide 对应架构的数字为准。

## 一手来源

- CUTLASS 4.8.0 源码（本地 `/usr-data/data2/repos/agent-repos/NVIDIA/cutlass/`，commit `0b55a2f6`，2026-09-23），行号锚：
  `include/cutlass/version.h`（4.8.0）· `include/cutlass/arch/mma_sm80.h:317`（mma.sync m16n8k16）· `include/cute/arch/mma_sm90_gmma.hpp:158`（wgmma m64n8k16）· `include/cute/arch/copy_sm90_tma.hpp:117`（TMA bulk tensor）· `include/cute/arch/mma_sm100_umma.hpp:111,1277`（tcgen05 f16 与 mxf8f6f4.block_scale）· `include/cute/atom/mma_traits_sm90_gmma.hpp:75-78`（Swizzle 布局四档）· `include/cutlass/gemm/dispatch_policy.hpp:119-123`（KernelTmaWarpSpecialized 三兄弟）· `include/cutlass/gemm/device/gemm.h:233`（2.x Gemm）· `include/cutlass/tensor_ref.h:152` · `include/cutlass/gemm/collective/collective_builder_decl.hpp:93` · `include/cutlass/gemm/collective/builders/sm90_gmma_builder.inl:209` · `include/cutlass/epilogue/collective/collective_builder.hpp:70` · `include/cute/layout.hpp:99` · `examples/python/CuTeDSL/cute/blackwell/tutorial/tutorial_gemm/fp16_gemm_0.py:80,295,298,302-305`
- CUDALibrarySamples 本地仓：`cuBLASLt/{LtMxfp8Matmul,LtNvfp4Matmul,LtHSHgemmGroupedSimple}`（epilogue 融合与 block-scaled 样例）
- deepwiki 全量（2026-10-26 抓取，INDEX 入口）：`../../../../讲透宇宙/05-侦/讲透NVIDIA//cutlass/`（71 页；profiler 用法出 10.3-performance-profiling）· `cudnn-frontend/`（32 页，graph API/execution plan/heuristics）· `AMGX/`（25 页，AMG/Krylov/smoothers）· `FasterTransformer/`（20 页，退役前的模型/优化全档）· `MatX/`（25 页，transforms/einsum）· `CUDALibrarySamples/`（20 页，各闭源库样例索引）
- 硬件峰值：NVIDIA 官方 datasheet（A100/H100/B200，dense 口径），本文仅取量级用于 roofline 推导
- 横切底座：`/usr-data/data2/repos/deepseek-ai/distilled/nvidia/NVIDIA-CUDA-STACK.md` 第〇节（算子线定位）与第三节（精度谱硬件机制）
