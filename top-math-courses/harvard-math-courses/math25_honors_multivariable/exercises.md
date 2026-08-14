# Harvard Math 25 · 精选习题

> 2 道基础 + 2 道中等 + 2 道开放题（严格证明导向）

---

## 基础题

### Q1（Fréchet 可微性）
证明 $f(x,y) = x^2 + y^2$ 在原点可微，并写出 $Df(0,0)$。

> **提示**：验证 $\frac{|f(\mathbf{h}) - f(\mathbf{0}) - Df\cdot\mathbf{h}|}{\|\mathbf{h}\|} \to 0$。
>
> **答案**：$Df(0,0) = (0, 0)$（零线性映射）。$f(\mathbf{h}) - 0 - 0 = \|\mathbf{h}\|^2$，除以 $\|\mathbf{h}\|$ 得 $\|\mathbf{h}\| \to 0$。

### Q2（链式法则）
设 $f: \mathbb{R}^2\to\mathbb{R}$，$f(x,y) = e^{xy}$，$g: \mathbb{R}\to\mathbb{R}^2$，$g(t) = (t, t^2)$。计算 $D(f\circ g)(1)$。

> **答案**：$Df = (y e^{xy}, xe^{xy})$，在 $(1,1)$ 处 $= (e, e)$。$Dg = (1, 2t)^T$，在 $t=1$ $= (1, 2)^T$。$D(f\circ g)(1) = (e, e)\cdot(1, 2)^T = 3e$。

---

## 中等题

### Q3（IFT 应用）
$f(x,y) = (e^x\cos y,\ e^x\sin y)$（复指数的实/虚部）：
(a) 求 $\det Df$
(b) $f$ 在哪些点局部可逆？

> **提示**：Jacobian 行列式。
>
> **答案**：$Df = \begin{pmatrix}e^x\cos y & -e^x\sin y\\e^x\sin y & e^x\cos y\end{pmatrix}$，$\det = e^{2x}(\cos^2 y + \sin^2 y) = e^{2x} > 0$（处处非零）。所以 $f$ 处处局部可逆。

### Q4（变量替换）
计算 $\iint_R (x^2 + y^2)\,dA$，其中 $R$ 是单位圆盘。用极坐标变换验证 $|\det J| = r$。

> **提示**：极坐标 $x = r\cos\theta$，$y = r\sin\theta$。
>
> **答案**：$\int_0^{2\pi}\int_0^1 r^2 \cdot r\,dr\,d\theta = 2\pi \cdot \frac{1}{4} = \frac{\pi}{2}$。

---

## 开放题（连接 ML）

### Q5（IFT → Normalizing Flows）
Normalizing Flow 用可逆变换 $f_\theta$ 把简单分布 $p_Z$ 变为复杂分布 $p_X$：
(a) 用变量替换公式写出 $p_X(\mathbf{x})$ 与 $p_Z(\mathbf{z})$ 的关系
(b) IFT 保证了什么？为什么 $\det J$ 可逆至关重要？

> **提示**：(a) $p_X(\mathbf{x}) = p_Z(f^{-1}(\mathbf{x})) / |\det J_f|$。
>
> **答案要点**：(a) $p_X(\mathbf{x}) = p_Z(\mathbf{z})|\det \frac{\partial f^{-1}}{\partial \mathbf{x}}| = p_Z(\mathbf{z})/|\det J_f(\mathbf{z})|$。(b) IFT 保证 $f_\theta$ 在 $\det J \neq 0$ 处局部可逆——否则 $f^{-1}$ 不存在，无法计算 $p_X$。这是 RealNVP 等架构设计三角矩阵 $J$（$\det$ 易算）的原因。

### Q6（Hessian + 收敛性严格分析）
对严格凸函数 $f$（$H \succeq mI$，$m > 0$），用二阶 Taylor 展开证明梯度下降（学习率 $\eta \leq 1/L$，$H \preceq LI$）满足线性收敛：
$$f(\mathbf{w}_{t+1}) - f^* \leq (1 - \eta m)(f(\mathbf{w}_t) - f^*)$$

> **提示**：$f(\mathbf{w} - \eta\nabla f) \leq f(\mathbf{w}) - \eta\|\nabla f\|^2 + \frac{L\eta^2}{2}\|\nabla f\|^2$。再用强凸性 $\|\nabla f\|^2 \geq 2m(f - f^*)$。
>
> **答案要点**：取 $\eta = 1/L$，$f(\mathbf{w}_{t+1}) \leq f(\mathbf{w}_t) - \frac{1}{2L}\|\nabla f\|^2 \leq f(\mathbf{w}_t) - \frac{m}{L}(f(\mathbf{w}_t) - f^*)$。收敛率 $\propto m/L$（条件数的倒数）。
