# 10 地址与连接管理：getaddrinfo 族与 use_cm 二选一

## 一、角色定位

qperf 同时活在两个地址宇宙里：TCP/IP 世界（控制通道、socket/RDS 测试、RDMA CM 的引导）用域名+端口说话，InfiniBand 世界（传统 verbs 路径）用 LID+QPN+PSN 说话。把前者统一起来的是三层 getaddrinfo 封装——基底 `getaddrinfo_port`（support.c:381）、socket 线变体 `getaddrinfo_kind`（socket.c:691）、rdma CM 变体（rdma.c:1814 直接调基底）；把后者串起来的是 NODE 结构交换（rdma.c:98-114）与 ib_prep 的 QP 状态机。两条宇宙的分叉开关就是 `use_cm`：RC 传输下 `-cm` 走连接管理器（IP 语义），缺省走传统 IB 寻址（rd_open 的 if 分叉，rdma.c:1492-1495）。本篇解剖这条"名字→连接"的完整链路。

## 二、内部结构

**基底 getaddrinfo_port**（support.c:381-396）：标准 getaddrinfo 只认服务名，这里 `qasprintf("%d", port)` 把数字端口格式化成串，失败时用 `gai_strerror` 给出人话、空结果单列"no valid entries"。全仓所有地址解析的必经之路，五处调用（qperf.c:1424/1511、socket.c:709、rdma.c:1814、rds.c:435/472 另走裸 getaddrinfo）。

**控制通道两端**。server：`server_listen`（qperf.c:1416-1447）用 AI_PASSIVE|AI_NUMERICSERV + AF_INET6 绑定 ListenPort（缺省 19765，qperf.c:76）——AF_INET6 配 AI_PASSIVE 在双栈内核上同时接 IPv4/IPv6，bind 失败逐个 addrinfo 退试，SO_REUSEADDR 先行。client：`client_send_request`（qperf.c:1503-1547）用 AF_UNSPEC 遍历 getaddrinfo 返回的全部协议族逐个 connect；全失败且设了 ServerWait 时 `sleep(1)` 重试到超时——`-ws` 选项让 client 能先起再等 server 起来（qperf.c:1515-1532）。connect 成功顺手把对端地址 memcpy 进 ServerAddr（qperf.c:1527-1528，注意这对变量此后无人读，死存储，见 12 篇）。

**数据面端口中继**。socket 测试的数据连接不能用写死端口（多 client 并发会撞），于是控制通道兼职端口分配器：server 侧 `stream_server_init`（socket.c:621-660）以 Req.port（通常 0）bind → listen → `get_socket_port`（socket.c:738-755，getsockname+getnameinfo NI_NUMERICSERV 反查实际端口）→ `send_mesg(&port, 4, "port")` 告知 client → accept。client 侧 `client_init`（socket.c:586-618）先 `recv_mesg(&rport,...)` 收端口再 `getaddrinfo_kind(0, kind, rport)` 发起数据连接。datagram_server_init（socket.c:663-688）同构但免 accept。RDMA CM 路径复用同一招：`cm_open_server`（rdma.c:1863-1898）rdma_bind_addr(INADDR_ANY:0) → `rdma_get_src_port` 取回内核分配的 CM 端口 → 控制通道发"RDMA CM TCP IPv4 server port"消息（rdma.c:1875）→ client `cm_open_client`（rdma.c:1801）收端口后 getaddrinfo_port(ServerName, port) 解析、rdma_resolve_addr/rdma_resolve_route/rdma_connect 三段式建链（超时 = Req.timeout×1000ms，rdma.c:1810）。

**getaddrinfo_kind 的协议改写**（socket.c:691-723）：hints 按 serverflag 分叉（server 加 AI_PASSIVE 且强制 AF_INET6，client 保持 AF_UNSPEC）+ kind 分叉（UDP 改 SOCK_DGRAM）。解析完还有一段独特的后处理：SDP 把 ai_family 改写成 AF_INET_SDP（socket 加速协议的伪地址族）、SCTP 把 ai_protocol 换成 IPPROTO_SCTP，不适配的条目置 ai_family=0——下游 socket()/bind() 循环里 `if (!ai->ai_family) continue` 跳过（socket.c:597/628）。这是在没有专用 resolver 的年代模拟协议感知解析的务实手法。

**IB 传统路径的对端发现**。不走 CM 时，对端地址不靠 IP 而靠 NODE 结构（rdma.c:98-114：vaddr/lid/qpn/psn/srqn/rkey/alt_lid/rd_atomic 八元组）在 rd_prep 里通过控制通道裸交换（rdma.c:1519-1527，enc_node/dec_node rdma.c:2550+）。本地 NODE 的填充在 ib_open：`Req.id` 支持 "hca名:端口" 复合语法，`index(Req.id, ':')` 当场切串（rdma.c:2024-2035，注意它直接改写 Req.id 把冒号变 '\0'）；LID 取 `ibv_query_port` 的 port_attr.lid，且若端口支持 LMC（多路径 LID），叠加 `Req.src_path_bits & ((1<<lmc)-1)` 选定子路径（rdma.c:2088-2090）；PSN 用 `srand48(getpid()*time(0)); lrand48()&0xffffff` 随机化（rdma.c:2087/2127）。拿到对端 NODE 后 ib_prep（rdma.c:2153）把 dlid/静态速率/SL/src_path_bits 灌进 RTR，把 alt_lid/alt_port 灌进 RTS 的备用路径字段——`Req.alt_port` 与对端 alt_lid 同时非零才追加 IBV_QP_ALT_PATH|IBV_QP_PATH_MIG_STATE 标志（rdma.c:2234），启用 APM（自动路径迁移）测链路切换。

## 三、外部连接

- **向上**：do_option 的 `host` 类型把 ServerName 存为字符串（qperf.c:869）；`-lp` 改 ListenPort、`-ip` 改数据面 Req.port、`-ap` 改 RDMA 备用端口——三个端口选项各管一段，互不越界。
- **向下**：socket()/connect()/bind() 三系统调用族；rdmacm 库的 resolve/connect 事件流（cm_expect_event 逐事件校验，rdma.c:1943-1963）；verbs 的 query_port/modify_qp。
- **横向**：RDS 线不走 getaddrinfo_kind，自己拼 `qasprintf("%d", port)` 裸调 getaddrinfo（rds.c:435/472）——AF_INET+rds_sockets 的私货路径（05 篇）。remote_name（support.c:522-529）则是反方向的"名字"：错误报告时把对端称为 client/server。

## 四、数据流

`qperf -cm host rc_lat` 的寻址全流程：控制通道 connect（AF_UNSPEC 遍历）→ REQ 发出 → server rd_open 走 cm_open：cm_init 建事件通道+cm_id（portspace 按 RC/UD 选 RDMA_PS_TCP/UDP，rdma.c:1784-1794）→ cm_open_server bind:0 → CM 端口经控制通道回传 → client getaddrinfo_port(ServerName) → resolve_addr → resolve_route → rdma_connect → ESTABLISHED → rd_prep 的 NODE 交换退化为摆设（CM 模式下 lid/qpn 由 CM 协商，NODE 仍发但 rnode 字段基本不用）→ cm_prep 是空函数（rdma.c:1930-1933）。对照无 `-cm` 时：rd_prep 的 NODE 交换成为唯一对端发现手段，ib_prep 的 RTR/RTS 状态机手工把 QP 推到就绪。

## 五、设计决策

1. **端口中继而非约定端口**：数据面/CM 端口全由内核分配（bind:0）再经控制通道告知，天然支持同机多实例与端口占用冲突；代价是每个测试多一次 RTT。
2. **双栈绑定单点化**：只在 server_listen/stream_server_init 用 AF_INET6+AI_PASSIVE，client 用 AF_UNSPEC 全族遍历——2009 年 IPv6 过渡期的标准姿势，今天读来仍是可移植教科书写法。
3. **use_cm 缺省 0（传统 IB 路径）**：CM 当时对 UD/XRC 支持不全（rd_params 里只有 RC 开放 use_cm，rdma.c:1428-1433），且 CM 引导本身要多一轮 TCP+resolve；测纯 IB 性能时绕开 IP 栈才是"干净"的基准。二选一不是互斥功能，而是两套哲学：IP 兼容性 vs 原生寻址。
4. **PSN 随机化 + LMC 子路径**：PSN 随机让陈旧链路的残留包无法伪装新连接的合法包；src_path_bits 暴露 LMC 多路径这个 IB 特有拓扑能力，把"走哪条等价路径"变成可测参数。
5. **ai_family=0 的淘汰标记**：SDP/SCTP 改写失败不删链表节点（会破坏 freeaddrinfo 的链），置 0 让消费循环跳过——最小侵入的过滤术。

## 六、新人提示

- 排查连不上先分清是哪一段：控制通道（19765/ListenPort，看 `qperf -D` 的 connect 重试日志）、数据面端口中继（"port"消息）、还是 CM resolve（超时报错会点名 RDMA_CM_EVENT）。三段的地址族策略不同，混看会误诊。
- `-i` 在 CM 模式与 IB 模式下语义不同：CM 模式几乎无感（设备由 CM 选），IB 模式下 `hca1:2` 直接选 HCA 与端口——同一条选项在两个宇宙里权重完全不同。
- getaddrinfo_kind 对 SCTP 只改 ai_protocol 不改 socktype，前提是内核 SCTP 实现接受 SOCK_STREAM+IPPROTO_SCTP；在裁剪内核上 sctp_bw 报"could not make SCTP connection"多半是协议栈没装，不是 qperf 的锅。
- `index()` 是老式 legacy 函数名（strings.h），现代代码应换 strchr——这个 2009 年的写法在新 glibc 仍可用但会有移植性告警。
- ServerAddr/ServerAddrLen 是已知死存储（写不读），追地址去向时别被它迷惑，真正的消费者是各初始化函数里的局部 addrinfo 链。
