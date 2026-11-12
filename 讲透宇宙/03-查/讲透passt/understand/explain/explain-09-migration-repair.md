# explain-09 · migrate.c + repair.c + passt-repair.c：TCP 连接热迁移

## 1. 角色定位

QEMU 热迁移虚拟机时，guest 内存、CPU 状态都能搬，但 passt 代理的 TCP 连接活在**宿主内核 socket** 里——序列号、拥塞窗口、发送/接收队列都是内核状态，普通进程读不出来也写不进去。这套三文件组合解决这个问题：`migrate.c`（313 行）定义迁移状态流的编解码框架（版本+阶段表）；`repair.c`（274 行）是 passt 侧的 helper 服务端；`passt-repair.c`（287 行）是**全仓唯一需要特权的独立二进制**（要 CAP_NET_ADMIN 才能操作 TCP_REPAIR），经 UNIX socket 用 SCM_RIGHTS 收 socket fd、代为 setsockopt(TCP_REPAIR)。链路全貌：qemu 迁移到 vhost-user 设备状态阶段 → 通过 device_state fd 把 passt 的状态流与 qemu 迁移流合流 → 源端 passt 经 repair 通道把连接转入 TCP_REPAIR 冻结态 → dump 全部内核 TCP 参数+队列数据 → 目标端 passt 重建 socket、回灌参数与队列。guest 全程无感知。

## 2. 内部结构

**migrate.c：框架层**。数据模型是"版本 → 阶段表"：`struct migrate_version`（migrate.h）持版本号+stages 数组；每个 `struct migrate_stage` 有 name/source/target 三元组。v2 阶段表（`migrate.c:107-124`）三步：①"observed addresses"——把学习到的 guest 地址/MAC（addr_seen/addr_ll_seen/guest_mac，`migrate.c:39-44` 的 packed 结构）原样搬运，目标端直接采纳（`seen_addrs_target_v2`，`migrate.c:86`），省去重新 ARP 学习；②"prepare flows"——`flow_migrate_source_pre` 只在源端跑（target=NULL），开启全表 repair；③"transfer flows"——`flow_migrate_source`/`flow_migrate_target` 对偶收发流表。版本协商遵循 vhost-user 惯例：header 带 magic（`MIGRATE_MAGIC 0xB1BB1D1B0BB1D1B0`，`migrate.c:30`）+ version + compat_version 三元组，`migrate_target_read_header()`（`migrate.c:185`）按 `[compat_version, version]` 区间匹配自己支持的版本；v1 的注释（`migrate.c:129-132`）是罕见的坦率：*"v1 was released, but not widely used. It had bad endianness for the MSS and omitted timestamps... we don't attempt to support compatibility"*——发布过但坏的版本直接放弃兼容。运行时编排在 `migrate_handler()`（`migrate.c:295`，由主循环每轮调用 `passt.c:315`）：device_state_fd 就绪则按 migrate_target 标志走 source 或 target，完事 `migrate_close()` 并记 `device_state_result`。

**repair.c：服务端**。`repair_sock_init()`（`repair.c:48`）listen `--repair-path` 指定的 socket（vu 模式在 `tap.c:1613` 起这个服务）。批量协议设计得很省：`repair_set()`（`repair.c:256`）攒 fd 进 `repair_fds[SCM_MAX_FD=253]` 数组，命令变化或攒满 253 才 `repair_flush()`（`repair.c:198`）——一次 sendmsg 带 SCM_RIGHTS 发一批 socket+一个命令字节（TCP_REPAIR_ON/OFF/OFF_NO_WP），helper 回显命令字节作确认（`repair.c:249-255`）。`repair_wait()`（`repair.c:160`）给 listen socket 设 10ms SO_RCVTIMEO 后直接同步 accept——迁移窗口里 helper 还没连上的竞态用短超时兜住。SCM_MAX_FD=253 的注释（`repair.c:36`，`passt-repair.c:45`）注明这是内核 include/net/scm.h 的常量，不在 UAPI 里，只能手工镜像。

**passt-repair.c：特权 helper**。`main()`（`passt-repair.c:144`）先自锁：`PR_SET_DUMPABLE=0` + 装构建期生成的 `filter_repair` seccomp（`:160-169`，比主程序白名单小得多——connect/setsockopt/recvmsg/sendmsg/stat 几个就够）。参数是 socket 路径或目录：目录则 `wait_for_socket()`（`:64`）inotify 等待 `*.repair` 文件出现（迁移时序上 passt 可能还没起完，:211-213 的 `ECONNREFUSED` 也循环重试）。主循环（`:220-286`）：recvmsg 收一批 fd+命令 → 校验命令合法性（只认三个 TCP_REPAIR 值，`:260-264`）→ 逐个 `setsockopt(SOL_TCP, TCP_REPAIR)` 后关掉自己的副本（`:268-278`）→ 回显命令。EOF 即退场。`:242-250` 有一段 CMSG_LEN 无逆公式的工程注释——靠穷举 1..253 找出 cmsg_len 对应的 fd 个数。

**flow.c 侧的编排**（迁移的"内容"层）：`flow_migrate_source_pre()`（`flow.c:1096`）先 `repair_wait` 再 `flow_migrate_repair_all(true)` 全表开 repair；`flow_migrate_source()`（`flow.c:1123`）先发流计数，然后一段自嘲注释（`flow.c:1146-1152` "HACK: local to local migrate will fail..."）解释为何要先关监听 socket（目标端要 bind 同样的端口），再两轮遍历：第一轮 `tcp_flow_migrate_source` 发 flow 表内存下的字段（失败且是第一条则 rollback 恢复运行，否则流已不一致只能 die，`flow.c:1160-1170`）；第二轮 `tcp_flow_migrate_source_ext` 发"扩展数据"（TCP_REPAIR 队列内容、时间戳、窗口参数，存于 `migrate_ext[FLOW_MAX]` 辅助数组 tcp.c:388）——长注释（`flow.c:1175-1181`）讲清时序约束：目标端要先有 socket 才能设 repair 参数，源端发完队列数据就关 socket 让目标端 connect。`flow_migrate_target()`（`flow.c:1217`）对称：读计数 → `repair_wait`+全表 repair → 逐流 `tcp_flow_migrate_target`（tcp.c:3805，重建 socket+bind+connect）→ 二轮 `tcp_flow_migrate_target_ext`（tcp.c:3876，回灌队列与窗口）。tcp.c 的 3077-4060 行是这套 dump/repair 原语族（`tcp_flow_dump_seq/repair_seq`、`tcp_flow_dump_sndqueue/repair_queue`、`tcp_flow_dump_wnd/repair_wnd`...每对函数对称成对），配合 64MiB 静态迁移缓冲（`tcp.c:371-374`）搬运 send/receive 队列。

## 3. 外部连接

migrate.c 被 vhost_user.c 调（`vu_init` 里 `migrate_init`；`vu_set_device_state_fd_exec`/`vu_check_device_state_exec` 处理 vhost-user 设备状态消息后 `migrate_request()`）；`vu_control_handler()` 尾部（vhost_user.c:1202-1214）据 `device_state_result` 判定迁移完成/退出。serialise.c 提供 `write_u32/read_all_buf` 等原语流。repair.c 的入口挂在 epoll（EPOLL_TYPE_REPAIR_LISTEN/REPAIR），passt.c 主循环分发。`linux_dep.h` 手工镜像的 `struct tcp_info_linux` 与 TCP_REPAIR 队列常量是防 uapi 漂移的配套（tour 描述里明确点名）。passt-repair 独立构建（Makefile 的 PASST_REPAIR_SRCS），发行版包里是单独二进制，libvirt/Podman 负责以特权拉起它。

## 4. 数据流

一次本机到本机的迁移：qemu `migrate` → 源 qemu 与 vhost-user 后端走到 SET_DEVICE_STATE_FD → 源 passt `migrate_request(fd, target=false)` → 主循环 `migrate_handler` → 发 header（magic/v2）→ 发 guest 地址 MAC → `flow_migrate_source_pre`：passt-repair 已连上 → 全表 socket 批量转 TCP_REPAIR_ON（内核冻结这些连接：不再响应网络、参数可读写）→ 关监听 → 逐流发 flow 字段+扩展数据（TCP_INFO 全参数、snd/rcv 队列原始字节，借 64MiB 静态缓冲）→ 源端关 socket。目标 qemu 带着同一份状态流到达 → 目标 passt `migrate_request(fd, target=true)` → 读回一切 → 新建 socket、bind 原地址端口、connect 对端 → 转 repair → 回灌队列与序号 → repair off，连接在目标内核里原地复活 → `vu_check_device_state` 回成功 → 源端 passt 收到 CHECK_DEVICE_STATE 确认后 "Migration complete, exiting"（vhost_user.c:1202-1214）。

## 5. 设计决策

**特权最小化的几何切分**是最大看点：TCP_REPAIR 需要 CAP_NET_ADMIN，而 passt 的卖点是无特权运行——解法不是给 passt 加能力，而是把"需要特权的 26 行 setsockopt"切成独立二进制，由有特权的父进程（libvirt）拉起，经 SCM_RIGHTS 传 fd 通信。特权面收窄到一个只能做三件事（ON/OFF/OFF_NO_WP）的哑助手，且它自己也装 seccomp+不可 dump。其二是**阶段表驱动的对称编解码**：source/target 函数对偶、按版本组织，新阶段加一行、新版本加一张表，版本协商协议与 vhost-user 设备状态迁移语义对齐。其三，**迁移窗口的失败语义分级**：flow.c:1160-1181 的注释把回滚能力切成三档——transfer 前可完整回滚、transfer 中第一条失败可回滚、队列数据阶段失败只能尽力而为——因为状态流一旦发一半就不可能重建，die 是唯一诚实选择。

## 6. 新人提示

测试这是唯一需要两实例+qemu 的功能：test/lib/setup 的 `passt_in_ns`/迁移场景与 `./ci` 里有完整编排，手工验证照抄。改协议时三处联动：stages_v2 加阶段、source/target 成对实现、passt.1 的 `--repair-path` 文档；兼容旧版本先看 `migrate.c:129` 的前车之鉴（v1 的字节序教训）。坑：`flow_migrate_source` 先关监听再发包（`fwd_listen_close`，flow.c:1153），失败回滚后监听 socket 已丢——HACK 注释明说这个窗口，本地到本地迁移测试偶发 bind 失败是已知边界而非新 bug。passt-repair 的等待逻辑（inotify+ECONNREFUSED 重试）对启动时序敏感，调试时用 `--debug` 看 "Waiting for socket"/"Failed to connect" 日志定位卡在哪一段。
