---
card_id: mcp-ecosystem-04-intra-project-map
title: work4ai 项目内 MCP 知识互链网——10+ 处散落资产的总地图与学习路径
universe: 讲透Agent/Agent框架案例/MCP协议生态全景
burke:
  场景: 本项目学习者要系统掌握 MCP，却不知道知识已散落在 10+ 个单元
  主体: work4ai 全库 MCP 相关资产（手册/用例库/案例卡/讲透单元）
  能动: 本案例（生态全景）作为索引枢纽
  行动: 盘点→分五层（协议/实操/生态/案例/工具面）→织互链→给学习路径
  目的: 一个入口找到全项目所有 MCP 知识，消灭重复建设
  张力: 生态膨胀（6.4万仓）vs 学习带宽（人的四档听说读写）
  弧线: 2026-08 各单元各自提及 MCP → 本案例收拢成网，孤儿变枢纽
status: 已完成
refs:
  - 用例库 README：「60/278（22%）的 README 显著提及 MCP——MCP 已成为 AI 工具的事实连接标准」
  - 工程化手册库 README：MCP 列 13 手册第 2 位
updated: 2026-08-19
---

# work4ai 项目内 MCP 知识互链网

> 一句话：**本项目 MCP 知识此前散落 10+ 处（手册/用例库/4 个案例目录/3 个讲透单元），本篇把它们按"协议→实操→生态→案例→工具面"五层织成一张网，此后学 MCP 从这里进。**

## 1. 五层资产地图

### L1 协议层（MCP 是什么、往哪去）

| 资产 | 位置 | 内容 |
|---|---|---|
| MCP工程手册 §1-3 | [`工程化手册库/MCP工程手册/README.md`](../../../../工程化手册库/MCP工程手册/README.md) | 是什么/为什么/USB 类比/SRCPT 解析框架（**2026-08 版，基于 2025 规范**） |
| 协议演进（本案例） | [02-协议演进2026-07-28](02-协议演进2026-07-28.md) | 2026-07-28 无状态化重构：删握手/session/ping，弃用 Sampling/Roots/Logging，MRTR 模式 |
| Agent Skills 对比 | [`前沿与媒体/103-AgentSkills开放标准深度解析.md`](../../../../前沿与媒体/103-AgentSkills开放标准深度解析.md) | Skills vs MCP 两条工具接入路线之争 |

### L2 实操层（怎么写、怎么评）

| 资产 | 位置 | 内容 |
|---|---|---|
| MCP工程手册 §2/§4 | 同上 | 听说读写四档自评 + 6 维度 server 评分卡（安全 0 分一票否决） |
| MCP工程手册 §5-7 | 同上 | SDK/Host 清单 + FastMCP 可跑代码（文件系统/SQLite 两例） |
| MCP工程手册 §8 | 同上 | 反模式 10 条（stdio 里 print 调试=协议崩 等） |
| 官方仓与 SDK（本案例） | [03-官方仓与SDK格局](03-官方仓与SDK格局.md) | SDK v2 重写、FastMCP 独立版、Registry、github-mcp-server toolsets 样板 |

### L3 生态层（江湖格局）

| 资产 | 位置 | 内容 |
|---|---|---|
| 生态统计与赛道（本案例） | [01-生态统计与赛道地图](01-生态统计与赛道地图.md) | topics/mcp 64k 仓统计 + top41 + 六赛道 + awesome 56 分类 |
| 用例库横向证据 | [`实例/用例库/README.md`](../../../../实例/用例库/README.md) | 279 仓快照：22% README 提及 MCP；「MCP 吞噬一切接口层」十大发现之一 |
| 深潜方法论 | [`透视GitHub-AI高星仓库全景.md`](../../../../透视GitHub-AI高星仓库全景.md) | 生态观测方法（本案例的方法论母本） |

### L4 案例层（源码级深读）

| 案例 | 位置 | MCP 相关看点 |
|---|---|---|
| codegraph | [`Agent上下文案例/codegraph代码知识图谱/`](../../../Agent上下文案例/codegraph代码知识图谱/README.md) | **MCP 常驻路线**：默认只暴露 1 个强工具 `codegraph_explore`；一次 MCP 调用省 28-43 次 grep |
| graphify | [`Agent上下文案例/graphify知识图谱skill/`](../../../Agent上下文案例/graphify知识图谱skill/README.md) | **skill 按需路线 vs MCP 常驻**的正面对照组（topics/mcp 第 7 名，108k★） |
| mem0 | [`Agent记忆系统案例/mem0开源记忆层/`](../../../Agent记忆系统案例/mem0开源记忆层/README.md) | mem0-plugin = MCP server + lifecycle hooks + OpenCode 插件三合一（记忆层接入样板） |
| deepseek-harness | [`Agent框架案例/deepseek-harness插件化框架/`](../../deepseek-harness插件化框架/README.md) | harness 视角：外部工具强制 `mcp__<server>__<tool>` 命名空间；MCP server = 一 server 一插件（`notes/02-capability-seams/02-插件机制全景.md`） |
| Serena / code-index-mcp | [`Agent上下文案例/README.md`](../../../Agent上下文案例/README.md) | LSP 实时语义路线（MCP 多工具面）与轻量索引路线对照 |
| ECC（opencode 改造） | [`Agent框架案例/opencode自成长改造/README.md`](../../opencode自成长改造/README.md) | AgentShield 六面扫描含 **MCP 面**（装前审计）——MCP 安全是 harness 责任 |

### L5 工具面层（本项目怎么用 MCP）

| 资产 | 位置 | 内容 |
|---|---|---|
| 本项目工具链 | `Karpathy经典代码精读/README.md` L18 | zread MCP 工具（读仓不依赖本机网络）——已在实战 |
| code agent 视角 | [`讲透代码生成/`](../../../../讲透代码生成/README.md) L62 | 「MCP 是 code agent 的 USB-C」；05 章讲 Agent 化代码工作流 |
| harness 手册 | [`工程化手册库/harness工程手册/README.md`](../../../../工程化手册库/harness工程手册/README.md) L69 | MCP工程手册 = harness T 组件的消费端（工具从哪来） |
| ContextEng 手册 | [`工程化手册库/ContextEngineering手册/README.md`](../../../../工程化手册库/ContextEngineering手册/README.md) L180 | MCP 工具调用 vs 上下文占用的定量权衡（codegraph -88% tool calls / +80% 驻留上下文） |

## 2. 学习路径（四档听说读写 × 项目资产）

```
听（看得懂 server）：MCP工程手册 §1-3 SRCPT ──► 用 codegraph 案例实拆一个 server
说（会指挥 host）：手册 §5-6 host 配置 ──► 本项目 zread 工具体感
读（读得懂 spec）：本案例 01 协议演进 ──► spec repo changelog 原文
写（写得出 server）：手册 §7 FastMCP ──► 03 篇 github-mcp-server toolsets 抄设计 ──► inspector 过检
```

**批判提醒**：手册（2025 规范）与本案例 01（2026-07-28 规范）冲突处，**以 01 为准**（握手/Sampling/Roots/传输细节）；三能力模型（Tools/Resources/Prompts）与评分卡不受影响。手册更新属于"规划中"级别的内容债，补一行互链即可，不必重写。

## 3. 反向检查（本网挂了谁）

本案例 README ↔ Agent框架案例/README ↔ 手册 ↔ 用例库 ↔ 上下文/记忆案例。**本篇是索引中的索引——若新增 MCP 资产（如未来讲透MCP 系列立项），必须回填本表。**

---

*盘点方法：`grep -ril "mcp" --include=README.md` 全库扫描 + 人工过滤（排除 node_modules 等基础设施目录——复杂系统审计三盲区之边界盲区）。*
