# 06 · openshell-supervisor-network：L7 逐协议执法的出站守门人

## 一、角色定位

`openshell-supervisor-network` 是沙箱内的出站网络栈。crate 文档（crates/openshell-supervisor-network/src/lib.rs:4-7）列明地盘："拥有出站代理、L7 执法、OPA 策略引擎、身份缓存、TLS 拦截与凭据注入；**产出**拒绝事件但不聚合（聚合归编排器）"。它解决的经典问题是：agent 沙箱不能靠 L4 黑名单保安全——HTTP 里的方法、路径、GraphQL operation、MCP 工具调用各有语义，必须在应用层逐请求裁决。核心立场是**默认拒绝**：`NetworkAction` 枚举（opa.rs:57-61）只有 `Allow`（端点+二进制被策略显式匹配）与 `Deny`（no matching policy）两态，没有第三态。

## 二、内部结构

**策略引擎（opa.rs，12284 行）**：名字叫 OPA，实现是内嵌 **regorus**（编译进二进制的 Rego 解释器，无 sidecar）。`BAKED_POLICY_RULES`（opa.rs:34）`include_str!` 固化 `data/sandbox-policy.rego`——裁决规则 `data.openshell.sandbox.allow_network`/`deny_reason`/`matched_network_policy` 写死在决策路径上，策略**数据**才热更新。`evaluate_network`（:517-556）持引擎锁评估，且先查 `fail_closed_reason`（:527-535）——引擎处于隔离态时**直接返回拒绝**，fail-closed 是一等状态。`NetworkInput`（:94-103）的 `cmdline_paths` 字段（:88-90 注释）专门捕捉"解释器是 exe、脚本是 cmdline"的场景（例：`/usr/local/bin/claude` 由 node 解释，`/proc/<pid>/exe` 看不到）——按 exe 归因会漏掉 agent CLI。热重载两入口：`reload_policy_and_middleware_from_proto_with_pid`（:744）与更根本的 `reload_configuration_from_proto_with_pid`（:757）——**策略+中间件+预备凭据作为同一代原子发布**（:749-756 注释：校验失败旧配置原封不动，credentials 提交回调被强制 infallible），`PolicyGenerationGuard` 保证一次请求从头到尾只见单一世代。

**L7 框架（l7/mod.rs，4527 行）**：三个横切枚举定基调——`TlsMode`（:71-80，默认 Auto 自动探测并透明终结 TLS；Skip=显式豁免做 mTLS 直通）、`CredentialSigning`（:83-95，SigV4 三态签名）、`EnforcementMode`（:103-110，**默认 Audit 观察不拦**、Enforce 才真拒绝——给迁移留安全缓冲）。`L7Protocol` 六协议（l7_validate.rs:94-101）：Rest/Websocket/Graphql/Sql/JsonRpc/Mcp。

**协议适配器**：`relay.rs`（12080 行）是总管，`relay_with_inspection`（crates/openshell-supervisor-network/src/l7/relay.rs:853）按协议分派，8KB 读前缓冲（:36）保住 pipelined 请求各自过策略（:864-867 注释）。`RelayOutcome`（crates/openshell-supervisor-network/src/l7/provider.rs:19-33）三态收尾：Reusable/Consumed/**Upgraded**（101 升级后溢出字节+permessage-deflate+子协议全带回，转 WebSocket 原始中继）。REST（rest.rs，10655 行）解析 HTTP/1.1 请求行+方法+路径+查询参数，处理 Content-Length/chunked 分帧，入口 `relay_http_request_with_resolver`（rest.rs:720）；GraphQL（graphql.rs:722 行）用 apollo_parser 真**解析**查询而非字符串匹配，产出 operation_type/name/fields/persisted-query 信息（:18-32），body 上限 64KB（:15）；JSON-RPC（jsonrpc.rs:2051 行）双模式（:34-41）：普通 JsonRpc 或 Mcp 深检（方法分类/元数据校验）；MCP（crates/openshell-supervisor-network/src/l7/mcp.rs:650 行）管协议修订版本选择，`mcp-protocol-version`/`mcp-method`/`mcp-name` 三个头（:13-15）必须与受检 body 一致，错配即 `McpProtocolVersionError`（:31-44，含 NotAllowed——修订版不在端点白名单）。SQL 尚未实现：`relay_with_inspection` 里 SQL 分支（crates/openshell-supervisor-network/src/l7/relay.rs:880 起）先过 `uninspectable_traffic_gate`（:888），Deny 即断流，未配中间件链才降级 passthrough 并发低危事件（:904）。

**凭据注入（token_grant_injection.rs，928 行）**：端点绑定的动态 token grant。`TokenGrantResolver` trait（:31-37）+ `SpiffeTokenGrantResolver`（:39）经 SPIFFE 身份换 provider token；`TokenGrantRequest`（:18-28）携带 token_endpoint/audience/scopes/grant_type。注入点在 HTTP 中继路径上（文件名即职责），配合 `build_credential_endpoint_mismatch_finding`（l7/mod.rs:38-67）——**凭据在未授权端点被使用直接产出 High 级 DetectionFinding**（OCSF 事件，DispositionId::Blocked）。`sigv4.rs`（585 行）另供 AWS SigV4 签名。

**代理层（proxy.rs，14996 行）**：透明 TCP 路径 `handle_transparent_tcp_connection`（proxy.rs:1066）先查 IP→意图映射（:1080 `lookup_intent`，查不到即拒），再 `authorize_egress_intent`（:3433/:3702 两处定义）做身份解析+OPA 裁决——`NetworkAction::Deny` 就地断连并发 DenialEvent（:1106 起）。身份解析放 `spawn_blocking`（:1100）因为要读 /proc。入口 PID 尚未出生也拒绝（:3466 "entrypoint process not yet spawned"）。另有 forward proxy 路径（:5172）与 `policy_dns/`（DNS 解析也按策略世代走，policy_dns/mod.rs 1414 行）。

## 三、外部连接

上游：`openshell-policy`（L7Protocol、端点语义校验）、`openshell-core`（DenialEvent、endpoint_status、mcp 版本工具、secrets 的 SecretResolver 与凭据标记重写）、`tower-mcp-types`（MCP 检查）、`aws-sigv4`、apollo_parser、regorus。下游：supervisor 编排器（run.rs 组装、聚合拒绝事件）；网关经 ConnectSupervisor 下发新策略触发热重载；OCSF 事件汇入遥测线。

## 四、数据流

workload connect → seccomp broker（openshell-sandbox）→ 代理（透明/转发路径）→ 身份解析（/proc exe+cmdline+祖先链）→ OPA regorus 裁决（数据=当前世代策略 JSON，规则=baked rego）→ Allow 则 TLS 终结（Auto）→ L7 中继逐请求解析（REST/GraphQL/JSON-RPC/MCP）→ 方法/路径/operation/工具调用再过策略+中间件链 → token grant 注入+SigV4 签名 → 上游；任何一环 Deny → 断流+DenialEvent+OCSF 事件。

## 五、设计决策

1. **规则内嵌、数据热更**：Rego 裁决规则编译进二进制，热重载只换数据+中间件+凭据——"换大脑"需要重新发版，攻击面小。
2. **世代原子性**：策略/中间件/凭据三者同世代原子切换，PolicyGenerationGuard 防止一个请求混用两代配置。
3. **cmdline_paths 归因**：解释器型 agent CLI 必须靠 cmdline 补盲，这是"claude 由 node 驱动"现实的直接建模。
4. **Enforce 前先 Audit**：默认观察模式让新策略先跑影子流量再收紧，误杀成本前置消化。
5. **不可检查即拒绝**：SQL 未实现但先过 uninspectable gate；凭据端点错配直接 High 级 finding。

## 六、新人提示

- 勘误：仓里没有独立 OPA 服务，opa.rs 是 regorus 内嵌实现；说"OPA sidecar"是错的。
- `EnforcementMode` 默认是 **Audit 不是 Enforce**（l7/mod.rs:106-108）——测试里忘了设 Enforce 会看到"违规放行"的假象。
- relay_with_inspection 的 SQL 分支"未实现"但**不可当绕过口**：无中间件链的 passthrough 会发 Low 级事件留痕（crates/openshell-supervisor-network/src/l7/relay.rs:903-907）。
- proxy.rs 3433 与 3702 两个 `authorize_egress_intent` 是不同 cfg 下的同名函数，grep 时注意区分。
- 拒绝事件的聚合不在这里——本 crate 只生产 `DenialEvent`（crates/openshell-supervisor-network/src/lib.rs:6-7），找聚合逻辑去 supervisor 编排器。
