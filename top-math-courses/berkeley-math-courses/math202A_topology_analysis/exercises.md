# Berkeley MATH 202A · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（拓扑空间）
证明紧致集的闭子集是紧致的。

<details><summary>解</summary>
$F \subset K$ 闭，$K$ 紧致。$\{G_\alpha\}$ 覆盖 $F$。$\{G_\alpha\} \cup \{F^c\}$ 覆盖 $K$。$K$ 紧致 → 有限子覆盖。去掉 $F^c$（如果出现），仍覆盖 $F$。
</details>

### Q2 ⭐⭐（Banach 空间）
证明 $L^2([0,1])$ 是 Hilbert 空间（完备 + 内积）。

<details><summary>解</summary>
**内积**: $\langle f, g \rangle = \int_0^1 f\bar{g} \, dm$。正定性、共轭对称、双线性直接验证。
**完备性**: $L^2$ 是 $L^p$ 的特例，完备性证明同 $L^1$（取子列 + Fatou 引理 + MCT）。
</details>

### Q3 ⭐⭐⭐（开放：RKHS 与核方法）
证明高斯核 $k(x,y) = e^{-\|x-y\|^2/(2\sigma^2)}$ 是正定的，并解释由此定义的 RKHS 如何用于 SVM。

<details><summary>解（思路）</summary>
**正定性**：$\sum_{ij} c_i c_j k(x_i, x_j) = \sum_{ij} c_i c_j e^{-\|x_i-x_j\|^2/(2\sigma^2)}$。
利用 Fourier 变换：$e^{-\|x\|^2/(2\sigma^2)} = \int e^{i\xi \cdot x} e^{-\sigma^2\|\xi\|^2/2} \frac{d\xi}{(2\pi)^d}$。
所以 $\sum c_i c_j k(x_i, x_j) = \int \left|\sum c_i e^{i\xi \cdot x_i}\right|^2 e^{-\sigma^2\|\xi\|^2/2} d\xi \geq 0$。正定 ✓。

**SVM**: 在 RKHS $\mathcal{H}$ 中 $\min \|w\|_\mathcal{H}^2$ s.t. $y_i\langle w, k(x_i,\cdot)\rangle \geq 1$。核技巧避免显式计算 $\phi(x)$。

**连接**: Math 202A 的 Riesz 表示定理保证了 $w$ 的存在。
</details>

### Q4 ⭐⭐（压缩映射）
在 Banach 空间 $C([0,1])$ 中，$T(f)(x) = \int_0^x f(t) \, dt$。$\|T^n\| \leq 1/n!$。证明 $I - T$ 可逆。

<details><summary>解</summary>
$\|T^n\| \leq 1/n! \to 0$。Neumann 级数 $(I-T)^{-1} = \sum_{n=0}^\infty T^n$ 收敛（因为 $\sum \|T^n\| \leq \sum 1/n! = e < \infty$）。

**ML 关联**：这就是梯度下降中 $(I - \eta H)^{-1}$ 可逆的理论基础（$H$ = Hessian）。
</details>

### Q5 ⭐⭐（DCT 应用）
$f_n(x) = n^2 x e^{-nx}$ on $[0,\infty)$。$\lim \int f_n = ?$

<details><summary>解</summary>
$f_n \to 0$ 逐点。但 $\sup f_n = f_n(1/n) = n/e \to \infty$（不有界），DCT 不能直接用。

积分：$\int_0^\infty n^2 x e^{-nx} dx = n^2 / n^2 = 1$（换元 $u = nx$）。所以 $\int f_n = 1 \not\to 0$。

**教训**：逐点 $\to 0$ + 积分不 $\to 0$ → DCT 不适用（缺少控制函数 $g$）。
</details>

### Q6 ⭐⭐⭐（开放：4 种收敛模式）
构造 $X_n \to 0$ 依概率但 $X_n \not\to 0$ a.s. 的例子，并用数值模拟验证。

<details><summary>解</summary>
**滑动区间**：$X_n = \mathbf{1}_{[k/2^m, (k+1)/2^m]}$，$n = 2^m + k$。$P(X_n > \epsilon) = 1/2^m \to 0$（依概率）。但每个 $x$ 被无穷多区间覆盖 → $X_n(x)$ 有无穷个 1 → 不 a.s. 收敛。

**ML 关联**：SGD 中 loss 依概率下降 ≠ 每次都下降——方差减少技术的动机。
</details>
