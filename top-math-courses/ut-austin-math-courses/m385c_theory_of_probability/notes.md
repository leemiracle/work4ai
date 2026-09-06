# UT Austin M 385C · 概率论笔记（Durrett *Probability: Theory and Examples*）

> **教材**：Durrett, *Probability: Theory and Examples* (5th ed, Cambridge, 2019) — **免费 PDF**
> **一手核实**：services.math.duke.edu/~rtd/PTE/PTE5_011119.pdf + UT Austin Probability Prelim 大纲
> **定位**：研究生测度论概率；UT Probability Prelim 第一学期（与 [MIT 18.175](../../mit-math-courses/18_175_probability/) 同级金课）

---

## 费曼三层讲透

### 🟢 直觉层

- **概率空间 = 三件套**：样本空间 $\Omega$（所有可能）、σ-代数 $\mathcal{F}$（你能观测的事件）、测度 $P$（给每个事件一个数）。$\mathcal{F}$ = "你知道的信息"。
- **σ-代数 = 信息**：$\mathcal{F}_n\subseteq\mathcal{F}_{n+1}$ 表示"时间向前，信息增多"（滤波）。 filtration = 信息逐步揭示的过程。
- **收敛的四种"味道"**：几乎必然（每条轨迹都收敛）、依概率（差距大的概率趋于 0）、$L^p$（均方意义收敛）、依分布（CDF 收敛）。越往下越弱。
- **LLN = 平均值稳定下来**：掷骰子很多次，平均点数趋于 3.5——这"趋于"是几乎必然的。
- **CLT = 波动变成正态**：很多独立扰动的和，总扰动形状像钟形曲线（正态）。
- **鞅 = 公平赌博**：无论你怎么下注，期望财富永远等于当前财富。$E[X_{n+1}|\mathcal{F}_n]=X_n$。
- **条件期望 = 最佳预测**：$E[Y|\mathcal{G}]$ = 在已知信息 $\mathcal{G}$ 下，对 $Y$ 的最优（$L^2$）估计。几何上是**投影**。
- **Brownian motion = 处处抖动的曲线**：连续但处处不可导，每个瞬间都在随机抖动。

**反例（警惕）**：
- **重尾让 CLT 失效**：Cauchy 分布的样本均值 $\bar X_n$ 与单个 $X_1$ 同分布——永不收敛！CLT 需要**有限方差**。
- **可选停时不能乱用**：鞅 $S_n$ 在停时 $\tau$ 处 $E[S_\tau]=E[S_0]$ 需要条件（有界 / 一致可积）。否则出"必胜策略"悖论（如加倍下注法）。
- **a.s. 收敛不蕴含 $L^1$ 收敛**：$X_n=n\mathbf{1}_{(0,1/n)}$ 在 $(0,1)$ 上 a.s.→0 但 $E[X_n]=1$ 不趋于 0（无一致可积）。

---

### 🔵 数学层

## 核心框架

```
测度论 → 概率空间 → 收敛模式 → LLN/CLT → 条件期望 → 鞅 → Brownian → 集中不等式
─────   ────────   ────────   ─────────   ────────   ──   ────────   ──────────
σ-代数   (Ω,F,P)    a.s./P/d    SLLN       RN定理      停时    W_t        Hoeffding
Lebesgue  独立性      Lp         CLT        投影视角    可选停时  反射原理    McDiarmid
积分      滤波        Berry-Esseen  特征函数  鞅         鞅收敛   Itô积分    Azuma
```

---

## 第 1 章：概率空间与测度论 ★★★

### 1.1 概率三元组

$(\Omega,\mathcal{F},P)$：
- $\Omega$：样本空间
- $\mathcal{F}$：$\Omega$ 上的 **σ-代数**（对可数并、补封闭的事件族）
- $P:\mathcal{F}\to[0,1]$：概率测度，$P(\Omega)=1$，$P(\bigcup A_i)=\sum P(A_i)$（不交）

### 1.2 随机变量与可测性

$X:\Omega\to\mathbb{R}$ 是 $\mathcal{F}$-**可测**的 $\Leftrightarrow \{X\leq x\}\in\mathcal{F},\forall x$。

→ "可测" = "你能用 $\mathcal{F}$ 的信息确定 $X$ 的值"。

### 1.3 Lebesgue 积分与期望

$$E[X]=\int X\,dP=\int_0^\infty P(X>t)\,dt-\int_{-\infty}^0 P(X<t)\,dt$$

**三大收敛定理**（交换极限与积分的工具）：

| 定理 | 条件 | 结论 |
|---|---|---|
| **MCT** 单调收敛 | $0\leq X_n\uparrow X$ | $E[X_n]\uparrow E[X]$ |
| **DCT** 控制收敛 | $\|X_n\|\leq Y,EY<\infty,X_n\to X$ a.s. | $E[X_n]\to E[X]$ |
| **Fatou** | $X_n\geq 0$ | $E[\liminf X_n]\leq\liminf E[X_n]$ |

**ML 关联**：DCT 是推导"交换期望与极限"的标准工具（如 SGD 分析中交换梯度与求和）。

---

## 第 2 章：收敛模式 ★★★

| 模式 | 定义 | ML 含义 |
|---|---|---|
| **a.s.** $X_n\xrightarrow{a.s.}X$ | $P(X_n\to X)=1$ | SGD 确定性收敛 |
| **$L^p$** $X_n\xrightarrow{L^p}X$ | $E\|X_n-X\|^p\to 0$ | 均方收敛（参数估计） |
| **依概率** $X_n\xrightarrow{P}X$ | $P(\|X_n-X\|>\epsilon)\to 0$ | 弱收敛保证 |
| **依分布** $X_n\xRightarrow{d}X$ | $F_n\to F$（连续点） | CLT（渐近分布） |

**蕴含**：$a.s.\Rightarrow P\Rightarrow d$；$L^p\Rightarrow P$。**反向不成立**（除非额外条件）。

### 反例：a.s. 收敛 ≠ $L^1$ 收敛

$X_n=n\mathbf{1}_{(0,1/n)}$（在 $[0,1]$ 均匀测度上）：$X_n\to 0$ a.s.（点态），但 $E[X_n]=1$ 不趋于 0。→ 缺**一致可积性**。

---

## 第 3 章：大数定律 ★★

### 3.1 强大数定律（SLLN）★★★

> $X_1,X_2,\dots$ i.i.d.，$E\|X_i\|<\infty$，$\mu=E[X_i]$，$S_n=\sum_{i=1}^n X_i$，则
> $$\frac{S_n}{n}\xrightarrow{a.s.}\mu$$

**证明思路**（Durrett 截断法）：
1. 截断 $Y_k=X_k\mathbf{1}_{\|X_k\|\leq k}$
2. Borel-Cantelli：$X_k=Y_k$ a.s.（$k$ 大）
3. Chebyshev + **Kronecker 引理**：$\frac{1}{n}\sum Y_k\to\mu$

**ML 关联**：SGD 收敛的理论根基——"小批量梯度平均几乎必然收敛到真实梯度"。

### 3.2 Borel-Cantelli 引理

- $A_n$ 任意，$\sum P(A_n)<\infty\Rightarrow P(A_n\text{ i.o.})=0$
- $A_n$ 独立，$\sum P(A_n)=\infty\Rightarrow P(A_n\text{ i.o.})=1$

→ "无限次发生"的 0-1 律。

---

## 第 4 章：中心极限定理 ★★★

### 4.1 特征函数

$$\varphi_X(t)=E[e^{itX}]\quad\text{（分布的 Fourier 变换）}$$

- $\varphi_X$ **唯一**确定分布
- 独立和：$\varphi_{X+Y}=\varphi_X\varphi_Y$
- $E[X^k]=i^{-k}\varphi^{(k)}(0)$（若存在）

### 4.2 CLT ★★★

> $X_i$ i.i.d.，$E[X_i]=\mu$，$\text{Var}=\sigma^2\in(0,\infty)$，则
> $$\frac{S_n-n\mu}{\sigma\sqrt{n}}\xRightarrow{d}N(0,1)$$

**证明**（特征函数法）：
1. $\varphi_{(S_n-n\mu)/(\sigma\sqrt n)}(t)=[\varphi_{(X-\mu)/\sigma}(t/\sqrt n)]^n$
2. Taylor：$\varphi(t/\sqrt n)\approx 1+(it)^2/(2n)+o(1/n)$
3. $[1+(it)^2/(2n)]^n\to e^{-t^2/2}$（标准正态特征函数）

**ML 关联**：
- mini-batch 梯度噪声正态化 $\Rightarrow$ BatchNorm
- MLE 的**渐近正态性**：$\sqrt n(\hat\theta-\theta)\xRightarrow{d}N(0,I^{-1}(\theta))$（Fisher 信息）
- 权重初始化（He / Xavier 用正态控制激活方差）

### 4.3 Berry-Esseen（收敛速度）

$$\sup_x|F_n(x)-\Phi(x)|\leq\frac{C\,E\|X_i\|^3}{\sigma^3\sqrt n}$$

→ CLT 近似误差 $O(1/\sqrt n)$，给出**有限样本**的精确常数。

### 4.4 CLT 的失效（重尾）⚠️

若 $X$ 服从 Cauchy 分布（密度 $\frac{1}{\pi(1+x^2)}$，方差不存在），则 $\bar X_n$ 与 $X_1$ **同分布**——CLT 完全失效。

→ 广义 CLT 需用**稳定分布**（Stable distribution）。

---

## 第 5 章：条件期望 ★★

### 5.1 定义（Radon-Nikodym 视角）

$Y=E[X|\mathcal{G}]$ 是 $\mathcal{G}$-可测且
$$\int_A Y\,dP=\int_A X\,dP,\quad\forall A\in\mathcal{G}$$

（存在性由 Radon-Nikodym 定理保证，需 $X\in L^1$。）

### 5.2 关键性质

- **塔性质**：$E[E[X|\mathcal{G}]]=E[X]$（全期望公式）
- 独立：$X\perp\mathcal{G}\Rightarrow E[X|\mathcal{G}]=E[X]$
- 可测：$X$ 是 $\mathcal{G}$-可测 $\Rightarrow E[X|\mathcal{G}]=X$
- **Jensen**：$E[\varphi(X)|\mathcal{G}]\geq\varphi(E[X|\mathcal{G}])$（凸 $\varphi$）

### 5.3 $L^2$ 投影视角 ★

在 $L^2$ 中，$E[X|\mathcal{G}]$ = $X$ 到 $\mathcal{G}$-可测函数子空间的**正交投影**（投影误差与 $\mathcal{G}$ 正交）。

**ML 关联**：回归 / 最小二乘 = 条件期望的逼近；条件期望 = "给定信息的最佳预测"。

---

## 第 6 章：鞅 ★★★

### 6.1 定义

$X_n$ 关于滤波 $\mathcal{F}_n$ 是**鞅** $\Leftrightarrow$：
1. $X_n$ 是 $\mathcal{F}_n$-可测
2. $E\|X_n\|<\infty$
3. $E[X_{n+1}|\mathcal{F}_n]=X_n$

（下鞅 $\geq$；上鞅 $\leq$。）

### 6.2 经典例子

- $S_n=\sum X_i$（i.i.d. 均值 0）是鞅
- **Doob 鞅**：$X_n=E[Y|\mathcal{F}_n]$（信息逐步揭示）
- 似然比 $L_n=\prod q(X_i)/p(X_i)$（在 $p$ 下是鞅）
- $S_n^2-n$（当 $X_i=\pm1$）是鞅

### 6.3 可选停时定理 ★

$\tau$ 是停时（$\{\tau\leq n\}\in\mathcal{F}_n$）。**条件下**：
$$E[X_\tau]=E[X_0]$$

**条件**（至少满足其一）：$\tau$ 有界 / $X_n$ 一致可积 / $P(\tau<\infty)=1$ 且 $E\|X_\tau\|<\infty$ 且 $\lim E[X_n\mathbf{1}_{\tau>n}]=0$。

**反例（加倍下注法）**：对称游走，$\tau$=首次赢。$P(\tau<\infty)=1$，但 $E[\tau]=\infty$ 且 $E[S_\tau]\neq0$（可选停时**失效**！）→ "必胜策略"是数学幻觉。

**应用**：对称游走首达 $\pm a$ 的 $E[\tau]=a^2$（用 $S_n^2-n$ 是鞅 + 可选停时）。

### 6.4 鞅收敛定理

> $L^1$-有界的下鞅 $\Rightarrow$ $X_n\xrightarrow{a.s.}X_\infty$（$E\|X_\infty\|<\infty$）。

### 6.5 Doob 分解与不等式

- **分解**：$X_n=M_n+A_n$（鞅 + 可料增序列）
- **Doob 极大值不等式**：$P(\max_{k\leq n}\|X_k\|\geq\lambda)\leq E[X_n^2]/\lambda^2$

**ML 关联**：
- RL 的 **TD 学习**：TD 误差在真值函数处是**鞅差**，期望为 0 → 收敛性
- 联机学习 regret bound（Azuma-Hoeffding）
- SGD：梯度噪声是鞅差 → Azuma 给收敛速率

---

## 集中不等式（ML 理论核心工具）★★★

| 不等式 | 条件 | 结论 | ML 用途 |
|---|---|---|---|
| **Markov** | $X\geq 0$ | $P(X\geq a)\leq E[X]/a$ | 基础 |
| **Chebyshev** | — | $P(\|X-\mu\|\geq a)\leq\sigma^2/a^2$ | 弱界 |
| **Chernoff** | 独立 | $P(S_n\geq(1+\delta)\mu)\leq e^{-\mu\delta^2/3}$ | 强界 |
| **Hoeffding** ★ | $X_i\in[a_i,b_i]$ | $P(\|S_n-ES_n\|\geq t)\leq 2e^{-2t^2/\sum(b_i-a_i)^2}$ | **泛化界核心** |
| **Bernstein** | 亚高斯 | $P(\|S_n\|\geq t)\leq 2\exp(-\frac{t^2}{2(\sigma^2+Mt/3)})$ | 重尾 |
| **McDiarmid** ★ | Lipschitz $f$ | $P(\|f-Ef\|\geq t)\leq 2e^{-2t^2/\sum c_i^2}$ | **算法稳定性** |
| **Azuma** | 鞅差 $\|D_i\|\leq c_i$ | $P(\|M_n-M_0\|\geq t)\leq 2e^{-t^2/(2\sum c_i^2)}$ | **联机学习** |
| **Jensen** | $\varphi$ 凸 | $\varphi(E[X])\leq E[\varphi(X)]$ | 不等式起点 |

### Hoeffding → PAC 泛化界 ★★★

$X_i\in[0,1]$（0-1 损失），$\hat R(h)=\frac{1}{n}\sum\ell(h,x_i)$：
$$P(|\hat R(h)-R(h)|>\epsilon)\leq 2e^{-2n\epsilon^2}$$

Union bound over $\|\mathcal H\|$ 个假设：
$$P(\exists h:|\hat R-R|>\epsilon)\leq 2|\mathcal H|e^{-2n\epsilon^2}$$

令 $=\delta$：$\epsilon=\sqrt{\frac{\ln(2|\mathcal H|/\delta)}{2n}}$ → **PAC 泛化界**。

---

## 第 7 章：Brownian Motion ★★

### 定义

$W_t$ 满足：$W_0=0$；增量独立；$W_t-W_s\sim N(0,t-s)$；路径连续。

### 关键性质

- **自相似**：$W_{at}\stackrel{d}{=}\sqrt a\,W_t$
- **反射原理**：$P(\max_{s\leq t}W_s\geq a)=2P(W_t\geq a)$
- **不可导**：处处连续但处处不可导（Hölder $<1/2$）

### Itô 积分与引理

$$df(W_t)=f'(W_t)\,dW_t+\frac{1}{2}f''(W_t)\,dt$$

多出 $\frac{1}{2}f''dt$！因为 $(dW_t)^2=dt$（非零，二次变差）。

**ML 关联**：扩散模型 = 反向 Itô SDE。Score matching = 估计 SDE 漂移项。

---

## Diffusion Model 的 SDE 基础 ★★★

### 前向 SDE（加噪）

$$dX_t=-\frac{1}{2}\beta(t)X_t\,dt+\sqrt{\beta(t)}\,dW_t$$

边际：$X_t|X_0\sim N(\sqrt{\bar\alpha_t}X_0,(1-\bar\alpha_t)I)$。

### 反向 SDE（生成）

Anderson (1982)：$dX_t=[-\frac{1}{2}\beta(t)X_t-\beta(t)\nabla\log p_t(X_t)]dt+\sqrt{\beta(t)}\,d\bar W_t$

关键：需 **score function** $\nabla\log p_t(x)$。

### Score Matching

训练 $s_\theta(x,t)\approx\nabla\log p_t(x)$，等价于 DDPM（Ho et al., arXiv:2006.11239 ✅）的噪声预测。

---

## 🟠 不足层（局限性）

1. **i.i.d. 假设**：集中不等式通常需独立。时间序列 / 图数据 / 对抗样本违反 i.i.d. → 鞅方法或混合条件替代。
2. **高维灾难**：$O(\sqrt{d/n})$ 的界在高维下很松；集中不等式常数在 $d$ 大时可能很大。
3. **重尾让 CLT 失效**：Cauchy / Pareto 方差不存在；需稳定分布或重尾理论。
4. **Itô 积分非直觉**：$(dW_t)^2=dt$ 让物理直觉失效；Stratonovich 更物理但不便数学。
5. **可选停时的微妙条件**：忽略一致可积条件会推出"必胜策略"悖论。
6. **频率派 vs 贝叶斯派**：测度论框架为两者提供统一语言，但"概率是频率还是信念"的哲学之争测度论无法裁决。

---

## 🔴 应用层（ML 公式级对应）

| 概念 | 公式 | ML 场景 |
|---|---|---|
| SLLN | $\frac{S_n}{n}\xrightarrow{a.s.}\mu$ | SGD 收敛 |
| CLT | $\frac{S_n-n\mu}{\sigma\sqrt n}\Rightarrow N(0,1)$ | BatchNorm / MLE 渐近正态 |
| Berry-Esseen | $\sup\|F_n-\Phi\|\leq C/\sqrt n$ | 有限样本泛化界常数 |
| Hoeffding | $P(\|\hat R-R\|>\epsilon)\leq 2e^{-2n\epsilon^2}$ | **泛化界** |
| McDiarmid | $P(\|f-Ef\|\geq t)\leq 2e^{-2t^2/\sum c_i^2}$ | 算法稳定性 |
| Azuma | $P(\|M_n-M_0\|\geq t)\leq 2e^{-t^2/(2\sum c_i^2)}$ | 联机学习 regret |
| 鞅 + 可选停时 | $E[X_\tau]=E[X_0]$ | RL TD 学习 |
| 条件期望 = 投影 | $E[Y\|\mathcal{G}]=\Pi_{\mathcal{G}}Y$ | 回归 |
| Brownian + Itô | $df=f'dW+\frac12 f''dt$ | 扩散模型 SDE |
| Markov 遍历 | $\frac1n\sum f(X_k)\to E_\pi f$ | MCMC |

---

## 与 work4ai 讲透系列的交叉

- **讲透泛化**：Hoeffding + McDiarmid + PAC-Bayes（本课集中不等式 + 信息论）
- **讲透 SGD**：SLLN + CLT + 鞅方法（梯度噪声 = 鞅差）
- **讲透扩散模型**：Brownian + 反向 SDE + score matching（DDPM arXiv:2006.11239 ✅）
- **讲透强化学习**：鞅 → TD 学习；Markov 链 → MDP
- **讲透统计学习理论**：Hoeffding + VC 维 + Rademacher 复杂度

---

## 与同级课程的对照

| 课程 | 教材 | 特色 |
|---|---|---|
| **MIT 18.175** | Durrett | 与本课同教材，ML 理论核心 |
| **Stanford Math 230A** | Durrett / Dembo | 测度论概率，更偏统计 |
| **Princeton MAT 514** | Durrett | Prelim 序列 |
| **Oxford B8.1** | Williams | 英式严格，鞅论强 |
| **Cambridge Part II** | Williams | 测度论概率金课 |
