# 07 · 传输框架：src/transport.cc

## 一、角色定位

拓扑搜索给出"数据走哪条路"，调优模型给出"用哪个算法协议"，**传输框架把抽象通道变成真实互联**：为每 channel 每 peer 建 send/recv 连接、交换连接素材（IPC 句柄、NIC 地址）、把最终 `ncclConnInfo` 刷进 GPU 可见显存。`src/transport.cc`（493 行）是这层中枢：全局传输表 `ncclTransports[]`（transport.cc:15-20，按 p2p → shm → net → collNet 顺序注册）加一套选择/建连/回收协议。四类传输实现同一个 vtable（transport.h:148-154），具体在 transport/p2p.cc:1493、shm.cc:467、net.cc:2126、coll_net.cc:1862——本文件只写协议不写硬件。

## 二、内部结构

### 1. 传输选择：selectTransport（transport.cc:22）

模板参数 type 区分 recv(0)/send(1)（transport.cc:27-28）。对每个 peer 连接，按表序轮询 `canConnect`（transport.cc:33），**第一个返回 1 的传输胜出**并立即调它的 `setup`（transport.cc:36）生成本地资源与 `ncclConnect` 连接素材。表序即优先级：机内 P2P 可达就不用 shm，同 host 才 shm，跨机才 net。`ncclConnect` 是 256 字节不透明缓冲（`CONNECT_SIZE`，transport.h:76-81），各传输自定义内容（如 p2p.cc 的 `p2pConnectInfo`，用 static_assert 保证不超限，p2p.cc:45）。

### 2. 连接登记：ncclTransportP2pConnect（transport.cc:46）

不建连，只登记需求：把 peer 的 channel 位图 OR 进 `comm->connectRecv[peer]/connectSend[peer]`（transport.cc:56/63，mask 按 `1ULL << channel->id`）。调用方（ring/tree/collnet 的 connect 逻辑，如 coll_net.cc:1610、nvls.cc:208-211）先声明"这些 channel 要连这个 peer"，真正的建连统一由 P2pSetup 批量执行。

### 3. 类型探测：ncclTransportCheckP2pType（transport.cc:87）

对本地所有 rank 对调 `ncclTopoCheckP2p`（transport.cc:101），产出三个布尔：`isAllDirectP2p`（全部两两直连且距离不超 `NCCL_P2P_LEVEL`）、`directMode`（任两 rank 同进程，判据 hostHash+pidHash 相等，transport.cc:109-111）、`isAllCudaP2p`（CUDA 层 P2P 可达不论距离）。供上层决定 buffer 注册与 direct 通信策略。

### 4. 主流程：ncclTransportP2pSetup（transport.cc:125）

整个建连的编排者，四阶段：

- **setup 阶段**：以 i=1..nRanks-1 轮转取 `recvPeer=(rank-i)%nRanks`、`sendPeer=(rank+i)%nRanks`（transport.cc:153-154），对 mask 命中的 channel 逐个 `selectTransport<0>/<1>`（transport.cc:173-188）。每对 peer 的素材打包进 `data[p]`（前段 recv、后段 send，布局注释 transport.cc:158-163），经 bootstrap 以 `bootstrapTag=(i<<8)+(graph->id+1)` 交换（transport.cc:152、191-223）；sendPeer==recvPeer 时一次 send/recv 完成双向交换（transport.cc:191-201）。按 `NCCL_CONNECT_ROUND_MAX_PEERS`（默认 128，transport.cc:77）分轮（transport.cc:226）。
- **connect 阶段**：轮内对所有未完成连接循环调 `conn->transportComm->connect(...)`（transport.cc:247/270）消费对端素材。connect 可返回 `ncclInProgress` 表示依赖未就绪（如等 proxy 线程回包），循环直到 `allChannelsConnected`（transport.cc:229-302）。成功置 `conn->connected=1` 并 `cudaMemcpyAsync` 把 connInfo 刷到 `devPeersHostPtr` 槽位（transport.cc:252-254/275-277），让 GPU kernel 读到对端 buff 指针与 head/tail。
- **收尾同步**：全 rank 经 bootstrap 做一轮空消息 barrier（transport.cc:321-350）——注释解释了原因：快的 rank 返回后可能立刻销毁连接，慢 rank 还在 import 它的缓冲，不同步会产生非法 shmem/cuda 访问。随后清零 connect mask。
- **资源释放**：`data/recvData/sendData` 全 free，并做 `ncclStreamWaitStream(deviceStream, hostStream)` 保证显存侧的 connInfo 拷贝在返回前对 device stream 可见（transport.cc:361）。

### 5. CollNet 专用三件套

CollNet 是"多对一"的聚合传输，连接拓扑与 P2P 环/树不同，故有独立路径：

- `ncclTransportCollNetSetup`（transport.cc:375）：构造**虚拟 peer `peerInfo[nranks]`** 代表 collNet 资源根（transport.cc:385），每节点只有 master 执行 setup（transport.cc:406-409）。recv 侧全 rank `bootstrapAllGather` 收集 master 素材筛出 masterConnects（transport.cc:412-426）；send 侧由对端 recv master 传来的 connect 打底（transport.cc:427-430）。master 最终 connect 并把 connInfo 拷进 GPU（transport.cc:432-441）。**返回 bool 而非 NCCLCHECK**（transport.cc:374 注释）——collNet 失败回退 P2P network 而非报错。
- `ncclTransportCollNetCheck`（transport.cc:453）：节点内 AllGather 收集各 rank 的失败标志，任一失败整体放弃并 WARN "using point-to-point network instead"（transport.cc:466）。
- `ncclTransportCollNetFree`（transport.cc:472）：collNet peer（peers[nRanks]）挂 refCount，归零时对 send/recv 各 `NCCL_MAX_CONNS` 个 connector 调 `transportComm->free`（transport.cc:479-489）并清 `transportResources` 防二次释放。

## 三、外部连接

include：comm.h/info.h/bootstrap.h/timer.h/transport.h（transport.cc:8-13）。依赖 transport.h 的 vtable 三件（transport.h:129-154）、`ncclPeerInfo`（transport.h:46-74，**wire ABI 只能追加字段**，transport.h:44-45）、`ncclConnect`（transport.h:79-81）。被调：`ncclTransportP2pSetup`（init.cc:1890 全量建连、group.cc:222、nvls.cc:215、coll_net.cc:1613/1619）；`ncclTransportP2pConnect`（coll_net.cc:1610/1616/1644、nvls.cc:208-211）；CheckP2pType/CollNet 三件套被 init.cc 与 coll_net.cc 调用。协作：connector 结构 `ncclConnInfo`（device.h:136-159：buffs/tail/head/flags/ptrExchange/connFifo/step）由各传输填充；proxy 线程承接 transportComm 的 proxySetup/proxyConnect/proxyFree/proxyProgress 回调。

## 四、数据流

```
ring/tree/collnet 逻辑声明连接:
  ncclTransportP2pConnect → connectSend/Recv[peer] 位掩码   [transport.cc:46]
建连批量执行: ncclTransportP2pSetup                        [transport.cc:125]
  ① selectTransport: 轮询 canConnect → 胜者 setup
       产出本地资源 + ncclConnect 素材(256B)               [transport.cc:36]
  ② bootstrapSend/Recv 交换素材(send/recv peer 对称轮转)    [transport.cc:191]
  ③ transportComm->connect 消费对端素材
       ncclInProgress → 循环等待; 完成 → connected=1
  ④ cudaMemcpyAsync: connInfo → devPeers(GPU 可见)          [transport.cc:252]
  ⑤ bootstrap barrier 防竞态 + 清掩码                       [transport.cc:325]
运行期: GPU kernel 经 connInfo->buffs/head/tail 直接读写对端缓冲
销毁: transportComm->free(经各传输 free 链)
```

握手协议的关键在于：**setup 产素材（本地视角）、exchange 换素材（bootstrap 可靠传输）、connect 消素材（远端视角）** 三步拆开，connect 允许异步完成，从而兼容 net 传输需要 proxy 线程介入的场景。

## 五、设计决策

1. **表驱动 + canConnect 探测定优先级**：框架对传输实现零假设，优先级就是 `ncclTransports[]` 数组序（transport.cc:15-20），新传输（如未来 CXL）只需实现 vtable 并插表，选择协议不动。
2. **256 字节不透明 ncclConnect**：框架不解析连接素材内容，各传输自行编解码（p2p.cc:45 的 static_assert 只保证尺寸）。代价是素材结构升级需版本协商（peerInfo 带 version 字段，transport.h:65），换来框架与传输完全解耦。
3. **位掩码批量登记 + 分轮建连**：connectSend/connectRecv 是 per-peer 的 channel 位图（transport.cc:50-64），P2pSetup 按 128 peer/轮批处理，把 O(ranks×channels) 连接摊平成可控批次，留 `REPORT_CONNECT_PROGRESS` 进度条（transport.cc:288-301）。
4. **CollNet 失败即回退、永不阻断**：Setup 返回 bool、Check 全员表决（transport.cc:453-470），collNet 不可用只是性能降级为 P2P network；这是"尽力启用新硬件"与"可用性优先"的折中模板。
5. **收尾 barrier 由注释钉死**（transport.cc:321-324）：分布式建连的最后一课——建立侧完成不等于消费侧完成，销毁前必须全 rank 对齐，这类隐性时序约束全靠此处显式同步兜底。

## 六、新人提示

- 看建连日志：`NCCL_DEBUG=INFO,NCCL_DEBUG_SUBSYS=INIT`，每个连接一行 `Channel %02d/%01d : rank[dev] -> rank[dev] via P2P/direct|IPC|CUMEM|shm|...`，via 后缀直接告诉你选了哪个传输（输出在 p2p.cc:420-443 等各传输 setup 内）。
- 大规模建连卡住时开 `NCCL_CONNECT_ROUND_MAX_PEERS` 调整批量、`NCCL_REPORT_CONNECT_PROGRESS=1` 看进度百分比（transport.cc:288-301 的 ETA 估算）。
- 加新传输的三步：实现 `ncclTransport` vtable（transport.h:148）→ 插入 `ncclTransports[]`（注意位置即优先级）→ 素材结构加 static_assert 防超 256B。
- 排查"连接建立但通信挂死"：先看 devPeersHostPtr 拷贝是否在 connect 完成路径上（transport.cc:252/275），再查对端 connect 是否返回了 inProgress 却永远没就绪——多数是 proxy 线程死了。
- `ncclPeerInfo` 是跨版本 wire 结构：改它只能向尾部追加字段（transport.h:44-45 注释），中间插入会让新旧 NCCL 混布集群全崩。
