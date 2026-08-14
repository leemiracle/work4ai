# UC Berkeley MATH 54 · ODE 部分精选习题

> 2 道基础 + 2 道中等 + 2 道开放题（仅 ODE 部分）

---

## 基础题

### Q1（可分离变量）
求解 $\dot{x} = 3x$，$x(0) = 2$。

> **答案**：$x(t) = 2e^{3t}$（指数增长）。

### Q2（二阶 ODE 分类）
$\ddot{x} + 6\dot{x} + 13x = 0$ 的解是什么类型？写出通解。

> **提示**：特征方程 $r^2 + 6r + 13 = 0$，$r = -3 \pm 2i$。
>
> **答案**：欠阻尼振荡，$x(t) = e^{-3t}(c_1\cos 2t + c_2\sin 2t)$。

---

## 中等题

### Q3（线性系统稳定性）
$\dot{\mathbf{x}} = \begin{pmatrix}0 & 1\\-6 & -5\end{pmatrix}\mathbf{x}$：
(a) 求特征值
(b) 判断稳定性

> **提示**：$\text{tr} = -5$，$\det = 6$。
>
> **答案**：(a) $\lambda^2 + 5\lambda + 6 = 0$，$\lambda = -2, -3$。(b) 两负实根 → 稳定节点。

### Q4（Laplace 变换）
用 Laplace 变换求解 $\dot{x} + 2x = e^{-t}$，$x(0) = 0$。

> **提示**：$sX + 2X = 1/(s+1)$ → $X = 1/((s+2)(s+1))$ → 部分分式。
>
> **答案**：$X = \frac{1}{s+1} - \frac{1}{s+2}$，$x(t) = e^{-t} - e^{-2t}$。

---

## 开放题（连接 ML）

### Q5（ResNet = Euler 法）
说明 ResNet 的 $\mathbf{h}_{l+1} = \mathbf{h}_l + f(\mathbf{h}_l)$ 是哪个 ODE 的 Euler 离散化。连续化（Neural ODE）有什么优势和劣势？

> **答案要点**：$\dot{\mathbf{h}} = f_\theta(\mathbf{h})$ 的 Euler 法（$\Delta t = 1$）。优势：内存 $O(1)$（adjoint），可变深度/精度；劣势：训练慢（需 ODE solver 反复求值）。详见 [MIT 18.03 exercises Q6](../../mit-math-courses/18_03_differential_equations/exercises.md)。

### Q6（Mamba 的离散化）
Mamba 的连续 SSM $\dot{\mathbf{h}} = A\mathbf{h} + B\mathbf{x}$，用 Euler 法离散化后是什么形式？为什么初始化时 $A$ 的特征值要为负？

> **答案要点**：Euler：$\mathbf{h}_k = (I + \Delta A)\mathbf{h}_{k-1} + \Delta B\mathbf{x}_k$。负特征值保证连续系统稳定 → 离散后长程记忆衰减但可控。详见 [MIT 18.03 exercises Q7](../../mit-math-courses/18_03_differential_equations/exercises.md)。
