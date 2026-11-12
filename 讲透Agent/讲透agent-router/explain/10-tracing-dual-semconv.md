# 10 · tracing 双语义约定：OpenInference 与 OTel GenAI 之间的一线切换

## 一、角色定位

`internal/tracing`（93 个 Go 文件，L11 可观测性层）是 extproc 的"词汇表面"：把每个 LLM 请求/响应记录成 OpenTelemetry span。它的独特之处是**双语义约定并存**——同一份 span 数据可以按 OpenInference（Arize 主导，LangFuse/Phoenix 生态）或 OTel GenAI（官方 semconv）两套属性词汇表输出，由环境变量 `AI_GATEWAY_TRACING_SEMCONV` 一线切换，非法值直接拒绝启动。存在理由：网关用户的后端看板已经押注了某一套约定，换网关不该逼用户换看板；两套词汇表的属性名（`llm.token_count.total` vs `gen_ai.usage.total_tokens`）完全不同，必须在出口处二选一。

## 二、内部结构

**装配 tracing.go:143 `NewTracingFromEnv`**：三级判定——`OTEL_SDK_DISABLED=true` 或 `OTEL_TRACES_EXPORTER=none` 返回 Noop（:145/:150）；exporter 未设且无任何 OTLP endpoint 也 Noop（:160-167，注释引 OTEL 规范的 endpoint 优先级）；`console` 特判走同步 stdout（:216-225，测试友好），否则 autoexport+Batcher（:228-237）；propagator 由 `OTEL_PROPAGATORS` 经 autoprop 决定（:241）；service.name 缺省 `ai-gateway`（:192-194，注释解释为何硬编码字符串避免钉 semconv 版本）。**关键联动**：span 属性上限按约定自适应（:209-212）——OpenInference 每条消息发一条属性（`llm.input_messages.3.message.role` 式索引键），长对话轻易超过 OTEL 默认 128 条上限且**静默截断**，所以仅在需要的约定下把 AttributeCountLimit 提到 -1。

**约定选择 semconv.go**：`EnvTracingSemConv`（:25）；`semConvs` 表（:72-75）首项 openinference 为缺省，第二项 gen_ai；`newRecordersFromEnv`（:83）非法值报错而非回退（:97-98）——注释 :79-82 是全篇最好的一段工程哲学："一个跑几个月、发着没人看的约定、或 redaction 设置没人消费的网关，比拒绝启动更糟"。`recorderSet`（:32-61）按端点收纳 16 个 recorder+MCP 词汇+`unboundedAttributeCount` 标志；配套 `TestSemConvs_complete`（:28-31 注释）用测试逼每个约定补全字段——keyed 字面量缺字段仍编译通过，测试才是防线。两实现：newOpenInferenceRecorders（:106，一份 TraceConfig 共享 :104-105 注释防配置漂移；MCP 无 OpenInference 约定故保留 legacy 词汇 :126-128）与 newOTelGenAIRecorders（:136；消息进单一 JSON 属性故不需解除上限 :158-160）。

**泛型骨架 tracer.go**：`requestTracerImpl`（:28）持 tracer/propagator/recorder/headerAttributes/spanFactory；15 个端点各一个类型别名（:53-68，从 chatCompletion 到 countTokens/tokenize）；noop tracer 在构造期短路（:77-79）。核心方法 `StartSpanAndInjectHeaders`（:89）：从请求头 extract 父上下文（:96）→recorder.StartParams 定名（:97）→开 span→把新上下文 inject 回 carrier（:100，给上游续链）→RecordRequest→按 headerAttributes 映射把业务头（如 agent-session-id）转成 span 属性（:109-119）。

**span.go**：泛型 `span[RespT,ChunkT]` 把流式 chunk 先攒后发（RecordResponseChunk :26 只 append；EndSpan :44-48 统一 RecordResponseChunks 再 End——流中间不发事件）；RecordBackend 用接口断言探测"该约定是否记后端属性"（:37-41）；EndSpanOnError（:52）走 recorder 的错误路径。

**两套词汇表**：openinference.go 定义 OpenInference 键——span kind LLM/EMBEDDING/TOKEN_COUNTER（:21-27）、`llm.model_name`/`llm.invocation_parameters`（:40-43）、索引式消息属性构造器 InputMessageAttribute（:194）等；token_count 五键+细分 cache/reasoning/audio（:129-190）。otelgenai.go 定义官方键——`gen_ai.request.*`（:27-37）、`gen_ai.response.*`（:39-41）、usage 五键（:43-47）、四个消息属性**默认不记**（:49-54 注释：需显式 capture）。隐私面双通道：OpenInference 用 11 个 `OPENINFERENCE_HIDE_*` 环境变量（openinference/config.go:17-45），脱敏值 `__REDACTED__`（:66），`CapturesMessages`（:148）反馈给上限决策；GenAI 用单一 capture 开关（semconv.go:156）。env 解析助手 tracingenv/env.go（:17 泛型 getEnv 解析失败回落默认值）。

**MCP 双词汇**：mcpVocabulary（mcp.go:39）结构体九个函数字段——注释 :30-38 说明设计：两实现（mcpVocabularyLegacy/mcpVocabularyOTel）并排读，"约定不同的都在这，相同的（传播/采样/自定义属性）在 mcpTracer 共享"；字段永不为 nil（:37-38），mcpSpan 无需分支。

## 三、外部连接

- **extproc**：processor_impl.go:321 在 router 侧开 span（01 篇同一位置）；装配入口 mainlib/main.go:288（NewTracingFromEnv 拿 spanRequestHeaderAttributes）。
- **translator**：SpanT 泛型参数即 tracingapi 各端点 span（02 篇），翻译器回译时顺手 RecordResponseChunk。
- **metrics**：tokenUsage 同源喂指标（06 篇），trace 与 metric 共享账本。
- **测试资产**：tests/internal/testopeninference 用外部参考实现预录 span 做对偶断言（12 篇）。

## 四、数据流

一次流式 chat 请求：客户端带 traceparent 进来 → router filter 解析 body 后 `StartSpanAndInjectHeaders`：extract 出父 span 上下文、开 `chat <model>` span、inject 出口头、RecordRequest 记输入消息（按约定决定记不记内容）→ 翻译器每收到一个回译 chunk 调 RecordResponseChunk（只攒）→ 流结束 EndSpan：一次性记全部输出 chunk+usage → BatchSpanProcessor 批量 OTLP 导出。MCP 支线：mcpproxy 走独立 MCPTracer，词汇表按约定切换但传播链共享。

## 五、设计决策

1. **非法值拒启动**（semconv.go:79-82）：观测配置的错误是慢性病，静默回退会把问题藏到看板空无一物那天。
2. **属性上限按约定自适应**（tracing.go:207-212 注释）：截断是静默的，只有"知道要发 N 条属性"的一方才有资格解除上限。
3. **词汇表钉死在测试里**：otelgenai.go:14-17 包注释明言"依赖升级不得悄悄改名破坏看板"，coverage/semconv_vocabulary 测试对着规范钉每个键。
4. **chunk 缓冲到 End**（span.go:44）：流式事件半路写会导致属性顺序不稳定，聚合一次性写既有确定性又少批次。
5. **MCP 不硬塞约定**：OpenInference 没有 MCP 规范，legacy 词汇原样保留（semconv.go:126-128 注释）——双约定的边界诚实止步于规范存在处。

## 六、新人提示

加新端点四步：tracingapi 加 Tracer/Recorder 接口与 SpanT 别名→tracer.go/span.go 补类型别名与构造器→recorderSet 加字段（TestSemConvs_complete 会逼两约定都实现）→两包各写 recorder。测试：tracing_test.go/semconv_test.go 单测、tests/data-plane 端到端断言。坑两处：span 属性莫名缺失先查是否撞 128 上限（换 OpenInference 或减少消息）；console exporter 是同步写（tracing.go:216-225），压测会拖慢流式路径，仅调试用。
