# explain-01 · 数据面核心 lib/ff_dpdk_if.c：main_loop / 收包 / 发包 / RSS 四主线

## 角色定位

ff_dpdk_if.c 是全仓最大的单文件（5420 行），也是 F-Stack 的心脏：它把 DPDK 的裸包收发、FreeBSD 协议栈的注入点、用户回调 loop()、以及 v2.0 热升级的"硬件属主"裁决全部装进一个轮询循环。应用侧调用的 ff_dpdk_run/ff_dpdk_if_send、ff_regist_packet_dispatcher、ff_rss_check 都在这里落地。可以说：ff_veth 是桥，ff_dpdk_if.c 是发动机——别的文件提供机制，这个文件决定每微秒发生什么。

## 内部结构

文件大致分四段：初始化段（ff_dpdk_init `lib/ff_dpdk_if.c:2061` 起：rte_eal_init→init_mem_pool→init_dispatch_ring→init_msg_ring→init_kni→init_port_start→init_clock，顺序即依赖序）；包处理段（ff_dpdk_process_packets `:2725`、ff_veth_input `:2303`、protocol_filter `:2358`）；发送段（ff_dpdk_if_send `:3311`→send_single_packet `:3290`→send_burst `:3223`）；RSS 段（toeplitz_hash `:4200`、ff_rss_check `:4530`、ff_rss_adjust_sport `:4843`）。全局态集中在文件头部：`dispatch_ring[RTE_MAX_ETHPORTS]`（`:203` 附近）按 port×queue 二级分配软转发环，`veth_ctx[lcore][port]` 保存每线程每端口的 ifnet 上下文。main_loop（`:3725-4132`）是唯一的运行时骨架，约 400 行把所有子系统按固定顺序各喂一口。

## 外部连接

向上：ff_veth_input 把 rte_mbuf 转成 BSD mbuf 后调 ff_veth_process_packet（`:2354`）进入 FreeBSD 栈——这是与 ff_veth.c 的交接点；lr->loop（`:4044`）回调应用层。向旁路：FF_KNI 打开时 ARP/NDP 包 deep clone 后 ff_kni_enqueue（`:2861`），由 ff_dpdk_kni.c 送内核；knictl_action 三模式（`:2868-2885`：ALL_TO_KNI/ALL_TO_FF/DEFAULT）支持运行时切换。向控制面：process_msg_ring（`:3986`）消费 ff_msg 环，分发到 handle_sysctl/ioctl/route/top/ngctl/knictl/reload 十余个 handler（`:2910-3112`）。向热升级：ff_reload_heartbeat_tick（`:3796`）、ff_reload_handover_ack（`:3894`）、ff_drain_ring_rx_dequeue（`:3979`）/tx_drain（`:3996`）——main_loop 同时是 reload 状态机的驱动源。向时钟：ff_hardclock（`:3810`）驱动 ff_kern_timeout.c 的 tick-wheel。

## 数据流

收包：rte_eth_rx_burst 批量取包（`:3942`）→ prefetch 流水（`:3953-3964`）→ 逐包 ff_dpdk_process_packets：先 pcap 抓包（`:2738`），再 mbuf_low_watermark 低水位 SYN 丢包保护（`:2745-2752`），然后可选 packet_dispatcher 回调（`:2759`）——应用可返回 FF_DISPATCH_RESPONSE 直接回包（`:2780`）、FF_DISPATCH_PEER 转交对端世代（`:2790`）、或改写目标 queue；ret!=queue_id 时经 dispatch_ring 软转发给兄弟 lcore（`:2817`）。此后 protocol_filter 分类，ARP/NDP 走 ff_fanout_neighbour 多播扇出（`:2848`），其余按 KNI/FF 分流，最终 ff_veth_input：校验和坏包丢弃（`:2307`）→ ff_mbuf_gethdr 包装（`:2316`）→ 分段链逐个 ff_mbuf_get（`:2339`）→ 可选 LRO（`:2350`）→ 进协议栈。发包：ff_dpdk_if_send 把 BSD mbuf 拷贝进 rte_mbuf 段链（`:3357-3390`），按 hw_features 填 IP/L4 校验和与 TSO offload 标志（`:3397-3476`），send_single_packet 入 tx_mbufs 暂存表，攒满 MAX_PKT_BURST 或 main_loop 的 drain_tsc 到期（`:3901`，由 pkt_tx_delay 配置，默认 BURST_TX_DRAIN_US）才 send_burst 真正 rte_eth_tx_burst（`:3265`）。

## 设计决策

四个值得咀嚼的决策：① 软硬两级 RSS 分流——硬件 RETA 按 (hash & (reta_size-1)) % nb_queues 轮询填表（set_rss_table `:1117`），但多进程场景 lcore 与 queue 不一定对齐，于是用 dispatch_ring 在进程间二次转发，正确性优先于一跳延迟。② ff_rss_adjust_sport 用 rte_thash_adjust_tuple 反解本地端口使 SYN-ACK 回包落在本地队列（`:4843`）——tuple 故意按"回包方向"排列（`:4925-4938` 注释），且修复了 sport=0 种子导致解出保留端口的 bug（`:4882-4888` 注释）；mlx5 上 RSS key 必须在 dev_configure 前发布，因为 rss_hash_update 只改软件副本不动 TIR（`:4601-4614` 注释）。③ 发送侧一切路径都先汇聚到 send_burst 一个出口，`:3248` 的 no_hw 守卫用"到达即丢+告警"兜住五条可能漏改的暂存路径——热升级停车期间绝不能碰硬件 TX 队列。④ main_loop 里 graceful_reload=1 时 hardclock 改走进程私有 TSC 节流（`:3803-3814`），避免与 rte_timer 共享槽位在世代交接期产生双驱动。

## 新人提示

读这个文件先跑通一条最小路径：rx_burst→process_packets→veth_input，再回头看 dispatcher 与 KNI 分支，最后才碰 reload 相关注释（占全文件近三分之一，全是为"停车不让硬件"服务的）。注意 ff_top_status 的 usr/sys/idle 三段 TSC 记账（`:4114-4128`）是 ff_top 工具的数据源，改循环体时别破坏记账边界。调试 RSS 用 FF_RSS_DIAG 编译开关（`:4578`）可 dump 世代间 key 对比。坑：tx_mbufs 是 per-lcore per-port 状态，send_single_packet 攒包后若进程退出会泄漏——热升级路径靠 ff_divert_tx_mbuf 排空（`:3922`）。
