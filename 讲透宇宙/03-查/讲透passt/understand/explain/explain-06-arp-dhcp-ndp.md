# explain-06 · arp.c + dhcp.c + ndp.c：让 guest 以为身处正常局域网的三个应答器

## 1. 角色定位

这三个小文件（arp.c 206 行、dhcp.c 483 行、ndp.c 475 行，外加 IPv6 侧租约的 dhcpv6.c）合起来扮演 guest 眼里的"路由器 + DHCP 服务器 + 邻居"。passt 的架构里没有网络，只有一台翻译机——但 guest 的网络栈初始化时会发 ARP 询问网关 MAC、发 DHCP 要地址、发 RS 要路由通告，这三个应答器负责把这些控制平面的呼唤全部就地应答，让 guest 无需任何特殊配置就"以为自己接在一台普通路由器上"。它们都是被动应答式（外加少量主动通告），不维护会话状态、不碰 flow 表，各自几百行就是全部。调用入口全在 `tap.c` 的收包路径：`tap4_handler` 把 ARP 帧交给 `arp()`（`tap.c:720`）、UDP/67 交给 `dhcp()`（`tap.c:798`）；`tap6_handler` 把 ICMPv6 NS/RS 交给 `ndp()`（`tap.c:1025`）、UDP/547 交给 `dhcpv6()`（`tap.c:1044`）——先于 L4 协议处理器拦截，返回 1 表示"这包是我的"。

## 2. 内部结构

**arp.c** 三个函数干净利落。`ignore_arp()`（`arp.c:41-61`）过滤非法帧：硬/协议类型、地址长度、操作码（只应答 REQUEST）逐项校验（`arp.c:44-49`）；丢弃 announcement 但保留 0.0.0.0 probe（`arp.c:51-54`）；**不应答 guest 自己地址的询问**（`arp.c:56-58`——guest 问"谁是我自己"没有意义）。`arp()`（`arp.c:70`）构造应答：栈上 packed 结构体 resp（ethhdr+arphdr+arpmsg，`arp.c:73-77`），源 MAC 用 `c->our_tap_mac`，四元组对调（sip←tip、tha←sha，`arp.c:111-113`）；最妙的一笔是 `fwd_neigh_mac_get()`（`arp.c:107-108`）——被询问 IP 若是宿主本地地址，就用宿主真实的邻居表 MAC 应答，让 guest 直连宿主服务时的 ARP 行为与真实网络一致。`arp_send_init_req()`（`arp.c:124`）在 tap 连接建立时主动广播 ARP request 探测 guest MAC（配合 tap.c 的 MAC 学习）。`arp_announce()`（`arp.c:160`）按 RFC 5227 发 gratuitous ARP（probe 变体：sender=target=被通告地址，`arp.c:186-199` 引用 RFC 原文），pasta 把宿主地址映射进 ns 时靠它让 guest 的 ARP 缓存立即生效。

**dhcp.c** 是"单文件 DHCP 服务器"。核心结构：`opts[256]`（`dhcp.c:52`）按选项号直接索引的静态选项表，`struct opt`（`dhcp.c:44`）区分收到的（c/clen）与要发的（s/slen）；`struct msg`（`dhcp.c:110`）是 BOOTP 头+选项区。`dhcp()`（`dhcp.c:303`）流程：剥 eth/ip/udp 头，非 67 端口返回 0 放行（`dhcp.c:331-332`）；校验 BOOTREQUEST 与长度（`dhcp.c:335-344`）；**手写 TLV 解析循环**逐项把选项存进 opts（`dhcp.c:366-391`，处理 255 终止、0 填充两种单字节选项）；状态机极简（`dhcp.c:392-405`）：DISCOVER→OFFER（支持 option 80 Rapid Commit 直接 ACK，`dhcp.c:392-398`），REQUEST→ACK，无 option 53 的纯 BOOTP 也给 ACK。应答内容全部从 ctx 直填：掩码按 prefix_len 算（`dhcp.c:411`）、option 3 网关=`guest_gw`、option 54 服务器=our_tap_addr；**option 121 无类静态路由**处理"网关不在分配子网内"的边角（`dhcp.c:414-429`，塞一条 /32 直连网关的路由）；option 26 MTU、option 6 DNS、option 12 hostname、option 81 FQDN（`dhcp.c:431-463`，flags 0x4 表示 E 编码）；`opt_set_dns_search()`（`dhcp.c:239`）做 DNS 搜索域编码（其搭档 `opt_dns_search_dup_ptr()` `dhcp.c:214` 处理压缩指针去重）。发回应答用 `tap_udp4_send()`（`dhcp.c:480`），广播 flag 决定目的地址（`dhcp.c:477-479`）。`dhcp_init()`（`dhcp.c:74`）只是把 opts 全部置 -1。

**ndp.c** 是 ICMPv6 控制面的三合一。`ndp()`（`ndp.c:358`）：只认 RS(133)~NA(136) 区间（`ndp.c:368`）；NS（Neighbor Solicitation，询问某 IPv6 的 MAC）→ `ndp_na()`（`ndp.c:196`）回应 Neighbor Advertisement；RS（Router Solicitation）→ `ndp_ra()`（`ndp.c:239`）回 Router Advertisement。`ndp_ra()` 的构造是声明式精品：`struct ndp_ra`（`ndp.c:153`）一个初始化器填完 ICMPv6 头（hop_limit=255、rt_lifetime 按 RFC 8319、managed 位=1 表示"还有 DHCPv6 可用"，`ndp.c:242-248`）、prefix_info 选项（/64 前缀、L+A 标志 0xc0、无限生存期，即 SLAAC，`ndp.c:249-256`）、源链路层地址；尾部变长区按需追加 MTU 选项（`ndp.c:266-274`）与 RDNSS/DNSSL 选项（DNS 服务器与搜索域，`ndp.c:276+`）。`ndp_timer()`（`ndp.c:408`）负责周期性主动 RA：间隔取 min(600s, RT_LIFETIME-1) 且不小于 3s（RFC 4861 6.2.1），并**加随机抖动**——注释 `ndp.c:425-435` 解释为什么：防多路由器同步 RA 风暴，random(3) 强度就够。`ndp_send_init_req()`（`ndp.c:468`）与 arp_send_init_req 对称，发 NS 探 guest MAC；`ndp_unsolicited_na()`（`ndp.c:228`）供 pasta 地址映射通告用。

## 3. 外部连接

三个文件的应答出口统一是 `tap.c` 的 `tap_send_single()`/`tap_udp4_send()`/`ndp_send()`→`tap_icmp6_send()`，即下行组帧家族。`dhcp()` 依赖 `conf.c` 填好的 `c->ip4`（addr/prefix_len/guest_gw/our_tap_addr/dns[]/hostname/fqdn/mtu）；`ndp` 同理依赖 `c->ip6`。`arp()` 反向依赖 `fwd.c` 的邻居表（`fwd_neigh_mac_get`）。被依赖方向：仅 tap.c 收包路径与 passt.c 的 `ndp_timer()`（`passt.c:120-121`）和初始化（`dhcp_init`/`dhcpv6_init`，`passt.c:415-419`）。dhcpv6.c 是本篇的 IPv6 移植版（DHCPv6 over UDP 547，租约/DNS/搜索域），结构同构不再展开。

## 4. 数据流

guest 冷启动的一次完整"入网仪式"：guest IP 栈先发 DHCP DISCOVER（UDP 广播 67）→ tap.c 拦截 → `dhcp()` 解 TLV → OFFER（yiaddr=c->ip4.addr，掩码/网关/DNS 全套）→ REQUEST → ACK；guest 配好地址后发 ARP 问网关 MAC → `arp()` 应答 our_tap_mac（或宿主真 MAC）→ guest 开始发包。IPv6 侧：guest 发 RS → `ndp_ra()` 回 RA（前缀+DNS）→ guest SLAAC 自配地址；期间 NS 询问由 `ndp_na()` 应答。此后这三个文件基本沉寂，只剩 `ndp_timer` 每 ~600s 一次的保活 RA。

## 5. 设计决策

共三条哲学。**其一，"假网络"要假得完整**：guest 看到的每个控制面交互都有标准应答，且严格按 RFC 细节实现——ARP 忽略 announcement、DHCP 支持 Rapid Commit 与 BOOTP 回退、RA 带随机抖动、FQDN 选项带正确的 flags/RCODE 编码。这些边角不是炫技：真实世界的 guest 栈（各种 OS/容器/pod）会触发它们。**其二，与转发层共享事实**：DHCP 应答的网关、RA 的前缀、ARP 的 MAC 全部直接引用 ctx 里的同一份配置（conf.c 探测宿主路由得出），绝不另存副本——配置变了应答自动变。**其三，主动探测代替被动等待**：tap 刚连上就用 `arp_send_init_req`/`ndp_send_init_req` 问 guest"你的 MAC 是什么"（配合 `tap.c:1170` 的 MAC 学习），把双向发现压到最小延迟。

## 6. 新人提示

改地址相关配置时的检查清单：`--dns`/`--hostname`/`--search` 选项最终都会流进这三个文件的应答里，加新 DHCP 选项时记得 `opts[]` 表是 256 项定长、`fill()`（`dhcp.c:168`）按序号排序输出。坑：`dhcp()` 返回值三义——0=不是 DHCP（放行给 UDP 处理器）、1=已消费、-1=坏包，tap.c 的调用点依赖这个区分（`tap.c:798` 的 `if (dhcp(...)) continue`）；NDP 的 RS 处理受 `--no-ra` 控制（`ndp.c:389`），测试 SLAAC 前先确认没关。调试三件套：`--pcap` 抓 guest 侧全部交互（offer/ack/RA 一目了然）、`info` 级日志（"DHCP: offer to discover"/"NDP: received NS"）、`--no-dhcp`/`--no-ndp` 开关做对照实验。dhcpv6 与 dhcp 的行为差异（有状态 vs RA+DHCPv6 混合）是 guest OS 差异问题的第一大来源。
