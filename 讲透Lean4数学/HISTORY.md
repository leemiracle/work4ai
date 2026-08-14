# 讲透Lean4数学 · 思想史

> **一句话定位**：形式化数学 3000 年从欧几里得走到 Lean 4，但真正改变游戏的不是技术突破——是三次范式转移（Coq 的类型论根基、Lean 的社区工程、AI 与形式化的合流），每次都伴随着"谁能参与数学研究"这个根本问题的重新定义。

> **本文件不是年代史**（"1967 年 de Bruijn 发明 Automath"是事实，但不是思想史）。**本文件是思想史**——追问：为什么 de Bruijn 在 1967 年而不是 1937 年做这件事？为什么 Coq 主导了 30 年却被 Lean 超越？为什么 Mizar 拥有最大的形式化数学库却走向衰落？为什么 Fields 奖得主 Voevodsky 突然转向计算机证明？为什么 2024 年 AlphaProof 让所有人措手不及？
>
> 配套：[`00-为什么用Lean做数学.md`](00-为什么用Lean做数学.md)（范式当下）· [`../top-math-courses/HISTORY_OF_IDEAS.md`](../top-math-courses/HISTORY_OF_IDEAS.md) §⑫（数学思想史第 12 次变革）· [`../讲透AI历史/00-为什么学AI历史.md`](../讲透AI历史/00-为什么学AI历史.md)（思想史方法论）

---

## 0. 方法论：为什么形式化数学史必须是思想史

### 0.1 年代史 vs 思想史

年代史（维基百科做法）给你一条时间线：

```
1967  de Bruijn → Automath
1972  Milner   → LCF
1973  Trybulec → Mizar
1984  Coquand/Huet → Coq
2009  Voevodsky → HoTT
2013  de Moura  → Lean
2021  Scholze  → Liquid Tensor Experiment
2024  DeepMind → AlphaProof
```

**这种讲法的问题**：它让你以为历史是"一个发明接着一个发明"的线性进步——仿佛每个证明助手都是前一个的"升级版"。**真相完全不是**。

- Automath（1967）和 Mizar（1973）是**两个完全不相交的思想传统**——前者从类型论出发，后者从集合论出发，直到今天它们的哲学后裔（Lean 和……几乎没有后裔）仍在分裂。
- Coq（1984）的创立者 Thierry Coquand 在 1985 年提出 Calculus of Constructions 时，**并不是在改进 Automath**——他是在 Martin-Löf 类型论遭遇悖论后的废墟上重建。
- Lean（2013）的创立者 Leonardo de Moura **根本不是数学家**——他是 SMT 求解器 Z3 的开发者，最初的动机是软件验证，不是形式化数学。Lean 被数学家"劫持"，是一次完全的偶然。

**思想史问的问题**：

| 年代史问 | 思想史问 |
|---------|---------|
| Lean 何时诞生？2013 | **为什么** 2013 年 de Moura 选择从零开始，而不是改进 Coq？|
| Voevodsky 何时提出 HoTT？2009 | **为什么**一个 Fields 奖代数几何学会突然转向类型论？他经历了什么？|
| AlphaProof 何时拿牌？2024 | **为什么**是 Lean 而不是 Coq 成为 AI 做数学的环境？5 年前能做吗？|
| Mizar 何时衰落？2010s | **为什么**拥有最大形式化数学库的系统会衰落？技术还是社会学？|

### 0.2 库恩范式转移的适用

形式化数学史至少经历了**四次范式转移**（本文核心结构）：

| 转移 | 旧范式 | 新范式 | 触发事件 | "换问题" |
|------|--------|--------|---------|---------|
| 第一次 | 命题逻辑 / set-based | **依赖类型论** | Coq 1984 | 从"验证程序"到"作为数学基础" |
| 第二次 | 单人 / 小组形式化 | **开源社区工程** | Lean + Mathlib 2017 | 从"作坊式"到"GitHub 式" |
| 第三次 | 证明助手是小众工具 | **主流数学家入场** | Scholze 2021 / Gowers 2023 | 从"计算机科学家玩具"到"数学家武器" |
| 第四次 | 人写证明，机器验证 | **AI 生成证明，机器验证** | AlphaProof 2024 | 从"人机交互"到"神经符号合流" |

每次转移都伴随库恩式的特征：① 旧范式累积反常 ② 新范式能解释反常 ③ 两代人有不可通约的世界观。下面逐次展开。

### 0.3 本文的五条方法论原则

继承 [`讲透AI历史/00`](../讲透AI历史/00-为什么学AI历史.md)：

1. **思想史 > 年代史**：每个"突破"都问"为什么是此时"
2. **路径依赖敏感**：Lean 的胜利可能部分是偶然（如果 Buzzard 2017 年选了 Coq……）
3. **失败与成功同等重要**：Mizar 的衰落比 Lean 的崛起更有教训
4. **跨学科**：形式化数学史受数理逻辑 / 类型论 / 软件工程 / 社会学 / AI 的共同塑造
5. **批判性**：不把"赢家"当真理——Lean 当前统治可能也是暂时的

---

## 1. 前夜：de Bruijn Automath 与 LCF 谱系（1967-1984）

### 1.1 欧几里得的幽灵：形式化是数学的本能

要理解 1967 年发生了什么，必须回到公元前 300 年。

欧几里得《几何原本》做了人类思想史上第一次系统形式化：从 5 条公设 + 5 条公理出发，演绎出 465 个定理。**形式化不是计算机时代的发明——它是数学的定义本身**。Leibniz 在 17 世纪梦想一种 *characteristica universalis*（普遍表意文字），能将推理变成"计算"——他说"有了它，两个哲学家争论数学问题就像两个会计对账一样"。Hilbert 在 1900 年提出将全部数学形式化的纲领。

但有一个鸿沟：**人类的"形式化"永远不够形式**。证明里总有"显然"、"易得"、"由……直接推出"——这些词背后隐藏着无数未言明的假设。Russell 1901 年的悖论正是藏在 Frege 自认为严格的系统里。

1967 年，荷兰数学家 **Nicolaas Govert de Bruijn**（恩荷芬理工大学）跨越了这条鸿沟：他创造了 **Automath**，第一个能将数学证明完全翻译成机器可检验形式的系统。

### 1.2 de Bruijn 的三个根本贡献

**贡献一：依赖类型论**

de Bruijn 独立于 Per Martin-Löf 发明了**依赖类型论**（dependent type theory）的核心思想：**类型可以依赖于值**。

在传统集合论中，"所有自然数"是一个集合 $\mathbb{N}$，"长度为 $n$ 的向量"是一个集合 $\text{Vec}(n)$，二者之间没有形式上的"依赖"关系。但在依赖类型论中，你可以写出一个**类型族**：对于每个 $n : \mathbb{N}$，有一个类型 $\text{Vec}(\alpha, n)$，这个类型**依赖于**值 $n$。

这不是语法糖——这是**数学语言的升级**。在集合论里，"长度为 3 的向量"和"长度为 5 的向量"在形式上没有区别（都是集合）；在依赖类型论里，类型系统**内部编码了**这个区别。这意味着许多数学定理的前提条件（"设 $V$ 是 $\mathbb{R}^n$ 上的向量空间"）直接进入类型，编译器替你检查。

**贡献二：Curry-Howard 对应的实践化**

Curry（1934）和 Howard（1969）发现了一个深刻的对应：**命题即类型，证明即程序**。命题 $A \Rightarrow B$ 对应函数类型 $A \to B$；证明 $A \Rightarrow B$ 就是构造一个把 $A$ 的证明变成 $B$ 的证明的函数。de Bruijn 在 Automath 中将这个哲学变成了可用的工具。

这意味着：**证明一个数学定理 = 写一个程序**。验证证明 = 类型检查。这是所有现代证明助手（Coq / Agda / Lean）的根基。

**贡献三：de Bruijn factor**

de Bruijn 提出了一个度量形式化成本的指标：**形式化工作量 / 非形式化工作量**。在 Automath 时代，这个因子大约是 **50-100**——形式化 Landau 的《分析基础》一本书，需要原始文本几十倍的工作量。这个数字后来被称为 **de Bruijn factor**。

de Bruijn factor 是理解整个形式化数学史的关键变量：
- 1970s（Automath）：~50-100
- 1990s（Coq 早期）：~30-50
- 2010s（Lean + Mathlib）：~20（Tao 2024 估计）
- 2025+（AI 整合）：Tao 预测可能降到 < 1

**de Bruijn factor < 1 是颠覆性的**：这意味着形式化比纸笔还快，所有数学论文将默认附 .lean 文件。

### 1.3 LCF 谱系：Milner 的信任内核

在 de Bruijn 从数学一侧推动形式化的同时，计算机科学家从另一侧推动。

1972 年，**Robin Milner** 在斯坦福大学（后移至爱丁堡）开发了 **LCF**（Logic of Computable Functions）。LCF 的根本创新不是它的逻辑——而是它的**架构哲学**：

> **小信任内核 + 可扩展策略**

LCF 有一个极小的、可信的推理核心（只有几条公理和推理规则）。所有复杂的推理都通过"策略"（tactic）来完成，但策略最终必须将证明**还原为核心接受的步骤**。这意味着：**你可以信任任何复杂的策略，因为最终的正确性由小内核保证**。

这是今天所有证明助手的架构基石。Coq 的 kernel、Lean 的 kernel——都是 LCF 哲学的后裔。de Moura 后来设计 Lean 时刻意保持 kernel 极小（~6000 行 C++），正是继承了 Milner 的衣钵。

Milner 还发明了 **ML**（Meta Language）——最初是 LCF 的策略编程语言。ML 后来变成了 Standard ML、OCaml、Haskell 的祖先。**函数式编程从定理证明里诞生**——这是 AI 史常被忽视的事实。

### 1.4 LCF 的后代：HOL 家族与 Isabelle

LCF 的思想直接催生了 **HOL 家族**（Higher-Order Logic）：
- **HOL**（Mike Gordon，剑桥，1980s）：从 LCF 派生，用经典高阶逻辑
- **HOL Light**（John Harrison，1990s）：极简实现，Flyspeck 项目用
- **Isabelle**（Larry Paulson，剑桥 / Tobias Nipkow，慕尼黑，1986-）：通用框架，Isabelle/HOL 是最成功的实例

HOL 家族在**软件/硬件验证**领域极其成功（ARM 处理器验证、seL4 微内核验证），但在**纯数学形式化**上始终不如 Coq/Lean——因为经典高阶逻辑缺乏依赖类型，无法优雅表达代数结构。

### 1.5 前夜的思想遗产

到 1984 年 Coq 诞生前，形式化数学有两条平行血脉：

| 血脉 | 根基 | 代表 | 数学 vs 验证 |
|------|------|------|-------------|
| **类型论血脉** | de Bruijn / Martin-Löf | Automath → Coq → Agda → Lean | 偏数学 |
| **LCF 血脉** | Milner | LCF → HOL → Isabelle | 偏软件验证 |
| **集合论血脉** | Tarski-Grothendieck | Mizar（1973） | 偏数学，但孤立 |

**这三条血脉直到今天仍在分裂**。理解这一点至关重要：Lean 不是"更好的 Coq"——它是类型论血脉的最新迭代，而 HOL/Isabelle 至今仍是软件验证的主流。Mizar 则代表了另一条几乎死去的路。

---

## 2. Coq 革命：Calculus of Inductive Constructions（1984-2010）

### 2.1 为什么是 1984 年

1984 年，**Thierry Coquand** 和 **Gérard Huet** 在法国 INRIA 启动了 Coq 项目。要理解"为什么是此时"，需要回到一个危机。

1971 年，瑞典逻辑学家 **Per Martin-Löf** 提出了一个雄心勃勃的直觉主义类型论，旨在作为"构造性数学的统一基础"。但 1972 年，Jean-Yves Girard 发现 Martin-Löf 的系统包含一个**悖论**（Girard 悖论，类似于 Russell 悖论的类型论版本）。Martin-Löf 的原始系统崩溃了。

这次危机催生了两条出路：
1. **Girard 自己**：系统 F（多态 λ-演算），后来发展成 System Fω
2. **Coquand（1985）**：**Calculus of Constructions**（CoC）——将 Girard 的系统与依赖类型论融合，创造一个**可证明一致**的系统

CoC 的关键创新是**命题和类型完全统一**（propositions-as-types 的极端版本）。1988 年，**Christine Paulin-Mohring** 和 Coquand 加入了**归纳构造**（inductive constructions），形成了 **CIC**（Calculus of Inductive Constructions）——这就是 Coq 的逻辑基础，也是后来 Lean 的逻辑基础的直系祖先。

### 2.2 Coq 的黄金时代：两大里程碑

Coq 在 1990s-2010s 取得了两个震动数学界的形式化成就：

**四色定理（2005）**

2005 年，**Georges Gonthier**（Microsoft Research）在 Coq 中完整形式化了四色定理的证明。四色定理（1976 年由 Appel-Haken 用计算机辅助证明）长期被数学界"不情愿地接受"——因为原始证明涉及 1936 个构形的计算机枚举，人类无法逐个检查。Gonthier 的形式化**不仅验证了这 1936 个构形，还验证了整个证明的逻辑结构**。

**这是形式化数学被主流数学界认真对待的起点**。Gonthier 之后受邀到 IAS 做报告——形式化不再是"玩具"。

**Feit-Thompson 定理（2012）**

Gonthier 团队更进一步：2012 年完成了 **Feit-Thompson 定理**（奇数阶群可解定理）的完整 Coq 形式化。这个定理是有限群论的基石，证明长达 255 页（原始论文），涉及大量群论、表示论、数论。形式化花了 **6 年**、**15 人团队**、**170 个引理**、**约 4 万行 Coq 代码**。

Feit-Thompson 形式化的意义在于：它证明了一个**非平凡的、数学家认为"重要"的定理**可以被完整形式化。四色定理可能被认为"特殊"（涉及大量计算），但 Feit-Thompson 是"真正的数学"。

### 2.3 Coq 为什么没能成为"最终答案"

Coq 是伟大的——但它有几个结构性问题，最终导致它在 2010s 后期被 Lean 超越：

**问题一：自动化不足**

Coq 的 tactic 系统强大但碎片化。没有像 Lean 的 `ring` / `nlinarith` 那样统一、高效的代数自动化。一个简单的代数等式（如 $(a+b)^2 = a^2 + 2ab + b^2$）在 Coq 里可能需要多行 tactic。这直接推高了 de Bruijn factor。

**问题二：语言设计不够现代**

Coq 的 Gallina 语言和 tactic 语言（Ltac）是两个不同的世界。Ltac 本身是一种不类型安全的"小语言"，难以调试和维护。Coq 社区后来发展了 Ltac2、SSR Reflect 等，但碎片化严重。

**问题三：库的碎片化**

Coq 有多个数学库（Coq 标准库、SSReflect / MathComp、UniMath……）互不兼容。一个定理在 MathComp 里，另一个在标准库里，你很难同时用。**没有一个统一的、社区维护的大库**。

**问题四：社区规模**

Coq 社区主要集中在法国（INRIA 传统）。虽然全球都有用户，但社区规模始终不如后来的 Mathlib。部分原因是 Coq 的学习曲线更陡峭。

> ⚠️ **批判性提醒**：这不是说 Coq "失败"了。Coq 仍在使用，MathComp 仍在发展。但在"形式化数学"这个特定赛道上，Lean 在 2020 年后占据了主导叙事。Coq 在验证领域（特别是 CompCert 形式化 C 编译器）仍不可替代。

### 2.4 思想史反思：Coq 的遗产

Coq 对形式化数学的贡献是奠基性的：
1. **确立了 CIC 作为数学基础的可行性**——Lean 的逻辑基础几乎是 CIC 的变体
2. **证明了非平凡大定理可以被形式化**——四色、Feit-Thompson
3. **培养了第一代形式化数学家**——Lean 社区的很多人（如 Mario Carneiro）有 Coq 背景
4. **积累了教训**——库碎片化、自动化不足、语言不统一——这些教训直接指导了 Lean 的设计

**Coq 不是被 Lean "打败"的——Coq 的遗产被 Lean "继承"了**。

---

## 3. HoTT 与 Voevodsky 的推动（2005-2017）

### 3.1 一个 Fields 奖得主的"皈依"

**Vladimir Voevodsky**（1966-2017），Fields 奖得主（2002，代数几何/motivic 同伦论），普林斯顿 IAS 教授。他是 20 世纪末最深刻的代数几何学家之一。

大约 2005 年，Voevodsky 发现自己的某些证明**可能有错误**。这不是自我怀疑——而是确切的。他后来在演讲中坦承，他 1990 年代的一篇重要论文（关于 2-范畴的稳定性）被同行发现了一个严重缺口，而他自己无法确认修改是否正确。

**一个 Fields 奖得主无法确信自己的证明是对的**——这个震撼驱使他转向形式化。

### 3.2 同伦类型论的诞生

Voevodsky 在 Coq/Aga 中形式化自己的工作时，发现标准类型论与同伦论之间有惊人的联系：

- **类型** 对应 **空间**
- **等式**（$a = b$）对应 **路径**（从 $a$ 到 $b$ 的连续映射）
- **等式的等式** 对应 **同伦**（路径之间的形变）

这个 **"同伦类型论"（Homotopy Type Theory, HoTT）** 的核心是 **univalence axiom**（单一性公理）：**同构的东西相等**。形式化地说，$(A \simeq B) \simeq (A = B)$——两个同构的类型是"相等"的。

这在集合论框架里是不可能的（两个同构但不相同的集合在 ZFC 里不相等）。但在 HoTT 中，"相等"被重新诠释为"路径"，而同构恰好提供了路径。**HoTT 为数学提供了一种新的基础——一种"结构主义"的基础，数学对象由其结构而非载体定义**。

### 3.3 IAS 特殊年与 HoTT Book（2012-2013）

2012-2013 年，Voevodsky 在 IAS 组织了 **"Univalent Foundations"特殊年**。一群类型论学家、范畴论学家、拓扑学家聚集在一起，合著了 **《Homotopy Type Theory: Univalent Foundations of Mathematics》**（"HoTT Book"）。这本书不是传统教科书——它是几十位作者在 GitHub 上协作完成的，本身就是形式化社区协作模式的早期实验。

HoTT Book 的影响巨大：它将类型论从逻辑学家的小众领域带到了主流数学家的视野。**许多数学家第一次认真对待形式化基础，是因为 HoTT**。

### 3.4 HoTT 的挫折与遗产

HoTT 没有成为数学的主流基础——原因复杂：

1. **一致性证明的困难**：Univalence 公理的一致性需要模型论证明（Voevodsky 本人用 cubical sets 做了，但技术上极复杂）
2. **与 CIC 的张力**：经典 Coq/Lean 的归纳类型与 univalence 有微妙冲突
3. **Voevodsky 的去世**（2017 年，51 岁）：失去了旗手
4. **Lean 的转向**：de Moura 最初计划在 Lean 中原生支持 HoTT，但最终 Lean 4 放弃了原生 HoTT 支持，转向经典数学

但 HoTT 的遗产深远：
- **cubical type theory** 成了 Agda 的核心特色，至今活跃
- **Voevodsky 亲自用 Coq 形式化了大量代数几何**（UniMath 库），激励了后来的 Lean 代数几何形式化
- **最重要的是**：Voevodsky 以 Fields 奖得主的身份为形式化数学"背书"——他让主流数学界意识到，**形式化不是计算机科学家的玩具，而是数学家的生存工具**。没有 Voevodsky 的"皈依"，很难想象后来 Scholze / Gowers / Tao 会如此认真地对待 Lean。

### 3.5 思想史的反常识：HoTT 的失败比成功更重要

HoTT 作为"数学新基础"的愿景没有实现——但它的失败比成功更有教育意义：

> **反常识**：一个被 Fields 奖得主全力推动、有 IAS 背书、有畅销书传播的新数学基础，**没有**取代集合论。这说明数学基础的变革比技术突破更依赖社会学因素（社区接受度、教材生态、激励机制）。

这直接预示了后来 Lean 的策略：**不试图改变数学的基础（如 HoTT），而是用现有数学家的语言（经典逻辑 + 集合论直觉）形式化他们的工作**。Lean 选择经典逻辑而非构造逻辑、选择 ZFC 风格而非 HoTT 风格——这是它比 Coq/Agda 更快被主流数学家接受的关键。

---

## 4. 第一次范式转移：Lean 出现（2013）

### 4.1 de Moura 的非典型出身

**Leonardo de Moura** 不是数学家，也不是逻辑学家。他的背景是 **SMT（Satisfiability Modulo Theories）求解器**——他在微软研究院开发的 **Z3** 是世界上最强大的自动定理证明器之一。

SMT 求解器的哲学与证明助手完全不同：SMT 追求**全自动**（给定一个命题，机器自动判定真假），而证明助手（Coq/Isabelle）追求**人机交互**（人引导，机器验证中间步骤）。de Moura 的愿景是**融合两者**：

> 能不能创造一个证明助手，既有 Coq 的依赖类型论根基，又有 Z3 级别的自动化？

这个愿景驱动了 Lean 的设计。**Lean 不是为了形式化数学而生的——它是为了"更好的自动推理"而生的**。Lean 被数学家"劫持"用于形式化数学，是后来社区选择的结果，不是 de Moura 的原始意图。

### 4.2 Lean 的设计哲学

de Moura 在 Lean 中做了几个关键设计决策，每一个都是对 Coq 的直接回应：

| 设计决策 | Coq 的做法 | Lean 的做法 | 动机 |
|---------|-----------|------------|------|
| 逻辑 | 经典或构造，用户选 | 经典逻辑为默认 | 数学家用经典逻辑 |
| 类型论 | CIC | CIC 变体 + 商类型 | 更好地表达经典数学 |
| 元编程 | Ltac（独立小语言） | Lean 自身（elab） | 用 Lean 写 Lean 的 tactic |
| 自动化 | 碎片化 tactic | SMT 风格统一自动化 | de Moura 的 Z3 经验 |
| Kernel | 中等大小 | 极小（~6000 行 C++） | Milner 的 LCF 哲学 |

其中最革命性的是**元编程**：Lean 4 的 tactic 语言就是 Lean 本身。你可以用 Lean 写 Lean 的 tactic，编译、调试、优化都用同一套工具链。这彻底解决了 Coq 的 "Ltac 是另一个世界" 的痛点。

### 4.3 Lean 早期（2013-2016）：无人问津的开端

一个反常识的事实：**Lean 的头三年几乎无人关心**。

Lean 1（2013-2014）和 Lean 2（2015）几乎只在微软研究院内部使用。形式化数学社区主流仍在用 Coq 和 Isabelle。de Moura 的论文在 SMT/自动化社区受关注，但在数学社区几乎无回响。

转折点是 **2017 年 Kevin Buzzard 的介入**。

### 4.4 Buzzard：从 Coq 到 Lean 的叛逃

**Kevin Buzzard**，帝国理工学院代数几何教授（伦敦数学会 Senior Berwick 奖得主），是第一个"主流数学家"级别的 Lean 推动者。

Buzzard 最初尝试用 Coq 形式化自己的工作（关于 perfectoid 空间），但很快受挫于 Coq 的学习曲线和库碎片化。2017 年，他尝试了刚发布的 Lean 3——立即被吸引。他在博客中写道（大意）：

> Lean 3 的设计感觉就像"有人真正想过数学家需要什么"。

Buzzard 随后在帝国理工开设了 **"Formalising Mathematics"** 课程，带领本科生用 Lean 做数学。更重要的是，他开始**在纯数学社区布道**——在数学会议上演示 Lean，说服同行"这不是玩具"。

**Buzzard 的角色不是技术贡献者——他是社会催化剂**。没有 Buzzard，Lean 可能仍是微软研究院的一个内部项目。

> 💡 **路径依赖分析**：如果 Buzzard 2017 年没有从 Coq 转向 Lean，而是在 Coq 社区投入同等的布道精力，今天的形式化数学格局可能完全不同。Buzzard 在 Lean 社区的地位——就像 Hinton 之于深度学习：不是唯一的技术贡献者，但是不可替代的旗手。

---

## 5. 第二次范式转移：Mathlib 社区（2017-）

### 5.1 Mathlib 的诞生：从"库"到"运动"

2017 年，随着 Lean 3 发布和 Buzzard 的加入，**Mathlib** 开始形成。最初只是几个人贡献的数学引理集合，但它很快演变成了一场**社区运动**。

Mathlib 的核心人物包括：
- **Mario Carneiro**（卡内基梅隆 PhD，后来在 Carnegie Mellon）：Lean 元理论专家，写了 Lean 3 到 4 迁移工具，是 Mathlib 架构的关键设计者
- **Johannes Hölzl**（前 Coq 用户）：从 Isabelle 带来了大量测度论/概率论的形式化经验
- **Sébastien Gouëzel**（南特大学，数学教授）：带来了分析学/度量几何的形式化
- **Jeremy Avigad**（CMU，逻辑学家）：哲学+实践的双重推动
- **Patrick Massot**（巴黎萨克雷，拓扑学家）：Natural Number Game 的作者之一
- **Reid Barton**（IMO 金牌 → 数学家）：范畴论形式化

这个团队的关键特征是**跨学科**：有纯数学家、有逻辑学家、有计算机科学家。这和 Coq 社区（偏法国 + 偏 CS）形成对比。

### 5.2 Mathlib 的工程哲学：GitHub 式数学

Mathlib 不是传统的数学库——它是一个**开源软件项目**。它的运作方式与 Linux 内核、PyTorch 类似：

| 维度 | 传统数学 | Mathlib |
|------|---------|---------|
| 贡献模式 | 论文（单人/小组）| GitHub PR（社区） |
| 审查机制 | 同行评审（期刊）| CI/CD + 维护者 review |
| 版本管理 | arXiv v1/v2/v3 | Git |
| 重复利用 | 引用论文 | `import Mathlib` |
| 贡献者数量 | 1-3 人/论文 | 100+ 活跃贡献者 |
| 累积速度 | 线性 | 指数（2020: ~10 万行 → 2025: 150 万+ 行）|

**这是数学研究模式的根本变革**。传统数学论文是"一次性"产出——写完发表后就冻结。Mathlib 的贡献是"活的"——被后续 PR 持续改进、重构、优化。你今天提交的引理，明天可能被另一个人简化，后天被第三个人推广。

### 5.3 为什么 Mathlib 成功而 MML 衰落

Mizar Mathematical Library（MML）在 1990s-2000s 曾是最大的形式化数学库，有超过 10000 个定义和定理。但它逐渐衰落了。比较 Mathlib 和 MML：

| 维度 | Mizar MML | Mathlib |
|------|-----------|---------|
| 开源 | 早期不完全开源 | 完全开源（Apache 2.0） |
| 社区地理集中度 | 波兰（比亚韦斯托克）为主 | 全球（Zulip 实时协作） |
| 工具链现代化 | 缓慢 | 持续迭代（Lean 3 → 4） |
| 吸引新用户 | 语法独特、学习曲线陡 | 有 NNG 等游戏化入门 |
| 与主流数学的连接 | 弱（Mizar 用户多为形式化专家）| 强（Tao/Gowers/Scholze 用 Lean） |

**核心教训**：技术优势不能保证生态胜利。Mizar 在某些形式化技术上不输 Lean，但它的社会学失败（封闭社区、地理集中、工具链陈旧）决定了它的衰落。**形式化数学的胜利不只是技术胜利，更是社区工程胜利**。

### 5.4 Lean 4（2021）：用 Lean 写 Lean

2021 年，Lean 4 发布。最引人注目的不是任何单一功能——而是 **Lean 4 的编译器是用 Lean 4 本身写的**。

这是"自举"（bootstrapping）——一门编程语言用自己来实现自己。C 用 C 写、OCaml 用 OCaml 写——Lean 也加入了这个行列。

自举的意义：
1. **元编程无缝**：tactic 就是 Lean 函数，调试 tactic 就是调试 Lean 程序
2. **性能**：Lean 4 代码可以编译成 C 然后编译成原生代码，速度远超 Lean 3（解释执行）
3. **一致性**：只有一套语言、一套类型系统、一套工具链

代价是**迁移痛苦**：从 Lean 3 到 Lean 4 是一次大规模 breaking change。Mathlib 3 → Mathlib 4 的迁移花了社区超过一年（`mathport` 工具自动翻译了大部分，但大量需要手动修复）。这次迁移中一些贡献者离开了——但社区整体存活并继续增长，证明了 Mathlib 社区的韧性。

### 5.5 思想史反思：社区比技术更重要

第二次范式转移的核心教训：

> **反常识**：Lean 超越 Coq 的关键不是 Lean 的逻辑更好或自动化更强——而是 Mathlib 社区的工程实践更好。GitHub + CI/CD + Zulip 的开源协作模式，比任何技术优势都更能吸引和留住贡献者。

这与 AI 史上的教训一致：PyTorch 超越 TensorFlow 不是因为 PyTorch 技术更好（早期 PyTorch 在性能上不如 TF），而是因为 PyTorch 的 API 更 Pythonic、社区更友好。**技术革命的胜负往往在社会学层面决定**。

---

## 6. 第三次范式转移：大数学家入场（2021-2023）

### 6.1 Scholze 与 Liquid Tensor Experiment（2021）

**Peter Scholze**，Fields 奖得主（2018，波恩大学），29 岁获 Fields 奖，被认为是当代最深刻的数学家之一。

2020 年底，Scholze 在博客上发出了一个不寻常的请求：他提出了关于 **condensed mathematics**（凝聚数学）的一个核心技术定理（"液体张量实验"，Liquid Tensor Experiment），并**公开邀请形式化社区用 Lean 验证它**。

这极其不寻常：
- Scholze 是当时在世最伟大的数学家之一
- 他主动要求计算机验证自己的工作
- 这个定理极难——涉及 condensed abelian groups、liquid tensor 乘积，是 Scholze 自己发展的前沿理论

**为什么 Scholze 要这么做**？他在博客中解释：condensed mathematics 的证明涉及如此多层次的抽象，他**自己都无法 100% 确信没有错误**。他想让机器来检查。

2021-2022 年，Johan Commelin（阿姆斯特丹大学）领导的团队在 Lean 中完成了形式化。Scholze 在完成后写道：

> "形式化过程中，我们在原始证明中发现了几处可以简化的地方。形式化让证明变得更好了。"

**Liquid Tensor Experiment 的历史意义**：这是第一次**一个 Fields 奖得主主动发起的前沿研究级定理的形式化**。它向整个数学界发出信号：形式化不是"验证已知的经典定理"，而是"验证正在发展的前沿数学"。

### 6.2 Gowers 与 Polynomial Freiman-Ruzsa（2023）

**Timothy Gowers**，Fields 奖得主（1998，剑桥），以"大众数学"博客和 Polymath 协作数学项目闻名。

2023 年 11 月，Gowers 和 collaborators 证明了 **Polynomial Freiman-Ruzsa (PFR) 猜想**——一个加性组合论中的重要猜想。然后他们做了一件前所未有的事：**在证明发布后的 3 周内，用 Lean 完整形式化了它**。

PFR 形式化的团队包括 Gowers、Ben Green（Tao 的长期合作者）、Tao 本人，以及约 20 名 Lean 社区贡献者。整个过程通过 Zulip 实时协作，**3 周完成**。

这在 2010 年是不可想象的——那时形式化一个定理需要数月甚至数年。PFR 的 3 周完成标志着 de Bruijn factor 的显著下降——部分原因是 Mathlib 已经有了大部分需要的引理（"站在巨人的肩膀上"）。

### 6.3 Equational Theories Project（2024-2025）

2024 年 9 月，Tao 发起了 **Equational Theories Project**：系统形式化 4694 个 magma 方程定律之间的所有蕴含关系——总共 **22,028,942 条**。

项目组织：
- 非形式化阶段（2 个月）：确定蕴含关系，纸笔 + 计算
- 形式化阶段（5 个月）：50+ 人协作，在 Lean 中逐条验证
- 2025 年 4 月完成

**这是"大规模协作数学"的范式样本**。Tao 在博客中说："未来类似项目会越来越多——一个数学领域的完整'蕴含图谱'可以被系统形式化。"

### 6.4 Buzzard 的 FLT 五年计划（2024-）

2024 年，Buzzard 在帝国理工正式启动 **Fermat 大定理形式化计划**：用 Lean 完整形式化 Wiles 1995 年的证明（100+ 页，涉及模形式、Galois 表示、椭圆曲线……）。

预计 5 年完成。这个项目如果成功，将是人类历史上形式化的最深的数学定理——它将把整个数论的工具链（模形式理论、Hecke 代数、Galois 表示……）带入 Lean。

### 6.5 思想史反思：从"验证"到"创造"

第三次范式转移的核心变化：

> **反常识**：形式化数学最初的目标是"验证已有证明"（四色、Feit-Thompson）。但到 2020s，它的角色变成了"参与数学创造本身"。Scholze 形式化时发现证明可以简化；Gowers 在形式化 PFR 时发现了新路径；Equational Theories Project 的形式化过程**本身就是数学研究**。

形式化从"事后的保险"变成了"过程的一部分"。这个转变的意义不亚于从"论文发表后才同行评审"到"Git PR 式持续评审"。

---

## 7. 第四次范式转移：AI + Lean（2024-）

### 7.1 AlphaProof：神经符号的里程碑

2024 年 7 月，DeepMind 宣布 **AlphaProof** 在 IMO 2024（国际数学奥林匹克）中达到**银牌水平**（28/42 分，银牌线 22 分）。

AlphaProof 解出的题目：
- **代数 P1、P2**：相对标准
- **代数 P6**：**最难的题目**，全球只有 5 人满分
- 结合 AlphaGeometry 2 解 **几何 P4**

AlphaProof 的架构是**神经符号**的完美范例：

```
自然语言问题
    ↓ （LLM 翻译）
Lean 形式化命题
    ↓ （RL 搜索证明）
Lean 证明
    ↓ （Lean kernel 验证）
✓ 可信证明
```

核心组件：
1. **LLM（Gemini 系）**：将自然语言数学问题翻译成 Lean 命题；生成证明思路
2. **AlphaZero 式 RL**：在 Lean 中搜索证明——自我对弈（生成证明 → 验证 → 强化）
3. **Lean kernel**：最终验证——不可欺骗的 ground truth

**为什么 AlphaProof 用 Lean 而不是 Coq**？
1. Lean 的 Mathlib 已有大量数学基础设施（IMO 涉及的代数、数论、组合）
2. Lean 的语法更适合 LLM 学习（更规则化）
3. Lean 社区已建立了 miniF2F 等 benchmark
4. DeepMind 与 Lean 社区有直接合作（多位 Lean 开发者参与）

**AlphaProof 的本质洞察**：形式化数学提供了一个**奖励不可欺骗**的 RL 环境。在围棋/国际象棋中，AI 通过自我对弈变强；在数学中，Lean kernel 扮演"裁判"，AI 通过"尝试证明 → 被 kernel 接受/拒绝 → 强化"变强。**这是 RL 应用于纯推理领域的首个里程碑级成功**。

### 7.2 为什么是 2024 年而不是 2019 年

AlphaProof 的成功需要三个条件同时成熟：

| 条件 | 2019 年状态 | 2024 年状态 |
|------|-----------|------------|
| LLM 能力 | GPT-2 级别，无法理解数学 | Gemini 级别，能翻译数学问题 |
| Lean 生态 | Mathlib 不够丰富 | Mathlib 150 万行，IMO 所需基础设施齐全 |
| RL + 搜索 | AlphaGo 证明了可行性，但数学更难 | AlphaZero 式 RL + Lean 的组合首次可行 |

**2019 年做 AlphaProof 会失败**——LLM 不够强、Mathlib 不够丰富。2024 年三个条件同时到位——这是一次"时机成熟"的爆发，和 2012 年 AlexNet 一样。

### 7.3 神经符号 AI 的合流

AlphaProof 代表了一个更大的趋势：**神经方法（深度学习）与符号方法（形式逻辑）的合流**。

在 AI 史上，连接主义（神经网络）和符号主义（逻辑推理）是两个对立的阵营（见 [`讲透AI历史/00`](../讲透AI历史/00-为什么学AI历史.md) §二）。AlphaProof 让两者协作：
- **神经网络**负责"直觉"（猜测证明方向、翻译自然语言）
- **符号系统**（Lean）负责"严格"（验证每一步、保证正确性）

这与人类数学家的思维方式惊人地一致：**直觉引导 + 严格验证**。Tao 在 2025 年的演讲中说，AI 辅助数学的理想状态就是"像有一个不知疲倦的博士后"——它有直觉（LLM），又不出错（Lean 验证）。

### 7.4 2025-2026 的前沿

AlphaProof 之后的发展：
- **AlphaProof Nexus**（2026）：开始攻击 Erdős 未解问题和 OEIS 问题
- **Tao《Analysis I》Lean companion**（2025-05）：整本实分析教材 Lean 化，留 sorry 让学生填
- **miniF2F / ProofNet 等 benchmark**：成为 AI-for-math 的标准评测
- **Lean Copilot / Copra 等 AI 辅助 Lean 工具**：将 LLM 集成到 Lean 编辑器中

Tao 预测 de Bruijn factor 在未来 5-10 年可能降到 < 1。如果成真，**所有数学论文将默认形式化**——这是数学研究方式的根本变革。

### 7.5 思想史反思：AI 不是形式化的替代品

> **反常识**：很多人担心 AI 会"取代"形式化——"如果 AI 能直接做数学，为什么还要 Lean？"。恰恰相反：**AI 让形式化更重要了**。因为 AI 生成的证明**必须**被验证（它会出错、会幻觉），而 Lean kernel 是唯一不可欺骗的验证器。AlphaProof 不是 Lean 的竞争者——它是 Lean 的最大用户。

AI 与形式化的关系是**共生**的：
- AI 没有 Lean → 无法训练（没有可靠奖励信号）
- Lean 没有 AI → de Bruijn factor 始终 ~20（太慢）
- **两者结合 → de Bruijn factor → 1**

---

## 8. 思想史反思：5 个反常识

### 反常识 1：Lean 不是"更好的 Coq"——它是被数学家"劫持"的软件验证工具

**官方叙事**：de Moura 创造 Lean 来形式化数学。

**真相**：de Moura 是 SMT/Z3 专家，创造 Lean 的原始动机是**更好的自动推理**。形式化数学是 Buzzard、Mathlib 社区"发现"Lean 的用途。de Moura 的贡献是技术平台；数学社区的贡献是定义了平台被用来做什么。

**教训**：技术工具的最终用途往往与创造者的意图不同。不要用"意图"来评价工具——用"实际影响"。

### 反常识 2：拥有最大数学库的系统（Mizar）可以衰落

**官方叙事**：技术更好 → 赢得竞争。

**真相**：Mizar 在 2000 年代拥有最大的形式化数学库，但它衰落了——不是因为技术落后，而是因为社区封闭、地理集中、开源滞后。**形式化数学的竞争不只是逻辑/自动化竞争，更是社会学竞争**。

**教训**：开源 + 全球社区 + 低门槛入门 > 技术优势。这与 AI 史的教训一致（PyTorch vs TensorFlow）。

### 反常识 3：Fields 奖得主转向形式化的动机是恐惧，不是信仰

**官方叙事**：Scholze / Voevodsky / Gowers 因为"信仰"形式化而推动它。

**真相**：他们转向形式化的直接动机是**发现自己或同行的证明可能有错**。Voevodsky 发现了自己的错误；Scholze 无法确信 condensed math 的证明。**推动形式化的不是哲学信仰，而是对错误的恐惧**。

**教训**：最可靠的技术采纳动机不是"理想"，而是"刚需"。

### 反常识 4：HoTT 的"失败"比成功更重要

**官方叙事**：HoTT 是形式化数学的重大进展。

**真相**：HoTT 作为"数学新基础"失败了——它没有取代集合论。但它的失败教会了 Lean 社区一个关键教训：**不要试图改变数学家的语言，用他们的语言形式化他们的工作**。Lean 选择经典逻辑而非 HoTT——这正是它比 Coq/Agda 更快被主流接受的原因。

**教训**：技术革命有时需要向旧范式"妥协"才能成功。

### 反常识 5：形式化数学已有 2300 年——计算机只是让它变得可执行

**官方叙事**：形式化数学是计算机时代的发明。

**真相**：欧几里得在公元前 300 年就在做形式化数学。de Bruijn 的 Automath 不是"发明"了形式化——它让形式化变得**可执行**（机器自动验证）。这个区分很重要：形式化数学的历史不是"从 1967 年开始"，而是"从欧几里得开始，在 1967 年获得了执行能力"。

**教训**：理解技术变革需要理解它延续了什么、改变了什么。形式化不变的是"严格证明"的理想；变的是"谁来检查严格性"——从人脑到机器。

---

## 9. 关键人物谱系

### 9.1 技术血脉

```
de Bruijn (Automath 1967)          Martin-Löf (类型论 1971)
         \                           /        |
          \                         /    Girard 悖论 (1972)
           \                       /          |
            Coquand (CoC 1985) ────┘     System F (Girard)
                    |
              Paulin-Mohring (归纳构造)
                    |
               CIC (1988)
             /        \
          Coq (1984→)  de Moura 的灵感来源
                            |
                      de Moura (Lean 2013, Z3)
                            |
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
         Buzzard       Carneiro      Mathlib 社区
        (布道者)      (架构师)       (2017-)
              ↓             ↓             ↓
         Scholze       Gowers        Tao
        (2021)         (2023)        (2024-)
                            ↓
                     AlphaProof (DeepMind 2024)
```

### 9.2 LCF 血脉（平行）

```
Milner (LCF 1972, Edinburgh)
         |
    ┌────┴────┐
    ↓         ↓
  Gordon    Paulson
  (HOL)    (Isabelle, 1986)
    |         |
 Harrison   Nipkow
(HOL Light) (Isabelle/HOL)
    |
  Hales (Flyspeck/Kepler 2014)
```

### 9.3 集合论血脉（衰落）

```
Trybulec (Mizar 1973, Białystok)
         |
    Mizar MML (1980s-2010s)
         |
      (衰落)
```

### 9.4 人物速写

| 人物 | 角色 | 核心贡献 | 类比 |
|------|------|---------|------|
| de Bruijn | 先知 | 依赖类型论 + de Bruijn factor | Turing（定义了游戏的规则）|
| Milner | 架构师 | LCF 小信任内核 + tactic | von Neumann（计算机架构）|
| Coquand | 重建者 | CIC | Church（λ-演算）|
| Voevodsky | 皈依者 | HoTT + 为形式化背书 | Hinton（为深度学习背书）|
| de Moura | 工程师 | Lean + SMT 自动化 | Linus Torvalds（造工具）|
| Buzzard | 布道者 | 将 Lean 推入主流数学 | Karpathy（为 AI 布道）|
| Scholze | 破壁人 | 前沿研究级形式化 | ——（无类比，太独特）|
| Gowers | 协作先驱 | PFR 快速形式化 | ——|
| Tao | 集大成者 | 多项目 + 预言家 | ——|
| Carneiro | 系统架构师 | Lean 元理论 + Mathlib 架构 | ——|

---

## 10. 失败方向：被淘汰的和未实现的

### 10.1 Mizar 的衰落

**Mizar**（1973，Andrzej Trybulec，波兰比亚韦斯托克大学）曾拥有最大的形式化数学库。基于 Tarski-Grothendieck 集合论，语法类似自然语言数学。

衰落原因：
1. **开源滞后**：Mizar 系统本身在很长时间内不是完全开源的，阻碍了社区参与
2. **地理集中**：核心开发者集中在波兰，缺乏全球社区
3. **工具链陈旧**：缺乏现代 IDE 集成、CI/CD、版本管理
4. **语法独特**：Mizar 语法与任何主流编程语言都不像，学习成本高
5. **没有"明星数学家"背书**：没有 Buzzard 级别的人物为 Mizar 布道

**教训**：在形式化数学领域，社区工程 > 技术优势。Mizar 在某些形式化技术上不输 Lean，但它的社会学失败决定了衰落。

### 10.2 NuPRL 的未竟之志

**NuPRL**（康奈尔大学，Constable 等，1980s-）是一个技术上极其精致的构造性类型论证明助手。它比 Coq 更早地实现了依赖类型论 + tactic 系统，并发展了独特的"refinement logic"。

但 NuPRL 从未获得主流采用：
- 学术项目性质（依赖少数教授的 grant）
- 没有形成社区库
- 竞争不过 Coq（INRIA 的工业化支持）

**教训**：学术项目难以与有机构持续支持的工业/半工业项目竞争。

### 10.3 PVS 的退潮

**PVS**（SRI International，1990s）曾是形式化验证的主流工具，广泛应用于航空航天、硬件验证。但 2010s 后活跃度下降，被 Coq/Isabelle 替代。

衰落原因：商业实验室项目（SRI）的持续性不如开源社区；缺乏新鲜血液。

### 10.4 Lean 中 HoTT 的放弃

de Moura 最初计划在 Lean 中原生支持 HoTT。Lean 2 有实验性 HoTT 支持。但 Lean 3/4 放弃了原生 HoTT，转向经典数学。

原因：
1. HoTT 与 Lean 的 quotient 类型有技术张力
2. HoTT 社区规模太小，不值得维护成本
3. 主流数学家不需要 HoTT

**教训**：技术上的"优雅"（HoTT 作为数学基础）不敌社会学上的"实用"（数学家需要经典逻辑）。

### 10.5 Coq/Lean 之间的迁移成本

形式化数学的历史充满了"沉没成本"——一旦你在 Coq 中形式化了大量工作，迁移到 Lean 极其痛苦。UniMath（Voevodsky 的 Coq 库）无法迁移到 Lean；MathComp（Coq 的数学库）与 Mathlib（Lean 的数学库）互不兼容。

**教训**：在生态竞争早期，技术选择有巨大的路径锁定效应。今天选 Lean 的人会越来越倾向于继续用 Lean——不是因为 Lean 最好，而是因为迁移成本太高。

---

## 11. 路径依赖与偶然性

### 11.1 "如果"反事实分析

**如果 Buzzard 2017 年没有转向 Lean……**

Buzzard 最初是 Coq 用户。如果他没有被 Lean 3 吸引，而是在 Coq 社区投入同等的布道精力，今天的格局可能完全不同。Buzzard 的帝国理工团队 + Coq 可能足以让 Coq 成为"主流数学家用的证明助手"。Lean 可能仍是微软的内部项目。

**如果 Voevodsky 没有在 2017 年去世……**

Voevodsky 去世时 51 岁，正处于学术巅峰。如果他还活着，他可能会：
- 推动 cubical type theory 进入主流
- 可能让 HoTT 成为 Coq/Lean 的标准特色
- 可能创办一个以 HoTT 为基础的新证明助手

Voevodsky 的去世是形式化数学界的重大损失——HoTT 失去了最有力的旗手。

**如果 de Moura 没有离开微软研究院……**

de Moura 后来离开了 MSR（先后去了 AWS 和 CMU）。如果他留在 MSR，Lean 可能有更多企业资源支持——但也可能更受企业战略影响。离开让 Lean 更"社区化"，但减少了资金稳定性。

**如果 AlphaProof 选择 Coq 而不是 Lean……**

如果 DeepMind 在 2022 年选择 Coq 作为 AlphaProof 的环境（完全可能——Coq 的 MathComp 在某些领域比 Mathlib 更成熟），那么今天 Coq 可能重新崛起。AlphaProof 的选择部分基于 Lean 社区的 miniF2F benchmark 和更好的工具链——但这些优势是累积的、可逆转的。

### 11.2 必然 vs 偶然

| 发展 | 必然性（迟早会发生）| 偶然性（具体时间/形式不确定）|
|------|------------------|------------------------|
| 依赖类型论证明助手 | 必然（de Bruijn/Martin-Löf 已铺路）| Coq 的具体形式（CIC）是偶然 |
| 社区驱动的数学库 | 必然（GitHub 时代迟早到来）| Mathlib 具体在 Lean 上是偶然 |
| Fields 奖得主入场 | 必然（迟早有人带头）| Scholze 在 2021 年带头是偶然 |
| AI + 形式化 | 必然（技术趋势）| AlphaProof 2024 拿 IMO 银牌是偶然 |
| Lean 成为主流 | **不确定**——可能是 Coq 或其他 | Buzzard 选了 Lean 是关键偶然 |

**核心洞察**：形式化数学的整体发展是必然的（技术、社区、AI 三重推动），但 Lean 的具体主导地位是偶然的——关键转折点（Buzzard 2017 年的选择）完全可以走另一条路。

---

## 12. 开放问题

### Q1：Lean 的统治会持续多久？

历史规律：Coq 统治了约 25 年（1989-2015）被 Lean 超越。Lean 从 2017 年开始崛起，目前约 8 年。如果历史重演，Lean 的统治可能在 2030-2040 年代被新系统挑战。

可能的挑战者：
- **AI 原生证明助手**：不基于传统类型论，而是为 AI 推理优化的新逻辑系统
- **统一系统**：融合 Coq + Lean + Isabelle 优势的系统（技术上极难，但不是不可能）
- **量子计算的影响**：如果量子计算改变密码学/数论，可能催生新的形式化需求

### Q2：形式化会成为所有数学论文的标准吗？

Tao 预测 de Bruijn factor < 1 后会。但社会学阻力巨大：
- 大部分数学家不会 Lean
- 形式化耗时（即使 factor < 1，也需要学习成本）
- 期刊/tenure 体制不奖励形式化

可能的过渡：先在特定领域（代数/数论/组合）成为标准，再逐步扩散。分析/PDE/几何领域由于 Mathlib 覆盖弱，可能很晚才跟上。

### Q3：AI 能"发明"新数学吗？

AlphaProof 目前只能"解已知类型的问题"（IMO 题）。发明新数学（新概念、新猜想）是更难的任务。但 AI 辅助猜想生成（Ramanujan 机器、DeepMind 的矩阵乘法发现）已开始。

**关键区分**：证明（deduction）vs 发现（abduction/induction）。Lean/AlphaProof 做的是前者；后者是 AI-for-math 的下一个前沿。

### Q4：形式化数学会改变"什么是证明"吗？

传统数学证明是**社会过程**——一群专家审阅、讨论、逐渐接受。形式化证明是**机械过程**——kernel 检查、接受/拒绝。

这两个概念有张力：
- 形式化支持者说："机器验证才是真正的证明"
- 传统主义者说："理解为什么一个定理是对的，比机械验证更重要"

这个争论会持续——但 AlphaProof 的出现让它更紧迫：如果 AI 生成的一个 10 万行的 Lean 证明通过了 kernel 检查，但没有任何人理解它——**这算"证明"了吗**？

### Q5：中国形式化数学的位置

中国形式化数学社区正在增长，但与西方（特别是 Lean 社区）仍有差距：
- Lean 中文资源较少
- 中国数学教育体系对形式化的接受度待观察
- 但中国 AI 能力（DeepSeek 等）可能让中国在 AI+形式化领域弯道超车

### Q6：数学基础会被统一吗？

当前数学有多个"基础"：
- ZFC 集合论（传统数学家）
- CIC 类型论（Coq/Lean）
- HoTT（Voevodsky 的愿景）
- 范畴论（部分代数几何学家）

形式化会促进还是阻碍统一？一方面，形式化可能暴露不同基础之间的翻译困难；另一方面，一个好的证明助手可能充当"通用语"。

---

## 13. 配套资源

### 13.1 核心文献（按时代）

| 时代 | 文献 | 价值 |
|------|------|------|
| 前夜 | de Bruijn "A survey of the project Automath" (1970) | 类型论根基的原典 |
| LCF | Milner "A Theory of Type Polymorphism in Programming" (1978) | ML 与类型安全 |
| Coq | Coquand & Huet "The Calculus of Constructions" (1988) | CIC 原始论文 |
| 四色 | Gonthier "A computer-checked proof of the Four Colour Theorem" (2005) | 形式化数学的里程碑 |
| Feit-Thompson | Gonthier et al. "Engineering Mathematics" (2013) | 大规模形式化的工程教训 |
| HoTT | HoTT Book (2013) | 免费在线，类型论+拓扑的圣经 |
| Lean | de Moura et al. "The Lean Theorem Prover" (2015) | Lean 设计论文 |
| Scholze | Scholze 博客 "Liquid Tensor Experiment" (2020-2022) | Fields 奖得主的亲述 |
| AlphaProof | DeepMind Nature 论文 (DOI: 10.1038/s41586-025-09833-y) | AI+形式化的里程碑 |

### 13.2 视频资源

| 视频 | 讲者 | 价值 |
|------|------|------|
| Tao 2025-02 Simons 演讲 (YouTube: `5ZIIGLiQWNM`) | Tao | ML/LLM/Lean 三者合流 |
| Buzzard "The Future of Mathematics?" | Buzzard | Lean 布道的经典 |
| Voevodsky 的 HoTT 讲座（YouTube 多个）| Voevodsky | 理解 Fields 奖得主的动机 |
| Scholze 的 condensed math 讲座 | Scholze | 理解 Liquid Tensor 的数学 |

### 13.3 实操入口

| 资源 | 用途 |
|------|------|
| Natural Number Game (NNG4) | Lean 入门游戏 |
| Theorem Proving in Lean 4 (TPIL4) | 官方教程 |
| Mathematics in Lean (Mil) | 数学家的 Lean 入门 |
| Lean Zulip (leanprover.zulipchat.com) | 社区主战场 |
| Tao Analysis I Lean companion | 实分析 + Lean 双修 |
| Mathlib 文档 (leanprover-community.github.io/mathlib4_docs/) | API 参考 |

### 13.4 社区与会议

| 社区/会议 | 说明 |
|----------|------|
| Lean Together | 年度 Lean 社区大会 |
| Certified Programs and Proofs (CPP) | 形式化方法的学术会议 |
| Interactive Theorem Proving (ITP) | 证明助手的旗舰会议 |
| Lean Community 官网 | leanprover-community.github.io |

---

## 14. 费曼回炉

> **Feynman 回炉**：用最朴素的语言重新讲述本文核心，检验是否真正理解。

### F1：用三句话给一个完全不懂的人讲完形式化数学史

> **版本 1（v1，可能不够朴素）**：形式化数学从 1967 年 de Bruijn 的 Automath 开始，经过 Coq 的类型论革命（1984）、HoTT 的哲学推动（2009）、Lean 的社区工程（2017），到 2024 年 AlphaProof 实现 AI+形式化的合流——经历了四次范式转移，每次都重新定义了"谁能参与数学研究"。

**回炉（v2，更朴素）**：形式化数学就是"让计算机检查证明"。1960 年代有人开始做这件事，1980 年代法国人做出了 Coq（好用但难学），2010 年代微软做出了 Lean（更好用+社区更强），2020 年代最厉害的数学家开始用，2024 年 AI 用它解了奥林匹克数学题。

**再回炉（v3，最朴素——给中学生讲）**：数学证明有时候有错——你以为对了其实漏了一步。60 年前有人开始让电脑来检查每一步对不对。最早很难用，后来越来越好用。现在最厉害的数学家都在用，而且 AI 也学会用它了。

### F2：卡壳点记录

**卡壳 1**：长期把"形式化"理解为"把数学输入电脑"——好像只是打字工作。回炉后才意识到：形式化的核心是**强制写清每一步推理**，"显然"这样的词在 Lean 里不存在。形式化的真正价值不是"存储"证明，而是**暴露隐含假设**。

**卡壳 2**：把 Lean 的胜利归结为"技术更好"。回炉后意识到：Lean 的胜利**更多是社会学胜利**（社区工程、开源、Buzzard 布道），而非纯技术胜利。Mizar 的衰落证明了这一点。

**卡壳 3**：把 HoTT 当成"形式化数学的成功故事"。回炉后意识到：HoTT 作为新基础**失败了**，但它的失败比成功更有教育意义——它教会了 Lean 社区"不要试图改变数学家的语言"。

### F3：术语翻译

- **依赖类型论** → 类型可以"看"到值：就像"长度为 n 的数组"是一个类型，n 变了类型就变了，编译器替你检查"不能把长度 3 的数组当长度 5 的用"
- **de Bruijn factor** → 形式化一个证明比手写多花多少倍的力气；现在是 ~20 倍，Tao 预测 AI 帮忙后可能不到 1 倍
- **小信任内核** → 把"相信什么"压缩到最小（几千行代码），其他所有复杂的推理最终都还原到这几千行——只要这几千行没错，整个证明就没错
- **Calculus of Inductive Constructions (CIC)** → Coq/Lean 的逻辑地基：一种特殊的类型论，既能表达数学命题，又能表达数学对象的构造
- **univalence axiom** → "同构的东西相等"——两个看起来不同但结构一样的数学对象在 HoTT 中是"同一个东西"

### F4：v1 → v2 的 diff

- **v1 的错误**：把四次范式转移写成"技术升级链"（Coq → Lean → AI），好像每次都是上一次的"改进版"
- **v2 的修正**：强调每次范式转移是"换问题"而非"换答案"：
  - Coq 的转移：从"验证程序"到"数学基础"
  - Lean 的转移：从"个人形式化"到"社区工程"
  - Scholze 的转移：从"验证旧数学"到"参与新数学创造"
  - AlphaProof 的转移：从"人写证明"到"AI 写证明"
- **核心 diff**：从"技术年代史"升级为"思想变革史"——每次变革都重新定义了"形式化数学是干什么的"

---

## 附：时间线速查

| 年份 | 事件 | 范式转移？ |
|------|------|-----------|
| 公元前 300 | 欧几里得《几何原本》| 形式化的起源 |
| 1670s | Leibniz 梦想 *characteristica universalis* | —— |
| 1900 | Hilbert 23 问题（第 2：算术一致性）| —— |
| 1931 | Gödel 不完备定理 | 摧毁 Hilbert 纲领 |
| 1967 | de Bruijn 创造 Automath | **类型论血脉起点** |
| 1972 | Milner 创造 LCF | **LCF 血脉起点** |
| 1973 | Trybulec 创造 Mizar | 集合论血脉起点 |
| 1984 | Coquand/Huet 启动 Coq | |
| 1985 | Coquand 提出 Calculus of Constructions | |
| 1988 | CIC（加入归纳构造）| **第一次范式转移：类型论根基确立** |
| 2005 | Gonthier Coq 形式化四色定理 | |
| 2009 | Voevodsky 提出 HoTT | |
| 2012 | Gonthier 团队 Coq 形式化 Feit-Thompson | |
| 2012-13 | IAS HoTT 特殊年 + HoTT Book | |
| 2013 | de Moura 在 MSR 启动 Lean | |
| 2017 | Lean 3 + Buzzard 加入 + Mathlib 兴起 | **第二次范式转移：社区工程** |
| 2017 | Voevodsky 去世（51 岁）| |
| 2021 | Scholze 发起 Liquid Tensor Experiment | **第三次范式转移：大数学家入场** |
| 2021 | Lean 4 发布（自举）| |
| 2022 | Lean 3→4 迁移（Mathlib port）| |
| 2023 | Gowers/Tao PFR 形式化（3 周）| |
| 2024 | Tao 发起 Equational Theories Project | |
| 2024 | Buzzard 启动 FLT 五年计划 | |
| 2024 | AlphaProof IMO 银牌 | **第四次范式转移：AI+形式化** |
| 2025 | Tao《Analysis I》Lean companion | |
| 2025 | AlphaProof Nature 论文发表 | |
| 2026 | AlphaProof Nexus 攻 Erdős 问题 | |
| ? | de Bruijn factor < 1？ | ？（Tao 预测 5-10 年内）|

---

📌 **下一步**：
- 回到 [`00-为什么用Lean做数学.md`](00-为什么用Lean做数学.md) → 理解你为什么在这个历史时刻学 Lean
- 读 [`../top-math-courses/HISTORY_OF_IDEAS.md`](../top-math-courses/HISTORY_OF_IDEAS.md) §⑫ → 把形式化数学放进数学思想史的更大脉络
- 读 [`../讲透AI历史/00-为什么学AI历史.md`](../讲透AI历史/00-为什么学AI历史.md) → 对照 AI 史的方法论
- 思考 §12 的 6 个开放问题——每个都是博士论文级方向
