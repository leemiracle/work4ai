# 05 CUDA 感知 MPI 转置：transposeCAMPI.cuf——设备缓冲直传的多卡协作

## 角色定位

`code/ch08/transposeCAMPI.cuf` 是多机多卡章的收官示例：n 个 MPI rank 各绑一块 GPU，用**CUDA-aware MPI** 把设备缓冲直接塞进 `MPI_Sendrecv`，省掉"设备→主存→网络→主存→设备"两跳中转。它也是全书装配度的检验场：kernel 继承 ch05 共享内存转置、绑卡来自 mpiDeviceUtil、打包用 CUF kernel do、通信用 MPI，四种机制各就各位。对照版 `transposeMPI.cuf` 用 pinned 主存 tile 中转（ch08/Makefile:40-41 同场构建），两版对比正是"感知/不感知"的带宽差实验。

## 内部结构

`module transpose_m`（transposeCAMPI.cuf:1-32）只含 kernel `cudaTranspose(matOut, ldOut, matIn, ldIn)`（transposeCAMPI.cuf:6-7）：形参是假定大小数组 `matOut(ldOut, *)`（transposeCAMPI.cuf:9）加 `integer, value` 前导维（transposeCAMPI.cuf:11）——比 ch05 定长版多了 ld 参数化，同一 kernel 可转置任意步长的子块；共享 tile 用消 bank 冲突的 `tile(nTile+1, nTile)`（transposeCAMPI.cuf:12）。主程序（transposeCAMPI.cuf:38-228）依序：MPI_Init 取 rank/size（70-72）→ assignDevice 绑卡（76）→ 整除校验（80-101）→ 网格配置（103-104）→ 宿主初始化+gold（129-138）→ 设备数组与列块装载（143-150）→ 转置主体（158-205）→ 校验与带宽报告（209-220）。

## 外部连接

绑卡依赖 `mpiDeviceUtil` 的 `assignDevice`（mpiDeviceUtil.cuf:6）：`MPI_Comm_split_type` 按 `MPI_COMM_TYPE_SHARED` 切出节点内子通信机（mpiDeviceUtil.cuf:14-15），取本地 rank 号直接 `cudaSetDevice(dev)`（mpiDeviceUtil.cuf:17）——节点内每个 rank 因此绑到不同 GPU；其注释给出关键约束：设备数组必须动态分配否则全落 device 0（mpiDeviceUtil.cuf:3-5），主程序遂全用 allocatable（transposeCAMPI.cuf:55-56）。kernel 血统上承 ch05 的 transposeNoBankConflicts（padded tile 同构，transpose.cuf:110）；同章 transposeP2P.cuf 是无 MPI 对等卡直写变体；构建用 mpif90 编两文件（ch08/Makefile:43-44）。

## 数据流

算法=对角块本地转+非对角块交换：每 rank 持全行×本 rank 列块（148-150 装载）。stage 0 本地转置：`cudaTranspose<<<dimGrid, dimBlock>>>` 把 `matIn_d(myrank*mpiTileRows+1,1)` 写进 `matOut_d(myrank*mpiTileCols+1,1)`（transposeCAMPI.cuf:165-167），传子块首地址+前导维，免切片拷贝。stage 1..nProcs-1：交换伙伴 `sRank=modulo(myrank-stage,nProcs)`、`rRank=modulo(myrank+stage,nProcs)`（174-175）；用 `!$cuf kernel do(2)` 并行打包待发行块成连续 `sTile_d`（181-186）；`MPI_Sendrecv` 的收发缓冲**都是设备数组**（188-191）；收到后立即从 `rTile_d` 转置进最终位置且免解包（196-198）。计时以 MPI_Barrier+MPI_Wtime 夹整体（160-161、202-203），跑两轮报第二轮（158）。

## 设计决策

sTile 打包是"为连续性付费"的典范：MPI 大消息要连续缓冲，而要发送的行块在 matIn_d 里跨列散布，`kernel do(2)`（transposeCAMPI.cuf:181）一次并行打包远快于逐元素拷贝；接收侧却零打包——转置 kernel 本身就能从任意 ld 读（transposeCAMPI.cuf:198 传 ldIn=mpiTileRows），rTile_d 直接当输入矩阵用。kernel 形参 ld 参数化（transposeCAMPI.cuf:6-11）让"写不同列块起点"用传地址实现（如 165-167 传 `matOut_d(...+1,1)`）。整除三连检（80-101）在分布式代码里必须逐 rank 退出前 `MPI_Finalize`（85、93、99），否则其余 rank 死等。

## 新人提示

CUDA-aware MPI 依赖 MPI 实现与 GPU 的联动编译（Open MPI 需 `--with-cuda`），把 transposeCAMPI.cuf:188-191 的设备缓冲传给不感知的 MPI 时小消息常能跑但数据错乱——排障先确认构建链。带宽按全局矩阵规模折算且仅 rank 0 打印（transposeCAMPI.cuf:214-216），多 rank 重复输出别当 bug。`do p = 1, 2` 的第一轮是隐式预热（transposeCAMPI.cuf:158），单轮计时会把 JIT/缓存冷启动计入。校验每 rank 各自报错（transposeCAMPI.cuf:219），单 rank 失败先怀疑本 rank 切片偏移再怀疑 kernel。
