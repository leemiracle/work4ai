# Princeton MAT 514 · 习题集（Durrett + KL 散度 + 信息论桥梁）

---

## 基础题

### Q1.1（收敛模式）
证明依概率收敛蕴含依分布收敛，但反之不然。

<details><summary>解</summary>

$P \Rightarrow d$：$|F_n(x)-F(x)| \leq P(|X_n-X|>\epsilon) + P(X \leq x+\epsilon) - P(X \leq x-\epsilon)$。取 $\epsilon\to 0$。

反例：$X_n = X + 1/n$（同分布序列）依分布收敛到 $X$ 但不依概率收敛（$|X_n-X|=1/n \not\to 0$... 实际上 $P(|X_n-X|>\epsilon)=0$ for $n>1/\epsilon$，所以这个例子不对）。

正确反例：$X_n \sim \mathcal{N}(0,1)$ i.i.d.，$X \sim \mathcal{N}(0,1)$ 独立于 $X_n$。$X_n \xRightarrow{d} X$ 但 $P(|X_n-X|>\epsilon)$ 不收敛到 0。

**ML 关联**：CLT（依分布收敛）比依概率收敛更弱。
</details>

### Q1.2（Radon-Nikodym 计算）
$P = \mathcal{N}(0,1)$, $Q = \mathcal{N}(1,1)$。求 $dP/dQ$ 和 $\text{KL}(P\|Q)$。

<details><summary>解</summary>

$\frac{dP}{dQ}(x) = \frac{p(x)}{q(x)} = \frac{e^{-x^2/2}}{e^{-(x-1)^2/2}} = e^{x - 1/2}$

$\text{KL}(P\|Q) = E_P[\log\frac{dP}{dQ}] = E_P[x-1/2] = 0-1/2 = -1/2$...

等一下，让我重算。$\text{KL}(P\|Q) = E_P[\log\frac{p}{q}] = E_P[x-1/2] = 0 - 1/2$ 不对。

$\log\frac{p(x)}{q(x)} = \log e^{x-1/2} = x - 1/2$

$E_P[x-1/2] = 0 - 1/2 = -1/2$？但 KL 必须 $\geq 0$！

错误在 $\log(p/q)$ 的计算：$-x^2/2 + (x-1)^2/2 = (-x^2+x^2-2x+1)/2 = (-2x+1)/2 = -x+1/2$

所以 $\text{KL}(P\|Q) = E_P[-x+1/2] = 0+1/2 = 1/2$ ✓

**ML 关联**：这就是 VAE 中高斯 KL 项的特例。
</details>

---

## 中等题

### Q2.1（Gibbs 不等式 KL ≥ 0）
用 Jensen 不等式证明 $\text{KL}(p\|q) \geq 0$。

<details><summary>解</summary>

$-\text{KL}(p\|q) = \sum p(x)\log\frac{q(x)}{p(x)}$

由 Jensen（$\log$ 凹）：$\sum p\log\frac{q}{p} \leq \log\sum p\cdot\frac{q}{p} = \log\sum q = \log 1 = 0$

所以 $-\text{KL} \leq 0 \Rightarrow \text{KL} \geq 0$ ✓

**ML 关联**：这就是 cross-entropy ≥ entropy 的证明 → 分类 loss 的下界。
</details>

### Q2.2（可选停时 — 对称随机游走）
$S_n^2 - n$ 是鞅。用可选停时推导对称随机游走首达 $\pm a$ 的期望时间。

<details><summary>解</summary>

$E[S_\tau^2 - \tau] = E[S_0^2 - 0] = 0$

$S_\tau = \pm a \Rightarrow S_\tau^2 = a^2$

$E[\tau] = a^2$ ✓

**ML 关联**：RL 中到达目标的期望步数。
</details>

### Q2.3（Cross-entropy = H + KL）
证明 $H(p,q) = H(p) + \text{KL}(p\|q)$，解释为什么最小化 cross-entropy 等价于最小化 KL。

<details><summary>解</summary>

$H(p,q) = -\sum p\log q = -\sum p\log p + \sum p\log p - \sum p\log q = H(p) + \text{KL}(p\|q)$

当 $p$ 固定（真实标签），$H(p)$ 是常数 → $\min H(p,q) = \min \text{KL}(p\|q)$ ✓

**ML 关联**：分类任务的最优性。
</details>

---

## 开放题

### Q3.1（VAE ELBO 推导）★
用 Jensen 不等式推导 VAE 的 ELBO，解释 Radon-Nikodym 导数在其中的角色。

<details><summary>解（思路）</summary>

$\log p(x) = \log\int p(x,z)\,dz = \log E_{q(z)}\left[\frac{p(x,z)}{q(z)}\right] \geq E_{q(z)}\left[\log\frac{p(x,z)}{q(z)}\right]$

$= E_q[\log p(x|z)] - \text{KL}(q(z)\|p(z))$

$\frac{p(x,z)}{q(z)}$ 就是 Radon-Nikodym 导数 $dP/dQ$ 的类比。

**ML 关联**：VAE 训练 = 最大化 ELBO。
</details>

### Q3.2（PAC-Bayes 泛化界）★
用 KL 散度 + Pinsker 不等式推导 PAC-Bayes 泛化界。

<details><summary>解（思路）</summary>

对每个 $h$：Hoeffding → $P(R(h)-\hat{R}(h)>\epsilon) \leq e^{-2n\epsilon^2}$

测度变换（Donsker-Varadhan）：$E_Q[e^{-2n\epsilon^2}] \leq e^{\text{KL}(Q\|P)}e^{-2n\epsilon^2}$

令 $= \delta$：$\epsilon = \sqrt{\frac{\text{KL}(Q\|P)+\ln(2\sqrt{n}/\delta)}{2n}}$

**ML 关联**：KL 散度量化"学到的策略与先验的距离" → 泛化能力。
</details>

### Q-Final（Pinsker 不等式证明）★
证明 $\text{TV}(P,Q) \leq \sqrt{\text{KL}(P\|Q)/2}$。

<details><summary>解（思路）</summary>

$\text{TV}(P,Q) = \frac{1}{2}\sum|p_i-q_i| = \frac{1}{2}\sum p_i|1-q_i/p_i|$

由 Pinsker 不等式的标准证明（分情况 $q_i/p_i \leq 1$ 和 $>1$，用 $\log$ 的切线界）：

$|p-q| \leq \sqrt{2p\log(p/q) + 2q\log(q/p)} \cdot \sqrt{p}/\sqrt{2}$

最终用 Cauchy-Schwarz 整合 → $\text{TV} \leq \sqrt{\text{KL}/2}$ ✓

**ML 关联**：Pinsker 不等式连接 KL 散度与全变差 → PAC-Bayes 泛化界的桥梁。
</details>
