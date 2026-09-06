# MIT 18.175 · 习题集（Durrett 精选 + ML 理论应用）

---

## 第 1 章 · 大数定律

### Q1.1（WLLN 证明思路）
用 Chebyshev 不等式证明弱大数定律。

<details><summary>解</summary>

$P(|S_n/n - \mu| > \epsilon) \leq \frac{\text{Var}(S_n/n)}{\epsilon^2} = \frac{\sigma^2}{n\epsilon^2} \to 0$

**ML 关联**：训练损失收敛到期望损失的理论保证。
</details>

### Q1.2（Borel-Cantelli 引理）
$P(A_n) < \infty \Rightarrow P(A_n \text{ i.o.}) = 0$。

<details><summary>解</summary>

$P(\limsup A_n) = P(\bigcap_N \bigcup_{n \geq N} A_n) \leq P(\bigcup_{n \geq N} A_n) \leq \sum_{n \geq N} P(A_n) \to 0$（因级数收敛，尾部 $\to 0$）。

**ML 关联**：证明"几乎必然收敛"的标准工具。
</details>

---

## 第 2 章 · 中心极限定理

### Q2.1（CLT 应用）★
$X_1, \dots, X_n$ i.i.d. Bernoulli(0.5)。$n = 100$，估计 $P(S_{100} \geq 60)$。

<details><summary>解</summary>

$\mu = 0.5, \sigma^2 = 0.25$

$P(S_{100} \geq 60) = P\left(\frac{S_{100} - 50}{5} \geq 2\right) \approx 1 - \Phi(2) \approx 0.0228$

**精确值**（用二项分布）：$P \approx 0.0284$（CLT 略低估）。

**ML 关联**：假设检验——"模型 A 是否显著好于 B"。
</details>

### Q2.2（Berry-Esseen 收敛速度）
标准化的样本均值与 $N(0,1)$ 的最大偏差是多少？

<details><summary>解</summary>

由 Berry-Esseen: $\sup_x |F_n(x) - \Phi(x)| \leq \frac{C \cdot E|X_i|^3}{\sigma^3 \sqrt{n}}$

对 Bernoulli(0.5): $E|X-\mu|^3/\sigma^3 = 1$, 所以误差 $\leq C/\sqrt{n}$（$C \approx 0.4748$）。

$n = 100$: 误差 $\leq 0.047$；$n = 10000$: 误差 $\leq 0.0047$。
</details>

---

## 集中不等式

### Q3.1（Hoeffding）★
$X_1, \dots, X_n$ i.i.d. $[0,1]$-值，$\mu = E[X]$。证明 $P(|\bar{X}_n - \mu| > \epsilon) \leq 2e^{-2n\epsilon^2}$。

<details><summary>解</summary>

Hoeffding: 每个 $X_i \in [0,1]$, $\sum (b_i - a_i)^2 = n$。

$P(\bar{X}_n - \mu \geq \epsilon) \leq e^{-2n\epsilon^2}$（单边）

由对称: $P(|\bar{X}_n - \mu| \geq \epsilon) \leq 2e^{-2n\epsilon^2}$

**ML 关联**：这就是**泛化界**的核心——
$$P(\text{训练误差} - \text{真实误差} > \epsilon) \leq 2e^{-2n\epsilon^2}$$

取 union bound over $|\mathcal{H}|$ 个假设:
$$P(\exists h: |\hat{R}(h) - R(h)| > \epsilon) \leq 2|\mathcal{H}|e^{-2n\epsilon^2}$$

令右边 $= \delta$: $\epsilon = \sqrt{\frac{\ln(2|\mathcal{H}|/\delta)}{2n}}$

→ 经典泛化界。
</details>

### Q3.2（McDiarmid）
$f: \mathcal{X}^n \to \mathbb{R}$ 满足 $\sup_{x_1,\dots,x_n,x_i'} |f(x_1,\dots,x_i,\dots) - f(x_1,\dots,x_i',\dots)| \leq c_i$。则
$$P(|f - Ef| \geq t) \leq 2\exp\left(-\frac{2t^2}{\sum c_i^2}\right)$$

<details><summary>解（思路）</summary>

用鞅分解：$D_i = E[f | X_1,\dots,X_i] - E[f | X_1,\dots,X_{i-1}]$，则 $f - Ef = \sum D_i$ 是鞅差。$|D_i| \leq c_i$ → 用 Azuma 不等式。

**ML 关联**：**算法稳定性**推导（如果算法对单个训练样本的改动 Lipschitz，则泛化好）。
</details>

---

## 第 5 章 · 鞅

### Q5.1（鞅的判定）
$X_1, X_2, \dots$ i.i.d., $E[X_i] = 0$。证明 $S_n = X_1 + \dots + X_n$ 是鞅。

<details><summary>解</summary>

$E[S_{n+1} | \mathcal{F}_n] = E[S_n + X_{n+1} | \mathcal{F}_n] = S_n + E[X_{n+1}] = S_n + 0 = S_n$ ✓

**ML 关联**：SGD 的梯度噪声是鞅差 → 鞅收敛定理适用。
</details>

### Q5.2（可选停时）
对称随机游走从 0 开始，首次到达 $\pm a$ 的期望时间？

<details><summary>解</summary>

$\tau = \inf\{n : |S_n| = a\}$。$S_n$ 是鞅, $\tau$ 是停时。

如果可选停时适用：$E[S_\tau] = E[S_0] = 0$。

$S_\tau = \pm a$，$P(S_\tau = a) = 1/2$（对称），$E[S_\tau] = 0$ ✓

$E[\tau]$: 用 $S_n^2 - n$ 也是鞅 → $E[S_\tau^2 - \tau] = 0$ → $a^2 - E[\tau] = 0$ → $E[\tau] = a^2$。

**ML 关联**：随机游走到达边界的时间 = RL 中到达目标的步数。
</details>

---

## 综合大题

### Q-Final ★（泛化界推导）
用 Hoeffding + union bound 推导有限假设类的 PAC 泛化界。

<details><summary>解</summary>

设假设类 $\mathcal{H} = \{h_1, \dots, h_M\}$，$|\mathcal{H}| = M$。

对每个 $h_j$，由 Hoeffding:
$$P(|\hat{R}(h_j) - R(h_j)| > \epsilon) \leq 2e^{-2n\epsilon^2}$$

Union bound:
$$P(\exists j: |\hat{R}(h_j) - R(h_j)| > \epsilon) \leq 2M \cdot e^{-2n\epsilon^2} = \delta$$

解 $\epsilon$:
$$\epsilon = \sqrt{\frac{\ln(2M/\delta)}{2n}}$$

**PAC 界**：以至少 $1-\delta$ 的概率，
$$\forall h \in \mathcal{H}: |R(h) - \hat{R}(h)| \leq \sqrt{\frac{\ln(2M/\delta)}{2n}}$$

**ML 关联**：这是所有机器学习泛化理论的起点。
</details>
