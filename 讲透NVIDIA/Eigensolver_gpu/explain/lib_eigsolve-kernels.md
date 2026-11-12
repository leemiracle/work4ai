# 精讲：三对角化 kernel 群 —— last-block 融合与手写 CUDA Fortran 计算底座

> 锚基线：仓库 @7c6d9f64；行号引自 lib_eigsolve/*.F90，全部经源码核实。

## 1. 角色定位

求解器的算力底座：`dsytrd_gpu.F90`（728 行，9 例程）与复数对偶 `zhetrd_gpu.F90`（883 行，9 例程）承担 Householder 分块三对角化；`dsymv_gpu.F90`/`zhemv_gpu.F90` 是分块对称乘 kernel；`dsytd2_gpu.F90`/`zhetd2_gpu.F90` 是 32x32 末块特化 kernel。这一层最能体现 2016 年 CUDA Fortran 手写 kernel 的工程水准——warp shuffle 归约、共享内存镜像、**last-block 融合**三个模式反复出现，实/复双线对照。

## 2. 内部结构

**主控层**（host 子程序）：`dsytrd_gpu`（`dsytrd_gpu.F90:30`）从 N 向下按 nb 批量循环——`dlatrd_gpu`（L98）生成 nb 个反射器（写 tau/更新 W），`cublasDsyr2k` 更新尾阵（L66）；余量块单独处理（L76-82），最后 32 列交 `dsytd2_gpu<<<1, dim3(32,32)>>>` 单 block kernel（L86）；对角元经 CUF kernel 直写 d（L89-93）。

**kernel 层**四类：

- **反射器生成** `dlarfg_kernel`（L200）：单 block；每线程算 x(i)² 分块累加（L228-241），warp 内 `__shfl_down` 五级折半归约（L245-254），lane 1 `atomicadd` 进共享 xnorm（L256-258）；tid==1 按 dlapy2 稳定公式算 beta/tau（L275-284），全线程并发 dscal 缩放+末元素置 1（L289-297）。复数版 `zlarfg_kernel`（`zhetrd_gpu.F90:211`）实虚双归约、beta 沿 alpha 相位取反。
- **融合 kernel**（本库精华）：`dsyr2_mv_dlarfg_kernel`（L303）先做对称秩 2 更新+清零（L328-344），随后 `threadfence`（L346）+ `atomicinc(finished, nBlocks-1)`（L350）——只有最后完成的 block 继续做 dlarfg 尾工（L353 起），其余 block return；`stacked_dgemv_N_finish_W`（L618）同款模式融合 finish_W 的 α 归约+daxpy。**四个非融合版是死代码**：`dsyr2_mv_kernel`（L166）与 `stacked_dgemv_N`（L511）的唯一调用点已被注释（L145/L157），复数版 `zher2_mv_kernel`/`stacked_zgemv_N` 同理。
- **堆叠 GEMV**：`stacked_dgemv_T`（L449）一个 2D 网格同时算 z1=Vᵀx、z2=Wᵀx（i>M 走 W 分支，L479-483），shuffle 归约+atomic 输出；复数共轭版 `stacked_zgemv_C`（`zhetrd_gpu.F90:513`）。
- **对称乘** `dsymv_gpu`（`dsymv_gpu.F90:33`）：32x8 线程块+4 tile 共享内存（BX=32/BY=8/NTILES=4 宏，L29-31）；对角块共享内存 (33,32) 镜像补全下三角（L82-86），上三角块算直接贡献之外顺带 shuffle 归约出对称下块贡献 r_s（L110-130），atomicadd 双路累加 y（L136/L147）。

**末块 kernel** `dsytd2_gpu`（`dsytd2_gpu.F90:3`）：单 32x32 block，a_s 共享整块镜像，i=n-1..1 逐列 warp 归约 xnorm、tl==1 算 beta/tau、全块并发 dscal+秩 2 修正（`a_s(tx,ty) -= a_s(tx,i+1)·tau(ty) + a_s(ty,i+1)·tau(tx)`，L149-151）；硬编码 32（kernel 签名 `a(lda,32)`）。

## 3. 外部连接

上游：`dsytrd_gpu use dsytd2_gpu`（`dsytrd_gpu.F90:32`）、`dlatrd_gpu use dsymv_gpu`（L100）——跨文件 kernel 调用；eigsolve_vars 提供 finished 设备计数器（`eigsolve_vars.F90:35`，init 清零 L57）与 stream1；cublas 的 syr2k 承担尾阵更新。下游：`dsyevd_gpu.F90:80` 调 `dsytrd_gpu`；复数线 `zheevd_gpu.F90:34`→`zhetrd_gpu`。Makefile 对本层特殊照顾：dsymv/zhemv 用 FLAGS3（cc60+maxregcount:255+nordc）编译、td2 用 FLAGS2（maxregcount:64）（`lib_eigsolve/Makefile:16-22`）——注释明言 Pascal 目标码在 Volta 上更快，勿改。

## 4. 数据流

`dlatrd_gpu` 的 W 矩阵（N×nb）是 kernel 链的数据枢纽：首列单独处理（dlarfg→dsymv 算 W 首列→finish_W 收尾，L125-139），其后每列四连：`dsyr2_mv_dlarfg`（更新 x 并生成下一反射器）→ `dsymv_gpu` 算 W 当前列 → `stacked_dgemv_T`（V/W 堆叠乘出两个中间向量）→ `stacked_dgemv_N_finish_W`（回乘并收尾 W 列）——相邻 kernel 间靠 finished 计数器与 threadfence 保证可见性。W2 工作列（N+2M 长度）由 kernel 首 block 清零复用。

## 5. 设计决策

- **last-block 融合省 launch**：2016 年 kernel launch 开销（~5-10μs）相对小 kernel 占比高，把"更新完顺手做反射器/收尾"折进同一 kernel 是吞吐关键——代价是每个融合 kernel 尾部多出一段 last-block-only 代码，可读性让位。
- **atomicinc 而非 cooperative groups**：那是 CUDA 9 之前的时代，`threadfence+atomicinc` 是标准的"最后一个 block"原语；cooperative launch 后来才标准化。
- **32 列切换单 block kernel**：尾块太小喂不饱多 block，共享内存整块驻留反而快——规模感知的算法切换点写死在主控（L59 `kk = N-((N-32)/nb)*nb`）。
- **死代码保留不删**：被融合版取代的 4 个 kernel 留在源里（调用点注释）——2016 年性能实验的遗迹，成了今天读"融合演进史"的活标本。
- **实/复完全平行**：两文件结构逐行对应，复数版只加共轭与相位逻辑——双线 diff 是维护策略也是教学材料。

## 6. 新人提示

精读顺序：`dlarfg_kernel`（warp shuffle 教科书）→ `dsymv_gpu`（分块+镜像+双贡献）→ 任一融合 kernel（last-block 模式）→ `dsytd2_gpu`（单 block 全流程）。读融合 kernel 先找到 `if (nFinished < nBlocks - 1) return` 这一行（L353/L667）——它之前是"人人有份"的更新段，之后是"最后 block 独做"的收尾段，两段思维模型不同。坑：finished 是**全局单例**（eigsolve_vars 分配），意味着同一时刻只能有一个融合 kernel 在跑——并发调用求解器会竞态；dsymv 的 FLAGS3 编译参数别"好心升级"到 cc70（Makefile 注释警告有据）；引用 stacked_dgemv_N/dsyr2_mv_kernel 时记得它们是死代码，别当活路径分析。

*（六节结构，不计空格约 2500 字符，锚 30+，2026-11-07）*
