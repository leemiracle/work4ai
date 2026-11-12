# 05 · nvpl_scalapack：BLACS+ScaLAPACK 分布式线性代数示例

## 1. 角色定位

`nvpl_scalapack/` 是七库中唯一必须 MPI 的示例集：f77 侧 15 文件（4 精度主程序 + 1 公共例程 + 9 个 `.dat`），cxx 侧 2 示例。血统在 README.md:194-197 Acknowledgments 写明：直接取自 Netlib ScaLAPACK 官方示例（Antoine Petitet 1995）。一处甄别：任务描述提到的"舒尔分解"在源码中不存在——`psscaex.f`/`pdscaex.f`/`pcscaex.f`/`pzscaex.f` 与 cxx 例全部做**分布式 LU 求解**（PS/PD/PC/PZGESV，内部即 PxGETRF 主元分解 + PxGETRS 回代），另用 PDGEMM 算残差，以源码为准。

## 2. 内部结构

**公共例程 `pdscaexinfo.f`** 被四精度共享（`f77/CMakeLists.txt:16-18`；`pzscaex.f:68` 也 CALL 它）。进程 0 读 `SCAEX.dat`（`pdscaexinfo.f:45`，含 N/NRHS/NB/NPROW/NPCOL），`NPROCS<1` 时 `BLACS_SETUP` 引导（`:82-85`）；再 `BLACS_GET(-1,0,ICTXT)`+`BLACS_GRIDINIT(ICTXT,'Row-major',1,NPROCS)` 建 1×NPROCS 临时全进程网格（`:90-91`），5 个整数经 `IGEBS2D` 广播、非 0 进程 `IGEBR2D` 接收（`:100/:150`），`BLACS_GRIDEXIT` 拆临时网格（`:159`）。`:161` RETURN 后还挂着 WRITE/ABORT 死代码（`:163-169`）——netlib 原版错误分支挪走后的孤儿语句。

**主程序 `pdscaex.f`**（236 行，四变体逐行同构）：
- NVLP 改造痕迹：`INTGSZ` 按 `#if defined(NVPL_ILP64)` 取 8/4（`:16-20`）；`TOTMEM=2000000` 折算 MEMSIZ（`:21`）；内存从静态大数组改 `ALLOCATABLE`+`ALLOCATE`（`:39/:62`）。
- BLACS 链：`BLACS_PINFO`（`:59`）→`GET/GRIDINIT/GRIDINFO`（`:73-75`）建 NPROW×NPCOL 网格，网外进程退出（`:80-81`）。
- 块循环分布全套样板：`NUMROC` 算 NP/NQ/NQRHS（`:83-85`），`DESCINIT` 建三个 9 元描述符（`:89-94`，索引常量 `:22-26`），在 MEM 里手工切 IPA/IPACPY/IPB/IPX/IPPIV/IPW 指针（`:99-105`）——`LIPIV=ICEIL(INTGSZ*(NP+NB),DBLESZ)`（`:104`）把整型 pivot 按字节折算塞进 double 存储，是榨干工作区的经典习语；内存检查经 `IGSUM2D` 全网格聚合（`:112-125`）。
- 计算验证：`PDLAREAD` 分布式读入（`:129-132`）→`PDLACPY` 备份（`:136-139`）→`PDGESV`（`:167`）→`PDLAPRNT`+`PDLAWRITE` 落盘（`:177-180`）→残差 `||A*X-B||/(||X||·||A||·eps·N)` 阈值 10（`:184-204`）。注意 netlib 原样的命名陷阱：`BNORM` 取自求解后的 IPB（`:186-187`），实为 ||X||；`XNORM` 取自 PDGEMM 输出（`:191-192`），实为 ||AX-B||——名字与语义错位但公式正确。

**`pzscaex.f` 两处钉版笔误**：① `:14` 声明 `CP16SZ`，`:15` 的 PARAMETER 却是 `CPLXSZ=8`——CP16SZ 未赋值即在 `:104`（LIPIV）与 `:114`（内存上报）使用，运行时取未定义值（对照 `pcscaex.f:14-15` 声明赋值一致）；② NPCOL 被全文误改名 `NPZOL`（`:33` 声明、`:68/74/75/80/84/85` 使用），大概是失控的 NPC→NPZ 批量替换，改名一致故功能正常，纯属命名污染。照抄 pzscaex 前先修 ①。

**cxx 侧**：`nvpl_scalapack_example_pdgesv.cpp` 是 F77 例的 C++ 翻译加计时：`Cblacs_pinfo`（`:19`）→`Cblacs_get(ic=-1)`（`:30-32`）→`gridinit('C',2,2)`（`:35-37`，排列参数用 'C' 而 F77 例用 'Row-major'，2×2 下无差异）；`numroc_/descinit_/pdgesv_` 走 Fortran 小写尾下划线符号（`:52/:85/:106`），整数统一 `nvpl_int_t` 适配 lp64/ilp64；计时用 `Cblacs_barrier` 双壁+`clock_gettime`（`:104-108`）；验证段同构但变量命名老实（`:130-139`），残差超阈 `throw`（`:151-153`）。`pdgemm.cpp` 只做 m=n=k=1000、mb=128 的 `pdgemm_` 计时（`:47/:118`），transA/transB 分支决定本地 NUMROC 维度（`:51-70`），无正确性验证。

## 3. 外部连接

顶层 `CMakeLists.txt:50-59` 定五开关：INT_TYPE(lp64/ilp64)、THR_TYPE(seq/omp)、MPI_INTERFACE(openmpi3/4/5、mpich)、MPI_NUMPROC(默认 4)、OMP_NUM_THREADS。f77 例一次链四 target（`f77/CMakeLists.txt:40-46`）：`nvpl::scalapack_${INT_TYPE}`+`nvpl::lapack_${INT_TYPE}_${THR_TYPE}`+`nvpl::blacs_${INT_TYPE}_${MPI_INTERFACE}`+`MPI::MPI_Fortran`——**BLACS 的 MPI 变体烧在库名里**（mpich 变体覆盖全部 MPICH-ABI 兼容发行版，README.md:25；NVHPC+HPC-X 官方指定 openmpi4 接口，README.md:27-30）。ilp64 要源码同步：`-cpp`+`NVPL_ILP64` 宏+`-fdefault-integer-8`/`-i8`（`:48-60`）。数据文件靠 `file(COPY)` 复制到运行目录（`:14`），缺了 CTest 必挂。cxx 侧加 `OMPI_SKIP_MPICXX` 避开 OpenMPI C++ 绑定（`cxx/CMakeLists.txt:20-23`）。CTest 以 `mpiexec` 起 4 进程（`f77/CMakeLists.txt:65-67`）；CMakePresets.json 把全组合做成 preset。

## 4. 数据流

F77 例"文件→分布→算→验证→文件"：`SCAEX.dat`（N=6,NRHS=1,NB=2,NPROW=2,NPCOL=2）由 rank0 读后广播；`?SCAEXMAT.dat`/`?SCAEXRHS.dat` 由 `P?LAREAD` 在 (0,0) 进程读、按块循环描述符分发。`.dat` 格式精度敏感：实数矩阵一行一值（`DSCAEXMAT.dat` 首行 "6 6" 后逐元素、D 记号；单精度 SSCAEXMAT 用 E 记号），**复数矩阵一行实虚成对**（`ZSCAEXMAT.dat:3` 的 `6.0000D+0  4.0000D+0`）。cxx 例不读文件：每进程以 `default_random_engine(mpi_rank)` 种子本地生成随机块（`pdgesv.cpp:62-66`），走备份→求解→残差链，解不落盘只打印时间。

## 5. 设计决策

①**共享 pdscaexinfo.f 而非四份拷贝**——netlib 原版各带一份，NVPL 收敛为单一公共源，四精度行为一致；②**cxx 直接 `pdgesv_` 裸符号**——依赖 nvpl_scalapack.h 的 `nvpl_int_t` 与原型，比手写 BIND(C) 薄得多，示范最省事的 C++ 迁移路径；③**残差判据沿用 netlib 的 `||AX-B||/(||A||·||X||·eps·N)<10`**——分母带 eps 与 N 使阈值与精度、规模无关，F77/cxx 两代判据一致可互为对照；④**`Cblacs_exit(keep_mpi=0)` 注释化教学**（`pdgesv.cpp:17/:163-164`）——0 表示退出时顺手 MPI_Finalize，是 BLACS/MPI 职责边界最易踩的点。

## 6. 新人提示

顺序：README（MPI 配置才是本库新知识）→`cxx/..._pdgesv.cpp`（最短闭环）→`f77/pdscaex.f`→`pzscaex.f`（看笔误）。坑：① `MPI_INTERFACE` 须与实际 `mpiexec` 匹配，Ubuntu 多 MPI 共存记得 `MPI_EXECUTABLE_SUFFIX=.openmpi`（README.md:39），配错的表现是链接通过但 BLACS 挂死；② ilp64 是"三 target+编译旗"四件套联动，只换一个会出现描述符错乱；③ 别照抄 pzscaex 的 CP16SZ/NPZOL；④ F77 例运行目录须有 9 个 `.dat`（CMake 已 COPY 进 build）；⑤ cxx 例硬编码 2×2 且 `mpi_size<4` 即退出（`pdgesv.cpp:22-28`），单进程直跑只得一句 Error；⑥ 要 Schur/特征值类分布式示例，本仓没有——去 Netlib ScaLAPACK examples 找。
