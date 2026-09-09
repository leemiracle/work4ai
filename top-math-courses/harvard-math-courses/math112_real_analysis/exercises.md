# Harvard Math 112 · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（度量空间）
证明 $(\mathbb{R}^2, d_\infty)$ 其中 $d_\infty(x,y) = \max(|x_1-y_1|, |x_2-y_2|)$ 是度量空间。

<details><summary>解</summary>
三条公理直接验证。三角不等式：$d_\infty(x,z) = \max_i |x_i-z_i| \leq \max_i(|x_i-y_i|+|y_i-z_i|) \leq d_\infty(x,y) + d_\infty(y,z)$。
</details>

### Q2 ⭐⭐（紧致性）
$S = \{(x,y) \in \mathbb{R}^2 : x^2 + y^2 \leq 1\}$（单位圆盘）是紧致的。

<details><summary>解</summary>
有界（$\|x\| \leq 1$）+ 闭（$x^2+y^2 \leq 1$ 定义闭集）。由 Heine-Borel → 紧致。

**ML 关联**：权重衰减 $\|\theta\| \leq R$ = 紧致集 → loss 最小值存在。
</details>

### Q3 ⭐⭐⭐（开放：ReLU 分析）
用 ε-δ 证明 ReLU 连续但不可微。为什么 PyTorch autograd 仍有效？

<details><summary>解</summary>
**连续**: $|\max(0,x) - 0| \leq |x|$。取 $\delta = \epsilon$。
**不可微**: 左导数 0 ≠ 右导数 1。
**PyTorch**: autograd 使用次梯度约定 $\text{ReLU}'(0) = 0$（工程选择）。ReLU a.e. 可微（除 $x=0$），反向传播在实践中有效。

**深层**: 深度学习只需 a.e. 可微 → 容许 kink。
</details>

### Q4 ⭐⭐（一致收敛）
$f_n(x) = x^n(1-x^n)$ 在 $[0,1]$ 上一致收敛到 0 吗？

<details><summary>解</summary>
$f_n \to 0$ 逐点。$\sup|f_n|$：$f_n'(x) = nx^{n-1}(1-2x^n) = 0 \Rightarrow x^n = 1/2 \Rightarrow x = (1/2)^{1/n}$。$f_n(x^*) = (1/2)(1-1/2) = 1/4 \not\to 0$。所以**不一致收敛**。

**ML 关联**：训练集拟合好 ≠ 泛化好（逐点 ≠ 一致）。
</details>

### Q5 ⭐（Cauchy 列）
$s_n = \sum_{k=1}^n (-1)^k / k$ 是 Cauchy 列吗？

<details><summary>解</summary>
交错级数收敛（Leibniz 判别法）→ 收敛 → Cauchy（$\mathbb{R}$ 完备）。
</details>

### Q6 ⭐⭐（Arzelà-Ascoli）
$\{f_n(x) = \sin(nx)/n\}$ 在 $[0, 2\pi]$ 上有收敛子序列吗？

<details><summary>解</summary>
1. 一致有界：$|f_n| \leq 1/n \leq 1$ ✓
2. 等度连续：$|f_n'| = |\cos(nx)| \leq 1$ → Lipschitz 1 → 等度连续 ✓
由 Arzelà-Ascoli → 有一致收敛子序列。极限 $f = 0$（$f_n \rightrightarrows 0$ 因为 $\sup = 1/n \to 0$）。

**ML 关联**：这就是 NTK 理论中函数族紧致性的来源。
</details>
