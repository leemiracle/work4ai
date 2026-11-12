# 05 store-client 持久层 + commons/data-models 契约

> 锚基座：本地仓 @fbe7ec29，行号实测；图谱 L02/L03/L09 层。

## 角色定位

这组库是全平台的"脊椎"：data-models proto 定义事件长什么样（跨语言契约），commons 提供发布/认证/审计/锁等横切设施，store-client 把"读写事件"抽象成可与 MongoDB/PostgreSQL/K8s CRD 无关的接口。所有 Go 组件都站在这三块地基上。

## 内部结构

**data-models**：`data-models/protobufs/health_event.proto` 是核心——health_event.proto:31 `OperationStatus`、:48 `HealthEventWithStatus`（事件+处理状态包装）、:54 `service PlatformConnector`（接入 RPC 契约）、:68 `ProcessingStrategy`（处理策略枚举，ADR-025）、:75 `RecommendedAction`、:89 `Entity`（受影响硬件）、:94 `HealthEvent` 主体、:118 `BehaviourOverrides`（行为覆盖：isFatal/RecommendedAction 可被配置覆盖，ADR-021 的压制误报就挂这层）、:125 `HealthEventResource`（K8s CRD 形态，ADR-027）。姊妹契约 `data-models/protobufs/external_remediation.proto`（ADR-040 ERR）与 `maintenance_request.proto`。生成物勿手改（`data-models/pkg/protos/health_event.pb.go` 等）。

**commons**（87 文件 28 包）四根柱子：healthpub——`commons/pkg/healthpub/dial.go:86` `DialFromEnvOr` 统一拨号（dial.go:128 直连模式、dial.go:194 最大重连延迟 10s、dial.go:214 重试上限 10000、dial.go:222 重试拦截器）；身份对——客户端 `commons/pkg/grpcclient/token.go:38` `TokenInterceptor`（投影 SA token 作 Bearer，ADR-030）配服务端 `commons/pkg/grpcauth/tokenreview.go:310` `CreateTokenReview`（tokenreview.go:205 `Authenticate` 带 audience 校验、tokenreview.go:457 `IsAuthBackendUnavailable` 区分"认证挂了"与"没权限"——fail-open/fail-closed 决策依据）；auditlogger（ADR-016，写操作审计，审计 RoundTripper 直接挂进 clientset transport，见 `platform-connectors/pkg/connectors/kubernetes/k8s_connector.go:152-154`）；distributedlock（节点锁）。

**store-client**（104 文件）：`store-client/pkg/datastore/interfaces.go` 六接口——interfaces.go:22 `DataStore`、:35 `HealthEventStore`、:65 `QueryBuilder`/:71 `UpdateBuilder`（**双输出** `.ToMongo()`/`.ToSQL()`，`store-client/POSTGRESQL_IMPLEMENTATION.md` 三层架构：服务层→查询构建层→provider 层）、:77 `ChangeStreamWatcher`、:85 `DataStoreFactory`。后端注册在 `store-client/pkg/datastore/registry.go:35` `RegisterProvider`（registry.go:26 ProviderFactory 类型、registry.go:30 全局注册表）。便捷层 `store-client/pkg/client/event_processor.go:131` `Start` 消费变化流→event_processor.go:203 `handleSingleEvent`→event_processor.go:291 `markProcessed` 按检查点顺序标记；event_processor.go:96 `uncheckpointedEventError` 专用错误防跳号消费。行为契约由 `store-client/pkg/datastore/behavioral_contract_test.go` 钉死（双后端跑同一套行为测试）。

## 外部连接

MongoDB chart 四层嵌套部署（mongodb-store→mongodb/psmdb-operator/psmdb-db→内层五子 chart）；PostgreSQL 用独立 chart v15.5.38（schema 见 `docs/postgresql-schema.sql`）；K8s CRD 后端是 ADR-027 的 HealthEventResource（CRD 随 k8s-datastore 子 chart 发布）。lagstate/watcher 支撑消费滞后指标（ADR-054）。

## 数据流

监控器→healthpub→连接器盖戳→store-client 写入（QueryBuilder 双输出按 provider 落 Mongo 或 PG JSONB）→下游组件（analyzer/quarantine/drainer/remediation）各自 event_processor 经 ChangeStreamWatcher 消费（PG 是轮询模拟 change stream）→检查点推进→markProcessed。身份上每次 gRPC 都过 TokenInterceptor→TokenReview 链。

## 设计决策

"接口在上、注册在中、双实现在下"：behavioral_contract_test 让两个后端被同一套行为测试约束，防实现漂移；查询构建器双输出让业务代码写一次查询跑两库（PG 用原生 SQL+JSONB 算子，非 ORM 翻译）。TokenReview 错误分类（:457）是生产关键——认证后端不可用时是否放行决定整个事件管道可用性。检查点顺序标记（:291）+ 专用未检查点错误（:96）保证重启后不丢不重。

## 新人提示

加新存储后端三步：实现六接口→RegisterProvider 注册→把行为测试跑绿。`store-client/DEVELOPER_GUIDE.md` 与 `POSTGRESQL_IMPLEMENTATION.md` 是扩展约定的钉版文档。改 proto 记得 `make` 重新生成而非手编 pb 文件。commons 的 tokenreview.go 有 582 行，tokenreview.go:526 `isRetryableAPIError` 的错误分类表值得精读。
