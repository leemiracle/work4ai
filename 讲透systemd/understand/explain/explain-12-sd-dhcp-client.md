# explain-12 · src/libsystemd-network/sd-dhcp-client.c — DHCPv4 客户端：RFC 2131 的状态机教科书

## 一、角色定位

sd-dhcp-client.c（1447 行）实现 systemd 自带的 DHCPv4 客户端协议库（libsystemd-network，供 systemd-networkd 进程内调用，不是独立守护进程）。它把 RFC 2131 的九态客户端状态机（dhcp-protocol.h:105-117：STOPPED/INIT/SELECTING/INIT_REBOOT/REBOOTING/REQUESTING/BOUND/RENEWING/REBINDING）完整落成事件驱动实现：九态迁移、指数退避重发、T1/T2/expire 三级租约定时、Rapid Commit、客户端标识（IAID/DUID 五种）、RFC 7844 匿名模式。与独立 dhclient/dhcpcnd 的本质差异：它是**嵌入宿主事件循环的库**——networkd 每 link 一个 client 实例，所有超时与收包都是 sd-event 源，没有线程没有 fork。

## 二、内部结构

前半是配置面（典型的 builder 模式 setter 群）：sd_dhcp_client_new（1417）→ attach_event（1344）→ set_ifindex（131）/set_mac（165）/set_client_id（236）/set_iaid_duid_*（282-377，LLT/LL/EN/UUID/raw 五种 DUID）/set_rapid_commit（377）/set_hostname（384）等 → start（1225）。运行期骨架三类成员：状态与回调（`client_set_state`：568 带日志迁移，`client_notify`：613 把 SD_DHCP_CLIENT_EVENT_* 事件抛给 networkd 的回调）；事件源（timeout_resend/timeout_t1/timeout_t2/timeout_expire 四个 CLOCK_BOOTTIME 定时器 + 收包 io 源 udp/raw 双份：1200/1204——raw socket 用于自定义 client port 与 BPF 过滤）；收发（dhcp_client_send_message 组 DISCOVER/REQUEST/DECLINE/RELEASE，client_handle_message:1106 按报文类型推进状态）。`DHCP_CLIENT_DONT_DESTROY`（695）是库内惯用的引用防拆宏——回调链里 client 可能被 stop/free。

## 三、外部连接

上游唯一消费者是 networkd（networkd-dhcp4.c 调 set_* 与回调，把租约交给地址/路由/NTP/DNS 分发）；sd_dhcp_lease（dhcp-lease.c）承载结果数据。下层依赖 sd-event 与系统 socket：默认 UDP 68 端口或 raw 模式（networkd 选 raw 以支持 ListenPort 与 udev 设备绑定——attach_device:1379 把 sd_device 挂进 BPF 过滤）。协议兄弟件：sd-dhcp6-client/sd-dhcp-server/ndisc 共享 dhcp-option 的 TLV 设施（set_extra_options:496 允许 networkd 注入任意 Vendor/User class 选项）。bootp 兼容开关（551）与 fallback lease lifetime（540）是为老旧/非常规服务器准备的逃生门。

## 四、数据流

获取租约主链：INIT 下 start → 首个 resend 定时器触发 `client_timeout_resend`（689）——INIT 立即切 SELECTING（716-718 fallthrough）——按指数退避（client_compute_request_timeout:674）连发 DISCOVER，超过 max_discover_attempts 报 ETIMEDOUT（721-724）；途中连续失败还会提前广播 TRANSIENT_FAILURE 事件让 networkd 决定降级（771-772）。收到 OFFER → client_enter_requesting（922）发 REQUEST → ACK → `client_enter_bound`（1063）接管租约并装三级定时器。

租约维护链是 RFC 时间学的精确实现（`client_set_lease_timeouts`:972）：无限租约不装定时器（983-988）；T1（renew，单播原服务器）与 T2（rebind，广播任意服务器）各减 RFC2131 §4.4.5 允许的随机 fuzz 防同网段时钟同步风暴（1005-1013，并保证 t2≥t1）；三个定时器按 expire→T2→T1 逆序装，已过期的时间点跳过（1025/1041）。T1 到 → RENEWING 重发 REQUEST（782-784 共用 resend 路径，退避序列基于距 t2 的剩余时间 709）；T2 到 → REBINDING 广播（713 基于 expire）；全失败 → timeout_expire（880）回 INIT 重来。

收包路径：io 源回调 client_receive_message_udp/raw（1200/1204）→ receive_message（1144，raw 模式要自行剥 IP 头并校验）→ handle_message（1106）按 xid/类型分派；DECLINE（1260，地址冲突时）与 RELEASE（1275，`sd_dhcp_client_stop` 里按 SendRelease= 决定是否发，1287）是两个显式出口。REQUESTING 重试到 MAX_REQUEST_ATTEMPTS 后按 RFC 2131 §3.1.5 回 INIT 重启（795-800 注释直引条文）。

## 五、设计决策

1. **纯事件驱动无轮询**：四个定时器 + io 源就是全部调度，挂进宿主 sd-event；networkd 因此能几百个 link 各自 DHCP 而零线程开销——库形态本身就是决策。
2. **协议条文进注释**：T1/T2 fuzz（1005）、REBOOTING 加速重用 REQUEST 退避再除四（735-742）、REQUEST 循环重启（796-798）都在代码旁标注 RFC 节号，读代码等于对照读协议。
3. **失败分级通知**：TRANSIENT_FAILURE（771）与最终 ETIMEDOUT 分开上报，让上层（networkd）能先试 IPv4LL/静态回退而不是干等。
4. **双收包通道**（1200/1204）：UDP socket 简单通用，raw socket 换来自定义端口、选项注入与 BPF 预过滤——把策略留给集成方。
5. **防御性回调**：DHCP_CLIENT_DONT_DESTROY + client_stop 统一清理（644），任何路径错误都收敛到带 error 码的事件，不向事件循环泄漏负返回值（804-809 注释）。

## 六、新人提示

调试 DHCP 最快路径是 debug 日志：client_set_state（568）与三个 timer 装配日志（1028/1044/1057 的 "lease expires in/T2 expires in/T1 expires in"）拼出完整时间线，配合 tcpdump port 67 or 68 对拍。常见坑：租约"莫名"丢失先看 expire 定时器日志与系统时钟（全部定时器用 CLOCK_BOOTTIME，睡眠唤醒不误触发）；服务器不理 REQUEST 就核对 client id/DUID 一致性（set_client_id:236 覆盖默认值后网络内的旧租约会失配）。改协议行为务必带上 RFC 节号注释——本文件的注释密度就是维护契约。Kylin 工作区提示：麒麟环境下若接国产 DHCP 服务器，非标选项（如私有大类 Vendor class）经 set_extra_options/vendor_options（496/503）注入即可，不必改协议库；而服务器不支持 Rapid Commit 时记得确认 networkd 配置没开（377 的开关直通报文构造）。此库与 sd-dhcp-server（同目录）构成最小可用 DHCP 全栈，是麒麟网络功能定制的低风险切入点——协议边界清晰，回归用例（test-dhcp-client.c）齐备。
