# 03 · 翻译矩阵最重的一行：OpenAI 到 AWS Bedrock 的双向改写

## 一、角色定位

02 篇讲契约，本篇啃矩阵最重方向：客户端说 OpenAI，后端是 AWS Bedrock。AWS 有两条线：`openai_awsbedrock.go` 映射为 Bedrock **Converse API**（openai_awsbedrock.go:37 注释明确"用 Converse 而非其兼容 API"）；`openai_awsanthropic.go` 走 InvokeModel 调原生 Claude。这条线必须存在：thinking budget、cachePoint、事件流回译只有原生 API 才有等价物。它也是"加一个云厂商写多少代码"的标尺：约 800+400 行。

## 二、内部结构

**请求方向（openai_awsbedrock.go:103）**：流式与否决定 path（:107）；模型名 URL 编码防 ARN 特殊字符（:121）；InferenceConfig 承接 temperature/topP/maxTokens（:125，两个 max 字段 `cmp.Or` 合流）；stop 兼容字符串/数组（:135）。thinking 进附加字段（:142，三态 :57），reasoning_effort 转 reasoning_config（:150，GLM/Nova）。消息转换（:183）：assistant 空内容丢弃（:206，OpenCode 这类客户端会发）；**tool 角色并入 user**（:250），连续 tool 消息再合并（:257）。工具转 ToolConfig（converse_helper.go:29），tool_choice 映射 auto/any/tool（:59），指定工具名仅对 anthropic+claude 放行（:76）。cachePoint：标了缓存控制的块插 `CachePointBlock`（openai_awsbedrock.go:93；converse_helper.go:51：Tool 是 union，须独立成元素）。

**响应非流式（openai_awsbedrock.go:355）**：Bedrock 响应无 model 字段，responseModel 用请求模型（:358）；HTTP 200 但 output 缺失时 nil 守卫防 panic（:398，Coral 框架错误的半截响应）；usage 含 cacheRead/cacheWrite 并细化 PromptTokensDetails（:423）；content 块按 union 分派（:456）：toolUse 转回 tool_calls（:321）、text、reasoning——推理文本进 `reasoning_content`，signature/redacted 进 thinking_blocks（:473）。

**响应流式**：Bedrock 事件流不是 SSE 而是 **AWS eventstream 二进制分帧**。`extractAmazonEventStreamEvents`（openai_awsbedrock.go:521）把累积 buffer 喂 decoder（:524），按 `:event-type` 头分类（:535），半包退回 buffer（:531）；`convertEvent`（:550）逐事件转 OpenAI chunk，metadata 事件带最终 usage（:560）；`ResponseHeaders` 改写 content-type（:289）并存 requestid（:296）；流末补 `[DONE]`（:388）。

**InvokeModel 线（openai_awsanthropic.go）**：path `/model/%s/invoke` 或流式变体（:68）；body 由 `buildAnthropicParams` 复用 anthropic_helper（:74）再注入 `anthropic_version`（:86，默认 bedrock-2023-05-31 :32）；流式用 streamParser 从 eventstream 剥出 Anthropic SSE（:217）。**错误翻译** `bedrockResponseError`（converse_helper.go:362）：JSON 错误体按 BedrockException 解析、类型取 `x-amzn-errortype` 头（:375）；非 JSON 文本包成 OpenAI error。

## 三、外部连接

- **apischema/awsbedrock**：ConverseInput/ConverseStreamEvent/CachePointBlock 等 wire 类型。
- **02 篇契约**：四方法全实现，flag 在此被忽略（签名 `_ bool`，openai_awsbedrock.go:103）——每次全量重建 body，天然幂等。
- **anthropic_helper**：与 anthropic_* 方向共享转换。
- **extproc**：`GetTranslator` 按后端 schema 选中（processor_impl.go:768），usage 喂 metrics/配额。


## 四、数据流

一次 Converse 流式请求：`RequestBody` 组装 ConverseInput（角色合并、工具转 ToolSpec、thinking 进附加字段）→ 设 converse-stream 路径与 content-length → backendauth 加 SigV4 头 → Bedrock 返回 eventstream 二进制流 → `ResponseHeaders` 改 content-type → 每个 chunk 进 `ResponseBody`：buffer 追加、decoder 抽事件、convertEvent 转 OpenAI chunk、拼 SSE 下发、metadata 事件提 usage → 流末补 `[DONE]`。重试时 body 每次从 `originalRequestBody` 全量重建；非 2xx 走 ResponseError。

## 五、设计决策

1. **Converse 而非兼容面**：Bedrock 自带兼容 API 能力受限，Converse 才能表达 thinking budget、cachePoint、显式 cache token；代价是自建 eventstream 解码与事件状态机。
2. **消息模型修复**：空 assistant 消息、tool 角色在 Bedrock 不合法，翻译层主动修——方言净化是网关隐藏职责，修错一处就是后端 400。
3. **缓存点即协议**：cachePoint 是插入独立块（union 语义）而非普通字段，断点摆错位置则缓存全失效。
4. **流式半包纪律**：解码失败即回退 buffer（openai_awsbedrock.go:531）保证跨 chunk 帧完整——02 篇半包规则的二进制对应物。

## 六、新人提示

加新 Bedrock 能力：先改 apischema/awsbedrock 类型，再在 convertEvent 与消息转换处补双向映射，跑 `internal/translator/openai_awsbedrock_test.go`（表驱动覆盖角色合并与事件序列），真实行为用 tests/data-plane 盒带。坑：tool 消息合并推进外层循环变量 i（:272）；usage 只在 metadata 事件出现一次。
