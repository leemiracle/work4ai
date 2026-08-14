# UC Berkeley MATH 53 · 精选习题

> 2 道基础 + 2 道中等 + 2 道开放题

---

## 基础题

### Q1（梯度）
对 $f(x,y) = x^2y + e^{xy}$，求 $\nabla f$ 在 $(1, 0)$ 处的值。

> **提示**：$\frac{\partial f}{\partial x} = 2xy + ye^{xy}$，$\frac{\partial f}{\partial y} = x^2 + xe^{xy}$。
>
> **答案**：$\nabla f(1,0) = (0,\ 1+1) = (0, 2)$。

### Q2（方向导数）
对 $f(x,y,z) = x^2 + y^2 + z^2$，求沿 $\hat{\mathbf{u}} = \frac{1}{\sqrt{3}}(1,1,1)$ 在 $(1,1,1)$ 处的方向导数。

> **提示**：$\nabla f = (2x, 2y, 2z)$，$D_{\hat{\mathbf{u}}}f = \nabla f \cdot \hat{\mathbf{u}}$。
>
> **答案**：$\nabla f(1,1,1) = (2,2,2)$，$D_{\hat{\mathbf{u}}}f = \frac{6}{\sqrt{3}} = 2\sqrt{3}$。

---

## 中等题

### Q3（Lagrange 乘子）
求 $f(x,y) = x^2 + y^2$ 在约束 $x + 2y = 5$ 下的最小值。

> **提示**：$\nabla f = \lambda\nabla g$，$g = x+2y-5$。
>
> **答案**：$(2x, 2y) = \lambda(1,2)$ → $2x = \lambda$，$2y = 2\lambda$ → $y = 2x$ → $x+4x=5$ → $x=1, y=2$，最小值 $= 5$。

### Q4（Hessian 判别）
对 $f(x,y) = x^2 - xy + y^2 + 3x$：
(a) 求所有临界点
(b) 用二阶判别法分类

> **提示**：$\nabla f = (2x - y + 3,\ -x + 2y) = 0$。
>
> **答案**：(a) 解得 $x=-2, y=-1$。(b) $f_{xx}=2, f_{yy}=2, f_{xy}=-1$，$D = 4-1 = 3 > 0$，$f_{xx} > 0$ → 局部最小。

---

## 开放题（连接 ML）

### Q5（梯度下降与条件数）
对 $f(x,y) = x^2 + 100y^2$（"狭谷"函数）：
(a) Hessian 和条件数是多少？
(b) 固定学习率梯度下降会遇到什么问题？
(c) Adam 如何通过梯度的二阶矩缓解？

> **提示/答案**：见 [MIT 18.02 exercises Q7](../../mit-math-courses/18_02_multivariable_calculus/exercises.md)（同类型题）。Hessian $=\text{diag}(2,200)$，条件数 $=100$。Adam 用 $\hat{m}/\sqrt{\hat{v}}$ 自适应缩放。

### Q6（重积分与概率）
联合密度 $p(x,y) = 4xy$（$0 \leq x \leq 1$，$0 \leq y \leq 1$）：
(a) 验证归一化
(b) 求边缘密度 $p(x)$

> **提示**：(a) $\int_0^1\int_0^1 4xy\,dx\,dy = 1$。(b) $p(x) = \int_0^1 4xy\,dy = 2x$。
>
> **答案**：(a) $= 4 \cdot \frac{1}{2} \cdot \frac{1}{2} = 1$ ✓。(b) $p(x) = 2x$（$0 \leq x \leq 1$）。
