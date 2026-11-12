# CUDALibrarySamples ONBOARDING（新人上路指南）

> 图谱基线：3189 节点 / 4547 边 / 16 层 / 16 步 tour / validator 0 issues / fingerprints 1714 文件 @ `07c4f09223302ce4310eef945ed458e092598d17`（2026-11-07 分析）
> 本文行号锚全部从源码核实（核实日期 2026-11-07）；仓内路径均相对 `/usr-data/data2/repos/agent-repos/NVIDIA/CUDALibrarySamples/`。

---

## 1. 项目定位：CUDA 全家桶官方示例集

NVIDIA/CUDALibrarySamples 是 NVIDIA 官方维护的 **CUDA 库示例总仓**：根 README 开宗明义"This repository contains various examples that demonstrate the use of GPU-accelerated libraries in CUDA"（`README.md:4`），覆盖数学运算、图像处理、信号处理、线性代数与压缩。仓根目录下并列 **25 个库域目录**，根 README 的 Library Examples 清单逐一链接（`README.md:29-53`）：cuBLAS/cuBLASLt/cuBLASMp、cuDSS、cuEST、cuFFT/cuFFTMp、cuPQC、cuRAND、cuSOLVER/cuSOLVERMp/cuSOLVERSp2cuDSS、cuSPARSE/cuSPARSELt、cuTENSOR/cuTENSORMg/cuTENSORMp、MathDx（内含五族 Dx）、NPP/NPP+、nvJPEG/nvJPEG2000/nvTIFF、nvCOMP、nvMatmulHeuristics。概览 bullets 段（`README.md:8-16`）先按"数学与图像处理库"归类点出八大主力。

三条定位要点：

- **不是框架，是教材田**。全仓 1714 个文件里没有一个被其它项目 install 复用的库代码；每个示例都是"一个算子/特性 + 最小程序集"的独立教学单元。C++/CUDA 为主（.cu/.cpp/.c/.hxx/.hpp），另含三条非 C++ 线：Fortran（cuFFTMp/Fortran_samples）、Python（cuEST 双线 + cuFFTMp/JAX_FFT + cuTENSOR/python + NPP/nppCanny 脚本线）、纯 C（cuSPARSE/cuRAND Host 全部 .c/.cpp）。
- **每库一个自包含顶级域**。域之间零代码共享——没有全仓级 CMake 顶层（各域各自构建），跨域复用只发生在"模式"层面（见第 2 节三件套）。
- **精度与规模双前沿**。从经典 BLAS 三级到 FP64 仿真（cuBLAS/Emulation）、FP8/MXFP8/NVFP4 块缩放（cuBLASLt）、NVSHMEM/JAX 分布式（cuFFTMp）、GPU 后量子密码（cuPQC）与量子化学（cuEST），示例代际跟硬件代际同步滚动。

配套文档三件套：`README.md`（导航）、`CONTRIBUTING.md`（贡献规范）、`LICENSE.md`（Apache 2.0）。域级 README（如 `cuBLAS/README.md`、`cuSPARSE/README.md`）承担该域的示例清单+构建说明。

---

## 2. 架构总览：16 域库边界分层地图

图谱 16 层按"库家族边界"切分，一个库家族=1-2 层，层间几乎无 import 边（除共享 utils 在域内）。全图骨架是**三重复制模式**，理解它即可握住 1714 文件：

### 2.1 三件套模式（每个示例目录）

```
<库>/<示例名>/
├── <示例名>_example.{cu,cpp,c}   # 主程序：参数解析→句柄→数据→调用→校验→打印
├── CMakeLists.txt / Makefile     # 双构建系统并存（CMake 为主，Makefile 兜底）
└── README.md                     # 算子说明+公式+构建指南
```

### 2.2 utils/cmake 枢纽模式（每个域）

每个库域都有 1-2 个被同域全部示例 include 的公共头与 CMake 函数模块，它们是 import 边图上的最高扇入节点：

| 枢纽 | 行号锚 | 作用 |
|---|---|---|
| `cuBLAS/utils/cublas_utils.h` | :62/:79/:96/:116 四精度 `traits` 特化；:138/:177/:223/:241 print 族特化 | 88 个 cuBLAS 示例共享，377 行 |
| `cuBLAS/cmake/cublas_example.cmake` | :16 `add_cublas_example()`；:18 `CUDA_ARCHITECTURES OFF`；:23 链接 cublas | 74 个示例 CMakeLists 复用 |
| `cuRAND/cmake/curand_example.cmake` | :17 `add_curand_example()`；链接 CUDA::cudart+CUDA::curand | 全部 Host 示例 |
| `cuSOLVER/cmake/cusolver_example.cmake` | :16 `add_cusolver_example()` | 30+ 示例 |
| `cuBLASLt/Common/helpers.h` | 800 行工具头（roundoff/错误检查/缩放张量尺寸） | 40 个 Lt 示例（fanIn=40） |
| `MathDx/cuFFTDx/common/common.hpp` | :157 `measure_execution_ms`；:309 `sm_runner` | 52 个 cuFFTDx 示例 |
| `MathDx/cuSolverDx/common/random.hpp` | 对角占优矩阵工厂（POTRF 数值健康前提） | 44 个示例 |

### 2.3 16 层地图（文件数为图谱 fileCount）

| 层 | 域 | 文件数 | 一句话定位 |
|---|---|---|---|
| L01 | 仓库总览+nvMatmulHeuristics+cuPQC | 20 | 入口文档与两个新兴专项 |
| L02 | cuBLAS Level-1/2/3 | 160 | 经典 BLAS 三级教学主线 |
| L03 | cuBLAS Extensions+Emulation | 89 | Ex 混合精度算子+FP64 仿真 |
| L04 | cuBLASLt+cuBLASMp | 101 | 低级 GEMM API+张量并行算子 |
| L05 | cuSPARSE+cuSPARSELt | 150 | 稀疏算子全谱+2:4 结构化 |
| L06 | cuFFT | 43 | 单 GPU FFT+LTO callback 深水区 |
| L07 | cuFFTMp | 86 | NVSHMEM 分布式+JAX 封装 |
| L08 | cuRAND Host | 66 | 引擎×分布矩阵 |
| L09 | cuSOLVER | 102 | 稠密分解+特征值谱系 |
| L10 | cuSOLVERMp+cuSOLVERSp2cuDSS+cuDSS | 83 | 分布式求解+稀疏直接求解 |
| L11 | MathDx 五族 | 249 | 设备端（in-kernel）数学对偶 |
| L12 | nvCOMP | 48 | GPU 压缩算法+基准 |
| L13 | NPP+NPP+ | 143 | 图像处理两代 API |
| L14 | nvJPEG/nvJPEG2000/nvTIFF | 66 | 图像编解码 IO |
| L15 | cuEST | 265 | **全仓最大域**：量子化学 |
| L16 | cuTENSOR 家族 | 43 | 张量缩并+Python 绑定 |

三个跨域规律（tour t16 沉淀）：
1. **精度阶梯贯穿全仓**：FP64 原生→FP64 仿真（bf16x9/定点）→FP32/TF32→FP8→MXFP8→NVFP4，cuBLAS 家族四层把这架梯子完整铺了一遍。
2. **host/device 对偶**：MathDx 五族是宿主库的设备端镜像（MathDx/README.md:9-14 逐一点名 cuBLASDx/cuFFTDx/cuSolverDx/cuRANDDx/nvCOMPDx+libmathdx），API 语义对映（cuFFTDx 00-10 号示例 ↔ cuFFT/cuFFTMp）。
3. **C/S 后缀扩展族**：cuSOLVER 的 X 前缀（Xgesvd/Xgesvdp/Xgesvdr/Xgeqrf…）是类型泛化变体；Mp/Mg 后缀（cuBLASMp/cuSOLVERMp/cuFFTMp/cuTENSORMg/cuTENSORMp）是分布式变体；Lt 后缀（cuBLASLt/cuSPARSELt）是轻量/低级形态。

---

## 3. cuBLAS 家族：从经典 BLAS 阶梯到张量并行算子田

cuBLAS 家族占四层（L02-L04），是全仓体量最大、教学线最完整的谱系。

### 3.1 Level-1/2/3 经典阶梯（L02，160 文件）

按 BLAS 规范三级展开，每示例一个算子：Level-1 向量（`Level-1/axpy/cublas_axpy_example.cu:57` 可见标准的 `cublasCreate`→数据上载→`cublasAxpy`→校验生命周期）、Level-2 矩阵-向量（gemv/ger/symv/hbmv…22 个）、Level-3 矩阵-矩阵（gemm/gemm3m/gemmBatched/gemmStridedBatched/syrk/herk…16 个）。全部 88 个示例走同一 CMake 入口（`cuBLAS/cmake/cublas_example.cmake:16` 的 `add_cublas_example(GROUP_TARGET, EXAMPLE_NAME, EXAMPLE_SOURCES)` 三参函数），同一工具头（`cublas_utils.h` 的 `template <>` 全特化四精度打印族，:138/:177/:223/:241）。**读通一个 axpy 就读通了 88 个**。

### 3.2 Extensions 与 Emulation 两条支线（L03，89 文件）

- **Extensions/**：Ex 后缀混合精度扩展算子（GemmEx/GemmStridedBatchedEx/AxpyEx/Nrm2Ex/Dot(c)Ex）与实用变换（dgmm 对角缩放、geam 转置、tpttr/trttp 三角 packing 互转）。`Extensions/GemmExAutoTuning/` 演示自动调优模式。
- **Emulation/**：回应新架构 FP64 吞吐收窄的硬件现实，两条精度仿真路线：
  - **bf16x9 路线**：同一程序并排跑原生与仿真两次 GEMM 做对照——`Emulation/bf16x9_gemmEx/cublas_GemmEx_example.cu:96-98` 用 `CUBLAS_COMPUTE_32F` 原生计算，:126-128 切 `CUBLAS_COMPUTE_32F_EMULATED_16BFX9`（9 个 bf16 拼出一个 FP64 等效精度），:135 起打印两侧结果对比。
  - **dynamic/fixed 定点路线**：`Emulation/dgemm_dynamic/cublas_dgemm_dynamic_example.cu:35-44` 注释块完整列出环境变量开关（`CUBLAS_EMULATE_DOUBLE_PRECISION`、`CUBLAS_FIXEDPOINT_EMULATION_MANTISSA_BIT_COUNT`），:55 `CUDA_EMULATION_MANTISSA_CONTROL_DYNAMIC` 枚举选择尾数位控制模式；fixed 变体是固定尾数版本，zgemm/gemmEx 各有 dynamic/fixed 两式共 8 个示例。

### 3.3 cuBLASLt：低级 GEMM 面板（L04 上半）

cuBLASLt 展示"把 GEMM 调度权交给开发者"的低级 API，目录名即精度阶梯：

| 示例目录 | 精度/特性 | 关键锚 |
|---|---|---|
| LtSgemm | 经典 FP32 入口 | — |
| LtDgemmPresetAlgo / LtDgemmEmulated | 预设算法/FP64 仿真 | — |
| LtFp8Matmul | FP8 逐张量缩放 | `sample_cublasLt_LtFp8Matmul.cu:23` 注释言明 per-tensor scaling+amax；:36-46 四个 scale 指针参数；:61 `cublasLtMatmulDescCreate(CUBLAS_COMPUTE_32F, CUDA_R_32F)` |
| LtMxfp8Matmul | MXFP8 块缩放 | `sample_cublasLt_LtMxfp8Matmul.cu:36-48` 缩放因子类型换 `__nv_fp8_e8m0`（每 32 元素一块的 e8m0 指数刻度）；:80-82 `CUBLASLT_MATMUL_DESC_{A,B}_SCALE_POINTER` 属性挂载 |
| LtNvfp4Matmul | NVFP4（Blackwell） | `sample_cublasLt_LtNvfp4Matmul.h:23` per-tensor **block** scaling；:37/:40/:47 数据类型 `__nv_fp4_e2m1` |
| LtBlk128x128Fp8{Matmul,gemmGroupedSimple} | Blackwell 128×128 块缩放 FP8 | — |
| LtSgemmGreenContext / LtPlanarComplex | Green Context / 平面复数布局 | — |
| LtFp8CustomFind / LtSgemmCustomFind | 算法枚举与自定义搜索 | 与 L01 nvMatmulHeuristics 呼应 |

共享底座：`Common/helpers.h`（800 行，fanIn=40）+`helpers.cpp`（显式模板实例化，tree-sitter 盲区由批分析手工补齐）。

### 3.4 cuBLASMp：张量并行算子田（L04 下半）

cuBLASMp 是大模型张量并行（TP）的官方示例田，基于 **CAL（Communication Abstraction Layer，MPI+NCCL 双栈）**：

- `tp_matmul.cu`（509 行）端到端覆盖：:31 `run_tp_matmul()`，:72-73 `cublasMpGridCreate` 建列主/行主两个进程网格（AllGather 列与 ReduceScatter 行的拓扑对偶），:466 `main`，:500-501 `Comm::collective_launch` 以 NCCL 通信器启动。
- `matmul_ag.cu`/`matmul_ar.cu`/`matmul_rs.cu`：TP 前反向形状的单算子变体（AG=AllGather+GEMM、RS=GEMM+ReduceScatter）。
- `gemm.cu`/`trsm.cu`/`symm.cu` 等 12 个 PBLAS 风格 2D 块循环分布算子（单文件 run_*+main 结构）。
- 共享底座最重：`helpers.h` 1525 行 + `matmul.h` 895 行 + `matrix_generator.hxx`。

---

## 4. 稀疏家族与求解器谱系：cuSPARSE→cuSPARSELt→cuSOLVER→cuDSS

### 4.1 cuSPARSE：35 个示例的全算子谱系（L05，150 文件）

算子维度全覆盖，且**每个示例都演示同一种"四段式"调用节奏**——以 `spmv_csr/spmv_csr_example.c` 为标尺：:88 `cusparseCreateCsr` 建稀疏描述符→:97 `cusparseSpMV_bufferSize`→:104 `cusparseSpMV_preprocess`→:110 `cusparseSpMV` 执行。spmm_csr 同构（:100/:111/:120/:128）。

- **格式谱系**：CSR/COO/BSR/BLOCKED-ELL/SELL 五代格式各有专属示例（spmv_sell、spmm_blockedell、dense2sparse_blockedell…）。
- **SpGEMM 三态**：`spgemm`（基础）/`spgemm_reuse`（两段式复用 workspace 与中间结果）/`spgemm_mem`（**注意：README 标题写的是泛型 cusparseSpGEMM，实际演示 `cusparseSpGEMM_estimateMemory` 显存受限变体**——`spgemm_mem/spgemm_mem_example.c:154/:164` 两处调用实证）。
- **SDDMM 采样乘**：`sddmm_csr`/`sddmm_csr_batched`/`sddmm_bsr` 三例。**勘误：`cuSPARSE/sddmm_bsr/README.md:1` 标题误写 `cusparseSDDMM CSR`，而源码 :159 注释明言"Create sparse matrix C in BSR format"——目录与代码是 BSR，仅 README 标题拷贝自 CSR 版未改**。
- **迭代求解器组合**：`cg/cg_example.c:156/:220/:294` 与 `bicgstab_example.c:190` 在迭代循环里反复调 `cusparseSpMV`，演示"库算子组装成求解器"。
- **图捕获**：`cuSPARSE/graph_capture/graph_capture_example.c:114-148` 完整 CUDA Graph 生命周期（:119 `cudaStreamBeginCapture`→:129 Instantiate→:135 Launch→:148 销毁），验证稀疏算子可捕获性。
- 其它：axpby/rot/gather/scatter/compression/coosort 元素级与预处理算子、gpsvInterleavedBatch 批量三对角、spvv/spmvop_csr/spmm_csr_op 变体。

### 4.2 cuSPARSELt：2:4 结构化稀疏极点（L05 内，9 节点小域）

专做张量核 2:4 结构化稀疏（每 4 元素至多 2 非零=50% 稀疏度）。`cuSPARSELt/matmul/matmul_example.cpp:206-208` 三件套（Descriptor/AlgSelection/Plan），**:218 `CUSPARSELT_SPARSITY_50_PERCENT` 是 2:4 的 API 表达**，:230-241 DescriptorInit→AlgSelectionInit→PlanInit→DescSetAttribute 链。`matmul_advanced` 加在线压缩与剪枝演示。

### 4.3 cuSOLVER 家族三层（L09+L10）

- **单节点 Dense（L09）**：分解主线 getrf（LU）/potrf（Cholesky）/geqrf（QR）+gesv 线性求解；特征值/奇异值谱系 syevd/syevj（Jacobi）/sygvd/gesvd/gesvdj；**X 前缀泛化变体**（Xgesvd/Xgesvdp/Xgesvdr/Xgeqrf/Xgetrf/Xpotrf/Xsyevd/Xsyevdx/Xtrtri——一个示例内按类型分发）与 **Mg 多 GPU 变体**（MgGetrf/MgPotrf/MgSyevd）；csrqr 稀疏 QR 两例；irs 迭代精化两代对照（`cusolver_irs_expert_cuda-10.2.cu` vs `cusolver_irs_expert_cuda-11.cu`）。工具头 `utils/cusolver_utils.h`（fanIn=39）+`cusolverMg_utils.h`。
- **cuSOLVERMp（L10）**：17 个 mp_* 示例把同类问题搬上 CAL 多 GPU——mp_potrf_potrs/mp_geqrf/mp_gels/mp_gesvd/mp_syevd/mp_sygvd/mp_sytrd_stedc_ormtr，外加 mp_laset/mp_polar（极分解）/mp_newton_schulz.cpp（本目录唯一 .cpp，回调以 lambda 传入）。**三文件族精度对照**：mp_potrf_potrs.c → _fp32.c → _fp32emulation.c 逐级只改数据类型与仿真开关。
- **cuDSS（L10）**：稀疏直接求解器 24 个 simple 示例（simple/batch/batch_sparse/complex/hybrid_execute_mode/hybrid_memory_mode/memory_handler/mgmn_distributed_matrix/mgmn_mode/mg_mode/multithreaded_mode/reordering_phase/residual/schur_complement/matrix_market/high_precision…）。入口节奏：`cuDSS/simple/simple.cpp:181-193` cudssCreate→ConfigCreate→DataCreate，:197 起建 Matrix 描述符。
- **cuSOLVERSp2cuDSS（L10）**：迁移指南域——`cuSolverSp2cuDSS.hpp` 单头模板实现，被 float/double/scomplex/dcomplex 四个 .cpp 各实例化一种 value_type；另有 csreigs2cuDSS（特征值迁移）；`cuSolverRf2cuDSS.hpp`+utils.hpp（enable_if 实/复分流）覆盖 cuSolverRf refine 路径。

---

## 5. FFT 与 MathDx：经典变换、构建链深水区与设备端对偶

### 5.1 cuFFT 经典域（L06，43 文件）

七个变换示例（1d_c2c/1d_mgpu_c2c/1d_r2c_c2r/2d_c2r_r2c/3d_c2c/3d_mgpu_c2c/3d_mgpu_r2c_c2r）+utils。`cuFFT/1d_c2c/1d_c2c_example.cpp:63/:69` 正逆变换各一行 `cufftExecC2C(plan, d_data, d_data, CUFFT_FORWARD/CUFFT_INVERSE)`，mgpu 变体演示多卡分工。共享 `utils/cufft_utils.h`（CUDA_RT_CALL/CUFFT_CALL 错误检查宏+scaling_kernel）。

### 5.2 lto_callback_window_1d：构建链深水区

本域最难也最有教学价值的是 **window load callback 的三实现对照**（legacy/NVRTC/LTO device）。LTO 路线展示了"设备函数如何嵌进宿主可执行"的完整构建链：

1. **编译**：`cuFFT/lto_callback_window_1d/CMakeLists.txt:92` 用 nvcc `--std=c++11 -dc -fatbin` 把 `r2c_c2r_lto_callback_device.cu` 编成 fatbin（GENCODE 带 `code=lto_<arch>`）；Makefile 等价链在 `cuFFT/lto_callback_window_1d/Makefile:59-63`。
2. **嵌入**：`cuFFT/lto_callback_window_1d/CMakeLists.txt:93` 用 CUDA 自带 **bin2c** 工具把 fatbin 转成 C 数组头 `r2c_c2r_lto_callback_device_fatbin.h`（`--name window_callback --type longlong`）。
3. **消费**：`src/r2c_c2r_lto_callback_example.cpp:32-33` include 该生成头，:77 `sizeof(window_callback)` 取字节数交给 cuFFT 的 LTO callback 注册接口。

NVRTC 对照实现在 `r2c_c2r_lto_nvrtc_callback_example.cpp`+`nvrtc_helper.h`（运行时编译 LTO IR）；legacy 对照在 `r2c_c2r_legacy_callback_example.cu`。三条路线同一数学（window 函数），差异全在"设备代码何时何地编译"。前置要求 CUDA 12.6 U2+（README.md:40 点名 cuFFT/NVRTC/nvJitLink）。

### 5.3 cuFFTMp：NVSHMEM 分布式 FFT（L07，86 文件）

- **samples/**（C++）：c2c/r2c_c2r 基础+pencils（笔式分解）+no_descriptors/cufftMpMakePlan/`cufftMpMakePlan` 变体+shared_scratch（共享 scratch 空间省显存）。公共底座 `samples/iterators/box_iterator.hpp`——自研 STL 兼容迭代器抽象 slab/pencil 两种数据分布，全部 C++ 示例靠它遍历本地盒子。
- **Fortran_samples/**：c2c/r2c_c2r/pencils 的 Fortran 版（`c2c/cufftmp_c2c.f90` 用 openACC 做设备侧缩放），`common.mk` 以 `?=` 环境变量覆盖模式管理库路径。
- **JAX_FFT/**：仓内最完整的 Python 生态对接线——把 cuFFTMp 封装为 JAX custom call 原语。`src/cufftmp_jax/cufftmp_jax.py` 三板式齐整：:31 `from jaxlib.hlo_helpers import custom_call`，:46 `_cufftmp_bind`（bind 原语），:154 `_cufftmp_abstract`（abstract_eval），中间 :64-93 `_partition`/`_supported_sharding` 实现 shard_map 集成，:103 `cufftmp()` 是用户面入口。`src/kernels.cu` 里 plan 缓存跨调用复用以摊销 cufftMakePlanMp。Dockerfile 的 `NVSHMEM_IB_SL/NCCL_IB_SL=1` 是大规模 IB 调优点。
- **extra_bootstraps/**：NVSHMEM bootstrapping 扩展示例。

### 5.4 MathDx：宿主库的设备端对偶（L11，249 文件，全仓第二大域）

`MathDx/README.md:9-14` 逐一点名五族+运行时：cuBLASDx（kernel 内 GEMM）/cuFFTDx（kernel 内 FFT）/cuSolverDx（kernel 内分解与求解）/cuRANDDx（**README 钦点"现代替代 cuRAND device API"**）/nvCOMPDx（设备端压缩）+libmathdx（C API JIT 编译设备函数，支撑 Python 等语言用 MathDx）。

- **cuFFTDx 00-10 号示例**与宿主域语义对映：00 introduction→01 thread 级→02 block 级→03 性能→04 NVRTC→05 FFT_Xd 高维→06/07 卷积（2D/3D）→08 混合精度→**09 LTO**→10 cufft device API 模式。`MathDx/cuFFTDx/00_introduction_example/introduction_example.cu:86` 的类型组合表达式是 Dx 范式的精髓：`decltype(Size<128>() + Precision<float>() + Type<fft_type::c2c>() + Direction<fft_direction::forward>())`——FFT 是编译期类型而非运行时 plan。
- **共享枢纽链**：`common/common.hpp`（526 行，fanIn=52：错误宏+`measure_execution_ms` :157+`sm_runner` :309 按架构循环）+`block_io.hpp`（233 行，`io<FFT>` 模板统一 global↔register 装载与 half2 RRII/RIRI 布局转换）+`random.hpp`。09 号 LTO 示例的 CMakeLists 用"运行期 file(READ) CSV+foreach 生成目标"模式。
- **cuBLASDx 16_dgemm_emulation** 与 L03 Emulation 呼应（`emulation_kernels.hpp` 的 `__grid_constant__ DevicePipeline` 传参）；15_nvrtc 走 NVRTC 动态编译。cuSolverDx 的 `common/random.hpp`（231 行）专造对角占优对称正定矩阵保 POTRF 数值健康，`error_checking.hpp` 是全示例验证底座。
- tree-sitter 对这批 namespace 内模板类/模板函数头文件全盲，图谱结构靠批分析手工补齐（NOTES-DIGEST 记录 7 处）——阅读时不要期待函数级导航，按示例目录读。

---

## 6. cuRAND 与随机域：Host API 矩阵与两处官方文案勘误

### 6.1 域修正：本域只覆盖 Host API

cuRAND/README.md:11 起全部条目都是 "**cuRAND xxx … using Host API**"——**经典 cuRAND 的 Device API 示例不在本仓**。但设备端随机数并非空白：MathDx/cuRANDDx（01_introduction/02_thread_api/03_nvrtc，代表文件 `01_introduction/philox_thread_api.cu`）就是官方给出的现代替代路径（cuRANDDx README 钦点替换关系，要求 Turing SM75+）。把 cuRAND/（Host 域）与 MathDx/cuRANDDx（Device 域）放在一起读才是完整的 cuRAND 图景。

### 6.2 引擎×分布矩阵与双路径互验

9 引擎（xorwow/philox/mtgp32/mt19937/mrg32k3a/sobol32/sobol64/scrambled_sobol32/scrambled_sobol64）×4 分布（uniform/normal/lognormal/poisson）矩阵式展开。philox 三示例展示 **host/device 双路径互验**：`cuRAND/Host/philox/curand_philox_uniform_example.cpp:48` `curandCreateGenerator(CURAND_RNG_PSEUDO_PHILOX4_32_10)`（设备路径，:63 生成到 d_data）与 :84 `curandCreateGeneratorHost`（主机路径，:99 直接生成到 h_data——Host API 能把随机数直接写主机内存）。

### 6.3 构建特性与两处文案勘误

- **纯主机编译域**：全部示例是 .cpp（无 .cu），`cuRAND/cmake/curand_example.cmake:17` 的 `add_curand_example` 同样设 `CUDA_ARCHITECTURES OFF`，gcc/g++ 主机编译器只链 CUDA::cudart+CUDA::curand。**勘误一（任务假设修正）：全 cuRAND/ 目录 grep 不到任何 cublas 引用——"gcc 链接 cuBLAS"不成立**；全仓真正在主机侧加载 libcublas.so 的是 cuEST 的 Python 绑定 `cuEST/python_examples/helpers/cuda_utils.py:39`（ctypes `LoadLibrary('libcublas.so')`，:44 libcusolver、:57 libcudart 同款）。
- **勘误二（官方 README 用词）**：cuRAND/README.md:95/:99/:103/:107/:111… 把 scrambled_sobol32/64 各分布条目写成 "**pseudorandom** generation"，而源码 `cuRAND/Host/sobol32/curand_sobol32_uniform_example.cpp:48` 用的是 `CURAND_RNG_QUASI_SOBOL32`——Sobol 是**准随机（quasi-random）**序列（低差异序列），非伪随机；sobol64/scrambled 系全部同款。
- 工具头 `cuRAND/utils/curand_utils.h:50/:55` 仅 float/unsigned int 两个 `print_vector` 特化（对比 cublas_utils 的四精度全家族）。

---

## 7. 图像与专用域：编解码、图像处理、压缩、张量与量子化学

### 7.1 nvJPEG 三库（L14，66 文件）

- **nvJPEG**：nvJPEG-Decoder（解码主线，`nvJPEG/nvJPEG-Decoder/nvjpegDecoder.h:237-238` `nvjpegDecoderCreate(NVJPEG_BACKEND_DEFAULT)`+`nvjpegDecoderStateCreate` 的解耦态解码节奏）、Decoder-Backend-ROI（ROI 后端选型）、Decoder/Encoder-MultipleInstances（多实例）、Image-Resize/Image-Resize-WaterMark（解码后处理级联）。
- **nvJPEG2000**：Decoder/Decoder-Pipelined（流水线）/Decoder-Tile-Partial（分块部分解码）/Encoder 四例。
- **nvTIFF**：Decode/Encode-Options/Decode-Encode/Batched-Region-Decode（批量区域解码）/GeoTIFF-Decode-Encode（**地理栅格格式**，遥感场景）/Image-Info-Multi-Image，`common/nvtiff_samples_common.h` 共享。

### 7.2 NPP 与 NPP+：两代图像 API 并置（L13，143 文件）

NPP 经典 C API 四例（batchedLabelMarkersAndCompression/distanceTransform/findContour/nppCanny），NPP+ 高级 C++ API 三例（floodFill/watershedSegmentation/findContour 等）。`NPP/nppCanny/` 下有 `BLOG.md`（Canny 教学博文）+cannyEdgeDetectorPython 脚本线（**勘误：BLOG.md 在 NPP/nppCanny/ 下而非 NPP+/，图谱代表节点显示时易误读**）。两域各 vendored 一份第三方 `dirent.h`（NPP/batchedLabelMarkersAndCompression/ 与 NPP+/batchedLabelMarkersAndCompression/，图谱按共享枢纽原则仅建 file 节点不深析——跨平台目录遍历的兼容垫片）。`.raw` 测试图像随仓分发。

### 7.3 nvCOMP：压缩算法矩阵与 nvbench 基准（L12，48 文件）

- **examples/**：quickstart 双门面（`high_level_quickstart_example.cpp:24` include `nvcompManagerFactory.hpp` 走 HLIF 高层接口，:63-64 `nvcompBatchedLZ4CompressDefaultOpts` 一行拿默认配置；low_level_quickstart 走底层描述符）；算法原生 API 全家（bitcomp_native_lossy/gzip_gpu/gdeflate/deflate…）；**CPU+GPU 异构组合**一族（lz4/deflate/gdeflate/snappy/zstd 的 `*_cpu_compression.cu`——CPU 压缩+GPU 解压）；nvcomp_gds（GDRCopy 直存）、nvcomp_crc32。
- **benchmarks/**：nvbench 模板横评 12 个 `benchmark_*_chunked.cu`（ans/bitcomp/cascaded/deflate/gdeflate/gzip/lz4/snappy/zstd…）+bitcomp_lossy+hlif+bitcomp_cpu+gdeflate_cpu+crc32，`benchmark_template_chunked.cuh` 统一骨架，`BatchData.h`（含 operator== 供压缩往返校验）是示例与基准共享的数据抽象。
- **python/** 子目录提供 Python 绑定示例。

### 7.4 cuTENSOR 家族（L16，43 文件）

- **主线**：contraction（基础缩并）→`contraction_jit.cu:129` `cutensorCreate`+:186 `cutensorCreateContraction`（JIT 即时编译描述符）→contraction_plan_cache（plan 缓存复用）→blocksparse（块稀疏缩并）→contraction_trinary/elementwise 系。
- **einsum.cu**（466 行）：`einsum()` 封装爱因斯坦求和，main 在 :434，:447-451 五次调用一次演示显式/隐式缩并、置换、归约（`"ijn,jmk->inkm"`/`"nij"`/`"nij->ji"`）——**全仓最高层 API 的教学样本**。
- **python/**：einsum 做成 torch/tensorflow 自定义算子（`python/cutensor/tensorflow/einsum_kernel.cc` 的 REGISTER_GPU 宏四实例化）。
- **cuTENSORMg**：多 GPU 缩并；**cuTENSORMp**：NCCL 分布式缩并/redistribute/unfold-fold。构建侧 `cuTENSOR/CMakeLists.txt` 用 IMPORTED 目标而非 find_package，CMake 3.24+ 门槛。

### 7.5 cuEST：量子化学最大域（L15，265 文件，全仓第一）

三条线+数据资产：

- **c_examples/** 七章（0_context→1_basic_data_structures→2_one_electron_integrals→3_density_fitting→4_exchange_correlation→5_effective_core_potentials→6_pcm），common/ 五个 helper：`helper_xyz_parser.h:68` `symbol_to_atomic_number`/`:91` `parseXYZFile`，`helper_gbs_parser.h:118` `parseGBSFileForElement`（按元素提取收缩壳层），`helper_workspaces.h`/`helper_ao_shells.h`（:formAOShells 构造 AO 壳层）/`helper_status.h`（cuestCheck 错误检查）。`run_all.sh` 用 set -euo pipefail+CMakeCache grep 自动装配。
- **python_examples/** 同构七章，helpers/ 以 **纯 ctypes** 直驱 CUDA 栈（`cuda_utils.py:39` libcublas/:44 libcusolver/:57 libcudart），把用户管理的 GPU 资源以回调注入 cuestCreate——"C API 无官方 binding 时的标准做法"样本。
- **cuest_scf_examples/**：上层 SCF 自洽场库（examples/ rhf-1/uhf-1/mp2-1/cphf-1），`cuest_scf/__init__.py` 是约 30 条 re-export 的 barrel（:26 注释掉的 ECPShell 行显示其尚未公开）；`cuest_handle.py` 包装 cuestCreate/Destroy+math_mode（FP32/FP64/仿真）+JIT 设置；cphf-1 的 `kernel_helper.py` 是 cuda-python+NVRTC 双依赖的 JIT 模式代表。
- **data/**：`basis_set/def2-svp.gbs`、`def2-svp-ecp.gbs`、`def2-universal-jkfit.gbs`（def2 基组族）+`geometry/h2o.xyz` 等——C/Python 双线共用。

### 7.6 L01 两个专项小域

- **nvMatmulHeuristics/**：cuBLASLt GEMM 启发式发现教程 0-7（`1_gemm_heuristics.cpp` 81 行 ：22 include `<nvMatmulHeuristics/nvMatmulHeuristics.h>`；README:35-40 展示 CTA/Warp/Instr/Stages/SplitK 配置表输出；5-7 号是 get_configs/exasm 采样 Python 脚本）。
- **cuPQC/**：GPU 后量子密码（example_ml_kem.cu/example_ml_dsa.cu/example_sha2.cu/example_sha3.cu/example_poseidon2.cu/example_merkle.cu）——NIST PQC 标准算法的 GPU 实现示例。

---

## 8. 新人上手：阅读路线、共享基建与勘误清单

### 8.1 推荐阅读路线（一周节奏）

1. **Day 1 骨架**：根 `README.md:29-53` 域清单→挑一个三件套读透（`cuBLAS/Level-1/axpy/`：源码 57 行处 cublasCreate 起的生命周期+CMakeLists 里对 add_cublas_example 的调用+README）。
2. **Day 2-3 主线**：cuBLAS Level-1→3 挑 gemm/gemmStridedBatched，转 Extensions/GemmEx，转 Emulation/bf16x9（:96/:126 两次调用的对照是最直观的精度课）。
3. **Day 4 进阶**：cuBLASLt LtFp8→LtMxfp8→LtNvfp4 精度阶梯（三个示例的 scale 类型从 float→e8m0→e2m1 块缩放）；cuBLASMp/tp_matmul.cu 看 TP 拓扑。
4. **Day 5 稀疏+求解**：cuSPARSE spmv_csr 四段式→spgemm 族→cg 组合；cuSOLVER potrf→Xpotrf 类型分发；cuDSS/simple。
5. **Day 6 深水区**：cuFFT/lto_callback_window_1d 构建链（CMakeLists:92-93 是全仓唯一 bin2c 样本）；MathDx/cuFFTDx 00→09。
6. **Day 7 专题**：按方向选修——LLM 工程师走 tp_matmul+cuSPARSELt；图像走 NPP→nvJPEG；科学计算走 cuEST 七章；Python 生态走 cuFFTMp/JAX_FFT+cuTENSOR/python。

### 8.2 共享基建地图（改示例前必读）

改任何示例先看它的 utils/cmake 枢纽（第 2.2 节表格）：cuBLAS 系示例的报错宏/打印/随机矩阵全部来自 `cublas_utils.h`，别在示例内重造；构建入口是域级 cmake 模块的函数（add_cublas_example/add_curand_example/add_cusolver_example），新加示例=新建目录+两行 CMakeLists。nvCOMP 的 BatchData.h、MathDx 各 common/、cuEST 五 helper 同理。

### 8.3 勘误清单（源码实证，阅读时防坑）

| # | 勘误 | 证据锚 |
|---|---|---|
| 1 | sddmm_bsr README 标题误写 `cusparseSDDMM CSR`，实际是 BSR | `cuSPARSE/sddmm_bsr/README.md:1` vs `sddmm_bsr_example.c:159` |
| 2 | spgemm_mem README 标题是泛型 SpGEMM，实际演示 `cusparseSpGEMM_estimateMemory` 显存受限变体 | `cuSPARSE/spgemm_mem/spgemm_mem_example.c:154/:164` |
| 3 | cuRAND README 把 scrambled sobol 系写成 "pseudorandom"，API 实为 QUASI 准随机 | `cuRAND/README.md:95` vs `curand_sobol32_uniform_example.cpp:48`（CURAND_RNG_QUASI_SOBOL32） |
| 4 | cuRAND 域与 cuBLAS 零关联（无链接无调用）；主机侧加载 libcublas 的是 cuEST Python | `cuRAND/cmake/curand_example.cmake:17-23`（仅 cudart+curand）vs `cuEST/python_examples/helpers/cuda_utils.py:39` |
| 5 | cuRAND 经典 Device API 不在本仓，设备端 RNG 看 MathDx/cuRANDDx | `cuRAND/README.md:11`（全部 Host API）+ `MathDx/cuRANDDx/README.md` |
| 6 | BLOG.md 在 `NPP/nppCanny/` 下，不是 NPP+ | `NPP/nppCanny/BLOG.md` |
| 7 | einsum.cu 的"21 行 main"说法不确：main 在 :434，函数体到 :457，总 466 行 | `cuTENSOR/einsum.cu:434` |
| 8 | scanner 把全部 CMakeLists.txt 归 txt/docs、Makefile 归 makefile/infra——图谱已甄别修正为 config/pipeline 语义（约 70 处） | NOTES-DIGEST batch-41~80 系列记录 |
| 9 | cuFFT mgpu 示例的"多卡"是单节点多 GPU（cufftXt API：`cufftXtSetGPUs` 挂卡+cufftXtExecDescriptor 执行），跨节点分布式在 cuFFTMp | `cuFFT/1d_mgpu_c2c/1d_mgpu_c2c_example.cpp:90` vs `cuFFTMp/samples/c2c_pencils/` |
| 10 | helpers.cpp/LTO 头等模板重灾区 tree-sitter 提取不全，图谱结构以 file 节点+手工补齐为准 | NOTES-DIGEST batch-7/9/12/18 记录 |

### 8.4 构建提示

三套构建并存：域级 CMake（主流，`cmake .. && make`）、目录级 Makefile（bin/ 输出，如 lto 示例 Makefile:50 的三目标）、脚本（cuEST run_all.sh）。多数域 README 给出"前置 CUDA 版本+对应库"清单（如 lto 需 CUDA 12.6 U2+cuFFT/NVRTC/nvJitLink，`cuFFT/lto_callback_window_1d/README.md:40`）；cuBLASMp/cuSOLVERMp/cuFFTMp 还需 MPI+NCCL/NVSHMEM 运行时，JAX_FFT 走 Docker。设备门槛各异：cuRANDDx 要 Turing+，NVFP4 系要 Blackwell。

### 8.5 图谱使用提示

knowledge-graph.json 的 import 边基本只反映"示例→utils 枢纽"与"示例→CMake 模块"两类依赖（域内扇入集中、域间为零）；跨域语义对映（host/device 对偶、精度阶梯、Mp 分布式族）存在 tour 步骤描述里而非边上——查"cuBLASLt 与 nvMatmulHeuristics 的呼应"这类关系请走 tour t03/t16 与本文第 2.3 节，别指望边查询。

（完）

