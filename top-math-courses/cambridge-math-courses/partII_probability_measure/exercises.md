# Cambridge Part II · Probability and Measure 习题集（Williams 精选 + ML 理论应用）

---

## 基础题

### Q1.1（收敛模式判定）
$X_n$ 独立，$P(X_n = 1) = 1/n$, $P(X_n = 0) = 1 - 1/n$。判断 $X_n$ 的收敛模式。

<details><summary>解</summary>

**依概率**：$P(|X_n - 0| > \epsilon) = P(X_n = 1) = 1/n \to 0$。所以 $X_n \xrightarrow{P} 0$ ✓

**几乎必然**：$\sum P(X_n = 1) = \sum 1/n = \infty$。由 Borel-Cantelli 第二引理（独立性），$P(X_n = 1 \text{ i.o.}) = 1$。所以 $X_n \not\xrightarrow{a.s.} 0$ ✗

**$L^p$**：$E|X_n|^p = 1/n \to 0$。所以 $X_n \xrightarrow{L^p} 0$ ✓

**结论**：$X_n \xrightarrow{P} 0$, $X_n \xrightarrow{L^p} 0$，但 $X_n \not\xrightarrow{a.s.} 0$。

**ML 关联**：依概率收敛 ≠ a.s. 收敛——泛化保证的强度差异。
</details>

### Q1.2（Fatou 引理严格不等）
构造 $f_n$ 使得 Fatou 引理严格成立：$\int\liminf f_n < \liminf\int f_n$。

<details><summary>解</summary>

取 $f_n = n \cdot \mathbf{1}_{(0, 1/n)}$（在 $(0,1)$ 上）。

- $\liminf f_n(x) = 0$ 对所有 $x$（因为 $f_n(x) = 0$ 当 $n > 1/x$）
- $\int f_n = n \cdot (1/n) = 1$，$\liminf\int f_n = 1$

所以 $\int\liminf f_n = 0 < 1 = \liminf\int f_n$ ✓

**ML 关联**：警示——不能盲目交换极限与积分。DCT 的条件（有可积控制函数）是必要的。
</details>

---

## 中等题

### Q2.1（条件期望 = 投影）★
在 $L^2(\Omega, \mathcal{F}, P)$ 中，证明 $E[X|\mathcal{G}]$ 是 $X$ 到 $\mathcal{G}$-可测函数子空间 $L^2(\mathcal{G})$ 的正交投影。

<details><summary>解</summary>

令 $Y = E[X|\mathcal{G}]$，$Z = X - Y$。

需证 $Z \perp L^2(\mathcal{G})$：即对所有 $\mathcal{G}$-可测的 $W$，$E[ZW] = 0$。

对 $W \in L^2(\mathcal{G})$：
$$E[ZW] = E[(X - Y)W] = E[XW] - E[YW]$$

因为 $Y = E[X|\mathcal{G}]$ 且 $W$ 是 $\mathcal{G}$-可测：
$$E[YW] = E[E[X|\mathcal{G}]\cdot W] = E[E[XW|\mathcal{G}]] = E[XW]$$

（第三步：$W$ 是 $\mathcal{G}$-可测 → $XW$ 的条件期望中 $W$ 可提出）

所以 $E[ZW] = E[XW] - E[XW] = 0$ ✓

**ML 关联**：线性回归 $\hat{Y} = X\hat{\beta}$ 是 $Y$ 到 $X$ 的列空间的投影 = 条件期望 $E[Y|X]$ 的离散近似。
</details>

### Q2.2（Borel-Cantelli 应用）
$X_n$ i.i.d. Exponential(1)。证明 $P(X_n > n\log n \text{ i.o.}) = 0$。

<details><summary>解</summary>

$P(X_n > n\log n) = e^{-n\log n} = n^{-n}$

$\sum_{n=2}^\infty n^{-n} < \sum n^{-2} < \infty$（收敛）

由 Borel-Cantelli 第一引理：$P(X_n > n\log n \text{ i.o.}) = 0$ ✓

**ML 关联**：a.s. 收敛证明的标准工具——证明"坏事件"只发生有限次。
</details>

### Q2.3（鞅判定）
$X_1, X_2, \dots$ i.i.d., $E[X_i] = 0$, $\text{Var}(X_i) = \sigma^2$。证明 $S_n^2 - n\sigma^2$ 是鞅。

<details><summary>解</summary>

$S_{n+1}^2 = (S_n + X_{n+1})^2 = S_n^2 + 2S_nX_{n+1} + X_{n+1}^2$

$E[S_{n+1}^2 - (n+1)\sigma^2 | \mathcal{F}_n]$
$= E[S_n^2 + 2S_nX_{n+1} + X_{n+1}^2 - (n+1)\sigma^2 | \mathcal{F}_n]$
$= S_n^2 + 2S_nE[X_{n+1}] + E[X_{n+1}^2] - (n+1)\sigma^2$
$= S_n^2 + 0 + \sigma^2 - (n+1)\sigma^2$
$= S_n^2 - n\sigma^2$ ✓

（第三步：$S_n$ 是 $\mathcal{F}_n$-可测，$X_{n+1}$ 与 $\mathcal{F}_n$ 独立）

**ML 关联**：用于推导对称随机游走的期望首达时间 $E[\tau] = a^2/\sigma^2$。
</details>

### Q2.4（Markov 链平稳分布）
Markov 链转移矩阵 $P = \begin{pmatrix} 0.5 & 0.5 \\ 0.3 & 0.7 \end{pmatrix}$，求平稳分布。

<details><summary>解</summary>

$\pi P = \pi$：
$$\pi_1 \cdot 0.5 + \pi_2 \cdot 0.3 = \pi_1$$
$$\pi_1 \cdot 0.5 + \pi_2 \cdot 0.7 = \pi_2$$

由第一个方程：$0.3\pi_2 = 0.5\pi_1 \Rightarrow \pi_2 = \frac{5}{3}\pi_1$

归一化：$\pi_1 + \frac{5}{3}\pi_1 = 1 \Rightarrow \pi_1 = \frac{3}{8}, \pi_2 = \frac{5}{8}$

**ML 关联**：PageRank = 在网页链接图上的 Markov 链平稳分布。MCMC 从平稳分布中采样。
</details>

---

## 开放题

### Q3.1（频率派 vs 贝叶斯派）
对同一个参数估计问题，分别用频率派（MLE）和贝叶斯派（MAP）方法求解，并讨论差异。

<details><summary>解（思路）</summary>

设 $X_1, \dots, X_n \sim \text{Bernoulli}(\theta)$。

**频率派（MLE）**：$\hat{\theta}_{\text{MLE}} = \bar{X}_n = \frac{1}{n}\sum X_i$

- 不引入先验，$\theta$ 是固定常数
- SLLN 保证 $\hat{\theta}_{\text{MLE}} \xrightarrow{a.s.} \theta$

**贝叶斯派（MAP）**：先验 $\theta \sim \text{Beta}(\alpha, \beta)$

后验 $\theta|D \sim \text{Beta}(\alpha + \sum X_i, \beta + n - \sum X_i)$

$\hat{\theta}_{\text{MAP}} = \frac{\alpha + \sum X_i - 1}{\alpha + \beta + n - 2}$（后验众数）

**差异**：
- 当 $n \to \infty$，两者趋同（先验被数据淹没）
- 小样本时，贝叶斯方法有先验正则化（防止极端估计）
- 贝叶斯方法给出完整后验分布（不确定性量化），频率派只给点估计

**ML 关联**：$L^2$ 正则化 = 高斯先验的 MAP；$L^1$ 正则化 = 拉普拉斯先验的 MAP。
</details>

### Q3.2（鞅方法证明 RL 收敛）★
TD(0) 算法：$V(s) \leftarrow V(s) + \alpha[r + \gamma V(s') - V(s)]$。解释为什么 TD 误差在真值 $V^*$ 处是鞅差。

<details><summary>解（思路）</summary>

TD 误差 $\delta_t = r_t + \gamma V^*(s_{t+1}) - V^*(s_t)$

$E[\delta_t | \mathcal{F}_t] = E[r_t|s_t] + \gamma E[V^*(s_{t+1})|s_t] - V^*(s_t)$

由 Bellman 方程 $V^*(s) = E[r|s] + \gamma E[V^*(s')|s]$：

$E[\delta_t|\mathcal{F}_t] = V^*(s_t) - V^*(s_t) = 0$

所以 $\delta_t$ 是关于 $\mathcal{F}_t$ 的鞅差序列。

随机逼近定理：$V_{t+1}(s) = V_t(s) + \alpha_t \delta_t$，若 $\sum\alpha_t = \infty$, $\sum\alpha_t^2 < \infty$，则 $V_t \xrightarrow{a.s.} V^*$。

**ML 关联**：这就是 TD 学习收敛的理论保证。鞅差 + Robbins-Monro 条件 → a.s. 收敛。
</details>

### Q3.3（重尾分布让 CLT 失效）
Cauchy 分布的样本均值为什么不收敛到正态？用特征函数解释。

<details><summary>解（思路）</summary>

Cauchy 分布的特征函数 $\varphi(t) = e^{-|t|}$。

样本均值 $\bar{X}_n = S_n/n$ 的特征函数：
$$\varphi_{\bar{X}_n}(t) = [\varphi(t/n)]^n = [e^{-|t|/n}]^n = e^{-|t|}$$

所以 $\bar{X}_n$ 的分布 = 原始 Cauchy 分布！（与 $n$ 无关）

**根本原因**：Cauchy 分布的方差不存在 → CLT 条件不满足。

**广义 CLT**：对于 $\alpha$-稳定分布（$0 < \alpha < 2$），样本均值收敛到同族稳定分布（不是正态）。

**ML 关联**：梯度裁剪 / Huber loss 的动机——重尾噪声让标准梯度方法失效。
</details>

### Q-Final（MCMC 遍历定理应用）★
Metropolis-Hastings 算法的接受概率 $\alpha = \min(1, \frac{\pi(y)q(x|y)}{\pi(x)q(y|x)})$。证明平稳分布是 $\pi$，并用遍历定理解释采样原理。

<details><summary>解（思路）</summary>

**细致平衡（detailed balance）**：需证 $\pi(x)P(x,y) = \pi(y)P(y,x)$

$P(x,y) = q(y|x)\alpha(x,y) = q(y|x)\min\left(1, \frac{\pi(y)q(x|y)}{\pi(x)q(y|x)}\right)$

情况 1：$\frac{\pi(y)q(x|y)}{\pi(x)q(y|x)} \geq 1$

$\alpha(x,y) = 1$, $\alpha(y,x) = \frac{\pi(x)q(y|x)}{\pi(y)q(x|y)}$

$\pi(x)q(y|x) \cdot 1 = \pi(y)q(x|y) \cdot \frac{\pi(x)q(y|x)}{\pi(y)q(x|y)} = \pi(x)q(y|x)$ ✓

情况 2 类似。→ 细致平衡成立 → $\pi$ 是平稳分布。

**遍历定理**：不可约 + 非周期 → $\frac{1}{N}\sum_{i=1}^N f(X_i) \xrightarrow{a.s.} E_\pi[f(X)]$

所以 MCMC 样本的经验平均 = 后验期望的 a.s. 估计。

**ML 关联**：MCMC 是贝叶斯推断的核心工具——从不可归一化的后验 $\pi(x) \propto p(x|D)$ 中采样。
</details>
