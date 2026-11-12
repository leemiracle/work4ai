# explain-08 · 虚拟以太网桥：lib/ff_veth.c（ifnet 伪造与 ZC 零拷贝 API）

## 角色定位

FreeBSD 协议栈离不开 ifnet——网卡接口抽象。ff_veth.c（1289 行）在用户态伪造出这个抽象：给每个 DPDK 端口造一张"虚拟以太网卡"（struct ff_veth_softc `:72`），注册 init/start/ioctl/transmit/qflush 五个回调（`:970-978`），把 MAC/IP/网关/VIP 全配进去，让 freebsd/ 树的 ether_input/ip_input 无差别地当真网卡用。收方向它是 rte_mbuf→BSD mbuf 的翻译官（ext cluster 挂钩零拷贝），发方向它是 ifp→ff_dpdk_if_send 的转接头（ff_veth_transmit `:562`）。另外它还是本分支零拷贝扩展（FSTACK_ZC_SEND/ZC_RECV）的家：ff_zc_mbuf_* 五个 API 让应用直接在 BSD mbuf 链上写数据、免一次 copy。

## 内部结构

三段式：① softc 与配置（ff_veth_config `:98`：config.ini 的 addr/netmask/broadcast/gateway/inet_pton 进 softc，VIP 数组、INET6 的 prefix 默认 64；vlan 版 `:155`）；② 接口装配（ff_veth_setup_interface `:961`：if_alloc(IFT_ETHER)、ether_ifattach 挂 MAC、按 hw_features 逐项开 IFCAP_RXCSUM/LRO/TSO 能力位——TSO 还设 maxsegcount=35/maxsegsize=2048 `:998-999`、ff_dpdk_register_if 反向登记 host_ctx `:1004`；随后 setaddr/set_gateway/setvaddr 经 in_control/rt ioctl 真实配栈，VLAN 模式走 if_clone_create 建 "vethX.vid" 子接口 `:1084-1091`）；③ mbuf 桥 API：ff_mbuf_gethdr（`:466`）/ff_mbuf_get（`:490`）用 m_extadd 把 rte_mbuf 数据区挂成 ext cluster（free 回调=ff_mbuf_ext_free `:318`，EXT_DISPOSABLE），ff_rte_frm_extcl（`:1263`）反向从 mbuf 追溯回 rte_mbuf；ff_mbuf_tx_offload（`:285`）把 CSUM_* 标志翻成协议无关的 ff_tx_offload；ZC 五件套 ff_zc_mbuf_get/write/read/segment/free（`:324-463`）；LRO 三件套（`:513-548`，收包侧软件聚合，ff_lro_flush 用 tcp_lro_flush_inactive）。

## 外部连接

上游 ff_dpdk_if.c：ff_veth_input（ff_dpdk_if.c:2303）构链后调 ff_veth_process_packet（`:551`：设 rcvif 后 if_input 进栈）；ff_veth_attach（`:1153`）在 ff_dpdk_if_up 与 worker 主循环里被调（ff_dpdk_if.c:3768），返回 host_ctx 存进 veth_ctx[lcore][port]；ff_veth_softc_to_hostc（`:1207`）供 ff_rss_check 从 softc 找回上下文。下游 ff_dpdk_if.c：栈要发包时 if_start→ff_veth_transmit→ff_dpdk_if_send（ff_dpdk_if.c:3311）完成 BSD→rte 拷贝（或 FF_USE_PAGE_ARRAY 模式下 ff_if_send_onepkt 页数组直发，ff_memory.h:187）。ZC 出口在 ff_syscall_wrapper.c：ff_zc_send（`:1323`）要求链头 M_PKTHDR 且 pkthdr.len 由 write 维护好，直接 kern_zc_sendit；ff_zc_recv（`:1360`）以非 NULL mbuf 出参调 kern_zc_recvit，socket buffer 的 mbuf 链不拷贝直接交还应用（注释 `:1348`：uio 只剩 resid 被读）。

## 数据流

收向（零拷贝只到栈口）：rte_mbuf 到达→ff_mbuf_gethdr 给首段 m_gethdr+m_extadd(data,len)——**不拷贝**，ext_arg1 存 rte_mbuf 指针；多段链逐个 ff_mbuf_get 串 m_next；VLAN 硬剥则 ff_mbuf_set_vlan_info 写 ether_vtag+M_VLANTAG（`:1276`）；带时间戳则 M_TSTMP_HPREC（`:1284`）；进 LRO 或直接 ff_veth_process_packet→if_input。**mbuf 的生与死**：栈消费完调 m_freem→ext 回调 ff_mbuf_ext_free→ff_dpdk_pktmbuf_free 释放底层 rte_mbuf（`:319-322`）——BSD mbuf 壳与 DPDK 缓冲区生命周期由此闭合。发向（两档）：普通档 ff_veth_transmit→ff_dpdk_if_send 逐段 copy 进 rte mbuf（见 explain-01）；ZC 档应用先 ff_zc_mbuf_get 预留 len、ff_zc_mbuf_write 顺链填数据（`:347-386`，M_TRAILINGSPACE 逐段填、pkthdr.len 只在链头累加——`:377-379` 注释引 mbuf(9)：sosend 在 uio==NULL 时拿 top->m_pkthdr.len 当 resid）、ff_zc_send 整链交栈，省掉 send buffer 的一次全量拷贝。

## 设计决策

① **ext cluster 零拷贝收包是全仓最重要的性能决策之一**：收方向"每包一次 memcpy"被彻底消灭，代价是引入跨体系生命周期耦合——freebsd/ 代码绝不能对 m_ext 外部缓冲区做越界写，EXT_DISPOSABLE 标记即此契约；FF_USE_PAGE_ARRAY 再进一步让发送也免拷贝（bsd_m_table 伴随表记录 BSD 侧 mbuf，send_burst 后 ff_enq_tx_bsdmbuf 回收，ff_dpdk_if.c:3272）。② IPv6 关 DAD（`:1045-1048`）：用户态没有 L2 对端应答 NS，DAD 会让地址永久 IN6_IFF_TENTATIVE、FreeBSD 15 ip6_input 静默丢单播——一条注释省掉一整类"IPv6 不通"工单。③ VLAN 用 if_clone_create 走正统 vlan(4) 克隆路径而非自造结构——每 VLAN 一个 fib（`fib_num=vlan_idx :1106`），多租户路由域借 FreeBSD 原生机制。④ ff_mbuf_tx_offload 把 CSUM_TCP 与 CSUM_TCP_IPV6 折叠成一个 tcp_csum（`:293-297`）：BSD 标志按协议分位，DPDK offload 协议无关——翻译层的"有损压缩"必须两侧都有人兜底（ff_dpdk_if.c:3415 再按 iph->version 重新展开）。

## 新人提示

理解本文件的钥匙是"两个所有权"：数据区归 rte_mbuf（ext_arg1 持有），mbuf 壳归 FreeBSD 栈——任何手写 mbuf 操作都要先问"free 时谁来放谁"。调 ZC 先看 example/main_zc.c 的用法节奏（get→write→send / recv→read→free），ff_zc_mbuf_write 越界返回 -1 且不再推进游标，别忽略返回值。ifname 冲突（ff_IF_NAME 模板 vs cfg->ifname）在多端口时常见；VLAN 场景记得主接口不配 IP（`:1020` 注释：vlan_flag 下只建 iface）。TSO 能力位是"宣称"，真正做分段的是 ff_dpdk_if.c 的 offload 翻译（`:3442-3469`），两侧参数（segsz 35/2048）必须一起改。tests/unit/test_ff_zc_send.c 是 ZC 链语义的回归锚，动 ff_zc_mbuf_* 先跑它。
