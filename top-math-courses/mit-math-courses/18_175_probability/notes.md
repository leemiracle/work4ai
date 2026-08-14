# MIT 18.175 · 章节笔记（Durrett *Probability: Theory and Examples* 5th ed）

> **教材**：Durrett, *Probability: Theory and Examples* (5th ed, Cambridge, 2019) — **免费 PDF**
> **一手核实**：services.math.duke.edu/~rtd/PTE/PTE5_011119.pdf
> **MIT 页面**：18.175 = 研究生/本科高年级合上

---

## 核心框架

Durrett 全书围绕一个主线：**从概率公理到强大数定律 + 中心极限定理**。

```
概率空间 → 随机变量 → 期望 → 收敛模式 → LLN → CLT → 鞅 → Brownian
```

---

## 第 1 章：Laws of Large Numbers

### 1.1 概率空间

$(\Omega, \mathcal{F}, P)$：
- $\Omega$：样本空间
- $\mathcal{F}$：σ-代数（事件集）
- $P: \mathcal{F} \to [0,1]$：概率测度，$P(\Omega) = 1$, $P(\bigcup A_i) = \sum P(A_i)$（不交）

### 1.2 随机变量

$X: \Omega \to \mathbb{R}$ 是 $\mathcal{F}$-可测的（$\{X \leq x\} \in \mathcal{F}$）。

**分布函数**：$F(x) = P(X \leq x)$

### 1.3 随机变量序列的收敛 ★

| 收敛模式 | 记号 | 定义 |
|---|---|---|
| **几乎必然** | $X_n \xrightarrow{a.s.} X$ | $P(\{\omega : X_n(\omega) \to X(\omega)\}) = 1$ |
| **依概率** | $X_n \xrightarrow{P} X$ | $\forall\epsilon: P(|X_n - X| > \epsilon) \to 0$ |
| **依分布** | $X_n \xrightarrow{d} X$ | $F_{X_n}(x) \to F_X(x)$ 在连续点 |
| **$L^p$** | $X_n \xrightarrow{L^p} X$ | $E|X_n - X|^p \to 0$ |

**蕴含关系**：$a.s. \Rightarrow P \Rightarrow d$；$L^p \Rightarrow P$。

### 1.4 期望

$E[X] = \int X \, dP = \int_{-\infty}^{\infty} x \, dF(x)$

**关键定理**：
- **单调收敛 (MCT)**：$0 \leq X_n \uparrow X \Rightarrow E[X_n] \uparrow E[X]$
- **控制收敛 (DCT)**：$|X_n| \leq Y$, $EY < \infty$, $X_n \to X$ a.s. $\Rightarrow E[X_n] \to E[X]$
- **Fatou 引理**：$E[\liminf X_n] \leq \liminf E[X_n]$

### 1.5 弱大数定律 (WLLN) ★

> 设 $X_1, X_2, \dots$ i.i.d. 且 $E|X_i| < \infty$，$S_n = X_1 + \dots + X_n$，则
> $$\frac{S_n}{n} \xrightarrow{P} \mu = E[X_i]$$

### 1.6 强大数定律 (SLLN) ★★★

> 同上条件，则
> $$\frac{S_n}{n} \xrightarrow{a.s.} \mu$$

**证明思路**（截断法）：
1. 截断：$Y_k = X_k \mathbf{1}_{|X_k| \leq k}$
2. 用 Borel-Cantelli 证明 $X_k = Y_k$ a.s. for large $k$
3. 用 Chebyshev + Kronecker 引理证明 $\frac{1}{n}\sum Y_k \to \mu$

**ML 关联**：SGD 收敛性的理论根基——"样本均值收敛到期望"。

---

## 第 2 章：Central Limit Theorems

### 2.1 特征函数 ★

$\varphi_X(t) = E[e^{itX}]$（概率分布的 Fourier 变换）

**关键性质**：
- $\varphi_X$ 唯一确定分布
- $X \perp Y \Rightarrow \varphi_{X+Y} = \varphi_X \varphi_Y$
- $E[X^k] = i^{-k} \varphi^{(k)}(0)$（如果存在）

### 2.2 中心极限定理 (CLT) ★★★

> $X_1, X_2, \dots$ i.i.d., $EX_i = \mu$, $\text{Var}(X_i) = \sigma^2 \in (0, \infty)$，则
> $$\frac{S_n - n\mu}{\sigma\sqrt{n}} \xrightarrow{d} N(0, 1)$$

**证明思路**：
1. 特征函数：$\varphi_{(S_n-n\mu)/(\sigma\sqrt{n})}(t) = [\varphi_{(X-\mu)/\sigma}(t/\sqrt{n})]^n$
2. Taylor 展开：$\varphi(t/\sqrt{n}) \approx 1 + (it)^2/(2n) + o(1/n)$
3. $[1 + (it)^2/(2n)]^n \to e^{-t^2/2}$（标准正态的特征函数）

**ML 关联**：
- SGD 噪声的正态分布
- 神经网络参数初始化
- PAC-Bayes 泛化界

### 2.3 Berry-Esseen 定理

$$\sup_x |F_n(x) - \Phi(x)| \leq \frac{C E|X_i|^3}{\sigma^3 \sqrt{n}}$$

**意义**：给出 CLT 的**收敛速度** $O(1/\sqrt{n})$。

**ML 关联**：有限样本下泛化界的精确常数。

### 2.4 局部 CLT 与大偏差

---

## 第 3 章：Random Variables (补充)

### 3.1 常见分布

| 分布 | PMF/PDF | 期望 | 方差 |
|---|---|---|---|
| Bernoulli($p$) | $p^x(1-p)^{1-x}$ | $p$ | $p(1-p)$ |
| Binomial($n,p$) | $\binom{n}{x}p^x(1-p)^{n-x}$ | $np$ | $np(1-p)$ |
| Poisson($\lambda$) | $e^{-\lambda}\lambda^x/x!$ | $\lambda$ | $\lambda$ |
| Uniform($a,b$) | $1/(b-a)$ | $(a+b)/2$ | $(b-a)^2/12$ |
| Normal($\mu,\sigma^2$) | $\frac{1}{\sqrt{2\pi}\sigma}e^{-\frac{(x-\mu)^2}{2\sigma^2}}$ | $\mu$ | $\sigma^2$ |
| Exponential($\lambda$) | $\lambda e^{-\lambda x}$ | $1/\lambda$ | $1/\lambda^2$ |

### 3.2 矩母函数与特征函数

$M_X(t) = E[e^{tX}]$（矩母函数，可能不存在）
$\varphi_X(t) = E[e^{itX}]$（特征函数，总是存在）

---

## 第 4 章：Conditional Probability / Expectation ★

### 4.1 条件期望

$E[X | \mathcal{G}]$ = $X$ 在 σ-代数 $\mathcal{G}$ 上的最佳 $\mathcal{G}$-可测逼近。

**定义**：$Y = E[X|\mathcal{G}]$ 是 $\mathcal{G}$-可测的且 $\int_A Y \, dP = \int_A X \, dP, \forall A \in \mathcal{G}$。

### 4.2 关键性质

- $E[E[X|\mathcal{G}]] = E[X]$（塔性质）
- $X$ 与 $\mathcal{G}$ 独立 $\Rightarrow E[X|\mathcal{G}] = E[X]$
- $X$ 是 $\mathcal{G}$-可测 $\Rightarrow E[X|\mathcal{G}] = X$
- Jensen：$E[\varphi(X)|\mathcal{G}] \geq \varphi(E[X|\mathcal{G}])$（凸 $\varphi$）

### 4.3 条件期望的几何直觉

在 $L^2$ 中，$E[X|\mathcal{G}]$ = $X$ 到 $\mathcal{G}$-可测函数子空间的**正交投影**。

**ML 关联**：回归/最小二乘 = 条件期望的逼近。

---

## 第 5 章：Martingales ★★★

### 5.1 定义

$X_n$ 关于 $\mathcal{F}_n$ 是**鞅 (martingale)** $\iff$：
1. $X_n$ 是 $\mathcal{F}_n$-可测
2. $E|X_n| < \infty$
3. $E[X_{n+1} | \mathcal{F}_n] = X_n$

（下鞅：$\geq X_n$；上鞅：$\leq X_n$）

### 5.2 例子

- $S_n = \sum X_i$（i.i.d. 均值 0）是鞅
- Doob 鞅：$X_n = E[Y | \mathcal{F}_n]$
- Polya 罐模型

### 5.3 可选停时定理 ★

如果 $X_n$ 是鞅, $\tau$ 是停时, 则在某些条件下 $E[X_\tau] = E[X_0]$。

**条件**：$\tau$ 有界 / $X_n$ 一致可积 / $P(\tau < \infty) = 1$ 且 $E|X_\tau| < \infty$ 且 $\lim E[X_n \mathbf{1}_{\tau > n}] = 0$。

### 5.4 鞅收敛定理 ★★

> $X_n$ 是 $L^1$-有界的下鞅 $\Rightarrow$ $X_n \xrightarrow{a.s.} X_\infty$, $E|X_\infty| < \infty$。

### 5.5 Doob 分解与不等式

- **分解**：$X_n = M_n + A_n$（鞅 + 可料增序列）
- **Doob 极大值不等式**：$P(\max_{k\leq n} |X_k| \geq \lambda) \leq E[X_n^2]/\lambda^2$

**ML 关联**：
- RL 中的 Bellman 方程（鞅方法）
- 联机学习 regret bound（Azuma-Hoeffding 不等式）
- MCMC 收敛

---

## 集中不等式速查（ML 理论核心工具）

| 不等式 | 条件 | 结论 |
|---|---|---|
| **Markov** | $X \geq 0$ | $P(X \geq a) \leq E[X]/a$ |
| **Chebyshev** | — | $P(|X-\mu| \geq a) \leq \sigma^2/a^2$ |
| **Chernoff** | $X_i$ 独立 | $P(S_n \geq (1+\delta)\mu) \leq e^{-\mu\delta^2/3}$ |
| **Hoeffding** ★ | $X_i \in [a_i, b_i]$ 独立 | $P(|S_n - ES_n| \geq t) \leq 2e^{-2t^2/\sum(b_i-a_i)^2}$ |
| **Azuma** | 鞅差 $|D_i| \leq c_i$ | $P(|M_n - M_0| \geq t) \leq 2e^{-t^2/(2\sum c_i^2)}$ |
| **McDiarmid** | Lipschitz 条件 | $P(|f - Ef| \geq t) \leq 2e^{-2t^2/\sum c_i^2}$ |
| **Jensen** | $\varphi$ 凸 | $\varphi(E[X]) \leq E[\varphi(X)]$ |

---

## 与 ML 理论的核心关联

| Durrett 章节 | ML 概念 |
|---|---|
| Ch 1 SLLN | SGD 收敛 |
| Ch 1 收敛模式 | 训练损失的收敛类型 |
| Ch 2 CLT | 参数估计的渐近正态性 |
| Ch 2 Berry-Esseen | 有限样本泛化界的常数 |
| Ch 4 条件期望 | 回归、贝叶斯推断 |
| Ch 5 鞅 | RL（Bellman 方程）、联机学习 |
| Hoeffding | **泛化界的核心工具** ★ |
| McDiarmid | **算法稳定性推导** |

---

## 与 work4ai 讲透系列的交叉

- **讲透泛化**：Ch 1 LLN + Ch 2 CLT + 集中不等式
- **讲透优化器**：Ch 1 SLLN → SGD 收敛
- **讲透扩散模型**：Ch 5 鞅 + Brownian motion（Durrett 后续章节）
- **讲透统计学习理论**：Hoeffding + VC 维 + Rademacher
