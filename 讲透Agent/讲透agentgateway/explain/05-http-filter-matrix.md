# 05 · HTTP 过滤器矩阵：数据面的三十把瑞士军刀

> 源码基线：`/usr-data/data2/repos/aaif-projects/repos/agentgateway/crates/agentgateway/src/http/`（28 个非测试 `.rs` 文件 + auth/ext_proc/budget/retry/compression/oidc/substrate 七个子目录），链编排在 `crates/agentgateway/src/proxy/httpproxy.rs`（5712 行），统一契约在 `crates/agentgateway/src/store/policy.rs`，过滤器家族清单在 `crates/agentgateway/src/store/binds.rs`。托管体（Body）在 `crates/http/`（crate 名 `agent-http`）。全文行号锚均经 sed/grep 逐条核实（写盘前自验通过）。
>
> **勘误（任务书 vs 源码，按源码为准）**：①任务书说"cors 过滤器"在本目录——实际 `src/http/` 内没有 cors.rs，CORS 实现在**独立 crate** `crates/policies/cors`（crate 名 `agent_policy_cors`），`http/mod.rs:41` 只有一行重导出别名 `pub use agent_policy_cors as cors;`；本目录里拼写相近的 `csrf.rs` 是另一个过滤器（CSRF 防护）。②任务书说"mod.rs 过滤器链编排"——`http/mod.rs`（997 行）实为**共享工具库**（HeaderOrPseudo 伪头枚举、Cookie 解析、URI/query 改写、`inspect_body` 等帮助函数），真正的链编排在 `proxy/httpproxy.rs` 的三个函数里（见数据流一节）。③任务书归类"outlier detection 过滤器"——`outlierdetection.rs`（101 行）**不是** Envoy 式被动熔断器，而是解析上游 429 响应中 `Retry-After`/`x-ratelimit-*` 头方言（Anthropic/OpenAI/GitHub/Cerebras 四家）的启发式函数库，为重试退避提供"该等多久"的建议。④任务书提"租户/统计过滤器"——没有以这两词命名的过滤器：租户维度由 budget（按 API key 的费用预算）与 localratelimit 的 CEL key 分桶承担，统计由每个过滤器 apply 点内嵌的 RequestLog/dtrace snapshot 机制承担（见设计决策）。

## 一、角色定位（16 层架构 L08；请求进出数据面的必经链路）

understand 图谱的 16 层架构中，本区域是 **L08「HTTP 过滤器矩阵」**——全图谱 16 层中节点数最大的层（1069 节点，第二名 L03 控制面翻译引擎 987），层摘要原文："数据面流量处理主力：src/http 下 30+ 过滤器——jwt/oidc/oauth 认证、ext_authz/ext_proc 外部集成、local/remote 限流、重试、路由、缓冲、压缩、CEL 转换、budget 预算……"。它的定位一句话：**每个进入数据面的 HTTP 请求和每个返回给客户端的响应，都要按固定顺序穿过这里的一串策略对象，任何一个都可以改写请求、注入头、扣减配额，或者干脆把请求短路成直接响应**。

数量上核对源码（store/binds.rs:398-427）：`RoutePolicies` 结构体有 **27 个策略字段**（local_rate_limit/remote_rate_limit/authorization/jwt/oidc/basic_auth/api_key/budget/ext_authz/substrate_egress/substrate_ingress/ext_proc/transformation/csrf/direct_response/llm/timeout/retry/delay/request_header_modifier/response_header_modifier/request_redirect/url_rewrite/hostname_rewrite/request_mirror/cors/buffer），`GatewayPolicies`（binds.rs:432）另有 11 个网关级字段，`BackendPolicies`（binds.rs:268）还有 20+ 个后端级字段（backend_tls/backend_auth/a2a/llm_provider/llm/inference_routing/mcp_* 等）。三处字段去重后约 **33 种不同过滤器**——"三十把瑞士军刀"名不虚传，且同一把刀可在 Gateway→Listener→Route→RouteRule 四个挂载点重复出现（见外部连接）。

与兄弟层的关系：L07（数据面骨架）提供 proxy/store/client 骨架并**调用**本层；L10（CEL 栈）为几乎每个过滤器的条件表达式求值提供底座；L14 的 agent-http crate（body/peekbody/recordbody）提供过滤器读写 body 的托管体；L11（LLM Provider 翻译）通过 `llm::Policy` 与 `inference_routing` 深度嵌入本矩阵（token 计费与请求改写都挂在本层的 apply 点上）。

## 二、内部结构（统一契约 → 链编排 → 代表过滤器精讲）

### 2.1 统一契约：三个 trait 划分执行时机（本矩阵最重要的抽象）

`store/policy.rs` 用三个 trait 把所有过滤器按**执行时机**分为三类，注释写得极清楚：

- **`RequestPolicyTrait`**（policy.rs:37）——请求侧策略，doc 注释（policy.rs:32-35）："run exactly once per request, **and are not repeated on retries**"（每请求恰好一次，重试不重复）。签名：`async fn apply(&self, client: &PolicyClient, log: &mut RequestLog, req: &mut Request) -> Result<PolicyResponse, ProxyResponse>`。返回值是双通道：`Ok(PolicyResponse)` 表示放行（可携带响应头注入），`Err(ProxyResponse)` 表示短路（直接响应）。
- **`ResponsePolicyTrait`**（policy.rs:80）——响应侧，注释（policy.rs:76-78）："run exactly once per request, **after all retry attempts**"（所有重试结束后恰好一次）。绝大多数实现是"同一 struct 同时实现请求侧与响应侧"，请求侧选中的实例被保留到响应侧复用。
- **`BackendPolicyTrait`**（policy.rs:91）——后端侧，注释（policy.rs:88-89）："runs per-backend... on **each backend call. This could be a retry attempt**"（每次后端调用都跑，含重试）。

另有**桥接 blanket impl**（policy.rs:54-56）：任何实现外部 `agent_policy::RequestPolicy` 的类型自动获得本网关的 `RequestPolicyTrait`——这正是 CORS crate 能以零胶水接入的原因。`RequestPolicy<T>` 包装器（policy.rs:111）管理"多策略 + CEL 条件"选择：`Multiple(Vec<PolicyWithCondition>)` 变体注释（policy.rs:123）明确"**the first one that matches is used**"（顺序求值，第一个条件命中者生效）；`select()`（policy.rs:263）做条件求值但不 apply；`merge_with_inheritance`（policy.rs:301）的注释（policy.rs:296-300）写明了继承合并规则：Route 策略按 less-specific 到 more-specific（Gateway → Listener → Route → RouteRule）游走，后写者胜，除非某级声明 `inheritance=Override` 则锁定该字段。

### 2.2 请求链编排（真实顺序，proxy/httpproxy.rs）

`apply_request_policies`（httpproxy.rs:233）是请求侧链的总装线，固定顺序为：

1. **timeout** 选择（httpproxy.rs:242）——最先跑，选出 `RequestDeadline` extension（httpproxy.rs:244-246）插进请求，供后续 body 读取 deadline 用；
2. **cors**（httpproxy.rs:255）——必须最先于一切认证，源码注释（httpproxy.rs:249-252）给出两条理由：预检 OPTIONS 请求要**无凭证短路**；且 CORS 响应头要"排队"进 response_headers，这样即使请求随后被认证拒绝，浏览器仍能读到错误详情而非笼统的 CORS 错误；
3. 认证四连：**oidc**（:260）→ 剥离保留 cookie 前缀（:262）→ **jwt**（:266）→ **basic auth**（:270）→ **api key**（:274）；
4. **budget**（:278，LLM 费用预算）→ **ext_authz**（:283，外部授权服务）→ **authorization**（:288，CEL 授权）→ substrate egress/ingress（:290-303，mTLS 身份进出网格）；
5. **retry 选择**（:305）——注意只 `select` 不 apply，且立即求值 retry precondition（:307-315），条件不满足则整单禁用重试；
6. **local rate limit**（:318-321）→ **remote rate limit**（:323-326）——都返回"已扣费桶"待响应侧结算；
7. **buffer**（:328）——唯一在链里用带响应侧的 `apply`；
8. **ext_proc**（:333-336）——`select` 出配置后 `build` 成 per-request 状态，再 `mutate_request`，其中 `assert_size::<{ 4 * 1024 }>()`（:339）限制单次 ext_proc 处理的 body 前缀 4KB；
9. **transformation**（CEL 请求改写，:346-349）→ **csrf**（:351-354）→ response header modifier 只 select 不跑（:358-360，条件在请求侧求值一次、动作留到响应侧）→ request header modifier（:361-364）→ hostname rewrite 默认 Auto（:366-379）→ **url rewrite**（:380-383）→ **request redirect**（:384-387）；
10. **delay**（:390-393）——注释（:389）"delay should happen after auth but before direct response"（故意故障注入要在认证后、直响应前）；
11. **direct response**（:394-397）——静态/CEL 直响应，终极短路。

收尾统一调 `mark_sensitive_headers`（http/mod.rs:43，把 Authorization/Proxy-Authorization 及配置的敏感头打 `set_sensitive` 标记，防日志/trace 泄漏）。backend 侧另有 `apply_backend_policies`（httpproxy.rs:405）在每次后端调用（含重试）时跑 backend 级 authorization/ext_authz/transformation/header modifier/url_rewrite/redirect；mirror 的 spawn 注释（:499）强调"**Mirror once per request (not per retry)**"——镜像只在首次尝试发射。

### 2.3 代表过滤器精讲之一：retry 与 ReplayBody（回环的核心）

配置 `retry::Policy`（retry/mod.rs:15）五字段：`attempts`（NonZeroU8，默认 1）、`backoff`、`codes`（可重试状态码）、`precondition`、`condition`（两者都是 CEL）。precondition 字段注释（retry/mod.rs:33-34）直说设计动机："Retrying requires **buffering the request body in memory** for replay, so this lets us skip that cost when the request is known to be non-retriable (e.g. streaming or websockets)"——即重试的成本不是多打一次请求，而是**整个请求体必须可回放**。

回放靠 `ReplayBody`（retry/body.rs:32），文件头（retry/body.rs:1-3）坦承血统："derived from **Linkerd2** and inspired by linkerd.io 2021 博客 how-linkerd-retries-http-requests-with-bodies"。它的语义（body.rs:17-27 注释）：惰性缓存读过的字节；clone 体在被 poll 时接管共享状态，drop 时把缓冲（含它新读到的）归还共享态供下一个 clone 用。

重试回环本体在 httpproxy.rs:1180-1336：`MAX_BUFFERED_BYTES = 64 * 1024`（:1169）是硬上限——仅当 `attempts > 1` 且 body size_hint 下界 ≤64KB 才把 body 换成 ReplayBody（:1195-1202），否则注释直言"initial body is too large to retry, disabling retries"（:1205）。回环 `for n in 0..attempts`（:1244）：非最后一次尝试先 clone（:1255）；n>0 时记 `log.retry_attempt`（:1262）并给上游请求加 `x-retry-attempt` 头（:1264-1266）；判定用 `should_retry`（:1297，函数体在 :3921-3942）：状态码命中 `codes`、或 CEL `condition` 为真（:3933 注释举例：某些 API 返回 200 但用头标失败，状态码判不出）、或错误本身 `is_retryable()`；直响应错误一律不重试。退避睡眠与 request_timeout **竞速**（:1321-1332）：`tokio::time::timeout_at(deadline, sleep(bo))`——deadline 先到就放弃退避直接超时，绝不为了等 backoff 突破总时限。

### 2.4 代表过滤器精讲之二：localratelimit 令牌桶（请求计数与 LLM token 双模）

`RateLimitSpec`（localratelimit.rs:35）五字段：`max_tokens`/`tokens_per_fill`/`fill_interval` 三件套描述令牌桶；`limit_type` 区分 `Requests`（一请求一 token）与 `Tokens`（按 LLM token 计费，:64-68）；`key` 是 CEL 表达式选桶（注释 :47-52 举例 `jwt.sub` 按用户、`jwt.team` 按团队，每distinct 值独立成桶）。

三个精细设计：

- **keyed 桶防炸**：`MAX_BUCKETS: usize = 65_536`（:93），注释（:90-92）解释"key 由调用方选（如请求头），否则任何人都能让 map 无限增长；超限丢最久未用的桶，效果等于从没见过那些 key"。桶缓存用 `quick_cache::sync::Cache`（:10 引入，:16 keyed 字段）。
- **ChargedBucket 记账**（:98-122）：请求被放行时返回已扣费的桶句柄；`amend_tokens`（:107）事后补扣（真实 LLM 用量结算），`refund`（:112）全额退还——用于**另一个规则后来拒绝了请求**的场景。请求侧 apply（:281-316）的 Err 分支注释（:300-302）写明动机："The request is rejected, so it **must not count against the rules that admitted it**"——多条限流顺序检查，中途一条 429 则先前的扣费全部回滚。
- **LLM token 双段计费**：请求侧 `charge_tokens`（:230-259）若已 tokenize 就先扣 input tokens；若没有（如流式透传），只确认桶里至少还有 1 个 token（:246-248），注释诚实承认"**this may lead to large over-allowance, especially with fast fill_intervals**"（可能大幅超放，尤其快填充率下）。响应侧由 llm crate 的 `amend_tokens`（llm/mod.rs:3500-3521）结算差值：`(normalized_input − 已扣 input) + output_tokens`。

### 2.5 代表过滤器精讲之三：ext_proc（Envoy 外部处理协议的流式实现）

ext_proc 是矩阵中最大的单文件过滤器（ext_proc.rs 1921 行 + 五个子模块 buffering/channel/headers/mutation/processing）。它把请求/响应头、body、trailers 通过**gRPC 双向流**发给外部处理服务，接收改写指令。默认体模式是 `BodySendMode::FullDuplexStreamed`（:215-216，请求与响应体都是全双工流式——body 边转发边送 ext_proc 服务，不整存）。核心入口 `mutate_request`（:914）先调 `mutate_request_inner`（:928）驱动 `RequestFlowFsm` 状态机（processing.rs：请求头→body 块→trailers 的相位推进，`mode_state` 是可被对端 mode_override 修改的协议状态，request_fsm 是本次调用的执行相位——:948-951 注释特意区分这两层状态）。

两个易漏的细节：①流式送出后**重建检查缓存**——`let rebuffer = req.body().needs_inspection()`（:918）+ mutate 后重新 `inspect_body`（:920-924）：因为 ext_proc 可能改写 body，下游过滤器的 body 检查缓存必须失效重建，这直接解释了 agent-http Body 的 `require_inspection` 语义（见设计决策）；②推理路由包装层 `mutate_request`（:240-263）在送出前**剥掉** `x-gateway-destination-endpoint` 头（:245-246），注释："The destination header is an **EPP output, not a client-controlled input**"——防客户端伪造 ext_proc 的目的地指令，这是安全边界。失败语义支持 fail-open：`failed_open = ext_proc.skipped`（:249）。

### 2.6 其余家族速览（一过滤器一句）

`timeout::Policy`（timeout.rs:8）三字段各管一段：`request_timeout`（起点到**响应头**到达，:9-11 注释明说 body 不算）、`backend_request_timeout`（上游调用全程）、`response_idle_timeout`（响应 body **帧间**空闲上限，:27-39 注释解释为何需要第三种：前两个到响应头即止，"neither can distinguish a stalled stream from a slow one"；且不适用于协议升级隧道）。`Buffer`（buffer.rs:30）请求/响应两侧可配 `max_bytes` 与 `failure_mode`（buffer.rs:8-14：FailClosed 超限报错为默认，FailOpen 超限转回流式继续）。`delay::Policy`（delay.rs:10）的 duration 本身就是 CEL 表达式，注释给出 `random() < 0.1 ? 500 : 0` 概率延迟与 `int(random() * 500)` 抖动的官方姿势。`DirectResponse`（filters.rs:294）支持静态 body 与 CEL `body_expression`/headers 表达式（两者互斥，:320-325）。`Csrf`（csrf.rs:9）基于 Origin 头校验 same-origin + additional_origins 白名单。`ExtAuthz`（ext_authz.rs:186）可配 gRPC/HTTP 协议与 failure_mode。`RemoteRateLimit`（remoteratelimit.rs:27 起）对接 Envoy 风格 rate limit service，failOpen 时服务挂了也放行（:31-32 注释）。`budget::BudgetCounter`（budget/mod.rs:29）是 nanodollar 精度（:23 常量 `NANODOLLARS_PER_USD = 1_000_000_000`）的滚动窗口计数器，配 SQLite/Postgres 持久化（budget/ 目录四 个 SQL 文件）。

## 三、外部连接（控制面热更新下发 / LLM 与 MCP 深水区 / agent-http 托管体）

**上游：xDS 热更新。** 过滤器配置不是编译期装配，而是每次请求时从 `store` 现取：`route_policies()`（binds.rs:996）按 RoutePath 把 Gateway→ListenerSet→Listener→Service→Route→RouteRule→inline 各挂载点的策略**newest-first 游走**合并，注释（binds.rs:999-1000）："merged with **last-writer-wins** semantics. Visit policies at each attachment level newest first so the **oldest policy is applied last and wins**"（最新优先游走、最老最后应用——last-writer-wins 的实现手法是反序应用）。store 的内容则由 control 面（src/control/，`agent_xds::ClientTrait` 实现）接收 xDS 推送刷新（见 01/03 篇控制面链路）。这意味着**改一条 Policy CR，数据面无需重启，下一个请求就用新链**。代价是每次请求都有一次策略合并——这是"灵活性 vs 每请求开销"的显式取舍（推断：RoutePolicies 字段全 Arc 克隆，合并成本可控，但高频路由下不可忽略；源码无直接注释）。

**下游：LLM 路由与 MCP 网关。** `RoutePolicies.llm` 字段（binds.rs:415）挂 L11 的 `llm::Policy`——请求在 HTTP 链里被 tokenize、计费（httpproxy.rs:621 的 `charge_tokens` 调用点就在 LLM 请求构建处）、协议翻译后送 provider；`inference_routing`（binds.rs:273）+ ext_proc 的推理路由模式（ext_proc.rs:129 的 `InferenceRoutingDestinationMode`）允许 ext_proc 服务动态选目的地。MCP 网关（L09）的 mcp_authorization/mcp_authentication/mcp_guardrails 三个 BackendPolicy 字段（binds.rs:431 注释指明在 mcp/handler.rs + mcp/session.rs 应用）复用同一套 trait 契约——矩阵的抽象对 MCP 流量同样成立。

**横向：agent-http 托管体。** 矩阵中所有 body 操作都走 `crates/http/`（crate `agent-http`）：`BodyInspection` 枚举（http/src/lib.rs:71-76）只有 `Complete`/`Partial` 两态；`RecordedBodyHandle`（recordbody.rs:19 起）的 doc 注释（recordbody.rs:13-18）精确定义了**检查 vs 录制**的分野："Recording is **passive**: enabling it does not read the body... primarily used for **logging after** a body has been sent. In contrast, `BodyInspection` is the immediate result of **actively inspecting** a body **before** forwarding"——检查是主动的、前置的、供过滤器决策；录制是被动的、伴随的、供审计日志。`inspect_body` 帮助函数在 agentgateway 侧的入口是 http/mod.rs:775。

## 四、数据流（一次请求穿链的完整路径，含短路/重试回环）

以一个带 JWT、走 LLM 后端、可能 503 的 POST 为例：

1. **入场**：请求归一化后进入 `apply_request_policies`（httpproxy.rs:233）。timeout 先行插 `RequestDeadline`（:244-246）；cors 放行并排队 CORS 头（:255）；jwt 验签通过后把 `jwt::Claims` 塞进 extensions（DebugExtensions 的枚举清单可见全量 extension 生态，mod.rs:805-879）；rate limit 桶扣 1 token（或按 input tokens 扣，:621）；若 jwt 拒签 → 返回 `Err(ProxyResponse)` → **整链短路**，链上剩余过滤器全部跳过，但已排队的 CORS 头仍会拼进错误响应（这正是 cors 先行的意义）。
2. **改写段**：transformation/ext_proc 可改头改体（ext_proc 流式段进 gRPC channel，同时请求继续向下）；header modifier/url rewrite 改 URI；direct response 若命中则直接构造响应返回——不触后端。
3. **重试准备**：`for n in 0..attempts`（:1244）回环开启。首轮 body 是 ReplayBody 包装：它边被上游连接消费、边把字节缓存进共享态；`should_retry`（:3921）看响应——503 在 codes 里 → 可重试。
4. **重试回环**：非末轮 clone body（:1255，共享缓冲交接）；打 `x-retry-attempt: 1`（:1264）；**backend 策略重跑**（BackendPolicyTrait 语义：每后端调用一次，httpproxy.rs:405 的函数在每次 attempt_upstream 内被调）；退避 sleep 与 request_timeout deadline 竞速（:1324）。第二轮拿到 200 → 不可重试 → 跳出。
5. **响应侧**：所有尝试结束后，ResponsePolicyTrait 们按序跑（response header modifier 此刻才真正改头，httpproxy.rs:5053-5057 两级：route 级与 backend 级）；ext_proc 的响应 FSM 做流式 body 变换；llm 的 `amend_tokens`（llm/mod.rs:3500）按真实 output tokens 结算限流桶；`apply_response_idle_timeout`（timeout.rs:50）给 body 挂帧间空闲超时后流回客户端。
6. **失败路径的岔口**：若上游 429，`retry_after`（httpproxy.rs:3885 调 outlierdetection.rs:19）解析 Retry-After/x-ratelimit-reset 头给出建议等待时长，写入 RequestLog（telemetry/log.rs:886 的 `fallback_duration = retry_after.or(retry_backoff)` 显示它还会兜底默认退避）；若限流桶空，请求侧直接 429 且**退还其他桶的扣费**（localratelimit.rs:301-305）。

## 五、设计决策（取舍三则：trait 时机契约 / 检查缓存 / 三段超时）

**① 三个 trait 而非单一 Filter 接口。** Envoy 用 filter 回调族（decodeData/encodeData...），本仓选择了"按**时机**切分契约"：Request/Response/Backend 三个 trait 把"重试时哪些逻辑要重跑、哪些不重跑"从运行时约定提升为**类型系统事实**（policy.rs:32/76/88 的三段注释是文档即契约）。代价：同一过滤器要改 body 头时得实现多个 trait（HeaderModifier 在 filters.rs:87/100/112 实现了三个）；收益：重试语义不可能配错——预算类扣费只能是 RequestPolicy（重试不重复扣），签名类重写必须是 BackendPolicy（每次 attempt 都要重签）。

**② 检查缓存（peekbody）为何存在。** 流式代理里"看一眼 body"是奢侈品：body 是单遍流，读了就得有人存。agent-http 的解法是 Representation 三态（body.rs:487-499 的 `inspection()`）：Buffered → Complete 缓存终身有效；Streaming+inspected_prefix → Partial（前缀缓存）；未检查 → None。第一个想看 body 的过滤器（如 transformation 的 CEL 求值）调 `inspect_body`（mod.rs:775）触发读取，**后续过滤器免费复用**，转发时 PrefixBody（peekbody.rs:14 起）把检查时读出的前缀重放给上游再续流——body 对网络仍是流式的，只有网关内存里多了一份限额前缀。失效规则被显式建模：`require_inspection`（body.rs:526）标记"此 body 之后会被替换，替换后仍需可检查"，ext_proc 流式改写后就靠它触发 rebuffer（ext_proc.rs:918-924）。没有这个缓存，矩阵里每个 body 相关过滤器（csrf 校验、CEL 转换、jwt 内嵌凭证提取、LLM tokenize）就得各自缓冲整份 body——内存放大 N 倍。

**③ 三段超时各管一段，body 用"软"空闲而非"硬"总限。** timeout.rs 的三字段覆盖三段不相交的时间窗：request_timeout 管"到响应头"、backend_request_timeout 管"单次上游调用"、response_idle_timeout 管"响应帧间隔"（:32-39 注释）。第三种最微妙：SSE/流式 LLM 响应总时长不可预估（长生成合法），但**卡死**必须检测——所以不设总限，只设帧间空闲（`set_idle_timeout` 挂在 body 上，:59；每帧到达重置窗口，timeout.rs:96-120 的测试 `each_frame_restarts_the_idle_window` 用 4 帧×0.8s 窗口 1s 验证了"慢但不卡"的流不被杀）。这相当于把"硬超时"（总时长上限）换成"软超时"（活跃度下限）——注释同时声明协议升级（WebSocket/CONNECT 隧道）豁免（:37-39）。补充：body 读取的绝对 deadline 由 `set_deadline`（body.rs:535）承载，与 RequestDeadline extension 联动——mod.rs:753-763 的三个 read 帮助函数注释统一写着"with the ... remaining body deadline"。

**④（补）重试体的 64KB 天花板是刻意的成本闸。** ReplayBody 缓存上限 64KB（httpproxy.rs:1169）+ size_hint 前置检查（:1195）意味着**大请求体自动失去重试资格**，配合 precondition CEL 让用户对 POST/流式显式豁免（retry/mod.rs:33）——这是"可重试性"与"内存安全"之间的明码标价，比 Envoy 的 buffer filter 方案更保守（推断：64KB 覆盖典型 JSON/LLM 小请求，而多部分上传/大 prompt 用户需自知不可重试；源码注释未解释 64KB 取值本身）。

## 六、新人提示（加过滤器的步骤 / 本地测试 / 坑）

**加一个请求侧过滤器的最短路径**：①在 `src/http/` 新建 `myfilter.rs`，定义 `#[apply(schema!)]` 配置 struct；②实现 `crate::store::RequestPolicyTrait`（policy.rs:37 的签名），短路就返回 `Err(ProxyResponse)`，注入头就填 `PolicyResponse.response_headers`（用 mod.rs:787-801 的 `PolicyResponseExt::apply` 语义：direct_response 存在则 Err 短路，否则 merge 头）；③在 `store/binds.rs:398` 的 `RoutePolicies` 加字段 `pub my_filter: RequestPolicy<MyFilter>`；④在 `proxy/httpproxy.rs` 的 `apply_request_policies` 里选好插入位置加一行 `apply_without_response`（顺序即语义：认证前还是认证后要想清楚——cors 的前置注释 httpproxy.rs:249 是顺序敏感的最佳教案）；⑤若配置含 CEL，实现 `expressions()`（policy.rs:48 的默认空实现注释警告："Any expressions used in the policy **MUST** be included here or they will be ignored"——漏了表达式就静默失效，不报错）。

**本地测试**：每个过滤器都有同目录 `*_tests.rs`（mod 内 `#[path]` 引入，如 filters.rs:20-22）；跨过滤器链级测试看 `tests_common.rs` 与 `src/tests/`（L13 层）；timeout 的测试展示了 tokio 时间冻结技巧（`#[tokio::test(start_paused = true)]`，timeout.rs:74）。限流类测试建议照 localratelimit_tests.rs 的桶构造 helper 抄。

**坑四条**：①**别在 mod.rs 找链**——编排在 httpproxy.rs，mod.rs 只是工具箱（本篇勘误②，笔者自己也先踩了）；②**cors/csr f 一字之差**：cors 是外部 crate 重导出（mod.rs:41），csrf 才是本目录实现，grep 时注意；③**多策略是"第一个命中生效"而非全跑**（policy.rs:123），配置了带条件的 fallback 链时，条件求值顺序就是优先级，调试时用 dtrace 的 `pol_result!` 输出（policy.rs:269-283 的 Skip/Apply 三态日志）看哪条被跳过；④**想读 body 就用 `inspect_body`（mod.rs:775）而非自己 collect**——缓存会让下一个过滤器白嫖你的读取，自己 collect 则既爆内存又破坏 deadline 传播；body 被你改写后记得 `require_inspection`（body.rs:526）保住下游的可检查性，否则下游过滤器拿到的是 None 缓存。

---

**本篇锚点清单**（全部经 sed 逐行核实）：http/mod.rs:41,43,90,775,805；http/filters.rs:20,29,44,87,100,112,152,234,294,382；store/policy.rs:32,37,48,54,76,80,88,91,111,123,263,296,301；proxy/httpproxy.rs:233,242,244,249,255,260,262,266,270,274,278,283,288,290,303,305,318,323,328,330,333,339,346,351,358,361,366,380,384,389,390,394,405,449,499,501,621,1169,1195,1200,1244,1255,1262,1264,1297,1321,1324,3885,3921,3933,5053；http/timeout.rs:8,9,27,32,50,59,74,96；http/retry/mod.rs:15,33；http/retry/body.rs:1,17,32；http/localratelimit.rs:10,16,35,64,90,93,98,107,112,230,243,246,281,300,301；http/outlierdetection.rs:19,29,30,68；http/ext_proc.rs:129,215,240,245,249,914,918,928,948,1034；http/buffer.rs:8,20,30；http/delay.rs:10,13；http/csrf.rs:9；http/budget/mod.rs:23,29；http/ext_authz.rs:186；http/remoteratelimit.rs:27,31；store/binds.rs:268,273,398,413,415,431,432,996,999；llm/mod.rs:3500；crates/http/src/lib.rs:71；crates/http/src/recordbody.rs:13,19；crates/http/src/body.rs:487,526,535；crates/http/src/peekbody.rs:14；telemetry/log.rs:886。
