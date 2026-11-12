# 06 · 接收引擎：MPA-DDP-RDMAP 帧的还原与一步式放置

> 仓库 zrlio/softiwarp @ 5d8a418 · 本文行号锚全部经源码核实

## 一、角色定位

siw_qp_rx.c（1351 行）是 siw 的"硬件接收 DMA+协议解析器"替身。TCP 递来的是无边界字节流，接收引擎要在 softirq 回调里同步完成三件事：**切帧**（按 MPA 长度前缀还原 FPDU 边界）、**分派**（按 RDMAP opcode 找处理器）、**放置**（DDP 语义：载荷一步写进注册内存）。RDMA_WRITE 的载荷直达目标缓冲、不消耗本端任何 WQE——"内核旁路零拷贝"这句口号在软件实现里的全部真相都在本篇。与 TX 引擎不同，RX 没有 worker 线程：所有处理都发生在 `siw_qp_llp_data_ready` 的 socket 回调上下文里（IMPLEMENTATION.txt:60-64 自述设计）。

## 二、内部结构

**入口两跳**（siw_qp.c）：socket 数据就绪回调 `siw_qp_llp_data_ready`（:156-198）——校验 rx 未挂起、trylock state_lock、**仅 RTS 态**才调 `tcp_read_sock(sk, &rd_desc, siw_tcp_rx_data)`（:184）；TCP 负责"没数据不调"。第二跳 `siw_tcp_rx_data`（siw_qp_rx.c:1201-1351）是主循环：装载 skb 三元组（:1208-1211），外层 `while (skb_new)` 消费字节；**rx_suspend 置位则整包吞掉**（:1219-1223）——SEND 无 RQE 匹配时的背压手段（连接即将拆除，静默排水）。

**三阶段四态状态机**（枚举 siw_rx_state，siw.h:401-406：GET_HDR/GET_DATA_START/GET_DATA_MORE/GET_TRAILER，数据阶段带两个子态）：

- **GET_HDR**（siw_get_hdr，:929-1026）：两段收头——先凑 4 字节通用头（mpa_len+ddp_rdmap_ctrl），立刻校验 DDP/RDMAP 版本与 opcode 上界（:957-972），再按 `iwarp_pktinfo[opcode].hdr_len` 补齐变长部分（:981-982，WRITE 头 16B、RREQ 头 36B、SEND 头 16B 等，iwarp.h:181-229）。头齐后判新段还是续段：`more_ddp_segs` 时期望 opcode 与上段一致，交错即 -EPROTO（:1008-1015）；DDP_FLAG_LAST 决定本段是否消息末段（:1020-1021）。回主循环后算载荷预算 `siw_fpdu_payload_len`（:1226-1244，mpa_len 推算）与 pad 对齐。
- **GET_DATA_START/MORE**（:1247-1275）：宏 `siw_rx_data` 查 iwarp_pktinfo 表分派 proc_data（siw.h:456-457，与 TX 共用一张表——siw_qp.c:80）；处理器返回 0 转 TRAILER，数据不够停在 MORE 等下个 skb（首段置 first_ddp_seg，续段跳过头部重校，:1256）。-ECONNRESET（unsupp/terminate）置 run_completion=0 直走断连（:1270-1271）。
- **GET_TRAILER**（siw_get_trailer，:876-926）：收 pad+CRC，**CRC32C 直接按网络序比对、免字节序转换**（:911-914 注释明示）；校验通过且 DDP_FLAG_LAST 置位则 `siw_rdmap_complete` 结算整条消息（:1290-1296）。

**四个数据处理器**（proc_data 列）：

- `siw_proc_send`（:457-551）：首段 `siw_rqe_get`（:380-442）取 RQE（或 SRQ，含低水位事件 :422-433），没有 RQE 返回 -ENOENT 触发挂起；校验 QN/MSN/MO（siw_send_check_ntoh :334-378）后按 SGE 链放置，umspace 不足报 LOC_LEN_ERR。
- `siw_proc_write`（:566-636）：零长直接过；`siw_write_check_ntoh` 首段记 sink STag/TO、续段核对一致（:289-321）；`siw_mem_id2obj(dev, ddp_stag>>8)` 查内存（:594）、`siw_check_mem` 验 PD/边界/SR_MEM_RWRITE（:608-609），然后 **`siw_rx_umem`（:125-199）逐页 kmap_atomic+skb_copy_bits 把载荷直接放进用户注册页**——不占 RQ、不产生本端完成，这就是 RDMA WRITE 的"远程放置"。
- `siw_proc_rreq`（:641-650）：请求不携带荷，校验后由 `siw_init_rresp`（:668-722）造伪 READ_RESPONSE WQE——TX 空闲直接占用 tx_wqe 并唤 kthread，忙则挂 IRQ 槽（与 05 篇闭环）。
- `siw_proc_rresp`（:765-852）：`siw_orqe_get`（:729-753）从 ORQ 头槽取回本端 READ 账目，`siw_rresp_check_ntoh`（:236-276）核对 sink STag/TO 与总长（防错配），按账目放置进本端缓冲。

**结算器 `siw_rdmap_complete`**（:1102-1189）：SEND（含 SEND_SE 落穿，:1114-1115）出 RQ 完成、MSN 前移；RRESP 出 SQ 完成（错误强制变 SIGNALED）并 `siw_check_tx_fence`（:1043-1087）放行被 READ_FENCE 挂起的 WQE；RREQ 触发 rresp；WRITE 仅释放内存引用。

**错误路径**（:1306-1341）：rv 非 0 非 EAGAIN 时先补结算（run_completion），随后 `siw_qp_cm_drop(qp, 1)` 排队断连——注释明言优雅 TERMINATE 是 TODO（:1308-1323），当前协议错误=直接断流。

## 三、外部连接

上游：CM 交接来的 socket 回调（04 篇 socket_assoc）；TX 引擎发出的对端帧。下游：放置目标=siw_mem.c 钉住的用户页（umem 二维页表）；完成出口=CQ（siw_rqe_complete/siw_sqe_complete）；READ 响应反哺 TX（IRQ/kthread）；fence 机制联动 ORQ。开头 :59-102 的大段注释是排序契约论证：引用 RFC 5040 §7.5 Rule 17 与 RFC 5041 §5.3，推导出"同 QP 的 DDP 段不可交错、同消息内按序"，**因此本引擎不支持乱序段、收到即报错**——这是对 TCP 有序性的合法透支，也是与硬件 RNIC（带重排序缓冲）的本质差异。

## 四、数据流

字节流→RDMA 消息的还原线：`skb → [GET_HDR: 凑头/验版本/定长] → [GET_DATA: 表分派→权限校验→kmap 直放] → [GET_TRAILER: pad+CRC32C] →（末段?）rdmap_complete → 下一帧`。所有进度记在 rctx 游标（fpdu_part_rcvd/rem、skb_offset、sge_idx/off），skb 耗尽即返回、新 skb 续传——与 TX 的游标续传对称。返回值是本次消费的字节数（:1350），tcp_read_sock 据此推进。

## 五、设计决策

1. **softirq 内同步放置**：目标是内核驻留页，skb_copy_bits+kmap 一次到位，无 defer 无双拷（IMPLEMENTATION.txt:60-64）。代价是大 WRITE 会占住软中断上下文——吞吐与延迟的软件权衡点。
2. **共享分发表**：iwarp_pktinfo 同时服务 TX 模板与 RX 分派，协议能力声明单点维护；增删 opcode 只改一处。
3. **CRC 按 NBO 原生比对**：发送端 crypto_shash_final 出的即是网络序，链路两端零转换（:911-914）。
4. **不支持乱序、不支持 TERMINATE**：两者都是对完整 RFC 的自觉裁剪，前者靠 TCP 有序性背书，后者留 TODO 直接断连（:1308）——审读互操作性问题时先查这两条。
5. **背压即排水**：rx_suspend 不是停收而是丢弃已到字节（:1219-1223），依赖 TCP 流控自然减速对端。

## 六、新人提示

1. 调 RX 问题先分帧还是放置：帧错（版本/opcode/交错）在 GET_HDR 三连校验；放置错（STag/边界/权限）在各 check_ntoh/check_mem，事件类型不同（QP_FATAL vs QP_ACCESS_ERR）。
2. 词汇四件套：MSN（untagged 消息号，按 QN 三列独立计数）、QN（队列号 0/1/2）、MO（消息内偏移）、TO（tagged 偏移）——RFC 5041 的骨架词，对照 iwarp.h:325-330 记。
3. SRQ 消费路径与普通 RQ 在 `siw_rqe_get` 内分叉（:386-435），低水位事件在取走 RQE 后探测（:422-433）——补 RQE 不及时是 SEND 吞数据的头号原因。
4. 实验：在三个 case 各加 dprint（:1226/:1258/:1277），跑 perftest write/send 各一轮，对照 wireshark 的 TCP 流可手工验证切帧逻辑；再 `insmod siw.ko mpa_crc_required=1` 开 CRC 看 trailer 分支。
5. 主线版已补齐 TERMINATE 处理与 stricter 校验，本仓的 TODO 注释是理解"参考实现→产品化"演进的最佳路标。

📌 至此六篇主线闭环：01 总览→02 设备与 verbs→03 QP 与状态机→04 连接→05 发送→06 接收。建议按 03→04→05→06 重读一遍数据面，每篇都回看 iwarp_pktinfo 与 siw.h 两处枢纽。
