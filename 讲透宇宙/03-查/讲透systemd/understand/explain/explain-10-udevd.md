# explain-10 · src/udev/udevd.c + udev-manager.c — udev 守护：事件队列与 worker 进程池

## 一、角色定位

systemd-udevd 是设备事件的中枢：监听内核 netlink 的 uevent，按 udev 规则（.rules 文件）处理——改名（eth0→ predictable names）、建符号链接 /dev/disk/by-*、设权限、触发 follow-up，最后把"设备已处理完"广播给全系统（networkd、storage 栈都在等它）。本仓是两层结构：udevd.c 仅 91 行的进程壳（`run_udevd`，udevd.c:28）——必须 root（42）、umask 022（47）、MAC 初始化（49）、提前 dlopen 五个重库防 fork 后缺页停顿（60-65，注释明言"before we fork any workers"）、可选 daemonize fork（67-88）；事件引擎全在 udev-manager.c（1558 行）：单线程事件循环 + **每事件一个一次性 worker 进程**的两级架构。规则匹配本身不在守护进程里跑——spawn 出的 worker（udev-worker.c）加载规则独立执行，守护进程只管排队、封锁依赖与生命周期。

## 二、内部结构

`manager_main()`（udev-manager.c:1476）装配一切：cgroup 委派检测——若自己跑在被委派的 /udev 子 cgroup 里，就建平级 workers cgroup，之后可用 cgroup.kill 原子清场（1486-1507）；事件循环与六个源：kernel netlink 监视（manager_start_device_monitor:1521，回调 on_uevent）、worker 汇报 socket（1529，on_worker_notify）、varlink 服务（1517，io.systemd.udev 管理/内省面）、inotify 设备监视（1525）、信号、post 源（1308）。规则只在启动/reload 时加载一次（udev_rules_load:1537），静态设备节点权限先行（1541）。就绪通知后有个关键细节：先从 fdstore 摘掉 event-serialization fd 再开始处理（1551），防止重执行时同一批序列化事件被处理两遍。队列语义核心在 Event 对象的三个字段：seqnum（内核序号，保序依据）、blocker（被谁挡住）、state；`event_find_blocker`（639）定义冲突关系——同 syspath、devpath 前缀父子（`devpath_conflict`：626，一个字符一个字符比到分叉再判 '/'）、改名前后路径（656-657）、同 devnode（658）四者其一即互斥。

## 三、外部连接

上游：内核 uevent（netlink KOBJECT group）；systemd 的 fdstore（socket activation + 重执行事件接续：manager_serialize_events:961 / deserialize:1001）。下游 worker：`event_run()`（589）遍历空闲 worker，用 device_monitor_send 把事件塞给它（600）；无空闲且未达 children_max 就 `worker_spawn`（619→523）——worker 与守护进程间两条通道：继承的 monitor socket 收事件、pidfd+notify socket 回报（on_worker_exit:442 收 SIGCHLD，on_worker_notify:1137 收字符串命令，如 INOTIFY_WATCH_ADD 请守护代挂 inotify 再 sigqueue 结果回 worker，1148-1175——worker 在自己的 mount namespace 里挂不了主 namespace 的 watch，必须回 host 侧代劳）。对外协作：/run/udev/queue 文件（1249/1265 建删，boot 进度条就靠它）；varlink 面给 udevadm monitor/info 的程序化替代。

## 四、数据流

事件主循环：netlink 到达 → `on_uevent`（1063）打 trace point、建 queue 文件、`event_queue_insert`（872）按 seqnum 插队、并对该设备相关已锁事件重排（1073）→ post 源驱动 `on_post`（1308）：先 requeue 被锁事件（1316），再 `event_queue_start` 尝试派发（1321）——对每个队首事件查 blocker（639），无人挡且 `manager_can_process_event`（673，children_max 内或有空闲 worker）就 `event_enter_locked`（819）加锁后 `event_run` 派给 worker。worker 处理完经 notify 回报，事件出队解锁，依赖它的事件在下一轮 post 获得放行。派不出去的事件留在队列等 SIGCHLD 腾名额（612-616 注释）。收敛路径（队列清空）：on_post 确认 monitor 无 pending、无合成 change 事件后，删 queue 文件、重置杀 worker 定时器（1326-1332）、等 worker 全部退出后对 workers cgroup 补刀（1336-1339）。退场协议 manager_exit（261）与重载 manager_reload（308，SIGHUP 重读规则）都经事件循环序列化过渡。

## 五、设计决策

1. **每事件一进程的故障隔离**：规则文件是第三方代码（厂商 udev 规则质量参差），崩了只死一个 worker（worker 超时还有 warning→kill 双定时器：367/379）；守护进程永不执行规则。代价是 fork 开销，用"worker 空闲复用 + children_max 池上限"（673）平衡。
2. **seqnum 保序但仅按需串行**：无冲突事件全并行，冲突判定只看 devpath 拓扑（626-637），既保住"同设备事件不乱序"的硬语义，又不让整条队列退化为单线程。
3. **锁在事件上而非设备上**（819 event_enter_locked）：设备对象生命周期与事件解耦，改名场景（devpath_old 也算冲突，656-657）天然正确。
4. **重执行安全**：事件队列可序列化进 fdstore（961），升级 udevd 不丢事件；1551 的"先摘 fd"防重复消费。
5. **宿主侧代办模式**（1148-1175）：worker 受限环境做不到的事（host inotify）通过 notify 字符串协议回托守护进程——RPC 粒度小而明确。

## 六、新人提示

排查设备问题三条命令一条线索：`udevadm monitor`（看事件进出）、`udevadm info /dev/sda`（看最终属性）、journal 里 udevd 的 "SEQNUM= blocked by SEQNUM="（udev-manager.c:661）——后者直接指认封锁依赖链，卡住的大多是某个永不返回的第三方规则（用 `udevadm test` 本地复现）。调规则永远 `udevadm test --action=add` 干跑，别在真机上反复触发热插拔。理解并发模型记住一句：**worker 并行、同设备串行、守护只排队**。children_max 默认随 CPU 数，慢规则堆积时队列文件存在即"还在处理"（boot 卡住先查 `ls /run/udev/queue` 是否消失）。Kylin 工作区提示：麒麟设备命名策略改动落在 99-*.rules 时，注意 devpath_conflict 的前缀语义——对同一路径的连续 change 事件会天然串行，新规则里 ifup/down 触发的时间假设要按此校正；国产存储多路径设备常见"同 devnode 多 devpath"，658 的判据已覆盖，但自定义标签规则仍要防重复触发。
