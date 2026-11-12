# explain-04 · tcp.c：L2-L4 翻译状态机与 TCP 动态镜像

## 1. 角色定位

`tcp.c`（4121 行）是全仓最重的模块，实现"guest 眼里的 TCP 对端"：在单一 L2 接口（tap）与宿主原生 L4 socket 之间翻译 TCP 流量。它**不是**一个 TCP 栈——头注释 Theory of Operation（`tcp.c:15-270`，全仓金矿）开宗明义三个目标：**transparency**（guest 应用感觉像直接跑在宿主上：尽量不做地址/端口转换，用 TCP_INFO 观察 socket 参数、用 tap 来包的 TCP 头反推对端行为，把 TCP 动态"镜像"回去）；**simplicity**（只实现一小撮 TCP 逻辑，重传/拥塞/排队全部委托给两端内核；不分段、不显式排队、不重组）；**security**（零动态内存分配，TODO synflood 防护）。支持四类连接流向（`tcp.c:25-41`）：host→guest（service mesh 主场景）、remote→guest、guest→host（补完整性）、guest→外网（如 NTP）。pasta 模式下本地流量走 `tcp_splice.c` 快路径（`tcp.c:260-269` 明确分界），本文件只管"经过 L2 的那半"。

## 2. 内部结构

**状态模型**：反直觉的核心决策——不用状态机而用**事件位图**（`tcp.c:130-163`）。`struct tcp_tap_conn`（`tcp_conn.h:31-`）的 `events` 字段是 8 位：SOCK_ACCEPTED/TAP_SYN_RCVD/ESTABLISHED 是三个互斥的基础态（设置即清其它，`tcp.c:160-163`），叠加 SOCK_FIN_RCVD/SENT、TAP_FIN_RCVD/SENT/ACKED 五个关闭事件；events==CLOSED 即连接死。注释说破动机：这个实现里绝大多数任务是"对事件做反应"而非"状态关联动作"，事件模型天然贴合。日志需要时用 `tcp_state_str[]`（`tcp.c:397-405`）把事件组合翻译成近似 RFC 状态名。

**连接建立（出站，guest 发起）**：`tcp_conn_from_tap()`（`tcp.c:1688`）是教科书级流程：`flow_alloc()` 要表项 → `flow_initiate_af()` 登记五元组 → `flow_target()` 判定转发目的地 → `tcp_conn_sock()` 从预开 socket 池取 socket → **用 bind() 探测目的地是否本机**（`tcp.c:1738-1756`：bind 失败即本地已有监听，打 LOCAL 标记改变后续窗口/ACK 策略；bind 成功则结论无效，换 socket 继续）→ 从 SYN 选项提取 MSS 设 TCP_MAXSEG（`tcp.c:1769-1772`）、`tcp_get_tap_ws()` 学窗口缩放因子 → 记录 `seq_init_from_tap`、按 `flow_hash_insert` 的哈希种子生成 `seq_to_tap`（`tcp_init_seq()`，`tcp.c:1519`——ISN 由流哈希+时间派生，防猜测）→ `connect()` 异步发起，EINPROGRESS 则等 EPOLLOUT。入站方向（host/remote 发起）由 `tcp_listen_handler()`（`tcp.c:2607`）accept 后 `tcp_tap_conn_from_sock()`（`tcp.c:2561`）建表项、passt 主动向 guest 发 SYN。

**数据上行（socket→tap）**：`tcp_data_from_sock()`（`tcp.c:1870`）是关键薄层：算 `already_sent = seq_to_tap - seq_ack_from_tap`，超出 guest 窗口就打 STALLED/ACK_FROM_TAP_BLOCKS 标记返回（`tcp.c:1890-1895`），否则按模式分派给 `tcp_buf_data_from_sock()`（L2 帧模板池路径，tcp_buf.c）或 `tcp_vu_data_from_sock()`（vhost-user 描述符路径）。零拷贝的心脏在 `tcp_set_peek_offset()`（`tcp.c:471`）：若内核支持 SO_PEEK_OFF（`tcp_probe_peek_offset_cap()`，`tcp.c:2871` 探测，`tcp_init()` `tcp.c:2947` 缓存结果），recv 永远从"guest 已 ACK 到的位置"peek，数据在内核 socket 缓冲里原地不动，直到 `tcp_sock_consume()`（`tcp.c:1843-1858`）用 `recv(NULL, MSG_TRUNC)` 按前进的 ack_seq 丢弃已确认部分——**重传不用应用层留副本，guest ACK 之前数据一直躺在内核缓冲里**。

**数据下行（tap→socket）**：`tcp_data_from_tap()`（`tcp.c:1932`）处理已建立连接的来包：RST 即关；旧序号+无载荷判为 keep-alive（`tcp.c:1979-1999`）；ACK 推进 `max_ack_seq`，同序号同窗口的重复 ACK 记 `retr` 触发快速重传（`tcp.c:2007-2012`）；零窗口包触发 `tcp_rewind_seq()`（`tcp.c:1279`）倒回重发。

**窗口/ACK 镜像**：`tcp_update_seqack_wnd()`（`tcp.c:1120`）是"transparency"的技术核心。它回答"该向 guest ACK 到哪、通告多大窗口"：条件齐全时（内核 TCP_INFO 提供 bytes_acked/delivery_rate、非 LOCAL、非低 RTT 目的、缓冲显著大于带宽时延积——`tcp.c:1139-1159` 的长注释解释每条判据）**只 ACK 对端真正确认的字节**（`tcpi_bytes_acked + seq_init_from_tap`，`tcp.c:1188-1189`），让 guest 看到真实的端到端确认；否则退化为"收到就 ACK"。窗口通告走 `tcp_wnd_from_sndbuf()`（`tcp.c:1032`）：用 SIOCOUTQ+SO_MEMINFO 估算 socket 可用缓冲，按 MSS 分段折算，再做 RFC 813 SWS 防呆——小于 MSS 的窗口直接归零（`tcp.c:1075-1103` 的长注释），最后与内核报告的 `tcpi_snd_wnd` 取小。

**事件入口三件**：`tcp_tap_handler()`（`tcp.c:2305`）解析 TCP 头与选项，`flow_lookup_af()` 查表；查无且是裸 SYN 则建新连接，否则 `tcp_rst_no_conn()` 回 RST（`tcp.c:2342-2348`）；随后按事件位分派到握手完成/建立/半关各分支。`tcp_sock_handler()`（`tcp.c:2757`）处理 socket 侧事件：EPOLLERR→RST、RDHUP→SOCK_FIN_RCVD、IN→`tcp_data_from_sock`、OUT（connect 完成/写疏通）→补 ACK。`tcp_timer_handler()`（`tcp.c:2687`）消化 timerfd 超时，按 flags 做 RTO 重传（上限 `tcp.c:186-191` 描述的重试次数）。

**资源与容量**：连接表即 flow 表（`flow_table.h` 的 `union flow` 联合体，头注释 `tcp.c:65-77`：TCP_MAX_CONNS 静态上限 128k；窗口最大 16MiB 对应 MSG_PEEK 预分配缓冲，窗口缩放因子上限 256）。socket 预开池 `init_sock_pool4/6`（`tcp.c:442-443`）由 `tcp_sock_refill_pool()`（`tcp.c:2826`）补货，避免连接建立时才 socket()。迁移专用大缓冲 `tcp_migrate_snd/rcv_queue`（各 64MiB 静态，`tcp.c:368-374`，注释自嘲 "we're going away after this, so splurge"）。`tcp_defer_handler()`（`tcp.c:3042`）驱动 keepalive（KEEPALIVE_INTERVAL=30s，`tcp.c:353`）与不活跃回收（INACTIVITY_INTERVAL=7200s，`tcp.c:352`）。3077 行起是 TCP_REPAIR 迁移序列（repair_on/off、dump/repair 队列与序号，见 explain-09）。

## 3. 外部连接

依赖：`flow.c`（表项生命周期与哈希查找）、`tcp_buf.c`/`tcp_vu.c`（两条数据路径）、`tap.c`（`tcp_fill_headers()` 在 `tcp.c:950` 组 L3/L4 头后由 buf/vu 路径调用 tap 发送）、`repair.c`/`serialise.c`（迁移）、`linux_dep.h`（手工镜像的 `struct tcp_info_linux`，规避发行版 uapi 漂移——`tcp_info_cap` 宏 `tcp.c:425-427` 逐字段按 getsockopt 实际返回长度做能力检测，snd_wnd/bytes_acked/min_rtt/delivery_rate 四个能力开关 `tcp.c:429-436` 各对应一个内核 commit）。被依赖：`passt.c`（三个 epoll handler 入口+defer）、`tcp_splice.c` 共用 `tcp_conn.h` 与 `conn_event()`。

## 4. 数据流

guest 向外网发一段数据的往返：SYN → `tcp_conn_from_tap` 建流、镜像 MSS/WS → 对端数据到 socket，EPOLLIN → `tcp_sock_handler` → `tcp_data_from_sock`：already_sent < 窗口 → `tcp_buf_data_from_sock` peek 数据组帧 → `tcp_fill_headers` 填 seq=seq_to_tap、窗口=wnd_to_tap → tap 发出、seq_to_tap 前进。guest 回 ACK → `tcp_data_from_tap` 检出 ack_seq 前进 → `tcp_sock_consume` 从 socket 缓冲丢掉已确认字节 → peek offset 归零对齐。若 ACK 丢失超时，timerfd 触发 → 从 `seq_ack_from_tap` 重发（数据仍在内核缓冲，peek offset 回拨即可）。

## 5. 设计决策

最有迁移价值的三条：**其一，借用内核缓冲做重传仓库**——SO_PEEK_OFF + MSG_TRUNC 组合让"未确认数据"天然驻留内核，省掉整个应用层发送队列，这是"简单性"目标的落地（头注释 `tcp.c:71-74`）。其二，**动态镜像而非协议终结**：passt 不实现拥塞控制，它把两端内核的 TCP 状态（窗口、ACK、MSS）互相转译，自己是"透明的翻译官"——`tcp.c:44-50` 把这一点列为 transparency 的实现手段。其三，**能力探测+优雅降级**：TCP_INFO 新字段逐个探测（`tcp.c:2920` `tcp_probe_tcp_info`），没有 bytes_acked 就退化为收到即 ACK，没有 SO_PEEK_OFF 就回退读缓冲，老内核上功能完整只是行为略糙。

## 6. 新人提示

必读 `tcp.c:15-270` 的 Theory of Operation（数据流四元组 seq_to_tap/seq_ack_from_tap/seq_from_tap/seq_ack_to_tap 的语义在 `tcp.c:215-227`，读代码前先背下来）。改代码时注意：events 位操作务必走 `conn_event()`（有日志与清位语义），直接赋 `conn->events` 会破坏不变量；`tcp_update_seqack_wnd` 的 ack 序号单调性保护（`tcp.c:1192-1197`）是防止 bytes_acked 方法与回退方法切换时 ACK 倒退的，别删。调试入口：`flow_trace` 日志按流过滤；`tcp_state_str` 让日志可读。坑：LOCAL 标记的连接（bind 探测出的本机目的地）走不同窗口策略，测试透传行为时注意 host 内自连场景；VALGRIND 下 `tcp_sock_consume` 特意 noinline（`tcp.c:1834-1842`），别"优化"。
