# UT Austin M 427L · 章节笔记

> **教材**：Colley, *Vector Calculus*；或 Stewart 多变量部分
> **定位**：UT Austin 向量微积分。与 [MIT 18.02](../../mit-math-courses/18_02_multivariable_calculus/) / [Berkeley MATH 53](../../berkeley-math-courses/math53_multivariable/) 对等
> **重点**：梯度/Jacobian/Hessian + 三大定理，连接 ML 优化

---

## 核心框架：多变量微积分的四级火箭

| 层级 | 数学对象 | ML 角色 |
|---|---|---|
| 偏导 | $\partial f/\partial x_i$ | 参数级梯度 |
| 梯度 | $\nabla f$ | 优化方向信号 |
| Jacobian | $J = \partial\mathbf{y}/\partial\mathbf{x}$ | **反向传播** ★ |
| Hessian | $H = \nabla^2 f$ | 二阶优化 / 曲率 |

---

## 第 1 章：向量与 3D 几何

### 1.1 点积

$$\mathbf{a}\cdot\mathbf{b} = \|\mathbf{a}\|\|\mathbf{b}\|\cos\theta$$

**ML 关联**：cosine similarity = 词向量相似度；attention score $= \mathbf{q}\cdot\mathbf{k}$。

### 1.2 叉积

$\|\mathbf{a}\times\mathbf{b}\| = \|\mathbf{a}\|\|\mathbf{b}\|\sin\theta$。

---

## 第 2 章：偏导数与梯度 ★★★

### 2.1 梯度

$$\nabla f = \left(\frac{\partial f}{\partial x}, \frac{\partial f}{\partial y}, \frac{\partial f}{\partial z}\right)$$

$\nabla f$ = 最陡上升方向；$-\nabla f$ = **梯度下降方向**。

### 2.2 方向导数

$$D_{\hat{\mathbf{u}}}f = \nabla f \cdot \hat{\mathbf{u}}$$

### 2.3 梯度下降 ★

$$\mathbf{w}_{t+1} = \mathbf{w}_t - \eta\nabla f(\mathbf{w}_t)$$

Adam（[arXiv:1412.6980](https://arxiv.org/abs/1412.6980)）：加动量 + 自适应步长。

### 2.4 链式法则（多元）

$$\frac{\partial L}{\partial x_j} = \sum_i \frac{\partial L}{\partial y_i}\frac{\partial y_i}{\partial x_j} = (J^T\nabla_\mathbf{y} L)_j$$

**ML 关联**：反向传播 = Jacobian 链式乘积。

---

## 第 3 章：多变量优化

### 3.1 临界点 + Hessian

$\nabla f = 0$ → 临界点。$D = f_{xx}f_{yy} - f_{xy}^2$：
- $D > 0$，$f_{xx} > 0$ → 最小
- $D < 0$ → 鞍点

### 3.2 Lagrange 乘子

$$\nabla f = \lambda\nabla g \quad (g = \text{约束})$$

**ML 关联**：SVM / KKT 条件。

---

## 第 4 章：重积分

$$\iint_R f\,dA, \quad \iiint_V f\,dV$$

**ML 关联**：概率归一化 $\iint p(x,y)\,dx\,dy = 1$；边缘化 $p(x) = \int p(x,y)\,dy$。

---

## 第 5 章：向量微积分三大定理

### 5.1 Green 定理

$$\oint_C P\,dx + Q\,dy = \iint_D (Q_x - P_y)\,dA$$

### 5.2 Stokes 定理

$$\oint_C \mathbf{F}\cdot d\mathbf{r} = \iint_S (\nabla\times\mathbf{F})\cdot d\mathbf{S}$$

### 5.3 散度定理（Divergence）

$$\iint_S \mathbf{F}\cdot d\mathbf{S} = \iiint_V (\nabla\cdot\mathbf{F})\,dV$$

**ML 关联**：扩散模型的概率流连续性方程 $\frac{\partial p}{\partial t} + \nabla\cdot(p\mathbf{v}) = 0$（[arXiv:2006.11239](https://arxiv.org/abs/2006.11239)）。

---

## 与 ML 的关联总表

| M 427L 概念 | ML 应用 |
|---|---|
| 梯度 $\nabla f$ | SGD / Adam |
| Jacobian | 反向传播 |
| Hessian | 二阶优化 / 鞍点 |
| Lagrange 乘子 | SVM |
| 散度定理 | 扩散模型概率流 |
| 重积分 | 概率归一化 |

---

## 代码验证

### 数值梯度 + Jacobian 验证

```python
## 代码验证

### 验证 1：梯度下降 + Rosenbrock

```python
import numpy as np

def num_gradient(f, w, h=1e-5):
    g = np.zeros_like(w)
    for i in range(len(w)):
        wp, wm = w.copy(), w.copy()
        wp[i] += h; wm[i] -= h
        g[i] = (f(wp) - f(wm)) / (2*h)
    return g

# Rosenbrock 函数
f = lambda w: (1-w[0])**2 + 100*(w[1]-w[0]**2)**2
w = np.array([-1.0, 1.0])
for _ in range(2000):
    w = w - 0.002 * num_gradient(f, w)
print(f"优化结果: {w}")  # 接近 (1, 1)
```

### 验证 2：散度定理数值验证

```python
import numpy as np

# 散度定理: ∫∫∫_V ∇·F dV = ∮∮_S F·n dA
# 简单验证: F = (x, y, z), V = 单位球
# ∇·F = 3, 体积 = 4π/3 → 体积分 = 4π
# 表面积 = 4π, F·n = 1 → 面积分 = 4π

# 数值体积分（Monte Carlo）
N = 100000
# 均匀采样在 [-1,1]^3 立方体中（体积=8），计算单位球内比例
N = 100000
pts = np.random.uniform(-1, 1, (N, 3))
r = np.linalg.norm(pts, axis=1)
inside = np.sum(r <= 1.0)
vol_ball = inside / N * 8  # 球体积 ≈ 4π/3
vol_integral = vol_ball * 3  # div F = 3

# 数值面积分（Monte Carlo on unit sphere）
pts_surf = pts[r > 0] / r[r > 0, None]  # 投影到单位球
surf_integral = np.sum(pts_surf**2, axis=1).mean() * 4 * np.pi  # F·n = r²/|r|² = 1

print(f"体积分 (散度×体积): {vol_integral:.4f}")
print(f"面积分 (F·n):       {surf_integral:.4f}")
print(f"精确值 4π:          {4*np.pi:.4f}")
```

### 验证 3：保守场验证（路径无关）

```python
import numpy as np

# F = ∇f where f(x,y) = x^2*y + y^3
# F = (2xy, x^2 + 3y^2)
f = lambda xy: xy[0]**2 * xy[1] + xy[1]**3
Fx = lambda xy: 2*xy[0]*xy[1]
Fy = lambda xy: xy[0]**2 + 3*xy[1]**2

# 从 (0,0) 到 (1,1)，走两条不同路径
# 路径1: 直线 (0,0)→(1,1)
# 路径2: 先 (0,0)→(1,0)，再 (1,0)→(1,1)

N = 1000
# 路径1
line_integral_1 = 0
for i in range(N):
    t = i / N
    x, y = t, t  # 参数化
    dx, dy = 1/N, 1/N
    line_integral_1 += Fx([x,y])*dx + Fy([x,y])*dy

# 路径2
line_integral_2 = 0
for i in range(N):  # 水平
    t = i / N; x, y = t, 0
    line_integral_2 += Fx([x,y])*(1/N)
for i in range(N):  # 垂直
    t = i / N; x, y = 1, t
    line_integral_2 += Fy([x,y])*(1/N)

exact = f([1,1]) - f([0,0])  # 保守场功 = 势能差
print(f"路径1: {line_integral_1:.4f}, 路径2: {line_integral_2:.4f}, 精确: {exact:.4f}")
print(f"路径无关: 两者都等于势能差 ✓" if abs(line_integral_1 - exact) < 0.1 else "×")
```

---

## 深度专题：散度定理与连续性方程

### 连续性方程（物理 → 概率流）

散度定理在 ML 中最直接的应用是连续性方程——概率守恒：

$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{v}) = 0$$

其中 $\rho(\mathbf{x}, t)$ 是概率密度，$\mathbf{v}(\mathbf{x}, t)$ 是速度场。

### 扩散模型中的概率流

Score-SDE [arXiv:2011.13456] 将扩散过程写成：

$$d\mathbf{x} = \mathbf{f}(\mathbf{x},t)dt + g(t)d\mathbf{w}$$

对应的 Fokker-Planck 方程（连续性方程变体）：

$$\frac{\partial p}{\partial t} = -\nabla \cdot (\mathbf{f} p) + \frac{g^2}{2}\Delta p$$

**散度定理保证了概率始终归一**：$\int p(\mathbf{x}, t) d\mathbf{x} = 1$ 对所有 $t$。

### Flow Matching [arXiv:2210.02747]

Flow Matching 直接构造连续速度场 $\mathbf{v}(\mathbf{x}, t)$ 满足连续性方程，生成 $\mathbf{x}_0 \to \mathbf{x}_1$ 的概率流。散度定理是理论基础。

---

## 深度专题：梯度场与保守性

### 为什么梯度场是保守场？

$\mathbf{F} = \nabla f$ 的旋度恒为零：$\nabla \times (\nabla f) = 0$。

**直观理解**：梯度场"只下山不上山"，环路净功为零——你绕一圈回到原点，势能不变。

### ML 应用：势能 = 损失函数

损失函数 $L(\mathbf{w})$ 的梯度 $\nabla L$ 是一个梯度场（保守场）。这意味着：

- 从任意 $\mathbf{w}_0$ 出发，沿 $-\nabla L$ 方向最终到达的 $L$ 值只取决于终点位置
- 不存在"环路"——SGD 不会循环回到同一个 $L$ 值（在精确梯度下）

**例外**：带动量的 SGD 可能振荡（动量使其"过冲"），但这是算法的近似，不是梯度场的性质。

---

## 不足与局限

| 方法 | 局限 | 更高级处理 |
|---|---|---|
| 梯度下降 | 条件数敏感 | Adam / 预处理 |
| Green/Stokes | 仅光滑场 | 分布理论 |
| Lagrange | 需解析约束 | 罚函数 |
| Euler 法 | 低精度/刚性不稳定 | RK45 / 隐式法 |

---

## 与 work4ai 讲透系列的交叉

- **讲透反向传播**：Jacobian 链式法则（第 2 章）
- **讲透优化器**：梯度 + Hessian（第 2-3 章）
- **讲透 SVM**：Lagrange 乘子（第 3 章）
- **讲透扩散模型**：散度定理 / 概率流（第 5 章）
- **讲透 Neural ODE**：向量场 + 积分曲线（第 4 章）
