# 06 · AG-UI 协议全链路：事件、转换器、Python 对称件与中间件链

> 定位文件：`skills/copilotkit-agui/`（协议规范镜像）+ `packages/runtime/src/graphql/message-conversion/`（双向转换器）+ `sdk-python/copilotkit/langgraph_agui_agent.py` + `@ag-ui/client` 消费面（图谱「shared 共享横切库」「runtime v1 服务端」「Python SDK」三层的协议纽带）

## 一、角色定位（16 层架构中位置）

AG-UI（Agent-User Interaction）是 CopilotKit 抽出的**开源事件协议**（独立 npm/PyPI 包族 @ag-ui/*，协议仓库在 ag-ui-ai/ag-ui），CopilotKit 全仓则是它最大的消费者与试验场。协议是前后端之间唯一的"语言"：服务端（runtime v1/v2，第 1 篇）把 agent 执行翻译成事件流；客户端（core 包的 HttpAgent，第 2 篇）把事件流回放成消息与状态。三层依赖它——shared 层 re-export 其消息类型、runtime v1 的 GraphQL 面用转换器在两套消息模型间摆渡、Python SDK 用 `ag_ui.core` 事件类做对称发射。**理解 AG-UI 是理解 CopilotKit 一切流式行为（打字机、工具卡、生成式 UI、interrupt）的钥匙**。

## 二、内部结构（关键文件+行号锚拆解）

### 2.1 事件 schema：生命周期骨架 + 弃用通道

协议规范（skills/copilotkit-agui/references/protocol-spec.md，源出 @ag-ui/core 的 Zod schema）：

- **BaseEvent 公共字段**（protocol-spec.md:8-18）：type 判别符 + 可选 timestamp/rawEvent；全部 schema 用 `.passthrough()`——**未知字段保留透传**，这是协议向前兼容的基石（第 3 篇 a2ui-surface 靠它塞自定义 lifecycle 字段）。
- **生命周期事件**：RUN_STARTED 携带 threadId/runId/parentRunId（分支与时间旅行指针，:40）与可选 input（本次 run 的完整输入回显，:42）；RUN_FINISHED 后同 runId 不得再有事件。
- **THINKING→REASONING 弃用通道**（protocol-spec.md:591-605）："Deprecated Events (Remove in 1.0.0" 章节列了 5 对替换（THINKING_START→REASONING_START 等），客户端 SDK 内置 `BackwardCompatibility_0_0_45` 中间件自动转换（:603）——**旧事件将在 1.0.0 移除**，自定义 agent 还在发 THINKING_* 的要排期迁移。
- **传输编码双轨**（protocol-spec.md:607-641）：**SSE 默认**（`data: <JSON>\n\n`，Content-Type text/event-stream）；**protobuf 可选**（@ag-ui/proto，Content-Type `application/x-ag-ui`），帧格式是**4 字节大端 uint32 长度前缀 + protobuf 编码消息体**（:632）。服务端 EventEncoder 按 Accept 头自动选择（:636-641：getContentType() 返回二选一，encodeBinary() 产出 Uint8Array）。

### 2.2 客户端传输内幕（skills/copilotkit-agui/references/client-sdk.md）

请求流五步（client-sdk.md:583-593）：HttpAgent.run → runHttpRequest 返回 HttpEvent 流（HeadersEvent/DataEvent 二态）→ `transformHttpEventStream()` 按 content-type 分流——`application/x-ag-ui` 走 protobuf parser，**其余一切**走 SSE parser（:588-589）→ SSE 按 `\n\n` 切帧提取 data: 行 → JSON 过 `EventSchemas.parse()`（Zod 判别联合校验）。错误语义（:597-601）：AbortError 转 `RUN_ERROR code:"abort"`——中止在网络层和协议层有正式对应物。**注意：本仓未装 node_modules，@ag-ui/client 是外部依赖，其行为以上述镜像文档 + 第 2 篇 HttpAgent 源码为准。**

### 2.3 gql↔agui 双向转换器（packages/runtime/src/graphql/message-conversion/，384+297 行）

v1 GraphQL API 的消息模型（TextMessage/ResultMessage/ActionExecutionMessage/AgentStateMessage/ImageMessage）与 AG-UI Message 的摆渡器：

- **aguiToGQL**（agui-to-gql.ts:81-184）：按消息形态分支——AgentState 消息（结构探测 isAgentStateMessage，:17-22）映射并可选保留 render 函数到 coAgentStateRenders（:97-106）；带图消息走 aguiMessageWithImageToGQLMessage（:121-122）；assistant+toolCalls 先出文本消息再逐 toolCall 生成 ActionExecutionMessage，**toolCall 名字按 id 记账**供后续 result 消息回查（:126-129），generativeUI 挂给同名 action、无同名则挂给 `*` 通配 action（:133-155 的 specific/wildcard 双优先级）。
- **reasoning 跳过**（任务书命题源码实证）：agui-to-gql.ts:157-160——`message.role === "reasoning"` 直接 `continue`，注释钉版："Reasoning messages are ephemeral display-only content with no GQL equivalent — skip them"（推理消息是临时展示内容、GQL 侧无对应物）。测试固化该语义（agui-to-gql.test.ts:1316 "should silently skip reasoning messages"、:1337 交错场景）。**方向性丢失**是刻意的：gqlToAGUI 不可能恢复 reasoning。
- **gqlToAGUI**（gql-to-agui.ts:19-56）：先扫一遍把 ResultMessage 的结果按 actionExecutionId 建 Map（:27-32），再逐消息分支转换；未知类型直接 throw（:54）。图片格式白名单 VALID_IMAGE_FORMATS = jpeg/png/webp/gif（gql-to-agui.ts:6，NOTES-DIGEST batch-21 钉版"与代码库其他处保持同步"）。
- **类型别名技巧**：`import * as agui from "@copilotkit/shared"; // named agui for clarity, but this only includes agui message types`（agui-to-gql.ts:3）——shared 包 re-export AG-UI 类型，转换器别名为 agui 提高可读性；图谱因此发的是对 shared 的边而非对 @ag-ui/client 的边。
- 唯一仓内消费者是 v1 的 copilot-runtime.ts:621（aguiToGQL(body.messages)）——**转换器服务于 GraphQL 遗产面，v2 SSE 面根本不过这道桥**。

### 2.4 Python 对称件：LangGraphAGUIAgent（sdk-python/copilotkit/langgraph_agui_agent.py）

- 头部 import 群（:8-19）：`from ag_ui_langgraph import LangGraphAgent` + **从 ag_ui.core 直接 import 九个事件类**（EventType/CustomEvent/TextMessageStart/Content/End/ToolCallStart/Args/End/StateSnapshot）——Python 侧与 JS 侧事件 schema 同源对称。
- **CustomEventNames 三元组**（:37-41）：copilotkit_manually_emit_message / _tool_call / _intermediate_state——CopilotKit 扩展 AG-UI 的自定义事件命名空间，配合 LangGraphEventTypes（on_chat_model_stream/on_custom_event，:44-47）做事件分流。
- **LangGraphAGUIAgent extends LangGraphAgent**（:60-71）：构造后向 constant_schema_keys 追加 "copilotkit" 键——让 CopilotKit 的配置透传进 LangGraph state schema。
- **_dispatch_event 覆写**（:73-80）：拦截 CUSTOM 事件做 CopilotKit 白名单转译，被过滤的事件 **return None**——docstring 坦承违反基类 str 返回类型注解"但基类自己也违反"（返回事件对象），None 在 run() 进 encoder 前被滤掉。这是"继承外部基类但语义局部超载"的诚实文档化范例，与 JS 侧 langgraph agent 集成的 dispatchEvent 白名单转译（NOTES-DIGEST batch-29）互为镜像。
- emit 通道全链：sdk-python/copilotkit/protocol.py 的工厂函数逐事件类型实例化，emit_runtime_event(s) 经 get_context_queue 投递（NOTES-DIGEST batch-73）；langgraph.py 的 emit 系列经 copilotkit_customize_config 写入 config 自定义键、由 runtime/AG-UI 层消费（batch-70）。

### 2.5 @ag-ui/client 中间件链：run() 的洋葱模型

中间件拦截 run() 调用实现事件变换/过滤/增强（client-sdk.md:379-381）。抽象基类三个方法（:386-406）：abstract `run(input, next)`、`runNext`（跑下一个并允许 chunk 变换）、**`runNextWithState`**（附带 EventWithState——event + 事件应用后的 messages/state 快照，让中间件能基于"已应用状态"做决策，:399-406）。函数式中间件直接改 input（forwardedProps 注入示例 :413-427）。内置件：FilterToolCallsMiddleware（按工具名白名单滤 TOOL_CALL_* 事件，:429-436）；客户端自动追加的向后兼容件（BackwardCompatibility_0_0_39/:606-608 的 0_0_45 THINKING→REASONING 转换）。

**CopilotKit 仓内的三个中间件实例**（都 extends Middleware，全链闭环）：
- OpenGenerativeUIMiddleware（runtime v2，第 1 篇 open-generative-ui-middleware.ts:242）：clarinet SAX 把工具参数流式转成 ACTIVITY_DELTA——runNextWithState 消费者；
- @ag-ui/a2ui-middleware 与 @ag-ui/mcp-apps-middleware（外部包，runtime.ts:18-19 引类型）：由 runtime 配置自动套到 agent 上（第 1 篇 CopilotRuntimeMiddlewares）；
- transformHttpEventStream（SSE/protobuf 分流）本质是传输层中间件思维在 HttpAgent 内的实现。

## 三、外部连接（imports 边上下游）

- **协议真源（外部）**：@ag-ui/core（Zod schema 与事件类）、@ag-ui/client（AbstractAgent/HttpAgent/Middleware/事件枚举——core 包 agent.ts 与 runtime v2 都 extends 它）、@ag-ui/encoder（EventEncoder SSE/protobuf 双编码）、@ag-ui/proto（protobuf schema）、@ag-ui/a2ui-middleware、@ag-ui/mcp-apps-middleware；Python 侧 ag_ui.core + ag_ui_langgraph。
- **仓内消费面**：shared 层 re-export AG-UI 类型（转换器的 agui 别名来源）；core 包 ProxiedCopilotRuntimeAgent/IntelligenceAgent extends 其基类；runtime v2 的三组 UI 中间件配置；react-core v2 的 activity 渲染器消费 ACTIVITY_* 事件；web-inspector 显示事件流（cpki_event_id 行即 AG-UI 事件持久化）。
- **文档镜像**：skills/copilotkit-agui/（SKILL.md + protocol-spec/client-sdk/building-agents/event-flow-diagrams 四篇 references）与根 skills/a2ui-renderer 等——图谱"CopilotKit 技能资产"层与协议层的边。

## 四、数据流（一条 assistant 工具调用消息的协议旅程）

以 LangGraph Python agent 被 v2 前端调用为例：

1. 前端 HttpAgent.run POST /agent/{id}/run，Accept 头默认 SSE；
2. LangGraphAGUIAgent 包装的 graph 执行，on_chat_model_stream 事件进 _dispatch_event：文本 chunk → TextMessageContentEvent 实例（ag_ui.core 类）；工具调用 → ToolCallStart/Args/End；CopilotKit 自定义事件命中白名单转译，否则过滤为 None；
3. 事件经 encoder 序列化：SSE 帧或（若客户端 Accept: application/x-ag-ui）4 字节大端长度前缀 protobuf 帧；
4. 前端 transformHttpEventStream 按 content-type 分流 → SSE parser 切帧 → EventSchemas.parse() Zod 校验（.passthrough() 放行自定义字段）；
5. 中间件链洋葱式处理：BackwardCompatibility_0_0_45 先把可能残留的 THINKING_* 转 REASONING_*；runtime 侧配置的 A2UI/OpenGenUI/MCPApps 中间件把工具参数流改写为 ACTIVITY_*；
6. verifyEvents 校验生命周期合法性（connect 续流路径豁免——第 2 篇 intelligence-agent.ts:170）；事件应用进 thread store，UI 逐帧更新；
7. 同一条消息若走 v1 GraphQL 面：aguiToGQL 把它翻成 ActionExecutionMessage+ResultMessage（reasoning 消息在这步被跳过丢弃）；v2 SSE 面则全程 AG-UI 原生模型，零转换。

## 五、设计决策（为什么这么设计 + 替代方案）

- **事件协议 vs WebSocket 双工 RPC**：agent→UI 的本质是单向广播流（生成不可撤销、增量展示），SSE 单向流足够且穿透代理/CDN/Serverless 边缘的兼容性远好于 WS；Interactive 通道（interrupt、 HITL）复用同一事件流用 CUSTOM 事件名空间表达，而非另开双工连接。代价是"客户端→服务端"动作要走独立 HTTP 调用（run/stop 端点）。
- **SSE 默认 + protobuf 可选 vs 单一格式**：SSE 可读可调试（curl 直接看）、生态零依赖；protobuf 帧省带宽与解析 CPU（高频 TEXT_MESSAGE_CONTENT 场景收益大）。Accept 头协商让同一服务端无版本裂痕地服务两类客户端（EventEncoder 自动检测，protocol-spec.md:636-641）。
- **.passthrough() + CUSTOM 事件 vs 封闭枚举**：封闭 schema 每加一种事件要发版协议包；passthrough 保留未知字段 + CUSTOM 事件（带 name/value 自由载荷）让 CopilotKit 的 manully_emit 三元组、a2ui lifecycle 字段都能在旧客户端上向前兼容地跑。代价是拼写错误的字段名静默存活——测试必须覆盖序列化回路（仓内 roundtrip-conversion.test.ts 561 行专干这个）。
- **reasoning 单向丢弃 vs 协议双模型**：GQL 遗产面没有 reasoning 概念，硬塞要动 v1 schema（冻结面）；跳过的代价是 v1 客户端永远看不到思考过程——被 v2 原生面（CopilotChatReasoningMessage，第 3 篇）补位。
- **THINKING→REASONING 换名 + 兼容中间件 vs 语义版本化共存**：换名让协议词汇与 LLM 行业术语（reasoning model）对齐；BackwardCompatibility 中间件把迁移成本压到客户端 SDK 内部一行配置，弃用窗口到 1.0.0。

## 六、新人提示（坑+勘误+延伸阅读）

- **坑（协议知识的位置）**：@ag-ui/* 的实现在外部仓（node_modules 未安装），本仓内最权威的镜像是 skills/copilotkit-agui/references/protocol-spec.md 与 client-sdk.md（图谱 document 节点，行号锚可查）；源码级消费点看 packages/core/src/agent.ts 与 runtime v2。
- **坑（1.0.0 弃用红线）**：还在发 THINKING_* 事件的自定义 agent 将在 AG-UI 1.0.0 断裂（protocol-spec.md:591）；`BackwardCompatibility_0_0_45` 是客户端侧补丁，**服务端自测不会暴露**——跨版本集成测试必须真跑双端。
- **勘误（protobuf 只在特定路径出现）**：仓内源码 grep 不到 protobuf 实现（仅 sdk-python/poetry.lock 作为传递依赖出现）；4 字节大端帧格式是 @ag-ui/proto 的外部实现，本仓只在文档层引用——**别在 CopilotKit 仓里找 protobuf 编码器源码**。
- **转换器的服务边界**：gql↔agui 只服务 v1 GraphQL 面（唯一消费者 copilot-runtime.ts:621）；v2 全程 AG-UI 原生。排查 v1 消息丢失时先查 agui-to-gql.ts 的分支表（reasoning 必丢、未知 role 直接 throw :174-177）。
- **Python/JS 对称陷阱**：ag_ui.core 与 @ag-ui/core 的 schema 同源但发版节奏独立，CustomEventNames（langgraph_agui_agent.py:37-41）的字符串是**无 schema 保护的自由载荷**——拼错事件名两端都不会报错，只会静默无渲染。
- 延伸阅读：第 1 篇（服务端 OpenGenerativeUIMiddleware——中间件链的仓内最深实例）、第 2 篇（HttpAgent 与 verifyEvents 豁免）、skills/copilotkit-agui/references/event-flow-diagrams.md（生命周期事件的时序图集）；外部协议仓 ag-ui-ai/ag-ui 的 schema 定义。
