# 東京大学物理系 Phase 2 · 一般相対論と宇宙論 深度講義

> **课程映射**（SURVEY §9 東大）：一般相対論 + 宇宙論
> **教材**：Carroll, Sean. *Spacetime and Geometry: An Introduction to General Relativity*（相対論指定）+ Dodelson, Scott. *Modern Cosmology* 2ed（宇宙論指定）+ Weinberg *Gravitation and Cosmology* + Ryden *Introduction to Cosmology*
> **定位**：从等效原理到 Einstein 场方程，从黑洞到宇宙微波背景——这是 20 世纪物理学两大支柱之一（GR）的完整呈现。**Kavli IPMU**（東大宇宙物理数学研究所）是连接粒子物理与宇宙学的世界级研究中心，暗物质、暗能量、中微子宇宙学是其核心方向。

---

## 0. 導引：广义相对论为何是「最美的物理理论」

Einstein 在 1915 年写下场方程：

$$G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}$$

左边是时空几何（曲率），右边是物质能量动量。一句话：**物质告诉时空如何弯曲，时空告诉物质如何运动。**

GR 的预言被逐一验证：
1. **水星近日点进动**（1915，立刻验证）。
2. **光线偏折**（1919 Eddington 日食观测）。
3. **引力红移**（Pound–Rebka 1959）。
4. **引力波**（LIGO 2015，双黑洞并合）。
5. **黑洞照片**（Event Horizon Telescope 2019，M87*）。

本章按 **等效原理 → 张量微积分 → Einstein 方程 → 黑洞 → 宇宙学 → 暗物质/暗能量** 展开，每节配 Python 数值验证。

---

## 1. 等效原理と時空の曲がり（Equivalence Principle）

### 1.1 弱等效原理（WEP）

**Galileo/Newton/Eötvös**：惯性质量 $m_I$ 等于引力质量 $m_G$：

$$m_I\,\vec{a} = -\frac{GMm_G}{r^2}\hat{r} \quad \xrightarrow{m_I=m_G} \quad \vec{a} = -\frac{GM}{r^2}\hat{r}$$

所有物体（不论成分/质量）在引力场中加速度相同。实验精度达 $10^{-15}$（MICROSCOPE 卫星 2017）。

### 1.2 Einstein 等效原理（EEP）

Einstein（1907「一生中最快乐的想法」）：在均匀引力场中的物理 $\equiv$ 在加速参考系中的物理。

推论：**局部自由落体参考系 = 局部惯性系**，其中狭义相对论成立。引力效应在局部可消除——引力不是「力」，而是时空弯曲的表现。

### 1.3 强等效原理（SEP）

包括引力自能：引力场自身的能量也参与引力相互作用。这是区分 GR 与其他引力理论的关键。

---

## 2. テンソル計算（Tensor Calculus）

### 2.1 度规张量

时空由度规 $g_{\mu\nu}$ 描述，线元：

$$ds^2 = g_{\mu\nu}\,dx^\mu\,dx^\nu$$

**Minkowski 度规**（平直时空）：$\eta_{\mu\nu} = \text{diag}(-1,+1,+1,+1)$，$ds^2 = -c^2dt^2 + dx^2 + dy^2 + dz^2$。

**Schwarzschild 度规**（球对称质量外）：

$$ds^2 = -\left(1-\frac{2GM}{rc^2}\right)c^2dt^2 + \left(1-\frac{2GM}{rc^2}\right)^{-1}dr^2 + r^2d\Omega^2$$

### 2.2 协变导数

矢量 $V^\mu$ 的协变导数（在弯曲时空中「正确」的导数）：

$$\nabla_\nu V^\mu = \partial_\nu V^\mu + \Gamma^\mu_{\nu\rho}V^\rho$$

$\Gamma^\mu_{\nu\rho}$ 是 **Christoffel 联络**（连接系数），描述坐标基矢量如何沿曲线变化：

$$\Gamma^\mu_{\nu\rho} = \frac{1}{2}g^{\mu\sigma}(\partial_\nu g_{\rho\sigma} + \partial_\rho g_{\nu\sigma} - \partial_\sigma g_{\nu\rho})$$

### 2.3 Riemann 曲率张量

**Riemann 张量**全面描述时空弯曲：

$$R^\mu_{\;\;\nu\rho\sigma} = \partial_\rho\Gamma^\mu_{\nu\sigma} - \partial_\sigma\Gamma^\mu_{\nu\rho} + \Gamma^\mu_{\rho\lambda}\Gamma^\lambda_{\nu\sigma} - \Gamma^\mu_{\sigma\lambda}\Gamma^\lambda_{\nu\rho}$$

缩并得 **Ricci 张量** $R_{\mu\nu} = R^\lambda_{\;\;\mu\lambda\nu}$ 和 **标量曲率** $R = g^{\mu\nu}R_{\mu\nu}$。

> **关键判据**：Riemann 张量全为零 $\Leftrightarrow$ 时空平直（可全局化为 Minkowski）。非零分量 = 弯曲。

### 2.4 测地线方程

自由粒子（仅受引力）走**测地线**（geodesic）——弯曲时空中的「直线」：

$$\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\nu\rho}\frac{dx^\nu}{d\tau}\frac{dx^\rho}{d\tau} = 0$$

$\tau$ 是固有时。这就是 GR 中取代牛顿 $F = ma$ 的运动方程。

---

## 3. Einstein 場方程（Einstein Field Equations）

### 3.1 场方程的推导

Einstein 要求：方程左边（几何）是度规二阶导的线性组合，右边（物质）是能量动量张量 $T_{\mu\nu}$。唯一选择：

$$\boxed{G_{\mu\nu} \equiv R_{\mu\nu} - \frac{1}{2}g_{\mu\nu}R = \frac{8\pi G}{c^4}T_{\mu\nu}}$$

$G_{\mu\nu}$ 称 **Einstein 张量**。

加入**宇宙学常数** $\Lambda$（Einstein 1917，他「最大的错误」，但 1998 年发现暗能量后复活）：

$$G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}$$

### 3.2 能量动量张量

| 源 | $T_{\mu\nu}$ | 物理模型 |
|----|-------------|----------|
| 真空 | $0$ | 真空解（Schwarzschild, Kerr）|
| 宇宙学常数 | $-\frac{\Lambda c^4}{8\pi G}g_{\mu\nu}$ | 暗能量 |
| 完美流体 | $(\rho+p/c^2)u_\mu u_\nu + pg_{\mu\nu}$ | 恒星、宇宙 |
| 电磁 | $\frac{1}{\mu_0}(F_{\mu\alpha}F_\nu^{\;\;\alpha} - \frac{1}{4}g_{\mu\nu}F^2)$ | 带电黑洞 |

### 3.3 Newton 极限

弱场 + 慢运动极限下，Einstein 方程退化为 Newton 引力：

$$\nabla^2\Phi = 4\pi G\rho$$

度规修正 $g_{00} \approx -(1 + 2\Phi/c^2)$。这验证了 GR 在弱场中正确回归 Newton。

---

## 4. ブラックホール（Black Holes）

### 4.1 Schwarzschild 黑洞

球对称真空解，Schwarzschild 半径（视界 event horizon）：

$$r_s = \frac{2GM}{c^2}$$

太阳 $r_{s,\odot} \approx 3$ km（但太阳半径 70 万 km，远未坍缩）；地球 $r_s \approx 9$ mm。

### 4.2 视界与奇点

- $r = r_s$：视界。从外部看，物体接近视界时间冻结（引力红移 $\to\infty$）。从下落者看，正常穿过（等效原理）。
- $r = 0$：奇点。时空曲率发散——物理失效。Penrose–Hawking 奇点定理证明：在合理条件下，奇点不可避免。

### 4.3 Kerr 黑洞（旋转）

旋转黑洞用 Kerr 度规描述，有两个视界（外视界 + 内视界 Cauchy）和一个**能层**（ergosphere）。能层内，所有粒子被迫与黑洞同向旋转——Penrose 过程可从中提取黑洞旋转能。

### 4.4 黑洞热力学（Bekenstein–Hawking）

黑洞有温度和熵：

$$T_H = \frac{\hbar c^3}{8\pi GMk_B}, \qquad S_{BH} = \frac{k_B c^3 A}{4G\hbar}$$

$A$ 是视界面积。Hawking 辐射（量子效应）使黑洞缓慢蒸发——宏观黑洞（$T_H \sim 10^{-7}$ K for $M_\odot$）蒸发极慢。

> **反直觉**：黑洞熵 $S_{BH} \propto A$（面积），而非 $\propto V$（体积）——这是全息原理的起源，暗示三维物理可编码在二维表面上。

---

## 5. 宇宙論（Cosmology）

### 5.1 宇宙学原理与 FRW 度规

宇宙学原理：大尺度上宇宙均匀各向同性。度规为 **Friedmann–Robertson–Walker (FRW)**：

$$ds^2 = -c^2dt^2 + a(t)^2\left[\frac{dr^2}{1-kr^2} + r^2d\Omega^2\right]$$

$a(t)$ 是**尺度因子**，$k = +1, 0, -1$ 对应闭合/平坦/开放宇宙。

### 5.2 Friedmann 方程

将 FRW 度规代入 Einstein 方程，得宇宙膨胀动力学：

$$\boxed{H^2 \equiv \left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}}$$

$$\frac{\ddot{a}}{a} = -\frac{4\pi G}{3}\left(\rho + \frac{3p}{c^2}\right) + \frac{\Lambda c^2}{3}$$

$H = \dot{a}/a$ 是 **Hubble 参数**，当前值 $H_0 \approx 70$ km/s/Mpc（Hubble 常数）。

### 5.3 物质组分与宇宙命运

当前宇宙的密度参数（以临界密度 $\rho_c = 3H_0^2/(8\pi G)$ 为单位）：

| 组分 | $\Omega_i$ | 性质 |
|------|-----------|------|
| 重子物质 | $\Omega_b \approx 0.05$ | 普通物质（恒星、气体）|
| 暗物质 | $\Omega_{\text{DM}} \approx 0.27$ | 不发光，引力效应 |
| 暗能量 | $\Omega_\Lambda \approx 0.68$ | 负压强，加速膨胀 |
| 辐射 | $\Omega_r \approx 5\times10^{-5}$ | CMB + 中微子 |
| **总和** | $\Omega_{\text{tot}} \approx 1.00$ | 平坦宇宙 ($k \approx 0$) |

> **反直觉**：我们熟悉的普通物质只占宇宙的 5%！95% 是完全未知的暗物质和暗能量。这是 21 世纪物理学的最大谜题。

### 5.4 宇宙的热历史：大爆炸

宇宙从极热极密状态膨胀冷却：
- $t \sim 10^{-36}$ s：暴胀（inflation，指数膨胀）。
- $t \sim 10^{-6}$ s：夸克禁闭，质子/中子形成。
- $t \sim 3$ min：大爆炸核合成（BBN），轻元素生成（H, He, Li）。
- $t \sim 380{,}000$ yr：复合（recombination），原子核捕获电子 $\Rightarrow$ 宇宙透明 $\Rightarrow$ **CMB** 释放。
- $t \sim 10^9$ yr：第一代恒星。
- $t \sim 13.8\times10^9$ yr：现在。

### 5.5 CMB 与宇宙学参数

**宇宙微波背景辐射（CMB）**温度 $T_0 = 2.7255$ K，是 $z \approx 1100$ 处的残余光子。Planck 卫星（ESA 2013–2018）精确测量了 CMB 温度涨落 $\Delta T/T \sim 10^{-5}$，提取宇宙学参数：

$$H_0 = 67.4\text{ km/s/Mpc}, \quad \Omega_b h^2 = 0.0224, \quad \Omega_{\text{DM}}h^2 = 0.120,\quad n_s = 0.965$$

CMB 角功率谱的第一个声学峰在 $\ell \approx 220$ $\Rightarrow$ $\Omega_{\text{tot}} = 1.00 \pm 0.02$（平坦宇宙）。

### 5.6 引力波（2015 LIGO 首次探测）

Einstein 1916 预言，2015 年 9 月 14 日 LIGO 首次直接探测到双黑洞并合（GW150914）的引力波信号。波形与 GR 数值模拟完美吻合，直接验证了强场动力学。

> 引力波天文学打开了宇宙的全新窗口——中子星并合的引力波 + 电磁对应体（2017 GW170817）验证了 $r$-过程核合成（金、铂的宇宙起源）。

---

## 6. Python 数值验证

### 6.1 Schwarzschild 测地线（光子偏折与近日点进动）

```python
# schwarzschild_geodesic.py —— Schwarzschild 度规中粒子轨道
import numpy as np
# 轨道方程: d²u/dφ² + u = GM/L² + 3GMu²/c² (u=1/r, GR修正项 = 3GMu²/c²)
# Newton: d²u/dφ² + u = GM/L² (纯 1/r² 力, 闭合椭圆)
# 取弱场参数: GM=1, c=10 → GM/c²=0.01(很小), 半通径 p=20(远大于 GM/c²)
GM, c_val = 1.0, 10.0
p = 20.0  # 半通径 (semi-latus rectum), Newton: GM/L² = 1/p
GM_over_L2 = GM / p**2 * p  # = GM/L² = 1/p = 0.05
def orbit(U0, dU0, phi_max, n=200000):
    phi = np.linspace(0, phi_max, n)
    dphi = phi[1]-phi[0]
    u = np.zeros(n); du = np.zeros(n)
    u[0], du[0] = U0, dU0
    for i in range(1, n):
        # GR: d²u/dφ² = -u + 3GMu²/c² + GM/L²
        ddu = -u[i-1] + 3*GM*u[i-1]**2/c_val**2 + GM_over_L2
        du[i] = du[i-1] + ddu*dphi
        u[i] = u[i-1] + du[i]*dphi
    return phi, u
# 初始条件: 从近日点出发, 偏心率 e=0.3
e = 0.3
u0 = (1 + e) / p  # 近日点 u = (1+e)/p
phi, u = orbit(u0, 0.0, 40*np.pi)  # 20 圈
# 找近日点（r 极小 = u 极大）
peaks = [i for i in range(1, len(u)-1) if u[i]>u[i-1] and u[i]>u[i+1]]
if len(peaks) >= 2:
    dphi_per_orbit = (phi[peaks[1]]-phi[peaks[0]])
    prec_deg = np.degrees(dphi_per_orbit) - 360
    # 解析: 每圈进动 δφ ≈ 6πGM/(c²p)
    prec_theory = np.degrees(6*np.pi*GM/(c_val**2*p))
    print(f"两近日点角间隔: Δφ = {dphi_per_orbit:.4f} rad = {np.degrees(dphi_per_orbit):.4f}°")
    print(f"Newton 预言: 360.000° (闭合椭圆)")
    print(f"GR 进动(数值): {prec_deg:.4f}°/圈")
    print(f"GR 进动(解析): 6πGM/(c²p) = {prec_theory:.4f}°/圈")
    print(f"\n水星实际: 43″/百年 = 0.0119°/圈 ← 太阳 GM/c²≈1.5km, p≈55×10⁶km")
else:
    print(f"轨道未完成两个周期 (找到 {len(peaks)} 个峰值)")
```

### 6.2 Friedmann 方程数值积分（ΛCDM 宇宙演化）

```python
# friedmann_cosmology.py —— ΛCDM 宇宙尺度因子 a(t) 演化
import numpy as np
# H² = H0²(Ωm/a³ + Ωr/a⁴ + Ωk/a² + ΩΛ)
H0 = 67.4  # km/s/Mpc → 转 Gyr⁻¹
H0_Gyr = H0 * 3.24e-20 * 3.156e16  # → /Gyr
Omega_m, Omega_r, Omega_L = 0.315, 9.2e-5, 0.685
Omega_k = 1 - Omega_m - Omega_r - Omega_L  # ≈ 0 (平坦)
def Hubble(a):
    return H0_Gyr * np.sqrt(Omega_m/a**3 + Omega_r/a**4 + Omega_k/a**2 + Omega_L)
# 数值积分 da/dt = a·H(a), 从 a=1 向过去/未来
dt = 0.01  # Gyr
# 过去 (a 减小)
a_past, t_past = [1.0], [0.0]
a = 1.0; t = 0.0
while a > 1e-4:
    da = -a * Hubble(a) * dt
    a += da; t -= dt
    a_past.append(a); t_past.append(t)
# 未来 (a 增大)
a_future, t_future = [1.0], [0.0]
a = 1.0; t = 0.0
while t < 50:
    da = a * Hubble(a) * dt
    a += da; t += dt
    a_future.append(a); t_future.append(t)
print("ΛCDM 宇宙演化 (平坦, Ωm=0.315, ΩΛ=0.685):")
# 宇宙年龄 = -t_past[-1]
t_bigbang = t_past[-1]
print(f"  大爆炸: t = {t_bigbang:.1f} Gyr 前")
print(f"  现在:   a = 1.000, t = 0")
print(f"  50 Gyr 后: a = {a_future[-1]:.2f}")
# 关键时刻
for target_a, label in [(0.5,"半大"),(0.1,"星系形成"),(1e-3,"CMB释放")]:
    idx = np.argmin(np.abs(np.array(a_past)-target_a))
    print(f"  a={target_a:8.1e} ({label}): t = {t_past[idx]:+.1f} Gyr")
# 物质-暗能量相等
a_eq = (Omega_m/Omega_L)**(1/3)
print(f"\n物质-暗能量相等: a = {a_eq:.3f} (约 z = {1/a_eq-1:.2f})")
print(f"  a < {a_eq:.3f}: 物质主导(减速膨胀)")
print(f"  a > {a_eq:.3f}: 暗能量主导(加速膨胀!)")
print(f"\n宇宙命运: 永远加速膨胀 → 大冻结(热寂), 非大坍缩")
```

### 6.3 黑洞 Hawking 温度与寿命

```python
# hawking_radiation.py —— Hawking 温度/熵/蒸发寿命
import numpy as np
hbar, c, G, kB = 1.055e-34, 3e8, 6.674e-11, 1.381e-23
def blackhole(M_kg):
    rs = 2*G*M_kg/c**2           # 视界半径
    A = 4*np.pi*rs**2            # 视界面积
    TH = hbar*c**3/(8*np.pi*G*M_kg*kB)  # Hawking 温度
    S = kB*c**3*A/(4*G*hbar)     # Bekenstein-Hawking 熵
    # 蒸发寿命 ~ 5120π G²M³/(ℏc⁴)
    tau = 5120*np.pi*G**2*M_kg**3/(hbar*c**4)
    return rs, TH, S, tau
print("黑洞 Hawking 辐射参数:")
print(f"{'天体':>10s}  {'M':>12s}  {'rs':>10s}  {'TH(K)':>10s}  {'S/kB':>12s}  {'寿命(yr)':>12s}")
for label, M in [("月球质量", 7.3e22), ("地球", 5.97e24),
                  ("太阳", 1.99e30), ("银河中心", 4e6*1.99e30),
                  ("TON618(最大)", 6.6e10*1.99e30)]:
    rs, TH, S, tau = blackhole(M)
    unit = "m" if rs < 1e4 else "km"
    rs_disp = f"{rs:.1f}{unit}" if unit=="m" else f"{rs/1e3:.0f}{unit}"
    print(f"  {label:>10s}  {M:.2e}kg  {rs_disp:>10s}  {TH:.2e}  {S:.2e}  {tau/3.156e7:.2e}")
print(f"\n反直觉:")
print(f"  太阳质量黑洞 TH≈6×10⁻⁸K << CMB(2.7K) → 吸收>辐射, 暂不蒸发")
print(f"  质量越小→温度越高→蒸发越快(负热容!)")
print(f"  太阳质量黑洞寿命~10⁶⁷年 >> 宇宙年龄(1.4×10¹⁰年)")
```

### 6.4 宇宙距离阶梯（Hubble 定律验证）

```python
# hubble_law.py —— Hubble 定律 v = H₀·d 与距离量级
import numpy as np
H0 = 70  # km/s/Mpc
Mpc = 3.086e22  # 1 Mpc in meters
print("Hubble 定律 v = H₀·d (H₀=70 km/s/Mpc):")
print(f"{'天体':>14s}  {'d(Mpc)':>10s}  {'v(km/s)':>10s}  {'红移z':>8s}")
objects = [("仙女座星系", 0.78), ("室女团", 16.5), ("后发团", 100),
           ("CMB '壳层'", 14000)]
for name, d in objects:
    v = H0 * d
    z = v / 3e5  # 非相对论红移
    print(f"  {name:>14s}  {d:10.1f}  {v:10.0f}  {z:8.4f}")
print(f"\n反直觉:")
print(f"  H₀ 的单位 km/s/Mpc 本身就是'速度/距离'")
print(f"  1/H₀ = {1/H0*3.086e19/3.156e16:.1f} Gyr ≈ Hubble 时间(宇宙年龄上界)")
print(f"  c/H₀ = {3e5/H0:.0f} Mpc ≈ Hubble 半径(可观测宇宙尺度)")
print(f"\n暗能量(ΩΛ=0.68)使膨胀加速:")
print(f"  远处超新星比 v=H₀d 预言更暗 → 1998年发现加速膨胀(Perlmutter/Schmidt/Riess 2011诺奖)")
```

---

## 7. 東大特色：Kavli IPMU と宇宙物理の最前線

### 7.1 Kavli IPMU（宇宙物理数学研究所）

2007 年成立的 **Kavli IPMU**（Institute for the Physics and Mathematics of the Universe）是東大直属的世界级研究所，聚焦五大问题：

1. **暗物质**是什么？（占宇宙 27%，但完全未知）。
2. **暗能量**是什么？（占 68%，导致加速膨胀）。
3. **中微子质量**的起源？（Kajita 中微子振荡的宇宙学意义）。
4. **宇宙如何开始**？（暴胀理论、原初引力波）。
5. **基本粒子和宇宙如何统一**？（弦理论、额外维）。

IPMU 的特色是**跨学科融合**——粒子物理学家、天文学家、数学家（弦论/拓扑）在同一栋楼工作，是東大「大科学」传统的延续。

### 7.2 東大与宇宙学实验

- **Subaru 望远镜**（夏威夷，8.2m）：東大国立天文台运营，暗能量巡天、系外行星探测。
- **Hyper-Kamiokande**（建设中）：CP 对称破缺测量、质子衰变探测。
- **LiteBIRD 卫星**（JAXA 计划）：原初引力波探测（暴胀验证）。

### 7.3 理论物理的东大传承

GR 和宇宙论在東大有深厚的理论传统：

- **佐藤勝彦**（Sato, 東大）：暴胀宇宙学的早期贡献者（1980 年代）。
- **村山斉**（Murayama, IPMU 首任所长）：粒子物理唯象学，暗物质模型。
- 東大理论组在弦唯象、额外维模型、引力波物理方面持续产出。

---

## 8. 習題集（Exercises）

> 标 ★ 为東大风格，★★ 为研究生级。

**习题 1（★）**　计算太阳和地球的 Schwarzschild 半径 $r_s$。若太阳压缩到 $r_{s,\odot}$ 以内，它会变成黑洞吗？
> *答案*：$r_{s,\odot} = 2GM_\odot/c^2 \approx 2.95$ km，$r_{s,\oplus} \approx 8.9$ mm。是——任何质量压缩到其 $r_s$ 以内即成黑洞。

**习题 2（★★）**　推导引力红移公式：从 Schwarzschild 度规出发，证明半径 $r$ 处发射的光子在无穷远处频率变为 $\nu_\infty = \nu_0\sqrt{1 - r_s/r}$。计算地球表面到无穷远的红移 $z$。
> *答案*：$z \approx GM_\oplus/(R_\oplus c^2) \approx 7\times10^{-10}$（极小，但 Pound–Rebka 实验测到了）。

**习题 3（★）**　Hubble 常数 $H_0 = 70$ km/s/Mpc。估算宇宙年龄（假设匀速膨胀 $t_0 = 1/H_0$），与精确 ΛCDM 值 13.8 Gyr 比较。
> *答案*：$t_0 = 1/H_0 \approx 14.0$ Gyr，与 13.8 Gyr 接近（巧合，因为 $\Omega_m$ 和 $\Omega_\Lambda$ 接近相等）。

**习题 4（★★）**　一个太阳质量黑洞的 Hawking 温度是多少？CMB 温度 2.725 K 高于它意味着什么？
> *答案*：$T_H \approx 6.2\times10^{-8}$ K $\ll T_{\text{CMB}}$。黑洞从 CMB 吸收的辐射多于 Hawking 辐射 $\Rightarrow$ 暂时不会蒸发（直到宇宙膨胀使 $T_{\text{CMB}} < T_H$，需 $10^{20}$ 年）。

**习题 5（★）**　宇宙的能量密度组分 $\Omega_m = 0.315, \Omega_\Lambda = 0.685$。在物质主导期 ($a < a_{\text{eq}}$) 和暗能量主导期 ($a > a_{\text{eq}}$)，尺度因子 $a(t)$ 各如何演化？
> *答案*：物质主导 $a \propto t^{2/3}$（减速）；暗能量主导 $a \propto e^{Ht}$（指数加速）。转变点 $a_{\text{eq}} = (\Omega_m/\Omega_\Lambda)^{1/3} \approx 0.77$（$z \approx 0.30$）。

**习题 6（★★）**　GW150914（LIGO 首次探测）是两个质量约 30 $M_\odot$ 的黑洞并合。峰值引力波频率约 250 Hz。估算并合时两个黑洞的间距（用 Kepler 第三定律 + $r_s$）。
> *答案*：$f = \frac{1}{2\pi}\sqrt{\frac{GM_{\text{tot}}}{r^3}} \Rightarrow r \approx \left(\frac{GM}{\pi^2 f^2}\right)^{1/3} \approx 350$ km $\approx 6 r_s$——正好在视界接触前。

---

## 9. 参考文献

1. Carroll, Sean. *Spacetime and Geometry: An Introduction to General Relativity*. Cambridge, 2019.（東大相対論指定，现代标准）
2. Dodelson, Scott; Schmidt, Fabian. *Modern Cosmology* 2ed. Academic Press, 2020.（東大宇宙論指定）
3. Weinberg, Steven. *Gravitation and Cosmology*. Wiley, 1972.（经典权威，严格）
4. Ryden, Barbara. *Introduction to Cosmology* 2ed. Cambridge, 2017.（本科入门）
5. Misner, Thorne, Wheeler. *Gravitation*. Freeman, 1973.（MTW，GR 圣经）
6. Poisson, Eric. *A Relativist's Toolkit*. Cambridge, 2004.（实用技术手册）
7. 佐藤文隆・郷田直輝. 『一般相対論』（岩波書店）——東大本土教材。
8. 村山斉. 『宇宙は何でできているのか』（講談社）——IPMU 所长通俗著作。

---

**完成日期**：2026-08-12　|　**对应 SURVEY §9 東大**：一般相対論 + 宇宙論　|　**特色收束**：Kavli IPMU + 暗物质/暗能量 + Subaru 望远镜 + Hyper-Kamiokande

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：广义相对论（GR）告诉你「时空不是舞台，而是演员」——物质告诉时空怎么弯曲，弯曲的时空告诉物质怎么运动。宇宙论则用这个理论+大量观测，告诉你宇宙从大爆炸到现在的故事：138 亿年前从一个奇点膨胀，现在 68% 是暗能量、27% 是暗物质、只有 5% 是我们熟悉的「东西」。
>
> **生活类比**：经典物理把时空当成一块固定的桌布，物体在桌上移动；GR 把时空当成一张橡胶蹦床——你（质量）站上去，蹦床就凹下去，旁边滚过的小球（光、行星）会沿着凹陷的曲面走。看起来像「引力」，其实是没有引力，只有时空弯曲。Wheeler 名言：「时空告诉物质如何运动，物质告诉时空如何弯曲。」
>
> **反直觉发现**：
> - **引力会让时间变慢**：在黑洞附近或地球表面（vs 卫星），时钟走得慢一些。GPS 必须修正这个效应，否则定位每天漂移 10 公里。Pound-Rebka 1959 用 22 米高的塔测到了。
> - **黑洞会蒸发（Hawking 1974）**：黑洞不只是「只进不出」——它有温度 $T_H = \hbar c^3/(8\pi G M k_B)$，会以黑体辐射形式蒸发。太阳质量黑洞的 $T_H \sim 10^{-8}$ K，比宇宙微波背景（2.7 K）冷得多，目前反而吸热，但 $10^{67}$ 年后会爆炸。
> - **宇宙在加速膨胀（1998）**：观测遥远 Ia 超新星比预期暗 → 它们在加速远离。Perlmutter/Schmidt/Riess 2011 诺奖。「暗能量」是什么？没人知道——但占宇宙 68%。
> - **引力波真的存在（2015 LIGO）**：两个 30 太阳质量黑洞并合，把 3 个太阳质量转化为引力波能量，在 13 亿光年外让地球上的激光臂摆动了 $10^{-18}$ 米（比原子核小 1000 倍）——人类「听」到了时空的涟漪。

---

## 🔗 衔接：从哪来，到哪去

### 前置
- **狭义相对论**：Lorentz 变换、四维矢量、$E = mc^2$、时空间隔不变量。
- **力学**：拉格朗日/哈密顿（变分原理 → Einstein-Hilbert 作用量）、张量。
- **数学**：微分几何（流形、度规、曲率张量、联络）、PDE。

### 本课解决了什么危机
- **Newton 引力瞬时超距**：Newton 万有引力「瞬间」传递，违反狭义相对论（信息不能超光速）。**Einstein 1915**：把引力几何化为时空曲率，扰动以光速传播（引力波）。
- **水星近日点进动异常**：Newton 预言每百年 5557 角秒，实测 5557 + 43 角秒。这多出的 43 角秒，Einstein GR 算出来时他「心脏差点停跳」——这是 GR 第一个实验验证。
- **宇宙膨胀的发现**：1929 Hubble 发现星系退行速度与距离成正比。但「膨胀」是怎么开始的？**Gamow 大爆炸（1948）** 预言宇宙微波背景（CMB）→ 1965 Penzias-Wilson 偶然发现 2.7 K 黑体辐射，大爆炸模型确立。

### 本课留下的新危机（通往下一站）
- **量子引力**：Einstein 方程在奇点（黑洞中心、宇宙诞生）失效。量子化引力不可重整化——需要弦理论 / 圈量子引力 / AdS-CFT。物理学的最大悬案。
- **暗物质 + 暗能量本质**：占宇宙 95% 但完全未知。候选：WIMP、axion、PBH；暗能量可能是宇宙学常数、quintessence，或修改引力。
- **暴胀（inflation）的验证**：宇宙诞生后 $10^{-36}$ 秒内指数膨胀，解释平坦性、视界问题。原初引力波（CMB B 模偏振）是关键证据——LiteBIRD 任务的目标。

### 后续（東大路径）
| 方向 | 课程 | 用到本课什么 |
|------|------|-------------|
| 弦理论 | 数学物理 | AdS/CFT、量子引力 |
| 宇宙学观测 | 实测天文 | Subaru/PFS、LiteBIRD、DESI |
| 粒子宇宙学 | 交叉 | 暗物质、leptogenesis、原初黑洞 |
| 相对论天体物理 | 专题 | 黑洞物理、引力波、中子星 |
| 量子信息与引力 | 前沿 | ER=EPR、黑洞信息悖论 |

---

## 🏭 理论联系实际：5 个应用

1. **GPS 卫星导航**：卫星速度 4 km/s（狭义相对论：每天慢 7 μs）+ 距地心远（广义相对论：每天快 45 μs），净效应每天快 38 μs。不修正，定位 1 分钟漂移 10 公里。GR 在你口袋里。
2. **引力波天文学（LIGO/Virgo/KAGRA）**：2015 首次探测（GW150914），开启「多信使天文学」。2017 双中子星并合 GW170817 同时看到 γ 暴和光学对应体，证实金、铂等重元素来自中子星碰撞。日本 KAGRA（神岡，2019 调试，2024 加入 O4 观测）。
3. **事件视界望远镜（EHT）**：2019 首张黑洞照片（M87*）；2022 银河系中心人马座 A*。直接「看到」了广义相对论预言的黑洞阴影——验证 GR 在极端引力下的精度。日本国立天文台是 EHT 成员。
4. **Subaru 望远镜 + PFS 巡天**：東大国立天文台运营的 8.2 米 Subaru（夏威夷）正在部署 Prime Focus Spectrograph（PFS），将测量 2400 个星系的红移分布，绘制暗物质大尺度结构，精确测量暗能量演化。2025–2030 巡天。
5. **暗物质直接探测**：XENONnT（意大利）、LZ（美国）、PandaX（中国）用液氙探测 WIMP 与原子核的反冲。東京大学宇宙線研究所（ICRR）的 XMASS、Kavli IPMU 的轴子探测方向持续投入。

---

## 🔬 最新研究前沿（2024-2026）

- **LiteBIRD 通过「任务定义评审 #2」（2026 年 8 月）**：JAXA 主导的下一代 CMB 偏振卫星 LiteBIRD 通过 MDR2 评审，进入 Phase A 准备阶段。**核心目标**：探测原初引力波在 CMB 留下的 B 模偏振——直接验证暴胀理论。Kavli IPMU 的松村知岳（Tomotake Matsumura）是项目 PI，IPMU 牵头 Science Ground Segment 数据分析管线。预计 2030s 发射。
- **Subaru/PFS 巡天（2025 启动）**：Prime Focus Spectrograph（ʻŌnohiʻula，2026 年 6 月 Kavli IPMU 公开通报已上线运行）将观测 2400 星系的红移空间分布，精确测量暗能量状态方程 $w(a)$、检验 ΛCDM。Subaru Hyper Supreme-Cam 已发现 2022 年最远星系候选（z > 13）。
- **JWST 早期宇宙发现（2024–2026）**：JWST（2021 发射，2022 科学运行）发现 z > 10 的成熟大质量星系——出乎 ΛCDM + 慢坍缩模型预期。可能暗示早期恒星形成效率高、或有原初黑洞辅助、或需修改宇宙学模型。Subaru 配合地面光学光谱验证。
- **DESI 暗能量结果争议（2024–2026）**：DESI（Dark Energy Spectroscopic Instrument）2024 年初公布的 BAО 数据轻微偏好「暗能量随时间演化」（$w_0w_a$ CDM 模型，$w_0 = -0.5, w_a = -1.3$），但显著性只有 2.5–4σ。Kavli IPMU 2026 年 8 月的研讨会上有专题「Possible interpretation of DESI BAO result」——暗能量是否动力学？这是宇宙学最大的悬念。
- **原初黑洞（PBH）作为暗物质候选（2025–2026）**：Kavli IPMU 的 Shing-Chi Leung、Ken'ichi Nomoto、Alexander Kusenko 团队 2025–2026 连续在 ApJ 发表系列工作，发现 PBH 穿过白矮星可触发 Ia 超新星，其化学丰度（Ni-56, Mn 等）与银河系观测相符——首次为 PBH 暗物质模型提供间接证据。

---

## 🗺️ 学习 Roadmap（Tokyo 路径）

```
狭义相对论（力学/普物 C）
  ↓ Lorentz 变换、四维矢量、E²=(pc)²+(mc²)²
一般相対論（4 年级/研究生， Carroll）
  ↓ 核心关卡 ↓
  ├─ 等效原理 + 时空曲率（Riemann 张量）
  ├─ Einstein 场方程 $G_{\mu\nu} = 8\pi G T_{\mu\nu}/c^4$
  ├─ Schwarzschild 解（黑洞、近日点进动、光线偏折）
  ├─ 引力波 + 弱场极限
  └─ 黑洞热力学（Hawking 辐射、Bekenstein 熵）
宇宙論（研究生， Dodelson）
  ↓ FRW 度规 + ΛCDM 模型
  ├─ 大爆炸核合成（BBN）+ CMB
  ├─ 暗物质 + 暗能量 + 暴胀
  └─ 结构形成（功率谱、BAO）
研究生进阶
  ├─ 弦理论 + AdS/CFT（量子引力）
  ├─ 引力波物理（KAGRA/LIGO 数据分析）
  ├─ 实测宇宙学（Subaru、LiteBIRD、DESI）
  └─ 量子信息与时空（ER=EPR、It from Qubit）
```

**知识检查**：
- [ ] 能说出等效原理（弱/强）并解释为什么它把引力「几何化」。
- [ ] 能写出 Schwarzschild 度规，并算出 Schwarzschild 半径 $r_s = 2GM/c^2$（太阳 ~3 km）。
- [ ] 能用 Hubble 定律 $v = H_0 d$ 算出宇宙年龄上界 $1/H_0 \approx 14$ Gyr，与精确 ΛCDM 值 13.8 Gyr 对比。
- [ ] 能解释「为什么 1998 年超新星观测暗示宇宙加速膨胀」（远处超新星比预期暗）。
- [ ] 能说出黑洞熵 $S_{BH} = k_B c^3 A/(4G\hbar)$ 与面积成正比（而非体积）暗示的「全息原理」。
- [ ] 能解释 LiteBIRD 探测 CMB B 模偏振为什么是验证暴胀理论的关键。
- [ ] 知道 2026 年 Super-Kamiokande 公布的 DSNB 首次迹象（2.6σ, 99.5% CL）依赖钆掺杂技术，及其对宇宙恒星形成史的启示。
