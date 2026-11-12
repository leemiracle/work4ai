# explain-02 · tap.c：三种后端之上的统一 L2 收发层

## 1. 角色定位

`tap.c`（1627 行）是"客户侧接口"的总抽象层：把 qemu UNIX socket（MODE_PASST）、/dev/net/tun（MODE_PASTA）、vhost-user（MODE_VU）三种完全不同的后端，统一成一组 `tap_send_*` / `tap_handler_*` 接口，供全部协议模块调用。它是整个代码库的汇合点——上行方向把 L2 帧剥头、校验、按五元组归并后分发给 tcp/udp/icmp/arp/dhcp/ndp 处理器；下行方向用 `tap_push_*` 系列从内向外逐层构造 L2/L3/L4 头。可以说：`passt.c` 是骨架，`tap.c` 是所有血液流过的心脏。

模式差异被压到极少数分支点：`tap_l2_max_len()`（`tap.c:107-122`）按模式返回帧长上限；`tap_send_single()`（`tap.c:130-161`）passt 模式帧前要加 4 字节 vnet 长度前缀（qemu stream netdev 的线上格式），pasta 直接裸帧，vu 转交 `vu_send_single()`。

## 2. 内部结构

**下行（构造帧）一族**：`tap_push_l2h()`（`tap.c:172`）写 ethhdr，目的 MAC 恒取 `c->guest_mac`（`tap.c:178`，附 TODO：tap 侧 ARP 查表）；`tap_push_ip4h()`（`tap.c:194`）/`tap_push_ip6h()`（`tap.c:301`）填 IP 头并顺手算校验和；`tap_push_uh4/uh6()`（`tap.c:225/329`）UDP 头带伪头部校验。组合件 `tap_udp4_send()`（`tap.c:253`）、`tap_udp6_send()`（`tap.c:359`）、`tap_icmp4_send()`（`tap.c:276`）、`tap_icmp6_send()`（`tap.c:384`）都是同一个模式：栈上 `char buf[USHRT_MAX]`，从 `buf` 开始逐层 push 头再 `tap_send_single()`。这是给协议应答器（DHCP/NDP/ICMP）用的低频路径；高频路径由 tcp.c/udp.c 自己批量组帧。

**下行（批量发送）**：`tap_send_frames()`（`tap.c:510`）按模式分派——pasta 走 `tap_send_frames_pasta()`（`tap.c:413`）逐帧 `writev`，EAGAIN/ENOBUFS 等错误容忍（`tap.c:427-439`，接口抖动不致命）；passt 走 `tap_send_frames_passt()`（`tap.c:463`）一次 `sendmsg` 打包全部 iovec（qemu 侧流式 socket 支持拼接帧流），短发送时用 `write_remainder()` 补尾（`tap.c:487`）。发完统一过 `pcap_multiple()`（`tap.c:538`）落抓包文件。`MODE_VU` 在此 assert(0)（`tap.c:531`）——vu 模式的批量发送有自己的 `vu_send_frames()`，不走这条路径。

**上行（收包入池）**：两个静态报文池 `pool_tap4`/`pool_tap6`（`tap.c:98-99`），池容量按"空 UDP 报文"估算能吞下整个 `pkt_buf`（`tap.c:78-95` 注释：只是调优参数，超了也能跑）。`tap_add_packet()`（`tap.c:1157`）是三种后端共同的入池口：先 `pcap_iov` 记录，再偷看 ethhdr 源 MAC——与 `c->guest_mac` 不同则更新并回调 `proto_update_l2_buf()` 刷新 TCP/UDP 的帧模板（`tap.c:1170-1178`），passt 模式下 MAC 就是这样"学"来的；然后按 ethertype 分池。

**上行（协议分发）**：`tap4_handler()`（`tap.c:692`）是 IPv4 侧主循环。逐包校验：剥 ethhdr，ARP 交给 `arp()`（`tap.c:720-723`）；IP 头长度/总长检查（`tap.c:733-736`）；分片直接丢并限速告警（`tap4_is_fragment()`，`tap.c:670-682`——passt 不重组 IP 分片）；环回地址丢弃（`tap.c:744`）；源地址学习进 `c->ip4.addr_seen`（`tap.c:759-761`）；尾部 padding 裁剪（`tap.c:770-776` 注释：Plan 9 virtio 驱动会把短帧补到 60 字节最小以太网长度）；ICMP 单包直发 `icmp_tap_handler()`（`tap.c:784`），UDP 先给 `dhcp()` 尝试截获（`tap.c:795-799`）。剩下的 TCP/UDP 包用 `L4_MATCH`/`L4_SET` 宏（`tap.c:808-822`）按"协议+端口+地址+TTL"归并进 `tap4_l4[TAP_SEQS]` 序列槽（`tap.c:572-583`），凑满 `TAP_SEQS=128` 个流或扫完输入后，flush 给 `tcp_tap_handler()`/`udp_tap_handler()`（`tap.c:851-872`）——**一次批处理多个包进一次协议调用**，这是 passt 吞吐的关键设计。`tap6_handler()`（`tap.c:940`）是 IPv6 镜像版本，多一步 `ipv6_l4hdr()`（`tap.c:894`）逐个跳过扩展头（`IPV6_NH_OPT` 宏 `tap.c:880-883` 列出 hopopts/routing/fragment/ah 等 11 种 nexthdr），并做 link-local/地址学习（`tap.c:1000-1013`）；ICMPv6 先给 `ndp()`（`tap.c:1025`）、UDP 先给 `dhcpv6()`（`tap.c:1044`）。

**后端建立**：`tap_backend_init()`（`tap.c:1593`）按模式建接口——vu 走 `vu_init()` 并把报文池 base 指到 vhost-user 的 mmap 内存（`tap.c:1597`，**报文池零拷贝的伏笔**）；passt/pasta 用 `pkt_buf`。pasta 的 `tap_sock_tun_init()`（`tap.c:1556`）通过 `NS_CALL(tap_ns_tun, c)` 进目标命名空间 open /dev/net/tun、TUNSETIFF（`tap_ns_tun()`，`tap.c:1525-1550`）。passt 模式 `tap_sock_unix_init()`（`tap.c:1393`）监听 UNIX socket；`tap_listen_handler()`（`tap.c:1465`）accept 时用 SO_PEERCRED 报 qemu PID、已有连接则拒绝并 discard（`tap.c:1477-1490`，passt 设计上只服务一个客户端），还把 SO_RCVBUF/SO_SNDBUF 顶到 INT_MAX/2（`tap.c:1506-1512`）。注意 accept 出的 socket 故意用**阻塞模式**——注释 `tap.c:1492-1496` 解释：平时全靠 epoll 事件无阻塞问题，仅 socket 缓冲满时 `write_remainder()` 需要（短暂的）阻塞写兜底。`passt.c` 侧 guest MAC 未知前先填广播地址（`tap.c:1618-1622`）。

**收包入口三胞胎**：`tap_passt_input()`（`tap.c:1225`）解析 4 字节长度前缀流，处理跨 recv 的半帧（static `partial_frame`/`partial_len`，`tap.c:1227-1228,1234-1240`）；`tap_pasta_input()`（`tap.c:1311`）循环 read 到 EAGAIN，EOF 直接 die（tap 设备没了意味着目标 ns 死了）；vu 的收包在 vu_kick_cb 里。

## 3. 外部连接

被依赖：所有协议文件 include `tap.h`；`tcp_buf.c`/`udp.c` 的帧模板要 `tap_l2_max_len()` 定尺寸。依赖：`packet.h`（报文池抽象）、`iov.h`（iov_tail 零拷贝视图）、`checksum.c`（L3/L4 校验和）、`pcap.c`（调试抓包双向都过它）、`netlink.c`/`pasta.c`（ns 进入与配置）、`vhost_user.h`（vu 模式）、`repair.h`（vu 模式 init 时起 repair socket，`tap.c:1613`）。头文件 `tap.h` 定义 `L2_MAX_LEN_PASST/PASTA/VU` 三档帧长上限，`tap.c:70-76` 的 `CHECK_FRAME_LEN` 静态断言三档都夹在 [ETH_HLEN, PACKET_MAX_LEN] 区间。

## 4. 数据流

以 guest DHCP discover 为例：qemu socket → `tap_handler_passt` → `tap_passt_input` 解帧 → `tap_add_packet` 入 pool_tap4（顺带学 MAC）→ `tap_handler` → `tap4_handler`：剥 ethhdr，发现 UDP 且 dst 67 → `dhcp()`（`tap.c:798`）命中、消费此包、构造 offer/ack（dhcp.c 内组帧）→ `tap_udp4_send()` → `tap_push_l2h/ip4h/uh4` 三层 push → `tap_send_single()` → sendmsg 回 qemu。整个旅程只有两次内存拷贝（payload memcpy 进 buf、socket 发送）。

## 5. 设计决策

三个决策值得抄走。其一，**分片直接丢**（`tap.c:738-739`）——guest TCP MSS 由 passt 亲自协商（tcp.c），UDP 又极少分片，正确路径上不该出现分片，出现即异常，省掉整个重组器。其二，**批处理归并**：TAP_SEQS 槽把一批帧按流聚齐再调协议 handler，让 tcp/udp 一次调用处理同流多包（时间戳、定时器、窗口判断都能批量摊销）。其三，**MAC 学习而非配置**：passt 模式 MAC 未知就先广播，收到第一帧即更新模板（`tap.c:1170-1178`），运行期 guest 换 MAC 也能跟上——比让用户传 MAC 参数省心且鲁棒。

## 6. 新人提示

读代码先看 `tap.h` 的宏与三档 L2_MAX_LEN，再看 `tap_backend_init()` 理解三条分支。改收包路径时记住：`tap4_handler`/`tap6_handler` 里的 `goto resume`（`tap.c:702,874-875`）是为 TAP_SEQS 溢出时先 flush 再继续扫设计的，别"简化"掉。`tap_send_frames` 返回值是"已记账帧数"（`tap.c:534-541`），失败帧只 debug 不重发——TCP 靠重传兜底、UDP 丢了就丢了，别在这里加重试。调试利器是 `--pcap`：所有收发都过 pcap 钩子，配合 `tap_packet_debug()`（`tap.c:621`）的 trace 日志能完整还原每批包的去向。
