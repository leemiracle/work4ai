# explain-03 · 移植黏合双支柱：lib/ff_glue.c 与 lib/ff_kern_timeout.c（P0 定时器修复）

## 角色定位

这两个文件回答同一个问题："FreeBSD 内核源码凭什么能在用户态链接通过并正确运行？"ff_glue.c（1474 行）是符号级黏合——补齐 prison/ucred/copyin 这类内核代码默认存在的基础设施；ff_kern_timeout.c（1324 行）是行为级黏合——把 FreeBSD 的 callout 定时轮（tick-wheel）完整搬进用户态并由 ff_hardclock 驱动。后者还是本仓一次著名 P0 修复的现场：曾有一个 no-op 的 callout_when() 桩让全部 TCP 定时器静默失效，修复叙事写在 ff_stub_14_extra.c:147-157 的注释里，是"链接通过≠行为正确"的最佳教材。

## 内部结构

ff_glue.c 分三块：① jail/ucred 家族（prison_check_ip4 `:263`、jailed `:354`、priv_check_cred `:377`、crget/crhold/crfree `:870-905`）——全部退化为"无 jail、恒有权限"，ucred 只剩引用计数语义；② 内存访问桩（copyin `:610`/copyout `:617` 就是 memcpy——用户态没有用户/内核地址隔离，这是一次正统性坍缩：内核语义的"跨空间拷贝"变成普通拷贝）、copyinstr `:638`、copyiniov `:650`、subyte `:666`；③ SMP/sysctl 桩（smp_topo `:173`、procinit `:221`）与 ELF 重定位收尾（elf_reloc_late `:1445`）。ff_kern_timeout.c 则几乎是 FreeBSD kern_timeout.c 的原样移植：struct callout_cpu（`:166`，含 cc_callwheel 轮盘与 cc_exec_entity 执行态）、callout_reset_tick_on（`:727`）、_ff_callout_stop_safe（`:834`）、softclock/softclock_call_cc（`:592/:417`）都在，但 `__thread struct callout_cpu cc_cpu`（`:191`）和 `#define CC_CPU(cpu) &cc_cpu`（`:192`）这两个改动把"每 CPU 一个定时轮"偷换成"每线程一个定时轮"。

## 外部连接

ff_kern_timeout.c 的驱动链：ff_dpdk_if.c main_loop 按 TSC 节流调 ff_hardclock（`lib/ff_kern_timeout.c:1251`）→ atomic_add_int(&ticks,1) + callout_tick()（`:338`，扫轮盘桶发现到期项就 softclock）+ tc_ticktock。TCP 全部定时器（RTO/keepalive/2MSL/persist/delack）经 callout_reset_sbt_on→callout_when（ff_callout_sbt.h:26）解析成绝对 sbt 再 callout_sbt_to_ticks（ff_callout_sbt.h:58）折算轮盘 tick。特例是 ff_tcp_hpts_softclock（`:1299`）：注释（`:1275-1294`）解释了为什么必须从主循环直调——f-stack 里 swi_sched 是 no-op（ff_kern_intr.c）且没有 userret，两条原生驱动路径全断，BBR pacing 会中途卡死；这里故意绕过 hpts_that_need_softclock 宏门（少连接场景恒 0），直取函数指针。ff_glue.c 则被 freebsd/ 树里上百个 .c 隐式依赖，链接期才见分晓。

## 数据流

一次 RTO 定时器的完整旅程：tcp_timer_activate→callout_reset_sbt_on(flags=C_HARDCLOCK)→callout_when（ff_callout_sbt.h:26：用户态没有 hardclocktime 快照，改以 sbinuptime() 为基，sbt<tick_sbt 时抬到一 tick，向上取整把额外延迟封顶在一个 tick）→callout_sbt_to_ticks 折 tick→callout_reset_tick_on→callout_cc_add（`:385`）按 `c_time & callwheelmask`（`:333`）挂桶。ff_hardclock 每 tick 推进 cc_softticks（callout_tick `:351`），追上全局 ticks 时进 softclock（`:605`），桶内 `c_time != curticks` 的项跳过（轮盘回绕的同桶不同轮项），命中项经 softclock_call_cc 执行：先处理取消竞态（cc_exec_cancel，`:468`），再 THREAD_NO_SLEEPING 包住 c_func（`:499-503`），收尾处理 drain 回调与等待者。多线程模式下 ff_hardclock_worker（`:1270`）只推本线程轮盘——注释（`:1263-1268`）点明全局 ticks/timecounter 必须归主线程所有，否则 N 线程共享时基快 N 倍。

## 设计决策

① **P0 修复的本质**：旧 callout_when() 桩是空函数，*sbt_out 原样不动（tp->t_timers[] 恒 SBT_MAX），tcp_timer_next() 恒返 TT_N——链接器不报错、编译不警告、ping 却永远不通，因为没有任何 TCP 定时器被真正布防。修复把实现放进 ff_callout_sbt.h 单源头，让 tests/unit/test_ff_callout.c 用 host shim 编同一份代码（头注释 `:4-6`），从此桩与实现不会分叉；测试 TC-1 的注释（test_ff_callout.c:119）明确说"P0 桩曾让两个输出都不写"。② copyin/copyout 直接 memcpy 而非保留语义检查——用户态协议栈里调用者与被拷贝区同属一个地址空间，防御没有意义，速度才有。③ FreeBSD 14 兼容层（`:62-73`）：CALLOUT_LOCAL_ALLOC/CS_EXECUTING 在 14.0+ 被删，这里 define 回 0/0x0002 保旧行为；_callout_stop_safe 二参公共 ABI 转调三参内部实现（`:826-831`）。④ sleepq 四宏空转（`:132-135`）——callout_drain 的阻塞等待退化为忙等返回，因为单线程栈里不可能有人在 drain。

## 新人提示

排查"TCP 行为怪异"类问题先想到这个文件：所有 *sbt/tick 换算集中在 ff_callout_sbt.h（仅 73 行），是全库最值得先读的小文件。改 callout 逻辑时记住 cc_cpu 是 __thread 的——跨线程 callout_reset 会写别人的轮盘，c_cpu 只是记录布防线程（`:188-193` 注释）。ff_hardclock 的调用频率由 config.ini 的 hz 决定，graceful_reload 模式下换成了进程私有 TSC 节流（见 ff_dpdk_if.c:3803），两条路径不要混改。glue 侧新增符号前先查 ff_stub_14_extra.c——14 升级引入的新符号都收在那，别在 ff_glue.c 里另起炉灶。
