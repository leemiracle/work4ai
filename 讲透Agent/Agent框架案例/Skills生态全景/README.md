# Skills 生态全景（github.com/topics/skills）· 索引

```yaml
card_id: skills-ecosystem-panorama
title: Agent Skills 生态全景——github.com/topics/skills 知识集成
universe: Agent框架案例
burke:
  场景: 2025-10 Anthropic 发布 Agent Skills 后，"skill"从人类学习资源语义迁移为 AI 技能包标准，GitHub topic:skills 一年膨胀至 11,492 仓
  主体: AI coding agent（Claude Code/Codex/Cursor/Gemini CLI/OpenCode 等 40+ 工具）与它们的开发者
  能动: Anthropic（标准发起）、大厂官方仓（Google/Microsoft/Cloudflare/Android/讯飞）、方法论作者（obra/addyosmani）、中文创作社区
  行动: 用文件夹+SKILL.md（2 个必填字段+Markdown 正文）打包程序性知识，经 progressive disclosure 按需加载，跨 40+ 工具免改复用
  目的: 把"教 agent 做事"从每次重讲的 prompt 变成可版本控制、可团队共享、可跨工具携带的文件资产
  张力: 供给爆炸（1,497+ 收录/AI 批量生成 slop）vs 治理缺位（校验不防恶意/40+ 实现语义漂移）；极简规范带来的 48 小时闪电采纳 vs context rot 装载代价
  弧线: Claude 私有功能(2025-10-16) → 开放标准(2025-12-18) → 48h 对手跟进 → 2026-03 32+ 工具 → 企业 registry/治理萌芽（下一站）
status: 已完成（快照 2026-08-19）
refs:
  - GitHub Search API topic:skills（11,492 仓，top500 样本实测）
  - agentskills.io/specification、anthropics/skills、openai/skills（API 实测 star）
  - 20+ 重点仓 README raw 抓取（2026-08-19）
updated: 2026-08-19
```

> 一句话定位：**github.com/topics/skills（11,492 仓）的知识集成**——Agent Skills 规范的演进与解剖、生态七赛道地图、20 张重点仓库深读卡、与项目内 MCP/harness/prompt 手册知识的互链网。姊妹篇：[`../MCP协议生态全景/`](../MCP协议生态全景/)（topics/mcp 64,438 仓）；**总纲**：[`../Topics全链路全景/`](../Topics全链路全景/README.md)（十层 topics 索引体系，本目录是其 L4 层深潜样本）。

## 四篇导读

| 篇 | 内容 | 何时查 |
|---|---|---|
| [`notes/01-生态统计与赛道地图.md`](notes/01-生态统计与赛道地图.md) | 11,492 仓快照口径；**语义迁移铁证**（top500 中 79% 创建于 2025-10 后）；逐月爆发曲线；语言分布；**七赛道**（方法论框架/官方厂牌/合集商店/注册分发/垂直技能/平台 skills 化/旧语义存量）；高星弱相关噪声样本；与 MCP 生态规模对照 | 想知道生态里都有谁、分几层、水有多深 |
| [`notes/02-规范演进与SKILL.md解剖.md`](notes/02-规范演进与SKILL.md解剖.md) | 时间线一手核实（2025-10-16 发布 → 2025-12-18 开放标准 → 48h MS/OpenAI 跟进 → 2026-06 40+ 工具）；SKILL.md 逐字段约束表；progressive disclosure 三层预算；跨工具安装路径矩阵；Skills vs MCP vs Plugins 三层分工；安全平面与治理缺口 | 要写 skill / 理解规范 / 做选型 |
| [`notes/03-重点仓库深读.md`](notes/03-重点仓库深读.md) | 20 张仓卡：官方厂牌 7（anthropics 170,317★ 实测+topic 盲区证据/openai/google/microsoft/cloudflare/android/gemini）；方法论 4（superpowers 273,749★/addyosmani/taste-skill/antfu 文档同步 POC）；合集商店/registry/垂直 9 | 找参考实现、选技能来源、看商业化形态 |
| [`notes/04-项目内Skills知识互链网.md`](notes/04-项目内Skills知识互链网.md) | 与 MCP 全景（插座vs手册/协议极简主义潮流）/ dsh 插件化（进程级vs context 级接缝）/ harness 全景 / prompt 手册 / 模型宇宙 Part IV 五条互链；**用户 opencode skills 目录即标准活案例** | 融会贯通、写新笔记找挂点 |

## 速查：什么问题查哪里

- **skills 生态格局/七赛道/中文社区形态** → `notes/01`
- **SKILL.md 怎么写/字段约束/500 行预算/校验工具** → `notes/02` §2
- **Skills 和 MCP/插件什么关系** → `notes/02` §4
- **官方大厂怎么组织 skills/evals 驱动选题/context rot** → `notes/03` A3-A6
- **装哪个方法论框架/superpowers 工作流** → `notes/03` B1-B2
- **企业私有技能治理** → `notes/03` D1（iflytek/skillhub）
- **安全风险（任意命令执行/slop 污染）** → `notes/02` §7

> 🔗 **2026-08-25 延伸**：本全景的"规范/生态"知识已扩展为教程单元 [`讲透Skills`](../../讲透Skills/README.md)（渐进披露经济学/触发路由机制/模型适配/自动优化工具栈/2026 六线研究地图/数学应用 + 实验室三实验全跑通）。本目录保持生态快照定位（2026-08-19 数据），动态更新以官方源为准（anthropics/skills 08-25 实测 171,450★）。
