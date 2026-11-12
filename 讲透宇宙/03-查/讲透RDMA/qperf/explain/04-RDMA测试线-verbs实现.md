# 04 RDMA 测试线：verbs 实现（rdma.c）

## 一、角色定位

rdma.c（2620 行）是 qperf 的主体与名字来源，实现 Tests 表中 25 个 RDMA 测试（RC/UC/UD/XRC 四种传输 × bw/bi_bw/lat/rdma_read/rdma_write/atomic 组合）。它分两层：上层是 25 对 `run_client_X/run_server_X` 入口薄壳（rd_params + 转发）；下层是统一的 verbs 资源生命周期（rd_open/rd_prep/rd_close）加可复用数据面引擎（rd_client_bw/rd_bi_bw/rd_pp_lat 等）。QP 状态机、内存注册、完成队列、rdma_cm 全封装在这套生命周期里，是学习 verbs API 工程化用法的优秀范本。

## 二、内部结构

**DEVICE 聚合根**（rdma.c:142-163）：一个 struct 收拢全部 verbs 句柄（buffer/mr/pd/cq/qp/ah/srq/xrc/channel），外加本地/远端 NODE（rdma.c:105-114：vaddr/lid/qpn/psn/srqn/rkey/alt_lid/rd_atomic 八字段，即两端要交换的"接线信息"）与 IBINFO/CMINFO。测试函数全程只操作这一个栈上 DEVICE。

**生命周期四段**：

1. `rd_open`（rdma.c:1471-1501）：client 先发请求，memset 清零、记录传输类型与 WR 深度，**按 Req.use_cm 二选一**调 cm_open 或 ib_open（rdma.c:1487-1490）。注意这是并列的两条路而非"CM 失败回退裸 verbs"——use_cm 由 rd_params（rdma.c:1429-1435）事先定死：RC 保留用户选择权（par_use L/R_USE_CM），UC/UD/XRC 一律 setv_u32 强制 0（CM 不支持）。最后 ibv_query_qp 拿 max_inline_data 备用。
2. `rd_prep`（rdma.c:1507-1547）：定 msg_size、分配注册内存（rd_mralloc rdma.c:1717-1742，posix_memalign 页对齐 + REMOTE_READ|WRITE|ATOMIC 全开）、**交换 NODE 结构**（enc_node/dec_node rdma.c:2551-2579，走控制通道）、再进 cm_prep（空函数 rdma.c:1925-1928）或 ib_prep（QP 升 RTR/RTS），非 poll 模式还 ibv_req_notify_cq。
3. 数据面引擎运转（见下）。
4. `rd_close`（rdma.c:1598-1620）：注释明言销毁顺序的坑——先 CQ 后 QP（否则 destroy_qp 可能挂死）、QP 先于 MR。

**两条建链路径**。ib_open（rdma.c:2001-2145）是裸 verbs 流程：解析 MTU（五档 IBV_MTU_*）、从 Req.id 用冒号切出设备名与端口号（rdma.c:2025-2033）、查 Rates 表（rdma.c:304-325，"4xDDR"→IBV_RATE_20_GBPS 等 20 档）、open_device、query_port 取 LID（lmc>0 叠加 src_path_bits，rdma.c:2088-2089）、rd_create_qp 建 QP 并 modify 到 INIT（UD 设 qkey，RC/XRC 全远程权限，UC 只留 REMOTE_WRITE，rdma.c:2104-2120）、随机 PSN。ib_prep（rdma.c:2152-2256）再把 QP 推过 RTR（对端 qpn/psn/lid、path_mtu、min_rnr_timer）与 RTS（timeout/retry/rnr_retry/max_rd_atomic、可选 alt_path 迁移）。CM 路径 cm_open（rdma.c:1768-1776）：client 走 resolve_addr→resolve_route→rdma_connect 标准事件流（cm_open_client rdma.c:1800-1856，每步 cm_expect_event 等待并 cm_ack_event）；server rdma_bind_addr→rdma_listen→等 CONNECT_REQUEST→rdma_accept（cm_open_server rdma.c:1862-1919）；UD over CM 的 qkey/ah_attr 从 CM 事件参数取（rdma.c:1849-1850）。

**数据面引擎五种**：rd_client_bw（rdma.c:885-925，send 深度 NCQE=1024 流水线补发）；rd_server_def（rdma.c:932-969，post NCQE 个 recv 挂着，收完补）；rd_bi_bw（rdma.c:975-1028，双向同抢一个 CQ，按 wr_id 分账）；rd_pp_lat/rd_pp_lat_loop（rdma.c:1034-1109，乒乓，done 位图 1|2 凑齐才回发）；rd_rdma_write_poll_lat（rdma.c:1119-1173，绕过 CQ，RDMA WRITE 后忙等 volatile 内存首尾字节变标记——MPI 的经典 trick，注释强调 *p/*q 须在 sync_test 前置初值避免竞态）。原子操作另有 ib_client_atomic（rdma.c:1283-1324）与校验版 ib_client_verify_atomic（rdma.c:1330-1392，atomic_seq rdma.c:1399-1419 生成可验证序列逐槽核对）。server 侧"无事可做"（RDMA read/write 的 responder、atomic 被操作端）统一 rd_server_nop（rdma.c:1263-1277）：post 一个 recv 后 `while(!Finished) pause()`——网卡硬件自己干活，CPU 睡觉。

**收发原语与轮询**。rd_post_send（rdma.c:2379-2423）单 SGE、IBV_WR_SEND；rd_post_rdma_std（rdma.c:2465-2502）挂 remote_addr=rnode.vaddr/rkey=rnode.rkey——_prep 交换的 NODE 在此生效。rd_poll（rdma.c:2508-2529）双模式：poll_mode=0 先阻塞 ibv_get_cq_event 再 req_notify 再 poll（事件驱动省 CPU）；=1 纯忙轮询换延迟。maybe（rdma.c:2538-2545）吸收"Finished 后 EINTR"的合法中断。

## 三、外部连接

- **对框架**：25 个入口按 02 篇契约注册（qperf.c:570-595）；rd_params 声明参数消费；统计进 LStat（rem_s/rem_r 在 RDMA read 记账远端，rdma.c:1244-1245）。
- **对库**：libibverbs + librdmacm，configure.ac AC_CHECK_LIB 探测到才编译本文件（Makefile.am else 分支不含 rdma.c）。
- **对控制通道**：NODE 交换、端口通告（cm_open_server L1880、cm_open_client L1812 收）走 support.c 的 send_mesg/recv_mesg。
- **防御性符号**：rdma_not_called（rdma.c:332-337）用 `if (0) ib_migrate(NULL)` 骗过 -Wunused-static——ib_migrate（rdma.c:2292-2310，主动路径迁移）无调用方，AFR 测试半成品。

## 四、数据流

`qperf server rc_bw`（默认 use_cm=1）：

1. client rd_open→cm_open_client：收 server 经 CM listen socket 通告的 TCP 端口→resolve_addr/route→connect→ESTABLISHED；server 对称 accept。
2. rd_prep：两端 rd_mralloc→NODE 八字段经控制通道互换→cm_prep 空转→req_notify_cq。
3. rd_client_bw：sync_test 起闹钟→rd_post_send_std(left_to_send(&sent, NCQE))（qperf.c:1941-1954，no_msgs 限额时截断）→循环 rd_poll 批量收 CQE 逐项查 status，按 Req.no_msgs 提前收工，否则补发 n 个。
4. server rd_server_def：recv 对称，access_recv 开启时每完成一个 touch_data。
5. stop_test_timer→exchange_results→rd_close。

RDMA write 带宽走 rd_client_rdma_bw(IBV_WR_RDMA_WRITE_WITH_IMM)（rdma.c:505）：write+immediate 仍消耗对端 recv WR，故 server 用 rd_server_def；write poll lat 则两端进忙等循环。

## 五、设计决策

- **use_cm 二选一而非回退链**（rdma.c:1487-1490）：CM 简化地址解析但只支持 RC/UD，裸 verbs 换来全传输类型 + LID/SL/alt_port 等 IB 旋钮。两套并存是能力矩阵差异驱动，不是容错层级。
- **NCQE=1024 批量流水线**（rdma.c:52）：一次 post/poll 上千 WR，CQE 处理 amortize 掉系统调用开销——RDMA 带宽打满线速的关键，max_cqes 统计（rdma.c:901-902）顺手记录批量深度。server_nop 则反向极致：responder 零 CPU 参与，pause() 等 SIGALRM，cpu 利用率列因此成为 RDMA offload 能力的直接证据。
- **内联自动启用**：msg_size ≤ max_inline_data 就 IBV_SEND_INLINE（rdma.c:2406/2488），小消息绕开 MR 读延迟受益；RDMA read 除外（rdma.c:2488 特判）。
- **XRC 走 SRQ**：rd_create_qp 的 XRC 分支（rdma.c:1679-1701）开 XRC domain + XRC SRQ 把 recv 队列共享化——XRC 区别于 RC 的全部要点，详见 05 篇。

## 六、新人提示

- 调试先开 `-D`：show_node_info（rdma.c:1553-1588）打印两端 lid/qpn/psn/rkey/vaddr，链路不通先核对 NODE 交换。注意 rdma.c:1586 格式串只放 5 个占位却传 6 个参数（n->srqn 多余被忽略），非 XRC 分支 srqn 恒 0。
- rd_mralloc 的 size==0 防御（rdma.c:1725-1726 强设 1）对应注释"我以为上层会拦截 size 0，我错了"——历史 bug 化石。
- QP 状态机排错：INIT（ib_open L2095-2123）→RTR/RTS（ib_prep L2196-2255）。卡 RTR 多半是 lid/qpn 交换错，卡 connect 多半是 CM 端口通告没到。
- Mellanox 驱动 workaround（rdma.c:1268）：rd_server_nop 明知 RQ 应为 0 仍开 1 个 recv WR——换硬件移植时首个重验点。
