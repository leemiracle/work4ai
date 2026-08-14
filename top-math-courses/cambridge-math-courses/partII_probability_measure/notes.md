# Cambridge Part II · Probability and Measure 章节笔记（Williams *Probability with Martingales*）

> **教材**：Williams, *Probability with Martingales* (CUP, 1991) — **本科测度论概率金课**
> **一手核实**：Cambridge Part II Michaelmas D-course 大纲
> **风格**：英式幽默 + 直觉 + 严格证明（Williams 独特的 "rapid" 风格）

---

## 费曼三层讲透

### 🟢 直觉层

- **σ-代数 $\mathcal{F}$** = "你当前知道的信息"：事件 $A \in \mathcal{F}$ 表示"你能判断 $A$ 是否发生"
- **条件期望 $E[Y|\mathcal{F}]$** = "在你已知信息 $\mathcal{F}$ 下，对 $Y$ 的最佳预测"
- **鞅** = "公平赌博"：你的期望财富永远等于初始财富 $E[X_{n+1}|\mathcal{F}_n] = X_n$
- **概率 = 不确定性的大小，但频率派和贝叶斯派对'概率是什么'有根本分歧**

---

### 🔵 数学层

## 核心框架

```
测度论基础 → 概率空间 → 随机变量 → 收敛定理 → LLN/CLT → 鞅
─────────   ────────   ────────   ─────────   ────────   ──
σ-代数      (Ω,F,P)    可测函数    MCT/DCT     SLLN       停时
Lebesgue    分布函数    期望/Lp     Fatou       CLT        可选停时
积分        独立性      条件期望    收敛模式    特征函数    鞅收敛
```

---

## 第 0-1 章：Measure Theory 速成

### 1.1 σ-代数

> $\mathcal{F}$ 是 $\Omega$ 的子集族，满足：
> 1. $\Omega \in \mathcal{F}$
> 2. $A \in \mathcal{F} \Rightarrow A^c \in \mathcal{F}$（对补集封闭）
> 3. $A_1, A_2, \dots \in \mathcal{F} \Rightarrow \bigcup A_i \in \mathcal{F}$（对可数并封闭）

**直觉**：$\mathcal{F}$ = "你能观测到的事件集合"。更大的 $\mathcal{F}$ = 更多信息。

**ML 关联**：滤波（filtration）$\mathcal{F}_0 \subseteq \mathcal{F}_1 \subseteq \cdots$ = 信息逐步揭示的过程（如 RL 中智能体逐步获得观测）。

### 1.2 测度与概率测度

**测度** $\mu: \mathcal{F} \to [0, \infty]$，$\mu(\emptyset) = 0$，$\mu(\bigcup A_i) = \sum \mu(A_i)$（不交）。

**概率测度** $P: \mathcal{F} \to [0,1]$，$P(\Omega) = 1$。

### 1.3 Lebesgue 积分 ★

对非负可测函数 $f$：
$$\int f\,d\mu = \sup\left\{\sum_{i} a_i \mu(A_i) : \text{简单函数} \leq f\right\}$$

**关键定理**（三大收敛定理）：

| 定理 | 条件 | 结论 |
|---|---|---|
| **单调收敛 MCT** | $0 \leq f_n \uparrow f$ | $\int f_n \uparrow \int f$ |
| **Fatou 引理** | $f_n \geq 0$ | $\int \liminf f_n \leq \liminf \int f_n$ |
| **控制收敛 DCT** | $\|f_n\| \leq g$, $\int g < \infty$, $f_n \to f$ | $\int f_n \to \int f$ |

**ML 关联**：DCT 是交换极限与积分的标准工具——在分析经验风险泛函的极限行为时核心。

---

## 第 2 章：随机变量与期望

### 2.1 随机变量

$X: \Omega \to \mathbb{R}$ 是 $\mathcal{F}$-可测的：$\{X \leq x\} \in \mathcal{F}, \forall x$。

**分布函数**：$F(x) = P(X \leq x)$

### 2.2 期望

$$E[X] = \int_\Omega X\,dP = \int_\mathbb{R} x\,dF(x)$$

### 2.3 $L^p$ 空间

$L^p = \{X : E|X|^p < \infty\}$，范数 $\|X\|_p = (E|X|^p)^{1/p}$。

**关键**：$L^2$ 是 Hilbert 空间（内积 $\langle X, Y\rangle = E[XY]$）→ 条件期望 = 正交投影。

---

## 第 3 章：收敛模式 ★★★

| 收敛模式 | 记号 | 定义 | 强度 |
|---|---|---|---|
| **几乎必然** | $X_n \xrightarrow{a.s.} X$ | $P(X_n \to X) = 1$ | 最强 |
| **$L^p$** | $X_n \xrightarrow{L^p} X$ | $E|X_n - X|^p \to 0$ | 强 |
| **依概率** | $X_n \xrightarrow{P} X$ | $\forall\epsilon: P(|X_n - X|>\epsilon) \to 0$ | 中 |
| **依分布** | $X_n \xRightarrow{d} X$ | $F_n(x) \to F(x)$ 连续点 | 最弱 |

**蕴含关系**：$a.s. \Rightarrow P \Rightarrow d$；$L^p \Rightarrow P$。

**反例**（不蕴含）：
- $X_n \xrightarrow{P} X$ 但 $X_n \not\xrightarrow{a.s.} X$：滑动窗口示例
- $X_n \xrightarrow{d} X$ 但 $X_n \not\xrightarrow{P} X$：$X_n = X$（同分布但非相等）

**ML 关联**：
- $a.s.$ 收敛 → SGD 的确定性收敛保证
- 依概率收敛 → 更弱的保证（但通常足够）
- 依分布收敛 → CLT（参数估计的渐近分布）

---

## 第 4 章：大数定律 ★★

### 4.1 弱大数定律 (WLLN)

> $X_1, X_2, \dots$ i.i.d., $E|X_i| < \infty$：
> $$\frac{S_n}{n} \xrightarrow{P} \mu$$

### 4.2 强大数定律 (SLLN) ★★★

> 同条件：
> $$\frac{S_n}{n} \xrightarrow{a.s.} \mu$$

**Williams 的证明思路**（用鞅方法）：
1. 截断：$Y_k = X_k \mathbf{1}_{|X_k| \leq k}$
2. 证明 $X_k = Y_k$ a.s. eventually（Borel-Cantelli）
3. 用 Kronecker 引理：$\sum \frac{Y_k - EY_k}{k^2}$ 收敛 $\Rightarrow \frac{1}{n}\sum(Y_k - EY_k) \to 0$

**ML 关联**：SGD 的理论根基——梯度平均 $\frac{1}{n}\sum\nabla\ell_i \to \nabla L$。

### 4.3 Borel-Cantelli 引理

1. $\sum P(A_n) < \infty \Rightarrow P(A_n \text{ i.o.}) = 0$
2. $A_n$ 独立且 $\sum P(A_n) = \infty \Rightarrow P(A_n \text{ i.o.}) = 1$

---

## 第 5 章：中心极限定理 ★★

### 5.1 特征函数

$\varphi_X(t) = E[e^{itX}]$ — 总存在，唯一确定分布。

### 5.2 CLT

> $X_1, \dots, X_n$ i.i.d., $EX_i = \mu$, $\text{Var}(X_i) = \sigma^2$：
> $$\frac{S_n - n\mu}{\sigma\sqrt{n}} \xRightarrow{d} \mathcal{N}(0,1)$$

**证明思路**（特征函数法）：
1. 标准化后特征函数 $\varphi(t/\sqrt{n}) = 1 - t^2/(2n) + o(1/n)$
2. $[\varphi(t/\sqrt{n})]^n \to e^{-t^2/2}$

**ML 关联**：mini-batch 梯度噪声 $\approx \mathcal{N}(0, \sigma^2/n)$ → BatchNorm 归一化的理论基础。

### 5.3 Berry-Esseen

$$\sup_x |F_n(x) - \Phi(x)| \leq \frac{C\, E|X-\mu|^3}{\sigma^3\sqrt{n}}$$

→ CLT 的收敛速度 $O(1/\sqrt{n})$。

---

## 第 6 章：条件期望 ★★★

### 6.1 定义

$Y = E[X|\mathcal{G}]$ 是 $\mathcal{G}$-可测的，且
$$\int_A Y\,dP = \int_A X\,dP, \quad \forall A \in \mathcal{G}$$

**直觉**：$E[X|\mathcal{G}]$ = $X$ 在"已知信息 $\mathcal{G}$"下的**最佳预测**。

### 6.2 关键性质

- **塔性质**：$E[E[X|\mathcal{G}]] = E[X]$（全期望公式）
- **独立性**：$X \perp \mathcal{G} \Rightarrow E[X|\mathcal{G}] = E[X]$
- **可测性**：$X$ 是 $\mathcal{G}$-可测 $\Rightarrow E[X|\mathcal{G}] = X$
- **Jensen**：$\varphi$ 凸 $\Rightarrow E[\varphi(X)|\mathcal{G}] \geq \varphi(E[X|\mathcal{G}])$

### 6.3 几何直觉（$L^2$ 投影）★

在 $L^2$ 中，$E[X|\mathcal{G}]$ = $X$ 到 $\mathcal{G}$-可测函数子空间的**正交投影**：
$$X - E[X|\mathcal{G}] \perp \mathcal{G}\text{-可测函数}$$

**ML 关联**：回归分析 = 条件期望的估计。$E[Y|X]$ = 给定特征 $X$ 时目标 $Y$ 的最佳预测（$L^2$ 意义下）。

---

## 第 7 章：鞅论 ★★★

### 7.1 定义

$X_n$ 关于滤波 $\mathcal{F}_0 \subseteq \mathcal{F}_1 \subseteq \cdots$ 是**鞅** $\iff$：
1. $X_n$ 是 $\mathcal{F}_n$-适应（$X_n$ 是 $\mathcal{F}_n$-可测）
2. $E|X_n| < \infty$
3. $E[X_{n+1}|\mathcal{F}_n] = X_n$

（下鞅 $\geq$；上鞅 $\leq$）

**直觉**：鞅 = 公平赌博。$\mathcal{F}_n$ = 第 $n$ 轮你知道的信息。$E[X_{n+1}|\mathcal{F}_n] = X_n$ = "无论你怎么下注，期望财富不变"。

### 7.2 经典例子

- **对称随机游走**：$S_n = \sum_{i=1}^n X_i$（$X_i$ i.i.d. 均值 0）是鞅
- **Doob 鞅**：$X_n = E[Y|\mathcal{F}_n]$（任何 $Y$ + 滤波给出鞅）
- **似然比**：$L_n = \prod \frac{q(X_i)}{p(X_i)}$ 在 $P$ 下是鞅（如果 $q$ 是真实分布）
- **Polya 罐**：$X_n$ = 红球比例是鞅

### 7.3 可选停时定理 ★★

> $\tau$ 是停时（$\{\tau \leq n\} \in \mathcal{F}_n$）。在某些条件下：
> $$E[X_\tau] = E[X_0]$$

**条件**（任一即可）：
- $\tau$ 有界
- $X_n$ 一致可积
- $P(\tau < \infty) = 1$ 且 $E|X_\tau| < \infty$ 且 $\lim E[X_n\mathbf{1}_{\tau > n}] = 0$

**经典应用**：对称随机游走从 0 出发，首次到达 $\pm a$ 的期望时间 $E[\tau] = a^2$。

**证明**：$S_n^2 - n$ 也是鞅。停时处 $E[S_\tau^2 - \tau] = 0 \Rightarrow a^2 - E[\tau] = 0$。

### 7.4 鞅收敛定理 ★★

> $X_n$ 是 $L^1$-有界下鞅 $\Rightarrow X_n \xrightarrow{a.s.} X_\infty$, $E|X_\infty| < \infty$。

### 7.5 Doob 分解与不等式

- **分解**：$X_n = M_n + A_n$（鞅 + 可料增序列）
- **Doob 极大值不等式**：$P(\max_{k\leq n}|X_k| \geq \lambda) \leq E[X_n^2]/\lambda^2$
- **Azuma-Hoeffding**：鞅差 $|D_i| \leq c_i \Rightarrow P(|M_n - M_0| \geq t) \leq 2e^{-t^2/(2\sum c_i^2)}$

---

## 频率派 vs 贝叶斯派的哲学分歧 ★★

**频率派**（Fisher, Neyman, Pearson）：
- 概率 = **长期频率的极限**：$P(A) = \lim_{n\to\infty} \frac{\#\{A \text{ 发生}\}}{n}$
- 概率是客观的、物理的属性
- 参数 $\theta$ 是固定的未知常数（不是随机变量）
- **ML 关联**：最大似然估计、假设检验、bootstrap

**贝叶斯派**（Bayes, Laplace, Jeffreys, Jaynes）：
- 概率 = **不确定性程度 / 信念强度**（subjective probability）
- 概率是你对事件发生的确信程度，可以因证据更新
- 参数 $\theta$ 是随机变量，有先验分布 $p(\theta)$
- **更新规则**：$p(\theta|D) \propto p(D|\theta)p(\theta)$（Bayes 定理）
- **ML 关联**：贝叶斯神经网络、变分推断、不确定性量化

**SLLN 的两面解读**：
- 频率派：SLLN **定义**了概率（频率的极限 = 概率）
- 贝叶斯派：SLLN 是一个**定理**（在概率公理下推导），概率是原始概念

**实践调和**：在 ML 中，频率派方法（SGD + cross-entropy）和贝叶斯方法（ELBO + KL 正则化）共存。大多数深度学习是频率派的，但 diffusion / VAE / RLHF 都有贝叶斯根源。

---

## Markov 链与 MCMC ★★

### Markov 性

$$P(X_{n+1} = j | X_n = i, X_{n-1}, \dots, X_0) = P(X_{n+1} = j | X_n = i) = P_{ij}$$

### 平稳分布

$\pi P = \pi$（$\pi$ 是平稳分布）

### 遍历定理

> 不可约 + 非周期 + 正常返 $\Rightarrow$ 唯一平稳分布 $\pi^*$，且
> $$\frac{1}{n}\sum_{k=1}^n f(X_k) \xrightarrow{a.s.} E_{\pi^*}[f(X)]$$

**ML 关联**：MCMC（Metropolis-Hastings / Hamiltonian Monte Carlo）用遍历定理从复杂后验分布中采样。

---

## 集中不等式速查

| 不等式 | 条件 | 结论 |
|---|---|---|
| **Markov** | $X \geq 0$ | $P(X \geq a) \leq E[X]/a$ |
| **Chebyshev** | — | $P(|X-\mu| \geq a) \leq \sigma^2/a^2$ |
| **Chernoff** | 独立 | $P(S_n \geq (1+\delta)\mu) \leq e^{-\mu\delta^2/3}$ |
| **Hoeffding** ★ | $X_i \in [a_i, b_i]$ | $P(|S_n - ES_n| \geq t) \leq 2e^{-2t^2/\sum(b_i-a_i)^2}$ |
| **Azuma** | 鞅差 $|D_i| \leq c_i$ | $P(|M_n - M_0| \geq t) \leq 2e^{-t^2/(2\sum c_i^2)}$ |

---

## 🟠 不足层（局限性）

1. **测度论的概率零事件悖论**：$P(A) = 0$ 不意味着 $A = \emptyset$（如连续分布下取特定点的概率为 0 但并非不可能）。这在频率派解释中令人困惑。

2. **重尾分布让 CLT 失效**：Cauchy 分布的期望/方差不存在 → CLT 不适用。更一般地，$\alpha$-稳定分布（$\alpha < 2$）不收敛到正态。

3. **独立性假设过强**：现实中数据往往有依赖性（时间序列、空间数据），i.i.d. 假设不成立。需要用混合条件（mixing conditions）或鞅方法替代。

4. **条件期望的存在性依赖于测度论**：没有 Radon-Nikodym 定理，条件期望的一般定义无法严格化。本科课程只能给出离散/连续的特殊情况。

---

## 🔴 应用层（ML 公式级对应）

| 概念 | 公式 | ML 场景 |
|---|---|---|
| SLLN | $\frac{S_n}{n}\xrightarrow{a.s.}\mu$ | SGD 梯度平均收敛 |
| CLT | $\frac{S_n-n\mu}{\sigma\sqrt{n}}\Rightarrow\mathcal{N}(0,1)$ | mini-batch 梯度噪声 |
| 条件期望 = 投影 | $E[Y\|\mathcal{F}]$ = $L^2$ 投影 | 回归分析 |
| 鞅 + 可选停时 | $E[X_\tau]=E[X_0]$ | RL 值函数估计 / 期权定价 |
| Hoeffding | $P(\|\hat{R}-R\|>\epsilon)\leq 2e^{-2n\epsilon^2}$ | 泛化界 |
| Markov 遍历 | $\frac{1}{n}\sum f(X_k) \to E_\pi[f]$ | MCMC 采样 |

---

## 与 work4ai 讲透系列的交叉

- **讲透泛化**：SLLN + CLT + 集中不等式
- **讲透 SGD**：SLLN → 梯度收敛，CLT → 噪声分析
- **讲透强化学习**：鞅 → TD 学习，Markov 链 → MDP
- **讲透 diffusion**：Brownian 运动 + 反向 SDE
