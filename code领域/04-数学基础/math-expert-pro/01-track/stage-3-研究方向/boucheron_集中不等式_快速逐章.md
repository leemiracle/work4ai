# Stéphane Boucheron, Gábor Lugosi, Pascal Massart《集中不等式：独立的非 asymptotic 理论》 · 快速逐章精读

> 基于原书：*Concentration Inequalities: A Nonasymptotic Theory of Independence*（Stéphane Boucheron / Gábor Lugosi / Pascal Massart, Oxford University Press, **2013**，Foreword by Michel Ledoux）/ 读于：2026-07-03
> 定位：**集中不等式（concentration of measure）的现代方法专精**，独立变量函数的「非渐近」浓度理论三部曲之一，是泛化界、Rademacher 复杂度、PAC-Bayes、过参数化理论背后**一切指数尾部控制的工具母机**。
> 特色：第二句——本书不以「应用广」取胜（那是 Vershynin 的定位），而以**方法统一**见长：方差界（Efron-Stein）→ 熵方法（log-Sobolev + Herbst argument）→ 等周（Gaussian / hypercube）→ transportation（Marton / Talagrand）四条路线汇聚到同一现象「独立 + 影响有界 ⇒ 指数集中」，是一部方法论专著。
> 声明：本文为**快速逐章精读**（核心逻辑串联 + 飞腾锚点 + 关键定理 LaTeX + 自测），非逐行证明复读。
> 关联：[Vapnik SLT](vapnik_统计学习理论_快速逐章.md)（刚做）· [Mohri FoML](mohri_机器学习理论基础_快速逐章.md)（刚做）· [Vershynin 高维概率](vershynin_高维概率_快速逐章.md) · [Wainwright 高维统计](wainwright_高维统计_快速逐章.md) · [Shalev-Shwartz UML](shalev_shwartz_理解机器学习_快速逐章.md) · [Cover-Thomas 信息论](cover_thomas_信息论_快速逐章.md)

---

> ⚠️ **TOC 校正说明（忠于原书，2026-07-03 经 WorldCat + OUP 双源核实）**：原书实为 **15 章**（非任务草拟的 14 章）。关键差异：① 任务给的「Ch4 Higher-Order Moments/Combinatorics」「Ch6 Variations on the Entropy Method」实为 Ch4 *Basic information inequalities* + Ch5 *Log-Sobolev* + Ch6 *The entropy method* 三章的合并误记；② 任务的「Ch11 极值的方差」实为 *The variance of suprema of empirical processes*；③ 任务的「Ch14 Applications to Statistical Learning Theory」原书并无独立此章——统计学习应用直接就是 Ch11–13 的经验过程上确界主题；④ 高阶矩在原书是末章 Ch15 *Moment inequalities*，Φ-entropy 是 Ch14。**本文以原书真实 15 章 TOC 为准并逐章标注**。

---

## §0 引言：集中不等式是什么，为什么 ML 理论方向必须读它（约 370 字）

三位作者——Boucheron（Paris-Diderot）、Lugosi（ICREA / Pompeu Fabra，机器学习理论名家）、Massart（Paris-Sud，模型选择 *Massart 不等式* 的提出者）——在 2013 年 OUP 推出这部专著，由 Michel Ledoux（浓度理论的另一位奠基者）作序。它聚焦一个核心现象：**若 $f(X_1,\dots,X_n)$ 是独立变量的函数，且任意单个 $X_i$ 对 $f$ 的影响「足够小」，则 $f$ 以压倒性概率紧贴其期望——大偏差的概率指数衰减**。书名副标题 *A Nonasymptotic Theory of Independence* 一语中的：本书不问 $n\to\infty$ 的渐近极限（那是 CLT 的领地），而问**有限 $n$ 下偏差到底多大**。

全书被四条方法论主线贯穿：① **方差界**（Ch3，Efron-Stein / Poincaré，二阶矩视角，只给 $O(1/t^2)$ 弱浓度）；② **熵方法**（Ch4–6，Han / log-Sobolev / Herbst argument，给出指数级 $\exp(-ct^2)$，全书引擎）；③ **等周**（Ch7、10，Gaussian / hypercube isoperimetry，几何视角）；④ **transportation**（Ch8，Marton / Talagrand，Wasserstein 距离视角）。Ch11–13 把工具砸到**经验过程上确界**——这正是统计学习泛化界的数学心脏：经验风险与真实风险之差 $\sup_{f\in\mathcal{F}}|(P_n-P)f|$ 的浓度，由 Bousquet / Massart 不等式控制（Ch12），其期望由 Rademacher 复杂度 / Dudley 链控制（Ch13）。**Vapnik（刚做）的 VC 泛化界、Mohri（刚做）的 Rademacher 界、Shalev-Shwartz 的 PAC-Bayes，全都建在本书 Ch11–13 之上**。飞腾锚点：**Iron Law<2%**（浓度 = 误差控制铁律）贯穿全书，**UDOT 16.9×**（期望/熵的本质是加权求和）是 MGF 与 tensorization 的硬件肉身。

### 四本浓度/高维教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|:---|:---|:---|:---|
| **Boucheron-Lugosi-Massart《集中不等式》2013（本书）** | 方法论专著，四条路线（方差/熵/等周/transportation）统一浓度现象 | ★★★★★（极严密，自洽推导） | 想吃透浓度方法本身、做 ML 泛化理论研究的人 |
| Ledoux《The Concentration of Measure Phenomenon》2001, AMS | 浓度理论奠基专著，几何 + 函数论视角，极凝练 | ★★★★★（大师级，但极硬） | 几何测度论背景、想追到源头的研究者 |
| Vershynin《High-Dimensional Probability》2018（已读） | 概率工具 + 数据科学应用入门，sub-gaussian 主轴 | ★★★★（证明完整、本科友好） | 想从概率工具快速进入应用的人 |
| Wainwright《High-Dimensional Statistics》2019（已读） | 非渐近统计理论，极小极大 + 信息下界，统计推断导向 | ★★★★★（系统、研究生级） | 做高维统计推断、oracle 不等式的人 |

> **阅读策略**：Vershynin（概率工具入门 + sub-gaussian） → **BLM（方法专精，理解 Hoeffding/log-Sobolev/Bousquet 为何成立）** → Wainwright（统计推断应用） → Ledoux（几何源头深挖）。本书是这条链的「**方法核心**」环节。Ledoux 的正确浓度专著是 *Concentration of Measure Phenomenon*（2001）而非 *Probability in Banach Spaces*（1991，另一主题）。

---

## §1 全书 15 章骨架一览（飞腾锚点分布）

> **结构概览**：全书分**五大块**。Block A（Ch1–2）设定现象 + 基本工具（Markov → Hoeffding/Bernstein，标量浓度）；Block B（Ch3）方差视角（Efron-Stein/Poincaré，弱浓度，引出对更强工具的需求）；Block C（Ch4–6）**熵方法三部曲**（信息不等式 → log-Sobolev → entropy method，全书引擎，给出指数级浓度）；Block D（Ch7–10）**几何/transportation 视角**（等周 + transportation + 影响/阈值，揭示浓度的几何本质）；Block E（Ch11–13）**经验过程上确界**（统计学习泛化界的数学心脏）；附录式（Ch14–15）Φ-entropy 与高阶矩推广。**全书灵魂：独立 + 影响有界 ⇒ 指数集中；熵方法、等周、transportation 是同一现象的三条对偶证明路径。**

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:--|:--|:--|:--|
| 1 | Introduction | 集中现象、三大动机例子 | Iron Law<2% 🟢 |
| 2 | Basic Inequalities | Markov/Chernoff/Hoeffding/Bernstein/McDiarmid | UDOT 16.9× 🟢 |
| 3 | Bounding the Variance | Efron-Stein、Poincaré、leave-one-out | matmul 15× 🟡 |
| 4 | Basic Information Inequalities | 熵、Han 不等式、次可加性 | UDOT 16.9× 🟢 |
| 5 | Logarithmic Sobolev Inequalities | log-Sobolev、Herbst argument | Iron Law<2% 🟢 |
| 6 | The Entropy Method | tensorization、self-bounding、Bernstein 型 | UDOT 16.9× 🟢 |
| 7 | Concentration and Isoperimetry | Gaussian 等周、Lévy 引理 | TLB 4.81× 🟡 |
| 8 | The Transportation Method | Marton、Talagrand、Pinsker、$T_2$ | Iron Law<2% 🟢 |
| 9 | Influences and Threshold Phenomena | Russo 公式、KKL、影响不等式 | 分支预测 🟢 |
| 10 | Isoperimetry on the Hypercube and Gaussian Spaces | Harper、edge-isoperimetry、Gaussian | Schmidt 正交化 🟡 |
| 11 | The Variance of Suprema of Empirical Processes | 对称化、上确界方差界 | GEMM 9.45G 🟢 |
| 12 | Suprema: Exponential Inequalities | Bousquet、Massart 尾界 | Iron Law<2% 🟢 |
| 13 | The Expected Value of Suprema | chaining、Dudley、Rademacher | matmul 15× 🟢 |
| 14 | Φ-Entropies | 广义熵、$\Phi(x)=x^p$、tensorization | UDOT 16.9× 🟡 |
| 15 | Moment Inequalities | 各阶矩、sub-gamma 矩序列 | Iron Law<2% 🟡 |

> **精读优先级**：⭐Ch2（标量浓度地基）→ ⭐Ch3（Efron-Stein，方差思维入口）→ ⭐Ch5–6（log-Sobolev + Herbst + entropy method，**全书灵魂**）→ ⭐Ch11–13（经验过程上确界，**ML 泛化界引擎**）→ Ch7–8（等周/transportation，几何对偶）→ Ch9（影响/阈值，组合应用）→ Ch4/10/14/15（推广）。15 章用 7 个锚点分散覆盖，相邻章均不重复。

---

# Block A · 现象与基本工具（Ch1–2）

---

## 第 1 章 · Introduction（引言：集中现象）

**核心**：开篇立下全书的**中心命题**：若 $Z=f(X_1,\dots,X_n)$，$X_i$ 独立，且每个 $X_i$ 对 $Z$ 的影响「有界」（$|f-f_i'|\le c_i$，即 *bounded differences*），则 $Z$ 高度集中——$\mathbb{P}(|Z-\mathbb{E}Z|\ge t)$ 随 $t$ 指数衰减。三个动机例子确立直觉：① Hoeffding（独立和）；② Gaussian / 球面等周（高维球上 Lipschitz 函数常数集中）；③ 组合优化（如 bin-packing、随机图）。本章把「集中」从零散不等式上升为一个**统一现象**：独立性是概率结构，有界影响是函数结构，二者结合产生指数集中。

**飞腾锚点** 🟢 **Iron Law<2%**：集中不等式即概率版的 **Iron Law**——「大偏差以压倒性概率不发生」，误差被铁律锁在指数衰减的尾部里。性能 = 指令数×CPI×时钟，每个因子都要 <2%；浓度 = 偏差概率 $\le 2e^{-ct^2}$，每个量级都被指数压住。全书即是对这条「概率铁律」的多角度证明。

**关键定理**：**有界差不等式（McDiarmid / bounded differences）预告**——若 $|f(x)-f(x')|\le c_i$ 当仅第 $i$ 坐标不同，则 $\mathbb{P}(|Z-\mathbb{E}Z|\ge t)\le 2\exp\!\left(-\tfrac{2t^2}{\sum_i c_i^2}\right)$。方差被 $\sum c_i^2/4$ 控制，尾部指数衰减。

**自测**：$Z=\max_i X_i$，$X_i\sim\mathsf{Uniform}[0,1]$ 独立。$Z$ 的方差量级？答：改变一个 $X_i$ 最多改变 $Z$ 约 $1$（仅当它是最大），但平均影响 $O(1/n)$；$\mathrm{Var}(Z)\sim 1/n^2$，故 $Z$ 极度集中（标准差 $\sim 1/n$）。

---

## 第 2 章 · Basic Inequalities（基本不等式：Markov → Hoeffding → Bernstein）

**核心**：标量浓度的**地基层**，按尾部收紧程度递进：**Markov**（$P(X\ge t)\le \mathbb{E}X/t$，多项式，最弱）→ **Chebyshev**（用方差，$1/t^2$）→ **Chernoff 方法**（用矩母函数 MGF $M(\lambda)=\mathbb{E}e^{\lambda X}$，对 $\lambda$ 优化，跳到指数级）→ **Hoeffding 引理**（有界变量 $X\in[a,b]$ 的 MGF 被 sub-Gaussian 界住）→ **Hoeffding 不等式**（独立和）→ **Bennett/Bernstein**（利用方差信息，比 Hoeffding 紧：小偏差 sub-Gaussian、大偏差 $\exp(-ct)$）。本章还含 **McDiarmid（bounded differences）**——把 Hoeffding 从「和」推广到「一般有界影响函数」，是 Ch1 预告命题的兑现。

**飞腾锚点** 🟢 **UDOT 16.9×**：MGF $M_X(\lambda)=\mathbb{E}e^{\lambda X}=\sum_x p(x)e^{\lambda x}$ 与独立和 $S_n=\sum X_i$（$M_{S_n}=\prod M_{X_i}$）本质都是**加权求和/内积**——UDOT 向量化点积累加 16.9× 加速是大规模 MGF 估计、蒙特卡洛浓度验证的硬件肉身。经验均值 $\bar X=\tfrac1n\sum X_i$ 每一行都是一次点积。

**关键定理**：**Hoeffding 不等式**（i.i.d. 版）——独立 $X_i\in[a,b]$，$\mu=\mathbb{E}X_i$：
$$\mathbb{P}\!\left(|\bar X-\mu|\ge t\right)\le 2\exp(-2nt^2).$$
**Bernstein**（方差 $\sigma^2$、界 $B$）：$\mathbb{P}(|\bar X-\mu|\ge t)\le 2\exp\!\left(-\tfrac{nt^2/2}{\sigma^2+Bt/3}\right)$。

**自测**：$n=1000$ 次伯努利 $p=0.5$，用 Hoeffding 给 $\mathbb{P}(|\hat p-0.5|\ge 0.03)$。答：$\le 2e^{-2\cdot1000\cdot0.0009}=2e^{-1.8}\approx0.33$；Chebyshev 只给 $\sigma^2/(n t^2)=0.25/(1000\cdot0.0009)\approx0.28$——量级相近但 Hoeffding 在大 $t$ 远胜。

---

# Block B · 方差视角（Ch3）

---

## 第 3 章 · Bounding the Variance（方差界：Efron-Stein、Poincaré）

**核心**：在拿到指数浓度（Ch5+）之前，先用**二阶矩**给一个弱但极通用的浓度。核心工具 **Efron-Stein 不等式**：用「leave-one-out / 替换一个变量」把 $\mathrm{Var}(Z)$ 控制在「每个变量的平均影响」之和上——不需要变量有界，只需「换一个变量的扰动可控」。**Poincaré 不等式**（Gaussian / 离散）是其连续/梯度版：$\mathrm{Var}(f)\le\mathbb{E}\|\nabla f\|^2$，方差被能量（梯度范数平方）控制。本章只给 Chebyshev 级 $O(1/t^2)$ 浓度，但它揭示：**浓度问题的钥匙是「每个变量的局部影响」之和**——熵方法（Ch5–6）正是把这一思想从二阶矩升级到指数矩。

**飞腾锚点** 🟡 **matmul 15×**：Efron-Stein 的 $\mathrm{Var}(Z)\le\tfrac12\sum_i\mathbb{E}(Z-Z_i')^2$ 是**平方项求和**（二次型）；Poincaré 的 $\mathbb{E}\|\nabla f\|^2=\sum_i\mathbb{E}(\partial_i f)^2$ 是梯度各分量平方和——本质是协方差/二次型，对应矩阵运算的 $x^\top x$ 内积。把方差当二次型，matmul 是它的工程原语。

**关键定理**：**Efron-Stein 不等式**——$Z=f(X_1,\dots,X_n)$，$Z_i'=f(X_1,\dots,X_i',\dots,X_n)$（仅第 $i$ 个换独立副本），则
$$\mathrm{Var}(Z)\le \tfrac{1}{2}\sum_{i=1}^n\mathbb{E}\!\left[(Z-Z_i')^2\right].$$
**Gaussian Poincaré**：$\mathrm{Var}(f)\le\sigma^2\,\mathbb{E}\|\nabla f\|^2$。

**自测**：$Z=\sum_i X_i$，$X_i$ 独立，方差 $\sigma_i^2$。Efron-Stein 给什么？答：$Z-Z_i'=X_i-X_i'$，$\mathbb{E}(X_i-X_i')^2=2\sigma_i^2$，故 $\mathrm{Var}(Z)\le\tfrac12\sum 2\sigma_i^2=\sum\sigma_i^2$——恰为等式（Efron-Stein 对线性函数紧）。

---

# Block C · 熵方法三部曲（Ch4–6）⭐⭐⭐ 全书引擎

---

## 第 4 章 · Basic Information Inequalities（基本信息不等式：Han、熵的次可加）

**核心**：熵方法三部曲的第一步——**引入信息论武器**。定义相对熵（KL）与**熵泛函** $\mathrm{Ent}(Z)=\mathbb{E}[Z\log Z]-\mathbb{E}Z\log\mathbb{E}Z$（$Z\ge0$）。关键性质 **tensorization（张量化）**：独立变量下，$\mathrm{Ent}$ 对乘积测度有「可加分解」——整个函数的熵 $\le$ 各变量「条件熵」之和。**Han 不等式**给出联合熵与边缘熵的关系，是 tensorization 的组合形式。本章把「$Z=e^{\lambda f}$ 的熵」转化为「$f$ 对各变量的条件依赖」之和——为 Ch5（log-Sobolev）和 Ch6（entropy method）铺好代数地基。

**飞腾锚点** 🟢 **UDOT 16.9×**：$\mathrm{Ent}(Z)=\mathbb{E}[Z\log Z]-\mathbb{E}Z\cdot\log\mathbb{E}Z$ 是两次**加权求和**（期望）；tensorization 把它拆成 $\sum_i$ 项条件熵——又是求和。熵的运算从第一步就落在点积求和上，UDOT 16.9× 是它的硬件骨架。

**关键定理**：**熵的 tensorization**——对乘积测度下 $Z\ge0$：
$$\mathrm{Ent}(Z)\le\sum_{i=1}^n\mathbb{E}\!\left[\mathrm{Ent}_{(i)}(Z)\right],$$
其中 $\mathrm{Ent}_{(i)}$ 是固定其余变量、仅对 $X_i$ 取的熵。**Han 不等式**：$H(X_1,\dots,X_n)\le\dfrac{1}{n-1}\sum_i H(X_{[n]\setminus i})$。

**自测**：$Z=\prod_i X_i$（独立 $X_i>0$）。$\mathrm{Ent}(Z)$ 与各 $\mathrm{Ent}_{(i)}$ 关系？答：取对数后乘积变求和，$\mathrm{Ent}(Z)=\sum_i\mathbb{E}\,\mathrm{Ent}_{(i)}(Z)$ 恰为等式——tensorization 对乘积紧。

---

## 第 5 章 · Logarithmic Sobolev Inequalities（对数 Sobolev 不等式）⭐⭐⭐

**核心**：三部曲第二步——**log-Sobolev 不等式**把「熵被梯度能量控制」写成一条几何-分析公理。**Gaussian log-Sobolev（Gross 1975）**：$\mathrm{Ent}(f^2)\le 2\sigma^2\,\mathbb{E}\|\nabla f\|^2$（比 Poincaré 的方差强：控制的是 $\mathrm{Ent}(f^2)$ 而非 $\mathrm{Var}$）。**Herbst argument（关键技巧）**：把 log-Sobolev 作用到 $Z=e^{\lambda f}$ 上，化成 $f$ 的 MGF 的微分不等式 $\lambda(\log M)'-\log M\le\tfrac{\sigma^2\lambda^2}{2}$，解出 $\log M(\lambda)\le\tfrac{\sigma^2\lambda^2}{2}$，即 $f$ 是 sub-Gaussian——**一步把 log-Sobolev 转成指数浓度**。离散版（hypercube log-Sobolev）同样成立。本章是「为什么 Lipschitz 函数 sub-Gaussian」的最干净证明路径。

**飞腾锚点** 🟢 **Iron Law<2%**：log-Sobolev + Herbst 是**最强的 Iron Law**——它给出 sub-Gaussian 尾 $\exp(-t^2/2\sigma^2)$，比 Efron-Stein 的 $1/t^2$ 收紧无数倍。Gross 不等式把「误差铁律」钉死成一条分析公理：能量（梯度）有界 ⇒ 浓度指数级。这是全书「精度」的顶峰。

**关键定理**：**Gaussian log-Sobolev 不等式**（Gross）：标准 Gaussian 下，光滑 $f$：
$$\mathrm{Ent}(f^2)\le 2\,\mathbb{E}\|\nabla f\|^2,\qquad \mathrm{Ent}(f^2)=\mathbb{E}[f^2\log f^2]-\mathbb{E}f^2\log\mathbb{E}f^2.$$
**Herbst 推论**：$1$-Lipschitz 的 $f$ 在标准 Gaussian 下，$\mathbb{P}(|f-\mathbb{E}f|\ge t)\le 2e^{-t^2/2}$。

**自测**：$f(X)=\|X\|$，$X\sim\mathcal{N}(0,I_n)$。$\|\nabla f\|=1$（Lipschitz 常数 1）。log-Sobolev 给什么浓度？答：$\mathbb{P}(|\|X\|-\mathbb{E}\|X\||\ge t)\le 2e^{-t^2/2}$——高维球面附近质量集中，$\|X\|\approx\sqrt{n}$ 误差 $O(1)$。

---

## 第 6 章 · The Entropy Method（熵方法）⭐⭐⭐ 全书方法高潮

**核心**：三部曲第三步——把 Ch4–5 的代数（tensorization + log-Sobolev）提炼成**通用算法**，对任意 $Z=f(X_1,\dots,X_n)$ 生产指数浓度。核心是「**条件熵界**」：$\mathrm{Ent}(e^{\lambda Z})\le\mathbb{E}\sum_i\lambda e^{\lambda Z}(Z-Z_i')(1-e^{-\lambda(Z-Z_i')})$（向量值熵不等式），配合 Herbst 解出 sub-Gamma / sub-exponential 尾。引入 **self-bounding（自界）函数**类：满足 $0\le Z-\inf_{x_i}Z\le1$ 且 $\sum_i(Z-\inf_{x_i}Z)\le Z$ 的函数（如经验风险、集合的大小），对它们熵方法给出**最优**的 Bernstein 型界 $P(|Z-\mathbb{E}Z|\ge t)\le 2\exp(-Z^* h(t/Z^*))$。本章是 Boucheron-Lugosi-Massart 自己发展出的统一框架。

**飞腾锚点** 🟢 **UDOT 16.9×**：entropy method 的代数核心是 $\sum_i$（对 $n$ 个变量的条件项求和）+ $\mathbb{E}$（期望求和）——双重求和，UDOT 向量化是它的工程原语。self-bounding 的 $\sum_i(Z-\inf Z)\le Z$ 本身就是一次内积不等式。

**关键定理**：**向量值熵不等式 + self-bounding 浓度**——若 $Z$ self-bounding（$Z^*=\sup Z$），则
$$\mathbb{P}(Z\ge \mathbb{E}Z+t)\le\exp\!\left(-Z^*\,h\!\left(\tfrac{t}{Z^*}\right)\right),\quad h(u)=(1+u)\log(1+u)-u,$$
即 Bernstein 型指数尾。**McDiarmid 的熵方法强化版**也在本章：把 bounded differences 的 $\exp(-2t^2/\sum c_i^2)$ 升级为方差敏感版。

**自测**：$Z=$ 集合 $A$ 的元素个数（cardinality），self-bounding？答：是——每移除一个元素 $Z$ 减 $\le1$，且 $\sum$ 贡献 $=Z$。故 $Z$ 有 Bernstein 型浓度，$\mathrm{Var}(Z)\le\mathbb{E}Z$。

---

# Block D · 几何与 transportation 视角（Ch7–10）

---

## 第 7 章 · Concentration and Isoperimetry（集中与等周）

**核心**：从**几何**重新理解浓度：集中是**等周不等式**（isoperimetry）的推论。**Gaussian 等周不等式**（Borell / Sudakov-Tsirelson）：在标准 Gaussian 下，使一半质量的集合，其 $t$-邻域的余质量 $\le 1-\Phi(\Phi^{-1}(1/2)+t)\le e^{-t^2/2}$——这是比 log-Sobolev 更锐的几何事实。**Lévy 引理**：球面上 Lipschitz 函数集中在中位数附近，偏差 $O(\sqrt{\log n}/r)$，与维度无关的常数浓度——「高维球上一切皆常数集中」。本章揭示浓度的**几何起源**：集合边界小 ⇒ 质量无法远离 ⇒ 函数常数集中。

**飞腾锚点** 🟡 **TLB 4.81×**：等周不等式说的是「集合的边界/局部性」——边界小则质量不扩散。TLB（转译后备缓冲器）测的是内存访问的**局部性**：命中则快，缺页则慢。类比：集合边界小 = 访问局部性好 = 浓度紧；边界大（如散开的集合）= 局部性差 = 质量扩散 = 浓度松。两者都是「局部性决定集中/效率」。

**关键定理**：**Gaussian 等周不等式**——所有 Borel 集 $A$，$\gamma_n(A)=1/2$，则 $\gamma_n(A_t)\ge 1-\overline\Phi(\Phi^{-1}(1/2)+t)\ge 1-e^{-t^2/2}$（$A_t$ 为 $t$-邻域）。**推论（Lipschitz 浓度）**：$\mathbb{P}(|f-\mathbb{M}f|\ge t)\le 2e^{-t^2/(2\sigma^2)}$（$\mathbb{M}$ 中位数）。

**自测**：球面 $S^{n-1}$ 上 $1$-Lipschitz 函数 $f$，Lévy 引理给 $\mathbb{P}(|f-\mathbb{M}f|>t)\le ?$ 答：$\le 2e^{-c\,n t^2}$（$c$ 绝对常数）——维度越高浓度越紧，这就是「高维是友非敌」的几何真相。

---

## 第 8 章 · The Transportation Method（Transportation 方法：Marton、Talagrand）

**核心**：第三条证明路径——**transportation（最优运输）**。浓度不直接看 $f$，而看分布本身：若乘积测度 $P$ 与任意 $Q$ 的 Wasserstein 距离 $W_1(P,Q)$ 被 KL 散度 $D(Q\|P)$ 控制（**$T_1$ / $T_2$ 不等式**），则由 Pinsker / Marton 立刻得浓度。**Marton 不等式**：对乘积测度 $W_1\le\sqrt{2\sigma^2 D(Q\|P)}$（$T_2$）。**Talagrand transportation 不等式**把乘积情形做到最优。Bobkov-Götze 给出 transportation-熵的对偶刻画。本章的关键洞察：**transportation 与 entropy 是同一浓度现象的对偶面**——熵法走 MGF，transportation 走耦合/距离，殊途同归。

**飞腾锚点** 🟢 **Iron Law<2%**：$T_2$ 不等式 $W_1\le\sqrt{2\sigma^2 D}$ 把「分布间距离」锁在熵散度下——再代 Markov 即得 $\exp(-t^2/2\sigma^2)$ 浓度。这是**同一条误差铁律的另一条证明**：transportation 走耦合，entropy 走 MGF，等周走几何，三者推出同一条 sub-Gaussian 尾。本章的价值是「铁律的对偶视角」。

**关键定理**：**Marton $T_2$ 不等式**——乘积测度 $P^n$ 下，任意 $Q$：
$$W_2(P^n,Q)\le\sqrt{2\sigma^2\,D(Q\|P^n)}.$$
**Pinsker**：$W_1(P,Q)\le\sqrt{D(Q\|P)/2}$。推论：Lipschitz $f$ 在乘积测度下 sub-Gaussian，与 Ch5/Ch7 一致。

**自测**：为什么 $T_2$ 比 $T_1$（Pinsker）强？答：$T_2$ 控 $W_2$（平方距离），对 Lipschitz 函数浓度给出 sub-Gaussian 尾；$T_1$ 只控 $W_1$，给线性尾。Gaussian 满足 $T_2$，故一切 Lipschitz 函数 sub-Gaussian。

---

## 第 9 章 · Influences and Threshold Phenomena（影响与阈值现象）

**核心**：把浓度工具砸到**布尔函数**上，连接组合与相变。**变量影响**（influence）$I_i(f)=\mathbb{P}(f(X)\ne f(X^{\oplus i})$，度量翻转第 $i$ 比特改变输出的概率。**Russo 公式**：单调 $f$ 的期望随偏置 $p$ 的导数 $\tfrac{d}{dp}\mathbb{E}_p f=\sum_i I_i(f)$——总影响驱动相变。**KKL 定理**（Kahn-Kalai-Linial）：任意布尔函数必有某变量影响 $\ge c\,\mathrm{Var}(f)\cdot\tfrac{\log n}{n}$——「总有人影响显著大于平均」。这解释随机图（Erdős-Rényi）的**尖锐阈值**：如 $G(n,p)$ 连通性在 $p\approx\tfrac{\log n}{n}$ 处从 0 跳到 1 窗口 $O(1/n)$。

**飞腾锚点** 🟢 **分支预测**：布尔函数的影响 = 翻转一个比特是否改变输出，本质是**条件分支**。分支预测器（0.71 vs 3.14 CPI）擅长预测「多数比特翻转不改变结果」（低影响）的模式；高影响变量 = 难预测的分支 = 流水线气泡。KKL 说「必有难预测的分支存在」，阈值现象 = 大量分支同时翻转 = 相变。

**关键定理**：**KKL 定理**——布尔函数 $f:\{0,1\}^n\to\{0,1\}$，存在 $i$ 使 $I_i(f)\ge c\,\mathrm{Var}(f)\cdot\dfrac{\log n}{n}$（$c$ 绝对常数）。**Russo 公式**：$\tfrac{d}{dp}\mathbb{E}_p f=\sum_{i=1}^n I_i^{(p)}(f)$（$f$ 单调）。

**自测**：多数函数（majority）$f=\mathbb{1}[\sum X_i>n/2]$ 的影响？答：每个变量对称，$I_i\sim\binom{n-1}{(n-1)/2}2^{-(n-1)}\sim\sqrt{2/(\pi n)}$——比 KKL 下界 $(\log n)/n$ 大，KKL 不紧但方向对。

---

## 第 10 章 · Isoperimetry on the Hypercube and Gaussian Spaces（立方体与 Gaussian 空间的等周）

**核心**：把 Ch7 的几何浓度做**最锐**，分别在离散（hypercube）与连续（Gaussian）两端。**Harper 边-等周不变式**（edge-isoperimetric）：hypercube $\{0,1\}^n$ 中给定大小的子集，**初始段**（字典序前 $m$ 个）边界最小——这是 hypercube 上浓度的组合源头。**Gaussian 等周**（ revisit）：半空间最优，$t$-邻域余质量 $\le\overline\Phi(t)$。本章把「为何 sub-Gaussian 是最优常数」彻底讲透：半空间达到 Gaussian 浓度的精确下界，log-Sobolev 的常数 $2$ 与等周一致——几何与分析在最优点重合。

**飞腾锚点** 🟡 **Schmidt 正交化**：hypercube 的坐标 $\{0,1\}^n$ 与 Gaussian 的坐标轴都是**正交基**——浓度沿各正交方向分解，半空间 $=$ 沿某一正交方向的投影边界。Harper 初始段的边界结构本质上是对超立方体的正交分层切割，与 Gram-Schmidt 把向量分解到正交基同构。

**关键定理**：**Harper 边-等周定理**——hypercube 上 $|A|=m$ 的子集，其边界（端点恰一者在 $A$ 内的边数）$\ge$ 字典序初始段 $[m]$ 的边界。**Gaussian 等周**：半空间达到 $\inf\{\gamma_n(A_t):|A|=1/2\}$。

**自测**：hypercube 上 $|A|=2^{n-1}$（一半），最小边界的集合是？答：半空间 $\{x:x_1=1\}$（初始段），边界 $=2^{n-1}$（所有横跨 $x_1$ 的边）——这就是浓度的组合源头。

---

# Block E · 经验过程上确界（Ch11–13）⭐⭐⭐ ML 泛化界引擎

---

## 第 11 章 · The Variance of Suprema of Empirical Processes（经验过程上确界的方差）

**核心**：进入全书对 ML 理论最关键的 Block。定义经验过程 $Z=\sup_{f\in\mathcal{F}}\left|\dfrac{1}{n}\sum_{i=1}^n f(X_i)-\mathbb{E}f\right|$——这正是 Vapnik（刚做）泛化界里经验-真实风险之差的数学对象。本章先用 **symmetrization（对称化）** 把 $Z$ 的方差/期望控制在与 Ghost 样本 $X_i'$ 的差上，再用 Efron-Stein 得 $\mathrm{Var}(Z)\le$ 「单点影响的平方和」。关键结论：上确界的方差 $\le$ 两倍经验 Rademacher 复杂度的平方——把「最坏函数」的波动归结为「对随机符号的拟合能力」。这为 Ch12（指数尾界）和 Ch13（期望界）铺路。

**飞腾锚点** 🟢 **GEMM 9.45G**：$Z=\sup_{f\in\mathcal{F}}\tfrac1n|\sum_i f(X_i)-\mathbb{E}f|$ 要对**整个函数类** $\mathcal{F}$ 同时计算经验均值——若 $\mathcal{F}$ 是神经网络/线性类，即对大量 $f$ 做批量 $\sum_i f(X_i)$（矩阵 $\times$ 样本矩阵）。GEMM 9.45 GFLOPS 吞吐决定能否在工程上扫遍 $\mathcal{F}$ 算上确界。

**关键定理**：**symmetrization + 方差界**——
$$\mathrm{Var}(Z)\le 2\,\mathbb{E}\!\left[\sup_{f\in\mathcal{F}}\tfrac{1}{n}\sum_{i=1}^n\sigma_i f(X_i)\right]^2 = 2\,\mathbb{E}[\mathfrak{R}_n(\mathcal{F})^2],$$
其中 $\sigma_i$ 为 Rademacher 符号（$\pm1$ 等概），$\mathfrak{R}_n$ 为经验 Rademacher 复杂度。

**自测**：$\mathcal{F}=\{x\mapsto\mathbb{1}[w\cdot x>0]:\|w\|\le1\}$（线性分类器），$\mathfrak{R}_n(\mathcal{F})\sim?$ 答：$\sim 1/\sqrt{n}$（与 VC 维 $d+1$ 一起给 $\mathrm{Var}(Z)\le O(d/n)$）。

---

## 第 12 章 · Suprema of Empirical Processes: Exponential Inequalities（上确界指数不等式）⭐⭐⭐

**核心**：把 entropy method（Ch6）专门化到经验过程上确界，得到 ML 泛化界**直接引用**的尾界。**Bousquet 不等式**（Massart 版的改进）：用「可料」方差估计 $v$ 与上界 $b$，$P(Z\ge\mathbb{E}Z+t)\le\exp\!\left(-\tfrac{t^2/2}{v+bt/3}+\tfrac{t^3}{...}\right)$——形式似 Bernstein，但 $v$ 是**数据相关**的方差代理，比 Ch2 的固定界紧得多。这条不等式是 Vapnik VC 界（Ch6 VC 不等式 $\sqrt{d\log n/n}$）的**现代紧版**：Mohri（刚做）§3 的 Rademacher 泛化界、Shalev-Shwartz 的 PAC 收敛定理，全都在引用 Bousquet/Massart。

**飞腾锚点** 🟢 **Iron Law<2%**：Bousquet 不等式即**经验过程上确界的误差铁律**——泛化间隙 $\sup_f|(P_n-P)f|$ 以 $\exp(-ct^2)$ 被锁住。这是「为什么经验风险能代理真实风险」的最终数学裁决：只要 Rademacher 复杂度够小，泛化误差就被 Iron Law 钉死。

**关键定理**：**Bousquet 不等式**——$Z=\sup_{f\in\mathcal{F}}(P-P_n)f$，记 $v$ 为方差代理、$b$ 为一致上界，则
$$\mathbb{P}(Z\ge \mathbb{E}Z + t)\le \exp\!\left(-\frac{t^2/2}{v + 2b\,\mathbb{E}Z + 3bt/2}\right).$$
结合 Ch13 的 $\mathbb{E}Z\le 2\mathfrak{R}_n$，即得 Rademacher 泛化界。

**自测**：$\mathcal{F}$ 有限（$|\mathcal{F}|=M$），$f\in[0,1]$。Bousquet 给 $\sup_f|P_n f-Pf|$ 的阶？答：$\lesssim\sqrt{\log M/n}$（union bound + Hoeffding），即 $\mathbb{E}Z+t$ 主项 $\sim\sqrt{\log M/n}$。

---

## 第 13 章 · The Expected Value of Suprema of Empirical Processes（上确界的期望：chaining、Dudley、Rademacher）⭐⭐⭐

**核心**：上确界的**期望** $\mathbb{E}Z$ 怎么控制？这是复杂度度量的核心。**chaining（链）**：Dudley 熵积分 $\mathbb{E}Z\le C\int_0^D\sqrt{\log\mathcal{N}(\mathcal{F},\varepsilon)}\,d\varepsilon$（$\mathcal{N}$ 为覆盖数，$D$ 为直径）——多尺度地用「网格逼近」控制上确界，是经验过程的招牌技巧。**Rademacher 复杂度** $\mathfrak{R}_n(\mathcal{F})=\mathbb{E}\sup_f|\tfrac1n\sum\sigma_i f(X_i)|$ 是 $\mathbb{E}Z$ 的等价度量——数据相关、可估计，比 VC 维（数据无关最坏）紧得多。本章把 VC 维（Vapnik 刚做）→ 覆盖数 → Rademacher 的**复杂度谱**讲透，是 Mohri/Shalev-Shwartz 泛化界的数学源头。

**飞腾锚点** 🟢 **matmul 15×**：Rademacher 复杂度 $\mathfrak{R}_n=\mathbb{E}\sup_f|\tfrac1n\sum_i\sigma_i f(X_i)|$——把 $n$ 个样本的函数值排成矩阵 $F\in\mathbb{R}^{|\mathcal{F}|\times n}$，乘随机符号 $\sigma$，取每行绝对值再 max。这是**矩阵 × 向量**（$F\sigma$），matmul 15× 向量化是 Rademacher 复杂度蒙特卡洛估计的硬件基础。

**关键定理**：**Dudley 熵积分界**——$\mathbb{E}\sup_{f\in\mathcal{F}}(P-P_n)f\le \dfrac{C}{\sqrt{n}}\int_0^{D}\sqrt{\log\mathcal{N}(\mathcal{F},\varepsilon,\|\cdot\|)}\,d\varepsilon$。**Rademacher 等价**：$\mathbb{E}Z\le 2\mathfrak{R}_n(\mathcal{F})$。对 VC 维 $d$ 类，$\mathfrak{R}_n\le C\sqrt{d/n}$。

**自测**：$\mathcal{F}=\{x\mapsto\mathbb{1}[x\le\theta]:\theta\in\mathbb{R}\}$（一维阈值，VC 维 2）。Dudley 给 $\mathfrak{R}_n$ 阶？答：$\sim 1/\sqrt{n}$（覆盖数 $\mathcal{N}\sim 1/\varepsilon$，积分为常数），与 VC 界 $\sqrt{2/n}$ 一致。

---

# Block F · 推广（Ch14–15）

---

## 第 14 章 · Φ-Entropies（Φ-熵：熵方法的推广）

**核心**：把 entropy method 的 $\Phi(x)=x\log x$ 推广到**一般凸函数 $\Phi$**。定义 $\Phi$-熵 $\mathrm{Ent}_\Phi(Z)=\mathbb{E}[\Phi(Z)]-\Phi(\mathbb{E}Z)$，研究何时它满足 tensorization（$\mathrm{Ent}_\Phi(Z)\le\sum_i\mathbb{E}\,\mathrm{Ent}_{\Phi,(i)}(Z)$）。关键特例：$\Phi(x)=x^p$（power entropy）恢复**方差/高阶矩**结构（$p=2$ 即方差），$\Phi(x)=-\log x$ 关联信息论。本章把 Ch3（方差）与 Ch5（log-熵）统一进一个框架，并给出**广义 log-Sobolev**——同一代数骨架，不同 $\Phi$ 产生不同矩阶的浓度。它是 Ch15（矩不等式）的代数基础。

**飞腾锚点** 🟡 **UDOT 16.9×**：$\Phi$-熵 tensorization 仍是 $\sum_i$ 求和（条件项）+ $\mathbb{E}[\Phi]$（加权求和）；选 $\Phi(x)=x^2$ 时 $\mathrm{Ent}_\Phi=\mathrm{Var}$ 即 Ch3 的方差分解（Parseval 式正交求和）。同一求和骨架，UDOT 是它的工程原语。

**关键定理**：**$\Phi$-熵 tensorization 准则**——$\mathrm{Ent}_\Phi$ 张量化 $\iff$ $x\mapsto x\Phi'(x)-\Phi(x)$ 凸（对若干 $\Phi$，如 $x^p$、$x\log x$ 成立）。**power-entropy 浓度**：$\Phi(x)=x\log x$ 给 sub-Gamma，$\Phi(x)=x^p$ 给 $p$-矩界。

**自测**：$\Phi(x)=x^2$，$\mathrm{Ent}_\Phi(Z)=?$ 是否 tensorize？答：$\mathrm{Ent}_\Phi=\mathbb{E}Z^2-(\mathbb{E}Z)^2=\mathrm{Var}(Z)$；独立时 $\mathrm{Var}$ 可加（线性函数），故 tensorize——这正是 Efron-Stein 的 $\Phi$-熵源头。

---

## 第 15 章 · Moment Inequalities（矩不等式）

**核心**：从尾部到**全矩序列**——给出 $\mathbb{E}|Z-\mathbb{E}Z|^q$ 对所有 $q$ 的界。**矩不等式**：若 $Z$ sub-Gaussian，则 $(\mathbb{E}|Z|^q)^{1/q}\le C\sqrt{q}$（矩增长 $\sqrt{q}$）；sub-exponential 给 $q$；一般自界函数给 $q^{1/\alpha}$ 增长。矩视角的优势：$\sup_q$ 即尾部，逐 $q$ 给出精细的「中等偏差」刻画，是 Vershynin（已读）$\psi_\alpha$ 范数的源头。本章把 Ch2–6 的尾部浓度翻译成矩增长语言，与 Ch14 的 power-entropy 闭环：**矩增长 $\Leftrightarrow$ $\Phi$-熵 $\Leftrightarrow$ 尾部浓度，三语言等价**。

**飞腾锚点** 🟡 **Iron Law<2%**：各阶矩界是 Iron Law 的**完整频谱**——sub-Gaussian 的 $\sqrt{q}$ 矩增长对应 $\exp(-t^2)$ 尾；sub-exponential 的 $q$ 增长对应 $\exp(-t)$ 尾。矩序列把「误差铁律」展开成无穷阶，每一阶都是一个尺度的误差预算。

**关键定理**：**矩-尾部等价**——$(\mathbb{E}|Z|^q)^{1/q}\le K\sqrt{q}\;\forall q\ge1$ $\iff$ $Z$ sub-Gaussian（$\mathbb{P}(|Z|>t)\le 2e^{-ct^2}$）。**自界函数矩界**：$\|Z-\mathbb{E}Z\|_q\le\sqrt{2e\,q\,\mathbb{E}Z^*}+eq\,Z^*_{\max}$（sub-Gamma 矩形式）。

**自测**：$Z\sim\mathcal{N}(0,1)$，$(\mathbb{E}|Z|^q)^{1/q}$ 增长？答：$\sim\sqrt{q/e}$（Gaussian 矩 $\sim\sqrt{2}(\Gamma((q+1)/2))^{1/q}\sim\sqrt{q}$）——sub-Gaussian 矩增长 $\sqrt{q}$ 的原型。

---

## §9 全书思想主线（约 220 字）

BLM 的统一主线是「**独立 + 影响有界 ⇒ 指数集中**」，由四条**对偶**证明路径汇聚而成。**方差路径**（Ch3，Efron-Stein/Poincaré）：二阶矩视角，最朴素但只给 $1/t^2$ 弱浓度——它揭示钥匙是「每变量局部影响之和」。**熵路径**（Ch4–6，tensorization → log-Sobolev → Herbst）：把钥匙从二阶矩升级到指数矩，Herbst argument 一步把 log-Sobolev 解成 sub-Gaussian——全书引擎。**几何路径**（Ch7、10，Gaussian/hypercube 等周）：浓度是集合边界小的推论，半空间达到最优常数。**transportation 路径**（Ch8，Marton/Talagrand）：浓度是分布间 Wasserstein 距离被 KL 控制的推论。**四条路推出同一条尾部** $\exp(-ct^2)$——这是现代概率最深刻的统一之一。Ch11–13 把工具砸到经验过程上确界，**直接生成 ML 泛化界**（Bousquet/Massart 尾 + Rademacher/Dudley 期望），是 Vapnik/Mohri/Shalev-Shwartz 一切泛化定理的数学心脏。

**一句话**：BLM 教你「**为什么 Hoeffding/log-Sobolev/Bousquet 成立、它们如何统一、又如何钉死泛化误差**」——读完本书，应能回答 Vershynin/Wainwright/Mohri（已读）背后所有尾界的**原始推导**：sub-Gaussian 从哪来？为什么 Lipschitz 函数常数集中？Rademacher 界为何紧？答案都在 BLM 四条路径的交汇处。与已读教材呼应：Vershynin 是 BLM 的概率工具入门版，Mohri 是 Ch11–13 的算法化，Vapnik 是 Ch11–13 的应用场景原典。

---

## §10 与本仓库其他笔记的交叉引用

**同类教材对比**：

1. **vs [Vapnik SLT](vapnik_统计学习理论_快速逐章.md)（刚做）**：Vapnik 的 VC 泛化界（Ch6 VC 不等式 $\sqrt{d\log n/n}$）在数学上正是 BLM **Ch11–13** 的特殊化——VC 维 $d$ 是数据无关的最坏复杂度，BLM 的 Rademacher/Dudley 给出数据相关的紧版。Vapnik 用 BLM 的工具（虽未点名）推出一致收敛；BLM 给出这些工具的**完整方法谱**。
2. **vs [Mohri FoML](mohri_机器学习理论基础_快速逐章.md)（刚做）**：Mohri §3（Rademacher 复杂度）+ §4（VC 维）= BLM **Ch11–13** 的算法化重写。Mohri 的泛化界直接引用 Bousquet 不等式（BLM Ch12），Mohri 的 Rademacher 收敛定理是 BLM Ch13 的应用。读 BLM Ch12 后，Mohri 的证明会「透明」。
3. **vs [Vershynin 高维概率](vershynin_高维概率_快速逐章.md)（已读）**：Vershynin Ch2（sub-gaussian/Hoeffding）= BLM **Ch2** 入门版；Vershynin Ch7（一致收敛/VC）= BLM Ch11–13 概率侧。但 Vershynin Ch9（**矩阵** Bernstein）超出 BLM 范围——BLM 是**标量**浓度专著，矩阵集中需补 Ahlswede-Winter/Tropp。
4. **vs [Wainwright 高维统计](wainwright_高维统计_快速逐章.md)（已读）**：Wainwright 全书以 BLM 的浓度工具为底座做高维统计推断（oracle 不等式、极小极大、信息下界）。Wainwright 的 Ch2（基本浓度）≈ BLM Ch2–6 浓缩。
5. **vs [Shalev-Shwartz UML](shalev_shwartz_理解机器学习_快速逐章.md)（已读）**：Shalev-Shwartz 的 PAC 收敛定理（Ch6 基本定理、Ch26 Rademacher、Ch31 PAC-Bayes）数学根基全在 BLM Ch11–12。PAC-Bayes 的 KL-散度界尤其依赖 entropy/transportation（BLM Ch4/Ch8）。
6. **vs [Cover-Thomas 信息论](cover_thomas_信息论_快速逐章.md)（已读）**：BLM Ch4 的 $\mathrm{Ent}$、Han 不等式、tensorization 与 Cover-Thomas 的熵-典型集-AEP 共享同一信息论根。BLM 把信息论从「编码」用到「浓度」——大偏差的两种面貌。

**AI/工程锚点（4 条）**：

7. **🟢 深度学习泛化与双下降**：BLM Ch11–13 的经验过程上确界浓度是泛化界的标准工具，但深度网 VC 维 $\sim W\log W\gg n$（Vapnik Ch16 开放问题），BLM 的 VC 界失效——需 Rademacher/PAC-Bayes/隐式正则补充，对接 [Goodfellow 深度学习](goodfellow_深度学习_快速逐章.md)。双下降现象挑战的就是 BLM Ch12 的 Bousquet 界。
8. **🟢 PAC-Bayes 与压缩估计**：BLM Ch13 提到的压缩估计、聚合（model selection / aggregation）是 PAC-Bayes 的工程入口；McAllester / Catoni 的 PAC-Bayes 界用 KL 散度（BLM Ch4 的 $\mathrm{Ent}$）替代 VC 维，对接 [Shalev-Shwartz Ch31](shalev_shwartz_理解机器学习_快速逐章.md)。
9. **🟡 差分隐私（differential privacy）**：privacy 的核心保证 $\mathbb{P}(M(x)\in S)\le e^\varepsilon\mathbb{P}(M(x')\in S)$ 本质是**浓度/transportation**（BLM Ch8 的 $T_\infty$）——噪声机制（Laplace/Gaussian）的隐私-效用权衡用 BLM 的浓度工具分析。
10. **🟡 强化学习的 concentration of measure**：RL 中的 PAC-MDP、regret 界依赖样本浓度（Hoeffding/Bernstein，BLM Ch2）与 high-probability 界；蒙特卡洛策略评估的方差用 Efron-Stein（BLM Ch3），对接 [Sutton-Barto RL](sutton_barto_强化学习_快速逐章.md)。

### 飞腾锚点速查（15 章 · 7 锚点分散覆盖）

| 锚点 | 章节 | 主题 |
|:------|:------|:------|
| **Iron Law<2% ⭐** | **Ch1⭐**, **Ch5⭐**, **Ch8⭐**, **Ch12⭐**, Ch15 | 浓度=误差铁律（现象/log-Sobolev 最强/transportation 对偶/Bousquet 泛化铁律/矩频谱） |
| **UDOT 16.9× ⭐** | Ch2, **Ch4⭐**, **Ch6⭐**, Ch14 | 求和/期望（MGF/熵 tensorization/entropy method/Φ-熵） |
| **matmul 15×** | Ch3, **Ch13⭐** | 二次型/矩阵（方差梯度/Rademacher 矩阵×符号） |
| **GEMM 9.45G ⭐** | **Ch11⭐** | 高维吞吐（经验过程上确界批量扫描函数类） |
| **TLB 4.81×** | Ch7 | 局部性（等周=集合边界小=局部性好） |
| **分支预测 ⭐** | **Ch9⭐** | 条件分支（布尔影响/翻转比特/阈值相变） |
| **Schmidt 正交化** | Ch10 | 正交基（hypercube/Gaussian 坐标正交分解） |

### 核心符号速查

| 符号 | 含义 | 首现 |
|:------|:------|:------|
| $\mathrm{Ent}(Z)$ | 熵泛函 $=\mathbb{E}[Z\log Z]-\mathbb{E}Z\log\mathbb{E}Z$ | Ch4 |
| $\|\nabla f\|^2$ | 梯度能量（Poincaré/log-Sobolev 右端） | Ch3/Ch5 |
| $Z_i'$ | leave-one-out 替换第 $i$ 变量后的 $Z$ | Ch3 |
| $\mathcal{N}(\mathcal{F},\varepsilon)$ | $\mathcal{F}$ 的 $\varepsilon$-覆盖数 | Ch13 |
| $\mathfrak{R}_n(\mathcal{F})$ | Rademacher 复杂度 $=\mathbb{E}\sup_f|\tfrac1n\sum\sigma_i f(X_i)|$ | Ch11/Ch13 |
| $I_i(f)$ | 布尔函数第 $i$ 变量的影响 | Ch9 |
| $W_p(P,Q)$ | $p$-Wasserstein 距离 | Ch8 |
| $\Phi$ | 广义熵凸函数（$x\log x$、$x^p$） | Ch14 |

---

> **续读指引**：精读 BLM 后，① ML 泛化深化 → 重读 [Mohri §3/§4](mohri_机器学习理论基础_快速逐章.md)（此时 Rademacher/Bousquet 证明全透明）+ [Vapnik Ch6/Ch11](vapnik_统计学习理论_快速逐章.md)（VC 界的紧版来源）；② 矩阵浓度 → 补 Tropp《Matrix Concentration》或 [Vershynin Ch9](vershynin_高维概率_快速逐章.md)（BLM 不含矩阵版）；③ 现代前沿 → 高维统计推断 [Wainwright](wainwright_高维统计_快速逐章.md) + 深度学习泛化（双下降/NTK，回应 BLM Ch11–13 的过参数化挑战）。**本书是理解一切 ML 泛化界尾部推导的「工具母机」**。
