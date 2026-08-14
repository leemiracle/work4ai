# Oxford Part A A8 · 概率笔记（Grimmett & Stirzaker 风格 + Markov 链特色）

> **教材**：Grimmett & Stirzaker, *Probability and Random Processes*
> **一手核实**：Oxford Part A A8 课程大纲
> **特色**：本科应用概率；**Markov 链是核心**——平稳分布、首次通过时间、遍历定理

---

## 费曼三层讲透

### 🟢 直觉层

- **概率 = 不确定性的大小**：频率派 = 长期频率，贝叶斯派 = 信念强度
- **Markov 性 = "未来只取决于现在"**：$P(X_{n+1}|X_n, X_{n-1}, \ldots) = P(X_{n+1}|X_n)$
- **平稳分布 = "稳态"**：时间足够长后，Markov 链"忘记"初始状态

---

### 🔵 数学层

## 第 1 章：概率空间与条件概率

### Bayes 定理 ★★★

$P(H|D) = \frac{P(D|H)P(H)}{P(D)}$

先验 → 似然 → 后验。

### 全概率公式

$P(D) = \sum_i P(D|H_i)P(H_i)$

---

## 第 2 章：随机变量与分布

### 常见离散分布

| 分布 | PMF | 期望 | ML 关联 |
|---|---|---|---|
| Bernoulli($p$) | $p^x(1-p)^{1-x}$ | $p$ | 二分类 |
| Binomial($n,p$) | $\binom{n}{k}p^k(1-p)^{n-k}$ | $np$ | 多次试验 |
| Poisson($\lambda$) | $e^{-\lambda}\lambda^k/k!$ | $\lambda$ | 稀疏事件 |
| Geometric($p$) | $(1-p)^{k-1}p$ | $1/p$ | 首次成功 |

### 常见连续分布

| 分布 | ML 关联 |
|---|---|
| Uniform($a,b$) | 随机初始化 |
| Normal($\mu,\sigma^2$) | CLT 核心 |
| Exponential($\lambda$) | 无记忆性 → RL 几何折扣 |

### 正态分布性质

线性变换、独立和、标准化（见 Stat 134 / Part IA 笔记）。

---

## 第 3 章：期望与方差

- 线性性（不需独立）：$E[aX+bY] = aE[X]+bE[Y]$
- 方差公式：$\text{Var}(X) = E[X^2]-(E[X])^2$
- 独立和方差：$\text{Var}(X+Y) = \text{Var}(X)+\text{Var}(Y)$

---

## 第 4 章：母函数 + 极限定理

### 母函数

$G_X(s) = E[s^X]$；独立和：$G_{X+Y} = G_X G_Y$

### LLN

$\bar{X}_n \xrightarrow{P} \mu$ → SGD 收敛

### CLT ★★★

$\frac{\bar{X}_n-\mu}{\sigma/\sqrt{n}} \xrightarrow{d}\mathcal{N}(0,1)$ → BatchNorm

---

## 第 5 章：Markov 链 ★★（Oxford 特色）

### 定义

$P(X_{n+1}=j|X_n=i, X_{n-1}, \ldots, X_0) = P(X_{n+1}=j|X_n=i) = P_{ij}$

### 转移矩阵

$P = (P_{ij})$，每行和为 1。

### Chapman-Kolmogorov 方程

$P^{(m+n)} = P^{(m)}P^{(n)}$（$n$ 步转移 = 两个阶段转移的矩阵乘积）

### 分类

- **不可约**：所有状态互相可达
- **非周期**：$\gcd\{n : P^n_{ii} > 0\} = 1$
- **正常返**：$E[\tau_{ii}] < \infty$

### 平稳分布 ★

$\pi P = \pi$（$\pi$ 是 $P^T$ 特征值 1 的特征向量）

**求解**：解线性方程组 $\sum_i \pi_i P_{ij} = \pi_j$, $\sum\pi_i = 1$。

### 首次通过时间

$f_{ij} = P(\text{首次从 } i \text{ 到达 } j)$

$m_i = E[\text{回到 } i \text{ 的时间}]$（平均返回时间）

**关系**：$\pi_i = 1/m_i$（平稳分布概率 = 平均返回时间的倒数）

### 遍历定理 ★★

> 不可约 + 非周期 + 正常返 → 唯一平稳分布 $\pi^*$，且
> $$\frac{1}{n}\sum_{k=1}^n f(X_k) \xrightarrow{a.s.} E_{\pi^*}[f(X)]$$

**ML 关联**：MCMC 采样——构造 Markov 链使平稳分布 = 目标分布，遍历定理保证样本均值 → 期望。

---

## Markov 链的 ML 应用 ★★

### 1. MCMC（Metropolis-Hastings）

构造转移核 $P$ 使 $\pi$ 是平稳分布（细致平衡 $\pi_i P_{ij} = \pi_j P_{ji}$）

→ 从不可归一化后验 $\tilde\pi(\theta) \propto p(\theta|D)$ 中采样

### 2. PageRank

网页链接图 → Markov 链 → 平稳分布 = 网页排名

$P = \alpha A + (1-\alpha)\frac{1}{N}\mathbf{1}\mathbf{1}^T$（$\alpha \approx 0.85$ 阻尼因子）

### 3. 强化学习（MDP）

MDP = Markov 链 + 奖励 + 决策。状态转移 $P(s'|s,a)$，值函数 $V(s) = E[r + \gamma V(s')]$

### 4. Hidden Markov Model（HMM）

隐藏状态 Markov 链 + 观测发射概率。用于语音识别、NLP（早期）、生物序列。

---

## 频率派 vs 贝叶斯派

- 频率派：$P$ = 长期频率。MLE。
- 贝叶斯派：$P$ = 信念。后验分布。MCMC 是贝叶斯推断的核心工具。

---

## 🟠 不足层

1. **无测度论**：连续 Markov 链需要测度论（B8.1 补充）
2. **Markov 假设过强**：现实状态转移可能依赖更长的历史
3. **遍历定理需要不可约+非周期**：不满足时平稳分布可能不唯一或不存在
4. **混合时间未讨论**：A8 只证明收敛但不讨论"多快"

---

## 🔴 应用层

| 概念 | ML 场景 |
|---|---|
| Bayes | 朴素贝叶斯 / 贝叶斯推断 |
| LLN + CLT | SGD 收敛 + BatchNorm |
| **Markov 链** ★ | MCMC / PageRank / RL / HMM |
| 平稳分布 | 贝叶斯后验采样 |
| 遍历定理 | MCMC 收敛保证 |

---

## 与 work4ai 讲透系列的交叉

- **讲透 MCMC**：Markov 链遍历定理 + 细致平衡
- **讲透 PageRank**：平稳分布 + 幂迭代
- **讲透强化学习**：Markov 性 → MDP
- **讲透 SGD**：LLN + CLT
