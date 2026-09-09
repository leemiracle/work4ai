# 类型论与 HoTT（Type Theory & Homotopy Type Theory）

> 类型论是继集合论之后第二种"数学基础"方案。它的核心直觉很朴素：**每个数学对象都带一个类型**，就像编程里的 `int`、`string`。更深一层是 Curry-Howard 同构——命题就是类型，证明就是程序。

## 历史脉络

| 年代 | 人物 | 事件 |
|------|------|------|
| 1903 | **Russell** | 在《Principles of Mathematics》附录提出类型论，用"类型分层"避免 $x\in x$ 这类自指悖论 |
| 1908 / 1910–13 | Russell / Whitehead-Russell | 分支类型论 ramified type theory；《Principia Mathematica》尝试把数学形式化 |
| 1940 | **Church** | 简单类型 λ-演算 simply typed λ-calculus |
| 1972–84 | **Martin-Löf** | 直觉类型论 Intuitionistic Type Theory：引入**依赖类型** dependent types、Π/Σ 类型 |
| 1980 | **Howard** | Curry-Howard 同构正式发表（成文于 1969），命题 = 类型 |
| 2013 | **HoTT 团队**（Voevodsky 等）| 《HoTT Book》出版，把类型论与同伦论结合，提出 Univalence Axiom |

## 核心思想：每个对象有类型

在集合论里，写 $x \in A$——$x$ 是集合 $A$ 的元素。在类型论里，写 $x : A$——$x$ 是类型 $A$ 的一个居民（inhabitant）。

区别看似细微，实则根本：
- **集合论**：先有一个"全集"，再在其中切出子集。无类型的元素可以属于任何集合。
- **类型论**：每个对象**出生时就带类型**，$x:A$ 是语法层面的判断，不靠性质去筛选。

这更像编程：你不能把 `3 : int` 当作 `"hello" : string` 使用，编译期就拦下了。类型论把这个"编译期检查"提升为数学基础——**良构性在构造时就保证了**。

## Curry-Howard 同构：命题 = 类型

| 逻辑 Prop | 类型 Type | 程序 |
|-----------|-----------|------|
| 真 $\top$ | 单位类型 $1$ | `()` |
| 假 $\bot$ | 空类型 $0$ | 无居民 |
| 合取 $A\wedge B$ | 积类型 $A\times B$ | `(a, b)` pair |
| 析取 $A\vee B$ | 和类型 $A+B$ | `inl a` / `inr b` |
| 蕴含 $A\to B$ | 函数类型 $A\to B$ | `λa. b` |
| 全称 $\forall x:A.\,P(x)$ | 依赖积 **Π 类型** | 依赖函数 |
| 存在 $\exists x:A.\,P(x)$ | 依赖和 **Σ 类型** | 依赖 pair |

要"证明"命题 $A$，就是构造一个类型为 $A$ 的程序。逻辑推理规则与类型构造规则**逐条对应**——这是 20 世纪逻辑学最深刻的发现之一。

## Martin-Löf 类型论（MLTT）

MLTT 在简单类型 λ-演算上加了**依赖类型**，让类型可以依赖于值：

### Π 类型（依赖函数）Dependent Product
$$\Pi_{x:A} B(x)$$
表示"对每个 $x:A$，给一个 $B(x)$ 类型的元素"。当 $B$ 不依赖 $x$ 时退化为普通函数类型 $A\to B$；逻辑上对应 $\forall$。

例：`vec_append : Π(n:Nat). Vec A n → Vec A m → Vec A (n+m)`——返回类型依赖于参数值。

### Σ 类型（依赖对）Dependent Sum
$$\Sigma_{x:A} B(x)$$
表示"一个 $x:A$，加上一个 $B(x)$ 的证据"。逻辑上对应 $\exists$。

例：$\Sigma_{n:\mathbb{N}}\,(\text{prime}(n))$ 就是"一个素数"——既给了数，又给了它是素数的证明。

### 等词类型 Identity Type
$$x =_A y$$
表示 $x$ 与 $y$ 在类型 $A$ 中相等。这看起来无害，但它的几何解释引爆了 HoTT。

## HoTT：类型 = 空间，等词 = 路径

HoTT（Homotopy Type Theory）由 Voevodsky 等人在 2012–2013 IAS 特别学年提出，核心是一组**惊人的对应**：

| 类型论 | 同伦论 Homotopy |
|--------|----------------|
| 类型 $A$ | 拓扑空间 |
| 元素 $a:A$ | 空间中的点 |
| 等词证明 $p : a =_A b$ | 从 $a$ 到 $b$ 的**路径** path |
| 两条路径相等 $p = q$ | 路径之间的**同伦** homotopy（二维路径）|
| 更高阶等词 | 高阶同伦 |

于是 $a =_A b$ 不再是"是/否"二值，而是"有几种不同的路径"——这给了相等一个**丰富的几何结构**。

### Univalence Axiom（Voevodsky）

非正式陈述：**等价的结构是相等的**。
$$ (A \simeq B) \;\simeq\; (A = B) $$
即"两个类型等价"当且仅当"它们相等"。

这听起来像废话，但在传统集合论里"同构 ≠ 相等"。Univalence 把"同构即相等"立为公理，极大简化了"把同构对象当作同一个对象"这一日常数学实践。

## 为什么重要：Lean / Coq 的基础

- **Lean 4**（mathlib4）：定理证明器，内核基于**依赖类型论**（Calculus of Inductive Constructions 的变体）。截至 2024 年 mathlib 已形式化数十万条定理，是当代最大的形式化数学仓库。
- **Coq**：基于 CIC（Calculus of Inductive Constructions），验证了四色定理（Gonthier 2005）、Feit-Thompson 定理（2012）。
- **Agda**：基于 MLTT 的证明助手与编程语言。

类型论的优势在于**可计算**与**构造性**：一个证明就是一个程序，可以"运行"它来提取算法。这是 ZFC 做不到的——ZFC 证明是符号序列，不能执行。

## 与集合论对比

| 维度 | 集合论 ZFC | 类型论 MLTT/HoTT |
|------|-----------|------------------|
| 对象归属 | $x \in A$（性质筛选）| $x : A$（语法判断）|
| 经典 vs 构造 | 经典，接受排中律 LEM | 默认构造性，LEM 需作为假设加入 |
| 存在 | 可非构造（AC）| 必须给出具体对象（程序）|
| 相等 | 二值（等或不等）| 分层（路径、高阶路径，HoTT）|
| 可计算性 | 证明不可执行 | 证明即程序，可运行 |
| 机器化 | 相对弱（Mizar 等）| 强（Lean / Coq / Agda）|
| 公理数 | ZFC 10 条 | 少数构造规则 + 可选 Univalence |

### 一个直观对照：构造同一个对象

要"证明" $\sqrt{2}$ 存在（即存在 $x$ 使 $x^2=2$）：
- **集合论**（经典）：假设不存在，推出矛盾，由排中律得存在。但**给不出具体 $x$ 的十进制展开**。
- **类型论**（构造）：必须给出一个算法/程序，能计算 $x$ 到任意精度（如 Newton 迭代）。证明本身就是计算过程。

这就是为什么构造性数学在计算机科学、算法验证、proof mining（从证明中提取算法）里有天然优势——它的证明天生可执行。

## 经典教材

| 教材 | 定位 | 备注 |
|------|------|------|
| **Pierce**《Types and Programming Languages》(TaPL, 2002) | PL 视角入门 | 不涉及 HoTT，建立类型直觉 |
| **Pierce** 等《Software Foundations》（在线）| Coq 实战 | 边读边在 Coq 里敲证明 |
| **HoTT Book**（2013，**开源免费**）| HoTT 权威 | 由特别年会的参与者集体写作，homotopytypetheory.org |
| **Martin-Löf**《Intuitionistic Type Theory》(1984) | 原始文献 | 哲学味重，适合深读 |
| **Theorem Proving in Lean 4**（在线教程）| Lean 入门 | leanprover.github.io |

## 学习路径建议

1. 先读 **Pierce TaPL** 前 6 章，建立"类型即命题、程序即证明"的直觉（不需要 HoTT）。
2. 用 **Lean 4** 或 **Coq**（Software Foundations 卷一）敲 10-20 个小证明，亲手感受 Curry-Howard。
3. 想深入数学基础 → 读 **HoTT Book** 第 1-3 章。
4. 想深入同伦解释 → HoTT Book 第 4-8 章（路径、同伦、Univalence）。

## 与本模块其他文件的关联

- Curry-Howard 详细展开 → [../统一视角/01-四种统一视角.md](../统一视角/01-四种统一视角.md) 的 (C)
- 类型论 vs 集合论的基础论战 → [../基础争议/01-基础论战与多元主义.md](../基础争议/01-基础论战与多元主义.md)
- 类型论为范畴论提供模型（topos）→ [../范畴论/01-范畴论作为统一语言.md](../范畴论/01-范畴论作为统一语言.md)
- 概念层面的"证明"多表征（含 Lean）→ [../../04-concepts/证明.md](../../04-concepts/证明.md)

## 自测

1. $x \in A$ 与 $x : A$ 的哲学区别是什么？为什么类型论不需要"分离公理"来规避悖论？
2. 在 Curry-Howard 下，$\exists x:A.\,P(x)$ 对应什么类型？要"证明"它需要构造什么？
3. Π 类型退化为普通函数类型 $A\to B$ 的条件是什么？
4. HoTT 里 $p : a =_A b$ 是一条"路径"——这意味着 $a$ 和 $b$ 之间可以有多条不同的路径吗？这与集合论的相等有什么不同？
5. Univalence 公理为什么让"同构对象可当作相等对象"成为合法操作？这违反了传统集合论的什么惯例？
6. 为什么说类型论的证明"可执行"，而 ZFC 的证明"不可执行"？
