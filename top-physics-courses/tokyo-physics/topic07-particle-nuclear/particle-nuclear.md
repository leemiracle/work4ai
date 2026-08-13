# 東京大学物理系 Phase 2 · 素粒子物理学と核物理学 深度講義

> **课程映射**（SURVEY §9 東大）：素粒子物理学 + 原子核物理学
> **教材**：Schwartz, Matthew. *Quantum Field Theory and the Standard Model*（素粒子指定）+ Halzen & Martin *Quarks and Leptons*（日文译本『クォークとレプトン』）+ Griffiths *Introduction to Elementary Particles* 2ed + Krane *Introductory Nuclear Physics*
> **定位**：从标准模型的完整拼图到核力与核结构——这是东京大学「計算伝統」在高能物理的巅峰体现。**小柴昌俊（Koshiba, 2002 诺奖）**和**梶田隆章（Kajita, 2015 诺奖）**的中微子振荡发现，正是素粒子物理实验在東大体系下的最高成就。

---

## 0. 導引：标准模型为何是「物理学的最高精度理论」

标准模型（Standard Model, SM）用一个 Lagrangian 量统一了三种基本相互作用：

$$\underbrace{\text{电磁力 } U(1)_Y}_{\text{QED}} + \underbrace{\text{弱力 } SU(2)_L}_{\text{电弱统一}} + \underbrace{\text{强力 } SU(3)_c}_{\text{QCD}}$$

它的预言精度达到 $10^{-12}$ 量级（电子反常磁矩 $g-2$），是人类最精确的物理理论。但标准模型不包含引力，且中微子振荡证明中微子有质量（SM 的最小版本中中微子无质量）——所以 SM 是一个**极好的有效理论，但不是终极理论**。

本章按 **费米子世代 → 规范相互作用 → 强子与核 → 中微子振荡 → 超越 SM** 展开，每一节配 Python 数值验证。

---

## 1. 素粒子の動物園（Particle Zoo & Standard Model）

### 1.1 基本费米子（三代）

| 世代 | 轻子（自旋 1/2）| 夸克（自旋 1/2）|
|------|-----------------|-----------------|
| I | $e^-$ (0.511 MeV), $\nu_e$ | $u$ (2.2 MeV), $d$ (4.7 MeV) |
| II | $\mu^-$ (105.7 MeV), $\nu_\mu$ | $c$ (1.28 GeV), $s$ (96 MeV) |
| III | $\tau^-$ (1777 MeV), $\nu_\tau$ | $t$ (173 GeV), $b$ (4.18 GeV) |

所有夸克带色荷（红/绿/蓝，3 种），轻子不带色荷。

### 1.2 规范玻色子（力的传递者）

| 相互作用 | 玻色子 | 自旋 | 质量 | 理论 |
|----------|--------|------|------|------|
| 电磁 | $\gamma$（光子）| 1 | 0 | QED ($U(1)$) |
| 弱 | $W^\pm, Z^0$ | 1 | 80.4, 91.2 GeV | 弱 ($SU(2)_L$) |
| 强 | $g$（胶子, 8 种）| 1 | 0 | QCD ($SU(3)_c$) |
| (引力) | (引力子?) | 2 | 0 | GR (不在 SM) |

### 1.3 Higgs 粒子（2012 发现）

Higgs 玻色子（$H$, 自旋 0, 质量 125 GeV）是电弱对称性自发破缺的产物。它赋予 $W, Z$ 和费米子质量。2012 年 CERN LHC 发现，2013 年 Englert–Higgs 获诺奖。

### 1.4 标准模型 Lagrangian 量

$$\mathcal{L}_{\text{SM}} = -\frac{1}{4}F_{\mu\nu}F^{\mu\nu} + i\bar{\psi}\gamma^\mu D_\mu\psi + (D_\mu\phi)^\dagger(D^\mu\phi) - V(\phi) - \bar{\psi}Y\phi\psi$$

其中 $D_\mu = \partial_\mu + igA_\mu$ 是规范协变导数，$\phi$ 是 Higgs 场，$V(\phi) = \mu^2\phi^\dagger\phi + \lambda(\phi^\dagger\phi)^2$ 是 Higgs 势。

> **一句话**：标准模型 = 规范对称性 $SU(3)\times SU(2)\times U(1)$ 决定一切相互作用 + Higgs 机制赋予质量。这是 20 世纪物理学的最高成就。

---

## 2. 電弱統一理論（Electroweak Unification）

### 2.1 弱相互作用的特点

弱力的特征：
- **V–A 结构**：只有左手费米子参与弱相互作用（宇称最大化破缺！）。
- **短力程**：$W, Z$ 有质量（$\sim 80$–$91$ GeV），力程 $\sim \hbar/(Mc) \sim 10^{-18}$ m。
- **味改变**：$W^\pm$ 可改变夸克味（$d \to u + W^-$，$\beta$ 衰变）。

### 2.2 Glashow–Weinberg–Salam 模型

电磁与弱统一为 $SU(2)_L \times U(1)_Y$ 规范理论。对称性自发破缺后：

$$\begin{pmatrix}\gamma\\Z^0\end{pmatrix} = \begin{pmatrix}\cos\theta_W & \sin\theta_W\\-\sin\theta_W & \cos\theta_W\end{pmatrix}\begin{pmatrix}B^0\\W^0\end{pmatrix}$$

**Weinberg 角** $\theta_W$：$\sin^2\theta_W \approx 0.231$。

对称性破缺后 $W, Z$ 获得质量：

$$M_W = \frac{gv}{2}, \quad M_Z = \frac{v\sqrt{g^2+g'^2}}{2}, \quad \frac{M_W}{M_Z} = \cos\theta_W$$

$v \approx 246$ GeV 是 Higgs 真空期望值。

### 2.3 弱混合矩阵（CKM 矩阵）

三代夸克之间的弱相互作用由 **Cabibbo–Kobayashi–Maskawa (CKM) 矩阵**描述：

$$\begin{pmatrix}d'\\s'\\b'\end{pmatrix} = V_{\text{CKM}}\begin{pmatrix}d\\s\\b\end{pmatrix}$$

> **小林誠・益川敏英（2008 诺奖）**：1973 年提出三代夸克模型和 CKM 矩阵，预言 $CP$ 对称破缺的起源。这是**东京大学理论物理对标准模型的最重要贡献**——从一个 $3\times3$ 幺正矩阵的复相位出发，解释了宇宙中物质-反物质不对称的微观起源。

---

## 3. 量子色力学 QCD（Quantum Chromodynamics）

### 3.1 色荷与胶子

夸克带三种色荷（红 $r$、绿 $g$、蓝 $b$），胶子带色-反色（8 种独立胶子）。QCD 的规范群是 $SU(3)_c$。

### 3.2 渐近自由与色禁闭

**渐近自由**（Asymptotic Freedom, Gross/Politzer/Wilczek 2004 诺奖）：高能（短距离）下夸克间耦合常数趋于零——夸克在强子内「自由」。

$$\alpha_s(Q^2) = \frac{12\pi}{(33-2n_f)\ln(Q^2/\Lambda^2_{\text{QCD}})}$$

$\Lambda_{\text{QCD}} \approx 200$ MeV 是 QCD 标度。$Q^2 \to \infty$ 时 $\alpha_s \to 0$。

**色禁闭**（Confinement）：低能（长距离）下耦合增强，夸克无法被单独分离——永远束缚在强子（无色态）中。试图拉开两个夸克 $\Rightarrow$ 从真空中产生新夸克对 $\Rightarrow$ 形成强子喷注（jet）。

> **反直觉**：强核力在短距离反而最弱（渐近自由），在长距离无限增强（禁闭）——与电磁力的距离行为完全相反！

### 3.3 强子谱

- **介子**（Meson, 夸克-反夸克 $q\bar{q}$）：$\pi^+ = u\bar{d}$, $K^+ = u\bar{s}$, $J/\psi = c\bar{c}$。
- **重子**（Baryon, 三夸克 $qqq$）：$p = uud$, $n = udd$, $\Omega^- = sss$。

质子质量 $\approx 938$ MeV，远大于组成夸克质量之和 $2m_u + m_d \approx 9$ MeV——**质子质量的 99% 来自 QCD 结合能（胶子场能量 + 海夸克）**。这是 $E = mc^2$ 在强子物理中的壮观体现。

---

## 4. 中性子 $\beta$ 衰变と核力

### 4.1 $\beta$ 衰变

自由中子衰变：$n \to p + e^- + \bar{\nu}_e$。

微观过程：$d \to u + W^- \to u + e^- + \bar{\nu}_e$（下夸克经 $W^-$ 变为上夸克）。

Fermi 黄金法则给出衰变率 $\Gamma \propto G_F^2\,\Delta m^5$（$G_F$ 是 Fermi 常数, $\Delta m = m_n - m_p \approx 1.29$ MeV）。

$$\tau_n \approx \frac{K}{G_F^2(1+3g_A^2)\Delta m^5 f} \approx 880\text{ s}$$

中子寿命是核物理/宇宙学的重要参数（大爆炸核合成 BBN 依赖它）。

### 4.2 核力与汤川秀树的介子理论

**汤川秀樹（Yukawa, 1949 诺奖）**：1935 年预言核力由交换介子传递——类比电磁力交换光子，核力交换有质量的 $\pi$ 介子。力程 $r \sim \hbar/(m_\pi c)$：

$$V(r) = -\frac{g^2}{4\pi}\frac{e^{-m_\pi c r/\hbar}}{r}$$

$\pi$ 介子质量 $m_\pi \approx 140$ MeV $\Rightarrow$ 力程 $\approx 1.4$ fm。1947 年 $\pi$ 介子在宇宙线中被发现，完美验证了汤川的预言。

> **这是东京大学理论物理的第一个世界级成就**——汤川从量纲分析出发，用不确定性原理 $\Delta E\Delta t \sim \hbar$ 估算交换粒子的质量，是物理直觉与计算结合的典范。

### 4.3 核结构：壳模型

原子核的**壳模型**（Mayer/Jensen 1963 诺奖）：核子在平均势中填充能级，类似原子中的电子壳层。幻数（magic numbers）$2, 8, 20, 28, 50, 82, 126$ 对应闭合壳层，特别稳定。

结合能的半经验公式（Weizsäcker 公式, 液滴模型）：

$$B(A,Z) = a_v A - a_s A^{2/3} - a_c\frac{Z(Z-1)}{A^{1/3}} - a_a\frac{(A-2Z)^2}{A} + \delta(A,Z)$$

各项：体积能、表面能、Coulomb 排斥、对称能（ favor $N = Z$）、配对能（偶-偶核更稳定）。

---

## 5. 中微子振動（Neutrino Oscillation）—— 東大诺奖的核心

### 5.1 中微子振荡的物理

中微子有三种味（$\nu_e, \nu_\mu, \nu_\tau$），但它们的质量本征态（$\nu_1, \nu_2, \nu_3$）不同。两者由 **PMNS 矩阵**联系（类似 CKM）：

$$|\nu_\alpha\rangle = \sum_i U_{\alpha i}|\nu_i\rangle$$

中微子在传播中，不同质量本征态有不同相速度 $\Rightarrow$ 味随距离周期性变化——**中微子振荡**。

**两味简化振荡概率**：

$$\boxed{P(\nu_\mu \to \nu_\tau) = \sin^2(2\theta)\sin^2\!\left(\frac{\Delta m^2\,c^4\,L}{4E\hbar c}\right)}$$

$\theta$ 是混合角，$\Delta m^2 = m_2^2 - m_1^2$，$L$ 是飞行距离，$E$ 是中微子能量。

### 5.2 Super-Kamiokande 与大气中微子振荡

**梶田隆章（Kajita, 2015 诺奖）**：1998 年 Super-Kamiokande（Super-K）实验发现大气中微子振荡——$\nu_\mu$ 在穿过地球后部分变为 $\nu_\tau$。

Super-K 原理：高能中微子在水中产生带电轻子（$\mu^\pm$ 或 $e^\pm$），后者以超光速（$v > c/n$）在水中发出 **Cherenkov 辐射**——一个清晰的光环。

关键测量值：
- 大气中微子：$\Delta m^2_{\text{atm}} \approx 2.5\times10^{-3}$ eV$^2$，$\theta_{23} \approx 45°$。
- 太阳中微子（SNO 合作，2002）：$\Delta m^2_{\text{sol}} \approx 7.5\times10^{-5}$ eV$^2$，$\theta_{12} \approx 33°$。

### 5.3 小柴昌俊与神冈探测器

**小柴昌俊（Koshiba, 2002 诺奖）**：KamiokaNDE 神冈探测器在 1987 年探测到**超新星 SN1987A 的中微子爆发**——人类首次「看到」恒星核心坍缩的瞬间（11 个中微子在 13 秒内到达，与引力坍缩理论一致）。同时确认了太阳中微子的流量，为后来中微子振荡的发现奠定基础。

> **SN1987A 中微子先于光到达地球约 3 小时**——因为中微子在坍缩瞬间即逃逸，而光要等到冲击波到达恒星表面。这是中微子天文学的诞生。

---

## 6. Python 数值验证

### 6.1 中微子振荡概率（大气 $\nu_\mu \to \nu_\tau$）

```python
# neutrino_oscillation.py —— Super-K 大气中微子振荡概率
import numpy as np
# 大气中微子参数 (Super-K 测量)
dm2 = 2.5e-3        # eV^2
theta = np.radians(45)  # 最大混合
# P = sin²(2θ) sin²(1.27 dm2[eV²] L[km] / E[GeV])
def P_nu(L_km, E_GeV):
    arg = 1.27 * dm2 * L_km / E_GeV
    return np.sin(2*theta)**2 * np.sin(arg)**2
print("大气中微子振荡 P(νμ→ντ), E=1 GeV:")
for L in [100, 500, 1000, 5000, 10000, 12742]:  # 12742=地球直径
    P = P_nu(L, 1.0)
    print(f"  L={L:6d} km ({'地球内' if L<12742 else '穿地球'}): "
          f"P={P:.3f}  存活率={1-P:.3f}")
# 振荡长度
L_osc = 2*np.pi*1.0/(1.27*dm2)  # E=1GeV
print(f"\n振荡长度(E=1GeV): L_osc ≈ {L_osc:.0f} km")
print("Super-K: 上方(短L)νμ多, 下方(穿地球,L~13000km)νμ少 → 振荡证据")
print(f"地球直径/振荡长度 = {12742/L_osc:.2f} → 正好在振荡谷附近")
```

### 6.2 核结合能（Weizsäcker 公式）与幻数

```python
# nuclear_binding.py —— 半经验质量公式 + 幻数检验
import numpy as np
# Weizsäcker 参数 (MeV)
a_v, a_s, a_c, a_a, delta = 15.8, 18.3, 0.714, 23.2, 12.0
def binding(A, Z):
    if A < 2: return 0
    N = A - Z
    pair = delta if (N%2==0 and Z%2==0) else (-delta if (N%2==1 and Z%2==1) else 0)
    B = (a_v*A - a_s*A**(2/3) - a_c*Z*(Z-1)/A**(1/3)
         - a_a*(N-Z)**2/A + pair/A**(3/4))
    return B
def B_per_A(A, Z):
    return binding(A, Z)/A
print("核子比结合能 B/A (稳定谷 Z≈A/(2+a_c*A^(2/3)/(2*a_a))):")
print(f"{'核':>6s}  {'A':>3s}  {'Z':>3s}  {'B/A(MeV)':>9s}")
for (sym, A, Z) in [("⁴He",4,2),("¹²C",12,6),("¹⁶O",16,8),
                     ("⁵⁶Fe",56,26),("²⁰⁷Pb",207,82),("²³⁸U",238,92)]:
    print(f"  {sym:>5s}  {A:3d}  {Z:3d}  {B_per_A(A,Z):9.3f}")
print(f"\n反直觉: ⁵⁶Fe B/A≈8.8 MeV/核子 (峰值!)")
print(f"        裂变(²³⁸U→两半)和聚变(轻核)都释放能量,")
print(f"        因为都向 ⁵⁶Fe 的最高 B/A 靠拢")
# 检验幻数: Z或N=2,8,20,28,50,82 的核特别稳定
magic = [2,8,20,28,50,82,126]
print(f"\n双幻数核(尤其稳定): ⁴He(Z=2,N=2), ¹⁶O(8,8), ⁴⁰Ca(20,20), ²⁰⁸Pb(82,126)")
for (sym,A,Z) in [("⁴He",4,2),("¹⁶O",16,8),("⁴⁰Ca",40,20),("²⁰⁸Pb",208,82)]:
    N = A - Z
    tag = "双幻数" if (Z in magic and N in magic) else ""
    print(f"  {sym}: B/A={B_per_A(A,Z):.2f}  Z={Z}✓ N={N}✓  {tag}")
```

### 6.3 汤川势与核力力程

```python
# yukawa_force.py —— 汤川势 V(r)=-g²e^(-mπr/ℏc)/(4πr) 验证力程
import numpy as np
hbar_c = 197.3   # MeV·fm
m_pi = 139.6     # MeV (π±)
# 力程 R = ℏc/(mπc²) ≈ 1.43 fm
R = hbar_c / m_pi
print("汤川介子交换核力:")
print(f"  π± 质量: {m_pi:.1f} MeV")
print(f"  Compton 波长 λ=ℏ/(mπc) = {R:.2f} fm (力程)")
print(f"  实测核力力程 ≈ 1-2 fm ✓")
# 汤川势形状
g2_over_4pi = 14.3  # 约化耦合常数 ≈ α_s
r = np.array([0.5, 1.0, 1.5, 2.0, 3.0, 5.0])
V = -g2_over_4pi * np.exp(-r/R) / r
print(f"\n汤川势 V(r) = -g²/(4π) · exp(-r/R)/r  (R={R:.2f} fm):")
for ri, Vi in zip(r, V):
    print(f"  r={ri:.1f} fm: V={Vi:7.1f} MeV")
print(f"\n对比: r=0.5fm V={V[0]:.0f}MeV (强吸引) → r=5fm V={V[-1]:.1f}MeV (衰减到~1%)")
# 不确定性原理验证: ΔE=mπc², Δt~R/c
dt = R / 3e23  # R in fm → time in units of fm/c
print(f"\n不确定性原理: ΔE·Δt ~ ℏ")
print(f"  ΔE = mπc² = {m_pi:.0f} MeV")
print(f"  Δt ~ R/c ~ {R:.2f} fm/c")
print(f"  ΔE·Δt = {m_pi*R:.0f} MeV·fm ≈ ℏc = {hbar_c:.0f} MeV·fm ✓")
```

### 6.4 标准模型粒子质量谱

```python
# sm_spectrum.py —— 标准模型基本粒子质量谱（对数尺度）
import numpy as np
fermions = {
    "ν₁": 0.01e-6, "ν₂": 0.009e-3, "ν₃": 0.05,  # 中微子(质量本征态, eV)
    "e":   0.511e-3, "μ": 105.7e-3, "τ": 1.777,  # GeV
    "u":   2.2e-3, "c": 1.28, "t": 173.0,
    "d":   4.7e-3, "s": 0.096, "b": 4.18,
}
bosons = {"γ":0, "g":0, "W":80.4, "Z":91.2, "H":125.1}
print("标准模型基本粒子质量谱 (GeV):")
print("费米子:")
for name, m in sorted(fermions.items(), key=lambda x: x[1]):
    print(f"  {name:>3s}: {m:.4g} GeV = {m*1e6:.4g} keV")
print("玻色子:")
for name, m in bosons.items():
    print(f"  {name}: {m:.1f} GeV" + (" (无质量)" if m==0 else ""))
# 质量跨度
m_min = min(v for v in fermions.values() if v > 0)
m_max = max(fermions.values())
print(f"\n质量跨度: {m_max/m_min:.0e} 倍 (从 {m_min:.1g} 到 {m_max:.0f} GeV)")
print("反直觉: top quark 质量是中微子的 ~10¹⁰ 倍, 但两者由同一 Lagrangian 描述")
print(f"\n质子质量 {938.3:.0f} MeV = 3夸克质量({2*2.2+4.7:.0f} MeV) + QCD结合能({938.3-2*2.2-4.7:.0f} MeV)")
print(f"  → 99% 的质子质量来自强相互作用能量(E=mc²)")
```

---

## 7. 東大特色：素粒子物理の黄金血脈

東京大学素粒子物理的血脉从汤川延伸到当代：

### 7.1 理论血脉

- **湯川秀樹**（Yukawa, 1949）：介子理论——日本首个诺奖。
- **朝永振一郎**（Tomonaga, 1965）：QED 重整化——与 Schwinger/Feynman 共享。
- **小林誠・益川敏英**（Kobayashi & Maskawa, 2008）：CKM 矩阵与 CP 破缺。
- **南部陽一郎**（Nambu, 2008，東大出身，任教 Chicago）：自发对称性破缺——标准模型 Higgs 机制的理论先驱。

### 7.2 实验血脉：Kamioka 系列

- **KamiokaNDE**（1983–1996）：小柴昌俊建造，探测质子衰变（未发现）+ 中微子。
- **Super-Kamiokande**（1996–至今）：5 万吨水，梶田发现大气中微子振荡。
- **Hyper-Kamiokande**（建设中，2027 启动）：26 万吨水，下一代中微子望远镜。

> 这条实验线体现了東大「大科学」传统——从 10 米级探测器到百米级，持续 40 年，每一步都催生诺奖级发现。

### 7.3 Kavli IPMU（宇宙物理数学研究所）

東大 Kavli IPMU（2007 年成立）是跨学科研究所，聚焦**暗物质、中微子、宇宙学**的交叉。其研究连接了粒子物理（标准模型之外）与宇宙学（暗物质、暗能量），是東大 Phase 2 宇宙論课（下一专题）的直接对接。

---

## 8. 習題集（Exercises）

> 标 ★ 为東大风格，★★ 为研究生级。

**习题 1（★）**　大气中微子振荡中，$\Delta m^2_{\text{atm}} = 2.5\times10^{-3}$ eV$^2$，$\nu_\mu$ 能量 $E = 1$ GeV。求振荡长度 $L_{\text{osc}}$（km）。
> *答案*：$L_{\text{osc}} = 4\pi E/(1.27\,\Delta m^2) \approx 4\pi/(1.27\times0.0025) \approx 3950$ km（约地球半径）。

**习题 2（★★）**　用 Weizsäcker 公式估算 $^{235}$U 裂变释放的能量。假设裂变为两个相等碎片 $A \approx 118, Z \approx 46$。
> *答案*：$\Delta B \approx 2B(118,46) - B(235,92) \approx 200$ MeV/裂变。

**习题 3（★）**　自由中子 $\beta$ 衰变 $n \to p + e^- + \bar{\nu}_e$ 的最大电子动能是多少？已知 $m_n = 939.57$, $m_p = 938.27$, $m_e = 0.511$ MeV。
> *答案*：$T_e^{\max} = m_n - m_p - m_e \approx 0.789$ MeV（中微子能量趋零时）。

**习题 4（★★）**　解释为什么 CKM 矩阵的复相位只在三代（或更多）夸克时才存在。两代夸克时 CKM 矩阵可否有 CP 破坏？
> *答案*：两代时 CKM 是 $2\times2$ 正交矩阵，只有 1 个实参数（Cabibbo 角），可通过夸克场相位重定义消除所有复数。三代时有 4 个参数（3 角 + 1 相位），相位 $\delta$ 不可消除 $\Rightarrow$ CP 破坏。

**习题 5（★）**　SN1987A 距地球 $d = 50$ kpc（$1.63\times10^{20}$ m）。中微子能量 $E = 10$ MeV，质量 $m_\nu < 10$ eV。估计中微子与光子的到达时间差。
> *答案*：$\Delta t \approx \frac{d}{c}\frac{m_\nu^2 c^4}{2E^2} \approx \frac{1.63\times10^{20}}{3\times10^8}\cdot\frac{(10)^2}{2\times(10^7)^2}\,\text{s} \approx 2.7\times10^{-2}$ s（可忽略）。实测 $\Delta t \sim$ 数秒来自物理机制（中微子先于光逃逸）。

**习题 6（★★）**　用渐近自由公式估算 $\alpha_s(Q^2)$ 在 $Q = 1$ GeV 和 $Q = 100$ GeV 处的值。取 $n_f = 5$, $\Lambda_{\text{QCD}} = 200$ MeV。
> *答案*：$Q = 1$ GeV: $\alpha_s \approx 12\pi/[(33-10)\ln(25)] \approx 0.47$。$Q = 100$ GeV: $\alpha_s \approx 0.11$（弱耦合，可做微扰）。

---

## 9. 参考文献

1. Schwartz, Matthew. *Quantum Field Theory and the Standard Model*. Cambridge, 2014.（東大素粒子物理指定，现代标准）
2. Halzen, Martin. *Quarks and Leptons*. Wiley, 1984.（经典入门，日文译本）
3. Griffiths, David. *Introduction to Elementary Particles* 2ed. Wiley-VCH, 2008.（最友好的入门）
4. Peskin, Schroeder. *An Introduction to Quantum Field Theory*. Westview, 1995.（QFT 研究生标准）
5. Krane, Kenneth. *Introductory Nuclear Physics*. Wiley, 1988.（核物理标准教材）
6. 小柴昌俊. 『物理のために』（培風館）——小柴自述+物理洞察。
7. 梶田隆章. 『ニュートリノの夢』（岩波書店）——Super-K 一手叙述。
8. 江沢洋 他. 『素粒子物理学』（岩波書店）——東大本土教材。

---

**完成日期**：2026-08-12　|　**对应 SURVEY §9 東大**：素粒子物理学 + 原子核物理学　|　**特色收束**：Koshiba/Kajita 中微子振荡 + 小林・益川 CKM 矩阵

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：素粒子物理学回答「世界最基本的积木是什么？它们之间有什么力？」——答案：12 种费米子（6 夸克 + 6 轻子）+ 4 种规范玻色子（光子、W、Z、胶子）+ Higgs 玻色子，靠三种力（电磁 + 弱 + 强）组合成你看到的一切。这套「标准模型」是人类最精确的理论（精度 $10^{-12}$）。
>
> **生活类比**：标准模型像一个三层的「乐高体系」——第一代（上、下夸克 + 电子 + 电子中微子）组成了日常物质；第二代（粲、奇 + μ 子）和第三代（顶、底 + τ 子）是「重影版」，衰变后回到第一代。三代之间用 CKM 矩阵「互相串门」（小林・益川的诺奖工作）。
>
> **反直觉发现**：
> - **夸克不能被单独看到（色禁闭）**：你用力拉两个夸克，能量越来越大，但到某个阈值会「啪」地从真空中生成新夸克对，形成强子喷注——你永远只能看到无色强子，看不到裸夸克。
> - **中微子振荡**：中微子在飞行中会「换味」——$\nu_\mu$ 变成 $\nu_\tau$ 再变回来。Super-Kamiokande（梶田 2015 诺奖）发现大气中微子穿过地球后部分消失——它们变成了 $\nu_\tau$。
> - **质子质量 99% 不是夸克**：3 个价夸克质量之和才 9 MeV，质子是 938 MeV——其余 99% 是胶子场和海夸克的能量。$E = mc^2$ 最壮观的体现。
> - **CP 破坏为什么重要**：大爆炸应该产生等量物质和反物质，它们湮灭后宇宙应该只剩光。但我们存在！小林・益川的 CKM 矩阵复相位提供了物质-反物质不对称的微观起源（虽然量级不够，需要新物理）。

---

## 🔗 衔接：从哪来，到哪去

### 前置
- **量子力学 B**：Dirac 记号、角动量、散射理论、Fermi 黄金规则。
- **电动力学**：规范变换、Maxwell → QED 的量子化。
- **数学**：群论 + 表示论（$SU(3)\times SU(2)\times U(1)$ 规范理论）、张量。

### 本课解决了什么危机
- **强力的渐近自由与禁闭**：QED 的电荷越靠近越远，但 QCD 反过来——高能（短距）耦合弱（渐近自由，2004 诺奖 Gross/Politzer/Wilczek），低能（长距）耦合强到禁闭。
- **电弱统一的成就**：电磁 + 弱表面看起来截然不同（光子无质量 vs W/Z 有 80–91 GeV 质量）。Glashow-Weinberg-Salam（1968）+ Higgs 机制（1964）证明它们在 $E > 100$ GeV 是一种力——电弱统一。1983 CERN 发现 W/Z，完美验证。
- **中微子质量的标准模型缺口**：最小 SM 中中微子无质量。但 1998 Super-K 振荡 + 2002 SNO 太阳中微子，证明中微子有质量——SM 必须扩展。这是 SM 的第一个「裂痕」。

### 本课留下的新危机（通往下一站）
- **暗物质**：宇宙 27% 是暗物质，但 SM 里没有候选者（中微子质量太小）。需新物理：WIMP、轴子（axion）、原初黑洞（PBH）。
- **物质-反物质不对称**：CKM 矩阵的 CP 破坏量级不够解释观测 $\eta_B \sim 10^{-9}$。需要新的 CP 源（leptogenesis？强 CP 与 axion？）。
- **引力未纳入 SM**：Einstein 广义相对论与量子场论无法统一。弦理论？圈量子引力？这是物理学最大悬案。
- **味谜与质量谱**：三代夸克质量跨越 5 个数量级（顶夸克 173 GeV vs 上夸克 2 MeV），中微子质量比顶夸克小 $10^{12}$ 倍。为什么？ flavour physics 的核心。

### 后续（東大路径）
| 方向 | 课程 | 用到本课什么 |
|------|------|-------------|
| 量子色动力学 | QFT 进阶 | 渐近自由、格点 QCD |
| 宇宙学 | 一般相対論/宇宙論 | 暗物质、原初核合成、leptogenesis |
| 加速器实验 | 实验 | LHC、KEK/Belle II |
| 中微子物理 | 实验 | Super-K / Hyper-K、T2K |
| 弦理论 | 数学物理 | AdS/CFT、额外维 |

---

## 🏭 理论联系实际：5 个应用

1. **PET 医学影像（正电子断层扫描）**：注射含正电子发射核（¹⁸F-FDG），正电子-电子湮灭产生两个反向 511 keV 光子——这是 QED + 反物质的医学应用。每年挽救数百万癌症患者。
2. **同步辐射光源（Spring-8, KEK PF）**：高能电子在弯转中辐射高强度 X 射线，用于蛋白质结构（新冠主蛋白酶 2020 解析）、新材料表征。日本 Spring-8（兵庫）是世界最大第三代同步辐射源。
3. **重离子治癌**：碳离子束在肿瘤位置精确释放能量（Bragg 峰），杀伤癌细胞而保护正常组织。QST（日本量子科学技術研究開発機構，千葉）是全球重离子治癌先驱，已治疗超 1.5 万例。
4. **中微子探测器与天体物理**：Super-Kamiokande（岐阜）监测超新星中微子（SN1987A 11 个中微子开启中微子天文学）、太阳中微子、大气中微子。Hyper-Kamiokande（2027 启动）将把探测灵敏度提升 10 倍。
5. **粒子加速器衍生技术**：超导磁体（MRI）、射频腔（自由电子激光）、探测器（CT/PET）、WWW（CERN 的 Tim Berners-Lee 发明）——粒子物理「大科学」催生大量民用技术。

---

## 🔬 最新研究前沿（2024-2026）

- **Super-Kamiokande 首次探测弥散超新星中微子背景（DSNB, 2026 年 8 月）**：基于约 5000 天数据（纯水 2008–2020 + 钆掺杂 2020–至今），在 13.3–81.3 MeV 能量区发现 2.6σ（99.5% CL）超出，对应 DSNB 通量 $\sim 3.6\ \text{cm}^{-2}\text{s}^{-1}$。钆掺杂技术由 IPMU 的 Mark Vagins 于 2004 年提出，20 年后开花结果。这是「中微子天文学」从单颗超新星扩展到宇宙历史的关键一步。
- **Hyper-Kamiokande 建设（2027 启动）**：26 万吨水（Super-K 的 10 倍），将精确测量中微子 CP 破坏（回答物质-反物质不对称）、质子衰变（验证大统一理论）。東大 ICRR + Kavli IPMU 主导。
- **μ 子 g-2 异常（Fermilab 2023/2025）**：μ 子磁矩实验值与标准模型差 $4.2\sigma$，可能指向新物理（暗光子、超对称）。2025 年的 lattice QCD 计算弱化了这个差异，但争议仍在——这是标准模型边界的最热争议。
- **Belle II（KEK, 2019–）进展**：日本筑波的 B 工厂升级，2024–2025 收集 $\sim 5\times10^{9}$ B 介子对，精确测量 CKM 矩阵元、寻找 $B \to K^* \nu\bar\nu$ 等暗物质相关稀有衰变。
- **轴子暗物质探测（ADMX, 2024–2026）**：华盛顿大学的 ADMX 在 μeV 质量范围达到 QCD 轴子灵敏度；東大 Kavli IPMU 的「轴子天体物理」组推动轴子-光子转换的望远镜探测（CAST, IAXO）。

---

## 🗺️ 学习 Roadmap（Tokyo 路径）

```
量子力学 B（4 年级， Sakurai）
  ↓ Dirac 记号、散射理论、Fermi 黄金规则
素粒子物理学（4 年级， Griffiths《Introduction》）
  ↓ 核心关卡 ↓
  ├─ 费米子三代 + 规范玻色子 + Higgs
  ├─ 电弱统一（GWS 模型 + Weinberg 角）
  ├─ QCD（渐近自由 + 色禁闭 + 强子谱）
  └─ 中微子振荡（PMNS 矩阵）
量子场论（研究生， Schwartz / Peskin-Schroeder）
  ↓ Lagrangian + Feynman 图 + 重整化
  ├─ QED 重整化（朝永遗产）
  ├─ 规范理论 + Higgs 机制
  └─ 标准模型完整推导
研究生进阶
  ├─ 超越标准模型（SUSY、大统一、弦）
  ├─ 宇宙学（暗物质、原初核合成）
  ├─ 加速器物理 + 探测器（LHC/Belle II/Hyper-K）
  └─ 中微子物理（实验与唯象）
```

**知识检查**：
- [ ] 能写出标准模型的规范群 $SU(3)_c \times SU(2)_L \times U(1)_Y$，并说出每个因子对应什么力。
- [ ] 能用 CKM 矩阵解释为什么 CP 破坏需要三代夸克（小林・益川论证）。
- [ ] 能用渐近自由公式解释「QCD 高能弱耦合、低能强耦合」，并说出 $\Lambda_{\text{QCD}} \approx 200$ MeV 的意义。
- [ ] 能算出大气中微子振荡长度 $L_{\text{osc}} \approx 4\pi E/(1.27 \Delta m^2) \approx 4000$ km（约地球半径）。
- [ ] 能解释 Super-Kamiokande 怎么用 Cherenkov 环区分 $\nu_\mu$ 与 $\nu_e$ 事件（μ 的环锐利、e 的环模糊）。
- [ ] 能说出 2026 年 Super-K 首次探测 DSNB 迹象为什么依赖「钆掺杂」技术（中子俘获 + 延迟 γ 标记）。
