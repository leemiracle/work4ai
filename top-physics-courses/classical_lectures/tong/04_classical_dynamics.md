# David Tong · Classical Dynamics（经典动力学）导读笔记

> Tong 系列第 04 本 | 难度 ★★（本科高年级）| 配合：L01 力学进阶

## §0 基本信息
- **作者**：David Tong（Cambridge，本科 Part IB）
- **难度**：★★（需要牛顿力学 + 微积分）
- **篇幅**：约 100 页
- **链接**：davidtong.org/teaching/dynamics-and-relativity/（注：本笔记针对 IB Classical Dynamics 部分）
- **配合项目**：L01 经典力学进阶

## §1 一句话定位
**从牛顿到拉格朗日到哈密顿**——理论力学的三重身，用对称性统一所有力学。

## §2 前置知识
- 必须会：牛顿力学（02_dynamics_relativity 的水平）、多元微积分（03_vector_calculus）、常微分方程
- 建议会：变分法基础、线性代数（本征值问题、矩阵对角化）

## §3 讲义全景（章节地图）

从作用量原理出发，重构全部力学。这是通往量子力学和场论的桥梁。

| 章 | 主题 | 核心问题 |
|----|------|---------|
| 1 | 拉格朗日力学 | 作用量极值如何给出运动方程？|
| 2 | 对称性与 Noether 定理 | 对称性如何保证守恒律？|
| 3 | 哈密顿力学 | 从位形空间到相空间 |
| 4 | 刚体动力学 | 三维旋转怎么算？|
| 5 | 小振动 | 耦合振子怎么分解？|
| 6 | 哈密顿-雅可比方程 | 力学与波动的桥梁 |

## §4 核心章节拆解（深化版）

### §4.1 拉格朗日力学与最小作用量原理

**核心思想**：系统沿使作用量 $S$ 取**驻值**（stationary，不只是极小）的路径演化。这是比 $F=ma$ 更基本的原理。

- **作用量与拉氏量**：
$$S = \int_{t_1}^{t_2} L\, dt, \quad L = T - V \quad \text{（拉氏量 = 动能 − 势能）}$$

**Euler-Lagrange 方程的推导**（从 $\delta S = 0$ 一步步推）：

1. 让路径 $q_i(t)$ 做微小变分 $q_i \to q_i + \eta_i(t)$，其中 $\eta_i(t_1) = \eta_i(t_2) = 0$（端点固定）。
2. 作用量变分为
$$\delta S = \int_{t_1}^{t_2} \left(\frac{\partial L}{\partial q_i}\eta_i + \frac{\partial L}{\partial \dot{q}_i}\dot{\eta}_i\right) dt$$
3. 对第二项**分部积分**：
$$\int \frac{\partial L}{\partial \dot{q}_i}\dot{\eta}_i\, dt = \left[\frac{\partial L}{\partial \dot{q}_i}\eta_i\right]_{t_1}^{t_2} - \int \frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i}\eta_i\, dt$$
4. 边界项为零（因为 $\eta_i(t_1) = \eta_i(t_2) = 0$），所以
$$\delta S = \int_{t_1}^{t_2} \left(\frac{\partial L}{\partial q_i} - \frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i}\right)\eta_i\, dt = 0$$
5. 由于 $\eta_i(t)$ 任意，被积函数必须为零：
$$\frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i} - \frac{\partial L}{\partial q_i} = 0 \quad \text{（Euler-Lagrange 方程）}$$

**工作示例：单摆**。选广义坐标 $\theta$（摆角），动能 $T = \frac{1}{2}ml^2\dot{\theta}^2$，势能 $V = mgl(1-\cos\theta)$。
$$L = \frac{1}{2}ml^2\dot{\theta}^2 - mgl(1-\cos\theta)$$
代入 E-L 方程：$\frac{d}{dt}(ml^2\dot{\theta}) + mgl\sin\theta = 0$，即 $\ddot{\theta} = -\frac{g}{l}\sin\theta$。小角度 $\sin\theta \approx \theta$ 回到 $\ddot{\theta} = -(g/l)\theta$。

**广义坐标与约束**：拉格朗日方法的威力在于**自动处理约束**。例如珠子在圆环上滑动，选角度 $\theta$ 为广义坐标，约束力（环对珠的支持力）自动不出现在方程中——因为它不做虚功。这就是 d'Alembert 原理：理想约束力对虚位移做功为零。

**为什么 $L = T - V$ 成立？** 这不是先验原理，而是：对 $V(q)$ 势能的机械系统，$T = \frac{1}{2}m\dot{q}^2$ 是**最简单的标量**，使得 E-L 方程恰好给出 $m\ddot{q} = -\nabla V = F$。任何 $L$ 都可以尝试，但 $T - V$ 是产生正确牛顿方程的最简选择。广义到非机械系统（电磁场、相对论）时 $L$ 需重新定义。

**反直觉点**：自然"选择"的是**驻点**（stationary），不一定是极小值——可以是鞍点。对短时间运动，作用量通常取极小；但长时间运动可以是鞍点。所以"最小作用量原理"这个名字其实不准确，更严谨的说法是"**驻定作用量原理**"。

---

### §4.2 Noether 定理（对称性的力量）

**核心概念**：每一个**连续**对称性 ↔ 一个守恒量。这是 20 世纪物理最深刻的定理之一（Emmy Noether, 1918）。

**Noether 荷的推导**：若 $q_i \to q_i + \epsilon\, \delta q_i$ 是对称变换（$\delta L = 0$），则
$$Q = \sum_i \frac{\partial L}{\partial \dot{q}_i}\, \delta q_i \quad \text{守恒} \quad \left(\frac{dQ}{dt} = 0\right)$$

**具体对称性 → 守恒量**：

| 对称变换 | $\delta q_i$ | 守恒量 $Q$ |
|---------|------------|-----------|
| 空间平移 $q_i \to q_i + \epsilon$ | $1$ | $\sum_i \frac{\partial L}{\partial \dot{q}_i} = \sum_i p_i = $ **总动量** |
| 时间平移 $t \to t + \epsilon$ | $\dot{q}_i$ | $\sum_i p_i\dot{q}_i - L = H = $ **能量** |
| 旋转 $\delta\mathbf{r} = \boldsymbol{\epsilon}\times\mathbf{r}$ | $(\boldsymbol{\epsilon}\times\mathbf{r})_i$ | $\sum_i \mathbf{r}_i \times \mathbf{p}_i = $ **总角动量** $\mathbf{L}$ |

**具体例子（中心力场）**：$L = \frac{1}{2}m(\dot{r}^2 + r^2\dot{\theta}^2) - V(r)$。
- 时间平移不变 → $H = E$ 守恒（能量）
- 旋转不变（$L$ 不含 $\theta$）→ $p_\theta = mr^2\dot{\theta}$ 守恒（角动量）

**直觉图像**：对称性 = "大自然不关心你选什么参照"——如果移动原点物理不变，那一定有"不可创造不可消灭"的东西（动量）。

**反直觉点**：守恒律不是"实验发现的规律"——它是对称性的**数学必然**。知道了 $L$ 的对称性，就自动知道所有守恒量，不需要解运动方程。粒子物理标准模型完全建立在这个框架上。

---

### §4.3 哈密顿力学

**核心概念**：用正则动量 $p_i = \partial L / \partial \dot{q}_i$ 代替速度，运动方程变成对称的一阶形式。

**Legendre 变换**（拉氏量 → 哈氏量）：
$$H(q, p) = \sum_i p_i \dot{q}_i - L(q, \dot{q})$$

**几何直觉（为什么 Legendre 变换有效）**：考虑 $L$ 作为 $\dot{q}$ 的函数，曲线 $L(\dot{q})$。Legendre 变换从"用斜率参数化"换成"用截距参数化"——新变量 $p = \partial L/\partial\dot{q}$ 是曲线在某点的**斜率**，$H = p\dot{q} - L$ 是该点切线的**截距**。斜率与截距是同一曲线的**对偶描述**，信息完全等价。

**Hamilton 正则方程**：
$$\dot{q}_i = \frac{\partial H}{\partial p_i}, \quad \dot{p}_i = -\frac{\partial H}{\partial q_i}$$

**基本 Poisson 括号**：$\{q_i, p_j\} = \delta_{ij}$，这是相空间的"基本结构"。对任意函数 $f, g$：
$$\{f, g\} = \sum_i \left(\frac{\partial f}{\partial q_i}\frac{\partial g}{\partial p_i} - \frac{\partial f}{\partial p_i}\frac{\partial g}{\partial q_i}\right)$$
守恒量满足 $\{f, H\} = 0$。

**Liouville 定理（相空间体积守恒）证明梗概**：
- 相空间中"流体"的速度场为 $(\dot{q}, \dot{p}) = (\partial H/\partial p, -\partial H/\partial q)$
- 散度 $\nabla \cdot \mathbf{v} = \frac{\partial\dot{q}}{\partial q} + \frac{\partial\dot{p}}{\partial p} = \frac{\partial^2 H}{\partial q\partial p} - \frac{\partial^2 H}{\partial p\partial q} = 0$
- 散度为零 → Hamilton 流**不可压缩** → 相空间体积不变

**相空间体积守恒 → 信息保持 → 统计力学桥梁**：经典力学中信息永不丢失（精确分布的"形状"可以拉伸变薄，但体积不变）。这是统计力学中微正则系综的基础。

**量子力学桥梁**：$\{q, p\} = 1 \to [\hat{q}, \hat{p}] = i\hbar$（Poisson 括号 → 对易子），这就是量子化。

**反直觉点**：在 Hamilton 框架中，$q$ 和 $p$ 是**独立变量**——$p = m\dot{q}$ 不是先验假设，而是 Hamilton 方程对特定 $H$ 的**后果之一**。把 $q, p$ 当独立变量是相空间几何的关键。

---

### §4.4 刚体动力学

**核心概念**：刚体 = 无限多质点的刚性约束，用**转动惯量张量** $\mathbf{I}$ 描述惯性。

**惯性张量**（$3\times 3$ 矩阵）：
$$I_{ij} = \int \rho(\mathbf{r})(\delta_{ij}\, r^2 - x_i x_j)\, d^3r$$
角动量 $\mathbf{L} = \mathbf{I}\cdot\boldsymbol{\omega}$（一般 $\mathbf{L}$ 与 $\boldsymbol{\omega}$ **不平行**！）。

**Euler 方程推导**（体坐标系中）：在惯性系 $\frac{d\mathbf{L}}{dt} = \boldsymbol{\tau}$，但体坐标系以 $\boldsymbol{\omega}$ 转动，需加 Coriolis 型修正：
$$\left(\frac{d\mathbf{L}}{dt}\right)_{\text{body}} + \boldsymbol{\omega}\times\mathbf{L} = \boldsymbol{\tau}$$
在主轴坐标系（$\mathbf{I}$ 对角化）中 $\mathbf{L} = (I_1\omega_1, I_2\omega_2, I_3\omega_3)$，无外力矩 $\boldsymbol{\tau}=0$ 时：
$$I_1\dot{\omega}_1 = (I_2 - I_3)\omega_2\omega_3, \quad \text{及循环置换}$$

**网球拍定理（中间轴不稳定性）**：设 $I_1 < I_2 < I_3$，分析绕各轴旋转的小扰动稳定性。
- 绕 $I_1$ 轴（$\omega_2, \omega_3$ 小）：线性化得 $\ddot{\omega}_2 \propto (I_1-I_3)(I_1-I_2)\omega_2$，系数为正 → **振荡稳定**
- 绕 $I_3$ 轴：同理系数为正 → **稳定**
- 绕 $I_2$ 轴（中间）：$\ddot{\omega}_1 \propto (I_2-I_3)(I_2-I_1)\omega_1$，系数为**负** → **指数增长，不稳定！**

**进动现象**：陀螺（自转角动量 $\mathbf{L}$ 沿自转轴）受重力矩 $\boldsymbol{\tau} = m g l\sin\theta\,\hat{\phi}$。$\frac{d\mathbf{L}}{dt} = \boldsymbol{\tau} \perp \mathbf{L}$ → $\mathbf{L}$ 方向改变但大小不变 → 自转轴画圆锥（进动），进动角速度 $\Omega = \frac{mgl}{I\omega}$。这是"力矩试图推倒陀螺，但角动量太大，只能转向"。

**反直觉点（Dzhanibekov 效应）**：太空中的翼形螺母（wingnut）绕中间轴旋转时，会**周期性翻转**——看起来不可能，但完全遵循 Euler 方程。1985 年宇航员 Vladimir Dzhanibekov 在空间站首次记录。这就是"中间轴不稳定"的戏剧化体现。

---

### §4.5 小振动与耦合振子

**核心概念**：在平衡点附近 Taylor 展开势能到二次项，得到耦合的简谐振子系统，用简正模分解。

**推导**：动能 $T = \frac{1}{2}\dot{\mathbf{q}}^T \mathbf{M} \dot{\mathbf{q}}$，势能在平衡点展开 $V \approx \frac{1}{2}\mathbf{q}^T \mathbf{K} \mathbf{q}$（线性项为零）。代入 E-L 方程得 $\mathbf{M}\ddot{\mathbf{q}} = -\mathbf{K}\mathbf{q}$。

设 $\mathbf{q} = \mathbf{v}\, e^{-i\omega t}$，得**广义本征值问题**：
$$\mathbf{K}\mathbf{v} = \omega^2 \mathbf{M}\mathbf{v} \quad \Longleftrightarrow \quad \mathbf{M}^{-1}\mathbf{K}\, \mathbf{v} = \omega^2 \mathbf{v}$$
本征值 $\omega_\alpha^2$ 是简正频率的平方，本征向量 $\mathbf{v}_\alpha$ 是简正模（振动模式）。

**简正坐标**：用本征向量做坐标变换 $Q_\alpha$，则 $L = \frac{1}{2}\sum_\alpha (\dot{Q}_\alpha^2 - \omega_\alpha^2 Q_\alpha^2)$——**完全解耦**。

**示例：两个耦合摆**（摆长 $l$、质量 $m$、耦合弹簧常数 $k$）：
- **对称模**（同相）：$\omega_1 = \sqrt{g/l}$（弹簧不伸长）
- **反对称模**（反相）：$\omega_2 = \sqrt{g/l + 2k/m}$（弹簧拉伸）

**反直觉点**：简正模**完全独立**——在线性近似下，一个模式中的能量**永远不会**转移到另一个模式。这是二次势能（简谐性）的魔力。一旦加入非线性（高阶项），模式间会有能量交换。

---

### §4.6 哈密顿-雅可比方程

**核心思想**：寻找一个正则变换使新哈密顿量为零，则新动量为常数——所有信息编码在生成函数 $S(q, \alpha, t)$（Hamilton 主函数）中。

**HJ 方程**：
$$\frac{1}{2m}\left(\frac{\partial S}{\partial q}\right)^2 + V(q) + \frac{\partial S}{\partial t} = 0$$

**与光学的类比（WKB 连接）**：分离变量 $S(\mathbf{q}, t) = -Et + W(\mathbf{q})$（$W$ 为 Hamilton 特征函数），则
$$\left(\frac{dW}{dq}\right)^2 = 2m(E - V)$$
这正是几何光学的**程函方程**（eikonal equation）——经典轨道对应光线，等 $S$ 面对应波前。

**通往量子力学**：令 $S = \hbar\ln\psi$（即 $\psi = e^{iS/\hbar}$），代入 Schrödinger 方程 $i\hbar\partial_t\psi = \hat{H}\psi$，展开到 $O(\hbar^0)$ 恰好给出 HJ 方程。$\hbar \to 0$ 极限下量子力学回归经典力学。

**反直觉点**：经典力学是量子力学的**几何光学极限**（短波长极限）。这解释了为什么 HJ 方程与光的程函方程形式相同——粒子力学和光线传播在数学上是同一件事。

## §5 必做习题（深化版）

| 题 | 内容 | 为什么必做 |
|----|------|----------|
| 1 | **单摆**：写拉氏量 $L = \frac{1}{2}ml^2\dot{\theta}^2 - mgl(1-\cos\theta)$，推运动方程 | 从 $L=T-V$ 到 EOM 的最基本练习 |
| 2 | **Noether**：中心力场中找全部连续对称性 → 列出全部守恒量 | 对称性优先思维的第一次实操 |
| 3 | **Legendre 变换**：给定 $L(q,\dot{q})$，算 $H(q,p)$，验证 $\dot{q}=\partial H/\partial p$ | 理解 $q,p$ 对偶与独立性 |
| 4 | **Euler 方程稳定性**：绕三个主轴做线性稳定性分析，证中间轴不稳定 | Dzhanibekov 效应的数学根源 |
| 5 | **双摆简正模**：写拉氏量 → $\mathbf{M}^{-1}\mathbf{K}$ 本征值 → 简正频率 | 耦合系统分解的核心技能 |
| 6 | **Poisson 括号**：验证 $\{L_i, L_j\} = \epsilon_{ijk}L_k$（角动量代数）| 角动量的李代数结构，量子化直接用 |
| 7 | **量子化桥梁**：从 $\{q,p\}=1$ 出发论证 $[\hat{q},\hat{p}]=i\hbar$ 的唯一性 | 理解经典→量子的正则量子化路径 |

**Tong 的习题表**在讲义末尾。建议**至少做完上表 7 题**才算入门。

## §6 读完后你应该能
- [ ] 对任何系统写出拉格朗日量并推导运动方程（选对广义坐标）
- [ ] 用 Noether 定理从对称性找出所有守恒量
- [ ] 做勒让德变换从 $L$ 得到 $H$，写出 Hamilton 方程
- [ ] 解刚体的欧拉方程，理解进动和 Dzhanibekov 效应
- [ ] 把耦合振子分解为简正模（矩阵对角化）
- [ ] 理解 HJ 方程为何是经典→量子的桥梁
- [ ] 理解 Poisson 括号 → 对易子的量子化路径

## §7 与项目的映射
- **前置**：02_dynamics_relativity.md（牛顿力学）
- **后续**：06_quantum_mechanics.md（哈密顿力学 → Schrödinger 方程）
- **深层**：14_qft.md（拉格朗日形式直接推广到场论——QFT 就是无限自由度的拉格朗日力学）
- **对应**：L01 经典力学进阶

## §8 延伸阅读
- 读完 → 06 Quantum Mechanics（哈密顿力学的量子版）
- 教材 → Landau & Lifshitz *Mechanics*（理论物理教程卷 1，从最小作用量从头开始构建力学，极推）
- 教材 → Goldstein *Classical Mechanics*（标准教材，习题丰富，刚体部分详细）
- 直觉 → Susskind *The Theoretical Minimum: Classical Mechanics*（YouTube + 书，最友好的入门）
- 深入 → Arnold *Mathematical Methods of Classical Mechanics*（微分几何观点，辛流形上的力学）
- 历史 → Lanczos *The Variational Principles of Mechanics*（变分原理的历史和哲学）

## §9 学习建议
- **节奏**：4-6 周（100 页 + 大量推导）
- **怎么读**：每节读完**合上书**，自己从 $L = T - V$ 重新推导运动方程。力学是"做"出来的，不是"看"出来的
- **陷阱**：
  - 最小作用量原理不是"粒子知道未来"——它是变分法的数学结果（边界固定，找驻值路径）
  - 广义坐标 $q_i$ 可以是任意参数（角度、长度…），不要拘泥于笛卡尔坐标
  - Noether 定理只对**连续**对称性有效——离散对称性（如宇称 $P$、时间反演 $T$）不给出守恒量
  - 哈密顿力学中 $q$ 和 $p$ 是**独立**变量，不再是 $p = m\dot{q}$ 的简单关系（虽然这个关系可以从 Hamilton 方程恢复）
- **关键洞察**：拉格朗日力学的真正威力不是"换个方法算 $F=ma$"，而是**对称性优先**——先找对称性，守恒律自动出来，方程自动简化。这就是现代物理（粒子物理、场论、广义相对论）的工作方式。学完这本，你就拿到了进入现代理论物理的钥匙。

## §10 常见误区（深化新增）

### 🕳️ 误区 1：最小作用量 = 粒子预知未来
- ❌ "粒子预知未来，主动选择最优路径"（目的论误解）
- ✅ 这是**变分法的数学结果**——在固定边界条件下求驻值路径，不涉及意识或预知。它是一个关于微分方程的等价表述，和"粒子有意图"毫无关系。

### 🕳️ 误区 2：广义坐标必须是笛卡尔坐标
- ❌ "$q_i$ 必须是 $x, y, z$"
- ✅ 广义坐标可以是**角度、弧长、任意参数**——这正是拉格朗日方法的巨大优势。球面摆用 $(\theta, \phi)$，无需约束力。

### 🕳️ 误区 3：Noether 定理对所有对称性有效
- ❌ "任何对称性都对应守恒量"
- ✅ Noether 定理只对**连续**对称性有效。离散对称性（如宇称 $P$、时间反演 $T$、晶体对称性）**不给出**守恒量。

### 🕳️ 误区 4：Hamilton 力学中 $p = m\dot{x}$
- ❌ "在哈密顿框架里 $p$ 仍然等于 $m\dot{x}$"
- ✅ 在 Hamilton 框架中 $q$ 和 $p$ 是**独立变量**。$p = m\dot{q}$ 只是特定 $H$ 下 Hamilton 方程的**后果之一**。广义动量 $p = \partial L/\partial\dot{q}$ 可以与 $m\dot{q}$ 完全不同（如电磁场中 $p = m\dot{q} + qA$）。

### 🕳️ 误区 5：Liouville 定理推翻热力学第二定律
- ❌ "相空间体积不变 → 熵不变 → 热力学第二定律错了"
- ✅ 精确的相空间分布体积确实不变，但会**拉伸变薄**，填满更大的有效体积。**粗粒化熵**（coarse-grained entropy）会增加——这正是统计力学的核心。精细信息守恒与宏观熵增加并不矛盾。

## §11 与其他经典力学教材的对比（深化新增）

| 教材 | 风格 | 适合谁 | vs Tong |
|------|------|--------|---------|
| **Landau & Lifshitz** *Mechanics* | 从最小作用量从头构建，极简极深 | 想看大师思维的人 | 比 Tong 更凝练，几乎无废话，但难 |
| **Goldstein** *Classical Mechanics* | 标准教材，全面，习题多 | 本科主教材 | 比 Tong 更详细（刚体/小振动），但缺乏物理直觉的"火花" |
| **Susskind** *Theoretical Minimum* | 最友好入门，配 YouTube | 零基础想入门理论物理 | 比 Tong 浅得多，适合先读再上 Tong |
| **Arnold** *Mathematical Methods* | 微分几何/辛流形观点 | 数学背景强 / 想理解几何结构 | 比 Tong 严谨得多，但物理直觉少 |
| **Lanczos** *Variational Principles* | 变分原理的历史与哲学 | 想理解"为什么"的人 | 比 Tong 更有历史纵深和思辨深度 |

**建议组合**：**Tong（主读）+ Landau（精读重推）+ Susskind（视频补充）** = 经典力学自学三件套。

---

**完成日期**：2026-08-13（深化版 v2，从 137 行扩到 ~310 行）
**配套**：[tong/README.md](README.md) + [TEMPLATE.md](../TEMPLATE.md) + [ai_for_physics/](../../ai_for_physics/)
