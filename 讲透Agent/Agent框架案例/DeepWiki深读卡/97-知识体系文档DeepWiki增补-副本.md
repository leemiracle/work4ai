# 知识体系文档 DeepWiki 增补（第六部分）

> 副本来源：~/ai/agent/awesome-agents/AGENT-KNOWLEDGE-SYSTEM.md（2026-08-21 增补章节）

# 第六部分：DeepWiki 深读卡资源层（2026-08-21 增补）

> **新基建**：awesome-agents 135 仓库的 DeepWiki 全量归档（98 个有 wiki，全文 `deepwiki/{name}/full.md`）+ work4ai 侧的「DeepWiki 深读卡」体系。本知识体系第三/四部分的每个架构论点，现在都有对应的 wiki 全文与深读卡可查证。

## 6.1 三层资源地图

| 层 | 位置 | 用途 |
|---|---|---|
| 全文归档 | `awesome-agents/deepwiki/{name}/{full.md, structure.txt, skeleton.md}` | 98 仓库 wiki 全文（每页带源码行号引用），skeleton 是导航骨架（页清单+标题树+mermaid 统计） |
| 深读卡 | `work4ai/讲透Agent/Agent框架案例/DeepWiki深读卡/{name}-深读卡.md` | 每仓库一张：定位→组件栈→核心机制→讲透对位→关键入口→子页地图 |
| 批判总览 | 同目录 `00-创新点与缺点总览.md` | 全框架创新点★×缺点✗ 横向对照 + 协调光谱/上下文工程/自进化三层次洞察 |

## 6.2 「成为专家」部分（第四部分）的实证升级对照

| 第四部分论点 | 深读卡实证 |
|---|---|
| ReAct 循环 | swarm 卡（100 行裸 executor）→ smolagents CodeAgent 卡（生产化） |
| Actor 消息模型 | autogen-ms 卡（Topic 订阅/gRPC 分布式） |
| 状态图编排 | haystack 卡（类型化 socket+Snapshot 恢复） |
| SOP 多角色 | metagpt 卡（watch 订阅拓扑+RoleZero 自革命） |
| 虚拟内存管理 | openhands 卡（Condenser 三策略）/opencode 卡（三级防御+DOOM_LOOP） |
| 自进化（第五创新） | agentk（造 Agent）/ACE（Skillbook）/aden-hive（改图）三卡递进 |

## 6.3 教学法建议（结合讲透系列）

1. **先卡后码**：新框架先读深读卡 5 分钟建立心智模型 → skeleton.md 选 2-3 页精读 → 才进本地源码。
2. **对位学习**：每张卡的「与讲透系列的对位」表是双向的——学讲透Agent 章节时反向抽卡看工业实现。
3. **批判性练习**：用「00-总览」的缺点列做"如果是你来修"的设计题（例：codel 的 docker.sock 漏洞怎么堵？bernstein 的零智能协调何时失灵？）。
