---
card_id: COL-00
title: "讲透多 Agent 协作：从编排到可靠"
universe: 讲透多Agent协作
burke:
  scene: "单 Agent 上下文爆炸、能力有界、单点失误"
  agent: "想造多 Agent 系统的架构师"
  agency: "orchestrator-worker / debate / hierarchy / market"
  act: "把一个大任务分解给多个 Agent 并行/对抗/制衡地完成"
  purpose: "获得超越单 Agent 的能力上限与可靠性"
tension: "协调开销可能 > 收益；多 Agent 会死锁、串谋、责任扩散"
arc: [直觉, 数学(博弈+共识), 代码(编排框架), 不足(失败模式), 应用(选型)]
status: in_progress
next_card: COL-01
refs:
  - "LangGraph 0.2+, 2024-2025"
  - "AutoGen v0.4, 2024"
  - "MetaGPT, 2023"
  - "OpenAI Swarm, 2024"
  - "Anthropic multi-agent research system, 2025"
updated: 2026-08-13
---
# 🤝 讲透多 Agent 协作：从编排到可靠

> **User Story**：作为一个想造多 Agent 系统的人，我想理解协作的原语与失败模式，以便编排可靠而不踩「协调开销>收益」的坑。

## 🎭 戏剧张力

多 Agent 听起来强大（分工、并行、对抗、制衡），但它的诅咒是 **Brooks 定律的 AI 版**：

> **N 个 Agent 之间的通信链路数 = O(N²)，而每个链路都是幻觉/误解/死锁的潜在入口。** 很多时候，3 个笨 Agent 的协作，不如 1 个聪明的 Agent + 好的 prompt。

整部「讲透协作」在回答：**什么时候值得多 Agent？怎么编排才不亏？**

## 📚 五幕总览

| 幕 | 文件 | 一句话 |
|---|---|---|
| 直觉 | `01-直觉-为什么需要多个Agent.md` | 单 Agent 三大极限 + 多 Agent 四种收益 |
| 数学 | `02-数学-协作的形式化.md` | 多智能体 MDP / 马尔可夫博弈 / Contract Net / 共识(Raft) / 通信信息论 |
| 代码 | `03-代码-最小多Agent编排.md` | 纯 Python 200 行 orchestrator-worker + message bus |
| 不足 | `04-不足-协作失败模式.md` | 死锁/活锁/责任扩散/幻觉级联/串谋/评估难 |
| 应用 | `05-应用-协作模式选型.md` | 5 种拓扑 + LangGraph/AutoGen/CrewAI/MetaGPT/Swarm 对比 |

## 🗺️ 五种协作拓扑（核心决策框架）

| 拓扑 | 适合 | 不适合 | 典型框架 |
|---|---|---|---|
| **Orchestrator-Worker** | 可分解的并行子任务（多文件实现） | 强耦合任务 | OpenAI Swarm, Cursor background agents |
| **Hierarchy** | 有明确上下级的组织（产品→工程→测试） | 平权协作 | MetaGPT, ChatDev |
| **Debate** | 需要多视角验证（红队/审查） | 时间敏感任务 | Multi-agent debate 论文 |
| **Peer-to-Peer** | 探索性/创意（brainstorm） | 需要确定性 | CrewAI |
| **Market/Auction** | 资源分配/调度 | 共识类 | Contract Net Protocol |

## 📊 2024-2026 关键实践

- **Anthropic 多 agent 研究系统**（2025）：一个 lead agent 派多个 sub-agent 并行搜资料再综合——**Claude 在评审 Claude 写的代码**，这是「debate + orchestrator」的工业级实践。
- **OpenAI Swarm**（2024）：极简的 handoff 抽象，证明「轻量编排 > 重框架」。
- **LangGraph 0.2+**：把 agent 流程建模成显式状态图，可断点/重放/人审。
- **AutoGen v0.4**：重写后强调 actor 模型 + 异步消息。

## 🔗 与其他宇宙

- **[`讲透Agent/`](../讲透Agent/)**：多体协作的第一课：先有可靠的单体（见 Agent 宇宙）
- 与 **`讲透群体智能/`**：协作讲**显式编排**（有中心），swarm 讲**涌现自组织**（无中心）。两者是光谱两端。
- 与 **`讲透代码生成/`**：并行多 agent coding 的核心是 **file ownership**（避免冲突）。
- 与 **`故事原语/``03-五原语统一表`**：协作本身就是「多个 Agent 共同推进一张故事卡图」。

## 💡 核心洞察

> **多 Agent 不是银弹，它是一种用「协调成本」换「能力上限」的交易。** 判断值不值的公式很简单：**(并行收益 + 对抗可靠性增益) > (通信开销 + 幻觉级联风险)** 时才用。否则，把多 Agent 退化为单 Agent + 更好的 context，往往是更熵减的选择。

---
📌 **下一步**：`02`（数学）和 `04`（失败模式）是工程师最该读的两章。
