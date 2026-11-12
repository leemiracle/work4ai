# explain-07 · KNI 内核共存通道：lib/ff_dpdk_kni.c（virtio_user 旁路）

## 角色定位

F-Stack 独占网卡后，内核栈就瞎了——SSH 管理、ARP 应答、OSPF/BGP 路由协议这些"控制面流量"仍需要走 Linux 内核。ff_dpdk_kni.c（654 行）就是这条旁路：把 F-Stack 不要的包送进内核、把内核发出的包送回物理网卡。名字虽叫 KNI，实现却**不是** DPDK 传统的 KNI 内核模块，而是 virtio_user 异常路径（`:524-527` 注释直接指向 DPDK 官方 howto "virtio_user_as_exception_path"）：hotplug 一个 `path=/dev/vhost-net,iface=veth%d` 的 vdev（`:532-543`），内核侧看到的就是一张普通 veth 网卡，无需加载 kmod。配合 ff_dpdk_if.c 的 protocol_filter 分类与 knictl_action 三模式，构成"数据面归 F-Stack、控制面归内核"的双栈共存。

## 内部结构

文件四块：① 归属判定——ff_kni_is_owner_thread（`:94`，thread_mode 看 lcore、进程模式看 PRIMARY）与 ff_kni_is_runtime_owner（`:102`，primary_slim+graceful_reload 下两代同 proc_id，必须再对 ff_reload_kni_owner_match 的世代目录属主字（`:120-121`），注释强调"两进程绝不能同时 rte_eth_tx_burst 同一 TX 队列"）；② 协议分类器——ff_kni_proto_filter（`:433`）→protocol_filter_ip（`:360`）：IPv4/IPv6 头长解析（v6 扩展头递归 get_ipv6_hdr_len `:309-342`，覆盖 HOPOPTS/ROUTING/FRAGMENT/AH 等）、OSPF 协议号 89 直接 FILTER_OSPF（`:400`）、TCP/UDP 查端口位图（`:269-291`）、IPIP/IPV6 隧道递归解内层（`:420-424`）、NDP 按 ICMP6 类型区间判（`:344-357`）；③ 位图限速——tcp/udp_port_bitmap 各 8192 字节即 65536 个端口位（`:472-485`），kni_set_bitmap 解析 "80,443,1000-2000" 范围语法（`:156-180`；注意 set_bitmap `:142` 先 htons 再置位，因为分类器读的是报文里的网络序端口）；④ 转发引擎——kni_rp（去内核）与 kni_inject_rp（primary 注入）两张环（`:90-91`），创建用 RING_F_SC_DEQ、非属主进程只 lookup 且 panic 报错带修复提示（`:559-562`："primary 的 config 是否开了 [kni] enable=1"）。

## 外部连接

上游：ff_dpdk_if.c 的收包路径按分类结果调 ff_kni_enqueue（ff_dpdk_if.c:2861/2871/2879），knictl_action（get_kni_action ff_dpdk_if.c:1046）支持 alltokni/alltoff/default 三档运行时切换（handle_knictl_msg `:3037` 消费控制消息）；ARP/NDP 包走"深拷贝双投"——一份进 KNI 一份进 F-Stack 栈（pktmbuf_deep_clone，ff_dpdk_if.c:2858）。驱动：main_loop 每圈过 ff_kni_process，但有属主线程门（ff_dpdk_if.c:4009：virtio vdev 归 primary 创建者，别的进程摸不合法）；primary_slim 模式下 owner secondary 额外跑 ff_kni_inject_process（ff_dpdk_if.c:4017-4026，条件三连：primary_slim + 非 no_hw + 非 primary）。配置面：config.ini [kni] 节的 tcp_ports/udp_ports 喂位图、method=accept|reject 决定未匹配端口的缺省去向、三个 ratelimit 键（console/general/kernel）经 ff_kni_enqueue 与 kni_process_tx 执行。

## 数据流

去内核向：收包分类 FILTER_KNI（端口位图命中）或 FILTER_OSPF/ARP/NDP→ff_kni_enqueue（`:621`）：先按 filter>=FILTER_ARP 分成 console（ARP/NDP/OSPF 这类）与 general 两类限速（各自累加、超限 goto error 丢包计数 `:624-637`）→入 kni_rp 环。属主线程每圈 kni_process_tx（`:183`）：dequeue burst→kernel_packets 第三类限速（`:194-203`，注释承认"可能多发几个，无所谓"）→rte_eth_tx_burst 到 virtio 端口（kni_stat[port_id]->port_id，其值=port_idx+nb_dev_ports `:545`，与 ff_dpdk_if.c:1159-1161 的内核 vdev 端口编号规则对齐）→vhost-net→内核 veth。回物理口向：kni_process_rx（`:219`）从 virtio 口 rx_burst 收内核发出的包→普通进程直接 rte_eth_tx_burst 物理口（`:245`）；primary_slim 的 primary 则改投 kni_inject_rp（`:228-243`，注释点明目的：避免 primary 与 owner secondary 同抢物理口 TX0 的竞态），由 runtime owner 的 ff_kni_inject_process（`:600`）代发。

## 设计决策

① **virtio_user 替代 KNI 设备**：不动内核模块、热插拔即建即毁，代价是多一跳 vhost-net——对控制面流量这点开销无关紧要，正确取舍。② 三层属主判定层层收紧（线程→进程→世代目录）是为了热升级安全：`kni_needs_stats :130-136` 的注释解释了为什么"未来可能当属主的进程"也要预建 stats 表——slim 配置下 owner_proc_id 的属主权可以在 ff_kni_init 之后、世代激活之时才生效，预分配不等于授权。③ 位图而非哈希表做端口过滤：8192 字节全量位图一次访存命中判断，控制面端口集合小而静态，简单方案完胜；范围语法解析是启动期一次性的。④ 限速三类分账（console/general/kernel）+ main_loop 每秒整点清零（ff_dpdk_if.c:3816-3842）——防止内核侧被打爆反噬 F-Stack 主循环；gerneal 的拼写错误（general→gerneal，`:632`）是历史遗留，改字段名要动 struct kni_ratelimit 三处。

## 新人提示

排查"KNI 不通"按三步：非属主进程的 ring lookup panic 信息直接指路 primary config（`:560-562`）；veth%d 接口在内核侧看到但没流量，先查 protocol_filter 的端口位图有没有配上你的端口（config [kni] tcp_ports）；限速误伤看日志里 kni ratelimit 行（每秒汇总 console/general/kernel 三计数）。改 filter 返回值注意 FilterReturn 枚举有序（FILTER_UNKNOWN<AR P<NDP<...<OSPF），ff_kni_enqueue 用 `filter >= FILTER_ARP` 二分 console/general，插新枚举值会改变分类。热升级场景下 KNI 属主随 active 世代翻（ff_reload_master_complete 同步 kni_owner_gen），测试用 tests/unit/test_ff_dpdk_kni.c + integration 的 KNI 用例双保险。
