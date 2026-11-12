# aden-hive 深读卡 —— 把 Agent 写成"目标+节点图"、由 Judge 验收、靠 coding agent 读日志改图的自我改进框架

> **定位**：Hive（aden-hive/hive）是 Python 生产级 AI Agent 框架，主打**声明式 node graph**：开发者只声明 Goal（成功判据+约束）与 NodeSpec/EdgeSpec，执行、重试、评审、记忆压缩、观测全部内建。两大核心想法：① goal-driven execution（按成功标准路由，而非固定调用链）；② self-improving loop（失败数据进结构化日志，Claude Code/Codex CLI 等 coding agent 读日志→改图→重部署）。双包交付：`framework`（core/，运行时+图执行器+TUI）与 `aden_tools`（tools/，100+ MCP 工具服务器）。

> **本地**：`repos/aden-hive`（aden-hive/hive）｜**深读**：deepwiki 31 子页归档 `deepwiki/aden-hive/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 触发层 | webhook/timer/event/手动多入口注册与调度 | `AgentRuntime`、`EntryPointSpec`、`WebhookServer`、cron/interval timer |
| 运行时层 | 每入口一条流的并发执行管理、暂停/恢复 | `ExecutionStream`、`ExecutionContext`、`StreamRuntime(Adapter)`、`SessionStore` |
| 图执行层 | 有向图遍历、EdgeCondition 路由、分支并行 | `GraphExecutor`、`GraphSpec`、`EdgeSpec`/`EdgeCondition`、`node_registry` |
| 节点执行层 | 唯一生产节点类型：LLM 流式循环+工具分发+验收 | `EventLoopNode`、`LoopConfig`、`OutputAccumulator`、`JudgeProtocol`/`JudgeVerdict` |
| LLM 层 | 100+ 后端统一抽象（LiteLLM 路由） | `LLMProvider`、`LiteLLMProvider`、`AnthropicProvider` |
| 记忆层 | 单图运行的 KV 共享状态 + 节点会话与分层压缩 | `SharedMemory`/`SharedStateManager`、`NodeConversation`、`FileConversationStore` |
| 工具层（MCP） | 工具不经 import 而经 MCP 伺服；agent-builder 反向生成图 | `ToolRegistry`、`MCPClient`、`aden_tools/mcp_server.py`、`agent_builder_server` |
| 基础设施 | 文件持久化（无数据库）、事件总线、凭证 | `FileStorage`/`ConcurrentStorage`、`EventBus`、`RuntimeLogStore`、`CredentialStore`（加密分层） |
| 交互层 | TUI/CLI/加载 API | `AdenTUI`（Textual）、`ChatRepl`、`AgentRunner.load()` |

## 二、核心机制

1. **Goal→Judge 验收闭环**：执行流 `AgentRuntime.trigger → ExecutionStream → GraphExecutor → EventLoopNode`；每轮 LLM 流式输出后交给 `JudgeProtocol.evaluate()`，裁决 `ACCEPT/RETRY/ESCALATE`，RETRY 反馈注入会话续跑；GraphExecutor 对 `event_loop` 节点**从不重试、不做输出校验**——Judge 是唯一验收机制（来源：Overview、3.3）。
2. **合成工具 + 隐式 Judge**：`EventLoopNode` 自动注入 `set_output`（写 OutputAccumulator，key 写错立即报错回喂）、`ask_user`/`escalate`（仅 client_facing 且非 event_triggered）；无显式 Judge 时隐式判定"所有 `output_keys` 已填 ⇒ ACCEPT"，使节点天然自终止（来源：3.3）。
3. **三级隔离 + 多入口会话共享**：`isolation_level = isolated/shared/synchronized` 控制并发执行的 SharedMemory 作用域（synchronized 带每 key `asyncio.Lock`）；timer/webhook 流通过 `resume_session_id` 继承主 chat 会话，共写同一 `state.json`，`_GraphScopedEventBus` 给事件盖 `graph_id` 以便过滤（来源：3.1）。
4. **崩溃可恢复 + 自我改进原料**：`OutputAccumulator` 对 `set_output` 直写（write-through）ConversationStore cursor，中途崩溃可 `restore()` 部分输出续跑；每节点边界 patch `state.json`（`_write_progress`）支持 HITL 暂停/恢复与 CheckpointStore；`RuntimeLogger` 落 L2 结构化日志——正是 agent_builder MCP server + `/hive` Claude skills 读日志改图的输入（来源：3.1、3.3、Overview）。附带工程细节：tool doom loop 检测（连续同指纹工具调用→阻断或警告）、stall 检测、分层会话压缩（`max_history_tokens=32k` 触发 phase-aware/standard compaction）、瞬态 API 错误指数退避重试全部内化在节点内。

## 三、与讲透系列的对位

| Hive 概念 | 讲透系列 | 对位说明 |
|---|---|---|
| Goal/NodeSpec/EdgeSpec 声明式图 + Judge 验收 | 讲透Agent | LangGraph"边编程"之外的**验收驱动**范式实物教材：路由让位于成功判据 |
| self-improving loop（日志→coding agent 改图→重部署） | 讲透学习型Agent | 框架级"从失败中学习"的最小可行实现：学习信号=结构化日志而非梯度 |
| NodeConversation 分层压缩 + OutputAccumulator 溢写 | 讲透上下文缓存 | 32k token 预算、phase-aware 压缩、工具结果 spillover 落盘的工程范本 |
| ExecutionStream 多入口并发 + 三级隔离 | 讲透多Agent协作 | 反向对照样本：同一 agent 的并发会话治理（非多角色对话），隔离语义可直接借用 |
| agent_builder MCP server + /hive Claude skills | 讲透代码生成 | "LLM 写代码改自己"的生产级用例：MCP 反向暴露图构建 API 给 IDE agent |

## 四、关键入口

```text
repos/aden-hive/
├── quickstart.sh                      # uv sync + ~/.hive/configuration.json + 凭证初始化
├── core/framework/
│   ├── runner/runner.py               # AgentRunner.load(agent.py|agent.json)、LLM 解析
│   ├── runtime/agent_runtime.py       # AgentRuntime.trigger() 入口编排
│   ├── runtime/execution_stream.py    # ExecutionStream / EntryPointSpec / 隔离与并发
│   ├── graph/executor.py              # GraphExecutor 图遍历（executor.py:843 显式跳过 event_loop 重试）
│   └── graph/event_loop_node.py       # EventLoopNode / LoopConfig / JudgeVerdict（唯一生产节点）
├── tools/src/aden_tools/mcp_server.py # FastMCP 工具服务器（email/gmail/web_search/arxiv…）
├── examples/templates/                # 模板 agent（email_inbox_management 等 9 recipes）
└── .claude/skills/                    # /hive 系列技能（改图自改进入口）
```

## 五、深读子页地图（31 页精选 6）

| 子页 | full.md 行号 | 价值 |
|---|---|---|
| 3.3 Event Loop Node | L3276 | 心脏：主循环流图、LoopConfig 全参数、doom loop/stall 检测 |
| 3.1 Agent Runtime and Execution Streams | L2215 | 入口/并发/隔离/暂停恢复/多入口会话共享全景 |
| 3.2 Graph Executor and Node Execution | L2747 | 图遍历与 EdgeCondition 路由（本卡未读，补图执行细节） |
| 4.2 Agent Builder MCP Server | L6597 | 自改进闭环的"改图端"：MCP 反向构建 agent |
| 8.1 Building Agents with Claude Skills | L10431 | /hive 技能实操：coding agent 建图工作流 |
| 3.6 Conversation and Memory Management | L4606 | 分层压缩与记忆续接的完整算法 |

## 六、与"我们"的关系（一句话）

讲透Agent/学习型Agent 的最佳对照实物：Hive 把"验收驱动执行 + coding agent 自改进"这条 2026 主线做成了可跑的最小闭环，正好补足讲透Agent 里 LangGraph 范式的对侧视角。

---
生成：2026-08-21 · deepwiki 31 页全归档
