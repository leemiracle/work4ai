# 09 · CEP 端点与 TCP 胶合：socket 回调主权的三次移交与字节流的入口分发

> 仓库 zrlio/softiwarp @ 5d8a418 · 本文行号锚全部经源码核实

## 一、角色定位

第 04 篇从 CM 流程视角看过建连全链；本篇换镜头，聚焦那条链的地基——**CEP 这个对象本身怎么活**（资源模型、互斥、工作池），以及 siw 与 Linux TCP 栈的**胶合层**：内核 socket API 的封装、sk_callback_lock 下的回调安装/还原、字节流从 TCP 进入 RDMA 引擎的入口分发。siw 没有自己的链路层，一切输入输出都借道 TCP socket；胶合层的质量决定并发正确性。作者在 IMPLEMENTATION.txt:69-73 自评"三个状态机（socket/QP/CEP）交互趋于混乱，CM 代码已知有 bug"——本篇把三者的交界面单独拆开看，正是读懂这句自评的前提。

## 二、内部结构

**CEP 资源模型**。`siw_cep_alloc`（siw_cm.c:176-200）：kzalloc 后初始化四个链表头（listenq/devq/work_freelist）、kref_init、IDLE 态、waitq、自旋锁，挂进 `sdev->cep_list` 并 `atomic_inc(&sdev->num_cep)`——debugfs 的 `ceps` 视图（siw_debug.c）就扫这张表。生命周期由 kref 护送：`siw_cep_get/put`（:457-473），归零触发 `__siw_cep_dealloc`（:272-293）：WARN_ON 残留 listen_cep、释放 mpa.pdata、回收 work 池、摘链、kfree。**in_use 互斥**（:235-269）：`siw_cep_set_inuse` 自旋锁内查 in_use，被占则 `wait_event_interruptible` 睡眠重试（signal 一律 flush，:249-251——CM 工作不响应信号）；`siw_cep_set_free` 清位+wake_up。它与单线程 workqueue（:1939）双保险：队列串行已保证同 CEP 工作不并发，in_use 还挡住进程上下文（accept/reject/destroy）与工作上下文的交错。

**工作池**：每个 CEP 创建时预分配 4 个 `siw_cm_work`（siw_cm_alloc_work :310-334），用完即还 freelist（siw_put_work :227-233）——**MPA 握手期五类工作（siw_cm.h:113-119）不会陷入分配失败**，这在软中断回调里排队工作的场景是必要的保守。MPA 超时用其中一个 work 兼任定时器：`mpa_timer` 指针 + MPAREQ_TIMEOUT=10s/MPAREP_TIMEOUT=5s（siw_cm.h:110-111），`siw_cancel_mpatimer`（:214-225）cancel 成功才补 put——定时器持有 CEP 引用的账算得很细。

**socket 胶合封装**：`ksock_recv`（:475-486）把 kvec+msghdr 包成一行 `kernel_recvmsg`；`kernel_bindconnect`（:1268）SO_REUSEADDR+阻塞 connect；`kernel_peername/localname`（:153-163）取址；`siw_sock_nodelay`（:73）设 TCP_NODELAY。四个原生回调的保存/安装/还原是三函数套：`siw_sk_save_upcalls`（:112-123，sk_state_change/data_ready/write_space/error_report 存进 CEP 同名字段）、`siw_cep_socket_assoc`（:165-173，sk_user_data=cep+安装 siw_cm_llp_* 四回调）、`siw_sk_restore_upcalls`（:125-132，原回调写回、sk_user_data 置 NULL）。**sk_to_cep/sk_to_qp 两宏**（siw_cm.h:150-151）都读 sk_user_data——同一字段的类型全靠阶段约定。

**回调桥（CM 阶段）**：`siw_cm_llp_data_ready`（:1162-1196）在 `read_lock(&sk->sk_callback_lock)` 下按 CEP 态过滤——AWAIT_MPAREQ/REP 才排队 READ_MPAHDR（:1184-1188）；**RDMA_MODE 与 LISTENING 静默 break**（:1179-1182）：前者因为回调主权已归 QP（理论上不会再进来，进来说明竞态），后者监听 socket 的数据无意义。`siw_cm_llp_state_change`（:1219-1266）翻译 TCP 态：ESTABLISHED→ACCEPT 工作（:1247）；CLOSE/CLOSE_WAIT→置 tx_suspend+PEER_CLOSE（:1251-1256）；**末尾无条件调 `orig_state_change(sk)`**（:1265）——把事件还给 TCP 栈原来的持有者，劫持必须代传。error_report 同理转发（:1206-1217 记 sk_err 后调 cep->sk_error_report）。write_space 在 CM 阶段只打印（:1198-1204）——MPA 头 16 字节，阻塞都不会。

**QP 阶段回调与入口分发**：握手完成时 `siw_qp_socket_assoc`（siw_qp.c:288-298）在 `write_lock_bh(&sk->sk_callback_lock)` 下把 sk_data_ready 换成 `siw_qp_llp_data_ready`、sk_write_space 换成 `siw_qp_llp_write_space`（:297-298）——**主权的第二次移交**（第一次是 CM 安装回调）。此后数据到达走 siw_qp.c:156-198：trylock `qp->state_lock` 读锁（拿不到说明正在改态，数据留给下次回调）+ 仅 RTS 态才 `tcp_read_sock(sk, &rd_desc, siw_tcp_rx_data)`（:184）。`tcp_read_sock` 是 TCP 栈的"消费式读"接口：对 receive queue 里每个 skb 调一次 `siw_tcp_rx_data`（siw_qp_rx.c:1201），传 read_descriptor_t（arg.data=qp）、skb、offset、len——**skb 不出栈，栈借回调让 siw 看一眼**。siw_tcp_rx_data 装载游标（skb_new/skb_offset/skb_copied，:1208-1211）后进入 06 篇剖析过的 HDR/DATA/TRAILER 状态机，**返回值是本次消费的字节数**（:1350），tcp_read_sock 据此推进；返回小于可用字节数意味着引擎已满（rx_suspend 整包吞掉，:1219-1223），剩余数据留在队列等下次回调。

## 三、外部连接

上游：TCP 栈的回调点（softirq 上下文）与 siw_cm_work_wq 工作线程（进程上下文）——**同一 CEP 的事件来自两个执行域**，in_use+单线程队列+sk_callback_lock 三件套划界：回调桥只做"翻译+排队"，重活推给工作线程。下游：MPA 头收齐后 siw_proc_mpareq/mpareply（04 篇）；RDMA_MODE 后字节流交 06 篇接收引擎。横切：`siw_qp_cm_drop`（:385-454）断连时 `siw_socket_disassoc`（:134-150）还原回调、sk_user_data 清空——第三次主权变更（交还内核）；get_tcp_mss（siw_cm.h:157-170）跨版本摸 GSO 段长给 TX 引擎定段。

## 四、数据流

被动建连到数据期的回调时序：`监听 socket ESTABLISHED → cm_llp_state_change（softirq）→ queue ACCEPT → wq 线程 siw_accept_newconn：新 socket+新 CEP+AWAIT_MPAREQ → MPA req 到达 → cm_llp_data_ready → queue READ_MPAHDR → siw_proc_mpareq（进程上下文收头）→ 应用 accept → siw_qp_socket_assoc 换回调（**此刻起 data_ready 直通 QP**）→ 发 MPA rep → 对端首个 RDMA FPDU 到达 → siw_qp_llp_data_ready（softirq）→ tcp_read_sock → siw_tcp_rx_data 状态机逐字节消费`。此后 CM 回调仅剩 state_change 还挂在 socket 上（data_ready 已换人），FIN 到达仍触发 PEER_CLOSE——**收发回调归 QP、连接状态回调留 CEP**，分工在 assoc 时一次性写定。

## 五、设计决策

1. **回调薄、工作重**：softirq 只翻译排队，MPA 解析、upcall 全在工作线程——避免软中断里跑可睡眠逻辑（kernel_recvmsg 可能睡眠）。
2. **sk_user_data 单字段判主**：零额外内存的复用，代价是所有回调必须防御 `!sk->sk_user_data`（:1169-1172 的 WARN_ON+goto out）——易主窗口期回调照常触发，判空是生死线。
3. **预分配工作池**：握手路径零动态分配，把内存故障可能性从建连关键路径上摘除。
4. **回调劫持但代传**（orig_state_change :1265）：socket 仍是内核 TCP 的 socket，劫持者承担转发义务——漏转会让 TCP 内部状态机（如 inet_sock 的 ESTABLISHED 记账）失真。
5. **tcp_read_sock 而非 kernel_recvmsg 收数据**：避免从 skb 拷贝到用户缓冲，引擎直接在 skb 上零拷贝解析放置（06 篇）——这是接收路径性能模型的地基。

## 六、新人提示

1. 调"连接卡住"按回调主权分期定位：握手前看 siw_cm_wq 线程栈（`ps -eLf | grep siw_cm`）、RDMA_MODE 后看 softirq CPU 占用与 debugfs qps 的 rx 游标。
2. sk_callback_lock 的锁序铁律：所有 CM/QP 回调先拿它 read，工作线程改回调拿 write（siw_qp_socket_assoc :293）——任何新代码在回调里再拿别的锁，都要确认不与 write 侧逆序。
3. `pr_info("cep already in RDMA mode")`（siw_cm.c:958，work_handler 的 READ_MPAHDR default 分支）出现即说明 MPA 头在移交后到达——竞态现场标记，不是普通日志。
4. in_use 等待用 interruptible 但 flush_signals 重试（:249-251）：CM 工作不接受信号提前退场——理解这点才能解释为什么 cm 线程"杀不死"。
5. 动手：在两个 data_ready 回调各加 jiffies 打点，跑一次 perftest，观察最后一次 CM data_ready 与第一次 QP data_ready 的时间差——那就是移交窗口的实测宽度。

📌 下一篇：10 篇越过内核边界看 userlib——alloc_context 的版本握手与 mapped 快路径如何免 syscall 提交工作。
