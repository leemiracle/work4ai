# 05 · BVLS-ADMM 求解器双路径——blendshape solve 的 CPU/GPU 两套数学方言

> 锚点前缀：仓库根 `audio2face-sdk/`。行号锚全部从源码核实。

## 一、角色定位

blendshape solve 是几何→权重的逆问题：给定目标顶点姿态，求一组带界 blendshape 权重使重建误差最小。SDK 对同一个问题维护**两套算法路径**：CPU 路径用 Eigen 手写的 **BVLS**（bounded-value least squares，有界变量最小二乘，bvls.cpp:293-368 的 solveSystem）；GPU 路径用 cuBLAS+自定义内核实现的 **ADMM**（交替方向乘子法，admm.cu）。工厂一布尔切换：`CreateBlendshapeSolver(bool gpuSolver)`（audio2face.h:110，audio2face.cpp:422-426 转发）。两份纯声明头 internal/admm.h（:24-43 仅两个函数原型）与 internal/bvls.h（:26-80 八个原型）在图谱阶段因 tree-sitter 提取为空而**手工补建函数节点**（NOTES-DIGEST batch-9-part-1/2 的甄别事实）。

## 二、内部结构

**BVLS 侧**（bvls.cpp，Eigen 方言）：核心是活动集法。`constrainedMin` 在固定边界变量后对自由变量做最小二乘——全部自由时直接 JacobiSVD 快解（:52-58），否则构造 `A_free = A(·, free_vars)` 解降维系统（:85-87），推导注释完整保留（:68-83 的 S 矩阵展开）。配套件：`initialFeasiblePoint` 逐轮把越界变量钉到边界（:107-148）；`computeKktOptimality` 取 KKT 违背最大值当收敛指标（:150-165）；`varToDetach` 按梯度符号挑"最值得松绑"的边界变量（:167-218）；`makePointFeasible` 是线搜索式比例检验（:220-267）；`updateOnBound` 刷新边界标记（:269-291）。**ADMM 侧**（admm.cu，CUDA 方言）：单个 `ADMMupdateKernel` 一次线程块内完成 x/z/u 三变量更新（:32-72，逐行注释对应 numpy 原型 :46/:57/:69），z 更新即 clip 到 [lower, upper]（:58-66）；`admm_init` 用两次 cublasSgemm 算 Aᵀb 与 A⁻¹b 初值（:102-131）后 ClipKernel 投影（:133-138）；`admm_update` 以 **alpha=1.9f**（过松弛，:153）单内核迭代（:155-161）。

## 三、外部连接

两条路径各挂在一份 solver 实现里，共享 blendshape_solver.h 的 `IBlendshapeSolver` 契约（:91-231）与默认正则常数——L1=1.0、L2=3.5、Symmetry=100、Temporal=0、templateBBSize=54.7、tolerance=1e-10（:30-35）。CPU 路径 blendshape_solver.cpp：Solve 用 promise/future 把异步封装成同步（:120-129）；SolveAsync 走 job runner 线程池（:137-150），b 向量在 GPU 算好（cublasSgemv :182-187）经 pinned 内存回传（:190-198），cpuSolve lambda 先 cudaEventSynchronize（:214）、叠加时间正则 `b = ATb + TemporalReg·scaleFactor·prevWeights`（:225）后调 `bvls::solveSystem`（:232）。GPU 路径 blendshape_solver_gpu.cpp 全程留在设备上：`admmSolveAsync` lambda 里 admm_init 后**双缓冲乒乓跑 2 轮 ×2 次更新**（:295-305，z1/u1↔z2/u2），Wait 仅是 cudaStreamSynchronize（:334-336）。两级管线中的位置见篇 02：blendshape 执行器在几何回调里对每轨 solver 调 SolveAsync（executor_blendshapesolve.cpp:421-423）。

## 四、数据流

两路径的 b 构造完全同构（对照 blendshape_solver.cpp:159-187 与 blendshape_solver_gpu.cpp:247-277）：目标姿态减中性姿态（cublasSaxpy，α=-1）→ deltaPosesᵀ·targetDelta（cublasSgemv 转置）→（GPU 版直接把 β 设为 `TemporalReg·scaleFactor` 在 gemv 里一步叠上时间正则，:271-276）。**cancel pairs 二次求解协议**两路径镜像：CPU 版首轮 BVLS 后按配对把败者上界压到 1e-10f 再解一轮（blendshape_solver.cpp:234-238）；GPU 版 `SetUpperByCancelPairs` 重设上界后整个 admmSolveAsync 重跑（blendshape_solver_gpu.cpp:314-318）。GPU 版收尾三步：保存 solvedWeights 为 prevWeights（:320）、把活跃姿态权重 Unmap 回全量 blendshape 向量（:323-325）、套乘数与偏移（:328-329）——CPU 版的对应收尾在 :234 之后同样存在。

## 五、设计决策

①**同一数学、两种方言**：BVLS 活动集精确但天然串行（每轮一次 SVD）；ADMM 可并行但只有 2 轮×2 次的浅迭代（blendshape_solver_gpu.cpp:296-305）——GPU 用精度换吞吐，依赖 L1/L2 正则把问题调得易收敛。②**正则骨架在 Prepare 预烘焙**：AMat、AmatInv、AdmmWeights、AdmmMatInv 全部缓存（BlendshapeSolverCache blendshape_solver.cpp:44-60），Solve 阶段零分解开销。③**时间正则两处不同实现**：CPU 在主机侧显式相加（:225），GPU 借 gemv 的 β 参数融合（:271）——同式不同形，读码时易误判为不一致。④**收敛保险丝**：BVLS 主循环上限 `iter < x.rows()`（bvls.cpp:316）、代价意外上升即 break 并 LOG_DEBUG（:352-357）、最优性停滞 1e-6 也 break（:361-364）——三重退出防止病态系统卡死。

## 六、新人提示

调"权重抖动"先动 TemporalReg（默认 0，blendshape_solver.h:33）再查 prevWeights 是否被正确回滚（CPU 版 Reset 应清 prevWeights）；两路径数值不会逐位一致——GPU 是近似解，对比回归基线要留容差。读 admm.cu 的 numpy 注释（:46/:57/:69）能最快理解三变量更新，但注意 alpha=1.9 的过松弛是源码经验值（:153）无推导。改动活跃姿态集合必须重跑 Prepare()（blendshape_solver.cpp:146-149 的报错提示），缓存里的 AMat 维度不会自适应。
