# registry.go 深度解析 —— NodeRegistry 分布式节点注册表

> 源码：`core/services/nodes/registry.go`（2788 行，commit 9e831d7）
> 知识图谱：`layer:distributed-nodes`（分布式集群与 P2P 层），complex 复杂度，103 个导出方法

## 角色定位

LocalAI 的分布式形态是"控制面（frontend）+ 数据面（worker 节点）"：frontend 是无状态 API 网关，真正跑模型的是各台 worker 上的后端进程。registry.go 就是**控制面的共享内存**——用一张 PostgreSQL/GORM 数据库表回答三个问题：集群里有哪些节点？每台节点上加载了哪些模型副本？还能往哪台节点上放新模型？

它处于 18 层架构中 `distributed-nodes` 层的底座位置：上层 SmartRouter（router.go）的每一次路由决策、reconciler 的每一次扩缩容、HTTP nodes API 的每一次节点管理操作，最终都落到这个文件的一个方法上。它实现 `ModelRouter` 接口，是"数据库即调度器"设计哲学的载体——所有调度判断（选节点、挑副本、算容量）都直接表达为 SQL 查询，集群状态因此天然对多个 frontend 实例可见且一致。

## 内部结构

文件由 8 个 GORM 表结构 + 一个巨型服务结构组成：

**数据模型（前 350 行）**
- `BackendNode`（L23）：节点主表。gRPC/HTTP 地址、状态机（registering→healthy/unhealthy/draining/offline/pending）、VRAM/RAM/磁盘三元组容量、`ReservedVRAM` 软预约字段、GPU 厂商与 compute capability、`MaxReplicasPerModel` 副本槽上限、`VRAMBudget` 管理员预算覆盖。注释里藏了大量"为什么"：磁盘字段特指 worker 的 models 目录而非根文件系统，因为 staged 权重只写在那里。
- `NodeModel`（L126）：节点×模型×副本槽行。`ReplicaIndex` 区分同节点多副本，每副本独立 gRPC 地址、`InFlight` 在途计数、`State` 状态机（staging/loading/loaded/unloading/idle）、`ConfigRevision` 配置世代戳、`ModelOptsBlob` 序列化的 pb.ModelOptions（供副本扩容复刻）。
- `ModelLoadInfo`（L164）：独立的每模型加载元数据表。存在原因写在注释里——早期把加载信息只存在 NodeModel 行上，worker 死亡+frontend 重启后行全被清掉，reconciler 无从恢复 min_replicas（"Bug-1"）。独立表让加载意图的生命周期与副本行解耦。
- `ModelConfigState`（L174）：模型的当前配置世代（revision，sha256 戳），是整个"配置一致性"机制的锚。
- `ModelSchedulingConfig`（L199）：每模型调度策略——node_selector 标签选择器、min/max replicas、SpreadAll、prefix-cache 路由策略阈值、`UnsatisfiableUntil` 冷却时间戳与 `UnsatisfiableTicks` 滞后计数。
- `PendingBackendOp`（L285）：持久化的后端运维意图（install/delete/upgrade）。针对离线节点的删除请求先落库，节点恢复健康后由 reconciler 消化，消灭"僵尸后端"。
- `ModelLoadJob`（L310）：冷加载任务行。主键即 trackingKey 的唯一性替代长持锁做并发去重——注释详述了演进：曾把整个冷加载（安装+数 GB staging+加载）关在 pg_advisory_lock 里，其它请求阻塞数十分钟直到被 statement_timeout 杀死；现在锁缩小到"认领"，工作本身无锁可观测地跑。

**服务结构 `NodeRegistry`（L346）**：持有 db 句柄 + 三个字段——`replicaRemovedHooks`（atomic.Pointer 指向不可变 hook 切表，副本行删除的单一收口点，prefix-cache 索引和本地模型存储都要在此失效）、`aliasResolver`（别名→目标模型解析器）、心跳 checkpoint 跳写器（`hbLastWrite` 快照 map）。

方法按功能簇分布：注册/生命周期（Register L554/ApproveNode/Deregister/MarkOffline/MarkDraining）、心跳（Heartbeat L1042 + skipHeartbeatWrite/heartbeatMaterial 跳写逻辑）、SQL 放置器（FindNodeWithVRAM L765/FindIdleNode/FindLeastLoadedNode 及 FromSet 变体）、VRAM 预算（ReserveVRAM L821/ReleaseVRAM/UpdateVRAMBudget）、副本操作（SetNodeModel/FindAndLockNodeWithModel L1697/IncrementInFlight/FindGlobalLRUModelWithZeroInFlight L2016）、配置 revision（EstablishModelConfigRevision L1495/AdvanceModelConfigRevisions L1521）、调度配置与标签、PendingBackendOp 队列。

## 外部连接

**被谁依赖（IN-imports 42 个文件）**：`core/application`（startup/distributed 装配）、`core/http/endpoints/localai/nodes.go`（节点管理 REST API）、`core/http/routes/ui_api.go`（React UI 后端）、`core/services/worker/worker.go`（worker 侧注册/心跳）、`pkg/mcp/localaitools`（把节点操作暴露为 MCP 工具）、以及 `tests/e2e/distributed/` 下 15+ 个端到端测试。

**它依赖什么（OUT-imports）**：`advisorylock`（schema 迁移互斥）、`pkg/system`（GPU 能力推导 CapabilityFromGPU）、`pkg/vrambudget`（预算字符串解析）、GORM/clause（UPSERT、SELECT FOR UPDATE、SKIP LOCKED）。

值得注意的对照关系：`FindAndLockNodeWithModel` 的 SQL ORDER BY 与 `replicapicker.go` 的 `PickBestReplica` 互为策略镜像，有专门的镜像测试防漂移——未来热路径会改走内存快照，SQL 是当前的真相源。

## 数据流

**注册流**：worker 启动 → NATS/HTTP 发 BackendNode → `Register`（L554）：按 name 查旧记录；重注册时保留 ID 与审批历史，`MaxReplicasPerModelManuallySet`/`VRAMBudgetManuallySet` 为真则 Omit 掉 worker 上报值防止 UI 覆盖被冲掉（L574-587）；磁盘字段因 GORM struct 更新会跳过零值而**强制写**——一个 100% 满盘的 worker 恰好上报 0，零跳过会把旧的好值留在库里让满盘节点继续接单（L613-624）；事务内先捕获 distinct 模型名再批量删副本行、提交后才 fire hook，保证"hook 集合 == 删除行集合"无交错缝隙（L644-653）；最后 `ClearAllUnsatisfiable` 唤醒冷却中的调度配置（L680）。

**心跳流**：`Heartbeat`（L1042）→ `skipHeartbeatWrite` 判定是否纯时间戳刷新：与上次**落库快照**（而非上一拍）比较，变化量小于 `heartbeatMaterialDelta`（256MiB，L467）且未超 checkpoint 间隔则跳过。VRAM 比较用的是被预算 ceiling 截断后的值——否则设了预算的节点 raw 值在 ceiling 上方震荡，每拍都"看似实质"，抑制永远失效（L955-963）。真正落库时：先查 ceiling、`capAvailable` 截断、`ReservedVRAM` 清零（worker 是真实余量的唯一权威，软预约只活一个心跳窗口，L1070-1073）。

**热路由流**：SmartRouter → `FindAndLockNodeWithModel`（L1697）单事务内：SHARE 锁住 ModelConfigState（与 revision 推进串行化）→ UPDATE 锁锁住候选副本行，三级排序 `in_flight ASC, last_used ASC, available_vram DESC`（注释明说：没有 last_used 层时平局塌缩成"最肥 GPU 永赢"，单节点吃掉几乎全部流量，L1723）→ `in_flight+1`、`last_used=now` → 回取 healthy 节点行。prefix-cache 路由可通过 `RoutePreference`（L1671）直接点名锁"精确的那个副本"。

**配置变更流**：管理员改模型 YAML → `AdvanceModelConfigRevisions`（L1521）单事务推进 revision，同时把所有 revision 不匹配的 loaded/loading/staging 副本行批量改 state=unloading（隔离区），删除陈旧 ModelLoadInfo——在途的旧加载在完成时即识别自己已陈旧。

## 设计决策

1. **SQL 即调度器**：放置判断（`available_vram - reserved_vram >= ?`）写进 WHERE，`ReserveVRAM`（L821）的 admission check 放在 UPDATE 的 WHERE 里——两个并发调度 tick 只有先落地者成功，后者拿 `ErrInsufficientVRAM` 换下一个节点。数据库原子性替代分布式锁。
2. **软预约 + 心跳复位**：ReservedVRAM 只防同一心跳窗口内超卖；worker 每次上报真实读数时清零。控制面乐观、数据面权威。
3. **单一失效收口点（chokepoint）**：副本行删除路径有六条（逐出/reconciler 缩容/探针回收/健康监控/卸载器/MarkOffline），全部收敛到 `fireReplicaRemoved`。hook 用不可变切片 + atomic CAS 注册，读写无锁。
4. **世代戳（revision）隔离**：所有 node_models 读查询都过 `currentModelRevision`（L1444） correlated 子查询——无状态行视为 legacy 合法，有状态后只认精确匹配。配置编辑与热路由因此有不变式：路由永远不落在陈旧配置的副本上。
5. **注释即事故记录**：Bug-1（加载信息随副本行消失）、满盘 0 被零跳过、预算 ceiling 震荡——每个坑的根因与修法都留在注释里，这是活文档。
6. **滞后的容量冷却**：capacity==0 时先计 tick，过阈值才升格为带过期时间的 UnsatisfiableUntil，且任何可能增容的集群事件（注册/审批/改标签/改槽位）都全量清冷却——"过度清除廉价且正确"。

## 新人提示

- **阅读切入点**：先读 L20-350 的表结构注释（信息密度最高），再跳到 `FindAndLockNodeWithModel`（L1697）看热路径，最后看 Register/Heartbeat 两个生命周期函数。
- **易混淆点 1**：`available_vram` 永远是"被预算截断后"的值，`total_vram` 永远是原始值——百分比预算需在容量变化后可重算。
- **易混淆点 2**：`MarkUnhealthy` 故意只改状态不删副本行（L1224 注释）：触发源是 NATS 瞬断这类可自愈事件，删行会迫使每次抖动都全量重载模型。
- **易混淆点 3**：GORM 的 struct Updates 跳零值是本文件反复出现的坑源，磁盘/预算的强制写与 auth 引用回拷都是为对抗它。
- **测试地图**：registry_test / registry_vrambudget_test / registry_clustermemory_test / revision_error_detail_test 是四个正交切面；e2e 在 tests/e2e/distributed/。
