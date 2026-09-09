# Tao 的 AI 数学实践：从 Polymath 到 Equational Theories

> **信息来源**：Kevin Hartnett《The Proof in the Code: How a Truth Machine Is Transforming Math and AI》（Quanta Books, 2026.06.09）+ Quanta Magazine 2026.06.08 文章
> **可信度**：Tier S（Quanta Magazine + 出版书籍 + Tao 博客可交叉验证）
> **与 [01-AI正在重写数学研究.md](01-AI正在重写数学研究.md) 的分工**：01 讲宏观趋势，本篇讲 Tao 的个人实践时间线——从 Polymath 到 Lean 到 Equational Theories。

---

## 🎯 为什么单独写 Tao

Terence Tao 是**唯一一位**同时具备以下身份的人：
- Fields Medal 得主（2006）——数学权威性
- President's Council of Advisors on Science and Technology（PCAST）成员——政策影响力
- 生成式 AI 工作组联合主席——AI 领域话语权
- Lean 社区活跃贡献者——形式化实践者
- 公开博客作者（terrytao.wordpress.com）——知识传播者

他的实践 = AI 时代数学研究的**风向标**。

---

## 📅 Tao 的 AI 数学实践时间线

### 2007-2009：Polymath 实验——大规模协作的先驱

- **2007**：Tao 开通博客，公开讨论研究
- **2009.01**：Timothy Gowers 发起 **Polymath Project**——"大规模协作数学"
  - 在公开论坛提议问题，任何人可贡献
  - Tao 立即加入，理解关键：找能**分解为子问题**的大问题
- **第一个 Polymath**：改进 Hales-Jewett 定理，几个月完成，论文署名"D.H.J. Polymath"
- **后续**：15+ 个 Polymath 项目，Tao 领导了其中多个
- **局限**：博客评论区是有限的协作平台；**人工审核贡献的正确性**成为瓶颈

> Tao 的反思：Polymath 需要一种**自动验证贡献**的方式——这指向了 Lean。

### 2022-2023：转向 Lean

- **2022.07**：Tao 组织"计算机辅助数学研究"工作坊，邀请 Kevin Buzzard（Lean 布道者）
- **2023.10.09**：Tao 在社交媒体宣布："我决定终于开始学 #Lean4"
- **2023.11.06**：Tao 完成**第一个 Lean 形式化证明**——Maclaurin 不等式
  - 原始论文 10 页，花**近 1 个月**形式化
  - 发现：**难的证明部分容易形式化，简单的部分反而费力**
  - 例：在纸上"$\geq 1$ 的三个数之和 $\geq 3$"是显然的，但在 Lean 里需要找到 Mathlib 中的对应引理
  - 类型问题：数字 3 同时是整数/自然数/实数，Lean 要求明确指定

### 2023.11：PFR 猜想形式化——Polymath + Lean 的首次结合 ⭐

- **背景**：Tao + Gowers + Green + Manners 证明了 **Polynomial Freiman-Ruzsa (PFR) 猜想**（2023.11.09 上传 arXiv）
  - PFR：小和集的集合必含长等差数列（Marton 猜想的强化版）
- **2023.11.13**：Tao 在 Lean 社区发起 PFR 形式化项目
  - 模式：**Polymath 式协作 + Lean 自动验证**（解决了 Polymath 的审核瓶颈）
  - 把证明拆成 **5 行级别的引理**（极度模块化）
  - 第一周：补充 Mathlib 缺失的概率论概念（如 Shannon 熵）
- **2023.11.22**：Tao 发布 22 个待证引理，**几分钟内被志愿者认领**
  - "我想认领均匀随机变量的熵 :)" — Paul Lezeau（伦敦几何数论博士生）
  - "我来试试 fibration identity" — Aaron Anderson（UCLA 博士生）
- **2023.11.28**：Tao 发帖找志愿者做小任务，**46 分钟后 Kim Morrison 完成**
  - Tao："哇，太快了！谢谢！"
- **3 周完成** PFR 形式化

> Tao 的反思："我几乎没写什么 Lean 代码，主要在分配任务。这很鼓舞人心——说明数学家可以领导 Lean 项目而不需要精通 Lean 编程。"

### 2024.09：Equational Theories——AI 时代数学的"实验"范式 ⭐⭐

- **2024.09.25**：Tao 在博客宣布 **Equational Theories** 项目
- **问题**：研究 4694 个代数律（操作恰好应用 4 次的等式）之间的逻辑蕴含关系
  - 总计 **22,000,000** 个潜在蕴含关系需要验证
- **方法**：
  1. 用 Python 脚本测试简化的"magma"结构——**48 小时内解决 99%**
  2. 用自动定理证明器搜索剩余问题
  3. 人工攻克最难的剩余案例
- **Tao 的震惊**（第 2 天）："这个项目推进得远比预期快——仅 48 小时已经解决了大部分蕴含！我以为 3 周的 PFR 已经很快了，但这快到了疯狂的程度。"
- **进度**：
  - 1 个月内：22 million → 238
  - 11 月底：→ 138
  - 新年初：→ 30
  - 3 月底：→ 4（停滞数周）
- **意外发现**：项目产生了全新的数学构造——**"magma cohomology"**
  - Tao 问 John Baez（上同调专家）是否见过——Baez 说从未遇到
  - 这证明"实验数学"能发现**真正新的数学**

> Tao 的愿景：数学应该像物理学一样有"实验"分支——大型协作（如 CERN）产生大量数据，理论与实验互补。Equational Theories 是这个愿景的**试点项目**。

### 2024-2026：政策与推广

- **2024**：Tao 在 PCAST 提出生成式 AI 工作组报告
- **2024 两次高规格演讲**：阐述"人类洞察 + LLM 创造力 + 形式验证"的三角愿景
  - LLM 像"过度自信的本科生"——有好想法但分不清好坏
  - 解决方案：LLM 解决简单子问题 → 输出为 Lean 形式证明 → 人工攻克难的
- **2026.06**：Kevin Hartnett 出版《The Proof in the Code》——Tao 的 AI 数学实践成为书籍主题

---

## 🧠 Tao 的核心洞见

### 1. "难的容易，容易的难"
形式化数学的悖论：复杂的数学推理容易翻译成 Lean（因为每步逻辑明确），而"显然"的步骤反而难（因为 Lean 不接受"显然"，需要找到精确的引理）。

### 2. 模块化是大规模协作的关键
把证明拆成 5 行的引理 → 每个人贡献一小块 → Lean 自动验证 → **无需人工审核**。这是 Polymath 未实现的梦想。

### 3. AI 不是替代数学家，而是改变工作方式
- 传统：1-3 人合作，解决 1-2 个问题
- 未来：100+ 人 + AI 协作，把大问题拆成数千子问题
- 数学家的角色：**决定证明什么 + 想出关键 idea**（AI 做不了的）
- AI 的角色：解决大量简单子问题 + 输出 Lean 可验证的证明

### 4. "实验数学"的诞生
物理学有理论 + 实验两个分支。数学一直只有理论。Lean + AI 让数学也可以"做实验"——大规模搜索、发现新模式、产生数据。Equational Theories 的 "magma cohomology" 就是实验发现的新数学。

---

## 📊 PFR 形式化 vs Equational Theories 对比

| 维度 | PFR 形式化 | Equational Theories |
|------|-----------|-------------------|
| 目标 | 形式化已有证明 | 探索新的蕴含关系 |
| 规模 | ~100 个引理 | 22,000,000 个关系 |
| 时长 | 3 周 | 数月（仍有 4 个未解） |
| 参与者 | ~20 人 | 更广泛的去中心化 |
| AI 角色 | 辅助 | 搜索 + 自动证明 |
| 产出 | 已有证明的形式化 | **新数学**（magma cohomology）|
| 范式 | Polymath + Lean | **实验数学** |

---

## 🔗 与项目其他模块的连接

| 你想... | 跳到 |
|---------|------|
| 理解 AI 如何改变数学（宏观）| [01-AI正在重写数学研究.md](01-AI正在重写数学研究.md) |
| 学 Lean 入门 | [02-Lean形式化数学入门.md](02-Lean形式化数学入门.md) |
| 了解 PFR 猜想背景 | [conjecture进展/千禧问题与大猜想进展表.md](../conjecture进展/千禧问题与大猜想进展表.md) |
| 追加性组合方向 | [热点方向追踪/2024-2026十大热点方向.md](../热点方向追踪/2024-2026十大热点方向.md) #2 |
| 看 2026 最新突破 | [热点方向追踪/2026年最新数学突破.md](../热点方向追踪/2026年最新数学突破.md) |
| 选形式化方向 | [17-decision/](../../17-decision/) |

---

## 📚 参考资源

| 资源 | 链接 | 说明 |
|------|------|------|
| **Tao 博客** | [terrytao.wordpress.com](https://terrytao.wordpress.com) | Tao 的研究博客 |
| **Equational Theories 项目** | [teorth.github.io/equational_theories](https://teorth.github.io/equational_theories/) | 项目主页 |
| **《The Proof in the Code》** | [quantabooks.org](https://www.quantabooks.org/books/the-proof-in-the-code/) | Hartnett 2026 新书 |
| **Quanta 文章** | [How Terry Tao Became an Evangelist for AI in Math](https://www.quantamagazine.org/how-terry-tao-became-an-evangelist-for-ai-in-math-20260608/) | 本文主要来源 |
| **PFR 形式化** | [arXiv:2311.05762](https://arxiv.org/abs/2311.05762) | PFR 证明原文 |

---

> 💡 **心法**：Tao 的实践告诉我们——AI 时代的数学家不是被替代，而是被**赋能**。关键转变：从"一个人证明一个定理"到"组织 100 人 + AI 证明一个纲领"。数学家的核心能力从"计算和推导"转向"分解问题、组织协作、想出关键 idea"。
