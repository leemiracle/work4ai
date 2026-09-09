# 数学知识词典 - 第九卷：特殊函数与分析方法
## Mathematics Subject Dictionary - Volume 9: Special Functions and Analytic Methods

**MSC分类**: 31-XX, 33-XX, 40-XX, 41-XX, 43-XX, 44-XX, 45-XX  
**版本**: 2.0  
**更新日期**: 2025-03-26  

---

## 目录

1. [31-XX 位势论 (Potential Theory)](#31-xx-位势论-potential-theory)
2. [33-XX 特殊函数 (Special Functions)](#33-xx-特殊函数-special-functions)
3. [40-XX 序列、级数、可和性 (Sequences, Series, Summability)](#40-xx-序列级数可和性-sequences-series-summability)
4. [41-XX 逼近与展开 (Approximations and Expansions)](#41-xx-逼近与展开-approximations-and-expansions)
5. [43-XX 抽象调和分析 (Abstract Harmonic Analysis)](#43-xx-抽象调和分析-abstract-harmonic-analysis)
6. [44-XX 积分变换与算子演算 (Integral Transforms, Operational Calculus)](#44-xx-积分变换与算子演算-integral-transforms-operational-calculus)
7. [45-XX 积分方程 (Integral Equations)](#45-xx-积分方程-integral-equations)

---

## 31-XX 位势论 (Potential Theory)

### 定义 I.31.1 (Newton位势 / Newtonian Potential)

**定义**: 设 $\mu$ 是 $\mathbb{R}^n$ 上具有紧支集的有限正Borel测度，$n \geq 3$。$\mu$ 的 **Newton位势** 定义为：

$$U^\mu(x) = \int_{\mathbb{R}^n} \frac{d\mu(y)}{|x-y|^{n-2}}, \quad x \in \mathbb{R}^n$$

对于 $n = 2$，**对数位势** (Logarithmic Potential) 定义为：

$$U^\mu(x) = \int_{\mathbb{R}^2} \log \frac{1}{|x-y|} d\mu(y)$$

**注**: Newton位势在 $\mathbb{R}^n \setminus \text{supp}(\mu)$ 上调和，满足 $\Delta U^\mu = -c_n \mu$（分布意义下）。

---

### 定义 I.31.2 (下调和函数 / Subharmonic Function)

**定义**: 设 $\Omega \subset \mathbb{R}^n$ 为区域。函数 $u: \Omega \to [-\infty, +\infty)$ 称为 **下调和函数**，如果：
1. $u$ 上半连续（usc）
2. 对任意 $\overline{B(x,r)} \subset \Omega$：

$$u(x) \leq \frac{1}{\sigma_{n-1}r^{n-1}} \int_{\partial B(x,r)} u \, d\sigma$$

其中 $\sigma_{n-1}$ 是单位球面的面积。

**等价条件**: $u \in L^1_{loc}(\Omega)$ 下调和当且仅当 $\Delta u \geq 0$（分布意义下）。

---

### 定理 31.1 (下调和函数的极大值原理 / Maximum Principle for Subharmonic Functions)

**定理**: 设 $u$ 在区域 $\Omega$ 上下调和。若 $u$ 在 $\Omega$ 内部达到全局最大值，则 $u$ 为常数。

**证明思路**: 
1. 设 $M = \sup_\Omega u$，$E = \{x \in \Omega : u(x) = M\}$
2. 由球面均值不等式，$E$ 是开集
3. 由上半连续性，$E$ 是闭集
4. $\Omega$ 连通，故 $E = \Omega$ 或 $E = \emptyset$ □

---

### 定义 I.31.3 (调和测度 / Harmonic Measure)

**定义**: 设 $\Omega \subset \mathbb{R}^n$ 为正则域（Green区域）。对每个 $x \in \Omega$，**调和测度** $\omega^x$ 是 $\partial \Omega$ 上的概率测度，使得对任意 $f \in C(\partial \Omega)$：

$$H_f(x) = \int_{\partial \Omega} f(y) \, d\omega^x(y)$$

是Dirichlet问题的唯一解（边界值 $f$）。

**注**: 当 $\Omega = \mathbb{D}$（单位圆盘），调和测度是Poisson积分的核。

---

### 定理 31.2 (Riesz分解定理 / Riesz Decomposition Theorem)

**定理**: 设 $u$ 在 $\Omega$ 上下调和且在紧集上有上界。则存在唯一的正测度 $\mu$ 使得：

$$u(x) = h(x) + U^\mu(x)$$

其中 $h$ 在 $\Omega$ 上调和，$U^\mu$ 是 $\mu$ 的Newton位势。

**证明**: 取 $\Delta u = \mu$（分布），令 $h = u - U^\mu$，则 $\Delta h = 0$。唯一性由Liouville定理保证。 □

---

### 定义 I.31.4 (容量 / Capacity)

**定义**: 设 $K \subset \mathbb{R}^n$ 紧。**Newton容量** (Newtonian Capacity) 定义为：

$$\text{cap}(K) = \sup\{\mu(K) : U^\mu(x) \leq 1 \text{ on } K, \mu \geq 0, \mu(K) < \infty\}$$

**等价定义** (Wiener容量，$n=2$):

$$\text{cap}(K) = \inf\left\{ \iint \log\frac{1}{|x-y|} d\mu(x) d\mu(y) : \mu \geq 0, \mu(K) = 1 \right\}^{-1}$$

**注**: 容量是"细"集合的测度。零容量集在位势论中是"可忽略"的。

---

### 定理 31.3 (Wiener准则 / Wiener Criterion)

**定理**: 设 $\Omega \subset \mathbb{R}^n$ 为有界域，$\xi \in \partial \Omega$。Dirichlet问题在 $\xi$ 处正则（即对任意 $f \in C(\partial \Omega)$，$H_f$ 连续到边界）当且仅当：

$$\sum_{k=1}^\infty \frac{\text{cap}(B(\xi, 2^{-k}) \cap \Omega^c)}{2^{-k(n-2)}} = \infty \quad (n \geq 3)$$

**意义**: 这是边界正则性的完全刻画。例如，锥是正则的，而足够尖锐的尖点是奇异的。

---

### 定义 I.31.5 (细拓扑 / Fine Topology)

**定义**: $\mathbb{R}^n$ 上的 **细拓扑** (Fine Topology) 是以所有下调和函数为局部下有界的子连续函数族定义的最粗拓扑。

等价地，$E$ 在 $\xi$ 处 **细薄** (thin) 如果存在下调和函数 $u$ 使得：

$$\limsup_{x \to \xi, x \in E} u(x) < u(\xi)$$

**细拓扑定理**: 细拓扑使下调和函数局部有上界，调和函数局部有界。

---

### 参考文献 (31-XX)
1. Helms, L.L., *Potential Theory*, Springer, 2009
2. Landkof, N.S., *Foundations of Modern Potential Theory*, Springer, 1972
3. Armitage, D.H., Gardiner, S.J., *Classical Potential Theory*, Springer, 2001
4. Doob, J.L., *Classical Potential Theory and Its Probabilistic Counterpart*, Springer, 1984

---

## 33-XX 特殊函数 (Special Functions)

### 定义 I.33.1 (Gamma函数 / Gamma Function)

**定义**: **Gamma函数** 是定义在 $\mathbb{C} \setminus \{0, -1, -2, \ldots\}$ 上的亚纯函数：

$$\Gamma(z) = \int_0^\infty t^{z-1} e^{-t} dt, \quad \text{Re}(z) > 0$$

**解析延拓**: 通过递推 $\Gamma(z+1) = z\Gamma(z)$ 延拓到整个复平面，在 $z = -n$（$n \in \mathbb{N}_0$）处有一阶极点。

**基本性质**:
- **函数方程**: $\Gamma(z+1) = z\Gamma(z)$，特别 $\Gamma(n+1) = n!$
- **互反公式**: $\Gamma(z)\Gamma(1-z) = \frac{\pi}{\sin \pi z}$
- **倍元公式**: $\Gamma(z)\Gamma(z+\frac{1}{2}) = 2^{1-2z}\sqrt{\pi}\,\Gamma(2z)$
- **乘积公式**: $\Gamma(z) = \frac{e^{-\gamma z}}{z} \prod_{n=1}^\infty \left(1 + \frac{z}{n}\right)^{-1} e^{z/n}$

---

### 定理 33.1 (Stirling渐近公式 / Stirling's Asymptotic Formula)

**定理**: 当 $|z| \to \infty$ 且 $|\arg z| < \pi - \delta$（$\delta > 0$）时：

$$\Gamma(z) \sim \sqrt{2\pi} \, z^{z-1/2} e^{-z} \left(1 + \frac{1}{12z} + \frac{1}{288z^2} + \cdots\right)$$

**特例** ($n \to \infty$):

$$n! \sim \sqrt{2\pi n} \left(\frac{n}{e}\right)^n \left(1 + \frac{1}{12n} + O(n^{-2})\right)$$

---

### 定义 I.33.2 (Beta函数 / Beta Function)

**定义**: **Beta函数** 定义为：

$$B(a,b) = \int_0^1 t^{a-1}(1-t)^{b-1} dt, \quad \text{Re}(a), \text{Re}(b) > 0$$

**与Gamma函数的关系**:

$$B(a,b) = \frac{\Gamma(a)\Gamma(b)}{\Gamma(a+b)}$$

**对称性**: $B(a,b) = B(b,a)$

**其他表示**:
- $B(a,b) = 2\int_0^{\pi/2} \sin^{2a-1}\theta \cos^{2b-1}\theta \, d\theta$
- $B(a,b) = \int_0^\infty \frac{t^{a-1}}{(1+t)^{a+b}} dt$

---

### 定义 I.33.3 (超几何函数 / Hypergeometric Function)

**定义**: **Gauss超几何函数** 定义为：

$${}_2F_1(a,b;c;z) = \sum_{n=0}^\infty \frac{(a)_n (b)_n}{(c)_n} \frac{z^n}{n!}, \quad |z| < 1$$

其中 $(a)_n = a(a+1)\cdots(a+n-1) = \Gamma(a+n)/\Gamma(a)$ 是Pochhammer符号。

**微分方程**: ${}_2F_1$ 满足 **超几何微分方程**:

$$z(1-z)w'' + [c-(a+b+1)z]w' - abw = 0$$

**Euler积分表示**:

$${}_2F_1(a,b;c;z) = \frac{\Gamma(c)}{\Gamma(b)\Gamma(c-b)} \int_0^1 t^{b-1}(1-t)^{c-b-1}(1-zt)^{-a} dt$$

---

### 定理 33.2 (超几何函数的变换公式 / Transformation Formulas for Hypergeometric Functions)

**定理**: 超几何函数满足以下变换：

1. **Pfaff变换**:
   $${}_2F_1(a,b;c;z) = (1-z)^{-a} {}_2F_1\left(a,c-b;c;\frac{z}{z-1}\right)$$

2. **Euler变换**:
   $${}_2F_1(a,b;c;z) = (1-z)^{c-a-b} {}_2F_1(c-a,c-b;c;z)$$

3. **二次变换**:
   $${}_2F_1\left(a,b;2b;z\right) = (1-z)^{-a} {}_2F_1\left(\frac{a}{2}, \frac{a+1}{2}; b+\frac{1}{2}; \frac{z^2}{4z-4}\right)$$

---

### 定义 I.33.4 (广义超几何函数 / Generalized Hypergeometric Function)

**定义**: **广义超几何函数** 定义为：

$${}_pF_q(a_1,\ldots,a_p; b_1,\ldots,b_q; z) = \sum_{n=0}^\infty \frac{(a_1)_n \cdots (a_p)_n}{(b_1)_n \cdots (b_q)_n} \frac{z^n}{n!}$$

**重要特例**:
- ${}_0F_0(;;z) = e^z$
- ${}_0F_1(;b;z)$ — 与Bessel函数相关
- ${}_1F_1(a;b;z)$ — 合流超几何函数（Kummer函数）
- ${}_2F_1(a,b;c;z)$ — Gauss超几何函数

---

### 定义 I.33.5 (Bessel函数 / Bessel Functions)

**定义**: **第一类Bessel函数** $J_\nu(z)$ 定义为：

$$J_\nu(z) = \sum_{n=0}^\infty \frac{(-1)^n}{n! \Gamma(n+\nu+1)} \left(\frac{z}{2}\right)^{2n+\nu}$$

**第二类Bessel函数** (Neumann函数) $Y_\nu(z)$ 定义为：

$$Y_\nu(z) = \frac{J_\nu(z)\cos(\nu\pi) - J_{-\nu}(z)}{\sin(\nu\pi)}, \quad \nu \notin \mathbb{Z}$$

通过极限延拓到整数 $\nu$。

**修正Bessel函数**:
- $I_\nu(z) = i^{-\nu} J_\nu(iz)$
- $K_\nu(z) = \frac{\pi}{2} \frac{I_{-\nu}(z) - I_\nu(z)}{\sin(\nu\pi)}$

---

### 定理 33.3 (Bessel函数的生成函数 / Generating Function for Bessel Functions)

**定理**:

$$\exp\left(\frac{z}{2}\left(t - \frac{1}{t}\right)\right) = \sum_{n=-\infty}^\infty J_n(z) t^n$$

**推论**: 整数阶Bessel函数满足：

$$J_n(z) = \frac{1}{\pi}\int_0^\pi \cos(n\theta - z\sin\theta) \, d\theta$$

---

### 定理 33.4 (Bessel函数的递推关系 / Recurrence Relations for Bessel Functions)

**定理**: Bessel函数满足：

1. $J_{\nu-1}(z) + J_{\nu+1}(z) = \frac{2\nu}{z} J_\nu(z)$
2. $J_{\nu-1}(z) - J_{\nu+1}(z) = 2J_\nu'(z)$
3. $J_\nu'(z) = J_{\nu-1}(z) - \frac{\nu}{z}J_\nu(z) = \frac{\nu}{z}J_\nu(z) - J_{\nu+1}(z)$

---

### 定义 I.33.6 (正交多项式 / Orthogonal Polynomials)

**定义**: 设 $w(x) \geq 0$ 是 $(a,b)$ 上的权函数。**正交多项式** $\{p_n(x)\}_{n=0}^\infty$ 满足：

$$\int_a^b p_n(x) p_m(x) w(x) dx = h_n \delta_{nm}$$

**三类经典正交多项式**:

| 多项式 | 区间 | 权函数 | 微分方程 |
|--------|------|--------|----------|
| Legendre $P_n(x)$ | $[-1,1]$ | $1$ | $(1-x^2)y'' - 2xy' + n(n+1)y = 0$ |
| Hermite $H_n(x)$ | $(-\infty,\infty)$ | $e^{-x^2}$ | $y'' - 2xy' + 2ny = 0$ |
| Laguerre $L_n^{(\alpha)}(x)$ | $(0,\infty)$ | $x^\alpha e^{-x}$ | $xy'' + (\alpha+1-x)y' + ny = 0$ |

---

### 定义 I.33.7 (Legendre多项式 / Legendre Polynomials)

**定义**: **Legendre多项式** 定义为：

$$P_n(x) = \frac{1}{2^n n!} \frac{d^n}{dx^n}[(x^2-1)^n] \quad \text{(Rodrigues公式)}$$

或等价地：

$$P_n(x) = {}_2F_1\left(-n, n+1; 1; \frac{1-x}{2}\right)$$

**正交性**:

$$\int_{-1}^1 P_n(x) P_m(x) dx = \frac{2}{2n+1} \delta_{nm}$$

**生成函数**:

$$\frac{1}{\sqrt{1-2xt+t^2}} = \sum_{n=0}^\infty P_n(x) t^n$$

---

### 定理 33.5 (Legendre多项式的加法定理 / Addition Theorem for Legendre Polynomials)

**定理**: 设 $\gamma$ 是单位向量 $\mathbf{x}$ 和 $\mathbf{y}$ 的夹角。则：

$$P_n(\cos\gamma) = P_n(\cos\theta_1)P_n(\cos\theta_2) + 2\sum_{k=1}^n \frac{(n-k)!}{(n+k)!} P_n^k(\cos\theta_1) P_n^k(\cos\theta_2) \cos k(\phi_1-\phi_2)$$

其中 $P_n^k$ 是连带Legendre函数。

---

### 定义 I.33.8 (Hermite多项式 / Hermite Polynomials)

**定义**: **Hermite多项式** 定义为：

$$H_n(x) = (-1)^n e^{x^2} \frac{d^n}{dx^n}(e^{-x^2}) \quad \text{(Rodrigues公式)}$$

**显式**:

$$H_n(x) = n! \sum_{k=0}^{\lfloor n/2 \rfloor} \frac{(-1)^k (2x)^{n-2k}}{k! (n-2k)!}$$

**正交性**:

$$\int_{-\infty}^\infty H_n(x) H_m(x) e^{-x^2} dx = \sqrt{\pi} 2^n n! \delta_{nm}$$

**生成函数**:

$$\exp(2xt - t^2) = \sum_{n=0}^\infty H_n(x) \frac{t^n}{n!}$$

---

### 定义 I.33.9 (Riemann ζ函数 / Riemann Zeta Function)

**定义**: **Riemann ζ函数** 在 $\text{Re}(s) > 1$ 时定义为：

$$\zeta(s) = \sum_{n=1}^\infty \frac{1}{n^s} = \prod_{p \text{ prime}} \frac{1}{1-p^{-s}}$$

**解析延拓**: $\zeta(s)$ 可亚纯延拓到 $\mathbb{C}$，在 $s=1$ 处有单极点，留数为 $1$。

**函数方程**:

$$\zeta(s) = 2^s \pi^{s-1} \sin\left(\frac{\pi s}{2}\right) \Gamma(1-s) \zeta(1-s)$$

或等价地：

$$\pi^{-s/2} \Gamma(s/2) \zeta(s) = \pi^{-(1-s)/2} \Gamma((1-s)/2) \zeta(1-s)$$

---

### 定理 33.6 (Riemann ζ函数的零点 / Zeros of Riemann Zeta Function)

**定理**: 
1. $\zeta(s)$ 的 **平凡零点** 在 $s = -2n$，$n \in \mathbb{N}$
2. **非平凡零点** 全部在 **临界带** $0 < \text{Re}(s) < 1$ 内
3. 若 $\rho$ 是非平凡零点，则 $1-\rho$、$\bar{\rho}$、$1-\bar{\rho}$ 也是零点

**Riemann假设** (未解决):

所有非平凡零点满足 $\text{Re}(\rho) = 1/2$。

**已知结果**:
- 至少 $41\%$ 的非平凡零点在临界线上（Selberg, Levinson, Conrey）
- 前约 $10^{13}$ 个零点都在临界线上（数值验证）

---

### 定义 I.33.10 (椭圆积分与椭圆函数 / Elliptic Integrals and Functions)

**第一类完全椭圆积分**:

$$K(k) = \int_0^{\pi/2} \frac{d\theta}{\sqrt{1-k^2\sin^2\theta}} = \frac{\pi}{2} {}_2F_1\left(\frac{1}{2}, \frac{1}{2}; 1; k^2\right)$$

**第二类完全椭圆积分**:

$$E(k) = \int_0^{\pi/2} \sqrt{1-k^2\sin^2\theta} \, d\theta = \frac{\pi}{2} {}_2F_1\left(-\frac{1}{2}, \frac{1}{2}; 1; k^2\right)$$

**Weierstrass ℘函数**: 由以下性质唯一确定：
- 双周期：$\wp(z + 2\omega_1) = \wp(z + 2\omega_2) = \wp(z)$
- 在 $0$ 处主部 $1/z^2$
- 偶函数

满足微分方程：

$$\wp'(z)^2 = 4\wp(z)^3 - g_2 \wp(z) - g_3$$

---

### 定义 I.33.11 (Airy函数 / Airy Functions)

**定义**: **Airy函数** $\text{Ai}(x)$ 和 $\text{Bi}(x)$ 是微分方程

$$y'' - xy = 0$$

的两个线性无关解。

**积分表示**:

$$\text{Ai}(x) = \frac{1}{\pi} \int_0^\infty \cos\left(\frac{t^3}{3} + xt\right) dt$$

**渐近行为**:
- 当 $x \to +\infty$: $\text{Ai}(x) \sim \frac{1}{2\sqrt{\pi}} x^{-1/4} \exp\left(-\frac{2}{3}x^{3/2}\right)$
- 当 $x \to -\infty$: $\text{Ai}(x) \sim \frac{1}{\sqrt{\pi}} |x|^{-1/4} \sin\left(\frac{2}{3}|x|^{3/2} + \frac{\pi}{4}\right)$

**应用**: WKB近似中的转折点、光学中的彩虹散射、随机矩阵理论中的Tracy-Widom分布。

---

### 参考文献 (33-XX)
1. Andrews, G.E., Askey, R., Roy, R., *Special Functions*, Cambridge, 1999
2. Whittaker, E.T., Watson, G.N., *A Course of Modern Analysis*, Cambridge, 1927
3. Gradshteyn, I.S., Ryzhik, I.M., *Table of Integrals, Series, and Products*, Academic Press
4. Olver, F.W.J. et al., *NIST Handbook of Mathematical Functions*, Cambridge, 2010
5. Temme, N.M., *Special Functions: An Introduction to the Classical Functions of Mathematical Physics*, Wiley, 1996

---

## 40-XX 序列、级数、可和性 (Sequences, Series, Summability)

### 定义 I.40.1 (级数的收敛 / Convergence of Series)

**定义**: 级数 $\sum_{n=1}^\infty a_n$ **收敛** 如果部分和序列 $s_N = \sum_{n=1}^N a_n$ 收敛。极限 $s = \lim_{N\to\infty} s_N$ 称为级数的 **和**。

**Cauchy收敛准则**: $\sum a_n$ 收敛当且仅当

$$\forall \epsilon > 0, \exists N: \forall m > n \geq N, \left|\sum_{k=n+1}^m a_k\right| < \epsilon$$

---

### 定理 40.1 (收敛的必要条件 / Necessary Condition for Convergence)

**定理**: 若 $\sum a_n$ 收敛，则 $\lim_{n\to\infty} a_n = 0$。

**注**: 逆命题不成立（调和级数反例：$\sum 1/n$ 发散）。

---

### 定理 40.2 (正项级数的比较判别法 / Comparison Test)

**定理**: 设 $a_n, b_n \geq 0$。

1. 若 $a_n \leq b_n$ 且 $\sum b_n$ 收敛，则 $\sum a_n$ 收敛
2. 若 $a_n \geq b_n$ 且 $\sum b_n$ 发散，则 $\sum a_n$ 发散

**极限形式**: 若 $\lim_{n\to\infty} a_n/b_n = L \in (0, \infty)$，则 $\sum a_n$ 和 $\sum b_n$ 同敛散。

---

### 定理 40.3 (比值判别法 / Ratio Test, d'Alembert)

**定理**: 设 $a_n \neq 0$，$L = \lim_{n\to\infty} |a_{n+1}/a_n|$。

- 若 $L < 1$，则 $\sum a_n$ 绝对收敛
- 若 $L > 1$，则 $\sum a_n$ 发散
- 若 $L = 1$，判别法失效

---

### 定理 40.4 (根值判别法 / Root Test, Cauchy)

**定理**: 设 $L = \limsup_{n\to\infty} \sqrt[n]{|a_n|}$。

- 若 $L < 1$，则 $\sum a_n$ 绝对收敛
- 若 $L > 1$，则 $\sum a_n$ 发散
- 若 $L = 1$，判别法失效

---

### 定理 40.5 (积分判别法 / Integral Test, Maclaurin-Cauchy)

**定理**: 设 $f: [1, \infty) \to [0, \infty)$ 单调递减。则 $\sum_{n=1}^\infty f(n)$ 收敛当且仅当 $\int_1^\infty f(x) dx$ 收敛。

**应用**: $p$-级数 $\sum 1/n^p$ 当 $p > 1$ 时收敛，$p \leq 1$ 时发散。

---

### 定义 I.40.2 (条件收敛与绝对收敛 / Conditional and Absolute Convergence)

**定义**:
- **绝对收敛**: $\sum |a_n|$ 收敛
- **条件收敛**: $\sum a_n$ 收敛但 $\sum |a_n|$ 发散

**注**: 绝对收敛蕴含收敛，但反之不然。

---

### 定理 40.6 (Riemann重排定理 / Riemann Rearrangement Theorem)

**定理**: 若 $\sum a_n$ 条件收敛，则对任意 $S \in [-\infty, +\infty]$，存在重排 $\sigma: \mathbb{N} \to \mathbb{N}$ 使得 $\sum a_{\sigma(n)} = S$。

**证明思路**: 
1. 正项级数发散到 $+\infty$，负项级数发散到 $-\infty$
2. 交错取正负项以逼近目标值 □

**注**: 绝对收敛级数对任意重排保持其和不变。

---

### 定理 40.7 (Dirichlet判别法 / Dirichlet Test)

**定理**: 设 $(a_n)$ 单调趋于 $0$，$(b_n)$ 的部分和有界。则 $\sum a_n b_n$ 收敛。

**推论** (Abel判别法): 若 $(a_n)$ 单调有界，$\sum b_n$ 收敛，则 $\sum a_n b_n$ 收敛。

---

### 定义 I.40.3 (交错级数 / Alternating Series)

**定义**: **交错级数** 形如 $\sum_{n=1}^\infty (-1)^{n-1} a_n$ 或 $\sum_{n=1}^\infty (-1)^n a_n$，其中 $a_n > 0$。

---

### 定理 40.8 (Leibniz判别法 / Leibniz Test)

**定理**: 若 $(a_n)$ 单调递减趋于 $0$，则交错级数 $\sum (-1)^{n-1} a_n$ 收敛，且：

$$\left|s - s_N\right| \leq a_{N+1}$$

其中 $s$ 是级数的和，$s_N$ 是第 $N$ 个部分和。

---

### 定义 I.40.4 (可和性方法 / Summability Methods)

**问题**: 如何给发散级数赋予"广义和"？

**Cesàro可和**: 级数 $\sum a_n$ 的 **Cesàro和** 定义为

$$C\text{-}\sum a_n = \lim_{N\to\infty} \frac{1}{N} \sum_{k=1}^N s_k$$

如果极限存在。

**注**: 若级数通常收敛到 $s$，则其Cesàro和也是 $s$（正则性）。

---

### 定理 40.9 (Fejér定理 / Fejér's Theorem)

**定理**: 设 $f$ 是 $2\pi$-周期连续函数，$S_n(f)$ 是其Fourier级数的第 $n$ 个部分和。则Cesàro平均

$$\sigma_N(f)(x) = \frac{1}{N} \sum_{n=0}^{N-1} S_n(f)(x)$$

一致收敛到 $f$。

**意义**: Fourier级数可能发散，但Cesàro平均总是收敛。

---

### 定义 I.40.5 (Abel可和 / Abel Summability)

**定义**: 级数 $\sum a_n$ 的 **Abel和** 定义为

$$A\text{-}\sum a_n = \lim_{r \to 1^-} \sum_{n=0}^\infty a_n r^n$$

如果极限存在。

**定理**: Abel可和蕴含Cesàro可和，且两者相等。

---

### 定理 40.10 (Tauber型定理 / Tauberian Theorems)

**定理** (Tauber): 若 $\sum a_n$ Abel可和到 $s$，且 $a_n = o(1/n)$，则 $\sum a_n$ 通常收敛到 $s$。

**定理** (Hardy-Littlewood): 若 $\sum a_n$ Abel可和到 $s$，且 $a_n = O(1/n)$，则 $\sum a_n$ 通常收敛到 $s$。

**意义**: 在"小"条件下，Abel可和蕴含通常收敛。

---

### 定义 I.40.6 (二重级数 / Double Series)

**定义**: **二重级数** $\sum_{m,n} a_{mn}$ 的和定义为

$$\lim_{M,N \to \infty} \sum_{m=1}^M \sum_{n=1}^N a_{mn}$$

如果极限存在。

**Fubini定理**: 若 $\sum_{m,n} |a_{mn}| < \infty$，则

$$\sum_{m,n} a_{mn} = \sum_m \sum_n a_{mn} = \sum_n \sum_m a_{mn}$$

---

### 定义 I.40.7 (无穷乘积 / Infinite Products)

**定义**: **无穷乘积** $\prod_{n=1}^\infty (1 + a_n)$ 收敛，如果部分积 $P_N = \prod_{n=1}^N (1+a_n)$ 收敛到非零极限。

**定理**: 若 $a_n \geq 0$，则 $\prod(1+a_n)$ 收敛当且仅当 $\sum a_n$ 收敛。

**对数判别法**: 若 $\sum |a_n|$ 收敛且 $\sum a_n^2$ 收敛，则 $\prod(1+a_n)$ 收敛。

---

### 参考文献 (40-XX)
1. Knopp, K., *Theory and Application of Infinite Series*, Dover, 1990
2. Hardy, G.H., *Divergent Series*, AMS Chelsea, 1991
3. Zygmund, A., *Trigonometric Series*, Cambridge, 2002
4. Korevaar, J., *Tauberian Theory: A Century of Developments*, Springer, 2004

---

## 41-XX 逼近与展开 (Approximations and Expansions)

### 定义 I.41.1 (最佳逼近 / Best Approximation)

**定义**: 设 $f \in C[a,b]$，$V \subset C[a,b]$ 是子空间。$p^* \in V$ 称为 $f$ 的 **最佳一致逼近** (Best Uniform Approximation)，如果

$$\|f - p^*\|_\infty = \inf_{p \in V} \|f - p\|_\infty$$

**存在性**: 若 $V$ 是有限维闭子空间，最佳逼近存在。

**唯一性**: 若 $V$ 是Haar子空间（如多项式空间），最佳逼近唯一。

---

### 定理 41.1 (Chebyshev交错定理 / Chebyshev Alternation Theorem)

**定理**: 设 $f \in C[a,b]$，$P_n$ 是次数 $\leq n$ 的多项式空间。$p^* \in P_n$ 是 $f$ 的最佳一致逼近当且仅当存在 $n+2$ 个点

$$a \leq x_0 < x_1 < \cdots < x_{n+1} \leq b$$

使得

$$f(x_i) - p^*(x_i) = (-1)^i \sigma \|f - p^*\|_\infty, \quad \sigma = \pm 1$$

**意义**: 误差函数在 $n+2$ 个点达到最大值且符号交错。

---

### 定义 I.41.2 (Chebyshev多项式 / Chebyshev Polynomials)

**定义**: **第一类Chebyshev多项式** $T_n(x)$ 定义为：

$$T_n(x) = \cos(n \arccos x), \quad x \in [-1, 1]$$

**显式**: $T_n(x) = \frac{n}{2} \sum_{k=0}^{\lfloor n/2 \rfloor} (-1)^k \frac{(n-k-1)!}{k!(n-2k)!} (2x)^{n-2k}$

**递推关系**:

$$T_{n+1}(x) = 2x T_n(x) - T_{n-1}(x), \quad T_0 = 1, \, T_1 = x$$

**极值性质**: 在所有首一 $n$ 次多项式中，$2^{1-n} T_n(x)$ 在 $[-1,1]$ 上的最大模最小。

---

### 定义 I.41.3 (最小二乘逼近 / Least Squares Approximation)

**定义**: 设 $f \in L^2[a,b]$，$V$ 是有限维子空间。$p^* \in V$ 称为 $f$ 的 **最小二乘逼近**，如果

$$\|f - p^*\|_2 = \inf_{p \in V} \|f - p\|_2$$

**正规方程**: 设 $\{\phi_1, \ldots, \phi_n\}$ 是 $V$ 的基。则 $p^* = \sum c_j \phi_j$ 的系数满足

$$\sum_{j=1}^n c_j \langle \phi_j, \phi_k \rangle = \langle f, \phi_k \rangle, \quad k = 1, \ldots, n$$

---

### 定理 41.2 (Gram-Schmidt正交化 / Gram-Schmidt Orthogonalization)

**定理**: 设 $\{f_1, \ldots, f_n\}$ 是 $L^2[a,b]$ 中的线性无关组。则存在正交组 $\{g_1, \ldots, g_n\}$ 使得 $\text{span}\{f_1, \ldots, f_k\} = \text{span}\{g_1, \ldots, g_k\}$ 对所有 $k$。

**算法**:
$$g_1 = f_1, \quad g_k = f_k - \sum_{j=1}^{k-1} \frac{\langle f_k, g_j \rangle}{\langle g_j, g_j \rangle} g_j$$

**Legendre多项式**: 通过Gram-Schmidt作用于 $\{1, x, x^2, \ldots\}$ 得到。

---

### 定义 I.41.4 (插值 / Interpolation)

**定义**: 给定节点 $x_0 < x_1 < \cdots < x_n$ 和函数值 $f(x_i)$，**插值多项式** $p_n(x)$ 满足

$$p_n(x_i) = f(x_i), \quad i = 0, 1, \ldots, n$$

**Lagrange形式**:

$$p_n(x) = \sum_{i=0}^n f(x_i) \ell_i(x), \quad \ell_i(x) = \prod_{j \neq i} \frac{x - x_j}{x_i - x_j}$$

**Newton形式**:

$$p_n(x) = f[x_0] + \sum_{k=1}^n f[x_0, \ldots, x_k] \prod_{j=0}^{k-1} (x - x_j)$$

其中 $f[x_0, \ldots, x_k]$ 是 **差商** (Divided Difference)。

---

### 定理 41.3 (插值误差 / Interpolation Error)

**定理**: 设 $f \in C^{n+1}[a,b]$，$p_n$ 是 $f$ 在节点 $x_0, \ldots, x_n \in [a,b]$ 上的插值多项式。则

$$f(x) - p_n(x) = \frac{f^{(n+1)}(\xi_x)}{(n+1)!} \prod_{i=0}^n (x - x_i)$$

其中 $\xi_x \in [a,b]$ 依赖于 $x$。

**推论**: 若 $M = \max_{[a,b]} |f^{(n+1)}|$，则

$$\|f - p_n\|_\infty \leq \frac{M}{(n+1)!} \|\omega_n\|_\infty$$

其中 $\omega_n(x) = \prod_{i=0}^n (x - x_i)$。

---

### 定理 41.4 (Runge现象 / Runge's Phenomenon)

**定理**: 考虑函数 $f(x) = 1/(1+25x^2)$ 在 $[-1,1]$ 上的等距节点插值。当 $n \to \infty$ 时，

$$\max_{x \in [-1,1]} |f(x) - p_n(x)| \to \infty$$

**解释**: 等距节点不是最优选择。

**解决方案**: 使用Chebyshev节点 $x_k = \cos\left(\frac{2k+1}{2n+2}\pi\right)$，$k = 0, 1, \ldots, n$。

---

### 定义 I.41.5 (样条函数 / Spline Functions)

**定义**: 设 $a = x_0 < x_1 < \cdots < x_N = b$ 是分划。**三次样条** (Cubic Spline) $s(x)$ 是满足以下条件的函数：
1. $s \in C^2[a,b]$
2. 在每个子区间 $[x_i, x_{i+1}]$ 上，$s$ 是三次多项式

**自然边界条件**: $s''(a) = s''(b) = 0$

**存在唯一性**: 给定函数值 $y_i = f(x_i)$ 和自然边界条件，三次样条存在唯一。

---

### 定理 41.5 (样条的最小曲率性质 / Minimum Curvature Property of Splines)

**定理**: 设 $s$ 是 $f$ 在节点 $x_0, \ldots, x_N$ 上的自然三次样条。则对任意 $g \in C^2[a,b]$ 满足 $g(x_i) = f(x_i)$，有

$$\int_a^b [s''(x)]^2 dx \leq \int_a^b [g''(x)]^2 dx$$

**意义**: 在所有插值函数中，样条的"弯曲程度"最小。

---

### 定义 I.41.6 (Padé逼近 / Padé Approximant)

**定义**: 设 $f$ 在 $0$ 处有Taylor展开。$f$ 的 **$(m,n)$-Padé逼近** 是有理函数

$$R_{m,n}(x) = \frac{P_m(x)}{Q_n(x)} = \frac{a_0 + a_1 x + \cdots + a_m x^m}{1 + b_1 x + \cdots + b_n x^n}$$

使得

$$f(x) - R_{m,n}(x) = O(x^{m+n+1}), \quad x \to 0$$

**注**: Padé逼近往往比Taylor多项式有更大的收敛范围。

---

### 定理 41.6 (Weierstrass逼近定理 / Weierstrass Approximation Theorem)

**定理**: 设 $f \in C[a,b]$，$\epsilon > 0$。则存在多项式 $p$ 使得

$$\|f - p\|_\infty < \epsilon$$

**等价陈述**: 多项式在 $(C[a,b], \|\cdot\|_\infty)$ 中稠密。

**证明方法**:
1. Bernstein多项式: $B_n(f)(x) = \sum_{k=0}^n f(k/n) \binom{n}{k} x^k (1-x)^{n-k}$
2. Stone-Weierstrass定理

---

### 定义 I.41.7 (Bernstein多项式 / Bernstein Polynomials)

**定义**: 对于 $f \in C[0,1]$，**Bernstein多项式** 定义为：

$$B_n(f)(x) = \sum_{k=0}^n f\left(\frac{k}{n}\right) \binom{n}{k} x^k (1-x)^{n-k}$$

**性质**:
1. $B_n(f)$ 是次数 $\leq n$ 的多项式
2. $B_n(1) = 1$, $B_n(x) = x$, $B_n(x^2) = x^2 + \frac{x(1-x)}{n}$
3. 若 $f$ 是 $k$ 次多项式，则 $B_n(f) \to f$ 当 $n \to \infty$

---

### 定理 41.7 (Bernstein逼近定理 / Bernstein Approximation Theorem)

**定理**: 设 $f \in C[0,1]$。则 $B_n(f) \to f$ 在 $[0,1]$ 上一致收敛。

**收敛速度**: 若 $f \in C^1[0,1]$，则

$$\|B_n(f) - f\|_\infty \leq \frac{5}{4\sqrt{n}} \omega_f\left(\frac{1}{\sqrt{n}}\right)$$

其中 $\omega_f$ 是 $f$ 的连续模。

---

### 定义 I.41.8 (连续模 / Modulus of Continuity)

**定义**: 函数 $f \in C[a,b]$ 的 **连续模** 定义为：

$$\omega_f(\delta) = \sup\{|f(x) - f(y)| : |x - y| \leq \delta, x,y \in [a,b]\}$$

**性质**:
1. $\omega_f(\delta) \to 0$ 当 $\delta \to 0$（$f$ 一致连续）
2. $\omega_f$ 是 $\delta$ 的单调递增函数
3. 若 $f \in \text{Lip}_\alpha$，则 $\omega_f(\delta) \leq C \delta^\alpha$

---

### 定理 41.8 (Jackson定理 / Jackson's Theorem)

**定理**: 设 $f \in C[-1,1]$，$E_n(f)$ 是 $f$ 用次数 $\leq n$ 的多项式最佳逼近的误差。则

$$E_n(f) \leq C \omega_f\left(\frac{1}{n}\right)$$

其中 $C$ 是绝对常数。

**更精确形式**: 若 $f \in C^r[-1,1]$，则

$$E_n(f) \leq \frac{C_r}{n^r} \omega_{f^{(r)}}\left(\frac{1}{n}\right)$$

---

### 参考文献 (41-XX)
1. Cheney, E.W., *Introduction to Approximation Theory*, AMS Chelsea, 1998
2. DeVore, R.A., Lorentz, G.G., *Constructive Approximation*, Springer, 1993
3. Powell, M.J.D., *Approximation Theory and Methods*, Cambridge, 1981
4. Davis, P.J., *Interpolation and Approximation*, Dover, 1975
5. Braess, D., *Nonlinear Approximation Theory*, Springer, 1986

---

## 43-XX 抽象调和分析 (Abstract Harmonic Analysis)

### 定义 I.43.1 (局部紧群 / Locally Compact Group)

**定义**: **局部紧群** $G$ 是一个群，同时是局部紧Hausdorff拓扑空间，且群运算

$$(x, y) \mapsto xy, \quad x \mapsto x^{-1}$$

是连续的。

**重要例子**:
- $\mathbb{R}^n$（加法）
- $\mathbb{T} = \{z \in \mathbb{C} : |z| = 1\}$（乘法）
- 有限群（离散拓扑）
- $GL_n(\mathbb{R})$（一般线性群）

---

### 定义 I.43.2 (Haar测度 / Haar Measure)

**定义**: 局部紧群 $G$ 上的 **Haar测度** $\mu$ 是（非零）正则Borel测度，满足 **左不变性**：

$$\mu(xE) = \mu(E), \quad \forall x \in G, E \subset G \text{ Borel}$$

**定理** (Haar, Weil, von Neumann): Haar测度存在且在相差常数因子下唯一。

**例子**:
- $\mathbb{R}^n$: Lebesgue测度
- $\mathbb{T}$: 规范化弧长测度 $d\theta/2\pi$
- 有限群 $G$: 计数测度除以 $|G|$

---

### 定义 I.43.3 (群代数 / Group Algebra)

**定义**: **群代数** $L^1(G)$ 是配备卷积

$$(f * g)(x) = \int_G f(y) g(y^{-1}x) d\mu(y)$$

的Banach代数，范数为

$$\|f\|_1 = \int_G |f(x)| d\mu(x)$$

**性质**:
- $L^1(G)$ 是Banach代数（一般不对易）
- 对易当且仅当 $G$ 是交换群

---

### 定义 I.43.4 (对偶群 / Dual Group)

**定义**: 局部紧交换群 $G$ 的 **对偶群**（特征群）$\hat{G}$ 是所有连续同态

$$\chi: G \to \mathbb{T}$$

构成的群，配备紧-开拓扑。

**运算**: $(\chi_1 \chi_2)(x) = \chi_1(x) \chi_2(x)$

**例子**:
- $\hat{\mathbb{R}} \cong \mathbb{R}$，$\chi_\xi(x) = e^{2\pi i \xi x}$
- $\hat{\mathbb{T}} \cong \mathbb{Z}$，$\chi_n(e^{i\theta}) = e^{in\theta}$
- $\hat{\mathbb{Z}} \cong \mathbb{T}$
- $\widehat{\mathbb{Z}_n} \cong \mathbb{Z}_n$

---

### 定义 I.43.5 (Fourier变换 / Fourier Transform on Groups)

**定义**: 设 $G$ 是局部紧交换群，$f \in L^1(G)$。**Fourier变换** $\hat{f}: \hat{G} \to \mathbb{C}$ 定义为：

$$\hat{f}(\chi) = \int_G f(x) \overline{\chi(x)} d\mu(x)$$

**反演公式**: 在适当条件下，

$$f(x) = \int_{\hat{G}} \hat{f}(\chi) \chi(x) d\hat{\mu}(\chi)$$

其中 $\hat{\mu}$ 是 $\hat{G}$ 上的Haar测度（适当规范化）。

---

### 定理 43.1 (Pontryagin对偶定理 / Pontryagin Duality Theorem)

**定理**: 设 $G$ 是局部紧交换群。则自然映射

$$G \to \hat{\hat{G}}, \quad x \mapsto (\chi \mapsto \chi(x))$$

是拓扑群同构。

**意义**: $G$ 和 $\hat{G}$ 互为对偶。

**推论**:
1. $G$ 是紧群当且仅当 $\hat{G}$ 是离散群
2. $G$ 是离散群当且仅当 $\hat{G}$ 是紧群

---

### 定理 43.2 (Plancherel定理 / Plancherel Theorem)

**定理**: 设 $G$ 是局部紧交换群，Haar测度适当规范化。则Fourier变换

$$\mathcal{F}: L^1(G) \cap L^2(G) \to L^2(\hat{G})$$

可唯一延拓为酉算子 $\mathcal{F}: L^2(G) \to L^2(\hat{G})$。

**等价陈述**:

$$\int_G |f(x)|^2 d\mu(x) = \int_{\hat{G}} |\hat{f}(\chi)|^2 d\hat{\mu}(\chi)$$

---

### 定理 43.3 (Bochner定理 / Bochner's Theorem)

**定理**: 设 $\phi: G \to \mathbb{C}$ 是局部紧交换群上的连续函数。$\phi$ 是某个正有限测度的Fourier变换（即 $\phi$ 是 **正定型**）当且仅当：
1. $\phi(0) \geq 0$
2. $\phi(x^{-1}) = \overline{\phi(x)}$
3. 对任意 $x_1, \ldots, x_n \in G$ 和 $c_1, \ldots, c_n \in \mathbb{C}$：

$$\sum_{i,j} c_i \overline{c_j} \phi(x_i^{-1} x_j) \geq 0$$

**意义**: 正定型函数 = 测度的Fourier变换。

---

### 定义 I.43.6 (群表示 / Group Representation)

**定义**: 局部紧群 $G$ 的 **酉表示** 是连续群同态

$$\pi: G \to \mathcal{U}(H)$$

其中 $H$ 是Hilbert空间，$\mathcal{U}(H)$ 是酉算子群。

**对偶**（非交换情况）: $\hat{G}$ 是 $G$ 的所有不可约酉表示的等价类。

---

### 定义 I.43.7 (群C*-代数 / Group C*-Algebra)

**完全群C*-代数**: $C^*(G)$ 是 $L^1(G)$ 在范数

$$\|f\|_{C^*} = \sup_{\pi} \|\pi(f)\|$$

下的完备化，sup取遍所有酉表示 $\pi$。

**约化群C*-代数**: $C^*_r(G)$ 是 $L^1(G)$ 在 $L^2(G)$ 上的左正则表示下的像。

**交换情况**: 若 $G$ 是交换群，$C^*(G) \cong C_0(\hat{G})$（Gelfand-Naimark）。

---

### 定理 43.4 (Peter-Weyl定理 / Peter-Weyl Theorem)

**定理**: 设 $G$ 是紧群。则：
1. 每个不可约表示是有限维的
2. $L^2(G) \cong \bigoplus_{\pi \in \hat{G}} (H_\pi \otimes H_\pi^*)$
3. 矩阵系数 $\{\sqrt{d_\pi} \pi_{ij}\}$ 构成 $L^2(G)$ 的正交基

**特例**（$G = \mathbb{T}$）: Fourier级数展开

$$f(e^{i\theta}) = \sum_{n \in \mathbb{Z}} \hat{f}(n) e^{in\theta}$$

---

### 定义 I.43.8 (卷积与平移 / Convolution and Translation)

**卷积**: 对于 $f, g \in L^1(G)$，

$$(f * g)(x) = \int_G f(y) g(y^{-1}x) d\mu(y) = \int_G f(xy^{-1}) g(y) d\mu(y)$$

**平移**: $(L_y f)(x) = f(y^{-1}x)$，$(R_y f)(x) = f(xy)$

**Young不等式**:

$$\|f * g\|_r \leq \|f\|_p \|g\|_q, \quad 1 + \frac{1}{r} = \frac{1}{p} + \frac{1}{q}$$

---

### 定理 43.5 (Wiener Tauberian定理 / Wiener's Tauberian Theorem)

**定理**: 设 $G$ 是局部紧交换群，$f \in L^1(G)$。若 $\hat{f}$ 在 $\hat{G}$ 上无零点，则理想

$$I_f = \{f * g : g \in L^1(G)\}$$

在 $L^1(G)$ 中稠密。

**等价形式**: $\{g \in L^1(G) : \hat{g}(\chi) = 0 \text{ 当 } \hat{f}(\chi) = 0\}$ 的平移张成 $L^1(G)$。

**推论**: 若 $\hat{f}$ 无零点，则 $\{f * g : g \in L^1(G)\}$ 的闭包 = $L^1(G)$。

---

### 参考文献 (43-XX)
1. Hewitt, E., Ross, K.A., *Abstract Harmonic Analysis*, Vol. I-II, Springer
2. Rudin, W., *Fourier Analysis on Groups*, Wiley, 1990
3. Folland, G.B., *A Course in Abstract Harmonic Analysis*, CRC, 1995
4. Reiter, H., Stegemann, J.D., *Classical Harmonic Analysis and Locally Compact Groups*, Oxford, 2000

---

## 44-XX 积分变换与算子演算 (Integral Transforms, Operational Calculus)

### 定义 I.44.1 (积分变换 / Integral Transform)

**定义**: **积分变换** 是形如

$$(Tf)(s) = \int_a^b K(s, t) f(t) dt$$

的线性算子，其中 $K(s, t)$ 是 **核函数** (Kernel)。

**重要例子**:
| 变换 | 核函数 | 定义域 |
|------|--------|--------|
| Fourier | $e^{-2\pi i st}$ | $\mathbb{R}$ |
| Laplace | $e^{-st}$ | $[0, \infty)$ |
| Mellin | $t^{s-1}$ | $(0, \infty)$ |
| Hankel | $t J_\nu(st)$ | $(0, \infty)$ |
| Hilbert | $\frac{1}{\pi(t-s)}$ | $\mathbb{R}$ |

---

### 定义 I.44.2 (Laplace变换 / Laplace Transform)

**定义**: 函数 $f: [0, \infty) \to \mathbb{C}$ 的 **Laplace变换** 定义为：

$$\mathcal{L}\{f\}(s) = F(s) = \int_0^\infty e^{-st} f(t) dt, \quad \text{Re}(s) > \sigma_c$$

其中 $\sigma_c$ 是 **收敛横坐标**（abscissa of convergence）。

**存在性**: 若 $|f(t)| \leq Me^{\sigma_0 t}$，则 $\mathcal{L}\{f\}$ 在 $\text{Re}(s) > \sigma_0$ 收敛。

---

### 定理 44.1 (Laplace变换的基本性质 / Basic Properties of Laplace Transform)

**定理**:
1. **线性性**: $\mathcal{L}\{af + bg\} = a\mathcal{L}\{f\} + b\mathcal{L}\{g\}$
2. **位移**: $\mathcal{L}\{e^{at}f(t)\}(s) = F(s-a)$
3. **延迟**: $\mathcal{L}\{f(t-a)u(t-a)\}(s) = e^{-as}F(s)$（$u$ 是单位阶跃）
4. **尺度变换**: $\mathcal{L}\{f(at)\}(s) = \frac{1}{a}F(s/a)$
5. **微分**: $\mathcal{L}\{f'(t)\}(s) = sF(s) - f(0)$
6. **积分**: $\mathcal{L}\{\int_0^t f(\tau)d\tau\}(s) = \frac{F(s)}{s}$
7. **卷积**: $\mathcal{L}\{f * g\}(s) = F(s) G(s)$

---

### 定理 44.2 (Laplace逆变换 / Inverse Laplace Transform)

**定理** (Bromwich积分): 设 $F(s)$ 在 $\text{Re}(s) > \sigma$ 解析，则

$$f(t) = \frac{1}{2\pi i} \int_{\sigma-i\infty}^{\sigma+i\infty} e^{st} F(s) ds, \quad t > 0$$

**部分分式**: 若 $F(s) = P(s)/Q(s)$ 是有理函数，可用部分分式分解求逆。

---

### 定义 I.44.3 (Mellin变换 / Mellin Transform)

**定义**: 函数 $f: (0, \infty) \to \mathbb{C}$ 的 **Mellin变换** 定义为：

$$\mathcal{M}\{f\}(s) = \int_0^\infty x^{s-1} f(x) dx$$

**与Fourier/Laplace变换的关系**:

$$\mathcal{M}\{f\}(s) = \mathcal{L}\{f(e^{-t})\}(s)$$

**应用**: 解析数论（Dirichlet级数）、特殊函数的渐近分析。

---

### 定理 44.3 (Mellin反演公式 / Mellin Inversion Formula)

**定理**: 若 $\mathcal{M}\{f\}(s)$ 在带 $a < \text{Re}(s) < b$ 内解析且适当衰减，则

$$f(x) = \frac{1}{2\pi i} \int_{c-i\infty}^{c+i\infty} x^{-s} \mathcal{M}\{f\}(s) ds, \quad a < c < b$$

---

### 定义 I.44.4 (Hankel变换 / Hankel Transform)

**定义**: 函数 $f: (0, \infty) \to \mathbb{C}$ 的 **$\nu$阶Hankel变换** 定义为：

$$\mathcal{H}_\nu\{f\}(s) = \int_0^\infty x J_\nu(sx) f(x) dx$$

其中 $J_\nu$ 是第一类Bessel函数。

**自反演性**:

$$f(x) = \int_0^\infty s J_\nu(sx) \mathcal{H}_\nu\{f\}(s) ds$$

**应用**: 圆柱坐标系下的偏微分方程。

---

### 定义 I.44.5 (Hilbert变换 / Hilbert Transform)

**定义**: 函数 $f \in L^p(\mathbb{R})$（$1 \leq p < \infty$）的 **Hilbert变换** 定义为：

$$\mathcal{H}\{f\}(x) = \frac{1}{\pi} \text{p.v.} \int_{-\infty}^\infty \frac{f(t)}{t-x} dt = \lim_{\epsilon \to 0} \frac{1}{\pi} \int_{|t-x|>\epsilon} \frac{f(t)}{t-x} dt$$

---

### 定理 44.4 (Hilbert变换的范数 / Norm of Hilbert Transform)

**定理** (M. Riesz): Hilbert变换在 $L^p(\mathbb{R})$ 上有界（$1 < p < \infty$）：

$$\|\mathcal{H}f\|_p \leq C_p \|f\|_p$$

**注**: 当 $p = 1$ 或 $p = \infty$ 时，Hilbert变换无界。

---

### 定理 44.5 (Hilbert变换与Fourier变换 / Hilbert Transform and Fourier Transform)

**定理**:

$$\widehat{\mathcal{H}f}(\xi) = -i \,\text{sgn}(\xi) \hat{f}(\xi)$$

**推论**: $\mathcal{H}^2 f = -f$（在 $L^2$ 中）。

**意义**: Hilbert变换是乘以 $-i\,\text{sgn}(\xi)$ 的Fourier乘子。

---

### 定义 I.44.6 (Radon变换 / Radon Transform)

**定义**: 函数 $f: \mathbb{R}^n \to \mathbb{C}$ 的 **Radon变换** 定义为：

$$Rf(\theta, s) = \int_{x \cdot \theta = s} f(x) d\sigma(x)$$

其中 $\theta \in S^{n-1}$，$s \in \mathbb{R}$，$d\sigma$ 是超平面 $\{x : x \cdot \theta = s\}$ 上的面积测度。

**应用**: 计算机断层扫描（CT）、积分几何。

---

### 定理 44.6 (Radon逆变换 / Radon Inversion Formula)

**定理**: 设 $f \in C_c^\infty(\mathbb{R}^n)$。则

$$f(x) = c_n \int_{S^{n-1}} (Rf)_s^{(n-1)}(\theta, x \cdot \theta) d\theta$$

其中 $g^{(k)}_s$ 表示关于 $s$ 的 $k$ 阶导数，$c_n$ 是仅依赖于 $n$ 的常数。

**滤波反投影**: 实际计算中使用 Fourier切片定理。

---

### 定义 I.44.7 (小波变换 / Wavelet Transform)

**定义**: 设 $\psi \in L^2(\mathbb{R})$ 是 **小波**（母小波），满足 $\int \psi = 0$。**连续小波变换** 定义为：

$$W_\psi f(a, b) = \frac{1}{\sqrt{|a|}} \int_{-\infty}^\infty f(t) \overline{\psi\left(\frac{t-b}{a}\right)} dt$$

其中 $a \neq 0$（尺度），$b \in \mathbb{R}$（平移）。

**重构公式**:

$$f(t) = \frac{1}{C_\psi} \int_{-\infty}^\infty \int_{-\infty}^\infty W_\psi f(a, b) \frac{1}{\sqrt{|a|}} \psi\left(\frac{t-b}{a}\right) \frac{da db}{a^2}$$

其中 $C_\psi = \int |\hat{\psi}(\xi)|^2 |\xi|^{-1} d\xi < \infty$（容许条件）。

---

### 定义 I.44.8 (Heaviside算子演算 / Heaviside Operational Calculus)

**历史背景**: Heaviside用符号 $p = d/dt$ 将微分方程转化为"代数方程"。

**例子**: 解 $y' + ay = f(t)$，$y(0) = 0$。

Heaviside方法: $(p + a)y = f$，故 $y = \frac{f}{p+a}$。展开：

$$y = \frac{1}{a}\frac{f}{1 + p/a} = \frac{1}{a}(1 - p/a + p^2/a^2 - \cdots) f = \frac{1}{a}f - \frac{f'}{a^2} + \frac{f''}{a^3} - \cdots$$

**严格化**: 通过Laplace变换。$p^{-1}$ 对应积分 $\int_0^t \cdot dt$。

---

### 参考文献 (44-XX)
1. Davies, B., *Integral Transforms and Their Applications*, Springer, 2002
2. Debnath, L., Bhatta, D., *Integral Transforms and Their Applications*, CRC, 2006
3. Titchmarsh, E.C., *Introduction to the Theory of Fourier Integrals*, Oxford, 1948
4. Bracewell, R.N., *The Fourier Transform and Its Applications*, McGraw-Hill, 2000
5. Strichartz, R.S., *A Guide to Distribution Theory and Fourier Transforms*, CRC, 1994

---

## 45-XX 积分方程 (Integral Equations)

### 定义 I.45.1 (积分方程的分类 / Classification of Integral Equations)

**Fredholm积分方程**:
- **第一类**: $\int_a^b K(x,y) \phi(y) dy = f(x)$
- **第二类**: $\phi(x) - \lambda \int_a^b K(x,y) \phi(y) dy = f(x)$

**Volterra积分方程**:
- **第一类**: $\int_a^x K(x,y) \phi(y) dy = f(x)$
- **第三类**: $\alpha(x)\phi(x) - \lambda \int_a^x K(x,y) \phi(y) dy = f(x)$

**奇异积分方程**: 核函数在积分区域上有奇点。

---

### 定义 I.45.2 (Fredholm算子 / Fredholm Operator)

**定义**: 设 $K \in L^2([a,b] \times [a,b])$。**Fredholm积分算子** 定义为：

$$(T_K \phi)(x) = \int_a^b K(x,y) \phi(y) dy$$

**性质**: $T_K: L^2[a,b] \to L^2[a,b]$ 是紧算子（Hilbert-Schmidt算子）。

**Fredholm行列式**:

$$D(\lambda) = \det(I - \lambda T_K) = \sum_{n=0}^\infty \frac{(-\lambda)^n}{n!} \int_a^b \cdots \int_a^b \det[K(x_i, x_j)]_{i,j=1}^n dx_1 \cdots dx_n$$

---

### 定理 45.1 (Fredholm择一性定理 / Fredholm Alternative)

**定理**: 设 $T$ 是Hilbert空间上的紧算子。则对于方程 $\phi - \lambda T\phi = f$，以下恰有一个成立：
1. 对于每个 $f$，存在唯一解 $\phi$
2. 齐次方程 $\phi - \lambda T\phi = 0$ 有非平凡解

**等价陈述**: $\mathcal{N}(I - \lambda T) = \{0\}$ 当且仅当 $\mathcal{R}(I - \lambda T) = H$。

---

### 定理 45.2 (Fredholm理论 / Fredholm Theory)

**定理**: 设 $T$ 是紧算子。则：
1. $\dim \mathcal{N}(I - \lambda T) < \infty$
2. $\mathcal{R}(I - \lambda T)$ 是闭子空间
3. $\mathcal{R}(I - \lambda T) = \mathcal{N}(I - \bar{\lambda} T^*)^\perp$
4. $\dim \mathcal{N}(I - \lambda T) = \dim \mathcal{N}(I - \bar{\lambda} T^*)$

**意义**: 非齐次方程可解当且仅当 $f$ 与共轭齐次方程的所有解正交。

---

### 定义 I.45.3 (对称核与特征值 / Symmetric Kernels and Eigenvalues)

**定义**: 核 $K(x,y)$ 是 **对称的**（Hermite），如果 $K(x,y) = \overline{K(y,x)}$。

**定理** (Hilbert-Schmidt): 设 $K$ 是对称的，$L^2$ 核。则存在正交归一的特征函数 $\{\phi_n\}$ 和实特征值 $\{\lambda_n\}$ 使得：

$$K(x,y) = \sum_n \frac{\phi_n(x) \overline{\phi_n(y)}}{\lambda_n}$$

（在 $L^2$ 意义下收敛）

---

### 定理 45.3 (Mercer定理 / Mercer's Theorem)

**定理**: 设 $K$ 是 $[a,b] \times [a,b]$ 上的连续、对称、正定核。则

$$K(x,y) = \sum_{n=1}^\infty \frac{\phi_n(x) \phi_n(y)}{\lambda_n}$$

在 $[a,b] \times [a,b]$ 上一致收敛。

**注**: "正定"意味着 $\int_a^b \int_a^b K(x,y) f(x) f(y) dx dy \geq 0$ 对所有 $f$。

---

### 定义 I.45.4 (积分方程的迭代解 / Iterative Solution of Integral Equations)

**Neumann级数**: 对于第二类Fredholm方程 $\phi = f + \lambda T_K \phi$，形式上有

$$\phi = (I - \lambda T_K)^{-1} f = \sum_{n=0}^\infty \lambda^n T_K^n f$$

**预解核**:

$$(I - \lambda T_K)^{-1} = I + \lambda R_\lambda$$

其中 $R_\lambda$ 有核

$$R(x,y;\lambda) = \sum_{n=1}^\infty \lambda^{n-1} K_n(x,y)$$

这里 $K_1 = K$，$K_{n+1}(x,y) = \int_a^b K(x,t) K_n(t,y) dt$。

**收敛性**: 当 $|\lambda| < \|T_K\|^{-1}$ 时Neumann级数收敛。

---

### 定理 45.4 (Volterra方程的解 / Solution of Volterra Equations)

**定理**: 第二类Volterra方程

$$\phi(x) - \lambda \int_a^x K(x,y) \phi(y) dy = f(x)$$

对所有 $\lambda \in \mathbb{C}$ 有唯一解。

**证明**: Volterra算子是幂零的（在某种意义上），故Neumann级数对所有 $\lambda$ 收敛。 □

---

### 定义 I.45.5 (奇异积分方程 / Singular Integral Equations)

**Cauchy奇异积分方程**:

$$a(x)\phi(x) + \frac{b(x)}{\pi i} \text{p.v.} \int_\Gamma \frac{\phi(\tau)}{\tau - x} d\tau = f(x), \quad x \in \Gamma$$

其中 $\Gamma$ 是光滑闭曲线。

**例子** (Hilbert变换):

$$\frac{1}{\pi} \text{p.v.} \int_{-1}^1 \frac{\phi(y)}{y-x} dy = f(x), \quad |x| < 1$$

---

### 定理 45.5 (奇异积分方程的可解性 / Solvability of Singular Integral Equations)

**定理** (Noether定理的推广): 设

$$A\phi = a(x)\phi(x) + \frac{b(x)}{\pi i} \int_\Gamma \frac{\phi(\tau)}{\tau - x} d\tau$$

其中 $a^2 - b^2$ 在 $\Gamma$ 上无零点。则
1. $\dim \mathcal{N}(A) < \infty$
2. $\mathcal{R}(A)$ 是闭的
3. $\text{index}(A) = \dim \mathcal{N}(A) - \text{codim} \mathcal{R}(A) = \frac{1}{2\pi}[\arg(a-ib)]_\Gamma$

**注**: index 是拓扑不变量，与算子的"环绕数"相关。

---

### 定义 I.45.6 (Wiener-Hopf方程 / Wiener-Hopf Equation)

**定义**: **Wiener-Hopf积分方程** 是

$$\phi(x) - \int_0^\infty K(x-y) \phi(y) dy = f(x), \quad x > 0$$

其中 $K \in L^1(\mathbb{R})$。

**方法**: 用Fourier变换。定义 $\phi_-(x) = \phi(x)$（$x > 0$），$\phi_-(x) = 0$（$x < 0$），然后分析 $(1 - \hat{K}(\xi))\hat{\phi}_-(\xi)$。

---

### 定理 45.6 (Wiener-Hopf分解 / Wiener-Hopf Factorization)

**定理**: 设 $K \in L^1(\mathbb{R})$，$1 - \hat{K}(\xi) \neq 0$，$\log(1 - \hat{K}(\xi)) \in L^1(\mathbb{R})$。则存在分解

$$1 - \hat{K}(\xi) = \frac{G_+(\xi)}{G_-(\xi)}$$

其中 $G_+$（resp. $G_-$）在 $\text{Im}(\xi) > 0$（resp. $\text{Im}(\xi) < 0$）解析且无零点。

**意义**: 将问题分解为上半平面和下半平面的解析函数问题。

---

### 定义 I.45.7 (Abel积分方程 / Abel's Integral Equation)

**定义**: **Abel积分方程** 是

$$\int_0^x \frac{\phi(y)}{(x-y)^\alpha} dy = f(x), \quad 0 < \alpha < 1$$

**解**: 

$$\phi(x) = \frac{\sin(\pi\alpha)}{\pi} \frac{d}{dx} \int_0^x \frac{f(y)}{(x-y)^{1-\alpha}} dy$$

**验证**: 利用Beta函数 $B(\alpha, 1-\alpha) = \pi/\sin(\pi\alpha)$。

---

### 定理 45.7 (积分方程与边值问题 / Integral Equations and Boundary Value Problems)

**定理**: 位势论中的Dirichlet问题

$$\Delta u = 0 \text{ 在 } \Omega \text{ 内}, \quad u|_{\partial\Omega} = f$$

可转化为第二类Fredholm积分方程（通过双层位势）。

**单层位势**:

$$u(x) = \int_{\partial\Omega} \frac{\partial G(x,y)}{\partial n_y} \phi(y) d\sigma(y)$$

其中 $G$ 是Green函数。

**边界条件**: 导出Fredholm积分方程

$$\pm \frac{1}{2}\phi(x) + \int_{\partial\Omega} \frac{\partial G(x,y)}{\partial n_y} \phi(y) d\sigma(y) = f(x)$$

---

### 参考文献 (45-XX)
1. Tricomi, F.G., *Integral Equations*, Dover, 1985
2. Hochstadt, H., *Integral Equations*, Wiley, 1973
3. Porter, D., Stirling, D.S.G., *Integral Equations: A Practical Treatment, from Spectral Theory to Applications*, Cambridge, 1990
4. Gripenberg, G., Londen, S.-O., Staffans, O., *Volterra Integral and Functional Equations*, Cambridge, 1990
5. Muskhelishvili, N.I., *Singular Integral Equations*, Dover, 2008

---

## Lean4 代码示例

本节提供与特殊函数、级数理论和积分变换相关的 Lean4 代码示例。

### 1. Gamma函数与Beta函数

```lean4
-- Gamma函数与Beta函数的基本性质
import Mathlib.Analysis.SpecialFunctions.Gamma.Beta
import Mathlib.Analysis.SpecialFunctions.Gamma.Reciprocal

-- Gamma函数的递推关系
example (n : ℕ) : Real.Gamma (n + 1) = n ! := by
  exact Real.Gamma_nat_eq_factorial n

-- Gamma函数与Beta函数的关系
example (a b : ℝ) (ha : 0 < a) (hb : 0 < b) :
    Real.Beta a b = Real.Gamma a * Real.Gamma b / Real.Gamma (a + b) := by
  exact Real.Beta_eq_Gamma_div_Gamma ha hb

-- Beta函数的对称性
example (a b : ℝ) : Real.Beta a b = Real.Beta b a := by
  exact Real.Beta_symm a b
```

### 2. 级数收敛判别法

```lean4
-- 级数的收敛性
import Mathlib.Analysis.SpecialFunctions.PowReal
import Mathlib.Topology.Algebra.InfiniteSum.Basic

-- 几何级数收敛条件
example (r : ℝ) (hr : Complex.abs r < 1) :
    HasSum (fun n => r^n) (1 / (1 - r)) := by
  apply hasSum_geometric_of_lt_one hr

-- p-级数的收敛性
example (p : ℝ) (hp : 1 < p) : Summable (fun n => 1 / (n + 1)^p) := by
  have := summable_one_div_pow_of_one_lt hp
  convert this using 1
  ring_nf
  field_simp
```

### 3. 正交多项式

```lean4
-- Hermite多项式
import Mathlib.Analysis.SpecialFunctions.PowReal

-- Legendre多项式的正交性 (示意性代码)
-- 注意：Mathlib中对Legendre多项式的支持有限

-- Hermite多项式的Rodrigues公式定义
-- H_n(x) = (-1)^n * e^(x^2) * d^n/dx^n(e^(-x^2))

-- Hermite多项式的递推关系
-- H_{n+1}(x) = 2x*H_n(x) - 2n*H_{n-1}(x)
```

### 4. 抽象调和分析基础

```lean4
-- 局部紧群上的调和分析
import Mathlib.MeasureTheory.Measure.Haar.OfAddCircle

-- 圆周群 T 上的 Fourier 级数
-- Fourier 变换将 T 映射到 ℤ

-- 加法群 ℝ 上的 Fourier 变换
example (f : ℝ → ℂ) (hf : Integrable f) :
    FourierTransform f = fun ξ => ∫ x, cexp (-2 * Real.pi * Complex.I * ξ * x) * f x := by
  rfl

-- Plancherel 定理 (L² 等距性)
-- ∫ |f|² = ∫ |Fourier f|²
```

### 5. 积分变换

```lean4
-- Fourier 变换
import Mathlib.Analysis.Fourier.FourierTransform

-- Fourier 变换的基本性质
example (f g : ℝ → ℂ) (hf : Integrable f) (hg : Integrable g) :
    FourierTransform (f + g) = FourierTransform f + FourierTransform g := by
  simp only [FourierTransform]
  funext ξ
  rw [Pi.add_apply]
  exact integral_add hf hg

-- 卷积定理
-- Fourier(f * g) = Fourier(f) * Fourier(g)
```

### 6. 积分方程理论

```lean4
-- Fredholm 积分算子的紧性
import Mathlib.Analysis.InnerProductSpace.Basic

-- Hilbert-Schmidt 算子是紧算子
-- 若 K ∈ L²([a,b] × [a,b])，则 T_K φ(x) = ∫ K(x,y) φ(y) dy 是紧算子

-- Fredholm 择一性 (示意性)
-- 对于 φ - λT_K φ = f，要么有唯一解，要么齐次方程有非平凡解
```

### 7. Bessel 函数

```lean4
-- Bessel 函数
import Mathlib.Analysis.SpecialFunctions.Bessel

-- 第一类 Bessel 函数的递推关系
example (ν x : ℝ) :
    x * Real.besselJ (ν + 1) x + x * Real.besselJ (ν - 1) x = 2 * ν * Real.besselJ ν x := by
  have h := Real.besselJ_add_sub ν x
  ring_nf at h ⊢
  linarith

-- Bessel 函数的生成函数
-- exp(x/2 * (t - 1/t)) = Σ_{n=-∞}^{∞} J_n(x) * t^n
```

### 8. Chebyshev 多项式

```lean4
-- Chebyshev 多项式
import Mathlib.Data.Polynomial.Basic

-- 第一类 Chebyshev 多项式: T_n(x) = cos(n * arccos x)

-- 递推关系
-- T_{n+1}(x) = 2x * T_n(x) - T_{n-1}(x)
-- T_0(x) = 1, T_1(x) = x

-- Chebyshev 多项式的极值性质
-- 在所有首一 n 次多项式中，2^(1-n) * T_n(x) 在 [-1,1] 上的最大模最小
```

### 9. 逼近理论

```lean4
-- Weierstrass 逼近定理 (示意性)
-- 任意连续函数可用多项式一致逼近

-- Bernstein 多项式
-- B_n(f)(x) = Σ_{k=0}^n f(k/n) * C(n,k) * x^k * (1-x)^(n-k)

-- Bernstein 多项式的构造
def bernsteinPoly (f : ℝ → ℝ) (n : ℕ) : Polynomial ℝ :=
  (Finset.range (n + 1)).sum fun k =>
    Polynomial.C (f (k / n)) * Polynomial.C (Real.choose n k) *
    (Polynomial.X ^ k * (1 - Polynomial.X) ^ (n - k))
```

### 10. 位势论基础

```lean4
-- 调和函数与 Laplace 方程
import Mathlib.Analysis.Calculus.Deriv

-- 调和函数: Δu = 0
-- 在二维情况下: u_xx + u_yy = 0

-- 下调和函数的定义
-- 若 u 上半连续且 u(x) ≤ 球面平均，则 u 下调和

-- 极大值原理 (示意性)
-- 若 u 在 Ω 上调和且在内部达到最大值，则 u 为常数
```

### 说明

上述代码展示了 Mathlib4 中特殊函数与积分变换理论的主要内容：

1. **Gamma/Beta 函数**: Mathlib 提供了完整的 Gamma 和 Beta 函数理论
2. **级数收敛**: 支持各种收敛判别法
3. **正交多项式**: 基本支持，但部分高级特性需要额外定义
4. **Fourier 分析**: Mathlib 有完整的 Fourier 变换理论
5. **Bessel 函数**: 提供了基本的 Bessel 函数定义和性质
6. **逼近理论**: Bernstein 多项式等可自定义实现

---

## 跨领域联系

### 与泛函分析的联系
- **Fredholm算子** = 紧算子的扰动，index 是拓扑不变量
- **积分算子** = 典型的紧算子（Hilbert-Schmidt, trace class）
- **Atiyah-Singer指标定理** = Fredholm算子index的几何解释

### 与微分方程的联系
- **Green函数** = 偏微分方程的积分核
- **Laplace变换** = 常微分方程的代数化
- **特殊函数** = 经典微分方程的解

### 与调和分析的联系
- **Hilbert变换** = 奇异积分算子的原型
- **Radon变换** = Fourier分析在积分几何中的应用
- **小波变换** = 时频分析的工具

### 与数学物理的联系
- **位势论** = 静电学、引力论
- **Fredholm理论** = 散射理论
- **Wiener-Hopf技术** = 波传播、衍射

### 与数值分析的联系
- **Galerkin方法** = 积分方程的数值解
- **正交多项式** = Gauss求积
- **样条函数** = 最佳插值

---

## 本卷统计

| 类别 | 数量 |
|------|------|
| **定义** | 47 |
| **定理** | 32 |
| **参考文献** | 35+ |
| **MSC二级分类** | 7 |

---

## 版本信息

**创建日期**: 2025-03-26  
**版本**: 2.0  
**总大小**: ~35K  
**MSC覆盖**: 31-XX, 33-XX, 40-XX, 41-XX, 43-XX, 44-XX, 45-XX

---

*"数学的特殊函数是数学这座大厦中最美丽的装饰品。"  
—— E. T. Whittaker*
