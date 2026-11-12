# 11 · proxy：代理线程（proxy.cc）

## ① 角色定位

`src/proxy.cc`（2230 行）实现 NCCL 的"代理"：进程内每 GPU 一组线程（非独立进程），替 CUDA kernel 收发跨节点数据。GPU kernel 只写共享缓冲并翻转指针，真正调 `ncclNet->isend/irecv/test` 的是 Progress 线程；Service 线程是本进程所有 comm 的总机，接收主线程与 peer 的控制命令（建连、MR 注册、fd 传递）并按需拉起 Progress；UDS 辅助线程专管 cuMem fd 跨进程序列化。三线程在 `ncclProxyCreate` 创建（`proxy.cc:2157-2163`）。

## ② 内部结构

**命令通道（TCP/UDS 两种 service）**。主线程与 proxy 的 RPC 走 Unix socket：`ncclProxyConnect`（`proxy.cc:1166-1249`）为每个 top-parent rank 建持久 peerSock，发 MsgInit 得 `ncclProxyConnection*` 句柄；后续命令经 `ncclProxyCallAsync`（`proxy.cc:1369-1394`）异步发出、`ncclPollProxyResponse`（`proxy.cc:1396-1462`）轮询回包，不匹配当前 opId 的响应缓进 expectedResponses 链表乱序匹配；消息类型表见 `proxy.cc:1367-1368`。UDS 通道独立：`ncclProxyServiceUDS`（`proxy.cc:2044-2109`）监听 ipcSock 只处理 GetFd/QueryFd——cuMem handle 经 `cuMemExportToShareableHandle` 转 fd 传对端（`proxy.cc:1601-1624`），或反向查询远端 fd（`proxy.cc:1584-1598`）。

**Service 线程主循环（`ncclProxyService`，`proxy.cc:1789-2016`）**：poll 监听 socket+全部 peer socket，timeout 500ms（有异步 op 时 0ms）保证能及时响应 abort（`proxy.cc:1849`）。新连接 accept 进 peers 数组（`proxy.cc:1883-1907`）；命令进入 `proxyServiceInitOp`（`proxy.cc:1702-1766`），先校验 connection 归属与 Init 的 transport/rank 边界（`proxy.cc:1713-1748`），再入 asyncOps 链表由 `proxyProgressAsync`（`proxy.cc:1626-1700`）分派到传输层虚表，完成时经 socket 回响应头+respBuff（`proxy.cc:1681-1689`）。MsgStop/Close 触发关停（`proxy.cc:1957-1967`）；退出条件是 stop 且 npeers==0——注释强调 abort 后仍要等所有 peer 安全退出，否则段错误（`proxy.cc:1842-1846`）。

**Progress 线程与 ops pool**。数据面命令不走 socket：主线程把 ncclProxyOp 写进**共享内存池** `ncclProxyOpsPool`（`proxyProgressInit` 在 /dev/shm/nccl-XXXXXX 建池并初始化 per-rank freeOps 链，`proxy.cc:1483-1527`），`ncclProxyPost`（`proxy.cc:476-486`）持锁挂链并 cond 唤醒。Progress 循环（`ncclProxyProgress`，`proxy.cc:951-1011`）：active 链逐 op 调 progress 回调（`progressOps`，`proxy.cc:796-826`）；空闲或每 PROGRESS_APPENDOP_FREQ（默认 8）轮才取新 op——频繁取 op 拖慢小消息（`proxy.cc:969-974` 注释）；全空闲时 cond 阻塞（`proxy.cc:844-855`）。取 op 按 (opCount,peer) 分批（默认 16，`proxy.cc:828,871-892`），CAS 还槽位（`proxy.cc:894-908`）。

**op→args 聚合**。取到的 op 经 `ProxyAppend`（`proxy.cc:437-474`）转成 `ncclProxyArgs`：同 peer 同 opCount 的 op 合并进一个 args 的 subs 数组（跨 comm 共享数据的聚合，`proxy.cc:443-446`）；不同 opCount 挂 nextPeer 链。`ncclProxyOpToArgs`（`proxy.cc:368-435`）把 chunkSteps/nsteps/loopSize/buffer 句柄拷进 sub，并绑定两个关键函数指针：`args->progress=connection->tcomm->proxyProgress`（传输层进度回调）与 `proxyAppendPtr`（后续同组 op 的追加位置）。ncclProxyArgs 从 `ncclProxyPool` 池分配，避免数据路径 malloc（`proxy.cc:207-231`）。

## ③ 外部连接

- 上游 enqueue：`uploadProxyOps` 调 `ncclProxySaveOp`（`proxy.cc:591-761`）——这是**回调注册表**式分发：按 pattern 决定给谁发代理（Ring/Pipeline 全员、Tree 按 up/down、Collnet/NVLS 只给 out、PAT 先在 CPU 上跑一遍 PatRS/PatAG 算法数出每个 peer 的步数 `proxy.cc:667-750`、Send/Recv 给 root）；`NeedProxy`（`proxy.cc:35-47`）判断链式算法中哪个 rank 免代理。
- 传输层：connection->tcomm 指向 `ncclTransports[]` 的 send/recv 虚表，proxySetup/proxyConnect/proxyRegister/proxyProgress 全部由 p2p/net/collNet 各传输实现，proxy.cc 只做编排。
- net_ib 后端的 isend/irecv/iflush 由 Progress 线程驱动；buffer 注册（Register/Deregister）经 Service 线程走 socket RPC。
- 生命周期：`ncclProxyInit`（`proxy.cc:2111-2128`）随 comm 初始化建 proxyState 与 ipcSock；`ncclProxyStop`（`proxy.cc:2168-2211`）在 refCount 归零时向自己发 MsgStop 并关 peer socket；`ncclProxyDestroy` 释放残余。

## ④ 数据流

一次跨节点 AllReduce 的 proxy 视角：

1. **握手**：enqueue 侧 hostStreamPlanTask 调 `ncclProxyStart`（`proxy.cc:1013-1028`）把主线程攒的 op 链经 ncclProxyPost 移交 pool 并唤醒 Progress。
2. **取批**：Progress 从 pool 取一批 op，按 peer/opCount 聚合成 ncclProxyArgs（每 sub 对应一个 channel 的一段数据）。
3. **推进**：args->progress 回调（net 传输的 netProgress）按 nsteps 循环：攒够 NCCL_STEPS 步的 isend/irecv 到 channel 缓冲，轮询 test、收到 GPU 写完的数据再发下一批——GPU 侧同步靠 connector 的 head/tail 指针。debug 视图见 `printProxyOp` 状态机注释（I/R/F/G/D 五态，`proxy.cc:265-289`）。
4. **完成**：所有 sub 的 done==nsteps 时 op 置 ncclProxyOpNone，`removeOp`（`proxy.cc:763-794`）把 args 还池并维护 nextPeer/active 链。
5. **停止**：comm 销毁→MsgStop→Service 循环退出前先 `ncclProxyProgressDestroy` join Progress 线程（`proxy.cc:1039-1065`）再释放连接池与 shm。

## ⑤ 设计决策

- **shm 池而非 socket 传数据面命令**：数据面 op 速率高且大（数百字节），socket 每次 syscall 太贵；ops pool 用免锁的 per-rank freeOps 链+一个互斥的 nextOps 队列，热路径只有一次 CAS。
- **聚合优先**：同 peer 同 opCount 的多 channel op 合并成一个 args 一次 progress 调用，摊薄循环开销；这正是 enqueue 端 opCount 编码（coll 偶/p2p 奇）与 finishPlan 归并排序的对偶。
- **两个 service 线程职责分离**：TCP Service 管低频控制命令，UDS 线程管 fd 传递——fd 必须经 SCM_RIGHTS 传递，故独立 ipcSock；poll 永不无限阻塞（500ms 超时）保证 abortFlag 可达（`proxy.cc:1847-1848,2068` 注释）。
- **每 GPU 而非每 comm 一组线程**：proxyState 挂 sharedRes、以 refCount 共享给 split comm（`proxy.cc:2130-2134` 注释），避免多 comm 场景线程爆炸；progress 线程设置 CPU 亲和（NCCL_PROXY_CPUSET，`proxy.cc:925-949`）避开与计算核争抢。
- **防错设计**：Init 做 connection 归属校验防伪造（`proxy.cc:1097-1121`）；setup/connect 完成后不再返回错误防 use-after-free（`proxy.cc:1676-1679` 注释）；PROXY_DUMP_SIGNAL 可 dump active 链辅助排查 hang（`proxy.cc:917-922`）。

## ⑥ 新人提示

1. 记口诀：Service 管"建立"（连接/注册/fd），Progress 管"搬运"（isend/irecv/test）；日志前缀分别标 [Service thread]/[Proxy Progress]。
2. 调 hang 先设 `NCCL_PROXY_DUMP_SIGNAL`，对进度线程发信号即可打印 active 链每个 op 的 I/R/F/G/D 状态（`proxy.cc:917-922`），G 态多=GPU 没写完，S/R 态多=网络慢。
3. 读 `ncclProxySaveOp` 的 switch 就是读各算法的通信拓扑：Tree 分 Up/Down 两半、Collnet/NVLS 只在 out 上、PAT 要 CPU 预演算法——这份 switch 是理解"哪些 rank 需要代理"的最短路径。
4. shm 池文件在 /dev/shm/nccl-*，异常退出可能残留；ops pool 的 freeOps CAS 链是并发热路径，改动前先理解 ncclProxyGetPostedOps 的批处理边界。
5. 常考"为什么不用独立 proxy 进程"：本版是线程实现（历史上有过进程版），同进程换来零 IPC 开销，代价是 comm 崩溃可能拖垮 proxy——500ms poll 超时与 stop 序列（`proxy.cc:2168-2211`）就是兜底。
