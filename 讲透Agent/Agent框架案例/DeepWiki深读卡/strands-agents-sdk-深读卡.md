# strands-agents-sdk 深读卡 —— AWS 开源的模型驱动 Agent SDK：一个循环+工具+Hook 撑起生产级 Agent

> **定位**：AWS 2025 年开源的 Agent SDK（Python + TypeScript 双实现 monorepo），核心理念是 "model-driven"——不写编排代码，让模型在一个递归事件循环里自主调工具完成任务。差异化在于"框架自身功能（重试/上下文管理/会话持久化）全部用同一套 Hook 扩展机制实现"，且深度绑定 AWS（Bedrock 默认、Guardrails、Cedar 授权、Knowledge Base 记忆、S3 上下文卸载）。
> **本地**：`repos/strands-agents-sdk`（strands-agents/sdk-python）｜**深读**：deepwiki 58 子页归档 `deepwiki/strands-agents-sdk/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Agent 核心 | 编排入口、会话与状态持有 | `Agent`、`AgentState`、`Snapshot`、`SessionManager` |
| 执行循环 | 模型调用→stop_reason 分派→工具执行→递归 | `event_loop_cycle()`、`StreamEvent`、`StopReason` |
| 模型抽象 | 统一 LLM 接口 + 流式事件归一化 + prompt caching | `Model` (ABC)、`BedrockModel`、`OpenAIModel`、`LiteLLMModel`(100+ provider)、`ModelRouter` |
| 工具生态 | 函数转工具、注册发现、并发/顺序执行 | `@tool`、`ToolRegistry`、`ToolExecutor`、`ToolWatcher`(热重载)、`MCPClient` |
| 扩展层 | 事件驱动定制、插件打包 hooks+tools | `HookRegistry`、`Plugin`、Middleware Stages |
| 上下文/记忆 | 滑窗/摘要压缩、记忆提取注入、卸载检索 | `SlidingWindow/SummarizingConversationManager`、`MemoryManager`、`ContextOffloader` |
| 多 Agent | 图/群游走/A2A 三种编排 | `GraphBuilder`、`Swarm`、`A2AServer`/`A2AAgent` |
| 可观测 | OTel tracing/metrics + GenAI 语义约定 | `Tracer`、`EventLoopMetrics` |

## 二、核心机制

1. **模型驱动递归事件循环**（来源：Event Loop and Execution Flow / Core Concepts）：`event_loop_cycle()` 单轮 = 初始化 cycle_id → OTel span → 模型流式调用（含 throttling 重试，`MAX_ATTEMPTS=6` 指数退避）→ 按 `stop_reason` 分派：`tool_use`→执行工具→`recurse_event_loop()` 递归；`end_turn`→结束；`max_tokens`→抛异常或恢复。**创新点**：整个"循环"只是一个函数，SDK 刻意保持极简（"a model, some tools, and a loop"），编排智能全部交给模型而非框架代码——与 LangGraph 式显式图编排是两个哲学极端。
2. **一切皆 Hook**（来源：Hook System / Extensibility System）：`HookRegistry` 派发强类型生命周期事件（`BeforeModelCallEvent`/`BeforeToolCallEvent`/`MessageAddedEvent`…），而 `ConversationManager`、`SessionManager`、`ModelRetryStrategy` 这些框架内置功能本身就是 HookProvider。**创新点**：扩展机制没有"二等公民"——用户 Hook 与框架核心能力走同一条路，`Plugin` 基类再自动发现并打包 hooks+tools（AgentSkills/Steering/GoalLoop 皆由此实现）。
3. **打断与人类在环（Interrupt/HITL）**（来源：Interrupt Handling and Human-in-the-Loop）：工具执行中抛 `InterruptException` → `_InterruptState` 持久化 → 返回用户 → 响应后恢复执行；配 Cedar 策略引擎做工具级 RBAC、限流、环境门禁。**创新点**：把"授权/审批"做成可插拔 intervention（HITL 风险分类器 + Cedar 策略热重载），是同类框架里最完整的权限模型，明显带 AWS 企业基因。
4. **上下文工程全家桶**（来源：Conversation Management / Memory System / Context Offloader）：反应式（`"auto"` 滑窗+摘要）与主动式（`"agentic"` 压缩）两种模式；`ContextOffloader` 把大工具结果卸载到内存/文件/S3 并注入检索工具；`MemoryManager` 用模型自动提取记忆 + `ContextInjector` 注入。**创新点**：上下文管理不是单一组件而是可组合策略栈，且每层都可换存储后端。

## 三、与讲透系列的对位

| Strands 概念 | 讲透系列对应概念 |
|---|---|
| `event_loop_cycle()` 递归循环 + stop_reason 分派 | 讲透Agent：ReAct 循环（模型→工具→观察→再推理） |
| `@tool` 类型提示生成 JSON Schema / `MCPClient` | 讲透Agent：工具调用与 MCP 协议 |
| `ConversationManager`/`MemoryManager`/`ContextOffloader` | 讲透Agent：记忆机制（工作记忆 vs 长期记忆分层） |
| `GraphBuilder`/`Swarm` handoff/`A2A` | 讲透多Agent协作：编排模式（DAG 图编排/群游走交接/跨进程协议） |
| Sandbox(Docker/SSH) + Cedar 授权 + HITL 打断 | 讲透Agent：安全沙盒与人机协同审批 |
| `GoalLoop`(Judge 验证)+`Steering`(运行中纠偏) | 讲透学习型Agent：自进化（自我评估-重试闭环） |

## 四、关键入口

```
strands-py/src/strands/agent/agent.py          # Agent 主编排器：messages/ToolRegistry/HookRegistry 装配，invoke/stream/__call__ 三种调用
strands-py/src/strands/event_loop/event_loop.py # 核心：event_loop_cycle 六阶段 + _handle_model_execution 重试 + recurse_event_loop 递归
strands-py/src/strands/models/model.py          # Model ABC：stream/结构化输出/token 计数接口，provider 切换零代码
strands-py/src/strands/tools/decorator.py       # @tool 装饰器：docstring+type hints→ToolSpec，ToolContext 注入
strands-py/src/strands/tools/registry.py        # ToolRegistry：注册/热重载/目录发现/名称冲突防护
strands-py/src/strands/hooks/registry.py        # HookRegistry：事件派发与回调类型推断
strands-py/src/strands/multiagent/graph.py      # GraphBuilder：节点/条件边/环/并行批执行
strands-py/src/strands/multiagent/swarm.py      # Swarm：handoff 工具注入 + SharedContext + 防重复交接
```

## 五、深读子页地图（58 页精选 6）

1. **P3 Core Concepts and Architecture** — 四大抽象（Agent/Model/Tool/Hook）+ 分层架构总纲，全库地图
2. **P7 Event Loop and Execution Flow** — 核心引擎逐阶段拆解：cycle 状态、重试、递归、InvokeModelStage 中间件
3. **P9 Conversation Management** — 滑窗/摘要/auto vs agentic 双模式，上下文溢出恢复的完整数据流
4. **P29 Interrupt Handling and Human-in-the-Loop** — 打断状态机（ID/版本/序列化/恢复）+ Cedar 授权全解
5. **P37 Graph-based Orchestration** — 29KB 大页：条件路由、循环图重置、中断状态恢复、并行批执行
6. **P38 Swarm Collaboration** — handoff 工具签名与执行流、共享上下文传播、执行限额与防循环检测

## 六、与"我们"的关系（一句话）

这是"把 ReAct 循环做成一个函数、把一切扩展压进 Hook"的极简派参考实现，加上企业级上下文工程与授权干预的完整工程答案——学 Agent 框架设计（对照 LangGraph 重编排哲学）和 AWS 生产化实践，这一库双收。

---
生成：2026-08-21 · deepwiki 58 页全归档
