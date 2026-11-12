# 04 · bootstrap.cc — 带外建链网：root/uniqueId 与 proxy 通道

## 一、角色定位

NCCL 正式通信靠 NVLink/IB/Socket，但传输的建立本身需要先互相知道地址——鸡生蛋问题。`src/bootstrap.cc`（1594 行）就是那个"蛋"：**用最朴素的 TCP socket 先织一张临时带外网（out-of-band）**，服务 init 期的寻址交换、节点内屏障与 proxy 通道引导。init 后它不退出：`bootstrapAllGather/Send/Recv` 运行期仍被约 16 个文件使用（src/gin/gin_host.cc、src/transport/coll_net.cc 等）。它与 ncclUniqueId 的关系是本质性的：用户广播的 128 字节 ID，内容就是 `ncclBootstrapHandle{magic,addr,nRanks}`（src/include/bootstrap.h:14-18）——root 地址 + 随机 magic，即"会师地点 + 暗号"。

## 二、内部结构

### 1) 网卡选择与 socket 握手层（src/bootstrap.cc:106-141）

`bootstrapNetInit` 进程内一次：设了 `NCCL_COMM_ID`（ip:port）则按"能路由到该地址的子网"选网卡（src/bootstrap.cc:120-121），否则自选第一块网卡。默认 TCP；`NCCL_OOB_NET_ENABLE=1`（src/bootstrap.cc:106，默认 0）改用 ncclNet 插件（src/bootstrap.cc:565-616）。底层 `ncclSocket`（src/include/socket.h:92-110）带 magic 与 crypto 指针：连接握手交换 magic，不匹配进入 BadHandshake（src/misc/socket.cc:504-508）——magic 由 getRandomData 生成（src/bootstrap.cc:455）挡住误连；另有 PSK/TLS 选项（src/misc/crypt.cc:460）。

### 2) root 线程：会师服务员（src/bootstrap.cc:279）

`bootstrapCreateRoot`（src/bootstrap.cc:408-431）绑 uniqueId 地址监听，起 detached 线程跑 `bootstrapRoot`。root 逻辑（src/bootstrap.cc:291-406）是"婚介所"：循环 accept，**从第一个连接学参数**（src/bootstrap.cc:322-335）——root 无需事先知道规模。每收到一个 rank 的 `extInfo`（src/bootstrap.cc:267-275）就做**前后向撮合**：若"前一 rank"已报到，立即把它要的 next 信息推给它（rootSend，src/bootstrap.cc:279-290）否则先存；对称处理"后一个"（src/bootstrap.cc:354-372）。效果：每 rank 只从 root 收一条消息，root 发送量 O(N) 而非 O(N²)。多 root 由纯函数组完成 rank→root 均分（src/bootstrap.cc:51-93），支撑 `ncclCommInitRankScalable`。

### 3) uniqueId 生成与 grow（src/bootstrap.cc:433）

`bootstrapGetUniqueId` 两条路：设了 `NCCL_COMM_ID` 则解析远端 root 地址、magic 固定 NCCL_MAGIC（本 rank 不当 root，src/bootstrap.cc:436-449）；否则随机 magic 并就地 bootstrapCreateRoot（src/bootstrap.cc:450-460）。grow 的 magic 由 parent 派生（src/bootstrap.cc:451-453），与 src/init.cc:2173 互为镜像。

### 4) bootstrapInit：从 uniqueId 到可用环（src/bootstrap.cc:754）

每 rank 建环流程（状态结构 src/bootstrap.cc:527-546）：① magic 定锚；② 建监听——环邻居口（src/bootstrap.cc:806-809）、root 回连口（用 root 的 magic 握手，src/bootstrap.cc:826-830）、P2P 口；③ **错峰**——每 root 名下 rank 数超 `NCCL_UID_STAGGER_THRESHOLD`（默认 256）时按 7000/s 线性延迟（src/bootstrap.cc:833-843）；④ sendToRoot 上报 extInfo（src/bootstrap.cc:845-866），阻塞等 root 推来 next 邻居（src/bootstrap.cc:869-883）；⑤ 建环——连 next、accept prev 同时进行（src/bootstrap.cc:687-700）；TLS 下 connect 阻塞到对端 accept，故 `bootstrapConcurrent`（src/bootstrap.cc:648-669）起 helper 线程防全环死锁；⑥ 建 proxy 监听与 UDS 地址（:899-905）；RAS 失败也**参与 ringAllInfo**（:916-932）；⑦ `ringAllInfo`（:701-735）全交换四类地址；⑧ `ncclProxyInit`（:941）立起 proxy 通道。

`bootstrapSplit`（src/bootstrap.cc:966-1060）是同构轻量版：不走 root，直接借**父 comm 的通道**给新环 prev/next 交换地址（src/bootstrap.cc:1013-1017）。

### 5) 运行期原语（src/bootstrap.cc:1062）

- **P2P 定向消息**：`bootstrapSend` 连对端 peerSocket，先发 `{rank,tag}` ACK 再发数据（src/bootstrap.cc:1067-1081）；接收侧按 (peer,tag) 匹配，不匹配的进 **unexpected 队列**（src/bootstrap.cc:1219-1300）——来者先收、对号入座。tag 常量见 :25-29。
- **TLS 异步发送**：加密下 send-only socket 也得收 TLS 握手，每次发送复制 payload 起线程异步跑；同 (peer,tag) 必须保序，靠 in-flight 队列"同键最早者先行"（src/bootstrap.cc:1124-1152）；失败置 abortFlag 暂存，下次操作冒出（src/bootstrap.cc:1307-1315）。
- **AllGather**：socket 路径用**双向双环**（src/bootstrap.cc:1363-1412），N rank 只需 ⌈N/2⌉ 步；net 路径单向环（src/bootstrap.cc:1326-1362）。**Barrier**：dissemination 算法 log₂(N) 轮（src/bootstrap.cc:1440-1455）。

`bootstrapClose`（src/bootstrap.cc:1558-1594）：drain 异步发送；unexpected 队列滞留视为错误（:1571-1577）；关 socket、delete state。

## 三、外部连接

- **被谁调用**：src/init.cc 是最大客户——bootstrapInit（src/init.cc:2190）、bootstrapSplit（src/init.cc:2165）、bootstrapAllGather（src/init.cc:1238、1533）、bootstrapIntraNodeBarrier（src/init.cc:1969）；运行期另有 gin_host/coll_net 等用户。
- **include 面**（图谱）：nccl.h/core/net/proxy/param/ras/crypt/os 等（:8-22）。
- **下层**：src/misc/socket.cc 与 crypt.cc；**上层** `ncclProxyInit` 建常驻 proxy 通信。

## 四、数据流

单机 8 卡典型流：① rank0 ncclGetUniqueId → 随机 magic+地址+起 root 线程，uniqueId 广播；② 各进程 bootstrapInit：开两个监听向 root 报到，互连成环；③ 两次 bootstrapAllGather 沿双环各转 4 步收齐 peerInfo 与图信息；④ ringAllInfo 交换 proxy 地址，ncclProxyInit 立通道；⑤ init 后环降级为控制面；⑥ destroy 收摊。`ncclBootstrapHandle` 生命周期最短（生成→广播→即弃）；bootstrapState 与 comm 同生命周期；unexpected 队列滞留到 close 即 bug 信号（src/bootstrap.cc:1571-1577）。

## 五、设计决策

1. **环形而非星形**：root 只"婚介"不"转发"——数据交换走 rank 直连环，root 带宽不随 N 膨胀。
2. **magic 随机化**：防误连 + 安全边界。
3. **root 从首连接学习规模**（src/bootstrap.cc:322-335）：协议无带外元数据，免"先广播 nranks"。
4. **错峰（stagger）**：阈值 256、7000 conn/s 限速——防 root accept 队列与对端 connect 超时共振。
5. **unexpected 队列**：与其规定严格时序，不如"先收下按 (peer,tag) 对号"。**RAS 失败也要参与 ringAllInfo**（src/bootstrap.cc:926-930）："独自退出"会让同伴挂死。
6. **abort 粒度**：长循环每 10000 次迭代查 abortFlag（src/bootstrap.cc:150-159），ncclCommAbort 秒级打断建链。

## 六、新人提示

- **读代码路线**：先 src/include/bootstrap.h（39 行）→ bootstrapRoot（src/bootstrap.cc:291-406）与 bootstrapInit（src/bootstrap.cc:754-964）对照读（一个发端一个收端）→ 运行期原语（src/bootstrap.cc:1062-1438）。画时序图胜过读十遍。
- **排 init 卡死**：症状是所有 rank 停在 "Bootstrap : Using..." 之后。先查 uniqueId 是否真到每个 rank（magic/地址错则 root 永远等不齐）；多机查 NCCL_COMM_ID 与网卡选择（src/bootstrap.cc:112-131 选错网卡是经典事故，`NCCL_SOCKET_IFNAME` 强制指定）；千卡以上慢是 stagger 设计。
- **加新消息类型**：永远带 tag（src/bootstrap.cc:25-29）；TLS 下注意 (peer,tag) 保序（:1102-1106）。
- **别发大数据**：socketSend 先发长度再发正文（src/bootstrap.cc:218-222），无流水线。
- 与 03 篇衔接：src/init.cc:2165-2192 的分岔决定进 bootstrapSplit 还是 bootstrapInit，改任一侧都要检查另一侧。
