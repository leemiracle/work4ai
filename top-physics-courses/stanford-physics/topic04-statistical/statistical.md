# Stanford 物理系 Phase 1 · 主题 4：统计物理与热力学

> **课程谱系**：PHYS 45/107 (热学与统计) → PHYS 170 (统计力学) → PHYS 220 (研究生统计)
>
> **教材阶梯**：Schroeder《Introduction to Thermal Physics》→ Kittel & Kroemer《Thermal Physics》2ed → Pathria & Beale《Statistical Mechanics》4ed
>
> **Stanford 特色**：从 SLAC 的粒子探测器冷却系统到凝聚态实验的低温物理，统计力学是连接微观与宏观的桥梁。Stanford 在量子统计、相变理论、凝聚态多体物理领域持续领先

---

## 目录

1. [热力学基础](#1-热力学基础)
2. [统计力学基本原理](#2-统计力学基本原理)
3. [系综理论](#3-系综理论)
4. [量子统计](#4-量子统计)
5. [相变与临界现象](#5-相变与临界现象)
6. [Stanford/SLAC 关联](#6-stanfordlac-关联)
7. [习题与解答](#7-习题与解答)
8. [代码实验](#8-代码实验)
9. [局限与延伸](#9-局限与延伸)

---

## 1. 热力学基础

### 1.1 直觉

热力学的核心是**宏观**规律——不需要知道 $10^{23}$ 个分子各自在哪，只需少数几个量（$T, P, V, S$）就能预测系统行为。Schroeder 教材的精妙：从微观统计出发「推导」热力学，而非黑盒公理。

### 1.2 热力学四定律

**第零定律**：若 $A$ 与 $B$ 热平衡，$B$ 与 $C$ 热平衡，则 $A$ 与 $C$ 热平衡 → 温度 $T$ 存在。

**第一定律**（能量守恒）：

$$\boxed{dU = \delta Q - \delta W = T\,dS - P\,dV}$$

**第二定律**（熵增）：孤立系统 $\Delta S \geq 0$。等号仅对可逆过程。

**第三定律**（Nernst 定理）：$T\to 0$ 时 $S\to S_0$（常数，对完美晶体 $S_0 = 0$）。

### 1.3 热力学势

| 势 | 定义 | 自然变量 |
|----|------|----------|
| 内能 $U$ | — | $S, V, N$ |
| 焓 $H$ | $U + PV$ | $S, P, N$ |
| 亥姆霍兹 $F$ | $U - TS$ | $T, V, N$ |
| 吉布斯 $G$ | $U + PV - TS = \mu N$ | $T, P, N$ |

麦克斯韦关系（来自全微分 $dF = -S\,dT - P\,dV + \mu\,dN$）：

$$\left(\frac{\partial S}{\partial V}\right)_T = \left(\frac{\partial P}{\partial T}\right)_V$$

### 1.4 热机与卡诺循环

卡诺效率（两个热源 $T_H > T_C$）：

$$\eta_{\text{max}} = 1 - \frac{T_C}{T_H}$$

这是所有热机的理论上限。

---

## 2. 统计力学基本原理

### 2.1 直觉

统计力学的核心假设：**等概率原理**——孤立系统的所有可达微观态等概率出现。宏观量是微观态的（加权）平均。

Boltzmann 的伟大洞察：**熵是微观态数的对数**。

### 2.2 微观态与熵

$$\boxed{S = k_B \ln\Omega}$$

$\Omega$ 是宏观态对应的微观态数。这就是 Boltzmann 墓碑上的公式。

### 2.3 配分函数

**玻尔兹曼分布**（正则系综，系统与热浴 $T$ 接触）：

$$P_i = \frac{e^{-\beta E_i}}{Z}, \quad \beta = \frac{1}{k_B T}$$

配分函数：

$$\boxed{Z = \sum_i e^{-\beta E_i}}$$

所有热力学量从 $Z$ 导出：

$$F = -k_B T\ln Z, \quad U = -\frac{\partial\ln Z}{\partial\beta}, \quad S = k_B\left(\ln Z - \beta\frac{\partial\ln Z}{\partial\beta}\right)$$

### 2.4 理想气体

单原子理想气体的配分函数：

$$Z = \frac{1}{N!}\left(\frac{V}{\lambda^3}\right)^N, \quad \lambda = \frac{h}{\sqrt{2\pi m k_B T}}$$

$\lambda$ 是**热德布罗意波长**。推导出 $PV = Nk_BT$ 和 $U = \frac{3}{2}Nk_BT$。

熵（Sackur-Tetrode 公式）：

$$S = Nk_B\left[\ln\left(\frac{V}{N\lambda^3}\right) + \frac{5}{2}\right]$$

---

## 3. 系综理论

### 3.1 直觉

三种系综对应不同的环境约束：

| 系综 | 守恒量 | 接触对象 | 分布 |
|------|--------|----------|------|
| 微正则 (NVE) | $N, V, E$ | 孤立 | 等概率 |
| 正则 (NVT) | $N, V, T$ | 热浴 | 玻尔兹曼 |
| 巨正则 ($\mu$VT) | $\mu, V, T$ | 粒子+热浴 | 玻色/费米 |

### 3.2 正则系综

密度矩阵（经典版本，相空间概率密度）：

$$\rho(p, q) = \frac{1}{Z}e^{-\beta H(p,q)}$$

$$Z = \int e^{-\beta H(p,q)}\,dp\,dq$$

### 3.3 巨正则系综

粒子数可变（与粒子库交换），化学势 $\mu$：

$$\mathcal{Z} = \sum_{N=0}^{\infty} e^{\beta\mu N} Z_N = \sum_{N,i} e^{-\beta(E_{N,i} - \mu N)}$$

平均粒子数：$\langle N\rangle = \frac{1}{\beta}\frac{\partial\ln\mathcal{Z}}{\partial\mu}$。

巨正则势：$\Omega = -PV = -k_B T\ln\mathcal{Z}$。

### 3.4 能量均分定理

经典系统中，每个二次自由度贡献 $\frac{1}{2}k_BT$ 到平均能量：

- 单原子理想气体：$U = \frac{3}{2}Nk_BT$（3 个平动）
- 双原子分子：$U = \frac{5}{2}Nk_BT$（高温，含 2 个转动）
- 固体（Dulong-Petit）：$U = 3Nk_BT$（3 动能 + 3 势能）

**均分定理在低温失效**——量子效应冻结自由度。这是 Einstein/Debye 固体理论的起点。

---

## 4. 量子统计

### 4.1 全同性原理

不可分辨粒子要求波函数对称（玻色子）或反对称（费米子）：

- **玻色子**（整数自旋）：$\Psi(...,\mathbf{r}_i,...,\mathbf{r}_j,...) = +\Psi(...,\mathbf{r}_j,...,\mathbf{r}_i,...)$
- **费米子**（半整数自旋）：$\Psi(...,\mathbf{r}_i,...,\mathbf{r}_j,...) = -\Psi(...,\mathbf{r}_j,...,\mathbf{r}_i,...)$

Pauli 不相容原理：费米子不能占据同一量子态。

### 4.2 量子分布函数

**玻色-爱因斯坦分布**：

$$\boxed{\bar{n}_\epsilon = \frac{1}{e^{(\epsilon - \mu)/(k_B T)} - 1}}$$

**费米-狄拉克分布**：

$$\boxed{\bar{n}_\epsilon = \frac{1}{e^{(\epsilon - \mu)/(k_B T)} + 1}}$$

经典极限（$\epsilon - \mu \gg k_BT$）两者都退化为麦克斯韦-玻尔兹曼分布 $e^{-\beta(\epsilon-\mu)}$。

### 4.3 简并费米气体

$T = 0$ 时费米子填满到费米能 $\epsilon_F$：

$$\epsilon_F = \frac{\hbar^2}{2m}\left(3\pi^2 n\right)^{2/3}$$

费米温度 $T_F = \epsilon_F/k_B$。金属中 $T_F \sim 10^4$ K，室温 $T \ll T_F$，电子气高度简并。

基态能量：$U_0 = \frac{3}{5}N\epsilon_F$。

**反直觉**：$T=0$ 时费米气体仍有巨大动能和压强！这是中子星简并压的来源。

### 4.4 黑体辐射（光子气体）

光子是玻色子，化学势 $\mu = 0$（光子数不守恒）。Planck 分布：

$$u(\nu) = \frac{8\pi h\nu^3}{c^3}\frac{1}{e^{h\nu/k_BT} - 1}$$

积分得 Stefan-Boltzmann 定律：

$$j = \sigma T^4, \quad \sigma = \frac{2\pi^5 k_B^4}{15 h^3 c^2}$$

**Wien 位移定律**：$\nu_{\max} \propto T$（峰值频率随温度线性增长）。

### 4.5 玻色-爱因斯坦凝聚 (BEC)

当温度低于临界温度 $T_c$，宏观数量玻色子凝聚到基态：

$$T_c = \frac{2\pi\hbar^2}{mk_B}\left(\frac{n}{\zeta(3/2)}\right)^{2/3}$$

凝聚分数 $N_0/N = 1 - (T/T_c)^{3/2}$。

---

## 5. 相变与临界现象

### 5.1 一阶相变与连续相变

**一阶相变**：熵/体积突变，吸收潜热。例：冰→水。

**连续相变**（二阶）：序参量连续趋零，比热/磁化率等发散。例：铁磁居里点、超导转变。

### 5.2 序参量与对称性破缺

| 系统 | 序参量 | 对称性破缺 |
|------|--------|------------|
| 铁磁 | 磁化 $M$ | 旋转 → 选定方向 |
| 气液 | $\rho_l - \rho_g$ | 平移 |
| 超导 | 凝聚波函数 $\psi$ | $U(1)$ 规范 |
| 超流 | $\psi$ | $U(1)$ 规范 |

### 5.3 临界指数

接近临界点 $T_c$ 时，各量以幂律发散：

$$M \sim |T-T_c|^\beta, \quad \chi \sim |T-T_c|^{-\gamma}, \quad C \sim |T-T_c|^{-\alpha}$$

**普适性**：临界指数只依赖维度和序参量分量数，与微观细节无关！这是统计力学最深刻的结论之一。

### 5.4 Ising 模型

最简单的相变模型。1D 无相变；2D (Onsager 1944) 在 $T_c = 2J/(k_B\ln(1+\sqrt{2}))$ 发生铁磁相变。

平均场理论（忽略涨落）给出定性图像但临界指数不准（如 $\beta_{\text{MF}} = 1/2$ vs 2D Ising 精确值 $\beta = 1/8$）。

### 5.5 重整化群

Wilson 的重整化群（RG）：相变的本质是**不同尺度的耦合**。在临界点，关联长度发散，系统「忘记」微观尺度，呈现**标度不变性**。这就是普适性的根源。

---

## 6. Stanford/SLAC 关联

| 实验/设施/理论 | 统计物理原理 |
|----------------|--------------|
| **SLAC 粒子探测器冷却** | 低温热力学，超导磁体液氦冷却 |
| **凝聚态实验组** | 量子相变、高温超导 |
| **KIPAC 宇宙学** | 早期宇宙热历史，CMB 黑体辐射 |
| **超冷原子实验** | BEC 实现，量子模拟 |
| **蛋白质折叠 (Stanford Bio-X)** | 统计力学应用于生物大分子 |
| **高效太阳能电池** | 热力学效率极限，光子统计 |

**Stanford 在统计物理的贡献**

- **Robert Laughlin**（1998 诺奖）：分数量子霍尔效应的统计力学解释
- **Steven Chu**（1997 诺奖，前 Stanford）：激光冷却与原子阱（BEC 前驱）
- **Srinivas Eng_datasets**：量子相变实验

**SLAC 的统计物理侧影**

LCLS（X 射线自由电子激光）探测物质结构需要统计力学解读散射数据。超导加速器腔的运行依赖低温热力学。每 $10^{13}$ 个粒子的束流统计涨落是加速器物理的核心问题。

---

## 7. 习题与解答

### 习题 1（PHYS 107 风格 · Schroeder 问题 2.18 简化）

两个宏观物体 $A, B$，热容 $C_A, C_B$（常数），初始温度 $T_A > T_B$。热接触达到平衡。求最终温度和总熵变。

<details>
<summary>解答</summary>

能量守恒：$C_A(T_f - T_A) + C_B(T_f - T_B) = 0$。

$$T_f = \frac{C_A T_A + C_B T_B}{C_A + C_B}$$

熵变（每个物体温度从 $T_i$ 到 $T_f$）：$\Delta S_i = C_i\ln(T_f/T_i)$。

$$\Delta S_{\text{total}} = C_A\ln\frac{T_f}{T_A} + C_B\ln\frac{T_f}{T_B}$$

由 AM-GM 不等式可证 $\Delta S_{\text{total}} > 0$（热从热到冷）。

特例 $C_A = C_B = C$：$T_f = (T_A+T_B)/2$，$\Delta S = C\ln\frac{(T_A+T_B)^2}{4T_AT_B} > 0$。
</details>

### 习题 2（PHYS 107 · 理想气体配分函数）

推导单原子理想气体的配分函数并验证 $PV = Nk_BT$。

<details>
<summary>解答</summary>

单粒子能级（箱中）：$\epsilon \approx p^2/(2m)$（准连续）。

单粒子配分函数：

$$Z_1 = \frac{1}{h^3}\int d^3p\,d^3r\, e^{-\beta p^2/(2m)} = \frac{V}{h^3}(2\pi m k_BT)^{3/2} = \frac{V}{\lambda^3}$$

$N$ 个不可分辨粒子：$Z_N = Z_1^N / N!$（Gibbs 因子防止过计数）。

亥姆霍兹自由能：

$$F = -k_BT\ln Z_N = -k_BT\left[N\ln\frac{V}{\lambda^3} - \ln N!\right]$$

压强：

$$P = -\left(\frac{\partial F}{\partial V}\right)_T = \frac{Nk_BT}{V}$$

故 $PV = Nk_BT$。$\square$
</details>

### 习题 3（PHYS 170 风格 · 自旋系统）

$N$ 个独立自旋 1/2 在磁场 $B$ 中，磁矩 $\mu$。求配分函数、磁化强度和高温磁化率。

<details>
<summary>解答</summary>

每个自旋能级 $\epsilon = \mp\mu B$（平行/反平行）。

单自旋配分函数：

$$Z_1 = e^{\beta\mu B} + e^{-\beta\mu B} = 2\cosh(\beta\mu B)$$

$N$ 个独立自旋：$Z = Z_1^N = [2\cosh(\beta\mu B)]^N$。

磁化强度：

$$M = N\mu\tanh\left(\frac{\mu B}{k_BT}\right)$$

高温极限 ($\mu B \ll k_BT$)：$\tanh x \approx x$。

$$\boxed{M \approx \frac{N\mu^2 B}{k_BT} \implies \chi = \frac{\mu_0 M}{B} = \frac{N\mu^2}{k_BT}}$$

这就是 **Curie 定律**：磁化率 $\chi \propto 1/T$。
</details>

### 习题 4（PHYS 220 风格 · 简并费米气体）

铜的电子密度 $n = 8.5\times 10^{28}\,\text{m}^{-3}$。求费米能、费米温度和零点压强。

<details>
<summary>解答</summary>

费米能：

$$\epsilon_F = \frac{\hbar^2}{2m_e}(3\pi^2 n)^{2/3}$$

代入 $n = 8.5\times 10^{28}$：

$\epsilon_F = \frac{(1.055\times10^{-34})^2}{2\times 9.11\times10^{-31}}(3\pi^2\times 8.5\times10^{28})^{2/3} = 1.13\times10^{-18}$ J $= 7.0$ eV。

费米温度 $T_F = \epsilon_F/k_B = 7.0\,\text{eV}/(8.617\times10^{-5}\,\text{eV/K}) = 8.1\times10^4$ K。

**反直觉**：室温 ($300$ K) 远低于费米温度。铜中电子的行为像 $T=0$ 的费米海，只有费米面附近的少量电子参与热运动——这就是为什么电子比热 $\propto T$（而非经典预言的常数）。

零点压强 $P_0 = \frac{2}{3}\frac{U_0}{V} = \frac{2}{5}n\epsilon_F \approx 4\times 10^{10}$ Pa $= 4\times 10^5$ atm！这是中子星抵抗引力的简并压的微观版本。
</details>

---

## 8. 代码实验

### 实验 8.1：熵与热力学第二定律（二态系统）

```python
"""
PHYS 45 实验：二态系统的熵
N 个粒子可处于高能/低能态，计算微观态数与熵
纯标准库
"""
import math

def log_factorial(n):
    """Stirling 近似 ln(n!)"""
    if n <= 1:
        return 0.0
    return n*math.log(n) - n + 0.5*math.log(2*math.pi*n)

def entropy_two_state(N, n_excited):
    """N 粒子中 n 激发态的熵 (k_B 单位)
    Omega = C(N, n) = N!/(n!(N-n)!)
    S = k_B * ln(Omega)"""
    n = n_excited
    if n == 0 or n == N:
        return 0.0
    log_omega = log_factorial(N) - log_factorial(n) - log_factorial(N-n)
    return log_omega

# 扫描激发态数
N = 1000
print(f"=== 二态系统熵 (N={N} 粒子, k_B=1) ===")
print(f"{'n_excited':>10} {'n/N':>8} {'S/k_B':>10} {'S_max?':>8}")
print("-" * 40)
max_S = 0
max_n = 0
for ratio in [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    n = int(ratio * N)
    S = entropy_two_state(N, n)
    flag = "<-- MAX" if S > max_S else ""
    if S > max_S:
        max_S, max_n = S, n
    print(f"{n:10d} {ratio:8.2f} {S:10.2f} {flag:8}")

print(f"\n最大熵在 n/N = {max_n/N:.2f}（最无序态）")
print(f"S_max = k_B * ln(2^N) approx = {N*math.log(2):.1f} k_B")
print(f"实际 S_max = {max_S:.1f} k_B (近似接近 N*ln2)")
print("\n反直觉：最概然宏观态对应最大微观态数（熵）。")
print("热力学第二定律 = 系统自发趋向微观态数最多的状态。")
```

### 实验 8.2：费米-狄拉克与玻色-爱因斯坦分布对比

```python
"""
PHYS 170 实验：量子统计分布对比
费米-狄拉克 vs 玻色-爱因斯坦 vs 麦克斯韦-玻尔兹曼
纯标准库
"""
import math

def fermi_dirac(epsilon, mu, kT):
    """费米-狄拉克分布"""
    x = (epsilon - mu) / kT
    if x > 500:
        return 0.0
    return 1.0 / (math.exp(x) + 1)

def bose_einstein(epsilon, mu, kT):
    """玻色-爱因斯坦分布"""
    x = (epsilon - mu) / kT
    if x < -500:
        return float('inf')
    if x == 0:
        return float('inf')
    return 1.0 / (math.exp(x) - 1)

def maxwell_boltzmann(epsilon, mu, kT):
    """经典极限"""
    x = (epsilon - mu) / kT
    if x > 500:
        return 0.0
    return math.exp(-x)

# 参数：注意 BE 要求 mu < epsilon_min（对玻色子，化学势不能超过基态能量）
# 这里用两套化学势分别对比
mu_fermi = 5.0   # 费米子：mu 可以取任意值，epsilon < mu 时占据数 ~1
mu_bose = -1.0   # 玻色子：mu 必须 < epsilon_min(=0)，否则分布发散
kT = 1.0

print(f"=== 费米-狄拉克 vs 玻色-爱因斯坦 (kT={kT}) ===")
print(f"费米子 mu = {mu_fermi}，玻色子 mu = {mu_bose}")
print(f"{'eps':>6} {'FD(mu=5)':>12} {'BE(mu=-1)':>12} {'MB':>12}")
print("-" * 46)
for eps in [0, 1, 2, 3, 4, 5, 6, 8, 10]:
    fd = fermi_dirac(eps, mu_fermi, kT)
    be = bose_einstein(eps, mu_bose, kT)
    mb_f = maxwell_boltzmann(eps, mu_fermi, kT)
    mb_b = maxwell_boltzmann(eps, mu_bose, kT)
    print(f"{eps:6.1f} {fd:12.4f} {be:12.4f} {mb_b:12.4f}")

print("\n=== 关键观察 ===")
print("1. 费米子：eps < mu_F 时 n~1（费米海填满），eps > mu_F 时 n~0（空）")
print("   低温下费米面 '阶梯' 清晰；mu_F 即费米能")
print("2. 玻色子：eps -> mu_B 时 n -> 无穷（BEC 凝聚的前兆）")
print("   化学势必须 mu < epsilon_min，否则物理上禁止")
print("3. 高能区 (eps >> mu) 三者趋于一致（经典极限）")
print("\n这就是为什么金属电子用 FD，光子用 BE，普通气体用 MB。")
```

### 实验 8.3：黑体辐射数值积分

```python
"""
PHYS 107 实验：黑体辐射谱
Planck 分布数值积分 -> Stefan-Boltzmann 定律
纯标准库
"""
import math

def planck_spectral_density(x):
    """无量纲 Planck 分布
    u(x) = x^3 / (e^x - 1), x = h*nu/(k_B*T)"""
    if x < 1e-10:
        return 0.0
    if x > 500:
        return 0.0
    return x**3 / (math.exp(x) - 1)

def simpson_integrate(f, x_min, x_max, n=1000):
    """辛普森积分"""
    if n % 2 == 1:
        n += 1
    h = (x_max - x_min) / n
    s = f(x_min) + f(x_max)
    for i in range(1, n):
        x = x_min + i*h
        s += 4*f(x) if i % 2 == 1 else 2*f(x)
    return s * h / 3

# 积分 Planck 分布：总能量密度
# u_total = (integral u(x) dx) * (kT)^4 * const
# 解析结果：integral x^3/(e^x-1) dx from 0 to inf = pi^4/15
integral = simpson_integrate(planck_spectral_density, 0.001, 50, 5000)
exact = math.pi**4 / 15
print("=== Planck 积分（Stefan-Boltzmann） ===")
print(f"数值积分: {integral:.6f}")
print(f"解析值 pi^4/15: {exact:.6f}")
print(f"误差: {abs(integral-exact)/exact*100:.4f}%")

# Wien 位移定律数值验证
# 求谱密度极大值：du/dx = 0 -> 3(1-e^{-x}) = x
print("\n=== Wien 位移定律 ===")
best_x, best_u = 0, 0
for i in range(1, 10000):
    x = i * 0.01
    u = planck_spectral_density(x)
    if u > best_u:
        best_u, best_x = u, x
print(f"峰值位置 x_max = h*nu_max/(kT) = {best_x:.3f}")
print(f"解析值（3+W(-3e^{-3}) ≈ 2.821）")
print(f"=> nu_max = 2.821 * kT/h, 与 T 成正比（Wien 律）")

# 不同温度的峰值
h = 6.626e-34
k_B = 1.381e-23
c = 3.0e8
print(f"\n=== 各温度黑体峰值波长 ===")
print(f"{'T (K)':>10} {'lambda_max (nm)':>16} {'波段':>10}")
for T, name in [(2.725, "CMB"), (300, "室温"), (5778, "太阳表面"), 
                 (3000, "白炽灯"), (100000, "热星")]:
    # Wien: lambda_max * T = 2.898e-3 m*K (波长形式 x=4.965)
    lam_max = 2.898e-3 / T * 1e9  # nm
    if lam_max > 1e6:
        band = "射电/微波"
    elif lam_max > 700:
        band = "红外"
    elif lam_max > 400:
        band = "可见光"
    elif lam_max > 10:
        band = "紫外"
    else:
        band = "X射线"
    print(f"{T:10.0f} {lam_max:16.1f} {band:>10}")

print(f"\n反直觉：CMB (2.7K) 峰值在微波 ~1mm，所以叫'微波背景'！")
print(f"太阳 5778K 峰值在可见光 ~500nm——眼睛进化适应了太阳光谱。")
```

### 实验 8.4：1D/2D Ising 模型（Monte Carlo）

```python
"""
PHYS 220 实验：Ising 模型 Monte Carlo 模拟
Metropolis 算法，观察铁磁相变
纯标准库
"""
import random
import math

def ising_energy(spins, J=1.0):
    """1D Ising 链能量 (周期边界)"""
    N = len(spins)
    E = 0.0
    for i in range(N):
        E -= J * spins[i] * spins[(i+1) % N]
    return E

def magnetization(spins):
    return sum(spins) / len(spins)

def metropolis_1d(spins, N, J, kT, steps):
    """Metropolis 算法"""
    for _ in range(steps):
        i = random.randrange(N)
        # 翻转 i 的能量变化（1D 最近邻）
        nb = spins[(i-1) % N] + spins[(i+1) % N]
        dE = 2 * J * spins[i] * nb
        if dE < 0 or random.random() < math.exp(-dE / kT):
            spins[i] *= -1
    return spins

random.seed(42)
N = 100
J = 1.0
steps = 50000

print("=== 1D Ising 模型 (Metropolis) ===")
print(f"N={N}, J={J}, MC steps={steps}")
print(f"\n{'kT':>6} {'|M|':>8} {'<E>/N':>8} {'相':>6}")
print("-" * 32)
for kT in [0.1, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0]:
    spins = [random.choice([-1, 1]) for _ in range(N)]
    spins = metropolis_1d(spins, N, J, kT, steps)
    M = abs(magnetization(spins))
    E = ising_energy(spins, J) / N
    phase = "有序" if M > 0.5 else ("部分" if M > 0.1 else "无序")
    print(f"{kT:6.2f} {M:8.3f} {E:8.3f} {phase:>6}")

print("\n注：1D Ising 无有限温度相变（kT_c=0）。")
print("2D Ising 才有 kT_c ≈ 2.269J 的相变 (Onsager 1944)。")
print("高温热涨落破坏任意长程序。")

# 解析验证：1D 关联长度 xi = -1/ln(tanh(J/kT))
print("\n=== 1D Ising 关联长度 ===")
print(f"{'kT':>6} {'xi (格点)':>12}")
for kT in [0.5, 1.0, 1.5, 2.0, 3.0]:
    xi = -1.0 / math.log(math.tanh(J/kT)) if math.tanh(J/kT) < 1 else float('inf')
    print(f"{kT:6.2f} {xi:12.3f}")
print("=> 高温关联短，低温关联长，但无发散 => 无相变。")
```

---

## 9. 局限与延伸

### 9.1 平衡统计力学的局限

| 局限 | 何时失效 | 替代理论 |
|------|----------|----------|
| 非平衡过程 | 系统远离平衡 | 非平衡统计（Prigogine） |
| 强关联系统 | 电子-电子关联强 | 多体物理（PHYS 261） |
| 涨落显著 | 小系统/临界点 | 涨落定理、随机过程 |
| 时间相关 | 动力学过程 | 线性响应、Kubo 公式 |
| 量子相变 | $T=0$ 量子涨落驱动 | 量子相变理论 |

### 9.2 从 PHYS 45 到 PHYS 220 的认知跃迁

1. **PHYS 45/107 (Schroeder)**：热的世界——熵、温度、热机、基本统计
2. **PHYS 170 (Kittel/Kroemer → Pathria)**：系综的世界——配分函数、量子统计
3. **PHYS 220 (Pathria/Huang)**：相变的世界——临界现象、RG、涨落
4. **PHYS 261 (Mahan)**：多体世界——格林函数、元激发

### 9.3 延伸阅读

- **Schroeder**：直觉最好的入门，Stanford 风格的「先物理后数学」
- **Kittel & Kroemer**：简洁的统计物理视角
- **Pathria & Beale**：研究生标准教材
- **Huang《Statistical Mechanics》2ed**：相变与临界现象深入
- **Landau & Lifshitz Vol 5《Statistical Physics》**：俄系经典
- **Goldenfeld《Lectures on Phase Transitions and the Renormalization Group》**：相变与 RG 最佳入门

---

## 参考文献

1. Schroeder, D. V. *An Introduction to Thermal Physics* Addison-Wesley, 2000.
2. Kittel, C. & Kroemer, H. *Thermal Physics* 2nd ed. W. H. Freeman, 1980.
3. Pathria, R. K. & Beale, P. D. *Statistical Mechanics* 4th ed. Elsevier, 2021.
4. Huang, K. *Statistical Mechanics* 2nd ed. Wiley, 1987.
5. Landau, L. D. & Lifshitz, E. M. *Statistical Physics* (Vol 5) 3rd ed. Butterworth-Heinemann, 1980.
6. Goldenfeld, N. *Lectures on Phase Transitions and the Renormalization Group* Westview, 1992.

---

> **本主题对应讲透X 宪法**：直觉（§1-2）→ 公式（§3-5）→ 代码（§8 bash 跑通）→ 不足（§9）→ 应用（§6 SLAC/Stanford）。
>
> **文件信息**：stanford-physics/topic04-statistical/statistical.md · Phase 1 主题 4 · 2026-08-12

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：你不需要知道 $10^{23}$ 个分子每个在哪——它们集体行为只服从一个简单规则：**总是往「最混乱」的方向走**。这个「混乱程度」就是熵，它只会增加，永不减少。

热力学第二定律是宇宙最铁的定律——比能量守恒还无情。打碎的杯子不会自己复原，泼出去的水不会自动收回杯子。为什么？因为「碎杯」的微观状态数远多于「整杯」，系统总是涌向状态数最多的地方。Boltzmann 用 $S = k_B\ln\Omega$ 一行公式揭示了时间箭头的本质。

> **生活类比**：扑克牌洗牌——一副按顺序排好的牌（低熵）洗几次后必然变乱（高熵）。反过来，乱牌洗成有序的概率小到宇宙寿命等不起。熵增不是「必然」，是「概率上几乎确定」。

> **反直觉发现（啊哈时刻）**：
> 1. **绝对零度时仍有运动**：费米气体在 $T=0$ 时仍有巨大动能和压强（费米能 $E_F$）！这就是中子星抵抗引力坍缩的简并压来源。
> 2. **卡诺效率永远 < 100%**：即使没有摩擦、没有损耗，热机效率也有上限 $\eta = 1 - T_C/T_H$——除非冷端是绝对零度（不可达）。
> 3. **黑体辐射峰值决定一切**：太阳 5778 K 峰值在 500 nm（可见光，所以眼睛长这样）；CMB 2.725 K 峰值在微波——我们「看见」了宇宙大爆炸的余温。

---

## 🔗 衔接：从哪来，到哪去

| 维度 | 内容 |
|------|------|
| **前置知识** | 主题 1（力学）的能量概念；主题 3（量子）的全同粒子/自旋；概率论 |
| **本主题解决的危机** | 如何从 $10^{23}$ 个粒子的微观行为推导宏观热力学规律？温度到底是什么？ |
| **核心跃迁** | 从「热机/熵」（PHYS 45）→「配分函数/系综」（PHYS 170）→「相变/RG」（PHYS 220） |
| **留下新危机** | ①远离平衡的系统（生命、湍流）②强关联系统（高温超导）③量子相变（$T=0$） |
| **后续主题** | **主题 6（固体）**：声子/电子气/超导；**主题 7（粒子）**：早期宇宙热历史；**主题 8（GR）**：BBN/CMB |

---

## 🏭 理论联系实际：5 个现代应用

1. **热电材料与废热回收**：利用 Seebeck 效应将工业废热转为电能，效率受 Boltzmann 输运统计限制。2024 年新型拓扑热电材料 ZT 值突破 2.0。

2. **超冷原子量子模拟器**：用激光冷却将原子降到 nK 温度（BEC），模拟 Hubbard 模型等强关联系统——Stanford/麻省团队直接「看到」了量子相变。

3. **Ising 模型与机器学习**：Boltzmann 机（深度学习的前身）直接借鉴统计力学的配分函数思想；2024 年扩散模型（DALL-E/Stable Diffusion）的理论基础正是非平衡统计物理。

4. **蛋白质折叠与熵**：蛋白质自发折叠成 3D 结构是熵焓竞争的结果——疏水效应本质是水分子构型熵最大化。AlphaFold 的物理基础就在这里。

5. **卡诺极限与热机优化**：从汽车发动机到核电站，所有热机效率都受 $\eta_{\max} = 1 - T_C/T_H$ 约束。先进联合循环电厂效率 ~62%（接近卡诺极限的 75%）。

---

## 🔬 最新研究前沿（2024-2026）

1. **时间晶体的实验证实（2023-2024）**：Google 量子处理器和 Stanford/NIST 团队实现了稳定的「离散时间晶体」——一种在时间维度上自发破缺平移对称性的非平衡相，颠覆了传统平衡热力学的相变概念。

2. **非平衡统计力学的精确解（2024-2025）**：涨落定理和 Jarzynski 等式的实验验证进入单分子水平——纳米尺度下「熵减」事件被直接观测到（小系统短暂违反第二定律）。

3. **张量网络与多体物理（2024）**：DMRG/MPS 等张量网络方法求解一维强关联系统精度达 $10^{-8}$，Stanford/谷歌团队用张量网络模拟 2D Hubbard 模型，逼近高温超导机制。

4. **扩散模型 = 非平衡统计物理（2023-2025）**：AI 生成模型（Stable Diffusion/DALL-E）的数学核心是随机过程的反向扩散——2024 年多篇论文将此联系精确化，统计力学「反向指导」AI 理论。

5. **主动物质与非平衡相变（2024-2025）**：细菌群体、细胞微管的集体运动呈现新型非平衡相，Toner-Tu 理论的实验验证推动「活性物质」成为统计物理新分支。

---

## 🗺️ 学习 Roadmap（Stanford 路径）

```
入门 → PHYS 45/107 (Schroeder)
  │   温度、熵、热机、卡诺循环、基础统计（配分函数）
  │   ✅ 检查点：能解释为什么熵增是概率规律而非绝对律
  ▼
进阶 → PHYS 170 (Kittel & Kroemer → Pathria)
  │   正则/巨正则系综、量子统计（FD/BE）、BEC、简并费米气体
  │   ✅ 检查点：能推导费米-狄拉克分布并解释费米温度
  ▼
深造 → PHYS 220 (Pathria/Huang/Goldenfeld)
  │   相变、临界指数、重整化群、普适性、涨落定理
  │   ✅ 检查点：理解为什么 2D Ising 临界指数与平均场不同
  ▼
前沿 → PHYS 261 (多体物理)
      格林函数、元激发、量子相变、张量网络
```

> **费曼的建议**：统计物理的核心就一句话——「最概然宏观态 = 微观态数最多的态」。先真正理解 Sackur-Tetrode 公式，整个学科就通了。
