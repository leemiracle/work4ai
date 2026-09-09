# UC Berkeley STAT 134 · 概率笔记（Pitman *Probability*）

> **教材**：Pitman, *Probability* (Springer) — **本科应用概率的最佳入门书**
> **一手核实**：Berkeley Stat 134 课程大纲 + Pitman 教材目录
> **特色**：无测度论，直觉优先，强调 Bayes + 常见分布 + 极限定理

---

## 费曼三层讲透

### 🟢 直觉层

- **概率 = 不确定性的大小**：频率派说"长期频率的极限"，贝叶斯派说"信念的强度"——两种解读都有用
- **条件概率 = "知道新信息后的修正"**：Bayes 定理告诉你如何用观测更新信念
- **CLT = "平均值的分布趋近于钟形"**：无论原始分布长什么样，样本均值在足够多时会正态化

---

### 🔵 数学层

## 核心框架

```
概率公理 → 条件概率 → Bayes → 随机变量 → 常见分布 → 期望/方差 → LLN → CLT
───────   ─────────   ─────   ────────   ────────   ─────────   ───   ───
可加性     P(A|B)      后验    离散/连续   Bernoulli   线性性      收敛   正态化
归一化     独立性      似然    PMF/PDF     Normal      方差公式     频率   标准化
```

---

## 第 1 章：概率空间与条件概率

### 1.1 概率公理（Kolmogorov）

1. $P(A) \geq 0$
2. $P(\Omega) = 1$
3. $A_i$ 互斥 $\Rightarrow P(\bigcup A_i) = \sum P(A_i)$

### 1.2 条件概率 ★

$$P(A|B) = \frac{P(A \cap B)}{P(B)}$$

**直觉**：$P(A|B)$ = "知道 $B$ 发生后，$A$ 发生的概率"。

### 1.3 Bayes 定理 ★★★

$$P(H|D) = \frac{P(D|H)P(H)}{P(D)} = \frac{P(D|H)P(H)}{\sum_i P(D|H_i)P(H_i)}$$

- $P(H)$：先验（数据前的信念）
- $P(D|H)$：似然（假设 $H$ 下看到数据 $D$ 的概率）
- $P(H|D)$：后验（数据后的信念）

**经典例子**：疾病检测
- 发病率 $P(D) = 0.001$，检测准确率 $P(+|D) = 0.99$，假阳性 $P(+|\bar{D}) = 0.05$
- $P(D|+) = \frac{0.99 \times 0.001}{0.99 \times 0.001 + 0.05 \times 0.999} \approx 0.019$

**直觉**：即使检测"准确率 99%"，阳性后真正患病的概率只有 2%！（因为发病率极低）

**ML 关联**：朴素贝叶斯分类器、变分推断、贝叶斯神经网络。

### 1.4 独立性

$A \perp B \iff P(A \cap B) = P(A)P(B)$

**条件独立**：$A \perp B | C \iff P(A \cap B|C) = P(A|C)P(B|C)$

**ML 关联**：朴素贝叶斯假设特征条件独立于类别。

---

## 第 2 章：随机变量

### 2.1 离散随机变量

PMF: $p(x) = P(X = x)$

### 2.2 连续随机变量

PDF: $f(x)$，$P(a \leq X \leq b) = \int_a^b f(x)\,dx$

CDF: $F(x) = P(X \leq x)$

---

## 第 3 章：常见分布 ★★

### 离散分布

| 分布 | PMF | 期望 | 方差 | ML 关联 |
|---|---|---|---|---|
| **Bernoulli($p$)** | $p^x(1-p)^{1-x}$ | $p$ | $p(1-p)$ | 二分类基础 |
| **Binomial($n,p$)** | $\binom{n}{x}p^x(1-p)^{n-x}$ | $np$ | $np(1-p)$ | 多次试验计数 |
| **Poisson($\lambda$)** | $e^{-\lambda}\lambda^x/x!$ | $\lambda$ | $\lambda$ | 稀疏事件、点击率 |
| **Geometric($p$)** | $(1-p)^{x-1}p$ | $1/p$ | $(1-p)/p^2$ | 首次成功等待时间 |
| **Negative Binomial** | $\binom{x-1}{r-1}p^r(1-p)^{x-r}$ | $r/p$ | $r(1-p)/p^2$ | $r$ 次成功的等待 |

### 连续分布

| 分布 | PDF | 期望 | 方差 | ML 关联 |
|---|---|---|---|---|
| **Uniform($a,b$)** | $1/(b-a)$ | $(a+b)/2$ | $(b-a)^2/12$ | 随机初始化 |
| **Normal($\mu,\sigma^2$)** | $\frac{1}{\sqrt{2\pi}\sigma}e^{-(x-\mu)^2/(2\sigma^2)}$ | $\mu$ | $\sigma^2$ | CLT 核心 |
| **Exponential($\lambda$)** | $\lambda e^{-\lambda x}$ | $1/\lambda$ | $1/\lambda^2$ | 生存分析 |
| **Gamma($\alpha,\beta$)** | $\frac{\beta^\alpha}{\Gamma(\alpha)}x^{\alpha-1}e^{-\beta x}$ | $\alpha/\beta$ | $\alpha/\beta^2$ | 正态先验 |
| **Beta($\alpha,\beta$)** | $\frac{x^{\alpha-1}(1-x)^{\beta-1}}{B(\alpha,\beta)}$ | $\alpha/(\alpha+\beta)$ | — | 概率参数先验 |

### 正态分布的性质 ★

1. **线性变换**：$X \sim \mathcal{N}(\mu,\sigma^2) \Rightarrow aX+b \sim \mathcal{N}(a\mu+b, a^2\sigma^2)$
2. **卷积**：$X \sim \mathcal{N}(\mu_1,\sigma_1^2)$, $Y \sim \mathcal{N}(\mu_2,\sigma_2^2)$ 独立 $\Rightarrow X+Y \sim \mathcal{N}(\mu_1+\mu_2, \sigma_1^2+\sigma_2^2)$
3. **标准化**：$Z = (X-\mu)/\sigma \sim \mathcal{N}(0,1)$

**ML 关联**：权重初始化、CLT、Bayesian prior。

### 指数分布的无记忆性 ★

$$P(X > s+t | X > s) = P(X > t)$$

**ML 关联**：几何折扣 $\gamma^t$（RL）是离散版无记忆性。

---

## 第 4 章：期望与方差

### 4.1 期望

$$E[X] = \sum_x x\,p(x) \quad \text{或} \quad E[X] = \int x\,f(x)\,dx$$

### 4.2 期望的线性性 ★

$$E[aX + bY] = aE[X] + bE[Y]$$

**注意**：不需要 $X, Y$ 独立！

### 4.3 方差

$$\text{Var}(X) = E[(X-\mu)^2] = E[X^2] - (E[X])^2$$

$$\text{Var}(aX+b) = a^2\text{Var}(X)$$

### 4.4 协方差与相关系数

$$\text{Cov}(X,Y) = E[(X-\mu_X)(Y-\mu_Y)] = E[XY] - E[X]E[Y]$$

$$\rho = \frac{\text{Cov}(X,Y)}{\sigma_X \sigma_Y} \in [-1, 1]$$

**关键**：$X \perp Y \Rightarrow \text{Cov}(X,Y) = 0$（但反之不成立！）

$$\text{Var}(X+Y) = \text{Var}(X) + \text{Var}(Y) + 2\text{Cov}(X,Y)$$

---

## 第 5 章：极限定理 ★★★

### 5.1 大数定律 (LLN)

> $X_1, \dots, X_n$ i.i.d., $E[X_i] = \mu$：
> $$\bar{X}_n = \frac{1}{n}\sum X_i \xrightarrow{P} \mu$$

**直觉**：样本量足够大时，样本均值 ≈ 期望。

**ML 关联**：SGD——梯度 $\nabla L(\theta) \approx \frac{1}{n}\sum\nabla\ell(\theta; x_i)$，mini-batch 平均梯度逼近真实梯度。

### 5.2 中心极限定理 (CLT) ★★★

> $X_1, \dots, X_n$ i.i.d., $EX_i = \mu$, $\text{Var}(X_i) = \sigma^2$：
> $$\frac{\bar{X}_n - \mu}{\sigma/\sqrt{n}} \xrightarrow{d} \mathcal{N}(0,1)$$
> 即 $\bar{X}_n \approx \mathcal{N}(\mu, \sigma^2/n)$

**直觉**：无论 $X_i$ 是什么分布，样本均值（标准化后）趋于正态。

**ML 关联**：
- mini-batch 梯度噪声 $\approx \mathcal{N}(0, \sigma^2/n)$ → batch size 越大，噪声越小
- BatchNorm：归一化激活值，利用 CLT 使分布稳定

### 5.3 Chebyshev 不等式

$$P(|X - \mu| \geq k) \leq \frac{\sigma^2}{k^2}$$

**ML 关联**：集中不等式的最简单形式 → 泛化界的雏形。

### 5.4 正态近似

Binomial($n,p$) ≈ $\mathcal{N}(np, np(1-p))$（当 $n$ 大时）

Poisson($\lambda$) ≈ $\mathcal{N}(\lambda, \lambda)$（当 $\lambda$ 大时）

---

## 第 6 章：母函数（Generating Functions）

### 概率母函数

$$G_X(s) = E[s^X] = \sum_x s^x p(x)$$

**性质**：
- $G_X(1) = 1$
- $E[X] = G_X'(1)$
- $X \perp Y \Rightarrow G_{X+Y}(s) = G_X(s)G_Y(s)$

### 矩母函数

$$M_X(t) = E[e^{tX}]$$

**ML 关联**：CLT 的证明工具（特征函数的弱化版）。

---

## 频率派 vs 贝叶斯派 ★★

**频率派**：概率 = 长期频率的极限。参数是固定的。MLE。

**贝叶斯派**：概率 = 信念强度。参数是随机变量。MAP / 后验分布。

**ML 实践**：
- 频率派：SGD + cross-entropy → 点估计 $\hat{\theta}$
- 贝叶斯派：VAE / Bayesian NN → 后验分布 $p(\theta|D)$，量化不确定性

---

## 🟠 不足层（局限性）

1. **无测度论**：条件期望的一般定义、连续随机变量的严格处理需要测度论。Stat 134 只给离散/连续特殊情况。

2. **i.i.d. 假设**：现实数据有时间依赖性、空间依赖性，i.i.d. 不成立。

3. **CLT 的局限**：重尾分布（Cauchy、Pareto）的方差不存在，CLT 失效。样本均值不收敛到正态。

4. **Bayes 定理的先验主观性**：贝叶斯方法需要指定先验，不同先验导致不同后验。这在科学上常被批评。

---

## 🔴 应用层（ML 公式级对应）

| 概念 | 公式 | ML 场景 |
|---|---|---|
| Bayes 定理 | $P(\theta\|D) = \frac{P(D\|\theta)P(\theta)}{P(D)}$ | 朴素贝叶斯 / 贝叶斯推断 |
| LLN | $\bar{X}_n \to \mu$ | SGD 梯度平均 |
| CLT | $\bar{X}_n \approx \mathcal{N}(\mu, \sigma^2/n)$ | 梯度噪声 / BatchNorm |
| Cross-entropy | $-\sum p\log q$ | 分类损失 |
| 期望线性性 | $E[\sum a_iX_i] = \sum a_iE[X_i]$ | 梯度计算 |
| Chebyshev | $P(\|X-\mu\| \geq k\sigma) \leq 1/k^2$ | 集中不等式入门 |

---

## 与 work4ai 讲透系列的交叉

- **讲透朴素贝叶斯**：Bayes 定理 + 条件独立
- **讲透 SGD**：LLN → 梯度收敛
- **讲透 BatchNorm**：CLT → 激活值正态化
- **讲透贝叶斯推断**：先验 + 似然 → 后验
