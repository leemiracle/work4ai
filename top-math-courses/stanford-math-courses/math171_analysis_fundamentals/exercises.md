# Stanford MATH 171 · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（压缩映射）
$T(x) = \frac{1}{2}(x + \frac{2}{x})$（Newton 法求 $\sqrt{2}$）。证明 $T$ 在 $[\sqrt{2}, \infty)$ 上是压缩映射。

<details><summary>解</summary>
$T'(x) = \frac{1}{2}(1 - 2/x^2)$。当 $x \geq \sqrt{2}$: $0 \leq T'(x) \leq 1/2$。由 MVT: $|T(x)-T(y)| \leq \frac{1}{2}|x-y|$。压缩 $q = 1/2 < 1$。不动点 $x^* = \sqrt{2}$。

**ML 关联**：这就是 Newton 法收敛的数学本质——压缩映射 → 不动点。
</details>

### Q2 ⭐⭐（Arzelà-Ascoli）
证明 $\{f \in C([0,1]) : \|f\|_\infty \leq 1, \|f'\|_\infty \leq L\}$ 在一致拓扑下紧致。

<details><summary>解</summary>
1. **一致有界**: $\|f\|_\infty \leq 1$ ✓
2. **等度连续**: $|f(x)-f(y)| \leq L|x-y|$ → 取 $\delta = \epsilon/L$ 对所有 $f$ 成立 ✓
3. $[0,1]$ 紧致 ✓
由 Arzelà-Ascoli：有收敛子序列 → 闭包紧致。

**ML 关联**：泛化界中覆盖数 $\mathcal{N}(\epsilon, \mathcal{F}) \leq (1+2/\epsilon)^{d}$ 就来自这里。
</details>

### Q3 ⭐⭐⭐（开放：Stone-Weierstrass → UAT）
用 Stone-Weierstrass 解释为什么单隐层网络可以逼近任何连续函数。

<details><summary>解</summary>
**Stone-Weierstrass**：代数 $\mathcal{A}$ 分离点 + 含常数 → 稠密。

**神经网络族** $\mathcal{F} = \{\sum_{i=1}^m \alpha_i \sigma(w_i^T x + b_i)\}$：
1. 含常数（$m=0$ 或 $w_i = 0$）✓
2. 分离点：取 $\sigma = \text{sigmoid}$，$\sigma(w^T x + b)$ 可以区分任意两点 ✓
3. 对加法封闭：两个网络的和还是网络（$m$ 翻倍）✓
4. 对数乘封闭 ✓

所以 $\mathcal{F}$ 在 $C(K)$ 中稠密 → **Universal Approximation**。

**注意**：Stone-Weierstrass 只保证**存在性**，不保证**可学习性**——深度学习是可学习的（梯度下降有效）。
</details>

### Q4 ⭐⭐（反函数定理）
$f(x, y) = (e^x \cos y, e^x \sin y)$。在哪里 $f$ 可逆？逆函数是什么？

<details><summary>解</summary>
Jacobian: $J = \begin{pmatrix} e^x \cos y & -e^x \sin y \\ e^x \sin y & e^x \cos y \end{pmatrix}$, $\det J = e^{2x} \neq 0$。所以处处局部可逆。

逆：$(u, v) \mapsto (\frac{1}{2}\ln(u^2+v^2), \arctan(v/u))$ = $(\ln r, \theta)$（极坐标变换）。

**ML 关联**：这就是 Normalizing Flow 的基础——可逆变换的 Jacobian 行列式用于密度变换。
</details>

### Q5 ⭐⭐（一致收敛）
$\sum_{n=1}^\infty \frac{\sin(nx)}{n^2}$ 在 $\mathbb{R}$ 上一致收敛吗？

<details><summary>解</summary>
Weierstrass M-判别法：$|\sin(nx)/n^2| \leq 1/n^2$，$\sum 1/n^2$ 收敛 → 一致收敛。

极限函数连续（一致收敛保持连续性）。

**ML 关联**：一致收敛保证 Fourier 级数收敛到连续函数——信号处理的基础。
</details>

### Q6 ⭐⭐⭐（开放：覆盖数与泛化）
解释 Arzelà-Ascoli 如何推导 Rademacher 复杂度界。

<details><summary>解（思路）</summary>
1. Lipschitz $L$ 的函数族 $\mathcal{F}$ 在 $C([0,1]^d)$ 中等度连续 + 有界 → Arzelà-Ascoli → 紧致。
2. 紧致集的 **$\epsilon$-覆盖数** $\mathcal{N}(\epsilon, \mathcal{F})$ 有限。
3. 由** Dudley 熵积分**：Rademacher 复杂度 $\mathfrak{R}_n(\mathcal{F}) \leq C \int_0^\infty \sqrt{\log \mathcal{N}(\epsilon, \mathcal{F})/n} \, d\epsilon$。
4. 对 VC 维 $d$ 的类：$\mathcal{N} \leq (en/d)^d$ → $\mathfrak{R}_n \leq O(\sqrt{d/n})$。

**ML 关联**：这就是泛化界 $O(\sqrt{d/n})$ 的推导——Arzelà-Ascoli 是起点。
</details>
