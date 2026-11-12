# semantic-kernel 深读卡 —— 微软 model-agnostic 的 LLM 编排 SDK，"Kernel 插件化函数 + Agent 抽象 + 多智能体编排"三层一体的企业级参照实现

> **定位**：Semantic Kernel 是微软的 multi-language（.NET/Python 双实现）AI orchestration SDK，以 `Kernel` 为 hub 统一管理 plugins、AI services 与 filter pipeline，把自然语言 prompt、原生代码与 OpenAPI 规范都统一成 `KernelFunction`。官方明确"已演进为 Microsoft Agent Framework"（与 AutoGen 汇流），提供 `Agent` 抽象、AgentChannel 广播、五种 orchestration 模式与 actor runtime。最值得学的是它"一个函数抽象打通三种来源 + 三类 filter 切面"的工程设计。
> **本地**：`repos/semantic-kernel`（microsoft/semantic-kernel）｜**深读**：deepwiki 30 子页归档 `deepwiki/semantic-kernel/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Kernel 编排层 | hub-and-spoke 中央协调：管 plugins/services/filters，同步+异步+流式执行 | `Kernel`、`KernelBuilder`、`InvokeAsync/InvokeStreamingAsync`、.NET DI `IServiceProvider` vs Python 多继承 extension（`KernelFunctionExtension` 等） |
| 函数与插件层 | 三种来源统一为一个函数抽象；plugin 是函数容器 | `KernelFunction`、`KernelFunctionFactory`、`@kernel_function`/`[KernelFunction]`、`KernelPlugin`、`KernelArguments`、`FunctionResult` |
| 模板引擎层 | prompt 渲染：块化 tokenization + 变量解析 + 模板内函数调用 `{{plugin.func $arg}}` | `CodeBlock/VarBlock/ValBlock`、`KernelPromptTemplate`、Handlebars/Liquid/Jinja2 工厂 |
| AI 服务连接层 | 多 provider 统一接口，按 `PromptExecutionSettings` 选服务 | `IChatCompletionService`、`IAIServiceSelector`/`OrderedAIServiceSelector`、OpenAI/Azure/Google/ONNX connectors |
| Agent 层 | 统一 Agent 抽象 + 各云厂商特化 + 会话线程 | `Agent`(abstract)→`ChatHistoryAgent`→`ChatCompletionAgent`、`OpenAIAssistantAgent`、`AzureAIAgent`、`BedrockAgent`、`AgentThread` 各实现 |
| 多智能体编排层 | 群聊/顺序/并发/交接/管理者五模式，actor 隔离执行 | `AgentGroupChat`、`Selection/TerminationStrategy`、`HandoffActor`、`Magentic-One(TaskLedger)`、`InProcessRuntime`、`AgentChannel`/`BroadcastQueue`、`OrchestrationResult` |
| 记忆与向量层 | RAG 标准接口，模型无关访问向量库 | `IVectorStore`、`IMemoryStore`、`TextMemoryPlugin`、Azure AI Search/Redis/Qdrant/Milvus 等 connector |
| 横切扩展层 | 函数调用全生命周期切面（日志/缓存/重试/校验） | `IFunctionInvocationFilter`、`IPromptRenderFilter`、`IAutoFunctionInvocationFilter`；`FunctionChoiceBehavior`(Auto/Required/None) |
| 协议与流程层 | 外部工具协议接入 + 声明式工作流 | MCP（as plugin + sampling）、OpenAPI plugin、`KernelProcess`(experimental)、YAML DeclarativeSpec |

## 二、核心机制

1. **Kernel hub + 三类 filter pipeline**：`Kernel` 持有 `KernelPluginCollection`、services 与三组 filter（function-invocation / prompt-render / auto-function-invocation）；.NET 用递归 `InvokeFilterOrFunctionAsync(index)` 把函数包进 filter 链，Python 用生成器实现同一洋葱模型——横切关注点与业务函数彻底解耦。（来源：Kernel Orchestration）
2. **函数三源归一**：C# 反射（`[KernelFunction]`+`[Description]`）或 Python 装饰器（`@kernel_function`）把原生方法、prompt 模板、OpenAPI operation 全部制成 `KernelFunction`，执行统一走"参数 enrichment→filter→核心逻辑→`FunctionResult`"管线；模板引擎可在 prompt 里再调其他 kernel 函数。（来源：Functions and Plugins）
3. **Auto Function Invocation 取代老 Planner**：由 `FunctionChoiceBehavior` 驱动循环——AI 返回 `FunctionCallContent`→校验函数存在→解析 `KernelArguments`→`kernel.invoke()`→结果包成 `FunctionResultContent` 回写 ChatHistory；历史 planner 退居 InternalUtilities，编排智能上移到 Agent 层。（来源：Kernel Orchestration；Functions and Plugins）
4. **多智能体：Channel 广播 + 双策略 + actor runtime**：`AgentGroupChat` 用 `SelectionStrategy`（Sequential/KernelFunction）选下一位发言者、`TerminationStrategy`（RegEx/KernelFunction/Aggregator）判停；异构 agent 靠各自 `AgentChannel` 同步历史 + `BroadcastQueue` 广播；Magentic-One 用 Orchestrator 维护 Task Ledger（facts+plan）做 plan/replan 循环；运行时是 actor 模型（`AgentActor`/`RoutedAgent`/`InProcessRuntime`，可换 Dapr）。（来源：Agent Framework；Multi-Agent Orchestration）

## 三、与讲透系列的对位

| 讲透系列主题 | semantic-kernel 对位概念 | 深读子页 |
|---|---|---|
| 讲透 Agent：工具调用/@decorator 注册工具 | `@kernel_function` 装饰器 + `KernelPlugin` 三源函数 | 3.2 Functions and Plugins |
| 讲透 Agent：MCP 协议 | MCP as plugin + agent sampling（`connectors/mcp.py`） | 6.6 MCP Integration |
| 讲透 Agent：多智能体协作（LangGraph/CrewAI 对照） | `AgentGroupChat`/五种 Orchestration/Magentic-One/actor runtime | 5.4 Multi-Agent Orchestration |
| 讲透 NLP / RAG 章节 | `IVectorStore` 抽象 + `TextMemoryPlugin` + RAG 决策文档 0034 | 3.3 Memory and Vector Stores |
| 讲透 Agent：Agent 记忆/状态 | `AgentThread` 各实现（ChatHistory/OpenAI/Azure/Bedrock） | 5.1 Agent Architecture |
| （可新增）讲透 Function Calling 循环 | `FunctionChoiceBehavior` 三态 + auto-invocation loop | 6.2 Prompt Execution Settings and Tool Calling |

## 四、关键入口

```text
python/semantic_kernel/kernel.py                          # Python Kernel hub（多继承 extension 拆分）
python/semantic_kernel/functions/kernel_function_decorator.py   # @kernel_function 注册
python/semantic_kernel/agents/orchestration/{group_chat,sequential,concurrent,handoffs,magentic}.py
python/semantic_kernel/agents/orchestration/agent_actor_base.py  # actor 模型基座
python/semantic_kernel/connectors/mcp.py                  # MCP 接入
dotnet/src/SemanticKernel.Abstractions/Kernel.cs          # .NET Kernel + 递归 filter 链
dotnet/src/Agents/Core/AgentGroupChat.cs                  # 双策略群聊
dotnet/src/Agents/Orchestration/                          # Handoff/AgentActor/OrchestrationResult
docs/decisions/0071-multi-agent-orchestration.md          # 多智能体编排 ADR（AutoGen 汇流背景）
python/samples/getting_started_with_agents/               # 最佳上手样例集
```

## 五、深读子页地图（30 页精选 6）

| 子页 | full.md 行号 | 为什么值得读 |
|---|---|---|
| 1 Overview | L6 | 双语言实现矩阵 + 概念→代码实体映射图，5 分钟建立全景 |
| 3.1 Kernel Orchestration | L1632 | filter 洋葱模型 .NET/Python 双实现对照，学切面设计范本 |
| 3.2 Functions and Plugins | L2088 | 三源函数归一 + 模板引擎块化 tokenization，SK 灵魂 |
| 5 Agent Framework | L4168 | Agent 类层次 + 五种云厂商 agent + YAML 声明式规格 |
| 5.4 Multi-Agent Orchestration | L5393 | 五编排模式 + Magentic-One Task Ledger + actor runtime |
| 6.6 MCP Integration | L7078 | MCP 作为 plugin 与 sampling 双向接入的最新实践 |

## 六、与"我们"的关系（一句话）

它是讲透 Agent 系列讲解"工具注册/function-calling 循环/多智能体编排/MCP 接入"时最合适的微软系生产级参照（与 LangChain/CrewAI 对照出"强类型企业风 vs 快速原型风"），其三源函数归一 + filter pipeline 设计是写"讲透 Agent 架构"章节的一手工程素材。

---
生成：2026-08-21 · deepwiki 30 页全归档
