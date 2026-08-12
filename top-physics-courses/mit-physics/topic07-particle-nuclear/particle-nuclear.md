# Topic 07 · 粒子物理与核物理（MIT 8.701 / 8.294 / 8.705）

> **教材**：David Griffiths《Introduction to Elementary Particles》2ed + Kenneth Krane《Introductory Nuclear Physics》
>
> **覆盖课程**：
> - **8.701** Introduction to Nuclear and Particle Physics（Griffiths：标准模型 / 费曼图 / 散射）
> - **8.294** Particle Physics II（进阶弱电统一 / QCD 基础）
> - **8.705** Nuclear Physics（Krane：核结构 / 核衰变 / 核反应）
>
> **宪法**：直觉 → 公式 → 代码(bash 跑通) → 不足 → 应用

---

## 目录

1. [粒子物理概览：标准模型](#1-粒子物理概览标准模型)
2. [夸克与强相互作用（QCD）](#2-夸克与强相互作用qcd)
3. [弱相互作用与电弱统一](#3-弱相互作用与电弱统一)
4. [费曼规则与散射截面](#4-费曼规则与散射截面)
5. [核结构模型](#5-核结构模型)
6. [核衰变与放射性](#6-核衰变与放射性)
7. [核反应与核能](#7-核反应与核能)
8. [Python 代码演示](#8-python-代码演示)
9. [习题与解答](#9-习题与解答)
10. [反直觉发现](#10-反直觉发现)
11. [不足与延伸](#11-不足与延伸)

---

## 1. 粒子物理概览：标准模型

### 1.1 基本粒子家族

标准模型是描述所有已知基本粒子及其相互作用（引力除外）的量子场论。粒子分三大类：

**费米子**（自旋 1/2，物质粒子）：

| 代 | 夸克（自旋 1/2，色荷 ×3） | 轻子（自旋 1/2，无色荷） |
|----|-------------------------|------------------------|
| I | $u$ (up, ~2.2 MeV), $d$ (down, ~4.7 MeV) | $e^-$ (0.511 MeV), $\nu_e$ (< 0.8 eV) |
| II | $c$ (charm, ~1.28 GeV), $s$ (strange, ~96 MeV) | $\mu^-$ (105.7 MeV), $\nu_\mu$ (< 0.17 MeV) |
| III | $t$ (top, ~173 GeV), $b$ (bottom, ~4.18 GeV) | $\tau^-$ (1777 MeV), $\nu_\tau$ (< 18.2 MeV) |

**规范玻色子**（自旋 1，力的传递者）：

| 玻色子 | 力 | 质量 | 耦合 |
|--------|-----|------|------|
| 光子 $\gamma$ | 电磁 | 0 | $\alpha \approx 1/137$ |
| $W^\pm$, $Z^0$ | 弱 | 80.4, 91.2 GeV | $\alpha_W \approx 1/30$ |
| 胶子 $g$ (×8) | 强 | 0 | $\alpha_s \approx 0.1$—$1$ |

**Higgs 玻色子**（自旋 0，质量起源）：$H$（125 GeV），2012 年 LHC 发现。

### 1.2 四种基本力

| 力 | 相对强度 | 力程 | 传递者 |
|----|---------|------|--------|
| 强 | 1 | $\sim 10^{-15}$ m | 胶子 |
| 电磁 | $1/137$ | $\infty$ | 光子 |
| 弱 | $10^{-6}$ | $\sim 10^{-18}$ m | $W, Z$ |
| 引力 | $10^{-39}$ | $\infty$ | 引力子（未发现） |

强力和弱力在日常生活不可见——它们只作用在核尺度上。但它们决定了原子核的存在、太阳的发光、超新星爆炸。

### 1.3 守恒定律

每个对称性对应一个守恒量（Noether 定理）：

| 守恒量 | 对称性 | 适用相互作用 |
|--------|--------|------------|
| 能量 $E$、动量 $\mathbf{p}$ | 时空平移 | 所有 |
| 角动量 $J$ | 旋转 | 所有 |
| 电荷 $Q$ | $U(1)_{em}$ | 所有 |
| 重子数 $B$ | $U(1)_B$ | 所有（实验上） |
| 轻子数 $L_e, L_\mu, L_\tau$ | $U(1)_L$ | 所有（实验上） |
| 奇异数 $S$、粲数 $C$ 等 | 味 | 强、电磁（弱可破坏） |
| 色荷 | $SU(3)_c$ | 强 |
| 宇称 $P$ | 空间反演 | 强、电磁（弱最大破坏） |

宇称在弱相互作用中破坏——这是 1956 年李政道-杨振宁的发现（1957 诺奖），由吴健雄实验确认。

---

## 2. 夸克与强相互作用（QCD）

### 2.1 夸克禁闭

夸克从未被单独观测到——它们总是束缚在**强子**中。

- **介子**（Meson）：夸克 + 反夸克（$q\bar{q}$），如 $\pi^+ = u\bar{d}$，自旋为整数（玻色子）。
- **重子**（Baryon）：三个夸克（$qqq$），如质子 $p = uud$，中子 $n = udd$，自旋为半整数（费米子）。

**夸克禁闭**：色荷之间的势能随距离线性增长——

$$
V(r) \approx -\frac{4}{3}\frac{\alpha_s}{r} + \sigma r
$$

其中 $\sigma \approx 1$ GeV/fm 是**弦张力**。拉开到 ~1 fm 时能量足够产生新夸克对→强子化→永远看不到自由夸克。

### 2.2 渐近自由

QCD 的反直觉特性：耦合常数 $\alpha_s$ 随能量增加（距离减小）而**减弱**：

$$
\alpha_s(Q^2) \approx \frac{12\pi}{(33 - 2n_f)\ln(Q^2/\Lambda^2_{QCD})}
$$

其中 $n_f$ 是味数，$\Lambda_{\text{QCD}} \approx 200$ MeV。

→ 高能（短距）时夸克几乎自由——这叫**渐近自由**（Asymptotic Freedom）。2004 年 Gross, Wilczek, Politzer 因此获诺奖。

低能（长距）时耦合强→微扰论失效→需要格点 QCD（数值模拟）。

### 2.3 质子的质量来源

质子由三个夸克组成：$u(2.2) + u(2.2) + d(4.7) \approx 9.1$ MeV。但质子质量是 938 MeV！

差额 929 MeV = **胶子场能量 + 夸克动能**。→ **可见物质的质量 99% 来自强相互作用场的能量**，而非 Higgs 机制。Higgs 只给夸克/轻子约 1% 的质量。

### 2.4 强子谱

夸克模型预测了大量强子态。最轻的介子（赝标介子）：

| 介子 | 组成 | 质量 (MeV) |
|------|------|-----------|
| $\pi^\pm$ | $u\bar{d}, d\bar{u}$ | 140 |
| $\pi^0$ | $(u\bar{u} - d\bar{d})/\sqrt{2}$ | 135 |
| $K^\pm$ | $u\bar{s}, s\bar{u}$ | 494 |
| $\eta$ | $(u\bar{u}+d\bar{d}-2s\bar{s})/\sqrt{6}$ | 548 |

$\pi$ 介子特别轻——它是**手征对称性自发破缺**的 Goldstone 玻色子。

---

## 3. 弱相互作用与电弱统一

### 3.1 β 衰变与费米理论

中子衰变：$n \to p + e^- + \bar{\nu}_e$。费米（1934）的四费米子点相互作用：

$$
\mathcal{L}_{\text{Fermi}} = -\frac{G_F}{\sqrt{2}}[\bar{p}\gamma^\mu(1-g_A\gamma^5)n][\bar{e}\gamma_\mu(1-\gamma^5)\nu]
$$

$G_F \approx 1.166\times 10^{-5}$ GeV$^{-2}$（费米常数）。这个理论在低能完美工作，但在高能 ($E\sim\sqrt{G_F^{-1}}\approx 300$ GeV) 破坏幺正性→需要 $W$ 玻色子。

### 3.2 弱相互作用的 V-A 结构

弱流是"矢量减赝矢量"：$J^\mu = \bar{\psi}\gamma^\mu(1 - \gamma^5)\psi$。

$(1 - \gamma^5)$ 投影出**左旋**粒子——弱相互作用只耦合左旋费米子（和右旋反费米子）。这是宇称最大破坏的根源。

→ 宇称破坏 = 自然界区分左右手。在弱相互作用中，一个镜中的世界行为**不同**。

### 3.3 电弱统一：Glashow-Weinberg-Salam

1961-1968 年，电磁力（$U(1)_Y$）和弱力（$SU(2)_L$）被统一为**电弱理论**（1979 诺奖）：

$$
\mathcal{L}_{EW} = \mathcal{L}_{\text{gauge}} + \mathcal{L}_{\text{Higgs}} + \mathcal{L}_{\text{Yukawa}}
$$

**Higgs 机制**：标量场 $\phi$ 获得真空期望值 $v \approx 246$ GeV，自发破缺 $SU(2)_L\times U(1)_Y \to U(1)_{em}$。

- 给 $W, Z$ 玻色子质量：$m_W = gv/2$，$m_Z = gv/(2\cos\theta_W)$
- 给费米子质量（通过 Yukawa 耦合 $y_f\bar{\psi}\phi\psi$）：$m_f = y_f v/\sqrt{2}$
- 光子保持无质量（未被破缺的 $U(1)_{em}$）

**Weinberg 角**：$\cos\theta_W = m_W/m_Z$，实验值 $\sin^2\theta_W \approx 0.231$。

### 3.4 CKM 矩阵

夸克的弱本征态与质量本征态不同，由 CKM 矩阵（Cabibbo-Kobayashi-Maskawa, 2008 小林-益川诺奖）联系：

$$
\begin{pmatrix}d'\\s'\\b'\end{pmatrix} = V_{\text{CKM}}\begin{pmatrix}d\\s\\b\end{pmatrix}
$$

$V_{\text{CKM}}$ 是 $3\times 3$ 幺正矩阵，有 4 个独立参数（3 个混合角 + 1 个 CP 破坏相位）。

CP 破坏的存在→**宇宙中物质-反物质不对称的可能来源**（需要更多 CP 破坏源，标准模型不足）。

---

## 4. 费曼规则与散射截面

### 4.1 费曼图

粒子相互作用的视觉语言。每条线 = 传播子，每个顶点 = 耦合常数。

**QED 顶点**：$-ie\gamma^\mu$，光子-电子-电子耦合。

**Born 近似散射截面**（$2\to 2$ 过程）：

$$
\frac{d\sigma}{d\Omega} = \frac{1}{64\pi^2 s}\frac{|\mathbf{p}_f|}{|\mathbf{p}_i|}|\mathcal{M}|^2
$$

$\mathcal{M}$ 是不变振幅，由费曼图计算。$s$ 是质心系能量平方。

### 4.2 卢瑟福散射

电子被库仑场散射（$t$ 道光子交换）：

$$
\frac{d\sigma}{d\Omega} = \left(\frac{\alpha}{2E\sin^2(\theta/2)}\right)^2 \propto \frac{1}{\sin^4(\theta/2)}
$$

→ 小角散射主导（库仑力长程）。这也是卢瑟福 $\alpha$ 粒子散射实验发现原子核的理论基础。

### 4.3 深度非弹性散射：夸克的发现

1968 年 SLAC 实验：高能电子散射质子，发现大角散射截面远超连续模型预测——质子内部有**点状结构**（夸克）。

类比卢瑟福实验：大角散射→存在硬的内部结构。

---

## 5. 核结构模型

### 5.1 核的基本性质

原子核由 $Z$ 个质子和 $N$ 个中子组成，质量数 $A = Z + N$。

核半径：$R = r_0 A^{1/3}$，$r_0 \approx 1.2$ fm。

→ 核密度 $\rho \sim A/(\frac{4}{3}\pi R^3) \propto A/A = \text{const}$。所有核密度接近相同 $\sim 2.3\times 10^{17}$ kg/m³（中子星级密度）。

### 5.2 结合能与半经验质量公式

**液滴模型**（Weizsäcker 1935）给出半经验质量公式（SEMF）：

$$
B(A,Z) = a_v A - a_s A^{2/3} - a_c\frac{Z(Z-1)}{A^{1/3}} - a_a\frac{(A-2Z)^2}{A} + \delta(A,Z)
$$

| 项 | 物理意义 | 典型值 (MeV) |
|----|---------|-------------|
| 体积项 $a_v A$ | 每个核子的结合能 | $a_v \approx 15.8$ |
| 表面项 $-a_s A^{2/3}$ | 表面核子配对少 | $a_s \approx 18.3$ |
| 库仑项 $-a_c Z^2/A^{1/3}$ | 质子排斥 | $a_c \approx 0.71$ |
| 对称项 $-a_a(A-2Z)^2/A$ | $N=Z$ 偏好 | $a_a \approx 23.2$ |
| 配对项 $\delta$ | 偶偶>奇A>奇奇 | $\delta_0\approx 12$ |

**铁-56 的结合能/核子最高**（$\sim 8.8$ MeV）——这是铁峰的来源：比铁轻的核聚变释放能量，比铁重的核裂变释放能量。

### 5.3 壳模型

与原子电子的壳层结构类似，核子也填充分立能级。**幻数**：

$$
2, 8, 20, 28, 50, 82, 126
$$

质子或中子数等于幻数的核特别稳定（如 $^4$He, $^{16}$O, $^{208}$Pb）。这需要引入强自旋-轨道耦合来解释（Mayer-Jensen 1949, 1963 诺奖）。

---

## 6. 核衰变与放射性

### 6.1 三种衰变

| 模式 | 典型过程 | 守恒律 |
|------|---------|--------|
| $\alpha$ 衰变 | ${}^{238}\text{U}\to{}^{234}\text{Th}+{}^4\text{He}$ | $A, Z, B, L$ 全守恒 |
| $\beta$ 衰变 | $n\to p+e^-+\bar\nu_e$ | $B, L_e$ 守恒，$Z$ 变 |
| $\gamma$ 衰变 | 激发态$\to$基态$+\gamma$ | 一切守恒 |

### 6.2 衰变定律

放射性衰变是指数过程：

$$
N(t) = N_0 e^{-\lambda t}, \qquad t_{1/2} = \frac{\ln 2}{\lambda}
$$

$\lambda$ 是衰变常数。半衰期 $t_{1/2}$ 从纳秒（短寿命激发态）到 $10^{10}$ 年（$^{238}$U）不等——跨越 28 个量级。

### 6.3 β 衰变能谱与中微子

$\beta$ 衰变的电子能量不是单值的（连续谱），这似乎违反能量守恒。1930 年 Pauli 假设存在不可见的**中微子**带走能量：

$$
E_e + E_\nu = Q \quad (\text{衰变 } Q \text{ 值})
$$

电子能谱的端点能量 $E_e^{\max} = Q$ 对应 $\nu$ 能量为零。中微子 1956 年由 Reines-Cowan 实验确认（1995 诺奖）。

### 6.4 α 衰变的量子隧穿

$\alpha$ 粒子在核内被强作用束缚，需穿过库仑势垒才能逃逸。势垒高度 ~30 MeV，但 $\alpha$ 能量只有 ~5 MeV——经典禁止。

量子隧穿（Gamow 1928）给出衰变常数：

$$
\lambda \propto e^{-2G}, \quad G = \int_{r_1}^{r_2}\frac{\sqrt{2m(V(r)-E)}}{\hbar}\,dr
$$

→ $G$ 依赖 $Z$ 和 $E$，$E$ 越高隧穿越快——半衰期对 $\alpha$ 能量极度敏感（Geiger-Nuttall 定律：$E$ 变化 1 MeV，$t_{1/2}$ 变化 $10^5$ 倍）。

---

## 7. 核反应与核能

### 7.1 核裂变

重核（如 $^{235}$U）吸收中子后分裂为两个中等质量核 + 多个中子：

$$
{}^{235}\text{U} + n \to {}^{141}\text{Ba} + {}^{92}\text{Kr} + 3n + \sim 200\text{ MeV}
$$

链式反应：每个裂变释放 2-3 个中子，可触发更多裂变。

**临界条件**：$k_{\text{eff}} = 1$。$k > 1$ 超临界（炸弹），$k < 1$ 亚临界（停堆），$k = 1$ 临界（稳定运行）。

### 7.2 核聚变

轻核聚合释放能量（结合能曲线上升段）：

$$
{}^2\text{H} + {}^3\text{H} \to {}^4\text{He} + n + 17.6\text{ MeV}
$$

太阳核心的 pp 链：

$$
p + p \to {}^2\text{H} + e^+ + \nu_e \quad (\text{慢: } \sim 10^{10}\text{ 年/碰撞})
$$

需要量子隧穿穿透库仑势垒——温度 $\sim 15$ MK。

### 7.3 Q 值

核反应释放（或吸收）的能量由质量差给出：

$$
Q = (m_{\text{初}} - m_{\text{终}})c^2
$$

$Q > 0$ 放热（自发），$Q < 0$ 吸热（需阈值能量）。

---

## 8. Python 代码演示

### 8.1 相对论运动学与卢瑟福散射

```python
"""
(a) 卢瑟福散射截面 dσ/dΩ vs θ
(b) 相对论两体碰撞质心能量 √s
"""
import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# (a) 卢瑟福散射
theta = np.linspace(5, 175, 500)  # 角度 (度)
theta_rad = np.radians(theta)
# dσ/dΩ ∝ 1/sin⁴(θ/2) (纯几何形状因子)
dsigma = 1.0 / np.sin(theta_rad/2)**4

axes[0].semilogy(theta, dsigma, 'b-', linewidth=2)
axes[0].set_xlabel('散射角 θ (度)')
axes[0].set_ylabel('dσ/dΩ (任意单位)')
axes[0].set_title('卢瑟福散射: 截面 ∝ 1/sin⁴(θ/2)')
axes[0].set_xlim(0, 180)
axes[0].grid(alpha=0.3)
axes[0].annotate('小角: 库仑力长程\n→ 大截面', xy=(20, 1e3), fontsize=9, color='blue')
axes[0].annotate('大角: 近距碰撞\n→ 探测核结构', xy=(120, 0.1), fontsize=9, color='red')

# (b) 对撞机 vs 固定靶: √s
# 固定靶: s = m² + m² + 2mE_beam
# 对撞: s = (E1+E2)² (对头碰)
m_p = 0.938  # GeV, 质子质量
E_beam = np.logspace(0, 4, 500)  # GeV

sqrt_s_FT = np.sqrt(2*m_p**2 + 2*m_p*E_beam)  # 固定靶
sqrt_s_col = 2*E_beam  # 对撞机 (等束能)

axes[1].loglog(E_beam, sqrt_s_FT, 'b-', linewidth=2, label='固定靶 √s=√(2mE)')
axes[1].loglog(E_beam, sqrt_s_col, 'r-', linewidth=2, label='对撞机 √s=2E')
axes[1].fill_between(E_beam, sqrt_s_FT, sqrt_s_col, alpha=0.1, color='green')
axes[1].set_xlabel('束流能量 E (GeV)')
axes[1].set_ylabel('质心能量 √s (GeV)')
axes[1].set_title('对撞机 vs 固定靶: 能量利用率')
axes[1].legend(fontsize=9); axes[1].grid(alpha=0.3)
axes[1].annotate('LHC: E=7TeV\n固定靶√s≈115GeV\n对撞√s=14TeV', xy=(200, 100), fontsize=8, color='darkgreen')

plt.tight_layout()
plt.savefig('rutherford_kinematics.png', dpi=110, bbox_inches='tight')
print("已保存 rutherford_kinematics.png")
print(f"E=7000 GeV (LHC): 固定靶 √s={np.sqrt(2*0.938**2+2*0.938*7000):.0f} GeV")
print(f"                 对撞机 √s={2*7000} GeV")
print("→ 对撞机能量利用率高 ~100x，这就是为什么要建对撞机")
```

### 8.2 半经验质量公式与结合能曲线

```python
"""
Weizsäcker 半经验质量公式 (SEMF)
绘制 B/A vs A 曲线，标注铁峰和幻数
"""
import numpy as np
import matplotlib.pyplot as plt

def SEMF_BperA(A, Z):
    """半经验质量公式的每核子结合能 (MeV)"""
    a_v, a_s, a_c, a_a, delta = 15.8, 18.3, 0.714, 23.2, 12.0
    if A % 2 == 0 and Z % 2 == 0:       # 偶偶
        d = delta / A
    elif A % 2 == 1:                     # 奇 A
        d = 0
    else:                                # 奇奇
        d = -delta / A
    return (a_v - a_s*A**(-1/3) - a_c*Z*(Z-1)*A**(-4/3)
            - a_a*(A-2*Z)**2/A**2 + d)

# 对每个 A，取最稳定的 Z（近似 Z ≈ A/(2+0.015*A^{2/3})）
A_arr = np.arange(2, 250)
BperA = []
for A in A_arr:
    Z = int(round(A / (2 + 0.015*A**(2/3))))
    Z = max(1, min(Z, A-1))
    BperA.append(SEMF_BperA(A, Z))
BperA = np.array(BperA)

# 铁峰
idx_Fe = np.argmin(np.abs(A_arr - 56))

fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(A_arr, BperA, 'b-', linewidth=1.5)
ax.plot(56, BperA[idx_Fe], 'ro', markersize=10, zorder=5, label=f'Fe-56: B/A={BperA[idx_Fe]:.2f} MeV')

# 幻数标注
magic = [4, 16, 40, 48, 100, 132, 208]
for m in magic:
    if m < len(A_arr):
        ax.axvline(m, color='green', linestyle=':', alpha=0.5)
        ax.annotate(f'{m}', xy=(m, 1), fontsize=8, color='green', ha='center')

# 标注关键核
for A_label, name in [(4, '⁴He'), (12, '¹²C'), (16, '¹⁶O'), (235, '²³⁵U'), (238, '²³⁸U')]:
    idx = np.argmin(np.abs(A_arr - A_label))
    Z = int(round(A_label / (2 + 0.015*A_label**(2/3))))
    ax.annotate(name, xy=(A_label, SEMF_BperA(A_label, Z)),
                fontsize=8, ha='center', va='bottom')

ax.set_xlabel('质量数 A')
ax.set_ylabel('每核子结合能 B/A (MeV)')
ax.set_title('半经验质量公式: B/A vs A (铁峰在 A≈56)')
ax.legend(fontsize=10); ax.grid(alpha=0.3)
ax.set_xlim(0, 250); ax.set_ylim(0, 9.5)
plt.tight_layout()
plt.savefig('binding_energy.png', dpi=110, bbox_inches='tight')
print("已保存 binding_energy.png")
print(f"Fe-56: B/A = {BperA[idx_Fe]:.3f} MeV (峰值)")
print(f"U-238: B/A = {SEMF_BperA(238, 92):.3f} MeV (裂变释放 ~0.8 MeV/核子)")
print(f"He-4:  B/A = {SEMF_BperA(4, 2):.3f} MeV (聚变释放 ~7 MeV/核子→He)")
```

### 8.3 β 衰变能谱与 α 衰变半衰期

```python
"""
(a) β 衰变电子能谱 (费米理论), 端点能量 Q
(b) Geiger-Nuttall: 半衰期 vs α 能量 (指数关系)
"""
import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# (a) β 衰变电子能谱
# dN/dE ∝ p E (Q-E)²  (允许跃迁, 忽略库仑修正)
Q = 1.0  # 端点能量 (归一化)
E = np.linspace(0.001, Q-0.001, 500)
me = 0.511  # 电子质量
p = np.sqrt(E**2 - me**2) if Q > me else np.sqrt(E*(E+2*me))  # 相对论动量

# 使用 E_total = E + me
E_tot = E + me
p = np.sqrt(E_tot**2 - me**2)
spectrum = p * E_tot * (Q - E)**2  # 允许跃迁形状因子
spectrum /= spectrum.max()

axes[0].plot(E/Q, spectrum, 'b-', linewidth=2)
axes[0].fill_between(E/Q, spectrum, alpha=0.1, color='blue')
axes[0].set_xlabel('电子动能 E/Q')
axes[0].set_ylabel('dN/dE (归一化)')
axes[0].set_title('β 衰变电子能谱 (允许跃迁)')
axes[0].grid(alpha=0.3)
axes[0].annotate('连续谱!\n→ 中微子带走\n   剩余能量', xy=(0.3, 0.6), fontsize=9, color='blue')
axes[0].annotate('端点 E=Q\n(ν能量=0)', xy=(0.85, 0.05), fontsize=9, color='red')

# (b) Geiger-Nuttall 关系: log(t₁/₂) ∝ Z/√E_α
# 实验数据 (近似): 几个 α 衰变核
data = [
    ('²³⁸U',  92, 4.20, 4.47e9*3.15e7),    # 年→秒
    ('²²⁶Ra', 88, 4.78, 1600*3.15e7),
    ('²¹⁰Po', 84, 5.30, 138.4*24*3600),      # 日→秒
    ('²²²Rn', 86, 5.49, 3.82*24*3600),       # 日→秒
    ('²¹⁴Po', 84, 7.69, 1.64e-4),             # 秒
    ('²¹²Po', 84, 8.78, 2.99e-7),             # 秒
]

names = [d[0] for d in data]
Z_arr = np.array([d[1] for d in data])
E_alpha = np.array([d[2] for d in data])
t_half = np.array([d[3] for d in data])

axes[1].semilogy(E_alpha, t_half, 'ro', markersize=8)
for i, name in enumerate(names):
    axes[1].annotate(name, xy=(E_alpha[i], t_half[i]),
                     textcoords="offset points", xytext=(8, 5), fontsize=8)
axes[1].set_xlabel('α 粒子能量 E_α (MeV)')
axes[1].set_ylabel('半衰期 t₁/₂ (秒)')
axes[1].set_title('Geiger-Nuttall 定律: E_α 变化 3 MeV, t₁/₂ 变化 ~10²⁰')
axes[1].grid(alpha=0.3)
axes[1].set_ylim(1e-8, 1e18)

# 拟合线性关系 (在 log-1/√E 空间)
x_fit = 1/np.sqrt(E_alpha)
y_fit = np.log10(t_half)
coeffs = np.polyfit(x_fit, y_fit, 1)
x_line = np.linspace(x_fit.min()-0.02, x_fit.max()+0.02, 100)
axes[1].semilogy((1/x_line)**2, 10**np.polyval(coeffs, x_line), 'b--', alpha=0.5,
                 label=f'拟合: log(t) ∝ Z/√E')

axes[1].legend(fontsize=9)

plt.tight_layout()
plt.savefig('beta_alpha_decay.png', dpi=110, bbox_inches='tight')
print("已保存 beta_alpha_decay.png")
print("Geiger-Nuttall: E_α 4.2→8.8 MeV (2倍), t₁/₂ 10¹⁷→10⁻⁷ 秒 (变化 ~10²⁴)")
print("→ 量子隧穿概率对能量极度敏感")
```

---

## 9. 习题与解答

### 习题 1（相对论运动学）— 不变质量

两质子各 7 TeV 对撞。求质心能量 $\sqrt{s}$。

**解**：对撞机 $\sqrt{s} = 2E = 14$ TeV。这是 LHC 设计能量。

对比固定靶：$s = 2m_p^2 + 2m_p E_{\text{beam}}$，要达到 14 TeV 需 $E_{\text{beam}} \approx s/(2m_p) \approx (14\times 10^3)^2/(2\times 0.938) \approx 10^8$ GeV = 100 PeV——不现实。

### 习题 2（Q 值）— α 衰变

${}^{238}\text{U}\to{}^{234}\text{Th}+\alpha$。已知质量 ${}^{238}\text{U} = 238.0508$ u, ${}^{234}\text{Th} = 234.0436$ u, $\alpha = 4.0026$ u。求 $Q$ 值。

**解**：$Q = (238.0508 - 234.0436 - 4.0026)\times 931.5 = 0.0046\times 931.5 = 4.28$ MeV。

$\alpha$ 动能 $E_\alpha = Q\cdot\frac{m_{\text{Th}}}{m_{\text{Th}}+m_\alpha} \approx Q\cdot\frac{234}{238} = 4.20$ MeV ✓（反冲修正）。

### 习题 3（SEMF）— 最稳定核

用半经验质量公式估计最稳定的核（$B/A$ 最大）。

**解**：对固定 $A$，令 $\partial(B/A)/\partial Z = 0$：

$$
Z^* \approx \frac{A}{2 + (a_c/a_a)A^{2/3}}
$$

$A = 56$ 时 $Z^* = 56/(2 + 0.031\times 14.4) \approx 56/2.44 \approx 23$。实际 Fe-56 的 $Z = 26$（库仑项略偏，但接近）。$B/A\approx 8.8$ MeV ✓。

### 习题 4（弱衰变）— μ 子寿命

μ 子衰变 $\mu^-\to e^-+\bar\nu_e+\nu_\mu$。费米理论给出衰变率 $\Gamma \propto G_F^2 m_\mu^5$。若 $m_\mu = 105.7$ MeV, $\tau_\mu = 2.2$ μs，估算 $\tau_\tau$（$m_\tau = 1777$ MeV）。

**解**：$\tau \propto 1/m^5$：

$$
\tau_\tau = \tau_\mu\left(\frac{m_\mu}{m_\tau}\right)^5 = 2.2\times 10^{-6}\times\left(\frac{105.7}{1777}\right)^5 = 2.2\times 10^{-6}\times 7.4\times 10^{-6} \approx 1.6\times 10^{-11}\text{ s}
$$

实验值 $\tau_\tau = 2.9\times 10^{-13}$ s——偏大因为 τ 还能衰变到强子（更多道）。

### 习题 5（幻数）— 壳模型

$^{208}$Pb 有 82 个质子和 126 个中子——双幻数。解释为何它特别稳定。

**解**：82 和 126 都是幻数，质子和中子壳层都满。$^{208}$Pb 是已知最重的稳定核素之一，结合能/核子 7.87 MeV（仅略低于铁峰），第一激发态高达 2.6 MeV（壳层关闭→大能隙）。

### 习题 6（QCD 渐近自由）

$\alpha_s$ 在 $Q = 1$ GeV 时约 0.5，$Q = 100$ GeV 时约 0.12。验证 $\alpha_s \propto 1/\ln Q$。

**解**：$0.5/0.12 = 4.17$。$\ln(100)/\ln(1) = \infty$（发散）。实际上 $\alpha_s \propto 1/\ln(Q/\Lambda)$，$\Lambda \approx 200$ MeV。

$\ln(100/0.2)/\ln(1/0.2) = \ln(500)/\ln(5) = 6.21/1.61 = 3.86$。与 $0.5/0.12 = 4.17$ 接近 ✓。

### 习题 7（链式反应）

$^{235}$U 裂变每次释放 2.4 个中子（平均）。临界条件。

**解**：增殖因子 $k = \eta fp$（快裂变因子 × 热利用因子 × 逃脱共振概率 × …）。简化 $k = 2.4\times P_{\text{吸收}}$。若 50% 的中子被吸收引起新裂变，$k = 1.2 > 1$→超临界。需要控制棒吸收多余中子维持 $k = 1$。

### 习题 8（太阳聚变）

太阳每秒辐射 $3.8\times 10^{26}$ W。每次 pp 链释放 ~26.7 MeV。求每秒聚变反应数和年质量损失。

**解**：

$$
N = \frac{3.8\times 10^{26}}{26.7\times 1.6\times 10^{-13}} = 8.9\times 10^{37}\text{ 反应/s}
$$

每反应 4 个质子→He，质量损失 $4m_p - m_{\text{He}} = 0.7\%\times 4\times 1.67\times 10^{-27} = 4.7\times 10^{-29}$ kg。

$$
\dot{M} = 8.9\times 10^{37}\times 4.7\times 10^{-29} = 4.2\times 10^9\text{ kg/s}
$$

每年 $1.3\times 10^{17}$ kg——仅太阳质量的 $7\times 10^{-14}$。

---

## 10. 反直觉发现

### 10.1 宇称不守恒：自然界的左右不对称

1956 年以前，物理学家默认自然规律在镜面反射下不变（宇称守恒）。李政道和杨振宁提出弱相互作用可能破坏宇称。吴健雄实验（Co-60 β 衰变）确认：发射的电子优先沿**与核自旋相反**的方向——镜中世界的物理不同。

→ 宇宙在最基本的层面区分左手和右手。这个发现震惊了整个物理学界。

### 10.2 质量来自能量

质子质量 938 MeV 中，夸克质量（Higgs 给的）只有 ~9 MeV。其余 929 MeV = 胶子和夸克的动能/场能（$E = mc^2$）。

→ 我们身体质量的 **99%** 来自强相互作用场的能量，而非基本粒子的"静止质量"。Higgs 机制只解释了约 1%。

### 10.3 中微子振荡

中微子有三种味（$\nu_e, \nu_\mu, \nu_\tau$），但它们的质量本征态 $\nu_1, \nu_2, \nu_3$ 不同。飞行中，$\nu_e$ 可以变成 $\nu_\mu$ 再变回来——**中微子振荡**。

这要求中微子有**非零质量**——标准模型预测零质量，需要修正。2015 年超级神冈实验（梶田隆章）和 SNO（McDonald）因此获诺奖。

### 10.4 弱力的力程极短

电磁力和引力是长程力（力程 ∞），但弱力的力程只有 $\sim 10^{-18}$ m——比质子半径还小 1000 倍。原因是 $W, Z$ 玻色子很重（~80-90 GeV），力程 $\sim \hbar/(m_Wc) \approx 0.0025$ fm。

→ 虽然弱力的"强度"（$\alpha_W \sim 1/30$）不小，但在低能下表现得极弱——因为重玻色子交换被大质量压低（$G_F \propto 1/m_W^2$）。

---

## 11. 不足与延伸

| 本主题局限 | 延伸方向 | 课程 |
|-----------|---------|------|
| 树图微扰论 | 圈图修正、重整化、跑动耦合 | 8.323 QFT |
| 标准模型成功 | 中微子质量、暗物质、引力 | BSM / 8.702 |
| 微扰 QCD（高能） | 低能 QCD、格点规范、夸克禁闭 | 8.324 |
| 核结构平均场 | 关联核力、配对、超流核物质 | 8.701 续 |
| 简单衰变率 | 强子化、Jet 物理、风味物理 | 8.294 |
| 核反应运动学 | 核天体物理（r-过程、超新星核合成） | 8.901 |

**学习路径**：8.701（Griffiths 粒子 + Krane 核）→ 8.294（弱电/QCD 进阶）→ 8.705（核物理专题）→ 8.323/8.324（QFT 正式课）。

---

**参考**：
- Griffiths《Introduction to Elementary Particles》2ed, Ch 3-4 (弱/强), Ch 7-9 (电弱/QCD/标准模型)
- Krane《Introductory Nuclear Physics》Ch 3 (核结构), Ch 6-8 (衰变), Ch 10 (裂变/聚变)
- Perkins《Introduction to High Energy Physics》4ed
- Halzen & Martin《Quarks and Leptons》— QCD/QED 入门
- MIT OCW 8.701 (Wise/Redshaw) / 8.294 / 8.705
