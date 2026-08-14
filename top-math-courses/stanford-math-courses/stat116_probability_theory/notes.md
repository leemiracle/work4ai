# Stanford STAT 116 · 概率论笔记（Ross / Bertsekas 风格）

> **教材**：Ross, *Introduction to Probability Models*；或 Bertsekas & Tsitsiklis, *Introduction to Probability*
> **一手核实**：Stanford Stat 116 课程大纲
> **特色**：本科概率（无测度论），强调 Poisson 过程 + Markov 链 + 建模思维

---

## 费曼三层讲透

### 🟢 直觉层

- **概率 = 对随机现象的定量描述**：频率派说"长期频率"，贝叶斯派说"信念强度"
- **条件概率 = 信息更新**：Bayes 定理告诉你"看到证据后如何修正判断"
- **Poisson 过程 = "完全随机的到达"**：每个瞬间独立地"有可能"来一个事件

---

### 🔵 数学层

## 核心框架

```
概率公理 → 条件概率 → Bayes → 随机变量 → 分布 → 期望/方差 → LLN/CLT → 随机过程
───────   ─────────   ─────   ────────   ────   ─────────   ────────   ─────────
可加性     P(A|B)      后验    离散/连续   常见   线性性       收敛+正态   Poisson+Markov
```

---

## 第 1 章：概率公理与条件概率

### 1.1 三大公理

1. $P(A) \geq 0$；2. $P(\Omega) = 1$；3. 互斥可加

### 1.2 Bayes 定理 ★★★

$$P(H_i|D) = \frac{P(D|H_i)P(H_i)}{\sum_j P(D|H_j)P(H_j)}$$

**疾病检测经典例**（见 Stat 134 笔记）：阳性后真正患病的概率可能很低（先验太低时）。

**ML 关联**：朴素贝叶斯、贝叶斯推断、变分推断。

### 1.3 全概率公式

$$P(D) = \sum_i P(D|H_i)P(H_i)$$

---

## 第 2 章：随机变量与分布

### 常见离散分布

| 分布 | PMF | 期望 | ML 关联 |
|---|---|---|---|
| **Bernoulli($p$)** | $p^x(1-p)^{1-x}$ | $p$ | 二分类 |
| **Binomial($n,p$)** | $\binom{n}{k}p^k(1-p)^{n-k}$ | $np$ | 多次试验 |
| **Poisson($\lambda$)** | $e^{-\lambda}\lambda^k/k!$ | $\lambda$ | 稀疏事件 |
| **Geometric($p$)** | $(1-p)^{k-1}p$ | $1/p$ | 首次成功 |
| **Multinomial** | $\frac{n!}{k_1!\cdots k_m!}\prod p_i^{k_i}$ | $np_i$ | 文本分类 |

### 常见连续分布

| 分布 | PDF | ML 关联 |
|---|---|---|
| **Uniform($a,b$)** | $1/(b-a)$ | 随机初始化 |
| **Normal($\mu,\sigma^2$)** | $\frac{1}{\sigma\sqrt{2\pi}}e^{-(x-\mu)^2/(2\sigma^2)}$ | CLT 核心 |
| **Exponential($\lambda$)** | $\lambda e^{-\lambda x}$ | 生存分析 |
| **Gamma($\alpha,\beta$)** | — | 正态先验 |
| **Beta($\alpha,\beta$)** | — | 概率参数先验 |

### 正态分布性质 ★

- **线性变换**：$aX+b \sim \mathcal{N}(a\mu+b, a^2\sigma^2)$
- **独立和**：$X+Y \sim \mathcal{N}(\mu_1+\mu_2, \sigma_1^2+\sigma_2^2)$
- **标准化**：$Z = (X-\mu)/\sigma \sim \mathcal{N}(0,1)$

---

## 第 3 章：期望与方差

### 关键公式

- **线性性**：$E[aX+bY] = aE[X]+bE[Y]$（不需独立！）
- **方差**：$\text{Var}(X) = E[X^2]-(E[X])^2$
- **独立和**：$\text{Var}(X+Y) = \text{Var}(X)+\text{Var}(Y)$（需独立）
- **条件期望**：$E[Y|X] = E[Y] + \frac{\text{Cov}(X,Y)}{\text{Var}(X)}(X-E[X])$（线性回归！）

---

## 第 4 章：极限定理 ★★

### LLN

$\bar{X}_n \xrightarrow{P} \mu$ → SGD 梯度收敛

### CLT ★★★

$$\frac{\bar{X}_n - \mu}{\sigma/\sqrt{n}} \xrightarrow{d} \mathcal{N}(0,1)$$

**ML 关联**：梯度噪声 $\approx \mathcal{N}(0, \Sigma/n)$ → BatchNorm 稳定性

### 矩母函数

$M_X(t) = E[e^{tX}]$ → $E[X^n] = M_X^{(n)}(0)$

独立时：$M_{X+Y}(t) = M_X(t)M_Y(t)$

---

## 第 5 章：Poisson 过程 ★★（Stanford 特色）

### 定义

计数过程 $\{N(t), t \geq 0\}$ 是参数 $\lambda$ 的 Poisson 过程：
1. $N(0) = 0$
2. 独立增量
3. $N(t+s) - N(t) \sim \text{Poisson}(\lambda s)$

### 到达间隔

$T_1, T_2, \dots$ i.i.d. $\sim \text{Exponential}(\lambda)$

### 关键性质

- $P(N(t) = k) = e^{-\lambda t}(\lambda t)^k / k!$
- $E[N(t)] = \lambda t$
- 到达时间 $S_n = T_1 + \cdots + T_n \sim \text{Gamma}(n, \lambda)$

**ML 关联**：事件流建模、API 请求分析、流式学习。

### Poisson 过程的叠加与分裂

- **叠加**：$\lambda_1$ 和 $\lambda_2$ 的独立 Poisson 过程 → $\lambda_1 + \lambda_2$ 的 Poisson 过程
- **稀疏化**：每个事件以概率 $p$ 保留 → 参数 $\lambda p$ 的 Poisson 过程

---

## 第 6 章：Markov 链入门 ★

### 定义

$$P(X_{n+1}=j|X_n=i, X_{n-1}, \dots) = P(X_{n+1}=j|X_n=i) = P_{ij}$$

### 平稳分布

$\pi P = \pi$

### PageRank ★

网页链接图的 Markov 链平稳分布 = PageRank。

转移矩阵 $P = \alpha A + (1-\alpha)\frac{1}{N}\mathbf{1}\mathbf{1}^T$（阻尼因子 $\alpha \approx 0.85$）

### MCMC 入门

用 Markov 链从复杂分布中采样——遍历定理保证收敛。

---

## 频率派 vs 贝叶斯派

- **频率派**：$P$ = 长期频率极限。参数固定。MLE。
- **贝叶斯派**：$P$ = 信念强度。参数随机。后验分布。

**ML 实践**：大多数 DL 是频率派的；VAE / diffusion / RLHF 有贝叶斯根源。

---

## 🟠 不足层

1. **无测度论**：条件期望的一般定义、连续 Markov 链的严格处理需要测度论
2. **i.i.d. 假设**：时间序列不满足
3. **CLT 对重尾分布失效**：Cauchy 方差不存在
4. **Poisson 过程的均匀到达假设**：现实中到达可能有 burst（非齐次 Poisson）

---

## 🔴 应用层

| 概念 | ML 场景 |
|---|---|
| Bayes | 朴素贝叶斯 / 贝叶斯推断 |
| CLT | BatchNorm / 统计检验 |
| Poisson 过程 | 事件流 / 点击率 |
| Markov 链 | MCMC / PageRank / RL |
| MGF | 分布卷积 / CLT 证明 |

---

## 与 work4ai 讲透系列的交叉

- **讲透朴素贝叶斯**：Bayes + 条件独立
- **讲透 PageRank**：Markov 链平稳分布
- **讲透 SGD**：LLN + CLT
- **讲透 MCMC**：Markov 链遍历定理
