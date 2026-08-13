# Stanford MATH 230A · 习题集（Durrett 精选 + ML 理论应用）

---

## 基础题

### Q1.1（收敛模式蕴含链）
证明 $L^p$ 收敛蕴含依概率收敛，但反之不然。

<details><summary>解</summary>

$L^p \Rightarrow P$：由 Markov 不等式 $P(|X_n-X|>\epsilon) \leq E|X_n-X|^p/\epsilon^p \to 0$

反例：$P(X_n = n) = 1/n$, $P(X_n = 0) = 1-1/n$。$X_n \xrightarrow{P} 0$ 但 $E|X_n|^p = n^p/n = n^{p-1} \to \infty$（$p \geq 1$）✗

**ML 关联**：均方收敛（$L^2$）比依概率收敛更强——但 SGD 分析通常只需依概率。
</details>

### Q1.2（CLT 应用）
$X_1, \dots, X_{50}$ i.i.d. Poisson(4)。估计 $P(S_{50} > 220)$。

<details><summary>解</summary>

$\mu = 4, \sigma^2 = 4, n = 50$

$P(S_{50} > 220) = P\left(\frac{S-200}{\sqrt{200}} > \frac{20}{\sqrt{200}}\right) \approx P(Z > 1.414) \approx 0.079$

**ML 关联**：模型性能评估的假设检验。
</details>

---

## 中等题

### Q2.1（鞅判定 + 可选停时）
$X_1, \dots$ i.i.d. 均值 0。证明 $S_n$ 是鞅，并用可选停时求对称随机游走首达 $\pm a$ 的期望时间。

<details><summary>解</summary>

鞅性：$E[S_{n+1}|\mathcal{F}_n] = S_n + E[X_{n+1}] = S_n$ ✓

$S_n^2 - n$ 也是鞅。可选停时：$E[S_\tau^2 - \tau] = 0 \Rightarrow E[\tau] = a^2$

**ML 关联**：RL 中到达目标状态的期望步数。
</details>

### Q2.2（Hoeffding → 泛化界）
推导有限假设类的 PAC 泛化界：以至少 $1-\delta$ 概率，$\forall h: |R(h)-\hat{R}(h)| \leq \sqrt{\frac{\ln(2|\mathcal{H}|/\delta)}{2n}}$。

<details><summary>解</summary>

对每个 $h_j$：$P(|\hat{R}(h_j)-R(h_j)|>\epsilon) \leq 2e^{-2n\epsilon^2}$

Union bound：$P(\exists j: \ldots) \leq 2|\mathcal{H}|e^{-2n\epsilon^2} = \delta$

$\epsilon = \sqrt{\frac{\ln(2|\mathcal{H}|/\delta)}{2n}}$ ✓

**ML 关联**：所有泛化理论的起点。
</details>

---

## 开放题

### Q3.1（SGD 的鞅分析）★
解释为什么 SGD 的梯度噪声 $\delta_t = \nabla L - \nabla\hat{L}_B$ 是鞅差序列，以及这如何用于收敛分析。

<details><summary>解（思路）</summary>

mini-batch 随机采样 → $\delta_t$ 关于历史 $\mathcal{F}_t$ 的条件期望为 0 → 鞅差

Azuma-Hoeffding：$P(|\sum_{t=1}^T \delta_t| \geq t) \leq 2e^{-t^2/(2Tc^2)}$

→ SGD 梯度累积误差 $O(\sqrt{T})$ → 收敛速率 $O(1/\sqrt{T})$（凸情况）
</details>

### Q3.2（扩散模型的概率推导）★
写出 DDPM（Ho et al., arXiv:2006.11239 ✅）的前向加噪过程，并解释它如何对应 SDE。

<details><summary>解（思路）</summary>

前向：$q(x_t|x_{t-1}) = \mathcal{N}(\sqrt{1-\beta_t}x_{t-1}, \beta_t I)$

边际：$q(x_t|x_0) = \mathcal{N}(\sqrt{\bar\alpha_t}x_0, (1-\bar\alpha_t)I)$

连续极限 → SDE：$dX_t = -\frac{1}{2}\beta_t X_t\,dt + \sqrt{\beta_t}\,dW_t$

**ML 关联**：扩散模型的训练目标 = 估计每步的噪声 $\epsilon$（等价于 score matching）。
</details>

### Q-Final（PAC-Bayes 泛化界）★
推导 PAC-Bayes 泛化界，解释 $\text{KL}(Q\|P)$ 的含义。

<details><summary>解（思路）</summary>

Hoeffding + 测度变换（Donsker-Varadhan）：

$E_Q[e^{-2n\epsilon^2}] \leq e^{\text{KL}(Q\|P)} \cdot e^{-2n\epsilon^2}$

$\epsilon = \sqrt{\frac{\text{KL}(Q\|P)+\ln(2\sqrt{n}/\delta)}{2n}}$

$\text{KL}(Q\|P)$：后验 $Q$（学到的）与先验 $P$（假设空间）的距离。简单模型 KL 小 → 泛化好。
</details>
