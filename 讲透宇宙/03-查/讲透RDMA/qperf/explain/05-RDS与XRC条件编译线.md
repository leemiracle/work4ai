# 05 RDS 与 XRC：两条条件编译线

## 一、角色定位

qperf 代码库里有两个"时代的切片"：rds.c（554 行）实现 RDS（Reliable Datagram Sockets）测试，是 2012 年 Intel 加入的内核套接字协议遗产；rdma.c 中的 XRC（eXtended Reliable Connection）块则是 OFED 1.4 时代可望不可及的硬件特性，被 `#ifdef HAS_XRC` 整体包裹。两者共同点是都活在条件编译之后、都在现代环境大概率缺席，但缺席方式不同：RDS 是独立文件无条件编译（rds.c 不在 Makefile.am 的 RDMA 分支里，socket 线之外的自由身），XRC 是构建期探测的"可能不存在"。读懂这两条线，等于读懂 C 项目如何用预处理器管理能力矩阵。

## 二、内部结构

### RDS 线（rds.c）

**AF_RDS 的三级兜底**（rds.c:52-91）是全文件最有戏的部分：`#ifndef AF_RDS` 时自定义 `get_af_rds()`——静态变量缓存，首次调用读 `/proc/sys/net/rds/pf_rds`（rds.c:67，RDS 还没进主线内核时以模块形式动态注册地址族的遗迹），读到就用之；否则报 `error(RET, "AF_RDS not defined...Using 21.")` 并落回硬编码 `DEFAULT_AF_RDS 21`（rds.c:58）。`#define AF_RDS get_af_rds()`（rds.c:90）让后面代码照常写 `socket(AF_RDS, ...)`。

**无连接语义的变通**是 RDS 线的设计主题。RDS 用 SOCK_SEQPACKET（rds.c:412）——有界消息但不可 connect，于是 init（rds.c:293-314）要解决"两端互相知道对方地址"：

1. `server_get_hosts`（rds.c:330-374）：server 另开一条 **TCP** 副通道（AF_INET6 bind 临时端口），把端口经控制通道发给 client，accept 后从 accept 得到的对端地址提取 client IP——`ipv6_addr_v4mapped`（rds.c:320-324，s6_addr32 三字或运算判 ::ffff:0:0/96 前缀）把 v4-mapped 地址折回 AF_INET（rds.c:361-369）。
2. `client_get_hosts`（rds.c:381-399）：connect_tcp（rds.c:461-491）连上副通道，get_socket_ip 取 server IP。
3. 两端各自 `send_mesg(rhost)`+`recv_mesg(lhost)` 互换 IP 字符串，再各自 rds_socket bind 本端、交换 RDS 端口（init rds.c:306-311），rds_makeaddr（rds.c:427-454，getaddrinfo 后按 AF_INET/AF_INET6 组 sockaddr 填 htons 端口）构造对端 RDS 地址存入静态 RAddr/RLen（rds.c:115-116）。

数据面四个入口：rds_bw 的 client 用 `sendto(RAddr)` 发（rds.c:136）、server 用 `read` 收（rds.c:168）；rds_lat 乒乓 client sendto/read（rds.c:202-213）、server recvfrom/sendto 回射（rds.c:246-257）。判错口径是 `n != Req.msg_size` 而非 n<0——SEQPACKET 语义下短包即错。默认尺寸 bw 8K（rds.c:130）。

### XRC 块（rdma.c 内 #ifdef HAS_XRC）

XRC 入口六件套全在 rdma.c:770-840 一段：run_client_xrc_bi_bw（L774）、run_client_xrc_bw（L798）、run_client_xrc_lat（L824）及三个 server 对应（L788/L814/L835），结构与 RC 版逐字相同，仅传输类型换成 IBV_QPT_XRC。深层差异散布在 rdma.c 各处的 HAS_XRC 卫兵里：

- rd_create_qp（rdma.c:1679-1701）：ibv_open_xrc_domain（O_CREAT）+ ibv_create_xrc_srq 共享接收队列，随后 `qp_attr.cap.max_recv_wr = 0` 把 QP 自身 RQ 清零——接收全走 SRQ；
- ib_open INIT 状态（rdma.c:2107-2111）与 ib_prep RTR/RTS（rdma.c:2211-2215）：XRC 与 RC 同支路（RC 的 access flags 全开）；
- rd_post_send（rdma.c:2401-2404）：send WR 挂 `xrc_remote_srq_num = dev->rnode.srqn`，_prep 交换的 NODE.srqn 字段（enc_node rdma.c:2558）在此消费；
- ib_close1（rdma.c:2269-2272）：额外 ibv_close_xrc_domain；
- show_node_info（rdma.c:1564-1583）：XRC 分支多打 srqn。

## 三、外部连接

- **RDS 对内核**：需要 rds 内核模块（`rds`、`rds_rdma` 或 `rds_tcp`），否则 socket(AF_RDS) 直接 ENOENT/EAFNOSUPPORT。RDS over TCP 形态（rds_tcp）无需 IB 硬件即可跑 rds_bw——这是它在虚机环境仍可教学的原因。
- **RDS 对框架**：rds.c 不依赖 libibverbs（include 清单里没有 verbs.h，rds.c:37-47），Tests 表 rds_bw/rds_lat 在 `#ifdef RDMA` 块**外**注册（qperf.c:559-560），属 socket 阵营——qperf.h:280-294 却把它们的原型排在"Socket tests in socket.c"注释组里（漂移之一，实现在 rds.c）。
- **XRC 对构建系统**：configure.ac 第 5 行 `AC_CHECK_LIB(ibverbs, ibv_open_xrc_domain, HAS_XRC=1)` 探测符号；Makefile.am 在 RDMA 分支内再叠 `-DHAS_XRC=1`；qperf.c Tests 表 L591-595 的三个 test(xrc_*) 条目、help.txt 的 `Tests +RDMA` 节（L372）随之增删。注意探测的是**符号存在**而非硬件可用——链接期有符号、运行期无 XRC 硬件时，xrc 测试会在建 QP 阶段报错。
- **XRC 对 help/mkman**：mkman do_tests 硬取 "Tests +RDMA" 节（mkman L57），XRC 测试的 man 条目只在 HAS_XRC 构建的 help.txt 里存在。

## 四、数据流

RDS 建链期有**三条通道并存**的奇观（控制 TCP + IP 交换 TCP 副通道 + RDS 数据通道）：

```
qperf 主控制通道(RemoteFD:19765)     TCP 副通道(动态口)         RDS socket
server ──"TCP server port"───────────┐
       ←─accept 得 client IP────────┤ client_get_hosts:
       ──"client IP"字符串───────────┘   connect_tcp→取 server IP
server: rds_socket(bind) ──"RDS port"──→ client: rds_socket(bind)
       ←──────"RDS port"──────────────  rds_makeaddr(RAddr)
                    ↓ sync_test
client: while(!Finished) sendto(sockfd,buf,RAddr)   [rds.c:136]
server: while(!Finished) read(sockfd,buf)           [rds.c:168]
```

XRC 数据流与 RC 完全同构（复用 rd_client_bw/rd_server_def 等引擎），唯一分叉在建链：rd_open→ib_open（非 CM，rd_params 对 XRC 走 setv_u32(use_cm,0)）→rd_create_qp 开 XRC domain+SRQ→NODE 交换（srqn 入列）→ib_prep→数据面 post 挂对端 srqn。

## 五、设计决策

- **RDS 用 TCP 副通道探对端 IP**：无连接协议没有 accept 这类"天然知道对端"的时机，作者借一条最小 TCP 连接偷看对端地址（server_get_hosts 注释 rds.c:327-329），比让用户手填 IP 优雅得多；v4-mapped 折叠处理则兼容了 getaddrinfo 优先返 v6 的现实。
- **n != msg_size 而非 n < 0**（rds.c:140/171 等）：SEQPACKET 每读一次必是一整条消息，短读意味着协议栈异常，按错误记账——与 socket.c 字节流口径（n<0 才错）形成对照，传输语义决定判错语义。
- **XRC 探测粒度选在库符号级**：ibv_open_xrc_domain 在 libibverbs 里存在与否是编译期能确定的最强信号，硬件能力留给运行期 error 兜底。三层（RDMA→HAS_XRC→运行期）各管一段，条件编译只裁"API 都没有"的硬缺席。
- **XRC 代码全部复用 RC 引擎**：六入口是浅壳，差异压到 rd_create_qp/rd_post_send 两处的 #ifdef 卫兵——新增传输类型的最小改动面示范。代价是 rdma.c 里散布 9 处 HAS_XRC 卫兵（L1564/1578/1679/2107/2128/2211/2269/2401 及 Tests 表），阅读时需全文检索。
- **AF_RDS 读 /proc 而非 sysconf**：地址族号本该是 ABI 常量，但 RDS 模块化年代内核给的是运行期注册值——三级兜底（宏→/proc→21）是那个过渡期的兼容化石。

## 六、新人提示

- 跑 rds 测试前 `modprobe rds rds_tcp` 并确认 `/proc/sys/net/rds/` 存在；报 "AF_RDS not defined...Using 21" 说明走了兜底，若内核实际注册号不是 21 会莫名 bind 失败——此时先 `cat /proc/sys/net/rds/pf_rds` 核对。
- 想要 XRC 测试需在配 IB XRC 的老硬件（如 ConnectX-3 时代）上构建；新 libibverbs 已删 xrc 接口，configure 探测失败属预期，qperf 会静默裁掉三个 xrc 测试（Tests 表、help、man 同步缩水，`qperf --help tests` 看不到即未启用）。
- 改 rds.c 时别用 socket.c 的 recv_full/send_full：RDS 不保证部分读写语义，整包判错才是对的。
- qperf.h:283-286 的 rds 原型挂在"socket.c"注释组下、make 时 rds.c 又与 socket 线同链——按头文件注释分组找代码会走错门，认准文件名。
