# Spivak 第 29 章 · Construction of the Real Numbers · 精读笔记(🎯全书闭环·Dedekind 分割版)

> 基于原书第 29 章(PP.588-600)。**全书最重要的章**:用 **Dedekind 分割**从 $\mathbb{Q}$ 构造 $\mathbb{R}$,证明 LUB。
> ⚠️ **修正**:Spivak 用 **Dedekind 分割**(非 Cauchy 序列)。本笔记忠实原书。
> 原书:`Calculus (Spivak) 4th ed.` ch29 / 读于:2026-07-01

---

## §0 一句话

> **实数 = $\mathbb{Q}$ 的 Dedekind 分割(向下封闭的子集)。$\sqrt 2$ = $\{q\in\mathbb{Q}:q^2<2$ 或 $q<0\}$。Spivak 用这个构造证明 LUB——第 8 章的"假设"变成"定理"。**

---

## §1 动机(原书 P.588)
第 28 章定义"完备有序域",问:(1)存在?(2)唯一?第 29 章构造 $\mathbb{R}$ 答"存在"。

---

## §2 Dedekind 分割构造(原书 PP.588-590)⭐

### 实数 = 分割
一个**实数** $\alpha$ 是 $\mathbb{Q}$ 的子集,满足四条件:
1. **向下封闭**:$x\in\alpha, y<x\Rightarrow y\in\alpha$
2. **非空**:$\alpha\ne\varnothing$
3. **非全**:$\alpha\ne\mathbb{Q}$
4. **无最大元**:$x\in\alpha\Rightarrow\exists y\in\alpha, y>x$

> 直觉:$\alpha$ 是"所有小于某实数的有理数"。例如 $\sqrt 2=\{q\in\mathbb{Q}:q<0$ 或 $q^2<2\}$。

### 序
$$\alpha<\beta\iff\alpha\subsetneq\beta\text{(真子集)}$$
（集合包含关系 = 实数大小!）

### 加法(原书 P.591)
$$\alpha+\beta=\{x+y:x\in\alpha, y\in\beta\}$$

### 特殊元素
- $0=\{q\in\mathbb{Q}:q<0\}$
- $-\alpha=\{q\in\mathbb{Q}:-q\notin\alpha,$ 且 $-q$ 不是 $\mathbb{Q}-\alpha$ 的最小元$\}$(需小心边界)

### 验证(原书 PP.590-595,繁复)
每定义一个运算都要验证结果是"实数"(四条件)。例如证 $\alpha+\beta$ 是实数、$-\alpha$ 是实数、$\alpha+(-\alpha)=0$(这步需 **Archimedean 性质**)。

---

## §3 LUB 的证明(原书 PP.589-590,本章高潮)⭐

### 定理
实数集(分割族)满足 LUB。

### 证明(精妙而简短)
设 $A$ 是实数的非空有界集。**定义**:
$$\beta=\{q\in\mathbb{Q}:q\in\alpha\text{ 对某 }\alpha\in A\}=\bigcup_{\alpha\in A}\alpha$$
（$A$ 中所有实数的**并集**!)

验证 $\beta$ 是实数(四条件) + 是 $A$ 的最小上界:
- $\beta$ 是上界:每个 $\alpha\subseteq\beta$ ⟹ $\alpha\le\beta$
- $\beta$ 最小:任何上界 $\gamma$ 满足 $\alpha\subseteq\gamma(\forall\alpha)$ ⟹ $\beta\subseteq\gamma$ ⟹ $\beta\le\gamma$ ∎

> 🎯 **证明的精髓**:并集运算天然给出"最小上界"——这是 Dedekind 分割的优雅所在。Cauchy 构造的 LUB 证明繁琐,而 Dedekind 的只需一行"取并集"。

---

## §4 $\mathbb{Q}$ 嵌入 + 稠密
- $q\in\mathbb{Q}$ ↦ 分割 $\{r\in\mathbb{Q}:r<q\}$(主分割)⟹ $\mathbb{Q}\hookrightarrow\mathbb{R}$
- $\mathbb{Q}$ 在 $\mathbb{R}$ 稠密(Archimedean 性质保证)

---

## §5 全书伏笔终极回收

| 章 | 伏笔 | 第 29 章回收 |
|:-:|------|------------|
| 2 | $\sqrt 2$ 存在 | $\sqrt 2$ = 分割 $\{q:q^2<2$ 或 $q<0\}$,真实存在 |
| 3 | Cauchy 方程对无理数 | $\mathbb{Q}$ 稠密 + 连续 ⟹ 扩张 |
| 8 | LUB 是假设 | **并集构造证明 LUB**(本章)|

> 🏆 **闭环**:$\mathbb{R}$ = $\mathbb{Q}$ 的所有 Dedekind 分割。每个分割"是"一个实数。第 8 章的 LUB 公理,现在是一个**关于并集的初等定理**。

---

## §6 飞腾/Python 锚点
| 概念 | 工程 |
|------|------|
| Dedekind 分割 | $\mathbb{R}$ 的集合论模型(理论,非计算)|
| 并集=sup | 数据库/集合运算的上界 |
| $\mathbb{Q}$ 稠密 | 浮点(有限有理)逼近 $\mathbb{R}$ |
| Archimedean 性质 | 任意大有理数(浮点溢出的反面)|

> 💡 **对照**:Cauchy 构造(序列等价类)与 Dedekind 构造(分割)是**等价**的两种 $\mathbb{R}$ 模型。Spivak 选 Dedekind 因其 LUB 证明更简洁;分析教材常选 Cauchy 因其更贴近"极限"直觉。

---

## §7 自测
1. 写出 Dedekind 分割的四条件。为什么要求"无最大元"?
2. $\sqrt 2$ 对应哪个分割?
3. 为什么 $\alpha<\beta\iff\alpha\subsetneq\beta$?(集合包含 = 大小)
4. **LUB 证明**:为什么 $A$ 的并集就是 $\sup A$?
5. **终极**:第 8 章"假设"LUB,第 29 章"证明"它——Spivak 完成了什么哲学转变?(从公理到构造)
