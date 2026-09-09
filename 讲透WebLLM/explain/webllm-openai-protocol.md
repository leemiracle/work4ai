# webllm-openai-protocol.md — src/openai_api_protocols/ 精讲：OpenAI 兼容协议层

## 角色定位

`src/openai_api_protocols/`（四文件共 ~1875 行）是 WebLLM 的 **API 表面伪装层**：把 openai-node（OpenAI 官方 TS SDK）的请求/响应类型逐字移植过来，使 WebLLM 的调用代码与调云端 OpenAI 的代码长得一模一样——`engine.chat.completions.create({...})` 换个 engine 对象即完成"云→端"迁移。它分内两职责：①类型定义（请求、响应、消息、tool call 等完整结构）；②请求校验（每个协议一个 `postInitAndCheckFields`，在转发给引擎前拦截不支持的字段与非法组合，以 69 个语义化错误类报错）。四个文件：`chat_completion.ts`（1228 行，主协议）、`completion.ts`（381 行，旧版文本补全）、`embedding.ts`（198 行，句向量）、`index.ts`（68 行 barrel，43 个导出）。

## 内部结构

**门面类对齐 openai-node 形态**：`Chat` 持有 engine 引用并暴露 `completions` 子对象；`Completions.create(request)` 按 stream 与否声明重载（非流式返回 `Promise<ChatCompletion>`，流式返回 `AsyncIterable<ChatCompletionChunk>`），方法体一行转发 `engine.chatCompletion(request)`。completion.ts 的 `Completions` 与 embedding.ts 的 `Embeddings` 同构（转给 `engine.completion` / `engine.embedding`）。真正的校验与执行都在 engine 侧，协议层保持"薄"。这层薄是有意的：所有类型同时被 web_worker.ts 用作跨线程消息的载荷类型——协议即线格式，若在门面里塞逻辑，worker 序列化边界就会被破坏。

**chat_completion.ts 类型面**：`ChatCompletionRequestBase` 覆盖 messages/stream/stream_options/n/frequency_penalty/presence_penalty/repetition_penalty/max_tokens/stop/temperature/top_p/logit_bias/logprobs/top_logprobs/seed/tool_choice/tools/response_format（`model` 字段被刻意移除——模型由 `CreateMLCEngine(modelId)` 预先指定，这是与 OpenAI 的最大语义差异，注释明示）。响应类型 `ChatCompletion`/`ChatCompletionChunk` 连 `system_fingerprint`（标注 not supported）这类字段都保留，降低类型不匹配摩擦。消息类型族（System/User/Assistant/ToolMessageParam、ContentPart 的 text/image_url、ToolCall 的 id/function/type）完整复刻，图像 URL 支持 http 与 `data:image` base64 前缀。`ResponseFormat` 四形态：`text`、`json_object`（可带 schema，走 xgrammar JSON schema 编译）、`grammar`（EBNF 字符串）、`structural_tag`（xgrammar StructuralTagLike）——后三者是 WebLLM 超集能力。

**postInitAndCheckFields（188 行，八组规则）**：①不支持字段检查（当前清单为空——全支持，但机制保留给未来）；②消息内容校验：非字符串 content 仅 VLM 可用（`UserMessageContentErrorForNonVLM`）、image_url 不支持 detail、URL 必须 http/data:image 前缀、每条消息至多一个 text part；③system 消息必须在首位、最后一条消息必须来自 user 或 tool；④stream 与 n>1 互斥（`StreamingCountError`，单序列限制）；⑤seed 必须整数；⑥response_format 三种扩展形态的字段-类型交叉校验（schema 只属于 json_object 等）；⑦function calling：模型必须在 `functionCallingModelIds` 白名单（五个 Hermes 型号），且对 Hermes-2-Pro/Hermes-3 **硬编码注入**——自动设 `response_format = json_object + officialHermes2FunctionCallSchemaArray`、把 tools 塞进专用系统提示词并 unshift 到消息头（用户自带 system 消息或 response_format 则抛错）；⑧stream_options 依赖 stream=true。该函数还会**就地改写请求**（注入消息/格式），不只是校验。

**completion.ts**：`CompletionCreateParams` 以 prompt/echo/max_tokens 等为主，校验拒绝 tools/logprobs 细项等不支持字段与非法整数参数；**embedding.ts**：`EmbeddingCreateParams.input` 四形态（string / Array&lt;string&gt; / Array&lt;number&gt; / Array&lt;Array&lt;number&gt;&gt;），不支持清单 `["dimensions", "user"]` 与 base64 编码，空输入逐层抛 `EmbeddingInputEmptyError`；响应 `CreateEmbeddingResponse` 的 usage 附 WebLLM 特有 `extra.prefill_tokens_per_s`。

## 外部连接

上游被 engine.ts 在每次请求前调用（`API.postInitAndCheckFieldsChatCompletion(request, modelId, modelType)` 等三个入口）；类型被 web_worker.ts（请求跨线程就是要序列化这些类型）、message.ts、conversation.ts（`getConversationFromChatCompletionRequest` 把 messages 转成 Conversation）、config.ts（ResponseFormat 进 GenerationConfig）消费；`tests/openai_*.test.ts` 三件套专项校验。它自己反向依赖 config.ts（白名单/枚举）、support.ts（Hermes schema 与系统提示词）、error.ts（十余个错误类）。

## 数据流

用户 `create(request)` → 门面转发 engine.chatCompletion → engine 取模型三元组后**先调 postInitAndCheckFields**（拦截或就地改写：Hermes 注入系统消息 + JSON schema）→ 组装 GenerationConfig（含从 extra_body 提取的 enable_thinking/enable_latency_breakdown）→ 进入生成循环 → 流式产出 ChatCompletionChunk（engine 的 asyncGenerate 组装 delta/finish_reason/usage）或非流式产出 ChatCompletion（choices + usage.extra 性能指标）。协议类型贯穿始终——worker 模式下请求对象整体 postMessage，类型即线协议；流式响应则反向逐 chunk 回流，每个 chunk 都携带同一 id 与 created 时间戳，UI 靠它们聚合同一次请求的增量。

## 设计决策

1. **逐字移植而非重设计 openai-node 类型**（Apache-2.0 头部声明）：迁移成本压到零，连未支持字段也保留类型并标注 note，用运行时校验兜底——TS 类型挡不住 JSON 传参，校验函数才是真闸门。
2. **校验与改写合一**：Hermes function calling 的硬编码（schema 注入 + 系统提示拼接）放在协议层而非引擎层，因为它本质是"请求的模板变换"，与采样无关。
3. **移除 model 字段**：模型选择是重操作（GB 级加载），与轻量请求解耦，避免 OpenAI 式"每请求换模型"语义在端侧爆炸。
4. **超集扩展走 response_format 而非新顶层字段**：grammar/structural_tag 借 OpenAI 的扩展位，SDK 用户无需学新协议。
5. **每协议独立 UnsupportedFields 清单**：能力边界显式可查（embedding 两个、completion 若干、chat 当前零个）。校验函数一律"拦截 + 就地改写"而非抛通用错误——69 个错误类按语义命名，用户拿到 `UnsupportedModelIdError` 时消息里直接列出白名单，排障不需要读源码。

## 新人提示

按 1228→381→198→68 的顺序读，chat_completion.ts 里类型与校验混排——先跳读 418-605 行的校验函数建立全景再回头看类型。写应用时把 `unsupported` 三张清单当兼容性矩阵。做 function calling 只需认准白名单五模型，且不要自己传 system 消息（Hermes 注入会冲突抛 `CustomSystemPromptError`）。响应里的 `usage.extra`（prefill_tokens_per_s 等）是性能调优先宝。配套精读：`webllm-engine.md`（校验之后的执行路径）与 `webllm-llm-chat.md`（response_format 如何变成 grammar bitmask）。
