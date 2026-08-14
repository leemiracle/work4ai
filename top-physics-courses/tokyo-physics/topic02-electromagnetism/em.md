# 東京大学物理系 Phase 1 · 電磁気学 深度講義

> **课程映射**（SURVEY §9 東大）：電磁気学
> **教材**：David J. Griffiths *Introduction to Electrodynamics* 4ed（東大指定，吉岡書店日文译本《電磁気学》）+ Purcell & Morin *Electricity and Magnetism* 3ed（荣誉版补充，Berkeley Physics Course Vol 2）
> **定位**：从 Coulomb 定律到 Maxwell 方程组再到电磁波，完成经典电动力学的闭环。Maxwell 方程组是物理学史上第一个**大统一**——电与磁与光的统一。東大此课的招牌是把积分形式与微分形式「并排推导」，让学生看到两种语言等价。

---

## 0. 導引：電磁気学為何是物理学的「中枢」

Maxwell（1865）把四个零散的实验定律统一成一组偏微分方程，并预言电磁波速度 $c = 1/\sqrt{\mu_0\varepsilon_0}$ 恰好等于光速——这一刻，「光就是电磁波」成为定理。Einstein 狭义相对论（1905）正是被 Maxwell 方程组在伽利略变换下不对称所驱动。所以 Griffiths 全书的逻辑线是：

$$\text{Coulomb/Biot-Savart（实验）} \to \text{积分形式} \to \text{微分形式} \to \text{势 + 规范} \to \text{电磁波} \to \text{辐射}$$

東大此课沿同一路线，但更强调**边界条件与镜像法**（这是日本高考与入试的经典题型）。

---

## 1. 静電気（Electrostatics）

### 1.1 Coulomb 定律与电场

两个点电荷间的力（Coulomb 1785）：

$$\vec{F}_{12} = \frac{1}{4\pi\varepsilon_0}\frac{q_1 q_2}{r^2}\hat{r} \approx (8.99\times10^9)\frac{q_1 q_2}{r^2}\hat{r}$$

定义**电场**（electric field）为单位试探电荷所受力：$\vec{E} = \vec{F}/q$。点电荷的电场：

$$\vec{E}(\vec{r}) = \frac{1}{4\pi\varepsilon_0}\frac{q}{r^2}\hat{r}$$

### 1.2 Gauss 定律

**积分形式**——穿过任意闭合曲面的电通量正比于包围的净电荷：

$$\boxed{\oint_S \vec{E}\cdot d\vec{A} = \frac{Q_{\text{enc}}}{\varepsilon_0}}$$

**微分形式**（用散度定理）：

$$\nabla\cdot\vec{E} = \frac{\rho}{\varepsilon_0}$$

Gauss 定律的高对称情形（球、柱、面）能秒解——这是東大入试的拿分点。

### 1.3 电势（Electric Potential）

$\nabla\times\vec{E} = 0$（静电场无旋）$\Rightarrow$ $\vec{E} = -\nabla V$，定义电势：

$$V(\vec{r}) = \frac{1}{4\pi\varepsilon_0}\int \frac{\rho(\vec{r}')}{|\vec{r}-\vec{r}'|}d^3r'$$

满足 **Poisson 方程** $\nabla^2 V = -\rho/\varepsilon_0$（无电荷区 $\nabla^2 V = 0$，Laplace 方程）。

### 1.4 多极展开（Multipole Expansion）

远处看任意电荷分布，电势展开为：

$$V(\vec{r}) = \frac{1}{4\pi\varepsilon_0}\left[\frac{Q}{r} + \frac{\vec{p}\cdot\hat{r}}{r^2} + \frac{1}{2}\sum_{ij}Q_{ij}\frac{\hat{r}_i\hat{r}_j}{r^3} + \cdots\right]$$

其中 $\vec{p} = \sum q_i\vec{r}_i$ 是**电偶极矩**（dipole moment），$Q_{ij}$ 是四极矩张量。这是東大分子物理/凝聚态的常用工具——极性分子（如 $\text{H}_2\text{O}$）的偶极矩决定相互作用。

### 1.5 镜像法（Method of Images）

导体表面（等势 $V = 0$）外的点电荷 $+q$，电场等价于在镜像位置放 $-q$（无导体时）。对无穷大接地导体板上方距离 $d$ 处的点电荷：

- 等效偶极矩 $p = 2qd$
- 导体上的感应电荷总量 $= -q$（吸引）
- 电荷受力 $F = -\frac{q^2}{16\pi\varepsilon_0 d^2}$（镜像吸引）

> **東大特色**：镜像法是東大電磁気学的招牌题型。学会它，入试里导体问题几乎通杀。

### 1.6 边界条件

两种介质（$\varepsilon_1, \varepsilon_2$）界面处：

| 量 | 边界条件 |
|----|----------|
| 法向 $E$ | $\varepsilon_1 E_{1\perp} - \varepsilon_2 E_{2\perp} = \sigma_f$（自由面电荷）|
| 切向 $E$ | $E_{1\parallel} = E_{2\parallel}$（连续）|
| 法向 $D$ | $D_{1\perp} - D_{2\perp} = \sigma_f$ |
| 切向 $E$ 连续意味着电场线在界面「折射」|

---

## 2. 静磁気（Magnetostatics）

### 2.1 Biot–Savart 定律

稳恒电流元产生的磁场：

$$d\vec{B} = \frac{\mu_0}{4\pi}\frac{I\,d\vec{l}\times\hat{r}}{r^2}$$

例：长直导线（电流 $I$）距离 $a$ 处 $B = \mu_0 I/(2\pi a)$；半径 $R$ 圆环电流轴线上 $B(z) = \mu_0 I R^2/[2(R^2+z^2)^{3/2}]$。

### 2.2 Ampère 定律

**积分形式**：

$$\boxed{\oint_C \vec{B}\cdot d\vec{l} = \mu_0 I_{\text{enc}}}$$

**微分形式**：$\nabla\times\vec{B} = \mu_0\vec{J}$。

Ampère 定律的高对称情形（无限长直导线、无限长螺线管、同轴电缆）能秒解。

### 2.3 矢势（Vector Potential）

$\nabla\cdot\vec{B} = 0$（无磁单极）$\Rightarrow$ $\vec{B} = \nabla\times\vec{A}$，定义**矢势** $\vec{A}$：

$$\vec{A}(\vec{r}) = \frac{\mu_0}{4\pi}\int \frac{\vec{J}(\vec{r}')}{|\vec{r}-\vec{r}'|}d^3r'$$

在 Coulomb 规范（$\nabla\cdot\vec{A} = 0$）下，$\vec{A}$ 满足 $\nabla^2\vec{A} = -\mu_0\vec{J}$。

### 2.4 磁偶极矩

电流环的磁偶极矩 $\vec{m} = I\vec{a}$（$\vec{a}$ 为面积矢量）。远处磁场等价于条形磁铁：

$$\vec{B}_{\text{dip}} = \frac{\mu_0}{4\pi r^3}\left[3(\vec{m}\cdot\hat{r})\hat{r} - \vec{m}\right]$$

形式与电偶极场完全对称——这是東大喜欢考的「电-磁对偶」。

---

## 3. Maxwell 方程組（Maxwell's Equations）

### 3.1 位移电流的引入

Ampère 定律 $\nabla\times\vec{B} = \mu_0\vec{J}$ 在电容充电时不自洽（取曲面跨过电容器极板间，$I_{\text{enc}} = 0$ 但 $\vec{B} \neq 0$）。Maxwell 的天才修补——**位移电流**（displacement current）：

$$\vec{J}_d = \varepsilon_0\frac{\partial\vec{E}}{\partial t}$$

### 3.2 完整 Maxwell 方程组（真空）

$$\boxed{\begin{aligned}
\text{(i)}\quad & \nabla\cdot\vec{E} = \frac{\rho}{\varepsilon_0} & \text{(Gauss)}\\
\text{(ii)}\quad & \nabla\cdot\vec{B} = 0 & \text{(无磁单极)}\\
\text{(iii)}\quad & \nabla\times\vec{E} = -\frac{\partial\vec{B}}{\partial t} & \text{(Faraday)}\\
\text{(iv)}\quad & \nabla\times\vec{B} = \mu_0\vec{J} + \mu_0\varepsilon_0\frac{\partial\vec{E}}{\partial t} & \text{(Ampère–Maxwell)}
\end{aligned}}$$

四个方程 + Lorentz 力 $\vec{F} = q(\vec{E} + \vec{v}\times\vec{B})$ 构成全部经典电动力学。

> **反直觉**：方程 (iii)(iv) 的两个时间导数项 $-\partial\vec{B}/\partial t$ 和 $\mu_0\varepsilon_0\partial\vec{E}/\partial t$ 互相激发，这正是电磁波存在的数学根源——变化的电场产生磁场，变化的磁场产生电场，自维持传播。

### 3.3 势与规范变换

引入标势 $\phi$ 和矢势 $\vec{A}$：

$$\vec{E} = -\nabla\phi - \frac{\partial\vec{A}}{\partial t}, \qquad \vec{B} = \nabla\times\vec{A}$$

**规范自由度**（gauge freedom）——对任意标量函数 $\chi(\vec{r}, t)$：

$$\vec{A} \to \vec{A} + \nabla\chi, \qquad \phi \to \phi - \frac{\partial\chi}{\partial t}$$

不改变 $\vec{E}, \vec{B}$。常用规范：
- **Coulomb 规范**：$\nabla\cdot\vec{A} = 0$（適合静磁/辐射）。
- **Lorentz 规范**：$\nabla\cdot\vec{A} + \frac{1}{c^2}\frac{\partial\phi}{\partial t} = 0$（Lorentz 协变，QFT 标准选）。

---

## 4. 電磁波（Electromagnetic Waves）

### 4.1 真空中的波动方程

真空中 $\rho = 0, \vec{J} = 0$。对 (iii) 取旋度并用 (iv)：

$$\nabla\times(\nabla\times\vec{E}) = -\frac{\partial}{\partial t}(\nabla\times\vec{B}) = -\mu_0\varepsilon_0\frac{\partial^2\vec{E}}{\partial t^2}$$

用矢量恒等式 $\nabla\times(\nabla\times\vec{E}) = \nabla(\nabla\cdot\vec{E}) - \nabla^2\vec{E} = -\nabla^2\vec{E}$（真空 $\nabla\cdot\vec{E} = 0$）：

$$\boxed{\nabla^2\vec{E} = \mu_0\varepsilon_0\frac{\partial^2\vec{E}}{\partial t^2} = \frac{1}{c^2}\frac{\partial^2\vec{E}}{\partial t^2}}$$

其中**波速** $c = 1/\sqrt{\mu_0\varepsilon_0} \approx 2.998\times10^8$ m/s——恰好是光速！

### 4.2 平面电磁波

单色平面波解：

$$\vec{E}(\vec{r}, t) = \vec{E}_0 e^{i(\vec{k}\cdot\vec{r} - \omega t)}, \qquad \omega = c|\vec{k}|$$

性质（横波条件）：
1. $\vec{k}\cdot\vec{E}_0 = 0$（电场垂直传播方向）。
2. $\vec{B}_0 = \frac{1}{\omega}\vec{k}\times\vec{E}_0$（$\vec{E}, \vec{B}, \vec{k}$ 构成右手系，$|\vec{B}| = |\vec{E}|/c$）。

### 4.3 偏振（Polarization）

$\vec{E}_0$ 的方向定义偏振态。线偏振（$\vec{E}_0$ 沿固定方向）、圆偏振（$\vec{E}_0 = E_0(\hat{x} \pm i\hat{y})/\sqrt{2}$，$\pm$ 对应左/右旋）、椭圆偏振。

### 4.4 能量与 Poynting 矢量

**能流密度**（Poynting vector）：

$$\vec{S} = \frac{1}{\mu_0}\vec{E}\times\vec{B}$$

电磁场能量密度 $u = \frac{1}{2}\varepsilon_0 E^2 + \frac{1}{2\mu_0}B^2$。能量守恒（Poynting 定理）：

$$\frac{\partial u}{\partial t} + \nabla\cdot\vec{S} = -\vec{J}\cdot\vec{E}$$

对平面波，$u_E = u_B$（电能 = 磁能），$\langle S \rangle = \frac{1}{2}c\varepsilon_0 E_0^2$（时间平均）。

### 4.5 介质中的电磁波（折射率）

线性介质中 $\vec{D} = \varepsilon\vec{E}, \vec{B} = \mu\vec{H}$，波速 $v = 1/\sqrt{\varepsilon\mu} = c/n$，**折射率** $n = \sqrt{\varepsilon_r\mu_r}$。这是光学（Snell 定律、Fresnel 公式）的电磁起源。

---

## 5. Python 数值验证

### 5.1 电场线与等势线（点电荷 + 镜像电荷）

```python
# image_charge_field.py —— 点电荷+接地导体板的电场（镜像法可视化）
import numpy as np
k = 8.99e9
q, d = 1e-9, 1.0          # 1nC, 距板 1m
def E(qi, ri, R):
    dr = R - ri
    r = np.linalg.norm(dr, axis=-1, keepdims=True)
    r = np.where(r < 0.05, 0.05, r)
    return k*qi*dr/r**3

x = np.linspace(-2, 2, 50); z = np.linspace(0.01, 3, 40)
X, Z = np.meshgrid(x, z)
R = np.stack([X, np.zeros_like(X), Z], axis=-1)
r_real = np.array([0,0,d]); r_img = np.array([0,0,-d])
Etot = E(q, r_real, R) + E(-q, r_img, R)    # 镜像电荷 -q
# 导体表面(z=0)感应电荷密度 σ = ε0 E_z|_{z=0+}
sigma = -8.854e-12 * Etot[:,:,2].mean(axis=0)
print(f"镜像法: 导体感应总电荷 ≈ {np.trapz(sigma, x)*1:.2e} C (理论 -{q:.1e} C)")
```

### 5.2 螺线管磁场（Ampère 定律验证）

```python
# solenoid_B.py —— 无限长螺线管内部 B=μ0nI，外部≈0
import numpy as np
mu0 = 4*np.pi*1e-7
n, I = 1000, 1.0     # 1000匝/m, 1A
B_inside = mu0*n*I   # 理论值
# 数值积分 Biot-Savart (有限长 20R 的近似无限长)
R, L = 0.05, 1.0     # 半径5cm, 长1m
N_seg = 2000
z_probe = np.array([0.0, 0.5*R, R, 2*R])
phi = np.linspace(0, 2*np.pi, N_seg)
for z in z_probe:
    Bz = 0.0
    for zz in np.linspace(-L/2, L/2, 400):
        rx = R*np.cos(phi); ry = R*np.sin(phi)
        dlx = -R*np.sin(phi)*(2*np.pi/N_seg); 
        dly =  R*np.cos(phi)*(2*np.pi/N_seg)
        dx = 0 - rx; dy = 0 - ry; dzr = z - zz
        r = np.sqrt(dx**2+dy**2+dzr**2)
        # dl × r 的 z 分量
        dBz = mu0/(4*np.pi)*I*n*(L/400)*(dlx*dy - dly*dx)/r**3
        Bz += dBz.sum()
    print(f"z={z/R:.1f}R: B={Bz:.2e} T  (内部理论 {B_inside:.2e} T)")
```

### 5.3 电磁波传播（横波性 + E⊥B⊥k）

```python
# em_wave.py —— 验证平面电磁波 E,B,k 正交且 |B|=|E|/c
import numpy as np
c = 3e8
E0 = np.array([1.0, 0, 0])     # 线偏振沿 x
omega = 2*np.pi*1e9             # 1 GHz
c = 3e8
k  = np.array([0, 0, omega/c])  # 波矢，|k|=ω/c，沿 z 传播
B0 = np.cross(k, E0)/omega      # 理论 B0 = k×E0/ω，故 |B0|=|E0|/c
print(f"E0 = {E0}, B0 = {B0}")
print(f"E·B = {np.dot(E0,B0):.3f} (应=0, 横波)")
print(f"E·k = {np.dot(E0,k):.3f}, B·k = {np.dot(B0,k):.3f} (应=0)")
print(f"|E|/|B| = {np.linalg.norm(E0)/np.linalg.norm(B0):.3e} m/s (应=c)")
# Poynting 方向 = k
S = np.cross(E0, B0)/mu0 if (mu0:=4*np.pi*1e-7) else None
print(f"S ∝ {np.cross(E0,B0)} (应沿 +z, 即 k 方向)")
```

### 5.4 验证 Maxwell 方程推出波速 c = 1/√(μ₀ε₀)

```python
# wave_speed.py —— 从常数算波速，等于光速
import numpy as np
mu0 = 4*np.pi*1e-7
eps0 = 8.854187817e-12
c_calc = 1/np.sqrt(mu0*eps0)
c_exact = 299792458
print(f"c = 1/√(μ₀ε₀) = {c_calc:.1f} m/s")
print(f"光速(精确)   = {c_exact} m/s")
print(f"相对误差     = {abs(c_calc-c_exact)/c_exact:.2e}")
# 这正是 Maxwell 推断"光就是电磁波"的依据
```

---

## 6. 東大特色：物理の数学化

東大電磁気学有一项训练：**把 Maxwell 方程组的四种形式（积分、微分、宏观、微观）并排默写**。这是朝永振一郎时代留下的传统——QED 要求你对 Maxwell 方程组的每一种写法（特别是协变的张量形式 $F^{\mu\nu}$）了如指掌。

電磁気学与東大诺奖的关联：
- **Maxwell 方程 → 狭义相对论**：Einstein 正是被 Maxwell 方程组在伽利略变换下不对称所启发，写出 1905 年的论文《论动体的电动力学》。
- **朝永振一郎（1965 诺贝尔奖）**：QED 重整化——本质是把 Maxwell 方程组量子化后处理紫外发散。
- **Super-Kamiokande（小柴 2002 / 梶田 2015）**：水中切伦科夫辐射是电磁波在介质中相速度 $c/n$ 被 $v > c/n$ 的带电粒子「超车」产生的——纯粹的 Maxwell 介质波问题。

---

## 7. 習題集

**习题 1（★）**　半径 $R$ 的均匀带电球体（总电荷 $Q$），用 Gauss 定律求球内、外电场，并验证边界连续。
> *答案*：球外 $E = Q/(4\pi\varepsilon_0 r^2)$；球内 $E = Qr/(4\pi\varepsilon_0 R^3)$（线性增长）。

**习题 2（★★）**　接地无穷大导体板上方距离 $d$ 处有点电荷 $+q$。用镜像法求（a）电荷受力；（b）导体表面感应电荷密度分布；（c）感应电荷总量。
> *答案*：(a) $F = -q^2/(16\pi\varepsilon_0 d^2)$；(b) $\sigma = -qd/[2\pi(r^2+d^2)^{3/2}]$（$r$ 为到垂足距离）；(c) $-q$。

**习题 3（★）**　无限长螺线管（单位长度 $n$ 匝，电流 $I$）内部磁场 $B$ 是多少？外部呢？用 Ampère 定律推导。
> *答案*：内部 $B = \mu_0 n I$（均匀），外部 $B = 0$（理想）。

**习题 4（★★）**　从 Maxwell 方程组出发，推导真空中 $\vec{E}$ 满足波动方程 $\nabla^2\vec{E} = \mu_0\varepsilon_0\,\partial_t^2\vec{E}$，并证明波速 $c = 1/\sqrt{\mu_0\varepsilon_0}$。这是 Maxwell 推断「光即电磁波」的关键。
> *提示*：取 $\nabla\times$(iii)，代入 (iv)，用 $\nabla\times(\nabla\times) = \nabla(\nabla\cdot) - \nabla^2$。

**习题 5（★）**　一束线偏振电磁波在真空中传播，$E_0 = 100$ V/m。求（a）磁振幅 $B_0$；（b）平均能流密度 $\langle S \rangle$。
> *答案*：(a) $B_0 = E_0/c \approx 3.33\times10^{-7}$ T；(b) $\langle S\rangle = \frac{1}{2}c\varepsilon_0 E_0^2 \approx 13.3$ W/m²。

**习题 6（★★）**　证明在两种线性介质界面，Snell 折射定律 $n_1\sin\theta_1 = n_2\sin\theta_2$ 来自电磁波的边界条件（切向 $k$ 连续）。
> *提示*：相速度匹配要求界面相位 $\vec{k}_\parallel$ 连续。

---

## 8. 参考文献

1. Griffiths, David J. *Introduction to Electrodynamics* 4ed. Cambridge, 2017.（東大指定，日文译本《電磁気学》）
2. Purcell, Morin. *Electricity and Magnetism* 3ed. Cambridge, 2013.（Berkeley Phys Course Vol 2，SI 版）
3. Jackson, John David. *Classical Electrodynamics* 3ed. Wiley, 1999.（研究生标准，東大研究生阶段）
4. Feynman, Leighton, Sands. *The Feynman Lectures on Physics* Vol 2.（电磁学讲得最有物理直觉）
5. 長岡洋介. 『電磁気学 I/II』（裳華房）——東大本土教材，镜像法与边界条件讲得极细。
6.砂川重信. 『電磁気学の考え方』（岩波書店）——物理图像清晰，适合桥梁阅读。

---

**完成日期**：2026-08-12　|　**对应 SURVEY §9 東大**：電磁気学

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：电磁学研究「电荷和电流如何创造电场和磁场，而这些场又如何反过来推电荷」。Maxwell 把四条零散的实验定律缝成一组方程，结果预言了电磁波——而且波速恰好等于光速。光就是电磁波。
>
> **生活类比**：电场像「温度场」——每个点有一个值（场强），电荷像热源，产生场扩散出去；磁场像「水流漩涡」——只有运动的电荷（电流）才能制造。两者通过 Faraday 定律（变磁场生电场）和 Ampère-Maxwell（变电场生磁场）「互相挠背」，结果能脱离电荷自己跑起来——这就是电磁波。
>
> **反直觉发现**：
> - **磁场不做功**：Lorentz 力 $q\vec{v}\times\vec{B}$ 永远垂直于速度，所以磁场对电荷做的功恒为零。磁铁吸引铁块「做功」其实是磁场改变了铁内电子自旋的能量（非磁力直接做功）。
> - **位移电流没有电荷流动**：电容器两板之间是真空，但 Maxwell 硬塞进一个 $\varepsilon_0 \partial\vec{E}/\partial t$，让 Ampère 定律在充电时不矛盾。这个「虚构电流」就是电磁波能在真空中传播的原因。
> - **光速竟然从两个常数算出来**：$c = 1/\sqrt{\mu_0\varepsilon_0} \approx 2.998\times10^8$ m/s。$\mu_0, \varepsilon_0$ 是实验室里测的电学常数，结果它们的组合恰好是光速——Maxwell 那一刻意识到「光」不过是电磁场的涟漪。

---

## 🔗 衔接：从哪来，到哪去

### 前置
- **力学**：矢量、功、能量、Newton 方程、保守力概念（$\nabla\times\vec{F}=0$）。
- **数学**：偏导、梯度/散度/旋度、线面积分（Gauss/Stokes 定理）、复数（交流电路、阻抗）。

### 本课解决了什么危机
- **电与磁的割裂**：1820 年前电（Coulomb）和磁（磁铁）被视为两件事。**Oersted 的针**：电流让磁针偏转 → **Ampère/Biot-Savart** → 最终 **Maxwell** 把它们统一成「电磁场」。
- **Ampère 定律的不自洽**：电容充电时取跨板曲面 $I_{\text{enc}}=0$ 但 $\vec{B}\neq 0$。**位移电流** 是 Maxwell 的天才修补——也催生了电磁波预言。

### 本课留下的新危机（通往下一站）
- **Maxwell 方程在伽利略变换下变形** $\to$ **Einstein 1905**：方程必须协变 → 狭义相对论。$E=mc^2$ 的种子就在这里。
- **电磁波被加热的金属（黑体辐射） disobey Maxwell** $\to$ **Planck 1900 / Einstein 1905**：光量子。量子力学的开端。
- **Maxwell 场量子化** $\to$ **QED**（朝永/Schwinger/Feynman 1965）：电磁场本身是粒子（光子）的集合。東大血脉由此进入粒子物理。

### 后续（東大路径）
| 方向 | 课程 | 用到本课什么 |
|------|------|-------------|
| 狭义相对论 | 力学/相对论 | Maxwell → Lorentz 协变性 |
| 量子光学 | 选修 | 光子、相干态、激光 |
| 等离子体物理 | 核聚变 | Maxwell + 流体方程 → MHD |
| 凝聚态光学 | 物性物理 | 介电常数、折射率、Fresnel |
| 加速器物理 | 素粒子实验 | RF 腔、同步辐射、Cherenkov |

---

## 🏭 理论联系实际：5 个应用

1. **5G/6G 与太赫兹通信**：毫米波阵列天线的设计是纯粹的电磁波辐射 + 相控阵理论。东京大学「電波通信工学」与 NTT/富士通联合推动 300 GHz 频段（2024–2026 6G 试验）。
2. **磁共振成像（MRI）**：超导螺线管产生 1.5–7 T 强磁场（Ampère 定律的极致应用）+ 射频脉冲激发质子（Faraday 感应）+ 梯度线圈定位。整套机器就是 Maxwell 方程的工程化。
3. **Super-Kamiokande 的 Cherenkov 环**：高能中微子在水中产生 $\mu/e$，速度 $v > c/n$，发出蓝色 Cherenkov 辐射。小柴（2002）、梶田（2015）诺奖都建立在这个「介质中电磁波」现象上。
4. **无线充电与电磁感应**：电动汽车、手机 Qi 充电，原理是 Faraday 电磁感应 + 谐振耦合。東京大学 IIS 研究所在动态无线供电公路（2024 试验段）走在前列。
5. **激光与光镊（Optical Tweezers, 2018 诺奖 Ashkin）**：高度聚焦激光的梯度力能夹住细胞、DNA、甚至单个原子。光镊本质是电磁场对偶极子的力（Poynting 矢量 + 偶极近似），现已成为生物物理标配。

---

## 🔬 最新研究前沿（2024-2026）

- **拓扑光子学（Topological Photonics）**：把量子霍尔效应的「边缘态」搬到光波导里——光只沿边缘无损耗传播，不能反向。2024–2025 多个团队（包括東京大学 Group）做出片上拓扑激光器，未来用于鲁棒光通信。
- **超表面（Metasurfaces）与平透镜**：亚波长金属/介质阵列取代厚玻璃透镜，一片 100 nm 厚的膜就能聚焦可见光。2025 年 Meta/Facebook 与 MIT 展示 AR 眼镜用超表面；東大『ナノフォトニクス』方向亦在跟进。
- ** muon g-2 实验（Fermilab 2023/2025）**：μ 子磁矩的测量值与标准模型预言差 $4.2\sigma$——可能指向新物理（暗光子？）。其理论计算需要把 Maxwell + QED 算到 10 级微扰，是电动力学精度的极限。
- **聚变等离子体的 Tokamak 进展（2024–2026）**：ITER（法国）+ JT-60SA（日本茨城，2023 首次放电）+ 民企 CFS（美国）。Maxwell + 磁流体力学（MHD）的工程奇迹——磁约束聚变重新升温。
- **量子电动力学的精确检验**：氢原子 $1S-2S$ 跃迁测量精度达 $10^{-15}$（2024），成为探测「光子是否有质量」「精细结构常数是否随时间变化」的最灵敏探针。

---

## 🗺️ 学习 Roadmap（Tokyo 路径）

```
普通物理 B（电磁学，Halliday 中段）
  ↓ Coulomb、电场电势、直流电路、磁场、电磁感应
電磁気学（2–3 年级，Griffiths）
  ↓ 核心关卡 ↓
  ├─ 静电：Gauss 定律、镜像法、多极展开
  ├─ 静磁：Biot-Savart、Ampère、矢势
  ├─ Maxwell 方程组 + 位移电流 + 边界条件
  ├─ 电磁波：平面波、偏振、Poynting、辐射
  └─ 势 + 规范变换（Coulomb / Lorentz）
研究生进阶
  ├─ Jackson《经典电动力学》（协变形式 F^μν）
  ├─ 等离子体物理 + MHD（核聚变方向）
  ├─ 量子电动力学 QED（朝永遗产）
  └─ 加速器物理 / 同步辐射光源（Spring-8、KEK）
```

**知识检查**：
- [ ] 能默写 Maxwell 方程组的四种形式（积分/微分、真空/介质）并说出每项物理意义。
- [ ] 能用镜像法求解「接地导体板 + 点电荷」，写出感应电荷分布。
- [ ] 能从 Maxwell 方程推出真空波动方程，并解释为什么 $c = 1/\sqrt{\mu_0\varepsilon_0}$。
- [ ] 能解释位移电流为什么是「必须」的（电容充电反例）。
- [ ] 能说出 Cherenkov 辐射条件 $v > c/n$ 并与 Super-K 中微子探测联系起来。
