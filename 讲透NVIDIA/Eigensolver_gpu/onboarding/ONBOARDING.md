# Eigensolver_gpu 新人导览（ONBOARDING）

> 图谱基座：`.understand-anything/knowledge-graph.json`（66 节点/122 边/7 层/12 步 tour，@7c6d9f64）。全部行号锚经源码核实（2026-11-07）。

## 1. 项目速览

NVIDIA 2016 年开源的 **Quantum ESPRESSO 定制 GPU 广义特征值求解器**（MIT）：求解 $A x = \lambda B x$（A 对称/Hermitian，B 正定），对标 LAPACK `DSYGVD/X`、`ZHEGVD/X` 与 MAGMA，但**对 CPU 计算的依赖更少**（`README.md:5`）——CPU 侧只剩一个 `zstedc` 调用。README 自我定位 "proof of concept"（`README.md:11`）：只支持一种配置 `ITYPE=1, JOBZ='V', RANGE='I', UPLO='U'`（上三角输入、算特征向量、按 [il,iu] 区间取特征对），即 QE 用到的那一种。

形态是 PGI CUDA Fortran（`!$cuf kernel` 与 `attributes(global)` 手写 kernel 混用），两个顶层入口 `dsygvdx_gpu`（实）/`zhegvdx_gpu`（复）逐行同构——实/复双线对照阅读是理解本库最高效的路径。构建产物是静态库 `lib_eigsolve.a`（13 个 .F90，`lib_eigsolve/Makefile:11`），配 test_driver 双程序四路对比验证。

## 2. 数值算法骨架：四阶段流水

两个顶层入口共享同一条流水（以实数版为例，`lib_eigsolve/dsygvdx_gpu.F90:71`）：

1. **Cholesky 分解 B**：`cusolverDnDpotrf`（`lib_eigsolve/dsygvdx_gpu.F90:121`）得 $B = U^H U$，B 被 Cholesky 因子覆盖；
2. **归约标准问题**：CUF kernel 先把 A 的**下三角暂存进 Z**（`lib_eigsolve/dsygvdx_gpu.F90:131`，evd 阶段要还原），随后 `dsygst_gpu(1,'U',N,A,B,nb=448)`（`lib_eigsolve/dsygst_gpu.F90:31`）分块两角法解 $C = U^{-H} A U^{-1}$——对角块两侧 Dtrsm 联除（L67），尾块 `gemm(±0.5)×2 + syr2k` 对称更新（L82）；
3. **标准问题求解**：`dsyevd_gpu`（`lib_eigsolve/dsyevd_gpu.F90:32`）= GPU 三对角化（dsytrd）→ **CPU `dstedc('I')`** 求三对角特征系（L99）→ GPU 块反射器回乘（DORMTR 手写内联，L119 的 nb2=64 分块循环）；
4. **回解广义问题**：`cublasDtrsm` 左乘 $U^{-H}$（`lib_eigsolve/dsygvdx_gpu.F90:155`）还原广义特征向量，末了 `cudaMemcpy2D` 回 host（可 `_skip_host_copy` 跳过）。

复数版差异全在复数语义：`Zpotrf/Ztrsm` 的 `OP_C`（共轭转置）、`Zher2k` 的 Hermitian 更新、以及多一组实工作区 rwork（`lib_eigsolve/zhegvdx_gpu.F90:75` 签名）。

## 3. 目录与代码地图

```
Eigensolver_gpu/
├── lib_eigsolve/                  # 求解器库（13 .F90 → lib_eigsolve.a）
│   ├── eigsolve_vars.F90          # 全局上下文：handle/3 stream/2 event/finished + init(L39)
│   ├── toolbox.F90                # NVTX 包装 nvtx_inters（USE_NVTX 开关）
│   ├── dsygvdx_gpu.F90 / zhegvdx_gpu.F90   # 顶层入口（实/复）
│   ├── dsygst_gpu.F90  / zhegst_gpu.F90    # 广义→标准归约
│   ├── dsyevd_gpu.F90  / zheevd_gpu.F90    # 标准求解（含 dlarft/dlarfb/finish_T）
│   ├── dsytrd_gpu.F90  / zhetrd_gpu.F90    # 分块三对角化（含 7+7 个 kernel）
│   ├── dsymv_gpu.F90   / zhemv_gpu.F90     # 对称乘 kernel
│   ├── dsytd2_gpu.F90  / zhetd2_gpu.F90    # 32x32 末块 kernel
│   └── Makefile                   # 三档编译参数
├── test_driver/                   # 验证+性能（四路对比）
│   ├── test_dsygvdx.F90 / test_zhegvdx.F90  # 主程序（含随机 SPD 生成器 funcs 模块）
│   ├── toolbox.F90                # compare_utils：泛型 compare 三实现
│   ├── wallclock.c                # gettimeofday 计时垫片（Fortran 下划线链接名）
│   └── Makefile                   # 链接 cuBLAS/cuSOLVER/MKL/静态库
└── README.md
```

图谱 7 层：文档与构建 → 运行时上下文与剖析 → 顶层求解器 → 归约与标准求解 → 三对角化主控 → device kernel 群 → 测试验证。Fortran 的 `use` 模块依赖 scanner 解析不到，图谱 28 条 imports 边为人工补扫并逐条磁盘核实（如 `dsyevd_gpu.F90 → dsytrd_gpu.F90/eigsolve_vars.F90/toolbox.F90`）。

## 4. 数据流与内存布局

**双 buffer 约定**：device 侧 `work` + host 侧 pinned `work_h/iwork_h`；Z 与 Z_h 双份特征向量。工作区契约在入口预检（`lib_eigsolve/dsygvdx_gpu.F90:101` 起）：device `lwork ≥ 2*64*64 + 66*N`，host `lwork_h ≥ 1 + 6*N + 2*N²`（正是 CPU dsygvd 的需求量，`test_driver/test_dsygvdx.F90:185`）。

**上三角存储的全库约定**：输入 A/B 只保证上三角有效；每个需要满阵的环节都先"镜像补全"——dsygst 的 CUF kernel（`lib_eigsolve/dsygst_gpu.F90:57`）、dsymv 对角块的共享内存反射（`lib_eigsolve/dsymv_gpu.F90:82`）、dsytd2 的 a_s 镜像（`lib_eigsolve/dsytd2_gpu.F90:31`）。反过来，dsyevd 结束时从 Z **还原** A 下三角（`lib_eigsolve/dsyevd_gpu.F90:87`，注释自曝 "works if called from zhegvd only!"）——顶层暂存/还原的配对是理解数据流的关键。

**双 stream 流水**：stream1 造块反射器 T（dlarft），stream2 应用（dlarfb），event1/event2 交替等待（`lib_eigsolve/dsyevd_gpu.F90:164`）；dsygst 尾块更新同样双 stream 交叠（`lib_eigsolve/dsygst_gpu.F90:53`）。

## 5. 关键设计决策

- **GPU/CPU 混合的最小 CPU 面**：三对角化、回乘全在 GPU，仅 `dstedc/zstedc` 留 CPU（对 MAGMA 的差异化优势，`README.md:6`）；代价是必须链接含 zstedc 的 LAPACK（`README.md:32`）。
- **last-block 融合 kernel**：`dsyr2_mv_dlarfg_kernel`（`lib_eigsolve/dsytrd_gpu.F90:303`）与 `stacked_dgemv_N_finish_W`（L618）用 `threadfence + atomicinc(finished, nBlocks-1)` 让最后完成的 block 顺手做掉下一步 dlarfg/finish_W 的尾工作——省一次 kernel launch，本库最有学习价值的 CUDA 模式（finished 计数器在 `lib_eigsolve/eigsolve_vars.F90:35` 全局分配）。
- **32x32 末块特化**：分块循环吃到剩 32 列时切换单 block 共享内存 kernel `dsytd2_gpu`（`lib_eigsolve/dsytrd_gpu.F90:86` 调用，`lib_eigsolve/dsytd2_gpu.F90:3` 实现）——小规模下整块驻留共享内存比继续分块快。
- **三档编译参数**（`lib_eigsolve/Makefile:3`）：symv kernel 特意用 `cc60 + maxregcount:255 + nordc` 编译，注释明言"Do not update the cc value!"——Pascal 目标码寄存器压力小，在 Volta 上反而更快；td2 用 `maxregcount:64`。跨架构调优的非直觉样本。
- **NVTX 全埋点**：每阶段 `nvtxStartRange/EndRange` 包裹（`-DUSE_NVTX` 开启，`lib_eigsolve/toolbox.F90:47`），nsight 里直接看 potrf/gst/evd/trsm 分段耗时。
- **单一配置不做通用库**：只支持一种 LAPACK 配置组合，换来热路径零分支——PoC 的自觉。

## 6. 测试与验证

`test_dsygvdx.F90`（`test_driver/test_dsygvdx.F90:73` main）是**四路对比**：① CPU LAPACK `dsygvd` 基准（先 worksize 探测再正式跑，L189）；② MAGMA（`-DHAVE_MAGMA` 编译开关，默认关）；③ cuSOLVER——`HAVE_CUSOLVERDNDSYGVDX` 宏要同时判 PGI 版本与 CUDA≥10.1（L69 的条件编译是 PGI 19.7 前不暴露 CUDA_VERSION 的兼容写法）；④ 自研 `dsygvdx_gpu`（L315）。每路用 `compare` 泛型接口（`test_driver/toolbox.F90:27`）对特征值/特征向量做相对误差核对，`wallclock_`（`test_driver/wallclock.c:30`，gettimeofday 毫秒级）分段计时。数据两条来路：`./test_dsygvdx N` 随机生成对称正定阵（`create_random_symmetric_pd`，L28），或传两个 unformatted 二进制文件。复数版 `test_zhegvdx.F90` 完全同构。

## 7. 坑与勘误（图谱甄别记录）

1. **随机矩阵模式下 M 未初始化**：`test_driver/test_dsygvdx.F90:109` 单参分支只设 N/lda，而 L246/L302 `iu = M` 直接消费 M——`./test_dsygvdx 1024` 跑法下 iu 未定义。双参文件分支才设 M（L137）。复数版同构同坑。
2. **工作区预检阈值与报错文案不一致**：`lib_eigsolve/dsygvdx_gpu.F90:109` 实检 `liwork_h < N`，报错却说 "must be at least 3 + 5*N"；zhegvdx 的 lwork_h/liwork_h 同款——检的从宽、文案照抄 LAPACK 真实需求。
3. **四个死 kernel**：`dsyr2_mv_kernel`（`lib_eigsolve/dsytrd_gpu.F90:166`）与 `stacked_dgemv_N`（L511）的唯一调用点已被注释（L145/L157），被融合版取代；复数版 `zher2_mv_kernel`/`stacked_zgemv_N` 同理——别把死代码当活路径。
4. **`dsyevd_gpu` 的 Z 按 lda 声明**（`lib_eigsolve/dsyevd_gpu.F90:47`）而非 ldz——能工作全靠调用方传 ldz=lda（`test_driver/test_dsygvdx.F90:315`）；外部直调且 ldz≠lda 会静默越界。
5. **`not(skip_host_copy)` 是位反内置的 PGI 扩展用法**（`lib_eigsolve/dsygvdx_gpu.F90:159`），移植 gfortran 要改 `.not.`。
6. **zhetd2/dsytd2 硬编码 32**：kernel 签名 `a(lda,32),tau(32)`（`lib_eigsolve/zhetd2_gpu.F90:7`）——块大小是编译期常量，非可调参数。
7. **`create_random_hermetian_pd` 拼写**（`test_driver/test_zhegvdx.F90:28`）：hermetian 系上游原文（非 hermitian），引用保持原文。
8. **tested_by 边曾被 merge 误删后人工回补**：merge 脚本按扩展名识别测试文件，`.F90` 不在模式表导致 `test_*.F90` 被判为生产码、两条合法 tested_by 边按 prod↔prod 规则丢弃——已回补并加 "tested" 标签（工具 schema 盲区，流水线钉版素材）。

## 8. 新人上手路径

1. 读 `README.md`（40 行）确认配置假设与依赖（PGI 18.10+/cuBLAS/cuSOLVER/MKL zstedc）；
2. 走通实数主线四阶段：`dsygvdx_gpu.F90:71` → `dsygst_gpu.F90:31` → `dsyevd_gpu.F90:32` → 回到入口的 trsm——对照第 2 节流水图；
3. 下钻三对角化：`dsytrd_gpu.F90:30`（主控）→ `dlatrd_gpu.F90:98`（kernel 编排）→ 挑 `dlarfg_kernel`（L200，warp shuffle 归约）和 `dsyr2_mv_dlarfg_kernel`（L303，last-block 融合）两个 kernel 精读；
4. 用复数版对照加深理解：`zhetrd_gpu.F90` 与 `dsytrd_gpu.F90` 逐段 diff，看复数 τ/共轭转置在哪里引入；
5. 跑 `test_driver/Makefile` 构建双测试程序（需 MKLROOT/CUDA_HOME 环境），先用小 N（如 512）验证四路 compare 全过，再用 nvprof/nsight 看 NVTX 分段（记得开 `-DUSE_NVTX`）；
6. 改动算法前先读第 7 节的坑清单——尤其 M 未初始化与预检文案不一致两处，避免在验证程序层面误判自己代码的 bug。

---

*图谱指纹基线 21 文件 @7c6d9f64；本文件 8 节，锚 40+，2026-11-07 生成。*
