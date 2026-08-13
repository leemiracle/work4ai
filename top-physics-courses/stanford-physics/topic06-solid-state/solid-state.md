# Stanford 物理系 Phase 2 · 主题 6：固体物理与凝聚态

> **课程谱系**：PHYS 195 (固体物理导论) → PHYS 230 (固体物理) → PHYS 240 (凝聚态) → PHYS 360 (凝聚态高级)
>
> **教材阶梯**：Kittel《Introduction to Solid State Physics》9ed → Ashcroft & Mermin《Solid State Physics》→ Chaikin & Lubensky《Principles of Condensed Matter Physics》
>
> **Stanford 特色**：Stanford 凝聚态物理群从 Shockley 的半导体革命到 Moore 基金会量子材料计划。SLAC/LCLS 的超快 X 射线衍射直接探测晶格动力学，Stanford 纳米加工设施（SNF）可制备原子级材料。凝聚态是物理学最大的分支，Stanford 在拓扑材料、量子计算、超导领域全球领先

---

## 目录

1. [晶体结构](#1-晶体结构)
2. [倒格子与衍射](#2-倒格子与衍射)
3. [声子与晶格热学](#3-声子与晶格热学)
4. [自由电子模型](#4-自由电子模型)
5. [能带理论](#5-能带理论)
6. [半导体物理](#6-半导体物理)
7. [超导电性](#7-超导电性)
8. [Stanford 关联](#8-stanford-关联)
9. [习题与解答](#9-习题与解答)
10. [代码实验](#10-代码实验)
11. [局限与延伸](#11-局限与延伸)

---

## 1. 晶体结构

### 1.1 直觉

晶体的美在于**平移对称性**——把整个晶体平移一个格矢量 $\mathbf{R}$，看起来一模一样。这种离散对称性深刻地决定了电子和声子的行为。Kittel 第 1 章的核心洞察。

### 1.2 Bravais 格子

三维空间有 **14 种 Bravais 格子**，分属 7 大晶系。基矢 $\mathbf{a}_1, \mathbf{a}_2, \mathbf{a}_3$ 生成格矢量：

$$\mathbf{R} = n_1 \mathbf{a}_1 + n_2 \mathbf{a}_2 + n_3 \mathbf{a}_3, \quad n_i \in \mathbb{Z}$$

常见的：简单立方（SC）、体心立方（BCC）、面心立方（FCC）。

### 1.3 原胞与 Wigner-Seitz 胞

**原胞**是体积最小的重复单元。**Wigner-Seitz 胞**的构造：以某格点为中心，到所有相邻格点连线的中垂面围成的区域。它自然反映了格点对称性。

FCC 的 Wigner-Seitz 胞 = 截角八面体（十四面体），这是第一布里渊区的形状。

### 1.4 晶面与 Miller 指数

用 Miller 指数 $(hkl)$ 标记晶面：截距为 $a_1/h, a_2/k, a_3/l$。密勒指数大的面间距小，原子密度低。

面间距公式（立方晶系）：

$$\boxed{d_{hkl} = \frac{a}{\sqrt{h^2 + k^2 + l^2}}}$$

---

## 2. 倒格子与衍射

### 2.1 倒格子

倒格子基矢：

$$\mathbf{b}_1 = 2\pi \frac{\mathbf{a}_2 \times \mathbf{a}_3}{\mathbf{a}_1 \cdot (\mathbf{a}_2 \times \mathbf{a}_3)}, \quad \text{cyclic}$$

满足 $\mathbf{a}_i \cdot \mathbf{b}_j = 2\pi \delta_{ij}$。

倒格矢 $\mathbf{G} = m_1\mathbf{b}_1 + m_2\mathbf{b}_2 + m_3\mathbf{b}_3$。

### 2.2 衍射条件与 Bragg 定律

波矢为 $\mathbf{k}$ 的 X 射线被晶体衍射，衍射条件（Laue 条件）：

$$\boxed{\Delta \mathbf{k} = \mathbf{k}' - \mathbf{k} = \mathbf{G}}$$

等价于 Bragg 定律：

$$2d\sin\theta = n\lambda$$

SLAC 的 SSRL（同步辐射光源）正是利用这一原理进行晶体结构分析。

### 2.3 结构因子

对基元中有多个原子的晶体，散射振幅包含**结构因子**：

$$F_{hkl} = \sum_j f_j \exp[i\mathbf{G} \cdot \mathbf{r}_j]$$

其中 $f_j$ 是第 $j$ 个原子的原子散射因子。$F_{hkl} = 0$ 时该衍射峰消失（系统消光）。

**反直觉发现**：FCC 格的 $(100)$ 衍射峰被消光！因为 FCC 可视为简单立方+4 原子基元，结构因子恰好为零。

---

## 3. 声子与晶格热学

### 3.1 一维单原子链

弹簧常数为 $K$、质量为 $M$ 的原子链。运动方程：

$$M\ddot{u}_n = K(u_{n+1} + u_{n-1} - 2u_n)$$

行波解 $u_n = u e^{i(qna - \omega t)}$ 代入，得**色散关系**：

$$\boxed{\omega(q) = 2\sqrt{\frac{K}{M}} \left|\sin\frac{qa}{2}\right|}$$

### 3.2 Debye 模型

将晶体视为连续弹性介质，声子色散 $\omega = v_s q$（线性），截止波矢 $q_D$ 由总模式数 = $3N$ 确定。

Debye 频率 $\omega_D$，Debye 温度 $\Theta_D = \hbar\omega_D/k_B$。

**Debye $T^3$ 定律**：低温热容

$$C_V \approx \frac{12\pi^4}{5} Nk_B \left(\frac{T}{\Theta_D}\right)^3 \quad (T \ll \Theta_D)$$

### 3.3 Einstein 模型 vs Debye 模型

| 模型 | 色散 | 高温 $C_V$ | 低温 $C_V$ |
|------|------|-----------|-----------|
| Einstein | $\omega = \omega_0$（常数） | $3Nk_B$ | $\sim e^{-\Theta_E/T}$ ❌ |
| Debye | $\omega = v_s q$（线性） | $3Nk_B$ | $\sim T^3$ ✅ |

Debye 赢在正确预言了低温 $T^3$ 律。

---

## 4. 自由电子模型

### 4.1 Drude 模型（经典）

电子在晶格中自由运动，碰撞提供阻力。电导率：

$$\sigma = \frac{ne^2\tau}{m}$$

其中 $\tau$ 是弛豫时间。Drude 模型正确预言了 Wiedemann-Franz 定律的**存在**，但数值差 2 倍。

### 4.2 Sommerfeld 模型（量子）

电子服从 Fermi-Dirac 统计，填满到 Fermi 能 $E_F$。态密度（3D 自由电子气）：

$$g(E) = \frac{V}{2\pi^2}\left(\frac{2m}{\hbar^2}\right)^{3/2} \sqrt{E}$$

Fermi 能：

$$\boxed{E_F = \frac{\hbar^2}{2m}\left(3\pi^2 n\right)^{2/3}}$$

典型金属 $E_F \sim 5$–$10$ eV，对应 Fermi 温度 $T_F = E_F/k_B \sim 50{,}000$ K。

### 4.3 电子热容

只有 Fermi 面附近的电子可参与热激发：

$$C_V^{el} = \frac{\pi^2}{3} g(E_F) k_B^2 T = \frac{\pi^2}{2} Nk_B \frac{T}{T_F}$$

室温下 $C_V^{el} \ll 3Nk_B$（经典值），完美解释了 Drude 模型的困惑。

---

## 5. 能带理论

### 5.1 直觉

周期势 $V(\mathbf{r}) = V(\mathbf{r}+\mathbf{R})$ 中的电子既非完全自由，也非束缚在原子周围。Bloch 定理给出了精确的数学形式：电子波函数是平面波被周期函数调制的产物。

### 5.2 Bloch 定理

周期势中电子波函数的形式为：

$$\boxed{\psi_{\mathbf{k}}(\mathbf{r}) = e^{i\mathbf{k}\cdot\mathbf{r}} u_{\mathbf{k}}(\mathbf{r}), \quad u_{\mathbf{k}}(\mathbf{r}+\mathbf{R}) = u_{\mathbf{k}}(\mathbf{r})}$$

### 5.3 近自由电子模型与能隙

在布里渊区边界 $k = \pm \pi/a$ 处，自由电子的 $k$ 和 $k-G = k - 2\pi/a$ 态简并。周期势的微扰使它们杂化，打开**能隙**：

$$E_\pm = \frac{\hbar^2}{2m}\left(\frac{\pi}{a}\right)^2 \pm |V_G|$$

能隙宽度 $= 2|V_G|$。

### 5.4 紧束缚模型

从原子轨道出发，相邻原子的轨道重叠产生能带：

$$E(k) = E_0 - 2t\cos(ka)$$

其中 $t$ 是跳跃积分（hopping integral）。能带宽度 $= 4|t|$（一维）。

### 5.5 有效质量

能带底部电子的行为像一个质量为 $m^*$ 的自由粒子：

$$\boxed{\frac{1}{m^*} = \frac{1}{\hbar^2}\frac{d^2 E}{dk^2}}$$

能带越「平」，有效质量越大。在 GaAs 中 $m^* \approx 0.067 m_e$，远小于自由电子质量。

---

## 6. 半导体物理

### 6.1 能带结构

- **绝缘体**：满带 + 大能隙（$\sim 5$ eV+）
- **半导体**：满带 + 小能隙（$\sim 1$ eV）
- **金属**：半满带

Si 的间接带隙 $E_g = 1.12$ eV；GaAs 的直接带隙 $E_g = 1.42$ eV。

### 6.2 掺杂

n 型（施主，如 P in Si）：多余电子在导带底下方 $E_d \approx 0.05$ eV。

p 型（受主，如 B in Si）：空穴在价带顶上方 $E_a \approx 0.05$ eV。

### 6.3 pn 结

平衡时 Fermi 能级对齐，产生内建电场。加正向偏压时电流指数增长（整流效应）：

$$I = I_0\left(e^{eV/k_BT} - 1\right)$$

这就是 Shockley 的二极管方程——硅谷的种子。

---

## 7. 超导电性

### 7.1 零电阻与 Meissner 效应

超导体的两大标志：(i) 电阻为零，(ii) 完全抗磁性（Meissner 效应，磁场被排出）。

### 7.2 London 方程

$$\frac{\partial \mathbf{J}_s}{\partial t} = \frac{n_s e^2}{m}\mathbf{E}, \quad \nabla \times \mathbf{J}_s = -\frac{n_s e^2}{m}\mathbf{B}$$

第二个方程预言了磁场穿透深度 $\lambda_L$：

$$B(x) = B_0 e^{-x/\lambda_L}, \quad \lambda_L = \sqrt{\frac{m}{\mu_0 n_s e^2}}$$

### 7.3 BCS 理论

Bardeen, Cooper, Schrieffer（1957）。核心思想：电子通过声子交换形成 **Cooper 对**。

Cooper 对结合能（能隙）：

$$\boxed{\Delta(0) = 1.764\, k_B T_c}$$

$T_c$ 是临界温度。Cooper 对是玻色子，凝聚到基态 → 超导。

### 7.4 第二类超导体

磁通量子化：

$$\Phi_0 = \frac{h}{2e} = 2.067 \times 10^{-15}\,\text{Wb}$$

混合态中磁通以 Abrikosov 涡旋格子排列（六角格子）。这是超导磁体和量子计算的基础。

---

## 8. Stanford 关联

| 方向 | Stanford 角色 |
|------|-------------|
| **半导体革命** | Shockley（Stanford 教授）创立肖克利半导体实验室 → 硅谷起源 |
| **SLAC SSRL** | 同步辐射 X 射线衍射晶体结构 |
| **LCLS** | 自由电子激光超快探测声子和电子动力学 |
| **量子材料** | Moore 基金会资助的量子材料生长与表征 |
| **超快科学** | 脉冲激光 + X 射线研究飞秒级晶格动力学 |
| **斯坦福纳米设施 (SNF)** | 原子级材料制备（MBE, ALD） |
| **量子计算** | 超导量子比特（Google/Stanford 合作） |

---

## 9. 习题与解答

### 习题 1（PHYS 195 风格 · Kittel Ch1）

铜是 FCC 结构，晶格常数 $a = 3.61$ Å。求铜的密度和最近邻距离。

<details>
<summary>解答</summary>

FCC 每原胞 4 个原子。原子质量 $M = 63.55$ g/mol。

原胞体积 $V = a^3 = (3.61 \times 10^{-10})^3 = 4.71 \times 10^{-29}$ m$^3$。

密度 $\rho = \frac{4M/N_A}{V} = \frac{4 \times 63.55 \times 10^{-3}/6.022\times10^{23}}{4.71\times10^{-29}}$

$= \frac{4.224\times10^{-25}}{4.71\times10^{-29}} = 8970$ kg/m$^3 = 8.97$ g/cm³。✅（实验值 8.96）

最近邻距离（FCC）$= a/\sqrt{2} = 3.61/1.414 = 2.55$ Å。
</details>

### 习题 2（PHYS 230 风格 · Ashcroft & Mermin Ch4）

推导一维单原子链的色散关系 $\omega(q)$，并讨论 $q \to 0$ 和 $q \to \pi/a$ 的极限。

<details>
<summary>解答</summary>

$M\ddot{u}_n = K(u_{n+1}+u_{n-1}-2u_n)$，代入 $u_n = ue^{i(qna-\omega t)}$：

$-M\omega^2 = K(e^{iqa} + e^{-iqa} - 2) = 2K(\cos qa - 1) = -4K\sin^2(qa/2)$

$$\omega = 2\sqrt{K/M}\,|\sin(qa/2)|$$

- $q \to 0$（长波）：$\sin(qa/2) \approx qa/2$，故 $\omega \approx v_s q$（声速 $v_s = a\sqrt{K/M}$）——**声学声子**线性色散。
- $q \to \pi/a$（布里渊区边界）：$\omega \to 2\sqrt{K/M}$（最大频率），群速 $d\omega/dq \to 0$——**Bragg 反射**使波成为驻波。
</details>

### 习题 3（PHYS 230 自由电子气）

计算钠（FCC，$a = 4.23$ Å，每个 Na 贡献 1 个价电子）的 Fermi 能和 Fermi 温度。

<details>
<summary>解答</summary>

电子密度 $n$：FCC 每原胞 4 原子，每原子 1 电子。

$n = 4/a^3 = 4/(4.23\times10^{-10})^3 = 5.29\times10^{28}$ m$^{-3}$。

$$E_F = \frac{\hbar^2}{2m_e}(3\pi^2 n)^{2/3}$$

$3\pi^2 n = 29.61 \times 5.29\times10^{28} = 1.566\times10^{30}$

$(3\pi^2 n)^{2/3} = (1.566\times10^{30})^{2/3} = 1.343\times10^{20}$ m$^{-2}$

$E_F = \frac{(1.055\times10^{-34})^2}{2\times9.11\times10^{-31}} \times 1.343\times10^{20}$

$= \frac{1.113\times10^{-68}}{1.822\times10^{-30}} \times 1.343\times10^{20} = 6.11\times10^{-19}\times 1.343\times10^{20}/1.822$

$\approx 3.13$ eV

$T_F = E_F/k_B = 3.13\times1.602\times10^{-19}/1.381\times10^{-23} \approx 36{,}300$ K。

与实验值 $E_F = 3.24$ eV, $T_F = 37{,}600$ K 吻合。
</details>

### 习题 4（PHYS 240 BCS）

证明超导能隙在 $T=0$ 时与 $T_c$ 的关系为 $\Delta(0) = 1.764\, k_B T_c$，并解释其物理意义。

<details>
<summary>解答</summary>

BCS 理论给出零温能隙方程：

$$1 = V g(E_F) \int_0^{\hbar\omega_D} \frac{d\xi}{\sqrt{\xi^2 + \Delta^2}} \approx V g(E_F) \ln\frac{2\hbar\omega_D}{\Delta}$$

得 $\Delta(0) = 2\hbar\omega_D\, e^{-1/[V g(E_F)]}$。

$T = T_c$ 时 $\Delta \to 0$，代入有限温度能隙方程：

$$k_B T_c = 1.14\, \hbar\omega_D\, e^{-1/[V g(E_F)]}$$

两式之比：

$$\frac{\Delta(0)}{k_B T_c} = \frac{2}{1.14} = 1.764$$

物理意义：破坏一个 Cooper 对需要能量 $2\Delta$。$T_c$ 时热能 $k_BT_c$ 刚好与能隙竞争，但比值 1.764 反映了 Cooper 对的集体效应（不是单个拆解）。
</details>

---

## 10. 代码实验

### 实验 10.1：一维单原子链色散关系

```python
"""
PHYS 195 实验：声子色散关系
一维单原子链: w(q) = 2*sqrt(K/M) * |sin(qa/2)|
对比 Debye 线性近似
纯标准库，输出 ASCII 图
"""
import math

K_M = 1.0  # K/M 比值（归一化）
a = 1.0    # 格点间距

def omega_exact(q):
    return 2 * math.sqrt(K_M) * abs(math.sin(q * a / 2))

def omega_debye(q):
    """长波近似: w ≈ c*q, c = a*sqrt(K/M)"""
    vs = a * math.sqrt(K_M)
    return vs * abs(q)

# 采样第一布里渊区 -pi/a 到 pi/a
N = 50
qs = [-math.pi/a + i*(2*math.pi/a)/(N-1) for i in range(N)]
qs.sort()

print("=== 一维单原子链声子色散 ===")
print(f"{'q (×π/a)':>10} {'ω_exact':>10} {'ω_Debye':>10} {'误差%':>8}")
for q in qs[::5]:
    we = omega_exact(q)
    wd = omega_debye(q)
    err = abs(we - wd)/max(we, 1e-10) * 100 if abs(q) > 0.01 else 0
    print(f"{q/(math.pi/a):10.3f} {we:10.4f} {wd:10.4f} {err:8.1f}")

# ASCII 图
print("\n色散曲线（* = 精确, . = Debye 近似）：")
height = 20
max_w = 2 * math.sqrt(K_M)
for row in range(height, -1, -1):
    w_target = row * max_w / height
    line = ""
    for q in qs:
        we = omega_exact(q)
        wd = omega_debye(q)
        if abs(we - w_target) < max_w/height/2:
            line += "*"
        elif abs(wd - w_target) < max_w/height/2:
            line += "."
        else:
            line += " "
    print(f"{w_target:4.2f} |{line}")

print("     " + "-" * N)
print("      q: -π/a              0              +π/a")
print("\n反直觉发现：Debye 线性近似在 q→π/a 时严重偏离！")
print("Bragg 反射使声子频率饱和，群速 dω/dq → 0。")
```

### 实验 10.2：Fermi-Dirac 分布与电子热容

```python
"""
PHYS 230 实验：Fermi-Dirac 分布
展示 T=0 到 T>>TF 的分布变化，计算电子热容
纯标准库
"""
import math

def fermi_dirac(E, T, EF, kB=1.0):
    """f(E) = 1/(exp((E-EF)/kBT) + 1)"""
    x = (E - EF) / (kB * T) if T > 1e-10 else (-999 if E > EF else 999)
    if x > 500:
        return 0.0
    elif x < -500:
        return 1.0
    return 1.0 / (math.exp(x) + 1)

EF = 5.0  # Fermi 能 (eV)
kB = 8.617e-5  # eV/K
TF = EF / kB  # ~58000 K

print(f"Fermi 能 EF = {EF:.1f} eV, Fermi 温度 TF = {TF:.0f} K")
print(f"\n{'温度 T (K)':>10} {'kBT (eV)':>10} {'kBT/EF':>10} {'分布尾部':>10}")
for T in [0, 300, 1000, 5000, 10000, 30000, 60000]:
    kB_T = kB * T
    ratio = kB_T / EF
    # EF 以上 1kBT 处的占据概率
    tail = fermi_dirac(EF + kB_T, T, EF) if T > 0 else 0.0
    print(f"{T:10d} {kB_T:10.4f} {ratio:10.5f} {tail:10.4f}")

# 电子热容: Cv = (pi^2/2)*NkB*(T/TF)
print("\n=== 电子热容 Cv/(3NkB) ===")
print("(3NkB = 经典 Dulong-Petit 值)")
print(f"{'T (K)':>8} {'T/TF':>10} {'Cv/(3NkB)':>10}")
for T in [1, 10, 100, 300, 1000, 10000, 30000]:
    ratio = T / TF
    cv_ratio = (math.pi**2 / 6) * ratio  # Cv/(3NkB) = (pi^2/6)*(T/TF)
    print(f"{T:8d} {ratio:10.6f} {cv_ratio:10.6f}")

print(f"\n反直觉发现：室温 T=300K 时 Cv_el/(3NkB) = {math.pi**2/6*300/TF:.6f}")
print("电子热容只有经典值的万分之几——因为只有 EF 附近的电子能被激发！")
print(f"这就是量子统计与经典统计的本质区别。TF = {TF:.0f} K >> 室温。")
```

### 实验 10.3：紧束缚能带结构

```python
"""
PHYS 230 实验：紧束缚能带
一维链: E(k) = E0 - 2t*cos(ka)
展示能带、有效质量、态密度
纯标准库
"""
import math

E0 = 0.0  # 原子能级
t = 1.0   # 跳跃积分
a = 1.0   # 格距

def energy_tb(k):
    """紧束缚色散"""
    return E0 - 2*t*math.cos(k*a)

def effective_mass(k):
    """1/m* = (1/hbar^2)*d2E/dk2 = 2t*cos(ka)/hbar^2
    归一化 hbar=1, m_e=1"""
    d2E = -2*t*a*a*math.cos(k*a)  # d2E/dk2, 注意 cos 二阶导
    # E = -2t cos(ka), dE/dk = 2ta sin(ka), d2E/dk2 = 2t a^2 cos(ka)
    d2E_correct = 2*t*a*a*math.cos(k*a)
    if abs(d2E_correct) < 1e-10:
        return float('inf')
    return 1.0 / d2E_correct

print("=== 一维紧束缚能带 ===")
print(f"E(k) = E0 - 2t*cos(ka),  E0={E0}, t={t}, a={a}")
print(f"带宽 W = 4t = {4*t}")
print(f"\n{'k (×π/a)':>10} {'E(k)':>8} {'m*/m_e':>10} {'含义':>15}")
for k_pi in [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]:
    k = k_pi * math.pi / a
    E = energy_tb(k)
    m_star = effective_mass(k)
    meaning = ""
    if abs(k_pi) < 0.01:
        meaning = "带底 (m*>0)"
    elif abs(abs(k_pi) - 1.0) < 0.01:
        meaning = "带顶 (m*<0!)"
    print(f"{k_pi:10.2f} {E:8.3f} {m_star:10.3f} {meaning:>15}")

print("\n=== ASCII 能带图 ===")
N = 41
height = 15
E_min, E_max = -2*t, 2*t
ks = [-math.pi/a + i*(2*math.pi/a)/(N-1) for i in range(N)]
for row in range(height, -1, -1):
    E_target = E_min + row*(E_max-E_min)/height
    line = ""
    for k in ks:
        E = energy_tb(k)
        if abs(E - E_target) < (E_max-E_min)/height/2:
            line += "*"
        else:
            line += " "
    label = "带顶" if row == height else ("带底" if row == 0 else "")
    print(f"{E_target:5.2f} |{line} {label}")

print("      " + "-"*N)
print("       -π/a        0        +π/a")

print("\n反直觉发现：带顶的有效质量为负！")
print("物理意义：带顶空穴的行为就像质量为 |m*| 的正电荷。")
print("这就是半导体物理中 '空穴' 概念的数学根源。")
```

---

## 11. 局限与延伸

### 11.1 固体物理的边界

| 局限 | 何时不够 | 前沿方向 |
|------|---------|---------|
| 独立电子近似 | 强关联系统（高温超导） | Hubbard 模型、t-J 模型 |
| 周期性假设 | 非晶/准晶/无序系统 | Anderson 局域化 |
| 微扰论 | 拓扑材料 | Berry 相位、拓扑不变量 |
| 经典 BCS | 非常规超导 | 重费米子、铜基/铁基超导 |
| 三维 Bloch | 二维材料 | 石墨烯、拓扑绝缘体 |

### 11.2 从 PHYS 195 到 PHYS 360 的认知跃迁

1. **PHYS 195**：描述晶体——结构、衍射、声子、能带是什么
2. **PHYS 230**：理解能带——为什么有导体/绝缘体/半导体之分
3. **PHYS 240**：超越独立电子——关联效应、量子相变
4. **PHYS 360**：现代凝聚态——拓扑、纠缠、涌现

### 11.3 延伸阅读

- **Ashcroft & Mermin**：凝聚态圣经，深度远超 Kittel
- **Chaikin & Lubensky**：软凝聚态 + 相变的现代视角
- **Girvin & Yang《Modern Condensed Matter Physics》**：含拓扑材料
- ** Coleman《Introduction to Many-Body Physics》**：凝聚态场论
- **Altland & Simons《Condensed Matter Field Theory》**：路径积分方法

---

## 参考文献

1. Kittel, C. *Introduction to Solid State Physics* 9th ed. Wiley, 2018.
2. Ashcroft, N. W. & Mermin, N. D. *Solid State Physics*. Saunders, 1976.
3. Chaikin, P. M. & Lubensky, T. C. *Principles of Condensed Matter Physics*. Cambridge, 1995.
4. Simon, S. H. *The Oxford Solid State Basics*. Oxford, 2013.
5. Girvin, S. M. & Yang, K. *Modern Condensed Matter Physics*. Cambridge, 2019.
6. Bardeen, J., Cooper, L. N. & Schrieffer, J. R. "Theory of Superconductivity." *Phys. Rev.* **108**, 1175 (1957).

---

> **本主题对应讲透X 宪法**：直觉（各节「直觉」段）→ 公式（§1-7 全部 boxed 公式）→ 代码（§10 bash 跑通）→ 不足（§11）→ 应用（§8 Stanford 关联）。
>
> **文件信息**：stanford-physics/topic06-solid-state/solid-state.md · Phase 2 主题 6 · 2026-08-12

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：固体的奥秘藏在「周期性」里——原子按格子排列，电子在周期势中行走，结果产生能带、能隙、导体/绝缘体之分。一块硅为什么是半导体？答案就在它的原子排列方式。

晶体的美在于**平移对称性**：把整个晶体平移一个格矢量，看起来一模一样。这种离散对称性深刻决定了电子和声子的行为。Bloch 定理说：周期势中的电子波函数是「平面波 × 周期函数」——它既不完全自由（像真空电子），也不完全束缚（像原子轨道），而是一种全新的「能带」态。

> **生活类比**：能带就像高速公路上的车道——导带是畅通车道（电子自由跑 = 金属），价带是满车道（电子动不了 = 绝缘体），中间有个收费站（能隙）。半导体的能隙不大不小，加点能量（光/热/电压）电子就能「跳」到畅通车道——这就是芯片的原理。

> **反直觉发现（啊哈时刻）**：
> 1. **金属里有 10⁵⁸ 个电子，但只有费米面附近的极少数参与导电**：费米温度 $T_F \sim 50000$ K，室温电子气像 $T=0$ 一样「冻住」，只有表面薄层可被激发——这就是为什么电子比热 $\propto T$ 而非常数。
> 2. **超导 = 电子配对当玻色子**：两个费米子（电子）通过声子「牵线」结成 Cooper 对，变成玻色子，集体凝聚——零电阻、抗磁性全部涌现。
> 3. **空穴是「缺失的电子」但行为像正电荷**：能带顶的有效质量为负！我们用「空穴」描述它，就像水库里排水孔——缺水的洞看起来在移动。

---

## 🔗 衔接：从哪来，到哪去

| 维度 | 内容 |
|------|------|
| **前置知识** | 主题 3（量子）的薛定谔方程/自旋；主题 4（统计）的费米-狄拉克分布；主题 5（数学）的傅里叶变换 |
| **本主题解决的危机** | 为什么有导体/绝缘体/半导体？Drude 经典模型无法解释电子比热。用量子力学 + 周期势 → 能带理论 |
| **核心跃迁** | 从「描述晶体」（PHYS 195）→「理解能带」（PHYS 230）→「超越独立电子」（PHYS 240）→「拓扑涌现」（PHYS 360） |
| **留下新危机** | ①高温超导机制（BCS 够吗？）②强关联系统（Mott 绝缘体）③拓扑相变 ④二维材料新奇物性 |
| **后续主题** | **主题 7（粒子）**：凝聚态类比（QED ↔ BCS）；**主题 8（GR）**：AdS/CFT 在凝聚态的应用；量子计算 |

---

## 🏭 理论联系实际：5 个现代应用

1. **硅芯片与摩尔定律**：Shockley（Stanford 教授）的半导体物理 → 肖克利半导体实验室 → 硅谷。pn 结二极管方程 $I = I_0(e^{eV/kT}-1)$ 是整个半导体工业的种子。

2. **LED 与太阳能电池**：直接带隙半导体（GaAs）发光，间接带隙（Si）适合光伏。钙钛矿太阳能电池效率从 2009 年 3.8% 飙升到 2024 年 >26%——能带工程的胜利。

3. **超导磁体（MRI + 量子计算）**：NbTi/Nb₃Sn 超导线圈产生强磁场（MRI 3T，LHC 8T）；超导量子比特（Google Willow）是凝聚态物理的直接工程化。

4. **石墨烯与 2D 材料**：单层碳原子六角晶格，电子色散线性（狄拉克锥），迁移率比硅高 100 倍——2010 诺奖，开启了整个 2D 材料家族。

5. **拓扑绝缘体与量子反常霍尔效应**：体绝缘、表面导电的拓扑相。2013 年薛其坤团队实验验证量子反常霍尔效应——无耗散边缘态有望用于低功耗电子学。

---

## 🔬 最新研究前沿（2024-2026）

1. **魔角双层石墨烯（Moiré / Twistronics, 2018-2025）**：两层石墨烯扭转 1.1°「魔角」时出现超导、绝缘体、磁性等丰富相图——一个平台模拟 Hubbard 模型与高温超导机制。2024 年扩展到三层、四层魔角结构，发现手性超导迹象。

2. **室温常压超导探索（2023-2025）**：LK-99 虽被证伪，但激发了对铜氧化物/氢化物高压超导的研究热潮。2024 年多个团队报告在近常压下接近室温的超导迹象（待重复验证）。

3. **分数量子霍尔效应的新平台（2024-2025）**：Stanford/MIT 团队在石墨烯莫尔超晶格中实现了分数量子反常霍尔效应——无需强磁场，基于拓扑能带，为拓扑量子计算提供新路径。

4. **SLAC LCLS-II 超快声子探测（2024-2025）**：飞秒 X 射线衍射直接「拍电影」记录声子动力学，观测电荷密度波相变的飞秒级动力学——验证非平衡相变理论。

5. **转角二维材料的关联与拓扑（2024）**：Stanford 团队在转角 WSe₂ 中实现 Hubbard 模型的量子模拟，直接测量 Mott 绝缘体到超流体的量子相变——用凝聚态实验台做「桌面量子模拟器」。

---

## 🗺️ 学习 Roadmap（Stanford 路径）

```
入门 → PHYS 195 (Kittel)
  │   晶体结构、倒格子、衍射、声子、能带基础、半导体
  │   ✅ 检查点：能用 Bloch 定理解释导体/绝缘体/半导体之分
  ▼
进阶 → PHYS 230 (Ashcroft & Mermin / Simon)
  │   自由电子气、费米面、紧束缚、有效质量、超导 BCS
  │   ✅ 检查点：能推导 Cooper 对结合能与 Tc 关系
  ▼
深造 → PHYS 240/360 (Girvin & Yang / Coleman)
  │   多体物理、格林函数、量子相变、拓扑物态、Berry 相位
  │   ✅ 检查点：理解为什么拓扑绝缘体的表面态受时间反演保护
  ▼
前沿 → Q-FARM 量子计算 / SLAC 量子材料
      莫尔物理、转角电子学、拓扑量子比特、量子模拟器
```

> **费曼的建议**：固体物理的钥匙是「倒格子」——一旦你理解傅里叶变换把晶格变成布里渊区，能带、声子、衍射就全通了。
