# 精讲：lib_eigsolve 求解流水 —— 四阶段广义特征值求解器（实/复双线）

> 锚基线：仓库 @7c6d9f64；行号引自 lib_eigsolve/*.F90，全部经源码核实。

## 1. 角色定位

求解器库的主干：两个顶层入口 `dsygvdx_gpu`（实对称，`lib_eigsolve/dsygvdx_gpu.F90:71`）与 `zhegvdx_gpu`（复 Hermitian，`lib_eigsolve/zhegvdx_gpu.F90:75`）各串起"Cholesky → 广义归约 → 标准求解 → 三角回解"四阶段，对标 LAPACK `DSYGVX/ZHEGVX` 的 `ITYPE=1, JOBZ='V', RANGE='I', UPLO='U'` 单一配置（README `README.md:19`）。README 对 MAGMA 的差异化主张——"less dependencies on CPU computation"（`README.md:6`）——落在这条流水上：CPU 侧仅剩 `dstedc/zstedc` 一个调用点。

## 2. 内部结构

以实数版为主线（复数版逐行同构）：

- **入口与工作区契约**（`dsygvdx_gpu.F90:96-113`）：五参数组工作区（device `work`、host pinned `work_h/iwork_h/Z_h/w_h`）先过尺寸预检——`lwork ≥ 2*64*64+66*N`、`lwork_h ≥ 1+6N+2N²`；注意 `liwork_h` 实检 `< N` 而报错文案写 "3+5*N"（L109-110，预检与文案不一致）。
- **阶段 1 Cholesky**（L121）：`cusolverDnDpotrf` 上三角分解 B；失败即置 info=-1 返回。
- **暂存下三角**（L131-138）：CUF kernel `!$cuf kernel do(2)` 把 A 的严格下三角拷进 Z——因为阶段 3 会摧毁 A 上三角，而 dsyevd 结束时要靠 Z 还原 A 的完整对称形（`dsyevd_gpu.F90:87` 注释自曝 "works if called from zhegvd only!"）。
- **阶段 2 归约**（L144）：`dsygst_gpu(1,'U',N,A,B,nb=448)`（`dsygst_gpu.F90:31`）分块两角法。每块先用 CUF kernel 镜像补满子块（L57-64，BLAS 三角解需要满阵），对角块两侧 `cublasDtrsm`（左 OP_T/右 OP_N，L67-70），尾块 `Dgemm(∓0.5)×2 + Dsyr2k` 完成对称秩 2 更新（L82-90）——±half 的两次 gemm 正是把对称化的工作量拆给非对称 gemm 的教科书写法。
- **阶段 3 标准求解**（L149）：`dsyevd_gpu('V','U',il,iu,...)`（`dsyevd_gpu.F90:32`）内部又是三步——`dsytrd_gpu` 三对角化（nb1=32，L80）→ 对角/次对角拷回 host 调 **CPU `dstedc('I')`**（L99，特征系在 CPU 算）→ 特征向量回 GPU 后 nb2=64 分块循环 `dlarft_gpu+dlarfb_gpu` 正交回乘（L119-128，DORMTR 的手写内联）。
- **阶段 4 回解**（L155）：`cublasDtrsm` 左乘 U^{-T} 把标准问题特征向量还原为广义特征向量；`not(skip_host_copy)` 时 `cudaMemcpy2D` 回 host（L159-166）。

复数版（`zhegvdx_gpu.F90:75-182`）的差异清单：`Zpotrf/Ztrsm`；`zhegst` 里 Dtrsm 左侧换 `OP_C` 共轭转置、尾块 `Zgemm+Zher2k(OP_C)`（`zhegst_gpu.F90:68/87/95`）；`zheevd` 调 `zstedc` 且实工作区独立成 rwork（`zheevd_gpu.F90:101`）；工作区预检五连（`zhegvdx_gpu.F90:104-127`）中 lwork_h/liwork_h 同样存在阈值与文案不一致。

## 3. 外部连接

模块 `use` 依赖（scanner 解析不到，图谱 28 条 imports 边手扫核实）：两个入口都 `use eigsolve_vars/nvtx_inters/gst/evd` 四模块；`dsyevd_gpu use dsytrd_gpu`（`dsyevd_gpu.F90:34`）；`dsygst/dsytrd use eigsolve_vars`（stream/event/handle 全局上下文）。tested_by 边指向 test_driver 双程序（`test_driver/test_dsygvdx.F90:315` 的调用点）；README documents 边（`README.md:22` 点名两入口文件）；lib Makefile configures 全部 13 个 .F90（`lib_eigsolve/Makefile:13` 的 OBJS 清单）。外部库依赖：cuSOLVER（potrf）、cuBLAS（trsm/gemm/syrk/syr2k/her2k）、CPU LAPACK（dstedc/zstedc）、可选 NVTX。

## 4. 数据流

设备/主机双轨：A、B、Z、w、work 在 device；work_h/iwork_h/Z_h/w_h 为 pinned host。A 的生命周期最有信息量——上三角输入 → 暂存下三角到 Z（入口）→ gst 摧毁上三角改写为标准问题矩阵 → trd 再摧毁成反射器+对角 → evd 从 Z 还原下三角（dsyevd L87-95）→ 回乘后 A 作废，结果在 Z/w。B 被原地覆盖为 Cholesky 因子 U（`dsygvdx_gpu.F90:57` 的 docstring 明示）。双 stream 流水：gst 与 evd 的"构造 T（stream1）/应用 T（stream2）"靠 event1/event2 交替（`dsygst_gpu.F90:48`、`dsyevd_gpu.F90:164`），让相邻块的 GPU 工作重叠。

## 5. 设计决策

- **CPU 只留 stedc**：三对角特征系这一步在 2016 年的 GPU 栈上没有好选择，干脆留给 LAPACK；其余全部 GPU 化——这就是"对 CPU 依赖更少"的可量化含义。
- **单一配置零分支**：uplo/itype 只支持一种，非法输入直接打印返回（`dsygst_gpu.F90:43`）——PoC 的自觉，换来无分支热路径。
- **nb=448（gst）/nb1=32（trd）/nb2=64（回乘）三组块大小各自硬编码**：分别匹配 trsm 吞吐、反射器生成粒度、回乘 gemm 效率——读代码时别找一个"统一的 NB"。
- **暂存-还原配对**（Z 存下三角 → evd 还原）是隐式跨阶段契约，只写在注释里，接口上不可见——重构时最易踩的暗雷。
- 预检阈值从宽（N）但文案照抄 LAPACK 需求（3+5N）：预检实际防的是"完全不够用"，不是精确契约。

## 6. 新人提示

入门顺序：先 `dsygvdx_gpu.F90`（170 行）把四阶段串起来，再下钻 `dsygst_gpu.F90`（100 行，最短）体会分块两角法，最后攻 `dsyevd_gpu.F90`+`dsytrd_gpu.F90`。读复数版时开实数版对照（diff 式阅读），复数语义差异集中在 OP_C 与共轭项。验证自己理解：跑 `test_driver`（四路对比）+ 开 `-DUSE_NVTX` 用 nsight 看 potrf/gst/evd/trsm 分段占比。改动前重读 ONBOARDING 第 7 节坑清单——尤其"Z 按 lda 声明"（`dsyevd_gpu.F90:47`）意味着外部直调 dsyevd_gpu 且 ldz≠lda 会静默越界。

*（六节结构，不计空格约 2400 字符，锚 25+，2026-11-07）*
