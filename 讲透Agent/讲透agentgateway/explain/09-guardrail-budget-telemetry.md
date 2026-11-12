# 09 · guardrail、预算与遥测：LLM 流量的治理三件套

> 源码基线：`crates/agentgateway/src/`（行号锚均经 sed 逐条核实）。本篇覆盖三个目录：`llm/policy/`（guardrail + PII 识别器）、`http/budget/`（预算）、`telemetry/log_store/`（请求日志库）。
>
> **路径勘误（以源码为准）**：任务书把三块都归在 `llm/` 下，实际 budget 位于 `src/http/budget/`（budget/mod.rs:16-17 声明 `mod database; mod status;`），log_store 位于 `src/telemetry/log_store.rs` + `log_store/{sqlite,postgres}.rs`。图谱分层归属也据此修正：policy/ 全部节点在 **L11「LLM Provider 翻译引擎」**，log_store 节点在 **L07「Rust 数据面核心与可观测性」**（含 `table:` 节点），budget 节点在 **L08「HTTP 过滤器矩阵」**；L10「CEL 表达式与策略求值栈」与 policy 的交集是 `cel::GuardDetail`（policy/mod.rs:8）与贯穿各评估函数签名的 `cel::RequestSnapshot`（如 589/662）这些 CEL 求值类型——即"治理三件套横跨 L11/L07/L08 并消费 L10"，而非任务书写的 L10/L11 交叉。

## 一、角色定位

如果把 agentgateway 的 LLM 数据面比作一条高速公路，本篇三块就是三根护栏：

- **guardrail（管得住）**：在请求进入上游模型前、响应回到客户端前插检。六类 kind（policy/mod.rs:2128-2141）中五类要出网调用外部评审服务（webhook / OpenAI moderation / AWS Bedrock Guardrails / Google Model Armor / Azure Content Safety），一类纯本地正则+PII 识别。失败语义默认 failClosed（policy/mod.rs:2230-2238：`FailureMode` 默认 `failClosed`，"When failing closed, the error is propagated and the LLM request is rejected"）。
- **budget（花得起）**：按 standalone API key 计费的配额器。内存 `BudgetCounter` 即时扣账、`pending` 增量每 5 秒批量落库（database.rs:15），USD 单位用 nanodollar 定点整数存库（mod.rs:23）避免浮点漂移。
- **log_store（看得见）**：请求日志的专用异步写入器+查询引擎。单后台线程聚合批量写入（默认批 16384 条，log_store.rs:160），Postgres 走 COPY 二进制流式导入，SQLite 走分块多值 INSERT；对外提供 search/get/tail/analytics_summary 四类查询（log_store.rs:97-129）。

三者共享同一条请求生命线 `RequestLog`：guardrail 结论写进 `log.guardrails`（llm/mod.rs:355），预算结算对象挂进 `log.budgets`（mod.rs:561），请求结束时统一触发结算并 `log_store::emit`（log.rs:1465-1467, 2242）。这是"治理三件套"在代码结构上的真实耦合点。

## 二、内部结构

### 2.1 六类 guardrail kind 与执行骨架

`RequestGuardKind` 六个变体（policy/mod.rs:2128-2141）：`Regex` / `Webhook` / `OpenAIModeration` / `BedrockGuardrails` / `GoogleModelArmor` / `AzureContentSafety`；`ResponseGuardKind` 少一个 moderation（2545-2556）。每个 guard 外壳是 `RequestGuard`（2058-2072）：`rejection`（自定义拒答响应，默认 403 + "The request was rejected due to inappropriate content"，2570-2576）+ `scope`（默认 systemPrompt+messages+toolOutput，2074-2080；显式空 scope 会被反序列化器直接报错拒绝，2082-2093）+ `kind`（`#[serde(flatten)]` 内联进 JSON）。

执行骨架是"评估与执行分离"：`apply_single_request_guard` 的注释钉死了契约（1015-1016）——"Provider-specific code only produces an evaluation; common code below applies its decision"，即六类 provider 只产出 `GuardrailOutcome`（358-366：`None`/`Masked`/`Rejected`/`Audit`/`FailOpen` 五态），公共层统一翻译成动作。两种动作枚举区分了"能不能改写"：regex 能改文本所以有 `Mask/Reject/Audit` 三态（2430-2439），云端评审服务只能给裁决所以是 `RejectAuditAction` 二态（2445-2456，注释："Bedrock, webhook, OpenAI moderation, Google Model Armor, and Azure Content Safety decide *what* they flag; the gateway only chooses whether to enforce that verdict"）。

三云集成端点实证：Bedrock 拼 `bedrock-runtime.{region}.amazonaws.com` 调 ApplyGuardrail API（bedrock_guardrails.rs:240,245）；Google Model Armor 拼 `modelarmor.{location}.rep.googleapis.com`（google_model_armor.rs:362）；Azure 拼 `https://{endpoint}/contentsafety/{text:analyze|text:detectJailbreak}?api-version=...`（azure_content_safety.rs:164,256,308）。Azure 是唯一"一托二"的：`analyze_text` 查四类危害+自定义 blocklist（severity 0-6，默认阈值 2，2405-2418），`detect_jailbreak` 仅限请求方向（2397-2400 注释 "Only applicable to request guards"）。OpenAI moderation 则复用 async-openai 类型直打 `https://api.openai.com/v1/moderations`（moderation.rs:26），默认模型 `omni-moderation-latest`（19）。

### 2.2 PII 识别器：Presidio 风格的本地识别层

`pii/` 目录结构完全复刻 Microsoft Presidio Analyzer 的形制：`Recognizer` trait（recognizer.rs:3-6，`recognize(&self, text) -> Vec<RecognizerResult>`）、带置信度分数的 `RecognizerResult{entity_type, matched, start, end, score}`（recognizer_result.rs:2-8）、`PatternRecognizer` 基类含 context 增强词表字段（pattern_recognizer.rs:14-20）——连 Presidio 的 `PatternValidator` 钩子都以注释形态保留在 19 行和 55-64 行（`// if let Some(validator) = self.validator`），这是"风格移植"的直接代码证据（移植来源为推断，注释未点名 Presidio）。

具体识别器（目录共六个文件）：email 单模式置信 0.85（email_recognizer.rs:19-20）；信用卡按卡组织五个正则预筛全部 0.3（credit_card_recognizer.rs:27-52），再过 **Luhn 校验**过滤假卡号（64 行 filter，73-98 行实现，注释直接引 PCI 安全标准文档链接）；美 SSN 五档模式从 0.05（弱：9 位裸数字）到 0.5（中：3-2-4 带分隔符）（us_ssn_recognizer.rs:20-32）；加 SIN 带格式 0.7 / 裸 9 位 0.3（ca_sin_recognizer.rs:15-21）；**电话识别器最重**——`phonenumber` 库按 US/GB/DE/IL/IN/CA/BR 七区解析验证（phone_recognizer.rs:20），`split_numbers` 是一个字级动态规划（102-158 行）：`MAX_NUMBER_WORDS=6`、E.164 上限 15 位（121-125 行注释），目标函数"最大化覆盖数字数、其次匹配数更少"（112 行 `score_from` + `Reverse` 排序），从连续数字串中切出最优的一组电话号划分。

**勘误（以源码为准）**：任务书说"识别器六件套"——目录确实六个识别器文件，但只有 5 个被接线：pii/mod.rs:19-32 只导出 `EMAIL/PHONE/CC/SSN/CA_SIN` 五个 static，`Builtin` 枚举（mod.rs:2201-2213）也只有 ssn/creditCard/phoneNumber/email/caSin 五项；`url_recognizer.rs`（内含巨型 TLD 枚举正则，14 行）**没有任何消费者**，靠 pii/mod.rs:1 的 `#![allow(dead_code)]` 压住编译警告，属编译进二进制但未启用的存货。

消费点在 `apply_prompt_guard_regex`（policy/mod.rs:1838-1934）：builtin 模式查 `pii::recognizer`（1853-1859），命中后按 action 分流——`Audit` 只记日志、`Reject` 返回拒绝、**`Mask` 是真改写**：替换占位符为 `<ENTITY_TYPE>`（1873 行 `format!("<{}>", results[0].entity_type)`，测试 2787-2809 验证 `john.doe@example.com → <EMAIL_ADDRESS>`），多命中按 start 降序+重叠合并后逐段 `replace_range`（1876-1887）；自定义 regex 则统一替换 `<masked>`（1928），并显式过滤零宽匹配防"替换出占位符"（1910-1915 注释）。

### 2.3 streaming_guardrails：pin_project 宏内的窗口化状态机

`streaming_guardrails.rs` 开篇模块文档（1-18 行）把设计说得极明白：SSE 帧**先扣住不转发**，文本增量攒到 `DEFAULT_EVAL_THRESHOLD=1024` 字节（44 行）触发评估；评估窗口 = 上一窗口的 `OVERLAP_BYTES=256` 字节尾部拼接本批（overlap 保证跨批模式连续可见）；通过则放行扣住的帧，拦截则**丢弃未转发帧**并注入合成错误事件。文档同时承认局限（17-18 行）："This is not 100% accurate: a guard that needs full-response context, or a pattern spanning more than the overlap window, can be missed."

实现核心是 `pin_project!` 宏包裹的 `GuardedSseBody`（264-283 行）：`#[pin] inner` 是上游 body（`poll_frame` 期间需要固定引用），其余字段（held_frames/held_bytes/pending_text/overlap_tail/sse_decoder/state）是普通字段可变借用——这是 pin_project_lite 对"自引用 Future 结构体"的标准拆法。状态机 `GuardedBodyState` 五态（213-225）：`Buffering`（攒帧）→ `Evaluating{fut, eof}`（异步评估，EvalFuture 是 `Pin<Box<dyn Future>>`，209-210）→ `Flushing{queue, eof}`（逐帧放行）或 `Blocked(Bytes)`（197-207 行 `guardrail_blocked_sse_bytes` 生成 `data: {"error":{"type":"guardrail_blocked","code":"guardrail_intervention",...}}` 单帧）→ `Done`。两个防御细节：缓冲区满但文本为空（全是控制帧/解析不了的格式）时直接原样放行防卡死（504-514 行注释 "flush the buffer as-is without evaluation, to avoid stalling on unprocessable content"）；SSE 解码出错则清缓冲重置 decoder 防错误累积（493-500）。

`extract_text_delta`（334-408）一函数适配四家流式格式：OpenAI Responses 事件（346-355）、OpenAI completions 的 choices[].delta（357-377，含 reasoning/reasoning_content/reasoning_details 三种推理字段）、Anthropic messages 的 delta/content_block（379-388）、Gemini candidates[].content.parts[]（390-406，`thought:true` 归 reasoning 流）。**text 与 reasoning 是两条独立窗口流**（`ResponseDelta` 228-231 + `take_windows` 247-262 各自维护 overlap），测试 879-889 验证"credit 在 answer 流、card 在 reasoning 流"不会拼成 credit card 误报；不透明推理（signature/redacted_thinking/encrypted）则完全不扫描（测试 891-915）。

评估器侧：`StreamingEvaluator` trait（policy/mod.rs:461-471）单方法 `evaluate(window)` 返回 `Blocked` 与否，driver 拥有批处理与 overlap、evaluator 无状态（450-457 行注释钉死分工）。`ResponseGuardEvaluator`（streaming_guardrails.rs:123-188）复用普通响应 guard 的完整评估路径（`evaluate_streaming_response_window`，policy/mod.rs:681-713，把窗口包成 `TextResponse` 走 `apply_single_response_guard`），`Drop` 时按流内最严动作记一次 Prometheus 指标（139-143）；实时 WebSocket 连接上多响应共享 evaluator，日志用 `merge_most_severe_guardrails` 折叠成"每 phase×guard 一条、取最严"（policy/mod.rs:52-69），防长连接日志无限膨胀。

### 2.4 budget：nanodollar 定点 + 双方言 upsert

内存态 `BudgetCounter`（budget/mod.rs:29-39）：`amount`（Decimal 已确认用量）+ `pending`（Decimal 未落库增量）+ 固定窗口 `window_start/end`。`budget_id` 用长度前缀防拼接歧义：`api-key:{len}:{key}:{len}:{name}`（298-306）。窗口对齐 Unix epoch 而非首请求时刻（308-314 注释：1h 跟 UTC 整点、24h 从 UTC 零点、30d 是连续 30 天而非日历月，"deliberately avoid daylight-saving"）；无窗口预算用 `UNBOUNDED_WINDOW`（epoch 到 DateTime 上限的整毫秒，333-334）永不重置。

请求路径 `check`（436-489）：超额且 `onBudgetExceeded=Block` 才拦（474-486），并计算向上取整的 `retry_after` 秒数（479-485）；Audit 型只打 warn 日志。结算路径 `settle`（493-534）：USD 预算扣 `response.cost.total()`、Tokens 预算扣 `response.total_tokens`（496-499），usage 缺失只记 debug 不扣（500-509 注释在 Budget 结构 124-127："Requests with unavailable usage are logged but cannot be charged or blocked retroactively"）。

持久化是**双份 SQL 文件 + include_str!**（database.rs:16-19：sqlite/postgres 各一对 schema+upsert）。schema 唯一差异 INTEGER vs BIGINT；upsert 语义完全同构，唯一方言差是 `MAX()` vs `GREATEST()`（sqlite_upsert.sql:14 / postgres_upsert.sql:14）。核心是 `ON CONFLICT(budget_id)`（主键只有 budget_id，窗口列随行原地更新，sqlite_upsert.sql:3）：

- **同窗口累加**：`CASE WHEN excluded.window_start = window_start AND excluded.window_end = window_end AND excluded.unit = unit THEN used_amount + excluded.used_amount`（7-12 行）；
- **跨窗口覆盖**：CASE ELSE 分支直接 `excluded.used_amount`（13 行）——新窗口从零开始；
- **陈旧窗口防护**：`WHERE excluded.window_end >= budget_usage.window_end OR excluded.window_end - excluded.window_start <> window_end - window_start`（17-18 行，注释："Ignore stale writes from an older window, but let a reconfigured window length replace the row"）——慢 worker 写旧窗口会被整个 UPDATE 丢弃，但"终身预算改成滚动窗口"这类配置变更允许覆盖。

`flush`（database.rs:155-258）流程：snapshot 非零 pending → USD 乘 `NANODOLLARS_PER_USD=10^9` 取整成 i64（179-186，回读时 `Decimal::new(x, 9)` 复原精度，196-199）→ 事务内逐条 upsert → **只减成功落库的份额**（244-254，窗口若在 flush 期间翻滚则不减）→ 重读全表 `reconcile` 多 worker 并发写的总额（255-256，281-312 的 reconcile 实现：行过滤条件要求窗口未过期+rolling 相同+unit 相同，否则内存退化为 `amount = pending` 防脏数据）。后台任务是 `Arc::downgrade` 弱引用 + `tokio::time::interval(5s)`（77-90），策略被 Drop 后任务自动退出，不会吊住进程。

### 2.5 log_store：21 列主表、COPY 批写、直方图聚合

Postgres 主表 `request_logs` 由 0001 迁移建 21 列（id/started_at/completed_at/duration_ms/trace_id/span_id/http_status/error/gen_ai 四列/input-output-total tokens/cost/agentgateway_user/group/user_agent_name/has_payload/attributes_json，awk 实测 21），0002 再加 5 个分析列（cache_read/cache_creation/reasoning tokens、time_to_first_token_ms、time_per_output_token_ms），共 26 列；prompt/completion 全文拆去附表 `request_log_payloads`（0001 第二张表，log_id 主键 + `ON DELETE CASCADE`），主表只留 `has_payload` 布尔——热查询扫窄表、大对象按需 JOIN（postgres.rs:630-637 的 `SELECT_LOGS` 就是 LEFT JOIN）。另有 7 个针对 completed_at/status/provider/model/user/group/user_agent 的复合索引（0001 尾部）。

写入路径是**单 OS 线程 + crossbeam 无界队列**：`LogStoreWorker::work` 自建 current-thread tokio runtime（log_store.rs:216-230），`work_async` 循环先阻塞 `recv()` 一条，再 `try_recv()` 攒批至 16384（238-291；批大小可用环境变量 `REQUEST_LOG_STORE_BATCH_SIZE` 覆盖，309-323）；任何查询消息（Search/Get/Tail/AnalyticsSummary）到达时**先 flush 再答**保证读己之写（342-361）。Postgres 批写用两次 `copy_in_raw`（postgres.rs:42,53）：主表与 payload 表各一条 COPY 语句（616-628），文本协议拼行送 STDIN，单事务提交（57 行）——COPY 绕过逐条 INSERT 的 SQL 解析开销，是 pg 批量导入的最快通道（代码注释：postgres.rs 无此注释，"最快"为推断；log_store.rs:159 倒有实测依据——"Testing shows this to achieve a pretty good throughput for both postgres and sqlite"）。SQLite 无 COPY，退化为 `QueryBuilder::push_values` 多值 INSERT 按 1150/8000 分块（sqlite.rs:22-23, 96-107；1150 是绕 SQLite 变量数上限的取值，推断自数值远小于 32766 上限的保守留白）。积压可见性：全局 `REQUEST_LOG_STORE_BACKLOG: AtomicUsize` 计数（log_store.rs:20），flush 时打 count/backlog/throughput（366-386）。

分析聚合：`analytics_summary`（postgres.rs:102 起）按 `FLOOR((EXTRACT(EPOCH FROM completed_at) - from) / bucket_seconds)` 分桶，SELECT 列是 16 项指标的共享片段 `ANALYTICS_TOTALS_SELECT`（log_store.rs:557-572，双方言通用，含 errors/ttft_requests/generation_tokens/cache 分桶等）；TTFT 与出词速率两个直方图维度用**代码生成 CASE SQL**：`histogram_bucket_sql`（545-553）按边界数组 `[0,100,250,500,1000,2000,5000,10000,30000,60000,120000,300000]`（536-538）生成 `CASE WHEN value < 上界 THEN '下界'` 链，`GroupByField::Ttft/OutputTokensPerSecond`（521-532）注释明确"the group value is the bucket's lower bound"，非流式请求归 null 桶。桶参数 `analytics_window`（869-902）默认 24h/96 桶。

## 三、外部连接

**上游：LLM 翻译引擎（L11，explain-07 的主角）**。请求侧入口在 llm/mod.rs:2305：`original_format.supports_prompt_guard()` 才挂 guard（Detect 透传格式不检）；响应侧缓冲路径 2653-2680 走 `apply_response_prompt_guard`（整包检查后 `managed_body.replace_content` 换体）；流式路径 3128-3150 的注释是本篇最重要的接线契约——"Build evaluators **before** format translation so guardrails run against **translated** SSE output, not raw upstream bytes. Applying them before translation silently breaks Bedrock (AWS Event Stream is binary, not SSE)"。随后 3202 行 `transform_stream(|b| GuardedSseBody::new(b, evaluators, buffer, None))` 把守卫体包在**翻译后的**流上；`None` 是因为 logger（AmendOnDrop）已由翻译体持有，注释 3199 行明说"pass None to avoid double-logging"。

**CEL 栈（L10）**：policy 的 webhook headers 用 `Arc<cel::Expression>` 计算（mod.rs:2253），评估时拿 `cel::RequestSnapshot` 原始请求快照（webhook/mod 两处）；拒绝详情 `cel::GuardDetail`（assessments JSON）经 `record_guardrail` 进访问日志（34-50）。guardrail 结论同时进 Prometheus：`GuardrailAction` 枚举**按严重度排序**（metrics.rs:61-71 注释 "Ordered by severity so guards can retain the most severe result"：Allow < FailOpen < Audit < Mask < Reject），`guardrail_checks` Family 按 phase×action 打标签（301 行）。

**下游：UI（L15）**。`ui/src/pages/analytics/AnalyticsCharts.tsx` 消费 analytics_summary 的返回：`bucketSeconds`（403 行参数）做毫秒换算（413 行），`totals` Map 按 group key 归并成时间序列（446-492 行）画折线/柱状——TTFT、出词速率、cache 读写 token 等列的消费端全在这张图。budget 的 status.rs 则给管理界面/API 出 `BudgetStatusResponse` 快照（status.rs:54-103：used/remaining/exceeded + 窗口信息，过期计数器按零用量上报）。

**storage（L07/L08 边界）**：budget 与 log_store 都从 `crate::database::DatabasePool`（Sqlite/Postgres 二态枚举）取池；log_store.rs:28-30 注明 request log 与 config store 配置相同时**共享一个连接池**（`setup_with_pool`，68-85）。

## 四、数据流：一条流式 LLM 响应的三线并行

以"客户端 → 翻译引擎 → 上游模型"的一条流式请求为例（行号链）：

1. **请求进门**：API key 认证匹配出 `MatchedBudgets`；budget policy `apply()`（budget/mod.rs:543-567）先 `check` 未超限，把 `BudgetSettlement` 挂上 `log.budgets`（561 行）。同阶段请求 guard 跑 `apply_prompt_guard`（policy/mod.rs:979-1013）：逐 guard 评估（regex 本地、云端出网），首个 Reject 直接返回自定义 403。
2. **响应回流**：上游 SSE 字节流先解压（llm/mod.rs:3105）、再由翻译层转成目标格式流；guardrail evaluators 在翻译**之后**构建（3128-3150），`GuardedSseBody` 包住翻译流（3202）。每 1024 文本字节扣帧评估一次：窗口=256 字节 overlap+本批，六类 kind 走同一 `StreamingEvaluator` 接口；通过→放行扣住的帧，拦截→丢帧+注入 `guardrail_blocked` 错误事件，metrics/log 按"每 guard 取最严动作"折叠。
3. **计费结算**：翻译体持有 `AmendOnDrop`（3152；结构 3524-3530），流式 usage 边收边 `update` 回 `LLMInfo`；流结束 Drop（3575-3583）触发 `report_usage`。请求收尾统一在 log.rs：`LLMContext` 组装后**循环结算所有挂账预算**（1465-1467 `for budgets in std::mem::take(&mut log.budgets) { budgets.settle(...) }`）——USD 预算按 catalog 价目表算 cost，Tokens 预算按 total_tokens，入内存 amount+pending。
4. **异步落库**：同在请求收尾，`log_store::emit(PendingRequestLog{...})`（log.rs:2242-2247）把记录推进无界队列即返回（不阻塞请求路径）；后台线程攒到 16384 条或下一条消息到达，Postgres 双 COPY 单事务写入 / SQLite 分块多值 INSERT。guardrail 结论此时已随 `record_guardrail` 写进 `GuardrailLog`（最终序列化进 attributes_json 的 `agw.ai.guardrails`，log.rs:2001-2002）。5 秒后 budget 后台 flush 把 pending 增量 upsert 进 `budget_usage` 表，供重启预载（database.rs:69-75 `read_persisted`+`reconcile` 在 initialize 时回灌内存）。

即：**guardrail 是同步内联的（看得见的延迟）、budget 扣账是内存同步+落库异步（秒级最终一致）、log_store 是全程异步（不挡请求）**——三档一致性换三档延迟预算。

## 五、设计决策

- **流式边界拦截 vs 全量缓冲**：模块文档（streaming_guardrails.rs:12-15）直接给了答案："Content flushed by earlier passing windows cannot be retracted — an accepted accuracy/latency tradeoff"——不做全量缓冲（那会毁掉首字延迟），接受"先前窗口已放行内容无法召回"的精度损失；跨窗口模式靠 256 字节 overlap 兜底，超过 overlap 跨度的模式可能漏检（17-18 行明示）。阈值 1024 的取舍注释在 41-43 行："Larger values reduce guardrail API calls but increase time-to-first-byte and the amount of content discarded on a mid-stream block"。**先翻译后守卫**（llm/mod.rs:3128-3131）是第二个关键序：守卫必须看到翻译后的统一 SSE，否则 Bedrock 二进制 Event Stream 直接不可解析。
- **PII 检测后改写还是只检测**：源码答案明确——**默认改写**。`Action` 枚举默认值就是 `Mask`（policy/mod.rs:2430-2433 `#[default] Mask`），builtin 模式命中后整段替换 `<EMAIL_ADDRESS>`/`<SSN>` 类占位符（1873）；只有 streaming 路径例外：`apply_single_response_guard` 在 streaming 时收到 Mask 结果按 Allow 放行（1983-1986 注释 "Streaming cannot apply masking"），realtime 路径同样"Masking outcomes are treated as pass"（583-585）——因为已发出的帧无法原地重写。**改写是尽力而为，检测永不缺席**。
- **budget 5 秒批 flush 的取舍**：每请求一次 DB 写在 LLM 网关的 QPS 下不可行，5 秒窗口意味着崩溃最多丢 5 秒扣账（进程重启后从库里回灌，丢失的 pending 无法追回——源码无此句，推断自"pending 只在内存"的结构事实）；换来的是 upsert 冲突域极小（同 budget 同窗口才累加）。`Arc::downgrade` 弱引用定时器（database.rs:77-90）保证 flush 任务不成为进程退出的悬挂引用。nanodollar 定点（mod.rs:23）把浮点 cost 换成 i64 存储，是支付系统的标准手法；SQLite/Postgres 双份 SQL 文件而非运行时方言分支，是把"两个数据库的行为差异"固化成可 review 的静态文件（16-19 行 include_str!）。
- **failClosed 默认 + FailOpen 显式**：三云/moderation/webhook 都可配 `failureMode: failOpen`（2230-2238），FailOpen 放行时指标记 `FailOpen` 而非 `Allow`（363-365 注释："must be recorded as FailOpen, not Allow"）——审计上可区分"检查过且通过"与"检查挂了放行"。
- **21 列主表 + payload 附表**：分析查询永远不碰大 JSON 列（全文在附表），这是"日志库既是审计源又是分析库"的双重角色下的列布局决策；`has_payload` 布尔留在主表做过滤（LogFilters 有该过滤项，log_store.rs:455）。

## 六、新人提示

1. **加一种 guardrail kind**：改四处——`RequestGuardKind`/`ResponseGuardKind` 加变体（policy/mod.rs:2128/2545）+ `name()` 加短名（2143-2153）+ `evaluate_single_request_guard` 加分发臂（1047-1100）+ 新建 provider 文件（参考 azure_content_safety.rs 362 行的"结构体配置+端点拼接+响应解析"三段式，记得带 `failure_mode` 字段并入 2115-2124 的 `failure_mode()` match）。若要流式可用，无需另写 evaluator：`ResponseGuardEvaluator` 自动复用缓冲路径的评估逻辑（streaming_guardrails.rs:151-187 调 `evaluate_streaming_response_window`）。若只是加本地 PII 模式，更轻的路子是给 `Builtin` 加变体（2201）+ pii/mod.rs 加 static——顺带可以把沉睡的 UrlRecognizer 接线复活（见勘误 2.2）。
2. **查预算表**：`SELECT budget_id, window_start, window_end, unit, used_amount, updated_at FROM budget_usage WHERE window_end > (strftime('%s','now')*1000)`（SQLite 毫秒时间戳；Postgres 同构）。注意 used_amount 对 USD 行是 nanodollar（除 1e9 才是美元），对 Tokens 行原值；要人读状态直接打 `/budgets` 类 status 接口（status.rs:54 返回已换算字符串）。
3. **调试日志落库**：`REQUEST_LOG_STORE_BATCH_SIZE=1` 跑（每条即 flush，log_store.rs:161 环境变量），再 `SELECT ... FROM request_logs LEFT JOIN request_log_payloads ...` 看全文；guardrail 命中记录在 `attributes_json` 的 `agw.ai.guardrails` 键（log.rs:2001）。流式守卫行为看 Prometheus `guardrail_checks{phase,action}`（metrics.rs:301），流结束才落最终最严值（Drop 钩子，streaming_guardrails.rs:139-143）。
4. **坑**：① scope 显式空数组会在**反序列化阶段**报错而非静默禁用（2082-2093），报错文案容易被误当 bug；② streaming 响应 guard 只支持 messages scope，配置带其它 scope 直接 validate 失败（329-330）；③ webhook guard 不支持自定义 scope，永远检 systemPrompt+messages（2096-2111 硬校验）；④ budget 必须配 `config.database`，否则 register 直接报错（400-403，测试 574-596 锁死该行为）；⑤ GuardedSseBody 的 eval_threshold=1024 是"文本字节"不是"SSE 帧数"，调优时别看帧；⑥ 长连接 realtime 的 guardrail 日志被折叠成最严重单条（55-69），别按"每事件一条"写告警规则。
