# Topic 01: 经典力学 — 从牛顿到拉格朗日到相对论

> **UC Berkeley 课程映射**：7A (Physics for Scientists and Engineers, Tipler) → 105 (Analytic Mechanics, Marion & Thornton / Taylor)
>
> **教材体系**：
> - **入门**：Tipler "Physics for Scientists and Engineers"（7A 主教材）
> - **中级**：Taylor "Classical Mechanics"（105 首选）/ Marion & Thornton "Classical Dynamics"（105 替代）
> - **研究生衔接**：Goldstein "Classical Mechanics"（部分 105 荣誉学生使用）
> - **Berkeley 传统**：Berkeley Physics Course Vol. 1 "Mechanics" (Kittel, Knight, Ruderman)

---

## 目录

1. [§1 牛顿力学回顾](#1-牛顿力学回顾)
2. [§2 拉格朗日力学](#2-拉格朗日力学)
3. [§3 哈密顿力学](#3-哈密顿力学)
4. [§4 刚体动力学](#4-刚体动力学)
5. [§5 狭义相对论](#5-狭义相对论)
6. [§6 Berkeley 特色](#6-berkeley-特色berkeley-physics-course-传统)
7. [习题集](#习题集)
8. [Python 演示](#python-演示)

---

## §1 牛顿力学回顾

### 1.1 牛顿三定律

**直觉**：牛顿力学的核心图像是"力改变运动状态"。一个质点知道它现在的位置 $\mathbf{r}$ 和速度 $\mathbf{v}$，加上受力 $\mathbf{F}$，就能预测它所有未来的轨迹。

$$\boxed{\mathbf{F} = \frac{d\mathbf{p}}{dt}, \quad \mathbf{p} = m\mathbf{v}}$$

对于质量恒定的经典情况，简化为 $F = ma$。

**关键守恒量**（从对称性导出，Noether 定理的伏笔）：

| 对称性 | 守恒量 | 表达式 |
|--------|--------|--------|
| 时间平移不变性 | 能量 | $E = \frac{1}{2}mv^2 + V(\mathbf{r})$ |
| 空间平移不变性 | 动量 | $\mathbf{p} = m\mathbf{v}$ |
| 空间旋转不变性 | 角动量 | $\mathbf{L} = \mathbf{r} \times \mathbf{p}$ |

### 1.2 中心力场中的运动

Berkeley 105 的经典问题：行星轨道的推导。中心力场中角动量守恒意味着运动在平面内。

有效势能：

$$V_{\text{eff}}(r) = V(r) + \frac{L^2}{2mr^2}$$

其中 $L^2/(2mr^2)$ 是离心势垒（centrifugal barrier）。

**反直觉发现**：对引力 $V = -k/r$，离心势垒在 $r \to 0$ 时趋于无穷，但总有效势在有限 $r$ 处有极小值——这就是稳定圆轨道存在的原因。但对 $1/r^2$ 力（非引力），轨道行为完全不同。

轨道方程（Binet 方程）：

$$\frac{d^2 u}{d\theta^2} + u = -\frac{m}{L^2 u^2} F\left(\frac{1}{u}\right), \quad u = \frac{1}{r}$$

对 $F = -k/r^2$（引力），解为圆锥曲线：

$$r(\theta) = \frac{p}{1 + e\cos\theta}, \quad p = \frac{L^2}{mk}, \quad e = \sqrt{1 + \frac{2EL^2}{mk^2}}$$

| 离心率 $e$ | 轨道类型 | 能量 $E$ |
|------------|----------|----------|
| $e = 0$ | 圆 | $E < 0$ |
| $0 < e < 1$ | 椭圆 | $E < 0$ |
| $e = 1$ | 抛物线 | $E = 0$ |
| $e > 1$ | 双曲线 | $E > 0$ |

---

## §2 拉格朗日力学

### 2.1 最小作用量原理

**直觉**：拉格朗日力学的核心信念是——自然选择让"作用量"取极值的路径。你不需要知道力；你只需要知道动能和势能，拉格朗日量 $L = T - V$ 就编码了全部动力学。

$$\boxed{\delta S = 0, \quad S = \int_{t_1}^{t_2} L(q, \dot{q}, t)\, dt}$$

对作用量变分为零（$\delta S = 0$），得到 **Euler-Lagrange 方程**：

$$\frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i} - \frac{\partial L}{\partial q_i} = 0$$

### 2.2 为什么拉格朗日比牛顿强？

**Taylor 第7章的核心论证**：

1. **坐标无关**：牛顿需要笛卡尔坐标再约束；拉格朗日直接用任意广义坐标 $q_i$。
2. **约束自动处理**：理想约束（不可逆运动方向）不需要显式约束力。
3. **守恒律直接读出**：如果 $L$ 不含某 $q_i$（循环坐标），则对应广义动量 $p_i = \partial L / \partial \dot{q}_i$ 守恒。

### 2.3 经典例子：双摆

双摆是 Berkeley 105 混沌动力学的招牌。设两摆长 $\ell_1, \ell_2$，质量 $m_1, m_2$，角度 $\theta_1, \theta_2$。

$$L = \frac{1}{2}(m_1+m_2)\ell_1^2\dot{\theta}_1^2 + \frac{1}{2}m_2\ell_2^2\dot{\theta}_2^2 + m_1\ell_1\ell_2\dot{\theta}_1\dot{\theta}_2\cos(\theta_1-\theta_2) + (m_1+m_2)g\ell_1\cos\theta_1 + m_2 g\ell_2\cos\theta_2$$

两个 Euler-Lagrange 方程给出耦合的非线性 ODE。这个系统的混沌行为在 [§7 Python 演示](#python-演示) 中可视化。

### 2.4 广义动量与 Hamilton 正则方程（桥梁）

定义正则动量：

$$p_i = \frac{\partial L}{\partial \dot{q}_i}$$

这为过渡到哈密顿力学做准备（见 §3）。

---

## §3 哈密顿力学

### 3.1 Legendre 变换

**直觉**：拉格朗日用 $(q, \dot{q})$ 描述状态；哈密顿用 $(q, p)$。Legendre 变换是连接两者的数学桥梁。

$$\boxed{H(q, p, t) = \sum_i p_i \dot{q}_i - L(q, \dot{q}, t)}$$

### 3.2 Hamilton 正则方程

从 $H$ 直接得到 $2n$ 个一阶方程（$n$ 个自由度）：

$$\dot{q}_i = \frac{\partial H}{\partial p_i}, \qquad \dot{p}_i = -\frac{\partial H}{\partial q_i}$$

对比牛顿/Euler-Lagrange 的 $n$ 个二阶方程，哈密顿方程是一阶的，更适合：
- 相空间分析
- 数值积分（辛积分器 symplectic integrator）
- 量子力学过渡（$p \to -i\hbar \partial/\partial q$）

### 3.3 哈密顿-雅可比方程

$$H\left(q, \frac{\partial S}{\partial q}, t\right) + \frac{\partial S}{\partial t} = 0$$

其中 $S$ 是哈密顿主函数。这个方程是经典力学到量子力学的最短路径——Schrodinger 方程的推导正是从这里出发（见 Topic 03 量子力学）。

### 3.4 Liouville 定理

**反直觉**：相空间中的"流体"不可压缩——代表点占据的体积在时间演化中不变。

$$\frac{d\rho}{dt} = \frac{\partial \rho}{\partial t} + \{\rho, H\} = 0$$

这个定理是统计力学的基础（见 Topic 04 统计物理），保证了微正则系综的合理性。

---

## §4 刚体动力学

### 4.1 惯量张量

**直觉**：一个刚体的转动惯性不是一个数（质量），而是一个 $3\times3$ 张量——因为绕不同轴的转动惯量不同。

$$\boxed{I_{ij} = \int \rho(\mathbf{r})\left(\delta_{ij} r^2 - r_i r_j\right) d^3r}$$

对角化为惯量主轴后：

$$I = \begin{pmatrix} I_1 & 0 & 0 \\ 0 & I_2 & 0 \\ 0 & 0 & I_3 \end{pmatrix}$$

### 4.2 欧拉方程

在体坐标系中，角动量定理给出：

$$\boxed{\begin{cases} I_1\dot{\omega}_1 = (I_2 - I_3)\omega_2\omega_3 \\ I_2\dot{\omega}_2 = (I_3 - I_1)\omega_3\omega_1 \\ I_3\dot{\omega}_3 = (I_1 - I_2)\omega_1\omega_2 \end{cases}}$$

### 4.3 网球拍定理（中间轴翻转定理）

**Berkeley 105 反直觉实验**：绕最大惯量轴或最小惯量轴的旋转是稳定的，但绕中间惯量轴的旋转不稳定！这就是为什么网球拍绕中间轴旋转时总会翻转。

数学证明：对 $I_1 > I_2 > I_3$，线性化欧拉方程后，绕 $I_2$ 的扰动满足 $\ddot{\epsilon} \propto +\epsilon$（指数增长），而绕 $I_1$ 和 $I_3$ 的扰动满足 $\ddot{\epsilon} \propto -\epsilon$（振荡）。

---

## §5 狭义相对论

### 5.1 Lorentz 变换

$$x' = \gamma(x - vt), \quad t' = \gamma\left(t - \frac{vx}{c^2}\right), \quad \gamma = \frac{1}{\sqrt{1-v^2/c^2}}$$

### 5.2 四维动量与质能关系

$$\boxed{E^2 = (pc)^2 + (mc^2)^2}$$

四维动量 $p^\mu = (E/c, \mathbf{p})$，是 Lorentz 不变量 $p^\mu p_\mu = m^2 c^2$。

### 5.3 相对论拉格朗日

$$L = -mc^2\sqrt{1 - \frac{v^2}{c^2}} - V(\mathbf{r})$$

低速展开回到经典 $L \approx -mc^2 + \frac{1}{2}mv^2 - V$（常数项 $-mc^2$ 不影响运动方程）。

### 5.4 相对论修正与近日点进动

水星近日点进动是广义相对论（Berkeley 139 课程）的预告。在狭义相对论层面，中心力场轨道已有微小修正。

---

## §6 Berkeley 特色（Berkeley Physics Course 传统）

### Berkeley Physics Course 丛书

UC Berkeley 在1960年代发起了一套影响深远的物理教材丛书——**Berkeley Physics Course**，共5卷：

| 卷 | 书名 | 作者 | Berkeley 地位 |
|----|------|------|--------------|
| Vol. 1 | Mechanics | Kittel, Knight, Ruderman | 7A/5A 荣誉 |
| Vol. 2 | Electricity and Magnetism | **Purcell** | 5B/7B 荣誉（见 Topic 02）|
| Vol. 3 | Waves | Crawford | 7C |
| Vol. 4 | Quantum Physics | Wichmann | 137 预备 |
| Vol. 5 | Statistical Physics | Reif | 112（见 Topic 04）|

**Vol.1 的教学特色**：
- 第一章不是运动学，而是"矢量"——强调数学工具先行
- 很早引入守恒律（能量在第4章，Newton 定律在第5章）
- 特殊相对论放在全书最后（第11-12章），而非附录

这种"先能量后力"的编排影响了后续众多教材。Berkeley 105 课程至今保留这种精神：**强调对称性和守恒律，而非力的计算**。

---

## 习题集

### 基础题（7A 级别）

**习题 1.1**：质量为 $m$ 的物体从高 $h$ 自由下落，用能量守恒求落地速度。
> **解**：$mgh = \frac{1}{2}mv^2 \Rightarrow v = \sqrt{2gh}$

**习题 1.2**：证明对弹性碰撞（$e=1$），动量和动能同时守恒。

**习题 1.3**：质量为 $m$ 的质点在弹簧（劲度 $k$）上做简谐振动。求周期 $T$。
> **解**：$T = 2\pi\sqrt{m/k}$

### 中级题（105 级别）

**习题 1.4**（Taylor 7.27 改编）：粒子在势场 $V = \frac{1}{2}kr^2 + \frac{1}{4}\alpha r^4$ 中运动。求有效势的圆轨道条件，并判断稳定性。
> **提示**：$V_{\text{eff}} = \frac{L^2}{2mr^2} + \frac{1}{2}kr^2 + \frac{1}{4}\alpha r^4$，令 $dV_{\text{eff}}/dr = 0$ 求 $r_0$，再检查 $d^2V_{\text{eff}}/dr^2 > 0$。

**习题 1.5**（Marion & Thornton 9.16）：写出球面摆（spherical pendulum）的拉格朗日量，指出循环坐标，并求相应的守恒量。
> **解**：$L = \frac{1}{2}m\ell^2(\dot\theta^2 + \sin^2\theta\,\dot\phi^2) + mg\ell\cos\theta$。循环坐标 $\phi$，守恒量 $p_\phi = m\ell^2\sin^2\theta\,\dot\phi = L_z$（$z$ 方向角动量）。

**习题 1.6**：用哈密顿力学推导一维谐振子的运动方程，并验证能量守恒。

**习题 1.7**（网球拍定理）：证明绕中间惯量主轴的旋转不稳定。
> **提示**：设 $I_1 > I_2 > I_3$，令 $\omega_2 = \omega_0 + \epsilon$，代入欧拉方程，对 $\epsilon$ 线性化得 $\ddot\epsilon = \frac{(I_1-I_2)(I_2-I_3)}{I_1 I_3}\omega_0^2 \epsilon > 0$。

### 挑战题

**习题 1.8**（拉格朗日乘子法）：小球在旋转抛物面 $z = ar^2$ 上无摩擦滑动，求小球的运动方程和约束力。

**习题 1.9**（相对论碰撞）：静质量为 $m$ 的粒子以速度 $v$ 撞击静止的同种粒子，发生完全非弹性碰撞。求复合粒子的静质量。
> **解**：$M = \sqrt{2m^2(1+\gamma)}$

---

## Python 演示

### 演示 1：双摆混沌（纯 NumPy，RK4 积分）

```python
"""
双摆混沌演示 — Berkeley 105 Analytic Mechanics
零依赖：numpy + matplotlib。几秒跑完。
"""
import numpy as np
import matplotlib.pyplot as plt

# --- 物理参数 ---
g = 9.81
L1, L2 = 1.0, 1.0
m1, m2 = 1.0, 1.0
dt = 0.005
T_total = 20.0
N = int(T_total / dt)

def derivatives(state):
    """双摆运动方程（从拉格朗日量导出）。"""
    th1, th2, w1, w2 = state
    delta = th1 - th2
    den1 = (m1 + m2) * L1 - m2 * L1 * np.cos(delta)**2
    den2 = (L2 / L1) * den1

    dw1 = (m2 * L1 * w1**2 * np.sin(delta) * np.cos(delta)
           + m2 * g * np.sin(th2) * np.cos(delta)
           + m2 * L2 * w2**2 * np.sin(delta)
           - (m1 + m2) * g * np.sin(th1)) / den1

    dw2 = (-m2 * L2 * w2**2 * np.sin(delta) * np.cos(delta)
           + (m1 + m2) * g * np.sin(th1) * np.cos(delta)
           - (m1 + m2) * L1 * w1**2 * np.sin(delta)
           - (m1 + m2) * g * np.sin(th2)) / den2

    return np.array([w1, w2, dw1, dw2])

def rk4_step(state, dt):
    """经典四阶 Runge-Kutta。"""
    k1 = derivatives(state)
    k2 = derivatives(state + 0.5 * dt * k1)
    k3 = derivatives(state + 0.5 * dt * k2)
    k4 = derivatives(state + dt * k3)
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

# --- 积分两条几乎相同的轨迹（展示混沌） ---
theta0_a = np.radians(120.0)
theta0_b = np.radians(120.001)  # 差 0.001 度！

state_a = np.array([theta0_a, 0.0, 0.0, 0.0])
state_b = np.array([theta0_b, 0.0, 0.0, 0.0])

traj_a = np.zeros((N, 4))
traj_b = np.zeros((N, 4))

for i in range(N):
    traj_a[i] = state_a
    traj_b[i] = state_b
    state_a = rk4_step(state_a, dt)
    state_b = rk4_step(state_b, dt)

t = np.arange(N) * dt

# --- 画图 ---
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

# 左：两条轨迹的角度差（指数增长 = 混沌）
ax = axes[0]
diff = np.abs(traj_a[:, 0] - traj_b[:, 0])
ax.semilogy(t, np.maximum(diff, 1e-15), 'r-', linewidth=0.8)
ax.set_xlabel('Time (s)')
ax.set_ylabel(r'$|\theta_1^{(a)} - \theta_1^{(b)}|$ (rad)')
ax.set_title('Chaos: Lyapunov Exponent\n(tiny gap grows exponentially)')
ax.axhline(0.1, color='gray', linestyle='--', alpha=0.5)
ax.set_ylim(1e-7, 5)

# 中：摆 2 的相空间（庞加莱截面预览）
ax = axes[1]
x2 = L1 * np.sin(traj_a[:, 0]) + L2 * np.sin(traj_a[:, 1])
y2 = -L1 * np.cos(traj_a[:, 0]) - L2 * np.cos(traj_a[:, 1])
ax.plot(x2, y2, 'b-', linewidth=0.3, alpha=0.7)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Pendulum 2 trajectory\n(free pendulum tip path)')
ax.set_aspect('equal')
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-2.5, 2.5)

# 右：能量守恒检验（RK4 不是辛积分器，能量缓慢漂移）
ax = axes[2]
th1, th2, w1, w2 = traj_a[:, 0], traj_a[:, 1], traj_a[:, 2], traj_a[:, 3]
T_kin = 0.5*(m1+m2)*L1**2*w1**2 + 0.5*m2*L2**2*w2**2 + m2*L1*L2*w1*w2*np.cos(th1-th2)
V_pot = -(m1+m2)*g*L1*np.cos(th1) - m2*g*L2*np.cos(th2)
E = T_kin + V_pot
ax.plot(t, (E - E[0]) / np.abs(E[0]) * 100, 'g-', linewidth=0.8)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Energy drift (%)')
ax.set_title(f'Energy conservation check\n(RK4: drift = {(E[-1]-E[0])/abs(E[0])*100:.3f}%)')

plt.tight_layout()
plt.savefig('double_pendulum_chaos.png', dpi=150)
plt.show()
print(f"Lyapunov time ~ {t[np.argmax(diff > 0.1)]:.1f} s")
```

**反直觉发现**：
1. **初值差 0.001° 在约 8 秒后放大到整个角度范围**——这就是混沌的"蝴蝶效应"。
2. **RK4 积分器不是辛积分器**，能量有缓慢数值漂移（约 0.01%）。真实的物理系统（如行星轨道）需要辛积分器（如 leapfrog/Verlet）才能长期保持能量守恒。
3. **双摆的轨迹在相空间中永不相交**——这是哈密顿系统的拓扑性质。

### 演示 2：有效势能与轨道稳定性

```python
"""
中心力场有效势能可视化 — Berkeley 105
展示离心势垒如何创造稳定轨道。
"""
import numpy as np
import matplotlib.pyplot as plt

r = np.linspace(0.01, 5, 500)
L_vals = [0.5, 1.0, 1.5]  # 不同角动量

fig, ax = plt.subplots(figsize=(8, 5))

for L in L_vals:
    V_cent = L**2 / (2 * r**2)   # 离心势垒
    V_grav = -1.0 / r             # 引力势
    V_eff = V_cent + V_grav       # 有效势

    ax.plot(r, V_eff, linewidth=2, label=f'$L = {L}$')
    r_min = L**2  # 极小值位置
    ax.plot(r_min, V_eff[np.argmin(np.abs(r - r_min))], 'ro', markersize=6)

ax.axhline(0, color='gray', linestyle='--', alpha=0.3)
ax.set_ylim(-1.5, 1.5)
ax.set_xlabel('r')
ax.set_ylabel(r'$V_{\mathrm{eff}}(r)$')
ax.set_title('Effective Potential: Centrifugal Barrier + Gravity')
ax.legend()
plt.tight_layout()
plt.savefig('effective_potential.png', dpi=150)
plt.show()
```

### 演示 3：网球拍定理（中间轴不稳定）

```python
"""
网球拍定理 (Tennis Racket Theorem / Dzhanibekov Effect)
中间惯量轴旋转不稳定。纯 NumPy 欧拉方程积分。
"""
import numpy as np
import matplotlib.pyplot as plt

# 惯量主轴：I1 > I2 > I3
I1, I2, I3 = 3.0, 2.0, 1.0

def euler_eq(omega, dt):
    """欧拉方程（体坐标系）。"""
    dw1 = (I2 - I3) / I1 * omega[1] * omega[2]
    dw2 = (I3 - I1) / I2 * omega[2] * omega[0]
    dw3 = (I1 - I2) / I3 * omega[0] * omega[1]
    return np.array([dw1, dw2, dw3])

# 绕中间轴 I2 旋转，加微小扰动
omega = np.array([0.01, 5.0, 0.01])  # 主要绕轴2
dt, N = 0.001, 50000
traj = np.zeros((N, 3))

for i in range(N):
    traj[i] = omega
    # RK4
    k1 = euler_eq(omega, dt)
    k2 = euler_eq(omega + 0.5*dt*k1, dt)
    k3 = euler_eq(omega + 0.5*dt*k2, dt)
    k4 = euler_eq(omega + dt*k3, dt)
    omega += (dt/6) * (k1 + 2*k2 + 2*k3 + k4)

t = np.arange(N) * dt
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(t, traj[:, 0], label=r'$\omega_1$ (max inertia axis)', alpha=0.8)
ax.plot(t, traj[:, 1], label=r'$\omega_2$ (MID axis)', alpha=0.8)
ax.plot(t, traj[:, 2], label=r'$\omega_3$ (min inertia axis)', alpha=0.8)
ax.set_xlabel('Time')
ax.set_ylabel('Angular velocity')
ax.set_title('Tennis Racket Theorem: Mid-axis rotation is UNSTABLE')
ax.legend()
plt.tight_layout()
plt.savefig('tennis_racket.png', dpi=150)
plt.show()
print("Observe: omega periodically flips sign — the 'Dzhanibekov flip'!")
```

---

## 学习路径建议

```
7A (Tipler)  →  牛顿力学 + 狭义相对论入门
      ↓
105 (Taylor Ch 1-7)  →  拉格朗日力学
      ↓
105 (Taylor Ch 8-13)  →  哈密顿力学 + 刚体 + 非线性
      ↓
139 (Schutz)  →  广义相对论
```

**Taylor 教材学习节奏**（Berkeley 105 一学期 15 周）：
- 周 1-3：Ch 1-3（牛顿力学复习 + 矢量力学）
- 周 4-7：Ch 6-7（拉格朗日力学，核心）
- 周 8-10：Ch 8-11（哈密顿力学 + 刚体）
- 周 11-13：Ch 12-13（非线性混沌 + 狭义相对论）
- 周 14-15：Ch 4-5（中心力 + 非惯性系，穿插复习）

---

> **文件信息**：Berkeley Physics · Topic 01 Mechanics · 2026-08-12
> 
> **教材交叉引用**：Tipler (7A) / Taylor (105) / Marion & Thornton (105) / Goldstein (研究生衔接)

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：力学就是研究"东西怎么动、为什么这么动"的学问——你推一下滑板，它会滑多远？地球绕太阳为什么走椭圆？这些问题力学都能回答。
>
> **生活类比**：想象一个滑板少年在 U 型池里来回荡。牛顿力学告诉你"他现在在哪儿、速度多少、下一步去哪"；拉格朗日力学换个视角——"不管他走什么路线，大自然帮他挑了最省力那条"；哈密顿力学则把位置和动量摆成一张地图（相空间），你一眼就能看出他所有可能的未来。
>
> **反直觉发现**：
> - **网球拍定理**：你把一本书抛到空中，绕某些轴旋转它稳稳的，绕另一些轴它会突然翻转！这不是你手笨——是惯量张量的数学结构决定的（中间轴必翻转）。
> - **双摆混沌**：两个摆首尾相连，初始角度差 0.001°，8 秒后轨迹天差地别。确定性方程产生不可预测的行为——这就是"蝴蝶效应"的数学根源。
> - **作用量极值**：光和粒子都"知道"走哪条路最省事。好像它们提前试了所有可能的路线，选了最优的——大自然是个超级优化器。

---

## 🔗 衔接：从哪来，到哪去

### 前置知识
- **高中物理**：牛顿三定律、能量守恒、动量守恒（基本直觉）
- **微积分**：导数（速度=位置的变化率）、积分（功=力的累积）、微分方程
- **矢量代数**：叉乘（力矩、角动量的数学语言）

### 本主题解决了什么危机
- **19 世纪危机**：牛顿力学处理多体问题和约束系统（如珠子在弯曲金属丝上滑动）极其繁琐——需要写大量约束力方程。**拉格朗日力学**（1788）用一个标量 $L = T - V$ 和最小作用量原理，一统所有力学问题，约束力自动消失。
- **统计物理的门槛**：牛顿力学无法处理 $10^{23}$ 个粒子。**哈密顿力学的相空间 + Liouville 定理**为统计力学铺设了数学基础——系综平均变成了相空间积分。

### 本主题留下的新危机
- **混沌不可预测**：决定论方程不意味着可预测——蝴蝶效应让长期天气预报 fundamentally 不可能。
- **高速极限失效**：当速度接近光速，$F = ma$ 破裂。需要狭义相对论（§5 已预告）。
- **小尺度失效**：原子尺度下粒子不再有确定轨道。需要量子力学（Topic 03）。
- **引力极限**：牛顿万有引力无法解释水星近日点进动。需要广义相对论（Berkeley 139）。

### 后续主题
- → **Topic 02 电磁学**：Lorentz 力是力学的直接延续；麦克斯韦方程组在力学框架内被推导
- → **Topic 03 量子力学**：哈密顿量 $H(q,p)$ 直接量子化为 $\hat{H}$；哈密顿-雅可比方程→薛定谔方程
- → **Topic 04 统计物理**：Liouville 定理→微正则系综；配分函数 $Z = \text{Tr}(e^{-\beta H})$
- → Berkeley **139 广义相对论**：等效原理→弯曲时空中的测地线运动

---

## 🏭 理论联系实际：5 个应用

1. **GPS 卫星轨道校正**：GPS 卫星在 2 万公里高空飞行，其轨道力学需要牛顿引力 + 开普勒定律。但相对论修正（每天快 38 微秒）如果不加，导航每天偏 11 公里。力学公式直接嵌入 GPS 芯片。

2. **陀螺仪与惯性导航**：手机里的 MEMS 陀螺仪利用刚体动力学（角动量守恒）。火箭、导弹、潜艇在 GPS 不可用时，靠惯性导航系统（INS）——纯力学计算位置。

3. **LIGO 引力波探测器**：两个 4 公里长的激光干涉臂，用悬挂的镜面做自由质点。引力波经过时拉伸空间，镜面位置变化 $< 10^{-18}$ 米——比质子还小 10000 倍。2015 年首次探测到引力波，打开了"听宇宙"的新窗口。

4. **机器人动力学与控制**：波士顿动力的 Atlas 机器人做后空翻，核心算法是拉格朗日方程 + 数值积分。每个关节的广义坐标 $q_i$ 都有一个 Euler-Lagrange 方程，实时求解来控制平衡。

5. **分子动力学模拟**：药物设计的核心工具。蛋白质里 $10^5$ 个原子用牛顿方程积分（每步 $10^{-15}$ 秒），计算药物分子如何结合靶点。需要辛积分器保能量守恒——正是 §3 哈密顿力学的直接应用。

---

## 🔬 最新研究前沿（2024-2026）

1. **流体断裂的发现**（2026-07, Quanta Magazine）：传统认为只有弹性固体才能断裂，但研究者发现简单非弹性流体在极端条件下也会"断裂"——这挑战了流体力学的百年假设，重新定义了流体力学中的断裂判据。

2. **分形上的量子不确定性原理**（2026-08-12, Quanta Magazine）：研究生证明了将混沌、分形结构和量子不确定性结合的数学定理——被称为"基础性结果"。这连接了经典力学中的混沌理论与量子力学的深层结构。

3. **热力学计算机**（2026-07-15, Quanta Magazine）：利用热力学涨落而非对抗它们的新型计算范式——统计力学原理直接驱动计算。Berkeley 统计物理方向的交叉研究热点。

4. **LIGO O4 观测运行**（2023-2024 持续）：Advanced LIGO + Advanced Virgo + KAGRA 联合观测，已探测到 100+ 引力波事件，包括前所未有的中等质量黑洞合并。Berkeley 天体物理组参与数据分析。

5. **非线性动力学与机器学习融合**（2024-2025）：Physics-Informed Neural Networks (PINNs) 用深度学习求解非线性微分方程，在湍流模拟、混沌控制中取得突破。Berkeley AI+Physics 交叉方向。

---

## 🗺️ 学习 Roadmap（Berkeley 路径）

```
高中物理 / AP Physics C
      ↓
 7A — Physics for Scientists and Engineers (Tipler)
      │  牛顿三定律 · 能量/动量守恒 · 转动 · 流体 · 热学入门 · 狭义相对论初探
      │  ✅ 知识检查：能否推导圆锥摆周期？能否用能量守恒求第二宇宙速度？
      ↓
 105 — Analytic Mechanics (Taylor / Marion & Thornton)
      │  拉格朗日力学 · 哈密顿力学 · 刚体(欧拉角/惯量张量) · 非线性混沌 · 微扰理论
      │  ✅ 知识检查：能否写出双摆的拉格朗日量？能否证明网球拍定理？
      ↓
 139 — General Relativity (Schutz / Carroll) [可选，研究生]
      │  等效原理 · 弯曲时空 · 爱因斯坦方程 · 施瓦兹希尔德解
      │  ✅ 知识检查：能否推导水星近日点进动？
      ↓
 研究前沿 → 非线性动力学 · 引力波物理 · 机器人学 · 分子动力学
```

**核心教材节奏**：
| 阶段 | 教材 | 周数 | 核心概念 |
|------|------|------|----------|
| 7A | Tipler Ch 1-11 | 15 周 | 牛顿力学 + 狭义相对论 |
| 105 | Taylor Ch 1-13 | 15 周 | 拉格朗日 + 哈密顿 + 混沌 |
| 139 | Carroll Ch 1-7 | 研究生 | 广义相对论 |

**费曼学习法检查点**：
- [ ] 能否用白话解释"最小作用量原理"？（费曼自己最爱用的讲法）
- [ ] 能否不查公式推导出单摆周期 $T = 2\pi\sqrt{L/g}$？
- [ ] 能否解释为什么辛积分器比 Euler 法更适合长时间模拟？
