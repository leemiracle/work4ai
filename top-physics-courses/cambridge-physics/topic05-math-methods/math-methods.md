# Cambridge Part IB · Mathematical Methods

> **教材**：Riley, Hobson & Bence *Mathematical Methods for Physics and Engineering* (3rd ed.) — Cambridge 自编指定教材（Cambridge University Press 出版，1300+ 页巨著）；Boas *Mathematical Methods in the Physical Sciences* 补充
>
> **Cambridge 课程编号**：Part IB Mathematical Methods (旧称 "Mathematical Methods I & II") + Part IB Complex Methods + Part IB Vector Calculus
>
> **Cambridge 特色**：这是全剑桥物理系最厚的一本教材——因为剑桥坚信**数学方法就是物理语言本身**。RHB 三位作者均为剑桥讲师，书中的例题直接取自历年 Tripos 考题。从线性代数到特殊函数，一切物理理论都建立在这套工具之上

---

## 目录

1. [线性代数](#1-线性代数)
2. [复变函数](#2-复变函数)
3. [常微分方程](#3-常微分方程)
4. [偏微分方程](#4-偏微分方程)
5. [特殊函数](#5-特殊函数)
6. [傅里叶分析](#6-傅里叶分析)
7. [Python 代码演示](#7-python-代码演示)
8. [Tripos 风格习题](#8-tripos-风格习题)

---

## 1. 线性代数

### 1.1 本征值与本征向量

剑桥 Part IB 的起点是**将矩阵理解为线性变换**，而非数字方阵。矩阵 $A$ 作用于向量 $\mathbf{v}$ 通常既改变长度又改变方向，但**本征向量**是特殊的——方向不变：

$$A\mathbf{v} = \lambda \mathbf{v}$$

本征值方程 $\det(A - \lambda I) = 0$ 是特征多项式。$n \times n$ 矩阵有 $n$ 个本征值（计入重数和复数）。

**反直觉发现**：实矩阵可以拥有复数本征值！旋转矩阵

$$R = \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix}$$

的特征多项式 $\lambda^2 + 1 = 0$，给出 $\lambda = \pm i$。这不是数学怪癖——它意味着**90° 旋转没有实数不动方向**。这个观察是通往复变函数的桥梁（§2）。

### 1.2 对角化

若 $A$ 有 $n$ 个线性无关的本征向量 $\{\mathbf{v}_k\}$，则可对角化：

$$A = P D P^{-1}, \quad D = \text{diag}(\lambda_1, \ldots, \lambda_n)$$

其中 $P$ 的列为本征向量。物理意义：在本征基下，线性变换退化为各坐标**独立缩放**。

### 1.3 对称矩阵与二次型

**实对称矩阵的关键定理**：(1) 本征值全实；(2) 不同本征值的本征向量正交；(3) 总可正交对角化。

实对称矩阵 $A$ 定义二次型：

$$Q(\mathbf{x}) = \mathbf{x}^T A \mathbf{x}$$

通过正交变换 $\mathbf{x} = P\mathbf{y}$ 可化为标准型：

$$Q = \lambda_1 y_1^2 + \lambda_2 y_2^2 + \cdots + \lambda_n y_n^2$$

本征值的符号决定了二次曲面的类型：

| 本征值符号 | 二次曲面（$n=3$） | 几何形状 |
|-----------|-----------------|---------|
| 全正 | $Q > 0$ | 椭球面 |
| 两正一负 | 鞍面 | 单叶双曲面 |
| 两负一正 | 鞍面 | 双叶双曲面 |
| 全负 | $Q < 0$ | 椭球面（反向） |

**Sylvester 惯性律**：二次型的正、负、零本征值个数（惯性指数）在合同变换下不变。这直接决定了广义相对论中时空**度规的符号差**——区分 Riemann 几何与 Lorentz 几何。

### 1.4 矩阵函数与指数映射

矩阵的指数是连接线性代数与微分方程的核心工具：

$$e^{A} = \sum_{n=0}^{\infty} \frac{A^n}{n!}$$

若 $A = PDP^{-1}$，则 $e^A = P e^D P^{-1}$。对于反对称矩阵 $A^T = -A$，$e^A$ 是**正交矩阵**——即旋转！这正是 SO(3) 李群的指数映射。

---

## 2. 复变函数

### 2.1 解析函数与 Cauchy-Riemann 方程

复变函数 $f(z) = u(x,y) + iv(x,y)$ 在某点**解析**（复可微），当且仅当满足 **Cauchy-Riemann 方程**：

$$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \qquad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$

解析函数是"刚性"的——一旦知道它在一小段弧上的值，**整个区域内的值就被完全确定**（唯一性定理）。这是复分析与实分析的根本区别。

**反直觉发现**：$f(z) = |z|^2 = x^2 + y^2$ 只在 $z = 0$ 一点复可微，**无处解析**。尽管它在实分析中是最光滑的函数之一！

### 2.2 Cauchy 定理与 Cauchy 积分公式

**Cauchy 定理**：若 $f$ 在简单闭合曲线 $C$ 及其内部解析，则

$$\oint_C f(z)\,dz = 0$$

由此推出**Cauchy 积分公式**——解析函数的值由边界值决定：

$$f(z_0) = \frac{1}{2\pi i}\oint_C \frac{f(z)}{z - z_0}\,dz$$

反复求导，解析函数**自动无限次可微**：

$$f^{(n)}(z_0) = \frac{n!}{2\pi i}\oint_C \frac{f(z)}{(z-z_0)^{n+1}}\,dz$$

### 2.3 Taylor 级数与 Laurent 级数

解析函数可展开为 **Taylor 级数**（收敛半径内）：

$$f(z) = \sum_{n=0}^{\infty} a_n (z - z_0)^n$$

围绕**奇点**则展开为 **Laurent 级数**——包含负幂项：

$$f(z) = \sum_{n=-\infty}^{\infty} a_n (z - z_0)^n$$

负幂项最高次数决定奇点类型：

| 负幂项 | 奇点类型 | 例子 |
|--------|---------|------|
| 最负到 $(z-z_0)^{-1}$ | **可去**（$a_{-1}=0$）或**极点** | $1/z$ 在 $z=0$ 为一阶极点 |
| 有限负幂 | 极点（$m$ 阶） | $1/z^3$ 为三阶极点 |
| 无限负幂 | **本性奇点** | $e^{1/z}$ 在 $z=0$ |

### 2.4 留数定理

**留数定理**是复变函数论最强大的计算工具：

$$\oint_C f(z)\,dz = 2\pi i \sum_k \text{Res}(f, z_k)$$

其中求和遍历 $C$ 内的所有孤立奇点。留数为 Laurent 级数的 $a_{-1}$ 系数：

$$\text{Res}(f, z_0) = \frac{1}{(m-1)!}\lim_{z\to z_0}\frac{d^{m-1}}{dz^{m-1}}\left[(z-z_0)^m f(z)\right] \quad (\text{$m$ 阶极点})$$

**工程应用**：留数定理可以将困难实积分化为简单复积分。例如积分

$$I = \int_0^{\infty} \frac{dx}{1 + x^4}$$

直接计算困难，但取上半平面大半圆闭合路径，被积函数的极点为 $e^{i\pi/4}, e^{i3\pi/4}$，留数定理一步给出 $I = \frac{\pi}{2\sqrt{2}}$。

---

## 3. 常微分方程

### 3.1 一阶 ODE

| 类型 | 形式 | 解法 |
|------|------|------|
| 可分离 | $y' = f(x)g(y)$ | $\int \frac{dy}{g(y)} = \int f(x)\,dx$ |
| 线性 | $y' + P(x)y = Q(x)$ | 积分因子 $\mu = e^{\int P\,dx}$ |
| 恰当 | $M\,dx + N\,dy = 0$, $\frac{\partial M}{\partial y}=\frac{\partial N}{\partial x}$ | 势函数 $F$ |
| Bernoulli | $y' + Py = Qy^n$ | 代换 $v = y^{1-n}$ |

### 3.2 二阶线性 ODE

一般形式：

$$y'' + P(x)y' + Q(x)y = R(x)$$

**常系数齐次**方程 $ay'' + by' + cy = 0$ 的特征方程 $a\lambda^2 + b\lambda + c = 0$ 给出：

| 判别式 | 根 | 通解 |
|--------|-----|------|
| $\Delta > 0$ | 两不同实根 $\lambda_{1,2}$ | $y = Ae^{\lambda_1 x} + Be^{\lambda_2 x}$ |
| $\Delta = 0$ | 重根 $\lambda$ | $y = (A + Bx)e^{\lambda x}$ |
| $\Delta < 0$ | 共轭复根 $\alpha \pm i\beta$ | $y = e^{\alpha x}(A\cos\beta x + B\sin\beta x)$ |

**反直觉发现**：阻尼谐振子 $\ddot{x} + 2\gamma\dot{x} + \omega_0^2 x = 0$ 在临界阻尼 $\gamma = \omega_0$ 时**最快回到平衡**，而非过阻尼！过阻尼时指数衰减很慢（一个根趋于零），欠阻尼会振荡。临界阻尼是两者之间的"甜区"——这正是汽车减震器设计在临界阻尼附近的原因。

### 3.3 Frobenius 方法与正则奇点

对于变系数方程，幂级数解法（$y = \sum a_n x^n$）在**正则奇点**处推广为 **Frobenius 方法**：

$$y = x^r \sum_{n=0}^{\infty} a_n x^n$$

指标方程决定 $r$。两个线性无关解的形式取决于指标根之差：

- 根之差不是整数：两解均为 Frobenius 型
- 根之差是整数：第二解可能含 $\ln x$ 项

这个 $\ln$ 项直接联系到 Bessel 方程的第二类解 $Y_\nu(x)$。

### 3.4 Sturm-Liouville 理论

形如

$$-\frac{d}{dx}\left[p(x)\frac{dy}{dx}\right] + q(x)y = \lambda w(x) y$$

的本征值问题称为 **Sturm-Liouville 问题**。关键性质：

1. 本征值 $\lambda_n$ 全实且可排序 $\lambda_0 < \lambda_1 < \cdots$
2. 本征函数在权 $w(x)$ 下**正交**：$\int y_m y_n w\,dx = 0$（$m\neq n$）
3. 本征函数构成**完备基**

物理中的 Schrödinger 方程、球谐函数、Bessel 函数都是 S-L 问题的特例。这是正交多项式与特殊函数的统一来源。

---

## 4. 偏微分方程

### 4.1 三大经典方程

| 方程 | 形式 | 物理背景 | 类型 |
|------|------|---------|------|
| **波动方程** | $u_{tt} = c^2 \nabla^2 u$ | 弦振动、声波、电磁波 | 双曲型 |
| **热传导方程** | $u_t = \alpha \nabla^2 u$ | 热扩散、布朗运动 | 抛物型 |
| **Laplace 方程** | $\nabla^2 u = 0$ | 静电势、稳态温度 | 椭圆型 |

### 4.2 分离变量法

以一维波动方程 $u_{tt} = c^2 u_{xx}$ 为例。设 $u(x,t) = X(x)T(t)$ 代入：

$$\frac{T''}{c^2 T} = \frac{X''}{X} = -k^2$$

分离为两个 ODE，各自求解后叠加：

$$u(x,t) = \sum_n \left[A_n\cos(k_n ct) + B_n\sin(k_n ct)\right]\sin(k_n x)$$

边界条件（如固定端 $u(0,t)=u(L,t)=0$）选出离散本征值 $k_n = n\pi/L$。

**分离变量法的本质**就是将 PDE 分解为 Sturm-Liouville 本征值问题（§3.4），本征函数给出正交基——这就是为什么特殊函数无处不在。

### 4.3 球坐标下的 Laplace 方程

球坐标 $\nabla^2 u = 0$ 的分离变量 $u(r,\theta,\phi) = R(r)\Theta(\theta)\Phi(\phi)$ 给出：

- **球谐函数** $Y_\ell^m(\theta,\phi)$（角部分，本征函数）
- **径向方程**给出 $r^\ell$ 和 $r^{-\ell-1}$

$$u(r,\theta,\phi) = \sum_{\ell=0}^{\infty}\sum_{m=-\ell}^{\ell}\left(A_{\ell m}r^\ell + B_{\ell m}r^{-\ell-1}\right)Y_\ell^m(\theta,\phi)$$

球谐函数连接量子力学角动量、电磁多极展开、引力势——一鱼三吃。

### 4.4 格林函数

**格林函数** $G(\mathbf{r}, \mathbf{r}')$ 是点源响应：

$$\mathcal{L}G(\mathbf{r}, \mathbf{r}') = \delta(\mathbf{r} - \mathbf{r}')$$

解为：

$$u(\mathbf{r}) = \int G(\mathbf{r}, \mathbf{r}') f(\mathbf{r}')\,d^3r'$$

Laplace 算符的三维格林函数就是熟悉的库仑势 $G = -\frac{1}{4\pi|\mathbf{r}-\mathbf{r}'|}$——数学工具与物理定律在此完美统一。

---

## 5. 特殊函数

### 5.1 Bessel 函数

Bessel 方程（柱坐标波动/扩散）：

$$x^2 y'' + xy' + (x^2 - \nu^2)y = 0$$

解为第一类 Bessel 函数 $J_\nu(x)$ 和第二类 $Y_\nu(x)$。

**渐近行为**：

| 区域 | $J_\nu(x)$ 行为 |
|------|----------------|
| $x \to 0$ | $\sim \frac{(x/2)^\nu}{\Gamma(\nu+1)}$ |
| $x \to \infty$ | $\sim \sqrt{\frac{2}{\pi x}}\cos(x - \frac{\nu\pi}{2} - \frac{\pi}{4})$ |

大 $x$ 时的振幅 $\sim 1/\sqrt{x}$ 衰减——这是柱面波的能量守恒在数学上的体现（波前柱面面积 $\propto r$，故振幅 $\propto r^{-1/2}$）。

### 5.2 Legendre 函数与连带 Legendre 函数

Legendre 方程（球坐标极角部分）：

$$(1-x^2)y'' - 2xy' + \ell(\ell+1)y = 0$$

解为 Legendre 多项式 $P_\ell(x)$（$\ell$ 为非负整数时）。**Rodrigues 公式**：

$$P_\ell(x) = \frac{1}{2^\ell \ell!}\frac{d^\ell}{dx^\ell}(x^2-1)^\ell$$

连带 Legendre 函数 $P_\ell^m(x) = (-1)^m(1-x^2)^{m/2}\frac{d^m}{dx^m}P_\ell(x)$ 组合为球谐函数：

$$Y_\ell^m(\theta,\phi) \propto P_\ell^{|m|}(\cos\theta)e^{im\phi}$$

### 5.3 Gamma 函数

$$\Gamma(z) = \int_0^\infty t^{z-1}e^{-t}\,dt, \quad \text{Re}(z) > 0$$

满足 $\Gamma(z+1) = z\Gamma(z)$（$\Gamma(n+1) = n!$ 对正整数）。它将阶乘**解析延拓**到复平面。

**反直觉发现**：$\Gamma(n) = (n-1)!$ 但 $\Gamma$ 有极点在 $z = 0, -1, -2, \ldots$。这意味着"负整数阶乘是无穷大"——阶乘无法解析延拓到负整数。更妙的是 $\Gamma(1/2) = \sqrt{\pi}$，连接了阶乘与圆周率！

---

## 6. 傅里叶分析

### 6.1 傅里叶级数

周期为 $2L$ 的函数可展开：

$$f(x) = \frac{a_0}{2} + \sum_{n=1}^{\infty}\left[a_n\cos\frac{n\pi x}{L} + b_n\sin\frac{n\pi x}{L}\right]$$

系数：

$$a_n = \frac{1}{L}\int_{-L}^{L} f(x)\cos\frac{n\pi x}{L}\,dx, \quad b_n = \frac{1}{L}\int_{-L}^{L} f(x)\sin\frac{n\pi x}{L}\,dx$$

**Gibbs 现象**：在函数的不连续点处，傅里叶级数**过冲约 9%**，且不随项数增加而消失——只是过冲区域变窄。这是部分和收敛的固有特征。

### 6.2 傅里叶变换

非周期函数取 $L\to\infty$ 极限，傅里叶级数变为**傅里叶变换**：

$$\tilde{f}(k) = \int_{-\infty}^{\infty} f(x)e^{-ikx}\,dx, \qquad f(x) = \frac{1}{2\pi}\int_{-\infty}^{\infty} \tilde{f}(k)e^{ikx}\,dk$$

### 6.3 不确定性原理

**带宽-时长乘积**：信号在时域和频域不能同时"很窄"。精确表述：

$$\Delta x \cdot \Delta k \ge \frac{1}{2}$$

Gauss 函数 $f(x) = e^{-x^2/2\sigma^2}$ 达到下界 $\Delta x \cdot \Delta k = 1/2$。这就是量子力学**位置-动量不确定性**的数学根源——$\Delta x \cdot \Delta p \ge \hbar/2$。

### 6.4 卷积定理

卷积的傅里叶变换等于傅里叶变换的乘积：

$$\mathcal{F}\{f * g\} = \tilde{f}\cdot\tilde{g}$$

这是信号处理、概率论（特征函数）、量子力学（传播子）的核心工具。

---

## 7. Python 代码演示

> 纯标准库实现：复变函数留数验证 + 傅里叶级数 Gibbs 现象 + Sturm-Liouville 本征值。

```python
"""
Cambridge Part IB Mathematical Methods — 演示
1. 留数定理验证: ∫₀^∞ dx/(1+x⁴) = π/(2√2)
2. Fourier 级数 Gibbs 现象 (方波过冲 ≈ 9%)
3. Sturm-Liouville 本征值: 量子谐振子能级 (WKB 量子化)
"""
import math
import cmath

# ============================================================
# 实验1: 留数定理验证积分 ∫₀^∞ dx/(1+x⁴)
# ============================================================
print("=" * 60)
print("实验1: 留数定理验证  ∫₀^∞ dx/(1+x⁴)")
print("=" * 60)

# 数值积分 (Simpson 法)
def f(x):
    return 1.0 / (1.0 + x**4)

def simpson(a, b, n=100000):
    """复合 Simpson 法"""
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += (4 if i % 2 == 1 else 2) * f(a + i * h)
    return s * h / 3

numerical = simpson(0, 1000, 200000)  # 积分到1000近似无穷
exact = math.pi / (2 * math.sqrt(2))
print(f"  数值积分 (Simpson) = {numerical:.10f}")
print(f"  精确值 π/(2√2)    = {exact:.10f}")
print(f"  误差               = {abs(numerical - exact):.2e}")

# 留数定理推导
# 1/(1+z⁴) 的极点: z⁴ = -1 = e^{iπ}  → z_k = e^{i(π+2kπ)/4}, k=0,1,2,3
# 上半平面极点: z₁ = e^{iπ/4}, z₂ = e^{i3π/4}
print("\n  --- 留数定理推导 ---")
poles_upper = [cmath.exp(1j * math.pi / 4), cmath.exp(1j * 3 * math.pi / 4)]
residue_sum = 0.0
for z0 in poles_upper:
    # 一阶极点留数: Res = 1/(d/dz(1+z⁴))|_{z₀} = 1/(4z₀³)
    res = 1.0 / (4 * z0**3)
    residue_sum += res
    print(f"  极点 z = {z0:.4f}, 留数 = {res:.6f}")

I_residue = 2 * math.pi * 1j * residue_sum  # ∮ = 2πi ΣRes
print(f"\n  2πi × Σ(留数) = {I_residue.real:.10f} + {I_residue.imag:.2e}i")
full_line_exact = math.pi / math.sqrt(2)  # ∫_{-∞}^{∞} = 2 × π/(2√2)
print(f"  (虚部≈0; 实部 = ∫₋∞^∞ 1/(1+x⁴)dx = π/√2 = {full_line_exact:.10f})")
print(f"  被2除得 ∫₀^∞ = {I_residue.real/2:.10f}  vs 精确 {exact:.10f}  ✓")

# ============================================================
# 实验2: Fourier 级数 Gibbs 现象
# ============================================================
print("\n" + "=" * 60)
print("实验2: 方波 Fourier 级数 — Gibbs 过冲")
print("=" * 60)

def square_wave_fourier(x, N):
    """方波的 N 项 Fourier 级数 (只有奇正弦项)
    f(x) = (4/π) Σ sin((2k-1)x)/(2k-1)
    """
    s = 0.0
    for k in range(1, N + 1):
        n = 2 * k - 1  # 奇数
        s += math.sin(n * x) / n
    return 4 * s / math.pi

# 在不连续点 x=0 附近，峰值 ≈ 1.179 (过冲 = 9%×跳变幅度2 = 0.179)
print("  方波跳变在 x=0 (从-1跳到+1, 跳变幅度=2)，考察 x→0⁺ 的峰值:")
print(f"  {'N(项数)':<10} {'峰值':<12} {'过冲/跳变':<12} {'标准Gibbs%'}")
for N in [5, 10, 20, 50, 100, 500]:
    # 第一个极大值在 x ≈ π/(2N) 附近
    x_peak = math.pi / (2 * N)
    # 扫描找精确峰值
    best = 0.0
    for i in range(1, 1000):
        x = i * 0.001
        if x > 0.5:
            break
        val = square_wave_fourier(x, N)
        if val > best:
            best = val
    overshoot_of_jump = (best - 1.0) / 2.0 * 100  # 占跳变幅度(2)的百分比
    print(f"  {N:<10} {best:<12.6f} {(best-1.0):<12.6f} {overshoot_of_jump:.2f}%")

# Gibbs 常数: Wilbraham-Gibbs 常数
# 精确值: 过冲/跳变 = (1/π)∫₀^π sin(t)/t dt - 1/2 ≈ 0.08949, 即 8.95%
print(f"\n  理论 Gibbs 过冲 ≈ 8.949% × 跳变幅度 (Wilbraham-Gibbs 常数)")
print(f"  峰值 ≈ 1 + 0.0895×2 = 1.179")
print(f"  注意: 过冲量不随 N 减小! 只是变窄 — Gibbs 现象")

# ============================================================
# 实验3: Sturm-Liouville → 量子谐振子能级
# ============================================================
print("\n" + "=" * 60)
print("实验3: 量子谐振子能级 — WKB 量子化 (对 QHO 精确!)")
print("=" * 60)
# Schrödinger: -ψ'' + x²ψ = Eψ  (ℏ=m=ω=1),  V(x)=x²/2
# 经典转折点: x_t = ±√(2E)
# Bohr-Sommerfeld 量子化: ∮√(2(E-V(x)))dx = 2π(n+1/2)
# 对 QHO 此条件精确 (无 WKB 修正), 故 E_n = n+1/2

def classical_action(E, n_quad=10000):
    """数值计算经典作用量 J(E) = ∮ p dx = 4∫₀^{√(2E)} √(2(E-x²/2)) dx
    解析结果: J = 2πE (QHO 的作用量恰为能量的 2π 倍)"""
    x_t = math.sqrt(2 * E)  # 转折点
    dx = x_t / n_quad
    integral = 0.0
    for i in range(1, n_quad):
        x = i * dx
        p_sq = 2 * (E - x*x/2)  # 动量平方 2(E-V)
        if p_sq > 0:
            integral += math.sqrt(p_sq)
    integral *= dx
    return 4 * integral  # ×4: 0→x_t 乘以 4 (两段 × 来回)

def solve_energy_from_action(n):
    """由 Bohr-Sommerfeld J(E)=2π(n+1/2) 反解 E
    J=2πE → E=n+1/2; 但用数值 J(E) 演示自洽求解"""
    target_J = 2 * math.pi * (n + 0.5)
    # J(E) = 2πE 对 QHO, 数值验证
    # 二分法: J 单调增 (dJ/dE = 周期 = 2π)
    E_lo, E_hi = 0.01, n + 2.0
    for _ in range(60):
        E_mid = (E_lo + E_hi) / 2
        if classical_action(E_mid) < target_J:
            E_lo = E_mid
        else:
            E_hi = E_mid
    return (E_lo + E_hi) / 2

print(f"  Bohr-Sommerfeld: J(E) = ∮√(2(E-V))dx = 2π(n+½)")
print(f"  解析解: E_n = n + ½\n")
print(f"  {'n':<5} {'数值 E_n':<15} {'J数值':<14} {'精确 E_n':<15} {'误差'}")
for n in [0, 1, 2, 3, 5, 8, 10]:
    E_num = solve_energy_from_action(n)
    E_exact = n + 0.5
    J_num = classical_action(E_num)
    print(f"  {n:<5} {E_num:<15.8f} {J_num:<14.6f} {E_exact:<15.8f} {abs(E_num-E_exact):.2e}")

J_analytic_check = classical_action(3.5)  # E=3.5 → n=3
print(f"\n  J(E=3.5) = {J_analytic_check:.8f}  vs 2π(n+½)=2π·3.5={2*math.pi*3.5:.8f}")
print(f"  (对 QHO, WKB 条件精确成立 — 无高阶修正!)")
print("\n  结论: WKB 量子化精确给出 E_n = n+½ (S-L 本征值)")
print("  → S-L 理论保证本征值实数、正交、完备")
```

---

## 8. Tripos 风格习题

### 习题 1（Part IB 难度）：留数定理求实积分

用留数定理计算

$$I = \int_0^{\infty} \frac{\cos ax}{x^2 + b^2}\,dx, \quad a, b > 0$$

<details>
<summary>解答</summary>

考虑 $f(z) = \frac{e^{iaz}}{z^2+b^2}$，取上半平面大半圆闭合路径（$a>0$ 保证大圆弧贡献为零，Jordan 引理）。

被积函数极点：$z = \pm ib$，上半平面仅有 $z = ib$（一阶极点）。

$$\text{Res}(f, ib) = \frac{e^{ia(ib)}}{2ib} = \frac{e^{-ab}}{2ib}$$

留数定理：

$$\int_{-\infty}^{\infty}\frac{e^{iax}}{x^2+b^2}dx = 2\pi i \cdot \frac{e^{-ab}}{2ib} = \frac{\pi e^{-ab}}{b}$$

取实部：

$$I = \frac{\pi}{2b}e^{-ab}$$

验证：$a=0$ 时 $I = \pi/(2b)$，即 $\int_0^\infty \frac{dx}{x^2+b^2} = \frac{\pi}{2b}$ ✓
</details>

### 习题 2（Part IB 难度）：临界阻尼

证明阻尼谐振子 $\ddot{x}+2\gamma\dot{x}+\omega_0^2 x = 0$ 在临界阻尼 $\gamma = \omega_0$ 时回到平衡最快。

<details>
<summary>解答</summary>

特征方程 $\lambda^2 + 2\gamma\lambda + \omega_0^2 = 0$，根 $\lambda = -\gamma \pm \sqrt{\gamma^2 - \omega_0^2}$。

**过阻尼** ($\gamma > \omega_0$)：两负实根 $\lambda_1 = -\gamma + \sqrt{\gamma^2-\omega_0^2}$，$\lambda_2 = -\gamma - \sqrt{\gamma^2-\omega_0^2}$。$\lambda_1$ 趋于零（$\gamma\gg\omega_0$ 时 $\lambda_1 \approx -\omega_0^2/(2\gamma) \to 0$），衰减极慢。

**临界阻尼** ($\gamma = \omega_0$)：重根 $\lambda = -\omega_0$，解 $x = (A+Bt)e^{-\omega_0 t}$，衰减率恰为 $\omega_0$。

**欠阻尼** ($\gamma < \omega_0$)：$x = e^{-\gamma t}(A\cos\omega_d t + B\sin\omega_d t)$，包络 $e^{-\gamma t}$，衰减率 $\gamma < \omega_0$。

比较包络衰减率：过阻尼 $\sim e^{-\omega_0^2 t / 2\gamma}$（很慢），临界 $e^{-\omega_0 t}$，欠阻尼 $e^{-\gamma t}$ ($\gamma < \omega_0$)。临界阻尼的 $e^{-\omega_0 t}$ 最快且不振荡。$\square$
</details>

### 习题 3（Part II 预习）：球谐函数正交性

证明球谐函数满足正交关系

$$\int_0^{2\pi}\int_0^{\pi} Y_\ell^m(\theta,\phi)\,Y_{\ell'}^{m'*}(\theta,\phi)\,\sin\theta\,d\theta\,d\phi = \delta_{\ell\ell'}\delta_{mm'}$$

<details>
<summary>解答</summary>

球谐函数 $Y_\ell^m \propto P_\ell^m(\cos\theta)e^{im\phi}$ 是角动量算符 $\hat{L}^2$ 和 $\hat{L}_z$ 的共同本征函数，属 Sturm-Liouville 问题（§3.4）。

**$\phi$ 积分**：$\int_0^{2\pi}e^{i(m-m')\phi}d\phi = 2\pi\delta_{mm'}$。

**$\theta$ 积分**：连带 Legendre 函数 $P_\ell^m(\cos\theta)$ 是 S-L 问题

$$\frac{d}{d\theta}\left(\sin\theta\frac{d\Theta}{d\theta}\right) + \left[\ell(\ell+1)\sin\theta - \frac{m^2}{\sin\theta}\right]\Theta = 0$$

的本征函数，权函数 $w = \sin\theta$。S-L 理论保证不同 $\ell$ 的本征函数在权 $\sin\theta$ 下正交。$\square$

**物理意义**：$Y_\ell^m$ 构成球面上平方可积函数的完备正交基——任意角分布可展开为"球谐级数"（类比 Fourier 级数），这是多极展开的数学基础。
</details>

### 习题 4（Part IB 难度）：Fourier 变换求 Green 函数

用 Fourier 变换求热传导方程 $\frac{\partial u}{\partial t} = \alpha \frac{\partial^2 u}{\partial x^2}$ 的基本解（Green 函数）。

<details>
<summary>解答</summary>

对 $x$ 做 Fourier 变换：$\tilde{u}(k,t) = \int u(x,t)e^{-ikx}dx$。

方程变为 ODE：$\frac{d\tilde{u}}{dt} = -\alpha k^2 \tilde{u}$

解：$\tilde{u}(k,t) = \tilde{u}(k,0)e^{-\alpha k^2 t}$

初始条件 $u(x,0) = \delta(x)$，即 $\tilde{u}(k,0) = 1$：

$$\tilde{u}(k,t) = e^{-\alpha k^2 t}$$

逆 Fourier 变换（Gauss 函数的 Fourier 变换仍是 Gauss 函数）：

$$G(x,t) = \frac{1}{\sqrt{4\pi\alpha t}}\exp\left(-\frac{x^2}{4\alpha t}\right)$$

这是一方差 $\sigma^2 = 2\alpha t$ 的 Gauss 分布——热扩散就是**概率分布的展宽**，直接联系 Brown 运动。

验证卷积定理：$u(x,t) = \int G(x-x',t)u(x',0)dx'$。$\square$
</details>

---

## Cambridge 数学传统

### Mathematical Tripos 与数学物理

Cambridge 是**数学物理方法的圣地**。Mathematical Tripos 本身就是一个数学考试体系——物理系学生（Natural Sciences）和数学系学生（Mathematical Tripos）都要掌握扎实的数学方法。这种"以数学为物理语言"的传统造就了剑桥的独特风格：

- **George Stokes** (1819–1903): Stokes 定理、Navier-Stokes 方程、荧光（Stokes 位移）
- **James Clerk Maxwell** (1831–1879): Maxwell 方程组——纯数学方法的巅峰，把 Faraday 的力线直觉化为偏微分方程
- **Paul Dirac** (1902–1984): Cambridge 培养了他对数学美的执着——Dirac 方程是"数学美先于物理"的典范
- **Roger Penrose** (1931–): Cambridge 数学的继承者，用旋量和扭量理论革新了广义相对论的数学表述

### RHB 教材的由来

Riley, Hobson & Bence 的 *Mathematical Methods for Physics and Engineering* 诞生于剑桥本科教学的实际需求。三位作者长期在剑桥讲授数学方法课程，教材中的习题大量改编自历年 Tripos 试题。这本书之所以厚达 1300+ 页，正是因为剑桥要求物理/工程学生掌握**几乎所有**纯数学与应用数学工具——从初等线性代数到群论，从复分析到积分变换——为后续的专业物理课程铺平道路。

---

## 参考与延伸阅读

| 教材 | 章节 | 重点 |
|------|------|------|
| Riley, Hobson & Bence Ch 1-8 | 线性代数 + 向量 | Part IB 基础 |
| Riley, Hobson & Bence Ch 12-15 | 复变函数 | Part IB Complex Methods |
| Riley, Hobson & Bence Ch 14 | 留数定理 | 核心计算工具 |
| Riley, Hobson & Bence Ch 16-25 | ODE + PDE + 特殊函数 | Part IB 核心 |
| Riley, Hobson & Bence Ch 12 | Fourier 分析 | 信号 + 量子力学桥梁 |
| Boas Ch 1-8 | 全部概览 | 偏直觉，快速入门 |
| Arfken, Weber & Harris | 特殊函数专章 | 深入参考 |
| Morse & Feshbach Vol I-II | 物理数学方法 | 高阶经典 |

---

**版本**：v1.0 (2026-08-12) · Cambridge Part IB Mathematical Methods


---

## 🎯 费曼式入口（白话版）

> **一句话解释**：物理学家说"大自然用数学说话"——这门课教你听懂这套语言：复变、级数、特殊函数、积分变换、群论，全是物理问题的"翻译工具"。
>
> **生活类比**：学外语。先背单词（特殊函数：贝塞尔、勒让德），再学语法（微分方程、变分法），最后能写诗（解出物理问题、发现新现象）。
>
> **反直觉发现（啊哈时刻）**：一个**发散**的无穷级数（渐近级数）反而能给出极其精确的近似——只要你别加太多项！量子电动力学的扰动计算就是靠这种"越加越差、截断最好"的级数拿到了与实验吻合到小数点后 12 位的精度。

---

## 🔗 衔接：从哪来，到哪去

- **前置知识**：中学微积分、矢量代数、Part IA Mathematics
- **危机（为何需要更多数学）**：物理问题越来越复杂——电磁波（PDE）、量子力学（复变 + 本征值）、相对论（张量）、粒子物理（群论）——没有这些工具寸步难行
- **新危机**：非线性、混沌、数值方法、**机器学习**进入物理，传统解析法碰到墙
- **后续去向**：群论 → **粒子物理/固体**（对称性分类）；张量 → **广义相对论**（Topic 8）；复变 → 量子/流体；积分变换 → 信号处理/量子场论

---

## 🏭 理论联系实际：5 个现代应用

1. **傅里叶变换**：JPEG/MP3 压缩、MRI 图像重建、5G 的 OFDM 调制——几乎所有数字信号处理的核心。
2. **拉普拉斯变换**：电路瞬态分析、自动控制系统（PID）、振动分析。
3. **群论**：晶体点群分类、粒子物理的夸克模型（SU(3)）、分子振动光谱选择定则。
4. **特殊函数**：贝塞尔函数 → 光纤模式；勒让德多项式 → 多极辐射（Topic 2 §1.4）；伽马函数 → 统计分布。
5. **数值 PDE / 有限元**：天气预报、飞机气动 CFD、桥梁应力分析全靠它。

---

## 🔬 最新研究前沿（2024-2026）

1. **物理信息神经网络（PINNs）**：2024 用深度学习解偏微分方程，把流体、材料、量子仿真从网格计算解放（Raissi 框架，*Nature Reviews Physics*, 2024 大量应用）。
2. **拓扑数据分析**：2024 用持续同调（persistent homology）分析材料结构、生物分子构象、宇宙大尺度结构——把代数拓扑变成数据分析工具。
3. **神经算子 / Fourier Neural Operator**：2024 学习无穷维算子映射，把科学计算加速 1000×，正在改变 PDE 求解范式。
4. **渐近分析与可积系统**：2024–2025 非线性 PDE（KdV、Painlevé 超越函数）的精确解与可积性研究持续突破。
5. **量子算法解线性代数/PDE**：2024 HHL 类量子线性代数算法与量子微分方程求解器的理论与实验进展。

---

## 🗺️ 学习 Roadmap（Cambridge Tripos 路径）

| 阶段 | 课程 | 你应当能做到 |
|------|------|------------|
| **Part IA** | Mathematics / NST Math | 微积分、矢量分析、线性代数、常微分方程 |
| **Part IB** | Mathematical Methods | 复变（留数定理）、PDE、傅里叶/拉普拉斯变换、特殊函数、变分法 |
| **Part IB** | Linear Algebra | 本征值、对角化、二次型 |
| **Part II** | Variational Methods / Group Theory / Tensors | 变分原理、群表示论、张量分析、渐近展开 |
| **Part III** | Differential Geometry / Lie Groups / Functional Analysis | 微分几何、李群李代数、泛函分析、随机过程 |

**知识检查三问**：
1. 能否用**留数定理**把一个难算的实积分秒杀？（例如 $\int_0^\infty \frac{dx}{1+x^4}$）
2. 能否用傅里叶变换把扩散方程/波动方程解出来？
3. 为什么说对称性"决定"了守恒量？（Noether 定理 + 群论的物理意义）
