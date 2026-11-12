# 07 · commons Go 核心库：healthpub 遥测底座与共享骨架

## 一、角色定位

`commons/` 是独立 Go 模块，全部 NVSentinel Go 组件的共享库：28 个 pkg、84 个 Go 文件（实测），覆盖健康事件发布、CEL 词表、gRPC 认证、HTTP 服务骨架、kube client 调优与日志/追踪/指标。它自身不部署进程——十余个消费方（五类 health monitor、lifecycle-manager、health-events-analyzer、preflight-checks/nccl-loopback、tilt 调试客户端）启动时全调 `healthpub.DialFromEnvOr`。

healthpub 是其中最重的包，是遥测链路的**统一出口**：ADR-001 定下"监控器经 gRPC 向 platform-connector 上报"的契约，commons 把客户端半边做成所有监控器免费继承的库——作者只管检测，重试、认证、幂等、指标、优雅关闭全在这里。grpcauth/grpcclient 是 ADR-030 认证的两半。

## 二、内部结构

**healthpub 五文件三角色**。dial.go 是模式裁决者：`DialFromEnvOr`（dial.go:86）读环境变量 `HEALTH_PUBLISH_TARGET`——未设走 socket 模式（节点本地 UDS，执行调用方的 legacy dial fallback），已设走 direct 模式（远程 deployment platform connector，TLS+projected token）。publisher.go 的 `New` 按 Option 装配两种形态；metrics.go 注册五个 promauto 计数器（success/error/skipped/dropped/retries）。

**socket 模式**核心是存在门：`socketPresent`（publisher.go:318）对从 dial target 解析出的 Unix 路径做 `os.Stat`，socket 消失即返回 `ErrPlatformConnectorUnavailable`（publisher.go:55）——**不重试不清缓存**，因为 connector 关闭时摘除 socket，事件滞留重试环会带着过期 GeneratedTimestamp 抵达。重试用 client-go `wait.ExponentialBackoff`（5 次/2s/1.5 倍/0.1 抖动），`WithRetryPolicy`（publisher.go:110）可覆盖但注释言明仅测试用，factor<1 会被拒。

**direct 模式**把重试从次数制换成窗口制：拦截器装在连接上（dial.go:222，go-grpc-middleware v2），尝试上限 10_000 只是护栏，真边界是每批 deadline（默认 5 分钟窗口、30s 单次 RPC）。拦截器链顺序讲究：`WithChainUnaryInterceptor(retryInterceptor, TokenInterceptor)`（dial.go:184）让 token 拦截器处于重试**内层**，每次尝试重读 token 文件，kubelet 轮换的 SA token 下次尝试即生效。重连退避压到 10s 上限，免得 gRPC 默认两分钟指数退避让恢复后的批次干等。

**遥测底座其余**：logger.go:38 `NewStructuredLogger` 输出 JSON slog 到 stderr（module/version 内建，另有 trace 关联变体）；tracing 包 `InitTracing` 从标准 OTel 变量建 OTLP exporter，span_attributes 把 `pb.HealthEventStatus` 逐字段转 span 属性；featureflags 包把运行时开关暴露成 `nvsentinel_feature_flag_enabled` gauge（ADR-032）。

## 三、外部连接

**对上是 data-models protobuf 契约**：`pb.PlatformConnectorClient`/`pb.HealthEvents`/RPC `HealthEventOccurredV1` 全部 import 自 `data-models/pkg/protos`——commons 只消费不定义契约；Python 客户端共用同名环境变量与等价重试语义。

**对内是认证两半边**：grpcclient/token.go:38 `TokenInterceptor` 每次调用重读 token 文件拼 Bearer 挂进 `authorization` metadata，空文件立即报错而非让排障者被引去查 RBAC；服务端半边 grpcauth 走 TokenReview 并强制校验 audience 回显，防 API-server-audience token 重放。condition 包做 proto↔metav1.Condition 双向适配，让 controller-runtime 的 `SetStatusCondition` 直接可用于 wire 格式。

**CEL 与 lambda 分工**（与任务书预设有出入，见甄别）：celevent.go:58 `Compile` 定义健康事件词表（`event` 绑定为 map[string]dyn），消费方是 platform-connector 的 override transformer 与 event-exporter 过滤器——一处学的表达式两处通用；celfields/fields.go:54 `FieldPaths` 从编译后的表达式推导实际读取的字段路径，供 fault-quarantine 的 nodecache 等做 informer 缓存裁剪（正确处理带点 label 分段）；其余组件自建词表。lambda 包是另一世界：Lambda Cloud REST API 客户端（lambda/client.go:15 包注释），`NormalizeEndpoint` 硬编码 host 白名单并拒绝 http——bearer token 绝不发明文。

**骨架复用**：server.go:338 `NewServer` 选项式装配 HTTP 服务（graceful shutdown/探针/Prometheus/TLS/超时）；polling_health.go:49 `PollingHealthChecker` 用单调时钟防 NTP 误报。kubeclient 统一 qps/burst 旗标，NodePatcher 做缓存感知补丁。

## 四、数据流

direct 模式一批事件的旅程（direct.go:142 `directState.publish`）：`admit` 锁内过 closed 检查并计数 → 构造 pendingBatch（幂等键 direct.go:375 一次性铸造的 UUIDv7，deadline=now+窗口）→ `proto.Size` 超 4MiB（direct.go:64）直接按 rejected 拒，服务端收包上限摆在那，重试白费 → 合并调用方 ctx、批次窗口与发布器生命周期的 deadline → 抢单发送槽（direct.go:113，`semaphore.NewWeighted(1)`，按到达序服务；等槽过窗的批次**丢弃而非迟到送达**）→ `outgoingContext`（direct.go:216）挂 `idempotency-key` header 并注入 W3C traceparent → RPC `HealthEventOccurredV1`（direct.go:177）带重试回调计量。

失败四分类：永久拒绝（direct.go:273：InvalidArgument/PermissionDenied/Unimplemented）、发布器关闭、调用方撤回、窗口耗尽，各配独立 metric reason 与日志级别。socket 模式更短：`Publish`（publisher.go:233）→ 存在门 → backoff 循环，每次尝试前**再探一次 socket**；错误归类时 `IsAuthBackendUnavailable` 优先于 gRPC code——认证后端故障与 connector 本地宕机同为 Unavailable，但一个要全员关注、一个只关本节点。

## 五、设计决策

**窗口制取代次数制**：direct 模式以 deadline 为唯一真边界，代价是 Publish 可能阻塞到窗口尽头——配套 `WaitingOnServer`（publisher.go:212）让监控器 liveness 区分"在等服务器"与"卡死"，且每个在途批次必有界。**单发送槽保序**：同一发布器同一时刻只有一批在飞，前一批落库后下一批才出发——多 goroutine 并发下服务端仍能按监控器看到事件顺序，用吞吐换语义。**幂等键选 UUIDv7**：毫秒时间戳开头使后铸的键排序靠后，datastore 唯一索引插入变追加而非散写；重试复用同一键，重复由服务端去重（ADR-039）吸收。**永久拒绝集的克制**：Unauthenticated 不在集内——token 会轮换，重试有意义；ResourceExhausted 也不在——gRPC 用它表达瞬态过载，按永久拒绝处理会永久丢批；唯一永久的"批太大"已客户端预检。**认证的每时每刻**：token 每次尝试重读，CA 每次握手现场重读（credentials.go:101 ClientHandshake），cert-manager 轮换免重启；direct 模式无 CA 即拒绝明文（credentials.go:39），token 要跨 pod 网络，只有节点内 socket 由内核而非 TLS 保护。**`AcknowledgesStorage` 诚实边界**：socket 模式成功只代表 connector 收下（此后是 ADR-006 环形缓冲异步落库），direct 模式成功才等于已入库——调用方据此决定能否推进"已上报"缓存。

## 六、新人提示

- **最大甄别**：`pkg/lambda` 不是 CEL 引擎，是 **Lambda Cloud API 客户端**（csp-health-monitor 消费）；CEL 在 celevent/celfields/condition 及各组件自建环境。任务书"lambda=CEL 求值"与源码不符，以源码为准。
- 写健康事件过滤器：`event.isFatal` 单独出现会因 dyn 类型被启动时拒绝，必须写 `event.isFatal == true`——刻意的启动期校验换运行期沉默。
- 收到 `ErrPlatformConnectorUnavailable` 绝不能推进"已发送"缓存，否则下轮轮询不会带新时间戳重发。
- `WithRetryPolicy` 只影响 socket 模式；direct 模式节奏在连接拦截器上，调用点调不动。4MiB 预检是客户端侧，改服务端收包上限要两端一起动。
- ADR 编号注意：代码注释的 "ADR-030"（gRPC TLS 认证）对应文件 `docs/designs/030-grpc-tls-authentication.md`，但该文档**内部标题误写 ADR-029**——以文件名为准。
- 加新监控器标准姿势：initializer 调 `DialFromEnvOr(fallback)` 拿三元组，`healthpub.New` 建长寿命发布器，退出时 `CloseOrWarn`（publisher.go:196）；liveness 配 `NewPollingHealthChecker` 并在轮询循环里 `MarkAlive`。
- healthpub 按注释即设计文档写：`Publish` 的 doc comment（publisher.go:233）一段就是完整错误契约清单，改行为先改注释。
