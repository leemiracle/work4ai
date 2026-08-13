# UT Austin M 381C · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（σ-代数）
证明 $\mathcal{M} = \{E \subset \mathbb{N} : E \text{ 或 } E^c \text{ 有限}\}$ 是 $\mathbb{N}$ 上的 σ-代数。

<details><summary>解</summary>
1. $\emptyset \in \mathcal{M}$ ($\emptyset$ 有限) ✓
2. $E \in \mathcal{M} \Rightarrow E^c \in \mathcal{M}$: 若 $E$ 有限则 $E^c$ 余有限, 反之亦然 ✓
3. $E_n \in \mathcal{M} \Rightarrow \bigcup E_n \in \mathcal{M}$:
   - 若所有 $E_n$ 有限: $\bigcup E_n$ 可数（可能无限）→ 需分情况
   - 若某 $E_k$ 余有限: $(\bigcup E_n)^c \subset E_k^c$ 有限 → $\bigcup E_n$ 余有限 ✓
   - 若所有 $E_n$ 有限: $\bigcup E_n$ 可数 → 若有限则 ∈ $\mathcal{M}$; 若无限则余集可数... 需要重新验证

实际上这是 **cofinite σ-代数**，$E$ 或 $E^c$ 有限 → 不满足可数并（如 $\{1\}, \{2\}, \{3\}, ...$ 的并 $= \mathbb{N}$，每个有限，但 $\mathbb{N}^c = \emptyset$ 有限 ✓ → $\mathbb{N} \in \mathcal{M}$ ✓）。
</details>

### Q2 ⭐⭐（DCT 应用）
$f_n(x) = (1 + x/n)^n$ on $[0, 1]$。$\lim \int_0^1 f_n = ?$

<details><summary>解</summary>
$f_n \to e^x$ 逐点。

**控制**: $(1+x/n)^n \leq e^x \leq e$ for $x \in [0,1], n \geq 1$（利用 $\ln(1+t) \leq t$）。

所以 $|f_n| \leq e \in L^1[0,1]$ ✓

**DCT**: $\lim \int_0^1 f_n = \int_0^1 e^x \, dx = e - 1$。
</details>

### Q3 ⭐⭐（$L^p$ 空间）
证明 $L^2([0,1]) \subset L^1([0,1])$ 但 $L^1 \not\subset L^2$。

<details><summary>解</summary>
**$L^2 \subset L^1$**: $\|f\|_1 = \int |f| \cdot 1 \leq \|f\|_2 \cdot \|1\|_2 = \|f\|_2 \cdot 1$ (Hölder/Cauchy-Schwarz)。所以 $\|f\|_1 \leq \|f\|_2 < \infty$。

**$L^1 \not\subset L^2$**: $f(x) = x^{-1/2}$ on $(0,1]$。$\int_0^1 x^{-1/2} = 2 < \infty$ ($L^1$)。但 $\int_0^1 x^{-1} = \infty$ ($\notin L^2$)。

**ML 关联**: $L^2$ = 有限方差 → 比 $L^1$ (有限期望) 更强。
</details>

### Q4 ⭐⭐⭐（开放：DCT 与 SGD）
解释为什么 DCT 是 mini-batch SGD 中"梯度换序"合法的数学基础。

<details><summary>解</summary>
**SGD**: $\hat{g}_n = \frac{1}{B} \sum_{i \in \text{batch}} \nabla \ell(\theta; z_i)$ → $\nabla L(\theta) = E_z[\nabla \ell(\theta; z)]$（$B \to \infty$）

**大数定律**: $\hat{g}_n \to \nabla L$ a.s. ($B \to \infty$)

**换序问题**: 我们需要 $\int \hat{g}_n \, d\theta \to \int \nabla L \, d\theta$ —— 这是积分和极限的换序。

**DCT 的角色**:
- 若 $|\hat{g}_n(\theta)| \leq G(\theta) \in L^1(d\theta)$（梯度有界）
- 且 $\hat{g}_n \to \nabla L$ a.e.
- 则 DCT 保证: $\lim \int \hat{g}_n \, d\theta = \int \nabla L \, d\theta$ ✓

**实际**: 梯度裁剪 (gradient clipping) = 强制满足 DCT 条件 $|\hat{g}_n| \leq G$。

**深层**: DCT 是 SGD 收敛证明的分析基础——没有 DCT，梯度换序不合法。
</details>

### Q5 ⭐⭐（Radon-Nikodym）
$X \sim N(0, 1)$, $Y = X + \theta$ ($Y \sim N(\theta, 1)$)。求 $dP_Y / dP_X$。

<details><summary>解</summary>
$P_X$ 和 $P_Y$ 都绝对连续 w.r.t. Lebesgue 测度 → $\nu \ll \mu$ → RN 导数存在。

$$\frac{dP_Y}{dP_X}(x) = \frac{p_Y(x)}{p_X(x)} = \frac{\frac{1}{\sqrt{2\pi}} e^{-(x-\theta)^2/2}}{\frac{1}{\sqrt{2\pi}} e^{-x^2/2}} = e^{-(x-\theta)^2/2 + x^2/2} = e^{\theta x - \theta^2/2}$$

**ML 应用**: 这就是**Neyman-Pearson 引理**的基础——似然比检验 $\frac{p_Y}{p_X}$。

**变分推断**: $\text{KL}(P_Y \| P_X) = \int \log \frac{dP_Y}{dP_X} dP_Y = E_Y[\theta X - \theta^2/2] = \theta^2/2$。

**KL = $\theta^2/2$**: 这就是高斯分布间 KL 散度的经典结果！
</details>

### Q6 ⭐⭐⭐（开放：4 种收敛与深度学习）
构造 $f_n \to 0$ 依概率但 $f_n \not\to 0$ a.s. 的例子，并解释这在 SGD 中的含义。

<details><summary>解</summary>
**构造（滑动区间）**: 将 $[0,1]$ 分成越来越细的段：
- $f_1 = \mathbf{1}_{[0,1]}$
- $f_2 = \mathbf{1}_{[0,1/2]}$, $f_3 = \mathbf{1}_{[1/2,1]}$
- $f_4 = \mathbf{1}_{[0,1/3]}$, $f_5 = \mathbf{1}_{[1/3,2/3]}$, $f_6 = \mathbf{1}_{[2/3,1]}$
- ...

每个 $x$ 被无穷多区间覆盖 → $f_n(x) = 1$ 无穷多次 → 不 a.s. 收敛。

但 $\mu(\{f_n > \epsilon\}) = \text{区间宽度} \to 0$ → 依概率收敛。

**SGD 含义**:
- **依概率收敛**: $P(|\hat{g}_n - \nabla L| > \epsilon) \to 0$ —— 大多数情况下梯度估计好
- **a.s. 收敛**: 对**每个**训练步, $\hat{g}_n \to \nabla L$ —— 更强保证
- 实践中 SGD 只依概率收敛 → 梯度估计偶尔很差（滑动区间效应）→ 需要 variance reduction (SGD + momentum, Adam)

**深层**: a.s. vs 依概率的差距 = 理论与实践的差距 → variance reduction 技术的动机。
</details>
