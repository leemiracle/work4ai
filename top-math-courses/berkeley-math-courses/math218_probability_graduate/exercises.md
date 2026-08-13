# UC Berkeley MATH 218 · 习题集（Durrett 精选 + 集中不等式 + ML 理论应用）

---

## 基础题

### Q1.1（收敛模式反例）
构造 $X_n \xrightarrow{P} 0$ 但 $X_n \not\xrightarrow{a.s.} 0$ 的例子。

<details><summary>解</summary>

令 $X_n = \mathbf{1}_{A_n}$，$A_n$ 独立，$P(A_n) = 1/n$。

依概率：$P(|X_n| > \epsilon) = 1/n \to 0$ ✓

a.s.：$\sum P(A_n) = \sum 1/n = \infty$，由 Borel-Cantelli，$P(A_n \text{ i.o.}) = 1$，所以 $X_n \not\to 0$ a.s. ✗

**ML 关联**：泛化保证的强度——a.s. 收敛比依概率更强。
</details>

### Q1.2（Hoeffding 推导泛化界）
$X_i \in [0,1]$ i.i.d.。用 Hoeffding 证明 $P(|\bar{X}_n - \mu| > \epsilon) \leq 2e^{-2n\epsilon^2}$。

<details><summary>解</summary>

Hoeffding：$P(|S_n - ES_n| \geq t) \leq 2e^{-2t^2/\sum(b_i-a_i)^2}$

$X_i \in [0,1]$ → $(b_i-a_i)^2 = 1$，$\sum = n$

$P(|S_n - n\mu| \geq n\epsilon) \leq 2e^{-2n^2\epsilon^2/n} = 2e^{-2n\epsilon^2}$

$P(|\bar{X}_n - \mu| \geq \epsilon) \leq 2e^{-2n\epsilon^2}$ ✓

**ML 关联**：这就是泛化界的核心——训练误差与真实误差的偏差。
</details>

---

## 中等题

### Q2.1（McDiarmid → 算法稳定性）★
如果算法 $A$ 改变一个训练样本最多改变输出 $c$，用 McDiarmid 证明泛化界。

<details><summary>解</summary>

$f(S) = R(A(S))$（算法 $A$ 在数据集 $S$ 上的真实风险）。

改变一个样本 $x_i$：$|f(S) - f(S')| \leq c$（Lipschitz 条件）

McDiarmid：$P(|f - Ef| \geq t) \leq 2e^{-2t^2/(nc^2)}$

$E[f] = E[R(A(S))]$（期望真实风险），$f = R(A(S))$（当前真实风险）

→ $P(|R(A(S)) - E[R(A(S))]| \geq t) \leq 2e^{-2t^2/(nc^2)}$

**结论**：如果算法稳定（$c$ 小），泛化误差的偏差指数衰减。

**ML 关联**：SGD 的随机性 → 算法稳定性 → 隐式正则化 → 泛化好。
</details>

### Q2.2（可选停时 — 对称随机游走）
对称随机游走从 0 出发，$S_n^2 - n$ 是鞅。用可选停时推导 $E[\tau] = a^2$。

<details><summary>解</summary>

$M_n = S_n^2 - n$ 是鞅（见 MIT 18.175 习题验证）。

$\tau = \inf\{n : |S_n| = a\}$。

如果可选停时适用：$E[M_\tau] = E[M_0] = 0$

$E[S_\tau^2 - \tau] = 0 \Rightarrow E[S_\tau^2] = E[\tau]$

$S_\tau = \pm a \Rightarrow S_\tau^2 = a^2$

$E[\tau] = a^2$ ✓

**ML 关联**：RL 中到达目标状态的期望步数分析。
</details>

### Q2.3（Brownian 运动的反射原理）
用反射原理证明 $P(\max_{s\leq t} W_s \geq a) = 2P(W_t \geq a)$。

<details><summary>解（思路）</summary>

反射原理：对于每条从 0 到 $\geq a$ 然后到 $W_t = x$ 的路径，反射首次越过 $a$ 后的部分，得到到 $W_t = 2a - x$ 的路径。一一对应。

$P(\max_{s\leq t} W_s \geq a, W_t \leq a) = P(W_t \geq a)$（反射后）

$P(\max \geq a) = P(\max \geq a, W_t \leq a) + P(W_t \geq a) = 2P(W_t \geq a)$ ✓

**ML 关联**：扩散模型中噪声路径的分析。
</details>

---

## 开放题

### Q3.1（SGD 的 SDE 极限）★
解释为什么 mini-batch SGD 的连续时间极限是 Langevin SDE $d\theta = -\nabla L\,dt + \sqrt{\eta\Sigma/B}\,dW$。

<details><summary>解（思路）</summary>

SGD 更新：$\theta_{t+1} = \theta_t - \eta\nabla\hat{L}(\theta_t) = \theta_t - \eta\nabla L(\theta_t) + \eta\delta_t$

其中 $\delta_t = \nabla L - \nabla\hat{L}$ 是梯度噪声。由 CLT，$\delta_t \approx \mathcal{N}(0, \Sigma/B)$。

连续化（$\eta \to 0$）：$d\theta = -\nabla L\,dt + \eta\sqrt{\Sigma/B}\,dW$

这就是 Langevin dynamics。

**稳态分布**：$\pi(\theta) \propto e^{-L(\theta)/\tau}$（$\tau = \eta\Sigma/(2B)$）

→ SGD 在长时间后采样自 $e^{-L/\tau}$ → 温度 $\tau$ 控制探索-利用权衡。

**ML 关联**：SGD 的隐式正则化 = 采样温度较低的后验分布。
</details>

### Q3.2（扩散模型的反向 SDE）★
写出扩散模型的前向 SDE 和反向 SDE，解释 score function 的作用。

<details><summary>解（思路）</summary>

**前向**：$dX_t = -\frac{1}{2}\beta_t X_t\,dt + \sqrt{\beta_t}\,dW_t$

（方差保持的加噪过程，$X_T \approx \mathcal{N}(0,I)$ 当 $T$ 大）

**反向**（Anderson 1982）：

$dX_t = \left[-\frac{1}{2}\beta_t X_t - \beta_t\nabla\log p_t(X_t)\right]dt + \sqrt{\beta_t}\,d\bar{W}_t$

（$\bar{W}$ 是反向时间的 Brownian 运动）

**Score function** $\nabla\log p_t(x)$：对数概率密度的梯度。指向高概率区域。

训练神经网络 $s_\theta(x,t) \approx \nabla\log p_t(x)$ → 用反向 SDE 生成新样本。

**ML 关联**：DDPM / Score-based generative models 的理论基础。
</details>

### Q-Final（PAC-Bayes 泛化界推导）★
推导 PAC-Bayes 泛化界：以至少 $1-\delta$ 概率，对所有后验 $Q$：

$$|E_Q[R] - E_Q[\hat{R}]| \leq \sqrt{\frac{\text{KL}(Q\|P) + \ln(2\sqrt{n}/\delta)}{2n}}$$

<details><summary>解（思路）</summary>

1. 对每个 $h$，Hoeffding：$P(R(h) - \hat{R}(h) > \epsilon) \leq e^{-2n\epsilon^2}$

2. 对先验 $P$ 取期望，改变测度到后验 $Q$：
   $$E_Q[e^{-2n\epsilon^2}] \leq e^{-2n\epsilon^2} \cdot e^{\text{KL}(Q\|P)}$$

3. 令右边 $= \delta$，解 $\epsilon$。

**$\text{KL}(Q\|P)$ 的含义**：后验 $Q$（学到的策略）与先验 $P$（假设空间）的距离。

**ML 关联**：
- 简单模型（$Q \approx P$）→ KL 小 → 泛化界紧
- 复杂模型（$Q \gg P$）→ KL 大 → 泛化界松
- 这解释了"简单模型泛化好"的信息论本质
</details>
