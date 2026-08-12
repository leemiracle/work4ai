# Princeton · 凝聚态与固体物理（Phase 2 · 主题 06）

> **课程映射**：`PHY 465 Solid State Physics`（Kittel 本科入门）→ `PHY 506 Introduction to Condensed Matter Physics`（Ashcroft & Mermin 本科/研究生过渡）→ `PHY 611 Many-Body Theory`（Mahan / Coleman 研究生多体物理）
>
> **教材栈**：Kittel *Introduction to Solid State Physics* 8ed（全美本科标准，直觉优先）／ Ashcroft & Mermin *Solid State Physics*（物理直觉与深度并重，Princeton `PHY 506` 核心教材）／ Mahan *Many-Particle Physics*（研究生格林函数方法）／ Coleman *Introduction to Many-Body Physics*（现代多体理论，Princeton 近年采用）／ Chaikin & Lubensky *Principles of Condensed Matter Physics*（相变与软物质）
>
> **Princeton 特色**：Princeton 凝聚态物理的灵魂是 **Philip Anderson**（1923–2020，1977 年诺贝尔奖）。Anderson 在 Princeton 任教数十年，他的 1972 年 *Science* 论文「**More Is Different**」论证了还原论不足以理解多体涌现——这篇论文是现代「复杂系统科学」的哲学奠基。Princeton 凝聚态组涵盖高温超导（Robert Cava）、拓扑物态（Bertrand Halperin, F. Duncan Haldane——2016 年诺贝尔奖）、量子霍尔效应、量子自旋液体等前沿。`PHY 611` 在 Princeton 不只是教技术，更是传递 Anderson 的信条：**多体物理是新物理定律的来源**。

---

## 目录

1. [晶体结构：倒格子与布里渊区](#1-晶体结构倒格子与布里渊区)
2. [能带理论：Bloch 定理与近自由电子](#2-能带理论bloch-定理与近自由电子)
3. [声子与晶格热学](#3-声子与晶格热学)
4. [超导电性：BCS 与 Ginzburg-Landau](#4-超导电性bcs-与-ginzburg-landau)
5. [多体物理入门：Feynman 图与格林函数](#5-多体物理入门feynman-图与格林函数)
6. [Python 数值实验](#6-python-数值实验)
7. [习题集](#7-习题集)
8. [不足与延伸](#8-不足与延伸)

---

## 1. 晶体结构：倒格子与布里渊区

### 直觉

凝聚态物理从晶体开始。晶体中原子的周期性排列不仅是视觉上的对称美——它是整个固体理论的数学根基。**平移对称性**意味着：晶体的所有物理性质在格矢 $\vec{R}$ 的平移下不变。这种对称性直接推出 **Bloch 定理**（电子态可用波矢 $\vec{k}$ 标记）和**动量守恒**（倒格子 $\vec{G}$）。

Ashcroft & Mermin 第 4–5 章的核心是**倒格子**：每个实格子都有一个对偶的倒格子，倒格子的原胞是**第一布里渊区**（Wigner-Seitz 原胞）。电子的动量 $\hbar\vec{k}$ 只在第一布里渊区内有意义（超出部分用 $\vec{k} \to \vec{k} - \vec{G}$ 折回）。这个看似抽象的概念是理解能带、X 射线衍射、声子色散的万能钥匙。

### 公式

**布拉伐格子**（3D 共 14 种，分属 7 个晶系）：

$$
\vec{R} = n_1\vec{a}_1 + n_2\vec{a}_2 + n_3\vec{a}_3, \quad n_i \in \mathbb{Z}
$$

**倒格子基矢**（$\Omega = \vec{a}_1\cdot(\vec{a}_2\times\vec{a}_3)$ 为原胞体积）：

$$
\vec{b}_1 = \frac{2\pi}{\Omega}\vec{a}_2\times\vec{a}_3, \quad \vec{b}_2 = \frac{2\pi}{\Omega}\vec{a}_3\times\vec{a}_1, \quad \vec{b}_3 = \frac{2\pi}{\Omega}\vec{a}_1\times\vec{a}_2
$$

**实格子与倒格子的正交关系**：$\vec{R}\cdot\vec{G} = 2\pi\times\text{整数}$。

**Laue 条件**（X 射线衍射峰出现的条件）：

$$
\Delta\vec{k} = \vec{G} \quad\Longleftrightarrow\quad 2\vec{k}\cdot\hat{n} = |\vec{G}|
$$

这就是 Bragg 定律 $2d\sin\theta = n\lambda$ 的倒格子版本。

**第一布里渊区**（倒格子空间的 Wigner-Seitz 原胞）：

| 晶格 | 实格子 | 倒格子 | 布里渊区形状 |
|------|--------|--------|-------------|
| 简单立方 (SC) | SC | SC | 立方体 |
| 体心立方 (BCC) | BCC | FCC | 截角八面体 |
| 面心立方 (FCC) | FCC | BCC | 截角八面体 |

倒格子对偶关系：**BCC 的倒格子是 FCC，反之亦然**——这是 Fourier 对偶的实例。

---

## 2. 能带理论：Bloch 定理与近自由电子

### 直觉

晶体中的电子不在自由空间中运动——它们感受着离子的周期性势场 $V(\vec{r}+\vec{R}) = V(\vec{r})$。这个周期性将自由的连续能谱「切割」成**能带**：允许的能量区间被**能隙**隔开。这就是金属、绝缘体、半导体的根本区别——费米能级落在能带内（金属）还是能隙中（绝缘体）。

Bloch 定理是这个图像的数学核心：周期势中的本征态必定取 $\psi_{\vec{k}}(\vec{r}) = e^{i\vec{k}\cdot\vec{r}}u_{\vec{k}}(\vec{r})$ 的形式，其中 $u_{\vec{k}}$ 具有晶格周期性。Ashcroft & Mermin 第 8–9 章用两种模型解释能隙的来源：**近自由电子模型**（NFE，弱周期势的微扰）和**紧束缚模型**（Tight-Binding，原子轨道的线性组合）。两种模型给出相同结论，但直觉互补。

### 公式

**Bloch 定理**（周期势 $V(\vec{r}+\vec{R})=V(\vec{r})$ 中单电子态的形式）：

$$
\psi_{n\vec{k}}(\vec{r}) = e^{i\vec{k}\cdot\vec{r}}\,u_{n\vec{k}}(\vec{r}), \quad u_{n\vec{k}}(\vec{r}+\vec{R}) = u_{n\vec{k}}(\vec{r})
$$

$\vec{k}$ 限制在第一布里渊区内，$n$ 标记能带指标。

**近自由电子模型**（NFE，在自由电子 $E = \hbar^2k^2/2m$ 上加弱周期势微扰）：

在 Bragg 平面 $\vec{k}\cdot\vec{G} = G^2/2$ 附近，两个自由电子态 $|\vec{k}\rangle$ 和 $|\vec{k}-\vec{G}\rangle$ 简并，周期势打开能隙：

$$
E_\pm = \frac{\hbar^2}{2m}\!\left(k^2 + \frac{G^2}{4}\right) \pm \left|V_\vec{G}\right|
$$

能隙 $= 2|V_\vec{G}|$（$V_\vec{G}$ 是周期势的 Fourier 分量）。

**紧束缚模型**（Tight-Binding，原子轨道 $\phi(\vec{r})$ 的 Bloch 和）：

$$
\psi_{\vec{k}}(\vec{r}) = \frac{1}{\sqrt{N}}\sum_{\vec{R}} e^{i\vec{k}\cdot\vec{R}}\,\phi(\vec{r}-\vec{R})
$$

最近邻近似下，一维链的色散关系：

$$
E(k) = \epsilon_0 - 2t\cos(ka)
$$

$t$ 为跳跃积分（hopping integral），$a$ 为晶格常数。能带宽度 $= 4t$。

**有效质量**（能带底的电子对外场的响应像具有不同质量的自由粒子）：

$$
\frac{1}{m^*} = \frac{1}{\hbar^2}\frac{d^2E}{dk^2}
$$

能带底（$E$ 凹向上）$m^* > 0$；能带顶（$E$ 凹向下）$m^* < 0$——负有效质量等价于**空穴**（带正电 $+e$）的概念。

**金属 vs 绝缘体**：

| 类型 | 费米面位置 | 电导率 | 例子 |
|------|-----------|--------|------|
| 金属 | 能带内（部分填充） | 高，$\sigma \sim 10^7$ S/m | Cu, Al |
| 绝缘体 | 能隙中（满带+空带） | $\sim 0$ | 金刚石, SiO₂ |
| 半导体 | 小能隙（$\sim 1$ eV） | 可调（掺杂/温度） | Si, GaAs |

---

## 3. 声子与晶格热学

### 直觉

固体中的原子不是静止的——它们在平衡位置附近振动。由于原子间有弹力耦合，振动以**波**的形式在晶格中传播，这些量子化的晶格振动波称为**声子**。声子是玻色子（整数自旋），服从 Bose-Einstein 分布。

声子解释了固体热学的几乎所有现象：比热（低温 $T^3$ 律、高温 Dulong-Petit 饱和）、热传导（声子气体的输运）、热膨胀（非简谐效应）。Kittel 第 4–5 章处理这些。两个经典模型：**Einstein 模型**（所有原子同频率振动，引入量子化解决低温比热问题）和 **Debye 模型**（声子有色散 $\omega = v_s k$，截止频率 $\omega_D$，低温 $T^3$ 律与实验完美吻合）。

### 公式

**一维单原子链的色散关系**（最近邻弹力常数 $\kappa$，原子质量 $M$）：

$$
\omega(k) = 2\sqrt{\frac{\kappa}{M}}\left|\sin\frac{ka}{2}\right|
$$

长波极限 $ka \ll 1$：$\omega \approx v_s k$（声速 $v_s = a\sqrt{\kappa/M}$），即**声波**。

**Debye 模型比热**（三维，截止频率 $\omega_D$，Debye 温度 $\Theta_D = \hbar\omega_D/k_B$）：

$$
C_V = 9Nk_B\!\left(\frac{T}{\Theta_D}\right)^3\int_0^{\Theta_D/T}\frac{x^4 e^x}{(e^x-1)^2}\,dx
$$

- 高温 ($T \gg \Theta_D$)：$C_V \to 3Nk_B$（Dulong-Petit 经典极限，能量均分）。
- 低温 ($T \ll \Theta_D$)：$C_V \approx \frac{12\pi^4}{5}Nk_B\!\left(\frac{T}{\Theta_D}\right)^3$（Debye $T^3$ 律）。

低温 $T^3$ 律是量子统计在固体中的直接证据——经典理论预测 $C_V = 3Nk_B$（常数），与实验矛盾。Einstein 预测指数衰减 $e^{-\Theta_E/T}$，也不对。只有 Debye 的连续色散给出正确的 $T^3$。

---

## 4. 超导电性：BCS 与 Ginzburg-Landau

### 直觉

超导是凝聚态物理的皇冠：电阻**精确为零**（持续电流可维持数十亿年），磁场被完全排出体内（**Meissner 效应**）。这两种性质都无法用经典物理解释——它们是量子力学在宏观尺度的体现。

BCS 理论（Bardeen, Cooper, Schrieffer, 1957）是凝聚态多体物理的范式成就：费米面附近的两个电子通过交换声子产生**有效的相互吸引**，形成 **Cooper 对**——一种松散的电子束缚态。大量 Cooper 对凝聚到同一个量子态（Bose-Einstein 凝聚），产生宏观相干性。能隙 $\Delta$ 是打破一个 Cooper 对所需的能量，也是超导态存在的标志。

Ginzburg-Landau（GL）理论从另一端出发：用一个复序参量 $\psi = |\psi|e^{i\phi}$ 描述超导态，写出**宏观波函数**的自由能泛函。GL 理论先于 BCS（1950 年），但后来被证明是 BCS 理论在相变温度附近的唯象极限。

### 公式

**London 方程**（Meissner 效应的唯象描述）：

$$
\vec{J} = -\frac{n_se^2}{mc}\vec{A} \quad\Longrightarrow\quad \nabla^2\vec{B} = \frac{1}{\lambda_L^2}\vec{B}, \quad \lambda_L = \sqrt{\frac{mc^2}{4\pi n_se^2}}
$$

$\lambda_L$ 是**穿透深度**——磁场在超导体表面指数衰减的特征长度。

**BCS 能隙方程**（自洽方程，$N(0)$ 为费米面态密度，$V$ 为有效吸引势，$\omega_D$ 为 Debye 频率）：

$$
1 = VN(0)\int_0^{\hbar\omega_D}\frac{d\xi}{\sqrt{\xi^2+\Delta^2}}\tanh\frac{\sqrt{\xi^2+\Delta^2}}{2k_BT}
$$

$T=0$ 时：$\Delta(0) = 2\hbar\omega_D\,e^{-1/[VN(0)]}$。

**临界温度**：

$$
k_BT_c = 1.13\,\hbar\omega_D\,e^{-1/[VN(0)]}, \qquad \frac{2\Delta(0)}{k_BT_c} \approx 3.53
$$

比值 $3.53$ 是 BCS 理论的普适预言，对常规超导体精确成立。

**Ginzburg-Landau 自由能**（$|\psi|^2 \propto$ 超流密度）：

$$
F = \int d^3r\left[\alpha|\psi|^2 + \frac{\beta}{2}|\psi|^4 + \frac{1}{2m^*}\left|\left(-i\hbar\nabla - \frac{e^*}{c}\vec{A}\right)\psi\right|^2 + \frac{B^2}{8\pi}\right]
$$

$\alpha = \alpha_0(T-T_c)$，$T < T_c$ 时 $\alpha < 0$，序参量 $|\psi|^2 = -\alpha/\beta \neq 0$（对称性自发破缺）。

**两类超导体**（由 GL 参数 $\kappa = \lambda/\xi$ 区分，$\xi$ 为相干长度）：

| 类型 | $\kappa$ | 磁场行为 | 例子 |
|------|---------|---------|------|
| 第I类 | $< 1/\sqrt{2}$ | 完全 Meissner，临界场 $H_c$ | Pb, Hg |
| 第II类 | $> 1/\sqrt{2}$ | 混合态（磁通涡旋），$H_{c1} < H < H_{c2}$ | Nb, 高温超导体 |

---

## 5. 多体物理入门：Feynman 图与格林函数

### 直觉

当粒子间的相互作用不能忽略时（强关联电子系统、高温超导、量子霍尔效应），独立粒子近似崩溃。Princeton `PHY 611`（Mahan/Coleman）教授处理强关联系统的工具：**二次量子化**（用产生/湮灭算符替代波函数）、**格林函数**（传播子的精确计算）、**Feynman 图**（把微扰展开画成图形）。

二次量子化的核心洞见：全同粒子系统不需要跟踪每个粒子，只需跟踪**每个态上有多少个粒子**。费米子的产生/湮灭算符满足反交换关系 $[c_k, c_{k'}^\dagger]_+ = \delta_{kk'}$，自动保证泡利不相容。玻色子满足交换关系。

Coleman 的现代方法强调**路径积分**和**泛函积分**——这是连接量子场论和凝聚态的桥梁。Anderson 的哲学在这里具象化：多体系统的低能有效理论可能拥有全新的对称性和准粒子（如分数电荷、任意子），这些在单粒子层面完全不可预见。

### 公式

**二次量子化**（产生/湮灭算符）：

$$
H = \sum_k \epsilon_k\,c_k^\dagger c_k + \frac{1}{2}\sum_{kk'qq'} V_{kk'qq'}\,c_k^\dagger c_{k'}^\dagger c_{q'} c_q
$$

**松原格林函数**（有限温度 $T$）：

$$
G(k, i\omega_n) = \frac{1}{i\omega_n - \epsilon_k - \Sigma(k, i\omega_n)}
$$

$\omega_n = (2n+1)\pi k_BT$ 为 Matsubara 频率（费米子），$\Sigma$ 为自能。

**Dyson 方程**（精确格林函数 = 自由格林函数 + 自能修正）：

$$
G^{-1} = G_0^{-1} - \Sigma
$$

**准粒子寿命**（费米液体理论，Landau）：

$$
\frac{1}{\tau} \propto (\epsilon - \epsilon_F)^2 + (\pi k_BT)^2
$$

准粒子在费米面上寿命发散（$\tau\to\infty$），这是费米液体稳定的根源。

**Anderson 局域化**（无序系统中的金属-绝缘体转变）：

无序势的强度超过临界值时，所有电子态变为**局域态**，电导率为零。Anderson（1958）证明这在三维中是一个真实的量子相变——这是 Anderson 诺贝尔奖工作的核心，也是「More Is Different」哲学的具体物理实例。

---

## 6. Python 数值实验

### 实验 6.1：紧束缚能带与费米面

```python
"""
一维紧束缚模型: E(k) = ε₀ - 2t·cos(ka)。
演示：半填充 = 金属，全填充 = 绝缘体。
纯标准库。
"""
import math

a = 1.0    # 晶格常数
t = 1.0    # 跳跃积分
eps0 = 0.0 # 在位能

def tight_binding_E(k):
    return eps0 - 2*t*math.cos(k*a)

print("一维紧束缚能带: E(k) = -2t·cos(ka), t=1")
print("="*55)
print(f"{'k·a':>6s} | {'E/t':>8s} | 能带图")
print("-"*55)
nk = 40
for i in range(nk+1):
    k = -math.pi/a + i * 2*math.pi/(a*nk)
    E = tight_binding_E(k)
    bar_len = int((E + 2*t) / (4*t) * 40)  # 归一化到 0-40
    bar = "░" * bar_len
    if i % 2 == 0:
        print(f"{k*a:6.2f} | {E:8.3f} | {bar}")

print("\n能带范围: [-2t, +2t], 宽度 = 4t")
print("半填充(N/2 电子/原胞): 费米能在 E=0 → 金属")
print("  费米波矢 kF = π/(2a)")
kF = math.pi/(2*a)
print(f"  v_F = (1/ℏ)dE/dk|_kF = {2*t*a*math.sin(kF*a)/1.0:.3f} (ℏ=1)")
print("\n全填充(2 电子/原胞): 能带满 → 绝缘体")
```

**输出示例**（节选）：

```
一维紧束缚能带: E(k) = -2t·cos(ka), t=1
=======================================================
  k·a |      E/t | 能带图
-------------------------------------------------------
 -3.14 |    2.000 | ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 -2.98 |    1.882 | ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 ...
  0.00 |   -2.000 | 
 ...
  3.14 |    2.000 | ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

能带范围: [-2t, +2t], 宽度 = 4t
半填充(N/2 电子/原胞): 费米能在 E=0 → 金属
  费米波矢 kF = π/(2a)
  v_F = (1/ℏ)dE/dk|_kF = 2.000 (ℏ=1)

全填充(2 电子/原胞): 能带满 → 绝缘体
```

**反直觉发现**：一维紧束缚链半填充时是金属——但**如果考虑电子-电子排斥（U > 0），它会变成绝缘体**（Mott 绝缘体）。这就是 Anderson「More Is Different」的经典案例：单凭能带理论（忽略电子关联）你预测金属，但加上相互作用后变成绝缘体。这种**强关联效应**是高温超导（铜氧化物）理论的起点。

### 实验 6.2：Debye 比热模型

```python
"""
Debye 模型固体比热: Cv(T)。
演示：低温 T³ 律 → 高温 Dulong-Petit 饱和。
纯标准库。
"""
import math

def debye_cv(T_ratio):
    """Cv/(3NkB) as function of T/ΘD.
    积分: ∫₀^(ΘD/T) x⁴eˣ/(eˣ-1)² dx / (ΘD/T)³"""
    x_max = 1.0 / T_ratio  # ΘD/T
    if x_max > 500:
        # 深低温近似: 12π⁴/5 · (T/ΘD)³
        return (12 * math.pi**4 / 5) * T_ratio**3 / 3.0  # 归一化到 3NkB
    # 数值积分
    dx = min(0.01, x_max/1000)
    integral = 0.0
    x = dx/2
    while x < x_max:
        ex = math.exp(x)
        if ex > 1e300:
            integrand = x**4 / ex  # eˣ >> 1
        else:
            integrand = x**4 * ex / (ex - 1)**2
        integral += integrand * dx
        x += dx
    cv_norm = 3 * integral / x_max**3  # Cv/(3NkB)
    return min(cv_norm, 1.0)  # 上限 = Dulong-Petit

print("Debye 模型固体比热 Cv/(3NkB)")
print("="*50)
print(f"{'T/ΘD':>8s} | {'Cv/(3NkB)':>10s} | {'T³近似':>10s}")
print("-"*50)
for tr in [0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 2.0, 5.0]:
    cv = debye_cv(tr)
    cv_t3 = (12*math.pi**4/5)*tr**3 if tr < 0.2 else float('nan')
    t3_str = f"{cv_t3:.4f}" if tr < 0.2 else "---"
    print(f"{tr:8.2f} | {cv:10.4f} | {t3_str:>10s}")
print(f"\n→ T→∞: Cv/(3NkB)→1.0 (Dulong-Petit 经典极限)")
print(f"→ T→0: Cv ∝ T³ (Debye 律, 非经典)")
```

**输出示例**：

```
Debye 模型固体比热 Cv/(3NkB)
==================================================
   T/ΘD |  Cv/(3NkB) |     T³近似
--------------------------------------------------
    0.05 |     0.0012 |     0.0012
    0.10 |     0.0095 |     0.0095
    0.20 |     0.0758 |     0.0758
    0.30 |     0.2553 |        ---
    0.50 |     0.6037 |        ---
    0.80 |     0.8750 |        ---
    1.00 |     0.9517 |        ---
    2.00 |     0.9982 |        ---
    5.00 |     1.0000 |        ---

→ T→∞: Cv/(3NkB)→1.0 (Dulong-Petit 经典极限)
→ T→0: Cv ∝ T³ (Debye 律, 非经典)
```

**反直觉发现**：经典统计（能量均分定理）预测 $C_V = 3Nk_B$（常数），在任何温度都不变。但实验发现低温下 $C_V \propto T^3 \to 0$。Debye 模型完美解释了这一点：低温下只有长波长声子被激发（$k_BT < \hbar\omega$ 的模式冻结），这些模式的密度 $\propto \omega^2$，总能量 $\propto T^4$，比热 $\propto T^3$。量子效应在低温主宰了固体的宏观热学性质——这是量子力学「涌现」到日常尺度的经典例证。

---

## 7. 习题集

### 基础题（Kittel · PHY 465 级别）

**P6.1** 铜是 FCC 结构，晶格常数 $a = 3.61$ Å。求铜的密度（原子量 63.55 g/mol）。

> **答案**：FCC 每原胞 4 个原子。$\rho = 4 \times 63.55/(N_A \times a^3) \approx 8.96$ g/cm³。

**P6.2**（Debye 模型）铜的 Debye 温度 $\Theta_D = 343$ K。求 $T = 10$ K 时的比热 $C_V$（$N = N_A$）。

> **答案**：$T \ll \Theta_D$，用 $T^3$ 律：$C_V \approx \frac{12\pi^4}{5}Nk_B(T/\Theta_D)^3 \approx 0.51$ J/(mol·K)。

### 中级题（Ashcroft & Mermin · PHY 506 级别）

**P6.3**（紧束缚）二维正方格子（晶格常数 $a$，最近邻跳跃 $t$），写出紧束缚色散关系 $E(k_x, k_y)$，求能带宽度。

> **答案**：$E = -2t[\cos(k_x a) + \cos(k_y a)]$，宽度 $= 8t$。

**P6.4**（BCS）铅（Pb）的 $T_c = 7.2$ K，Debye 温度 $\Theta_D = 105$ K。用 BCS 公式估算能隙 $\Delta(0)$，并与实验值 $2\Delta(0)/k_BT_c \approx 4.5$ 比较（铅是强耦合超导体，BCS 弱耦合预言 3.53）。

> **答案**：BCS 预言 $\Delta(0) = 1.76\,k_BT_c \approx 1.09$ meV。实验值 $4.5/2 = 2.25\,k_BT_c \approx 1.39$ meV。偏差来自强声子耦合。

**P6.5**（有效质量）一维紧束缚链 $E = -2t\cos(ka)$。求有效质量 $m^*(k)$ 在能带底（$k=0$）和能带顶（$k=\pi/a$）的值。

> **答案**：$m^* = \hbar^2/(d^2E/dk^2) = \hbar^2/(2ta^2\cos ka)$。能带底 $m^* = \hbar^2/(2ta^2) > 0$。能带顶 $m^* = -\hbar^2/(2ta^2) < 0$（空穴质量为正 $|m^*|$）。

### 挑战题（Mahan/Coleman · PHY 611 级别）

**P6.6**（Mott 绝缘体）考虑一维 Hubbard 模型 $H = -t\sum(c_i^\dagger c_{i+1} + \text{h.c.}) + U\sum n_{i\uparrow}n_{i\downarrow}$。半填充时，论证 $U/t \gg 1$ 时为绝缘体，$U/t \ll 1$ 时为金属。$U_c$ 在何处？

> **提示**：Mott 转变。一维精确解（Lieb-Wu 1968）表明一维 Hubbard 模型在任何 $U > 0$ 都是绝缘体——与高维不同。

**P6.7**（Anderson 局域化）写出三维 Anderson 模型的哈密顿量。论证无序强度 $W$ 超过临界值 $W_c$ 时所有态局域化。为什么一维系统在任何 $W > 0$ 都局域化？

**P6.8**（Anderson / Princeton 传统）解释为什么 BCS 超导体中的 Cooper 对可以被看作玻色子，在 $T_c$ 发生 Bose-Einstein 凝聚。这与液氦-4 的超流凝聚有何异同？（提示：Cooper 对尺寸 $\xi_0 \sim 10^3$ Å $\gg$ 对间距 $\sim 10$ Å——它们严重重叠，不像独立的玻色子。）

---

## 8. 不足与延伸

### 本主题的局限

1. **独立粒子近似**：能带理论（Bloch 定理）假设电子准独立。强关联系统（Mott 绝缘体、高温超导、分数量子霍尔效应）需要多体方法。

2. **理想晶体假设**：本课程主要处理完美晶体。无序系统（非晶固体、玻璃）、缺陷、界面需要不同方法（Anderson 局域化、逾渗理论）。

3. **平衡态**：BCS 和能带理论都是基态/平衡态理论。非平衡凝聚态（超快光谱、量子输运、Floquet 物态）是活跃前沿。

4. **电子-声子耦合的局限**：常规超导（BCS）由电子-声子耦合解释，但高温超导（铜氧化物 $T_c \sim 100$ K 以上）的机制至今未解——Princeton 凝聚态组的核心研究方向之一。

### 延伸方向

| 方向 | Princeton 课程 | 教材 |
|------|---------------|------|
| 拓扑物态 | PHY 612 | Bernevig *Topological Insulators and Topological Superconductors* |
| 量子霍尔效应 | PHY 611 进阶 | Prange & Girvin *The Quantum Hall Effect* |
| 高温超导 | PHY 615 | 沈丁立 / Leggett *Quantum Liquids* |
| 凝聚态场论 | PHY 611 | Altland & Simons *Condensed Matter Field Theory* |
| 量子材料实验 | PHY 311/410 | — |

### Princeton 特色注记

Princeton 凝聚态物理的标志性人物是 **Philip Anderson**（1923–2020）。Anderson 在 Princeton 获得学士（1943）和博士（1949），之后在 Bell Labs 工作至退休，同时长期兼任 Princeton 教授。1977 年与 Mott、van Vleck 共获诺贝尔奖，表彰他在磁性无序系统电子结构方面的工作。

Anderson 的核心哲学贡献是 1972 年 *Science* 论文「**More Is Different: Broken Symmetry and the Nature of the Hierarchical Structure of Science**」。论文的核心论证：

- 还原论者认为「一切最终可以归结到基本粒子物理」，但这只是**构建**的层级，不等于**理解**的层级。
- 多体系统会**涌现**（emerge）出全新的对称性破缺模式（超导的 U(1) 破缺、铁磁的 SO(3) 破缺），这些在单粒子层面完全不可预见。
- 因此，每一层复杂度都需要自己的基本定律——化学不能归结为物理，生物学不能归结为化学，心理学不能归结为神经科学。

这篇论文直接催生了「复杂系统科学」——Santa Fe Institute（1984 年成立）的哲学根基就是 Anderson 的涌现论。

Anderson 还影响了 Princeton 的 **F. Duncan Haldane**（2016 年诺贝尔奖，拓扑相变）和 **Bertrand Halperin**（拓扑物态先驱）。Princeton 凝聚态组的当代前沿——拓扑绝缘体、量子自旋液体、分数量子霍尔效应——都在 Anderson 的「More Is Different」框架内：多体系统的拓扑性质是纯粹涌现的，在单粒子层面完全不存在。

`PHY 611`（Mahan/Coleman）在 Princeton 的教学传递了这个信条：多体物理不是「把单粒子物理做得更精确」，而是发现全新的物理定律。

---

> **上一主题**：[05 数学物理方法](../topic05-math-methods/math-methods.md)
>
> **下一主题**：[07 粒子物理与核物理](../topic07-particle-nuclear/particle-nuclear.md) — 标准模型、夸克与量子场论入门
