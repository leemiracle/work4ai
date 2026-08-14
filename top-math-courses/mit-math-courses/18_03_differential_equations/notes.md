# MIT 18.03 · 章节笔记

> **教材**：Boyce & DiPrima, *Elementary Differential Equations*；Edwards & Penney
> **视频**：OCW 18.03 Prof. Arthur Mattuck 33 讲 — ocw.mit.edu/courses/18-03-differential-equations-spring-2010
> **定位**：从静态到动态——ODE 是 Neural ODE、扩散模型、RNN/SSM 的数学根基

---

## 核心框架：ODE 的"四层金字塔"

| 层级 | 数学形式 | ML 对应 |
|---|---|---|
| **1. 一阶标量 ODE** | $\dot{x} = f(x, t)$ | Neural ODE 单变量版 |
| **2. 二阶 ODE** | $\ddot{x} + p\dot{x} + qx = 0$ | 阻尼振荡 / 物理仿真 |
| **3. 线性系统** | $\dot{\mathbf{x}} = A\mathbf{x}$ | 连续 RNN / Mamba SSM |
| **4. 数值求解** | Euler / RK4 | ODE solver = Neural ODE 的引擎 |

---

## 第 1 章：一阶 ODE（First-Order ODE）★★

### 1.1 直觉

> **比喻**：ODE 是"知道你的速度表读数，还原你的位置轨迹"。$\dot{x} = f(x,t)$ 意味着"在状态 $x$、时刻 $t$，你的瞬时速度是 $f(x,t)$"——ODE solver 就是从速度信息重建轨迹。

### 1.2 可分离变量

$$\frac{dx}{dt} = g(x)h(t) \implies \int \frac{dx}{g(x)} = \int h(t)\,dt$$

### 1.3 一阶线性 ODE

$$\dot{x} + p(t)x = q(t)$$

**积分因子法**：设 $\mu(t) = e^{\int p\,dt}$，则：

$$\frac{d}{dt}[\mu x] = \mu q \implies x(t) = \frac{1}{\mu}\int \mu q\,dt + \frac{C}{\mu}$$

### 1.4 ML 关联：Neural ODE ★★★

Neural ODE（[arXiv:1806.07366](https://arxiv.org/abs/1806.07366)）的核心方程：

$$\frac{d\mathbf{h}(t)}{dt} = f_\theta(\mathbf{h}(t), t), \quad \mathbf{h}(0) = \mathbf{x}$$

- 用 ODE solver 从 $\mathbf{h}(0)$ 积分到 $\mathbf{h}(T)$ 得到输出
- 训练用**伴随方法（adjoint method）**反向传播，内存 $O(1)$
- ResNet $\mathbf{h}_{l+1} = \mathbf{h}_l + f(\mathbf{h}_l)$ 是其 Euler 离散化（$\Delta t = 1$）

---

## 第 2 章：二阶线性 ODE（Second-Order Linear ODE）

### 2.1 标准形式

$$\ddot{x} + p\dot{x} + qx = 0$$

### 2.2 特征方程法

设 $x = e^{rt}$，代入得特征方程：

$$r^2 + pr + q = 0$$

三种情况：

| 判别式 | 根 | 通解 | 物理意义 |
|---|---|---|---|
| $p^2 - 4q > 0$ | 两个实根 $r_1 \neq r_2$ | $c_1 e^{r_1 t} + c_2 e^{r_2 t}$ | 过阻尼 |
| $p^2 - 4q = 0$ | 重根 $r$ | $(c_1 + c_2 t)e^{rt}$ | 临界阻尼 |
| $p^2 - 4q < 0$ | 复根 $\alpha \pm i\beta$ | $e^{\alpha t}(c_1\cos\beta t + c_2\sin\beta t)$ | **振荡** |

### 2.3 阻尼振荡

$$x(t) = Ae^{-\gamma t}\cos(\omega t + \phi)$$

- $\gamma > 0$：振幅指数衰减（稳定）
- $\gamma = 0$：等幅振荡（无阻尼）

### 2.4 非齐次：待定系数 / 共振

外力频率 = 自然频率时发生**共振**，振幅线性增长。

---

## 第 3 章：线性 ODE 系统（Linear Systems）★★★

### 3.1 直觉

> **比喻**：单个二阶 ODE 可以拆成两个一阶 ODE 组成的系统——就像把"位置+速度"当作状态向量 $\mathbf{x} = (x, \dot{x})$。

### 3.2 标准形式

$$\dot{\mathbf{x}} = A\mathbf{x}, \quad \mathbf{x} \in \mathbb{R}^n$$

### 3.3 矩阵指数解 ★

$$\mathbf{x}(t) = e^{At}\mathbf{x}(0)$$

其中 $e^{At} = \sum_{k=0}^\infty \frac{(At)^k}{k!}$。

**对角化**：若 $A = P\Lambda P^{-1}$，则 $e^{At} = Pe^{\Lambda t}P^{-1}$。

### 3.4 特征值与稳定性 ★★★

$A$ 的特征值 $\lambda_i$ 决定系统行为：

| 特征值 | 行为 | 相图 | ML 关联 |
|---|---|---|---|
| $\text{Re}(\lambda) < 0$ | 收敛到原点（稳定） | 吸引子 | 模型收敛 |
| $\text{Re}(\lambda) > 0$ | 发散（不稳定） | 排斥子 | 训练发散 |
| $\lambda = \alpha \pm i\beta$ | 螺旋 | 螺旋 | 振荡训练 |

### 3.5 ML 关联：Mamba / SSM = 线性 ODE ★

Mamba（[arXiv:2312.00752](https://arxiv.org/abs/2312.00752)）的状态空间模型：

$$\dot{\mathbf{h}}(t) = A\mathbf{h}(t) + B\mathbf{x}(t), \quad \mathbf{y}(t) = C\mathbf{h}(t) + D\mathbf{x}(t)$$

这是一个**线性常系数 ODE**（输入 $\mathbf{x}(t)$ 作为外力）。ZOH 离散化后变成 RNN：

$$\mathbf{h}_k = \bar{A}\mathbf{h}_{k-1} + \bar{B}\mathbf{x}_k$$

Mamba 的创新：让 $A, B$ 依赖输入 $\mathbf{x}$（即 ODE 系数时变/非线性化）。

---

## 第 4 章：Laplace 变换

### 4.1 定义

$$\mathcal{L}\{f(t)\}(s) = F(s) = \int_0^\infty e^{-st}f(t)\,dt$$

### 4.2 核心性质：微分 → 乘法

$$\mathcal{L}\{f'(t)\} = sF(s) - f(0)$$

**意义**：把微分方程变成**代数方程**，求解后逆变换回来。

### 4.3 常用变换

| $f(t)$ | $F(s)$ |
|---|---|
| $1$ | $1/s$ |
| $e^{at}$ | $1/(s-a)$ |
| $\sin(\omega t)$ | $\omega/(s^2+\omega^2)$ |
| $\delta(t)$（冲激） | $1$ |

---

## 第 5 章：数值方法（Numerical Methods）★★★

### 5.1 Euler 法

$$x_{n+1} = x_n + h \cdot f(x_n, t_n)$$

- 最简单，$O(h)$ 精度（一阶）
- 是 ResNet 的数学原型

### 5.2 Runge-Kutta 4（RK4）

$$x_{n+1} = x_n + \frac{h}{6}(k_1 + 2k_2 + 2k_3 + k_4)$$

其中：
- $k_1 = f(x_n, t_n)$
- $k_2 = f(x_n + \frac{h}{2}k_1,\ t_n + \frac{h}{2})$
- $k_3 = f(x_n + \frac{h}{2}k_2,\ t_n + \frac{h}{2})$
- $k_4 = f(x_n + hk_3,\ t_n + h)$

- $O(h^4)$ 精度，是 Neural ODE 的默认 solver

### 5.3 ML 关联

- **Neural ODE** 用 RK45（自适应步长 RK4）求解
- **扩散模型采样**：DDPM 用 Euler 离散化反向 SDE；DPM-Solver 用高阶方法加速

---

## 第 6 章：非线性系统与稳定性

### 6.1 相平面分析

对 $\dot{x} = f(x,y)$，$\dot{y} = g(x,y)$，在 $(x,y)$ 平面画向量场 $(f,g)$，看轨迹走向。

### 6.2 平衡点线性化

在平衡点 $(x^*, y^*)$（$f = g = 0$）附近，Jacobian 矩阵：

$$J = \begin{pmatrix}f_x & f_y\\g_x & g_y\end{pmatrix}_{(x^*,y^*)}$$

$J$ 的特征值决定平衡点类型（节点/鞍点/螺旋/中心）。

### 6.3 Lyapunov 函数

若存在 $V(x)$ 使 $\dot{V} < 0$（沿轨迹递减），则平衡点稳定。

**ML 关联**：损失函数本身可视为一种 Lyapunov 函数——训练使损失递减。

---

## 与 ML 的关联总表

| 18.03 概念 | ML 应用 | 具体公式 |
|---|---|---|
| 一阶 ODE | **Neural ODE** | $\dot{\mathbf{h}} = f_\theta(\mathbf{h}, t)$ |
| Euler 法 | ResNet | $\mathbf{h}_{l+1} = \mathbf{h}_l + f(\mathbf{h}_l)$ |
| RK4 | Neural ODE solver | $O(h^4)$ 精度积分 |
| 线性系统 | **Mamba / SSM** | $\dot{\mathbf{h}} = A\mathbf{h} + B\mathbf{x}$ |
| 特征值稳定性 | RNN 梯度爆炸/消失 | $\|\lambda\| > 1$ → 不稳定 |
| 热传导 PDE | **扩散模型 DDPM** | $\partial_t u = D\nabla^2 u$ |
| Laplace 变换 | 控制 / 信号处理 | 频域分析 |

---

## 代码验证

### 验证 1：Euler vs RK4 精度对比

```python
import numpy as np

def euler(f, x0, t):
    """前向 Euler 法"""
    x = np.zeros((len(t), len(x0)))
    x[0] = x0
    for i in range(len(t) - 1):
        h = t[i+1] - t[i]
        x[i+1] = x[i] + h * f(x[i], t[i])
    return x

def rk4(f, x0, t):
    """经典四阶 Runge-Kutta"""
    x = np.zeros((len(t), len(x0)))
    x[0] = x0
    for i in range(len(t) - 1):
        h = t[i+1] - t[i]
        k1 = f(x[i], t[i])
        k2 = f(x[i] + h/2 * k1, t[i] + h/2)
        k3 = f(x[i] + h/2 * k2, t[i] + h/2)
        k4 = f(x[i] + h * k3, t[i] + h)
        x[i+1] = x[i] + h/6 * (k1 + 2*k2 + 2*k3 + k4)
    return x

# dx/dt = -x (解析解: x(t) = e^{-t})
f = lambda x, t: -x
x0 = np.array([1.0])

for h in [0.5, 0.1, 0.01]:
    t = np.arange(0, 2 + h, h)  # 确保 t=2 包含在内
    euler_err = abs(euler(f, x0, t)[-1, 0] - np.exp(-2))
    rk4_err = abs(rk4(f, x0, t)[-1, 0] - np.exp(-2))
    print(f"h={h:.2f}: Euler 误差={euler_err:.2e}, RK4 误差={rk4_err:.2e}")
```

### 验证 2：线性系统稳定性（特征值）

```python
import numpy as np

# 稳定: 特征值实部 < 0
A_stable = np.array([[-2, 0], [0, -1]])
# 不稳定: 有正特征值
A_unstable = np.array([[1, 0], [0, -2]])
# 振荡: 复特征值
A_oscillate = np.array([[0, 1], [-4, 0]])  # λ = ±2i

for name, A in [("stable", A_stable), ("unstable", A_unstable), ("oscillate", A_oscillate)]:
    eigvals = np.linalg.eigvals(A)
    print(f"{name}: 特征值 = {eigvals}, 实部最大 = {max(eigvals.real):.1f}")
```

### 验证 3：Neural ODE = 连续 ResNet

```python
import numpy as np

# f(h) = -h (衰减)，模拟一个简单的 Neural ODE
f = lambda h, t: -h * np.tanh(h**2)  # 非线性"神经网络"

# 用 Euler 法求解（= 单层 ResNet 的连续极限）
h_val, dt = 1.0, 0.1
trajectory = [h_val]
for _ in range(50):
    h_val = h_val + dt * f(h_val, 0)  # Euler step = ResNet layer
    trajectory.append(h_val)
print(f"Neural ODE 最终状态: {trajectory[-1]:.6f}")
print(f"轨迹从 {trajectory[0]:.4f} 衰减到 {trajectory[-1]:.6f}")
```

---

## 不足与局限

| 方法 | 局限 | 更高级的处理 |
|---|---|---|
| Euler 法 | 低精度，刚性方程不稳定 | 隐式法 / RK45 自适应 |
| 解析求解 | 大多数 ODE 无解析解 | 数值方法 |
| 特征值分析 | 仅适用于线性化附近 | 全局相平面 / 分岔理论 |
| Neural ODE | 训练慢（需 ODE solver） | 直接离散化 / Parallel ODE |

---

## 与 work4ai 讲透系列的交叉

- **讲透 Neural ODE**：一阶 ODE + Euler 法（第 1、5 章）
- **讲透扩散模型**：热传导 PDE + SDE（第 6 章）
- **讲透 Mamba/SSM**：线性系统 + ZOH 离散化（第 3 章）
- **讲透 RNN 梯度问题**：线性系统稳定性（第 3 章特征值）
