# explain-07 · udp.c / udp_flow.c / udp_vu.c：无连接协议的类连接代理

## 1. 角色定位

UDP 没有 TCP 那样的握手与连接语义，但现实中绝大多数 UDP 应用（DNS、NTP、QUIC 前身协议）都是"客户端从临时端口发包到知名端口、服务端原路换序回复"的类连接模式。`udp.c`（1196 行）就是把这套模式翻译成 flow 表项（FLOW_UDP）的完整实现，文件头的 Theory of Operation（`udp.c:15-81`）分四节讲透设计：UDP Flows（伪连接与超时策略）、Listening sockets（"监听"socket 上的哈希分派）、Flow sockets（connect 消除哈希查找的技巧）、Spliced flows（pasta 模式 socket 对 socket 直转，**不用 splice() 系统调用**——注释 `udp.c:76-78` 明说对数据报没意义，改用 recvmmsg/sendmmsg 对）。辅助角色：`udp_flow.c`（393 行）管伪连接生命周期（建 socket、入哈希、超时）；`udp_vu.c` 是 vhost-user 模式的同逻辑另一条数据面。

## 2. 内部结构

**静态模板池**（`udp.c:122-205`）：UDP_MAX_FRAMES=32 帧一批。每帧一套五段 iovec：`UDP_IOV_TAP`（tap 后端头，passt 模式是 4 字节长度前缀）→ `UDP_IOV_ETH`（预填好的以太网头 `udp_eth_hdr[]`）→ `UDP_IOV_IP`（预填 IP 头 `udp_meta[].ip4h/ip6h`，L2_BUF_IP4_INIT/IP6_INIT 宏）→ `UDP_IOV_PAYLOAD`（UDP 头+数据）→ `UDP_IOV_ETH_PAD`（802.3 60 字节最小帧填充）。`udp_iov_init_one()`（`udp.c:222`）在 init 时把这些 iovec 永久指向静态缓冲；运行期发帧只改少量字段。`udp_update_l2_buf()`（`udp.c:206`）在 guest MAC 变化时被 `proto_update_l2_buf()`（passt.c:154）回调刷新 32 个以太网头模板。

**监听 socket 路径**：`udp_listen_sock_handler()`（`udp.c:930`）收到数据报时 socket 上可能混着多条流的目的地报文，所以 `udp_sock_fwd()` 要用 `recvmsg` 取包、按源五元组查哈希分派——监听 socket 是"多路复用入口"。

**流 socket 路径**：`udp_sock_handler()`（`udp.c:947`）是单流 socket（已 connect），epoll 引用直接带 flowside 索引，零查找。EPOLLERR 走 `udp_sock_errs()`（`udp.c:692`，配 `udp_send_tap_icmp4/6`（`udp.c:412/462`）翻译错误队列）：从 IP_RECVERR 错误队列读出错误（如 ICMP port unreachable），把它**翻译成 ICMP 包送回 guest**——这是 UDP 代理透明性的关键一环，guest 应用依赖 ICMP 错误感知对端不可达。EPOLLIN 按对端 pif 三分派：socket 对 socket（`udp_sock_to_sock`）、vu 模式（`udp_vu_sock_to_tap`）、其余（`udp_buf_sock_to_tap`）。注释 `udp.c:967-975` 记录了一个实测调优：pasta 模式逐个收比批量收吞吐更高（数据局部性？），所以 `n = (c->mode == MODE_PASTA ? 1 : UDP_MAX_FRAMES)`。

**tap 侧入口**：`udp_tap_handler()`（`udp.c:1010`）查 flow 表，未命中且目的单播则建新流（`udp_flow_new()`），命中则刷新活动时间并把报文组帧/直转。

**组帧发送**：`udp_tap_prepare()`（`udp.c:362`）把一个数据报变成 tap 帧——只更新模板里的动态字段：MAC（`eth_update_mac`，源 MAC 用对端真实 MAC `tap_omac`）、按 v4/v6 填 `udp_update_hdr4/6()`（地址、长度、校验和，`no_udp_csum` 选项可跳过 UDP 校验换性能）、`tap_hdr_update()` 写 tap 头长度、`udp_tap_pad()`（`udp.c:342-353`）补 60 字节最小帧。然后整批 `tap_send_frames()`。

**伪连接生命周期**（udp_flow.c）：`udp_flow_new()`（`udp_flow.c:142`）按 flow 状态机走 NEW→INI→TGT→TYPED→ACTIVE，核心动作在 `udp_flow_sock()`（`udp_flow.c:71`）：为目标侧建 **bound+connected** socket——connect 让内核替你过滤：只有这条流的对端报文会到达这个 socket，epoll 事件即流事件（Theory of Operation `udp.c:48-53` 的核心技巧）。从监听 socket 发起的流还会在 INISIDE 再建一个同绑定地址的 connected 复制品（`udp.c:55-60`：即使原监听 socket 因端口自动探测被关掉，回复路径仍然存活）。`udp_flow_close()`（`udp_flow.c:43`）双侧摘哈希、关 socket。超时策略两层（`udp.c:27-32`）：单向流或仅一问一答 → UDP_TIMEOUT（默认 30s，读自 nf_conntrack_udp_timeout，`udp.c:124-129`）；双向多包流 → UDP_TIMEOUT_STREAM（120s）——与 netfilter 的 UDP conntrack 语义对齐，guest 视角的流存活窗口和宿主防火墙一致。`udp_flow_activity()`（`udp_flow.c:387`）负责记账并判断是否升级为 stream 超时。

**ICMP 翻译细节**：`ICMP4_MAX_DLEN 8`（`udp.c:132`）与 `ICMP6_MAX_DLEN`（按 IPv6 最小 MTU 算，`udp.c:133-135`）分别遵守 RFC 792/4443 的"错误报文携带原报文头若干字节"规则。

## 3. 外部连接

udp.c 依赖 flow.c（表项与哈希）、tap.c（帧发送与 tap 头宏 `tap_hdr_iov/tap_hdr_update`）、`udp_internal.h`（udp.c 与 udp_flow.c 的私有契约）。`udp_vu.c`（4 个函数：`udp_vu_hdrlen` `udp_vu.c:42`、`udp_vu_sock_recv` `udp_vu.c:65`、`udp_vu_prepare` `udp_vu.c:103`、`udp_vu_sock_to_tap` `udp_vu.c:148`）依赖 `vu_common.c` 的批量收发原语（`vu_collect/free` 系列）——它不组装完整 L2 帧，而是把 L3/L4 头直接写进 vring 描述符。上游：passt.c 的两个 epoll 入口 + `udp_init()`（`udp.c:1184`：读超时参数、初始化模板池、pasta 模式额外 `udp_splice_iov_init()`）；flow.c 的 `udp_flow_defer/timer` 巡检回调。

## 4. 数据流

guest 发一条 DNS 查询：帧到 tap → `udp_tap_handler` 查 PIF_TAP 侧未命中 → `udp_flow_new`：flow_alloc → flow_target（fwd 判定 PIF_HOST）→ FLOW_SET_TYPE(FLOW_UDP) → `udp_flow_sock` 建 connected socket 入 epoll → 查询数据 sendto → 应答回来 EPOLLIN → `udp_sock_handler`：topif==PIF_TAP 且非 vu → `udp_buf_sock_to_tap`：recvmmsg 批量收进 `udp_payload[]` → `udp_tap_prepare` 更新模板字段 → `tap_send_frames` 一批帧回 guest。若查询的目的端口没人监听，宿主内核回 ICMP unreachable → 该 socket 的错误队列有货 → EPOLLERR → `udp_sock_errs` 读错误队列 → `udp_send_tap_icmp4` 组 ICMP 包告诉 guest——与直连行为完全一致。

## 5. 设计决策

三条最值得学。**其一，connect() 当过滤器**：为每条伪连接建 connected socket，让内核做五元组匹配，epoll 事件自带流身份——对比"一个 socket 收所有包再软件分派"（监听路径的无奈之举），流路径零哈希开销。两条路径并存的原因也在 Theory of Operation 里写明：监听 socket 天然多路复用（入站方向无法预知来源），流 socket 是我们主动建的（可以精确 connect）。**其二，超时语义对齐 netfilter**：直接读 `/proc/sys/net/netfilter/nf_conntrack_udp_timeout{,_stream}`（`udp.c:124-126`），保证 passt 的流存活窗口与宿主 conntrack 一致——guest 侧应用感知不到中间多了一层代理。**其三，模板池+五段 iovec**：所有头字段按"静态预填/动态更新"二分，发送路径只有字段级写没有结构体级构造，代价是 32 帧的静态内存，收益是零分配零拷贝组帧。

## 6. 新人提示

读代码顺序：`udp.c:15-81` Theory of Operation → 静态缓冲区声明区（`udp.c:137-204`）→ `udp_sock_handler`。注意 udp.c/udp_flow.c 的分工边界（生命周期全在 udp_flow.c，数据面全在 udp.c），`udp_internal.h` 是两者的私有头，别把内部函数挪到 udp.h。坑：`UDP_IOV_*` 的五段布局与 `tcp_buf.c` 的帧模板是同一套思想但宏不通用，改一处别顺手"统一"另一处；splice 路径的名字（udp_splice_*）有历史误导性——不调用 splice(2)，见 `udp.c:76-78` 注释。调试：`--udp-no-csum` 快速验证校验和问题；pcap 抓包看 ICMP 翻译是否生效；`udp_flow_activity` 的 trace 日志能看清一条流何时升级 stream 超时。
