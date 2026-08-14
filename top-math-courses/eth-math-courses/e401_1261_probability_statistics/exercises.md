# ETH 401-1261 · 习题集（概率 + 统计推断 + ML 应用）

---

## 基础题

### Q1.1（MLE）
$X_1,\ldots,X_n \sim \text{Bernoulli}(p)$。求 $p$ 的 MLE，验证它是无偏的。

<details><summary>解</summary>

$\ell(p) = \sum x_i\log p + (n-\sum x_i)\log(1-p)$

$\frac{d\ell}{dp} = \frac{\sum x_i}{p} - \frac{n-\sum x_i}{1-p} = 0$

$\hat{p} = \frac{1}{n}\sum X_i = \bar{X}$

$E[\hat{p}] = p$ ✓（无偏）

**ML 关联**：二分类交叉熵的 MLE 本质。
</details>

### Q1.2（CLT → 置信区间）
$X_1,\ldots,X_{100} \sim \text{Uniform}(0,1)$。求 $\mu=E[X]$ 的 95% 置信区间。

<details><summary>解</summary>

$\mu=0.5$, $\sigma^2=1/12$, $\text{SE}=\sqrt{1/(12\times100)}=1/\sqrt{1200}\approx 0.0289$

95% CI：$0.5 \pm 1.96\times 0.0289 \approx 0.5\pm 0.0566$

即 $[0.443, 0.557]$。

**ML 关联**：模型性能估计的置信区间。
</details>

---

## 中等题

### Q2.1（假设检验）★
硬币掷 100 次，60 次正面。在 $\alpha=0.05$ 下检验 $H_0: p=0.5$。

<details><summary>解</summary>

$Z = \frac{0.6-0.5}{\sqrt{0.5\times0.5/100}} = \frac{0.1}{0.05} = 2.0$

$|Z|=2.0 > 1.96$ → 拒绝 $H_0$

$p$-value $= 2P(Z\geq 2.0)\approx 0.046 < 0.05$ ✓

**ML 关联**：A/B 测试的核心逻辑。
</details>

### Q2.2（Fisher 信息 + Cramér-Rao）★
$X \sim \text{Exponential}(\lambda)$。求 Fisher 信息 $I(\lambda)$ 和 MLE 的渐近方差。

<details><summary>解</summary>

$\log p(x|\lambda) = \log\lambda - \lambda x$

$\frac{\partial^2}{\partial\lambda^2}\log p = -1/\lambda^2$

$I(\lambda) = -E[-1/\lambda^2] = 1/\lambda^2$

MLE：$\hat\lambda = 1/\bar{X}$

渐近方差：$1/(nI(\lambda)) = \lambda^2/n$

**ML 关联**：Fisher 信息 = 参数估计精度的理论极限。
</details>

### Q2.3（贝叶斯后验）
$X|\theta \sim \text{Bernoulli}(\theta)$，先验 $\theta\sim\text{Beta}(a,b)$。求后验分布。

<details><summary>解</summary>

$p(\theta|D) \propto \theta^{\sum x_i}(1-\theta)^{n-\sum x_i}\cdot\theta^{a-1}(1-\theta)^{b-1}$

$= \theta^{\sum x_i+a-1}(1-\theta)^{n-\sum x_i+b-1}$

→ 后验 $\text{Beta}(\sum x_i+a, n-\sum x_i+b)$（共轭先验）

**ML 关联**：贝叶斯平滑 / Laplace 平滑。
</details>

---

## 开放题

### Q3.1（交叉熵 = 负对数似然）★
证明多分类交叉熵 loss 等价于 MLE，并解释为什么 softmax 是自然的输出。

<details><summary>解（思路）</summary>

似然：$\prod_i p_{y_i} = \prod_i \frac{e^{z_{y_i}}}{\sum_j e^{z_j}}$

负对数似然：$-\sum_i\log\frac{e^{z_{y_i}}}{\sum_j e^{z_j}}$（= 交叉熵 loss）

Softmax 是分类分布（categorical）的自然参数化。

**ML 关联**：为什么深度学习用交叉熵 loss。
</details>

### Q3.2（Conformal Prediction 简介）★
解释 conformal prediction 如何用交换性（exchangeability）构造有限样本覆盖保证的预测区间。

<details><summary>解（思路）</summary>

1. 假设数据是可交换的（弱于 i.i.d.）
2. 定义 nonconformity score $s_i = |y_i - \hat{f}(x_i)|$
3. 新样本的 $1-\alpha$ 预测区间：$[\hat{f}(x_{n+1}) - s_{(\lceil(n+1)(1-\alpha)\rceil)}, \ldots]$
4. 覆盖率 $P(y_{n+1}\in\text{interval})\geq 1-\alpha$（有限样本，无分布假设）

**ML 关联**：大模型不确定性量化的工具。
</details>

### Q-Final（频率派 vs 贝叶斯派 → VAE）★
从 MLE 出发，推导 VAE 的 ELBO 是 MLE 的变分下界。讨论频率派与贝叶斯派在此的融合。

<details><summary>解（思路）</summary>

**频率派 MLE**：$\hat\theta = \arg\max_\theta\log p(x|\theta)$

**隐变量模型**：$\log p(x|\theta) = \log\int p(x,z|\theta)\,dz$

**Jensen 不等式**（变分下界）：

$\log p(x|\theta) \geq E_{q(z)}\left[\log\frac{p(x,z|\theta)}{q(z)}\right] = \text{ELBO}$

**融合视角**：
- VAE 的编码器 $q_\phi(z|x)$ 是贝叶斯后验的变分近似
- 解码器 $p_\theta(x|z)$ 的训练目标源于频率派 MLE
- $\Rightarrow$ 频率派 MLE + 贝叶斯后验近似 = VAE

**ML 关联**：VAE 是频率派与贝叶斯派最完美的融合。
</details>
