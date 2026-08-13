# Topic 07 · 粒子物理与核物理 — Caltech Ph 109

> **课程链**：Ph 7b/12b（量子力学基础）→ Ph 109 *Elementary Particles*（Griffiths 粒子物理）→ Ph 230ab *Nuclear and Particle Physics*（Halzen & Martin / Peskin & Schroeder 研究生级）
>
> **教材三角**：Griffiths *Introduction to Elementary Particles* 2ed（最友好的入门，Caltech Ph 109 标准）· Halzen & Martin *Quarks and Leptons*（经典中级教材）· Perkins *Introduction to High Energy Physics* 4ed（实验视角补充）

---

## Caltech 特色：Feynman 图传统 + 高能实验

Caltech 的粒子物理教学有两个独树一帜的基因：

1. **Feynman 图的诞生地**——Richard Feynman 在 Caltech 工作（1949 年起）。他的**Feynman 图**（1948–1949）彻底改变了粒子物理的计算方式：把复杂的量子电动力学（QED）微扰展开，变成了一目了然的图形语言。Caltech 的 Ph 109 教学直接传承了这种**图先于方程**的风格——先画出物理过程，再写出振幅。

2. **Caltech 高能实验传统**——Caltech 参与了费米实验室（Fermilab）和欧洲核子研究中心（CERN）的多个大型实验合作。Caltech 实验组对顶夸克发现（1995）和 Higgs 玻色子发现（2012）都有直接贡献。Caltech 理论组在弦理论（John Schwarz）、量子引力等方面也有深远影响。

---

## §1 标准模型总览

### 1.1 基本粒子

> 标准模型是现代物理学的最高成就之一——用一组简洁的原理（规范对称性 + 自发对称破缺）统一了除引力以外的所有基本相互作用。

**费米子**（自旋 1/2，物质粒子）分为三代：

| 代 | 轻子（不参与强作用）| 夸克（参与强作用）|
|----|------|------|
| 第一代 | $e^-$（电子），$\nu_e$（电子中微子）| $u$（上），$d$（下）|
| 第二代 | $\mu^-$（μ子），$\nu_\mu$ | $c$（粲），$s$（奇）|
| 第三代 | $\tau^-$（τ子），$\nu_\tau$ | $t$（顶），$b$（底）|

每个费米子还有对应的**反粒子**（相同质量、相反电荷/量子数）。

**规范玻色子**（自旋 1，力的传递者）：

| 玻色子 | 相互作用 | 质量 |
|--------|---------|------|
| 光子 $\gamma$ | 电磁力 | 0 |
| $W^\pm, Z^0$ | 弱力 | $\sim 80$–$91\,\text{GeV}/c^2$ |
| 胶子 $g$（8种）| 强力 | 0 |

**Higgs 玻色子**（自旋 0）：$H$，质量 $\sim 125\,\text{GeV}/c^2$，2012 年在 LHC 发现。

### 1.2 四种基本力

| 力 | 相对强度 | 力程 | 传递者 |
|----|---------|------|--------|
| 强力 | 1 | $\sim 10^{-15}\,\text{m}$ | 胶子 |
| 电磁力 | $1/137$ | $\infty$ | 光子 |
| 弱力 | $10^{-6}$ | $\sim 10^{-18}\,\text{m}$ | $W, Z$ |
| 引力 | $10^{-39}$ | $\infty$ | 引力子？（未发现）|

> **统一之路**：电磁力 + 弱力 → 电弱统一（Glashow-Salam-Weinberg, 1960s，1979 诺奖）。电弱 + 强力 → 大统一理论（GUT，尚未实验验证）。全部 + 引力 → 万有理论（弦理论等，仍在探索中）。

### 1.3 标准模型的规范群

$$SU(3)_C \times SU(2)_L \times U(1)_Y$$

- $SU(3)_C$：色荷（color charge），QCD
- $SU(2)_L$：弱同位旋（左手费米子）
- $U(1)_Y$：超荷（hypercharge）

电弱对称破缺后：$SU(2)_L \times U(1)_Y \to U(1)_{em}$

---

## §2 量子电动力学（QED）：最精确的理论

### 2.1 Feynman 图：图形化微扰论

> **Feynman 的天才**：把 S 矩阵的微扰展开用图形表示。每个图对应一个确定数学表达式。

**基本规则**（QED）：

| 图形元素 | 数学对应 |
|---------|---------|
| 电子线（带箭头）| 传播子 $\frac{i(\gamma^\mu p_\mu + m)}{p^2 - m^2 + i\epsilon}$ |
| 光子线（波浪线）| 传播子 $\frac{-ig_{\mu\nu}}{q^2 + i\epsilon}$ |
| 顶点 | $-ie\gamma^\mu$ |
| 闭合圈 | 动量积分，乘 $-1$ |

### 2.2 电子-缪子散射（树图）

最低阶过程 $e^- \mu^- \to e^- \mu^-$（单光子交换）：

不变振幅：

$$\mathcal{M} = \frac{e^2}{q^2}[\bar{u}(p_3)\gamma^\mu u(p_1)][\bar{u}(p_4)\gamma_\mu u(p_2)]$$

其中 $q = p_1 - p_3$ 是交换光子的四动量。

高能极限下，微分截面（Mott/Rutherford 散射）：

$$\frac{d\sigma}{d\Omega} = \left(\frac{\alpha\hbar}{2p\sin(\theta/2)}\right)^2\frac{E'}{E}\left(\cos^2\frac{\theta}{2} + \frac{Q^2}{2m^2}\sin^2\frac{\theta}{2}\right)$$

其中 $\alpha = e^2/(4\pi\epsilon_0\hbar c) \approx 1/137$ 是精细结构常数。

### 2.3 QED 的惊人精度

> 电子的异常磁矩——QED 最辉煌的验证。

Dirac 方程预测 $g = 2$。实验测得 $g \neq 2$，差异由 QED 虚粒子圈修正解释：

$$a_e = \frac{g - 2}{2} = \frac{1}{2}\frac{\alpha}{\pi} - 0.328478965\left(\frac{\alpha}{\pi}\right)^2 + \cdots$$

理论与实验吻合到 **12 位有效数字**——这是物理学最精确的理论预言！

$$a_e^{exp} = 0.00115965218073(28), \quad a_e^{th} = 0.00115965218161(82)$$

---

## §3 量子色动力学（QCD）：强相互作用

### 3.1 色荷与胶子

夸克携带**色荷**——红、绿、蓝三种（及反色）。胶子同时携带色和反色，因此有 $3\times3 - 1 = 8$ 种。

> **与 QED 的根本区别**：光子不带电（不自身相互作用），但胶子带色荷（胶子之间也通过强作用力耦合）——这就是 QCD 比 QED 难得多的原因。

### 3.2 渐近自由

> Gross, Politzer, Wilczek (1973, 2004 诺奖)：在高能（短距离）下，夸克间耦合常数**变小**——夸克"自由"了。

$$\alpha_s(Q^2) = \frac{12\pi}{(33-2n_f)\ln(Q^2/\Lambda^2_{QCD})}$$

其中 $n_f$ 是夸克味数（$\leq 6$），$\Lambda_{QCD} \approx 200\,\text{MeV}$ 是 QCD 尺度。

> **反直觉发现**：距离越近，夸克间力越**弱**；距离越远，力越**强**（与电磁力相反）。在 $\sim 1\,\text{fm}$ 以外，力强到无法分离——这就是**色禁闭**。

### 3.3 色禁闭

> 自由夸克**从未**被观测到。当试图拉开两个夸克时，色力线（色流管）越来越紧，能量线性增长。到某一点，能量足以从真空中产生新的夸克-反夸克对——产生新的强子，而非自由夸克。

$$V(r) \approx -\frac{4}{3}\frac{\alpha_s}{r} + \sigma r \qquad (\sigma \approx 1\,\text{GeV/fm，色弦张力})$$

### 3.4 强子谱

| 类型 | 构成 | 例子 |
|------|------|------|
| 重子 | $qqq$ | 质子 $uud$，中子 $udd$，$\Delta^{++}\,uuu$ |
| 介子 | $q\bar{q}$ | $\pi^+\,u\bar{d}$，$K^+\,u\bar{s}$，$J/\psi\,c\bar{c}$ |

> **Caltech 关联**：Murray Gell-Mann（Caltech 教授，1969 诺奖）在 1964 年提出夸克模型。他的"八重道"（Eightfold Way）用 $SU(3)$ 味对称性将强子分类——这是群论在粒子物理中的辉煌应用。

---

## §4 电弱统一理论

### 4.1 弱相互作用

弱力是唯一能改变**粒子味**（flavor）的相互作用——例如 $d \to u + W^-$。

**β 衰变**：$n \to p + e^- + \bar{\nu}_e$

费米早期的四费米子接触作用：

$$\mathcal{L}_{Fermi} = -\frac{G_F}{\sqrt{2}}[\bar{p}\gamma^\mu(1-g_A\gamma^5)n][\bar{e}\gamma_\mu(1-\gamma^5)\nu]$$

费米常数 $G_F = 1.166\times10^{-5}\,\text{GeV}^{-2}$。

### 4.2 V-A 结构：宇称破坏

> 吴健雄实验（1957）证实弱相互作用**最大程度破坏宇称对称性**。

弱相互作用中只有**左手螺旋**的费米子参与：

$$\psi_L = \frac{1-\gamma^5}{2}\psi$$

这就是为什么中微子**全部是左手的**（反中微子全部是右手的）——如果中微子有质量，这会产生深刻后果。

### 4.3 Higgs 机制

> 电弱对称破缺（EWSB）：Higgs 场真空期望值 $v \approx 246\,\text{GeV}$ 给 $W, Z$ 以质量，但光子保持无质量。

$$m_W = \frac{gv}{2} \approx 80.4\,\text{GeV}/c^2, \qquad m_Z = \frac{m_W}{\cos\theta_W} \approx 91.2\,\text{GeV}/c^2$$

Weinberg 角：$\sin^2\theta_W \approx 0.231$

费米子质量来自与 Higgs 场的 Yukawa 耦合：

$$m_f = \frac{y_f v}{\sqrt{2}}$$

其中 $y_f$ 是 Yukawa 耦合常数——从电子的 $\sim 10^{-6}$ 到顶夸克的 $\sim 1$，跨越 6 个数量级，标准模型无法解释这些值。

---

## §5 核物理

### 5.1 原子核组成

原子核由 $Z$ 个质子和 $N$ 个中子组成（质量数 $A = Z + N$）。

核力（剩余强作用）：核子间的吸引力，力程 $\sim 1$–$3\,\text{fm}$，由介子（$\pi$ 为主）交换传递。

### 5.2 液滴模型（半经验质量公式, SEMF）

Weizsäcker 质量公式：

$$B(A,Z) = a_V A - a_S A^{2/3} - a_C\frac{Z(Z-1)}{A^{1/3}} - a_A\frac{(A-2Z)^2}{A} + \delta(A,Z)$$

| 项 | 系数（MeV）| 物理意义 |
|----|-----------|---------|
| 体积能 $a_V$ | $\approx 15.8$ | 每个核子的结合能 |
| 表面能 $a_S$ | $\approx 18.3$ | 表面核子配对不足 |
| 库仑能 $a_C$ | $\approx 0.71$ | 质子排斥 |
| 对称能 $a_A$ | $\approx 23.2$ | 倾向 $N = Z$ |
| 配对能 $\delta$ | $\approx 12$ | 偶-偶核更稳定 |

配对项：$\delta = \begin{cases}+a_P A^{-3/4} & \text{偶偶} \\ 0 & \text{奇}A \\ -a_P A^{-3/4} & \text{奇奇}\end{cases}$

### 5.3 核壳模型

> 类比原子壳模型——核子在平均势中填充壳层。

**幻数**（满壳核子数，核特别稳定）：

$$2, 8, 20, 28, 50, 82, 126$$

> **Mayer & Jensen (1963 诺奖)**：引入**强自旋-轨道耦合** $V_{ls}\mathbf{l}\cdot\mathbf{s}$ 才能解释大幻数。核子总角动量 $j = l \pm 1/2$，$j = l + 1/2$ 能级更低——这与原子物理的弱 $ls$ 耦合截然不同。

### 5.4 α 衰变与量子隧穿

$$^{238}\text{U} \to ^{234}\text{Th} + \alpha \quad (Q \approx 4.2\,\text{MeV})$$

$\alpha$ 粒子必须穿过核力势垒（Gamow 1928）——**量子隧穿**。

半衰期对能量极其敏感：

$$T_{1/2} \propto \exp\left(\frac{4\pi Z_\alpha Z_d e^2}{\hbar v}\right)$$

> **Geiger-Nuttall 定律**：$\alpha$ 能量每变化 1 MeV，半衰期变化 $\sim 10^5$ 倍！$^{212}$Po 的 $T_{1/2} = 0.3\,\mu\text{s}$（$E_\alpha = 8.8\,\text{MeV}$），而 $^{238}\text{U}$ 的 $T_{1/2} = 4.5\,\text{Gyr}$（$E_\alpha = 4.2\,\text{MeV}$）——能量差 2 倍，半衰期差 $10^{23}$ 倍！

### 5.5 β 衰变与中微子

$$n \to p + e^- + \bar{\nu}_e \quad (T_{1/2} \approx 880\,\text{s, 自由中子})$$

中微子的预测：Pauli (1930) 为拯救能量-动量守恒而假设 $\nu$ 存在——连续 $\beta$ 谱（而非分立线）意味着有第三个粒子带走能量。

> **Caltech 关联**：Feynman 和 Gell-Mann (1958) 的 V-A 理论精确描述了弱作用的 $\beta$ 衰变——这是 Caltech 对核物理的直接贡献。

---

## §6 粒子物理前沿：超越标准模型

### 6.1 标准模型的未解之谜

1. **中微子质量**：标准模型预测中微子无质量，但中微子振荡实验（1998–2015 诺奖）证明它们有质量
2. **暗物质**：标准模型中没有合适的暗物质候选者
3. **物质-反物质不对称**：宇宙中物质远多于反物质（CP 破坏不够）
4. **质量等级问题**：为什么顶夸克比电子重 $3.6\times10^5$ 倍？
5. **引力**：标准模型不含引力

### 6.2 超对称（SUSY）

每个标准模型粒子有一个超对称伙伴（自旋差 1/2）：

| 标准模型粒子 | SUSY 伙伴 |
|------------|----------|
| 电子 $e$ | 标量电子 $\tilde{e}$ |
| 夸克 $q$ | 标量夸克 $\tilde{q}$ |
| 光子 $\gamma$ | 中微子 $\tilde{\gamma}$ |

> 若 SUSY 在 TeV 标度破缺，最轻超对称粒子（LSP）可能是暗物质候选者。但 LHC 至今未发现超对称粒子——SUSY 面临压力。

---

## Python 演示：粒子质量谱 + α 衰变隧穿

```python
"""
Caltech Ph 109 Demo: 粒子物理与核物理两个核心计算
1. 标准模型粒子质量谱（对数尺度）
2. α 衰变 Gamow 隧穿: 半衰期对能量的指数敏感性
纯标准库零依赖，bash 可直接跑通。
"""
import math

# ══════════════════════════════════════════════
# 1. 标准模型粒子质量谱
# ══════════════════════════════════════════════
print("=== 标准模型粒子质量谱（MeV/c²）===\n")

# 费米子
fermions = [
    ("电子 e",       0.511,      "第一代 轻子"),
    ("电子中微子 νe",  0.000001,    "第一代 轻子 (< 1 eV)"),
    ("上夸克 u",      2.2,        "第一代 夸克"),
    ("下夸克 d",      4.7,        "第一代 夸克"),
    ("缪子 μ",       105.7,       "第二代 轻子"),
    ("奇夸克 s",      95,         "第二代 夸克"),
    ("粲夸克 c",      1275,       "第二代 夸克"),
    ("陶子 τ",       1777,        "第三代 轻子"),
    ("底夸克 b",      4180,       "第三代 夸克"),
    ("顶夸克 t",      173000,     "第三代 夸克"),
]

# 玻色子
bosons = [
    ("光子 γ",         0,         "电磁"),
    ("胶子 g",         0,         "强（8种）"),
    ("W 玻色子",       80379,     "弱"),
    ("Z 玻色子",       91188,     "弱"),
    ("Higgs H",       125100,     "Higgs"),
]

print(f"{'粒子':>16s} {'质量(MeV)':>12s} {'质量(GeV)':>12s} {'类别':>20s}")
print("-" * 65)
for name, mass, category in fermions:
    print(f"{name:>16s} {mass:12.6f} {mass/1000:12.6f} {category:>20s}")
print("-" * 65)
for name, mass, category in bosons:
    mass_str = f"{mass:.3f}" if mass > 0 else "0（无质量）"
    print(f"{name:>16s} {mass_str:>12s} {'':>12s} {category:>20s}")

# 质量比
m_e = 0.511
m_t = 173000
print(f"\n→ 质量跨度: 电子 {m_e:.3f} MeV → 顶夸克 {m_t:.0f} MeV")
print(f"  比值 m_t/m_e = {m_t/m_e:.0f}——标准模型无法解释此等级！")
print(f"  这就是 Yukawa 耦合 y_t/y_e 的谜题，超越标准模型的核心动机。\n")

# ══════════════════════════════════════════════
# 2. α 衰变 Gamow 隧穿
# ══════════════════════════════════════════════
print("=== α 衰变 Gamow 隧穿: Geiger-Nuttall 定律 ===\n")

# Gamow 因子: 隧穿概率 ~ exp(-2G)
# WKB 积分: G = ∫_R^{r_c} sqrt(2m(V-E))/(ℏc) dr  （用 ℏc 避免 SI/fm 单位混乱）

# 参数（全部 MeV-fm 自然单位）
Z_alpha = 2     # α 粒子电荷
r0 = 1.2        # 核半径参数（fm）
hbar_c = 197.3  # MeV·fm
m_alpha = 3727.4 # MeV/c²（α 粒子静质量能）
e2 = 1.440      # MeV·fm（e²/4πε₀）

# 核素数据: (名称, A, Q值MeV, 实测半衰期秒)
nuclei = [
    ("²¹²Po", 212, 8.787, 0.3e-6),
    ("²¹⁰Po", 210, 5.304, 138*24*3600),
    ("²³⁸U",  238, 4.270, 4.468e9*365.25*24*3600),
    ("²³²Th", 232, 4.083, 14.05e9*365.25*24*3600),
]

print(f"{'核素':>8s} {'Q(MeV)':>8s} {'log₁₀(T½/秒)':>14s} {'Gamow G':>10s} {'2G/ln10':>10s}")
print("-" * 56)

gamow_data = []
for name, A, Q, T_half in nuclei:
    Z_d = A - 2  # 子核电荷数
    R = r0 * A**(1.0/3)  # 核半径（fm）
    r_c = 2 * Z_d * e2 / Q  # 经典转折点（fm）
    x = R / r_c

    # α 粒子速度: v/c = sqrt(2Q/mα)
    v_over_c = math.sqrt(2 * Q / m_alpha)

    # 解析 Gamow 因子:
    # G = (2 Z_d e²)/(ℏc) · (c/v) · [arccos(√x) - √(x(1-x))]
    G = (2 * Z_d * e2 / hbar_c) * (1.0 / v_over_c) * \
        (math.acos(math.sqrt(x)) - math.sqrt(x * (1 - x)))

    log10_T_actual = math.log10(T_half)
    two_G_ln10 = 2 * G / math.log(10)

    print(f"{name:>8s} {Q:8.3f} {log10_T_actual:14.2f} {G:10.2f} {two_G_ln10:10.2f}")
    gamow_data.append((name, Q, log10_T_actual, G))

# 验证 Geiger-Nuttall 线性关系: log₁₀(T½) vs Z_d/√Q
print(f"\nGeiger-Nuttall 线性性验证:")
print(f"{'核素对':>16s} {'Δ(2G/ln10)':>12s} {'Δlog₁₀(T½)':>12s} {'比值':>8s}")
for i in range(1, len(gamow_data)):
    name0, Q0, logT0, G0 = gamow_data[0]  # 以 ²¹²Po 为基准
    name, Q, logT, G = gamow_data[i]
    dGamow = 2 * (G - G0) / math.log(10)
    dLogT = logT - logT0
    ratio = dLogT / dGamow if dGamow != 0 else 0
    print(f"{'%s→%s' % (name0, name):>16s} {dGamow:12.2f} {dLogT:12.2f} {ratio:8.2f}")

print(f"\n→ Δlog₁₀(T½) / Δ(2G/ln10) ≈ 1 表明半衰期指数 ≈ exp(2G)")
print(f"→ Q 值从 4.1 MeV 到 8.8 MeV（仅 2× 变化），")
print(f"  半衰期跨越 ²³²Th(140亿年) → ²¹²Po(0.3微秒) = 10²³ 倍！")
print(f"→ 这就是量子隧穿对能量极端敏感的铁证（Geiger-Nuttall 定律）。")
print(f"  Gamow (1928) 用纯量子力学+经典势垒完美解释——核物理的经典时刻。")
```

**反直觉发现**：$\alpha$ 衰变能量从 $4.1\,\text{MeV}$（$^{232}$Th）变到 $8.8\,\text{MeV}$（$^{212}$Po）——仅变化约 2 倍——但半衰期跨越 $10^{23}$ 倍（从 140 亿年到 0.3 微秒）。量子隧穿对能量的极端敏感性是经典物理完全无法理解的——只有量子力学的波函数穿透势垒才能解释这种天文数字的跨度的根源。

---

## 习题

### 基础题（Griffiths 级别）

**P1.** 用守恒律分析 $\pi^0 \to \gamma\gamma$ 衰变。$\pi^0$ 质量为 $135\,\text{MeV}/c^2$，无自旋。为什么不能衰变成单个光子？

**P2.** 证明精细结构常数 $\alpha = e^2/(4\pi\epsilon_0\hbar c) \approx 1/137$ 是无量纲的。用它在 SI 和自然单位制之间转换。

**P3.** 写出质子 $uud$ 和中子 $udd$ 的所有夸克量子数（电荷、同位旋、奇异数），验证电荷分别为 $+1$ 和 $0$。

### 进阶题（Halzen & Martin 级别）

**P4.**（QED 磁矩）计算电子的 Schwinger 修正（一圈图）：$a_e = (g-2)/2 = \alpha/(2\pi)$。画出对应的 Feynman 图。

**P5.**（QCD 渐近自由）解释为什么胶子的自相互作用导致耦合常数在短距离变小。用不确定性原理做定性论证。

**P6.**（核结合能）用 Weizsäcker 公式计算 $^{56}$Fe 的每核子结合能，验证它接近经验峰值 $\sim 8.8\,\text{MeV}$。为什么铁是恒星核合成的终点？

### 挑战题

**P7.**（电弱统一）从 Higgs 势 $V(\Phi) = -\mu^2\Phi^\dagger\Phi + \lambda(\Phi^\dagger\Phi)^2$ 出发，推导真空期望值 $v = \mu/\sqrt{\lambda}$ 和 Higgs 质量 $m_H = \sqrt{2}\mu$。证明 $W, Z$ 获得质量而光子不获得。

**P8.**（中微子振荡）两个味本征态 $\nu_e, \nu_\mu$ 的质量本征态 $\nu_1, \nu_2$ 满足 $|\nu_e\rangle = \cos\theta|\nu_1\rangle + \sin\theta|\nu_2\rangle$。推导振荡概率 $P(\nu_e \to \nu_\mu) = \sin^2(2\theta)\sin^2(\Delta m^2 L / 4E)$。用大气中微子数据估计 $\Delta m^2_{atm} \approx 2.5\times10^{-3}\,\text{eV}^2$ 和 $\theta_{23} \approx 45°$。

---

## 知识地图与跨课程联系

```
粒子物理与核物理 (Ph 109)
    │
    ├──→ QED ──→ 量子场论 (Ph 205)
    │        │
    │   Feynman 图 → 微扰 QFT
    │        │
    │   异常磁矩 → 精度极限验证
    │
    ├──→ QCD ──→ 强相互作用
    │        │
    │   渐近自由/色禁闭 → 格点 QCD (Ph 230)
    │        │
    │   Gell-Mann 夸克模型 (Caltech!) → SU(3) 群论 (Ph 106)
    │
    ├──→ 电弱统一 ──→ Higgs 机制
    │        │              │
    │   规范对称破缺 → 宇宙早期相变 (Ph 237 宇宙学)
    │
    ├──→ 核物理 ──→ 液滴/壳模型
    │        │
    │   α 衰变隧穿 → 量子力学 (Ph 125)
    │        │
    │   β 衰变 → 中微子 → 中微子振荡 (BSM)
    │
    └──→ 超越标准模型 ──→ 暗物质 / SUSY / 弦理论
                              │
                         Caltech (Schwarz 弦理论)
```

**关键连接**：
- Feynman 图 $\to$ 量子场论的微扰展开
- QCD 渐近自由 $\to$ 晶格 QCD 数值模拟
- Higgs 机制 $\to$ 宇宙学暴胀理论
- 核壳模型 $\to$ 量子力学（类似原子壳模型）
- 中微子振荡 $\to$ 超越标准模型物理
- $\alpha$ 衰变隧穿 $\to$ 量子力学基本原理

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Griffiths *Introduction to Elementary Particles* 2ed | Ch 1-3（标准模型）、Ch 4-6（QED/QCD/弱作用）、Ch 7（规范理论）| Ph 109 主教材，最友好 |
| Halzen & Martin *Quarks and Leptons* | Ch 1-4（QED）、Ch 5-7（QCD）、Ch 8-10（电弱）| 经典中级教材 |
| Perkins *Introduction to High Energy Physics* 4ed | 全书 | 实验视角补充 |
| Krane *Introductory Nuclear Physics* | Ch 3（核模型）、Ch 6-8（衰变）、Ch 10-13（核反应）| 核物理标准教材 |

> **Feynman 的话**：*"If all of scientific knowledge were to be destroyed, and only one sentence passed on to the next generation… I believe it is the atomic hypothesis that all things are made of atoms."* 但如果传给下一代的是粒子物理的一句话，那就是：**万物由夸克和轻子构成，它们通过规范玻色子交换力**——标准模型的简洁与力量。

> **Gell-Mann 的 Caltech 遗产**：Murray Gell-Mann 在 Caltech 工作了半个多世纪（1955–2019）。他的夸克模型和"八重道"在 Caltech 诞生，将群论（$SU(3)$）引入粒子物理分类——这是 Caltech 对物理学最深远的贡献之一。

---

*本文件属于 top-physics-courses/caltech-physics Phase 2。对应课程 Ph 109。Feynman 图是 Caltech 的粒子物理 DNA。*

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：粒子物理研究"世界最小的乐高积木是什么"——拆到底，万物由夸克和轻子组成，它们靠交换"信使粒子"（光子、胶子、W/Z 玻色子）来传递力。
>
> **生活类比**：两个人隔空传球。球是"信使粒子"（光子传递电磁力、胶子传递强力），传球让他们互相推拉。夸克和轻子是"球员"，但你永远抓不到单个夸克（色禁闭）——它们像被弹簧绑着，越拉越紧，扯断反而产生新夸克对。
>
> **反直觉发现（啊哈时刻）**：
> - **力 = 交换粒子**：电磁力是交换光子，强力是交换胶子。你坐在椅子上没掉下去，本质是电子之间在疯狂交换虚光子。
> - **越靠近反而力越弱**（渐近自由）：夸克越靠近，强相互作用越弱——这违背直觉（磁铁越近越强）。2024 诺奖（2004 Gross, Politzer, Wilczek）就是发现这个。Caltech 的 Feynman 粒子物理 DNA 孕育了这一切。
> - **质量来自能量**：质子质量 938 MeV，但组成它的三个夸克静止质量加起来才 ~10 MeV——**99% 的质量来自夸克胶子的高速运动和相互作用能量**。$E=mc^2$ 的极致体现。

---

## 🔗 衔接：从哪来，到哪去

### 前置（你需要先会什么）
- **Ph 125 量子力学**：自旋、角动量、本征态——粒子分类的语言
- **Ph 106 群论**：$SU(3)$ 群——夸克模型（八重道）的数学基础（Gell-Mann 在 Caltech 创立）
- **Ph 122 电动力学**：规范不变性 $\to$ 规范理论 $U(1)\to SU(2)\to SU(3)$

### 粒子物理的"危机"（为什么需要升级）
- **1930s 粒子动物园危机**：加速器发现几百种强子，看起来杂乱无章
- **解决 → 夸克模型**（Gell-Mann 1964, Caltech）：强子由 u/d/s 夸克组成，$SU(3)$ 八重道分类
- **新危机**：弱相互作用中宇称不守恒（吴健雄实验），电磁力与弱力是两套理论
- **解决 → 电弱统一**（Glashow-Salam-Weinberg 1967）+ Higgs 机制（1964）→ 标准模型
- **今天的新危机**：标准模型无法解释暗物质、中微子质量、物质-反物质不对称、引力 → BSM（超越标准模型）

### 后续（粒子物理通向哪里）
- 标准模型 → **量子场论 QFT**（Ph 205/237，Peskin & Schroeder）
- Higgs 机制 → **宇宙暴胀 / 早期宇宙相变**（Ph 237 宇宙学）
- 中微子振荡 → **BSM 物理**（质量产生机制、轻子 CP 破坏）
- 格点 QCD → **核物理**（质子质量、核力从第一性原理）

---

## 🏭 理论联系实际：5 个应用

1. **PET 正电子发射断层扫描**（反物质应用）：注入人体的放射性同位素释放正电子，与电子湮灭产生两个 511 keV 光子——粒子物理 $e^+e^-\to\gamma\gamma$ 在医院里用，诊断癌症。
2. **LIGO 双中子星并合 + 重元素合成**（2017 GW170817）：中子星并合的 r-过程核合成产生了宇宙中的金、铂、铀——核物理 + 引力波 + 多信使天文学的融合。Caltech LIGO 团队主导。
3. **医用质子治疗**（核物理应用）：质子束精准打击肿瘤，Bragg 峰让能量沉积在病灶——核物理的回旋加速器 + 相互作用的医学应用。
4. **碳-14 考古测年**（弱相互作用 β 衰变）：$^{14}\text{C}\to^{14}\text{N}+e^-+\bar\nu_e$，半衰期 5730 年——考古学、地质学的基础工具。
5. **Muong-2 / 粒子加速器寻暗物质**（BSM 探索）：Fermilab Muon g-2（2021-2024 持续）测量 $\mu$ 子反常磁矩，与标准模型预言偏差暗示新物理；LZ/XENONnT（2024-2025）直接搜寻暗物质。

---

## 🔬 最新研究前沿（2024-2026）

1. **Muon g-2 最终结果与反常**（2023-2025）：Fermilab Muon g-2 实验 2023-08 发布更精确的 $\mu$ 子反常磁矩测量，与标准模型预言的 $5\sigma$ 偏差持续——2024-2025 理论"格点 QCD"重新计算标准模型值后争议未决，仍是 BSM 物理的最大线索之一。
2. **中微子质量序与 CP 破坏测量**（2024-2026 活跃）：T2K、NOvA、DUNE（建设）实验精确测量中微子混合角与质量差——2024-2025 数据倾向于正常质量序，CP 破坏相位接近最大。这关系到宇宙物质-反物质不对称之谜。
3. **LIGO 双黑洞并合与第二代黑洞**（2025-2026）：LIGO 在 GWTC-4.0（2025-08）和 GWTC-5.0（2026-05）中发现了**第二代黑洞**的证据（黑洞本身由前一次并合产生）——多代黑洞层级并合改变我们对黑洞族群的理解。[LIGO Caltech 2025-08-26 / 2026-05-26]
4. **暗物质直接探测的极限推进**（2024-2025）：LZ（2024-2025 更新）和 XENONnT 把暗物质-核子相互作用截面限制推到 $10^{-48}\,\text{cm}^2$——仍未发现 WIMP，迫使社区转向轴子（axion）、暗光子等轻暗物质候选。Caltech 团队参与 HAYSTAC 轴子搜寻。
5. **Gell-Mann 遗产 + Caltech 弦理论**（持续）：Murray Gell-Mann（2019 逝）在 Caltech 工作半世纪的夸克模型遗产，延续到 John Schwarz 的弦理论（1970s 至今）。2024-2026 弦理论转向 Swampland 纲领、AdS/CFT 凝聚态应用——Caltech 仍是量子引力理论的核心阵地。

---

## 🗺️ 学习 Roadmap（Caltech 路径）

```
Ph 2a/125  量子力学 (自旋、本征态、角动量)  ← 前置
Ph 106c  群论 (SU(3)、表示论)  ← 前置（Gell-Mann 夸克模型的工具）
Ph 122b  电动力学 (规范不变性 → 规范理论)  ← 前置
    │
    ▼
Ph 109  粒子物理导论 (Griffiths *Elementary Particles*)  ← 研一
    │   • 掌握：标准模型组成、Feynman 图、QED 一圈修正、QCD 渐近自由
    │   • ✅ 知识检查：画出电子-μ子散射的最低阶 Feynman 图
    │
    ▼
Ph 205/237  量子场论 (Peskin & Schroeder / Srednicki)  ← 研一/研二
    │   • 掌握：路径积分 QFT、规范理论重整化、电弱统一、Higgs 机制
    │   • ✅ 知识检查：推导 Higgs 势破缺后 W/Z 获得质量而光子不获得
    │
    ▼
Ph 230  格点 QCD / 强相互作用  ← 研二/研三
    │   • 掌握：格点离散化、蒙特卡洛、强子质量的第一性原理计算
    │   • ✅ 知识检查：解释为什么渐近自由使微扰 QCD 在高能失效
    │
    ▼
→ Ph 237 宇宙学 (Higgs 相变 → 早期宇宙；暗物质 → BSM)
→ LIGO / 多信使天文学 (双中子星 → 核物理 + 引力波)
→ Caltech 弦理论组 (Schwarz：量子引力 / Swampland)
```

**关键里程碑**：能否用一句话说出"标准模型 = $SU(3)\times SU(2)\times U(1)$ 规范理论 + Higgs 破缺"，并解释"质子 99% 的质量来自能量而非夸克静止质量"，是检验你是否理解粒子物理核心的试金石。Caltech 的 Gell-Mann 用群论统一了"粒子动物园"，这是 Caltech 对粒子物理最深远的贡献。
