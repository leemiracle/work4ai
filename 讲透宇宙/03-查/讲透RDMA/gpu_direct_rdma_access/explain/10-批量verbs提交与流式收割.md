# 10 批量 verbs 提交与流式收割：数据面的账本与节奏

> 对应 tour 第 12 步「一发一收：批量 verbs 提交与流式完成」。源码锚均对 HEAD `a99d506` 核实。

## 一、角色定位

`rdma_exec_task`（gpu_direct_rdma_access.c:889-1006，118 行）与 `rdma_poll_completions`（:1422-1548，127 行）是数据面的心脏，也是第 8 篇 submit 链的终点站。前者把一次应用任务编排成 verbs-ex 批量域上的若干 WR 一次性敲给硬件；后者把 CQE 流翻译回应用语义。两函数之间隔着一本**应用层账本**——`wr_id` 虚拟化与发送队列信用，这是本仓数据面最值得偷师的设计：CQE 携带的不是应用请求号而是槽位号，账本负责双向翻译与资源归还。

它们只在 server 进程被调用（server.c:370、380），client 的世界（第 8 篇）里没有这两个名字。

## 二、内部结构

常量体系先行（gpu_direct_rdma_access.c:66-72）：`CQ_DEPTH 640`、`SEND_Q_DEPTH 640`（两者相等，CQ 容量按"SQ 打满且全信令"的最坏情形配）、`COMP_ARRAY_SIZE 16`（单次收割上限）、`WR_ID_FLUSH_MARKER UINT64_MAX`（第 11 篇的哨兵）。`MAX_SEND_SGE 10` 在公共头（gpu_direct_rdma_access.h:45）——每 WR 最多挂 10 个 SGE。

账本三件套住在 rdma_device 里（gpu_direct_rdma_access.c:122-124）：`app_wr_id[SEND_Q_DEPTH]`（每槽一条 `wr_id_reported`：wr_id/num_wrs/flags，:82-86）、`app_wr_id_idx`（环形分配游标）、`qp_available_wr`（剩余 WR 信用）。flags 只有一个语义位 `WR_ID_FLAGS_ACTIVE`（:78-80）——槽位是否持有未完结任务。

exec_task 的骨架：算 required_wr（:893，`(iovcnt + MAX_SEND_SGE - 1) / MAX_SEND_SGE`，无 iov 时为 1）→ 查信用（:894-898）→ `ibv_wr_start` 开批量域（:905）→ 占槽记账（:920-934）→ 按"有无 gather list"二选一组装（:938-988）→ `ibv_wr_complete` 敲门铃（:992）。

## 三、外部连接

提交侧用的是 verbs-ex 批量接口族：`ibv_wr_start`/`ibv_wr_complete`（gpu_direct_rdma_access.c:905、992）括起一个原子提交域，域内动词只在 complete 时一次性下发——对比逐个 ibv_post_send，省了每 WR 一次的锁与门铃。域内三步曲：动词（`ibv_wr_rdma_read|write`，:951、978——函数指针在 :899-901 按任务标志选定）→ 数据源（`ibv_wr_set_sge_list` 多段 :962 / `ibv_wr_set_sge` 单段 :983）→ DC 目的地（`mlx5dv_wr_set_dc_addr`，:969、987，连 AH+DCTN+DC_KEY 三件套）。这个白名单在 QP 创建时就已声明（第 9 篇 :804-805）。

收割侧有两套实现，编译期二选一：默认路径用 `ibv_poll_cq` 批量拉（:1527）；`PRINT_LATENCY` 路径用 `ibv_start_poll`/`ibv_next_poll`/`ibv_end_poll` 流式拉（:1440、1516、1522）并顺路读完成时间戳（`ibv_wc_read_completion_ts`，:1460）。开关在 Makefile：`make PRINT_LAT=1` 追加 `-DPRINT_LATENCY`（Makefile:15-19）——README 没有记载这个构建维度，属于"源码里长出来的"实验功能（第 12 篇对照清单的一项）。

## 四、数据流

一次任务穿越账本的完整流水：

1. **占槽**：`wr_id_idx = app_wr_id_idx++`（环形回绕，:920-923，注释自嘲 "should be atomic operation"——单线程 demo 的诚实）；槽位写入 `{应用 wr_id, required_wr, ACTIVE}`（:932-934），信用 `qp_available_wr -= required_wr`（:931）。
2. **wr_id 掉包**：`qpex->wr_id = (uint64_t)wr_id_idx`（:936）——CQE 回来时带的只是这个 640 以内的索引，应用号藏在账本里。
3. **组装与信令**：多 SGE 路径 while 循环按 MAX_SEND_SGE 切片（:944-970），每片一个 WR；`wr_flags` 只有**最后一个 WR** 置 IBV_SEND_SIGNALED，中间片全 0（:946）——非信令 WR 不产 CQE，于是 25 个 SGE 的任务 = 3 个 WR = **1 个 CQE**。远端地址随片推进（`curr_rem_addr += sg_list[i].length`，:957、941）。单段路径（:971-988）直接 SIGNALED，长度取 `rem_buf_size`（:983，即扣除 offset 后的远端剩余尺寸）。
4. **敲门**：`ibv_wr_complete`（:992）一次下发全部 WR。
5. **对账**：收割时按 `wc[i].wr_id`（即槽位号）反查账本（:1538-1543）：ACTIVE 位校验→清位→信用 `qp_available_wr += num_wrs` 归还（:1540）→向应用上报 `{原 wr_id, status}`。调用方 server 每迭代至少等 1 个事件（server.c:379-382，本地数组 10 槽、实取上限受 COMP_ARRAY_SIZE=16 与传参 10 双闸，:1428-1431）。

账本闭环：信用在提交时扣、在完成时还——这就是**应用层流控**，深度用尽时 exec_task 直接拒绝（:894-898）而不是让硬件排队失败。

## 五、设计决策

- **wr_id 为什么要虚拟化**：verbs 的 CQE 只回传 64 位 wr_id，若直接放应用请求号，收割时要靠应用自己维护"号→任务"映射，且多 WR 任务（一请求多 CQE）无法聚合。槽位号方案让反查变 O(1) 数组索引，`num_wrs` 字段把"一个应用请求占几个 WR"的答案随槽携带——信令优化（只标最后 WR）与记账归还（一次还清 required_wr）都建立在这层间接上。
- **信令只挂末 WR**：CQE 生成率从"每 WR 一个"降到"每任务一个"。对 10MB 大消息按 10 SGE×1024 段切的任务，CQE 压力降一个数量级，poll 循环（server.c:379）也更短。代价：错误冲刷时按 verbs 规范**所有**已提交 WR（含非信令的）都会吐出 CQE——此时同一槽位会收到多个 CQE，第一个清掉 ACTIVE 位后，后续的同槽 CQE 被 :1538 的 ACTIVE 检查静默丢弃。这个 flag 的真实身份是**冲刷去重位**，不只是"有效位"。
- **流式 poll 的意义**：ibv_poll_cq 每次调用都要带 wc 数组出入内核驱动；start_poll/next_poll 模式拉住 CQ 游标逐个消费，配时间戳扩展（IBV_WC_EX_WITH_COMPLETION_TIMESTAMP，:571）做 HCA 时钟域的时延测量（换算用 hca_core_clock_kHz，:676、1092-1104）。这是样例里唯一的性能观测钩子。
- **单段路径取 rem_buf_size 当长度**：无 gather list 时传输长度完全由"远端描述"决定（:983），本地缓冲只是起点（恒为 buf_addr，:1354）——尺寸契约压在凭据串一侧，第 8 篇的 buff_size_validation（debug 模式）就是对这笔账的预检。
- **CQ_DEPTH = SEND_Q_DEPTH**：等深配比让"CQ 溢出"在数学上不可能（最坏情形每 WR 一个 CQE 也装得下），省掉 CQ 满错处理——又一处"用容量换代码"的样例哲学。

## 六、新人提示

1. **PRINT_LATENCY 分支有潜伏编译错误**：`rdma_dev->app_wr_id[wc[i].wr_id].flags = 0`（gpu_direct_rdma_access.c:1453）引用的 `wc` 与 `i` 只在 #else 分支声明（:1524-1525）——`make PRINT_LAT=1` 会在 1453 行炸掉（本机无 OFED 头文件无法实测编译，结论来自作用域静态分析）。想用延迟测量先修这一行成 `cq_wr_id`。
2. **同分支还有 perror 标签错**：next_poll 失败打印 "ibv_start_poll"（:1517-1518），复制粘贴痕迹，排障时别被日志带偏。
3. **mmin 宏没加括号**：`#define mmin(a, b) a < b ? a : b`（:74）——`mmin(x,y)+1` 会展开成 `x<y?x:y+1`。现仓唯一调用点（:945）直接赋值所以无害，但复用这个宏前先补括号。
4. **槽位号当索引用**：`wc[i].wr_id` 直接做数组下标（:1538）无边界检查——安全性由 :936 只写入 <SEND_Q_DEPTH 索引保证。若有人把 qpex->wr_id 改成别的值（比如塞应用号），这里就是越界读，改动前想清楚。
5. **信用拒绝不是错误重试**：required_wr 超可用信用时 exec_task 直接返回 1（:894-898），上层（server.c:370-373）把它当致命错误走清理——demo 不会遇到（每迭代先收割再提交），但复用库做流水线时会撞上：正确姿势是先 poll 攒信用再提交。
