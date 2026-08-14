# UT Austin M 378K · 数值分析 精读笔记

> **课程**：Numerical Analysis (Undergraduate)
> **教材**：Burden & Faires, *Numerical Analysis*；或 Atkinson, *An Introduction to Numerical Analysis*
> **参考**：[utexas.edu/math](https://www.ma.utexas.edu/)

---

## 〇、费曼直觉层

> **数值分析 = 用有限的计算机资源，近似求解连续数学问题。**

M 378K 是本科数值分析入门课，覆盖面广但深度适中。与 [Oxford Part A A12](../../oxford-math-courses/partA_a12_numerical_analysis/) 和 [Cambridge Part IB NA](../../cambridge-math-courses/partIB_numerical_analysis/) 同级。研究生级深度参见 [M 383E Trefethen & Bau](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)。

---

## 一、核心主题（Burden-Faires 体系）

### 1.1 数学预备与误差

- **浮点数系统**：IEEE 754 标准，机器精度 $\epsilon_{\text{mach}}$
- **误差传播**：前向/后向误差分析
- **条件数**：问题对输入扰动的敏感度

### 1.2 一元方程求根

| 方法 | 收敛阶 | 需要导数？ |
|---|---|---|
| 二分法 | 线性 (1) | 否 |
| 不动点迭代 | 线性 (1) | 否 |
| **Newton 法** ★ | 二次 (2) | 是 |
| 割线法 | 超线性 (1.618) | 否 |

### 1.3 插值与逼近

- **Lagrange/Newton 插值** → 参见 [Oxford A12](../../oxford-math-courses/partA_a12_numerical_analysis/)
- **Hermite 插值**：同时匹配函数值和导数
- **三次样条**：分段三次多项式，$C^2$ 连续

### 1.4 数值微分与积分

- **数值微分**：前向/中心差分，精度与步长的权衡
- **复化求积**：复化梯形 / 复化 Simpson
- **Gauss 求积**：最优节点 → 最高代数精度
- **自适应积分**：根据局部误差估计自动加密

### 1.5 ODE 初值问题

- **Euler 方法**（显式/隐式）
- **Runge-Kutta 方法**：RK4 = 四级四阶
- **多步法**：Adams-Bashforth（显式）/ Adams-Moulton（隐式）
- **预测-校正**：AB-AM 配对
- **刚性方程**：需要隐式方法（A-稳定性）

### 1.6 直接法解线性系统

- **高斯消元 + 部分选主元** → LU 分解
- **Cholesky 分解**：对称正定矩阵
- **条件数** → 参见 [Oxford A12](../../oxford-math-courses/partA_a12_numerical_analysis/)

### 1.7 迭代法

- **Jacobi / Gauss-Seidel**：不动点迭代解 $Ax=b$
- **收敛条件**：对角占优或对称正定
- **SOR（逐次超松弛）**：加速收敛

---

## 二、代码层

### 2.1 RK4 vs Euler

```python
import numpy as np

def f(t, y): return -y  # y' = -y, 解 y = e^{-t}

def euler(f, t0, y0, T, h):
    t, y = t0, y0
    while t < T:
        y += h * f(t, y); t += h
    return y

def rk4(f, t0, y0, T, h):
    t, y = t0, y0
    while t < T:
        k1 = f(t, y); k2 = f(t+h/2, y+h*k1/2)
        k3 = f(t+h/2, y+h*k2/2); k4 = f(t+h, y+h*k3)
        y += h/6 * (k1 + 2*k2 + 2*k3 + k4); t += h
    return y

T, exact = 1.0, np.exp(-1.0)
for h in [0.1, 0.01, 0.001]:
    e = abs(euler(f, 0, 1, T, h) - exact)
    r = abs(rk4(f, 0, 1, T, h) - exact)
    print(f"h={h:.3f}: Euler 误差={e:.2e}, RK4 误差={r:.2e}")
# Euler: O(h), RK4: O(h^4) — RK4 快得多
```

### 2.2 Gauss-Seidel 迭代

```python
def gauss_seidel(A, b, x0, tol=1e-10, max_iter=1000):
    n = len(b); x = x0.copy()
    for it in range(max_iter):
        x_old = x.copy()
        for i in range(n):
            x[i] = (b[i] - A[i,:i]@x[:i] - A[i,i+1:]@x[i+1:]) / A[i,i]
        if np.linalg.norm(x - x_old) < tol: break
    return x, it

A = np.array([[4,1,0],[1,3,1],[0,1,2]], dtype=float)
b = np.array([1,2,3], dtype=float)
x, iters = gauss_seidel(A, b, np.zeros(3))
print(f"解 = {x}, 迭代次数 = {iters}")
```

---

## 三、与 ML 的联系

参见 [Oxford A12 notes.md §3](../../oxford-math-courses/partA_a12_numerical_analysis/)。核心要点：
- 条件数 → 训练数值稳定性
- Newton 法 → 牛顿型优化
- 迭代法 → 大规模优化
- ODE 求解器 → Neural ODE

---

## 四、推荐路径

1. **Burden-Faires 第 1-6 章**：误差 + 求根 + 插值 + 积分 + ODE → **核心**
2. **第 7 章**：直接法解线性系统 → 基础
3. **进阶**：[M 383E Trefethen & Bau](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)（数值线代招牌课）
4. **交叉**：[ETH 401-2611 CSE NA](../../eth-math-courses/e401_2611_numerical_methods_cse/)（PDE 方向）
