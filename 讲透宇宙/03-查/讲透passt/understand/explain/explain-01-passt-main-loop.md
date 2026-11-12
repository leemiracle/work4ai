# explain-01 · passt.c：守护进程骨架与主事件循环

## 1. 角色定位

`passt.c`（464 行）是整个守护进程的入口与骨架。passt 与 pasta 两个二进制其实是同一份代码——`Makefile` 里 pasta 只是 passt 的符号链接别名，靠 `argv[0]` 区分模式（`passt.1` 手册同时覆盖两模式）。这个文件做三件事：把进程带到一个"干净、无特权、可以安全跑主循环"的状态；初始化全部子系统（flow 表、tap 后端、TCP/UDP/DHCP/NDP、pcap、repair 通道）；然后进入永不到达出口的 `epoll_wait` 循环，把每个就绪 fd 分发给对应协议处理器。文件头注释（`passt.c:14-19`）一句话讲清本质：从 AF_UNIX socket（passt 模式）或 tap 设备（pasta 模式）抓以太网帧，为每个 TCP/UDP 五元组建 socket，做连接跟踪并转发；socket 收到的包反向送回 guest。

要理解分发逻辑，必须配两份小头文件：`epoll_type.h` 枚举全部 19 类 fd（堪称架构地图，每加一类事件源都要在这里挂号）；`epoll_ctl.h:30-44` 的 `union epoll_ref` 把 `epoll_event.data` 这 8 字节拆成位域——`type:8` + `fd:24` + 4 字节协议私有载荷（flow 索引/监听引用/vhost 队列号等），一次 `epoll_wait` 返回就同时拿到"这是什么 fd、它在哪个流上"。这是 passt 单循环设计的关键：不用任何额外查找结构，事件自带路由信息。

## 2. 内部结构

全局状态极简：`passt.c:63` 定义唯一的大缓冲 `pkt_buf`（对齐到 PAGE_SIZE，`main()` 里 `passt.c:376` 用 `madvise(MADV_HUGEPAGE)` 贴大页）；`passt.c:65-73` 定义全局唯一 `struct ctx passt_ctx`，所有 fd 初始化为 -1。注意 ctx 是全局而非堆分配——迁移/重配置代码可以直接索引它。

按调用顺序过一遍关键函数：

- `main()`（`passt.c:333`）：入口。`passt.c:345` `arch_avx2_exec()` 先判断能否 exec AVX2 变体二进制；`passt.c:347-348` 立即 `isolate_initial()` + `isolate_fds()`——在任何解析之前先关掉多余 fd，这是"尽早丢特权"哲学的第一步。`passt.c:350-357` 把 0/1/2 补上 /dev/null（守护进程化前防 fd 0 被当成套接字用）；`passt.c:365` `conf_mode()` 只解析模式（passt 还是 pasta）， pasta 模式要装 SIGCHLD handler（`passt.c:367-371`，因为 pasta 会 fork 出 reaper）；`passt.c:376-388` 建 epollfd、把 RLIMIT_NOFILE 顶到 max（连接数上限在这里一次性抬高）；随后 `conf()`（`passt.c:392`）完成全部配置与地址探测，`tap_backend_init()`（`passt.c:397`）建立 guest 侧接口，`flow_init()`/`fwd_scan_ports_init()`/`udp_init()`/`tcp_init()`（`passt.c:404-408`）依次起各协议。`passt.c:426-434` 是 fork 沙箱化的分界：`isolate_prefork()` 在 daemonize **之前**执行（此时还能用 ns 能力），`__daemon()` fork 后 `isolate_postfork()`（`passt.c:449`）做最后收窄。`passt.c:453-463` 就是主循环本体：`epoll_wait` 超时取 `TIMER_INTERVAL`（`passt.c:60-61`，三个定时器周期的最小值），唤醒后交给 `passt_worker`，`goto loop` 永不返回。
- `passt_worker()`（`passt.c:229`）：事件分发核心。先 `clock_gettime(CLOCK_MONOTONIC)` 取统一时间戳 `now`（全循环共享，避免各 handler 重复取时间），然后对每个事件把 `events[i].data.u64` 重释为 `union epoll_ref`（`passt.c:240`），`switch (ref.type)` 分发到 19 个 handler（`passt.c:247-308`）：tap 三种后端（TAP_PASTA/TAP_PASST/TAP_LISTEN）、TCP 四类（连接/连接-splice/监听/定时器）、UDP 两类、ping、vhost-user 两类（CMD/KICK）、repair 两类、netlink 邻居、配置 socket 两类、pasta ns 退出监视两类。每类事件计数进 `stats.events[]`（`passt.c:309`）。事件排空后跑 `post_handler()`（`passt.c:313`）——TCP 延迟任务、flow 定时器、端口扫描、NDP 定时器都在这里周期推进；最后 `migrate_handler()`（`passt.c:315`）驱动热迁移状态机。
- `post_handler()`（`passt.c:112-122`）：`tcp_defer_handler` + `flow_defer_handler` + `fwd_scan_ports_timer` + `ndp_timer` 四件周期任务，用 `no_tcp`/`no_ndp` 开关短路。
- `random_init()`（`passt.c:128-138`）：`raw_random()`（getrandom）灌 `c->hash_secret`（SipHash 流表哈希种子——防哈希碰撞 DoS）并 `srandom()`。
- `exit_handler()`（`passt.c:169-174`）：SIGTERM/SIGQUIT 统一走 `passt_exit(EXIT_SUCCESS)`；头注释 `passt.c:164-165` 留着一个未解之谜——unshare PID ns 后 SIG_DFL 不生效的 TODO。
- `print_stats()`（`passt.c:182`）：`--stats` 选项的表格打印，每 `c->stats` 秒一行，每 20 行重打表头（用空格画对角线表头，`passt.c:201-214`）。

## 3. 外部连接

依赖（从 `#include` `passt.c:39-56` 核实）：几乎所有子系统头——`isolation.h`（沙箱）、`conf.h`（配置）、`pasta.h`、`tap.h`、`tcp_splice.h`、`vu_common.h`、`migrate.h`、`repair.h`、`netlink.h`、`epoll_ctl.h`。反向依赖几乎为零：`main()` 不被任何文件调用，但 `proto_update_l2_buf()`（`passt.c:154`）被 `tap.c` 的 `tap_add_packet()` 在学到新 guest MAC 时回调——这是少数"主文件提供库函数"的反向边。`epoll_type_str[]`（`passt.c:75-95`）与 `epoll_type.h` 的枚举用 `static_assert`（`passt.c:96-97`）锁死同步，加类型漏改字符串会直接编译失败。

## 4. 数据流

一次 qemu 里 guest 发 TCP 数据包的完整旅程：guest virtio-net → qemu 把帧加 4 字节长度前缀写入 UNIX socket → epoll 唤醒，`ref.type == EPOLL_TYPE_TAP_PASST` → `tap_handler_passt()` → `tap_passt_input()` 解帧入池 → `tap4_handler()` 按五元组归并 → `tcp_tap_handler()` 建/查流表项、写 socket。反向：对端 socket 可读 → `EPOLL_TYPE_TCP` → `tcp_sock_handler()` 读数据、构造带 L2 头的帧 → `tap_send_frames()` sendmsg 回 qemu。主循环本身只是"路由器"：它不知道任何协议细节，只认 `ref.type`。

## 5. 设计决策

文件头 `passt.c:3-7` 的双关命名（PASST/PASTA 递归缩写）暗示了核心决策——**一份代码两种模式**，靠 `c->mode` 而非编译期分支区分，事件循环完全共享。其次是"先隔离后干活"：`isolate_initial()` 在 `main()` 第二行就执行（`passt.c:347`），连配置解析都发生在已收窄的环境里。第三，`#syscalls` 注释（如 `passt.c:167,325-331`）不是装饰——`seccomp.sh` 构建期扫描这些注释生成 seccomp 白名单，所以系统调用清单维护在"用它的函数"头上而非集中列表。第四，fork 时序精妙：daemonize 前后分别 `isolate_prefork/postfork`，把"需要特权的初始化"与"运行期"切在 fork 两侧。

## 6. 新人提示

入口阅读顺序建议：`epoll_type.h`（19 类 fd 地图）→ `epoll_ctl.h`（epoll_ref 位域）→ `main()`（初始化次序）→ `passt_worker()`（switch 即分发总表）。加新事件源的三步：`epoll_type.h` 加枚举、`passt.c:75` 的字符串表补条目（static_assert 会强制）、`passt_worker()` switch 加 case。坑：`TIMER_INTERVAL` 是三个定时器的最小值，改任何一个定时器周期都会间接改变主循环唤醒频率；`pkt_buf` 是全局共享的收包大缓冲，tap 路径与 splice/vu 路径对它的占用方式不同（vu 用自己的 mmap 内存，`tap.c:1597`），排查内存问题先分清模式。
