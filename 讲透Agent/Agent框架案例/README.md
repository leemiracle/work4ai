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
| **openclaw/** | 2026 现象级个人 AI 助手（**386,825★/9 个月**，HEAD `f612675284`，2026-08-20）源码级解剖：六组件实证（42 挂点/steering 原语/tool-call-repair 2900 行）/ 协议中枢与插件面（gateway-protocol 极简主义、模型=catalog 数据）/ 安全平面（四档权限/pairing 审批/net-policy fail-closed，PRISM 插件实地锚）/ **可借鉴与缺点清单**（按件拆借别整屋搬），5 篇笔记全部行号钉版 | 已完成 |
| **claw-code/** | Claude Code 泄露（2026-03-31，512K 行 TS 经 npm .map 裸奔）后的**净室重写**（2h50K star，HEAD `08106b0` 2026-08-16，1690 commits/11 crates/**115,957 行 Rust**）源码级解剖：Rust 正典 harness 六组件实证（ConversationRuntime 压缩内嵌循环/动态边界系统提示/五档权限双层/55 工具含 Worker* 舰队 9 件套）/ **治理档案**（PARITY 9-lane 对拍+g002-g013 质量门+.omx Ralph 回执——agent 自管仓库最完整标本）/ Python 镜像层移植方法学+claw-analog NDJSON+旁路 RAG 三产品线 / 泄露叙事对账（7 篇解读文献地图）与"博物馆化"收尾，5 篇笔记全部行号钉版 | 已完成 |
| **ClaudeCode源码深读/** | **Claude Code 本体泄露源码**（v2.1.x，1884 文件/**512,664 行 TS** 实测，本地 `~/ai/agent/awesome-agents/repos/claude-code-source` 钉版 `091cde4` + 20 篇配套拆解）file:line 级深读，7 篇笔记：启动链路（快路径分发/预取竞速/ABLATION 消融基线）/ **queryLoop 显式状态机**（7 continue/10 Terminal/五级压缩链/withhold）/ 工具系统与 Bash 三层防线（AST→策略→沙箱，23 项解析器差异攻击编目）/ **上下文工程三件套**（哨兵边界装配/缓存闩锁/五层压缩）/ 记忆系统（文件即记忆/autoDream 做梦/无向量库）/ 权限管线（编号求值步骤/分类器竞速/影子规则）/ 多 Agent 三层体系+隐藏面（89 feature flag/buddy/undercover/anti-distillation 反蒸馏投毒）。抽查 6 处行号引用全部与源码一致 | 已完成 |

## 速查：什么问题查哪里

- **harness 整体架构 / "一切皆插件"** → `deepseek-harness插件化框架/notes/00-overview/`
- **个人助手 / 常驻 Gateway / steering 夺回控制权 / 工具调用修复** → `openclaw/notes/`
- **42 挂点全景 / 会话权限四档 / SSRF 防火墙原语** → `openclaw/notes/02-六组件实证.md` 与 `04-安全平面.md`
- **插件机制与能力接缝** → `notes/02-capability-seams/`
- **沙箱/审批/供应链安全** → `notes/03-trust/`
- **插件生态格局** → `notes/07-ecosystem/`
- **MCP 生态格局 / 规范演进（2026-07-28 无状态化）/ SDK 选型** → `MCP协议生态全景/notes/`
- **Skills 生态格局 / SKILL.md 怎么写 / Skills vs MCP vs 插件分工 / superpowers 等方法论选型** → `Skills生态全景/notes/`
- **全链路技术选型 / 某层该用哪个 topic 检索 / 各层代表仓 / 微调 vs RAG 决策** → `Topics全链路全景/notes/`（十层总纲，06 篇含成本阶梯）
- **Claude Code 架构 / harness 组件教材（主循环/系统提示动态边界/权限拒绝回注/上下文压缩）** → `claw-code/notes/02-Rust正典harness解剖.md`
- **agent 自管仓库 / PARITY 对拍 / 质量门 / 反 slop 治理** → `claw-code/notes/03-治理系统与agent自管证据.md`
- **Claude Code 泄露源码本体（TS）逐模块深读 / queryLoop 状态机 / 五层压缩 / Bash 三层防线 / 记忆系统 / 权限编号步骤 / 多 Agent 账本 / feature flag 隐藏面** → `ClaudeCode源码深读/notes/`（7 篇，全部 file:line）
- **配套反欺骗实验** → [`../../欺骗动力学-AI纪实验包.md`](../../欺骗动力学-AI纪实验包.md)
