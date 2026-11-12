# MatX 全链图谱 ONBOARDING（NVIDIA/MatX @ce764c01）

> 基于 understand-anything 知识图谱（2884 节点 / 4276 边 / 16 层 / 15 步 tour / fingerprints 1580 文件基线），行号锚经源码核实。读者假设：会 C++ 模板与 CUDA 基础，用过 NumPy。

## 1. 项目定位与全景

MatX 是 NVIDIA 开源的 **C++17 GPU 张量计算模板库**，定位为"现代 NumPy 的 C++/CUDA 等价物"：`auto t = make_tensor<float>({10, 20})` 一行即得设备张量，`(B = A + 1).run(stream)` 一行即在 GPU 上完成逐元素计算——没有显式 kernel 编写、没有内存搬运样板代码。版本 `MATX_VERSION 1.1.0`（CMakeLists.txt:3），`project(MATX ...)`（CMakeLists.txt:37）。

它解决的核心痛点是**数值计算代码从原型到 GPU 生产的鸿沟**：传统路线要把 NumPy 原型翻译成 CUDA C++（手写 kernel、手管显存、手调句柄），MatX 用表达式模板把"数组式写法"直接编译成 GPU 执行流，底层按需调用 cuSOLVER/cuBLAS/cuFFT/CUB/LAPACK。

仓库规模（图谱实测 1580 源文件）：include/matx 256（库本体）、test 161、docs_input 330（api/ 259 页）、cmake 665（含 rapids-cmake vendored）、public/cpm-cmake 81、examples 41、bench 16、docker/.devcontainer/.github 等 22。

**一句话架构**：`operators/`（111 头）用 CRTP 表达式模板搭建**惰性声明层**，`transforms/`（58 头）提供**立即执行层**，`executors/` 抽象执行域（CUDA 流/host/JIT），线性代数在 `transforms/` 内以 **cuda/lapack 成对后端**落地（chol/eig/lu/qr/svd/solve），`kernels/` 存放手写融合 kernel。这个"惰性声明 × 立即执行 × 双后端"三元结构是理解全库的钥匙，下文第 4、5 节专章展开。

图谱导航：根构建（L01）→ core 张量（L02）→ operators 惰性层（L03）→ transforms 立即层（L04）→ generators（L05）→ 双后端（L06）→ kernels+executors（L07）→ streaming/file_io（L08）→ test 骨干（L09）/外围（L10）→ bench（L11）→ examples（L12）→ docs API（L13）/教程（L14）→ vendored rapids（L15）/cpm（L16）。

## 2. 构建体系与仓库布局：header-only + 自包含依赖

MatX 的库本体**没有 .cpp 文件**——`include/matx.h` 是唯一伞头（include/matx.h:33 `#pragma once`），且注释明确"defines.h should always be included first. Its definitions may impact the behavior of other headers"（include/matx.h:41-42）——头文件包含顺序有语义，这是模板库的典型约束。伞头内还有硬件门槛检查：compute capability < 6.0 直接 `#error`（include/matx.h:36-39 一带）。

CMake 顶层的选项矩阵（CMakeLists.txt:62-82）勾勒能力面：`MATX_BUILD_EXAMPLES/TESTS/BENCHMARKS` 目标开关，`MATX_EN_CUTENSOR/CUDSS/FILEIO/NVTIFF/X86_FFTW/NVPL/BLIS/OPENBLAS` 后端开关——host BLAS/LAPACK 有 OpenBLAS/BLIS/NVPL（ARM 性能库）三选一。`cmake/` 17 个模块分两类：`Find*.cmake`（FindBLIS/FindcuDSS/FindcuTENSOR 等系统包发现）与 `Get*.cmake`（GetCUTLASS/GetGTest/GetPyBind11，版本由 cmake/versions.json 钉死）。

两个 vendored 子树值得新人知道边界：
- `cmake/rapids-cmake/`（648 文件）是 RAPIDS 生态的 CMake 框架整体拷贝，其中 `testing/` 占 448 个（GTest 夹具矩阵），由 `public/rapids-cmake.txt` subtree 指针维护；
- `public/cpm-cmake/`（79 文件）是 CPM.cmake 依赖管理器，`CPMFindPackage`（public/cpm-cmake/cmake/CPM.cmake:232）先本地 find_package、失败回退 `CPMAddPackage` 拉源码——保证"clone 即可构建"的自包含体验。

docker/ 与 .devcontainer/ 提供 CUDA 开发容器镜像与 VSCode 远程容器配方，.github/workflows 驱动 CI。改动库本体时这些目录通常不用碰；升级依赖版本改 cmake/versions.json + 重算 subtree。

## 3. 张量核心体系（core/，41 文件）

### 3.1 三层张量类型

core 的设计是"描述符与数据分离"的三层继承：

1. **`tensor_desc_t`**（include/matx/core/tensor_desc.h:55）持有形状+步长，姊妹类 `static_tensor_desc_t` 把编译期常量形状编码进类型——零运行期形状存储、让 kernel 启动参数在编译期定死。
2. **`tensor_impl_t`**（include/matx/core/tensor_impl.h:91）= Desc + Data 指针，实现 Size/Stride/Shape 查询与 `PermuteImpl` 维度重排等公共操作。
3. **`tensor_t`**（include/matx/core/tensor.h:76，`class tensor_t : public detail::tensor_impl_t<T,RANK,Desc>`）是面向用户的值语义张量，自带 `PrefetchDevice`（include/matx/core/tensor.h:743，异步预取）与 `Permute` 重载（include/matx/core/tensor.h:923/947）。

`make_tensor` 工厂（include/matx/core/make_tensor.h:59/87/107）支持 `{10,20}` 运行期与 `make_tensor<float,10,20>` 编译期两种形状（docs_input/quickstart.rst:30/41 有官方示例）——前者灵活后者零开销。

### 3.2 存储、分配与缓存

- `matxAlloc/matxFree`（include/matx/core/allocator.h:410）统一 host/device/managed/pinned 分配，`matxPointerAttr_t`（include/matx/core/allocator.h:78）记录指针属性；`matxPrintMemoryStatistics` 输出 MemTracker 记账，examples/simple_radar_pipeline.cu:155 收尾即调用它打印内存统计。
- `storage.h` 提供 RAII 持有与自定义 allocator 注入点（对接 RMM 池分配）。
- `cache.h` 的 `GetCache()`（include/matx/core/cache.h:742）是全局句柄/计划缓存：cuFFT plan、cuBLAS/cuSOLVER 句柄、LTO IR 都按参数键缓存复用——**变换第二次调用免重建 plan** 是 MatX 性能常识；`ClearCachesAndAllocations`（test/main.cu:45 在每个测试夹具里调用）负责测试间清场。

### 3.3 张量变体与互操作

- `dynamic_tensor_t`（include/matx/core/dynamic_tensor.h:133）：运行期 rank+类型擦除，牺牲编译期优化换脚本绑定灵活性。
- `sparse_tensor_t`（include/matx/core/sparse_tensor.h:81）+ sparse_tensor_format.h 的格式代数：`isCOO()/isCSR()`（include/matx/core/sparse_tensor_format.h:162/172），`using CSR = SparseTensorFormat<2, LvlSpec<D0, Dense>, LvlSpec<D1, Compressed>>`（:373）——用 lvl 描述符组合表达存储格式，与 GraphBLAS 风格的格式系统同构。
- `tie.h` 把多个输出张量绑成一个可赋值对象（`tie(a,b,c) = svd(x)` 风格）；`dlpack.h` 实现跨语言数组协议；`pybind.h`（include/matx/core/pybind.h:41 起 numpy 互操作、:165/:194 `module_::import("numpy")`）在 `MATX_ENABLE_PYBIND11` 下（:37）把张量视图零拷贝暴露给 Python——examples/python_integration_sample 展示闭环。
- 数值类型：`half.h/half_complex.h` 半精度与半精度复数，type_utils.h/tensor_utils.h 提供全套类型萃取（`is_tensor_view_v` 等，是 operators 编译期分派的依赖）。

## 4. 惰性/立即双层架构（全库主轴，专节一）

### 4.1 惰性层：operators/ 的 CRTP 表达式模板

`BaseOp`（include/matx/operators/base_operator.h:148）是全部 111 个算子的 CRTP 基类：`using matxop = bool` 类型标记让 trait 系统能识别"这是个 MatX 算子"，模板参数 `T` 是**最终派生类自身**（curiously recurring template pattern）——运算符组合 `A + B * C` 在编译期展开成 `matxBinaryOp<tensor, matxBinaryOp<tensor, tensor, MulOp>, AddOp>` 类型的表达式树，全程零虚函数、零堆分配。

算子族谱（每个文件一个算子的组织哲学）：
- **代数组合**：`matxBinaryOp`（include/matx/operators/binary_operators.h:91，运算符重载 +,-,*,/,%）、`matxUnaryOp`（include/matx/operators/unary_operators.h:58，abs/sqrt/exp/pow…）；
- **视图/索引**：`SliceOp`（include/matx/operators/slice.h:49）、`AtOp`（at.h:45）、`CloneOp`（clone.h:43）、permute/collapse/concat/reverse/reshape——**只改 tensor_desc 映射，不拷贝数据**，视图链的自由度即 NumPy 广播/切片语义的来源；
- **归约**：`ReduceOp`（include/matx/operators/reduce.h:44）、`ArgMaxOp`（argmax.h:45 一带）等；
- **转换**：`CastOp/ComplexCastOp`（cast.h）；
- **变换门面**：`FFTOp/FFT2Op`（include/matx/operators/fft.h:59/772）——注意 fft.h 同时存在于 operators/ 与 transforms/，前者只声明"这是 FFT 表达式"，后者才含 cuFFT 调用。这是双层的直接物证。

### 4.2 立即层：transforms/ 与 exec 驱动

`BaseOp::run(Ex&&)`（include/matx/operators/base_operator.h:181）是惰性到立即的**唯一渡口**，其编译期分派链按 trait 逐路特化（以下行号均在 base_operator.h）：
1. `is_jit_cuda_executor_t` → 交给 JIT 执行器整体编译（:187 注释明言"不需要 PreRun/PostRun，因为没有异步分配"）；
2. dynamic-rank 表达式 → static_assert 拒绝（只能走 CUDAJITExecutor）；
3. `is_mtie` 多输出绑定 → `tp->Exec(ex)`（:212 一带）；
4. `is_matx_set_op` 赋值表达式 → 再分：分布式张量、transform 短路 `TransformExec`（:222/:234，避免中间临时分配）、direct_assign 直填；别名检查 `check_aliased_memory` 在 LHS/RHS 内存重叠时抛 `matxInvalidParameter`（:225 附近）；
5. 一般路径 → `PreRun(shape, ex)`（:276/:291，分配变换所需的设备临时内存）→ `Exec(ex)` → `PostRun`（:282/:297，归还异步分配）。

`run(cudaStream_t stream = 0)`（:307）与事件重载（:319）是常用糖。**PreRun/PostRun 生命周期**是 transforms 的通用协议：所有"重"变换（FFT/conv/matmul…）在 PreRun 里按需申请 workspace，在 PostRun 里释放——streaming 层的 `SegmentLifecycleGuard`（include/matx/streaming/stream_detail.h:59）就是为分段执行这个协议而生的 RAII 卫兵。

transforms/ 30 个直接头是立即层门面：reduce/transpose/copy（数据移动三件套）、conv/corr/filter（信号族）、einsum/matvec、norm/normalize/percentile/pinv/det/inverse、cgsolve、pwelch/find_peaks/ambgfun（谱分析）、resample_poly/channelize_poly/sar_bp（多速率信号）、cub.h/cub_device.h（CUB 原语桥接）、host_algorithms.h（CPU 等价实现）、solver_common.h/solver_cusolverdx.h（求解器公共设施）。`transforms.h` 汇总入口仅 35 行——组织单元是"每个变换一个子树"。

### 4.3 为什么要双层

惰性层买来三样东西：**表达式融合**（JIT 执行器把整棵树编成单个 kernel）、**通用性**（任何算子吃任何 BaseOp，视图/生成器/张量统一处理）、**写法即文档**（数学式直译）。立即层保留对库调用与手写 kernel 的完全控制——两层分离使"用户写 NumPy 式代码、库做 CUDA 工程决策"同时成立。

## 5. 双后端线性代数（专节二）

transforms/ 下八个子目录（chol/convert/eig/fft/lu/matmul/qr/solve/svd）藏着 MatX 最有辨识度的设计：**同名变换 × 双执行域成对实现**。以 LU 为例：

- **device 后端** lu_cuda.h（314 行）：`cusolverDnXgetrf_bufferSize`（include/matx/transforms/lu/lu_cuda.h:117）问 workspace 大小 → `cusolverDnSetStream`（:163）绑流 → `cusolverDnXgetrf`（:168）批量分解 → `cudaMemcpyAsync` 拷回 info（:180）→ 按 info 正负区分"参数非法"与"U 奇异"（:188/:191）。统一入口 `lu_impl` 在 :264。
- **host 后端** lu_lapack.h（261 行）：`getrf_dispatch`（include/matx/transforms/lu/lu_lapack.h:174）按标量类型 `LAPACK_CALL(sgetrf/dgetrf/cgetrf)`（:178/:180/:182）分派 LAPACK 例程，批处理是逐矩阵循环（:151），同样有 info 语义检查（:156/:159）；:107 的 static_assert 钉死 pivot 张量整数类型必须匹配宿主 LAPACK 的 lapack_int_t。

chol（potrf）/eig/qr/svd/solve 完全同构。**选择逻辑由张量数据所在域驱动**：张量在 device 上走 cuda 后端，host 张量走 LAPACK——用户写同一行 `lu(a, piv)` 不感知后端。这也是 CMake 选项里 OpenBLAS/BLIS/NVPL 三选一的消费点（host BLAS 后端可换）。

matmul 是后端最多的变换（六路）：`matmul_cuda.h`（1603 行）自研 tile kernel（`GemmOpRows/GemmOpCols` 处理转置语义，include/matx/transforms/matmul/matmul_cuda.h:211/:217；Exec 主体 :651）与 cuBLAS 桥（`CheckCublasStatus` :158、`CublasOperandMemOrder` :182 行/列主序判定）；`matmul_cblas.h` 链接 cuBLAS/OpenBLAS/BLIS；`matmul_cublasdx.h` device-side GEMM；`matmul_cusparse.h/matvec_cusparse.h` 稀疏乘。FFT 同样多路：`fft_cuda.h`（865 行）cuFFT 调用 + plan 参数键缓存（`GetFFTParams` fft_cuda.h:190、`fft_cuda_cache_t` :645）；`fft_cufftdx.h` 设备端单 block FFT（libcufftdx，fft_cufftdx.h:42）用于 JIT 融合；`fft_fftw.h` host FFTW。convert/ 三件负责稀疏格式转换。

## 6. 执行器、kernels、生成器与流式处理

**executors/**（9 头）抽象执行域：`cudaExecutor`（include/matx/executors/cuda.h:57）继承 `CudaExecutorBase`（cuda_executor_common.h:86，持有 stream 与可选 NVTX profiling）；`CUDAJITExecutor`（jit_cuda.h:325）是融合执行器——用 **NVRTC 在运行期把整棵表达式树编译成单个 CUDA kernel**（jit_cuda.h:318 注释），kernel 二进制按表达式类型+sm 架构键缓存（:133/:143）；`host.h` 服务 LAPACK/FFTW 后端；`distributed.h`+core/distributed_tensor.h 支持多 GPU 分布式张量（test/00_tensor/DistributedTensorTests.cu 覆盖）。BaseOp::run 分派链的 dynamic-rank 检查说明动态 rank 表达式**只能**走 JIT——需要运行期代码生成。

**kernels/**（11 个 .cuh）是无法用库调用表达的手写 CUDA kernel 库：transpose.cuh（`transpose_kernel_oop` out-of-place 转置）、conv.cuh（streaming 层点名的 conv 引擎，见 conv1d_stream.h:48 注释）、matvec.cuh（DIA-I/DIA-J 对角稀疏 SpMV）、sar_bp.cuh（SAR 后向投影成像）、pwelch/resample_poly/filter/channelize_poly、tensor_accessor/utility。**fltflt.h**（include/matx/kernels/fltflt.h:40）是特色双精度技巧：`struct alignas(8) fltflt`（:57）用两个非重叠 fp32 分量表示 unevaluated sum，无 FP64 硬件时逼近 double 精度（:73 从 IEEE-754 double 位型拆 hi/lo）——bench/00_misc/fltflt_arithmetic.cu 专测其算术。

**generators/**（19 头）零存储数据源：`Range`（range.h:42）、linspace/logspace、`RandomOp`（random.h:207）、zeros/ones/fill、hamming/hanning/blackman 等窗函数族、chirp/meshgrid/diag/fftfreq。生成器继承 BaseOp，能直接进表达式：`(y = fft(hamming(N) * x)).run()` 一行完成加窗 FFT——零中间数组。

**streaming/**（5 头）把有状态变换封装成流式对象：构造时绑定滤波器与 executor（Conv1DStream 类 include/matx/streaming/conv1d_stream.h:105，static_assert 限定 CUDA/host 执行器与 1D 滤波器 :112/:113），之后反复 `feed()` 喂数据、终了 `flush()` 冲出尾部——VALID/SAME/FULL 三模式共享单一因果引擎（conv1d_stream.h:38-49 的注释表是权威说明，skip/flush_len 语义 :128-:139）。resample_poly_stream.h（:96 类定义）同理，:170 的 `Upper bound on the outputs a single feed() or flush() call can produce` 注释给出输出缓冲 sizing 契约。stream_detail.h 的 `StreamSlicePlan`（:47，lo+cnt 输出窗口计划）与 `SegmentLifecycleGuard`（:59，异常安全地跑 PreRun/PostRun）是流式底座。这套设计面向雷达/通信连续数据流：examples/streaming.cu 与 01_radar 测试分区是完整用例。

**file_io/**（2 头）：file_io.h 通用 IO + tiff.h（MATX_EN_NVTIFF 下读 TIFF）。

## 7. 质量与生态面：test / bench / examples / docs_input

**test/**（161 文件）按数字前缀分区：00_tensor（张量语义 12 个：BasicTensorTests/ViewTests/DLPackTests/DistributedTensor*Tests 等）、00_operators（81，几乎每算子一文件）、00_transform（13）、00_solver（11）是骨干；test_vectors（11）数值参考夹具；00_misc/00_io/00_sparse/01_radar 外围。test/main.cu:45 在夹具级调用 `matx::ClearCachesAndAllocations()` 保证测试隔离。

**bench/**（16 文件）基于 **nvbench**：bench/00_transform/fft.cu:2 引入 nvbench.cuh，:20-21 `state.exec(...)` 计时 `(xv = fft(xv)).run(cudaExecutor(launch.get_stream()))`，:24 幂次轴扫 1K-256K 点 FFT。覆盖 conv/cub/einsum/fft/matmul/qr/resample_poly/sarbp/svd_power/SpMM/fltflt_arithmetic——性能回归即 API 契约。

**examples/**（41 文件）领域横截面：black_scholes（金融）、simple_radar_pipeline（雷达全链：PulseCompression→ThreePulseCanceller→DopplerProcessing→CFARDetections 四段 NVTX range，examples/simple_radar_pipeline.cu:83-95，:141 打印吞吐 Gbps）、mvdr_beamformer、spectrogram、spherical_harmonics、kernel_fusion、streaming；cmake_sample_project 教 find_package 消费，python_integration_sample 教嵌入 Python。**读例学 API 是 MatX 最快的上手路径**。

**docs_input/**（330 文件）Sphinx 站点：quickstart.rst（make_tensor 两种形状 :30/:41、`(t4pc = t4p).run()` :196）、basics 16 篇、notebooks 36 篇交互教程、developer_guide 5 篇、api/ 259 页逐函数参考。

## 8. 新人上手路径与常见坑

**推荐学习顺序**（图谱 tour 同构）：quickstart.rst 过语法 → core/tensor.h+make_tensor.h 建张量 → base_operator.h 的 BaseOp::run 分派链（赋值即执行）→ 挑一个 transforms（reduce/transpose）读懂 PreRun/Exec/PostRun → 对照 lu_cuda.h vs lu_lapack.h 吃透双后端 → examples/simple_radar_pipeline.cu 全链 → executors/jit_cuda.h 融合编译 → streaming/ 流式状态管理。

**关键事实速记**：header-only（改 .h 即生效）；`(expr).run(stream)` 触发执行，忘记 .run 什么都不发生；plan/handle 全局缓存（测试间要 ClearCachesAndAllocations）；后端选择自动（张量在哪个域就走哪个后端）。

**常见坑**（源码实证）：
- 头文件顺序敏感：defines.h 必须最先（include/matx.h:41 注释），自写伞头别打乱；
- LHS/RHS 别名重叠会被 run 期检查直接抛异常（base_operator.h:225 一带 `check_aliased_memory`）——`A = A + 1` 走拷贝语义没问题，但显式同内存视图的变换赋值会炸；
- dynamic-rank 张量表达式只能配 CUDAJITExecutor（base_operator.h 分派链第 2 路 static_assert）；
- Conv1DStream 一个对象同时只服务一条流（conv1d_stream.h:100 注释"An object serves one stream at a time"）；feed() 的输出缓冲按 Upper bound 契约预留（resample_poly_stream.h:170）；
- compute capability ≥ 6.0 硬门槛（include/matx.h:36-39）；
- LAPACK pivot 张量整数类型必须匹配宿主 lapack_int_t（lu_lapack.h:107 static_assert）；
- vendored 子树用 subtree 指针管理（public/subtreeInstructions.txt），别手动散改。

**深读材料**：work4ai/讲透NVIDIA/MatX/explain/ 系列按主题展开（tensor 核心/operators CRTP/transforms exec/generators/双后端/fft/kernels+executors/streaming/test+bench/docs+vendored 十篇）。

---
*图谱资产：.understand-anything/knowledge-graph.json（2884n/4276e/16 层/15 步 tour，validator 0 issues，fingerprints 1580@ce764c01）。行号锚写作时逐一核实，后续提交可能漂移。*
