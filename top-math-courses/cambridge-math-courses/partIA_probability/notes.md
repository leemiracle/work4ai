# Cambridge Part IA · 概率笔记（Cambridge 讲义风格 + 母函数特色）

> **教材**：Cambridge 自编讲义；配 Pitman *Probability* / Ross *Probability Models*
> **一手核实**：Cambridge Part IA Lent term 大纲
> **特色**：本科概率（无测度论），Cambridge 式严格；**母函数**是核心工具

---

## 费曼三层讲透

### 🟢 直觉层

- **概率 = 不确定性的大小**：频率派说"长期频率极限"，贝叶斯派说"信念强度"
- **母函数 = 分布的"DNA"**：$G(s) = E[s^X]$ 唯一确定分布，乘法 = 独立和的卷积
- **CLT = "平均值趋近于钟形"**：不管原始分布长什么样

---

### 🔵 数学层

## 第 1 章：概率空间与条件概率

### 公理 + Bayes

$P(H|D) = \frac{P(D|H)P(H)}{P(D)}$

先验 → 似然 → 后验。**ML 关联**：朴素贝叶斯 / 贝叶斯推断。

### 独立性

$A \perp B \iff P(A \cap B) = P(A)P(B)$

---

## 第 2 章：随机变量与常见分布

### 离散分布

| 分布 | PMF | 期望 | ML 关联 |
|---|---|---|---|
| Bernoulli($p$) | $p^x(1-p)^{1-x}$ | $p$ | 二分类 |
| Binomial($n,p$) | $\binom{n}{k}p^k(1-p)^{n-k}$ | $np$ | 多次试验 |
| Poisson($\lambda$) | $e^{-\lambda}\lambda^k/k!$ | $\lambda$ | 稀疏事件 |
| Geometric($p$) | $(1-p)^{k-1}p$ | $1/p$ | 首次成功 |

### 连续分布

| 分布 | PDF | ML 关联 |
|---|---|---|
| Uniform($a,b$) | $1/(b-a)$ | 随机初始化 |
| Normal($\mu,\sigma^2$) | $\frac{1}{\sigma\sqrt{2\pi}}e^{-(x-\mu)^2/(2\sigma^2)}$ | CLT 核心 |
| Exponential($\lambda$) | $\lambda e^{-\lambda x}$ | 无记忆性 → RL 几何折扣 |

### 正态分布性质

线性变换 $aX+b \sim \mathcal{N}(a\mu+b, a^2\sigma^2)$；独立和 $X+Y \sim \mathcal{N}(\mu_1+\mu_2, \sigma_1^2+\sigma_2^2)$。

---

## 第 3 章：期望与方差

- **线性性**：$E[aX+bY] = aE[X]+bE[Y]$（不需独立）
- **方差**：$\text{Var}(X) = E[X^2]-(E[X])^2$
- **独立和方差**：$\text{Var}(X+Y) = \text{Var}(X)+\text{Var}(Y)$

---

## 第 4 章：母函数 ★★（Cambridge 特色）

### 概率母函数

$$G_X(s) = E[s^X] = \sum_k s^k P(X=k)$$

### 关键性质

1. $G_X(1) = 1$
2. $E[X] = G_X'(1)$
3. $E[X^2] = G_X''(1)+G_X'(1)$ → $\text{Var}(X) = G_X''(1)+G_X'(1)-(G_X'(1))^2$
4. **独立和** ★：$X \perp Y \Rightarrow G_{X+Y}(s) = G_X(s)G_Y(s)$

### 常见分布的母函数

| 分布 | $G(s)$ |
|---|---|
| Bernoulli($p$) | $(1-p)+ps$ |
| Binomial($n,p$) | $((1-p)+ps)^n$ |
| Poisson($\lambda$) | $e^{\lambda(s-1)}$ |
| Geometric($p$) | $\frac{ps}{1-(1-p)s}$ |

### 母函数的应用 ★

**求独立和的分布**：$X \sim \text{Poisson}(\lambda_1)$, $Y \sim \text{Poisson}(\lambda_2)$ 独立

$G_{X+Y}(s) = e^{\lambda_1(s-1)} \cdot e^{\lambda_2(s-1)} = e^{(\lambda_1+\lambda_2)(s-1)}$

→ $X+Y \sim \text{Poisson}(\lambda_1+\lambda_2)$ ✓（Poisson 分布的叠加性）

### 矩母函数

$M_X(t) = E[e^{tX}]$（可能不存在）。CLT 证明的工具。

---

## 第 5 章：极限定理 ★★

### LLN

$\bar{X}_n \xrightarrow{P} \mu$ → SGD 梯度收敛

### CLT ★★★

$\frac{\bar{X}_n-\mu}{\sigma/\sqrt{n}} \xrightarrow{d}\mathcal{N}(0,1)$ → 梯度噪声正态化 / BatchNorm

### 正态近似

Binomial($n,p$) ≈ $\mathcal{N}(np, np(1-p)$)；Poisson($\lambda$) ≈ $\mathcal{N}(\lambda,\lambda)$。

---

## 第 6 章：Markov 链入门

$P(X_{n+1}=j|X_n=i,\ldots) = P_{ij}$

**平稳分布**：$\pi P = \pi$

**ML 关联**：MCMC / PageRank / 强化学习。

---

## 频率派 vs 贝叶斯派

- 频率派：$P$ = 长期频率。MLE。参数固定。
- 贝叶斯派：$P$ = 信念。后验分布。参数随机。
- ML 实践：SGD（频率派）vs VAE/diffusion（贝叶斯根源）。

---

## 🟠 不足层

1. **无测度论**：母函数是特征函数的"无 rigor 版本"
2. **i.i.d. 假设**：现实数据有依赖
3. **CLT 对重尾失效**：Cauchy 方差不存在
4. **母函数只适用于非负整数随机变量**（概率母函数 PGF）；矩母函数可能不存在

---

## 🔴 应用层

| 概念 | ML 场景 |
|---|---|
| Bayes | 朴素贝叶斯 / 贝叶斯推断 |
| LLN | SGD 收敛 |
| CLT | BatchNorm / 统计检验 |
| 母函数 | 分布卷积 / 独立和推导 |
| Markov 链 | MCMC / PageRank / RL |

---

## 与 work4ai 讲透系列的交叉

- **讲透朴素贝叶斯**：Bayes + 条件独立
- **讲透 SGD**：LLN → 梯度收敛
- **讲透 MCMC**：Markov 链遍历定理
- **讲透 Poisson 过程**：母函数 → Poisson 叠加
