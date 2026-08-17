---
card_id: CG-00
title: "讲透代码生成：从模板到 Agentic 的四时代"
universe: 讲透代码生成
burke:
  scene: "LLM 能写代码了，但不可靠、会幻觉、多步就崩"
  agent: "想用 AI 真正提效（而非被它带坑）的工程师"
  agency: "模板/AST/统计生成/Agentic 循环 + 约束解码 + 工具调用"
  act: "从'AI 补全一行'到'AI 独立完成一个 feature 并自检'"
  purpose: "在效率与正确性之间找到可信赖的工程化路径"
tension: "LLM 生成的统计流畅性 ≠ 程序的语义正确性——看起来对跑起来错"
arc: [直觉(四时代), 数学(为什么会生成), 代码(最小回路), 不足(失败模式), 应用(Agent化工作流)]
status: in_progress
next_card: CG-01
refs:
  - "Chen et al., Codex, 2021"
  - "Jimenez et al., SWE-bench, 2024"
  - "Wang et al., CodeAct, 2024"
  - "Cursor 1.x, 2025"
  - "Anthropic, Claude Code, 2025"
  - "Model Context Protocol (MCP), 2024-2025"
updated: 2026-08-13
---
# 💻 讲透代码生成：从模板到 Agentic 的四时代

> **User Story**：作为一个想用 AI 写代码的人，我想理解代码生成的演化谱系与边界，以便选对工具链而不被营销忽悠。

## 🎭 戏剧张力

代码生成表面繁荣（Copilot 接受率、Cursor 融资、Devin demo），但本质冲突尖锐：

> **自然语言的统计流畅性 ≠ 程序的语义正确性。** LLM 写出「看起来完全对」的代码，调用了不存在的 API、漏了边界条件、多步推理后悄悄跑偏——而编译器/测试是唯一真相。

整部「讲透代码生成」都在回答：**如何让统计生成变成可信赖的工程？**

## 📚 五幕总览

| 幕 | 文件 | 一句话 |
|---|---|---|
| 直觉 | `01-直觉-代码生成四时代.md` | 模板 → AST → 统计(Codex) → Agentic(CodeAct/Claude Code) |
| 数学 | `02-数学-为什么会生成与如何让它正确.md` | 代码=AST 概率分布；BPE 对代码的影响；约束解码（outlines/XGrammar）|
| 代码 | `03-代码-最小生成回路.md` | 一个能读改跑测的 150 行 agentic loop |
| 不足 | `04-不足-代码生成的失败模式.md` | 幻觉 API / 多步累积误差 / SWE-bench 真实差距 / 注入安全 |
| 应用 | `05-应用-Agent化代码工作流.md` | Cursor rules / AGENTS.md / skills / MCP / 并行多 agent |

## 🗺️ 四时代演化（核心叙事）

```
第 1 代 模板/宏        第 2 代 AST 规则       第 3 代 统计生成        第 4 代 Agentic
(1960s Lisp macro)   (2010s CodeQL/         (2021 Codex/           (2024-2026 CodeAct/
 确定性但死板           semgrep)              Copilot)               Claude Code/Cursor/
                      可分析但不会写         流畅但不可靠            Devin/OpenCode)
                      ↓                      ↓                       ↓
                   "能查不能写"           "能写不能信"           "能写能改能验证"
                                               ↑ 当前主战场 ↑
```

## 📊 2024-2026 真实进展标尺

- **SWE-bench Verified**（解决真实 GitHub issue）：从 2024 年初的 ~13% 到 2025 年 Claude 3.5 Sonnet 的 ~50%+，2026 年顶尖系统破 70%。**这仍是「半自动」，远未到「自动」**。
- **Claude Code / Cursor / OpenCode / Aider**：Agentic 模式成为主流——LLM 读文件→改→跑测试→看报错→再改的闭环。
- **MCP（Model Context Protocol）**：让 LLM 标准化接工具/数据源，是 code agent 的「USB-C」。
- **CodeAct**：用「代码作为 action」取代 JSON function calling，更灵活。

## 🔗 与其他宇宙的关系

- 与 **`Karpathy经典代码精读/`**（已有）：那边读别人的代码，这边让 AI 写代码。
- 与 **`讲透多Agent协作/`**：并行多 agent coding 需要 file ownership（见 `05`）。
- 与 **`讲透上下文缓存/`**：coding agent 的瓶颈往往是 context（Augment 60 万 token 的意义）。
- 外部论文流：[PaperAgent精华合入-总入口 §十三](../PaperAgent精华合入-总入口.md)——92 页 Vibe Coding 综述：五类开发模式（UAM/ICCM/PDM/TDM/CEM = 人的参与度坐标系）+ 四级反馈回路（编译 RLCF +45% / 运行 TDD / 人类 ClarifyGPT / 自反思 Reflexion +11%——与本项目"迭代即熵泵"洞察互证）+ Agent-as-a-Job。

## 💡 核心洞察

> **代码生成的本质是「把自然语言的不确定性收敛到 AST 的确定性结构」。** 第 4 代 Agentic 之所以比第 3 代统计生成更可靠，不是因为模型更强，而是因为它把「生成-执行-反馈」闭合成了**耗散结构**：每一轮测试都是负熵注入，把统计噪声泵出系统。这就是为什么 SWE-bench 分数能持续爬升——**迭代即熵泵**。

---
📌 **下一步**：逐章填充，重点在 `03`（可跑回路）和 `04`（失败模式，这是工程师最需要的）。
