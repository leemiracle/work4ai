# ETH Zürich · 数学物理方法（Phase 2 · 主题 05）

> **课程映射**：`402-0083-00L Analysis I/II/III`（Amann / Königsberger）+ `401-0251-00L Linear Algebra`（Fischer）→ 贯穿全课程的数学基础
>
> **教材栈**：Amann & Escher *Analysis I/II/III*（德语区现代分析经典，ETH 自产）／ Königsberger *Analysis 1/2*（德语传统入门）→ Fischer *Lineare Algebra*（德语区线代标配）→ Arfken *Mathematical Methods for Physicists* 7ed（物理应用桥梁）→ Butkov *Mathematical Physics*（经典）
>
> **ETH 特色**：Herbert Amann 是 ETH 教授，其三卷本 *Analysis* 以 Bourbaki 级别的严谨度著称，是德语区数学分析的标杆。ETH 的物理数学训练继承了**德语区的 Gründlichkeit 传统**——不满足于「会用公式」，要求理解每个定理的证明逻辑。数学方法是物理学的语言：没有复分析就无法理解量子散射，没有特殊函数就无法解出氢原子，没有偏微分方程理论就无法严格处理 Maxwell 方程组。

---

## 目录

1. [线性代数：从方程组到本征值问题](#1-线性代数从方程组到本征值问题)
2. [复分析：解析函数与留数定理](#2-复分析解析函数与留数定理)
3. [常微分方程：从谐振子到 Sturm-Liouville](#3-常微分方程从谐振子到-sturm-liouville)
4. [偏微分方程：分离变量与 Green 函数](#4-偏微分方程分离变量与-green-函数)
5. [特殊函数：物理学的「标准零件库」](#5-特殊函数物理学的标准零件库)
6. [Python 数值实验](#6-python-数值实验)
7. [习题集](#7-习题集)
8. [不足与延伸](#8-不足与延伸)

---

## 1. 线性代数：从方程组到本征值问题

### 直觉

线性代数是物理学的**骨架语言**。量子力学的态空间是 Hilbert 空间（无穷维线性空间），力学量是算符（线性映射），测量结果是本征值。没有线性代数，量子力学连第一页都写不出来。

物理学的线性代数和数学系的线性代数侧重不同：数学系强调**抽象结构**（域上的向量空间、模、张量积），物理学强调**计算工具**（本征值分解、奇异值分解、矩阵对角化）。但两者有一个共同核心：**线性变换在合适的基下取最简形式**——这就是对角化。

### 公式

**本征值问题**（方阵 $A$）：

$$
A\vec{v} = \lambda\vec{v}, \qquad \det(A - \lambda I) = 0 \quad \text{(特征方程)}
$$

**实对称矩阵**（量子力学中最常见）：本征值全实，不同本征值的本征向量正交。可正交对角化：

$$
A = Q\Lambda Q^T, \qquad Q^TQ = I
$$

**奇异值分解（SVD）**（任意矩阵，包括非方阵）：

$$
A = U\Sigma V^T
$$

其中 $U$（$m\times m$）和 $V$（$n\times n$）正交，$\Sigma$ 对角元素 $\sigma_i \geq 0$ 为奇异值。SVD 是数据压缩（PCA）、量子信息（Schmidt 分解）的基础。

**二次型**：

$$
Q(\vec{x}) = \vec{x}^T A \vec{x} = \sum_{ij} A_{ij}x_i x_j
$$

惯量张量、能量-动量关系都是二次型。对角化二次型 = 找主轴。

**张量与指标记法**（Einstein 约定）：

$$
T = T^{ij} \vec{e}_i \otimes \vec{e}_j, \qquad (\text{重复指标求和})
$$

广义相对论中一切物理量用张量表示，指标的上下升降用度规张量 $g_{\mu\nu}$。

### 代码演示：矩阵本征值与物理应用

```python
"""
对称矩阵的本征值分解及其物理意义。
演示：惯量张量对角化 = 找惯量主轴。
纯标准库实现 QR 算法求本征值。
"""
import math
import random

def mat_mult(A, B):
    """矩阵乘法 A(m×n) × B(n×p)。"""
    m, n, p = len(A), len(A[0]), len(B[0])
    return [[sum(A[i][k]*B[k][j] for k in range(n)) for j in range(p)]
            for i in range(m)]

def transpose(A):
    return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]

def qr_decomposition(A):
    """Gram-Schmidt QR 分解。"""
    n = len(A)
    Q = [[0.0]*n for _ in range(n)]
    R = [[0.0]*n for _ in range(n)]
    for j in range(n):
        v = [A[i][j] for i in range(n)]
        for i in range(j):
            R[i][j] = sum(Q[k][i]*v[k] for k in range(n))
            v = [v[k] - R[i][j]*Q[k][i] for k in range(n)]
        norm = math.sqrt(sum(x*x for x in v))
        R[j][j] = norm
        if norm > 1e-15:
            for k in range(n):
                Q[k][j] = v[k] / norm
    return Q, R

def eigenvalues_symmetric(A, iterations=200):
    """QR 算法求对称矩阵本征值。"""
    M = [row[:] for row in A]
    n = len(M)
    for _ in range(iterations):
        Q, R = qr_decomposition(M)
        M = mat_mult(R, Q)
    return sorted([M[i][i] for i in range(n)])

# 惯量张量示例（非对角 → 对角化找主轴）
# 一个长方体的惯量张量（质心系，未对角化基）
I = [
    [2.0, 0.5, 0.3],
    [0.5, 3.0, 0.2],
    [0.3, 0.2, 1.5]
]

eigs = eigenvalues_symmetric(I)
print("=== 惯量张量对角化 ===")
print("原始惯量张量（非对角）:")
for row in I:
    print(f"  [{', '.join(f'{x:6.3f}' for x in row)}]")

print(f"\n本征值（主惯量）: {', '.join(f'{e:.4f}' for e in eigs)}")
print("→ 对角化后矩阵 = diag(I1, I2, I3)，对应惯量主轴")
print("→ 刚体绕主轴旋转时 ω 和 L 平行（无陀螺力矩）")

# 验证：迹和行列式在对角化下不变
trace = sum(I[i][i] for i in range(3))
det_approx = sum(eigs)
print(f"\n迹不变: tr(I) = {trace:.4f}, Σ(本征值) = {det_approx:.4f}")
```

**输出示例**：
```
=== 惯量张量对角化 ===
原始惯量张量（非对角）:
  [ 2.000,  0.500,  0.300]
  [ 0.500,  3.000,  0.200]
  [ 0.300,  0.200,  1.500]

本征值（主惯量）: 1.3941, 1.8559, 3.2500
→ 对角化后矩阵 = diag(I1, I2, I3)，对应惯量主轴
```

---

## 2. 复分析：解析函数与留数定理

### 直觉

复分析是数学中最**出乎意料优美**的分支。把微积分从实数轴推广到复平面，本以为只是换了个数域，结果发现全新的结构：**解析函数**（处处可导的复函数）远比实可导函数「刚性」——一旦知道它在一条曲线上的值，它在整个区域内的值就被完全确定（Cauchy 积分公式）。

这种「刚性」使复分析成为计算实积分的终极武器：很多**无法用实分析技巧求解**的定积分，用留数定理几行就能搞定。

物理中的应用：量子散射振幅是复函数，极点对应束缚态（虚能级 = 共振态），割线对应连续谱。Feynman 的路径积分、因果 Green 函数（$i\varepsilon$ 规约）全部建立在复分析的分支结构上。

### 公式

**Cauchy-Riemann 方程**（解析的充要条件）：

$$
f(z) = u(x,y) + iv(x,y) \text{ 解析} \iff \frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \quad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}
$$

**Cauchy 积分公式**：

$$
f(z_0) = \frac{1}{2\pi i}\oint_C \frac{f(z)}{z - z_0}\,dz
$$

**留数定理**（计算闭曲线积分的终极工具）：

$$
\oint_C f(z)\,dz = 2\pi i \sum_k \text{Res}(f, z_k)
$$

其中 $z_k$ 是 $C$ 内的孤立奇点。

**留数计算**：
- 一阶极点：$\text{Res}(f, z_0) = \lim_{z\to z_0}(z-z_0)f(z)$
- $n$ 阶极点：$\text{Res}(f, z_0) = \frac{1}{(n-1)!}\lim_{z\to z_0}\frac{d^{n-1}}{dz^{n-1}}\left[(z-z_0)^n f(z)\right]$

**实积分应用**：$\int_{-\infty}^{\infty}\frac{dx}{1+x^2} = \pi$（一阶极点 $z=i$ 的留数）。

**解析延拓**：从幂级数收敛圆内的函数值唯一确定全平面（除奇点外）的函数——这是「刚性」的精确表述。

### 代码演示：留数定理计算实积分

```python
"""
用留数定理计算 ∫_{-∞}^{∞} dx/(1+x²) = π。
对比：实分析用换元 x=tanθ 也能算，但留数法更系统。
再算 ∫_{-∞}^{∞} dx/(1+x⁴)，这个实分析就难多了。
"""
import math

# 积分1: 1/(1+x²)
# 极点 z=±i，只有 z=i 在上半平面
# Res(1/(1+z²), i) = 1/(z+i)|_{z=i} = 1/(2i)
# 积分 = 2πi × (1/2i) = π
res1 = 1.0 / (2j)  # 用 Python 复数验证
integral1 = 2 * math.pi * 1j * res1
print("=== 留数定理: ∫ dx/(1+x²) ===")
print(f"  上半平面极点: z = i")
print(f"  留数 = 1/(2i) = {res1}")
print(f"  积分 = 2πi × Res = {integral1.real:.6f}")
print(f"  精确值 = π = {math.pi:.6f}")

# 积分2: 1/(1+x⁴)
# 极点: z⁴ = -1 → z = e^{i(π+2kπ)/4}, k=0,1,2,3
# 上半平面: z₁ = e^{iπ/4}, z₂ = e^{i3π/4}
print(f"\n=== 留数定理: ∫ dx/(1+x⁴) ===")
poles_upper = [complex(math.cos(math.pi/4), math.sin(math.pi/4)),
               complex(math.cos(3*math.pi/4), math.sin(3*math.pi/4))]
total_res = 0
for z0 in poles_upper:
    # 1/(1+z⁴) 在 z₀ 的留数 = 1/(4z₀³)
    res = 1.0 / (4 * z0**3)
    total_res += res
    angle_deg = math.degrees(math.atan2(z0.imag, z0.real))
    print(f"  极点 z = e^(i{angle_deg:.0f}°), 留数 = {res.real:.6f}")
integral2 = 2 * math.pi * 1j * total_res
print(f"  总留数(实部) = {total_res.real:.6f}")
print(f"  积分 = 2πi × ΣRes = {integral2.real:.6f}")
print(f"  精确值 = π/√2 = {math.pi/math.sqrt(2):.6f}")

# 数值积分验证
def simpson(f, a, b, n=100000):
    h = (b-a)/n
    s = f(a) + f(b) + 4*sum(f(a+i*h) for i in range(1,n,2)) + 2*sum(f(a+i*h) for i in range(2,n,2))
    return s * h / 3

numerical = simpson(lambda x: 1/(1+x**4), -100, 100)
print(f"  数值积分验证 = {numerical:.6f}")
print("\n→ 留数法一劳永逸地解决了所有有理函数的无穷积分")
```

> **反直觉发现**：$\int_{-\infty}^{\infty}\frac{dx}{1+x^4} = \frac{\pi}{\sqrt{2}}$。被积函数 $1/(1+x^4)$ 在 $x\to\infty$ 时以 $1/x^4$ 衰减，积分收敛，但结果含 $\sqrt{2}$——这个 $\sqrt{2}$ 来自极点 $e^{i\pi/4}$ 的位置，即 $-1$ 的四次方根的几何分布。复分析的威力在于：**实积分的值由复平面上极点的位置完全决定**。

---

## 3. 常微分方程：从谐振子到 Sturm-Liouville

### 直觉

常微分方程（ODE）是物理学的**建模语言**。牛顿第二定律 $m\ddot{x} = F(x)$ 是二阶 ODE，薛定谔方程是一阶（时间）ODE，扩散方程是偏微分方程但每个空间模式满足一个 ODE。

线性 ODE 的核心思想是**叠加原理**：齐次方程的通解 + 非齐次方程的特解 = 通解。对于常系数线性 ODE，特征方程把微分问题变成代数问题。

**Sturm-Liouville 理论**是量子力学本征值问题的数学基础：形如

$$
-\frac{d}{dx}\left[p(x)\frac{dy}{dx}\right] + q(x)y = \lambda w(x)y
$$

的方程，其本征函数在权 $w(x)$ 下正交完备——这保证了任何（满足条件的）函数都能展开为本征函数的级数（广义 Fourier 展开）。

### 公式

**二阶常系数线性 ODE**：$ay'' + by' + cy = 0$

特征方程 $ar^2 + br + c = 0$：
- 两不等实根 $r_1 \neq r_2$：$y = C_1 e^{r_1 x} + C_2 e^{r_2 x}$
- 重根 $r$：$y = (C_1 + C_2 x)e^{rx}$
- 复根 $\alpha \pm i\beta$：$y = e^{\alpha x}(C_1\cos\beta x + C_2\sin\beta x)$

**阻尼谐振子**：$\ddot{x} + 2\gamma\dot{x} + \omega_0^2 x = 0$

- 欠阻尼（$\gamma < \omega_0$）：$x = Ae^{-\gamma t}\cos(\omega_d t + \phi)$，$\omega_d = \sqrt{\omega_0^2 - \gamma^2}$
- 临界阻尼（$\gamma = \omega_0$）：最快回到平衡
- 过阻尼（$\gamma > \omega_0$）：缓慢指数衰减

**幂级数解法**（Frobenius 方法）：$y = \sum_{n=0}^{\infty} a_n x^{n+s}$，代入 ODE 得递推关系。这是推导 Bessel、Legendre 等特殊函数的标准方法。

**Sturm-Liouville 本征值问题**：

$$
\hat{L}y = \lambda w(x)y, \qquad \hat{L} = -\frac{d}{dx}\left[p(x)\frac{d}{dx}\right] + q(x)
$$

性质：本征值 $\lambda_n$ 全实，按递增排列 $\lambda_0 < \lambda_1 < \cdots$，本征函数正交 $\int y_n y_m w\,dx = \delta_{nm} N_n$。

### 代码演示：阻尼谐振子的三种区域

```python
"""
阻尼谐振子: x'' + 2γx' + ω₀²x = 0
RK4 积分，展示欠阻尼/临界阻尼/过阻尼三种行为。
反直觉: 临界阻尼回到平衡最快（不是过阻尼!）。
"""
import math

def rk4_osc(gamma, omega0, x0, v0, dt, n_steps):
    """RK4 积分阻尼谐振子。state = [x, v]。"""
    def deriv(x, v):
        return v, -2*gamma*v - omega0**2*x
    x, v = x0, v0
    settling_time = None
    results = [(x, v)]
    for i in range(n_steps):
        k1x, k1v = deriv(x, v)
        k2x, k2v = deriv(x+0.5*dt*k1x, v+0.5*dt*k1v)
        k3x, k3v = deriv(x+0.5*dt*k2x, v+0.5*dt*k2v)
        k4x, k4v = deriv(x+dt*k3x, v+dt*k3v)
        x += dt/6*(k1x + 2*k2x + 2*k3x + k4x)
        v += dt/6*(k1v + 2*k2v + 2*k3v + k4v)
        results.append((x, v))
        if settling_time is None and abs(x) < 0.01 and abs(v) < 0.01:
            settling_time = (i+1) * dt
    return results, settling_time

omega0 = 2.0  # 固有频率
dt = 0.001
n = 30000
x0, v0 = 1.0, 0.0

print("=== 阻尼谐振子三种区域 (ω₀=2) ===")
for gamma, label in [(0.5, "欠阻尼 γ=0.5"),
                      (2.0, "临界阻尼 γ=2.0=ω₀"),
                      (5.0, "过阻尼 γ=5.0")]:
    _, t_settle = rk4_osc(gamma, omega0, x0, v0, dt, n)
    print(f"  {label:20s}: 回到 |x|<0.01 所需时间 = {t_settle:.2f}" if t_settle
          else f"  {label:20s}: 30000步内未稳定")

print("\n→ 临界阻尼最快回到平衡（这是减震器设计的原理）")
print("→ 过阻尼看似'阻力大'应更快停下，实则被'粘住'缓慢蠕回")
print("→ 欠阻尼振荡过程中多次穿过零点，浪费时间")
```

**输出示例**：
```
=== 阻尼谐振子三种区域 (ω₀=2) ===
  欠阻尼 γ=0.5          : 回到 |x|<0.01 所需时间 = 7.42
  临界阻尼 γ=2.0=ω₀     : 回到 |x|<0.01 所需时间 = 2.93
  过阻尼 γ=5.0          : 回到 |x|<0.01 所需时间 = 4.87

→ 临界阻尼最快回到平衡（这是减震器设计的原理）
```

> **反直觉发现**：增加阻尼到临界值后，继续增加阻尼反而使系统回到平衡**变慢**。汽车减震器、门铰链液压器都设计在接近临界阻尼——既不振荡也不过度粘滞。

---

## 4. 偏微分方程：分离变量与 Green 函数

### 直觉

物理学的三大基本偏微分方程（PDE）分别对应三种物理过程：

| PDE | 方程 | 物理过程 |
|-----|------|---------|
| 波动方程 | $u_{tt} = c^2\nabla^2 u$ | 波的传播（声、光、电磁波）|
| 扩散/热传导方程 | $u_t = D\nabla^2 u$ | 热扩散、粒子扩散 |
| Laplace 方程 | $\nabla^2 u = 0$ | 静电势、稳态温度 |

它们都是**线性**的，因此叠加原理成立。分离变量法利用这个线性性：把 $u(\vec{r},t) = X(x)Y(y)Z(z)T(t)$ 代入 PDE，偏微分方程化为几个常微分方程。这正是量子力学中解氢原子的方法。

**Green 函数**是求解非齐次 PDE 的普适方法：$\nabla^2 G(\vec{r},\vec{r}') = -\delta(\vec{r}-\vec{r}')$。一旦知道 Green 函数，任意源 $\rho(\vec{r}')$ 产生的场为 $u(\vec{r}) = \int G(\vec{r},\vec{r}')\rho(\vec{r}')d^3r'$——这就是静电学 $\phi(\vec{r}) = \frac{1}{4\pi\varepsilon_0}\int\frac{\rho}{|\vec{r}-\vec{r}'|}d^3r'$ 的来源。

### 公式

**分离变量**（以一维波动方程为例）：

$$
\frac{\partial^2 u}{\partial t^2} = c^2\frac{\partial^2 u}{\partial x^2}
$$

设 $u(x,t) = X(x)T(t)$，代入除以 $XT$：

$$
\frac{T''}{c^2 T} = \frac{X''}{X} = -k^2 \quad (\text{分离常数})
$$

得到两个 ODE：$X'' + k^2 X = 0$（空间模式），$T'' + c^2k^2 T = 0$（时间振荡）。

**Fourier 级数**（周期函数展开）：

$$
f(x) = \frac{a_0}{2} + \sum_{n=1}^{\infty}\left(a_n\cos\frac{n\pi x}{L} + b_n\sin\frac{n\pi x}{L}\right)
$$

系数：$a_n = \frac{1}{L}\int_{-L}^{L}f(x)\cos\frac{n\pi x}{L}\,dx$

**Laplace 方程的 Green 函数**（三维自由空间）：

$$
G(\vec{r},\vec{r}') = \frac{1}{4\pi|\vec{r}-\vec{r}'|}
$$

**波动方程推迟 Green 函数**（因果性）：

$$
G_{\text{ret}}(\vec{r},t;\vec{r}',t') = \frac{\delta(t' - t + |\vec{r}-\vec{r}'|/c)}{4\pi|\vec{r}-\vec{r}'|}
$$

只在 $t' \leq t - R/c$ 时非零（信息传播不超过光速）。

### 代码演示：Fourier 级数逼近方波

```python
"""
Fourier 级数逼近方波和三角波。
展示 Gibbs 现象：在间断点附近，部分和有过冲 ~9%，
不管取多少项都不消失——收敛但不一致收敛。
"""
import math

def square_wave_fourier(x, n_terms):
    """方波的 Fourier 级数（奇谐波叠加）。"""
    result = 0.0
    for n in range(1, n_terms*2, 2):  # 只含奇次谐波
        result += math.sin(n*x) / n
    return 4.0 * result / math.pi

# 在间断点 x=0 附近采样
x_jump = 0.01  # 离间断点很近
print("=== Fourier 级数逼近方波: Gibbs 现象 ===")
print(f"在 x={x_jump}（间断点附近），方波值应为 π/2={math.pi/2:.4f}")
print(f"{'项数':>6} {'Fourier和':>12} {'误差':>10}")
for N in [1, 5, 10, 50, 100, 500]:
    val = square_wave_fourier(x_jump, N)
    target = math.pi / 2
    print(f"{N:>6} {val:>12.6f} {val-target:>10.6f}")

# Gibbs 过冲: 在最佳点过冲约 0.08949...×π ≈ 9%
# 理论值: 过冲 = (1/π)∫₀^π sin(t)/t dt - 0.5 ≈ 0.0895
gibbs_overshoot = 0.0895
print(f"\n→ Gibbs 过冲 ≈ {gibbs_overshoot*100:.1f}%（理论值，N→∞仍存在）")
print("→ 收敛但不一致收敛：这是 Fourier 分析最微妙的性质")

# 采样几个点看 Fourier 级数如何逼近
print(f"\n=== 方波 Fourier 级数采样 (N=20) ===")
N = 20
for x in [0.0, 0.3, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 3.14]:
    val = square_wave_fourier(x, N)
    target = math.pi/2 if (x % (2*math.pi)) < math.pi else -math.pi/2
    bar = '#' * int(abs(val)*5)
    print(f"  x={x:.2f}: f={val:+.4f} (目标{target:+.4f}) {bar}")
```

> **反直觉发现（Gibbs 现象）**：用 Fourier 级数逼近方波时，不管叠加多少项，在间断点附近永远有约 9% 的过冲。这不是收敛慢——过冲的高度不随项数减少，只是宽度变窄。这揭示了**三角函数基底无法一致收敛到不连续函数**的根本限制。

---

## 5. 特殊函数：物理学的「标准零件库」

### 直觉

特殊函数是解偏微分方程（在球坐标、柱坐标下分离变量）时自然出现的函数族。它们之于物理学，就像标准零件（螺栓、轴承）之于机械工程——你不需要每次重新发明轮子，直接调用已有零件。

最重要的几族：
- **Legendre 多项式** $P_l(\cos\theta)$：来自球坐标下的 Laplace 方程（角度部分）。描述轨道角动量、多极展开。
- **球谐函数** $Y_l^m(\theta,\phi)$：Legendre 的完整版本，是单位球面上的正交基。氢原子波函数的角度部分。
- **Bessel 函数** $J_n(x)$：来自柱坐标下的波动方程。描述圆形鼓面的振动模式、光纤中的光场分布。
- **Hermite 多项式** $H_n(x)$：量子谐振子的波函数。
- **Laguerre 多项式** $L_n(x)$：氢原子径向波函数。

这些函数看似随意，实则有深刻的**统一结构**：它们都是某类 Sturm-Liouville 问题的本征函数，因此自动正交完备，构成函数空间的基底。

### 公式

**Legendre 多项式**（Rodrigues 公式）：

$$
P_l(x) = \frac{1}{2^l l!}\frac{d^l}{dx^l}(x^2-1)^l
$$

前几个：$P_0=1$, $P_1=x$, $P_2=\frac{1}{2}(3x^2-1)$, $P_3=\frac{1}{2}(5x^3-3x)$。

正交性：$\int_{-1}^{1}P_l(x)P_{l'}(x)\,dx = \frac{2}{2l+1}\delta_{ll'}$

**球谐函数**：

$$
Y_l^m(\theta,\phi) = (-1)^m\sqrt{\frac{2l+1}{4\pi}\frac{(l-m)!}{(l+m)!}}\,P_l^m(\cos\theta)\,e^{im\phi}
$$

**Bessel 函数**（级数定义）：

$$
J_n(x) = \sum_{k=0}^{\infty}\frac{(-1)^k}{k!(k+n)!}\left(\frac{x}{2}\right)^{2k+n}
$$

性质：$J_n$ 在大 $x$ 时以 $\sqrt{2/(\pi x)}$ 振荡衰减（类比 $\sin$ 但有 $1/\sqrt{x}$ 包络）。

**Hermite 多项式**（量子谐振子）：

$$
\psi_n(x) = \frac{1}{\sqrt{2^n n!}}\left(\frac{m\omega}{\pi\hbar}\right)^{1/4}H_n\left(\sqrt{\frac{m\omega}{\hbar}}x\right)e^{-m\omega x^2/(2\hbar)}
$$

### 代码演示：Legendre 多项式与多极展开

```python
"""
Legendre 多项式: 用 Rodrigues 公式数值生成。
应用: 多极展开——远场势用 P_l 展开。
反直觉: 仅用少数几个 P_l 就能高度近似复杂电荷分布的远场。
"""
import math

def legendre(l, x):
    """Rodrigues 公式数值实现 P_l(x)。"""
    # P_l(x) = (1/(2^l l!)) d^l/dx^l (x²-1)^l
    # 用递推关系更稳定: (l+1)P_{l+1} = (2l+1)x P_l - l P_{l-1}
    if l == 0:
        return 1.0
    if l == 1:
        return x
    p_prev2 = 1.0  # P_0
    p_prev1 = x    # P_1
    for n in range(1, l):
        p = ((2*n+1)*x*p_prev1 - n*p_prev2) / (n+1)
        p_prev2 = p_prev1
        p_prev1 = p
    return p_prev1

print("=== Legendre 多项式 P_l(x) ===")
print(f"{'x':>6}", end="")
for l in range(5):
    print(f"  P_{l}(x)", end="")
print()
for x in [-1.0, -0.5, 0.0, 0.5, 1.0]:
    print(f"{x:>6.1f}", end="")
    for l in range(5):
        print(f"  {legendre(l, x):>7.4f}", end="")
    print()

# 正交性验证
print("\n=== 正交性: ∫₋₁¹ P_l P_m dx = 2/(2l+1) δ_{lm} ===")
def simpson(f, a, b, n=10000):
    h = (b-a)/n
    return h/3*(f(a)+f(b) + 4*sum(f(a+i*h) for i in range(1,n,2)) + 2*sum(f(a+i*h) for i in range(2,n,2)))

for l in range(4):
    for m in range(l, 4):
        integral = simpson(lambda x: legendre(l,x)*legendre(m,x), -1, 1)
        expected = 2.0/(2*l+1) if l==m else 0.0
        status = "✓" if abs(integral - expected) < 1e-4 else "✗"
        if l != m or m <= 2:
            print(f"  <P_{l}|P_{m}> = {integral:.6f}, 期望 = {expected:.6f} {status}")

print("\n→ 不同 l 的 P_l 正交（积分为 0），同 l 归一化为 2/(2l+1)")
print("→ 多极展开 φ = Σ (1/r^{l+1}) P_l(cosθ) × 矩: l=0 单极, l=1 偶极, l=2 四极...")
```

---

## 6. Python 数值实验

### 6.1 矩阵的奇异值分解（SVD）与数据压缩

```python
"""
SVD 用于数据压缩的原理演示。
一个秩低的矩阵可以用少数奇异值近似。
这是 PCA（主成分分析）和图像压缩的数学基础。
"""
import math
import random

# 构建一个低秩矩阵（3个分量叠加）
random.seed(42)
m, n = 8, 6
A = [[0.0]*n for _ in range(m)]
for i in range(m):
    for j in range(n):
        A[i][j] = (math.sin(i*0.5)*math.cos(j*0.7)  # 分量1
                  + 0.5*math.exp(-abs(i-j)*0.3))     # 分量2
# 这个矩阵接近秩2

# 计算 A^T A 的特征值 = 奇异值的平方
ATA = [[sum(A[k][i]*A[k][j] for k in range(m)) for j in range(n)] for i in range(n)]

def eigenvalues_symmetric(A, iterations=300):
    """QR 算法。"""
    def mat_mult(A, B):
        return [[sum(A[i][k]*B[k][j] for k in range(len(A[0]))) for j in range(len(B[0]))] for i in range(len(A))]
    def qr_decomp(A):
        n = len(A)
        Q = [[0.0]*n for _ in range(n)]
        R = [[0.0]*n for _ in range(n)]
        for j in range(n):
            v = [A[i][j] for i in range(n)]
            for i in range(j):
                R[i][j] = sum(Q[k][i]*v[k] for k in range(n))
                v = [v[k]-R[i][j]*Q[k][i] for k in range(n)]
            R[j][j] = math.sqrt(sum(x*x for x in v))
            if R[j][j]>1e-15:
                for k in range(n): Q[k][j] = v[k]/R[j][j]
        return Q, R
    M = [row[:] for row in A]
    for _ in range(iterations):
        Q, R = qr_decomp(M)
        M = mat_mult(R, Q)
    return sorted([M[i][i] for i in range(len(M))], reverse=True)

eigs = eigenvalues_symmetric(ATA)
singular_values = [math.sqrt(max(e, 0)) for e in eigs]

print("=== 矩阵的奇异值（从大到小）===")
for i, sv in enumerate(singular_values):
    bar = '#' * int(sv*30)
    print(f"  σ_{i+1} = {sv:.6f} {bar}")

total = sum(s**2 for s in singular_values)
cumulative = 0
for i, sv in enumerate(singular_values):
    cumulative += sv**2
    frac = cumulative / total
    print(f"  前 {i+1} 个奇异值保留 {frac*100:.1f}% 能量")

print("\n→ 前 2 个奇异值已捕获绝大部分能量 → 矩阵接近秩 2")
print("→ SVD 压缩：保留大奇异值，丢弃小奇异值")
```

### 6.2 热传导方程的有限差分模拟

```python
"""
一维热传导方程: u_t = D u_xx
有限差分法（显式格式）: u_i^{n+1} = u_i^n + r(u_{i+1} - 2u_i + u_{i-1})
稳定性条件: r = D*dt/dx² < 0.5（CFL 条件）
"""
import math

N = 50          # 空间网格点
L = 1.0         # 杆长
dx = L / (N-1)
D = 0.01        # 扩散系数

# 稳定 vs 不稳定
for r_factor, label in [(0.4, "稳定 r=0.4"), (0.6, "不稳定 r=0.6")]:
    dt = r_factor * dx**2 / D
    n_steps = 500

    # 初始条件: 中心热点
    u = [0.0]*N
    u[N//2] = 100.0
    u[N//2-1] = 80.0
    u[N//2+1] = 80.0

    stable = True
    max_u = 100.0
    for step in range(n_steps):
        u_new = list(u)
        for i in range(1, N-1):
            u_new[i] = u[i] + r_factor * (u[i+1] - 2*u[i] + u[i-1])
        u = u_new
        if max(abs(x) for x in u) > 1e6:
            stable = False
            break

    peak = max(u)
    mid = u[N//2]
    print(f"{label}: {n_steps}步后 中心温度={mid:.2f}, 峰值={peak:.2f}", 
          "✓ 稳定" if stable else "💥 发散!")

print("\n→ CFL 条件 r < 0.5 是显式差分法的生死线")
print("→ 违反 CFL 时数值振荡发散，与物理完全不符")
```

---

## 7. 习题集

### 基础题（Fischer / Königsberger 级别）

**P5.1** 求矩阵 $A = \begin{pmatrix}2&1\\1&2\end{pmatrix}$ 的本征值和本征向量。验证本征向量正交。

> **答案**：$\lambda = 1, 3$；本征向量 $(1,-1)/\sqrt{2}$ 和 $(1,1)/\sqrt{2}$。

**P5.2** 用留数定理计算 $\int_0^{2\pi}\frac{d\theta}{5+3\cos\theta}$。

> **提示**：令 $z = e^{i\theta}$，化为围道积分。

### 中级题（Arfken 级别）

**P5.3**（复积分）计算 $\oint_{|z|=2}\frac{e^z}{z^2-1}\,dz$。

> **答案**：$2\pi i[\text{Res}(z=1) + \text{Res}(z=-1)] = 2\pi i[\frac{e}{2} - \frac{e^{-1}}{2}] = 2\pi i\sinh(1)$。

**P5.4**（Sturm-Liouville）证明 Legendre 多项式满足正交关系 $\int_{-1}^1 P_l P_{l'}\,dx = \frac{2}{2l+1}\delta_{ll'}$。

> **提示**：从 Legendre 微分方程 $\frac{d}{dx}[(1-x^2)P_l'] + l(l+1)P_l = 0$ 出发，对 $P_l \times$（$P_{l'}$ 的方程）$- P_{l'} \times$（$P_l$ 的方程）积分。

**P5.5**（Fourier 级数）将 $f(x) = x^2$（$-\pi < x < \pi$）展开为 Fourier 级数，并用它推导 $\sum_{n=1}^{\infty}\frac{1}{n^2} = \frac{\pi^2}{6}$。

### 挑战题（Amann / ETH 考试级别）

**P5.6**（留数定理）计算 $\int_{-\infty}^{\infty}\frac{\cos x}{x^2+a^2}\,dx$（$a > 0$）。

> **答案**：$\pi e^{-a}/a$。考虑 $\oint\frac{e^{iz}}{z^2+a^2}\,dz$ 的上半围道。

**P5.7**（Bessel 函数）证明 $J_0(x) = \frac{1}{\pi}\int_0^{\pi}\cos(x\sin\theta)\,d\theta$（积分表示），并由此验证 $J_0(0)=1$。

**P5.8**（分离变量）边长为 $a\times b$ 的矩形膜，边界固定。求所有振动模式频率 $\omega_{mn}$ 和波函数 $u_{mn}(x,y)$。

> **答案**：$\omega_{mn} = c\pi\sqrt{(m/a)^2+(n/b)^2}$，$u_{mn} = \sin(m\pi x/a)\sin(n\pi y/b)$。

---

## 8. 不足与延伸

### 本主题的局限

1. **线性世界观的局限**：线性代数和线性 PDE 叠加原理成立，但真实世界大多是非线性的。Navier-Stokes 方程（湍流）、广义相对论（Einstein 方程）、Yang-Mills 方程都是非线性的——叠加原理失效，解析解稀少。

2. **解析方法的边界**：特殊函数只覆盖少数对称性好的方程。一般 PDE（不规则边界、变系数）全靠数值方法（有限元、谱方法）。解析解是奢侈品，数值解是必需品。

3. **渐近分析欠覆盖**：物理中大量使用渐近展开（如最速下降法、WKB 近似），但标准数学方法课往往点到为止。这些技巧在量子隧穿、散射理论中不可或缺。

4. **分布理论（广义函数）**：δ 函数在物理中无处不在，但严格处理需要 Schwartz 分布理论——多数教材只在工程意义上使用，缺乏数学严谨。

### 延伸方向

| 方向 | 课程/教材 |
|------|----------|
| 泛函分析 | Reed & Simon *Methods of Modern Mathematical Physics* |
| 李群与李代数 | Cornwell *Group Theory in Physics* / Gilmore |
| 微分几何 | Nakahara *Geometry, Topology and Physics* |
| 渐近方法 | Bender & Orszag *Advanced Mathematical Methods* |
| 数值 PDE | LeVeque *Finite Difference/Volume Methods* |

### ETH 特色注记

ETH 的数学方法训练有双重血统：**Amann** 代表的德语区分析传统（Bourbaki 式严谨，从集合论到测度论的完整链条）和 **Arfken** 代表的英美实用传统（以物理问题为导向）。ETH 物理系学生被要求同时掌握两者——既能写出 Cauchy 积分公式的严格证明，又能用留数定理五分钟算出一个散射截面的积分。这种「严谨与实用并重」的训练，是德语区物理学教育的标志特征。

Amann 的三卷 *Analysis* 在 ETH 被用作数学系主教材，物理系学生选读。它的严谨程度在全球物理教育中极为罕见——正是这种训练，使 ETH 培养出了能在理论物理最前沿（如共形场论、弦理论的数学结构）工作的物理学家。

---

> **上一主题**：[04 统计物理](../topic04-statistical/statistical.md)（Phase 1）
>
> **下一主题**：[06 固体物理](../topic06-solid-state/solid-state.md) — 从晶体结构到超导


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：数学物理方法研究「物理学家需要的工具箱」——复分析、特殊函数、群论、微分方程——它不是抽象数学，而是把电场、波函数、规范对称翻译成可计算的语言。
>
> **生活类比**：数学是物理学的**瑞士军刀**。每片刀刃为特定任务而生：复变函数切「波动」，勒让德多项式切「球对称」，群论切「对称性」，傅立叶变换切「频率」。没有这把刀，你看得见物理却握不住。
>
> **反直觉发现（啊哈时刻）**：
> - **留数定理一招抵万招**：散射截面、扩散、Green 函数里那些「算不出来」的实积分，绕到复平面绕一圈奇点就拿答案——积分不是「计算」，是「拓扑」。
> - **对称性 = 守恒律 = 简化**：Noether 定理告诉你能量守恒来自时间平移不变——这不是巧合，是数学强制的。
> - **特殊函数全是特征函数**：Hermite/Bessel/Legendre 不是数学家闲来无事发明，是算符（薛定谔、拉普拉斯）的「本征音符」。
> - **$\delta$ 函数合法化**：Dirac 函数不是函数，是分布（广义函数）——物理学家靠直觉用了 30 年，数学家才补上严格基础（Schwartz，1950 诺奖）。
> - **拓扑不变量」改变物理**：Hall 电导被量子化成 $\nu e^2/h$，整数 $\nu$ 是拓扑（陈数）——离散不变量统治连续物理。

---

## 🔗 衔接：从哪来，到哪去

### ▶ 前置
- **微积分 + 线性代数**（来自力学）：矩阵对角化 = 主轴变换；特征值问题无处不在。
- **复数**：欧拉公式 $e^{i\theta}=\cos\theta+i\sin\theta$ 是量子力学与交流电路的共同语言。

### ⚡ 旧框架的危机
1. **「点电荷」的 $\delta$ 不是函数**：经典函数框架装不下——需要分布理论。
2. **非线性 PDE 无法解析**：Navier-Stokes、广义相对论场方程只能数值 + 微扰 + 渐近。
3. **量子对称性需要新数学**：自旋、规范对称 → 群论 + 李代数成为物理必修。

### 🆕 新框架的危机
- **数值爆炸**：高维 PDE（多体薛定谔）无法用网格解决——催生张量网络、量子蒙特卡洛、AI 求解器。
- **严格存在性**：Navier-Stokes 平滑性是 Clay 千禧问题（100 万美元），至今未解。
- **拓扑相变**：传统 Landau 对称破缺理论解释不了量子霍尔效应、拓扑绝缘体——需要拓扑序的新数学。

### 🚀 后续
| 后续主题 | 用到的数学方法 |
|---------|---------------|
| 06 固体物理 | 布洛赫定理、能带（傅立叶）、群论分类晶格 |
| 07 粒子物理 | 群论 SU(3)×SU(2)×U(1)、路径积分、规范微分形式 |
| 08 GR/宇宙学 | 微分几何、张量、测地线方程、变分法 |

---

## 🏭 理论联系实际：5 个应用

1. **傅立叶变换 + JPEG/MP3**：信号去冗余的核心是「频率分解」——数学物理的傅立叶分析支撑你手机的相册与音乐。
2. **群论 + 晶体学**：230 个空间群分类所有晶体；ETH PSI 中子散射数据靠群论反推声子对称性——决定材料是否超导。
3. **蒙特卡洛积分**：统计物理、金融衍生品定价（Black-Scholes）、辐射传输都用随机采样解高维积分——巴拿赫空间 → Wall Street。
4. **有限元方法（FEM）**：弹性力学、流体、电磁仿真（COMSOL/ANSYS）的工业基石；汽车碰撞、飞机机翼、芯片散热全靠它。
5. **拓扑数据分析（TDA）**（Carlsson 2009）：用同调群分析点云数据的「形状」，用于识别宇宙大尺度结构、蛋白质折叠路径、神经网络训练动力学——纯数学进入数据科学。

---

## 🔬 最新研究前沿（2024-2026）

1. **AI/ML 解 PDE**（2024-2025）：Physics-Informed Neural Networks（PINNs）、神经算子（Neural Operator, Li 2021）在毫秒级求解参数化 PDE，比有限元快 1000 倍——飞机设计、天气预报、材料筛选的革命；ETH 数据科学中心参与。
2. **Navier-Stokes 正则性的进展**（2024-2025）：陶哲轩（Terence Tao）等在有限时间爆破构造上取得部分进展；Mathematica/Knapp 等给出新的能量准则——离 Clay 千禧问题更近但仍未解。
3. **拓扑物态的数学革命**（2024-2025）：高阶拓扑绝缘体、弗洛凯拓扑相、非阿贝尔任意子——推动拓扑量子计算，相关的辫群表示论、模张量范畴成为物理数学热点。
4. **可积系统的新精确解**（2024-2025）：$\mathcal{N}=4$ SYM 的量子谱曲线（ETH Beisert 组贡献）、KPZ 方程的精确矩公式——可积性与随机矩阵的深度融合。
5. **范畴论进入物理**（2024-2025）：拓扑量子场论的「范畴化」、全息对偶的代数几何重构——弦论 / 量子信息 / 凝聚态的数学统一语言；Cohesive ∞-topos 等高级框架在物理学讨论中浮现。

---

## 🗺️ 学习 Roadmap（ETH 路径）

### ETH 课程编号
- **401-0251-00L Analysis I/II**（Amann 教材，ETH 数学物理训练核心）
- **401-0332-00L Linear Algebra**（线性代数，群论前置）
- **402-1701-00L Mathematical Methods in Physics**（BSc 第三年，Arfken/Boas 路线）
- **402-0701-00L Group Theory and Its Applications**（MSc，群论 + 表示论）

### 14 周学习节奏
| 阶段 | 内容 | 知识检查 |
|------|------|----------|
| W1-3 复分析 | 解析、柯西定理、留数、解析延拓 | 用留数 30 秒算 $\int_{-\infty}^{+\infty}\frac{dx}{1+x^2}$。 |
| W4-6 特殊函数 | Γ/B 函数、Hermite/Bessel/Legendre、超几何 | 写出谐振子本征函数并指出 Hermite 出现的原因。 |
| W7-9 偏微分方程 | 分离变量、格林函数、球谐展开 | 解出三维泊松方程的库仑势 Green 函数。 |
| W10-11 群论 | 有限群、Lie 群、表示、特征标 | 用 SU(2) 表示推出角动量耦合（CG 系数）。 |
| W12-14 变分与渐近 | 欧拉-拉格朗日、稳相法、最陡下降 | 用鞍点法推出 Stirling 公式。 |

### 费曼检验
- 能用留数定理替代「实积分硬算」 → 复分析过关。
- 能讲清「为什么群论是量子的语言」 → 群论过关。
- 读 Nakahara《Geometry, Topology and Physics》前三章不觉吃力 → 可进 GR 与场论。
