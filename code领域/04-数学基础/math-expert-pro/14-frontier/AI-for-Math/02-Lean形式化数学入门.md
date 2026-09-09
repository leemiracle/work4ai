# Lean 形式化数学入门：从零到第一个机器验证的证明

> **信息日期**：2026-07-12（综合 leanprover-community 官方 / Mathlib GitHub / Kevin Buzzard 讲座 / Tao 博客）
> **可信度**：Tier S（Lean 官方文档 + Mathlib 仓库可验证 + Fields 得主 Tao 公开背书）
> **与 [01-AI正在重写数学研究.md](01-AI正在重写数学研究.md) 的分工**：01 讲"为什么形式化是革命"（宏观叙事），本篇讲"你如何开始用 Lean"（实操入门）。

---

## 🎯 这篇指南给谁

- 你学完本科核心数学（[01-track/stage-1](../../01-track/stage-1-本科核心/)），想知道"形式化"到底怎么入手
- 你听说 AlphaProof 用 Lean 在 IMO 拿银牌，想亲眼看 Lean 怎么验证证明
- 你想给自己的数学笔记加一道"机器验证"保险（[NOTES_TEMPLATE.md](../../NOTES_TEMPLATE.md) §4 严格证明的进阶版）

**读完你能**：
1. 理解 Lean 4 + Mathlib 是什么、为什么是 2024-2026 的事实标准
2. 在浏览器里 5 分钟写出第一个机器验证的证明
3. 知道从哪开始学、学到什么程度够用

---

## 🧠 30 秒理解 Lean

**Lean 是什么**：一个**定理证明器** + **函数式编程语言**。你用 Lean 写证明，Lean 的内核（kernel）会 100% 验证逻辑正确性——不是"看起来对"，而是**机器保证对**。

**核心机制**：依赖类型论（Dependent Type Theory）。在 Lean 里：
- **类型** = 命题（如 `n + 0 = n` 是一个类型）
- **程序** = 证明（如 `Nat.zero_add n` 是 `n + 0 = n` 这个类型的实例）
- **类型检查** = 证明验证（如果程序能通过类型检查，证明就成立）

> 💡 这就是 **Curry-Howard 同构**——命题即类型，证明即程序。详见 [16-foundations/Curry-Howard/](../../16-foundations/Curry-Howard/)。

**为什么是 Lean 而不是 Coq/Agda/Isabelle**：
| 证明器 | 优势 | 劣势 | 2024 现状 |
|--------|------|------|----------|
| **Lean 4** ⭐ | 数学语法贴近人类 / Mathlib 庞大 / AI 首选 | 仍在快速迭代 | **事实标准**，DeepMind/OpenAI/Anthropic 都选它 |
| Coq | 历史悠久 / 工业验证成熟 | 语法底层 / 库分散 | 仍在用，但社区向 Lean 迁移 |
| Agda | 依赖类型最纯粹 | 数学库小 / 偏 PL 研究 | 小众但活跃 |
| Isabelle/HOL | 定理自动化强 / 有 Archive | 语法不贴近数学家 | 欧洲学派用得多 |

---

## 📚 Mathlib：集体数学图书馆

**Mathlib** 是 Lean 社区维护的开源数学库，是 Lean 能用来做严肃数学的根基。

**规模（截至 2026.07，Mathlib4 GitHub 实时统计）**：
- Stars：**3.6k** / Forks：**1.5k**
- Commits：**33,249+**（持续增长）
- 最新版本：**v4.31.0**（2026.06.15 发布）
- 代码量：**超 150 万行 Lean 代码**（99.7% Lean）
- 维护者：**30+ 核心成员**（含 Kevin Buzzard / Mario Carneiro / Heather Macbeth / Patrick Massot / Sébastien Gouëzel / Johan Commelin）
- 覆盖：从自然数算术到范畴论、代数几何、测度论、微分拓扑
- 相当于：**一部机器可验证的数学百科全书**

> 📊 数据来源：[github.com/leanprover-community/mathlib4](https://github.com/leanprover-community/mathlib4)（2026.07 实时抓取）

**关键里程碑**：
| 年份 | 事件 |
|------|------|
| 2017 | Lean 3 + mathlib 启动，Kevin Buzzard（帝国理工）开始推动 |
| 2021 | Peter Scholze 用 Lean 验证"液态张量实验"（Liquid Tensor Experiment）——**Fields 得主亲自下场验证自己的工作**，证明他提出的 condensed mathematics 核心引理 |
| 2022 | Scholze 的验证完成，他在博客宣布"我现在 100% 确信这个定理是对的" |
| 2023 | Lean 4 + mathlib4 稳定，社区大规模迁移完成 |
| 2024 | mathlib 超 150 万行；多项式 PI 理论、Sylow 定理、Fermat 小定理等全部形式化 |
| 2024.07 | AlphaProof 用 Lean 在 IMO 2024 拿银牌（28/42），详见 [01-AI正在重写数学研究.md](01-AI正在重写数学研究.md) |
| 2024-2025 | Terence Tao 持续在博客和讲座推广 Lean，预测"10 年内所有数学论文都会附带 Lean 形式化" |

**Terence Tao 的判断**（2024 多次公开表述）：
> Lean 不会取代数学家的直觉，但它会像 LaTeX 一样成为**标准工具**。10 年后，"这个证明没被形式化"可能像今天"这个证明没被同行评审"一样不可接受。

---

## 🚀 5 分钟在线尝试（无需安装）

### 方式一：Lean Web Editor（最快）

打开 [https://live.lean-lang.org/](https://live.lean-lang.org/)（Lean 官方在线编辑器）：

```lean
-- 你的第一个 Lean 证明
theorem my_first_proof : 1 + 1 = 2 := by
  norm_num

-- 用归纳法证明：n + 0 = n
theorem zero_add (n : ℕ) : 0 + n = n := by
  induction n with
  | zero => rfl
  | succ k ih => simp [Nat.succ_eq_add_one, ih]
```

把这段贴进编辑器，如果右侧面板显示 `Goals accomplished` 🎉 ——你刚写出了机器验证的证明。

### 方式二：Natural Number Game（强烈推荐新手）

Kevin Buzzard 设计的互动游戏，从皮亚诺公理一步步证明自然数性质：

🔗 [https://adam.math.hhu.de/](https://adam.math.hhu.de/) → 找 "Natural Number Game"

- 每关一个定理，你填 tactic，它告诉你对不对
- 从 `0 + n = n` 一路证到 `n + m = m + n`（加法交换律）
- **完成游戏 = 掌握 Lean 归纳法基础**，约 2-4 小时

### 方式三：Mathematics in Lean（系统教程）

官方交互式教程，每章一个数学主题：

🔗 [https://leanprover-community.github.io/mathematics_in_lean/](https://leanprover-community.github.io/mathematics_in_lean/)

覆盖：集合 / 函数 / 数论 / 拓扑 / 微积分，每节都可在线运行。

---

## 💻 本地安装（如果你想长期用）

### 安装 elan（Lean 版本管理器，类似 rustup/nvm）

```bash
# Linux/macOS
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# 验证
lean --version
lake --version   # lake 是 Lean 的包管理器（类似 cargo）
```

### 创建你的第一个 Lean 项目

```bash
# 用 mathlib 模板创建项目
lake new my_math_proj math

cd my_math_proj
lake build   # 首次编译较慢（下载 + 编译 mathlib 依赖）

# 在 VS Code 装 "Lean 4" 扩展，打开项目即可
```

> ⚠️ 首次 `lake build` 会下载并编译 mathlib，**需要 10-30 分钟 + 8GB+ 内存**。如果只是学习，先用在线编辑器。

### VS Code 配置（推荐编辑器）

1. 安装 VS Code
2. 扩展市场搜 "Lean 4"（leanprover.lean4），安装
3. 打开 `.lean` 文件，右侧自动显示 tactic state（当前证明目标）

---

## ✍️ 第一个证明：逐步拆解

我们来证明一个看似显然的定理：**对所有自然数 n，n + 0 = n**。

### 数学证明（传统）
> 对 n 做归纳。基例 n=0：0+0=0 显然。归纳步：假设 k+0=k，要证 (k+1)+0=k+1。由加法定义 (k+1)+0 = (k+0)+1 = k+1（用归纳假设）。∎

### Lean 证明

```lean
-- 声明定理：对所有自然数 n，n + 0 = n
theorem add_zero (n : ℕ) : n + 0 = n := by
  -- Lean 进入 tactic 模式，目标是：n + 0 = n
  induction n with
  -- 情况1：n = 0，目标变成 0 + 0 = 0
  | zero =>
    -- rfl 检查等式两边是否定义相等
    rfl
  -- 情况2：n = k+1，有归纳假设 ih : k + 0 = k
  | succ k ih =>
    -- 目标：(k+1) + 0 = (k+1)
    -- simp 用化简规则 + 归纳假设自动搞定
    simp [Nat.succ_eq_add_one, ih]
```

**逐行解读**：
| 代码 | 作用 |
|------|------|
| `theorem add_zero (n : ℕ) : n + 0 = n` | 声明定理，`ℕ` 是自然数类型 |
| `:= by` | 进入 tactic 模式（交互式证明） |
| `induction n with` | 对 n 做归纳 |
| `\| zero => rfl` | 基例：`rfl` 证明定义相等 |
| `\| succ k ih => simp [...]` | 归纳步：`ih` 是归纳假设，`simp` 自动化简 |

> 💡 Mathlib 里已经有 `Nat.add_zero`（证明 `n + 0 = n`），你不需要自己证。但**自己证一遍是学 Lean 的最佳方式**。

### 用 tactic 自动证明（进阶）

Lean 有强大的自动化 tactic：

```lean
-- norm_num：专门处理数值计算
theorem calc_proof : 2^10 = 1024 := by norm_num

-- ring：处理交换环等式
theorem ring_proof (x y : ℤ) : (x + y)^2 = x^2 + 2*x*y + y^2 := by ring

-- linarith：处理线性不等式
theorem linear_proof (x y : ℝ) (h1 : x > 0) (h2 : y > 0) : x + y > 0 := by linarith

-- nlinarith：非线性不等式
example (x : ℝ) (h : x^2 < 4) : -2 < x ∧ x < 2 := by nlinarith
```

这些 tactic 像你的"自动证明助手"——你给目标，它们尝试用对应理论自动证明。

---

## 📈 学习路径（4 阶段）

### 阶段 0：尝鲜（2-4 小时）
- ✅ 玩 [Natural Number Game](https://adam.math.hhu.de/)（通关 = 掌握归纳法）
- ✅ 读 [Mathematics in Lean](https://leanprover-community.github.io/mathematics_in_lean/) 前 3 章

### 阶段 1：基础（1-2 周，配合 [01-track/stage-1](../../01-track/stage-1-本科核心/)）
- 学会常用 tactic：`intro / apply / exact / rw / simp / induction / ring / norm_num`
- 能把本科证明（集合 / 函数 / 数论基础）翻译成 Lean
- 目标：形式化你 [NOTES_TEMPLATE.md](../../NOTES_TEMPLATE.md) §4 的一个证明

### 阶段 2：进阶（1-3 月，配合 [01-track/stage-2](../../01-track/)）
- 读 Mathlib 源码，学风格
- 能用 Mathlib 现有定理组合证明
- 尝试给 mathlib 提 PR（从证明一个小引理开始）

### 阶段 3：研究级（阶段 3，[01-track/stage-3](../../01-track/)）
- 形式化你的研究方向的核心定理
- 关注 [14-frontier/AI-for-Math/](.) 的 AlphaProof 进展——AI 可能帮你生成 Lean 证明草稿

---

## 📦 关键资源清单

| 资源 | 链接 | 用途 |
|------|------|------|
| **Lean 官方文档** | [leanprover.github.io](https://leanprover.github.io/) | 语言手册 |
| **Mathlib 文档** | [leanprover-community.github.io/mathlib4_docs/](https://leanprover-community.github.io/mathlib4_docs/) | 查定理（像查字典）|
| **Mathematics in Lean** | [leanprover-community.github.io/mathematics_in_lean/](https://leanprover-community.github.io/mathematics_in_lean/) | 官方交互教程 ⭐ |
| **Natural Number Game** | [adam.math.hhu.de](https://adam.math.hhu.de/) | 新手游戏 ⭐ |
| **Lean Zulip** | [leanprover.zulipchat.com](https://leanprover.zulipchat.com/) | 社区问答（数学家都在）|
| **Mathlib GitHub** | [github.com/leanprover-community/mathlib4](https://github.com/leanprover-community/mathlib4) | 源码 + 贡献 |
| **Kevin Buzzard 博客** | [xena.io](https://xena.io/) | 帝国理工 Lean 推广者 |
| **Terence Tao 博客** | [terrytao.wordpress.com](https://terrytao.wordpress.com/) | 经常讨论 Lean |
| **lean4web** | [live.lean-lang.org](https://live.lean-lang.org/) | 在线编辑器 |

---

## 🔗 与项目其他模块的连接

| 你想... | 跳到 |
|---------|------|
| 理解 Curry-Howard 同构（命题=类型，证明=程序）| [16-foundations/Curry-Howard/](../../16-foundations/Curry-Howard/) |
| 理解依赖类型论（Lean 的数学基础）| [16-foundations/类型论/](../../16-foundations/类型论/) |
| 看 AI 怎么用 Lean 做数学 | [01-AI正在重写数学研究.md](01-AI正在重写数学研究.md) |
| 形式化你笔记里的证明 | [NOTES_TEMPLATE.md](../../NOTES_TEMPLATE.md) §4（加一个"Lean 验证"子节）|
| 用 Lean 做研究方向 | [17-decision/](../../17-decision/)（选方向后形式化核心定理）|
| 找 Lean 学习社区 | [18-resources/社区/](../../18-resources/社区/) |

---

## ⚠️ 常见坑

| 坑 | 表现 | 解药 |
|----|------|------|
| **装不上** | `lake build` 卡住 / 内存爆 | 先用在线编辑器；本地需 8GB+ 内存 |
| **找不到定理** | "这个定理 mathlib 有吗" | 查 [Mathlib 文档](https://leanprover-community.github.io/mathlib4_docs/)，或在 Zulip 问 |
| **tactic 不工作** | `simp` 没证出来 | 加具体引理参数 `simp [xxx]`，或换 `rw` 手动重写 |
| **过度依赖自动化** | 全靠 `simp` 不理解证明 | 先手写，再让 `simp` 检查你的理解对不对 |
| **版本不匹配** | Lean 4 vs mathlib 版本冲突 | 用 `elan` 管理版本，`lake update` 同步 |

---

## 📊 时效声明

- 本指南事实截至 **2024 年底 / 2025 年初**
- Mathlib 规模每月增长，具体数字查 [Mathlib GitHub](https://github.com/leanprover-community/mathlib4)
- AlphaProof 进展查 [14-frontier/conjecture进展/](../conjecture进展/) 和 DeepMind 官方
- 每年 ICM 后（8 月）+ 年底（12 月）刷新一次

---

> 💡 **心法**：学 Lean 不是"学一个工具"，是**给你的数学证明加一道机器验证的保险**。即使你只用它验证本科证明，也比手写证明多一层确定性。从 Natural Number Game 开始，2 小时后你会有第一个"机器保证对"的证明。
