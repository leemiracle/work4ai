# Topic 02: 电磁学 — 从静电到麦克斯韦方程组

> **UC Berkeley 课程映射**：7B (E&M, Knight) → 110A (Electrodynamics, Griffiths Ch 1-7) → 110B (Electrodynamics II, Griffiths Ch 8-12 / Jackson)
>
> **教材体系**：
> - **入门**：Knight "Physics for Scientists and Engineers"（7B）
> - **荣誉入门**：**Purcell & Morin "Electricity and Magnetism"**（Berkeley Physics Course Vol. 2！）
> - **中级**：Griffiths "Introduction to Electrodynamics" 4ed（110A/110B 主教材）
> - **研究生**：Jackson "Classical Electrodynamics" 3ed（110B 高阶章节）

---

## 目录

1. [§1 静电学](#1-静电学)
2. [§2 静磁学](#2-静磁学)
3. [§3 麦克斯韦方程组](#3-麦克斯韦方程组)
4. [§4 电磁波](#4-电磁波)
5. [§5 Berkeley 特色：Purcell 传统](#5-berkeley-特色purcell-传统)
6. [习题集](#习题集)
7. [Python 演示](#python-演示)

---

## §1 静电学

### 1.1 Coulomb 定律与电场

**直觉**：电荷在空间中产生电场，电场作用于其他电荷。两个点电荷之间的力由 Coulomb 定律给出。

$$\boxed{\mathbf{F}_{12} = \frac{1}{4\pi\epsilon_0} \frac{q_1 q_2}{r^2} \hat{\mathbf{r}}}$$

电场定义：

$$\mathbf{E}(\mathbf{r}) = \frac{1}{4\pi\epsilon_0} \int \frac{\rho(\mathbf{r}')(\mathbf{r} - \mathbf{r}')}{|\mathbf{r} - \mathbf{r}'|^3} d^3r'$$

### 1.2 Gauss 定律

**Griffiths 第2章核心**：Gauss 定律是 Coulomb 定律的积分形式，但对高对称性电荷分布（球、柱、面），它远比直接积分强大。

$$\oint \mathbf{E} \cdot d\mathbf{A} = \frac{Q_{\text{enc}}}{\epsilon_0} \qquad \nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}$$

**经典应用**：

| 电荷分布 | 对称性 | 电场 |
|----------|--------|------|
| 均匀带电球（半径 $R$，总电荷 $Q$） | 球对称 | $E = \frac{1}{4\pi\epsilon_0}\frac{Q}{r^2}$（$r>R$），$E = \frac{Qr}{4\pi\epsilon_0 R^3}$（$r<R$） |
| 无限长均匀带电线（线电荷 $\lambda$） | 柱对称 | $E = \frac{\lambda}{2\pi\epsilon_0 r}$ |
| 无限大均匀带电面（面电荷 $\sigma$） | 面对称 | $E = \frac{\sigma}{2\epsilon_0}$（恒定！）|

### 1.3 电势

$$V(\mathbf{r}) = \frac{1}{4\pi\epsilon_0} \int \frac{\rho(\mathbf{r}')}{|\mathbf{r} - \mathbf{r}'|} d^3r'$$

$$\mathbf{E} = -\nabla V$$

### 1.4 电偶极子

电偶极矩 $\mathbf{p} = q\mathbf{d}$，远场电势和电场：

$$V_{\text{dip}} = \frac{1}{4\pi\epsilon_0} \frac{\mathbf{p} \cdot \hat{\mathbf{r}}}{r^2}$$

$$\mathbf{E}_{\text{dip}} = \frac{1}{4\pi\epsilon_0 r^3}\left[3(\mathbf{p}\cdot\hat{\mathbf{r}})\hat{\mathbf{r}} - \mathbf{p}\right]$$

**反直觉**：偶极子电场比点电荷衰减更快（$\sim 1/r^3$ vs $1/r^2$），因为正负电荷的场在远场几乎完全抵消。

### 1.5 静电能

$$U = \frac{\epsilon_0}{2} \int E^2\, d^3r = \frac{1}{2} \int \rho V\, d^3r$$

两种表达等价——前者说"能量储存在场中"，后者说"能量储存在电荷分布中"。Berkeley 倾向于前者（场的图像优先）。

---

## §2 静磁学

### 2.1 Lorentz 力

$$\boxed{\mathbf{F} = q(\mathbf{E} + \mathbf{v} \times \mathbf{B})}$$

### 2.2 Biot-Savart 定律

电流元产生的磁场：

$$d\mathbf{B} = \frac{\mu_0}{4\pi} \frac{I\, d\mathbf{l} \times \hat{\mathbf{r}}}{r^2}$$

**经典结果**：
- 无限长直导线：$B = \frac{\mu_0 I}{2\pi r}$
- 圆形电流环（轴上）：$B = \frac{\mu_0 I R^2}{2(R^2+z^2)^{3/2}}$
- 螺线管内部：$B = \mu_0 n I$（$n$ = 单位长度匝数）

### 2.3 Ampere 定律

$$\oint \mathbf{B} \cdot d\mathbf{l} = \mu_0 I_{\text{enc}} \qquad \nabla \times \mathbf{B} = \mu_0 \mathbf{J}$$

### 2.4 磁矢势

$$\mathbf{B} = \nabla \times \mathbf{A}$$

$$\mathbf{A}(\mathbf{r}) = \frac{\mu_0}{4\pi} \int \frac{\mathbf{J}(\mathbf{r}')}{|\mathbf{r} - \mathbf{r}'|} d^3r'$$

**Purcell 的独特视角**：磁矢势 $\mathbf{A}$ 不是数学技巧——在量子力学中（Aharonov-Bohm 效应），$\mathbf{A}$ 比磁场 $\mathbf{B}$ 更基本！

---

## §3 麦克斯韦方程组

### 3.1 完整方程组

**这是整个经典物理学的最高成就——四个方程统一了电和磁：**

$$\boxed{\begin{aligned} \nabla \cdot \mathbf{E} &= \frac{\rho}{\epsilon_0} & \text{(Gauss 定律)} \\ \nabla \cdot \mathbf{B} &= 0 & \text{(无磁单极)} \\ \nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} & \text{(Faraday 定律)} \\ \nabla \times \mathbf{B} &= \mu_0 \mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t} & \text{(Ampere-Maxwell 定律)} \end{aligned}}$$

### 3.2 Maxwell 的天才修正：位移电流

**Griffiths 第7章的关键推导**：Ampere 原始定律 $\nabla \times \mathbf{B} = \mu_0 \mathbf{J}$ 对电容器的充电电流不自洽（取一个跨介质的环路，面积取在极板间则 $I_{\text{enc}} = 0$，取穿过导线的面积则 $I_{\text{enc}} \neq 0$）。

Maxwell 引入位移电流 $\epsilon_0 \partial\mathbf{E}/\partial t$ 修复了这个矛盾，并预言了电磁波。

### 3.3 电磁波方程

在真空中（$\rho = 0$, $\mathbf{J} = 0$），取 $\nabla \times (\nabla \times \mathbf{E}) = -\partial/\partial t (\nabla \times \mathbf{B})$：

$$\nabla^2 \mathbf{E} = \mu_0\epsilon_0 \frac{\partial^2 \mathbf{E}}{\partial t^2}$$

$$\boxed{c = \frac{1}{\sqrt{\mu_0 \epsilon_0}} \approx 3 \times 10^8 \text{ m/s}}$$

**物理学史上最伟大的时刻之一**：光速 $c$ 纯粹由两个电磁学常数确定！

### 3.4 Poynting 矢量与辐射能量流

$$\mathbf{S} = \frac{1}{\mu_0} \mathbf{E} \times \mathbf{B}$$

电磁波携带的能量流密度。时间平均强度 $\langle S \rangle = \frac{1}{2} c \epsilon_0 E_0^2$。

---

## §4 电磁波

### 4.1 平面电磁波

$$\mathbf{E}(\mathbf{r}, t) = E_0 \cos(kz - \omega t)\,\hat{\mathbf{x}}, \quad \mathbf{B} = \frac{E_0}{c}\cos(kz-\omega t)\,\hat{\mathbf{y}}$$

$\mathbf{E}$, $\mathbf{B}$, $\mathbf{k}$ 三者互相垂直，$|\mathbf{B}| = |\mathbf{E}|/c$。

### 4.2 介质中的电磁波

$$v = \frac{c}{n}, \qquad n = \sqrt{\epsilon_r \mu_r}$$

折射率 $n$ 由介电常数和磁导率决定。

### 4.3 偏振

线偏振、圆偏振（左旋/右旋）、椭圆偏振。偏振态可用 Jones 矢量描述。

$$\text{右旋圆偏振：} \quad \hat{\mathbf{e}}_R = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ -i \end{pmatrix}$$

### 4.4 辐射：偶极辐射

加速电荷辐射电磁波。振荡偶极子的辐射功率（Larmor 公式的周期平均）：

$$\langle P \rangle = \frac{\mu_0 p_0^2 \omega^4}{12\pi c}$$

**反直觉**：辐射功率正比于 $\omega^4$——这就是为什么天空是蓝色的（蓝光频率高，瑞利散射截面 $\propto \omega^4$）！

---

## §5 Berkeley 特色：Purcell 传统

### Purcell "Electricity and Magnetism"（Berkeley Physics Course Vol. 2）

**Edward M. Purcell**（1912-1997），Berkeley 本科校友（1933），Harvard 教授，诺贝尔物理学奖（1952，核磁共振）。

他的教材 **"Electricity and Magnetism"**（1963 初版，Morin 2013 修订第3版）是 Berkeley Physics Course 的第二卷，有三大革命性特色：

#### 特色 1：相对论先行（Berkeley 传统）

Purcell 在第 5 章用 **狭义相对论** 推导磁场！方法如下：

1. 先建立电场 $\mathbf{E}$ 的概念（Coulomb 定律）。
2. 考虑一个以速度 $\mathbf{v}$ 运动的参考系。
3. 在运动系中，由于 Lorentz 收缩，电荷密度改变，电场也随之改变。
4. **磁场不是新的力——它只是运动参考系中看到的电场的相对论修正！**

$$\mathbf{F}_{\text{mag}} = q\mathbf{v} \times \mathbf{B}$$

在 Purcell 的框架中，磁力纯粹是电力的相对论效应。

**对比 Griffiths**：Griffiths 的 110A 课程在 Ch 5 才引入相对论，且磁场作为独立现象先讲。Purcell 的方法更深刻但更难——它揭示了电磁学的本质统一性。

#### 特色 2：强调微观图像

Purcell 大量使用原子和分子图像解释宏观现象：
- 极化 = 原子偶极矩排列
- 磁化 = 电子轨道/自旋角动量排列
- 导体 = 自由电子气

#### 特色 3：物理直觉优先于数学

Purcell 有意避免高级矢量分析（如 $\nabla$ 算符的复杂运算），而是用对称性和物理论证。这使得概念更深刻，但不如 Griffiths 系统化。

#### Berkeley 110A 如何选择？

| 方面 | Griffiths 路线 | Purcell 路线 |
|------|---------------|-------------|
| 磁场引入 | 实验事实（Biot-Savart） | 相对论推导 |
| 数学水平 | 完整矢量分析 | 物理论证为主 |
| 习题风格 | 计算密集 | 概念密集 |
| 适合 | 标准物理主修 | 荣誉/理论方向 |

Berkeley 110A 标准用 Griffiths，但 Purcell 作为补充阅读被强力推荐。

---

## 习题集

### 基础题（7B 级别）

**习题 2.1**：求均匀带电球壳（半径 $R$，总电荷 $Q$）内外的电场。
> **解**：$E = 0$（$r < R$），$E = \frac{Q}{4\pi\epsilon_0 r^2}$（$r > R$）。

**习题 2.2**：两平行金属板（面积 $A$，间距 $d$，电势差 $V$）形成电容器。求电容。
> **解**：$C = \epsilon_0 A / d$。

**习题 2.3**：无限长直导线载电流 $I$，求距离 $r$ 处的磁场。
> **解**：$B = \mu_0 I / (2\pi r)$。

### 中级题（110A 级别，Griffiths）

**习题 2.4**（Griffiths 2.50）：半径为 $R$ 的球内均匀分布电荷密度 $\rho$。求球内外的电势。
> **提示**：先求电场 $E_{\text{in}} = \rho r / (3\epsilon_0)$，$E_{\text{out}} = \rho R^3 / (3\epsilon_0 r^2)$，再积分 $V = -\int_\infty^r E\, dr$。

**习题 2.5**（Griffiths 5.13）：电偶极子 $\mathbf{p}$ 在外电场 $\mathbf{E}$ 中的势能和力矩。
> **解**：$U = -\mathbf{p}\cdot\mathbf{E}$，$\boldsymbol{\tau} = \mathbf{p} \times \mathbf{E}$。

**习题 2.6**（Griffiths 7.35）：证明真空中 Maxwell 方程组在无源情况下支持平面波解，并求 $|\mathbf{E}|/|\mathbf{B}| = c$。

**习题 2.7**（Purcell 风格）：用 Purcell 的相对论方法，证明在以速度 $v$ 运动的参考系中，一个静止线电荷产生的电场变换出一个磁场 $B' = \gamma v E / c^2$。

### 挑战题

**习题 2.8**（Jackson 导引）：求振荡电偶极子的辐射场和角分布。
> **解**：$E_\theta \propto \sin\theta / r$，辐射功率 $\langle P \rangle = \mu_0 \omega^4 p_0^2 / (12\pi c)$。

**习题 2.9**（位移电流）：平行板电容器（圆形极板半径 $R$）以恒定速率 $dQ/dt = I$ 充电。求极板间距离轴 $r$ 处的磁场。
> **解**：$B = \frac{\mu_0 I r}{2\pi R^2}$（$r < R$）。这是位移电流的直接证据。

---

## Python 演示

### 演示 1：偶极子电场可视化

```python
"""
电偶极子电场线与等势线 — Berkeley 110A
Griffiths 3.4 节可视化。
"""
import numpy as np
import matplotlib.pyplot as plt

# --- 偶极子参数 ---
q = 1.0
d = 0.5  # 正负电荷间距的一半
k = 1.0  # 简化 1/(4πε₀)

x = np.linspace(-3, 3, 300)
y = np.linspace(-3, 3, 300)
X, Y = np.meshgrid(x, y)

# 正电荷在 (+d, 0)，负电荷在 (-d, 0)
r_pos = np.sqrt((X - d)**2 + Y**2)
r_neg = np.sqrt((X + d)**2 + Y**2)

# 避免奇点
r_pos = np.maximum(r_pos, 0.05)
r_neg = np.maximum(r_neg, 0.05)

# 电势
V = k * q * (1/r_pos - 1/r_neg)

# 电场（负梯度）
Ey, Ex = np.gradient(-V, y, x)
E_mag = np.sqrt(Ex**2 + Ey**2)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# 左：电场线
ax = axes[0]
ax.streamplot(X, Y, Ex, Ey, color=np.log(E_mag+0.1), linewidth=0.8,
              cmap='inferno', density=2, arrowsize=1.2)
ax.plot(d, 0, 'ro', markersize=10, label='+q')
ax.plot(-d, 0, 'bo', markersize=10, label='-q')
ax.set_title('Electric Dipole: Field Lines')
ax.set_aspect('equal')
ax.legend()

# 右：等势线
ax = axes[1]
levels = np.linspace(-30, 30, 40)
cs = ax.contour(X, Y, V, levels=levels, cmap='RdBu_r', linewidths=0.7)
ax.plot(d, 0, 'ro', markersize=10)
ax.plot(-d, 0, 'bo', markersize=10)
ax.set_title('Electric Dipole: Equipotential Lines')
ax.set_aspect('equal')

plt.tight_layout()
plt.savefig('dipole_field.png', dpi=150)
plt.show()
print("Notice: field lines go from + to -, but density ~ 1/r³ (dipole falls fast)")
```

### 演示 2：位移电流与电磁波传播

```python
"""
1D 电磁波传播 — Berkeley 110A
用 Yee 网格（FDTD 方法）模拟 Maxwell 方程组。
展示位移电流项如何让电磁波传播。
"""
import numpy as np
import matplotlib.pyplot as plt

# --- 1D FDTD 参数 ---
c = 3e8
dx = 0.01           # 空间步长 (m)
dt = dx / (2 * c)   # CFL 稳定条件
Nx = 500
Nt = 800

# 场量
Ez = np.zeros(Nx)   # z 方向电场
Hy = np.zeros(Nx)   # y 方向磁场

# 记录波形
snapshots = []
snapshot_times = [0, 100, 200, 400, 600]

# 高斯脉冲源
source_pos = Nx // 4
def source(t):
    return np.exp(-((t - 50) / 15)**2) * np.sin(2 * np.pi * t / 30)

# --- FDTD 主循环 ---
# E 更新: ∂E/∂t = (1/ε₀) ∂H/∂x
# H 更新: ∂H/∂t = (1/μ₀) ∂E/∂x
# 归一化单位使得 c = 1/(√(ε₀μ₀)) = dx/(2dt)

for t in range(Nt):
    # 更新磁场 (Faraday 定律)
    Hy[:-1] -= 0.5 * (Ez[1:] - Ez[:-1])

    # 更新电场 (Ampere-Maxwell 定律，含位移电流!)
    Ez[1:] -= 0.5 * (Hy[1:] - Hy[:-1])

    # 注入源
    Ez[source_pos] += source(t)

    # 边界条件 (Mur 吸收边界)
    Ez[0] = Ez[1]
    Ez[-1] = Ez[-2]

    if t in snapshot_times:
        snapshots.append(Ez.copy())

fig, axes = plt.subplots(len(snapshots), 1, figsize=(9, 10), sharex=True)
x_axis = np.arange(Nx) * dx * 100  # 转为 cm

for ax, snap, t in zip(axes, snapshots, snapshot_times):
    ax.plot(x_axis, snap, 'b-', linewidth=1)
    ax.set_ylabel(f't={t}')
    ax.set_ylim(-1.2, 1.2)
    ax.axhline(0, color='gray', linewidth=0.3)

axes[-1].set_xlabel('Position (cm)')
axes[0].set_title('EM Wave Propagation (1D FDTD)\nMaxwell eqs with displacement current → wave speed c')
plt.tight_layout()
plt.savefig('em_wave.png', dpi=150)
plt.show()
print("Key insight: without the displacement current term, NO wave would propagate!")
```

### 演示 3：偶极辐射角分布

```python
"""
振荡偶极子的辐射方向图 — Berkeley 110B
功率 ∝ sin²θ (donut shape)。
"""
import numpy as np
import matplotlib.pyplot as plt

theta = np.linspace(0, 2*np.pi, 500)
intensity = np.sin(theta)**2  # sin²θ

fig, ax = plt.subplots(1, 1, figsize=(7, 7), subplot_kw=dict(projection='polar'))
ax.plot(theta, intensity, 'r-', linewidth=2)
ax.fill_between(theta, 0, intensity, alpha=0.2, color='red')
ax.set_title('Dipole Radiation Pattern\nPower ∝ sin²θ', pad=20)
ax.set_theta_zero_location('E')
plt.tight_layout()
plt.savefig('dipole_radiation.png', dpi=150)
plt.show()
print("Maximum radiation ⊥ to dipole axis; zero along axis.")
```

---

## 学习路径建议

```
7B (Knight)  →  基础 E&M（Coulomb, Biot-Savart, 基本电路）
      ↓
110A (Griffiths Ch 1-7)  →  静电 + 静磁 + Maxwell 方程
      ↓  (可选补充: Purcell Vol.2 第5章——相对论推导磁场)
110B (Griffiths Ch 8-12)  →  电磁波 + 辐射 + 相对论
      ↓
研究生 Jackson  →  高级电动力学（波导, 多极辐射, 辐射反作用）
```

**Griffiths 教材学习节奏**（Berkeley 110A 一学期 15 周）：
- 周 1-3：Ch 1-2（矢量分析 + 静电学）
- 周 4-5：Ch 3（电多极展开）
- 周 6-7：Ch 4（物质中的电场）
- 周 8-10：Ch 5（静磁学）
- 周 11-12：Ch 6（物质中的磁场）
- 周 13-15：Ch 7（Maxwell 方程组 + 位移电流）

---

> **文件信息**：Berkeley Physics · Topic 02 Electromagnetism · 2026-08-12
> 
> **教材交叉引用**：Knight (7B) / Purcell (Berkeley Phys Course Vol.2) / Griffiths (110A/110B) / Jackson (研究生)
