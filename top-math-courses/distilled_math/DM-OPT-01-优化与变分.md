---
card_id: DM-OPT-01
title: 蒸馏卡 · 优化与变分
universe: distilled_math
burke: {场景:数学学习+AI研究, 主体:GLM-5.3教师, 能动:内隐知识显性化, 行动:八节结构+三层验证, 目的:可复用数学知识资产, 张力:模型知识海量vs可核查外显有限, 弧线:直觉链→定理网→反例→验证→互链→路径}
prereq: [DM-LIN-01, DM-REAL-01]
status: distilled-verified
refs: [Boyd & Vandenberghe, Convex Optimization; Nocedal & Wright, Numerical Optimization; Bertsekas, Convex Analysis and Optimization]
updated: 2026-08-27
---
# 优化与变分（模型蒸馏版）
> 一句话本质：优化研究"最好的选择"（向量空间里的极值），变分把对象升级为函数（曲线/场上的极值）；凸性是分水岭——凸世界里局部=全局、对偶无 gap、KKT 充要，非凸世界里这三条全部只剩"必要"。

## 0. 蒸馏元数据
- teacher：GLM-5.3（zhipuai-coding-plan/glm-5.3）
- 验证状态：L1 机器断言 **13/13 通过**（`experiments/dm_opt_check.py`，2026-08-27 真跑）；L2 出处教材级；L3 Lean 挂账
- 置信统计：机器验证 28 条 / 教师高置信未核 7 条 / 争议或简化 0 条
- 诚实边界：μP 定理出处写"Greg Yang Tensor Programs 系列，arXiv ID 待核"（项目铁律：ID 不凭记忆）；PL 收敛常见归于 Karimi–Nutini–Schmidt（arXiv ID 待核）；FISTA 速率 O(1/k²) 是上界陈述，P7 只验证"等预算分离"而非斜率指数（调参中实测斜率可达 −3.5，见 §3-3，未入正式脚本）
- 验证日志：2026-08-27 首跑 11/13 → P7 改等预算分离断言、P8 独立实例+预逆、P9 半角恒等式、P10 窗口法 → 13/13

## 1. 直觉链（这个域为什么存在）
1. **为什么对偶是"定价"**
   每个约束配一个影子价格（Lagrangian 乘子），把"必须可行"换成"违反要付钱"。对偶问题=市场找最优价格；强对偶（gap=0）=无套利。KKT 条件读作：价格非负、无人为松弛约束付钱（互补松弛）、供需平衡（平稳性）。
2. **为什么凸性是分水岭**
   凸函数的切平面永远在下方——局部极小立即全局；加上 Slater 内点条件，对偶 gap 消失、KKT 从必要变充要。P12/P13 反面见证：非凸或整数约束下这些全部失效。凸性是"可解性"的经济学。
3. **为什么 prox/分裂算法统治稀疏学习**
   Lasso 的 ℓ1 不可微，但它的 prox 有闭式（软阈值）——"光滑部分走梯度、非光滑部分跳闭式"。ISTA/FISTA/ADMM 全是这个哲学的变奏；Moreau 恒等式把 prox 和投影配成一对互补工具。
4. **为什么变分法**
   优化对象从向量升级为曲线/函数——最速降线不是直线（0.4513 < 直线 0.6389）。Euler–Lagrange 方程就是无穷维的"导数为零"；Beltrami 恒等式是无外力时的能量守恒捷径。物理最小作用量、Neural ODE 的 adjoint 反传、最优控制的 Pontryagin 都在这里汇合。
5. **为什么 PL 条件重要**
   深度学习损失非凸不强凸，但很多仍线性收敛——PL 条件（损失下降速率被梯度平方控制）精确刻画"非凸但可几何收敛"的类。P10：Hessian 奇异的 3×20 最小二乘照样几何衰减——奇异≠病态，各向异性才是常态。
6. **为什么参数化决定可训练性**
   同一个函数类，不同参数坐标下梯度尺度天差地别——SP 参数化梯度随宽度 ×3.70 增长（最优 lr 必须缩），μP ×1.04（lr 可迁移）。优化难度不只由损失函数决定，还由"你用什么坐标写它"决定——这是 μP 学习率迁移的机制内核。

## 2. 定理网络（骨架，对齐 FOREST 域四 4.1/4.2/4.3）
- ★ **Fenchel–Young 不等式**
  f(x)+f*(s)≥sx 恒成立，共轭点取等。为什么真：f*(s) 就是 sup 的定义。Boyd §3.3。→ 关联：P1（(−ln x)*=−1−ln(−s) 精确取等）。
- ☆ **Fenchel 对偶/强对偶定理**
  凸问题 + Slater ⇒ p*=d*。为什么真：分离超平面在 epi f 与约束集之间。Boyd §5.2。→ 关联：P3 数值见证。
- ★ **LP 强对偶**
  线性规划恒有零 gap（无需 Slater，多面体精细结构）。为什么真：多面体的面结构保证对偶可达。Boyd。→ 关联：P2（p*=d*=2.8）。
- ★ **Slater 条件**
  相对内点可行点存在 ⇒ 凸问题强对偶 + 对偶最优可达。为什么真：内点让分离论证不退化。Boyd §5.2.3。→ 关联：P3（QP gap=0.00e+00）。
- ★ **KKT 条件**
  凸问题时必要⇔充分（平稳/原始可行/对偶可行/互补松弛）。为什么真：Lagrangian 鞍点=原对偶最优。Boyd §5.5.3。→ 关联：P4（活跃集 λ=[1,1,0]，λ₃=0 恰在活跃集外）。
- ☆ **弱对偶（一般陈述）**
  任何问题 d*≤p*，无需凸性。为什么真：min-max 交换放缩。→ 关联：P2 的对偶可行点 10.0≥2.8 见证。
- ★ **软阈值=prox_{λ|·|}**
  argmin ½(x−v)²+λ|x|=sign(v)max(|v|−λ,0)。为什么真：分情况求导。→ 关联：P5（|v|≤λ 精确归零=稀疏性来源）。
- ★ **Moreau 恒等式**
  prox_f(x)+prox_{f*}(x)=x。为什么真：共轭的次微分互逆。Bertsekas。→ 关联：P6（软阈值+区间投影=x，偏差 0）。
- ☆ **ISTA/FISTA 收敛率**
  ISTA O(1/k)、FISTA O(1/k²)（Nesterov 加速）；上界陈述。Beck–Teboulle（arXiv ID 待核）。→ 关联：P7 等预算分离 515962×。
- ★ **ADMM**
  分裂 x=w 的乘子交替方向法，收敛到鞍点。为什么真：Douglas–Rachford 分裂的不变式。Boyd et al. ADMM 专著。→ 关联：P8（与 FISTA 解差 2.4e-15 + Lasso KKT 双见证）。
- ★ **Euler–Lagrange + Beltrami 恒等式**
  泛函极值曲线满足 ∂L/∂y−d/dt(∂L/∂ẏ)=0；L 不显含 t 时 L−ẏ·∂L/∂ẏ=常数。Gelfand & Fomin。→ 关联：P9（最速降线 Beltrami 常数波动 1.1e-15）。
- ☆ **PL 条件 ⇒ GD 线性收敛**
  ½‖∇f‖²≥μ(f−f*) 时几何衰减，无需强凸。常见归于 Karimi–Nutini–Schmidt（arXiv ID 待核）。→ 关联：P10（3×20 行满秩，窗口内相邻比 0.4939 恒定，cv 0.0000）。
- ☆ **Nesterov 下界**
  一阶黑箱方法最坏情形 Ω(1/k²)——加速不是工程技巧而是信息论极限。Nocedal & Wright。→ 关联：与 FISTA 率配对读。
- ☆ **μP（Maximal Update Parametrization）**
  特定参数化下激活/梯度尺度宽度无关，最优 lr 可跨宽度迁移。Greg Yang Tensor Programs 系列（arXiv ID 待核）。→ 关联：P11 见证机制（×3.70 vs ×1.04）；[../BIDIRECTIONAL_FLYWHEEL.md](../BIDIRECTIONAL_FLYWHEEL.md) μP→P1 自举台账。

## 3. 反例与陷阱（模型见过最多人栽的坑）
1. ★ **错误直觉：KKT 点就是最优**
   反例：f=(x²−1)² s.t. x≤2，(0,0) 满足全部 KKT 但 f(0)=1>f(0.5)=0.5625（P12）。修正：非凸时 KKT 只必要；凸性缺失=鞍点/局部极小混入。
2. ★ **错误直觉：松弛不损失**
   反例：max x₁+x₂ s.t. x₁+x₂≤1.5, x∈{0,1}²——LP 松弛 1.5 vs 整数最优 1，gap=0.5（P13）。修正：整数约束破坏凸性，组合优化的对偶 gap 是本相不是数值误差。
3. ★ **错误直觉：加速方法的实测斜率=理论率**
   反例：病态 Lasso 上 FISTA 在支撑集识别后转入线性阶段，调参中实测 log-log 斜率 −3.5（远陡于 −2，未入正式脚本）。修正：O(1/k²) 是最坏情形上界，不是轨迹保证；速率实验要报告拟合窗口（本卡 P7 因此改为等预算分离断言）。
4. ★ **错误直觉：Hessian 奇异=收敛退化**
   反例：3×20 最小二乘零空间巨大，GD 损失仍几何衰减（P10 相邻比 0.4939，cv 0.0000）。修正：退化的方向若不含"损失曲率"就无害——PL 条件刻画精确边界；但 f=(x²−1)² 有平稳点不满足 PL（教师级陈述），非凸的账要逐点算。
5. ★ **参数化陷阱：同函数不同坐标，梯度尺度不同**
   SP 参数化梯度随宽度 ×3.70（最优 lr 必须随宽度缩），μP ×1.04（P11）。修正：谈"最优学习率"前先固定参数化；宽度扫描调 lr 的痛苦多数是 SP 的坐标系病。
6. ★ **数值消去陷阱**
   最速降线时间的 1−cos θ 项在 θ→0 时灾难性消去；改写 2sin²(θ/2) 后 Beltrami 常数波动 1.1e-15（P9 实修）。修正：涉三角差的浮点表达式先做半角恒等式改写。
7. ☆ **无约束≠无陷阱**
   非凸景观中"∇f=0"候选众多（鞍点/局部极大/平台），实践中靠噪声（SGD）逃离——理论保证要 PL/逃逸率分析，不能停留在驻点论证。
8. ★ **"参考最优"本身是构造物**
   验证收敛率需要 opt 的独立估计——P7 用 60000 步 FISTA 历史最小做参考（0.145429）；数值实验报告应写明真值来源与残余不确定性。

## 4. 计算验证（`experiments/dm_opt_check.py`，13/13 PASS）
- ★ P1：Fenchel–Young：f+f*−sx≥0 全网格成立且 x=−1/s 处 <1e-12 取等；|x|*=δ_[−1,1]（s=1/2 取等见证）
- ★ P2：LP 顶点枚举 p*=2.8；弱对偶 10.0≥p*；d*=2.8000000000000003，gap=0
- ★ P3：Slater QP p*=¼，数值 d*=0.25000000，gap=0.00e+00<1e-8
- ★ P4：KKT 活跃集反解 x*=(0,0)，λ=[1,1,0]≥0，平稳残差 0.0e+00，互补 0.0e+00
- ★ P5：软阈值=数值 argmin，最大偏差 2.0e-06；|v|≤λ 精确归零
- ★ P6：Moreau 恒等式网格最大偏差 0.0e+00
- ★ P7：病态 Lasso（cond≈10³）等预算 6000 步：ISTA 差距 2.89e-03 vs FISTA 5.59e-09，分离 515962×；k≥100 起 FISTA 目标恒低；参考最优 0.145429（60000 步）
- ★ P8：ADMM 与 FISTA 解差 2.4e-15；Lasso KKT：零分量 |(Aᵀr)ᵢ|≤λ（max 2.6876），非零分量 =λ（差 8.9e-15）
- ★ P9：最速降线 Beltrami 常数波动 1.1e-15；下降时间 摆线 0.4513<直线 0.6389<曲线 0.9781
- ★ P10：3×20（非强凸、行满秩）GD 几何衰减：窗口 32 点相邻比 0.4939（cv 0.0000），衰减 3.1e+09 倍，终值 0.0e+00
- ★ P11：两层线性网 SP 梯度尺度 ×3.70>2（lr 须随宽度缩）；μP ×1.04（0.5–2 内可迁移）
- ★ P12：非凸 KKT 点 (0,0) 全条件满足但 f(0)=1>f(0.5)=0.5625
- ★ P13：整数最优 1 vs LP 松弛 1.5，gap=0.5

## 5. 与 AI 的关联（FOREST 域四逐行对齐）
- **4.1 语言层（凸分析语法）**
  Fenchel 共轭=对偶的字母表；正则化训练的每一项（ℓ1/ℓ2/约束）都是 prox 结构——Lasso/弹性网/正则逻辑回归的统一读法（P5/P6/P8 一脉）。
- **4.2 算法层**
  SGD/momentum/Adam=随机近似梯度流（互链 ODE 卡动力系统视角）；ISTA/FISTA/ADMM=分裂哲学；学习率调度=步长规则；RLHF 的 KL 约束优化用 Fisher 度规（互链 [DM-GEO-01](DM-GEO-01-几何与拓扑.md) G10–G12）。
- **4.3 理论层**
  PL 条件=非凸可线性收敛类的边界（P10）；Nesterov 下界=一阶方法极限；μP=参数化几何决定训练动力学——[../BIDIRECTIONAL_FLYWHEEL.md](../BIDIRECTIONAL_FLYWHEEL.md) 自举台账第 4 行（μP→P1 首跑：SP 最优 η 漂移 3.5→1.5，μP 稳定区 43→100+ 步不发散，方向符合 Yang 理论）。
- **变分法三向出口**
  Neural ODE adjoint 反传=变分恒等式（互链 [DM-ODE-01](DM-ODE-01-微分方程与动力系统.md)）；物理最小作用量（讲透物理侧）；最优控制/Pontryagin（RL 的形式母体）。
- **LoRA/低秩约束**
  参数高效微调=低秩可行集上的优化——约束优化的当代最大应用场景之一。
- 基础互链：数值实现（线搜索/BFGS）→[DM-NUMA-01](DM-NUMA-01-数值分析.md)；凸分析严格化（次微分）→[DM-REAL-01](DM-REAL-01-实分析与测度.md)。

## 6. ZDP 学习路径
- 入门：Boyd & Vandenberghe《Convex Optimization》（免费 PDF + Stanford 公开课）——本卡 §1–§2 几乎全部内容的现代母本，习题即工程。
- 进阶：Nocedal & Wright《Numerical Optimization》（算法层：线搜索/信任域/共轭梯度/内点）；Gelfand & Fomin《Calculus of Variations》（变分法薄而全）。
- 研究：Bertsekas《Convex Analysis and Optimization》/ Rockafellar《Convex Analysis》（次微分机器）；加速方法一手文献从 Nesterov 专著进（引文本卡一律待核 ID 后补）。
- 工具：本卡实验全部 NumPy 手写（无 scipy/cvxpy 依赖），任何 numpy≥1.26 环境可复现；本机 LAPACK 100×100 解方程病态（约 1s/次），脚本已用预逆+matvec 绕开（见 §3-6 数值坑）。

## 7. 教材锚点
- [../TEXTBOOK_LIBRARY.md](../TEXTBOOK_LIBRARY.md) §7.4（优化：Boyd & Vandenberghe / Nocedal & Wright / Bertsekas）
- [../TEXTBOOK_LIBRARY.md](../TEXTBOOK_LIBRARY.md) §11.3（变分法/数学物理相关条目）
- 注：Gelfand & Fomin、Beck–Teboulle、Karimi–Nutini–Schmidt、Tensor Programs 不在教材库内，属本卡补充推荐且 arXiv ID 待核；方法论见 [./METHODOLOGY.md](METHODOLOGY.md)，篇目见 [./README.md](README.md)
