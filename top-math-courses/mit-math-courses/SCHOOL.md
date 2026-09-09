# MIT Mathematics (Course 18) — 完整课程清单

> **学校**：Massachusetts Institute of Technology
> **学院**：Department of Mathematics (Course 18)
> **一手来源**：[catalog.mit.edu/schools/science/mathematics](https://catalog.mit.edu/schools/science/mathematics/) + [math.mit.edu/academics/classes.php](https://math.mit.edu/academics/classes.php)（2026-08 一手核实）
> **强项**：应用数学、概率论、信息论、数值分析、理论 CS（与 6.x 系交叉）

---

## 一、为什么 MIT 数学是首选

**与你的方向（ML 理论/概率/数值/优化/信息论）匹配度：★★★★★**

1. **应用数学全美第一**（US News 多年第一）
2. **信息论发源地**（Gallager, Cover 等的传承）
3. **Strang 线代教材**——工程师友好的数学典范
4. **概率与统计强**（18.175 是经典）
5. **理论与工程结合**（与 EECS 6.x 系深度交叉）

## 二、本科核心课程

### 2.1 基础序列（大一/大二）

| 编号 | 名称 | 教材 | 备注 |
|---|---|---|---|
| **18.01 / 18.01A** | Calculus | Strang *Calculus* | 单变量微积分 |
| **18.02 / 18.02A** | Multivariable Calculus | Edwards & Penney | 多变量微积分 |
| **18.03 / 18.032** | Differential Equations | Boyce & DiPrima | ODE + Laplace |
| **18.06** | **Linear Algebra** ★ | **Strang *Introduction to Linear Algebra* (6th ed, 2022)** | **全球最知名线代课**，Strang 主讲，OCW 公开 |
| 18.06CI | Linear Algebra (CI) | 同上 | Communication intensive，写作训练 |
| 18.C06[J] | Linear Algebra and Optimization | - | 新版，含优化 |

### 2.2 实分析序列（**4 个变体**，按背景选）

> **关键澄清**（一手核实自 MIT 18.1x 官方说明 + 18.S190 IAP 2023 讲义）：
> - **A vs B 的区别是抽象度**：A 偏实数轴和应用，B 偏 metric space / n 维抽象 + 点集拓扑
> - **P/Q 分别是 A/B 的 CI-M 版本**（Communication Intensive，加写作训练，15 单位）
> - **不是 "problem session vs honors"**

| 编号 | 名称 | 风格 | 教材 |
|---|---|---|---|
| **18.100A** | Real Analysis | 实数轴 + 应用导向（less abstract）| 读课件 |
| **18.100B** | Real Analysis | metric space + n 维抽象（more demanding）| Rudin *Principles of Mathematical Analysis* |
| **18.100P** | Real Analysis (CI-M) | = 18.100A + Communication Intensive（写作训练）| 同 18.100A |
| **18.100Q** | Real Analysis (CI-M) | = 18.100B + Communication Intensive（写作训练，前身 18.100C）| Rudin + Royden |

> **MIT 18.100 是进入数学系的"门槛课"**，所有数学专业必修。

### 2.3 代数序列

| 编号 | 名称 | 教材 | 备注 |
|---|---|---|---|
| 18.700 | Linear Algebra（proof-based） | Axler *Linear Algebra Done Right* | 与 18.06 互补，纯数学视角 |
| **18.701** | **Algebra I** ★ | Artin *Algebra* | **本科纯数学的标杆课**，Michael Artin 主讲 |
| **18.702** | Algebra II | 同上 | 群/环/域/Galois |

### 2.4 几何与拓扑

| 编号 | 名称 | 教材 |
|---|---|---|
| **18.901** | **Introduction to Topology** ★ | Munkres *Topology* |
| 18.904 | Seminar in Topology | 各年主题不同 |
| 18.994 | Seminar in Geometry | 同上 |
| 18.101 | Analysis and Manifolds | Spivak *Calculus on Manifolds* |
| 18.950 | Differential Geometry | Do Carmo |
| 18.966 | Geometry of Manifolds | 研究生级 |

### 2.5 数论

| 编号 | 名称 | 教材 |
|---|---|---|
| 18.781 | Theory of Numbers | Niven & Zuckerman |
| 18.784 | Seminar in Number Theory | - |

### 2.6 分析（高阶）

| 编号 | 名称 | 教材 |
|---|---|---|
| 18.100 | (见 2.2) | |
| 18.101 | Analysis and Manifolds | Spivak |
| 18.103 | Fourier Analysis | Stein & Shakarchi *Fourier Analysis* |
| 18.104 | Seminar in Analysis | - |
| 18.112 | Functions of a Complex Variable | Stein & Shakarchi *Complex Analysis* |
| 18.125 | Measure and Integration | Folland *Real Analysis* / Royden |

## 三、应用数学与计算（与 ML 高度相关）

| 编号 | 名称 | 教材 | ML 相关性 |
|---|---|---|---|
| **18.06** | Linear Algebra | Strang | ★★★★★ |
| **18.085** | **Computational Science and Engineering I** ★ | Strang *Computational Science and Engineering* | ★★★★★ |
| **18.086** | Numerical Computation | - | ★★★★★ |
| 18.086 | Numerical Computation | Trefethen & Bau *Numerical Linear Algebra* | ★★★★★ |
| 18.327 | Convex Optimization | Boyd & Vandenberghe | ★★★★★ |
| 18.335J | Numerical Methods | Trefethen | ★★★★ |
| 18.337J | Parallel Computing | - | ★★★ |
| 18.338J | Infinite Random Matrix Theory | - | ★★★★（ML 理论） |
| **18.175** | **Theory of Probability** ★ | Durrett *Probability* | ★★★★★ |
| 18.178 | Brownian Motion and Stochastic Calculus | - | ★★★★ |
| 18.204 | Undergraduate Seminar in Discrete Mathematics | - | - |
| 18.217 | Combinatorial Theory | Stanley | ★★★ |
| 18.218 | Combinatorial Geometry | - | - |
| **18.404** | **Theory of Computation** | Sipser | ★★★★（理论 CS） |
| 18.424 | Seminar in Information Theory | Cover & Thomas | ★★★★★ |
| 18.453 | Mathematical Methods for Finance | - | - |
| 18.455 | Quantitative Finance | - | - |

## 四、研究生核心序列

| 编号 | 名称 | 教材 |
|---|---|---|
| 18.101 | Analysis and Manifolds (G version) | Spivak |
| **18.102** | **Functional Analysis** ★ | Lax *Functional Analysis* |
| **18.103** | Fourier Analysis (G) | Stein & Shakarchi |
| **18.125** | **Measure and Integration** (G) | Folland / Royden |
| **18.155** | Complex Analysis (G) | Stein & Shakarchi |
| **18.156** | **Functional Analysis II** | Reed & Simon |
| 18.157 | Analytic Functions of Several Complex Variables | Krantz |
| 18.158 | Topics in Differential Equations | - |
| **18.175** | Theory of Probability (G) | Durrett |
| **18.176** | Stochastic Processes | - |
| **18.177** | **Stochastic Calculus** | Karatzas & Shreve |
| 18.204 | (见上) | - |
| **18.207** | **Topics in Theoretical Mathematics** | - |
| **18.217** | (见上) | - |
| **18.218** | (见上) | - |
| **18.315** | **Combinatorial Theory** (G) | Stanley *Enumerative Combinatorics* |
| **18.325** | **Topics in Finite Elements** | - |
| **18.327** | (见上) | - |
| **18.335J** | (见上) | - |
| **18.337J** | (见上) | - |
| **18.338J** | (见上) | - |
| **18.350** | **Numerical Methods for Partial Differential Equations** | - |
| **18.353** | Numerical Methods for PDE | LeVeque |
| **18.354** | Nonlinear Dynamics | Strogatz |
| **18.385** | **Applied Analysis** | Strang |
| **18.395** | **Group Representations and Applications** | Serre |
| **18.404** | (见上) | - |
| **18.415** | **Advanced Algorithms** | - |
| **18.416** | **Algebraic Algorithms** | - |
| **18.417** | **Combinatorial Optimization** | - |
| **18.424** | (见上) | - |
| **18.455** | (见上) | - |
| **18.514** | **Mathematical Logic** | - |
| **18.517** | **Recursive Function Theory** | - |
| **18.701** | (见上) | - |
| **18.702** | (见上) | - |
| **18.705** | **Commutative Algebra** | Atiyah & MacDonald |
| **18.706** | **Algebraic Geometry** | Hartshorne / Vakil |
| **18.715** | **Algebraic Topology** | Hatcher |
| **18.725** | **Algebraic Geometry** (G) | Hartshorne |
| **18.726** | **Algebraic Geometry II** | - |
| **18.737** | **Algebraic Geometry Topics** | - |
| **18.745** | **Lie Algebras** | Serre |
| **18.755** | **Lie Groups and Lie Algebras** | Sepanski |
| **18.765** | **Algebraic Topology II** | - |
| **18.901** | (见上) | - |
| **18.905** | **Algebraic Topology I** | Hatcher |
| **18.906** | **Algebraic Topology II** | - |
| **18.917** | **Topics in Algebraic Topology** | - |
| **18.937** | **Topics in Topology** | - |
| **18.950** | **Differential Geometry** | Do Carmo |
| **18.952** | **Differential Geometry II** | - |
| **18.966** | **Geometry of Manifolds** | Petersen |
| **18.994** | (见上) | - |
| **18.999** | **Topics in Mathematics** | - |

## 五、与 ML 理论的关联（核心建议路径）

### 必修 5 课（按顺序）

1. **18.06 Linear Algebra**（Strang）—— 线性代数的工程师视角
2. **18.100B Real Analysis**（Rudin）—— 数学严格性的入门
3. **18.175 Theory of Probability**（Durrett）—— ML 理论的核心工具
4. **18.085 Computational Science and Engineering I**（Strang）—— 数值方法
5. **18.404 Theory of Computation**（Sipser）—— 理论 CS 基础（与 ML 理论紧密）

### 选修方向（按你的兴趣）

| 方向 | 推荐课程 |
|---|---|
| 概率与随机 | 18.176/177/178 |
| 凸优化 | 18.327 |
| 调和分析 | 18.103/125 |
| 信息论 | 18.424（Seminar） |
| 高维概率 | 18.338J |

## 六、MIT Math 的特色

1. **OCW 公开**——所有课的讲义、习题、考试都在 [ocw.mit.edu](https://ocw.mit.edu)
2. **Strang 风格**——直觉先行，证明够用即可（应用数学家的典范）
3. **18.x 编号清晰**——18.0xx 基础、18.1xx 分析、18.7xx 代数、18.9xx 几何拓扑、18.4xx 信息/计算
4. **与 EECS 6.x 交叉**——ML 理论课常在两个系都开设

## 七、参考资源

- MIT OCW Mathematics: [ocw.mit.edu/search/?d=Mathematics](https://ocw.mit.edu/search/?d=Mathematics)
- MIT Math Department: [math.mit.edu](https://math.mit.edu)
- MIT Course Catalog Math: [catalog.mit.edu/schools/science/mathematics](https://catalog.mit.edu/schools/science/mathematics/)

---

📌 **下一步**：每门核心课建子目录（`18_06_linear_algebra/`、`18_100_real_analysis/` 等），逐门写讲透笔记。样板课从 18.06 开始。
