# Harvard 粒子与核物理 — Phys 253a/b + 核物理专题

> **课程**：Phys 253a (Quantum Field Theory I) · Phys 253b (Quantum Field Theory II) · 核物理专题（散布于研究生选修课）
> **教材**：Schwartz *Quantum Field Theory and the Standard Model* (2014, **Harvard 教授自著**) · Peskin & Schroeder *Introduction to QFT* (1995) · Krane *Introductory Nuclear Physics* (1988)
> **一手来源**：[Harvard 2025-26 SPS Guide](https://www.physics.harvard.edu/resource/sps-guide-physics-2025-2026) + [Harvard Grad Requirements](https://www.physics.harvard.edu/grad/requirements)（2026-08 核实）

> ⚠️ **核实说明**：用户原文指定 "Phys 211/212/218"。经核实：**Phys 212 = Physical Cosmology**（Dvorkin），**Phys 218 = Advanced Semiclassical Methods for QM**——均非粒子/核物理。Harvard 的粒子物理在研究生序列 **Phys 253a/b (QFT)** 中教授，教材是 Harvard 自己的 Matthew Schwartz 教授所著。核物理无独立编号课程，散布于专题选修。

---

## 🎓 Harvard 特色：Schwartz 的 QFT 与标准模型

Harvard 2025-26 SPS Guide 对 Phys 253a 的描述（原文）：

> *"Physics 253a is the first course in the graduate quantum field theory sequence... The course is often taught by Prof. Matthew Schwartz, whose celebrated textbook Quantum Field Theory and the Standard Model provides a good introduction."*

> *"Harvard's version covers significantly more material in a shorter amount of time [than MIT's 3-semester series]."*

**三个特色**：

1. **自家教材**：Schwartz 的书是 Harvard 教授写的，内容直接对应课程节奏（Peskin 是备选参考书）
2. **加速节奏**：两个学期（253a/b）覆盖 MIT 三个学期（8.323-8.325）的内容
3. **从经典场论到标准模型**：253a 建立场论框架 → 253b 直达标准模型

**Harvard 理论高能物理组**：Cumrun Vafa（弦论/F-理论）、Andrew Strominger（弦论/黑洞）、Xiao-Gang Wen（拓扑物态/量子信息）、Matt Schwartz（QFT/有效理论）。

| 教材 | 定位 | 特色 |
|------|------|------|
| **Schwartz** | Harvard 253a/b 主教材 | 推导清晰、现代视角、直奔标准模型 |
| **Peskin & Schroeder** | 国际标准 QFT 教材 | 经典参考、路径积分处理详细 |
| **Krane** | 核物理入门 | 实验导向、覆盖核结构/衰变/反应 |

---

## 第一部分：从量子力学到场论（Schwartz Ch.1-3, Peskin Ch.2-3）

### 1.1 为什么需要场论？

**量子力学的局限**：
1. 粒子数不守恒（对撞实验中粒子可创生/湮灭）
2. 不能自然描述自旋-统计关系
3. 不能处理反物质（需要 Dirac 场）

**量子场论的核心思想**：**粒子是场的激发**。

$$\text{场 } \phi(x) \longrightarrow \text{粒子 = 场的量子}$$

电子是电子场 $\psi(x)$ 的激发；光子是电磁场 $A_\mu(x)$ 的激发；夸克是夸克场的激发。

### 1.2 Klein-Gordon 场

最简单的标量场满足 Klein-Gordon 方程：

$$(\Box + m^2)\phi = 0, \quad \Box = \partial_\mu\partial^\mu = \frac{1}{c^2}\partial_t^2 - \nabla^2$$

**场量子化**：将 $\phi(x)$ 展开为平面波，赋予产生/湮灭算符：

$$\hat{\phi}(x) = \int\frac{d^3p}{(2\pi)^3}\frac{1}{\sqrt{2\omega_p}}\left[\hat{a}_p\,e^{-ipx} + \hat{a}_p^\dagger\,e^{ipx}\right]$$

其中 $\omega_p = \sqrt{p^2 + m^2}$，对易关系 $[\hat{a}_p, \hat{a}_{p'}^\dagger] = (2\pi)^3\delta^3(\vec{p}-\vec{p'})$。

> 🔑 **反直觉**：真空不空！$\langle 0|\hat{\phi}^2|0\rangle = \infty$（紫外发散）。真空中充满了"虚粒子对的沸腾"，这直接导致 Lamb 移动和 Casimir 效应。

### 1.3 Noether 定理与守恒流

**Noether 定理**：连续对称性 → 守恒流。

| 对称性 | 守恒流 | 守恒荷 |
|--------|--------|--------|
| 时间平移 | $T^{\mu\nu}$（能动张量） | 能量 $E$ |
| 空间平移 | $T^{\mu i}$ | 动量 $\vec{P}$ |
| 相位旋转 $\phi \to e^{i\alpha}\phi$ | $j^\mu = i(\phi^*\partial^\mu\phi - \phi\partial^\mu\phi^*)$ | 粒子数 $N$ |

---

## 第二部分：费曼图与微扰论（Schwartz Ch.4-7, Peskin Ch.4-6）

### 2.1 S 矩阵与散射截面

散射振幅通过 S 矩阵描述：

$$\langle f | S | i \rangle = \delta_{fi} + i(2\pi)^4\delta^4(P_f - P_i)\,\mathcal{M}$$

**散射截面**：

$$d\sigma = \frac{1}{4E_1E_2|v_1 - v_2|}\left|\mathcal{M}\right|^2\,d\Pi_{\text{LIPS}}$$

其中 $d\Pi_{\text{LIPS}}$ 是 Lorentz 不变相空间。

### 2.2 费曼规则

**传播子**（自由传播子）：

| 粒子 | 传播子 |
|------|--------|
| 标量 | $\frac{i}{p^2 - m^2 + i\epsilon}$ |
| 旋量 | $\frac{i(\slashed{p}+m)}{p^2-m^2+i\epsilon}$ |
| 光子 | $\frac{-ig_{\mu\nu}}{p^2+i\epsilon}$（Feynman 规范） |

**顶点因子**：由相互作用 Lagrangian 决定。

> 💡 **直觉**：费曼图是计算工具，不是物理图像。每个图对应微扰展开的一个阶——虚粒子不是"真的飞过去"，而是数学上对量子涨落的编码。

### 2.3 树图计算示例

**Bhabha 散射**（$e^+e^- \to e^+e^-$）：有两幅树图贡献——s 道光子交换 + t 道光子交换。

**最低阶截面**（高能极限 $s \gg m_e^2$）：

$$\frac{d\sigma}{d\Omega} = \frac{\alpha^2}{4s}\left[\frac{1+\cos^4(\theta/2)}{\sin^4(\theta/2)} + \frac{1+\cos^2\theta}{2} - \frac{2\cos^4(\theta/2)}{\sin^2(\theta/2)}\right]$$

---

## 第三部分：规范对称性与标准模型（Schwartz Ch.8-12, 25-29）

### 3.1 规范不变性

**U(1) 规范理论（QED）**：要求 Lagrangian 在局域相位变换下不变：

$$\psi(x) \to e^{-ie\alpha(x)}\psi(x)$$

需要引入规范场 $A_\mu$，协变导数 $D_\mu = \partial_\mu + ieA_\mu$。

**QED Lagrangian**：

$$\mathcal{L}_{\text{QED}} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}$$

> 🔑 **深刻原理**：规范不变性**要求**光子无质量！如果光子有质量 $m_\gamma$，需要在 $\mathcal{L}$ 中加 $\frac{1}{2}m_\gamma^2 A_\mu A^\mu$，但这破坏规范不变性。因此无质量规范玻色子是规范对称性的直接推论。

### 3.2 非阿贝尔规范理论（Yang-Mills）

推广到非阿贝尔群（如 SU(2), SU(3)），规范场自身带有荷：

$$\mathcal{L}_{\text{YM}} = -\frac{1}{4}F^a_{\mu\nu}F^{a\mu\nu}, \quad F^a_{\mu\nu} = \partial_\mu A^a_\nu - \partial_\nu A^a_\mu + gf^{abc}A^b_\mu A^c_\nu$$

**关键区别**：非阿贝尔规范场有**自相互作用**（三胶子/四胶子顶点）——光子之间不直接相互作用，但胶子会！

### 3.3 标准模型

标准模型 = SU(3) × SU(2) × U(1) 规范理论。

**基本粒子表**：

| 类型 | 粒子 | 自旋 | 荷 |
|------|------|------|-----|
| 夸克（3代×3色） | $u,d$ / $c,s$ / $t,b$ | 1/2 | 分数电荷 |
| 轻子（3代） | $e,\nu_e$ / $\mu,\nu_\mu$ / $\tau,\nu_\tau$ | 1/2 | 整数电荷 |
| 规范玻色子 | $\gamma$（光子）, $g$（胶子×8）, $W^\pm$, $Z^0$ | 1 | 力的传递者 |
| Higgs 玻色子 | $h$ | 0 | 赋予质量 |

**三种力**：

| 力 | 规范群 | 玻色子 | 相对强度 |
|----|--------|--------|---------|
| 强相互作用 | SU(3) | 8 个胶子 | ~1 |
| 电弱相互作用 | SU(2)×U(1) | $W^\pm, Z^0, \gamma$ | ~$10^{-2}$（弱部分 ~$10^{-5}$） |

### 3.4 Higgs 机制

**自发对称性破缺**：Lagrangian 对称，但真空不对称。

**Higgs 势**：

$$V(\Phi) = -\mu^2|\Phi|^2 + \lambda|\Phi|^4$$

最小值在 $|\Phi| = v/\sqrt{2}$ 处（$v = \mu/\sqrt{\lambda} \approx 246$ GeV），真空期望值非零。

> 🔑 **反直觉**：**对称性不是被"破坏"了——它是隐藏的**。Lagrangian 仍然有完整对称性，但真空态"选择"了一个特定方向，使得对称性不再明显。质量 $m_W = gv/2$, $m_Z = \sqrt{g^2+g'^2}v/2$，光子保持无质量。

---

## 第四部分：QCD 与强相互作用（Schwartz Ch.25-26）

### 4.1 渐近自由

**Gross-Wilczek / Politzer 发现**（1973, 诺贝尔奖 2004）：QCD 耦合常数在高能（短距离）下**变弱**：

$$\alpha_s(Q^2) = \frac{12\pi}{(33 - 2n_f)\ln(Q^2/\Lambda_{\text{QCD}}^2)}$$

其中 $\Lambda_{\text{QCD}} \approx 200$ MeV 是 QCD 标度，$n_f$ 是夸克味数。

> 🔑 **反直觉**：与 QED 相反！QED 耦合在高能时**增强**（Landau 极点），QCD 耦合在高能时**减弱**。原因是胶子的自相互作用导致"反屏蔽"效应。

### 4.2 夸克禁闭

低能（$Q \sim \Lambda_{\text{QCD}}$）时 $\alpha_s \to \infty$——夸克无法被单独分离。

**禁闭假设**：夸克永远以束缚态（强子）形式存在。

**色禁闭**：只有"色单态"可以被孤立观测：
- 重子（qqq）：$3 \otimes 3 \otimes 3 = 1 \oplus \ldots$
- 介子（q$\bar{\text{q}}$）：$3 \otimes \bar{3} = 1 \oplus 8$

### 4.3 深度非弹性散射

**Bjorken 标度**：高能电子-质子散射中，结构函数只依赖无量纲比值 $x = Q^2/(2p\cdot q)$。

→ 揭示质子内部有**点状结构**（部分子 = 夸克），是夸克存在的关键实验证据。

---

## 第五部分：弱相互作用与 CP 破坏（Schwartz Ch.29）

### 5.1 V-A 理论

弱相互作用是左手性的——只有左手螺旋度的费米子参与弱相互作用：

$$\mathcal{L}_{\text{weak}} = -\frac{G_F}{\sqrt{2}}J^\mu J_\mu^\dagger$$

$$J^\mu = \bar{\nu}_e\gamma^\mu(1-\gamma^5)e + \bar{u}\gamma^\mu(1-\gamma^5)d' + \ldots$$

> 🔑 **最大宇称破坏**：吴健雄实验（1957）证明 $\beta$ 衰变中电子偏好左手发射——自然界**区分左右**！这是物理最深刻的发现之一。

### 5.2 CP 破坏与物质-反物质不对称

**CKM 矩阵**：夸克弱相互作用本征态与质量本征态不同：

$$\begin{pmatrix} d' \\ s' \\ b' \end{pmatrix} = V_{\text{CKM}}\begin{pmatrix} d \\ s \\ b \end{pmatrix}$$

CKM 矩阵包含一个**不可消除的复相位** $\delta_{\text{CP}}$ → CP 破坏。

> **宇宙学含义**：CP 破坏是 Sakharov 三条件之一（重子数破坏 + C/CP 破坏 + 偏离热平衡），解释宇宙中物质-反物质不对称。但标准模型的 CP 破坏量不够——可能需要新物理。

### 5.3 中微子振荡

**PMNS 矩阵**（中微子版 CKM）：不同味中微子在传播中相互转换。

$$P(\nu_e \to \nu_\mu) = \sin^2(2\theta)\sin^2\left(\frac{\Delta m^2 L}{4E}\right)$$

太阳中微子实验（SNO, 2001）和大气中微子实验（Super-K）证实了振荡 → 中微子有质量（超出原始标准模型！）。

---

## 第六部分：核物理（Krane）

### 6.1 结合能与核子相互作用

**半经验质量公式**（Weizsäcker / Bethe）：

$$B(A,Z) = a_v A - a_s A^{2/3} - a_c\frac{Z(Z-1)}{A^{1/3}} - a_a\frac{(A-2Z)^2}{A} + \delta(A,Z)$$

| 项 | 物理含义 | 典型值 (MeV) |
|----|---------|-------------|
| 体积能 $a_v A$ | 每个核子结合能饱和 | $a_v \approx 15.5$ |
| 表面能 $-a_s A^{2/3}$ | 表面核子少邻居 | $a_s \approx 16.8$ |
| Coulomb 能 $-a_c Z^2/A^{1/3}$ | 质子排斥 | $a_c \approx 0.72$ |
| 对称能 $-a_a(A-2Z)^2/A$ | 偏好 $N=Z$ | $a_a \approx 23$ |
| 配对能 $\delta$ | 偶-偶核更稳定 | $a_p \approx 34$ |

> 🔑 **反直觉**：铁-56（$\,^{56}$Fe）不是结合能最高的核！从**每核子结合能**看，$\,^{62}$Ni 和 $\,^{58}$Fe 更高。$\,^{56}$Fe 之所以被误认为最高，是因为它在前驱过程（超新星）中最容易大量产生。

### 6.2 核壳层模型

类似于原子壳层模型，但力是强相互作用而非电磁力。

**幻数**：$2, 8, 20, 28, 50, 82, 126$——这些中子/质子数的核特别稳定。

**Mayer-Jensen 模型**（1963 诺贝尔奖）：引入**强自旋-轨道耦合** $V_{ls}\vec{l}\cdot\vec{s}$，打破了简并，产生幻数。

$$\vec{l}\cdot\vec{s} = \frac{1}{2}[j(j+1) - l(l+1) - s(s+1)]$$

### 6.3 核衰变

| 衰变类型 | 过程 | 半衰期范围 |
|---------|------|-----------|
| $\alpha$ 衰变 | $\,^A_Z X \to \,^{A-4}_{Z-2}Y + \,^4_2\text{He}$ | $10^{-7}$s – $10^{10}$yr |
| $\beta^-$ 衰变 | $n \to p + e^- + \bar{\nu}_e$ | ms – Gyr |
| $\gamma$ 衰变 | 激发态退激 | $10^{-16}$s – yr |

**$\alpha$ 衰变的量子隧穿**：$\alpha$ 粒子在核内被强相互作用束缚，但需要穿越 Coulomb 势垒。Gamow 用量子隧穿解释了衰变半衰期与 $\alpha$ 粒子能量的指数关系（Geiger-Nuttall 定律）。

---

## 📝 习题精选

### 习题 1（传播子）

写出标量场的 Feynman 传播子，并验证它在质量壳上 $p^2 = m^2$ 处发散。

### 习题 2（Higgs 质量关系）

已知 $m_W = 80.4$ GeV, $m_Z = 91.2$ GeV, $v = 246$ GeV。求 Weinberg 角 $\theta_W$。

> **答案**：$\cos\theta_W = m_W/m_Z = 0.882$，$\sin^2\theta_W = 1 - (m_W/m_Z)^2 = 0.222$。

### 习题 3（渐近自由）

已知 $\Lambda_{\text{QCD}} = 200$ MeV, $n_f = 6$。求 $\alpha_s$ 在 $Q = 91.2$ GeV（$Z$ 玻色子质量）处的值。

> **提示**：$\alpha_s = 12\pi/[(33-12)\ln(Q^2/\Lambda^2)]$。

### 习题 4（结合能）

用半经验质量公式计算 $\,^{56}$Fe 和 $\,^{238}$U 的每核子结合能。

> **提示**：代入参数 $a_v = 15.5$, $a_s = 16.8$, $a_c = 0.72$, $a_a = 23$, $a_p = 34$。

### 习题 5（中微子振荡）

大气中微子实验测得 $\Delta m^2_{23} \approx 2.5 \times 10^{-3}$ eV², $\theta_{23} \approx 45°$。求能量 1 GeV 的 $\nu_\mu$ 振荡到 $\nu_\tau$ 的第一个极大值距离。

> **答案**：$L_{\max} = \pi E/\Delta m^2 \approx 500$ km（大气中微子振荡尺度）。

---

## 💻 Python 代码

### 代码 1：标准模型粒子表与衰变宽度

```python
"""
标准模型基本粒子数据 + 常见衰变分支比
零依赖纯 Python
"""
import math

# --- 标准模型费米子 ---
fermions = [
    ("u (up)",       2.2,     2/3, "I"),
    ("d (down)",     4.7,    -1/3, "I"),
    ("c (charm)",    1275,    2/3, "II"),
    ("s (strange)",  95,     -1/3, "II"),
    ("t (top)",      173000,  2/3, "III"),
    ("b (bottom)",   4180,   -1/3, "III"),
    ("e (electron)", 0.511,  -1,   "I"),
    ("mu (muon)",    105.7,  -1,   "II"),
    ("tau",          1777,   -1,   "III"),
    ("nu_e",         0.0008,  0,   "I"),
    ("nu_mu",        0.00017, 0,   "II"),  # 上限
    ("nu_tau",       0.018,   0,   "III"), # 上限
]

# --- 规范玻色子 ---
bosons = [
    ("gamma (photon)", 0,       "电磁"),
    ("g (gluon)",      0,       "强"),
    ("W±",             80379,   "弱"),
    ("Z0",             91188,   "弱"),
    ("Higgs (h)",      125100,  "质量起源"),
]

print("=== 标准模型费米子 ===")
print(f"{'名称':>16} {'质量(MeV)':>12} {'电荷':>6} {'代':>5}")
print("-" * 45)
for name, mass, charge, gen in fermions:
    print(f"{name:>16} {mass:12.4f} {charge:6.2f} {gen:>5}")

print(f"\n=== 规范玻色子 ===")
print(f"{'名称':>18} {'质量(MeV)':>12} {'作用':>8}")
print("-" * 42)
for name, mass, force in bosons:
    print(f"{name:>18} {mass:12.0f} {force:>8}")

# --- Weinberg 角 ---
mW, mZ = 80379, 91188
cos_W = mW / mZ
sin2_W = 1 - cos_W**2
print(f"\n=== 电弱参数 ===")
print(f"Weinberg 角: cos θW = mW/mZ = {cos_W:.4f}")
print(f"sin²θW = {sin2_W:.4f} (实验值 ≈ 0.231)")
print(f"电弱精细结构常数 α_em = e²/(4π) ≈ 1/128 (Z质量处)")

# --- QCD 跑动耦合 ---
Lambda_QCD = 200  # MeV
nf = 6
def alpha_s(Q_MeV):
    """单圈 QCD 跑动耦合"""
    Q = Q_MeV / 1000  # 转 GeV
    L = Lambda_QCD / 1000
    return 12 * math.pi / ((33 - 2*nf) * math.log(Q**2 / L**2))

print(f"\n=== QCD 渐近自由: αs(Q) ===")
print(f"Λ_QCD = {Lambda_QCD} MeV, nf = {nf}")
for Q_label, Q in [("1 GeV", 1000), ("10 GeV", 10000), ("91 GeV (Z)", 91188), ("173 GeV (top)", 173000)]:
    a = alpha_s(Q)
    print(f"  Q = {Q_label:>14}: αs = {a:.4f}")

print(f"\n结论: αs 随 Q 增大而减小 → 渐近自由 (Gross/Wilczek/Politzer 1973)")
print(f"  低能 αs → ∞ → 夸克禁闭")
```

### 代码 2：核结合能半经验公式

```python
"""
Weizsäcker 半经验质量公式: 计算每核子结合能
验证 ⁵⁶Fe 附近的极大值
零依赖纯 Python
"""
import math

# 半经验质量公式参数 (MeV)
a_v = 15.75   # 体积能
a_s = 17.8    # 表面能
a_c = 0.711   # Coulomb 能
a_a = 23.7    # 对称能
a_p = 11.18   # 配对能

def binding_energy(A, Z):
    """半经验结合能 (MeV)"""
    if A <= 0 or Z <= 0 or Z > A:
        return 0.0
    volume = a_v * A
    surface = a_s * A**(2/3)
    coulomb = a_c * Z * (Z - 1) / A**(1/3)
    asym = a_a * (A - 2*Z)**2 / A
    # 配对能
    if A % 2 == 0 and Z % 2 == 0:      # 偶-偶
        delta = a_p / A**0.5
    elif A % 2 == 1:                    # 奇 A
        delta = 0.0
    else:                               # 奇-奇
        delta = -a_p / A**0.5
    return volume - surface - coulomb - asym + delta

def binding_per_nucleon(A, Z):
    """每核子结合能"""
    return binding_energy(A, Z) / A

def most_stable_Z(A):
    """给定 A, 求最稳定 Z (对 B/A 求极值, 忽略配对项)"""
    # dB/dZ = 0 → Z* ≈ A / (2 + a_c*A^(2/3)/(2*a_a))
    Z_approx = A / (2 + a_c * A**(2/3) / (2 * a_a))
    # 搜索整数 Z
    best_Z, best_B = 0, 0
    for Z in range(max(1, int(Z_approx)-3), min(A, int(Z_approx)+4)):
        B = binding_per_nucleon(A, Z)
        if B > best_B:
            best_B, best_Z = B, Z
    return best_Z, best_B

print("=== 每核子结合能 ===\n")
print(f"{'核素':>8} {'A':>4} {'Z':>3} {'B/A (MeV)':>10}")
print("-" * 30)
for A, Z, name in [(4,2,"⁴He"), (12,6,"¹²C"), (16,8,"¹⁶O"),
                    (56,26,"⁵⁶Fe"), (58,26,"⁵⁸Fe"), (62,28,"⁶²Ni"),
                    (238,92,"²³⁸U"), (235,92,"²³⁵U")]:
    B = binding_per_nucleon(A, Z)
    print(f"{name:>8} {A:4d} {Z:3d} {B:10.4f}")

# 扫描找极大值
print("\n=== 扫描 B/A 极大值 ===")
best = (0, 0, 0)
for A in range(1, 300):
    Z, B = most_stable_Z(A)
    if B > best[2]:
        best = (A, Z, B)
print(f"B/A 最大值: A={best[0]}, Z={best[1]} ({best[0]}元素的 Z={best[1]} 同位素)")
print(f"  B/A = {best[2]:.4f} MeV")
print(f"\n结论: 56Fe 的 B/A=8.79 是 '著名' 极大值, 但 62Ni 实际更高")

# α 衰变条件
print("\n=== α 衰变能量条件 ===")
for A, Z, name in [(212,84,"²¹²Po"), (238,92,"²³⁸U"), (210,84,"²¹⁰Po")]:
    parent = binding_energy(A, Z)
    daughter = binding_energy(A-4, Z-2)
    alpha = binding_energy(4, 2)
    Q = daughter + alpha - parent
    print(f"  {name}: Q_α = {Q:.2f} MeV ({'衰变' if Q > 0 else '稳定'})")
```

### 代码 3：中微子振荡概率

```python
"""
中微子振荡: 双味近似下的振荡概率
P(νμ→ντ) = sin²(2θ) · sin²(Δm²L/4E)
零依赖纯 Python, 用 ASCII 图展示振荡
"""
import math

# 大气中微子参数
theta = math.radians(45)    # 最大混合
dm2 = 2.5e-3                # Δm²₂₃ (eV²)
sin2_2theta = math.sin(2*theta)**2

def oscillation_prob(L_km, E_GeV):
    """P(νμ→ντ) 双味近似"""
    # 自然单位: Δm²[eV²] L[km] / E[GeV] → 系数 1.267
    phase = 1.267 * dm2 * L_km / E_GeV
    return sin2_2theta * math.sin(phase * math.pi / 180 * 1)**2  # 修正相位

def osc_prob(L_km, E_GeV):
    """修正: phase = Δm² L / 4E, 单位换算后 = 1.267 * dm2 * L / E"""
    arg = 1.267 * dm2 * L_km / E_GeV
    # 1.267 = (Δm² L)/(4E) in [rad] when dm2[eV²], L[km], E[GeV]
    return sin2_2theta * math.sin(arg)**2

# 振荡概率 vs 距离
print("=== νμ → ντ 振荡 (E = 1 GeV, θ₂₃ = 45°, Δm² = 2.5e-3 eV²) ===\n")
E = 1.0  # GeV
print(f"{'L (km)':>10} {'P(νμ→ντ)':>10} {'P(νμ→νμ)':>10} {'bar':>30}")
print("-" * 65)
for L in [0, 100, 250, 500, 750, 1000, 1500, 2000, 3000]:
    P = osc_prob(L, E)
    P_survive = 1 - P
    bar = "█" * int(P * 30)
    print(f"{L:10d} {P:10.4f} {P_survive:10.4f} {bar:>30}")

# 第一个极大值
L_max = math.pi * E / (2 * 1.267 * dm2)  # π/2 处
print(f"\n第一个振荡极大: L ≈ {L_max:.0f} km (E = {E} GeV)")
print(f"  对应 Super-K 大气中微子实验 (上行/下行中微子差异)")

# 能量依赖
print(f"\n=== 固定 L = 1000 km, 扫描能量 ===")
print(f"{'E (GeV)':>10} {'P(νμ→ντ)':>10}")
for E in [0.3, 0.5, 1.0, 2.0, 5.0, 10.0]:
    P = osc_prob(1000, E)
    print(f"{E:10.1f} {P:10.4f}")

print(f"\n结论: 中微子振荡直接证明 ν 有质量 → 标准模型必须扩展!")
```

---

## 📚 教材对比

| 教材 | 定位 | 强项 | 弱项 |
|------|------|------|------|
| **Schwartz** | Harvard 253a/b 主教材 | 现代视角、推导清晰、直奔标准模型 | 习题偏少 |
| **Peskin & Schroeder** | 国际标准 | 路径积分深入、重整化群详细 | 叙述冗长 |
| **Krane** | 核物理入门 | 实验导向、覆盖全面 | 理论深度有限 |

**学习路径**：
1. **Schwartz Ch.1-7**（标量场 + 费曼图）→ 建立场论框架
2. **Schwartz Ch.8-12**（规范理论 + QED）→ 理解规范不变性
3. **Schwartz Ch.25-29**（QCD + 电弱 + 标准模型）→ 核心物理
4. **Krane**（核物理）→ 独立补充，不依赖 QFT

---

## 🔗 与其他课程的衔接

- **← Phys 143a/b（量子力学）**：算符代数、微扰论、自旋是前置
- **← Phys 151（经典力学）**：Lagrangian/Hamiltonian 直接移植到场论
- **→ Phys 210/211r（广义相对论/黑洞）**：AdS/CFT 对偶连接 QFT 与引力
- **→ Harvard 理论组**：Vafa（F-理论）、Strominger（弦论）、Wen（拓扑序）
- **→ 实验**：LHC（CERN）、Super-K（中微子）、LIGO（引力波）

---

*完成日期：2026-08-12 | 课程编号经 Harvard 2025-26 SPS Guide + Grad Requirements 一手核实（Phys 212 实为 Physical Cosmology, Phys 218 实为 Semiclassical QM，粒子物理在 253a/b QFT 序列中教授）*

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：粒子物理研究宇宙最小的"乐高积木"（夸克、轻子、玻色子）和把它们粘在一起的"胶水"（四种力）；核物理专门研究原子核里质子和中子怎么抱团。
>
> **生活类比**：原子像一套乐高。分子是大积木拼的小车，原子是单块积木，原子核是积木中间的"扣子"，质子中子是扣子的塑料，夸克是塑料的分子。粒子物理学家就是在研究"塑料到底由什么组成、为什么能粘住"。
>
> **反直觉发现**：你的体重 99% 不是来自组成你的粒子的质量！上/下夸克的质量只贡献质子质量的 ~1%，剩下 99% 是**把夸克绑在一起的胶子场的能量**（$E=mc^2$）。换句话说，你大部分的质量是"绑胶带的能量"。更震撼的：标准模型这套极其成功的理论，却**完全无法解释**你为什么存在——它预言大爆炸应该产生等量物质和反物质，应该全部湮灭成光，宇宙应该是空的。

---

## 🔗 衔接：从哪来，到哪去

### 前置知识
量子力学（Phys 143a/b）+ 狭义相对论（Morin Ch.11-14）+ 电磁学（规范场概念）+ 群论（SU(N) 表示）。Harvard 的粒子物理在研究生 QFT 序列（Phys 253a/b）中教授。

### 本主题解决了什么危机
20 世纪初，物理学家面对粒子 zoo（粒子动物园）——加速器里发现了几百种"基本粒子"，乱成一团。标准模型用**规范对称性**（SU(3)×SU(2)×U(1)）+ 自发对称破缺（希格斯机制）把这一团乱麻整理成一张优美的表格：12 个费米子（6 夸克+6 轻子）+ 4 种力（胶子、光子、W/Z、引力子待定）+ 希格斯玻色子。2012 年希格斯在 LHC 被发现，标准模型封顶。

### 本主题留下的新危机
1. **暗物质**：星系旋转速度暗示宇宙有 5 倍于可见物质的"看不见的东西"——标准模型里没有候选者
2. **暗能量**：宇宙加速膨胀的驱动力，占宇宙能量 68%，本质完全未知
3. **物质-反物质不对称**：为什么宇宙有物质而不是全变成光？（CP 破坏不够大）
4. **中微子质量**：标准模型说中微子无质量，但振荡实验证明它们有质量——标准模型必须修改
5. **引力没量子化**：标准模型不含引力，与广义相对论在普朗克尺度矛盾
6. **参数之谜**：标准模型有 ~19 个自由参数（粒子质量、耦合常数），为什么是这些值？

### 后续主题
- **← 量子力学（143b）+ 狭义相对论 + 群论**
- **→ 广义相对论/宇宙学（Phys 210/212）**：粒子宇宙学、暗物质、早期宇宙
- **→ 弦论/量子引力**：统一四种力（Harvard Strominger 组）
- **→ 核技术/医学物理**：聚变能源、放疗、同位素

---

## 🏭 理论联系实际：5 个应用

1. **PET 正电子发射断层扫描**：把发射正电子的同位素（如 F-18）标记的葡萄糖注入体内，正电子与电子湮灭产生两个反向 511 keV 光子，探测器符合测量定位代谢活跃区（常是肿瘤）。这是反物质在医学上的日常应用——狄拉克预言的反电子（1932 安德森发现）如今救人性命。

2. **放射治疗与同位素**：钴-60、直线加速器产生的 X 射线/质子束精准杀死癌细胞；碘-131 治甲亢；锝-99m 做 SPECT 显像。核物理的衰变定律（$N(t)=N_0 e^{-\lambda t}$）和截面测量是核医学的基础。

3. **核能：裂变与聚变**：核电站（铀-235 裂变，1 克铀 = 2.7 吨煤的能量）；可控聚变（CFS 的 ARC/SPARC、ITER）。Commonwealth Fusion Systems（MIT 衍生）2026 发表 ARC 设计论文，目标并网发电。$E=mc^2$ 的小质量差 = 巨大能量。

4. **烟雾报警器（α 源电离）**：家用烟雾报警器里有微量镅-241，α 粒子电离空气形成电流，烟尘进入打断电流 → 报警。核物理的最日常应用，每年拯救无数生命。

5. **加速器制造同位素 + 材料改性**：回旋加速器生产医用同位素；离子注入掺杂半导体芯片；加速器中子源做材料辐照测试。粒子物理的"大玩具"催生了整个放射化学工业和芯片制造工艺。

---

## 🔬 最新研究前沿（2024-2026）

### "胶球"——由力组成的粒子——被找到了？
- **发现**：物理学家宣布发现了神秘的"胶球"（glueball）——一种完全由胶子（传递强力的粒子）组成、不含任何夸克的粒子！科学家预言它的存在已数十年，探测它花了漫长时光。这是对量子色动力学（QCD）的关键检验。
- **来源**：Basu，*Nature* (2026-08-12 新闻)。DOI: 10.1038/d41586-026-02498-1

### "企鹅"衰变或终将打破标准模型
- **发现**：CERN 最新 LHC 实验中的"企鹅"（penguin）衰变暗示了奇特的新物理——可能指向超出标准模型的新粒子或新相互作用。这些罕见衰变道的测量精度正在逼近能发现 BSM 物理的临界。
- **来源**：Gibney，*Nature* (2026-05-01 新闻)

### JUNO 实验：逼近中微子质量序
- **发现**：JUNO（江门中微子实验，中国）的首批测量展示了前所未有的精度，物理学家希望它能确定哪种中微子质量最大（质量序问题）——这是修改标准模型的关键输入。
- **来源**：Vahle & Vallari / Castelvecchi，*Nature* 654:330, 582 (2026-06-10)

### μ子 g-2 获突破奖（磁矩异常持续）
- **发现**：μ子反常磁矩的精确测量（Fermilab Muon g-2）持续显示与标准模型预言的偏差，暗示可能存在新粒子。该工作获 2026 年突破奖基础物理学奖（300 万美元），数百名物理学家跨 30 多个机构获奖。
- **来源**：Merali，*Nature* (2026-04-18 新闻)

### 第一台"核钟"开始滴答（钍-229）
- **发现**：两个研究团队创造了期待已久的"核钟"——利用钍-229 同核异能态的超窄跃迁（~8 eV，远低于典型核跃迁的 keV-MeV），精度可能超越原子钟，且对基本常数变化更敏感。
- **来源**：Gibney，*Nature* 655:17 (2026-06-22 新闻)；von der Wense，*Nature Physics* 22:818 (2026-05-29)

### 亚 keV 能区核聚变增强
- **发现**：在钯和钛氢化物中，氘聚变在极低能区达到了有限的产额"地板"——固体材料能强烈重塑核反应环境、改变核反应速率。这对聚变能源和凝聚态-核物理交叉有启示。
- **来源**：Karahadian, Colborne & Munday，*Nature Communications* (2026-07-18)

> 💡 **趋势洞察**：粒子物理正处在"标准模型之后"的十字路口。胶球、企鹅衰变、μ子异常、中微子质量——多个独立线索都指向超出标准模型的新物理。同时，核物理因钍-229 核钟、增强聚变、CFS 聚变商业化而焕发第二春。Harvard 的 Jefferson Lab 合作和理论组（Strominger）都在前沿。

---

## 🗺️ 学习 Roadmap（Harvard 路径）

### 🟢 入门（本科选修 / 自学）
- **教材**：Griffiths *Introduction to Elementary Particles* 2ed
- **核心**：标准模型费米子/玻色子一览、四种基本力、费曼图入门、夸克模型、弱电统一定性
- **里程碑**：能画出 β 衰变、电子-电子散射的费曼图；理解为什么需要希格斯

### 🟡 进阶（Phys 253a/b 量子场论，一年）
- **教材**：Peskin & Schroeder *An Introduction to Quantum Field Theory* + Schwartz *QFT and the Standard Model*
- **核心**：规范场论（杨-米尔斯）、自发对称破缺（希格斯机制）、量子色动力学（QCD）、重整化、费曼图计算
- **里程碑**：能从拉格朗日量推导出电子-μ子散射截面；理解跑动耦合常数

### 🔴 深造（研究生 / 前沿方向）
- **教材**：Weinberg *The Quantum Theory of Fields* 三卷 + Srednicki
- **方向**：超出标准模型（SUSY/大统一/弦论）、味物理、中微子物理、QCD 格点计算、粒子宇宙学
- **Harvard 资源**：Phys 253a/b（QFT 序列）、Strominger 组（弦论/黑洞）、Jefferson Lab 核物理合作

### ✅ 知识检查（自测清单）
- [ ] 标准模型有几个费米子？几种规范玻色子？（12 费米子，4 力的玻色子）
- [ ] 为什么质子质量 99% 不是夸克质量？（胶子场能量，$E=mc^2$）
- [ ] 希格斯机制解决什么问题？（W/Z 有质量但光子无质量的起源）
- [ ] CP 破坏和"你为什么存在"有什么关系？（物质-反物质不对称）
- [ ] 中微子振荡证明了什么？（中微子有质量，标准模型需修改）

> 🔬 粒子物理是"终极还原论"——把宇宙拆到最小。但越拆越发现"最小"背后是优美的对称性，而对称性背后又是更深的谜（为什么是这些对称性？）。
