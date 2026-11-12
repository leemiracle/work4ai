# NVPL BLAS C 示例集（nvpl_blas/c）

## 1. 角色定位

`nvpl_blas/c` 是 NVPL（NVIDIA Performance Libraries）BLAS 库 **CBLAS C 接口**的官方示例目录：160 个 `.c` 文件（每文件一个 `main`、演示一个目标函数），加共享辅助头 `example_helper.h` 与 `CMakeLists.txt` 共 162 个目录项。NVPL 是面向 NVIDIA Grace/Vera 等 aarch64 CPU 的纯 CPU 数学库（零 CUDA 依赖），C 示例展示它作为标准 CBLAS 的 drop-in 替代怎么用，以及 NVPL 特有扩展（axpby、gemmt、批接口、显式 64 位入口、线程控制服务函数）的调用姿势。它与 `nvpl_blas/f77`（Fortran 侧示例）互为姊妹目录，二者由同一个顶层 CMake 工程（`nvpl_blas/CMakeLists.txt:19` 的 `project(nvpl_blas_examples LANGUAGES Fortran C)`）统一编排。

## 2. 内部结构

**文件按 `<精度前缀><例程名>.c` 命名**，s/d/c/z 四种前缀覆盖单精度/双精度/单复数/双复数。按 BLAS 分层组织：

- **Level 1（向量-向量）**：`axpy/copy/swap/scal/dot/nrm2/asum` 族 + `rot` 八件套（`srot.c/srotg.c/srotm.c/srotmg.c` 及 d 系列）+ 索引最大值 `isamax.c/idamax.c/icamax.c/izamax.c`。混合精度变体独立成文件：`csscal.c/zdscal.c`（复数向量乘实标量）、`dsdot.c/sdsdot.c`（双精度累加的点积）、`scnrm2.c/dznrm2.c`、`scasum.c/dzasum.c`（复数的实部虚部分别求和）。
- **Level 2（矩阵-向量）**：`gemv/gbmv/trmv/trsv/tbmv/tbsv/tpmv/tpsv` 四精度全套；对称/Hermitian 族（`symv/hemv/sbmv/hbmv/spmv/hpmv/syr/her/spr/hpr` 及 rank-2 变体 `syr2/her2/spr2/hpr2`）只有 s/d 或 c/z 各两种精度——实数走 sym 系、复数走 her 系，天然对半分。带状例程（`gbmv/tbmv/tbsv`）是唯一用到 `fill_*bandmatrix` 辅助函数的家族。
- **Level 3（矩阵-矩阵）**：`gemm/symm/syrk/syr2k/trmm/trsm` 四精度 + `hemm/herk/her2k` 双精度（c/z）+ **NVPL 扩展**：`gemmt`（三角形输出 GEMM，`sgemmt.c` 等 4 个）、`gemm_batch` 与 `gemm_batch_strided`（各 4 个，gemm 家族共 17 个文件）、`dgemm_64.c`（显式 ILP64 入口，全目录唯一）、`caxpby.c/daxpby.c/saxpby.c/zaxpby.c`（厂商扩展 AXPBY）。
- **`service_functions.c`**：非计算例程，演示版本查询与线程控制（见下）。

**共享辅助头 `example_helper.h`（1143 行）** 是整个目录的"工具箱"，全部函数 `static`（header-only，每个示例独立编译各带一份）：

- 16 个 `fill_*` 数据生成器：稠密矩阵 `fill_smatrix/dmatrix/cmatrix/zmatrix`（`example_helper.h:26/82/138/198`）、向量 `fill_s/d/c/zvector`（`:256/271/285/299`）、带状矩阵 `fill_s/d/c/zbandmatrix`（`:314/372/430/488`）。
- 16 个 `print_*` 打印器，与 fill 一一对应（向量 `:545-599`、稠密 `:613-732`、带状 `:744-1084`）。
- 5 个枚举转字符的单行转换器：`transpose_to_char/order_to_char/uplo_to_char/diag_to_char/side_to_char`（`example_helper.h:1086/1099/1110/1121/1132`），把 CBLAS 枚举打成 F77 风格单字母，用于 `#### args` 参数回显行。

两个值得注意的实现细节：其一，fill 采用**确定性伪随机**——稠密矩阵元素是 `1/1024.f * ((91u + j) & 1023u) - 0.5f`（`example_helper.h:32`，值只依赖列号 j），复数虚部用 `479u` 偏移（`:145`）；带状矩阵更直接，值等于线性存储索引 `A[i*ld + j_start + l] = (float)(i*ld + j_start + l)`（`:328`），肉眼即可核对存储布局。其二，三角矩阵填充会把"例程按约定不应触碰的区域"填 `NAN`、对角线在 `CblasUnit` 时强制 1.0（`example_helper.h:38-44`）——若实现违规读取未引用区域，输出立即显形。

## 3. 外部连接

每个示例通过 `example_helper.h:7` 的 `#include "nvpl_blas_cblas.h"` 接上 NVPL 安装提供的 CBLAS 主头（由 `nvpl::blas_*` imported target 的 include 目录带进来）。两个例外走自己的头：`dgemm_64.c:11` 额外包含 `nvpl_blas_cblas_64.h`（声明 `cblas_dgemm_64`）；`service_functions.c:10` 包含 `nvpl_blas.h`（服务函数不在 cblas 头里）。

构建侧，`nvpl_blas/c/CMakeLists.txt` 对 `*.c` 做 `file(GLOB)`（第 3 行），**每个源文件生成一个可执行目标**，命名为 `c_${INT_TYPE}_${THR_TYPE}_${name}`（第 6 行，如 `c_ilp64_omp_sgemm`），链接 `nvpl::blas_${INT_TYPE}_${THR_TYPE}`（第 11 行）；`THR_TYPE=omp` 时追加 `OpenMP::OpenMP_C`（第 13-16 行），并全部注册 `add_test`（第 18 行）——目标名即 ctest 测试名。`INT_TYPE`（lp64/ilp64）与 `THR_TYPE`（omp/seq）在顶层 `nvpl_blas/CMakeLists.txt:25-28` 定义为 cache 变量，`CMakePresets.json` 预置了四种组合；顶层还固定 `CMAKE_C_STANDARD 99`（`:20`）与 `CMAKE_Fortran_FORMAT FIXED`（`:21`，服务 f77 子目录）。

## 4. 数据流

`caxpy.c`（46 行）是全目录的范本，四段式骨架：**声明参数 → 算长度分配 → 填充打印 → 调用打印释放**。先 `printf("#### args: ...")` 用 `PRId64` 显式回显参数（`caxpy.c:18-19`）；再按步长算实际占用 `len_x = 1 + (N - 1) * labs(incX)`（`:21-22`）后 malloc——这是处理负步长/跨步向量的关键一步；`fill_cvector` 填 X/Y、`print_cvector` 打输入（`:28-33`）；第 36 行一行调用 `cblas_caxpy(N, &alpha, X, incX, Y, incY)`；打结果、free、返回。

两个批接口示例展示同一计算的两条数据组织路线：**group 版**（`cgemm_batch.c`）把异构 GEMM 分组，M/N/K/lda/alpha/ transA 全是 `GROUP_COUNT` 长度的数组（`:12-23`），矩阵本体装进指针数组 `A_array/B_array/C_array`（`:39-41`），`total_batch_count` 由 `group_size` 累加（`:35-37`），一次调用（`:82-83`）处理 2 组共 5 个矩阵；**strided 版**（`cgemm_batch_strided.c`）面向同构大批量：单块大 buffer 一次 malloc（`:51-53`），第 i 个矩阵地址用指针算术 `A + strideA * i`（`:57`），stride 直接取 `lda * colsA`（`:36-41`）。`dgemm_64.c` 演示 ILP64 入口：尺寸参数声明为 `nvpl_int64_t`（`:14-19`），调用 `_64` 后缀变体（`:59`）；由于 helper 函数签名吃 `nvpl_int_t`，需显式收窄转换并附注释说明（`:47-51`）。

`service_functions.c` 的数据流是"控制流"：编译期版本宏 `NVPL_BLAS_VERSION_MAJOR/MINOR/PATCH` 对比运行时 `nvpl_blas_get_version()`（`:20-27`）验证链接的就是预期库；随后 `nvpl_blas_get_max_threads()`（`:34`）→ `nvpl_blas_set_num_threads(2)`（`:40`）→ OpenMP 并行区里 `nvpl_blas_set_num_threads_local(4)` 线程私有覆盖（`:56`），并演示并行区内默认不再嵌套并行（`:65-69` 的注释）。

## 5. 设计决策

- **每文件一例程 + GLOB 全量建目标**：示例集要的是"查 API 即得可运行最小程序"，每个 `.c` 自成一体可单独摘抄；代价是目标数 = 文件数（lp64/omp 下 160 个可执行），对示例工程完全可接受。
- **helper 全 static 的 header-only**：无公共库、无符号冲突、拷进任何工程即用；牺牲了二进制体积（每目标一份拷贝），示例场景无关紧要。
- **确定性数据代替 rand()**：无 seed、无平台差异，教程输出与文档截图永远一致——比随机数据更适合回归对照。
- **batch 双 API 对峙**：group 版参数全数组（表达异构）、strided 版全标量+stride（表达同构），对应真实负载的两类批处理形态；这组命名与 cuBLAS 的 batch/group API 同构，方便 GPU 代码迁移对照。
- **`dgemm_64` 显式 64 位入口**：注释明说该符号 **从 LP64 和 ILP64 两种库构建中都导出**（`dgemm_64.c:4-7`）——与"整库切 ilp64"路线互补，让单个超大尺寸调用混进 lp64 工程而不必整包 ABI 迁移。
- **枚举转换器的 default 分支**：`transpose_to_char` 对未知枚举值返回 `'T'`（`example_helper.h:1094-1095`），`side/uplo/diag/order` 各有类似兜底——打印辅助函数的防御式取向，坏值不崩、印出来即可诊断。
- **`PRId64` + `(int64_t)` 强转打印**：`nvpl_int_t` 在 lp64 构建是 32 位、ilp64 下 64 位，统一转 `int64_t` 配 `PRId64` 让两种构建的输出格式一致（`caxpy.c:18`）。

## 6. 新人提示

- **上手顺序**：`caxpy.c`（46 行，看懂四段式）→ 任一 `?gemm.c`（矩阵版）→ `cgbmv.c`（带状布局）→ `cgemm_batch.c` 与 `cgemm_batch_strided.c`（两种批组织对照读）→ `dgemm_64.c` → `service_functions.c`（线程模型）。读完这七个，其余 150 余个都是同一骨架的参数变奏。
- **构建运行**：`cmake -S nvpl_blas -B build -DINT_TYPE=lp64 -DTHR_TYPE=omp && cmake --build build && cd build && ctest`；或直接用 preset（如 `--preset ilp64_seq`）。README 给的运行样例是 `./build/c/c_ilp64_omp_sgemm`（`nvpl_blas/README.md:36-37`）。
- **坑**：①`nvpl_int_t` 宽度随 INT_TYPE 变，打印别写 `%d`，照抄示例的 `PRId64` 惯用法；②`fill_*bandmatrix` 填的是**线性索引值**不是伪随机数，核对带状存储时按"值=位置"读；③`_64` 入口的参数是 `nvpl_int64_t`，与 helper 的 `nvpl_int_t` 混用要显式转换（`dgemm_64.c:49` 的写法即答案）；④group 批示例里 `total_batch_count` 与结果回读的 `idx` 必须同步推进（`cgemm_batch.c:35/87`），改示例时容易漏；⑤helper 头的函数全是 `static`，不能指望"链接期共享"，跨文件复用只能靠 include。
- 平台前提：aarch64 Linux，NVPL 26.x（README 声明示例只保证对最新 NVPL 版本兼容）。
