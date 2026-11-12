# 07 · agent-llm：八类 Provider 的翻译引擎与虚拟模型路由

## 一、角色定位

在 agentgateway 的 16 层图谱中，本区域是第 11 层（index 10）"LLM Provider 翻译引擎"（575 节点），紧挨着它的第 12 层是 176 个金样本夹具库——这个相邻关系本身就是定位宣言：**翻译引擎的每一行行为都被金样本快照锁死**。

它的角色是 LLM 流量的 babel 鱼：客户端用任何一种方言（OpenAI Chat Completions、Anthropic Messages、OpenAI Responses、原生 Gemini generateContent）发请求，后端接任意一家 provider，网关在中间完成请求体、响应体、SSE 流、错误体四个维度的方言互译。与第 02 篇讲的控制面 translator（K8s→xDS）不同，这里翻译的是**数据面热路径上的每一个 token**，所以这套代码同时承担三件事：翻译、策略执行（guardrail/限流/token 预算都要先"看懂"请求）、可观测性（统一 usage 口径）。

一个必须先纠正的坐标：任务书把"3579 行 mod.rs"归给 agent-llm crate，实际上它属于**数据面** `crates/agentgateway/src/llm/mod.rs`（3579 行，翻译管线主循环）；agent-llm crate（`crates/llm/src/`）的主文件是 `lib.rs`（698 行），承载类型与翻译原语。两层的关系是：agent-llm 提供"字典和语法"（类型、SSE 解析器、conversion 函数、provider 端点常量），数据面 mod.rs 提供"调度员"（选格式、选路径、装配管线）。另外任务书说"六类 provider"，源码 `AIProvider` 枚举是**八种**：OpenAI/Gemini/Vertex/Anthropic/Bedrock/Azure/Copilot/Custom（`crates/agentgateway/src/llm/mod.rs:152`）；图谱摘要写"七类"同样数错。真正需要写翻译代码的**wire 方言**是五种 `ChatFormat`（`crates/llm/src/lib.rs:233`）：OpenAICompletions、OpenAIResponses、AnthropicMessages、BedrockConverse、VertexGemini——这是理解本 crate 的关键杠杆。

## 二、内部结构

### 2.1 agent-llm crate：类型层与解析原语

**lib.rs 是统一词汇表**。`RouteType`（lib.rs:152，14 个变体）描述 HTTP 端点语义（Completions/Messages/Responses/Embeddings/Realtime/Rerank/Decisions/SystemOne/GenerateContent 等），`InputFormat`（lib.rs:185，13 个变体）描述客户端 payload 方言，两者分离的注释理由写在 lib.rs:143-149：客户端打 `/v1/messages` 是 `RouteType::Messages`+`InputFormat::Messages`，但翻译后可能以 `RouteType::Completions` 发往上游。`ChatFormat`（lib.rs:233）则是上游 wire 方言，`tag()` 方法（lib.rs:242）把它映射到 model_catalog 的标签字符串。

**LLMRequest 不是完整中间表示**（lib.rs:255-268）：它只携带元数据——`input_format`、`request_model`、`provider`、`streaming`、采样参数 `LLMRequestParams`（lib.rs:315）、可选的规范化 prompt。真正的请求体翻译是 wire-to-wire 直转，不经过"解析成 IR 再序列化"的全量往返。附带的状态包 `ProviderState`（lib.rs:271-282）很精妙：Bedrock 翻译时生成的 tool 名字映射表、OpenAICompletions 的 namespace 映射，会在请求阶段挂到 LLMRequest 上，响应阶段取出来还原——请求与响应两侧翻译的"记忆"就存在这里。

计量口径的统一靠 `CacheTokenConvention`（lib.rs:285）：Anthropic/Bedrock 的 input_tokens **不含** cache 部分，OpenAI/Gemini **含**，`include_cache_tokens`（lib.rs:298-311）用 saturating_add 归一。`LLMResponse`（lib.rs:378）字段面覆盖 13 种 token 计数，`usage_lines`（lib.rs:423）专门承接 Anthropic `usage.iterations` 多 pass 计费；流式延迟观测用固定内存的 `TokenGapSummary`（lib.rs:464，14 桶+溢出桶，注释明言数组须与 telemetry 侧手工同步）。

**types/ 是 13 个 wire 协议模块**（types/mod.rs:1-13：bedrock/completions/count_tokens/decisions/detect/embeddings/gemini/messages/rerank/responses/systemone/vertex/vertex_gemini——任务书写 11 种，实为 13 个）。两个 trait 是翻译体系的接口面：`RequestType`（types/mod.rs:231）的 `to_llm_request`（types/mod.rs:242）负责"旁听"请求提取元数据，`visit_text_mut` 给 guardrail 提供改写钩子；`ResponseType`（types/mod.rs:90）反向对应。`ContentScope`（types/mod.rs:120）把可扫描内容分为 SystemPrompt/Messages/ToolOutput/ToolInput 四类，注释明示 ToolInput 的 mask 可能改坏 JSON。数据面 README（src/llm/README.md）钉版的解析策略是 **passthrough+rest**：所有类型带 `#[serde(flatten)] rest: Value` 吞下未知字段，仅在需要互译时才升级到 `typed` 子类型——这是兼容性的第一道防线。`ChatRequest`（types/mod.rs:21-27）是四种已解析 chat 方言的枚举聚合。思考预算的跨方言映射也在这一层：`thinking_budget_for_reasoning_effort`（types/mod.rs:29-42）把 OpenAI effort 档位折算成 token 数（Low=1024…Max=16384）。

**parse/ 是流式四类管线**，全部架在 `TransformedBody` 这个通用底座上（parse/transform.rs:82 的 `parser()` 组合 Decoder×Encoder×handler，transform.rs:107 实现 `HttpBody::poll_frame`，逐帧 decode→handler→encode，L52 的 `terminal_error_frame` 保证出错时已编码数据先落地）。在此之上：`json_passthrough`（parse/sse.rs:62）只旁听不改写（Detect/遥测用）；`json_transform`（sse.rs:102）一帧进一帧出（OpenAI↔Anthropic 流式互译的主力）；`json_transform_multi`（sse.rs:141）一帧进多帧出且可带 event name（转 Anthropic 事件流必需）。两个工程细节值得注意：`DoneTolerantSseDecoder`（sse.rs:38-60）容忍上游少发空行终止符的 `[DONE]`；`append_done_on_success`（sse.rs:14）为非 SSE 上游补写 `[DONE]`。Bedrock 不走 SSE 而走 AWS Event Stream 二进制编码，由 aws_sse.rs（334 行）单独解码。

**conversion/ 是互译矩阵的实现体**：messages.rs（Anthropic 方言，1121 行）、completions.rs（1452 行）、responses.rs（1699 行）、bedrock.rs（4658 行最大）、vertex_gemini.rs（1664 行），每个模块内按 `from_completions`/`from_messages`/`from_responses` 子模块组织——**每家目标方言只需实现"从 N 种源到我这"的方向**。mod.rs 的 `ProviderUsage`/`ResponseWithProviderUsage`（conversion/mod.rs:13/22）是个包装 trait：翻译响应时先抄下 provider 侧 usage，再包住翻译后的对象，防止 usage 口径在翻译中被吞（mod.rs:28-40 显式回填）。零散但关键的互译助手：`tool_arguments_to_input`（mod.rs:86，空参数串补 `{}`、坏 JSON 原样透传）、`supports_reasoning_effort`（mod.rs:63，gpt-3.5/gpt-4/chatgpt-4o 前缀的老模型拒绝 reasoning 参数）、`supports_prompt_cache_breakpoint`（mod.rs:69，版本 ≥5.6 才支持）。

**provider 配置文件**都很薄（host/path/认证常量）：anthropic.rs:17/24/28（api.anthropic.com、版本 2023-06-01、`path_suffix` 按 RouteType 出 `/messages` 或 `/messages/count_tokens`）、openai.rs:67（其余路由一律落 `/chat/completions`）、gemini.rs:18/25、copilot.rs:97。真正有逻辑的判定函数：bedrock.rs:58 的 `is_anthropic_model`（模型名含 "anthropic.claude"）、vertex.rs:39、copilot.rs:20——同名函数在三家 provider 各自实现，因为三家的 Claude 命名法不同。tokenizer.rs:14 的 `num_tokens` 是请求侧预算的估算器：o200k_base 计数，Claude 乘 1.3、Claude 4.7+ 乘 1.6，带工具再加 600（隐藏系统提示），注释里的数字全部来自实测。model_catalog.rs:6-27 定义目录标签（runtime/mantle 端点标签、五种格式标签、adaptive/legacy thinking 标签），目录以只读 handle 显式传参进 agent-llm，避免反向依赖。

### 2.2 数据面 mod.rs：调度员与四维翻译

`AIBackend`（mod.rs:81）管理一个 provider 端点集合，`select_provider`（mod.rs:100）用两次随机取优（power-of-two-choices，注释 L114-115 明言允许重复采样防饿死）挑端点；多个优先级组自动开启健康驱逐（mod.rs:90-93）。

心脏是 `CHAT_TRANSLATIONS` 互译矩阵（mod.rs:374-403）：13 条 `ChatTranslation{input, output}` 规则按**成本优先**排序——直通规则在最前（Responses→OpenAIResponses、Gemini→VertexGemini、同方言直通），然后是跨方言转换（Completions↔Messages↔Responses→各家），两处 `// Missing:` 注释（L389 Bedrock→Bedrock、L401 Responses→Messages）诚实标注未实现的路径。`chat_translation`（mod.rs:1121）拿 `supported_chat_formats`（mod.rs:1052）与该表求交，取第一条命中——**每个客户端方言 × 每家 provider 的组合由表驱动选定**，选不中就报 `UnsupportedConversion`。

选定格式后，四个维度的翻译都是 `output ChatFormat × input InputFormat` 的二维 match：`render_request`（mod.rs:577）分派到五个 render 函数（mod.rs:405/443/477/495/513 分别对应 Completions/Responses/Messages/VertexGemini/BedrockConverse）；`render_response`（mod.rs:603）负责缓冲响应的回译；`stream`（mod.rs:682）给流式响应装翻译管线（各 conversion 模块的 `translate_stream`）；`error`（mod.rs:816）连上游错误体都按 `ChatErrorFormat`（mod.rs:311，OpenAI/Google/Anthropic/Bedrock 四种）翻译回客户端方言。Bedrock 的 render（mod.rs:513-556）最能体现"请求侧状态供响应侧还原"：翻译时产出的 tool_name_map/namespaces 打包进 `ProviderState::Bedrock`（mod.rs:547）。

`cache_convention_for`（mod.rs:268-309）是口径侦探：不看 provider 名而看**实际 wire 格式**——因为 Vertex 也能服务 Anthropic 模型（Vertex 判定 is_anthropic_model 后走 AnthropicMessages，mod.rs:296），Bedrock 的 Mantle 端点还能说 OpenAI 话（路径后缀探测，mod.rs:287-290）。

### 2.3 model_router：虚拟模型

`ModelRouter`（model_router.rs:215）持有两类路由对象：具体模型 `ModelRoute`（L21，带 visibility Public/Internal——Internal 模型只能被虚拟模型引用不能直连，L48）和虚拟模型 `VirtualModelRoute`（L174）。虚拟模型四种路由模式（`VirtualModelRouting`，L183）：**Weighted** 加权随机、**Failover** 直接绑一个后端引用、**Conditional** 按 CEL 表达式选目标、**Callout** 调外部 HTTP 服务动态选模型。`resolve`（L295）是总入口：剥 path_prefix→识别端点分类→提取请求模型名→先查虚拟模型表，命中走 `resolve_virtual_model`（L486），否则查具体模型。Callout 模式的完整实现在 router_callout.rs：`VirtualModelCallout`（L26）用 CEL 表达式构造请求头/体，从响应 JSON 里取 `model` 字段选目标、`transformation` 还能反向改写请求 payload；失败模式 `FailClosed`（默认拒绝）或 `Fallback`（降级到指定模型）（L62）；带 `ExpiringCache` 做 session 粘性缓存。

## 三、外部连接

**向上（客户端侧）**：数据面 HTTP 过滤器链。`proxy/httpproxy.rs:95` 把 `Backend::AI` 与 `Backend::LLMRouter` 归类为 `RequestProtocol::AI`；httpproxy.rs:2579 调 `router.resolve()` 拿到 `ResolvedBackend` 后，才进入本模块的请求翻译。模型路由器自己维护一套端点识别表 `SERVING_ENDPOINTS`（model_router.rs:68 起，16 个精确路径+Vertex/Gemini 正则），与 HTTPRoute 的后缀匹配并存。

**向下（provider 侧）**：八家 provider 的连接目标由 `default_connector_target`（mod.rs:1225）给出（如 OpenAI→api.openai.com:443，Bedrock 按模型重解端点）；认证由 `default_connector_policies`（mod.rs:1182）装配——Copilot 专用 token、Vertex 走 GCP、Bedrock 走 AWS SigV4（带凭证缓存与 assume-role 缓存，mod.rs:165-172）、Azure 走 AAD。`setup_request`（mod.rs:1243）三步定型上游请求：`set_default_path`（Bedrock 按 Runtime/Mantle 端点出 `/model/{model}/converse[-stream]`，bedrock.rs:191-192，或 Mantle 的 OpenAI 兼容路径）→`set_default_authority`→`set_required_fields`（如 anthropic-version 缺省注入，mod.rs:56）。

**横向（数据面策略层）**：`crates/agentgateway/src/llm/policy/` 挂在翻译管线上——mod.rs 的 `prepare_request`（mod.rs:2289）在翻译前执行 prompt enrichment 与 prompt guard webhook（guardrail 拒绝会短路成 `PreparedRequest::GuardrailRejected`）；流式路径上 guardrail 在**翻译后**的 SSE 上运行（process_streaming L3128 注释明言：先跑会静默弄崩 Bedrock，因其二进制流不是 SSE）。policy/ 目录含 bedrock_guardrails、google_model_armor、azure_content_safety、moderation 四家托管 guardrail 适配与 pii/ 正则识别器套件（信用卡/邮箱/电话/SSN 等 9 个 recognizer）。token 预算闭环由 `amend_tokens`（mod.rs:3500）+`AmendOnDrop`（mod.rs:3524，Drop impl 在 L3575 兜底保证上报）完成：请求时先按估算扣，响应后按真实 usage 差额修正。

**验证侧（golden_tests）**：`crates/llm/src/golden_tests.rs`（2027 行）+ `src/tests/` 下 173 个 JSON fixture 与 371 个 insta 快照。三个测试入口对齐三个翻译维度：`test_request`（golden_tests.rs:54，翻译请求+提取 LLMRequest 一起快照）、`test_response`（L746，翻译响应+to_llm_response）、`test_streaming`（L810，把 `.bin` 原始字节流灌进 translate_stream 逐帧断言）。fixture 按 `requests/{completions,messages,responses,gemini,...}/{场景}.json` 组织，快照名 `{场景}.{provider}.snap`（golden_tests.rs:19-27），provider 名单（L37-56）覆盖 anthropic/bedrock-titan/bedrock-nova/bedrock-cohere/vertex-gemini/gemini-native 等十余种变体。`namespace_tools_round_trip`（L1106 起）展示了最严格的用法：同一 namespace-tools 请求分别走 Bedrock 与 OpenAICompat 两条翻译路径，响应都还原成 Responses 方言后对拍。

## 四、数据流：一个 OpenAI 请求打到 Anthropic 后端的完整回环

以"客户端发 OpenAI `/v1/chat/completions`（stream=true），路由目标选了 Anthropic provider"为例：

1. **模型解析**：httpproxy 拿到请求，`ModelRouter::resolve`（model_router.rs:295）从 body 提取 `model` 字段（模型名在 Body/Multipart/Path 三种位置，L240-246），先匹配虚拟模型（若是 Weighted/Conditional/Callout 会在此改写目标），否则定位到具体 ModelRoute，返回 ResolvedBackend；原始模型名存进 `OriginalModel` 扩展供日志（L193）。
2. **方言选定**：数据面按路由类型解析出 `InputFormat::Completions`，`chat_translation`（mod.rs:1121）查 CHAT_TRANSLATIONS 表——Anthropic 的 `supported_chat_formats` 只回 `[AnthropicMessages]`，命中规则 `chat(Completions, AnthropicMessages)`（mod.rs:392）。
3. **策略前置**：`prepare_request`（mod.rs:2289）先跑 prompt enrichment、prompt guard webhook（webhook 有权直接改写或拒绝），再 `to_llm_request`（types/mod.rs:242）提取 LLMRequest 元数据（含 tokenize=true 时用 o200k 估算 input_tokens），`cache_convention_for`（mod.rs:268）按 AnthropicMessages 判定 `InputExcludesCache`。
4. **请求翻译**：`render_request`→`render_anthropic_messages`（mod.rs:477）→`conversion::messages::from_completions::translate`（messages.rs:253）。内部先 `json::convert` 把 passthrough 类型升级到 typed（messages.rs:256），然后逐块翻译：system/developer 消息收进 Anthropic 顶层 `system` 数组、user 内容的 image_url 解析成 base64/url source（messages.rs:110-125）、assistant 的 reasoning_signature 有值则重放 Thinking 块且必须携带原签名（messages.rs:143-149 注释：无签名块会被上游拒收）、tool_calls 的 arguments 字符串经 `tool_arguments_to_input`（conversion/mod.rs:86）转 input 对象。思考预算约束 `cap_thinking_budget_to_max_tokens`（messages.rs:14）保证 budget≥1024 且 < max_tokens（Anthropic 硬性边界）。
5. **上游装配**：`setup_request`（mod.rs:1243）把路径设为 `/v1/messages`（anthropic.rs:28-33），注入缺省 `anthropic-version: 2023-06-01`（mod.rs:56 + anthropic.rs:24），认证头按 BackendAuth 装配，body 替换为翻译后的字节。
6. **流式回译**：响应 200 且 SSE，`process_streaming`（mod.rs:3057）先解压（L3101 注释：SSE 解析器只吃明文）、`normalize_sse_response_headers`（mod.rs:70）改写 content-type，然后 `stream()`（mod.rs:682）命中 `AnthropicMessages × Completions` 分支，装上 `conversion::messages::from_completions::translate_stream`（messages.rs:664）。管线核心是 `parse::sse::json_transform`（sse.rs:102）：每帧 `message_start` 事件只记账不输出（messages.rs:719-737，role 憋到下一个 chunk 才随 delta 发出，注释解释了 OpenAI chunk 无顶层 role 字段）；`content_block_start` 的 tool_use 生成带 index 的 tool_calls chunk（messages.rs:745-780）；`input_json_delta` 增量拼 arguments；`content_block_stop` 时若一个参数都没发过则合成 `{}`（OngoingToolCall.emitted_arguments，messages.rs:668-672）；usage 在 message_start/message_delta 累计，经 `StreamingUsageGuard` 回写 LLMInfo。
7. **收尾计量**：流结束（或连接断开触发 Drop，mod.rs:3575），`AmendOnDrop::report_usage` 调 `amend_tokens`（mod.rs:3500）修正限流预算；guardrail 若配置了流式扫描，则在翻译后的 OpenAI 形 chunk 上跑（mod.rs:3128）。

非流式时走 `process_response`（mod.rs:2530）的缓冲分支：`buffer_response` 解压整包（mod.rs:2711），`render_response`（mod.rs:603）命中 `AnthropicMessages × Completions`→`translate_response`（messages.rs:510）把 content blocks 还原成 OpenAI choices（多 text 块拼接、thinking 块 join 成 reasoning_content 且**仅单一签名块时**保留签名，messages.rs:565-575），usage 由 ResponseWithProviderUsage 包装保真。

## 五、设计决策

**wire-to-wire 而非 canonical IR**。最省 token 的设计：请求体不进"统一中间表示"再序列化，而是 typed 方言两两直转。收益是 passthrough 请求零翻译开销（同方言直通规则排在 CHAT_TRANSLATIONS 最前，mod.rs:380-381），代价是互译函数要处理彼此的字段怪癖（如签名块重放、空参数补 `{}`）。`LLMRequest` 只服务策略与遥测，这让"翻译"与"治理"解耦——guardrail 改的是 typed 请求而非 IR。

**N×2 互译矩阵而非 N×M**。conversion 模块按**目标方言**组织（每家一个 from_X 子模块集），加第六种方言只需写"5 个源→新方言"，存量 20 个方向零改动；CHAT_TRANSLATIONS 表（mod.rs:374）把方向选择外部成数据，`// Missing:` 注释（L389/L401）把已知缺口写进代码——这是罕见的"诚实清单"风格。Gemini 入站只在直通与转 Completions 时可用（render 函数里 Gemini→其他一律 UnsupportedConversion，mod.rs:432-435/489-491），注释明言"跨 provider 翻译 out of scope"。

**口径归一在边界处做**。CacheTokenConvention 按 wire 格式而非 provider 名判定（mod.rs:262-267 注释直接给了理由：Vertex 可携带 Anthropic 语义）；usage 用 ProviderUsage 包装防翻译吞没（conversion/mod.rs:21 注释"Keep provider token counts for accounting"）。这类"注释即设计文档"的密度在 bedrock.rs:137 也有（"all chat runtime models seem to support converse"——工程判断的出处都留了痕）。

**虚拟模型放在数据面 router 而非控制面**（推断，无直接注释）：四种路由模式都需要请求期上下文（Weighted 要随机、Conditional 要 CEL 求值、Callout 要拿请求体），而 model_router.rs 与 httpproxy 同进程同请求路径，`OriginalModel`（L193）扩展传递成本为零。Failover 模式直接返回 `RouteBackendReference`（L505-512）复用 AIBackend 的优先级组+健康驱逐（mod.rs:89-93），没有另造一套故障转移机制。

**Bedrock 双端点是整个体系最深的特判**：Runtime（Converse 专用，二进制 Event Stream）与 Mantle（OpenAI 兼容层）按模型目录标签选择（bedrock.rs:135-160），这解释了为什么 parse/ 要有 aws_sse.rs、为什么流式 guardrail 必须在翻译后运行（mod.rs:3128 注释）、为什么 cache_convention 要嗅探路径后缀（mod.rs:287）。

**金样本即契约**：173 fixture×371 快照（insta）锁死全部翻译方向，改任何 conversion 函数都会在快照 diff 里现形。快照把"翻译产物+LLMRequest 元数据"打包断言（golden_tests.rs:83-89），连错误路径（stream-error/stream-context_window 等 fixture，golden_tests.rs:1097 起）都有基线。

## 六、新人提示

**加一家 provider 的最小路径**（源码归纳）：①若它说五种方言之一，只需在 `crates/llm/src/` 加一个薄配置文件（抄 anthropic.rs:28 的 `path_suffix` 模式），②在数据面 `AIProvider` 枚举（mod.rs:152）加变体并接好 `supported_chat_formats`（mod.rs:1052）——CHAT_TRANSLATIONS 表会自动为它匹配现成翻译函数，③`default_connector_target/policies`（mod.rs:1225/1182）给连接与认证，④Copilot 式特判参考 copilot.rs:20 的模型名嗅探。只有当它发明第六种方言时才需要动 conversion/。自建 OpenAI 兼容端点更简单：直接用 `custom::Provider` 的 `formats` 声明（custom.rs:19-20）。

**调 golden 快照**：`cargo insta` 工作流；新增翻译行为先写 fixture（`src/tests/requests/{方言}/{场景}.json`）再在 golden_tests.rs 的用例矩阵里挂上 provider 名；审快照 diff 时重点看 `parsed`（LLMRequest）字段——它暴露元数据提取回归。流式场景存 `.bin` 原始字节（含分帧），`test_streaming`（L810）会真实过 TransformedBody 管线。

**坑位清单**（全部有源码出处）：①Anthropic 思考预算硬边界 1024 且必须小于 max_tokens（messages.rs:9-23），越界直接被上游拒；②`[DONE]` 的两种方言差异——OpenAI 要发、Anthropic 没有，翻译层靠 append_done_on_success（sse.rs:14）与 DoneTolerant 解码器（sse.rs:38）双向兜底；③thinking 块签名只在"恰一个签名块"时能保住（messages.rs:571-575），多块合并必丢签名；④Bedrock 工具名会被 sanitize，请求侧必须把原始名存进 tool_name_map（mod.rs:3438）否则响应侧对不回；⑤token 估算对 Claude 有 1.3/1.6 乘数与 +600 工具开销（tokenizer.rs:14-40），预算测试别用 OpenAI 数字硬套；⑥guardrail 千万别插在翻译前（mod.rs:3128 用血泪注释钉版）；⑦`INTER_CHUNK_LATENCY_BUCKETS` 与 telemetry 侧是手工同步的两份拷贝（lib.rs:452-454 注释），改桶边界要改两处。

**读码路线**：lib.rs 词汇表 → mod.rs 的 CHAT_TRANSLATIONS+四个 render/translate 分派 → 挑一条 conversion（推荐 messages.rs 的 from_completions，它同时覆盖文本/图片/工具/思考四种块型）→ 用 golden 快照对照读，`tests/requests/messages/` 下每个场景文件都是对应翻译分支的活文档。

---
*锚点统计：全文行号锚 60+ 处，全部于 2026-10-24 从源码 sed/grep 核实。任务书勘误：①"mod.rs 3579 行"属数据面 `crates/agentgateway/src/llm/mod.rs` 而非 agent-llm crate；②provider 实为 8 种（AIProvider 枚举）而非 6 种，图谱摘要"七类"亦误；③types/ 为 13 个 wire 模块而非 11 种。*
