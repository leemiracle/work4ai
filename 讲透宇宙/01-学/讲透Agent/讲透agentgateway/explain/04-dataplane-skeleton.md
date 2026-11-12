# 04 · Rust 数据面骨架：lib.rs 装配、配置双后端与热更新

> 层级定位：知识图谱 16 层架构 **L07「Rust 数据面核心与可观测性」**。前两篇（01 reconciler、02 translator）讲的是 Go 控制面；本篇跨到 Rust 侧，覆盖 `crates/agentgateway/src/` 的骨架文件（lib.rs / config.rs / config_store.rs / state_manager.rs / app.rs / proxy/ / control/）与 `crates/agentgateway-app/` CLI 壳，回答一个问题：**一个网关进程从敲下 `agentgateway` 命令到能转发第一条请求，中间发生了什么；之后配置变了，又如何不断流地换血。**
>
> **两处与常见直觉（含本系列任务书原文）不符的事实，先钉版**：
> 1. 任务书称 lib.rs 为"数据面总装配"。源码中 `lib.rs` 实际是**类型定义层**——`RawConfig`（lib.rs:158）与内部表示 `Config`（lib.rs:694）都在此定义，真正的**装配顺序在 app.rs:21-214 的 `run_with_ui_assets`**。lib.rs 里最接近"装配"的是 `ProxyInputs` 结构（lib.rs:908）——它是传给代理引擎的"一篮子依赖"。
> 2. 任务书给出"running_in_kubernetes 直读 config.yaml（lib.rs:206 类锚）"。实际位置在 **agentgateway-app/src/lib.rs:197 与 214-216**（另一个 crate 的 lib.rs），且语义相反：**在 Kubernetes 里恰恰禁止走默认 config.yaml 路径**——检测到 `KUBERNETES_SERVICE_HOST` 且未设 `LOCAL_XDS_PATH` 时直接报错要求显式传 `--config/--file`（agentgateway-app/src/lib.rs:197-201）；默认 config.yaml 兜底只在非 K8s 环境生效。

## 角色定位（L07；从 CLI 启动到 proxy 就绪）

L07 层在图谱中的摘要是"数据面 crate 的骨架：lib/config/state_manager 承载全量配置模型与热更新生命周期，proxy 为代理骨架……control 消费 xDS"。展开成启动链就是四段：

1. **CLI 壳**（`agentgateway-app`）：`agentgateway-app/src/lib.rs:141` 的 `run()` 是 main 后第一站——先 `libc::prctl(PR_SET_THP_DISABLE)` 关透明大页（lib.rs:144-147，注释明说是防 RSS 膨胀）、按平台装 jemalloc/mimalloc 分配器、`agentgateway::crypto::init()` 装 crypto provider，然后 clap 分派到四条子命令：`oneshot`（Linux 专属）/`import`/`migrate`，无子命令则默认 `run`（lib.rs:163-169）。
2. **配置装载**：`commands/run.rs:32` 用 current_thread runtime 包住整个启动：读配置 → `parse_config`（run.rs:41）→ 连数据库（run.rs:57-66）→ Hybrid 模式建 `ConfigResourceStore`（run.rs:70-81）→ `ensure_session_key`（run.rs:82）→ 起请求日志库（run.rs:88-104），最后进入 `proxy()`（run.rs:204-212）调用 `app::run_with_ui_assets`。
3. **数据面总装**（`agentgateway/src/app.rs:21`）：建独立的数据面线程池 runtime（app.rs:28）、readiness/drain 通道（app.rs:33-43）、`StateManager`（app.rs:124）、admin UI 服务（app.rs:147）、`ProxyInputs`（app.rs:164）、`Gateway`（app.rs:178）。
4. **就绪闸门**：`Gateway` 被投进数据面池但**先不跑**——它 await 一个 `xds_rx.changed()`（app.rs:186），等 `StateManager` 首次把配置灌进 stores 后才 `gw.run()`（app.rs:188）。readiness 同样被 `state manager` 任务卡住（app.rs:42），xds 首次到货才放行（app.rs:138-143）。

一句话：**app.rs 是总装车间，state_manager 是供血系统，config_store 是外存，Gateway 是只认 stores 不认配置文件的车轮。**

## 内部结构

### lib.rs：配置模型的两层皮 + 一篮子依赖

lib.rs 前 54 行 `pub mod` 声明（lib.rs:26-54）列出数据面全部子系统入口（http/llm/mcp/proxy/control/store/types/telemetry 等），这是图谱 L07-L13 的模块地图。核心内容三块：

- **`RawConfig`（lib.rs:158-274）**：用户输入的原始形态，字段与 YAML/env 一一对应（`enable_ipv6`、`xds_address`、`admin_addr`、`database: Option<telemetry::log_store::Config>` 在 lib.rs:171 等）。注释钉版了设计意图："RawConfig represents the inputs a user can pass in. Config represents the internal representation of this."（lib.rs:157）。
- **`Config`（lib.rs:694-753）**：解析后的内部表示，携带运行期句柄——`admin_runtime_handle`（lib.rs:738）、`budget_policy`（lib.rs:741）、`config_reload_status`（lib.rs:746，记录最近一次配置重载失败原因，供 admin API `/api/runtime` 查询）。
- **`ProxyInputs`（lib.rs:908-922）**：`cfg + stores + upstream + metrics + model_catalog + admin + mcp_state + ca + spiffe + admission` 十件套。lib.rs:924-953 还提供 `ProxyInputs::new`，注释明说这是给"把 agentgateway 当库嵌入别的应用"用的，会绕过 `app::run` 自建的 admin/信号/xDS 管理——嵌入式集成的官方入口。
- **`ConfigStoreMode`（lib.rs:499-509）**：三态 `File`（默认，UI 改动写回配置文件）/`Hybrid`（文件做基线，UI 覆盖层写数据库）/`ReadOnly`。

### config.rs：parse_config 的优先级阶梯

`parse_config`（config.rs:33）把 `String → Config`，几条硬规则：

- 先 `shellexpand::full` 展开 shell 变量再解析（config.rs:38-39），schema 魔法注释行被替换掉；
- **env 永远压过文件**：每个字段都是 `parse::<T>("ENV")?.or(raw.xxx)` 模式，如 `LOCAL_XDS_PATH`（config.rs:69-72）、`ADMIN_ADDR`（config.rs:350）、`SESSION_KEY`（config.rs:377）；
- 配了 `XDS_ADDRESS` 则 `NAMESPACE/GATEWAY` 变必填（config.rs:101-112），否则双双默认 `"default"`；
- 三个服务地址默认值：admin `localhost:15000`（config.rs:355）、stats `:15020`（config.rs:359）、readiness `:15021`（config.rs:363）；
- Hybrid 模式两道闸：必须配 `config.database.url`（config.rs:413-414）；Postgres 后端 `maxConnections` 至少 2（config.rs:415-425）——因为 Postgres 侧要留一条连接给 LISTEN 通知。
- `ensure_session_key`（config.rs:1100-1130）：`SESSION_KEY`/`config.session.key` 都没设时，优先从 ConfigResourceStore 取（乐观并发自愈，见下），否则 `persist_session_key`（config.rs:1133）生成 AES-256 密钥**写回 YAML 文件**并加"改它会作废现有会话"的注释行。

### config_store.rs：双后端 + 乐观 generation 并发控制

这是本篇最值得精读的文件。`ConfigResourceStore`（config_store.rs:17-21）三个字段：`pool: DatabasePool` + `change_tx: watch::Sender<()>` + `notification_id: Option<String>`。

**双后端判定**：`DatabasePool` 是 SQLite/Postgres 的枚举封装，`from_pool`（config_store.rs:227-271）按池类型执行各自 schema（`SQLITE_SCHEMA` config_store.rs:2275-2296，`POSTGRES_SCHEMA` config_store.rs:2298-2319，表结构完全同构：`agw_config_resources` 主键 `(kind,id)` + 软删 `deleted_at` + `agw_config_meta` 单行 `generation`）。

**15 种资源类型**（config_store.rs:82-115）：`llm.provider/llm.model/llm.virtualModel/llm.apiKey/llm.policy/mcp.target/mcp.policy/traffic.gateway/traffic.route/session.key` 等，UI 上看到的一切可管理对象都在此枚举。

**乐观并发的核心是一条 SQL**（SQLite 版 config_store.rs:1841-1868，Postgres 版 config_store.rs:1871-1898 逐字等价）：

```sql
UPDATE agw_config_meta SET generation = generation + 1
 WHERE id = 1 AND (? IS NULL OR generation = ?)
 RETURNING generation
```

写事务先原子地"比较并自增"：调用方传入读取快照时的 `expected generation`，不匹配则 0 行返回，立即回读当前值并抛 `ConfigResourceError::GenerationConflict { expected, found }`（config_store.rs:70-79）——**没有锁等待，没有重试，输家直接拿 409 回去**。配套单测把语义钉死：`rejects_a_write_pinned_to_a_stale_generation`（config_store.rs:2364）验证被拒写入零残留，`concurrent_writers_cannot_both_commit_one_generation`（config_store.rs:2394）验证并发双写恰好一胜一负。

**两后端差异**（都有注释解释为什么）：SQLite 写事务用 `BEGIN IMMEDIATE`（config_store.rs:1839，注释："A deferred SQLite lock upgrade can fail without busy_timeout"）；Postgres 读快照用 `BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY`（config_store.rs:1802）保证 generation 与资源行同相。**变更通知也分叉**：Postgres 在事务内 `pg_notify('agentgateway_config_changed', notification_id)`（config_store.rs:2197-2207，channel 常量 config_store.rs:2321），`from_pool` 里起的 `PgListener` 循环（config_store.rs:245-263）只对**别人的** notification_id 触发 `change_tx`（config_store.rs:249-251，自通知过滤），断线重连也强制触发一次全量 reload（config_store.rs:253-256）；SQLite 没有 LISTEN，靠同进程 `upsert` 后直接 `notify_changed()` 兜底。消费端一律 `subscribe_changes()`（config_store.rs:277-279）拿 watch receiver。

**upsert 的"无变化不 bump revision"**：config_store.rs:1919-1929 的 `ON CONFLICT ... DO UPDATE ... WHERE deleted_at IS NOT NULL OR value_json IS NOT excluded.value_json`——值相同就整个跳过，`revision` 只在真实变化时 +1，`WriteResult::Unchanged`（config_store.rs:39-53）由此而来。

**session key 的乐观自愈**：`session_key()`（config_store.rs:282-318）是个 loop——读不到就生成一个，带 `Some(snapshot.generation)` 尝试写入；若**别的副本抢先写入**导致 GenerationConflict，吞掉错误重读（config_store.rs:309-314 注释明说"possibly another replica generating its own key"）。多副本共享 Postgres 时天然收敛到同一把密钥。

### state_manager.rs：xDS 消费与本地文件双模

`StateManager`（state_manager.rs:16-25）= `stores + xds_client + resource_manager`。`new()`（state_manager.rs:34-106）按配置二选一或并存：

- **xDS 模式**（state_manager.rs:49-78）：`control::grpc_connector` 建 gRPC 通道（见下节），`agent_xds::Config::new(...)` 注册两个 watched handler——`istio.workload.Address → stores.discovery`、`agentgateway.dev.resource.Resource → stores.binds`（state_manager.rs:74-75，TypeURL 常量 state_manager.rs:27-31）；`Authorization` handler 被注释掉（state_manager.rs:76）。
- **本地模式**（state_manager.rs:82-100）：`xds.local_config` 存在时构造 `LocalClient` 并 `Box::pin(local_client.run()).await`——注释直说定位："LocalClient serves as a local file reader alternative for XDS. This is intended for testing."（state_manager.rs:124）。但如今它承载了整个 standalone 文件网关形态。

`LocalClient` 的热更新是**三路 select**（state_manager.rs:167-207）：① 文件 invalidate 通知（notify 风格 `watch_files_with_options`，state_manager.rs:155-157，删除后自动重挂 watch，state_manager.rs:175-183）；② `resource_manager.subscribe_changes()`（a2a 等外部资源变化）；③ `config_resource_store.subscribe_changes()`（Hybrid 数据库覆盖层变化）。任何一路触发都走 `reload_config_after_change` → `reload_config`（state_manager.rs:247-297）：读文件（Hybrid 时先 `materialize_hybrid_config` 把 DB 覆盖层叠上去，state_manager.rs:299-306）→ `NormalizedLocalConfig::from` 解析 → `binds.sync_local` + `discovery.sync_local`。**失败安全**：解析或 bind 失败只置 `config_synchronized=0` 并 `record_failure`（state_manager.rs:308-326），保留 `prev` 状态继续跑旧配置；成功则 `record_success` 清错。顺序也有讲究："Sync binds first, but always run discovery sync even when a new bind cannot open"（state_manager.rs:270-271）——bind 错误不能挡住 workload/service 状态同步。

另一根线是 `start_self_workload_resolution`（app.rs:136 调用，state_manager.rs:341-368）：本地化路由需要知道"我自己是哪个 workload"。`Wds` 模式下注册 readiness 任务、订阅 workload 插入流，60 秒超时（`SELF_WORKLOAD_TIMEOUT` state_manager.rs:335）后**放行 readiness 但继续等**（state_manager.rs:424-431，warn 日志明说"unblocking readiness, still watching"）；无 xDS 则直接放弃（state_manager.rs:401-404，有单测钉死不得永久阻塞 readiness）。

### control/：xDS 通道的认证与 TLS

`control/mod.rs` 三件事：`AuthSource` 枚举（control/mod.rs:73-82）——`Token(文件路径, cluster_id)` / `StaticToken` / `None`；`AuthSourceLoader`（control/mod.rs:116 起）对 Token 模式**每 60 秒重读 token 文件并热换 Bearer**（control/mod.rs:117-119 建间隔，control/mod.rs:145-158 比对换新，测试 `test_token_file_loader_rotation` control/mod.rs:393 钉死），请求时注入 `authorization` + `clusterid` 两个头（control/mod.rs:189-203）；`grpc_connector`（control/mod.rs:215-232）把 RootCert（File/Static/Default→系统信任，control/mod.rs:29-33）转成 rustls ClientConfig 并强制 ALPN h2（control/mod.rs:64），产出实现了 `agent_xds::ClientTrait` 的 `GrpcChannel`（control/mod.rs:284-302）。同目录 `spiffe.rs`/`caclient.rs` 分别管 SPIFFE Workload API 与 Istio CA 签证。

### proxy/：Gateway 只消费 BindEvent

`Gateway`（proxy/gateway.rs:128-131）只有两个字段：`pi: Arc<ProxyInputs>` + `drain`。`run()`（gateway.rs:164）第一步 `self.pi.stores.binds.write().subscribe()`（gateway.rs:169）订阅 BindStore，然后对事件分派（gateway.rs:175-190）：`Add` → 起 `run_bind` 任务（http/tcp 由 listener 类型决定，走 L08 过滤器矩阵与 L11 llm 翻译）；`Update` → **不重启任务**，`active.update(bind)` 用 `config.send_replace(Arc::new(bind))`（gateway.rs:151-155）原地换 watch 里的配置，监听 socket 与连接全不动——这就是数据面热更新的最后一环；`Remove` → abort 任务。实验性 `ThreadPerCore` 模式为每个 CPU 起独立 current_thread runtime 并绑核（gateway.rs:195-213）。`BindEvent` 定义在 store/binds.rs:135-139，由 `upsert_bind` 在配置落库时发出（binds.rs:940-942）。

### app.rs 装配顺序（编号即源码顺序）

`run_with_ui_assets`（app.rs:21）依次：① 数据面线程池（app.rs:28，`new_data_plane_pool` app.rs:333-386——专用 `agentgateway-{id}` 命名线程的多线程 runtime + mpsc 收任务，`block_shutdown` 任务进 JoinSet、其余 spawn 即忘）；② OTel 资源默认值（app.rs:31）；③ shutdown/drain/ready（app.rs:33-43）；④ readiness server 进数据面池（app.rs:45-59）；⑤ 指标注册（含 tokio/cgroups/smaps collector，app.rs:61-66）；⑥ CA client + SPIFFE + HBONE pool（app.rs:72-93）；⑦ 上游 client + metrics（app.rs:101-109）；⑧ model catalog（**Hybrid 时先合并 DB 里的 catalog 资源**，app.rs:111-121）；⑨ `watch` 通道 + `StateManager::new`（app.rs:123-132）；⑩ self workload 解析（app.rs:136）；⑪ xds ready 联动 readiness（app.rs:138-143）；⑫ `spawn(state_mgr.run())`（app.rs:145）；⑬ admin UI（app.rs:147-159）；⑭ `ProxyInputs`（app.rs:164-176）；⑮ `Gateway::new`（app.rs:178）；⑯ 数据面池收 Gateway 任务、先等 xds ready（app.rs:182-191）；⑰ metrics server（app.rs:199-207）。返回 `Bound`（app.rs:289-294）给 CLI 去 `wait_termination`（app.rs:305-325：等信号 → 触发各 bind 的 shutdown policy → graceful drain）。

## 外部连接

- **上游（控制面）**：`StateManager` 经 `agent_xds` crate（L14）订阅两类资源（state_manager.rs:74-75）。proto → 内部类型的翻译层在 `types/agent_xds.rs`：`Bind::from_xds`（agent_xds.rs:1583）、`Listener::from_xds`（agent_xds.rs:1617）、`TCPRoute::from_xds`（agent_xds.rs:1652）、`Route::from_xds`（agent_xds.rs:1682）、`ModelRoute::from_xds`（agent_xds.rs:1727）——全部带 `Diagnostics` 收集告警、返回 `Result` 拒绝坏资源。**本地 YAML 与远端 xDS 走同一条下游管线**：xDS 处理器是 `impl agent_xds::Handler<ADPResource> for StoreUpdater`（store/binds.rs:2350-2356，逐条 `insert_xds`、坏配置进 `RejectedConfig` 回 NACK 给控制面），本地文件是 `sync_local`（binds.rs:2226）——两者最终都变成 stores 里的状态，Gateway 无感。这也解释了 binds.rs:2253-2257 那条注释的对比："Unlike XDS (which must tolerate a bad dynamic config), a static local config that cannot open a newly added listener is a fatal misconfiguration"——**xDS 更新失败可容忍，本地文件 reload 加新端口失败是致命错**（issue #87 修复），同一 store 两种容错策略。
- **下游（流量处理）**：`ProxyInputs.upstream` 是所有出站连接的共享 client（app.rs:101-109 构建，DNS/连接池/H2 keepalive 全吃 config.backend）；`mcp_state` 喂 MCP 会话网关（L09）；http 过滤器矩阵（L08）与 llm provider 翻译（L11）通过 binds/listeners 间接驱动，本篇不展开。
- **telemetry**：请求日志写库由 run.rs:88-104 的 `log_store::setup_with_pool` 完成——独立 writer 线程 `request-log-db-writer` + crossbeam 无界队列（log_store.rs:70-77），**与 config store 共池条件是两边 `Config` 完全相等**（run.rs:90-94 逐字段比较）；后端同样由 URL 前缀判定："A postgres:// or postgresql:// URL uses Postgres; any other value is treated as a SQLite database"（log_store.rs:26 注释）。`config_reload_status`（lib.rs:746）+ `config_synchronized` 指标（state_manager.rs:312/317）构成配置健康度的可观测出口。

## 数据流

**冷启动**：`agentgateway` → app-crate run()（分派）→ read_config_contents：`--config` 字符串 / `--file` 文件（`-` 走 /dev/stdin 且标记 read-once，app-crate lib.rs:189-194）/ 都没有时非 K8s 才兜底 `default_config_dir()/config.yaml`（不存在则生成带 `sqlite://data.db` 的默认单机配置，app-crate lib.rs:262-269）→ parse_config（env > file，双皮 RawConfig→Config）→ database pool → Hybrid 建 store → session key → log store → `app::run_with_ui_assets` 按上节 ①-⑰ 装配 → **Gateway 卡在等 xds_rx** → StateManager：有 xDS 地址则 AdsClient 连控制面（token 60s 自动轮换），无则 LocalClient 立即 `reload_config` 灌 stores → binds 发 `BindEvent::Add` → xds_tx 放行 → Gateway `run_bind` 监听端口 → readiness 转绿。

**一次热更新（standalone 文件形态）**：用户编辑 config.yaml → notify invalidate → 三路 select 命中第①路（state_manager.rs:170）→ `reload_config_after_change` → （Hybrid 先 materialize 覆盖层）→ `NormalizedLocalConfig::from` → `binds.sync_local` diff 出 Add/Update/Remove → mpsc 发 BindEvent → Gateway 对 Update `send_replace` 原地换配置（不重起 socket）、对 Add/Remove 起停任务 → `config_synchronized=1`。**全程无锁交换、失败回退旧状态**。K8s/xDS 形态下同构，只是触发源换成 StoreUpdater::handle 收到的新资源。

**oneshot 形态**（测试利器）：`agentgateway oneshot -- <cmd>` 起子进程（oneshot.rs:30-33），子进程 `PR_SET_PDEATHSIG=SIGTERM`（父死子亡，oneshot.rs:36-39）+ `READY_FD=3` 管道；父进程阻塞读管道直到子进程 readiness 后 run.rs:199 `drop(ready_fd)` 发 EOF（oneshot.rs:116-127），然后 `exec` 目标命令——**"网关就绪才启动被测客户端"** 的精确同步。

## 设计决策

1. **SQLite vs Postgres 何时选**：源码没有长篇论证，但事实链可拼出决策面——默认生成的单机配置直接用 `sqlite://<dir>/data.db`（app-crate lib.rs:263-265）；共享 Postgres 时强制 `maxConnections>=2`（config.rs:415-425）因为要养 LISTEN 连接；`session_key` 的多副本自愈注释（config_store.rs:309）只在多副本场景成立。**推断**：SQLite=单实例零运维默认，Postgres=多副本共享配置+跨进程变更通知的必选项（SQLite 的 watch 通知只在同进程内传播）。
2. **乐观 generation vs 锁**：config_store.rs:1839 注释给出 SQLite 侧动机（deferred 锁升级会绕过 busy_timeout 直接失败，所以写前就 BEGIN IMMEDIATE 抢写锁）；generation 比较则把"读到写"的窗口显式化，冲突方拿 409 自己决定重试与否，服务端零等待队列。两注释合起来是完整答案：**物理层用数据库事务锁保序，语义层用 generation CAS 表达意图**，缺一不可（只靠 BEGIN IMMEDIATE 无法表达 UI"我基于版本 N 编辑"的语义）。
3. **K8s 里禁用默认 config.yaml**（app-crate lib.rs:197-201）：Pod 里静默落到 `/config/config.yaml` 会让"忘挂卷"变成"跑了个空网关"，直接报错把事故提前到部署时。而 `/config` 目录回退链（app-crate lib.rs:218-242：/config 可写→用之；存在不可写→报错；官方容器未挂载→报错；否则 XDG_CONFIG_HOME/agentgateway）+ 官方容器探测（`AGENTGATEWAY_ENV=container`，app-crate lib.rs:244-246）区分了容器/桌面两种发行形态。
4. **双 runtime**：数据面独占线程池（app.rs:333）而控制/管理任务留在主 runtime——`config.admin_runtime_handle`（lib.rs:738）的存在（run.rs:42-44 注释）说明 OTLP exporter 等后台任务被有意赶到 admin runtime，避免和数据面抢线程。
5. **xDS 与本地文件共用 stores 但容错分级**（binds.rs:2253-2257）：远端配置坏是"控制面还在学"，本地文件坏是"用户手改错了"，前者 NACK 继续跑旧的，后者 reload 时对新增 bind 直接报错——**同一份同步代码用 `is_new_bind` 一个布尔实现两种策略**。

## 新人提示

- **本地跑数据面**：`cargo run -p agentgateway-app -- --config '<yaml>'` 或省略参数让它生成默认配置（`~/.config/agentgateway/config.yaml` + SQLite）。`--validate-only` 只做解析+`NormalizedLocalConfig` 校验不监听（run.rs:38-39, 144-170）。想看完整启动日志用 `oneshot` 配 `--output`。
- **改配置加载逻辑**：入口全在 `parse_config`（config.rs:33）。加新字段时三处同步：`RawConfig`（lib.rs:158）加 Option 字段 → parse_config 里 `env.or(raw)` → 需要序列化的话 `Config`（lib.rs:694）加对应字段。别忘 schema 注解宏 `#[apply(schema_de!)]`。
- **调试 xDS 断连**：看 `agent_xds::Metrics`（app.rs:63 注册，admin :15000 的 /metrics 可查 `config_synchronized`）；本地文件形态下 reload 失败会 `record_failure` 进 `config_reload_status`，用 `/api/runtime` 查最近错误。token 轮换问题看 control/mod.rs:148 的 error 日志（"Failed to reload token"）。Postgres 通知断线有专门 warn（config_store.rs:254）并自动全量 reload。
- **坑**：① Postgres Hybrid 写 `maxConnections: 1` 会在 parse_config 就被拒（config.rs:415-425），报错信息即原因；② `--config` 与 `--file` 互斥（app-crate lib.rs:176）；③ SESSION_KEY 未设且文件不可写时 MCP 会话 ID 落到 base64 明文并打 warn（config.rs:1125-1128）——不是 bug 是降级；④ K8s 里跑必须显式给配置，`LOCAL_XDS_PATH` 环境变量也算显式（app-crate lib.rs:197）；⑤ upsert 相同内容不会 bump generation 也不会触发重载（config_store.rs:1919-1929），调试"为什么没 reload"时先确认内容真的变了；⑥ oneshot 仅 Linux（app-crate lib.rs:122-123 cfg 门），且 `--copy-self` 仅 musl 构建可用（run.rs:124-131）。

---

*锚点口径：`lib.rs`/`config.rs`/`config_store.rs`/`state_manager.rs`/`app.rs` 指 `crates/agentgateway/src/` 下同名文件；`app-crate lib.rs`/`run.rs`/`oneshot.rs` 指 `crates/agentgateway-app/src/`；`binds.rs` 指 `src/store/binds.rs`；`agent_xds.rs` 指 `src/types/agent_xds.rs`；`gateway.rs` 指 `src/proxy/gateway.rs`；`control/mod.rs` 与 `log_store.rs`（src/telemetry/）全路径已随文标注。全部行号经 sed/grep 对源码核实。*
