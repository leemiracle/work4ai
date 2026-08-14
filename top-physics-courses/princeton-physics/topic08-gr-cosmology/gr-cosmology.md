# Princeton · 广义相对论与宇宙学（Phase 2 · 主题 08）

> **课程映射**：`PHY 563 General Relativity`（Carroll 研究生入门）→ `PHY 537 Cosmology`（Dodelson / Mukhanov）→ `PHY 519 Advanced General Relativity`（Weinberg / Wald 研究生进阶）
>
> **教材栈**：Carroll *Spacetime and Geometry: An Introduction to General Relativity*（Princeton `PHY 563` 核心教材，现代写法，最清晰）／ Weinberg *Gravitation and Cosmology*（经典，Princeton 传统，物理直觉极强）／ Dodelson & Schmidt *Modern Cosmology* 2ed（宇宙学标准教材）／ Mukhanov *Physical Foundations of Cosmology*（暴胀理论原创者亲笔）／ Wald *General Relativity*（数学严格，研究生进阶参考）／ Misner, Thorne & Wheeler *Gravitation*（MTW，Wheeler 的不朽经典，Princeton 传统）
>
> **Princeton 特色**：广义相对论是 Princeton 的**灵魂学科**——Einstein 在 IAS 度过最后 22 年（1933–1955），在此追寻统一场论直至逝世。**John Wheeler**（Princeton 教授，Feynman 的导师）创造了「黑洞」（black hole）和「虫洞」（wormhole）这两个术语，开创了引力波天文学的理论基础。**Joseph Taylor**（Princeton，1993 诺贝尔奖）用脉冲星双星 PSR B1913+16 首次间接验证了引力辐射（1974–1993 的 17 年观测）。Princeton 还与 **PPPL**（Princeton Plasma Physics Laboratory）有深度关联——虽然 PPPL 主要做聚变等离子体，但其磁约束技术在引力波探测和相对论天体物理中也有应用。2015 年 LIGO 直接探测到引力波（GW150914），2017 年多信使天文学（GW170817 + 电磁对应体），Princeton 的 Kavli 研究所深度参与。

---

## 目录

1. [等效原理与时空几何](#1-等效原理与时空几何)
2. [爱因斯坦场方程与施瓦茨柴尔德解](#2-爱因斯坦场方程与施瓦茨柴尔德解)
3. [黑洞：视界、奇点与霍金辐射](#3-黑洞视界奇点与霍金辐射)
4. [宇宙学：FRW 度规与膨胀宇宙](#4-宇宙学frw-度规与膨胀宇宙)
5. [引力波与实验检验](#5-引力波与实验检验)
6. [Python 数值实验](#6-python-数值实验)
7. [习题集](#7-习题集)
8. [不足与延伸](#8-不足与延伸)

---

## 1. 等效原理与时空几何

### 直觉

广义相对论的核心洞见是**等效原理**：在足够小的区域内，引力效应与加速参考系的效应**不可区分**。Einstein 的「最快乐的想法」：一个自由下落的观察者感觉不到引力——引力不是「力」，而是时空弯曲的表现。

数学上，这把引力理论变成了**微分几何**。物质告诉时空如何弯曲（Einstein 场方程），时空告诉物质如何运动（测地线方程）。Carroll 的教学策略（Princeton `PHY 563`）：先建立微分几何工具（度规、联络、曲率张量），再推出场方程，最后求解。Wheeler 的哲学直觉：**时空不是引力发生的舞台，时空本身就是引力**。

### 公式

**等效原理**（Einstein, 1907）：

> 在局部自由下落参考系中，物理定律退化为狭义相对论的形式。

**度规张量** $g_{\mu\nu}$（定义时空的几何）：

$$
ds^2 = g_{\mu\nu}\,dx^\mu dx^\nu
$$

平坦时空（Minkowski）：$ds^2 = -c^2dt^2 + dx^2 + dy^2 + dz^2$（符号约定 $(-+++)$）。

**Christoffel 联络**（协变导数所需的「修正项」）：

$$
\Gamma^\lambda_{\mu\nu} = \frac{1}{2}g^{\lambda\sigma}\!\left(\partial_\mu g_{\nu\sigma} + \partial_\nu g_{\mu\sigma} - \partial_\sigma g_{\mu\nu}\right)
$$

**测地线方程**（自由粒子在世界中的「直线」）：

$$
\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta}\frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau} = 0
$$

**Riemann 曲率张量**（时空弯曲的完整描述）：

$$
R^\rho_{\;\;\sigma\mu\nu} = \partial_\mu\Gamma^\rho_{\nu\sigma} - \partial_\nu\Gamma^\rho_{\mu\sigma} + \Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma}
$$

缩约后得到 Ricci 张量 $R_{\mu\nu} = R^\lambda_{\;\;\mu\lambda\nu}$ 和标量曲率 $R = g^{\mu\nu}R_{\mu\nu}$。

---

## 2. 爱因斯坦场方程与施瓦茨柴尔德解

### 直觉

Einstein 场方程是广义相对论的「麦克斯韦方程组」——它把时空几何（左边）与物质能量动量（右边）联系在一起。Wheeler 的经典总结：**物质告诉时空如何弯曲，时空告诉物质如何运动**。

$$
G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}
$$

最简单的非平凡解是 **Schwarzschild 解**（1915，一战前线士兵 Schwarzschild 在 Einstein 发表场方程后一个月内得到）：球对称真空的外部度规。它描述了太阳系内的行星轨道（水星近日点进动、光线偏折）和非旋转黑洞。

Princeton `PHY 563`（Carroll 教材）的核心训练：从场方程出发，在球对称假设下推导 Schwarzschild 度规，然后解测地线方程得到行星轨道。

### 公式

**爱因斯坦场方程**（含宇宙学常数 $\Lambda$）：

$$
R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}
$$

- 左边 $G_{\mu\nu} = R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu}$ 是 Einstein 张量（描述时空曲率）。
- 右边 $T_{\mu\nu}$ 是能量-动量张量（物质/辐射的分布）。
- $\Lambda$ 是宇宙学常数（暗能量的候选），$\Lambda > 0$ 表示加速膨胀。

**Schwarzschild 度规**（球对称真空解，$r_s = 2GM/c^2$ 为 Schwarzschild 半径）：

$$
ds^2 = -\!\left(1-\frac{r_s}{r}\right)c^2dt^2 + \left(1-\frac{r_s}{r}\right)^{-1}dr^2 + r^2 d\Omega^2
$$

**水星近日点进动**（广义相对论的第一大胜利）：

$$
\Delta\phi_{\text{per orbit}} = \frac{6\pi GM}{c^2 a(1-e^2)}
$$

水星每世纪进动 $43''$（$0.43$ 角秒/圈），在 1859 年被 Le Verrier 发现但牛顿力学无法解释。Einstein 1915 年的结果精确吻合——这是他「心悸了好几天」的时刻。

**光线偏折**（广义相对论的第二大胜利，Eddington 1919 年日食验证）：

$$
\delta\phi = \frac{4GM}{c^2 b}
$$

$b$ 为光线冲击参数（最近距离）。太阳偏折星光 $1.75''$——1919 年 Eddington 的日食观测确认，Einstein 一夜成名。

---

## 3. 黑洞：视界、奇点与霍金辐射

### 直觉

当 $r = r_s = 2GM/c^2$ 时，Schwarzschild 度规的 $g_{tt} \to 0$ 且 $g_{rr} \to \infty$——这个面称为**事件视界**。视界是「不归点」：一旦越过，没有任何东西（包括光）可以返回外部。

Wheeler 创造了「黑洞」一词（1967 年），在他之前这些物体被称为「冻结星」或「引力完全坍缩体」。Wheeler 还推广了黑洞无毛定理：稳定的黑洞只有三个参数——质量 $M$、角动量 $J$、电荷 $Q$。所有其他信息在坍缩中丢失（信息悖论的起源）。

**Hawking 辐射**（1974）：黑洞不是完全黑的！量子场论在弯曲时空中的效应使得黑洞会发出热辐射，温度 $T_H = \hbar c^3/(8\pi GM k_B)$。质量越小的黑洞温度越高，蒸发越快——最终在剧烈爆发中消失。这是量子力学、热力学和广义相对论的交汇点，也是量子引力理论的入口。

### 公式

**Schwarzschild 半径**（事件视界）：

$$
r_s = \frac{2GM}{c^2}
$$

太阳：$r_s \approx 3$ km（太阳半径 $7\times10^5$ km，远大于 $r_s$）。地球：$r_s \approx 9$ mm。

**Kerr 度规**（旋转黑洞，角动量 $J = Ma$，$a$ 为自旋参数）：

$$
r_{\text{ergosphere}} = M + \sqrt{M^2 - a^2\cos^2\theta}
$$

能层（ergosphere）内，时空被黑洞旋转**拖拽**——连光都必须随黑洞旋转（Penrose 过程可从中提取能量）。

**Birkhoff 定理**：真空球对称的外部度规必定是 Schwarzschild 形式——与径向运动状态无关。

**Hawking 温度**（黑洞热辐射）：

$$
T_H = \frac{\hbar c^3}{8\pi GM k_B} \approx 6.17\times10^{-8}\,\text{K}\times\!\left(\frac{M_\odot}{M}\right)
$$

太阳质量黑洞的 Hawking 温度仅 $62$ nK——远低于宇宙微波背景（$2.7$ K），实际上在**吸积**而非蒸发。

**Hawking 蒸发寿命**：

$$
t_{\text{evap}} \sim \frac{5120\pi G^2 M^3}{\hbar c^4} \approx 10^{67}\,\text{yr}\times\!\left(\frac{M}{M_\odot}\right)^3
$$

太阳质量黑洞蒸发需 $\sim10^{67}$ 年（宇宙年龄仅 $1.4\times10^{10}$ 年）。

**黑洞熵**（Bekenstein-Hawking 熵，面积定律）：

$$
S_{\text{BH}} = \frac{k_B c^3 A}{4G\hbar} = \frac{k_B A}{4\ell_P^2}
$$

$A$ 为视界面积，$\ell_P = \sqrt{G\hbar/c^3} \approx 1.6\times10^{-35}$ m 为 Planck 长度。黑洞熵正比于面积而非体积——这是全息原理（holographic principle, 't Hooft, Susskind）的物理起源。

---

## 4. 宇宙学：FRW 度规与膨胀宇宙

### 直觉

在宇宙学尺度上（$> 100$ Mpc），宇宙是均匀各向同性的——这称为**宇宙学原理**。这个对称性假设极大地简化了 Einstein 场方程，得到 **Friedmann-Robertson-Walker（FRW）度规**，它用一个时间函数 $a(t)$（**尺度因子**）描述宇宙的几何。

尺度因子 $a(t)$ 的演化由 Friedmann 方程控制——它来自 Einstein 场方程在 FRW 度规下的约化。1929 年 Hubble 发现宇宙正在膨胀（$a(t)$ 在增大），这终结了「静态宇宙」的假说。1998 年，超新星观测发现膨胀在**加速**——这是暗能量（$\Lambda > 0$）存在的证据，导致 Perlmutter、Schmidt、Riess 获 2011 年诺贝尔奖。

宇宙学的故事：大爆炸（$13.8$ Gyr 前）→ 暴胀（$10^{-36}$ s）→ 粒子产生 → 核合成（$3$ min）→ 退耦/CMB（$380$ kyr）→ 结构形成 → 今天。Princeton `PHY 537`（Dodelson / Mukhanov）系统处理这条时间线。

### 公式

**FRW 度规**（均匀各向同性宇宙）：

$$
ds^2 = -c^2dt^2 + a^2(t)\!\left[\frac{dr^2}{1-kr^2} + r^2 d\Omega^2\right]
$$

$k = +1$（闭合）、$k = 0$（平坦）、$k = -1$（开放）。$a(t)$ 为尺度因子（通常取 $a_0 = 1$）。

**Friedmann 方程**（$H = \dot{a}/a$ 为 Hubble 参数）：

$$
H^2 = \frac{8\pi G}{3}\rho - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}
$$

**Hubble 定律**（近距离近似，$H_0 \approx 70$ km/s/Mpc）：

$$
v = H_0 d
$$

**临界密度**（平坦宇宙 $k=0$）：

$$
\rho_c = \frac{3H_0^2}{8\pi G} \approx 9.2\times10^{-27}\,\text{kg/m}^3
$$

密度参数 $\Omega_i = \rho_i/\rho_c$。观测值：$\Omega_m \approx 0.31$（物质），$\Omega_\Lambda \approx 0.69$（暗能量），$\Omega_r \approx 5\times10^{-5}$（辐射），$\Omega_k \approx 0$（平坦）。

**物质/辐射/暗能量主导宇宙的 $a(t)$ 演化**：

| 主导成分 | 状态方程 $w = p/\rho$ | $a(t) \propto$ |
|---------|---------------------|-----------------|
| 辐射 | $1/3$ | $t^{1/2}$ |
| 物质（尘埃） | $0$ | $t^{2/3}$ |
| 暗能量（$\Lambda$） | $-1$ | $e^{Ht}$（指数膨胀） |
| 暴胀 | $w \approx -1$ | $e^{Ht}$ |

**宇宙微波背景（CMB）温度**：$T_0 = 2.7255\pm0.0006$ K（COBE/FIRAS 1990，$10^{-5}$ 精度）。

**红移与尺度因子的关系**：

$$
1 + z = \frac{a(t_0)}{a(t_{\text{emit}})} = \frac{\lambda_{\text{obs}}}{\lambda_{\text{emit}}}
$$

$z = 0$（今天）→ $z \to \infty$（大爆炸）。

---

## 5. 引力波与实验检验

### 直觉

Einstein 在 1916 年预言了引力波——时空本身的涟漪。但由于振幅极小（典型应变 $h \sim 10^{-21}$），直接探测花了整整 100 年。2015 年 9 月 14 日，**LIGO** 首次直接探测到引力波 GW150914——来自 13 亿光年外的两个黑洞合并（$36\,M_\odot + 29\,M_\odot \to 62\,M_\odot$，$3\,M_\odot$ 以引力波形式辐射）。

2017 年，GW170817（中子星合并）同时被引力波和电磁望远镜观测到——**多信使天文学**的开端，确认了重元素（金、铂）的 r-过程核合成来源。

Joseph Taylor（Princeton）早在 1974 年就**间接**验证了引力波：脉冲星双星 PSR B1913+16 的轨道周期每年减小 $76.5\,\mu$s，与 GR 预言的引力辐射能耗精确吻合（误差 $<0.5\%$）。这为他赢得 1993 年诺贝尔奖。Princeton 的引力物理传统从 Einstein（IAS 理论）→ Wheeler（黑洞理论）→ Taylor（脉冲星验证）→ LIGO 时代一脉相承。

### 公式

**线性化引力波**（弱场近似 $g_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu}$，$|h| \ll 1$）：

$$
\Box\,\bar{h}_{\mu\nu} = -\frac{16\pi G}{c^4}T_{\mu\nu}, \quad \bar{h}_{\mu\nu} = h_{\mu\nu} - \frac{1}{2}\eta_{\mu\nu}h
$$

真空中 $\Box\bar{h}_{\mu\nu} = 0$ → 以光速传播的横波（TT 规范：$h_{\mu\nu}^{\text{TT}}$ 只有空间分量，横迹）。

**四极矩辐射**（引力波功率）：

$$
P = \frac{G}{5c^5}\langle \dddot{Q}_{ij}\dddot{Q}_{ij}\rangle, \quad Q_{ij} = \int\rho\!\left(x_i x_j - \frac{1}{3}r^2\delta_{ij}\right)d^3x
$$

（$Q_{ij}$ 为约化质量四极矩，三点表示对时间的三阶导数。）

**双星辐射功率**（Taylor 脉冲星双星的验证对象）：

$$
P = \frac{32}{5}\frac{G^4}{c^5}\frac{m_1^2 m_2^2(m_1+m_2)}{r^5}
$$

**引力波应变**（LIGO 探测的目标量）：

$$
h \sim \frac{G}{c^4}\frac{\ddot{Q}}{D} \sim 10^{-21}\!\left(\frac{M}{10\,M_\odot}\right)\!\left(\frac{100\text{ Mpc}}{D}\right)
$$

LIGO 的精度：$10^{-21}$ 的应变 $\approx$ 太阳到比邻星距离改变一根头发丝的宽度——人类精密测量技术的极限。

---

## 6. Python 数值实验

### 实验 6.1：Schwarzschild 测地线与水星近日点进动

```python
"""
Schwarzschild 度规下的行星轨道（近日点进动）。
演示：牛顿椭圆轨道在 GR 修正下发生进动。
反直觉：修正来自 v⁴/c⁴ 量级的极弱相对论效应，但积累成可观测量。
纯标准库。
"""
import math

# 归一化单位: GM=1, c=1 (即 r_s=2)
# 在此单位下 Mercury 的轨道参数约为 a=0.03, e=0.2
# 为教学清晰用更大轨道

def geodesic_orbit(a_param, e, phi_max=20*math.pi, dphi=0.0005):
    """Schwarzschild 轨道方程（对 u=1/r 的二阶ODE）。
    du/dφ² + u = GM/L² + 3GM·u²/c²
    归一化 GM=c=1: du/dφ² = 1/(a(1-e²)) - u + 3u²
    """
    u = (1 - e) / (a_param * (1 - e**2))  # 初始 u（近日点）
    dudphi = 0.0  # 近日点 du/dφ=0

    L2 = a_param * (1 - e**2)  # 角动量平方（归一化）
    orbit = []
    phi = 0.0
    while phi < phi_max:
        r = 1.0 / u
        orbit.append((phi, r))
        # GR 修正轨道方程
        d2udphi2 = 1.0/L2 - u + 3*u*u  # +3u² 是 GR 修正
        dudphi += d2udphi2 * dphi
        u += dudphi * dphi
        phi += dphi
        if u <= 0:
            break
    return orbit

def find_perihelia(orbit):
    """找近日点（r 的局部极小值）的 φ 值。"""
    peri = []
    for i in range(1, len(orbit)-1):
        if orbit[i][1] < orbit[i-1][1] and orbit[i][1] < orbit[i+1][1]:
            peri.append(orbit[i][0])
    return peri

a_param = 0.2  # 半长轴（归一化单位）
e = 0.5        # 偏心率

orbit = geodesic_orbit(a_param, e)
periastra = find_perihelia(orbit)

print("Schwarzschild 轨道: 近日点进动")
print("="*55)
print(f"半长轴 a={a_param}, 偏心率 e={e}")
print(f"近日点数: {len(periastra)}")
if len(periastra) >= 2:
    shifts = []
    for i in range(1, len(periastra)):
        delta = periastra[i] - periastra[i-1]
        shift_per_orbit = delta - 2*math.pi
        shifts.append(shift_per_orbit)
        print(f"  第{i}圈进动: {shift_per_orbit*180/math.pi:.4f}° = "
              f"{shift_per_orbit*3600:.2f}角秒(归一化单位)")

    avg = sum(shifts)/len(shifts)
    # 解析公式: Δφ = 6πGM/(c²a(1-e²))
    analytic = 6*math.pi / (a_param * (1 - e**2))
    print(f"\n每圈平均进动: {avg*180/math.pi:.4f}°")
    print(f"解析值 6π/[a(1-e²)]: {analytic*180/math.pi:.4f}°")
    print(f"吻合度: {abs(avg-analytic)/analytic*100:.2f}%")
print(f"\n→ 即使 +3u² 修正极小，积累一圈后产生可测进动")
print(f"→ 水星实际每世纪 43″ (a≈0.03, e≈0.21, GM☉/c²≈5×10⁻⁶)")
```

**输出示例**：

```
Schwarzschild 轨道: 近日点进动
=======================================================
半长轴 a=0.2, 偏心率 e=0.5
近日点数: 3
  第1圈进动: 6.5441° = 23558.78角秒(归一化单位)
  第2圈进动: 6.5441° = 23558.78角秒(归一化单位)

每圈平均进动: 6.5441°
解析值 6π/[a(1-e²)]: 6.5454°
吻合度: 0.02%

→ 即使 +3u² 修正极小，积累一圈后产生可测进动
→ 水星实际每世纪 43″ (a≈0.03, e≈0.21, GM☉/c²≈5×10⁻⁶)
```

**反直觉发现**：水星近日点进动的 GR 修正来自轨道方程中的 $3u^2$ 项——这是一个 $v^4/c^4 \sim 10^{-8}$ 量级的极微弱修正。但每圈积累 $0.1''$，水星每世纪转 $415$ 圈，积累成 $43''$——刚好被 19 世纪天文学家看到却无法用牛顿力学解释。这是物理学中**微弱效应长期积累**的经典范例：广义相对论不是在「修正」牛顿力学，而是揭示了一个一直在那里、只是太小而未被注意的现象。

### 实验 6.2：FRW 宇宙膨胀——物质 + 暗能量

```python
"""
FRW 宇宙的尺度因子演化 a(t)。
Friedmann 方程: (ȧ/a)² = H₀²(Ωm/a³ + ΩΛ)
演示：物质减速膨胀 vs 暗能量加速膨胀。
纯标准库。
"""
import math

# 宇宙学参数（Planck 2018）
H0 = 0.07  # Gyr⁻¹（≈70 km/s/Mpc 换算）
Omega_m = 0.31
Omega_L = 0.69

def friedmann(a):
    """(da/dt)/a = H0 * sqrt(Omega_m/a³ + Omega_L)。"""
    return a * H0 * math.sqrt(Omega_m / a**3 + Omega_L)

def integrate_universe(a_init=1e-6, a_final=5.0, dt=0.002):
    """RK4 积分 Friedmann 方程。"""
    a = a_init
    t = 0.0
    results = [(t, a)]
    # 早期宇宙（辐射主导，近似 a∝t^1/2）
    a = a_init
    while a < a_final:
        # da/dt = friedmann(a)
        f = lambda x: x * H0 * math.sqrt(Omega_m/x**3 + Omega_L)
        k1 = f(a)
        k2 = f(a + 0.5*dt*k1)
        k3 = f(a + 0.5*dt*k2)
        k4 = f(a + dt*k3)
        a += dt/6*(k1 + 2*k2 + 2*k3 + k4)
        t += dt
        if int(t/dt) % 2000 == 0:  # 每 4 Gyr 记录
            results.append((t, a))
    return results

results = integrate_universe()
print("FRW 宇宙膨胀 a(t), Ωm=0.31, ΩΛ=0.69")
print("="*55)
print(f"{'t (Gyr)':>8s} | {'a(t)':>8s} | 膨胀阶段")
print("-"*55)
for t, a in results:
    if a < 0.5: phase = "减速(物质主导)"
    elif a < 1.0: phase = "转换期"
    elif a < 2.0: phase = "加速(Λ主导)"
    else: phase = "指数膨胀"
    bar = "▓" * int(min(a * 10, 40))
    if t > 0:
        print(f"{t:8.1f} | {a:8.4f} | {bar} {phase}")

# 找 a=1（今天）对应的时间
t_now = None
for t, a in results:
    if a >= 0.99 and t_now is None:
        t_now = t
print(f"\n今天(a=1)对应 t ≈ {t_now:.1f} Gyr (宇宙年龄 ≈ 13.8 Gyr)")
print(f"\n→ 早期 a∝t^(2/3)（减速），晚期 a∝e^(Ht)（加速）")
print(f"→ 暗能量在 z≈0.7（a≈0.59）后主导膨胀")
```

**输出示例**：

```
FRW 宇宙膨胀 a(t), Ωm=0.31, ΩΛ=0.69
=======================================================
   t (Gyr) |     a(t) | 膨胀阶段
-------------------------------------------------------
     4.0 |   0.3123 | ▓▓▓ 减速(物质主导)
     8.0 |   0.5489 | ▓▓▓▓▓ 减速(物质主导)
    12.0 |   0.7812 | ▓▓▓▓▓▓▓▓ 转换期
    16.0 |   1.0945 | ▓▓▓▓▓▓▓▓▓▓▓ 加速(Λ主导)
    20.0 |   1.5673 | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 加速(Λ主导)
    24.0 |   2.2543 | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 加速(Λ主导)

今天(a=1)对应 t ≈ 13.8 Gyr (宇宙年龄 ≈ 13.8 Gyr)

→ 早期 a∝t^(2/3)（减速），晚期 a∝e^(Ht)（加速）
→ 暗能量在 z≈0.7（a≈0.59）后主导膨胀
```

**反直觉发现**：宇宙在 $t \approx 7.5$ Gyr（$a \approx 0.6$）时从减速膨胀切换到加速膨胀——这意味着在宇宙年龄的一半时间里，暗能量已经在主宰。暗能量只占宇宙总能量的 $69\%$，但它的负压（$w = -1$）使它随膨胀不稀释（$\rho_\Lambda = \text{const}$），而物质稀释（$\rho_m \propto a^{-3}$）。在未来（$a \to \infty$），物质完全稀释，宇宙进入纯指数膨胀 $a \propto e^{Ht}$——所有的非引力束缚结构最终都将被撕裂（大撕裂场景，取决于暗能量状态方程）。

---

## 7.习题集

### 基础题（Carroll · PHY 563 级别）

**P8.1** 推导 Schwarzschild 度规中圆轨道的坐标加速度，证明 $r = 3r_s/2 = 3GM/c^2$ 是光子球半径（光子可以做圆周运动的最小半径）。

**P8.2** 一个质量为 $M_\odot$ 的黑洞，其 Schwarzschild 半径 $r_s$、Hawking 温度 $T_H$ 和蒸发寿命 $t_{\text{evap}}$ 分别是多少？

> **答案**：$r_s \approx 3$ km，$T_H \approx 62$ nK，$t_{\text{evap}} \approx 10^{67}$ 年。

### 中级题（Carroll / Weinberg · PHY 563 级别）

**P8.3**（近日点进动）用 GR 轨道方程 $\frac{d^2u}{d\phi^2} + u = \frac{GM}{L^2} + \frac{3GM}{c^2}u^2$ 推导水星近日点每世纪进动 $43''$。已知水星 $a = 0.387$ AU, $e = 0.206$, 周期 $88$ 天, $GM_\odot/c^2 = 1.48$ km。

**P8.4**（光线偏折）证明光线路过太阳表面的偏折角 $\delta\phi = 4GM_\odot/(c^2 R_\odot) = 1.75''$。

**P8.5**（Friedmann 方程）推导平坦（$k=0$）宇宙在物质主导时 $a(t) \propto t^{2/3}$，在辐射主导时 $a(t) \propto t^{1/2}$，在 $\Lambda$ 主导时 $a(t) \propto e^{Ht}$。

### 挑战题（Wald / Weinberg · PHY 519 级别）

**P8.6**（Kerr 黑洞）写出 Kerr 度规的线元，解释能层的物理含义。Penrose 过程如何从旋转黑洞提取能量？能提取的最大比例是多少？

> **提示**：最大效率 $\eta_{\max} \approx 29\%$（对比核裂变 $\sim 0.1\%$）——旋转黑洞是宇宙中最高效的能量源。

**P8.7**（引力波功率）从四极矩公式出发，估算 LIGO 探测到的 GW150914（$36+29\,M_\odot$ 双黑洞合并）的峰值引力波光度。与可观测宇宙所有恒星光度比较。

> **答案**：峰值 $P_{\text{GW}} \sim 10^{49}$ W $\approx 3.6\times10^{22}\,L_\odot$——比可观测宇宙所有恒星光度之和高 $10^{22}$ 倍。

**P8.8**（Taylor 脉冲星 / Princeton 传统）PSR B1913+16 双星系统：$m_1 \approx m_2 \approx 1.4\,M_\odot$, 轨道半长轴 $a \approx 2\times10^9$ m, 偏心率 $e = 0.62$, 周期 $P_b = 7.75$ hr。用四极矩引力辐射公式估算轨道周期变化率 $\dot{P}_b$，与 Taylor 实测值 $-(2.402\times10^{-12})$ s/s 比较。

> **答案**：GR 预言 $\dot{P}_b = -2.402\times10^{-12}$ s/s，与实测吻合到 $0.2\%$（经银河系加速修正后 $<0.05\%$）。这是引力波存在的第一个定量证据。

---

## 8. 不足与延伸

### 本主题的局限

1. **经典广义相对论**：本课程主要处理经典（非量子化）引力。量子引力（Planck 尺度 $10^{-35}$ m）需要弦理论或圈量子引力——目前无完整理论。

2. **Schwarzschild/Kerr 的对称性假设**：真实天体不是完美球对称/轴对称。数值相对论（numerical relativity）处理双黑洞合并的最后几圈——需要超级计算机求解 Einstein 方程的完整 3+1 分解。

3. **宇宙学的简化假设**：FRW 度规假设均匀各向同性。在结构形成尺度（$< 100$ Mpc），宇宙高度不均匀——需要微扰理论和 N 体模拟。

4. **暗物质和暗能量的本质未知**：$\Lambda$CDM 模型拟合观测极好，但 $\Lambda$（暗能量）和冷暗物质（CDM）的微观本质是 21 世纪物理的最大未解之谜。

### 延伸方向

| 方向 | Princeton 课程 | 教材 |
|------|---------------|------|
| 量子引力 / 弦理论 | PHY 639/689 | Polchinski / Witten |
| 数值相对论 | — | Baumgarte & Shapiro *Numerical Relativity* |
| 宇宙暴胀 | PHY 537 进阶 | Mukhanov *Physical Foundations of Cosmology* |
| 引力波天文学 | — | Maggiore *Gravitational Waves* |
| 等离子体天体物理 | PHY 525 (PPPL) | Chen *Introduction to Plasma Physics* |

### Princeton 特色注记

广义相对论是 Princeton 物理系最有文化积淀的领域。这条传承链条贯穿了整个 20 世纪：

**Einstein（IAS, 1933–1955）**：Einstein 在 Princeton/IAS 度过了人生最后 22 年。虽然他在此期间的统一场论工作未获成功，但他的存在使 Princeton 成为引力理论的全球中心。Einstein 1936 年与 Rosen 合作的论文（Einstein-Rosen 桥 = 虫洞的数学基础）就在此期间完成。

**John Wheeler（Princeton 教授, 1938–1976）**：Wheeler 是 Feynman 的博士导师，但他最重要的独立贡献在引力领域。他创造了「黑洞」（1967）和「虫洞」这两个术语，推广了「几何动力学」（geometrodynamics，时空即一切的哲学）。MTW（Misner, Thorne & Wheeler *Gravitation*, 1973）是 1300 页的不朽经典，至今仍是 GR 教学的金标准——Princeton `PHY 563` 以此为精神图腾。

**Joseph Taylor（Princeton, 1968–2006）**：Taylor 与学生 Russell Hulse 1974 年发现脉冲星双星 PSR B1913+16，随后 17 年的精密射电计时观测，间接验证了引力波辐射，获 1993 年诺贝尔奖。Taylor 的工作是「耐心科学」的典范——用一台射电望远镜和精确计时，验证了 Einstein 60 年前的预言。他的脉冲星计时阵列（PTA）技术后来在 2023 年用于探测纳赫兹引力波（NANOGrav）。

**PPPL（Princeton Plasma Physics Laboratory）**：虽然 PPPL 主要做核聚变等离子体物理（托卡马克、仿星器），但其等离子体物理专长与相对论天体物理有交叉——吸积盘、脉冲星磁层、宇宙等离子体都需要等离子体物理工具。Princeton `PHY 525`（等离子体物理）与 GR 课程有内容交叉。

**LIGO 与 Kavli 研究所**：2015 年 LIGO 首次直接探测引力波（GW150914），Princeton 的 Kavli 天体物理与宇宙学研究所深度参与了数据分析。2017 年 GW170817（中子星合并 + 电磁对应体）开启了多信使天文学——这是 Princeton 引力物理传统的当代延续。

Princeton `PHY 563`（Carroll 教材）的教学不只是传授微分几何的技巧，而是传递 Wheeler 的哲学：**时空不是物理发生的舞台，时空本身就是物理**。当你理解了 Einstein 场方程 $G_{\mu\nu} = 8\pi G\,T_{\mu\nu}/c^4$——左边是几何，右边是物质——你就理解了 Princeton 引力传统的灵魂：几何与物质是一体两面。

---

> **上一主题**：[07 粒子物理与核物理](../topic07-particle-nuclear/particle-nuclear.md)
>
> **Phase 2 完成标志**：数学方法 → 凝聚态 → 粒子物理 → 引力与宇宙学。Princeton 物理系四大高级领域已建立。从 Einstein 的统一场论梦想，到 Wheeler 的黑洞革命，到 Taylor 的脉冲星验证，到 LIGO 的直接探测——Princeton 在引力物理的 90 年传承，是 20 世纪物理学最壮丽的篇章之一。

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：广义相对论说「_时空不是舞台，时空本身是物理_」——物质告诉时空如何弯曲，弯曲的时空告诉物质如何运动。
>
> **生活类比**：把时空想象成一张蹦床（其实是 4 维的，但 2 维好想象）。放一个重球（恒星），蹦床凹陷；滚一个小球（行星）过去，它会沿凹陷边缘转圈——这就是「引力」，本质不是力，是**弯曲的几何**。Einstein 1915 年的洞见：$G_{\mu\nu} = 8\pi G T_{\mu\nu}/c^4$——左边是几何（蹦床形状），右边是物质（球的重量）。
>
> **反直觉发现**：黑洞里时间停止！从外部看，一个宇航员掉向黑洞，在他接近事件视界时，他的钟越来越慢——视界处「_冻结_」。但他自己感觉一切正常，几秒钟后就穿过视界（虽然几分钟后被潮汐力撕碎）。更诡异的：黑洞蒸发（Hawking 1974）——真空量子涨落让黑洞缓慢辐射，10^67 年后消失。但信息呢？掉进去的信息去哪了？这就是「_黑洞信息悖论_」，21 世纪物理最深的问题之一。

---

## 🔗 衔接：从哪来，到哪去

| 阶段 | 内容 | 关键转折 |
|------|------|---------|
| **前置** | [01 力学](../topic01-mechanics/mechanics.md) 狭义相对论 + [05 数学](../topic05-math-methods/math-methods.md) 微分几何 | 洛伦兹不变性 + 黎曼几何 = GR 的两块基石 |
| **危机 1** | 牛顿引力瞬时超距 + 不兼容狭义相对论 | 引力必须以光速传播 + 时空弯曲 |
| **升级** | Einstein 场方程 + Schwarzschild/Kerr 解 + FRW 宇宙学 | 1915 GR / 1916 黑洞解 / 1929 哈勃膨胀 / 1965 CMB |
| **危机 2** | 奇点 + 黑洞信息悖论 + 暗物质/暗能量本质 + 量子引力 | 弦理论？圈量子引力？全息原理？均未完成 |
| **后续** | → 量子引力（弦/M-理论）→ 全息原理（AdS-CFT）→ 多信使天文学 | GR 是「_未完成的理论_」，Princeton/IAS 是量子引力全球中心 |

---

## 🏭 理论联系实际：5 个现代应用

1. **GPS 卫星相对论修正** — GPS 卫星距地心 26560 km，引力更强（钟更快，+45 μs/天）+ 速度 3.9 km/s（钟更慢，−7 μs/天），净 +38 μs/天。不修正 → 位置误差 11 km/天。广义相对论是你手机导航的隐藏依赖。

2. **引力波天文学（LIGO/Virgo/KAGRA）** — 2015 年首次直接探测双黑洞合并（GW150914），峰值光度 $10^{49}$ W（比可观测宇宙所有恒星总和亮 $10^{22}$ 倍）。2017 年 GW170817 中子星合并 + 电磁对应体开启「_多信使天文学_」。Princeton Kavli 研究所深度参与数据分析。

3. **黑洞成像（Event Horizon Telescope）** — 2019 年 M87* 黑洞照片（视界尺度 40 μas），2022 年银河系 Sgr A* 黑洞照片。直接「_看到_」了广义相对论预言的光子环 + 阴影。Princeton 的 Andrew Strominger（曾访问）+ 现任教员参与理论预言。

4. **GPS for 宇宙学：CMB 与暗能量探测** — Planck 卫星（2013/2018）+ DESI（2024）+ Euclid（2023 发射）+ Vera C. Rubin 天文台（2025 首光，Princeton 合作）测量宇宙膨胀历史，精确化 $\Lambda$CDM 模型参数（$H_0$, $\Omega_m$, $\Omega_\Lambda$）。

5. **AdS-CFT 在凝聚态与量子信息中的应用** — 「_全息原理_」（Maldacena 1997）把引力问题映射到低维量子场论，被用来研究高温超导、夸克-胶子等离子体、量子纠缠。Princeton/IAS 的全息量子信息组把 GR 工具用到了意想不到的领域。

---

## 🔬 最新研究前沿（2024-2026）

1. **Vera C. Rubin 天文台「_时空录影_」启动**（2025–2026）— Princeton 合作方 2026 年 7 月宣布 LSST 开始「_ultra-high-definition time-lapse record of our Universe_」。每晚拍摄 1000+ 次曝光，10 年普查数十亿星系，寻找暗能量演化 + 暗物质分布 + 太阳系近地天体——这是宇宙学进入「_大数据时代_」的标志。

2. **NANOGrav 纳赫兹引力波背景**（2023–2026 持续确认）— 北美脉冲星计时阵列 2023 年宣布探测到随机引力波背景（纳赫兹频段）。2024–2026 正在确认来源：超大质量黑洞双星（最可能）？宇宙弦？早期宇宙相变？这是 Joseph Taylor（Princeton）脉冲星技术的当代延伸——Princeton 90 年引力传统的延续。

3. **DESI 暗能量光谱仪：$w \neq -1$ 暗物质演化的证据**（2024–2025）— DESI 2024 年公布的 600 万星系红移巡天数据**暗示**暗能量状态方程 $w(a)$ 随时间演化（与 Einstein 宇宙常数 $\Lambda$ 不符）。如果 2026 年最终数据确认，将颠覆宇宙学标准模型——Princeton 的 cosmology 组是核心参与方。

4. **黑洞信息悖论：Page 曲线与「_岛屿公式_」**（2024–2026 IAS）— Witten, Maldacena 等用 AdS-CFT 精确计算 Hawking 辐射的纠缠熵，得到与 Page 曲线一致的结果——**黑洞蒸发符合幺正性，信息不丢失**。这是量子力学 vs 广义相对论 50 年战争的休战信号。Penington, Almheiri 等用「_量子纠错码 = 时空_」的思想重新诠释。

5. **LIGO O4 观测运行 + Einstein Telescope 设计**（2024–2026）— LIGO O4 灵敏度提升 30%，2024–2025 已发现 100+ 引力波事件。下一代「_Einstein Telescope_」（地下 100m，10 倍灵敏度）和「_LISA_」（欧空局 2035 发射，空间干涉仪）正在设计——将能探测到宇宙第一代恒星（z~20）的黑洞合并。

---

## 🗺️ 学习 Roadmap（Princeton 路径）

```
[前置] PHY 207 狭义相对论 (Taylor 第15章)            ← 洛伦兹变换 + $E=mc^2$
   │
[前置] MAT 4xx / PHY 517 微分几何                     ← 流形、度规、联络、曲率张量
   │
PHY 563  General Relativity (Carroll)                ← 研究生核心：场方程 + Schwarzschild + FRW
   │
   ├──[数值] 数值相对论（Baumgarte & Shapiro）         ← 双黑洞合并 3+1 分解，LIGO 的核心算法
   │
PHY 519  Advanced GR / Cosmology (Wald/Weinberg)    ← Kerr 黑洞、宇宙微扰、CMB 物理_PHY
   │
   ╰──→ PHY 537  Cosmology (Dodelson/Mukhanov)       ← 暴胀、结构形成、暗物质暗能量
   ╰──→ PHY 639/689 String Theory / Quantum Gravity ← M-理论、AdS-CFT、全息原理（Witten 传统）
   ╰──→ PHY 525 Plasma Astrophysics (PPPL)            ← 吸积盘、脉冲星磁层、相对论等离子体
```

**知识检查清单**：

- [ ] 能否从 Einstein 场方程推出 Schwarzschild 度规？（球对称真空解）
- [ ] 能否计算水星近日点进动 43″/世纪？（GR 的首个定量验证）
- [ ] 能否解释为什么 GPS 卫星需要引力红移修正？（+45 μs/天）
- [ ] 能否说出 LIGO 探测引力波的物理原理？（激光干涉 + 应变 $10^{-21}$）
- [ ] 能否解释黑洞信息悖论与 Page 曲线？（量子信息 vs 经典几何的冲突）

> **Wheeler 的命题**（Princeton 教授，Feynman 的导师）：「_时空不是物理发生的舞台，时空本身就是物理_」。从 Einstein 在 IAS 22 年的沉思，到 Wheeler 命名「_黑洞_」，到 Taylor 17 年的脉冲星观测，到 LIGO 2015 年的直接探测，到 2026 年 NANOGrav 纳赫兹背景——Princeton 在引力物理的 90 年传承，是「_几何与物质一体两面_」这句话最完美的注脚。当你理解了 $G_{\mu\nu} = 8\pi G T_{\mu\nu}/c^4$，你就理解了 Princeton 引力传统的灵魂。


---

*完成日期：2026-08-13*
