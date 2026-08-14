# Topic 08 · 广义相对论与宇宙学 — Caltech GR / LIGO 核心

> **课程链**：Ph 106bc（数学方法/微分几何）→ Ph 236abc *General Relativity*（**MTW — Misner, Thorne & Wheeler**，Caltech 自己的经典！）→ Ph 237 *Gravitational Physics*（Carroll 进阶）
>
> **教材三角**：**Misner, Thorne & Wheeler (MTW) *Gravitation***（**Caltech 的圣经！** Kip Thorne 是 Caltech 教授、2017 诺奖）· Carroll *Spacetime and Geometry*（现代标准研究生教材）· Hartle *Gravity: An Introduction to Einstein's General Relativity*（最友好的入门）

---

## Caltech 特色：MTW + LIGO —— Caltech 的相对论王国

Caltech 的广义相对论教学有两个不可替代的基因：

1. **MTW 是 Caltech 的圣经**——*Gravitation*（1973）由 Charles Misner（Maryland）、**Kip Thorne（Caltech）**、John Archibald Wheeler（Princeton）合著。这本书有近 1300 页，黑色封面，物理学家戏称它为"**电话簿**"（the Telephone Book）。它至今仍是 GR 教材中最全面的百科全书，其多轨教学策略（前半部面向本科直觉，后半部面向研究生严谨）影响了全球一代相对论学家。Caltech 的 Ph 236 至今以 MTW 为核心参考。

2. **LIGO 是 Caltech 的旗舰**——Kip Thorne 和 Rainer Weiss（MIT）在 1980–90 年代构想了激光干涉仪引力波天文台（LIGO）。Caltech 是 LIGO 的两个主导机构之一（另一个是 MIT）。2015 年 9 月 14 日，Advanced LIGO 首次直接探测到引力波（GW150914——双黑洞并合），证实了 Einstein 1916 年的预言。Thorne、Weiss 和 Barry Barish（Caltech）因此获 2017 年诺贝尔物理学奖。Caltech 的 40m 原型干涉仪至今仍在运行，是下一代探测器（Cosmic Explorer）的研发平台。

---

## §1 等效原理与几何化

### 1.1 等效原理的三层

Einstein 的天才洞察——引力和加速度在局部不可区分：

| 层次 | 表述 | 实验检验 |
|------|------|---------|
| 弱等效原理（WEP）| 惯性质量 = 引力质量 | Eötvös 实验：$10^{-15}$ |
| Einstein 等效原理（EEP）| WEP + 局部 Lorentz 不变 + 局部位置不变 | 精度 $10^{-10}$+ |
| 强等效原理（SEP）| EEP 对引力自能也成立 | 月球激光测距 |

> **物理意义**：EEP 成立 $\Rightarrow$ 引力是时空几何效应（度规理论），而非一种力。这是 GR 的哲学基础。

### 1.2 从平直到弯曲：度规

狭义相对论的 Minkowski 度规：

$$ds^2 = \eta_{\mu\nu}dx^\mu dx^\nu = -c^2dt^2 + dx^2 + dy^2 + dz^2$$

广义相对论：时空是弯曲的，度规 $g_{\mu\nu}(x)$ 成为 dynamical 变量：

$$ds^2 = g_{\mu\nu}(x)\,dx^\mu dx^\nu$$

> **核心思想（MTW 的风格）**：物质告诉时空如何弯曲；弯曲的时空告诉物质如何运动。 Wheeler 的经典总结。

---

## §2 张量分析与微分几何

### 2.1 协变导数

在弯曲时空中，普通偏导数不是张量。需要引入**协变导数**：

$$\nabla_\mu V^\nu = \partial_\mu V^\nu + \Gamma^\nu_{\mu\lambda}V^\lambda$$

其中 $\Gamma^\nu_{\mu\lambda}$ 是 **Christoffel 联络**（ Levi-Civita connection）：

$$\Gamma^\lambda_{\mu\nu} = \frac{1}{2}g^{\lambda\sigma}(\partial_\mu g_{\nu\sigma} + \partial_\nu g_{\mu\sigma} - \partial_\sigma g_{\mu\nu})$$

> **物理直觉**：$\Gamma$ 表示坐标基矢在时空中如何"旋转"。粒子沿测地线运动，看似加速实则是坐标基在变——这是 Einstein 的洞察。

### 2.2 测地线方程

自由下落粒子走**测地线**（弯曲时空的"直线"）：

$$\boxed{\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta}\frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau} = 0}$$

> **对比牛顿力学**：在弱场低速极限下，$g_{00} \approx -(1+2\Phi/c^2)$，测地线方程退化为 $\ddot{x}^i = -\partial_i\Phi$——牛顿引力是 GR 的极限！

### 2.3 Riemann 曲率张量

曲率张量衡量时空的弯曲程度：

$$R^\rho_{\;\;\sigma\mu\nu} = \partial_\mu\Gamma^\rho_{\nu\sigma} - \partial_\nu\Gamma^\rho_{\mu\sigma} + \Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma}$$

缩并得到：
- **Ricci 张量**：$R_{\mu\nu} = R^\lambda_{\;\;\mu\lambda\nu}$
- **标曲率**：$R = g^{\mu\nu}R_{\mu\nu}$
- **Einstein 张量**：$G_{\mu\nu} = R_{\mu\nu} - \frac{1}{2}g_{\mu\nu}R$

---

## §3 Einstein 场方程

### 3.1 宇宙中最美的方程

$$\boxed{G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}}$$

或展开为：

$$R_{\mu\nu} - \frac{1}{2}g_{\mu\nu}R + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}$$

| 项 | 意义 |
|----|------|
| 左边 $G_{\mu\nu}$ | 时空几何（曲率）|
| $\Lambda g_{\mu\nu}$ | 宇宙学常数（暗能量）|
| 右边 $T_{\mu\nu}$ | 物质-能量动量张量 |
| $8\pi G/c^4$ | 耦合常数 $\approx 2\times10^{-43}\,\text{N}^{-2}$ |

> **MTW 的表述**（Ch 17）：左边是时空的弹性；右边是载荷。Einstein 方程是时空的"应力-应变关系"。

### 3.2 能量动量张量

不同物质的 $T_{\mu\nu}$：

**理想流体**：
$$T^{\mu\nu} = (\rho + p/c^2)u^\mu u^\nu + pg^{\mu\nu}$$

其中 $\rho$ 是质量密度，$p$ 是压强，$u^\mu$ 是四速度。

**真空能（宇宙学常数）**：
$$T^{\mu\nu}_{\Lambda} = -\frac{\Lambda c^4}{8\pi G}g^{\mu\nu}$$

### 3.3 Bianchi 恒等式与守恒

Bianchi 恒等式 $\nabla_\lambda R_{\mu\nu\rho\sigma} + \text{cyclic} = 0$ 缩并后给出：

$$\nabla_\mu G^{\mu\nu} = 0$$

这自动保证能量动量守恒 $\nabla_\mu T^{\mu\nu} = 0$——**几何守恒 = 物理守恒**，这是 Einstein 方程的自洽性。

---

## §4 Schwarzschild 解：黑洞

### 4.1 球对称真空解

Schwarzschild (1916)——Einstein 发表场方程后仅一个月就找到了第一个精确解：

$$ds^2 = -\left(1-\frac{r_s}{r}\right)c^2dt^2 + \frac{dr^2}{1-r_s/r} + r^2(d\theta^2 + \sin^2\theta\,d\phi^2)$$

其中 **Schwarzschild 半径**（事件视界）：

$$r_s = \frac{2GM}{c^2}$$

**数字感**：
- 太阳：$r_{s,\odot} \approx 3\,\text{km}$
- 地球：$r_{s,\oplus} \approx 9\,\text{mm}$
- LIGO 探测的 36 $M_\odot$ 黑洞：$r_s \approx 106\,\text{km}$

### 4.2 引力时间膨胀

在引力势中，时钟变慢：

$$\Delta t_\infty = \frac{\Delta \tau}{\sqrt{1 - r_s/r}}$$

> **GPS 应用**：GPS 卫星在 $h \approx 20{,}000\,\text{km}$ 高度，引力时间膨胀使卫星钟比地面快 $\sim 45\,\mu\text{s/day}$，狭义相对论速度效应慢 $\sim 7\,\mu\text{s/day}$，净效应 $+38\,\mu\text{s/day}$。不修正的话，GPS 定位每天误差 $\sim 10\,\text{km}$——GR 的日常应用！

### 4.3 光线弯曲

光线经过质量 $M$，偏转角：

$$\alpha = \frac{4GM}{c^2 b} = \frac{2r_s}{b}$$

其中 $b$ 是碰撞参数（impact parameter）。

> **历史时刻**：Eddington 1919 年日全食观测确认了 Einstein 的预言（$\alpha \approx 1.75''$ for 太阳），使 Einstein 一夜成名。

### 4.4 黑洞无毛定理

> **Israel-Carter-Hawking 定理**：稳态黑洞完全由三个参数决定——质量 $M$、角动量 $J$（或 $a = J/Mc$）、电荷 $Q$。

$$\text{黑洞} = (M, J, Q) \quad \text{——"黑洞无毛"}$$

> **意义**：无论前身如何复杂（恒星、星系、人……），一旦坍缩成黑洞，几乎所有信息都消失了——只留三个量子数。这是 GR 最深刻的结论之一，也是信息悖论的起源。

### 4.5 Kerr 黑洞（旋转）

旋转黑洞的度规（Kerr 1963）：

$$a = \frac{J}{Mc}$$

事件视界：$r_+ = \frac{GM}{c^2} + \sqrt{\left(\frac{GM}{c^2}\right)^2 - a^2}$

能层（ergosphere）：$r_{\rm ergo} = \frac{GM}{c^2} + \sqrt{\left(\frac{GM}{c^2}\right)^2 - a^2\cos^2\theta}$

> **Penrose 过程**：在能层内，粒子可以有负能量轨道。抛入粒子并使其分裂，一部分带负能量坠入黑洞，另一部分带正能量逃逸——**从旋转黑洞提取能量**！这在天体物理中可能是相对论性喷流的能源。

---

## §5 引力波：LIGO 的物理基础

### 5.1 线性化引力波

弱场极限 $g_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu}$，$|h_{\mu\nu}| \ll 1$。

在横向无迹（TT）规范下，波动方程：

$$\Box \bar{h}_{\mu\nu}^{TT} = 0$$

平面波解：

$$h_{\mu\nu}^{TT} = A_{\mu\nu}\cos(k_\alpha x^\alpha)$$

只有两个独立偏振态：$+$（plus）和 $\times$（cross）。

### 5.2 四极矩辐射

> Einstein 1916/1918：引力波由质量**四极矩**的二阶时间导数辐射（对比电磁辐射是偶极矩）。

功率（四极矩公式）：

$$P_{GW} = \frac{G}{5c^5}\langle \dddot{Q}_{ij}\dddot{Q}_{ij}\rangle$$

> **反直觉发现**：$G/c^5 \approx 3.6\times10^{-53}\,\text{W}^{-1}$ 是极其微小的耦合——这意味着即使最剧烈的天体事件（如超新星），引力波功率也只有 $\sim 10^{-4}$ 倍太阳光度被辐射为引力波。但因为 $c^5$ 在分母，辐射极弱——这就是为什么引力波探测花了 100 年。

### 5.3 双星旋近

两个致密天体（黑洞/中子星）螺旋向内，辐射引力波损失能量：

$$\frac{dE}{dt} = -\frac{32}{5}\frac{G^4}{c^5}\frac{M_1^2 M_2^2(M_1+M_2)}{r^5}$$

轨道频率 chirp（增加）：

$$\dot{f} = \frac{96}{5}\pi^{8/3}\left(\frac{G\mathcal{M}}{c^3}\right)^{5/3}f^{11/3}$$

其中 **chirp 质量**：

$$\mathcal{M} = \frac{(M_1 M_2)^{3/5}}{(M_1+M_2)^{1/5}}$$

### 5.4 GW150914——人类首次探测

> **2015 年 9 月 14 日 09:50:45 UTC**——Advanced LIGO 首次直接探测到引力波。

| 参数 | 值 |
|------|-----|
| 源距离 | $\sim 410\,\text{Mpc}$（$\sim 13$ 亿光年）|
| 初始质量 | $36\,M_\odot + 29\,M_\odot$ |
| 最终质量 | $62\,M_\odot$ |
| 辐射能量 | $3\,M_\odot c^2$（峰值功率 $\sim 3.6\times10^{49}\,\text{W}$）|
| 频率扫描 | 35 → 150 Hz（chirp）|
| 应变 $h$ | $\sim 10^{-21}$ |

> **$10^{-21}$ 有多小？** LIGO 臂长 $L = 4\,\text{km}$，臂长变化 $\Delta L = hL \approx 4\times10^{-18}\,\text{m}$——比质子半径还小 10000 倍。Caltech 和 MIT 的工程师们花了 20 年把噪声降到这个水平以下。这是人类精密工程的极限。

### 5.5 多信使天文学

> **GW170817**（2017 年 8 月 17 日）——双中子星并合。LIGO 探测到引力波，Fermi 卫星 1.7 秒后探测到伽马射线暴。

| 测量 | 结果 |
|------|------|
| 距离 | $\sim 40\,\text{Mpc}$（1.3 亿光年，NGC 4993）|
| 速度差 | $|v_{GW} - v_\gamma|/c < 10^{-15}$ |
| r-过程核合成 | 证实中子星并合是金、铂等重元素来源 |

> **Thorne 的话**："We are opening a fundamentally new window onto the universe." 引力波天文学从此诞生。

---

## §6 宇宙学

### 6.1 宇宙学原理与 FLRW 度规

在宇宙大尺度上，时空均匀且各向同性：

$$ds^2 = -c^2dt^2 + a^2(t)\left[\frac{dr^2}{1-kr^2} + r^2(d\theta^2 + \sin^2\theta\,d\phi^2)\right]$$

其中 $a(t)$ 是**尺度因子**，$k = 0, \pm 1$ 是空间曲率。

### 6.2 Hubble 定律

$$v = H_0 d$$

Hubble 常数（Planck 2018）：

$$H_0 \approx 67.4\,\text{km/s/Mpc}$$

Hubble 时间 $1/H_0 \approx 145$ 亿年——宇宙年龄的量级。

### 6.3 Friedmann 方程

从 Einstein 方程 + FLRW 度规：

$$\left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}$$

$$\frac{\ddot{a}}{a} = -\frac{4\pi G}{3}\left(\rho + \frac{3p}{c^2}\right) + \frac{\Lambda c^2}{3}$$

### 6.4 宇宙的能量组成

| 成分 | 占比 | 状态方程 $w = p/\rho c^2$ |
|------|------|------|
| 暗能量 $\Lambda$ | $\Omega_\Lambda \approx 0.69$ | $-1$ |
| 暗物质 | $\Omega_{DM} \approx 0.26$ | $0$ |
| 重子物质 | $\Omega_b \approx 0.05$ | $0$ |
| 辐射 | $\Omega_r \approx 5\times10^{-5}$ | $1/3$ |
| 曲率 | $\Omega_k \approx 0$ | — |

> **宇宙的 95% 是我们不了解的**——暗能量和暗物质占宇宙总能量的 95%，而标准模型的粒子只占 5%。这是 21 世纪物理学最大的谜题。

### 6.5 大爆炸与宇宙微波背景

宇宙膨胀 $\Rightarrow$ 早期更热更密 $\Rightarrow$ **大爆炸**。

宇宙微波背景（CMB）：$T = 2.7255\,\text{K}$，黑体辐射近乎完美。

$$T(z) = T_0(1+z)$$

> **CMB 的发现**（Penzias & Wilson, 1965, 1978 诺奖）——大爆炸理论的决定性证据。CMB 的温度涨落 $\Delta T/T \sim 10^{-5}$ 是结构形成的种子。

### 6.6 暴胀

宇宙在极早期（$t \sim 10^{-36}\,\text{s}$）经历了指数膨胀：

$$a(t) \propto e^{Ht}, \quad H \approx \text{const}$$

暴胀解决三大难题：
1. **视界问题**：为什么 CMB 全天温度如此均匀？
2. **平坦性问题**：为什么 $\Omega_k \approx 0$？
3. **磁单极问题**：为什么看不到大统一理论预言的磁单极？

> **暴胀的预言**：原初引力波（CMB B 模偏振）——LIGO 的宇宙学表亲（CMB-S4 实验）正在搜寻。Caltech 的 Simons Observatory 也参与其中。

---

## Python 演示：Schwarzschild 测地线 + 宇宙膨胀

```python
"""
Caltech Ph 236/237 Demo: GR 与宇宙学两个核心计算
1. Schwarzschild 圆轨道: 测地线方程 vs Newton 极限
2. ΛCDM 宇宙: 尺度因子演化 a(t)
纯标准库零依赖，bash 可直接跑通。
"""
import math

# ══════════════════════════════════════════════
# 1. Schwarzschild 圆轨道: GR 修正
# ══════════════════════════════════════════════
print("=== Schwarzschild 圆轨道 ===\n")
print("GR 圆轨道角速度 vs Newton:\n")

# 在 Schwarzschild 度规中，圆轨道 r=const 的测地线给出：
# Ω² = GM/r³ （巧合：与 Newton 完全相同！）
# 但轨道速度 v 和有效势有 GR 修正

# ISCO (最内稳定圆轨道) = 6GM/c² = 3 r_s
# Newton: 无 ISCO（所有 r > 0 稳定）

print("轨道半径 r / r_s    Newton v²/c²    GR v²/c²    稳定性")
print("-" * 65)
for r_over_rs in [100, 50, 20, 10, 6.0, 5.0, 3.5, 3.0]:
    r = r_over_rs  # 以 r_s 为单位
    # Newton: v²/c² = (GM/rc²) = r_s/(2r) = 1/(2·r_over_rs)
    v2_newton = 1.0 / (2 * r_over_rs)
    # GR: 圆轨道 v²/c² = (1/2)·(r_s/r) / (1 - r_s/r) 但更准确用角动量
    # 稳定圆轨道条件: r > 3r_s (=ISCO at 6M=3r_s)
    if r_over_rs > 1:
        v2_gr = 0.5 * (1.0 / r_over_rs) / (1 - 1.0 / r_over_rs)
    else:
        v2_gr = float('inf')

    # ISCO 判断（r > 6M = 3 r_s 稳定）
    if r_over_rs >= 6.0:
        stability = "稳定 ✓"
    elif r_over_rs >= 3.0:
        stability = "不稳定 ✗"
    else:
        stability = "无圆轨道（视界内）"

    if v2_gr < 1:
        print(f"  {r_over_rs:8.1f}         {v2_newton:.6f}      {v2_gr:.6f}     {stability}")

print(f"\n→ GR 最内稳定圆轨道 ISCO = 6GM/c² = 3 r_s（r/r_s = 6）")
print(f"→ Newton 理论无此限制——ISCO 是纯 GR 效应，对吸积盘至关重要。")
print(f"→ LIGO 探测的黑洞并合最后阶段就发生在 ISCO 附近。\n")

# ══════════════════════════════════════════════
# 2. ΛCDM 宇宙: 尺度因子 a(t)
# ══════════════════════════════════════════════
print("=== ΛCDM 宇宙演化 a(t) ===\n")

# Friedmann 方程: (ȧ/a)² = H₀²[Ω_r/a⁴ + Ω_m/a³ + Ω_Λ + Ω_k/a²]
# 令 a₀=1, 数值积分 ȧ = H₀·√(Ω_r/a² + Ω_m/a + Ω_Λ·a²)

H0 = 0.07  # 1/Gyr（≈ 67.4 km/s/Mpc 换算）
Omega_m = 0.31
Omega_L = 0.69
Omega_r = 5e-5  # 辐射（今天可忽略，早期主导）

def adot(a):
    """ȧ/a = H₀√(Ω_r/a⁴ + Ω_m/a³ + Ω_Λ)"""
    if a <= 0:
        return 0
    return H0 * a * math.sqrt(Omega_r/a**4 + Omega_m/a**3 + Omega_L)

# 向前积分: 从 a=1 (现在) 到 a=2 (未来)
print("未来演化 (从现在 a=1):")
print(f"{'a':>8s} {'t-现在(Gyr)':>14s} {'H(t)/H₀':>10s}")
a = 1.0
t = 0.0
dt = 0.01
for step in range(200):
    # RK4
    k1 = adot(a)
    k2 = adot(a + 0.5*dt*k1)
    k3 = adot(a + 0.5*dt*k2)
    k4 = adot(a + dt*k3)
    a_new = a + dt/6*(k1 + 2*k2 + 2*k3 + k4)
    if a_new <= a:
        break
    t += dt
    a = a_new
    H_ratio = adot(a) / (H0 * a)
    if step % 40 == 0 or a > 1.99:
        print(f"{a:8.4f} {t:14.2f} {H_ratio:10.4f}")

print(f"\n→ 未来宇宙膨胀加速（暗能量主导），H → H₀√Ω_Λ = {H0*math.sqrt(Omega_L):.4f}/Gyr")
print(f"  宇宙渐近 de Sitter 指数膨胀。\n")

# 向后积分: 从 a=1 到 a→0 (大爆炸)
print("过去演化 (追溯大爆炸):")
print(f"{'a':>8s} {'t-大爆炸(Gyr)':>14s} {'主导成分':>12s}")
a = 1.0
t = 0.0
dt = -0.001
for step in range(20000):
    k1 = adot(a) * dt
    k2 = adot(a + 0.5*k1) * dt
    k3 = adot(a + 0.5*k2) * dt
    k4 = adot(a + k3) * dt
    a_new = a + (k1 + 2*k2 + 2*k3 + k4)/6
    if a_new <= 0.001:
        break
    t += dt
    a = a_new
    # 判断主导成分
    term_r = Omega_r / a**4
    term_m = Omega_m / a**3
    term_L = Omega_L
    dominant = "辐射" if term_r > term_m else ("物质" if term_m > term_L else "暗能量")
    if step % 2000 == 0:
        print(f"{a:8.4f} {abs(t):14.2f} {dominant:>12s}")

print(f"\n→ 宇宙年龄 ≈ {abs(t):.1f} Gyr（观测值 13.8 Gyr）")
print(f"  早期: 辐射主导 → 物质主导 → （现在）暗能量主导")
print(f"  这就是 ΛCDM 宇宙的三个纪元。")

# LIGO 关联
print("\n=== Caltech/LIGO/Thorne 关联 ===")
print("MTW《Gravitation》= Caltech 的圣经（Thorne 合著）")
print("LIGO = Caltech+MIT 旗舰项目（Thorne/Weiss/Barish 2017 诺奖）")
print("GW150914: 双黑洞并合，辐射 3 M☉c² 能量，应变 ~10⁻²¹")
print("GW170817: 双中子星并合，开启多信使天文学时代")
print("Caltech 40m 干涉仪: 下一代探测器(Cosmic Explorer)研发平台")
```

**反直觉发现**：黑洞的最内稳定圆轨道（ISCO）位于 $r = 6GM/c^2 = 3r_s$——Newton 引力理论中所有 $r > 0$ 的圆轨道都是稳定的，但 GR 预言存在一个**不可逾越的下限**。LIGO 探测到的引力波信号，其频率扫到最大值（chirp 终止）的时刻正是两个黑洞各自到达 ISCO 并最终并合的时刻——GR 定量预测的 ISCO 直接编码在引力波信号中。

---

## 习题

### 基础题（Hartle 级别）

**P1.** 计算 Schwarzschild 半径 $r_s$ 对太阳、地球和一个 $10^9\,M_\odot$ 的超大质量黑洞。

**P2.** 用等效原理推导引力红移：从半径 $r$ 处发射的光子，在无穷远处观测到的频率红移 $z = (1 - r_s/r)^{-1/2} - 1$。

**P3.** 证明在弱场极限 $|\Phi|/c^2 \ll 1$ 下，测地线方程退化为牛顿运动方程 $\ddot{\mathbf{x}} = -\nabla\Phi$。提示：设 $g_{00} = -(1 + 2\Phi/c^2)$。

### 进阶题（Carroll / MTW 级别）

**P4.** 从 Schwarzschild 度规出发，推导光线偏转角 $\alpha = 4GM/(c^2 b)$。提示：用测地线方程或等效原理+等效折射率。

**P5.**（引力波）证明四极矩公式 $P = \frac{G}{5c^5}\langle\dddot{Q}_{ij}\dddot{Q}_{ij}\rangle$。估算双脉冲星 PSR B1913+16（Hulse-Taylor，1993 诺奖）的引力波功率，验证轨道衰变率 $\dot{P}_b$ 与观测一致。

**P6.**（宇宙学）从 Friedmann 方程出发，推导物质主导宇宙 $a(t) \propto t^{2/3}$ 和辐射主导宇宙 $a(t) \propto t^{1/2}$。

### 挑战题

**P7.**（Kerr 黑洞）写出 Kerr 度规的 Boyer-Lindquist 形式。推导事件视界半径 $r_+$ 和能层外边界 $r_{\rm ergo}$。讨论 Penrose 过程如何从旋转黑洞提取能量（上限效率 $\sim 29\%$）。

**P8.**（GW150914 分析）给定 LIGO 探测到的 chirp 信号频率演化 $f(t)$ 和 $\dot{f}(t)$，用 chirp 质量公式 $\mathcal{M} = \frac{c^3}{G}\left[\frac{5}{96}\pi^{-8/3}f^{-11/3}\dot{f}\right]^{3/5}$ 估算源系统的 chirp 质量。验证 $\mathcal{M} \approx 28\,M_\odot$。

---

## 知识地图与跨课程联系

```
广义相对论 (Ph 236)
    │
    ├──→ 等效原理 / 度规 ──→ 微分几何 (Ph 106)
    │
    ├──→ Einstein 方程 ──→ 数值相对论 (Ph 237)
    │        │
    │   Schwarzschild → 黑洞物理
    │        │
    │   Kerr → 旋转黑洞 / 吸积盘
    │
    ├──→ 引力波 ──→ LIGO (Caltech/MIT) ★★★
    │        │
    │   四极矩辐射 → 双黑洞/中子星并合
    │        │
    │   GW150914 / GW170817 → 多信使天文学
    │
    ├──→ 黑洞热力学 ──→ Hawking 辐射
    │        │              │
    │   Bekenstein-Hawking 熵 → 量子引力
    │
    └──→ 宇宙学 (Ph 237)
             │
        FLRW 度规 → Friedmann 方程
             │
        ┌────┴────┐
        大爆炸    暗能量/暗物质
        CMB       ΛCDM
             │
        暴胀 → 原初引力波 → CMB-S4 (Caltech 参与)
```

**关键连接**：
- 测地线方程 $\to$ 牛顿引力（弱场极限）
- Schwarzschild 解 $\to$ 黑洞、GPS、引力透镜
- 引力波 $\to$ LIGO（Caltech 旗舰项目）
- Kerr 黑洞 $\to$ 天体物理喷流、吸积盘
- 黑洞熵 $\to$ 量子引力/信息悖论
- Friedmann 方程 $\to$ 暗能量/暗物质（21 世纪最大谜题）
- 暴胀 $\to$ 原初引力波（CMB B 模偏振）

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| **MTW** *Gravitation* | Ch 1-6（几何直觉）、Ch 8-14（微分几何/场方程）、Ch 31-34（引力波/宇宙学）| **Caltech 圣经**，全面但庞大 |
| Carroll *Spacetime and Geometry* | Ch 1-4（流形/几何）、Ch 5-6（Schwarzschild/黑洞）、Ch 8（宇宙学）| 现代标准研究生教材 |
| Hartle *Gravity* | Ch 1-9（物理直觉优先）| 最友好的入门 |
| Maggiore *Gravitational Waves* Vol 1-2 | 全书（理论+物理+数据分析）| LIGO 研究者必备 |

> **Kip Thorne 的话**：*"Einstein's general relativity is the most beautiful of all existing physical theories."* MTW 把这份美传递给了全世界——而 Caltech 的 LIGO 团队把它变成了人类能"听"到的宇宙之声。

> **Thorne 在 GW150914 发现后**：*"This is the first time the universe has spoken to us in gravitational waves. For the first time, we can hear the universe."* Caltech 从 MTW 到 LIGO，用 40 年把 Einstein 纸上的方程变成了人类感知宇宙的全新感官。

---

*本文件属于 top-physics-courses/caltech-physics Phase 2。对应课程 Ph 236 → Ph 237。MTW 是 Caltech 的相对论圣经；LIGO 是 Caltech 对人类认识宇宙最大的贡献。*

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：广义相对论告诉你"引力不是力，而是时空的弯曲"——质量告诉时空怎么弯曲，弯曲的时空告诉物质怎么运动。宇宙学则用这套语言研究整个宇宙的过去和未来。
>
> **生活类比**：把时空想象一张蹦床。放一个保龄球（太阳）上去，蹦床凹陷。滚过的小玻璃球（地球）会绕着凹陷转圈——它"觉得"自己在走直线，其实是时空本身弯了。引力 = 时空几何。如果两个保龄球剧烈碰撞，蹦床会震出涟漪向外传——这就是**引力波**。
>
> **反直觉发现（啊哈时刻）**：
> - **黑洞不是"洞"，是时空的极端弯曲**：事件视界内，连光都跑不出去——不是引力太强拽住了光，而是时空弯曲到"所有未来"都指向中心。2025 年 LIGO 用 10 年数据**验证了 Hawking 黑洞面积定理**（视界总面积不减）。
> - **引力波让你"听"宇宙**：LIGO 测的不是光，而是时空本身的拉伸压缩——幅度只有质子直径的千分之一。2015 年人类第一次"听"到 13 亿光年外两个黑洞的并合，Caltech 的 Kip Thorne 让这件事成为现实。
> - **宇宙在加速膨胀（暗能量）**：1998 年发现宇宙膨胀在加速，暗示 68% 的宇宙是"暗能量"——一种推开空间的神秘成分。我们至今不知它是什么，这是 21 世纪物理最大谜题。

---

## 🔗 衔接：从哪来，到哪去

### 前置（你需要先会什么）
- **Ph 1a 狭义相对论**：洛伦兹变换、四维时空——GR 是把狭义相对论推广到弯曲时空
- **Ph 106 张量分析 + 微分几何**：度规、协变导数、曲率张量——GR 的数学语言
- **Ph 105 拉格朗日力学**：Einstein-Hilbert 作用量 $S=\int R\sqrt{-g}\,d^4x$，变分给出 Einstein 方程

### 广义相对论的"危机"（为什么需要升级）
- **牛顿引力的局限**：瞬时超距作用违反狭义相对论（信息不能超光速）；无法解释水星近日点进动
- **解决 → 广义相对论**（Einstein 1915）：等效原理 + 时空弯曲 = Einstein 方程 $G_{\mu\nu}=8\pi G T_{\mu\nu}/c^4$
- **新危机 1**：GR 与量子力学不兼容（量子引力）
- **新危机 2**：宇宙学发现暗物质、暗能量、宇宙加速膨胀——标准 $\Lambda$CDM 模型仍有 95% 是"暗"的
- **新方向**：多信使天文学（引力波 + 电磁波 + 中微子）+ JWST 早期宇宙观测

### 后续（GR/宇宙学通向哪里）
- Schwarzschild/Kerr → **黑洞物理 + 天体物理**（吸积盘、喷流）
- 引力波 → **LIGO / LISA / 多信使天文学**（Caltech 旗舰）
- 黑洞熵 + Bekenstein-Hawking → **量子引力 / AdS-CFT / 信息悖论**
- Friedmann 方程 → **暗物质 / 暗能量 / 暴胀 / CMB**

---

## 🏭 理论联系实际：5 个应用

1. **LIGO 引力波探测**（Caltech 旗舰，Kip Thorne 2017 诺奖）：2015-09-14 首次直接探测到引力波 GW150914（双黑洞并合），开启多信使天文学时代。截至 2026-05 的 GWTC-5.0 目录累计 **390 个引力波事件**，Caltech 从 MTW 理论到 LIGO 工程用了 40 年。
2. **GPS 相对论修正**（广义相对论日常应用）：卫星在弱引力场（钟快 $\sim 45\,\mu\text{s/day}$）+ 高速运动（钟慢 $\sim 7\,\mu\text{s/day}$）→ 净 $\sim 38\,\mu\text{s/day}$ 校正。没有 GR，GPS 一天漂 10 km。
3. **引力透镜 / 强透镜天文学**：大质量天体弯曲背景光，形成爱因斯坦环 / 多重像。JWST 用强透镜放大早期宇宙星系；弱透镜统计测量暗物质分布。
4. **黑洞照片（EHT）**：2019-04 首张 M87 黑洞阴影照片，2022 银河系中心 Sgr A* 黑洞——事件视界望远镜（EHT）直接"看见"了广义相对论预言的光子环。
5. **宇宙微波背景（CMB）+ 暴胀检验**：Planck 卫星（2013-2020）精确测量 CMB 各向异性，验证暴胀预言；CMB-S4（Caltech 参与，建设中）将搜寻原初引力波的 B 模偏振。

---

## 🔬 最新研究前沿（2024-2026）

1. **LIGO GWTC-5.0 目录 + Hawking 面积定理验证**（2025-2026）：2025-09-10 LIGO 用 10 年双黑洞并合数据，**统计性地验证了 Hawking 黑洞面积定理**（事件视界总面积不减）——这是热力学第二定律在黑洞物理中的体现。2026-05-26 发布的 GWTC-5.0 新增 161 个事件（总计 390 个），首次给出**第二代黑洞**证据、最精确的天空定位、有史以来最清晰的引力波信号。[LIGO Caltech 2025-09-10 / 2026-05-26]
2. **LIGO-India 破土动工 + AI 提升灵敏度**（2025-2026）：2026-04-23 LIGO-India 破土——世界第五个引力波天文台，将大幅改善天空定位（多三角形基线）。2025-09-08 Caltech 联合 Google DeepMind 用 **Deep Loop Shaping** AI 算法实时压制 LIGO 噪声。[LIGO Caltech 2025-09-08 / 2026-04-23]
3. **JWST 早期宇宙 + Hubble 张力加剧**（2024-2026 持续）：JWST 发现 $z>10$ 的成熟星系（JADES-GS-z14-0，$z\approx 14.3$，宇宙仅 ~3 亿岁），挑战星系形成模型；同时 JWST 对造父变星的精确测光让 Hubble 张力（$H_0$ 直接测 vs CMB 推）达到 $5\sigma$——可能是新物理（暗能量演化、早期暗能量）的信号。
4. **Kerr 黑洞的 Superradiance 与轴子搜寻**（2024-2026 活跃）：旋转黑洞的超辐射不稳定性（Penrose 过程的波动版）可以把轴子（暗物质候选）放大成"引力原子"云，再辐射引力波——2024-2025 LIGO O4 数据中搜寻这种信号，限制轴子质量窗口。
5. **NANOGrav / 脉冲星计时阵列的随机引力波背景**（2023-2026）：2023-06 NANOGrav 等团队宣布探测到 nHz 频段的随机引力波背景（可能是超大质量黑洞双星的并合嗡嗡声）。2024-2026 持续积累数据，可能在 2026-2027 区分"超大质量黑洞"vs"原初引力波"来源。

---

## 🗺️ 学习 Roadmap（Caltech 路径）

```
Ph 1c  狭义相对论 (Feynman Vol 1 Ch 15-17)  ← 大一前置
Ph 106c  张量分析 + 群论 (Mathews & Walker)  ← 大二/大三前置
Ph 105/121  拉格朗日/哈密顿力学  ← 前置（Einstein-Hilbert 作用量）
    │
    ▼
Ph 236abc  广义相对论 (Carroll *Spacetime and Geometry*; MTW 参考)  ← 研一
    │   • 掌握：微分几何、Einstein 方程、Schwarzschild 解、Kerr 解
    │   • ✅ 知识检查：推出光线偏折角 4GM/(c²b) 和近日点进动
    │
    ▼
Ph 237ab  宇宙学 + 数值相对论 (MTW Ch 27-34; Maggiore)  ← 研二
    │   • 掌握：Friedmann 方程、CMB、暗物质/暗能量、引力波四极矩公式
    │   • ✅ 知识检查：从 Friedmann 推出物质/辐射/Λ 主导宇宙的 a(t)
    │
    ▼
Ph 239  引力波物理 + LIGO (Maggiore *Gravitational Waves*)  ← 研二/研三
    │   • 掌握：引力波传播/探测原理、匹配滤波、LIGO 设计极限
    │   • ✅ 知识检查：估算双中子星并合的 chirp 质量 M_c
    │
    ▼
→ LIGO 研究组 (Caltech 旗舰：Thorne, Adhikari, Weinstein...)
→ 量子引力 / 弦理论 (Ph 240+，Caltech Schwarz、Preskill)
→ CMB-S4 / LISA (下一代宇宙学 + 空间引力波)
```

**关键里程碑**：能否用一句话说出"引力 = 时空弯曲"并用 Einstein 方程解释为什么光线会被太阳偏折（引力透镜），同时说出 LIGO 测量的本质是"时空本身的拉伸"——这是检验你是否理解 GR 与 LIGO 精髓的试金石。Caltech 从 MTW（1973 理论）到 LIGO（2015 探测）用 40 年把 Einstein 纸上的方程变成了人类感知宇宙的全新感官。Kip Thorne 说：*"For the first time, we can hear the universe."*
