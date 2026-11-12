# 01 · amg.cu：AMG_Setup 主流程——三精度模板与粗化层级构建

## 角色定位

`src/amg.cu`（1564 行）是 AMGX 顶层装配线：`AMG<vecPrec,matPrec,indPrec>` 持有层级骨架，后半的 `AMG_Setup` functor 类（amg.cu:146-1563）把细网格矩阵逐层粗化成层级，`AMG_Solve`（amg.cu:1086）驱动单次迭代。粗化算法本身全在 AMG_Level 三系子类里，本文件只做层级生命周期编排：建层、复用、跨 host/device 移交、停层。

## 内部结构

四段。①`AMG` 构造函数一次读 12 个层级控制参数（amg.cu:43-54：cycle_iters/max_levels/coarsen_threshold/min_coarse_rows/structure_reuse_levels 等）；coarse_solver 为 NOSOLVER 时置空，否则 SolverFactory 在 host+device 双空间各分配一个（amg.cu:64-73）；DENSE_LU_SOLVER 再补读 dense_lu_num_rows/max_rows（amg.cu:81-85）。②`AMG_Setup::setup<TConfig_hd>` 的 `while(true)` 循环（amg.cu:201-418）：判粗层终止（amg.cu:207：`num_levels>=max_levels || min_partition_rows<=min_rows`）→分配或复用 next level（amg.cu:232-262，复用时对粗矩阵 `Ac.set_initialized(0)` amg.cu:261）→createCoarseVertices（amg.cu:270）→全局规约下层规模→建或删。③`setup_v2`（amg.cu:425）是带 glue（分区合并）的变体。④末尾 6 组显式实例化（amg.cu:1554-1561）：三个实数/复数精度组合，索引恒 indInt。

## 外部连接

向上被 amg_solver.cu 调用：`setup(Matrix_h&)`（amg.cu:1123）以 `setup<TConfig_h,AMGX_host,AMGX_device>` 进入，`setup(Matrix_d&)`（amg.cu:1152-1162）镜像对调。向下经 `AMG_LevelFactory::allocate`（amg.cu:241/603）分发三系层级；分布式挂 glue_matrices（amg.cu:844，unpack→glue→upload→repack）；D2 workspace 与 CSR_Multiply 共享（amg.cu:128/135）。solve 侧经 `CycleFactory::generate`（amg.cu:1110）交 cycles 层。

## 数据流

setup 是矩阵逐层收缩：A 进 level_0（amg.cu:897-899）→每轮 createCoarseVertices 出粗点标记、createCoarseMatrices（amg.cu:367）出 P/R/Ac；压缩率判据 `nextN <= coarsen_threshold*N && min_partition_rows>=min_rows`（amg.cu:365）不满足则 deleteNextLevel 回滚（amg.cu:388）。建层成功按 nextSize resize xc/bc/r 并以 `tag*100+{0,1,2}` 编通信标签（amg.cu:369-383）。分布式每轮 global_reduce 收 partition_rows（amg.cu:280），min 或 sum（use_sum_stopping_criteria，amg.cu:333-361）聚出全体一致的停层判据。solve 极薄：solve_iteration 同步流后取 finest 交 CycleFactory（amg.cu:1102-1118）。

## 设计决策

三精度枚举做模板参数而非 T_Config（amg.cu:37），精度组合在类型层固化、显式控制实例化数量。静态 functor 而非成员函数，为按 TConfig_hd 二轴分派且免虚调用。两个折中：①hybrid 模式 `min_fine_rows>min_coarse_rows` 时细层在 GPU 建、到阈值后剩余层级整体搬到另一内存空间重建（amg.cu:968-995），粗层 kernel 启动开销不划算；②classical 的 consolidation 用 rank0 的 cudaMemGetInfo 反推层级内存 6 倍估算（amg.cu:913-928），MPI_Bcast 阈值（amg.cu:947-948）——纯启发式。WARNING 注释明示复用层级时不重算 P/R 只重算 Ac（amg.cu:250-259/612-621）。amg_host_levels_rows>0 的 host 层级拷贝自注 experimental（amg.cu:1007），transfer_from（amg.cu:1031）逐层复制。

## 新人提示

先抓 `while(true)` 不变量：level 从 finest 走向 coarsest，num_levels 每轮 +1（amg.cu:414-417），提前 return 分支（DENSE_LU 超限 amg.cu:211、空矩阵 amg.cu:551、非 root consolidation 分区 amg.cu:402-409）都先处理 smoother 再退。三套 setup 入口勿混：三参版（amg.cu:861）是外层编排，单参版是层内循环，v2 仅 classical+consolidation 进入（amg.cu:901-961）。0 行分区的忽略规则 v1/v2 有差（amg.cu:341 vs 702）。printGridStatistics/printCoarsePoints（amg.cu:1230/1421）是调试层级最快手段。
