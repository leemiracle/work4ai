# ETH Zürich · 粒子物理（Phase 2 · 主题 07）

> **课程映射**：`402-3201-00L Particle Physics`
>
> **教材栈**：Griffiths *Introduction to Elementary Particles* 2ed（经典入门）→ Halzen & Martin *Quarks and Leptons*（QCD/QED 直觉经典）→ Schwartz *Quantum Field Theory and the Standard Model*（现代标准，ETH 首选研究生教材）→ Peskin & Schroeder（QFT 权威，衔接 402-2901-00L）
>
> **ETH 特色**：ETH 是 **CERN 的瑞士方主要合作院校**。CERN 位于日内瓦郊外，距 ETH Zürich 约 280 公里（瑞士联邦物理研究的核心枢纽）。ETH 物理系直接参与 LHC 的 ATLAS 和 CMS 实验，以及未来的 FCC（Future Circular Collider）项目。ETH 粒子物理课不仅讲标准模型的优美结构，更连接着 CERN 的实验前沿——学生们可以在课程结束后去 CERN 做毕业论文。Felix Bloch（ETH 校友、NMR 之父、1952 诺奖）和近年来的 ETH-CERN 合作，构成了 ETH 粒子物理的双重血脉：**理论的优美 + 实验的壮观**。

---

## 目录

1. [标准模型：粒子动物园的秩序](#1-标准模型粒子动物园的秩序)
2. [量子电动力学（QED）：精确到 12 位](#2-量子电动力学qed精确到-12-位)
3. [弱相互作用与电弱统一](#3-弱相互作用与电弱统一)
4. [量子色动力学（QCD）：夸克禁闭](#4-量子色动力学qcd夸克禁闭)
5. [Higgs 机制与对称性破缺](#5-higgs-机制与对称性破缺)
6. [Python 数值实验](#6-python-数值实验)
7. [习题集](#7-习题集)
8. [不足与延伸](#8-不足与延伸)

---

## 1. 标准模型：粒子动物园的秩序

### 直觉

20 世纪中叶，粒子加速器发现了上百种「基本粒子」，物理学家戏称其为「粒子动物园」。标准模型的伟大成就在于：**用三条基本原理把整个动物园整理为一个优雅的表格**。

这三条原理是：
1. **规范对称性**（$SU(3)\times SU(2)\times U(1)$）——决定了力的种类
2. **自旋统计**——费米子（物质）自旋 1/2，玻色子（力的载体）自旋 1
3. **量子场论**——每种粒子对应一个场，粒子是场的量子激发

最终图像惊人简洁：**12 种费米子**（6 夸克 + 6 轻子，加上各自反粒子）+ **4 种规范玻色子**（光子、W、Z、胶子）+ **1 种 Higgs 玻色子**。17 种基本粒子构成了宇宙中所有已知的物质和力。

### 标准模型粒子表

**费米子**（自旋 1/2，物质粒子）：

| 代 | 夸克（参与所有力）| 轻子（不参与强作用）|
|----|-----------------|-------------------|
| I | $u$（上夸克）$m \approx 2.2$ MeV | $e$（电子）$0.511$ MeV |
|   | $d$（下夸克）$m \approx 4.7$ MeV | $\nu_e$（电子中微子）$< 0.8$ eV |
| II | $c$（粲夸克）$1.28$ GeV | $\mu$（μ子）$105.7$ MeV |
|    | $s$（奇异夸克）$95$ MeV | $\nu_\mu$（μ中微子）$< 0.17$ MeV |
| III | $t$（顶夸克）$173$ GeV | $\tau$（τ轻子）$1.78$ GeV |
|     | $b$（底夸克）$4.18$ GeV | $\nu_\tau$（τ中微子）$< 18.2$ MeV |

**规范玻色子**（自旋 1，力的载体）：

| 玻色子 | 质量 | 偶合对称性 | 作用 |
|--------|------|-----------|------|
| $\gamma$（光子）| $0$ | $U(1)_{\text{em}}$ | 电磁 |
| $g$（胶子，8 种）| $0$ | $SU(3)_c$ | 强 |
| $W^\pm$ | $80.4$ GeV | $SU(2)_L$ | 弱 |
| $Z^0$ | $91.2$ GeV | $SU(2)_L\times U(1)_Y$ | 弱（中性流）|

**Higgs 玻色子**（自旋 0）：$m_H = 125$ GeV，2012 年 LHC 发现。

**关键观测**：质量跨度从 $\sim 0$（中微子）到 173 GeV（顶夸克），相差 $10^{14}$ 倍。为什么质量谱如此不均匀？标准模型无法回答——质量是「输入参数」，不是理论预言值。这是超越标准模型的动力之一。

### 公式

**标准模型拉格朗日密度**（总框架）：

$$
\mathcal{L}_{\text{SM}} = \mathcal{L}_{\text{gauge}} + \mathcal{L}_{\text{Higgs}} + \mathcal{L}_{\text{fermion}} + \mathcal{L}_{\text{Yukawa}}
$$

**规范场部分**：

$$
\mathcal{L}_{\text{gauge}} = -\frac{1}{4}F_{\mu\nu}^a F^{a\mu\nu} \quad (a \text{ 遍历规范群生成元})
$$

**费米子动能**：

$$
\mathcal{L}_{\text{fermion}} = \bar{\psi}\left(i\gamma^\mu D_\mu - m\right)\psi
$$

其中协变导数 $D_\mu = \partial_\mu + igA_\mu^a T^a$ 包含了费米子与规范场的耦合。

**精细结构常数**（电磁耦合强度）：

$$
\alpha = \frac{e^2}{4\pi\varepsilon_0\hbar c} \approx \frac{1}{137.036}
$$

### 代码演示：标准模型粒子质量谱

```python
"""
标准模型费米子质量谱（对数尺度）。
反直觉: 三代费米子质量跨 14 个数量级。
顶夸克(t)比上夸克(u)重 80000 倍——为什么?
标准模型无法回答这个「代问题」(flavor puzzle)。
"""
import math

fermions = [
    ("ν_e", 0.0000000008e-3, "I"),    # ~0.8 eV → GeV
    ("ν_μ", 0.00000017e-3, "II"),
    ("ν_τ", 0.0000182e-3, "III"),
    ("e",   0.000511, "I"),
    ("u",   0.0022, "I"),
    ("d",   0.0047, "I"),
    ("s",   0.095, "II"),
    ("μ",   0.1057, "II"),
    ("c",   1.275, "II"),
    ("τ",   1.777, "III"),
    ("b",   4.18, "III"),
    ("t",   173.0, "III"),
]

print("=== 标准模型费米子质量谱 (GeV) ===")
print(f"{'粒子':>6} {'质量(GeV)':>12} {'log₁₀(m/eV)':>14} {'代':>4} {'质量条'}")
for name, mass_GeV, gen in sorted(fermions, key=lambda x: x[1]):
    mass_eV = mass_GeV * 1e9
    log_m = math.log10(mass_eV) if mass_eV > 0 else -99
    bar_len = max(0, int((log_m + 1) * 2))
    bar = '█' * bar_len
    print(f"{name:>6} {mass_GeV:>12.2e} {log_m:>14.2f} {gen:>4} {bar}")

print("\n→ 质量跨度: 中微子 ~1 eV 到顶夸克 ~173 GeV = 14 个数量级!")
print("→ 同一类型的粒子跨三代增重: e(0.5MeV) → μ(106MeV) → τ(1777MeV)")
print("→ 但中微子质量极小且几乎简并 → 'seesaw mechanism' 的线索")
print("→ 为什么有三代? 为什么质量如此分布? → 标准模型最大谜题")
```

---

## 2. 量子电动力学（QED）：精确到 12 位

### 直觉

QED 是物理学**最精确的理论**。它对电子反常磁矩的预言值与实验测量值吻合到小数点后 **12 位**——相当于测量地球到月球的距离精确到一根头发的宽度。Feynman 称之为「物理学的明珠」。

QED 的核心思想：**电磁力 = 带电粒子之间交换虚光子**。两个电子互相排斥，因为它们不断抛接虚光子（就像两个人互投球会产生斥力）。Feynman 图把这个过程画成直观的图形——每条线对应一个传播子，每个顶点对应一个耦合 $e$。

**重整化**是 QED 的关键技术：计算中出现无穷大（虚光子动量可到无穷），但通过重新定义质量和电荷（吸收无穷大到可观测量中），最终得到有限且极其精确的预言。这看似数学戏法，实则深刻——它告诉我们裸质量/裸电荷不可观测，可观测量已经包含了所有量子修正。

### 公式

**QED 拉格朗日量**：

$$
\mathcal{L}_{\text{QED}} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}
$$

其中 $D_\mu = \partial_\mu + ieA_\mu$。

**电子磁矩**（Dirac 方程预言）：

$$
\vec{\mu} = -g\frac{e}{2m}\vec{S}, \qquad g = 2 \quad (\text{Dirac})
$$

**反常磁矩**（Schwinger 一阶辐射修正）：

$$
a_e = \frac{g-2}{2} = \frac{\alpha}{2\pi} \approx 0.00116
$$

高阶修正：

$$
a_e = \frac{1}{2}\left(\frac{\alpha}{\pi}\right) - 0.328478965\left(\frac{\alpha}{\pi}\right)^2 + 1.181241456\left(\frac{\alpha}{\pi}\right)^3 - \cdots
$$

**QED 跑动耦合常数**（能量越高，有效电荷越大）：

$$
\alpha(q^2) = \frac{\alpha(0)}{1 - \frac{\alpha(0)}{3\pi}\ln(q^2/m_e^2 c^2)}
$$

### 代码演示：反常磁矩的级数收敛

```python
"""
电子反常磁矩 a_e = (g-2)/2 的 QED 微扰级数。
展示: 各阶贡献递减, 级数快速收敛。
反直觉: 每高一阶多一个虚光子圈, 计算量增加数千倍,
       但贡献以 (α/π) ≈ 0.0023 的比率缩小。
"""
import math

alpha = 1.0 / 137.035999  # 精细结构常数
x = alpha / math.pi       # ~0.00232

# QED 各阶系数 (实验+理论确定)
coeffs = [
    (1, 0.5,                    "Schwinger 1948 (1阶)"),
    (2, -0.328478965,           "Petermann 1957 (2阶)"),
    (3, 1.181241456,            "3阶, 72个Feynman图"),
    (4, -1.9097,                "4阶, 891个Feynman图"),
    (5, 9.16,                   "5阶, 12672个Feynman图"),
]

print("=== 电子反常磁矩 a_e 的 QED 级数 ===")
print(f"精细结构常数 α = 1/{1/alpha:.3f}")
print(f"展开参数 α/π = {x:.6f}")
print(f"\n{'阶':>4} {'系数':>14} {'贡献':>14} {'说明'}")

total = 0
for order, coeff, desc in coeffs:
    contribution = coeff * x**order
    total += contribution
    print(f"{order:>4} {coeff:>14.6f} {contribution:>14.10f}  {desc}")

print(f"\n{'QED理论值:':>20} a_e = {total:.12f}")
print(f"{'实验测量值:':>20} a_e = 0.00115965218028")
print(f"\n→ 5阶QED(12672个Feynman图!)贡献仅 ~9×10⁻¹³")
print("→ 理论与实验吻合到 ~10⁻¹²（物理学最精确的验证）")

# 跑动耦合常数
print(f"\n=== QED 跑动耦合常数 α(q²) ===")
print(f"{'q²/m_e²':>12} {'α(q²)':>10} {'1/α(q²)':>10}")
for log_q2 in [0, 5, 10, 15, 20, 25]:
    q2_ratio = 10**log_q2 if log_q2 > 0 else 1
    alpha_q2 = alpha / (1 - alpha/(3*math.pi) * math.log(q2_ratio))
    print(f"{'10^'+str(log_q2):>12} {alpha_q2:>10.6f} {1/alpha_q2:>10.2f}")
print("→ 能量越高 α 越大（屏蔽减弱），但 QED 在所有可达能量始终弱耦合")
```

> **反直觉发现**：QED 对电子磁矩的预言精确到 12 位有效数字，每提高一阶需要计算多出数量级的 Feynman 图（5 阶需要 12672 个图！），但贡献以 $(\alpha/\pi) \approx 0.0023$ 的比率缩小。这是**微扰展开**有效性的极致体现——展开参数天然小，使无穷级数在实践中截断到几项就够了。

---

## 3. 弱相互作用与电弱统一

### 直觉

弱相互作用是四种基本力中最「怪异」的一种：
1. **极弱**：耦合常数比电磁力小千倍（在低能下）
2. **力程极短**：$W/Z$ 玻色子极重（80-91 GeV），力程 $\sim 10^{-18}$ m
3. **违反宇称（P）最大**：自然界区分分左/右！中微子只有左旋
4. **违反 CP 对称性**：在 $K^0$ 和 $B^0$ 介子衰变中观测到

弱力的标志性过程是 **β 衰变**：$n \to p + e^- + \bar{\nu}_e$。这个反应使中子（自由中子平均寿命 880 秒）不稳定，是核反应堆和恒星核聚变的关键过程。

**电弱统一理论**（Glashow-Salam-Weinberg, 1961-1967，1979 诺奖）是标准模型最辉煌的部分：它证明电磁力和弱力是**同一种力**（电弱力）的两种低能表现。它们的差别纯粹来自 Higgs 机制对对称性的不同破缺——光子保持无质量（远程力），$W/Z$ 获得大质量（近程力）。

### 公式

**费米常数**（弱相互作用强度）：

$$
G_F = \frac{g^2}{4\sqrt{2}M_W^2} = 1.166 \times 10^{-5}\,\text{GeV}^{-2}
$$

**弱混合角**（Weinberg 角）：

$$
\sin^2\theta_W = 1 - \frac{M_W^2}{M_Z^2} \approx 0.231
$$

**W/Z 质量关系**（电弱统一的核心预言）：

$$
M_W = \frac{e}{2\sin\theta_W}v, \qquad M_Z = \frac{M_W}{\cos\theta_W}
$$

其中 $v \approx 246$ GeV 是 Higgs 真空期望值。

**μ子衰变率**（电弱理论的经典检验）：

$$
\Gamma_\mu = \frac{G_F^2 m_\mu^5}{192\pi^3} \quad \Rightarrow \quad \tau_\mu = \frac{1}{\Gamma_\mu} \approx 2.2\,\mu\text{s}
$$

**CKM 矩阵**（夸克代混合）：

$$
\begin{pmatrix}d'\\s'\\b'\end{pmatrix} = V_{\text{CKM}}\begin{pmatrix}d\\s\\b\end{pmatrix}
$$

$V_{\text{CKM}}$ 接近单位矩阵，非对角元很小（如 $|V_{us}| \approx 0.22$），但非零——这是 CP 破坏的来源。

### 代码演示：弱衰变寿命与质量关系

```python
"""
弱衰变寿命 Γ ∝ G_F² m⁵ 的验证。
反直觉: 衰变率正比于质量的5次方!
这意味着: m_τ ≈ 17×m_μ → Γ_τ/Γ_μ ≈ 17⁵ ≈ 140万倍
即 τ 轻子比 μ 子寿命短 ~100万倍。
"""
import math

GF = 1.166e-5  # GeV⁻²

def muon_like_lifetime(mass_GeV, label):
    """Γ ∝ G_F² m⁵, τ = 192π³/(G_F² m⁵) × 辐射修正。"""
    # μ子: m=0.1057 GeV, τ=2.197 μs
    m_mu = 0.105658
    tau_mu = 2.196981e-6  # 秒
    ratio = (m_mu / mass_GeV)**5
    tau = tau_mu * ratio
    return tau

particles = [
    ("μ⁻", 0.105658, "μ → e ν ν̄"),
    ("τ⁻", 1.77686, "τ → (多种模式)"),
    ("π⁺", 0.13957, "π → μ ν_μ (弱衰变)"),
    ("K⁺", 0.49368, "K → μ ν_μ"),
    ("W⁻", 80.379, "W → e ν̄ (树图衰变)"),
    ("中子 n", 0.93957, "n → p e⁻ ν̄_e"),
    ("顶夸克 t", 173.0, "t → b W⁺"),
]

print("=== 弱衰变寿命: τ ∝ 1/m⁵ ===")
print(f"{'粒子':>10} {'m (GeV)':>10} {'τ_预测 (s)':>14} {'说明':>25}")
for name, m, desc in particles:
    tau = muon_like_lifetime(m, name)
    if tau > 1: tau_str = f"{tau:.4e}"
    elif tau > 1e-10: tau_str = f"{tau:.4e}"
    else: tau_str = f"{tau:.2e}"
    print(f"{name:>10} {m:>10.3f} {tau_str:>14} {desc:>25}")

print(f"\n→ τ轻子(m=1.78GeV)寿命 = {muon_like_lifetime(1.77686,'τ')*1e12:.1f} ps")
print(f"  实际值 ≈ 290 fs = 0.29 ps（辐射修正后吻合）")
print(f"\n→ 顶夸克(m=173GeV): τ ≈ {muon_like_lifetime(173.0,'t')*1e25:.2f} × 10⁻²⁵ s")
print(f"  实际值 ≈ 5 × 10⁻²⁵ s（比强子化时间还短!）")
print(f"\n→ m⁵ 定律: 质量越大衰变越快 → 重粒子寿命极短")
print(f"→ 这是弱衰变的标志特征，电磁/强衰变不遵循此律")
```

> **反直觉发现**：弱衰变率正比于 $m^5$。$\tau$ 轻子比 $\mu$ 子重 17 倍，但寿命短 $17^5 \approx 140$ 万倍。顶夸克重 173 GeV，寿命 $\sim 10^{-25}$ 秒——比强子化时间还短，所以顶夸克在衰变前来不及形成强子束缚态（唯一「自由夸克」）。

---

## 4. 量子色动力学（QCD）：夸克禁闭

### 直觉

QCD 描述夸克之间的强相互作用。它的结构类似 QED，但有一个关键区别：**胶子本身带色荷**（光子不带电）。这个区别导致两个截然不同的后果：

1. **渐近自由**（Asymptotic Freedom, Gross-Politzer-Wilczek 1973，2004 诺奖）：高能（短距离）下夸克间耦合变弱，接近自由粒子。这解释了为什么深度非弹性散射实验中质子内的夸克看起来「准自由」。

2. **夸克禁闭**（Color Confinement）：低能（长距离）下耦合增强，夸克无法被分离。当你试图把两个夸克拉开，色场线聚集成「流管」（flux tube），能量线性增长。当能量足够大时，流管断裂，从真空中产生新的夸克-反夸克对——你得到的不是自由夸克，而是新的强子（喷注 jet）。

**ETH-CERN 关联**：LHC 的 ALICE 实验专门研究夸克-胶子等离子体（QGP）——在极端高温下夸克解除禁闭的状态（宇宙大爆炸后微秒内存在的物质形态）。

### 公式

**QCD 拉格朗日量**：

$$
\mathcal{L}_{\text{QCD}} = \bar{q}(i\gamma^\mu D_\mu - m)q - \frac{1}{4}G_{\mu\nu}^a G^{a\mu\nu}
$$

协变导数 $D_\mu = \partial_\mu + ig_s G_\mu^a T^a$（$T^a$ 为 $SU(3)$ 生成元，$a=1,\ldots,8$）。

**色荷**：夸克有 3 种色（红、绿、蓝），胶子有 $3\times 3 - 1 = 8$ 种色组合。

**QCD 跑动耦合**（与 QED 相反方向！）：

$$
\alpha_s(q^2) = \frac{12\pi}{(33-2n_f)\ln(q^2/\Lambda_{\text{QCD}}^2)}
$$

其中 $n_f$ 为活跃味数（夸克味），$\Lambda_{\text{QCD}} \approx 200$ MeV 是 QCD 尺度。

**关键区别**：
- QED：$\beta > 0$，能量越高 $\alpha$ 越大（屏蔽减弱）
- QCD：$\beta < 0$，能量越高 $\alpha_s$ 越小（反屏蔽/渐近自由）

**夸克势**（唯象模型）：

$$
V(r) = -\frac{4}{3}\frac{\alpha_s}{r} + \sigma r
$$

短距离库仑样 $-1/r$，长距离线性 $\sigma r$（$\sigma \approx 1$ GeV/fm 为弦张力）。

### 代码演示：QCD 耦合常数的跑动

```python
"""
QCD vs QED 跑动耦合常数对比。
反直觉: QED 的 α(q²) 随能量增加(反屏蔽),
       QCD 的 αs(q²) 随能量减小(渐近自由)。
根本原因: 胶子带色荷, 自相互作用产生反屏蔽。
"""
import math

Lambda_QCD = 0.2  # GeV, QCD特征尺度
n_f = 5            # 活跃夸克味数
alpha_em_0 = 1.0/137.036  # 低能电磁耦合

def alpha_QCD(Q_GeV):
    """QCD 跑动耦合 (1圈修正)。Q = 能量尺度。"""
    if Q_GeV <= Lambda_QCD:
        return float('inf')  # 微扰论失效(禁闭区)
    b0 = (33 - 2*n_f) / (12*math.pi)
    return 1.0 / (b0 * math.log(Q_GeV**2 / Lambda_QCD**2))

def alpha_QED(Q_GeV):
    """QED 跑动耦合。Q = 能量尺度。"""
    m_e = 0.000511  # GeV
    ratio = (Q_GeV/m_e)**2 if Q_GeV > m_e else 1
    return alpha_em_0 / (1 - alpha_em_0/(3*math.pi) * math.log(ratio))

print("=== QCD vs QED 跑动耦合常数 ===")
print(f"{'Q (GeV)':>10} {'α_s(QCD)':>10} {'α(QED)':>10} {'说明':>20}")
energies = [0.3, 0.5, 1.0, 2.0, 5.0, 10.0, 91.2, 173.0, 1000.0]
for Q in energies:
    as_qcd = alpha_QCD(Q)
    a_qed = alpha_QED(Q)
    note = ""
    if Q < 0.5: note = "禁闭区(微扰不可靠)"
    elif Q < 2: note = "强耦合"
    elif Q < 10: note = "中等耦合"
    elif Q < 100: note = "弱耦合(渐近自由)"
    else: note = "极弱耦合"
    if math.isfinite(as_qcd):
        print(f"{Q:>10.1f} {as_qcd:>10.4f} {a_qed:>10.6f} {note:>20}")
    else:
        print(f"{Q:>10.1f} {'∞':>10} {a_qed:>10.6f} {note:>20}")

print(f"\n→ Z玻色子质量处(Q=91GeV): α_s ≈ {alpha_QCD(91.2):.4f} (实验~0.118)")
print(f"→ 顶夸克质量处(Q=173GeV): α_s ≈ {alpha_QCD(173):.4f}")
print(f"→ Q→∞: α_s→0（渐近自由，夸克近似自由）")
print(f"→ Q→Λ_QCD: α_s→∞（禁闭，微扰失效）")
print(f"\n对比QED: α在所有能量都小(<0.01), 始终可微扰")
print(f"→ QCD的α_s在不同能区差别巨大 → 需要'有效理论'策略")
```

> **反直觉发现**：QCD 的耦合常数在低能（$Q \sim \Lambda_{\text{QCD}} \approx 200$ MeV）趋向无穷大，在高能趋向零。这意味着强相互作用在**高能是弱**的（可微扰计算），在**低能是强**的（需格点 QCD 等非微扰方法）。这与日常直觉「近距离力更强」截然相反——渐近自由是 20 世纪物理最深刻的发现之一。

---

## 5. Higgs 机制与对称性破缺

### 直觉

标准模型有一个根本问题：规范对称性要求规范玻色子（$W, Z$）**无质量**——但实验测得 $W$ 和 $Z$ 分别重 80 和 91 GeV。如何解决这个矛盾？

Higgs 机制（Higgs, Englert, Brout, 1964；2013 诺奖）的解答精妙绝伦：**引入一个标量场（Higgs 场），它的真空期望值非零，自发破缺电弱对称性**。对称性破缺后，$W/Z$ 通过与 Higgs 场的耦合获得质量，而光子保持无质量（因为电磁 $U(1)$ 对称性未被破缺）。

更深刻的是：**所有费米子的质量也来自与 Higgs 场的 Yukawa 耦合**。顶夸克之所以重（173 GeV），是因为它与 Higgs 的耦合最强（$y_t \approx 1$）。电子之所以轻（0.5 MeV），是因为其 Yukawa 耦合极弱（$y_e \approx 10^{-6}$）。**质量不是粒子的内禀属性，而是它与 Higgs 场的相互作用**——这是标准模型最反直觉的洞察之一。

2012 年 7 月 4 日，CERN 的 ATLAS 和 CMS 实验宣布发现质量约 125 GeV 的新玻色子，后被确认为 Higgs 粒子——标准模型的最后一块拼图终于到位。

### 公式

**Higgs 势**（Mexican hat 势）：

$$
V(\phi) = \mu^2|\phi|^2 + \lambda|\phi|^4, \quad \mu^2 < 0
$$

最小值在 $|\phi| = v/\sqrt{2}$，其中**真空期望值**：

$$
v = \sqrt{-\mu^2/\lambda} \approx 246\,\text{GeV}
$$

**W/Z 获得质量**：

$$
M_W = \frac{gv}{2} \approx 80.4\,\text{GeV}, \quad M_Z = \frac{M_W}{\cos\theta_W} \approx 91.2\,\text{GeV}
$$

**Higgs 玻色子质量**：

$$
m_H = \sqrt{2\lambda}\,v = \sqrt{-2\mu^2} \approx 125\,\text{GeV}
$$

**费米子质量**（Yukawa 耦合）：

$$
m_f = \frac{y_f v}{\sqrt{2}}
$$

### 代码演示：Mexican Hat 势与自发破缺

```python
"""
Higgs 势 V(φ) = μ²|φ|² + λ|φ|⁴ (μ²<0) 的 'Mexican Hat' 形状。
展示: 对称势 → 不对称真空。
反直觉: 势能具有完美的旋转对称性, 但真空选择了一个特定方向!
这就是 '自发对称性破缺' 的本质——不是对称性本身被破坏,
而是基态(真空)不尊重它。
"""
import math

mu2 = -1.0  # μ² < 0（关键!）
lam = 0.5   # λ > 0

def higgs_potential(phi):
    """V(φ) = μ²φ² + λφ⁴，φ = |φ|。"""
    return mu2 * phi**2 + lam * phi**4

# 求最小值
# dV/dφ = 2μ²φ + 4λφ³ = 0 → φ(μ² + 2λφ²) = 0
# φ=0 是最大值（V=0），φ² = -μ²/(2λ) 是最小值
v = math.sqrt(-mu2 / (2*lam))
V_min = higgs_potential(v)
V_origin = higgs_potential(0)

print("=== Higgs Mexican Hat 势 ===")
print(f"V(φ) = {mu2}·φ² + {lam}·φ⁴")
print(f"\n{'φ':>8} {'V(φ)':>10} {'说明':>25}")
for phi_frac in [0.0, 0.2, 0.5, 0.8, 1.0, 1.5, 2.0]:
    phi = phi_frac * v if v > 0 else phi_frac
    V = higgs_potential(phi)
    note = ""
    if phi_frac == 0: note = "φ=0: 局部最大!(不稳定)"
    elif abs(phi_frac - 1.0) < 0.01: note = f"真空 v = {v:.4f} (最小值)"
    elif phi_frac > 1.2: note = "远离真空, 势能升高"
    print(f"{phi:>8.4f} {V:>10.4f} {note:>25}")

print(f"\n真空期望值 v = √(-μ²/2λ) = {v:.4f}")
print(f"V(0) = {V_origin:.4f} (对称点, 不稳定!)")
print(f"V(v) = {V_min:.4f} (真空, 能量最低)")
print(f"\n→ 势能 V(φ) 在 φ 空间具有旋转对称性")
print(f"→ 但真空 |φ|=v 的圆上每一点都是等价的最低能态")
print(f"→ 大自然'选择'了其中一个方向 → 对称性自发破缺")

# 粒子获得质量
print(f"\n=== Higgs 机制: 粒子如何获得质量 ===")
print(f"真空期望值 v ≈ 246 GeV (真实物理值)")
v_phys = 246.0
# m_f = y_f × v / √2
print(f"{'粒子':>8} {'m (GeV)':>10} {'Yukawa y_f':>12}")
fermions_higgs = [
    ("e", 0.000511), ("μ", 0.1057), ("τ", 1.777),
    ("u", 0.0022), ("c", 1.275), ("t", 173.0),
    ("d", 0.0047), ("s", 0.095), ("b", 4.18),
]
for name, m in sorted(fermions_higgs, key=lambda x: x[1]):
    yf = m * math.sqrt(2) / v_phys
    print(f"{name:>8} {m:>10.4f} {yf:>12.6f}")

print(f"\n→ 顶夸克 y_t ≈ {173*math.sqrt(2)/v_phys:.3f} ≈ 1（强耦合）")
print(f"→ 电子 y_e ≈ {0.000511*math.sqrt(2)/v_phys:.2e}（极弱耦合）")
print(f"→ 质量差异 = 与Higgs场耦合强度的差异")
print(f"→ 为什么耦合如此不同? → 标准模型未解之谜!")
```

> **反直觉发现**：Higgs 势 $V(\phi) = -|\mu^2|\phi^2 + \lambda\phi^4$ 在 $\phi$ 空间具有**完美旋转对称性**（一个墨西哥帽的形状），但**真空不在对称中心** $\phi=0$（那里是不稳定的最大值！），而在帽檐上任意一点 $\phi = v$。大自然选择了一个方向，对称性就「自发破缺」了。这就像一支竖立的铅笔——理论上各个方向等价，但一旦倒下就选了一个特定方向。

---

## 6. Python 数值实验

### 6.1 粒子碰撞运动学（质心系）

```python
"""
LHC 质子-质子对撞的质心能量计算。
反直觉: 固定靶实验 vs 对撞机: 同样能量的束流,
       对撞机产生的质心能量高得多。
这是为什么 LHC 用对撞机而非固定靶。
"""
import math

# LHC 参数
E_beam = 7000  # GeV = 7 TeV (每束)
m_p = 0.938    # GeV, 质子质量

# 对撞机: 两个 7TeV 质子对头碰撞
sqrt_s_collider = 2 * E_beam
print("=== LHC 对撞机 vs 固定靶 ===")
print(f"束流能量: {E_beam} GeV = {E_beam/1000} TeV/束")
print(f"\n对撞机(对头碰): √s = 2×E_beam = {sqrt_s_collider} GeV = {sqrt_s_collider/1000} TeV")

# 固定靶: 一个 7TeV 质子打静止质子
# √s = √(2m_p(E_beam + m_p)) ← 远小于对撞机!
sqrt_s_fixed = math.sqrt(2 * m_p * (E_beam + m_p))
print(f"固定靶(打静止质子): √s = √(2m_p·E) = {sqrt_s_fixed:.1f} GeV = {sqrt_s_fixed/1000:.2f} TeV")

ratio = sqrt_s_collider / sqrt_s_fixed
print(f"\n→ 对撞机效率是固定靶的 {ratio:.0f} 倍!")
print(f"→ 要在对撞机达到 14TeV, 固定靶需要 E ∝ s/(2m) = {(sqrt_s_collider**2)/(2*m_p):.0f} GeV")
print(f"  = {sqrt_s_collider**2/(2*m_p)/1e6:.0f} × 10⁶ GeV = {sqrt_s_collider**2/(2*m_p)/1e9:.0f} PeV")
print("→ 固定靶达到 LHC 能量需要加速到 ~10⁸ TeV (不可能!)")
print("→ 这就是为什么粒子物理使用对撞机")
```

### 6.2 衰变分支比与运动学

```python
"""
Z玻色子衰变分支比。
Z(91.2 GeV) 衰变到各费米子对的分支比。
反直觉: Z 衰变到 invisible(中微子) 占 ~20%!
这是 LEP 精确测量轻子代数的依据。
"""
import math

# Z→ff 的偏宽度 ∝ N_c × (g_V² + g_A²) × m_Z
# 其中 g_V, g_A 依赖费米子类型, N_c = 色数

MZ = 91.1876  # GeV

# 各衰变道的偏宽度（归一化，单位 arb）
decays = [
    ("e⁺e⁻",     1, 84.0),
    ("μ⁺μ⁻",     1, 84.0),
    ("τ⁺τ⁻",     1, 84.0),
    ("ν_eν̄_e",   1, 167.0),  # 中微子 g_V ≈ g_A, 宽度翻倍
    ("ν_μν̄_μ",   1, 167.0),
    ("ν_τν̄_τ",   1, 167.0),
    ("qq̄ (每味)", 3, 377.0),  # 3色 × 某宽度
]

# 夸克道还要乘以色数和味数
quark_flavors = 5  # u,d,s,c,b (t太重不能产生)
# 实际Z→qq̄总宽度 ≈ 每味 × 5味
total_hadronic = 377.0 * quark_flavors

total_lep = 3 * 84.0
total_inv = 3 * 167.0
total = total_hadronic + total_lep + total_inv

print("=== Z⁰ 玻色子衰变分支比 ===")
print(f"Z 质量 = {MZ} GeV, 总宽度 Γ_Z ≈ 2.495 GeV")
print(f"\n{'道':>12} {'Γ偏':>8} {'分支比':>8}")
for label, _, width in decays[:6]:
    br = width / total * 100
    print(f"{label:>12} {width:>8.1f} {br:>7.2f}%")
print(f"{'qq̄ (总)':>12} {total_hadronic:>8.1f} {total_hadronic/total*100:>7.2f}%")
print(f"{'合计':>12} {total:>8.1f} {'100.00':>8}%")

inv_frac = total_inv / total
print(f"\n→ Z → 不可见(中微子) 分支比 = {inv_frac*100:.1f}%")
print(f"  (实验值 ≈ 20.0%)")
print(f"→ 三代中微子贡献: {inv_frac*100/3:.1f}% / 代")
print(f"→ 如果有第4代轻中微子: 不可见分支比应为 {inv_frac*100*4/3:.1f}%")
print(f"  实验排除 → 轻中微子恰好3代（标准模型确认!）")
```

---

## 7.习题集

### 基础题（Griffiths 级别）

**P7.1** 用海森堡不确定性原理估算 $\pi$ 介子（介导核力的虚粒子）的质量。核力力程 $R \approx 1.4$ fm。

> **答案**：$m_\pi \approx \hbar/(cR) \approx 140$ MeV/$c^2$（与实际 $\pi$ 介子质量吻合！这是 Yukawa 的伟大预言）。

**P7.2** 电子和 $\mu$ 子质量相近（$m_\mu \approx 207 m_e$），但 $\mu$ 子会衰变 $e^+\nu_e\nu_\mu$。为什么电子稳定？

> **提示**：电子是最轻的带电粒子，没有更轻的带电粒子可衰变。

### 中级题（Halzen & Martin 级别）

**P7.3**（QED）计算电子 $g-2$ 的 Schwinger 一阶修正 $a_e^{(1)} = \alpha/(2\pi)$。从这个结果出发，估算需要几阶 QED 修正才能达到 $10^{-12}$ 的精度。

**P7.4**（电弱）从 $M_W = 80.4$ GeV 和 $\sin^2\theta_W = 0.231$ 推算 $M_Z$ 和 Higgs 真空期望值 $v$。

> **答案**：$M_Z = M_W/\cos\theta_W \approx 91.2$ GeV，$v = 2M_W\sin\theta_W/e \approx 246$ GeV。

**P7.5**（CKM 矩阵）利用 Wolfenstein 参数化，证明 CKM 矩阵接近单位矩阵但非对角元不为零。解释为什么 $|V_{td}| \ll |V_{us}|$（顶到底跃迁远弱于上到奇异）。

### 挑战题（Schwartz / ETH 考试级别）

**P7.6**（渐近自由）从 QCD 的 $\beta$ 函数 $\beta(g) = -b_0 g^3/(16\pi^2)$ 出发，推导跑动耦合 $\alpha_s(Q^2)$ 的表达式。解释为什么 $n_f \leq 16$ 时才有渐近自由（$b_0 > 0$）。

**P7.7**（Higgs 物理）从 Higgs 势 $V(\phi) = -\mu^2\phi^2 + \lambda\phi^4$ 出发，推导：(a) 真空期望值 $v$；(b) Higgs 粒子质量 $m_H$；(c) 顶夸克质量 $m_t = y_t v/\sqrt{2}$。给定 $m_t = 173$ GeV，求 $y_t$。

**P7.8**（CERN 应用）LHC 在 $\sqrt{s} = 14$ TeV 下产生 Higgs 粒子（$gg \to H$，通过顶夸克圈）。估算产生截面 $\sigma(gg\to H)$ 的数量级，并与 ATLAS/CMS 的实验测量值（$\sim 50$ pb）比较。

> **CERN 关联**：ETH 参与 ATLAS 和 CMS 实验。Higgs 发现论文（2012）的作者列表中有 ETH 物理系的贡献者。

---

## 8. 不足与延伸

### 本主题的局限

1. **标准模型不是终极理论**：
   - 不包含引力
   - 不解释暗物质（占宇宙 27%）和暗能量（68%）
   - 中微子质量需要超出标准模型的物理（右手中微子？Seesaw？）
   - 物质-反物质不对称需要更大的 CP 破坏（CKM 不够）
   - 「代问题」和「质量谱」无理论解释

2. **强相互作用低能区的困难**：微扰 QCD 在 $Q \sim \Lambda_{\text{QCD}}$ 失效。夸克禁闭、质子质量（大部分来自 QCD 结合能而非夸克质量）等基本问题需要格点 QCD 数值模拟——计算极其昂贵。

3. **自然性问题**：Higgs 质量的辐射修正 $\delta m_H^2 \sim \Lambda^2$（$\Lambda$ 为新物理截止），若 $\Lambda \sim M_{\text{Planck}}$ 则需要 $10^{30}$ 级别的精细调节。解决方案（超对称？复合 Higgs？）尚无实验支持。

4. **真空稳定性**：$m_H = 125$ GeV 处于亚稳态边界——标准模型真空可能在极长时间尺度上不稳定（衰变到真正的最低能态）。这是否与宇宙学有关？

### 延伸方向

| 方向 | 课程/教材 |
|------|----------|
| 量子场论 | ETH 402-2901-00L / Peskin & Schroeder |
| 弦理论 | ETH 402-3601-00L / Polchinski |
| 宇宙学 | ETH 402-3301-00L / Dodelson |
| 中微子物理 | Zyla et al. *PDG Review* |
| 格点 QCD | Gattringer & Lang |
| 超出标准模型 | 暗物质/超对称/额外维度 |

### ETH 特色注记

ETH 的粒子物理深度绑定 **CERN**——全球最大的粒子物理实验室。CERN 的 LHC（大型强子对撞机）是人类建造的最大科学装置（27 公里周长），ETH 物理系是 ATLAS 和 CMS 两大探测器的核心参与方。ETH 学生可以在本科阶段就去 CERN 参与暑期实习，毕业后直接加入 CERN 的研究团队。

ETH 的**理论粒子物理**传统同样辉煌：从 Felix Bloch（NMR，1952 诺奖，ETH 校友）到现代的 ETH 弦理论组（Niklas Beisert 等在 $\mathcal{N}=4$ 超对称 Yang-Mills 的可积性方面的工作），ETH 在粒子物理理论和实验两端均有顶尖贡献。

**ETH-CERN 的独特优势**在于「近距离」——ETH 到 CERN 仅 280 公里（瑞士联邦的南北两端），高铁 3 小时可达。ETH 物理系的粒子物理方向学生常年在 CERN 和 ETH 之间穿梭：在 ETH 学标准模型理论，在 CERN 跑真实数据分析。这种理论-实验的无缝结合，是 ETH 粒子物理教育不可复制的独特优势。未来 FCC（Future Circular Collider，100 公里周长）的规划中，ETH 也将是瑞士方的核心参与者——粒子物理的未来，在 ETH 继续。

---

> **上一主题**：[06 固体物理](../topic06-solid-state/solid-state.md)
>
> **下一主题**：[08 广义相对论与宇宙学](../topic08-gr-cosmology/gr-cosmology.md) — 从时空几何到大爆炸


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：粒子物理研究「世界的最小砖块是什么、它们如何粘合」——标准模型用 12 种费米子 + 4 种规范玻色子 + 1 个 Higgs 描述了除引力之外的一切，并预言了至今全部的实验室结果（精度达 12 位）。
>
> **生活类比**：把宇宙想象成一场**乐高派对**。12 种费米子是「积木」（夸克 + 轻子），4 种玻色子是「胶水」（光子、胶子、W/Z），Higgs 是「派对的暖场 DJ」——它给积木赋质量，没有 DJ 大家都是无质量的瘦子（光子）。标准模型 = 这场派对的规则手册，缺一不可。
>
> **反直觉发现（啊哈时刻）**：
> - **质量 99% 来自动能，不是 Higgs**：质子质量 938 MeV，组成夸克静止质量才 ~10 MeV——其余 99% 是夸克 + 胶子的相对论动能与场能。Higgs 只给夸克「裸质量」。
> - **CP 破坏是「我们存在」的原因**：宇宙诞生时正反物质等量，若没有 CP 不对称，早已全部湮灭成光——我们活着本身就是 CP 破坏的证据（但标准模型的 CP 破坏量级不够，新物理必须存在）。
> - **中微子有质量是「标准模型的裂痕」**：标准模型预言中微子零质量，1998 年 Super-K 发现振荡 → 标准模型必须扩展。
> - **渐近自由**：夸克越靠近，相互作用越弱（Gross-Politzer-Wilczek 2004 诺奖）——你越想分开它们，胶子「管子」越紧，单夸克永远被囚禁。
> - **宇宙 95% 看不见**：暗物质 + 暗能量占 95%，标准模型只描述 5% 的「普通物质」——粒子物理的最大尴尬也是最大机会。

---

## 🔗 衔接：从哪来，到哪去

### ▶ 前置
- **量子力学（03）**：自旋、全同粒子、规范对称——粒子物理是「把量子力学推到相对论极限」。
- **量子场论（主题 05+07 衔接）**：把粒子视为场的激发；Feynman 图是路径积分的图形化。
- **群论（05）**：标准模型规范群 SU(3)×SU(2)×U(1) 是粒子分类的语法。

### ⚡ 旧框架的危机
1. **β 衰变能量不守恒**：Pauli 1930 假设「中微子」拯救能量守恒——直到 1956 年才直接探测到。
2. **强相互作用太强**：微扰 QED 套路失效 → QCD + 渐近自由 + 夸克禁闭。
3. **弱作用手征**：W 只耦合左旋粒子——宇称被李杨（1957 诺奖）打破，宇宙有「手性」。

### 🆕 新框架的危机
- **Higgs 后无新物理**：2012 发现 Higgs，但 supersymmetry / 额外维度 / 复合 Higgs 在 LHC Run 2 都没出现——「自然性」危机。
- **暗物质无信号**：LZ、XENONnT 直接探测极限压到 $10^{-47}$ cm² 仍空——WIMP 范围被严重压缩。
- **(g-2)μ 与 W 质量异常**：缪子反常磁矩 5σ 偏离、CDF 测 W 质量偏移——若属实即新物理，但需独立确认。

### 🚀 后续
| 后续主题 | 用到的粒子概念 |
|---------|---------------|
| 08 GR/宇宙学 | 早期宇宙粒子物理（暴胀、重子生成、核合成）、暗物质粒子候选 |
| 06 固体物理 | 凝聚态类比（Higgs 机制 = 超导序参量，Goldstone = 声子） |

---

## 🏭 理论联系实际：5 个应用

1. **CERN / LHC 与 ETH**：ETH 物理系是 ATLAS、CMS、LHCb 核心成员；27 km 周长对撞机每秒 40 million 次质子碰撞，ETH 学生做本科论文就能处理真实数据。
2. **医疗粒子治疗**：质子 / 碳离子治疗肿瘤（PSI 的 PROSCAN 中心）——布拉格峰精准释放剂量在肿瘤位置，副作用远低于 X 射线。QED 与加速器物理的医学副产品。
3. **PET 正电子发射断层**：β⁺ 衰变产生的正电子与电子湮灭 → 一对 511 keV 光子；医院里的粒子物理。
4. **同步辐射与散裂中子源**：PSI 的 SLS 2.0（光子）、SINQ（中子）、SwissFEL（X 射线自由电子激光）——粒子加速器反过来研究凝聚态、化学、生物。
5. **超算格点 QCD**：在超级计算机上离散化时空格点，精确计算强子性质——ETH 理论组、CERN 理论部用此预言 (g-2)μ 的标准模型值，决定新物理的存在与否。

---

## 🔬 最新研究前沿（2024-2026）

1. **Muon g-2 最终结果（5σ 偏离）**（2024.08，Fermilab）：缪子反常磁矩最终实验值与标准模型预言（取决于 e⁺e⁻ 数据 vs BMW 格点 QCD）存在约 5σ 偏离——若以传统色散关系为准，这是迄今最可靠的新物理信号。ETH 理论组参与格点 QCD 评估。
2. **KATRIN 直接中微子质量上限**（2024.04，*Nature Phys.）：氚 β 衰变给出 $m(\nu_e)<0.8$ eV（95% CL）——首次突破 1 eV，约束宇宙学中微子质量和、轻子数破坏模型。
3. **FCC 可行性研究获批**（2024.02 CERN 理事会；2025 报告）：未来 91 km 周长对撞机（FCC-ee → FCC-hh）进入正式设计阶段，目标 2040s 投入运行；ETH 作为瑞士核心方深度参与，目标是 Higgs 工厂 + 100 TeV 强子对撞。
4. **暗物质直接探测极限再压低**（2024-2025）：LZ（ Sanford ）与 XENONnT（Gran Sasso）联合结果将 WIMP-核子散射截面下限压至 ~$10^{-48}$ cm²，仍未发现信号；轴子搜索（ADMX、ALPS-II、IAXO）成为新希望，ETH 参与 IAXO 的 X 光学系统。
5. **中微子振荡精确化与 CP 相位**（2024-2025）：T2K、NOvA、Super-K 持续累积数据，CP 破坏相位 δ_CP 初步指向 $-\pi/2$（最大 CP 破坏方向），DUNE（2030s）将给出决定性测量——重子生成之谜的关键拼图。

---

## 🗺️ 学习 Roadmap（ETH 路径）

### ETH 课程编号
- **402-2901-00L Quantum Field Theory I**（MSc，Peskin & Schroeder）
- **402-2902-00L Quantum Field Theory II**（规范理论、标准模型）
- **402-0817-00L Particle Physics**（BSc/MSc，Halzen & Martin / Griffiths）
- **402-9305-00L Astroparticle Physics**（暗物质 / 宇宙线，对接 CERN 与地下实验室）

### 14 周学习节奏
| 阶段 | 内容 | 知识检查 |
|------|------|----------|
| W1-3 相对论量子力学 | Klein-Gordon、Dirac 方程、反粒子 | 解释为什么 Dirac 方程自然预言自旋 1/2 与正电子。 |
| W4-6 规范对称 | U(1) QED、SU(2) 弱、SU(3) 色、Higgs 机制 | 推出 W/Z 质量来自 Higgs，光子为何无质量。 |
| W7-9 标准模型 | 费米子家族、Feynman 图、跑动耦合 | 画 e⁺e⁻ → μ⁺μ⁻ 的树图并算截面。 |
| W10-11 QCD | 渐近自由、禁闭、强子化 | 解释为什么单夸克永远分离不出来。 |
| W12-14 超出标准模型 | 中微子质量、暗物质、CP、大统一 | 列出三种暗物质候选（WIMP / 轴子 / 惰性中微子）。 |

### 费曼检验
- 能解释「质子质量 99% 不是 Higgs 给的」 → QCD 过关。
- 能讲清「CP 破坏为什么是宇宙存在的前提」 → 标准模型过关。
- 能从规范对称推出 W/Z 的质量公式 → 可进 BSM 与弦论。
