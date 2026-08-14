# UT Austin M 427L · 精选习题

> 2 道基础 + 2 道中等 + 2 道开放题

---

## 基础题

### Q1（梯度）
$f(x,y,z) = x^2 + 2y^2 + 3z^2$，求 $\nabla f$ 在 $(1,1,1)$ 处的值和 $\|\nabla f\|$。

> **答案**：$\nabla f = (2x, 4y, 6z)$，$(2, 4, 6)$，$\|\nabla f\| = \sqrt{4+16+36} = \sqrt{56} = 2\sqrt{14}$。

### Q2（方向导数）
对上题的 $f$，沿 $(1,1,1)/\sqrt{3}$ 方向在 $(1,1,1)$ 处的方向导数。

> **答案**：$D_{\hat{\mathbf{u}}}f = (2,4,6)\cdot\frac{1}{\sqrt{3}}(1,1,1) = \frac{12}{\sqrt{3}} = 4\sqrt{3}$。

---

## 中等题

### Q3（Lagrange 乘子）
求 $f(x,y) = 2x + y$ 在约束 $x^2 + y^2 = 1$ 下的最大值。

> **提示**：$\nabla f = \lambda\nabla g$。
>
> **答案**：$(2, 1) = \lambda(2x, 2y)$ → $x = 1/\lambda$，$y = 1/(2\lambda)$。代入 $1/\lambda^2 + 1/(4\lambda^2) = 1$ → $\lambda = \sqrt{5}/2$，最大值 $= 2\cdot\frac{2}{\sqrt{5}} + \frac{1}{\sqrt{5}} = \sqrt{5}$。

### Q4（Green 定理）
用 Green 定理计算 $\oint_C (3x - y)\,dx + (x + 5y)\,dy$，$C$ 为单位圆（逆时针）。

> **提示**：$P = 3x-y$，$Q = x+5y$，$Q_x - P_y = 1 - (-1) = 2$。
>
> **答案**：$= \iint_D 2\,dA = 2 \cdot \pi(1)^2 = 2\pi$。

---

## 开放题（连接 ML）

### Q5（Jacobian → 反向传播）
对两层网络 $\mathbf{h} = \text{ReLU}(W_1\mathbf{x})$，$\hat{y} = \mathbf{w}_2^T\mathbf{h}$，$L = \frac{1}{2}(\hat{y} - y)^2$，用 Jacobian 链式法则推导 $\frac{\partial L}{\partial W_1}$。

> **答案要点**：$\frac{\partial L}{\partial W_1} = (\hat{y}-y)\cdot\mathbf{w}_2 \odot \mathbb{1}[W_1\mathbf{x} > 0] \cdot \mathbf{x}^T$。详见 [MIT 18.02 exercises Q6](../../mit-math-courses/18_02_multivariable_calculus/exercises.md)。

### Q6（散度定理 → 扩散模型概率流）
扩散模型中前向过程满足连续性方程 $\frac{\partial p}{\partial t} = -\nabla\cdot(p\mathbf{v})$（$\mathbf{v}$ = 速度场）。用散度定理解释：为什么这保证了"总概率守恒"（$\int p\,d\mathbf{x} = 1$ 对所有 $t$）？

> **提示**：对全空间积分 $\frac{\partial}{\partial t}\int p\,d\mathbf{x} = -\int\nabla\cdot(p\mathbf{v})\,d\mathbf{x}$，用散度定理转面积分。
>
> **答案要点**：$\frac{\partial}{\partial t}\int p\,d\mathbf{x} = -\oint_{\partial V}(p\mathbf{v})\cdot d\mathbf{S}$。若概率在全空间衰减（边界 $p \to 0$），面积分 $= 0$，所以 $\int p\,d\mathbf{x}$ 不随时间变化 $= 1$。这是 DDPM（[arXiv:2006.11239](https://arxiv.org/abs/2006.11239)）和 Score-SDE（[arXiv:2011.13456](https://arxiv.org/abs/2011.13456)）概率流方程的基础。
