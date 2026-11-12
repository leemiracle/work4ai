# MatX test 分区与 bench nvbench 基准：质量双面

## 一、角色定位

`test/`（161 文件）与 `bench/`（16 文件）是 MatX 的两个质量面：前者是按数字前缀分区的 GTest 回归矩阵，验证数值正确性与 API 语义；后者是 nvbench 框架的性能测量面，锁定变换的吞吐基线。二者共同构成"改一行头文件，数值与性能都要过"的守护网——对 header-only 库尤其重要，因为任何头文件改动都直接波及全部下游编译单元。

## 二、内部结构

### 2.1 test：数字前缀分区 = 依赖分层

- **00_tensor（12）**：张量语义底座——BasicTensorTests.cu（TYPED_TEST_SUITE 三连 :91-93，按全类型/复数/浮点类型参数化 × CUDA 执行器）、ViewTests（视图语义）、MakeTensorTests、Storage、DLPackTests、DynamicTensorTests、EinsumTests（einsum 归张量侧测）、CUBTests、VizTests、DistributedTensor(MultiGpu)Tests（分布式双测）。
- **00_operators（81）**：几乎每算子一文件（abs2_test/advanced_op_test/aliased_memory_test/angle_test/apply_idx_test/at_test/base_op_test/broadcast_test/cast_test/clone_add_test…），惰性层每个表达式的行为都有对口测试；aliased_memory_test 专测别名检查（对应 base_operator.h:225 的守卫）。
- **00_transform（13）**：立即层变换——ConvCorr/Copy/Cov/FFT/MatMul/Norm/ResamplePoly/SarBp/Solve + **Streaming 三件套**（StreamingConv/StreamingResample/StreamingChannelize，流式层回归）。
- **00_solver（11）**：双后端求解器——Cholesky/Det/Eigen/Inverse/LU/QR/QR2/QREcon/Pinv/SolveDense/SVD，每个后端（cuda/lapack）与每个精度类型都进参数化矩阵。
- **外围**：00_misc（AllocatorTests/CapabilitiesTests/ClearCacheTests/CudaExecutorCommonTests/ErrorTests/FloatFloatTests/GridDimTests/ProfilingTests/PropertyTests/TensorAccessorTests——core 底座与 fltflt、profiling 全有对口）、00_sparse（Basic.cu）、00_io、01_radar（雷达端到端）、test_vectors（数值参考夹具，11 文件）、test/include（公共测试工具）。

结构证据：LU.cu 里 TYPED_TEST_SUITE 按浮点类型族组织（:73），并有 **JIT 专属组**（LUSolverJITTestFloatTypes :93，CuSolverDxSingleMatrixProjectionJIT :96）与回归测试（CuSolverDxUnsupportedProjectionReportsNoShm :136，防 unsupported 投影误报共享内存）——求解器的 cusolverdx/JIT 集成是测试最密的区域。GTEST_SKIP（LU.cu:50）按硬件能力跳过，是异构 GPU 矩阵下的正确姿势。

驱动：test/main.cu（夹具级 `matx::ClearCachesAndAllocations()` main.cu:45，保证 plan/句柄缓存与内存记账不跨测试泄漏）、test/CMakeLists.txt、matx_test.sh（命令行运行器）。

### 2.2 bench：nvbench 三层结构

bench/00_transform/ 是标准范本（fft.cu/matmul.cu）：`#include <nvbench/nvbench.cuh>`（matmul.cu:2）→ benchmark 函数（:12，`nvbench::type_list` 参数化 float/double/复数 :7）→ `state.exec([&](nvbench::launch &launch){ (cv = av*bv).run(cudaExecutor(launch.get_stream())); })`（:32，nvbench 管理预热与计时轮）→ `add_int64_power_of_two_axis("M", nvbench::range(12,13,1))`（:55-56，扫 4096/8192 维）。覆盖 conv/cub/einsum/fft/matmul/qr/resample_poly/sarbp/svd_power + 00_operators（operators/reduction）+ 00_sparse SpMM + 01_radar。

**fltflt_arithmetic.cu**（00_misc）是最有讲头的基准：注释开宗明义"Compares performance across three precision modes: float, double, and fltflt"（:34），type_list 三精度同台（:42）；它还自定义摘要项 `matx/fltflt/gops_per_sec`（:58-66，add_summary 挂 GOp/s 汇总）并按 ILP_FACTOR 折算每迭代实际运算数（:54）——因为 fltflt 一次"加法"是多次 fp32 运算的组合（kernels/fltflt.h），吞吐必须按有效位宽折算才公平；:77 注释补充"只有 double 和 fltflt 提供重载"的测量口径说明。

## 三、外部连接

- test 消费全部库层：operators 测试直接构造表达式树验证 `operator()` 语义，transform/solver 测试走 `.run(cudaExecutor)` 全链路（部分对照 host 执行器/LAPACK 结果），JIT 组消费 executors/jit_cuda.h；
- test_vectors 生成/加载参考数据（与 docs_input/notebooks 的教学数值互补）；
- bench 消费 nvbench（vendored？否——由 cmake/Get* 模块或 rapids-cmake 拉取，bench/CMakeLists.txt 组织）与 nvtx（profiling 联动 executors/cuda.h 的 profiling 开关）；
- CI（.github/workflows）跑 test 矩阵，bench 多用于本地/发布前回归。

## 四、数据流

一次求解器测试的数据流（LU.cu 为例）：TYPED_TEST 参数化类型 → make_tensor 造随机输入（generators/random.h 造数）→ `lu(a, piv)` 或 `(tie(l,u,p) = ...) ` 形式触发惰性对象 → `.run(exec)` 进入 cuda 或 lapack 后端 → 与参考解对照（三角重建/残差范数）→ 夹具析构 ClearCachesAndAllocations 清场。bench 数据流同构但无断言：热身轮建 plan → 计时轮 state.exec 反复执行 → nvbench 聚合中位吞吐写表。

## 五、设计决策

1. **分区数字前缀即构建排序**：00_tensor→00_operators→00_transform→00_solver 由底向上，CMake 按分区粒度控制编译目标（大库拆小目标防编译爆炸）。
2. **类型参数化 × 执行器参数化**：TYPED_TEST_SUITE 把 float/double/complex/half 全类型矩阵与 CUDA/host 执行器做笛卡尔积，模板库的正确性必须在类型×域全组合上验证。
3. **JIT/回归单独成组**：cusolverdx 类新集成享受专属测试组+回归用例（LU.cu:93/:136）——实验性边界靠测试钉住。
4. **bench 自定义摘要**：fltflt 的 gops_per_sec 折算（:58-66）示范了"测量口径必须匹配语义"——不同精度类型的"一次运算"含义不同。
5. **甄别**：任务书称"bench/scripts"有脚本——实证 bench/ 仅 16 文件且 scripts 下为辅助脚本（如聚合），性能面本体是 13 个 nvbench .cu。

## 六、新人提示

1. 加新算子/变换的最短闭环：00_operators 拷一个相邻 *_test.cu 改断言 + 00_transform 加数值对照（对照 numpy/test_vectors 参考）；
2. 测试内出现 plan 命中异常先看夹具是否 ClearCaches（main.cu:45 的机制）；
3. 跑单测用 matx_test.sh 或 ctest -R 分区名；GPU 能力不足的用例会 GTEST_SKIP 不是失败；
4. 写 bench 抄 matmul.cu 骨架：type_list + state.exec + 幂次轴三件套，自定义指标学 fltflt_arithmetic.cu:58；
5. bench 与 test 的文件名不必一一对应（svd_power 基准无对口 solver 测试文件名），查覆盖以变换 API 为纲不是以文件名为纲。

*锚清单：BasicTensorTests.cu:91-93、LU.cu:50/73/93/96/136、main.cu:45、matmul.cu:2/7/12/32/55-56、fltflt_arithmetic.cu:33-34/37/42/54/58/66/77、bench/00_transform/fft.cu、kernels/fltflt.h、base_operator.h:225、executors/jit_cuda.h；分区清单锚：test/00_tensor/BasicTensorTests.cu、test/00_tensor/DistributedTensorTests.cu、test/00_operators/aliased_memory_test.cu、test/00_transform/StreamingConv.cu、test/00_solver/{Cholesky,Eigen,QR,QREcon,Pinv,SolveDense,SVD}.cu、test/00_misc/{AllocatorTests,CapabilitiesTests,FloatFloatTests,ProfilingTests}.cu、test/00_sparse/Basic.cu。*
