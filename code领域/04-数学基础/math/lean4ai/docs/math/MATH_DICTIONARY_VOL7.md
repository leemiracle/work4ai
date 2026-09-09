# 数学知识词典 - 第七卷：数学物理
## Volume VII: Mathematical Physics

**MSC分类**: 70-XX, 76-XX, 78-XX, 81-XX, 82-XX, 83-XX  
**版本**: 1.0  
**日期**: 2025-03-26

---

## 目录

1. [经典力学 (70-XX)](#1-经典力学)
2. [量子力学 (81-XX)](#2-量子力学)
3. [统计力学 (82-XX)](#3-统计力学)
4. [相对论 (83-XX)](#4-相对论)

---

## 1. 经典力学 (70-XX)

### 1.1 Lagrange力学 [70Hxx]

#### 定义 XL.1.1 (Lagrange量)
**Definition XL.1.1 (Lagrangian)**

**Lagrange量**: L(q, q̇, t) = T - V
- T: 动能
- V: 势能
- q: 广义坐标
- q̇: 广义速度

**作用量**: S[q] = ∫_{t₁}^{t₂} L(q, q̇, t) dt

**Hamilton原理**: 真实运动使作用量取极值 δS = 0

#### 定理 40.1 (Euler-Lagrange方程)
**Theorem 40.1 (Euler-Lagrange Equations)**

从Hamilton原理得Euler-Lagrange方程:
```
d/dt(∂L/∂q̇^i) - ∂L/∂q^i = 0
```

**例子**:
1. **自由粒子**: L = (m/2)ẋ² → mẍ = 0
2. **谐振子**: L = (m/2)ẋ² - (k/2)x² → mẍ + kx = 0
3. **中心力场**: L = (m/2)(ṙ² + r²θ̇²) - V(r)

---

### 1.2 Hamilton力学 [70Hxx]

#### 定义 XL.2.1 (Hamilton量)
**Definition XL.2.1 (Hamiltonian)**

**广义动量**: p_i = ∂L/∂q̇^i

**Hamilton量** (Legendre变换): H(q, p, t) = Σ p_i q̇^i - L

**Hamilton方程**:
```
q̇^i = ∂H/∂p_i
ṗ_i = -∂H/∂q^i
```

**相空间**: (q, p)空间，2n维

**Liouville定理**: 相空间体积在Hamilton流下守恒

#### 定理 40.2 (Noether定理)
**Theorem 40.2 (Noether's Theorem)**

连续对称性 ⟺ 守恒量

**例子**:
1. 时间平移对称 → 能量守恒
2. 空间平移对称 → 动量守恒
3. 旋转对称 → 角动量守恒

---

## 2. 量子力学 (81-XX)

### 2.1 量子力学公理 [81Pxx]

#### 公理 I (态矢量)
**Axiom I (State Vectors)**

**量子态**: Hilbert空间H中的单位向量|ψ⟩ (||ψ|| = 1)

**叠加原理**: |ψ₁⟩和|ψ₂⟩是可能态 ⟹ α|ψ₁⟩ + β|ψ₂⟩也是可能态

#### 公理 II (可观测量)
**Axiom II (Observables)**

**可观测量**: 自伴算符A = A†

**谱定理**: A = Σ λ_n P_n (P_n是投影)

**测量**: 测量A得到本征值λ_n，概率P(λ_n) = ⟨ψ|P_n|ψ⟩

**期望**: ⟨A⟩ = ⟨ψ|A|ψ⟩

**不确定度**: ΔA = √(⟨A²⟩ - ⟨A⟩²)

#### 公理 III (时间演化)
**Axiom III (Time Evolution)**

**Schrödinger方程**: iℏ ∂|ψ⟩/∂t = H|ψ⟩

**演化算符**: U(t) = e^{-iHt/ℏ} (酉算符)

**定态**: H|ψ_n⟩ = E_n|ψ_n⟩

---

### 2.2 不确定关系 [81Pxx]

#### 定理 41.1 (Heisenberg不确定关系)
**Theorem 41.1 (Heisenberg Uncertainty Principle)**

对可观测量A, B:
```
ΔA · ΔB ≥ |⟨[A,B]⟩|/2
```

**特例** (位置-动量): Δx · Δp ≥ ℏ/2

*证明*. Cauchy-Schwarz不等式。 □

---

### 2.3 简单量子系统 [81Qxx]

#### 例子 41.1 (一维谐振子)
**Example 41.1 (1D Harmonic Oscillator)**

**Hamilton量**: H = p²/(2m) + (mω²/2)x²

**能谱**: E_n = ℏω(n + 1/2), n = 0, 1, 2, ...

**升降算符**:
- a|n⟩ = √n|n-1⟩
- a†|n⟩ = √(n+1)|n+1⟩
- [a, a†] = 1

#### 例子 41.2 (氢原子)
**Example 41.2 (Hydrogen Atom)**

**Hamilton量**: H = p²/(2m) - e²/(4πε₀r)

**能谱**: E_n = -13.6 eV/n²

**量子数**: (n, ℓ, m, s)
- n = 1, 2, 3, ... (主量子数)
- ℓ = 0, 1, ..., n-1 (角量子数)
- m = -ℓ, ..., ℓ (磁量子数)
- s = ±1/2 (自旋)

**简并度**: 2n² (含自旋)

---

### 2.4 自旋 [81Rxx]

#### 定义 XLI.4.1 (自旋算符)
**Definition XLI.4.1 (Spin Operators)**

**Pauli矩阵**:
```
σ_x = [0  1]   σ_y = [0 -i]   σ_z = [1  0]
      [1  0]         [i  0]         [0 -1]
```

**性质**:
- σ_i² = I
- {σ_i, σ_j} = 0 (i ≠ j)
- [σ_i, σ_j] = 2iε_{ijk} σ_k

**自旋算符**: S_i = (ℏ/2)σ_i

**总角动量**: J = L + S

---

## 3. 统计力学 (82-XX)

### 3.1 统计系综 [82Axx]

#### 定义 XLII.1.1 (微正则系综)
**Definition XLII.1.1 (Microcanonical Ensemble)**

**条件**: 孤立系统，能量E固定

**熵** (Boltzmann): S = k_B ln Ω(E)
- Ω(E): 能量E附近的态数
- k_B: Boltzmann常数 (1.38×10⁻²³ J/K)

**温度**: 1/T = ∂S/∂E

#### 定义 XLII.1.2 (正则系综)
**Definition XLII.1.2 (Canonical Ensemble)**

**条件**: 系统与热库接触，温度T固定

**Boltzmann分布**:
```
P(E_n) = e^{-βE_n}/Z
Z = Σ_n e^{-βE_n}  (配分函数)
β = 1/(k_B T)
```

**自由能**: F = -k_B T ln Z = U - TS

**内能**: U = ⟨E⟩ = -∂ ln Z/∂β

**熵**: S = k_B(ln Z + βU)

#### 定义 XLII.1.3 (巨正则系综)
**Definition XLII.1.3 (Grand Canonical Ensemble)**

**条件**: 粒子数和能量可变，化学势μ

**概率**:
```
P(N, E_n) = e^{-β(E_n - μN)}/Ξ
Ξ = Σ_{N,n} e^{-β(E_n - μN)}
```

**巨势**: Ω = -k_B T ln Ξ

---

### 3.2 量子统计 [82Bxx]

#### 定义 XLII.2.1 (Bose-Einstein统计)
**Definition XLII.2.1 (Bose-Einstein Statistics)**

**Bose子**: 自旋整数，波函数对称

**分布**: n(ε) = 1/(e^{β(ε-μ)} - 1)

**Bose-Einstein凝聚**: T < T_c时宏观数目粒子占据基态

**例子**: 
- 光子 (自旋1)
- He-4 (自旋0)
- Cooper对 (有效自旋0)

#### 定义 XLII.2.2 (Fermi-Dirac统计)
**Definition XLII.2.2 (Fermi-Dirac Statistics)**

**Fermi子**: 自旋半整数，波函数反对称

**分布**: n(ε) = 1/(e^{β(ε-μ)} + 1)

**Pauli不相容原理**: 每个量子态最多一个Fermi子

**Fermi能级**: T=0时最高占据态能量 ε_F

**例子**:
- 电子 (自旋1/2)
- 质子、中子 (自旋1/2)

---

### 3.3 相变 [82Bxx]

#### 定义 XLII.3.1 (序参数)
**Definition XLII.3.1 (Order Parameter)**

**序参数**: 区分相的宏观量

**例子**:
- 铁磁: 磁化强度 M
- 液气: 密度差 ρ_L - ρ_G
- 超导: 能隙 Δ

**临界指数**:
- 序参数: M ~ (T_c - T)^β
- 磁化率: χ ~ |T - T_c|^{-γ}
- 关联长度: ξ ~ |T - T_c|^{-ν}

**普适性**: 同一普适类的系统有相同临界指数

---

### 3.4 Ising模型 [82Bxx]

#### 定义 XLII.4.1 (Ising模型)
**Definition XLII.4.1 (Ising Model)**

**Hamilton量**: H = -J Σ_{⟨ij⟩} s_i s_j - h Σ_i s_i
- s_i = ±1 (自旋)
- J: 耦合常数 (J>0铁磁)
- h: 外场

**1维**: 无相变 (严格解，Ising 1925)

**2维**: 有相变 (严格解，Onsager 1944)
- 临界温度: k_B T_c/J = 2/ln(1+√2) ≈ 2.269
- 临界指数: β = 1/8, γ = 7/4

**3维**: 数值计算，无严格解

---

## 4. 相对论 (83-XX)

### 4.1 狭义相对论 [83Axx]

#### 定义 XLIII.1.1 (Lorentz变换)
**Definition XLIII.1.1 (Lorentz Transformation)**

**Lorentz变换** (沿x轴速度v):
```
t' = γ(t - vx/c²)
x' = γ(x - vt)
y' = y
z' = z
γ = 1/√(1 - v²/c²)
```

**不变量**: 间隔 ds² = c²dt² - dx² - dy² - dz²

**时间膨胀**: Δt' = γΔt

**长度收缩**: Δx' = Δx/γ

**同时性**: 相对性 - 不同参考系同时性不同

#### 定理 43.1 (能量-动量关系)
**Theorem 43.1 (Energy-Momentum Relation)**

**四动量**: p^μ = (E/c, **p**)

**不变量**: p·p = m²c²

**展开**: E² = p²c² + m²c⁴

**静止能量**: E_0 = mc²

**相对论质量**: m_rel = γm

---

### 4.2 广义相对论基础 [83Cxx]

#### 定义 XLIII.2.1 (度规张量)
**Definition XLIII.2.1 (Metric Tensor)**

**时空**: 4维Lorentz流形(M, g)

**度规**: g_{μν} (符号 -+++ 或 +---)

**线元**: ds² = g_{μν} dx^μ dx^ν

**例子**:
- **Minkowski**: ds² = -c²dt² + dx² + dy² + dz²
- **Schwarzschild**: ds² = -(1-2GM/rc²)c²dt² + (1-2GM/rc²)^{-1}dr² + r²dΩ²

#### 定理 43.2 (Einstein场方程)
**Theorem 43.2 (Einstein Field Equations)**

```
G_{μν} + Λg_{μν} = (8πG/c⁴) T_{μν}
```

其中:
- Einstein张量: G_{μν} = R_{μν} - (1/2)R g_{μν}
- Ricci张量: R_{μν}
- 标量曲率: R
- 宇宙常数: Λ
- 能动张量: T_{μν}

**作用量** (Einstein-Hilbert):
```
S = (c³/16πG) ∫ (R - 2Λ) √(-g) d⁴x + S_matter
```

---

### 4.3 黑洞 [83Cxx]

#### 定义 XLIII.3.1 (Schwarzschild黑洞)
**Definition XLIII.3.1 (Schwarzschild Black Hole)**

**度规** (球对称真空解):
```
ds² = -(1 - r_s/r)c²dt² + (1 - r_s/r)^{-1}dr² + r²dΩ²
```

**Schwarzschild半径**: r_s = 2GM/c²

**事件视界**: r = r_s (单向膜，光无法逃逸)

**奇点**: r = 0 (曲率发散)

**性质**:
1. **无毛定理**: 黑洞完全由(M, Q, J)刻画
2. **Hawking辐射**: T_H = ℏc³/(8πGMk_B)
3. **黑洞熵**: S = k_B A/(4ℓ_P²) (Bekenstein-Hawking)

#### 定义 XLIII.3.2 (Kerr黑洞)
**Definition XLIII.3.2 (Kerr Black Hole)**

**旋转黑洞**: 角动量J ≠ 0

**Kerr度规**: 轴对称，有能层(ergosphere)

**Penrose过程**: 从能层提取能量

---

### 4.4 宇宙学 [83Fxx]

#### 定义 XLIII.4.1 (FRW度规)
**Definition XLIII.4.1 (FRW Metric)**

**度规** (均匀各向同性宇宙):
```
ds² = -c²dt² + a(t)² [dr²/(1-kr²) + r²dΩ²]
```

**标度因子**: a(t)

**曲率**: k = {-1, 0, +1} (开, 平, 闭)

**Hubble参数**: H = ȧ/a

**当前观测**: H₀ ≈ 70 km/s/Mpc

#### 定理 43.3 (Friedmann方程)
**Theorem 43.3 (Friedmann Equations)**

**第一方程**:
```
(ȧ/a)² = (8πG/3c²)ρ - kc²/a² + Λc²/3
```

**第二方程**:
```
ä/a = -(4πG/3c²)(ρ + 3p/c²) + Λc²/3
```

**宇宙组分** (当前):
- 暗能量: Ω_Λ ≈ 0.69
- 暗物质: Ω_DM ≈ 0.26
- 重子物质: Ω_b ≈ 0.05

---

### 4.5 引力波 [83Cxx]

#### 定义 XLIII.5.1 (引力波)
**Definition XLIII.5.1 (Gravitational Waves)**

**产生**: 加速的质量分布

**波动方程** (弱场近似):
```
□ h_{μν} = -16πG/c⁴ T_{μν}
```

**性质**:
- 横波，两种偏振模式 (+, ×)
- 传播速度 = c
- 携带能量和角动量

**探测**: LIGO (2015年首次探测)

**源**: 双黑洞合并、双中子星合并

---

## Lean4 代码示例

本节提供与第七卷（数学物理）内容相关的Lean4代码示例。

### 1. 经典力学 - Lagrangian与Hamiltonian

```lean4
import Mathlib.Analysis.Calculus.FDeriv

-- Lagrangian L(q, q̇, t)
-- Hamiltonian H(q, p, t) = p·q̇ - L

-- Euler-Lagrange方程
-- d/dt(∂L/∂q̇) - ∂L/∂q = 0

-- Hamilton正则方程
-- q̇ = ∂H/∂p
-- ṗ = -∂H/∂q

-- 谐振子
-- L = (1/2)m*q̇² - (1/2)k*q²
def harmonicLagrangian (m k : ℝ) (q q̇ : ℝ) : ℝ :=
  (1/2) * m * q̇^2 - (1/2) * k * q^2

-- Hamiltonian
def harmonicHamiltonian (m k : ℝ) (q p : ℝ) : ℝ :=
  p^2 / (2 * m) + (1/2) * k * q^2

-- 能量守恒
example (m k : ℝ) (q p : ℝ) :
    harmonicHamiltonian m k q p = 
    (1/2) * m * (p/m)^2 + (1/2) * k * q^2 := by
  ring_nf

-- Legendre变换
example (m k q : ℝ) (hm : 0 < m) (hk : 0 < k) :
    let q̇ := p / m
    let L := harmonicLagrangian m k q q̇
    let H := harmonicHamiltonian m k q (m * q̇)
    p * q̇ - L = H := by
  sorry
```

### 2. 量子力学 - Hilbert空间与算子

```lean4
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Analysis.InnerProductSpace.Spectrum

-- 量子态空间: Hilbert空间
-- 可观测量: 自伴算子

-- Schrödinger方程
-- iℏ ∂ψ/∂t = Ĥψ

-- 测量公理
-- 测量可观测量A得到本征值λ的概率 = |⟨λ|ψ⟩|²

-- 位置与动量算子的对易关系
-- [x̂, p̂] = iℏ

-- 不确定性原理
-- Δx · Δp ≥ ℏ/2

example (H : Type*) [InnerProductSpace ℂ H] [CompleteSpace H]
    (ψ : H) (hnorm : ‖ψ‖ = 1) :
    ∃ x p : ℝ, variance ψ x * variance ψ p ≥ (1/2 : ℝ) := by
  sorry  -- Heisenberg不确定性原理

-- 薛定谔猫态 (叠加)
def catState (α β : ℂ) (hαβ : |α|^2 + |β|^2 = 1) : ℂ^2 :=
  (α, β)

-- 测量坍缩
example (α β : ℂ) (hαβ : |α|^2 + |β|^2 = 1) :
    probabilityMeasure (catState α β hαβ) = (|α|^2, |β|^2) := by
  sorry
```

### 3. 统计力学 - 配分函数

```lean4
import Mathlib.Analysis.SpecialFunctions.Pow.Real

-- 正则系综
-- 配分函数 Z = Σᵢ e^(-βEᵢ)
-- β = 1/(k_B T)

-- 自由能 F = -k_B T ln Z

-- 内能 U = -∂ln Z/∂β

-- 熵 S = k_B (ln Z + βU)

-- 理想气体的配分函数
def idealGasPartitionFunction (N : ℕ) (V β m : ℝ) : ℝ :=
  (V / N!) * (2 * Real.pi * m / β)^(3*N/2)

-- Maxwell-Boltzmann分布
def maxwellBoltzmann (β m : ℝ) (v : ℝ^3) : ℝ :=
  (β * m / (2 * Real.pi))^(3/2) * Real.exp (-β * m * ‖v‖^2 / 2)

-- Bose-Einstein分布
def boseEinstein (β ε μ : ℝ) : ℝ :=
  1 / (Real.exp (β * (ε - μ)) - 1)

-- Fermi-Dirac分布
def fermiDirac (β ε μ : ℝ) : ℝ :=
  1 / (Real.exp (β * (ε - μ)) + 1)

-- Fermi-Dirac分布的性质
example (β ε μ : ℝ) (hβ : 0 < β) :
    0 < fermiDirac β ε μ ∧ fermiDirac β ε μ < 1 := by
  sorry
```

### 4. 狭义相对论

```lean4
import Mathlib.Analysis.SpecialFunctions.Pow.Real

-- Lorentz变换
-- x' = γ(x - vt)
-- t' = γ(t - vx/c²)
-- γ = 1/√(1 - v²/c²)

def lorentzFactor (v c : ℝ) : ℝ :=
  1 / Real.sqrt (1 - (v/c)^2)

-- 时间膨胀
-- Δt' = γΔt

example (v c Δt : ℝ) (hv : 0 < v) (hc : v < c) :
    lorentzFactor v c * Δt > Δt := by
  sorry

-- 长度收缩
-- Δx' = Δx/γ

example (v c Δx : ℝ) (hv : 0 < v) (hc : v < c) :
    Δx / lorentzFactor v c < Δx := by
  sorry

-- 质能关系
-- E = mc² = γm₀c²

def relativisticEnergy (m₀ v c : ℝ) : ℝ :=
  lorentzFactor v c * m₀ * c^2

-- 动量
def relativisticMomentum (m₀ v c : ℝ) : ℝ :=
  lorentzFactor v c * m₀ * v

-- 能量-动量关系
-- E² = (pc)² + (m₀c²)²

example (m₀ v c : ℝ) (hv : 0 ≤ v) (hc : v < c) :
    relativisticEnergy m₀ v c^2 = 
    (relativisticMomentum m₀ v c * c)^2 + (m₀ * c^2)^2 := by
  sorry
```

### 5. 热力学

```lean4
-- 热力学势
-- 内能 U(S, V)
-- 焓 H = U + PV
-- Helmholtz自由能 F = U - TS
-- Gibbs自由能 G = H - TS

-- Maxwell关系
-- (∂T/∂V)_S = -(∂P/∂S)_V
-- (∂T/∂P)_S = (∂V/∂S)_P

-- 理想气体状态方程
-- PV = nRT

def idealGasPressure (n R T V : ℝ) : ℝ := n * R * T / V

-- 热容
-- C_V = (∂U/∂T)_V
-- C_P = (∂H/∂T)_P

example (n R : ℝ) : 
    C_P - C_V = n * R := by  -- 对理想气体
  sorry

-- 熵变
-- dS = dQ_rev/T

example (T₁ T₂ : ℝ) (hT : T₁ < T₂) (C : ℝ) :
    entropyChange C T₁ T₂ = C * Real.log (T₂ / T₁) := by
  sorry
```

### 6. 流体力学基础

```lean4
-- 连续性方程
-- ∂ρ/∂t + ∇·(ρv) = 0

-- Euler方程 (无粘)
-- ∂v/∂t + (v·∇)v = -∇p/ρ + g

-- Navier-Stokes方程
-- ∂v/∂t + (v·∇)v = -∇p/ρ + ν∇²v + g

-- 不可压缩条件
-- ∇·v = 0

-- Reynolds数
def reynoldsNumber (ρ v L μ : ℝ) : ℝ :=
  ρ * v * L / μ

-- 层流与湍流的判据
example (ρ v L μ : ℝ) (hRe : reynoldsNumber ρ v L μ < 2300) :
    IsLaminarFlow ρ v L μ := by
  sorry

-- Bernoulli方程
-- P + (1/2)ρv² + ρgh = 常数

example (P₁ v₁ h₁ P₂ v₂ h₂ ρ g : ℝ) 
    (hBernoulli : P₁ + (1/2)*ρ*v₁^2 + ρ*g*h₁ = P₂ + (1/2)*ρ*v₂^2 + ρ*g*h₂) :
    True := by trivial
```

### 7. Ising模型

```lean4
-- Ising Hamilton量
-- H = -J Σ_{⟨ij⟩} s_i s_j - h Σ_i s_i

def isingHamiltonian (J h : ℝ) (spins : ℤ → ℝ) (n : ℕ) : ℝ :=
  -- 最近邻相互作用
  (∑ i ∈ Finset.range n, -J * spins i * spins (i + 1)) +
  (∑ i ∈ Finset.range n, -h * spins i)

-- 磁化强度
def magnetization (spins : ℤ → ℝ) (n : ℕ) : ℝ :=
  (∑ i ∈ Finset.range n, spins i) / n

-- 配分函数 (需要求和所有构型)
-- Z = Σ_{configurations} exp(-βH)

-- 1D Ising模型的严格解
example (J h β : ℝ) (n : ℕ) :
    partitionFunction1D J h β n > 0 := by
  sorry

-- 2D Ising模型的Onsager解 (无外场)
-- T_c = 2J / (k_B * ln(1 + √2))

example (J k_B : ℝ) :
    criticalTemperature2D J k_B = 2 * J / (k_B * Real.log (1 + Real.sqrt 2)) := by
  sorry
```

### 8. 相对论场论

```lean4
-- 作用量原理
-- δS = 0

-- Klein-Gordon方程
-- (□ + m²)φ = 0
-- □ = ∂²/∂t² - ∇²

-- Dirac方程
-- (iγ^μ∂_μ - m)ψ = 0

-- 电磁场 (Maxwell方程)
-- ∇·E = ρ/ε₀
-- ∇×E = -∂B/∂t
-- ∇·B = 0
-- ∇×B = μ₀J + μ₀ε₀∂E/∂t

-- 能量-动量张量
-- T^μν = (ε₀E² + B²/μ₀)  (能量密度)

-- 规范对称性
-- A_μ → A_μ + ∂_μΛ  (U(1)规范变换)

-- Noether定理
-- 连续对称性 → 守恒律

example (symmetry : ContinuousSymmetry) :
    ∃ conservedQuantity, IsConserved conservedQuantity := by
  sorry  -- Noether定理
```

---

## 参考文献

### 经典力学
1. Goldstein, H., Poole, C., Safko, J., *Classical Mechanics*, 3rd ed., Addison-Wesley, 2001
2. Landau, L.D., Lifshitz, E.M., *Mechanics*, 3rd ed., Butterworth-Heinemann, 1976
3. Arnold, V.I., *Mathematical Methods of Classical Mechanics*, 2nd ed., Springer, 1989

### 量子力学
4. Sakurai, J.J., Napolitano, J., *Modern Quantum Mechanics*, 2nd ed., Pearson, 2017
5. Griffiths, D.J., *Introduction to Quantum Mechanics*, 3rd ed., Cambridge, 2018
6. Shankar, R., *Principles of Quantum Mechanics*, 2nd ed., Springer, 1994

### 统计力学
7. Pathria, R.K., Beale, P.D., *Statistical Mechanics*, 3rd ed., Academic Press, 2011
8. Huang, K., *Statistical Mechanics*, 2nd ed., Wiley, 1987
9. Reichl, L.E., *A Modern Course in Statistical Physics*, 4th ed., Wiley, 2016

### 相对论
10. Misner, C.W., Thorne, K.S., Wheeler, J.A., *Gravitation*, Princeton, 2017
11. Wald, R.M., *General Relativity*, Chicago, 1984
12. Carroll, S.M., *Spacetime and Geometry*, Addison-Wesley, 2004

### 综合参考
13. Landau, L.D., Lifshitz, E.M., *Course of Theoretical Physics*, Vol. 1-10, Butterworth-Heinemann
14. Thorne, K.S., *Modern Classical Physics*, Princeton, 2017

---

**注**: 本文档是第七卷，涵盖了数学物理的核心内容。

---

*本卷完成日期: 2025-03-26*  
*下一卷预告: 应用数学（已创建为第八卷）*
