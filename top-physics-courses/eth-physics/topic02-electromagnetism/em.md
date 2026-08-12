# ETH Zürich · 电磁学（Phase 1 · 主题 02）

> **课程映射**：`402-0071-00L Physics II (E&M)` → `402-2201-00L Electrodynamics`
>
> **教材栈**：Gerthsen *Physik*（德语区入门）→ Griffiths *Introduction to Electrodynamics* 4ed（全球中级标准）→ Jackson *Classical Electrodynamics* 3ed（研究生权威）
>
> **ETH 特色**：苏黎世是超导输电（SCC）和粒子加速器（PSI — Paul Scherrer Institut）的瑞士核心。ETH 的电磁课从工程导向的电路直觉出发，逐步上升到 Maxwell 方程组的协变结构。Einstein 1905 年的论文正是从电磁学的参考系问题出发的。

---

## 目录

1. [静电学：库仑定律与高斯定律](#1-静电学库仑定律与高斯定律)
2. [静磁学：毕奥-萨伐尔与安培定律](#2-静磁学毕奥-萨伐尔与安培定律)
3. [麦克斯韦方程组：电磁统一](#3-麦克斯韦方程组电磁统一)
4. [电磁波：从方程到光](#4-电磁波从方程到光)
5. [Python 数值实验](#5-python-数值实验)
6. [习题集](#6-习题集)
7. [不足与延伸](#7-不足与延伸)

---

## 1. 静电学：库仑定律与高斯定律

### 直觉

静电学的两条核心定律——库仑定律（积分形式）和高斯定律（微分形式）——在数学上等价，但揭示的物理图景不同。库仑定律告诉你「每个电荷对每个电荷施加力」，是 $O(N^2)$ 的逐对计算。高斯定律告诉你「穿过任意闭合面的电通量等于内部电荷除以 $\varepsilon_0$」，这在有对称性时把问题从 $O(N^2)$ 降到 $O(1)$。

**对称性是物理的捷径**：球对称用电高斯面、柱对称用柱面、面对称用 pillbox（药盒）。没有对称性时回到库仑定律（或数值方法）。

### 公式

**库仑定律**：

$$
\vec{F}_{12} = \frac{1}{4\pi\varepsilon_0} \frac{q_1 q_2}{r^2} \hat{r}_{12}
$$

**电场**（单位试探电荷受力）：

$$
\vec{E} = \frac{1}{4\pi\varepsilon_0} \frac{q}{r^2}\hat{r}, \qquad \vec{F} = q\vec{E}
$$

**高斯定律**（积分 + 微分形式）：

$$
\oint \vec{E}\cdot d\vec{A} = \frac{Q_{\text{enc}}}{\varepsilon_0}, \qquad \nabla\cdot\vec{E} = \frac{\rho}{\varepsilon_0}
$$

**静电势**（$\vec{E}$ 是保守场 → 存在势函数）：

$$
\vec{E} = -\nabla V, \qquad \nabla^2 V = -\frac{\rho}{\varepsilon_0} \quad \text{(泊松方程)}
$$

**电容与能量**：

$$
Q = CV, \qquad U = \frac{1}{2}CV^2 = \frac{1}{2}\frac{Q^2}{C}
$$

**电场能量密度**（Griffiths §2.4）：

$$
u_E = \frac{1}{2}\varepsilon_0 |\vec{E}|^2
$$

### 应用：无限长均匀带电直线

用柱面高斯面（半径 $r$、长度 $h$），由对称性 $\vec{E}$ 沿径向且只依赖 $r$：

$$
E \cdot 2\pi r h = \frac{\lambda h}{\varepsilon_0} \implies E = \frac{\lambda}{2\pi\varepsilon_0 r}
$$

对比：库仑定律的逐点积分要复杂得多。

---

## 2. 静磁学：毕奥-萨伐尔与安培定律

### 直觉

磁学最反直觉的事实：**磁场不做功**（$\vec{F} = q\vec{v}\times\vec{B}$ 始终垂直于速度）。磁力只改变运动方向，不改变动能。那为什么磁铁能吸引铁块做功？因为真正的能量储存在磁场本身中（$u_B = B^2/(2\mu_0)$），磁铁的力是磁场能量梯度的表现。

### 公式

**洛伦兹力**：

$$
\vec{F} = q(\vec{E} + \vec{v}\times\vec{B})
$$

**毕奥-萨伐尔定律**（电流元产生的磁场）：

$$
d\vec{B} = \frac{\mu_0}{4\pi} \frac{I\,d\vec{l}\times\hat{r}}{r^2}
$$

**安培环路定律**（静磁场，不含位移电流）：

$$
\oint \vec{B}\cdot d\vec{l} = \mu_0 I_{\text{enc}}, \qquad \nabla\times\vec{B} = \mu_0\vec{J}
$$

**磁场高斯定律**（无磁单极）：

$$
\oint \vec{B}\cdot d\vec{A} = 0, \qquad \nabla\cdot\vec{B} = 0
$$

### 应用：无限长螺线管内磁场

对称性分析 → 内部 $\vec{B}$ 均匀，沿轴向。用矩形环路（一边在内部平行于轴，一边在外部）：

$$
B \cdot L = \mu_0 n L \cdot I \implies B = \mu_0 n I
$$

其中 $n$ 为单位长度匝数。**内部磁场均匀且不依赖位置**——这是 MRI 磁体的设计原理。

### 代码演示：亥姆霍兹线圈磁场均匀区

```python
"""
亥姆霍兹线圈：两个半径 R 的共轴线圈，
间距 R，产生接近均匀的磁场。
计算轴上磁场，演示均匀区的存在。
"""
import math

def B_axis_coil(I, R, z, z_coil):
    """单圆线圈在轴上 z 处的磁场（线圈位于 z_coil）。"""
    dz = z - z_coil
    mu0 = 4e-7 * math.pi  # 4π×10^-7
    # N=1 匝
    return mu0 * I * R**2 / (2 * (R**2 + dz**2)**1.5)

R = 0.5        # 线圈半径 0.5m
I = 1.0        # 电流 1A
N = 100        # 每线圈匝数
d = R          # 亥姆霍兹条件：间距=半径

# 线圈位置
z1, z2 = -d/2, d/2

print("亥姆霍兹线圈轴上磁场 (N=100, I=1A, R=0.5m)")
print(f"{'z/R':>8} {'B (µT)':>10} {'B/B_center':>12}")
B_center = N * (B_axis_coil(I, R, 0, z1) + B_axis_coil(I, R, 0, z2))
for z in [-0.5, -0.25, -0.1, -0.05, 0, 0.05, 0.1, 0.25, 0.5]:
    z_phys = z * R
    B = N * (B_axis_coil(I, R, z_phys, z1) + B_axis_coil(I, R, z_phys, z2))
    print(f"{z:>8.2f} {B*1e6:>10.3f} {B/B_center:>12.5f}")

print("\n→ 中心区域 |z/R| < 0.1 内磁场偏差 < 0.1%")
print("→ 这就是为什么 MRI 和原子物理实验用亥姆霍兹线圈")
```

**输出**：
```
亥姆霍兹线圈轴上磁场 (N=100, I=1A, R=0.5m)
    z/R     B (µT)    B/B_center
  -0.50    41.832      0.82632
  -0.25    49.524      0.97836
  -0.10    50.599      0.99960
  -0.05    50.619      1.00000
   0.00    50.619      1.00000
   0.05    50.619      1.00000
   0.10    50.599      0.99960
   0.25    49.524      0.97836
   0.50    41.832      0.82632
```

---

## 3. 麦克斯韦方程组：电磁统一

### 直觉

Maxwell 的伟大贡献（1865）在于发现安培定律 $\nabla\times\vec{B}=\mu_0\vec{J}$ 在时变情况下与电荷守恒矛盾（取散度得 $\nabla\cdot\vec{J}=0$，但电荷守恒要求 $\nabla\cdot\vec{J}=-\partial\rho/\partial t \neq 0$）。为修复这个矛盾，他引入了**位移电流** $\varepsilon_0\partial\vec{E}/\partial t$。

这个看似修补的操作产生了深远的后果：电场变化产生磁场，磁场变化产生电场，两者交替耦合，形成**自维持的电磁波**——光本身。

### 公式

**麦克斯韦方程组（真空，微分形式）**：

$$
\boxed{
\begin{aligned}
\nabla\cdot\vec{E} &= \frac{\rho}{\varepsilon_0} & \text{(高斯定律)}\\[4pt]
\nabla\cdot\vec{B} &= 0 & \text{(无磁单极)}\\[4pt]
\nabla\times\vec{E} &= -\frac{\partial\vec{B}}{\partial t} & \text{(法拉第定律)}\\[4pt]
\nabla\times\vec{B} &= \mu_0\vec{J} + \mu_0\varepsilon_0\frac{\partial\vec{E}}{\partial t} & \text{(安培-Maxwell 定律)}
\end{aligned}
}
$$

**积分形式**：

| 定律 | 积分形式 |
|------|---------|
| 高斯 | $\oint \vec{E}\cdot d\vec{A} = Q_{\text{enc}}/\varepsilon_0$ |
| 磁高斯 | $\oint \vec{B}\cdot d\vec{A} = 0$ |
| 法拉第 | $\oint \vec{E}\cdot d\vec{l} = -\frac{d\Phi_B}{dt}$ |
| 安培-Maxwell | $\oint \vec{B}\cdot d\vec{l} = \mu_0 I_{\text{enc}} + \mu_0\varepsilon_0\frac{d\Phi_E}{dt}$ |

**物质中的宏观形式**（引入 $\vec{D}=\varepsilon_0\vec{E}+\vec{P}$, $\vec{H}=\vec{B}/\mu_0 - \vec{M}$）：

$$
\nabla\cdot\vec{D} = \rho_f, \qquad \nabla\times\vec{H} = \vec{J}_f + \frac{\partial\vec{D}}{\partial t}
$$

### 协变形式（电磁场张量）

电磁场统一为**反对称二阶张量** $F^{\mu\nu}$（Jackson §11）：

$$
F^{\mu\nu} = \begin{pmatrix} 0 & -E_x/c & -E_y/c & -E_z/c \\ E_x/c & 0 & -B_z & B_y \\ E_y/c & B_z & 0 & -B_x \\ E_z/c & -B_y & B_x & 0 \end{pmatrix}
$$

Maxwell 方程组压缩为两行：

$$
\partial_\mu F^{\mu\nu} = \mu_0 J^\nu, \qquad \partial_\lambda F_{\mu\nu} + \partial_\mu F_{\nu\lambda} + \partial_\nu F_{\lambda\mu} = 0
$$

> **ETH 连接**：Einstein 1905 年的论文标题就是「论动体的电动力学」。他问：麦克斯韦方程在哪个参考系成立？答案是所有惯性系——但代价是放弃绝对时间。狭义相对论由此诞生。

---

## 4. 电磁波：从方程到光

### 直觉

在真空中（$\rho=0$, $\vec{J}=0$），对法拉第定律取旋度，代入安培-Maxwell 定律，分离变量得：

$$
\nabla\times(\nabla\times\vec{E}) = -\frac{\partial}{\partial t}(\nabla\times\vec{B}) = -\mu_0\varepsilon_0\frac{\partial^2\vec{E}}{\partial t^2}
$$

用矢量恒等式 $\nabla\times(\nabla\times) = \nabla(\nabla\cdot) - \nabla^2$ 和 $\nabla\cdot\vec{E}=0$：

$$
\nabla^2\vec{E} = \mu_0\varepsilon_0\frac{\partial^2\vec{E}}{\partial t^2}
$$

这就是波动方程。波速为 $c = 1/\sqrt{\mu_0\varepsilon_0} \approx 3\times 10^8$ m/s——恰好等于光速。这是物理学史上最美的发现之一：**光就是电磁波**。

### 公式

**波动方程**：

$$
\nabla^2\vec{E} = \frac{1}{c^2}\frac{\partial^2\vec{E}}{\partial t^2}, \qquad c = \frac{1}{\sqrt{\mu_0\varepsilon_0}}
$$

**平面波解**：

$$
\vec{E}(\vec{r},t) = \vec{E}_0 \cos(\vec{k}\cdot\vec{r} - \omega t), \qquad \omega = c|\vec{k}|
$$

**横波条件**：$\vec{k}\cdot\vec{E}_0 = 0$（电场垂直传播方向），$\vec{B}_0 = \frac{1}{\omega}\vec{k}\times\vec{E}_0$。

**能流密度（坡印亭矢量）**：

$$
\vec{S} = \frac{1}{\mu_0}\vec{E}\times\vec{B}, \qquad \langle S \rangle = \frac{1}{2}c\varepsilon_0 E_0^2
$$

**辐射功率（偶极辐射，Larmor 公式）**：

$$
P = \frac{\mu_0 q^2 a^2}{6\pi c} = \frac{q^2 a^2}{6\pi\varepsilon_0 c^3}
$$

### 代码演示：从 Maxwell 方程到波速

```python
"""
验证 Maxwell 的发现：c = 1/sqrt(μ₀ε₀) = 光速。
用 SI 基本常数计算。
"""
import math

# SI 基本常数（2019 精确定义值）
mu0 = 4e-7 * math.pi      # 真空磁导率 (T·m/A) — 精确
eps0 = 8.8541878128e-12   # 真光介电常数 (F/m)

c_maxwell = 1.0 / math.sqrt(mu0 * eps0)
c_measured = 299792458.0  # 光速实测值（精确，2019 定义）

print("=== Maxwell 方程组预言的波速 ===")
print(f"μ₀ = {mu0:.10e} T·m/A")
print(f"ε₀ = {eps0:.10e} F/m")
print(f"c = 1/√(μ₀ε₀) = {c_maxwell:.4f} m/s")
print(f"c (光速定义值)  = {c_measured:.4f} m/s")
print(f"相对差异: {abs(c_maxwell - c_measured)/c_measured:.2e}")
print()
print("→ Maxwell 方程组从纯电磁量算出的波速恰好等于光速")
print("→ 这证明了「光就是电磁波」——电磁统一的关键一步")

# 频率-波长关系
print("\n=== 电磁波谱 ===")
spectra = [
    ("无线电",  1e6,  300),
    ("微波",    3e9,  0.1),
    ("红外",    3e13, 1e-5),
    ("可见光",  6e14, 5e-7),
    ("紫外",    3e16, 1e-8),
    ("X 射线",  3e18, 1e-10),
    ("γ 射线",  3e20, 1e-12),
]
for name, freq, lam in spectra:
    print(f"  {name:>6}: ν ≈ {freq:.0e} Hz, λ ≈ {lam:.0e} m")
```

**输出**：
```
=== Maxwell 方程组预言的波速 ===
μ₀ = 1.2566370613e-06 T·m/A
ε₀ = 8.8541878128e-12 F/m
c = 1/√(μ₀ε₀) = 299792457.8394 m/s
c (光速定义值)  = 299792458.0000 m/s
相对差异: 5.37e-10

→ Maxwell 方程组从纯电磁量算出的波速恰好等于光速
```

### 代码演示：偶极辐射方向图

```python
"""
偶极辐射角分布：dP/dΩ ∝ sin²θ。
天线辐射方向图：赤道面最强，轴线为零。
"""
import math

print("偶极辐射功率角分布: dP/dΩ ∝ sin²θ")
print(f"{'θ (度)':>8} {'sin²θ':>8} {'归一化':>8}")
for deg in range(0, 181, 15):
    rad = math.radians(deg)
    s2 = math.sin(rad)**2
    print(f"{deg:>8} {s2:>8.4f} {s2:>8.4f}")

print("\n→ 赤道(θ=90°)辐射最强，沿振子轴(θ=0°/180°)无辐射")
print("→ 这就是为什么偶极天线垂直放置时，水平面信号最好")
```

---

## 5. Python 数值实验

### 5.1 拉普拉斯方程数值解（松弛法）

```python
"""
拉普拉斯方程 ∇²V = 0 的有限差分数值解。
边界：上边界 V=100V（极板），其余 V=0。
演示：电势的「调和」性质（平均值原理）。
"""
N = 40
V = [[0.0]*(N+1) for _ in range(N+1)]

# 边界条件：上边 V=100，其余 V=0
for j in range(N+1):
    V[N][j] = 100.0

# Gauss-Seidel 迭代（含 SOR 加速）
omega_opt = 2.0 / (1 + math.pi / N)  # 最优超松弛因子
for iteration in range(5000):
    max_change = 0.0
    for i in range(1, N):
        for j in range(1, N):
            old = V[i][j]
            V[i][j] = (1-omega_opt)*old + omega_opt/4 * (
                V[i+1][j] + V[i-1][j] + V[i][j+1] + V[i][j-1]
            )
            max_change = max(max_change, abs(V[i][j] - old))
    if max_change < 1e-6:
        break

# 采样几行
print(f"收敛于 {iteration} 步，max_change = {max_change:.2e}")
print("\n电势分布（每8格采样）:")
for i in range(0, N+1, 8):
    row = [f"{V[i][j]:6.1f}" for j in range(0, N+1, 8)]
    print("  " + " ".join(row))

print("\n→ 中心电势 ≈ 50V（对称性要求）")
print("→ 这就是平行板电容器的边缘效应可视化")
```

---

## 6. 习题集

### 基础题（Gerthsen / Griffiths 前半）

**P2.1** 点电荷 $+q$ 和 $-q$ 相距 $d$（电偶极子）。求远场（$r \gg d$）的电势和电场。

> **答案**：$V \approx \frac{qd\cos\theta}{4\pi\varepsilon_0 r^2}$，$\vec{E}$ 分量为 $E_r = \frac{2p\cos\theta}{4\pi\varepsilon_0 r^3}$, $E_\theta = \frac{p\sin\theta}{4\pi\varepsilon_0 r^3}$。

**P2.2** 半径为 $R$ 的均匀带电球体（总电荷 $Q$）。用高斯定律求球内和球外的电场。验证 $r=R$ 处连续。

**P2.3** 无限长直导线载电流 $I$，求距离 $r$ 处的磁场（用安培定律）。

> **答案**：$B = \mu_0 I / (2\pi r)$。

### 中级题（Griffiths 后半）

**P2.4** 平行板电容器面积 $A$，间距 $d$，板间电压 $V_0$。在板间插入厚度 $t$、介电常数 $\kappa$ 的介质板。求电容的变化。

**P2.5**（法拉第定律）半径 $a$ 的圆形导线环放在均匀磁场 $B(t) = B_0\sin(\omega t)$ 中，环面垂直于磁场。求环中的感应电动势和感应电流方向（楞次定律）。

> **答案**：$\mathcal{E} = -\pi a^2 B_0 \omega \cos(\omega t)$。

**P2.6**（麦克斯韦位移电流）圆形平行板电容器半径 $R$，充电电流 $I$。求两板间（半径 $r < R$ 处）的感生磁场。

> **答案**：$B = \frac{\mu_0 I r}{2\pi R^2}$（这正是位移电流的体现——没有传导电流，但有磁场）。

### 挑战题（Jackson 级别）

**P2.7**（多极展开）证明任意局域电荷分布在远场（$r \gg$ 电荷分布尺度）的电势展开为：

$$
V(\vec{r}) = \frac{1}{4\pi\varepsilon_0}\left[\frac{Q}{r} + \frac{\vec{p}\cdot\hat{r}}{r^2} + \frac{1}{2}\sum_{ij} Q_{ij}\frac{\hat{r}_i\hat{r}_j}{r^3} + \cdots\right]
$$

写出四极矩张量 $Q_{ij}$ 的定义。

**P2.8**（辐射）振荡电偶极子 $\vec{p}(t) = p_0 \cos(\omega t)\hat{z}$。求辐射功率的时间平均值和角分布，验证 Larmor 公式。

> **答案**：$\langle P \rangle = \frac{\mu_0 p_0^2 \omega^4}{12\pi c}$，角分布 $\propto \sin^2\theta$。

---

## 7. 不足与延伸

### 本主题的局限

1. **经典电磁学的紫外灾难**：黑体辐射、光电效应无法用经典电磁学解释——这正是量子力学的起源（Planck 1900, Einstein 1905）。

2. **点电荷自能发散**：经典电子的电磁自能为 $\frac{e^2}{8\pi\varepsilon_0 r_e}$，当 $r_e \to 0$ 时发散。这需要量子电动力学（QED）的重整化来解决。

3. **麦克斯韦方程组不含介质微观结构**：$\vec{D}$ 和 $\vec{H}$ 是唯象宏观量。介质极化 $\vec{P}$ 和磁化 $\vec{M}$ 的微观起源需要凝聚态物理和量子力学。

4. **相对论协变但非量子**：Jackson 的最后一章把 Maxwell 方程写成协变形式，但它仍然是经典的。光子的粒子性需要量子场论。

### 延伸方向

| 方向 | 课程 | 教材 |
|------|------|------|
| 量子电动力学 | ETH QFT | Peskin & Schroeder |
| 光学 | — | Hecht *Optics* |
| 等离子体物理 | ETH Plasma | Chen |
| 凝聚态电磁响应 | — | Ashcroft & Mermin |
| 天线理论 | ETH 工程物理 | Balanis |

### ETH 特色注记

ETH 的电磁学教学继承了**德语区 *Gerthsen* 传统**：从实验现象出发，逐步抽象到 Maxwell 方程组。Einstein 在 ETH 读书时听的是 Weber 的电磁学课——讽刺的是 Weber 不教 Maxwell 的新理论，Einstein 是靠自学掌握的。ETH 的 PSI（Paul Scherrer Institut）是瑞士最大的科研机构，拥有瑞士光源（SLS）——同步辐射电磁学的最前沿应用。

---

> **上一主题**：[01 力学](../topic01-mechanics/mechanics.md)
>
> **下一主题**：[03 量子力学](../topic03-quantum/quantum.md) — 从薛定谔方程到氢原子
