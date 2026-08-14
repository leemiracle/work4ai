# Oxford Part B B8.1 · 习题集（Williams + 鞅 + 泛化界 + 扩散预览）

---

## 基础题

### Q1.1（收敛模式蕴含关系）
证明 a.s. 收敛蕴含依概率收敛。给出一个依概率收敛但非 a.s. 收敛的例子。

<details><summary>解</summary>

$a.s. \Rightarrow P$：$X_n \xrightarrow{a.s.} X$ 意味着 $\forall\epsilon>0$，$P(\sup_{m\geq n}|X_m-X|>\epsilon)\to 0$，故 $P(|X_n-X|>\epsilon)\to 0$。

**反例（滑移序列）**：$\Omega=[0,1]$，$X_n = \mathbf{1}_{[k/2^m,(k+1)/2^m]}$，$n=2^m+k$。每个 $\omega$ 被无穷多次覆盖（$X_n=1$ 无穷多次），但 $P(X_n=1)=1/2^m\to 0$。故 $X_n\xrightarrow{P}0$ 但不 a.s. 收敛。

**ML 关联**：SGD 的 a.s. 收敛比依概率收敛更强。
</details>

### Q1.2（可选停时）
$S_n$ 为对称随机游走，$\tau=\inf\{n:S_n=\pm a\}$。用鞅 $S_n^2-n$ 证明 $E[\tau]=a^2$。

<details><summary>解</summary>

$M_n = S_n^2-n$ 是鞅。验证条件：

1. $\tau<\infty$ a.s.（对称游走在 $\mathbb{Z}$ 上常返）
2. $E[\tau]<\infty$（可证）
3. $|M_{n\wedge\tau}|\leq a^2$（有界，满足可选停时条件）

由可选停时：$E[M_\tau]=E[M_0]=0$

$E[S_\tau^2-\tau]=0 \Rightarrow a^2-E[\tau]=0 \Rightarrow E[\tau]=a^2$ ✓

**ML 关联**：RL 中到达目标的期望步数。
</details>

---

## 中等题

### Q2.1（Hoeffding → PAC 泛化界）★
假设类 $\mathcal{H}$ 有限。用 Hoeffding + union bound 推导 PAC 泛化界。

<details><summary>解</summary>

对每个 $h$：$P(|\hat{R}(h)-R(h)|>\epsilon)\leq 2e^{-2n\epsilon^2}$（Hoeffding）

Union bound：

$P(\exists h\in\mathcal{H}: |\hat{R}(h)-R(h)|>\epsilon)\leq 2|\mathcal{H}|e^{-2n\epsilon^2}$

令 $=\delta$：

$$\epsilon = \sqrt{\frac{\ln(2|\mathcal{H}|/\delta)}{2n}}$$

即以 $\geq 1-\delta$ 概率：$R(h^*)\leq\hat{R}(h^*)+\sqrt{\frac{\ln(2|\mathcal{H}|/\delta)}{2n}}$

**ML 关联**：这就是有限假设类下的 PAC 泛化保证。
</details>

### Q2.2（条件期望 = $L^2$ 投影）
证明 $E[Y|\mathcal{G}]$ 是 $Y$ 到 $\mathcal{G}$-可测 $L^2$ 函数空间的正交投影。

<details><summary>解</summary>

设 $Z = E[Y|\mathcal{G}]$，$W$ 是任意 $\mathcal{G}$-可测函数。

$E[(Y-Z)W] = E[E[(Y-Z)W|\mathcal{G}]] = E[W\cdot E[Y-Z|\mathcal{G}]] = E[W\cdot 0] = 0$

（$W$ 是 $\mathcal{G}$-可测，可提出条件期望；$Z=E[Y|\mathcal{G}]$ 消去。）

故 $Y-Z \perp$ 所有 $\mathcal{G}$-可测函数 → $Z$ 是正交投影。✓

**ML 关联**：回归 $E[Y|X]$ = 最小均方误差预测。
</details>

### Q2.3（似然比鞅）
$X_1,X_2,\ldots$ i.i.d.，$H_0$: 密度 $p$，$H_1$: 密度 $q$。证明似然比 $L_n=\prod_{i=1}^n q(X_i)/p(X_i)$ 在 $H_0$ 下是鞅。

<details><summary>解</summary>

$E_0[L_{n+1}|\mathcal{F}_n] = L_n \cdot E_0\left[\frac{q(X_{n+1})}{p(X_{n+1})}\right] = L_n \cdot \int\frac{q(x)}{p(x)}p(x)\,dx = L_n \cdot 1 = L_n$

故 $L_n$ 在 $H_0$ 下是鞅。✓

**ML 关联**：序贯假设检验 / SPRT（序贯概率比检验）。
</details>

---

## 开放题

### Q3.1（McDiarmid 不等式 → 随机算法稳定性）★
设 $f(X_1,\ldots,X_n)$ 满足有界差分条件：改变单个 $X_i$，$f$ 变化 $\leq c_i$。证明 McDiarmid 不等式并解释其在 ML 中的应用。

<details><summary>解（思路）</summary>

**McDiarmid 不等式**：

$$P(|f-Ef|\geq t)\leq 2\exp\left(-\frac{2t^2}{\sum c_i^2}\right)$$

**证明**：构造 Doob 鞅 $Z_k = E[f|\mathcal{F}_k]$，鞅差 $|Z_k-Z_{k-1}|\leq c_k$，应用 Azuma-Hoeffding。

**ML 应用**：
- 学习算法的算法稳定性 → 泛化
- 随机化算法的集中性
- 超参数搜索的置信区间

**ML 关联**：bounded differences 假设 → 算法稳定性 → 泛化保证。
</details>

### Q3.2（鞅与联机学习 regret bound）★
联机学习算法的 regret $R_n$ 用 Azuma-Hoeffding 推导高概率上界。

<details><summary>解（思路）</summary>

Regret $R_n = \sum_{t=1}^n \ell_t(a_t) - \min_a\sum_{t=1}^n\ell_t(a)$

在适当条件下（如 Hedge/EXP3），$E[R_n]\leq O(\sqrt{n\ln K})$

超额 regret 是鞅差序列 → Azuma-Hoeffding：

$P(R_n \geq E[R_n]+t)\leq e^{-t^2/(2n)}$

高概率 regret：$R_n\leq O(\sqrt{n\ln K})+O(\sqrt{n\ln(1/\delta)})$ w.p. $\geq 1-\delta$

**ML 关联**：Multi-armed bandit / EXP3 / Hedge 的 regret 保证。
</details>

### Q-Final（Brownian 运动与 Itô 引理 → 扩散模型预览）★
设 $W_t$ 是 Brownian 运动。用 Itô 引理推导 $d(W_t^2)$，并解释为什么 $W_t^2-t$ 是鞅。简要说明这在扩散模型中的角色。

<details><summary>解（思路）</summary>

$f(x)=x^2$，$f'(x)=2x$，$f''(x)=2$。

Itô 引理：$d(W_t^2) = 2W_t\,dW_t + \frac{1}{2}\cdot 2\,dt = 2W_t\,dW_t + dt$

$W_t^2 = 2\int_0^t W_s\,dW_s + t$

$W_t^2 - t = 2\int_0^t W_s\,dW_s$（Itô 积分是鞅）→ $W_t^2-t$ 是鞅 ✓

**扩散模型关联**：前向 SDE $dX_t = -\frac{1}{2}\beta_t X_t\,dt + \sqrt{\beta_t}\,dW_t$ 中 $dW_t$ 项就是 Brownian 运动驱动。反向 SDE 的推导需要 Girsanov 定理（测度变换 = Radon-Nikodym 导数）。

→ 扩散模型生成 = 求解反向 SDE，用 score matching 估计 $\nabla\log p_t$。

**ML 关联**：B8.1 的鞅 + 测度变换为 Part C SDE 打基础。
</details>
