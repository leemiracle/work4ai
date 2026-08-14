# Topic 04 · 统计物理 — Caltech Ph 2c / Ph 127 / Ph 129

> **课程链**：Ph 2abc（Feynman Lectures + Schroeder 风格导引）→ Ph 127abc Statistical Physics（Pathria / Reif）→ Ph 129ab Statistical Mechanics（Landau & Lifshitz Vol 5 / Pathria）
>
> **教材三角**：Reif *Fundamentals of Statistical and Thermal Physics*（最全面的本科-研究生过渡教材） · Pathria & Beale *Statistical Mechanics* 4ed（研究生标准） · Landau & Lifshitz Vol 5 *Statistical Physics*（Landau 的绝妙洞察，Caltech Ph 129 参考书）

---

## Caltech 特色：小班 + LIGO/Thorne 关联

Caltech 的统计物理教学有两个独有基因：

1. **超小班**——Ph 127/129 通常只有 5–15 人。教授可以按学生反应即时调整深度，这对统计物理尤其重要——因为统计物理的直觉（熵=无知、温度=拉格朗日乘子、相变=集体涌现）需要反复打磨。

2. **LIGO/Thorne 关联**——Kip Thorne（Caltech 教授、2017 诺奖）的 LIGO 团队需要极端精密的热噪声分析（悬挂镜的热涨落、量子散粒噪声）。Caltech 40m 原型干涉仪就是一个统计物理实验台。从涨落-耗散定理到干涉仪噪声谱，统计物理在 Caltech 不是抽象理论——它是 LIGO 能否探测到引力波的关键。

---

## §1 热力学

### 1.1 热力学四定律

| 定律 | 表述 | 数学 |
|------|------|------|
| 第零定律 | 热平衡可传递 → 温度存在 | $A\sim B,\, B\sim C \Rightarrow A\sim C$ |
| 第一定律 | 能量守恒 | $dU = \delta Q - \delta W$ |
| 第二定律 | 熵不减（孤立系）| $dS \geq 0$（不可逆）/ $dS = \delta Q/T$（可逆） |
| 第三定律 | $T\to 0$ 时 $S\to S_0$（常数）| $\lim_{T\to 0}S = 0$（完美晶体）|

### 1.2 热力学势

通过 Legendre 变换从内能 $U(S,V,N)$ 导出：

| 势 | 定义 | 自然变量 | 微分 |
|----|------|---------|------|
| 内能 $U$ | — | $S, V, N$ | $dU = TdS - pdV + \mu dN$ |
| 自由能 $F$ | $U - TS$ | $T, V, N$ | $dF = -SdT - pdV + \mu dN$ |
| Gibbs $G$ | $U - TS + pV$ | $T, p, N$ | $dG = -SdT + Vdp + \mu dN$ |
| 焓 $H$ | $U + pV$ | $S, p, N$ | $dH = TdS + Vdp + \mu dN$ |

> **Feynman 的强调**（Vol 1 Ch 44-46）：热力学势的选择取决于实验条件。恒温恒压用 $G$，恒温恒容用 $F$——平衡态对应势的极小值。

### 1.3 卡诺循环与效率

理想卡诺热机（两个等温 + 两个绝热）：

$$\eta_{\text{Carnot}} = 1 - \frac{T_C}{T_H}$$

这是所有热机的**效率上限**——第二定律的直接后果。

> **Order-of-magnitude（Ph 101 风格）**：发电厂蒸汽温度 $T_H \approx 600\,\text{K}$，冷凝 $T_C \approx 300\,\text{K}$，$\eta_{\max} = 50\%$。实际发电效率 $\sim 35$–$40\%$——已经很接近卡诺极限。

---

## §2 系综理论

### 2.1 微正则系综（NVE）

孤立系统，能量固定在 $E \sim E + \delta E$。

**等概率原理**：所有可达微观态等概率。

$$S = k_B \ln \Omega(N, V, E)$$

温度定义（拉格朗日乘子）：

$$\frac{1}{T} = \left(\frac{\partial S}{\partial E}\right)_{V,N} = k_B \frac{\partial \ln \Omega}{\partial E}$$

### 2.2 正则系综（NVT）

系统与热库 $T$ 接触。概率分布（玻尔兹曼因子）：

$$P_i = \frac{e^{-\beta E_i}}{Z}, \qquad \beta = \frac{1}{k_BT}$$

**配分函数**：

$$Z = \sum_i e^{-\beta E_i}$$

所有热力学量从 $Z$ 导出：

$$F = -k_BT \ln Z, \qquad U = -\frac{\partial \ln Z}{\partial \beta}, \qquad S = k_B(\ln Z + \beta U)$$

$$p = \frac{1}{\beta}\frac{\partial \ln Z}{\partial V}$$

> **核心洞察**：$Z$ 是统计力学的"生成函数"。一旦知道 $Z$，一切热力学量都可得——这与拉格朗日力学中"一旦知道 $\mathcal{L}$，一切运动方程都可得"是平行的。

### 2.3 巨正则系综（μVT）

系统与粒子库+热库接触。概率：

$$P_{i,N} = \frac{e^{-\beta(E_i - \mu N)}}{\mathcal{Z}}$$

**巨配分函数**：

$$\mathcal{Z} = \sum_{N=0}^{\infty} \sum_i e^{-\beta(E_i - \mu N)} = \sum_{N=0}^{\infty} z^N Z_N$$

其中 $z = e^{\beta\mu}$ 是逸度。

### 2.4 经典极限：相空间表述

$N$ 个经典粒子的配分函数：

$$Z_N = \frac{1}{N! h^{3N}} \int d^{3N}\mathbf{p}\, d^{3N}\mathbf{r}\; e^{-\beta H(\mathbf{p}, \mathbf{r})}$$

$1/N!$ 是 Gibbs 修正因子（粒子不可分辨）——没有它会导致 Gibbs 悖论（混合同种气体表观熵增 $\neq 0$）。

---

## §3 量子统计

### 3.1 两种统计

| 统计 | 粒子 | 占据数 | 分布函数 |
|------|------|--------|---------|
| Bose-Einstein | 玻色子（整数自旋）| $n_k = 0, 1, 2, \ldots$ | $\langle n_k \rangle = \frac{1}{e^{\beta(\epsilon_k - \mu)} - 1}$ |
| Fermi-Dirac | 费米子（半整数自旋）| $n_k = 0, 1$ | $\langle n_k \rangle = \frac{1}{e^{\beta(\epsilon_k - \mu)} + 1}$ |
| Maxwell-Boltzmann | 经典极限 | — | $\langle n_k \rangle \approx e^{-\beta(\epsilon_k - \mu)}$ |

> **Townsend/Sakurai 的联系**：自旋统计定理——整数自旋的粒子是玻色子（光子、He-4 原子），半整数自旋的是费米子（电子、质子、He-3 原子）。这在量子场论中才能严格证明。

### 3.2 黑体辐射（Bose-Einstein 光子气）

光子数不守恒 $\Rightarrow \mu = 0$。

光子气配分函数 $\Rightarrow$ Planck 分布：

$$u(\nu) = \frac{8\pi h\nu^3}{c^3}\frac{1}{e^{h\nu/k_BT} - 1}$$

总能量密度（Stefan-Boltzmann）：

$$u = aT^4, \qquad a = \frac{\pi^2 k_B^4}{15\hbar^3 c^3}$$

> **历史意义**：Planck 1900 年为拟合黑体辐射曲线引入了能量量子化 $E = h\nu$——这是量子力学的起点。Caltech 的 Feynman Vol 1 Ch 41 "The Brownian Movement" 把涨落和量子涨落统一在统计物理框架中。

### 3.3 白矮星与中子星：费米简并压

> **LIGO/Thorne 关联**：LIGO 探测到的双中子星并合（GW170817）涉及中子星的物态方程。中子星之所以不塌缩成黑洞，是因为**中子费米简并压**支撑——这是 Fermi-Dirac 统计的极端应用。

零温费米气体：电子填满到费米能 $E_F$。

费米能：$E_F = \frac{\hbar^2}{2m}\left(3\pi^2 n\right)^{2/3}$

简并压：

$$P = \frac{2}{5}nE_F = \frac{\hbar^2}{5m}(3\pi^2)^{2/3} n^{5/3}$$

**白矮星**：电子简并压支撑（Chandrasekhar 极限 $1.44\,M_\odot$）。

**中子星**：电子简并压不够 → 电子俘获 → 中子简并压支撑。

---

## §4 相变

### 4.1 Ising 模型

一维链上 $N$ 个自旋 $s_i = \pm 1$，近邻相互作用：

$$H = -J\sum_{\langle i,j \rangle} s_i s_j - h\sum_i s_i$$

- **1D Ising**：$T_c = 0$（无有限温相变，Landau 1936 用此教学生涨落摧毁长程序）
- **2D Ising**：Onsager 1944 精确解，$T_c = 2J/(k_B \ln(1+\sqrt{2}))$，有相变

> **Onsager 解的意义**：这是第一个**精确求解**的相变模型。它证明了序参量可以连续但不可导——即二级相变——而不需要平均场近似。Caltech 的 Ph 127 会详细推导。

### 4.2 临界指数与标度律

在 $T_c$ 附近，各物理量以幂律发散/消失：

| 指数 | 定义 | 平均场 | 2D Ising（精确）| 3D Ising（数值）|
|------|------|--------|---------------|----------------|
| $\alpha$ | $C \sim |t|^{-\alpha}$ | 0 (jump) | 0 (log) | 0.110 |
| $\beta$ | $M \sim |t|^{\beta}$ | 1/2 | 1/8 | 0.326 |
| $\gamma$ | $\chi \sim |t|^{-\gamma}$ | 1 | 7/4 | 1.237 |
| $\delta$ | $M \sim h^{1/\delta}$ ($T=T_c$) | 3 | 15 | 4.789 |

其中 $t = (T-T_c)/T_c$。

> **反直觉**：平均场理论给出的指数**全部错误**（除了 $\alpha$ 巧合）。原因是平均场忽略了涨落——而临界点附近涨落恰恰最重要（关联长度发散）。重整化群（Wilson 1971, 1982 诺奖）才能正确解释这些指数。

### 4.3 涨落-耗散定理

> **LIGO 的直接应用**：LIGO 悬镜的热噪声谱由涨落-耗散定理决定。

$$\langle x^2 \rangle_\omega = \frac{2k_BT}{\omega}\,\text{Im}\,\chi(\omega)$$

其中 $\chi(\omega)$ 是机械响应函数（ susceptibility）。温度越高 → 涨落越大 → 噪声越大。LIGO 需要**冷却**镜子来降低热噪声——但量子极限（散粒噪声）又设了下限。这个经典-量子噪声的权衡是 LIGO 设计的核心物理。

---

## Python 演示：配分函数 + Ising 模型 Monte Carlo

```python
"""
Caltech Ph 2c / Ph 127 Demo: 统计物理两个核心计算
1. 理想气体的正则配分函数 → 验证内能均分定理
2. 2D Ising 模型 Monte Carlo → 观测相变
纯标准库零依赖，bash 可直接跑通。
"""
import math
import random

# ══════════════════════════════════════════════
# 1. 理想气体配分函数与均分定理
# ══════════════════════════════════════════════
print("=== 理想气体正则配分函数 ===\n")

# 单粒子配分函数: Z₁ = V/λ³_T,  λ_T = h/√(2πmkT)
# N 粒子: Z_N = Z₁^N / N!
# 内能: U = -∂lnZ/∂β = 3/2 NkT (均分定理)

kB = 1.0  # 归一化

def partition_function_single(T, V=1.0, m=1.0, h=1.0):
    """单粒子配分函数 Z₁ = V/λ_T³"""
    lambda_T = h / math.sqrt(2 * math.pi * m * kB * T)
    return V / lambda_T**3

# 验证 U = (3/2)NkT
print("温度扫描: 内能/粒子 应 ≈ 1.5 kT（均分定理）")
print(f"{'T':>6s} {'U/(NkT)':>10s} {'理论=1.5':>10s}")
for T in [0.5, 1.0, 2.0, 5.0, 10.0]:
    Z1 = partition_function_single(T)
    # U = -∂lnZ/∂β, 数值微分
    dT = 0.001
    Z1_plus = partition_function_single(T + dT)
    Z1_minus = partition_function_single(T - dT)
    # lnZ 对 T 求导: dlnZ/dT = (1/Z)dZ/dT
    # U = kT² dlnZ/dT
    dlnZ_dT = (math.log(Z1_plus) - math.log(Z1_minus)) / (2*dT)
    U_per_N = kB * T**2 * dlnZ_dT
    print(f"{T:6.1f} {U_per_N/(kB*T):10.4f} {'1.5000':>10s}")
print("→ 每个自由度贡献 1/2 kT，3 个平动自由度 = 3/2 kT ✓\n")

# ══════════════════════════════════════════════
# 2. 2D Ising 模型 Metropolis Monte Carlo
# ══════════════════════════════════════════════
print("=== 2D Ising 模型 Monte Carlo ===\n")

L = 10          # 格点 L×L（增大 L → 相变更尖锐，但变慢）
J = 1.0         # 耦合常数
N_equil = 500   # 平衡步数
N_sample = 1000 # 采样步数

def init_lattice():
    """随机初始化"""
    return [[random.choice([-1, 1]) for _ in range(L)] for _ in range(L)]

def energy_site(s, i, j):
    """单个自旋与近邻的相互作用能"""
    e = 0.0
    for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
        ni, nj = (i+di)%L, (j+dj)%L  # 周期边界
        e -= J * s[i][j] * s[ni][nj]
    return e

def magnetization(s):
    total = sum(s[i][j] for i in range(L) for j in range(L))
    return total / (L*L)

def metropolis_step(s, T):
    """一次 Metropolis sweep"""
    for _ in range(L*L):
        i, j = random.randint(0,L-1), random.randint(0,L-1)
        dE = -2 * energy_site(s, i, j)  # 翻转后的能量变化
        if dE < 0 or random.random() < math.exp(-dE/(kB*T)):
            s[i][j] *= -1

# 温度扫描
Tc_theory = 2*J / (kB * math.log(1 + math.sqrt(2)))
print(f"理论 T_c (Onsager) = {Tc_theory:.4f} J/kB\n")

temperatures = [1.0, 1.5, 2.0, 2.269, 2.5, 3.0, 4.0]
print(f"{'T/(J/kB)':>10s} {'|M|':>8s} {'M²':>8s}")
random.seed(42)

for T in temperatures:
    s = init_lattice()
    # 平衡
    for _ in range(N_equil):
        metropolis_step(s, T)
    # 采样
    mag_list = []
    for _ in range(N_sample):
        metropolis_step(s, T)
        mag_list.append(abs(magnetization(s)))
    avg_M = sum(mag_list)/len(mag_list)
    avg_M2 = sum(m*m for m in mag_list)/len(mag_list)
    print(f"{T:10.3f} {avg_M:8.4f} {avg_M2:8.4f}")

print(f"\n→ T < T_c 时 |M| ≈ 1（有序铁磁相）")
print(f"→ T > T_c 时 |M| ≈ 0（无序顺磁相）")
print(f"→ T ≈ T_c = {Tc_theory:.3f} 时磁化强度急剧下降（相变）")
print(f"\n注意: 有限尺寸 L={L} 会平滑相变。增大 L → 更尖锐的转变。")
```

---

## 习题

### 基础题（Reif / Kittel & Kroemer 级别）

**P1.** 推导理想气体的熵（Sackur-Tetrode 方程）：

$$S = Nk_B\left[\ln\left(\frac{V}{N}\left(\frac{4\pi mU}{3Nh^2}\right)^{3/2}\right) + \frac{5}{2}\right]$$

证明它满足第三定律 $T \to 0$ 时 $S \to 0$ 的条件（实际上理想气体的经典公式在低温失效——量子效应接管）。

**P2.** 证明正则系综中 $\langle E^2\rangle - \langle E\rangle^2 = k_BT^2 C_V$。这就是能量涨落与热容的关系——涨落-耗散定理的特例。

**P3.** 用配分函数推导理想气体压强 $pV = Nk_BT$，验证与状态方程一致。

### 进阶题（Pathria / Landau 级别）

**P4.** 理想费米气体零温时的费米能 $E_F$ 和总能量 $U$。证明压强 $P = \frac{2}{3}(U/V)$，并用此估算白矮星的电子简并压。

**P5.** 光子气（Bose-Einstein, $\mu = 0$）：从巨配分函数出发推导 Planck 分布和 Stefan-Boltzmann 定律 $P = \sigma T^4$。

**P6.**（LIGO 关联）用涨落-耗散定理估算 LIGO 悬镜（质量 $m = 40\,\text{kg}$，悬丝品质因子 $Q = 10^6$，共振频率 $f_0 = 1\,\text{Hz}$，温度 $T = 300\,\text{K}$）的热噪声功率谱密度。这是限制 LIGO 灵敏度的主要因素之一。

### 挑战题

**P7.** **2D Ising Onsager 解**：零磁场下，Onsager 1944 年的精确自由能：

$$f = -k_BT\ln\left[2\cosh(2\beta J)\right] - \frac{k_BT}{2\pi}\int_0^\pi \ln\left[\frac{1+\sqrt{1-\kappa^2\sin^2\phi}}{2}\right]d\phi$$

其中 $\kappa = 2\sinh(2\beta J)/\cosh^2(2\beta J)$。证明比热在 $T_c$ 处对数发散（$\alpha = 0$）。

**P8.** 用 Monte Carlo 方法模拟 3D Ising 模型，比较临界指数 $\beta$ 与 2D 精确解（$1/8$）和平均场（$1/2$）的差异。讨论涨落如何改变相变性质。

---

## 知识地图与跨课程联系

```
热力学 (Ph 2c)
    │
    ├──→ 系综理论 (Ph 127)
    │         │
    │    配分函数 Z ──→ 全部热力学量
    │         │
    ├──→ 量子统计 (Ph 127/129)
    │         │
    │    Bose-Einstein → 黑体辐射 / 超流 / Bose-Einstein 凝聚
    │    Fermi-Dirac → 白矮星 / 中子星 / 金属电子气
    │                    │
    │               LIGO 中子星并合 (Caltech/Thorne)
    │
    ├──→ 相变与临界现象 (Ph 129)
    │         │
    │    Ising 模型 → 重整化群 (Wilson) → 凝聚态物理
    │
    └──→ 涨落-耗散定理 ──→ LIGO 热噪声分析
                              │
                         Caltech 的直接应用
```

**关键连接**：
- 配分函数 $\to$ 拉格朗日量（生成函数的类比）
- 系综理论 $\to$ 哈密顿力学的相空间（刘维尔定理）
- 量子统计 $\to$ 量子力学的自旋统计定理
- 相变 $\to$ 量子场论的重整化群
- 涨落-耗散 $\to$ LIGO 噪声分析（Caltech 的工程物理）

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Reif *Fundamentals of Statistical and Thermal Physics* | Ch 3-4（热力学）、Ch 6-7（正则/巨正则）、Ch 9（量子统计）| 最全面的本科-研过渡教材 |
| Pathria & Beale *Statistical Mechanics* 4ed | Ch 3-4（系综）、Ch 7（理想量子气）、Ch 12（相变）| Ph 127/129 研究生标准 |
| Landau & Lifshitz Vol 5 *Statistical Physics* | Ch 1-2（热力）、Ch 3（吉布斯分布）、Ch 8（涨落）| Landau 的绝妙洞察 |
| Kittel & Kroemer *Thermal Physics* 2ed | 全书最简洁的量子统计入门 | 本科推荐补充 |

> **Landau 的话**：*"The enormous usefulness of statistical mechanics comes from the fact that it connects the microscopic world to the macroscopic world."* 从 $10^{23}$ 个分子的微观规律到温度、压强、熵——这是物理学的伟大综合。Caltech 的 LIGO 把统计物理推向极端精密：测量 $10^{-21}$ 量级的时空涨落。

---

*本文件属于 top-physics-courses/caltech-physics Phase 1。对应课程 Ph 2c → Ph 127 → Ph 129。*

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：统计物理研究的是"为什么一堆乱七八糟的分子，集体上却表现得规律有序"——温度、压强、熵都是从 $10^{23}$ 个分子的统计中涌现出来的。
>
> **生活类比**：想象一个巨大的硬币盒，里面 100 万枚硬币。你无法预测任何一枚硬币是正是反，但你**确定**地知道：大约 50 万枚正面、50 万枚反面。这个"大约"就是温度（平均值），偏离它的概率小到可以忽略（这就是熵增）。整个房间不会突然把所有空气挤到角落——不是物理禁止，而是概率太小（$10^{-10^{23}}$）。
>
> **反直觉发现（啊哈时刻）**：
> - **熵不是混乱，而是无知**：$S = k_B\ln\Omega$ 中 $\Omega$ 是你**不知道**系统在哪个微观态的"可能性数目"。熵增 = 你失去信息。Laplace 妖如果在，熵就是常数。
> - **时间之箭来自概率，不是物理定律**：微观牛顿方程是时间可逆的，但宏观上鸡蛋碎了不能复原——纯粹是因为"碎"的状态比"整"的多得不可想象。时间之箭是统计的错觉。
> - **温度是拉格朗日乘子**：$1/T=\partial S/\partial E$——温度不是基本物理量，它是为了"固定平均能量"而引入的数学技巧（和拉格朗日力学中的约束乘子同源）。

---

## 🔗 衔接：从哪来，到哪去

### 前置（你需要先会什么）
- **Ph 1a 力学**：哈密顿力学的相空间——统计物理就建立在相空间上
- **Ph 1c 热力学**：第零/一/二/三定律的宏观经验
- **Ph 2a 量子力学**：量子统计（Bose-Einstein / Fermi-Dirac）的基础
- **Ph 106 概率 + 组合**：配分函数求和需要

### 统计物理的"危机"（为什么需要升级）
- **热力学的局限**：四定律是唯象的，不知"为什么"——熵是什么？温度是什么？
- **解决 → 微观统计**：玻尔兹曼 $S=k_B\ln\Omega$ 给出熵的微观意义，配分函数 $Z$ 统一所有热力学量
- **新危机 1**：经典统计无法解释黑体辐射、比热的低温行为（需要量子化）
- **新危机 2**：平衡态理论成熟，但**非平衡态**（生命、湍流、玻璃）仍是开放前沿
- **新危机 3**：相变中涨落最重要（平均场失效），需要重整化群

### 后续（统计物理通向哪里）
- 量子统计 → **凝聚态**（电子气、声子、超导）、**天体物理**（白矮星、中子星简并压）
- Ising + 重整化群 → **量子场论的相变 / 临界现象**（Wilson）
- 涨落-耗散定理 → **LIGO 热噪声分析**（Caltech/Thorne 的直接应用）
- 非平衡统计 → **机器学习的统计力学**（2024 诺奖 Hopfield 网络！）

---

## 🏭 理论联系实际：5 个应用

1. **LIGO 热噪声极限**（Caltech 旗舰）：悬挂镜的热涨落（Brownian noise）由涨落-耗散定理 $\langle x^2\rangle_\omega=\frac{2k_BT}{\omega}\text{Im}\,\chi(\omega)$ 决定——这是统计物理决定 LIGO 灵敏度上限的直接例子。
2. **白矮星与中子星**：中子星不塌缩靠**中子费米简并压** $P\propto n^{5/3}$——Fermi-Dirac 统计支撑了宇宙中最致密的天体。LIGO GW170817 双中子星并合直接探测到物态方程。
3. **Bose-Einstein 凝聚（BEC）**：1995 年实现，$^{87}$Rb 气体冷到 nK 量级，宏观数量原子凝聚到同一量子态——Bose-Einstein 统计的直观展示。现在用于原子钟、量子模拟。
4. **半导体掺杂与 PN 结**：费米能级位置决定载流子浓度 $n=N_c e^{-(E_c-E_F)/k_BT}$——所有半导体器件的统计物理基础。
5. **机器学习的统计力学**：Hopfield 网络（2024 诺奖）把神经网络当作自旋玻璃 Ising 模型；扩散模型（Diffusion）用非平衡统计物理生成图像——统计物理与 AI 深度融合。

---

## 🔬 最新研究前沿（2024-2026）

1. **2024 诺贝尔物理学奖：Hopfield & Hinton——神经网络的统计力学**（2024-10-08）：John Hopfield（自旋玻璃 Ising 模型类比）和 Geoffrey Hinton（Boltzmann 机）因"用统计物理的基础发现实现机器学习"获奖。这是统计物理反哺 AI 的里程碑，也是 Ph 129 Ising 模型的现代延续。
2. **时间晶体与非平衡相变**（2024-2026 持续）：离散时间晶体（周期性驱动的系统展现出时间平移对称破缺）在 2024-2026 多个实验平台（超冷原子、NV 色心）得到验证——这是平衡态相变概念向非平衡的延伸。Caltech 的 Norman Yao（前 Caltech）是先驱。
3. **LIGO O4 运行的统计噪声分析**（2024-2025）：O4 期间（2024-04 至 2025-01）积累了大量引力波事件，每次探测都依赖统计物理的信号检测理论（匹配滤波 + 噪声统计建模）。[LIGO Caltech GWTC-4.0/5.0, 2025-08/2026-05]
4. **活性物质与自组织**（2024-2026 热点）：鸟群、细菌菌落、细胞骨架——这些"自己会动"的系统违反细致平衡，2024-2025 *Nature Physics* 多篇论文建立了活性物质的非平衡统计力学。
5. **超冷原子量子模拟器**（2024-2026）：用 BEC 模拟 Hubbard 模型、规范理论——2024-2025 多个实验组（包括 Caltech 相关合作）用量子模拟器实现此前无法数值计算的强关联多体物理。

---

## 🗺️ 学习 Roadmap（Caltech 路径）

```
Ph 1c/2c  热力学导论 (Feynman Vol 1 Ch 39-46)  ← Caltech 大一
    │   • 掌握：四定律、卡诺循环、熵的概念
    │   • ✅ 知识检查：解释为什么永动机不可能（用卡诺效率）
    │
    ▼
Ph 2c  统计物理入门 (Schroeder *Thermal Physics*)  ← 大二
    │   • 掌握：玻尔兹曼因子、配分函数、理想气体
    │   • ✅ 知识检查：用 Z 推导 pV=NkT 和 U=3/2 NkT
    │
    ▼
Ph 127abc  统计物理 (Reif, Pathria)  ← 研究生
    │   • 掌握：微正则/正则/巨正则系综、量子统计、涨落-耗散
    │   • ✅ 知识检查：推导 Fermi-Dirac 分布并解释白矮星支撑
    │
    ▼
Ph 129ab  高等统计力学 (Landau Vol 5, Pathria)  ← 研究生
    │   • 掌握：Ising 模型 Onsager 解、重整化群、相变临界指数
    │   • ✅ 知识检查：解释为什么平均场临界指数全错
    │
    ▼
→ Ph 136 凝聚态 (量子统计的应用：能带、超导、声子)
→ LIGO 研究组 (涨落-耗散定理 → 热噪声分析)
→ Ph 237/239 (非平衡统计 → 宇宙学、生物物理)
```

**关键里程碑**：能否用配分函数 $Z$ 一次性推出内能 $U$、熵 $S$、压强 $p$、自由能 $F$，并解释为什么 $Z$ 是统计物理的"生成函数"（类比拉格朗日量），是检验你是否理解统计物理统一性的试金石。Caltech 的 LIGO 把统计物理推到了 $10^{-21}$ 量级的极限。
