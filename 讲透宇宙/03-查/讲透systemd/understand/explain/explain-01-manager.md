# explain-01 · src/core/manager.c — Manager：PID 1 的事件循环心脏

## 一、角色定位

manager.c 是整个 systemd 的"操作系统内核调度器"式组件：`Manager` 对象（结构体定义在 manager.h:186）持有系统里全部 unit、job、事务与事件源，systemd（PID 1）与 systemd --user 各自实例化一份。它不实现任何具体 unit 类型的行为——那是各 `service.c`/`socket.c` 等 vtable 的职责——它只负责三件事：把 D-Bus/信号/IPC 等外部事件翻译成事务（transaction），把事务排成 job 队列，以及驱动一个单线程事件循环把队列排空。本仓 5692 行里几乎每个函数都是围绕这三件事的守卫与管线。它同时是 re-exec（升级自身不中断服务）与 serialization/deserialization（状态落盘恢复）的载体，`manager_startup()`（manager.c:2172）负责从旧进程序列化流里接生。

## 二、内部结构

核心数据结构全在 `Manager` 里（manager.h:186-300+）：
- `units` / `units_by_invocation_id` / `jobs` 三个 Hashmap（manager.h:191-194）：名字到对象的索引；
- 十余条 intrusive 双向链表头，每条是一个"待办队列"：`load_queue`（待加载）、`run_queue`（Prioq，manager.h:204，待执行 job）、`dbus_unit_queue`/`dbus_job_queue`（待发 PropertiesChanged 信号）、`gc_unit_queue`、`cgroup_realize_queue`、`stop_when_unneeded_queue` 等——这是理解 manager 的钥匙：**它是一台队列机器**，任何子系统想干活都把自己的对象挂进对应队列，再触发对应 dispatch。
- `sd_event *event`（manager.h:271）：libsystemd 事件循环实例。

初始化链路：`manager_new()`（manager.c:922）用 C 风格"构造器"把所有 fd 初始化为 `-EBADF`、job id 从 1 起（manager.c:962）、设置 Ctrl-Alt-Del 限速 2 秒 7 次（manager.c:987-988）；随后 `manager_setup_signals()`（manager.c:521）屏蔽并接管 30+ 个信号——SIGCHLD/SIGTERM/SIGHUP 加上 SIGRTMIN+0..29 全谱实时信号（SIGRTMIN+0 启动 default.target、+4 poweroff、+5 reboot、+7 soft-reboot，manager.c:548-555）——统一汇入 signalfd（manager.c:584），转成 fd 事件。`manager_setup_notify()`（manager.c:1093）绑定 `/run/systemd/notify` AF_UNIX 数据报 socket，开 SO_PASSCRED（manager.c:1130）与 SO_PASSPIDFD（manager.c:1135），配合 `manager_dispatch_notify_fd()`（manager.c:3108）接收服务进程的 READY=1/STATUS= 上报。

## 三、外部连接

- 上游：`main.c` 调 manager_new/manager_startup/manager_loop；`manager_add_jobs()`（manager.c:2315）是 D-Bus StartUnit 等入口的汇聚点，内部 `transaction_new → transaction_add_job_and_dependencies → transaction_activate`（manager.c:2351-2410）把依赖图折叠成一次性事务。
- 下游：unit.c（对象生命周期）、job.c（job_run_and_invalidate）、transaction.c（依赖求解）；`manager_dispatch_sigchld`（manager.c:3185）消费子进程退出，`watch_pids`/`watch_pids_more` 双 hashmap（manager.h:264-265）把 pidref 映射回 unit。
- 横向：sd-bus（systemd-hostnamed 式 API bus）、varlink（`manager_varlink_send_pending_reload_message`，manager.c:2922——新 RPC 面已并入同一队列节流机制）、cgroup、inotify 时区监视（manager.c:445）。

## 四、数据流

主循环 `manager_loop()`（manager.c:3636-3699）是一个严格的"队列清空后再睡"状态机：每轮先查 `event_loop_ratelimit`（manager.c:3651）防止死循环烧 CPU（超限则 sleep(1) 并告警），然后按固定顺序 dispatch 十条队列——load → gc_job → gc_unit → cleanup → cgroup_realize → start_when_upheld → stop_when_bound → stop_when_unneeded → release_resources → stop_notify → dbus（manager.c:3659-3690），任何一条有产出就 `continue` 重扫；全部排空才调 `sd_event_run(m->event, watchdog_runtime_wait(2))`（manager.c:3693）睡进 epoll。job 执行走 defer 事件源：`manager_setup_run_queue()`（manager.c:761）注册 `manager_dispatch_run_queue`，`manager_trigger_run_queue()`（manager.c:2900）按 Prioq 空非空切 ONESHOT 开关，dispatch 时 `while ((j = prioq_peek(m->run_queue))) job_run_and_invalidate(j)`（manager.c:2884-2888）。D-Bus 信号有双闸门：`MANAGER_BUS_BUSY_THRESHOLD` 队列深度阈值（manager.c:2959）限空间、`MANAGER_BUS_MESSAGE_BUDGET` 每轮条数预算（manager.c:2973）限时间——注释里明确"threshold 管内存、budget 管 CPU"（manager.c:2964-2972）。

## 五、设计决策

1. **单线程 + 全队列化**：拒绝多线程，所有并发来源（信号、子进程、socket、inotify）都被 sd-event 归一成 fd 事件，跨子系统协调用"挂队列+触发 dispatch"完成，彻底消灭锁。代价是每轮 O(队列) 扫描，换来确定性顺序。
2. **事件优先级分层**：notify（EVENT_PRIORITY_NOTIFY，manager.c:1151）先于 signal（manager.c:598 注释明言：要在 SIGCHLD 收尸之前拿到进程最后一条通知）、signal 又先于 cgroup 事件——用 sd-event 优先级编码了"进程临终语义"的因果序。
3. **限速内建**：事件循环本身（manager.c:3651）、Ctrl-Alt-Del（manager.c:988）、dump（manager.c:968）三处 RateLimit，体现"PID 1 必须自保"的防御性编程。
4. **GC 用 mark-and-sweep**：`unit_gc_mark_good`/`unit_gc_sweep`（manager.c:1356/1367）对引用计数归零候选做可达性判定，避免依赖环导致 unit 永不释放。
5. **职责剥离**：exec 细节全部移入 systemd-executor 子进程（`executor_fd`，manager.c:970；`pin_executor_binary()`，manager.c:898）——PID 1 只传参数不碰 fork 细节，是近年最重要的瘦身。

## 六、新人提示

读这份文件的正确顺序：先 manager.h:186 的结构体注释（每个字段都有用途说明），再 manager_loop()（manager.c:3636），最后按队列名反查各 dispatch 函数。调试利器是 SIGRTMIN+22（动态开 LOG_DEBUG）与 SIGUSR2（dump 全部状态到 journal），两者都在 `manager_dispatch_signal_fd()`（manager.c:3307）里处理。注意 `manager_dispatch_dbus_queue` 里 api_bus 未就绪时的 reload 回复保序窗口（manager.c:2937-2946 注释），这是历史上真实 bug 的化石。改代码时牢记：任何新异步动作都应建模成"挂某条队列"，而不是在回调里直接递归干活——递归会破坏队列机的事务性。
