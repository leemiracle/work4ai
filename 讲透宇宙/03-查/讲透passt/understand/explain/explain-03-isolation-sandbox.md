# explain-03 · isolation.c：五阶段无特权自沙箱

## 1. 角色定位

`isolation.c`（580 行）承载 passt 的安全立身之本："不请求特权、主动丢弃特权"。Theory of Operation（`isolation.c:15-62`）开宗明义：即使被攻破也要把影响压到最小——按"资源用完即弃"次序分五阶段收窄：1a `isolate_initial()` 丢能力 → 1b `isolate_fds()` 关泄漏 fd → 2 `isolate_user()` 切 uid/userns → 3 `isolate_prefork()` pivot_root 封文件系统 → 4 `isolate_postfork()` seccomp 锁系统调用。每个阶段的 Should/Mustn't 约束写在函数注释里（如 `isolation.c:202-208`：此时**不能**去掉文件系统访问，setup 还要读文件）。

调用时序钉在 `passt.c` 的 `main()` 上：`isolate_initial()`+`isolate_fds()` 在 `main()` 第 3-4 行（`passt.c:347-348`）；`isolate_user()` 由 `conf()` 在解析 `--runas`/`--userns` 后调用；`isolate_prefork()` 在 daemonize 前（`passt.c:426`）；`isolate_postfork()` 在 fork 后进主循环前（`passt.c:449`）。

## 2. 内部结构

- `drop_caps_ep_except()`（`isolation.c:106-127`）：直接 `syscall(SYS_capget/SYS_capset)` 按 64 位掩码同时清 effective 与 permitted——丢 permitted 留 effective 没意义，两集合一起剪。
- `clamp_caps()`（`isolation.c:143-174`）：防子进程东山再起。`PR_CAPBSET_DROP` 逐个（0..63）清 **bounding set**（`isolation.c:152-164`）再清 inheritable。注释（`isolation.c:129-142`）讲透：bounding set 只限制 exec 后可获得的 cap，不影响自身；EINVAL（未分配 cap 号）与 EPERM（`--netns-only` 无 CAP_SETPCAP）容忍。
- `isolate_initial()`（`isolation.c:209-250`）：保留名单是理解全局的钥匙（`isolation.c:236-238`）：CAP_NET_BIND_SERVICE（转发低端口）、CAP_SETUID/SETGID（稍后切用户）、CAP_SYS_ADMIN/NET_ADMIN（`--netns-only` 时 setns+配接口）、CAP_DAC_OVERRIDE（`--runas` 组合下建 socket）、CAP_SYS_CHROOT（fallback 用）。`isolation.c:246-247` 是两条内核版本考古：Linux 5.12 起 pasta 从非 init userns fork 子进程要写 uid_map 就得留 CAP_SETFCAP；join 同 userns 下的 netns 要 CAP_SYS_PTRACE。
- `isolate_fds()`（`isolation.c:263-293`）：先 `conf_tap_fd()` 从命令行挖出 `--fd` 传入的 socket（挪到 fd 3），然后 `close_range(close_from, ~0U, CLOSE_RANGE_UNSHARE)` 一刀切（`isolation.c:278`）。CLOSE_RANGE_UNSHARE 先复制 fd 表再改，避免误伤共享 fd 表的线程；内核不支持（ENOSYS/EINVAL）只 warn 不死（`isolation.c:279-289`）——注释很诚实："carry on and hope for the best"。
- `enter_userns()`/`userns_holder()`/`create_userns()`（`isolation.c:299-366`）：自建 userns 的杂技。`create_userns()` 的注释（`isolation.c:342-351`）列出四重约束：userns 要在 setuid(nobody) **之前**建（否则 ns 属主是 nobody）；setuid 又要在进 ns **之后**；只有父命名空间里的当前用户才能写 uid_map；于是不能 unshare 只能 `do_clone()` 一个 `userns_holder()` 占位进程（PDEATHSIG=SIGKILL 挂保险，`isolation.c:325-326`），父进程给它写好 uid/gid map（`make_ugid_map`，`isolation.c:363`），再 setns 进去、杀掉 holder（`isolation.c:420-421`），最后在 ns 内 setuid(0)（映射自真实 uid，`isolation.c:424-428`）。
- `isolate_user()`（`isolation.c:382-462`）：顺序敏感。先 `setgroups(0, NULL)` 丢补充组（EPERM 容忍）；指定 userns 或不自建时**先** setgid/setuid 再进 ns（`isolation.c:399-405`），自建时反序（见上）。进 ns 后 Linux 白送全套能力，随即第二次 `drop_caps_ep_except(ns_caps)`（`isolation.c:461`）：常留 CAP_SYS_ADMIN（prefork 要 unshare、pasta 要 setns 进 netns）；pasta 额外留 NET_ADMIN/NET_BIND_SERVICE/SYS_PTRACE——`isolation.c:436-459` 每个能力都注释了消费者。
- `isolate_prefork()`（`isolation.c:477-544`）：文件系统封印。unshare IPC/NS/UTS/PID 四命名空间（pasta 前台跑时不加 NEWPID，因为没法再 fork，`isolation.c:482-487`）；`/` 改 MS_UNBINDABLE 防被 bind 引用（`isolation.c:494`）；挂一个 `nr_inodes=2,nr_blocks=0` 的只读空 tmpfs（`isolation.c:499-504`，两个 inode 是 "." 和 ".."）；`pivot_root(".", ".")` 换根后 `umount2(".", MNT_DETACH)` 卸掉旧根（`isolation.c:511-526`）。pivot_root 失败且开了 `--chroot-fallback` 时退 `move_root()`（`isolation.c:181-199`，MS_MOVE+chroot 的弱化版）。最后 `clamp_caps()` + 第三次 drop_caps——pasta 只留 SYS_ADMIN+NET_BIND_SERVICE（`isolation.c:531-538`）。
- `isolate_postfork()`（`isolation.c:554-580`）：终局。`PR_SET_DUMPABLE=0` 禁 core dump（`isolation.c:558`）；`PR_SET_NO_NEW_PRIVS` + `PR_SET_SECCOMP` 装上按模式三选一的 BPF 过滤器（`isolation.c:560-579`，filter_passt/filter_pasta/filter_vu 来自构建期生成的 `seccomp.h`）。

## 3. 外部连接

上游调用者只有 `passt.c` 与 `conf.c`。依赖 `seccomp.h`——**不是手写的**：`seccomp.sh` 构建期扫描全部 `#syscalls` 注释（如 `passt.c:167` 的 `#syscalls exit_group`、`tap.c:411` 的 `#syscalls:pasta write`，冒号后缀按模式区分）生成 BPF 规则——加新系统调用的正确姿势是在调用处加 `#syscalls` 行而非改 seccomp.sh。`util.c` 的 `ns_is_init()/do_clone()/make_ugid_map()` 是配套原语。`contrib/apparmor/abstractions/passt` 与 `contrib/selinux/passt.te` 逐条对应这里的操作，三层策略互为印证。

## 4. 数据流

以 pasta 由普通用户启动为例：main 立即 `isolate_initial()`（原进程没能力时 capget/capset 大多无操作，无害）；`isolate_fds()` 关掉父进程（如 container runtime）泄漏的 fd。conf 后 `isolate_user()`：clone holder → 写 uid_map(uid→0) → setns → 杀 holder → setuid(0)（ns 内 0=真实 uid）→ 丢多余能力。初始化完 tap/flow 后 `isolate_prefork()`：四 ns unshare、空 tmpfs pivot_root——从此 `/` 下空无一物。daemonize 后 `isolate_postfork()` 装 filter_pasta：白名单外 syscall 直接被 SIGSYS 杀。

## 5. 设计决策

最值得学的是**阶段化的"资源用完即弃"**：不追求一步到位的最小沙箱，而是在每个"最后一次需要某特权"的时刻丢弃它（头注释 `isolation.c:23-26`）。其次是**注释即规格**：每个函数头用 Should/Mustn't 双清单写明本阶段允许与禁止做的事，比如 prefork 的 "Mustn't: remove syscalls we need to daemonise"（`isolation.c:475`）——seccomp 必须在 daemonize 之后装，否则 `__daemon()` 里的 fork 相关调用就被自己的过滤器杀了。第三是**能力与用途一一对应**：每个保留的 capability 都注释了消费者，审阅时可以反向核对"这个 cap 还有人用吗"。userns_holder 的四重约束注释（`isolation.c:342-351`）是内核 API 语义陷阱的精彩案例：三件事的先后顺序互相制约，唯一解是引入一个临时进程。

## 6. 新人提示

改代码时三条铁律：新系统调用必须在调用处加 `#syscalls` 注释，否则 seccomp 阶段进程被杀（症状：装好 filter 后第一笔流量就 SIGSYS 死亡，日志只有 dmesg 里的 seccomp 记录）；新能力需求要挂在正确的阶段——prefork 之后还在用的能力必须留在 prefork 的保留名单里。调试技巧：`--chroot-fallback` 可以在 pivot_root 失败的环境（某些容器 runtime）下退化为 chroot 继续跑；怀疑能力问题时用 `--foreground` + `capsh --decode=$(grep CapEff /proc/$pid/status)` 对照三阶段保留名单。注意 `isolate_fds()` 只在启动时执行一次，运行期 pesto/conf socket 新开的 fd 不受影响——fd 卫生只防"继承泄漏"，不防"自开"。
