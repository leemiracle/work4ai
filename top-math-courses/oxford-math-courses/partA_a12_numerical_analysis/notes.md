# Oxford Part A A12 · 数值分析 精读笔记

> **课程**：Numerical Analysis (Part A, Year 2)
> **教材**：Süli & Mayers, *An Introduction to Numerical Analysis* (CUP) — Oxford 标准教材
> **参考**：[courses.maths.ox.ac.uk](https://courses.maths.ox.ac.uk/)

---

## 〇、费曼直觉层

> **数值分析 = 用有限精度算术近似连续数学，并量化误差。**

核心矛盾：数学是精确的（$1/3$ 存在），但计算机只能存有限位（$0.333\ldots 33$）。如何让近似**可控**？

### 核心概念

| 概念 | 直觉 | ML 对应 |
|---|---|---|
| **条件数** | 问题对扰动的敏感度 | 训练的数值稳定性 |
| **稳定性** | 算法不放大误差 | 反向传播的数值安全 |
| **收敛速率** | 误差随迭代/步长下降的速度 | 优化器收敛分析 |

---

## 一、核心主题（Süli-Mayers 体系）

### 1.1 误差分析基础 ★

- **截断误差**：用有限步近似无穷过程（如截断 Taylor 级数）
- **舍入误差**：浮点数表示的有限精度
- **条件数** ★：$\kappa = \left|\frac{\text{相对输出变化}}{\text{相对输入变化}}\right|$
  - 好条件 $\kappa \approx 1$；坏条件 $\kappa \gg 1$
  - 矩阵条件数：$\kappa(A) = \|A\|\|A^{-1}\| = \sigma_{\max}/\sigma_{\min}$

**经验法则**：如果条件数为 $\kappa$，你将损失约 $\log_{10}\kappa$ 位有效数字。

### 1.2 多项式插值

- **Lagrange 插值**：$p(x) = \sum y_i \ell_i(x)$，$\ell_i(x) = \prod_{j\neq i}\frac{x-x_j}{x_i-x_j}$
- **Newton 插值**：差商表 → 便于增删节点
- **误差定理** ★：$f(x) - p(x) = \frac{f^{(n+1)}(\xi)}{(n+1)!}\prod(x - x_i)$
- **Runge 现象**：等距节点高次插值在端点振荡 → 用 Chebyshev 节点解决

### 1.3 数值积分

- **梯形法则**：$O(h^2)$ 精度
- **Simpson 法则**：$O(h^4)$ 精度
- **Richardson 外推** ★：用两个步长的结果外推 → 提升精度阶
  $$\text{Romberg 积分} = \text{Richardson 外推} + \text{梯形法则}$$

### 1.4 非线性方程求根

- **二分法**：可靠但慢（线性收敛 $O(1/2^n)$）
- **Newton 法** ★：$x_{n+1} = x_n - f(x_n)/f'(x_n)$，二次收敛 $O(|e_n|^2)$
- **割线法**：不需导数，超线性收敛 $O(|e_n|^{1.618})$

### 1.5 ODE 数值解

- **Euler 方法**：$y_{n+1} = y_n + hf(t_n, y_n)$
- **精度**：局部截断误差 $O(h^2)$，全局误差 $O(h)$
- **稳定性区域**：$z = h\lambda$ 在稳定区域内时误差不增长
- **Runge-Kutta**：更高阶 + 更大稳定区域

### 1.6 数值线性代数入门

- **高斯消元** → LU 分解：$O(n^3/3)$
- **条件数与误差放大**：$\frac{\|\delta x\|}{\|x\|} \leq \kappa(A)\frac{\|\delta b\|}{\|b\|}$
- **最小二乘**：正规方程 $A^TAx = A^Tb$ vs QR 分解（更稳定）

---

## 二、代码层

### 2.1 条件数与数值稳定性

```python
import numpy as np

# 条件数的影响: 解 Ax=b
np.random.seed(42)
for n in [5, 10, 20]:
    A = np.random.randn(n, n)
    kappa = np.linalg.cond(A)
    x_true = np.ones(n)
    b = A @ x_true
    # 加微小扰动
    b_perturbed = b + 1e-10 * np.random.randn(n)
    x_computed = np.linalg.solve(A, b_perturbed)
    rel_error = np.linalg.norm(x_computed - x_true) / np.linalg.norm(x_true)
    print(f"n={n}: κ(A)={kappa:.1f}, 相对误差={rel_error:.2e}, 损失位数≈{np.log10(kappa):.1f}")
```

### 2.2 Newton 法收敛

```python
# 求 sqrt(2): f(x) = x^2 - 2
x = 2.0
for i in range(10):
    x_new = x - (x**2 - 2) / (2*x)
    error = abs(x_new - 2**0.5)
    print(f"迭代 {i}: x={x:.15f}, 误差={error:.2e}")
    if error < 1e-15: break
    x = x_new
# 二次收敛: 误差平方化
```

---

## 三、与 ML 的联系

1. **条件数 → 训练稳定性**：Hessian 条件数大 → 梯度下降慢（需要 Adam/预处理）
2. **Newton 法 → 牛顿法优化**：$x_{n+1} = x_n - H^{-1}\nabla f$
3. **QR 分解 → 最小二乘**：线性回归的数值稳定实现
4. **ODE 求解器 → Neural ODE**：用数值 ODE 解算器做前向传播

---

## 四、推荐路径

1. **Süli-Mayers 第 1-7 章**：误差 + 插值 + 积分 + 求根 + ODE → **核心**
2. **第 8-9 章**：数值线代 → 参考 [UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)
3. **交叉**：[Cambridge Part IB NA](../../cambridge-math-courses/partIB_numerical_analysis/)（类似难度，不同组织）
