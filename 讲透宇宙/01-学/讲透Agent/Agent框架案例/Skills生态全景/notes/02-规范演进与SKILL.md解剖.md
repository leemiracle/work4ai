# 02 · 规范演进与 SKILL.md 解剖：从 Claude 功能到 40+ 工具的事实标准

> 姊妹篇：[`01-生态统计与赛道地图.md`](01-生态统计与赛道地图.md)（生态面）。本篇讲**规范本身**：时间线（一手核实）、SKILL.md 逐字段解剖、progressive disclosure、与 MCP/Plugins 的三层分工、安全平面。所有关键日期均经 agentskills.io / Anthropic 工程博客 / 多方报道交叉核实（2026-08-19）。

---

## 1. 时间线（核实版）

| 日期 | 事件 | 来源 |
|---|---|---|
| 2025-09-22 | `anthropics/skills` 仓库创建（GitHub API 实测） | repos API |
| **2025-10-16** | Anthropic 工程博客发布 **Agent Skills**：SKILL.md + 渐进披露，Claude.ai / Claude Code / Agent SDK / Developer Platform 全支持 | anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills |
| 2025-10~12 | 社区跟进：superpowers（10-09 创建）、VoltAgent/awesome-agent-skills（10-28） | API created_at |
| **2025-12-18** | **开放为独立标准**：规格迁至 agentskills.io + 独立 GitHub org `agentskills/agentskills`；同步发布企业技能管理层与伙伴技能目录（Atlassian/Canva/Cloudflare/Figma/Notion/Ramp/Stripe/Zapier） | agentskills.io；VentureBeat 报道 |
| 2025-12-19/20 | **48 小时内**：Microsoft VS Code/Copilot 与 OpenAI ChatGPT/Codex CLI 跟进采纳（Simon Willison 12-19 称其 "a deliciously tiny specification"，12-20 Codex 文档上线） | simonwillison.net；三方报道 |
| 2026-01 | Google Antigravity 正式采纳 | neuralcoretech 时间线 |
| 2026 Q1 | Anthropic "Skills 2.0"：内置 evals + 企业治理控制 | neuralcoretech 时间线 |
| **2026-03** | 采纳过 **32+ 工具**：Gemini CLI、JetBrains Junie、AWS Kiro、Block Goose…… | iaieye/neuralcoretech |
| 2026-06 | agentskills.io 列出 **~40 支持产品**（含 Cursor、GitHub Copilot、OpenCode、Databricks、Snowflake）；skills.sh（Vercel）/Agensi 市场索引数万技能 | agentskills.io；devtoollab 2026-07-11 |

**关键节奏对比**：MCP 从发布到跨厂商跟进花了几个月；Agent Skills 只花了 **48 小时**。原因不是技术而是**规范尺寸**——全部规范 = 2 个必填 YAML 字段 + Markdown 正文，一个下午就能给任何工具加上支持（devtoollab 评）。

---

## 2. SKILL.md 规范解剖（agentskills.io/specification 一手）

### 2.1 目录结构

```
skill-name/
├── SKILL.md          # 必需：YAML frontmatter + Markdown 指令
├── scripts/          # 可选：可执行代码（agent 可直接 spawn 运行）
├── references/       # 可选：按需载入的参考文档
└── assets/           # 可选：模板/图/数据
```

### 2.2 frontmatter 字段全表

| 字段 | 必填 | 约束 |
|---|---|---|
| `name` | ✅ | 1–64 字符；小写字母/数字/连字符；不得首尾连字符、不得连续 `--`；**必须与父目录同名** |
| `description` | ✅ | 1–1024 字符；要同时写"做什么"+"何时用"——这是 agent 触发命中的唯一依据 |
| `license` | ❌ | 许可证名或捆绑 LICENSE 文件引用 |
| `compatibility` | ❌ | ≤500 字符；环境要求（目标产品/系统包/网络） |
| `metadata` | ❌ | string→string 任意 KV（客户端扩展位） |
| `allowed-tools` | ❌ | **实验性**：空格分隔的预批准工具，如 `Bash(git:*) Bash(jq:*) Read` |

最小合法示例：

```markdown
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
---
（正文：给 agent 的操作指令）
```

### 2.3 Progressive Disclosure（三层渐进披露）——规范的灵魂

| 层 | 加载时机 | 预算 |
|---|---|---|
| 1. metadata（name+description） | agent 启动时，全部技能 | ~100 tokens × N |
| 2. SKILL.md 正文 | 任务命中 description 时 | <5,000 tokens，**<500 行** |
| 3. scripts/references/assets | 正文显式引用且需要时 | 按需，理论无界 |

这一机制回答了"装 100 个技能为什么不爆 context"：闲置技能的常驻成本只有 frontmatter。**上下文经济学**：正文超 500 行就该拆到 references/；引用链建议只深一层（避免嵌套引用链）。

### 2.4 校验工具

```bash
npx skills-ref validate ./my-skill   # 检查 frontmatter 合法性/name 匹配目录名/引用存在
```

来自官方参考库 `agentskills/agentskills/skills-ref`。**注意：只查格式不查恶意**（见 §7）。

---

## 3. 跨工具安装路径矩阵（cloudflare/skills README 一手 + 报道补充）

| 工具 | 个人级路径 | 项目级路径 |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| **OpenCode** | `~/.config/opencode/skills/` | `.opencode/skill/` |
| OpenAI Codex | `~/.codex/skills/`（USER scope `~/.agents/skills/`） | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| GitHub Copilot | — | `.github/skills/` |
| Pi | `~/.pi/agent/skills/` | — |
| Claude API | `/v1/skills` endpoint 上传 | workspace 级 |

**通用安装命令**：`npx skills add <org>/<repo>`（skills.sh CLI，google/microsoft/antfu 官方推荐路径）。

> 🔗 **本项目即活案例**：work4ai 日常开发用的 opencode，其 `~/.config/opencode/skills/` 下 30+ 技能正是这个标准——用户每天在用 Agent Skills。

**可移植性边界**：只用标准字段写的 skill 跨 40+ 工具免改；用到工具私有扩展（如 Claude Code 的 context-forking）则需调整。

---

## 4. 三层分工：Skills vs MCP vs Plugins

| | Agent Skills | MCP | Plugins（以 Claude Code 为例） |
|---|---|---|---|
| 本质 | **文件夹约定**（SKILL.md+资源） | client-server 协议（JSON-RPC over stdio/HTTP） | 分发打包格式（marketplace 条目） |
| 给 agent 什么 | 程序性知识（怎么做事，playbook） | 动态能力（调 API/查库，插座） | skills+commands+agents+MCP 配置的**捆绑交付** |
| 运行时 | 无（agent 自有工具执行） | 常驻 server 进程 | 无（装载器解析） |
| 失败模式 | 像坏 prompt 一样失败 | server 崩溃/鉴权过期/（旧版）session 状态漂移 | 供应链问题（第三方插件不可信） |
| 数据 vs 知识 | 知识稳定数周（changelog 格式、错误分类流程） | 数据每次变化（工单状态、DB 行、搜索结果） | — |

**Plugin 打包 Skills 的证据**（anthropics/claude-plugins-official README，2026-08-19 抓取）：plugin 结构含 `skills/` 目录；skill-bundle 插件可用 `strict: false + skills[]` 数组直接声明外部仓库的技能目录，注册为 `<plugin-name>:<skill-name>`。

**实战组合**：MCP 拉 GitHub issue（动态数据）→ Skill 定义 triage 步骤（静态流程）。MCP 是神经系统，Skills 是操作手册——Anthropic 官方定位 skills"补足 MCP server，教涉及外部工具的更复杂工作流"。

---

## 5. 标准设计课：极简主义的胜利

1. **规范尺寸决定采纳速度**。MCP 先证明"开放标准换生态"路线可行，但 JSON-RPC/握手/session 的复杂度让采纳以月计，并最终在 2026-07-28 走向**无状态化瘦身**（删 initialize/session/ping，见姊妹篇 [`../../MCP协议生态全景/notes/02-协议演进2026-07-28.md`](../../MCP协议生态全景/notes/02-协议演进2026-07-28.md)）。Skills 一开始就只有 2 个必填字段——**MCP 在做减法的方向，是 Skills 出生的位置**。
2. **复用已有执行面**。Skills 不定义协议、不定义运行时，直接搭 agent 已有的文件系统+代码执行工具的便车。渐进披露本质是"把 context 管理问题转化为文件组织问题"。
3. **公司路线重复验证**：自家用（2025-10 Claude 功能）→ 验证有用 → 开放标准换生态（2025-12-18）→ 对手 48 小时跟进。与 MCP 完全同构，速度更快。
4. **版本治理留白是隐忧**：40+ 工具各自实现，"同一份手册谁保证读出同一个意思"是 2026 下半年的成熟度指标（signals.tw）。`allowed-tools` 还在实验期，各端行为不一。

---

## 6. topic 检索盲区（方法论警示）

生态核心仓**不在** topic:skills 榜单：anthropics/skills（170,317★，只挂 agent-skills）、openai/skills（25,028★）。检索该主题必须双关键词（`skills` + `agent-skills`）+ awesome 清单对账，否则漏掉的就是最重要的官方仓。此教训与 MCP 笔记"awesome 对账"方法一致。

---

## 7. 安全平面（必须直视）

1. **信任边界 = Bash**：skill 正文可以指示 agent 执行任意命令，scripts/ 可以 curl 外部主机——与 Bash-capable MCP server 同级信任边界，但讨论度低得多（devtoollab 警告）。
2. **校验工具不防恶意**：`skills-ref validate` 只查格式；恶意指令藏在正文里它不管。
3. **供给端污染**：AI 批量生成技能泛滥（awesome 清单以 "not AI-slop generated" 为卖点反证）；Claude-Red（2,941★）这类攻击安全技能库是双刃。
4. **治理萌芽**：tech-leads-club "validated registry"、iflytek/skillhub 企业内部 namespace、Skills 2.0 企业治理控制、Claude 官方 marketplace 的 `renames` 自动迁移机制——四处信号汇成一个方向：**供给爆炸之后，下一站是准入与审计**。

---

## refs
- agentskills.io/specification（2026-08-19 webfetch）
- anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills（2025-10-16，含 2025-12-18 开放标准 update 注记）
- github.com/agentskills/agentskills（规范仓）
- cloudflare/skills、anthropics/claude-plugins-official、microsoft/skills、antfu/skills、android/skills README（2026-08-19 raw 抓取）
- devtoollab.com/blog/agent-skills-open-standard-guide（2026-07-11）、neuralcoretech.com（2026-06-17）、blog.iaieye.com（2026-05-05）、signals.tw（2026-07-05）——三方交叉

*updated: 2026-08-19*
