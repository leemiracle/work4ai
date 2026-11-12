# NVPLSamples ONBOARDING

> 仓库：`/usr-data/data2/repos/agent-repos/NVIDIA/NVPLSamples`（commit 78c53b0b）｜图谱：1141 节点/1874 边/12 层/16 步 tour｜行号锚均经源码核实。

## 1. 一句话定位与仓库全景

NVPLSamples 是 **NVIDIA Performance Libraries（NVPL）官方示例集**：NVPL 是面向 NVIDIA aarch64 CPU 优化的数学库全家桶，**纯 CPU、零 CUDA/CTK 依赖**，作为标准 C/Fortran 数学 API 的 **drop-in 替代**（README.md:3-5）——现有 BLAS/LAPACK/FFTW 程序重链 `nvpl::` 目标即得优化实现。

七库矩阵（README.md:20-26）：**BLAS / FFT / LAPACK / RAND / ScaLAPACK / Sparse / Tensor**。目标硬件 aarch64（README.md:32-43）：Vera/Grace/DGX Spark(GB10)/Graviton 5-2/Ampere Altra，下限 Armv8.1-A。对齐发行版 **NVPL-26.5**（README.md:14）。关键认知：**本仓只有示例，库本体另行安装**（`nvpl_ROOT` 指前缀，README.md:99-102）。

## 2. 目录地图与七库分工

仓根=七子目录+README+LICENSE，无顶层 CMake，各库独立构建。计数为亲自 ls 所得：

| 目录 | 源文件（实数） | 语言 | 要点 |
| :--- | :--- | :--- | :--- |
| nvpl_blas | c/ 160 `.c`；f77/ 170 `.f`（含共享 common_func.f→169 示例） | C+F77 | Level1-3 全家族+batch+64 位接口+厂商扩展，最大板块 |
| nvpl_lapack | cpp/ 66 `.cpp`（含 utils.cpp）；f77/ 23 `.f`（含 common_func.f） | C+++F | LAPACKE 高层 vs NVPL_LAPACK_* Fortran 风格双轨 |
| nvpl_fft | cxx/ 12 `.cpp`；fortran/ 3 `.f90`+1 `.f` | C+++F | FFTW API 兼容层、wisdom、OpenMP、benchmark |
| nvpl_sparse | c/ 8 `.c` | C | COO/CSR/SELL 三格式 × SpMV/SpMM/SpSV 四阶段 API |
| nvpl_rand | 7 `.cpp`（平铺） | C++ | rand/rand_mt 双引擎+cuRAND 逐位对照 |
| nvpl_scalapack | f77/ 5 `.f`（pdscaexinfo.f 共享）+cxx/ 2 `.cpp`+9 `.dat` | F+C++ | 1995 官方 p?scaex 四精度+pdgemm/pdgesv |
| nvpl_tensor | 六算子目录 6 `.c`+1 `.cxx` | C(+C++) | cuTensor 风格描述符 API 六算子 |

合计约 470 个示例源文件（图谱 522 文件含 CMake/README/.dat）；每库顶层自带 CMakeLists+Presets+README，是独立构建单元。

## 3. 构建与运行体系

统一 **CMake Package Config**：`find_package(nvpl REQUIRED COMPONENTS blas)`（nvpl_blas/CMakeLists.txt:35），链接 imported target `nvpl::<lib>_<opts>`（nvpl_blas/c/CMakeLists.txt:11）。目标命名三轴（README.md:149-157）：

- **BLAS/LAPACK**：`nvpl::blas_<int>_<thr>`，`<int>`∈{lp64,ilp64} 由 `INT_TYPE` 选（nvpl_blas/CMakeLists.txt:25），`<thr>`∈{seq,omp} 由 `THR_TYPE` 选，默认 lp64+omp；
- **ScaLAPACK**：`nvpl::scalapack_<int>`+`nvpl::blacs_<int>_<mpi>`，`<mpi>`∈{mpich,openmpi3/4/5} 由 MPI_INTERFACE 控制（nvpl_scalapack/CMakeLists.txt:54），须与本机 MPI 匹配；
- **FFT/Rand/Sparse/Tensor**：`nvpl::fftw`/`nvpl::rand(_mt)`/`nvpl::sparse`/`nvpl::tensor` 单目标无后缀。

**Presets**：BLAS 5 个 configure preset（default+四组合，按 preset 分桶）；ScaLAPACK 最重——INT×THR×MPI 全组合 17×3=51 个（实测）。ctest 批跑，可执行名带变体后缀（c_ilp64_omp_sgemm）。

**编译器分支**：Fortran ILP64 下 GNU 加 `-fdefault-integer-8`、NVHPC 加 `-i8 -Mlarge_arrays`（nvpl_blas/f77/CMakeLists.txt:13）；FFT 的 Fortran `.f90` 用 `-std=f2003`、`.f` 用 `-std=legacy`，加 `-fall-intrinsics` 供 EXIT()（nvpl_fft/fortran/CMakeLists.txt:26）；ScaLAPACK 的 CTest 由 mpiexec 拉起，OpenMPI 下定义 OMPI_SKIP_MPICXX 规避 C++ 绑定。

## 4. 示例代码的通用骨架（四段式）

BLAS 示例几乎同一副骨架，范本 `nvpl_blas/c/caxpy.c`：**printf 横幅+参数行（nvpl_blas/c/caxpy.c:17）→ fill_* 确定性填充（nvpl_blas/c/caxpy.c:28）→ 一行 cblas_caxpy（nvpl_blas/c/caxpy.c:36）→ print_* 结果（nvpl_blas/c/caxpy.c:40）**，外加 malloc/free。数据全为确定性伪随机，公式 `mod(91+i,1023)/1024-0.5`（nvpl_blas/f77/common_func.f:96），输出可逐位比对。

四份共享辅助文件（tour step-03/07/08/10 锚点）：

- **nvpl_blas/c/example_helper.h**（图谱 fanIn=159 全仓第一枢纽）：float/double/nvpl_scomplex_t/nvpl_dcomplex_t 四精度的向量/矩阵（Full/Upper/Lower）/带状 fill_/print_ 全家+5 个枚举转单字符工具（transpose_to_char 在 nvpl_blas/c/example_helper.h:1086、order_to_char 在 nvpl_blas/c/example_helper.h:1099、uplo/diag/side 紧随其后至 :1132）；
- **nvpl_blas/f77/common_func.f**：F77 对应物，24 个 print_*/fill_* 例程+NaN 生成器 get_dnan（nvpl_blas/f77/common_func.f:2）/get_snan（nvpl_blas/f77/common_func.f:13），用于给三角矩阵未引用区域填 NaN 标记；
- **nvpl_lapack/cpp/utils.h+utils.cpp**：extern "C" 共 13 个打印函数（整数向量 print_vector 在 nvpl_lapack/cpp/utils.h:29），实现集中在 print_element 模板族（nvpl_lapack/cpp/utils.cpp:14 起：浮点 %6.2f/复数实+虚/整数 NVPL_LAPACK_IFMT）；
- **nvpl_fft/cxx/common.h**（fanIn=11）：header-only 测试框架——test_info 布局（nvpl_fft/cxx/common.h:27）、R2C/C2R 就地布局推导 get_r2c_c2r_setups（nvpl_fft/cxx/common.h:70）、精度三件套 compute_reference/compute_error/assess_error（nvpl_fft/cxx/common.h:151 起）、compute_statistics（nvpl_fft/cxx/common.h:212）。

另有 nvpl_sparse/c/example_helper.h 的 `CHECK_SPARSE` 宏与 nvpl_rand/common.hpp 的 `NVPL_RAND_CHECK`，是各库自己的错误处理门面。

## 5. 双接口模式

**C 与 F77 逐 API 对偶**是本仓最大特色：cblas_caxpy（nvpl_blas/c/caxpy.c:36）与 CALL CAXPY（nvpl_blas/f77/caxpy.f:42）同一算子两种入口；F77 接口声明统一来自 `include "nvpl_blas_f77_blas.fi"`（nvpl_blas/f77/caxpy.f:11）——该文件在 NVPL 安装包、**不在本仓**（见第 8 节）。

**LAPACK 双轨**（tour step-08/09）：①LAPACKE 高层 C 接口（LAPACKE_dgels 等，自带 ROW/COL_MAJOR，内部自动管理工作区）；②NVPL_LAPACK_* Fortran 风格接口——指针传参+**lwork=-1 工作区查询→malloc→二次调用**两段式（查询与实调在 nvpl_lapack/cpp/ex_cgels.cpp:43-58），开头 nvpl_lapack_get_version() 打版本（nvpl_lapack/cpp/ex_cgels.cpp:31）；③ILP64：ex_lapacke_64.cpp 演示 LAPACKE_dgels_64（尺寸参数 nvpl_int64_t），文件头注释（nvpl_lapack/cpp/ex_lapacke_64.cpp:4）明确 `_64` 变体从 LP64 与 ILP64 两种库均有导出。

**FFTW API 兼容层**：C++ 头 `<nvpl_fftw.h>`（nvpl_fft/cxx/1d_c2c_double_example.cpp:3），API 完全 FFTW——fftw_plan_dft_1d（nvpl_fft/cxx/1d_c2c_double_example.cpp:28）与 execute/destroy_plan/cleanup 全生命周期，单精度换 fftwf_ 前缀；include_header_example 验证直接 `#include <fftw3.h>` 也能链到 nvpl_fftw。Fortran 侧 include 'fftw3.f03'（nvpl_fft/fortran/c2c_c2r_r2c_double_apis_example.f90:73）同样来自安装包；nvpl_fft/cxx/1d_c2c_double_example.cpp:6 明言改自 CUDALibrarySamples/cuFFT——CPU/GPU 示例同源。

**厂商扩展**：BLAS 批接口 cblas_dgemm_batch（group 指针数组）与 cblas_dgemm_batch_strided（统一步长）两范式；F77 的 SAXPBY/DAXPBY 双缩放；LAPACK 无主元 LU——ipiv 传 null 即启用（nvpl_lapack/f77/ex_getrf_nopivot.f:28）；线程控制服务函数 nvpl_blas_set_num_threads_local 等（service_functions.c、ex_thread_control.cpp）。**Sparse/Tensor 不走标准 API 兼容**，是 cuSPARSE/cuTensor 风格描述符 API：Sparse 四阶段 create→buffer_size→analysis→execute（nvpl_sparse/c/spmv_coo.c:89 与 nvpl_sparse/c/spmv_coo.c:102），Tensor 三段式 handle→descriptor→op→plan→execute（nvpl_tensor/contraction/contraction.c:147 与 nvpl_tensor/contraction/contraction.c:210）。

## 6. 图谱导航

**12 层**（onboard-input.json layers）：L01 仓库总览→L02-04 BLAS 三层（构建→162 文件 C→171 文件 F77）→L05-07 LAPACK 三层（构建→68 C++→24 F77）→L08 FFT→L09 Sparse→L10 Rand→L11 ScaLAPACK（含 9 个 .dat 数据节点）→L12 Tensor。层结构=「每库先构建/文档层、再语言子目录层」，与目录一一对应。

**16 步 tour**：step-01 全景→02 构建体系→03-07 BLAS（caxpy 范本→GEMM→批接口→F77 对偶→common_func.f）→08-09 LAPACK→10-12 FFT（主线→wisdom/OpenMP→Fortran）→13 Sparse→14 Rand→15 ScaLAPACK→16 Tensor 收官。

**Hub 入口**（按 fanIn）：file:nvpl_blas/c/example_helper.h（159，全仓最大集散地）、file:nvpl_lapack/cpp/utils.h（63）、file:nvpl_fft/cxx/common.h（11）——三份共享辅助头是进任何示例都绕不开的入口；函数级 hub 有 order_to_char（42）、uplo_to_char（35）、print_svector（nvpl_blas/f77/common_func.f:24）等。

## 7. 新人上手路径

推荐顺序（半天到一天走完主线）：

1. 根 README.md：定位、支持矩阵、nvpl:: 目标表（README.md:149-157）；
2. nvpl_blas/c/caxpy.c+example_helper.h：吃透四段式骨架（第 4 节）；
3. 实跑：cd nvpl_blas，`cmake --preset lp64_omp`→build→ctest（前提 NVPL 已装、nvpl_ROOT 正确）；
4. GEMM 家族：sgemm.c→dgemm_64.c（ILP64）→dgemm_batch.c 与 dgemm_batch_strided.c（两种批范式）；
5. F77 对偶：caxpy.f+common_func.f，体会 .fi 引入与列主序默认；
6. LAPACK 双轨：ex_lapacke_dgels_colmajor.cpp（高层）vs ex_cgels.cpp（两段式），再看 ex_batched_getrf.cpp（OpenMP 区内 NVPL 自动限内线程数=1 防超订）；
7. FFT：1d_c2c_double_example.cpp（标准环）→auxiliary_apis_example.cpp（wisdom 三通道）→plan_many_dft_benchmark_example.cpp（测带宽）；
8. 按需下钻：Sparse spmv_coo.c、Rand nvpl_rand/verify_version.cpp:10（版本校验冒烟）、ScaLAPACK pdscaex.f（PDGESV 在 nvpl_scalapack/f77/pdscaex.f:167）、Tensor contraction.c。

注意：目标 aarch64-only（x86 只能读）；omp 变体关注 OMP_NUM_THREADS；ScaLAPACK 先确认本机 MPI 再设 MPI_INTERFACE；FFT benchmark 参数表在 nvpl_fft/README.md。

## 8. 常见坑与勘误清单

**认知坑**：

1. **外部接口文件不在仓内**：nvpl_blas_f77_blas.fi（nvpl_blas/f77/caxpy.f:11、nvpl_blas/f77/common_func.f:5）、fftw3.f、fftw3.f03（nvpl_fft/fortran/c2c_c2r_r2c_double_apis_example.f90:73）全来自 NVPL 安装包 include 目录，仓内 grep 不到是正常的。
2. **两个 f77 目录源码格式相反**：nvpl_blas/f77 是固定格式（CMAKE_Fortran_FORMAT FIXED，nvpl_blas/CMakeLists.txt:21）；nvpl_lapack/f77 的 .f 却是自由格式（-ffree-form，nvpl_lapack/f77/CMakeLists.txt:8，源码用 =>/allocatable 可证）。按固定格式读 LAPACK 的 .f 会读出鬼画符。
3. **tree-sitter 对 Fortran 提取为零**：图谱 Fortran 函数/调用边全部由批分析 worker 人工补齐（台账 b20-24 补 305 条边），F77 例程节点可靠但属人工补偿。
4. **示例改自 CUDA 生态**：nvpl_fft/cxx/1d_c2c_double_example.cpp:6 明注源自 cuFFT；Sparse/Tensor API 命名同 cuSPARSE/cuTensor——可对照 CUDA 版资料，但 NVPL 版多 CPU 特有参数（线程控制等）。

**上游笔误（均源码核实）**：

1. nvpl_scalapack/f77/pzscaex.f:14 声明 INTEGER CP16SZ 且 nvpl_scalapack/f77/pzscaex.f:104 拿它当 ICEIL 除数，但 PARAMETER 定义的却是 CPLXSZ=8——CP16SZ 从未赋值（隐式=0），除零隐患级改名事故；
2. 同文件 NPCOL 被误改名 NPZOL（:33/:68/:74 链条），对照 nvpl_scalapack/f77/pcscaex.f:68 全用 NPCOL——仅 pzscaex 一家不齐；
3. nvpl_fft/cxx/utils.h:1 include guard 拼成 NVPLFFT_EXAMPLE_UNTILS_H_（UNTILS≠UTILS），:50 收尾同错——不碍编译的命名伤疤；
4. nvpl_lapack/cpp/utils.cpp:6-12 的 is_element_complex trait（主模板+两特化）定义后零使用=死代码；
5. nvpl_rand/CMakeLists.txt:41 硬编码 set(CUDAToolkit_FOUND FALSE) 关闭 cuRAND 对照（:118 被注释的 CUDA::curand 链接行互证）；
6. nvpl_lapack/f77/ex_getrf_nopivot.f:18 用 random_number——全仓几乎全确定性填充，此例是罕见非确定输出，diff 验证会踩坑。

---

*understand-anything 流水线 onboarding 产物；行号与计数以源码为准。*
