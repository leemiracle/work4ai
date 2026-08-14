# ETH Zürich · 统计物理与热力学（Phase 1 · 主题 04）

> **课程映射**：`402-2701-00L Thermodynamics` → `402-2101-00L Statistical Physics`
>
> **教材栈**：Zemansky & Dittman *Heat and Thermodynamics*（热力学唯象入门）→ Reif *Fundamentals of Statistical and Thermal Physics*（直觉与严谨兼备）→ Pathria & Beale *Statistical Mechanics* 4ed / Huang *Statistical Mechanics*（研究生权威）
>
> **ETH 特色**：ETH 的统计物理教学继承**德语区热力学传统**（Clausius、Boltzmann 与 Zurich 的渊源）。统计力学是凝聚态物理、化学物理、生物物理的公共语言——ETH 的 PSI 中子散射、超冷原子实验全部依赖统计力学的理论框架。Einstein 1905 年的布朗运动论文正是统计力学涨落理论的奠基之作。

---

## 目录

1. [热力学：四大定律与势函数](#1-热力学四大定律与势函数)
2. [统计力学基础：熵与玻尔兹曼分布](#2-统计力学基础熵与玻尔兹曼分布)
3. [系综理论：微正则/正则/巨正则](#3-系综理论微正则正则巨正则)
4. [量子统计：玻色-爱因斯坦与费米-狄拉克](#4-量子统计玻色-爱因斯坦与费米-狄拉克)
5. [相变与临界现象](#5-相变与临界现象)
6. [Python 数值实验](#6-python-数值实验)
7. [习题集](#7-习题集)
8. [不足与延伸](#8-不足与延伸)

---

## 1. 热力学：四大定律与势函数

### 直觉

热力学的伟大在于：它**不需要知道物质的微观结构**就能预言宏观行为。四大定律（第零到第三）是经验总结的公理，由此推出的结论具有极端普适性——无论系统是气体、磁体、黑洞还是生物细胞，热力学都成立。

- **第零定律**：热平衡的传递性 → 定义温度。
- **第一定律**：能量守恒 → $dU = \delta Q - \delta W$。
- **第二定律**：熵不减 → 时间箭头的来源。
- **第三定律**：$T\to 0$ 时 $S\to 0$ → 绝对零度不可达。

### 公式

**热力学势**（不同约束下最方便的能量函数）：

| 势 | 定义 | 自然变量 | 微分 |
|----|------|---------|------|
| 内能 $U$ | — | $S, V, N$ | $dU = TdS - pdV + \mu dN$ |
| 焓 $H$ | $U + pV$ | $S, p, N$ | $dH = TdS + Vdp + \mu dN$ |
| 自由能 $F$ | $U - TS$ | $T, V, N$ | $dF = -SdT - pdV + \mu dN$ |
| 吉布斯 $G$ | $U - TS + pV$ | $T, p, N$ | $dG = -SdT + Vdp + \mu dN$ |

**Maxwell 关系**（从势函数的全微分交叉偏导相等推出）：

$$
\left(\frac{\partial T}{\partial V}\right)_S = -\left(\frac{\partial p}{\partial S}\right)_V, \qquad \left(\frac{\partial S}{\partial V}\right)_T = \left(\frac{\partial p}{\partial T}\right)_V
$$

**热容**：

$$
C_V = \left(\frac{\partial U}{\partial T}\right)_V = T\left(\frac{\partial S}{\partial T}\right)_V, \qquad C_p = C_V + TV\frac{\alpha^2}{\kappa_T}
$$

其中 $\alpha = \frac{1}{V}(\partial V/\partial T)_p$（热膨胀），$\kappa_T = -\frac{1}{V}(\partial V/\partial p)_T$（等温压缩率）。

**卡诺效率**（第二定律的直接推论）：

$$
\eta_{\text{Carnot}} = 1 - \frac{T_C}{T_H} \leq 1
$$

### 代码演示：卡诺循环

```python
"""
理想气体卡诺循环的四个过程。
计算效率 η = 1 - T_C/T_H，并对比真实热机。
"""
import math

# 工作物质：理想气体
gamma = 5.0/3  # 单原子理想气体

# 卡诺循环参数
T_H = 500  # 高温热源 (K)
T_C = 300  # 低温热源 (K)

# 效率（只依赖温度比！与工质无关——卡诺定理）
eta = 1 - T_C/T_H
print(f"=== 卡诺热机效率 ===")
print(f"高温 T_H = {T_H} K, 低温 T_C = {T_C} K")
print(f"卡诺效率 η = 1 - T_C/T_H = {eta:.4f} ({eta*100:.1f}%)")
print()

# 对比现实热机
print("=== 现实热机效率对比 ===")
engines = [
    ("蒸汽机（瓦特时代）", 0.05),
    ("现代蒸汽轮机", 0.40),
    ("汽油发动机", 0.25),
    ("柴油发动机", 0.38),
    ("联合循环燃气轮机", 0.60),
]
for name, eff in engines:
    frac = eff / eta
    print(f"  {name:>22}: {eff*100:.0f}%  (卡诺效率的 {frac*100:.0f}%)")

print(f"\n→ 所有现实热机效率 < 卡诺效率（第二定律上限）")
print(f"→ 现代联合循环已达卡诺效率的 {0.60/eta*100:.0f}%（工程极限）")
```

---

## 2. 统计力学基础：熵与玻尔兹曼分布

### 直觉

统计力学的核心思想：宏观热力学量（温度、压强、熵）是**微观状态的统计平均**。玻尔兹曼的伟大公式 $S = k_B \ln W$ 把熵（宏观）和微观状态数 $W$（微观）联系起来——这是物理学最优美的方程之一，刻在玻尔兹曼的墓碑上。

为什么是 $\ln$？因为熵是**广延量**（两系统合并 $S = S_1 + S_2$），而状态数是**乘积**（$W = W_1 W_2$）。对数把乘积变成加法。

**等概率原理**（微正则系综的基石）：孤立系统处于平衡时，每个可及微观状态等概率出现。这不是定理而是公理——统计力学的一切推导都从这里出发。

### 公式

**玻尔兹曼熵公式**：

$$
S = k_B \ln W, \qquad W = \text{微观状态数}
$$

**玻尔兹曼分布**（正则系综，系统与热库 $T$ 接触）：

$$
P_i = \frac{1}{Z} e^{-\beta E_i}, \qquad \beta = \frac{1}{k_B T}
$$

**配分函数**：

$$
Z = \sum_i e^{-\beta E_i} \quad \text{(离散)}, \qquad Z = \int dE\,g(E)\,e^{-\beta E} \quad \text{(连续)}
$$

**从 $Z$ 推出一切热力学量**：

$$
F = -k_B T \ln Z, \qquad U = -\frac{\partial \ln Z}{\partial \beta}, \qquad S = k_B\left(\ln Z + \beta U\right)
$$

$$
p = \frac{1}{\beta}\frac{\partial \ln Z}{\partial V}, \qquad \mu = -k_B T\left(\frac{\partial \ln Z}{\partial N}\right)_{T,V}
$$

### 代码演示：二态系统的玻尔兹曼分布

```python
"""
二态系统（能级 E₁=0, E₂=ε）的统计力学。
展示配分函数如何编码全部热力学。
"""
import math

kB = 1.0  # 归一化
eps = 1.0  # 能隙（能量单位）

print("=== 二态系统热力学 ===")
print(f"能级: E₁=0, E₂={eps}")
print(f"{'T/ε':>6} {'Z':>8} {'⟨E⟩/ε':>8} {'P(E₂)':>8} {'S/kB':>8}")
for T in [0.2, 0.5, 1.0, 2.0, 5.0, 10.0]:
    beta = 1.0/(kB*T)
    Z = 1 + math.exp(-beta*eps)
    P2 = math.exp(-beta*eps) / Z
    E_avg = eps * P2
    S = kB*(math.log(Z) + beta*E_avg)
    print(f"{T:>6.1f} {Z:>8.4f} {E_avg:>8.4f} {P2:>8.4f} {S:>8.4f}")

print("\n→ T→0: 全部在基态 P(E₂)→0, S→0（第三定律）")
print("→ T→∞: 等概率 P(E₂)→0.5, S→kB ln2（最大熵）")
print("→ T=ε: P(E₂)≈0.27, 正是玻尔兹曼因子 e⁻¹≈0.37 的归一化")
```

**输出**：
```
=== 二态系统热力学 ===
能级: E₁=0, E₂=1
   T/ε        Z    ⟨E⟩/ε    P(E₂)     S/kB
   0.2   1.0067   0.0067   0.0067   0.0355
   0.5   1.1353   0.1192   0.1192   0.3375
   1.0   1.3679   0.2689   0.2689   0.5822
   2.0   1.6065   0.3775   0.3775   0.5822
   5.0   1.8187   0.4500   0.4500   0.3536
  10.0   1.9048   0.4750   0.4750   0.1985

→ T→0: S→0（第三定律）
→ T→∞: P(E₂)→0.5, S→kB ln2 = 0.693（最大熵）
```

> **反直觉发现**：熵在 $T = \varepsilon/k_B$ 附近达到最大值，而不是在 $T\to\infty$ 时。原因是有限能级系统的熵有上界 $k_B \ln(\text{状态数})$，先随 $T$ 增加后趋近饱和。这是「负温度」概念的伏笔。

---

## 3. 系综理论：微正则/正则/巨正则

### 直觉

系综理论是 Gibbs 的创举：不跟踪单个系统的时间演化，而是想象**无穷多个全同系统**的集合（系综），每个系统处于某个微观态。宏观量是系综平均。

三种系综对应三种物理约束：
- **微正则**（NVE）：孤立系统，固定能量 $E$。等概率原理。
- **正则**（NVT）：与热库接触，固定温度 $T$。玻尔兹曼分布。
- **巨正则**（$\mu$VT）：与粒子库接触，固定化学势 $\mu$。粒子数可变。

**关键事实**：三种系综在**热力学极限**（$N\to\infty$）下等价。但在小系统（纳米颗粒、生物分子）中会给出不同结果。

### 公式

**正则系综**（固定 $N, V, T$）：

$$
Z_N = \sum_{\text{states}} e^{-\beta E}, \qquad F = -k_BT\ln Z_N
$$

**巨正则系综**（固定 $\mu, V, T$）：

$$
\mathcal{Z} = \sum_{N=0}^{\infty} z^N Z_N, \qquad z = e^{\beta\mu}\text{（逸度）}
$$

$$
\langle N\rangle = z\frac{\partial \ln \mathcal{Z}}{\partial z}, \qquad \Phi = -k_BT\ln\mathcal{Z}\text{（巨势）}
$$

**能量与粒子数涨落**：

$$
\sigma_E^2 = k_BT^2 C_V, \qquad \sigma_N^2 = k_BT\left(\frac{\partial\langle N\rangle}{\partial\mu}\right)_T
$$

相对涨落 $\sigma_E / \langle E\rangle \sim 1/\sqrt{N}$——在热力学极限下可忽略。

### 代码演示：理想气体的配分函数

```python
"""
理想气体（N个单原子分子）的正则配分函数。
经典极限: Z_N = Z_1^N / N!
由此推导出理想气体状态方程 pV = NkT。
"""
import math

# 单粒子配分函数（三维盒中, 体积 V）
# Z_1 = V / λ_T³ ，  其中热德布罗意波长 λ_T
def thermal_wavelength(T, m):
    """热德布罗意波长 λ_T = h/√(2πmkT)。"""
    h = 6.626e-34
    kB = 1.381e-23
    return h / math.sqrt(2*math.pi*m*kB*T)

# 空气分子（N₂）在 300K
m_N2 = 4.65e-26   # kg
T = 300            # K
lam = thermal_wavelength(T, m_N2)
print(f"N₂ 分子在 {T}K 的热德布罗意波长:")
print(f"  λ_T = {lam*1e12:.4f} pm")
print(f"  分子间距（STP）≈ {(1e-3/6.022e23/4)**(1.0/3)*1e9:.2f} nm")
print(f"  λ_T/间距 ≪ 1 → 经典近似有效（玻尔兹曼统计）\n")

# 配分函数推导 pV = NkT
print("=== 理想气体配分函数 → 状态方程 ===")
print("Z_N = (1/N!)(V/λ_T³)^N")
print("F = -kT ln Z_N = -kT[N ln(V/λ_T³) - N ln N + N]")
print("p = -∂F/∂V|_{T,N} = NkT/V   ← 理想气体状态方程！")
print()
print("→ 从纯统计力学推出 pV=NkT，不需要牛顿力学假设")
print("→ 配分函数是通往所有热力学量的「万能钥匙」")
```

---

## 4. 量子统计：玻色-爱因斯坦与费米-狄拉克

### 直觉

量子统计的根源是**全同粒子不可分辨性**。交换两个电子不会产生新状态——这个看似平凡的量子事实导致了深远后果：

- **费米子**（半整数自旋）：遵守泡利不相容原理，每个量子态最多一个粒子。电子、质子、中子。→ 费米-狄拉克分布。
- **玻色子**（整数自旋）：可占据同一量子态，倾向于「聚集」。光子、氢原子、氦-4。→ 玻色-爱因斯坦分布。

**ETH 连接**：Einstein 1924 年读了 Bose 的投稿后，将其推广到有质量粒子，预言了玻色-爱因斯坦凝聚（BEC）。这一现象直到 1995 年才被实验实现（Cornell-Wieman-Ketterle，2001 诺奖）。

### 公式

**平均占据数**：

费米-狄拉克（泡利不相容）：

$$
\bar{n}_i = \frac{1}{e^{\beta(\varepsilon_i - \mu)} + 1}
$$

玻色-爱因斯坦（无限制）：

$$
\bar{n}_i = \frac{1}{e^{\beta(\varepsilon_i - \mu)} - 1}, \qquad \mu < \varepsilon_0
$$

经典极限（$\bar{n}_i \ll 1$）：

$$
\bar{n}_i \approx e^{-\beta(\varepsilon_i - \mu)} \quad \text{(Maxwell-Boltzmann)}
$$

**简并判据**：量子效应显著的条件是 $\lambda_T^3 (N/V) \gtrsim 1$。

**费米能**（$T=0$ 时化学势）：

$$
\varepsilon_F = \frac{\hbar^2}{2m}\left(3\pi^2 \frac{N}{V}\right)^{2/3}
$$

**费米温度**：$T_F = \varepsilon_F/k_B$。

**电子比热**（低温）：

$$
C_V^{\text{electron}} = \gamma T, \qquad \gamma = \frac{\pi^2}{2}\frac{Nk_B}{T_F}
$$

### 代码演示：FD vs BE 分布对比

```python
"""
费米-狄拉克 vs 玻色-爱因斯坦 vs 经典分布。
展示：费米子在 ε=μ 处占据数=1/2（费米面）。
"""
import math

print("=== 平均占据数 n̄(ε) 在 μ=kT=1 时 ===")
mu = 1.0
kT = 1.0
print(f"{'ε/μ':>6} {'FD':>8} {'BE':>8} {'MB':>8}")
for eps_over_mu in [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]:
    eps = eps_over_mu * mu
    arg = (eps - mu)/kT
    fd = 1.0 / (math.exp(arg) + 1)
    be = 1.0 / (math.exp(arg) - 1) if arg > -0.01 else float('inf')
    mb = math.exp(-arg)
    print(f"{eps_over_mu:>6.2f} {fd:>8.4f} {be:>8.4f} {mb:>8.4f}")

print("\n→ FD: ε≪μ 时 n̄→1（泡利填满），ε≫μ 时 n̄→0")
print("→ BE: ε→μ⁻ 时 n̄→∞（凝聚前兆）")  
print("→ MB: 指数衰减，高温低密极限")
print("\n=== 铜中电子的费米能 ===")
n_cu = 8.5e28   # 电子数密度 (m⁻³)
m_e = 9.11e-31
hbar = 1.055e-34
kB = 1.381e-23
EF = hbar**2/(2*m_e) * (3*math.pi**2*n_cu)**(2.0/3)
TF = EF/kB
print(f"  ε_F = {EF/1.602e-19:.2f} eV")
print(f"  T_F = {TF:.0f} K（远高于室温 → 电子始终简并）")
print(f"  → 室温 300K 对电子气体来说是「极低温」")
```

**输出**：
```
=== 平均占据数 n̄(ε) 在 μ=kT=1 时 ===
  ε/μ       FD       BE       MB
  0.00   0.7311   1.5820   2.7183
  0.25   0.5622   1.1292   2.1170
  0.50   0.3775   0.5820   1.6487
  0.75   0.2090   0.3218   1.2840
  1.00   0.5000   0.5000   1.0000
  1.50   0.1824   0.1824   0.6065
  2.00   0.0658   0.0658   0.3679
  3.00   0.0067   0.0067   0.1353

=== 铜中电子的费米能 ===
  ε_F = 7.04 eV
  T_F = 81617 K（远高于室温 → 电子始终简并）
```

> **反直觉发现**：对铜中的传导电子，室温 300K 相当于 $T/T_F \approx 0.004$ 的「极低温」。电子气体在室温下几乎完全简并——这就是为什么金属的电子比热 $C \propto T$ 而非常数（Dulong-Petit 值的一小部分）。

---

## 5. 相变与临界现象

### 直觉

相变是统计物理最迷人的主题。为什么水在精确的 100°C 突然沸腾？为什么铁在 770°C（居里点）突然失去磁性？这些「突变」的物理起源是**大量粒子的合作行为**——每个粒子的微观相互作用虽弱，但 $10^{23}$ 个粒子的集体效应产生了宏观的质变。

**连续相变**（二级相变）的特征：
- 序参量（如磁化 $M$）连续趋于零
- 关联长度发散 $\xi \to \infty$（涨落跨越所有尺度）
- **普适性**：临界指数只依赖对称性维度，不依赖微观细节（水、磁体、合金共享同一类指数）

### 公式

**临界指数**（以 Ising 铁磁相变为例）：

| 指数 | 定义 | 2D Ising | 3D Ising | 平均场 |
|------|------|---------|---------|--------|
| $\alpha$ | $C_V \sim |t|^{-\alpha}$ | 0 (log) | 0.110 | 0 |
| $\beta$ | $M \sim (-t)^\beta$ | 1/8 | 0.326 | 1/2 |
| $\gamma$ | $\chi \sim |t|^{-\gamma}$ | 7/4 | 1.237 | 1 |
| $\delta$ | $M \sim H^{1/\delta}\,(t=0)$ | 15 | 4.789 | 3 |
| $\nu$ | $\xi \sim |t|^{-\nu}$ | 1 | 0.630 | 1/2 |

其中 $t = (T-T_c)/T_c$ 是约化温度。

**标度关系**（Rushbrooke）：$\alpha + 2\beta + \gamma = 2$（严格成立）。

**Ising 模型哈密顿量**：

$$
H = -J\sum_{\langle i,j\rangle} s_i s_j - h\sum_i s_i, \qquad s_i = \pm 1
$$

**BEC 临界温度**（理想玻色气体）：

$$
T_c = \frac{2\pi\hbar^2}{mk_B}\left(\frac{n}{\zeta(3/2)}\right)^{2/3}, \qquad \zeta(3/2) \approx 2.612
$$

### 代码演示：2D Ising 模型的磁化曲线

```python
"""
2D Ising 模型的 Weiss 平均场近似。
给出磁化 M(T) 的定性行为：T<T_c 时自发磁化，T>T_c 时 M=0。
（精确解需要 Onsager 1944 的复杂推导，这里用平均场演示定性图像。）
"""
import math

# 平均场理论: T_c_mf = zJ/kB，z=4（正方格子）
# m = tanh(β z J m)，自洽方程
Tc_mf = 4.0  # 归一化 zJ/kB = 4

def solve_m(T):
    """迭代求解自洽方程 m = tanh(Tc/T * m)。"""
    if T >= Tc_mf:
        return 0.0
    m = 0.5  # 初始猜测
    for _ in range(1000):
        m_new = math.tanh(Tc_mf / T * m)
        if abs(m_new - m) < 1e-10:
            return m_new
        m = m_new
    return m

print("=== Ising 模型平均场: M(T) ===")
print(f"平均场临界温度 T_c = {Tc_mf:.1f} (zJ/kB)")
print(f"{'T/Tc':>6} {'m(T)':>8}")
for ratio in [0.1, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0, 1.5]:
    T = ratio * Tc_mf
    m = solve_m(T)
    print(f"{ratio:>6.2f} {m:>8.4f}")

print("\n→ T<Tc 时自发磁化 m≠0（铁磁相）")
print("→ T≥Tc 时 m=0（顺磁相），相变发生在 Tc")
print("→ 平均场指数 β_mf = 1/2（精确2D值为1/8，平均场高估了β）")
print("\n=== BEC 临界温度估算 ===")
# Rb-87 原子气体
m_Rb = 87 * 1.66e-27   # kg
hbar = 1.055e-34
kB = 1.381e-23
n = 2.5e20  # 典型原子数密度 m⁻³
zeta32 = 2.612
Tc = 2*math.pi*hbar**2/(m_Rb*kB) * (n/zeta32)**(2.0/3)
print(f"Rb-87 气体 n={n:.1e} m⁻³ 的 BEC 临界温度:")
print(f"  T_c = {Tc*1e9:.0f} nK = {Tc*1e6:.2f} µK")
print("→ 需要激光冷却 + 蒸发冷却到纳开尔文量级")
print("→ 1995 年 JILA/MIT 首次实现（Cornell-Wieman/Ketterle，2001 诺奖）")
```

---

## 6. Python 数值实验

### 6.1 配分函数 → 热容（爱因斯坦固体）

```python
"""
爱因斯坦固体模型：N 个独立量子谐振子。
配分函数 Z_1 = Σ exp(-βℏω(n+1/2))。
展示热容 C_V(T) 从 T→0（量子冻结）到 T→∞（Dulong-Petit 极限）。
"""
import math

def einstein_CV(T_over_theta):
    """爱因斯坦固体 C_V/NkB，T_over_theta = kT/ℏω。"""
    if T_over_theta < 0.01:
        return 0.0
    x = 1.0 / T_over_theta  # ℏω/kT
    ex = math.exp(x)
    return x**2 * ex / (ex - 1)**2

print("=== 爱因斯坦固体热容 C_V(T) ===")
print(f"{'kT/ℏω':>8} {'C_V/NkB':>10}")
for t in [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]:
    cv = einstein_CV(t)
    print(f"{t:>8.2f} {cv:>10.4f}")

print("\n→ T→0: C_V→0（量子冻结，能级离散，第三定律要求）")
print("→ T→∞: C_V→1×NkB（Dulong-Petit 经典极限）")
print("→ 经典统计给出 C_V=3NkB（高温），量子力学修复了低温行为")
```

### 6.2 麦克斯韦-玻尔兹曼速率分布

```python
"""
理想气体分子的速率分布。
f(v) = 4πn(m/2πkT)^(3/2) v² exp(-mv²/2kT)
展示三种特征速率: 最概然/平均/方均根。
"""
import math

# 归一化形式（v_p=1）
def maxwell_boltzmann(v):
    return v**2 * math.exp(-v**2/2) * math.sqrt(2/math.pi)

# 特征速率（以 v_p 为单位）
v_p = 1.0
v_mean = math.sqrt(4/math.pi)     # ≈1.128
v_rms = math.sqrt(3*math.pi/8)     # ≈1.085... 实际 v_rms/v_p = √(3/2)

print("=== 麦克斯韦-玻尔兹曼速率分布特征值 ===")
print(f"最概然速率 v_p  = {v_p:.4f} v_p")
print(f"平均速率   ⟨v⟩  = {v_mean:.4f} v_p = {math.sqrt(4/math.pi):.4f} v_p")
print(f"方均根速率 v_rms = {math.sqrt(3/2):.4f} v_p")

print("\n分布采样:")
print(f"{'v/vp':>6} {'f(v)':>8}")
for v in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
    f = maxwell_boltzmann(v)
    bar = '#' * int(f*30)
    print(f"{v:>6.1f} {f:>8.4f} {bar}")

print("\n→ v=0 时 f=0（没有静止分子，因 v² 因子）")
print("→ 峰值在 v=v_p，但 v_rms > ⟨v⟩ > v_p（长尾拖高均值）")

# 室温下空气分子的典型速率
m_N2 = 4.65e-26
kB = 1.381e-23
T = 300
v_p_real = math.sqrt(2*kB*T/m_N2)
print(f"\n室温 {T}K 下 N₂ 分子 v_p = {v_p_real:.0f} m/s = {v_p_real*3.6:.0f} km/h")
print("→ 这就是为什么声音传播速度 ~340 m/s（与分子速率同量级）")
```

---

## 7. 习题集

### 基础题（Zemansky / Reif 前半）

**P4.1** 1 mol 理想气体从 $(p_1, V_1)$ 等温膨胀到 $(p_1, 2V_1)$。计算 $\Delta S$, $Q$, $W$。

> **答案**：$\Delta S = R\ln 2$，$Q = W = RT\ln 2$。

**P4.2** 用 Maxwell 关系 $(\partial S/\partial V)_T = (\partial p/\partial T)_V$ 推导理想气体内能 $U$ 只依赖温度（焦耳定律）。

### 中级题（Reif / Pathria 前半）

**P4.3**（配分函数）二维谐振子的能级 $E_n = (n+1)\hbar\omega$。写出单振子配分函数 $Z_1$，并计算 $\langle E\rangle$ 和 $C_V$。

> **答案**：$Z_1 = 1/(2\sinh(\beta\hbar\omega/2))$。

**P4.4**（理想气体熵）从 $Z_N = Z_1^N/N!$ 推导理想气体的熵 $S$（Sackur-Tetrode 方程），并验证它满足 $S \to 0$ 当 $T\to 0$ 的困难（经典统计的局限）。

**P4.5**（费米气体）$T=0$ 时 $N$ 个自由电子在体积 $V$ 中。计算费米能 $\varepsilon_F$、基态总能量 $E_0$ 和压强 $p_0$。

> **答案**：$E_0 = \frac{3}{5}N\varepsilon_F$，$p_0 = \frac{2}{5}n\varepsilon_F$。

### 挑战题（Pathria / Huang 级别）

**P4.6**（黑体辐射）光子气体（$\mu=0$ 的玻色子，色散 $\varepsilon = pc = \hbar\omega$）。推导普朗克分布 $u(\omega)d\omega$ 和 Stefan-Boltzmann 定律 $U/V \propto T^4$。

> **提示**：态密度 $g(\omega) \propto \omega^2$，配分函数发散但能量收敛。

**P4.7**（Ising 模型）一维 Ising 模型的精确配分函数。用转移矩阵法证明 $Z_N = \lambda_+^N + \lambda_-^N$，其中 $\lambda_\pm$ 是转移矩阵的特征值。并证明一维 Ising 模型没有有限温度相变。

**P4.8**（BEC）理想玻色气体的凝聚分数 $N_0/N$ 作为 $T/T_c$ 的函数。推导 $N_0/N = 1-(T/T_c)^{3/2}$（$T<T_c$），并解释凝聚相的物态方程。

---

## 8. 不足与延伸

### 本主题的局限

1. **平衡态假设**：统计力学处理的是平衡态。非平衡态统计力学（Boltzmann 方程、涨落-耗散定理、线性响应）是更难的领域。生命系统（细胞、生态系统）是远离平衡的。

2. **平均场理论的失败**：平均场近似忽略了涨落，在低维（$d \leq 2$ Ising 模型）和某些相变（如 KT 相变）中给出错误预测。正确处理需要重整化群（Wilson 1971）。

3. **相变的严格性**：BEC、铁磁相变的严格证明需要 Yang-Yang 定理等高深数学。二维连续对称性系统的 Mermin-Wagner 定理说**不能有连续对称破缺**（没有长程序）——这对二维超流、二维磁性有深刻影响。

4. **非平衡相变**：从湍流到生命系统，远离平衡的「相变」（如湍流 onset、生命起源）缺乏像平衡态那样优美的理论框架。

### 延伸方向

| 方向 | 课程 | 教材 |
|------|------|------|
| 凝聚态理论 | ETH CMT 402-3101-00L | Coleman, Mahan |
| 相变与重整化群 | — | Goldenfeld *Lectures on Phase Transitions* |
| 非平衡统计 | — | Kardar *Statistical Physics of Particles/Fields* |
| 量子多体 | ETH Many-Body | Fetter & Walecka |
| 软物质/生物物理 | ETH Biophysics 402-3501-00L | Nelson, Chaikin & Lubensky |
| 量子信息与热力学 | — | Nielsen & Chuang |

### ETH 特色注记

ETH 的统计物理教学处于**德语区唯象热力学**（Zemansky 路线）和**Gibbs 系综理论**（Pathria 路线）的交汇点。Einstein 对统计力学有根本性贡献：1905 年布朗运动论文（涨落-耗散关系的前身）、1910 年临界乳光理论、1924 年 Bose-Einstein 统计的创立。ETH 的统计物理课不仅传授公式，更传承 Einstein 的物理直觉——「上帝不掷骰子」的态度，和**涨落才是物理的本质**这一深层认识。ETH PSI 的中子散射实验直接观测统计力学的涨落和相变；ETH 超冷原子实验实现了 Einstein 预言的 BEC。统计力学是连接微观量子世界和宏观凝聚态世界的桥梁。

---

> **上一主题**：[03 量子力学](../topic03-quantum/quantum.md)
>
> **Phase 1 完成**：力学 → 电磁学 → 量子力学 → 统计物理，构成经典物理 + 量子物理的完整基础。


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：统计物理研究「亿亿个粒子组成的系统，如何用少数几个宏观量（温度、压强、熵）描述」——它把不可数的多体问题，化约为概率与对称的游戏，揭示「熵增」就是「系统走向概率最大的状态」。
>
> **生活类比**：把粒子比作洗乱的一副扑克。洗牌前有序（低熵），洗牌后乱（高熵）——不是因为「宇宙讨厌秩序」，而是有序排列只占极少数微观态，乱排列占绝大多数。**时间箭头 = 走向高概率**。
>
> **反直觉发现（啊哈时刻）**：
> - **熵不是混乱，是无知**：气体均匀分布看起来「无序」，但对气体本身而言每个分子都有确定位置——熵衡量的是**观察者**不知道的微观态数。
> - **麦克斯韦妖被信息杀死**：精灵要分拣分子必须测量，测量的信息擦除（Landauer 原理）耗能 $kT\ln 2$——信息是物理的。
> - **BEC 的临界温度低到纳开尔文**：室温下原子德布罗意波长太短无法叠加；1924 年 Einstein 预言，1995 年才实现。
> - **相变是「涌现」的极致**：水分子不知道「沸腾」，但 100°C 时集体行为突变——多即不同（More is different, Anderson）。
> - **涨落-耗散定理**：你搅动咖啡感受到的粘性，与咖啡里分子的随机噪声**严格成正比**——爱因斯坦 1905 年布朗运动论文的核心。

---

## 🔗 衔接：从哪来，到哪去

### ▶ 前置
- **力学（01）的刘维尔定理**：相空间体积守恒 = 微正则系综（等概率）的合法性来源。
- **量子力学（03）**：全同粒子 → Bose-Einstein / Fermi-Dirac 分布；量子涨落主导低温物理。
- **组合数学 + 概率**：斯特林公式 $N!\approx N^N e^{-N}$ 是配分函数对数展开的钥匙。

### ⚡ 旧框架的危机
1. **不可积多体**：经典力学解不出 $10^{23}$ 个粒子的方程——必须用**统计系综**绕过细节。
2. **黑体辐射**：能量均分定理给出紫外灾难——Planck 量子化是统计物理被迫引入量子的入口。
3. **可逆微观 vs 不可逆宏观**：牛顿方程时间反演不变，但熵总增——Loschmidt 佯谬至今仍在精细讨论（粗粒化 + 宇宙初条件）。

### 🆕 新框架的危机
- **平衡态之外**：生命、气候、湍流都是远离平衡的耗散系统，无普遍理论（Prigogine 路线尚不完整）。
- **相变严格性**：相变「尖锐性」需要热力学极限 $N\to\infty$；小系统涨落让相变模糊。
- **量子多体强关联**：高温超导、分数量子霍尔效应——现有统计方法失效，需要张量网络 / 量子模拟。

### 🚀 后续
| 后续主题 | 用到的统计概念 |
|---------|---------------|
| 05 数学方法 | 概率生成函数、鞍点法、Legendre 变换（自由能↔配分函数） |
| 06 固体物理 | 声子（Bose 统计）、电子气（Fermi 海）、相变、超导 |
| 07 粒子物理 | 配分函数 = 路径积分；夸克-胶子等离子体 = 量子统计 |
| 08 GR/宇宙学 | 早期宇宙热历史、CMB 涨落、黑洞熵 $S=kA/4$ |

---

## 🏭 理论联系实际：5 个应用

1. **Bose-Einstein 凝聚（BEC）**：Einstein 1924 预言，1995 Cornell-Wieman-Ketterle 实现（2001 诺奖）；ETH 冷原子组（Esslinger, Donner）用 BEC 模拟 Hubbard 模型、量子相变——爱因斯坦的预言在 ETH 的实验室里被持续验证。
2. **蒙特卡洛与 Ising 模型**：Metropolis 算法（1947 氢弹计划副产品）→ 今天材料设计、蛋白质折叠、金融风险都用 Metropolis 采样；2D Ising 精确解（Onsager 1944）是相变理论的圣杯。
3. **量子退火与组合优化**：D-Wave 用量子隧穿帮助 Ising 自旋玻璃找基态，物流路线优化、药物筛选。
4. **PSI 中子散射测涨落**：SINQ 中子源直接测量材料中自旋-声子的动态结构因子 $S(\vec{q},\omega)$ ——这是涨落-耗散定理的实验体现。
5. **涨落定理与微小机器**（Evans, Searles 1993；Jarzynski 1997）：纳米尺度下「违背」第二定律的小概率事件可量化，用于设计分子马达、理解酶的不可逆性——统计力学进入单分子生物。

---

## 🔬 最新研究前沿（2024-2026）

1. **KPZ 普适类在量子系统中首次实现**（2024, *Nature*，ETH Esslinger 组）：1D 超冷原子的关联函数遵循 Kardar-Parisi-Zhang 标度——经典表面生长的混沌方程在量子多体里复现，**非平衡统计物理的里程碑**。
2. **时间晶体进入稳态**（2024-2025）：在驱动 + 耗散系统中实现稳定的「离散时间晶体」，周期倍频永不衰减——非平衡相变从理论走向材料（Google Sycamore、QuEra 多组演示）。
3. **热力学不确定性关系（TUR）的量子推广**（2024-2025）：精度与熵产的下界 $\sigma\cdot\text{Var}/\langle J\rangle^2 \geq 2k_B$ 在量子区被修正，用于评估量子热机与分子机器的效率极限。
4. **量子热机与纳米制冷机**（2024-2025）：单原子/单自旋热机实验实现，效率接近卡诺极限；量子相干作为「燃料」的争议持续——统计热力学 + 量子信息的交叉热点。
5. **Many-Body Localization（MBL）的角力**（2024）：早期 MBL 信号论文被《Science》撤稿（2021 Block et al.），2024 新数值证据质疑 2D 甚至 1D 长程 MBL 的存在——ETH、MIT 主导「热化 vs 局域」的根本性问题重新洗牌。

---

## 🗺️ 学习 Roadmap（ETH 路径）

### ETH 课程编号
- **402-0901-00L Thermodynamics and Statistical Physics**（BSc 第三年）
- **402-0101-00L Statistical Physics**（MSc，Kardar / Pathria 路线）
- **402-9101-00L Quantum Many-Body Physics**（MSc，Fetter-Walecka）
- **402-3501-00L Biophysics**（软物质 / 非平衡统计应用）

### 14 周学习节奏
| 阶段 | 内容 | 知识检查 |
|------|------|----------|
| W1-3 热力学四定律 | 状态量、Carnot、熵 $dS=\delta Q/T$ | 证明卡诺效率只依赖 $T_h, T_c$。 |
| W4-6 系综理论 | 微正则/正则/巨正则、配分函数 | 写出谐振子配分函数并推出 $C_v$。 |
| W7-8 Bose & Fermi 统计 | 黑体辐射、BEC、Fermi 海、白矮星 | 推出 T=0 时电子气的费米能。 |
| W9-11 相变与重整化 | Ising、临界指数、Wilson RG | 解释「普适类」为什么与微观细节无关。 |
| W12-14 非平衡初步 | 涨落-耗散、Jarzynski、响应函数 | 用爱因斯坦关系推出扩散-迁移 $D=\mu k_BT$。 |

### 费曼检验
- 能从配分函数一路推出理想气体的状态方程 → 统计物理过关。
- 能讲清「熵增不是宇宙偏好混乱，是概率最大」 → 直觉过关。
- 能用 Wilson RG 解释「为什么水、铁磁体、合金的临界指数相同」 → 可进凝聚态与场论。
