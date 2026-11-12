# 02 · classical 经典 AMG：strength → selector → interpolator 流水线

## 角色定位

classical 目录实现 Ruge-Stüben 式经典 AMG（图谱 L02，36 节点）：把点划分为粗点 C/细点 F，直接构造细点到粗点的延拓权重。组织成三段流水线——strength（连接强度）→ selector（C/F 选择）→ interpolator（延拓矩阵 P）——由 `Classical_AMG_Level_Base`（include/classical/classical_amg_level.h:35）串成层级。与 aggregation 的分段常数延拓不同，这里生成显式稀疏 P 与 R=P^T 再 Galerkin 积出粗矩阵。

## 内部结构

骨架在 src/classical/classical_amg_level.cu（987 行）：构造函数经三工厂各分配一组件（:181-183）。`createCoarseVertices`（:213-251）在前 aggressive_levels 层换装激进 selector（:215-220），分配 m_cf_map/m_s_con/m_scratch（:241-243）后调 `markCoarseFinePoints`（:250）。后者（:345-402）是流水线现场：strength->computeStrongConnectionsAndWeights 填权重（:375/380）→分布式交换 1-ring halo（:386）→selector->markCoarseFinePoints 出 cf_map（:390）→2-ring 交换（:397）→renumberAndCountCoarsePoints（:401）。`createCoarseMatrices`（:254-342）先拒分布式 D1（:270-273），再 computeProlongationOperator（:406-435：generateInterpolationMatrix :415→max_elmts 截断 :424-427）→computeRestrictionOperator（:441-447，transpose 出 R）→computeAOperator（:916）/分布式变体（:929），末段对 RAP 做 interior/boundary 重排（:303-322）。组件侧：selector.cu（1620 行）是骨架与工厂；distance2.cu（2274 行）插值族最大，device 实现在 :1903、Base 分发 :2241-2255、7 个 `__launch_bounds__` kernel 在 :604-1564。

## 外部连接

上游：AMG_Setup 按序调 createCoarseVertices/createCoarseMatrices（src/amg.cu:270/367）；AMG_LevelFactory 注册名 CLASSICAL（src/core.cu:627）。注册表集中在 core.cu：selector PMIS/AGGRESSIVE_PMIS/HMIS/AGGRESSIVE_HMIS/DUMMY/CR（core.cu:646-651），插值器 D1/D2/MULTIPASS（:659-661），strength AHAT/ALL/AFFINITY（:665-667）；默认 selector=PMIS（:459）、interpolator=D1（:451）、strength=AHAT（:481）。solve 期 restrictResidual（:591）/prolongateAndApplyCorrection（:852）被 FixedCycle 调。

## 数据流

setup 四工件：m_s_con（强连接标记）、weights（浮点测度，供 PMIS 随机优先序）、m_cf_map（C/F 映射→粗点局部编号）、P/R。分布式下 weights 与 cf_map 各需 halo 交换（1-ring/2-ring），是跨分区 C/F 一致性关键。P 生成后临时数组 clear+shrink（:416-421）。solve：r=A*x-b→restrictResidual→粗层 xc→prolongateAndApplyCorrection 加回 x；consolidation 向量搬移走 :943/959。

## 设计决策

三段各自工厂化，PMIS 换 HMIS 不动其余两段。AHAT 度量仅一行谓词 `-val >= -threshold`（include/classical/strength/ahat.h:26-30），权重骨架在 strength_base.cu:688；AFFINITY 是重武器：跑 affinity_iterations 轮测试向量平滑（affinity.cu:446）后按 s_xy²/(s_xx·s_yy+ε) 算亲和度（affinity.cu:256），参数默认 4/4（core.cu:486-487）。PMIS 以 MarkAdditionalPoints 迭代标记（pmis.cu:25/204-205），块大小>1 FatalError（pmis.cu:633-637）——classical 整族基本 1x1 专用。激进粗化不建新类：临时改配置字符串再买组件（classical_amg_level.cu:161-178）。

## 新人提示

查参数去 core.cu:445-487 注册描述，合法值与默认值一行可查。默认 PMIS+D1 适合结构网格；非结构/各向异性换 D2 或 MULTIPASS（AMG_CLASSICAL_* 预设全用 D2）。三旋钮：strength_threshold 0.25（粗化太慢就降）、max_row_sum 1.1、interp_max_elements -1（复杂度爆炸开截断）。读 distance2.cu 先看 :2241 分发再看 :1903 实现。分布式重点在 :303-322 重排段，P 列数靠 reduce max+1 回填（:318-320）最易错。strength 文档只写 `<ahat|all>`（core.cu:481）但 AFFINITY 已注册——文档滞后。
