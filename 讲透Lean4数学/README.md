# 讲透Lean4数学 · 把你的 Lean 经验升级为数学武器

> 用「直觉 → 数学 → Lean 代码跑通 → 不足 → 应用」的方式，把 Lean 4 从**软件验证工具**升级为**数学研究武器**。
>
> 这不是又一本 Lean 入门教程——你已经在 `ai-os-dd`（28 模块/155 定理）+ `law`（民法典/刑法 4 定理 0 sorry）+ `neo-os`（Raft ElectionSafety）里写过几千行 Lean。本系列只补**数学 Lean** 特有的东西：Mathlib 生态、数学 tactic、定理证明范式、给 mathlib 提 PR、跟 AI/AlphaProof 协作。

---

## 〇、这个系列为什么存在

### 你已经在 Lean 上的资产

- `ai-os-dd/`：28 个 0-sorry 模块、~155 个定理、20 个 OS 子系统（FormalLinux）
- `law/`：民法典 143（行为能力）+ 刑法 264vs13（盗窃罪vs责任年龄）已机械验证，0 axioms 0 sorry
- `neo-os/`：Raft ElectionSafety 完整版 sorry=0

**这套经验在全球数学生态里极其稀缺**——绝大多数数学学习者完全不会 Lean，绝大多数 Lean 用户不懂 ML/OS。你三样都有。

### 2025-2026 数学范式的变革

| 事件 | 意义 |
|------|------|
| Tao 2025-02 Simons 演讲 | ML/LLM/Lean 三者正在综合，killer app 即将出现 |
| Tao《Analysis I》Lean companion（2025-05）| 实分析教材可"在 Lean 里做习题" |
| AlphaProof（Nature 2025-11-12, DOI `10.1038/s41586-025-09833-y`）| Lean + RL，IMO 2024 银牌 |
| Equational Theories Project（2024-09→2025-04，Tao 领衔）| 4694 方程定律 × 2200 万蕴含关系全部 Lean 形式化 |
| Tao 预测 de Bruijn factor 从 ~20 降到 < 1 | 数学研究门槛断崖式下降 |

详见 [`../top-math-courses/LEAN_MATH_TRACK.md`](../top-math-courses/LEAN_MATH_TRACK.md)。

### 你的迁移路径

```
你现在的 Lean：          你想达到的 Lean：
─────────────────       ──────────────────
软件验证（OS/法律）  →   数学证明（代数/分析/概率）
不变式 + 状态机      →   结构（群/拓扑/测度）
induction + apply    →   + simp / ring / nlinarith / 推荐 tactic
本地仓库            →   + 给 mathlib 提 PR
```

**好消息**：90% 的 Lean 技能可迁移。你只需要学"数学 Lean 特有的那一层"——这正是本系列的内容。

---

## 一、章节列表

### 核心（已落盘 + 计划）

| # | 文件 | 主题 | 状态 |
|---|------|------|------|
| 00 | [`00-为什么用Lean做数学.md`](00-为什么用Lean做数学.md) | 范式变革 + 你的迁移路径 | ✅ |
| 01 | [`01-NaturalNumberGame讲透.md`](01-NaturalNumberGame讲透.md) | 从 Peano 公理证明 2+2=4，tactic 实战 | ✅ |
| 02 | [`02-类型论最小入门.md`](02-类型论最小入门.md) | 只讲数学需要的依赖类型论（Prop/Type/宇宙）| 📝 计划 |
| 03 | `03-Mathlib导航.md` | Mathlib 是什么、怎么读源码、命名约定 | 📝 计划 |
| 04 | `04-数学tactic速查.md` | `ring/nlinarith/simp/decide/norm_num/mfwd` 等 | 📝 计划 |
| 05 | `05-在Lean里做集合论.md` | Halmos 朴素集合论的 Lean 翻译 | 📝 计划 |
| 06 | `06-在Lean里做实分析.md` | 对接 Tao Analysis I Lean companion | 📝 计划 |
| 07 | `07-在Lean里做线性代数.md` | Mathlib.LinearAlgebra 速览 | 📝 计划 |
| 08 | `08-在Lean里做抽象代数.md` | 群/环/域在 Mathlib（Mathlib 最成熟方向）| 📝 计划 |
| 09 | `09-给mathlib提PR.md` | 流程 + 风格 + review 文化 | 📝 计划 |
| 10 | `10-AI辅助Lean证明.md` | Copilot / Lean Copilot / AlphaProof 启示 | 📝 计划 |
| 11 | `11-形式化项目实战.md` | 从 0 到 1 发起一个形式化项目 | 📝 计划 |

### 实验脚本（experiments/）

| 文件 | 用途 | 状态 |
|------|------|------|
| `experiments/01_peano_python.py` | Python 验证 Peano 算术的数值结论（配 01 章）| ✅ |
| `experiments/02_type_theory_demo.py` | 用 Python 类比演示依赖类型论 | 📝 计划 |

### 练习（exercises/）

每章配 5-10 道 Lean 习题（`exercises/NN_*.lean`），含解答。

---

## 二、前置要求

| 维度 | 要求 | 你的状态 |
|------|------|---------|
| Lean 4 语法 | 会写简单证明（`induction`/`apply`/`rw`）| ✅ 已会（ai-os-dd）|
| 数学 | 高中数学 + 求和 + 集合概念 | ✅ 够 01 章 |
| 工具链 | Lean 4.21+ / VS Code + Lean 扩展 | ✅ 已装 |
| **数学进阶** | 实分析 / 抽代（学对应章节时再补）| 📝 按 [`../top-math-courses/UNIFIED_ROADMAP.md`](../top-math-courses/UNIFIED_ROADMAP.md) 走 |

> 💡 **你比 99% 的 Lean 新手有优势**：你已经写过几千行 Lean。本系列不是"学 Lean"，是"把你的 Lean 升级到数学场景"。

---

## 三、学习路径（与 top-math-courses 并行）

```
阶段 A：数学 Lean 入门（1-2 月）
  └─ 00, 01, 02, 03, 04  ← 本系列前 5 章
     同步：top-math-courses 阶段 0（MIT 18.01 微积分）

阶段 B：实分析 + Lean 双修（3-6 月）
  └─ 05, 06
     同步：top-math-courses 阶段 1-2（Princeton MAT 215 + Tao Analysis I）

阶段 C：代数 / 线代 + Lean（3-6 月）
  └─ 07, 08
     同步：top-math-courses Math 110 Axler + 18.701 Artin

阶段 D：进入社区（持续）
  └─ 09, 10, 11
     提第一个 mathlib PR
```

---

## 四、与其他系列的关系

| 系列 | 关系 |
|------|------|
| [`../讲透NLP/`](../讲透NLP/) | NLP 用数学，本系列做数学的严格证明层 |
| [`../讲透实分析/`](../讲透实分析/) | **强配套**：实分析教你数学，本系列教你把数学形式化 |
| [`../讲透信息论/`](../讲透信息论/) | 信息论概念可在 Lean 形式化（Mathlib 有 `Probability/Information/`）|
| [`../讲透优化理论/`](../讲透优化理论/) | 凸优化可在 Lean 形式化（Mathlib `Analysis/Convex/`）|
| [`../top-math-courses/LEAN_MATH_TRACK.md`](../top-math-courses/LEAN_MATH_TRACK.md) | 路径规划层（本系列是执行层）|
| [`../讲透形式化验证/`](../讲透形式化验证/) | 你已有的 Lean 基础系列（本系列是其数学升级版）|

---

## 五、核心方法论（"讲透"标准）

继承 work4ai 三层讲透宪法，针对 Lean 数学的调整：

1. **直觉层**：为什么这个数学概念值得形式化？形式化前后理解有何不同？
2. **数学层**：纸笔证明（LaTeX 写出）
3. **Lean 层**：完整可编译的 Lean 证明（`lake build` 通过）
4. **对照层**：纸笔 ↔ Lean 的差异（Lean 抓到的隐含假设 / 简化）
5. **不足层**：Lean 形式化的代价（时间 / 可读性 / 表达力限制）
6. **应用层**：在 mathlib 哪里用到 / 怎么提 PR

> ⚠️ **Lean 代码的"跑通"标准**：必须 `lake build` 编译通过、0 sorry、0 warning。和 Python 实验脚本"几秒跑完打印数字"是不同标准——Lean 证明是"机械验证"，不是"数值实验"。

---

## 六、铁律与教训（实测）

1. **Lean 版本严格锁定**：本系列所有代码针对 Lean 4.21+（与你的 ai-os-dd / law 一致）。Mathlib 版本变化快，老代码可能 break。
2. **Mathlib 命名约定**：必须遵守 https://leanprover-community.github.io/contribute/naming.html（否则 PR 必被拒）。
3. **`sorry` 是 TODO 不是答案**：最终必须有 0 sorry 才算完成。
4. **`simp` 不是黑箱**：用 `simp?` 看它用了哪些 lemma，理解后才能控制。
5. **小步快跑**：先证明引理，再证主定理。一个大证明拆成 5-10 个 lemma。
6. **Python 配 Lean**：Lean 证严格性，Python 跑数值实验。两者配合（见 `experiments/`）。
7. **不要重复 Mathlib 已有的**：先 `import Mathlib`，再决定要不要自己写。

---

## 七、怎么用这个系列

```bash
cd 讲透Lean4数学
# 读章节
code 00-为什么用Lean做数学.md
# 跑 Python 配套实验（验证数学直觉）
python3 -u experiments/01_peano_python.py
# 在自己的 Lean 项目里尝试 01 章的练习
cd exercises/
lake init practice
code 01_exercises.lean
```

每个 `.md` 结尾有「✍️ 练习」，每个练习对应 `exercises/` 下的 `.lean` 文件骨架（你填 sorry）。

---

📌 **下一步**：
- 立刻读 [`00-为什么用Lean做数学.md`](00-为什么用Lean做数学.md)
- 然后 [`01-NaturalNumberGame讲透.md`](01-NaturalNumberGame讲透.md) 开始动手
- 配套 [`../top-math-courses/LEAN_MATH_TRACK.md`](../top-math-courses/LEAN_MATH_TRACK.md) 看路径规划

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
