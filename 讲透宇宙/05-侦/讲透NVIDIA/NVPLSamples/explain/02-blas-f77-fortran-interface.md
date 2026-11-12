# NVPL BLAS Fortran 77 接口示例（nvpl_blas/f77）

## 1. 角色定位

`nvpl_blas/f77` 是 NVPL BLAS **Fortran 77 经典接口**（即 BLAS 原生调用约定：全大写例程名、参数全为标量/数组引用）的示例目录，170 个 `.f` 文件中含 168 个示例程序、1 个共享辅助源 `common_func.f`、1 个 `service_functions.f`（另有 CMakeLists）。它与 `nvpl_blas/c` 是一对姊妹目录：两边共享 158 个同名示例，f77 侧独有 10 个（`cgemm3m.f/zgemm3m.f`、复数 Givens 旋转 `crotg.f/zrotg.f/csrot.f/zdrot.f`、绝对值最小索引 `isamin.f/idamin.f/icamin.f/izamin.f`——这批在 CBLAS 标准里没有对应入口），C 侧独有 `dgemm_64.c`（`_64` 后缀入口是 C 接口特性）。对从古老 Fortran HPC 代码迁移到 Grace CPU 的用户，这里就是"接口兼容性"的直接证据：只需换链接库，源码几乎不动。

## 2. 内部结构

**固定格式（FIXED form）**：顶层 `nvpl_blas/CMakeLists.txt:21` 设 `CMAKE_Fortran_FORMAT FIXED`，所有源码遵守 72 列固定格式——代码从第 7 列起，续行符在第 6 列（`caxpy.f:22` 的 `&`、`cgemm_batch.f:18` 的 `$`、`caxpy.f:25` 的 `&` 都在用），注释行首列 `!` 或 `*`。

**程序命名 `XXX_MAIN`**：168 个示例程序全部命名为 `<例程名>_MAIN`（`caxpy.f:7` 的 `program CAXPY_MAIN`、`cgemm_batch.f:7`、`daxpby.f:7`），两个例外是 `common_func.f`（纯子程序库，无 program）与 `service_functions.f:1` 的 `program SERVICE_FUNCTIONS`。这保证了同一可执行文件里例程名（如 `CAXPY`，外部过程）与主程序名不冲突。

**外部接口机制 `include "nvpl_blas_f77_blas.fi"`**：169 个源文件共 170 处包含该文件（`common_func.f` 在 `get_dnan/get_snan` 各包含一次，第 5、16 行），唯一的例外是 `service_functions.f:5` 改用 `include 'nvpl_blas.fi'`。这些 `.fi`（Fortran include）文件不在本仓库而在 **NVPL 安装包**里，内容是全部 BLAS 例程的显式 `EXTERNAL`/接口声明——F77 无标准头文件机制，NVPL 用 include 文件给隐式类型检查兜底，避免调用方手写 `EXTERNAL` 清单。示例本体仍保留 `external print_cvector` 一行（`caxpy.f:28`）声明辅助子程序。

**`common_func.f`（708 行、26 个例程）** 是 F77 侧的"工具箱"，与 C 侧 example_helper.h 职能对等但结构不同——它是**独立编译的源文件**而非头文件：

- 2 个 NaN 工厂函数：`get_dnan()`（`common_func.f:2-11`）与 `get_snan()`（`:13-22`）。实现是位级构造：`data nan_bits_data/Z'7FFFFFFFFFFFFFFF'/` 后 `ibset(...,bit_size(1_8)-1)` 置符号位、再 `transfer` 成浮点（`:8-10`）——因为 F77 标准（甚至 F90）没有可移植的 NaN 字面量。
- 8 个向量/矩阵填充例程：`fill_s/d/c/zvector`（`:88-140`，公式 `1.0/1024.0*mod(91+i,1023)-0.5` 与 C 侧同源，`:96`）、`fill_s/d/c/zmatrix`（`:202-328`，`uplo` 参数取 `'F'` 全填充或 `'L'/'U'` 三角、未引用区填 `get_snan()`（`:225`）、`diag='U'` 时对角线填 1.0）。
- 8 个带状矩阵例程：`fill_s/d/c/zbandmatrix`（`:330-492`，值 = 行坐标 `a(ku-ku1+i,j) = ku-ku1+i`，`:349`——与 C 侧"值=存储位置"思路一致）与 `print_s/d/c/zbandmatrix`（`:494-708`）。
- 8 个打印例程：`print_s/d/c/zvector`（`:24-86`）与 `print_s/d/c/zmatrix`（`:142-200`），全用带标号的 `FORMAT` 语句。
- 4 个带状打印里的**计算 goto**：`goto (10,20,30,40,50) k`（`common_func.f:513/567/621/675`）按对角线序号 k 跳到五档递进缩进的 FORMAT（`:540-544`，缩进 2x/10x/18x/26x/34x）——F77 没有动态宽度 FORMAT，只能用多分支+计算 goto 模拟对齐输出，这是全仓库最"古法"的代码。

## 3. 外部连接

每个示例通过 `.fi` include 连接 NVPL 安装的 Fortran 接口声明，构建期再链接 `nvpl::blas_${INT_TYPE}_${THR_TYPE}` imported target。`nvpl_blas/f77/CMakeLists.txt` 与 C 侧同构但有三个 Fortran 特有差异：其一，`file(GLOB)` 后先 `list(REMOVE_ITEM SOURCES ... common_func.f)`（第 4 行），再在 `add_executable(${name} ${src} common_func.f)`（第 8 行）把工具箱**作为第二源文件编进每个目标**——对应 C 侧的 header-only static 方案；其二，ILP64 构建给编译器加 8 字节整数开关：GNU 用 `-fdefault-integer-8`、NVHPC 用 `-i8 -Mlarge_arrays`（第 11-16 行的生成器表达式）——Fortran 侧的 ILP64 是"整型默认宽度全改"，与 C 侧换 `nvpl_int_t` typedef 的路线完全不同；其三，目标命名 `f77_${INT_TYPE}_${THR_TYPE}_${name}`（第 7 行），omp 时链 `OpenMP::OpenMP_Fortran`（第 21-24 行）。README 的运行样例是 `./build/f77/f77_ilp64_omp_icamax`（`nvpl_blas/README.md:37`）。

`service_functions.f` 与 C 侧 `service_functions.c` 演示同一组服务函数的 Fortran 绑定：`nvpl_blas_get_version()`（`service_functions.f:14`）、`nvpl_blas_get_max_threads()`（`:21`）、`nvpl_blas_set_num_threads`（`:27`）、`nvpl_blas_set_num_threads_local`（`:35`，返回旧值便于恢复，`:37-38`）。

## 4. 数据流

`caxpy.f` 展示 Level-1 范本：`parameter` 常量声明（n/incx/incy/alpha，`:16-19`）→ 编译期算出向量尺寸 `xsize=1+(n-1)*abs(incx)`（`:21-22`，与 C 侧 `1+(N-1)*labs(incX)` 同式）→ **`DATA` 语句静态初始化**（`:24-25`，`/(1.0,-3.7,4.3,0.0,5.0)/` 与 `ysize*2.0` 重复因子）→ 隐式 DO 打印（`:38-39`）→ 第 42 行 `call CAXPY(n,alpha,x,incx,y,incy)` → 打结果、`stop`。注意 Level-1 示例用 DATA 字面量而非 `fill_*vector`，后者留给矩阵类示例（`dsyr2.f:40-41` 就是 fill 派）。输出格式全靠句尾 `FORMAT` 标号语句（`caxpy.f:49-53`），`#### args` 参数回显行与 C 侧输出风格对齐。

**组批接口的 `LOC()` 惯用法**是 F77 侧最有技术含量的数据流（`cgemm_batch.f`）：批数据用三维静态数组 `a(rmaxa,cmaxa,maxmat)`（`:35-36`，`maxmat=20` 上限参数 `:14`）；指针数组声明为 `integer*8 a_array(maxmat)`（`:37-38`——即使 LP64 构建，LOC 返回值也按 8 字节存，规避大地址截断）；循环内 `a_array(matidx) = LOC(a(1,1,matidx))`（`:54-56`）取第 matidx 个矩阵首地址；辅助例程用三元组切片 `a(:,:,matidx)` 传参（`:57-62`）；最后 `call CGEMM_BATCH(transa,transb,m,n,k,alpha,a_array,lda,...,grp_cnt,grp_size)`（`:71-72`）。**strided 版**（`dgemm_batch_strided.f`）则完全不需要 LOC——三维数组 `a(lda,k,batch_size)`（`:23-24`）直接传首地址，stride 在 `parameter (stridea=lda*k, ...)` 编译期算好（`:20`），调用 `DGEMM_BATCH_STRIDED(...,stridea,...)`（`:49-50`）。

厂商扩展示例：`daxpby.f` 演示 `DAXPBY(n,alpha,x,incx,beta,y,incy)`（`:42`，双标量缩放相加，BLAS 标准无此例程）；`cgemm3m.f` 演示复数 GEMM 的 Gauss 复杂度削减算法变体（`:31-32` 的文案与 `:46` 的 `call CGEMM3M`），这是 f77 独有示例之一。

## 5. 设计决策

- **工具箱做成独立源文件而非 include**：C 侧用 header-only static（每目标静态拷贝、无链接依赖），F77 侧 `common_func.f` 被显式编进每个可执行目标（CMakeLists 第 4+8 行）。两种方案殊途同归——示例目标自包含、可单独摘抄，代价是每个目标带一份工具代码。
- **NaN 用位构造而非编译器扩展**：`get_dnan/get_snan` 的 `transfer+ibset` 写法（`common_func.f:8-10`）在 gfortran/nvfortran 都成立，比依赖 `-fno-range-check` 或 IEEE_ARITHMETIC 模块更贴近 F77 的可移植底线。
- **`LOC()` 指针传递是组批接口的唯一出路**：F77 没有指针数组类型，BLAS 组批 API（沿用 Intel MKL 的 batch 设计）约定"整型数组装地址"。`integer*8` 承载地址是保守选择；这个惯用法直接来自 Cray/MKL 时代的成熟实践，NVPL 文档也以 LOC() 为标准姿势。
- **固定格式 + 全大写例程名**：刻意保持与数十年遗留代码的字符级兼容——迁移老代码时 diff 噪声最小。续行符混用 `&`/`$`/`*` 也说明这些示例本身脱胎于多代参考实现（`$` 是古老续行符）。
- **ILP64 走编译器全局开关**：Fortran 侧没有 `nvpl_int_t` 这种 typedef 机制，NVPL 选择 `-fdefault-integer-8` 整体切换（CMakeLists 第 13 行），配套库里 INTEGER 亦为 8 字节——因此 Fortran ILP64 程序里所有整型都变宽，连 `common_func.f` 的循环变量也不例外，这是与 C 侧 `_64` 后缀"单点 64 位"截然不同的全局 ABI 世界。
- **文案瑕疵一处（源码为准）**：`dsyr2.f:55` 描述 DSYR2 为 "packed Hermitian rank-2 update"，实际 DSYR2 是**非压缩的实对称** rank-2 更新（packed/Hermitian 是 `dspr2/cher2` 的属性，注释明显从姊妹示例拷贝时未改）。读示例学 API 时以调用行 `:48` 的参数表为准。

## 6. 新人提示

- **上手顺序**：`caxpy.f`（DATA+FORMAT 范本）→ `dgemm.f`（矩阵版，看 fill/print 的 uplo/'F' 惯用法）→ `dgemm_batch_strided.f`（三维数组+编译期 stride，最短批示例）→ `cgemm_batch.f`（LOC() 组批）→ `cgemm3m.f`/`daxpby.f`（扩展 API）→ `common_func.f` 通读一遍（26 个例程的名字与 C 侧 helper 一一对应，`mod(91+i,1023)` 公式两边同源）。
- **构建**：与 C 示例同一工程同一 preset，`cmake --preset ilp64_omp && cmake --build --preset ilp64_omp && ctest`；注意 ILP64 preset 会自动加 `-fdefault-integer-8`，若脱离本工程手编，漏掉该开关会得到静默的错误 ABI 链接（整数宽度不匹配，运行时崩溃或结果错乱）。
- **坑**：①`.fi` 文件在 NVPL 安装包不在本仓库——克隆仓库后直接 `gfortran xxx.f` 会报 include 找不到，须先装 NVPL 或找到安装前缀的 include 路径；②带状打印的 5 档计算 goto 只支持 `k≤5`（即 ku+1≤5），改大带宽示例时输出缩进会失准；③LOC() 返回值必须放 `integer*8`，用默认 integer 在 LP64 下通常侥幸、在超大数组下截断；④`dsyr2.f` 等示例的描述性 FORMAT 文案存在拷贝残留（见上），别把注释当 API 语义；⑤固定格式 72 列截断——抄示例改长表达式时留意第 6 列续行符别丢。
