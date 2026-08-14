# Topic 04: 统计物理 — 从热力学到相变

> **UC Berkeley 课程映射**：112 (Statistical Physics, Kittel & Kroemer / Reif)
>
> **教材体系**：
> - **主教材**：Kittel & Kroemer "Thermal Physics" 2ed（Berkeley Physics Course 传统）
> - **经典替代**：Reif "Fundamentals of Statistical and Thermal Physics"（Berkeley Physics Course Vol. 5）
> - **入门替代**：Schroeder "Introduction to Thermal Physics"
> - **研究生衔接**：Pathria & Beale "Statistical Mechanics" 4ed

---

## 目录

1. [§1 热力学基础](#1-热力学基础)
2. [§2 系综理论](#2-系综理论)
3. [§3 量子统计](#3-量子统计)
4. [§4 相变与临界现象](#4-相变与临界现象)
5. [§5 Berkeley 特色](#5-berkeley-特色kittel--kroemer-与-reif-传统)
6. [习题集](#习题集)
7. [Python 演示](#python-演示)

---

## §1 热力学基础

### 1.1 热力学四定律

**第零定律**：如果 A 与 B 热平衡，B 与 C 热平衡，则 A 与 C 热平衡。→ 温度的存在性。

**第一定律**（能量守恒）：

$$\boxed{dU = \delta Q - \delta W = TdS - pdV}$$

**第二定律**（熵增）：

$$\Delta S \geq 0 \quad \text{（孤立系统）}$$

$$\boxed{dS \geq \frac{\delta Q}{T}}$$

等号对可逆过程成立。

**第三定律**（Nernst 定理）：$T \to 0$ 时 $S \to 0$（完美晶体的熵趋于零）。

### 1.2 热力学势

| 势 | 定义 | 微分 | 自然变量 |
|----|------|------|----------|
| 内能 $U$ | — | $dU = TdS - pdV$ | $S, V$ |
| 焓 $H$ | $U + pV$ | $dH = TdS + Vdp$ | $S, p$ |
| 自由能 $F$ | $U - TS$ | $dF = -SdT - pdV$ | $T, V$ |
| Gibbs $G$ | $U + pV - TS$ | $dG = -SdT + Vdp$ | $T, p$ |

**Kittel & Kroemer 的直觉**：自由能 $F = U - TS$ 是"有用的"能量——内能减去"浪费"在熵上的部分。系统在恒温恒容下最小化 $F$。

### 1.3 Maxwell 关系

从热力学势的全微分，利用混合偏导对称性 $\partial^2 f/\partial x \partial y = \partial^2 f/\partial y \partial x$：

$$\left(\frac{\partial T}{\partial V}\right)_S = -\left(\frac{\partial p}{\partial S}\right)_V$$

$$\left(\frac{\partial T}{\partial p}\right)_S = \left(\frac{\partial V}{\partial S}\right)_p$$

$$\left(\frac{\partial S}{\partial V}\right)_T = \left(\frac{\partial p}{\partial T}\right)_V$$

$$\left(\frac{\partial S}{\partial p}\right)_T = -\left(\frac{\partial V}{\partial T}\right)_p$$

Maxwell 关系让你用可测量的量（如热膨胀 $\partial V/\partial T$）表达不可测量的量（如 $\partial S/\partial p$）。

---

## §2 系综理论

### 2.1 微正则系综（NVE）

**直觉**：孤立系统的能量固定为 $E$。所有可达的微观态等概率出现。

$$\boxed{P_i = \frac{1}{\Omega(E)}, \quad S = k_B \ln \Omega(E)}$$

其中 $\Omega(E)$ 是能量在 $E$ 附近的微观态数。

这就是 **Boltzmann 墓碑上的公式**——它连接了微观状态数和宏观熵。

### 2.2 正则系综（NVT）

**直觉**：系统与一个大热浴接触，温度 $T$ 固定。系统能量可以涨落，但概率由 Boltzmann 因子决定。

$$\boxed{P_i = \frac{e^{-\beta E_i}}{Z}, \quad Z = \sum_i e^{-\beta E_i}, \quad \beta = \frac{1}{k_B T}}$$

$Z$ 是配分函数——统计力学的"圣杯"。所有热力学量都能从 $Z$ 导出：

$$F = -k_B T \ln Z$$

$$U = -\frac{\partial \ln Z}{\partial \beta}, \qquad S = k_B\left(\ln Z + \beta U\right), \qquad C_V = \frac{\partial U}{\partial T}$$

**Kittel & Kroemer 的核心洞察**：计算 $Z$ 就等于解出了全部热力学。

### 2.3 巨正则系综（μVT）

化学势 $\mu$ 固定，粒子数可变：

$$P_i = \frac{e^{-\beta(E_i - \mu N_i)}}{\mathcal{Z}}, \quad \mathcal{Z} = \sum_{i,N} e^{-\beta(E_i - \mu N)}$$

巨配分函数 $\mathcal{Z}$ 对化学物理和量子统计至关重要。

### 2.4 能量涨落

正则系综中能量涨落：

$$\langle (\Delta E)^2 \rangle = k_B T^2 C_V$$

**反直觉**：宏观系统的相对涨落 $\sqrt{\langle(\Delta E)^2\rangle} / \langle E \rangle \sim 1/\sqrt{N}$——对 $N \sim 10^{23}$ 的系统，涨落完全不可见！这就是为什么微正则和正则系综在热力学极限下给出相同结果。

### 2.5 经典例子：理想气体

$$Z_N = \frac{1}{N!}\left(\frac{V}{\lambda_{\text{th}}^3}\right)^N, \quad \lambda_{\text{th}} = \frac{h}{\sqrt{2\pi m k_B T}}$$

由此导出理想气体状态方程：

$$pV = Nk_B T$$

和熵（Sackur-Tetrode 方程）：

$$S = Nk_B\left[\ln\left(\frac{V}{N\lambda_{\text{th}}^3}\right) + \frac{5}{2}\right]$$

---

## §3 量子统计

### 3.1 Bose-Einstein 与 Fermi-Dirac 分布

**核心问题**：全同粒子的统计与经典不同。整数自旋（玻色子）允许多个粒子占据同一态；半整数自旋（费米子）每个态最多一个粒子（Pauli 不相容）。

$$\boxed{\bar{n}_\epsilon = \frac{1}{e^{\beta(\epsilon - \mu)} \mp 1}}$$

- **玻色子（− 号）**：$n_{\text{BE}}(\epsilon) = \frac{1}{e^{\beta(\epsilon-\mu)} - 1}$
- **费米子（+ 号）**：$n_{\text{FD}}(\epsilon) = \frac{1}{e^{\beta(\epsilon-\mu)} + 1}$
- **经典极限**（$\bar{n} \ll 1$）：$n_{\text{MB}}(\epsilon) = e^{-\beta(\epsilon-\mu)}$（Maxwell-Boltzmann）

### 3.2 黑体辐射（光子气体）

光子是玻色子，化学势 $\mu = 0$（光子数不守恒）。

Planck 分布：

$$u(\nu) = \frac{8\pi h \nu^3}{c^3} \frac{1}{e^{h\nu/k_B T} - 1}$$

总能量密度：

$$u = \frac{\pi^2 k_B^4}{15 \hbar^3 c^3} T^4$$

这就是 **Stefan-Boltzmann 定律** $j = \sigma T^4$ 的统计力学推导。

**反直觉**：经典 Rayleigh-Jeans 公式在高频趋于无穷（紫外灾难）；量子统计自然截断。

### 3.3 Fermi 气体

$T = 0$ 时费米子填满直到 Fermi 能 $\epsilon_F$：

$$\epsilon_F = \frac{\hbar^2}{2m}\left(3\pi^2 n\right)^{2/3}$$

Fermi 温度 $T_F = \epsilon_F / k_B$ 对金属约 $10^4$ K——常温 $T \ll T_F$，电子气几乎是简并的。

**Kittel & Kroemer 的经典应用**：电子气对金属热容的贡献 $\propto T$（而非经典的 $3/2\,k_B$ 常数）——只有 Fermi 面附近的电子被激发，这解释了电子热容远小于经典预期。

### 3.4 Bose-Einstein 凝聚（BEC）

当温度低于临界温度 $T_c$ 时，宏观数量的玻色子凝聚到基态：

$$T_c = \frac{2\pi\hbar^2}{mk_B}\left(\frac{n}{\zeta(3/2)}\right)^{2/3} \approx 3.31\frac{\hbar^2 n^{2/3}}{mk_B}$$

凝聚分数：

$$\frac{N_0}{N} = 1 - \left(\frac{T}{T_c}\right)^{3/2}$$

**反直觉**：BEC 不是相互作用驱动的相变——它是纯量子统计效应！1995 年实验实现（JILA, Cornell & Wieman; MIT, Ketterle），2001 年诺贝尔奖。

---

## §4 相变与临界现象

### 4.1 相变分类

**Ehrenfest 分类**（按自由能导数的奇异性）：
- **一级相变**：自由能一阶导数不连续（如冰→水，有潜热）
- **连续（二级）相变**：自由能一阶导连续，二阶导发散（如铁磁 Curie 点）

### 4.2 Ising 模型

$$\boxed{H = -J\sum_{\langle i,j \rangle} s_i s_j - h\sum_i s_i, \quad s_i = \pm 1}$$

**2D Ising 模型精确解**（Onsager 1944）是统计物理的里程碑——这是相变的最简单精确可解模型！

Onsager 解的关键结果（$h=0$）：

- 临界温度：$k_B T_c = 2J / \ln(1+\sqrt{2}) \approx 2.269J$
- 自发磁化（$T < T_c$）：$M = \left[1 - \sinh^{-4}(2J/k_B T)\right]^{1/8}$

**临界指数** $\beta = 1/8$（而非平均场预言的 $1/2$）——揭示了涨落的重要性。

### 4.3 临界指数与标度律

在临界点附近，各热力学量以幂律发散/消失：

| 量 | 行为 | 临界指数 | 2D Ising 精确值 | 平均场值 |
|----|------|----------|-----------------|----------|
| 磁化 $M$ | $\sim (T_c - T)^\beta$ | $\beta$ | 1/8 | 1/2 |
| 磁化率 $\chi$ | $\sim |T - T_c|^{-\gamma}$ | $\gamma$ | 7/4 | 1 |
| 比热 $C$ | $\sim |T - T_c|^{-\alpha}$ | $\alpha$ | 0 (对数) | 0 (跳跃) |
| 关联长度 $\xi$ | $\sim |T-T_c|^{-\nu}$ | $\nu$ | 1 | 1/2 |

**标度律**（Rushbrooke）：$\alpha + 2\beta + \gamma = 2$

### 4.4 重整化群（Renormalization Group）

**Wilson 的洞察**（1982 诺贝尔奖）：在临界点，系统没有特征尺度——自相似（尺度不变）。重整化群通过逐步粗粒化，跟踪耦合常数在尺度变换下的流动。

对 2D Ising，一次 decimation 后 $K \to K'$：

$$K' = R(K)$$

临界点是不动点 $K^* = R(K^*)$。在不动点附近线性化 $R$ 的本征值给出临界指数。

---

## §5 Berkeley 特色：Kittel & Kroemer 与 Reif 传统

### Berkeley Physics Course 的统计物理双璧

UC Berkeley 在统计物理教学上有两本标志性教材，都属于 Berkeley Physics Course 传统：

#### Kittel & Kroemer "Thermal Physics" 2ed（1980）

**Charles Kittel**（1911-2019），Berkeley 教授（1951-1978），固体物理泰斗。

**Herbert Kroemer**（1928-2024），Berkeley 教授（1976-2012），诺贝尔物理学奖（2000，半导体异质结）。

这本教材的特色：

1. **从统计出发**：不先讲热力学再讲统计（如 Reif 的传统），而是直接从微观统计推导宏观规律。第一章就是 Counting States。
2. **化学势 $\mu$ 的核心地位**：K&K 反复强调化学势作为"粒子逃逸趋势"的物理直觉，用 $\mu$ 统一处理半导体、BEC、化学平衡。
3. **物理图像丰富**：大量实际应用（半导体能带、白矮星、BEC、热机效率）穿插理论推导。

Berkeley 112 课程至今以此为核心教材。

#### Reif "Fundamentals of Statistical and Thermal Physics"（1965）

**F. Reif**，Berkeley 教授。这是 Berkeley Physics Course Vol. 5。

特色：
1. **传统路线**：热力学 → 动力学理论 → 系综理论，层层递进。
2. **数学严谨**：概率论基础扎实，涨落理论详尽。
3. **篇幅大**（近900页），适合深入参考。

两本教材对比：

| 方面 | Kittel & Kroemer | Reif |
|------|-----------------|------|
| 结构 | 统计→热力学 | 热力学→统计 |
| 化学势 | 核心工具 | 后期才引入 |
| 物理应用 | 穿插各章 | 集中在后半部 |
| 适合 | 物理主修，快速上手 | 深入理解，参考查阅 |

### Berkeley 统计物理研究前沿

Berkeley 在统计物理相关领域的研究优势连接到 112 课程内容：

| Berkeley 112 内容 | 研究前沿连接 |
|-------------------|-------------|
| 量子统计 | 冷原子量子模拟（Berkeley Dan Stamper-Kurn 组）|
| BEC | 量子气体（Berkeley Norman Yao 组） |
| 相变 | 凝聚态临界现象（Berkeley Ashvin Vishwanath 组）|
| 涨落定理 | 非平衡统计力学（Berkeley bio-physics） |
| 熵与信息 | 量子信息热力学 |

---

## 习题集

### 基础题（热力学）

**习题 4.1**：理想气体等温膨胀（$V_1 \to V_2$）。求 $\Delta S$, $\Delta U$, $Q$, $W$。
> **解**：$\Delta S = nR\ln(V_2/V_1)$，$\Delta U = 0$（理想气体等温），$Q = W = nRT\ln(V_2/V_1)$。

**习题 4.2**：证明 $C_p - C_V = nR$（理想气体）。
> **提示**：$C_p - C_V = T(\partial p/\partial T)_V (\partial V/\partial T)_p$，代入 $pV = nRT$。

**习题 4.3**（K&K 风格）：用 Maxwell 关系证明焦耳-汤姆孙系数 $\mu_{JT} = (\partial T/\partial p)_H = \frac{1}{C_p}\left[T(\partial V/\partial T)_p - V\right]$。

### 中级题（系综理论）

**习题 4.4**：计算二维谐振子的配分函数 $Z$（频率 $\omega$），并求 $U$ 和 $C_V$。
> **解**：$Z = \left[\frac{1}{2\sinh(\beta\hbar\omega/2)}\right]^2$。$U = \hbar\omega \coth(\beta\hbar\omega/2)$。高温 $C_V \to 2k_B$，低温 $C_V \to 0$。

**习题 4.5**（K&K 3.5）：$N$ 个自旋 1/2 在磁场 $B$ 中。求配分函数和磁化强度 $M = N\mu \tanh(\beta\mu B)$。验证居里定律 $\chi \propto 1/T$（高温极限）。

**习题 4.6**（Reif 风格）：证明正则系综中的能量涨落 $\langle(\Delta E)^2\rangle = k_B T^2 C_V$。

### 挑战题

**习题 4.7**（BEC 临界温度）：推导自由玻色气体 BEC 临界温度 $T_c = \frac{2\pi\hbar^2}{mk_B}\left(\frac{n}{\zeta(3/2)}\right)^{2/3}$。
> **提示**：在三维中，激发态粒子数 $\int_0^\infty g(\epsilon) n_{\text{BE}}(\epsilon)\, d\epsilon$ 在 $\mu \to 0$ 时有限。令此积分等于 $N$ 求解 $T_c$。

**习题 4.8**（Ising 平均场）：用平均场近似推导 1D 和 2D Ising 模型的临界温度 $k_B T_c^{MF} = zJ$（$z$ = 配位数），并与 2D 精确解 $T_c \approx 2.269J/k_B$ 比较。
> **解**：2D 方格 $z=4$，平均场 $T_c^{MF} = 4J/k_B$，精确解 $T_c \approx 2.269J/k_B$。平均场高估 76%。

**习题 4.9**（Onsager 解导引）：写出 2D Ising 模型无外场时的配分函数 $Z = \sum_{\{s_i\}} e^{\beta J \sum s_i s_j}$，说明为什么一维没有有限温相变而二维有。
> **提示**：用 Peierls 论证——低温下界面（domain wall）的自由能代价在二维正，在三维更高维也正；一维下界面无代价。

---

## Python 演示

### 演示 1：2D Ising 模型 Monte Carlo 模拟

```python
"""
2D Ising 模型 Monte Carlo — Berkeley 112
Metropolis 算法，模拟相变。
纯 NumPy 实现，约 30 秒跑完。
"""
import numpy as np
import matplotlib.pyplot as plt

def metropolis_ising(L=20, T_vals=None, n_eq=2000, n_mc=4000):
    """
    Metropolis Monte Carlo 模拟 2D Ising 模型。
    L: 格点边长, T_vals: 温度列表, J=1, kB=1。
    """
    if T_vals is None:
        T_vals = np.linspace(1.5, 3.5, 21)

    J = 1.0
    magnetizations = []
    susceptibilities = []
    energies = []
    specific_heats = []

    for T in T_vals:
        beta = 1.0 / T
        # 随机初始构型
        spins = np.random.choice([-1, 1], size=(L, L))

        M_list = []
        E_list = []

        for step in range(n_eq + n_mc):
            # 随机选一个格点翻转
            i, j = np.random.randint(0, L, 2)
            s = spins[i, j]
            # 周期性边界条件的邻居和
            nb = (spins[(i+1)%L, j] + spins[(i-1)%L, j] +
                  spins[i, (j+1)%L] + spins[i, (j-1)%L])
            dE = 2 * J * s * nb

            if dE < 0 or np.random.random() < np.exp(-beta * dE):
                spins[i, j] = -s

            if step >= n_eq:
                M = np.abs(np.mean(spins))
                E = -J * np.sum(spins * (
                    np.roll(spins, 1, axis=0) + np.roll(spins, -1, axis=0) +
                    np.roll(spins, 1, axis=1) + np.roll(spins, -1, axis=1)
                )) / 2  # 每对计数两次
                M_list.append(M)
                E_list.append(E)

        M_arr = np.array(M_list)
        E_arr = np.array(E_list)

        magnetizations.append(np.mean(M_arr))
        susceptibilities.append(beta * L**2 * (np.mean(M_arr**2) - np.mean(M_arr)**2))
        energies.append(np.mean(E_arr) / L**2)
        specific_heats.append(beta**2 * L**2 * (np.mean(E_arr**2) - np.mean(E_arr)**2) / L**2)

    return (T_vals, np.array(magnetizations), np.array(susceptibilities),
            np.array(energies), np.array(specific_heats))


# --- 运行模拟 ---
print("Running Monte Carlo (this takes ~30s)...")
T, M, chi, E, Cv = metropolis_ising(L=16, n_eq=1000, n_mc=2000)
Tc_exact = 2.0 / np.log(1 + np.sqrt(2))  # Onsager 精确解

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

ax = axes[0, 0]
ax.plot(T, M, 'bo-', markersize=4)
ax.axvline(Tc_exact, color='r', linestyle='--', label=f'$T_c$ = {Tc_exact:.3f} (Onsager)')
ax.set_xlabel('Temperature (T)')
ax.set_ylabel('Magnetization |M|')
ax.set_title('Spontaneous Magnetization')
ax.legend()

ax = axes[0, 1]
ax.plot(T, chi, 'rs-', markersize=4)
ax.axvline(Tc_exact, color='r', linestyle='--', alpha=0.5)
ax.set_xlabel('Temperature (T)')
ax.set_ylabel('Susceptibility χ')
ax.set_title('Magnetic Susceptibility (diverges at $T_c$)')

ax = axes[1, 0]
ax.plot(T, E, 'g^-', markersize=4)
ax.axvline(Tc_exact, color='r', linestyle='--', alpha=0.5)
ax.set_xlabel('Temperature (T)')
ax.set_ylabel('Energy per site')
ax.set_title('Internal Energy')

ax = axes[1, 1]
ax.plot(T, Cv, 'mD-', markersize=4)
ax.axvline(Tc_exact, color='r', linestyle='--', alpha=0.5)
ax.set_xlabel('Temperature (T)')
ax.set_ylabel('Specific heat $C_V$')
ax.set_title('Specific Heat (peak at $T_c$)')

plt.suptitle('2D Ising Model: Phase Transition at $T_c \\approx 2.269$\n(Monte Carlo L=16, Onsager exact Tc shown)', fontsize=13)
plt.tight_layout()
plt.savefig('ising_phase_transition.png', dpi=150)
plt.show()
print(f"\nOnsager Tc = {Tc_exact:.4f}")
print(f"Peak susceptibility at T = {T[np.argmax(chi)]:.2f}")
print("Note: finite L shifts and rounds the transition (finite-size effects)")
```

### 演示 2：Boltzmann 分布与 Maxwell-Boltzmann 速度分布

```python
"""
Boltzmann 分布可视化 — Berkeley 112
1. 粒子能量分布 = Boltzmann
2. Maxwell-Boltzmann 速度分布
3. 不同温度对比
"""
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 能级占据数（二能级系统） ---
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

ax = axes[0]
delta = 1.0  # 能级间隔 (归一化)
T_vals = [0.5, 1.0, 2.0, 5.0]
x = np.linspace(0, 4, 200)

for T in T_vals:
    # P(ε) ∝ exp(-ε/kT)
    P = np.exp(-x / T)
    P /= np.trapz(P, x)
    ax.plot(x, P, linewidth=2, label=f'T = {T} (kT/Δ = {T/delta:.1f})')

ax.set_xlabel('Energy ε (units of Δ)')
ax.set_ylabel('Probability')
ax.set_title('Boltzmann Distribution\n(high T → flat; low T → ground state)')
ax.legend()

# --- 2. Maxwell-Boltzmann 速度分布 ---
ax = axes[1]
m = 1.0  # 归一化质量
kB = 1.0

for T in [0.5, 1.0, 2.0]:
    v = np.linspace(0, 6, 300)
    f_v = 4 * np.pi * (m / (2 * np.pi * kB * T))**1.5 * v**2 * np.exp(-m * v**2 / (2 * kB * T))
    ax.plot(v, f_v, linewidth=2, label=f'T = {T}')
    vp = np.sqrt(2 * kB * T / m)  # 最概然速率
    ax.axvline(vp, color='gray', linestyle=':', alpha=0.5)

ax.set_xlabel('Speed v')
ax.set_ylabel('f(v)')
ax.set_title('Maxwell-Boltzmann Speed Distribution\n(dotted = most probable speed)')
ax.legend()

# --- 3. Fermi-Dirac vs Bose-Einstein vs Boltzmann ---
ax = axes[2]
epsilon = np.linspace(-2, 4, 300)
mu = 0.0
T = 0.5
beta = 1.0 / T

n_FD = 1.0 / (np.exp(beta * (epsilon - mu)) + 1)
n_BE = 1.0 / (np.exp(beta * (epsilon - mu)) - 1)
n_BE = np.maximum(n_BE, 0)  # 避免 ε < μ 的发散
n_MB = np.exp(-beta * (epsilon - mu))

ax.plot(epsilon, n_FD, 'b-', linewidth=2, label='Fermi-Dirac')
ax.plot(epsilon, n_BE, 'r-', linewidth=2, label='Bose-Einstein')
ax.plot(epsilon, n_MB, 'g--', linewidth=2, label='Maxwell-Boltzmann')
ax.axvline(mu, color='gray', linestyle=':', alpha=0.5, label='μ')
ax.set_xlabel('Energy ε')
ax.set_ylabel('⟨n(ε)⟩')
ax.set_title(f'Quantum Distributions (T={T}, μ={mu})')
ax.set_ylim(0, 3)
ax.legend()

plt.tight_layout()
plt.savefig('boltzmann_distributions.png', dpi=150)
plt.show()
print("Key: FD ≤ 1 (Pauli), BE diverges at ε=μ (BEC), MB is classical limit")
```

### 演示 3：Bose-Einstein 凝聚模拟

```python
"""
BEC 凝聚分数 vs 温度 — Berkeley 112
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import zeta

# 归一化温度 T/Tc
t_ratio = np.linspace(0.01, 1.5, 300)

# 凝聚分数 N₀/N = 1 - (T/Tc)^{3/2}  for T < Tc
N0_fraction = np.where(t_ratio < 1, 1 - t_ratio**1.5, 0)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
ax.plot(t_ratio, N0_fraction, 'b-', linewidth=2.5)
ax.axvline(1.0, color='r', linestyle='--', alpha=0.5, label='$T = T_c$')
ax.fill_between(t_ratio[t_ratio < 1], N0_fraction[t_ratio < 1], alpha=0.15, color='blue')
ax.set_xlabel('$T / T_c$')
ax.set_ylabel('$N_0 / N$ (condensate fraction)')
ax.set_title('Bose-Einstein Condensation\n$N_0/N = 1 - (T/T_c)^{3/2}$')
ax.legend()
ax.set_ylim(-0.05, 1.05)

# 激发态粒子分布（不同温度）
ax = axes[1]
epsilon = np.linspace(0.001, 5, 300)
for t_r, label in [(0.3, '$T=0.3T_c$'), (0.7, '$T=0.7T_c$'), (1.5, '$T=1.5T_c$')]:
    if t_r < 1:
        mu = 0  # BEC 时 μ ≈ 0
    else:
        mu = -0.5  # T > Tc 时 μ < 0
    beta = 1.0 / t_r
    n_exc = 1.0 / (np.exp(beta * (epsilon - mu)) - 1)
    ax.plot(epsilon, n_exc, linewidth=2, label=label)

ax.set_xlabel('Energy ε')
ax.set_ylabel('$n_{BE}(ε)$')
ax.set_title('Bose-Einstein Occupation\n(ground state macroscopic below $T_c$)')
ax.set_ylim(0, 5)
ax.legend()

plt.tight_layout()
plt.savefig('bec.png', dpi=150)
plt.show()
print(f"ζ(3/2) = {zeta(1.5):.4f}  (appears in T_c formula)")
print(f"T_c ∝ n^(2/3) / m  (lighter + denser → higher Tc)")
```

---

## 学习路径建议

```
112 (Kittel & Kroemer Ch 1-6)  →  热力学 + 经典统计 + 系综
      ↓
112 (K&K Ch 7-9 或 Reif)      →  量子统计 + 黑体辐射 + Fermi/Bose 气体
      ↓
研究生 (Pathria Ch 7-12)       →  相变 + 重整化群 + 非平衡统计
```

**Kittel & Kroemer 教材学习节奏**（Berkeley 112 一学期 15 周）：
- 周 1-3：Ch 1-2（态计数 + 熵 + 温度）
- 周 4-5：Ch 3-4（化学势 + 热力学势）
- 周 6-8：Ch 5-6（理想气体 + 正则系综）
- 周 9-11：Ch 7-8（Fermi 气体 + Bose 气体）
- 周 12-13：Ch 9（黑体辐射 + 声子）
- 周 14-15：相变专题（Ising 模型，补充材料）

---

> **文件信息**：Berkeley Physics · Topic 04 Statistical Physics · 2026-08-12
> 
> **教材交叉引用**：Kittel & Kroemer (112) / Reif (BPC Vol.5) / Schroeder (入门替代) / Pathria (研究生)

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：统计物理研究"一大堆粒子整体怎么行为"——单个分子的运动是混沌的、不可预测的，但 $10^{23}$ 个分子组成的气体却精确遵守温度、压强等简单规律。少即是混沌，多反而有序！
>
> **生活类比**：想象一个巨型体育场里有十万个观众。你想预测某个人什么时候去厕所——不可能。但你可以精确预测"下午 3 点有 3427 个人在排队"——这就是统计规律。温度就是分子的平均动能（"大家跑得多快"），压强就是分子撞壁的总力（"大家推墙推多猛"），熵就是混乱程度（"房间有多乱"）。
>
> **反直觉发现**：
> - **熵增 = 时间箭头**：打破的杯子不会自动复原——不是因为力学定律禁止（它是时间反演对称的！），而是因为"碎片→杯子"的概率小到荒谬。时间的方向不是来自基本物理定律，而是来自概率和巨大粒子数。
> - **麦克斯韦妖的悖论**：一个假想的小妖精能筛选快慢分子，似乎能违反第二定律。解决这个悖论花了 100 年——"擦除信息"本身需要消耗能量（Landauer 原理），信息和能量是等价的！
> - **玻色-爱因斯坦凝聚(BEC)**：把原子冷却到纳开尔文温度，它们会"凝聚"到同一个量子态——像一个军团齐步走。1995 年实验实现，2001 年诺贝尔奖。
> - **相变是涌现的**：单个水分子没有"沸腾"的概念。但当温度到 100°C，$10^{23}$ 个分子集体改变了行为——这是"涌现"（emergence）的典型例子，整体大于部分之和。

---

## 🔗 衔接：从哪来，到哪去

### 前置知识
- **Topic 01 经典力学**：哈密顿力学 → 相空间 → Liouville 定理（统计物理的数学基础）
- **Topic 02 电磁学**：黑体辐射问题 → 普朗克量子假设（统计物理的催化剂）
- **Topic 03 量子力学**：全同粒子 → Fermi-Dirac / Bose-Einstein 统计；能级 → 配分函数
- **概率论**：组合数学（状态计数）、概率分布

### 本主题解决了什么危机
- **热力学的微观基础**（Boltzmann 1877）：热力学定律（宏观经验规律）为什么成立？Boltzmann 证明 $S = k_B \ln W$——熵就是微观状态数的对数。宏观的热力学是微观粒子统计行为的涌现。
- **时间箭头之谜**：基本物理定律（牛顿/麦克斯韦/薛定谔）都是时间反演对称的——为什么时间只朝一个方向流？答案在统计物理：熵增定律是概率性的，不是绝对的，但对宏观系统概率如此之高以至于等于确定性。
- **黑体辐射公式**：Planck 用统计物理（能量量子化假设）推导出了与实验完美吻合的黑体辐射公式——这直接催生了量子力学。

### 本主题留下的新危机
- **非平衡态统计物理**：我们理解了平衡态（系综理论），但生命、气候、经济都是远离平衡的耗散结构。Prigogine 的耗散结构理论只是开始——非平衡统计物理仍是开放领域。
- **信息与物理的关系**：Maxwell 妖、Landauer 原理、黑洞信息悖论——信息、熵、能量三者的深层关系尚未完全厘清。
- **相变的普适性**：为什么水沸腾和铁磁转变属于同一个"普适类"？重整化群回答了部分问题，但强关联系统的相变仍是前沿。
- **量子统计的复杂性**：量子多体系统的计算指数困难——这既是凝聚态物理的挑战，也是量子计算的机遇。

### 后续主题
- → **Topic 06 固体物理**：声子（玻色子）的热容(Debye 模型)；电子（费米子）的费米能级和能带
- → **Topic 07 粒子物理**：早期宇宙的统计物理（大爆炸核合成）；夸克-胶子等离子体
- → Berkeley **112→130**：从平衡态到非平衡态，到流体力学和等离子体物理
- → 交叉学科：**化学物理**(化学反应速率) · **生物物理**(蛋白质折叠) · **天体物理**(恒星结构)

---

## 🏭 理论联系实际：5 个应用

1. **热机与制冷（空调/冰箱/热泵）**：卡诺循环定义了热机效率的极限 $\eta = 1 - T_c/T_h$。现代发电厂、汽车引擎、空调都在追求逼近卡诺极限。热泵技术（COP > 3）是碳中和的关键——用 1 度电搬运 3-4 度电的热量。

2. **量子退火与优化计算**：D-Wave 量子退火机利用统计物理的模拟退火原理求解优化问题。Berkeley 的研究组用量子退火解决物流优化、药物分子对接等 NP-hard 问题。

3. **宇宙微波背景辐射(CMB)**：宇宙大爆炸的"余温"是完美的黑体辐射谱（温度 2.725 K）。Planck 卫星以 $10^{-6}$ 精度测量 CMB 的温度涨落——这些涨落记录了宇宙诞生 38 万年时的密度分布。统计物理直接应用于宇宙学。

4. **超导与超流**：液氦的超流（$T < 2.17$ K）和金属的超导都是宏观量子现象——玻色子凝聚到基态。超导磁体用于 MRI、粒子加速器（LHC）、可控核聚变（ITER）。Berkeley LBNL 的材料实验室研究高温超导。

5. **生物物理中的统计力学**：蛋白质折叠遵循能量景观理论（统计力学的 spin glass 模型）；细胞内的分子马达（驱动蛋白、肌球蛋白）是纳米级的热机——用 ATP 的化学能做机械功，效率接近卡诺极限。

---

## 🔬 最新研究前沿（2024-2026）

1. **热力学计算机**（2026-07-15, Quanta Magazine）：一种全新的计算范式——不抵抗热涨落，而是利用它们来做计算。统计力学原理直接驱动计算过程，可能实现全新的高效计算架构。Berkeley 统计物理与计算交叉研究的热点。

2. **量子"温度计"：反常热流检测量子性**（2025-10-01, Quanta Magazine）："反常"热流——初看违反热力学第二定律的现象——提供了一种不破坏量子纠缠就能检测它的方法。这架起了量子力学与统计力学的深层桥梁，可能催生新型量子传感器。

3. **量子"干扰"（Jamming）探索基本原理**（2026-04-17, Quanta Magazine）：重新发现的量子干扰概念探索了即使量子力学规则不成立时消息保密的可能性，涉及信息论与统计物理的深层交叉。

4. **主动物质（Active Matter）物理**（2024-2025）：鸟群、细菌群落、细胞骨架——这些"自驱动粒子"系统打破传统平衡统计物理的框架。Berkeley 的物理生物组研究细菌湍流和活性胶体的非平衡相变，开辟"物质第四态"的新领域。

5. **机器学习驱动的相变发现**（2024-2025）：用神经网络从蒙特卡洛模拟数据中自动发现相变和序参量。Berkeley 的 Simone Zagorac 等人用深度学习识别强关联电子系统的隐藏相，加速新材料发现。

---

## 🗺️ 学习 Roadmap（Berkeley 路径）

```
高中物理 / AP Physics (热学部分)
      ↓
 7A — Physics for Scientists and Engineers (Tipler)
      │  温度 · 热膨胀 · 热力学第一定律 · 气体动理论入门
      │  ✅ 知识检查：能否用分子运动论推导理想气体状态方程 PV=nRT？
      ↓
 112 — Statistical Physics (Kittel & Kroemer / Reif)
      │  热力学(四大定律) · 熵与信息 · 系综理论(微正则/正则/巨正则)
      │  · 经典统计(麦克斯韦-玻尔兹曼) · 量子统计(Fermi-Dirac/Bose-Einstein)
      │  · 黑体辐射 · 声子 · 相变入门
      │  ✅ 知识检查：能否推导玻色-爱因斯坦凝聚温度 Tc？能否解释费米能级的物理意义？
      ↓
 130 — Thermal and Statistical Physics (进阶)
      │  非平衡热力学 · 相变与重整化群 · 涨落-耗散定理
      │  ✅ 知识检查：能否用重整化群解释相变的普适性？
      ↓
 研究生 (Pathria) — 高级统计物理
      │  临界现象 · 伊辛模型精确解 · 非平衡统计 · 量子统计力学
      ↓
 研究前沿 → 主动物质 · 量子热力学 · 生物物理 · 宇宙学
```

**核心教材节奏**：
| 阶段 | 教材 | 周数 | 核心概念 |
|------|------|------|----------|
| 7A | Tipler Ch 15-20 | 5 周 | 热学基础 |
| 112 | Kittel & Kroemer 全书 | 15 周 | 统计物理 |
| 研究生 | Pathria Ch 7-12 | — | 相变 + 非平衡 |

**费曼学习法检查点**：
- [ ] 能否用白话解释"为什么熵总是增加"？（概率论证，不是物理定律！）
- [ ] 能否解释 Maxwell 妖为什么不能违反第二定律？（Landauer 原理）
- [ ] 能否区分费米子和玻色子的统计行为，并各举一个日常例子？
- [ ] 能否解释为什么绝对零度不可达到？（量子零点能 + 热力学第三定律）
