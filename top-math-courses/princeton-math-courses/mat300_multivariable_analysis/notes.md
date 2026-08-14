# Princeton MAT 300 · 章节笔记（Spivak *Calculus on Manifolds*）

> **教材**：Spivak *Calculus on Manifolds*；补充 Munkres *Analysis on Manifolds*
> **特色**：多变量微积分的严格基础——微分形式、Stokes 定理

---

# 费曼三层讲透：多变量分析

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **全导数 $Df$** | **"最佳线性近似"**：Jacobian 矩阵 = 多变量版的斜率 |
| **链式法则** | **"复合放大率 = 逐级放大率之积"**：$D(f \circ g) = Df \cdot Dg$ |
| **反函数定理** | **"Jacobian 非零 → 局部可逆"** |
| **微分形式** | **"可以积分的东西"**：$k$-形式在 $k$ 维面上积分 |
| **Stokes 定理** | **"边界上的流 = 内部的旋"**：$\int_{\partial M} \omega = \int_M d\omega$ |

---

## 🧮 数学层

### 多变量微分

$f: \mathbb{R}^n \to \mathbb{R}^m$ 在 $a$ 可微 $\iff$ $\exists$ 线性映射 $Df(a): \mathbb{R}^n \to \mathbb{R}^m$:

$$\lim_{h \to 0} \frac{\|f(a+h) - f(a) - Df(a) \cdot h\|}{\|h\|} = 0$$

$Df(a)$ = Jacobian 矩阵 $J_{ij} = \partial f_i / \partial x_j$。

### 链式法则

$$D(f \circ g)(a) = Df(g(a)) \cdot Dg(a)$$

**ML 应用**：反向传播就是链式法则！$\frac{\partial L}{\partial \theta_1} = \frac{\partial L}{\partial z} \cdot \frac{\partial z}{\partial \theta_1}$。

### 反函数定理 ★★

$Df(a)$ 可逆 $\implies$ $f$ 在 $a$ 附近有 $C^1$ 逆函数。

$$D(f^{-1})(f(a)) = [Df(a)]^{-1}$$

**ML 应用**：Normalizing Flows —— $p_Y(y) = p_X(f^{-1}(y)) |\det J_{f^{-1}}(y)|$。

### 隐函数定理 ★

$F: \mathbb{R}^{n+k} \to \mathbb{R}^n$, $\det D_x F(a,b) \neq 0$ $\implies$ 存在 $g: \mathbb{R}^k \to \mathbb{R}^n$ 使得 $F(g(y), y) = 0$。

### 微分形式与 Stokes 定理 ★★★

**外微分** $d: \Omega^k \to \Omega^{k+1}$，$d \circ d = 0$。

**Stokes 定理**（统一形式）：

$$\boxed{\int_{\partial M} \omega = \int_M d\omega}$$

统一了：微积分基本定理、Green 定理、Gauss 散度定理、经典 Stokes 定理。

---

## 💻 代码层

```python
import numpy as np
# 数值 Jacobian
def numerical_jacobian(f, x, eps=1e-5):
    n, m = len(x), len(f(x))
    J = np.zeros((m, n))
    f0 = np.array(f(x))
    for j in range(n):
        x_plus = x.copy()
        x_plus[j] += eps
        J[:, j] = (np.array(f(x_plus)) - f0) / eps
    return J

# 示例: f(x,y) = (x^2, xy)
f = lambda x: [x[0]**2, x[0]*x[1]]
x = np.array([2.0, 3.0])
J = numerical_jacobian(f, x)
print(f"数值 Jacobian:\n{J}")
print(f"精确 Jacobian: [[2x, 0], [y, x]] = [[4, 0], [3, 2]]")

# 链式法则演示 = 反向传播
# L = (x*y)^2,  dL/dx = 2(x*y)*y
x_val, y_val = 2.0, 3.0
z = x_val * y_val       # 前向
L = z ** 2              # 前向
dL_dz = 2 * z           # 反向: dL/dz
dz_dx = y_val           # 反向: dz/dx
dL_dx = dL_dz * dz_dx   # 链式法则
print(f"\n链式法则: dL/dx = {dL_dx} (精确: {2*(x_val*y_val)*y_val})")
```

---

## ⚠️ 不足层
- Spivak 紧凑但缺例子 → 用 Munkres 补充
- 不涉及流形理论 → MAT 429 / 高阶课

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| Jacobian | 反向传播 / Normalizing Flows |
| 链式法则 | Backpropagation ★★★ |
| 反函数定理 | Normalizing Flows 密度变换 |
| 隐函数定理 | 等约束优化 / 隐式层 |
| Stokes 定理 | 流形上的优化 / 信息几何 |

---

## 章节概览（Spivak）

| 章 | 内容 | 关键 |
|---|---|---|
| 1 | $\mathbb{R}^n$ 上的函数 | 范数、内积 |
| 2 | 微分 ★ | Jacobian、链式法则 |
| 3 | 反/隐函数定理 ★★ | Normalizing Flows |
| 4 | 积分 | Fubini、变量替换 |
| 5 | 微分形式 ★★★ | Stokes 定理 |
