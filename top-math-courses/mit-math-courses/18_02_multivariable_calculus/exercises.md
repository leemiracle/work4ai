# MIT 18.02 · 精选习题

> 2 道基础 + 3 道中等 + 2 道开放题（连接 ML）

---

## 基础题

### Q1（梯度计算）

对 $f(x,y,z) = x^2y + yz^3 + \sin(xz)$，求 $\nabla f$ 在点 $(1, 2, 0)$ 处的值。

> **提示**：分别对 $x, y, z$ 求偏导再代入。
>
> **答案**：$\nabla f = (2xy + z\cos(xz),\ x^2 + z^3,\ 3yz^2 + x\cos(xz))$，在 $(1,2,0)$ 处 $= (4,\ 1,\ 1)$。

### Q2（方向导数）

对 $f(x,y) = x^2 + 3xy + y^2$，求沿方向 $\mathbf{u} = \frac{1}{\sqrt{2}}(1, 1)$ 在 $(1, 0)$ 处的方向导数。哪个方向是 $f$ 下降最快的？

> **提示**：$D_{\mathbf{u}}f = \nabla f \cdot \mathbf{u}$；下降最快方向是 $-\nabla f / \|\nabla f\|$。
>
> **答案**：$\nabla f(1,0) = (2, 3)$，$D_{\mathbf{u}}f = \frac{5}{\sqrt{2}} \approx 3.54$。下降最快方向 $= -(2,3)/\sqrt{13}$。

---

## 中等题

### Q3（梯度下降迭代）

对 $f(x, y) = x^2 + 4y^2$，从 $(1, 1)$ 出发，学习率 $\eta = 0.1$：
(a) 写出前 2 步梯度下降的值
(b) 最小值在哪里？为什么这条路径会收敛？

> **提示**：$\nabla f = (2x, 8y)$。
>
> **答案**：(a) $\nabla f(1,1)=(2,8)$，$(x_1,y_1)=(0.8, 0.2)$；$\nabla f(0.8,0.2)=(1.6,1.6)$，$(x_2,y_2)=(0.64,0.04)$。 (b) 最小值在 $(0,0)$。注意 $y$ 方向收敛远快于 $x$（因为系数 4 vs 1）——这正是**条件数**问题，是 Adam 等自适应优化器要解决的。

### Q4（Jacobian 矩阵）

对坐标变换 $\mathbf{y} = (y_1, y_2)$，其中 $y_1 = x_1^2 + x_2$，$y_2 = x_1 x_2^2$：
(a) 求 Jacobian 矩阵 $J = \frac{\partial \mathbf{y}}{\partial \mathbf{x}}$
(b) 在 $(1, 1)$ 处求 $J$，并解释其行列式的几何意义

> **提示**：$J$ 的第 $(i,j)$ 元素是 $\partial y_i / \partial x_j$。
>
> **答案**：(a) $J = \begin{pmatrix}2x_1 & 1\\x_2^2 & 2x_1 x_2\end{pmatrix}$。(b) $J(1,1) = \begin{pmatrix}2&1\\1&2\end{pmatrix}$，$\det J = 3$。行列式 = 面积放大倍数 = 3。

### Q5（Lagrange 乘子）

求 $f(x,y) = xy$ 在约束 $x + y = 4$ 下的最大值。

> **提示**：设 $g(x,y) = x + y - 4 = 0$，解 $\nabla f = \lambda\nabla g$。
>
> **答案**：$(y, x) = \lambda(1, 1)$ → $x = y$，代入 $2x = 4$ → $x = y = 2$，最大值 $= 4$。

---

## 开放题（连接 ML）

### Q6（Jacobian 推导反向传播）

对两层网络 $\mathbf{h} = \sigma(W_1\mathbf{x})$，$\hat{\mathbf{y}} = W_2\mathbf{h}$，损失 $L = \frac{1}{2}\|\hat{\mathbf{y}} - \mathbf{y}\|^2$：
(a) 用 Jacobian 链式法则写出 $\frac{\partial L}{\partial W_1}$ 的完整表达式
(b) 解释为什么反向传播比"前向模式自动微分"在大网络中更高效

> **提示**：(a) $\frac{\partial L}{\partial W_1} = \frac{\partial L}{\partial \hat{\mathbf{y}}}\cdot\frac{\partial \hat{\mathbf{y}}}{\partial \mathbf{h}}\cdot\frac{\partial \mathbf{h}}{\partial W_1}$，其中 $\frac{\partial \mathbf{h}}{\partial \mathbf{a}} = \text{diag}(\sigma'(\mathbf{a}))$。
> (b) 前向模式对每个输入维度传播一次（$O(n)$ 次），反向模式对每个输出传播一次（$O(m)$ 次）。ML 损失是标量（$m=1$），所以反向只需 1 次。
>
> **答案要点**：$\frac{\partial L}{\partial W_1} = W_2^T(\hat{\mathbf{y}}-\mathbf{y}) \odot \sigma'(W_1\mathbf{x}) \cdot \mathbf{x}^T$。

### Q7（条件数与优化器）

(a) 对 $f(x,y) = x^2 + 100y^2$，Hessian 是什么？条件数是多少？
(b) 用纯梯度下降（固定学习率）优化时会出现什么问题？
(c) Adam 如何缓解这个问题？用梯度的二阶矩解释

> **提示**：(a) 条件数 = 最大/最小特征值。(c) Adam 对每个参数自适应缩放步长。
>
> **答案要点**：(a) $H = \text{diag}(2, 200)$，条件数 $= 100$。(b) $y$ 方向梯度大、$x$ 方向梯度小，固定学习率要么在 $y$ 方向发散（$\eta$ 太大）要么在 $x$ 方向极慢（$\eta$ 太小）。(c) Adam 用 $\hat{m}_t / (\sqrt{\hat{v}_t} + \epsilon)$ 自适应缩放——$y$ 方向的大梯度被 $\sqrt{v_t}$ 大值抵消，相当于自动减小步长。
