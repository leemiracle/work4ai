# 03 · TCP 原语与建连：sock.c 线

## ① 角色定位

sock.c（179 行）+ sock.h 提供 RDMA 建连**之前**的带外（out-of-band）信息通道，在图谱中占"TCP 带外通道原语"（第 6 层）与"QPInfo 带外交换"（第 7 层）两层，tour 第 7/8/9 步。它存在的理由是 RDMA 的鸡生蛋问题：要把一条 RC QP 迁到 RTR 状态，必须知道对端的 qp_num 和 lid；而这两个值要 QP 创建之后才存在——**RDMA 网络自己无法承载"第一次认识"的流量**，必须借一条已经能用的网络（TCP）把 QP 地址信息递过去。本仓选择手写这条通道而不是用 rdma_cm，是全仓最重要的教学决策之一（见第 ⑤ 节）。

六个函数两两成对：sock_read/sock_write（可靠字节流）、sock_create_bind/sock_create_connect（建连）、sock_set_qp_info/sock_get_qp_info（QPInfo 序列化）。

## ② 内部结构

**读写原语**：

- **sock_read**（sock.c:11-31）：定长循环读。`while (len != 0 && (nr = read(...)) != 0)` 直到读满 len 字节；nr<0 时 EINTR 则 continue 重读（sock.c:19-20），其余错误返回 -1（sock.c:22）；对端关闭（read 返回 0）直接跳出返回已读数，由调用方校验短读。L14 的 `char *buf = buffer` 注释写明是避免对 void 指针做算术。
- **sock_write**（sock.c:33-53）：镜像的定长循环写，EINTR 容错在 sock.c:42-43。

**建连原语**（结构完全对称的 getaddrinfo 三段式）：

- **sock_create_bind**（sock.c:55-98）：memset hints 后设 SOCK_STREAM/AF_UNSPEC/AI_PASSIVE（sock.c:61-64）——AI_PASSIVE + node 传 NULL 意味着 bind 通配地址；getaddrinfo 返回候选链表（sock.c:66），for 循环逐个 socket+bind，bind 成功即 break（sock.c:69-83），失败 close 换下一个。IPv4/IPv6 都愿意试。
- **sock_create_connect**（sock.c:100-142）：同构，getaddrinfo 解析服务器名（sock.c:110），循环 socket+connect 直到某个地址连上（sock.c:113-127）。错误路径 freeaddrinfo + close（sock.c:134-141）。

**QPInfo 序列化对**（sock.c:144-178）：sock_set_qp_info 把 lid/qp_num/rank 三字段经 htons/htonl 转网络序到栈上临时结构（sock.c:149-151），按 `sizeof(struct QPInfo)` 整块 sock_write（sock.c:153）；sock_get_qp_info 整块 sock_read 后 ntohs/ntohl 还原（sock.c:167-172）。QPInfo 定义在 ib.h:29-33，`__attribute__((packed))` 压掉填充，线上定长 **10 字节**（uint16+uint32+uint32）——packed 保证发送方栈结构与接收方逐字节对齐，这就是"整块传输"可行的前提。

sock.h:8 还定义了 `SOCK_SYNC_MSG "sync"`，但 sync 收发不走 sock.c 的函数，直接由 setup_ib.c 调 sock_read/sock_write 完成（见 05 篇）。

## ③ 外部连接

sock.h:6 include ib.h 复用 QPInfo 结构——sock 模块因此是"传输工具+协议载荷"的合体，但它不依赖任何 RDMA 运行时。上游调用方全部在 setup_ib.c 的两个建连编排函数里：connect_qp_server 用 sock_create_bind（setup_ib.c:25）、accept（setup_ib.c:33，系统调用直接用）、sock_get_qp_info/sock_set_qp_info（setup_ib.c:55/70）、sync 收发（setup_ib.c:96/101）；connect_qp_client 用 sock_create_connect（setup_ib.c:143）与对应的收发（setup_ib.c:161/171/200/205）。sock_read/sock_write 不被 client.c/server.c 数据面使用——TCP 在建连完成后即退役。图谱方向 sock→ib(仅头文件)→debug，是叶子模块。

## ④ 数据流

一次完整建连的 sock 线数据流（2×2 拓扑为例）：

1. **监听侧**：server 进程 sock_create_bind(port) 得到监听 fd → listen(sockfd, 5)（setup_ib.c:27）→ 循环 accept 收齐 num_peers 个连接（setup_ib.c:32-36），accept 顺序即 peer_sockfd[] 下标。
2. **连接侧**：client 进程对 config_info.servers[i] 逐个 sock_create_connect（setup_ib.c:142-146），连接顺序即数组下标——client 侧下标天然等于 server rank。
3. **QPInfo 上行**：client 把本端 {lid, qp_num, rank} 整块发出（setup_ib.c:160-163 → sock.c:149-153），server 在每个 accept 出的 fd 上整块读入 remote_qp_info[i]（setup_ib.c:54-57）。
4. **QPInfo 下行**：server 按 rank 配对后回发本端 QP 信息（setup_ib.c:62-71）。
5. **sync 双向握手**：client 先写后读（setup_ib.c:199-207），server 先读后写（setup_ib.c:94-103），5 字节同步字（`sizeof(SOCK_SYNC_MSG)`=5，即 "sync" 4 字符+结尾 NUL）内容无意义，纯粹当屏障用。
6. **退役**：全部建连信息交换完毕，双方 close 所有 fd（setup_ib.c:105-109/209-212），此后通信 100% 走 RDMA。

字节序链路值得记住：本地主机序 → htons/htonl（sock.c:149-151）→ 网络序线上字节 → ntohs/ntohl（sock.c:170-172）→ 对端主机序。imm_data 在数据面走同一条链（ib.c:94 的 htonl 与 server.c:103/client.c:130 的 ntohl），与 QPInfo 一致。

## ⑤ 设计决策

**① 手写 TCP 带外而非 rdma_cm**：rdma_cm（本仓甚至链接了它，Makefile:5 的 -lrdmacm 但全仓零调用）可以把 QP 信息交换藏在 rdma_connect/rdma_accept 后面，一行代码换一个黑盒。本仓反其道：bind/listen/accept/connect、QPInfo 10 字节、sync 握手每一步都摊开可见——教学价值优先，学生能精确看到"RC 连接 = 交换 {lid, qp_num} + 双方各改一次 QP 状态"。代价是多写 200 行且要自己处理配对（05 篇的 accept 顺序假设即源于此）。

**② 定长整块传输而非文本协议**：QPInfo packed 定长 10 字节，配 sock_read 的"读满为止"循环，天然免疫 TCP 短读——不需要分隔符、不需要长度前缀。这是二进制带外通道的最小实现。

**③ EINTR 容错内聚在原语层**：信号打断 read/write 是长跑进程的常态，sock.c:19-20/42-43 在最底层消化，调用方完全不感知。

**④ getaddrinfo 而非固定 sockaddr_in**：AF_UNSPEC + 候选链表遍历（sock.c:63/69-83）让代码同时接受 IPv4/IPv6 解析结果，2014 年的代码里这是现代写法。

**⑤ accept 用裸系统调用**：accept 不在 sock.c 封装（setup_ib.c:33 直接调），因为 accept 的语义（收齐 N 个、按下标管理）属于建连编排层——工具与编排的分界线画在"单连接操作"与"多对端拓扑"之间。

## ⑥ 新人提示

读 sock.c 顺序：先 sock_read/sock_write（注意 read 返回 0 是对端关闭、不是错误），再两个 create 函数（对照 for 循环里"失败 close 换下一个"的容错），最后序列化对。三个易踩点：① `sizeof(SOCK_SYNC_MSG)` 是 5 不是 4——字符串字面量含结尾 NUL，sync 按字节计数所以无碍，但若有人改成 strlen 会两边不一致；② sock_read 对"对端中途关闭"返回已读字节数，调用方靠 `check(n == sizeof(...))` 抓短读（sock.c:154/168），这不是冗余而是必要防线；③ 端口复 string 而非 int（getaddrinfo 的 service 参数，sock.c:66/110），main.c:26 直接把 argv[2] 塞进来，端口合法性由 getaddrinfo 代为校验。

想实验：把 QPInfo 加一个字段（如对端 num_qps），只需改 ib.h:29-33 的结构——packed 序列化对会自动带上它，这正是二进制定长协议的可扩展红利。反过来，理解了这条 sock 线，rdma_cm 做的就是同样的事，只是协议换成了 RDMA 侧的 CM 报文。
