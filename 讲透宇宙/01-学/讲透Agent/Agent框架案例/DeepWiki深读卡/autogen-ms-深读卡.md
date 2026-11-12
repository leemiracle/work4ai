# AutoGen 深读卡 —— 微软多 Agent 框架（Actor 消息模型的工业级实现）

> **定位**：微软开源的多 Agent 对话/协作框架，`autogen-core` 用 Actor 风格消息传递（AgentRuntime + 订阅/发布 Topic）做运行时底座，上层 `agentchat` 提供开箱即用的 Team 编排。**⚠️ 2026 已进入维护模式（README.md:14-26）：不再新增特性，社区托管；新项目官方指路 [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)，有官方迁移指南**。
> **本地**：`repos/autogen-ms`（microsoft/autogen）｜**深读**：deepwiki 37 子页全文归档 `deepwiki/autogen-ms/full.md`（2026-08-21 抓取，v0.7.5）

## 一、组件栈（DeepWiki Overview 蒸馏）

| 层 | 包 | 职责 | 关键实体 |
|---|---|---|---|
| Foundation | `autogen-core` | 运行时/Agent 抽象/消息传递 | `AgentRuntime`(协议) · `BaseAgent` · `ChatCompletionClient` · `BaseTool` |
| High-Level API | `autogen-agentchat` | 预置 Agent + Team 模式 | `AssistantAgent` · `CodeExecutorAgent` · `RoundRobinGroupChat`/`SelectorGroupChat`/`Swarm`/`GraphFlow` · `TerminationCondition` |
| Extensions | `autogen-ext` | 可选集成（按 extras 安装） | OpenAI/Anthropic/Ollama 客户端 · Docker/Jupyter/ACA 代码执行器 · ChromaDB/Redis/Mem0 记忆 · `McpWorkbench` |
| 工具链 | studio/agbench/m1 | 可视化/评测/参考实现 | AutoGen Studio（Web）· agbench（GAIA/HumanEval）· Magentic-One CLI |
| 跨语言 | `dotnet/` | .NET 8 SDK，gRPC 与 Python 互操作 | `Microsoft.AutoGen.*` NuGet 系列 |

**记忆实现矩阵**（Memory Systems 页）：`ListMemory`(进程内) / `RedisMemory`(语义+时序) / `ChromaDBMemory`(向量) / `Mem0Memory` / `TextCanvasMemory`(实验)。

## 二、核心架构机制（本框架的知识增量）

1. **Actor 消息模型**（Agent Runtime System 页，31KB/11 图）：消息走 Runtime 的 Topic 订阅/发布，`SingleThreadedAgentRuntime` 为进程内默认实现，`GrpcWorkerAgentRuntime` 支持跨进程分布式（agent_worker.proto）；消息信封带 trace 传播（OpenTelemetry）。
2. **Hub-and-Spoke Team 结构**（Team Orchestration 页）：GroupChatManager 为枢纽，四种编排模式——RoundRobin（轮转）/ Selector（LLM 选发言人）/ **Swarm（Handoff 移交）**/ **MagenticOne（Orchestrator 双循环+停滞检测重试）**；GraphFlow 用 DiGraph 状态机+激活组管理并发分支与环。
3. **分层工具编排**（Message Types and Tool Agents 页）：`AgentTool`/`TeamTool` 把 Agent/Team 本身封装成工具（Agent-as-Tool），`TaskRunnerTool` 统一执行逻辑——层级式多 Agent 的工程化实现。
4. **双向 MCP**（MCP Integration 页，29KB）：不止消费工具——`ChatCompletionClientSampler`（服务端反向采样）、`StdioElicitor`（向用户征集输入）、`StaticRootsProvider`（文件系统根），AutoGen 可作为 MCP Host 运行。
5. **组件配置系统**：一切组件（Agent/Team/Memory/ModelClient）皆可 `ComponentBase` 序列化为 JSON 声明式配置——AutoGen Studio 低代码的根基；带 Provider 安全信任机制。

## 三、与讲透系列的对位

| AutoGen 概念 | 讲透系列对应 |
|---|---|
| `AgentRuntime` Topic 订阅/发布 | 讲透多Agent协作/02 §Actor 消息模型 |
| `Swarm` Handoff | 讲透Agent/01 §Handoff 模式 |
| `GraphFlow` DiGraph+激活组 | 讲透多Agent协作/03 §图编排（对照 LangGraph） |
| `MagenticOne` Orchestrator 停滞检测 | 讲透Agent/03 §规划循环的工业版 |
| `TerminationCondition` 组合（and/or/max） | 讲透Agent/00 §循环终止条件 |
| AgentTool（Agent-as-Tool） | 讲透多Agent协作/01 §层级编排 |

## 四、关键入口

```
python/packages/autogen-core/src/autogen_core/
  _single_threaded_agent_runtime.py   # 默认运行时（消息循环/订阅）
  _base_agent.py / _routed_agent.py   # Agent 协议 + 消息路由装饰器
  model_context/                      # 5 种上下文（buffered/token_limited/…）
  memory/                             # Memory 协议 + ListMemory
python/packages/autogen-agentchat/src/autogen_agentchat/
  agents/_assistant_agent.py          # AssistantAgent（工具/handoff/结构化输出）
  teams/_group_chat/_base_group_chat.py        # Team 骨架
  teams/_group_chat/_magentic_one/             # Magentic-One 编排器
  teams/_group_chat/_graph/                    # GraphFlow DiGraph
python/packages/autogen-ext/src/autogen_ext/tools/mcp/  # McpWorkbench/双向能力
```

## 五、深读子页地图（37 页精选 8）

基础：1 Overview（含维护模式警告）｜运行时：5 Agent Runtime System（11 图，消息流必读）｜编排：14 Multi-Agent Teams / 15 Team Orchestration / 17 GraphFlow / 18 MagenticOne System｜集成：24 MCP Integration（双向 MCP 唯一详解）｜工具链：27-29 AutoGen Studio 三部曲。

## 六、与"我们"的关系（一句话）

讲透Agent 里教的 Handoff/图编排/循环终止，在 AutoGen 中分别是 `Swarm`/`GraphFlow`/`TerminationCondition` 组合子——**Actor 消息模型的最佳参考实现**；但选型新项目时应直接看 Microsoft Agent Framework（AutoGen 的官方继任者，维护模式确认于 deepwiki 2026-08 快照）。

---
生成：2026-08-21 · deepwiki 全文归档（37 页 572KB）+ skeleton 核验 · 状态：**维护模式**
