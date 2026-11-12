# CUDA-Fortran-2ed 新人入门（ONBOARDING）

> 基于仓库 knowledge-graph（380 节点/473 边/16 层/16 步导览）与源码逐行核实生成。
> 锚点格式 `路径:行号`，全部从源码核实。仓库 HEAD：2f1cc85。

## 1. 这个仓库是什么

一句话：这是 NVIDIA 出版的《CUDA Fortran for Scientists and Engineers, Best Practices for Efficient CUDA Fortran Programming (Second Edition)》全书配套示例源码，12 章源码按 `code/ch01`–`code/ch12` 逐章组织（README.md:1-6），共 158 个源文件（`.cuf/.f90/.F90/.CUF/.cu/.c`）。

它不是库、不是产品、没有第三方依赖，而是**教学代码仓**，一切设计围绕书的三个教学法：

- **CPU/GPU 成对对照**：新概念先给纯 CPU 版再给 GPU 版。最典型的是 `code/ch01/increment.f90:3`（do 循环版 `subroutine increment`）与 `code/ch01/increment.cuf:3`（`attributes(global) subroutine increment` kernel 版），module 同名、逐行对照。
- **单文件自包含**：绝大多数示例是「module（包装 kernel 提供显式接口）+ program（驱动）」同文件形态，一个文件编译出一个可执行、运行自校验打印 `Program Passed`/`Failed`（increment.cuf:31-35）。全书仅 ch06 有两个多文件链接目标。
- **每章一个主题阶梯**：12 章从起步、调试、度量一路推进到光线追踪综合项目，代码即教材。

预期读者：有 Fortran 基础、刚接触 GPU 的科学家/工程师。正确打开方式是**按章读代码**，不是当 API 库检索。

## 2. 仓库布局

```
CUDA-Fortran-2ed/
├── README.md            # 逐章逐节的总索引（Section 号 → 示例文件）
├── LICENSE.txt          # Apache-2.0（NVIDIA 2024）
└── code/
    ├── ch01/  18 文件   # 起步：设备查询、首核、网格映射、managed、错误处理
    ├── ch02/   6 文件   # 正确性与调试：sanitizer、cuda-gdb、浮点精度
    ├── ch03/   9 文件   # 性能度量：cudaEvent、带宽、NVTX
    ├── ch04/  20 文件   # 同步：原子、共享内存、warp 原语、流异步
    ├── ch05/  17 文件   # 优化：内存层级、合并访存、转置专题、占用率
    ├── ch06/  16 文件   # 移植：!@cuf/#ifdef 渐进 GPU 化、可复用 module 库
    ├── ch07/  17 文件   # 库互操作：cuBLAS/cuSPARSE/cuSOLVER/cuTENSOR/Thrust/CUDA C
    ├── ch08/  12 文件   # 多 GPU：P2P 直访 + MPI/CUDA-aware MPI
    ├── ch09/  13 文件   # 案例：蒙特卡洛与归约算法四方案
    ├── ch10/   7 文件   # 案例：9 点有限差分 stencil
    ├── ch11/   7 文件   # 案例：cuFFT 谱方法（泊松/NS 方程/重叠流水）
    └── ch12/  16 文件   # 综合项目：光线追踪器（全章 Host/CUDA 双编译）
```

全书分两部分：Part 1「CUDA Fortran Programming」（ch1–ch8，README.md:25）讲语言与工具链；Part 2「Case Studies」（ch9–ch12，README.md:256）用四个完整应用收束。

**每章目录完全自包含**：源码 + 一个 Makefile，需要精度开关的章（ch09/ch11）各带一份 `precision_m` 副本，跨章不共享任何文件——这是刻意组织，代价是同名 module 多处出现（见第 6 节消歧）。

后缀约定：`.f90`=纯 CPU Fortran；`.cuf`=CUDA Fortran（自动启用 `-cuda`）；`.F90`=需 C 预处理的 Fortran（大小写敏感，内有 `#ifdef`）；`.CUF` 同 `.cuf` 仅一例（ch09/compute_pi_performance.CUF）；`.cu`=CUDA C（仅 ch07 两个文件）。

## 3. 怎么构建运行

**没有顶层 Makefile**——进入目标章节目录直接 `make`：

```bash
cd code/ch01 && make            # 构建该章全部 18 个可执行
./incrementcuf                  # 运行单个示例，自校验打印 Program Passed
make clean                      # 清理
```

工具链是 **NVIDIA HPC SDK**（前身 PGI，`pgnvfortran` 更名而来；本仓统一写 `nvfortran`，配套 `nvc` 编 C、`nvcc` 编 .cu、MPI 示例用 `mpif90`）。仓库不设变量不查环境，要求 SDK 在 PATH。

各章 Makefile 是「编译开关的活教材」：

| 开关 | 含义 | 代表位置 |
|---|---|---|
| `-cuda` | 把 `.f90/.F90` 当 CUDA Fortran 编（启用 `!@cuf` 与 `_CUDA` 宏） | code/ch01/Makefile:50-51 |
| `-gpu=managed` | 编译器隐式把可分配数组放统一内存 | code/ch01/Makefile:37 |
| `-gpu=cc80` / `cc90` | 锁定 sm80 / sm90 架构目标 | code/ch05/Makefile:72 / code/ch04/Makefile:96 |
| `-gpu=ptxinfo` | 打印 kernel 寄存器/共享内存占用 | code/ch05/Makefile:21 |
| `-gpu=keep` / `fma,keep` | 保留 GPU 中间产物供检视（是否生成 FFMA） | code/ch05/Makefile:82 |
| `-gpu=nordc` | 关闭 RDC（供 cuda-gdb 单步） | code/ch02/Makefile:21 |
| `-cudalib=cublas,cufft,curand,nvtx,...` | 链接对应 CUDA 库 | code/ch07/Makefile:20 |
| `-DDOUBLE` / `-DSINGLE` | 预处理宏切单双精度 | code/ch11/Makefile:10/34 |
| `-Minstrument` | 自动 NVTX 插桩 | code/ch03/Makefile:30 |
| `-Mpreprocess` | 强制 .cuf 走预处理 | code/ch11/Makefile:29 |

两条**硬件门槛**：ch04 的 swap（线程块集群）要求 sm90（code/ch04/Makefile:96），ch05 的 parallelismPipeline 要求 sm80（code/ch05/Makefile:72）——老卡上这两个目标构建失败属预期。

精度双目标惯用法：同一源码出 `_sp`/`_dp` 两个可执行，差异只在 `-DDOUBLE` 一行（code/ch09/Makefile:8-12、code/ch11/Makefile:6-10）；ns2d 则用 `-DSINGLE` 反向切换（code/ch11/Makefile:33-37）。

MPI 线（ch08）：`wallclock.c` 由 `nvc` 编成 .o（code/ch08/Makefile:24-25），MPI 示例用 `mpif90`（code/ch08/Makefile:33-44），运行需 `mpirun -n N`。小勘误：`code/ch08/Makefile~` 是编辑器备份残留，忽略即可。

## 4. 核心概念地图（按 16 层看主题演进）

图谱 16 层大致一章一层、ch04/ch05 各拆两层，串起来正是全书的难度阶梯：

**地基（L01–L02）**：12 个 Makefile + README 构成构建基建；跨章同名支撑模块（precision_m 家族与 rgb_m）单拎一层消歧——「各章自带副本」是新人第一困惑点。

**起步三连（L03–L05，ch1–ch3）**：ch1 建立全书基线——deviceQuery 摸清设备（code/ch01/deviceQuery.cuf:10,27）；increment 对照组走完「device 数组 + `a_d=a` 拷贝 + `<<<1,n>>>` 启动 + `a=a_d` 拷回」完整回路（code/ch01/increment.cuf:27-29）；managed 系列给出统一内存三条路径（显式 `integer, managed`（code/ch01/managed.cuf:22）、`-gpu=managed` 隐式、`!@cuf` 条件注释单源双编译（code/ch01/managedCUF2.f90:2,11））。ch2 教「写错了怎么办」：memcheck 故意写 `a(0)` 越界供 compute-sanitizer 抓，accuracy 展示百万 float32 求和顺序的舍入差异。ch3 教度量：cudaEvent 生命周期、有效/峰值带宽、limitingFactor 判定计算还是带宽受限、NVTX 四级标注。

**线程模型与流（L06–L07，ch04 上下两半）**：上半是并行原语谱系——raceAndAtomic 对照竞态与 atomicAdd、sharedExample 三种共享内存形态、`__shfl_xor` 蝶形归约（code/ch04/shfl.cuf:15）、ballot 位掩码、threadfence 内存序，直到 smooth 的 `attributes(grid_global)` 全网格同步与 swap 的 sm90 线程块集群 `cluster_dims(2,1,1)`+`cluster_map_shared_rank` 跨块共享内存直访（code/ch04/swap.cuf:6,29）。下半是流异步——空流/阻塞流语义、event 跨流依赖，pipeline 拼出 pinned+多流软件流水线。

**内存与访存优化（L08–L09，ch5 上下两半）**：上半讲资源占用决定 occupancy——constant 广播缓存、local 内存触发实测、launch_bounds 引发 spill、超 48KB 共享内存 opt-in、`__ldcg/__ldcv` 显式 load 语义。下半是全仓最精彩的性能实验区：transpose.cuf 六 kernel 走完经典优化阶梯——基准 copy/copySharedMem（code/ch05/transpose.cuf:9,26）、naive 写不合并（:53）、coalesced 双端合并（:75）、加一列消 bank 冲突（:105）、对角重排（:135）；stride/offset 扫描非合并塌陷曲线；HDtransfer/async 对比 pinned 带宽与最优流数。

**移植方法论（L10，ch6）**：面向存量 Fortran 代码——porting 系列从纯 CPU 基线出发，经 managed、`!@cuf` 哨兵注释、`#ifdef _CUDA` 预处理多路径保持**单源双跑**；laplace 系列落到 4096² Jacobi 迭代（code/ch06/laplace2D.f90:3）；compact_m 把块内+跨块扫描封装成 6 类型泛型 module 库（code/ch06/compact_m.cuf:9-12）。

**生态与扩展（L11–L12，ch7–ch8）**：ch7 不再手写 kernel——callingC 用 `bind(C,name='Ckernel')` 绑 CUDA C 符号（code/ch07/callingC.cuf:5），`nvcc -rdc=true` 编 .cu 供 Fortran 调（code/ch07/Makefile:12）；cuBLAS 新旧 API 与 TF32 横评、cusparseEx 把 13 参 API 压成 3–5 参简式（code/ch07/cusparseEx.cuf:4-17）、Thrust 排序包装成 Fortran 泛型。ch8 走多卡——P2P 直访矩阵/带宽、无 MPI 的 transposeP2P 流水线、mpiDeviceUtil.assignDevice 用 `MPI_Comm_split_type` 切子通信机让每个 rank 绑一块卡（code/ch08/mpiDeviceUtil.cuf:14-17）、transposeCAMPI 展示 CUDA-aware MPI 直搬设备缓冲。

**应用案例（L13–L15，ch9–ch11）**：ch9 归约专题——求 pi 用四方案实现（shared 树形双核、warp shuffle、atomicCAS 自旋锁、`attributes(grid_global)` 单核网格同步（code/ch09/pi_gridGroup.cuf:3）），compute_pi_performance.CUF 统一横评，收尾欧式期权定价。ch10 把 9 点 stencil 做成 8 kernel 变体模块（sPencils/lPencils 两种 tile 形态，code/ch10/derivative_m.cuf:19-20），解析解验证+有效带宽换算。ch11 谱方法——poisson 频域解泊松、ns2d 以 4 级 RK 推进 2D Navier-Stokes（cuFFT 类型全靠宏切换，code/ch11/ns2d.cuf:6-17）、exampleOverlapFFT 多流重叠 H2D/FFT/IFFT/D2H。

**综合收官（L16，ch12）**：光线追踪器总复习全书技法——ray/sphere/triangle 求交、四种材质、相机景深、程序纹理（texture.F90 全章最长 870 行），全部 Host/CUDA 双编译，rgb_m 的全套运算符重载与 cuRAND 采样撑起渐进移植+模块复用闭环。

## 5. 关键文件 TOP10

| # | 文件 | 一句话 |
|---|---|---|
| 1 | `README.md` | 全书总索引：Section 号→示例文件映射，读任何示例前先来这里定位书中章节 |
| 2 | `code/ch01/increment.cuf` | 全仓 hello-world：36 行走完 module 包装 kernel→device 数组→拷贝→启动→校验全回路 |
| 3 | `code/ch01/managed.cuf` | 统一内存最省事写法：`integer, managed` 免显式拷贝（:22），dim3 二维网格启动（:33） |
| 4 | `code/ch04/sharedExample.cuf` | 共享内存三形态对照（静态/动态/自动推定），理解 shared 的第一站 |
| 5 | `code/ch05/transpose.cuf` | 转置优化四台阶教科书（naive→coalesced→消 bank 冲突→对角），CUDA 访存优化微缩史 |
| 6 | `code/ch06/compact_m.cuf` | 流压缩 module 库（383 行）：块内+跨块扫描封装成 6 类型泛型接口，复用性标杆 |
| 7 | `code/ch07/cusparseEx.cuf` | 把冗长 CUDA 库 API 封装成 Fortran 简式接口的工程手法（134 行） |
| 8 | `code/ch08/mpiDeviceUtil.cuf` | MPI rank 绑卡的标准答案：19 行解决同节点多进程分卡 |
| 9 | `code/ch09/compute_pi_performance.CUF` | 五种归约实现同台横评，检验 ch4 全部原语的理解 |
| 10 | `code/ch12/rgb_m.F90` | Host/CUDA 双编译模块的机制核心：`#ifdef _CUDA` 切换模块名+`!@cuf` 注入 device 属性 |

辅助但常被查的：`code/ch01/deviceQuery.cuf`（环境自检第一步）、`code/ch11/ns2d.cuf`（最大应用文件）、`code/ch06/laplace2D.f90`（移植案例 CPU 基线）。

## 6. 同名 module 消歧（新人最易踩的坑）

各章自包含的直接后果：**同一个 module 名在全仓多处定义，行为还不一样**。用 `use precision_m` 前必须确认你链接的是哪一份。

**precision_m：4 个目录、5 个文件、3 种形态。**

| 文件 | 默认 fp_kind | 切换方式 |
|---|---|---|
| `code/ch01/precision_m.cuf` | real64（:3） | 不可切，纯演示 |
| `code/ch01/precision2_m.cuf` | real32（:7） | `#ifdef DOUBLE` 切 real64（:4）——**module 名也叫 precision_m**，只是文件名不同 |
| `code/ch09/precision_m.F90` | real32（:10） | `#ifdef DOUBLE` 切 real64（:7），另带 singlePrecision/doublePrecision 别名参数 |
| `code/ch10/precision_m.cuf` | real32（:3） | 不可切，固定单精度 |
| `code/ch11/precision_m.F90` | real32（:7） | `#ifdef DOUBLE` 切 real64（:4） |

陷阱场景：把 ch11 示例拷到 ch10 目录编译，会静默链上「不可切」的 ch10 版，`-DDOUBLE` 完全失效且**不报错**。同理 ch01 里 precision_m.cuf 与 precision2_m.cuf 同名，后编的 .mod 覆盖先编的。规则：**永远用所在章自带的那份，跨章搬代码连 precision_m 一起搬**。

**rgb_m：一文件两模块，宏二选一。** `code/ch12/rgb_m.F90:1-6` 用 `#ifdef _CUDA` 把同一源码编成两个不同名模块——`-cuda` 编译时是 `rgbCUDA`，纯宿主编译时是 `rgbHost`。ch12/Makefile 对应产出 `rgb_m.cuda.o`（:33-34）与 `rgb_m.host.o`（:30-31），rayHost 链 host 版、rayCUDA 链 cuda 版（:38-42）。所以 ch12 示例里看到的是 `use rgbCUDA`/`use rgbHost` 而非 `use rgb_m`——不是笔误，是与编译开关联动的机制。ch12 所有 `.F90` 示例同理靠 `_CUDA` 宏与 `!@cuf` 单源双跑。

**其余撞名**：`code/ch06/compact_m.cuf` 与 `compactOpt_m.cuf` 是**同名 module `compact` 的两套实现**（后者为优化版），同一 testCompact.cuf 驱动分别链接对照；ch02 的 debug/memcheck/initcheck 三文件各带一份同源 `module m`（仅 memcheck 埋了越界 bug）；`multidim.cuf` 在 ch01 与 ch03 各有一份（前者讲网格映射、后者当计时机）。**判断原则：module 的真实身份由「编译它所在的那份文件」决定，同名不同目录=不同实现。**

## 7. 常见任务切入点

「我想看 X 主题的示例」速查（章节目录即主题索引）：

| 你想做的事 | 去哪 | 关键文件 |
|---|---|---|
| 摸清本机 GPU 能力/算力 | ch01 | deviceQuery.cuf、version.cuf（:5-8 打印驱动与运行时版本） |
| 写第一个 kernel | ch01 | increment.cuf → multiblock.cuf → multidim.cuf |
| 免拷贝/统一内存 | ch01 | managed.cuf、managedImplicit.cuf（配 `-gpu=managed`） |
| 单源同时出 CPU/GPU 版 | ch06 | managedCUF2.f90（ch01）、portingManagedSent.F90、laplace2DAssoc.f90 |
| 调 kernel（越界/未初始化/单步） | ch02 | memcheck.cuf、initcheck.cuf、debug.cuf+`compute-sanitizer`/`cuda-gdb` |
| 计时、算带宽、打时间线标注 | ch03 | events.cuf、effectiveBandwidth.cuf、nvtxBasic.cuf |
| 共享内存 / 原子 / warp 原语 | ch04 | sharedExample.cuf、raceAndAtomic.cuf、shfl.cuf |
| 多流异步、重叠传输与计算 | ch04 | pipeline.cuf、eventSync.cuf、twoKernels.cuf |
| 占用率、寄存器、local 内存 | ch05 | parallelism.cuf、spill.cuf、local.cuf（配 `-gpu=ptxinfo`） |
| 合并访存/转置优化 | ch05 | transpose.cuf、stride.cuf、offset.cuf |
| 调 cuBLAS/cuSPARSE/cuSOLVER/cuTENSOR | ch07 | sgemmNew.cuf、cusparseMV.cuf（全参版）→cusparseMV_Ex.cuf（简式） |
| Fortran 调 CUDA C/C++ | ch07 | callingC.cuf+c.cu、thrust.cuf+thrust.cu |
| 多卡 P2P 直传 | ch08 | p2pAccess.cuf、directTransfer.cuf、transposeP2P.cuf |
| 多卡 MPI（含 CUDA-aware） | ch08 | mpiDeviceUtil.cuf、transposeCAMPI.cuf |
| 随机数/蒙特卡洛/归约 | ch09 | generate_randomnumbers.cuf、pi_*.cuf 四方案、montecarlo_european_option.cuf |
| stencil/有限差分 | ch10 | derivative_m.cuf、finiteDifference.cuf |
| FFT/谱方法求解 PDE | ch11 | fft_test_c2c.cuf、poisson.cuf、ns2d.cuf |
| 综合大项目练手 | ch12 | ray.F90 起步 → texture.F90（870 行）收官 |

反过来，「按书中章节号找文件」走 README.md——每章条目下 `Section N.N.N: 文件名` 精确对应书中段落。

## 8. 进一步阅读与已知勘误

**主线读物**是书本身：《CUDA Fortran for Scientists and Engineers: Best Practices for Efficient CUDA Fortran Programming, Second Edition》（NVIDIA Press，Ruetsch / Domeika）。示例与书中小节号一一对应，对照阅读效果最佳；仓内只有代码与注释，没有书文。

**仓内导航**：README.md 是唯一总索引；各章 Makefile 内的 `# section N.N` 注释（如 code/ch01/Makefile:8）是第二层目录，可反查每个目标的书中出处。

**外部文档**：NVIDIA HPC SDK 的 nvfortran 手册（CUDA Fortran 语言参考与 `-gpu`/`-cudalib` 选项）、CUDA Toolkit 的 compute-sanitizer/nsys/cuda-gdb 指南、cuBLAS/cuSPARSE/cuSOLVER/cuTENSOR/cuFFT/cuRAND 各库 API 手册。

**README.md 实测勘误**（按图索骥时别被误导）：

- README.md:49 写 `asynError.cuf`，实际文件名 `asyncError.cuf`；
- README.md:155 写 `stide.cuf`，实际 `stride.cuf`；
- README.md:188 写 `portindDevice.cuf`，实际 `portingDevice.cuf`；
- README.md:268 写 `pi_performance.CUF`，实际文件 `compute_pi_performance.CUF`（`pi_performance_sp` 只是 Makefile 目标名，code/ch09/Makefile:31）；
- README.md:276 写 `accuracy_sum.cuf`，实际是纯宿主文件 `accuracy_sum.f90`；
- README.md:304 写 `exampleOverlapFFT.cuf`，实际文件 `exampleOverlapFFT_nvtx.cuf`（code/ch11/Makefile:28）。

**上手 30 分钟路线**：`make` ch01 → 跑 deviceQuery 确认环境 → diff increment.f90 与 increment.cuf 体会最小改动 → 读 managed.cuf 与 managedCUF2.f90 理解「要不要显式管拷贝」的三档选择 → 跳 ch05/transpose.cuf 看性能阶梯。之后按第 7 节表格按需跳章——本仓章节间耦合度低，任意切入都成立。

---

*生成于 understand-anything 流水线 onboarding 阶段；行号锚基于 commit 2f1cc85 全量核实。*



