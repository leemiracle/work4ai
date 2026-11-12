# NVPL LAPACK 双接口示例（nvpl_lapack/cpp 与 nvpl_lapack/f77）

## 1. 角色定位

`nvpl_lapack` 是 NVPL LAPACK 的示例工程，分 `cpp/`（68 个目录项：66 个 `.cpp` 含 `utils.cpp`、加 `utils.h` 与 CMakeLists）与 `f77/`（24 个目录项：23 个 `.f` 含 `common_func.f`、加 CMakeLists）。它要回答的问题是：**同一个 LAPACK 计算，用户可能从三种入口进来**——LAPACKE 高层 C 接口（`LAPACKE_dgesv`）、Fortran 风格的 C 绑定（`NVPL_LAPACK_dgesv`，全参数指针）、以及原生 Fortran 调用（`call dgesv(...)`）。示例矩阵刻意对称覆盖五种核心例程族（gesv 线性方程组、gels 最小二乘、posv 对称正定、syev/heev 特征值、getrf LU 分解）× 四精度，再叠加厂商扩展（nopivot、batched）与 ILP64/线程控制专题。与 BLAS 示例相比，它的组织重心从"API 全覆盖"转向"接口风格对照"。

## 2. 内部结构

**cpp 侧三档接口分层**。第一档是 20 个原生 Fortran 风格示例（`ex_dgesv.cpp` 等）：核心一行是 `NVPL_LAPACK_dgesv(&n, &nrhs, A, &lda, ipiv, b, &ldb, &info)`（`ex_dgesv.cpp:40`）——与 Fortran ABI 同构，**所有标量都取地址**、矩阵列主序（数据按列初始化，`:18` 注释）、`info` 出参在最后。第二档是 40 个 LAPACKE 示例（5 例程族 × 4 精度 × col/row-major 各一）：`LAPACKE_dgesv(LAPACK_ROW_MAJOR, n, nrhs, A, lda, ipiv, b, ldb)`（`ex_lapacke_dgesv_rowmajor.cpp:39`）——矩阵布局做成首参数、**标量全部传值**、无 `info` 指针（返回值即 info）、work 数组完全隐藏，row-major 版由库内部转置，代价显式化为 `LAPACK_WORK_MEMORY_ERROR/LAPACK_TRANSPOSE_MEMORY_ERROR` 两个可检错误（`:42-45`）。第三档是专题示例：`ex_lapacke_64.cpp`（ILP64 显式入口 `LAPACKE_dgels_64`，`:48-49`，尺寸参数全 `nvpl_int64_t`，`:13-17`，注释明确"从 LP64 与 ILP64 两种库都导出"，`:3-4`）、`ex_lapacke_compat.cpp`（`#include <lapacke.h>` 原样编译，`:7`，注释说明 NVPL 提供 `lapacke.h` 兼容头转发到自家 API，`:3-6`——Netlib 存量代码零改动迁移）、`ex_batched_getrf.cpp`（OpenMP `parallel for` 循环（第 26 行）里直接调 **F77 重整名符号** `dgetrf_(&m, &n, ...)`，第 29-30 行，注释点明"并行区内内部线程数限制为 1"，第 28 行）、`ex_thread_control.cpp`（`nvpl_lapack_get_max_threads()` `:50`、`nvpl_lapack_set_num_threads(7)` `:54`、`omp_set_max_active_levels(2)` `:61`；文件头还有一段 `__attribute__((noinline))` 包装 `slarfg` 的"NVHPC 编译器 bug workaround"，`:12-16`）。

**utils 模板打印体系**（`utils.h` 31 行声明 + `utils.cpp` 137 行实现）：核心是四个函数模板——`print_element<T>` 主模板 + 三个全特化（实型 `%6.2f` `utils.cpp:14-17`、复型 `%6.2f + %6.2fj` `:19-31`、整型用 `NVPL_LAPACK_IFMT` 宏 `:33-36`）、`print_matrix_rowmajor_impl`（`i * ldn + j` 索引，`:45-49`）与 `print_matrix_colmajor_impl`（`i + j * ldm` 索引，`:59-63`）、`print_vector_impl`（`:67-74`）；外面用 `extern "C"` 包 13 个具名包装函数（`:76-136`，头文件 `utils.h:6-30` 对应声明）供各示例当 C 函数调。两处源码甄别：其一，`utils.cpp:6-12` 定义了 `is_element_complex` 类型 trait（主模板 false + 两个复数特化 true），但**全文件乃至全目录零引用**——打印分派实际由 `print_element` 特化完成，这个 trait 是死代码；其二，批分析曾记"utils.h UNTILS 拼写笔误"，实际核实该笔误在**另一个库**的头文件 `nvpl_fft/cxx/utils.h:1-2`（include guard 写作 `NVPLFFT_EXAMPLE_UNTILS_H_`），nvpl_lapack 的 utils.h 并无此问题——引用甄别事实前须核对的活例子。

**f77 侧**（22 个示例 + `common_func.f`）：与 BLAS f77 的固定格式截然相反，这里是**自由格式现代 Fortran**——程序统一叫 `program usageexample`（`ex_dgesv.f:1`、`ex_dsyev.f:1`），用 `allocatable` 动态数组（`ex_dgesv.f:3-5`）与 `reshape` 初始化（`:29-32`）、接口声明只靠一行 `external dgesv`（`:6`），没有 `.fi` include。`common_func.f`（147 行、9 个例程）延续"看起来像固定格式"的缩进风格但按自由格式编译：`print_s/d/c/zmatrix`（`f77/common_func.f:1/17/33/49`）、`print_s/d/c/zvector`（`:65/82/99/116`）、外加 `print_ivector`（`:133`，LAPACK 特有——打印 ipiv 之类整型向量）。

## 3. 外部连接

两侧都通过 `nvpl::lapack_${INT_TYPE}_${THR_TYPE}` imported target 链接（四个变体 `lp64/ilp64 × seq/omp`），cpp 侧统一 `#include <nvpl_lapack.h>`（`ex_dgesv.cpp:2`），compat 示例改包 `lapacke.h`。构建编排的差异是本仓最大特色：**cpp/CMakeLists.txt 用宏展开扇出**——`addCXXExample(name)` 一次生成 4 个目标 `ex_cpp_<name>_{ilp64,lp64}_{seq,omp}`（第 5-25 行），`addCXXOMPExample` 生成 2 个 omp 目标（第 28-39 行）；62 个 `addCXXExample` + 3 个 `addCXXOMPExample` 对应 65 个示例程序（20 原生 + 40 LAPACKE + compat + lapacke_64 + 3 OMP 专题）。**f77/CMakeLists.txt 同样宏扇出**且按编译器分支设定标志：GNU 用 `-fdefault-integer-8` + `-ffree-form`、NVHPC 用 `-i8` + `-Mfree`（第 6-19 行），全部 22 个示例各出 4 个目标 `ex_f77_<name>_{ilp64,lp64}_{seq,omp}`（宏第 22-50 行）——注意顶层 `CMakeLists.txt` 对 OpenMP 是无条件 `find_package(OpenMP REQUIRED COMPONENTS CXX Fortran)`，比 BLAS 工程的条件式更硬。README 给的运行样例 `./build/default/ex_lapacke_dgels_colmajor_ilp64_seq` 与 `OMP_NUM_THREADS=8 ..._lp64_omp`（`nvpl_lapack/README.md:41-46`）。f77 示例还能反向调用服务函数：`ex_potrf.f:5` 声明 `external nvpl_lapack_set_num_threads`、`:31` 直接 `call nvpl_lapack_set_num_threads(nt)`。

## 4. 数据流

**LAPACKE 高层路径**（`ex_lapacke_dgesv_rowmajor.cpp`）：栈数组按行主序初始化（`:18`，注意 `ldb = nrhs` 而非 n，`:11`——行主序下 b 的 leading dimension 是列数）→ `print_dmatrix_rowmajor` → 一行 `LAPACKE_dgesv(LAPACK_ROW_MAJOR, ...)` 传值调用（`:38-39`）→ 返回值即 info，分支处理内存类错误 → 原位输出：b 变解、A 变 LU 因子、ipiv 是置换索引（`:54-62` 打印三样）。work 数组的分配/释放完全在库内发生，用户数据流里看不到。

**Fortran 风格路径**（f77 `ex_dsyev.f`）演示了 LAPACKE 替你做掉的那件事——**`lwork = -1` 两段式 workspace 查询**：`lwork = -1 ! Workspace query`（`ex_dsyev.f:14`）→ 先 `allocate(work(1))` 用占位长度调一次 `call dsyev('V','L',n,a,lda,w,work,lwork,info)`（`:38-39`）→ 库把最优长度写进 `work(1)`，`lwork = int(work(1))` 读回（`:40`）→ 释放占位、按最优长度重分配 `allocate(work(lwork))`（`:44`）→ 第二次真算（`:47`）。这是 Fortran LAPACK 四十年不变的空间协商协议：不查也能跑（lwork 给个保守值），查了才能拿到库针对当前硬件选的最优缓冲。`ex_dgesv.f` 则是无 workspace 例程的对照（dgesv 无 work 参数，`:50` 一步直调）。

**厂商扩展路径**：`ex_getrf_nopivot.f` 用 `integer, pointer :: ipiv => null()`（`:4`）构造空指针，`call sgetrf(m, n, a, lda, ipiv, info)`（`:28`）传 null 进去即触发无主元 LU——注释明示这是 NVPL 扩展语义（`:27`）；数据用 `random_number` 生成并对角加强保证非奇异（`:18-20`）。`ex_batched_getrf.cpp` 则是"用户侧批处理"范式：128 个 512×512 矩阵连续存放，`matrices.data() + batch_id * m * n` 指针偏移切批（`:29`），OpenMP 并行区外层并行、内层库线程收缩为 1 的嵌套模型。

## 5. 设计决策

- **双接口并陈而非二选一**：LAPACKE 高层接口（传值、布局参数、隐藏 work）适合新写 C/C++ 代码；`NVPL_LAPACK_*` 指针风格保 Fortran ABI 兼容，适合从 Fortran 代码直译或追求零开销（不经 LAPACKE 的内部转置/拷贝）。40 个 col/row-major 成对示例把"行主序支持是 LAPACKE 层功能而非核心库功能"这一事实摆到明面。
- **`_64` 入口同时从两库导出**（`ex_lapacke_64.cpp:3-4`）：与 BLAS 的 `cblas_dgemm_64` 同一设计哲学——单点 64 位免全局 ABI 迁移；打印辅助吃 `nvpl_int_t`，示例里显式收窄（`:38-41`），与 BLAS `dgemm_64.c:47-51` 的处理如出一辙。
- **打印体系用模板而非 s/d/c/z 四份手写**：LAPACK 示例只需打印（无填充需求，数据都是手写小矩阵字面量），一个 `print_element<T>` 特化点就把四精度+整型收进 137 行；对比 BLAS 的 16 个 fill + 16 个 print 手写族，工程取向随需求复杂度而变。`is_element_complex` 死代码大概率是模板重构的遗迹——曾计划用 trait 分派、后改走函数特化，trait 忘了删。
- **f77 侧改用自由格式+allocatable**：与 BLAS f77 的 FIXED+DATA+LOC 古法刻意分层——BLAS 示例面向"遗留代码原样迁移"，LAPACK 示例面向"现代 Fortran 新代码"；`ex_dsyev.f` 的 allocatable 两段式正是两风格叠加处的标准写法。
- **宏扇出四变体**：每个示例源码不写死 ABI，由 CMake 宏同一份源码生成 lp64/ilp64 × seq/omp 四目标，目标名即变体自述（`ex_cpp_dgesv_ilp64_omp`）——示例即 ABI 矩阵的活文档。

## 6. 新人提示

- **上手顺序**：`ex_dgesv.cpp`（Fortran 风格 C 调用，最短）→ `ex_lapacke_dgesv_colmajor.cpp` 与 `ex_lapacke_dgesv_rowmajor.cpp` 对照读（同一矩阵两种初始化与 ldb 语义）→ f77 `ex_dgesv.f` → `ex_dsyev.f`（lwork 两段式，LAPACK 必学协议）→ `ex_lapacke_64.cpp` / `ex_lapacke_compat.cpp`（ABI 专题）→ `ex_getrf_nopivot.f` / `ex_batched_getrf.cpp`（扩展与并行模型）→ `utils.cpp` 收尾看模板打印。
- **构建**：`cmake --preset default -Dnvpl_ROOT=$PATH_TO_NVPL_INSTALLATION && cmake --build --preset default -j`，ctest 全跑（README:13-15、30-35）。
- **坑**：①row-major 的 LAPACKE 示例里 `ldb = nrhs`（`ex_lapacke_dgesv_rowmajor.cpp:11`），抄到列主序代码会把 b 的尺寸搞错——layout 改了 ld 语义就变；②`NVPL_LAPACK_*` 风格忘取地址（传值给 `nvpl_int_t*` 形参）在 C++ 里能编译过（指针当整数），运行才炸，务必对照 `ex_dgesv.cpp:40` 的全 `&` 写法；③f77 侧脱离本工程手编时，ILP64 要加 `-fdefault-integer-8`（GNU）或 `-i8`（NVHPC），自由格式标志也要带上（f77/CMakeLists.txt 第 7-17 行的清单）；④`ex_getrf_nopivot.f` 的对角加强 `a(i,i) += m*2.0` 不是装饰——无主元 LU 不做行交换，对角不占优会数值爆炸；⑤批处理示例的"并行区内部线程=1"是 NVPL 嵌套并行默认契约，想改用 `nvpl_lapack_set_num_threads_local`（见 `ex_thread_control.cpp`）而非在并行区里改全局设置。
- 勘误一则：如需引用"UNTILS 笔误"，正确位置是 `nvpl_fft/cxx/utils.h:1-2`（本库 utils.h 无此问题）；`is_element_complex` 死代码则确在 `nvpl_lapack/cpp/utils.cpp:6-12`。
