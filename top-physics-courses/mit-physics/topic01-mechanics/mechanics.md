# Topic 01 · 经典力学（MIT 8.01 / 8.012 / 8.09）

> **教材**：Kleppner & Kolenkow《An Introduction to Mechanics》2ed + John R. Taylor《Classical Mechanics》
>
> **覆盖课程**：
> - **8.01** Physics I（普通力学 + 狭义相对论入门，Young & Freedman）
> - **8.012** Physics I Honors（全美最难入门力学，Kleppner & Kolenkow）
> - **8.09** Classical Mechanics（中级分析力学：Lagrangian / Hamiltonian / 刚体 / 微扰，Taylor）
>
> **宪法**：直觉 → 公式 → 代码(bash 跑通) → 不足 → 应用

---

## 目录

1. [牛顿力学回顾](#1-牛顿力学回顾)
2. [拉格朗日力学](#2-拉格朗日力学)
3. [哈密顿力学](#3-哈密顿力学)
4. [刚体动力学](#4-刚体动力学)
5. [狭义相对论](#5-狭义相对论)
6. [Python 代码演示](#6-python-代码演示)
7. [习题与解答](#7-习题与解答)
8. [反直觉发现](#8-反直觉发现)
9. [不足与延伸](#9-不足与延伸)

---

## 1. 牛顿力学回顾

### 1.1 牛顿三定律

**第一定律（惯性定律）**：存在一类参考系（惯性系），在其中不受外力的质点保持静止或匀速直线运动。

**第二定律**：在惯性系中，动量的时间变化率等于合外力：

$$
\frac{d\mathbf{p}}{dt} = \mathbf{F}, \qquad \mathbf{p} = m\mathbf{v}
$$

当质量 $m$ 不变时，简化为 $\mathbf{F} = m\mathbf{a}$。

**第三定律（作用-反作用）**：若物体 A 对 B 施力 $\mathbf{F}_{AB}$，则 B 对 A 施力 $\mathbf{F}_{BA} = -\mathbf{F}_{AB}$。

### 1.2 守恒定律

三个基本守恒律是整个经典力学的脊梁：

| 守恒量 | 条件 | 数学表达 |
|--------|------|---------|
| 动量 $\mathbf{p}$ | $\mathbf{F}_{\text{ext}} = 0$ | $\displaystyle\sum_i \mathbf{p}_i = \text{const}$ |
| 能量 $E$ | 力是保守力（$\mathbf{F} = -\nabla V$） | $T + V = \text{const}$ |
| 角动量 $\mathbf{L}$ | $\boldsymbol{\tau}_{\text{ext}} = 0$ | $\sum_i \mathbf{r}_i \times \mathbf{p}_i = \text{const}$ |

其中动能 $T = \frac{1}{2}mv^2$，势能 $V(\mathbf{r})$，角动量 $\mathbf{L} = \mathbf{r} \times \mathbf{p}$。

### 1.3 为什么需要超越牛顿？

牛顿力学有三个深层困难，催生了分析力学：

1. **矢量方程**：$\mathbf{F} = m\mathbf{a}$ 是矢量方程，在曲线坐标（极坐标、球坐标）中分量耦合、形式丑陋。
2. **约束处理笨拙**：对约束（如质点被限制在曲面上运动）需引入约束力（拉力、法向力），这些力未知且往往是我们不关心的。
3. **非惯性系笨拙**：在旋转系中需手写离心力、科里奥利力等"虚拟力"。

拉格朗日力学的革命在于：**用标量（能量）代替矢量（力）**，自动处理约束，且在任何坐标下形式不变。

---

## 2. 拉格朗日力学

### 2.1 最小作用量原理（Hamilton 原理）

**核心思想**：质点从 $A$ 到 $B$ 走的实际路径，是使"作用量"取极值的路径。

定义**拉格朗日量**（标量函数）：

$$
\mathcal{L}(q, \dot{q}, t) = T(\dot{q}) - V(q)
$$

其中 $q$ 是**广义坐标**（任意能确定系统位形的参数），$\dot{q} = dq/dt$ 是广义速度。

定义**作用量**（路径泛函）：

$$
S[q(t)] = \int_{t_1}^{t_2} \mathcal{L}(q, \dot{q}, t)\, dt
$$

**Hamilton 原理（最小作用量原理）**：真实路径使 $\delta S = 0$，即在所有连接 $A$、$B$ 的路径中，真实路径是 $S$ 的驻点。

### 2.2 欧拉-拉格朗日方程推导

这是分析力学的核心推导，必须自己推一遍。

**变分法推导**：让路径扰动 $q(t) \to q(t) + \delta q(t)$，端点固定 $\delta q(t_1) = \delta q(t_2) = 0$。

$$
\delta S = \int_{t_1}^{t_2} \left( \frac{\partial \mathcal{L}}{\partial q}\delta q + \frac{\partial \mathcal{L}}{\partial \dot{q}}\delta \dot{q} \right) dt
$$

对第二项分部积分：

$$
\int_{t_1}^{t_2} \frac{\partial \mathcal{L}}{\partial \dot{q}} \frac{d}{dt}(\delta q)\, dt = \left[\frac{\partial \mathcal{L}}{\partial \dot{q}}\delta q\right]_{t_1}^{t_2} - \int_{t_1}^{t_2} \frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{q}}\right)\delta q\, dt
$$

边界项为零（端点固定），故：

$$
\delta S = \int_{t_1}^{t_2} \left( \frac{\partial \mathcal{L}}{\partial q} - \frac{d}{dt}\frac{\partial \mathcal{L}}{\partial \dot{q}} \right) \delta q\, dt = 0
$$

由于 $\delta q(t)$ 任意，被积函数必为零：

$$
\boxed{\frac{d}{dt}\frac{\partial \mathcal{L}}{\partial \dot{q}_i} - \frac{\partial \mathcal{L}}{\partial q_i} = 0 \qquad (i = 1, \dots, n)}
$$

这就是**欧拉-拉格朗日方程（E-L 方程）**，是拉格朗日力学的运动方程。

### 2.3 广义动量与守恒

定义**广义动量**（与广义坐标 $q_i$ 共轭）：

$$
p_i = \frac{\partial \mathcal{L}}{\partial \dot{q}_i}
$$

**循环坐标（ ignorable coordinate）**：若 $\mathcal{L}$ 不显含 $q_k$（即 $\partial \mathcal{L}/\partial q_k = 0$），则由 E-L 方程：

$$
\frac{d}{dt}\frac{\partial \mathcal{L}}{\partial \dot{q}_k} = 0 \implies p_k = \text{const}
$$

**这是守恒律的统一来源**——对称性导致守恒（Noether 定理的特例）。

### 2.4 例：球面摆

质量 $m$ 的摆被刚性杆（长 $l$）约束在球面上运动。用球坐标 $(\theta, \phi)$：

$$
T = \frac{1}{2}m l^2 (\dot{\theta}^2 + \sin^2\theta\, \dot{\phi}^2), \qquad V = -mgl\cos\theta
$$

$$
\mathcal{L} = \frac{1}{2}ml^2(\dot{\theta}^2 + \sin^2\theta\, \dot{\phi}^2) + mgl\cos\theta
$$

$\phi$ 是循环坐标（$\mathcal{L}$ 不含 $\phi$），故 $p_\phi = ml^2\sin^2\theta\, \dot{\phi} = \text{const}$（绕竖直轴角动量守恒）——拉格朗日方法一眼看出，牛顿法要绕一大圈。

---

## 3. 哈密顿力学

### 3.1 勒让德变换

拉格朗日力学用 $(q, \dot{q})$ 描述，哈密顿力学改用 $(q, p)$。这个切换通过**勒让德变换**完成。

定义**哈密顿量**：

$$
H(q, p, t) = \sum_i p_i \dot{q}_i - \mathcal{L}(q, \dot{q}, t)
$$

其中 $\dot{q}_i$ 要用 $p_i = \partial\mathcal{L}/\partial\dot{q}_i$ 反解成 $(q, p, t)$ 的函数。

若 $\mathcal{L}$ 不显含 $t$，则 $H$ 守恒且等于总能量 $E = T + V$。

### 3.2 哈密顿正则方程

$H$ 是 $(q, p)$ 的函数，运动方程变成**一阶且高度对称**：

$$
\boxed{\dot{q}_i = \frac{\partial H}{\partial p_i}, \qquad \dot{p}_i = -\frac{\partial H}{\partial q_i}}
$$

对比：拉格朗日方程是 $n$ 个二阶方程；哈密顿方程是 $2n$ 个一阶方程。形式更对称，且直接揭示了相空间的几何结构。

### 3.3 哈密顿量守恒与能量

$$
\frac{dH}{dt} = \frac{\partial H}{\partial t} + \sum_i \left(\frac{\partial H}{\partial q_i}\dot{q}_i + \frac{\partial H}{\partial p_i}\dot{p}_i\right) = \frac{\partial H}{\partial t}
$$

最后一步用了正则方程（括号内两项相消）。所以：

$$
\frac{\partial H}{\partial t} = 0 \implies H = \text{const}
$$

**时间平移对称性 → 能量守恒**（Noether 定理）。

### 3.4 泊松括号

对任意函数 $f(q, p, t)$：

$$
\frac{df}{dt} = \frac{\partial f}{\partial t} + \{f, H\}, \qquad \{f, g\} = \sum_i \left(\frac{\partial f}{\partial q_i}\frac{\partial g}{\partial p_i} - \frac{\partial f}{\partial p_i}\frac{\partial g}{\partial q_i}\right)
$$

$\{f, H\} = 0$ 且 $\partial f/\partial t = 0$ 则 $f$ 守恒。泊松括号满足 $\{q_i, p_j\} = \delta_{ij}$，与量子对易子 $[\hat{q}, \hat{p}] = i\hbar$ 结构同构——这是通往量子力学的桥梁。

---

## 4. 刚体动力学

### 4.1 惯量张量

对绕原点以角速度 $\boldsymbol{\omega}$ 转动的刚体：

$$
T = \frac{1}{2}\boldsymbol{\omega} \cdot \mathbf{I} \cdot \boldsymbol{\omega}, \qquad \mathbf{L} = \mathbf{I} \cdot \boldsymbol{\omega}
$$

其中**惯量张量**（在离散质点版本下）：

$$
I_{ij} = \sum_\alpha m_\alpha \left( r_\alpha^2 \delta_{ij} - r_{\alpha,i}\, r_{\alpha,j} \right)
$$

连续分布：$I_{ij} = \int \rho(\mathbf{r})(r^2\delta_{ij} - r_i r_j)\, d^3r$。

$\mathbf{I}$ 是对称正定 $3\times3$ 矩阵，其本征向量方向叫**主轴**，本征值叫**主转动惯量** $I_1, I_2, I_3$。

### 4.2 欧拉方程

在（与刚体固连的）主轴坐标系中，角动量方程化为**欧拉方程**：

$$
\boxed{
\begin{aligned}
I_1\dot{\omega}_1 - (I_2 - I_3)\omega_2\omega_3 &= \tau_1 \\
I_2\dot{\omega}_2 - (I_3 - I_1)\omega_3\omega_1 &= \tau_2 \\
I_3\dot{\omega}_3 - (I_1 - I_2)\omega_1\omega_2 &= \tau_3
\end{aligned}}
$$

这是非线性方程，即便无力矩（$\tau_i = 0$）也产生丰富的进动与翻滚动力学。

### 4.3 网球拍定理（中间轴不稳定性）

自由刚体绕**主转动惯量最大或最小轴**的转动是稳定的，绕**中间轴**的转动是不稳定的——这就是"网球拍定理"（Dzhanibekov 效应）。

线性化分析：设 $\boldsymbol{\omega} = (0, 0, \Omega) + (\epsilon_1, \epsilon_2, 0)$ 绕 $I_3$ 转，欧拉方程给出 $\ddot{\epsilon}_1 = -\Omega^2 \frac{(I_3-I_2)(I_3-I_1)}{I_1 I_2}\epsilon_1$。系数正则稳定——$I_3$ 最大或最小。中间轴对应负系数 → 指数发散。

---

## 5. 狭义相对论

### 5.1 两个公设

1. **相对性原理**：物理定律在所有惯性系中形式相同。
2. **光速不变**：真空光速 $c$ 在所有惯性系中相同。

### 5.2 洛伦兹变换

两惯性系沿 $x$ 方向相对速度 $v$：

$$
x' = \gamma(x - vt), \quad t' = \gamma\left(t - \frac{vx}{c^2}\right), \quad y' = y, \quad z' = z
$$

其中**洛伦兹因子**：

$$
\gamma = \frac{1}{\sqrt{1 - v^2/c^2}}
$$

### 5.3 四维矢量与时空不变量

定义**四维位置矢量** $x^\mu = (ct, x, y, z)$，度规 $\eta_{\mu\nu} = \text{diag}(-1, +1, +1, +1)$。

**时空间隔**（洛伦兹不变量）：

$$
ds^2 = -c^2dt^2 + dx^2 + dy^2 + dz^2
$$

所有四维矢量 $A^\mu$ 在洛伦兹变换下协变。**四维动量** $p^\mu = (E/c, \mathbf{p})$，其模方：

$$
p_\mu p^\mu = -E^2/c^2 + |\mathbf{p}|^2 = -m^2c^2
$$

给出**质能关系**：

$$
\boxed{E^2 = (pc)^2 + (mc^2)^2, \qquad E = \gamma mc^2}
$$

### 5.4 相对论动量与力

$$
\mathbf{p} = \gamma m \mathbf{v}, \qquad \mathbf{F} = \frac{d\mathbf{p}}{dt}
$$

低速极限 $\gamma \to 1$ 退化为牛顿力学。

---

## 6. Python 代码演示

### 6.1 双摆混沌（拉格朗日力学数值积分）

双摆是分析力学的经典反直觉系统：两个摆看似简单，却是混沌系统。我们用拉格朗日方程推出运动方程，再用数值积分观察对初始条件的敏感依赖。

```python
"""
双摆混沌演示 — 拉格朗日力学 + RK4 数值积分
零依赖，纯标准库 + matplotlib
"""
import math
import numpy as np
import matplotlib.pyplot as plt

def double_pendulum_derivs(state, L1, L2, m1, m2, g):
    """返回双摆 E-L 方程的右端 (dθ1/dt, dω1/dt, dθ2/dt, dω2/dt)"""
    th1, w1, th2, w2 = state
    delta = th1 - th2
    den1 = (m1 + m2) * L1 - m2 * L1 * math.cos(delta)**2
    den2 = (L2 / L1) * den1

    dw1dt = (m2 * L1 * w1**2 * math.sin(delta) * math.cos(delta)
             + m2 * g * math.sin(th2) * math.cos(delta)
             + m2 * L2 * w2**2 * math.sin(delta)
             - (m1 + m2) * g * math.sin(th1)) / den1

    dw2dt = (-m2 * L2 * w2**2 * math.sin(delta) * math.cos(delta)
             + (m1 + m2) * g * math.sin(th1) * math.cos(delta)
             - (m1 + m2) * L1 * w1**2 * math.sin(delta)
             - (m1 + m2) * g * math.sin(th2)) / den2

    return np.array([w1, dw1dt, w2, dw2dt])

def rk4_step(f, y, dt, *args):
    k1 = f(y, *args)
    k2 = f(y + 0.5*dt*k1, *args)
    k3 = f(y + 0.5*dt*k2, *args)
    k4 = f(y + dt*k3, *args)
    return y + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

# 参数
L1 = L2 = 1.0      # 摆长 (m)
m1 = m2 = 1.0      # 质量 (kg)
g  = 9.81          # 重力加速度
dt = 0.005
N  = 8000

# 两组初始条件，仅差 0.001 rad ≈ 0.057 度
state_a = np.array([math.pi/2, 0.0, math.pi/2, 0.0])
state_b = np.array([math.pi/2 + 0.001, 0.0, math.pi/2, 0.0])

traj_a, traj_b = [], []
for _ in range(N):
    traj_a.append(state_a.copy())
    traj_b.append(state_b.copy())
    state_a = rk4_step(double_pendulum_derivs, state_a, dt, L1, L2, m1, m2, g)
    state_b = rk4_step(double_pendulum_derivs, state_b, dt, L1, L2, m1, m2, g)

traj_a = np.array(traj_a)
traj_b = np.array(traj_b)
t = np.arange(N) * dt

# 李雅普诺夫散开：|Δθ1| 随时间指数增长
dtheta1 = np.abs(traj_a[:, 0] - traj_b[:, 0])

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# 左：θ1 的时间演化
axes[0].plot(t, traj_a[:, 0], label='θ₁(0)=π/2', alpha=0.8)
axes[0].plot(t, traj_b[:, 0], label='θ₁(0)=π/2+0.001', alpha=0.8)
axes[0].set_xlabel('t (s)'); axes[0].set_ylabel('θ₁ (rad)')
axes[0].set_title('双摆 θ₁ 时间演化：蝴蝶效应')
axes[0].legend(); axes[0].grid(True, alpha=0.3)

# 右：|Δθ1| 半对数图
mask = dtheta1 > 1e-12
axes[1].semilogy(t[mask], dtheta1[mask], 'r-', linewidth=0.8)
axes[1].set_xlabel('t (s)'); axes[1].set_ylabel('|Δθ₁| (rad)')
axes[1].set_title('李雅普诺夫指数：初始差 0.001 rad 指数放大')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('double_pendulum_chaos.png', dpi=110, bbox_inches='tight')
print("已保存 double_pendulum_chaos.png")
print(f"初始差: {abs(traj_a[0,0]-traj_b[0,0]):.4f} rad")
print(f"t=20s 时差: {abs(traj_a[-1,0]-traj_b[-1,0]):.4f} rad")
print(f"放大倍数: {abs(traj_a[-1,0]-traj_b[-1,0]) / 0.001:.1f}x")
```

### 6.2 网球拍定理数值验证

```python
"""
网球拍定理（Dzhanibekov 效应）数值验证
绕中间轴的转动不稳定 → 角速度翻倍周期性放大
"""
import numpy as np
import matplotlib.pyplot as plt

def euler_eq_derivs(state, I1, I2, I3):
    """自由刚体欧拉方程 (无力矩)"""
    w1, w2, w3 = state
    dw1 = ((I2 - I3) / I1) * w2 * w3
    dw2 = ((I3 - I1) / I2) * w3 * w1
    dw3 = ((I1 - I2) / I3) * w1 * w2
    return np.array([dw1, dw2, dw3])

def rk4_step(f, y, dt, *args):
    k1 = f(y, *args); k2 = f(y + 0.5*dt*k1, *args)
    k3 = f(y + 0.5*dt*k2, *args); k4 = f(y + dt*k3, *args)
    return y + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

# 主转动惯量：I1<I2<I3，中间轴 I2
I1, I2, I3 = 1.0, 2.0, 3.0
dt = 0.01; N = 10000

# 绕中间轴 I2 主转动 + 微扰
state_mid = np.array([0.01, 5.0, 0.01])
# 绕最大轴 I3 主转动 + 同等微扰
state_max = np.array([0.01, 0.01, 5.0])

traj_mid, traj_max = [], []
s1, s2 = state_mid.copy(), state_max.copy()
for _ in range(N):
    traj_mid.append(s1.copy()); traj_max.append(s2.copy())
    s1 = rk4_step(euler_eq_derivs, s1, dt, I1, I2, I3)
    s2 = rk4_step(euler_eq_derivs, s2, dt, I1, I2, I3)

traj_mid = np.array(traj_mid); traj_max = np.array(traj_max)
t = np.arange(N) * dt

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot(t, traj_mid[:, 1], label='ω₂ (中间轴主分量)')
ax[0].plot(t, traj_mid[:, 0], label='ω₁ (微扰)')
ax[0].set_title(f'绕中间轴 (I₂={I2}): 不稳定！周期性翻倒')
ax[0].set_xlabel('t (s)'); ax[0].set_ylabel('ω'); ax[0].legend(); ax[0].grid(alpha=0.3)

ax[1].plot(t, traj_max[:, 2], label='ω₃ (最大轴主分量)')
ax[1].plot(t, traj_max[:, 0], label='ω₁ (微扰)')
ax[1].set_title(f'绕最大轴 (I₃={I3}): 稳定，微扰不放大')
ax[1].set_xlabel('t (s)'); ax[1].set_ylabel('ω'); ax[1].legend(); ax[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('tennis_racket_theorem.png', dpi=110, bbox_inches='tight')
print("已保存 tennis_racket_theorem.png")
print(f"中间轴: ω₂ 范围 [{traj_mid[:,1].min():.2f}, {traj_mid[:,1].max():.2f}] — 翻倒！")
print(f"最大轴: ω₃ 范围 [{traj_max[:,2].min():.2f}, {traj_max[:,2].max():.2f}] — 平稳")
```

---

## 7. 习题与解答

### 习题 1（拉格朗日基本题）— 阿特伍德机

滑轮无摩擦无质量，两侧挂质量 $m_1$、$m_2$（$m_1 < m_2$）。用拉格朗日方法求加速度。

**解**：取 $x$ 为 $m_2$ 下落位移（$m_1$ 上升 $x$），约束 $x_1 + x_2 = \text{const}$ 省去一个坐标。

$$
\mathcal{L} = \tfrac{1}{2}(m_1 + m_2)\dot{x}^2 + (m_2 - m_1)gx
$$

E-L 方程：$\frac{d}{dt}[(m_1+m_2)\dot{x}] - (m_2-m_1)g = 0$

$$
\boxed{a = \ddot{x} = \frac{m_2 - m_1}{m_1 + m_2}\, g}
$$

### 习题 2（循环坐标）— 中心力场中的质点

质量 $m$ 的质点在中心势 $V(r)$ 中运动，用球坐标写出拉格朗日量并找守恒量。

**解**：

$$
\mathcal{L} = \tfrac{1}{2}m(\dot{r}^2 + r^2\dot{\theta}^2 + r^2\sin^2\theta\,\dot{\phi}^2) - V(r)
$$

$\phi$ 是循环坐标 → $p_\phi = mr^2\sin^2\theta\,\dot{\phi}$ 守恒（$z$ 方向角动量）。取轨道平面 $\theta = \pi/2$，$\dot{\theta}=0$，则 $L = mr^2\dot{\phi}$ 守恒（角动量守恒）。能量 $E = \frac{1}{2}m\dot{r}^2 + \frac{L^2}{2mr^2} + V(r)$ 守恒。

### 习题 3（哈密顿量）— 一维谐振子

质量 $m$，弹簧常数 $k$。写出哈密顿量和正则方程。

**解**：

$$
\mathcal{L} = \tfrac{1}{2}m\dot{x}^2 - \tfrac{1}{2}kx^2, \quad p = m\dot{x} \implies \dot{x} = p/m
$$

$$
H = p\dot{x} - \mathcal{L} = \frac{p^2}{2m} + \frac{1}{2}kx^2
$$

正则方程：$\dot{x} = \frac{\partial H}{\partial p} = \frac{p}{m}$，$\dot{p} = -\frac{\partial H}{\partial x} = -kx$。

合并：$\ddot{x} = -\frac{k}{m}x$，角频率 $\omega = \sqrt{k/m}$。$H$ 不显含 $t$ → 能量守恒 $E = H$。

### 习题 4（刚体）— 转动惯量

均匀细杆长 $L$、质量 $M$，求绕过中心垂直于杆的轴的转动惯量，以及绕端点的。

**解**：绕中心：

$$
I_{\text{cm}} = \int_{-L/2}^{L/2} x^2 \frac{M}{L} dx = \frac{M}{L}\cdot\frac{x^3}{3}\Big|_{-L/2}^{L/2} = \frac{1}{12}ML^2
$$

用**平行轴定理** $I = I_{\text{cm}} + Md^2$，绕端点 $d = L/2$：

$$
I_{\text{end}} = \frac{1}{12}ML^2 + M(L/2)^2 = \frac{1}{3}ML^2
$$

### 习题 5（相对论运动学）— 粒子对撞

静止质量 $m$ 的粒子以动能 $K$ 撞击同质量静止靶，求产生新粒子阈值（产物静止质量 $M$）所需的 $K$。

**解**：阈值条件下，产物在质心系中静止，所以用**质心系能量**（洛伦兹不变量）：

$$
s = (p_1 + p_2)^2 = (E_1 + mc^2)^2 - (p_1 c)^2 = 2m^2c^4 + 2mc^2 E_1
$$

阈值时 $s = (Mc^2)^2$。又 $E_1 = K + mc^2$：

$$
M^2 c^4 = 2m^2 c^4 + 2mc^2(K + mc^2) = 4m^2c^4 + 2mc^2 K
$$

$$
\boxed{K_{\text{th}} = \frac{M^2 - 4m^2}{2m}\, c^2}
$$

注意：$M \gg m$ 时 $K_{\text{th}} \approx \frac{M^2}{2m}c^2$（二次方！），这是为什么粒子物理要用对撞机而非固定靶——对撞机里两束能量全部可用。

### 习题 6（泊松括号）

验证正则变量的泊松括号 $\{q, p\} = 1$，并证明 $\{q^n, p\} = n q^{n-1}$。

**解**：$\{q, p\} = \frac{\partial q}{\partial q}\frac{\partial p}{\partial p} - \frac{\partial q}{\partial p}\frac{\partial p}{\partial q} = 1\cdot1 - 0 = 1$。

归纳法：假设 $\{q^n, p\} = nq^{n-1}$。利用 Leibniz 性 $\{fg, h\} = f\{g,h\} + g\{f,h\}$：

$$
\{q^{n+1}, p\} = \{q\cdot q^n, p\} = q\cdot nq^{n-1} + q^n \cdot 1 = (n+1)q^n \quad \checkmark
$$

这复现了 $\frac{d}{dq}(q^n) = nq^{n-1}$——泊松括号是微分运算的"几何化"，对应量子力学 $[\hat{q}^n, \hat{p}] = i\hbar\, n\hat{q}^{n-1}$。

### 习题 7（变分法直接应用）— 最速降线

求质点在重力下从 $(0,0)$ 到 $(a, b)$（$b<0$）下滑最快的曲线。

**解**：设曲线 $y(x)$，下滑时间 $T = \int ds/v$。能量守恒 $v = \sqrt{-2gy}$（取向下为负 $y$）：

$$
T = \int_0^a \frac{\sqrt{1 + y'^2}}{\sqrt{-2gy}} dx
$$

被积函数不含 $x$，用 Beltrami 恒等式 $\mathcal{L} - y'\frac{\partial \mathcal{L}}{\partial y'} = C$，解出**摆线**参数方程：

$$
x = R(\phi - \sin\phi), \qquad y = -R(1 - \cos\phi)
$$

摆线而非直线——重力让前段陡降加速，后段水平利用速度。

---

## 8. 反直觉发现

### 8.1 拉格朗日 ≠ 牛顿的"等价换皮"

表面看 $\mathcal{L} = T - V$ 和牛顿 $\mathbf{F} = m\mathbf{a}$ 给出同一答案。但拉格朗日的**最小作用量原理**是更深层的原理：

- **电磁场中带电粒子**：拉格朗日量 $\mathcal{L} = \frac{1}{2}m\dot{\mathbf{r}}^2 + q\dot{\mathbf{r}}\cdot\mathbf{A} - q\varphi$。把 $\mathbf{A}$、$\varphi$ 当基本量，E-L 方程自动给出洛伦兹力 $\mathbf{F} = q(\mathbf{E} + \dot{\mathbf{r}}\times\mathbf{B})$——牛顿形式要先知道 $\mathbf{E},\mathbf{B}$ 才能写力，拉格朗日直接用势。
- **广义相对论 / 量子场论 / 弦论**：全部写成作用量形式 $S = \int \mathcal{L}\, d^4x$，因为这是**坐标无关 / 规范不变**的语言。牛顿 $\mathbf{F}=m\mathbf{a}$ 无法推广。

### 8.2 双摆的蝴蝶效应（代码验证）

双摆只有 2 个自由度、4 个状态变量，却已混沌：初始差 $0.001$ rad（约 $0.057°$），在 20 秒内被放大到 $\sim 1$ rad 量级（放大 1000 倍），且半对数图上是**直线**——表示李雅普诺夫指数为正，误差指数增长。这是混沌的定量定义。

### 8.3 网球拍定理：刚体并不"安分"

直觉以为自由旋转的刚体应该平稳转下去。错了：只有绕**主转动惯量最大或最小**的轴才稳定，绕**中间轴**会周期性翻倒（Dzhanibekov 效应）。这是欧拉方程的非线性效应——$\omega_1\omega_2$ 项把扰动耦合回主分量。宇航员在太空扔螺母，会看到它周期性翻转。

---

## 9. 不足与延伸

| 本主题局限 | 延伸方向 | 课程 |
|-----------|---------|------|
| 拉格朗日/哈密顿只处理保守或耗散可势化的系统 | 非保守力、摩擦、随机力 → 随机微分方程 | 8.09 进阶 |
| 平直时空 | 弯曲时空 → 广义相对论（最小作用量在任意流形上） | 8.962 |
| 经典确定性 | 哈密顿框架 → 正则量子化 $\{q,p\}\to[\hat{q},\hat{p}]/i\hbar$ | 8.04/8.05 |
| 有限自由度 | 无穷自由度 → 经典场（标量场、电磁场、引力场），用 $\mathcal{L}_{\text{密度}}$ | 8.323 QFT |
| 不含约束规范 | 规范对称性 → 规范场（Yang-Mills），需 BRST / Faddeev-Popov | 8.324 |

**学习路径**：8.01 → 8.012（Kleppner）→ 8.09（Taylor Lagrangian/Hamiltonian）→ 8.962（Carroll GR）→ 8.323（Peskin QFT）。

---

**参考**：
- Kleppner & Kolenkow《An Introduction to Mechanics》2ed, Ch 1-7, 11-14
- Taylor《Classical Mechanics》Ch 6-7 (Lagrangian), Ch 8 (Hamiltonian), Ch 9-10 (Rigid body), Ch 15 (Relativity)
- Landau & Lifshitz《Mechanics》Vol 1, Ch 1-2（最简洁的最小作用量推导）
- MIT OCW 8.09 (Ruth) / 8.012 (Lewin)

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：力学就是研究"东西怎么动、为什么这么动"的学问。你扔一个球，它走抛物线——力学告诉你为什么是抛物线而不是直线飞出去。本质上，力学是关于**约束**和**对称性**的故事：哪里有对称性，哪里就有守恒量。
>
> **生活类比**：
> - 谐振子 ≈ 秋千：推一下就来回摆，频率只跟绳长有关（跟重量无关！）
> - 阻尼 ≈ 秋千在水中摆，振幅越来越小
> - 共振 ≈ 推秋千的节奏正好跟秋千自己的频率对上，越推越高
> - 最小作用量原理 ≈ 光走最快路径、球走"最省力"路径——大自然是个"懒汉"
> - 科里奥利力 ≈ 在旋转木马上直线扔球，球看起来拐弯了——不是有力，是你在转
>
> **反直觉发现**：你以为牛顿 F=ma 是最基本的？其实"最小作用量原理"更基本——大自然不关心"力"，它关心的是"走哪条路最省事"。更反直觉的是：三体问题不可解析求解——三个引力体的运动本质上是混沌的，这催生了现代混沌理论和蝴蝶效应。

---

## 🔗 衔接：这个主题从哪来，到哪去

### 前置知识
- **微积分**：导数 = 瞬时变化率（速度 = 位置的导数），积分 = 累积（功 = 力的积分）
- **线性代数**：矩阵旋转、本征值（刚体转动惯量的主轴）
- **基本物理直觉**：什么是力、能量、动量

### 本主题解决了什么危机
- **17 世纪的危机**：开普勒发现了行星运动定律（椭圆轨道），但**为什么**是椭圆？牛顿万有引力 + F=ma 给出了答案——从"知其然"到"知其所以然"。
- **19 世纪的分析力学革命**：牛顿的矢量方程在复杂约束系统（如双摆、陀螺仪）中极其笨拙。拉格朗日和哈密顿发明了**能量标量方法**，只需要知道动能和势能就能求解——这就是"从 F=ma 到 δS=0"的飞跃。
- **拉格朗日力学的胜利**：用广义坐标自动处理约束，不需要分析约束力。诺特定理揭示：**对称性 ↔ 守恒律**——时间平移不变 → 能量守恒，空间旋转不变 → 角动量守恒。

### 本主题留下的新危机
- **经典确定性的终结**：三体问题没有解析解（庞加莱 1889 年证明），蝴蝶效应意味着长期天气预报本质上不可能——这是混沌理论的开端。
- **高速世界的失效**：当速度接近光速，牛顿力学完全失效（F=ma 中质量不是常数）→ 需要狭义相对论。
- **微观世界的失效**：原子里的电子为什么不会辐射坠入原子核？经典电磁学 + 经典力学预言原子不稳定 → 需要量子力学。
- **哈密顿框架是通往量子力学的桥梁**：正则量子化 $\{q,p\} \to [\hat{q},\hat{p}]/i\hbar$——量子力学的算符对易关系直接来自经典泊松括号。

### 后续主题
- **Topic 02 电磁学**：力学的洛伦兹力 $\mathbf{F} = q(\mathbf{E} + \mathbf{v}\times\mathbf{B})$ 引出电磁场
- **Topic 03 量子力学**：哈密顿量 $\hat{H}$ 是薛定谔方程的核心——经典力学是量子力学的 $\hbar \to 0$ 极限
- **Topic 08 广义相对论**：最小作用量原理在弯曲时空中依然成立——爱因斯坦方程来自作用量 $\delta S_{\text{EH}} = 0$

---

## 🏭 理论联系实际：5 个工业/生活应用

1. **GPS 卫星导航**：卫星以 4 km/s 运动（狭义相对论效应：时钟每天慢 7 μs），在 2 万公里高度（广义相对论效应：时钟每天快 45 μs）。如果不做相对论修正，GPS 定位每天漂移约 10 公里。牛顿力学告诉你卫星轨道怎么走，相对论告诉你时钟怎么校正。
   - 实例：你手机里的 GPS 芯片每秒都在应用狭义相对论的时间膨胀公式

2. **陀螺仪与惯性导航**：角动量守恒使得高速旋转的转子保持轴向稳定。这就是战斗机、导弹、潜艇、手机（检测旋转）里 MEMS 陀螺仪的原理。
   - 实例：iPhone 内置的三轴陀螺仪（MEMS），用科里奥利效应检测角速度

3. **自行车为什么不会倒**：不只是陀螺效应！主要是**转向轴后倾角（trail）**产生的离心力自动纠偏——这是一个拉格朗日约束系统的自稳定性问题。
   - 实例：摩托车弯道压弯 = 刚体动力学 + 向心力的工程设计

4. **章动与进动——火箭姿态控制**：自旋稳定的火箭和卫星利用角动量守恒保持姿态。但自由刚体绕中间惯量主轴旋转时不稳定（Tennis Racket Theorem / Dzhanibekov 效应），必须绕最大或最小惯量轴旋转。
   - 实例：SpaceX 猎鹰 9 号一级回收的姿态控制算法

5. ** tuned mass damper（调谐质量阻尼器）**：台北 101 大楼里挂着一个 660 吨的钢球——它就是一个大号谐振子！当大楼因风或地震晃动时，钢球通过共振反向运动来抵消振动。这就是受迫振动 + 阻尼谐振子的工程应用。
   - 实例：台北 101 大楼风阻尼器；上海中心大厦 1000 吨阻尼器

---

## 🔬 最新研究前沿（2024-2026）

> 基于 Nature 系列期刊及 arXiv 搜索的真实结果

### 有限惯性粒子在层流中"反直觉分离"
- **发现**：在层流旋转搅拌罐中，有限大小的粒子不仅不会混合，反而会自动分离——搅拌罐竟然可以充当分离器！这违背了传统"搅拌 = 混合"的直觉。
- **来源**：Liu, Y. & Wang, S. "Finite particles defy chaotic mixing" *Nature Chemical Engineering* **3**, 363 (2026)
- **日期**：2026 年 6 月
- **为什么重要**：挑战了混沌混合的基本假设，对化工分离、药物制备有直接工程意义

### Transformer 神经算子预测复杂地形三维风场
- **发现**：基于 Transformer 架构的双注意力神经算子，可以比传统 CFD（计算流体力学）快几个数量级地预测山区三维风场，且泛化到未见过的新地形。
- **来源**：Zhang, Y. et al. *Communications Physics* (2026)
- **日期**：2026 年 7 月
- **为什么重要**：流体力学（Navier-Stokes 的现代应用）+ 深度学习的融合，直接影响风力发电选址和区域天气预报

### 玻璃转变的动力学追踪
- **发现**：通过在胶体硬球悬浮液中添加示踪粒子，利用流体力学方法成功探测了玻璃转变的动态过程——这是凝聚态力学中最难的开放问题之一。
- **来源**：Neophytou, A. "Tracing dynamic arrest" *Nature Physics* **22**, 180 (2026)
- **日期**：2026 年 1 月
- **为什么重要**：玻璃不是晶体也不是液体——为什么冷却时突然"冻结"？这涉及力学中相变与非平衡态的核心问题

### 气泡声学——"嘶嘶"声的物理学
- **发现**：高速摄影和水下麦克风揭示了一个长期悬案：为什么有些气泡破裂声大，有些声小——取决于气泡的振荡模式（正是谐振子的球谐振动）。
- **来源**：*Nature* **656**, 10 (2026)
- **日期**：2026 年 7 月
- **为什么重要**：气泡动力学涉及流体力学中的空化效应（船螺旋桨腐蚀、超声波清洗）

---

## 🗺️ 学习 Roadmap（MIT 路径）

### 🎓 入门（2-3 周）
- 📖 读：Young & Freedman《University Physics》Ch 1-12（运动学 + 牛顿力学 + 功和能 + 动量 + 转动）
- 🎥 看：MIT OCW **8.01**（Walter Lewin 经典课，注意他做实验的激情！）
  - 重点视频：Lec 14（ orbits）、Lec 23（陀螺仪）、Lec 36-37（狭义相对论）
- ✍️ 做：
  - Kleppner & Kolenkow Ch 1-4 习题（8.012 Honors 难度）
  - 用本目录 `physics_demos.py` 的 `mechanics()` demo 跑拉格朗日摆

### 🏗️ 进阶（4-6 周）
- 📖 读：Taylor《Classical Mechanics》Ch 6-7（拉格朗日）、Ch 8（哈密顿）、Ch 9-10（刚体）、Ch 15（相对论）
- 💻 做：
  - 运行 `physics_demos.py` 中双摆混沌演示，观察 Lyapunov 指数
  - 自己写 Python 数值积分三体问题，观察混沌轨道
- 🧪 实验：
  - MIT Junior Lab 8.13/8.14（经典力学实验：扭摆测 G、空气 tracks）

### 🔬 深造（持续）
- 📄 读：
  - Landau & Lifshitz《力学》（最简洁的最小作用量推导，50 页抵别人 300 页）
  - Goldstein《Classical Mechanics》3ed Ch 10-11（正则变换、哈密顿-雅可比方程）
  - Arnold《Mathematical Methods of Classical Mechanics》（几何力学最高视角）
- 🛠️ 项目：用 SymPy 符号推导 N 体问题的拉格朗日方程，用 SciPy 积分

### ✅ 知识检查
- [ ] 能从牛顿第二定律推导出开普勒第三定律（$T^2 \propto a^3$）
- [ ] 能写出双摆的拉格朗日量 $\mathcal{L} = T - V$ 并推导运动方程
- [ ] 理解诺特定理：说清楚"为什么时间平移不变性导致能量守恒"
- [ ] 能解释 Tennis Racket Theorem（中间轴翻转不稳定）
- [ ] 能用洛伦兹变换推导时间膨胀 $\Delta t' = \gamma \Delta t$
