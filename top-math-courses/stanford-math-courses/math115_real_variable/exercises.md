# Stanford MATH 115 · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（Dedekind 切）
用 Dedekind 切描述 $\sqrt{3}$。

<details><summary>解</summary>
$A = \{q \in \mathbb{Q} : q < 0 \text{ 或 } q^2 < 3\}$, $B = \{q \in \mathbb{Q} : q > 0, q^2 \geq 3\}$。切 $(A,B)$ 定义 $\sqrt{3}$。
</details>

### Q2 ⭐⭐（紧致性）
$f(x) = x^2 e^{-x}$ 在 $[0, \infty)$ 上有最大值吗？用极值定理分析。

<details><summary>解</summary>
$[0,\infty)$ 非紧致 → 极值定理不直接适用。但 $f \to 0$ as $x \to \infty$，所以存在 $M$ 使 $f(x) < f(1)$ for $x > M$。在 $[0, M]$ 上（紧致）应用极值定理。$f'(x) = e^{-x}(2x - x^2) = 0 \Rightarrow x = 2$。$f(2) = 4e^{-2} \approx 0.54$。最大值存在。

**ML 关联**：正则化让 loss 在无穷远处衰减 → 等效紧致化 → 极值存在。
</details>

### Q3 ⭐⭐⭐（开放：激活函数展开）
用 Taylor 定理估计 tanh(x) 在 $x = 0$ 附近的线性近似的有效范围。

<details><summary>解</summary>
$\tanh(x) \approx x - x^3/3 + \cdots$。线性近似 $\tanh(x) \approx x$，误差 $\approx x^3/3$。要求误差 $< \epsilon$: $|x| < (3\epsilon)^{1/3}$。

对 $\epsilon = 0.01$: $|x| < 0.31$。这就是为什么 tanh 在 $|x| > 1$ 时饱和——线性近似失效。

**ML 关联**：tanh 饱和导致梯度消失——Taylor 分析揭示了"为什么"。
</details>

### Q4 ⭐（级数收敛）
$\sum \frac{1}{n(\ln n)^2}$ 收敛吗？

<details><summary>解</summary>
积分判别法：$\int_2^\infty \frac{1}{x(\ln x)^2} dx = \left[-\frac{1}{\ln x}\right]_2^\infty = \frac{1}{\ln 2}$。收敛。
</details>

### Q5 ⭐⭐（一致连续）
$f(x) = \sin(1/x)$ 在 $(0, 1]$ 上一致连续吗？

<details><summary>解</summary>
不一致连续。取 $x_n = 1/(2n\pi)$, $y_n = 1/(2n\pi + \pi/2)$。$|x_n - y_n| \to 0$ 但 $|f(x_n) - f(y_n)| = |0 - 1| = 1 \not\to 0$。

**ML 关联**：高频振荡函数不稳定 → 需要平滑正则化。
</details>
