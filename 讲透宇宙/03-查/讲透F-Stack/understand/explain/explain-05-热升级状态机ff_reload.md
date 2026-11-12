# explain-05 · 热升级状态机：lib/ff_reload.c（graceful reload 的仲裁层）

## 角色定位

ff_reload.c（2147 行）+ ff_reload.h（683 行）实现 v2.0 招牌能力"热升级不丢连接"的地基：nginx USR2 换代时，新旧两代 F-Stack 进程谁碰网卡、谁只排水，全由这里的共享状态仲裁。关键认知：**状态机本体不在本文件**——T0~T5 的 FSM 驻留在 app/nginx-1.28.0/src/event/modules/ngx_ff_reload.c（`ngx_ff_reload_fsm_event :99`，EV_HUP 进 T1、EV_GOLD_EXITED 触发 complete），ff_reload.c 提供的是"原语层"：共享块（struct ff_reload_state）、rx 交接互斥、T2 停车屏障、READY/心跳/drain 上报、跨 master 世代目录同步。设计极度克制——不发明 IPC、不建控制通道，一切仲裁都落在 fork 继承的匿名 mmap 里几个 uint32/uint64 字上（ff_reload.h:545 注释原话）。

## 内部结构

共享块 struct ff_reload_state（ff_reload.h:130-192）是核心数据结构：magic "FRLM"（`:49`）+ version 防脏映射；epoch 每次 reload 尝试自增；active_gen/target_gen 双世代（FF_RELOAD_GEN_MAX=2，`:54`）；ready[128] 每 worker 槽的 `(epoch<<32)|pid` 就绪字（`:146`）；rx_owner_gen/rx_stopped 两个词构成交接互斥（`:156`）；handover_epoch+rx_parked[128] 是 T2 屏障（`:165`）；fsm_state 镜像给观测（`:154`）；reserved[0..6] 有精确的用途表（`:168-180` 注释：[0.1]=drain 扩展块指针、[4]=rx 属主 epoch 对、[5]=kni 属主 epoch 对——只能经 helper 访问）。函数侧分五组：世代/epoch 存取（ff_reload_set_gen `:251`）、世代目录用户表（user_claim `:404`、ff_reload_gendir_user_add `:445`）、目录同步（ff_reload_dir_sync `:877`）、rx 交接（ff_reload_rx_release `:1431`/epoch 版 `:1479`/ff_queue_handover_mutex `:1522`）、T2 屏障（arm `:1591`/ack `:1619`）、master 编排（begin `:1896`/abort `:1915`/complete `:1938`）与心跳（tick `:2093`/sample `:2115`）。

## 外部连接

消费者全景：nginx master 的 FSM（ngx_ff_reload.c:117 调 ff_reload_master_begin、`:154` 调 complete、`:132` abort）；worker 侧 main_loop 每圈调 ff_no_hw_mode（ff_reload.c:1406）判"本代是否被停权"，其无同步版 `:1372` 被每包发送路径使用；ff_dpdk_if.c 的停车 ack（ff_reload_handover_ack）与心跳（tick/sample）直接嵌在主循环里。世代目录 ff_reload_gendir.c 是跨 master 的唯一权威（epoch→slot 映射、唯一硬件属主坐标、master 存活），由常驻 slim primary 建 hugepage memzone，ff_reload_dir_sync 把本 master 的仲裁词镜像进去——"只收窄不放宽"（`:1400` 注释），目录滞后最多损失一圈。drain 扩展块（FF_RELOAD_DRAIN_MAGIC "FRLD"，ff_reload.h:270）经 reserved[0.1] 挂接，ff_drain_ring/ff_flow_map 的进展都回报到它。工具面：ff_dpdk_if.c:3089 的 handle_reload_msg 只支持 FF_RELOAD_CMD_QUERY（其余一律 ENOTSUP，注释明令"新命令必须显式处理不许回声"）。

## 数据流

一轮 HUP 重载的时间线：master 收 EV_HUP→ff_reload_master_begin（`:1903-1906`：epoch++、target=active^1、reload_active=1，开窗）→fork 新代 worker→新代起来后 ff_reload_publish_ready（`:1962`：写 `(epoch<<32)|pid`，master 用 ready_matches 三元组核对槽位+pid+epoch）→T2 停车：master arm 一个新 handover_epoch（`:1600`）并令旧代 rx_stopped=1，旧代每个 worker 在"将跳过 rx/tx 的那一圈主循环里"ack（`ff_dpdk_if.c:3894`→ff_reload_handover_ack `:1619`）——ack 即铁证"本进程无在飞 rx_burst"；master 收齐所有存活旧代槽位才翻转 rx_owner_gen。翻转本身在旧代侧：ff_reload_rx_release（`:1453-1454`）先 rx_stopped=1 再 rx_owner_gen=to_gen，**顺序即安全**（`:1450` 注释：两写之间被采样的循环也已看到 stopped）。新代 ff_queue_handover_mutex（`:1564-1574`）自旋+sched_yield 有界等待属主到位后清 stopped 恢复收发。此后 T3 排水（旧代 no_hw 模式靠 drain ring 存活，见 explain-06），G_old 退出后 EV_GOLD_EXITED→complete（`:1945-1955`：active=kni_owner=rx_owner=target、stopped=0、关窗）。异常路径 abort（`:1921-1928`）把硬件还给仍在服务的 active 代——标记词全可逆。心跳兜底：rx 属主每圈 tick，非属主采样，整超时窗无推进即强制接管（ff_dpdk_if.c:4064-4082 调 reclaim_forced_add 让 master 弃这轮）。

## 设计决策

① **两词互斥胜过锁**：rx_owner_gen/rx_stopped 是普通原子字，无 memzone、无控制通道——fork 继承天然共享，崩溃进程不持锁；"never steal"（`:1552-1558`）保证同一队列上并发 rx_burst 不可能，且 GEN_MAX==2 时 BUSY 分支实际不可达、纯为未来扩世代数设防。② **epoch 标记一切**：READY 字、park ack 都带 epoch，中止轮的陈旧 ack 无需清扫即无害（ff_reload.h:172 注释）——免掉"谁来清共享数组"这个经典难题。③ USR2 路径（跨 master）比 HUP 多一层 users_proven_stopped（`:1460-1476`）：2ms 间隔轮询、reclaim_timeout 有界等待同坐标所有用户停证，超时则**拒绝并回滚停车**（`:1501-1505`）——"宁可继续服务也不共享队列"。④ FF_RELOAD_FAULT_INJECTION 故障注入钩子（flip_fail/flip_fail_once/mutex_timeout/ready_never/ready_delay，`:1433-1443/:1533/:1966`）与 tests/integration/test_graceful_reload.sh 配套，翻转失败时标记词不动、abort 回滚保持一致——可测性是设计出来的不是补出来的。

## 新人提示

理解本文件先背下三个词的生命周期：reload_active（窗口开关）、rx_owner_gen（谁可碰硬件）、rx_stopped（属主是否已停车）——ff_no_hw_mode（`:1406`）就是这三者的导出函数且"永不闩锁"（可逆 seam）。调试用 ff_reload_msg 工具查询 fsm_state/heartbeat；reserved[] 绝对不许直写（`:181` 注释）。读 nginx 集成时注意 master 无 EAL、读不了世代目录——它靠 peer_epoch/peer_gen 镜像（ff_reload.h:185-190）与 worker 的 dir_sync 间接知情，这条约束解释了很多"为什么由 worker 做"的怪设计。单测侧 tests/unit/test_ff_config.c 也引用这些符号做配置合法性检查，改结构体字段名记得同步。
