# 06 · MCP 网关与 A2A 适配：agent 协议的南北向闸门

> 行号锚均相对 `crates/agentgateway/src/`（仓根 `/usr-data/data2/repos/aaif-projects/repos/agentgateway`），写盘前已 sed/grep 逐条核实。图谱定位：16 层架构 **L09「MCP 网关与数据面配置类型」**（251 节点，knowledge-graph.json）。

## 角色定位（L09）

`src/mcp/` 是 agentgateway 的招牌能力所在：它不是又一个 MCP server 或 client SDK，而是把 MCP 流量当作一等公民做**会话级治理**的网关——客户端只面对网关一个 MCP endpoint，网关在南向维护到任意多个上游 MCP server 的连接，在中间完成认证、鉴权、工具级 guardrails、遥测与协议版本协商。全模块 14 个源文件（不含测试与 `guardrails/`、`upstream/` 子目录），入口 `mcp/mod.rs`（874 行）负责公共类型与错误映射，`mcp/router.rs` 的 `App` 持有全局 `Stores` 与 `Arc<SessionManager>`（router.rs:26-29），是整个数据面的锚点。

与之并列的 `src/a2a/`（354 行）是东西向的 A2A 协议适配器：它不做代理路由，只在 backend HTTP 过滤器链的末端对 A2A 流量做两件事——agent card 的 URL 改写（让客户端拿到指向网关的地址）与 JSON-RPC 响应的遥测提取。两者合成 agent 协议的"南北向闸门"：MCP 管工具与资源的会话，A2A 管 agent 之间的消息。

差异化在于治理粒度：普通反代只能看到 HTTP，而这里 `MCPInfo`（mod.rs:514-550）把每个请求解析成 `method_name/session_id/target/tool{target,name,arguments,result,error}/task` 等字段供 CEL 策略消费，工具调用参数与结果都被捕获进访问日志与策略上下文（mod.rs:752-777）。

## 内部结构

**1. 路由入口（router.rs）。** `App::serve`（router.rs:70）先按 target 逐个合并 backend/sub-backend 策略（router.rs:79-119），然后依次执行：DNS rebinding 防护（router.rs:141-145）、CEL 表达式注册与请求体缓冲、认证（router.rs:159-163）、最后按路径分流——`/sse` 走遗留 SSE 传输（router.rs:174-177），其余全部交给 `StreamableHttpService`（router.rs:194-199），`stateful_mode` 直接来自 backend 配置。

**2. 会话管理（session.rs）。** `SessionManager`（session.rs:880-884）持有 `RwLock<HashMap<String, SessionEntry>>`，懒启动 idle reaper 后台任务（session.rs:899-903），每 30 秒清一轮（SESSION_REAP_INTERVAL，session.rs:57）。会话 ID 是 UUID v4（session.rs:886-888），但 initialize 之后会被替换为**编码后的持久化会话状态**（session.rs:528-543）：把每个上游的 session id 打包成 `SessionState::MCP` 用 base64/AES Encoder 编码——网关重启或本地实例切换后，`get_or_resume_session`（session.rs:926-983）能解码出上游会话并重建连接，恢复时严格校验 backend id 与 target 条件匹配（session.rs:932-944）。无状态请求也复用 `Session` 结构，但 `synthetic=true`，该 ID 既不注册也不外发（session.rs:39-46）。

**3. 传输层（streamablehttp.rs）。** `handle_post`（streamablehttp.rs:103-215）先做协议卫生检查：Accept 必须同时含 JSON 与 text/event-stream（streamablehttp.rs:108-120）、Content-Type 必须 JSON，再解析 body、校验协议版本头。会话路由三分支：无状态模式直接 `serve_stateless`（streamablehttp.rs:163-165）；带 `Mcp-Session-Id` 头则查找/恢复会话（streamablehttp.rs:172-184）；无头且非 initialize 报 `MissingSessionHeader`，是 initialize 则建会话并把新 ID 写回响应头（streamablehttp.rs:190-214）。无状态路径若上游可能持有连接状态（stdio/SSE），响应体挂 drop guard，在客户端真正收完后异步清理 stdio 进程（streamablehttp.rs:240-248）。

**4. 协议双代际。** `is_modern_version`（mod.rs:92-96）以 2026-07-28 为界：modern 客户端用 `server/discover` + 每请求 `_meta` 协商，无会话；`REMOVED_METHODS_2026_07_28`（mod.rs:102-108）列出对 modern 移除的五个方法（initialize/ping/setLevel/subscribe/unsubscribe），`validate_request_protocol`（streamablehttp.rs:474-533）据此在分发前给出 404。

**5. 上游连接组（upstream/mod.rs）。** `Upstream` 枚举四种传输（upstream/mod.rs:208-212）：`McpStreamable`/`McpSSE`/`McpStdio`/`OpenAPI`。`new_for_request`（upstream/mod.rs:498-540）按 target 数量决定 `is_multiplexing`，单 target 且非 `prefixMode: always` 时记录 `default_target_name`（upstream/mod.rs:504-506）。`setup_upstream`（upstream/mod.rs:641-742）中 SSE 默认路径 `/sse`（upstream/mod.rs:646-649）、streamable HTTP 默认 `/mcp`（upstream/mod.rs:670-673）、stdio 走 `TokioChildProcess`（upstream/mod.rs:690-716，Windows 上先用 `which` 解析可执行文件）、OpenAPI 由 schema 解析出工具集（upstream/mod.rs:717-721）。`has_connection_teardown` 明确 stdio/SSE 持有每连接状态（upstream/mod.rs:608-613）。

**6. 工具聚合与重写（handler.rs）。** 多路复用的命名空间约定：工具/prompt 名用 `_` 连接（DELIMITER，handler.rs:37；`resource_name` handler.rs:69-75），资源 URI 与 task id 用 `+`（`resource_uri` handler.rs:158-167 同时接受层级与 opaque URI；`task_id` handler.rs:204-211）。反向解析 `parse_resource_name` 按 `_` 切分（handler.rs:436-449）。`prefixMode: never` 时进入 `resolve_unprefixed`（handler.rs:471-514）：并发向所有上游翻页 list 直到找到唯一 owner，多 owner 报错（handler.rs:488-494），探测请求用 `agw-resolve-{seq}` 独立 ID 避免上游看到重复 ID（handler.rs:527-535），最多 64 页防死循环（handler.rs:529-530）。`merge_tools`（handler.rs:802-849）对 fanout 结果做三件事：按 target 去重、RBAC 过滤不允许的工具（handler.rs:822-831，挂在 `TOOLS_LIST` 方法上）、再重命名加前缀（handler.rs:833-836）。`merge_initialize` 取所有上游的最低协议版本（handler.rs:884-899）；`merge_discover` 反向取支持版本交集（handler.rs:944-961）。

**7. A2A 双形态解析（a2a/mod.rs）。** `classify_request`（a2a/mod.rs:17-62）把请求分成三类：GET `/.well-known/agent.json`（旧）或 `agent-card.json`（v0.3.0+，a2a/mod.rs:21-26）为 AgentCard；POST JSON 为 Call（抽取 JSON-RPC method）；其余 Unknown。响应遥测 `ResponseInfo::from_json` 是 v0.3/v1.0 兼容的核心：v0.3 把 Task/Message 平铺在 `result` 上、用 `kind` 判别；v1.0 改为 `oneof payload` 嵌套在 `result.task`/`result.message` 且无 `kind`——代码先取平铺形态、取不到再回退嵌套形态（a2a/mod.rs:94-109），`task_state` 与 `context_id` 同样双路径回退（a2a/mod.rs:110-129）。测试 `test_apply_to_response_records_v1_nested_task_telemetry`（a2a/tests.rs:792 起）锁定了 v1.0 无判别字段的嵌套形态。

## 外部连接

- **北向（下游客户端）**：streamable HTTP POST/GET/DELETE（streamablehttp.rs:87-100）与遗留 SSE（`/sse` 路径，router.rs:174-177）。GET 事件流与 DELETE 会话都是 legacy-only，modern 版本直接拒绝（streamablehttp.rs:251-257、285-291）。
- **南向（上游 MCP server）**：四种传输的连接全部经 `McpHttpClient` 包裹 `PolicyClient`（upstream/mod.rs:651-660、675-684），即上游流量同样穿过 backend HTTP 过滤器链（backend auth、transformation、header modifier 等，见 httpproxy.rs:460-476 的链式 apply）。
- **guardrails 工具级拦截**：`mcp/guardrails/mod.rs` 的模块级文档（guardrails/mod.rs:1-10）钉死了两套语义——单目标方法（`tools/call` 等）在**上游原生命名空间**触发，处理器看到未加前缀的名字；fanout 方法（`*/list` 等）对合并结果只跑一次，名字是客户端视角。`Processor.methods` 支持精确/前缀/后缀/全量通配（guardrails/mod.rs:72-79）。请求相挂钩在 `authorize_with_ctx` 内联执行（session.rs:642-655 → handler.rs:743-800，含 `_meta` 从 extensions 暂时搬回 params 再复原的细节），响应相通过 `GuardrailsCtx`（handler.rs:1864-1870）在 `respond_with_guardrails` 包裹整个流（handler.rs:1400-1407）。
- **RBAC 与工具隐藏**：鉴权失败刻意报 `Unknown {kind}: {name}` 而非"未授权"——注释明言要隐藏工具存在性（mod.rs:169-171）；`tools/list` 阶段就按策略把工具从清单里滤掉（handler.rs:822-831）。
- **A2A 挂点**：请求侧在 backend 过滤器链最末端、紧邻真正发请求之前（httpproxy.rs:481-496，在 url_rewrite/request_redirect 之后）；响应侧在 LLM provider 处理之前（httpproxy.rs:3303-3312）。agent card 改写区分两代：v1.0 遍历 `supportedInterfaces` 数组逐条重写 URL（a2a/mod.rs:202-229），v0.3 改写顶层单一 `url`（a2a/mod.rs:230-232），两处都没有则报错（a2a/mod.rs:233-234）。

## 数据流：一个 `tools/call` 的完整回环

1. **入口校验**：客户端 POST JSON-RPC，`handle_post` 验 Accept/Content-Type（streamablehttp.rs:108-130）、解析 body、`validate_request_protocol` 校验版本头与 body 一致性（streamablehttp.rs:155-157），按会话头路由到已有会话或无状态会话（streamablehttp.rs:163-188）。
2. **会话分发**：`Session::send_internal`（session.rs:491）match 到 `CallToolRequest`（session.rs:620）。多目标 `prefixMode: never` 时先 fanout list 探测 owner（session.rs:628-634 → handler.rs:471-514），否则按 `_` 前缀切分出 `(service_name, tool)`。
3. **策略前置**：写遥测 `set_tool`/`capture_call_arguments`（session.rs:636-639）；把客户端看到的带前缀名**还原**为上游原始名（session.rs:640-641）；`authorize_with_ctx` 以 `TOOLS_CALL` 方法执行 RBAC + 请求相 guardrails（session.rs:642-655）。
4. **上行**：`send_single`（handler.rs:1369）查 `upstreams.get(service_name)`（handler.rs:1377），构造响应相 guardrails 上下文（handler.rs:1382），经 `generic_stream` 发往该 target 的专属传输（handler.rs:1385-1393）。
5. **回程改写**：响应流经 `rewrite_outbound_server_messages`（handler.rs:391-423）——资源 URI 加 `target+` 前缀、task id 加命名空间（handler.rs:400-402），并重写工具元数据中的 UI 资源 URI 且对它们跑 RBAC（handler.rs:404-421）。
6. **回环收尾**：流交给 `respond_with_guardrails`（handler.rs:1400-1407）执行响应相处理器并产出最终 HTTP 响应。特殊映射：被限流的 `tools/call` 不回 JSON-RPC 协议错误，而是转成 `isError` 的 CallToolResult，让 agent 循环继续运转（mod.rs:202-217、325-357；自定义 `-32003 RESOURCE_EXHAUSTED` 见 mod.rs:63）。

## 设计决策

- **MCP SDK 双版本并存的真身（勘误细化）**：任务书引 onboard 勘误说"rmcp 3.1.0 + legacy-rmcp 0.10.0 并存"。源码核实：运行时依赖只有一个 `rmcp = "3.1.0"`（Cargo.toml:125，[dependencies]）；`legacy-rmcp = { package = "rmcp", version = "0.10.0" }` 位于 **[dev-dependencies]**（Cargo.toml:206、230），注释说明因官方 SDK 删除了 SSE 传输（rust-sdk PR #562）而用旧版做**测试用 SSE client/server**（Cargo.toml:228-229），全仓使用点仅在 `mcp/mcp_tests.rs`（如 mcp_tests.rs:4880 的 `LegacyService` 类型）。即：双版本是测试基建，不进生产二进制——这比"并存"更精确。
- **工具名前缀重写的意义**：多上游聚合到一个客户端视图时必须有全局唯一命名空间。选 `_`（名字）与 `+`（URI/task id）两个分隔符并保留为保留字——target 名校验正则的注释明言"`+` 和 `_` 是保留 MCP 分隔符"（types/agent.rs:2006 附近的 MCP_TARGET_NAME_RE 与 2010 的 `validate_mcp_target_name`，上限 253 字符对齐 Gateway API SectionName）。资源 URI 加前缀还要兼容 opaque URI（`memo:insights`），`uri_scheme_prefix_len` 专门按 RFC 3986 识别 scheme（handler.rs:132-150）。
- **A2A 兼容两版的代价**：官方注释给出动机——"Prefer the flat v0.3 shape and fall back to the nested v1.0 shape so both spec generations populate"（a2a/mod.rs:98-99）。代价是每个遥测字段都要双路径取值（kind/state/contextId 各两跳），且 v1.0 无 `kind` 判别只能靠"哪个 oneof 分支非空"反推（a2a/mod.rs:107-109）。
- **FailClosed 默认**：任一 target 初始化失败或 fanout 中失败即整会话失败；FailOpen 则跳过失败者继续（mod.rs:44-53 注释）。GET 流有个专门补丁：FailOpen 下全部上游 GET 流消失时保持 SSE 连接打开，防遗留客户端紧密重连环（handler.rs:1498-1511，注释明言）。
- **版本协商方向相反**：initialize 合并取**最低**公共版本（handler.rs:884-899），discover 取**交集**（handler.rs:961）；单上游 discover 直通透传不翻译（handler.rs:928-941 注释）。推断：前者保旧客户端可用，后者让客户端精确知道可用集合。
- **`tools/list` 强制 `ttl_ms=0` + `CacheScope::Private`**（handler.rs:845-846）：注释说明缓存描述的是网关呈现的服务而非上游，网关路由配置可变，不允许客户端缓存。

## 新人提示

1. **接一个新 MCP server 的配置路径**：target spec 的 serde 键是 `sse`/`mcp`/`stdio`/`openapi` 四选一（types/agent.rs:2029-2045）；stdio 支持 `cmd/args/env/clearEnv`；`sse.path`/`mcp.path` 留空分别默认 `/sse`、`/mcp`（upstream/mod.rs:646-649、670-673）。target 名必须过 `validate_mcp_target_name`——小写字母数字加 `-`/`.`，**不能含 `_` 和 `+`**（它们是路由分隔符）。backend 级还有 `prefixMode`（Conditional/Always/Never，types/agent.rs:1902-1911）、`failureMode`、`sessionIdleTtl`（默认 30 分钟，mod.rs:55）、`stateful`。
2. **调试会话**：先看 `Mcp-Session-Id` 响应头拿会话 ID；`UnknownSession` 大概率是网关重启后会话未持久化（非 AES Encoder 时无 backend 绑定）或 target `condition` 集合变了（恢复校验在 session.rs:932-944，target-keyed 恢复严格要求数量与名字全匹配，handler.rs:653-680）。无状态模式下第一个请求不是 initialize 会得到 `MissingSessionHeader`（streamablehttp.rs:198-199）。
3. **坑**：①`prefixMode: never` 的每次 tool call 都可能触发全上游翻页 list（无缓存，TODO 在 handler.rs:469-470），上游多、工具多时延迟放大明显；②探测请求 ID 是网关自造的 `agw-resolve-*`（handler.rs:533-536），上游日志里看到别慌；③`dns_rebinding_protection` 默认关（types/agent.rs:1935-1940 注释明言：网关通常不是浏览器直连的 localhost MCP server）；④modern（2026-07-28+）协议下 GET/DELETE 会话端点直接 4xx，别按旧文档调；⑤guardrails 处理器看到的名字空间取决于方法类型（单目标=上游原生名，fanout=客户端视角名，guardrails/mod.rs:3-10），写 CEL 时别混。
