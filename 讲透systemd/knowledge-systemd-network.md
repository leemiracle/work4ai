# systemd 网络子系统深读（systemd-networkd / netdev / resolved / libsystemd-network / udev link）

- 仓：/usr-data/data2/kylin/network/systemd（git，只读消化）
- commit：2026-11-06 `3e38798c35` "test-vmspawn-memory: add missing missing short comments"，版本 **263~devel**（meson.version）
- 消化范围：`src/network/`（networkd+networkctl+netdev+wait-online+tc）、`src/resolve/`、`src/libsystemd-network/`（协议库）、`src/udev/net/`（link-config）、`src/bpf/`（网络相关 BPF）、`network/`+`man/` 配置面、`docs/` 架构文档、`TODO.md` 官方欠账
- 总评：**Linux 网络管理的"内核态-用户态桥梁"教科书实现**——一个 sd-event 单线程事件循环吃下 rtnetlink/genl/udev/D-Bus/Varlink 五路输入，用"请求队列 + 配置状态位 + 计数器汇合"把异步内核配置收敛成可判定的 Link 状态机；协议库（DHCP/DHCPv6/NDISC/LLDP/radv/IPv4LL/ACD）全部自研、零外部依赖、全部带 fuzz 入口；resolved 用 scope/transaction/cache 三层对象模型实现了带 DNSSEC 与 DoT(OpenSSL) 的本地 stub（127.0.0.53/54）。对麒麟/信创场景：这是把网卡从"内核枚举"到"可路由"全生命周期接管的参考实现，且 sysctl 写入已被 BPF ring buffer 监控（2026 年新趋势）。

## 1. systemd 总体架构 30 秒背景（消化网络线的必要前提）

`docs/ARCHITECTURE.md` 钉版的分层规则（谁可用谁）：

- `src/fundamental/`（EFI+用户空间通用，零依赖）→ `src/basic/`（用户空间原语）→ `src/libsystemd/`（libsystemd.so，含 sd-event/sd-netlink/sd-device/sd-network 等公共 API）→ `src/shared/`（libsystemd-shared-nnn.so，组件间共享）→ 各组件目录（`src/network`、`src/resolve`、`src/udev` 等）。
- **Rust 已进入共享层**：`src/rust/` 生成 `systemd_shared` crate，Rust 程序与 C 程序同 meson 声明、同链 libsystemd-shared。
- PID1 进程模型：`posix_spawn() → systemd-executor（memfd 反序列化沙箱配置）→ execve(目标程序)`，避免 fork 后 exec 前的 glibc 禁区。
- 配置三入口原则（unit 设置 = unit file 的 load-fragment-gperf + D-Bus 的 dbus-*.c + 客户端 bus-unit-util.c）——**networkd 完全同构**：`.network` 文件 gperf 解析（networkd-network-gperf.gperf，342+ 键）、D-Bus（org.freedesktop.network1）、networkctl CLI 三面一体。
- 网络线相关的 docs/ 专题：`NETWORK_ONLINE.md`（network-pre/network/network-online 三 target 语义：network-pre=防火墙先行的被动点、network=主要为关机序、network-online=主动等待且默认 90s 超时，官方立场是"好软件应监听 rtnetlink 动态响应而非等 online"）、`PREDICTABLE_INTERFACE_NAMES.md`（enp3s0f2 命名策略，udev net 名字策略的文档面）、`WRITING_NETWORK_CONFIGURATION_MANAGERS.md`（NM/connman 如何通过 SetLinkDNS/SetLinkDomains 总线 API 对接 resolved——networkd 自己就是这套 API 的第一个全功能消费者）、`RESOLVED-VPNS.md`。

---

## 2. networkd 架构与状态机（src/network/，~95 个 .c 文件）

### 2.1 进程骨架与权限

`networkd.c`（仅 130 行）：geteuid()==0 时降权到 `systemd-network` 用户，但**保留 6 个 capability**：CAP_NET_ADMIN/CAP_NET_BIND_SERVICE/CAP_NET_BROADCAST/CAP_NET_RAW/CAP_SYS_ADMIN/CAP_BPF（L74-79）——BPF capability 的保留与 §8 的 sysctl-monitor 直接相关。启动序：manager_new → manager_setup → parse config → load config → enumerate（扫现有链路）→ deserialize（/run/systemd/netif/state 断点续配）→ manager_start → `sd_event_loop`。**serialize/deserialize 是 networkd 重启（如升级）不丢网络状态的关键**（networkd-serialize.c + networkd-state-file.c，TODO.md 承认"状态序列化的单测仍缺"）。

### 2.2 事件驱动：五路输入一个循环（networkd-manager.c）

Manager 持有单一 `sd_event`，挂接：

1. **rtnetlink**（`sd_netlink_open` → attach_event → `netlink_add_match`）：RTM_NEWLINK/DELLINK、NEW/DELADDR、NEW/DELNEIGH、NEW/DELROUTE、NEW/DELRULE、QDISC/TCLASS 共 11 类消息各注册回调（manager_rtnl_process_link/address/neighbor/route/rule/qdisc/tclass）。还调 `sd_netlink_increase_rxbuf` + **`sd_netlink_attach_filter`**（BPF 过滤器直接在 netlink socket 上预筛消息，manager_setup_rtnl_filter，L340-371——内核态丢包前过滤，性能优化）。
2. **generic netlink**：nl80211（CONFIG + MLME 组，wlan/wiphy 管理）、wwan。
3. **udev device monitor**（`sd_device_monitor`）：subsystem 过滤 `net` + `ieee80211` + `rfkill`，manager_process_uevent 处理设备初始化完成（link 从 PENDING 出发的扳机）。
4. **D-Bus**：org.freedesktop.network1（link/manager/network 三对象）+ PrepareForSleep 信号（休眠唤醒后 reconfigure）+ ModemManager 信号。
5. **Varlink**：`io.systemd.Network`（Reload 等新接口，networkd-manager-varlink.c）+ `io.systemd.Network.Link` + 独立 metrics socket（networkd-varlink-metrics.c，sd_listen_fds 取 4 个 fd：rtnl/varlink/varlink-metrics/resolve-hook）。

Manager 数据面：`links_by_index/links_by_name/links_by_hw_addr/links_by_dhcp_pd_subnet_prefix` 四个索引 hashmap + `OrderedHashmap *networks`（.network 集合）+ `address_pools` + speed_meter（可选周期统计吞吐）。

### 2.3 Link 状态机（networkd-link.h/c，3320 行核心）

```
PENDING（udev 未初始化完）→ INITIALIZED（udev 就绪，收到 device uevent）
  → CONFIGURING（link_configure 启动配置管线）
  → CONFIGURED（link_check_ready：全部 *_configured 位汇齐）
  → UNMANAGED（无 .network 匹配或 Unmanaged=yes）
  → FAILED（任一配置失败） / LINGER（RTM_DELLINK 后延迟清理）
```

**link_configure()（networkd-link.c L1289）的配置管线顺序**（每步都是异步 request）：drop_unmanaged_config → bound_to_list → traffic_control（tc）→ MTU →（CAN 特例短路）→ SR-IOV VF → sysctl → MAC → IPoIB → flags → group → addrgen mode → master（加入 bond/bridge）→ **stacked netdevs** → bond/bridge/bridge-vlan 参数 → activate → IPv4LL → DHCP4 → DHCP6 → NDISC → DHCP relay → DHCP server → RADV → LLDP rx/tx → static configs（地址/路由/邻居/FDB/MDB/nexthop/routing policy rule/address label）→ modem reconfigure。

**汇合机制（最值得学的工程模式）**：每个配置对象有独立 `NetworkConfigState` 位机（networkd-util.h L17-27）：
`REQUESTING(1<<0) → CONFIGURING(1<<1) → CONFIGURED(1<<2)`，GC 用 `MARKED(1<<3) → REMOVING(1<<4)`。Link 上再叠加 `unsigned static_route_messages` 等**计数器**（在途 netlink 请求个数），归零且 configured 位置位才 link_check_ready。所以"配置完成"是全维度计数器清零的可判定事件，而非定时器猜测。

**operstate 双轴模型**（src/libsystemd/sd-network/network-util.h，networkctl status 的语义来源）：
- LinkCarrierState：off/no-carrier/dormant/degraded-carrier/carrier/enslaved（物理层轴）
- LinkAddressState：off/degraded/routable（协议层轴，degraded=只有 link-local 无全球地址）
- LinkOperationalState=9 态合成：missing/off/no-carrier/dormant/degraded-carrier/carrier/degraded/enslaved/routable
- LinkOnlineState：offline/partial/online——wait-online 用 `RequiredForOnline=` + `RequiredFamilyForOnline=` 对照 operstate 区间（默认 DEGRADED..ROUTABLE，L91-95 LINK_OPERSTATE_RANGE_DEFAULT）判 online。
- `link_update_operstate()` 同时向 master（bond/bridge）传播，master 的 operstate 由成员聚合。

### 2.4 请求队列（networkd-queue.c）

所有对内核的写操作（RequestType：activate_link/address/address_label/bridge_fdb/bridge_mdb/dhcp_* /ndisc/neighbor/neighbor_proxy/…约 20 种）走统一 Request 队列：带 netlink slot 引用、回调计数（REPLY_CALLBACK_COUNT_THRESHOLD=128 防积压告警）、link 引用计数。**外部队列而非每 link 自旋**，重载（`networkctl reload`）时可整体 drain 后重放。

### 2.5 值得注意的子模块

- **networkd-dhcp-prefix-delegation.c**：DHCPv6-PD 前缀切分给下游接口（links_by_dhcp_pd_subnet_prefix 索引就是为它建的）。
- **networkd-ndisc.c**：RA 处理器，gperf 键族 `IPv6AcceptRA.Use*`（UseRedirect/UseGateway/UseRoutePrefix/UseAutonomousPrefix/UseOnLinkPrefix/UsePREF64/UseDNS/UseDNR/UseDomains/UseMTU/UseHopLimit/UseReachableTime，L342-353）暴露了细粒度取舍；ndisc_rdnss/dnssl/captive_portals/pref64/redirects/dnr 全部有独立集合。
- **networkd-neighbor-proxy.c / networkd-netlabel.c**：邻居代理与 CALIPSO/NetLabel（少见的网络栈冷角）。
- **networkd-resolve-hook.c**：networkd→resolved 的 DNS 信息推送通道（独立 fd，systemd-resolved-hook.service）。
- **networkd-speed-meter.c**：周期读 /proc/net/dev 差分，networkctl status 显示速率。
- **networkctl\*.c 拆 12 个文件**：list/status-link/status-system/lldp/dhcp-lease/link-info(-json)/address-label/config-file/journal/misc/description——CLI 按动词分文件的当代组织法。
- **wait-online/**：wait-online.c 主 + link/manager 两层；默认判据=所有受管 link 达 CONFIGURED/FAILED/UNMANAGED 且至少一个 online（docs/NETWORK_ONLINE.md 钉板）。
- **generator/**：systemd-network-generator（从内核 cmdline ip=/rd.route= 生成 .network/.netdev，云镜像无配置文件场景的兜底）。

### 2.6 fuzz 与测试组织

- `fuzz-network-parser.c`/`fuzz-netdev-parser.c`：配置文件解析 fuzz（oss-fuzz 常驻）；libsystemd-network 侧另有 fuzz-dhcp-client/dhcp6-client/dhcp-server/dhcp-relay/lldp-rx/ndisc-rs 六个**协议状态机 fuzz**——网络报文直接喂客户端状态机，这是协议库质量的护城河。
- `test-network.c`（252 行）是 request 机制单测；真正的集成测试在 `test/networkd/`（python，networkd-test.py）+ `test/integration-tests/TEST-85-NETWORK/`（一套完整 VM/nspawn 系统级测试，meson.build 驱动）。

---

## 3. netdev 全表（src/network/netdev/，38 种虚拟设备）

`NetDevKind` 枚举（netdev.h L47-89）+ `netdev_kind_table`（netdev.c L97-138）+ vtable 分派（netdev_vtable，每 kind 一个 `NetDevVTable`，含 create/fill/create_message 等回调）。每 kind 一个 .c 文件、gperf 键盘 `netdev-gperf.gperf`（293 行）负责 `[NetDev]`/`[XXX]` 节解析。全 38 种 Kind= 值与内核机制对照：

| 类别 | Kind= 值 | 内核机制 / 一句话语义 |
|---|---|---|
| 虚拟交换 | bridge | rtnl IFLA_INFO_KIND "bridge"，二层交换+STP/FDB/MDB/VLAN |
| 聚合 | bond | rtnl bond，主备/802.3ad 聚合，成员经 `.network` 的 Bond= 入队 |
| VLAN 族 | vlan / vxlan / macvlan / macvtap / ipvlan / ipvtap | 802.1Q / UDP 封装_overlay / MAC 复用 / tap 变体 / L3 复用（ipvtap=IPVLAN+tap） |
| CAN 族 | vcan / vxcan | 虚拟 CAN / 虚拟 CAN 交叉对（类似 veth 的 CAN 版） |
| 隧道（sit/ipip 系） | sit / ipip / vti / vti6 / ip6tnl | IPv6-in-IPv4 / IPv4-in-IPv4 / IPSec VTI 隧道 / VTI over IPv6 / 通用 IPv6 隧道 |
| 隧道（gre 系） | gre / gretap / ip6gre / ip6gretap / erspan | GRE / GRE 以太桥 / IPv6 GRE 两代 / 镜像流量抓取（ERSPAN） |
| UDP 隧道 | fou / geneve / bareudp / l2tp | Foo-over-UDP / GENEVE / bare UDP 封装任意协议 / L2TPv3 |
| 加密/安全 | wireguard / macsec / xfrm | WG（私钥走 credential，TODO 提到 macsec 也应如此）/ 802.1AE 链路加密 / XFRM policy 隧道接口 |
| 点对点 | veth / tun / tap | 容器对连线（vz/vb/ve 三套 .link+.network 预置即用它）/ 字符设备 TUN / TAP |
| 无线 | wlan | 虚拟 wlan 接口（nl80211 多接口能力，phy 上开 AP/STA） |
| 延展 | hsr / ifb / nlmon / dummy / batadv / ipoib / vrf | HSR 冗余环 / 中间功能块（tc 重定向靶）/ netlink 监听伪设备 / 空设备 / B.A.T.M.A.N. mesh / InfiniBand IPoIB / VRF 路由域 |

工程要点：
- **创建路径三分**：纯 rtnl 可建（bridge/bond/vlan…）直接 RTM_NEWLINK+IFLA_INFO_DATA；tun/tap 走 /dev/net/tun；wireguard/wlan 等带独立协商。stacked netdev（`_NETDEV_KIND_TUNNEL` 供 config_parse_stacked_netdev 引用，netdev.h L87）需要**本端地址就绪**才能建——这就是 link_configure 管线里 `link_request_stacked_netdevs` 的位置及 LinkConfiguringReason 里独立 reason 的原因。
- **NetDevState**：LOADING →（配好）→（等待 carrier/从属）→ READY；netdev 与 .network 双向引用（`.netdev` 声明设备，`.network` 的 `Bond=`/`Bridge=` 把物理口挂上去）。
- fuzz-netdev-parser 覆盖整个解析面。

---

## 4. 协议库剖析（src/libsystemd-network/，sd-event 之上的自研协议栈）

全库零外部依赖（不链 libc 之外的协议库），对外以 `sd-*.h` 公共 API（libsystemd.so 的一部分）暴露，networkd/timesyncd/test 各自消费。**每个客户端都有对应 fuzz**（fuzz-dhcp-client/dhcp6-client/lldp-rx/ndisc-rs…）。

### 4.1 DHCPv4（sd-dhcp-client.c 1447 行 + dhcp-server + relay）

- 状态机（dhcp-protocol.h L105）：`STOPPED → INIT → SELECTING → REQUESTING → BOUND → RENewing → REBINDING`，另有 INIT_REBOOT→REBOOTING 快路径（记住旧 lease 直接 REQUEST）。
- 完整 RFC2131 时序 + client-id（dhcp-client-id.c，支持 mac/duid 类型）、DUID 生成（sd-dhcp-duid.c：en/uuid/LLT/LNR 四型）、rapid commit、IPv4LL fallback 联动、`dhcp-client-send.c` 拆出发送面。
- **SD_DHCP_SERVER**（sd-dhcp-server.c）：static lease（networkd-dhcp-server-static-lease.c 挂 `.network` `[DHCPServer]`）、PersistLeases= 落 /run/systemd/netif/dhcp-server-lease/（networkd.conf gperf L47，重启续租）、FORCERENEW 支持。
- **SD_DHCP_RELAY**（sd-dhcp-relay.c + dhcp-relay-upstream/downstream.c）：跨网段中继，networkd 的 `[DHCPRelay]` 消费。
- 6rd 选项支持（Link 里 `dhcp4_6rd_tunnel_name`——DHCP 拿到 IPv6 前缀自动建隧道，国内运营商场景罕见但源码已备）。

### 4.2 DHCPv6（sd-dhcp6-client.c 1618 行）

状态机（dhcp6-protocol.h L51）：`STOPPED → SOLICITATION → REQUEST → BOUND → RENEW → REBIND`，加 INFORMATION_REQUEST（无状态只拿 DNS 等）与 STOPPING。IA_NA（非临时地址）完整实现；**TODO 官方欠账**：IA_TA 临时地址、RECONFIGURE 消息、DHCPv6 authentication、断电续租（client->ia_na 持久化）都没做。

### 4.3 NDP / NDISC（sd-ndisc.c 570 行 + ndisc-option/router/neighbor/redirect/router-solicit 五个对象头）

ND（IPv6 Neighbor Discovery）双角色拆分：
- **RS 发送方**（sd-ndisc.c + ndisc-router-solicit）：发 Router Solicitation；
- **RA 接收方**（sd-ndisc-router.c）：解析 Router Advertisement 全家——PIO（前缀）、RDNSS（DNS）、DNSSL（搜索域）、**PREF64（NAT64 前缀发现，较新 RFC 8781）**、**DNR（Discovery of Resolvers，RFC 9463，加密 DNS 发现；Link 结构里 ndisc_dnr 集合+IPv6AcceptRA.UseDNR 已实装）**、captive portal、MTU、redirect（sd-ndisc-redirect.c，UseRedirect 控制）。
- icmp6-packet.c/icmp6-util.c：ICMPv6 层；option 解析 ndisc-option.c。
- fuzz-ndisc-rs 直接喂 RS 构造。

### 4.4 RADV（sd-radv.c）：networkd 的路由通告**服务端**——`[IPv6SendRA]` 发 RA（给下游发前缀/DNS），与 DHCPv6-PD 前缀链联动（拿到 PD 前缀后自动 advertise 出去）。

### 4.5 IPv4LL + ACD（sd-ipv4ll.c + sd-ipv4acd.c）

- IPv4LL：169.254/16 链路本地地址自配（RFC 3927）。
- **ACD（Address Conflict Detection，RFC 5227）**：IPv4ACDState 独立状态机（INIT/PROBING/ANNOUNCING/…），默认 ACD 超时 200ms（DEFAULT_ACD_TIMEOUT_USEC）；DHCP/IPv4LL 拿到地址先 ACD 探测再上链路，冲突则 DECLINE——networkd 的 `ipv4acd_by_address` hashmap 支持多地址并行探测。

### 4.6 LLDP（sd-lldp-rx.c + sd-lldp-tx.c + lldp-neighbor.c）

接收：邻居信息存 lldp-neighbor 对象（ chassis/port id/description/system name/capabilities/TLV 全解析，tlv-util.c），networkd 把它喂给 networkctl lldp 与 Varlink JSON 输出；发送：`[LLDP]` 节声明机架身份（chassis id/system description）。TODO 欠账：读取 802.3 max-frame-size TLV 以发现 jumbo。

### 4.7 其他

- **arp-util / ip-util**：arp 头构造、checksum、FCS；
- **sd-dns-resolver.c + dns-resolver-internal.h**：异步 DNS 解析辅助（DHCPServer 用）；
- **network-common/internal**：ether_addr↔string 等共享件；
- test-dhcp-\*/test-ndisc-\*/test-ipv4ll/test-acd/test-tlv-util 等单测齐备，另有 test-ipv4ll-manual 供真机手工验证。

---

## 5. resolved 深析（src/resolve/，87 个 .c/.h）

### 5.1 对象模型四层（TODO 承认"还没有文档解释这些对象"，此处源码钉板）

- **Manager**（resolved-manager.c，2378 行）：持有全局 unicast scope、stub 监听、LLMNR/mDNS 套接字族（ipv4/ipv6 × udp/tcp 六个 fd，manager_new L730-736 可见）、/etc/hosts 缓存、trust anchor。
- **DnsScope**（resolved-dns-scope.c）：解析的"作用域"——origin 分 GLOBAL（全局 DNS）/LINK（每接口的 LLMNR/mDNS）/DELEGATE（resolved-dns-delegate：把下游容器/VM 的 DNS 委托进来，较新机制）；每 scope 关联 protocol（DNS/LLMNR/mDNS）+ address family。
- **DnsQuery → DnsTransaction**（resolved-dns-query.c/transaction.c 3878 行）：一个用户查询按 scope 拆多个并行 transaction；**DnsTransactionState 18 态**（transaction.h L10-31）：NULL→PENDING→VALIDATING→SUCCESS，失败面细分 RCODE_FAILURE/NO_SERVERS/TIMEOUT/ATTEMPTS_MAX_REACHED/INVALID_REPLY/ERRNO/ABORTED/DNSSEC_FAILED/NO_TRUST_ANCHOR/RR_TYPE_UNSUPPORTED/NETWORK_DOWN/NOT_FOUND/NO_SOURCE/**STUB_LOOP**（检测到自己转发给自己的环——对应 §5.2 的 127.0.0.53/54 过滤）。
- **DnsCache**（resolved-dns-cache.c）：per-scope 缓存；**DnsCacheMode 三态**（shared/resolve-util.h L16）：NO/YES/NO_NEGATIVE（只缓存正向，不缓存否定应答——弱网下防 NXDOMAIN 污染）。

### 5.2 本地 stub 双地址：127.0.0.53 与 127.0.0.54

- `INADDR_DNS_STUB = 0x7f000035`（127.0.0.53，resolve-util.h L8）与 `INADDR_DNS_PROXY_STUB = 0x7f000036`（127.0.0.54）。
- manager_dns_stub_start（resolved-dns-stub.c L1388）：UDP/TCP × 两个地址共 4 个监听（.53=完整解析器 stub 给 /etc/resolv.conf "nameserver 127.0.0.53"；.54 是**上行代理模式**给第三方（如 nspawn/TODO 里 nftables 转发 53 端口的场景），不做本地合成记录）；`DNSStubListener=` 三态 udp/tcp/yes；EADDRINUSE/EPERM 时优雅降级为关闭并告警。
- **自环防御三道**：配置解析时过滤、dns_server_is_stub（resolved-manager.c L1915-1938 双保险）、上游服务器解析出的 0.0.0.0/127.0.0.53/54 静默剔除（resolved-dns-server.c L903）+ STUB_LOOP 事务态兜底。
- `/run/systemd/resolve/stub-resolv.conf`（"nameserver 127.0.0.53\noptions edns0 trust-ad"）与 `resolv.conf`（直连上行模式）双文件策略（resolved-resolv-conf.c L315）。
- **socket-graveyard**（resolved-socket-graveyard.c）：TCP 连接关闭后延后释放 socket，防 TIME_WAIT 期端口被攻击者抢注——安全工程细节。

### 5.3 DNSSEC 与 DoT

- **DNSSEC**：信任锚（resolved-dns-trust-anchor.c，内置根 KSK + RFC 5011 自动滚动）、validator（resolved-dns-dnssec.c）、**支持 ML-DSA 后量子签名**（test-dnssec-mldsa.c 实锤已实装）；DnssecVerdict/DnssecResult 全枚举；per-link DNSSEC 模式（captive portal 场景可按接口关验证）。
- **DNS-over-TLS**：resolved-dnstls.\* 只剩 **OpenSSL 一条后端**（`#if !HAVE_OPENSSL #error`，L13-14——gnutls 后端已删）；SSL_CTX 全局 + SSL_SESSION per-server 会话复用 + 流式握手状态机（DnsTlsStreamData.handshake）。

### 5.4 多播名字解析与杂项

- **LLMNR**（RFC 4795）与 **mDNS**（resolved-mdns.c + resolved-llmnr.c）：单标签名走 LLMNR、.local 走 mDNS；**DNS-SD 浏览已实装**（resolved-dns-browse-services.c + resolvectl browse-services），服务注册还在 TODO。
- **合成记录**（resolved-dns-synthesize.c）：\*_gateway/\*_outgoing.\_udp.\{接口名\} 等魔术名 + nss-resolve 联动；**etc-hosts**（resolved-etc-hosts.c 带文件监控增量重载）+ **static-records**（新机制，可下发额外 RR）。
- **Varlink 双接口**：`io.systemd.Resolve`（查询/订阅 DNS 配置变化，DNR 时代的 API 面）+ `io.systemd.Resolve.Monitor`（订阅查询结果流）；D-Bus 侧 org.freedesktop.resolve1 完整保留（SetLinkDNS/SetLinkDomains/SetLinkDNSSEC/RevertLink——文档 WRITING_NETWORK_CONFIGURATION_MANAGERS.md 即此 API 教程）。
- **resolvconf 兼容**（resolvconf-compat.c）：/usr/bin/resolvconf 命令别名。
- 测试面：resolved 是全仓测试密度最高的目录之一（18 个 test-\*.c，含 test-resolved-dummy-server 可当假上游服务器做黑盒测）。

---

## 6. 网络配置文件体系（.link / .netdev / .network / networkd.conf / resolved.conf / sysctl 默认值）

### 6.1 三类 per-link 文件的职责切分

| 文件 | 谁消费 | 管什么 | 时机 |
|---|---|---|---|
| `.link`（systemd.link(5)） | **udev**（systemd-udev，src/udev/net/link-config.c） | 设备命名/MAC/驱动绑定：NamePolicy=/AlternativeNamesPolicy=（keep/database/onboard/slot/path/mac 六策略顺序链）、MACAddressPolicy（persistent/random/none）、SpeedBits/WakeOnLan 等 ethtool 面 | 设备**枚举时**（早于 networkd） |
| `.netdev`（systemd.netdev(5)） | networkd | 创建虚拟设备（§3 全表 38 种），`[NetDev] Kind=` + 各 kind 专属节 | 按需/启动时 |
| `.network`（systemd.network(5)） | networkd | 一切链路层之上的配置：地址/路由/邻居/DHCP/NDISC/桥接/tc/… | link 就绪后（状态机 §2.3） |

匹配语法共享 `[Match]`（MACAddress=/PermanentMACAddress=/Driver=/Type=/Host=/Virtualization=/KernelCommandLine=/Property= 等，net-condition.c），目录优先级 /etc > /run > /usr/lib，**首个匹配胜出**（.network 是全部叠加需 `Match` 唯一化，.link/.netdev 同名覆盖）。

### 6.2 `.network` 关键节速查（gperf 实证，networkd-network-gperf.gperf 共 342+ 键）

- `[Network]`：DHCP=（yes/no/ipv4/ipv6）、IPv6AcceptRA=（tri）、LinkLocalAddressing=（v4/v6/yes/no）、Bridge=/Bond=/VRF=（挂主设备）、IPMasquerade=、ConfigureWithoutCarrier=、KeepConfiguration=（dhcp/静态/断 carrier 保配置——升级重启网络不抖的关键）、DefaultRouteOnDevice=、DNS=/Domains=/NTP=。
- `[Address]`（多节）：Address=/Peer=/Label=/PreferredLifetime=，`AddressState=` 语义见 ip 添加失败重试。
- `[Route]`：Gateway=/Destination=/Metric=/Table=/Source=/MultiPath=（nexthop 语法）/GatewayOnLink=。
- `[DHCPv4]/[DHCPv6]/[IPv6AcceptRA]/[IPv6SendRA]/[DHCPServer]/[DHCPRelay]/[LLDP]/[Bridge]/[BridgeVLAN]/[CAN]/[QDisc]/[RoutingPolicyRule]/[Neighbor]/[SR-IOV]/[TrafficControl]` 等各成体系；`IPv6AcceptRA.Use*` 13 键族见 §2.5。
- **tc 独立目录** `src/network/tc/`：qdisc 家族 htb/htb-fq-codel/fq/fq-codel/fq-pie/codel/pie/cake/gred/drr/ets/hhf/netem/mq/multiq/qdisc+hbf（bufferbloat 全家桶），tclass/filters 由 `[QDisc]`/`[Filter]` 节驱动。

### 6.3 全局配置与默认值

- **networkd.conf**（src/network/networkd.conf + networkd-gperf.gperf）：`[Network]` SpeedMeter(IntervalSec)/ManageForeignRoutes/ManageForeignNextHops/ManageForeignRoutingPolicyRules（是否回收他人配置的路由——多网络管理器共存开关）、`[DHCPServer] PersistLeases=`、`[DHCPv4] RenewOffsetSec=` 等。
- **resolved.conf.in**：DNS=/FallbackDNS=/Domains=/DNSSEC=/DNSOverTLS=/Cache=/DNSStubListener=(yes/udp/tcp/no)+**DNSStubListenerExtra=**（自定义地址:端口多开 stub，resolved-conf.c config_parse_dns_stub_listener_extra）/ReadEtcHosts=/StaleRetentionSec=。
- **sysctl.d/ 顶层目录**：网络相关默认值（如 50-default.conf 的 IPv6 accept_ra 处理、99-sysctl.conf 占位）+ networkd 自身按 `.network` 的 sysctl 项写 /proc/sys/net（ipv4.ip_forward、rp_filter、accept_ra 等 per-link 化）。
- **顶层 network/ 预置文件**（装机即用的 drop-in 体系）：`99-default.link`（默认命名策略）、80-container-ve/vb/vz + host0（nspawn 三种联网模式）、80-vm-vt、80-6rd-tunnel（.link+.network 成对）、80-namespace-ns、wifi adhoc/ap/station 例、89-ethernet 例——**这组文件本身就是"systemd 哲学的配置样例库"**。
- timesyncd（NTP，SNTP client）不在本任务范围但 man 面共享（timesyncd.conf、org.freedesktop.timesync1）。

### 6.4 udev 侧 link-config 深一层（src/udev/net/）

link-config.c 是 udev builtin（net_setup_link）：udev 收到 net 设备 uevent → 匹配 .link → 应用命名策略（netif-naming-scheme.c 按 --default-net-naming-scheme 版本切换 kernel/database/onboard/slot/path/mac 组合，见 docs/PREDICTABLE_INTERFACE_NAMES.md）→ 设置 MAC/驱动 ethtool 参数 → 重命名（ALT_IFNAME 保留旧名）。fuzz-link-parser 覆盖。**与 networkd 的分工**：udev 管"你是谁"（名字/MAC），networkd 管"你怎么配"（地址/路由）。

---

## 7. systemd×eBPF 交汇点（源码实证，非文档转述）

本仓 BPF 程序统一在 **`src/bpf/`**（.bpf.c 骨架源 + vmlinux.h；编译期 clang -target bpf，运行期 libbpf 经 `dlopen_bpf()` 弱链接——LIBBPF_NOTE(recommended)，无 libbpf 时全部优雅降级）。网络相关交汇五处：

1. **networkd 的 sysctl 写入监控（最新鲜，2026）**：`src/bpf/sysctl-monitor.bpf.c` —— BPF_PROG_TYPE_CGROUP_SYSCTL 程序 attach 到 **root cgroup**，过滤条件"目标 cgroup == networkd 自己"（cgroup_map 只放 networkd 的 cgroup fd），拦截 networkd 进程的 sysctl write 调用，把"键+值"丢进 **BPF_MAP_TYPE_RINGBUF（256KB）**；用户态 networkd-sysctl.c `manager_install_sysctl_monitor()`（L100-166）用 ring_buffer\_\_poll + sd_event_add_io 消费，维护 `sysctl_shadow` hashmap（写过的 sysctl 的影子值）。用途：**区分"networkd 自己写的 sysctl"与"外部/管理员改的 sysctl"**——link 重新配置时只需清自己的影子（link_clear_sysctl_shadows），且能感知外部篡改触发 reconfigure。这是"cgroup-level syscall 拦截做配置管理一致性"的罕见案例。
2. **netlink socket 上的 BPF 预过滤**：networkd-manager.c L340-371 `manager_setup_rtnl_filter()` → `sd_netlink_attach_filter()`——经典 sock filter（cBPF）挂在 rtnl socket，内核态丢弃不关心的多播组消息，减用户态唤醒。
3. **cgroup 网络过滤（PID1 侧，per-unit）**：`IPIngressFilterPath=`/`IPEgressFilterPath=`（systemd.resource-control(5) L1163，src/core/dbus-cgroup.c 属性）挂 bpffs 中的 cgroup-bpf 程序；`BPFProgram=<hook>:<path>`（L1204）泛化到任意 cgroup hook（inet/bind、connect4/6、recv4/6 等）。
4. **SocketBindAllow=/SocketBindDeny=**（resource-control.xml L888）：cgroup-inet/bind 钩子 BPF，按"any/ipv4/ipv6 + port(-range)"限制服务可 bind 端口——网络面沙箱。
5. **RestrictNetworkInterfaces=**（L992）：cgroup-bpf（bind-iface.bpf.c / restrict-ifaces.bpf.c）限制服务可见/可用接口（配合 BPF link 的 netns/ifindex 绑定）；同族还有 restrict-fs(userns-restrict) 等非网络项。
6. firewall 的 BPF 后端（BPFFirewall=）历史上尝试过，当前主线主要走 nftables/iptables（TODO 无复活迹象）——此为"曾是交汇点"的诚实记录。

**趋势判读**：systemd 对 BPF 的用法从"资源隔离副产品"（cgroup filter）走向"**网络管理器自身的可观测性/一致性工具**"（sysctl ring buffer 监控）。写网络栈相关的 eBPF 学习材料时，sysctl-monitor 是 2026 年版 BPF 应用面的活样本。

---

## 8. 官方 TODO 里的网络欠账精选（TODO.md grep 实证，行号为 263~devel 时点）

**协议库层**：
- dhcp6（L889-895）：IA_TA 临时地址、RECONFIGURE（RFC 8415 5.3/15.11/22.20）、DHCPv6 authentication、Confirm 消息价值评估、租约跨重启持久化（"store them in client->ia_na"）、RouteTable= 未接。
- dhcp（L903）：Maximum Message Size 上限探索。
- sd-lldp（L2339）：读 802.3 max-frame-size TLV 检测 jumbo。
- sd-resolve refcounting "borked"（L2118，官方原话）。

**networkd 层**（L1835-1853 集中）：
- routerless DHCP lease（无网关租约）处理、非以太网设备支持完善；
- carrier 丢失后 DHCP 附带数据（NTP/DNS）未即时撤除——设计债；
- DHCP option 15/12/81/123/144（geolocation）/252（WPAD/PAC）尚未暴露到 API；
- [Match] Name= 不支持重复与 `foo*|bar*` 通配组合；
- uplink 变化时 DHCP server 应发 FORCERENEW；
- per-interface 默认路由 metric（静态与 DHCP 分离）；
- macsec 密钥改走 credential（抄 wireguard 现成逻辑，L793-794）；
- state 序列化单测缺失（L983）；
- DEVTYPE 烂值修正（L1254）；
- resolved-hook：把 DHCP server 发出去的租约 IP 反向注册成主机名（L1824-1830）。

**resolved 层**（L2182-2195）：
- mDNS/DNS-SD **服务注册**（浏览已有）、socket unit 直发 DNS-SD 注册、avahi 兼容层；
- per-interface 附加 LLMNR 名（容器场景统一 "host" 名）；
- 单次查询强制 DNSSEC（全局关也可单查开）；
- 消费 DHCP DNR 信息（NDISCS 侧已收 ndisc_dnr，端到端打通未完）；
- 应答回 TTL（wireguard 定期重解析想用 TTL 做节流提示）；
- **IPv6 stub**：占一个固定 ULA（fd00:5353::/64 型）让 .53 stub 也能被 IPv6-only 客户端用——当前 stub 仅 127.0.0.53/54 IPv4；
- /etc/hosts 经 credential 增补（L2073）；
- nspawn：可选 nftables 把容器 53 端口转到 127.0.0.54（L1906）。

**架构级**：networkd/nspawn 联动按需建 netdev（bus 接口就绪后，L1869-1871）；PCP 客户端库给 wireguard 打 NAT 洞（sd-pcp-client 或直接用 libjuice，L197-198）；EFI 侧网络启动（DHCP/HTTP boot 二进制，L2728）；lldp 邻居做 resource-monitor 后端（L192）；"networking provider API"仿 StorageProvider（L2637-2639）。

---

## 9. 学习者路径（按依赖顺序，全部本仓可自足）

1. **入门（半天）**：man/systemd.network.xml 的示例节 + 顶层 network/ 预置 .network（80-container-ve.network 最短可读）；docs/NETWORK_ONLINE.md 弄清三个 target 的语义边界。
2. **状态机（1 天）**：networkd-link.h 全读（枚举+结构体=networkd 的世界观）→ networkd-link.c 只读 link_configure()（L1289 起 130 行）与 link_check_ready()（L636 起）→ networkd-util.h 的 NetworkConfigState 宏族（理解"配置完成"如何被判定）。
3. **事件骨架（1 天）**：networkd.c（130 行全读）→ networkd-manager.c 的 manager_connect_rtnl/manager_setup_device_monitor/manager_listen_fds 三函数——sd-event+sd-netlink 组合的标准范式。
4. **协议库（2-3 天）**：sd-dhcp-client.c 状态机（对照 RFC2131 读 dhcp-protocol.h 枚举）→ sd-ndisc.c（ND 最小实现）→ sd-ipv4acd.c（ACD，200ms 默认超时这类工程参数）。
5. **resolved（2 天）**：resolved-manager.c manager_new + manager_dns_stub_start（resolved-dns-stub.c L1388）→ resolved-dns-transaction.h 的 18 态枚举 → resolved-dns-cache.c 的 hit/miss 路径；用 resolvectl query --json 配合 debug 日志做黑盒观察。
6. **进阶专题**：BPF sysctl monitor（src/bpf/sysctl-monitor.bpf.c 60 行 + networkd-sysctl.c 消费端，一晚）；netdev 任选 wireguard.c（密钥/peer 管理）或 vxlan.c 读 vtable 模式；tc/ 目录读 htb.c。
7. **验证能力**：test/integration-tests/TEST-85-NETWORK/（系统级）+ src/network/test-network.c（单元级）双样例可学测试写法。

---

## 10. AI agent 用法（本地路径与 grep 关键词）

- 仓根：`/usr-data/data2/kylin/network/systemd`（git 只读，勿改）；版本锚：263~devel @ 3e38798c35（2026-11-06）。
- **快速定位表**：
  - "某个 .network 配置键跑到哪段代码"：`grep -n 'IPv6AcceptRA.UseDNS' /usr-data/data2/kylin/network/systemd/src/network/networkd-network-gperf.gperf` → 拿到解析函数名与 Network 结构体 offset → grep 该函数名找语义。
  - "netdev Kind=xyz 支持哪些键"：`src/network/netdev/netdev-gperf.gperf`（293 行，全节名如 `VXLAN`/`WireGuard`）+ 对应 `src/network/netdev/<kind>.c`。
  - "networkd 什么时候认为链路配置完"：`networkd-link.c` 的 `link_check_ready`（L636）+ Link 结构的 `*_configured` 位与 `*_messages` 计数器。
  - "某 DNS 行为（stub/环回/缓存）"：`grep -rn 'STUB_LOOP\|INADDR_DNS_STUB\|DNS_CACHE_MODE' src/resolve/`。
  - "协议选项是否实现"（如 DHCP option 82 / DHCPv6 IA_TA）：先 grep 协议库 `src/libsystemd-network/`，再查 TODO.md 对应小节（"没做"在 TODO 有官方记录，勿臆造）。
  - "BPF 相关"：`src/bpf/*.bpf.c` 全集 + `grep -rn 'dlopen_bpf\|sym_bpf' src/` 找消费端。
- **man 源即文档**：man/systemd.network.xml、systemd.netdev.xml、systemd.link.xml、networkd.conf.xml、resolved.conf.xml、networkctl.xml、systemd-networkd-wait-online.service.xml——XML 里的 `<variablelist>` 是配置键的权威语义（比网页新一个 commit）。
- 高价值小文件（上下文预算有限时优先喂）：networkd-link.h（231 行，Link 全字段）、network-util.h（118 行，状态枚举）、netdev.h（Kind 枚举段）、dhcp-protocol.h/dhcp6-protocol.h（状态机枚举）、resolve-util.h（stub 地址+CacheMode）、resolved-dns-transaction.h（18 态）。
- 陷阱提示：①`src/basic/` 与 `src/fundamental/` 有同名头（如 socket-util），import 时注意层级；②`sd-*-client` API 的头文件在 `src/systemd/`（公共 API 面），实现在 `src/libsystemd-network/`；③test-*.c 与 fuzz-*.c 会带大量 mock，非生产路径；④仓内 CLAUDE.md/AGENTS.md 的 README IMPORTANT 行规则只约束改码 PR，本消化任务不适用。



---

---

---
