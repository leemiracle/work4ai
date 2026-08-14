# LEAN_MATH_TRACK：学数学同时练 Lean 的并行路径（2025+ 数学的最大变量）

> **本章核心**：在 2025-2026，"学数学"和"练 Lean 形式化证明"不再是两件事——它们正在合并成**同一件事**。这份文档告诉你**为什么**这是你最大的杠杆，以及**怎么**把 [`UNIFIED_ROADMAP`](UNIFIED_ROADMAP.md) 的 30 课和 Lean 训练并行推进。
>
> 前沿信息全部来自 2024-2026 一手来源（Tao 博客、AlphaProof Nature 论文、Equational Theories Project、mathlib4 仓库），已核实。

---

## 〇、为什么这是你最大的杠杆

### 0.1 你已有的稀缺资产

从你的画像：
- **Lean4 实战经验**：`ai-os-dd`（28 个 0-sorry 模块 / ~155 定理 / 20 子系统）、`law`（民法典 143 + 刑法 264vs13 已机械验证）、`neo-os`（Raft ElectionSafety 完整版 sorry=0）
- **AI 工程能力**：讲透NLP / 讲透基础模型 / world-ai4sci-math 一整套
- **数学学习路径**：top-math-courses 30 课已规划

**这套组合（Lean4 + AI + 数学路径）在 2025 年的全球数学生态里极其稀缺**。绝大多数数学学习者不会 Lean，绝大多数 Lean 用户不懂 ML，绝大多数 ML 工程师不会证明。你三样都有。

### 0.2 范式变革正在发生

| 事件（2024-2026 已发生） | 影响 |
|------------------------|------|
| **Tao 2025-02 Simons 演讲**：ML/LLM/Lean 三者正在综合 | killer app 即将出现 |
| **Tao 2025-05 发布《Analysis I》Lean companion** | 实分析教材可在 Lean 里做习题 |
| **Equational Theories Project**（2024-09→2025-04）| 4694 个方程定律的 2200 万条蕴含关系全部 Lean 形式化 |
| **AlphaProof**（Nature 2025-11-12, `s41586-025-09833-y`）| Lean + RL，IMO 2024 银牌（28/42），攻下最难的 P6 |
| **AlphaProof Nexus**（2026-05，repo `google-deepmind/alphaproof-nexus-results`）| 已攻 Erdős / OEIS 问题 |
| **Buzzard 5 年计划**：在 Lean 里形式化 Fermat 大定理 | 整个证明体系将被机器验证 |
| **Tao 预测 "de Bruijn factor"**（形式化/非形式化难度比）从 ~20 降到 < 1 | 数学研究门槛断崖式下降 |

**结论**：你不是"在数学后面追赶"，你是"在一个范式变革的入口已经站好位置"——只是还没把 Lean4 当作"学数学的第二大脑"。

---

## 一、de Bruijn 因子：理解范式变革的钥匙

### 1.1 什么是 de Bruijn 因子

Nicolaas Govert de Bruijn（荷兰数学家，Automath 证明助手发明者）提出：

> **de Bruijn factor** = 形式化一个证明所需的工作量 / 写非形式化证明所需的工作量

经验值：
- **1990s（Coq 早期）**：de Bruijn factor ~100（每写 1 行非形式证明要花 100 倍时间形式化）
- **2010s（Lean / Mathlib 兴起前）**：~30-50
- **2020s（Lean 4 + Mathlib 成熟）**：~20（Tao 2024 估计）
- **未来 5-10 年（AI 整合）**：Tao 预测可能 < 1

### 1.2 为什么 < 1 是颠覆性的

如果 de Bruijn factor < 1：
- **写形式证明比写非形式证明还快**
- 论文默认附 .lean 文件（不只是 PDF）
- "证明对不对"不再依赖人类 reviewer
- 数学可以**大规模协作**（Equational Theories Project 是雏形：50+ 人 7 个月完成 2200 万条证明）

### 1.3 对你的意义

```
de Bruijn factor = 20 的世界：
  → 只有少数专家（如 Tao / Buzzard）能用 Lean 做研究
  → 你的 Lean 经验是"小众技能"

de Bruijn factor < 1 的世界（Tao 预测未来 5-10 年）：
  → 所有数学论文都形式化
  → "会 Lean + 会数学"成为数学研究者的基本要求
  → 你的 Lean 经验变成"主流技能"——但你已经在 2025 年就练熟了
  → AI 工程能力让你能写工具、贡献 AlphaProof 类系统
```

**这是你在时间上的红利**：今天练 Lean，等于 2010 年学 Python、2015 年学 PyTorch。

---

## 二、学习路径：从"会写 OS 的 Lean"到"会做数学的 Lean"

你已有的 Lean4 经验偏**软件验证**（OS / Raft / 法律条文）。数学 Lean 不一样，但门槛对你**极低**。下面是迁移路径。

### 2.1 第一阶段：数学 Lean 入门（1-2 个月）

#### 2.1.1 Natural Number Game（NNG）

**地址**：https://adam_GAME..com  或  https://github.com/PatrickMassot/nng4（Lean 4 版）

**讲什么**：从 Peano 公理出发，证明 $1+1=2$、加法交换律、结合律等。

**价值**：
- 学 Lean 的**核心 tactics**（`induction`, `rw`, `simp`, `apply`, `exact`）
- 体会"数学是构造性"的——每个定理都是一个程序
- 重新理解你小学就会的加法（用 Peano 公理）

**配合**：见 [`../讲透Lean4数学/01-NaturalNumberGame讲透.md`](../讲透Lean4数学/01-NaturalNumberGame讲透.md)（本批新建）。

#### 2.1.2 The Mechanization of Mathematics（在线教程）

- **Kevin Buzzard 的 "Formalising Mathematics" 课**（Imperial College，YouTube + GitHub）
- **"The Lean Theorem Prover" 官方教程**：https://lean-lang.org/lean4/doc/

#### 2.1.3 Mathlib Overview

**必读**：https://leanprover-community.github.io/mathlib-overview.html

了解 Mathlib 已有哪些理论已形式化——你学一个数学概念时，先查 Mathlib 有没有，有的话读它的 Lean 实现。

### 2.2 第二阶段：实分析 + Lean 双修（3-6 个月）

**核心**：Tao《Analysis I》Lean companion

- **仓库**：https://github.com/terrytao/analysis1-lean（2025-05-31 发布）
- **简介**：Tao 把《Analysis I》的定义、定理、习题翻译成 Lean，**用 sorry 留空让你填**。
- **设计**：前几章用自定义的 `Chapter2.Nat`（不用 Mathlib 的 Nat），让你从 Peano 公理自己构造自然数。后期逐步切换到 Mathlib 的标准定义。

**怎么用**：
1. 读 Tao《Analysis I》纸书一章
2. 在纸上做习题
3. 在 Lean companion 里填对应的 sorry
4. 双向印证：纸笔证明 ↔ Lean 证明

**这是 2025 年学实分析的最优路径**——一举两得。

### 2.3 第三阶段：给 Mathlib 提 PR（6-12 个月）

Mathlib 是开源社区库，**接受外部 PR**。流程：
1. 在 https://github.com/leanprover-community/mathlib4/issues 找 `good first issue` 标签
2. 或者你学某个定理时发现 Mathlib 没有 → 自己实现 → 提 PR
3. Reviewer 会 review（这是事实上的"导师反馈"）
4. 被合并 = 你的名字在 Mathlib contributor 列表

**价值**：
- Reviewer 是顶尖 Lean 数学工作者（如 Mario Carneiro, Jasmin Blanchette）
- 这是"无导师自学者的最佳替代品"
- 简历 / PhD 申请的有效产出

### 2.4 第四阶段：研究级形式化（1-2 年+）

参与或发起**形式化项目**：
- **Equational Theories Project 模式**：找一个数学领域，把它的"蕴含关系图"系统形式化
- ** Buzzard 的 Fermat 大定理计划**：https://github.com/ImperialCollegeLondon/FLT
- **形式化你研究的方向的奠基论文**

---

## 三、与 UNIFIED_ROADMAP 30 课的并行映射

下面是把 [UNIFIED_ROADMAP](UNIFIED_ROADMAP.md) 30 课和 Lean 训练**严格并行**的方案。每学一门数学课，对应的 Lean 练习。

| # | 数学课 | 同期 Lean 练习 | Mathlib 对应文件 |
|---|--------|---------------|-----------------|
| 1 | MIT 18.01 微积分 | NNG 完成 + 学 Lean 基础 tactics | `Mathlib/Init/` |
| 2 | MIT 18.02 多变量 | 在 Lean 里证极限定义 | `Mathlib/Topology/` |
| 3 | MIT 18.06 线代（Strang） | 在 Lean 里玩矩阵（`Matrix` 模块）| `Mathlib/LinearAlgebra/` |
| 4 | MIT 18.03 ODE | 选学（Mathlib ODE 较少）| `Mathlib/Dynamics/` |
| 5 | Berkeley Math 110（Axler） | 在 Lean 里证谱定理 | `Mathlib/LinearAlgebra/Eigenspace/` |
| 6 | MIT 6.042J 离散 | NNG 后半 + 集合论 | `Mathlib/Logic/`, `Mathlib/Set/` |
| 7 | Berkeley Stat 134 概率 | 选学（概率在 Mathlib 较少）| `Mathlib/Probability/` |
| 8 | Princeton MAT 215 实分析入门 | **Tao Analysis I Lean companion** ★ | Tao 的 repo |
| 9 | Princeton MAT 300 多变量 | companion 后续章节 | 同上 |
| 10 | Berkeley Math 185 复分析 | Mathlib 复分析（`Complex/`）| `Mathlib/Analysis/Complex/` |
| 11 | MIT 18.100B 实分析（Rudin） | 形式化 Rudin 关键定理 | `Mathlib/Analysis/` |
| 12 | MIT 18.701 抽代 I | **Mathlib 抽象代数极成熟** ★ | `Mathlib/Algebra/GroupTheory/`, `RingTheory/` |
| 13 | MIT 18.702 抽代 II | Galois 理论在 Mathlib | `Mathlib/FieldTheory/` |
| 14 | MIT 18.901 拓扑 | Mathlib 拓扑（极成熟）★ | `Mathlib/Topology/` |
| 15 | Cambridge Part IB Linear Algebra | 选学 | `Mathlib/LinearAlgebra/` |
| 16 | MIT 18.125 测度论 | Mathlib 测度论 | `Mathlib/MeasureTheory/` ★ |
| 17 | MIT 18.175 概率（Durrett） | Mathlib Probability | `Mathlib/Probability/` |
| 18 | UT Austin M 383E 数值线代 | 用 Julia/NumPy 实现，Lean 选学 | `Mathlib/Analysis/Matrix/` |
| 19 | MIT 18.086 ODE 数值 | 用 Julia 实现 | — |
| 20 | Stanford CME 364A 凸优化 | Lean 选学（Mathlib 较少）| `Mathlib/Analysis/Convex/` |
| 21 | Berkeley Stat 200A 数理统计 | Mathlib 统计 | `Mathlib/Statistics/` |
| 22 | MIT 18.424 信息论 | Mathlib Information | `Mathlib/Probability/Information/` ★ |
| 23 | MIT 18.102 泛函 | Mathlib 泛函 | `Mathlib/Analysis/Normed/`, `OperatorTheory/` |
| 24 | MIT 18.103 调和分析 | 选学（较前沿）| `Mathlib/Analysis/Fourier/` |
| 25 | Berkeley Math 218 随机过程 | Mathlib Probability/MarkovChain | `Mathlib/Probability/MarkovChain/` |
| 26 | UT Austin M 387D SDE | 选学（Mathlib 在发展中）| `Mathlib/MeasureTheory/Pell/` |
| 27 | Cambridge 微分几何 | Mathlib 流形（发展中）| `Mathlib/Geometry/Manifold/` |
| 28 | ETH 401-3651 SDE 数值 | 用 Julia 实现 | — |
| 29-30 | 前沿专题 | **找一篇前沿论文形式化** | — |

> ★ 标记的是 Mathlib **特别成熟**的方向，做形式化练习时反馈好。

---

## 四、Tao《Analysis I》Lean companion 详解（你的实分析 + Lean 主战场）

### 4.1 为什么这是最优起点

- **作者权威**：Tao 是 Fields 奖 + Breakthrough Prize 得主，2024-2026 领导多个 Lean 项目
- **教材质量**：《Analysis I》是公认最好的实分析入门之一（和 Rudin 并列）
- **设计精妙**：从 Peano 公理自建 `Nat`，逐步切换到 Mathlib 的 `Nat`
- **官方"留空"**：所有习题都用 `sorry` 标记，你填 → 编译通过 = 证对

### 4.2 怎么用

```bash
# 1. Clone 仓库
git clone https://github.com/terrytao/analysis1-lean
cd analysis1-lean

# 2. 装 Lean（已装跳过，你已有 ai-os-dd 经验）
# https://lean-lang.org/lean4/doc/setup.html

# 3. 编译
lake build

# 4. 在 VS Code 里打开，找 sorry，开始填
code .
```

### 4.3 一章的典型学习循环

```
Day 1-3: 读 Tao《Analysis I》Ch N 纸书
Day 4:   在纸上做习题
Day 5-7: 在 Lean companion 里填对应 sorry
Day 8:   对照纸笔证明 ↔ Lean 证明，找差异
```

### 4.4 预期产出

完成全书 ≈ 6-12 个月（每周 5-10h）。产出：
- 实分析严格训练（数学）
- Lean tactics 熟练（形式化）
- 可以 fork 你的解作为"实分析 + Lean 双修"的作品集

---

## 五、mathlib PR 实操

### 5.1 找第一个 PR

**渠道**：
1. https://github.com/leanprover-community/mathlib4/issues?q=is:open+label:"good+first+issue"
2. 在 Zulip（https://leanprover.zulipchat.com）的 `#new members` 频道问"我想做第一个 PR"
3. 你学某定理时发现 Mathlib 没有 → 自己加

**典型的"good first issue"**：
- 补一个引理（如"两个紧集的乘还是紧集"——Heine-Borel 的推广）
- 改进一个证明（更短/更可读）
- 加 docstring（解释某个定义）

### 5.2 PR 流程

```bash
# 1. Fork mathlib4 到你的 GitHub
# 2. Clone 你的 fork
git clone https://github.com/YOUR_USERNAME/mathlib4
cd mathlib4

# 3. 加 upstream
git remote add upstream https://github.com/leanprover-community/mathlib4

# 4. 新分支
git checkout -b my-first-pr

# 5. 改代码，lake build 验证

# 6. 提 PR
git push origin my-first-pr
# 在 GitHub 上发 PR，描述改了什么、为什么
```

### 5.3 Review 文化

- Mathlib 有严格的 **style guide**：https://leanprover-community.github.io/contribute/naming.html
- Reviewer 可能要你改命名、加 lemma、改证明结构
- **不要怕被拒**——被 review 是学习 fastest 的方式
- 第一次 PR 平均要改 3-5 轮才合并

### 5.4 Lean Zulip：社区主战场

- 注册：https://leanprover.zulipchat.com
- 必加频道：
  - `#new members`（新手提问）
  - `#Is there code for X?`（查 Mathlib 有没有 X）
  - `#mathlib4`（开发讨论）
  - 你数学方向的频道（如 `#measure theory`, `#linear algebra`）

---

## 六、前沿：AlphaProof / Equational Theories / FLT（必看，不必重现）

### 6.1 AlphaProof（DeepMind，Nature 2025-11-12）

**论文**：*Olympiad-Level Formal Mathematical Reasoning with Reinforcement Learning*，arXiv 同步，DOI `10.1038/s41586-025-09833-y`。

**核心**：
- Lean 4 + Mathlib 作为环境
- LLM（Gemini 系）预训练 + 在 Lean 上 fine-tune
- AlphaZero 式 RL：自己生成证明 → 验证 → 强化
- IMO 2024：解出 P1/P2/P6（含最难的 P6，全球只 5 人满分）+ AlphaGeometry 2 解 P4 = 28/42 银牌

**对你**：
- 看 Nature 论文（不长，20 页）理解架构
- 不必重现（资源不够）——但**理解它代表什么**：数学已成 AI 可攻克的领域
- 关注 miniF2F benchmark（https://github.com/google-deepmind/miniF2F）作为练手目标

### 6.2 AlphaProof Nexus（2026-05）

- repo: https://github.com/google-deepmind/alphaproof-nexus-results
- 已开始攻 **Erdős 未解问题** 和 **OEIS 问题**
- 提供 Lean 形式化 + 自然语言证明对照
- **这是 2026 数学研究的当前 frontier**——关注但不强求重现

### 6.3 Equational Theories Project（Tao 领衔，2024-09→2025-04）

- **论文**：https://teorth.github.io/equational_theories/paper.pdf（2025-12 上传 arXiv）
- **目标**：4694 个 magma 方程定律之间的 22,028,942 条蕴含关系，全部 Lean 形式化
- **过程**：2 个月非形式化 + 5 个月形式化，50+ 人协作
- **意义**：大规模协作数学的范式样本。Tao 在博客说"未来类似项目会越来越多"

**对你**：
- 读论文的 §1-3（项目组织）和 §4（Lean 基础设施）
- 想象：未来你能不能发起一个 ML 理论的类似项目？（如：神经网络的等价类蕴含图）

### 6.4 FLT（Buzzard 5 年计划）

- **目标**：在 Lean 里形式化整个 Fermat 大定理证明（Wiles 1995，100+ 页）
- repo: https://github.com/ImperialCollegeLondon/FLT
- 进度：2024 启动，预期 2029 完成
- 你**不必参与**（需要代数几何 PhD 级背景），但关注进展理解"形式化正在覆盖整个数学"

---

## 七、工具链与社区

### 7.1 工具链

```bash
# Lean 4 + Mathlib
elan install leanprover/lean4:stable   # Lean 版本管理（已装）
lake                                   # Lean 的构建工具（已装）

# 编辑器
VS Code + Lean 4 扩展                   # 你已用

# AI 辅助
GitHub Copilot                          # 自动补全 Lean（Tao 在用）
Lean Copilot（https://github.com/lean-dojo/LeanCopilot）# 专门的 Lean AI

# 文档
https://leanprover-community.github.io/mathlib4_docs/  # Mathlib 文档
https://leanprover.github.io/theorem_proving_in_lean4/ # TPIL 4 官方教程
```

### 7.2 学习资源（按顺序）

1. **The Natural Number Game**（NNG4）—— 入门游戏
2. **Functional Programming in Lean**（FPiL）—— Lean 作为函数式语言（你已会编程，跳着读）
3. **Theorem Proving in Lean 4**（TPIL 4）—— 官方证明教程
4. **Mathematics in Lean**（Mil）—— 数学工作者写的 Lean 入门 ★
5. **Tao Analysis I companion** —— 实战
6. **Mathlib source code** —— 高阶（读别人的实现）

### 7.3 社区

- **Lean Zulip**：https://leanprover.zulipchat.com（社区主战场）
- **Lean Community 官网**：https://leanprover-community.github.io
- **Lean Together**：年度大会（有录像）
- **r/Lean** on Reddit：浅一些
- **Twitter Lean 圈**：Buzzard (@kbuzzard), Tao (@terrytao) 等

---

## 八、与你的现有 Lean 项目联动

你已有的 Lean 资产：

| 项目 | 内容 | 迁移价值 |
|------|------|---------|
| `ai-os-dd` | 28 模块 / 155 定理 / 20 子系统 | 你已经会写大 Lean 项目。数学项目的结构组织你已熟 |
| `law` | 民法典 143 + 刑法 264vs13（0 axioms 0 sorry）| 你已会"把自然语言形式化"。这是 Lean 数学最稀缺的能力 |
| `neo-os` | Raft ElectionSafety sorry=0 | 你已会不变式证明 + 归纳。数学证明 90% 是这两件事 |

**迁移要点**：
- OS 的 Lean 偏**程序语义**（不变式 / 状态机），数学的 Lean 偏**结构**（代数 / 拓扑 / 测度）
- 你需要学的：**Mathlib 的命名约定**、**tactic 高级用法**（如 `simp` 的 lemma 集合）、**type class 推理**
- 不需要重学的：Lean 语法、依赖类型论基础、`induction` / `apply` / `rw` 等核心 tactic

> 💡 **关键**：你比 99% 的 Lean 新手有优势——你已经"用 Lean 写过几千行代码"。现在只是把对象从 OS 换成数学。

---

## 九、建议节奏（与你 top-math-courses 并行）

### 第 1 个月
- [ ] 完成 NNG4（每天 1-2 关）
- [ ] 读 TPIL 4 前 5 章
- [ ] Clone Tao Analysis I Lean companion，编译通过
- [ ] 注册 Lean Zulip，自我介绍

### 第 2-3 个月
- [ ] 开始学 MIT 18.01 / Spivak（数学）
- [ ] 在 Lean companion 里填前 2 章的 sorry
- [ ] 在 math.stackexchange 回答 1 道 Lean 相关题

### 第 4-6 个月
- [ ] 学 MIT 18.06（线代）
- [ ] 在 Lean 里玩 `Mathlib.LinearAlgebra`
- [ ] 提第一个 Mathlib PR（good first issue）

### 第 6-12 个月
- [ ] 进入实分析主战场（Tao Analysis I 全书）
- [ ] 完成 5-10 个 Mathlib PR
- [ ] 写第一篇 "讲透 Lean 数学" blog

### 第 1-2 年
- [ ] 找一个细分方向（建议：ML 理论 / 数值分析 / 形式化数学）
- [ ] 参与一个形式化项目（FLT / Equational Theories 类）
- [ ] 在 Zulip 上回答新手问题（巩固 + 建立声誉）

---

## 十、自检题

1. **de Bruijn factor 是什么？目前大约多少？Tao 预测未来降到多少？为什么 < 1 是颠覆性的？**
2. **Clone Tao Analysis I Lean companion，编译通过**。截一张编译成功的图。
3. **完成 NNG4 前 5 关**。能证明 $2 + 2 = 4$ 吗？
4. **在 Lean Zulip 注册并自我介绍**（"我是 X，背景是 ML 工程 + Lean OS 验证，想学数学 Lean"）。
5. **读 AlphaProof Nature 论文的 abstract + introduction**。能用 3 句话复述它做什么吗？

---

## 十一、与其他文档的衔接

| 你想做什么 | 去哪 |
|-----------|------|
| 数学研究方法论（解题 / 阅读 / 写作）| [`RESEARCH_METHODOLOGY.md`](RESEARCH_METHODOLOGY.md) |
| 30 课数学主路径 | [`UNIFIED_ROADMAP.md`](UNIFIED_ROADMAP.md) |
| 学 Lean 的讲透系列 | [`../讲透Lean4数学/`](../讲透Lean4数学/)（本批新建）|
| 学实分析的讲透系列（配 Lean）| [`../讲透实分析/`](../讲透实分析/)（本批新建）|
| 数学 ↔ ML 工程映射 | [`CROSS_INDEX_WITH_WORK4AI.md`](CROSS_INDEX_WITH_WORK4AI.md) |
| 数学前沿论文 | [`LATEST_RESEARCH.md`](LATEST_RESEARCH.md) |

---

📌 **下一步**：
- **立刻**：Clone Tao Analysis I Lean companion，编译通过（4.2）
- **本周**：完成 NNG4 前 5 关（2.1.1）
- **本月**：读 AlphaProof Nature 论文 + Tao 2025-02 演讲
- **本季**：提第一个 Mathlib PR（5.1）
- **本年**：完成 Tao Analysis I Lean companion 前 5 章 + 找到细分方向

**记住**：你不是从零开始学 Lean。你是把已有的 Lean4 OS 经验**升级**为数学武器。这个升级是 2025-2026 数学生态里最稀缺的迁移。
