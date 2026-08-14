# Cambridge Part IB · Thermal and Statistical Physics

> **教材**：Kittel & Kroemer *Thermal Physics* (2nd ed.) — Cambridge 指定教材；Guenther *Statistical Mechanics* — Cambridge 补充
>
> **Cambridge 课程编号**：Part IB Thermal and Statistical Physics
>
> **Cambridge 特色**：从热力学四定律到系综理论的严密过渡；连接经典力学（Liouville 定理）与量子统计（Bose-Einstein/Fermi-Dirac）的桥梁

---

## 目录

1. [热力学基础](#1-热力学基础)
2. [熵与第二定律](#2-熵与第二定律)
3. [统计力学基础](#3-统计力学基础)
4. [正则系综](#4-正则系综)
5. [量子统计](#5-量子统计)
6. [相变与临界现象](#6-相变与临界现象)
7. [Python 代码演示](#7-python-代码演示)
8. [Tripos 风格习题](#8-tripos-风格习题)

---

## 1. 热力学基础

### 1.1 热力学四定律

| 定律 | 内容 | 数学表述 |
|------|------|---------|
| **第零定律** | 热平衡的传递性 | 若 $A\sim B$ 且 $B\sim C$，则 $A\sim C$ → 温度 $T$ 存在 |
| **第一定律** | 能量守恒 | $dU = \delta Q + \delta W$ |
| **第二定律** | 熵增原理 | $dS \ge \delta Q/T$ |
| **第三定律** | 绝对零度不可达 | $T\to 0$ 时 $S\to S_0$（常数，常取为零）|

### 1.2 第一定律与热力学势

基本微分关系（可逆过程）：

$$dU = T\,dS - P\,dV + \mu\,dN$$

由此定义各种热力学势：

| 势 | 定义 | 微分 |
|----|------|------|
| 内能 $U$ | — | $dU = TdS - PdV + \mu dN$ |
| 焓 $H$ | $H = U + PV$ | $dH = TdS + VdP + \mu dN$ |
| 自由能 $F$ | $F = U - TS$ | $dF = -SdT - PdV + \mu dN$ |
| Gibbs $G$ | $G = U + PV - TS$ | $dG = -SdT + VdP + \mu dN$ |

**物理直觉**：
- $F(T, V, N)$：等温等容系统的极小化目标
- $G(T, P, N)$：等温等压（实验室最常见条件）系统的极小化目标
- 化学势 $\mu = G/N$（对单组分系统）

### 1.3 热容

$$C_V = \left(\frac{\partial U}{\partial T}\right)_V = T\left(\frac{\partial S}{\partial T}\right)_V$$

$$C_P = \left(\frac{\partial H}{\partial T}\right)_P = T\left(\frac{\partial S}{\partial T}\right)_P$$

对理想气体：$C_P - C_V = Nk_B$（Mayer 关系）。

**比热比** $\gamma = C_P/C_V$：单原子理想气体 $\gamma = 5/3$，双原子 $\gamma = 7/5$。

---

## 2. 熵与第二定律

### 2.1 熵的统计定义

Boltzmann 公式（刻在他维也纳墓碑上）：

$$S = k_B \ln \Omega$$

$\Omega$ 是与宏观约束一致的微观态数。这公式将**信息**（$\ln\Omega$）与**物理量**（$S$）直接联系。

### 2.2 第二定律的统计诠释

为什么熵总是增加？因为高熵宏观态对应的微观态数**指数级地多于**低熵态。

**例**：$N$ 个粒子在两半容器中。左边 $n$ 个的概率：

$$P(n) = \binom{N}{n}/2^N$$

对 $N = 10^{23}$（Avogadro 数量级），$P(N/2) \sim 1$，而 $P(N) \sim 2^{-N} \approx 10^{-3\times10^{22}}$。即"所有粒子在左边"不是不可能——只是概率小到**超越任何物理意义**。

### 2.3 玻尔兹曼分布

与恒温热库 $T$ 接触的系统，微观态 $i$（能量 $E_i$）的概率：

$$P_i = \frac{e^{-\beta E_i}}{Z}, \quad \beta = \frac{1}{k_BT}$$

配分函数 $Z = \sum_i e^{-\beta E_i}$ 是一切热力学量的生成函数：

$$F = -k_BT\ln Z$$
$$U = -\frac{\partial \ln Z}{\partial \beta}$$
$$S = k_B(\ln Z + \beta U)$$

### 2.4 Maxwell 关系

由 $dF = -SdT - PdV$ 和 $\frac{\partial^2 F}{\partial T\partial V} = \frac{\partial^2 F}{\partial V\partial T}$：

$$\left(\frac{\partial S}{\partial V}\right)_T = \left(\frac{\partial P}{\partial T}\right)_V$$

类似的 Maxwell 关系有四个（每个热力学势对应一个）。它们在推导难以直接测量的量时极有用。

---

## 3. 统计力学基础

### 3.1 微正则系综

孤立系统（$U, V, N$ 固定），等概率假设：所有可达微观态等概率。

$$P_i = \frac{1}{\Omega(U, V, N)}$$

熵 $S = k_B\ln\Omega$。温度由 $\frac{1}{T} = \left(\frac{\partial S}{\partial U}\right)_{V,N}$ 定义。

### 3.2 从经典力学到统计力学

相空间密度 $\rho(q, p, t)$ 满足**Liouville 方程**（见 Topic 1 §4.3）：

$$\frac{\partial \rho}{\partial t} + \{\rho, H\} = 0$$

平衡时 $\rho$ 不显含时间，$\{\rho, H\} = 0$，故 $\rho$ 是运动积分的函数。对微正则系综：$\rho = \text{const}$（在能量壳上）。

**Liouville 定理保证相空间体积不变**——这是统计力学的经典力学根基。没有这个定理，就无法合理地定义"等概率"。

### 3.3 理想气体的熵

$N$ 个单原子理想气体，体积 $V$，能量 $U$：

$$S = Nk_B\left[\ln\frac{V}{N}\left(\frac{4\pi m U}{3Nh^2}\right)^{3/2}\right] + \frac{5}{2}Nk_B$$

这就是 **Sackur-Tetrode 方程**。注意其中的 $1/N!$（Gibbs 修正）——它解决了 Gibbs 佯谬（混合同种气体熵不变），且其量子力学根源是粒子不可分辨性。

---

## 4. 正则系综

### 4.1 与热库接触的系统

系统与恒温热库 $T$ 接触。微观态 $i$ 的概率（Boltzmann 分布）：

$$P_i = \frac{e^{-E_i/(k_BT)}}{Z}$$

### 4.2 配分函数

$$Z = \sum_i e^{-\beta E_i}$$

经典极限下（相空间积分）：

$$Z = \frac{1}{N!h^{3N}}\int d^{3N}q\,d^{3N}p\,e^{-\beta H(q,p)}$$

热力学量：

| 量 | 公式 |
|----|------|
| 自由能 | $F = -k_BT\ln Z$ |
| 内能 | $U = -\frac{\partial\ln Z}{\partial\beta}$ |
| 熵 | $S = k_B\ln Z + k_BT\frac{\partial\ln Z}{\partial T}$ |
| 压强 | $P = -\left(\frac{\partial F}{\partial V}\right)_T$ |
| 热容 | $C_V = \frac{1}{k_BT^2}\frac{\partial^2\ln Z}{\partial\beta^2}$ |

### 4.3 能量涨落

正则系综中能量不固定，但涨落很小：

$$\frac{\Delta E}{\langle E\rangle} \sim \frac{1}{\sqrt{N}}$$

对宏观系统（$N \sim 10^{23}$），涨落仅为 $10^{-11}$ 量级——**这就是为什么微正则和正则系综对宏观系统等价**。

### 4.4 巨正则系综

与恒温恒化学势热库接触，$T, V, \mu$ 固定，粒子数可变：

$$\mathcal{Z} = \sum_N \sum_i e^{-\beta(E_{N,i} - \mu N)}$$

巨势 $\Phi = -k_BT\ln\mathcal{Z}$。

巨正则系综在**量子统计**（处理粒子数可变的量子气体）中最为方便。

---

## 5. 量子统计

### 5.1 不可分辨性与统计

量子粒子的不可分辨性导致两种统计：

| 统计 | 波函数 | 粒子 | 占有数 |
|------|--------|------|--------|
| **Bose-Einstein** | 对称 | 玻色子（整数自旋） | 无限制 |
| **Fermi-Dirac** | 反对称 | 费米子（半整数自旋） | 0 或 1 |

### 5.2 分布函数

能量 $\epsilon$ 的能级平均占有数：

**Bose-Einstein**：
$$\bar{n}_{BE}(\epsilon) = \frac{1}{e^{(\epsilon - \mu)/(k_BT)} - 1}$$

**Fermi-Dirac**：
$$\bar{n}_{FD}(\epsilon) = \frac{1}{e^{(\epsilon - \mu)/(k_BT)} + 1}$$

经典极限（$\epsilon - \mu \gg k_BT$）都退化为 **Maxwell-Boltzmann**：
$$\bar{n}_{MB} \approx e^{-(\epsilon-\mu)/(k_BT)}$$

### 5.3 黑体辐射（玻色子）

光子是玻色子（自旋 1），$\mu = 0$（光子数不守恒）。Planck 分布：

$$u(\nu) = \frac{8\pi h\nu^3}{c^3}\frac{1}{e^{h\nu/(k_BT)} - 1}$$

对频率积分得到 Stefan-Boltzmann 定律：$j = \sigma T^4$，$\sigma = \frac{2\pi^5 k_B^4}{15h^3 c^2}$。

对频率求峰值（$du/d\nu = 0$）得到 Wien 位移定律：$\nu_{\max}/T \approx 5.88 \times 10^{10}$ Hz/K。

### 5.4 白矮星与电子简并压（费米子）

电子是费米子。在 $T \to 0$ 极限，所有态填到 Fermi 能 $\epsilon_F$：

$$\epsilon_F = \frac{\hbar^2}{2m_e}(3\pi^2 n)^{2/3}$$

（$n$ = 电子数密度）。Fermi 能以下的态全满，以上全空。这个"零温压"——**电子简并压**——抵抗引力坍缩，支撑白矮星。

**反直觉**：温度 $T \ll T_F = \epsilon_F/k_B$ 时，比热 $C_e \propto T$（线性），而非经典的常数 $3Nk_B/2$。这就是为什么常温金属的电子比热远小于经典预期——只有 Fermi 面附近 $k_BT$ 范围内的电子才能参与热激发。

### 5.5 Bose-Einstein 凝聚

当温度低于临界温度 $T_c$ 时，宏观数量的玻色子凝聚到基态：

$$T_c = \frac{2\pi\hbar^2}{mk_B}\left(\frac{n}{\zeta(3/2)}\right)^{2/3}$$

$\zeta(3/2) \approx 2.612$。凝聚分数 $N_0/N = 1 - (T/T_c)^{3/2}$。

1995 年首次在碱金属气体中实验实现 BEC（2001 年诺奖），这是量子统计的惊人宏观体现。

---

## 6. 相变与临界现象

### 6.1 相变的分类

**Ehrenfest 分类**（按自由能导数的连续性）：
- **一级相变**：$G$ 的一阶导数（$S, V$）不连续 → 潜热
- **连续相变**（二级以上）：一阶导数连续，高阶导数不连续 → 无潜热

**现代观点**：
- 一级：有潜热（如水结冰）
- 连续：无潜热，有临界点附近的**普适性**和**标度行为**

### 6.2 序参量与对称性破缺

Landau 理论：相变由**序参量** $\eta$ 描述，自由能展开为：

$$F(\eta, T) = F_0 + a(T-T_c)\eta^2 + b\eta^4 + \cdots$$

- $T > T_c$：$a > 0$，极小在 $\eta = 0$（无序相）
- $T < T_c$：$a < 0$，极小在 $\eta = \pm\sqrt{-a/2b} \ne 0$（有序相）

对称性**自发破缺**：自由能 $F(\eta)$ 对 $\eta \to -\eta$ 对称，但系统选择了 $\eta > 0$ 或 $\eta < 0$ 之一。

### 6.3 临界指数

连续相变在临界点 $T_c$ 附近服从幂律：

$$\eta \sim (T_c - T)^\beta, \quad C_V \sim |T-T_c|^{-\alpha}, \quad \chi \sim |T-T_c|^{-\gamma}$$

**普适性**：完全不同的物理系统（液体-气体、铁磁体、合金有序-无序）可以有**相同的临界指数**，只取决于维数和序参量分量数。

### 6.4 Ising 模型

最简单的相变模型：自旋 $s_i = \pm 1$ 在格点上，哈密顿量：

$$\hat{H} = -J\sum_{\langle i,j\rangle} s_i s_j - h\sum_i s_i$$

- **一维**（Ising 1925）：无相变（$T_c = 0$）
- **二维**（Onsager 1944）：精确解，$T_c > 0$，临界指数 $\beta = 1/8$

Onsager 解是统计物理的里程碑——证明了涨落和关联可以在二维产生长程序。这是 Cambridge Part II 统计物理的核心话题。

---

## 7. Python 代码演示

### 7.1 Maxwell-Boltzmann / Fermi-Dirac / Bose-Einstein 分布

```python
"""
三种量子统计分布函数的对比
零依赖。
"""
import math

def maxwell_boltzmann(epsilon, mu, T_star):
    """n_MB = exp(-(ε-μ)/kT)"""
    x = (epsilon - mu) / T_star
    if x > 500:
        return 0.0
    return math.exp(-x)

def fermi_dirac(epsilon, mu, T_star):
    """n_FD = 1/(exp((ε-μ)/kT) + 1)"""
    x = (epsilon - mu) / T_star
    if x > 500:
        return 0.0
    if x < -500:
        return 1.0
    return 1.0 / (math.exp(x) + 1)

def bose_einstein(epsilon, mu, T_star):
    """n_BE = 1/(exp((ε-μ)/kT) - 1), 要求 ε > μ"""
    x = (epsilon - mu) / T_star
    if x <= 0:
        return float('inf')
    if x > 500:
        return 0.0
    return 1.0 / (math.exp(x) - 1)

print("=== 三种量子统计分布 ===")
print("横轴: ε/(kT) [0 到 5], μ=0\n")

# 高温极限 (T_star=2.0): 三者趋于一致
print("--- 高温极限 (kT=2.0) → 经典极限, 三者趋同 ---")
print(f"{'ε/kT':>6} {'MB':>10} {'FD':>10} {'BE':>10}")
for e10 in range(0, 51, 5):
    e = e10 / 10.0
    T_star = 2.0
    mb = maxwell_boltzmann(e, 0, T_star)
    fd = fermi_dirac(e, 0, T_star)
    be = bose_einstein(e, 0, T_star)
    print(f"{e:6.1f} {mb:10.4f} {fd:10.4f} {be:10.4f}")

# 低温 (T_star=0.2): 差异显著
print(f"\n--- 低温 (kT=0.2) → 量子效应显著 ---")
print(f"{'ε/kT':>6} {'MB':>10} {'FD':>10} {'BE':>10}")
for e10 in range(0, 51, 5):
    e = e10 / 10.0
    T_star = 0.2
    mb = maxwell_boltzmann(e, 0, T_star)
    fd = fermi_dirac(e, 0, T_star)
    be = bose_einstein(e, 0, T_star)
    be_str = f"{be:10.2f}" if be < 1000 else "    >1000"
    print(f"{e:6.1f} {mb:10.4f} {fd:10.4f} {be_str}")

print("\n关键观察:")
print("  FD: ε→0时 n→1 (Pauli 不相容, 最多1个)")
print("  BE: ε→0时 n→∞ (玻色凝聚倾向)")
print("  MB: 经典 Boltzmann 尾巴")
print("  高温时三者趋同: 量子效应消失")
```

### 7.2 理想气体分子的速率分布

```python
"""
Maxwell 速率分布
f(v) dv = 4π (m/(2πkT))^(3/2) v² exp(-mv²/(2kT))
零依赖，用自然单位 m=k=T=1。
"""
import math

def maxwell_speed_distribution(v, m=1.0, kT=1.0):
    """Maxwell 速率分布 (归一化)"""
    if v < 0:
        return 0.0
    alpha = m / (2 * kT)
    norm = 4 * math.pi * (alpha / math.pi)**1.5
    return norm * v**2 * math.exp(-alpha * v**2)

print("=== Maxwell 速率分布 (m=kT=1 自然单位) ===\n")

# 计算特征速率
v_mp = math.sqrt(2)       # 最概然速率 vp = √(2kT/m)
v_avg = math.sqrt(8/math.pi)  # 平均速率 <v> = √(8kT/πm)
v_rms = math.sqrt(3)      # 方均根速率 vrms = √(3kT/m)

print(f"最概然速率 vp = √2 ≈ {v_mp:.4f}")
print(f"平均速率   <v> = √(8/π) ≈ {v_avg:.4f}")
print(f"方均根速率 vrms = √3 ≈ {v_rms:.4f}")
print(f"关系: vp < <v> < vrms\n")

# 分布表
print(f"{'v':>6} {'f(v)':>10} {'柱状图':>40}")
dv = 0.1
total = 0.0
for i in range(60):
    v = i * dv
    f = maxwell_speed_distribution(v)
    total += f * dv
    bar = "█" * int(f * 50)
    if i % 2 == 0:
        print(f"{v:6.1f} {f:10.6f} {bar}")

print(f"\n归一化检验: ∫f(v)dv ≈ {total:.6f} (应=1.0)")

# 不同温度比较
print(f"\n=== 温度对分布的影响 ===")
print(f"{'v':>6}", end="")
for kT in [0.5, 1.0, 2.0, 4.0]:
    print(f"  T={kT:.1f}", end="")
print()

for i in range(0, 80, 4):
    v = i * 0.1
    print(f"{v:6.1f}", end="")
    for kT in [0.5, 1.0, 2.0, 4.0]:
        f = maxwell_speed_distribution(v, kT=kT)
        print(f"  {f:.4f}", end="")
    print()

print(f"\n→ 温度升高: 分布展宽、峰值右移、变低")
print(f"→ 这就是热运动: 高温气体分子'跑得更快'")
```

### 7.3 Ising 模型 Monte Carlo（Metropolis 算法）

```python
"""
1D 和 2D Ising 模型的 Metropolis Monte Carlo
零依赖。
"""
import math
import random

def ising_1d_mc(N=20, J=1.0, h=0.0, T=2.0, n_steps=10000, seed=42):
    """1D Ising 模型 Metropolis MC"""
    random.seed(seed)
    spins = [random.choice([-1, 1]) for _ in range(N)]

    magnetization_history = []
    energy_history = []

    for step in range(n_steps):
        i = random.randint(0, N - 1)
        # 计算 flip 的能量变化
        s = spins[i]
        nb = spins[(i-1)%N] + spins[(i+1)%N]
        dE = 2 * s * (J * nb + h)

        # Metropolis 判据
        if dE < 0 or random.random() < math.exp(-dE / T):
            spins[i] = -s

        # 每 100 步记录
        if step % 100 == 0:
            M = sum(spins) / N
            E = -J * sum(spins[i]*spins[(i+1)%N] for i in range(N)) / N
            E -= h * sum(spins) / N
            magnetization_history.append(M)
            energy_history.append(E)

    return magnetization_history, energy_history

def ising_2d_mc(N=10, J=1.0, h=0.0, T=2.0, n_steps=20000, seed=42):
    """2D Ising 模型 Metropolis MC
    Onsager 精确解临界温度: Tc = 2J/ln(1+√2) ≈ 2.269J
    """
    random.seed(seed)
    spins = [[random.choice([-1, 1]) for _ in range(N)] for _ in range(N)]

    magnetization_history = []
    energy_history = []

    for step in range(n_steps):
        i = random.randint(0, N - 1)
        j = random.randint(0, N - 1)
        s = spins[i][j]
        # 周期性边界 4 邻居
        nb = (spins[(i-1)%N][j] + spins[(i+1)%N][j] +
              spins[i][(j-1)%N] + spins[i][(j+1)%N])
        dE = 2 * s * (J * nb + h)

        if dE < 0 or random.random() < math.exp(-dE / T):
            spins[i][j] = -s

        if step % 200 == 0:
            M = sum(sum(row) for row in spins) / (N*N)
            E = 0.0
            for i in range(N):
                for j in range(N):
                    E -= J * spins[i][j] * (spins[(i+1)%N][j] + spins[i][(j+1)%N])
            E /= (N*N)
            magnetization_history.append(M)
            energy_history.append(E)

    return magnetization_history, energy_history

print("=== Ising 模型 Metropolis Monte Carlo ===\n")

# 2D Ising: 不同温度下的磁化强度
Tc_onsager = 2.0 / math.log(1 + math.sqrt(2))
print(f"2D Ising Onsager 精确临界温度: Tc = {Tc_onsager:.4f} J/k_B\n")

print(f"{'T':>6} {'<|M|>':>10} {'<E>/N':>10} {'相':>8}")
print("-" * 40)
for T in [1.0, 1.5, 2.0, 2.269, 2.5, 3.0, 4.0]:
    mag_hist, E_hist = ising_2d_mc(N=10, T=T, n_steps=30000)
    # 取后半程平均（跳过热化期）
    M_avg = sum(abs(m) for m in mag_hist[len(mag_hist)//2:]) / (len(mag_hist)//2)
    E_avg = sum(E_hist[len(E_hist)//2:]) / (len(E_hist)//2)
    phase = "铁磁有序" if M_avg > 0.3 else "顺磁无序"
    marker = " ← Tc" if abs(T - Tc_onsager) < 0.01 else ""
    print(f"{T:6.2f} {M_avg:10.4f} {E_avg:10.4f} {phase:>8}{marker}")

print(f"\n→ T < Tc: 自发磁化 (铁磁相)")
print(f"→ T > Tc: 无自发磁化 (顺磁相)")
print(f"→ T ≈ Tc: 临界涨落, 磁化率发散")

# 1D Ising: 无相变
print(f"\n=== 1D Ising 模型 (无有限温度相变) ===")
print(f"{'T':>6} {'<|M|>':>10}")
for T in [0.5, 1.0, 2.0, 4.0, 8.0]:
    mag_hist, _ = ising_1d_mc(N=20, T=T, n_steps=20000)
    M_avg = sum(abs(m) for m in mag_hist[len(mag_hist)//2:]) / (len(mag_hist)//2)
    print(f"{T:6.1f} {M_avg:10.4f}")
print("→ 1D Ising 在任何 T>0 都无自发磁化 (Tc=0)")
```

### 7.4 黑体辐射谱

```python
"""
Planck 黑体辐射谱 (能量密度 vs 频率)
零依赖。
"""
import math

def planck_spectral_density(nu, T):
    """u(ν,T) = 8πhν³/c³ · 1/(exp(hν/kT)-1)
    用自然单位 h=k=c=1: u = 8πν³/(e^{ν/T} - 1)
    """
    if nu <= 0:
        return 0.0
    x = nu / T
    if x < 0.001:
        return 8 * math.pi * nu**2 * T  # Rayleigh-Jeans 极限: u ≈ 8πν²T
    if x > 500:
        return 0.0
    return 8 * math.pi * nu**3 / (math.exp(x) - 1)

def rayleigh_jeans(nu, T):
    """经典极限: u = 8πν²T (紫外灾难!)"""
    return 8 * math.pi * nu**2 * T

def wien_approximation(nu, T):
    """高频近似: u ∝ ν³ exp(-ν/T)"""
    return 8 * math.pi * nu**3 * math.exp(-nu / T)

print("=== Planck 黑体辐射谱 (h=k=c=1 自然单位) ===\n")

# 找峰值频率 (Wien 位移定律)
# d/dx [x³/(e^x-1)] = 0 → x ≈ 2.821
x_peak = 2.821
print(f"Wien 位移定律: 峰值在 x=ν/T ≈ {x_peak}")
print(f"即 ν_max ≈ {x_peak:.3f} × T\n")

# Planck vs Rayleigh-Jeans (紫外灾难)
print(f"{'ν/T':>6} {'Planck':>12} {'Rayleigh-Jeans':>15} {'Wien':>12}")
print("-" * 50)
for x10 in range(1, 101, 5):
    x = x10 / 10.0
    T = 1.0
    nu = x * T
    u_planck = planck_spectral_density(nu, T)
    u_rj = rayleigh_jeans(nu, T)
    u_wien = wien_approximation(nu, T)
    marker = " ← 峰值" if abs(x - x_peak) < 0.03 else ""
    print(f"{x:6.1f} {u_planck:12.4f} {u_rj:15.4f} {u_wien:12.4f}{marker}")

print(f"\n关键观察:")
print(f"  Rayleigh-Jeans (经典): ν→∞ 时发散 → '紫外灾难'")
print(f"  Planck (量子): 高频指数衰减, 无灾难")
print(f"  Wien (高频近似): 低频区偏离 Planck")
print(f"  峰值 x ≈ {x_peak} → 高温物体辐射蓝移 (Wien 位移)")

# 不同温度的黑体谱
print(f"\n=== 不同温度的黑体谱 (模拟恒星) ===")
stars = [("红巨星", 0.5), ("太阳", 1.0), ("天狼星", 2.0), ("蓝巨星", 5.0)]
print(f"{'ν/T':>6}", end="")
for name, _ in stars:
    print(f"  {name:>8}", end="")
print()

for x10 in range(1, 101, 5):
    x = x10 / 10.0
    print(f"{x:6.1f}", end="")
    for name, T in stars:
        nu = x * 5.0  # 固定频率范围
        u = planck_spectral_density(nu, T) / 1000  # 缩放
        print(f"  {u:8.2f}", end="")
    print()
```

---

## 8. Tripos 风格习题

### 习题 1（Part IB）：理想气体的绝热膨胀

理想气体（$\gamma = C_P/C_V$）经历绝热过程。

(a) 推导 $PV^\gamma = \text{const}$。
(b) 气体从 $(P_1, V_1)$ 绝热膨胀到 $V_2 = 2V_1$，求 $T_2/T_1$（对 $\gamma = 5/3$）。
(c) 计算气体对外做的功 $W$。

<details>
<summary>解答</summary>

(a) 绝热 $dQ = 0$，第一定律 $dU = -P\,dV$。

对理想气体 $dU = nC_V dT$，$P = nRT/V$：

$$nC_V dT = -\frac{nRT}{V}dV$$

$$\frac{dT}{T} = -\frac{R}{C_V}\frac{dV}{V} = -(\gamma-1)\frac{dV}{V}$$

积分：$\ln T = -(\gamma-1)\ln V + \text{const}$，即 $TV^{\gamma-1} = \text{const}$。

用 $PV = nRT$ 代入：$P V^\gamma = \text{const}$。

(b) $T_2/T_1 = (V_1/V_2)^{\gamma-1} = (1/2)^{2/3} = 2^{-2/3} \approx 0.630$

(c) $W = \int_{V_1}^{V_2} P\,dV = \frac{P_1 V_1^\gamma}{1-\gamma}\left[V_2^{1-\gamma} - V_1^{1-\gamma}\right]$

$= \frac{P_1 V_1}{1-\gamma}\left[2^{1-\gamma} - 1\right] = \frac{nRT_1}{1-\gamma}[2^{-2/3}-1]$

$= \frac{3}{2}nRT_1[1 - 2^{-2/3}] \approx 0.555\,nRT_1 > 0$（气体做正功）
</details>

### 习题 2（Part IB）：理想顺磁体的熵

$N$ 个自旋 1/2 粒子在磁场 $B$ 中，每个自旋能量 $\epsilon = \mp\mu B$（平行/反平行）。

(a) 写出配分函数 $Z$。
(b) 求磁化强度 $M = N\mu\tanh(\mu B / k_BT)$。
(c) 求熵 $S$，并讨论 $B \to 0$ 和 $B \to \infty$ 极限。
(d) 这与"Gibbs 佞谬"有什么关系？

<details>
<summary>解答</summary>

(a) 单个自旋：$Z_1 = e^{\beta\mu B} + e^{-\beta\mu B} = 2\cosh(\beta\mu B)$

$N$ 个独立自旋：$Z = Z_1^N = [2\cosh(\beta\mu B)]^N$

(b) $F = -k_BT\ln Z = -Nk_BT\ln[2\cosh(\beta\mu B)]$

$M = -\frac{\partial F}{\partial B} = N\mu\tanh(\beta\mu B)$

(c) $U = -N\mu B\tanh(\beta\mu B)$

$S = (U-F)/T = Nk_B\left[\ln 2\cosh(\beta\mu B) - \beta\mu B\tanh(\beta\mu B)\right]$

$B \to 0$: $\tanh(x) \approx x$，$S \to Nk_B\ln 2$（每个自旋 2 态等概率，最大熵）

$B \to \infty$: $\tanh \to 1$，$\ln\cosh \to \beta\mu B$，$S \to 0$（全部对齐，唯一态）

(d) $B=0$ 时 $S = Nk_B\ln 2$。若把这 $N$ 个自旋分为两组 $N_1$ 和 $N_2$，分别独立处理，$S = S_1 + S_2 = N_1 k_B\ln 2 + N_2 k_B\ln 2 = Nk_B\ln 2$——熵可加，无佯谬。但如果是经典可区分粒子，就会出现 Gibbs 佯谬（额外熵）。自旋的量子不可分辨性避免了这个问题。
</details>

### 习题 3（Part II 预习）：白矮星的电子简并压

(a) 利用 Fermi-Dirac 分布在 $T \to 0$ 极限，推导电子数密度 $n$ 与 Fermi 动量 $p_F$ 的关系。
(b) 求电子简并压 $P = \frac{2}{3}\frac{U}{V}$（非相对论极限）。
(c) 估算白矮星（$n \sim 10^{36}$/m³）的中心压强。
(d) 将此与引力压比较，讨论稳定性。

<details>
<summary>解答</summary>

(a) $T=0$ 时所有 $p < p_F$ 的态填满。态密度（含自旋 2）：

$$n = 2\int_0^{p_F}\frac{4\pi p^2}{h^3}dp = \frac{8\pi p_F^3}{3h^3}$$

$$p_F = h\left(\frac{3n}{8\pi}\right)^{1/3} = \hbar(3\pi^2 n)^{1/3}$$

(b) 非相对论 $U = \sum_{p<p_F} p^2/(2m_e)$。每单位体积：

$$\frac{U}{V} = 2\int_0^{p_F}\frac{p^2}{2m_e}\frac{4\pi p^2}{h^3}dp = \frac{8\pi}{10 m_e h^3}p_F^5 = \frac{3}{5}n\epsilon_F$$

$P = \frac{2}{3}\frac{U}{V} = \frac{2}{5}n\epsilon_F = \frac{\hbar^2}{5m_e}(3\pi^2)^{2/3}n^{5/3}$

(c) $n = 10^{36}$/m³:

$p_F = \hbar(3\pi^2 \times 10^{36})^{1/3} \approx \hbar \times 3.1\times10^{12}$ m$^{-1}$

$\epsilon_F = p_F^2/(2m_e) \approx \frac{(1.05\times10^{-34})^2 \times (3.1\times10^{12})^2}{2\times9.1\times10^{-31}} \approx 5.8\times10^{-15}$ J $\approx 36$ keV

$P \approx \frac{2}{5}\times 10^{36}\times 5.8\times10^{-15} \approx 2.3\times10^{21}$ Pa

(d) 白矮星引力压 $P_{\text{grav}} \sim GM^2/R^4$。对 $M \sim 10^{30}$ kg, $R \sim 10^7$ m:

$P_{\text{grav}} \sim \frac{6.67\times10^{-11}\times10^{60}}{10^{28}} \sim 10^{22}$ Pa

与简并压量级相当！这就是白矮星能稳定存在的原理。当质量超过 Chandrasekhar 极限（$\sim 1.4 M_\odot$），电子简并压不足以抵抗引力 → 中子星或黑洞。
</details>

### 习题 4（Part IB）：Landau 自由能与相变

(a) 某系统自由能 $F = F_0 + a(T-T_c)\eta^2 + b\eta^4$（$a, b > 0$），求序参量 $\eta$ 的平衡值。
(b) 求比热的跳变 $\Delta C$。
(c) 求临界指数 $\beta$（$T \to T_c^-$ 时 $\eta$ 的行为）。

<details>
<summary>解答</summary>

(a) $\frac{\partial F}{\partial \eta} = 2a(T-T_c)\eta + 4b\eta^3 = 0$

$\eta[\eta^2 + \frac{a(T-T_c)}{2b}] = 0$

- $T > T_c$: 唯一极小 $\eta = 0$
- $T < T_c$: $\eta = \pm\sqrt{\frac{a(T_c-T)}{2b}}$

(b) $F_{\min} = \begin{cases}F_0 & T>T_c \\ F_0 - \frac{a^2(T_c-T)^2}{4b} & T<T_c\end{cases}$

$S = -\frac{\partial F}{\partial T} = \begin{cases}0 & T>T_c \text{ (相对)}\\ \frac{a^2(T_c-T)}{2b} & T<T_c\end{cases}$

$C = T\frac{\partial S}{\partial T}$，故在 $T_c$ 处 $C$ 从 0 跳到 $\frac{a^2 T_c}{2b}$。

$\Delta C = \frac{a^2 T_c}{2b}$（有限跳变 → 二级相变特征）

(c) $\eta \propto (T_c-T)^{1/2}$，故 $\beta = 1/2$（Landau/平均场值）。

注意：2D Ising 精确值 $\beta = 1/8 \ne 1/2$——涨落修正了平均场。
</details>

---

## Cambridge 统计物理传统

### Maxwell-Boltzmann 与剑桥

**James Clerk Maxwell** 是统计物理的奠基人之一：
- **Maxwell 速率分布** (1860)：第一个统计物理定律，确立了温度与分子速度的定量关系
- **Maxwell 妖** (1867)：关于第二定律的思想实验，后来被 Landauer 原理（信息擦除需要耗能）解决
- **Maxwell-Boltzmann 统计**：与 Boltzmann 共同建立了经典统计力学框架

### Boltzmann 与剑桥

虽然 Boltzmann 是维也纳人，但他的熵公式 $S = k_B\ln\Omega$ 在剑桥的传播中起了决定性作用。**Eddington**（Cambridge）曾将熵增原理称为"宇宙中唯一不可逆的方向"。

### 现代 Cavendish 的统计物理

- **Sir Sam Edwards**：将统计力学方法应用于聚合物和颗粒物质（Copernicus of Soft Matter）
- **Cavendish 凝聚态理论组**：量子相变、拓扑物态、量子霍尔效应
- **Cambridge Part III**：从平均场到重整化群的完整训练

### 从 Liouville 到 Gibbs

Cambridge Part IB 的教学主线特别强调从**经典力学**（Topic 1 的 Liouville 定理）到**统计力学**的桥梁：

$$\text{Hamilton 力学} \xrightarrow{\text{Liouville 定理}} \text{微正则系综} \xrightarrow{\text{热库接触}} \text{正则系综} \xrightarrow{\text{量子化}} \text{量子统计}$$

这条主线将四个物理主题有机连接——这正是 Cambridge Tripos 体系的教学特色。

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Kittel & Kroemer Ch 1-3 | 热力学 + 熵 | Part IB 核心 |
| Kittel & Kroemer Ch 4-6 | 玻尔兹曼 + 理想气体 | Part IB |
| Kittel & Kroemer Ch 7-9 | 量子统计 | Part IB 核心 |
| Guenther Ch 1-5 | 系综理论 | Part IB 深度 |
| Guenther Ch 6-8 | 相变 | Part II 预习 |
| Schroeder *Thermal Physics* | 全部 | 直觉补充 |
| Reif *Statistical Physics* | 全部 | 研究生经典 |
| Pathria & Beale | 研究生 | Part II/III |
| Landau & Lifshitz Vol 5 | 全部 | 简洁优美 |

---

**版本**：v1.0 (2026-08-12) · Cambridge Part IB Thermal and Statistical Physics


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：当你有亿亿个分子时，不可能跟踪每一个——但你不需要，因为"平均"行为出奇地可预测。统计力学就是把"无数微观粒子"翻译成"少数宏观量"（温度、压强、熵）的语法书。
>
> **生活类比**：摇晃一盒豆子。每颗豆子的轨迹都混乱无比，但整盒豆子的"平均动能"（温度）和"挤的程度"（压强）却非常稳定。统计力学就是研究这种"混乱中的秩序"。
>
> **反直觉发现（啊哈时刻）**：时间只朝一个方向流（熵增、打碎的杯子不会复原），但底层的微观方程是**完全时间可逆**的！时间箭头来自我们对初始条件的无知——这就是 Loschmidt 回复佯谬，物理学最深的哲学谜题之一（见 Demo 7 麦克斯韦妖）。

---

## 🔗 衔接：从哪来，到哪去

- **前置知识**：**经典力学（相空间、哈密顿、Liouville 定理——Topic 1 §4）**、概率论、组合数学、Part IB 热学
- **危机（统计的诞生）**：热力学是唯象定律（"为什么"不清楚），需要微观基础 → Boltzmann 用 $S=k\ln\Omega$ 给出熵的原子解释
- **新危机**：
  - 非平衡态（生命、玻璃、湍流）没有好的统计描述 → **非平衡统计力学**
  - 可逆微观方程如何给出不可逆宏观？（Loschmidt、Zermelo 佯谬）
- **后续去向**：量子统计 → **凝聚态**（Fermi/Bose 分布，Topic 6）；涨落定理 → 生物物理；**信息论与热力学统一**（Landauer 原理）

---

## 🏭 理论联系实际：5 个现代应用

1. **半导体掺杂与载流子浓度**：Fermi-Dirac 分布直接决定晶体管的电子/空穴密度。
2. **热机与制冷机效率**：卡诺极限是所有发电厂、空调、冰箱、热泵的理论上限。
3. **化学反应速率**：Arrhenius 公式 $k\propto e^{-E_a/kT}$ 就是玻尔兹曼因子的直接应用。
4. **蛋白质折叠与相变**：统计力学模型（Ising、HP 模型）解释生物大分子的协同折叠。
5. **金融与复杂网络**：幂律分布、相变、涨落——统计物理被广泛用于经济物理与网络科学。

---

## 🔬 最新研究前沿（2024-2026）

1. **活性物质（active matter）**：2024–2025 自推进粒子、细菌群落、细胞集体运动的连续介质理论成为软凝聚态最大热点；剑桥有专门的 Active Matter 研究组。
2. **玻璃转变之谜**：2024–2025 仍是无序系统最大的未解难题，mean-field RFOT 理论与动力学玻璃理论持续交锋（*Nature Physics* 系列）。
3. **时间晶体**：2024 在开放/驱动量子系统中实现稳定的非平衡"时间晶体"相——打破热平衡框架的新物态。
4. **非厄米 / 开放系统统计力学**：2024–2025 为与环境有能量/粒子交换的非幺正系统建立新的统计描述。
5. **信息热力学**：2024 用纳米胶体机器和单分子实验验证涨落定理（Crooks、Jarzynski），逼近 Landauer 擦除极限 $kT\ln 2$（见 Demo 7）。

---

## 🗺️ 学习 Roadmap（Cambridge Tripos 路径）

| 阶段 | 课程 | 你应当能做到 |
|------|------|------------|
| **Part IA** | Physics A/B（热学） | 温度、热力学四定律、理想气体、熵的初步概念 |
| **Part IB** | Thermal Physics | 配分函数、正则系综、Boltzmann 分布、热力学势 |
| **Part II** | Statistical Physics | 巨正则系综、Fermi/Bose 分布、相变与临界现象 |
| **Part II** | Soft Matter / Polymers | 软物质、高分子物理 |
| **Part III** | Non-equilibrium / Critical Phenomena / Quantum Many-body | 重整化群、非平衡统计、量子多体、生物物理 |

**知识检查三问**：
1. 为什么麦克斯韦妖**不违反**热力学第二定律？（Landauer 原理，Demo 7）
2. 为什么绝对零度（0 K）不可达？（热力学第三定律 + 量子零点能）
3. 为什么金属的电子比热远小于经典预期？（Fermi-Dirac 退化，只有费米面附近的电子活跃）
