# 04 · syscall 出口修正（exit.c）与 seccomp 加速（seccomp.c）

> 图谱锚：L04 Syscall 翻译链。锚均经源码现场核实（/usr-data/data2/repos/termux-repo/proot@b27d81a）。

## 一、角色定位：圆谎者与守门人

PRoot 的哲学是"不代理执行，只改参数"：enter 把 guest 路径翻成 host 路径放行，内核照常执行，exit 再把内核**写回 guest 内存的结果**修正成 guest 视角自洽。`exit.c` 的 `translate_syscall_exit`（exit.c:58）就是"圆谎者"，修正四类东西——**路径回填、身份改写、errno 注入、状态簿记**：readlink 读出的 host 路径换算回 guest，getcwd 报 guest 的 cwd，uname 在 32 位兼容层谎报 i686，statfs 把 /dev/shm 伪装成 tmpfs。

`seccomp.c` 是"守门人"：`enable_syscall_filtering`（seccomp.c:500）在 fork 子进程里（event.c:146）装一张手写 BPF 的 seccomp filter，把 syscall 分三类——完全放行（零停机）、只停 enter（一停）、两停。没有它，ptrace 模式每 syscall 停两次，glibc 启动动辄上千次调用，性能不可接受。两文件一个管"停下来改什么"，一个管"哪些不用停"。

## 二、内部结构

### exit.c：四段序曲 + 巨型 switch

`translate_syscall_exit` 的执行顺序就是优先级声明：

1. **扩展截胡**：`notify_extensions(SYSCALL_EXIT_START)`（exit.c:64）返回 <0 直接写 errno，>0 跳过整个函数——fake_id0/link2symlink 等扩展优先于 PRoot 自身。
2. **errno 注入**：enter 翻译失败已把 `tracee->status` 置负，此处 poke 进 `SYSARG_RESULT`（exit.c:74-77）——内核根本没执行，错误码由翻译层杜撰。
3. **voided 结果保全**：enter 阶段被 PRoot 自己回答（syscall 号换成 avoider、结果已 poke）的调用，exit 强制保留 enter 写的值（exit.c:81-82），防内核 -ENOSYS 或外层 seccomp 沙箱回滚值覆盖（syscall.c:202-218 长注释详述 Android 沙箱场景）。
4. **按 `get_sysnum(tracee, ORIGINAL)` 分派**（exit.c:88）——用 ORIGINAL 而非 CURRENT：enter 可能改写过 syscall 号，guest 语义须按原始号判定。

case 收尾只有三种：`break`（局部 `status` poke 进结果寄存器，exit.c:839）、`goto end`（不动内核结果）、`status = -errno` 后 break。处理逻辑分四组：

- **输出缓冲回填**：getcwd 把 `tracee->fs->cwd` 写回 ORIGINAL SYSARG_1 指向的缓冲（exit.c:112-120）；readlink 族把内核写入的 host 目标经 `detranslate_path` 换算后重写（exit.c:484、:504-517）；accept/getsockname/getpeername 的 sockaddr 走 `translate_socketcall_exit`（exit.c:150）。
- **身份改写**：uname 在 x86_64 的 ABI_2（32 位兼容）下把 machine 改写为 "i686"（exit.c:527、:542-544）；statfs 对 /dev/shm 写 TMPFS_MAGIC 四字节（exit.c:744-756）；FICLONE ioctl 的 -EACCES 改写为 -EOPNOTSUPP（exit.c:773-776）。
- **簿记**：rename/renameat 若搬动的是 cwd 所在目录，`substitute_path_prefix` 更新 `tracee->fs->cwd`（exit.c:322、:341、:354-363）；socket 出口记录伪造 netlink fd 与真实 NETLINK_ROUTE fd（exit.c:781-824），供 recvfrom/recvmsg 的 ack 仿真消费（:832、enter.c:1705）。
- **auxv 三部曲**（Termux fork 的 loader 身份修补）：open 出口识别 `/proc/self/auxv` 记下 fd（exit.c:566-583）；read 出口扫 auxv 把 AT_EXECFN 改成 `tracee->execfn_addr`（exit.c:604-616）；prctl 的 PR_GET_AUXV 出口做同样扫描（exit.c:673-685）。

### seccomp.c：90 行的手写 BPF 生成器

filter 结构四块拼装（伪代码注释 seccomp.c:245-249）：

```
for each arch:  [load arch; jeq; 不匹配跳过本节]   ← start_arch_section (seccomp.c:174-191)
    for each sysnum: [jeq nr; RET TRACE|flag]     ← add_trace_syscall (seccomp.c:106-113)
    RET ALLOW                                     ← end_arch_section (seccomp.c:135-137)
RET KILL                                          ← finalize (seccomp.c:216-218)
```

每个被跟踪 syscall 只花 2 条 BPF：`BPF_JEQ` 比号（seccomp.c:109）+ `BPF_RET SECCOMP_RET_TRACE + flag`（seccomp.c:112）——`FILTER_SYSEXIT`（=0x1，syscall/seccomp.h:44）编码在返回值里，内核经 `PTRACE_GETEVENTMSG` 原样交给 tracer。名单 `proot_sysnums`（seccomp.c:331-445）约 110 项，flag 只有 0 与 FILTER_SYSEXIT 两种。`set_seccomp_filters`（seccomp.c:253）按 `SECCOMP_ARCHS`（arch.h:70-73 x86_64 双 ABI、:95 ARM）逐架构换算 syscall 号（seccomp.c:276、:290），`PR_SET_NO_NEW_PRIVS` + `PR_SET_SECCOMP` 装载（:311、:320）。

## 三、外部连接

- **上游**：`translate_syscall`（syscall.c:140）按 `IS_IN_SYSENTER` 分流，exit 分支在 :265-268 调 `translate_syscall_exit`，随后 `chain_next_syscall` 推进链式注入（:282-283）。seccomp 由 `launch_process` 的 fork 子进程 exec 前自装（event.c:145-146），`PROOT_NO_SECCOMP` 可关。
- **寄存器三版本**（tracee.h:37-43）：CURRENT=活寄存器、ORIGINAL=enter 前 guest 原值、MODIFIED=enter 改写后值。exit.c 靠这套快照做对称：输出缓冲地址读 ORIGINAL（exit.c:119），enter 翻译后的路径指针读 MODIFIED（exit.c:318）。
- **委托出去的 case**：brk→heap.c:150、execve→execve/exit.c:411、wait4→wait.c:181、statx→statx.c:7。
- **扩展名单合并**：`merge_filtered_sysnums`（seccomp.c:452）把 fake_id0（fake_id0.c:323）、link2symlink（link2symlink.c:1749-1766）、hidden_files 等 8 个扩展的名单按 flag OR 并入（seccomp.c:488）——扩展因此在 kernel 层精确布防自己的 exit 拦截。
- **event.c 消费侧**：`PTRACE_EVENT_SECCOMP` 停机在 event.c:689-690 分派，是 seccomp.c 生成物的唯一运行时消费者。

## 四、数据流

### detranslate_path：出口方向的路径换算

与 enter 侧 `canonicalize` 逐分量推进（stat+解 symlink）不同，`detranslate_path`（path.c:454）只做**前缀减法与绑定回代**：非绝对路径返回 0 不动（path.c:468-469）；readlink 场景 referrer 在 /proc 下时先走 `readlink_proc2` 仿真魔术链接（path.c:479-497）；`substitute_binding(HOST)` 做 host→guest 回代（path.c:526-535）；最后剥掉 guest root 前缀（path.c:537-556）。返回值三义：0=对称绑定无需改写（readlink 出口据此 `goto end` 保留内核结果，exit.c:490-496）；正数=新路径长度含终止符；负数=errno。截断救援是 Termux fork 典型补丁：host 路径远长于 guest 路径，内核缓冲填满时 detranslate 产出错误截断的路径，而 bubblewrap/glibc realpath 这类"返回值恰等于缓冲长度才扩容"的调用方察觉不到——exit.c:467-473 检测 `old_size == max_size` 时用全尺寸缓冲重读再翻译。

### seccomp 如何省掉 ptrace stop

无 seccomp：每 syscall 两停。有 seccomp，内核在 syscall 号判定处跑 BPF——

- **ALLOW**（不在名单）：直通，**零停机**，PRoot 不感知；
- **TRACE 无 flag**：一次 `PTRACE_EVENT_SECCOMP` 停，event.c:769-770 当场执行 enter 翻译后 `PTRACE_CONT`——**一停**，sysexit 被跳过；
- **TRACE|FILTER_SYSEXIT**：event.c:758-764 转 `PTRACE_SYSCALL`——**两停**，exit 修正得以发生。

例外通道 `sysexit_pending`（tracee.h:335）：enter 临时需要 exit 停机的调用（auxv 的 open、voided 结果保全，exit.c:581、syscall.c:219-222）置位后，event.c:774-775 把 restart_how 升级为 PTRACE_SYSCALL。新内核 seccomp 晚于 ptrace sysenter 停的次序问题由 `seccomp_already_handled_enter` 吞掉重复事件（event.c:793-795）。

### 与 enter 的对称性实例

socketcall 的 SYS_BIND/CONNECT 最干净：x86 多路复用参数存于 guest 内存数组，enter 翻译 sockaddr 后把**原始地址与长度**存进 SYSARG_5/SYSARG_6 闲置寄存器（enter.c:2461-2462）并改写内存（:2466-2467）；exit 用 POKE_WORD 从 MODIFIED 版 SYSARG_5/6 恢复原值（exit.c:217-218）——guest 读回参数时不能看见翻译痕迹。chdir 则是"全仿真"对称：enter 侧完成全部工作（校验+更新 cwd+poke 结果 0+`set_sysnum(PR_void)`，enter.c:2022-2023），内核只跑无害 avoider 号；exit 对 chdir/mount/unshare/setns 等一律强制 `status = 0`（exit.c:276-290），防某些内核把 avoider 的 -ENOSYS 泄漏进结果。

## 五、设计决策

1. **兜底 KILL 而非 ALLOW**（seccomp.c:217）：未列出的架构直接杀进程——宁可死也不让未翻译的 syscall 静默通过（guest 看到 host 路径，谎言破产）。代价是名单须穷尽目标架构，x86_64 构建为此列两节（arch.h:70-73）。
2. **flag 编译进 filter 数据**：`SECCOMP_RET_TRACE + flag` 让"要不要 exit 停"在装 filter 时一次编译，运行时零查表，内核经 PTRACE_GETEVENTMSG（event.c:725）白送。针对 aarch64 4.14.357 这类每次 ptrace 请求都清 eventmsg、读回恒 0 的内核（event.c:729-738），`filtered_sysnum_flags`（seccomp.c:540）从构建 filter 的同一份名单重算标志（event.c:740-754）——两处必须同步演进，改名单不改镜像函数就静默漏停。
3. **exit 不重翻路径**：出口修正全走轻量 `detranslate_path`（前缀减法）而非重量级 `canonicalize`——出口时内核已用完 host 路径，只需换算**展示给 guest 的字符串**。
4. **结果寄存器写权分层**：序曲（errno/voided/扩展错误，exit.c:66、:75、:82）→ case 内 break（:839）→ 尾声 `SYSCALL_EXIT_END` 扩展兜底（:842-844），扩展在 exit 末尾仍能否决一切。
5. **手写 BPF 拒绝 libseccomp 依赖**：只依赖 `<linux/filter.h>` 宏，`add_statements` 用 talloc 动态拼接（seccomp.c:73-90），`end_arch_section` 内置长度对账（:146-148，不符返回 -ERANGE 拒装坏 filter）。
6. **Android 条件布防**：PR_ioctl 仅 `__ANDROID__` 下挂 FILTER_SYSEXIT（seccomp.c:373-375），服务 exit.c:773-776 的 FICLONE 改写——普通 Linux 不会对 FICLONE 报 EACCES，多一停纯属浪费。

## 六、新人提示

- **改一个 syscall 处理器要三处联动**：enter.c 的 case、exit.c 的 case、seccomp.c 的名单。漏名单项=seccomp 模式下该调用零停直通，翻译被静默跳过且只在 Android 真机复现——本仓最难查的一类回归。
- **调试三板斧**：`PROOT_NO_SECCOMP=1` 关加速对照（event.c:145）；开 seccomp.c:52 的 `DEBUG_FILTER` 宏看生成的 BPF（:315-318 注释给了 dump 原始 filter 的技巧）；`-v 5/6` 看 sysenter/sysexit 前后寄存器打印（syscall.c:159、:260）。
- **先建立"三版本寄存器"直觉**：exit.c 里 ORIGINAL 与 MODIFIED 混用不慌——输出缓冲地址永远 ORIGINAL（guest 给的），enter 塞入的翻译产物永远 MODIFIED，SYSARG_5/6 是双方约定的传递槽。
- **观察练习**：seccomp.c:415 给 renameat2 挂了 FILTER_SYSEXIT，但 exit.c 的 cwd 跟踪 switch 只列 PR_rename/PR_renameat（exit.c:292-293）——查 link2symlink.c:1764 会发现该号的 exit 停机真正服务扩展的元数据同步，PRoot 自身对 renameat2 的 cwd 跟踪是缺位的。顺此线可吃透"名单三方共建"与"exit 事件多消费者"。
- **测试提醒**（AGENTS.md 铁律）：seccomp 行为强依赖内核次序（seccomp 先于/后于 ptrace sysenter 停，event.c:698 的 `seccomp_after_ptrace_enter` 两种都要测），裸 Linux 过不代表 Android 过。
