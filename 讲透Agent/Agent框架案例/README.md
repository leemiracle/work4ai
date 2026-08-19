# Agent 框架案例 · 索引

> 一句话定位：**Agent 的"骨架"——harness 层（进程/循环/工具/沙箱/审批）的开源实现源码级解剖。**
>
> 与 [`Agent上下文案例/`](../Agent上下文案例/)（上下文层：单次任务内给模型看什么代码）、[`Agent记忆系统案例/`](../Agent记忆系统案例/)（记忆层：跨会话知识）平行，本目录是**框架层**：agent 进程怎么跑起来、能力怎么接缝、信任平面怎么设计。
>
> 🌐 **生态观测锚点（2026-08-15）**：[`../../透视GitHub-Harness高星仓库全景.md`](../../透视GitHub-Harness高星仓库全景.md)——topic:harness 高星 37 仓快照与概念卡（五子系统/四层栈），本目录 dsh 案例是其中一个实现样本；方法蒸馏见 [`../../harness精华合入-总入口.md`](../../harness精华合入-总入口.md)。同日新增组织级纵深：DeepSeek 开源全景分析（已并入 [`../../讲透DeepSeek/README.md`](../../讲透DeepSeek/README.md)，dsh 双头下注分析的最新增量底稿 G）。**Skills 侧姊妹锚点（2026-08-19）**：[`Skills生态全景/`](Skills生态全景/README.md)——topic:skills 11,492 仓快照。

| 案例库 | 内容 | 状态 |
|---|---|---|
| **deepseek-harness插件化框架/** | DeepSeek 官方开源 agent harness（dsh，219 插件包）源码级深读：核心运行时（turn/step 状态机、事件日志）/ 能力接缝 + 插件机制全景 / 信任平面（沙箱、审批、供应链）/ 装配与外部接口 / DeepWiki 对照增补 / dsh-plugin 生态分析（star>66 共 59 仓），12 篇笔记全部行号钉版（HEAD `47f943859b`，2026-08-13） | 已完成 |
| **MCP协议生态全景/** | github.com/topics/mcp（64,438 仓）知识集成：生态统计与六赛道（top41 + awesome 3,371 条双口径对账）/ **2026-07-28 规范无状态化重构**（删 initialize 握手/session/ping，弃用 Sampling/Roots/Logging，MRTR 模式）/ 官方 org 与 SDK v2 格局（Registry 诞生、FastMCP 独立版）/ 项目内 MCP 知识互链网（10+ 处散落资产织网），快照 2026-08-19 | 已完成 |
| **Skills生态全景/** | github.com/topics/skills（11,492 仓）知识集成：**语义迁移铁证**（top500 中 79% 创建于 2025-10 后，"人类技能"→"Agent Skills"）/ 规范演进一手时间线（2025-10-16 发布 → 2025-12-18 开放标准 → 48h MS/OpenAI 跟进 → 2026-06 40+ 工具）+ SKILL.md 逐字段解剖 + progressive disclosure 三层预算 / 七赛道地图 + 20 张重点仓深读卡（anthropics 170,317★ 实测+topic 盲区证据、superpowers 273,749★、讯飞 skillhub）/ Skills vs MCP vs Plugins 三层分工与项目互链网，快照 2026-08-19 | 已完成 |
| **Topics全链路全景/** | **全链路总纲**：Prompt→Context→MCP/Skills→微调/对齐→推理/模型 十层 GitHub topics 索引体系，68 个核心 topics 逐个 API 实测（2026-08-19，数据留档 data/）+ 三家素材对账仲裁（纠正 Kimi 报告 fine-tuning 错 67 倍/RAG 漏主 topic 45 倍/MCP 长短名差百倍）+ 每层使用背景/代表仓/批判 + 5W2H/第一性原理/SWOT/成本阶梯四方法收束；L3/L4 层由 MCP/Skills 两个深潜篇承载 | 已完成 |

## 速查：什么问题查哪里

- **harness 整体架构 / "一切皆插件"** → `deepseek-harness插件化框架/notes/00-overview/`
- **插件机制与能力接缝** → `notes/02-capability-seams/`
- **沙箱/审批/供应链安全** → `notes/03-trust/`
- **插件生态格局** → `notes/07-ecosystem/`
- **MCP 生态格局 / 规范演进（2026-07-28 无状态化）/ SDK 选型** → `MCP协议生态全景/notes/`
- **Skills 生态格局 / SKILL.md 怎么写 / Skills vs MCP vs 插件分工 / superpowers 等方法论选型** → `Skills生态全景/notes/`
- **全链路技术选型 / 某层该用哪个 topic 检索 / 各层代表仓 / 微调 vs RAG 决策** → `Topics全链路全景/notes/`（十层总纲，06 篇含成本阶梯）
- **配套反欺骗实验** → [`../../欺骗动力学-AI纪实验包.md`](../../欺骗动力学-AI纪实验包.md)
