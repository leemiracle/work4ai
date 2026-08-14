# Cambridge Part IA · 概率习题集（母函数特色 + ML 应用）

---

## 基础题

### Q1.1（Bayes 定理）
两枚硬币：一枚公平（双面），一枚两面都是正面。随机选一枚掷，得到正面。选的是双正硬币的概率？

<details><summary>解</summary>

$P(\text{双正}|\text{正}) = \frac{P(\text{正}|\text{双正})P(\text{双正})}{P(\text{正})}$

$= \frac{1 \times 0.5}{0.5 \times 1 + 0.5 \times 0.5} = \frac{0.5}{0.75} = \frac{2}{3}$

**ML 关联**：贝叶斯推断的后验更新。
</details>

### Q1.2（母函数求期望）
Poisson($\lambda$) 的母函数 $G(s) = e^{\lambda(s-1)}$。用母函数求 $E[X]$ 和 $\text{Var}(X)$。

<details><summary>解</summary>

$G'(s) = \lambda e^{\lambda(s-1)}$ → $E[X] = G'(1) = \lambda$

$G''(s) = \lambda^2 e^{\lambda(s-1)}$ → $E[X^2] = G''(1)+G'(1) = \lambda^2+\lambda$

$\text{Var}(X) = \lambda^2+\lambda-\lambda^2 = \lambda$ ✓

**ML 关联**：母函数是求矩的统一工具。
</details>

---

## 中等题

### Q2.1（独立和的母函数）★
$X \sim \text{Binomial}(m,p)$, $Y \sim \text{Binomial}(n,p)$ 独立。用母函数证明 $X+Y \sim \text{Binomial}(m+n,p)$。

<details><summary>解</summary>

$G_X(s) = ((1-p)+ps)^m$, $G_Y(s) = ((1-p)+ps)^n$

$G_{X+Y}(s) = G_X(s)G_Y(s) = ((1-p)+ps)^{m+n}$

→ $X+Y \sim \text{Binomial}(m+n,p)$ ✓

**ML 关联**：独立 Bernoulli 试验的聚合。
</details>

### Q2.2（CLT 应用）
$X_1,\dots,X_{36}$ i.i.d. Uniform(0,1)。估计 $P(S_{36} > 20)$。

<details><summary>解</summary>

$\mu=18$, $\sigma^2=3$, $\sigma=\sqrt{3}$

$P(S_{36}>20) = P\left(Z > \frac{2}{\sqrt{3}}\right) \approx P(Z>1.155) \approx 0.124$

**ML 关联**：A/B 测试的显著性判断。
</details>

### Q2.3（指数分布无记忆性）
证明 $X \sim \text{Exponential}(\lambda)$ 满足 $P(X>s+t|X>s) = P(X>t)$。

<details><summary>解</summary>

$P(X>s+t|X>s) = \frac{P(X>s+t)}{P(X>s)} = \frac{e^{-\lambda(s+t)}}{e^{-\lambda s}} = e^{-\lambda t} = P(X>t)$ ✓

**ML 关联**：RL 的几何折扣 $\gamma^t$ 是离散版无记忆性。
</details>

---

## 开放题

### Q3.1（朴素贝叶斯文本分类）★
给定训练集（垃圾邮件/正常邮件 + 词频），推导朴素贝叶斯分类器的预测公式。

<details><summary>解（思路）</summary>

$\hat{y} = \arg\max_y P(y)\prod_w P(w|y)$

条件独立假设：词在给定类别下独立。

**为什么"朴素"有效**：即使独立假设不成立，argmax 可能不受影响。
</details>

### Q3.2（CLT 与 SGD 噪声）★
解释为什么 mini-batch SGD 的梯度噪声近似正态，方差 $\propto 1/B$。

<details><summary>解（思路）</summary>

梯度 $= \frac{1}{B}\sum\nabla\ell_i$，由 CLT $\approx \mathcal{N}(\nabla L, \Sigma/B)$。

噪声方差 $\propto 1/B$ → batch size 越大噪声越小 → BatchNorm 稳定性。
</details>

### Q-Final（Markov 链平稳分布 + MCMC）★
3 状态 Markov 链转移矩阵 $P$。求平稳分布，并解释遍历定理如何用于 MCMC 采样。

<details><summary>解（思路）</summary>

$\pi P = \pi$ 求解（特征值 1 的左特征向量）。

遍历定理：$\frac{1}{n}\sum f(X_k) \to E_\pi[f]$ → MCMC 样本均值估计后验期望。

**ML 关联**：贝叶斯推断中从后验 $\pi(\theta|D)$ 采样。
</details>
