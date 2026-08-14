# Cambridge Part III · General Relativity & Cosmology

> **教材**：Hawking & Ellis *The Large Scale Structure of Space-Time* — Cambridge经典巨著（Hawking 本人在剑桥写作）；Wald *General Relativity* — 现代标准教材；Dodelson *Modern Cosmology* — 宇宙学标准教材；Carroll *Spacetime and Geometry* — 现代友好入门
>
> **Cambridge 课程编号**：Part III General Relativity + Part III Cosmology
>
> **Cambridge 特色**：**剑桥是广义相对论的精神故乡**——Stephen Hawking 在剑桥 DAMTP 工作一生，Lucasian 数学教授（牛顿、Dirac 曾任此席）。Hawking 与 Penrose 的奇点定理、Hawking 辐射、Bekenstein-Hawking 熵——黑洞热力学的全部核心概念都诞生于剑桥。Part III 是剑桥的硕士级课程，深度为英国之最

---

## 目录

1. [广义相对论基础](#1-广义相对论基础)
2. [Einstein 场方程](#2-einstein-场方程)
3. [黑洞物理](#3-黑洞物理)
4. [宇宙学基础](#4-宇宙学基础)
5. [早期宇宙与扰动](#5-早期宇宙与扰动)
6. [Python 代码演示](#6-python-代码演示)
7. [Tripos 风格习题](#7-tripos-风格习题)

---

## 1. 广义相对论基础

### 1.1 等效原理

**Einstein 等效原理**：局部（时空一点附近）引力效应不可与加速度区分。精确表述：在任何引力场中，可建立**局部惯性系**，使物理定律取狭义相对论形式。

等效原理有强弱之分：

| 类型 | 内容 | 适用范围 |
|------|------|---------|
| 弱等效原理 | 惯性质量 = 引力质量 | 所有物质 |
| Einstein 等效原理 | 局部 Lorentz 不变 + 局部位置不变 | 非引力物理 |
| 强等效原理 | Einstein 原理 + 对自引力体成立 | GR 成立 |

Eötvös 实验已验证弱等效原理精度达 $10^{-15}$——这是物理学最精确检验之一。

### 1.2 弯曲时空几何

等效原理要求用**弯曲流形**描述引力。度规张量 $g_{\mu\nu}$ 编码时空几何：

$$ds^2 = g_{\mu\nu}dx^\mu dx^\nu$$

**联络**（Christoffel 符号）由度规导出：

$$\Gamma^\lambda_{\mu\nu} = \frac{1}{2}g^{\lambda\rho}(\partial_\mu g_{\nu\rho} + \partial_\nu g_{\mu\rho} - \partial_\rho g_{\mu\nu})$$

**Riemann 曲率张量**：

$$R^\rho_{\ \sigma\mu\nu} = \partial_\mu\Gamma^\rho_{\nu\sigma} - \partial_\nu\Gamma^\rho_{\mu\sigma} + \Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma}$$

曲率张量的全部信息就是"测地线的相对加速度"——即**潮汐力**。

**反直觉发现**：度规 $g_{\mu\nu}$ 看似 10 个独立分量（对称 $4\times4$），但**坐标自由度**（4 个任意函数）使物理自由度仅有 **6**。Einstein 方程进一步约束后，真空引力波只有 **2 个偏振自由度**。引力比表面看起来简单得多——10 个度规分量最终只剩 2 个物理自由度。

### 1.3 测地线方程

自由落体粒子沿**测地线**运动：

$$\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta}\frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau} = 0$$

这是"引力不是力"的数学表达——粒子在弯曲时空中走"直线"（测地线），我们感知的"引力"只是时空弯曲的表现。

---

## 2. Einstein 场方程

### 2.1 场方程

**Einstein 场方程**：

$$G_{\mu\nu} \equiv R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}$$

左边是几何（Einstein 张量），右边是物质（能动张量）。**物质告诉时空如何弯曲，时空告诉物质如何运动**（Wheeler 语）。

加入宇宙学常数 $\Lambda$：

$$G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}$$

### 2.2 Schwarzschild 解

球对称真空解（$T_{\mu\nu}=0$）：

$$ds^2 = -\left(1-\frac{2GM}{rc^2}\right)c^2dt^2 + \left(1-\frac{2GM}{rc^2}\right)^{-1}dr^2 + r^2d\Omega^2$$

**Schwarzschild 半径**（事件视界）：

$$r_s = \frac{2GM}{c^2}$$

对太阳 $r_s \approx 3$ km，对地球 $r_s \approx 9$ mm。

### 2.3 经典检验

| 检验 | 预言 | 实测精度 |
|------|------|---------|
| **近日点进动** | 水星 $\Delta\phi = 43''/$百年 | $10^{-4}$ |
| **光线偏折** | 太阳边缘 $\delta\theta = 1.75''$ | $10^{-4}$ |
| **引力红移** | $\Delta\nu/\nu = -\Delta\Phi/c^2$ | $10^{-5}$ |
| **Shapiro 延迟** | 雷达回波延迟 | $10^{-3}$ |
| **引力波** | 双星轨道衰减 | 与 PSR B1913+16 吻合 $10^{-3}$ |

**引力波**（2015 LIGO 首次直接探测）：时空度规的涟漪。线性化 GR 给出横波、张量偏振（plus "+" 和 cross "×"），传播速度 $c$。

---

## 3. 黑洞物理

### 3.1 黑洞的形成

大质量恒星坍缩或物质压缩过其 Schwarzschild 半径，形成**事件视界**——一个因果边界，内部信号无法逃逸。

**无毛定理**（Israel-Carter-Hawking）：稳态黑洞完全由三个量描述：质量 $M$、角动量 $J$、电荷 $Q$。"黑洞无毛"——无论坍缩物质的复杂细节，最终的黑洞只有这三个参数。

### 3.2 Kerr 度规

旋转黑洞由 **Kerr 度规**描述：

$$ds^2 = -\frac{\Delta}{\Sigma}(dt - a\sin^2\theta\,d\phi)^2 + \frac{\sin^2\theta}{\Sigma}[(r^2+a^2)d\phi - a\,dt]^2 + \frac{\Sigma}{\Delta}dr^2 + \Sigma\,d\theta^2$$

其中 $\Sigma = r^2 + a^2\cos^2\theta$，$\Delta = r^2 - 2GMr + a^2$，$a = J/M$。

Kerr 黑洞有两个视界（外事件视界 $r_+$ 和内 Cauchy 视界）和一个**能层**（ergosphere）——在能层内，粒子**被迫**与黑洞共转。

### 3.3 Hawking 辐射与黑洞热力学

**Hawking 的革命性发现**（1974，剑桥）：黑洞并非完全黑——它发射热辐射！

$$T_H = \frac{\hbar\kappa}{2\pi k_B c}$$

其中 $\kappa$ 为视界表面引力。对 Schwarzschild 黑洞：

$$T_H = \frac{\hbar c^3}{8\pi GMk_B}$$

**Bekenstein-Hawking 熵**：

$$S_{BH} = \frac{k_B c^3 A}{4G\hbar} = \frac{k_B A}{4\ell_P^2}$$

$A$ 为视界面积，$\ell_P = \sqrt{G\hbar/c^3} \approx 1.6\times10^{-35}$ m 为 Planck 长度。

**反直觉发现**：黑洞熵正比于**面积**而非体积！这与普通热力学系统（熵 $\propto$ 体积）根本不同。这个"面积律"是量子引力的核心线索——它暗示时空本身可能是**全息的**（holographic），三维体积的信息编码在二维边界上。't Hooft 和 Susskind 的全息原理正源于此。

**黑洞的四个定律**（与热力学平行）：

| 黑洞定律 | 热力学对应 |
|---------|-----------|
| 零律：$\kappa$ 在视界恒定 | 零律：$T$ 在平衡态恒定 |
| 一定律：$dM = \frac{\kappa}{8\pi G}dA + \Omega\,dJ + \Phi\,dQ$ | 一定律：$dU = TdS + \cdots$ |
| 二定律：$dA \geq 0$ | 二定律：$dS \geq 0$ |
| 三定律：$\kappa\to0$ 不可达 | 三定律：$T\to0$ 不可达 |

### 3.4 信息悖论

Hawking 辐射导致黑洞蒸发。问题：落入黑洞的信息（如量子态纯态）最终去了哪里？

- 若辐射是**热辐射**（混合态），信息丢失——违反量子力学幺正性
- 若信息返回辐射，需某种非热修正

这是**量子引力**最大的未解悖论。Hawking 自己在 2004 年打赌认输，承认信息可能返回——但机制至今不明。AdS/CFT 对偶（Maldacena 1997）暗示引力理论在边界上等价于无引力量子场论，强烈支持信息守恒。

---

## 4. 宇宙学基础

### 4.1 宇宙学原理与 FLRW 度规

**宇宙学原理**：宇宙在大尺度上均匀且各向同性。由此导出 **FLRW 度规**（Friedmann-Lemaître-Robertson-Walker）：

$$ds^2 = -dt^2 + a(t)^2\left[\frac{dr^2}{1-kr^2} + r^2 d\Omega^2\right]$$

$a(t)$ 为**尺度因子**，$k \in \{+1, 0, -1\}$ 为空间曲率（闭合/平直/开放）。

### 4.2 Friedmann 方程

将 Einstein 方程用于 FLRW 度规，得 **Friedmann 方程**：

$$H^2 \equiv \left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}$$

**连续性方程**（能量守恒）：

$$\dot{\rho} + 3H\left(\rho + \frac{P}{c^2}\right) = 0$$

物态方程 $P = w\rho c^2$ 下，能量密度演化：

| 成分 | $w$ | $\rho(a)$ | $a(t)$ |
|------|-----|-----------|--------|
| 辐射 | $1/3$ | $\propto a^{-4}$ | $\propto t^{1/2}$ |
| 物质 | $0$ | $\propto a^{-3}$ | $\propto t^{2/3}$ |
| 暗能量 | $-1$ | const | $\propto e^{Ht}$ |
| 曲率 | $-1/3$ | $\propto a^{-2}$ | $\propto t$ |

**反直觉发现**：宇宙膨胀中辐射密度下降**比物质更快**（$a^{-4}$ vs $a^{-3}$）——多出的一个 $a^{-1}$ 来自红移（光子能量被膨胀拉伸）。这意味着虽然早期宇宙是**辐射主导**，但膨胀后必然转为**物质主导**，最终（当前！）进入**暗能量主导**。三种主导时代的更迭完全由物态方程决定。

### 4.3 宇宙的成分

当前宇宙（Planck 2018 卫星数据）：

| 成分 | 占比 ($\Omega$) | 物理本质 |
|------|----------------|---------|
| 暗能量 | $\approx 0.69$ | 未知（$\Lambda$？标量场？） |
| 暗物质 | $\approx 0.26$ | 未知（WIMP？轴子？） |
| 重子物质 | $\approx 0.05$ | 质子、中子（仅 5%！） |
| 辐射 | $\approx 5\times10^{-5}$ | CMB 光子、中微子 |

**普通物质仅占宇宙的 5%**——95% 的宇宙是未知的。这是现代物理最深刻的未解之谜之一。

### 4.4 哈勃定律

$$v = H_0 d$$

$H_0 \approx 67$–$73$ km/s/Mpc（Hubble 常数，存在"Hubble 紧张"争议：Planck 给 67，局域测量给 73）。

---

## 5. 早期宇宙与扰动

### 5.1 大爆炸与热历史

宇宙从高温高密度状态膨胀冷却：

| 时代 | 温度 | 事件 |
|------|------|------|
| Planck | $10^{32}$ K | 量子引力 |
| 大统一 | $10^{28}$ K | 重子生成？ |
| 电弱 | $10^{15}$ K | Higgs 对称破缺 |
| QCD | $10^{12}$ K | 夸克禁闭 |
| 核合成 (BBN) | $10^9$ K | 轻核合成（H, He, Li） |
| 复合 | $3000$ K | 原子形成，CMB 退耦 |

### 5.2 宇宙微波背景 (CMB)

**CMB** 是宇宙 38 万岁时（复合时期）留下的光子"化石"。其**黑体谱**（$T = 2.7255$ K）完美程度达 $10^{-5}$，是大爆炸理论最强证据。

CMB 的**温度涨落** $\delta T/T \sim 10^{-5}$ 编码了早期宇宙的密度扰动，这些扰动在引力作用下增长，形成今天的大尺度结构（星系、星系团）。

**声学峰**（CMB 功率谱中的振荡峰）是早期宇宙**光子-重子等离子体声学振荡**的遗迹。峰的位置和高度精确确定了宇宙学参数（$\Omega_b, \Omega_m, \Omega_\Lambda, H_0, n_s$ 等）。

### 5.3 暴胀

**暴胀理论**（Guth 1980, Linde 1982）：宇宙在极早期经历指数膨胀 $a \propto e^{Ht}$，持续约 $10^{-36}$–$10^{-32}$ 秒，尺度增长 $e^{60}$ 倍以上。

暴胀解决三大问题：

1. **平坦性问题**：暴胀把曲率拉平（$\Omega \to 1$）
2. **视界问题**：暴胀使现今因果断开的区域曾经接触
3. **磁单极问题**：暴胀稀释了拓扑缺陷

**暴胀的量子涨落**被指数膨胀拉伸到宇宙学尺度，成为大尺度结构的**种子**。暴胀预言原初扰动谱近似**尺度不变**（$n_s \approx 1$），且产生**原初引力波**——后者可通过 CMB **B 模偏振**探测（BICEP/Keck 持续搜寻中）。

**反直觉发现**：暴胀有一个惊人的推论——**永恒暴胀**。量子涨落使某些区域持续暴胀，产生无穷多的"口袋宇宙"，我们只是其中一个。这暗示存在**多重宇宙**（multiverse），物理常数在不同宇宙中可能不同（人择原理）。这个推论是否属于科学（不可检验？）至今争论不休。

---

## 6. Python 代码演示

> 纯标准库实现：Schwarzschild 测地线 + Friedmann 膨胀 + Hawking 温度。

```python
"""
Cambridge Part III GR & Cosmology — 演示
1. Schwarzschild 时空光子测地线 (光线偏折)
2. Friedmann 宇宙膨胀 a(t): 物质/辐射/Λ主导
3. Hawking 温度 vs 黑洞质量 (蒸发)
"""
import math

# ============================================================
# 实验1: Schwarzschild 光子轨道 (光线引力偏折)
# ============================================================
print("=" * 60)
print("实验1: Schwarzschild 光子测地线 — 光线偏折")
print("=" * 60)
# 取 r_s = 2GM/c² = 1 (几何单位)
# 光子方程: d²u/dφ² + u = 3u²/2  (u = r_s/r 的约化方程, GM/r = u/... )
# 简化: 用 (1/r) 的方程, 真空测地线
# 实际: d²u/dφ² + u = (3/2) r_s u²  where u = 1/r

def photon_deflection(b_impact, dphi=0.001):
    """积分光子轨道, b=碰撞参数 (单位 r_s)
    光子从远方来, 最接近点 r_min, 偏折角 = φ_out - π/2 对齐
    返回总偏折角 (弧度)
    方程: u'' + u = 1.5 r_s u²,  u=1/r,  r_s=1
    """
    r_s = 1.0
    # 初始: 光子从 x=-∞, y=b, 沿+x方向 → u 小, du/dφ = -b⁻¹ (近似)
    # 在远场 r 大, u = sin(φ)/b → du/dφ = cos(φ)/b
    # 起点 φ≈0, u≈0 (r≈∞)... 从近心点积分更稳定
    # 近心点 r0 (u=1/r0), du/dφ=0
    r0 = b_impact  # 近似, 近心点≈碰撞参数(大 b 时)
    u0 = 1.0 / r0
    u, dudphi = u0, 0.0
    
    # 积分到 r→∞ (u→0), 从近心点向外
    phi = 0.0
    max_phi = 4 * math.pi
    while phi < max_phi:
        k1 = dudphi
        l1 = -u + 1.5 * r_s * u**2
        u_mid = u + k1 * dphi / 2
        dudphi_mid = dudphi + l1 * dphi / 2
        l2 = -u_mid + 1.5 * r_s * u_mid**2
        u += dudphi_mid * dphi
        dudphi += l2 * dphi
        phi += dphi
        if u < 1e-6:  # r→∞, 光子逃出
            break
    # 偏折角: 总 φ (从近心点到出射) 减去直线 π/2
    total_deflection = 2 * phi - math.pi  # 两侧对称
    return total_deflection

print("  光子方程 u'' + u = (3/2)r_s·u², 取 r_s=1\n")
print(f"  {'碰撞参数 b/r_s':<15} {'数值偏折 δ':<14} {'GR预言 2r_s/b':<14} {'比值'}")
# GR 弱场: δθ ≈ 2r_s/b = 4GM/(bc²)
for b in [100, 50, 20, 10, 5, 3]:
    delta_num = photon_deflection(b, dphi=0.0005)
    delta_gr = 2.0 / b  # 2 r_s / b
    ratio = delta_num / delta_gr
    print(f"  {b:<15} {delta_num:<14.6f} {delta_gr:<14.6f} {ratio:.4f}")

print(f"\n  弱场极限 (b≫r_s): δθ → 2r_s/b = 4GM/(bc²)")
print(f"  太阳边缘 (b=R☉): δθ = 1.75″  (1919 Eddington 验证)")
print(f"  强场 (b→r_s): 偏折发散 → 光子俘获")

# ============================================================
# 实验2: Friedmann 宇宙膨胀 a(t)
# ============================================================
print("\n" + "=" * 60)
print("实验2: Friedmann 宇宙膨胀  a(t)")
print("=" * 60)
# 平直宇宙 (k=0): (ȧ/a)² = (8πG/3)ρ
# 物质主导: a ∝ t^(2/3)
# 辐射主导: a ∝ t^(1/2)
# Λ主导:   a ∝ exp(Ht)

def friedmann_integrate(w_eff, a0=0.01, t0=0, dt=0.01, n_steps=10000):
    """积分 ȧ/a = H₀√(Ω a^{-3(1+w)}), 取 H₀=1, Ω=1 (平直)
    da/dt = H₀·a^{1 - 3(1+w)/2} = a^{-(1+3w)/2}
    """
    H0 = 1.0
    a = a0
    t = t0
    results = [(t, a)]
    for _ in range(n_steps):
        dadt = H0 * a**(-(1 + 3*w_eff)/2)
        a += dadt * dt
        t += dt
        results.append((t, a))
    return results

print("  平直单成分宇宙 (H₀=1, Ω=1):\n")
print(f"  {'成分':<10} {'w':<6} {'a(t) 解析':<16} {'a(t) 数值(2t)':<14}")
for name, w in [("辐射", 1/3), ("物质", 0.0), ("曲率", -1/3)]:
    sol = friedmann_integrate(w, a0=0.1, t0=1.0, dt=0.01, n_steps=500)
    # 取 t=2.0 附近的 a
    a_num = None
    for t, a in sol:
        if abs(t - 2.0) < 0.02:
            a_num = a
            break
    if w == 1/3:
        a_ana = "t^{1/2}"
        ratio = a_num / math.sqrt(2.0) * math.sqrt(1.0)  # 归一化
    elif w == 0:
        a_ana = "t^{2/3}"
        ratio = a_num / (2.0**(2/3))
    else:
        a_ana = "t^1"
        ratio = a_num / 2.0
    print(f"  {name:<10} {w:<6} {a_ana:<16} {a_num:<14.4f} 比值={ratio:.4f}")

print(f"\n  Λ主导: a(t) = a₀·exp(H₀t) → 加速膨胀")
print(f"  当前宇宙: Ω_Λ≈0.69 → 正在进入指数膨胀阶段")

# ============================================================
# 实验3: Hawking 温度与黑洞蒸发
# ============================================================
print("\n" + "=" * 60)
print("实验3: Hawking 辐射 — 黑洞质量与温度")
print("=" * 60)
# T_H = ℏc³/(8πGMk_B)
# 取常数: ℏc³/(8πGk_B) = 1.227×10²³ K·kg

hbar_c3_over_8piGkB = 1.227e23  # K·kg

def hawking_temp(M_kg):
    return hbar_c3_over_8piGkB / M_kg

def schwarzschild_radius(M_kg):
    G = 6.674e-11
    c = 3e8
    return 2*G*M_kg / c**2

print(f"  T_H = ℏc³/(8πGMk_B),  r_s = 2GM/c²\n")
print(f"  {'黑洞':<20} {'M (kg)':<15} {'T_H (K)':<14} {'r_s':<14}")
cases = [
    ("太阳质量", 2e30),
    ("地球质量", 6e24),
    ("月球质量", 7e22),
    ("Mt Everest", 1e15),
    ("人(70kg)", 70),
]
for name, M in cases:
    T = hawking_temp(M)
    rs = schwarzschild_radius(M)
    if rs < 1e-3:
        rs_str = f"{rs:.2e} m"
    else:
        rs_str = f"{rs:.2e} m"
    print(f"  {name:<20} {M:<15.2e} {T:<14.4e} {rs_str}")

print(f"\n  反直觉:")
print(f"  • 太阳质量黑洞 T ≈ 60 nK — 比宇宙背景(2.7K)冷10⁸倍!")
print(f"  • 小黑洞更热 → 蒸发更快 → 质量越小温度越高 → 失稳爆炸")
print(f"  • 当前宇宙中, 只有 M < 10¹² kg 的原初黑洞在蒸发")
print(f"  • Bekenstein-Hawking 熵 S = k_B·A/(4ℓ_P²)")
Msun = 2e30
G, c, hbar, kB = 6.674e-11, 3e8, 1.055e-34, 1.381e-23
lp = math.sqrt(G*hbar/c**3)
A_sun = 4*math.pi*(schwarzschild_radius(Msun))**2
S_BH = kB * A_sun / (4*lp**2)
print(f"  • 太阳质量黑洞熵 S ≈ {S_BH:.2e} J/K")
print(f"  • 远超太阳热力学熵 (~10⁴⁴ J/K) — 黑洞是宇宙最大熵载体!")
```

---

## 7. Tripos 风格习题

### 习题 1（Part III 难度）：测地线方程与 Newton 极限

证明 Schwarzschild 度规中，弱场低速极限下测地线方程退化为 Newton 引力。

<details>
<summary>解答</summary>

Schwarzschild 度规（弱场 $r\gg r_s$）：

$$g_{00} = -(1-r_s/r) \approx -(1 - 2GM/rc^2)$$

定义 Newton 势 $\Phi = -GM/r$，故 $g_{00} \approx -(1 + 2\Phi/c^2)$。

低速极限 $dx^i/d\tau \ll c\,dt/d\tau$，测地线方程的时间分量：

$$\frac{d^2x^0}{d\tau^2} + \Gamma^0_{00}\left(\frac{dx^0}{d\tau}\right)^2 = 0$$

空间分量（主要项）：

$$\frac{d^2x^i}{d\tau^2} + \Gamma^i_{00}\left(\frac{dx^0}{d\tau}\right)^2 = 0$$

计算 $\Gamma^i_{00} = \frac{1}{2}g^{ij}(-\partial_j g_{00}) = \frac{1}{c^2}\partial_i\Phi$（用 $g^{ij}\approx\delta^{ij}$）。

$dx^0/d\tau = c\,dt/d\tau \approx c$（低速）。故：

$$\frac{d^2x^i}{dt^2} = -\Gamma^i_{00}c^2 = -\partial_i\Phi$$

这正是 **Newton 引力方程** $\ddot{\mathbf{r}} = -\nabla\Phi$。$\square$

**关键**：$g_{00} \approx -(1+2\Phi/c^2)$ 是 GR 与 Newton 的桥梁。
</details>

### 习题 2（Part III 难度）：Hawking 辐射

(a) 用量纲分析推导 Schwarzschild 黑洞的 Hawking 温度对 $M$ 的依赖。
(b) 解释为什么黑洞有负热容。

<details>
<summary>解答</summary>

(a) $T_H$ 应由 $G, \hbar, c, k_B, M$ 组成（唯一带量纲的参数）。量纲分析：

$$[T] = K, \quad [M] = \text{kg}, \quad [G] = \text{m}^3\text{kg}^{-1}\text{s}^{-2}, \quad [\hbar] = \text{J·s}, \quad [c] = \text{m/s}$$

设 $T \propto M^\alpha G^\beta \hbar^\gamma c^\delta k_B^{-1}$。解量纲方程得 $\alpha=-1, \beta=-1, \gamma=1, \delta=3$：

$$T_H = \frac{\hbar c^3}{8\pi G M k_B} \propto \frac{1}{M}$$

精确系数需弯曲时空量子场论计算。$\square$

(b) $T_H \propto 1/M$。黑洞能量 $E = Mc^2$，故 $dE/dT = Mc^2 \cdot dM/dT < 0$（因 $T\propto 1/M$）。**负热容**！

物理意义：黑洞辐射失去质量 → $M$ 减小 → $T$ 升高 → 辐射更快 → $M$ 更小……**失控**。这是引力系统（自吸引）的普遍特征——恒星也有负热容（Kelvin-Helmholtz 机制）。负热容系统不能与正热容热浴稳定平衡，导致黑洞最终爆炸蒸发。$\square$
</details>

### 习题 3（Part III 难度）：Friedmann 方程

平直物质主导宇宙求 $a(t)$ 和年龄 $t_0$。

<details>
<summary>解答</summary>

平直 ($k=0$)、$\Lambda=0$、物质主导 ($\rho = \rho_0 a^{-3}$)：

$$\dot{a}^2 = \frac{8\pi G\rho_0}{3}\frac{1}{a} = \frac{H_0^2}{a}$$

（用了 $\rho_0 = 3H_0^2/(8\pi G)$，归一化 $a(t_0)=1$）。

$$a^{1/2}da = H_0\,dt \implies \frac{2}{3}a^{3/2} = H_0 t$$

$$a(t) = \left(\frac{3H_0 t}{2}\right)^{2/3}, \qquad t_0 = \frac{2}{3H_0}$$

$H_0 \approx 70$ km/s/Mpc $\implies t_0 \approx 9.3$ Gyr。但实测宇宙年龄 $\approx 13.8$ Gyr——偏短的 $t_0$ 是暗能量存在的证据之一（$\Lambda$ 使膨胀加速，"拉长"了宇宙年龄）。$\square$
</details>

### 习题 4（Part III 预习）：能量条件

列出经典能量条件并解释其在奇点定理中的作用。

<details>
<summary>解答</summary>

| 能量条件 | 数学表述 | 物理含义 |
|---------|---------|---------|
| 弱 (WEC) | $T_{\mu\nu}u^\mu u^\nu \geq 0$ | 观测者测正能量密度 |
| 强 (SEC) | $(T_{\mu\nu}-\frac{1}{2}Tg_{\mu\nu})u^\mu u^\nu \geq 0$ | 引力普遍吸引 |
| 主导 (DEC) | WEC + $T^{\mu}_{\ \nu}u^\nu$ 类时 | 能量流不超光速 |
| 零 (NEC) | $T_{\mu\nu}k^\mu k^\nu \geq 0$ ($k$ 类光) | 光沿类光线正能量 |

**Hawking-Penrose 奇点定理**（剑桥的核心贡献）：在合理能量条件（NEC + 某全局假设如正能量）下，广义相对论预言时空存在**不完备测地线**——即奇点不可避免。

奇点定理的威力：它**不需要知道物质细节**，只需能量条件。它证明了黑洞中奇点不可避免，且大爆炸不可避免（在经典 GR 中）。但奇点处 GR 失效——需要量子引力。$\square$

**注**：暗能量（$w<-1$）违反 SEC，量子场论（Casimir 效应）可违反 WEC——这些是经典能量条件的边界。
</details>

---

## Cambridge 与广义相对论

### Stephen Hawking 与剑桥 GR 传统

**Cambridge 是广义相对论和黑洞物理的精神中心**。Stephen Hawking（1942–2018）在剑桥 DAMTP（应用数学与理论物理系）工作一生，1979–2009 年任 **Lucasian 数学教授**——这一教席曾属于牛顿（1669）和 Dirac（1932）。

Hawking 的核心贡献全部诞生于剑桥：

1. **奇点定理**（1970，与 Penrose）：证明经典 GR 中奇点不可避免
2. **Hawking 辐射**（1974）：黑洞发射热辐射——量子场论与弯曲时空的交汇
3. **Bekenstein-Hawking 熵**：黑洞热力学的奠基

### Penrose 与剑桥的联系

**Roger Penrose**（Oxford，但与剑桥深度合作）：用拓扑学方法（Penrose 图、共形紧致化）革新了 GR 的全局结构分析。2020 年诺奖表彰他"证明黑洞是 GR 的稳健预言"。Penrose-Hawking 奇点定理是两人合作的巅峰——Oxford 的数学严格与剑桥的物理直觉完美结合。

### Lucasian 教席传承

Lucasian 数学教授序列本身就是物理学史：

| 年份 | 教授 | 贡献 |
|------|------|------|
| 1669 | **Isaac Newton** | 经典力学、万有引力、微积分 |
| 1828 | **Charles Babbage** | 计算机先驱 |
| 1932 | **Paul Dirac** | 量子力学、反物质 |
| 1979 | **Stephen Hawking** | 黑洞、量子引力 |
| 2009 | **Michael Green** | 弦理论（弦理论创始人之一） |

从牛顿到 Green，Lucasian 教席串起了从经典引力到量子引力的完整脉络——剑桥是引力理论千年传承的载体。

### 当代剑桥宇宙学

剑桥的 **Institute of Astronomy** 和 DAMTP 是宇宙学研究的世界中心：

- **George Efstathiou**：CMB 分析先驱，Planck 卫星科学团队领导
- **Jeremiah Ostriker**（曾访学）：暗能量理论
- 剑桥主导的宇宙学模拟（如 IllustrisTNG 部分）和 CMB 数据分析

Part III 的 GR 与宇宙学课程直接反映这种研究前沿——学生从 Schwarzschild 解一路学到暴胀理论和黑洞信息悖论，这是全球最深入的本科/硕士级 GR 课程之一。

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Carroll Ch 1-5 | 流形 + 测地线 + 场方程 | 现代友好入门 |
| Carroll Ch 6-7 | Schwarzschild + 黑洞 | Part III 核心 |
| Wald Ch 1-6 | 微分几何 + 场方程 | 严格数学表述 |
| Wald Ch 9-12 | 因果结构 + 奇点定理 | Hawking-Ellis 传统 |
| Hawking & Ellis | 全书 | 经典巨著, 奇点定理原始出处 |
| Dodelson Ch 2-4 | Friedmann + CMB | 宇宙学标准教材 |
| Dodelson Ch 7-10 | 扰动 + 暴胀 | 大尺度结构 |
| Weinberg *Cosmology* | 全书 | 深入理论 |
| Mukhanov *Physical Foundations* | 暴胀 | 早期宇宙专著 |

---

**版本**：v1.0 (2026-08-12) · Cambridge Part III General Relativity & Cosmology


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：引力不是一种"力"，而是**时空本身的弯曲**——质量告诉时空怎么弯，弯曲的时空告诉物质怎么走（惠勒语）。
>
> **生活类比**：蹦床上的保龄球。球把蹦床压出一个凹坑，旁边滚过的小球会被凹坑吸引而转弯。宇宙里，太阳压凹了时空，地球沿着凹坑里的"直线"（测地线）转动——只是因为时空本身是弯的，这条"直线"看起来成了椭圆。
>
> **反直觉发现（啊哈时刻）**：宇宙在膨胀，但**没有膨胀进"什么东西"里**——是空间本身在拉伸，星系只是彼此远离。更妙的是，膨胀还在**加速**，驱动它的是一种谁也看不见的"暗能量"（占宇宙能量 ~68%）。

---

## 🔗 衔接：从哪来，到哪去

- **前置知识**：**狭义相对论**（Topic 1 §6）、**张量分析/微分几何**（Part III 数学）、经典变分法、**电动力学**（Topic 2，规范结构类比）
- **危机（广义相对论为何诞生）**：牛顿引力"瞬时超距作用"与狭义相对论（信息不能超光速）矛盾；水星近日点进动无法精确解释 → 爱因斯坦用弯曲时空重写引力
- **新危机**：
  - 引力**无法量子化**（与其他三种力不兼容）
  - 暗物质 / 暗能量本质未知
  - 奇点（黑洞内部、大爆炸起点）标志理论失效
  - 宇宙加速膨胀的机制
- **后续去向**：**量子引力**（弦论 / 圈量子引力）、宇宙学（暴胀、原初引力波、CMB）、**黑洞信息悖论**（全息原理）

---

## 🏭 理论联系实际：5 个现代应用

1. **GPS 卫星定位**：必须做相对论修正——卫星钟既受狭义相对论（速度变慢）又受广义相对论（引力变快）影响，每天累计误差约 38 μs，若不修正定位每天漂移约 10 km。
2. **引力波天文学**：LIGO/Virgo/KAGRA 探测双黑洞、双中子星并合，开启"多信使天文学"（引力波 + 光 + 中微子）。
3. **黑洞成像**：事件视界望远镜（EHT）2019 拍到 M87* 黑洞阴影，2022 拍到银河系中心 Sgr A*。
4. **引力透镜**：前景星系/星系团弯曲背景光，放大极远星系——哈勃/JWST 的"宇宙放大镜"。
5. **精确宇宙学**：宇宙学常数 Λ / 暗能量驱动加速膨胀，主导宇宙命运（大冻结 vs 大撕裂）。

---

## 🔬 最新研究前沿（2024-2026）

1. **纳赫兹引力波背景（NANOGrav 等）**：2023–2024 北美 NANOGrav、欧洲 EPTA、中国 CPTA、澳洲 PPTA 脉冲星计时阵列**联合**探测到纳赫兹频段的随机引力波背景，源自超大质量黑洞双星旋近（*ApJ Letters* 等, 2023；2024 后续确认）。
2. **JWST 早期宇宙挑战**：2024 JADES 等深场观测发现大爆炸后 < 5 亿年就存在出乎意料成熟、明亮的星系，挑战星系形成的 ΛCDM 标准图像。
3. **DESI 暗能量演化**：2024 DESI 重子声学振荡（BAO）巡天结果暗示暗能量状态方程 $w(a)$ 可能**随时间演化**（动态暗能量），动摇"宇宙学常数"假设。
4. **黑洞信息悖论**：2024–2025 全息"岛公式"（island formula）在解决霍金辐射纯度问题上取得共识性进展，连接量子信息与引力。
5. **剑桥 Kavli 宇宙学研究所**：剑桥深度参与 **Euclid**（2023 发射，2024 首批数据，弱引力透镜暗能量测绘）、**SKA**（21 cm 宇宙学）、**CMB-S4**、**Simons Observatory**。

---

## 🗺️ 学习 Roadmap（Cambridge Tripos 路径）

| 阶段 | 课程 | 你应当能做到 |
|------|------|------------|
| （前置） | Part IB/II Special Relativity + Tensors + Classical Field Theory | 掌握洛伦兹几何、张量微积分 |
| **Part III** | General Relativity | 微分几何（流形、度规、曲率）、爱因斯坦方程、Schwarzschild 解、线性化引力 |
| **Part III** | Cosmology | FRW 宇宙学、暴胀、结构形成、CMB 物理 |
| **Part III** | Gravitational Waves / Black Holes | 数值相对论、黑洞热力学 |
| （研究） | Kavli Institute for Cosmology / IoA | Euclid, SKA, CMB-S4, 理论宇宙学 |

**知识检查三问**：
1. 为什么 GPS 必须做相对论修正，否则定位每天漂移 ~10 km？
2. 为什么宇宙在**加速**膨胀？什么在驱动它？
3. 黑洞信息悖论是什么？为什么它指向量子引力？
