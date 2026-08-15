# 01 · 现有 Skills 审计报告

> **审计对象**：`~/.config/opencode/skills/` 37 个 AI/编程 skill
> **审计日期**：2026-08-13
> **审计方法**：扫所有 SKILL.md，按 description + 内容分类、评分、识别冗余

---

## 📊 总体统计

| 指标 | 数值 |
|---|---|
| **总 skill 数** | 37 |
| **平均行数** | ~100 行/SKILL.md |
| **总行数** | ~3700 行 |
| **有 description** | 35/37（2 个空：`prompt-optimize`、`question`）|
| **含跨 skill 协作段** | ~10/37（27%）|
| **含资源链接** | ~25/37（68%）|

---

## 🗂️ 5 大类分类

### 类别 1 · AI 学习（12 个，32%）

| Skill | 行数 | 用途 | 评价 |
|---|---|---|---|
| `concept-3layer` | 38 | 概念三层讲解（直觉→公式→代码）| ⭐⭐⭐⭐ 简洁实用 |
| `cv-learning` | 139 | CV 全栈学习 | ⭐⭐⭐⭐ 内容丰富 |
| `llm-mastery` | 162 | LLM 全栈学习 | ⭐⭐⭐⭐⭐ 核心 |
| `math-learning` | 90 | 数学学习 | ⭐⭐⭐⭐ |
| `ml-theory` | 145 | ML 理论精讲 | ⭐⭐⭐⭐⭐ 核心 |
| `nlp-learning` | 138 | NLP 全栈 | ⭐⭐⭐⭐ |
| `rl-learning` | 132 | 强化学习 | ⭐⭐⭐⭐ |
| `paper-deepread` | 51 | 论文精读（轻量）| ⭐⭐⭐ 与 paper-mastery 重叠 |
| `paper-mastery` | 135 | 论文精读（详尽）| ⭐⭐⭐⭐⭐ 保留这个 |
| `learning-methodology` | 135 | 学习方法论 | ⭐⭐⭐⭐ |
| `progress-tracker` | 48 | 进度追踪 | ⭐⭐⭐⭐ |
| `frontier-briefing` | 37 | 前沿简报 | ⭐⭐⭐⭐ |

### 类别 2 · 软件工程（13 个，35%）

| Skill | 行数 | 用途 | 评价 |
|---|---|---|---|
| `code-review-workflow` | 112 | 代码审查 | ⭐⭐⭐⭐ |
| `debug-helper` | 126 | Debug 工作流 | ⭐⭐⭐⭐ 与 diagnose 重叠 |
| `diagnose` | 93 | 诊断循环 | ⭐⭐⭐⭐ 与 debug-helper 重叠 |
| `git-workflow` | 131 | Git 工作流 | ⭐⭐⭐⭐⭐ |
| `grill-with-docs` | 56 | 拷问计划 | ⭐⭐⭐⭐ |
| `impl-from-scratch` | 42 | 从零实现 | ⭐⭐⭐⭐ |
| `improve-codebase-architecture` | 66 | 改善架构 | ⭐⭐⭐⭐ |
| `karpathy-guidelines` | 92 | Karpathy 编码原则 | ⭐⭐⭐⭐⭐ |
| `prototype` | 53 | 原型设计 | ⭐⭐⭐ |
| `refactor-guide` | 92 | 重构指南 | ⭐⭐⭐⭐ |
| `tdd` | 101 | 测试驱动 | ⭐⭐⭐⭐ |
| `to-issues` / `to-prd` | 73 / 73 | 计划转 issues/PRD | ⭐⭐⭐ |
| `triage` | 72 | issue 分诊 | ⭐⭐⭐ |
| `zoom-out` | 66 | 拉远视角 | ⭐⭐⭐ |
| `repo-scan` | 109 | 代码库智能 | ⭐⭐⭐⭐ |

### 类别 3 · AI 工程（5 个，14%）

| Skill | 行数 | 用途 | 评价 |
|---|---|---|---|
| `agent-development` | 172 | Agent 开发 | ⭐⭐⭐⭐⭐ |
| `ai-deployment` | 131 | 模型部署 MLOps | ⭐⭐⭐⭐ |
| `ml-experiment` | 187 | 实验设计 | ⭐⭐⭐⭐⭐ |
| `prompt-engineering` | 160 | Prompt 工程 | ⭐⭐⭐⭐⭐ 与新 prompt 手册互补 |
| `prompt-optimize` | 64 | Prompt 优化（**description 空**）| ⭐⭐ 需重写 |

### 类别 4 · 研究方法（4 个，11%）

| Skill | 行数 | 用途 | 评价 |
|---|---|---|---|
| `deep-research` | 160 | 深度研究 | ⭐⭐⭐⭐⭐ |
| `question` | 173 | 七层提问（**description 几乎空**）| ⭐⭐⭐ 需补 description |
| `research-companion` | 119 | 研究全周期 | ⭐⭐⭐⭐ |
| `trending-projects` | 102 | GitHub trending | ⭐⭐⭐⭐ |

### 类别 5 · 工作流（3 个，8%）

| Skill | 行数 | 用途 | 评价 |
|---|---|---|---|
| `customize-opencode` | - | 配置 opencode | ⭐⭐⭐⭐ |
| `skill-creator`（agents 目录）| - | 创造 skill | ⭐⭐⭐⭐ |

---

## 🚨 发现的 5 大问题

### 问题 1 · 冗余（4 组重叠）

| 重叠组 | 建议 |
|---|---|
| `paper-deepread` (51 行) vs `paper-mastery` (135 行) | **合并到 paper-mastery**，paper-deepread 降为 alias |
| `prompt-engineering` (160 行) vs `prompt-optimize` (64 行，空 desc) | **删 prompt-optimize**，prompt-engineering 已含优化 |
| `debug-helper` (126 行) vs `diagnose` (93 行) | **合并**：debug-helper 偏 bug，diagnose 偏性能。可保留两个但明确边界 |
| `concept-3layer` (38 行) vs `question` (173 行) | **明确分工**：concept-3layer 快速三层讲，question 七层深问 |

### 问题 2 · 空 description（2 个）

| Skill | 问题 | 修复 |
|---|---|---|
| `prompt-optimize` | description 完全空 | **要么删，要么补** |
| `question` | description 空 | **必补**（不然无法触发）|

### 问题 3 · 缺跨 skill 协作段（27/37 缺）

只有 ~10 个 skill 有 "跨 Skill 协作" 段。**这是 opencode 多 skill 联动的核心机制**。

**建议**：所有 ⭐⭐⭐⭐+ skill 必须加协作段。

### 问题 4 · 缺更新机制

37 个 skill 都没"最后更新日期" + "版本号"。**容易过时**。

**建议**：每个 SKILL.md 顶部加 `<!-- updated: YYYY-MM-DD -->`。

### 问题 5 · 金融 skill 在另一个目录

`~/.agents/skills/` 有 60+ 金融 skill（dcf-model / lbo-model / 3-statement-model / cim-builder 等）。**与 AI skill 完全分离**。

**建议**：要么移到 `~/.config/opencode/skills/`（统一管理），要么明确两边职责。

---

## 🎯 推荐的 8 个核心 skill（**用户顶级专家目标相关**）

按你 GAP_ANALYSIS 路线（数学前置 + interp 方向 + 社群 + 产出），最相关的 8 个：

| 优先级 | Skill | 为什么 |
|---|---|---|
| 🔴 P0 | `paper-mastery` | 读 interp 论文 |
| 🔴 P0 | `frontier-briefing` | 跟踪前沿 |
| 🔴 P0 | `ml-theory` | 数学 + 理论 |
| 🔴 P0 | `learning-methodology` | 学习方法 |
| 🟠 P1 | `progress-tracker` | 追踪进度 |
| 🟠 P1 | `concept-3layer` | 学新概念 |
| 🟠 P1 | `deep-research` | 系统调研 |
| 🟡 P2 | `llm-mastery` | interp 基础 |

**建议冻结**（不删，但不优先用）：cv-learning / nlp-learning / rl-learning / agent-development / ai-deployment（这些和 interp 方向相关性低）

---

## 📋 整理 Action 清单

### 立即做（30 分钟）
- [ ] 给 `prompt-optimize` 补 description（或删）
- [ ] 给 `question` 补 description
- [ ] 合并 `paper-deepread` → `paper-mastery`

### 本周做（2 小时）
- [ ] 给 8 个 P0/P1 skill 加 "跨 Skill 协作" 段
- [ ] 给所有 skill 加 `<!-- updated: 2026-08-13 -->` 头部
- [ ] 跑 ``06-审计脚本`` 验证

### 本月做
- [ ] 写新 skill `expert-track`（顶级专家路径，见 [`05-实战`](05-实战-写expert-track新skill.md)）
- [ ] 写新 skill `paper-to-blog`（论文转 blog，配合产出节奏）
- [ ] 写新 skill `interp-lab`（ mech interp 实验工作流）
- [ ] 评估金融 skill 是否移过来

---

## 📊 评分汇总

| 类别 | 总分 | 平均 | 最佳 | 最差 |
|---|---|---|---|---|
| AI 学习 | ⭐⭐⭐⭐ | 4.0 | paper-mastery / ml-theory | paper-deepread（冗余）|
| 软件工程 | ⭐⭐⭐⭐ | 3.8 | git-workflow / karpathy | to-issues（弱）|
| AI 工程 | ⭐⭐⭐⭐ | 4.2 | agent-development | prompt-optimize（空）|
| 研究方法 | ⭐⭐⭐⭐ | 4.0 | deep-research | question（空 desc）|
| **整体** | **⭐⭐⭐⭐** | **3.9/5** | - | - |

**结论**：37 个 skill 总体质量不错，但有冗余和空 description。删 2-3 个 + 合并 2 组 + 补 description = 升到 4.3/5。

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**37 个 skill 像工具箱。10 把螺丝刀不如 1 把好用的 + 知道在哪。**

---

## 📥 增补记录（审计快照之后的新装技能）

| 日期 | # | Skill | 来源 | 说明 |
|---|---|---|---|---|
| 2026-08-15 | 38 | `eng-ponytail-lazy-senior` | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)（102.9K★，星/月榜 #1） | 最懒资深工程师：七级懒梯（YAGNI→复用→stdlib→平台原生→已有依赖→一行→最少代码）。MIT 原文忠实移植，触发词含 "ponytail"/"be lazy"/"yagni"/"simplest solution"。基准：~54% 更少代码/~20% 更便宜/~27% 更快（可复现）。**首个带生产级基准报告的本地技能**——解构卡见 [`07-案例-ponytail`](07-案例-ponytail最懒资深工程师.md) |

> 审计口径：v1.0 快照为 37 个（2026-08-13）；增补不回改快照表，只在此登记。
