# passt / pasta — 无特权的用户态 L2→L4 网络转换层

- 本地仓：`/usr-data/data2/kylin/network/passt`（只读消化，勿改）
- 当前 commit：**2026-10-25 `6aa4f88`** "passt-repair: Suppress false positive cppcheck negativeIndex warning"（浅克隆，最近 tag 为 2026_10_02.cba3570）
- 上游：https://passt.top/passt（git.pub.scmoke / bugs.passt.top），GPL-2.0-or-later
- 作者：Stefano Brivio <sbrivio@redhat.com>（Red Hat），核心贡献者 David Gibson（flow table/isolation）、Laurent Vivier（vhost-user 线）
- 规模：约 32,500 行 C（含 .h），零外部依赖（仅 libc）；tcp.c 单文件 4,121 行是"理论文档+实现"合体

**总评**：passt 是"网络协议翻译器"流派的教科书实现——它不实现一个 TCP/IP 栈，而是做一个**会说网络协议的普通进程**：把 guest/netns 侧的 L2 帧翻译成宿主机内核的原生 L4 socket，再用 TCP_INFO 镜像把两端的 TCP 动力学（窗口/ACK/MSS）互相"复读"，从而在**不持有任何 capability、不建任何 host 接口**的前提下，让 guest 里的进程看起来就像跑在宿主机本地。这个设计砍掉了 slirp 系方案的第三层 TCP/IP 栈，换来 4-50 倍吞吐提升；2025-2026 年新增的 vhost-user 数据面（单次拷贝）、TCP_REPAIR 连接迁移和 pesto 运行时改配，使它从"QEMU/Podman 的联网配件"进化为 rootless 容器/VM 网络的事实标准后端之一。

## 1. 设计哲学与动机

**名字即纲领**：passt = "Plug A Simple Socket Transport"，pasta = "Pack A Subtle Tap Abstraction"。同一二进制，按 argv 决定模式（MODE_PASST / MODE_PASTA / MODE_VU）。

**要解决的问题**（README "Motivation"）：容器负载搬进 VM 后，service mesh 等生态期待应用"本地运行"——socket 可见、进程可见，才能做 socket 重定向、监控、端口映射。传统解法是 libslirp 式 user-mode networking，但代价惨重：

1. 每个请求要穿越**三个 TCP/IP 栈**（guest、适配层、host）；
2. 地址要协调（NAT masquerade 或桥接）才能伪装出一致的地址/路由视图；
3. service mesh 看到的流量是"远端复制品"——拥塞窗口与网络缓冲机制失真，携带地址信息的协议（FTP/SIP 类）出现语义漂移。

passt 的回应是**只实现"假装进程在本地"所严格需要的部分**：不做通用栈，不缓存整条连接的报文，而是把观察到的发送窗口与 ACK 在两侧之间反射（reflect）。之所以需要这层 TCP 适配，是因为 passt 运行时没有 `CAP_NET_RAW`，开不了 raw IP socket，只能把 L2 包映射到 host 内核提供的 L4 socket——这个约束反过来塑造了整个架构。

**pasta 的动机**：普通用户可以创建 network namespace，但把 netns 连通到外部需要 veth 对，而建 veth 要 `CAP_NET_ADMIN`。pasta（类 slirp4netns）在**namespace 内部**创建 tap 设备，进程在 namespace 里对着 tap 说话，对外仍用宿主侧原生 L4 socket——host 上不新增任何接口。相比 slirp4netns：不做通用 TCP/IP 栈、本地连接有直通快路径、默认地址/路由直接映射进 ns **无需 NAT**。

贯穿全仓的工程红线：**无动态内存分配**（sbrk/brk/mmap 被 seccomp 封禁，全部静态缓冲）、单线程 epoll 事件循环、限制性 seccomp（x86_64 上 passt 34 条/pasta 43 条系统调用白名单，由 `seccomp.sh` 从源码里的 `#syscalls:PROFILE` 注释自动生成，还带 arm:/ppc64: 等按架构变体）、分级自我隔离（isolation.c：先丢 capability、关泄漏 fd、再切 UID/GID 与 user namespace，最后 chroot/pivot_root + 新 user/mount/IPC/UTS/PID namespace）。README 早期目标 "~5000 LoC" 早已被 vhost-user/迁移线撑破，但"每个 .c 头部几十行设计注释"的传统保留至今——tcp.c 头部 300 行 "Theory of Operation" 是全仓最好的架构文档。

## 2. 架构剖析：tap 抽象 → L2/L3 应答 → L4 转发

### 2.1 三种 tap 后端（tap.h / tap.c）

`struct ctx.mode` 决定 guest 侧接口形态，统一的 `tap_send_frames()` 批量出口把差异收敛在 `struct tap_hdr`（passt 模式是 4 字节帧长前缀，即 qemu socket backend 的 vnet_len 帧；pasta 是内核 /dev/net/tun（帧长上限 65521）；MODE_VU 则完全绕开帧封装、直接操作 virtqueue 描述符）。入方向 `tap_handler()` 做以太网解复用：ARP 交 arp.c，IPv4/IPv6 剥 L2 后按 protocol 分发 `tcp/udp/icmp_tap_handler()`——**没有路由表、没有转发表**，L3 只做最小合法性检查。帧大小上限由 `CHECK_FRAME_LEN` static_assert 统一钉在 PACKET_MAX_LEN（64K）内。pasta 模式下 tap fd 在 namespace 里创建，epoll 仍由宿主侧主循环统一驱动。

### 2.2 L2/L3 控制面：替 guest 回答"我是谁、网关在哪"

passt 对外的关键伪装术是用**微型协议服务器**替代内核栈的地址配置：

- **arp.c（ARP proxy）**：应答 guest 对网关（即宿主上游接口地址）的 ARP 请求，MAC 用宿主原网卡 MAC（`our_tap_mac`/`guest_mac` 从 DHCP 或首包学习）。
- **dhcp.c（单地址 DHCP server）**：只发一个 IPv4 地址——**就是宿主上游接口的首地址**，网关/DNS/搜索域照抄宿主，MTU 可配。guest 与宿主"同地址不同 MAC"，因此默认无需 NAT；guest 若用了别的地址，出向包做地址翻译兜底。无 DHCP 时 IPv4 link-local 兜底 169.254.2.1（conf.c）。
- **ndp.c（NDP proxy + RA/SLAAC）**：处理 RS/NS/NA（类型 133-136），RA 携带从宿主上游地址派生的前缀（SLAAC 让 guest 自配地址）、MTU、RDNSS/DNSSL 选项。
- **dhcpv6.c（单地址 DHCPv6 server）**：可选，发宿主同款 IPv6 地址，使地址完全免翻译。
- **igmp.c / mld.c**：目前只是占位（IGMP/MLD proxy 仍在做，bug #2）。

netlink.c 负责"抄作业"：用 rtnetlink 读宿主接口/地址/路由（pasta 默认原样映射进 ns），`--config-net` 时再反向用 netlink 配置 ns 内接口。

### 2.3 流表（flow.c / flow.h / flow_table.h）与事件循环

所有逻辑"流"（TCP 连接、spliced TCP、UDP 伪流、ping 序列）住进静态 `union flow flowtab[]`：`FLOW_INDEX_BITS=17` → 上限 **128k-1 条**，空闲槽组织成 cluster 链表做 O(1) 分配。生命周期状态机 FREE→NEW→INI→TGT→TYPED→ACTIVE；类型表 FLOW_TCP/FLOW_TCP_SPLICE/FLOW_PING4/PING6/FLOW_UDP 各自挂 epoll_type。地址统一存 `union inany_addr`（IPv4 以 v4-mapped IPv6 形式内嵌），一套哈希（siphash，128 位 hash_secret）同时服务 v4/v6 查表。主循环 passt.c：单线程 epoll（NUM_EPOLL_EVENTS=8），共用 timerfd 的间隔取 `min(TCP_TIMER_INTERVAL, FWD_PORT_SCAN_INTERVAL, FLOW_TIMER_INTERVAL)`；收发包走静态 `pkt_buf`（页对齐）+ `struct pool` 边界检查包池——README 所称 "clearly defined boundary-checked packet abstraction"，所有取包都过 `packet_get_do()` 的范围断言，这是它对"用户态栈容易越界"的自我防御。

### 2.4 TCP（tcp.c，4121 行）：镜像，而非重实现

tcp.c 头部 Theory of Operation 的核心思想：**不做分段/排队/重组**，把 TCP 行为尽量委托给 guest 与 host 两个内核栈，自己在中间当"动力学复读机"：

- **事件代替状态机**：连接用位标志事件集（SOCK_ACCEPTED / TAP_SYN_RCVD / ESTABLISHED / 各 FIN 事件）而非传统状态机，动作都是对事件的反应；`tcp_state_str[]` 仅用于把事件近似映射成 RFC 状态名打日志。
- **窗口镜像**：socket 侧用 `TCP_INFO` 读取内核观察到的窗口/ACK 字节数（`tcpi_bytes_acked` 换算 seq_ack），tap 侧解析报头窗口，双侧互推。**window scaling 上限被砍到 2^8=256 倍（MAX_WINDOW=16 MiB）**——因为未确认数据要用 MSG_PEEK 留在 socket 里、丢弃缓冲静态分配（tcp_buf_discard 16 MiB + MSS 级 buf），更大窗口就要动态内存，违背红线。
- **四条数据流原语**：`seq_to_tap / seq_ack_from_tap / seq_from_tap / seq_ack_to_tap`，socket→tap 方向按 MSS 分段、受 `wnd_from_tap` 节流；两个重复 ACK 触发从 `seq_ack_from_tap` 重发（快速重传语义）。
- **超时**：RTO 走 RFC 6298（初始 1s），并读宿主 `/proc/sys/net/ipv4/tcp_syn_retries`、`tcp_syn_linear_timeouts`、`tcp_rto_max_ms` 对齐内核行为；RTT 逼近值以 100us 粒度存储（RTT/2 触发补 ACK）；KEEPALIVE_INTERVAL=30s 向 tap 发保活探测对端是否还认这条连接；INACTIVITY_INTERVAL=7200s 清死连接。
- **安全**：ISN 用 siphash 随机化（RFC 6528）；本地低 RTT 目的地址有 LRU 表用于识别 host 本地流量。**明确不做**：SACK、PAWS/timestamps（bug #1）、IPv4/IPv6 分片。
- **端口策略**：passt 模式默认把宿主所有未占用非临时端口（0-49152）全 bind 成监听 socket（低端口无 CAP_NET_BIND_SERVICE 会失败、被 proxy 占的跳过）——所以**要求 passt 晚于 mesh sidecar 启动**。入站连接复用源端口反向发起，唯一不可避免的是 guest 主动出站时 host 内核选的源端口。

### 2.5 UDP（udp.c）与 ICMP（icmp.c）

UDP 无真连接，但按"客户端临时端口→服务器知名端口"的会话模式建 **FLOW_UDP 伪流**：单向流 UDP_TIMEOUT、双向流 UDP_TIMEOUT_STREAM 秒过期。"listening" socket（可接受新流的长期 socket）与 connect() 过的 "flow" socket 并存——connect 保证内核只把该五元组的报文投给 flow socket，epoll 引用直指 flow 免哈希；这里有个微妙的内核行为假设（connect 过的 socket 优先于仅 bind 的收到匹配报文），passt 甚至写了 `doc/platform-requirements/reuseaddr-priority.c` 来钉死这条平台契约——同目录还有 listen-vs-repair、recv-zero、tcp-close-rst、udp-close-dup 等内核行为探针程序，是这个仓"依赖内核语义就写成可编译证据"的独特工程文化。

ICMP 只代理 echo：ICMPv4 用 ping socket（dgram ICMP，不需要 CAP_NET_RAW），按 identifier 建 FLOW_PING4/6 流，60s 超时。

### 2.6 pasta 的本地直通：tcp_splice.c 与 UDP splice

pasta 杀手锏：ns 内进程若连的是**映射端口上的本地目的**（两 namespace 间的 loopback 流量），完全跳过 L2 翻译——TCP 用**一对 pipe + splice(2)** 在两个 L4 socket 间零拷贝搬运（事件集 SPLICE_CONNECT/ESTABLISHED/OUT_WAIT/FIN 系列；pipe 池 32 条、单 pipe 可扩 8 MiB；为省 fd 与连接数压力有 CONN_PRESSURE/FILE_PRESSURE 30% 阈值降级）；UDP 用 recvmmsg/sendmmsg 对。ns 侧 socket 由**socket 池**（ns_sock_pool4/6）预热：主进程 `ns_enter()`（setns）进去预先开好 socket，避免每次连接付 setns 代价。外出非本地流量退回标准 L2 翻译路径。

### 2.7 vhost-user 数据面（MODE_VU：vhost_user.c / virtio.c / vu_common.c / tcp_vu.c / udp_vu.c）

`--vhost-user` 让 passt 直接充当 **vhost-user 后端**（virtio_net 设备），QEMU 侧 `-chardev socket` 接 passt 的 `--socket` 路径。virtqueue 代码移植自 QEMU libvhost-user（GPL/BSD 双许可痕迹保留在文件头）。收益：数据面**最多一次拷贝**——tcp_vu/udp_vu 直接把帧构造进 guest 内存中的 descriptor 链（iov_vu[VIRTQUEUE_MAX_SIZE]），`vu_packet_check_range()` 校验每个 iovec 落在已映射的 guest 内存区域。README 明言该路径同时降请求-响应时延。代价是复杂度：设备状态迁移、内存表重映射都要伺候。

### 2.8 迁移（migrate.c / repair.c / passt-repair.c）与 pesto

2025 年新增的**连接迁移**线：把整张 flow table + socket 状态序列化搬到新 passt 实例，配合 VM/容器在线迁移。关键难点是 TCP socket 的序列号/窗口状态必须原样搬——用 `TCP_REPAIR` socket option 冻结连接，但开它要 `CAP_NET_ADMIN`，而 passt 自己没有：于是拆出**特权小帮手 passt-repair**（seccomp 白名单极窄），通过 UNIX socket + SCM_RIGHTS 接收 fd 并代为切换 repair 模式，主进程保持无特权。迁移缓冲 tcp_migrate_snd/rcv_queue 各 64 MiB 静态区（注释自嘲："we're going away after this, so splurge"）。vhost-user 设备状态走独立 device_state_fd 通道（migrate.h）。配套 doc/migration/{source,target}.c 是可独立跑的最小演示。

**pesto**（2026，"Programmable Extensible Socket Translation Orchestrator — it's not actually extensible"，官方自嘲）：连上 passt/pasta 的 control socket（`-c` 路径），运行时**查看/增删端口转发规则**（-A/-D/-C/-s），不用重启守护进程——补上了"passt 起来之后改配置要重启"这个老短板；fwd_rule.c 定义规则语法与临时端口范围探测（读 ip_local_port_range）。

### 2.9 生态接口

qemu 原生 socket backend（qemu 7.2+）、libvirt `<interface type='passt'>`、Podman 4.3.2+ `--net=pasta`（rootless 默认）、rootless Docker 经 rootlesskit、`slirp4netns.sh` 是**bug-to-bug 兼容**的替换包装脚本，Kata Containers 有 out-of-tree patch。测试矩阵 test/ 含 passt_vu / two_guests / pasta_podman / perf（passt_tcp/udp、passt_vu_tcp/udp、pasta_tcp/udp 六条基线）/ rampstream（内存压测）/ nstool。

## 3. 关键文件表

| 文件 | 一句话职责 |
|---|---|
| passt.c | 守护进程主体：epoll 主循环、信号、静态 pkt_buf 与全局 ctx |
| passt.h | `struct ctx` 执行上下文：模式、地址/路由模板、fd、开关全集 |
| tap.c / tap.h | guest 侧接口抽象：三种后端统一收发、L2 头构造、L3 分发入口 |
| tcp.c | TCP L2↔L4 翻译状态机（头部 300 行 Theory of Operation 必读） |
| tcp_conn.h / tcp_internal.h | 连接结构体、窗口常量（MAX_WS=8、MAX_WINDOW=16MiB） |
| tcp_buf.c | 静态发送缓冲管理（MSG_PEEK 丢弃缓冲 + MSS 缓冲池） |
| tcp_splice.c | pasta 本地连接零拷贝直通（pipe + splice(2) + ns socket 池） |
| tcp_vu.c / udp_vu.c | vhost-user 数据面：帧直接构造进 virtqueue descriptor |
| udp.c / udp_flow.c | UDP 伪流：listening/flow 双 socket 模型、超时、pasta mmsg 直通 |
| icmp.c | ICMP/ICMPv6 echo 代理（ping socket，identifier 流） |
| flow.c / flow.h / flow_table.h | 静态流表（128k-1 上限、free cluster、类型分发） |
| arp.c / ndp.c / dhcp.c / dhcpv6.c | 四个微型控制面服务器（ARP/NDP+RA/DHCP/DHCPv6） |
| igmp.c / mld.c | IGMP/MLD 占位（proxy 开发中） |
| conf.c | 命令行/环境/netlink 配置汇总（2,237 行，第二大文件） |
| fwd.c / fwd_rule.c | 端口转发表、邻居表（1024 槽 ARP/NDP cache）、规则解析 |
| netlink.c | rtnetlink 读写：接口/地址/路由的抄写与配置 |
| pasta.c | namespace 特有逻辑：clone 起 ns、inotify 监控 netns 存活、退出联动 |
| vhost_user.c / virtio.c / vu_common.c | vhost-user 协议机 + vring 操作 + guest 内存边界校验 |
| migrate.c / repair.c / passt-repair.c | 连接迁移序列化 + TCP_REPAIR 特权帮手（SCM_RIGHTS 传 fd） |
| pesto.c / pesto.1 | 运行时改配客户端（control socket 上增删转发规则） |
| isolation.c | 分级自我隔离（caps→fds→uid→namespaces→chroot） |
| seccomp.sh | 从 `#syscalls:` 源码注释生成 per-arch seccomp profile |
| checksum.c / arch.c | 校验和（AVX2 运行时选版） |
| pcap.c / log.c | 调试双件：pcap 抓包落盘 + 分级日志 |
| util.c / iov.c / inany.c / packet.c | 基础设施：socket 帮手、iovec 裁剪、v4-mapped 地址、边界检查包池 |
| doc/platform-requirements/ | 内核行为契约的 C 探针程序（reuseaddr 优先级等五件） |
| test/ | CI 全家桶：distro 矩阵、perf 基线、rampstream、迁移、valgrind |

## 4. 对比定位：libslirp / 内核栈 / f-stack

**vs libslirp（及 slirp4netns/QEMU user-mode networking）**：libslirp 是完整用户态 TCP/IP 栈——自己握三次握手、自己管拥塞窗口与重传，于是 guest 栈、slirp 栈、host 栈三栈串联，单连接吞吐被 slirp 自身栈的保守窗口钳死，且地址必然要 NAT 伪装（10.0.2.x）。passt 把中间栈**削成一个翻译层**：拥塞控制、RTT 估计、重传全部委托给两端内核，自己只镜像窗口与 ACK，host 侧连接就是普通 socket——service mesh 的 socket 重定向/监控因此直接可用。官方口径：IPv4 TCP 吞吐是同类方案的 4-50 倍（随 MTU 变化）。slirp4netns.sh 脚本把 pasta 包装成 slirp4netns 命令行兼容层（连 bug 都兼容），供 Podman 无缝切换。

**vs 内核 veth/bridge + NAT 路线**：内核路线性能最好，但 rootless 场景下建 veth/bridge 要 CAP_NET_ADMIN，正是 passt/pasta 存在的理由。它不是内核栈的竞争者，而是"**没有权限时唯一能拿到接近原生体验**"的那一层。

**vs f-stack / mTCP 等 kernel-bypass 用户态栈**：目标相反。f-stack 接管网卡做高性能收发包（DPDK），需要大页、CPU 绑核、专属 NIC；passt 不碰网卡，只做 host 内核 L4 socket 与 L2 帧之间的翻译，单线程即可，追求的是**低权限下的透明性**而非 pps 极限。把它当"应用层侧的协议适配器"而非"数据面加速器"更准确（vhost-user 模式是唯一显著压时延的数据面优化）。

**vs QEMU virtio-net + tap**：传统 `-netdev tap` 需要打开 /dev/net-tun 并在 host 建接口（特权/配置）；passt 模式用 qemu 的 socket backend 走 UNIX socket，host 零新增接口。vhost-user 模式则反过来吸收了 virtio 生态：既保留无特权，又拿到接近 virtio-net 的单拷贝路径。

## 5. 性能特征与适用场景

- **拷贝次数账**（README 口径）：常规路径每数据包最多两次 cache-hot 拷贝；pasta 本地连接按设计零拷贝（splice）；vhost-user 最多一次拷贝。
- **吞吐 vs 时延的取舍**：单线程事件循环 + 静态缓冲意味着单流吞吐好（4-50x slirp 系），但**请求-响应时延**受 L4 socket 翻译路径拖累——vhost-user 模式专门补这一刀（README：lower request-response latency）。多线程仍在 roadmap（bug #13）。
- **吞吐不敏感、时延敏感的场景**（数据库短查询、RPC 风暴）优先 vhost-user；长肥管道受 16 MiB 窗口上限约束（scaling≤256）——万兆以上单流大 RTT 会遇到天花板，这是静态内存红线的直接代价。
- **适用**：rootless 容器（Podman/Docker rootless 默认后端）、Kata/Kubevirt 类 VM 的 service mesh 兼容联网、CI/沙箱里无特权网络、桌面虚拟化（GNOME Boxes 后端）。**不适用**：需要组播/IGMP 重场景、SCTP、巨型帧 jumbograms、IPv4 分片依赖的老协议、单机 pps 极限型负载。

## 6. 局限与坑

1. **IPv4/IPv6 分片不支持**（jumbograms 也不支持）：MTU 必须让路径不产生分片，大 UDP 包会被静默丢弃。
2. **TCP 语义缺口**：无 SACK（丢包恢复退化为重复 ACK 重传）、无 PAWS/timestamps（bug #1 开着）、window scaling 硬顶 256 倍/16 MiB——长肥管道吞吐受限。
3. **连接数硬上限 128k-1**（FLOW_TABLE_PRESSURE 30% 即开始施压回收），静态内存模型决定了不能弹。
4. **passt 端口全 bind 的启动顺序坑**：默认绑所有未占用端口，**必须晚于** mesh sidecar/服务 proxy 启动，否则抢了别人的端口（或被别人抢）。
5. **pasta 依赖 user namespace** 才能 unprivileged 建 tap；systemd `.socket` 单元或 nosuid 挂载环境可能踩雷。pasta 默认复制宿主地址路由，宿主接口变化（DHCP 续租换地址）不会自动跟进。
6. **单线程**：所有流量过一个核；flow 表扫描类的定时任务与数据面抢同一个循环（多线程 bug #13 未落地）。
7. **迁移线新且复杂**：TCP_REPAIR 帮手需要单独给 passt-repair 授 CAP_NET_ADMIN（架构上已最小化，但部署上多一件事）；迁移缓冲 128 MiB 静态占用常驻。
8. **行为契约绑定内核版本**：TCP_INFO 字段、SO_BINDTODEVICE unprivileged 可用性（no_bindtodevice 探测）、connect socket 优先级等都有版本差异——doc/platform-requirements 的探针就是为此存在，换内核发行版要跑 CI 矩阵。
9. **UDP 非会话型协议不友好**：双向不对称端口、组播类协议（mDNS/SSDP）不在模型内，会当普通伪流处理并按超时回收。

## 7. 学习者阅读路径

按依赖顺序，每站先读文件头注释再读码：

1. **README.md**（Motivation/Features 两节）→ 建立"为什么不要第三个栈"的问题意识；
2. **passt.c 头注释 + 主循环** → 看清 epoll 事件源全集（tap/socket/timer/repair/control）；
3. **tap.h 全文**（很短）→ 三后端抽象与帧上限；
4. **arp.c → dhcp.c → ndp.c → dhcpv6.c** → 理解"用应答器替代内核栈配置"这一层（都是小文件，一天可读完四个）；
5. **flow.h / flow_table.h → udp.c Theory of Operation** → 流表 + 最简单的 L4 翻译；
6. **tcp.c 头部 300 行 Theory of Operation**（本仓高光，含 seq/window 四元组与事件表）→ 再对照 tcp_conn.h 字段读 tcp.c 数据路径；
7. **tcp_splice.c** → pasta 零拷贝与 pipe 池；
8. **isolation.c + seccomp.sh** → 无特权安全的工程化范式；
9. 进阶：vhost_user.c/virtio.c（vhost-user 协议最小实现）、migrate.c/passt-repair.c（TCP_REPAIR 玩法）、doc/platform-requirements/*.c（内核行为契约）；
10. 实操：`doc/demo.sh` 起一个 qemu + passt；`./pasta` 进 ns 里 `dhclient`；`--pcap /tmp/p.pcap` 抓包对照 tcpdump 学镜像行为。

## 8. AI agent 用法

- **本地路径**：`/usr-data/data2/kylin/network/passt`（源码只读；产出写 `/usr-data/data2/kylin/network/knowledge/`）
- **快速定位**：
  - 架构问题先 grep 注释：`grep -n 'Theory of Operation' *.c`（tcp/udp/tcp_splice/isolation 四处）
  - TCP 行为：`grep -n 'seq_to_tap\|wnd_from_tap\|TCP_INFO' tcp.c`
  - 窗口/连接上限：`tcp_internal.h` 的 `MAX_WS/MAX_WINDOW`、`flow.h` 的 `FLOW_INDEX_BITS`
  - syscall 白名单证据：`grep -rn '#syscalls' *.c`（seccomp.sh 的输入）
  - 模式开关：`passt.h` 的 `enum passt_modes`（MODE_PASST/MODE_PASTA/MODE_VU）
- **可跑性**：`make` 零依赖即可出 passt/pasta/passt-repair/pesto 四个二进制；测试 `test/run`（需 root 与 distro 镜像，重）；轻量验证用 `doc/demo.sh`。
- **引用规范**：本仓注释即权威文档，回答行为类问题应引用 `文件名 + Theory of Operation 节`，而非二手博客；版本敏感结论（如 seccomp 白名单条数）标注基于 commit 6aa4f88。



