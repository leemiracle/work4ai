# 数学知识词典 - 第一卷：基础与代数（第一部分）
## Volume I: Foundations and Algebra (Part 1)

**MSC分类**: 03-XX, 05-XX, 06-XX, 11-XX  
**版本**: 1.0  
**日期**: 2025-03-26

---

## 目录

1. [数理逻辑与基础 (03-XX)](#1-数理逻辑与基础)
2. [组合数学 (05-XX)](#2-组合数学)
3. [序、格与有序代数结构 (06-XX)](#3-序格与有序代数结构)
4. [数论 (11-XX)](#4-数论)

---

## 1. 数理逻辑与基础 (03-XX)

### 1.1 命题逻辑 (Propositional Logic) [03B05]

#### 定义 I.1.1 (命题与命题联结词)
**Definition I.1.1 (Propositions and Propositional Connectives)**

一个**命题** (proposition) 是一个可判断真值的陈述。

**基本联结词** (logical connectives):
- 否定 (negation): ¬p
- 合取 (conjunction): p ∧ q (p且q)
- 析取 (disjunction): p ∨ q (p或q)
- 蕴含 (implication): p → q (如果p则q)
- 等价 (equivalence): p ↔ q (p当且仅当q)

**真值表** (Truth tables):

| p | q | ¬p | p∧q | p∨q | p→q | p↔q |
|---|---|----|----|-----|-----|-----|
| T | T | F  | T  | T   | T   | T   |
| T | F | F  | F  | T   | F   | F   |
| F | T | T  | F  | T   | T   | F   |
| F | F | T  | F  | F   | T   | T   |

#### 定义 I.1.2 (永真式与矛盾式)
**Definition I.1.2 (Tautology and Contradiction)**

- **永真式** (tautology): 对所有赋值都为真的公式
- **矛盾式** (contradiction): 对所有赋值都为假的公式
- **可满足式** (satisfiable): 至少有一个赋值使其为真的公式

**例子**:
- 永真式: p ∨ ¬p (排中律)
- 矛盾式: p ∧ ¬p
- 可满足式: p → q

#### 定理 1.1 (完备性定理)
**Theorem 1.1 (Completeness Theorem for Propositional Logic)**

在命题逻辑中，一个公式是永真的当且仅当它是可证明的。

*证明*. 见Enderton, H.B., *A Mathematical Introduction to Logic*, 2nd ed., Academic Press, 2001. □

**历史注记**: 
- Gödel (1930) 首次证明了完备性定理
- 这是数理逻辑基础性结果之一

#### 定义 I.1.3 (范式)
**Definition I.1.3 (Normal Forms)**

- **析取范式** (Disjunctive Normal Form, DNF): 形如 ∨ᵢ(∧ⱼlᵢⱼ)，其中lᵢⱼ是原子或原子的否定
- **合取范式** (Conjunctive Normal Form, CNF): 形如 ∧ᵢ(∨ⱼlᵢⱼ)

**定理 1.2** 每个命题公式都有等价的DNF和CNF。

---

### 1.2 一阶逻辑 (First-Order Logic) [03C07]

#### 定义 I.2.1 (一阶语言)
**Definition I.2.1 (First-Order Language)**

一个**一阶语言** ℒ 由以下组成:
1. **逻辑符号** (logical symbols):
   - 变量: x, y, z, ...
   - 联结词: ¬, ∧, ∨, →, ↔
   - 量词: ∀ (全称), ∃ (存在)
   - 等词: =
2. **非逻辑符号** (non-logical symbols):
   - 常量符号: c, d, ...
   - 函数符号: f, g, ... (带元数)
   - 关系符号: R, S, ... (带元数)

#### 定义 I.2.2 (项与公式)
**Definition I.2.2 (Terms and Formulas)**

**项** (terms) 递归定义:
1. 变量和常量是项
2. 若t₁,...,tₙ是项，f是n元函数符号，则f(t₁,...,tₙ)是项

**公式** (formulas) 递归定义:
1. 若t₁,t₂是项，则t₁=t₂是公式(原子公式)
2. 若t₁,...,tₙ是项，R是n元关系符号，则R(t₁,...,tₙ)是公式(原子公式)
3. 若φ,ψ是公式，则¬φ, φ∧ψ, φ∨ψ, φ→ψ, φ↔ψ是公式
4. 若φ是公式，x是变量，则∀xφ, ∃xφ是公式

#### 定义 I.2.3 (自由变量与约束变量)
**Definition I.2.3 (Free and Bound Variables)**

在公式∀xφ中，x的出现称为**约束的** (bound)。不约束的出现称为**自由的** (free)。

**句子** (sentence): 没有自由变量的公式

**记号**: φ(x₁,...,xₙ) 表示φ的自由变量在{x₁,...,xₙ}中

#### 定义 I.2.4 (结构)
**Definition I.2.4 (Structure/Model)**

语言ℒ的一个**结构** 𝔐 = (M, ·) 由以下组成:
- **论域** (universe) M: 非空集合
- 解释函数 ·: 
  - 常量c解释为c^M ∈ M
  - n元函数f解释为f^M: Mⁿ → M
  - n元关系R解释为R^M ⊆ Mⁿ

#### 定义 I.2.5 (可满足性与有效性)
**Definition I.2.5 (Satisfaction and Validity)**

给定结构𝔐和赋值s: Var → M，定义𝔐 ⊨ φ[s]（𝔐在s下满足φ）的递归规则:

1. 𝔐 ⊨ t₁=t₂[s] ⟺ s(t₁) = s(t₂)
2. 𝔐 ⊨ R(t₁,...,tₙ)[s] ⟺ (s(t₁),...,s(tₙ)) ∈ R^M
3. 𝔐 ⊨ ¬φ[s] ⟺ 𝔐 ⊭ φ[s]
4. 𝔐 ⊨ φ∧ψ[s] ⟺ 𝔐 ⊨ φ[s] 且 𝔐 ⊨ ψ[s]
5. 𝔐 ⊨ ∀xφ[s] ⟺ 对所有a ∈ M, 𝔐 ⊨ φ[s(x|a)]

其中s(x|a)是将x映射到a，其他变量保持不变的赋值。

**有效性** (validity): 句子σ是有效的 ⟺ 对所有结构𝔐, 𝔐 ⊨ σ

**可满足性** (satisfiability): 句子σ是可满足的 ⟺ 存在结构𝔐使得𝔐 ⊨ σ

#### 定理 1.3 (Gödel完备性定理)
**Theorem 1.3 (Gödel's Completeness Theorem)**

对于一阶逻辑，一个句子是有效的当且仅当它是可证明的。

*证明思路*:
1. Henkin构造：扩展语言和理论
2. 最大化一致集
3. 从最大化一致集构造模型
4. 证明完备性

详见Enderton (2001), Chapter 2. □

**历史注记**:
- Kurt Gödel, 1930年在博士论文中首次证明
- 这是20世纪逻辑学最重要的结果之一

#### 定理 1.4 (紧致性定理)
**Theorem 1.4 (Compactness Theorem)**

句子集Γ是可满足的当且仅当它的每个有限子集都是可满足的。

*证明*. 完备性定理的直接推论. □

**应用**:
- 非标准分析的基础
- 证明模型的存在性
- 代数中的饱和模型

#### 定理 1.5 (Löwenheim-Skolem定理)
**Theorem 1.5 (Löwenheim-Skolem Theorem)**

**下行** (Downward): 若可数语言的理论T有模型，则T有可数模型。

**上行** (Upward): 若T有任意大的有限模型，则T有无穷模型。

*推论*: (Skolem悖论) 若ZFC有模型，则它有可数模型，即使ZFC能证明存在不可数集合。

**哲学意义**: 揭示了语法与语义之间的本质区别。

---

### 1.3 模型论基础 [03Cxx]

#### 定义 I.3.1 (初等等价)
**Definition I.3.1 (Elementary Equivalence)**

两个结构𝔐和𝔑**初等等价** (elementarily equivalent)，记作𝔐 ≡ 𝔑，如果它们满足相同的句子。

**例**:
- (ℚ, <) ≡ (ℝ, <) (都是稠密线性序无端点)
- (ℤ, +) ≢ (ℚ, +)

#### 定义 I.3.2 (初等子结构)
**Definition I.3.2 (Elementary Substructure)**

𝔐是𝔑的**初等子结构** (elementary substructure)，记作𝔐 ≺ 𝔑，如果:
1. 𝔐是𝔑的子结构
2. 对所有公式φ(x₁,...,xₙ)和所有a₁,...,aₙ ∈ M:
   𝔐 ⊨ φ[a₁,...,aₙ] ⟺ 𝔑 ⊨ φ[a₁,...,aₙ]

#### 定理 1.6 (Tarski-Vaught测试)
**Theorem 1.6 (Tarski-Vaught Test)**

𝔐是𝔑的初等子结构当且仅当对每个公式∃y φ(x₁,...,xₙ,y)和所有a₁,...,aₙ ∈ M:
若𝔑 ⊨ ∃y φ[a₁,...,aₙ]，则存在b ∈ M使得𝔑 ⊨ φ[a₁,...,aₙ,b]

*证明*. 见Marker, D., *Model Theory: An Introduction*, Springer, 2002. □

#### 定义 I.3.3 (类型)
**Definition I.3.3 (Types)**

设T是理论，A ⊆ M。**类型** (type) p(x)是一组公式{φᵢ(x,ā) : i ∈ I}使得T ∪ {φᵢ(x,ā)}是可满足的。

**完全类型**: 对于每个公式φ(x,ā)，要么φ ∈ p要么¬φ ∈ p

**实现**: 元素a实现类型p ⟺ 对所有φ ∈ p, 𝔐 ⊨ φ[a]

#### 定理 1.7 (省略定理)
**Theorem 1.7 (Omitting Types Theorem)**

设T是可数语言中的可数一致理论，p(x)是非孤立的完全类型。则T有模型省略p。

*证明*. 见Marker (2002). □

---

### 1.4 集合论 [03Exx]

#### 定义 I.4.1 (ZFC公理系统)
**Definition I.4.1 (ZFC Axiom System)**

**Zermelo-Fraenkel集合论带选择公理** (ZFC):

1. **外延公理** (Extensionality): ∀A∀B(∀x(x∈A↔x∈B)→A=B)
2. **配对公理** (Pairing): ∀x∀y∃z∀w(w∈z↔w=x∨w=y)
3. **分离公理** (Separation): ∀A∃B∀x(x∈B↔x∈A∧φ(x))
4. **并集公理** (Union): ∀F∃A∀Y∀x(x∈A↔∃Y∈F(x∈Y))
5. **幂集公理** (Power Set): ∀X∃Y∀z(z∈Y↔z⊆X)
6. **无穷公理** (Infinity): ∃I(∅∈I∧∀x(x∈I→x∪{x}∈I))
7. **替换公理** (Replacement): ∀A(∀x∈A∃!yφ(x,y)→∃B∀x∈A∃y∈Bφ(x,y))
8. **正则公理** (Regularity): ∀S(S≠∅→∃x∈S(x∩S=∅))
9. **选择公理** (Choice): ∀X(∅∉X→∃f:X→∪X, ∀A∈X(f(A)∈A))

#### 定义 I.4.2 (序数)
**Definition I.4.2 (Ordinals)**

集合α是**序数** (ordinal) 如果:
1. ∈是α上的传递关系
2. ∈在α上是良基的

**记号**: Ord表示所有序数的类

**性质**:
- 序数是传递集: x∈y∈α → x∈α
- 序数由∈良序
- 每个良序集同构于唯一序数

**例子**: 0 = ∅, 1 = {0}, 2 = {0,1}, ..., ω = {0,1,2,...}

#### 定义 I.4.3 (基数)
**Definition I.4.3 (Cardinals)**

**基数** (cardinal) 是不与任何较小序数双射的序数。

**记号**: 
- |X|表示集合X的基数
- ℵ₀ = ω (可数无穷)
- ℵ₁, ℵ₂, ... (后继基数)
- ℶ₀ = ℵ₀, ℶ_{α+1} = 2^{ℶ_α}

#### 定理 1.8 (Cantor定理)
**Theorem 1.8 (Cantor's Theorem)**

对任何集合X，|X| < |P(X)|。

*证明*. 对角论证法:
- 设f: X → P(X)，定义D = {x∈X : x∉f(x)}
- 则D ≠ f(y)对任何y∈X (否则y∈D ↔ y∉f(y) = D，矛盾)
- 因此f不是满射 □

#### 定理 1.9 (Schröder-Bernstein定理)
**Theorem 1.9 (Schröder-Bernstein Theorem)**

若|A| ≤ |B|且|B| ≤ |A|，则|A| = |B|。

*证明*. 见Kunen, K., *Set Theory*, College Publications, 2011. □

#### 定理 1.10 (选择公理的等价形式)
**Theorem 1.10 (Equivalents of AC)**

以下命题等价:
1. 选择公理 (AC)
2. **良序定理** (Zermelo): 每个集合可良序化
3. **Zorn引理**: 每个链有上界的偏序集有极大元
4. **Tukey引理**: 每个有限特征的族有极大元

*证明*. 见Kunen (2011). □

#### 定义 I.4.4 (连续统假设)
**Definition I.4.4 (Continuum Hypothesis)**

**连续统假设** (CH): 2^{ℵ₀} = ℵ₁

**广义连续统假设** (GCH): 对所有序数α, 2^{ℵ_α} = ℵ_{α+1}

#### 定理 1.11 (Gödel和Cohen的独立性定理)
**Theorem 1.11 (Independence Results)**

1. **Gödel (1940)**: 如果ZF一致，则ZFC + GCH一致
2. **Cohen (1963)**: 如果ZF一致，则ZFC + ¬CH一致

**意义**: CH在ZFC中不可判定。

---

### 1.5 可计算性理论 [03Dxx]

#### 定义 I.5.1 (图灵机)
**Definition I.5.1 (Turing Machine)**

**图灵机** M = (Q, Σ, Γ, δ, q₀, q_accept, q_reject) 其中:
- Q: 有限状态集
- Σ: 输入字母表
- Γ: 纸带字母表 (Σ ⊆ Γ, 包含空白符号␣)
- δ: Q × Γ → Q × Γ × {L,R} (转移函数)
- q₀: 初始状态
- q_accept, q_reject: 接受和拒绝状态

**计算**: 从初始状态q₀开始，读写头在输入最左端，按照δ转移，直到进入q_accept或q_reject。

#### 定义 I.5.2 (可计算函数)
**Definition I.5.2 (Computable Functions)**

函数f: ℕ^k → ℕ是**可计算的** (computable/recursive) 如果存在图灵机M使得:
- 对所有输入(n₁,...,nₖ)，M停机并输出f(n₁,...,nₖ)

**等价定义**:
- μ-递归函数
- λ-可定义函数
- 寄存器机可计算函数
- (通过Church-Turing论题) 直观可计算函数

#### 定义 I.5.3 (可判定集)
**Definition I.5.3 (Decidable Sets)**

集合A ⊆ ℕ是**可判定的** (decidable/recursive) 如果其特征函数χ_A是可计算的。

A是**可枚举的** (recursively enumerable, r.e.) 如果存在可计算函数f使得A = range(f)。

#### 定理 1.12 (停机问题不可判定)
**Theorem 1.12 (Undecidability of Halting Problem)**

集合HALT = {⟨M,w⟩ : 图灵机M在输入w上停机} 是不可判定的。

*证明*. 对角化论证:
- 设HALT可判定，有图灵机H判定它
- 构造机器D: D(⟨M⟩) = 在M(⟨M⟩)上停机则死循环，否则接受
- 考虑D(⟨D⟩): 停机⟺不停机，矛盾 □

#### 定义 I.5.4 (归约与完备性)
**Definition I.5.4 (Reductions and Completeness)**

**多一归约** (many-one reduction): A ≤_m B ⟺ 存在可计算f使得x∈A ⟺ f(x)∈B

**图灵归约** (Turing reduction): A ≤_T B ⟺ A可被B-谕示图灵机计算

**完备性**: 
- A是r.e.-完备 ⟺ A是r.e.且所有r.e.集多一归约到A

**例子**: HALT是r.e.-完备的。

#### 定理 1.13 (Rice定理)
**Theorem 1.13 (Rice's Theorem)**

设P是可计算函数的性质。若P非平凡(存在函数满足P，存在函数不满足P)，则P不可判定。

*推论*: 没有算法能判定程序是否总是输出0、是否在有限步内停机、是否等价于另一个程序等。

#### 定义 I.5.5 (算术层级)
**Definition I.5.5 (Arithmetical Hierarchy)**

- **Σ₀ = Π₀ = Δ₀**: 可判定集
- **Σ_{n+1}**: 形如{x : ∃y₁∀y₂∃y₃...Qyₙ R(x,y₁,...,yₙ)}，其中R可判定
- **Π_{n+1}**: 形如{x : ∀y₁∃y₂∀y₃...Qyₙ R(x,y₁,...,yₙ)}，其中R可判定
- **Δ_n = Σ_n ∩ Π_n**

**例子**:
- HALT ∈ Σ₁ \ Π₁
- TOT = {e : φ_e处处定义} ∈ Π₂ \ Σ₂

---

## 2. 组合数学 (05-XX)

### 2.1 经典组合问题 [05Axx]

#### 定义 II.1.1 (排列与组合)
**Definition II.1.1 (Permutations and Combinations)**

**排列数**: P(n,k) = n!/(n-k)! (从n个不同元素选k个的有序排列数)

**组合数**: C(n,k) = (n choose k) = n!/[k!(n-k)!] (从n个不同元素选k个的无序选择数)

**基本恒等式**:
1. C(n,k) = C(n,n-k)
2. C(n,k) = C(n-1,k) + C(n-1,k-1) (Pascal恒等式)
3. Σ_{k=0}^n C(n,k) = 2^n
4. C(n,0) - C(n,1) + C(n,2) - ... = 0

#### 定义 II.1.2 (容斥原理)
**Definition II.1.2 (Inclusion-Exclusion Principle)**

|A₁ ∪ A₂ ∪ ... ∪ Aₙ| = Σ|Aᵢ| - Σ|Aᵢ∩Aⱼ| + Σ|Aᵢ∩Aⱼ∩Aₖ| - ... + (-1)^{n+1}|A₁∩A₂∩...∩Aₙ|

**例子** (错排问题): D_n = n!(1 - 1/1! + 1/2! - 1/3! + ... + (-1)^n/n!)

#### 定义 II.1.3 (生成函数)
**Definition II.1.3 (Generating Functions)**

序列{aₙ}的**普通生成函数** (ordinary generating function):
G(x) = a₀ + a₁x + a₂x² + ...

**指数生成函数** (exponential generating function):
E(x) = a₀ + a₁x/1! + a₂x²/2! + ...

**例子**:
- {1,1,1,...}的OGF: 1/(1-x)
- {n!}的EGF: 1/(1-x)
- Fibonacci序列{Fₙ}: F(x) = x/(1-x-x²)

#### 定理 2.1 (Catalan数)
**Theorem 2.1 (Catalan Numbers)**

**Catalan数** Cₙ = (2n choose n)/(n+1) = C(2n,n) - C(2n,n+1)

**等价定义**: Cₙ计数:
1. n+1个叶子的满二叉树数目
2. n对括号的合法配对数目
3. 从(0,0)到(n,n)不越过对角线的路径数目
4. 用不相交对角线将凸n+2边形分成三角形的数目

**生成函数**: C(x) = (1-√(1-4x))/(2x)

**递推关系**: Cₙ = Σ_{i=0}^{n-1} CᵢC_{n-1-i}, C₀ = 1

#### 定义 II.1.4 (Stirling数)
**Definition II.1.4 (Stirling Numbers)**

**第一类Stirling数** s(n,k): 将n个元素排成k个轮换的方法数
- 递推: s(n,k) = s(n-1,k-1) + (n-1)s(n-1,k)
- 生成函数: x(x-1)...(x-n+1) = Σ_{k=0}^n s(n,k)x^k

**第二类Stirling数** S(n,k): 将n个元素分成k个非空子集的方法数
- 递推: S(n,k) = S(n-1,k-1) + kS(n-1,k)
- 公式: S(n,k) = (1/k!)Σ_{i=0}^k (-1)^{k-i}C(k,i)i^n

**关系**: n!S(n,k) = |s(n,k)|

---

### 2.2 图论基础 [05Cxx]

#### 定义 II.2.1 (图)
**Definition II.2.1 (Graphs)**

**图** G = (V,E) 其中:
- V: 顶点集(有限或无限)
- E ⊆ V×V: 边集

**简单图**: 无自环、无重边
**多重图**: 允许重边
**有向图**: E中的元素是有序对

**基本概念**:
- **邻接**: u,v相邻 ⟺ {u,v} ∈ E
- **度**: deg(v) = |{e∈E : v∈e}|
- **路径**: 顶点序列v₀,v₁,...,vₖ使得{vᵢ,vᵢ₊₁}∈E
- **圈**: 起点等于终点的路径
- **连通**: 任意两点有路径连接

#### 定理 2.2 (握手定理)
**Theorem 2.2 (Handshaking Lemma)**

Σ_{v∈V} deg(v) = 2|E|

*证明*. 每条边对总度数贡献2. □

*推论*: 度数为奇数的顶点数目是偶数。

#### 定理 2.3 (Euler路径与回路)
**Theorem 2.3 (Eulerian Paths and Circuits)**

图G有Euler回路 ⟺ G连通且每个顶点度数为偶数。

图G有Euler路径 ⟺ G连通且恰好有0个或2个奇度数顶点。

**历史**: Euler (1736) 解决柯尼斯堡七桥问题，开创图论。

#### 定理 2.4 (图的着色)
**Theorem 2.4 (Graph Coloring)**

**顶点着色**: 给顶点染色使相邻顶点颜色不同

**色数** χ(G): 着色所需的最少颜色数

**基本结果**:
1. χ(Kₙ) = n (完全图)
2. χ(C₂ₙ) = 2, χ(C₂ₙ₊₁) = 3 (圈)
3. χ(平面图) ≤ 4 (四色定理)
4. χ(G) ≤ Δ(G) + 1 (Δ是最大度数)

**Brooks定理**: 若G不是完全图或奇圈，则χ(G) ≤ Δ(G)。

#### 定理 2.5 (图的匹配)
**Theorem 2.5 (Matching Theory)**

**匹配**: 两两不相交的边集

**完美匹配**: 覆盖所有顶点的匹配

**Hall婚配定理**: 二部图G = (X,Y,E)有饱和X的匹配 ⟺ 对所有S⊆X, |N(S)| ≥ |S|

其中N(S) = {y∈Y : ∃x∈S, {x,y}∈E}是S的邻域。

#### 定理 2.6 (平面图)
**Theorem 2.6 (Planar Graphs)**

**平面图**: 可在平面上画出使得边不相交的图

**Euler公式**: 对连通平面图, V - E + F = 2 (V顶点,E边,F面)

*推论*:
1. E ≤ 3V - 6 (V ≥ 3)
2. 存在度数≤5的顶点
3. K₅和K₃,₃不是平面图(Kuratowski定理)

---

### 2.3 极值组合 [05Dxx]

#### 定理 2.7 (Ramsey定理)
**Theorem 2.7 (Ramsey's Theorem)**

对任意正整数r, s, 存在最小的R(r,s)使得:
任何R(r,s)个顶点的图的边被染成红蓝两色后，必有红色K_r或蓝色K_s。

**Ramsey数**:
- R(3,3) = 6 (友谊定理)
- R(4,4) = 18
- R(5,5) = ? (只知道在43-48之间)

**一般形式**: 对任意k和正整数n₁,...,nₖ，存在N使得K_N的边k染色后必有某色的K_{nᵢ}。

**无限形式**: 无限完全图的边任意有限染色，必有无限单色完全子图。

#### 定理 2.8 (Turán定理)
**Theorem 2.8 (Turán's Theorem)**

不含K_{r+1}的n个顶点的图的最大边数是(1-1/r)n²/2，由Turán图T(n,r)达到。

**Turán图** T(n,r): 将n个顶点尽可能均匀地分成r份，不同份的顶点间连边。

#### 定理 2.9 (Erdős-Ko-Rado定理)
**Theorem 2.9 (Erdős-Ko-Rado Theorem)**

设n ≥ 2k，F是[n]的k元素子集族，且F中任意两个集合相交。则|F| ≤ C(n-1,k-1)。

**等号情况**: n > 2k时，等号成立当且仅当F是星型族(所有集合包含某固定元素)。

---

### 2.4 代数组合 [05Exx]

#### 定义 II.4.1 (组合设计)
**Definition II.4.1 (Combinatorial Designs)**

**(v,k,λ)-设计**: 集合V（|V|=v）的子集族B使得:
1. 每个B∈B有k个元素
2. V的每对元素恰好含于λ个区组B

**例子**:
- Fano平面: (7,3,1)-设计
- 仿射/射影平面

#### 定义 II.4.2 (对称函数)
**Definition II.4.2 (Symmetric Functions)**

**初等对称函数**: eₖ(x₁,...,xₙ) = Σ_{1≤i₁<...<iₖ≤n} x_{i₁}...x_{iₖ}

**完全齐次对称函数**: hₖ = Σ_{1≤i₁≤...≤iₖ≤n} x_{i₁}...x_{iₖ}

**幂和**: pₖ = x₁^k + ... + xₙ^k

**关系**:
- Σ_{i=0}^k (-1)^i eᵢh_{k-i} = 0
- pₖ = Σ_{λ⊢k} χ^λ(λ!)e_λ / z_λ

---

## 3. 序、格与有序代数结构 (06-XX)

### 3.1 偏序集 [06Axx]

#### 定义 III.1.1 (偏序)
**Definition III.1.1 (Partial Order)**

集合P上的**偏序** ≤ 是一个二元关系，满足:
1. 自反性 (reflexivity): x ≤ x
2. 反对称性 (antisymmetry): x ≤ y 且 y ≤ x ⟹ x = y
3. 传递性 (transitivity): x ≤ y 且 y ≤ z ⟹ x ≤ z

**偏序集** (poset): (P,≤)

**全序**: 任意两个元素可比较的偏序

**例子**:
- (ℕ,≤): 自然数的通常序
- (P(X),⊆): 集合的包含关系
- (ℕ,|): 整除关系

#### 定义 III.1.2 (Hasse图)
**Definition III.1.2 (Hasse Diagram)**

偏序集的**Hasse图**是表示覆盖关系的图:
y覆盖x ⟺ x < y且不存在z使得x < z < y

在图中，x在y下方，有边连接。

#### 定义 III.1.3 (特殊元素)
**Definition III.1.3 (Special Elements)**

设S ⊆ P是偏序集的子集:
- **上界** (upper bound): u使得对所有s∈S, s ≤ u
- **下界** (lower bound): l使得对所有s∈S, l ≤ s
- **最小上界/上确界** (supremum): sup(S) = min{u : u是S的上界}
- **最大下界/下确界** (infimum): inf(S) = max{l : l是S的下界}
- **极大元** (maximal): x ∈ S使得不存在y > x in S
- **最大元** (maximum): x ∈ S使得对所有y∈S, y ≤ x

**注意**: 最大元一定唯一，但极大元不一定唯一。

#### 定理 3.1 (Zorn引理在偏序集中的应用)
**Theorem 3.1 (Zorn's Lemma for Posets)**

若偏序集P的每条链都有上界，则P有极大元。

**应用**:
- 证明每个向量空间有基
- 证明每个环有极大理想
- 证明Hahn-Banach扩张定理

---

### 3.2 格 [06Bxx]

#### 定义 III.2.1 (格)
**Definition III.2.1 (Lattices)**

**格** (lattice) 是一个偏序集(L,≤)使得每对元素都有上确界和下确界。

**格运算**:
- x ∨ y = sup{x,y} (并/join)
- x ∧ y = inf{x,y} (交/meet)

**代数定义**: 格是集合L带两个二元运算∨和∧，满足:
1. 交换律: x ∨ y = y ∨ x, x ∧ y = y ∧ x
2. 结合律: (x ∨ y) ∨ z = x ∨ (y ∨ z), (x ∧ y) ∧ z = x ∧ (y ∧ z)
3. 吸收律: x ∨ (x ∧ y) = x, x ∧ (x ∨ y) = x
4. 幂等律: x ∨ x = x, x ∧ x = x

**例子**:
- (P(X), ∪, ∩): 集合格
- (ℕ, gcd, lcm): 整除格
- (子空间, +, ∩): 子空间格

#### 定理 3.2 (对偶原理)
**Theorem 3.2 (Duality Principle)**

格中成立的任何命题，将∨与∧互换，≤与≥互换后仍然成立。

#### 定义 III.2.2 (分配格、模格)
**Definition III.2.2 (Distributive and Modular Lattices)**

**分配格** (distributive lattice): x ∨ (y ∧ z) = (x ∨ y) ∧ (x ∨ z)

**模格** (modular lattice): x ≤ z ⟹ x ∨ (y ∧ z) = (x ∨ y) ∧ z

**关系**: 分配格 → 模格 → 一般格

**例子**:
- 集合格是分配格
- 子群格是模格(但一般不分配)
- 子空间格是模格

#### 定理 3.3 (Birkhoff表示定理)
**Theorem 3.3 (Birkhoff's Representation Theorem)**

每个有限分配格同构于某个有限偏序集的序理想的格。

*证明*. 见Davey & Priestley, *Introduction to Lattices and Order*, Cambridge, 2002. □

---

### 3.3 布尔代数 [06Exx]

#### 定义 III.3.1 (布尔代数)
**Definition III.3.1 (Boolean Algebras)**

**布尔代数** (B,∨,∧,¬,0,1) 是有补的分配格，即:
1. (B,∨,∧)是分配格
2. 0 ≤ x ≤ 1对所有x
3. x ∨ ¬x = 1, x ∧ ¬x = 0

**等价公理系统**:
Huntington公理: (x')' = x, x∨y = y∨x, (x∨y)' = x'∧y'

#### 定理 3.4 (Stone表示定理)
**Theorem 3.4 (Stone Representation Theorem)**

每个布尔代数同构于某个拓扑空间的开闭集的布尔代数。

**对偶**: 布尔代数范畴对偶于Stone空间(全不连通紧Hausdorff空间)范畴。

#### 定理 3.5 (布尔代数的完备性定理)
**Theorem 3.5 (Completeness for Boolean Algebras)**

命题逻辑中的永真式等价于在所有布尔代数中恒为1的表达式。

---

## 4. 数论 (11-XX)

### 4.1 初等数论 [11Axx]

#### 定义 IV.1.1 (整除与最大公约数)
**Definition IV.1.1 (Divisibility and GCD)**

**整除**: a|b ⟺ ∃c, b = ac

**最大公约数**: gcd(a,b) = max{d : d|a且d|b}

**欧几里得算法**:
```
gcd(a,b) = gcd(b, a mod b)  if b ≠ 0
gcd(a,0) = a
```

#### 定理 4.1 (Bézout恒等式)
**Theorem 4.1 (Bézout's Identity)**

gcd(a,b) = ax + by 对某x,y ∈ ℤ

*证明*. 欧几里得算法的逆过程构造x和y. □

#### 定理 4.2 (算术基本定理)
**Theorem 4.2 (Fundamental Theorem of Arithmetic)**

每个大于1的整数可唯一分解为质数乘积(不计顺序)。

*证明*. 
- 存在性: 归纳法(若n是合数，则n=ab, 1<a,b<n)
- 唯一性: 若p|ab则p|a或p|b (Euclid引理) □

#### 定义 IV.1.2 (模运算)
**Definition IV.1.2 (Modular Arithmetic)**

a ≡ b (mod n) ⟺ n|(a-b)

**性质**:
- 自反、对称、传递
- a≡b, c≡d (mod n) ⟹ a+c≡b+d, ac≡bd (mod n)

**剩余类环**: ℤ/nℤ = {[0],[1],...,[n-1]}

#### 定理 4.3 (Fermat小定理)
**Theorem 4.3 (Fermat's Little Theorem)**

若p是质数且gcd(a,p)=1，则a^{p-1} ≡ 1 (mod p)

*证明*. 
- 方法1: 考虑{a,2a,...,(p-1)a} mod p
- 方法2: 群论(|(ℤ/pℤ)*| = p-1) □

#### 定理 4.4 (中国剩余定理)
**Theorem 4.4 (Chinese Remainder Theorem)**

若gcd(m,n)=1，则对任意a,b，方程组:
```
x ≡ a (mod m)
x ≡ b (mod n)
```
在[0,mn)中有唯一解。

*证明*. Bézout恒等式: 1 = mx + ny, 取x₀ = a·ny + b·mx. □

**推广**: 对n₁,...,nₖ两两互质，方程组在[0,Πnᵢ)中有唯一解。

---

### 4.2 二次剩余 [11Exx]

#### 定义 IV.2.1 (Legendre符号)
**Definition IV.2.1 (Legendre Symbol)**

对奇质数p和a不被p整除:
```
(a|p) = 1   若x²≡a (mod p)有解
(a|p) = -1  若x²≡a (mod p)无解
```

**Euler判据**: (a|p) ≡ a^{(p-1)/2} (mod p)

#### 定理 4.5 (二次互反律)
**Theorem 4.5 (Quadratic Reciprocity)**

对奇质数p,q:
```
(p|q)(q|p) = (-1)^{(p-1)(q-1)/4}
```

**补充**: 
- (-1|p) = (-1)^{(p-1)/2}
- (2|p) = (-1)^{(p²-1)/8}

**历史**: Gauss称其为"黄金定理"，给出了8个证明。现在有200多个证明。

---

### 4.3 解析数论基础 [11Mxx]

#### 定义 IV.3.1 (Riemann ζ函数)
**Definition IV.3.1 (Riemann Zeta Function)**

**Riemann ζ函数**: ζ(s) = Σ_{n=1}^∞ 1/n^s (Re(s) > 1)

**Euler乘积**: ζ(s) = ∏_p (1-p^{-s})^{-1}

**解析延拓**: ζ(s)可延拓到整个复平面，仅在s=1有单极点。

**函数方程**: ζ(s) = 2^s π^{s-1} sin(πs/2) Γ(1-s) ζ(1-s)

#### 定义 IV.3.2 (Riemann假设)
**Definition IV.3.2 (Riemann Hypothesis)**

**Riemann假设 (RH)**: ζ(s)的所有非平凡零点都在Re(s)=1/2上。

**等价形式**:
1. π(x) = Li(x) + O(√x log x) (质数定理的强形式)
2. M(x) = Σ_{n≤x} μ(n) = O(x^{1/2+ε}) (Mertens函数)
3. ζ(1/2+it) = O(t^ε) (Lindelöf假设)

**状态**: 未解决，是Clay研究所千禧年问题之一。

#### 定理 4.6 (质数定理)
**Theorem 4.6 (Prime Number Theorem)**

π(x) ~ x/log(x) 当x→∞

其中π(x)是≤x的质数个数。

**证明思路** (Hadamard & de la Vallée Poussin, 1896):
1. ζ(s)在Re(s)≥1无零点
2. 通过复分析得到渐近公式

**误差项**: 已知π(x) = Li(x) + O(x exp(-c√(log x)))，但RH给出最好误差O(√x log x)

---

### 4.4 代数数论 [11Rxx]

#### 定义 IV.4.1 (代数整数)
**Definition IV.4.1 (Algebraic Integers)**

**代数整数**: 首一整系数多项式的根

**代数数**: 有理系数多项式的根

**数域**: ℚ的有限扩张K

**整数环**: O_K = K中所有代数整数

**例子**:
- ℤ[√-1] (Gauss整数)
- ℤ[√2]
- ℤ[ω] (ω是三次单位根, Eisenstein整数)

#### 定理 4.7 (整数环的唯一分解性质)
**Theorem 4.7 (Unique Factorization in Integer Rings)**

O_K不一定是UFD。但它是**Dedekind整环**:
1. Noetherian
2. 整闭
3. 非0素理想都是极大理想

**理想类群**: Cl(K) = {理想}/~ (A~B ⟺ A=aB对某a∈K*)
**类数**: h_K = |Cl(K)|

**定理**: O_K是UFD ⟺ h_K = 1

**例子**:
- ℤ[√-5]不是UFD: 6 = 2×3 = (1+√-5)(1-√-5)
- 但其理想有唯一分解

#### 定理 4.8 (Dirichlet单位定理)
**Theorem 4.8 (Dirichlet's Unit Theorem)**

数域K的单位群O_K* ≅ μ_K × ℤ^{r+s-1}

其中:
- μ_K: 单位根群(有限循环群)
- r: 实嵌入个数
- s: 复共轭嵌入对数
- [K:ℚ] = r + 2s

**例子**:
- ℤ[√2]* ≅ ±1 × ℤ (由1+√2生成无限部分)
- ℤ[√-1]* = {±1, ±i}

#### 定义 IV.4.2 (素理想分解)
**Definition IV.4.2 (Prime Ideal Decomposition)**

设L/K是数域扩张，P是O_K的素理想。

P O_L = ∏_{i=1}^g P_i^{e_i}

**分歧指数**: e_i
**剩余次数**: f_i = [O_L/P_i : O_K/P]
**基本关系**: Σ_{i=1}^g e_i f_i = [L:K]

**分歧**: 某个e_i > 1

**例子**: 在ℚ(√-1)/ℚ中:
- (2) = (1+i)² 完全分歧 (e=2,f=1,g=1)
- (3) 惯性 (e=1,f=2,g=1)
- (5) = (2+i)(2-i) 分裂 (e=1,f=1,g=2)

---

### 4.5 椭圆曲线 [11Gxx]

#### 定义 IV.5.1 (椭圆曲线)
**Definition IV.5.1 (Elliptic Curves)**

**椭圆曲线** (Weierstrass形式):
```
E: y² = x³ + ax + b  (char ≠ 2,3)
判别式: Δ = -16(4a³ + 27b²) ≠ 0
```

**群结构**: E上的点构成阿贝尔群:
- 单位元O: 无穷远点
- P + Q: 连接P,Q的直线与E的第三点R的y对称
- 2P: P点切线与E的第三点的y对称

**例子**: y² = x³ - x
- 点 (0,0), (±1,0), O
- 这是4阶群: ℤ/4ℤ 或 ℤ/2ℤ × ℤ/2ℤ

#### 定义 IV.5.2 (Mordell-Weil群)
**Definition IV.5.2 (Mordell-Weil Group)**

**Mordell-Weil群**: E(K) (K上所有有理点)

#### 定理 4.9 (Mordell-Weil定理)
**Theorem 4.9 (Mordell-Weil Theorem)**

对数域K上的椭圆曲线E, E(K)是有限生成阿贝尔群:
```
E(K) ≅ ℤ^r × E(K)_tors
```
- r: 秩(rank)
- E(K)_tors: 有限阶子群

**Mazur定理**: E(ℚ)_tors是以下15种之一:
- ℤ/nℤ (n=1,...,10,12)
- ℤ/2ℤ × ℤ/2nℤ (n=1,...,4)

#### 定义 IV.5.3 (L函数)
**Definition IV.5.3 (L-Functions)**

**椭圆曲线的L函数**: 
```
L(E,s) = ∏_p L_p(p^{-s})^{-1}
```
其中对好质数p:
```
L_p(T) = 1 - a_p T + p T²
a_p = p + 1 - #E(𝔽_p)
```

**BSD猜想** (Birch and Swinnerton-Dyer):
L(E,s)在s=1的零点阶数等于E(ℚ)的秩r。

**状态**: 千禧年问题，仅对r≤1证明。

#### 定理 4.10 (模性定理)
**Theorem 4.10 (Modularity Theorem)**

每个ℚ上的椭圆曲线都是模的: 存在权2的尖点形式f使得L(E,s) = L(f,s)。

**历史**:
- Taniyama-Shimura猜想 (1950s)
- Wiles证明半稳定情形 (1995, 费马大定理)
- Breuil-Conrad-Diamond-Taylor证明一般情形 (2001)

---

## Lean4 代码示例

本节提供与第一卷内容相关的Lean4代码示例，基于Mathlib4库。

### 1. 命题逻辑的Lean4实现

```lean4
-- 命题逻辑基本联结词
-- 在Lean4中，命题是Prop类型的元素

-- 否定、合取、析取、蕴含、等价都是内置的
-- ¬p 是 ¬p (或 p → False)
-- p ∧ q 是合取
-- p ∨ q 是析取
-- p → q 是蕴含
-- p ↔ q 是等价

-- 排中律 (Law of Excluded Middle)
example (p : Prop) : p ∨ ¬p := by
  exact Classical.em p

-- 使用 decidability 的构造性证明
example (p : Prop) [Decidable p] : p ∨ ¬p := by
  by_cases h : p
  · left; exact h
  · right; exact h

-- 德摩根定律
example (p q : Prop) : ¬(p ∧ q) ↔ ¬p ∨ ¬q := by
  constructor
  · intro h
    by_cases hp : p
    · right
      intro hq
      exact h ⟨hp, hq⟩
    · left
      exact hp
  · intro h ⟨hp, hq⟩
    cases h with
    | inl hnp => exact hnp hp
    | inr hnq => exact hnq hq

-- 蕴含的传递性
example (p q r : Prop) : (p → q) → (q → r) → (p → r) := by
  intro hpq hqr hp
  exact hqr (hpq hp)

-- 双重否定消除
example (p : Prop) : ¬¬p ↔ p := by
  constructor
  · intro hnn
    exact Classical.byContradiction (fun hnp => hnn hnp)
  · intro hp hnp
    exact hnp hp
```

### 2. 一阶逻辑与集合论

```lean4
-- 量词的使用
-- ∀ (全称量词) 和 ∃ (存在量词)

-- 全称量词消去
example (P : ℕ → Prop) (h : ∀ n, P n) : P 0 := h 0

-- 存在量词消去
example (P : ℕ → Prop) (h : ∃ n, P n) (Q : Prop) 
    (hP : ∀ n, P n → Q) : Q := by
  obtain ⟨n, hn⟩ := h
  exact hP n hn

-- 集合论基础
import Mathlib.Data.Set.Basic

-- 集合的包含与相等
example (A B : Set ℕ) : A = B ↔ A ⊆ B ∧ B ⊆ A := by
  exact Set.Subset.antisymm_iff

-- 并集与交集
example (A B C : Set ℕ) : A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C) := by
  ext x
  constructor <;> intro h
  · cases h.2 with
    | inl hb => left; exact ⟨h.1, hb⟩
    | inr hc => right; exact ⟨h.1, hc⟩
  · cases h with
    | inl hab => exact ⟨hab.1, Or.inl hab.2⟩
    | inr hac => exact ⟨hac.1, Or.inr hac.2⟩

-- Cantor定理: |X| < |P(X)|
import Mathlib.SetTheory.Cardinal.Basic

example (α : Type*) : Cardinal.mk α < Cardinal.mk (Set α) := by
  exact Cardinal.cantor (α := α)
```

### 3. 自然数与递归定义

```lean4
import Mathlib.Data.Nat.Basic
import Mathlib.Data.Nat.Parity

-- 自然数的递归定义
def factorial : ℕ → ℕ
  | 0 => 1
  | n + 1 => (n + 1) * factorial n

-- factorial的性质
example : factorial 0 = 1 := rfl
example : factorial 5 = 120 := rfl

-- 费波那契数列
def fib : ℕ → ℕ
  | 0 => 0
  | 1 => 1
  | n + 2 => fib n + fib (n + 1)

example : fib 10 = 55 := rfl

-- 数学归纳法
example (P : ℕ → Prop) (h0 : P 0) (hs : ∀ n, P n → P (n + 1)) : ∀ n, P n := by
  intro n
  induction n with
  | zero => exact h0
  | succ n ih => exact hs n ih

-- 1 + 2 + ... + n = n(n+1)/2
example (n : ℕ) : 2 * (∑ i ∈ Finset.range (n + 1), i) = n * (n + 1) := by
  induction n with
  | zero => simp
  | succ n ih =>
    simp [Finset.sum_range_succ, Nat.mul_add]
    omega
```

### 4. 整除与最大公约数

```lean4
import Mathlib.Data.Nat.GCD.Basic
import Mathlib.Data.Nat.Prime.Basic

-- 整除的定义
example (a b : ℕ) : a ∣ b ↔ ∃ k, b = a * k := Iff.rfl

-- 整除的传递性
example (a b c : ℕ) : a ∣ b → b ∣ c → a ∣ c := by
  intro ⟨k1, hk1⟩ ⟨k2, hk2⟩
  use k1 * k2
  rw [hk1, hk2, mul_assoc]

-- GCD的基本性质
example (a b : ℕ) : Nat.gcd a b ∣ a ∧ Nat.gcd a b ∣ b := by
  constructor
  · exact Nat.gcd_dvd_left a b
  · exact Nat.gcd_dvd_right a b

-- GCD是最大的公约数
example (a b d : ℕ) (ha : d ∣ a) (hb : d ∣ b) : d ∣ Nat.gcd a b := by
  exact Nat.dvd_gcd ha hb

-- Bézout恒等式
example (a b : ℕ) : ∃ x y, a * x = b * y + Nat.gcd a b ∨ 
                         a * x + Nat.gcd a b = b * y := by
  use Nat.gcdA a b, Nat.gcdB a b
  exact Or.inl (Nat.gcd_eq_gcd_ab a b).symm

-- 互素的定义
example (a b : ℕ) : Nat.Coprime a b ↔ Nat.gcd a b = 1 := Iff.rfl

-- 互素的性质
example (a b : ℕ) (h : Nat.Coprime a b) : ∃ x y, a * x + b * y = 1 := by
  use Nat.gcdA a b, Nat.gcdB a b
  have := Nat.gcd_eq_gcd_ab a b
  rwa [Nat.gcd_eq_one_iff_coprime.mpr h] at this
```

### 5. 素数

```lean4
import Mathlib.Data.Nat.Prime.Basic

-- 素数的定义
example (p : ℕ) : Nat.Prime p ↔ 2 ≤ p ∧ ∀ m, m ∣ p → m = 1 ∨ m = p := by
  exact Nat.prime_def_le''' p

-- 检查素数
example : Nat.Prime 2 := Nat.prime_two
example : Nat.Prime 7 := Nat.prime_seven
example : Nat.Prime 101 := Nat.prime_oneHundredOne

-- 素数有无穷多个 (简化版本)
-- Euclid的证明：如果有有限个素数，考虑它们的乘积加1

-- 如果 p ∣ a * b 则 p ∣ a 或 p ∣ b
example (p a b : ℕ) (hp : Nat.Prime p) (h : p ∣ a * b) : p ∣ a ∨ p ∣ b := by
  exact Nat.Prime.dvd_mul hp h

-- 欧几里得引理
example (p a b : ℕ) (hp : Nat.Prime p) (hpa : ¬p ∣ a) (h : p ∣ a * b) : p ∣ b := by
  exact (Nat.Prime.dvd_mul hp h).resolve_left hpa
```

### 6. 模运算

```lean4
import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Int.ModEq

-- 模运算的基本性质
example (a b n : ℤ) : a ≡ b [MOD n] ↔ (a - b) % n = 0 := by
  exact Int.modEq_iff_dvd

-- 模运算保持加法
example (a b c d n : ℤ) (hab : a ≡ b [MOD n]) (hcd : c ≡ d [MOD n]) :
    a + c ≡ b + d [MOD n] := by
  exact Int.ModEq.add hab hcd

-- 模运算保持乘法
example (a b c d n : ℤ) (hab : a ≡ b [MOD n]) (hcd : c ≡ d [MOD n]) :
    a * c ≡ b * d [MOD n] := by
  exact Int.ModEq.mul hab hcd

-- Fermat小定理
example (p : ℕ) (a : ℤ) (hp : Nat.Prime p) (ha : ¬(p : ℤ) ∣ a) :
    a^(p-1) ≡ 1 [MOD p] := by
  have := Int.ModEq.pow_card_sub_one_eq_one hp a ha
  convert this using 1
  simp [Nat.card]

-- 中国剩余定理
import Mathlib.NumberTheory.ChineseRemainder

example (m n : ℕ) (a b : ℤ) (hmn : Nat.Coprime m n) :
    ∃ x, x ≡ a [MOD m] ∧ x ≡ b [MOD n] := by
  exact Int.exists_modEq_and m n a b hmn
```

### 7. 组合数学基础

```lean4
import Mathlib.Data.Finset.Basic
import Mathlib.Algebra.BigOperators.Group.Finset

-- 二项式系数
open Nat

example (n k : ℕ) : choose n k = (Finset.range (n + 1)).card.choose k := rfl

-- 帕斯卡恒等式
example (n k : ℕ) (hk : k ≤ n) : 
    choose n k = choose (n - 1) (k - 1) + choose (n - 1) k := by
  exact choose_succ_succ (n - 1) (k - 1)

-- 二项式定理的系数
example (n : ℕ) : ∑ k ∈ Finset.range (n + 1), choose n k = 2^n := by
  exact Fin.sum_choose n

-- 鸽笼原理 (简化版)
example (f : Fin (n + 1) → Fin n) : ∃ i j, i ≠ j ∧ f i = f j := by
  by_contra h
  push_neg at h
  have := Fintype.card_fin (n + 1)
  have := Fintype.card_fin n
  omega

-- 容斥原理 (两个集合)
example (α : Type*) [Fintype α] (A B : Finset α) :
    (A ∪ B).card = A.card + B.card - (A ∩ B).card := by
  exact Finset.card_union_add_card_inter A B
```

### 8. 格与序结构

```lean4
import Mathlib.Order.Lattice
import Mathlib.Order.CompleteLattice

-- 偏序集的定义
example (α : Type*) [PartialOrder α] (a : α) : a ≤ a := le_rfl

-- 偏序的传递性
example (α : Type*) [PartialOrder α] (a b c : α) : a ≤ b → b ≤ c → a ≤ c := by
  intro hab hbc
  exact le_trans hab hbc

-- 反对称性
example (α : Type*) [PartialOrder α] (a b : α) : a ≤ b → b ≤ a → a = b := by
  intro hab hba
  exact le_antisymm hab hba

-- 格的上确界和下确界
example (α : Type*) [Lattice α] (a b : α) : a ⊓ b ≤ a := by
  exact inf_le_left

example (α : Type*) [Lattice α] (a b : α) : a ≤ a ⊔ b := by
  exact le_sup_left

-- 分配格
example (α : Type*) [DistribLattice α] (a b c : α) :
    a ⊔ (b ⊓ c) = (a ⊔ b) ⊓ (a ⊔ c) := by
  exact sup_inf_left

-- 布尔代数
import Mathlib.Algebra.BooleanAlgebra.Basic

example (α : Type*) [BooleanAlgebra α] (a : α) : a ⊔ aᶜ = ⊤ := by
  exact sup_compl_eq_top

example (α : Type*) [BooleanAlgebra α] (a : α) : a ⊓ aᶜ = ⊥ := by
  exact inf_compl_eq_bot

-- De Morgan定律
example (α : Type*) [BooleanAlgebra α] (a b : α) : (a ⊓ b)ᶜ = aᶜ ⊔ bᶜ := by
  exact compl_inf
```

### 9. 群论基础

```lean4
import Mathlib.Algebra.Group.Basic
import Mathlib.Algebra.Group.Subgroup.Basic

-- 群的定义
example (G : Type*) [Group G] (g : G) : g * g⁻¹ = 1 := by
  exact mul_inv_self

example (G : Type*) [Group G] (g : G) : g⁻¹ * g = 1 := by
  exact inv_mul_self

-- 单位元的唯一性
example (G : Type*) [Group G] (g : G) (h : g * g = g) : g = 1 := by
  exact eq_one_of_mul_eq_self h

-- 子群的定义
example (G : Type*) [Group G] (H : Subgroup G) : 
    (1 : G) ∈ H ∧ (∀ g ∈ H, g⁻¹ ∈ H) ∧ (∀ g h ∈ H, g * h ∈ H) := by
  exact ⟨Subgroup.one_mem H, Subgroup.inv_mem H, Subgroup.mul_mem H⟩

-- Lagrange定理：子群的阶整除群的阶
import Mathlib.Algebra.Group.FiniteTorsion

example (G : Type*) [Group G] [Fintype G] (H : Subgroup G) [Fintype H] :
    Nat.card H ∣ Nat.card G := by
  exact Nat.card_subgroup_dvd_card H
```

---

## 参考文献

### 数理逻辑
1. Enderton, H.B., *A Mathematical Introduction to Logic*, 2nd ed., Academic Press, 2001
2. Kunen, K., *Set Theory*, College Publications, 2011
3. Marker, D., *Model Theory: An Introduction*, Springer, 2002

### 组合数学
4. Stanley, R.P., *Enumerative Combinatorics*, Vols. 1-2, Cambridge, 1997-1999
5. van Lint, J.H., Wilson, R.M., *A Course in Combinatorics*, 2nd ed., Cambridge, 2001

### 格与序
6. Davey, B.A., Priestley, H.A., *Introduction to Lattices and Order*, 2nd ed., Cambridge, 2002
7. Birkhoff, G., *Lattice Theory*, 3rd ed., AMS, 1967

### 数论
8. Hardy, G.H., Wright, E.M., *An Introduction to the Theory of Numbers*, 6th ed., Oxford, 2008
9. Neukirch, J., *Algebraic Number Theory*, Springer, 1999
10. Silverman, J.H., *The Arithmetic of Elliptic Curves*, 2nd ed., Springer, 2009
11. Iwaniec, H., Kowalski, E., *Analytic Number Theory*, AMS, 2004

### 综合参考
12. Bourbaki, N., *Éléments de mathématique*, 多卷本, Springer

---

**注**: 本文档是第一卷第一部分，后续部分将包含:
- 12-XX 域论
- 13-XX 交换代数  
- 15-XX 线性代数与多重线性代数
- 16-XX 结合环与代数
- 17-XX 非结合环与代数
- 18-XX 范畴论
- 19-XX K-理论
- 20-XX 群论

每个主题都将遵循相同的严格标准和完整性要求。

---

*本卷完成日期: 2025-03-26*  
*下一卷预告: 泛函分析与算子理论*
