# 04 · energymin 能量极小化 AMG 与 scalers/convergence 外围

## 角色定位

energymin 是第三种 AMG 变体（图谱 L04，27 节点域主体）：粗点选择沿用 classical，插值改为能量极小化（EMIN-AMG 路线）——对每个粗点邻域子块解小规模最小二乘，使延拓算子在能量范数下最优。`Energymin_AMG_Level_Base`（include/energymin/energymin_amg_level.h，实现 src/energymin/energymin_amg_level.cu 431 行）是三系层里最小的。同域另有收敛外围：scalers（预缩放）与 convergence（停止判据），挂在求解器框架上。

## 内部结构

层级构造关键在复用：selector 直接买 classical 工厂产品（energymin_amg_level.cu:43），仅当配置 selector=PMIS 时补 strength（:48-52）；成员声明印证——selector 是 `amgx::classical::Selector*`（energymin_amg_level.h:94）。自己的插值器走 energymin 域工厂，按 `energymin_interpolator` 参数取（em_interpolator.cu:77，注册名 EM，core.cu:663；默认 EM，core.cu:453）。`createCoarseVertices`（:67-78）只备 m_cf_map 后 markCoarseFinePoints。`createCoarseMatrices`（:82-121）顺序 R→P→Ac：computeRestrictionOperator（:92）在前，单卡 computeProlongationOperator+computeAOperator（:98-99）、分布式 computeAOperator_distributed（:103）。host 未实现（computeAOperator_1x1 :235-238、distributed :333-335 两处 FatalError）——实际 device-only。EM 插值器（src/energymin/interpolators/em.cu，1280 行）三步：generateInterpolationMatrix_1x1（:1112）数粗点、生成 coarse_idx（:1117-1127），computePsparsity（:1132）定稀疏结构；solveMa_e 对 Ma·x=e 跑 PCG（:1201，源码保留 Matlab 等价注释 :1190-1194）；computePvalues（:1219）按 P(:,j)=It_j·(invAij_j·(It_jᵀ·x)) 逐列解，稠子块 LU 用 cusolverDn（:1221-1228）。

## 外部连接

上游注册名 ENERGYMIN（core.cu:629）。scalers 经 ScalerFactory 注册 DIAGONAL_SYMMETRIC/BINORMALIZATION/NBINORMALIZATION（core.cu:687-689）：对角对称缩放 D^(1/2)AD^(1/2)（diagonal_symmetric.cu:135 sqrtVector，SPD 正对角检查 :131），binormalization 行列双侧幂迭代（binormalization.cu:80/150 host/device 双实现，n 次迭代变体 nbinormalization.cu 647 行）。convergence 五判据注册（core.cu:680-685），RELATIVE_INI 常用（relative_ini.cu:34 判据 `nrm <= max(nrm_ini*ε_machine, eps)`），机器精度阈值 Epsilon_conv 按类型特化（include/convergence/convergence.h:25-33）。

## 数据流

setup：cf_map（借 classical selector+strength 产出）→R 结构→Ma 组装与 PCG 解 x→逐粗点列稠密 Aij 子块 LU→P 数值。与 classical 的差别是 P 不是插值公式而是能量最优解，每列独立小方程组天然并行。solve 期与 classical 同构。scaler 在 setup 前缩放 A 存 scale 向量；convergence 每迭代拿范数序列检查。

## 设计决策

energymin 不自建 selector 体系而复用 classical（energymin_amg_level.cu:43）——但留下一处断链勘误：energymin 域自己的 SelectorFactory（em_selector.cu:14-80，allocate 读 `energymin_selector`，core.cu:455 注册默认值"CR"）在 core.cu:652 只有空注释占位、零注册项，运行时走到必 FatalError"has not been registered"；CR 实际注册在 classical 工厂（core.cu:651），要用 CR 配 selector=CR 而非 energymin_selector=CR。EM 把稠密 LU 放 device 因小矩阵批量求解吞吐更高。scaler 与 cycle 的配合见预设 V-cheby-smoother.json（scaling=DIAGONAL_SYMMETRIC 配 CHEBYSHEV）。

## 新人提示

energymin 是三系里成熟度最低的：host 三处 FatalError、预设 JSON 无一份 ENERGYMIN 配置，生产优先 aggregation/classical。读 em.cu 先读 :1186-1240 的 Matlab 等价注释块再回 kernel。收敛发散先查 convergence 判据与 tolerance（预设标配 RELATIVE_INI+1e-06），再试 binormalization 预缩放。Epsilon_conv 的 float 1e-6 是单精度相对判据地板（精度体系见 include/basic_types.h）。加新判据记得 core.cu 注册表与 convergence.cu 工厂两处同步。
