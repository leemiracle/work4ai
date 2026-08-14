# ETH Zürich · 固体物理（Phase 2 · 主题 06）

> **课程映射**：`402-2601-00L Solid State Physics`
>
> **教材栈**：Kittel *Introduction to Solid State Physics* 9ed（入门标配）→ Ashcroft & Mermin *Solid State Physics*（理论深度，凝聚态圣经）→ Simon *The Oxford Solid State Basics*（现代直觉补充）
>
> **ETH 特色**：ETH 的凝聚态物理是王牌方向之一，与 **PSI（Paul Scherrer Institute）** 的中子散射、同步辐射光源紧密对接。PSI 的 SwissFEL（自由电子激光）和 SLS（同步辐射光源）是研究凝聚态物质结构的国之重器。Karl Alexander Müller 和 J. Georg Bednorz 在 IBM Zürich 发现了铜氧化物高温超导（1986 年，1987 年诺奖），这一发现直接诞生在 ETH 的学术生态圈内。ETH 固体物理课不仅讲晶格和能带，更传承了**从实验发现理论**的 ETH 传统。

---

## 目录

1. [晶体结构与倒易晶格](#1-晶体结构与倒易晶格)
2. [晶格振动与声子](#2-晶格振动与声子)
3. [自由电子模型与能带论](#3-自由电子模型与能带论)
4. [半导体的电子结构](#4-半导体的电子结构)
5. [超导电性](#5-超导电性)
6. [Python 数值实验](#6-python-数值实验)
7. [习题集](#7-习题集)
8. [不足与延伸](#8-不足与延伸)

---

## 1. 晶体结构与倒易晶格

### 直觉

固体物理的出发点是一个惊人的事实：**晶体中原子的排列具有完美的平移对称性**。一块食盐（NaCl）中每对 Na-Cl 的距离精确到皮米级别相同，这种长程序延伸到 $10^{10}$ 个原子尺度。这种规则性不是巧合——它是能量最低化的自然结果，也是 X 射线衍射能产生尖锐斑点的原因。

**倒易晶格**（reciprocal lattice）是晶体物理最反直觉但最强大的概念。它是实空间晶格的 Fourier 变换：每个倒易格点对应实空间中的一组晶面。倒易空间中的矢量 $\vec{G}$ 满足 $e^{i\vec{G}\cdot\vec{R}} = 1$（对所有实格矢 $\vec{R}$）。

为什么需要倒易晶格？因为**波在晶体中的行为由波矢 $\vec{k}$ 描述，而 $\vec{k}$ 生活在倒易空间中**。X 射线衍射条件、电子能带结构、声子色散——全部用倒易空间中的量来表达。

### 公式

**Bravais 晶格**（实空间）：

$$
\vec{R} = n_1\vec{a}_1 + n_2\vec{a}_2 + n_3\vec{a}_3, \quad n_i \in \mathbb{Z}
$$

3D 共 14 种 Bravais 晶格（分属 7 大晶系）。

**倒易晶格**：

$$
\vec{b}_1 = 2\pi\frac{\vec{a}_2\times\vec{a}_3}{\vec{a}_1\cdot(\vec{a}_2\times\vec{a}_3)}, \quad \text{(循环置换)}
$$

$$
\vec{G} = h\vec{b}_1 + k\vec{b}_2 + l\vec{b}_3, \quad h,k,l\in\mathbb{Z}
$$

**Miller 指数** $(hkl)$：用倒易格矢标记晶面。截距倒数化整。

**Bragg 条件**（X 射线衍射）：

$$
2d\sin\theta = n\lambda
$$

等价的 Laue 条件（倒易空间形式）：

$$
\vec{k}' - \vec{k} = \vec{G}
$$

**Brillouin 区**：倒易空间中的 Wigner-Seitz 原胞。第一 Brillouin 区是倒易空间中「一个电子波矢」的全部独立取值范围。

**原胞体积**：$V_{\text{cell}} = |\vec{a}_1\cdot(\vec{a}_2\times\vec{a}_3)|$

### 代码演示：倒易晶格与 Bragg 衍射

```python
"""
简单立方(SC)晶格的倒易晶格计算 + Bragg 条件演示。
反直觉: 实空间简单立方 → 倒易空间也是简单立方（但尺度反转为 2π/a）。
体心立方(BCC) → 面心立方(FCC)（互为倒易!）。
"""
import math

# 简单立方晶格 (a = 5.43 Å, 硅的晶格常数)
a = 5.43  # Å

# 实空间基矢
a1 = (a, 0, 0)
a2 = (0, a, 0)
a3 = (0, 0, a)

# 倒易基矢（SC 的倒易也是 SC）
b1 = (2*math.pi/a, 0, 0)
b2 = (0, 2*math.pi/a, 0)
b3 = (0, 0, 2*math.pi/a)

print("=== 简单立方 (SC) 晶格 ===")
print(f"实空间基矢: a={a} Å")
print(f"原胞体积 V = a³ = {a**3:.2f} ų")
print(f"倒易基矢: b = 2π/a = {2*math.pi/a:.4f} Å⁻¹")
print(f"第一Brillouin区: 立方体 |k_i| < π/a = {math.pi/a:.4f} Å⁻¹")

# Bragg 衍射
print("\n=== Cu Kα X射线衍射 (λ=1.54 Å) ===")
wavelength = 1.54
print(f"{'晶面 (hkl)':>12} {'d (Å)':>8} {'2θ (°)':>8} {'sinθ':>8}")
for h, k, l in [(1,0,0), (1,1,0), (1,1,1), (2,0,0), (2,1,0), (2,2,0), (3,1,1)]:
    # 立方晶系面间距: d = a / √(h²+k²+l²)
    d = a / math.sqrt(h**2 + k**2 + l**2)
    sin_theta = wavelength / (2*d)
    if sin_theta <= 1.0:
        theta = math.degrees(math.asin(sin_theta))
        print(f"  ({h}{k}{l})     {d:>8.3f} {2*theta:>8.2f} {sin_theta:>8.4f}")
    else:
        print(f"  ({h}{k}{l})     {d:>8.3f}   不可达（λ太大）")

print("\n→ 不同晶面给出不同衍射角，XRD 图谱是晶体的'指纹'")

# BCC ↔ FCC 互为倒易的演示
print("\n=== BCC 与 FCC 互为倒易晶格 ===")
print("BCC 实空间基矢 → 倒易空间得到 FCC 结构")
print("FCC 实空间基矢 → 倒易空间得到 BCC 结构")
print("→ 这意味着 BCC 晶体的 XRD 消光规律 = FCC 格点的位置")
```

---

## 2. 晶格振动与声子

### 直觉

晶体中的原子并非静止不动——它们在平衡位置附近振动。但这种振动不是各自为政的随机抖动，而是**集体模式**：所有原子以同一个频率和波矢协同振动，形成一种「晶格波」。这些集体振动模式的量子化就是**声子**（phonon）。

声子是玻色子，服从 Bose-Einstein 分布。晶体的热容、热传导、超导（BCS 理论中的电子-声子耦合）全部由声子决定。

**声学声子**（acoustic）在 $k\to 0$ 时频率趋于零（$\omega \approx ck$），对应整体的刚性平移——这就是声波。
**光学声子**（optical）在 $k=0$ 时频率有限，对应原胞内不同原子反向运动——可被红外光激发（故称「光学」）。

### 公式

**一维单原子链色散关系**：

$$
\omega(k) = 2\sqrt{\frac{K}{M}}\left|\sin\frac{ka}{2}\right|
$$

其中 $K$ 为弹簧常数，$M$ 为原子质量，$a$ 为晶格常数。小 $k$ 时 $\omega \approx c_s |k|$（声速 $c_s = a\sqrt{K/M}$）。

**Debye 模型**（三维声子气）：

态密度 $D(\omega) \propto \omega^2$（截至 Debye 频率 $\omega_D$）。

热容：

$$
C_V = 9Nk_B\left(\frac{T}{\Theta_D}\right)^3\int_0^{\Theta_D/T}\frac{x^4 e^x}{(e^x-1)^2}\,dx
$$

低温极限 $T \ll \Theta_D$：$C_V \approx \frac{12\pi^4}{5}Nk_B\left(\frac{T}{\Theta_D}\right)^3 \propto T^3$（Debye $T^3$ 律）。

高温极限 $T \gg \Theta_D$：$C_V \to 3Nk_B$（Dulong-Petit 经典极限）。

**Einstein 模型**（所有原子以同一频率 $\omega_E$ 独立振动）：

$$
C_V = 3Nk_B\frac{(\Theta_E/T)^2 e^{\Theta_E/T}}{(e^{\Theta_E/T}-1)^2}
$$

低温时 $C_V \propto e^{-\Theta_E/T}$（指数衰减，比 $T^3$ 快——但不正确，因为忽略了声学声子的低频模式）。

### 代码演示：声子色散与热容的 Debye vs Einstein

```python
"""
一维单原子链色散关系 + Debye/Einstein 热容对比。
反直觉: Einstein 模型低温热容衰减太快（指数 vs T³）。
原因: Einstein 忽略了声学模式（ω→0），而正是这些低频模式主导低温热容。
"""
import math

# === 一维单原子链色散 ===
print("=== 一维单原子链声子色散 ω(k) ===")
print("ω(k) = 2√(K/M) |sin(ka/2)|")
omega_max = 2.0  # 归一化 √(K/M) = 1, a = 1
print(f"{'k*a/π':>8} {'ω/ω_max':>10} {'说明':>20}")
for ka_frac in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0]:
    ka = ka_frac * math.pi
    omega = abs(math.sin(ka/2))  # 归一化
    note = ""
    if ka_frac < 0.2: note = "声频区 ω∝k"
    elif ka_frac > 0.8: note = "Brillouin区边界"
    print(f"{ka_frac:>8.2f} {omega:>10.4f} {note:>20}")
print("→ k=0: ω=0（刚性平移，声波）")
print("→ k=π/a: ω=ω_max（相邻原子反相振动）")

# === Debye vs Einstein 热容 ===
def debye_CV(T_over_theta):
    """Debye 热容 C_V / 3NkB。"""
    if T_over_theta < 0.01:
        return 0.0
    xD = 1.0 / T_over_theta
    integral = 0.0
    n = 1000
    dx = xD / n
    for i in range(1, n+1):
        x = i * dx
        ex = math.exp(x)
        integral += x**4 * ex / (ex - 1)**2 * dx
    return 3 * integral / xD**3

def einstein_CV(T_over_theta):
    """Einstein 热容 C_V / 3NkB。"""
    if T_over_theta < 0.01:
        return 0.0
    x = 1.0 / T_over_theta
    ex = math.exp(x)
    return x**2 * ex / (ex - 1)**2

print(f"\n=== Debye vs Einstein 热容 ===")
print(f"{'T/Θ':>6} {'Debye':>8} {'Einstein':>10} {'差':>8}")
# Einstein Θ_E ≈ 0.72 Θ_D（等效拟合）
for T_ratio in [0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 5.0]:
    cv_D = debye_CV(T_ratio)
    cv_E = einstein_CV(T_ratio / 0.72)  # 调整 Einstein 特征温度
    diff = cv_D - cv_E
    print(f"{T_ratio:>6.2f} {cv_D:>8.4f} {cv_E:>10.4f} {diff:>+8.4f}")

print("\n→ 高温: 两者都 → 3NkB（Dulong-Petit）")
print("→ 低温: Debye ∝ T³ ✓（与实验吻合），Einstein ∝ e^{-Θ/T} ✗（衰减太快）")
print("→ 原因: 低频声学声子 ω→0 在低温仍可激发，Einstein 模型缺失了它们")
```

> **反直觉发现**：Einstein 模型看似合理（所有原子以同一频率振动），但在低温严重高估了热容的衰减速度。Debye 模型的关键洞察是：声学声子的频率可以任意低（$\omega \propto k$），正是这些低能激发在低温主导热容，给出 $T^3$ 律。**低频模式主导低温物理**——这是凝聚态物理的普适教训。

---

## 3. 自由电子模型与能带论

### 直觉

**Drude 自由电子模型**（1900 年）把金属中的电子当作经典理想气体——能解释 Wiedemann-Franz 定律（热导/电导比正比于温度），但电子比热预测大 100 倍。

**Sommerfeld 模型**（1928 年）用量子力学修复了 Drude：电子服从 Fermi-Dirac 统计，填满到费米能。这立刻解释了为什么电子比热只有经典值的 $T/T_F$ 倍——只有费米面附近 $k_BT$ 窗口内的电子能参与热激发。

**能带论**是固体物理的核心突破：周期势中的电子不再是自由粒子，其能级形成**允许带**和**禁带**（band gap）。这一简单结构解释了导体/绝缘体/半导体的区别：
- 导体：最高带部分填满（费米面在带内）
- 绝缘体：最高带全满，禁带很大（$E_g \gg k_BT$）
- 半导体：最高带全满，但禁带不大（$E_g \sim k_BT$，可热激发）

### 公式

**自由电子气态密度**（3D）：

$$
g(E) = \frac{V}{2\pi^2}\left(\frac{2m}{\hbar^2}\right)^{3/2}\sqrt{E}
$$

**费米能**（$T=0$）：

$$
E_F = \frac{\hbar^2}{2m}(3\pi^2 n)^{2/3}, \quad n = N/V
$$

**电子比热**（低温）：

$$
C_V^{\text{el}} = \frac{\pi^2}{2}Nk_B\frac{T}{T_F} = \gamma T
$$

**总比热**（金属低温）：$C_V = \gamma T + \beta T^3$（电子 + 声子）。

**Bloch 定理**：周期势 $V(\vec{r}+\vec{R}) = V(\vec{r})$ 中的波函数

$$
\psi_{\vec{k}}(\vec{r}) = e^{i\vec{k}\cdot\vec{r}}u_{\vec{k}}(\vec{r}), \quad u_{\vec{k}}(\vec{r}+\vec{R}) = u_{\vec{k}}(\vec{r})
$$

**近自由电子模型**：在 Brillouin 区边界 $k = \pi/a$ 处，Bragg 反射打开能隙 $E_g = 2|V_G|$。

**紧束缚模型**（tight-binding）：

$$
E(k) = E_0 - 2t\cos(ka) \quad \text{(一维)}
$$

带宽 $W = 4t$（$t$ 为跃迁积分）。这正是 §6 数值实验的内容。

### 代码演示：紧束缚模型能带

```python
"""
紧束缚模型(Tight-Binding)能带结构。
一维原子链, 每个原子贡献一个 s 轨道, 最近邻跃迁 t。
E(k) = E₀ - 2t·cos(ka)
反直觉: 自由电子 E=ℏ²k²/2m 是抛物线, 但周期势下 E(k) 变成余弦形!
在 Brillouin 区边界 k=±π/a 发生能带分裂。
"""
import math

E0 = 0.0  # 原子轨道能量（参考点）
t = 1.0   # 跃迁积分（归一化）

print("=== 一维紧束缚能带 E(k) = E₀ - 2t·cos(ka) ===")
print(f"参数: E₀={E0}, t={t}")
print(f"带宽 W = 4t = {4*t}")
print(f"{'k·a/π':>8} {'E(k)':>8} {'说明':>20}")
for ka_frac in [-1.0, -0.8, -0.5, -0.2, 0.0, 0.2, 0.5, 0.8, 1.0]:
    ka = ka_frac * math.pi
    E = E0 - 2*t*math.cos(ka)
    note = ""
    if abs(ka_frac) < 0.05: note = "带底 E=E₀-2t"
    elif abs(abs(ka_frac)-1.0) < 0.05: note = "带顶 E=E₀+2t"
    print(f"{ka_frac:>8.2f} {E:>+8.4f} {note:>20}")

# 有效质量: E ≈ E₀-2t + t(ka)² 在带底
# 对比自由电子: E = ℏ²k²/2m*
# → m* = ℏ²/(2ta²) （有效质量由跃迁决定!）
m_star_over_m = 1.0 / (2 * t)  # 归一化 ℏ=a=1
print(f"\n有效质量 m* = ℏ²/(2ta²)")
print(f"在带底, 电子表现为质量为 m* 的自由粒子")
print(f"→ t 大（强耦合）→ m* 小（电子轻，迁移率高）")
print(f"→ t 小（弱耦合）→ m* 大（电子重，局域化）")

# 费米面的位置（半填充）
print(f"\n=== 半填充情况（每个原子贡献 1 个电子）===")
kF = math.pi / 2  # Fermi 波矢 = π/(2a)
EF = E0 - 2*t*math.cos(kF)
print(f"Fermi 波矢 k_F = π/(2a) = {kF:.4f}/a")
print(f"Fermi 能 E_F = E₀ - 2t·cos(π/2) = {EF:.4f}")
print(f"→ 半填充时 E_F = E₀（能带中央），体系为金属")
print(f"→ 若每原子 2 个电子（带满）→ 绝缘体!")
```

> **反直觉发现**：在紧束缚模型中，电子的「有效质量」$m^*$ 由跃迁积分 $t$ 决定——$t$ 越大电子越「轻」。这意味着在强耦合的晶格中电子反而更容易移动，与直觉（耦合强 = 移动慢）相反。物理原因是：$t$ 大意味着原子轨道重叠多，电子在格点间隧穿越容易。

---

## 4. 半导体的电子结构

### 直觉

半导体是现代文明的物理基础——晶体管、芯片、太阳能电池、LED 全部建立在半导体的能带结构上。半导体的关键特征是**适中大小的禁带**（硅 $E_g = 1.12$ eV，锗 $0.67$ eV，砷化镓 $1.42$ eV），使得在室温下有少量电子从价带热激发到导带，产生可操控的载流子。

**掺杂**是半导体技术的核心魔法：在硅中掺入磷（5 价，多一个电子）提供导带电子（n 型），掺入硼（3 价，少一个电子）在价带留下空穴（p 型）。ppm 量级的掺杂就能将电导率改变数个量级——这是任何纯物质无法想象的灵敏度。

### 公式

**本征载流子浓度**：

$$
n_i = \sqrt{N_c N_v}\,e^{-E_g/(2k_BT)}
$$

其中 $N_c, N_v$ 为导带/价带有效态密度。

**掺杂电导率**：

$$
\sigma = e(n\mu_e + p\mu_h)
$$

**p-n 结**：耗尽层宽度

$$
W = \sqrt{\frac{2\varepsilon(V_0 - V)}{e}\frac{N_A + N_D}{N_A N_D}}
$$

**二极管方程**（Shockley）：

$$
I = I_0\left(e^{eV/k_BT} - 1\right)
$$

### 代码演示：半导体的温度依赖

```python
"""
硅的载流子浓度和电导率 vs 温度。
反直觉: 本征半导体在高温下电导率增加（vs 金属减少）。
这是半导体区别于金属的根本特征。
"""
import math

kB = 8.617e-5  # eV/K
Eg_Si = 1.12   # 硅禁带宽度 eV

print("=== 硅本征载流子浓度 n_i vs 温度 ===")
print(f"禁带 E_g = {Eg_Si} eV")
print(f"n_i ∝ T^(3/2) exp(-E_g / 2kT)")
# 前因子近似为 ~5×10^19 × T^1.5 (T in K)
print(f"{'T (K)':>8} {'kT (meV)':>10} {'n_i (cm⁻³)':>14} {'状态':>15}")
for T in [10, 77, 200, 300, 400, 500, 600, 1000]:
    kT = kB * T * 1000  # meV
    # n_i ≈ 5e19 * (T/300)^1.5 * exp(-Eg/(2kT))
    ni = 5e19 * (T/300)**1.5 * math.exp(-Eg_Si / (2*kB*T))
    if T < 50: status = "冻结（绝缘体）"
    elif T < 200: status = "极低载流子"
    elif T < 350: status = "室温工作区"
    elif T < 500: status = "本征激发增强"
    else: status = "高温（漏电流大）"
    print(f"{T:>8} {kT:>10.2f} {ni:>14.2e} {status:>15}")

print("\n→ 室温(300K): n_i ≈ 1e10 cm⁻³（纯硅几乎绝缘）")
print("→ 1000K: n_i 暴增到 ~1e18 → 接近导体（芯片失效！）")
print("→ 这就是芯片有工作温度上限（~150°C）的物理原因")

# 掺杂效应
print(f"\n=== 掺杂对电导率的影响（300K）===")
print(f"{'掺杂':>12} {'n (cm⁻³)':>12} {'σ (S/m)':>12} {'倍数':>10}")
ni_300 = 1e10
sigma_intrinsic = ni_300 * 1.6e-19 * 1500 * 1e-4  # μ_n≈1500 cm²/Vs
for label, n_dop in [("本征", 1e10), ("轻掺 1e15", 1e15), 
                      ("中掺 1e17", 1e17), ("重掺 1e19", 1e19)]:
    sigma = n_dop * 1.6e-19 * 1500 * 1e-4  # n型, μ=1500
    ratio = sigma / sigma_intrinsic
    print(f"{label:>12} {n_dop:>12.1e} {sigma:>12.2f} {ratio:>10.0f}x")
print("→ 掺杂 1e19 比本征电导率高 10⁹ 倍！")
```

---

## 5. 超导电性

### 直觉

超导是凝聚态物理最壮观的现象：某些材料在临界温度 $T_c$ 以下电阻**精确为零**，磁场被完全排出体内（**Meissner 效应**）。这不是「电阻极小」，而是**真正的零**——一个超导环中的电流可以维持数十亿年不衰减。

超导的微观机制由 **BCS 理论**（Bardeen-Cooper-Schrieffer, 1957）解释：电子通过声子交换配对形成 **Cooper 对**。配对后的电子对是玻色子（自旋为零），可以凝聚到同一量子态——这就是超导态。

**ETH 连接**：1986 年，IBM Zürich 实验室的 Bednorz 和 Müller 发现了铜氧化物高温超导（$T_c = 35$ K），打破了保持 15 年的 $T_c$ 记录，次年获诺贝尔奖。ETH 与 IBM Zürich 地理相邻、学术共生，这一发现直接影响了 ETH 凝聚态物理的研究方向。至今，高温超导的完整理论仍是未解之谜。

### 公式

**London 方程**（Meissner 效应的唯象描述）：

$$
\frac{\partial \vec{J}_s}{\partial t} = \frac{n_s e^2}{m}\vec{E}, \qquad \nabla\times\vec{J}_s = -\frac{n_s e^2}{m}\vec{B}
$$

**London 穿透深度**：

$$
\lambda_L = \sqrt{\frac{m}{\mu_0 n_s e^2}}
$$

**BCS 关键预言**：

- Cooper 对结合能：$\Delta(0) = 1.76\,k_B T_c$
- 能隙温度依赖：$\Delta(T) \approx \Delta(0)\left[1.74 - 3.06\sqrt{T_c/T - 1}\right]$（近 $T_c$）
- 相干长度：$\xi_0 = \frac{\hbar v_F}{\pi\Delta}$

**临界磁场**（第一类超导体）：

$$
H_c(T) = H_c(0)\left[1 - \left(\frac{T}{T_c}\right)^2\right]
$$

**磁通量子化**（第二类超导体）：

$$
\Phi_0 = \frac{h}{2e} = 2.07 \times 10^{-15}\,\text{Wb}
$$

### 代码演示：超导能隙与比热跃变

```python
"""
BCS 超导体的能隙 Δ(T) 和电子比热跃变。
反直觉: 超导相变时比热在 Tc 处不连续跃变（二级相变），
       但没有潜热（熵连续）。
"""
import math

# BCS 能隙近似公式（有效范围 0 < T/Tc < 0.95）
def bcs_gap(t_ratio):
    """Δ(T)/Δ(0) 的近似表达式。t_ratio = T/Tc。"""
    if t_ratio >= 1.0:
        return 0.0
    if t_ratio <= 0.01:
        return 1.0  # T→0 时 Δ→Δ(0)
    if t_ratio < 0.5:
        # 低温近似: tanh(1.74 √(Tc/T - 1))
        return math.tanh(1.74 * math.sqrt(1.0/t_ratio - 1))
    # 近 Tc: (Tc/T - 1) 的幂律
    delta = 1.74 * math.sqrt(1.0/t_ratio - 1)
    # 更好的全域近似
    return math.tanh(1.74 * math.sqrt(max(1.0/t_ratio - 1, 0)))

print("=== BCS 能隙 Δ(T)/Δ(0) ===")
print("Δ(0) = 1.76 kTc")
print(f"{'T/Tc':>6} {'Δ/Δ(0)':>8} {'2Δ(0)/kTc':>10}")
for t in [0.0, 0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]:
    gap = bcs_gap(t)
    ratio = 2 * 1.76  # 2Δ(0)/kTc ≈ 3.52
    print(f"{t:>6.2f} {gap:>8.4f} {ratio if t < 0.01 else '':>10}")

print("→ T→0: Δ→Δ(0)（完整能隙）")
print("→ T→Tc: Δ→0（能隙关闭，超导消失）")

# 比热跃变
print(f"\n=== 超导比热跃变 (T=Tc) ===")
print("正常态电子比热: C_n = γT (线性)")
print("超导态: C_s(Tc) = 2.43 × γTc  (BCS 精确结果)")
jump = 2.43
print(f"比热跃变 ΔC/γTc = {jump:.2f}")
print("→ 比热不连续跳跃 143%，但熵连续（二级相变）")

# 超导材料 Tc 对比
print(f"\n=== 超导材料临界温度 ===")
materials = [
    ("Hg (传统金属)", 4.2, 1911),
    ("Pb", 7.2, 1913),
    ("Nb₃Sn", 18.0, 1954),
    ("铜氧化物 (Bednorz-Müller)", 35.0, 1986),
    ("YBCO", 92.0, 1987),
    ("铁基超导", 55.0, 2008),
    ("H₂S (高压)", 203.0, 2015),
    ("LK-99 (争议)", 400.0, 2023),
]
for name, tc, year in materials:
    bar = '#' * int(tc / 5)
    note = " ⚠️未证实" if "争议" in name else ""
    print(f"  {name:>25}: Tc = {tc:>6.1f} K ({year}){note} {bar}")

print("\n→ 1986 Bednorz-Müller 发现打破 15 年僵局（IBM Zürich!）")
print("→ 液氮沸点 77K 以上（YBCO 92K）→ 可用廉价液氮冷却")
```

> **反直觉发现**：超导相变在 $T_c$ 处比热**跃变** 143%，但这不是一级相变——**熵是连续的**（无潜热）。这是二级相变的标志性特征，对应对称性的自发破缺（U(1) 规范对称性破缺）。BCS 理论预言的 $\Delta C/\gamma T_c = 1.43$ 与实验精确吻合，是 BCS 正确性的关键证据之一。

---

## 6. Python 数值实验

### 6.1 电子能带结构（近自由电子模型）

```python
"""
近自由电子(NFE)模型: 周期势 V(x) = 2V_G·cos(2πx/a) 中的电子。
展示 Brillouin 区边界处的能隙打开。
"""
import math

a = 1.0  # 晶格常数
VG = 0.5  # 倒易格点势能分量

print("=== 近自由电子: 能隙在 Brillouin 区边界打开 ===")
print(f"{'k (×π/a)':>10} {'E_-(k)':>8} {'E_+(k)':>8} {'gap':>8}")
for k_frac in [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
    k = k_frac * math.pi / a
    # 自由电子能量
    E0 = k**2 / 2  # ℏ²/2m = 1
    # 在 k = ±π/a 处 (k 和 k-G 耦合)
    kG = k - 2*math.pi/a
    E0G = kG**2 / 2
    # 二阶简并微扰
    avg = (E0 + E0G) / 2
    diff = (E0 - E0G) / 2
    root = math.sqrt(diff**2 + VG**2)
    E_minus = avg - root
    E_plus = avg + root
    gap = E_plus - E_minus
    print(f"{k_frac:>10.1f} {E_minus:>8.4f} {E_plus:>8.4f} {gap:>8.4f}")

print(f"\n→ 能隙 E_g = 2|V_G| = {2*VG}")
print("→ 在 k=π/a (Brillouin区边界)，自由电子简并被周期势打开")
print("→ 这就是绝缘体/半导体存在禁带的根本原因")
```

### 6.2 Ising 铁磁/反铁磁的平均场理论

```python
"""
磁性平均场理论: Curie-Weiss 定律。
铁磁 T<Tc 自发磁化, T>Tc 磁化率 χ ∝ 1/(T-Tc)。
"""
import math

# 平均场 Tc = zJ/kB, z=配位数
def magnetization_MF(t_ratio):
    """t_ratio = T/Tc。"""
    if t_ratio >= 1.0:
        return 0.0
    m = 0.5
    for _ in range(500):
        m_new = math.tanh(m / t_ratio)
        if abs(m_new - m) < 1e-10:
            return m_new
        m = m_new
    return m

print("=== Ising 平均场自发磁化 M(T) ===")
print(f"{'T/Tc':>6} {'M(T)':>8}")
for t in [0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99, 1.0, 1.5]:
    m = magnetization_MF(t)
    bar = '#' * int(m * 40)
    print(f"{t:>6.2f} {m:>8.4f} {bar}")

print("\n→ T<Tc: M≠0 (铁磁有序), T>Tc: M=0 (顺磁)")
print("→ 近 Tc: M ∝ (Tc-T)^(1/2) (平均场临界指数 β=1/2)")
```

---

## 7. 习题集

### 基础题（Kittel 级别）

**P6.1** 铜是 FCC 结构，晶格常数 $a = 3.61$ Å。求铜的密度（原子量 63.55）。

> **提示**：FCC 每原胞 4 个原子。

**P6.2** 用 Debye 模型证明低温热容 $C_V \propto T^3$，并估算铜的 Debye 温度 $\Theta_D \approx 343$ K。

### 中级题（Ashcroft & Mermin 级别）

**P6.3**（自由电子气）钾的密度 $\rho = 0.86$ g/cm³，原子量 39.1，每个原子贡献 1 个传导电子。计算费米能 $E_F$、费米温度 $T_F$ 和费米波矢 $k_F$。

> **答案**：$E_F \approx 2.1$ eV，$T_F \approx 2.5\times 10^4$ K。

**P6.4**（紧束缚）一维紧束缚能带 $E(k) = E_0 - 2t\cos(ka)$。求电子的有效质量 $m^*$（在带底）和群速度 $v_g(k)$。

> **答案**：$m^* = \hbar^2/(2ta^2)$，$v_g = 2ta\sin(ka)/\hbar$。

**P6.5**（p-n 结）硅 p-n 结，$N_A = 10^{17}$ cm⁻³，$N_D = 10^{16}$ cm⁻³。求 300K 下的内建电势 $V_0$ 和耗尽层宽度 $W$。

### 挑战题（ETH 考试 / Bednorz-Müller 级别）

**P6.6**（BCS 理论）推导 Cooper 不稳定性：两个动量相反的电子通过任意弱吸引力配对后，费米海能量降低。说明为什么只要存在吸引相互作用，无论多弱，费米海就不稳定。

**P6.7**（高温超导）铜氧化物超导体的 $T_c$ 与载流子掺杂的关系呈现「穹顶」形状：欠掺杂和过掺杂都降低 $T_c$。讨论这一现象的可能理论解释（反铁磁母体 → 赝能隙 → 超导穹顶）。

> **ETH 关联**：Bednorz-Müller 1986 年在 IBM Zürich 发现铜氧化物超导，开启了高温超导时代。ETH 与 IBM Zürich 的紧密合作使 ETH 成为超导研究的重要基地。

---

## 8. 不足与延伸

### 本主题的局限

1. **独立电子近似**：能带论假设电子之间无关联（除了通过 Pauli 不相容）。但强关联电子体系（过渡金属氧化物、高温超导体）中电子-电子库仑相互作用是核心，单电子能带论失效。Mott 绝缘体就是经典反例：能带论预言为导体，实际为绝缘体。

2. **BCS 的局限**：传统 BCS 理论预言 $T_c < 30$ K 左右（McMillan 公式），无法解释铜氧化物的 $T_c > 100$ K。高温超导机制至今未完全理解，是凝聚态物理最大的未解之谜之一。

3. **无序效应**：Anderson 局域化——无序足够强时，所有电子态都变为局域的，金属变成绝缘体。这是凝聚态物理最深刻的结果之一（Anderson 定理）。

4. **二维物理的特殊性**：Mermin-Wagner 定理禁止二维连续对称性自发破缺，但 Kosterlitz-Thouless 相变提供了二维超流/超导的替代机制（拓扑缺陷.unbind）。

### 延伸方向

| 方向 | 课程/教材 |
|------|----------|
| 凝聚态理论 | ETH 402-3101-00L CMT / Coleman, Mahan |
| 超导理论 | Tinkham *Introduction to Superconductivity* |
| 拓扑绝缘体 | Bernevig & Hughes *Topological Insulators* |
| 强关联电子 | Auerbach *Interacting Electrons and Quantum Magnetism* |
| 软凝聚态 | Chaikin & Lubensky *Principles of Condensed Matter Physics* |

### ETH 特色注记

ETH 的固体物理教学深度植根于**实验传统**：PSI 的中子散射（SINQ）直接测量声子色散和磁结构，SLS 同步辐射光源探测电子能带结构（ARPES），SwissFEL 观测超快动力学。ETH 学生在学习 Ashcroft & Mermin 的理论框架时，可以亲手在 PSI 获得实验数据验证。这种「理论-实验共生」是 ETH 凝聚态物理的核心优势。

Bednorz-Müller 的高温超导发现（IBM Zürich, 1986）在 ETH 引发了持久的研究热潮。ETH 的凝聚态理论组至今活跃在高温超导、拓扑物态、量子材料的前沿。ETH 教授如 Oleg Yazyev（拓扑材料）、Nikolay Chernov（关联电子）代表了新一代 ETH 固体物理的传承——从晶格振动到拓扑量子计算，ETH 的固体物理课是一切这些前沿研究的起点。

---

> **上一主题**：[05 数学方法](../topic05-math-methods/math-methods.md)
>
> **下一主题**：[07 粒子物理](../topic07-particle-nuclear/particle-nuclear.md) — 从标准模型到 CERN


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：固体物理研究「亿亿个原子组成的固体，为什么有的导电、有的绝缘、有的超导」——核心是量子力学 + 周期对称 → 能带 + 拓扑 + 关联，把 $10^{23}$ 个电子压缩成几个宏观量。
>
> **生活类比**：把固体想象成一座**巨型足球场**（晶格），观众席上坐着电子。空场地里观众随便走（自由电子，金属）；座位间有栏杆（能隙，绝缘体）；栏杆只到膝盖（半导体，光能踢电子过去）；观众手拉手集体跳舞（超导）。固体的「性格」全在「栏杆的高度与形状」。
>
> **反直觉发现（啊哈时刻）**：
> - **超导零电阻不是「电阻变小」**：电阻是**精确的零**，电流一旦流动可维持数年不衰减——量子力学的宏观体现。
> - **Meissner 效应 ≠ 零电阻**：零电阻只是「磁场进得来出不去」，Meissner 是「主动把磁场推出去」——两个不同现象。
> - **整数量子霍尔效应是拓扑**：Hall 电导被锁定在 $\nu e^2/h$，整数 $\nu$ 是「陈数」——晶格细节不重要，几何不变量统治物理。
> - **声子是「集体幻觉」**：原子集体振动的量子化模式，但单个原子不会「声子」——它是涌现粒子，和电子一样真实。
> - **莫尔超晶格改变一切**：两层石墨烯扭 1.1° 形成「魔法角」，平能带 → 关联绝缘体 + 非常规超导（2018 Cao et al.）——一个旋钮调出整个关联物理。

---

## 🔗 衔接：从哪来，到哪去

### ▶ 前置
- **量子力学（03）**：布洛赫定理 = 平移对称下的波函数；费米海 = $T=0$ 的电子统计。
- **统计物理（04）**：声子是 Bose 子、电子是 Fermi 子、费米能 = $T=0$ 占据边界。
- **群论（05）**：晶体由空间群分类，能带用不可约表示标记。

### ⚡ 旧框架的危机
1. **Drude 模型解释不了超导**：经典电子气无法产生零电阻与 Meissner——需要 BCS 配对（1957）。
2. **Landau 对称破缺不够用**：量子霍尔效应没有对称破缺，却是「相变」——拓扑序的概念革命。
3. **高温超导无共识机制**：铜基 $T_c$ 高达 164 K（常压），BCS 电子-声子解释不了——强关联物理至今未解。

### 🆕 新框架的危机
- **莫尔材料参数空间爆炸**：扭角、层数、压力、电场——组合无限，理论跟不上实验。
- **拓扑物态分类未完**：弗洛凯、高阶、非阿贝尔——需要新的拓扑不变量数学。
- **量子材料设计**：如何「定制」具有所需物性的新材料？AI + 量子模拟给出部分答案。

### 🚀 后续
| 后续主题 | 用到的固体概念 |
|---------|---------------|
| 07 粒子物理 | 凝聚态类比（Higgs = 超导序参量，Goldstone = 声子）；格点 QCD 借鉴张量网络 |
| 08 GR/宇宙学 | 凝聚态类比全息对偶（AdS/CMT）、黑洞 = 量子物态的极端版本 |

---

## 🏭 理论联系实际：5 个应用

1. **超导磁体**：MRI（3 T）、LHC 弯转磁体（8 T）、核聚变 ITER（13 T）、Maglev 列车——PSI 的 Muon Cooling、CERN 的粒子加速器全靠 NbTi/Nb₃Sn 超导线。
2. **半导体芯片产业**：能带工程 → MOSFET、FinFET、GAA；2D 材料（MoS₂）作为后硅候选；台积电/Intel 工程师每天都在解能带与散射。
3. **量子点显示（QLED）**：3 nm 量子点能级由尺寸决定（量子限制）——三星电视的色彩纯度来自「尺寸调谐」的量子力学。
4. **PSI 同步辐射与中子散射**：SLS 2.0（ARPES 看电子能带）、SINQ（中子看自旋/声子）、SwissFEL（超快动力学）——ETH 学生的标准实验工具。
5. **拓扑量子计算候选**：分数量子霍尔任意子、马约拉纳零模、转角石墨烯——微软 Majorana 1（2025）、量子计算机的「拓扑免疫」路线。

---

## 🔬 最新研究前沿（2024-2026）

1. **菱面体多层石墨烯的非常规超导**（2024, *Nature*）：MIT Han 组在 rhombohedral 四/五层石墨烯观测到 robust 超导 + 关联绝缘，$T_c$ 显著、对磁场敏感，强烈指向自旋三重态 / 非常规配对——BCS 之外的新超导家族。
2. **Kagome 金属 AV₃Sb₅ 的手性电荷序**（2024-2025）：CsV₃Sb₅、KV₃Sb₅ 显示非公度电荷密度波 + 可能的超导 + 手性；ETH 凝聚态组参与 ARPES/STM——「几何阻挫 + 拓扑 + 关联」三合一。
3. **分数量子反常霍尔效应（FQAHE）**（2023-2024）：在 moiré 材料中无需外磁场实现分数量子霍尔——2024 多组（Park, Lucas, ETH 合作）演示，通往非阿贝尔任意子与拓扑量子计算的关键平台。
4. **Nickelate 高温超导的成熟**（2023-2025）：无限层 Nd₀.八Sr₀.二NiO₂、双层 Nickelate $T_c$ 突破 80 K——铜基超导 30 年后的第一个真正「兄弟家族」，挑战现有强关联理论。
5. **AI 设计量子材料**（2024-2025）：GNoME（Google DeepMind, 2023.12 发现 220 万新晶体）、MatterGen（微软 2024）——大规模生成稳定晶体结构，ETH 理论组、PSI 实验组跟进验证；超导新材料搜索被加速 10⁴ 倍。

---

## 🗺️ 学习 Roadmap（ETH 路径）

### ETH 课程编号
- **402-0502-00L Solid State Physics**（BSc 第三年，Ashcroft & Mermin 路线）
- **402-9142-00L Advanced Solid State Physics**（MSc，拓扑 / 关联电子）
- **402-9122-00L Topological Phases of Matter**（MSc，Bernevig 教材）
- **402-0705-00L Quantum Materials and Devices**（对接 PSI 实验）

### 14 周学习节奏
| 阶段 | 内容 | 知识检查 |
|------|------|----------|
| W1-3 晶体 + 倒格子 | 布喇伐格子、倒空间、布洛赫定理 | 解释为什么倒格子傅立叶变换出现。 |
| W4-6 声子与热学 | Debye 模型、声子色散、比热 $T^3$ 律 | 推出低温绝缘体 $C_v\propto T^3$。 |
| W7-9 自由电子气 + 能带 | Sommerfeld、Fermi 面、近自由电子、紧束缚 | 解释为什么铜是金属、金刚石是绝缘体。 |
| W10-11 半导体 | 有效质量、PN 结、MOSFET 原理 | 推出二极管 I-V 特性。 |
| W12-14 超导与拓扑 | BCS、Meissner、Hall 效应、拓扑绝缘体 | 解释「陈数」如何量子化 Hall 电导。 |

### 费曼检验
- 能解释「为什么金刚石透明、铜不透明」 → 能带过关。
- 能讲清「Meissner 不是零电阻推论」 → 超导过关。
- 能用拓扑不变量解释量子霍尔效应 → 可进拓扑量子计算。
