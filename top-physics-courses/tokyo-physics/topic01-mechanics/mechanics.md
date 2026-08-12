# 東京大学物理系 Phase 1 · 力学と解析力学 深度講義

> **课程映射**（SURVEY §9 東大）：普通物理 A/B/C（力学部分）+ 解析力学
> **教材**：Halliday/Resnick/Walker *Fundamentals of Physics*（普通物理）+ Goldstein/Poole/Safko *Classical Mechanics* 3ed + Landau & Lifshitz *Mechanics* Vol 1
> **定位**：从牛顿矢量力学升级到拉格朗日/哈密顿解析力学，并以刚体与狭义相对论收束。这是东大「物理の計算伝統」的根基——汤川秀树（1949 日本首个诺贝尔奖）到朝永振一郎（1965 QED 重整化）的理论血脉，都从这里出发。

---

## 0. 導引：東大力学怎麼教

東京大学理学部物理学科の力学教育有一条暗线：**先让学生在普通物理（Halliday/Resnick，日文译本《フィジックス》）里把矢量计算练到肌肉记忆，再在三年级的「解析力学」课里把同一组问题用拉格朗日重做一遍**。这种「同一题、两种语言」的训练法，源自俄国学派（Landau）经汤川、朝永引入日本后与本格派计算传统的融合。

Goldstein 第 2 章的一句话是东大这门课的精神纲领：

> *The entire subject of theoretical physics can be organized around the principle of least action.*

本章我们按 **牛顿 → 拉格朗日 → 哈密顿 → 刚体 → 相对论** 的递进展开，每一节配 Python 数值验证，最后给出東大风格的习题集。

---

## 1. ニュートン力学（Newtonian Mechanics）

### 1.1 三定律与运动方程

牛顿三定律（Newton's three laws）：

1. **惯性定律**：$\vec{F} = 0 \Rightarrow \dot{\vec{p}} = 0$，动量守恒。
2. **运动定律**：$\vec{F} = \dfrac{d\vec{p}}{dt}$，当 $v \ll c$ 时退化为 $\vec{F} = m\vec{a}$。
3. **作用反作用**：$\vec{F}_{12} = -\vec{F}_{21}$。

其中动量 $\vec{p} = m\vec{v}$。对单个质点，运动方程是二阶 ODE：

$$m\ddot{\vec{r}} = \vec{F}(\vec{r}, \dot{\vec{r}}, t)$$

给定初始条件 $(\vec{r}_0, \dot{\vec{r}}_0)$ 即可积分求轨迹。

### 1.2 守恒律（Conservation Laws）

| 守恒量 | 条件 | 数学形式 |
|--------|------|----------|
| 动量 $\vec{p}$ | $\vec{F}_{\text{ext}} = 0$ | $\sum \vec{p}_i = \text{const}$ |
| 角动量 $\vec{L} = \vec{r}\times\vec{p}$ | $\vec{\tau}_{\text{ext}} = 0$ | $\vec{r}\times\vec{F} = 0$ |
| 能量 $E = T + V$ | 力是保守力 $\vec{F} = -\nabla V$ | $\oint \vec{F}\cdot d\vec{r} = 0$ |

**保守力的判据**：$\nabla \times \vec{F} = 0$（旋度为零）$\Leftrightarrow$ $\vec{F} = -\nabla V$ 存在势能。

### 1.3 有心力运动（Central Force）

太阳系、氢原子（量子版）的经典前身。角动量守恒 $\Rightarrow$ 运动在固定平面内（取极坐标 $(r, \theta)$）：

$$L = mr^2\dot{\theta} = \text{const} \quad (\text{Kepler 第二定律的力学表述})$$

径向方程化为**有效势**（effective potential）问题：

$$\frac{1}{2}m\dot{r}^2 + \underbrace{\left[V(r) + \frac{L^2}{2mr^2}\right]}_{V_{\text{eff}}(r)} = E$$

其中 $L^2/(2mr^2)$ 称**离心势**（centrifugal barrier）。对平方反比引力 $V(r) = -k/r$，$V_{\text{eff}}$ 有极小值，对应稳定圆轨道。

**Kepler 三定律的推导**：从有效势出发可解出轨道方程

$$r(\theta) = \frac{p}{1 + e\cos\theta}, \quad p = \frac{L^2}{mk}, \quad e = \sqrt{1 + \frac{2EL^2}{mk^2}}$$

$e < 1$ 椭圆、$e = 1$ 抛物线、$e > 1$ 双曲线。

---

## 2. ラグランジュ力学（Lagrangian Mechanics）

### 2.1 最小作用量原理（Principle of Least Action）

拉格朗日量（Lagrangian）定义为动能减势能：

$$\mathcal{L}(q, \dot{q}, t) = T - V$$

其中 $q_i$ 是**广义坐标**（generalized coordinates），个数等于自由度。真实轨迹使**作用量**（action）

$$S = \int_{t_1}^{t_2} \mathcal{L}(q, \dot{q}, t)\, dt$$

取驻值（$\delta S = 0$）。这就是 **Hamilton 变分原理**。

### 2.2 Euler–Lagrange 方程

对 $S$ 变分（分部积分，端点固定 $\delta q(t_1) = \delta q(t_2) = 0$），得每个广义坐标满足：

$$\boxed{\frac{d}{dt}\frac{\partial \mathcal{L}}{\partial \dot{q}_i} - \frac{\partial \mathcal{L}}{\partial q_i} = 0}$$

**关键优势**：
- 约束力（如摆的绳张力、斜面法向力）自动消失——只需选对广义坐标。
- 标量计算（$T, V$ 是标量），避免矢量分解。
- 坐标无关（coordinate-free）：任何广义坐标都成立。

### 2.3 例：单摆与双摆

**单摆**（simple pendulum）：取角度 $\theta$ 为广义坐标。

$$T = \tfrac{1}{2}ml^2\dot{\theta}^2, \quad V = -mgl\cos\theta$$

$$\mathcal{L} = \tfrac{1}{2}ml^2\dot{\theta}^2 + mgl\cos\theta$$

代入 EL 方程：$ml^2\ddot{\theta} + mgl\sin\theta = 0 \Rightarrow \ddot{\theta} = -(g/l)\sin\theta$。

小角度 $\sin\theta \approx \theta \Rightarrow T = 2\pi\sqrt{l/g}$（等时性）。大角度时周期变长（见 §5 Python 验证）。

**双摆**（double pendulum）——混沌的教科书例子：两根无质量杆 $l_1, l_2$，两质量 $m_1, m_2$，角度 $\theta_1, \theta_2$。

$$\mathcal{L} = \tfrac{1}{2}(m_1+m_2)l_1^2\dot{\theta}_1^2 + \tfrac{1}{2}m_2 l_2^2\dot{\theta}_2^2 + m_2 l_1 l_2 \dot{\theta}_1\dot{\theta}_2\cos(\theta_1-\theta_2) + (m_1+m_2)gl_1\cos\theta_1 + m_2 gl_2\cos\theta_2$$

代入 EL 得两个耦合非线性 ODE（见 §5 代码）。初始条件的微小差异在数十秒内放大到 $O(1)$——**Lyapunov 指数为正**。

### 2.4 广义动量与守恒

**广义动量**（conjugate / canonical momentum）：

$$p_i = \frac{\partial \mathcal{L}}{\partial \dot{q}_i}$$

若 $\mathcal{L}$ 不显含某坐标 $q_i$（称**循环坐标** cyclic coordinate），则 $\dot{p}_i = 0 \Rightarrow p_i = \text{const}$。

> **Noether 定理的力学版**：每个连续对称性 $\Rightarrow$ 一个守恒量。时间平移不变 $\Rightarrow$ 能量守恒；空间平移不变 $\Rightarrow$ 动量守恒；旋转不变 $\Rightarrow$ 角动量守恒。

---

## 3. ハミルトン力学（Hamiltonian Mechanics）

### 3.1 Legendre 变换

定义**哈密顿量**（Hamiltonian）为 $\mathcal{L}$ 对速度的 Legendre 变换：

$$\mathcal{H}(q, p, t) = \sum_i p_i \dot{q}_i - \mathcal{L}$$

若势能不显含速度且约束是完整稳定的，则 $\mathcal{H} = T + V = E$（总能量）。

### 3.2 正则方程（Hamilton's Canonical Equations）

从 Legendre 变换的性质可得 $n$ 自由度系统的 $2n$ 个一阶 ODE：

$$\boxed{\dot{q}_i = \frac{\partial \mathcal{H}}{\partial p_i}, \qquad \dot{p}_i = -\frac{\partial \mathcal{H}}{\partial q_i}}$$

相比牛顿/拉格朗日的二阶方程，哈密顿形式是一阶但数目翻倍——这把**相空间**（phase space, $(q, p)$ 空间）推到了舞台中央。

### 3.3 相空间与 Liouville 定理

哈密顿流在相空间中保持体积不变——**Liouville 定理**：

$$\frac{d\rho}{dt} = \frac{\partial \rho}{\partial t} + \{\rho, \mathcal{H}\} = 0$$

其中 $\{f, g\} = \sum_i\left(\frac{\partial f}{\partial q_i}\frac{\partial g}{\partial p_i} - \frac{\partial f}{\partial p_i}\frac{\partial g}{\partial q_i}\right)$ 是 **Poisson 括号**（Poisson bracket）。这是统计力学的微观基础（相空间密度 = 概率，Liouville 保证等概率原理的动力学自洽）。

物理意义：一群代表点像不可压缩流体一样流动。这是为什么微正则系综里等能面上分布均匀——不是假设，是定理。

---

## 4. 剛体力学（Rigid Body Dynamics）

### 4.1 慣性テンソル（Moment of Inertia Tensor）

刚体内任意两点距离不变。对固定转轴，$I = \sum m_i r_{i,\perp}^2$；一般情形需**惯性张量**（3×3 对称矩阵）：

$$I_{ij} = \int \rho(\vec{r})\left(\delta_{ij}r^2 - r_i r_j\right) d^3r$$

对角化后得主惯性矩 $I_1, I_2, I_3$ 和主轴。角动量与角速度关系：$\vec{L} = \mathbf{I}\vec{\omega}$（一般不同向！）。

### 4.2 Euler 方程与自由刚体

在（随体旋转的）主轴坐标系中，**Euler 方程**：

$$I_1\dot{\omega}_1 - (I_2 - I_3)\omega_2\omega_3 = \tau_1$$
$$I_2\dot{\omega}_2 - (I_3 - I_1)\omega_3\omega_1 = \tau_2$$
$$I_3\dot{\omega}_3 - (I_1 - I_2)\omega_1\omega_2 = \tau_3$$

**自由刚体（$\tau = 0$）的稳定性判据**（网球拍定理 / intermediate axis theorem）：

- 绕 $I_{\min}$ 或 $I_{\max}$ 主轴转 → 稳定。
- 绕中间轴 $I_{\text{mid}}$ 转 → **不稳定**（小扰动指数放大）。

> **反直觉**：把网球拍绕中间轴抛起，它会不可预测地翻转——即便没有外力矩！这是刚体动力学的经典反直觉，见 §5 Python 模拟。

### 4.3 Euler 角与陀螺

描述刚体姿态需 3 个 **Euler 角** $(\phi, \theta, \psi)$（进动 precession / 章动 nutation / 自转 spin）。对称陀螺（$I_1 = I_2$）的重力进动频率：

$$\dot{\phi} = \frac{Mgl}{I_3 \omega_3} \quad (\text{快自转近似})$$

这是自行车不倒、陀螺仪定向的物理基础。

---

## 5. 特殊相対論（Special Relativity）

### 5.1 Lorentz 变换

Einstein（1905）的两条公设——相对性原理 + 光速不变——推出 Lorentz 变换（沿 $x$ 方向相对速度 $v$）：

$$x' = \gamma(x - vt), \quad t' = \gamma\left(t - \frac{vx}{c^2}\right), \quad \gamma = \frac{1}{\sqrt{1 - v^2/c^2}}$$

推论：**时间膨胀** $\Delta t' = \gamma \Delta t_0$（固有时最短）、**长度收缩** $L' = L_0/\gamma$。

### 5.2 四维时空与不变量

引入四维矢量 $x^\mu = (ct, \vec{r})$，间隔不变量：

$$ds^2 = c^2dt^2 - d\vec{r}^2 = \text{Lorentz 不变}$$

类时（$ds^2 > 0$）允许因果联系；类空（$ds^2 < 0$）不允许。

### 5.3 相对论能量-动量

四维动量 $p^\mu = (E/c, \vec{p})$，模方不变：

$$\boxed{E^2 = (pc)^2 + (mc^2)^2}$$

静能 $E_0 = mc^2$。动量 $\vec{p} = \gamma m \vec{v}$，总能量 $E = \gamma mc^2$，动能 $T = (\gamma - 1)mc^2$。

> **東大关联**：Koshiba 小柴昌俊（2002 诺奖，Super-Kamiokande 中微子探测）和 Kajita 梶田隆章（2015 诺奖，中微子振荡）的实验基础，正是相对论能量-动量关系在 MeV–GeV 能区的精确应用。Super-K 水切伦科夫探测器里，高能中微子产生的带电 $\mu/e$ 以 $v > c/n$（水中光速）发出切伦科夫辐射——没有 $E = \gamma mc^2$ 就没有这些测量。

---

## 6. Python 数值验证

所有代码纯 NumPy / 标准库，`bash` 可直接运行。

### 6.1 单摆大角度周期（验证 $T > 2\pi\sqrt{l/g}$）

```python
# pendulum_period.py —— 验证大角度摆周期增长
import numpy as np

g, L = 9.8, 1.0
dt, T_max = 1e-4, 20.0

def period(theta0_deg):
    theta = np.radians(theta0_deg)
    omega = 0.0
    t = 0.0
    crossed = []
    sign = np.sign(theta)
    n = int(T_max / dt)
    for _ in range(n):
        omega += -(g/L)*np.sin(theta)*dt
        theta += omega*dt
        t += dt
        if np.sign(theta) != sign and abs(theta) < 0.3:
            crossed.append(t)
            sign = np.sign(theta)
            if len(crossed) >= 3:
                break
    return crossed[-1] - crossed[-3]  # 一个完整周期（两次半周期）

T_small = 2*np.pi*np.sqrt(L/g)
for a in [5, 30, 60, 90, 120, 150, 179]:
    T = period(a)
    print(f"θ0={a:3d}°  T={T:.3f}s  T/T0={T/T_small:.3f}")
```

预期输出（$T_0 = 2.006$s）：大角度周期显著增大，$\theta_0 = 90°$ 时 $T/T_0 \approx 1.18$，$\theta_0 = 179°$ 时 $T/T_0 \approx 2.3$。解析近似 $T \approx T_0[1 + \frac{1}{16}\theta_0^2 + \frac{11}{3072}\theta_0^4 + \cdots]$。

### 6.2 双摆混沌（Lyapunov 指数为正）

```python
# double_pendulum_chaos.py —— 双摆混沌：初始微小差指数放大
import numpy as np

def deriv(s, m1=1, m2=1, l1=1, l2=1, g=9.8):
    th1, th2, w1, w2 = s
    d = th1 - th2
    den = 2*m1 + m2 - m2*np.cos(2*d)
    a1 = (-g*(2*m1+m2)*np.sin(th1) - m2*g*np.sin(th1-2*th2)
          - 2*np.sin(d)*m2*(w2**2*l2 + w1**2*l1*np.cos(d))) / (l1*den)
    a2 = (2*np.sin(d)*(w1**2*l1*(m1+m2) + g*(m1+m2)*np.cos(th1)
          + w2**2*l2*m2*np.cos(d))) / (l2*den)
    return np.array([w1, w2, a1, a2])

def rk4(s, dt):
    k1 = deriv(s); k2 = deriv(s+0.5*dt*k1)
    k3 = deriv(s+0.5*dt*k2); k4 = deriv(s+dt*k3)
    return s + dt*(k1+2*k2+2*k3+k4)/6

dt, T = 1e-3, 10.0
s  = np.array([np.pi/2, np.pi/2, 0, 0])           # 初始
s2 = s.copy(); s2[0] += 1e-6                       # 差 1e-6 rad
N = int(T/dt)
sep = []
for _ in range(N):
    s  = rk4(s,  dt)
    s2 = rk4(s2, dt)
    sep.append(np.linalg.norm(s - s2))
sep = np.array(sep)
# 估计 Lyapunov 指数：log(sep) ~ λ t
t = np.arange(N)*dt
mask = (sep > 1e-9) & (sep < 0.5)                  # 线性区
lam = np.polyfit(t[mask], np.log(sep[mask]), 1)[0]
print(f"双摆最大 Lyapunov 指数 λ ≈ {lam:.3f} /s  (>0 → 混沌)")
```

### 6.3 中间轴不稳定（网球拍定理验证）

```python
# tennis_racket.py —— Euler 方程：中间轴旋转不稳定
import numpy as np

def euler_deriv(w, I1, I2, I3):
    return np.array([
        (I2-I3)/I1 * w[1]*w[2],
        (I3-I1)/I2 * w[2]*w[0],
        (I1-I2)/I3 * w[0]*w[1]])

def rk4(w, dt, I1, I2, I3):
    k1=euler_deriv(w,I1,I2,I3); k2=euler_deriv(w+0.5*dt*k1,I1,I2,I3)
    k3=euler_deriv(w+0.5*dt*k2,I1,I2,I3); k4=euler_deriv(w+dt*k3,I1,I2,I3)
    return w + dt*(k1+2*k2+2*k3+k4)/6

# 模拟一本书：I1 < I2 < I3
I1, I2, I3 = 1.0, 2.0, 3.0
eps = 0.01
for label, w0 in [("最小轴(稳定)", [1,eps,0]),
                  ("中间轴(不稳定)", [0,1,eps]),
                  ("最大轴(稳定)", [eps,0,1])]:
    w = np.array(w0, dtype=float)
    dt, T = 0.001, 30.0
    for _ in range(int(T/dt)):
        w = rk4(w, dt, I1, I2, I3)
    print(f"{label:18s}: 初始 ω={[round(x,3) for x in w0]} → "
          f"末态 |ω|分量={[round(x,3) for x in w]}")
```

预期：中间轴情形，能量从 $\omega_2$ 大量转移到 $\omega_1, \omega_3$（翻转）；稳定轴基本保持。

### 6.4 相对论能量-动量关系

```python
# relativistic_energy.py —— 验证 E²=(pc)²+(mc²)²
import numpy as np
c = 3e8
m = 9.109e-31   # 电子质量
mc2 = m*c**2    # ≈ 8.187e-14 J = 0.511 MeV
for v_frac in [0.1, 0.5, 0.9, 0.99, 0.999, 0.9999]:
    v = v_frac*c
    gamma = 1/np.sqrt(1 - v**2/c**2)
    E = gamma*mc2
    p = gamma*m*v
    E_check = np.sqrt((p*c)**2 + mc2**2)
    T_kin = (gamma-1)*mc2
    print(f"v/c={v_frac:.4f}  γ={gamma:9.3f}  "
          f"E={E/mc2:.3f}mc²  T={T_kin/mc2:.3f}mc²  "
          f"√(p²c²+m²c⁴)={E_check/mc2:.4f}mc²")
```

---

## 7. 東大特色：計算伝統

東京大学理論物理の系譜有明确的「先算对、再想透」传统：

- **朝永振一郎**（Tomonaga, 1965 诺贝尔奖）：QED 重整化的关键是把无穷大一步步算到有限——超-renormalization 的计算密度。
- **湯川秀樹**（Yukawa, 1949）：介子理论来自对核力力程的量纲估算（$r \sim \hbar/(m_\pi c) \approx 1.4$ fm），是 Goldstein 第 2 章最小作用量原理在量子尺度的回响。
- **南部陽一郎**（Nambu, 2008）：自发对称性破缺——从拉格朗日量的对称性到真空的不对称，正是解析力学 Noether 定理在量子场论的延伸。

这种「把每一个积分、每一个守恒量算到精确」的学风，是 Goldstein + Landau 在东大被奉为圭臬的原因。Landau 卷 1 全书的开篇就是最小作用量，东大解析力学课也是如此安排——**从变分原理出发，把牛顿定律作为推论**，而非公理。

---

## 8. 習題集（Exercises）

> 标 ★ 为東大风格（重计算），★★ 为 Goldstein 习题难度。

**习题 1（★）**　一质点在势能 $V(x) = kx^4/4$（$k > 0$）中一维运动。求周期作为能量 $E$ 的函数。
> *提示*：$T(E) = 4\int_0^{x_m}\frac{dx}{\sqrt{2(E - kx^4/4)/m}}$，令 $u = x/x_m$ 化为 Beta 函数。答案 $T = \frac{1}{\pi}B(1/4, 1/2)\sqrt{m/k}\,E^{-1/4}$。

**习题 2（★★）**　写出球面摆（spherical pendulum，长度 $l$）的拉格朗日量，找循环坐标与守恒量，并证明有效势有稳定圆轨道。
> *答案要点*：$\phi$ 循环，$p_\phi = ml^2\sin^2\theta\,\dot\phi$ 守恒。$V_{\text{eff}} = -mgl\cos\theta + p_\phi^2/(2ml^2\sin^2\theta)$，极小值处对应稳定圆锥摆。

**习题 3（★）**　一均匀实心球（质量 $M$，半径 $R$）沿斜面（倾角 $\alpha$）纯滚动。用拉格朗日求加速度，并与无摩擦滑动比较。
> *答案*：纯滚动 $a = \frac{5}{7}g\sin\alpha$（球 $I = 2MR^2/5$），无摩擦 $a = g\sin\alpha$。

**习题 4（★★）**　证明：自由对称陀螺（$I_1 = I_2 \neq I_3$）绕任意轴初始旋转后，角速度矢量在体坐标系中绕主轴 3 以频率 $\Omega = (I_3 - I_1)\omega_3/I_1$ 进动。
> *这是自由刚体的「无力矩进动」，Euler 方程的直接推论。*

**习题 5（★）**　μ子在海拔 10 km 产生（平均寿命 $\tau_0 = 2.2\,\mu$s），以 $v = 0.999c$ 向地面飞行。用时间膨胀计算它能否到达地面（不考虑能量损失）。
> *答案*：实验室寿命 $\gamma\tau_0 \approx 49\,\mu$s，可飞行 $\approx 14.7$ km > 10 km，故能到达。这是相对论「延长寿命」的经典证据。

**习题 6（★★）**　用哈密顿正则方程推导一维谐振子（$\mathcal{H} = p^2/(2m) + \tfrac{1}{2}kx^2$）的相轨迹是椭圆，并验证 $\oint p\,dq$ 与振幅无关地等于 $E/f$（$f$ 为频率）。
> *这是 Sommerfeld 作用量积分，Bohr 对应原理的桥梁。*

---

## 9. 参考文献

1. Halliday, Resnick, Walker. *Fundamentals of Physics* 11ed. Wiley, 2018.（東大普通物理 A/B/C 指定，日文版《フィジックス》培風館）
2. Goldstein, Poole, Safko. *Classical Mechanics* 3ed. Addison-Wesley, 2002.（東大解析力学指定）
3. Landau, Lifshitz. *Mechanics* (Course of Theoretical Physics Vol 1) 3ed. Butterworth-Heinemann, 1976.（最小作用量开篇，俄系经典）
4. Taylor, John R. *Classical Mechanics*. University Science Books, 2005.（中级力学桥梁教材）
5. Hand, Finch. *Analytical Mechanics*. Cambridge, 1998.（变分法与刚体讲得细致）
6. 清水 明. 『解析力学』（東京大学出版会）——東大本土教材，变分法 + 正则变换 + 刚体的紧凑讲解。

---

**完成日期**：2026-08-12　|　**对应 SURVEY §9 東大**：普通物理 A/B/C + 解析力学
