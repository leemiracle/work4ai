# explain-05 · src/network/networkd-link.c — Link 状态机：从 udev 就绪到 routable

## 一、角色定位

networkd-link.c（3320 行）实现 `Link`——单块网卡的完整生命周期状态机。每块接口一个 Link 对象（`link_new()`，networkd-link.c:2905，在 manager 收到 RTM_NEWLINK 时创建，按 ifindex 存入 links_by_index），它承载：内核状态镜像（flags/MTU/MAC/master/driver 的增量更新）、.network 匹配与配置下发编排、以及对外可见的三态视图（carrier/address/operational state）。networkd 的核心承诺——"配置是声明式的，内核事件只触发向期望状态收敛"——由本文件兑现：所有配置动作都注册成异步 Request（挂进 explain-04 的 request_queue），回调链完成后 `link_check_ready()` 判定收敛。八态 LinkState（networkd-link.h:14-23）：PENDING（等 udev）→ INITIALIZED → CONFIGURING → CONFIGURED，旁路 UNMANAGED/FAILED/LINGER（收到 RTM_DELLINK 后的待清理态）。

## 二、内部结构

入口防线在 udev：`link_check_initialized()`（networkd-link.c:1829）要求设备已被 udevd 处理完（device_is_processed，1845）且不在改名中（device_is_renaming，1854），否则保持 PENDING。就绪后 `link_initialized()`（networkd-link.c:1786）有个著名的同步技巧——先发一个 GETLINK，等应答回来时"排队的 NEWLINK 必然已处理完"（networkd-link.c:1821-1826 注释），保证配置基于最新内核状态。随后 `link_get_network()`（1425）做 .network 文件匹配（MatchMAC/Type/Driver/Path/Name），命中则进 `link_configure()`（1289）。Link 结构体的字段几乎与 networkctl status 输出一一对应：carrier_state、operstate、addresses/routes 集合、dhcp_client/dhcp6_client/ndisc/llldp 等引擎句柄、BoundTo/BoundBy 依赖 hashmap（networkd-link.c:970/1003 建，1048-1063 侧释放）。

## 三、外部连接

上游：manager_rtnl_process_link 把消息交给 `link_update()`（networkd-link.c:2840），它分派给一族 link_update_* 增量更新器——flags(2322)、master(2404)、driver(2442)、permanent_hardware_address(2488)、hardware_address(2510)、mtu(2593)、alternative_names(2657)、name(2702，改名会触发重新匹配 .network)。下游引擎全部懒启动：DHCPv4/DHCPv6 客户端、NDisc/RA、DHCP server、RADV、LLDP rx/tx（在 link_configure 中按需 request，networkd-link.c:1375-1409）。横向：resolved 通过 link_set_dns/link 的 DNS 设置取接口解析配置（networkd-link.c:3311）；BindsTo/BoundTo 语义在 905-948 的 handle 家族里实现主备联动；SR-IOV PF/VF 端口管理（1812）、stacked netdev（VLAN/MACVLAN 等堆叠，709）、modem（1415）都挂同一编排点。

## 四、数据流

`link_configure()`（networkd-link.c:1289-1423）是最有教学价值的编排函数，顺序即依赖：先清非托管遗留（1298）→ 建 BoundTo 链（1302）→ 流量控制 qdisc（1306）→ MTU（1310）→ **CAN 总线短路路径**（1314-1321，跳过 IP 栈直接激活）→ sysctl（1327）→ MAC/ipoib/flags/group/addrgen-mode（1331-1347）→ 主从关系（1351）→ 堆叠 netdev 与 bond/bridge/vlan（1355-1369）→ **link_request_to_activate**（1371，把接口 UP）→ IPv4LL/DHCPv4/DHCPv6/NDisc/DHCP 中继/DHCP 服务器/RADV/LLDP（1375-1409）→ 静态地址/路由/邻居/FDB（1411 link_request_static_configs）→ 有 carrier 则立即启动动态配置（1422）。

收敛判定在 `link_check_ready()`（networkd-link.c:636）：仅当处于 CONFIGURING、且 `link_get_configuring_reason_full` 找不出任何"还没就绪的理由"（静态地址未到位、等 DHCP 租约等）才切 CONFIGURED（660），debug 日志会精确说出卡在哪个地址/原因（652-657）。反向路径：carrier 丢失走 `link_carrier_lost`（2012，带 timer 去抖，1999 的 handler），恢复走 link_carrier_gained（1908）。对外视图由 `link_update_operstate()`（2122）合成：carrier state 由内核 operstate + 是否 enslave（2122-2142）、聚合口递归降级子口（2147-2152 DEGRADED_CARRIER），再与 address state 交叉出 operational state——代码内嵌那张 6×3 映射表注释（2157-2164）就是 networkctl 五态（off/no-carrier/dormant/degraded/routable）的权威定义。失败统一进 `link_enter_failed`（457）；重载配置走 link_reconfigure_impl（1530）差量撤销（link_drop_requests，1105，按 NetworkConfigSource 区分静态/动态/外来配置的归属权——只删自己发的）。

## 五、设计决策

1. **udev 作为准入闸门**：PENDING 态本质是"等 udev 把驱动数据库/改名 settles"，避免对半初始化网卡下发配置（networkd-link.c:1829 的三个检查）；GETLINK 应答当屏障（1821-1826）是零成本的事件序同步，比记序号优雅。
2. **全部异步 Request 化**：没有一处同步 ioctl 等待；下发即入队、应答即回调，carrier 抖动时请求自然合并去重——网络瞬断不会产生配置风暴。
3. **配置来源三分类**（static/dynamic/foreign）：link_drop_requests（1105）按 source 选择性回收，使 daemon-reload 与 DHCP 租约变更互不误伤，也支持 KeepConfiguration 语义。
4. **合成视图而非镜像内核**：operstate 是 networkd 自己计算的（2122 的矩阵），聚合链路状态对 bond/team 的降级传播（DEGRADED_CARRIER）在内核里没有对应物，是 systemd 的增值语义。
5. **CAN 短路**（1314-1321）：非 IP 设备跳过整套 IP 配置管线，体现编排器对异质链路的开放性。

## 六、新人提示

调试单网卡问题按状态机顺序问三句：卡在 PENDING？（查 udev：`udevadm info --wait` / journal udevd）；CONFIGURING 不收敛？（debug 日志 link_check_ready 每轮打印"configuring reason"，networkd-link.c:651-657，直接指认卡住的静态地址或引擎）；operstate 与预期不符？（对照 2157-2164 的矩阵表手算一遍 carrier×address）。改代码时记住铁律：新配置项必须做成 Request 进队列（参考 networkd-route.c 的模式）并在 link_configure 的正确层级插入——同步 rtnl 调用会破坏整个事件模型。网卡改名（2702）路径容易踩坑：旧名的 Link 要迁移配置与请求队列。Kylin 工作区提示：麒麟自研网卡驱动若 udev 属性迟到，表现为接口长期 pending，可对照 device_is_processed 的两处检查定位是 udev 还是驱动 database 未 settle；国产聚合驱动的 carrier 上报差异会被 DEGRADED_CARRIER 逻辑放大，联调时优先核对 slaves 集合的 carrier_state。
