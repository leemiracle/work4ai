# 11 · extensionserver xDS 扩展：PostTranslateModify 编排与"控制 Envoy 而不 fork Envoy"

## 一、角色定位

`internal/extensionserver`（16 文件）实现 Envoy Gateway 的扩展 gRPC 服务：EG 在 xDS 生成管线的固定钩子点回调本服务，允许在集群/路由/监听器翻译完成后打补丁。这是全仓"深度介入 Envoy 配置而不 fork Envoy"的关键机制——AI Gateway 的 upstream ext_proc 过滤器、InferencePool 端点选择、MCP 回环监听器、流空闲超时全部经此注入。服务同时挂 gRPC 健康检查（extensionserver.go:101 Check 直接回 SERVING）；cmd/controller 与 aigw run（cmd/aigw/run.go:183）两个入口都起它，standalone 标志（:35）影响极小。配额注入的第五张脸（quota_ratelimit.go）已在 05 篇拆过，本篇讲其余四族钩子。

## 二、内部结构

**Server（extensionserver.go:29）**：内嵌 UnimplementedEnvoyGatewayExtensionServer；New（:51）解析 request-header-attributes 与限流服务地址；toAny（:118）统一 marshals 为 Any（type.googleapis.com 前缀 :123）。

**PostTranslateModify（post_translate_modify.go:113，1313 行文件的主体）**十步编排：①若快照里有 AI 集群则先解析 metadataForwardingNamespaces（:118-123，metadataForwardingNamespacesForSnapshot :587——按快照内 Gateway 反查 GatewayConfig 合并，mergeGateways 场景注释 :583-586）；②逐集群 maybeModifyCluster（:127）；③为 InferencePool 建 EPP 集群（:135）；④改 listener/routes 支持 pool（:142）；⑤applyStreamIdleTimeouts（:147）；⑥兜底补 `ai-gateway-extproc-uds` 集群（:153-206：STATIC+UDS Pipe 端点 :191-195、buffer 提到 50MB 注释 :177-181）；⑦maybeGenerateResourcesForMCPGateway（:209）；⑧插 header→metadata 过滤器（:212）；⑨配额注入（:218，05 篇）；⑩返回全量资源（:223）。

**集群名协议（:65 parseAIGatewayClusterName）**：只认 `httproute/<ns>/<name>/rule/<idx>` 或再加 `/backend/<idx>` 的 5/7 段形状（:67）；`hasAIGatewayClusterName`（:99）注释坦白这是短路不是过滤器——普通 HTTPRoute 也长这样，真正判别靠后面 Get AIGatewayRoute（:340，NotFound 即跳过 :342-346）。

**maybeModifyCluster（:326，四职责注释 :310-325）**：endpoint 元数据是 workaround（注释引 EG#5523）、upstream ext_proc 过滤器（引 EG#5881）、header mutation、pool 特判。三分支盖满 LoadAssignment 形态：nil=EDS 场景只写集群级元数据（:368-384，注释里 TODO 直言 AWS 后端此时丢 VPCE 签名 host #902/#975）；指定 backendRef 则逐 endpoint 盖名+priority（:385-395）；默认分支按非零权重后端顺序对齐 endpoint 组——lbEndpointIndex 失配的长注释（:405-424）解释"CR 与 EG 翻译差一个 revision"时如何安全断尾。**upstream ext_proc 过滤器构造（:481-516）**：ReceivingNamespaces 收自家元数据命名空间（:483-485）、ForwardingNamespaces 按声明（:487-491）；RequestAttributes 四条元数据路径（:493-498）正是 01 篇 upstream filter 判别后端的数据来源；ProcessingMode 注释（:501-506）解释 RequestHeaderMode=SEND、RequestBodyMode=NONE（router filter 已把原文握在内存）、响应全 SKIP（响应在 router 层处理避免重试纠缠）；MessageTimeout 10s（:508）。**过滤器插入次序（:553-573）**：先删可能残留的旧过滤器（:476-479 注释：EG 每次重建，不期待带着我们的过滤器来），再插到 upstream_codec 之前（最后一格永远是编解码器，空链则补造 :560-572）。header_mutation 过滤器用 `%DYNAMIC_METADATA%` 从元数据回填 content-length（:527-543）——body 被改写后长度对不上的兜底。

**applyStreamIdleTimeouts（:230）**：遍历 route 配置，`maybeSetStreamIdleTimeout`（:248）解析路由名（:256-263）→按 ObjectKey 缓存查 AIGatewayRoute（retrieveAndCacheAIGatewayRoute :294，NotFound 缓存 nil 防风暴）→规则仍在则把 GetStreamIdleTimeout 写进 `retry_policy.per_try_idle_timeout`（:285-289）——注释 :244-247 讲透机制：空闲超时触发 Envoy reset 上游流，配合重试策略在首字节前 failover。

**Post 路由/集群钩子**：PostRouteModify（post_route_modify.go:21）只管 InferencePool——至多一个（:39-41），关 AutoHostRewrite（:60-62，EPP 用 `x-gateway-destination-endpoint` 头指定目的地不能被改 host），无 EndpointPickerRef 则原样放行（:48-54 注释：v1.5.0 起可选，宁可不配也不 panic）；PostClusterModify（post_cluster_modify.go:32）把 pool 集群改 ORIGINAL_DST+CLUSTER_PROVIDED（:80/:83）、LbConfig 用头选端点（:90-94）、清 EDS（:102），appProtocol h2c 需自解协议选项（:104-112 注释：pool 后端是 Pod 不是 Service，EG 无 appProtocol 线索）。inferencepool.go 补齐胶水：元数据键 `per_route_rule_inference_pool`（:41）、六段编码 ns/name/svc/port/bodyMode/allowOverride（:101-129 反解、:174-183 正写）、EPP 专用 STRICT_DNS 集群（buildClustersForInferencePoolEndpointPickers :186、单集群构造 :204，默认端口 9002 :47）、行为开关藏在 InferencePool 注解（:50-52 两个 annotation 键；bodyMode duplex/buffered 解析 :353-373）。

**mcproute.go（MCP 回环）**：maybeGenerateResourcesForMCPGateway（:40）先改主 listener 路由再搬家（:46 注释：顺序敏感）；createRoutesForBackendListener（:229）把每后端 HTTPRoute 深拷贝（proto Marshal/Unmarshal :237-247）搬进新配置；createBackendListener（:72）在 127.0.0.1:MCPBackendListenerPort 起独立 listener（:151-154），header_to_metadata 规则**排序后**生成（:104-107 注释：map 遍历序不稳定会白白 bump xDS 版本导致 listener 反复重建）、内部头转元数据后删除（:118）；maybeUpdateMCPRoutes（:172）把 trusted shim 的动态元数据渲染成头给纯 HTTP 的 mcpproxy（dynamicMetadataHeader :214-223，OVERWRITE+KeepEmptyValue 防客户端伪造）；主路由 rule/0 的 dummy IP 集群被整体换成 127.0.0.1:MCPProxyPort（modifyMCPGatewayGeneratedCluster :280-315）；extractMCPBackendFiltersFromMCPProxyListener（:337）把每后端过滤器从主 listener 抽走搬进回环 listener，access log 取第一份的长论证注释（:322-336：同 Gateway 共享 EnvoyProxy 基础设施故配置必然一致）。

## 三、外部连接

- **internalapi**：集群/endpoint 元数据路径常量（RequestAttributes :493-498）、MCP 端口与前缀（:151-153/:176/:235）、EPP 头键（post_cluster_modify.go:93）全在共享契约包（04 步暗线）。
- **extproc**：RequestAttributes 与元数据是 01 篇 upstream filter 判别输入；forward_proxy.go 按同一 AIGatewayRoute 决定是否给集群包 CONNECT 代理隧道（:451-455）。
- **Gateway API Inference Extension**：InferencePool 的 unstructured 解析（inferencepool.go:55-86）、EPP 集群与元数据往返。
- **上游 EG**：两个 issue 引用（#5523/#5881）是本层存在的临时性理由——上游解决后对应 workaround 应删。

## 四、数据流

一次 xDS 翻译周期：EG 把 IR 译成 Cluster/Listener/RouteConfiguration → gRPC 调 PostTranslateModify → 本服务按名字认领 AI 集群、盖元数据、插 upstream 过滤器、补 UDS 集群 → 有 MCPRoute 则重构监听器拓扑（回环 listener+路由搬家）→ 有 pool 则改 ORIGINAL_DST+建 EPP 集群 → 配额注入（05 篇）→ 返回补丁后资源，EG 继续下发给 Envoy。请求侧闭环：Envoy 按路由选集群→upstream ext_proc 从 endpoint 元数据读到 backend 名（01 篇 server.go:411）→完成定向改写。

## 五、设计决策

1. **不 fork 的代价**：集群名 5/7 段协议、HttpProtocolOptions 重建行为都是 EG 的内部约定，post_translate_modify.go:158/:172/:178 三处贴上游源码链接钉版本——EG 升级是本层最脆的时刻，测试（post_translate_modify_test.go）就是迁移指南。
2. **确定性优先**：删旧再插（:476-479）、header_to_metadata 排序（:104-107）都在对抗"xDS 版本无谓 bump→Envoy 换 listener 排空连接"这类隐性抖动。
3. **注解当逃生舱**：EPP 的 body mode/allow override 不进 CRD 而挂 InferencePool 注解（inferencepool.go:50-52）——InferencePool 是上游 CRD，本仓无权扩 schema，注解是唯一合法频道。
4. **revision 差容忍**：lbEndpointIndex 断尾（:405-424）与 ruleIndex 越界守卫（:276-278）都假设"EG 翻译的是稍旧的期望状态"，宁可等下一轮补齐也不 panic。
5. **TODO 即路线图**：AWS VPCE 丢失（:374-375）、SecurityPolicy 精确目标（mcproute.go:185）等 TODO 注释诚实标注已知缺口。

## 六、新人提示

改钩子先读 post_translate_modify.go:104-225 的编排注释再定位分步函数；测试 post_translate_modify_test.go/mcproute_test.go/inferencepool_test.go 全表驱动，加场景即加行。排障：config_dump 看集群是否带 ext_proc 过滤器与元数据、listener 里找 `aigateway-mcp-backend-listener`。坑：MCP 搬家必须"先改路由再抽过滤器"（mcproute.go:45-46 注释），顺序颠倒会把 authn 过滤器一起搬走；集群名解析失败只 Info 不报错（:329-330），"AI 后端没生效"别只盯 error 级日志。
