# Cambridge Part IA Analysis I · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（序列收敛）
$s_n = (1 + 1/n)^n$ 收敛吗？极限是什么？

<details><summary>解</summary>
$s_n \to e$。可以证明 $s_n$ 单调递增有上界（$s_n < 3$）→ 单调收敛定理 → 收敛。

取对数: $\ln s_n = n \ln(1+1/n) = n(1/n - 1/(2n^2) + ...) = 1 - 1/(2n) + ... \to 1$。所以 $s_n \to e^1 = e$。
</details>

### Q2 ⭐⭐（中值定理）
$f(x) = x^3 - x + 1$。证明在 $[-2, -1]$ 中有根。

<details><summary>解</summary>
$f(-2) = -8+2+1 = -5 < 0$, $f(-1) = -1+1+1 = 1 > 0$。由 **IVT**（$f$ 连续），$\exists c \in (-2,-1): f(c) = 0$。

**ML 关联**: 这就是梯度下降找零点的连续函数版——loss 从正变负保证有根。
</details>

### Q3 ⭐⭐（Riemann 积分）
Dirichlet 函数 $\mathbf{1}_\mathbb{Q}(x)$ 在 $[0,1]$ 上 Riemann 可积吗？

<details><summary>解</summary>
**不可积**。任何分割中，每个小区间既有有理点（$f=1$）又有无理点（$f=0$）→ 上和 = 1，下和 = 0 → $\overline{S} - \underline{S} = 1 \neq 0$。

但 **Lebesgue 可积**（$a.e.$ 连续 → 可积，$\mathbf{1}_\mathbb{Q}$ a.e. = 0）。

**ML 关联**: 这正是需要 Lebesgue 积分的动机——更广的函数类可积。
</details>

### Q4 ⭐⭐（Taylor 展开）
$e^x = \sum_{k=0}^\infty x^k/k!$。用 Taylor 余项证明对一切 $x$ 收敛。

<details><summary>解</summary>
$R_n(x) = \frac{e^c}{(n+1)!} x^{n+1}$ for some $c$ between 0 and $x$。

$|R_n(x)| \leq \frac{e^{|x|}}{(n+1)!} |x|^{n+1} \to 0$（$n!$ 增长比任何指数快）。

所以 $e^x = \sum x^k/k!$ 对一切 $x$ 收敛 ✓。

**ML 关联**: softmax = 归一化的 $e^x$ → 数值稳定性需要理解指数的级数行为。
</details>

### Q5 ⭐⭐⭐（开放：ε-δ 与数值稳定性）
用 ε-δ 分析解释为什么 $\log(1 + e^x)$（softplus）比 $\max(0, x)$（ReLU）数值更稳定。

<details><summary>解</summary>
**Softplus** $f(x) = \log(1+e^x)$: 处处光滑可微，$f'(x) = \sigma(x) = \frac{e^x}{1+e^x}$。
- 当 $x$ 很大: $f(x) \approx x + e^{-x}$（需用恒等式 $f(x) = x + \log(1+e^{-x})$ 避免溢出）
- 当 $x$ 很小: $f(x) \approx e^x$

**ReLU** $g(x) = \max(0,x)$: 在 $x=0$ 不可微，但处处 Lipschitz 1。

**ε-δ 分析**:
- Softplus 连续可微 → 反向传播梯度处处有界 → 数值稳定
- ReLU 在 $x=0$ 处梯度定义不唯一 → 需要工程约定（PyTorch 选 $\text{ReLU}'(0) = 0$）

**深层**: 连续可微（$C^1$）保证优化轨迹光滑；ReLU 的 kink 在实践中影响小但理论上不完美。
</details>

### Q6 ⭐⭐（级数收敛）
$\sum_{n=2}^\infty \frac{1}{n(\ln n)^2}$ 收敛吗？

<details><summary>解</summary>
**积分判别法**: $\int_2^\infty \frac{1}{x(\ln x)^2} dx = \left[-\frac{1}{\ln x}\right]_2^\infty = \frac{1}{\ln 2} < \infty$ → 收敛 ✓。

**对比**: $\sum \frac{1}{n \ln n}$ 发散（积分 $\ln \ln x \to \infty$）。
</details>
