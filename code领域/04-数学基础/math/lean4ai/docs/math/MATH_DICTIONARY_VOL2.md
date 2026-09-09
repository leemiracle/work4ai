# 数学知识词典 - 第二卷：分析与微分方程
## Volume II: Analysis and Differential Equations

**MSC分类**: 26-XX, 28-XX, 30-XX, 32-XX, 33-XX, 34-XX, 35-XX, 37-XX, 42-XX  
**版本**: 1.0  
**日期**: 2025-03-26

---

## 目录

1. [实分析 (26-XX)](#1-实分析)
2. [测度论 (28-XX)](#2-测度论)
3. [单复变函数 (30-XX)](#3-单复变函数)
4. [偏微分方程 (35-XX)](#4-偏微分方程)
5. [动力系统 (37-XX)](#5-动力系统)
6. [傅里叶分析 (42-XX)](#6-傅里叶分析)

---

## 1. 实分析 (26-XX)

### 1.1 实数系统 [26Axx]

#### 定义 XIII.1.1 (实数的完备性)
**Definition XIII.1.1 (Completeness of Real Numbers)**

**完备序域**: ℝ是包含ℚ的完备序域，满足:
1. **确界原理**: 每个有上界的非空集合有最小上界
2. **Dedekind分割**: 每个分割(A,B)有分界点
3. **Cauchy完备**: 每个Cauchy序列收敛

**等价公理**:
1. 单调收敛定理
2. 闭区间套定理
3. Bolzano-Weierstrass定理
4. Heine-Borel定理

---

### 1.2 极限与连续性 [26Axx]

#### 定义 XIII.2.1 (ε-δ定义)
**Definition XIII.2.1 (ε-δ Definitions)**

**函数极限**: lim_{x→a} f(x) = L ⟺ 
```
∀ε > 0, ∃δ > 0: 0 < |x - a| < δ ⟹ |f(x) - L| < ε
```

**连续性**: f在a连续 ⟺ lim_{x→a} f(x) = f(a)

**一致连续**: ∀ε > 0, ∃δ > 0: ∀x,y, |x - y| < δ ⟹ |f(x) - f(y)| < ε

#### 定理 13.1 (Heine-Cantor定理)
**Theorem 13.1 (Heine-Cantor Theorem)**

紧集上的连续函数一致连续。

*证明*. 紧性 + Lebesgue数引理。 □

#### 定理 13.2 (介值定理)
**Theorem 13.2 (Intermediate Value Theorem)**

若f在[a,b]连续且f(a) < 0 < f(b)，则∃c ∈ (a,b)使f(c) = 0。

*证明*. 连通性或二分法。 □

---

### 1.3 微分学 [26Axx]

#### 定义 XIII.3.1 (导数)
**Definition XIII.3.1 (Derivatives)**

**导数**: f'(a) = lim_{h→0} [f(a+h) - f(a)]/h

**可微性**: f在a可微 ⟺ 该极限存在且有限

**高阶导数**: f^{(n)} = (f^{(n-1)})'

#### 定理 13.3 (中值定理)
**Theorem 13.3 (Mean Value Theorems)**

**Rolle**: f(a) = f(b) ⟹ ∃c: f'(c) = 0

**Lagrange**: ∃c ∈ (a,b): f'(c) = [f(b)-f(a)]/(b-a)

**Cauchy**: ∃c: [f(b)-f(a)]g'(c) = [g(b)-g(a)]f'(c)

*证明*. 应用Rolle定理到辅助函数。 □

#### 定理 13.4 (Taylor定理)
**Theorem 13.4 (Taylor's Theorem)**

**带Lagrange余项**:
```
f(x) = Σ_{k=0}^n f^{(k)}(a)(x-a)^k/k! + f^{(n+1)}(ξ)(x-a)^{n+1}/(n+1)!
```
其中ξ在a和x之间。

**Peano余项**: R_n(x) = o((x-a)^n) 当x→a

---

### 1.4 Riemann积分 [26Axx]

#### 定义 XIII.4.1 (Riemann积分)
**Definition XIII.4.1 (Riemann Integral)**

**Riemann和**: S(f,P,ξ) = Σ f(ξᵢ)(xᵢ-xᵢ₋₁)

**Riemann可积**: lim_{||P||→0} S(f,P,ξ)存在

**Darboux定义**: 
```
∫_a^b f = sup{L(f,P)} = inf{U(f,P)}
```
其中L(f,P)和U(f,P)是下和与上和。

#### 定理 13.5 (Riemann可积条件)
**Theorem 13.5 (Riemann Integrability)**

有界函数f在[a,b]上Riemann可积 ⟺ f的不连续点集的测度为零。

*推论*: 连续函数、单调函数、有有限个间断点的函数都可积。

---

## 2. 测度论 (28-XX)

### 2.1 σ-代数与测度 [28Axx]

#### 定义 XIV.1.1 (σ-代数)
**Definition XIV.1.1 (σ-Algebras)**

X的子集族ℱ是**σ-代数** 如果:
1. X ∈ ℱ
2. A ∈ ℱ ⟹ A^c ∈ ℱ
3. Aₙ ∈ ℱ ⟹ ⋃ Aₙ ∈ ℱ

**可测空间**: (X, ℱ)

**Borel σ-代数**: 由开集生成的σ-代数 ℬ(X)

#### 定义 XIV.1.2 (测度)
**Definition XIV.1.2 (Measures)**

**测度** μ: ℱ → [0,∞] 满足:
1. μ(∅) = 0
2. **可数可加性**: Aᵢ不交 ⟹ μ(⋃ Aᵢ) = Σ μ(Aᵢ)

**测度空间**: (X, ℱ, μ)

**完备性**: E ⊆ F且μ(F) = 0 ⟹ E ∈ ℱ

#### 定理 14.1 (Carathéodory扩张定理)
**Theorem 14.1 (Carathéodory Extension Theorem)**

环R上的准测度μ可唯一扩张为σ(R)上的测度。

*应用*: Lebesgue测度的构造。

---

### 2.2 Lebesgue测度 [28Axx]

#### 定义 XIV.2.1 (Lebesgue测度)
**Definition XIV.2.1 (Lebesgue Measure)**

**外测度**:
```
m^*(A) = inf{Σ l(Iₙ) : A ⊆ ⋃ Iₙ}
```
其中Iₙ是开区间。

**Lebesgue可测**: A可测 ⟺ 对所有E ⊆ ℝ:
```
m^*(E) = m^*(E∩A) + m^*(E\A)
```

**性质**:
1. 平移不变性: m(A+x) = m(A)
2. 可数可加性
3. m([a,b]) = b-a
4. 不可测集存在 (Vitali集)

---

### 2.3 Lebesgue积分 [28Axx]

#### 定义 XIV.3.1 (简单函数)
**Definition XIV.3.1 (Simple Functions)**

**简单函数**: s = Σ_{i=1}^n aᵢ χ_{Aᵢ} (aᵢ ∈ ℝ, Aᵢ可测)

**积分**: ∫ s dμ = Σ aᵢ μ(Aᵢ)

#### 定义 XIV.3.2 (非负函数的积分)
**Definition XIV.3.2 (Integral of Non-negative Functions)**

```
∫ f dμ = sup{∫ s dμ : 0 ≤ s ≤ f, s简单}
```

**一般函数**: ∫ f dμ = ∫ f^+ dμ - ∫ f^- dμ (当至少一个有限)

**L¹空间**: L¹(μ) = {可测f : ∫ |f| dμ < ∞}

#### 定理 14.2 (单调收敛定理)
**Theorem 14.2 (Monotone Convergence Theorem)**

若0 ≤ fₙ ↗ f，则 ∫ fₙ dμ → ∫ f dμ。

*证明*. Fatou引理的推论。 □

#### 定理 14.3 (控制收敛定理)
**Theorem 14.3 (Dominated Convergence Theorem)**

若fₙ → f a.e.且|fₙ| ≤ g ∈ L¹，则:
```
∫ fₙ dμ → ∫ f dμ
```

*证明*. Fatou引理应用于g±fₙ。 □

#### 定理 14.4 (Fatou引理)
**Theorem 14.4 (Fatou's Lemma)**

若fₙ ≥ 0，则:
```
∫ liminf fₙ dμ ≤ liminf ∫ fₙ dμ
```

*证明*. 下确界性质。 □

---

### 2.4 乘积测度与Fubini定理 [28Axx]

#### 定理 14.5 (Fubini定理)
**Theorem 14.5 (Fubini's Theorem)**

设(X,μ)和(Y,ν)是σ-有限测度空间。

**Tonelli**: 若f ≥ 0可测，则:
```
∫_{X×Y} f d(μ×ν) = ∫_X [∫_Y f(x,y) dν(y)] dμ(x)
```

**Fubini**: 若f ∈ L¹(μ×ν)，则:
```
∫_{X×Y} f d(μ×ν) = ∫_X [∫_Y f(x,y) dν(y)] dμ(x) = ∫_Y [∫_X f(x,y) dμ(x)] dν(y)
```

*证明*. 从简单函数到一般函数。 □

---

## 3. 单复变函数 (30-XX)

### 3.1 解析函数 [30Axx]

#### 定义 XV.1.1 (复导数)
**Definition XV.1.1 (Complex Derivatives)**

**复可微**: f在z₀可微，如果极限
```
f'(z₀) = lim_{z→z₀} [f(z) - f(z₀)]/(z - z₀)
```
存在（沿任何路径）。

**解析函数/全纯函数**: 在区域内处处可微的函数

**Cauchy-Riemann方程**: 设f = u + iv，则f解析 ⟺
```
∂u/∂x = ∂v/∂y,  ∂u/∂y = -∂v/∂x
```
且u,v连续可微。

#### 定理 15.1 (解析函数的性质)
**Theorem 15.1 (Properties of Analytic Functions)**

若f在区域Ω内解析，则:
1. f有任意阶导数
2. f在每点可展开为Taylor级数（半径等于到边界的距离）
3. f满足Cauchy-Riemann方程
4. f是调和函数的解析组合

---

### 3.2 Cauchy积分理论 [30Axx]

#### 定理 15.2 (Cauchy积分定理)
**Theorem 15.2 (Cauchy's Integral Theorem)**

若f在单连通域D内解析，γ是D中的闭曲线，则:
```
∮_γ f(z) dz = 0
```

*等价形式*: Morera定理（逆定理）

*证明*. Green定理 + Cauchy-Riemann方程。 □

#### 定理 15.3 (Cauchy积分公式)
**Theorem 15.3 (Cauchy's Integral Formula)**

若f在|z-a| ≤ R解析，则对|z-a| < R:
```
f(z) = (1/2πi) ∮_{|ζ-a|=R} f(ζ)/(ζ-z) dζ
```

**高阶导数公式**:
```
f^{(n)}(z) = (n!/2πi) ∮ f(ζ)/(ζ-z)^{n+1} dζ
```

*推论*: **Cauchy估计**: |f^{(n)}(a)| ≤ n!M/R^n

---

### 3.3 留数理论 [30Axx]

#### 定义 XV.3.1 (留数)
**Definition XV.3.1 (Residues)**

设f在z₀有孤立奇点，Laurent展开为:
```
f(z) = Σ_{n=-∞}^∞ c_n(z-z₀)^n
```

**留数**: Res(f, z₀) = c_{-1}

**计算**:
- 一阶极点: Res(f, z₀) = lim_{z→z₀} (z-z₀)f(z)
- n阶极点: Res(f, z₀) = lim_{z→z₀} [1/(n-1)!] d^{n-1}/dz^{n-1} [(z-z₀)^n f(z)]

#### 定理 15.4 (留数定理)
**Theorem 15.4 (Residue Theorem)**

若f在简单闭曲线γ内除有限个奇点z₁,...,zₙ外解析，则:
```
∮_γ f(z) dz = 2πi Σ Res(f, zₖ)
```

*应用*: 计算实积分

**例子**: ∫_{-∞}^∞ dx/(1+x²) = π

*计算*: f(z) = 1/(1+z²)在上半平面有一阶极点z=i，Res(f,i) = 1/2i。 □

---

### 3.4 解析延拓 [30Axx]

#### 定理 15.5 (解析延拓的唯一性)
**Theorem 15.5 (Uniqueness of Analytic Continuation)**

设f在区域D内解析。若f在D中有聚点的子集上为零，则f ≡ 0。

*推论*: 解析延拓若存在则唯一。

#### 定义 XV.4.1 (最大模原理)
**Definition XV.4.1 (Maximum Modulus Principle)**

**最大模原理**: 若f在区域D内解析且非常数，则|f|在D内取不到最大值。

*推论*: 开映射定理（解析函数是开映射）

---

## 4. 偏微分方程 (35-XX)

### 4.1 分类与基本概念 [35Axx]

#### 定义 XVI.1.1 (PDE分类)
**Definition XVI.1.1 (Classification of PDEs)**

**二阶线性PDE**: au_xx + bu_xy + cu_yy + du_x + eu_y + fu = g

**判别式**: Δ = b² - 4ac
- Δ > 0: 双曲型 (如波动方程)
- Δ = 0: 抛物型 (如热方程)
- Δ < 0: 椭圆型 (如Laplace方程)

**例子**:
1. **波动方程**: u_tt - c²u_xx = 0 (双曲型)
2. **热方程**: u_t - ku_xx = 0 (抛物型)
3. **Laplace方程**: u_xx + u_yy = 0 (椭圆型)

---

### 4.2 椭圆型方程 [35Jxx]

#### 定义 XVII.2.1 (Laplace算子)
**Definition XVII.2.1 (Laplace Operator)**

**Laplace算子**: Δu = Σ ∂²u/∂x_i²

**调和函数**: Δu = 0的解

**性质**:
1. 平均值性质: u(x₀) = (1/|∂B|) ∫_{∂B} u dS
2. 极大值原理: 调和函数在内部取不到极值
3. 实解析

#### 定理 17.1 (Dirichlet问题的适定性)
**Theorem 17.1 (Well-posedness of Dirichlet Problem)**

**Dirichlet问题**:
```
Δu = 0  在Ω内
u = f   在∂Ω上
```

若Ω有界且∂Ω光滑，则解存在唯一。

*证明*. Perron方法（下调和函数）或变分法。 □

---

### 4.3 抛物型方程 [35Kxx]

#### 定理 17.2 (热方程的解)
**Theorem 17.2 (Solution of Heat Equation)**

**热方程**: u_t = ku_xx, u(x,0) = f(x)

**解**: u(x,t) = (1/√(4πkt)) ∫_{-∞}^∞ f(y) e^{-(x-y)²/(4kt)} dy

**热核**: K(x,t) = (1/√(4πkt)) e^{-x²/(4kt)}

**性质**:
1. 无穷传播速度
2. 平滑化性质
3. 极大值原理

---

### 4.4 双曲型方程 [35Lxx]

#### 定理 17.3 (波动方程的解)
**Theorem 17.3 (Solution of Wave Equation)**

**一维波动方程**: u_tt - c²u_xx = 0

**d'Alembert公式**:
```
u(x,t) = [f(x+ct) + f(x-ct)]/2 + (1/2c) ∫_{x-ct}^{x+ct} g(s) ds
```

**二维 (Kirchhoff公式)**:
```
u(x,t) = (1/2πc) ∂/∂t ∫_{B(x,ct)} [f(y)/√(c²t²-|x-y|²)] dy + ...
```

**三维 (Poisson公式)**:
```
u(x,t) = (1/4πc²t) ∫_{∂B(x,ct)} f(y) dS(y) + ...
```

**性质**:
1. 有限传播速度
2. Huygens原理 (3维)
3. 特征线方法

---

### 4.5 弱解与Sobolev空间 [35Dxx]

#### 定义 XVII.5.1 (弱导数)
**Definition XVII.5.1 (Weak Derivatives)**

u有弱导数D^α u ∈ L¹_loc(Ω) 如果对所有φ ∈ C_c^∞(Ω):
```
∫_Ω u D^α φ dx = (-1)^{|α|} ∫_Ω (D^α u) φ dx
```

#### 定义 XVII.5.2 (Sobolev空间)
**Definition XVII.5.2 (Sobolev Spaces)**

**Sobolev空间**: W^{k,p}(Ω) = {u ∈ L^p(Ω) : D^α u ∈ L^p(Ω), |α| ≤ k}

**范数**: ||u||_{W^{k,p}} = [Σ_{|α|≤k} ||D^α u||_{L^p}^p]^{1/p}

**H^k(Ω) = W^{k,2}(Ω)**

#### 定理 17.4 (Sobolev嵌入定理)
**Theorem 17.4 (Sobolev Embedding Theorem)**

若kp > n，则:
```
W^{k,p}(Ω) ⊆ C^{0,γ}(Ω̄)
```
其中γ = k - n/p (Holder连续)

*推论*: H^1(ℝ³) ⊆ L^6(ℝ³)

---

## 5. 动力系统 (37-XX)

### 5.1 拓扑动力系统 [37Bxx]

#### 定义 XVIII.1.1 (动力系统)
**Definition XVIII.1.1 (Dynamical Systems)**

**拓扑动力系统**: 对(X, T)其中X是紧度量空间，T: X → X连续。

**轨道**: Orb(x) = {T^n(x) : n ≥ 0}

**ω-极限集**: ω(x) = ⋂_{n≥0} Cl{T^k(x) : k ≥ n}

**不动点**: T(x) = x

**周期点**: T^n(x) = x对某n

#### 定义 XVIII.1.2 (极小性与传递性)
**Definition XVIII.1.2 (Minimality and Transitivity)**

**极小**: X没有非平凡闭不变子集

**传递**: 存在x使得Orb(x)稠密 ⟺ 对任意开U,V，存在n使T^n(U)∩V≠∅

**混沌** (Devaney):
1. 传递
2. 周期点稠密
3. 初值敏感依赖

---

### 5.2 遍历理论 [37Axx]

#### 定义 XVIII.2.1 (保测变换)
**Definition XVIII.2.1 (Measure-Preserving Transformations)**

T: X → X **保测** 如果μ(T^{-1}(A)) = μ(A)对所有可测A。

**遍历**: T的不变集测度为0或1

#### 定理 18.1 (Birkhoff遍历定理)
**Theorem 18.1 (Birkhoff's Ergodic Theorem)**

设(X,μ)是概率空间，T保测遍历。则对f ∈ L¹:
```
lim_{n→∞} (1/n) Σ_{k=0}^{n-1} f(T^k x) = ∫ f dμ   a.e.
```

*意义*: 时间平均 = 空间平均

*应用*: 统计力学、数论

---

### 5.3 双曲系统 [37Dxx]

#### 定义 XVIII.3.1 (双曲不动点)
**Definition XVIII.3.1 (Hyperbolic Fixed Points)**

**双曲不动点**: x₀使得T(x₀)=x₀且DT(x₀)的特征值λ满足|λ|≠1

**稳定流形**: W^s(x₀) = {x : T^n(x) → x₀ 当n→∞}

**不稳定流形**: W^u(x₀) = {x : T^{-n}(x) → x₀ 当n→∞}

#### 定理 18.2 (稳定流形定理)
**Theorem 18.2 (Stable Manifold Theorem)**

双曲不动点的稳定/不稳定流形是光滑浸入子流形。

*证明*. 不动点定理 + 隐函数定理。 □

---

## 6. 傅里叶分析 (42-XX)

### 6.1 Fourier级数 [42Axx]

#### 定义 XIX.1.1 (Fourier级数)
**Definition XIX.1.1 (Fourier Series)**

**Fourier系数** (对周期2π的函数):
```
aₙ = (1/π) ∫_{-π}^{π} f(x) cos(nx) dx
bₙ = (1/π) ∫_{-π}^{π} f(x) sin(nx) dx
```

**Fourier级数**: 
```
f(x) ~ a₀/2 + Σ_{n=1}^∞ [aₙ cos(nx) + bₙ sin(nx)]
```

**复形式**: f(x) ~ Σ_{n=-∞}^∞ ĉ_n e^{inx},  ĉ_n = (1/2π) ∫ f(x) e^{-inx} dx

#### 定理 19.1 (收敛定理)
**Theorem 19.1 (Convergence Theorems)**

1. **Dirichlet**: 若f逐段光滑，则Fourier级数在连续点收敛到f，在间断点收敛到[f(x+)+f(x-)]/2

2. **Fejér**: 若f连续，则Fourier级数的Cesàro平均一致收敛到f

3. **Carleson**: 若f ∈ L²([-π,π])，则Fourier级数几乎处处收敛

---

### 6.2 Fourier变换 [42Axx]

#### 定义 XIX.2.1 (Fourier变换)
**Definition XIX.2.1 (Fourier Transform)**

**Fourier变换** (对f ∈ L¹(ℝ)):
```
f̂(ξ) = ∫_{-∞}^∞ f(x) e^{-2πixξ} dx
```

**逆变换**:
```
f(x) = ∫_{-∞}^∞ f̂(ξ) e^{2πixξ} dξ
```

**性质**:
1. 平移: (f(x-a))̂ = e^{-2πiaξ} f̂(ξ)
2. 伸缩: (f(ax))̂ = (1/|a|) f̂(ξ/a)
3. 导数: (f')̂ = 2πiξ f̂(ξ)
4. 卷积: (f*g)̂ = f̂·ĝ

#### 定理 19.2 (Plancherel定理)
**Theorem 19.2 (Plancherel's Theorem)**

Fourier变换是L²(ℝ)上的酉算子:
```
||f̂||_{L²} = ||f||_{L²}
```

*推论*: Parseval等式 ∫|f|² = ∫|f̂|²

---

### 6.3 分布理论 [42Axx]

#### 定义 XIX.3.1 (测试函数与分布)
**Definition XIX.3.1 (Test Functions and Distributions)**

**测试函数空间**: C_c^∞(ℝ) (无限可微、紧支集)

**分布**: 测试函数空间上的连续线性泛函

**正则分布**: Tf(φ) = ∫ f(x)φ(x) dx

**Dirac delta**: δ(φ) = φ(0)

**分布导数**: (D^α T)(φ) = (-1)^{|α|} T(D^α φ)

**例子**: δ' (偶极子分布)

#### 定理 19.3 (Schwartz核定理)
**Theorem 19.3 (Schwartz Kernel Theorem)**

每个连续线性算子T: C_c^∞(X) → D'(Y)有分布核K ∈ D'(X×Y)使得:
```
(Tφ, ψ) = ⟨K, ψ ⊗ φ⟩
```

---

## Lean4 代码示例

本节提供与第二卷（分析与微分方程）内容相关的Lean4代码示例。

### 1. 实数与极限

```lean4
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Analysis.SpecificLimits

-- 实数的完备性
example : ∃ (x : ℝ), x ^ 2 = 2 := by
  use Real.sqrt 2
  exact Real.sq_sqrt (by norm_num : 0 ≤ 2)

-- 序列极限的定义
example (a : ℕ → ℝ) (l : ℝ) : 
    Filter.Tendsto a Filter.atTop (nhds l) ↔ 
    ∀ ε > 0, ∃ N, ∀ n ≥ N, |a n - l| < ε := by
  exact Metric.tendsto_atTop

-- 收敛序列的性质
example (a b : ℕ → ℝ) (la lb : ℝ) (ha : Tendsto a atTop (nhds la)) 
    (hb : Tendsto b atTop (nhds lb)) :
    Tendsto (a + b) atTop (nhds (la + lb)) := by
  exact Tendsto.add ha hb

-- 乘法保持收敛
example (a b : ℕ → ℝ) (la lb : ℝ) (ha : Tendsto a atTop (nhds la)) 
    (hb : Tendsto b atTop (nhds lb)) :
    Tendsto (a * b) atTop (nhds (la * lb)) := by
  exact Tendsto.mul ha hb

-- 单调有界数列收敛
example (a : ℕ → ℝ) (hmono : Monotone a) (hbdd : BddAbove (Set.range a)) :
    ∃ l, Tendsto a atTop (nhds l) := by
  exact ⟨_, hmono.tendsto hbdd⟩

-- e的定义
example : Tendsto (fun n => (1 + 1/n) ^ n) atTop (nhds Real.e) := by
  exact Real.tendsto_one_div_n_add_one_pow_n
```

### 2. 函数的连续性与微分

```lean4
import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.Calculus.MeanValue

-- 连续性的定义
example (f : ℝ → ℝ) (x : ℝ) : 
    ContinuousAt f x ↔ ∀ ε > 0, ∃ δ > 0, ∀ y, |y - x| < δ → |f y - f x| < ε := by
  exact Metric.continuity_at_iff

-- 导数的定义
example (f : ℝ → ℝ) (x : ℝ) : 
    HasDerivAt f (deriv f x) x ↔ Tendsto (fun h => (f (x + h) - f x) / h) (𝓝 0) (nhds (deriv f x)) := by
  constructor
  · intro h
    exact h.tendsto_div
  · intro h
    exact HasDerivAt.of_tendsto_div h

-- 常数的导数为0
example (c : ℝ) : deriv (fun _ => c) = 0 := by
  ext x
  exact deriv_const x c

-- 线性函数的导数
example (a b : ℝ) : deriv (fun x => a * x + b) = a := by
  ext x
  exact deriv_id x |>.mul_const a

-- 链式法则
example (f g : ℝ → ℝ) (x : ℝ) (hf : HasDerivAt f (deriv f x) x) 
    (hg : HasDerivAt g (deriv g (f x)) (f x)) :
    deriv (g ∘ f) x = deriv g (f x) * deriv f x := by
  exact (hg.comp x hf).deriv

-- 中值定理
example {f : ℝ → ℝ} {a b : ℝ} (hab : a < b) (hfc : ContinuousOn f (Icc a b))
    (hfd : DifferentiableOn ℝ f (Ioo a b)) :
    ∃ c ∈ Ioo a b, deriv f c = (f b - f a) / (b - a) := by
  exact exists_deriv_eq_slope f hab hfc hfd
```

### 3. 积分理论

```lean4
import Mathlib.MeasureTheory.Integral.Bochner
import Mathlib.MeasureTheory.Measure.Lebesgue

open MeasureTheory

-- 可测函数
example (f : ℝ → ℝ) : Measurable f ↔ ∀ s : Set ℝ, MeasurableSet s → MeasurableSet (f ⁻¹' s) := by
  exact measurable_iff

-- 简单函数的积分
example (f : ℝ → ℝ) (s : Finset ℝ) (hf : SimpleFunc.Equal f s) :
    ∫ x, f x = ∑ c ∈ s, c * (volume (f ⁻¹' {c})).toReal := by
  sorry  -- 简化示例

-- 积分的线性性
example (f g : ℝ → ℝ) (a b : ℝ) : 
    ∫ x, a * f x + b * g x = a * ∫ x, f x + b * ∫ x, g x := by
  sorry  -- 需要可积性条件

-- 单调收敛定理
example (f : ℕ → ℝ → ℝ) (hf : ∀ n, Measurable (f n)) 
    (hmono : ∀ n x, f n x ≤ f (n + 1) x) :
    Tendsto (fun n => ∫ x, f n x) atTop (nhds (∫ x, (fun x => Sup {y | ∃ n, f n x = y}) x)) := by
  sorry  -- 需要非负条件

-- 控制收敛定理
example (f : ℕ → ℝ → ℝ) (g : ℝ → ℝ) (hf : ∀ n, Measurable (f n))
    (hfg : ∀ n x, |f n x| ≤ g x) (hg : Integrable g) :
    Tendsto (fun n => ∫ x, f n x) atTop (nhds (∫ x, (fun x => lim (fun n => f n x)) x)) := by
  sorry  -- 需要逐点收敛条件
```

### 4. 复分析

```lean4
import Mathlib.Analysis.Complex.CauchyIntegral
import Mathlib.Analysis.Complex.Polynomial.Basic

-- 全纯函数
open Complex

example (f : ℂ → ℂ) (z : ℂ) : 
    DifferentiableAt ℂ f z ↔ ∃ c, Tendsto (fun h => (f (z + h) - f z) / h) (𝓝 0) (nhds c) := by
  constructor
  · intro h
    exact ⟨deriv f z, h.hasDerivAt.tendsto_div⟩
  · intro ⟨c, hc⟩
    exact DifferentiableAt.of_tendsto_div hc

-- Cauchy-Riemann方程
example (f : ℂ → ℂ) (z : ℂ) (hf : DifferentiableAt ℂ f z) :
    let u := fun x y => (f ⟨x, y⟩).re
    let v := fun x y => (f ⟨x, y⟩).im
    (deriv (fun x => u x z.im) z.re = deriv (fun y => v z.re y) z.im) ∧
    (deriv (fun y => u z.re y) z.im = -deriv (fun x => v x z.im) z.re) := by
  intro u v
  constructor <;> sorry  -- 简化示例

-- 最大模原理
example (f : ℂ → ℂ) (hf : DifferentiableOn ℂ f (ball 0 1)) 
    (hmax : IsMaxOn |f| (ball 0 1) 0) :
    ∃ c, ∀ z ∈ ball 0 1, f z = c := by
  sorry  -- 简化示例

-- Liouville定理
example (f : ℂ → ℂ) (hf : Differentiable ℂ f) (hbdd : ∃ M, ∀ z, |f z| ≤ M) :
    ∃ c, ∀ z, f z = c := by
  sorry  -- 简化示例
```

### 5. Fourier分析

```lean4
import Mathlib.Analysis.Fourier.FourierTransform

-- Fourier系数（简化版）
-- 对于周期函数，Fourier系数定义为积分

-- Fourier变换的基本性质
example (f : ℝ → ℂ) (hf : Integrable f) (ξ : ℝ) :
    (∫ x, f x * cexp (-2 * Real.pi * Complex.I * ξ * x)) = 
    (∫ x, f x * cexp (2 * Real.pi * Complex.I * ξ * x)) := by
  sorry  -- 需要对称性条件

-- 平移性质
example (f : ℝ → ℂ) (a : ℝ) (hf : Integrable f) :
    (∫ ξ, (∫ x, f (x - a) * cexp (-2 * Real.pi * Complex.I * ξ * x)) * 
           cexp (2 * Real.pi * Complex.I * ξ * 0)) = 
    (∫ ξ, cexp (-2 * Real.pi * Complex.I * ξ * a) * 
           (∫ x, f x * cexp (-2 * Real.pi * Complex.I * ξ * x))) := by
  sorry  -- 简化示例

-- Parseval定理（简化版）
example (f : ℝ → ℂ) (hf : Memℒp f 2 volume) :
    (∫ x, |f x| ^ 2) = ∫ ξ, |∫ x, f x * cexp (-2 * Real.pi * Complex.I * ξ * x)| ^ 2 := by
  sorry  -- 需要Plancherel定理
```

### 6. 偏微分方程（热传导方程）

```lean4
import Mathlib.Analysis.PDE.HeatEquation

-- 热传导方程的解（简化示例）
-- ∂u/∂t = α ∂²u/∂x²

-- 热传导方程的基本解
example (α : ℝ) (hα : α > 0) :
    let G := fun x t => (4 * Real.pi * α * t) ^ (-1/2) * Real.exp (-x^2 / (4 * α * t))
    ∀ t > 0, (∫ x, G x t) = 1 := by
  intro α hα G t ht
  sorry  -- Gauss积分

-- 极值原理
example (u : ℝ → ℝ → ℝ) (h : ∀ x t, 0 < t → t < 1 → 
    ∂ u x t / ∂t = ∂² u x t / ∂x²) :
    (∀ x t, 0 < t → t < 1 → u x t ≤ Sup {y | ∃ x₀, (y = u x₀ 0) ∨ (∃ t₀ < 1, y = u x₀ t₀)}) := by
  sorry  -- 极值原理
```

### 7. 动力系统基础

```lean4
import Mathlib.Dynamics.OmegaLimit

-- 轨道的定义
def orbit {X : Type*} (T : X → X) (x : X) : Set X := {y | ∃ n : ℕ, (T^[n]) x = y}

-- ω-极限集
def omegaLimit {X : Type*} [TopologicalSpace X] (T : X → X) (x : X) : Set X :=
  ⋂ n, closure {y | ∃ m ≥ n, (T^[m]) x = y}

-- 不动点
example {X : Type*} (T : X → X) (x : X) : T x = x ↔ x ∈ {y | T y = y} := by
  rfl

-- 周期点
def isPeriodicPt {X : Type*} (T : X → X) (n : ℕ) (x : X) : Prop := 
  n > 0 ∧ (T^[n]) x = x

-- 周期点的不动点
example {X : Type*} (T : X → X) (x : X) (n : ℕ) (h : isPeriodicPt T n x) :
    (T^[n * k]) x = x := by
  intro k
  induction k with
  | zero => simp
  | succ k ih => 
    rw [Nat.mul_succ, Nat.add_comm n k, Function.iterate_add]
    rw [h.2]
    exact ih
```

---

## 参考文献

### 实分析
1. Rudin, W., *Principles of Mathematical Analysis*, 3rd ed., McGraw-Hill, 1976
2. Royden, H.L., Fitzpatrick, P., *Real Analysis*, 4th ed., Pearson, 2010

### 测度论
3. Folland, G.B., *Real Analysis: Modern Techniques and Their Applications*, 2nd ed., Wiley, 1999
4. Rudin, W., *Real and Complex Analysis*, 3rd ed., McGraw-Hill, 1987

### 复分析
5. Ahlfors, L.V., *Complex Analysis*, 3rd ed., McGraw-Hill, 1979
6. Conway, J.B., *Functions of One Complex Variable*, 2nd ed., Springer, 1978

### PDE
7. Evans, L.C., *Partial Differential Equations*, 2nd ed., AMS, 2010
8. Gilbarg, D., Trudinger, N.S., *Elliptic Partial Differential Equations of Second Order*, Springer, 2001

### 动力系统
9. Katok, A., Hasselblatt, B., *Introduction to the Modern Theory of Dynamical Systems*, Cambridge, 1995
10. Walters, P., *An Introduction to Ergodic Theory*, Springer, 2000

### Fourier分析
11. Stein, E.M., Shakarchi, R., *Fourier Analysis: An Introduction*, Princeton, 2003
12. Grafakos, L., *Classical Fourier Analysis*, 3rd ed., Springer, 2014

---

**注**: 本文档是第二卷，涵盖了分析学的核心内容。

---

*本卷完成日期: 2025-03-26*  
*下一卷预告: 泛函分析与算子理论*
