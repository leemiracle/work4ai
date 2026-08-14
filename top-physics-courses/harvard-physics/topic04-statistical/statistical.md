# Harvard 统计与热物理 — Phys 165 / 166

> **课程**：Phys 165 (Thermodynamics) · Phys 166 (Statistical Mechanics)
> **教材**：Schroeder *Introduction to Thermal Physics* (2000) · Reif *Fundamentals of Statistical and Thermal Physics* (1965)
> **一手来源**：[Harvard Physics Catalog](https://www.physics.harvard.edu/academics/courses)（2026-08 核实）

---

## 🎓 Harvard 特色：从微观到宏观的桥梁

Harvard 的 Phys 165/166 序列采用 **"Schroeder 入门 → Reif 深化"** 的两级火箭策略：

- **Phys 165 (Schroeder)**：从分子动理论出发，先建立热力学的"分子图像"，让学生理解**为什么**热力学定律成立。Schroeder 的特色是"少即是多"——全书仅 400 页，但每个概念都用**最简单的模型**讲透（如用 Einstein 固体讲熵）。

- **Phys 166 (Reif)**：在 Schroeder 的物理直觉之上，建立严格的**系综理论**框架。Reif 以严密著称，从微正则系综出发推导一切，强调配分函数 $Z$ 作为统计力学的"万能钥匙"。

Schroeder 的教学理念：
> *"Thermodynamics is not a collection of formulas to memorize. It's the art of relating what you can measure to what you want to know."*

---

## 第一部分：热力学（Phys 165, Schroeder Ch.1-3）

### 1.1 热力学第零定律与温度

**第零定律**：若 A 与 B 热平衡，B 与 C 热平衡，则 A 与 C 热平衡。

→ 存在态函数**温度** $T$，热平衡即 $T_A = T_B$。

### 1.2 第一定律（能量守恒）

$$\Delta U = Q - W$$

- $U$：内能（态函数）
- $Q$：系统吸收的热量（过程量）
- $W$：系统对外做功（过程量）

功的表达式（可逆过程）：$dW = P\,dV$

### 1.3 第二定律与熵

**Clausius 不等式**：$\oint \frac{dQ}{T} \leq 0$（任意循环）

→ 存在态函数**熵** $S$，对可逆过程 $dS = dQ/T$。

**第二定律**：孤立系统的熵永不减少：
$$\Delta S_{\text{universe}} \geq 0$$

> 🔑 **Schroeder 的核心洞察**：熵 $S = k_B \ln\Omega$ 度量微观态数。第二定律的本质是**概率**——系统趋向微观态数最多的宏观态。热力学第二定律不是绝对定律，而是统计必然性。

### 1.4 热力学势

通过 Legendre 变换（与哈密顿力学中 $H$ 的定义类比）构造不同的热力学势：

| 势 | 定义 | 自然变量 | 物理意义 |
|----|------|---------|---------|
| 内能 $U$ | — | $S, V, N$ | 总能量 |
| 焓 $H$ | $U + PV$ | $S, P, N$ | 等压过程的热 |
| 自由能 $F$ | $U - TS$ | $T, V, N$ | 等温过程的最大功 |
| Gibbs $G$ | $U+PV-TS$ | $T, P, N$ | 等温等压的判据 |
| 巨势 $\Phi$ | $U-TS-\mu N$ | $T, V, \mu$ | 开放系统 |

### 1.5 Maxwell 关系

从热力学势的全微分出发，利用 $dU = TdS - PdV$ 的恰当微分条件 $\partial^2 U/\partial X\partial Y = \partial^2 U/\partial Y\partial X$：

$$\left(\frac{\partial T}{\partial V}\right)_S = -\left(\frac{\partial P}{\partial S}\right)_V$$

（以及其他三个类似关系）

**用途**：用容易测量的量（如 $\partial P/\partial T$）表达难以测量的量（如 $\partial S/\partial V$）。

### 1.6 卡诺循环与效率

理想可逆热机在两个热源 $T_H$ 和 $T_C$ 之间运行（两个等温 + 两个绝热）：

$$\eta = 1 - \frac{T_C}{T_H}$$

这是所有热机的效率上限（第二定律的直接推论）。

---

## 第二部分：系综理论（Phys 166, Reif Ch.2-6）

### 2.1 微正则系综（孤立系统）

**基本假设**：孤立系统处于每个可达微观态的概率相等（等概率假设）。

$$p_i = \frac{1}{\Omega}, \quad \Omega = \text{微观态数}$$

熵（Boltzmann 公式）：
$$S = k_B \ln\Omega$$

> 💡 **等概率假设的合理性**：刘维尔定理（来自哈密顿力学）保证相空间密度不变，加上各态历经假说（时间平均 = 系综平均），等概率是自然选择。

### 2.2 正则系综（与热库接触）

系统与大热库 $T$ 接触，可交换能量但不能交换粒子。

**Boltzmann 分布**：微观态 $i$（能量 $E_i$）的概率

$$\boxed{p_i = \frac{1}{Z}e^{-\beta E_i}, \quad \beta = \frac{1}{k_BT}}$$

配分函数：
$$Z = \sum_i e^{-\beta E_i}$$

**从 $Z$ 求一切热力学量**：

$$E = -\frac{\partial \ln Z}{\partial \beta}, \quad S = k_B(\ln Z + \beta E), \quad F = -k_BT\ln Z$$

> 🔑 **Reif 的核心信息**：配分函数 $Z$ 是统计力学的"生成函数"——一旦知道 $Z$，所有热力学量均可通过求导得到。这与量子力学中"一旦知道波函数就知道一切"异曲同工。

### 2.3 巨正则系综（开放系统）

系统与热库交换能量**和**粒子（化学势 $\mu$）。

**巨配分函数**：
$$\mathcal{Z} = \sum_{N=0}^{\infty}\sum_i e^{-\beta(E_{Ni}-\mu N)} = \sum_N z^N Z_N$$

其中 $z = e^{\beta\mu}$ 是逸度。

$$\langle N \rangle = \frac{1}{\beta}\frac{\partial \ln\mathcal{Z}}{\partial\mu}, \quad \Phi = -k_BT\ln\mathcal{Z}$$

### 2.4 经典极限（麦克斯韦-玻尔兹曼）

高温低密时，量子统计退化为经典。单原子理想气体配分函数：

$$Z_1 = V\left(\frac{2\pi m k_BT}{h^2}\right)^{3/2} = V/\lambda_{th}^3$$

热德布罗意波长 $\lambda_{th} = h/\sqrt{2\pi m k_BT}$。

$N$ 个不可分辨粒子：$Z_N = Z_1^N / N!$

推导出理想气体状态方程 $PV = Nk_BT$ 和熵公式（Sackur-Tetrode 方程）。

### 2.5 能量均分定理

在经典正则系综中，哈密顿量中每个**二次项**贡献 $\frac{1}{2}k_BT$ 到平均能量。

3D 理想气体（3 个动量二次项）：$E = \frac{3}{2}Nk_BT$ → $C_V = \frac{3}{2}Nk_B$

Einstein 固体（3D 谐振子，6 个二次项）：$E = 3Nk_BT$ → $C_V = 3Nk_B$（Dulong-Petit 定律）

> ⚠️ **均分定理的失败**：低温下固体热容 $\to 0$（实验事实），均分定理给出常数 $3Nk_B$。这个矛盾催生了量子统计（→ 第四部分）。

---

## 第三部分：量子统计（Phys 166, Reif Ch.9-11）

### 3.1 全同粒子与交换对称性

- **玻色子**（整数自旋）：波函数对称，多个粒子可占据同一态
- **费米子**（半整数自旋）：波函数反对称，**泡利不相容**（每态最多一个）

### 3.2 Bose-Einstein 分布与 Fermi-Dirac 分布

平均占据数（能量 $\epsilon$ 的单粒子态）：

$$\bar{n}(\epsilon) = \frac{1}{e^{\beta(\epsilon-\mu)} \mp 1}$$

| 分布 | 符号 | 分母 | 适用 |
|------|------|------|------|
| Bose-Einstein | $\bar{n}_{BE}$ | $e^{\beta(\epsilon-\mu)} - 1$ | 玻色子 |
| Fermi-Dirac | $\bar{n}_{FD}$ | $e^{\beta(\epsilon-\mu)} + 1$ | 费米子 |
| Maxwell-Boltzmann | $\bar{n}_{MB}$ | $e^{\beta(\epsilon-\mu)}$ | 经典极限 |

> **经典极限条件**：$\bar{n} \ll 1$（低占据），即 $e^{\beta(\epsilon-\mu)} \gg 1$，此时 $\pm 1$ 可忽略，三种分布统一。

### 3.3 黑体辐射（光子气体）

光子是玻色子（自旋 1），化学势 $\mu = 0$（光子数不守恒）。

Planck 分布：
$$u(\nu) = \frac{8\pi h\nu^3}{c^3}\frac{1}{e^{h\nu/k_BT}-1}$$

总能量密度（Stefan-Boltzmann 定律）：$u = aT^4$，$a = 4\sigma/c$

> 🏆 **历史意义**：Planck 为拟合黑体辐射曲线引入了能量量子化 $E = h\nu$（1900），开启了量子力学。

### 3.4 德拜模型（固体热容的量子理论）

将固体视为声子（量子化的晶格振动）气体，声子是玻色子。

态密度 $g(\omega) \propto \omega^2$（截断到德拜频率 $\omega_D$）。

低温极限 $T \ll \Theta_D$：
$$C_V \propto T^3 \quad (\text{德拜 } T^3 \text{ 定律})$$

这正确解释了实验观测的低温热容→趋于零，修正了均分定理的失败。

### 3.5 理想费米气体

$T=0$ 时：费米子填满到费米能 $\epsilon_F$（所有 $\epsilon < \epsilon_F$ 态被占）。

费米能与费米温度：
$$\epsilon_F = \frac{\hbar^2}{2m}\left(\frac{3\pi^2 N}{V}\right)^{2/3}, \quad T_F = \epsilon_F/k_B$$

> **反直觉**：$T=0$ 时费米气体仍有巨大动能！电子气 $T_F \sim 10^4$ K。金属中的传导电子即使冷却到绝对零度，也以接近费米速度运动——这是泡利不相容原理的后果。

低温热容：$C_V = \frac{\pi^2}{2}Nk_B\frac{T}{T_F}$（线性 $T$ 依赖，与德拜 $T^3$ 叠加）。

---

## 第四部分：相变与临界现象（Phys 166, Reif Ch.10）

### 4.1 相变分类（Ehrenfest 分类）

- **一级相变**：熵和体积不连续（有潜热），如冰→水。自由能一阶导不连续。
- **连续（二级）相变**：熵连续但热容发散。自由能二阶导不连续/发散。

### 4.2 Ising 模型

自旋在格点上取 $\pm 1$，最近邻相互作用：

$$H = -J\sum_{\langle i,j\rangle}s_is_j - h\sum_i s_i$$

| 维度 | 结果 |
|------|------|
| 1D | 无相变（任何 $T>0$ 都无序） |
| 2D (Onsager 1944) | 有连续相变，$T_c = 2J/(k_B\ln(1+\sqrt{2}))$ |
| 3D | 有相变（数值解，无精确解析解） |

### 4.3 序参量与对称性破缺

**序参量** $m$：相变中从零变非零的量。

Ising 模型中 $m = \langle s_i \rangle$（平均磁化）。

- $T > T_c$：$m = 0$（对称态）
- $T < T_c$：$m \neq 0$（自发对称性破缺）

> 🔑 **自发对称性破缺**：哈密顿量有 $\mathbb{Z}_2$ 对称性（$s_i \to -s_i$），但低温下系统选择 $m > 0$ 或 $m < 0$ 之一。对称性被系统状态"破缺"而非定律本身。

### 4.4 临界指数与普适性

接近 $T_c$ 时，物理量以幂律发散/消失：

$$m \sim |T-T_c|^\beta, \quad C_V \sim |T-T_c|^{-\alpha}, \quad \xi \sim |T-T_c|^{-\nu}$$

其中 $\xi$ 是关联长度。

**普适性**：临界指数只依赖（维度 + 序参量分量数 + 相互作用范围），不依赖微观细节。

2D Ising：$\beta = 1/8$；3D Ising：$\beta \approx 0.326$（数值）。

### 4.5 平均场理论（Landau 理论）

Landau 将自由能展开为序参量的幂级数：

$$F(m) = F_0 + a(T-T_c)m^2 + bm^4 + \ldots$$

- $T > T_c$：$a(T-T_c) > 0$，极小在 $m=0$
- $T < T_c$：$a(T-T_c) < 0$，极小在 $m \neq 0$

平均场临界指数：$\beta_{MF} = 1/2$（与精确 2D 值 $1/8$ 不同——涨落被忽略）。

---

## 📝 习题精选

### 习题 1（Phys 165 级，Schroeder 熵）

两个 Einstein 固体 A 和 B（各 $N_A = N_B = 50$ 个振子），共享 100 个能量量子。求平衡时各有多少量子，总熵。

> **提示**：平衡时 $dS_{\text{total}}/dq_A = 0$，即 $q_A = q_B = 50$（对称）。用 $\Omega = \binom{q+N-1}{q}$。

### 习题 2（Phys 165 级，卡诺效率）

蒸汽机锅炉 $T_H = 500$ K，冷凝器 $T_C = 300$ K。最大效率多少？若要输出 100 MW 功率，每秒需吸热多少？

> **答案**：$\eta = 1 - 300/500 = 40\%$。$Q_H = W/\eta = 250$ MW。

### 习题 3（Phys 166 级，正则系综）

二能级系统：能级 $E_0 = 0$, $E_1 = \epsilon$。求配分函数 $Z$、平均能量、热容，讨论高温/低温极限。

> **答案**：$Z = 1+e^{-\beta\epsilon}$；$\langle E\rangle = \epsilon/(e^{\beta\epsilon}+1)$；$C = k_B(\beta\epsilon)^2 e^{\beta\epsilon}/(e^{\beta\epsilon}+1)^2$。高温 $C \to k_B(\epsilon/k_BT)^2 \to 0$；低温 $C \to k_B(\epsilon/k_BT)^2 e^{-\epsilon/k_BT} \to 0$。中间有 Schottky 峰。

### 习题 4（Phys 166 级，费米气体）

铜中自由电子密度 $n = 8.5\times10^{28}\,\text{m}^{-3}$。求费米能、费米温度和 $T=0$ 时的平均电子能量。

> **答案**：$\epsilon_F \approx 7.0$ eV，$T_F \approx 8.1\times10^4$ K，$\langle E\rangle = \frac{3}{5}\epsilon_F \approx 4.2$ eV。

### 习题 5（Phys 166 级，Ising 模型）

一维 Ising 模型（$N$ 个自旋，周期性边界），证明任何 $T > 0$ 都不发生自发磁化。

> **提示**：考虑翻转一段连续同向自旋的能量代价 $\Delta E = 2J$，熵增益 $\Delta S \sim k_B\ln N$。自由能变化 $\Delta F = \Delta E - T\Delta S < 0$（$N$ 足够大），故无序态总在热力学上占优。

---

## 💻 Python 代码

### 代码 1：Einstein 固体熵的计算

```python
"""
Einstein 固体: 验证 S = k_B ln Ω 及热平衡
Ω(N,q) = (q+N-1)! / (q!(N-1)!)
"""
import math

def log_factorial(n):
    """Stirling 近似: ln(n!) ≈ n ln n - n"""
    if n <= 1:
        return 0.0
    return n * math.log(n) - n + 0.5*math.log(2*math.pi*n)

def log_omega(N, q):
    """ln Ω(N,q) = ln[(q+N-1)!] - ln[q!] - ln[(N-1)!]"""
    return (log_factorial(q+N-1) - log_factorial(q) - log_factorial(N-1))

# 两个 Einstein 固体, 各 50 个振子, 共享 100 个量子
NA, NB = 50, 50
q_total = 100

print("=== Einstein 固体热平衡 ===")
print(f"固体A({NA}振子) + 固体B({NB}振子), 总量子={q_total}\n")

# 扫描 q_A = 0..100, 找熵极大
max_entropy = -1e10
best_qA = 0
for qA in range(q_total+1):
    qB = q_total - qA
    S_total = log_omega(NA, qA) + log_omega(NB, qB)
    if S_total > max_entropy:
        max_entropy = S_total
        best_qA = qA

print(f"熵极大在 q_A = {best_qA}, q_B = {q_total - best_qA}")
print(f"最大 ln(Ω_total) = {max_entropy:.2f}")
print(f"（对称性预期: q_A = q_B = {q_total//2}）\n")

# 熵 vs qA 曲线（验证熵是凸函数，极大在中心）
print("qA   ln(Ω_total)")
for qA in range(0, 101, 10):
    qB = q_total - qA
    S = log_omega(NA, qA) + log_omega(NB, qB)
    bar = '#' * int((S - 100) * 0.5)  # 简单可视化
    print(f"{qA:3d}   {S:8.2f}  {bar}")
```

### 代码 2：Boltzmann 分布与配分函数

```python
"""
二能级系统的正则系综
演示配分函数 Z 如何编码一切热力学
"""
import math

def two_level(Z_args):
    """
    二能级系统: E0=0, E1=epsilon
    返回各热力学量关于 T 的函数
    """
    epsilon = Z_args  # 能隙 (eV)

    results = []
    kT_range = [0.1*epsilon, 0.5*epsilon, epsilon, 2*epsilon, 5*epsilon, 10*epsilon]

    for kT in kT_range:
        beta = 1.0 / kT
        Z = 1 + math.exp(-beta * epsilon)
        avg_E = epsilon * math.exp(-beta*epsilon) / Z
        prob_excited = math.exp(-beta*epsilon) / Z
        # 熵 S = k_B[ln Z + beta*<E>], 取 k_B=1
        S = math.log(Z) + beta * avg_E
        # 热容 C = d<E>/dT
        x = epsilon / kT
        C = x**2 * math.exp(x) / (math.exp(x)+1)**2

        results.append((kT/epsilon, prob_excited, avg_E/epsilon, S, C))

    return results

epsilon = 1.0  # 归一化能隙
results = two_level(epsilon)

print("=== 二能级系统正则系综 ===")
print(f"能级: E0=0, E1={epsilon}ε\n")
print(f"{'kT/ε':>6} {'P(excited)':>12} {'<E>/ε':>8} {'S/kB':>8} {'C/kB':>8}")
print("-" * 50)
for kT_ratio, p, E, S, C in results:
    print(f"{kT_ratio:6.1f} {p:12.4f} {E:8.4f} {S:8.4f} {C:8.4f}")

print("\n💡 高温(kT>>ε): P→1/2, <E>→ε/2, C→0 (能级饱和)")
print("   低温(kT<<ε): P→0, <E>→0, C→0 (冻结在基态)")
print("   中间 kT≈ε: 热容 C 有峰值 (Schottky 异常)")
```

### 代码 3：二维 Ising 模型 Monte Carlo

```python
"""
二维 Ising 模型 Metropolis 算法
演示自发磁化相变（Onsager 精确解 Tc 验证）
"""
import random
import math

def ising_2d(L, T, steps, seed=42):
    """
    L×L 格点 Ising 模型
    T: 温度 (J/kB 为单位, 取 J=kB=1)
    返回平均磁化率 <|m|>
    """
    random.seed(seed)
    J = 1.0  # 耦合常数

    # 初始化: 随机自旋
    spins = [[random.choice([-1, 1]) for _ in range(L)] for _ in range(L)]

    def neighbor_sum(i, j):
        """周期性边界条件的邻居和"""
        up = spins[(i-1) % L][j]
        down = spins[(i+1) % L][j]
        left = spins[i][(j-1) % L]
        right = spins[i][(j+1) % L]
        return up + down + left + right

    total_mag = sum(sum(row) for row in spins)
    mags = []

    for step in range(steps):
        i = random.randint(0, L-1)
        j = random.randint(0, L-1)
        s = spins[i][j]
        nb = neighbor_sum(i, j)
        dE = 2 * J * s * nb  # 翻转 s 的能量变化

        if dE < 0 or random.random() < math.exp(-dE / T):
            spins[i][j] = -s
            total_mag += 2 * (-s)

        if step % (L*L) == 0:  # 每个 MC step 记录一次
            mags.append(abs(total_mag) / (L*L))

    return sum(mags[len(mags)//2:]) / len(mags[len(mags)//2:])  # 后半段平均

# Onsager 精确临界温度: Tc = 2J / [kB * ln(1+√2)] ≈ 2.269
Tc_exact = 2.0 / math.log(1 + math.sqrt(2))

print("=== 二维 Ising 模型相变 ===")
print(f"Onsager 精确 Tc = {Tc_exact:.4f} (J/kB)\n")

L = 16
steps = 50000
print(f"格点: {L}x{L}, MC步数: {steps}\n")
print(f"{'T':>6} {'|m|':>8} {'状态':>8}")
print("-" * 28)

for T in [1.0, 1.5, 2.0, 2.269, 2.5, 3.0, 4.0]:
    m = ising_2d(L, T, steps)
    state = "有序" if m > 0.3 else "无序"
    print(f"{T:6.2f} {m:8.4f} {state:>8}")

print(f"\n💡 T < Tc≈{Tc_exact:.2f}: |m|>0 (自发磁化, 铁磁有序)")
print(f"   T > Tc: |m|→0 (顺磁无序)")
print(f"   相变是连续的(二级)")
```

### 代码 4：黑体辐射 Planck 分布

```python
"""
Planck 黑体辐射分布
验证 Stefan-Boltzmann 定律和 Wien 位移定律
"""
import math

# 物理常数
h = 6.626e-34    # J·s
c = 3.0e8         # m/s
kB = 1.381e-23    # J/K
sigma = 5.67e-8   # Stefan-Boltzmann

def planck_spectral(nu, T):
    """Planck 谱: u(ν) = 8πhν³/c³ · 1/(exp(hν/kBT)-1)"""
    x = h * nu / (kB * T)
    if x > 500:
        return 0.0
    return (8 * math.pi * h * nu**3 / c**3) / (math.exp(x) - 1)

def total_radiance(T):
    """Stefan-Boltzmann: u = aT⁴, 功率/面积 = σT⁴"""
    return sigma * T**4

def wien_displacement(T):
    """Wien 定律: λ_max T = b ≈ 2.898e-3 m·K"""
    return 2.898e-3 / T

# 太阳 (T≈5778 K)
T_sun = 5778
print("=== 太阳黑体辐射 (T=5778 K) ===")
print(f"峰值波长: λ_max = {wien_displacement(T_sun)*1e9:.0f} nm (可见光绿)")
print(f"辐射功率密度: {total_radiance(T_sun)/1e6:.1f} MW/m²")
print(f"(Stefan-Boltzmann σT⁴ 验证)")

# 宇宙微波背景 (T=2.725 K)
T_cmb = 2.725
print(f"\n=== 宇宙微波背景 (T=2.725 K) ===")
print(f"峰值波长: λ_max = {wien_displacement(T_cmb)*1e3:.2f} mm (微波)")

# Planck 分布峰值验证
print("\n=== Planck 分布验证 (T=5778K) ===")
peak_nu = 0
peak_u = 0
for i in range(1, 10000):
    nu = i * 1e10  # 10 GHz 步长
    u = planck_spectral(nu, T_sun)
    if u > peak_u:
        peak_u = u
        peak_nu = nu

# Wien 频率位移定律: ν_max ≈ 2.82 kBT/h
nu_max_wien = 2.82 * kB * T_sun / h
print(f"数值峰值频率: {peak_nu/1e12:.1f} THz")
print(f"Wien 频率定律: {nu_max_wien/1e12:.1f} THz (2.82kBT/h)")
print(f"对应波长: λ = c/ν = {c/peak_nu*1e9:.0f} nm")
print(f"Wien 波长定律: {wien_displacement(T_sun)*1e9:.0f} nm")
print("(两者不完全对应, 因 λ 和 ν 峰值定义不同)")
```

---

## 📚 Schroeder vs Reif 对比

| 维度 | Schroeder | Reif |
|------|-----------|------|
| **篇幅** | ~400 页（精炼） | ~780 页（全面） |
| **风格** | 物理直觉优先，例题驱动 | 数学严谨，推导完整 |
| **起点** | 分子动理论（计数微观态） | 概率论 + 系综公理 |
| **相变** | 简要介绍 | 专章（Ising + 临界指数） |
| **量子统计** | 第 7 章（概览） | 第 9-11 章（详细推导） |
| **涨落** | 偶尔提及 | 专章（第 10 章 + 关联函数） |
| **适合** | Phys 165（入门） | Phys 166（深化） |

**学习路径**：Schroeder Ch.1-3（热力学+计数法）→ Ch.4-5（正则/巨正则系综）→ Reif Ch.9-11（量子统计）→ Reif Ch.10（相变+涨落）。

---

## 🔗 衔接

- **← Phys 143a/b（量子力学）**：量子统计需要 Bose-Einstein / Fermi-Dirac 分布
- **← Phys 15a（力学）**：刘维尔定理 → 微正则系综的等概率假设
- **→ Phys 195（固体物理）**：费米气体 → 金属电子论；声子 → 德拜模型
- **→ Phys 216（凝聚态）**：相变理论 → 重整化群 → 临界现象
- **→ 天体物理**：黑体辐射 → 恒星光谱；费米气体 → 白矮星/中子星

---

## 🌟 统计力学的"万能钥匙"总结

```
配分函数 Z = Σ exp(-βE_i)
     │
     ├── 自由能:  F = -kT ln Z
     ├── 内能:    U = -∂(ln Z)/∂β
     ├── 熵:      S = k(ln Z + βU)
     ├── 压强:    P = (1/β)∂(ln Z)/∂V
     ├── 热容:    C = ∂U/∂T
     └── 化学势:  μ = -(1/β)∂(ln Z)/∂N
```

> 一旦写出 $Z$，所有热力学量自动得出。这是统计力学**最美的部分**——也是 Reif 全书反复回归的主旋律。

---

*完成日期：2026-08-12 | 基于 Harvard Physics Catalog + Schroeder + Reif 教材*

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：统计力学用"概率"把微观粒子的疯狂运动（$10^{23}$ 个分子乱撞）和宏观量（温度、压强、熵）联系起来——你不需要追踪每一个分子，只需要统计它们整体的"平均行为"。
>
> **生活类比**：想象一个拥挤的操场，$10^{23}$ 个孩子在随机乱跑。你不可能盯住每个孩子（微观），但你能测出"平均有多挤"（密度=压强）、"平均跑多快"（温度）。统计力学就是这套"从操场人潮推教室温度"的数学。
>
> **反直觉发现**：时间只朝一个方向流（打碎的杯子不会自己复原），但底层的牛顿/量子方程都是**时间可逆**的！这个矛盾叫"时间箭头"——答案在概率：把所有分子都聚到杯子完整状态的概率小到不可能，而散开的状态有天文数字那么多。**熵增不是物理定律禁止逆过程，而是概率上几乎不可能。**

---

## 🔗 衔接：从哪来，到哪去

### 前置知识
经典力学（刘维尔定理、相空间）+ 量子力学（能级、费米/玻色子）+ 概率论 + 多变量微积分。Harvard 的 Phys 165/166 假设你已学完 143a 量子力学。

### 本主题解决了什么危机
热力学（19 世纪工程产物）只给宏观定律（四大定律），但**不解释为什么**——为什么温度这个量存在？为什么熵只能增？统计力学（Boltzmann、Gibbs）从微观力学出发，用配分函数 $Z=\sum e^{-\beta E_n}$ 一次性推出所有热力学量。**温度 = 能量涨落的标度，熵 = 微观状态数的对数（$S=k_B\ln\Omega$）**——宏观量从此有了微观根基。

### 本主题留下的新危机
1. **非平衡态**：平衡态统计力学很成熟，但生命、气候、湍流都是**远离平衡**的开放系统——非平衡统计力学（涨落定理、Jarzynski 等式）仍在发展中
2. **时间箭头与可逆性的矛盾**：微观可逆 vs 宏观不可逆，至今是物理哲学的深水区
3. **相变与涌现**：单个水分子没有"温度""液态"属性——这些是 $10^{23}$ 个粒子**集体涌现**的。涌现如何从微观产生？（重整化群给出了部分答案）
4. **玻璃态与 jamming**：玻璃是液体还是固体？无序系统的统计力学仍是开放前沿

### 后续主题
- **← 力学（刘维尔定理）+ 量子（量子统计）**：平衡态的两大支柱
- **→ 凝聚态（AP 295a）**：声子、费米液体、超导 BCS 理论
- **→ 生物物理（Nelson）**：蛋白质折叠、分子马达、扩散限制反应
- **→ 宇宙学（Phys 212）**：早期宇宙的统计力学、CMB、热力学大爆炸
- **→ 机器学习/复杂系统**：玻尔兹曼机、Ising 模型 → 神经网络

---

## 🏭 理论联系实际：5 个应用

1. **半导体器件设计（费米-狄拉克分布）**：芯片里电子怎么分布、PN 结怎么形成、掺杂浓度怎么定——全靠费米能级和费米-狄拉克分布 $f(E)=1/(e^{(E-\mu)/kT}+1)$。化学势 $\mu$ 决定了电子流动方向，是半导体工程的"指挥棒"。

2. **超导与超流（玻色-爱因斯坦凝聚）**：氦-4 在 2.17 K 以下变成无粘性的超流体（爬壁现象），某些金属在低温下零电阻超导——都是宏观量子统计现象：玻色子凝聚到同一基态（BEC），费米子配对成库珀对。MRI 超导磁体、量子计算机稀释制冷机都依赖此。

3. **天气预报与气候模型**：大气是 $10^{44}$ 个分子的非平衡统计系统。数值天气预报解的是宏观流体方程（从玻尔兹曼方程粗粒化而来），参数化次网格过程（湍流、云）本质是统计力学Closure 问题。气候敏感度的不确定性根源在云的统计物理。

4. **蛋白质折叠与药物设计**：蛋白质从随机链折叠成有功能的 3D 结构，服从自由能极小化 $\Delta G=\Delta H-T\Delta S$（焓 vs 熵的竞争）。分子动力学模拟（统计力学采样）是现代药物设计的核心工具。Nelson《生物物理》用统计力学解释生命的分子逻辑。

5. **扩散与电池/燃料电池**：锂离子在电池电极中扩散（菲克定律，源于随机行走的统计力学）、燃料电池质子交换膜的传输——全是非平衡统计输运过程。电池快充的极限由离子扩散速率决定。

---

## 🔬 最新研究前沿（2024-2026）

### 活性物质：微电机阵列的相干与无序诱导波
- **发现**：3D 打印的耦合自推进微电机实验显示，旋转运动可以产生时空有序，而**无序反而诱导波传播**——活性物质（消耗能量自我驱动的系统，如细菌群、细胞组织）展现出平衡态系统没有的集体行为。这是非平衡统计力学的实验前沿。
- **来源**：Braun, Poncet & Bartolo，*Nature Physics* (2026-08-11)

### 随机热力学拓展到社会模仿动力学
- **发现**：把随机热力学（描述小系统非平衡能量学的框架）扩展到**社会模仿动力学**，建立了联系社会属性变化、信息和不可逆性的"第二定律"，并给出涨落定理和不确定关系。统计力学的工具正在跨界到社会科学。
- **来源**：Irisarri, Trigal & Manzano，*Nature Communications* (2026-08-08)

### 从轨迹数据学习耗散动力学（+熵产率）
- **发现**：开发了从轨迹数据恢复唯一能量景观并量化**熵产率**的框架，揭示了聚合物拉伸的标度律和学习算法的采样偏差——把机器学习和非平衡统计力学结合，从数据反推物理。
- **来源**：Zhu, Soh & Li，*Nature Communications* (2026-08-06)

### Jamming 与组织相变解耦：粘附 vs 密度
- **发现**：独立调节细胞密度和粘附（体外+体内），发现**粘附决定组织的物态**——粘附驱动的未堵塞（unjammed）多能组织凝固推动了上皮组织化。揭示了相变如何指导发育程序。这是 jamming 物理学在生物学的应用。
- **来源**：*Nature Physics* 22:830 (2026-06-02 News & Views)

### 运动回形针"学会"功能反射（自主学习的物质）
- **发现**：一个由铰链组成的"运动回形针"能按需学习、遗忘、再学习自动反应——揭示了模拟生命物质自主学习所需的**物理原理**。物质本身在做统计学习。
- **来源**：Alim，*Nature Physics* 22:653 (2026-04-16 News & Views)

> 💡 **趋势洞察**：统计力学的边界正在爆炸式扩张——从平衡态晶体/气体，走向活性物质、生命系统、机器学习、社会动力学。核心问题"无序+多体如何涌现有序"从未如此relevant。Harvard 的 Nelson 组（生物物理软物质）正处在这场跨学科浪潮中心。

---

## 🗺️ 学习 Roadmap（Harvard 路径）

### 🟢 入门（Phys 165，半学期-一学期）
- **教材**：Schroeder *An Introduction to Thermal Physics*
- **核心**：熵的统计诠释（$S=k_B\ln\Omega$）、温度/化学势的物理意义、配分函数 $Z$、自由能、热机/卡诺
- **里程碑**：能用配分函数从微观能级推出热容；理解为什么化学势是"粒子的水位"

### 🟡 进阶（Phys 166，一学期）
- **教材**：Reif *Fundamentals of Statistical and Thermal Physics*
- **核心**：微正则/正则/巨正则系综、量子统计（费米/玻色）、相变（Ising 模型）、非平衡初步（输运、涨落定理）
- **里程碑**：能从巨正则分布推出费米-狄拉克分布；用 Ising 模型解释自发磁化

### 🔴 深造（研究生 / 前沿方向）
- **教材**：Pathria *Statistical Mechanics* + Kardar *Statistical Physics of Particles/Fields*
- **方向**：重整化群（相变普适性）、非平衡统计力学、活性物质、玻璃/jamming、生物物理
- **Harvard 资源**：Nelson《Biological Physics》（生物物理招牌）、Lukin 组（量子多体模拟）

### ✅ 知识检查（自测清单）
- [ ] 熵到底是什么？为什么它只增不减？（状态数，概率）
- [ ] 化学势为什么是"粒子的水位"？（粒子从 μ 高流向 μ 低）
- [ ] 为什么绝对零度下电子还在以费米速度飞驰？（泡利不相容 + 零点能）
- [ ] Ising 模型怎么解释磁铁加热到居里点失去磁性？（自发对称破缺）
- [ ] 时间箭头和微观可逆性矛盾怎么化解？（概率，洛施密特回波）

> 跑一下 `python3 physics_demos.py 5 7`（化学势与费米能级 + 生物物理随机行走扩散）验证统计直觉！
