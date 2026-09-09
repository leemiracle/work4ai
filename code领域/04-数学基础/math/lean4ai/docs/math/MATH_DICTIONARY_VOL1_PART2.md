# 数学知识词典 - 第一卷：基础与代数（第二部分）
## Volume I: Foundations and Algebra (Part 2)

**MSC分类**: 12-XX, 13-XX, 15-XX, 16-XX, 17-XX, 18-XX, 19-XX, 20-XX  
**版本**: 1.0  
**日期**: 2025-03-26

---

## 目录

1. [域论 (12-XX)](#1-域论)
2. [交换代数 (13-XX)](#2-交换代数)
3. [线性代数与多重线性代数 (15-XX)](#3-线性代数与多重线性代数)
4. [结合环与代数 (16-XX)](#4-结合环与代数)
5. [非结合环与代数 (17-XX)](#5-非结合环与代数)
6. [范畴论 (18-XX)](#6-范畴论)
7. [K-理论 (19-XX)](#7-k-理论)
8. [群论 (20-XX)](#8-群论)

---

## 1. 域论 (12-XX)

### 1.1 域扩张基础 [12Fxx]

#### 定义 V.1.1 (域扩张)
**Definition V.1.1 (Field Extensions)**

**域扩张** K/F 是域对(F, K)使得F是K的子域。

**记号**: 
- [K:F] = dim_F K (扩张次数)
- 有限扩张: [K:F] < ∞
- 无限扩张: [K:F] = ∞

**例子**:
- ℂ/ℝ: [ℂ:ℝ] = 2
- ℚ(√2)/ℚ: [ℚ(√2):ℚ] = 2
- ℝ/ℚ: 无限扩张

#### 定理 5.1 (塔定理)
**Theorem 5.1 (Tower Law)**

若 F ⊆ L ⊆ K 是域扩张，则:
```
[K:F] = [K:L][L:F]
```

*证明*. 若{αᵢ}是L/F的基，{βⱼ}是K/L的基，则{αᵢβⱼ}是K/F的基。 □

#### 定义 V.1.2 (代数元与超越元)
**Definition V.1.2 (Algebraic and Transcendental Elements)**

α ∈ K 称为F上的:
- **代数元** (algebraic): 存在非零f(x) ∈ F[x]使f(α) = 0
- **超越元** (transcendental): 不是代数元

**极小多项式**: 代数元α的次数最低的首一多项式m_α(x) ∈ F[x]

**例子**:
- √2在ℚ上代数，m(x) = x² - 2
- π, e在ℚ上超越 (Lindemann, 1882; Hermite, 1873)

#### 定理 5.2 (单扩张的结构)
**Theorem 5.2 (Structure of Simple Extensions)**

**代数扩张**: F(α) ≅ F[x]/(m_α(x))，[F(α):F] = deg m_α

**超越扩张**: F(α) ≅ F(x) (有理函数域)

*证明*. 
- 代数情形: 将α映到x，核为(m_α)
- 超越情形: F[α] ≅ F[x]，局部化得F(α) ≅ F(x) □

---

### 1.2 可分与正规扩张 [12Fxx]

#### 定义 V.2.1 (可分扩张)
**Definition V.2.1 (Separable Extensions)**

代数扩张K/F称为**可分的** (separable) 如果每个α ∈ K的极小多项式在分裂域中无重根。

**特征0**: 所有扩张可分
**特征p**: α可分 ⟺ m_α(x)与m_α'(x)互素

#### 定义 V.2.2 (正规扩张)
**Definition V.2.2 (Normal Extensions)**

代数扩张K/F称为**正规的** (normal) 如果每个不可约多项式f(x) ∈ F[x]在K中有根，则在K中完全分裂。

**等价**: K是某族多项式在F上的分裂域。

#### 定理 5.3 (有限扩张的性质)
**Theorem 5.3 (Properties of Finite Extensions)**

对有限扩张K/F，以下等价:
1. K/F是Galois扩张 (可分且正规)
2. |Aut(K/F)| = [K:F]
3. K是某个可分多项式在F上的分裂域

---

### 1.3 Galois理论 [12Fxx]

#### 定义 V.3.1 (Galois群)
**Definition V.3.1 (Galois Groups)**

**Galois群**: Gal(K/F) = Aut(K/F) (K的保持F不动的自同构群)

**基本例子**:
- Gal(ℂ/ℝ) ≅ ℤ/2ℤ (共轭)
- Gal(ℚ(√2)/ℚ) ≅ ℤ/2ℤ (√2 ↦ ±√2)
- Gal(ℚ(√2,√3)/ℚ) ≅ ℤ/2ℤ × ℤ/2ℤ

#### 定理 5.4 (Galois基本定理)
**Theorem 5.4 (Fundamental Theorem of Galois Theory)**

设K/F是有限Galois扩张，G = Gal(K/F)。则:

1. **反序对应**: 存在双射
```
{中间域 E: F ⊆ E ⊆ K} ⟷ {子群 H ≤ G}
E ↦ Gal(K/E)
K^H ↤ H
```
其中K^H = {x ∈ K : ∀σ ∈ H, σ(x) = x}

2. **次数关系**: [K:E] = |Gal(K/E)|, [E:F] = [G:H]

3. **正规性**: E/F是Galois ⟺ Gal(K/E) ◁ G
此时Gal(E/F) ≅ G/Gal(K/E)

*证明*. 见Lang, *Algebra*, Chapter 6. □

#### 应用5.1 (古典作图问题)

**定理 5.5** 以下用尺规不可作:
1. 倍立方: ³√2不可作 (度数3不是2的幂)
2. 三等分角: cos(20°)不可作 (度数3)
3. 化圆为方: √π不可作 (π超越)

*证明思路*: 可作数构成ℚ的2-幂次扩张塔。 □

#### 应用5.2 (五次方程不可解)

**定理 5.6 (Abel-Ruffini)** 一般五次方程不能用根式求解。

*证明*. 
1. 一般五次多项式的Galois群是S₅
2. S₅不可解 (A₅单)
3. 可解群对应可用根式求解 □

**可解群**: 有正规列G = G₀ ◁ G₁ ◁ ... ◁ Gₙ = {e}，商群是Abel群。

---

### 1.4 有限域 [12Exx]

#### 定理 5.7 (有限域的结构)
**Theorem 5.7 (Structure of Finite Fields)**

1. 有限域的阶必定是素数幂pⁿ
2. 对每个pⁿ存在唯一(同构意义下)的有限域𝔽_{pⁿ}
3. 𝔽_{pⁿ}是x^{pⁿ} - x在𝔽_p上的分裂域
4. Gal(𝔽_{pⁿ}/𝔽_p) ≅ ℤ/nℤ (由Frobenius自同构σ: x ↦ x^p生成)

*证明*. 见任何代数教材。 □

**子域**: 𝔽_{pᵐ} ⊆ 𝔽_{pⁿ} ⟺ m|n

---

## 2. 交换代数 (13-XX)

### 2.1 Noether环 [13Axx]

#### 定义 VI.1.1 (Noether环)
**Definition VI.1.1 (Noetherian Rings)**

环R称为**Noether的** 如果以下等价条件之一成立:
1. 每个理想是有限生成的 (ACC条件)
2. 理想的升链条件: I₁ ⊆ I₂ ⊆ ... 稳定
3. 非空理想集有极大元

**例子**:
- 域、PID、ℤ、F[x]都是Noether环
- ℤ[x₁,x₂,...]不是Noether环 (理想(x₁,x₂,...)不有限生成)

#### 定理 6.1 (Hilbert基定理)
**Theorem 6.1 (Hilbert's Basis Theorem)**

若R是Noether环，则R[x]是Noether环。

*推论*: k[x₁,...,xₙ]是Noether环 (k是域)。

*证明*. 设I ⊆ R[x]是理想。构造I中多项式首项系数生成的理想J ⊆ R。因R Noether，J = (a₁,...,aₘ)。设f₁,...,fₘ ∈ I的首项系数是a₁,...,aₘ。令d = max{deg fᵢ}。

对任意f ∈ I，若deg f ≥ d，可用fᵢ归纳降次。故I由{次数<d的多项式}和{f₁,...,fₘ}生成。前者有限(有限维R-空间)。 □

---

### 2.2 局部化 [13Bxx]

#### 定义 VI.2.1 (乘法封闭集)
**Definition VI.2.1 (Multiplicative Sets)**

S ⊆ R是**乘法封闭的** (multiplicative) 如果:
1. 1 ∈ S
2. s,t ∈ S ⟹ st ∈ S

#### 定义 VI.2.2 (局部化)
**Definition VI.2.2 (Localization)**

R关于S的**局部化**:
```
S^{-1}R = {r/s : r ∈ R, s ∈ S} / ~
其中 r₁/s₁ ~ r₂/s₂ ⟺ ∃t ∈ S: t(r₁s₂ - r₂s₁) = 0
```

**运算**: (r₁/s₁) + (r₂/s₂) = (r₁s₂+r₂s₁)/(s₁s₂), (r₁/s₁)(r₂/s₂) = (r₁r₂)/(s₁s₂)

**例子**:
- S = R \ P (P是素理想): 局部环R_P
- S = {s ∈ R : s非零因子}: 全商环
- R是整环，S = R\{0}: 分式域

#### 定理 6.2 (局部化的泛性质)
**Theorem 6.2 (Universal Property of Localization)**

设φ: R → A是环同态，使得φ(s)在A中可逆对所有s ∈ S。则存在唯一ψ: S^{-1}R → A使得ψ(r/1) = φ(r)。

---

### 2.3 维数理论 [13Cxx]

#### 定义 VI.3.1 (Krull维数)
**Definition VI.3.1 (Krull Dimension)**

环R的**Krull维数**:
```
dim R = sup{素理想链的长度}
= sup{n : P₀ ⊊ P₁ ⊊ ... ⊊ Pₙ}
```

**例子**:
- 域: dim = 0
- PID (不是域): dim = 1 (如ℤ, k[x])
- k[x₁,...,xₙ]: dim = n

#### 定理 6.3 (零点定理)
**Theorem 6.3 (Nullstellensatz)**

设k是代数闭域，I ⊆ k[x₁,...,xₙ]是理想。则:
```
I(V(I)) = √I = {f : f^m ∈ I 对某m}
```
其中V(I) = {P ∈ kⁿ : f(P) = 0 ∀f ∈ I}

**强形式**: 建立了代数集与根理想的反序对应。

*证明*. 见Eisenbud, *Commutative Algebra*, Chapter 4. □

---

### 2.4 正则序列与深度 [13Cxx]

#### 定义 VI.4.1 (正则序列)
**Definition VI.4.1 (Regular Sequences)**

R中序列x₁,...,xₙ称为**正则的** (regular) 如果:
1. x₁在R中非零因子
2. 对i > 1，xᵢ在R/(x₁,...,x_{i-1})中非零因子
3. (x₁,...,xₙ) ≠ R

**例子**:
- (x,y)在k[x,y,z]中正则
- (x,xy)不正则 (xy在R/(x) = k[y,z]中是零因子)

#### 定义 VI.4.2 (深度)
**Definition VI.4.2 (Depth)**

R-模M的**深度**: depth(M) = 最长正则序列的长度

**Auslander-Buchsbaum公式**: 对Noether局部环(R,m)上的有限生成模M:
```
depth(M) + pd(M) = depth(R)
```
其中pd(M)是投射维数。

---

## 3. 线性代数与多重线性代数 (15-XX)

### 3.1 向量空间与线性映射 [15Axx]

#### 定义 VII.1.1 (向量空间)
**Definition VII.1.1 (Vector Spaces)**

**向量空间** V over域F是Abel群(V,+)带标量乘法F×V→V，满足:
1. α(u+v) = αu+αv
2. (α+β)v = αv+βv
3. (αβ)v = α(βv)
4. 1v = v

**线性映射**: T: V → W满足T(αu+βv) = αT(u)+βT(v)

**核与像**:
- Ker(T) = {v : T(v) = 0}
- Im(T) = {T(v) : v ∈ V}

#### 定理 7.1 (秩-零度定理)
**Theorem 7.1 (Rank-Nullity Theorem)**

对线性映射T: V → W (dim V < ∞):
```
dim V = dim Ker(T) + dim Im(T)
```

*证明*. 取Ker(T)的基{v₁,...,vₖ}，扩充为V的基{v₁,...,vₙ}。则{T(v_{k+1}),...,T(vₙ)}是Im(T)的基。 □

---

### 3.2 矩阵与行列式 [15Axx]

#### 定义 VII.2.1 (行列式)
**Definition VII.2.1 (Determinants)**

n×n矩阵A = (a_{ij})的**行列式**:
```
det A = Σ_{σ∈Sₙ} sgn(σ) ∏_{i=1}^n a_{i,σ(i)}
```

**性质**:
1. det(AB) = det(A)det(B)
2. det(A^T) = det(A)
3. det(A⁻¹) = 1/det(A)
4. A可逆 ⟺ det(A) ≠ 0

#### 定理 7.2 (特征多项式)
**Theorem 7.2 (Characteristic Polynomial)**

A的特征多项式: p_A(λ) = det(λI - A)

**Cayley-Hamilton定理**: p_A(A) = 0

*证明*. 对三角矩阵显然。一般情况: 相似于Jordan型。 □

---

### 3.3 特征值与对角化 [15Axx]

#### 定义 VII.3.1 (特征值与特征向量)
**Definition VII.3.1 (Eigenvalues and Eigenvectors)**

**特征值** λ: 存在非零向量v使Av = λv

**特征向量**: 对应的v

**特征空间**: E_λ = {v : Av = λv} = Ker(A - λI)

**谱**: σ(A) = {A的特征值}

#### 定理 7.3 (谱定理)
**Theorem 7.3 (Spectral Theorem)**

**实对称矩阵**: A = A^T ⟹ 存在正交矩阵Q使得Q^TAQ = diag(λ₁,...,λₙ)

**等价条件**:
1. A = A^T
2. A有正交特征向量基
3. A可正交对角化

**证明思路**:
1. 特征值存在(代数基本定理+实对称 ⟹ 实特征值)
2. 不同特征值对应的特征向量正交
3. 归纳构造正交基 □

#### 定理 7.4 (对角化判定)
**Theorem 7.4 (Diagonalization Criterion)**

A可对角化 ⟺ A有n个线性无关的特征向量
⟺ 特征多项式的每个根的几何重数等于代数重数

---

### 3.4 Jordan标准型 [15Axx]

#### 定义 VII.4.1 (Jordan块)
**Definition VII.4.1 (Jordan Blocks)**

**Jordan块**:
```
J_k(λ) = [λ 1     ]
         [  λ 1   ]
         [    · · ]
         [      λ ]
```
(k×k矩阵)

**Jordan标准型**: 块对角矩阵J = diag(J_{k₁}(λ₁), ..., J_{kₘ}(λₘ))

#### 定理 7.5 (Jordan标准型定理)
**Theorem 7.5 (Jordan Canonical Form)**

对代数闭域上的任意矩阵A，存在P使得P⁻¹AP = J (Jordan标准型)。

Jordan型在排列Jordan块的顺序意义下唯一。

*证明*. 见Horn & Johnson, *Matrix Analysis*. □

---

### 3.5 奇异值分解 [15Axx]

#### 定理 7.6 (SVD)
**Theorem 7.6 (Singular Value Decomposition)**

对任意m×n矩阵A，存在分解:
```
A = U Σ V^*
```
其中:
- U: m×m酉矩阵 (UU^* = I)
- Σ: m×n对角矩阵，对角元σ₁ ≥ ... ≥ σ_r > 0
- V: n×n酉矩阵

**奇异值**: σᵢ = √(λᵢ) 其中λᵢ是A^*A的特征值

**应用**:
1. 低秩逼近 (Eckart-Young定理)
2. 伪逆: A^+ = V Σ^+ U^*
3. 主成分分析 (PCA)

*证明*. A^*A是正定的，有正交特征向量。 □

---

## 4. 结合环与代数 (16-XX)

### 4.1 环的基本性质 [16Dxx]

#### 定义 VIII.1.1 (理想)
**Definition VIII.1.1 (Ideals)**

**左理想** I ⊆ R: (I,+)是子群且RI ⊆ I

**右理想**: IR ⊆ I

**双边理想**: 左且右

**主理想**: 由一个元素生成的理想 (a) = RaR (+ Ra + aR + ℤa)

**例子**:
- (0) ⊆ (2) ⊆ (1) = ℤ (在ℤ中)
- (x) ⊆ (x,y) ⊆ (1) (在k[x,y]中)

---

### 4.2 模论 [16Dxx]

#### 定义 VIII.2.1 (模)
**Definition VIII.2.1 (Modules)**

**左R-模** M是Abel群带标量乘法R×M→M，满足:
1. r(m+n) = rm+rn
2. (r+s)m = rm+sm
3. (rs)m = r(sm)
4. 1m = m

**子模**: N ⊆ M是子群且RN ⊆ N

**例子**:
- 向量空间 = 域上的模
- Abelian群 = ℤ-模
- 理想 = 环的子模

#### 定理 8.1 (结构定理)
**Theorem 8.1 (Structure Theorem for Modules over PID)**

PID上有限生成模M:
```
M ≅ R^r ⊕ R/(d₁) ⊕ ... ⊕ R/(dₘ)
```
其中d₁|d₂|...|dₘ (不变因子)

**应用**:
- ℤ-模: 有限生成Abel群
- F[x]-模: 有理标准型

---

### 4.3 半单环 [16Dxx]

#### 定义 VIII.3.1 (半单环)
**Definition VIII.3.1 (Semisimple Rings)**

**单环**: 没有非平凡双边理想

**半单环**: 作为左模是单模的直和

**Wedderburn定理**: 半单环R ≅ ∏ M_{nᵢ}(Dᵢ) (Dᵢ是除环)

**Maschke定理**: 特征不整除|G|时，群代数k[G]是半单的。

---

### 4.4 Jacobson根 [16Nxx]

#### 定义 VIII.4.1 (Jacobson根)
**Definition VIII.4.1 (Jacobson Radical)**

**Jacobson根**:
```
J(R) = {x ∈ R : 1 - rx在R中可逆, ∀r ∈ R}
     = 所有极大左理想的交
     = 所有极大右理想的交
```

**性质**:
- R/J(R)是半单的
- x ∈ J(R) ⟺ 1 - rxs对所有r,s ∈ R可逆

**Nakayama引理**: 若M是有限生成R-模且J(R)M = M，则M = 0。

---

## 5. 非结合环与代数 (17-XX)

### 5.1 李代数 [17Bxx]

#### 定义 IX.1.1 (李代数)
**Definition IX.1.1 (Lie Algebras)**

**李代数** 𝔤 over域F是向量空间带双线性运算[·,·]满足:
1. 反对称性: [x,y] = -[y,x]
2. Jacobi恒等式: [x,[y,z]] + [y,[z,x]] + [z,[x,y]] = 0

**例子**:
- 𝔤𝔩(V): End(V)配备[x,y] = xy - yx
- 𝔰𝔩(V): 迹0的线性变换
- 𝔰𝔬(n): 反对称矩阵
- 向量场: [X,Y] = XY - YX

#### 定义 IX.1.2 (表示)
**Definition IX.1.2 (Representations)**

**表示**: 李代数同态 ρ: 𝔤 → 𝔤𝔩(V)

**伴随表示**: ad: 𝔤 → 𝔤𝔩(𝔤), ad(x)(y) = [x,y]

#### 定理 9.1 (李定理)
**Theorem 9.1 (Lie's Theorem)**

复可解李代数的每个不可约表示是一维的。

**Engel定理**: 李代数幂零 ⟺ 对所有x，ad(x)幂零。

---

### 5.2 半单李代数 [17Bxx]

#### 定义 IX.2.1 (Killing型)
**Definition IX.2.1 (Killing Form)**

**Killing型**: κ(x,y) = tr(ad(x)ad(y))

**Cartan判据**: 𝔤半单 ⟺ κ非退化

**Cartan分解**: 𝔤 = 𝔥 ⊕ ⨁_{α∈Φ} 𝔤_α
- 𝔥: Cartan子代数
- Φ: 根系
- 𝔤_α: 根空间

#### 定理 9.2 (半单李代数的分类)
**Theorem 9.2 (Classification of Semisimple Lie Algebras)**

复半单李代数由Dynkin图分类:

| 类型 | 李代数 | 维数 | 秩 |
|------|--------|------|-----|
| Aₙ | 𝔰𝔩(n+1) | n(n+2) | n |
| Bₙ | 𝔰𝔬(2n+1) | n(2n+1) | n |
| Cₙ | 𝔰𝔭(2n) | n(2n+1) | n |
| Dₙ | 𝔰𝔬(2n) | n(2n-1) | n |
| E₆ | - | 78 | 6 |
| E₇ | - | 133 | 7 |
| E₈ | - | 248 | 8 |
| F₄ | - | 52 | 4 |
| G₂ | - | 14 | 2 |

---

### 5.3 泛包络代数 [17Bxx]

#### 定义 IX.3.1 (泛包络代数)
**Definition IX.3.1 (Universal Enveloping Algebra)**

**泛包络代数** U(𝔤) 是满足泛性质的结合代数:
```
对任意李代数同态φ: 𝔤 → A (A是结合代数，配备[·,·] = · - ·)
存在唯一代数同态ψ: U(𝔤) → A使得i∘ψ = φ
```

**构造**: U(𝔤) = T(𝔤)/⟨x⊗y - y⊗x - [x,y] : x,y ∈ 𝔤⟩

**PBW定理**: 若{eᵢ}是𝔤的基，则{e_{i₁}^{k₁}...e_{iₙ}^{kₙ}}是U(𝔤)的基。

---

## 6. 范畴论 (18-XX)

### 6.1 范畴与函子 [18Axx]

#### 定义 X.1.1 (范畴)
**Definition X.1.1 (Categories)**

**范畴** C 由以下组成:
1. 对象类Ob(C)
2. 对每对对象X,Y，态射集Hom(X,Y)
3. 复合Hom(Y,Z) × Hom(X,Y) → Hom(X,Z)
4. 恒等态射id_X ∈ Hom(X,X)

满足:
- 结合律: (h∘g)∘f = h∘(g∘f)
- 单位律: f∘id = id∘f = f

**例子**:
- Set: 集合与函数
- Grp: 群与群同态
- Top: 拓扑空间与连续映射
- R-Mod: R-模与线性映射

#### 定义 X.1.2 (函子)
**Definition X.1.2 (Functors)**

**共变函子** F: C → D:
- 对象映射: X ↦ F(X)
- 态射映射: f ↦ F(f)
- 保持恒等: F(id_X) = id_{F(X)}
- 保持复合: F(g∘f) = F(g)∘F(f)

**反变函子**: 反转态射方向

**自然变换**: η: F → G是一族态射η_X: F(X) → G(X)使得对所有f: X → Y有G(f)η_X = η_Y F(f)。

---

### 6.2 极限与余极限 [18Axx]

#### 定义 X.2.1 (极限)
**Definition X.2.1 (Limits)**

**极限** (lim F) 是图表F: I → C的泛锥:
- 对象lim F
- 态射πᵢ: lim F → F(i)对所有i
- 泛性质: 对任意锥(X, fᵢ: X → F(i))，存在唯一u: X → lim F使πᵢu = fᵢ

**特殊极限**:
- 积 (product): 离散图表的极限
- 拉回 (pullback): cospan的极限
- 终对象 (terminal): 空图表的极限

#### 定义 X.2.2 (余极限)
**Definition X.2.2 (Colimits)**

**余极限** (colim F) 是极限的对偶概念。

**特殊余极限**:
- 余积 (coproduct): 积的对偶
- 推出 (pushout): 拉回的对偶
- 初始对象: 终对象的对偶

---

### 6.3 伴随函子 [18Axx]

#### 定义 X.3.1 (伴随)
**Definition X.3.1 (Adjunctions)**

**伴随** F ⊣ G (F是G的左伴随) 如果存在自然双射:
```
Hom_D(FX, Y) ≅ Hom_C(X, GY)
```

**等价描述**:
1. 单位η: id → GF和余单位ε: FG → id满足三角等式
2. F保持余极限，G保持极限

**例子**:
- 自由函子 ⊣ 遗忘函子
- F: Set → Grp, U: Grp → Set, F ⊣ U
- 张量积 ⊣ Hom (在模范畴中)

---

### 6.4 Abel范畴 [18Exx]

#### 定义 X.4.1 (Abel范畴)
**Definition X.4.1 (Abelian Categories)**

**Abel范畴** A 是满足:
1. 加性范畴: Hom集是Abel群，复合双线性
2. 有零对象、积、余积
3. 每个态射有核与余核
4. 每个单态射是核，每个满态射是余核

**例子**:
- R-Mod
- Sheaves of abelian groups
- Chain complexes

**重要性质**:
- 可做同调代数
- 有正合序列
- 蛇引理成立

---

## 7. K-理论 (19-XX)

### 7.1 代数K-理论 [19Axx]

#### 定义 XI.1.1 (K₀群)
**Definition XI.1.1 (K₀ Group)**

环R的**K₀群**: 由有限生成投射R-模生成的自由Abel群模去关系[P⊕Q] = [P] + [Q]。

**等价定义**: 
```
K₀(R) = Gr(P(R)) 
```
其中P(R)是投射模范畴，Gr是Grothendieck群。

**例子**:
- K₀(域) = ℤ
- K₀(ℤ) = ℤ
- K₀(Mₙ(R)) = K₀(R)

#### 定义 XI.1.2 (K₁群)
**Definition XI.1.2 (K₁ Group)**

```
K₁(R) = GL(R)/[GL(R), GL(R)] = GL(R)^{ab}
```

其中GL(R) = ⋃_n GL_n(R) (直和)。

**等价**: K₁(R) = H₁(GL(R), ℤ)

---

### 7.2 高阶K-理论 [19Dxx]

#### 定义 XI.2.1 (高阶K-群)
**Definition XI.2.1 (Higher K-Groups)**

**Quillen定义**: K_n(R) = π_n(BGL(R)^+) (n ≥ 1)

其中BGL(R)^+是BGL(R)的加化(plus construction)。

**性质**:
- K₀, K₁, K₂与代数定义一致
- 长正合序列
- Bott周期性(在某些环上)

**计算例子**:
- K_n(ℤ) (Quillen):
  - n ≡ 0 (mod 4): ℤ ⊕ 有限
  - n ≡ 1,2 (mod 4): ℤ/2
  - n ≡ 3 (mod 4): 有限

---

## 8. 群论 (20-XX)

### 8.1 群的基础 [20Axx]

#### 定义 XII.1.1 (群)
**Definition XII.1.1 (Groups)**

**群** G 是集合带运算·满足:
1. 结合律: (ab)c = a(bc)
2. 单位元: 存在e使ea = ae = a
3. 逆元: 对a存在a⁻¹使aa⁻¹ = a⁻¹a = e

**Abel群**: ab = ba对所有a,b

**例子**:
- Sₙ: n元对称群 (|Sₙ| = n!)
- ℤ/nℤ: 循环群
- GL(n,F): 一般线性群
- D_n: 二面体群

#### 定理 12.1 (Lagrange定理)
**Theorem 12.1 (Lagrange's Theorem)**

对有限群G的子群H: |G| = |H| [G:H]

*推论*: 元素的阶整除群的阶。

*证明*. 左陪集分解。 □

---

### 8.2 Sylow定理 [20Dxx]

#### 定理 12.2 (Sylow定理)
**Theorem 12.2 (Sylow Theorems)**

设|G| = pⁿm，其中p ∤ m。

1. **存在性**: 存在阶为pⁿ的子群(Sylow p-子群)
2. **共轭性**: 所有Sylow p-子群共轭
3. **计数**: Sylow p-子群个数n_p满足:
   - n_p ≡ 1 (mod p)
   - n_p | m

**应用**:
- 证明某些群非单
- 群的结构分析

*证明*. 见Dummit & Foote, *Abstract Algebra*. □

---

### 8.3 群表示 [20Cxx]

#### 定义 XII.3.1 (群表示)
**Definition XII.3.1 (Group Representations)**

**表示**: 群同态 ρ: G → GL(V)

**特征标**: χ(g) = tr(ρ(g))

**不可约表示**: 没有非平凡不变子空间

**Maschke定理**: 若char(F) ∤ |G|，则F[G]是半单的。

#### 定理 12.3 (特征标正交性)
**Theorem 12.3 (Character Orthogonality)**

对有限群G的不可约特征标χᵢ, χⱼ:
```
(1/|G|) Σ_{g∈G} χᵢ(g) χⱼ(ḡ) = δᵢⱼ
```

**推论**: 不可约表示数 = 共轭类数

---

### 8.4 有限单群 [20Dxx]

#### 定理 12.4 (分类定理)
**Theorem 12.4 (Classification of Finite Simple Groups)**

有限单群是以下之一:
1. 素数阶循环群 ℤ/pℤ
2. 交错群 Aₙ (n ≥ 5)
3. Lie型群 (Chevalley群、扭曲群)
4. 26个散在群 (包括Monster)

**历史**: 1955-2004，超过100位数学家参与，证明超过10000页。

**最大散在群**: Monster (|M| ≈ 8×10⁵³)

---

## Lean4 代码示例

本节提供与第一卷第二部分（代数学）内容相关的Lean4代码示例。

### 1. 域论与Galois理论

```lean4
import Mathlib.Algebra.Field.Basic
import Mathlib.RingTheory.FieldTheory.Basic

-- 域的基本性质
example (F : Type*) [Field F] (a : F) (ha : a ≠ 0) : a * a⁻¹ = 1 := by
  exact mul_inv_cancel ha

-- 域的特征
example (F : Type*) [Field F] (p : ℕ) [CharP F p] (hp : p ≠ 0) : 
    Nat.Prime p := CharP.char_prime F p

-- 域扩张的基础
import Mathlib.RingTheory.Algebraic.Basic

-- 代数扩张的定义
example (K L : Type*) [Field K] [Field L] [Algebra K L] (α : L) :
    IsAlgebraic K α ↔ ∃ p : K[X], p.Monic ∧ p ≠ 0 ∧ p.eval₂ (algebraMap K L) α = 0 := by
  exact isAlgebraic_def

-- 极小多项式
example (K L : Type*) [Field K] [Field L] [Algebra K L] (α : L) 
    [hα : IsAlgebraic K α] :
    Irreducible (minpoly K α) ∧ (minpoly K α).Monic := by
  exact ⟨minpoly.irreducible hα, minpoly.monic hα⟩
```

### 2. 线性代数

```lean4
import Mathlib.LinearAlgebra.Matrix.Basic
import Mathlib.LinearAlgebra.Matrix.Determinant
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

-- 矩阵的基本操作
example (n : Type*) [Fintype n] [DecidableEq n] (R : Type*) [CommRing R] 
    (A B : Matrix n n R) : (A + B).det = A.det + B.det := by
  -- 这是不成立的，但我们可以展示矩阵乘法
  sorry

-- 矩阵乘法的结合律
example (n : Type*) [Fintype n] [DecidableEq n] (R : Type*) [CommRing R]
    (A B C : Matrix n n R) : A * B * C = A * (B * C) := by
  exact mul_assoc A B C

-- 单位矩阵
example (n : Type*) [Fintype n] [DecidableEq n] (R : Type*) [CommRing R]
    (A : Matrix n n R) : A * 1 = A ∧ 1 * A = A := by
  constructor <;> simp

-- 可逆矩阵
example (n : Type*) [Fintype n] [DecidableEq n] (R : Type*) [CommRing R]
    (A : Matrix n n R) (h : IsUnit A.det) : A * A⁻¹ = 1 := by
  have := A.mul_nonsingular_inv (isUnit_det_iff.mp h)
  convert this using 2 <;> ext <;> simp

-- 行列式的性质
example (n : Type*) [Fintype n] [DecidableEq n] (R : Type*) [CommRing R]
    (A B : Matrix n n R) : (A * B).det = A.det * B.det := by
  exact Matrix.det_mul A B

-- 转置的性质
example (n : Type*) [Fintype n] [DecidableEq n] (R : Type*) [CommRing R]
    (A B : Matrix n n R) : (A * B)ᵀ = Bᵀ * Aᵀ := by
  exact Matrix.transpose_mul A B
```

### 3. 线性映射与向量空间

```lean4
import Mathlib.LinearAlgebra.LinearIndependent
import Mathlib.LinearAlgebra.Basis

-- 向量空间的定义（已隐含在Module中）
example (K V : Type*) [Field K] [AddCommGroup V] [Module K V] :
    (0 : V) + 0 = (0 : V) := by simp

-- 线性映射的定义
example (K V W : Type*) [Field K] [AddCommGroup V] [AddCommGroup W] 
    [Module K V] [Module K W] (f : V →ₗ[K] W) :
    f (0 : V) = 0 ∧ (∀ a b, f (a + b) = f a + f b) := by
  constructor
  · exact map_zero f
  · exact map_add f

-- 线性无关的定义
example (K ι V : Type*) [Field K] [AddCommGroup V] [Module K V]
    (v : ι → V) : LinearIndependent K v ↔ 
    ∀ (s : Finset ι) (g : ι → K), (∑ i ∈ s, g i • v i) = 0 → ∀ i ∈ s, g i = 0 := by
  exact linearIndependent_iff_finset.mp

-- 秩-零化度定理
import Mathlib.LinearAlgebra.Dimension.Finrank

example (K V W : Type*) [Field K] [AddCommGroup V] [AddCommGroup W]
    [Module K V] [Module K W] [FiniteDimensional K V] [FiniteDimensional K W]
    (f : V →ₗ[K] W) : 
    FiniteDimensional.finrank K V = 
    FiniteDimensional.finrank K f.ker + FiniteDimensional.finrank K f.range := by
  exact FiniteDimensional.finrank_add_finrank_range_eq_finrank f
```

### 4. 环与理想

```lean4
import Mathlib.RingTheory.Ideal.Basic

-- 理想的定义
example (R : Type*) [CommRing R] (I : Ideal R) : 
    (0 : R) ∈ I ∧ (∀ r ∈ I, ∀ s ∈ I, r + s ∈ I) ∧ (∀ r ∈ I, ∀ x : R, x * r ∈ I) := by
  refine ⟨?_, ?_, ?_⟩
  · exact Ideal.zero_mem I
  · exact fun _ hr _ hs => Ideal.add_mem I hr hs
  · exact fun _ hr _ => Ideal.mul_mem_left I _ hr

-- 理想的和
example (R : Type*) [CommRing R] (I J : Ideal R) : 
    (I + J) = Ideal.span (I ∪ J : Set R) := by
  exact Ideal.add_eq_span I J

-- 理想的积
example (R : Type*) [CommRing R] (I J : Ideal R) : 
    (I * J) = Ideal.span {(r * s) | r ∈ I, s ∈ J} := by
  exact Ideal.mul_eq_span I J

-- 素理想
example (R : Type*) [CommRing R] (I : Ideal R) : 
    I.IsPrime ↔ (1 : R) ∉ I ∧ ∀ r s, r * s ∈ I → r ∈ I ∨ s ∈ I := by
  exact Ideal.isPrime_iff

-- 极大理想
example (R : Type*) [CommRing R] (I : Ideal R) : 
    I.IsMaximal ↔ (1 : R) ∉ I ∧ ∀ J, I ≤ J → J = ⊤ ∨ J = I := by
  exact Ideal.isMaximal_iff
```

### 5. 范畴论基础

```lean4
import Mathlib.CategoryTheory.Category.Basic
import Mathlib.CategoryTheory.Functor.Basic
import Mathlib.CategoryTheory.NaturalIsomorphism

open CategoryTheory

-- 范畴的基本性质
example (C : Type*) [Category C] (X Y Z : C) (f : X ⟶ Y) (g : Y ⟶ Z) :
    f ≫ g = CategoryStruct.comp f g := rfl

-- 恒等态射
example (C : Type*) [Category C] (X : C) : 𝟙 X ≫ 𝟙 X = 𝟙 X := by
  simp

-- 结合律
example (C : Type*) [Category C] (W X Y Z : C) 
    (f : W ⟶ X) (g : X ⟶ Y) (h : Y ⟶ Z) :
    (f ≫ g) ≫ h = f ≫ (g ≫ h) := by
  exact Category.assoc f g h

-- 函子保持恒等
example (C D : Type*) [Category C] [Category D] (F : C ⥤ D) (X : C) :
    F.map (𝟙 X) = 𝟙 (F.obj X) := by
  exact F.map_id X

-- 函子保持复合
example (C D : Type*) [Category C] [Category D] (F : C ⥤ D) 
    {X Y Z : C} (f : X ⟶ Y) (g : Y ⟶ Z) :
    F.map (f ≫ g) = F.map f ≫ F.map g := by
  exact F.map_comp f g

-- 自然变换
example (C D : Type*) [Category C] [Category D] (F G : C ⥤ D) 
    (η : F ⟶ G) (X : C) : 
    F.map (𝟙 X) ≫ η.app X = η.app X ≫ G.map (𝟙 X) := by
  simp [η.naturality]
```

### 6. 群论深入

```lean4
import Mathlib.Algebra.Group.Subgroup.Basic
import Mathlib.GroupTheory.Subgroup.Center
import Mathlib.GroupTheory.Subgroup.Normal

-- 子群的交集
example (G : Type*) [Group G] (H K : Subgroup G) : 
    Subgroup.inf H K = Subgroup.mk (H ∩ K) := rfl

-- 子群的并（由并生成的子群）
example (G : Type*) [Group G] (H K : Subgroup G) : 
    (H ⊔ K : Set G) = Subgroup.closure (H ∪ K : Set G) := by
  exact Subgroup.sup_toSubmonoid_eq_closure H K

-- 正规子群
example (G : Type*) [Group G] (N : Subgroup G) : 
    N.Normal ↔ ∀ g : G, g * N = N * g := by
  constructor
  · intro h g
    exact Set.ext (fun x => ⟨fun hx => ⟨g⁻¹ * x * g, 
        h.out (by simp [Subgroup.mem_normal] at h ⊢; exact h.2 g x hx), 
        by group⟩,
      fun hx => ⟨g * x * g⁻¹, 
        h.out (by simp [Subgroup.mem_normal] at h ⊢; exact h.2 g⁻¹ x (by 
          obtain ⟨y, hy, eq⟩ := hx
          simp only [Set.mem_setOf_eq] at hy ⊢
          rw [← eq]; exact hy), by group⟩, by simp⟩⟩)
  · intro h g x hx
    have := h g
    sorry  -- 需要更多技术细节

-- 商群
import Mathlib.GroupTheory.QuotientGroup.Basic

example (G : Type*) [Group G] (N : Subgroup G) [N.Normal] :
    QuotientGroup.mk (1 : G) = (1 : G ⧸ N) := by
  simp

-- 第一同构定理
example (G H : Type*) [Group G] [Group H] (f : G →* H) :
    Nonempty (G ⧸ f.ker ≃* f.range) := by
  exact ⟨MonoidHom.ofKerEquivRange f⟩
```

### 7. 有限群

```lean4
import Mathlib.GroupTheory.OrderOfElement
import Mathlib.GroupTheory.Finiteness

-- 元素的阶
example (G : Type*) [Group G] [Fintype G] (g : G) : 
    g ^ orderOf g = 1 := by
  exact pow_orderOf_eq_one g

-- Lagrange定理
example (G : Type*) [Group G] [Fintype G] (H : Subgroup G) [Fintype H] :
    Nat.card H ∣ Nat.card G := by
  exact Nat.card_subgroup_dvd_card H

-- 元素的阶整除群的阶
example (G : Type*) [Group G] [Fintype G] (g : G) :
    orderOf g ∣ Nat.card G := by
  exact orderOf_dvd_card_univ

-- 循环群
import Mathlib.GroupTheory.CyclicBasic

example (G : Type*) [Group G] [Fintype G] (hG : IsCyclic G) :
    ∃ g : G, ∀ x : G, ∃ n : ℤ, x = g ^ n := by
  exact hG
```

---

## 参考文献

### 域论与Galois理论
1. Lang, S., *Algebra*, 3rd ed., Springer, 2002
2. Cox, D.A., *Galois Theory*, 2nd ed., Wiley, 2012

### 交换代数
3. Atiyah, M.F., MacDonald, I.G., *Introduction to Commutative Algebra*, Addison-Wesley, 1969
4. Eisenbud, D., *Commutative Algebra with a View Toward Algebraic Geometry*, Springer, 1995

### 线性代数
5. Horn, R.A., Johnson, C.R., *Matrix Analysis*, 2nd ed., Cambridge, 2013
6. Hoffman, K., Kunze, R., *Linear Algebra*, 2nd ed., Prentice Hall, 1971

### 环与模
7. Lam, T.Y., *A First Course in Noncommutative Rings*, 2nd ed., Springer, 2001
8. Anderson, F.W., Fuller, K.R., *Rings and Categories of Modules*, 2nd ed., Springer, 1992

### 李代数
9. Humphreys, J.E., *Introduction to Lie Algebras and Representation Theory*, Springer, 1972
10. Knapp, A.W., *Lie Groups Beyond an Introduction*, 2nd ed., Birkhäuser, 2002

### 范畴论
11. Mac Lane, S., *Categories for the Working Mathematician*, 2nd ed., Springer, 1998
12. Awodey, S., *Category Theory*, 2nd ed., Oxford, 2010

### K-理论
13. Rosenberg, J., *Algebraic K-Theory and Its Applications*, Springer, 1994
14. Srinivas, V., *Algebraic K-Theory*, 2nd ed., Birkhäuser, 1996

### 群论
15. Dummit, D.S., Foote, R.M., *Abstract Algebra*, 3rd ed., Wiley, 2004
16. Rotman, J.J., *An Introduction to the Theory of Groups*, 4th ed., Springer, 1995

---

**注**: 本文档是第一卷第二部分，完成了基础代数的全部内容。

---

*本卷完成日期: 2025-03-26*  
*下一卷预告: 分析与微分方程*
