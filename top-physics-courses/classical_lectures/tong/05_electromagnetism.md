# David Tong · Electromagnetism（电磁学）导读笔记

> Tong 系列第 05 本 | 难度 ★★（本科核心）| 配合：L02 电磁学

## §0 基本信息
- **作者**：David Tong（Cambridge，本科 Part IB）
- **难度**：★★（需要矢量微积分 + 基本微分方程）
- **篇幅**：约 155 页
- **链接**：davidtong.org/teaching/electromagnetism/
- **配合项目**：L02 电磁学

## §1 一句话定位
**从 Coulomb 定律到麦克斯韦方程组**——电磁学是经典物理的集大成，也是狭义相对论的天然语言。

## §2 前置知识
- 必须会：矢量微积分（03_vector_calculus，散度/旋度/积分定理）、常微分方程、02 的狭义相对论
- 建议会：Fourier 分析（电磁波部分有用）、复变函数（辐射积分）

## §3 讲义全景（章节地图）

从静电场到电磁波，再到辐射和相对论形式。

| 章 | 主题 | 核心问题 |
|----|------|---------|
| 1 | 静电场 | 电荷怎么产生电场？|
| 2 | 多极展开 | 远场怎么近似？|
| 3 | 静磁场 | 电流怎么产生磁场？|
| 4 | 麦克斯韦方程 | 四个方程统一电磁 |
| 5 | 电磁波 | 变化的电磁场怎么传播？|
| 6 | 势与规范 | 电场磁场的"幕后"是什么？|
| 7 | 辐射 | 加速电荷怎么发光？|
| 8 | 介质中的电磁学 | 物质中的电磁场 |
| 9 | 相对论形式 | 电磁场的时空结构 |

## §4 核心章节拆解（深化版）

### §4.1 静电场与 Gauss 定律

**核心概念**：电荷产生电场，电场的通量由总电荷决定。

- **关键公式**：
$$\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}, \quad \oint \mathbf{E} \cdot d\mathbf{S} = \frac{Q_{\text{enc}}}{\epsilon_0}$$
- **Coulomb 定律**：$\mathbf{E} = \frac{1}{4\pi\epsilon_0} \frac{q\hat{r}}{r^2}$
- **电势**：$\mathbf{E} = -\nabla\phi$（静电场无旋），$\phi = \frac{1}{4\pi\epsilon_0}\frac{q}{r}$
- **Poisson 方程**：$\nabla^2\phi = -\rho/\epsilon_0$

**边界条件（介质界面）**：
- $\mathbf{E}_\parallel$（切向分量）**连续**
- $D_\perp$（法向 $\mathbf{D}=\epsilon\mathbf{E}$ 分量）**跃变** = $\sigma_{\text{free}}$（自由面电荷密度）

**电场能量密度**：$u = \frac{1}{2}\epsilon_0 E^2$。把两个电荷从无穷远推到一起所做的功，存储在场中。

**直觉图像**：电荷是电场线的"源头"——正电荷发出场线，负电荷吸入场线。场线密度 = 场强。

**反直觉点**：Gauss 定律说**不管你怎么分布**电荷，只要总电荷一样，远处球面上的通量就一样——但近处场强可以天差地别。

---

### §4.2 多极展开

**核心概念**：任意电荷分布在远场的电场 = 单极 + 偶极 + 四极 + …（类似 Taylor 展开，按 $1/r$ 的幂次展开）。

- **关键公式**：$$V(\mathbf{r}) = \frac{1}{4\pi\epsilon_0}\left[\frac{Q}{r} + \frac{\mathbf{p} \cdot \hat{r}}{r^2} + \frac{1}{2}\sum Q_{ij}\frac{\hat{r}_i \hat{r}_j}{r^3} + \ldots\right]$$
- **单极矩**：$Q = \sum q_i$（总电荷）
- **偶极矩**：$\mathbf{p} = \sum q_i \mathbf{r}_i$
- **四极矩张量**：$Q_{ij} = \sum q_i(3x_i x_j - r^2\delta_{ij})$（无迹）
- **偶极场**：$\mathbf{E}_{\text{dip}} \propto 1/r^3$（比单极 $1/r^2$ 衰减更快）
- **偶极场方向性**：轴向 $\mathbf{E}_{\text{dip}} = \frac{1}{4\pi\epsilon_0}\frac{2\mathbf{p}}{r^3}$，赤道面 $\mathbf{E}_{\text{dip}} = -\frac{1}{4\pi\epsilon_0}\frac{\mathbf{p}}{r^3}$

**直觉图像**：从远处看，一个复杂的电荷分布先像一个点电荷（单极），然后像一个偶极子，越远越像点电荷。

**反直觉点**：中性系统（$Q = 0$）的远场由偶极矩决定——"整体"看不到细节，只看到净电荷和偶极。这就是为什么分子间力是偶极-偶极相互作用（van der Waals 力、氢键的根源）。

### §4.3 静磁场与 Ampère 定律
- **核心概念**：电流产生磁场，磁场沿闭合回路的积分由穿过回路的总电流决定
- **关键公式**：
$$\nabla \times \mathbf{B} = \mu_0 \mathbf{J}, \quad \oint \mathbf{B} \cdot d\mathbf{r} = \mu_0 I_{\text{enc}}$$
- **Biot-Savart 定律**：$d\mathbf{B} = \frac{\mu_0}{4\pi}\frac{I\, d\mathbf{l} \times \hat{r}}{r^2}$
- **直觉图像**：右手定则——电流方向 → 磁场绕它旋转。直导线磁场绕成同心圆
- **反直觉点**：磁场没有"源头"（$\nabla \cdot \mathbf{B} = 0$）——不存在磁单极（至少经典电磁学中如此）。每根磁感线都是闭合的——没有起点没有终点

### §4.4 麦克斯韦方程组与电磁波

**核心概念**：四个方程统一电与磁，加上 Lorentz 力定律 $\mathbf{F} = q(\mathbf{E} + \mathbf{v} \times \mathbf{B})$，这就是全部经典电磁学。

**关键公式**（真空形式）：
$$\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0} \quad \text{（Gauss 定律）}$$
$$\nabla \cdot \mathbf{B} = 0 \quad \text{（无磁单极）}$$
$$\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t} \quad \text{（Faraday 定律）}$$
$$\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0\epsilon_0 \frac{\partial \mathbf{E}}{\partial t} \quad \text{（Ampère-Maxwell 定律）}$$

**位移电流的必然性（从电荷守恒推导）**：
- 电荷守恒：$\nabla \cdot \mathbf{J} + \frac{\partial\rho}{\partial t} = 0$
- 取 Ampère 原始方程 $\nabla \times \mathbf{B} = \mu_0\mathbf{J}$ 的散度：$\nabla\cdot(\nabla\times\mathbf{B}) = 0$ 但 $\mu_0\nabla\cdot\mathbf{J} = -\mu_0\frac{\partial\rho}{\partial t} \neq 0$——**矛盾！**
- Maxwell 补丁：加入 $\mu_0\epsilon_0\frac{\partial\mathbf{E}}{\partial t}$，则散度 $= \mu_0(\nabla\cdot\mathbf{J} + \epsilon_0\nabla\cdot\frac{\partial\mathbf{E}}{\partial t}) = \mu_0(\nabla\cdot\mathbf{J} + \frac{\partial\rho}{\partial t}) = 0$ ✓

**电磁波的推导**（一步步推）：
1. 真空 $\rho=0, \mathbf{J}=0$。从 Faraday 定律 $\nabla\times\mathbf{E} = -\frac{\partial\mathbf{B}}{\partial t}$
2. 两边取旋度：$\nabla\times(\nabla\times\mathbf{E}) = -\frac{\partial}{\partial t}(\nabla\times\mathbf{B})$
3. 左边用矢量恒等式 $\nabla\times(\nabla\times\mathbf{E}) = \nabla(\nabla\cdot\mathbf{E}) - \nabla^2\mathbf{E} = -\nabla^2\mathbf{E}$（真空 $\nabla\cdot\mathbf{E}=0$）
4. 右边用 Ampère-Maxwell：$\nabla\times\mathbf{B} = \mu_0\epsilon_0\frac{\partial\mathbf{E}}{\partial t}$
5. 得波动方程：$\nabla^2\mathbf{E} = \mu_0\epsilon_0\frac{\partial^2\mathbf{E}}{\partial t^2} = \frac{1}{c^2}\frac{\partial^2\mathbf{E}}{\partial t^2}$
6. **波速** $c = 1/\sqrt{\mu_0\epsilon_0} \approx 3\times10^8$ m/s——**恰好等于光速**！

**反直觉点**：电磁波的速度 $c = 1/\sqrt{\mu_0\epsilon_0}$ **完全由两个常数决定**——Maxwell 发现这个值恰好等于光速，由此推断"光就是电磁波"。这是物理学史上最伟大的统一之一。

---

### §4.5 电磁波与偏振

**核心概念**：真空中 $\rho = 0, \mathbf{J} = 0$ 时，麦克斯韦方程给出波动方程。

- **平面波解**：$\mathbf{E} = \mathbf{E}_0 e^{i(\mathbf{k}\cdot\mathbf{r} - \omega t)}$，$\omega = ck$
- **横波性**：$\nabla\cdot\mathbf{E}=0$ 要求 $\mathbf{E} \perp \mathbf{k}$；同理 $\mathbf{B} \perp \mathbf{k}$，且 $\mathbf{E} \perp \mathbf{B}$
- **振幅关系**：$|\mathbf{B}| = |\mathbf{E}|/c$，且 $\mathbf{B} = \frac{1}{c}\hat{\mathbf{k}}\times\mathbf{E}$
- **能量**：Poynting 矢量 $\mathbf{S} = \frac{1}{\mu_0}\mathbf{E} \times \mathbf{B}$（能流密度），时间平均 $\langle\mathbf{S}\rangle = \frac{1}{2\mu_0 c}|\mathbf{E}_0|^2\hat{\mathbf{k}}$
- **能量密度**：$u = \frac{1}{2}\epsilon_0 E^2 + \frac{1}{2\mu_0}B^2$（电场与磁场各贡献一半，对平面波）

**偏振**：$\mathbf{E}_0$ 可以是线偏振（固定方向）、圆偏振（$\mathbf{E}_0 = E_0(\hat{\mathbf{x}} \pm i\hat{\mathbf{y}})/\sqrt{2}$，端点画圆）、椭圆偏振。偏振态是光子的自旋自由度。

**直觉图像**：电场和磁场像两条蛇互相追逐——$\mathbf{E}$ 变化产生 $\mathbf{B}$，$\mathbf{B}$ 变化产生 $\mathbf{E}$，自维持传播。

**反直觉点**：电磁波不需要介质（不需要"以太"）——这在当时极其反直觉，直到 1905 年 Einstein 狭义相对论才给出解释。

### §4.6 势与规范变换
- **核心概念**：电场和磁场可以从势导出：标量势 $\phi$ 和矢量势 $\mathbf{A}$
- **关键公式**：$\mathbf{E} = -\nabla\phi - \frac{\partial \mathbf{A}}{\partial t}$, $\mathbf{B} = \nabla \times \mathbf{A}$
- **规范自由度**：$\mathbf{A} \to \mathbf{A} + \nabla\chi$, $\phi \to \phi - \partial\chi/\partial t$ 不改变 $\mathbf{E}$ 和 $\mathbf{B}$
- **常用规范**：Coulomb 规范 $\nabla \cdot \mathbf{A} = 0$（QM 常用）；Lorentz 规范 $\nabla \cdot \mathbf{A} + \frac{1}{c^2}\frac{\partial\phi}{\partial t} = 0$（协变）
- **直觉图像**：势是"幕后"的量，场是"可观测"的量——不同的势给出同一个场
- **反直觉点**：在量子力学中，**势本身**有物理效应（Aharonov-Bohm 效应）——即使场为零的区域，势也能影响电子的量子相位

---

### §4.7 辐射

**核心概念**：**加速**运动的电荷辐射电磁波——匀速运动不辐射。

**Larmor 公式**（非相对论总功率）：
$$P = \frac{q^2 a^2}{6\pi\epsilon_0 c^3}$$
只依赖加速度 $a$ 的平方。$a=0$（匀速）→ $P=0$。

**相对论推广（Liénard 公式）**：
$$P = \frac{q^2\gamma^6}{6\pi\epsilon_0 c^3}\left(a^2 - \frac{(\mathbf{v}\times\mathbf{a})^2}{c^2}\right)$$
其中 $\gamma = 1/\sqrt{1-v^2/c^2}$。当加速度垂直于速度（圆周运动），功率正比于 $\gamma^4$——**同步辐射**极其强烈。

**辐射方向图**：低速时各向同性（$\propto\sin^2\theta$）；高速时向前聚焦成窄锥（相对论束流效应 beaming）。

**同步辐射**：相对论电子在磁场中做圆周运动，辐射强烈的前向窄锥光束。这是大型同步辐射光源（如 ESRF、SSRF）的物理基础，也是天体物理中（蟹状星云）的重要辐射机制。

**辐射场**：$\mathbf{E}_{\text{rad}} \propto \frac{q\, \mathbf{a}_\perp}{r}$（只与加速度的横向分量有关，$1/r$ 衰减——比 Coulomb 场 $1/r^2$ 衰减慢！）

**反直觉点**：**匀速运动不辐射**。匀速运动的场跟着电荷走，不辐射能量。只有加速度才"甩出"电磁波——像甩鞭子产生声波。这就是为什么远处能看到星星的光（$1/r$ 辐射场），但感受不到它们的电场（$1/r^2$ 近场早已衰减为零）。

---

### §4.8 介质中的电磁学

**核心概念**：在物质中引入 $\mathbf{D}$ 和 $\mathbf{H}$，把束缚电荷和电流的效果吸收进去。

- **关键公式**：$\mathbf{D} = \epsilon_0 \mathbf{E} + \mathbf{P}$, $\mathbf{H} = \frac{1}{\mu_0}\mathbf{B} - \mathbf{M}$
- **线性介质**：$\mathbf{D} = \epsilon\mathbf{E}$（$\epsilon = \epsilon_0\epsilon_r$），$\mathbf{B} = \mu\mathbf{H}$
- **介质中光速**：$v = 1/\sqrt{\mu\epsilon} = c/n$，折射率 $n = \sqrt{\epsilon_r\mu_r}$
- **色散**：$\epsilon(\omega)$ 随频率变化 → 折射率依赖频率 → 棱镜分光、彩虹

**直觉图像**：介质的分子像小偶极子，被外场极化（$\mathbf{P}$）或磁化（$\mathbf{M}$）。外场使正负电荷中心错位，产生宏观偶极矩。

**反直觉点**：$\mathbf{D}$ 和 $\mathbf{H}$ 是"辅助"场，不是基本场——基本场只有 $\mathbf{E}$ 和 $\mathbf{B}$。引入 $\mathbf{D}$、$\mathbf{H}$ 只是为了方便（消去束缚电荷/电流）。物理上，束缚电荷也是真实的电荷，只是被"打包"进了 $\mathbf{P}$。

---

### §4.9 电磁场的相对论形式

**核心概念**：电场和磁场是同一个**电磁场张量** $F_{\mu\nu}$ 的不同分量——它们可以互相转化。

**电磁场张量**：
$$F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu$$
$$F_{\mu\nu} = \begin{pmatrix} 0 & -E_x/c & -E_y/c & -E_z/c \\ E_x/c & 0 & -B_z & B_y \\ E_y/c & B_z & 0 & -B_x \\ E_z/c & -B_y & B_x & 0 \end{pmatrix}$$

**协变 Lorentz 力**：
$$\frac{dp^\mu}{d\tau} = q F^{\mu\nu} u_\nu$$
其中 $u_\nu = dx_\nu/d\tau$ 是四维速度。这一个方程就包含了 $\mathbf{F} = q(\mathbf{E}+\mathbf{v}\times\mathbf{B})$ 的全部信息。

**E 和 B 的混合**：在 Lorentz boost 下，$F_{\mu\nu}$ 做张量变换。一个参考系中的**纯电场**在另一个运动参考系中变成**电场 + 磁场**。

**反直觉点（磁力的相对论本质）**：一根载流直导线在实验室系中**电中性**（正离子与电子密度精确平衡）。但从电子（在另一根平行导线中运动）的静止系看，导线中的运动电子因**长度收缩**密度变化，导线变得**带电**——产生电力。这就是"磁力"的本质：**磁力是电力的相对论修正**。日常磁力如此之强是因为导线中有 $\sim10^{23}$/cm³ 的电荷，中性平衡极其精确，微小相对论偏差就被放大成可观的磁效应。**磁学就是电学 + 狭义相对论**。

## §5 必做习题（深化版）

| 题 | 内容 | 为什么必做 |
|----|------|----------|
| 1 | **Gauss 定律**：均匀带电球的电场 $E(r)$（内部 + 外部），画图 | 球对称下 Gauss 面法的第一练 |
| 2 | **Ampère 定律**：无限长螺线管内部磁场 | 高对称性下 Ampère 回路法 |
| 3 | **推导电磁波**：从麦克斯韦方程一步步推波动方程，验 $c=1/\sqrt{\mu_0\epsilon_0}$ | 理解位移电流为何是波的根源 |
| 4 | **Larmor 公式**：振荡偶极子的辐射功率与角分布 | 加速电荷辐射的核心计算 |
| 5 | **推迟势**：Lorentz 规范下推导 $\phi(\mathbf{r},t) = \frac{1}{4\pi\epsilon_0}\int\frac{\rho(\mathbf{r}',t_r)}{|\mathbf{r}-\mathbf{r}'|}d^3r'$ | 理解因果性与规范选择 |
| 6 | **$F_{\mu\nu}$ 变换**：验证电磁场张量在 Lorentz boost 下正确变换 | 确信 E/B 是同一张量的分量 |
| 7 | **Poynting 矢量**：平面波 $\mathbf{S} = \frac{1}{\mu_0}\mathbf{E}\times\mathbf{B}$，算能流密度与强度 | 电磁波携带能量的定量理解 |

## §6 读完后你应该能
- [ ] 写出麦克斯韦方程组的微分和积分形式，解释每个方程的物理意义
- [ ] 用 Gauss/Ampère/Faraday 定律解高对称性的场
- [ ] 理解为什么变化的电磁场会自维持传播为波
- [ ] 解释为什么电场和磁场是相对论性的概念（$F_{\mu\nu}$ 的统一）
- [ ] 计算偶极辐射的功率和角分布
- [ ] 理解规范变换的物理意义（为什么 QFT 以规范对称性为核心）
- [ ] 推导光速 $c = 1/\sqrt{\mu_0\epsilon_0}$

## §7 与项目的映射
- **前置**：03_vector_calculus.md（必须有矢量微积分基础）
- **后续**：14_qft.md（电磁场的量子化 = QED）
- **对应**：L02 电磁学
- **并行**：13_general_relativity.md（同样是张量场论，但用度规而非规范势）

## §8 延伸阅读
- 读完 → 14 QFT（电磁场的量子化）
- 教材 → Griffiths *Introduction to Electrodynamics*（最经典本科教材，清晰且幽默，强烈推荐）
- 教材 → Jackson *Classical Electrodynamics*（研究生标准，全面但难，辐射和多极展开特别详细）
- 相对论部分 → 02_dynamics_relativity.md
- 历史 → Feynman 讲义卷 2（用更直觉的方式讲电磁学）
- 深入 → Purcell *Electricity and Magnetism*（Berkeley Physics Course，从相对论推导磁力）

## §9 学习建议
- **节奏**：6-8 周（155 页，内容密集）
- **怎么读**：每章配做 Griffiths 对应章节的习题，至少 5 道
- **陷阱**：
  - 不要跳过势和规范——这是通往 QFT 的桥梁
  - 麦克斯韦方程的**微分形式**比积分形式更常用，要熟练
  - 相对论形式（$F_{\mu\nu}$）看似抽象，但它是理解"电场磁场是同一东西"的关键
  - 位移电流是 Maxwell 的**天才补丁**——不要因为它"只是个修正项"就忽略它，没有它就没有电磁波
  - 多极展开的收敛性取决于 $r/d$（观测距离 vs 系统大小），近场不收敛
- **关键洞察**：电磁学是**第一个规范理论**——规范变换 $\mathbf{A} \to \mathbf{A} + \nabla\chi$ 的思想后来推广到弱力、强力，成为粒子物理标准模型的核心。理解电磁学的规范结构 = 理解标准模型的一半。

## §10 常见误区（深化新增）

### 🕳️ 误区 1：电场和磁场是完全不同的东西
- ❌ "电场归电场，磁场归磁场，两者独立"
- ✅ 它们是同一个**电磁场张量 $F_{\mu\nu}$** 的不同分量——在 Lorentz 变换下互相转化。纯电场在一个参考系中，在另一个运动参考系中会变成电场 + 磁场。

### 🕳️ 误区 2：位移电流是 Maxwell 凑出来的数学技巧
- ❌ "位移电流 $\epsilon_0\partial\mathbf{E}/\partial t$ 只是数学补丁"
- ✅ 它是**电荷守恒的必然要求**。没有它，$\nabla\cdot(\nabla\times\mathbf{B})=0$ 与 $\nabla\cdot\mathbf{J} = -\partial\rho/\partial t \neq 0$ 矛盾。没有位移电流就没有电磁波。

### 🕳️ 误区 3：匀速运动的电荷会辐射
- ❌ "运动的电荷（如导线中的电流）会辐射电磁波"
- ✅ **只有加速度才辐射**。匀速运动的场跟着电荷走，不辐射能量（Larmor 公式 $P \propto a^2$，$a=0$ 则 $P=0$）。导线中电流不辐射，只有加速电荷（如天线中的振荡电荷）才辐射。

### 🕳️ 误区 4：电磁波需要介质（以太）传播
- ❌ "电磁波像声波一样需要介质"
- ✅ 电磁波在**真空中自维持传播**——$\mathbf{E}$ 变化产生 $\mathbf{B}$，$\mathbf{B}$ 变化产生 $\mathbf{E}$，无需任何介质。这正是 1905 年 Einstein 狭义相对论要解释的核心事实。

### 🕳️ 误区 5：Aharonov-Bohm 效应证明规范势比场更基本
- ❌ "AB 效应说明 $\mathbf{A}$ 比 $\mathbf{E}, \mathbf{B}$ 更基本，规范自由度有物理意义"
- ✅ AB 效应证明的是**规范势的回路积分**（Wilson loop $\oint\mathbf{A}\cdot d\mathbf{l}$，即磁通量）有物理效应。但**规范自由度本身仍然冗余**——不同的规范给出相同的 Wilson loop。场和"规范的等价类"才是基本的。

## §11 与其他电磁学教材的对比（深化新增）

| 教材 | 风格 | 适合谁 | vs Tong |
|------|------|--------|---------|
| **Griffiths** *Intro to Electrodynamics* | 清晰幽默，习题经典 | 本科主教材 | 比 Tong 更详细（边界条件/介质），标准选择 |
| **Jackson** *Classical Electrodynamics* | 研究生标准，全面严谨 | 进阶/参考 | 辐射、多极展开、相对论特别深，但难 |
| **Purcell** *Electricity and Magnetism*（Berkeley）| 从相对论推导磁力 | 想理解"磁=电+相对论" | 物理直觉极强，与 Tong 互补 |
| **Feynman Lectures** vol 2 | 最直觉，费曼风格 | 想要"啊哈"时刻 | 比 Tong 更散文化，物理洞察多 |
| **Landau & Lifshitz** *Electrodynamics of Continuous Media* | 理论物理教程风格 | 想看最深 | 凝练极深，连续介质部分权威 |

**建议组合**：**Tong（主读）+ Griffiths（做题）+ Purcell（相对论直觉）** = 电磁学自学三件套。

---

**完成日期**：2026-08-13（深化版 v2，从 163 行扩到 ~310 行）
**配套**：[tong/README.md](README.md) + [TEMPLATE.md](../TEMPLATE.md) + [ai_for_physics/](../../ai_for_physics/)
