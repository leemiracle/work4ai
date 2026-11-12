# 01 cuBLAS 经典主线：Level-1/2/3 教学阶梯与 utils 枢纽

## 角色定位

cuBLAS 目录是全仓的"第一课"：以教科书式节奏展示经典 BLAS 三级 API（对应图谱 L02 层，160 节点，是仓内最大的单一示例群）。Level-1 共 13 个示例目录（dot 目录内含 dot/dotc 两个可执行体，共 14 例）、Level-2 共 23 个、Level-3 共 16 个，合计 52 目录；再加 Extensions 与 Emulation，全家族 78 个示例 CMakeLists 复用同一个注册函数（`cuBLAS/cmake/cublas_example.cmake:16` 的 `add_cublas_example`）——注意 NOTES-DIGEST 记的"88 个"有误，实测 `grep -rl add_cublas_example | wc -l` 为 78。

## 内部结构

每个示例是同一副骨架的五步流程，以 axpy 为例：step1 建 handle 并绑流（`cuBLAS/Level-1/axpy/cublas_axpy_example.cu:57-60`），step2 异步拷入设备（:63-69），step3 计算一行（:72 `cublasDaxpy`），step4 拷回并同步（:75-78），step5 逆序释放（:89-96）。Level-3 的 gemm 同构（`cuBLAS/Level-3/gemm/cublas_gemm_example.cu:87`），仅参数从向量换成 m/n/k/lda 与 alpha/beta。所有示例 `using data_type = double`（axpy_example.cu:28）——文件名是泛型算子名，实际演示的是 D 前缀的 double 变体，改名一行即可切换精度。

枢纽是 `cuBLAS/utils/cublas_utils.h`（377 行）：`CUDA_CHECK`/`CUBLAS_CHECK` 宏（:34/:44）抛异常而非 exit；`traits<>` 对 float/double/cuComplex/cuDoubleComplex 四特化（:62-:134）统一 abs/rand/add/mul 与 `cudaDataType` 映射；`print_matrix`/`print_packed_matrix`/`print_vector` 三族模板全特化（:136-:267）覆盖列主序与 packed 布局打印；`generate_random_matrix`（:269）与 `make_diag_dominant_matrix`（:297，供求解类示例保证收敛）。CMake 侧 `add_cublas_example` 设 `CUDA_ARCHITECTURES OFF`（cublas_example.cmake:18）——示例无设备代码，无需按架构重复编译。

## 外部连接

utils 头被 100+ 个示例经 `../../utils` 包含路径引用（各示例 CMakeLists 统一配置），是图谱 t15"共享基建域"在 cuBLAS 侧的根。Emulation 子域把 utils 向下延伸：`getFixedPointWorkspaceSizeInBytes`（cublas_utils.h:348-377）就是为 FP64 仿真示例定制的。上游依赖仅 cublas 与 cudart（cublas_example.cmake:23-26）。

## 数据流

以 Emulation 亮点 `zgemm_fixed` 为例（`cuBLAS/Emulation/zgemm_fixed/cublas_zgemm_fixed_example.cu`，173 行）：注释块（:32-45）先交代三个环境变量（`CUBLAS_EMULATE_DOUBLE_PRECISION`/`CUBLAS_EMULATION_STRATEGY`/`CUBLAS_FIXEDPOINT_EMULATION_MANTISSA_BIT_COUNT`）；随后 `mantissaBitCount = 55`（:51，注释点明即 7 个 INT8 切片——55+1 尾数位按 8 位一片切 7 片）。与经典五步相比多两步：预分配 workspace（:112-115，调 utils 的 workspace 公式后 `cublasSetWorkspace`，注释明言不预分配会退到 cudaMallocAsync 慢路径）；四连配置（:131-:140）依次 `CUBLAS_FP64_EMULATED_FIXEDPOINT_MATH` 数学模式、EAGER 策略、FIXED 尾数控制、55 位上限，最后照常 `cublasZgemm`（:144）。workspace 公式本身见 utils：m/n 按 1024 对齐、k 按 128 对齐（cublas_utils.h:356-358），尾部恒加 128MB 常数（:375）与 1.25 倍系数（:351）。

## 设计决策

三个值得抄的决策：其一，示例代码"求同"，全部复用 utils 与同一 CMake 函数，改动面收敛在算子调用一行；其二，列主序数据在注释里画矩阵（gemm_example.cu:40-46 的 A={1,3,2,4} 即列优先），提醒 Fortran 血统与 C 数组的错位；其三，Emulation 用"环境变量文档化 + API 四连"双通道控制，注释比正文长，是官方 API 文档的补充教材。勘误一处：`cuBLAS/README.md:201` 与 :205 把 syr2k/syrkx 两条目都写成 "cuBLAS syrk"，且 Level-3 的 gemmGroupedBatched 目录未列入 README。

## 新人提示

从 Level-1/axpy 入门即可掌握全部示例的 95% 结构；读 Emulation 前先读 utils 的 workspace 公式，注意 zgemm_fixed 的精度预算（55 尾数位≈double 的 52+3）与 7 切片的换算关系。改示例做实验时只动 `data_type` 与 step3；要加新示例，抄任一子目录的 CMakeLists（一行调 `add_cublas_example`）即可入组。
