# router.go 深度解析 —— SmartRouter 智能路由器

> 源码：`core/services/nodes/router.go`（2117 行，commit 9e831d7）
> 知识图谱：`layer:distributed-nodes`，complex；与 registry.go 同包、互为表里（registry 是数据底座，router 是决策大脑）

## 角色定位

每一条推理请求（chat completion、embedding、TTS……）进入分布式 LocalAI 后，第一个真正做决策的组件就是 SmartRouter：**这个模型此刻在集群的哪里能跑？** 它给出两级答案——热路径（模型已加载，直接锁定副本返回 gRPC client）与冷路径（模型未加载，走"选节点→装后端→传文件→远程加载"的完整流水线）。

它存在的根本原因是 LocalAI 的 worker 是通用空白节点：worker 不预装任何推理引擎，SmartRouter 通过 NATS `backend.install` 动态把后端装到被选中的节点上。路由器因此兼任调度器（scheduler）、安装编排器（orchestrator）和文件分发器（stager）三职，是 distributed-nodes 层中唯一同时触碰数据库、NATS 总线和 gRPC 数据面的组件。

## 内部结构

**构造与选项**：`SmartRouterOptions`（L41）集中声明全部依赖——NodeCommandSender（NATS 命令通道）、FileStager（文件分发）、`PrefixProvider`（prefix-cache 亲和的接缝，nil 即完全退回 round-robin）、`ConflictResolver`（并发组反亲和）、以及**四层冷加载时间预算**：`ModelLoadCeiling`（持锁总上限）→ `ModelLoadTimeout`（远程 LoadModel 的 gRPC deadline）→ `StagingStallWindow`（staging 零字节宽限窗）→ `ModelLoadAbsoluteMax`（绝对上限 24h）→ 外加 `ModelLoadWait`（请求方等待上限，只约束 caller 不约束 job）。`ModelLoadCeilingFor`（L142）从安装预算+加载预算+5min 余量推导 ceiling，下限钉在历史值 25m。

**SmartRouter 结构**（L154）：registry（ModelRouter 接口）、unloader、fileStager、`installFlight`（singleflight 合并并发安装）、`probeCache`（健康探测记忆 30s TTL）、stagingTracker（UI 进度）、loadWaiters（每模型一个广播 channel，同模型等待者共享一次唤醒）。

**函数族**（按职责）：
- 入口：`Route`（L608）→ `tryWarmPath`（L712）→ `coldLoad`（L764）/`routeViaLoadJob`；reconciler 侧入口 `ScheduleAndLoadModel`（L562）。
- 调度链：`scheduleNewModel`（L1044）→ `resolveSelectorCandidates`→`narrowByGroupAntiAffinity`（L958）→`narrowByDiskHeadroom`（L1242）→ `FindNodesWithFreeSlot` → `selectNode` 闭包（VRAM→idle→least-loaded 三级）→ `evictLRUAndFreeNodeFrom`（L2039）。
- 编排：`scheduleAndLoad`（L330）总管；`applyNodeHardwareDefaults`（L286）按被选中节点的 GPU 调优 NBatch/parallel。
- staging：`stageModelFiles`（L1390，217 行）+ `stageDirectory`/`stageCompanionFiles`/`stageGenericOptions`/`stageOptionDir`。
- prefix-cache：`buildPreference`（L832）/`observePrefix`（L919）。
- 收尾：`newRouteResult`（L1955，在途计数 exactly-once 释放）、`UnloadModel`/`EvictLRU`。

## 外部连接

**依赖**：`NodeRegistry`（所有状态读写）、`prefixcache` 子包（radix-tree 前缀索引 + Provider 接口 + Select 负载守卫 + Pressure 压力信号）、`pkg/vram`（显存估算）、`pkg/distributedhdr`（从 ctx 提取 PrefixChain）、`pkg/grpc`（Backend client 工厂）、`core/config`（硬件默认值/超时推导）、`singleflight`。

**被调用**：`core/application`（startup/distributed 装配）、`core/http/endpoints` 各推理端点经 model loader 间接调 `Route`、reconciler 调 `ScheduleAndLoadModel`/`EvictLRU`、`pkg/mcp/localaitools`（管理工具）。20 个 router_*_test.go 文件按正交切面（eviction/staging/load-budget/reservation/revision/sharedmodels/slot...）覆盖它。

## 数据流

**Route 主流程**（L608）：① trackingKey 确认（modelID 优先）→ `EstablishModelConfigRevision` 建立配置世代（只建不换，晚到的旧请求不能把控制器状态滚回去）→ ② 一次性取调度配置 sched + selector 候选集（避免缓存副本查找与新加载用不同候选集——曾导致选择器排除的节点上的缓存副本被选中、回退时又撞容量的"eviction-busy 循环"）→ ③ `buildPreference` 计算 prefix-cache 偏好 → ④ `tryWarmPath`：`FindAndLockNodeWithModel` 锁副本（带偏好则锁精确副本）→ `probeHealth`（probeCache 记忆 + singleflight 合并并发探测）失败则回滚计数、删行、回退冷路径；节点不再满足 selector 同样回退 → ⑤ 冷路径：有 DB 走 durable load job（per-model advisory lock 只保护"认领"，传输无锁），无 DB 单机直接 `coldLoad`。

**冷加载编排 scheduleAndLoad**（L330）：`scheduleNewModel` 选节点+槽位 → `applyNodeHardwareDefaults`（此时才知道目标 GPU：Blackwell 提大 batch、并行槽按**预算截断后的** VRAM 计算，#10485）→ 立刻写 staging 状态行（冷加载对 /api/nodes 可见且占住槽位）→ defer 失败清行（若 revision 已被隔离则不清——持久清理意图优先）→ `modelPayloadBytes` 在 staging 改写路径**之前**统计本地字节数 → `stageModelFiles` 上传 → 算 effectiveOptionsHash → 状态推进 loading → `extendLoadDeadline`（staging 有进度延长持锁，但 LoadModel 阶段无进度上报，进入前先按 loadTimeout+余量扩宽，防 25m ceiling 误杀 70GB checkpoint 的合法加载）→ gRPC LoadModel → loaded 落库（stale revision 则触发精确清理）→ 存 ModelOptsBlob（副本行 + ModelLoadInfo 双写，防 Bug-1）。

**放置决策链 scheduleNewModel**（L1044）：VRAM 估算（本地 GGUF 元数据/HF repo，10s 超时）→ selector → 并发组反亲和（软过滤：全员冲突则放弃过滤交给 watchdog）→ **磁盘余量**（staging 要先写盘，VRAM 再多也救不了没盘的节点——"在传输第 16 分钟以 500 失败"不如调度时就拒绝）→ 空闲槽位过滤 → `selectNode` 三级择优：`FindNodeWithVRAM(FromSet)`（`(available-reserved) >= 需求`，空闲优先→负载最低）→ 失败则 idle→least-loaded 保守路径 → 仍无节点则 `evictLRUAndFreeNodeFrom`（事务内 SELECT FOR UPDATE 锁 LRU 行 + min_replicas 地板守卫 SQL，提交后才发 NATS 卸载，5×500ms 重试）→ `NextFreeReplicaIndex` 分配槽位（只认 ErrNoFreeSlot 为"满"，其它错误是"查不到"——控制面慢查询不能当作满盘证据去驱逐健康模型）→ `ReserveVRAM` 软预约（失败仅告警继续）→ NATS `installBackendOnNode`（singleflight key=node|backend|model|replica，6 个并发请求 1 次 NATS 往返；DoChan 尊重 ctx 取消，防 15m 安装死锁钉死持锁者）。

**staging 细节**（L1390）：7 个路径字段（ModelFile/MMProj/LoraAdapter/DraftModel/CLIPModel/Tokenizer/AudioPath）逐个 EnsureRemote 并改写为远端绝对路径；目录模型展开逐文件上传；伴生文件表（.onnx→.onnx.json）；选项值（vae_path 等）保持相对路径由后端经 ModelPath 解析；哈希 sidecar 跳过（接收端为每个文件写 .sha256，重传会生成 .sha256.sha256 无限套娃——野外见过 11 层嵌套 5077 个垃圾文件）；shared-models 模式（全部节点挂同一 models 卷）直接跳过上传。

## 设计决策

1. **三级择优 + 软预约**：VRAM 匹配（带预算与预约扣减）→ idle 优先 → least-loaded 兜底；ReserveVRAM 的 admission 在 SQL UPDATE 的 WHERE 里原子完成，防同一心跳窗口双调度超卖。
2. **prefix-cache 亲和**：请求带的 PrefixChain（token 前缀哈希链）在 `prefixcache.Provider`（radix tree）里找持有最长匹配的**副本**（亲和按 replica 粒度——同节点两副本是两个独立 KV cache），经 `Select` 负载守卫（balance 阈值）后通过 RoutePreference 点名锁定；被守卫强行赶离热副本时记 Pressure，作为 reconciler 扩容"缓存热副本"的唯一信号。
3. **进度延长型截止时间**：冷加载不设固定超时（固定值=模型尺寸悬崖，70GB@26MB/s 需要 45m 却在 25m00s 被杀），而是"字节在动就续命、停滞一个 stall window 才判 wedged"，外加 24h 绝对上限。
4. **上下文脱钩（detach）**：冷加载跑在 `context.WithoutCancel` 上——浏览器刷新/LB 空闲超时取消请求上下文，不能连带杀掉数 GB 的传输（"model-load outage"根因）。
5. **gRPC 取消只取消客户端**：LoadModel 超时后 worker 仍在同步加载（实例：83GB checkpoint 在客户端超时 30 分钟后仍在下载，每次重试堆一个加载进程），`loadAbandonedOnWorker` 判定后用精确 processKey `model#replica` reap 孤儿进程。
6. **exactly-once 释放**：in_flight 预约的释放绑定"首次推理完成或路由拆除"先到者，sync.Once 保证——泄漏的 in_flight=1 会让副本永远不满足逐出条件。
7. **驱逐的候选集约束**：全局驱逐曾把 selector 禁用节点上的无关模型踢掉、然后仍把模型放到违规硬件上；驱逐必须与放置共用同一候选集。

## 新人提示

- **切入点**：先读 Route（L608）与 tryWarmPath（L712）理解两级路径，再啃 scheduleNewModel（L1044）的过滤漏斗，最后读 evictLRUAndFreeNodeFrom（L2039）的那段地板守卫 SQL（全文件最难的 30 行）。
- **易混淆 1**：modelID vs modelName——前者是 DB tracking key（逻辑名），后者是传给 LoadModel 的文件路径；trackingKey=modelID 优先。
- **易混淆 2**：probeCache 只缓存**成功**结果，失败立即失效，陈旧副本的清理路径因此仍能在下一请求触发。
- **易混淆 3**：staging 改写的是 clone 后的 opts，本地原 opts 不动——所以 payloadBytes 必须在 staging 前统计。
- **周边文件**：load_job_runner.go（durable job 与等待者广播）、load_deadline.go（进度延长机制实现）、probe_cache.go、staging_progress.go、replicapicker.go（与 registry SQL 镜像的 Go 选择器）共同构成 router 的支撑族，读 router 时建议同步翻阅。
