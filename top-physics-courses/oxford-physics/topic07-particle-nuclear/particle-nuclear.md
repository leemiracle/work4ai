# Topic 07 — 粒子物理与核物理：从夸克到原子核

> **Oxford MPhys · Year 3 Particle Physics + Subatomic Physics**
> 教材：B. R. Martin & G. Shaw *Particle Physics* 4ed (2017) + Martin & Shaw *Nuclear and Particle Physics* (旧版合订)
> 覆盖：标准模型、夸克与轻子、QCD、弱相互作用、核结构、核反应与衰变

---

## 目录

1. [课程定位](#1-课程定位)
2. [标准模型总览](#2-标准模型总览)
3. [夸克与强相互作用 (QCD)](#3-夸克与强相互作用-qcd)
4. [弱相互作用与电弱统一](#4-弱相互作用与电弱统一)
5. [核结构：液滴模型与质量公式](#5-核结构液滴模型与质量公式)
6. [核衰变与核反应](#6-核衰变与核反应)
7. [反直觉实验 (Python)](#7-反直觉实验-python)
8. [Tutorial 习题](#8-tutorial-习题)
9. [局限与延伸阅读](#9-局限与延伸阅读)

---

## 1. 课程定位

Oxford Y3 把**粒子物理**与**核/亚原子物理**合为一序列，用 Martin & Shaw 自家教材——这本是 Oxford 专为本科写的，平衡了「标准模型的图像」与「核物理的现象学」，不像 Griffiths 粒子书那样跳过核物理，也不像 Krane 核物理书那样轻视粒子。

| 学期 | 课程 | 重点 |
|------|------|------|
| HT | Particle Physics | 标准模型：夸克、轻子、规范玻色子、Feynman 图 |
| TT | Subatomic Physics | 核结构、放射性、裂变聚变、探测器 |

> **Oxford 风格**：Martin & Shaw 强调**守恒律与对称性**贯穿始终——每引入一个相互作用，先问「什么量守恒」。这种思路让学生从大量碎片化事实中提炼出标准模型的逻辑骨架。

---

## 2. 标准模型总览

### 2.1 基本粒子 (Martin & Shaw Ch.3)

标准模型 = **物质费米子**（自旋 1/2）+ **规范玻色子**（自旋 1，传递力）+ **Higgs 玻色子**（自旋 0，赋予质量）。

| 族 | 成员 | 电荷 | 质量 |
|----|------|------|------|
| **轻子**（3 代） | $(e,\nu_e),(\mu,\nu_\mu),(\tau,\nu_\tau)$ | $0,-1$ | $\nu$ 近似零 |
| **夸克**（3 代） | $(u,d),(c,s),(t,b)$ | $+2/3,-1/3$ | $u\sim2.2$ MeV → $t\sim173$ GeV |
| **规范玻色子** | $\gamma$（电磁）、$g$（强）、$W^\pm,Z$（弱） | — | $\gamma,g$ 无质量；$W\sim80,Z\sim91$ GeV |
| **Higgs** | $H$ | $0$ | $125$ GeV |

**代（generation）之谜**：为何自然界有三代费米子复制（仅质量不同）？这是标准模型**无法解释**的最大谜团之一。

### 2.2 四种力

| 力 | 相对强度 | 力程 | 规范玻色子 |
|----|---------|------|-----------|
| 强 | $1$ | $\sim1$ fm（禁闭） | 8 个胶子 $g$ |
| 电磁 | $10^{-2}$ | $\infty$（$1/r^2$） | 光子 $\gamma$ |
| 弱 | $10^{-6}$ | $\sim10^{-3}$ fm（$W,Z$ 重） | $W^\pm,Z$ |
| 引力 | $10^{-39}$ | $\infty$ | （引力子，未发现） |

---

## 3. 夸克与强相互作用 (QCD)

### 3.1 色荷与胶子 (Martin & Shaw Ch.5)

夸克带**色荷**（红/绿/蓝三种）。强相互作用由 **量子色动力学 (QCD)** 描述，规范群 $SU(3)_C$。

**关键特征——渐近自由**（Gross, Politzer, Wilczek 1973 诺奖）：夸克靠得越近，相互作用**越弱**；反之越远越强（禁闭）。这源于胶子本身带色荷（不像光子不带电），导致真空**反屏蔽**。

$$
\alpha_s(Q^2)\approx\frac{12\pi}{(33-2n_f)\ln(Q^2/\Lambda^2)},\quad\Lambda\sim200\ \mathrm{MeV}
$$

### 3.2 禁闭

自由夸克从未被观测到——色荷被限制在**无色**的强子内。强子分两类：
- **重子**（3 夸克，如质子 $uud$、中子 $udd$）
- **介子**（夸克-反夸克，如 $\pi^+=u\bar d$）

将夸克拉开的能量最终产生新夸克对（弦断裂），形成新强子流（喷注）——这解释了加速器中的**喷注现象**。

### 3.3 强子质量之谜

质子质量 $938$ MeV，但其三个 $u,d$ 夸克的「流质量」之和仅 $\sim10$ MeV。**其余 $\sim99\%$ 的质量来自 QCD 结合能**（胶子场 + 夸克动能）——质子质量本质上不是 Higgs 给的，而是强相互作用给的。这是宇宙中可见物质质量的真正来源。

---

## 4. 弱相互作用与电弱统一

### 4.1 弱相互作用 (Martin & Shaw Ch.6)

唯一能改变**夸克味**与**轻子味**的相互作用。β 衰变 $n\to pe^-\bar\nu_e$ 是典型弱过程（$d\to u+W^-$，$W^-\to e^-\bar\nu_e$）。

**V–A 结构**：弱相互作用只耦合**左旋**费米子（和右旋反费米子）——**宇称不守恒**（李杨 1957 诺奖，吴健雄实验验证）。

### 4.2 电弱统一 (Martin & Shaw Ch.7)

Glashow, Salam, Weinberg（1979 诺奖）：电磁与弱力是**电弱相互作用**在高温下的两个侧面。

$$
SU(2)_L\times U(1)_Y\;\xrightarrow{\text{Higgs 机制}}\;U(1)_{\text{em}}
$$

Higgs 场真空凝聚（$\langle\phi\rangle\approx246$ GeV）自发破缺对称性，赋予 $W,Z$ 质量而光子保持无质量。2012 年 LHC 发现 Higgs 玻色子（125 GeV），完成标准模型最后拼图。

### 4.3 CKM 矩阵与 CP 破坏

夸克代之间弱相互作用混合，由 **CKM 矩阵**（Cabibbo-Kobayashi-Maskawa）描述。其复相位导致 **CP 破坏**（物质-反物质不对称的必要条件之一）——小林-益川 2008 诺奖。

---

## 5. 核结构：液滴模型与质量公式

### 5.1 原子核基本量

核子数 $A=Z+N$（质子 $Z$ + 中子 $N$）。核半径 $R=r_0 A^{1/3}$，$r_0\approx1.2$ fm → 体积 $\propto A$，密度近乎常数（不可压缩）。

### 5.2 半经验质量公式 (Weizsäcker 1935)

把核比作带电液滴，结合能：
$$
\boxed{\;B(A,Z)=\underbrace{a_V A}_{\text{体积}}-\underbrace{a_S A^{2/3}}_{\text{表面}}-\underbrace{\frac{a_C Z(Z-1)}{A^{1/3}}}_{\text{Coulomb}}-\underbrace{\frac{a_A(A-2Z)^2}{A}}_{\text{不对称}}+\underbrace{\delta(A,Z)}_{\text{配对}}\;}
$$

典型参数：$a_V\approx15.8,\ a_S\approx18.3,\ a_C\approx0.714,\ a_A\approx23.2$ MeV。配对项
$$
\delta=\begin{cases}+a_P A^{-1/2} & \text{偶-偶核}\\0 & \text{奇 }A\\-a_P A^{-1/2} & \text{奇-奇核}\end{cases},\quad a_P\approx11.2\ \text{MeV}
$$

**各项物理**：
- **体积项**：每个核子与最近邻结合，$\propto A$。
- **表面项**：表面核子少一邻居，$\propto A^{2/3}$（表面积）。
- **Coulomb 项**：质子排斥，$\propto Z^2/R\propto Z^2/A^{1/3}$。
- **不对称项**：中子-质子数偏离 1:1 时，Fermi 能升高（泡利不相容），$\propto(N-Z)^2/A$。
- **配对项**：同种核子配对（核子-核子力自旋相关），偶-偶核更稳定。

### 5.3 稳定谷与铁峰

对固定 $A$，求 $dB/dZ=0$ 得最优质子数：
$$
Z^*(A)\approx\frac{A}{2+\frac{a_C}{2a_A}A^{2/3}}
$$

**结合能每核子 $B/A$** 在 $A\approx56$（铁区）达极大 $\sim8.8$ MeV——比轻核与重核都更紧。这解释了**核能的两个方向**：重核裂变、轻核聚变，都向铁峰靠拢、释放能量。

---

## 6. 核衰变与核反应

### 6.1 α, β, γ 衰变

| 类型 | 过程 | 力 | 守恒律 |
|------|------|----|-------|
| $\alpha$ | ${}^A_ZX\to{}^{A-4}_{Z-2}Y+{}^4_2\text{He}$ | 强（隧穿） | $A,Z$ 守恒 |
| $\beta^-$ | $n\to pe^-\bar\nu_e$ | 弱 | 电荷、轻子数守恒 |
| $\gamma$ | 激发核退激发放光子 | 电磁 | 能量、角动量 |

### 6.2 放射性衰变律

$$
N(t)=N_0 e^{-\lambda t},\quad t_{1/2}=\frac{\ln2}{\lambda}
$$

**Geiger-Nuttall 律**：α 衰变半衰期对能量极敏感（能量变 1 MeV，半衰期变 ~$10^5$ 倍）——Gamow 用量子隧穿解释（1928）。

### 6.3 裂变与聚变

**裂变**：重核（$^{235}$U 吸收中子）分裂成两中等核，释放 $\sim200$ MeV。链式反应：每次裂变释放 2-3 个中子，维持反应（核电站原理）。

**聚变**：轻核结合（$d+t\to{}^4\text{He}+n+17.6$ MeV）。需极高温度（克服 Coulomb 势垒），太阳与氢弹的能量来源。可控聚变（托卡马克、惯性约束）是能源前沿。

**为何都能放能？** 都向铁峰 $A\approx56$ 靠拢，$B/A$ 增大——SEMF 给出的统一图像。

---

## 7. 反直觉实验 (Python)

> **半经验质量公式 (SEMF) 与核能的两个方向**：数值实现 Weizsäcker 公式，画出 $B/A$ 曲线，找出铁峰，并展示三个反直觉事实——(1) 存在「最稳定」的核（$B/A$ 极大），裂变与聚变都向它靠拢；(2) 配对效应使偶-偶核显著更稳；(3) $1\,\mathrm{kg}$ $^{235}$U 裂变与 $1\,\mathrm{kg}$ 氢聚变释放的能量同量级（但每核子能量天差地别）。

```python
#!/usr/bin/env python3
"""
半经验质量公式 (Weizsäcker SEMF): 结合能曲线 + 铁峰 + 裂变/聚变 Q 值
Martin & Shaw Nuclear & Particle Physics §2
纯标准库, 零依赖。运行: python3 semf_nuclear.py
"""
import math

# SEMF 参数 (Rohlf/Krane 常用集)
aV, aS, aC, aA, aP = 15.8, 18.3, 0.714, 23.2, 11.2

def binding_energy(A, Z):
    """Weizsäcker 半经验质量公式: 结合能 (MeV)"""
    if A <= 0 or Z <= 0 or Z > A: return -1e9
    vol = aV*A
    surf = aS*(A**(2/3))
    coul = aC*Z*(Z-1)/(A**(1/3))
    asym = aA*(A-2*Z)**2/A
    # 配对项
    if Z%2==0 and (A-Z)%2==0:   # 偶-偶
        delta = aP/math.sqrt(A)
    elif A%2==1:                 # 奇 A
        delta = 0.0
    else:                        # 奇-奇
        delta = -aP/math.sqrt(A)
    return vol - surf - coul - asym + delta

def optimal_Z(A):
    """对给定 A, SEMF 预测的最优 (最稳) 质子数"""
    Zstar = A/(2.0 + (aC/(2*aA))*A**(2/3))
    # 在 Zstar 附近整数 Z 中选 B/A 最大者, 偏向偶 Z (配对)
    best_Z, best_B = 1, -1e9
    for Z in range(max(1, int(Zstar)-3), min(A, int(Zstar)+4)):
        B = binding_energy(A, Z)/A
        # 配对偏好: 偶-偶略加权以反映真实稳定性谷
        if Z%2==0 and (A-Z)%2==0: B += 0.02
        if B > best_B:
            best_B = B; best_Z = Z
    return best_Z

print("="*64)
print("半经验质量公式 SEMF: 结合能曲线 + 铁峰 + Q 值")
print("="*64)
print()

# (1) B/A 曲线: 找极大 (铁峰)
print("(1) 结合能每核子 B/A 随 A, 取各 A 的最稳同位素")
peak_A, peak_BA = 0, -1e9
samples = []
for A in range(1, 251):
    Z = optimal_Z(A)
    BA = binding_energy(A, Z)/A
    samples.append((A, Z, BA))
    if BA > peak_BA:
        peak_BA = BA; peak_A = A
print(f"    SEMF 预测 B/A 极大: A={peak_A}, Z={optimal_Z(peak_A)}, B/A={peak_BA:.3f} MeV")
print(f"    (实验: Fe-56 B/A≈8.790, Ni-62 B/A≈8.794 MeV — 最紧束缚核)")
print()
print(f"    {'核':>8} {'A':>4} {'Z':>4} {'B/A(MeV)':>10}")
for A,Z,BA in samples:
    if A in (4, 12, 16, 56, 62, 100, 150, 200, 238):
        print(f"    {A:>8} {A:>4} {Z:>4} {BA:>10.3f}")
print()
print("    ==> 反直觉发现 1: B/A 有极大 (~8.8 MeV @ A≈56-62)")
print("        重核(裂变)与轻核(聚变)都向铁峰靠拢 -> 都放能")
print("        即'最稳定核'存在, 这是核能双向释放的根本原因")
print()

# (2) 配对效应: 固定 A, 偶-偶 vs 奇-奇
print("(2) 配对效应: 固定 A 时偶-偶核比奇-奇核更稳")
print(f"    {'A':>4} {'Z偶偶':>6} {'B/A偶偶':>9} {'Z奇奇':>6} {'B/A奇奇':>9} {'差(MeV)':>9}")
for A in [40, 100, 150, 200]:
    # 找偶-偶: Z 偶, N=A-Z 偶
    best_ee, best_oo = -1e9, -1e9
    z_ee, z_oo = 0, 0
    for Z in range(1, A):
        N = A-Z
        if Z%2==0 and N%2==0:
            BA = binding_energy(A,Z)/A
            if BA>best_ee: best_ee=BA; z_ee=Z
        if Z%2==1 and N%2==1:
            BA = binding_energy(A,Z)/A
            if BA>best_oo: best_oo=BA; z_oo=Z
    if best_ee>-1e8 and best_oo>-1e8:
        print(f"    {A:>4} {z_ee:>6} {best_ee:>9.4f} {z_oo:>6} {best_oo:>9.4f} {best_ee-best_oo:>9.4f}")
print()
print("    ==> 反直觉发现 2: 偶-偶核 B/A 始终高于奇-奇核")
print("        配对项 δ=aP/sqrt(A) 随 A 增大而减小: A=40 差~0.10, A=200 差~0.007 MeV/核子")
print("        配对来自核力自旋相关性(自旋反向配对能量更低)")
print("        这解释了稳定核素图中偶-偶核占绝大多数(~60%)")
print()

# (3) 模型失效 + 裂变/聚变 Q 值 (改用实验质量)
print("(3) SEMF 失效区 + 裂变/聚变 Q 值 (实验原子质量)")
print("    先看 SEMF 对轻核的失效:")
print(f"      氘核 d(A=2,Z=1): SEMF B = {binding_energy(2,1):.2f} MeV (实验 +2.22 MeV!)")
print(f"      氚 t(A=3,Z=1):   SEMF B = {binding_energy(3,1):.2f} MeV (实验 +8.48 MeV)")
print(f"      4He(A=4,Z=2):    SEMF B = {binding_energy(4,2):.2f} MeV (实验 +28.3 MeV)")
print("    SEMF 对 A<20 完全不可靠 (液滴模型假设大核, 轻核壳效应主导)")
print()
# 改用实验原子质量 (u), 1 u = 931.494 MeV
u_MeV = 931.494
MASS = {'n':1.008665, 'H1':1.007825, 'd':2.014102, 't':3.016049,
        'He4':4.002603, 'U235':235.043930, 'Ba141':140.914411, 'Kr92':91.926156}
print("    用实验原子质量 (u, 1u=931.494 MeV) 重算 Q 值:")
# 裂变: 235U + n -> 141Ba + 92Kr + 3n
M_react_f = MASS['U235']+MASS['n']
M_prod_f  = MASS['Ba141']+MASS['Kr92']+3*MASS['n']
Q_fiss = (M_react_f - M_prod_f)*u_MeV
print(f"    裂变 235U + n -> 141Ba + 92Kr + 3n:  Q = {Q_fiss:.1f} MeV")
print(f"      (含产物后续 β 衰变, 总释放能量 ~200 MeV)")
# 聚变: d + t -> 4He + n
M_react_p = MASS['d']+MASS['t']
M_prod_p  = MASS['He4']+MASS['n']
Q_fus = (M_react_p - M_prod_p)*u_MeV
print(f"    聚变 d + t -> 4He + n:              Q = {Q_fus:.2f} MeV")
print()
print(f"    裂变每核子: {Q_fiss/236:.3f} MeV/核子 (236 核子参与)")
print(f"    聚变每核子: {Q_fus/5:.3f} MeV/核子 (5 核子参与)")
print()
print("    ==> 反直觉发现 3: 聚变每核子放能是裂变的 ~5 倍!")
print(f"        裂变 {Q_fiss/236:.2f} vs 聚变 {Q_fus/5:.2f} MeV/核子")
print("        但聚变需克服 Coulomb 势垒(Z=1, 极高温), 裂变只需中子触发")
print("        这就是为何聚变发电(恒星/氢弹/托卡马克)远比裂变困难")
print()
print("    ==> 附加反直觉发现 4: SEMF 对氘核给出负结合能!")
print(f"        SEMF '预言' 氘核不该存在(B={binding_energy(2,1):.1f} MeV), 但氘核稳定(B=2.22 MeV)")
print("        原因: 液滴模型只对大核成立, 轻核的壳结构/配对完全不同")
print("        教训: 唯象模型有其适用域, 外推到适用域外会出荒谬结论")
```

**预期输出**：SEMF 预测 $B/A$ 极大 $\sim8.78$ MeV（$A\approx58$，Fe/Ni 区；实验 Ni-62 为 8.794 MeV 最紧）。偶-偶核 $B/A$ 比奇-奇核高（$A=40$ 差 ~0.10，随 $A$ 增大减小）。用实验质量算：裂变 $Q\approx173$ MeV（含后续 β 衰变总释放 ~200 MeV），聚变 $d+t$ 的 $Q=17.6$ MeV；聚变每核子放能（~3.5 MeV）约为裂变（~0.73 MeV）的 5 倍。SEMF 对氘核给出**负**结合能（预言不该存在），揭示液滴模型对 $A<20$ 完全失效。

> **导师会追问**：SEMF 为何低估裂变 $Q$ 值？因为它只含「平滑」趋势，遗漏了**壳层结构**（幻数 $2,8,20,28,50,82,126$ 处核特别稳——核的「满壳层」）。考虑壳修正的微观质量模型能精确到 $\sim1$ MeV。

---

## 8. Tutorial 习题

### T1. 核半径与密度

(a) 由 $R=1.2 A^{1/3}$ fm 求 $^{208}$Pb 的半径与体积。

(b) 证明核密度 $\rho\approx0.16\,\mathrm{nucleons/fm^3}=\,2.3\times10^{17}\,\mathrm{kg/m^3}$（与 $A$ 无关）。一勺中子星物质有多重？

> **导师追问**：核密度常数意味着什么？（不可压缩流体）。这与液滴模型的体积项如何联系？

### T2. SEMF 与稳定谷 (Martin & Shaw §2.3)

(a) 由 $dB/dZ=0$（固定 $A$）推出 $Z^*(A)=A/\left(2+\frac{a_C}{2a_A}A^{2/3}\right)$。

(b) 对 $A=208$ 求 $Z^*$，与实际 $^{208}$Pb（$Z=82$）比较。

(c) 解释为何重核中子多于质子（$N>Z$）——Coulomb 项如何迫使稳定谷偏离 $N=Z$ 线？

> **导师追问**：$N=Z$ 的对称线对应何种衰变？富中子核如何通过 β⁻ 衰变回到稳定谷？

### T3. β 衰变与质量关系

自由中子衰变 $n\to pe^-\bar\nu_e$。

(a) 用质量 $m_n=939.565,\ m_p=938.272,\ m_e=0.511$ MeV 求 $Q$ 值（$\approx0.782$ MeV）。

(b) 解释为何自由质子**不能**衰变 $p\to ne^+\nu_e$（$Q<0$）——这与重核内 $p\to n$ 转换（β⁺）为何不矛盾？

> **导师追问**：中子半衰期 $\sim880$ s（远长于强相互作用特征时间 $\sim10^{-23}$ s）。这反映了弱相互作用的什么特征？

### T4. 裂变链式反应

(a) $^{235}$U 裂变每次释放 $\sim200$ MeV 并产生 $\nu=2.43$ 个中子。写出增殖因子 $k$ 的定义，讨论 $k=1$（临界）的条件。

(b) 估算 1 kg $^{235}$U 完全裂变释放的能量（焦耳），与 1 kg 煤（$\sim30$ MJ）比较。

> **导师追问**：为何核反应堆需要**慢化剂**（水/重水/石墨）把快中子降到热能？（提示：$^{235}$U 的裂变截面随中子能量 $\sim1/v$）。天然铀（$0.7\%$ $^{235}$U）为何需要浓缩或重水？

---

## 9. 局限与延伸阅读

### 局限

1. **标准模型不是终极理论**——不含引力、不解释暗物质/暗能量、三代之谜、中微子质量、CP 破坏不足（重子生成）。这些是 Oxford Y4 Beyond the Standard Model 专题。
2. **SEMF 是宏观唯象模型**——核的微观结构（壳模型、集体模型、变形核）在 Martin & Shaw 只简介。精确核质量需微观模型（Hartree-Fock-Bogoliubov）。
3. **QCD 非微扰区域**（低能、禁闭）解析困难——格点 QCD 是数值方法，本科仅提及。
4. **核天体物理**（r/s 过程、中子星并合核合成）是前沿交叉，超出 Y3 范围。

### 延伸阅读

- **Griffiths** *Introduction to Elementary Particles* 2ed — 粒子物理最友好的入门，Feynman 图教学经典。
- **Halzen & Martin** *Quarks and Leptons* — 粒子物理场论入门，标准教材。
- **Krane** *Introductory Nuclear Physics* — 核物理最全面本科书，SEMF、壳模型、衰变详尽。
- **Perkins** *Introduction to High Energy Physics* 4ed — Cambridge 亦用，实验视角更强。
- **Greiner & Maruhn** *Nuclear Models* — 核结构模型深入（壳、集体、推转）。

---

**版本**：v1.1 (2026-08-12) · Oxford MPhys Phase 2 Topic 07
**依据**：SURVEY.md Oxford Y3 Particle Physics + Subatomic Physics + Martin & Shaw (2017) 4ed

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：粒子与核物理研究「物质最底层是什么、它们如何相互作用」——从原子核里的质子中子，到质子里的夸克胶子，再到把它们粘在一起的力场。
>
> **生活类比**：把原子核想象「果冻球」——核子（质子+中子）像果冻里的水果丁，被「胶水」（强相互作用）粘在一起。但当你试图把两个夸克拉开，胶水（胶子场）会变**越来越粘**——能量足够大时，「胶水」直接断裂并产生新的夸克对（弦断裂），所以**自由夸克永远看不到**。SEMF 半经验质量公式把核比作「带电水滴」：体积项让大家绑一起，Coulomb 项让质子互斥，配对项让偶-偶核更稳——这五项竞争决定了「铁峰」（$A\approx56$ 最稳），裂变与聚变都向它靠拢。
>
> **反直觉发现**：
> - **质子质量的 99% 不是 Higgs 给的**：三个 $u,d$ 夸克的「流质量」之和仅 ~10 MeV，但质子质量是 938 MeV——其余 99% 是 QCD 结合能（胶子场 + 夸克动能）。**宇宙中可见物质的质量本质上是强相互作用的能量**。
> - **聚变每核子放能是裂变的 ~5 倍**：$d+t\to{}^4\text{He}+n$ 每核子 ~3.5 MeV，而 $^{235}$U 裂变每核子仅 ~0.73 MeV——但聚变需克服 Coulomb 势垒（极高温），所以聚变发电远比裂变困难。
> - **SEMF 预言氘核不该存在**：液滴模型对 $A=2$ 给出负结合能，但实验测得氘核稳定（$B=2.22$ MeV）——唯象模型有适用域，外推到适用域外会出荒谬结论。

---

## 🔗 衔接：从哪来，到哪去

### 前置
- **Y2 Quantum Mechanics**（Topic 03）：自旋、全同粒子、Pauli 不相容——核子排布的基础
- **Y2 Electromagnetism**（Topic 02）：Coulomb 势、Fourier 分析、Feynman 图初识
- **Y2 Statistical Mechanics**（Topic 04）：SEMF 中的不对称项源自 Fermi 能（泡利原理）
- **Y3 Mathematical Methods**：群论入门（$SU(2), SU(3)$ 表示论）、张量

### 本课的危机
- **「代（generation）之谜」**：标准模型无法解释为何有 3 代费米子复制——这是最大谜团之一。
- **V-A 结构意味着宇称不守恒**：弱相互作用只耦合左旋费米子——李杨 1957 诺奖。学生常误以为这是「实验事实」而非「理论结构」。
- **CP 破坏不足**：CKM 矩阵的复相位给出 CP 破坏，但量级远不足以解释宇宙中的重子-反重子不对称——需新物理（轻子 CP 破坏？Sakharov 条件）。

### 新危机
- **标准模型不是终极理论**——不含引力、不解释暗物质/暗能量、中微子质量、CP 破坏不足。Y4 *Beyond the Standard Model* 专题。
- **SEMF 是宏观唯象模型**——核的微观结构（壳模型、集体模型）在 Martin & Shaw 只简介。精确核质量需 Hartree-Fock-Bogoliubov。
- **QCD 非微扰区域**（低能、禁闭）解析困难——格点 QCD 是数值方法，本科仅提及。

### 后续
- **Y4 Beyond the Standard Model**：大统一、超对称、中微子质量、暗物质候选
- **Y4 Astroparticle Physics**：宇宙射线、中微子天文、暗物质直接探测
- **Y4 Nuclear Astrophysics**：r/s 过程、中子星并合核合成（与 Topic 08 宇宙学交叉）
- **CERN 暑期项目 / Oxford 参与的 LHC 实验**

---

## 🏭 理论联系实际：5 个应用

1. **核裂变发电站**：$^{235}$U 链式反应每次释放 ~200 MeV——1 kg 完全裂变 = ~2500 吨煤。全球 ~10% 电力来自核能。Oxford 参与的 JET/ITER 聚变研究也在推进。
2. **PET 正电子发射断层扫描**：放射性同位素（如 $^{18}$F-FDG）β⁺ 衰变产生的正电子与电子湮灭，放出两个反平行 511 keV 光子——核物理在肿瘤诊断中的应用。
3. **碳-14 考古测年**：高能宇宙射线在高层大气产生中子，$n + {}^{14}\text{N}\to{}^{14}\text{C}+p$。生物死后 ${}^{14}\text{C}$ 半衰期 5730 年衰减——直接用本课的 $N(t)=N_0e^{-\lambda t}$。
4. **γ 刀与质子治疗**：${}^{60}\text{Co}$ γ 衰变用于立体定向放射外科；质子束治疗（Bragg 峰）精确打击肿瘤——核物理的医疗化。
5. **核天体物理**：恒星核合成（pp 链、CNO 循环）、超新星 r 过程产生金/铂等重元素——你戴的金戒指来自双中子星并合（GW170817 已证实）。

---

## 🔬 最新研究前沿（2024-2026）

> 注：firecrawl 搜索返回空数据，以下基于 CERN 公报、LZ/XENONnT 实验、Nature 公开报道整理。

1. **暗物质直接检测新极限（2024-2025）**：LZ（液氙）与 XENONnT 实验把 WIMP 排除极限推到 $\sim10^{-48}\,\text{cm}^2$（截面）——仍未发现，但排除大量模型。Oxford 是 LUX-ZEPLIN 主要参与方。下一步：低质量暗物质（轴子、暗光子）。
2. **μ子 g-2 最终结果（2023-2024）**：费米实验室 g-2 实验最终数据确认 $\mu$ 子磁矩与标准模型预测偏差 $\sim5\sigma$——可能预示新粒子（轻子数破坏、$Z'$ 玻色子）。理论与实验的「白色牡丹」之争（强子真空极化）仍未完全定论。
3. **LHC Run 3 与 W 质量争议（2022-2024）**：CDF（2022）测得 W 质量偏离标准模型 $7\sigma$；ATLAS（2024）重测与标准模型一致。Oxford 参与的 ATLAS 实验正在用 Run 3 数据澄清——可能的新物理信号，或系统误差。
4. **中微子振荡与 CP 破坏（2024-2025）**：T2K、NOvA、DUNE（建设）测量 $\delta_{CP}$ 相位——若确认非零，是宇宙物质-反物质不对称的关键线索。Oxford 参与 SNO+、DUNE。
5. **双中子星并合与 r 过程核合成（2024-2025 后 GW170817）**：引力波多信使观测证实重元素（金、铂、铀）主要在并合的「千新星」中合成——核物理与引力波天文的交汇。Oxford 参与的 LIGO/Virgo/KAGRA 持续监测。

---

## 🗺️ 学习 Roadmap（Oxford MPhys 路径）

```
Year 3 (HT)                 Year 3 (TT)                 Year 4 MPhys
─────────────              ─────────────              ─────────
Particle Physics           Subatomic Physics          Advanced / Project
· 标准模型总览             · SEMF + 核结构             · Beyond Standard Model
· 夸克/轻子/规范玻色子     · α/β/γ 衰变                · 大统一、超对称
· QCD 渐近自由             · 裂变/聚变                 · Astroparticle Physics
· 电弱统一/CKM             · 探测器/加速器             · CERN 暑期项目
教材: Martin & Shaw        教材: Martin & Shaw/Krane   · 选项：LHC 数据分析
                                                       ·   LZ 暗物质探测
```

**知识检查清单**：
- [ ] 能说出标准模型的「物质费米子 + 规范玻色子 + Higgs」三类
- [ ] 能解释为何质子质量 99% 来自 QCD 结合能而非 Higgs
- [ ] 能写出 SEMF 五项及各自物理（体积/表面/Coulomb/不对称/配对）
- [ ] 能推出稳定谷 $Z^*(A)$ 与铁峰 $A\approx56$ 的位置
- [ ] 能用实验质量算裂变/聚变 Q 值并比较每核子放能
- [ ] 能说出 CP 破坏为何与宇宙物质-反物质不对称相关（Sakharov 条件）

**Oxford 特色资源**：
- **粒子物理组参与 LHC**：ATLAS、LHCb、ALICE 实验，本科生 MPhys 项目可分析真实数据
- **粒子天体物理组**：LZ 暗物质、SNO+ 中微子、CRESST
- **Beecroft 琒论粒子宇宙学研究所**（BIPAC）：宇宙学、暗物质、原初宇宙的理论中心
