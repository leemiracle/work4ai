# Stanford MATH 51 · 多变量部分精选习题

> 2 道基础 + 2 道中等 + 2 道开放题（多变量微积分部分）

---

## 基础题

### Q1（梯度与方向导数）
$f(x,y) = x^2 + 2y^2$，求 $\nabla f(1,1)$ 和沿 $(1,1)/\sqrt{2}$ 方向的方向导数。

> **答案**：$\nabla f = (2x, 4y)$，$(2, 4)$。$D_{\hat{\mathbf{u}}}f = (2+4)/\sqrt{2} = 3\sqrt{2}$。

### Q2（链式法则）
$z = f(x, y)$，$x = t^2$，$y = t^3$。写出 $\frac{dz}{dt}$ 并计算 $f(x,y) = xy$ 时在 $t=1$ 的值。

> **提示**：$\frac{dz}{dt} = f_x \cdot 2t + f_y \cdot 3t^2$。
>
> **答案**：$f_x = y, f_y = x$。$t=1$ 时 $x=1, y=1$，$\frac{dz}{dt} = 1\cdot2 + 1\cdot3 = 5$。

---

## 中等题

### Q3（Lagrange 乘子）
最大化 $f(x,y,z) = xyz$，约束 $x+y+z = 6$（$x,y,z > 0$）。

> **提示**：$\nabla f = \lambda\nabla g$。
>
> **答案**：$(yz, xz, xy) = \lambda(1,1,1)$ → $x = y = z = 2$，最大值 $= 8$。

### Q4（Hessian 判别）
$f(x,y) = x^3 - 3x + y^2$：
(a) 求所有临界点
(b) 分类

> **答案**：$\nabla f = (3x^2-3,\ 2y) = 0$ → $x = \pm 1, y = 0$。$H = \text{diag}(6x, 2)$。
> $(1,0)$：$D = 12 > 0$，$f_{xx} = 6 > 0$ → 局部最小。
> $(-1,0)$：$D = -12 < 0$ → 鞍点。

---

## 开放题（连接 ML）

### Q5（链式法则 → 反向传播）
对 $\hat{y} = \sigma(w_1x_1 + w_2x_2 + b)$，$L = \frac{1}{2}(\hat{y}-y)^2$，用链式法则推导 $\frac{\partial L}{\partial w_1}$。

> **答案要点**：$\frac{\partial L}{\partial w_1} = (\hat{y}-y)\cdot\sigma'(z)\cdot x_1$，其中 $z = w_1x_1+w_2x_2+b$。详见 [MIT 18.01 exercises Q6](../../mit-math-courses/18_01_calculus/exercises.md)（同型题）。

### Q6（SVD + 梯度 = PCA + 优化）
解释为什么对 $f(\mathbf{w}) = \mathbf{w}^T H\mathbf{w}$（$H$ 正定），在 Hessian 特征基下做坐标变换后，梯度下降各方向的收敛速度由特征值决定。这与 PCA 有什么联系？

> **提示/答案要点**：在特征基下 $H = \text{diag}(\lambda_1, \dots, \lambda_n)$，各方向独立。方向 $i$ 的有效学习率 $\propto \lambda_i$。条件数 $= \lambda_{\max}/\lambda_{\min}$ 决定整体收敛速度。PCA 找的正是协方差矩阵（类似 $H$）的最大特征值方向——即方差最大/收敛最慢的方向。Adam 通过自适应步长缓解这个条件数问题。
