# 06 QueuePairFactory——连接引导：TCP 带外交换三元组，accept/connect/loopback 三入口

> 源文件：`src/infinity/queues/QueuePairFactory.h`（59 行）/ `src/infinity/queues/QueuePairFactory.cpp`（185 行）

## ① 角色定位

QP 转入 RTR 需要对端三元组（LID/QPN/PSN，见 QueuePair.cpp:94-104），而交换三元组时 RDMA 通路尚不存在——鸡生蛋问题。Factory 处于 L10，用**普通 TCP socket 做带外引导**解决它：先 TCP 交换连接参数，再 activate QP 进入可通信态。需勘误任务书一处：本库**不使用 rdma_cm，也没有事件循环**——rdma_cm 那套（rdma_bind/rdma_connect/事件回调）全仓零引用，Factory 是自建经典 socket 编程，accept/connect 全程阻塞单发。三个入口（QueuePairFactory.h:35/40/45）：acceptIncomingConnection（被动侧）、connectToRemoteHost（主动侧）、createLoopback（本机自连）。它同时是 RegionToken 跨机飞行的实际载体（握手 userData 槽）。

## ② 内部结构

**serializedQueuePair 协议结构**（QueuePairFactory.cpp:23-31）：定长报文 = localDeviceId(2)+queuePairNumber(4)+sequenceNumber(4)+userDataSize(4)+userData[1024]（Configuration.h:45 上限）——一次 send/recv 交换全部连接参数与附带数据，无多轮协商、无版本字段。

**成员极简**（QueuePairFactory.h:49-51）：context 指针 + `int32_t serverSocket`（仅被动侧用，主动侧不需要 bind）。

**五方法**：构造/析构（析构只关 serverSocket，QueuePairFactory.cpp:42-44）；bindToPort（被动侧前置）；三入口各返回一个**已完成 activate 并登记**的 QueuePair。

## ③ 外部连接

**依赖**：Context（new QueuePair 的原料 + registerQueuePair 登记）；QueuePair（activate/setRemoteUserData 都是 friend-only 接口，QueuePair.h:46/66-67，全库唯一合法调用方就是 Factory）；utils/Address（bindToPort 后打印 ib0 接口 IP，QueuePairFactory.cpp:68→Address.cpp:23）。

**被谁用**：两个示例的连接建立全部经它（read-write-send.cpp:59-60/73；send-performance.cpp:65-66/110）；图谱中 `QueuePairFactory.h→QueuePair.h` 与 `→Context.h` 两条边 + `.cpp→QueuePair.cpp` 调用边刻画了"工厂组装零件"的关系。**握手用户数据的巧妙复用**：read-write-send.cpp:60 把 RegionToken 当 userData 传——连接建立与凭证投递一步完成，省一轮消息。

## ④ 数据流

**bindToPort**（QueuePairFactory.cpp:48-72）：socket→SO_REUSEADDR（:59）→bind 到 INADDR_ANY:port（:62，sin_addr 经 memset 为全零即任意接口）→listen backlog 128（:65）。打印 ib0 IP 仅是提示信息，不影响实际绑定面。

**acceptIncomingConnection**（:74-116）：阻塞 accept（:82）→ **recv 先行**收对端三元组+userData（:85）→ new QueuePair（:89，此时 QP 在 INIT，QueuePair.cpp:60-65）→ 填 sendBuffer 本端三元组+userData 并 send 回去（:91-97）→ activate 进 RTR/RTS（:105）→ setRemoteUserData 存对端附带数据（:106）→ context->registerQueuePair 登记（:108，供 receive 反查来源）→ close 连接 socket（:110）。

**connectToRemoteHost**（:118-169）：inet_pton 解析 IP 字符串（:129，**只收点分 IP 不收域名**）→ connect（:135）→ **send 先行**再 recv（:146/:150）——与 accept 的 recv 先行严格互补，双方不会同时等对方先发而死锁。后续 activate/登记同构（:158-161）。

**createLoopback**（:171-181）：new QP 后**拿自己的三元组 activate 自己**（:174）——网卡对 self-QP 走环回路径，同进程自连，无任何 socket。userData 原样 setRemoteUserData 回自己（:175）——你的握手数据兜一圈回到 getUserData。

## ⑤ 设计决策

**TCP 而非 rdma_cm**：rdma_cm 优点是事件驱动+内置地址解析，代价是引入回调状态机与额外依赖；作者选 TCP 定长单发报文——百行内解决问题、行为完全可预测、跨 IB/RoCE 都有 TCP 可用（但 activate 写死 is_global=0，QueuePair.cpp:100，实际只通 IB）。这是 2015-2017 年原型的典型工程判断。

**定长 1KB userData 槽**：把"连接时捎带数据"做成一等能力，RegionToken 等凭证搭便车；上限检查用严格小于（:76/:120，1024 恰好满载会被拒）。

**阻塞单连接 per accept**：一次 accept 一条连接，多连接须循环调用或多线程——没有连接池、没有并发 accept；原型场景（两机 join 实验）够用。

**风险留白**：单次 recv 期望整份报文（:85/:150）——TCP 短读时默认编译（断言编译掉，Debug.h:21-24）会把半初始化的 calloc 缓冲当三元组用；无鉴权无加密，任何能连上端口的人都能拿到 QP。内网假设下的取舍。

## ⑥ 新人提示

上手顺序：先看 QueuePairFactory.cpp:23-31 的协议结构（握手的全部秘密就在这 1KB），再对照读 accept 与 connect 注意 send/recv 顺序互补，最后跑 createLoopback 写个不碰网络的自测。四个坑：①SERVER_IP 硬编码在示例里（read-write-send.cpp:22 的 192.0.0.1），换环境要改源码重编；②被动侧忘记先 bindToPort，accept 会在 serverSocket=-1 上失败；③loopback 的 userData 是"自己发自己收"，别误以为拿到了对端数据；④握手是纯阻塞的，对端不起 server 侧就永远挂起——调试时用两终端分别跑 `-s` 与客户端。验收自测：画出 accept/connect 各自的报文交换时序图，标出 new QueuePair 与 activate 的相对位置并解释为何 activate 必须在交换之后。
