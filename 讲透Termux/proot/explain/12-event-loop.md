# 12 · 事件循环心脏：event.c 与 wait.c（ptrace 主循环与 wait4 仿真）

> 锚均于 /usr-data/data2/repos/termux-repo/proot@b27d81a 现场核实。`event.c` 指 `src/tracee/event.c`（967 行），`wait.c` 指 `src/ptrace/wait.c`（394 行，属 L05 嵌套 ptrace 仿真层）。

## 1. 角色定位

两文件是 proot 的"心脏起搏器"。`event.c` 是主进程调度核心：`launch_process()`（event.c:95）产下第一个被跟踪进程，`event_loop()`（event.c:314）阻塞在 `waitpid(-1, ..., __WALL)`（event.c:416）上，任何 tracee 的任何停机——syscall 进出、fork/clone/exec/exit 事件、信号、seccomp 反馈——都汇入这里，经 `handle_tracee_event()`（event.c:472）分派翻译，再由 `restart_tracee()`（event.c:946）放行。循环停转，guest 世界就冻结。

`wait.c` 是同一循环的"影子侧"：guest 内部也有 tracer（gdb/strace）时，proot 要扮演内核的 ptrace 角色，把 guest tracer 的 `wait4` 截下来代答——L05 嵌套 ptrace 仿真的 wait 半边（另半边是 `ptrace/ptrace.c`）。主循环处理每个 stop 前先调 `handle_ptracee_event()`（event.c:454，实现在 wait.c:235）分流：属 guest tracer 走仿真，否则走 proot 自家翻译。

## 2. 内部结构

### 2.1 启动握手（launch_process，event.c:95-163）

fork 后子进程四步：①`signal(SIGPIPE, SIG_DFL)`（event.c:126）——SIG_IGN 穿透 fork+exec，防宿主的忽略状态污染 guest 管道语义；②`ptrace(PTRACE_TRACEME)`（event.c:130）自声明可跟踪，免 root 的根基；③`kill(getpid(), SIGSTOP)`（event.c:141）与 tracer 同步——缺这一停 tracer 只能看到下个 execve 的"返回"，无法处理解释器展开；④`execvp` 目标程序（event.c:152）。seccomp 过滤器在 TRACEME 后、exec 前装上（event.c:145-146，`PROOT_NO_SECCOMP` 可禁）。

### 2.2 主循环骨架（event_loop，event.c:314-465）

循环前铺信号表（event.c:335-375）：致命五信号挂 `kill_all_tracees2`（:345）杀光 tracee 防孤儿，SIGUSR1/2 挂 talloc 打印（:352），tty 六信号默认（:357-363），**其余一律 SIG_IGN**（:368）——proot 对 ^C 装死是刻意的。SIGALRM 单独挂且不带 SA_RESTART（:382-391），用来打断 waitpid 做周期工作。

每轮五步：①`free_terminated_tracees()`（event.c:401）——注释钉版"唯一安全的 tracee 释放点"；②shadow pipe 收割（:405/:413）；③阻塞 `waitpid`（:416），ECHLD 说明全灭、跳出返回退出码（:424-428）；④`get_tracee()` 找/建 Tracee（:432），EXEC 事件且执行者是线程则换人（:438-440，见 4.3）；⑤扩展先行（:450）→ 嵌套 ptrace 分流（:454-458）→ `handle_tracee_event()` 算信号 → `restart_tracee()`（:460-461）。

### 2.3 PTRACE_EVENT_* 分派表（handle_tracee_event，event.c:472-916）

入口先做 restart 模式预选（event.c:492-503）：seccomp 启用且无需 sysexit 时默认 `PTRACE_CONT`（无关 syscall 直通），否则 `PTRACE_SYSCALL`。状态三叉中 WIFEXITED/WIFSIGNALED 只记退出码并 `terminate_tracee()` 标记待回收（event.c:508-521），WIFSTOPPED 才是主戏。

**取信号不用 `WSTOPSIG()`**（event.c:523-525 注释明言）——它会清 PTRACE_EVENT 位，必须手撸 `(tracee_status & 0xfff00) >> 8`。分派表：

| case | 行号 | 处理 |
|---|---|---|
| 裸 SIGTRAP（首停） | :530-582 | 一次性 `PTRACE_SETOPTIONS` 装 7 项默认选项（:531-538），先试加 TRACESECCOMP（:554-555），失败回退（:558-572） |
| SIGTRAP\|0x80 | :584-687 | syscall 停机 → `translate_syscall()`（:615）。**勘误：常被提及的 `translate_open_call` 本仓不存在（grep 零命中）**；唯一入口是 `translate_syscall`（syscall/syscall.c:140），本文件 :615/:761/:858 三处调用 |
| SECCOMP/SECCOMP2 | :689-797 | 加速路径，见 5 之④ |
| VFORK | :799-802 | `new_child(tracee, CLONE_VFORK)`（:801） |
| FORK/CLONE | :804-808 | `new_child(tracee, 0)`（:807），三事件共用，flags 从寄存器重读（tracee.c:669-677） |
| VFORK_DONE/EXEC/EXIT | :810-817 | 只把 `restart_how` 恢复为 `last_restart_how`（:814-816） |
| SIGSTOP | :819-839 | 首个 SIGSTOP 吞掉（:835-838）；exe==NULL 时 `signal=-1` 扣住等 fork 认领（:823-824），`adopt_held_children()`（:830）兜底 |
| SIGSYS | :841-896 | `PTRACE_GETSIGINFO` 验 `si_code==SYS_SECCOMP`（:843-844）后分流 |
| default | :898-908 | 普通信号默认转发；chain 中压制暂存（见 4.1） |

### 2.4 wait.c 仿真三段

`translate_wait_enter()`（wait.c:87）：guest tracer 调 wait4 时，若确有 ptracee 且目标 pid 匹配（:100-105），改写为 PR_void（:109）挂起真实执行。`translate_wait_exit()`（wait.c:181）：查 `get_stopped_ptracee()`（:196，定义于 tracee.c:304）有无待交事件的停机 ptracee；无则按语义返回 -ECHILD 或 WNOHANG 的 0（:199-210），或把 ptracer 挂进等待状态（:216-217）事后唤醒。`handle_ptracee_event()`（wait.c:235）：停机先存 `event4.proot`（:246-247），guest tracer 想看哪些按其 SETOPTIONS 过滤（CASE_FILTER_EVENT 宏 :266-283；SECCOMP 事件不支持仿真 :285-289）；需 proot 先行的事件当场调 `handle_tracee_event()`（:320）——**PRoot 永远比 guest tracer 先看一眼**；随后 `kill(ptracer->pid, SIGCHLD)`（:364）模仿内核异步通知，ptracer 正阻塞则直接代答并重启（:369-390）。

## 3. 外部连接

上游：cli/proot.c 调 `launch_process` 后进 `event_loop`，返回值即 proot 退出码（event.c:267/:509）。下游：`translate_syscall`（syscall.c:140）分 enter/exit 两相，`handle_seccomp_event`（tracee/seccomp.c:85，调用点 event.c:890）接 guest 自装过滤器拦截的 syscall；tracee.c 家族构成 fork 认领线——`new_child`（:662）/`attach_child`（:716）/`adopt_held_children`（:574）/`resolve_pending_child`（:613）/`get_execve_tracee`（:408）/`free_terminated_tracees`（:366）。reg.c:393 在新 child 首停修复寄存器（event.c:448），扩展经 NEW_STATUS（event.c:450）有否决权。

## 4. 数据流：三个关键场景

### 4.1 信号的四类归宿

**转发**：default 分支（event.c:898-908）算出的 signal 原样传给 `restart_tracee`，经 `ptrace(restart_how, pid, NULL, signal)`（event.c:957）由内核在重启时投递——SIGINT/SIGSEGV 等普通信号的主路。**吞掉**：signal 置 0 后重启，内核"忘了"它——裸 SIGTRAP 首停与 syscall 停机（:584-585）、seccomp 事件（:693）、首个 SIGSTOP（:835-838）全走此路：这些停机是给 tracer 看的通知，转发会杀死 guest。**重排**（压制后补投）：syscall chain 进行中到达的信号不能打断链条，`chain.suppressed_signal` 暂存（:901-907），chain 跑完补投（:656-660）；guest-tracer 侧同理入 `event4.ptracer.pending` 排队（wait.c:359-360）。**伪造**：wait.c:339-342 为 guest tracer 合成 syscall-exit 停机的 wstatus（`(SIGTRAP|0x80)<<8|0x7f`），配 `kill(SIGCHLD)`（:364）伪装内核通知；另一处是 SIGSYS 到达时主动合成 sysexit 调 `translate_syscall`（event.c:856-858）。第五种特殊值 `signal=-1`（:824）表示根本不重启——扣住等 fork 认领或等 guest ptracer。

### 4.2 僵尸收割（两段式）

`terminate_tracee()`（tracee.c:350-361）只置 `terminated` 标记，真正的 `TALLOC_FREE` 在下一轮循环头 `free_terminated_tracees()`（event.c:401→tracee.c:366-383）——**延迟释放是刻意设计**：事件处理途中 tracee 可能被多处引用，循环头是唯一无引用时刻。嵌套 ptrace 下有第三条路径：guest tracer 的 wait 取走事件后，`is_zombie` 置位的 ptracee 在 `update_wait_status()` 里被 `detach_from_ptracer`+`TALLOC_FREE` 立即释放（wait.c:167-171）——guest tracer 收走状态即内核僵尸已 reap，proot 簿记必须同步消失。最精妙是 wait.c:131-152 的**去重**：内核对"父=tracer"的进程只报一次终止事件，proot 先藏起给 guest-tracer 的事件、让 guest 以父身份再 wait 一次（:140），确保僵尸从内核视角真的被收割。

### 4.3 execve 竞态（get_execve_tracee）

非 leader 线程调 execve 时内核杀光兄弟线程、把 leader 的 PID 让渡给该线程，且**不报 leader 的死亡**（tracee.c:408-434 注释引 ptrace(2) man page）。不处理的话，PTRACE_EVENT_EXEC 落在 leader 的 Tracee 上，execve 的 sysexit 状态却在线程的 Tracee 里，后者永远无人释放，直到内核复用其 TID 时 `attach_child()` 撞上幽灵（tracee.c:736-744 的 pid-reuse 分支正是补救）。解法在 event.c:438-440：凡 EXEC 事件先 `get_execve_tracee()` 换人——`PTRACE_GETEVENTMSG`（tracee.c:415）读出"前线程 ID"，把 leader 的 pid/vpid/parent 过继给线程的 Tracee（tracee.c:432-436）后 `TALLOC_FREE(leader)`。fork 侧姊妹竞态：child 可能在 fork 事件到达前就死，`attach_child` 用 `is_still_traced()`（tracee.c:450，`waitid(WNOWAIT)` 探测）甄别后放弃建 Tracee（tracee.c:726-734）。

## 5. 设计决策

**① TRACEME 而非 ATTACH**（event.c:130）：子进程自我声明，零权限。**② `__WALL` 收线程**（:416）：多线程 guest 每线程都要翻译，漏一个就是未翻译路径裸奔。**③ restart_how/last_restart_how 双字段**（:814-816/:961-962）：PTRACE_EVENT 不改变停机节奏，事件完自动恢复此前模式。**④ seccomp 事件顺序自适应**：新老内核对"seccomp 评估 vs ptrace sysenter 停机"先后不同，`seccomp_after_ptrace_enter` 在首个 SECCOMP 事件一次性探测（event.c:695-701），此后跳过冗余停机（:707-716）或标记吞掉后到的停机（:793-795）。**⑤ 内核缺陷容错三连**：uname 判 3.5 以下内核静默吞 TRACESECCOMP 位（event.c:80-89）；aarch64 4.14.357 每次 ptrace 请求清 eventmsg，用 `EVENTMSG_LOST` 状态+自家过滤表补偿（:729-754）；fork 事件读不到 child pid 时转 `pending_child` 延迟认领（tracee.c:696-707）。**⑥ PRoot 先行原则**（wait.c:318-320）：嵌套 ptrace 下 proot 永远先于 guest tracer 处理事件——嵌套仿真正确性的基石。**⑦ SIGSYS 谨慎分类**（event.c:841-896）：分辨是外层 seccomp 拦了 proot 自己 void 掉的 syscall（必须吞，否则 link2symlink 副作用重放，:884-888），还是 guest 过滤器拦 guest syscall（交 `handle_seccomp_event` 仿真，:890）；ARM 的 SYSARG_1 同寄存器坑有补丁（:860-866）。

## 6. 新人提示

- **`WSTOPSIG()` 是陷阱**：它会清 PTRACE_EVENT 位，只能用 `(status & 0xfff00) >> 8` 替代（event.c:523-525）；裸 SIGTRAP 只有第一次是"首停"，靠 static `deliver_sigtrap` 区分（:548-551）。
- `signal=-1` 与 `signal=0` 语义完全不同：前者"扣住不重启"（restart_tracee 显式拦截，event.c:951-952），后者"吞信号重启"，返回值是三态协议。
- 调试：`PROOT_NO_SECCOMP` 关加速回纯两段停机（:145）；`PROOT_ASSUME_NEW_SECCOMP` 强制新内核事件序（:481）；发 SIGUSR1 dump talloc 层级（:348-352）。
- wait.c 只在 guest 有 tracer 时激活（wait.c:95-96）；guest 里 strace/gdb 出问题先查 wait.c 与 ptrace.c。
- 僵尸堆积排查：先看 `free_terminated_tracees` 是否被饿死，再查去重分支（wait.c:131-152）与 is_zombie 收割（:167-171）。
- 内核怪癖兼容密度极高（5 节⑤），提 PR 前确认行为不是某怪癖变体——AGENTS.md 钉版维护态，设备特定回归是雷区。
