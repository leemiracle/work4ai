# 12 · 软 iWARP 性能边界：每个 FPDU 的 CPU 账单，与一张分发表的勘误

> 仓库 zrlio/softiwarp @ 5d8a418 · 本文行号锚全部经源码核实

## 一、角色定位

收官篇回答整个系列悬着的问题：**软件 iWARP 到底慢在哪、快在哪、边界在哪**。siw 把 RNIC 的全部职责搬进内核软件：MPA/DDP/RDMAP 帧解析在 softirq、CRC32C 用 crypto API、TCP 收发走内核 socket、完成通知靠共享内存。IMPLEMENTATION.txt:85-88 作者自陈"performance was not yet our main focus, there is known headroom"——但代码里处处是性能意识的痕迹（mapped 模式、burst 限流、绑核、忙等）。本篇前半算一笔**每个 FPDU 的 CPU 账单**并对比硬卡；后半完成一项承诺的勘误——分发表 siw_qp.c:131-132 把 SEND_SE 与 SEND 绑到同一个 siw_proc_send，**这不是遗漏而是分层**，SE 的协议语义藏在 1600 行之外的结算器里。

## 二、内部结构：每个 FPDU 的 CPU 账单

**发送侧六项开销**（对照 05 篇流水线）：① WQE 提交——mapped 模式下用户态写共享环+一次 doorbell syscall（10 篇），这是**全链唯一强制 syscall**（IMPLEMENTATION.txt:102-110 自述设计目标）；无 doorbell 补丁内核时空命令 doorbell 退化为一进一出两次特权级切换。② 头部构造——prepare_tx 每段 memcpy 头模板（siw_qp_tx.c:200+）。③ CRC32C——每段 crypto_shash_update 累计、final 比对（:297/:625，每 FPDU 恒定开销，且是可协商关闭的：mpa_crc_required=0 时 :60 不要求）。④ 数据搬运——sendpage 路径免拷贝（use_sendpage），但 KVA 化的 map_sg 仍要遍历散射表。⑤ TCP 栈本体——软中断、队列、ACK 处理，这部分是"借来的成本"，硬卡上根本不存在。⑥ burst 限流——SQ_USER_MAXBURST=10 段（siw.h:84）就让出 CPU（siw_qp_tx.c:945），防单 QP 饿死同核其他流量，代价是吞吐上不去时唤醒延迟叠加。

**接收侧三项**（对照 06 篇）：① softirq 上下文同步解析+放置——tcp_read_sock 逐 skb 回调（09 篇），每 FPDU 两次头部校验（通用头+变长头）；② kmap_atomic+skb_copy_bits 逐页放置——CPU 搬运替代硬件 DMA；③ RQ 匹配/CQ 发布——锁+屏障+可能的 comp_handler。

**与硬 RNIC 的结构性对照**：mlx5/CX 网卡把 ①②③④ 全部做进 ASIC 线速逻辑，MSI-X 完成中断替代共享内存握手，应用侧 doorbell 经 BAR 写不进内核；**siw 省掉的是硬件成本与 PCIe 传输，付出的是每个 FPDU 数千 CPU 周期**。粗算量级：一次 crc32c final + 两次头校验 + 锁往返 + softirq 进出 ≈ 5k-10k cycles/FPDU；4KB FPDU 意味着单核每秒 20-40 万 FPDU ≈ 8-16 Gbps 上限——**同量级于 25G 线速的单向，但吃掉整核**；而硬卡 100G 双向只需一个核管理队列。对 SEND/RECV 小消息（无 RDMA 卸载收益），siw 对比内核 TCP 的额外开销只有帧头+CRC+verbs 间接层，**约 10-20% 劣化**——软 iWARP 的真实定位正是这里：无卡环境跑通 RDMA 语义，性能是第二位。

**软件侧的性能努力清单**（代码可考）：mapped 快路径（10 篇）；doorbell 在调用者上下文直跑 sq_process（siw_verbs.c:969-971 置 in_syscall=1，省 kthread 唤醒）；low_delay_tx=1 忙等窗口（siw_qp_tx.c:70-72，:1310-1324）压唤醒延迟；tx_cpu_list 绑核 + kthread 突发负载均衡到空闲核（siw_main.c:80-85、siw_qp_tx.c:1388-1398，与 RSS 对齐）；零拷贝 sendpage。**没有做的**（边界所在）：无 GSO/TSO 聚合（每 FPDU 独立送栈）、无中断聚合、CRC 用通用 shash 而非 pclmulqdq 内联、单条 CQE 收割的锁往返（08 篇 TODO）。

## 三、外部连接

性能叙事的上下游：上承 05（burst/零拷贝模型）、06（softirq 放置成本）、08（通知握手成本）、10（doorbell 唯一 trap）、11（FULLSEGS 死代码正是想优化"整段发送"的未竟实验——若复活可减少段分裂，但引入 wpace 等待）；下接现实选型：rdma-core 主线版 siw 已重写（多核扩展、crypto 优化），本仓的价值是**性能决策的最小可读标本**。测试工具链即 10 篇的 perftest 线：ib_write_bw/ib_send_lat 直接量化本篇每项账单。

## 四、数据流：SEND_SE 的完整一生（勘误的主体）

分发表 iwarp_pktinfo（siw_qp.c:80-151）按 RDMAP opcode 绑处理器：SEND→siw_proc_send（:114）、**SEND_SE→siw_proc_send（:131-132）**、SEND_INVAL/SEND_SE_INVAL→siw_proc_unsupp（:123/:141）、TERMINATE→siw_proc_terminate（:150）。**误读**：SEND_SE 与 SEND 同绑，容易得出"SE 语义未实现"的结论。**实况分三层**：

1. **放置层**（分发表）：SE 与非 SE 的载荷放置完全同构（都是 untagged SEND 消息队列消费），分派无需区分——同绑是正确的。
2. **发送层**（siw_qp_tx.c:210-216）：本端 WQE 带 SIW_WQE_SOLICITED 时，memcpy 头模板换成 `iwarp_pktinfo[RDMAP_SEND_SE].ctrl`——**线上的 SE 位由本端 post_send 的标志点燃**。git 考古 ae550b5 "fixed SOLICITED flag in tx" 正是这条映射的修复。
3. **结算层**（siw_qp_rx.c:1113-1115）：收端 `case RDMAP_SEND_SE: wqe->rqe.flags |= SIW_WQE_SOLICITED;` **fall through** 进 SEND 分支出 RQ 完成——SE 位在消息收尾时回填到 RQE 标志。
4. **通知层**（08 篇）：siw_rqe_complete → siw_cq_notify 读到 SOLICITED 标志且用户 arm 了 SIW_NOTIFY_SOLICITED——触发完成事件。

闭环即：**本端 WR 标志 → 线协议 SE 位 → 对端 RQE 标志 → solicited 完成事件**。分发表只承担第 1 层；把协议语义读进分发表，就会漏掉藏在结算器 switch 里的 fall-through 链——这正是 06 篇"SEND_SE 落穿"一笔带过处，本篇补全证据链。对照 INVAL 系列（SEND_WITH_INVALIDATE）绑 siw_proc_unsupp（siw_qp_rx.c:855+）才是"真不支持"，两者别混。

## 五、设计决策

1. **正确性优先于吞吐**：作者自陈 performance 非目标，burst=10、单 CQE 收割、阻塞 connect（09 篇）都是保守选择——软 iWARP 的使命是语义可跑通、可测试（10 篇的测试线价值），性能留白。
2. **SE 语义的分层放置**：分发表管放置、结算器管协议效应——一张表干一件事，新增 opcode 只动一处；代价是语义追踪要跨三个文件，需本篇这样的导览。
3. **可协商 CRC**：mpa_crc_required/strict 两参数矩阵（04 篇）允许关 CRC 换性能——RFC 5044 合规与吞吐的显式交易。
4. **mapped 模式是最大性能杠杆**：把提交成本压到一次 syscall，剩余全部走共享内存——但数据搬运仍在内核，"用户态直跑"的假象仅覆盖控制面。
5. **每 FPDU 一个 syscall 的硬边界**：无 doorbell 补丁时空命令 doorbell 是吞吐天花板；这是软件 iWARP 与 kernel-bypass RDMA（真卡）在提交路径上的本质差距，优化到头也绕不开。

## 六、新人提示

1. 跑性能前先定基线：同机 loopback（loopback_enabled=1）下 siw vs TCP（iperf3）对比，再看跨机；小消息延迟重点看 ib_send_lat——softirq 解析成本在小包上占比最高。
2. 绑核三件套：`insmod siw.ko tx_cpu_list=<核>`、应用与 NUMA 对齐、关 irqbalance——siw 的单核模型对 CPU 迁移极敏感（QP 记住自己的 cpu，siw_qp_tx.c:1381）。
3. 性能调参四项按序试：mapped 模式（内核 if_type）> tcp_nodelay=1（04 篇）> 关 CRC（两端都要）> low_delay_tx 维持默认 1。
4. 读到分发表任何"意外绑定"先查结算器再下结论：opcode 的协议语义可能在 siw_rdmap_complete（siw_qp_rx.c:1102-1189）里另有分支——本篇 SEND_SE 即是。
5. 动手：用 perf 采样 perftest 全速跑分，看 `crypto_shash_final`、`skb_copy_bits`、`_raw_spin_lock_irqsave` 三者的占比分布——这份 profile 就是本篇账单的实测版，也是判断"优化下一步该打哪"的依据。

📌 本系列 12 篇至此收官：01-03 纵览与对象生命周期，04-09 五条执行线（CM/SQ/RX/CQ/胶合），10 用户态，11 考古，12 性能——一张从动机到边界的全图。
