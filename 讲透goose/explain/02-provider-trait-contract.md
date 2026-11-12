# 02 · providers/base.rs + api_client.rs：Provider trait 契约——一切模型的统一抽象

> 源码基线：`crates/goose/src/providers/base.rs`（1130 行）+ `crates/goose/src/providers/api_client.rs`（702 行）。所有行号锚 `文件:行` 均从源码 sed/grep 逐一核实。

## 角色定位：16 层架构里的"模型出口"

在 goose 的知识图谱 16 层分层中，本层名为 **LLM Provider 适配层**（图谱该层节点 130 个），位于 agent 执行引擎之下、外部模型世界之上。它回答一个问题：**agent 循环如何对 30+ 家完全异构的模型服务（REST API、CLI 子进程、本地推理）保持同一张面孔？**

答案浓缩在一个 trait 上：`Provider`（base.rs:460，doc 注释写明 "Base trait for AI providers (OpenAI, Anthropic, etc)"）。上游消费者是 agent.rs 的 reply 循环——`agent.rs:1774` 调用 `Self::stream_response_from_provider(...)` 拿到一条 `MessageStream`，随后在 `while let Some(next) = stream.next().await` 循环里逐块消费。中间经手 `reply_parts.rs:252` 的 `stream_response_from_provider`：它先过滤 agent 可见消息（`reply_parts.rs:264` 的 `is_agent_visible()`），再真正调 `provider.stream(...)`（`reply_parts.rs:285-286`）。也就是说，agent 层从头到尾只见 `Arc<dyn Provider>`（图谱显示 104 个文件节点 import base.rs，其中 agent.rs/reply_parts.rs/orchestrator.rs/summarize.rs/permission_judge.rs 等是主力消费方）。

本层内部再切两半：

- **base.rs 是契约层**——定义 `Provider`/`ProviderDef` 两个 trait、`ProviderMetadata`（base.rs:195）/`ModelInfo`（base.rs:102）/`ConfigKey`（base.rs:293）三组元数据类型，以及流聚合工具 `collect_stream`（base.rs:817）。它不含任何 HTTP 代码。
- **api_client.rs 是传输层**——`ApiClient`（api_client.rs:18）封装 reqwest，负责 URL 拼接、认证头注入、mTLS 证书、超时。所有走 HTTP 的 provider 都拿它当底座。

一个常被忽视的全局件：`CURRENT_MODEL: Lazy<Mutex<Option<String>>>`（base.rs:34），doc 注释直言用途——"when a provider returns, it tells us the real model, not an alias"（provider 返回真实模型名而非别名时由此全局回传）。另一件是 `DEFAULT_PROVIDER_TIMEOUT_SECS = 600`（base.rs:13），注释解释"长推理可达数分钟，故放宽到 10 分钟"。

## 内部结构：一个必选方法 + 一族默认实现

### Provider trait 方法面（base.rs:460-802）

**必选项只有三个**：`get_name()`（base.rs:462）、`stream()`（base.rs:469）、`get_model_config()`（base.rs:532）。其中 `stream` 是唯一必选的推理入口，签名五个参数：`model_config / session_id / system / messages / tools`，返回 `Result<MessageStream, ProviderError>`。它上方有段值得抄录的工程注释（base.rs:464-468）：**禁止给 `stream` 加 `#[instrument]`**——telemetry span 由调用方（`complete` 和 `stream_response_from_provider`）统一创建，好让 `session.id` 只设一次而不是每个 provider 重复设。这是典型的"trait 默认实现与观测层职责分离"决策。

其余全部带默认实现，按职责分五组：

1. **推理便捷层**：`complete()`（base.rs:483）= `stream()` + `collect_stream()` 的组合默认实现，自带 `#[tracing::instrument]`；`complete_fast()`（base.rs:498）先试 fast 模型（base.rs:506 `use_fast_model()`），失败且 fast≠regular 时回退常规模型（base.rs:512-528）。
2. **模型目录**：`fetch_supported_models()`（base.rs:538，默认返回空 vec）、`fetch_model_info()`（base.rs:551）、`fetch_recommended_models()`（base.rs:560）——最后这个是最有料的默认实现：拉全量模型后经 canonical registry 过滤，只留文本输入（base.rs:585 `Modality::Text`）且支持工具调用（base.rs:590 `tool_call`，或用户开了 toolshim）的模型，按 release_date 降序排（base.rs:601-606），过滤后为空则退回全量（base.rs:613-617）。`map_to_canonical_model()`（base.rs:629）也在此组。
3. **能力开关**：`supports_embeddings()`（base.rs:644）、`manages_own_context()`（base.rs:652，注释点名 CLI 包装类 provider 如 Claude Code——它们自管上下文时 goose 侧跳过 tool-pair 摘要）、`supports_cache_control()`（base.rs:656）、`skip_canonical_filtering()`（base.rs:555）。
4. **会话辅助**：`generate_session_name()`（base.rs:711）是个完整的默认算法：取前 3 条用户消息（`MSG_COUNT_FOR_SESSION_NAME_GENERATION = 3`，base.rs:98）+ preprompt 上下文，用 `session_name.md` 模板渲染 system，走 `complete_fast` 生成短标题，再经 `strip_xml_tags`（base.rs:36）剥思维链标签、`extract_short_title`（base.rs:46）抽取引号内短语、`safe_truncate` 截到 100 字符。
5. **凭据与权限**：`configure_oauth()`（base.rs:775，默认返回"不支持"错误）、`refresh_credentials()`（base.rs:781）、`update_mode()`（base.rs:787）、`permission_routing()`（base.rs:791，默认 `Noop`）。

### MessageStream：部分文本 + 完整工具调用的流语义

`MessageStream` 是个别名（base.rs:807-809）：`Pin<Box<dyn Stream<Item = Result<(Option<Message>, Option<ProviderUsage>), ProviderError>> + Send>>`。base.rs:804-806 的 doc 注释钉死了协议语义：**流可以 yield 只含一个词的部分文本消息，但工具调用消息必须等拼接完整后才 yield 一次**。这个约定让 UI 层可以逐字渲染文本、又不必自己攒工具参数。配套工具两个：`stream_from_single_message()`（base.rs:811）把单条消息包装成一次性流（非流式 provider 的兜底）；`collect_stream()`（base.rs:817）做反向聚合，其中 base.rs:833 的注释 "Coalesce consecutive text blocks" 标出关键逻辑——连续 Text 块合并、非 Text 块（图片/工具调用）打断合并；usage 缺失时兜底为 `ProviderUsage::new("unknown", ...)`（base.rs:859）。

### ProviderDef：静态工厂 trait（base.rs:396-450）

与 `Provider` 并存的是 `ProviderDef`（base.rs:396），全部是关联类型上的静态方法：`metadata()`（base.rs:399）返回注册元数据，`from_env()`（base.rs:403）返回 `BoxFuture` 异步构造实例。`from_env_with_working_dir()`（base.rs:410）带默认实现直接转发 `from_env`，注释（base.rs:418-419）说明原因：**ACP 子进程 provider 必须覆写它以保留会话 cwd，非子进程 provider 不在乎 cwd 可用默认**。另有 inventory 三件套（base.rs:423/430/443）。

### ApiClient：认证注入与流式管道（api_client.rs）

`ApiClient` 七个字段（api_client.rs:18-26）：reqwest `Client`、host、`AuthMethod`、默认头、默认 query、timeout、`TlsConfig`。认证是五路枚举 `AuthMethod`（api_client.rs:28-38）：`NoAuth / BearerToken / ApiKey{header_name,key} / OAuth(OAuthConfig) / Custom(Box<dyn AuthProvider>)`。

注入点在 `send_request()`（api_client.rs:495）的 match（api_client.rs:511-525）：Bearer 拼 `Authorization: Bearer <token>`，ApiKey 写自定义头（Anthropic 的 `x-api-key` 就是这条路），OAuth 现场走 `get_oauth_token_async` 换 token，Custom 调 `AuthProvider::get_auth_header()`（api_client.rs:245-247，单方法 trait，返回 `(header_name, value)` 二元组）。**同一个方法里还做 session 头治理**：先 `headers.remove(SESSION_ID_HEADER)` 防伪造注入，再在 session_id 非空时写入（api_client.rs:501-506）；`request()` 的 doc（api_client.rs:384）明确"None 仅用于配置或会话前任务"。安全细节：`AuthMethod` 的 Debug 实现（api_client.rs:254-268）把所有 token/key 打成 `[hidden]`，防止日志泄漏。

构造与定制：`new()`（api_client.rs:286）默认挂 600 秒超时（api_client.rs:290 引用 base.rs:13 的常量）；`with_timeout()`（api_client.rs:294）在 build 前先读 `TlsConfig::from_config()`（api_client.rs:60）——从全局配置读 `GOOSE_CLIENT_CERT_PATH/GOOSE_CLIENT_KEY_PATH/GOOSE_CA_CERT_PATH` 三个键，cert 与 key 必须成对提供否则报错（api_client.rs:69-88）。native-tls 路径还有段教科书级的"why"注释（api_client.rs:172-190）：`Identity::from_pkcs8_pem` 只收 PKCS#8，而现实世界私钥有 PKCS#1/SEC1/PKCS#8 三种，故 `convert_key_to_pkcs8_pem()`（api_client.rs:192）做自动转换，免得用户手工跑 `openssl pkey`。

## 外部连接：26 个实现者 + 三个配套子系统

图谱边是硬证据：**26 个类向 `class:base.rs:Provider` 发出 `implements` 边**（knowledge-graph.json 实测），覆盖 anthropic/openai/google/openrouter/ollama/bedrock/snowflake/xai_oauth 等 REST 系，以及 claude_code/gemini_cli/cursor_agent/codex 等 CLI 子进程系。注册侧由 `init.rs:57` 的 `with_providers` 闭包完成——`registry.register::<AnthropicProvider>(true)` 逐个登记（bool 表示 preferred 与否），随后为 github_copilot/databricks 等八家挂 cleanup 函数。`provider_registry.rs` 的 `ProviderEntry` 把 `ProviderDef` 的静态方法擦除成三个 Arc 闭包（`ProviderConstructor` 类型别名，provider_registry.rs:11），`register::<F>`（provider_registry.rs:118）统一捕获 `F::from_env` / `from_env_with_working_dir` 并装箱 `Arc<dyn Provider>`；`create()` 工厂（init.rs:177）按名取 entry 再调构造器。`normalize_model_config()`（provider_registry.rs:60）在构造前给 ModelConfig 回填 canonical 上下文限额。

三处衔接值得点名：

1. **格式翻译器 formats/**——`providers/formats/mod.rs` 声明 anthropic/google/ollama/openai_responses/openrouter/snowflake 等 9 个族内翻译模块；共享的 OpenAI 格式翻译器在 `goose-providers/src/formats/openai.rs`：`create_request()`（1221 行）+ `ModelConfigParams`（1242 行）负责出站翻译，`response_to_message()`（559 行）/`response_to_streaming_message()`（893 行）负责入站。注意 `openai_compatible.rs` **不是**格式翻译器而是 provider（复用基座，openai_compatible.rs:29），它在 68 行调 `create_request` 组 payload。
2. **canonical 5063 模型目录**——`mod.rs:11-12` 显示 canonical 模块整体再导出自 `goose_providers` crate。registry.rs:8-9 用 `include_str!("data/canonical_models.json")` 把目录**编译进二进制**，`Lazy` 静态缓存；registry 结构是 `HashMap<(provider, model), CanonicalModel>`（registry.rs:28），`bundled()`（registry.rs:40）取全局单例、`get()`（registry.rs:82）按键查。JSON 实测 5063 条模型记录；`CanonicalModel`（model.rs:66）携带 modalities/tool_call/reasoning/release_date/Pricing/Limit 全套元数据。数据来源是 canonical/README.md 钉版的：`cargo run --bin build_canonical_models` 从 **OpenRouter API** 拉取生成。
3. **重试子系统 retry.rs**——`should_retry()`（retry.rs:84）按错误类型决定可否重试，`ProviderRetry` trait（retry.rs:139）给 provider 提供 `with_retry` 包装。

## 数据流：一次 stream 调用的完整旅程

以 Anthropic 为例（HTTP 系标准路径），六步：

1. **agent 侧预处理**（reply_parts.rs:252）：过滤 `is_agent_visible` 消息 → toolshim 开关时把工具定义折进 system prompt → 调 `provider.stream()`（reply_parts.rs:285）。stream 创建失败时**不直接返回 Err**，而是包成一条立即 yield 错误的流（reply_parts.rs:297-304，注释明言这样 agent.rs 既有的错误处理逻辑能统一接住）。
2. **出站格式翻译**（anthropic.rs:336-347）：`create_request_with_options` 组 Anthropic 格式 payload，随后手工插入 `"stream": true`。
3. **HTTP 发送 + 重试**（anthropic.rs:359-371）：`api_client.request(Some(session_id), "v1/messages")`（anthropic.rs:361）建链式 builder → 逐个挂条件头 → `response_post(&payload)`（anthropic.rs:366）→ `handle_status` 检查状态码（anthropic.rs:367），整包 `with_retry` 包住（anthropic.rs:360）。认证头此刻由 send_request 的 match 注入（api_client.rs:511），`build_url`（api_client.rs:424）负责 host/path 拼接与斜杠规整。
4. **字节流转消息流**（anthropic.rs:373-385）：`response.bytes_stream()`（373 行）→ `StreamReader` 转 AsyncRead（376 行）→ `FramedRead + LinesCodec` 按行切 SSE（377 行）→ `response_to_streaming_message(framed)`（380 行）解析每行 `data:` 前缀。openai_compatible.rs:187-208 是同构实现：`stream_openai_compat` 里 try_stream! 宏逐块 yield `(message, usage)`，错误经 `downcast::<ProviderError>` 还原类型（openai_compatible.rs:202-203）。
5. **SSE 语义还原**（formats/openai.rs:893 起）：处理 `[DONE]` 终止符（918 行）、累积跨块的 tool_call 参数、reasoning_content 与内联 `<think>` 去重（`pending_inline_thinking` 缓冲，防结构化推理后到造成重复）。
6. **消费与聚合**：agent.rs:1774 起 `stream.next().await` 逐块消费——usage 块更新会话计量、message 块经 `categorize_tools` 分类前后端工具后 `yield AgentEvent::Message`。若上游要的是完整消息（如 `complete` 默认实现），`collect_stream`（base.rs:817）按 base.rs:833 的合并规则聚拢。非流式 provider 走另一岔路：openai_compatible.rs:154-174 直接 `response.json()` 解析整包，最后 `stream_from_single_message`（openai_compatible.rs:173 → base.rs:811）包装成一次性流——**对外协议不变，这是"流"作为统一货币的价值**。

每个 provider 还全程携带 `RequestLog`（anthropic.rs:357 `RequestLog::start`、openai_compatible.rs:205 逐块 `log.write`），失败走 `log.error`——请求级审计是内建而非可选。

## 设计决策

**1. ProviderDef 与 Provider 为何分两层？** 代码给出的直接证据是签名：`metadata()` 与 `from_env()` 都是 `where Self: Sized` 的静态方法（base.rs:399-408）——它们**不可能**放进 `dyn Provider` 的对象安全虚表。分层的动机是生命周期错位：metadata 在"还没构造出实例"时就要用（注册表展示、setup 向导、inventory 判断），from_env 是异步工厂（等待 keychain/网络），而 Provider 实例每会话重建。`provider_registry.rs:118` 的 register 用泛型 `F: ProviderDef` 把静态方法擦除为闭包，正是这两层的粘合剂。（"为何不用关联函数 trait 对象 + 泛型注册"之外更细的权衡属**推断**：分离也让 declarative provider——`register_with_name` 系列，provider_registry.rs:153 起——能拿同一家 metadata 改名复用。）

**2. canonical 5063 模型目录解决什么？** 源码注释给了明确答案：`fetch_recommended_models` 过滤掉非文本输入与不支持工具调用的模型（base.rs:582-592），使模型选择器不被 embedding/图像模型污染；`model_info_for_provider_model`（base.rs:158）用 canonical 目录反查 reasoning 标志（base.rs:166-169，catalog 查不到再退 `ModelConfig::is_reasoning_model`）与上下文限额。canonical.rs:33-36 的 TODO 注释坦承代价："trades speed for correctness"——编译进二进制意味着新模型可能滞后。另一个有注释的决策：canonical.rs:70 `is_local_provider`（ollama/local）把 Pricing 清零——本地跑模型不该显示云端价格（测试 `ollama_models_have_zero_cost` 钉死该行为）。

**3. AuthProvider 为何独立成 trait？** api_client.rs:37 的 `Custom(Box<dyn AuthProvider>)` 是答案的一半：五路枚举覆盖不了的现实（GCP 的 OAuth 刷新、Azure 的租户发现、Databricks 的三方 token），以对象安全的小 trait 注入，ApiClient 对策略无感。另一半在 base.rs:775-785：`configure_oauth`/`refresh_credentials` 落在 **Provider** 上而非 AuthProvider 上，因为 OAuth 流程需要 provider 自身的配置键集合（ConfigKey 的 `oauth_flow`/`device_code_flow` 标志，base.rs:304-308，后者注明 RFC 8628 设备码授权）驱动 UI 分支。认证的"怎么发头"与"怎么拿到凭据"被切开：前者归 ApiClient，后者归 Provider + 各家 auth 模块（gcpauth/azureauth/databricks_auth/huggingface_auth）。（此拆分的意图陈述属**推断**，代码只体现结构。）

**4. 流式作为唯一必选推理方法的语义设计**——base.rs:804-806 的注释（部分文本/完整工具调用）+ base.rs:811 的单消息包装器，共同构成"内部一切皆流、外部按需聚合"的架构：非流式 provider 不损失协议一致性，流式消费者（UI 打字机）零轮询。

**5. 默认实现即产品决策**：`complete_fast` 的回退逻辑（base.rs:512-528）意味着每家 provider 免费获得"快速模型失败自动降级"；`generate_session_name`（base.rs:711）意味着会话命名零配置可用——但代价是 base.rs 里出现了 `strip_xml_tags`/`extract_short_title` 两个纯文本启发式函数（共 60 行），与"契约文件"的纯粹性略有张力。

## 新人提示

**新增一个 provider 的最小步骤**（以 REST 系为例）：

1. 写 provider 文件：定义结构体（持 `ApiClient + ModelConfig + name`），`impl ProviderDef`——参考 anthropic.rs:231-258 的 `metadata()`：known_models 列表 + ConfigKey 声明（secret 键要标 `secret: true`，如 anthropic.rs:248 的 API_KEY）；`from_env`（anthropic.rs:68）读配置→组 AuthMethod（anthropic.rs:77 用 ApiKey 挂 `x-api-key` 头）→`ApiClient::new().with_header(...)`（anthropic.rs:83 挂版本头）。
2. `impl Provider`：必选三件 + `stream`。若目标 API 是 OpenAI 兼容，**别写 stream**——直接实例化 `OpenAiCompatibleProvider`（openai_compatible.rs:29），传 base_url + completions_prefix 即可（xai/avian/nanogpt 等都这么复用）。
3. 注册：init.rs 的 `with_providers` 列表加一行 `registry.register::<XxxProvider>(bool)`。
4. 在 `mod.rs` 加 `pub mod xxx;`。

**格式翻译的坑**：(a) SSE 行解析必须用 `bytes_stream → StreamReader → LinesCodec` 三段管道，别自己 split 字节——跨 chunk 的半行会咬人（anthropic.rs:373-377 / openai_compatible.rs:191-195 是标准照抄模板）；(b) `[DONE]` 判定在 strip `data:` 前缀**之后**做（formats/openai.rs:918）；(c) tool_call 参数跨多个 chunk 到达，必须按 index 累积、`finish_reason == "tool_calls"` 才算完整（formats/openai.rs:961）；(d) 手工插 `"stream": true` 时记得非流式路径别插（openai_compatible.rs:312-330 的测试专门断言非流式 payload 无 stream 键）。

**测试矩阵在哪**：三层——base.rs 内嵌单测（base.rs:869-1130，覆盖 strip_xml_tags/extract_short_title/collect_stream 合并语义/ModelInfo）；各 provider 文件尾部 wiremock 测试（anthropic.rs:396 的 `make_provider_with_server` 用 wiremock MockServer 起 HTTP 假端点）；openai_compatible.rs:241-309 的 `http_status_maps_to_expected_error` 参数化测试钉死 402/429/401/400/500/404 到 ProviderError 变体的映射，改错误分类必过这关。跨 provider 契约测试在 provider_test.rs / testprovider.rs（TestProvider 也实现 Provider，图谱 implements 边可查）。

**其他易踩点**：给 `stream` 加 `#[instrument]` 会被 PR review 打回（base.rs:464-468 注释明令禁止）；API_KEY 类 secret 永远走 `config.get_secret` 而非 `get_param`（anthropic.rs:72）；新 provider 的 context_limit 若不在 canonical 目录里，`normalize_model_config`（provider_registry.rs:60）会用 metadata.known_models 兜底回填。

---

*本篇锚点 92 处，全部于写盘前 sed/grep 核实。图谱引用：LLM Provider 适配层（130 节点）、26 条 implements Provider 边、104 条 imports base.rs 入边。*
