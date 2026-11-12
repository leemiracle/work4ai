# qperf ONBOARDING

> 图谱 253 节点/396 边/16 层（commit 118a571）；行号锚均经核实。

## ① 项目定位

qperf 测 RDMA 与 socket 各协议**带宽/延迟/消息率**：一端裸跑 `qperf` 即 server，另一端 `qperf <host> <test>` 驱动。主作者 Johann George（QLogic，qperf.h:4-5），OFED 标准配网工具。全仓 5 个 .c 约 7900 行（最大 qperf.c 2868），覆盖 TCP/UDP/SCTP/SDP/RDS 与 RC/UC/UD/XRC。灵魂设计是**双形态编译**：configure.ac:4-8 探测 ibverbs 双符号与 rdmacm，定义 RDMA/HAS_XRC；无 ibverbs 时退化为 socket-only（src/Makefile.am:10-13），Tests[]（qperf.c:556）整块 RDMA 条目随 `#ifdef RDMA`（qperf.c:569）消失。

## ② 快速上手

构建（README:1-5）：`./cleanup && ./autogen.sh && ./configure && make`。注意 `make clean` 清不净，重构建必先 ./cleanup（README:17-18）。

典型用法（help.txt:102 起）：

```bash
qperf                          # server：监听 19765（qperf.c:76）
qperf myserver tcp_bw tcp_lat  # TCP 带宽+延迟
qperf myserver ud_lat ud_bw    # RDMA UD 延迟与带宽
qperf myserver -t 10 rc_bw     # 跑 10 秒（默认 2s，DEF_TIME qperf.c:73）
qperf myserver -oo msg_size:1:64K:*2 -vu tcp_lat  # loop：尺寸 1→64K 每轮×2
qperf myserver udp_lat quit    # 测完关 server
```

测试名支持唯一前缀缩写（find_test qperf.c:832）；选项：`-t` 时长、`-m` 消息大小（K/M/G 后缀，str_size qperf.c:1126）、`-cm` 走 rdma_cm、`-ca` 绑核；完整清单看 `--help`。

## ③ 架构总览（16 层并为 7 段）

**A. 构建引导（L01）**：autogen.sh 引导 autotools；cleanup 删生成物并按三条件决定删否 qperf.spec（cleanup:30-36）。
**B. 探测与打包（L02-L04）**：configure.ac 仅 10 行；qperf.spec.in 以 @RDMA_TRUE@ 占位符双形态打包，生成的 spec 刻意入库供 OFED 用；src/Makefile.am:3-13 是条件编译落点（RDMA 版多 rdma.c 并链 -libverbs）。
**C. 共享契约（L05）**：qperf.h 是五个 .c 唯一交汇点——REQ（qperf.h:153-176，前四字段锁定）、USTAT/STAT（182-202）、RESN/RES（208-232）、PAR_INDEX（L_*/R_* 成对，94-133）、全部测试原型与 extern 全局（363-373）。
**D. 支撑库（L06）**：support.c=测试外基础设施：字节序编解码（enc_int:128/dec_int:141）、控制消息核心 send_recv_mesg（support.c:301，带外唤醒+重试+失联检测）、统一错误出口 error（support.c:537，BUG/SYS/RET 标志）。
**E. 主程序三层（L07-L09）**：qperf.c 命令行层（do_args:727/do_option:848/parse_loop:972）、会话层（server:1337/client:1467/client_send_request:1503/exchange_results:1582）、结果层（calc_results:1875+view_*/place_* 排版）。
**F. 三条测试线（L10-L14）**：socket.c（四协议×两引擎）、rds.c（RDS 变通）、rdma.c（四传输，49 对入口+资源+数据面）。三线独立，仅经 qperf.h 与 support.c 汇合。
**G. 文档（L15-L16）**：help.txt（981 行）单一数据源，±RDMA 标记（help.txt:34,56）按编译条件裁剪；mkhelp 产 help.c、mkman 产 qperf.1。

## ④ 核心链路

**分流**：main（qperf.c:601）= initialize()（开 /proc/stat 等）→ set_signals() → do_args()。do_args（qperf.c:727）中 `-` 参数走选项表，非选项首参当 ServerName、次参查 Tests[] 进 do_loop（qperf.c:774）；**无任何客户端型参数则调 server()**（qperf.c:758）——"裸跑即 server"的本质。

**server 侧**（qperf.c:1337）：server_listen（1416）accept 控制连接 → 收 REQ → **fork 子进程**处理（父进程 waitpid，1349-1357）→ 子进程 remotefd_setup → 版本校验 → 按 req_index 分发 test->server()。

**client 侧**（qperf.c:1467）：client() 补默认值（time=2s/timeout=5s）后直接调 test->client()——**REQ 发送下放给各测试线**：socket 线在 client_init（socket.c:587）、rds 线在 rds.c:131、rdma 线在 rd_open（rdma.c:1476）各自调 client_send_request（qperf.c:1503）。

**三条线的数据面**：
- **socket（tcp_bw）**：client_init 发 REQ 后收服务器回送的数据端口；getaddrinfo_kind（socket.c:693）按协议改写解析结果（SDP 换 AF_INET_SDP、SCTP 换 IPPROTO_SCTP）→ connect → sync_test → while(!Finished) 压流 → exchange_results → show_results。
- **rds**：RDS 无 connect，connect_tcp（rds.c:462）建 TCP 辅助通道带外交地址（get_hosts rds.c:382/331）；AF_RDS 由 get_af_rds（rds.c:59）读 /proc/sys/net/rds/pf_rds 动态发现、回退 21。
- **rdma（rc_bw）**：rd_open（rdma.c:1471）按 `Req.use_cm` 二选一——`-cm` 走 cm_open（rdma.c:1769），默认 ib_open（2001）+ib_prep（2152）经 TCP 换 LID/QPN/PSN → rd_prep（1507）建 QP+注册 MR → rd_post_send_std（2369）按 NCQE=1024（rdma.c:52）压流、rd_poll（2508）轮询 CQ → rd_close（1598）回收。

**计时收尾**：sync_test（qperf.c:1794）= 双端 synchronize + start_test_timer（1805，SIGALRM 间隔 10ms 防 SLES11 连发）→ set_finished（1852）置 Finished 终结循环 → exchange_results（1582）→ show_results（1864）→ calc_results（1875）。

## ⑤ 关键模块深讲

**qperf.c（2868 行）**：三表驱动——ParName/ParInfo（292/316，L_*/R_* 绑 Req/RReq）、Options[]、Tests[]。qperf.c:555 的 `#define test(n) {#n, run_client_##n, run_server_##n}` 以 token 拼接让测试名与入口自动绑定，新增测试只写一对入口+一行 `test(x)`。view_band（2372）自动切 GB/s 与 Gb/s，place_show（2563）右对齐；enc_req/dec_req_data/enc_stat/dec_stat（2635/2680/2708/2730）手工字节序转换支撑异构端。
**rdma.c（2620 行）**：三层——49 对薄壳入口（如 run_client_rc_bw rdma.c:367）→ 公共引擎（rd_client_bw:885 压流/rd_bi_bw:975 双向/rd_pp_lat_loop:1053 往返计时并扣时钟开销/ib_client_atomic:1283）→ 资源层（rd_create_qp:1626/rd_mralloc:1717）。特色：rd_rdma_write_poll_lat（1119）忙轮询测纯写延迟；ib_client_verify_atomic（1330）+atomic_seq（1399）按操作序列推演期望值**校验原子语义正确性**；ib_migrate（2292）APM 路径迁移；rdma_not_called（333）socket-only 占位报错。
**support.c（673 行）**：send_recv_mesg（301）控制面核心；urgent（419）TCP 带外唤醒阻塞对端，双端干净退出的关键；error（537）位标志统一错误出口；touch_data（213）测前触摸缓冲防污染。
**socket.c+rds.c**：getaddrinfo_kind 改写解析结果使 stream/datagram 两引擎（266/415）复用到四协议；rds.c 是历史包袱教科书，tab 缩进与四空格分裂（后并入）。

## ⑥ 设计决策与取舍

**三代传输线的抽象**：socket→RDS→RDMA 三线不共用框架，靠三约定粘合——test 宏注册表、run_client_X/run_server_X 命名约定、公共会话骨架（REQ→sync→数据面→exchange）。代价是各线自带样板，收益是各线按协议本性自由变形。
**条件编译而非运行时探测**：XRC 整块 `#ifdef HAS_XRC`（qperf.c:591-595、rdma.c:770 等），老 libibverbs 无符号不编；±RDMA 让文档同构裁剪，--help 永不展示跑不了的测试。
**双建链路径**：rd_open（rdma.c:1485-1489）if/else 二选一，默认裸 verbs（rdmacm 缺失不阻断，configure.ac:6），`-cm` 才走 rdma_cm；代价是 ib_prep 手工状态机。
**REQ 发送权下放**：各线建链顺序不同（socket 先收数据端口、rdma 建 QP 前同步参数），集中发送须加特例。
**双许可**：GPLv2（COPYING）或 OpenIB BSD（条款在源文件头部 qperf.h:7-33；qperf.spec:5 写 `BSD 3-Clause, GPL v2`）。

## ⑦ 新人学习路径（按 tour 15 步）

第一遍骨架（t01-t04，半天）：README+help.txt 建认知 → configure.ac/Makefile.am 懂双形态 → 精读 qperf.h 结构体（唯一接口文档）。第二遍主流程（t05-t08）：support.c 的 send_recv_mesg/error → qperf.c 的 main→do_args→client/server 全链 → 跟一次 tcp_bw 看懂输出每列。第三遍按方向深入（t09-t13，各半天）：网络背景走 socket.c→rds.c；RDMA 背景直上 rdma.c——t11 建链（rd_open/ib_open/ib_prep 最难）→ t12 数据面（rd_post_send/rd_poll/rd_client_bw/rd_pp_lat_loop 四函数即引擎内核）→ t13 入口矩阵。收尾 t14-t15 看双生成器与双许可。实验：双终端 `qperf`+`qperf localhost tcp_bw`，再 `-oo msg_size:64:64K:*4 rc_bw`。

## ⑧ 已知坑与勘误（全部源码实证）

1. **版本宏漂移**：qperf.c:63-65 为 0/4/**11**，configure.ac:1 与 qperf.spec:3 均为 **0.4.10**——README:7-12 自定的三处同步规则仓内未遵守。握手只比对 maj/min（qperf.c:1364），混跑不报错。
2. **COPYING 与实际双许可不符**：COPYING 仅 GPLv2 全文，BSD 条款只在源文件头部（qperf.h:7-33），权威是 qperf.spec:5。
3. **死原型**：qperf.h:257 `check_remote_error` 与 qperf.h:308-309 `run_client_bug`/`run_server_bug` 只声明无定义，勿找实现。
4. **头文件注释漂移**：RDS 四原型（qperf.h:283-286）挂在 "Socket tests in socket.c" 注释块（qperf.h:281）下，实际在 **rds.c**。
5. **configure.in 旧命名**：README:9 与 cleanup:30,36 仍写 configure.in，实际文件是 configure.ac。
6. **图谱摘要勘误**：rd_open **不是**"rdma_cm 失败回退 verbs"——rdma.c:1485-1489 纯 if/else 二选一（--use_cm，默认 verbs），无回退；引用图谱 L12/t11 摘要以此为准。
7. **qperf.spec 是生成物却入库**：由 configure 从 spec.in 实例化（configure.ac:9），刻意入库供 OFED；改版本号须最后改否则被 cleanup 删（README:11-12）。
8. **quit 即远程关服**：`qperf host quit` 终结 server（run_server_quit qperf.c:1778），自动化脚本慎用。
9. **风格分裂**：rds.c tab 缩进+K&R 紧凑，其余四空格——判读 blame 时注意。

---

*onboarding 子代理 · 2026-11-11*
