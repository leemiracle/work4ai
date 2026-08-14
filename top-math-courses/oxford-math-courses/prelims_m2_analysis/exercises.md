# Oxford Prelims M2 · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（上确界）
$S = \{x \in \mathbb{Q} : x^2 < 2\}$。$\sup S = ?$ （在 $\mathbb{R}$ 中）

<details><summary>解</summary>
$\sup S = \sqrt{2} \approx 1.41421...$

证明: (1) $\sqrt{2}$ 是上界（$x^2 < 2 \Rightarrow x < \sqrt{2}$）。(2) $\sqrt{2}$ 是最小上界（$\forall \epsilon > 0$, $\sqrt{2} - \epsilon \in S$, 因为 $(\sqrt{2}-\epsilon)^2 < 2$）。

**注意**: $\sqrt{2} \notin \mathbb{Q}$！$\sup S$ 在 $\mathbb{Q}$ 中**不存在**——这正是需要完备化的原因。
</details>

### Q2 ⭐⭐（MVT 应用）
证明: $|\sin x - \sin y| \leq |x - y|$。

<details><summary>解</summary>
MVT: $\sin x - \sin y = \cos(c)(x-y)$ for some $c$ between $x, y$。
$|\cos c| \leq 1$ → $|\sin x - \sin y| \leq |x-y|$ ✓

**推论**: $\sin$ 是 Lipschitz 1。

**ML 关联**: Lipschitz 连续 → GAN 稳定性的 Lipschitz 约束。
</details>

### Q3 ⭐⭐（级数收敛）
$\sum_{n=1}^\infty \frac{n}{2^n}$ 收敛吗？和是多少？

<details><summary>解</summary>
比值法: $\frac{(n+1)/2^{n+1}}{n/2^n} = \frac{n+1}{2n} \to 1/2 < 1$ → 收敛。

求和: 设 $S = \sum n/2^n = \sum n x^n|_{x=1/2}$。

$\sum_{n=1}^\infty n x^n = x \frac{d}{dx} \sum x^n = x \frac{d}{dx} \frac{x}{1-x} = \frac{x}{(1-x)^2}$

$S = \frac{1/2}{(1-1/2)^2} = \frac{1/2}{1/4} = 2$。

**ML 关联**: 几何级数及其导数 → 期望、折扣因子分析。
</details>

### Q4 ⭐⭐⭐（开放：Taylor → 牛顿法）
用 Taylor 展开解释牛顿法的收敛速率，并与梯度下降对比。

<details><summary>解</summary>
**牛顿法**: $\theta_{k+1} = \theta_k - H^{-1} \nabla L(\theta_k)$

Taylor 展开 $L(\theta + d) \approx L(\theta) + \nabla L^T d + \frac{1}{2} d^T H d$。

最小化关于 $d$: $\nabla L + H d = 0 \Rightarrow d = -H^{-1} \nabla L$ → 牛顿步。

**收敛速率**:
- 牛顿法（二阶）：$|e_{k+1}| \leq C|e_k|^2$ — **二次收敛**
- 梯度下降（一阶）：$|e_{k+1}| \leq q|e_k|$ ($q < 1$) — **线性收敛**

**ML 关联**: 
- 梯度下降: $O(1/k)$ for convex, $O(1/\sqrt{k})$ for non-convex
- 牛顿法: $O(\log \log 1/\epsilon)$ for convex — 快得多但 Hessian 计算 $O(d^3)$
- 实际: Adam / L-BFGS 近似二阶信息
</details>

### Q5 ⭐（Riemann 积分）
$\int_0^1 x^3 \, dx = ?$

<details><summary>解</summary>
$\int_0^1 x^3 \, dx = \left[\frac{x^4}{4}\right]_0^1 = \frac{1}{4}$

**ML 关联**: 期望 $E[X^3]$ for $X \sim U[0,1]$ 就是这个积分。
</details>

### Q6 ⭐⭐⭐（开放：softmax 的级数基础）
用幂级数解释 $e^x$ 的收敛性，并说明为什么 softmax 需要数值稳定技巧。

<details><summary>解</summary>
**幂级数**: $e^x = \sum_{k=0}^\infty x^k / k!$, 收敛半径 $R = \infty$ → 对一切 $x$ 收敛。

但实际计算问题:
1. **大 $x$ 溢出**: $e^{1000} = \infty$ in float64 → 用恒等式 $e^x = e^{x - c} \cdot e^c$
2. **softmax 稳定**: $\text{softmax}(z)_i = \frac{e^{z_i}}{\sum_j e^{z_j}}$

稳定版: $\text{softmax}(z)_i = \frac{e^{z_i - \max(z)}}{\sum_j e^{z_j - \max(z)}}$

分子分母同除 $e^{\max(z)}$ → 结果不变但避免溢出。

**深层**: 幂级数收敛保证理论上有效，但浮点运算有限精度 → 需要代数恒等式重排。
</details>
