# 02 转置优化阶梯：transpose.cuf——合并访存的四步爬升

## 角色定位

`code/ch05/transpose.cuf` 是全书性能教学的枢纽文件：矩阵转置"计算极简、访存极重"，六个 kernel 排成从 naive 到对角重排的优化阶梯，把"合并访存—共享内存中转—bank 冲突—分区冲突"这条 CUDA 性能主线一次讲透。主程序以统一的事件计时+校验+带宽换算收口（transpose.cuf:380-387）——ch03 教的度量方法在这里兑现为结论。ch08 的多卡转置直接复用本文件的 kernel 形态。

## 内部结构

`module kernels`（transpose.cuf:1-172）定死规模 nRows=nCols=1024、线程块 32×8（transpose.cuf:2-3）、nTile=32（transpose.cuf:4）。六个 kernel 依次是：`copyMat` 纯拷贝基准（transpose.cuf:9-22）；`copySharedMem` 加共享内存中转的拷贝基准（transpose.cuf:26-46），用来隔离"共享内存本身不白给"的代价；`transposeNaive`（transpose.cuf:53-66）读合并写不合并；`transposeCoalesced`（transpose.cuf:75-98）共享 tile 中转后双端合并；`transposeNoBankConflicts`（transpose.cuf:105-128）tile 加一列 padding；`transposeDiagonal`（transpose.cuf:135-170）再叠加块调度重排。每个 kernel 的循环结构相同：32×8 线程块按 `do j = 0, nTile-1, blockCols` 分四趟处理 32×32 tile（transpose.cuf:19）。

## 外部连接

计时骨架来自 ch03：`cudaEventCreate`（transpose.cuf:248-249）、record-loop-record-synchronize-elapsed 五连（transpose.cuf:265-271）、NUM_REPS=100 次重复取均值（transpose.cuf:187）。正确性参照用宿主内建 `gold = transpose(matIn)`（transpose.cuf:238）。ch08 的 `cudaTranspose` 继承了本文件 `transposeNoBankConflicts` 的 padded tile 写法（transposeCAMPI.cuf:12 的 `tile(nTile+1, nTile)`），并把定长形参推广为 ldOut/ldIn 前导维参数化版本（transposeCAMPI.cuf:6-11）——同一 kernel 从单卡演示长成了集群构件，是本仓"模块复用"叙事的最好例证。

## 数据流

每个 kernel 内部两段式搬运：读段把全局内存 tile 装入 `real, shared :: tile(nTile, nTile)`（transpose.cuf:80），`call syncthreads()`（transpose.cuf:90）设栅栏，写段再读出。关键在坐标交换：读段 `tile(threadIdx%x, threadIdx%y+j) = matIn(row,col+j)`（transpose.cuf:87），threadIdx%x 连续 → 行连续 → Fortran 列主序下地址连续，读合并；naive 直接 `matOut(col+j,row) = matIn(row,col+j)`（transpose.cuf:64），写端地址跨 nCols 步长塌陷。coalesced 版在写段把行列角色对调（transpose.cuf:92-93），`matOut(row,col+j) = tile(threadIdx%y+j, threadIdx%x)`（transpose.cuf:96）恢复写合并。宿主侧：`random_number(matIn)`（transpose.cuf:237）→ `matIn_d = matIn`（242）→ 各 kernel 计时 → 拷回交 postprocess 比对（311-312）。

## 设计决策

padding 决策是本文件的点睛之笔：写段访问 `tile(threadIdx%y+j, threadIdx%x)`，第一维慢变第二维快变，对 `tile(32,32)` 等价于步长 32 的列访问，32 个线程全部落在同一 bank 上（32 路 conflict）；把 tile 改成 `tile(nTile+1, nTile)`（transpose.cuf:110）后步长变 33，bank 被打散。对角重排（transpose.cuf:144-147 方阵分支、149-152 矩形分支）改的不是访存模式而是块调度顺序：让写向同一 DRAM 分区的块在时间上错开。主程序把 threadBlock 定成 `dim3(blockRows, blockCols, 1)` 的 parameter（transpose.cuf:184），并预检 nRows/nCols 整除 nTile（transpose.cuf:202-206）。带宽口径在 postprocess 内定死：`2.0*sizeof(res)*1.0e-6/(t/NUM_REPS)`（transpose.cuf:383），读+写各计一次。

## 新人提示

读代码时盯住"谁的连续在换手"：合并访存的本质是**同一 warp 内相邻线程访问相邻地址**，与循环写法无关。四个台阶的收益都要在这张带宽表上实测验证，不同架构上对角重排可能已无增益。`do j = 0, nTile-1, blockCols` 从 0 起步（transpose.cuf:19）是对齐 C 原版的写法，与线程索引从 1 起步（transpose.cuf:16-17）并存于同一文件，移植时最容易看串。校验失败的行打印 `*** Failed ***`（transpose.cuf:385）而非带宽数，跑表先扫这一列。
