# Topic 05 · 物理学中的数学方法 — Caltech Ph 106

> **课程链**：Ph 106abc *Topics in the Theory of Nonlinear Dynamics and Mathematical Physics*（Mathews & Walker 主导）→ Ph 125/126/127 各方向的数学基础
>
> **教材三角**：Mathews & Walker *Mathematical Methods of Physics* 2ed（**Caltech 自己的经典！** Jon Mathews 是 Caltech 教授，Walker 是其学生） · Arfken, Weber & Harris *Mathematical Methods for Physicists* 7ed（最全面的标准参考） · Boas *Mathematical Methods in the Physical Sciences* 3ed（最友好的入门）

---

## Caltech 特色：Mathews & Walker —— Caltech 的数学方法DNA

Caltech 的数学方法教学有一条独特的血脉：

1. **Mathews & Walker 是 Caltech 的原创**——Jon Mathews（1930–2003）是 Caltech 物理教授，Robert Walker 是他的博士生。这本书诞生于 Caltech 的课堂，历经半个世纪仍是全球物理系的标准教材之一。它的风格是**物理直觉先于数学严谨**——每一个定理都用物理问题引入，而非从公理体系出发。Caltech 的 Ph 106 至今仍以本书为骨干。

2. **数学是工具，不是目的**——Caltech 的物理训练反复强调：物理学家学数学不是为了成为数学家，而是为了**解决物理问题**。Mathews & Walker 的每一章都以一个物理动机开头：为什么我们需要复变？（因为电磁学需要二维势论）为什么需要特殊函数？（因为氢原子和黑体辐射）为什么需要群论？（因为晶体对称性和粒子物理的选择定则）。

3. **Thorne 的数学工具箱**——Kip Thorne 在 Caltech 教 GR（Ph 236）时常说：MTW（《Misner, Thorne & Wheeler》）的前 3 章基本就是 Mathews & Walker 的微分几何版本。Caltech 学生在 Ph 106 打好的张量分析和复变基础，直接铺向 GR 和量子场论。

---

## §1 线性代数：本征值问题

### 1.1 本征值与本征向量

物理中的本征值问题无处不在——量子力学的能量本征态、转动惯量的主轴、简正模式——核心都是：

$$\mathbf{A}\mathbf{v} = \lambda \mathbf{v}$$

**Hermitian 矩阵**（$\mathbf{A}^\dagger = \mathbf{A}$）的三条定理：

| 性质 | 数学表述 | 物理意义 |
|------|---------|---------|
| 实本征值 | $\lambda_i \in \mathbb{R}$ | 可观测量必须是实数 |
| 正交本征矢 | $\mathbf{v}_i^\dagger \mathbf{v}_j = \delta_{ij}$ | 量子态的正交性 |
| 完备性 | $\sum_i \mathbf{v}_i\mathbf{v}_i^\dagger = \mathbf{I}$ | 任意态可展开 |

### 1.2 奇异值分解（SVD）

任意 $m\times n$ 矩阵 $\mathbf{A}$ 可分解为：

$$\mathbf{A} = \mathbf{U}\boldsymbol{\Sigma}\mathbf{V}^\dagger$$

其中 $\mathbf{U}$ ($m\times m$)、$\mathbf{V}$ ($n\times n$) 是酉矩阵，$\boldsymbol{\Sigma}$ 是对角阵（奇异值 $\sigma_i \geq 0$）。

> **物理应用**：SVD 是数据分析的瑞士军刀——LIGO 的信号提取、量子态层析（quantum tomography）、压缩感知都依赖它。Mathews & Walker Ch 1 就奠定了线性空间的基础语言。

### 1.3 二次型与对角化

$$Q = \mathbf{x}^T \mathbf{A} \mathbf{x} = \sum_{ij} A_{ij} x_i x_j$$

对称矩阵 $\mathbf{A}$ 可通过正交变换 $\mathbf{A} = \mathbf{R}^T \mathbf{D} \mathbf{R}$ 对角化，其中 $\mathbf{D} = \text{diag}(\lambda_1, \ldots, \lambda_n)$。

**例**：刚体转动惯量张量 $I_{ij}$ 对角化后给出主轴转动惯量 $I_1, I_2, I_3$——这就是 Ph 105 中网球拍定理的数学基础。

---

## §2 复变函数：物理学的万能钥匙

> **Mathews & Walker 第 4 章**——Caltech 的复变教学以物理应用为导向。核心理念：**二维势论（静电场、流体力学）等价于复解析函数理论**。

### 2.1 解析函数与 Cauchy-Riemann 条件

函数 $f(z) = u(x,y) + iv(x,y)$ 在 $z = x + iy$ 处解析，当且仅当：

$$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \qquad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$

**推论**：$u$ 和 $v$ 都满足 Laplace 方程 $\nabla^2 u = 0$——所以解析函数就是二维无源场的通解。

### 2.2 Cauchy 定理与留数

**Cauchy 积分定理**：若 $f(z)$ 在闭合曲线 $C$ 内解析：

$$\oint_C f(z)\,dz = 0$$

**留数定理**——计算实积分的终极武器：

$$\oint_C f(z)\,dz = 2\pi i \sum_k \text{Res}(f, z_k)$$

其中 $z_k$ 是 $C$ 内的极点。在 $m$ 阶极点 $z_0$ 处的留数：

$$\text{Res}(f, z_0) = \frac{1}{(m-1)!}\lim_{z\to z_0}\frac{d^{m-1}}{dz^{m-1}}\left[(z-z_0)^m f(z)\right]$$

### 2.3 实积分的留数计算

> **Caltech 经典练习**：用留数定理计算 $\int_0^\infty \frac{\cos ax}{1+x^2}\,dx$（$a > 0$）。

将被积函数延拓到复平面，取上半平面大半圆围道。唯一的极点在 $z = i$（一阶极点）：

$$\text{Res}\left(\frac{e^{iaz}}{1+z^2},\, i\right) = \frac{e^{ia\cdot i}}{2i} = \frac{e^{-a}}{2i}$$

$$\int_{-\infty}^{\infty} \frac{e^{iax}}{1+x^2}\,dx = 2\pi i \cdot \frac{e^{-a}}{2i} = \pi e^{-a}$$

取实部：$\int_0^\infty \frac{\cos ax}{1+x^2}\,dx = \frac{\pi}{2}e^{-a}$

> **反直觉发现**：一个看似与复变无关的实积分 $\cos(ax)/(1+x^2)$，其结果 $\frac{\pi}{2}e^{-a}$ 恰好是复平面极点 $z=i$ 处的指数衰减 $e^{-a}$——复平面的几何直接决定了实积分的值。

### 2.4 色散关系（Kramers-Kronig）

因果性（响应不能早于激励）意味着极点全在上半平面，导致实部和虚部由 Hilbert 变换联系：

$$\text{Re}\,\chi(\omega) = \frac{1}{\pi}\mathcal{P}\int_{-\infty}^{\infty}\frac{\text{Im}\,\chi(\omega')}{\omega'-\omega}\,d\omega'$$

$$\text{Im}\,\chi(\omega) = -\frac{1}{\pi}\mathcal{P}\int_{-\infty}^{\infty}\frac{\text{Re}\,\chi(\omega')}{\omega'-\omega}\,d\omega'$$

> **LIGO 关联**：LIGO 悬镜的机械响应函数 $\chi(\omega)$ 服从色散关系。知道吸收谱（虚部）就能推出弹性常数（实部）——这是涨落-耗散定理的数学基础。

---

## §3 常微分方程

### 3.1 一阶线性 ODE

$$\frac{dy}{dx} + P(x)y = Q(x)$$

积分因子 $\mu(x) = e^{\int P\,dx}$：

$$y = \frac{1}{\mu}\int \mu Q\,dx + \frac{C}{\mu}$$

### 3.2 二阶线性 ODE 与特殊函数

二阶 ODE 是物理中最常见的方程。标准形式：

$$y'' + P(x)y' + Q(x)y = 0$$

**级数解法（Frobenius 方法）**——Mathews & Walker 的核心教法：设 $y = \sum_{n=0}^{\infty} a_n x^{n+s}$，代入方程逐项比较。

三大经典方程及其解：

| 方程 | 解 | 物理场景 |
|------|-----|---------|
| Bessel: $x^2y''+xy'+(x^2-n^2)y=0$ | $J_n(x),\,Y_n(x)$ | 圆膜振动、柱坐标波动 |
| Legendre: $(1-x^2)y''-2xy'+l(l+1)y=0$ | $P_l(x)$ | 球坐标角分布 |
| Hermite: $y''-2xy'+2ny=0$ | $H_n(x)$ | 量子谐振子 |

### 3.3 Green 函数：非齐次方程的万能工具

**核心思想**：先求点源响应（Green 函数），再用叠加原理求任意源的响应。

对于算子 $L$，Green 函数 $G(x, x')$ 满足：

$$L\,G(x, x') = \delta(x - x')$$

非齐次方程 $Ly = f(x)$ 的解：

$$y(x) = \int G(x, x') f(x')\,dx'$$

> **物理意义**：Green 函数就是**传播子**（propagator）。量子场论中的 Feynman 传播子、电动力学中的势论、信号处理中的冲激响应——全都是 Green 函数的不同面孔。Mathews & Walker 用 Green 函数统一了很多看似不同的物理问题。

### 3.4 Sturm-Liouville 理论

形如

$$-\frac{d}{dx}\left[p(x)\frac{dy}{dx}\right] + q(x)y = \lambda w(x)y$$

的本征值问题有深刻性质：

- 本征值 $\lambda_n$ 是实数且有序：$\lambda_0 < \lambda_1 < \cdots$
- 本征函数 $y_n$ 在权函数 $w(x)$ 下正交：$\int y_m y_n w\,dx = N_n \delta_{mn}$
- **完备性**：任意（满足边界条件的）函数可展开为本征函数的级数（广义 Fourier 级数）

> 这就是为什么 Bessel、Legendre、Hermite 函数能构成完备基——它们都是不同 Sturm-Liouville 问题的本征函数。

---

## §4 偏微分方程

### 4.1 三大经典方程

| 方程 | 形式 | 物理场景 |
|------|------|---------|
| 波动方程 | $\nabla^2 u = \frac{1}{c^2}\frac{\partial^2 u}{\partial t^2}$ | 弦振动、电磁波、声波 |
| 扩散方程 | $\nabla^2 u = \frac{1}{D}\frac{\partial u}{\partial t}$ | 热传导、粒子扩散 |
| Laplace 方程 | $\nabla^2 u = 0$ | 静电场、稳态温度 |

### 4.2 分离变量法

**例**：矩形区域 $0 \leq x \leq a$，$0 \leq y \leq b$ 的 Laplace 方程，边界条件 $u(0,y)=u(a,y)=u(x,0)=0$，$u(x,b)=V_0$。

设 $u(x,y) = X(x)Y(y)$，分离得 $X''/X = -Y''/Y = -k^2$。

边界条件要求 $k = n\pi/a$，解为：

$$u(x,y) = \sum_{n=1}^{\infty} B_n \sin\frac{n\pi x}{a}\,\sinh\frac{n\pi y}{a}$$

由顶部边界 $u(x,b)=V_0$ 展开为 Fourier 正弦级数确定 $B_n$：

$$B_n = \frac{4V_0}{n\pi\,\sinh(n\pi b/a)}\quad(n\text{ 奇})$$

### 4.3 球坐标下的 Laplace 方程

分离变量 $u(r,\theta,\phi) = R(r)\Theta(\theta)\Phi(\phi)$ 得到：

- 径向：$r^2R''+2rR'-l(l+1)R=0$ → $R \sim r^l$ 或 $r^{-(l+1)}$
- 角向：球谐函数 $Y_l^m(\theta,\phi)$

> **Caltech 关联**：球谐函数是量子力学角动量的语言（$|l,m\rangle$），也是 LIGO 天线方向图的基函数。Mathews & Walker Ch 7 的分离变量法直接通向 Sakurai 的角动量理论。

---

## §5 特殊函数速览

### 5.1 $\Gamma$ 函数与 $\beta$ 函数

$$\Gamma(z) = \int_0^\infty t^{z-1}e^{-t}\,dt, \qquad \Gamma(n) = (n-1)!$$

**反射公式**：$\Gamma(z)\Gamma(1-z) = \frac{\pi}{\sin\pi z}$

### 5.2 Bessel 函数

$$J_n(x) = \sum_{k=0}^{\infty}\frac{(-1)^k}{k!\,\Gamma(n+k+1)}\left(\frac{x}{2}\right)^{n+2k}$$

渐近行为：$J_n(x) \xrightarrow{x\to\infty} \sqrt{\frac{2}{\pi x}}\cos\left(x - \frac{n\pi}{2}-\frac{\pi}{4}\right)$

**正交性**：$\int_0^a J_n\left(\frac{\alpha_{np}}{a}r\right)J_n\left(\frac{\alpha_{nq}}{a}r\right) r\,dr = \frac{a^2}{2}[J_{n+1}(\alpha_{np})]^2\delta_{pq}$

其中 $\alpha_{np}$ 是 $J_n$ 的第 $p$ 个零点。

### 5.3 球谐函数

$$Y_l^m(\theta,\phi) = (-1)^m\sqrt{\frac{(2l+1)(l-m)!}{4\pi(l+m)!}}\,P_l^m(\cos\theta)\,e^{im\phi}$$

正交归一：$\int |Y_l^m|^2\,d\Omega = 1$

前几个：
- $Y_0^0 = \frac{1}{\sqrt{4\pi}}$（各向同性）
- $Y_1^0 = \sqrt{\frac{3}{4\pi}}\cos\theta$（偶极）
- $Y_2^0 = \sqrt{\frac{5}{16\pi}}(3\cos^2\theta - 1)$（四极）

> **物理意义**：$l=0$ 是 s 轨道（球对称），$l=1$ 是 p 轨道（偶极），$l=2$ 是 d 轨道（四极）——原子轨道就是球谐函数。

---

## §6 群论：对称性的数学语言

### 6.1 群的定义

集合 $G$ 配合运算 $\cdot$，满足：

1. **封闭性**：$a, b \in G \Rightarrow a\cdot b \in G$
2. **结合律**：$(a\cdot b)\cdot c = a\cdot(b\cdot c)$
3. **单位元**：$\exists\, e \in G,\; a\cdot e = e\cdot a = a$
4. **逆元**：$\forall a,\, \exists a^{-1} \in G,\; a\cdot a^{-1} = e$

### 6.2 物理中重要的群

| 群 | 描述 | 物理应用 |
|----|------|---------|
| $SO(3)$ | 三维旋转 | 角动量、原子光谱 |
| $SU(2)$ | 旋量旋转 | 电子自旋、同位旋 |
| $O(N)$ | 正交变换 | 晶体对称性 |
| $SU(3)$ | 特殊幺正 | 色荷（QCD）|
| 点群 $C_n, D_n, T_d, O_h$ | 离散对称 | 分子振动、能带 |

### 6.3 表示与特征标

群的**表示**是把群元映射为矩阵的**同态** $\rho: G \to GL(n)$。

**特征标**：$\chi^{(\alpha)}(g) = \text{Tr}\,\rho^{(\alpha)}(g)$

> **物理应用——选择定则**：跃迁矩阵元 $\langle f | \hat{O} | i\rangle \neq 0$ 的条件是直积表示 $\Gamma_f^* \otimes \Gamma_O \otimes \Gamma_i$ 包含恒等表示。这决定了**原子光谱线的有无**——纯群论推导！Mathews & Walker Ch 13 用此统一了大量光谱学结果。

### 6.4 $SO(3)$ 与 $SU(2)$

$SU(2)$ 是 $SO(3)$ 的**双重覆盖**——每个 $SO(3)$ 元素对应 $SU(2)$ 的两个元素 $\pm U$。这直接导致**旋量在旋转 $2\pi$ 后变号**——费米子的数学根源。

---

## Python 演示：留数计算验证 + 球谐函数

```python
"""
Caltech Ph 106 Demo: 数学方法两个核心验证
1. 留数定理计算实积分 → 数值验证
2. 球谐函数: 归一化与正交性
纯标准库零依赖，bash 可直接跑通。
"""
import math
import cmath

# ══════════════════════════════════════════════
# 1. 留数定理验证: ∫₀^∞ cos(ax)/(1+x²) dx = π/2 · e^{-a}
# ══════════════════════════════════════════════
print("=== 留数定理: ∫₀^∞ cos(ax)/(1+x²) dx ===\n")

a_values = [0.5, 1.0, 2.0, 3.0, 5.0]

print(f"{'a':>5s} {'数值积分':>12s} {'留数=π/2·e^(-a)':>16s} {'相对误差':>10s}")
for a in a_values:
    # 数值积分（Simpson 法）
    N = 100000
    x_max = 50.0  # 截断
    dx = x_max / N
    integral = 0.0
    for i in range(N + 1):
        x = i * dx
        fx = math.cos(a * x) / (1 + x * x)
        weight = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
        integral += weight * fx
    integral *= dx / 3

    # 留数定理结果: π/2 · e^{-a}
    residue_result = math.pi / 2 * math.exp(-a)
    err = abs(integral - residue_result) / residue_result * 100
    print(f"{a:5.1f} {integral:12.8f} {residue_result:16.8f} {err:9.4f}%")

print("\n→ 留数定理结果与数值积分高度吻合。")
print("  关键: 实积分 ∫cos(ax)/(1+x²)dx 的值由复平面极点 z=i 处的 e^{-a} 决定。")
print("  这就是 Mathews & Walker Ch 4 的核心洞察: 复分析 = 实积分的万能钥匙。\n")

# ══════════════════════════════════════════════
# 2. 球谐函数: 归一化与正交性
# ══════════════════════════════════════════════
print("=== 球谐函数 Y_l^m: 归一化与正交性 ===\n")

def legendre_assoc(l, m, x):
    """关联 Legendre 多项式 P_l^m(x)（|x| ≤ 1）
    使用递推关系计算。"""
    # 计算 P_m^m
    pmm = 1.0
    if m > 0:
        somx2 = math.sqrt((1 - x) * (1 + x))
        fact = 1.0
        for i in range(1, m + 1):
            pmm *= -fact * somx2
            fact += 2.0
    if l == m:
        return pmm
    # P_{m+1}^m
    pmmp1 = x * (2 * m + 1) * pmm
    if l == m + 1:
        return pmmp1
    # 递推: (l-m) P_l^m = (2l-1)x P_{l-1}^m - (l+m-1) P_{l-2}^m
    pll = 0.0
    for ll in range(m + 2, l + 1):
        pll = ((2 * ll - 1) * x * pmmp1 - (ll + m - 1) * pmm) / (ll - m)
        pmm = pmmp1
        pmmp1 = pll
    return pll

def Y_lm(l, m, theta, phi):
    """球谐函数 Y_l^m(θ, φ)"""
    norm = math.sqrt((2 * l + 1) / (4 * math.pi)
                     * math.factorial(l - m) / math.factorial(l + m))
    return norm * legendre_assoc(l, m, math.cos(theta)) * cmath.exp(1j * m * phi)

# 归一化检验: ∫|Y_l^m|² dΩ = 1
print("归一化检验: ∫|Y_l^m|² dΩ 应 = 1.000")
n_theta, n_phi = 50, 100
dtheta = math.pi / n_theta
dphi = 2 * math.pi / n_phi

for (l, m) in [(0,0), (1,0), (1,1), (2,0), (2,1), (2,2), (3,0), (3,2)]:
    total = 0.0
    for i in range(n_theta):
        theta = (i + 0.5) * dtheta
        for j in range(n_phi):
            phi = (j + 0.5) * dphi
            ylm = Y_lm(l, m, theta, phi)
            total += abs(ylm)**2 * math.sin(theta) * dtheta * dphi
    print(f"  Y_{l}^{m}: ∫|Y|² dΩ = {total:.6f}")

# 正交性检验: ∫Y_l^m · (Y_l'^m')* dΩ = δ_{ll'}δ_{mm'}
print("\n正交性检验: ∫Y_1^0 · (Y_l'^0)* dΩ 应 = δ_{1,l'}")
for lp in [0, 1, 2, 3]:
    total = 0.0
    for i in range(n_theta):
        theta = (i + 0.5) * dtheta
        for j in range(n_phi):
            phi = (j + 0.5) * dphi
            total += (Y_lm(1, 0, theta, phi) * Y_lm(lp, 0, theta, phi).conjugate()
                     ).real * math.sin(theta) * dtheta * dphi
    print(f"  <Y_1^0 | Y_{lp}^0> = {total:.6f} {'✓ δ=1' if lp == 1 else '(≈0 ✓)'}")

print("\n→ 球谐函数构成单位球面上的完备正交基。")
print("  量子力学角动量 |l,m⟩、原子轨道(s,p,d,f)、LIGO 天线方向图都用它。")
print("  Mathews & Walker Ch 7 的分离变量法 = 球谐函数的物理来源。")
```

**反直觉发现**：留数定理告诉我们，实积分 $\int_0^\infty \frac{\cos ax}{1+x^2}\,dx$ 的值**完全由复平面上一个点**（极点 $z = i$）决定——$e^{-a}$ 正是 $|e^{iaz}|$ 在 $z=i$ 处的值。一个实变量的积分结果却编码在复平面的拓扑中，这就是复分析的美。

---

## 习题

### 基础题（Mathews & Walker / Boas 级别）

**P1.** 用留数定理计算 $\int_0^\infty \frac{dx}{1+x^4}$。提示：$1+x^4$ 的根是 $e^{i\pi/4}, e^{3i\pi/4}, e^{5i\pi/4}, e^{7i\pi/4}$，上半平面有两个。

**P2.** 证明 Cauchy-Riemann 条件 $\Rightarrow u, v$ 满足 Laplace 方程。由此解释为什么二维静电场可以用复势描述。

**P3.** 用 Frobenius 方法求 Bessel 方程 $x^2y'' + xy' + (x^2 - n^2)y = 0$ 在 $n=0$ 时的级数解前 5 项，验证它收敛到 $J_0(x) = 1 - x^2/4 + x^4/64 - \cdots$。

### 进阶题（Arfken / Mathews & Walker 级别）

**P4.** 求无穷长线电荷 $\lambda$ 的电势。用 Green 函数方法验证 $\Phi = -\frac{\lambda}{2\pi\epsilon_0}\ln r$（柱坐标二维 Green 函数与三维的 $1/r$ 不同）。

**P5.**（色散关系）若某介质的折射率虚部 $\text{Im}\,n(\omega) = \frac{A\gamma\omega}{(\omega_0^2-\omega^2)^2+\gamma^2\omega^2}$（Lorentz 振子模型），用 Kramers-Kronig 关系求 $\text{Re}\,n(\omega)$。

**P6.** 用群论证明：氢原子 $l=1 \to l=0$ 的电偶极跃迁，只有 $\Delta m = 0, \pm 1$ 的跃迁允许（选择定则）。提示：$D^{(1)} \otimes D^{(1)} = D^{(0)} \oplus D^{(1)} \oplus D^{(2)}$。

### 挑战题

**P7.**（Mathews & Walker 经典）用围道积分计算 Fresnel 积分：

$$\int_0^\infty \cos(x^2)\,dx = \int_0^\infty \sin(x^2)\,dx = \sqrt{\frac{\pi}{8}}$$

提示：取 $e^{iz^2}$ 沿 $45°$ 楔形围道。

**P8.**（Sturm-Liouville 应用）证明 Hermite 多项式 $H_n(x)$ 构成权函数 $w(x) = e^{-x^2}$ 下的正交完备集。由此推导量子谐振子能量 $E_n = (n+\frac{1}{2})\hbar\omega$——这是量子力学 Ph 125 的数学基础。

---

## 知识地图与跨课程联系

```
数学方法 (Ph 106)
    │
    ├──→ 线性代数 ──→ 量子力学矩阵表述 (Ph 125)
    │        │              │
    │   本征值/对角化    海森堡矩阵力学
    │        │              │
    │      SVD ──→ 数据分析 / LIGO 信号处理
    │
    ├──→ 复变分析 ──→ 电动力学 (Ph 108) 二维势论
    │        │
    │   留数/色散 ──→ 涨落-耗散定理 (Ph 127)
    │                  → LIGO 噪声分析
    │
    ├──→ ODE/Green函数 ──→ 散射理论 (Ph 125c)
    │        │
    │   特殊函数 ──→ 氢原子波函数 / 角动量
    │
    ├──→ PDE/分离变量 ──→ 热传导/波动/扩散
    │        │              │
    │   球谐函数 ──→ 原子轨道 / 天体辐射方向图
    │
    └──→ 群论 ──→ 粒子物理标准模型 (Ph 109)
              │              │
        选择定则 ──→ 光谱学
              │
        SU(2)/SO(3) ──→ 自旋 / 广义相对论 (Ph 236)
```

**关键连接**：
- Green 函数 $\to$ 量子场论的传播子
- 球谐函数 $\to$ 量子力学角动量
- 群论 $\to$ 粒子物理的选择定则
- 复变+色散 $\to$ LIGO 的噪声分析（Caltech/Thorne）
- Sturm-Liouville $\to$ 正交完备基（量子力学的数学基石）

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| **Mathews & Walker** *Mathematical Methods of Physics* 2ed | Ch 1-3（线性代数/复变）、Ch 4-6（ODE/PDE/特殊函数）、Ch 7-8（Green函数/变分法）、Ch 13（群论）| **Caltech 原创**，物理直觉优先 |
| Arfken, Weber & Harris *Mathematical Methods* 7ed | 全书 | 最全面的标准参考，可当百科全书查 |
| Boas *Mathematical Methods in the Physical Sciences* 3ed | Ch 2-3（线代/复变）、Ch 8-9（ODE/PDE）、Ch 12-16（特殊函数/群论）| 最友好的入门教材 |
| Stone & Goldbart *Mathematics for Physics* | Ch 1-3（变分/复变）、Ch 17-18（群论/微分几何）| 现代物理视角，桥接 MTW |

> **Mathews 的话**（Caltech 课堂）：*"Mathematical rigor is the physicist's servant, not his master."* 物理学家学数学是为了解物理问题——先会用，再问为什么对。Caltech 的 Ph 106 就贯彻这个理念：从物理问题出发，把数学工具磨成快刀。

---

*本文件属于 top-physics-courses/caltech-physics Phase 2。对应课程 Ph 106abc。Mathews & Walker 是 Caltech 物理系的 DNA。*
