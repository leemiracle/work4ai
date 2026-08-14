# Berkeley MATH 104 · 习题集（Ross 精选）

> **来源**：Ross *Elementary Analysis* + 自编
> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

## 序列与极限

### Q1 ⭐（ε-N 极限）
用 ε-N 定义证明 $\lim_{n \to \infty} \frac{3n+1}{n+2} = 3$。

<details><summary>解</summary>
$\left|\frac{3n+1}{n+2} - 3\right| = \frac{5}{n+2} < \frac{5}{n}$。取 $N = 5/\epsilon$，则 $n > N \Rightarrow \frac{5}{n+2} < \epsilon$。
</details>

### Q2 ⭐⭐（单调收敛）
设 $s_1 = 1$, $s_{n+1} = \sqrt{2 s_n}$。证明 $s_n$ 收敛并求极限。

<details><summary>解</summary>
归纳法证 $s_n \leq 2$：$s_1 = 1 \leq 2$；$s_{n+1} = \sqrt{2s_n} \leq \sqrt{4} = 2$。
递增：$s_{n+1}^2 = 2s_n \geq s_n \cdot s_n$（当 $s_n \leq 2$）→ $s_{n+1} \geq s_n$。
由单调收敛定理收敛。极限 $L$：$L = \sqrt{2L} \Rightarrow L^2 = 2L \Rightarrow L = 2$。

**ML 关联**：迭代不动点 = 梯度下降的收敛点。
</details>

## 连续性

### Q3 ⭐⭐⭐（开放：sigmoid 的 ε-δ）
用 ε-δ 证明 $\sigma(x) = \frac{1}{1+e^{-x}}$ 在 $\mathbb{R}$ 上连续，并估计在 $x=0$ 处的 δ(ε)。

<details><summary>解</summary>
$|\sigma(x) - \sigma(0)| = |\sigma(x) - 1/2|$。$\sigma'(0) = 1/4$。当 $|x| < 1$：$|\sigma'(x)| \leq \sigma(0)(1-\sigma(0)) + \text{误差} \leq 1/4 + \delta$。取 $\delta = \min(1, 4\epsilon)$。由 MVT：$|\sigma(x)-1/2| \leq |x|/4 \leq \delta/4 \leq \epsilon$。

**ML 关联**：sigmoid 的导数 $\sigma(1-\sigma)$ 最大值 1/4 决定了梯度消失的速率。
</details>

## 微分

### Q4 ⭐（Taylor 展开）
求 $e^x$ 在 $x=0$ 的 3 阶 Taylor 多项式。

<details><summary>解</summary>
$P_3(x) = 1 + x + x^2/2 + x^3/6$。余项 $R_3 = e^c x^4/24$。
</details>

### Q5 ⭐⭐（MVT）
证明 $e^x \geq 1 + x$ for all $x$。

<details><summary>解</summary>
$f(x) = e^x - 1 - x$，$f(0) = 0$。$f'(x) = e^x - 1$。
- $x > 0$: $f'(x) > 0 \Rightarrow f$ 递增 $\Rightarrow f(x) \geq f(0) = 0$。
- $x < 0$: $f'(x) < 0 \Rightarrow f$ 递减 $\Rightarrow f(x) \geq f(0) = 0$。
所以 $e^x \geq 1 + x$。

**ML 关联**：这是 ELBO（证据下界）不等式的基础。
</details>

## 积分

### Q6 ⭐（Riemann 可积）
计算 $\int_0^1 x^2 \, dx$ 用 Darboux 和的定义。

<details><summary>解</summary>
分割 $n$ 等分，$\Delta x = 1/n$。上和 $U = \sum (k/n)^2 \cdot 1/n = \frac{n(n+1)(2n+1)}{6n^3} \to 1/3$。下和 $L = \sum ((k-1)/n)^2 \cdot 1/n \to 1/3$。所以积分 $= 1/3$。
</details>

## 综合

### Q7 ⭐⭐⭐（一致收敛与神经网络）
$f_n(x) = \sigma(nx)$（$\sigma$ = sigmoid）。$f_n$ 逐点收敛到什么函数？一致收敛吗？

<details><summary>解</summary>
逐点：$x > 0 \Rightarrow nx \to \infty \Rightarrow \sigma(nx) \to 1$。$x < 0 \Rightarrow \to 0$。$x = 0 \Rightarrow 1/2$。
极限 $f(x) = \begin{cases} 1 & x > 0 \\ 1/2 & x = 0 \\ 0 & x < 0 \end{cases}$（Heaviside 函数变体）。

$f_n$ 连续但 $f$ 不连续 → **不一致收敛**。

**ML 关联**：$\sigma(nx)$ 就是"温度" $T = 1/n$ 的 sigmoid——温度趋零时变成硬阶跃。这就是知识蒸馏中温度参数的数学本质。
</details>
