# microagents 深读卡 —— 按需生成、评估、持久化的"微 Agent"自建库实验框架

> **定位**：aymenfurter 的实验性框架：**动态创建 self-improving 微 Agent**——小而专的 microagent 按需生成（响应查询）、评估（功能与效果）、持久化（跨会话复用）、组合（解复杂问题），逐步攒出一座专长 Agent 库。与 ADAS（搜索架构空间）/agentk（造 Agent 的内核 Agent）同属"Agent 造 Agent"思潮，但主打"微+持久库"路线。
> **本地**：`repos/microagents`（aymenfurter/microagents）｜**深读**：deepwiki 19 子页归档 `deepwiki/microagents/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 编排层 | 查询→决定生成/复用哪个 microagent | main.py |
| Agent 层 | 微 Agent 生命周期 | MicroAgent core、Agent Lifecycle（生成→评估→持久化） |
| 层级通信 | Agent 间层级与消息 | Agent Hierarchy and Communication |
| 存储 | 持久化 Agent 库 | persisted agents（跨会话复用） |

## 二、核心机制

1. **按需生成四步曲**（Overview）：Generated on-demand（响应查询生成）→ Evaluated（功能/效果评估）→ Persisted（存库复用）→ Combined（组合解复杂任务）——"agent 即可积累资产"的完整闭环（对照 Voyager 技能库：那里存代码，这里存 Agent）。
2. **Agent 层级与通信**（专页）：微 Agent 可层级组织、相互通信——组合性是设计目标而非事后补丁。
3. **生命周期管理**（专页）：从生成到退役的状态机，含评估门槛（不过关不进库）。

## 三、与讲透系列的对位

| microagents 概念 | 讲透系列对应概念 |
|---|---|
| 按需生成+评估+持久化 | 讲透学习型Agent/05 §Agent 库自积累 |
| 微 Agent 组合 | 讲透多Agent协作/01 §组合性 |
| 评估门槛 | 质量门（对照 agentk smoke test） |

## 四、关键入口

```
main.py               # 入口：查询→生成/复用决策
microagents/          # 微 Agent 核心（lifecycle/communication）
```

## 五、深读子页地图（19 页精选 4）

Microagents Overview｜System Architecture｜**Agent Hierarchy and Communication**｜Agent Lifecycle。

## 六、与"我们"的关系（一句话）

"Agent 资产化"思潮的第三个样本（Voyager 存技能 / ADAS 存架构 / microagents 存 Agent 本身）——三对照讲"自进化到底进化什么"极佳。

---
生成：2026-08-21 · deepwiki 19 页全归档
