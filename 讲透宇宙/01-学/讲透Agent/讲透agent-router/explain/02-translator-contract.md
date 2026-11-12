# 02 · translator 契约与 SSE 地基：几十个翻译器共用的一套骨架

## 一、角色定位

`internal/translator` 是全仓心脏（88 文件）：客户端说 OpenAI 或 Anthropic 方言，后端说各家原生方言，本包在两套词汇表间来回改写请求与响应。`translator.go:48` 的泛型接口约束全部翻译器，每种 from_To 组合一个文件，文件名即方向（openai_awsbedrock.go = OpenAI 入 → Bedrock 出）。本篇讲契约、流式地基与直通族，多云重方向见 03 篇。

## 二、内部结构

**四方法契约（translator.go:48）**：`RequestBody(raw, body, flag)` 翻请求体——flag 是"forceBodyMutation 或 onRetry"（translator.go:52），首次发送与故障重发行为可不同；`ResponseHeaders`（:61）改响应头；`ResponseBody`（:69）回译响应体并顺带产出 tokenUsage 与 responseModel——计费与指标全靠这个出口；`ResponseError`（:78）把非 2xx 译回客户端方言。注释明确**每请求新建、非线程安全**（:47）。

**可选能力接口**：`ContentTypeSetter`（translator.go:110，multipart 需 boundary）、`RequestHeadersSetter`（:114）、`HeaderValueFilterSetter`（:120，多值头过滤）、双 Redactor（:130、:141）。extproc 用类型断言探测（processor_impl.go:781）。

**SSE 三件套（util.go）**：`cutSSEFieldPrefix`（util.go:40）剥 `data:` 前缀且只容忍一个空格；`nextSSEEvent`（:56）按 `\n\n` 或 `\r\n\r\n` 切完整事件、半包留 buffer（LF/CRLF 兼容）。序列化侧 `serializeOpenAIChatCompletionChunk`（:111）统一拼 `data: {...}\n\n`，`sseDoneFullLine`（:34）预生成 `[DONE]` 行；`forceOriginalBodyIfEmpty`（:92）兜底回填原体。

**直通族 openai_openai.go**：`NewChatCompletionOpenAIToOpenAITranslator`（openai_openai.go:30）并非纯透传——`RequestBody`（:69）用 sjson 覆写 model（:79；`sjsonOptions` 在 translator.go:187，注释强调 ReplaceInPlace 必须为 false：重试会多次调用须幂等）、设 path 头（:88）。AWS 变体（:36）多一个 `forceRequestBodyMutation`：SigV4 签的是最终 body，须原样输出（:49）。`ResponseBody`（:143）流式透传增量但持续扫 usage（:152），非流式细分 cached/reasoning token（:179）并 `cmp.Or` 兜底缺失 model（:190）。流式提取在 `extractUsageFromBufferEvent`（:199）：逐行切、剥前缀、跳坏行、同批多 usage 取最新。

**Azure 变体**：内嵌直通翻译器（openai_azureopenai.go:44）只覆写 `RequestBody`（:49）——Azure 从 URI 的 deployment-id 取模型而非 body（:42），path 模板 `/openai/deployments/%s/chat/completions?api-version=%s`（:63）。重试时 path 可能已被改写，靠这层设回。

## 三、外部连接

- **extproc**：upstream 处理器请求头阶段调 `RequestBody`（processor_impl.go:375）、响应阶段调 ResponseHeaders/Body（:516）；SetBackend 探测可选接口（:781）。
- **apischema**：ReqT/RespT 全来自 internal/apischema 手写 wire 类型。
- **tracing**：SpanT 即 tracingapi 各端点 span（translator.go:152-183 定义 13 个类型别名），回译时顺手记录 chunk（openai_openai.go:216）。
- **internalapi**：共享 `ErrInvalidRequestBody` 错误语义，extproc 识别后转 422 用户可见错误。

## 四、数据流

直通翻译生命周期：构造（带 modelNameOverride）→ `RequestBody`：模型覆写则 sjson 改写、设 `:path`，flag 为真时无改动也回填原体 → Envoy 转发 → 流式则每个 SSE 块进 `ResponseBody`：累积 buffer、扫 usage、原文与 usage 一并返回（直通族只"旁听"）→ 非流式整体解码、填 Usage、返回 tokenUsage。出错走 `ResponseError`：`convertErrorOpenAIToOpenAIError`（openai_openai.go:106）把非 JSON 错误体（如连接失败的 503 文本）包成 OpenAI error JSON（:107）。

## 五、设计决策

1. **泛型四方法**：一个接口约束 88 个文件，编译期保证每方向实现四阶段；SpanT 让翻译器不依赖具体 tracing 实现就能记事件。
2. **flag 承载重试语义**：不另设 RetryTranslator 类型，靠布尔上下文切换（onRetry 强制重放原体），代价是 flag 含义随实现漂移。
3. **SSE 手写解析**：encoding/json 与 SSE 事件级 framing 不匹配，三件套统一了切分/剥前缀/半包保留行为，所有流式翻译器复用。
4. **直通也要建模**：模型覆写、path 重写、usage 旁听、SigV4 强制输出体都发生在"直通"层——passthrough 是营销词不是代码事实。

## 六、新人提示

改 OpenAI↔Anthropic 映射先看 anthropic_helper.go（1541 行共享库，双向入口都被波及）；加新组合：拷最近似的 from_To 文件改四方法，再补 apischema 类型。测试在 `internal/translator/*_test.go` 与 `tests/data-plane`。坑：流式 usage 扫描只处理完整行（:201），半行留给下一批；翻译器每请求新建，别塞跨请求状态。
