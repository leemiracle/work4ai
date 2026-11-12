# 03 通信骨架：socket 测试线（socket.c）

## 一、角色定位

socket.c（821 行）实现四个基于 BSD socket 的测试族：TCP、UDP、SCTP、SDP，每族又分带宽（bw）与延迟（lat）两型，共 8 个用户可见测试（Tests 表 qperf.c:561-568）。它是三条传输线中最"老派"的一条，但恰恰是理解 qperf 测试范式的最佳入口：它完整展示了"控制通道传端口 → 数据通道压测 → 交换统计"三段式骨架，且用一套 `stream/datagram × bw/lat` 四象限引擎函数把 8 个入口收敛到 8 个 static 实现。RDS 线（rds.c）与 RDMA 线的数据面虽然完全不同，测试节奏仍复用这里定下的形状。

## 二、内部结构

**两乘四的矩阵收敛**。8 个 `run_client_*`/`run_server_*` 入口（如 run_client_tcp_bw socket.c:177-184）只做三件事：par_use 声明消费的参数、`ip_parameters(默认msg尺寸)` 填默认并 opt_check、然后转投对应引擎：

| | stream（面向连接） | datagram（数据报） |
|---|---|---|
| **带宽** | stream_client_bw:265 / stream_server_bw:297 | datagram_client_bw:414 / datagram_server_bw:446 |
| **延迟** | stream_client_lat:331 / stream_server_lat:373 | datagram_client_lat:479 / datagram_server_lat:521 |

四象限的差异在读写原语与统计口径：stream 用自写的 `send_full/recv_full`（socket.c:769-808，循环 write/read 直到整包完成，read 返回 0 视为 EOF 调 set_finished）；datagram 直接 write/read 一次一包，server 延迟版用 recvfrom/sendto 回射对端地址（socket.c:533-545）。带宽测试 show_results(BANDWIDTH)（TCP）或 BANDWIDTH_SR（UDP 无重传，收发分开算）；延迟测试收发同包计数，show_results(LATENCY)。

**KIND 枚举做协议轴**（socket.c:53-60）：`K_SCTP/K_SDP/K_TCP/K_UDP` 配 `Kinds[]` 名字表。协议差异被压进一个函数 `getaddrinfo_kind`（socket.c:692-724）：先以标准 getaddrinfo 拿地址列表，然后按需"篡改"——SDP 把 ai_family 从 AF_INET/AF_INET6 替换成私有的 `AF_INET_SDP 27`（socket.c:47，内核 socksdp 模块约定值）；SCTP 把 ai_protocol 从 IPPROTO_TCP 换成 IPPROTO_SCTP（socket.c:716-721），不支持的家族置 0 由调用方跳过。UDP 则在 hints 层就改 SOCK_DGRAM。这是"在标准 API 返回值上做最小变换来承载非标准协议"的典型手法。

**初始化三件套**。client 侧 `client_init`（socket.c:581-608）：先走 `client_send_request()` 发 REQ，再从控制通道收 server 通告的数据端口，getaddrinfo_kind 后逐地址 connect。server 侧 `stream_server_init`（socket.c:614-650）：bind 临时端口（Req.port 为 0 时系统分配）→ listen(1) → `get_socket_port`（socket.c:748-762，getsockname+getnameinfo 绕路取端口号，注释自嘲"必有更高效办法但没找到可移植的"）→ 把端口 encode_uint32 后经控制通道 `send_mesg` 发给 client → accept → `set_socket_buffer_size`（socket.c:730-741，按 Req.sock_buf_size 同设 SO_SNDBUF/SO_RCVBUF）。datagram 版（socket.c:656-685）无 listen/accept，bind 后直接通告端口。

**ip_parameters**（socket.c:565-575）是 socket 线的参数声明块：默认消息尺寸由各入口传入（TCP/SDP bw 64K、SCTP bw 32K、lat 全部 1 字节），par_use 认领 port 与 sock_buf_size。

## 三、外部连接

- **对 qperf.c**：消费框架的 sync_test/start 计时、exchange_results、show_results；LStat 统计累加；Finished/SIGALRM 机制终止循环。
- **对 support.c**：qmalloc 分配缓冲、send_mesg/recv_mesg/decode_uint32 收发端口、setsockopt_one 设 SO_REUSEADDR、touch_data 在 access_recv 开启时消费接收数据（socket.c:317-318，防止网卡零拷贝直达后 CPU 从不碰页的"假带宽"）。
- **对内核/协议栈**：SCTP 依赖内核 IPPROTO_SCTP；SDP 依赖加载的 sdp 模块（AF_INET_SDP 套接字）；两者在现代内核上多已不可用，但代码路径完整保留，是 OFED 时代协议考古的活标本。
- **对 Tests 表**：qperf.c:561-568 的 8 个 `test()` 宏条目无条件注册（socket 线不参与 RDMA 条件编译），保证最小构建（无 libibverbs）也有完整 IP 测试能力。

## 四、数据流

以 `qperf server tcp_bw` 为例（client 侧 stream_client_bw socket.c:265-291）：

1. client_init：REQ 已发，收到 rport（如 19766），connect 成功。
2. `sync_test()`：控制通道互发同步串，双方 start_test_timer。
3. 主循环（socket.c:274-285）：`send_full(sockFD, buf, Req.msg_size)` 整包发送；n<0 记 no_errs 继续（EINTR 由 Finished 检查吸收）；否则 no_bytes/no_msgs 自增。循环直到 SIGALRM 置 Finished。
4. `stop_test_timer` → `exchange_results`（server 先发 STAT，client 收后回 sync）→ show_results(BANDWIDTH)。
5. server 侧 stream_server_bw（socket.c:297-325）对称：recv_full 收包计数，access_recv 开启时每包 touch_data。

延迟版是乒乓：client 发一等收一（socket.c:341-360），server 收一等发一（socket.c:383-402），RTT 的一半由 calc_results 的 `Res.latency = time_real / no_msgs`（qperf.c:1891-1893）给出。注意所有循环里每个 I/O 前后都查 Finished——计时器响起后收到的包不再计数，这是 stop_test_timer 注释（qperf.c:1826-1835）明说的防作弊设计。

## 五、设计决策

- **端口协商走控制通道而非固定端口**：数据通道端口由 server bind(0) 动态分配再回传（socket.c:640-642），同机多实例互不干扰，防火墙也只需放行 19765。三条传输线全沿用此约定。
- **server 端不开 show_results**：只有 client 打印（stream_server_bw 结尾无 show 调用），双端输出解耦——server 是 fork 出的短命子进程，统计经 exchange_results 集中到 client 算。
- **错误分类统计而非中止**：n<0 只 no_errs++ 继续（socket.c:279-282），测试在时间窗内照常跑完。性能测试要的是吞吐画像不是 fail-fast，UDP 丢包、SCTP 重传都体现在 errors 列而非退出码。
- **SDP/SCTP 复用 TCP 形状的引擎**：getaddrinfo_kind 在地址结构上做手脚后，stream_* 引擎完全无感——协议异质性被压缩到初始化层，数据面零分支。代价是 K_SDP 的 connect 失败信息只能笼统报"could not make SDP connection"（socket.c:602）。
- **UDP 带宽用 BANDWIDTH_SR 而非 BANDWIDTH**（socket.c:439）：无连接协议收发不对称（丢包），合并 bw 会失真，框架为此专门设了 send/recv 分列的 MEASURE 档位。

## 六、新人提示

- 调 sock_buf_size 时注意它同时设收发两向（socket.c:737-740），且只在 server 侧数据 socket 上设置（client 侧没设）；要单边控制需自行改 client_init。
- stream 与 datagram 的"整包"语义不同：send_full 是字节流凑齐，datagram 一次系统调用即完整消息；msg_size 超过 UDP MTU 时 write 仍会成功（本地缓冲），丢包发生在网络段——别拿 no_errs 判断 UDP 分片问题。
- AF_INET_SDP=27 是硬编码（socket.c:47），与 rds.c 的 AF_RDS=21 兜底（rds.c:58）同属"内核模块自定义地址族"时代的遗迹；在新内核上跑 sdp/sctp 测试前先确认模块存在。
- server 端 `listen(listenFD, 1)`（socket.c:637） backlog 故意为 1：单 client 单连接，勿改成大值——这行代码假设了整个工具的使用模型。
