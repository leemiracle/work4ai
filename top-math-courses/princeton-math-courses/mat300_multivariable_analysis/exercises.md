# Princeton MAT 300 · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（Jacobian）
$f(x, y) = (x^2 + y^2, xy)$。求 $Df(1, 2)$。

<details><summary>解</summary>
$J = \begin{pmatrix} 2x & 2y \\ y & x \end{pmatrix}$, $Df(1,2) = \begin{pmatrix} 2 & 4 \\ 2 & 1 \end{pmatrix}$, $\det = 2 - 8 = -6 \neq 0$ → 局部可逆。
</details>

### Q2 ⭐⭐（链式法则）
$z = f(x, y)$, $x = g(t)$, $y = h(t)$。求 $dz/dt$。

<details><summary>解</summary>
$\frac{dz}{dt} = \frac{\partial f}{\partial x}\frac{dg}{dt} + \frac{\partial f}{\partial y}\frac{dh}{dt}$

**ML 关联**：这就是反向传播的计算规则——沿计算图反向累积梯度。
</details>

### Q3 ⭐⭐⭐（开放：反向传播 = 链式法则）
对于 $L = \text{MSE}(W_2 \sigma(W_1 x), y)$，用链式法则推导 $\partial L / \partial W_1$。

<details><summary>解</summary>
设 $\hat{y} = W_2 h$, $h = \sigma(W_1 x)$, $L = \frac{1}{2}\|\hat{y} - y\|^2$。

反向传播：
1. $\frac{\partial L}{\partial \hat{y}} = \hat{y} - y$
2. $\frac{\partial L}{\partial W_2} = (\hat{y}-y) h^T$
3. $\frac{\partial L}{\partial h} = W_2^T (\hat{y}-y)$
4. $\frac{\partial L}{\partial W_1} = (\sigma'(W_1 x) \odot W_2^T(\hat{y}-y)) \cdot x^T$

**关键**: 链式法则保证每次只需乘一个 Jacobian → $O(d^2)$ 而非 $O(d^3)$。
</details>

### Q4 ⭐⭐（反函数定理）
$f(x, y) = (e^x \cos y, e^x \sin y)$。验证处处可逆，求逆。

<details><summary>解</summary>
$\det J = e^{2x} > 0$ → 处处可逆。逆：$(u,v) \mapsto (\frac{1}{2}\ln(u^2+v^2), \text{atan2}(v,u))$ = 极坐标 → 笛卡尔的逆。

**ML 关联**：Normalizing Flows 中 RealNVP 等模型需要可逆 + 易算 Jacobian。
</details>

### Q5 ⭐⭐（变量替换积分）
$\int_{x^2+y^2 \leq 1} (x^2+y^2) \, dx \, dy = ?$

<details><summary>解</summary>
极坐标 $x = r\cos\theta, y = r\sin\theta$, $dx\,dy = r\,dr\,d\theta$。
$\int_0^{2\pi}\int_0^1 r^2 \cdot r \, dr \, d\theta = 2\pi \cdot \frac{1}{4} = \frac{\pi}{2}$。

**ML 关联**：概率密度的变量替换法则 $p_Y(y) = p_X(x) |\det J|^{-1}$。
</details>

### Q6 ⭐⭐⭐（开放：Normalizing Flows 的数学基础）
解释 Normalizing Flow 如何用反函数定理做密度估计。

<details><summary>解</summary>
**目标**: 学习复杂密度 $p_X(x)$。

**方法**: 通过可逆变换 $z = f^{-1}(x)$ 映射到简单先验 $p_Z(z)$（如高斯）。

**密度变换**: $p_X(x) = p_Z(f^{-1}(x)) \left|\det \frac{\partial f^{-1}}{\partial x}\right| = p_Z(z) |\det J_f|^{-1}$

**关键**: 反函数定理保证 $f$ 可逆 $\iff$ $\det J_f \neq 0$。

**工程**: RealNVP 设计 $f$ 使 Jacobian 为三角矩阵 → $\det$ $O(d)$ 而非 $O(d^3)$。

**对数似然**: $\log p_X(x) = \log p_Z(z) - \log |\det J_f|$ → 可直接优化。
</details>
