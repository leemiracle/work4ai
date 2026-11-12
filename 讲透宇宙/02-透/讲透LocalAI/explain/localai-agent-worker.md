# core/services/worker — 分布式 worker 的后端进程监督者：端口、身份与生命周期的正确性

> 源文件：`core/services/worker/supervisor.go`（1024 行）+ `worker.go`（276 行）
> 知识图谱归属：services-core 层（worker 目录共 88 个文件节点，另含 install.go 安装/升级/锁定、NATS 订阅、staging 清理等）

## 一、角色定位

分布式 LocalAI 的 worker 侧：在一台 GPU 节点上管理后端 gRPC 进程的完整生命周期。`worker.go` 的 `Run`（L31-276）是进程入口编排——注册 frontend→连 NATS→起 HTTP 文件传输服务→心跳→构建 supervisor→订阅生命周期事件→等信号；`supervisor.go` 的 `backendSupervisor` 是核心状态机——**端口分配（亲和+隔离）、进程启停与健康标记、死亡回收、按身份精确停止、产物目录完整性校验**。它与前两篇文档的 controller 侧（`core/services/nodes/registry.go`/`router.go`）互为镜像：controller 记 NodeModel 行、按地址调度；worker 拥有真实进程、保证地址永远指向"当初那个东西"。

上游是 NATS 生命周期主题（backend.install/stop/delete、model.stop）与 frontend 注册 API；横向依赖 `core/gallery`（重装的 rename-install-delete 三步交换是 `backendDirIntact` 存在的理由）、`pkg/model`（StartProcess 及工作目录约定）、`pkg/grpc`（带 token 的健康检查/Free）；下游就是它 spawn 出来的后端进程们（第 4 篇讲的那些 backend/go 与 backend/cpp 二进制）。

## 二、内部结构

**backendProcess（L26-60）**：proc/addr/port/serving/stopping/backendName/backendDir+backendDirID。三条注释各藏一个事故：`serving` 是"生命周期的开括号"——addr 在 spawn 时记录但 gRPC 绑定要 10-15s；`backendName` 不可从 map key 推导（key=`modelID#replica`，delete 按名字来查）；`backendDirID` 存 `os.FileInfo`（inode 身份）而非路径——**工作目录跨 rename 跟随 inode**，重装幸存的进程 CWD 已是死 inode，getcwd 全 ENOENT。

**端口分配器 allocatePort（L275-317）四级瀑布**：①本 key 的亲和端口（隔离期已过）→②无主自由端口→③nextPort 在范围内增长→④偷其他 key 的端口（Warn 文案自带处方"raise LOCALAI_GRPC_MAX_PORT"）→全尽报 `ErrNoFreePort`。这套机制的**正确性论证**（L248-273）是全文件最精彩的一段：进程 key `modelID#replica` 与 controller NodeModel 行 `(nodeID, modelName, replicaIndex)` 同构——若端口只能被上次持有它的 key 重绑，那么还能指名该端口的陈旧行必属同一个 key，而该 key 的重注册会覆写它。**静默误路由（#10952）因此被消除而不是缓解**。两个时间常量刻意不从 controller 侧派生：`defaultPortQuarantine`=15s 覆盖"NATS 往返+删行"窗口（probeHealth 验活性不验身份）；`defaultPortAffinityWindow`=5min 超过最慢的行 reap（~45s@默认 cadence）且必须过期——永久持有会让分配器按 distinct-key 数而非并发数耗尽范围。`claimPort`（L368-379）驱逐旧主保映射 injective，map 上限=端口数，与被修的端口泄漏同形状的无界增长一并堵死。sweep 全惰性（无 timer goroutine，唯一观察者是分配本身）。

**启动 startBackend（L428-556）**：先强停"目录被换的幸存者"（优雅 Free 对 CWD 已失解析的进程只会挂起，L436-442）；running 三分支（stopping 拒/活复用/死 reap）；分配端口后 `StartProcess`（bind `0.0.0.0`、对内回报 `127.0.0.1`）；spawn 时记目录身份；**健康轮询 200ms×30s**——注释记录旧 4s 窗口的翻车：慢节点（Jetson 首次 CUDA init）让 worker 在未监听的端口上回 Success，前端首拨 connection refused；轮询中发现进程死（OOM/CUDA）带 stderr 尾 20 行上报；`markBackendServing`（L566-575）做指针身份校验——健康应答时 entry 可能已被并发 stop/换掉，"检查+标记"共享一次持锁。超时同样停半启动进程+回收端口+带 stderr 上报（不 then 留一个没人认领的 unbound 地址）。

**死亡回收 reapDeadProcess（L577-605）**：非请求性死亡（OOM、CUDA fault、段错误）懒发现；注释直书历史 bug——此路径曾只删 entry 不释放端口，crash-loop 每个 restart 永久漏一个端口（这才是走到范围尽头的真因，不是 #10961 假设的并发峰值）；且回收必须走亲和路径——这里没有 reply 能通知 controller，端口只能回到同一个 key 手里。

**三种标识的解析矩阵（L624-730）**：`resolveProcessKeys`（bare modelID→前缀展开所有 `id#N` 副本；带 `#` 不命中则空——显式调用者不做前缀回退，这是 PR #9583 改 key 格式后 admin"Unload model"静默失效的修复）；`resolveProcessKeysForBackend`（backend 名→按记录的 backendName 匹配+legacy 空 backendName 兜底——backend 名永不出现在 `modelID#replica` key 里，这个错配曾让被删 backend 的进程带着已删文件存活）；`resolveStopTargets`（backend.stop 载荷是双义的：admin UI 发 BACKEND 名、UnloadRemoteModel 与 router 弃载收割发 MODEL 名——stop 幂等所以 union 安全，delete 严格因为其标识无歧义）。`backendIdentitySet` 只查自身 metadata 的具体名+别名（两个 backend 可共享一个别名，按别名全展开会误收别人的进程）。

**目录完整性 backendDirIntact（L791-819）+processMatchesBackend（L745-766）**：名字检查之上的第二道闸。重装保名换目录是名字匹配唯一看不见的情形；幸存进程的病征极具欺骗性——Python 后端懒 import torch，HealthCheck 照答，直到 LoadModel 才在 torch 自定义算子注册深处爆 `[Errno 2] No such file or directory`，没有任何指回重装的线索。`os.SameFile` 比对 spawn 时记录的 inode 与现状；stat 失败降级为名字匹配而非拒启。

**停止三段式（L841-956）**：`beginBackendStop`（锁内标记 stopping，entry+port 预留）→`stopBackendExact`（锁外跑：先 5s 超时的 best-effort `Free()` 释 VRAM，再 proc.Stop——网络 I/O 不得持 supervisor 锁）→`finishBackendStop`（**终止完成才**删 entry 释端口；停止失败且进程仍活则 stopping=false 并返回错误——delete 调用者不能在进程还服务时就向 operator 报成功）。`stopModelExact`（L868-919）是 controller 确认路径：地址校验与 stopping 预约同一临界区，陈旧请求永不能停掉同 key 的替身，并等 `proc.Done()`。`LoadedBackendAddresses`（L1012-1024）只取生命周期**中段**（serving 且非 stopping）——报两端会让常规冷启动/关机被 K8s readinessProbe 当数据面故障摘出轮转。

**worker.go 启动序**（细节全是事故墓碑）：认证要求但 token 空→**fail-fast 拒启**（HTTP 文件服务器空 token 会 fail-open，先注册再死更糟，L38-40）；prefetch 放注册**前**（还在暖缓存的 worker 不该被宣布 ready；失败全非致命，master 可按需推文件）；NATS 凭据双路（静态 JWT 直用 / CredentialManager 注册-审批-到期刷新-透明重连，刷新永败触发内部关停让进程重启而非赖活）；`StartEphemeralStagingCleanup`（per-request staging 无人清理曾让长命 worker 填满自己的盘）；readiness 用 `CompositeReadiness`（NATS+数据面双门——NATS 通但后端全死是"up and useless"，#10987：被切离总线的 worker 应报 503 而非无意义 200）；收尾 GracefulDeregister→stopAllBackends(false)→关文件服务器。

## 三、外部连接

| 方向 | 对象 | 交互 |
|------|------|------|
| 上游 | NATS 生命周期主题 | backend.install/stop/delete、model.stop（订阅在 worker 目录其他文件） |
| 上游 | frontend 注册 API | RegistrationClient 注册/心跳/优雅注销；NATSCredentialManager 凭据生命周期 |
| 横向 | core/services/nodes | 对端 controller（registry/router）；文件传输服务器与 readiness 组件 |
| 横向 | core/gallery | InstallBackend 重装交换、ListSystemBackends 别名解析 |
| 下游 | pkg/model + pkg/grpc | StartProcess（工作目录约定）、带 token 健康检查/Free |
| 下游 | 后端 gRPC 进程 | supervisor spawn 与监督的对象 |

## 四、数据流

装载：controller 决定→backend.install→worker 安装（install.go）→`startBackend`：分配端口（亲和优先，隔离拦截）→spawn 子进程（CWD=backendDir，身份记录在案）→30s 健康轮询→serving=true→地址回报 controller 落 NodeModel 行→前端拨 `127.0.0.1:port`/ advertised addr 推理。停止：resolveStopTargets→预约→Free()（best-effort VRAM）→proc.Stop→等终止→端口进隔离 15s→自由池但 5min 内只还给原 key。死亡：下次 start 懒发现→reap→亲和回收。探活：/readyz 拨 LoadedBackendAddresses 的中段地址。

## 五、设计决策

1. **端口亲和是正确性属性不是优化**：key 与 controller 行同构的论证把"陈旧行误路由"从概率问题变成结构不可能；隔离缩窗、亲和除根。
2. **跨侧常量不派生**：worker 本地窗口若派生自 controller 可调/可关的 cadence，在部分集群上静默错误——注释明言"提升此值不是懒删行的替代品"。
3. **inode 身份>路径>名字**：三者各覆盖一层重装情形，缺一层就有一类幸存进程不可见。
4. **生命周期精确到括号**：serving 只在健康应答后置位、地址只在中段上报、终止完成才释放资源——每个边界都对准一个真实的误判故事。
5. **指针身份对抗竞态**：markBackendServing/releaseBackendStart 的 `current != bp` 校验，防轮询窗口内的偷换。
6. **失败必须带证据**：一切死亡/超时路径附 stderr 尾 20 行，把"backend won't start"从玄学变成可诊断。
7. **锁的分段**：预约在锁内、I/O 在锁外、释放在锁内确认身份后——网络卡顿不能冻结整个 supervisor。
8. **注释即事故报告**：#10952/#10961/#10987/#9583 每处都写清旧假设错在哪——这份文件同时是分布式状态管理的案例集。

## 六、新人提示

- **先读注释块再读代码**：defaultPortQuarantine、defaultPortAffinityWindow、allocatePort、backendDirIntact 四段注释合起来是"分布式资源回收正确性"的完整论文，代码只是它的实现。
- **三种标识别混用**：modelID（人用）/processKey `modelID#replica`（map 键）/backendName（gallery 身份）。`isRunning` 明确不收 backend 名，注释警告过这个假设的代价。
- **改端口逻辑前自问**："controller 还有没有行指着这个端口？"——这是亲和、隔离、停止预留全部规则的唯一检验标准。
- **排查"backend won't start"**：`ErrNoFreePort` 的错误文案自带处方；启动失败看 stderr 尾；端口耗尽先查 crash-loop（每死一个漏一个）再看并发峰值。
- **K8s 部署理解 readiness 双门**：NATS 通+数据面通才算 ready，别把探针只接总线。
- **lifecycle 订阅与安装/升级在邻近文件**（install.go 的 installBackend/upgradeBackend/lockBackend、backendLocks 按 on-disk 产物串行化并发安装）——本文件管"活着的进程"，那边管"磁盘上的工件"。
