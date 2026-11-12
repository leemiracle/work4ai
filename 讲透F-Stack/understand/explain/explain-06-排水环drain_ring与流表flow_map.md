# explain-06 · 升级数据不丢两件套：lib/ff_drain_ring.c + lib/ff_flow_map.c

## 角色定位

热升级窗口期（explain-05 的 T3 阶段）新世代 G_new 独占硬件，旧世代 G_old 被停权（no_hw）但连接还活着——这两件套就是让 G_old"不死也不碰网卡"的管道与判官：ff_drain_ring.c（673 行）建每 (port,queue,世代) 一对的 rte_ring，把 G_old 该收的包从 G_new 转过去、把 G_old 要发的包送到 G_new 发出；ff_flow_map.c（478 行）是进程本地四元组流表，裁决"这个 SYN 属于新开的流（我收）还是老流（转给 G_old）"。没有它们，热升级窗口里的存量连接会瞬间断掉——graceful reload 的"graceful"二字一半押在这两个文件上（另一半在 ff_flow_peer 的 UDP 移交，同层邻居）。

## 内部结构

ff_drain_ring.c：静态二维表 drain_ring_rx/tx[RTE_MAX_ETHPORTS]（`:72-73`），扁平索引 `[queue*EPOCH_SLOT_MAX+slot]*GEN_MAX+gen`（`:57-59`）；环名两套格式——HUP 单 master 用 `drain_rx_p%u_q%u_g%d`（`:49`），USR2 跨 master 加 epoch slot 命名空间 `..._e%u_g%d`（`:53`），且用 typedef 编译期断言环名不超过 RTE_RING_NAMESIZE-1（`:63-68`）。入口四个：rx_enqueue（`:496`，gen=目的地世代）/tx_enqueue（`:539`，gen=来源世代——两端语义相反，`gen_mismatch_warn :108` 专门防"喂错边自环"的编码错误且只告警一次）/rx_dequeue（`:567`）/tx_drain（`:600`）。统计计数器本地累积、~1Hz flush 成增量进共享 drain 块（flush_stats `:635`）。ff_flow_map.c：开放寻址哈希表 struct ff_flow_slot{40字节 key+state+hash}（`:73-77`），默认 65536 槽（`:61`）、线性探测上限 16（`:63`）、满表最多翻倍 4 次（`:68`）；flow_hash 是 FNV 变体双链乘散列（`:102-121`，注释明确"可移植、无 ISA/DPDK 依赖、只混身份字节"）；revoke 的线性探测回填（`:195-209` 注释解释 hole 语义：把会断链的拉回来、home 在洞与现位之间的不动）。

## 外部连接

flow_map 的三边契约设计得很干净（ff_flow_map.h:29-47 注释）：生产者是 FreeBSD 栈内的 syncache 插入钩子（tcp_syncache.c:497）与主动 connect（in_pcb.c:836 的 in_pcb_flow_admit）；消费者是应用的 packet_dispatcher 回调——nginx 侧 ngx_ff_flow_map_dispatcher（ngx_ff_module.c:347 起）手解以太/VLAN/IP 头组 key，查表命中返回 queue_id（本地收），miss 返回 FF_DISPATCH_PEER；ff_api.h:267 定义该常量。头文件刻意不 include 任何东西（ff_flow_map.h:35-36："freebsd/ 编译单元不许拉 ff_api.h"），自带 extern "C"（`:44`）保 C++ 可用。drain_ring 的接线全在 ff_dpdk_if.c：FF_DISPATCH_PEER 分支调 ff_drain_ring_rx_enqueue（`:2800`）、no_hw 发送路径 ff_divert_tx_mbuf 调 tx_enqueue、被停权代主循环 rx_dequeue（`:3979`）收转来的包、硬件属主每圈 tx_drain（`:3996`）替对端发包；ff_reload.c 的 1Hz housekeeping 调 flush_stats 上报水位。

## 数据流

收向：G_new 收到包→dispatcher 查 flow_map（先做"纯 SYN 快判"：SYN 且无 ACK 必是新流，直接本地，ngx_ff_module.c:452 注释解释若不这样做 G_old 的 conns/syncache 会被持续喂新流、排水完成条件永不可满足）→miss 则 FF_DISPATCH_PEER→ff_dpdk_if.c:2799 检查窗口有效后 rx_enqueue 进 G_old 的 drain_rx 环（满则丢包计数，`drain_ring_full_warn :123` 每秒每方向至多一行，"TCP 重传会救回来"）→G_old 主循环的 no_hw 分支 rx_dequeue 取包→`pkts_from_ring=1` 调 ff_dpdk_process_packets（`:595`，该标志防止再 clone/再分发形成回声环）。发向：G_old 应用发包→ff_dpdk_if_send 见 no_hw→ff_divert_tx_mbuf→tx_enqueue 进自己世代的 drain_tx→G_new（硬件属主）主循环 tx_drain 取出直接 rte_eth_tx_burst（`:623`），发不完的 free 并计 tx_dropped。UDP 特例：无 SYN 无流表条目，靠 ff_flow_peer_classify 三分类（LEGACY/FWD 转发、LEARN 学入本地，ngx_ff_module.c:470-478）。

## 设计决策

① **方向语义不对称是刻意的**：rx 环按目的地命名（G_old 的环由 G_new 写、G_old 读），tx 环按来源命名（G_old 写、G_new 读）——每环恰好一个生产者一个消费者，rte_ring SPSC 语义下零锁；代价是两个 enqueue 的 gen 参数含义相反，代码用守卫+一次性告警把这类编码错误显式化（`:101-116`）。② flow_map 坚持"进程本地堆内存、无锁无原子"（`:34-46`）：理由是生产/消费/控制面全在同一个数据面线程的 main_loop 里；注释还检讨了旧版 SEQ_CST-on-state 并不是真正的发布机制——诚实的单线程契约胜过假装的并发安全。③ 关键字直接存网络字节序（ff_flow_map.h:57-59）：表只做等值比较，syncache 钩子免去每 SYN 一次字节交换；nginx 消费侧同样 memcpy 裸线序字节（ngx_ff_module.c:480 注释警告"组装成大端整数会存成主机序、永远匹配不上"）。④ 容量语义：65536 是"单窗口新建连接数"而非进程连接上限（`:57-60` 注释），满表先翻倍（最多 4 次）再拒绝——拒绝的时机也在 admit 里讲清楚（`:155-159`）：与其回 SYN-ACK 再被下一个 ACK RST，不如当场拒。

## 新人提示

调这层的第一个工具是 drain 统计：ff_reload_drain_counters 暴露 fwd/peak，rx 环峰值高说明 G_old 消费慢（大概率是其主循环被应用 loop 阻塞）。读代码注意 gen_mismatch 的"精确自环判定"——USR2 下对端 master 的同 gen 不同 slot 是合法目的地（`:504-515`），只有 (slot,gen) 全等才是自环。flow_map 改动必须同步 freebsd/ 两个钩子文件（tcp_syncache.c/in_pcb.c）与 nginx 消费侧的三处字节序约定；fragment/非 TCP-UDP/扩展头一律留在本地栈不参与分流（ngx_ff_module.c:421/431），这是有意的保守边界。tests/integration/test_graceful_reload.sh 与 reload_checks.py 会实际验证"窗口内连接不中断"，改这两个文件后必跑。
