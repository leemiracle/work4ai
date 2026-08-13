# ETH 401-2611 · CSE 数值方法 精读笔记

> **课程**：Numerical Methods for CSE (Computational Science and Engineering)
> **参考**：[ETH Course Catalog](https://www.vvz.ethz.ch/)；Quarteroni, *Numerical Models for Differential Problems*
> **特色**：ETH CSE 方向，重点在**PDE 数值解** + **高性能计算**

---

## 〇、费曼直觉层

> **CSE 数值方法 = 用计算机解连续数学问题的算法设计。**

核心问题：微积分/PDE 定义在连续空间，但计算机只能处理离散数据。如何在**有限精度、有限时间**内得到**足够准确**的近似解？

### CSE vs 经典数值分析

| 经典 NA | CSE 数值方法 |
|---|---|
| 插值、积分、根求解 | PDE 数值解（FEM/FDM） |
| 单变量为主 | 多变量、高维 |
| 精度分析 | **大规模并行** + **HPC** |

---

## 一、核心主题

### 1.1 数值线性代数回顾

参见 [UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)（Trefethen & Bau）。核心：
- LU/QR/Cholesky 分解
- SVD 与低秩近似
- 迭代法（CG, GMRES）→ 大规模稀疏系统

### 1.2 函数逼近与插值 ★

- **多项式插值**：Lagrange / Newton 形式
- **样条**：三次样条（$C^2$ 连续）
- **Chebyshev 节点** ★：避免 Runge 现象
  $$x_k = \cos\frac{(2k+1)\pi}{2n}, \quad k = 0, \ldots, n-1$$
- **最小二乘逼近**：正交多项式基

### 1.3 数值积分（Quadrature）

- **Newton-Cotes 公式**：梯形、Simpson
- **Gauss 求积** ★：最优节点选择 → $n$ 点达到 $2n-1$ 阶精度
  $$\int_{-1}^1 f(x)\,dx \approx \sum_{i=1}^n w_i f(x_i)$$
  $x_i$ = Legendre 多项式的根

### 1.4 ODE 数值解

- **初值问题**：$\dot{y} = f(t, y)$, $y(0) = y_0$
- **单步法**：Euler / RK4
  - Euler：$y_{n+1} = y_n + hf(t_n, y_n)$，精度 $O(h)$
  - RK4：四级 Runge-Kutta，精度 $O(h^4)$
- **稳定性**：刚性方程需要隐式方法（BDF, implicit Euler）
- **自适应步长**：误差估计 → 步长控制

### 1.5 有限元方法（FEM）★（ETH 强项）

**核心思想**：把 PDE 弱形式化，在有限维子空间中求解。

**热方程** $\Delta u = f$ 的 FEM：
1. **弱形式**：$\int \nabla u \cdot \nabla v = \int fv$ 对所有测试函数 $v$
2. **离散化**：$u_h = \sum c_i \phi_i$，$\phi_i$ 是基函数（"帐篷函数"）
3. **线性系统**：$Kc = F$，$K_{ij} = \int \nabla\phi_i \cdot \nabla\phi_j$（刚度矩阵）

### 1.6 有限差分法（FDM）

- 网格上用差分近似导数：$u''(x) \approx \frac{u(x-h) - 2u(x) + u(x+h)}{h^2}$
- 稳定性条件（CFL 条件）：$\Delta t \leq C \Delta x^2$（显式热方程）

### 1.7 谱方法 ★

- 用三角函数/Chebyshev 多项式全局逼近
- **指数收敛**（对光滑解）：误差 $\sim e^{-cn}$
- **FFT** 加速 → $O(n \log n)$

---

## 二、代码层

### 2.1 有限差分法解热方程

```python
import numpy as np
import matplotlib.pyplot as plt

L, T = 1.0, 0.05
Nx, Nt = 50, 5000
dx, dt = L/Nx, T/Nt
r = dt / dx**2  # CFL: r < 0.5 for stability
assert r < 0.5

x = np.linspace(0, L, Nx+1)
u = np.zeros(Nx+1)
u[Nx//2 - 3:Nx//2 + 3] = 1.0  # 初始脉冲

for n in range(Nt):
    u_new = u.copy()
    u_new[1:-1] = u[1:-1] + r * (u[2:] - 2*u[1:-1] + u[:-2])
    u = u_new

plt.plot(x, u); plt.title(f'热方程 t={T} (有限差分)')
plt.savefig('fdm_heat.png', dpi=150)
```

### 2.2 Gauss 求积

```python
import numpy as np

def gauss_legendre_quadrature(f, a, b, n):
    """n 点 Gauss-Legendre 求积"""
    nodes, weights = np.polynomial.legendre.leggauss(n)
    # 变换 [-1,1] → [a,b]
    t = 0.5*(b-a)*nodes + 0.5*(a+b)
    return 0.5*(b-a) * np.sum(weights * f(t))

# 精确: ∫_0^1 e^x dx = e - 1 ≈ 1.71828
for n in [1, 2, 3, 5, 10]:
    approx = gauss_legendre_quadrature(np.exp, 0, 1, n)
    exact = np.e - 1
    print(f"n={n:2d}: {approx:.12f}, 误差 = {abs(approx-exact):.2e}")
# n=5 已达到机器精度！
```

---

## 三、与 ML 的联系

### 3.1 数值优化 → 训练算法
线搜索、信赖域 → Adam/L-BFGS 的理论基础。

### 3.2 FEM/FDM → PINN 和 Neural Operators
PDE 的数值方法启发了用神经网络解 PDE（PINN, Fourier Neural Operator [2010.08895](https://arxiv.org/abs/2010.08895) ✅）。

### 3.3 Chebyshev 逼近 → 谱归一化
GAN 的谱归一化约束 Lipschitz 常数——与数值分析中的算子范数估计相关。

### 3.4 CG/GMRES → 大规模线性系统
自然语言处理中的注意力矩阵求逆可用 Krylov 子空间方法加速。

---

## 四、推荐路径

1. **Quarteroni** 第 1-5 章：插值 + 积分 + ODE → **核心**
2. **第 7-8 章**：FEM/FDM → **ETH CSE 核心**
3. **第 10 章**：谱方法 + FFT → 高精度方法
4. **交叉**：[UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)（数值线代）+ [Princeton MAT 322](../../princeton-math-courses/mat322_pde/)（PDE 理论）
