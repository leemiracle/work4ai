# 03 · init.cc — communicator 建立全流程

## 一、角色定位

`src/init.cc`（4007 行，全库最大源文件）是 `ncclComm_t` 的一生记录者：从 `ncclCommInitRank*` 的校验与 config 解析，到 bootstrap 建链、拓扑探测、算法图计算、传输连接、设备侧结构下放，再到 finalize/destroy/abort 与 split/shrink/grow。它是**总装车间**：不实现网络（bootstrap.cc）、不做选路（graph/topo.cc）、不搬数据（transport/*.cc），而是把二十几个子系统按正确次序与屏障串起来。入口分层：公共 API 统一汇入 **`ncclCommInitRankDev`**（src/init.cc:2851-2943）；后者构造异步 job，干活的 **`ncclCommInitRankFunc`**（src/init.cc:2105-2251）；最重阶段是 **`initTransportsRank`**（src/init.cc:1163-1995，833 行）。

## 二、内部结构

### 1) 一次性初始化与 uniqueId

`ncclInit()`（src/init.cc:183-186，call_once）做 ncclOsInitialize、GDRCopy 可选初始化与 `bootstrapNetInit()`（选带外网卡，无条件执行，src/init.cc:176-177）；`ncclInitEnv()`（src/init.cc:196-199）拉起 env plugin；`ncclGetUniqueId`（src/init.cc:208-222）实为 bootstrapGetUniqueId+memcpy。

### 2) ncclCommInitRankDev：同步壳与异步 job

校验后分配裸 `ncclComm` 并设置 abortFlag、设备可见 abortFlagDev 与 `startMagic/endMagic` 腐坏探测（src/init.cc:2882-2886）；`parseCommConfig` 消化 ncclConfig_t（src/init.cc:2891，env 覆盖在 src/init.cc:2260）；**先把 `initState=ncclInProgress` 并发布 `*newcomm=comm`**（src/init.cc:2892-2894）——调用者立刻拿到句柄而后台还在建；投递任务走 `ncclMgmtTaskEnqueue` 或老 `ncclAsyncLaunch`（src/init.cc:2923-2929）；non-blocking 模式只轮询一次 async error 即返回（src/init.cc:3072-3075）。

### 3) ncclCommInitRankFunc：主线时序（src/init.cc:2105）

八个计时器切阶段（收尾打 "Init timings" INFO，src/init.cc:2233-2240）：① kernel 准备——装设备 kernel、设 kernel 栈防 NVSHMEM 式重配置（src/init.cc:2120-2134）；② 分岔——split/shrink 走 `bootstrapSplit`（src/init.cc:2136-2168），正常 init 与 grow 走 `bootstrapInit`（src/init.cc:2169-2192）；③ **commAlloc**（src/init.cc:512-657）——parent 且 shareResources 时共享 sharedRes 与 memManager（src/init.cc:550-555），否则新建（src/init.cc:547-549）；④ initTransportsRank（src/init.cc:2196）；⑤ `initState=ncclSuccess` 发布（src/init.cc:2207），失败置错误码（:2249）。

### 4) initTransportsRank：三阶段核心（src/init.cc:1163）

**AllGather1**（src/init.cc:1234-1314）：`fillInfo`（src/init.cc:888-983）填本 rank 的 ncclPeerInfo——掺 commHash 的 hostHash/pidHash、GPU UUID、cuMem/GDR/CFT/GIN/RMA 能力位。全交换后对账：**版本不一致直接 fail**（src/init.cc:1273-1278）；能力位取全集群交集（src/init.cc:1280-1302），一个 rank 不支持就全体降级。

**拓扑与图**（src/init.cc:1381-1468）：ncclTopoGetSystem 探测 → ComputePaths → TrimSystem 裁不可达 GPU → 按算法族算图 ring/tree/CollNet/NVLS（src/init.cc:1423-1467）。

**AllGather3**（src/init.cc:1489-1738）：交换每算法图参数与 topoRanks，全集群对齐——图参数取各 rank 最小/最保守值（src/init.cc:1690-1698），**保证所有 rank 跑同一套图**；net/CollNet 设备数不齐默认报错、可 `NCCL_IGNORE_*_MISMATCH` 放行（src/init.cc:1576-1619）；CollNet 低于节点阈值自动禁用（src/init.cc:1721-1728）。

**连接与收尾**（src/init.cc:1755-1995）：computeBuffSizes 定三协议缓冲；profiler plugin 先于 proxy 线程（src/init.cc:1775-1786）；连接分两支——**runtimeConn**（cuMemSupport 且 NCCL_RUNTIME_CONNECT=1，默认）只 setupChannel+延迟建连（src/init.cc:1811-1819），否则一次性连好 ring/tree/PAT/NVLS/CollNet 与 PXN proxy（src/init.cc:1821-1864）。`devCommSetup`（src/init.cc:1952，实现在 src/init.cc:712-858）把 rankToLocalRank/buffSizes/channels 拷进 device 可见内存，CC 开则 workFifo=0（src/init.cc:750-763）——**必须在最后屏障前完成，防有人先跑 kernel 时内存没分配好而死锁**（src/init.cc:1950-1951 注释）；最后 bootstrapIntraNodeBarrier 屏障（src/init.cc:1969-1971）后恢复 CPU 亲和。

### 5) 拆除路径（src/init.cc:3205）

`ncclCommFinalize`（src/init.cc:3205-3253）防重入后投递 commDestroySync，完成后 state 由 inProgress 变 success。`ncclCommDestroy`（src/init.cc:3330）排队 `commReclaim`——**进程内最后一个 rank 的扫地僧**（src/init.cc:3255-3328）：finalizeRankCnt 原子计数凑齐同进程所有 comm，对未 finalize 的兄弟 comm 开线程补跑（src/init.cc:3282-3305）再统一 commCleanup。`ncclCommEnsureReady`（src/init.cc:493-510）是公共入口守门员：abortFlag 已置则 abort，inProgress 则拒绝复用。

## 三、外部连接

- **include 面**（图谱实测 28 条）：bootstrap/topo/transport/net/coll_net/proxy/enqueue/gin/rma/mnnvl/ras/param 等（27 个 NCCL_PARAM，src/init.cc:61-77）。
- **被谁调用**：公共 API 被 group.cc/collectives.cc 调用；ncclCommEnsureReady 被每次集合通信入口调用；`comm->devComm` 是设备侧 kernel 常驻输入。
- **与 bootstrap.cc 耦合**：Init/Split/AllGather/IntraNodeBarrier 四入口（src/init.cc:2165、2190、1238、1969）。

## 四、数据流

三个逐渐丰满的结构：**ncclComm**——src/init.cc:2882 裸壳 → commAlloc → initTransportsRank 填 channels/graphs → devCommSetup 造 devComm → initState inProgress→success，终点 commReclaim。**ncclPeerInfo[nranks+1]**（src/init.cc:1236，多一坑位给 CollNet root）——全交换 → 能力交集，长期驻留。**allGatherInfo[nranks]**（src/init.cc:1491-1533）——临时缓冲，消费完即 free。Init timings 日志（src/init.cc:2233-2240）是性能体检表。

## 五、设计决策

1. **异步 init + 立即发布句柄**：大集群 init 可达几十秒，blocking 模式把等待挪进后台线程（src/init.cc:2923-2929），`*newcomm` 先给、initState 后补。**两次 allgather**：第一次交换后才能做拓扑裁剪。
2. **能力协商全取交集**（src/init.cc:1280-1302、1690-1698）：异构集群"最弱 rank 决定全体"，避免 rank 间算法/通道不一致的静默数据错。
3. **failover 闸门全靠显式环境变量**：net/CollNet 数不齐与节点阈值默认 fail、可 opt-in 继续（src/init.cc:1591-1592）。
4. **devCommSetup 前置到最终屏障前**（src/init.cc:1950-1952）：同进程别的线程先启动 kernel 而设备内存没分配完就死锁。
5. **拆除的进程内聚合**：CUDA context/stream 池按进程共享，等最后一个 comm 结束才能放；原子计数+兄弟补跑收敛在一个函数。

## 六、新人提示

- **读代码路线**：先 src/init.cc:2105-2251 主线 → 分段啃 1163-1995（配 `NCCL_DEBUG=INFO` 跑一次 8 卡 init）→ 拆除读 3205-3340。
- **排 init 挂死**：九成卡在 bootstrap（04 篇）或连接阶段，`NCCL_DEBUG=INFO` 最后一条日志指明位置。
- **改 config 字段两头都要动**：nccl.h.in 结构体追加（01 篇）+ parseCommConfig/envConfigOverride（src/init.cc:2260 起），漏后者用户设置被静默忽略。
- split/shrink/grow 不是重新 init：复用 bootstrapSplit/parent bootstrap 与 sharedRes/proxyState。新公共 API 必先过 ncclCommEnsureReady（src/init.cc:493）。
