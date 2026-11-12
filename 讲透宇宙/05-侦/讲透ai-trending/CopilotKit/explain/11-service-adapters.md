# 11 · 服务适配器群：LLM 适配层与 agent 接线的两代形态

## 角色定位（16 层架构中位置）

本篇覆盖图谱第 5 层「runtime v1 服务适配器」（`packages/runtime/src/service-adapters/`）与第 4 层里的 agent-integrations 角落（`packages/runtime/src/lib/runtime/agent-integrations/`）。二者是 v1 服务端的两条对称接线：**service-adapters 向下接 LLM 提供商**（把 CopilotKit 的统一请求翻译成 OpenAI/Anthropic/Groq/Bedrock 等 SDK 调用，把响应流转译回 CopilotKit 事件流），**agent-integrations 向旁接 agent 框架**（LangGraph 的 agent 真身）。它们都服务于第 4 层的 v1 GraphQL 主线（copilot.resolver 的 generateCopilotResponse）；v2 线（第 6 层）走 AG-UI 协议 + BuiltInAgent，把这两类接线大部分外移给了 @ag-ui 生态——所以本篇也是理解"v1 怎么被 v2 替代"的最佳切片。

一句话：service-adapters 是"多 LLM 厂商的电源转换头"，agent-integrations 是"LangGraph 世界的大门"。

## 内部结构（关键文件+行号锚拆解）

### 纯接口基座：service-adapter.ts

`service-adapters/service-adapter.ts` 是纯 TypeScript interface 文件（tree-sitter 零提取属预期，语义由 file 节点承载——digest b3）：`CopilotKitResponse`（`stream: ReadableStream` + 可选 headers，`:10-13`）、`CopilotRuntimeChatCompletionRequest`（`:15-27`，携带 eventSource/messages/actions/model/threadId/runId/forwardedParameters/agentSession 等全套 v1 请求语义）、`CopilotRuntimeChatCompletionResponse`（`:29-33`）与核心 `CopilotServiceAdapter`（`:35-40`，`provider?/model?` + 唯一方法 `process(request)`）。注意它 import 了 graphql 层的类型（`../graphql/types/converted` 的 Message、inputs 目录的 ActionInput 等）——**适配器接口与 v1 GraphQL schema 深度耦合**，这是 v2 换 AG-UI 协议时整个层被边缘化的根因。

### 目录全家福与 18 行 barrel

`service-adapters/index.ts`（18 行纯 re-export barrel，scanner batchImportData 全空的典型盲区，13 条边手工补录——digest b13）按序导出：openai / langchain / google / openai-assistant / unify / groq / anthropic / experimental-ollama / bedrock / empty 十家，加 `export * from "./shared"`（`:8`）与 langserve 的 RemoteChain（`:7`）。

### 三种接入姿态

十家适配器分三种结构姿态（全部经 grep 核实）：

**姿态一：implements 直接实现**——OpenAI 系。`OpenAIAdapter implements CopilotServiceAdapter`（`openai/openai-adapter.ts:108`，DEFAULT_MODEL "gpt-4o" `:69`）、`GroqAdapter implements CopilotServiceAdapter`（`groq/groq-adapter.ts:58`，DEFAULT_MODEL "llama-3.3-70b-versatile" `:34`）、`UnifyAdapter implements CopilotServiceAdapter`（`unify/unify-adapter.ts:36`）、`AnthropicAdapter implements CopilotServiceAdapter`（`anthropic/anthropic-adapter.ts:81`，DEFAULT_MODEL "claude-3-5-sonnet-latest" `:42`，provider "anthropic" `:83`）。其中 **Groq 与 Unify 复用 openai 转换层**：两家都从 `../openai/utils` 导入 `convertActionInputToOpenAITool / convertMessageToOpenAIMessage / limitMessagesToTokenCount` 三件套（`groq/groq-adapter.ts:30-34`、`unify/unify-adapter.ts:29`）——Groq/Unify 的 API 与 OpenAI 形状兼容，共享转换是最经济的复用；Anthropic 则自带 utils.ts 独立实现（消息形状不兼容）。

**姿态二：extends LangChainAdapter**——LangChain 生态的"免写"通道。`LangChainAdapter implements CopilotServiceAdapter`（`langchain/langchain-adapter.ts:64`）是基类，`BedrockAdapter extends LangChainAdapter`（`bedrock/bedrock-adapter.ts:48`，DEFAULT_MODEL "amazon.nova-lite-v1:0" `:46`）与 `GoogleGenerativeAIAdapter extends LangChainAdapter`（`google/google-genai-adapter.ts:39`）白嫖 LangChain 的 Runnable 统一接口——只要厂商有 LangChain 集成，适配器只剩构造与默认模型。

**姿态三：哨兵**——`empty/empty-adapter.ts` 空实现（返回空流），测试与降级用。

### events.ts：ReplaySubject 解耦

`service-adapters/events.ts:134` `RuntimeEventSubject extends ReplaySubject<RuntimeEvent>`——RxJS ReplaySubject 保证**后订阅者可回放全部历史事件**，这是 GraphQL SSE 订阅与适配器产出解耦的关键（digest b3）：适配器先开跑、订阅后建立，事件不丢。`RuntimeEventSource`（`:287-288`）持有私有 eventStream$。

### failed-response-status-reasons 继承族

`packages/runtime/src/utils/failed-response-status-reasons.ts`（46 行）是 GraphQL 失败状态的类型化工厂族：基类 `FailedResponseStatus` 来自 `../graphql/types/response-status.type`（`:1-4`），三个子类各钉一个 reason 枚举——`GuardrailsValidationFailureResponse`（`:6-18`，reason=GUARDRAILS_VALIDATION_FAILED，details.guardrailsReason）、`MessageStreamInterruptedResponse`（`:20-34`，reason=MESSAGE_STREAM_INTERRUPTED，details 带 messageId+description）、`UnknownErrorResponse`（`:36+`，details 可携带 originalError 的 code/statusCode/severity/visibility/extensions 全套元数据）。彩蛋：`:31` 的 description 硬编码 "Check the message for mode details"——**mode 是 more 的拼写错误**，且会原样发给前端用户。

### agent-integrations：langgraph 真身 + lib 哨兵

agent-integrations 目录只有一个真子包 langgraph（甄别注：任务书语境"AG2/ADK/Agno/Strands/CrewAI 等外部框架接线"经核实**不在本仓代码里**——它们是知识层接线，见"外部连接"节）：

- **真身**：`agent-integrations/langgraph/agent.ts:38` `export class LangGraphAgent extends AGUILangGraphAgent`——基类以别名 import 自外部包 @ag-ui/langgraph（`:11` `LangGraphAgent as AGUILangGraphAgent`），文件头注释 `:29` 明言"Import and re-export from separate file to maintain API compatibility"。核心扩展是 `dispatchEvent(event)`（`:43`）：对 `EventType.CUSTOM` 事件做白名单转译——如 `CopilotKitManuallyEmitMessage` 命中时把一个 custom 事件展开成 TEXT_MESSAGE_START/CONTENT/END 三连发（`:51-70`），然后 `return true` 阻断默认分发（`:66`）；CopilotKitManuallyEmitToolCall 等其余白名单分支同型（`:90/:105/:114` 三处 return true）。这是 CopilotKit 扩展 AG-UI 协议的桥接点——Python/JS SDK 的 emit 系列手动事件在此被翻译成标准 AG-UI 事件流。
- **哨兵**：`packages/runtime/src/lib/index.ts` 头部正常 re-export 十家适配器与 copilot-runtime（`:1-10`），然后是一排"构造即 throw"的哑类：`export class LangGraphAgent { constructor() { throw new Error("LangGraphAgent import from @copilotkit/runtime is deprecated. Please import it from @copilotkit/runtime/langgraph instead") } }`（`lib/index.ts:16-24`）——LangGraphHttpAgent（`:27-33`）、TextMessageEvents、ToolCallEvents、CustomEventNames、PredictStateTool 同款（`:38/:42/:46/:50` 附近）。这是"编译期兼容+运行期报错引导"的硬哨兵（与 sdk-python 的软警告形成对比）：老代码 `import { LangGraphAgent } from "@copilotkit/runtime"` 仍能编译，一实例化就得到指路错误。

## 外部连接（imports 边上下游）

- **上游（被消费的 LLM SDK）**：openai SDK（openai-adapter + openai-assistant-adapter 双形态）、@anthropic-ai/sdk（anthropic-adapter `:110` createAnthropic）、groq-sdk（groq-adapter `:20` type import ChatCompletionMessageParam）、@langchain/core（langchain 基类 + langserve 的 `require("langchain/runnables/remote")` 运行时动态加载）、@google/ 与 AWS Bedrock 经 LangChain 间接接入。runtime 的 package.json 把这些全部放 peerDependencies **且标 optional**（九项全 optional，digest b34）——按需加载，装哪家用哪家。
- **上游（agent 框架）**：@ag-ui/langgraph（LangGraphAgent 基类）——agent 框架接入在 v2 时代的标准路径是 AG-UI 生态：`@ag-ui/agno`（AgnoAgent，wiring-external-agents.md:15）、`@ag-ui/client` HttpAgent（AG2/任意 AG-UI server，`:18`）、A2A（要求预建 A2AClient 实例非 URL）。
- **下游消费者**：v1 GraphQL copilot.resolver 的 generateCopilotResponse 按 model/provider 选适配器；conversion.ts 做 AG-UI↔v1 消息转换；`shared/sdk-client-utils.ts` 零 import 自含，用窄化类型断言绕过 SDK 无公共访问器的私有字段。
- **知识层接线**（本仓无代码的框架）：`skills/runtime/references/` 的 wiring 系列八篇——wiring-agno / wiring-aws-strands / wiring-ag2 / wiring-adk（Google ADK）/ wiring-a2a / wiring-crewai-crews / wiring-crewai-flows / wiring-mastra，总览表在 wiring-external-agents.md（Agno 行 `:15`、AG2 行 `:18`，References 清单 `:337-340`）。这些文档描述的 import 全部来自 @ag-ui/* 外部包与用户项目，不发仓内 imports 边——**框架接线的"实现"在 AG-UI 生态，CopilotKit 只提供知识与协议消费**。

## 数据流

一次 v1 LLM 调用（service-adapter 视角）：

1. GraphQL mutation `generateCopilotResponse` 到达 → copilot.resolver 组装 `CopilotRuntimeChatCompletionRequest`（messages/actions/forwardedParameters...）；
2. runtime 按用户传的 adapter 实例调 `adapter.process(request)`；
3. 适配器内部三步：`convertMessageToOpenAIMessage` 族转换消息（Groq/Unify 复用 openai/utils，`groq-adapter.ts:30-34`）→ 调厂商 SDK（streaming）→ 把厂商 chunk 流转译成 RuntimeEvent 推进 `RuntimeEventSource.eventStream$`（ReplaySubject，`events.ts:287-288`）；
4. process() 返回 `CopilotKitResponse { stream }`；GraphQL 层的 Repeater 逐块 push，content/arguments 以 string[] 分块形态进 GraphQL 响应（copilot-response.type.ts）；
5. 失败路径：厂商错误 → `convertServiceAdapterError`（shared）→ 若 Guardrails 拦截/流中断/未知错误，构造 failed-response-status-reasons.ts 的对应子类（`:6/:20/:36`），reason 枚举进 GraphQL ResponseStatusUnion 的多态分发。

agent 接线数据流（langgraph 视角）：Python emit 系列（sdk-python）→ LangGraph 事件流 → AGUILangGraphAgent 基类消费 → LangGraphAgent.dispatchEvent（`agent.ts:43`）把 CopilotKit 手动事件白名单转译为标准 AG-UI 事件 → return true 阻断默认分发防双发。

## 设计决策

- **三种姿态反映接入成本梯度**：厂商 API 像 OpenAI → 直接 implements（写一次转换）；厂商进了 LangChain 生态 → extends 白嫖（零转换代码）；API 兼容 OpenAI 但 endpoint 不同（Groq/Unify）→ implements + 复用 openai/utils（转换一份，客户端两个）。这个梯度让"新增一家厂商"的成本从 500 行到 5 行不等。
- **接口与 GraphQL 耦合是 v1 的原罪**：service-adapter.ts import graphql inputs/types，适配器测试要拉整套 GraphQL 语义；v2 的 AG-UI 协议把消息格式标准化后，这个层的历史使命基本结束——现存十家适配器更像兼容性仓库而非演进方向。
- **硬哨兵 vs 软警告**：LangGraphAgent 的哑类 throw（`lib/index.ts:16-24`）比 sdk-python langchain.py 的 warnings.warn 更激进——因为 agent 类的构造参数在新旧路径语义已不同（旧签名直接错），静默成功比报错更危险；而 Python emit 函数行为没变，只需提示换门牌。
- **dispatchEvent 的 return true 协议**：白名单命中→转译→return true（默认分发跳过）；未命中→走 AG-UI 默认路径。这种"拦截器返回布尔"的模式让 CopilotKit 的协议扩展点收敛在一个方法里，新增手动事件类型只改一个文件。
- **wiring 文档层与代码层分离**：AG2/ADK/Agno/Strands/CrewAI 零仓内代码是刻意架构——AG-UI 协议把"框架适配"外包给生态（@ag-ui/agno 等由框架方或 AG-UI 维护），CopilotKit 只需是合格的 AG-UI 消费者。对比 v1 时代每接一家要在本仓写 adapter，v2 的接线成本转移给了生态。
- **继承族为 GraphQL 联合类型而生**：FailedResponseStatus 三子类的 reason/details 结构与 response-status.type.ts 的 `@InterfaceType resolveType 按 code 多态分发`（digest b3）严格对齐——类型系统（TS 继承）与 schema 系统（GraphQL 联合）双轨同构，新增失败原因要同时动两处。

## 新人提示

1. **选适配器先看姿态**：Bedrock/Google 用户直接 `new BedrockAdapter()`——LangChain 帮你写了；Groq/Unify 用户放心用，它们吃的是 openai/utils 的转换（`groq-adapter.ts:30-34`）；真正需要读实现细节的只有 openai/anthropic 两家。
2. **加新 LLM 厂商的 checklist**：API 像 OpenAI → 抄 groq-adapter.ts（改 DEFAULT_MODEL 与 provider 字符串即可，约 60 行）；有 LangChain 集成 → 抄 bedrock-adapter.ts（更短）；都不像 → 抄 anthropic-adapter.ts（要自带 utils）。
3. **别从 `@copilotkit/runtime` 根导入 LangGraphAgent**——那是 throw 的哑类（`lib/index.ts:16-24`）；正确路径 `@copilotkit/runtime/langgraph`（package.json 的子路径 exports）。
4. **读 agent.ts 只需读 dispatchEvent**（`agent.ts:43`）：所有 CopilotKit↔AG-UI 方言翻译都在这一个方法的白名单分支里，其余全是基类委托。
5. **报错文案彩蛋**：`failed-response-status-reasons.ts:31` 的 "Check the message for mode details" 是 more 的笔误且直达用户——改它是一行 PR，但先确认没有下游对文案做字符串匹配。
6. **v2 项目的框架接线去 wiring 文档找**：`skills/runtime/references/wiring-*.md` 八篇是唯一权威（外部框架经 @ag-ui/* 接入，仓内无对应代码），别在 service-adapters 里找 Agno/Strands——这里只有 LLM 适配器。
