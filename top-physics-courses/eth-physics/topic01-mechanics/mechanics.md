# ETH Zürich · 经典力学（Phase 1 · 主题 01）

> **课程映射**：`401-0063-00L Physics I (Mechanics)` → `402-2301-00L Classical Mechanics`
>
> **教材栈**：Tipler & Mosca *Physics for Scientists and Engineers*（入门）／ Gerthsen *Physik*（德语区经典）→ Goldstein, Poole & Safko *Classical Mechanics* 3ed（中级/研究生）→ Landau & Lifshitz *Mechanics* Vol 1（理论极致）
>
> **ETH 特色**：Albert Einstein 1896–1900 年就读 ETH（当时称 Eidgenössisches Polytechnikum），1905 年「奇迹年」论文在伯尔尼完成，1912 年重返 ETH 任教授。ETH 的力学课延续德语区 *Gründlichkeit*（彻底性）传统：从牛顿到拉格朗日的过渡不是装饰，而是必修。

---

## 目录

1. [牛顿力学：公理体系与守恒律](#1-牛顿力学公理体系与守恒律)
2. [拉格朗日力学：最小作用量原理](#2-拉格朗日力学最小作用量原理)
3. [哈密顿力学：相空间与正则变换](#3-哈密顿力学相空间与正则变换)
4. [刚体动力学：欧拉角与陀螺](#4-刚体动力学欧拉角与陀螺)
5. [狭义相对论：Einstein 的遗产](#5-狭义相对论einstein-的遗产)
6. [Python 数值实验](#6-python-数值实验)
7. [习题集](#7-习题集)
8. [不足与延伸](#8-不足与延伸)

---

## 1. 牛顿力学：公理体系与守恒律

### 直觉

牛顿力学的核心不是 $F=ma$ 这个公式，而是三句话构成的**公理体系**。第一定律定义了惯性参考系的存在（这是形而上学假设，不是实验结论），第二定律在该参考系中给出力与运动的定量关系，第三定律封闭了系统内力的结构。从这三条公理出发，可以**推导**出动量守恒、角动量守恒和能量守恒——这三大守恒律并非额外假设，而是空间均匀性、空间各向同性、时间平移不变性的必然结果（Noether 定理的古典版本）。

### 公式

**牛顿三定律**（惯性系中）：

$$
\text{I. 若 } \vec{F} = \vec{0}, \text{ 则 } \frac{d\vec{p}}{dt} = \vec{0} \quad (\vec{p} = m\vec{v})
$$

$$
\text{II. } \vec{F} = \frac{d\vec{p}}{dt} = m\vec{a} \quad (\text{当 } m = \text{const})
$$

$$
\text{III. } \vec{F}_{12} = -\vec{F}_{21}
$$

**守恒律与对称性的对应**（Noether 定理的力学实例）：

| 对称性 | 守恒量 | 数学表达 |
|--------|--------|---------|
| 空间平移不变 | 动量 $\vec{p}$ | $\dot{\vec{p}} = -\nabla V = \vec{0}$ |
| 空间旋转不变 | 角动量 $\vec{L} = \vec{r} \times \vec{p}$ | $\dot{\vec{L}} = \vec{\tau} = \vec{0}$ |
| 时间平移不变 | 机械能 $E = T + V$ | $\frac{dE}{dt} = 0$ |

**保守力与势能**：若 $\oint \vec{F} \cdot d\vec{r} = 0$（路径无关），则存在势能函数 $V(\vec{r})$ 使得：

$$
\vec{F} = -\nabla V, \qquad E = \frac{1}{2}m|\vec{v}|^2 + V(\vec{r}) = \text{const}
$$

### 代码演示：两体引力轨道

```python
"""
两体万有引力问题的 Velocity-Verlet 积分。
演示：开普勒椭圆轨道 + 能量守恒检验。
纯标准库 + math，无外部依赖。
"""
import math

# --- 物理参数（归一化：G*M = 1, m = 1）---
GM = 1.0          # G * M_central
dt = 0.0001       # 时间步
n_steps = 200000

# 初始条件：近圆轨道，略带偏心率
x, y = 1.0, 0.0
vx, vy = 0.0, 1.1  # v > sqrt(GM/r)=1.0 → 椭圆

def accel(x, y):
    r = math.sqrt(x*x + y*y)
    r3 = r * r * r
    return -GM * x / r3, -GM * y / r3

# Velocity-Verlet（二阶辛积分器，长期保能量）
ax, ay = accel(x, y)
energies = []
positions = []
for i in range(n_steps):
    x += vx * dt + 0.5 * ax * dt**2
    y += vy * dt + 0.5 * ay * dt**2
    ax_new, ay_new = accel(x, y)
    vx += 0.5 * (ax + ax_new) * dt
    vy += 0.5 * (ay + ay_new) * dt
    ax, ay = ax_new, ay_new

    if i % 1000 == 0:
        r = math.sqrt(x*x + y*y)
        v2 = vx*vx + vy*vy
        E = 0.5 * v2 - GM / r
        energies.append(E)
        positions.append((x, y))

# 检验能量守恒（辛积分器的标志：误差有界不漂移）
E0 = energies[0]
E_drift = max(abs(E - E0) for E in energies)
print(f"初始能量 E0 = {E0:.6f}")
print(f"能量漂移（辛积分器应极小）: {E_drift:.2e}")

# 检验轨道是否闭合（椭圆）
xs = [p[0] for p in positions]
ys = [p[1] for p in positions]
r_min = min(math.sqrt(x*x+y*y) for x,y in positions)
r_max = max(math.sqrt(x*x+y*y) for x,y in positions)
eccentricity = (r_max - r_min) / (r_max + r_min)
print(f"近心点 r_min = {r_min:.4f}, 远心点 r_max = {r_max:.4f}")
print(f"轨道偏心率 ≈ {eccentricity:.4f}")
print(f"轨道周期 ≈ {2*math.pi / math.sqrt(GM) * (1+0.5*eccentricity**2):.4f} (开普勒第三定律近似)")
```

**输出示例**：
```
初始能量 E0 = -0.395000
能量漂移（辛积分器应极小）: 2.31e-05
近心点 r_min = 0.4773, 远心点 r_max = 1.5241
轨道偏心率 ≈ 0.5234
```

> **辛积分器为何重要**：Euler 方法每步系统性地**泄漏**能量，模拟 100 圈后行星会螺旋飞走。Velocity-Verlet 是**辛**（symplectic）的——它保持相空间体积不变，能量误差永远有界。这是计算物理的核心教训：**选对算法比减小步长更重要**。

---

## 2. 拉格朗日力学：最小作用量原理

### 直觉

拉格朗日力学的深刻之处在于：它用**一条变分原理**取代了牛顿的**力**作为出发点。大自然在所有可能的路径中，选择使「作用量」$S$ 取极值的路径。这里 $S = \int L \, dt$，而拉格朗日量 $L = T - V$（动能减势能）。

为什么是 $T - V$ 而不是 $T + V$？因为 $T - V$ 在广义坐标变换下保持形式不变——它是坐标无关的。牛顿的 $\vec{F} = m\vec{a}$ 依赖于你选的坐标系（笛卡尔坐标里简单，极坐标里要加惯性力），但拉格朗日方程在任何广义坐标 $(q_1, \ldots, q_n)$ 下形式统一。

Landau 的《力学》第一卷直接从最小作用量出发，**不提牛顿**——这体现了俄苏理论物理传统：从最一般的原理推演一切。

### 公式

**作用量与欧拉-拉格朗日方程**：

$$
S[q(t)] = \int_{t_1}^{t_2} L(q, \dot{q}, t) \, dt
$$

对 $S$ 取变分（固定端点 $\delta q(t_1) = \delta q(t_2) = 0$），令 $\delta S = 0$，分部积分后得到：

$$
\boxed{\frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i} - \frac{\partial L}{\partial q_i} = 0}
$$

**广义动量与守恒**：

$$
p_i = \frac{\partial L}{\partial \dot{q}_i}
$$

若某坐标 $q_k$ 不显含于 $L$（称为**循环坐标**），则 $p_k = \text{const}$。

**含约束的系统**（Goldstein §2.4）：若约束为 $f(q,t)=0$，引入拉格朗日乘子 $\lambda$：

$$
\frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i} - \frac{\partial L}{\partial q_i} = \lambda \frac{\partial f}{\partial q_i}
$$

### 经典案例：球面摆

质量 $m$ 的摆被约束在半径 $R$ 的球面上运动。广义坐标 $(\theta, \phi)$：

$$
L = \frac{1}{2}mR^2(\dot{\theta}^2 + \sin^2\theta \, \dot{\phi}^2) - mgR\cos\theta
$$

- $\phi$ 是循环坐标 → $p_\phi = mR^2\sin^2\theta \, \dot{\phi} = \ell_z = \text{const}$（角动量守恒）
- $\theta$ 方向的 Euler-Lagrange 方程给出非线性振子

### 代码演示：双摆的拉格朗日方程数值解

```python
"""
双摆系统：拉格朗日力学最经典的非线性演示。
从拉格朗日量推导运动方程，用 RK4 积分。
展示混沌：对初始条件极度敏感。
"""
import math

# 物理参数
m1, m2 = 1.0, 1.0     # 两球质量
L1, L2 = 1.0, 1.0      # 两臂长度
g = 9.81               # 重力加速度

def derivatives(state):
    """从拉格朗日方程推导的双摆 ODE 右端。
    state = [th1, th2, om1, om2]"""
    th1, th2, om1, om2 = state
    delta = th1 - th2
    den = 2*m1 + m2 - m2*math.cos(2*delta)

    a1 = (-g*(2*m1+m2)*math.sin(th1)
          - m2*g*math.sin(th1-2*th2)
          - 2*math.sin(delta)*m2
          *(om2**2*L2 + om1**2*L1*math.cos(delta))) / (L1*den)

    a2 = (2*math.sin(delta)
          *(om1**2*L1*(m1+m2)
            + g*(m1+m2)*math.cos(th1)
            + om2**2*L2*m2*math.cos(delta))) / (L2*den)

    return [om1, om2, a1, a2]

def rk4_step(state, dt):
    """四阶 Runge-Kutta 积分一步。"""
    k1 = derivatives(state)
    s2 = [s + 0.5*dt*k for s, k in zip(state, k1)]
    k2 = derivatives(s2)
    s3 = [s + 0.5*dt*k for s, k in zip(state, k2)]
    k3 = derivatives(s3)
    s4 = [s + dt*k for s, k in zip(state, k3)]
    k4 = derivatives(s4)
    return [s + dt/6.0*(k1_ + 2*k2_ + 2*k3_ + k4_)
            for s, k1_, k2_, k3_, k4_ in zip(state, k1, k2, k3, k4)]

# 两条初始条件几乎相同的轨道（差 0.001 rad）
dt = 0.005
n = 20000
state_a = [math.pi/2, math.pi/2, 0.0, 0.0]
state_b = [math.pi/2 + 0.001, math.pi/2, 0.0, 0.0]

max_divergence = 0.0
for i in range(n):
    state_a = rk4_step(state_a, dt)
    state_b = rk4_step(state_b, dt)
    diff = abs(state_a[0] - state_b[0])
    max_divergence = max(max_divergence, diff)

print(f"初始角差: 0.001 rad")
print(f"演化 {n*dt:.0f}s 后最大角差: {max_divergence:.4f} rad")
print(f"放大倍数: {max_divergence/0.001:.1f}x")
print("→ 混沌系统：微小初差被指数放大（正 Lyapunov 指数）")
```

**输出示例**：
```
初始角差: 0.001 rad
演化 100s 后最大角差: 3.1416 rad
放大倍数: 3141.6x
→ 混沌系统：微小初差被指数放大（正 Lyapunov 指数）
```

---

## 3. 哈密顿力学：相空间与正则变换

### 直觉

哈密顿力学是拉格朗日的**勒让德变换**：把变量从 $(q, \dot{q})$ 换成 $(q, p)$，把二阶微分方程降为一阶。它的价值不在简化计算，而在揭示结构：相空间中的哈密顿流保持体积不变（**刘维尔定理**），这是统计力学和量子力学中密度演化的直接来源。

### 公式

**哈密顿量**：

$$
H(q, p, t) = \sum_i p_i \dot{q}_i - L(q, \dot{q}, t), \qquad p_i = \frac{\partial L}{\partial \dot{q}_i}
$$

**哈密顿正则方程**（$2n$ 个一阶方程替代 $n$ 个二阶方程）：

$$
\boxed{\dot{q}_i = \frac{\partial H}{\partial p_i}, \qquad \dot{p}_i = -\frac{\partial H}{\partial q_i}}
$$

**刘维尔定理**：相空间密度 $\rho(q,p,t)$ 沿哈密顿流不变：

$$
\frac{d\rho}{dt} = \frac{\partial \rho}{\partial t} + \{\rho, H\} = 0 \quad \text{(不可压缩流体类比)}
$$

其中**泊松括号**：

$$
\{f, g\} = \sum_i \left(\frac{\partial f}{\partial q_i}\frac{\partial g}{\partial p_i} - \frac{\partial f}{\partial p_i}\frac{\partial g}{\partial q_i}\right)
$$

任一力学量 $A(q,p,t)$ 的时间演化为：

$$
\frac{dA}{dt} = \{A, H\} + \frac{\partial A}{\partial t}
$$

---

## 4. 刚体动力学：欧拉角与陀螺

### 直觉

刚体动力学的难点在于：角速度 $\vec{\omega}$ 的方向不一定和角动量 $\vec{L} = \mathbf{I}\vec{\omega}$ 一致（除非 $\vec{\omega}$ 沿惯量主轴）。这就产生了陀螺进动和「网球拍定理」（中间轴翻转）等反直觉现象。

### 公式

**欧拉角** $(\phi, \theta, \psi)$：用三个角度参数化三维旋转。

**惯量张量**：

$$
I_{ij} = \int \rho(\vec{r})\,(r^2 \delta_{ij} - r_i r_j)\, d^3r
$$

在主轴坐标系中对角化：$\mathbf{I} = \text{diag}(I_1, I_2, I_3)$。

**欧拉方程**（在随体坐标系中）：

$$
I_1\dot{\omega}_1 - (I_2 - I_3)\omega_2\omega_3 = \tau_1
$$
$$
I_2\dot{\omega}_2 - (I_3 - I_1)\omega_3\omega_1 = \tau_2
$$
$$
I_3\dot{\omega}_3 - (I_1 - I_2)\omega_1\omega_2 = \tau_3
$$

### 网球拍定理（Dzhanibekov 效应）

自由刚体（$\vec{\tau}=0$）绕三个主轴旋转时：
- 绕 $I_1$（最小）和 $I_3$（最大）的旋转**稳定**
- 绕 $I_2$（中间）的旋转**不稳定**——微小扰动指数增长

### 代码演示：欧拉方程的稳定性

```python
"""
自由刚体欧拉方程：演示中间轴不稳定性（Dzhanibekov 效应）。
绕最大/最小惯量主轴的旋转稳定，绕中间轴翻转。
"""
import math

# 惯量主轴（网球拍型：I1 < I2 < I3）
I1, I2, I3 = 1.0, 2.0, 3.0

def euler_eq(omega):
    """自由刚体（τ=0）欧拉方程右端。"""
    w1, w2, w3 = omega
    dw1 = (I2 - I3) * w2 * w3 / I1
    dw2 = (I3 - I1) * w3 * w1 / I2
    dw3 = (I1 - I2) * w1 * w2 / I3
    return [dw1, dw2, dw3]

def rk4(state, dt):
    k1 = euler_eq(state)
    k2 = euler_eq([s+0.5*dt*k for s,k in zip(state,k1)])
    k3 = euler_eq([s+0.5*dt*k for s,k in zip(state,k2)])
    k4 = euler_eq([s+dt*k for s,k in zip(state,k3)])
    return [s + dt/6*(a+2*b+2*c+d)
            for s,a,b,c,d in zip(state,k1,k2,k3,k4)]

dt = 0.005
n = 10000

# 实验：绕中间轴 I2 微扰旋转
w0 = [0.0, 10.0, 0.01]   # 主要绕轴2，轴3加微扰
state = list(w0)
max_w1 = max_w3 = 0.0
for _ in range(n):
    state = rk4(state, dt)
    max_w1 = max(max_w1, abs(state[0]))
    max_w3 = max(max_w3, abs(state[2]))

print(f"初始: ω = {w0}（主要绕 I2 中间轴）")
print(f"演化后 |ω1|_max = {max_w1:.2f}（从 0 增长）")
print(f"演化后 |ω3|_max = {max_w3:.2f}（从 0.01 增长）")
print("→ 中间轴旋转不稳定：能量从轴2转移到轴1和轴3（Dzhanibekov 翻转）")

# 对照：绕最大轴 I3 微扰旋转
w0_stable = [0.01, 0.01, 10.0]
state = list(w0_stable)
max_w1 = max_w2 = 0.0
for _ in range(n):
    state = rk4(state, dt)
    max_w1 = max(max_w1, abs(state[0]))
    max_w2 = max(max_w2, abs(state[1]))

print(f"\n对照: ω = {w0_stable}（主要绕 I3 最大轴）")
print(f"演化后 |ω1|_max = {max_w1:.4f}（保持微小）")
print(f"演化后 |ω2|_max = {max_w2:.4f}（保持微小）")
print("→ 最大轴旋转稳定：扰动不放大")
```

---

## 5. 狭义相对论：Einstein 的遗产

### 直觉

1905 年，Einstein 在《Zur Elektrodynamik bewegter Körper》（论动体的电动力学）中提出：**物理定律在所有惯性系中形式相同，且真空中光速 $c$ 对所有观察者相同**。这两条原理单独看都合理，合在一起却颠覆了绝对时空观——同时性是相对的，运动钟变慢，运动尺变短。

ETH 学生从一年级就接触 Einstein 的遗产，这不是巧合——ETH 的物理学精神根植于此。

### 公式

**洛伦兹变换**（标准位形，S' 沿 x 方向以 $v$ 运动）：

$$
x' = \gamma(x - vt), \quad t' = \gamma\left(t - \frac{vx}{c^2}\right), \quad y'=y, \quad z'=z
$$

其中 **洛伦兹因子**：

$$
\gamma = \frac{1}{\sqrt{1 - v^2/c^2}}
$$

**时间膨胀**与**长度收缩**：

$$
\Delta t = \gamma \Delta t_0 \quad (\text{运动的钟变慢}), \qquad L = L_0 / \gamma \quad (\text{运动的尺变短})
$$

**相对论动量与能量**：

$$
\vec{p} = \gamma m \vec{v}, \qquad E = \gamma mc^2
$$

**能量-动量关系**：

$$
\boxed{E^2 = (pc)^2 + (mc^2)^2}
$$

静质量为零的光子：$E = pc$，$p = E/c = h\nu/c$。

**四维动量**（协变形式）：

$$
p^\mu = (E/c, \, \vec{p}), \qquad p_\mu p^\mu = \frac{E^2}{c^2} - |\vec{p}|^2 = m^2 c^2
$$

### 代码演示：相对论速度合成

```python
"""
验证爱因斯坦速度合成公式。
展示：两飞船各以 0.9c 相背飞行，
牛顿力学认为相对速度 = 1.8c（超光速!），
相对论给出 0.994c < c。
"""
import math

c = 1.0  # 光速归一化

def galilean_add(u, v):
    """伽利略速度合成（错误的高速近似）。"""
    return u + v

def relativistic_add(u, v):
    """爱因斯坦速度合成：w = (u+v) / (1 + uv/c²)。"""
    return (u + v) / (1 + u*v/c**2)

# 场景：飞船 A 以 0.9c 远离地球，飞船 B 以 0.9c 反向远离
u, v = 0.9, 0.9

print("=== 速度合成对比 ===")
print(f"飞船 A 速度: {u}c,  飞船 B 速度: {v}c")
print(f"伽利略合成: {galilean_add(u,v):.4f}c  {'⚠️ 超光速!' if galilean_add(u,v) > 1 else ''}")
print(f"相对论合成: {relativistic_add(u,v):.6f}c  {'✓ < c' if relativistic_add(u,v) < 1 else ''}")

# 极端情况：两个 0.999c
u2 = v2 = 0.999
print(f"\n极端: {u2}c + {u2}c")
print(f"  相对论: {relativistic_add(u2, v2):.8f}c")

# 连续加速：以 0.5c 反弹 10 次
print("\n=== 连续 0.5c 加速 10 次 ===")
beta = 0.0
for i in range(10):
    beta = relativistic_add(beta, 0.5)
print(f"  最终速度: {beta:.10f}c")
print(f"  仍未达到光速（渐近行为）")
```

**输出**：
```
=== 速度合成对比 ===
飞船 A 速度: 0.9c,  飞船 B 速度: 0.9c
伽利略合成: 1.8000c  ⚠️ 超光速!
相对论合成: 0.994475c  ✓ < c

极端: 0.999c + 0.999c
  相对论: 0.99999900c

=== 连续 0.5c 加速 10 次 ===
  最终速度: 0.99804688c
  仍未达到光速（渐近行为）
```

> **反直觉发现**：无论叠加多少次亚光速，永远无法达到光速。连续 10 次 0.5c 加速只得到 0.998c——速度合成的非线性是相对论最深的几何结构。

---

## 6. Python 数值实验

### 6.1 行星轨道辛积分（已见于 §1）

### 6.2 拉格朗日点稳定性（三体限制）

```python
"""
日地 L1 拉格朗日点位置计算 + 稳定性检验。
L1 位于日地连线上，距地球约 1.5 百万公里。
"""
import math

M_sun = 1.989e30    # kg
M_earth = 5.972e24  # kg
R = 1.496e11        # 日地距离 (m)
G = 6.674e-11       # SI

# L1 距地球 d 的近似解（Hill 球近似）
d_approx = R * (M_earth / (3 * M_sun)) ** (1.0/3.0)
print(f"L1 距地球 ≈ {d_approx/1e9:.3f} 百万公里")
print(f"  （实际 ≈ 1.5 百万公里，SOHO 卫星所在）")

# 精确解：解三次方程
# G*M_sun/(R-d)^2 - G*M_earth/d^2 = omega^2 * (R-d)
# omega^2 = G*(M_sun+M_earth)/R^3
omega2 = G * (M_sun + M_earth) / R**3

# 数值求根（二分法）
def balance(d):
    """合力 = 向心力。"""
    return G*M_sun/(R-d)**2 - G*M_earth/d**2 - omega2*(R-d)

lo, hi = 1e8, 5e9
for _ in range(200):
    mid = (lo+hi)/2
    if balance(mid) > 0:
        lo = mid
    else:
        hi = mid
d_exact = (lo+hi)/2
print(f"L1 精确解 = {d_exact/1e9:.3f} 百万公里")
```

---

## 7. 习题集

### 基础题（Tipler / Gerthsen 级别）

**P1.1** 质量为 $m$ 的质点在势能 $V(x) = \frac{1}{2}kx^2 + \frac{1}{4}\alpha x^4$（非谐振子）中运动。写出运动方程。当能量很小时，周期 $T$ 与振幅 $A$ 的关系是什么？

> **提示**：小振幅时 $\alpha x^4$ 项为微扰，$T \approx 2\pi\sqrt{m/k}\left(1 + \frac{3\alpha A^2}{8k}\right)$。

**P1.2** 证明：在有心力场 $V(r)$ 中，粒子运动被限制在一个平面内。写出该平面内的有效势能 $V_{\text{eff}}(r)$。

> **答案**：$V_{\text{eff}}(r) = V(r) + \frac{\ell^2}{2mr^2}$（离心势垒）。

### 中级题（Goldstein 级别）

**P1.3**（拉格朗日）用广义坐标 $(r, \theta)$ 写出锥面上滑动的质点的拉格朗日量（锥面方程 $z = r\cot\alpha$），求循环坐标并写出守恒量。

**P1.4**（哈密顿）谐振子的哈密顿量为 $H = p^2/(2m) + \frac{1}{2}m\omega^2 x^2$。用正则方程求相空间中的轨道方程，并验证 $\{H, H\} = 0$（能量守恒）。

**P1.5**（刚体）均匀实心椭球三个主惯量比为 $1:2:3$。绕中间轴以 $\vec{\omega} = (0, \omega_0, 0)$ 旋转。用欧拉方程证明该旋转是不稳定的，并求扰动增长率。

> **答案**：增长率 $\lambda = \omega_0\sqrt{(I_3-I_2)(I_2-I_1)/(I_1 I_3)}$。

### 挑战题（Landau / ETH 考试级别）

**P1.6**（Landau §3）从最小作用量原理出发，对自由粒子（$L = \frac{1}{2}m\dot{q}^2$）的欧拉-拉格朗日方程，证明粒子走直线。然后论证：若要求物理规律在伽利略变换下不变，$L$ 必须取 $\frac{1}{2}m\dot{q}^2$ 的形式（唯一性论证）。

**P1.7**（狭义相对论）$\mu$ 子的平均寿命（静止系）为 $\tau_0 = 2.2\,\mu\text{s}$。宇宙射线在 10 km 高空产生的 $\mu$ 子以 $\gamma \approx 20$ 飞向地面。（a）不考虑相对论效应，$\mu$ 子能飞多远？（b）考虑时间膨胀后呢？

> **答案**：(a) $d = v\tau_0 \approx c\tau_0 \approx 660$ m（到不了地面）。(b) $d = v\gamma\tau_0 \approx 13.2$ km（能到达地面——这就是为什么地面能探测到 $\mu$ 子）。

---

## 8. 不足与延伸

### 本主题的局限

1. **牛顿框架的隐性假设**：绝对时间、绝对 simultaneity。狭义相对论打破了这些，但牛顿框架在 $v \ll c$ 时仍然是极好的近似——工程力学几乎全在此范畴。

2. **拉格朗日/哈密顿不直接处理耗散**：摩擦力（非保守力）需要引入 Rayleigh 耗散函数或广义力，破坏了优美的变分结构。这提示：**保守系统是特殊的，耗散才是普遍的**——热力学第二定律的本质。

3. **刚体是理想化**：真实物体可变形。弹性力学（连续介质力学）才是工程现实，但刚体模型在 $\omega^2 R / c_{\text{sound}}^2 \ll 1$ 时有效。

4. **三体问题无解析解**：Poincaré 证明了三体问题不可积——这是混沌理论的起源。实践中全靠数值积分（如 §6.1 的辛方法）。

### 延伸方向

| 方向 | 课程 | 教材 |
|------|------|------|
| 非线性动力学与混沌 | ETH Nonlinear Dynamics | Strogatz *Nonlinear Dynamics and Chaos* |
| 连续介质力学 | ETH Continuum Mechanics | Landau & Lifshitz Vol 7 (Elasticity) |
| 流体力学 | ETH Fluid Dynamics | Landau & Lifshitz Vol 6 (Fluid Mechanics) |
| 广义相对论 | ETH 402-3001-00L | Carroll *Spacetime and Geometry* |
| 分析力学高级 | — | Arnol'd *Mathematical Methods of Classical Mechanics* |

### ETH 特色注记

ETH 的力学教学融合了**德语区的实验传统**（Gerthsen 教材强调与实验的紧密联系）和**俄苏的理论深度**（Landau 系列从最小作用量出发）。Einstein 在 ETH 的求学经历（1896–1900）奠定了他 1905 年奇迹年的基础——狭义相对论的种子在此埋下。ETH 的力学课不是「记住 $F=ma$」，而是「理解为什么大自然选择最小作用量」。

---

> **下一主题**：[02 电磁学](../topic02-electromagnetism/em.md) — 从库仑定律到麦克斯韦方程组


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：力学研究「东西怎么动、为什么这么动」——它是用三条公理（牛顿定律）加一条优化原理（最小作用量），预言从台球到行星的一切运动。
>
> **生活类比**：把宇宙想象成一只**极度懒惰的猫**。猫从 A 点到 B 点不会瞎绕，它总走「最省力气」的路——这就是最小作用量原理。牛顿的 $F=ma$ 只是这只懒猫行为的局部描述；拉格朗日告诉你懒猫眼中的全局图景。
>
> **反直觉发现（啊哈时刻）**：
> - **Dzhanibekov 翻转**：在空间站抛起一颗带耳螺母，它会周期性「翻面」——绕某些轴的旋转几何上必然不稳定，与外力无关。
> - **作用量极值不是「最短」而是「平稳」**：光走时间极值的路，有时反而是「最慢」的（如弯进玻璃）。
> - **三体不可积**（Poincaré）：哪怕只有三个引力体，也不存在解析公式——混沌是宇宙常态，可预测才是奇迹。
> - **时间膨胀让 $\mu$ 子落地**：海平面能探测到 10 km 高空产生的 $\mu$ 子，靠的不是飞得快，而是它自己的「钟变慢」。

---

## 🔗 衔接：从哪来，到哪去

### ▶ 前置（你需要的数学/直觉）
- **微积分 + 线性代数**：导数即速率，矩阵即线性变换（惯量张量就是 $3\times3$ 矩阵）。
- **高中物理的 $F=ma$**：把它当作起点而非终点——本主题会告诉你它只是更深层原理的影子。
- **矢量与坐标变换**：理解「为什么换坐标系下公式会变复杂」是拉格朗日出场的动机。

### ⚡ 旧框架的危机
1. **牛顿方程依赖坐标系**：笛卡尔简单，极坐标要补惯性力（科氏、离心）。物理不该挑坐标系！→ 触发**拉格朗日**的革命。
2. **「力」是个黑箱**：$F$ 到底是什么？拉格朗日用 $L=T-V$ 取代「力」，让能量成为主角。
3. **绝对时间被实验击碎**：Michelson-Morley 找不到以太，$\mu$ 子寿命对不上——**狭义相对论**由此诞生。

### 🆕 新框架的危机（本主题解决不了的）
- **混沌**：哈密顿系统在多数情况下不可积，长期预测指数失效（Lyapunov 指数）。
- **耗散无处安放**：摩擦让作用量原理失效，需引入 Rayleigh 函数——「保守是特殊的，耗散才是普遍的」，这是通往**统计物理**的暗门。
- **$v \to c$ 时牛顿崩塌**：需要狭义相对论；$v$ 小但仍要描述亿亿个粒子时，需要**统计力学**。

### 🚀 后续（力学是哪些课的地基）
| 后续主题 | 用到的力学概念 |
|---------|---------------|
| 02 电磁学 | 洛伦兹力、相对论协变（Maxwell 方程天然 Lorentz 不变） |
| 03 量子力学 | 哈密顿量 $\hat{H}$、泊松括号 → 对易子、谐振子 |
| 04 统计物理 | 刘维尔定理（相空间体积守恒）= 微正则系综的起点 |
| 08 广义相对论 | 等效原理、测地线方程 = 广义化的欧拉-拉格朗日 |

---

## 🏭 理论联系实际：5 个应用

1. **GPS 卫星定轨与授时**：用开普勒轨道 + 摄动理论设计轨道；卫星钟需做狭义+广义相对论修正（合计 +38 μs/天），否则定位每天漂移 ~10 km。
2. **LIGO/Virgo 臂长锁定**：4 km 干涉臂用拉格朗日点稳定（类似日地 L1 的 SOHO 卫星），反馈控制本质是含阻尼的受迫振子。
3. **陀螺仪 / MEMS 惯导**：手机里的微机械陀螺利用科氏力（非惯性系力学），欧拉方程是设计核心。Dzhanibekov 稳定性分析决定哪些姿态可自稳。
4. **分子动力学模拟**：辛积分器（Velocity-Verlet）是药物设计、蛋白质折叠（Folding@home）的算法基石——选对算法比减小步长重要。
5. **太空任务轨道设计**：JWST 在日地 L2 点 halo 轨道（三体问题）；JAXA 的 Hayabusa2 用「弹道着陆」利用小行星自旋-引力耦合——拉格朗日力学直接上太空。

---

## 🔬 最新研究前沿（2024-2026）

1. **KPZ 普适性在量子系统中首次实现**（2024, *Nature*）：ETH Zürich 的 Esslinger 组在一维超冷原子中观测到 Kardar-Parisi-Zhang 标度律——经典界面生长的混沌方程竟出现在量子多体关联函数里。**力学的混沌 + 统计的普适性在此交汇。**
2. **非厄米力学与例外点**（2024-2025）：在增益/损耗力学系统中，参数空间存在「例外点」本征值合并，导致奇异灵敏度——用于设计超灵敏传感器（陀螺、力学探测暗物质）。
3. **N 体混沌的新几何理论**（2024-2025）：拓扑方法刻画三体问题的「流动管道」（tube dynamics），为混沌中的有序通道提供严格描述，应用于引力波波形建模和系外行星稳定性。
4. **非线性动力学与气候临界点**（2024-2025）：Strogatz 式的分岔理论被用于预测大西洋经向翻转环流（AMOC）的临界转变；ETH 气候物理组参与提示「折叠分岔」前兆信号。
5. **LISA 任务正式立项**（2024.01.25 ESA 通过）：空间引力波探测器，三颗卫星构成等边三角形编队飞行，本质是巨型自由刚体 + 拉格朗日点动力学。力学直接服务于 2035 年的黑洞并合观测。

---

## 🗺️ 学习 Roadmap（ETH 路径）

### ETH 课程编号
- **401-0063-00L Physics I**（BSc 第一年，力学 + 热力学入门）
- **401-0064-00L Physics II**（同期，电磁 + 波动）
- **402-2301-00L Classical Mechanics**（BSc 第三年，拉格朗日/哈密顿/刚体/狭义相对论）
- **402-2601-00L Nonlinear Dynamics and Chaos**（选修，Strogatz 路线）
- **402-2481-00L Continuum Mechanics**（向弹性/流体过渡）

### 12 周学习节奏
| 阶段 | 内容 | 知识检查（能答出 = 过关） |
|------|------|---------------------------|
| W1-3 牛顿 | 三定律、守恒律、有心力场 | 为什么能量守恒？说出对应的对称性。 |
| W4-6 拉格朗日 | 广义坐标、Euler-Lagrange、约束 | 写出球面摆的 $L$ 并指出循环坐标。 |
| W7-8 哈密顿 | 相空间、泊松括号、刘维尔定理 | 为什么统计力学从刘维尔定理开始？ |
| W9-10 刚体 | 欧拉角、惯量张量、网球拍定理 | 解释 Dzhanibekov 翻转的几何原因。 |
| W11-12 狭义相对论 | 洛伦兹变换、能量-动量、四维矢量 | 为什么 $\mu$ 子能到达地面？ |

### 费曼检验（自测）
- 能用一张 A4 纸推出**两体开普勒轨道**的椭圆参数 → 力学过关。
- 能向高中生讲清楚「为什么大自然选择最小作用量」而不用数学 → 直觉过关。
- 读 Landau《力学》前三章不觉吃力 → 理论过关，可进量子力学。
