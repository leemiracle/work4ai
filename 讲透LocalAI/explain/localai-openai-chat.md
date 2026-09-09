# localai-openai-chat — ChatEndpoint 管线、ComputeChoices 与流式 worker 解耦

> 源码：`core/http/endpoints/openai/chat.go`（1149 行）+ 同包 `inference.go` 的 `ComputeChoices`（195 行）
> 定位：`/v1/chat/completions` 主 handler——OpenAI 兼容面的心脏

## 角色定位

18 层架构中"API 兼容层"的主干。OpenAI 客户端生态（任意 SDK、Web UI、agent 框架）打到 LocalAI 的流量绝大多数落在这一条 handler 上。它上游承接请求中间件（鉴权/PII 脱敏/模型配置解析已完成，168-178 行直接从 echo context 取产物），下游经 `ComputeChoices`→`ModelInferenceFunc` 进入 gRPC/embed 后端层。它还是**多协议复用源**：图谱显示 anthropic `/v1/messages`、ollama `/api/chat|generate`、openresponses、localai/mcp 五个端点复用其产物与流程片段——OpenAI 语义是仓内事实上的"中间语言"。

## 内部结构

- `ChatEndpoint`（162-1100 行）：闭包工厂，参数即依赖注入——`ModelConfigLoader`/`ModelLoader`/`templates.Evaluator`/`ApplicationConfig`/`MCPNATSClient`/`assistantHolder`/`compressor` 七件套；返回 `echo.HandlerFunc`。内部 940 行单闭包按"准备段→流式分支→非流式分支"组织。
- 辅助四件套（30-160 行）：`stripEmptySystemMessages`（剔除 Web UI 空白 system 轮，防其覆盖 YAML system_prompt）、`mergeToolCallDeltas`（跨 chunk 按 index 拼接 tool_call 增量：id/name 首现定形、arguments 流式拼接）、`applyAutoparserOverride`（C++ autoparser 增量结果覆盖 Go 侧解析）、`handleQuestion`（函数结果回塞对话再生成）。
- 尾部：`forwardCloudProxyOpenAIViaBackend`（1143）云代理旁路。
- `ComputeChoices`（inference.go 24-195）：从 OpenAIRequest 抽取多模态数组/tools JSON/logprobs/logit_bias → `ModelInferenceFunc` 拿推理闭包 → n 个 choice × maxRetries 5 重试循环 → 返回 `[]Choice + TokenUsage + []*pb.ChatDelta`。

## 外部连接

被 `core/http/routes/openai.go` 注册；被 5 个姊妹端点 import（anthropic/ollama/openresponses/mcp）。依赖 `middleware`（压缩/usage 戳）、`templates.Evaluator`（提示模板）、`functions`（GBNF 语法生成与 tool call 解析）、`reason`（思考标签检测与分离）、`mcpTools`（MCP 执行器/assistant 持有者）、`backend.TokenUsage`。ChatDelta 从 pb 类型直达此层——C++ autoparser 的产物穿透到 HTTP 边缘。

## 数据流

**准备段**（168-434 行）：

1. 168-192：取中间件产物（OpenAIRequest+ModelConfig）；`stripEmptySystemMessages`；tokenizer-template 模型补注 YAML system_prompt。
2. 194-204：**云代理旁路**——passthrough 模式整体绕过本地管线（模板/MCP/gRPC），直接 `forwardCloudProxyOpenAIViaBackend`。
3. 206-295：工具收集；**LocalAI Assistant 模式优先**（218-254：admin 的进程内 MCP 工具面 + 内置安全 system prompt，且 disable 标志热读——改设置下一请求即生效）；常规 MCP：服务器工具发现注入 + prompt/resource 消息前插。
4. 324-414：response_format→grammar（`json_object`→内置 JSONBNF；`json_schema`→JSONFunctionStructure.Grammar）；shouldUseFn 时函数列表→GBNF 语法（自动追加 noAction 兜底函数，可配名）。
5. 427-434：非 tokenizer-template 模型渲染提示模板得 `predInput`。

**流式分支**（436-732 行）：SSE 头就位后进入 **MCP 迭代外循环**（≤max 10 或 Agent.MaxIterations）：

- 起 goroutine 跑 `processStream`/`processStreamWithTools`，经 `responses` channel 发 OpenAIResponse chunk，终态经 `ended` channel 回传 usage/err——**生成与 HTTP 写出解耦**的关键结构。
- 主循环 `select`：`input.Context.Done`（客户端断连→Cancel→break）；`responses` chunk（有 tool_call 增量则 merge 收集；原始 content 累积进 collectedContent 供 MCP 回灌与自动解析——**用未过滤原文**，PII 遮蔽不破坏 tool-call 标记，521-527 注释）；写 SSE 并 Flush；`ended` 终态（错误→SSE 错误帧+[DONE]）。
- 573-579：客户端断连后 **drain responses channel** 直到 worker close——防 goroutine 卡在发送上泄漏。
- 582-633：收集到 MCP tool call→执行工具、结果以 `mcp_tool_result` 事件流出、追加 assistant/tool 消息、`continue` 下一轮迭代（重新压缩+重渲染模板）。
- 637-670：AutomaticToolParsingFallback——请求没带工具但模型吐了工具标记，解析成 tool_call chunk 补发。
- 673-726：finish_reason 判定（stop/tool_calls/function_call/**length**——#9716：撞 max_tokens 不是"空响应"）；最终空 delta 帧 + `StampUsage` + include_usage 时 usage trailer（#9927：tools 路径曾漏报）+ `[DONE]`。

**非流式分支**（735-1100 行）：同样 MCP 外循环；`tokenCallback` 里做思考标签提取（shouldUseFn 时只存原文、解析后置）；`ComputeChoices`（793-819）带 `shouldRetry` 闭包——仅当"只有 reasoning 没有产出"时重试（809-817）；随后 **三级 tool call 解析优先级**（836-854）：C++ ChatDeltas 工具调用 > ChatDeltas 纯 content（Gemma 4 案例：Go 侧把干净 content 误判成思考）> Go 侧原文正则解析；无工具要走 `handleQuestion`（函数结果作为问题答案再生成一轮），有工具则组装 tool_calls/function_call choice。

## 设计决策

1. **worker 解耦的流式架构**：goroutine 生成 + channel 传递 + select 三路复用（ctx/数据/终态），错误走数据流不下沉为 panic；drain 兜底断连场景——一套结构同时满足 SSE 实时性、取消传播、资源回收。
2. **OpenAI 规范的像素级跟随**：usage trailer 仅在 include_usage 出现、length 与空响应的区分、`chat.completion.chunk` 对象类型——注释直接引用 issue 号，兼容性靠测试钉死。
3. **双解析器策略**（C++ autoparser 优先、Go 解析兜底）：新模型家族的思考标签层出不穷，把解析职责下沉到引擎侧同时保留 Go 兜底，两端各吃一半长尾。
4. **MCP agent 循环上浮到 HTTP 层**：多轮工具执行（含上下文重压缩、重模板）在 handler 内完成而非独立 agent 框架——OpenAI 端点原生具备轻量 agentic 能力。
5. **云代理旁路**：passthrough 一条 early return，避免"为了不用管线而先建管线"。

## 新人提示

- 切入点：先读 436-732 流式主循环（select 结构一目了然），再回头读准备段；非流式分支与流式共享九成准备代码，读一半得全部。
- 易混淆点一：`processStream`/`processStreamWithTools` 定义在同包 stream.go，不在本文件——本文件只见 channel 协议。
- 易混淆点二：`shouldUseFn`（有函数且允许）与 `toolsCalled`（模型实际调了）是两个阶段的事实；finish_reason 用后者。
- 易混淆点三：SSE 错误帧后仍发 `[DONE]`——OpenAI 客户端解析器依赖它收尾，漏发会挂死客户端。
- 调试流式问题加 `--log-level=debug`：每个 chunk、每次 MCP 迭代、grammar 生成都有 xlog.Debug 埋点（434、462、534、604 行等）。
