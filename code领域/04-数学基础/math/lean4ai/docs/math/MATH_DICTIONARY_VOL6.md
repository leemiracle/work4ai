# 数学知识词典 - 第六卷：数值分析与计算数学
## Volume VI: Numerical Analysis and Computational Mathematics

**MSC分类**: 65-XX, 68-XX  
**版本**: 1.0  
**日期**: 2025-03-26

---

## 目录

1. [数值线性代数 (65Fxx)](#1-数值线性代数)
2. [数值逼近 (65Dxx)](#2-数值逼近)
3. [常微分方程数值方法 (65Lxx)](#3-常微分方程数值方法)
4. [偏微分方程数值方法 (65Mxx, 65Nxx)](#4-偏微分方程数值方法)
5. [计算复杂度 (68Qxx)](#5-计算复杂度)

---

## 1. 数值线性代数 (65Fxx)

### 1.1 线性方程组求解 [65Fxx]

#### 定义 XXXV.1.1 (条件数)
**Definition XXXV.1.1 (Condition Number)**

矩阵A的**条件数**: κ(A) = ||A||·||A^{-1}||

**意义**: 刻画线性方程组Ax=b对输入扰动的敏感性
```
||δx||/||x|| ≤ κ(A) (||δA||/||A|| + ||δb||/||b||)
```

**性质**:
- κ(A) ≥ 1
- κ(A) = σ_max/σ_min (奇异值比)
- κ(A)大 → 问题病态(ill-conditioned)

**例子**:
- Hilbert矩阵: κ(H_n) ~ e^{3.5n} (严重病态)
- 正交矩阵: κ(Q) = 1 (最优)

---

### 1.2 LU分解 [65Fxx]

#### 算法 35.1 (LU分解)
**Algorithm 35.1 (LU Factorization)**

**目标**: A = LU，L下三角(对角1)，U上三角

**算法** (不带主元):
```
for k = 1 to n-1:
    for i = k+1 to n:
        L[i,k] = A[i,k] / A[k,k]
        for j = k to n:
            A[i,j] -= L[i,k] * A[k,j]
```

**复杂度**: O(n³/3)

**主元选取**:
- 部分主元: 选择列中最大元 (数值稳定)
- 全主元: 选择子矩阵中最大元 (更稳定但昂贵)

#### 定理 35.1 (LU分解的存在性)
**Theorem 35.1 (Existence of LU Factorization)**

若A的所有顺序主子式非零，则存在唯一LU分解。

*带主元*: 对任意可逆A，存在置换P使得PA = LU。

---

### 1.3 QR分解 [65Fxx]

#### 算法 35.2 (Gram-Schmidt)
**Algorithm 35.2 (Gram-Schmidt Process)**

**目标**: A = QR (Q正交，R上三角)

**经典Gram-Schmidt** (数值不稳定):
```
for k = 1 to n:
    v_k = a_k
    for j = 1 to k-1:
        r_{jk} = q_j^T a_k
        v_k -= r_{jk} * q_j
    r_{kk} = ||v_k||
    q_k = v_k / r_{kk}
```

**修正Gram-Schmidt** (稳定):
```
for k = 1 to n:
    r_{kk} = ||a_k||
    q_k = a_k / r_{kk}
    for j = k+1 to n:
        r_{kj} = q_k^T a_j
        a_j -= r_{kj} * q_k
```

#### 算法 35.3 (Householder变换)
**Algorithm 35.3 (Householder Transformation)**

**Householder矩阵**: H = I - 2vv^T/||v||² (反射)

**性质**:
- H正交对称
- Hx = ||x||e₁ (适当选择v)

**算法**:
```
for k = 1 to n-1:
    x = A[k:m, k]
    v = x + sign(x_1)||x||e₁
    v = v / ||v||
    A[k:m, k:n] -= 2v(v^T A[k:m, k:n])
```

**复杂度**: O(2mn² - 2n³/3)

---

### 1.4 特征值计算 [65Fxx]

#### 算法 35.4 (QR算法)
**Algorithm 35.4 (QR Algorithm)**

**基本QR算法**:
```
A_0 = A
for k = 1,2,...:
    A_k = Q_k R_k (QR分解)
    A_{k+1} = R_k Q_k
```

**收敛**: A_k → 上三角(T)或分块上三角，对角元→特征值

**改进**:
1. **移位**: A_k - μ_k I，加速收敛
2. **双重移位**: 处理复特征值(实矩阵)
3. **缩减**: 利用Hessenberg形式

**复杂度**: O(n³) (预处理) + O(n²) (每次迭代)

#### 定理 35.2 (QR算法的收敛性)
**Theorem 35.2 (Convergence of QR Algorithm)**

若A的特征值满足|λ₁| > |λ₂| > ... > |λ_n| > 0，则QR算法线性收敛:
```
a_{i,j}^{(k)} → 0  (i>j) 当 k→∞
a_{i,i}^{(k)} → λ_i
```

---

### 1.5 迭代方法 [65Fxx]

#### 算法 35.5 (共轭梯度法)
**Algorithm 35.5 (Conjugate Gradient Method)**

**适用于**: 对称正定矩阵Ax = b

**算法**:
```
x_0 = 0, r_0 = b, p_0 = r_0
for k = 0,1,...:
    α_k = (r_k^T r_k) / (p_k^T A p_k)
    x_{k+1} = x_k + α_k p_k
    r_{k+1} = r_k - α_k A p_k
    β_k = (r_{k+1}^T r_{k+1}) / (r_k^T r_k)
    p_{k+1} = r_{k+1} + β_k p_k
```

**收敛**:
```
||x_k - x*||_A ≤ 2 [(√κ - 1)/(√κ + 1)]^k ||x_0 - x*||_A
```

**预处理**: 用M ≈ A改善条件数，求解M^{-1}Ax = M^{-1}b

#### 算法 35.6 (GMRES)
**Algorithm 35.6 (GMRES)**

**适用于**: 一般非奇异矩阵

**思想**: 在Krylov子空间K_k(A,b) = span{b, Ab, ..., A^{k-1}b}中最小化残差

**算法**: Arnoldi过程 + 最小二乘

---

## 2. 数值逼近 (65Dxx)

### 2.1 多项式插值 [65Dxx]

#### 定义 XXXVI.1.1 (Lagrange插值)
**Definition XXXVI.1.1 (Lagrange Interpolation)**

给定点(x_i, y_i), i=0,...,n，**Lagrange插值多项式**:
```
P_n(x) = Σ_{i=0}^n y_i L_i(x)
L_i(x) = Π_{j≠i} (x - x_j)/(x_i - x_j)
```

**误差** (插值余项):
```
f(x) - P_n(x) = f^{(n+1)}(ξ)/(n+1)! · Π(x - x_i)
```

**Runge现象**: 等距节点在区间端点振荡

**解决**: Chebyshev节点 x_i = cos((2i+1)π/(2n+2))

---

### 2.2 样条插值 [65Dxx]

#### 定义 XXXVI.2.1 (三次样条)
**Definition XXXVI.2.1 (Cubic Splines)**

**三次样条** S(x)满足:
1. S(x_i) = y_i (插值)
2. 在每个[x_i, x_{i+1}]上是三次多项式
3. S, S', S''在内部节点连续

**边界条件**:
- 自然: S''(x_0) = S''(x_n) = 0
- 固定: S'(x_0) = f'_0, S'(x_n) = f'_n
- 周期: S'(x_0) = S'(x_n), S''(x_0) = S''(x_n)

**定理**: 三次样条存在唯一(适当边界条件)

**性质**: 最小曲率性质

---

### 2.3 数值积分 [65Dxx]

#### 算法 36.1 (Newton-Cotes公式)
**Algorithm 36.1 (Newton-Cotes Formulas)**

**梯形法则** (n=1):
```
∫_a^b f(x)dx ≈ (b-a)/2 [f(a) + f(b)]
误差: -(b-a)³/12 f''(ξ)
```

**Simpson法则** (n=2):
```
∫_a^b f(x)dx ≈ (b-a)/6 [f(a) + 4f((a+b)/2) + f(b)]
误差: -(b-a)^5/2880 f^{(4)}(ξ)
```

**复合公式**:
- 复合梯形: T_n = h/2 [f(a) + 2Σf(x_i) + f(b)], h=(b-a)/n
- 复合Simpson: S_n = h/3 [f(a) + 4Σf(x_{2i-1}) + 2Σf(x_{2i}) + f(b)]

#### 算法 36.2 (Gauss求积)
**Algorithm 36.2 (Gaussian Quadrature)**

**Gauss-Legendre**: 
```
∫_{-1}^1 f(x)dx ≈ Σ_{i=1}^n w_i f(x_i)
```
其中x_i是Legendre多项式P_n(x)的根，w_i = 2/[(1-x_i²)P'_n(x_i)²]

**精度**: 2n-1次多项式精确

**例子** (n=2): x = ±1/√3, w = 1

---

### 2.4 数值微分 [65Dxx]

#### 公式 36.1 (差分公式)
**Formulas 36.1 (Finite Difference Formulas)**

**一阶导数**:
- 前向: f'(x) ≈ [f(x+h) - f(x)]/h, 误差O(h)
- 后向: f'(x) ≈ [f(x) - f(x-h)]/h, 误差O(h)
- 中心: f'(x) ≈ [f(x+h) - f(x-h)]/(2h), 误差O(h²)

**二阶导数**:
```
f''(x) ≈ [f(x+h) - 2f(x) + f(x-h)]/h², 误差O(h²)
```

**Richardson外推**: 提高精度

---

## 3. 常微分方程数值方法 (65Lxx)

### 3.1 单步方法 [65Lxx]

#### 算法 37.1 (Euler方法)
**Algorithm 37.1 (Euler's Method)**

**问题**: y' = f(t,y), y(t₀) = y₀

**显式Euler**:
```
y_{n+1} = y_n + h f(t_n, y_n)
```

**局部截断误差**: O(h²)
**全局误差**: O(h)

**隐式Euler**:
```
y_{n+1} = y_n + h f(t_{n+1}, y_{n+1})
```
**稳定性**: A-稳定 (对刚性方程)

#### 算法 37.2 (Runge-Kutta方法)
**Algorithm 37.2 (Runge-Kutta Methods)**

**经典4阶RK** (RK4):
```
k_1 = f(t_n, y_n)
k_2 = f(t_n + h/2, y_n + hk_1/2)
k_3 = f(t_n + h/2, y_n + hk_2/2)
k_4 = f(t_n + h, y_n + hk_3)
y_{n+1} = y_n + h(k_1 + 2k_2 + 2k_3 + k_4)/6
```

**局部截断误差**: O(h^5)
**全局误差**: O(h⁴)

---

### 3.2 多步方法 [65Lxx]

#### 算法 37.3 (线性多步法)
**Algorithm 37.3 (Linear Multistep Methods)**

**一般形式**:
```
Σ_{j=0}^k α_j y_{n+j} = h Σ_{j=0}^k β_j f(t_{n+j}, y_{n+j})
```

**Adams-Bashforth** (显式):
- 2步: y_{n+1} = y_n + h(3f_n - f_{n-1})/2
- 4步: y_{n+1} = y_n + h(55f_n - 59f_{n-1} + 37f_{n-2} - 9f_{n-3})/24

**Adams-Moulton** (隐式):
- 2步: y_{n+1} = y_n + h(f_{n+1} + f_n)/2
- 4步: y_{n+1} = y_n + h(9f_{n+1} + 19f_n - 5f_{n-1} + f_{n-2})/24

**预测-校正**: Adams-Bashforth预测 + Adams-Moulton校正

---

### 3.3 稳定性 [65Lxx]

#### 定义 XXXVII.3.1 (稳定性)
**Definition XXXVII.3.1 (Stability)**

**测试方程**: y' = λy (Re(λ) < 0)

**绝对稳定域**: {z = λh : |R(z)| < 1}，R(z)是稳定函数

**A-稳定**: 绝对稳定域包含左半平面

**例子**:
- 显式Euler: |1 + z| < 1 (圆，不是A稳定)
- 隐式Euler: |1/(1-z)| < 1 (A稳定)
-梯形法则: |(1+z/2)/(1-z/2)| < 1 (A稳定)

**刚性方程**: 不同时间尺度，需要隐式方法

---

## 4. 偏微分方程数值方法 (65Mxx, 65Nxx)

### 4.1 有限差分法 [65Mxx]

#### 问题 38.1 (热方程)
**Problem 38.1 (Heat Equation)**

**热方程**: u_t = αu_{xx}, 0 < x < L, t > 0

**显式格式** (FTCS):
```
(u_i^{n+1} - u_i^n)/Δt = α(u_{i+1}^n - 2u_i^n + u_{i-1}^n)/Δx²
```

**稳定性条件** (CFL): r = αΔt/Δx² ≤ 1/2

**隐式格式** (后向Euler):
```
(u_i^{n+1} - u_i^n)/Δt = α(u_{i+1}^{n+1} - 2u_i^{n+1} + u_{i-1}^{n+1})/Δx²
```
无条件稳定

**Crank-Nicolson**:
```
(u_i^{n+1} - u_i^n)/Δt = α/2[(u_{i+1}^{n+1} - 2u_i^{n+1} + u_{i-1}^{n+1})/Δx² + (u_{i+1}^n - 2u_i^n + u_{i-1}^n)/Δx²]
```
无条件稳定，O(Δt², Δx²)

---

### 4.2 有限元法 [65Nxx]

#### 算法 38.1 (Ritz-Galerkin方法)
**Algorithm 38.1 (Ritz-Galerkin Method)**

**问题**: -u'' = f, u(0) = u(1) = 0

**弱形式**: 找u ∈ H₀¹使得∫ u'v' dx = ∫ fv dx (所有v ∈ H₀¹)

**Galerkin逼近**: u_h = Σ c_j φ_j (φ_j是基函数)

**线性系统**: Kc = F
- K_{ij} = ∫ φ'_i φ'_j dx (刚度矩阵)
- F_i = ∫ f φ_i dx (载荷向量)

**分片线性元** (P1):
- 节点基函数
- 误差: ||u - u_h||_H¹ ≤ Ch||u''||

---

### 4.3 谱方法 [65Nxx]

#### 算法 38.2 (谱方法)
**Algorithm 38.2 (Spectral Methods)**

**全局基函数**: 三角函数、Chebyshev多项式

**Galerkin谱方法**:
```
u_N(x) = Σ_{k=-N}^N û_k e^{ikx}
```
系数由投影决定

**配置谱方法** (拟谱):
在配置点满足方程

**精度**: 指数收敛(光滑解)

**应用**: 流体力学、天气预报

---

## 5. 计算复杂度 (68Qxx)

### 5.1 时间与空间复杂度 [68Qxx]

#### 定义 XXXIX.1.1 (渐近记号)
**Definition XXXIX.1.1 (Asymptotic Notation)**

**大O**: f(n) = O(g(n)) ⟺ ∃c,n₀: f(n) ≤ cg(n) (n ≥ n₀)

**Ω**: f(n) = Ω(g(n)) ⟺ ∃c,n₀: f(n) ≥ cg(n) (n ≥ n₀)

**Θ**: f(n) = Θ(g(n)) ⟺ f(n) = O(g(n)) = Ω(g(n))

**例子**:
- 矩阵乘法: O(n³) (朴素), O(n^{2.373}) (最优)
- 排序: O(n log n) (比较排序下界)
- FFT: O(n log n)

---

### 5.2 P vs NP [68Qxx]

#### 定义 XXXIX.2.1 (复杂度类)
**Definition XXXIX.2.1 (Complexity Classes)**

**P**: 多项式时间内可判定的问题类

**NP**: 非确定性多项式时间 (证书可在多项式时间验证)

**NP-完全**: NP中最难的问题
1. ∈ NP
2. 所有NP问题可多项式归约

**例子** (NP-完全):
- SAT (可满足性)
- 3-SAT
- 旅行商问题 (TSP)
- 背包问题
- 图着色

**P = NP?**: 千禧年问题之一，未解决

---

### 5.3 算法设计技术 [68Qxx]

#### 技术 39.1 (分治法)
**Technique 39.1 (Divide and Conquer)**

**模式**:
1. 分解为子问题
2. 递归求解
3. 合并解

**例子**:
- 归并排序: T(n) = 2T(n/2) + O(n) → O(n log n)
- 快速排序: 平均O(n log n)
- Strassen矩阵乘法: O(n^{2.807})

**主定理**: T(n) = aT(n/b) + f(n)
- f(n) = O(n^{log_b a - ε}) → T(n) = Θ(n^{log_b a})
- f(n) = Θ(n^{log_b a}) → T(n) = Θ(n^{log_b a} log n)
- f(n) = Ω(n^{log_b a + ε}) → T(n) = Θ(f(n))

---

## Lean4 代码示例

本节提供与第六卷（数值分析）内容相关的Lean4代码示例。

### 1. 数值线性代数

```lean4
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.LinearAlgebra.Matrix.Determinant

-- 矩阵乘法的复杂度
-- 朴素算法: O(n³)
-- Strassen算法: O(n^{log₂ 7}) ≈ O(n^{2.807})

-- LU分解
-- A = LU 其中L是下三角，U是上三角

example (n : Type*) [Fintype n] [DecidableEq n] (A : Matrix n n ℝ) 
    (hA : A.det ≠ 0) :
    ∃ (L U : Matrix n n ℝ), A = L * U ∧ 
    (∀ i j, i < j → L i j = 0) ∧  -- L下三角
    (∀ i j, i > j → U i j = 0) := by  -- U上三角
  sorry  -- LU分解存在性

-- QR分解
-- A = QR 其中Q是正交矩阵，R是上三角

example (n : Type*) [Fintype n] [DecidableEq n] (A : Matrix n n ℝ) 
    (hA : A.det ≠ 0) :
    ∃ (Q R : Matrix n n ℝ), A = Q * R ∧ 
    IsOrthogonal Q ∧ 
    (∀ i j, i > j → R i j = 0) := by
  sorry  -- QR分解存在性

-- 特征值计算 (幂迭代法)
def powerIteration (A : Matrix n n ℝ) (v : n → ℝ) (k : ℕ) : n → ℝ :=
  match k with
  | 0 => v
  | k + 1 => (A *ᵥ powerIteration A v k) / ‖A *ᵥ powerIteration A v k‖
```

### 2. 数值积分

```lean4
import Mathlib.Analysis.SpecialFunctions.Integrals

-- 梯形法则
def trapezoidalRule (f : ℝ → ℝ) (a b : ℝ) (n : ℕ) : ℝ :=
  let h := (b - a) / n
  let x := fun i => a + i * h
  (h / 2) * (f a + 2 * (∑ i ∈ Finset.range (n - 1), f (x i)) + f b)

-- Simpson法则
def simpsonRule (f : ℝ → ℝ) (a b : ℝ) (n : ℕ) : ℝ :=
  let h := (b - a) / (2 * n)
  let x := fun i => a + i * h
  (h / 3) * (f a + 4 * (∑ i ∈ Finset.range n, f (x (2 * i + 1))) + 
              2 * (∑ i ∈ Finset.range (n - 1), f (x (2 * i + 2))) + f b)

-- Gauss求积
-- 使用Legendre多项式的零点作为节点

-- Simpson法则的误差估计
example (f : ℝ → ℝ) (a b : ℝ) (n : ℕ) (hf : ContDiff ℝ 4 f) :
    |∫ x in a..b, f x - simpsonRule f a b n| ≤ 
    ((b - a)^5 / (180 * n^4)) * sup {x | x ∈ Set.Icc a b} |deriv^[4] f x| := by
  sorry  -- Simpson法则误差
```

### 3. 常微分方程数值方法

```lean4
import Mathlib.Analysis.ODE.Gronwall
import Mathlib.Analysis.ODE.PicardLindelof

-- 欧拉方法
def eulerMethod (f : ℝ → ℝ → ℝ) (y₀ : ℝ) (a b : ℝ) (n : ℕ) : Fin (n + 1) → ℝ
  | ⟨0, _⟩ => y₀
  | ⟨k + 1, hk⟩ => 
    let h := (b - a) / n
    let yk := eulerMethod f y₀ a b n ⟨k, Nat.lt_of_succ_lt hk⟩
    let tk := a + k * h
    yk + h * f tk yk

-- Runge-Kutta四阶方法 (RK4)
def rk4Method (f : ℝ → ℝ → ℝ) (y₀ : ℝ) (a b : ℝ) (n : ℕ) : Fin (n + 1) → ℝ
  | ⟨0, _⟩ => y₀
  | ⟨k + 1, hk⟩ => 
    let h := (b - a) / n
    let yk := rk4Method f y₀ a b n ⟨k, Nat.lt_of_succ_lt hk⟩
    let tk := a + k * h
    let k₁ := f tk yk
    let k₂ := f (tk + h/2) (yk + h/2 * k₁)
    let k₃ := f (tk + h/2) (yk + h/2 * k₂)
    let k₄ := f (tk + h) (yk + h * k₃)
    yk + h/6 * (k₁ + 2*k₂ + 2*k₃ + k₄)

-- 欧拉方法的收敛性
example (f : ℝ → ℝ → ℝ) (y₀ : ℝ) (a b : ℝ) 
    (hlip : ∃ L, ∀ t y₁ y₂, |f t y₁ - f t y₂| ≤ L * |y₁ - y₂|)
    (hcont : ∀ y, Continuous (fun t => f t y)) :
    ∃ C, ∀ n, ‖eulerMethod f y₀ a b n n - (ODESolution f y₀ a) b‖ ≤ C / n := by
  sorry  -- 欧拉方法收敛阶1
```

### 4. 偏微分方程数值方法

```lean4
import Mathlib.Analysis.PDE.HeatEquation

-- 有限差分法 (热传导方程)
-- u_t = α u_xx

-- 显式格式 (FTCS - Forward Time Central Space)
def heatExplicit (α : ℝ) (u₀ : ℝ → ℝ) (L T : ℝ) (nx nt : ℕ) : ℕ → ℕ → ℝ
  | 0, j => u₀ (j * L / nx)  -- 初值
  | n + 1, j => 
    let dx := L / nx
    let dt := T / nt
    let r := α * dt / dx^2
    let u_n := heatExplicit α u₀ L T nx nt n
    if j = 0 ∨ j = nx then 0  -- 边界条件
    else u_n j + r * (u_n (j - 1) - 2 * u_n j + u_n (j + 1))

-- CFL稳定性条件
example (α : ℝ) (L T : ℝ) (nx nt : ℕ) :
    α * (T / nt) / (L / nx)^2 ≤ 1/2 → 
    IsStable (heatExplicit α u₀ L T nx nt) := by
  sorry  -- 稳定性分析

-- 隐式格式 (Crank-Nicolson)
def crankNicolson (α : ℝ) (u₀ : ℝ → ℝ) (L T : ℝ) (nx nt : ℕ) : ℕ → ℕ → ℝ
  | 0, j => u₀ (j * L / nx)
  | n + 1, j => sorry  -- 需要求解线性系统
```

### 5. 插值与逼近

```lean4
import Mathlib.Data.Polynomial.Basic
import Mathlib.Analysis.SpecialFunctions.Polynomial.Laguerre

-- Lagrange插值
def lagrangeInterpolation (points : Fin n → ℝ × ℝ) : Polynomial ℝ :=
  ∑ i : Fin n, 
    let (xᵢ, yᵢ) := points i
    yᵢ • (Polynomial.interpolation (fun j => (points j).1) i)

-- 多项式插值的唯一性
example (points : Fin n → ℝ × ℝ) (p q : Polynomial ℝ)
    (hp : ∀ i, p.eval (points i).1 = (points i).2)
    (hq : ∀ i, q.eval (points i).1 = (points i).2)
    (hdeg_p : p.natDegree < n) (hdeg_q : q.natDegree < n) :
    p = q := by
  sorry  -- 插值多项式唯一

-- Taylor逼近
def taylorApprox (f : ℝ → ℝ) (a : ℝ) (n : ℕ) (hf : ContDiff ℝ n f) : Polynomial ℝ :=
  ∑ k ∈ Finset.range (n + 1), 
    (deriv^[k] f a / k.factorial) • Polynomial.X^k

-- Taylor余项 (Lagrange形式)
example (f : ℝ → ℝ) (a x : ℝ) (n : ℕ) (hf : ContDiff ℝ (n + 1) f) :
    ∃ ξ ∈ Set.Ioo (min a x) (max a x),
    f x - (taylorApprox f a n hf).eval (x - a) = 
    (deriv^[n + 1] f ξ / (n + 1).factorial) * (x - a)^(n + 1) := by
  sorry  -- Taylor余项
```

### 6. 优化算法

```lean4
import Mathlib.Analysis.Calculus.Gradient
import Mathlib.Analysis.Convex.Basic

-- 梯度下降
def gradientDescent (f : ℝ^n → ℝ) (grad_f : ℝ^n → ℝ^n) (x₀ : ℝ^n) 
    (α : ℝ) (k : ℕ) : ℝ^n :=
  match k with
  | 0 => x₀
  | k + 1 => gradientDescent f grad_f x₀ α k - α • grad_f (gradientDescent f grad_f x₀ α k)

-- 牛顿法
def newtonMethod (f : ℝ → ℝ) (f' f'' : ℝ → ℝ) (x₀ : ℝ) (k : ℕ) : ℝ :=
  match k with
  | 0 => x₀
  | k + 1 => 
    let xk := newtonMethod f f' f'' x₀ k
    xk - f' xk / f'' xk

-- 牛顿法的二次收敛
example (f : ℝ → ℝ) (f' f'' : ℝ → ℝ) (x* : ℝ) 
    (hroot : f' x* = 0) (hconvex : f'' x* > 0)
    (hlip : ∃ L, ∀ x, |f'' x - f'' x*| ≤ L * |x - x*|) :
    ∃ C, ∀ k, |newtonMethod f f' f'' x₀ k - x*| ≤ C * |newtonMethod f f' f'' x₀ (k - 1) - x*|^2 := by
  sorry  -- 二次收敛

-- 最速下降的收敛性
example (f : ℝ^n → ℝ) (hf : ConvexOn ℝ (Set.univ : Set (ℝ^n)) f) 
    (hgrad : LipschitzWith L (gradient f)) :
    ∃ C, ∀ k, f (gradientDescent f (gradient f) x₀ (1/L) k) - f x* ≤ 
    (1 - μ/L)^k * (f x₀ - f x*) := by
  sorry  -- 强凸情况下的线性收敛
```

### 7. 计算复杂度

```lean4
import Mathlib.Computability.Primrec
import Mathlib.Computability.TuringMachine

-- 时间复杂度的定义
def TimeComplexity (f : ℕ → ℕ) (problem : ℕ → Bool) : Prop :=
  ∃ (M : TuringMachine) (c : ℕ), 
    ∀ n, Steps (M, problem, n) ≤ c * f n

-- P类问题
def P (problem : ℕ → Bool) : Prop :=
  ∃ (p : Polynomial), TimeComplexity (fun n => p.eval n) problem

-- NP类问题
def NP (problem : ℕ → Bool) : Prop :=
  ∃ (verifier : ℕ → ℕ → Bool) (p : Polynomial),
    (∀ x, problem x ↔ ∃ c, verifier x c) ∧
    (∀ x c, Steps (verifier x c) ≤ p.eval (|x| + |c|))

-- 矩阵乘法的复杂度
example : TimeComplexity (fun n => n^3) MatrixMultiplication := by
  sorry  -- 朴素算法

-- Strassen算法
example : TimeComplexity (fun n => n^(7/3 : ℝ)) MatrixMultiplication := by
  sorry  -- Strassen算法
```

### 8. 数值稳定性

```lean4
import Mathlib.Analysis.SpecialFunctions.Pow.Real

-- 浮点误差
-- 机器精度 ε_mach

-- 舍入误差的累积
example (n : ℕ) (x : Fin n → ℝ) :
    |fl (∑ i, x i) - ∑ i, x i| ≤ n * ε_mach * ∑ i, |x i| := by
  sorry  -- 舍入误差上界

-- 条件数
def conditionNumber (A : Matrix n n ℝ) : ℝ := ‖A‖ * ‖A⁻¹‖

-- 条件数与误差放大
example (A : Matrix n n ℝ) (b x : n → ℝ) (hAx : A *ᵥ x = b) 
    (Δb : n → ℝ) (Δx : n → ℝ) (hAΔx : A *ᵥ (x + Δx) = b + Δb) :
    ‖Δx‖ / ‖x‖ ≤ conditionNumber A * (‖Δb‖ / ‖b‖) := by
  sorry  -- 条件数与相对误差

-- 良态矩阵
example (A : Matrix n n ℝ) (hcond : conditionNumber A ≈ 1) :
    ∀ b Δb, ‖Δx‖ / ‖x‖ ≤ ‖Δb‖ / ‖b‖ := by
  sorry  -- 良态矩阵误差不放大
```

---

## 参考文献

### 数值线性代数
1. Golub, G.H., Van Loan, C.F., *Matrix Computations*, 4th ed., Johns Hopkins, 2013
2. Trefethen, L.N., Bau, D., *Numerical Linear Algebra*, SIAM, 1997
3. Demmel, J.W., *Applied Numerical Linear Algebra*, SIAM, 1997

### 数值分析
4. Burden, R.L., Faires, J.D., *Numerical Analysis*, 10th ed., Cengage, 2015
5. Stoer, J., Bulirsch, R., *Introduction to Numerical Analysis*, 3rd ed., Springer, 2002
6. Higham, N.J., *Accuracy and Stability of Numerical Algorithms*, 2nd ed., SIAM, 2002

### 微分方程数值解
7. Butcher, J.C., *Numerical Methods for Ordinary Differential Equations*, 3rd ed., Wiley, 2016
8. LeVeque, R.J., *Finite Difference Methods for Ordinary and Partial Differential Equations*, SIAM, 2007
9. Brenner, S.C., Scott, L.R., *The Mathematical Theory of Finite Element Methods*, 3rd ed., Springer, 2008

### 计算复杂度
10. Arora, S., Barak, B., *Computational Complexity: A Modern Approach*, Cambridge, 2009
11. Sipser, M., *Introduction to the Theory of Computation*, 3rd ed., Cengage, 2012
12. Cormen, T.H., et al., *Introduction to Algorithms*, 3rd ed., MIT Press, 2009

### 综合参考
13. Press, W.H., et al., *Numerical Recipes: The Art of Scientific Computing*, 3rd ed., Cambridge, 2007
14. Quarteroni, A., Sacco, R., Saleri, F., *Numerical Mathematics*, 2nd ed., Springer, 2007

---

**注**: 本文档是第六卷，涵盖了数值分析与计算数学的核心内容。

---

*本卷完成日期: 2025-03-26*  
*下一卷预告: 数学物理*
