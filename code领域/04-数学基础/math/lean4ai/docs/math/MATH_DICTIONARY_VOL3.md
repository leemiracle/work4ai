# 数学知识词典 - 第三卷：泛函分析与算子理论
## Volume III: Functional Analysis and Operator Theory

**MSC分类**: 46-XX, 47-XX, 49-XX  
**版本**: 1.0  
**日期**: 2025-03-26

---

## 目录

1. [拓扑线性空间 (46-XX)](#1-拓扑线性空间)
2. [Banach空间 (46-XX)](#2-banach空间)
3. [Hilbert空间 (46-XX)](#3-hilbert空间)
4. [算子理论 (47-XX)](#4-算子理论)
5. [算子代数 (46-XX, 47-XX)](#5-算子代数)
6. [变分法 (49-XX)](#6-变分法)

---

## 1. 拓扑线性空间 (46-XX)

### 1.1 基本概念 [46Axx]

#### 定义 XX.1.1 (拓扑线性空间)
**Definition XX.1.1 (Topological Vector Spaces)**

**拓扑线性空间** (TVS) X 是向量空间配备Hausdorff拓扑，使得:
1. 加法 (x,y) ↦ x+y: X×X → X 连续
2. 标量乘法 (α,x) ↦ αx: 𝔽×X → X 连续

**局部凸空间** (LCS): 0点有凸邻域基

**例子**:
- 赋范空间
- Fréchet空间 (完备可度量LCS)
- 分布空间 D'(Ω)
- 测试函数空间 C_c^∞(Ω)

#### 定义 XX.1.2 (半范数)
**Definition XX.1.2 (Seminorms)**

**半范数** p: X → [0,∞) 满足:
1. p(αx) = |α|p(x)
2. p(x+y) ≤ p(x)+p(y)

**范数**: 半范数 + p(x) = 0 ⟹ x = 0

**定理**: LCS的拓扑可由半范数族{p_α}生成。

---

### 1.2 对偶空间 [46Axx]

#### 定义 XX.2.1 (对偶空间)
**Definition XX.2.1 (Dual Spaces)**

**代数对偶**: X* = {线性泛函f: X → 𝔽}

**拓扑对偶** (连续对偶): X' = {连续线性泛函}

**例子**:
- (ℓ^p)' = ℓ^q (1/p + 1/q = 1)
- (L^p(μ))' = L^q(μ) (1 < p < ∞)
- (c₀)' = ℓ¹
- (C[0,1])' = M[0,1] (Radon测度)

#### 定理 20.1 (Hahn-Banach定理)
**Theorem 20.1 (Hahn-Banach Theorem)**

**解析形式**: 设p是向量空间X上的次线性泛函，f是子空间Y上的线性泛函满足f ≤ p|_Y。则存在F ∈ X*使得F|_Y = f且F ≤ p。

**几何形式**: 设A,B ⊆ X是凸集，A开，A∩B = ∅。则存在闭超平面H分离A和B。

*推论*:
1. 非零连续泛函存在
2. 凸集的闭包 = 弱闭包
3. 分离定理

*证明*. Zorn引理。 □

---

## 2. Banach空间 (46-XX)

### 2.1 基本性质 [46Bxx]

#### 定义 XXI.1.1 (Banach空间)
**Definition XXI.1.1 (Banach Spaces)**

**Banach空间**: 完备赋范空间

**例子**:
- L^p(μ) (1 ≤ p ≤ ∞)
- C(X) (紧空间X上的连续函数，上确界范数)
- ℓ^p (序列空间)
- c₀ (收敛到0的序列)

#### 定理 21.1 (开映射定理)
**Theorem 21.1 (Open Mapping Theorem)**

Banach空间之间的满连续线性算子是开映射。

*等价形式*: 
1. **闭图像定理**: T: X → Y线性，X,Y Banach ⟹ T连续 ⟺ G(T)闭
2. **有界逆定理**: 双射连续线性算子有连续逆

*证明*. Baire纲定理。 □

#### 定理 21.2 (一致有界原理)
**Theorem 21.2 (Uniform Boundedness Principle)**

设{T_α}是Banach空间X到赋范空间Y的有界线性算子族。若sup_α ||T_α(x)|| < ∞对所有x ∈ X，则sup_α ||T_α|| < ∞。

*证明*. Baire纲定理。 □

---

### 2.2 对偶与自反性 [46Bxx]

#### 定义 XXI.2.1 (自反性)
**Definition XXI.2.1 (Reflexivity)**

**典范嵌入**: J: X → X''，J(x)(f) = f(x)

**自反**: J是满射（即X ≅ X''）

**例子**:
- 自反: L^p (1 < p < ∞), ℓ^p (1 < p < ∞), Hilbert空间
- 不自反: L¹, L^∞, ℓ¹, c₀

#### 定理 21.3 (Pettis定理)
**Theorem 21.3 (Pettis' Theorem)**

Banach空间X自反 ⟺ X的闭单位球弱紧。

*证明*. Alaoglu定理 + Goldstine定理。 □

---

### 2.3 弱拓扑 [46Axx]

#### 定义 XXI.3.1 (弱拓扑)
**Definition XXI.3.1 (Weak Topologies)**

**弱拓扑** σ(X,X'): X上使所有f ∈ X'连续的最弱拓扑

**弱*拓扑** σ(X',X): X'上使所有J(x)连续的最弱拓扑

**弱收敛**: x_n →^w x ⟺ f(x_n) → f(x) 对所有f ∈ X'

#### 定理 21.4 (Alaoglu定理)
**Theorem 21.4 (Alaoglu's Theorem)**

赋范空间X的对偶空间X'的闭单位球在弱*拓扑中紧。

*证明*. Tychonoff定理。 □

#### 定理 21.5 (Eberlein-Šmulian定理)
**Theorem 21.5 (Eberlein-Šmulian Theorem)**

Banach空间的子集W相对弱紧 ⟺ W的每个序列有弱收敛子列。

---

### 2.4 凸性与最佳逼近 [46Bxx]

#### 定义 XXI.4.1 (最佳逼近)
**Definition XXI.4.1 (Best Approximation)**

对闭凸集K ⊆ X和x ∈ X，**最佳逼近**是P_K(x) ∈ K使得:
```
||x - P_K(x)|| = inf_{y∈K} ||x - y||
```

#### 定理 21.6 (存在与唯一性)
**Theorem 21.6 (Existence and Uniqueness)**

1. 若K是Hilbert空间H的闭凸子集，则P_K(x)存在且唯一
2. 对Banach空间，存在性需要自反性，唯一性需要严格凸性

**刻画**: y₀ = P_K(x) ⟺ Re⟨x-y₀, y-y₀⟩ ≤ 0 对所有y ∈ K

---

## 3. Hilbert空间 (46-XX)

### 3.1 基本结构 [46Cxx]

#### 定义 XXII.1.1 (内积空间)
**Definition XXII.1.1 (Inner Product Spaces)**

**内积** ⟨·,·⟩: H×H → 𝔽 满足:
1. 线性性（第一个变量）
2. 共轭对称: ⟨x,y⟩ = ⟨y,x⟩̄
3. 正定性: ⟨x,x⟩ ≥ 0, 等号⟺x=0

**诱导范数**: ||x|| = √⟨x,x⟩

**Hilbert空间**: 完备内积空间

**Cauchy-Schwarz不等式**: |⟨x,y⟩| ≤ ||x|| ||y||

**平行四边形法则**: ||x+y||² + ||x-y||² = 2||x||² + 2||y||²

#### 定理 22.1 (极化恒等式)
**Theorem 22.1 (Polarization Identity)**

**实情形**: ⟨x,y⟩ = [||x+y||² - ||x-y||²]/4

**复情形**: ⟨x,y⟩ = [||x+y||² - ||x-y||² + i||x+iy||² - i||x-iy||²]/4

*意义*: 范数完全决定内积。

---

### 3.2 正交性与基 [46Cxx]

#### 定义 XXII.2.1 (正交性)
**Definition XXII.2.1 (Orthogonality)**

**正交**: x ⊥ y ⟺ ⟨x,y⟩ = 0

**正交补**: M^⊥ = {x : ⟨x,m⟩ = 0, ∀m ∈ M}

**标准正交系**: {e_n}使得⟨e_i,e_j⟩ = δ_{ij}

#### 定理 22.2 (投影定理)
**Theorem 22.2 (Projection Theorem)**

设M是Hilbert空间H的闭子空间。则:
1. H = M ⊕ M^⊥ (正交直和)
2. 对x ∈ H，存在唯一的P_M(x) ∈ M使得||x-P_M(x)||最小
3. P_M(x)是x在M上的正交投影

**刻画**: y = P_M(x) ⟺ y ∈ M 且 x-y ⊥ M

*证明*. 变分原理。 □

#### 定义 XXII.2.2 (标准正交基)
**Definition XXII.2.2 (Orthonormal Bases)**

**完全标准正交系** {e_n}: {e_n}^⊥ = {0}

**标准正交基**: 完全标准正交系

**等价条件**:
1. Span{e_n}稠密
2. Parseval等式: ||x||² = Σ |⟨x,e_n⟩|²
3. Fourier展开: x = Σ ⟨x,e_n⟩e_n

**例子**:
- ℓ²: 标准基 {e_n}
- L²[0,2π]: {e^{inx}/√(2π)}
- L²[-1,1]: Legendre多项式

#### 定理 22.3 (Gram-Schmidt正交化)
**Theorem 22.3 (Gram-Schmidt Orthogonalization)**

任意可数线性无关集{v_n}可化为标准正交系{e_n}使得Span{v₁,...,v_n} = Span{e₁,...,e_n}。

*公式*: e_n = [v_n - Σ_{k<n} ⟨v_n,e_k⟩e_k] / ||·||

---

### 3.3 Riesz表示定理 [46Cxx]

#### 定理 22.4 (Riesz表示定理)
**Theorem 22.4 (Riesz Representation Theorem)**

对Hilbert空间H上的每个连续线性泛函f ∈ H'，存在唯一的y_f ∈ H使得:
```
f(x) = ⟨x,y_f⟩  (对所有x ∈ H)
```
且||f|| = ||y_f||。

*意义*: H' ≅ H (反线性同构)

*证明*: 若f ≠ 0，取z ∈ Ker(f)^⊥，令y = ||z||²̄f(z)̄ z/||f(z)||²。 □

#### 定理 22.5 (Lax-Milgram定理)
**Theorem 22.5 (Lax-Milgram Theorem)**

设a(·,·)是Hilbert空间H上的有界强制双线性型:
- 有界: |a(x,y)| ≤ C||x|| ||y||
- 强制: Re a(x,x) ≥ α||x||² (α > 0)

则对每个f ∈ H'，存在唯一u ∈ H使得:
```
a(u,v) = f(v)  (对所有v ∈ H)
```

*证明*: Riesz表示 + Lax-Milgram算子。 □

---

## 4. 算子理论 (47-XX)

### 4.1 有界线性算子 [47Axx]

#### 定义 XXIII.1.1 (有界算子)
**Definition XXIII.1.1 (Bounded Operators)**

**有界线性算子** T: X → Y: 存在C使得||Tx|| ≤ C||x||对所有x

**算子范数**: ||T|| = sup_{||x||≤1} ||Tx|| = sup_{||x||=1} ||Tx||

**Banach代数** B(X): X上有界算子全体

**例子**:
- 积分算子: (Tf)(x) = ∫ K(x,y)f(y)dy
- 微分算子 (无界)
- 平移算子
- 乘法算子

#### 定理 23.1 (对偶算子)
**Theorem 23.1 (Dual Operators)**

**对偶算子** (伴随算子) T': Y' → X'定义为(T'f)(x) = f(Tx)。

**性质**:
1. ||T'|| = ||T||
2. (ST)' = T'S'
3. (T')' = T (X,Y自反时)

**Hilbert空间**: 存在Hilbert伴随T*满足⟨Tx,y⟩ = ⟨x,T*y⟩

---

### 4.2 谱理论 [47Axx]

#### 定义 XXIII.2.1 (谱)
**Definition XXIII.2.1 (Spectrum)**

对T ∈ B(X)，**预解集**: ρ(T) = {λ ∈ ℂ : T-λI可逆}

**谱**: σ(T) = ℂ \ ρ(T)

**分类**:
- **点谱** σ_p(T): 特征值 (T-λI不单射)
- **连续谱** σ_c(T): T-λI单射、稠密值域、不可逆
- **剩余谱** σ_r(T): T-λI单射、值域不稠密

#### 定理 23.2 (谱的基本性质)
**Theorem 23.2 (Properties of Spectrum)**

1. σ(T) ≠ ∅ (非空)
2. σ(T)是紧集，r(T) = max{|λ| : λ ∈ σ(T)} ≤ ||T||
3. 谱半径公式: r(T) = lim_{n→∞} ||T^n||^{1/n}
4. σ(T') = σ(T) (X自反时)

*证明*. Liouville定理（复分析）。 □

#### 定理 23.3 (谱映射定理)
**Theorem 23.3 (Spectral Mapping Theorem)**

对多项式p: σ(p(T)) = p(σ(T))

*推广*: 对解析函数f: σ(f(T)) = f(σ(T)) (函数演算)

---

### 4.3 紧算子 [47Axx]

#### 定义 XXIII.3.1 (紧算子)
**Definition XXIII.3.1 (Compact Operators)**

**紧算子** T: T(闭单位球)是相对紧集

**等价**: T将有界序列映射为有收敛子列的序列

**例子**:
- 有限秩算子
- Hilbert-Schmidt算子: ∫∫ |K(x,y)|² dxdy < ∞
- 单位球上的积分算子

#### 定理 23.4 (Fredholm二择一)
**Theorem 23.4 (Fredholm Alternative)**

设K是紧算子，λ ≠ 0。则以下恰有一个成立:
1. (T-λI)x = 0有非平凡解
2. (T-λI)x = y对所有y有唯一解

*等价*: dim Ker(T-λI) = codim Im(T-λI) < ∞

---

### 4.4 谱定理 [47Axx]

#### 定义 XXIII.4.1 (自伴算子)
**Definition XXIII.4.1 (Self-Adjoint Operators)**

**自伴**: T = T*
**正规**: TT* = T*T
**酉**: T*T = TT* = I

#### 定理 23.5 (有限维谱定理)
**Theorem 23.5 (Spectral Theorem - Finite Dimension)**

**自伴矩阵** A: 存在酉矩阵U使得U*AU = diag(λ₁,...,λₙ)

**正规矩阵**: 可对角化

#### 定理 23.6 (无限维谱定理)
**Theorem 23.6 (Spectral Theorem - Infinite Dimension)**

**Hilbert空间上的自伴算子** T，以下等价:

1. **谱测度形式**: T = ∫_σ(T) λ dE(λ) (投影值测度E)

2. **乘法算子形式**: 存在测度空间(X,μ)和实值函数f使得T酉等价于M_f

3. **函数演算**: 对Borel函数φ，φ(T)有定义且||φ(T)|| = sup_{λ∈σ(T)} |φ(λ)|

**应用**:
- 量子力学 (观测量 = 自伴算符)
- 极分解
- 算子的平方根

*证明*. Gelfand-Naimark定理 + Riesz-Markov。 □

---

## 5. 算子代数 (46-XX, 47-XX)

### 5.1 C*-代数 [46Lxx]

#### 定义 XXIV.1.1 (C*-代数)
**Definition XXIV.1.1 (C*-Algebras)**

**C*-代数** A 是Banach *-代数满足:
```
||a*a|| = ||a||²  (对所有a ∈ A)
```

**例子**:
- B(H) (Hilbert空间上有界算子)
- C(X) (紧空间X上的连续函数，f*(x) = f(x)̄)
- 紧算子代数 K(H)

#### 定理 24.1 (Gelfand-Naimark定理)
**Theorem 24.1 (Gelfand-Naimark Theorem)**

1. **交换情形**: 每个交换C*-代数同构于C₀(X)，X是局部紧Hausdorff空间

2. **一般情形**: 每个C*-代数等距*同构于某个B(H)的闭*子代数

*意义*: C*-代数 = 非交换拓扑

*证明*. Gelfand变换 + GNS构造。 □

---

### 5.2 von Neumann代数 [46Lxx]

#### 定义 XXIV.2.1 (von Neumann代数)
**Definition XXIV.2.1 (von Neumann Algebras)**

**von Neumann代数** (W*-代数): B(H)的*子代数M，在弱算子拓扑(WOT)中闭

#### 定理 24.2 (双换位子定理)
**Theorem 24.2 (Double Commutant Theorem)**

M ⊆ B(H)是von Neumann代数 ⟺ M = M'' = (M')'

其中M' = {T ∈ B(H) : TS = ST 对所有S ∈ M} (换位子)

#### 定义 XXIV.2.2 (因子)
**Definition XXIV.2.2 (Factors)**

**因子**: 中心Z(M) = M ∩ M' = ℂI

**分类** (Murray-von Neumann):
- **I型**: B(H)或B(H)⊗M_n
- **II型**: II₁ (有限), II_∞
- **III型**: III_λ (0 ≤ λ ≤ 1)

**应用**: 量子场论、统计力学

---

## 6. 变分法 (49-XX)

### 6.1 经典变分问题 [49Axx]

#### 定义 XXV.1.1 (泛函)
**Definition XXV.1.1 (Functionals)**

**泛函** J: V → ℝ (V是函数空间)

**例子**:
1. **弧长**: J[y] = ∫_a^b √(1 + y'²) dx
2. **Dirichlet能量**: J[u] = (1/2)∫ |∇u|² dx
3. **作用量**: J[q] = ∫ L(q,q̇,t) dt

#### 定理 25.1 (Euler-Lagrange方程)
**Theorem 25.1 (Euler-Lagrange Equation)**

**变分问题**: 极值化 J[y] = ∫_a^b L(x,y,y') dx (y(a), y(b)固定)

**必要条件** (Euler-Lagrange方程):
```
∂L/∂y - d/dx(∂L/∂y') = 0
```

*证明*. 设y_ε = y + εη (η(a)=η(b)=0)，则dJ/dε|_{ε=0} = 0导致分部积分。 □

**例子**:
1. **最速降线**: L = √[(1+y'²)/(2gy)] → y(1+y'²) = const (摆线)
2. **测地线**: L = √(g_{ij}ẋ^iẋ^j) → 测地线方程
3. **极小曲面**: L = √(1+|∇u|²) → 极小曲面方程

---

### 6.2 直接方法 [49Axx]

#### 定理 25.2 (变分的直接方法)
**Theorem 25.2 (Direct Method in Calculus of Variations)**

设J: V → ℝ满足:
1. **强制性**: J[v] → ∞ 当||v|| → ∞
2. **弱下半连续性**: v_n →^w v ⟹ J[v] ≤ liminf J[v_n]

则J在V中有极小值。

**证明**:
1. 取极小化序列{v_n}
2. 强制性 ⟹ {v_n}有界
3. 弱紧性 ⟹ 子列弱收敛到v
4. 弱下半连续性 ⟹ v是极小值 □

---

### 6.3 Lagrange乘子 [49Axx]

#### 定理 25.3 (约束极值)
**Theorem 25.3 (Constrained Extrema)**

**问题**: 极值化 J[v] 约束于 G[v] = 0

**Lagrange乘子定理**: 若v₀是极值点且DG(v₀)满射，则存在λ使得:
```
DJ(v₀) + λ DG(v₀) = 0
```

**应用**:
1. **特征值问题**: 极小化 ∫|∇u|² 约束于 ∫|u|² = 1
   → -Δu = λu (第一特征值)

2. **等周问题**: 固定周长极大化面积

---

### 6.4 Hamilton原理 [49Axx]

#### 定义 XXV.4.1 (Hamilton原理)
**Definition XXV.4.1 (Hamilton's Principle)**

**Hamilton原理**: 真实运动是作用量泛函的临界点
```
δ∫ L(q,q̇,t) dt = 0
```

**Legendre变换**: H(q,p) = p·q̇ - L(q,q̇,t), p = ∂L/∂q̇

**Hamilton方程**:
```
q̇ = ∂H/∂p
ṗ = -∂H/∂q
```

**例子**:
1. 谐振子: L = (m/2)q̇² - (k/2)q² → H = p²/(2m) + (k/2)q²
2. 刚体: Euler方程
3. 场论: Lagrange密度 ℒ(φ,∂μφ)

---

## Lean4 代码示例

本节提供与第三卷（泛函分析与算子理论）内容相关的Lean4代码示例。

### 1. 赋范空间与Banach空间

```lean4
import Mathlib.Analysis.NormedSpace.Basic
import Mathlib.Analysis.NormedSpace.Banach

-- 赋范空间的定义
example (E : Type*) [NormedAddCommGroup E] (x : E) : ‖x‖ = 0 ↔ x = 0 := by
  constructor
  · intro h
    rw [norm_eq_zero h]
  · intro h
    rw [h]

-- 范数的三角不等式
example (E : Type*) [SeminormedAddCommGroup E] (x y : E) : ‖x + y‖ ≤ ‖x‖ + ‖y‖ := by
  exact norm_add_le x y

-- 范数的齐次性
example (E : Type*) [NormedAddCommGroup E] (c : ℝ) (x : E) : ‖c • x‖ = |c| * ‖x‖ := by
  exact norm_smul c x

-- Banach空间的完备性
-- (在Lean4中，Banach空间通过CompleteSpace类型类表示)
example (E : Type*) [NormedAddCommGroup E] [CompleteSpace E] : 
    IsComplete (uniformOn E) := by
  exact Complete.is_complete
```

### 2. Hilbert空间

```lean4
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Analysis.InnerProductSpace.Projection

-- 内积的性质
example (H : Type*) [InnerProductSpace ℂ H] (x y : H) :
    reInner (inner x y) = inner y x := by
  exact inner_conj_symm x y

-- 内积与范数的关系
example (H : Type*) [InnerProductSpace ℝ H] (x : H) : ‖x‖² = inner x x := by
  exact norm_sq_eq_inner x

-- Cauchy-Schwarz不等式
example (H : Type*) [InnerProductSpace ℂ H] (x y : H) : 
    |inner x y| ≤ ‖x‖ * ‖y‖ := by
  exact abs_inner_le_norm x y

-- 平行四边形定律
example (H : Type*) [InnerProductSpace ℂ H] (x y : H) :
    ‖x + y‖² + ‖x - y‖² = 2 * (‖x‖² + ‖y‖²) := by
  exact parallelogram_law x y

-- 极化恒等式
example (H : Type*) [InnerProductSpace ℂ H] (x y : H) :
    inner x y = (‖x + y‖² - ‖x - y‖² + I * ‖x + I•y‖² - I * ‖x - I•y‖²) / 4 := by
  exact polar_identity x y

-- 正交投影
example (H : Type*) [InnerProductSpace ℂ H] [CompleteSpace H] 
    (K : Submodule ℂ H) (x : H) :
    ∃ y ∈ K, ∃ z ∈ Kᗮ, x = y + z ∧ ∀ w ∈ K, inner y z = 0 := by
  obtain ⟨y, hy⟩ := Submodule.exists_norm_eqInf_of_mem K x
  use y
  refine ⟨hy.1, ?_, ?_, ?_⟩
  · exact K.mem_orthogonal (norm_eqInf_of_mem K hy)
  · exact (norm_eqInf_add_mem_orthogonal K x hy).symm
  · intro w hw
    exact (K.inner_norm_eqInf_mem_orthogonal x y w hy hw).2
```

### 3. 有界线性算子

```lean4
import Mathlib.Analysis.NormedSpace.OperatorNorm
import Mathlib.Analysis.NormedSpace.ContinuousLinearMap

-- 有界线性算子的范数
example (E F : Type*) [NormedAddCommGroup E] [NormedAddCommGroup F]
    (T : E →L[ℝ] F) : ‖T‖ = sSup (Set.image (fun x => ‖T x‖ / ‖x‖) {x : E | x ≠ 0}) := by
  exact ContinuousLinearMap.opNorm_def' T

-- 算子范数的性质
example (E F : Type*) [NormedAddCommGroup E] [NormedAddCommGroup F]
    (T : E →L[ℝ] F) (x : E) : ‖T x‖ ≤ ‖T‖ * ‖x‖ := by
  exact ContinuousLinearMap.le_opNorm T x

-- 算子的有界性
example (E F : Type*) [NormedAddCommGroup E] [NormedAddCommGroup F]
    (T : E →L[ℝ] F) : Continuous T := by
  exact T.cont

-- Banach-Steinhaus定理 (一致有界原理)
import Mathlib.Analysis.NormedSpace.HahnBanach

example (E F : Type*) [NormedAddCommGroup E] [NormedAddCommGroup F]
    [CompleteSpace E] [CompleteSpace F]
    (S : Set (E →L[ℝ] F)) (h : ∀ x, BddAbove {n : ℝ | ∃ T ∈ S, n = ‖T x‖}) :
    BddAbove {n : ℝ | ∃ T ∈ S, n = ‖T‖} := by
  exact uniform_bounded_principle S h
```

### 4. 对偶空间与Hahn-Banach定理

```lean4
import Mathlib.Analysis.NormedSpace.Dual

-- 对偶空间的定义
example (E : Type*) [NormedAddCommGroup E] : 
    NormedAddCommGroup (Dual ℝ E) := by
  infer_instance

-- Hahn-Banach延拓定理
example (E : Type*) [SeminormedAddCommGroup E] (p : E →L[ℝ] ℝ) 
    (φ : ℝ →L[ℝ] ℝ) (H : ℝ →L[ℝ] E) (h : ∀ x, p x ≤ φ x) :
    ∃ ψ : E →L[ℝ] ℝ, (∀ x, ψ (H x) = φ x) ∧ (∀ x, ψ x ≤ p x) := by
  sorry  -- 需要更多技术设置

-- 范数的对偶表示
example (E : Type*) [NormedAddCommGroup E] [CompleteSpace E] (x : E) :
    ‖x‖ = sSup {‖φ x‖ / ‖φ‖ | φ : E →L[ℝ] ℝ, φ ≠ 0} := by
  sorry  -- 技术性证明

-- 对偶空间的对偶
example (E : Type*) [NormedAddCommGroup E] [CompleteSpace E] 
    [FiniteDimensional ℝ E] : 
    Nonempty (E ≃L[ℝ] Dual ℝ (Dual ℝ E)) := by
  exact ⟨FiniteDimensional.equivDualDual ℝ E⟩
```

### 5. 谱理论初步

```lean4
import Mathlib.Analysis.NormedSpace.Spectrum
import Mathlib.Analysis.NormedSpace.BoundedLinearMaps

-- 谱的定义
example (E : Type*) [NormedAddCommGroup E] [CompleteSpace E]
    (T : E →L[ℂ] E) : 
    spectrum ℂ E T = {λ : ℂ | ¬IsUnit (T - (λ • 1 : E →L[ℂ] E))} := by
  rfl

-- 谱半径
example (E : Type*) [NormedAddCommGroup E] [CompleteSpace E]
    (T : E →L[ℂ] E) :
    spectralRadius T = sSup (Set.image Complex.abs (spectrum ℂ E T)) := by
  rfl

-- 谱半径公式 (Gelfand)
example (E : Type*) [NormedAddCommGroup E] [CompleteSpace E]
    (T : E →L[ℂ] E) :
    Tendsto (fun n => ‖T ^ n‖ ^ (1/n : ℕ → ℝ)) atTop (nhds (spectralRadius T)) := by
  sorry  -- 技术性证明

-- 有限维空间的谱
example (n : Type*) [Fintype n] (T : Matrix n n ℂ) :
    spectrum ℂ (EuclideanSpace ℂ n) T.toLin' = Set.range T.eigenvalues := by
  sorry
```

### 6. 紧算子

```lean4
import Mathlib.Analysis.NormedSpace.CompactOperator

-- 紧算子的定义
example (E F : Type*) [NormedAddCommGroup E] [NormedAddCommGroup F]
    [CompleteSpace F] (T : E →L[ℝ] F) :
    IsCompactMap T ↔ Bornology.IsBounded (Set.image T (Metric.ball 0 1)) := by
  sorry  -- 需要展开定义

-- 有限秩算子是紧的
example (E F : Type*) [NormedAddCommGroup E] [NormedAddCommGroup F]
    [CompleteSpace F] (T : E →L[ℝ] F) [FiniteDimensional ℝ T.range] :
    IsCompactMap T := by
  exact IsCompactMap.of_finiteDimensional_range T

-- 紧算子的复合
example (E F G : Type*) [NormedAddCommGroup E] [NormedAddCommGroup F] [NormedAddCommGroup G]
    [CompleteSpace F] [CompleteSpace G]
    (T : E →L[ℝ] F) (S : F →L[ℝ] G) (hT : IsCompactMap T) :
    IsCompactMap (T.comp S) := by
  sorry
```

### 7. 自伴算子

```lean4
import Mathlib.Analysis.InnerProductSpace.Adjoint

-- 伴随算子
example (H : Type*) [InnerProductSpace ℂ H] [CompleteSpace H]
    (T : H →L[ℂ] H) :
    ∃ T' : H →L[ℂ] H, ∀ x y, inner (T x) y = inner x (T' y) := by
  exact ⟨ContinuousLinearMap.adjoint T, ContinuousLinearMap.inner_adj T⟩

-- 自伴算子的定义
example (H : Type*) [InnerProductSpace ℂ H] [CompleteSpace H]
    (T : H →L[ℂ] H) :
    T.IsSelfAdjoint ↔ ContinuousLinearMap.adjoint T = T := by
  rfl

-- 自伴算子的谱是实数
example (H : Type*) [InnerProductSpace ℂ H] [CompleteSpace H]
    (T : H →L[ℂ] H) (hT : T.IsSelfAdjoint) :
    ∀ λ ∈ spectrum ℂ H T, Im λ = 0 := by
  sorry  -- 技术性证明

-- 自伴算子的Rayleigh商
example (H : Type*) [InnerProductSpace ℂ H] [CompleteSpace H]
    (T : H →L[ℂ] H) (hT : T.IsSelfAdjoint) :
    sSup {reInner (inner x (T x)) / ‖x‖² | x : H, x ≠ 0} = 
    sSup (Set.image Complex.re (spectrum ℂ H T)) := by
  sorry
```

---

## 参考文献

### 泛函分析
1. Rudin, W., *Functional Analysis*, 2nd ed., McGraw-Hill, 1991
2. Conway, J.B., *A Course in Functional Analysis*, 2nd ed., Springer, 1990
3. Reed, M., Simon, B., *Methods of Modern Mathematical Physics*, Vol. 1-4, Academic Press
4. Brezis, H., *Functional Analysis, Sobolev Spaces and Partial Differential Equations*, Springer, 2011

### 算子理论
5. Kato, T., *Perturbation Theory for Linear Operators*, Springer, 1995
6. Douglas, R.G., *Banach Algebra Techniques in Operator Theory*, 2nd ed., Springer, 1998

### 算子代数
7. Murphy, G.J., *C*-Algebras and Operator Theory*, Academic Press, 1990
8. Takesaki, M., *Theory of Operator Algebras I-III*, Springer
9. Kadison, R.V., Ringrose, J.R., *Fundamentals of the Theory of Operator Algebras*, Vol. 1-4, Academic Press

### 变分法
10. Struwe, M., *Variational Methods*, 4th ed., Springer, 2008
11. Giaquinta, M., Hildebrandt, S., *Calculus of Variations I-II*, Springer, 1996
12. Dacorogna, B., *Direct Methods in the Calculus of Variations*, 2nd ed., Springer, 2008

### 综合参考
13. Lax, P.D., *Functional Analysis*, Wiley, 2002
14. Yosida, K., *Functional Analysis*, 6th ed., Springer, 1980

---

**注**: 本文档是第三卷，涵盖了泛函分析的核心内容。

---

*本卷完成日期: 2025-03-26*  
*下一卷预告: 几何与拓扑*
