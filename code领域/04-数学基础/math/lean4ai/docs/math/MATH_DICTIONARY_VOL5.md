# 数学知识词典 - 第五卷：概率论与统计学
## Volume V: Probability Theory and Statistics

**MSC分类**: 60-XX, 62-XX  
**版本**: 1.0  
**日期**: 2025-03-26

---

## 目录

1. [概率论基础 (60-XX)](#1-概率论基础)
2. [随机变量与分布 (60-XX)](#2-随机变量与分布)
3. [极限定理 (60-XX)](#3-极限定理)
4. [随机过程 (60-XX)](#4-随机过程)
5. [统计学基础 (62-XX)](#5-统计学基础)

---

## 1. 概率论基础 (60-XX)

### 1.1 概率空间 [60Axx]

#### 定义 XXXI.1.1 (概率空间)
**Definition XXXI.1.1 (Probability Spaces)**

**概率空间** (Ω, ℱ, ℙ):
- **样本空间** Ω: 所有可能结果
- **σ-代数** ℱ: 事件集
- **概率测度** ℙ: ℱ → [0,1] 满足:
  1. ℙ(Ω) = 1
  2. 可数可加性: Aᵢ不交 ⟹ ℙ(⋃Aᵢ) = Σℙ(Aᵢ)

**例子**:
- 古典概率: Ω = {ω₁,...,ω_n}, ℙ(ω_i) = 1/n
- 几何概率: Ω ⊆ ℝ^n, ℙ(A) = vol(A)/vol(Ω)
- 频率概率: ℙ(A) = lim_{n→∞} N_n(A)/n

#### 定义 XXXI.1.2 (条件概率)
**Definition XXXI.1.2 (Conditional Probability)**

**条件概率**: ℙ(A|B) = ℙ(A∩B)/ℙ(B) (ℙ(B) > 0)

**Bayes公式**:
```
ℙ(A|B) = ℙ(B|A)ℙ(A) / ℙ(B)
       = ℙ(B|A)ℙ(A) / Σ_i ℙ(B|Aᵢ)ℙ(Aᵢ)
```

**独立性**: A,B独立 ⟺ ℙ(A∩B) = ℙ(A)ℙ(B)

---

### 1.2 随机变量 [60Axx]

#### 定义 XXXI.2.1 (随机变量)
**Definition XXXI.2.1 (Random Variables)**

**随机变量** X: Ω → ℝ 是ℱ-可测函数

**累积分布函数 (CDF)**: F_X(x) = ℙ(X ≤ x)

**性质**:
1. 单调不减
2. 右连续
3. lim_{x→-∞} F(x) = 0, lim_{x→∞} F(x) = 1

**概率质量函数 (PMF)** (离散): p_X(x) = ℙ(X = x)

**概率密度函数 (PDF)** (连续): f_X(x) = F'_X(x), ℙ(a≤X≤b) = ∫_a^b f_X(x)dx

---

## 2. 随机变量与分布 (60-XX)

### 2.1 常见分布 [60Exx]

#### 定义 XXXII.1.1 (离散分布)
**Definition XXXII.1.1 (Discrete Distributions)**

**Bernoulli(p)**: X ~ Ber(p)
- ℙ(X=1) = p, ℙ(X=0) = 1-p
- EX = p, Var(X) = p(1-p)

**Binomial(n,p)**: X ~ Bin(n,p)
- X = X₁+...+X_n, Xᵢ~Ber(p)独立
- ℙ(X=k) = C(n,k)p^k(1-p)^{n-k}
- EX = np, Var(X) = np(1-p)

**Poisson(λ)**: X ~ Poi(λ)
- ℙ(X=k) = e^{-λ}λ^k/k!
- EX = Var(X) = λ

**Geometric(p)**: X ~ Geom(p)
- ℙ(X=k) = (1-p)^{k-1}p (k≥1)
- EX = 1/p, Var(X) = (1-p)/p²

#### 定义 XXXII.1.2 (连续分布)
**Definition XXXII.1.2 (Continuous Distributions)**

**Uniform(a,b)**: X ~ U(a,b)
- f_X(x) = 1/(b-a) (a<x<b)
- EX = (a+b)/2, Var(X) = (b-a)²/12

**Exponential(λ)**: X ~ Exp(λ)
- f_X(x) = λe^{-λx} (x≥0)
- EX = 1/λ, Var(X) = 1/λ²
- 无记忆性: ℙ(X>s+t|X>t) = ℙ(X>s)

**Normal(μ,σ²)**: X ~ N(μ,σ²)
- f_X(x) = (1/√(2πσ²)) e^{-(x-μ)²/(2σ²)}
- EX = μ, Var(X) = σ²
- Z = (X-μ)/σ ~ N(0,1) (标准化)

**Gamma(α,β)**: X ~ Gamma(α,β)
- f_X(x) = β^α x^{α-1} e^{-βx} / Γ(α) (x≥0)
- EX = α/β, Var(X) = α/β²

**Beta(α,β)**: X ~ Beta(α,β)
- f_X(x) = x^{α-1}(1-x)^{β-1} / B(α,β) (0≤x≤1)
- EX = α/(α+β), Var(X) = αβ/[(α+β)²(α+β+1)]

---

### 2.2 多元分布 [60Exx]

#### 定义 XXXII.2.1 (联合分布)
**Definition XXXII.2.1 (Joint Distributions)**

**联合CDF**: F_{X,Y}(x,y) = ℙ(X≤x, Y≤y)

**联合PDF** (连续): f_{X,Y}(x,y), ℙ((X,Y)∈A) = ∫∫_A f_{X,Y}(x,y)dxdy

**边缘分布**: f_X(x) = ∫ f_{X,Y}(x,y)dy

**条件分布**: f_{Y|X}(y|x) = f_{X,Y}(x,y)/f_X(x)

**独立性**: X,Y独立 ⟺ f_{X,Y}(x,y) = f_X(x)f_Y(y)

**协方差**: Cov(X,Y) = E[(X-EX)(Y-EY)]

**相关系数**: ρ(X,Y) = Cov(X,Y)/[√Var(X)√Var(Y)]

---

### 2.3 期望与矩 [60Exx]

#### 定义 XXXII.3.1 (期望)
**Definition XXXII.3.1 (Expectation)**

**期望**: EX = ∫ xdF_X(x)
- 离散: EX = Σ x·p_X(x)
- 连续: EX = ∫ x·f_X(x)dx

**性质**:
1. 线性: E(aX+bY) = aEX + bEY
2. E(c) = c
3. X≥0 ⟹ EX ≥ 0

**k阶矩**: E[X^k]

**k阶中心矩**: E[(X-EX)^k]

**方差**: Var(X) = E[(X-EX)²] = EX² - (EX)²

**标准差**: σ_X = √Var(X)

#### 定理 31.1 (Cauchy-Schwarz)
**Theorem 31.1 (Cauchy-Schwarz Inequality)**

|Cov(X,Y)| ≤ √Var(X)·√Var(Y)

*推论*: |ρ(X,Y)| ≤ 1

*证明*. 对E[(X+tY)²] ≥ 0应用二次不等式。 □

#### 定理 31.2 (Jensen不等式)
**Theorem 31.2 (Jensen's Inequality)**

若φ凸，则:
```
φ(EX) ≤ E[φ(X)]
```

*应用*: φ(x) = |x|^p (p≥1) ⟹ |EX|^p ≤ E|X|^p

---

## 3. 极限定理 (60-XX)

### 3.1 大数定律 [60Fxx]

#### 定理 32.1 (弱大数定律)
**Theorem 32.1 (Weak Law of Large Numbers)**

设X₁,X₂,...独立同分布(i.i.d.)，EXᵢ = μ，Var(Xᵢ) = σ² < ∞。则:
```
X̄_n = (X₁+...+X_n)/n →^p μ
```
(依概率收敛)

*证明*. Chebyshev不等式: ℙ(|X̄_n-μ|≥ε) ≤ Var(X̄_n)/ε² = σ²/(nε²) → 0 □

#### 定理 32.2 (强大数定律)
**Theorem 32.2 (Strong Law of Large Numbers)**

设X₁,X₂,...i.i.d.，EXᵢ = μ。则:
```
X̄_n → μ  a.s.
```
(几乎必然收敛)

*意义*: 频率稳定到概率

*证明*. Kolmogorov的三级数定理或Etemadi证明。 □

---

### 3.2 中心极限定理 [60Fxx]

#### 定理 32.3 (Lindeberg-Lévy CLT)
**Theorem 32.3 (Lindeberg-Lévy Central Limit Theorem)**

设X₁,X₂,...i.i.d.，EXᵢ = μ，Var(Xᵢ) = σ² ∈ (0,∞)。则:
```
√n(X̄_n - μ)/σ →^d N(0,1)
```
(依分布收敛)

*等价*: (X₁+...+X_n-nμ)/(σ√n) →^d N(0,1)

*意义*: 大样本的样本均值近似正态

*证明*. 特征函数 + Lévy连续定理。 □

#### 定理 32.4 (Berry-Esséen定理)
**Theorem 32.4 (Berry-Esséen Theorem)**

CLT的收敛速度:
```
|F_n(x) - Φ(x)| ≤ C·E|X-μ|³/(σ³√n)
```

其中F_n是标准化和的CDF，Φ是N(0,1)的CDF。

---

### 3.3 其他极限定理 [60Fxx]

#### 定理 32.5 (Borel-Cantelli引理)
**Theorem 32.5 (Borel-Cantelli Lemmas)**

**第一引理**: 若Σℙ(A_n) < ∞，则ℙ(A_n i.o.) = 0

**第二引理**: 若{A_n}独立且Σℙ(A_n) = ∞，则ℙ(A_n i.o.) = 1

其中A_n i.o. = {ω : ω属于无穷多个A_n}

#### 定理 32.6 (重对数律)
**Theorem 32.6 (Law of the Iterated Logarithm)**

对i.i.d.序列X₁,X₂,...，EXᵢ = 0，Var(Xᵢ) = σ² < ∞:
```
limsup_{n→∞} (X₁+...+X_n)/(σ√(2n log log n)) = 1  a.s.
```

---

## 4. 随机过程 (60-XX)

### 4.1 Markov链 [60Jxx]

#### 定义 XXXIII.1.1 (Markov链)
**Definition XXXIII.1.1 (Markov Chains)**

**Markov链** {X_n} 满足:
```
ℙ(X_{n+1}=j | X_n=i, X_{n-1}=i_{n-1}, ..., X_0=i_0) = ℙ(X_{n+1}=j | X_n=i) = p_{ij}
```
(Markov性/无记忆性)

**转移矩阵**: P = (p_{ij}), p_{ij} ≥ 0, Σ_j p_{ij} = 1

**n步转移**: P^{(n)} = P^n, p_{ij}^{(n)} = ℙ(X_n=j|X_0=i)

**Chapman-Kolmogorov方程**: P^{(m+n)} = P^{(m)}P^{(n)}

#### 定理 33.1 (平稳分布)
**Theorem 33.1 (Stationary Distributions)**

**平稳分布** π: πP = π

**存在性**: 有限状态Markov链总有平稳分布

**唯一性**: 不可约 ⟹ 平稳分布唯一

**收敛性**: 若不可约、非周期、正常返，则:
```
P^n → 1·π  (矩阵极限)
```

---

### 4.2 Brown运动 [60Jxx]

#### 定义 XXXIII.2.1 (Brown运动)
**Definition XXXIII.2.1 (Brownian Motion)**

**Brown运动** (Wiener过程) {B_t}_{t≥0}:
1. B₀ = 0
2. 增量独立: B_t - B_s ⟂⟂ B_v - B_u (0≤u<v≤s<t)
3. B_t - B_s ~ N(0, t-s)
4. 轨道连续 (a.s.)

**性质**:
- B_t ~ N(0, t)
- Cov(B_s, B_t) = min(s,t)
- 自相似: {c^{-1/2}B_{ct}} 也是Brown运动
- 处处不可微 (a.s.)

#### 定理 33.2 (反射原理)
**Theorem 33.2 (Reflection Principle)**

```
ℙ(max_{0≤s≤t} B_s ≥ a) = 2ℙ(B_t ≥ a) = 2[1-Φ(a/√t)]
```

*推论*: Brown运动首达a的时刻T_a有分布:
```
ℙ(T_a ≤ t) = ℙ(max_{0≤s≤t} B_s ≥ a)
```

---

### 4.3 Poisson过程 [60Jxx]

#### 定义 XXXIII.3.1 (Poisson过程)
**Definition XXXIII.3.1 (Poisson Processes)**

**Poisson过程** {N_t}_{t≥0}, 速率λ:
1. N₀ = 0
2. 独立增量
3. N_t - N_s ~ Poi(λ(t-s))

**到达时间**: T₁, T₂, ... (第n个事件发生时间)
- T_n - T_{n-1} ~ Exp(λ) i.i.d.
- T_n ~ Gamma(n, λ)

**等待时间**: W₁, W₂, ... (第n个事件后到下一个的时间)
- W_n ~ Exp(λ) (无记忆性)

---

## 5. 统计学基础 (62-XX)

### 5.1 估计理论 [62Fxx]

#### 定义 XXXIV.1.1 (估计量)
**Definition XXXIV.1.1 (Estimators)**

**统计量**: T(X₁,...,X_n)

**估计量**: 用于估计参数θ的统计量 θ̂

**评价标准**:
1. **无偏性**: E[θ̂] = θ
2. **有效性**: Var(θ̂) 最小
3. **相合性**: θ̂ → θ (当n→∞)
4. **渐近正态性**: √n(θ̂-θ) → N(0,σ²)

#### 定理 34.1 (Cramér-Rao下界)
**Theorem 34.1 (Cramér-Rao Lower Bound)**

对无偏估计量θ̂:
```
Var(θ̂) ≥ 1/I(θ)
```
其中 **Fisher信息**:
```
I(θ) = E[(∂/∂θ) log f(X;θ)]²
     = -E[∂²/∂θ² log f(X;θ)]
```

*有效估计量*: 达到下界

---

### 5.2 最大似然估计 [62Fxx]

#### 定义 XXXIV.2.1 (MLE)
**Definition XXXIV.2.1 (Maximum Likelihood Estimation)**

**似然函数**: L(θ|x) = f(x;θ)

**对数似然**: ℓ(θ) = log L(θ)

**MLE**: θ̂_MLE = argmax_θ L(θ) = argmax_θ ℓ(θ)

**例子**:
1. **N(μ,σ²)**: X₁,...,X_n
   - μ̂ = X̄ (样本均值)
   - σ̂² = (1/n)Σ(Xᵢ-X̄)²

2. **Bernoulli(p)**: p̂ = X̄ = (成功次数)/n

#### 定理 34.2 (MLE的性质)
**Theorem 34.2 (Properties of MLE)**

**渐近性质** (n→∞):
1. **相合性**: θ̂_MLE → θ
2. **渐近正态**: √n(θ̂_MLE-θ) → N(0, I(θ)^{-1})
3. **渐近有效**: 达到Cramér-Rao下界
4. **不变性**: 若θ̂是θ的MLE，则g(θ̂)是g(θ)的MLE

---

### 5.3 假设检验 [62Fxx]

#### 定义 XXXIV.3.1 (假设检验)
**Definition XXXIV.3.1 (Hypothesis Testing)**

**假设**:
- H₀: 原假设
- H₁: 备择假设

**拒绝域**: C ⊆ 样本空间

**错误**:
- **第一类错误**: P(H₀真但拒绝H₀) = α (显著性水平)
- **第二类错误**: P(H₁真但接受H₀) = β

**功效**: 1-β = P(H₁真时拒绝H₀)

**p值**: 在H₀下，得到当前或更极端结果的概率

#### 定理 34.3 (Neyman-Pearson引理)
**Theorem 34.3 (Neyman-Pearson Lemma)**

对简单假设H₀: θ=θ₀ vs H₁: θ=θ₁，最优势检验的拒绝域:
```
C = {x : L(θ₁|x)/L(θ₀|x) > c}
```
其中c由显著性水平α决定。

*意义*: 似然比检验最优

---

### 5.4 回归分析 [62Jxx]

#### 定义 XXXIV.4.1 (线性回归)
**Definition XXXIV.4.1 (Linear Regression)**

**模型**: Y = Xβ + ε
- Y: n×1 响应变量
- X: n×p 设计矩阵
- β: p×1 参数
- ε: n×1 误差, E[ε]=0, Cov(ε)=σ²I

**最小二乘估计**: β̂ = (X'X)^{-1}X'Y

**性质**:
1. 无偏: E[β̂] = β
2. Gauss-Markov: BLUE (最佳线性无偏估计)
3. Cov(β̂) = σ²(X'X)^{-1}

#### 定理 34.4 (Gauss-Markov定理)
**Theorem 34.4 (Gauss-Markov Theorem)**

在误差球面对称假设下(0均值、常数方差、不相关)，OLS是BLUE。

---

### 5.5 Bayes统计 [62Fxx]

#### 定义 XXXIV.5.1 (Bayes推断)
**Definition XXXIV.5.1 (Bayesian Inference)**

**先验分布**: π(θ)

**似然**: L(θ|x)

**后验分布** (Bayes公式):
```
π(θ|x) ∝ L(θ|x)π(θ)
```

**Bayes估计**:
1. **后验均值**: θ̂_B = E[θ|X] (平方损失下)
2. **后验中位数** (绝对损失)
3. **后验众数** (0-1损失)

**例子**: Bernoulli(p) + Beta(α,β)先验 ⟹ Beta(α+ΣXᵢ, β+n-ΣXᵢ)后验

---

## Lean4 代码示例

本节提供与第五卷（概率与统计）内容相关的Lean4代码示例。

### 1. 概率空间与随机变量

```lean4
import Mathlib.Probability.Notation
import Mathlib.Probability.ProbabilityMassFunction.Basic

open Probability

-- 概率空间在Lean4中通过MeasureSpace和ProbabilityMeasure表示
-- 随机变量是从概率空间到其他空间的可测函数

-- 随机变量的定义
variable {Ω : Type*} [MeasurableSpace Ω] [MeasureSpace Ω] [IsProbabilityMeasure (ℙ : Measure Ω)]

-- 期望
example (X : Ω → ℝ) (hX : Measurable X) (hintegr : Integrable X ℙ) : 
    E[X] = ∫ ω, X ω ∂ℙ := rfl

-- 方差
example (X : Ω → ℝ) (hX : Measurable X) (hintegr : Integrable X ℙ) : 
    Var[X] = E[(X - E[X])^2] := by
  simp [variance]

-- 独立性
example (X Y : Ω → ℝ) (hX : Measurable X) (hY : Measurable Y) :
    Indep X Y ↔ ∀ a b, ℙ {ω | X ω ≤ a ∧ Y ω ≤ b} = ℙ {ω | X ω ≤ a} * ℙ {ω | Y ω ≤ b} := by
  sorry  -- 需要展开定义
```

### 2. 常见概率分布

```lean4
import Mathlib.Probability.Distributions.Uniform
import Mathlib.Probability.Distributions.Normal
import Mathlib.Probability.Distributions.Binomial
import Mathlib.Probability.Distributions.Poisson
import Mathlib.Probability.Distributions.Exponential

-- 均匀分布
example {a b : ℝ} (hab : a < b) : 
    ∫ x in Set.Ioo a b, (1 / (b - a)) • (1 : ℝ) = 1 := by
  sorry  -- 需要积分计算

-- 正态分布
-- 在Lean4中，Normal通过PDF定义
-- PDF(x) = (1 / (σ * sqrt(2π))) * exp(-(x - μ)^2 / (2 * σ^2))

example (μ σ : ℝ) (hσ : 0 < σ) :
    ∫ x, Real.normalPDF μ σ x = 1 := by
  exact integral_normalPDF hσ

-- 二项分布
-- Binomial(n, p)的概率质量函数
example (n : ℕ) (p : ℝ) (hp : 0 ≤ p ∧ p ≤ 1) (k : ℕ) (hk : k ≤ n) :
    ℙ (Binomial n p = k) = (n.choose k) * p^k * (1-p)^(n-k) := by
  sorry  -- 定义展开

-- Poisson分布
example (λ : ℝ) (hλ : 0 < λ) (k : ℕ) :
    ℙ (Poisson λ = k) = (λ^k * Real.exp (-λ)) / k.factorial := by
  sorry

-- 指数分布
example (λ : ℝ) (hλ : 0 < λ) (x : ℝ) (hx : 0 ≤ x) :
    Real.expPDF λ x = λ * Real.exp (-λ * x) := by
  sorry
```

### 3. 极限定理

```lean4
import Mathlib.Probability.WeakConv
import Mathlib.Probability.CentralLimitTheorem

-- 大数定律 (弱)
-- 在Lean4中，概率收敛通过Tendsto定义

example (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n))
    (hindep : iIndep X) (hintegr : ∀ n, Integrable (X n) ℙ)
    (hident : ∀ n m, E[X n] = E[X m]) :
    Tendsto (fun n => (1/n : ℝ) * ∑ i ∈ Finset.range n, X i) 
    atTop (nhds E[X 0]) := by
  sorry  -- 弱大数定律

-- 中心极限定理
example (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n))
    (hindep : iIndep X) (hintegr : ∀ n, Integrable (X n) ℙ)
    (hident : ∀ n m, E[X n] = E[X m]) (hvar : ∀ n, Var[X n] = σ^2) (hσ : σ ≠ 0) :
    Tendsto (fun n => (∑ i ∈ Finset.range n, X i - n * E[X 0]) / (σ * Real.sqrt n))
    Filter.atTop (Measure.vague (MeasureTheory.Measure.map Normal 0 1)) := by
  sorry  -- 中心极限定理
```

### 4. Markov链

```lean4
import Mathlib.Probability.MarkovChain.Basic

-- Markov性质: P(X_{n+1} | X_n, X_{n-1}, ...) = P(X_{n+1} | X_n)

-- 状态空间
variable (S : Type*) [Fintype S] [Nonempty S]

-- 转移矩阵
def TransitionMatrix (S : Type*) [Fintype S] := Matrix S S ℝ

-- 转移矩阵的性质
example (P : TransitionMatrix S) (hP : ∀ i j, 0 ≤ P i j) 
    (hsum : ∀ i, ∑ j, P i j = 1) :
    ∀ i, (∑ j, P i j) = 1 := hsum

-- Markov链的平稳分布
-- πP = π 的解
example (P : TransitionMatrix S) : 
    ∃ π : S → ℝ, (∀ i, 0 ≤ π i) ∧ (∑ i, π i = 1) ∧ ∀ i, ∑ j, π j * P j i = π i := by
  sorry  -- 不可约链的平稳分布存在性
```

### 5. 统计估计

```lean4
import Mathlib.Statistics.Sample
import Mathlib.Statistics.Estimator

-- 样本均值
def sampleMean (X : Fin n → ℝ) : ℝ := (∑ i, X i) / n

-- 样本方差
def sampleVariance (X : Fin n → ℝ) : ℝ := 
  (∑ i, (X i - sampleMean X)^2) / (n - 1)

-- 无偏性
example (X : Fin n → Ω → ℝ) (hX : ∀ i, Measurable (X i))
    (hindep : iIndep X) (hintegr : ∀ i, Integrable (X i) ℙ)
    (hident : ∀ i j, E[X i] = E[X j]) (μ : ℝ) (hμ : E[X 0] = μ) :
    E[sampleMean X] = μ := by
  sorry  -- 样本均值的无偏性

-- Fisher信息
-- I(θ) = E[(∂/∂θ) log f(X;θ)]^2 = -E[∂²/∂θ² log f(X;θ)]

-- Cramér-Rao下界
example (θ̂ : Ω → ℝ) (hθ̂ : Measurable θ̂) (hunbiased : ∀ θ, E[θ̂ | θ] = θ)
    (I : ℝ → ℝ) (hI : FisherInfo θ = I θ) :
    Var[θ̂ | θ] ≥ 1 / I θ := by
  sorry  -- Cramér-Rao下界
```

### 6. 假设检验

```lean4
import Mathlib.Statistics.HypothesisTesting

-- 第一类错误（显著性水平）
def type1Error (α : ℝ) (test : Ω → Bool) (H0 : Prop) : Prop := 
  ℙ {ω | test ω ∧ ¬H0} ≤ α

-- 第二类错误
def type2Error (β : ℝ) (test : Ω → Bool) (H1 : Prop) : Prop := 
  ℙ {ω | ¬test ω ∧ H1} ≤ β

-- 功效
def power (test : Ω → Bool) (H1 : Prop) : ℝ := 
  ℙ {ω | test ω ∧ H1}

-- p值
-- 在原假设下，得到当前或更极端结果的概率

-- 似然比检验
def likelihoodRatioTest (θ0 θ1 : ℝ) (X : Fin n → ℝ) : Bool := 
  (∏ i, likelihood θ1 (X i)) / (∏ i, likelihood θ0 (X i)) > c

-- Neyman-Pearson引理
example (test : Ω → Bool) (α : ℝ) (hα : type1Error α test H0) : 
    IsOptimal test := by
  sorry  -- 似然比检验的最优性
```

### 7. 线性回归

```lean4
import Mathlib.Statistics.Regression

-- 最小二乘估计
def OLS (X : Matrix (Fin n) (Fin p) ℝ) (Y : Fin n → ℝ) : Fin p → ℝ :=
  (Xᵀ * X)⁻¹ *ᵥ (Xᵀ *ᵥ Y)

-- OLS的性质
-- 1. 无偏性: E[β̂] = β
-- 2. 方差: Var[β̂] = σ²(X'X)^(-1)
-- 3. Gauss-Markov: BLUE

example (X : Matrix (Fin n) (Fin p) ℝ) (Y : Fin n → Ω → ℝ) 
    (β : Fin p → ℝ) (ε : Fin n → Ω → ℝ)
    (hY : ∀ i ω, Y i ω = (X *ᵥ β) i + ε i ω)
    (hEε : ∀ i, E[ε i] = 0) (hVarε : ∀ i, Var[ε i] = σ^2)
    (hIndepε : iIndep ε) :
    E[OLS X Y] = β := by
  sorry  -- OLS的无偏性
```

### 8. Bayes统计

```lean4
import Mathlib.Statistics.Bayes

-- 先验分布
def prior (θ : ℝ) : ℝ := sorry  -- 先验密度

-- 似然函数
def likelihood (θ : ℝ) (x : Fin n → ℝ) : ℝ := sorry  -- 似然函数

-- 后验分布 (Bayes公式)
def posterior (θ : ℝ) (x : Fin n → ℝ) : ℝ := 
  likelihood θ x * prior θ / (∫ θ', likelihood θ' x * prior θ')

-- 共轭先验
-- 例: Bernoulli + Beta ⟹ Beta后验

example (α β : ℝ) (x : Fin n → Bool) (npos : ℕ) :
    posterior (θ : ℝ) x ∝ θ^(npos + α - 1) * (1 - θ)^(n - npos + β - 1) := by
  sorry  -- Beta-Bernoulli共轭

-- Bayes估计
-- 后验均值
def bayesEstimate (x : Fin n → ℝ) : ℝ := 
  ∫ θ, θ * posterior θ x

-- 后验均值是最小化平方损失的Bayes估计
example (x : Fin n → ℝ) :
    bayesEstimate x = argmin (fun θ̂ => E[(θ - θ̂)^2 | x]) := by
  sorry
```

---

## 参考文献

### 概率论
1. Durrett, R., *Probability: Theory and Examples*, 5th ed., Cambridge, 2019
2. Billingsley, P., *Probability and Measure*, 3rd ed., Wiley, 1995
3. Feller, W., *An Introduction to Probability Theory and Its Applications*, Vol. 1-2, Wiley
4. Shiryaev, A.N., *Probability*, 2nd ed., Springer, 1996

### 随机过程
5. Karlin, S., Taylor, H.M., *A First Course in Stochastic Processes*, 2nd ed., Academic Press, 1975
6. Rogers, L.C.G., Williams, D., *Diffusions, Markov Processes and Martingales*, Vol. 1-2, Cambridge
7. Øksendal, B., *Stochastic Differential Equations*, 6th ed., Springer, 2003

### 统计学
8. Casella, G., Berger, R.L., *Statistical Inference*, 2nd ed., Duxbury, 2002
9. Lehmann, E.L., Casella, G., *Theory of Point Estimation*, 2nd ed., Springer, 1998
10. Lehmann, E.L., Romano, J.P., *Testing Statistical Hypotheses*, 3rd ed., Springer, 2005

### 数理统计
11. van der Vaart, A.W., *Asymptotic Statistics*, Cambridge, 1998
12. Bickel, P.J., Doksum, K.A., *Mathematical Statistics*, 2nd ed., Prentice Hall, 2015

### Bayes统计
13. Gelman, A., et al., *Bayesian Data Analysis*, 3rd ed., CRC Press, 2013
14. Robert, C.P., *The Bayesian Choice*, 2nd ed., Springer, 2007

---

**注**: 本文档是第五卷，涵盖了概率论与统计学的核心内容。

---

*本卷完成日期: 2025-03-26*  
*高优先级卷册已全部完成*
