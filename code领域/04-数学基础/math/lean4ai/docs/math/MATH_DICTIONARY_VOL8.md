# 数学知识词典 - 第八卷：应用数学
## Volume VIII: Applied Mathematics

**MSC分类**: 90-XX, 91-XX, 92-XX, 93-XX, 94-XX  
**版本**: 1.0  
**日期**: 2025-03-26

---

## 目录

1. [运筹学 (90-XX)](#1-运筹学)
2. [博弈论 (91-XX)](#2-博弈论)
3. [生物数学 (92-XX)](#3-生物数学)
4. [控制论 (93-XX)](#4-控制论)
5. [信息论 (94-XX)](#5-信息论)

---

## 1. 运筹学 (90-XX)

### 1.1 线性规划 [90Cxx]

#### 问题 XLIV.1.1 (线性规划)
**Problem XLIV.1.1 (Linear Programming)**

**标准形式**:
```
minimize c^T x
subject to: Ax = b, x ≥ 0
```

**几何**: 在可行域(多面体)的顶点处达到最优

**例子** (食谱问题、运输问题)

#### 定理 44.1 (对偶定理)
**Theorem 44.1 (Duality Theorem)**

**原问题**:
```
min c^T x  s.t.  Ax = b, x ≥ 0
```

**对偶问题**:
```
max b^T y  s.t.  A^T y ≤ c
```

**强对偶**: 若原问题有最优解，则对偶也有最优解且最优值相等。

**互补松弛**: x_j > 0 ⟹ (A^T y)_j = c_j

---

### 1.2 单纯形法 [90Cxx]

#### 算法 44.1 (单纯形法)
**Algorithm 44.1 (Simplex Method)**

**思想**: 沿可行域顶点移动

**算法**:
1. 找初始基本可行解
2. 选择进入变量(负检验数)
3. 选择离开变量(最小比值)
4. 旋转
5. 重复直到最优

**复杂度**:
- 平均: O(mn) (m约束，n变量)
- 最坏: 指数 (Klee-Minty例子)

**改进**: 修正单纯形法(矩阵更新)

---

### 1.3 整数规划 [90Cxx]

#### 定义 XLIV.1.2 (整数规划)
**Definition XLIV.1.2 (Integer Programming)**

**问题**: 线性规划 + x ∈ ℤ^n

**NP-难**: 一般情况NP-完全

**特殊可解**: 
- 全么模整数规划 (在格点上)
- 网络流问题 (网络单纯形)

**方法**:
1. 分支定界 (Branch and Bound)
2. 割平面 (Cutting Planes)
3. 启发式 (Heuristics)

---

### 1.4 图论与网络流 [90Bxx]

#### 定义 XLIV.1.3 (最大流问题)
**Definition XLIV.1.3 (Maximum Flow Problem)**

**网络**: G = (V, E), s源, t汇, 容量c

**流**: f: E → ℝ⁺
- 容量约束: 0 ≤ f(e) ≤ c(e)
- 守恒: 除s,t外，Σf(in,v) = Σf(out,v)

**最大流**: max f的总流出

#### 定理 44.2 (最大流最小割定理)
**Theorem 44.2 (Max-Flow Min-Cut Theorem)**

```
max flow = min cut capacity
```

**割**: 分离s和t的边集

**Ford-Fulkerson算法**: 增广路径

**复杂度**: O(E·max_flow) (基本) → O(VE²) (Dinic)

---

## 2. 博弈论 (91-XX)

### 2.1 正规形式博弈 [91Axx]

#### 定义 XLV.1.1 (博弈)
**Definition XLV.1.1 (Games)**

**正规形式博弈**: G = (N, {S_i}, {u_i})
- N: 玩家集合
- S_i: 玩家i的策略集
- u_i: 玩家i的效用函数

**例子** (囚徒困境):
```
         坦白    沉默
坦白   (-5,-5)  (0,-10)
沉默  (-10,0)  (-1,-1)
```

#### 定义 XLV.1.2 (Nash均衡)
**Definition XLV.1.2 (Nash Equilibrium)**

**Nash均衡**: 策略组合s* = (s*_1,...,s*_n)使得对每个i:
```
u_i(s*_i, s*_{-i}) ≥ u_i(s_i, s*_{-i})  ∀s_i ∈ S_i
```

(无人能通过单方面改变策略获益)

**例子**: 囚徒困境中(坦白,坦白)是Nash均衡

#### 定理 45.1 (Nash存在定理)
**Theorem 45.1 (Nash Existence Theorem)**

有限博弈(有限玩家、有限策略)至少有一个Nash均衡(可能混合策略)。

*证明*. Kakutani不动点定理。 □

---

### 2.2 零和博弈 [91Axx]

#### 定义 XLV.2.1 (零和博弈)
**Definition XLV.2.1 (Zero-Sum Games)**

**零和**: u₁ + u₂ = 0 (双人)

**极小极大定理** (von Neumann):
```
max_{p∈P} min_{q∈Q} u₁(p,q) = min_{q∈Q} max_{p∈P} u₁(p,q)
```

**意义**: 混合策略下有鞍点

**算法**: 线性规划求解

---

### 2.3 演化博弈 [91Axx]

#### 定义 XLV.3.1 (演化稳定策略)
**Definition XLV.3.1 (Evolutionary Stable Strategy)**

**演化稳定策略** (ESS): 策略p是ESS如果对所有q ≠ p:
```
u(p,p) ≥ u(q,p)
若u(p,p) = u(q,p)，则u(p,q) > u(q,q)
```

**意义**: 群体中p不能被小群体q侵入

**复制子动态**:
```
ẋ_i = x_i(u_i - ū)
```
ū是平均适应度

---

## 3. 生物数学 (92-XX)

### 3.1 种群动力学 [92Dxx]

#### 模型 46.1 (Malthus模型)
**Model 46.1 (Malthus Model)**

**方程**: dN/dt = rN

**解**: N(t) = N₀e^{rt}
- r > 0: 指数增长
- r < 0: 指数衰减

**局限**: 无环境容量限制

#### 模型 46.2 (Logistic模型)
**Model 46.2 (Logistic Model)**

**方程**: dN/dt = rN(1 - N/K)

**解**: N(t) = K / [1 + ((K-N₀)/N₀)e^{-rt}]

**性质**:
- K是环境容量
- N → K 当 t → ∞
- S形曲线

#### 模型 46.3 (Lotka-Volterra模型)
**Model 46.3 (Lotka-Volterra Model)**

**捕食者-猎物**:
```
dx/dt = αx - βxy  (猎物)
dy/dt = δxy - γy  (捕食者)
```

**性质**:
- 周期解(极限环)
- 守恒量(首次积分)
- 相位移动

---

### 3.2 传染病模型 [92Dxx]

#### 模型 46.4 (SIR模型)
**Model 46.4 (SIR Model)**

**状态**: S(易感), I(感染), R(康复)

**方程**:
```
dS/dt = -βSI
dI/dt = βSI - γI
dR/dt = γI
```

**基本再生数**: R₀ = βS₀/γ
- R₀ > 1: 流行
- R₀ < 1: 消亡

**群体免疫阈值**: 1 - 1/R₀

---

### 3.3 神经元模型 [92Cxx]

#### 模型 46.5 (Hodgkin-Huxley模型)
**Model 46.5 (Hodgkin-Huxley Model)**

**方程**:
```
C dV/dt = -g_Na m³h(V - V_Na) - g_K n⁴(V - V_K) - g_L(V - V_L) + I_ext
dm/dt = α_m(V)(1-m) - β_m(V)m
dh/dt = α_h(V)(1-h) - β_h(V)h
dn/dt = α_n(V)(1-n) - β_n(V)n
```

**意义**: 动作电位的离子机制(诺贝尔奖1963)

**简化** (FitzHugh-Nagumo):
```
dv/dt = v - v³/3 - w + I
dw/dt = ε(v + a - bw)
```

---

## 4. 控制论 (93-XX)

### 4.1 系统建模 [93Axx]

#### 定义 XLVII.1.1 (状态空间)
**Definition XLVII.1.1 (State Space)**

**状态方程**:
```
ẋ = Ax + Bu  (状态)
y = Cx + Du  (输出)
```
- x: n维状态向量
- u: m维输入
- y: p维输出

**例子**: 
- 质量-弹簧-阻尼: ẍ + (c/m)ẋ + (k/m)x = (1/m)u

---

### 4.2 可控性与可观测性 [93Bxx]

#### 定义 XLVII.2.1 (可控性)
**Definition XLVII.2.1 (Controllability)**

**可控**: 可从任意初态到任意终态

**判据**: 可控性矩阵满秩
```
rank[C] = n, C = [B, AB, A²B, ..., A^{n-1}B]
```

**对偶**: 可观测性
```
rank[O] = n, O = [C', A'C', ..., (A')^{n-1}C']
```

---

### 4.3 稳定性 [93Dxx]

#### 定义 XLVII.3.1 (Lyapunov稳定)
**Definition XLVII.3.1 (Lyapunov Stability)**

**稳定**: 初值小扰动 ⟹ 解保持小

**渐近稳定**: 稳定 + x(t) → 0

**Lyapunov函数**: V(x) > 0 (x≠0), V(0) = 0, V̇ ≤ 0

**定理**: 存在Lyapunov函数 ⟹ 渐近稳定

**线性系统**: 渐近稳定 ⟺ A的特征值实部< 0

---

### 4.4 最优控制 [93Exx]

#### 问题 47.1 (线性二次调节器)
**Problem 47.1 (Linear Quadratic Regulator)**

**目标**: min ∫ (x^T Qx + u^T Ru) dt

**解** (Riccati方程):
```
u* = -R^{-1}B^T P x
-A^T P - PA + PBR^{-1}B^T P = Q
```

**应用**: 航天器控制、机器人

---

## 5. 信息论 (94-XX)

### 5.1 熵 [94Axx]

#### 定义 XLVIII.1.1 (Shannon熵)
**Definition XLVIII.1.1 (Shannon Entropy)**

**熵** (离散):
```
H(X) = -Σ p(x) log₂ p(x)
```

**性质**:
1. H(X) ≥ 0
2. H(X) ≤ log |X| (等号: 均匀分布)
3. H(X,Y) ≤ H(X) + H(Y) (次可加性)

**例子**:
- 公平硬币: H = 1 bit
- 公平骰子: H = log₂ 6 ≈ 2.58 bits

#### 定义 XLVIII.1.2 (微分熵)
**Definition XLVIII.1.2 (Differential Entropy)**

**连续**: h(X) = -∫ f(x) log f(x) dx

**例子**:
- Uniform(a,b): h = log(b-a)
- N(μ, σ²): h = (1/2)log(2πeσ²)

---

### 5.2 互信息 [94Axx]

#### 定义 XLVIII.2.1 (互信息)
**Definition XLVIII.2.1 (Mutual Information)**

```
I(X;Y) = H(X) - H(X|Y) = H(Y) - H(Y|X)
       = Σ p(x,y) log [p(x,y)/(p(x)p(y))]
```

**性质**:
1. I(X;Y) ≥ 0
2. I(X;Y) = 0 ⟺ X,Y独立
3. I(X;Y) = I(Y;X)

**意义**: Y提供关于X的信息量

---

### 5.3 信道容量 [94Axx]

#### 定义 XLVIII.3.1 (信道容量)
**Definition XLVIII.3.1 (Channel Capacity)**

**信道**: p(y|x)

**容量**: C = max_{p(x)} I(X;Y)

**例子**:
- **二元对称信道** (BSC, 误差p): C = 1 - H₂(p)
- **高斯信道** (功率P, 噪声N): C = (1/2)log(1 + P/N)

#### 定理 48.1 (信道编码定理)
**Theorem 48.1 (Channel Coding Theorem)**

**可达性**: R < C ⟹ 存在码率R的可靠编码

**逆定理**: R > C ⟹ 不可能可靠传输

**意义**: C是可靠通信的极限速率

---

### 5.4 信源编码 [94Axx]

#### 定理 48.2 (信源编码定理)
**Theorem 48.2 (Source Coding Theorem)**

**无损压缩**: 熵是平均码长的下界

**熵的渐近等分性** (AEP):
```
(1/n)log p(X₁,...,X_n) → -H(X)  a.s.
```

**典型集**: 约2^{nH}个序列占概率≈1

**Huffman编码**: 最优前缀码

**Lempel-Ziv**: 通用编码(无需知道分布)

---

### 5.5 率失真理论 [94Axx]

#### 定义 XLVIII.4.1 (率失真函数)
**Definition XLVIII.4.1 (Rate-Distortion Function)**

**失真**: d(x, x̂)

**率失真函数**:
```
R(D) = min_{p(x̂|x): E[d]≤D} I(X;X̂)
```

**意义**: 失真≤D所需的最小码率

**例子**:
- 高斯信源(方差σ²): R(D) = (1/2)log(σ²/D)
- 二元信源(误差p): R(D) = H(p) - H(D)

---

## 参考文献

### 运筹学
1. Hillier, F.S., Lieberman, G.J., *Introduction to Operations Research*, 10th ed., McGraw-Hill, 2014
2. Bertsimas, D., Tsitsiklis, J.N., *Introduction to Linear Optimization*, Athena Scientific, 1997
3. Nemhauser, G.L., Wolsey, L.A., *Integer and Combinatorial Optimization*, Wiley, 1988

### 博弈论
4. Osborne, M.J., Rubinstein, A., *A Course in Game Theory*, MIT Press, 1994
5. Fudenberg, D., Tirole, J., *Game Theory*, MIT Press, 1991
6. Myerson, R.B., *Game Theory: Analysis of Conflict*, Harvard, 1991

### 生物数学
7. Edelstein-Keshet, L., *Mathematical Models in Biology*, SIAM, 2005
8. Murray, J.D., *Mathematical Biology*, Vol. 1-2, 3rd ed., Springer, 2002
9. Keener, J., Sneyd, J., *Mathematical Physiology*, 2nd ed., Springer, 2009

### 控制论
10. Åström, K.J., Murray, R.M., *Feedback Systems*, 2nd ed., Princeton, 2019
11. Zhou, K., Doyle, J.C., Glover, K., *Robust and Optimal Control*, Prentice Hall, 1996
12. Anderson, B.D.O., Moore, J.B., *Optimal Control*, Prentice Hall, 1990

### 信息论
13. Cover, T.M., Thomas, J.A., *Elements of Information Theory*, 2nd ed., Wiley, 2006
14. MacKay, D.J.C., *Information Theory, Inference, and Learning Algorithms*, Cambridge, 2003
15. Gallager, R.G., *Information Theory and Reliable Communication*, Wiley, 1968

---

**注**: 本文档是第八卷(最后一卷)，涵盖了应用数学的核心领域。

---

*本卷完成日期: 2025-03-26*

---

## Lean4 代码示例

本节提供与第八卷（应用数学）内容相关的Lean4代码示例。

### 1. 运筹学 - 线性规划

```lean4
import Mathlib.Data.Real.Basic
import Mathlib.Data.Matrix.Basic

-- 线性规划问题
-- min c^T x s.t. Ax = b, x ≥ 0

-- 单纯形法
def simplexMethod (A : Matrix (Fin m) (Fin n) ℝ) (b : Fin m → ℝ) (c : Fin n → ℝ) : Fin n → ℝ :=
  sorry  -- 单纯形算法实现

-- 对偶问题
-- max b^T y s.t. A^T y ≤ c

def dualLinearProgram (A : Matrix (Fin m) (Fin n) ℝ) (b : Fin m → ℝ) (c : Fin n → ℝ) : Fin m → ℝ :=
  sorry  -- 对偶线性规划

-- 强对偶定理
example (A : Matrix (Fin m) (Fin n) ℝ) (b : Fin m → ℝ) (c : Fin n → ℝ) :
    (primal A b c).val = (dual A b c).val := by
  sorry  -- 强对偶性
```

### 2. 博弈论

```lean4
-- Nash均衡
-- 每个玩家策略是对其他玩家策略的最佳响应

def nashEquilibrium (payoffs : Player → Strategy → Player → Strategy → ℝ) : Prop :=
  ∀ i sᵢ, payoff i sᵢ ≥ payoff i (bestResponse i (s₋ᵢ)) (s₋ᵢ)

-- 囚徒困境
def prisonersDilemma : Bool → Bool → ℝ × ℝ
  | false, false => (3, 3)   -- 都合作
  | false, true => (0, 5)    -- p1合作, p2背叛
  | true, false => (5, 0)    -- p1背叛, p2合作
  | true, true => (1, 1)    -- 都背叛

-- 唯一Nash均衡: (背叛, 背叛)
example : nashEquilibrium prisonersDilemma true true := by
  sorry

-- 混合策略Nash均衡
def mixedNashEquilibrium : Fin 2 → ℝ → Prop :=
  ∀ s, nashEquilibrium (mixedPayoff s)
```

### 3. 信息论

```lean4
import Mathlib.Probability.Notation

-- 熵
def entropy (p : Fin n → ℝ) (hpos : ∀ i, p i > 0) (hsum : ∑ i, p i = 1) : ℝ :=
  -∑ i, p i * Real.log p i / Real.log 2

-- 熵非负性
example (p : Fin n → ℝ) (hpos : ∀ i, p i > 0) (hsum : ∑ i, p i = 1) :
    entropy p hpos hsum ≥ 0 := by
  sorry  -- Jensen不等式

-- 互信息
def mutualInformation (X Y : Type*) : ℝ :=
  entropy X + entropy Y - jointEntropy X Y

-- 信道容量
def channelCapacity (p : Fin m → Fin n → ℝ) : ℝ :=
  sSup (fun x => mutualInformation X (channelOutput p x))
```

**🎉 全部8卷创建完成！ 🎉**
