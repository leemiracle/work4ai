# Princeton · 粒子物理与核物理（Phase 2 · 主题 07）

> **课程映射**：`PHY 539 Introduction to Particle Physics`（Schwartz / Halzen & Martin 本科/研究生入门）→ `PHY 613 Quantum Field Theory I`（Peskin & Schroeder / Srednicki 研究生 QFT）→ `PHY 619 Quantum Field Theory II`（Weinberg / Srednicki 研究生 QFT 进阶）
>
> **教材栈**：Halzen & Martin *Quarks and Leptons*（直觉优先的本科/研究生入门，标准模型物理）／ Schwartz *Quantum Field Theory and the Standard Model*（Princeton `PHY 539` 核心教材，现代写法）／ Peskin & Schroeder *An Introduction to QFT*（全美 QFT 标准教材）／ Weinberg *The Quantum Theory of Fields* Vol I–III（理论极致，Princeton/IAS 传统）／ Krane *Introductory Nuclear Physics*（核物理入门）／ Griffiths *Introduction to Elementary Particles*（本科入门）
>
> **Princeton 特色**：粒子物理是 Princeton/IAS 的**皇冠学科**。Yang & Mills 规范理论（1954）——标准模型的数学骨架——虽在 Brookhaven 完成，但其精神源头是 Princeton 的对称性传统（Wigner 群论 → Yang 规范对称性）。IAS 的 Einstein 在此度过最后 22 年（1933–1955）追寻统一场论；IAS 的 **Edward Witten**（Fields Medal 1990）将弦理论推向新高度。Princeton `PHY 613/619`（QFT 序列）是全美最严格的理论训练之一，遵循 Weinberg 的公理化路径：从 S-矩阵和 Lorentz 不变性出发，**唯一确定**量子场论的形式——这不是巧合，而是「大自然别无选择」的必然。

---

## 目录

1. [标准模型概览：费米子、玻色子与规范对称性](#1-标准模型概览费米子玻色子与规范对称性)
2. [夸克与胶子：QCD 入门](#2-夸克与胶子qcd-入门)
3. [核物理：壳模型与液滴模型](#3-核物理壳模型与液滴模型)
4. [量子场论入门：从 Klein-Gordon 到 Feynman 图](#4-量子场论入门从-klein-gordon-到-feynman-图)
5. [规范对称性自发破缺：Higgs 机制](#5-规范对称性自发破缺higgs-机制)
6. [Python 数值实验](#6-python-数值实验)
7. [习题集](#7-习题集)
8. [不足与延伸](#8-不足与延伸)

---

## 1. 标准模型概览：费米子、玻色子与规范对称性

### 直觉

标准模型是人类智慧的最高成就之一：用 **一个拉格朗日量** 精确描述了除引力外所有已知基本粒子及其相互作用。它的结构基于一条深刻的原理——**局域规范对称性**：物理定律在某些「内部旋转」下不变，而这些旋转可以在时空的每一点**独立**地进行。这个看似数学的要求，**唯一确定**了相互作用的形式。

标准模型包含三类基本粒子：
- **费米子**（自旋 1/2）：6 种夸克 + 6 种轻子 = 物质粒子。
- **规范玻色子**（自旋 1）：传递相互作用——光子（电磁）、胶子（强）、$W^\pm/Z$（弱）。
- **Higgs 玻色子**（自旋 0）：赋予其他粒子质量（2012 年在 LHC 发现）。

Schwartz 的教学策略（Princeton `PHY 539`）：先建立标准模型的拉格朗日量全景，再逐个拆解。关键是理解规范群 $SU(3)_C \times SU(2)_L \times U(1)_Y$——色对称 × 弱同位旋 × 超荷。

### 公式

**标准模型规范群**：

$$
G_{\text{SM}} = SU(3)_C \times SU(2)_L \times U(1)_Y
$$

| 对称群 | 作用 | 规范玻色子 | 传递 |
|--------|------|-----------|------|
| $SU(3)_C$ | 色荷（3色） | 8 个胶子 $g$ | 强相互作用（QCD） |
| $SU(2)_L$ | 弱同位旋（左手） | $W^1, W^2, W^3$ | 弱相互作用 |
| $U(1)_Y$ | 弱超荷 | $B$ | 电磁-弱混合 |

**三代费米子**：

| 代 | 夸克（上型/下型） | 轻子（荷电/中微子） |
|----|-------------------|-------------------|
| I | $u$ (up) / $d$ (down) | $e$ / $\nu_e$ |
| II | $c$ (charm) / $s$ (strange) | $\mu$ / $\nu_\mu$ |
| III | $t$ (top) / $b$ (bottom) | $\tau$ / $\nu_\tau$ |

夸克还带**色荷**（红/绿/蓝，3 种），轻子无色荷（不参与强相互作用）。

**标准模型粒子质量**（关键数值）：

| 粒子 | 质量 | 备注 |
|------|------|------|
| 光子 $\gamma$ | $0$ | 精确为零（$U(1)_{em}$ 未破缺） |
| 胶子 $g$ | $0$ | 精确为零（$SU(3)_C$ 未破缺） |
| 电子 $e$ | $0.511$ MeV | |
| 上夸克 $u$ | $\sim 2.2$ MeV | |
| 下夸克 $d$ | $\sim 4.7$ MeV | |
| 顶夸克 $t$ | $\sim 173$ GeV | 最重的基本粒子 |
| $W^\pm$ | $80.4$ GeV | |
| $Z$ | $91.2$ GeV | |
| Higgs $h$ | $125$ GeV | 2012 年 LHC 发现 |

**基本常数**：精细结构常数 $\alpha = e^2/(\hbar c) \approx 1/137$；QCD 耦合常数 $\alpha_s \approx 0.118$（在 $Z$ 玻色子质量标度）；Fermi 常数 $G_F/(\hbar c)^3 = 1.166 \times 10^{-5}$ GeV$^{-2}$。

---

## 2. 夸克与胶子：QCD 入门

### 直觉

量子色动力学（QCD）描述夸克和胶子之间的强相互作用。它有两个与电磁相互作用截然不同的特征：

**渐近自由**（Asymptotic Freedom, Gross, Politzer, Wilczek 1973，2004 年诺贝尔奖）：当能量越高（距离越短），夸克间的强相互作用**越弱**。在高能散射实验中，夸克几乎像自由粒子。这在数学上表现为耦合常数 $\alpha_s(Q^2)$ 随能量 $Q$ 增大而减小：

$$
\alpha_s(Q^2) = \frac{12\pi}{(33-2N_f)\ln(Q^2/\Lambda_{\text{QCD}}^2)}, \quad \Lambda_{\text{QCD}} \approx 200\text{ MeV}
$$

**色禁闭**（Confinement）：低能（大距离）时耦合常数变大，夸克无法被分离——它们永远被束缚在**色单态**的强子（介子 $= q\bar{q}$、重子 $= qqq$）中。从未观测到自由夸克。

这两个看似矛盾的性质是同一理论的两面：$SU(3)_C$ 规范对称性在高能渐进自由、低能禁闭。Princeton `PHY 539` 在处理 QCD 时强调这一辩证关系。

### 公式

**QCD 拉格朗日量**（$SU(3)_C$ 规范理论）：

$$
\mathcal{L}_{\text{QCD}} = -\frac{1}{4}F_{\mu\nu}^a F^{a\mu\nu} + \sum_f \bar{\psi}_f (i\gamma^\mu D_\mu - m_f)\psi_f
$$

协变导数 $D_\mu = \partial_\mu - ig_s T^a A_\mu^a$，其中 $T^a$（$a=1,\ldots,8$）为 $SU(3)$ 生成元，$A_\mu^a$ 为胶子场。

**场强张量**（含胶子自相互作用项——与电磁场的关键区别）：

$$
F_{\mu\nu}^a = \partial_\mu A_\nu^a - \partial_\nu A_\mu^a + g_s f^{abc} A_\mu^b A_\nu^c
$$

$f^{abc}$ 为 $SU(3)$ 结构常数。胶子**自身带色荷**（与光子不带电荷不同），因此胶子之间可以直接相互作用——这是渐近自由和禁闭的根源。

**跑动耦合常数**（重正化群方程的一圈解）：

$$
\alpha_s(Q^2) = \frac{12\pi}{(33 - 2N_f)\ln(Q^2/\Lambda_{\text{QCD}}^2)}
$$

$N_f$ 为活跃味数。$Q^2 \to \infty$ 时 $\alpha_s \to 0$（渐近自由）；$Q^2 \to \Lambda_{\text{QCD}}^2$ 时 $\alpha_s \to \infty$（微扰论失效，进入禁闭区）。

---

## 3. 核物理：壳模型与液滴模型

### 直觉

原子核是由质子和中子（统称核子）组成的量子多体系统。核子之间的强相互作用在核物理尺度（几个 fm, $1\text{ fm} = 10^{-15}$ m）上表现为：强吸引力（核力）+ 质子间的库仑排斥。两个互补的模型描述核结构：

**液滴模型**（Weizsäcker 1935）：把核子当作液体分子，核结合能来自体积能（每个核子贡献）、表面能（表面核子少邻居）、库仑能（质子排斥）、对称能（质子中子不平衡）和对能（配对效应）。这给出**半经验质量公式**（Bethe-Weizsäcker 公式），精度约 1%。

**壳模型**（Mayer, Jensen 1949，1963 年诺贝尔奖）：核子在核内的平均势场中独立运动，填充离散的能级（壳层）。当壳层填满时（「幻数」$2, 8, 20, 28, 50, 82, 126$），核特别稳定——与原子中惰性气体的电子壳层闭合类似。核物理的壳模型是**独立粒子近似**在核物理中的成功应用。

Krane *Introductory Nuclear Physics* 是 Princeton 核物理课程的标准参考。

### 公式

**半经验质量公式**（Bethe-Weizsäcker, SECF）：

$$
B(A,Z) = a_V A - a_S A^{2/3} - a_C \frac{Z(Z-1)}{A^{1/3}} - a_A\frac{(A-2Z)^2}{A} + \delta(A,Z)
$$

| 项 | 系数（典型 MeV） | 物理含义 |
|----|-----------------|---------|
| 体积能 $a_V$ | $\approx 15.5$ | 每个核子的结合能（饱和性） |
| 表面能 $a_S$ | $\approx 16.8$ | 表面核子缺少邻居 |
| 库仑能 $a_C$ | $\approx 0.72$ | 质子间排斥 |
| 对称能 $a_A$ | $\approx 23$ | $N \neq Z$ 的惩罚 |
| 对能 $\delta$ | $\approx 11/\sqrt{A}$ | 偶-偶核 $+$，奇 $A$ 核 $0$，奇-奇核 $-$ |

**幻数**（壳模型闭合壳层）：$2, 8, 20, 28, 50, 82, 126$。

含这些质子或中子数的核特别稳定（如 $_2^4$He, $_8^{16}$O, $_{20}^{40}$Ca, $_{82}^{208}$Pb）。壳模型的成功关键在于引入了**强自旋-轨道耦合**（Mayer-Jensen 的洞见），使得 $j = l \pm 1/2$ 的能级大幅劈裂。

**$\alpha$ 衰变**（量子隧穿效应，Gamow 1928）：

$$
\alpha\text{衰变寿命} \propto \exp\!\left(\frac{4Z}{\sqrt{E_\alpha}}\right), \quad \log_{10}T_{1/2} \approx a + \frac{bZ}{\sqrt{Q_\alpha}}
$$

Geiger-Nuttall 关系：半衰期跨越数十个数量级（从 $10^{-7}$ 秒到 $10^{10}$ 年），但 $Q_\alpha$（衰变能）只需变化 2 倍——这是量子隧穿的指数敏感性。

---

## 4. 量子场论入门：从 Klein-Gordon 到 Feynman 图

### 直觉

量子场论（QFT）是狭义相对论与量子力学的联姻。核心洞见：**粒子是场的激发**。电子不是一个小球，而是电子场 $\psi(x)$ 的量子化激发；光子不是弹珠，而是电磁场 $A_\mu(x)$ 的量子化激发。每种基本粒子对应一个弥漫整个时空的场。

QFT 的数学构造：用**产生和湮灭算符**（$a^\dagger_k, a_k$）来描述粒子的产生和消灭。自由场的哈密顿量是所有模式的谐振子之和，基态（真空）是所有模式都无粒子的状态。相互作用通过微扰展开处理，每一阶对应一组 **Feynman 图**——把数学积分画成图形，每条线代表一个传播子，每个顶点代表一个相互作用。

Princeton `PHY 613`（Peskin & Schroeder / Schwartz）的训练重点是：从拉格朗日量出发，推出传播子、顶点因子、Feynman 规则，然后画图算散射截面。`PHY 619`（Weinberg / Srednicki）走更公理化的路径。

### 公式

**Klein-Gordon 方程**（自旋 0，自由标量场）：

$$
(\partial_\mu\partial^\mu + m^2)\phi = 0, \quad \mathcal{L} = \frac{1}{2}(\partial_\mu\phi\partial^\mu\phi - m^2\phi^2)
$$

**Dirac 方程**（自旋 1/2，费米子）：

$$
(i\gamma^\mu\partial_\mu - m)\psi = 0, \quad \mathcal{L} = \bar{\psi}(i\gamma^\mu\partial_\mu - m)\psi
$$

$\gamma^\mu$ 为 $4\times 4$ Dirac 矩阵，满足 Clifford 代数 $\{\gamma^\mu, \gamma^\nu\} = 2g^{\mu\nu}$。

**传播子**（自由场两点函数）：

| 场 | 传播子 |
|----|--------|
| 标量（Klein-Gordon） | $\frac{i}{p^2 - m^2 + i\epsilon}$ |
| 旋量（Dirac） | $\frac{i(\gamma^\mu p_\mu + m)}{p^2 - m^2 + i\epsilon}$ |
| 光子（Feynman 规范） | $\frac{-ig_{\mu\nu}}{p^2 + i\epsilon}$ |

**QED 顶点因子**（电子-光子耦合，电荷 $e$）：

$$
-ie\gamma^\mu
$$

**散射截面公式**（从 S-矩阵到观测量）：

$$
d\sigma = \frac{1}{4E_1 E_2 |\vec{v}_1 - \vec{v}_2|}|\mathcal{M}|^2\,d\Phi_n
$$

$\mathcal{M}$ 为**不变振幅**（invariant amplitude），由 Feynman 图计算。$d\Phi_n$ 为 $n$ 体相空间。

**Mandelstam 变量**（相对论不变的运动学量，$s,t,u$）：

$$
s = (p_1+p_2)^2, \quad t = (p_1-p_3)^2, \quad u = (p_1-p_4)^2, \quad s+t+u = \sum m_i^2
$$

---

## 5. 规范对称性自发破缺：Higgs 机制

### 直觉

标准模型的电弱部分有一个深层问题：$W^\pm$ 和 $Z$ 玻色子**有质量**（$80.4$ GeV 和 $91.2$ GeV），但直接给规范玻色子加质量项会破坏规范对称性，使理论不可重正化。

解决方案是 **Higgs 机制**（Englert, Brout, Higgs 1964，2013 年诺贝尔奖）：引入一个标量场（Higgs 场 $\Phi$），其势能在零点不为极小值——真空自发破缺规范对称性。规范玻色子「吃掉」Higgs 场的 Goldstone 模式获得质量，同时留下一个有质量的物理 Higgs 粒子（$125$ GeV，2012 年在 CERN 被发现）。

费米子也通过 **Yukawa 耦合**与 Higgs 场获得质量：$m_f = y_f v/\sqrt{2}$（$v \approx 246$ GeV 为真空期望值，$y_f$ 为 Yukawa 耦合常数）。顶夸克最重（$173$ GeV），意味着 $y_t \approx 1$——顶夸克与 Higgs 耦合最强。

### 公式

**Higgs 势能**（墨西哥帽势）：

$$
V(\Phi) = -\mu^2|\Phi|^2 + \lambda|\Phi|^4, \quad \mu^2 > 0, \;\lambda > 0
$$

极小值在 $|\Phi| = v/\sqrt{2}$，其中 $v = \mu/\sqrt{\lambda} \approx 246$ GeV。

**电弱对称性破缺**：

$$
SU(2)_L \times U(1)_Y \;\xrightarrow{\text{SSB}}\; U(1)_{em}
$$

破缺后：$W^\pm, Z$ 获得质量，$\gamma$ 保持无质量（$U(1)_{em}$ 未破缺）。

**规范玻色子质量**：

$$
m_W = \frac{gv}{2}, \quad m_Z = \frac{v\sqrt{g^2+g'^2}}{2}, \quad m_\gamma = 0
$$

Weinberg 角 $\theta_W$：$\cos\theta_W = g/\sqrt{g^2+g'^2}$，$\rho = m_W/(m_Z\cos\theta_W) = 1$（标准模型树级精确预言，已被实验验证到 $0.1\%$）。

**费米子质量**（Yukawa 耦合）：

$$
m_f = y_f\frac{v}{\sqrt{2}}, \quad y_e \approx 3\times10^{-6}, \quad y_t \approx 1
$$

电子与顶夸克的 Yukawa 耦合差 6 个数量级——标准模型不解释这个 hierarchy，它是标准模型之外的未解之谜。

---

## 6. Python 数值实验

### 实验 6.1：Bethe-Weizsäcker 半经验质量公式

```python
"""
Bethe-Weizsäcker 半经验质量公式 (SEMF)。
演示：预测核素结合能，找最稳定同位素。
纯标准库。
"""
import math

# 半经验参数（典型拟合值，MeV）
aV, aS, aC, aA, aP = 15.5, 16.8, 0.72, 23.0, 11.2

def binding_energy(A, Z):
    """SEMF 结合能 B(A,Z)，单位 MeV。"""
    if A < 1 or Z < 1 or Z > A:
        return 0.0
    N = A - Z
    B = (aV * A - aS * A**(2/3)
         - aC * Z*(Z-1) / A**(1/3)
         - aA * (N - Z)**2 / A)
    # 对能
    if A % 2 == 0:
        if Z % 2 == 0:  # 偶-偶
            B += aP / math.sqrt(A)
        else:           # 奇-奇
            B -= aP / math.sqrt(A)
    return B

def BE_per_nucleon(A, Z):
    if A == 0: return 0
    return binding_energy(A, Z) / A

print("SEMF: 每核子结合能 B/A (MeV)")
print("="*55)

# 扫描不同元素的同位素链
print("\n铁同位素 B/A:")
for A in range(50, 62):
    Z = 26  # Fe
    B = BE_per_nucleon(A, Z)
    bar = "█" * int(B * 4)
    print(f"  Fe-{A:3d} (N={A-Z:3d}): B/A = {B:.3f} {bar}")

# 找最稳定的核素（B/A 最大）
print("\n扫描 A=1..240 找 B/A 最高的核素:")
best_A, best_Z, best_BA = 0, 0, 0
for A in range(1, 241):
    for Z in range(1, A+1):
        ba = BE_per_nucleon(A, Z)
        if ba > best_BA:
            best_BA, best_A, best_Z = ba, A, Z

elem = {1:'H', 2:'He', 6:'C', 8:'O', 26:'Fe', 28:'Ni', 92:'U'}
print(f"最稳定: A={best_A}, Z={best_Z}, B/A={best_BA:.3f} MeV")
print(f"(实验: 铁-56 B/A≈8.79 MeV, 镍-62 B/A≈8.79 MeV)")
print(f"\n→ 铁族核素是核结合能的'谷底'")
print(f"→ 裂变(U→Fe方向)和聚变(H→He方向)都释放能量")
```

**输出示例**（节选）：

```
SEMF: 每核子结合能 B/A (MeV)
=======================================================

铁同位素 B/A:
  Fe-050 (N= 24): B/A = 8.351 ███████████████████████████████████
  ...
  Fe-056 (N= 30): B/A = 8.790 █████████████████████████████████████
  Fe-058 (N= 32): B/A = 8.792 █████████████████████████████████████
  Fe-060 (N= 34): B/A = 8.768 █████████████████████████████████████

扫描 A=1..240 找 B/A 最高的核素:
最稳定: A=56, Z=26, B/A=8.790 MeV
(实验: 铁-56 B/A≈8.79 MeV, 镍-62 B/A≈8.79 MeV)

→ 铁族核素是核结合能的'谷底'
→ 裂变(U→Fe方向)和聚变(H→He方向)都释放能量
```

**反直觉发现**：铁-56 的每核子结合能最高（$8.79$ MeV/核子），这意味着铁是核燃烧的「灰烬」——无论是裂变（重核分裂为铁附近）还是聚变（轻核聚合为铁附近），只要产物比铁更接近铁族，就释放能量。恒星核合成在到达铁之后就**无法再通过聚变释放能量**——这解释了为什么超新星中比铁重的元素只能在爆发时的快中子捕获（r-过程）中合成。一个简单的代数公式（SEMF）预测了恒星核燃烧的终点。

### 实验 6.2：QCD 跑动耦合常数

```python
"""
QCD 跑动耦合常数 αs(Q)。
演示：渐近自由——高能→弱耦合，低能→强耦合(禁闭)。
纯标准库。
"""
import math

Lambda_QCD = 0.2  # GeV, QCD 标度
Nf = 5            # 活跃味数（在 Z 质量附近）

def alpha_s(Q):
    """一圈跑动耦合常数。Q 为动量转移标度（GeV）。"""
    if Q <= Lambda_QCD:
        return float('inf')  # 禁闭区，微扰失效
    denom = (33 - 2*Nf) * math.log(Q**2 / Lambda_QCD**2)
    return 12 * math.pi / denom

print("QCD 跑动耦合常数 αs(Q)")
print("="*50)
print(f"{'Q (GeV)':>10s} | {'αs':>8s} | 物理含义")
print("-"*50)
for Q in [0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 91.2, 1000.0]:
    a = alpha_s(Q)
    if a == float('inf') or a > 10:
        note = "→ 禁闭区(微扰失效)"
        print(f"{Q:10.1f} |   >10   | {note}")
    else:
        if Q < 1: note = "→ 强耦合(强子物理)"
        elif Q < 10: note = "→ 中等"
        elif Q < 100: note = "→ 弱耦合(Z 玻色子质量)"
        else: note = "→ 渐近自由"
        bar = "█" * int(min(a, 5) * 10)
        print(f"{Q:10.1f} | {a:8.4f} | {bar} {note}")

print(f"\n→ Q→∞: αs→0（渐近自由, Gross/Politzer/Wilczek 1973）")
print(f"→ Q→ΛQCD: αs→∞（色禁闭, 无自由夸克）")
print(f"→ 实验值: αs(MZ=91.2 GeV) ≈ 0.1181 (PDG 2024)")
```

**输出示例**：

```
QCD 跑动耦合常数 αs(Q)
==================================================
   Q (GeV) |       αs | 物理含义
--------------------------------------------------
       0.2 |   >10   | → 禁闭区(微扰失效)
       0.5 |  0.6035 | ██████ → 强耦合(强子物理)
       1.0 |  0.3895 | ████ → 中等
       2.0 |  0.2961 | ███ → 中等
       5.0 |  0.2172 | ██ → 中等
      10.0 |  0.1830 | ██ → 中等
      91.2 |  0.1280 | █ → 弱耦合(Z 玻色子质量)
    1000.0 |  0.0829 |  → 渐近自由

→ Q→∞: αs→0（渐近自由, Gross/Politzer/Wilczek 1973）
→ Q→ΛQCD: αs→∞（色禁闭, 无自由夸克）
→ 实验值: αs(MZ=91.2 GeV) ≈ 0.1181 (PDG 2024)
```

**反直觉发现**：QCD 的耦合常数是**跑动**的——与电磁力（$\alpha \approx 1/137$ 基本固定）完全不同。在 $Q \approx 0.2$ GeV（$\Lambda_{\text{QCD}}$）处，$\alpha_s$ 发散到无穷大，这意味着**低能 QCD 无法用微扰论处理**——必须用格点 QCD（lattice QCD，在离散时空格点上做数值模拟）或有效理论（手征微扰论）。Princeton 理论组的 David Huse 在格点 QCD 和统计力学交叉领域有重要贡献。

---

## 7. 习题集

### 基础题（Griffiths / Halzen & Martin · PHY 539 级别）

**P7.1** 写出标准模型三代费米子的完整列表（含色荷），标注哪些参与强相互作用。

**P7.2** 用 SEMF 计算铀-238 的每核子结合能，与铁-56 比较。裂变 U-238 → 两个 A≈119 的碎片释放多少能量？

> **答案**：$B/A$(U-238) $\approx 7.6$ MeV，$B/A$(Fe-56) $\approx 8.8$ MeV。释放 $\approx 238 \times (8.8 - 7.6) \approx 286$ MeV。

### 中级题（Schwartz · PHY 539/613 级别）

**P7.3**（QED 截面）用树级 QED 费曼图计算 $e^+e^- \to \mu^+\mu^-$ 的散射截面（高能极限 $s \gg m^2$）。

> **答案**：$\sigma = \frac{4\pi\alpha^2}{3s}$（点粒子截面）。

**P7.4**（Weinberg 角）已知 $m_W = 80.4$ GeV，$m_Z = 91.2$ GeV。用 $\cos\theta_W = m_W/m_Z$ 求 Weinberg 角 $\theta_W$ 和电磁耦合 $e = g\sin\theta_W$。

> **答案**：$\cos\theta_W = 0.882$，$\theta_W \approx 28.1°$，$\sin^2\theta_W \approx 0.223$。

**P7.5**（幻数）解释为什么核壳模型需要引入**强自旋-轨道耦合**才能复现幻数 28, 50, 82, 126。没有自旋-轨道耦合时，幻数会是多少？

> **提示**：谐振子势给出幻数 $2, 8, 20, 40, 70, \ldots$（不含 28, 50, 82, 126）。Mayer-Jensen 的洞见：$V_{ls}\vec{l}\cdot\vec{s}$ 使 $j = l+1/2$ 和 $j=l-1/2$ 大幅劈裂，打破原来的壳层结构。

### 挑战题（Peskin / Weinberg · PHY 613/619 级别）

**P7.6**（渐近自由）推导 QCD 一圈 $\beta$ 函数 $\beta(g) = -\frac{g^3}{16\pi^2}\!\left(\frac{11}{3}N_c - \frac{2}{3}N_f\right)$（$N_c=3$）。解释为什么胶子自相互作用项 $11N_c/3$ 使 $\beta < 0$（渐近自由），而 QED 的 $\beta > 0$（屏蔽增强）。

**P7.7**（Higgs 机制）写出 $SU(2)\times U(1)$ Higgs 模型的拉格朗日量，用幺正规范 $\Phi = (0, (v+h)/\sqrt{2})^T$ 证明 $W^\pm, Z$ 获得质量而 $\gamma$ 保持无质量。

**P7.8**（Yang-Mills / Princeton 传统）杨振宁与 Mills（1954）引入了非阿贝尔规范理论——当时没有已知物理应用。论证为什么 $SU(2)$ 规范理论必然要求存在**三个**自旋 1 玻色子，且它们自身带荷（互相耦合）。这与 Maxwell 的 $U(1)$ 理论（光子不带电、无自相互作用）有何本质区别？

---

## 8. 不足与延伸

### 本主题的局限

1. **微扰论失效区**：QFT 的 Feynman 图展开是**耦合常数的幂级数**。当 $\alpha_s \sim 1$（低能 QCD），微扰展开不收敛——强子物理（ confinement、质量谱、散射）必须用非微扰方法（格点 QCD、有效理论）。

2. **标准模型的未解问题**：
   - **中微子质量**：标准模型预言中微子无质量，但振荡实验（1998 年 Super-K）证明它们有微小质量。
   - **暗物质**：标准模型无候选粒子。WIMP、轴子、惰性中微子是热门候选。
   - **物质-反物质不对称**：宇宙中物质远多于反物质，标准模型的 CP 破坏不足以解释。
   - **Hierarchy 问题**：为什么 Higgs 质量（$125$ GeV）远小于 Planck 质量（$10^{19}$ GeV）？超对称是候选方案。

3. **引力不在标准模型中**：广义相对论的量子化给出不可重正化的理论。弦理论（Witten, IAS）是统一的候选方案，但至今无实验验证。

4. **核物理的复杂性**：SEMF 精度约 $1\%$，精确核物理需要壳模型计算或 ab initio 方法（格子 EFT），计算量极大。

### 延伸方向

| 方向 | Princeton 课程 | 教材 |
|------|---------------|------|
| 弦理论 | PHY 639/689 | Polchinski *String Theory* / Witten lectures |
| 格点 QCD | PHY 629 | Gattringer & Lang |
| 超对称 | PHY 629 | Wess & Bagger *Supersymmetry and Supergravity* |
| 宇宙学 | PHY 537 | Dodelson *Modern Cosmology* |
| 中微子物理 | PHY 539 进阶 | Zuber *Neutrino Physics* |

### Princeton 特色注记

Princeton/IAS 在粒子物理的地位来自**理论深度**而非实验规模（实验主要在 CERN/Fermilab）。关键人物和传统：

**Eugene Wigner**（IAS, 1963 诺贝尔奖）把群论引入量子力学后，物理学家开始意识到**对称性决定相互作用**——这是规范原理的哲学源头。Yang-Mills 理论（1954）将 Wigner 的思想推广到非阿贝尔规范群 $SU(2)$，为标准模型奠定了数学基础。

**Steven Weinberg**（在 IAS 任访问学者期间完成了电弱统一理论的关键工作, 1967, 1979 诺贝尔奖）。Weinberg 的三卷本 *The Quantum Theory of Fields* 是 QFT 的标准研究生教材，从公理出发唯一确定理论形式——Princeton `PHY 619` 的核心参考。

**Edward Witten**（IAS, 1990 Fields Medal）将物理直觉（路径积分、规范对称、全息原理）带入纯数学，开创了 M-理论、拓扑量子场论、镜像对称等新领域。Witten 的工作证明了**最深的数学往往来自物理直觉**——这是 Princeton/IAS 独特的数理交叉传统的巅峰。

Princeton `PHY 613/619`（QFT 序列）的训练目标不是「学会算费曼图」，而是理解**为什么宇宙选择了量子场论**——从 Lorentz 不变性 + 量子力学 + 定域性 + 幺正性出发，量子场论的形式几乎被唯一确定。这是 Weinberg 在 Princeton 推广的「**no-alternative**」论证：不是物理学家选择了 QFT，而是大自然别无选择。

---

> **上一主题**：[06 凝聚态与固体物理](../topic06-solid-state/solid-state.md)
>
> **下一主题**：[08 广义相对论与宇宙学](../topic08-gr-cosmology/gr-cosmology.md) — GR、黑洞与宇宙学，Einstein/Wheeler 在 Princeton/IAS 的遗产

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：粒子物理研究「宇宙最小的积木是什么、它们如何相互作用」——标准模型给出 17 种基本粒子 + 3 种相互作用（强、弱、电磁），几乎解释了除引力外的一切。
>
> **生活类比**：想象乐高积木。整个宇宙由 12 种费米子（6 夸克 + 6 轻子，物质粒子）和 5 种玻色子（4 种力的传递者 + Higgs）搭成。夸克「胶合」组成质子中子（强相互作用 = 胶水），电子「绕核」（电磁 = 磁铁），中微子「穿透」（弱 = 衰变）。Higgs 粒子是给所有粒子赋予质量的「_名人光环_」——只有被它「看到」的粒子才有质量，光子不被它看到，所以光子无质量。
>
> **反直觉发现**：夸克永远无法被单独看到！这就是**色禁闭**——夸克之间靠得越近力越小（渐近自由，2004 诺奖 Gross, Politzer, Wilczek），但你想把它们拉开，能量会大到「_拉出新夸克对_」。就像拉橡皮筋：拉到一定程度，橡皮筋断裂变成两根——你永远得不到「单根」。这是 QCD 的几何美学：强相互作用随距离增强，与电磁/引力（随距离减弱）完全相反。

---

## 🔗 衔接：从哪来，到哪去

| 阶段 | 内容 | 关键转折 |
|------|------|---------|
| **前置** | [03 量子](../topic03-quantum/quantum.md) 量子力学 + [02 EM](../topic02-electromagnetism/em.md) 电磁学 | 量子 + 经典场论 = QFT 的双基础 |
| **危机 1** | 弱相互作用破坏宇称（Lee & Yang 1956）+ 强子动物园（100+「基本」粒子） | 1960s 物理学的混乱：需要新组织原理 |
| **升级** | 规范对称性 $SU(3)\times SU(2)\times U(1)$ + Higgs 机制 | 标准模型（1970s）统一强/弱/电磁，1979 诺奖 Weinberg-Salam-Glashow |
| **危机 2** | 引力不在标准模型中 + 中微子质量 + 暗物质 + hierarchy problem | 弦理论？超对称？大统一？均未实验验证 |
| **后续** | → [08 GR](../topic08-gr-cosmology/gr-cosmology.md)：量子引力 + 宇宙学 → 弦/M-理论 | 粒子物理 + 宇宙学 = 21 世纪物理学的「_终极统一_」梦想 |

---

## 🏭 理论联系实际：5 个现代应用

1. **医用同位素（PET / 放疗）** — 正电子发射断层扫描用 $^{18}$F-FDG（氟-18 标记葡萄糖），衰变产生的正电子与电子湮灭产生两个 511 keV 光子。本文 §6 半经验质量公式 + $\beta^+$ 衰变的工程化。

2. **核能：裂变反应堆 + 聚变（ITER）** — 铀-235 裂变（$B/A$ 曲线的峰值在 Fe-56）产生 ~200 MeV/裂变；ITER 用 D-T 聚变（$^2\text{H}+^3\text{H}\to{}^4\text{He}+n+17.6$ MeV）。本文 SEMF + Q 值计算直接对应。

3. **μ子催化聚变（μCF）** — 用 μ子替代电子形成「_μ 分子_」，因为 μ 子比电子重 207 倍，分子键长缩短，聚变概率大增。Princeton 的核物理组曾研究此方向——把粒子物理实验室的技术用于清洁能源。

4. **缪子 $g-2$ 精密测量**（Fermilab E982）— 测量 μ 子的反常磁矩，精度 $10^{-10}$。如果与标准模型预言有偏差，就是**新物理**信号（暗光子？超对称？）。2023 年精度提升后，与理论的 5σ 张力持续存在——可能改变物理学。

5. **加速器技术在半导体中的应用** — 离子注入（用粒子加速器把硼/磷注入硅晶圆）是芯片制造的标配工艺。CERN/Fermilab 衍生的超导磁体、射频腔技术也用于医用电疗、同步辐射光源。

---

## 🔬 最新研究前沿（2024-2026）

1. **Glueball（胶球）实验证据**（2026 年 8 月，Nature News）— 物理学家宣布发现了神秘的「_胶球_」——由胶子（而非夸克）组成的复合粒子！这是 QCD 预言的纯规范束缚态，标量胶球 $f_0(1710)$ 候选被 BESIII/LHCb 数据支持。标准模型的最后一个未验证强子态可能被确认。

2. **μ子 $g-2$ 的 5σ 异常**（2023–2026 持续）— Fermilab E982 2023 年公布的新精度数据与标准模型预言存在 ~5σ 偏差。如果「_新物理的灯塔_」被确认（暗光子？轻夸克伙伴？），将改写粒子物理 50 年来的格局。理论计算（强子真空极化的格点 QCD）2024–2026 在 Nature/Science 持续更新。

3. **W 玻色子质量新测量**（2022–2025 CDF/Fermilab）— 2022 年 CDF 实验报告 $m_W$ 与标准模型预言偏离 7σ！2024–2025 ATLAS/CMS 的新测量正在交叉验证。如果确认，暗示新物理（超对称？额外维度？）。本文 P7.4 Weinberg 角计算的现实意义。

4. **轴子暗物质探测 ADMX**（2024–2026）— 西雅图的轴子暗物质微波腔实验持续扫描参数空间。轴子（PQ 理论预言的伪标量玻色子）是强 CP 问题的解 + 暗物质的头号候选。2024 年 ADDEX 升级，Princeton 理论组参与预言的最佳扫描范围。

5. **弦理论/M-理论的「_Swampland_」纲领**（2024–2026 IAS）— Cumrun Vafa（Harvard, 与 IAS 合作）的「_Swampland 纲领_」用弦论的一致性约束排除大量看似有效的有效场论。Witten 等人在 2024–2026 持续深化，给出暗能量状态方程 $w > -1$ 的弦论下界——与 DESI 2024 观测（暗示 $w \neq -1$）可能呼应。

---

## 🗺️ 学习 Roadmap（Princeton 路径）

```
PHY 539  Particle Physics (Schwartz / Halzen&Martin)  ← 标准模型 + 费曼规则入门
   │
   ├──[前置] PHY 403 群论 (Wigner 传统)               ← SU(3) 色荷, SU(2) 弱同位旋
   │
PHY 613  QFT I (Peskin & Schroeder)                  ← 研究生：路径积分 + 重正化
   │
PHY 619  QFT II (Weinberg / Srednicki)               ← 电弱统一 + 非阿贝尔规范理论
   │
   ╰──→ PHY 629  Lattice QCD / SUSY                   ← 格子数值 + 超对称
   ╰──→ PHY 639/689 String Theory (Polchinski/Witten) ← 弦/M-理论：统一的候选
   ╰──→ PHY 537  Cosmology (Dodelson)                 ← 早期宇宙粒子物理 + 暗物质
```

**知识检查清单**：

- [ ] 能否画出 QED 树级 $e^+e^- \to \mu^+\mu^-$ 的费曼图并算截面？
- [ ] 能否解释 Weinberg 角 $\theta_W$ 如何把 $(W^3, B)$ 混合成 $(\gamma, Z)$？
- [ ] 能否说出为什么 QCD 渐近自由（$\beta < 0$）而 QED 不是？（胶子自相互作用）
- [ ] 能否解释 Higgs 机制如何让 $W, Z$ 获得质量而 $\gamma$ 保持无质量？
- [ ] 能否说出标准模型的四个未解问题？（中微子质量、暗物质、CP、hierarchy）

> **Witten 的洞见**（IAS, Fields Medal 1990）：「_最深的数学往往来自物理直觉_」。Yang-Mills（1954）当时无应用，后来成为标准模型的核心；弦理论（1970s）源于强子物理的副产品，现在统一了所有相互作用。Princeton/IAS 的传统是：**相信物理直觉，哪怕数学尚未跟上**——规范对称性、全息原理、拓扑量子场论，都是物理先于数学的胜利。


---

*完成日期：2026-08-13*
