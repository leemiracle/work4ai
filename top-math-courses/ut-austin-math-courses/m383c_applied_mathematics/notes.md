# UT Austin M 383C · 应用数学 精读笔记

> **课程**：Applied Mathematics (Graduate, M 383C)
> **教材**：Logan, *Applied Mathematics*；Strang, *Computational Science and Engineering*
> **参考**：[utexas.edu/math](https://www.ma.utexas.edu/)；Bender & Orszag, *Advanced Mathematical Methods*

---

## 〇、费曼直觉层

> **应用数学 = 连接数学理论与物理/工程问题的桥梁。**

M 383C 是 UT Austin 应用数学研究生核心课，覆盖面极广：**量纲分析 → 渐近方法 → 积分变换 → 变分法 → 微扰论**。不是单一主题的深入课，而是**应用数学的工具箱**。

### 与其他课的关系

| 主题 | 详细笔记在哪 |
|---|---|
| PDE | [Princeton MAT 322](../../princeton-math-courses/mat322_pde/) |
| 复分析 | [Berkeley 185](../../berkeley-math-courses/math185_complex_analysis/) |
| 数值线代 | [M 383E Trefethen](../../ut-austin-math-courses/m383e_numerical_linear_algebra/) |
| 凸优化 | [Stanford CME 364A Boyd](../../stanford-math-courses/cme364A_convex_optimization/) |

本课独特覆盖：**量纲分析、渐近展开、变分法**——这些在其他课中很少系统讲解。

---

## 一、核心主题

### 1.1 量纲分析与标度 ★

**Buckingham $\pi$ 定理**：物理定律可以用无量纲量表示。

**例子**：阻力 $F$ 依赖速度 $v$、密度 $\rho$、面积 $A$。量纲分析 → $F = C \rho v^2 A$（$C$ 是无量纲常数，由实验/理论确定）。

**ML 应用**：Neural Scaling Laws 的量纲分析（参数量、数据量、计算量之间的标度关系）。

### 1.2 渐近展开 ★

**动机**：精确解不了时，用小参数 $\epsilon$ 展开。

**正则微扰**：$y = y_0 + \epsilon y_1 + \epsilon^2 y_2 + \cdots$

**奇异微扰** ★：正则展开失效（如边界层）→ 需要**匹配渐近展开**。

**例子**：$\epsilon y'' + y' + y = 0$, $y(0)=0$, $y(1)=1$。$\epsilon \to 0$ 时退化为一阶方程，丢失一个边界条件 → 出现**边界层**。

### 1.3 积分变换

- **Fourier 变换**：$\hat{f}(\omega) = \int f(t)e^{-i\omega t}dt$
- **Laplace 变换**：$F(s) = \int_0^\infty f(t)e^{-st}dt$
- **应用**：把微分方程化为代数方程 → 解代数方程 → 逆变换

### 1.4 变分法 ★

**问题**：求使泛函 $J[y] = \int_a^b L(x, y, y')\,dx$ 取极值的函数 $y(x)$。

**Euler-Lagrange 方程** ★：
$$\frac{\partial L}{\partial y} - \frac{d}{dx}\frac{\partial L}{\partial y'} = 0$$

**应用**：
- 最速降线问题（Brachistochrone）
- 测地线（广义相对论）
- **ML**：变分推断（VAE）的 ELBO 推导

### 1.5 特征函数展开

- **Sturm-Liouville 理论** ★：$\frac{d}{dx}\left[p(x)\frac{dy}{dx}\right] + [\lambda w(x) - q(x)]y = 0$
- 特征函数正交完备 → 广义 Fourier 展开
- 这是 PDE 分离变量的理论基础

### 1.6 Green 函数

参见 [Princeton MAT 322 PDE notes.md](../../princeton-math-courses/mat322_pde/) §1.7。

点源响应函数 → 任意源的解 = Green 函数卷积。

### 1.7 摄动理论与稳定性分析

- **线性稳定性**：扰动 $e^{\lambda t}$，$\mathrm{Re}(\lambda) > 0$ → 不稳定
- **分岔理论**：参数变化导致解的定性变化（鞍-结分岔、Hopf 分岔）

---

## 二、代码层

### 2.1 量纲分析与 Neural Scaling Law

```python
import numpy as np

# Kaplan et al. (OpenAI 2020): L(N, D) ≈ A/N^α + B/D^β
# 量纲分析: 损失 L 应该是参数量 N 和数据量 D 的幂律组合
# 与 Buckingham π 定理一致: 无量纲量之间的关系

N = np.logspace(8, 12, 50)  # 参数量
D = np.logspace(8, 12, 50)  # token 数
alpha, beta = 0.076, 0.095  # Chinchilla 拟合值
L_N = 1.0 / N**alpha
L_D = 1.0 / D**beta
print(f"参数量 N: 10^8 → 10^12, 损失∝ N^{-α} (α={alpha})")
print(f"数据量 D: 10^8 → 10^12, 损失∝ D^{-β} (β={beta})")
print("→ 量纲分析 + 实验 → Neural Scaling Laws")
```

### 2.2 Euler-Lagrange 方程

```python
# 最速降线: 使下落时间最短的曲线
# L = sqrt((1+y'^2)/(2gy)), Euler-Lagrange → 摆线参数方程
import matplotlib.pyplot as plt
theta = np.linspace(0, np.pi, 100)
# 摆线: x = r(θ - sinθ), y = r(1 - cosθ)
r = 1.0
x = r * (theta - np.sin(theta))
y = r * (1 - np.cos(theta))
plt.plot(x, -y); plt.title('最速降线 = 摆线')
plt.savefig('brachistochrone.png', dpi=150)
```

### 2.3 奇异微扰 — 边界层

```python
# εy'' + y' + y = 0, y(0)=0, y(1)=1
# 外解 (ε→0): y' + y = 0 → y = Ce^{-x}, C = e (由 y(1)=1)
# 内解 (边界层在 x=0): 尺度 ξ = x/ε
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 1, 200)
for eps in [0.5, 0.1, 0.01, 0.001]:
    # 精确解 (常数系数 ODE)
    r1, r2 = [(-1 + np.sqrt(1 - 4*eps))/(2*eps),
               (-1 - np.sqrt(1 - 4*eps))/(2*eps)]
    C1, C2 = np.linalg.solve([[1, 1], [r1, r2]], [0, 1])
    y = C1 * np.exp(r1*x) + C2 * np.exp(r2*x)
    plt.plot(x, y, label=f'ε={eps}')
plt.legend(); plt.title('奇异微扰: 边界层随 ε→0 变窄')
plt.savefig('boundary_layer.png', dpi=150)
```

---

## 三、与 ML 的联系

### 3.1 变分法 → VAE / ELBO
$$\mathcal{L}_{\text{ELBO}} = \mathbb{E}_{q}[\log p(x|z)] - \mathrm{KL}(q(z|x)\|p(z))$$
ELBO 是一个泛函，VAE 用变分法优化 $q(z|x)$。

### 3.2 渐近分析 → 大模型缩放律
Neural Scaling Laws 本质是渐近展开——大参数/大数据的极限行为。

### 3.3 稳定性分析 → GAN 训练
GAN 的纳什均衡稳定性分析使用动力系统的分岔理论工具。

### 3.4 特征函数展开 → 核方法
核矩阵的特征分解 = 离散的 Sturm-Liouville 问题 → 核岭回归的泛化分析。

---

## 四、推荐路径

1. **Logan** 第 1-3 章：量纲分析 + 渐近方法 + 微扰论 → **本课独特价值**
2. **第 4-5 章**：变分法 + 特征函数 → 与 PDE/优化交叉
3. **Bender-Orszag**：渐近方法的经典参考（WKB、最速下降法等）
4. **交叉**：[Princeton MAT 322 PDE](../../princeton-math-courses/mat322_pde/) + [Berkeley 185 复分析](../../berkeley-math-courses/math185_complex_analysis/)
