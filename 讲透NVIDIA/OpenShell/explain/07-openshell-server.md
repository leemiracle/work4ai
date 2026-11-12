# 07 · openshell-server：网关本体——grpc/ 拆分与 .persistence 双后端

## 一、角色定位

`openshell-server` 是整个系统的**控制面本体**。crate 文档（crates/openshell-server/src/lib.rs:4-11）自述四件套：gRPC 服务实现、HTTP 健康端点、同端口 gRPC+HTTP 协议多路复用、mTLS 支持。它把自己写成"后端无关"的服务器：crates/openshell-server/src/lib.rs:20-21 明说"编译进来的 compute 驱动在 gateway 启动时注册进一个 registry，运行时选择只查 registry 或已配置的外部端点，**不按驱动名字 switch**"。`openshell-gateway` 二进制只是它的"组装边界"（见第 08 篇）。本 crate 也是全仓最大的单体：src 根 38 个条目、crates/openshell-server/src/lib.rs:15-53 集中声明 36 个模块，其中 `grpc/policy.rs` 23492 行、`grpc/provider.rs` 15876 行、`compute/mod.rs` 15710 行（大量内嵌 cfg(test)），是读仓时必须按模块切片啃的巨物。

历史上 gRPC 处理器曾集中在单文件 `grpc.rs`，现已拆为 `grpc/` 目录（grpc/mod.rs:6-15 声明 auth_rpc/policy/provider/sandbox/service/validation/workspace 七个模块加 mutation_replay 子树）。这个拆分在仓库 git 历史里追溯不到（`git log --all -- crates/openshell-server/src/grpc.rs` 为空），但 `.claude/agent-memory/principal-engineer-reviewer/MEMORY.md` 里仍残留旧路径 `crates/openshell-server/src/grpc.rs`——agent 记忆落后于代码现状的活标本（详见第 12 篇）。

## 二、内部结构

**服务状态枢纽 `ServerState`**（crates/openshell-server/src/lib.rs:259-358）。全部 handler 共享的可变世界：`store: Arc<Store>`（:264，持久层）、`compute: ComputeRuntime`（:267）、`credentials` 凭据运行时（:270）、`supervisor_sessions` 会话注册表（:301）、`peer_routes`/`service_upstreams`（:315-319，多副本中继与服务路由连接复用）、`gateway_interceptors`（:347-349，拦截器执行计划，None 即未配置）、`admin_role`（:358，OIDC 未配置时 workspace 授权把所有认证用户当 Platform Admin——单机模式的后门性默认）。

**grpc/ 目录按资源域切分**。`policy.rs`（23492 行）承载策略 CRUD 与 draft chunk 审批流；`provider.rs`（15876 行）是凭据 provider 全生命周期；`sandbox.rs`（9469 行）沙箱生命周期；`workspace.rs`（1761 行）多租户工作区；`service.rs`（1278 行）服务暴露（ExposeService 走 create/update 双路径 CAS，service.rs:106-131——已存在则带 `MatchResourceVersion` 更新，否则 `MustCreate` 防竞态）；`validation.rs`（2516 行）集中输入校验；`auth_rpc.rs`（1029 行）认证相关 RPC。grpc/mod.rs:78-102 的 `persistence_error_to_status` 把 CAS 冲突映射为 gRPC ABORTED 引导客户端重试；:135-168 是跨模块共享的字段级限额常量表（如 `MAX_NAME_LEN=253` 对齐 K8s 名字上限，`MAX_POLICY_SIZE=262_144`）。

**persistence/ 双后端**。crates/openshell-server/src/persistence/mod.rs:195-198 的 `Store` 枚举只有两臂：`Postgres(PostgresStore)` 与 `Sqlite(SqliteStore)`。所有方法通过 `store_dispatch!` 宏（crates/openshell-server/src/persistence/mod.rs:255-262）一行分派，杜绝第三处逻辑。核心写入原语三个：`put_if`（:367，带 `WriteCondition`——MustCreate/MatchResourceVersion/Unconditional 三态，crates/openshell-server/src/persistence/mod.rs:174-183）、`create_relaxed`（:402-419，"崩了也无所谓"的写入）、`update_message_cas`（:1142-1247，读-改-写 CAS 循环，内部操作冲突时最多重试 `INTERNAL_CAS_ATTEMPTS=5` 次，:1161；客户端操作则直接报 Conflict）。

## 三、外部连接

- **上游**：`Store::connect`（crates/openshell-server/src/persistence/mod.rs:303-327）按 URL scheme 分流——`postgres://`/`postgresql://` 走 Postgres，`sqlite:` 走 SQLite，其它 scheme 直接 config 错误。连接后各跑一次 `migrate()`。
- **migrations/ 双目录**：postgres/ 与 sqlite/ 各 6 个 SQL（001/004/005/006/007/008，002/003 编号被删——001 建的 `objects` 单表是核心：id/object_type/name/scope/payload BLOB/时间戳，005 加 resource_version，006 加 workspace 列，008 加分页索引）。两方言 schema 完全镜像。
- **消费方**：`openshell-gateway` 二进制、CLI/TUI（经 openshell-sdk）；沙箱侧经 multiplex 的 relay 通道回连。
- **legacy_time_wire.rs**（645 行）：读取时把旧时间字段 wire 格式迁移到新格式（`decode_record` crates/openshell-server/src/persistence/mod.rs:240-248 每次解码都过一遍）。

## 四、数据流

以一次沙箱策略更新为例：gRPC 请求进 multiplex（可选过拦截器，multiplex.rs:334-471）→ `extract_principal`（grpc/mod.rs:121-129，中间件保证已插入 Principal，缺了算内部接线错误）→ policy handler 做 workspace 授权 → `update_message_cas` 取当前记录 → 应用 mutation → `put_if(MatchResourceVersion)` 写回 → 数据库唯一约束/版本冲突由 `map_db_error`（crates/openshell-server/src/persistence/mod.rs:1254-1265）识别，SQLite 还要从错误消息文本反推约束名（`infer_sqlite_unique_constraint` crates/openshell-server/src/persistence/mod.rs:1267-1279，SQLite 不像 Postgres 报约束名）→ 冲突上行变 ABORTED。关键设计：**protobuf payload 是权威存储格式**，DB 只加 object_type/name/workspace/labels/resource_version 等索引列；`resource_version` 永远从 DB 行"水合"回消息（crates/openshell-server/src/persistence/mod.rs:246），不信 payload 里的旧值。

## 五、设计决策

1. **乐观并发 + 分布式锁的分层**。单写 CAS 够用时不加锁；跨对象不变量（如沙箱+provider 联合校验）才走 `acquire_distributed_mutation_guard`（crates/openshell-server/src/persistence/mod.rs:291-300）：SQLite 单副本只有进程内互斥，Postgres 额外拿会话级 advisory lock（postgres.rs:117-135），key 是 `0x4f50_454e_5348_4c4c`——字节拼出来是 "OPENSHLL"（少个 E，postgres.rs:38-41 注释自己承认），配 `lock_timeout=10s`（:46），等锁超时宁可失败也不让全机 mutation 无限阻塞。
2. **SQLite 双池耐久度分层**是本 crate 最精彩的取舍（sqlite.rs:79-114 大段注释）：主池 WAL + `synchronous=FULL`——因为撤销类写入（吊销 SSH 会话）若在崩溃后"复活"是安全倒退；`relaxed_pool`（:44-47）用 `synchronous=NORMAL` 专供"丢了只会拒绝访问"的写入（新铸 SSH token）。两池共用同一 WAL 文件，下一次 FULL 提交的 fsync 顺带固化之前的 relaxed 写入——崩溃永远不会回滚 FULL 提交。
3. **错误即信号**：`PersistenceError::is_expected`（crates/openshell-server/src/persistence/mod.rs:69-71）把 UniqueViolation/Conflict 定义为"调用方要行动的信号"而非故障——lease 抢锁靠 MustCreate 失败，CAS 重试靠 Conflict 驱动。
4. **批量删除限流**：`DELETE_MANY_BATCH_SIZE=128`（crates/openshell-server/src/persistence/mod.rs:34），后端把大请求拆成独立可重试的有界写语句，远低于 SQLite 绑定变量上限。

## 六、新人提示

- **别找 grpc.rs**——它是目录。记忆文件与旧文档里的单文件路径全部过期。
- **migration 编号有洞**（无 002/003），不是漏抓；sqlx migrate 按文件名顺序执行，删号不影响。
- **list 方法双轨制**：offset 分页（`list`）与 keyset 分页（`list_after`/`list_object_page`，游标是全序键 `(created_at_ms, name, workspace, id)`，crates/openshell-server/src/persistence/mod.rs:113-123）并存；新代码应走 keyset，offset 在深翻页时漂移。
- **mutation_replay.rs 是"准入栅栏"不是租约**（该文件 :4-7 注释）：owner 持久化失败会让 claim 永远悬着；成功记录 `SUCCESS_TTL_MS` 24 小时（:38），全局并发由 `Semaphore(64)` 封顶（:40），对象类型 `mutation_admission_v1`（:40）。
- **Windows 上 mxc 之外四个驱动注册的是"显式不支持"工厂**（crates/openshell-gateway/src/lib.rs:78-102），报错信息清晰而非链接失败——但那条代码在 gateway crate，server 本身保持平台中立。
- 勘误一条：`Store::close` 仅 test-support 编译（crates/openshell-server/src/persistence/mod.rs:340-343），注释明说"今天没有运行时停机路径"——别在生产代码里找优雅关闭。
