# UC Berkeley MATH 54 · ODE 部分章节笔记

> **教材**：Lay, Lay, McDonald, *Linear Algebra and Its Applications*（ODE 部分用配套补充材料）
> **范围**：本笔记**只覆盖 ODE 部分**（第 7-10 单元）。线代部分见其他笔记
> **对照**：ODE 内容与 [MIT 18.03](../../mit-math-courses/18_03_differential_equations/) 等价但更紧凑

---

## 核心框架：ODE 的四个层级

| 层级 | 数学形式 | ML 对应 |
|---|---|---|
| **1. 一阶 ODE** | $\dot{x} = f(x,t)$ | Neural ODE |
| **2. 二阶 ODE** | $\ddot{x} + p\dot{x} + qx = 0$ | 阻尼振荡 |
| **3. 线性系统** | $\dot{\mathbf{x}} = A\mathbf{x}$ | RNN / Mamba SSM |
| **4. Laplace 变换** | $\mathcal{L}\{f\}(s)$ | 信号处理 |

---

## 第 1 节：一阶 ODE

### 1.1 可分离变量

$$\frac{dx}{dt} = g(x)h(t) \implies \int\frac{dx}{g(x)} = \int h(t)\,dt$$

### 1.2 一阶线性 ODE

$$\dot{x} + p(t)x = q(t)$$

积分因子 $\mu = e^{\int p\,dt}$，解：$x = \mu^{-1}\int\mu q\,dt + C/\mu$。

### 1.3 ML 关联

Neural ODE（[arXiv:1806.07366](https://arxiv.org/abs/1806.07366)）：$\dot{\mathbf{h}} = f_\theta(\mathbf{h}, t)$。ResNet 是其 Euler 离散化（$\Delta t = 1$）。

---

## 第 2 节：二阶线性 ODE

### 2.1 常系数齐次

$$\ddot{x} + p\dot{x} + qx = 0$$

特征方程 $r^2 + pr + q = 0$：

| 判别式 | 通解 | 行为 |
|---|---|---|
| $p^2 > 4q$ | $c_1e^{r_1t} + c_2e^{r_2t}$ | 过阻尼 |
| $p^2 = 4q$ | $(c_1 + c_2t)e^{rt}$ | 临界阻尼 |
| $p^2 < 4q$ | $e^{\alpha t}(c_1\cos\beta t + c_2\sin\beta t)$ | 欠阻尼振荡 |

### 2.2 非齐次

待定系数法 / 参数变易法。共振：外力频率 = 自然频率时振幅线性增长。

---

## 第 3 节：线性 ODE 系统 ★★★

### 3.1 标准形式

$$\dot{\mathbf{x}} = A\mathbf{x}$$

### 3.2 矩阵指数解

$$\mathbf{x}(t) = e^{At}\mathbf{x}(0)$$

若 $A = P\Lambda P^{-1}$，则 $e^{At} = Pe^{\Lambda t}P^{-1}$。

### 3.3 特征值与稳定性

| 特征值 | 行为 | ML 关联 |
|---|---|---|
| $\text{Re}(\lambda) < 0$ | 稳定（收敛） | 模型收敛 |
| $\text{Re}(\lambda) > 0$ | 不稳定（发散） | 训练发散 |
| 纯虚数 $\pm i\omega$ | 中心振荡 | 周期行为 |

### 3.4 ML 关联：Mamba SSM ★

Mamba（[arXiv:2312.00752](https://arxiv.org/abs/2312.00752)）：

$$\dot{\mathbf{h}}(t) = A\mathbf{h}(t) + B\mathbf{x}(t), \quad \mathbf{y}(t) = C\mathbf{h}(t)$$

这是线性常系数 ODE + 输入项。ZOH 离散化 → RNN：$\mathbf{h}_k = \bar{A}\mathbf{h}_{k-1} + \bar{B}\mathbf{x}_k$。

---

## 第 4 节：Laplace 变换

### 4.1 核心性质

$$\mathcal{L}\{f'(t)\} = sF(s) - f(0)$$

微分方程 → 代数方程 → 求解 → 逆变换。

### 4.2 常用变换对

| $f(t)$ | $F(s)$ |
|---|---|
| $e^{at}$ | $1/(s-a)$ |
| $\sin\omega t$ | $\omega/(s^2+\omega^2)$ |
| $\delta(t)$ | $1$ |
| $u(t-a)$（阶跃） | $e^{-as}/s$ |

---

## 与 ML 的关联总表

| MATH 54 (ODE) 概念 | ML 应用 |
|---|---|
| 一阶 ODE | Neural ODE |
| Euler 法 | ResNet |
| 线性系统 | Mamba / SSM |
| 特征值稳定性 | RNN 梯度问题 |
| Laplace 变换 | 控制 / 信号处理 |

---

## 代码验证

### 验证 1：Euler vs 解析解

```python
import numpy as np

# dx/dt = -x + t, x(0) = 0
f = lambda x, t: -x + t
x, h = 0.0, 0.1
trajectory = [(0, x)]
t = 0
for _ in range(50):
    x = x + h * f(x, t)
    t += h
    trajectory.append((t, x))
# 解析解: x(t) = t - 1 + e^{-t}
exact = t - 1 + np.exp(-t)
print(f"Euler: x(5)={trajectory[-1][1]:.4f}, 精确解: {exact:.4f}")
```

### 验证 2：特征值与稳定性

```python
import numpy as np

# 线性系统 dx/dt = Ax
systems = {
    "稳定节点 (λ<0)": np.array([[-3, 0], [0, -1]]),
    "不稳定 (λ>0)": np.array([[2, 0], [0, -1]]),
    "螺旋稳定 (复λ)": np.array([[-0.5, 2], [-2, -0.5]]),
    "中心点 (纯虚λ)": np.array([[0, 1], [-4, 0]]),
}

for name, A in systems.items():
    eigvals = np.linalg.eigvals(A)
    max_real = max(eigvals.real)
    status = "稳定" if max_real < 0 else ("不稳定" if max_real > 0 else "临界")
    print(f"{name}: λ={np.round(eigvals, 2)}, {status}")
```

### 验证 3：共振——受迫振荡

```python
import numpy as np

# mx'' + cx' + kx = F₀cos(ωt)
# 当 ω → ω₀ = √(k/m) 时，振幅→∞（共振）
m, k = 1.0, 4.0  # ω₀ = 2
c = 0.2           # 小阻尼
F0 = 1.0
omega0 = np.sqrt(k/m)

for omega in [1.0, 1.5, 2.0, 2.5, 3.0]:
    # 稳态振幅: A = F0 / √((k - mω²)² + (cω)²)
    A = F0 / np.sqrt((k - m*omega**2)**2 + (c*omega)**2)
    marker = " ← 共振!" if abs(omega - omega0) < 0.1 else ""
    print(f"ω={omega:.1f}: 稳态振幅={A:.2f}{marker}")
```

---

## 深度专题：线性 ODE 与 Mamba/SSM

### 状态空间模型 = 线性 ODE 离散化

Mamba [arXiv:2312.00752] 基于连续状态空间模型：

$$h'(t) = Ah(t) + Bx(t), \quad y(t) = Ch(t)$$

零阶保持（ZOH）离散化（步长 $\Delta$）：

$$\bar{A} = e^{A\Delta}, \quad \bar{B} = (e^{A\Delta} - I)A^{-1}B$$

离散递推：$h_{k+1} = \bar{A}h_k + \bar{B}x_k$

### 特征值决定记忆衰减

$\bar{A} = e^{A\Delta}$ 的特征值 $= e^{\lambda_i \Delta}$。

- $\text{Re}(\lambda_i) < 0$ → $|e^{\lambda_i\Delta}| < 1$ → 状态衰减（遗忘）
- $|e^{\lambda_i\Delta}| \approx 1$ → 长记忆
- Mamba 的核心创新：让 $A, B, C$ 依赖输入（选择性机制）

### 与 RNN 梯度问题的联系

RNN 的梯度递推：$\frac{\partial L}{\partial h_k} = \bar{A}^T \frac{\partial L}{\partial h_{k+1}}$

若 $\bar{A}$ 的特征值绝对值 $> 1$：梯度爆炸（$\to \infty$）

若 $< 1$：梯度消失（$\to 0$）

**MATH 54 的线性系统稳定性直接解释了 RNN 的梯度问题**。

---

## 深度专题：Laplace 变换与信号处理

### 从时域到频域

Laplace 变换：$\mathcal{L}\{f(t)\} = F(s) = \int_0^\infty f(t)e^{-st}dt$

将微分方程变为代数方程：

$$\mathcal{L}\{x'(t)\} = sX(s) - x(0)$$

### 传递函数与系统响应

线性系统 $x'' + 2\zeta\omega_0 x' + \omega_0^2 x = u(t)$ 的传递函数：

$$H(s) = \frac{\omega_0^2}{s^2 + 2\zeta\omega_0 s + \omega_0^2}$$

- 极点 $s = -\zeta\omega_0 \pm \omega_0\sqrt{\zeta^2 - 1}$ 决定系统行为
- $\zeta > 1$：过阻尼（两个实根）
- $\zeta = 1$：临界阻尼（重根）
- $\zeta < 1$：欠阻尼振荡（复根）

**ML 联系**：Attention 中的 softmax 可以看作频率域滤波——将注意力权重视为频域权重。

---

## 不足与局限

| 方法 | 局限 | 更高级处理 |
|---|---|---|
| 解析求解 | 多数 ODE 无解析解 | 数值方法 (RK4) |
| Euler 法 | 低精度，刚性不稳定 | 隐式法 / RK45 |
| 特征值分析 | 仅局部（线性化附近） | 全局相平面 |
| Laplace 变换 | 需线性常系数 | 数值 Laplace / 时频分析 |

---

## 与 work4ai 讲透系列的交叉

- **讲透 Neural ODE**：一阶 ODE + Euler（第 1 节）
- **讲透 Mamba/SSM**：线性系统 + 离散化（第 3 节）
- **讲透 RNN 梯度问题**：线性系统特征值稳定性（第 3 节）
- **讲透扩散模型**：SDE + Fokker-Planck（第 4 节）
- **讲透信号处理**：Laplace 变换 / 传递函数（第 5 节）
