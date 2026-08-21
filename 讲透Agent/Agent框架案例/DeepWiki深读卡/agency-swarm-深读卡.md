# agency-swarm 深读卡 —— 把"公司组织架构"编码成 `communication_flows` 的多 Agent 编排层（agent 互调即工具）

> **定位**：agency-swarm 是构建 multi-agent 应用的编排框架，现版本是 OpenAI Agents SDK 之上的 orchestration layer（早期以 OpenAI Assistants API 闻名，已迁移）。核心抽象是 **Agency**：用 `communication_flows` 显式声明 agent 间允许的通信路径（"Agency Chart"），框架据此把 `SendMessage`/`Handoff` 作为工具注入 sender，实现 agent 间工具化互调，并内置线程持久化、FastAPI 部署与 MCP 互操作。
> **本地**：`repos/agency-swarm`（VRSEN/agency-swarm）｜**深读**：deepwiki 39 子页归档 `deepwiki/agency-swarm/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 编排层 | 组织结构、通信流、入口与运行生命周期 | `Agency`、`communication_flows`、`entry_points`、`get_response(_stream)`、`run_fastapi`、`visualize` |
| Agent 层 | 角色指令、工具发现、文件与提醒管理 | `Agent`、`tools_folder`、system reminders、conversation starters、`subagents` |
| 通信层 | agent 间互调即 tool call | `SendMessage`（默认阻塞）、`Handoff`（控制转移）、custom `SendMessage` 子类、`MasterContext` |
| 工具层 | 声明式工具 → SDK 原语 | `BaseTool`（Pydantic）、`@function_tool`、`ToolFactory`、内置 `IPythonInterpreter`/`PersistentShellTool`/`PresentFiles` |
| 互操作层 | 外部工具协议双向接入 | `mcp_converter`、`PersistentMCPServerManager`、MCP OAuth、OpenAPI/LangChain importer |
| 状态层 | 会话持久化与消息格式化 | `ThreadManager`、`PersistenceHooks`、`MessageStore`、`MessageFormatter` |
| 服务层 | 生产部署与实时语音 | `run_fastapi`、endpoint handlers、`RealtimeAgency`、ag-ui protocol bridge |
| 可观测层 | 成本/追踪/引用抽取 | usage tracking（model_prices JSON）、Langfuse/AgentOps tracing、citation extraction |

## 二、核心机制

1. **编排初始化管线**：`Agency.__init__` → `parse_agent_flows()`（把 `a > b > c` 链解析为 sender-receiver 对）→ `register_all_agents_and_set_entry_points()` → `apply_shared_resources()`（分发 `shared_instructions`/`shared_tools`/`shared_mcp_servers`）→ `configure_agents()` → `initialize_agent_runtime_state()`（按流把 `SendMessage`/`Handoff` 织入各 agent）。（来源：Agency Class）
2. **通信即工具，两种语义**：`SendMessage` 默认同步阻塞——"pending-recipient guard"保证同一 recipient 未完成时不可重发，但**不同 recipient 可并发**；`Handoff` 则终止调用方当前 turn、把控制权整体移交（配 `handoff_reminder` 防幻觉）；可子类化 `SendMessage` 强制附加结构化字段（如 CoT）。`Orchestrator-Worker` 为默认模式。（来源：Communication Flows）
3. **显式共享状态与隔离**：`MasterContext` 让工具跨调用共享数据而不经消息字符串（`self.context.get/set`）；同一 Agent 可被多个 Agency 复用，thread 与 context 按 Agency 实例隔离；持久化走 `load/save_threads_callback` → `PersistenceHooks` → `ThreadManager`，run 结束存不可变快照，`CompositeRunHooks` 合并用户 hooks。（来源：Communication Flows / Agency Class）
4. **工具适配与互操作**：Pydantic `BaseTool` 经 `ToolFactory` 适配为 SDK `FunctionTool`（保留 `MasterContext` 注入，`normalize_function_tool` 兜底各执行路径）；工具可从 OpenAPI schema、LangChain、MCP server 导入，也可反向把自家工具经 MCP 对外供给，含 OAuth 延迟认证。（来源：Overview / ToolFactory / MCP Integration）

## 三、与讲透系列的对位

| agency-swarm 概念 | 讲透X / agent-development 落点 |
|---|---|
| `Agency` + `communication_flows`（组织架构即代码） | 多智能体协作章：图编排（LangGraph）vs "agent 即工具"（Agency-as-Tools）框架选型对照 |
| `SendMessage`/`Handoff`（互调=tool call） | 工具调用/MCP 章："把 agent 暴露为工具"范式的生产级参考实现 |
| `MasterContext`（显式共享状态） | 记忆机制章：与 LangGraph state / 共享黑板模型对读 |
| `ThreadManager` + `PersistenceHooks` | 记忆/会话管理章：可跑的持久化快照实验素材 |
| `BaseTool` → `FunctionTool` 适配 | "从零实现 tool calling"实验：Pydantic schema → JSON Schema 的真实工程链路 |
| MCP 双向集成 + OAuth | agent-development 的 MCP 协议章：stdio/SSE/hosted 三种 transport 的一手代码 |

## 四、关键入口

```python
# repos/agency-swarm 最小骨架（DeepWiki: Getting Started / Communication Flows）
from agency_swarm import Agency, Agent, Handoff

ceo  = Agent(name="CEO", instructions="统筹拆解任务", tools_folder="./ceo/tools")
dev  = Agent(name="Developer", instructions="写代码")

agency = Agency(
    ceo,                                  # 位置参数 = entry point（直面用户）
    communication_flows=[
        (ceo, dev),                       # SendMessage：阻塞式委派，结果回传 CEO
        ceo > researcher,                 # '>' 运算符等价写法
        (triage > specialist, Handoff),   # Handoff：控制权整体移交用户对话
    ],
    shared_instructions="全公司守则",
    user_context={"repo": "..."},         # 注入 MasterContext，工具内 self.context.get()
)
agency.get_response("Build a site")       # → agency/responses.py → Agent execution 管线

# 源码锚点：
# src/agency_swarm/agency/{core,setup,responses}.py   编排层
# src/agency_swarm/agent/{core,execution*}.py          Agent 与执行/流式管线
# src/agency_swarm/tools/{send_message,base_tool,tool_factory}.py  通信与工具
# src/agency_swarm/utils/thread.py                     ThreadManager/PersistenceHooks
```

## 五、深读子页地图（39 页精选 6）

| 子页 | full.md 行 | 为什么要读 |
|---|---|---|
| Agency Class | L685 | 构造参数全表 + 初始化管线 mermaid + `get_response` 内幕（recipient reminder） |
| Communication Flows | L2256 | 本框架灵魂：SendMessage 阻塞语义、Handoff、MasterContext 隔离 |
| Agent Class | L896 | 初始化管线、`tools_folder` 工具发现、模型能力检测 |
| ToolFactory | L1512 | BaseTool→FunctionTool 适配数据流 + OpenAPI/MCP/LangChain 导入 |
| MCP Integration | L1875 | 双向 MCP（消费 server + 对外供工具）与 OAuth 持久化 |
| FastAPI Integration | L3970 | `run_fastapi` 端点生成、请求生命周期、ClientConfig 覆盖 |

## 六、与"我们"的关系（一句话）

它是"多 Agent 协作 = 把彼此当工具调用 + 显式通信拓扑"这一范式的生产级开源实现，正好充当讲透X/agent-development 多智能体章的一手对照代码骨架（与 LangGraph 图编排互为镜像）。

---
生成：2026-08-21 · deepwiki 39 页全归档
