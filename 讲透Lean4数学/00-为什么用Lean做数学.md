# 00 - 为什么用 Lean 做数学

> 在动手学 tactic 之前，必须想清楚一件事：**为什么 2025 年的数学学习者应该用 Lean？**
>
> 这一章不教 Lean，只回答"为什么"。答案分三层：(1) 历史范式 (2) 你的位置 (3) 代价。

---

## 一、历史范式：数学的"形式化"是一条 2000 年的长河

Terence Tao 在 2025-02 Simons Foundation 演讲里说：

> "数学的历史，从欧几里得对几何的公理化，到符号代数记号的普及，一直是**形式化**的过程。Lean / Mathlib 是这条长河的延续。"

```
公元前 300 年    欧几里得《几何原本》           ← 第一个公理化系统
17 世纪          符号代数（Viète, Descartes）  ← 用符号代替文字
19 世纪          集合论 + 数理逻辑（Cantor, Frege）← 数学语言的严格化
20 世纪 30s      形式系统（Hilbert, Gödel, Turing）← 证明的可计算理论
20 世纪 70s      计算机辅助证明（四色定理, 1976）  ← 机器开始介入
21 世纪 10s      Coq/Agda/Lean                  ← 交互式定理证明器成熟
21 世纪 20s      Lean 4 + Mathlib + AlphaProof   ← 数学的"GitHub 时刻"
```

**我们正处在那条长河的一个拐点**：2024 年 AlphaProof 拿到 IMO 银牌，2025 年 Tao 把整本《Analysis I》Lean 化，2026 年 AlphaProof Nexus 攻 Erdős 问题。

> 💡 这就像 1995 年的互联网、2012 年的深度学习——**已经能用，但 killer app 还没出现**。Tao 原话：the killer app is coming。

---

## 二、用 Lean 做数学的 5 个真实理由

### 理由 1：你的证明 100% 是对的（不是"似乎对"）

人写证明会有 bug。Lean 的 kernel 检查每个证明步骤——**编译通过 = 数学界承认的正确**。

- Scholze 的 liquid tensor experiment：2022 年 Lean 验证后，Scholze 自己说"形式化过程发现了几个小错误和简化"。
- 即使是顶尖数学家，证明里也有错。Lean 抓得到。

### 理由 2：你会理解得**更深**

写非形式证明时，"显然"、"由...易得"可以掩盖漏洞。Lean 强制你写清每一步——你**被迫**理解每个细节。

Tao 关于《Analysis I》Lean companion 的原话：
> "形式化过程让我重新理解了自己写的东西——我以为我对某些章节理解得很透，但 Lean 揭示了多处隐藏假设。"

### 理由 3：你能加入大规模协作

传统数学研究是**1-3 人**协作。Lean 让 **50+ 人**协作一个项目成为可能：
- **Polynomial Freiman–Ruzsa conjecture**：Tao + 20 人，3 周完成 Lean 形式化（2023）
- **Equational Theories Project**：Tao + 50 人，7 个月完成 2200 万条证明（2024-25）
- **Fermat 大定理**：Buzzard 领衔，5 年计划（2024 启动）

> 💡 这是数学界从"作坊式"到"开源式"的转变——和 1990s 软件工程的转变完全平行。

### 理由 4：你的工作可复用 / 可累积

非形式证明在论文里，几十年后可能被遗忘。Lean 证明在 Mathlib 里，**全球研究者都能 import**。

你今天证一个引理，10 年后某个研究者可能直接 `import YourLemma`。这是数学的"开源贡献"。

### 理由 5：你是 AI-for-math 时代的稀缺人才

2025 年 AlphaProof = Lean + LLM + RL。这类系统的开发需要：
- 懂 ML（训练 LLM）
- 懂 Lean（环境）
- 懂数学（评估）

**你三样都有**。这是未来 10 年最稀缺的能力组合。

---

## 三、你的位置：Lean OS 经验 → Lean 数学

### 3.1 你已经会的

从 `ai-os-dd` / `law` / `neo-os`，你已经掌握：

| 能力 | 你已会用 |
|------|---------|
| Lean 4 语法（`def`/`theorem`/`lemma`/`inductive`）| ✅ |
| 基础 tactic（`intro`/`apply`/`exact`/`rw`/`simp`）| ✅ |
| `induction`（自然数归纳 / 结构归纳）| ✅ |
| 不变式证明（状态机 / 选举安全性）| ✅ |
| 大型 Lean 项目结构（多模块 / lake）| ✅ |
| 与 kernel 打交道（0 sorry / 0 axiom）| ✅ |

### 3.2 你需要学的（本系列的核心）

| 能力 | 数学场景特有 |
|------|-------------|
| Mathlib 的命名约定（如 `Nat.add_comm`）| 数学定理命名严格 |
| 高级 tactic（`ring` / `nlinarith` / `polyrith` / `decide`）| 代数 / 不等式自动化 |
| Type class 推理（`Ring`/`Field`/`TopologicalSpace`）| 数学的"接口" |
| 结构化证明（`have`/`obtain`/`rcases`）| 长 proof 的分解 |
| Mathlib 生态（`Order`/`Algebra`/`Topology`/`Analysis`）| 每个数学分支的库 |
| 数学品味（哪个定理值得形式化）| 工程没有这个 |

### 3.3 你的迁移成本

我估计：你已经掌握的 Lean 能力占数学 Lean 所需的 **70-80%**。剩下 20-30% 是本系列要教的——这是**几个月**的事，不是几年。

> 💡 **对比**：一个完全不会 Lean 的数学博士，从 0 到能给 mathlib 提 PR，通常需要 **6-12 个月**。你只需要 **1-3 个月**。

---

## 四、代价：用 Lean 做数学的 4 个真实代价

我不想给你灌迷汤。用 Lean 做数学有代价：

### 代价 1：de Bruijn factor ≈ 20

形式化一个证明的工作量 ≈ 写非形式证明的 20 倍。Tao 2024 估计。

写一个 5 行纸笔证明的定理，在 Lean 里可能要 100 行 + 几小时调试。

### 代价 2：不是所有数学都适合 Lean

- **代数 / 分析 / 拓扑**：Mathlib 极成熟，形式化顺畅。
- **概率 / 测度**：Mathlib 在发展中，部分概念表达费劲。
- **PDE / 几何分析**：Mathlib 覆盖弱，形式化成本极高。
- **组合 / 数论的 ad hoc 论证**：可能比代数证明难形式化。

### 代价 3：你可能在"形式化"而不是"做数学"

风险：花 3 天 Lean 调一个证明的 syntax，但这 3 天本来可以学 3 个新数学概念。

**对策**：把 Lean 当**验证工具**，不是学习主路径。学数学用纸笔 / 书 / 论文，**学完后**才在 Lean 里形式化巩固。

### 代价 4：你写的代码可能 Mathlib 不收

Mathlib 有严格 style guide 和 review 文化。第一次 PR 被拒 / 要求大改很常见。

**对策**：先看 `good first issue`，按 reviewer 反馈改。被 review 是学习最快的途径。

---

## 五、什么情况下**不**该用 Lean

诚实地说：

- ❌ 学**新**数学概念时（先用纸笔，再 Lean）
- ❌ 跑数值实验时（用 Python / Julia）
- ❌ 写论文初稿时（用 LaTeX）
- ❌ 探索性思考时（用纸笔 / 黑板 / 费曼讲）
- ✅ 学完一个定理想"100% 确认我懂了"时
- ✅ 写论文最终稿，想机械验证关键 lemma 时
- ✅ 给 Mathlib 贡献时
- ✅ 参与 Tao / Buzzard 类协作项目时

> 💡 **黄金比例**：数学学习时间的 **20-30%** 用 Lean。剩下 70-80% 是纸笔 + 读书 + 做题 + 思考。

---

## 六、本系列的承诺

读完本系列，你应该能：

1. **熟练**读 Mathlib 的任意源码（如 `Mathlib.Algebra.Group.Defs`）
2. **独立**证明数学课（Tao Analysis I / Axler / Rudin）的习题
3. **提交** mathlib PR 并通过 review
4. **评估**一篇 ML 理论论文能否形式化、成本多大
5. **参与** Tao / Buzzard 类协作项目（FLT / Equational Theories）

---

## 七、立刻能做的 3 件事

1. **Clone Tao Analysis I Lean companion**：
   ```bash
   git clone https://github.com/terrytao/analysis1-lean
   cd analysis1-lean && lake build
   ```
   能编译 = 你环境 OK。

2. **打开 Natural Number Game**（Lean 4 版）：
   - 在线版：https://adam.math.allport.co.uk/  或 https://www.ma.imperial.ac.uk/~buzzard/xto?
   - 本地：`git clone https://github.com/PatrickMassot/nng4`

3. **注册 Lean Zulip**：https://leanprover.zulipchat.com
   - 加入 `#new members`
   - 自我介绍："背景：ML 工程 + Lean OS 验证（ai-os-dd/law/neo-os）；目标：迁移到数学 Lean"

---

📌 **下一步**：
- 读 [`01-NaturalNumberGame讲透.md`](01-NaturalNumberGame讲透.md) 开始动手
- 配套 [`../top-math-courses/LEAN_MATH_TRACK.md`](../top-math-courses/LEAN_MATH_TRACK.md) 看路径规划

## ✍️ 练习

在动 01 章之前，先回答这 3 个问题（不要 Google）：

1. **de Bruijn factor 是什么？目前大约多少？**
2. **AlphaProof 在 IMO 2024 解出几道题？这为什么是 landmark？**
3. **你已有的 Lean 项目（ai-os-dd / law / neo-os）里，最难证明的一条定理是什么？为什么难？**

（答不上来 1、2 是正常的——回去读 [`../top-math-courses/LEAN_MATH_TRACK.md`](../top-math-courses/LEAN_MATH_TRACK.md) §一、§六。第 3 题是你自己的反思，用来定位你已经会什么。）

---


---

## 🎭 欺骗动力学视角：形式化数学 = 反证明欺骗

> 承接 [`欺骗动力学-社会进步的隐秘引擎.md`](欺骗动力学-社会进步的隐秘引擎.md) §5。

### 三问

1. **讲透Lean4数学 防的是什么欺骗？** → 数学证明里藏漏洞（hand-waving / 隐含假设）。
2. **被什么攻破？** → Lean 本身的元理论 / 公理选择 / 自动化策略的不可靠。
3. **沉淀进哪条主链？** → 验证主链 + 密码学主链——把人审证明升级为机器可检验证明。

### 一句话

> Lean4 让证明可信不再依赖审稿人的善意，而是依赖内核的强制检查。
