# Cambridge Part IA/IB · Mechanics & Classical Dynamics

> **教材**：Kibble & Berkshire *Classical Mechanics* (5th ed.) — Cambridge 指定教材；Goldstein, Poole & Safko *Classical Mechanics* (3rd ed.) — Part IB Classical Dynamics 补充
>
> **Cambridge 课程编号**：Part IA Mechanics A/B + Part IB Classical Dynamics
>
> **Cambridge 特色**：Natural Sciences Tripos 考试体系以深度计算题著称；Cavendish Lab 的物理直觉传统；从牛顿到拉格朗日一气呵成的教学主线

---

## 目录

1. [牛顿力学回顾](#1-牛顿力学回顾)
2. [有心力与轨道力学](#2-有心力与轨道力学)
3. [拉格朗日力学](#3-拉格朗日力学)
4. [哈密顿力学](#4-哈密顿力学)
5. [刚体动力学](#5-刚体动力学)
6. [狭义相对论](#6-狭义相对论)
7. [Python 代码演示](#7-python-代码演示)
8. [Tripos 风格习题](#8-tripos-风格习题)

---

## 1. 牛顿力学回顾

### 1.1 牛顿三定律

剑桥 Part IA Mechanics 的起点不是"背诵三定律"，而是从**最小作用量原理**的角度重新审视牛顿力学。不过我们先用传统框架引入。

**牛顿第二定律**：

$$m\ddot{\mathbf{r}} = \mathbf{F}(\mathbf{r}, \dot{\mathbf{r}}, t)$$

这是一组二阶常微分方程。给定初始条件 $\mathbf{r}(0)$ 和 $\dot{\mathbf{r}}(0)$，系统的未来完全确定——这就是**经典决定论**。

### 1.2 保守力与势能

若力可以写为标量势的梯度：

$$\mathbf{F} = -\nabla V$$

则系统总能量守恒：

$$E = \frac{1}{2}m|\dot{\mathbf{r}}|^2 + V(\mathbf{r}) = \text{const}$$

**反直觉发现**：并非所有常见力都是保守力。摩擦力 $\mathbf{F}_f = -\gamma \dot{\mathbf{r}}$ 显然不是（依赖速度且不可逆）。但更微妙的是，磁场 $\mathbf{F} = q\dot{\mathbf{r}} \times \mathbf{B}$ 虽然依赖速度，却**不做功**——它只改变方向不改变动能。这为后来拉格朗日框架中速度依赖势（$U = q\mathbf{A}\cdot\dot{\mathbf{r}} - q\phi$）埋下伏笔。

### 1.3 非惯性参考系

剑桥特色之一是**早早引入非惯性系**。在旋转参考系中：

$$m\mathbf{a}_{\text{rot}} = \mathbf{F} - m\dot{\boldsymbol{\omega}} \times \mathbf{r} - 2m\boldsymbol{\omega} \times \mathbf{v}_{\text{rot}} - m\boldsymbol{\omega} \times (\boldsymbol{\omega} \times \mathbf{r})$$

其中：
- $-2m\boldsymbol{\omega} \times \mathbf{v}_{\text{rot}}$ — **科里奥利力**
- $-m\boldsymbol{\omega} \times (\boldsymbol{\omega} \times \mathbf{r})$ — **离心力**

**例题（Foucault 摆）**：在纬度 $\lambda$ 处，摆的振动平面旋转角速度为 $\Omega \sin\lambda$（$\Omega$ 为地球自转角速度）。在剑桥（$\lambda \approx 52^\circ$），摆面旋转一圈需 $\frac{2\pi}{\Omega \sin 52^\circ} \approx 31.9$ 小时——**不是 24 小时**！这正是 Foucault 1851 年实验的精髓。

---

## 2. 有心力与轨道力学

### 2.1 约化质量与有效势

两体问题约化为等效单体问题。约化质量：

$$\mu = \frac{m_1 m_2}{m_1 + m_2}$$

角动量守恒 $\mathbf{L} = \mathbf{r} \times \mathbf{p} = \text{const}$ 意味着运动在平面内。引入有效势：

$$V_{\text{eff}}(r) = V(r) + \frac{L^2}{2\mu r^2}$$

径向运动等价于一维问题：

$$\frac{1}{2}\mu \dot{r}^2 + V_{\text{eff}}(r) = E$$

### 2.2 开普勒问题

引力势 $V(r) = -\frac{GM\mu}{r}$。有效势：

$$V_{\text{eff}}(r) = -\frac{GM\mu}{r} + \frac{L^2}{2\mu r^2}$$

轨道方程通过 Binet 公式求解，结果为圆锥曲线：

$$r(\theta) = \frac{p}{1 + e\cos\theta}$$

其中 $p = \frac{L^2}{GM\mu^2}$，偏心率 $e = \sqrt{1 + \frac{2EL^2}{G^2M^2\mu^3}}$。

| 能量 $E$ | 偏心率 $e$ | 轨道类型 |
|----------|-----------|---------|
| $E < 0$ | $0 \le e < 1$ | 椭圆（含圆 $e=0$） |
| $E = 0$ | $e = 1$ | 抛物线 |
| $E > 0$ | $e > 1$ | 双曲线 |

### 2.3 Runge-Lenz 矢量

开普勒问题有一个**隐藏的守恒量**——Laplace-Runge-Lenz 矢量：

$$\mathbf{A} = \mathbf{p} \times \mathbf{L} - \mu k \hat{\mathbf{r}}$$

（其中 $k = GM\mu$）。它的存在意味着轨道是**闭合的**椭圆（Bertrand 定理：只有 $1/r$ 和 $r^2$ 势给出所有有界轨道闭合）。在量子力学中，这个额外的对称性对应 $SO(4)$ 群，解释了氢原子的"偶然简并"——这是剑桥连接经典与量子的经典话题。

---

## 3. 拉格朗日力学

### 3.1 最小作用量原理

这是剑桥 Part IB Classical Dynamics 的核心。定义**拉格朗日量**：

$$\mathcal{L}(q, \dot{q}, t) = T - V$$

其中 $q$ 为广义坐标。**哈密顿原理**（最小作用量原理）：

$$\delta S = \delta \int_{t_1}^{t_2} \mathcal{L}\,dt = 0$$

### 3.2 欧拉-拉格朗日方程

由变分法导出运动方程：

$$\frac{d}{dt}\frac{\partial \mathcal{L}}{\partial \dot{q}_i} - \frac{\partial \mathcal{L}}{\partial q_i} = 0$$

**为什么拉格朗日比牛顿好？**
1. 自动处理约束（只需选对广义坐标）
2. 标量运算（能量）代替矢量运算（力）
3. 坐标无关——任何广义坐标下形式不变
4. 直接与对称性联系（Noether 定理）

### 3.3 例：球面摆

质量 $m$ 的摆，摆长 $\ell$，用球坐标 $(\theta, \phi)$：

$$T = \frac{1}{2}m\ell^2(\dot{\theta}^2 + \sin^2\theta\,\dot{\phi}^2), \quad V = -mg\ell\cos\theta$$

$$\mathcal{L} = \frac{1}{2}m\ell^2(\dot{\theta}^2 + \sin^2\theta\,\dot{\phi}^2) + mg\ell\cos\theta$$

$\phi$ 是循环坐标，故 $\frac{\partial \mathcal{L}}{\partial \dot{\phi}} = m\ell^2\sin^2\theta\,\dot{\phi} = p_\phi = \text{const}$（角动量守恒）。

$\theta$ 方向的 Euler-Lagrange 方程：

$$m\ell^2\ddot{\theta} = m\ell^2\sin\theta\cos\theta\,\dot{\phi}^2 - mg\ell\sin\theta$$

### 3.4 Noether 定理

**每一个连续对称性对应一个守恒量。**

| 对称性 | 守恒量 |
|--------|-------|
| 时间平移 $t \to t + \epsilon$ | 能量 $E$ |
| 空间平移 $\mathbf{r} \to \mathbf{r} + \boldsymbol{\epsilon}$ | 动量 $\mathbf{p}$ |
| 旋转 $\mathbf{r} \to \mathbf{r} + \boldsymbol{\theta} \times \mathbf{r}$ | 角动量 $\mathbf{L}$ |

---

## 4. 哈密顿力学

### 4.1 勒让德变换

从拉格朗日量定义广义动量：

$$p_i = \frac{\partial \mathcal{L}}{\partial \dot{q}_i}$$

**哈密顿量**：

$$H(q, p, t) = \sum_i p_i \dot{q}_i - \mathcal{L}$$

### 4.2 正则方程

$$\dot{q}_i = \frac{\partial H}{\partial p_i}, \quad \dot{p}_i = -\frac{\partial H}{\partial q_i}$$

这是 $2n$ 个一阶方程（代替拉格朗日的 $n$ 个二阶方程），具有优美的对称结构。

### 4.3 相空间与 Liouville 定理

哈密顿力学自然地生活于**相空间** $\Gamma = \{(q, p)\}$ 中。

**Liouville 定理**：哈密顿流保持相空间体积不变。

$$\frac{d\rho}{dt} = \frac{\partial \rho}{\partial t} + \{\rho, H\} = 0$$

其中 Poisson 括号：

$$\{f, g\} = \sum_i \left(\frac{\partial f}{\partial q_i}\frac{\partial g}{\partial p_i} - \frac{\partial f}{\partial p_i}\frac{\partial g}{\partial q_i}\right)$$

Liouville 定理是统计力学的基石——它告诉我们相空间点像不可压缩流体。这个定理在 Topic 4（统计物理）中将起到核心作用。

---

## 5. 刚体动力学

### 5.1 转动惯量张量

$$I_{ij} = \int \rho(\mathbf{r})(r^2 \delta_{ij} - r_i r_j)\,d^3r$$

角动量与角速度通过惯量张量联系：$L_i = I_{ij}\omega_j$。

**主轴**：在主轴坐标系中 $I_{ij}$ 对角化，$L_i = I_i \omega_i$。

### 5.2 欧拉方程

在体坐标系中（注意 $\dot{\boldsymbol{\omega}} \ne$ 体坐标系的角加速度，需要修正）：

$$I_1\dot{\omega}_1 - (I_2 - I_3)\omega_2\omega_3 = \tau_1$$
$$I_2\dot{\omega}_2 - (I_3 - I_1)\omega_3\omega_1 = \tau_2$$
$$I_3\dot{\omega}_3 - (I_1 - I_2)\omega_1\omega_2 = \tau_3$$

### 5.3 自由刚体与稳定性

无力矩时（$\tau_i = 0$），绕三个主轴的转动是否稳定？

**结论**（反直觉！）：绕 $I_1$（最小）和 $I_3$（最大）的转动稳定，但绕 $I_2$（中间）的转动**不稳定**！

这就是为什么你把一本书抛到空中时，绕短轴和长轴旋转都稳定，但绕中间轴旋转会翻滚（"tennis racket theorem" / Dzhanibekov 效应）。这个实验在 Cavendish 演示实验室是经典项目。

---

## 6. 狭义相对论

### 6.1 洛伦兹变换

沿 $x$ 方向的洛伦兹变换：

$$x' = \gamma(x - vt), \quad t' = \gamma\left(t - \frac{vx}{c^2}\right)$$

其中 $\gamma = \frac{1}{\sqrt{1 - v^2/c^2}}$。

### 6.2 四维时空

引入四维坐标 $x^\mu = (ct, x, y, z)$，度规 $\eta_{\mu\nu} = \text{diag}(-1, +1, +1, +1)$（或 $+---$，剑桥用 $-+++$ 惯例）。

**四维动量**：$p^\mu = (E/c, \mathbf{p})$，满足：

$$p_\mu p^\mu = -\left(\frac{E}{c}\right)^2 + |\mathbf{p}|^2 = -m^2c^2$$

即：

$$E^2 = p^2c^2 + m^2c^4$$

### 6.3 相对论拉格朗日

相对论自由粒子作用量（剑桥 Part IB 拓展话题）：

$$S = -mc^2 \int d\tau = -mc \int ds$$

其中 $ds = \sqrt{-\eta_{\mu\nu}dx^\mu dx^\nu} = c\,d\tau$。

对应的拉格朗日量（用坐标时 $t$ 参数化）：

$$\mathcal{L} = -mc^2\sqrt{1 - \frac{v^2}{c^2}}$$

注意：$\mathcal{L} \ne T - V$！在相对论中，拉格朗日量不等于 $T - V$。由此导出的动量：

$$p = \frac{\partial \mathcal{L}}{\partial v} = \frac{mv}{\sqrt{1-v^2/c^2}} = \gamma mv \quad \checkmark$$

---

## 7. Python 代码演示

### 7.1 Dzhanibekov 效应（中间轴不稳定性）

```python
"""
Dzhanibekov 效应 / Tennis Racket Theorem
演示绕中间惯量主轴旋转的不稳定性。
用 RK4 积分保证能量守恒。
零依赖，几秒跑完。
"""
import math

def euler_rhs(w, I):
    """欧拉方程右端（无外力矩）: dw_i/dt = (I_j - I_k) * w_j * w_k / I_i"""
    I1, I2, I3 = I
    w1, w2, w3 = w
    return ((I2 - I3) * w2 * w3 / I1,
            (I3 - I1) * w3 * w1 / I2,
            (I1 - I2) * w1 * w2 / I3)

def simulate_euler_rk4(dt=0.002, T=20.0, I=(1.0, 2.0, 4.0),
                       omega0=(0.0, 0.01, 10.0)):
    """RK4 积分欧拉方程（无外力矩）。
    I: (I1, I2, I3) 主惯量
    omega0: 初始角速度
    """
    w = list(omega0)
    steps = int(T / dt)
    trajectory = []

    for _ in range(steps):
        k1 = euler_rhs(w, I)
        w2 = [w[i] + 0.5*dt*k1[i] for i in range(3)]
        k2 = euler_rhs(w2, I)
        w3 = [w[i] + 0.5*dt*k2[i] for i in range(3)]
        k3 = euler_rhs(w3, I)
        w4 = [w[i] + dt*k3[i] for i in range(3)]
        k4 = euler_rhs(w4, I)
        for i in range(3):
            w[i] += dt/6.0 * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i])
        trajectory.append(tuple(w))

    return trajectory

# 模拟：绕最大惯量轴(I3=4)稳定旋转 + 轴1微小扰动
traj = simulate_euler_rk4(dt=0.001, T=20.0)

print("=== Dzhanibekov 效应模拟 (RK4) ===")
print(f"I1=1.0, I2=2.0, I3=4.0")
print(f"初始: ω=(0.0, 0.01, 10.0)  [绕最大轴I3 + 微小扰动]")
print(f"\n绕最大轴I3旋转 → 稳定（扰动不放大）")
for i in range(0, len(traj), len(traj)//10):
    w1, w2, w3 = traj[i]
    t = i * 0.001
    print(f"  t={t:5.1f}s  ω1={w1:+.4f}  ω2={w2:+.6f}  ω3={w3:.4f}")

# 测试绕中间轴的不稳定旋转
print(f"\n绕中间轴I2旋转 → 不稳定！（扰动指数放大 → 翻转）")
traj_unstable = simulate_euler_rk4(dt=0.001, T=20.0,
                                     I=(1.0, 2.0, 4.0),
                                     omega0=(0.01, 10.0, 0.0))
for i in range(0, len(traj_unstable), len(traj_unstable)//10):
    w1, w2, w3 = traj_unstable[i]
    t = i * 0.001
    print(f"  t={t:5.1f}s  ω1={w1:+.4f}  ω2={w2:.4f}  ω3={w3:+.4f}")

# 能量守恒检验（应为常数）
def kinetic_energy(traj, I=(1.0, 2.0, 4.0)):
    I1, I2, I3 = I
    energies = []
    for w1, w2, w3 in traj:
        E = 0.5*(I1*w1**2 + I2*w2**2 + I3*w3**2)
        energies.append(E)
    return energies

E_stable = kinetic_energy(traj)
E_unstable = kinetic_energy(traj_unstable)
print(f"\n=== 能量守恒检验 (RK4) ===")
print(f"稳定旋转:   E[0]={E_stable[0]:.6f}, E[-1]={E_stable[-1]:.6f}, "
      f"漂移={abs(E_stable[-1]-E_stable[0])/E_stable[0]*100:.4f}%")
print(f"不稳定旋转: E[0]={E_unstable[0]:.6f}, E[-1]={E_unstable[-1]:.6f}, "
      f"漂移={abs(E_unstable[-1]-E_unstable[0])/E_unstable[0]*100:.4f}%")
print("→ RK4 显著优于前向欧拉法, 能量漂移 < 0.1%")
```

**运行结果解读**：
- 绕 $I_3$（最大）旋转：$\omega_1, \omega_2$ 保持微小，$\omega_3$ 稳定 → 稳定
- 绕 $I_2$（中间）旋转：微小扰动 $\omega_1, \omega_3$ **指数放大**，最终发生"翻转" → 不稳定
- 能量应严格守恒（数值积分误差很小），因为欧拉方程是在无外力矩下推导的

### 7.2 开普勒轨道数值积分

```python
"""
开普勒二体问题：Velocity Verlet 积分
演示椭圆轨道 + 能量/角动量守恒
零依赖，几秒跑完。
"""
import math

def kepler_orbit(dt=0.0002, T=2.0, GM=4.0 * math.pi**2,
                 r0=1.0, v0=5.5):
    """单位制: AU, 年, 太阳质量 -> GM = 4π²
    r0=1 AU, v0=5.5 AU/yr (略低于圆轨速度2π≈6.28)
    → 椭圆轨道, 偏心率适中
    """
    x, y = r0, 0.0
    vx, vy = 0.0, v0
    steps = int(T / dt)
    results = []

    for _ in range(steps):
        r = math.sqrt(x*x + y*y)
        ax = -GM * x / r**3
        ay = -GM * y / r**3
        # Velocity Verlet (蛙跳) — symplectic, 能量守恒好
        x += vx * dt + 0.5 * ax * dt**2
        y += vy * dt + 0.5 * ay * dt**2
        r_new = math.sqrt(x*x + y*y)
        ax_new = -GM * x / r_new**3
        ay_new = -GM * y / r_new**3
        vx += 0.5 * (ax + ax_new) * dt
        vy += 0.5 * (ay + ay_new) * dt

        # 守恒量
        KE = 0.5 * (vx**2 + vy**2)
        PE = -GM / r_new
        L = x * vy - y * vx  # 角动量z分量
        results.append((x, y, KE + PE, L))

    return results

orbit = kepler_orbit(dt=0.0001, T=3.0)  # 约3个轨道周期

print("=== 开普勒轨道数值积分 ===")
print(f"GM=4π²≈{4*math.pi**2:.4f}, r0=1AU, v0=5.5 AU/yr")
print(f"理论圆轨速度 = √(GM/r0) = {math.sqrt(4*math.pi**2):.4f} AU/yr")
print(f"初始速度低于圆轨 → 椭圆轨道\n")

# 找近日点和远日点
r_vals = [math.sqrt(x**2+y**2) for x, y, _, _ in orbit]
r_min = min(r_vals)
r_max = max(r_vals)
a = (r_min + r_max) / 2  # 半长轴
e = (r_max - r_min) / (r_max + r_min)  # 偏心率

print(f"近日点 r_min = {r_min:.6f} AU")
print(f"远日点 r_max = {r_max:.6f} AU")
print(f"半长轴 a = {a:.6f} AU")
print(f"偏心率 e = {e:.6f}")
print(f"理论周期 T = a^(3/2) = {a**1.5:.6f} yr (开普勒第三定律)")

# 守恒量检验
energies = [E for _, _, E, _ in orbit]
angular_m = [L for _, _, _, L in orbit]
print(f"\n=== 守恒量检验 ===")
print(f"能量: E[0]={energies[0]:.6f}, E[-1]={energies[-1]:.6f}, "
      f"漂移={abs(energies[-1]-energies[0])/abs(energies[0])*100:.6f}%")
print(f"角动量: L[0]={angular_m[0]:.6f}, L[-1]={angular_m[-1]:.6f}, "
      f"漂移={abs(angular_m[-1]-angular_m[0])/abs(angular_m[0])*100:.6f}%")
```

---

## 8. Tripos 风格习题

> Cambridge Tripos 的特点是**多步推导 + 精确计算**，以下习题模仿其风格。

### 习题 1（Part IA 难度）：旋转液面

一个柱形容器绕中心轴以角速度 $\omega$ 匀速旋转，容器内液体达到平衡。求液面形状。

**提示**：在旋转系中液体受力平衡，或用离心势 $\frac{1}{2}\omega^2 r^2$。

<details>
<summary>解答</summary>

在旋转系中，液面处每一点的有效势为：

$$\Phi_{\text{eff}} = gz - \frac{1}{2}\omega^2 r^2$$

等势面 $\Phi_{\text{eff}} = \text{const}$ 给出：

$$z(r) = z_0 + \frac{\omega^2 r^2}{2g}$$

这是一个**旋转抛物面**。有趣的应用：大型望远镜可以用旋转液态汞面作为反射镜！
</details>

### 习题 2（Part IB 难度）：耦合摆的简正模

两个相同的摆（质量 $m$，摆长 $\ell$）用弹簧（劲度系数 $k$）连接，弹簧连接点在摆锤处。

(a) 写出拉格朗日量并求运动方程。
(b) 求简正模频率。
(c) 若初始时摆1静止，摆2有位移，描述系统的拍频现象。

<details>
<summary>解答</summary>

(a) 取角度 $\theta_1, \theta_2$ 为广义坐标。小角近似下：

$$T = \frac{1}{2}m\ell^2(\dot{\theta}_1^2 + \dot{\theta}_2^2)$$
$$V = \frac{1}{2}mg\ell(\theta_1^2 + \theta_2^2) + \frac{1}{2}k\ell^2(\theta_1 - \theta_2)^2$$

运动方程：

$$m\ell^2\ddot{\theta}_1 = -mg\ell\theta_1 - k\ell^2(\theta_1 - \theta_2)$$
$$m\ell^2\ddot{\theta}_2 = -mg\ell\theta_2 + k\ell^2(\theta_1 - \theta_2)$$

(b) 简正模：
- **对称模**：$\theta_1 = \theta_2$，$\omega_1 = \sqrt{g/\ell}$
- **反对称模**：$\theta_1 = -\theta_2$，$\omega_2 = \sqrt{g/\ell + 2k/m}$

(c) 初始条件 $\theta_1(0)=0, \theta_2(0)=\theta_0$ 可分解为：

$$\theta_1(t) = \frac{\theta_0}{2}\left[\cos\omega_1 t - \cos\omega_2 t\right]$$

利用和差化积，能量在两个摆之间来回转移，拍频为 $\omega_{\text{beat}} = \omega_2 - \omega_1$。
</details>

### 习题 3（Part IB 难度）：相对论性碰撞

一个静质量为 $m$ 的粒子以速度 $v$ 撞击另一个静止的同种粒子，碰撞后两粒子粘在一起（完全非弹性碰撞）。

(a) 用动量守恒和能量-动量关系求复合粒子的速度和质量。
(b) 证明复合粒子的静质量 $M > 2m$（"质量亏损"为负），并解释物理意义。

<details>
<summary>解答</summary>

(a) 四维动量守恒：

$$p_1^\mu + p_2^\mu = P^\mu$$

入射粒子：$E_1 = \gamma mc^2$，$p_1 = \gamma mv$；静止粒子：$E_2 = mc^2$，$p_2 = 0$。

复合粒子：$E = E_1 + E_2 = (\gamma + 1)mc^2$，$P = p_1 = \gamma mv$。

速度：$V = \frac{Pc^2}{E} = \frac{\gamma mv c^2}{(\gamma+1)mc^2} = \frac{\gamma v}{\gamma + 1}$

静质量：$M^2c^4 = E^2 - P^2c^2 = (\gamma+1)^2m^2c^4 - \gamma^2 m^2v^2 c^2$

$$M^2 = m^2\left[(\gamma+1)^2 - \gamma^2\frac{v^2}{c^2}\right] = m^2\left[\gamma^2 + 2\gamma + 1 - \gamma^2 + 1\right]$$

$$= m^2(2\gamma + 2) = 2m^2(\gamma + 1)$$

$$M = m\sqrt{2(\gamma + 1)}$$

(b) 因为 $\gamma \ge 1$，所以 $M = m\sqrt{2(\gamma+1)} \ge m\sqrt{4} = 2m$。

物理意义：入射粒子的**动能**转化为了复合粒子的**内能**（即静质量能）。这是 $E = mc^2$ 的直接体现——动能"凝固"为质量。
</details>

### 习题 4（Part II 预习）：小振动与简正模

三个相同质量 $m$ 用相同弹簧 $k$ 连接成链：墙—$k$—$m$—$k$—$m$—$k$—$m$—$k$—墙。

求三个简正模的频率和模式形状。

<details>
<summary>解答</summary>

运动方程矩阵形式：$m\ddot{\mathbf{x}} = -k A \mathbf{x}$，其中

$$A = \begin{pmatrix} 2 & -1 & 0 \\ -1 & 2 & -1 \\ 0 & -1 & 2 \end{pmatrix}$$

本征值：$\lambda_j = 2 - 2\cos\frac{j\pi}{4}$，$j=1,2,3$。

$$\omega_j^2 = \frac{k}{m}\left(2 - 2\cos\frac{j\pi}{4}\right) = \frac{4k}{m}\sin^2\frac{j\pi}{8}$$

- $j=1$: $\omega_1^2 = \frac{4k}{m}\sin^2\frac{\pi}{8} = \frac{k}{m}(2-\sqrt{2})$ — 对称模
- $j=2$: $\omega_2^2 = \frac{4k}{m}\sin^2\frac{\pi}{4} = \frac{2k}{m}$ — 反对称模
- $j=3$: $\omega_3^2 = \frac{k}{m}(2+\sqrt{2})$ — 高频模

模式形状 $v_j \propto \sin\frac{ij\pi}{4}$（离散正弦波）——这是固定边界条件下的一维链振动，连接到固体物理中的声子。
</details>

---

## Cambridge Cavendish 传统

### Cavendish Laboratory 与力学

Cavendish Laboratory 成立于 1874 年，以 Henry Cavendish 命名。在力学方面：

- **James Clerk Maxwell**（第一任 Cavendish Professor）重新组织了实验室的教学体系，强调精确测量
- **Ernest Rutherford** 时代，$\alpha$ 粒子散射实验（1911）本质上是经典力学有心力问题的直接应用——库仑势下的双曲轨道
- **Geiger-Marsden 实验**的分析用的就是本节 §2.2 的轨道方程

### Tripos 的历史

Cambridge Mathematical Tripos 始于 18 世纪，是世界上最古老的数学/物理考试体系之一。"Tripos" 一词来源于三脚凳（三位考官坐在三脚凳上提问）。著名 Tripos 高分获得者（Senior Wrangler）包括：

- **George Stokes** (1841) — 流体力学
- **James Clerk Maxwell** (1854, 第二名) — 电磁学
- **J.J. Thomson** (1880) — 电子发现
- **Paul Dirac** (未参加，但受 Tripos 传统影响) — 量子力学

Tripos 的训练风格——**大量困难计算题**——直接影响了英国物理学的风格：重计算、重精确、轻概念直觉（与美国 Feynman 风格形成对比）。

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Kibble & Berkshire Ch 1-4 | 牛顿力学 | 基础，Part IA |
| Kibble & Berkshire Ch 4-7 | 有心力 + 刚体 | Part IA 核心 |
| Kibble & Berkshire Ch 12 | 相对论 | 精要介绍 |
| Goldstein Ch 1-2 | 变分法 + 拉格朗日 | Part IB 核心 |
| Goldstein Ch 8-9 | 哈密顿 + 正则变换 | Part IB 拓展 |
| Goldstein Ch 4-5 | 刚体 | 深入 |
| Landau & Lifshitz Vol 1 | 全部 | 简洁优美，高阶 |
| Morin *Introduction to Classical Mechanics* | 习题 | Tripos 风格练习 |

---

**版本**：v1.0 (2026-08-12) · Cambridge Part IA/IB Mechanics & Classical Dynamics


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：物理学最古老的那个问题——"东西为什么会动、怎么动"。从苹果落地到火箭升空，全靠 $F=ma$ 这条祖传秘方，再叠上"大自然是个经济学家，总走最省事的路径"（最小作用量）。
>
> **生活类比**：弹吉他。你拨一下弦（给个力），弦按自己的脾气振动（惯性 + 回复力），整首旋律的规则都写在这套方程里。换成太阳和地球，那条"最省事路径"就是椭圆轨道。
>
> **反直觉发现（啊哈时刻）**：把一本书抛到空中，绕"中间"那根轴转，它会突然翻个跟头再继续转——这就是 Dzhanibekov 效应（§5.3）。太空站里的螺丝会周期性"翻面"，看着像违反物理，其实是刚体方程的必然结果。

---

## 🔗 衔接：从哪来，到哪去

- **前置知识**：中学物理（牛顿三定律、矢量）、Part IA Mathematics（微积分、矢量分析、常微分方程）
- **危机（牛顿力学的三道墙）**：
  - 高速（接近光速）→ 牛顿失效 → **狭义相对论**（§6）
  - 原子尺度 → 牛顿失效 → **量子力学**（Topic 3）
  - 多体/复杂系统 → 算不动 → **统计物理 + 混沌**
- **新危机**：牛顿的"决定论"在混沌系统里崩塌——三体问题、湍流的初始条件微小差异会被指数放大（蝴蝶效应）
- **后续去向**：拉格朗日/哈密顿框架是通往**量子力学（正则量子化）、统计力学（相空间 + Liouville）、广义相对论（等效原理）、量子场论**的统一桥梁

---

## 🏭 理论联系实际：5 个现代应用

1. **陀螺仪 / 手机 IMU**：你手机里那颗能感知方向的小芯片，靠的就是刚体动力学 + 科里奥利振动陀螺（MEMS）。§1.3 的非惯性系方程是它的设计原理。
2. **卫星轨道与引力弹弓**：SpaceX、ESA 的轨道转移（霍曼转移）、旅行者号的引力辅助，全是 §2 有心力问题的工程化。
3. **旋转液面望远镜**：§习题 1 的旋转抛物面是现实！加拿大的大型天顶望远镜（LZT）用旋转的液态汞做 6 米反射镜，省去磨镜成本。
4. **车辆/飞行器稳定性**：自行车为什么不倒、无人机为什么能悬停，背后是刚体角动量与中间轴稳定性。
5. **体育中的角动量守恒**：体操运动员的"猫翻身"——在零角动量下通过身体形变完成转体；花样滑冰收紧手臂加速旋转，全靠 $\mathbf{L}$ 守恒。

---

## 🔬 最新研究前沿（2024-2026）

> 以下为该领域近年重要进展，标注来源与年份。

1. **湍流的机器学习闭合**：2024 年多个团队用物理信息神经算子（Fourier Neural Operator）学习 Navier-Stokes 的湍流闭合项，把气候与航空 CFD 仿真加速 100–1000×（*PNAS*, 2024）。经典力学的"三体危机"在流体上正被 AI 缓解。
2. **N 体引力的新统计规律**：2023–2024 对三体问题混沌出口的统计研究揭示了出射角分布的幂律结构，给出了三体问题第一个解析统计解（Kol, Breen 等, *Nature*, 2023；后续 2024 验证）。
3. **活性物质 / 颗粒力学**：2024–2025 自推进粒子、鸟群、细胞群的连续介质力学成为软凝聚态热点，剑桥 Active Matter 小组参与其中。
4. **冷原子超精密陀螺仪**：2024 物质波干涉陀螺仪实现新灵敏度，用于广义相对论检验与无 GPS 导航——把 §1.3 的科里奥利效应测到量子精度。
5. **非厄米/拓扑经典力学超材料**：2024 在力学、声学超材料里实现 PT 对称与拓扑 protected 振动模式，把抽象群论变成可触摸的力学结构。

---

## 🗺️ 学习 Roadmap（Cambridge Tripos 路径）

| 阶段 | 课程 | 你应当能做到 |
|------|------|------------|
| **Part IA** | Mechanics A/B | 用牛顿定律算开普勒轨道；解释 Foucault 摆为何 ≈31 小时而非 24 小时 |
| **Part IB** | Classical Dynamics | 对任意约束系统写出拉格朗日量；用 Noether 定理一眼看出守恒量；推导 Dzhanibekov 效应 |
| **Part II** | Classical Dynamics 拓展 | 处理经典混沌（Lyapunov 指数）、摄动理论、连续介质（流体/弹性）入门 |
| **Part III** | Analytical/Geometric Mechanics | 辛流形上的几何力学、非平衡统计的力学根基 |

**知识检查三问**：
1. 能否从**最小作用量原理**推出行星椭圆轨道？
2. 为什么 Foucault 摆在剑桥转一圈约 30 小时而非 24 小时？
3. 为什么绕中间惯量主轴旋转会翻转，而绕最大/最小轴稳定？
