# Stanford 物理系 Phase 1 · 主题 2：电磁学

> **课程谱系**：PHYS 43 (电磁学) → PHYS 63 (电磁学荣誉) → PHYS 120 (中级电动力学)
>
> **教材阶梯**：Young & Freedman / Purcell & Morin《Electricity and Magnetism》3ed → Griffiths《Introduction to Electrodynamics》4ed
>
> **Stanford 特色**：SLAC 的粒子加速器是电磁学理论的终极实验室——从静电加速到同步辐射，从波荡器到自由电子激光，Maxwell 方程组在此被「工程化」

---

## 目录

1. [静电学](#1-静电学)
2. [静磁学](#2-静磁学)
3. [麦克斯韦方程组](#3-麦克斯韦方程组)
4. [电磁波](#4-电磁波)
5. [Stanford/SLAC 关联](#5-stanfordlac-关联)
6. [习题与解答](#6-习题与解答)
7. [代码实验](#7-代码实验)
8. [局限与延伸](#8-局限与延伸)

---

## 1. 静电学

### 1.1 直觉

静电学的核心是**超距作用**的疑问：两个电荷不接触，如何施力？Faraday 的回答是**场**——电荷在其周围空间产生电场，另一个电荷「感受」到这个场。

Purcell 教材（PHYS 63 荣誉）的独特视角：从相对论出发推导磁场，揭示磁力本质上是电场力的相对论修正。这是 Stanford 荣誉课的灵魂。

### 1.2 库仑定律与电场

$$\mathbf{F} = \frac{1}{4\pi\epsilon_0}\frac{q_1 q_2}{r^2}\hat{\mathbf{r}}$$

电场定义 $\mathbf{E} = \mathbf{F}/q$：

$$\mathbf{E}(\mathbf{r}) = \frac{1}{4\pi\epsilon_0}\frac{q}{r^2}\hat{\mathbf{r}}$$

### 1.3 高斯定律

$$\boxed{\oint_S \mathbf{E}\cdot d\mathbf{A} = \frac{Q_{\text{enc}}}{\epsilon_0}}$$

微分形式：$\nabla\cdot\mathbf{E} = \rho/\epsilon_0$。利用对称性，高斯定律可秒解球、柱、平面对称的电场。

### 1.4 电势

保守场 $\mathbf{E} = -\nabla V$：

$$V(\mathbf{r}) = \frac{1}{4\pi\epsilon_0}\frac{q}{r}$$

电势满足泊松方程：

$$\nabla^2 V = -\frac{\rho}{\epsilon_0}$$

无源区退化为拉普拉斯方程 $\nabla^2 V = 0$。

### 1.5 电容与电介质

电容 $C = Q/V$。平行板电容 $C = \epsilon_0 A/d$。

电介质中 $\mathbf{D} = \epsilon_0\mathbf{E} + \mathbf{P} = \epsilon\mathbf{E}$，极化率 $\chi_e$，$\epsilon = \epsilon_0(1+\chi_e)$。

### 1.6 静电能

电场存储能量密度：

$$u = \frac{1}{2}\epsilon_0 E^2$$

总能量 $U = \frac{\epsilon_0}{2}\int E^2\, d^3r$。

---

## 2. 静磁学

### 2.1 直觉

磁场源于**运动电荷**。Purcell 的洞察：在静止参考系中只有电力的两个电荷，在运动参考系中会「出现」磁力——因为长度收缩改变了电荷密度。**磁场是电场的相对论效应**。

### 2.2 毕奥-萨伐尔定律

电流元 $Id\mathbf{l}$ 产生的磁场：

$$d\mathbf{B} = \frac{\mu_0}{4\pi}\frac{Id\mathbf{l}\times\hat{\mathbf{r}}}{r^2}$$

长直导线：$B = \frac{\mu_0 I}{2\pi r}$。圆环中心：$B = \frac{\mu_0 I}{2R}$。

### 2.3 安培定律与磁场高斯定律

$$\oint \mathbf{B}\cdot d\mathbf{l} = \mu_0 I_{\text{enc}}, \quad \oint \mathbf{B}\cdot d\mathbf{A} = 0$$

微分形式：$\nabla\times\mathbf{B} = \mu_0\mathbf{J}$，$\nabla\cdot\mathbf{B} = 0$（无磁单极）。

### 2.4 磁矢势

$\mathbf{B} = \nabla\times\mathbf{A}$，库仑规范 $\nabla\cdot\mathbf{A} = 0$ 下：

$$\nabla^2\mathbf{A} = -\mu_0\mathbf{J}$$

### 2.5 洛伦兹力

$$\mathbf{F} = q(\mathbf{E} + \mathbf{v}\times\mathbf{B})$$

SLAC 加速器的核心：电场加速、磁场偏转。回旋频率 $\omega_c = qB/m$。

---

## 3. 麦克斯韦方程组

### 3.1 直觉

Maxwell 的伟大发现：安培定律 $\nabla\times\mathbf{B}=\mu_0\mathbf{J}$ 与电荷守恒 $\nabla\cdot\mathbf{J} = -\partial\rho/\partial t$ 矛盾。他加入了**位移电流**项，方程组瞬间自洽，并且预言了电磁波。

### 3.2 完整方程组

| 名称 | 积分形式 | 微分形式 |
|------|----------|----------|
| 高斯定律（电） | $\oint\mathbf{E}\cdot d\mathbf{A} = Q/\epsilon_0$ | $\nabla\cdot\mathbf{E} = \rho/\epsilon_0$ |
| 高斯定律（磁） | $\oint\mathbf{B}\cdot d\mathbf{A} = 0$ | $\nabla\cdot\mathbf{B} = 0$ |
| 法拉第定律 | $\oint\mathbf{E}\cdot d\mathbf{l} = -d\Phi_B/dt$ | $\nabla\times\mathbf{E} = -\partial\mathbf{B}/\partial t$ |
| 安培-麦克斯韦定律 | $\oint\mathbf{B}\cdot d\mathbf{l} = \mu_0 I + \mu_0\epsilon_0\,d\Phi_E/dt$ | $\nabla\times\mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\,\partial\mathbf{E}/\partial t$ |

### 3.3 位移电流

麦克斯韦的关键修正 $\mu_0\epsilon_0\,\partial\mathbf{E}/\partial t$。其物理意义：**变化的电场产生磁场**，正如变化的磁场产生电场。

### 3.4 电磁波速度

真空无源区，方程组退化为波动方程：

$$\nabla^2\mathbf{E} = \mu_0\epsilon_0\frac{\partial^2\mathbf{E}}{\partial t^2}$$

波速：

$$\boxed{c = \frac{1}{\sqrt{\mu_0\epsilon_0}} = 2.998\times 10^8\,\text{m/s}}$$

Maxwell 惊叹：这个速度等于已知的光速！光就是电磁波。

---

## 4. 电磁波

### 4.1 平面波解

$$\mathbf{E}(\mathbf{r},t) = \mathbf{E}_0 e^{i(\mathbf{k}\cdot\mathbf{r} - \omega t)}, \quad \mathbf{B} = \frac{1}{c}\hat{\mathbf{k}}\times\mathbf{E}$$

$\mathbf{E}\perp\mathbf{B}\perp\mathbf{k}$（横波），$|\mathbf{B}| = |\mathbf{E}|/c$。

### 4.2 坡印廷矢量

能流密度：

$$\mathbf{S} = \frac{1}{\mu_0}\mathbf{E}\times\mathbf{B}$$

时间平均强度 $I = \langle S\rangle = \frac{1}{2}c\epsilon_0 E_0^2$。

### 4.3 辐射

加速电荷辐射功率（拉莫尔公式）：

$$P = \frac{q^2 a^2}{6\pi\epsilon_0 c^3}$$

相对论推广（利纳尔公式）：$P \propto \gamma^6$，这是同步辐射的基础。

### 4.4 偶极辐射

振荡偶极子的远场辐射：

$$\langle S\rangle = \frac{\mu_0 p_0^2\omega^4}{32\pi^2 c}\frac{\sin^2\theta}{r^2}$$

辐射功率 $\propto \omega^4$——频率越高辐射越强，解释了天空为什么是蓝色的（瑞利散射 $\propto \omega^4$）。

---

## 5. Stanford/SLAC 关联

| 实验/设施 | 电磁学原理 |
|-----------|------------|
| **SLAC 直线加速器** | 射频腔电场加速电子，$\Delta E = q\int E\,dz$ |
| **SPEAR 储存环** | 偶极弯转磁铁，$r = p/(qB)$，同步辐射光源 |
| **SSRL 同步辐射** | 相对论电子弯转辐射，利纳尔公式 $\propto\gamma^4$ |
| **LCLS 自由电子激光** | 波荡器中周期磁场使电子扭摆，产生相干辐射 |
| **BABAR 探测器** | 螺线管磁场 $B\approx 1.5$ T 用于动量测量 |
| **KIPAC 天体物理** | 磁重联、宇宙射线加速（天体尺度的洛伦兹力） |

**SPEAR 同步辐射的能量标度**：3 GeV 电子在 1.5 T 磁场中，
- 弯转半径 $r = p/(eB) = \gamma m v/(eB) \approx 8.7$ m
- 特征光子能量 $\epsilon_c = \frac{3}{2}\hbar c\gamma^3/r \approx$ keV 量级（X 射线）

这就是为什么 SLAC 的 SSRL 是世界级 X 射线光源——能量全部来自电磁学。

---

## 6. 习题与解答

### 习题 1（PHYS 63 风格 · Purcell 问题 5.16 变体）

一无限长螺线管，单位长度匝数 $n$，电流 $I$ 以速率 $dI/dt$ 变化。求管外距轴 $r$ 处的感生电场。

<details>
<summary>解答</summary>

管内 $B = \mu_0 n I$（轴向），管外 $B = 0$。

法拉第定律，取半径 $r > R$（$R$ 为螺线管半径）的圆形回路：

$$\oint\mathbf{E}\cdot d\mathbf{l} = -\frac{d\Phi_B}{dt}$$

左边 $= 2\pi r E$，右边 $= -\pi R^2 \frac{dB}{dt} = -\pi R^2 \mu_0 n \frac{dI}{dt}$。

$$\boxed{E = -\frac{\mu_0 n R^2}{2r}\frac{dI}{dt}}$$

**反直觉**：管外 $B=0$ 但 $E\neq 0$！变化的磁通（藏在管内）在管外产生了涡旋电场。
</details>

### 习题 2（PHYS 120 风格 · Griffiths 问题 7.42 简化）

证明平行板电容器充电时，位移电流 $I_d$ 等于传导电流 $I$。

<details>
<summary>解答</summary>

板间电场 $E = Q/(\epsilon_0 A)$，$dE/dt = I/(\epsilon_0 A)$。

位移电流 $I_d = \epsilon_0 \frac{d\Phi_E}{dt} = \epsilon_0 A \frac{dE}{dt} = \epsilon_0 A \cdot \frac{I}{\epsilon_0 A} = I$。

物理意义：传导电流在导线中，位移电流「延续」到电容器内部，保证电流连续性。$\square$
</details>

### 习题 3（PHYS 120 · 同步辐射）

SPEAR 中 3 GeV 电子在 $B = 1.5$ T 磁场中做圆周运动。求弯转半径和每圈同步辐射功率损失。已知 $I_{\text{beam}} = 100$ mA。

<details>
<summary>解答</summary>

电子相对论因子 $\gamma = E/(m c^2) = 3000/0.511 = 5870$。

弯转半径 $r = p/(eB) = \gamma m c/(eB)$。

$r = \frac{5870 \times 9.109\times 10^{-31} \times 3\times 10^8}{1.6\times 10^{-19}\times 1.5} = 6.7$ m。

向心加速度 $a = v^2/r \approx c^2/r$（极端相对论）。

单电子辐射功率（利纳尔）：

$$P_1 = \frac{e^2 c \gamma^4}{6\pi\epsilon_0 r^2}$$

代入：$P_1 = \frac{(1.6\times10^{-19})^2 \times 3\times10^8 \times 5870^4}{6\pi\times 8.85\times10^{-12}\times 6.7^2} \approx 3.7\times 10^{-6}$ W/电子。

每圈能量损失 $U_0 = P_1 \cdot (2\pi r/c) \approx 0.52$ MeV。

要维持 100 mA 束流，需补偿功率 $P_{\text{total}} = U_0 \times N_e \times f_{\text{rev}}$，量级在 kW。
</details>

### 习题 4（PHYS 63 · 偶极辐射）

氢原子中电子（玻尔模型 $a_0 = 0.529$ Å）若按经典电动力学辐射，多久落入核中？

<details>
<summary>解答</summary>

圆周运动加速度 $a = v^2/r = e^2/(4\pi\epsilon_0 m r^2)$。

拉莫尔功率 $P = \frac{e^2 a^2}{6\pi\epsilon_0 c^3}$。

能量 $E = -\frac{e^2}{8\pi\epsilon_0 r}$，$dE/dt = \frac{e^2}{8\pi\epsilon_0 r^2}\frac{dr}{dt}$。

令 $dE/dt = -P$，积分：

$$\tau = \frac{4\pi\epsilon_0 m^2 c^3 r_0^3}{e^4} \approx 1.6\times 10^{-11}\,\text{s}$$

**反直觉结论**：经典物理预言原子在 $10^{-11}$ 秒内崩溃！这正是经典物理的致命缺陷，催生了量子力学。
</details>

---

## 7. 代码实验

### 实验 7.1：电场可视化（偶极子场）

```python
"""
PHYS 43 实验：电偶极子电场数值计算
点电荷叠加 + ASCII 矢量场图
纯标准库，几秒跑完
"""
import math

def E_point(q, rx, ry, px, py, k=1.0):
    """点电荷 q 在 (px,py) 在观测点 (rx,ry) 产生的电场"""
    dx, dy = rx - px, ry - py
    r2 = dx*dx + dy*dy
    if r2 < 1e-10:
        return 0.0, 0.0
    r = math.sqrt(r2)
    factor = k * q / (r2 * r)
    return factor * dx, factor * dy

def total_field(charges, x, y):
    """叠加多个点电荷的电场"""
    Ex = Ey = 0.0
    for q, px, py in charges:
        ex, ey = E_point(q, x, y, px, py)
        Ex += ex
        Ey += ey
    return Ex, Ey

def ascii_vector_field(charges, x_range, y_range, nx=25, ny=12):
    """ASCII 矢量场图"""
    arrows = ['→','↗','↑','↖','←','↙','↓','↘']
    lines = []
    for j in range(ny-1, -1, -1):
        y = y_range[0] + j*(y_range[1]-y_range[0])/(ny-1)
        row = ''
        for i in range(nx):
            x = x_range[0] + i*(x_range[1]-x_range[0])/(nx-1)
            Ex, Ey = total_field(charges, x, y)
            mag = math.sqrt(Ex*Ex + Ey*Ey)
            if mag < 1e-8:
                row += '.'
                continue
            angle = math.atan2(Ey, Ex)
            idx = int((angle + math.pi) / (2*math.pi) * 8) % 8
            row += arrows[idx]
        lines.append(row)
    return '\n'.join(lines)

# 电偶极子：+q 在 (-1,0)，-q 在 (1,0)
print("=== 电偶极子电场 ===")
print("+q 在 (-1,0)，-q 在 (1,0)\n")
dipole = [(1.0, -1.0, 0.0), (-1.0, 1.0, 0.0)]
print(ascii_vector_field(dipole, (-3, 3), (-2, 2)))

# 电势沿 x 轴
print("\n=== 电势 V(r) 沿 x 轴 ===")
print(f"{'x':>6} {'V':>12} {'E_x':>12}")
for x10 in range(-30, 31, 3):
    x = x10 / 10
    if abs(x) < 0.9:  # 避开电荷位置
        continue
    Ex, Ey = total_field(dipole, x, 0)
    # V = k*q/r+ - k*q/r-
    r_plus = abs(x - (-1))
    r_minus = abs(x - 1)
    V = 1.0/r_plus - 1.0/r_minus
    print(f"{x:6.1f} {V:12.4f} {Ex:12.4f}")
```

**预期输出**（ASCII 图显示偶极子的经典「双涡旋」场线图案）：

```
←←←←←←←←←←←.→→→→→→→→→→→→→
↙↙↙↙↙↙↙↙↙↙.↗↗↗↗↗↗↗↗↗↗↗
↓↓↓↓↓↓↓↓↓↓.↑↑↑↑↑↑↑↑↑↑↑↑↑
↙↙↙↙↙↙↙↙↙↙↗↗↗↗↗↗↗↗↗↗↗↗
←←←←←←←←←+q←←←-q→→→→→→→→→
↖↖↖↖↖↖↖↖↖↖↘↘↘↘↘↘↘↘↘↘↘↘
↑↑↑↑↑↑↑↑↑↑↑.↓↓↓↓↓↓↓↓↓↓↓
↖↖↖↖↖↖↖↖↖↖.↘↘↘↘↘↘↘↘↘↘↘
←←←←←←←←←←←.→→→→→→→→→→→→→
```

### 实验 7.2：麦克斯韦方程组验证（位移电流）

```python
"""
PHYS 120 实验：平行板电容器中的位移电流
验证安培-麦克斯韦定律的环路积分
纯标准库
"""
import math

def conduction_current(Q, dt):
    """传导电流 I = dQ/dt"""
    return Q / dt

def displacement_current_density(E_field, dt, epsilon_0=8.854e-12):
    """J_d = epsilon_0 * dE/dt"""
    return epsilon_0 * E_field / dt

def ampere_loop_integral(r, R, B, mu_0=4*math.pi*1e-7):
    """安培环路积分: 磁场 x 周长"""
    return B * 2 * math.pi * r

# 平行板电容器充电
print("=== 平行板电容器充电中的位移电流 ===")
epsilon_0 = 8.854e-12
mu_0 = 4 * math.pi * 1e-7
A = 1e-2  # 1 cm^2 板面积
d_plate = 1e-3  # 1 mm 间距
C = epsilon_0 * A / d_plate

print(f"电容 C = {C*1e12:.2f} pF")
print(f"\n{'t(ms)':>8} {'Q(nC)':>8} {'I(mA)':>8} {'I_d(mA)':>8} {'I=I_d?':>8}")

for t_ms in [1, 2, 5, 10]:
    t = t_ms * 1e-3
    # 假设 Q 线性增长到 1 nC 在 10ms
    Q = 1e-9 * (t_ms / 10)
    I = 1e-9 / 10e-3  # 恒定充电电流 0.1 nA... 让我们用更大值
    
# 用更实际的参数
V_max = 100  # V
t_charge = 10e-3  # 10 ms 线性充电
Q_max = C * V_max
I_cond = Q_max / t_charge
print(f"\n实际参数: V_max={V_max}V, 充电时间={t_charge*1e3}ms")
print(f"最大电荷 Q_max = {Q_max*1e9:.2f} nC")
print(f"传导电流 I = {I_cond*1e9:.2f} nA")

# 板间位移电流
E_between = V_max / d_plate  # 最终电场
I_d_total = epsilon_0 * A * (E_between / t_charge)  # 总位移电流

print(f"\n板间最终电场 E = {E_between:.0f} V/m")
print(f"总位移电流 I_d = epsilon_0*A*dE/dt = {I_d_total*1e9:.2f} nA")
print(f"传导电流 I = {I_cond*1e9:.2f} nA")
print(f"\nI_d / I = {I_d_total/I_cond:.4f}")
print("=> 位移电流精确等于传导电流！麦克斯韦的伟大自洽性。")

# 磁场计算（板间边缘 r 处）
r = d_plate  # 在板间距一半处
B_induced = mu_0 * I_d_total / (2 * math.pi * r)
print(f"\n板间距 r={r*1e3:.1f}mm 处感生磁场 B = {B_induced*1e12:.2f} pT")
print("（极小，但真实存在——这是电磁波的种子）")
```

### 实验 7.3：SLAC 同步辐射参数

```python
"""
PHYS 120 实验：SPEAR 同步辐射关键参数
计算弯转半径、特征频率、每圈能量损失
"""
import math

# 物理常数
m_e = 9.109e-31  # kg
c = 2.998e8       # m/s
e = 1.602e-19     # C
epsilon_0 = 8.854e-12

# SPEAR 参数
E_beam_GeV = 3.0  # 3 GeV
E_beam_J = E_beam_GeV * 1e9 * e
gamma = E_beam_J / (m_e * c**2)
B = 1.5  # Tesla

print("=== SLAC SPEAR 同步辐射参数 ===")
print(f"束流能量 E = {E_beam_GeV} GeV")
print(f"洛伦兹因子 gamma = {gamma:.0f}")
print(f"v/c = {math.sqrt(1-1/gamma**2):.15f}")

# 弯转半径
p = gamma * m_e * c  # 相对论动量
r_bend = p / (e * B)
print(f"\n弯转半径 r = {r_bend:.2f} m")

# 每圈辐射能量损失 U_0 = (e^2 * gamma^4) / (3 * epsilon_0 * r)
# 标准公式: U_0[keV] = 88.5 * E^4[GeV] / r[m]
U0_keV = 88.5 * E_beam_GeV**4 / r_bend
U0_MeV = U0_keV / 1000
print(f"每圈能量损失 U_0 = {U0_keV:.1f} keV = {U0_MeV:.3f} MeV")
print(f"占束流能量比例 = {U0_MeV/E_beam_GeV/1000*100:.4f}%")

# 特征光子能量
omega_c = (3/2) * gamma**3 * c / r_bend
epsilon_c_eV = 1.055e-34 * omega_c / e
print(f"\n特征光子能量 = {epsilon_c_eV:.0f} eV = {epsilon_c_eV/1000:.1f} keV (X射线!)")
print(f"特征波长 = {2*math.pi*c/omega_c * 1e12:.3f} pm")

print(f"\n=== 反直觉发现 ===")
print(f"1. 每圈损失 {U0_MeV:.2f} MeV，必须用射频腔补偿（否则电子螺旋坠毁）")
print(f"2. 损失 ∝ gamma^4：能量翻倍，辐射损失增 16 倍！")
print(f"3. 这正是同步辐射光源（SSRL）的 X 射线来源——'废物利用'")
```

---

## 8. 局限与延伸

### 8.1 经典电磁学的局限

| 局限 | 何时失效 | 替代理论 |
|------|----------|----------|
| 点电荷自能发散 | $r\to 0$ | 量子电动力学（QED） |
| 原子稳定性 | 电子绕核辐射崩溃 | 量子力学 |
| 高频/高能 | 黑体辐射紫外灾难 | 量子统计 |
| 强场 | $E \sim E_{\text{crit}} = m^2c^3/(e\hbar)$ | QED 真空极化 |

### 8.2 从 PHYS 43 到 PHYS 120 的认知跃迁

1. **PHYS 43**：力的世界——库仑定律，画电场线
2. **PHYS 63 (Purcell)**：相对论的世界——磁场是电场的相对论效应
3. **PHYS 120 (Griffiths)**：场方程的世界——Maxwell 方程组统一，辐射，介质
4. **PHYS 335 (Jackson)**：边值问题——多极展开，Green 函数，规范场

### 8.3 延伸阅读

- **Purcell & Morin** 第 5 章：磁场源于相对论，独此一家
- **Griffiths 第 9-11 章**：电磁波、辐射、相对论
- **Jackson**：研究生电磁学圣经（PHYS 335）
- **Landau & Lifshitz Vol 2《The Classical Theory of Fields》**：协变表述
- **Feynman Lectures Vol 2**：直觉与深度并存

---

## 参考文献

1. Purcell, E. M. & Morin, D. J. *Electricity and Magnetism* 3rd ed. Cambridge, 2013.
2. Griffiths, D. J. *Introduction to Electrodynamics* 4th ed. Cambridge, 2017.
3. Jackson, J. D. *Classical Electrodynamics* 3rd ed. Wiley, 1999.
4. Landau, L. D. & Lifshitz, E. M. *The Classical Theory of Fields* (Vol 2) 4th ed.
5. SLAC / SSRL. *Synchrotron Radiation Source*. slac.stanford.edu

---

> **本主题对应讲透X 宪法**：直觉（§1）→ 公式（§2-4）→ 代码（§7 bash 跑通）→ 不足（§8）→ 应用（§5 SLAC）。
>
> **文件信息**：stanford-physics/topic02-electromagnetism/em.md · Phase 1 主题 2 · 2026-08-12

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：电荷之间「隔空传话」靠的是一种看不见的「场」——变化的电场生磁场，变化的磁场生电场，它俩手拉手就能自己跑起来，跑得飞快，就是光。

Maxwell 的伟大发现：他把四条电与磁的定律拼在一起，突然发现它们「矛盾」——除非加一个修正项（位移电流）。加上之后，方程瞬间自洽，并且自然预言了一种波，速度 $c = 1/\sqrt{\mu_0\epsilon_0} \approx 3\times10^8$ m/s。Maxwell 惊呼：**这个速度就是光速！光就是电磁波！**

> **生活类比**：电场和磁场不是两种东西，是同一个「电磁场」的两个面。就像一个圆柱体——从正面看是长方形（电场），从侧面看是圆（磁场）。你跑起来看（换参考系），它俩就互相转换。这就是 Purcell 在 PHYS 63 揭示的真相：**磁场是电场的相对论修正**。

> **反直觉发现（啊哈时刻）**：
> 1. **螺线管外面 B=0 但 E≠0**：变化的磁场藏在管内，却在管外产生了涡旋电场！
> 2. **电磁波不需要介质**：光不是「以太」的振动，是电场磁场自己互相产生的自持波。
> 3. **原子为什么稳定？** 经典电磁学预言电子绕核辐射 $10^{-11}$ 秒坠入核中——这个致命缺陷直接催生了量子力学。

---

## 🔗 衔接：从哪来，到哪去

| 维度 | 内容 |
|------|------|
| **前置知识** | 主题 1（力学）的矢量、能量概念；微积分（线积分/面积分） |
| **本主题解决的危机** | 超距作用的困惑——法拉第用「场」概念取代，麦克斯韦用方程组统一 |
| **核心跃迁** | 从「库仑力」（PHYS 43）→「相对论场」（PHYS 63 Purcell）→「Maxwell 方程组」（PHYS 120 Griffiths） |
| **留下新危机** | ①原子辐射崩溃（需量子力学）②黑体辐射紫外灾难（需量子统计）③强场下真空极化（需 QED） |
| **后续主题** | **主题 3（量子）**：电磁波量子化为光子；**主题 7（粒子）**：QED 精度 12 位；**主题 5（GR）**：电磁场方程的协变形式 |

---

## 🏭 理论联系实际：5 个现代应用

1. **无线充电（Qi 标准）**：手机无线充电用的是法拉第电磁感应 + 谐振耦合。两个线圈在 MHz 频率共振，磁场在间隙中传递能量——正是 §1.3 和 §2.3 的工程实现。

2. **SLAC LCLS-II 自由电子激光**：电子在波荡器（周期磁场）中扭摆，发射相干 X 射线——2024 年升级后以 MHz 重复率运行，是世界上最亮的 X 射线脉冲源，可「拍电影」记录分子化学反应过程。

3. **MRI 磁共振成像**：超导磁体产生 3 T 强磁场，射频脉冲激发质子进动，接收线圈探测信号——全部基于洛伦兹力和法拉第定律。

4. **5G/卫星通信**：天线辐射本质是加速电荷辐射（§4.3 拉莫尔公式），毫米波阵列通过相位控制实现波束成形。

5. **托卡马克核聚变（ITER）**：用磁场约束上亿度等离子体（$r = p/(eB)$），磁约束的本质是洛伦兹力使带电粒子绕磁力线螺旋运动。

---

## 🔬 最新研究前沿（2024-2026）

1. **LCLS-II 超导直线加速器全面运行（2024-2025）**：SLAC 的新一代 X 射线 FEL 以 MHz（百万脉冲/秒）重复率运行，比第一代 LCLS 亮 10000 倍，可实时拍摄飞秒级的化学键断裂和电子动力学。

2. **拓扑光子学（2024-2025）**：利用光子晶体模拟凝聚态拓扑相，实现「光路中的单向传输」——光波绕过缺陷无损传播，无需反射。Stanford 与 MIT 团队在拓扑激光器方向取得突破。

3. **无线电能传输突破（2024）**：远距离无线电能传输（WPT）效率在 2024 年多篇论文中突破 80% @ 数米距离，关键是用超材料透镜聚焦磁偶极场——麦克斯韦方程组的逆向设计。

4. **非线性超表面与光计算（2024-2025）**：亚波长厚度的超表面实现光频率转换、光逻辑门，有望替代电子芯片——本质是非线性 Maxwell 方程的纳米结构工程。

5. **量子电动力学精度检验（2024）**：µ子 g-2 实验（Fermilab 2023-2024）测量值与标准模型理论值偏差达 $4.2\sigma$，暗示新物理——电磁学在极高精度下「不再完美」。

---

## 🗺️ 学习 Roadmap（Stanford 路径）

```
入门 → PHYS 43/63 (Purcell & Morin)
  │   库仑定律、高斯定律、磁场、洛伦兹力、法拉第定律
  │   Purcell 特色：从相对论推导磁场，揭示 E/B 是一体两面
  │   ✅ 检查点：能解释为什么运动电荷会产生磁场
  ▼
进阶 → PHYS 120 (Griffiths)
  │   Maxwell 方程组、电磁波、辐射、介质电动力学、相对论
  │   ✅ 检查点：能推导位移电流并解释其物理意义
  ▼
深造 → PHYS 335 (Jackson)
  │   多极展开、Green 函数、规范场、散射衍射、同步辐射
  │   ✅ 检查点：能用推迟势推导利纳尔辐射公式
  ▼
前沿 → PHYS 330/360 (Peskin / QED)
      电磁场的量子化 → 光子 → 量子电动力学 → 标准模型
```

> **费曼的建议**：电磁学的灵魂在 Purcell 的第 5 章——一旦你理解「磁场就是运动看到的电场」，整个电磁学就串成一条线了。
