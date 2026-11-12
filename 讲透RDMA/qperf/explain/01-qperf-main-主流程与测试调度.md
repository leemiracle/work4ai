# 01 qperf 主流程与测试调度（qperf.c）

## 一、角色定位

qperf.c（2868 行）是整个工具的"操作系统内核"：它不实现任何具体网络测试，而是负责四件事——解析命令行、决定本进程是 client 还是 server、建立 TCP 控制通道、把控制权移交给 `Tests[]` 表中对应的测试函数对。socket.c/rds.c/rdma.c 三条传输线全部以"插件"姿态挂在它定义的 `TEST` 方法表（qperf.c:139-143）之下。读懂 qperf.c 的 main→do_args→client/server 分叉→run_test 分发这条主线，是理解其余 2000 行代码的前提。

版本三连宏位于 qperf.c:63-65：`VER_MAJ 0 / VER_MIN 4 / VER_INC 11`，即 0.4.11。注意它与 configure.ac:1 的 `AC_INIT(qperf, 0.4.10, ...)` 不一致——源码版本宏比构建系统新一位，README"Changing version"一节要求四处同步改版本（qperf.c/configure.in/qperf.spec），此处显然漏改了 configure.ac，这是仓库已知的版本宏漂移。

## 二、内部结构

**入口只有三行**（qperf.c:600-607）：

```c
main(int argc, char *argv[]) {
    initialize();
    set_signals();
    do_args(&argv[1]);
}
```

- `initialize()`（qperf.c:613-627）把 RemoteFD 置 -1、校验 ParInfo 表与 PAR_INDEX 枚举严格同序（错序即 `error(BUG, ...)`）、打开 `/proc/stat` 常驻 fd、缓存 CPU 数与时钟频率——"表序即枚举序"的自检是全库第一个防御性设计。
- `set_signals()`（qperf.c:674-690）注册四组 SA_SIGINFO 处理器：SIGALRM→`sig_alrm`（计时结束，置 Finished）；SIGPIPE 也挂 sig_alrm（对端崩了别死）；SIGQUIT→`sig_quit`（子进程请父进程退场）；SIGURG→`sig_urg`（TCP 带外数据，见 06 篇）。

**client/server 判定是隐式的**，藏在 `do_args()`（qperf.c:726-767）里：扫描参数时只要碰到一个非 'S' 前缀类型的选项（qperf.c:738-739）或一个非选项裸参数，`isClient` 就置 1。全部参数扫完：

- `!isClient` → `server()`（qperf.c:757-758）：进入永久监听循环；
- isClient 但没指定测试 → 三连错误提示（qperf.c:759-766），其中"你用了 client 专属选项却没给服务器名"的场景单独给了引导文案。

**server 循环**（qperf.c:1336-1380）是教科书式的 accept-fork 模型：`server_listen()` 用 AI_PASSIVE+AF_INET6 绑定 19765 端口（DEF_LISTEN_PORT，qperf.c:76）；accept 后 `fork()`，父进程关 RemoteFD 等子进程退出。版本协商分两步收（qperf.c:1361-1366）：先收前 4 个头部字段解版本，maj/min 不符即调 `version_error()`（qperf.c:1387-1409，明确告诉用户该升级哪一端），过关才收剩余 REQ。子进程用 `(test->server)()` 完成分发后 exit(0)，回到 accept 循环。

**client 侧**`client(TEST *test)`（qperf.c:1466-1496）做对称的准备工作：重置 inuse 标志、未显式设 no_msgs 时给 L/R_TIME 填默认 2 秒（DEF_TIME）、填 RReq 版本三连与 `req_index = test - Tests`（指针差即测试下标，qperf.c:1488）、`printf("%s:\n", TestName)` 先打测试名，再 `(*test->client)()`。测试函数内部会各自调用 `client_send_request()`（qperf.c:1502-1546）真正发起连接：getaddrinfo 遍历地址族逐个 connect，失败隔 1 秒重试直到 ServerWait 超时；成功后 `remotefd_setup()`（qperf.c:1552-1561）设非阻塞并 F_SETOWN 使 SIGURG 定向送达。

**测试节奏由三个全局函数统一**：`sync_test()`（qperf.c:1793-1798）= 控制通道同步一次 + `start_test_timer(Req.time)` 起闹钟；`sig_alrm`→`set_finished()`（qperf.c:1852-1857）置 volatile Finished 并冻结结束时刻；`stop_test_timer()`（qperf.c:1837-1846）复位。start_test_timer 里有一段 SLES11 高精度定时器的注释（qperf.c:1817-1821）：interval 设 10ms 是为了第二次 SIGALRM 能把卡在系统调用里的循环踹醒——配合 set_finished 注释里"结束后的包要拒收以免作弊"的口径，可见计时精度是被认真设计过的。

## 三、外部连接

- **向 qperf.h**：所有跨文件契约（REQ/STAT/RES 结构、PAR_INDEX、extern 全局变量）都在 qperf.h:153-176/362-373 定义，qperf.c 是这些全局量（Res/Req/LStat/ServerName/RemoteFD/Finished 等，qperf.c:275-284）的定义点。
- **向三条传输线**：`Tests[]` 表（qperf.c:556-597）按字母序引用 socket 线 12 项 + `#ifdef RDMA` 包住的 22 项（qperf.c:569）+ `#ifdef HAS_XRC` 包住的 3 项（qperf.c:591-595）。传输线文件只暴露 `run_client_X/run_server_X` 命名对，本文件用函数指针调用，互相不知晓实现。
- **向 support.c**：错误处理 error/debug、编码 enc_int/dec_int、地址解析 getaddrinfo_port、消息收发 send_mesg/recv_mesg 全部外包。
- **向 help.c（构建产物）**：do_option 的 help 分支（qperf.c:858-874）按 category 检索 `Usage[]` 数组——该数组由 mkhelp 从 help.txt 生成，仓库中无 help.c（见 06 篇）。
- **向系统**：/proc/stat（CPU 时间采样）、/proc/cpuinfo（conf 测试读 CPU 型号）、itimerval（计时）、fork/waitpid（server 并发模型）。

## 四、数据流

一次 `qperf server01 tcp_bw` 的完整生命周期：

1. do_args 识别 "server01" 为 ServerName、"tcp_bw" 经 `find_test`（qperf.c:831-841）命中 Tests 表 → `do_loop` 无循环变量时直接 `client(test)`。
2. client 填 RReq（含 req_index）→ 测试函数 `run_client_tcp_bw` → `client_send_request`：connect、`remotefd_setup`、`enc_req(&RReq)`（qperf.c:2634-2659 逐字段小端编码）+ `send_mesg` 发出整个 REQ。
3. server accept 后 fork，子进程两步收 REQ、`dec_req_*` 解码、查表调 `run_server_tcp_bw`。
4. 双方各自 sync_test 同步起跑；数据面测完 `exchange_results()`（qperf.c:1581-1597）交换 STAT 结构（server 先发，client 收完回 sync）。
5. client 侧 `show_results` → `calc_results`（qperf.c:1874-1935，合并本地/远端 USTAT、算带宽时延与 CPU 成本）→ `place_show()`（qperf.c:2562-2610）统一列宽输出。

控制通道全程复用 RemoteFD 单条 TCP 连接；数据通道（TCP/UDP/SCTP/SDP/RDS socket 或 RDMA QP）由各测试线另行建立，端口经控制通道交换。

## 五、设计决策

- **角色判定靠选项类型而非位置参数**：'S' 前缀类型（Slp/Sdebug/Stime）是 server 也可用的，其余一律使进程成为 client（qperf.c:738-739）。这让 `qperf`（无参）与 `qperf -lp 2000`（自定义监听口的服务器）天然成立。
- **向后兼容表驱动**：`Renamed[]`（qperf.c:360-416）53 条旧选项映射，`find_option` 命中即打"obsolete"警告并翻译成新名（qperf.c:808-817）——十余年 CLI 演进靠一张 DICT 表消化。
- **版本协商只认 maj/min**：ver_inc 不参与判定（qperf.c:1364），对应 qperf.c:58-61 注释承诺——改 REQ 结构才动 VER_MIN。
- **展示层两段式**：view_* 先 place 进 ShowTable（256 槽），最后 place_show 统一算列宽再打印，使 loc_/rem_ 前缀、单位自适应（view_band qperf.c:2371-2398，nice_1024 qperf.c:2428-2450）与逗号分位（commify qperf.c:2813-2857）解耦于数值计算。
- **REQ 前 4 字段冻结**（qperf.h:148-151 注释）：ver_maj..req_index 不得移动，server 靠 `offset(REQ, req_index)` 分两段收包就是建立在这个布局保证上。

## 六、新人提示

- 读代码顺序：qperf.h 结构与 PAR_INDEX → 本文件 main/do_args/server/client 四函数 → 任一测试线（推荐 socket.c 的 tcp_bw，最短）→ calc_results。
- `#define test(n) { #n, run_client_##n, run_server_##n }`（qperf.c:555）是 token-pasting 宏，Tests 表里一行 `test(tcp_bw)` 同时生成名字字符串与两个函数指针——新增测试只需写好 run_client_X/run_server_X 并在此表加一行。
- run_client_conf/run_client_quit（qperf.c:1613-1630/1764-1771）是两个特殊"测试"：前者只交换 CONF 信息，后者经 server 端 `kill(getppid(), SIGQUIT)`（qperf.c:1785）让常驻 server 优雅退出——server 不是被 kill 的，是 quit 出来的。
- 勘误提醒：qperf.h:308-309 声明的 run_client_bug/run_server_bug 在全仓没有任何定义与调用（死原型）；configure.ac 停在 0.4.10 而源码已是 0.4.11，引用版本号时以 qperf.c:63-65 为准。
