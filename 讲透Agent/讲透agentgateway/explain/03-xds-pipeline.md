# 03 · xDS 下发链：控制面 IR 到数据面配置的 gRPC 大动脉

> 源码基线：`/usr-data/data2/repos/aaif-projects/repos/agentgateway/`。Go 侧 `controller/pkg/syncer/syncer.go`（962 行）+ `syncer/krtxds/xds.go`（1487 行）+ `krtxds/pushqueue.go`（123 行）+ `syncer/nack/publisher.go`（89 行）；Rust 侧 `crates/xds/src/client.rs`（862 行，crate 名 `agent-xds`）+ `crates/protos/`（12 个 proto + build.rs）；下游消费 `crates/agentgateway/src/state_manager.rs`、`store/binds.rs`、`store/control/mod.rs`。全文行号锚均经 sed/grep 逐条核实。
>
> **勘误（任务书 vs 源码，按源码为准）**：①任务书写 syncer.go 路径为 `controller/pkg/controller/syncer.go`——实际在 `controller/pkg/syncer/syncer.go`（`pkg/controller/` 下是 reconciler，见 01 篇）。②任务书把 `control/mod.rs` 称为"下游数据面消费"——它实际是 **gRPC 传输连接器**（`GrpcChannel` 实现 `agent_xds::ClientTrait`，control/mod.rs:284），真正的资源消费在 `state_manager.rs:69-77` 的 handler 装配与 `store/binds.rs:2350`/`store/discovery.rs:736` 的两个 `Handler` 实现。③"agent-xds client.rs"即 `crates/xds/src/client.rs`（Cargo.toml name = "agent-xds"），无单独 agent-xds 目录。

## 一、角色定位（16 层架构 L04↔L14 衔接；Go syncer 与 Rust AdsClient 隔着 proto 对望）

understand 图谱 16 层中，本链路横跨两层：**L04「控制面核心：reconciler 与 xDS 下发」**持有 syncer.go/krtxds/pushqueue/nack 全部节点；**L14「Rust 基础 crate」**持有 crates/xds（AdsClient）与 crates/protos（proto 契约与生成）。两层之间没有一行直接调用——唯一的交点是 `crates/protos/proto/` 下的 proto 文件：Rust 侧由 `build.rs` 用 protox+prost/tonic 编译（build.rs:5-16 列出 proto 清单，resource.proto 在 :14）；Go 侧由根目录 `buf generate --path crates/protos/proto/resource.proto`（Makefile:146）经 buf.gen.yaml 输出到 `api/`（独立 Go module `github.com/agentgateway/agentgateway/api`，api/go.mod:1）。同一份 resource.proto，两边各生成一份代码——这就是"隔着 proto 对望"的字面含义。

链路全景：K8s 资源经 translator 变成 IR（`ir.AgwResource`），Syncer 把 IR 集合注册成两个 xDS 类型（syncer.go:910-911），krtxds.DiscoveryServer 在 gRPC `DeltaAggregatedResources` 流上把变更推给每个网关实例（xds.go:331），Rust 侧 AdsClient 收流、调 handler 更新 store、回 ACK/NACK；NACK 被控制面转成 K8s Event 挂回 Gateway 对象（publisher.go:86）。它是整个系统的"自主神经"：策略变更到数据面生效，全程无人工介入。

## 二、内部结构（Go 三件套：集合注册/推送管线/nack 出口；Rust 一件套：AdsClient 主循环）

### 2.1 Go syncer.go：集合装配与 xDS 注册

`Syncer`（syncer.go:50）持有 `Registrations []krtxds.Registration`（:71）与 `NackPublisher`（:68）。装配主线 `buildResourceCollections`（:143）把 translator 产物层层 Join：binds/listeners/routes/policies/backends 五路汇成 `resources/AllResources`（:729），最后 `buildXDSCollection`（:901）注册两个 xDS 类型——`krtxds.Collection[Address, *workloadapi.Address]`（WDS，服务/工作负载地址，:910）与 `krtxds.PerGatewayCollection[agwir.AgwResource, *api.Resource]`（RDS，按 Gateway 切片，:911）。`setupSyncDependencies`（:914）把 `agwResources.HasSynced`、`addresses.HasSynced`、`NackPublisher.HasSynced`（:922-927）一起纳入等待清单；`Start`（:930）等缓存同步后 `s.ready.Store(true)`（:943）。注意 `NeedLeaderElection` 返回 false（:953-955，注释言明"runs on all pods"）——**每个控制器副本都serve xDS**，数据面可连任意副本。

### 2.2 krtxds/xds.go：delta DiscoveryServer

文件头注释自述血统：derived from istio/istio pilot/pkg/xds/delta.go，剥离 Istio 专属逻辑、建在 krt 生成器层上（xds.go:1-3）。

**集合→注册**：`PerGatewayCollection`（:142）把任意 krt 集合包成 `DiscoveryResource`——proto 内容经 `MessageToAnyDeterministic` 序列化后取 **xxhash 内容哈希的十六进制当版本号**（:154，注释："Content hashes remain stable across controller replicas"，多副本一致性靠内容寻址而非全局状态）。`RegisterBatch`（:171）监听集合变更，聚成 `PushRequest{ConfigsUpdated}` 塞进 `pushChannel`（:182）。内部键 `ResourceName()` 带 Gateway 前缀（:128-133），线上名 `XDSResourceName()` 不带——不同 Gateway 可有同名资源互不冲突。

**推送管线三级流水**：①`pushChannel`（容量 10，:224）→ `debounce`（:1057，env 可调 `KGW_DEBOUNCE_AFTER` 默认 10ms / `KGW_DEBOUNCE_MAX` 默认 1s，:201-215；触发条件"静默满 AFTER 或总延迟超 MAX"，:1082）合并事件 → ②`Push`（:1031）给所有连接 `pushQueue.Enqueue`（:1037）→ ③`sendPushes`（:981）受 `concurrentPushLimit` 信号量限流（:220，istio features.PushThrottle），逐连接起 goroutine 把 `Event` 投进 `con.PushCh()`，流已关则直接 `doneFunc()`（:1018-1024）。PushQueue（pushqueue.go:9）保证"同连接重复入队则 CopyMerge 去重"（:46-54）、"处理中新变更暂存、MarkDone 后重新入队"（:92-105）。

**连接主循环**：`DeltaAggregatedResources`（:331）→ `StreamDeltas`（:335）。门禁三连：`IsServerReady`（:745，所有注册集合已同步）不过直接拒绝（:344-346，注释引 istio#25495：防止缓存未热时下发空配置）；`WaitForRequestLimit` 防惊群（:354）；`authenticate` 取 mTLS 身份（:359）。然后 `go s.receiveDelta`（:375）单独读流，主循环等 `<-con.InitializedCh()`（:382）后进入**双 select**（:384-426）：第一个 select 只查请求（非阻塞 default），因为"请求优先级更高且往往是廉价的 ACK"（:385-387 注释）；第二个 select 同时等请求与推送事件——请求处理量约为推送 2 倍，防请求洪峰饿死推送（:402-405 注释）。`processDeltaRequest`（:526）→ `shouldRespondDelta`（:556）实现 xDS 协议的 ACK/NACK/过期 nonce/自发订阅变更全套规则：带 `ErrorDetail` 的请求先解析结构化诊断（:565），有错则记 `LastError`、发 NackEvent、**不响应**（:585-601）；nonce 不匹配是过期请求直接忽略（:641-644）；纯 ACK（订阅未变）也不响应（:689-690）。

**增量计算**：`GenerateDeltas`（:1193）两分支——请求驱动分支遍历集合全量 List、按 `IsForGateway` 过滤、`InitialResourceVersions` 版本相等的跳过（:1203，断线重连只补差量）、订阅集合里已不存在的就是删除（:1196-1208）；推送驱动分支只看 `ConfigsUpdated` 键，PerGateway 类型做"无前缀+本 Gateway 前缀"双键查找（:1218-1224），查不到即删除（:1237-1239）。

### 2.3 nack/publisher.go：把 NACK 变成 K8s Event

`Publisher`（publisher.go:36）持 EventRecorder 与 Gateway informer 缓存。`PublishNack`（:63）/`PublishWarning`（:68）最终 `publish`（:72）：按 NACK 里的 Gateway 名查缓存（:73），组装 ObjectReference 后 `eventRecorder.Event(..., EventTypeWarning, reason, message)`（:86）。事件原因两个常量：`AgentGatewayNackError`/`AgentGatewayConfigWarning`（:23-24）。`NackPublisher.HasSynced` 进 Syncer 等待清单（syncer.go:925）——NACK 出口自身也是就绪依赖。

### 2.4 Rust crates/xds/src/client.rs：AdsClient 双向流主循环 + 就绪门闩 + 指数退避

**主循环**：`run`（:583）无限循环递增 connection_id；`run_internal`（:595）建 100 容量 mpsc 请求通道（:596），把 `state.known_resources` 里记的"已知资源名→版本"填进初始请求的 `initial_resource_versions`（:604-614，断线重连协商差量的客户端半边），`delta_aggregated_resources` 建流（:642），解码上限 **200MB**（:641，大配置场景）。收发主循环是 `tokio::select!`（:653-674）：收响应走 `handle_stream_event`，回执经 `pending_ack_sends` 异步发送防止阻塞收流。

**ACK/NACK 构造**：`handle_stream_event`（:686）按 type_url 分发 handler（:700-701）；handler 返回 `Vec<RejectedConfig>` 则 `RejectedConfig::format_json`（:76，序列化为 `[{key,warn?,error?}]` JSON——与 Go 侧 `parseNackDiagnostics`（xds.go:79-99）的解析格式精确对偶）填进 `error_detail`，组装 `DeltaDiscoveryRequest{response_nonce: nonce, error_detail}`（:737-745）回发；无拒绝则回纯 ACK。

**就绪门闩**：`block_ready`（:453）是启动时传入的 `tokio::sync::watch::Sender`（state_manager.rs:77 `build(config_metrics, awaiting_ready)`）。`record_response`（:677）在每个**无错误**响应后把该 type_url 从 `types_to_expect` 移除，集合清空时 `mem::drop(block_ready)`（:681）释放就绪。单元测试 `warning_only_response_is_nonfatal_and_releases_readiness`（:833）钉死语义：**warning 级 NACK 不拦就绪**（has_errors=false），error 级才拦。

**指数退避**：`run_loop`（:506）连接/传输错误退避翻倍封顶 `MAX_BACKOFF=15s`（:474-475，:510/:523）；`Cancelled`/`DeadlineExceeded`/`Unavailable("transport is closing"/"received prior goaway")` 属正常重连（MaxConnectionAge 到期），**重置回 10ms**（:536-550）；收到任何响应即重置（run_internal 内 :661）。node 身份按 istio 四段式构造 `agentgateway~{ip}~{pod}.{ns}~{ns}.svc.cluster.local`（:410-416），metadata 里 `role = "{ns}~{gw_name}"`（:398）——正是 Go 侧 `AgentgatewayID`（xds.go:1444）用 `KeyDelimiter="~"`（:1464）切分 `RoleKey="role"`（:1467）解析的目标，控制面据此把连接路由到对应 Gateway 的配置切片。

### 2.5 下游 handler：从 proto 到 OS socket

`state_manager.rs` 装配两个监听（:74-75）：`XdsAddress`→discovery store、`ADPResource`→binds store。binds 侧 `Handler<ADPResource>`（binds.rs:2350）逐条 `insert_xds`（:2363，按 oneof kind 分发到 bind/listener/route/policy/backend 等八类子表，:1924-1983），warning 进 diagnostics 转 `RejectedConfig::warning`，error 直接 reject。落到 bind 时 `insert_bind`（:1778）注释钉版："XDS 下发的 bind 失败不许 crash 代理，坏配置应拒绝并记日志"（:1780-1782，引 issue #87）；`upsert_bind`（:879）决定 socket 生死——internal 模式永不开 socket（:914-918 注释）、地址变更先 `BindEvent::Remove`（:909）、`bind_listeners`（:922）真正打开监听（port 0 会回写实际端口，:925-930），最后 `BindEvent::Add`（:940）触发 accept 循环。路由/策略更新则只改内存表，已建连接的后续请求即时走新配置——这就是"热更新"的全部秘密：**socket 只随 bind 增删改，其余资源纯内存替换**。

## 三、外部连接（上游 IR/契约 schema/下游消费）

**上游（L03 translator）**：`ir.AgwResource`（ir/ir.go:41）= `*api.Resource + Gateway 归属`；`IntoProto()`（:46）直接返回内嵌 Resource；`XDSResourceName()`（:57）委托 `GetAgwResourceName`（:15）——按 oneof kind 生成 `bind/{key}`、`route/{key}`、`policy/{key}` 等前缀名，这个函数同时是 Go 集合内资源命名与 Rust 侧 store 键（binds.rs:1906 remove_resource 按 kind 反查子表）的公共词汇表。Address 侧 `IntoProto` 在 syncer/service.go:492。

**契约（L14 protos）**：resource.proto `package agentgateway.dev.resource`（resource.proto:3），`message Resource` 是 10 分支 oneof（:11-23：bind/listener/route/backend/policy/tcp_route/workload/service/route_group/model_route）——agentgateway 用**一张自己的 Resource 表**而非 Envoy 的 LDS/RDS/CDS 全家桶，两类型 URL 常量在 xds.go:1428-1429（`agentgateway.dev.resource.Resource` 与 `istio.workload.Address`），日志缩写 RDS/WDS（:1433-1442）。传输契约 xds.proto：`DeltaDiscoveryRequest`（xds.proto:130）关键字段 `resource_names_subscribe`（:161）、`initial_resource_versions`（:174）、`response_nonce`（:180）、`error_detail`（:185）；服务就一个 `AggregatedDiscoveryService`（:265），Go 侧 `StreamAggregatedResources`（SOTW）直接 `return errors.New("not supported")`（xds.go:327-329）。

**下游（L07 数据面）**：`state_manager.rs:49` 起读 `config.xds.address`，`control::grpc_connector`（state_manager.rs:60 → control/mod.rs:215）构造带 token 轮换（AuthSourceLoader 60s 周期，control/mod.rs:117）与可选 mTLS 的 `GrpcChannel`，它实现 `agent_xds::ClientTrait`（:284）——AdsClient 因此能跑在 agentgateway 自己的 HTTP 栈上而非 tonic 内置连接器。服务器侧装配：setup/setup.go:303/:312 `runXDSServer(..., agw.NackPublisher, agw.Registrations...)` → controlplane.go:70 `NewDiscoveryServer` → :78 `RegisterAggregatedDiscoveryServiceServer`。

## 四、数据流（一次策略变更的十步全链）

1. 用户 kubectl apply 一个 AgentgatewayPolicy；informer 事件进入 krt 集合，translator 的策略集合重算，产出新 `ir.AgwResource`（Gateway 归属=目标网关）。
2. `PerGatewayCollection` 的变换函数重跑（xds.go:144-161）：新内容哈希成新 Version，krt 触发 `RegisterBatch` 回调（:171）。
3. 回调把资源名塞进 `PushRequest.ConfigsUpdated[RDS]`，`pushChannel <- &pr`（:182），`InboundUpdates` 计数 +1。
4. `debounce` 等 10ms 静默（或 1s 上限，:1082），期间多个变更 Merge 成一个请求，调 `Push`（:1031）。
5. `Push` 取全局版本号（RFC3339+自增，:842-844）分发给所有连接的 PushQueue（:1037）；`sendPushes` 拿信号量、起 goroutine 投 `Event` 到该连接的 PushCh（:1012-1025）。
6. 连接主循环第二个 select 命中推送（:416-418）→ `pushConnectionDelta`（:430）→ `pushDeltaXds`（:698）：`GenerateDeltas` 用 `ConfigsUpdated` 双键查到新资源（:1220-1233），包成 `DeltaDiscoveryResponse{Nonce, Resources}` 经 `sendDelta` 发出（:715-729），并记 `NonceSent`（:508-515）。
7. Rust 主循环 select 收到（client.rs:654），退避重置（:661），`handle_stream_event`（:686）按 `agentgateway.dev.resource.Resource` 找到 binds handler（:700）。
8. `HandlerWrapper` 解码、split 出失败项（:191-198），调 `StoreUpdater::handle`（binds.rs:2350）→ `insert_xds`（:2363）→ 策略进内存表；若含 bind 则 `upsert_bind` 开/换 socket（binds.rs:879/:922/:940）。已有连接的下一次请求即走新策略。
9. handler 无拒绝 → 回 ACK（client.rs:737-745 无 error_detail）；Go 侧 `shouldRespondDelta` 识别 ACK、清 `LastError`、记 `NonceAcked`（xds.go:656-667），不再响应。
10. 若数据面拒绝（如引用不存在的 secret）→ `RejectedConfig::format_json` 塞 error_detail 回 NACK（client.rs:710-716）；Go 侧 `parseNackDiagnostics`（xds.go:565）解析、`xdsRejectsTotal.Inc`（:585）、`nackPublisher.PublishNack`（:599）→ K8s Event `AgentGatewayNackError` 挂上 Gateway（publisher.go:86）——用户 `kubectl describe gateway` 立刻可见。

## 五、设计决策（注释实证优先，无注释处标"推断"）

**delta 而非 SOTW**：SOTW 入口显式返回 not supported（xds.go:327-329），是刻意单押。收益有三，前两条有代码实证：重连只补差量（`initial_resource_versions` 双侧配合，xds.go:618-635 与 client.rs:604-614）；推送只发明变更的资源（GenerateDeltas 按 `ConfigsUpdated` 键取数，:1211-1240）；第三条"避免全量快照的内存与序列化开销"无注释，属推断。

**为什么 krt**：文件头注释（xds.go:1-3）明说"building on the KRT generator layer"——krt 集合让"K8s 事件→IR 重算→xDS 推送"成为一条声明式依赖图，syncer 只需注册集合（syncer.go:910-911），无需手写任何 watch/recompute 循环。版本号用内容哈希而非单调序号（:153-154 注释"stable across controller replicas"）配合 `NeedLeaderElection=false`（syncer.go:953）：**无主架构下任意副本可服务任意客户端且版本一致**——这是多副本可行性的根基。代价也写在代码里：`ProxyNeedsPush` 恒返回 true（:859-862，带 TODO(krt) 注释），每个变更都会唤醒所有连接，过滤推迟到 GenerateDeltas 内部做——小集群浪费、大规模依赖 debounce 合并，属推断。

**背压三级**：请求级 `RequestRateLimit`（:255，注释"prevent thundering hurd"，原文拼写如此）、推送并发 `PushThrottle` 信号量（:220/:981-991）、连接级双 select 请求优先（:385-405 注释）。全部继承自 istio 同名机制。

**NACK 的结构化协议**：这是本仓对 istio 原版的显著增强——错误消息不再是自由文本，而是 `[{key,warn,error}]` JSON（Rust 序列化 client.rs:108-131，Go 解析 xds.go:79-99）。语义分层：error 级拦就绪、记 LastError、转 K8s Event；warning 级只记 Event 与指标（`xds_warnings_total`，xds.go:58-63）**不拦就绪不拦 ACK 流程**（测试 client.rs:833-861 钉死）。Rust 侧配套细节：被拒资源不写入 `known_resources`（client.rs:214-220 注释"Do not advertise rejected resources as retained on reconnect"）——重连时不谎报已持有坏配置，服务器会重发。警告级则会记入（severity 过滤只挑 Error，:218）。

**单 ADS 流双类型**：RDS 与 WDS 走同一条聚合流（ADS），靠 type_url 分发（client.rs:700）。相比 Envoy 每类型一流，少一次握手且全局有序——顺序由 `watchedResourcesByOrder`（xds.go:866-883）在服务器侧按 pushOrder 保证（当前 pushOrder 为空，按 map 序，属推断为待完善点）。

## 六、新人提示（调试与坑）

**调试三板斧**：①看推送：控制面日志 `push response`（xds.go:734-740）带 type/资源数/字节数；`push debounce stable`（:1086-1098）带合并事件数与成因。②看回执：`ADS: ACK`（:689）/`ADS: ACK ERROR`（:584）按连接打印；数据面日志 `sending response type=NACK error=...`（client.rs:722-728）。③看 K8s Event：`kubectl describe gateway` 里的 `AgentGatewayNackError`/`AgentGatewayConfigWarning`（publisher.go:23-24）直接给出坏资源 key 与原因（结构化诊断的好处）。

**坑清单**：①**xDS 不下发先查就绪门**：所有注册集合 HasSynced 之前 `StreamDeltas` 直接拒绝连接（xds.go:344-346）；控制器日志等 "caches warm!"（syncer.go:941）。②**订阅语义陷阱**：delta 协议"不订阅任何资源名 = 订阅 *"（:792-799 注释），想"订空"必须同时订阅+退订 `*`——agentgateway 数据面用通配符全订（client.rs 初始请求无 resource_names_subscribe），服务器 `deltaWatchedResources` 据此走全量分支。③**过期 nonce 是常态不是错误**：重连/多推送交错下旧 ACK 会被静默丢弃（:641-644），别当故障查。④**role metadata 格式**：连接归属靠 `node.metadata.role = "ns~gwName"`（client.rs:398 ↔ xds.go:1444-1460），手写 agentgateway.dev/config 或 file 模式跑数据面时填错 ns/name 会拿到空配置集（IsForGateway 全不匹配）。⑤**port 0**：bind 端口 0 会在数据面绑定后回写真实端口（binds.rs:925-930），但控制面不知道实际端口——status/地址展示需另查。⑥**bind 失败不 crash 也不重试**：xds 下发的 bind 开 socket 失败只 warn（binds.rs:1785-1787），资源仍在 store 里；修好端口冲突后需等下一次该 bind 的配置变更才会重试 upsert——属推断，源码无重试循环。⑦**NACK 风暴上限**：NACK 不触发服务器重推（shouldRespondDelta 返回 false，:601），坏配置会静止到下一次配置变更；想让它重发需改配置触发。⑧**200MB 解码上限**（client.rs:641）：超大 WDS（万级 workload）逼近上限时先想到这里。
