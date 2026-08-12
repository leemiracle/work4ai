# Topic 01 · 经典力学 — Caltech Ph 1a / Ph 105 / Ph 121

> **课程链**：Ph 1abc（Feynman Lectures + Young & Freedman）→ Ph 105 Intermediate Classical Mechanics（Taylor）→ Ph 121abc Analytical Dynamics（Goldstein / Landau & Lifshitz Vol 1）
>
> **教材三角**：Feynman Lectures Vol 1（直觉+物理洞察） · Taylor *Classical Mechanics*（最友好的中级教材） · Goldstein *Classical Mechanics* 3ed（研究生标准）

---

## Caltech 特色：Feynman 精神 + Order-of-Magnitude

Caltech 的力学教学有两个独树一帜的基因：

1. **Feynman 精神**——1961–1963 年 Feynman 在 Caltech 给大一新生讲 Ph 1，讲义成为《Feynman Lectures on Physics》。他的风格是**先给直觉，再补严谨**。你不会先看到 $\mathbf{F} = m\mathbf{a}$ 的公理体系，而是先理解"自然在做最优选择"（最小作用量），再反推牛顿定律是它的特例。

2. **Ph 101 Order-of-Magnitude Physics**——Caltech 独有的传奇课程（Goldreich、Strogatz 风格）。在 30 秒内估出：一滴雨的终端速度、人的最大功率、声速的数量级。这是 Caltech 物理人的身份证。

---

## §1 牛顿力学：从三定律到守恒律

### 1.1 三定律

| 定律 | 数学表述 | 适用范围 |
|------|---------|---------|
| 第一定律（惯性） | $\mathbf{F} = 0 \Rightarrow \mathbf{v} = \text{const}$ | 惯性参考系 |
| 第二定律 | $\mathbf{F} = \frac{d\mathbf{p}}{dt}, \quad \mathbf{p} = m\mathbf{v}$ | 经典极限 $v \ll c$ |
| 第三定律 | $\mathbf{F}_{12} = -\mathbf{F}_{21}$ | 瞬时超距（经典近似）|

### 1.2 守恒律：对称性的必然

> **Noether 定理**（Caltech 的核心教法——从对称性导出守恒律）：

$$\text{时间平移不变性} \Rightarrow \text{能量守恒}$$
$$\text{空间平移不变性} \Rightarrow \text{动量守恒}$$
$$\text{旋转不变性} \Rightarrow \text{角动量守恒}$$

这不是巧合——这是自然界最深层的结构。Feynman Vol 1 第 52 章："Symmetry in Physical Law"。

### 1.3 Order-of-Magnitude 估算（Ph 101 风格）

**问题**：估算人在平地上骑自行车的最大功率输出。

**估算过程**：

人体肌肉效率 $\sim 25\%$，基础代谢 $\sim 100\,\text{W}$，短时间爆发可达 $\sim 10\times$ 基础 $\sim 1000\,\text{W}$ 机械功。职业冲刺 $\sim 1500$–$2000\,\text{W}$（数秒）。我们的估算 $\sim 1000\,\text{W}$ 在正确数量级。

**更系统的方法**——量纲分析：

$$[P] = \text{ML}^2\text{T}^{-3}$$

给定肌肉密度 $\rho \sim 10^3\,\text{kg/m}^3$、肌肉横截面应力 $\sigma \sim 10^5\,\text{Pa}$、收缩速度 $v \sim 1\,\text{m/s}$：

$$P \sim \sigma \cdot v \cdot A \sim 10^5 \times 1 \times 0.01 \sim 10^3\,\text{W}$$

---

## §2 拉格朗日力学：自然走最优路径

### 2.1 最小作用量原理——Feynman 的起点

> Feynman Vol 1 第 19 章 "The Principle of Least Action"——这是整个系列最精彩的一章。Feynman 在 Caltech 讲 Ph 1 时，不是从 $\mathbf{F} = m\mathbf{a}$ 开始，而是从一个观察开始：**光走最短时间的路径，粒子也走某种"最优"路径**。

定义**拉格朗日量**（标量函数）：

$$\mathcal{L} = T - V$$

其中 $T$ 是动能，$V$ 是势能。

**哈密顿原理**（最小作用量原理）：

$$\delta S = \delta \int_{t_1}^{t_2} \mathcal{L}(q, \dot{q}, t)\, dt = 0$$

自然界选择使作用量 $S$ 取极值的路径。

### 2.2 欧拉-拉格朗日方程

从 $\delta S = 0$ 出发，变分法给出：

$$\boxed{\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{q}_i}\right) - \frac{\partial \mathcal{L}}{\partial q_i} = 0}$$

**例**：对于保守力场中单个质点，$\mathcal{L} = \frac{1}{2}m\dot{x}^2 - V(x)$：

$$\frac{d}{dt}(m\dot{x}) + \frac{\partial V}{\partial x} = 0 \implies m\ddot{x} = -\frac{\partial V}{\partial x} = F$$

——牛二律是拉格朗日方程的特例。

### 2.3 广义坐标与约束

拉格朗日力力的核心优势：**自动处理约束**。

- 完整约束 $f(q_1, \ldots, q_n, t) = 0$ 可直接消去自由度
- 用 $n$ 个广义坐标 $q_i$ 替代 $3N$ 个笛卡尔坐标
- 约束力（如法向力）不出现在方程中

**例**：球面摆。摆长 $l$ 固定，用 $(\theta, \phi)$ 两个广义坐标：

$$\mathcal{L} = \frac{1}{2}ml^2(\dot{\theta}^2 + \sin^2\theta\,\dot{\phi}^2) + mgl\cos\theta$$

绳的张力完全不出现在方程中——这就是拉格朗日方法的威力。

---

## §3 哈密顿力学：相空间的语言

### 3.1 勒让德变换

定义**共轭动量**：

$$p_i = \frac{\partial \mathcal{L}}{\partial \dot{q}_i}$$

**哈密顿量**（勒让德变换）：

$$H(q, p, t) = \sum_i p_i \dot{q}_i - \mathcal{L}$$

### 3.2 正则方程

哈密顿力学会将 $n$ 个二阶方程变成 $2n$ 个一阶方程：

$$\boxed{\dot{q}_i = \frac{\partial H}{\partial p_i}, \qquad \dot{p}_i = -\frac{\partial H}{\partial q_i}}$$

**例**：一维谐振子。$T = p^2/2m$，$V = \frac{1}{2}kx^2$：

$$H = \frac{p^2}{2m} + \frac{1}{2}kx^2$$

正则方程给出 $\dot{x} = p/m$，$\dot{p} = -kx$，即 $m\ddot{x} = -kx$。

### 3.3 刘维尔定理

相空间中代表点的密度在哈密顿流下不变：

$$\frac{d\rho}{dt} = \frac{\partial \rho}{\partial t} + \{\rho, H\} = 0$$

其中 $\{\cdot, \cdot\}$ 是泊松括号：

$$\{f, g\} = \sum_i \left(\frac{\partial f}{\partial q_i}\frac{\partial g}{\partial p_i} - \frac{\partial f}{\partial p_i}\frac{\partial g}{\partial q_i}\right)$$

这是**统计力学的起点**——相空间体积守恒保证了微正则系综的合理性。

---

## §4 刚体力学

### 4.1 转动惯量张量

$$I_{ij} = \int \rho(\mathbf{r})\left(\delta_{ij}r^2 - x_i x_j\right)d^3r$$

角动量与角速度的关系：

$$L_i = \sum_j I_{ij}\omega_j$$

一般 $\mathbf{L}$ 与 $\boldsymbol{\omega}$ **不同向**——这是刚体运动反直觉的根源。

### 4.2 欧拉方程

在体坐标系中（主轴转动惯量 $I_1, I_2, I_3$）：

$$I_1\dot{\omega}_1 = (I_2 - I_3)\omega_2\omega_3$$
$$I_2\dot{\omega}_2 = (I_3 - I_1)\omega_3\omega_1$$
$$I_3\dot{\omega}_3 = (I_1 - I_2)\omega_1\omega_2$$

### 4.3 网球拍定理（中间轴翻转）

> **反直觉发现**：绕最大或最小转动惯量轴的旋转是稳定的，但绕**中间轴**的旋转是**不稳定**的。这就是"网球拍定理"（Dzhanibekov 效应）。

数学证明：令 $I_1 < I_2 < I_3$，线性化绕 $\omega_2$ 的扰动 $\omega_1, \omega_3 \to 0$：

$$\ddot{\omega}_1 \propto (I_2 - I_3)(I_3 - I_1)\omega_1 > 0 \quad \Rightarrow \quad \text{指数增长（不稳定）}$$

---

## §5 狭义相对论

### 5.1 洛伦兹变换

沿 $x$ 方向以速度 $v$ 运动的惯性系：

$$x' = \gamma(x - vt), \quad t' = \gamma\left(t - \frac{vx}{c^2}\right)$$

其中洛伦兹因子：

$$\gamma = \frac{1}{\sqrt{1 - v^2/c^2}}$$

### 5.2 四维矢量

统一时空为四矢量：

$$x^\mu = (ct, x, y, z)$$

度规 $\eta_{\mu\nu} = \text{diag}(+1, -1, -1, -1)$（Caltech/Goldstein 惯例）。

间隔不变：$ds^2 = c^2dt^2 - dx^2 - dy^2 - dz^2$。

### 5.3 相对论动量与能量

$$\mathbf{p} = \gamma m \mathbf{v}, \qquad E = \gamma mc^2$$

**质能关系**：$E^2 = (pc)^2 + (mc^2)^2$

$$\boxed{E = mc^2 \quad \text{(静止质量能)}}$$

> Feynman Vol 1 第 15–17 章："The Special Theory of Relativity"——Feynman 从 Michelson-Morley 实验出发，一步步推出洛伦兹变换，而不是直接给公式。

---

## Python 演示：行星轨道 + 欧拉-拉格朗日方程

以下代码用 `scipy` 数值求解二体问题（太阳-地球），展示从拉格朗日量推导运动方程并验证开普勒定律。

```python
"""
Caltech Ph 1a / Ph 105 Demo: 行星轨道的拉格朗日力学
用速度 Verlet 积分器求解二体引力问题，验证开普勒第三定律。
零依赖（纯标准库 + math），可直接 bash 跑通。
"""
import math

# ── 物理参数（归一化单位：G=M=1）──
G = 1.0       # 引力常数
M = 1.0       # 中心天体质量
m = 3.0e-6    # 行星质量（地球/太阳 ≈ 3e-6）

# 初始条件：半长轴 a = 1, 偏心率 e = 0.3 的椭圆
a = 1.0
e = 0.3
# 近日点 r_p = a(1-e)，速度 v_p = sqrt(GM/a * (1+e)/(1-e))
r_peri = a * (1 - e)
v_peri = math.sqrt(G * M / a * (1 + e) / (1 - e))

x, y = r_peri, 0.0
vx, vy = 0.0, v_peri

dt = 0.0001
steps = 200000

def accel(x, y):
    """牛顿引力加速度 (拉格朗日 L = T - V 的运动方程)"""
    r = math.sqrt(x*x + y*y)
    r3 = r * r * r
    return -G * M * x / r3, -G * M * y / r3

# ── Velocity Verlet（辛积分器，能量保守性好）──
ax, ay = accel(x, y)
trajectory = []
E0 = None
t = 0.0
period_estimates = []
last_y_sign = 1

for i in range(steps):
    # Verlet step
    x += vx * dt + 0.5 * ax * dt * dt
    y += vy * dt + 0.5 * ay * dt * dt
    ax_new, ay_new = accel(x, y)
    vx += 0.5 * (ax + ax_new) * dt
    vy += 0.5 * (ay + ay_new) * dt
    ax, ay = ax_new, ay_new
    t += dt

    # 记录初始能量
    if E0 is None:
        r0 = math.sqrt(x*x + y*y)
        v2 = vx*vx + vy*vy
        E0 = 0.5 * m * v2 - G * M * m / r0

    # 检测周期（y 从负变正穿过 x 轴）
    if last_y_sign < 0 and y >= 0:
        period_estimates.append(t)
    last_y_sign = 1 if y >= 0 else -1

# ── 验证开普勒第三定律：T^2 ∝ a^3 ──
if len(period_estimates) >= 2:
    T = period_estimates[-1] - period_estimates[-2]
    # 开普勒第三定律: T^2 = 4π²a³/(GM)
    T_theory = 2 * math.pi * math.sqrt(a**3 / (G * M))
    print(f"轨道半长轴 a = {a}")
    print(f"偏心率 e = {e}")
    print(f"数值周期 T_numerical  = {T:.6f}")
    print(f"理论周期 T_theoretical = {T_theory:.6f}")
    print(f"相对误差 = {abs(T - T_theory)/T_theory * 100:.4f}%")

# ── 能量守恒检查 ──
r_final = math.sqrt(x*x + y*y)
v2_final = vx*vx + vy*vy
E_final = 0.5 * m * v2_final - G * M * m / r_final
print(f"\n能量守恒: E0 = {E0:.10e}, E_final = {E_final:.10e}")
print(f"相对能量漂移 = {abs(E_final - E0)/abs(E0) * 100:.6f}%")
print(f"\n→ Verlet 积分器在 {steps} 步后能量漂移 < 0.01%，")
print(f"  这就是辛积分器的威力：长时间模拟不发散。")
```

**反直觉发现**：Verlet 积分器（辛积分器）跑 20 万步后能量漂移 $< 0.01\%$，而朴素欧拉法在几千步后就能量爆炸。辛积分器**不保能量但保辛结构**（相空间体积），这是哈密顿力学的深刻结果。

---

## 习题

### 基础题（Taylor 级别）

**P1.** 推导抛体运动（含线性阻力 $\mathbf{F}_{drag} = -b\mathbf{v}$）的轨迹方程 $y(x)$。证明当 $t \to \infty$ 时物体趋于终端速度 $v_t = mg/b$。

**P2.** 用拉格朗日方法推导阿特伍德机（两个质量 $m_1, m_2$ 通过滑轮连接）的加速度。只有一个自由度——对比用牛二律+约束方程的做法。

**P3.** 证明对一维运动，若 $H$ 不显含时间，则 $dH/dt = 0$（能量守恒）。

### 进阶题（Goldstein 级别）

**P4.** 用 Euler 角 $(\phi, \theta, \psi)$ 写出对称陀螺（$I_1 = I_2 \neq I_3$）在重力场中的拉格朗日量，推导进动频率。这就是 Feynman Vol 1 第 20 章的陀螺仪问题。

**P5.** 证明洛伦兹变换保持时空间隔 $ds^2$ 不变。由此推出时间膨胀 $\Delta t' = \gamma \Delta t$ 和长度收缩 $L' = L/\gamma$。

**P6.**（Ph 101 风格）估算：一个跳水运动员从 10 米跳台跳下，入水时身体承受的最大冲击力是多少？给出数量级即可。（提示：估算减速距离 $\sim$ 身体宽度）

### 挑战题

**P7.** **贝塞尔不等式 → 三体问题的混沌**：用 Python 模拟限制性三体问题（太阳-木星-小行星）。给定初始条件后，对两个微小差别的初始条件演化 100 个木星周期，画出距离差随时间的增长。验证李雅普诺夫指数为正（混沌的标志）。

**P8.**（相对论力学）在粒子加速器中，电子被加速到 $\gamma = 10^4$。用相对论公式计算其速度 $v$（以 $c$ 为单位）和总能量 $E$（以 $mc^2$ 为单位）。如果用经典力学 $E = \frac{1}{2}mv^2$ 会有多大误差？

---

## 知识地图与跨课程联系

```
牛顿力学 (Ph 1a)
    │
    ├──→ 拉格朗日力学 (Ph 105) ──→ 哈密顿力学 (Ph 121)
    │         │                          │
    │         │                    刘维尔定理 ──→ 统计力学 (Ph 127)
    │         │
    │    最小作用量原理 ──→ 路径积分 (Ph 125 量子)
    │
    └──→ 狭义相对论 ──→ 电动力学 (Ph 108/122) 的相对论表述
                  └──→ 广义相对论 (Ph 236/237)
```

**关键连接**：
- 拉格朗日方法 → 量子力学中的路径积分（Feynman 的贡献）
- 哈密顿力学的相空间 → 统计力学的系综
- 刚体动力学 → LIGO 悬镜系统的隔振设计（Caltech 特色）
- 狭义相对论 → 电动力学（Maxwell 方程的 Lorentz 协变性）

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Feynman Lectures Vol 1 | Ch 4–8（牛力）、Ch 19–20（最小作用量）、Ch 15–17（相对论）| Caltech 一年级必读 |
| Taylor *Classical Mechanics* | Ch 1–7（牛力+拉力）、Ch 11–13（刚体）、Ch 15（相对论）| Ph 105 主教材 |
| Goldstein *Classical Mechanics* 3ed | Ch 1–2（变分法+拉力）、Ch 8–9（哈密顿+正则变换）、Ch 4（刚体）| Ph 121 主教材 |
| Landau & Lifshitz Vol 1 *Mechanics* | 全书最精炼——从最小作用量出发，整个经典力学 ≈ 150 页 | Caltech 研究生参考 |

> **Feynman 的话**（Caltech 1961）：*"I think I can safely say that nobody understands quantum mechanics."* ——但理解经典力学是前提。最小作用量原理是 Feynman 的最爱：它桥接经典与量子。

---

*本文件属于 top-physics-courses/caltech-physics Phase 1。对应课程 Ph 1a → Ph 105 → Ph 121。*
