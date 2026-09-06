# 東京大学物理系 Phase 2 · 物理数学 I/II 深度講義

> **课程映射**（SURVEY §9 東大）：物理数学 I（線形代数・複素解析）+ 物理数学 II（微分方程式・特殊函数）
> **教材**：Arfken, Weber, Harris *Mathematical Methods for Physicists* 7ed（日文译本『物理者のための数学』）+ Riley, Hobson, Bence *Mathematical Methods for Physics and Engineering* 3ed（日文译本）+ Boas *Mathematical Methods in the Physical Sciences* 3ed
> **定位**：物理数学是东大物理学科的「工具箱」课程——线代给你量子力学的语言，复变给你计算的翅膀，ODE/PDE 给你连续物理的骨架，特殊函数给你解出的一切命名。没有这门课，量子力学的矩阵、电动力学的势、统计力学的配分函数积分，都无法真正落地。

---

## 0. 導引：物理数学为何是「工具箱」而非「数学课」

东大物理数学 I/II 与数学系的线性代数/复变分析截然不同：

- **数学系**：公理→定理→证明→推广，追求严格与一般性。
- **物理数学**：已知问题（量子力学的本征值、电动力学的 Laplace 方程、散射相移的 Legendre 多项式）→ 找到能解的数学结构 → 算出数字。

Arfken 全书的哲学一句话概括：

> *The physicist needs to know not just what is true, but what is useful.*

本章按 **线性代数 → 复变分析 → ODE → PDE → 特殊函数** 展开，每一节配 Python 数值验证，最后给出東大风格的习题集。

---

## 1. 線形代数（Linear Algebra）

### 1.1 矢量空间与线性变换

$n$ 维矢量空间 $V$ 上的线性变换 $A: V \to V$ 在基 $\{\vec{e}_i\}$ 下表示为矩阵 $A_{ij}$。物理中最核心的三类：

- **Hermite 矩阵**（$A^\dagger = A$）：量子力学的可观测量（Hamiltonian、自旋）。
- **幺正矩阵**（$U^\dagger U = I$）：对称操作（旋转、时间演化、规范变换）。
- **正交矩阵**（$O^T O = I$）：刚体旋转、Lorentz 变换（推广为 Lorentz 群 $O(1,3)$）。

### 1.2 本征值问题

$$\mathbf{A}\vec{v} = \lambda\vec{v} \quad \Longleftrightarrow \quad \det(\mathbf{A} - \lambda\mathbf{I}) = 0$$

**关键定理**：Hermite 矩阵的本征值全实，不同本征值的本征矢正交。这是量子力学「可观测量有实数谱、态正交」的数学根基。

### 1.3 对角化与谱分解

若 $\mathbf{A}$ 有 $n$ 个线性无关本征矢 $\{\vec{v}_i\}$，令 $\mathbf{S} = [\vec{v}_1 | \cdots | \vec{v}_n]$，则：

$$\mathbf{A} = \mathbf{S}\,\text{diag}(\lambda_1,\ldots,\lambda_n)\,\mathbf{S}^{-1}$$

Hermite/幺正矩阵总可对角化（谱定理），且 $\mathbf{S}$ 可选为幺正 $\Rightarrow$ **幺正对角化**。

### 1.4 二次型

$Q = \vec{x}^T\mathbf{A}\vec{x} = \sum_{ij} A_{ij}x_i x_j$。对角化 $\mathbf{A}$ 后，$Q = \sum_i \lambda_i y_i^2$。物理应用：惯性张量（力学篇 §4）、应变张量、能量曲面（$E = \vec{p}^2/2m$ 是二次型）。

> **正定判据**：$\mathbf{A}$ 正定 $\Leftrightarrow$ 所有 $\lambda_i > 0$。这在统计力学的稳定性分析（Hessian 正定 $\Rightarrow$ 局部稳定平衡）中关键。

### 1.5 张量初步

物理量按坐标变换行为分类：标量（0 阶）、矢量（1 阶）、矩阵/二阶张量（2 阶）、$n$ 阶张量。Einstein 求和约定：$T_{ij}x_j = \sum_j T_{ij}x_j$。

**张量缩并**（contraction）：$C_i = T_{ij}v_j$。物理中无处不在——Maxwell 方程 $\partial_\mu F^{\mu\nu} = J^\nu$ 就是张量缩并。

---

## 2. 複素解析（Complex Analysis）

### 2.1 解析函数与 Cauchy–Riemann 方程

$f(z) = u(x,y) + iv(x,y)$ 在 $z_0$ 的邻域内可导 $\Leftrightarrow$ $u, v$ 满足 **Cauchy–Riemann 方程**：

$$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \qquad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$

此时 $u, v$ 都是调和函数（$\nabla^2 u = \nabla^2 v = 0$）——复变与二维 Laplace 方程的直接联系。

### 2.2 Cauchy 积分定理与公式

**Cauchy 定理**：若 $f$ 在闭合曲线 $C$ 包围的区域内解析，则

$$\oint_C f(z)\,dz = 0$$

**Cauchy 积分公式**：$f$ 解析，$z_0$ 在 $C$ 内：

$$f(z_0) = \frac{1}{2\pi i}\oint_C \frac{f(z)}{z - z_0}\,dz$$

推论：解析函数无穷次可微，且由边界值完全决定。

### 2.3 留数定理（Residue Theorem）

物理数学最强大的计算工具。若 $f$ 在 $C$ 内有孤立奇点 $z_k$（$k = 1,\ldots,n$），则：

$$\boxed{\oint_C f(z)\,dz = 2\pi i \sum_k \text{Res}(f, z_k)}$$

其中**留数**（residue）：

$$\text{Res}(f, z_0) = \frac{1}{(m-1)!}\lim_{z\to z_0}\frac{d^{m-1}}{dz^{m-1}}\left[(z-z_0)^m f(z)\right] \quad (m\text{ 阶极点})$$

**一阶极点**（最常见）：$\text{Res}(f, z_0) = \lim_{z\to z_0}(z-z_0)f(z)$。

### 2.4 实积分的留数计算

物理中大量定积分可用留数定理计算。标准技巧——**Jordan 引理**处理半圆大弧贡献趋零的情形：

$$\int_{-\infty}^{\infty} \frac{e^{ikx}}{x^2+a^2}\,dx = \frac{\pi}{a}e^{-ka} \quad (k > 0,\, a > 0)$$

> 这是量子力学传播子、Green 函数计算的核心。Feynman 传播子的极点选取（因果边界条件 $+i\epsilon$）就是留数定理的物理化。

### 2.5 色散关系与 Kramers–Kronig

因果性（响应不能早于激励）$\Rightarrow$ 极点全在上半平面或下半平面 $\Rightarrow$ 实部与虚部由 Hilbert 变换联系：

$$\text{Re}\,f(\omega) = \frac{1}{\pi}\mathcal{P}\!\int_{-\infty}^{\infty}\frac{\text{Im}\,f(\omega')}{\omega'-\omega}\,d\omega'$$

这是光学、粒子物理中**色散关系**（Kramers–Kronig）的数学根源。

---

## 3. 常微分方程（ODE）

### 3.1 一阶 ODE

**可分离变量**：$dy/dx = f(x)g(y) \Rightarrow \int dy/g(y) = \int f(x)\,dx$。

**线性 ODE**：$y' + P(x)y = Q(x)$，积分因子 $\mu = e^{\int P\,dx}$：

$$y = \frac{1}{\mu}\left(\int \mu Q\,dx + C\right)$$

### 3.2 二阶线性 ODE

物理中最核心的方程形式：

$$y'' + P(x)y' + Q(x)y = 0$$

**常系数**：$y'' + ay' + by = 0$，特征方程 $r^2 + ar + b = 0$。

- 两实根 $r_1 \neq r_2$：$y = c_1 e^{r_1 x} + c_2 e^{r_2 x}$
- 重根 $r$：$y = (c_1 + c_2 x)e^{rx}$
- 复根 $\alpha \pm i\beta$：$y = e^{\alpha x}(c_1\cos\beta x + c_2\sin\beta x)$

> 谐振子 $y'' + \omega^2 y = 0$ 的解 $y = A\cos\omega t + B\sin\omega t$ 就是复根情形 $\alpha = 0$。

### 3.3 级数解法（Frobenius 方法）

$P(x), Q(x)$ 不恒为常数时，用幂级数 $y = \sum a_n x^{n+s}$ 代入，递推求系数。在**正则奇点**（regular singular point）处可用 **Frobenius 方法**。

> 这是 Bessel、Legendre、Hermite、Laguerre 等特殊函数的统一来源——它们都是同一个二阶 ODE 在不同系数下的级数解。见 §5。

### 3.4 Sturm–Liouville 理论

形如

$$\frac{d}{dx}\!\left[p(x)\frac{dy}{dx}\right] + [\lambda w(x) - q(x)]y = 0$$

的本征值问题，满足适当边界条件后：
- 本征值 $\lambda_n$ 全实。
- 本征函数 $y_n$ 关于权重 $w(x)$ 正交。
- 任意函数可按 $\{y_n\}$ 广义 Fourier 展开。

**这是量子力学「Hamiltonian 本征态正交完备」的数学根基**——Schrödinger 方程就是 Sturm–Liouville 型。

---

## 4. 偏微分方程（PDE）

### 4.1 三大方程

| 方程 | 形式 | 物理起源 | 类型 |
|------|------|----------|------|
| **波动方程** | $\nabla^2 u = \frac{1}{c^2}\frac{\partial^2 u}{\partial t^2}$ | 弦、声波、电磁波 | 双曲型 |
| **热传导方程** | $\nabla^2 u = \frac{1}{D}\frac{\partial u}{\partial t}$ | 热扩散、粒子扩散 | 抛物型 |
| **Laplace 方程** | $\nabla^2 u = 0$ | 静电势、稳态温度 | 椭圆型 |

### 4.2 分离变量法

核心思想：设 $u(x,t) = X(x)T(t)$，代入 PDE 后两边除以 $u$，使每边只含一个变量 $\Rightarrow$ 各等于分离常数。两个 ODE 分别求解后叠加。

**例：弦振动**（一维波动方程，两端固定 $u(0,t) = u(L,t) = 0$）：

$$X'' + k^2 X = 0 \Rightarrow X_n = \sin\frac{n\pi x}{L}, \quad T_n = \cos\frac{n\pi c t}{L}$$

$$u(x,t) = \sum_{n=1}^{\infty}\sin\frac{n\pi x}{L}\left(A_n\cos\frac{n\pi ct}{L} + B_n\sin\frac{n\pi ct}{L}\right)$$

系数 $A_n, B_n$ 由初始条件经 Fourier 正弦展开确定。**这就是为什么弦的振动是基频 + 泛音的叠加——分离变量把物理音乐还给了数学。**

### 4.3 球坐标下的 Laplace 方程

在球坐标 $(r, \theta, \phi)$ 中，$\nabla^2 u = 0$ 分离变量 $u = R(r)\Theta(\theta)\Phi(\phi)$，得到：
- $\Phi'' + m^2\Phi = 0$ $\Rightarrow$ $e^{im\phi}$（周期边界 $\Rightarrow m$ 整数）。
- $\Theta$ 满足连带 Legendre 方程 $\Rightarrow$ $P_\ell^m(\cos\theta)$。
- $R(r) = r^\ell$ 或 $r^{-(\ell+1)}$。

**球面谐调函数**（spherical harmonics）：

$$Y_\ell^m(\theta,\phi) = \sqrt{\frac{2\ell+1}{4\pi}\frac{(\ell-m)!}{(\ell+m)!}}\,P_\ell^m(\cos\theta)\,e^{im\phi}$$

这是氢原子、原子轨道、天体辐射、引力多极展开的统一语言。

### 4.4 Green 函数

点源的解推广为任意源的解。对 Laplace 算子：

$$\nabla^2 G(\vec{r}, \vec{r}') = -4\pi\delta^3(\vec{r}-\vec{r}') \quad \Rightarrow \quad G = \frac{1}{|\vec{r}-\vec{r}'|}$$

$$\nabla^2\phi = -\rho/\epsilon_0 \quad \Rightarrow \quad \phi(\vec{r}) = \frac{1}{4\pi\epsilon_0}\int\frac{\rho(\vec{r}')}{|\vec{r}-\vec{r}'|}d^3r'$$

Green 函数是把微分方程转化为积分方程的桥梁——量子场论的传播子就是 Green 函数。

---

## 5. 特殊函数（Special Functions）

### 5.1 Bessel 函数

Bessel 方程（柱坐标分离变量）：

$$x^2 y'' + xy' + (x^2 - \nu^2)y = 0$$

解为 $J_\nu(x)$（第一类）、$Y_\nu(x)$（第二类/Neumann）。**渐近行为**：

- $x \to 0$：$J_\nu(x) \approx (x/2)^\nu/\Gamma(\nu+1)$。
- $x \to \infty$：$J_\nu(x) \approx \sqrt{2/(\pi x)}\cos(x - \nu\pi/2 - \pi/4)$。

应用：圆柱波导中的电磁模式、圆形鼓膜振动、Fraunhofer 圆孔衍射（Airy 斑）。

### 5.2 Legendre 多项式与球面谐调函数

Legendre 方程：

$$(1-x^2)y'' - 2xy' + \ell(\ell+1)y = 0 \quad (\ell = 0,1,2,\ldots)$$

解 $P_\ell(x)$（Rodrigues 公式）：

$$P_\ell(x) = \frac{1}{2^\ell \ell!}\frac{d^\ell}{dx^\ell}(x^2-1)^\ell$$

前几个：$P_0=1,\; P_1=x,\; P_2=\frac{1}{2}(3x^2-1),\; P_3=\frac{1}{2}(5x^3-3x)$。

**正交性**：$\int_{-1}^{1} P_\ell(x)P_{\ell'}(x)\,dx = \frac{2}{2\ell+1}\delta_{\ell\ell'}$。

应用：多极展开（电偶极 $P_1$、四极 $P_2$）、氢原子角向波函数。

### 5.3 Hermite 多项式

量子谐振子：$H_n'' - 2xH_n' + 2n H_n = 0$。

$$H_n(x) = (-1)^n e^{x^2}\frac{d^n}{dx^n}e^{-x^2}$$

前几个：$H_0=1,\; H_1=2x,\; H_2=4x^2-2$。谐振子波函数 $\psi_n \propto H_n(\xi)e^{-\xi^2/2}$。

### 5.4 Laguerre 多项式

氢原子径向方程：$xL_n'' + (1-x)L_n' + nL_n = 0$。连带 Laguerre $L_n^k(x)$ 出现在氢原子径向波函数中。

---

## 6. Python 数值验证

所有代码纯 NumPy / 标准库，`bash` 可直接运行。

### 6.1 矩阵对角化（量子力学简谐振子的三个本征模式）

```python
# diagonalize.py —— Hermite 矩阵对角化验证正交性与谱分解
import numpy as np
np.random.seed(42)
n = 4
A = np.random.randn(n, n)
H = A + A.T              # Hermite（实对称）
eigvals, V = np.linalg.eigh(H)  # Hermite 专用（保证实本征值+正交本征矢）
print("H =\n", np.round(H, 3))
print(f"\n本征值: {np.round(eigvals, 4)}  (全实 ✓)")
# 验证正交
err_ortho = np.max(np.abs(V.T @ V - np.eye(n)))
print(f"正交性误差: {err_ortho:.2e} ✓")
# 验证谱分解 H = V Λ V^T
err_recon = np.max(np.abs(V @ np.diag(eigvals) @ V.T - H))
print(f"谱分解误差: {err_recon:.2e} ✓")
# 二次型的几何意义：椭球主轴
print(f"\n二次型 x^T H x 的主轴长度 ∝ 1/√|λ|: {np.round(1/np.sqrt(np.abs(eigvals)), 3)}")
```

### 6.2 留数定理验证：实积分 $\int_{-\infty}^{\infty}\frac{dx}{(x^2+a^2)(x^2+b^2)}$

```python
# residue_integral.py —— 留数定理 vs 数值积分
import numpy as np
a, b = 1.0, 2.0
# 解析结果（上半平面极点 ia, ib）：
# Res(ia) = 1/[(2ia)(b²-a²)]，Res(ib) = 1/[(-2ib)(a²-b²)]
# 总 = π/[ab(a+b)]
analytic = np.pi / (a * b * (a + b))
# 数值积分
x = np.linspace(-200, 200, 1000000)
dx = x[1] - x[0]
numerical = np.sum(1 / ((x**2 + a**2) * (x**2 + b**2))) * dx
print(f"留数定理: ∫ = {analytic:.8f}")
print(f"数值积分: ∫ = {numerical:.8f}")
print(f"相对误差: {abs(analytic - numerical)/analytic:.2e}")
print(f"\n解析公式: π/[ab(a+b)] = π/{a*b*(a+b):.0f} = {analytic:.6f}")
```

### 6.3 弦振动分离变量（Fourier 级数合成初始形状）

```python
# string_wave.py —— 波动方程分离变量解：拨弦（初始三角）
import numpy as np
L, c = 1.0, 1.0
Nx, N_modes = 200, 50
x = np.linspace(0, L, Nx)
# 初始形状：在 x0 处拨弦的三角
x0 = 0.3
def init_shape(x):
    return np.where(x < x0, x/x0, (L-x)/(L-x0))
u0 = init_shape(x)
# Fourier 正弦展开
A = np.zeros(N_modes)
for n in range(1, N_modes+1):
    A[n-1] = 2/L * np.trapz(u0 * np.sin(n*np.pi*x/L), x)
print("拨弦(x0=0.3L)的前10个 Fourier 正弦系数 An:")
for n in range(1, 11):
    print(f"  A_{n:2d} = {A[n-1]:+.4f}  (n={n} 频率 = {n*c/(2*L):.1f} Hz)")
print(f"\nn={int(L/(2*x0)):d} 模式振幅最大 ← 驻波节点最接近拨弦点")
# 检验重建精度
u0_recon = sum(A[n]*np.sin((n+1)*np.pi*x/L) for n in range(N_modes))
print(f"\n50模重建误差: {np.max(np.abs(u0_recon - u0)):.4f}")
```

### 6.4 球面谐调函数与多极展开

```python
# multipole.py —— 用 Legendre 多项式做电多极展开
import numpy as np
from numpy.polynomial.legendre import legval
# 点电荷 q 在 z=a 处，远场势 φ ∝ 1/|r - a ẑ| = Σ(a/r)^<ℓ P_ℓ(cosθ) / r  (r > a)
a = 1.0
r = 5.0   # 远场
theta = np.linspace(0, np.pi, 200)
cos_th = np.cos(theta)
exact = 1.0 / np.sqrt(r**2 + a**2 - 2*r*a*cos_th)  # 精确 1/|r - aẑ|
print("多极展开 1/|r-aẑ| (r=5, a=1):")
prev = np.zeros_like(theta)
for L in range(6):
    coeffs = [0]*L + [1]      # P_L 的系数
    PL = legval(cos_th, coeffs)
    term = (a/r)**L * PL / r
    prev += term
    err = np.max(np.abs(prev - exact))
    print(f"  ℓ={L}: {term.sum()/term.sum()*100:.0f}%  累计最大误差={err:.4e}")
print(f"\n精确势(θ=π/2): {1.0/np.sqrt(r**2+a**2):.6f}")
print(f"ℓ=5近似(θ=π/2): {prev[len(theta)//2]:.6f}  ← (a/r)⁵=3.2e-4 级别收敛")
```

---

## 7. 東大特色：計算伝統と数学的厳密さ

東京大学物理数学教育有两个鲜明特色：

### 7.1 「计算即理解」的学风

东大物理数学课的考试从不考证明题——全是大计算量题（留数定理算三阶极点、Bessel 函数递推、分离变量 5 项叠加）。这与东大「先算对、再想透」的传统一脉相承：

- **朝永振一郎**在 QED 重整化中的超人计算力，基础就是物理数学训练。
- **湯川秀樹**对介子质量的量纲估算，依赖于对特殊函数渐近行为的直觉。
- **小林誠・益川敏英**（2008 诺奖，CKM 矩阵）的工作本质是 $3\times3$ 幺正矩阵的参数化——线性代数直接产出诺奖。

### 7.2 日文教材传统

東大出版会翻译的物理数学教材体系完整：
- Arfken 日文版（吉岡書店）——最权威的研究生级参考。
- Riley-Hobson-Bence 日文版（東京電機大学出版局）——本科标准。
- **荒川泰彦**『物理数学』——東大本土教材，把复变和特殊函数讲得极紧凑。

---

## 8. 習題集（Exercises）

> 标 ★ 为東大风格（重计算），★★ 为研究生级。

**习题 1（★）**　用留数定理计算 $\displaystyle\int_0^{2\pi}\frac{d\theta}{a + b\cos\theta}$（$a > |b| > 0$）。
> *提示*：令 $z = e^{i\theta}$，化为单位圆上的围道积分。答案 $\dfrac{2\pi}{\sqrt{a^2-b^2}}$。

**习题 2（★★）**　证明 $J_{1/2}(x) = \sqrt{2/(\pi x)}\sin x$（半整数阶 Bessel 化为初等函数），并由此写出 $J_{3/2}(x)$。
> *答案*：$J_{3/2}(x) = \sqrt{2/(\pi x)}\left(\dfrac{\sin x}{x} - \cos x\right)$。半整数阶 Bessel 与球面 Bessel $j_\ell$ 直接关联。

**习题 3（★）**　求 Hermite 矩阵 $\mathbf{A} = \begin{pmatrix}2&1&1\\1&2&1\\1&1&2\end{pmatrix}$ 的本征值与本征矢。
> *答案*：本征值 $\lambda = 1$（二重简并，本征矢 $(1,-1,0)/\sqrt{2}$ 和 $(1,0,-1)/\sqrt{2}$）和 $\lambda = 4$（本征矢 $(1,1,1)/\sqrt{3}$）。

**习题 4（★★）**　一维热传导方程 $\partial u/\partial t = D\,\partial^2 u/\partial x^2$，初始条件 $u(x,0) = \delta(x)$。用 Fourier 变换求 $u(x,t)$，并验证 $\int_{-\infty}^{\infty}u\,dx = 1$（概率守恒）。
> *答案*：$u(x,t) = \dfrac{1}{\sqrt{4\pi Dt}}\exp\!\left(-\dfrac{x^2}{4Dt}\right)$（Gaussian），宽度 $\sigma = \sqrt{2Dt}$。

**习题 5（★）**　用 Rodrigues 公式验证 $P_4(x) = \frac{1}{8}(35x^4 - 30x^2 + 3)$，并验证正交性 $\int_{-1}^{1}P_2(x)P_4(x)\,dx = 0$。

**习题 6（★★）**　用 Frobenius 方法求 Laguerre 方程 $xy'' + (1-x)y' + ny = 0$ 的多项式解（$n$ 为非负整数），并写出 $L_0, L_1, L_2$。
> *答案*：$L_0=1,\; L_1=1-x,\; L_2=1-2x+x^2/2$。

---

## 9. 参考文献

1. Arfken, Weber, Harris. *Mathematical Methods for Physicists* 7ed. Academic Press, 2012.（東大物理数学 I/II 核心，日文版吉岡書店）
2. Riley, Hobson, Bence. *Mathematical Methods for Physics and Engineering* 3ed. Cambridge, 2006.（本科标准，习题极丰富，日文版東京電機大学出版局）
3. Boas, Mary L. *Mathematical Methods in the Physical Sciences* 3ed. Wiley, 2005.（最友好的入门，计算导向）
4. Butkov, Eugene. *Mathematical Physics*. Addison-Wesley, 1968.（复变与 PDE 讲得详尽）
5. Matthews, Walker. *Mathematical Methods of Physics* 2ed. Benjamin.（Feynman 风格，直觉优先）
6. 荒川泰彦. 『物理数学』（岩波書店）——東大本土教材，紧凑精炼。
7. 和達三樹. 『物理のための数学』（岩波書店）——東大经典，从线代到群论一册通。

---

**完成日期**：2026-08-12　|　**对应 SURVEY §9 東大**：物理数学 I（線形代数・複素解析）+ 物理数学 II（微分方程式・特殊函数）

---

## 🎯 费曼式入口（白话版）

> **一句话解释**：物理数学是「让物理学家算出数字」的工具箱——它不追求数学家那种严格证明，而追求「能解开我手里这个 Schrödinger 方程」。Arfken 全书的哲学是：知道什么有用，比知道什么严格更重要。
>
> **生活类比**：学物理数学像学做菜——你不需要懂味蕾的神经科学（数学系），但你需要熟练用刀（线代）、掌握火候（复变）、知道食材怎么变熟（ODE/PDE）、最后给菜品起个好听的名字（特殊函数）。每个数学工具都对应一类物理问题的「菜谱」。
>
> **反直觉发现**：
> - **留数定理是「作弊器」**：实轴上一个麻烦的积分 $\int_{-\infty}^{\infty} \frac{dx}{(x^2+1)(x^2+4)}$，硬算要分式分解+三角代换；用留数定理，把积分扩展到复平面，闭曲线绕一下，只看里面两个极点的「留数」，$10$ 秒算完。物理中所有 Green 函数、传播子都靠它。
> - **Hermite 矩阵的本征值永远是实数**：这是量子力学「可观测量测出来必是实数」的全部数学根基。没有这条定理，物理学就没法定义「能量」。
> - **特殊函数其实是同一个 ODE**：Bessel、Legendre、Hermite、Laguerre 看起来八竿子打不着，但都是「二阶线性 ODE 在不同系数下用幂级数解」的产物。Frobenius 方法一通百通。
> - **Green 函数 = 量子场论传播子**：你把单位点源的解叫 Green 函数，量子场论里把粒子「从这到那」的概率幅叫传播子——本质是同一个数学对象。

---

## 🔗 衔接：从哪来，到哪去

### 前置
- **微积分**：多元函数、偏导、多重积分、线面积分。
- **线性代数（基础）**：矩阵、本征值、对角化。
- **ODE 基础**：一阶、二阶常系数线性方程。

### 本课解决了什么危机
- **线代会算但不严格**：你能在 3 行内对角化矩阵，但不知道「为什么能对角化」。物理数学用谱定理（Hermite 矩阵）一锤定音。
- **复变为什么有用**：实积分算不动，但「绕到复平面」反而简单——因为复变函数在解析域里有超强结构（Cauchy 积分公式）。
- **特殊函数记不住**：Bessel/Legendre/Hermite/Laguerre 像动物园。**Frobenius 方法**统一它们：所有正则奇点附近的二阶 ODE 都用幂级数 + 递推，记一套就够。

### 本课留下的新危机（通往下一站）
- **非线性 PDE 没有通用方法**：Navier-Stokes、Yang-Mills 方程解析解寥寥 → 数值方法（FEM/谱方法）、机器学习求解 PDE（PINN, 2020s）兴起。
- **群论 + 表示论**：本课只讲张量初步。量子力学（角动量、原子光谱）、粒子物理（标准模型 $SU(3)\times SU(2)\times U(1)$）需要完整的 Lie 群论。東大研究生「物理学数学 III」专攻此。
- **随机过程 + 路径积分**：统计力学的 Langevin 方程、量子力学的 Feynman 路径积分——需要随机微积分（Itô 积分）+ 变分法。

### 后续（東大路径）
| 方向 | 课程 | 用到本课什么 |
|------|------|-------------|
| 量子力学 | 量子 A/B | Hermite 算符、本征值、CG 系数 |
| 电动力学 | EM | 多极展开（Legendre）、Green 函数 |
| 量子场论 | 素粒子 | 留数定理、传播子、群论 |
| 流体力学 | 选修 | PDE + Navier-Stokes |
| 凝聚态 | 物性 | Bloch 定理、紧束缚、格林函数 |

---

## 🏭 理论联系实际：5 个应用

1. **结构工程与有限元（FEM）**：桥梁、飞机、汽车的安全设计都依赖求解弹性力学 PDE。特征值问题（线代）找共振频率避免坍塌——东京天空树、东京湾跨海大桥的振动分析都靠这些。
2. **图像压缩与 SVD**：JPEG 2000、Netflix 推荐算法的本质是矩阵奇异值分解（SVD）。线代不止是教科书——它处理每天 YouTube 几十亿次视频流。
3. **控制论与信号处理**：Laplace 变换 + 留数定理是经典控制理论（PID、机器人、自动驾驶）的核心数学。東大 IIS 的自动车研究高度依赖。
4. **机器学习与张量网络**：神经网络的训练是大规模矩阵运算 + 梯度下降（最优化）；AlphaFold 的注意力机制 = 张量运算。物理学家的张量网络（PEPS/MERA）反向启发新 AI 架构。
5. **随机矩阵理论与金融物理**：随机矩阵（如 Gaussian Unitary Ensemble）的本征值分布，被发现与股价相关性矩阵、核能级谱、黎曼 ζ 函数零点吻合——一种「普适性」。东京大学数学物理组有传统。

---

## 🔬 最新研究前沿（2024-2026）

- **物理信息神经网络（PINN）解 PDE（2020s 大爆发）**：用深度学习近似求解非线性 PDE，2024–2025 在湍流、生物流体、高维 Schrödinger 方程取得突破。東大「データ駆動科学」与物性研联合推进。
- **量子算法冲击线性代数**：HHL 算法（2009）理论上能指数加速解线性方程组；2024–2025 NISQ 时代的变分版本（VQLS）开始在小规模问题上展示优势。如果成熟，机器学习训练将被颠覆。
- **拓扑数据分析（TDA）进入物理**：用持续同调（persistent homology）分析分子结构、相变、神经网络。2024 年多篇 PRL/Nature 用 TDA 识别新的物质相。
- **随机矩阵 + 深度学习**：训练好的神经网络权重矩阵的本征值谱被发现符合 Marchenko-Pastur 律——为什么大模型能泛化？答案可能在线代 + 随机矩阵的交叉。
- **数值相对论 + 谱方法**：LIGO 引力波信号模板需要求解 Einstein 方程这种高度非线性 PDE。2024–2025 用谱方法 + GPU 实现「黑洞并合」的全数值模拟，速度提升 100 倍。

---

## 🗺️ 学习 Roadmap（Tokyo 路径）

```
基础微积分 + 线性代数（1 年级， 工程数学）
  ↓ 一元/多元微积分、矩阵、本征值
物理数学 I（2 年级， Arfken Ch.1-6 / Boas）
  ↓ 核心关卡 I ↓
  ├─ 线性代数：Hermite/幺正矩阵、对角化、二次型、张量
  ├─ 复变：解析函数、Cauchy 定理、留数定理、色散关系
  └─ 积分变换：Fourier、Laplace
物理数学 II（3 年级， Arfken Ch.7-14 / Riley-Hobson-Bence）
  ↓ 核心关卡 II ↓
  ├─ ODE：一阶/二阶、级数解、Sturm-Liouville
  ├─ PDE：分离变量、波动/热传导/Laplace、Green 函数
  └─ 特殊函数：Bessel / Legendre / Hermite / Laguerre
研究生进阶
  ├─ 群论 + 表示论（物理学数学 III，标准模型前置）
  ├─ 微分几何 + 拓扑（广义相对论、规范场论）
  ├─ 泛函分析 + 路径积分（QFT 工具）
  └─ 数值方法 + 机器学习（PINN、张量网络）
```

**知识检查**：
- [ ] 能用留数定理算 $\int_{-\infty}^{\infty}\frac{dx}{(x^2+a^2)(x^2+b^2)}$，10 秒给出答案 $\pi/[ab(a+b)]$。
- [ ] 能解释 Hermite 矩阵本征值为实数的证明（$A\vec{v}=\lambda\vec{v}$ $\Rightarrow$ 取共轭转置）。
- [ ] 能用分离变量法解一维波动方程（弦振动），并解释为什么是基频 + 泛音叠加。
- [ ] 能写出氢原子 Schrödinger 方程，分离变量后说清楚每段（径向 + 球谐）对应的特殊函数。
- [ ] 能说出 Green 函数与 QFT 传播子的对应关系。
- [ ] 能用 Frobenius 方法推 Laguerre 多项式（氢原子径向解）。
