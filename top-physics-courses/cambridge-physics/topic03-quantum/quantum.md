# Cambridge Part IB/II · Quantum Mechanics

> **教材**：Shankar *Principles of Quantum Mechanics* (2nd ed.) — Cambridge Part IB 核心；Cohen-Tannoudji, Diu & Laloë *Quantum Mechanics* (2 vols.) — Part II 深度补充
>
> **Cambridge 课程编号**：Part IB Quantum Mechanics + Part II Quantum Physics
>
> **Cambridge 特色**：Dirac 的 legacy——从 bras/kets 到泊松括号的量子化；Cavendish 在原子物理/量子光学的实验根基

---

## 目录

1. [量子力学的数学基础](#1-量子力学的数学基础)
2. [薛定谔方程](#2-薛定谔方程)
3. [一维势场](#3-一维势场)
4. [谐振子与代数方法](#4-谐振子与代数方法)
5. [氢原子](#5-氢原子)
6. [角动量与自旋](#6-角动量与自旋)
7. [微扰理论](#7-微扰理论)
8. [Python 代码演示](#8-python-代码演示)
9. [Tripos 风格习题](#9-tripos-风格习题)

---

## 1. 量子力学的数学基础

### 1.1 希尔伯特空间与 Dirac 记法

量子态是复希尔伯特空间 $\mathcal{H}$ 中的矢量。Dirac（Cavendish 传统核心人物）发明的 bra-ket 记号：

- **Ket** $|\psi\rangle$ — 态矢量（列向量）
- **Bra** $\langle\phi|$ — 对偶矢量（行向量）
- **内积** $\langle\phi|\psi\rangle \in \mathbb{C}$

公理：$\langle\phi|\psi\rangle^* = \langle\psi|\phi\rangle$（共轭对称性），$\langle\psi|\psi\rangle \ge 0$（正定性）。

### 1.2 算符与可观测量

物理可观测量对应**厄米算符** $\hat{A} = \hat{A}^\dagger$。厄米算符的关键性质：
1. 本征值为实数：$A|a\rangle = a|a\rangle$，$a \in \mathbb{R}$
2. 不同本征值的本征态正交：$\langle a'|a\rangle = \delta_{a'a}$
3. 构成完备基：$|\psi\rangle = \sum_a |a\rangle\langle a|\psi\rangle$（完备性关系 $\sum_a|a\rangle\langle a| = \hat{I}$）

### 1.3 测量公设

测量可观测量 $\hat{A}$：
1. 结果只能是本征值 $a_n$ 之一
2. 测得 $a_n$ 的概率 $P(a_n) = |\langle a_n|\psi\rangle|^2$
3. 测量后态**坍缩**到 $|a_n\rangle$（投影公设）

**反直觉的核心**：测量不是"被动观察"，而是**主动改变**系统状态。这是量子力学与经典物理最深刻的分歧。

### 1.4 不确定性原理

对任意两个厄米算符 $\hat{A}, \hat{B}$：

$$\Delta A \cdot \Delta B \ge \frac{1}{2}|\langle[\hat{A}, \hat{B}]\rangle|$$

特别地，位置-动量：$[\hat{x}, \hat{p}] = i\hbar$，故：

$$\Delta x \cdot \Delta p \ge \frac{\hbar}{2}$$

这不是测量精度不够，而是**自然界的基本限制**——粒子不存在同时确定的位置和动量。

---

## 2. 薛定谔方程

### 2.1 含时薛定谔方程

$$i\hbar\frac{\partial}{\partial t}|\psi(t)\rangle = \hat{H}|\psi(t)\rangle$$

哈密顿算符 $\hat{H}$ 是能量算符。对于质量 $m$ 的粒子在势场 $V$ 中：

$$\hat{H} = \frac{\hat{p}^2}{2m} + V(\hat{x}) = -\frac{\hbar^2}{2m}\nabla^2 + V(\mathbf{r})$$

### 2.2 定态薛定谔方程

若 $\hat{H}$ 不显含时间，分离变量 $|\psi(t)\rangle = e^{-iEt/\hbar}|\phi\rangle$：

$$\hat{H}|\phi\rangle = E|\phi\rangle$$

这就是**定态薛定谔方程**（能量本征值方程）。通解是定态的叠加：

$$|\psi(t)\rangle = \sum_n c_n e^{-iE_n t/\hbar}|n\rangle$$

### 2.3 连续性与概率守恒

定义概率密度 $\rho = |\psi|^2$ 和概率流：

$$\mathbf{j} = \frac{\hbar}{2mi}(\psi^*\nabla\psi - \psi\nabla\psi^*)$$

则连续性方程保证概率守恒：

$$\frac{\partial \rho}{\partial t} + \nabla \cdot \mathbf{j} = 0$$

---

## 3. 一维势场

### 3.1 无限深势阱

$$V(x) = \begin{cases} 0 & 0 < x < L \\ \infty & \text{otherwise} \end{cases}$$

本征态和本征值：

$$\phi_n(x) = \sqrt{\frac{2}{L}}\sin\frac{n\pi x}{L}, \quad E_n = \frac{n^2\pi^2\hbar^2}{2mL^2}$$

**关键特征**：
- 能量**量子化**（$E_n \propto n^2$）
- 基态能量 $E_1 > 0$（零点能——不确定性原理的直接后果）
- 波函数在边界为零（硬墙边界条件）

### 3.2 有限深势阱与隧穿

有限深势阱 $V(x) = -V_0$（$|x|<a$），$V=0$（外部）：

- 束缚态 ($E < 0$)：波函数在阱外指数衰减 $e^{-\kappa|x|}$，$\kappa = \sqrt{2m|E|}/\hbar$
- 有限个束缚态（取决于 $V_0 a^2$）
- **散射态** ($E > 0$)：部分透射部分反射

**量子隧穿**：即使 $E < V_0$（经典禁区），粒子有一定概率穿透势垒。透射系数（方势垒）：

$$T \approx e^{-2\kappa a}, \quad \kappa = \sqrt{2m(V_0 - E)}/\hbar$$

隧穿的物理后果：$\alpha$ 衰变、扫描隧道显微镜 (STM)、半导体隧道二极管。

### 3.3 δ 函数势

$V(x) = -\alpha\delta(x)$——最简单的可解束缚态模型。

唯一的束缚态：$E = -\frac{m\alpha^2}{2\hbar^2}$，$\phi(x) = \sqrt{\frac{m\alpha}{\hbar^2}}e^{-m\alpha|x|/\hbar^2}$

波函数在 $x=0$ 处连续但**导数不连续**：$\Delta\phi' = -\frac{m\alpha}{\hbar^2}\phi(0)$——这直接反映了 $\delta$ 函数势的奇异性。

---

## 4. 谐振子与代数方法

### 4.1 升降算符

一维谐振子 $V = \frac{1}{2}m\omega^2 x^2$ 是量子力学最重要的可解模型。

定义**升降算符**（Dirac 的天才方法）：

$$\hat{a} = \sqrt{\frac{m\omega}{2\hbar}}\left(\hat{x} + \frac{i\hat{p}}{m\omega}\right), \quad \hat{a}^\dagger = \sqrt{\frac{m\omega}{2\hbar}}\left(\hat{x} - \frac{i\hat{p}}{m\omega}\right)$$

对易关系：$[\hat{a}, \hat{a}^\dagger] = 1$

哈密顿量：$\hat{H} = \hbar\omega\left(\hat{a}^\dagger\hat{a} + \frac{1}{2}\right) = \hbar\omega\left(\hat{N} + \frac{1}{2}\right)$

### 4.2 能谱

$$E_n = \hbar\omega\left(n + \frac{1}{2}\right), \quad n = 0, 1, 2, \ldots$$

- $\hat{a}^\dagger|n\rangle = \sqrt{n+1}|n+1\rangle$（升）
- $\hat{a}|n\rangle = \sqrt{n}|n-1\rangle$（降）
- $\hat{a}|0\rangle = 0$（基态被湮灭为零）

基态波函数：$\phi_0(x) = \left(\frac{m\omega}{\pi\hbar}\right)^{1/4}e^{-m\omega x^2/(2\hbar)}$

**零点能** $E_0 = \frac{1}{2}\hbar\omega$ 是不确定性原理的必然结果——粒子被束缚在有限空间，必有非零动量，故必有非零能量。

### 4.3 相干态

定义相干态：$|\alpha\rangle = e^{-|\alpha|^2/2}\sum_n \frac{\alpha^n}{\sqrt{n!}}|n\rangle$

它是 $\hat{a}$ 的本征态：$\hat{a}|\alpha\rangle = \alpha|\alpha\rangle$。

相干态是**最接近经典的量子态**——在谐振子势中，相干态的波包像经典粒子一样振荡而不扩散（最小不确定波包）。激光就是相干态的光子场。

---

## 5. 氢原子

### 5.1 径向方程

中心势 $V(r) = -\frac{e^2}{4\pi\epsilon_0 r}$。分离变量 $\psi(r,\theta,\phi) = R(r)Y_l^m(\theta,\phi)$。

径向方程（令 $u = rR$）：

$$-\frac{\hbar^2}{2m}\frac{d^2u}{dr^2} + \left[-\frac{e^2}{4\pi\epsilon_0 r} + \frac{\hbar^2 l(l+1)}{2mr^2}\right]u = Eu$$

### 5.2 能级

束缚态能量（玻尔能级）：

$$E_n = -\frac{mc^2\alpha^2}{2n^2} = -\frac{13.6\text{ eV}}{n^2}$$

其中 $\alpha = e^2/(4\pi\epsilon_0\hbar c) \approx 1/137$ 是精细结构常数。

**简并度**：$n^2$ 重简并（$l = 0, \ldots, n-1$，$m = -l, \ldots, +l$）。这个"额外的"简并（比一般中心力场多）源于 Runge-Lenz 矢量的隐藏 $SO(4)$ 对称性（见 Topic 1 §2.3）。

### 5.3 波函数

$$\psi_{nlm}(r,\theta,\phi) = R_{nl}(r)Y_l^m(\theta,\phi)$$

$R_{nl}(r)$ 涉及关联拉盖尔多项式。例如基态：

$$\psi_{100} = \frac{1}{\sqrt{\pi a_0^3}}e^{-r/a_0}$$

其中玻尔半径 $a_0 = \frac{\hbar}{\alpha mc} \approx 0.529$ Å。

---

## 6. 角动量与自旋

### 6.1 轨道角动量

$$\hat{L}_i = \epsilon_{ijk}\hat{x}_j\hat{p}_k$$

对易关系：$[\hat{L}_i, \hat{L}_j] = i\hbar\epsilon_{ijk}\hat{L}_k$

共同本征态：$\hat{L}^2 Y_l^m = \hbar^2 l(l+1)Y_l^m$，$\hat{L}_z Y_l^m = m\hbar Y_l^m$

$l = 0, 1, 2, \ldots$；$m = -l, \ldots, +l$（整数！）

### 6.2 自旋

**自旋**是粒子的内禀角动量，与空间运动无关。电子 $s = 1/2$。

自旋算符 $\hat{S}_i$ 满足与轨道角动量相同的代数：$[\hat{S}_i, \hat{S}_j] = i\hbar\epsilon_{ijk}\hat{S}_k$。

但对自旋，量子数可以是**半整数**：$s = 0, \frac{1}{2}, 1, \frac{3}{2}, \ldots$

$$\hat{S}^2|s, m_s\rangle = \hbar^2 s(s+1)|s, m_s\rangle$$
$$\hat{S}_z|s, m_s\rangle = m_s\hbar|s, m_s\rangle$$

### 6.3 Pauli 矩阵

对 $s = 1/2$ 自旋，引入 Pauli 矩阵：

$$\sigma_x = \begin{pmatrix}0&1\\1&0\end{pmatrix}, \quad \sigma_y = \begin{pmatrix}0&-i\\i&0\end{pmatrix}, \quad \sigma_z = \begin{pmatrix}1&0\\0&-1\end{pmatrix}$$

$\hat{S}_i = \frac{\hbar}{2}\sigma_i$。自旋向上 $|\!\uparrow\rangle = \binom{1}{0}$，向下 $|\!\downarrow\rangle = \binom{0}{1}$。

**反直觉**：自旋 $1/2$ 粒子需要"转两圈"才能回到原来的状态！$e^{-i2\pi\hat{S}_z/\hbar}|\!\uparrow\rangle = -|\!\uparrow\rangle$。这个 $-1$ 相因子虽然在孤立状态下不可观测，但在干涉实验中完全可检测。

### 6.4 自旋-轨道耦合

$$\hat{H}_{SO} = \frac{1}{2m^2c^2}\frac{1}{r}\frac{dV}{dr}\hat{\mathbf{L}}\cdot\hat{\mathbf{S}}$$

耦合 $\hat{\mathbf{L}}\cdot\hat{\mathbf{S}} = \frac{1}{2}(\hat{J}^2 - \hat{L}^2 - \hat{S}^2)$。对氢原子 $l > 0$ 态，这导致了精细结构分裂。

---

## 7. 微扰理论

### 7.1 非简并微扰

$\hat{H} = \hat{H}_0 + \lambda\hat{H}'$，已知 $\hat{H}_0|n^{(0)}\rangle = E_n^{(0)}|n^{(0)}\rangle$。

**一阶能量修正**：

$$E_n^{(1)} = \langle n^{(0)}|\hat{H}'|n^{(0)}\rangle$$

就是微扰在未扰动态中的期望值——非常直观。

**二阶能量修正**：

$$E_n^{(2)} = \sum_{k\ne n}\frac{|\langle k^{(0)}|\hat{H}'|n^{(0)}\rangle|^2}{E_n^{(0)} - E_k^{(0)}}$$

注意分母：与高能态耦合使能量**降低**（$E_k^{(0)} > E_n^{(0)}$ 时该项为负）。

### 7.2 Stark 效应

外加均匀电场 $\mathcal{E}$ 下的氢原子：$\hat{H}' = e\mathcal{E}z = e\mathcal{E}r\cos\theta$。

基态 ($n=1$)：一阶修正为零（宇称），二阶修正给出极化率。

激发态 ($n=2$)：四重简并，需用简并微扰理论。结果——线性 Stark 效应——能级分裂与 $\mathcal{E}$ 成正比（不是 $\mathcal{E}^2$）。

### 7.3 含时微扰与跃迁

含时微扰 $\hat{H}'(t)$ 导致能级间跃迁。Fermi 黄金定则：

$$\Gamma_{i\to f} = \frac{2\pi}{\hbar}|\langle f|\hat{H}'|i\rangle|^2 \rho(E_f)$$

$\rho(E_f)$ 是末态密度。这是所有辐射跃迁（吸收/发射）的理论基础。

---

## 8. Python 代码演示

### 8.1 无限深势阱波函数

```python
"""
无限深势阱 (0 < x < L) 的波函数与概率密度
零依赖。
"""
import math

def inf_well_wavefunction(n, x, L=1.0):
    """ψ_n(x) = √(2/L) sin(nπx/L)"""
    return math.sqrt(2/L) * math.sin(n * math.pi * x / L)

def inf_well_energy(n, L=1.0, m=1.0, hbar=1.0):
    """E_n = n²π²ℏ²/(2mL²)"""
    return n**2 * math.pi**2 * hbar**2 / (2 * m * L**2)

L = 1.0
print("=== 无限深势阱 (L=1, ℏ=m=1 自然单位) ===\n")

print("能级:")
for n in range(1, 6):
    E = inf_well_energy(n, L)
    print(f"  E_{n} = {E:.4f} π²/2 = {n**2}× E_1")

print(f"\n关键: E_n ∝ n² (非线性间距)")
print(f"零点能 E_1 = {inf_well_energy(1, L):.4f} > 0")

# 波函数采样
print("\n=== 波函数 ψ_n(x) 采样 ===")
print(f"{'x':>6}", end="")
for n in range(1, 4):
    print(f"  ψ_{n}(x)", end="")
print("   |ψ_1|²")

n_points = 21
for i in range(n_points):
    x = i / (n_points - 1) * L
    print(f"{x:6.3f}", end="")
    vals = []
    for n in range(1, 4):
        v = inf_well_wavefunction(n, x, L)
        vals.append(v)
        print(f"  {v:+7.4f}", end="")
    prob1 = vals[0]**2
    bar = "▓" * int(prob1 * 20)
    print(f"   {prob1:.4f} {bar}")

# 正交性检验
print("\n=== 正交性检验 ∫ψ_m·ψ_n dx = δ_{mn} ===")
# 用梯形积分
N_int = 1000
for m in range(1, 4):
    for n in range(1, 4):
        overlap = 0.0
        for i in range(N_int):
            x = (i + 0.5) / N_int * L
            overlap += inf_well_wavefunction(m, x, L) * inf_well_wavefunction(n, x, L)
        overlap /= N_int  # 归一化 (dx ≈ L/N)
        overlap *= L
        marker = "✓" if (abs(overlap - (1 if m==n else 0)) < 0.01) else "✗"
        print(f"  <{m}|{n}> = {overlap:+.6f}  {marker}")
```

### 8.2 量子隧穿概率

```python
"""
方势垒隧穿系数 T(E)
T = [1 + V₀²sinh²(κa)/(4E(V₀-E))]⁻¹  for E < V₀
T = [1 + V₀²sin²(ka)/(4E(E-V₀))]⁻¹   for E > V₀
零依赖。
"""
import math

def tunneling_probability(E, V0=10.0, a=1.0, m=1.0, hbar=1.0):
    """方势垒 V₀=10, 宽度 a=1"""
    if E < 0:
        return 0.0
    if E == 0:
        return 0.0
    if E < V0:
        kappa = math.sqrt(2*m*(V0 - E)) / hbar
        arg = kappa * a
        sinh_sq = math.sinh(arg)**2
        T = 1.0 / (1.0 + V0**2 * sinh_sq / (4*E*(V0-E)))
        return T
    elif E == V0:
        # 特殊情况
        return 1.0 / (1.0 + m*V0*a**2/(2*hbar**2))
    else:
        k = math.sqrt(2*m*(E - V0)) / hbar
        arg = k * a
        sin_sq = math.sin(arg)**2
        T = 1.0 / (1.0 + V0**2 * sin_sq / (4*E*(E-V0)))
        return T

V0, a = 10.0, 1.0
print("=== 方势垒隧穿 (V₀=10, a=1, ℏ=m=1 自然单位) ===\n")

print(f"{'E':>6} {'E/V₀':>6} {'T(E)':>10} {'-log₁₀(T)':>10} {'类型':>10}")
print("-" * 50)
for E10 in range(1, 200, 2):
    E = E10 / 10.0
    T = tunneling_probability(E, V0, a)
    regime = "隧穿" if E < V0 else ("共振" if abs(T-1.0)>0.01 else "近全透")
    logT = -math.log10(T) if T > 0 else float('inf')
    marker = " ★" if E < V0 and T > 0.01 else ""
    print(f"{E:6.1f} {E/V0:6.2f} {T:10.6f} {logT:10.3f}     {regime}{marker}")

print("\n=== 关键观察 ===")
T_low = tunneling_probability(2.0, V0, a)
T_high = tunneling_probability(8.0, V0, a)
T_over = tunneling_probability(15.0, V0, a)
print(f"E=2.0 (远低于势垒): T={T_low:.6e} → 指数抑制")
print(f"E=8.0 (接近势垒顶): T={T_high:.6f} → 隧穿显著")
print(f"E=15.0 (高于势垒): T={T_over:.6f} → 部分反射（经典不会）!")

# 势垒宽度对隧穿的影响
print("\n=== 隧穿 vs 势垒宽度 (E=5.0, V₀=10.0) ===")
for a10 in range(1, 21):
    a = a10 / 10.0
    T = tunneling_probability(5.0, V0, a)
    bar = "█" * int(-math.log10(max(T, 1e-20)) * 2) if T < 0.5 else ""
    print(f"  a={a:.1f}: T={T:.2e} {bar}")
print("→ T 随 a 指数下降: 这是 STM (扫描隧道显微镜) 的原理")
```

### 8.3 谐振子能级与升降算符

```python
"""
量子谐振子的代数结构
用升降算符从基态构造所有激发态
零依赖。
"""
import math

def ho_wavefunction(n, xi):
    """谐振子波函数 (自然单位 ℏ=m=ω=1)
    ξ = x√(mω/ℏ) = x
    ψ_n(ξ) = (1/√(2^n n! √π)) H_n(ξ) e^{-ξ²/2}
    用递推构造 Hermite 多项式
    """
    # Hermite 多项式递推: H_0=1, H_1=2ξ, H_{n+1}=2ξH_n - 2nH_{n-1}
    if n == 0:
        H = 1.0
    elif n == 1:
        H = 2*xi
    else:
        H_prev, H_curr = 1.0, 2*xi
        for k in range(1, n):
            H_next = 2*xi*H_curr - 2*k*H_prev
            H_prev, H_curr = H_curr, H_next
        H = H_curr

    norm = 1.0 / math.sqrt(2**n * math.factorial(n) * math.sqrt(math.pi))
    return norm * H * math.exp(-xi**2 / 2)

print("=== 量子谐振子 (自然单位 ℏ=m=ω=1) ===\n")

print("能级: E_n = ℏω(n + 1/2) = n + 0.5")
for n in range(6):
    E = n + 0.5
    print(f"  E_{n} = {E:.1f}  {'← 零点能' if n==0 else ''}")

# 升降算符作用验证
print("\n=== 升降算符矩阵元验证 ===")
print("a|n> = √n |n-1>,  a†|n> = √(n+1) |n+1>")
print("<n|a†a|n> = n (粒子数算符)\n")

# 数值验证 <n-1|a|n> = √n
# a = (ξ + d/dξ)/√2
# <m|a|n> = √n δ_{m,n-1}
N_int = 500
xi_max = 5.0
for n in range(1, 5):
    for m in range(0, 5):
        overlap = 0.0
        for i in range(N_int):
            xi = (i + 0.5) / N_int * 2 * xi_max - xi_max
            dxi = 2 * xi_max / N_int
            psi_m = ho_wavefunction(m, xi)
            psi_n = ho_wavefunction(n, xi)
            # a|n> = (ξ + d/dξ)/√2 · ψ_n
            # 数值微分
            psi_n_plus = ho_wavefunction(n, xi + dxi*0.01)
            psi_n_minus = ho_wavefunction(n, xi - dxi*0.01)
            dpsi_n = (psi_n_plus - psi_n_minus) / (2 * dxi * 0.01)
            a_psi_n = (xi * psi_n + dpsi_n) / math.sqrt(2)
            overlap += psi_m * a_psi_n * dxi
        expected = math.sqrt(n) if m == n-1 else 0.0
        if abs(overlap) > 0.01:
            status = "✓" if abs(overlap - expected) < 0.05 else "✗"
            print(f"  <{m}|a|{n}> = {overlap:+.4f} (期望 √{n}={expected:+.4f} if m={n-1} else 0) {status}")

print(f"\n=== 概率密度 |ψ_n(ξ)|² 采样 ===")
print("(展示 n=0,1,2,3 的概率分布)")
print(f"{'ξ':>6}", end="")
for n in range(4):
    print(f"  |ψ_{n}|²", end="")
print()

for i10 in range(-40, 41, 4):
    xi = i10 / 10.0
    print(f"{xi:6.1f}", end="")
    for n in range(4):
        psi = ho_wavefunction(n, xi)
        prob = psi**2
        print(f"  {prob:.4f}", end="")
    print()
```

---

## 9. Tripos 风格习题

### 习题 1（Part IB）：势阱中的高斯波包

质量 $m$ 的粒子在无限深势阱 $0 < x < L$ 中，初始波函数为：

$$\psi(x, 0) = A\,x(L-x)$$

(a) 归一化求 $A$。
(b) 展开为能量本征态 $\psi(x,0) = \sum c_n \phi_n(x)$，求 $c_n$。
(c) 写出 $\psi(x,t)$。
(d) 求能量期望值 $\langle E \rangle$ 和其不确定度 $\Delta E$。

<details>
<summary>解答</summary>

(a) $\int_0^L |A|^2 x^2(L-x)^2 dx = |A|^2 \frac{L^5}{30} = 1 \Rightarrow A = \sqrt{30/L^5}$

(b) $c_n = \int_0^L \phi_n(x)\psi(x,0)\,dx = \sqrt{\frac{2}{L}}\sqrt{\frac{30}{L^5}}\int_0^L \sin\frac{n\pi x}{L}x(L-x)\,dx$

利用积分公式，结果只有 $n$ 为奇数时非零：

$$c_n = \begin{cases} \frac{4\sqrt{15}}{n^2\pi^2} & n \text{ 奇} \\ 0 & n \text{ 偶} \end{cases}$$

验证归一化：$\sum_{n\text{ odd}} c_n^2 = \frac{240}{\pi^4}\sum_{k=0}^\infty\frac{1}{(2k+1)^4} = \frac{240}{\pi^4}\cdot\frac{\pi^4}{96} = 1$ ✓

(利用 $\sum_{k=0}^\infty 1/(2k+1)^4 = \pi^4/96$)

(c) $\psi(x,t) = \sum_{n\text{ odd}} c_n\phi_n(x)e^{-iE_n t/\hbar}$

(d) $\langle E\rangle = \sum |c_n|^2 E_n = \frac{480}{\pi^4}\cdot\frac{\pi^2\hbar^2}{2mL^2}\sum_{k=0}^\infty\frac{1}{(2k+1)^2}$

利用 $\sum_{k=0}^\infty 1/(2k+1)^2 = \pi^2/8$：$\langle E\rangle = \frac{480}{\pi^4}\cdot\frac{\pi^4\hbar^2}{16mL^2} = \frac{30\hbar^2}{mL^2} = \frac{10\hbar^2}{\pi^2 m L^2}\cdot\pi^2 = \frac{5\hbar^2}{mL^2}$
</details>

### 习题 2（Part IB）：自旋 1/2 的进动

电子在均匀磁场 $\mathbf{B} = B_0\hat{z}$ 中，初始自旋沿 $\hat{x}$ 方向。

(a) 写出哈密顿量。
(b) 求自旋态 $|\psi(t)\rangle$。
(c) 证明 $\langle S_x(t)\rangle$ 随时间振荡，求进动频率。
(d) 对 $B_0 = 1$ T，计算进动频率（电子回旋频率）。

<details>
<summary>解答</summary>

(a) $\hat{H} = -\boldsymbol{\mu}\cdot\mathbf{B} = \frac{e}{m_e}\hat{\mathbf{S}}\cdot\mathbf{B} = \frac{eB_0}{m_e}\hat{S}_z = \omega_0\hat{S}_z$

其中 $\omega_0 = eB_0/m_e$（注意电子电荷取绝对值，$g \approx 2$）。

(b) 初始态 $|\psi(0)\rangle = |\!\uparrow_x\rangle = \frac{1}{\sqrt{2}}(|\!\uparrow_z\rangle + |\!\downarrow_z\rangle)$

$|\psi(t)\rangle = \frac{1}{\sqrt{2}}(e^{-i\omega_0 t/2}|\!\uparrow_z\rangle + e^{i\omega_0 t/2}|\!\downarrow_z\rangle)$

(c) $\langle S_x\rangle = \langle\psi|\hat{S}_x|\psi\rangle = \frac{\hbar}{2}\cos\omega_0 t$

进动频率 $\omega_0 = eB_0/m_e$。同理 $\langle S_y\rangle = \frac{\hbar}{2}\sin\omega_0 t$——自旋在 $xy$ 平面进动。

(d) $\omega_0/2\pi = eB_0/(2\pi m_e) = 28.0 \times B_0[\text{GHz/T}] = 28.0$ GHz

这是电子自旋共振 (ESR/EPR) 的基础频率。
</details>

### 习题 3（Part II 预习）：氢原子精细结构

(a) 用非简并微扰理论，计算自旋-轨道耦合对氢原子 $n=2, l=1$ 能级的修正。
(b) 证明总角动量 $j$ 是好量子数，并给出修正后的能级。
(c) 数值计算分裂大小（以 eV 为单位）。

<details>
<summary>解答</summary>

(a) $\hat{H}_{SO} = \frac{1}{2m_e^2 c^2}\frac{e^2}{4\pi\epsilon_0}\frac{1}{r^3}\hat{\mathbf{L}}\cdot\hat{\mathbf{S}}$

对 $n=2, l=1$：$j = 1/2$ 或 $j = 3/2$。

$\hat{\mathbf{L}}\cdot\hat{\mathbf{S}} = \frac{1}{2}(\hat{J}^2 - \hat{L}^2 - \hat{S}^2)$

$\langle\hat{\mathbf{L}}\cdot\hat{\mathbf{S}}\rangle = \frac{\hbar^2}{2}[j(j+1) - l(l+1) - s(s+1)]$

(b) 对 $s=1/2, l=1$:
- $j=1/2$: $\langle\hat{\mathbf{L}}\cdot\hat{\mathbf{S}}\rangle = \frac{\hbar^2}{2}[\frac{3}{4}-2-\frac{3}{4}] = -\hbar^2$
- $j=3/2$: $\langle\hat{\mathbf{L}}\cdot\hat{\mathbf{S}}\rangle = \frac{\hbar^2}{2}[\frac{15}{4}-2-\frac{3}{4}] = +\frac{\hbar^2}{2}$

利用 $\langle r^{-3}\rangle_{21} = 1/(24a_0^3)$:

$\Delta E_{SO} = \frac{e^2\hbar^2}{8m_e^2c^2\epsilon_0}\cdot\frac{1}{24a_0^3}\times\begin{cases}-1 & j=1/2\\ +1/2 & j=3/2\end{cases}$

(c) 分裂 $\Delta E = \Delta E_{j=3/2} - \Delta E_{j=1/2} \propto \alpha^4 m_e c^2 \sim 10^{-4}$ eV 量级。对应波长约 0.1 nm 量级的精细结构分裂。
</details>

---

## Dirac 的 Legacy

### Paul Dirac 与 Cambridge

Paul Dirac (1902-1984) 是 Cambridge 培养的最伟大的物理学家之一：

1. **Dirac 方程** (1928)：相对论性量子力学，预言正电子
2. **bra-ket 记号**：整个量子力学的标准语言
3. **Dirac δ 函数**：分布论的先驱
4. **费米-狄拉克统计**：与 Enrico Fermi 独立发现
5. **磁单极子**：Dirac 弦与电荷量子化
6. **路径积分思想的先驱**

Dirac 的风格——**数学优美优先**——深刻影响了剑桥量子力学的教学传统。他的名言："It is more important to have beauty in one's equations than to have them fit experiment."

### Cavendish 的量子实验根基

- **Thomson (1897)**：电子的发现 → 自由电子的量子化
- **Rutherford (1911)**：原子核 → 有心力量子问题
- **Bragg (1913)**：X 射线衍射 → 波粒二象性的宏观证据
- **Cockcroft-Walton (1932)**：人工核反应 → $E=mc^2$
- **Cavendish 量子光学组**至今活跃：冷原子、量子信息、量子计算

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Shankar Ch 1-4 | 数学基础 + 公理 | Part IB 核心 |
| Shankar Ch 5-7 | 一维问题 | Part IB |
| Shankar Ch 7-9 | 谐振子 + 角动量 | Part IB 核心 |
| Shankar Ch 13-15 | 微扰 + 路径积分 | Part II |
| Cohen-Tannoudji Vol I Ch 1-7 | 基本框架 | Part IB 深度补充 |
| Cohen-Tannoudji Vol II Ch 9-12 | 角动量 + 自旋 + 加法 | Part II |
| Griffiths *Quantum Mechanics* Ch 1-6 | 入门 | Part IA |
| Sakurai *Modern QM* Ch 1-5 | 研究生 | Part II/III |
| Dirac *Principles of QM* | 全部 | 经典原典 |

---

**版本**：v1.0 (2026-08-12) · Cambridge Part IB/II Quantum Mechanics


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：在量子世界里，粒子不是"小球"而是"概率波"——它同时在这又在那，直到你"看"它一眼，才在某一处现身。
>
> **生活类比**：旋转中的硬币。在它转着的时候，既像正面又像反面；只有你用手按住（测量）的那一刻，它才"决定"是哪一面。量子粒子就是这样叠加着，直到被测量。
>
> **反直觉发现（啊哈时刻）**：两个粒子可以"纠缠"——测量其中一个，瞬间决定另一个的状态，无论它们相隔多远。爱因斯坦称之为"幽灵般的超距作用"（spukhafte Fernwirkung），但实验证明它真实存在，且是量子计算与量子加密的根基。

---

## 🔗 衔接：从哪来，到哪去

- **前置知识**：线性代数（本征值/本征矢、对角化）、复变函数、Part IB 数学方法、**经典哈密顿力学**（Topic 1 §4——$q,p$ → 算符的正则量子化）
- **危机（量子的诞生）**：经典物理无法解释①黑体辐射 ②光电效应 ③原子线状光谱 ④氢原子不坍缩 → 量子力学横空出世
- **新危机**：
  - 量子力学 + 狭义相对论 → **量子场论**（Topic 7 粒子物理的基石）
  - "测量问题" → 诠释之争（哥本哈根 / 多世界 / 退相干 / Bohm），至今未定
- **后续去向**：量子统计 → **凝聚态**（Topic 6）；量子场论 → **粒子物理**（Topic 7）；量子信息 → **量子计算/通信**

---

## 🏭 理论联系实际：5 个现代应用

1. **半导体晶体管**：能带论 + 隧穿，是所有芯片（手机、CPU、GPU）的根基。
2. **激光**：受激辐射产生相干态光子场（§4.3 相干态），从光驱到激光手术。
3. **量子隧穿的应用**：STM 扫描隧道显微镜（单原子成像，§3.2）、闪存、隧道二极管。
4. **MRI / 核磁共振**：核自旋量子化与塞曼效应（§6）。
5. **量子计算与量子加密**：纠缠 + 叠加 → Shor 算法（威胁 RSA）、BB84 量子密钥分发。

---

## 🔬 最新研究前沿（2024-2026）

1. **Google Willow 量子芯片**（2024-12）：105 个超导量子比特，**首次**实现表面码纠错"低于阈值"——逻辑比特错误率随编码尺寸下降，是容错量子计算的里程碑（*Nature*, 2024 年 12 月）。
2. **中性原子阵列量子计算**：2024–2025 用光镊操控上千个中性原子（Atom Computing 1180 原子、QuEra 等），实现可重构的逻辑量子比特，剑桥在该方向有深厚积累。
3. **剑桥冷原子多体模拟**：剑桥 Ulrich Schneider 等用光晶格中的超冷原子模拟多体物理——多体局域化、非厄米动力学（2024 系列实验），把量子力学变成"量子模拟器"。
4. **拓扑量子计算**：2024 微软 Majorana 拓扑量子比特路线持续推进，追求"内禀容错"的硬件。
5. **跨平台逻辑量子比特演示**：2024 离子阱（Quantinuum、IonQ）、超导、中性原子平台竞相演示纠错后的逻辑比特，进入"NISQ → 容错"过渡期。

---

## 🗺️ 学习 Roadmap（Cambridge Tripos 路径）

| 阶段 | 课程 | 你应当能做到 |
|------|------|------------|
| **Part IB** | Quantum Mechanics | 解一维势阱、谐振子（代数法）、氢原子、自旋 1/2 |
| **Part II** | Quantum Physics | 微扰论、散射、角动量加法、多电子原子初步 |
| **Part II** | Atomic & Molecular Physics | 原子结构、光谱、精细/超精细结构 |
| **Part III** | QFT / Quantum Information / Quantum Optics | 路径积分、量子信息论、腔 QED、凝聚态量子理论 |

**知识检查三问**：
1. 为什么液氦在常压下永不凝固？（零点能 §4.2——与 Demo 6 一致）
2. 为什么自旋 1/2 的电子需要"转两圈"才回到原状态？
3. 量子隧穿如何让太阳核聚变得以发生？（见 Demo 5）
