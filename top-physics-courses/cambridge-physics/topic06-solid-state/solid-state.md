# Cambridge Part II · Solid State Physics

> **教材**：Ashcroft & Mermin *Solid State Physics* — 经典巨著；Simon *The Oxford Solid State Basics* — 现代友好的入门；Kittel *Introduction to Solid State Physics* (8th ed.) — 标准教材
>
> **Cambridge 课程编号**：Part II Solid State Physics
>
> **Cambridge 特色**：Cavendish Lab 是凝聚态实验的圣地——从 Bragg 父子的 X 射线衍射（1913 诺奖）到半导体物理（BCS 理论研究者 Cooper 曾访学剑桥）。剑桥强调"从晶格对称性出发推导一切"——晶体结构不是辅助知识，而是全部凝聚态物理的逻辑起点

---

## 目录

1. [晶体结构与倒格子](#1-晶体结构与倒格子)
2. [能带理论](#2-能带理论)
3. [声子与晶格热学](#3-声子与晶格热学)
4. [超导电性](#4-超导电性)
5. [金属与费米面](#5-金属与费米面)
6. [Python 代码演示](#6-python-代码演示)
7. [Tripos 风格习题](#7-tripos-风格习题)

---

## 1. 晶体结构与倒格子

### 1.1 Bravais 晶格

**Bravais 晶格**是平移对称下不变的无穷点阵：对于任意格点 $\mathbf{R} = n_1\mathbf{a}_1 + n_2\mathbf{a}_2 + n_3\mathbf{a}_3$，晶格平移 $\mathbf{R}$ 后与自身重合。

三维共有 **14 种 Bravais 晶格**，分属 7 大晶系。最常见的：

| 晶格 | 基矢示例 | 每原胞格点数 | 典型材料 |
|------|---------|-------------|---------|
| 简单立方 (SC) | $a\hat{x}, a\hat{y}, a\hat{z}$ | 1 | $\alpha$-Po (罕见) |
| 体心立方 (BCC) | SC + 中心 | 1 (传统) / 2 (惯用) | Fe, Cr, Na |
| 面心立方 (FCC) | SC + 各面心 | 1 / 4 (惯用) | Cu, Al, Au |
| 六方密堆 (HCP) | 60° 菱形底 + 半高 | 2 | Mg, Zn, Ti |

**反直觉发现**：FCC 和 HCP 的**堆叠密度相同**（均为 74%，理论最大值），仅堆叠顺序不同（FCC: ABCABC...，HCP: ABABAB...）。自然界约一半金属选 FCC，一半选 HCP——能量差异极小，由细节电子结构决定。

### 1.2 倒格子

**倒格子基矢**定义为：

$$\mathbf{b}_1 = 2\pi\frac{\mathbf{a}_2 \times \mathbf{a}_3}{\mathbf{a}_1\cdot(\mathbf{a}_2\times\mathbf{a}_3)}, \quad \text{etc.}$$

满足正交关系 $\mathbf{a}_i\cdot\mathbf{b}_j = 2\pi\delta_{ij}$。倒格矢 $\mathbf{G} = m_1\mathbf{b}_1 + m_2\mathbf{b}_2 + m_3\mathbf{b}_3$。

倒格子的物理意义：它定义了**动量空间中的周期性**。晶格中电子的波函数满足 Bloch 定理，在倒格子空间中周期化。

### 1.3 Brillouin 区与 X 射线衍射

**第一 Brillouin 区**（第一 BZ）是倒格子中的 Wigner-Seitz 原胞——围绕原点的最近邻倒格点的垂直平分面围成的区域。

**Bragg 条件**（衍射）：

$$2d\sin\theta = n\lambda$$

等价于 **Laue 条件**：$\mathbf{k}' - \mathbf{k} = \mathbf{G}$（散射前后波矢差等于倒格矢）。这是 Cambridge 的 Bragg 父子（William Henry & William Lawrence）的核心贡献——他们因此获 1915 年诺奖。

---

## 2. 能带理论

### 2.1 Bloch 定理

**Bloch 定理**：周期势 $V(\mathbf{r}+\mathbf{R}) = V(\mathbf{r})$ 中单粒子 Schrödinger 方程的解可写为：

$$\psi_{\mathbf{k}}(\mathbf{r}) = e^{i\mathbf{k}\cdot\mathbf{r}}u_{\mathbf{k}}(\mathbf{r}), \quad u_{\mathbf{k}}(\mathbf{r}+\mathbf{R}) = u_{\mathbf{k}}(\mathbf{r})$$

即平面波乘以周期函数。本征能量 $E(\mathbf{k})$ 在倒格子中周期：$E(\mathbf{k}+\mathbf{G}) = E(\mathbf{k})$。

### 2.2 近自由电子模型

电子近似自由（弱周期势微扰），但 Bragg 反射在**BZ 边界**打开能隙。

设弱势的 Fourier 分量 $V_\mathbf{G}$，在 $\mathbf{k} = \pi/a$（一维 BZ 边界）处，简并的两个平面波 $e^{\pm i\pi x/a}$ 被 $V_\mathbf{G}$ 耦合，对角化给出：

$$E_\pm = \frac{\hbar^2}{2m}\left(\frac{\pi}{a}\right)^2 \pm |V_\mathbf{G}|$$

**能隙** $= 2|V_\mathbf{G}|$。这就是**能带**的来源——自由电子的抛物线在 BZ 边界被"撕开"。

### 2.3 紧束缚模型

从另一个极端出发——原子轨道弱耦合。最近邻近似下：

$$E(\mathbf{k}) = \epsilon_0 - t\sum_{\text{n.n.}} e^{i\mathbf{k}\cdot\mathbf{\delta}}$$

其中 $t$ 为跃迁积分，$\mathbf{\delta}$ 为最近邻矢量。

简单立方晶格（6 个最近邻）：

$$E(\mathbf{k}) = \epsilon_0 - 2t[\cos(k_xa) + \cos(k_ya) + \cos(k_za)]$$

带宽 $W = 12t$（6 近邻 × 2）。$t$ 越大，轨道重叠越多，能带越宽——这是"局域 vs 离域"的定量表述。

### 2.4 导体、绝缘体、半导体

能带填充决定导电性。每个能带可容纳 $2N$ 个电子（自旋简并）。若**价电子数使最高占据带正好填满**（绝缘体/半导体），则 Fermi 能级落入能隙；若最高带**部分填充**（金属），则存在 Fermi 面。

| 类型 | 能隙 $E_g$ | 例子 | 室温导电 |
|------|-----------|------|---------|
| 绝缘体 | $E_g > 4$ eV | 金刚石 ($5.5$ eV) | 无 |
| 半导体 | $0 < E_g < 4$ eV | Si ($1.12$ eV), Ge ($0.67$ eV) | 温度依赖 |
| 半金属 | 能带微弱重叠 | Bi, Sb | 弱金属 |
| 金属 | 部分填充带 | Cu, Al | 强金属 |

**反直觉发现**：金刚石和硅的化学键本质相同（$sp^3$ 共价），但金刚石是极好的绝缘体而硅是半导体。差异全在能隙大小——而能隙由轨道重叠程度决定。碳原子小、轨道紧、重叠强、$t$ 大……但金刚石中价带和导带的间距反而最大。原因在于晶体势的深度——Si 的 $d$ 轨道参与使导带下移。

---

## 3. 声子与晶格热学

### 3.1 一维单原子链

一维链（弹簧常数 $k$，质量 $m$，间距 $a$）的运动方程：

$$m\ddot{u}_n = -k(u_n - u_{n-1}) - k(u_n - u_{n+1})$$

平面波解 $u_n = Ae^{i(qna - \omega t)}$ 给出**色散关系**：

$$\omega(q) = 2\sqrt{\frac{k}{m}}\left|\sin\frac{qa}{2}\right|$$

- $q\to 0$（长波）：$\omega \approx c_s|q|$，$c_s = a\sqrt{k/m}$ 为声速——**线性色散**（声学声子）
- $q = \pi/a$（BZ 边界）：$\omega_{\max} = 2\sqrt{k/m}$

### 3.2 双原子链与光学声子

若原胞含两原子（质量 $M_1, M_2$），出现**两支**：

- **声学支**（$q\to 0$ 时 $\omega\to 0$）：两原子同向运动
- **光学支**（$q\to 0$ 时 $\omega \neq 0$）：两原子反向运动

光学支的名称来源：若两原子带异号电荷（如 NaCl），反向振动产生交变偶极矩，可与红外光耦合——故名"光学声子"。

$$\omega_{\text{opt}}^2(0) = 2k\left(\frac{1}{M_1} + \frac{1}{M_2}\right)$$

### 3.3 Debye 模型与比热

**Debye 模型**：将声子色散近似为线性 $\omega = c_s q$，截止到 Debye 频率 $\omega_D$（由总模数 $3N$ 确定）。

低温 ($T \ll \Theta_D$) 比热的 **Debye $T^3$ 定律**：

$$C_V = \frac{12\pi^4}{5}Nk_B\left(\frac{T}{\Theta_D}\right)^3$$

高温 ($T \gg \Theta_D$) 回到 Dulong-Petit 经典值 $C_V = 3Nk_B$。

**反直觉发现**：经典统计给 $C_V = 3Nk_B$（每个自由度 $\frac{1}{2}k_BT$，每原子 6 自由度）。但实验在低温下 $C_V\to 0$——这是量子效应的直接证据。$T^3$ 定律的"3"恰好是空间维数；一维链会给出 $T^1$，二维给出 $T^2$。Debye 温度 $\Theta_D = \hbar\omega_D/k_B$ 是"量子冻结"的能量尺度。

### 3.4 声子热导

热导率 $\kappa = \frac{1}{3}C_v v_s \ell$，其中 $\ell$ 为声子平均自由程。低温下 $\ell$ 很大（缺陷散射少），但 $C_v\to 0$；高温下声子-声子 Umklapp 散射使 $\ell$ 锐减。两者竞争使 $\kappa(T)$ 在约 $\Theta_D/10$ 处出现**峰值**——这就是为什么铜在 20K 附近热导率最高。

---

## 4. 超导电性

### 4.1 零电阻与迈斯纳效应

**超导态的两大标志**（1911 Kamerlingh Onnes 发现零电阻，1933 Meissner-Ochsenfeld 发现完全抗磁性）：

1. **零电阻**：$T < T_c$ 时电阻突然降为零
2. **Meissner 效应**：超导体**主动排斥**内部磁场（$\mathbf{B}=0$），不同于理想导体（仅"冻结"磁通）

Meissner 效应证明超导是**热力学态**，而非无耗散的动力学态。

### 4.2 London 方程

**London 方程**（1935）唯象描述：

$$\frac{\partial \mathbf{J}_s}{\partial t} = \frac{n_s e^2}{m}\mathbf{E}, \qquad \nabla\times\mathbf{J}_s = -\frac{n_s e^2}{m}\mathbf{B}$$

第二式结合 Maxwell 方程给出**London 穿透深度**：

$$\lambda_L = \sqrt{\frac{m}{\mu_0 n_s e^2}}$$

磁场在超导体表面 $\lambda_L \sim 10^2$ nm 内指数衰减——不是瞬间为零，而是有限穿透深度。

### 4.3 BCS 理论

**BCS 理论**（Bardeen-Cooper-Schrieffer, 1957）的物理图像：

1. 电子与晶格振动（声子）耦合：一个电子畸变晶格，留下"正电荷尾迹"
2. 第二个电子被这个尾迹吸引——**有效吸引**
3. 两个电子（动量相反、自旋相反）形成 **Cooper 对**——一个束缚态！
4. 所有 Cooper 对凝聚到同一量子态——**相干超流**

BCS 能隙方程给出：

$$k_BT_c = 1.13\,\hbar\omega_D\,e^{-1/[N(E_F)V]}$$

其中 $N(E_F)$ 为 Fermi 能态密度，$V$ 为电子-声子耦合强度。

**反直觉发现**：Cooper 对中两个电子的**实际距离**约为 $10^3$–$10^4$ Å（相干长度 $\xi_0$），远大于晶格常数！这意味着 $10^6$ 个 Cooper 对互相重叠——这是**宏观量子现象**。超导不是"电子配对跳格子"，而是百万对电子的集体相干舞蹈。

### 4.4 第 I 类与第 II 类超导体

| 类型 | 临界场行为 | $\lambda$ vs $\xi$ | 例子 |
|------|-----------|---------------------|------|
| **第 I 类** | 单一 $H_c$，$H>H_c$ 立即正常 | $\lambda < \xi/\sqrt{2}$ | Pb, Hg, Sn |
| **第 II 类** | $H_{c1} < H < H_{c2}$ 混合态（磁通涡旋） | $\lambda > \xi/\sqrt{2}$ | Nb, 高 $T_c$ 铜氧化物 |

第 II 类的**磁通涡旋格子**（Abrikosov 格子，1957 诺奖）是超导磁体的物理基础——NbTi 线在 $H_{c2} \sim 15$ T 下仍超导，使 MRI 和粒子加速器成为可能。

---

## 5. 金属与费米面

### 5.1 自由电子气

Drude-Sommerfeld 模型：电子为自由 Fermi 气体。Fermi 能：

$$E_F = \frac{\hbar^2}{2m}(3\pi^2 n)^{2/3}$$

典型金属 $E_F \sim 1$–$10$ eV，对应 Fermi 温度 $T_F = E_F/k_B \sim 10^4$–$10^5$ K。这意味着**室温对电子气而言是"极低温"**——只有 Fermi 面附近 $\sim k_BT/E_F \sim 1\%$ 的电子可参与激发，这正是金属 $C_V \propto T$（线性）的来源。

### 5.2 Fermi 面拓扑

Fermi 面 $E(\mathbf{k}) = E_F$ 在 $\mathbf{k}$ 空间的形状决定了金属的输运性质。Fermi 面可以是球（自由电子）、近球（碱金属）、或多连通复杂形状（过渡金属）。

**反直觉发现**：碱金属（Li, Na, K）的 Fermi 面几乎是完美球——实验精度下偏差小于 $10^{-3}$。但铜的 Fermi 面不是球，而是"肚子+脖子"形状——脖子接触 BZ 边界，导致铜的 Hall 系数为**正**（仿佛载流子是空穴而非电子）。这就是"空穴导电"的真实来源——Fermi 面拓扑。

### 5.3 Wiedemann-Franz 定律

金属热导率与电导率之比正比于温度：

$$\frac{\kappa}{\sigma T} = L = \frac{\pi^2}{3}\left(\frac{k_B}{e}\right)^2 \approx 2.44\times10^{-8}\,\text{W}\Omega/\text{K}^2$$

$L$ 为 **Lorenz 数**。这是 Fermi 液体理论的预言，偏离 $L$ 值是强关联（非 Fermi 液体）的信号。

---

## 6. Python 代码演示

> 纯标准库实现：单/双原子链声子色散 + Debye 比热 + 一维紧束缚能带。

```python
"""
Cambridge Part II Solid State — 演示
1. 单原子链 & 双原子链声子色散关系
2. Debye 模型比热 C_V(T) — T³定律与 Dulong-Petit 极限
3. 一维紧束缚能带 + 能态密度
"""
import math

# ============================================================
# 实验1: 声子色散关系
# ============================================================
print("=" * 60)
print("实验1: 声子色散关系  (ω vs q)")
print("=" * 60)

# 单原子链: ω = 2√(k/m) |sin(qa/2)|, 取 √(k/m)=1, a=1
print("\n--- 单原子链 ---")
print(f"  ω(q) = 2√(k/m)|sin(qa/2)|, 取 a=√(k/m)=1")
print(f"  {'q/π':<10} {'ω':<12} {'类型'}")
for i in range(0, 11):
    q = i * math.pi / 10  # q 从 0 到 π
    omega = 2.0 * abs(math.sin(q / 2))
    regime = "长波(声速)" if q < 0.5 else ("BZ边界" if i == 10 else "")
    print(f"  {q/math.pi:<10.2f} {omega:<12.6f} {regime}")

# 双原子链 (质量 M1=1, M2=2)
print("\n--- 双原子链 (M₁=1, M₂=2, k=1) ---")
print("  光学支 & 声学支")
M1, M2, k_spring = 1.0, 2.0, 1.0
print(f"  {'q/π':<10} {'ω_acoustic':<14} {'ω_optical':<14} {'间隙'}")
for i in range(0, 11):
    q = i * math.pi / 10
    cos_q = math.cos(q)
    # 双原子链色散: ω² = k(1/M1+1/M2) ± k√((1/M1+1/M2)² - 4sin²(q)/(M1·M2))
    sum_inv = 1.0/M1 + 1.0/M2
    disc = sum_inv**2 - 4*math.sin(q)**2 / (M1*M2)
    disc = max(disc, 0.0)
    sqrt_disc = math.sqrt(disc)
    omega_ac = math.sqrt(k_spring * (sum_inv - sqrt_disc))
    omega_op = math.sqrt(k_spring * (sum_inv + sqrt_disc))
    gap = omega_op - omega_ac
    print(f"  {q/math.pi:<10.2f} {omega_ac:<14.6f} {omega_op:<14.6f} {gap:.6f}")

print(f"\n  q→0: 光学 ω(0) = √(2k(1/M1+1/M2)) = {math.sqrt(2*k_spring*sum_inv):.6f}")
print(f"  q→0: 声学 ω(0) = 0 (Goldstone 模)")
print(f"  声学-光学间隙 = 频率禁区 (无传播模)")

# ============================================================
# 实验2: Debye 模型比热
# ============================================================
print("\n" + "=" * 60)
print("实验2: Debye 比热  C_V(T/Θ_D)")
print("=" * 60)

def debye_cv(T_ratio, N_terms=2000):
    """Debye 比热 C_V / (3Nk_B), T_ratio = T/Θ_D
    C_V = 9Nk_B (T/Θ_D)³ ∫₀^{Θ_D/T} x⁴eˣ/(eˣ-1)² dx
    归一化后 C_V/(3Nk_B) = 3(T/Θ_D)³ ∫₀^{Θ_D/T} x⁴eˣ/(eˣ-1)² dx
    """
    if T_ratio < 1e-6:
        return 0.0
    x_max = 1.0 / T_ratio  # Θ_D/T
    integral = 0.0
    dx = x_max / N_terms
    for i in range(1, N_terms + 1):
        x = i * dx
        if x < 1e-4:
            # x⁴eˣ/(eˣ-1)² ≈ x² for small x
            integrand = x * x
        else:
            ex = math.exp(x)
            integrand = x**4 * ex / (ex - 1)**2
        integral += integrand * dx
    return 3.0 * T_ratio**3 * integral

print(f"  {'T/Θ_D':<12} {'C_V/3Nk_B':<14} {'极限'}")
print(f"  {'(高温)':<12} {'→1 (Dulong-Petit)':<20}")
print(f"  {'(低温)':<12} {'→(12π⁴/5)(T/Θ_D)³':<20}")
T3_coeff = 12 * math.pi**4 / 5  # ≈ 233.8
print(f"  Debye T³ 系数 = 12π⁴/5 = {T3_coeff:.1f}\n")

for T_ratio in [0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 2.0, 5.0]:
    cv = debye_cv(T_ratio)
    if T_ratio < 0.15:
        limit = T3_coeff * T_ratio**3
        label = f"T³={limit:.4f}"
    else:
        label = f"经典偏差{(1-cv)*100:+.1f}%"
    print(f"  {T_ratio:<12.2f} {cv:<14.6f} {label}")

print(f"\n  结论: T/Θ_D ≪ 1 → C_V ∝ T³ (Debye 定律)")
print(f"        T/Θ_D ≫ 1 → C_V → 3Nk_B (Dulong-Petit)")

# ============================================================
# 实验3: 一维紧束缚能带
# ============================================================
print("\n" + "=" * 60)
print("实验3: 紧束缚能带 + 能态密度 (1D)")
print("=" * 60)

# E(k) = ε₀ - 2t·cos(ka), 取 ε₀=0, t=1
print("  E(k) = -2t·cos(ka), t=1, a=1, BZ: k∈[-π/a, π/a]")
print(f"  带宽 W = 4t = 4.0")
print(f"  带顶 E = +2 (k=0), 带底 E = -2 (k=±π/a)\n")

t_hop = 1.0
# 能态密度 g(E) = (1/π)·1/√(4t²-E²)  (一维 van Hove 奇点)
print(f"  {'E':<8} {'cos(ka)':<10} {'k/π':<10} {'DOS∝1/√(4-E²)'}")
for E in [-1.9, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 1.9]:
    cos_ka = E / (2*t_hop)
    ka = math.acos(max(-1, min(1, cos_ka)))
    k_over_pi = ka / math.pi
    if abs(E) < 2.0:
        dos = 1.0 / math.sqrt(4.0 - E**2)
    else:
        dos = float('inf')
    print(f"  {E:<8.1f} {cos_ka:<10.4f} {k_over_pi:<10.4f} {dos:<14.6f}")

print(f"\n  反直觉: DOS 在带边 E=±2 处发散 (1D van Hove 奇点)!")
print(f"  → 一维系统在带边的态密度无穷大, 影响 Peierls 畸变")
```

---

## 7. Tripos 风格习题

### 习题 1（Part II 难度）：单原子链色散

一维单原子链（质量 $m$，弹簧常数 $k$，间距 $a$）：

(a) 导出色散关系 $\omega(q)$。
(b) 求长波极限下的声速 $c_s$。
(c) 证明群速度 $v_g = d\omega/dq$ 在 BZ 边界 $q=\pi/a$ 为零，并解释物理意义。

<details>
<summary>解答</summary>

(a) 运动方程 $m\ddot{u}_n = k(u_{n+1}+u_{n-1}-2u_n)$。代入 $u_n = Ae^{i(qna-\omega t)}$：

$$-m\omega^2 = k(e^{iqa}+e^{-iqa}-2) = -4k\sin^2\frac{qa}{2}$$

$$\omega(q) = 2\sqrt{\frac{k}{m}}\left|\sin\frac{qa}{2}\right|$$

(b) 长波 $q\to 0$：$\sin(qa/2)\approx qa/2$，$\omega\approx \sqrt{k/m}\cdot a|q|$，故 $c_s = a\sqrt{k/m}$。

(c) $v_g = \frac{d\omega}{dq} = a\sqrt{k/m}\cos(qa/2)$。在 $q=\pi/a$，$v_g = a\sqrt{k/m}\cos(\pi/2)=0$。

物理意义：BZ 边界处相邻原子的振动相位差 $\pi$（完全反相），这是**驻波**——能量不能传播，群速度为零。这是 Bragg 反射在晶格振动中的体现。$\square$
</details>

### 习题 2（Part II 难度）：Debye $T^3$ 定律

证明 Debye 模型在 $T\ll\Theta_D$ 时 $C_V = \frac{12\pi^4}{5}Nk_B(T/\Theta_D)^3$。

<details>
<summary>解答</summary>

Debye 比热：

$$C_V = 9Nk_B\left(\frac{T}{\Theta_D}\right)^3\int_0^{\Theta_D/T}\frac{x^4e^x}{(e^x-1)^2}dx$$

当 $T\ll\Theta_D$，积分上限 $\Theta_D/T\to\infty$：

$$I = \int_0^{\infty}\frac{x^4e^x}{(e^x-1)^2}dx$$

由分部积分 $\int_0^\infty x^4\frac{d}{dx}\left(-\frac{1}{e^x-1}\right)dx = 4\int_0^\infty\frac{x^3}{e^x-1}dx$。再用标准结果 $\int_0^\infty\frac{x^3}{e^x-1}dx = \Gamma(4)\zeta(4) = 6\cdot\frac{\pi^4}{90} = \frac{\pi^4}{15}$。

故 $I = \frac{4\pi^4}{15}$，代入：

$$C_V = 9Nk_B\left(\frac{T}{\Theta_D}\right)^3\cdot\frac{4\pi^4}{15} = \frac{12\pi^4}{5}Nk_B\left(\frac{T}{\Theta_D}\right)^3 \quad\square$$

$T^3$ 中的指数 3 来自三维态密度 $g(\omega)\propto\omega^2$。一维链会给出 $C_V\propto T$。
</details>

### 习题 3（Part II 难度）：BCS 能隙

BCS 理论给出 $T_c$ 处能隙闭合。零温能隙 $\Delta(0) = 1.764\,k_BT_c$。

(a) 解释为什么 Cooper 对的束缚能是 $2\Delta$ 而非 $\Delta$。
(b) 估算铅（$T_c = 7.2$ K）的 London 穿透深度 $\lambda_L$ 和相干长度 $\xi_0$ 的数量级。

<details>
<summary>解答</summary>

(a) $\Delta$ 是**拆散一个 Cooper 对中一个电子**所需的能量（将电子从凝聚态激发到准粒子态）。但 Cooper 对有两个电子，要完全破坏一对，需激发**两个**准粒子，总能量 $2\Delta$。因此 Cooper 对束缚能 = $2\Delta = 3.528\,k_BT_c$。

(b) 铅 $T_c = 7.2$ K：
- $\lambda_L \sim 100$–$400$ nm（实验约 40 nm，理论需 Fermi 速度等参数）
- $\xi_0 \approx \frac{\hbar v_F}{\pi\Delta} \approx \frac{0.54\,\text{eV}\cdot\text{nm}}{3.5\,k_BT_c} \sim 83$ nm（铅 $v_F\approx 6\times10^5$ m/s，$\Delta\approx 1.1$ meV）

铅是**第 I 类超导体**（$\kappa = \lambda/\xi < 1/\sqrt{2}$），而 Nb（$\kappa > 1/\sqrt{2}$）是第 II 类——这正是超导磁体用 NbTi 而非 Pb 的原因。$\square$
</details>

### 习题 4（Part II 预习）：紧束缚能带

简单立方晶格最近邻紧束缚，带宽 $W = 12t$。

(a) 写出 $E(\mathbf{k})$ 并求有效质量 $m^*$ 在带底 $\mathbf{k}=0$ 附近的值。
(b) 若 $t = 1$ eV，估算 Fermi 能（每原胞 1 个电子）。

<details>
<summary>解答</summary>

(a) $E(\mathbf{k}) = \epsilon_0 - 2t[\cos(k_xa)+\cos(k_ya)+\cos(k_za)]$。带底 $\mathbf{k}=0$，$E_{\min} = \epsilon_0 - 6t$。

小 $\mathbf{k}$ 展开 $\cos(ka)\approx 1 - k^2a^2/2$：

$$E \approx (\epsilon_0-6t) + ta^2k^2$$

有效质量：$\hbar^2k^2/(2m^*) = ta^2k^2$，故 $m^* = \hbar^2/(2ta^2)$。$t$ 越大（能带越宽），有效质量越轻——电子越"自由"。

(b) 简单立方 BZ 体积 $(2\pi/a)^3$，每态体积 $(2\pi/a)^3/(2N) = (2\pi)^3/2$（含自旋）。每原胞 1 电子 → Fermi 球体积 = BZ/2：

$$\frac{4\pi}{3}k_F^3 = \frac{1}{2}\cdot\frac{(2\pi)^3}{a^3}\cdot\frac{1}{2} \implies k_F = \left(\frac{3\pi^2}{a^3}\cdot a^3\right)^{1/3}\cdot\frac{1}{\sqrt[3]{2}}$$

化简 $k_Fa \approx (3\pi^2/2)^{1/3}\approx 1.92$。$E_F \approx ta^2k_F^2 = t(1.92)^2 \approx 3.7t \approx 3.7$ eV。$\square$
</details>

---

## Cambridge Cavendish 凝聚态传统

### Bragg 父子与 X 射线晶体学

Cavendish Lab 是**凝聚态实验的发源地**。William Henry Bragg 和 William Lawrence Bragg 父子在剑桥发展了 X 射线衍射分析晶体结构的方法——Bragg 定律 $2d\sin\theta = n\lambda$。1915 年他们共同获得诺贝尔物理学奖（Lawrence 当时仅 25 岁，至今最年轻的诺奖得主）。Bragg 方法不仅奠定了固体物理学，还直接导致了 DNA 双螺旋结构的发现（Cavendish 的 Crick 与 Watson，1962 诺奖）。

### 从晶体学到凝聚态

Cavendish 的凝聚态传统延续至今：

- **Nevill Mott** (1905–1996): 非晶半导体理论，1977 诺奖。他在剑桥建立的凝聚态理论组是世界顶级
- **Brian Josephson** (1940–): 22 岁时预言 Josephson 效应（超导隧道结），1973 诺奖。他是剑桥培养的凝聚态天才
- **David Thouless** (1934–2019): 剑桥本科，拓扑相变理论，2016 诺奖。他的工作直接源于剑桥对晶体缺陷和相变的深刻理解

### 半导体与超导

Cambridge Part II Solid State 的实验基础部分与 Cavendish 的**超导研究**紧密相连。剑桥的超导组长期研究非常规超导体（重费米子、铜氧化物、铁基超导体），Josephson 效应就诞生在 Cavendish。这种"理论-实验紧密结合"的传统使剑桥的凝聚态教学特别注重**物理直觉与数学严谨并重**——这正是 Ashcroft & Mermin 与 Simon 两本教材互补使用的教学哲学。

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Simon Ch 1-6 | 晶体 + 倒格子 + 能带 | 现代友好入门 |
| Simon Ch 9-12 | 声子 + 超导 | BCS 直觉推导 |
| Ashcroft & Mermin Ch 4-9 | 倒格子 + 能带 | 经典深入 |
| Ashcroft & Mermin Ch 23-27 | 声子 + 半导体 | Tripos 核心范围 |
| Kittel Ch 4-7 | 声子 + 能带 | 标准教材 |
| Kittel Ch 10-12 | 超导 + 半导体 | 应用导向 |
| Tinkham *Superconductivity* | London + BCS | 超导专著 |
| Marder *Condensed Matter Physics* | 全书 | 现代综合 |

---

**版本**：v1.0 (2026-08-12) · Cambridge Part II Solid State Physics


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：把亿亿个原子排成晶体，电子就开始玩出新花样——导电、绝缘、甚至零电阻超导，全靠"集体行为"，而不是单个原子的性质。
>
> **生活类比**：体育场人浪。单个观众只是坐着，但大家协调起来就能造出一圈"波"扫过全场；固体里的电子也一样，集体行动会产生单个电子完全没有的全新性质（能带、超导、磁性）。
>
> **反直觉发现（啊哈时刻）**：石墨和钻石都是纯碳，一个软且导电，一个硬且绝缘——差别只在原子怎么排列（晶体结构 → 能带结构）。同样是碳，换个排法就从铅笔芯变成钻戒。

---

## 🔗 衔接：从哪来，到哪去

- **前置知识**：**量子力学**（薛定谔方程、谐振子、周期势——Topic 3）、**统计力学**（Fermi-Dirac 分布——Topic 4）、Part IB 数学（群论、傅里叶）
- **危机（为何需要新框架）**：经典 Drude 模型无法解释①金属电子比热极小 ②超导 ③绝缘体存在 → 需要 **量子 + 统计的能带论**
- **新危机**：强关联电子体系（高温超导、莫特绝缘体、重费米子）**超出单电子能带图像**，需要多体场论
- **后续去向**：凝聚态实验（**Cavendish**）→ 新材料；多体理论 → 量子场论方法；拓扑物态 → **拓扑量子计算**

---

## 🏭 理论联系实际：5 个现代应用

1. **半导体芯片**：能带工程（Si, GaN, SiC）是所有 CMOS、功率器件的根基。
2. **超导磁体**：MRI（3 T）、粒子加速器（LHC 8 T）、可控核聚变（ITER）都依赖 NbTi/Nb₃Sn 超导线材。
3. **LED / 激光 / 光伏**：直接带隙半导体（GaAs、GaN）把电变成光，或把光变成电。
4. **硬盘与自旋电子学**：巨磁阻（GMR，2007 诺奖）让硬盘容量爆炸；自旋阀、MRAM 是量子自旋的工程化。
5. **二维材料**：石墨烯（2010 诺奖）、过渡金属硫族化物（TMD）、魔角石墨烯——下一代电子学候选。

---

## 🔬 最新研究前沿（2024-2026）

1. **分数量子反常霍尔效应（FQAHE）**：2024 在 moiré 石墨烯和半导体异质结中实现了**无需外加磁场**的分数量子霍尔态（*Nature*, 2024，华盛顿大学、MIT、剑桥等多组），是拓扑量子计算的潜在平台。
2. **镍基超导**：2024–2025 镍酸盐（如 La₃Ni₂O₇）薄膜在高压下超导，挑战铜氧化物对高温超导的垄断，重燃配对机制争论。
3. **Kagome 金属**：2024 AV₃Sb₅ 类材料中观察到电荷密度波、手性反常、非常规超导，是关联拓扑前沿。
4. **拓扑超导与 Majorana**：2024 拓扑超导候选体系（FeTe₀.₅Se₀.₅、工程异质结）持续推进，瞄准容错拓扑量子比特。
5. **Cavendish 量子材料**：剑桥 Suchitra Sebastian 等在非常规超导、关联电子的高压/强场实验（2024），以及二维材料异质结的精确构筑方面持续产出。

---

## 🗺️ 学习 Roadmap（Cambridge Tripos 路径）

| 阶段 | 课程 | 你应当能做到 |
|------|------|------------|
| **Part II** | Solid State Physics | 晶体结构 + 倒格子、能带论、声子、费米面、输运、超导/磁性初步 |
| （前置） | Quantum Mechanics + Statistical Physics | 提供 §量子 + §Fermi 分布的工具 |
| **Part III** | Condensed Matter Field Theory / Topology / Strongly Correlated | BCS 理论、拓扑物态（拓扑不变量、Berry 相）、强关联、量子霍尔效应 |
| （实验） | Cavendish 实验轮转 | 低温/强磁场、扫描探针、角分辨光电子能谱 ARPES |

**知识检查三问**：
1. 为什么金属导电而绝缘体不导？（能带 + 禁带）
2. 为什么超导体的直流电阻严格为零？（Cooper 对 + 能隙）
3. 魔角双层石墨烯为什么会出现超导和绝缘？（moiré 平带 → 关联效应）
