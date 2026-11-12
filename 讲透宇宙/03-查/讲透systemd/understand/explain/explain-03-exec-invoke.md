# explain-03 · src/core/exec-invoke.c + executor.c — 沙箱执行：从 exec 参数到 execve 的全部仪式

## 一、角色定位

exec-invoke.c（7291 行）实现 `exec_invoke()`（exec-invoke.c:5612）：systemd 里"把一个 ExecStart= 命令真正变成进程"的唯一下沉点。服务管理器不在 PID 1 里 fork——而是 exec 一个独立的 `systemd-executor` 二进制（executor.c，245 行的瘦壳：解析 `--deserialize=<fd>` 选项（executor.c:82-114）、收集全部 fd（executor.c:166）、反序列化出 ExecContext/ExecCommand/ExecParameters/CGroupContext 四件套（executor.c:177 `exec_deserialize_invocation`），然后调用 exec_invoke（executor.c:192））。exec-invoke.c 因此集中了 systemd 全部沙箱硬技能：mount namespace、user namespace、seccomp、capabilities、LSM、PAM、PTY、cgroup 挂靠。本仓为上游原版（origin=github.com/systemd/systemd，仓内无 Kylin 私有 diff），是麒麟工作区研究安全加固与 exec 链路的首选对照实现。

## 二、内部结构

文件按主题分块：std 流装配（fixup_input:488 / setup_input:507 / setup_output:703 / acquire_broker_terminal:354——ptybrokerd PTY 后端）；确认弹窗（ask_for_confirmation:1011）；身份（enforce_groups:1192 / enforce_user:1233 / setup_pam:1511 / setup_private_users:2788 / setup_private_users_child:2746）；二十余个 `apply_*` 沙箱原语，一个原语对应一条指令：apply_protect_sysctl:2169、apply_protect_kernel_modules:2185、apply_protect_kernel_logs:2200、apply_protect_clock:2213、apply_private_devices:2226、apply_restrict_namespaces:2241、apply_lock_personality:2254、apply_restrict_filesystems:2283（cgroup-bpf 实现限制文件系统，exec-invoke.c:2303 调 `bpf_restrict_fs_update`）、apply_protect_hostname:2307、apply_memory_deny_write_execute:2059、apply_restrict_realtime:2085、apply_restrict_suid_sgid:2098；mount 层（compile_bind_mounts:3758 / apply_mount_namespace:4274 / setup_ephemeral:3990 / pin_rootfs:4126 + verity_settings_prepare:4077——Verity 根文件系统）；环境构建（build_environment:2394）。趋势信号：io_uring 限制族（apply_io_uring_filter:1883 等，1839 起对 io_uring 的 BPF 过滤检查）与 bpffs 辅助进程（bpffs_helper:2679）都是近两年攻击面收紧的产物。

## 三、外部连接

上游：service.c/socket.c 等通过 spawn 阶段把参数序列化（execute-serialize.c）经 socket 交给 executor；manager 侧 pin 住 executor 二进制防升级竞争。内部依赖 execute.h 的 ExecContext（解析后的全部 Exec* 指令）、exec-util.h、以及 cgroup-bpf 设施（bpf_restrict_fs_map_fd 从 manager 侧映射传入，exec-invoke.c:5789）。与用户空间联动最深的三处：PAM 会话（setup_pam 起子进程建 session 再回填环境）、NSS 查询（通过 manager 的 user_lookup socket 回传结果，send_user_lookup:4771——PID 1 自己禁止做 NSS 的设计延伸）、journal（setup_output 记录 journal_stream_dev/ino 让 journald 识别日志流归属，exec-invoke.c:6052）。PTY 走 ptybrokerd（exec-invoke.c:5701-5715 长注释解释为何必须在进 namespace 之前先拿后端 fd）。

## 四、数据流

exec_invoke 是一条 1500 行的顺序仪式，顺序本身就是安全语义（注释反复强调"能撤的先做，不能撤的尽量贴近 execve"）：
1. 预检与重命名（exec-invoke.c:5670 防 CVE-2021-4034 式空命令行；5676 rename_process_from_path）；
2. socket/named fd 分流（5678-5699）；PTY broker fd 先取（5716）；
3. 信号复位（5736）、`close_remaining_fds`（5802）——先把不用的 fd 全关，防泄漏；
4. 计算 `needs_sandboxing`（5972：EXEC_APPLY_SANDBOXING 且非 FULLY_PRIVILEGED 命令）与 needs_mount_namespace；
5. std 流定型（6039-6058）→ DynamicUser 实现（5873 dynamic_creds_realize）→ PAM（6476）；
6. namespace 三明治：第一遍 setup_delegated_namespaces（6590，unshare 非委派 ns）→ setup_private_users（6563/6660 两处，managed userns 场景）→ 第二遍 setup_delegated_namespaces（6692，unshare 委派 ns）→ attach_to_subcgroup（6732，join 到 manager 预建的 cgroup）；
7. root dir（6904）→ enforce_user/setresuid（6910，真正掉权限的不可逆点）→ working directory（6954）；
8. 最后贴着 execve 的原语：apply_restrict_filesystems（7116）、apply_syscall_filter（7152，注释 exec-invoke.c:7150 明言"尽可能靠近 execve，让自身代码也受 seccomp 约束"）；
9. handoff 时间戳（7272）、exec_fd 标记（7266 注释：manager 靠 POLLHUP 判定 execve 成败）→ `fexecve_or_execve`（7284）。
每一步失败都写入语义化 exit_status（EXIT_FDS/EXIT_USER/EXIT_SETSID…），systemctl 看到 "Failed at step XXX" 时就是这里产生的。

## 五、设计决策

1. **executor 进程隔离**：把 fork+配置移出 PID 1（executor.c 全文件），崩溃与内存开销都不伤管理器；代价是多一次 exec 与序列化往返，mac_init_lazy（executor.c:170-172 注释：SELinux 全量加载 2-10ms，按需初始化）就是为此做的优化。
2. **顺序即安全**：身份变更后不可再做需要特权的事，故 mount 组装全部先于 enforce_user（6904→6910）；seccomp 刻意最后装（7150），让守护代码"以身作则"。
3. **失败退出码语义化**：EXIT_STATUS 枚举让"哪一步失败"穿透两层进程边界仍可读（executor.c:198-205 转 SD_MESSAGE_SPAWN_FAILED 结构化日志）。
4. **不可逆动作尽量晚**：exec_fd/handoff（7266/7272）在 execve 前一瞬完成，确保 manager 拿到的成功信号不可能早于配置完成。
5. **降级而非失败**：PTY broker 不可达时 ExecStop= 类命令降级而非失败（exec-invoke.c:5720-5729），保证关机晚期语义。

## 六、新人提示

读这份文件别按行号顺序读，按上面"数据流"的仪式顺序跳读最有效。`systemd-analyze security` 的每个评分项几乎都能在 apply_* 函数里找到实现落点，对照学习事半功倍。调试三板斧：`systemd-analyze verify` 查配置；journal 里 "Failed at step" 的 EXIT_XXX 码反查 exec-invoke.c 中赋值点；strace 会被 seccomp 干扰，改用 `SystemCallFilter= TRACE...` 或关沙箱对照。Kylin 工作区关注点：若在麒麟发行版上做安全合规定制（如默认收紧 RestrictFileSystems/PrivateDevices），上游这里的 apply_* 原语即插即用，无需改 manager；而 fexecve（7284）在只读根文件系统/verity 场景（pin_rootfs:4126）是必经路径，兼容层务必覆盖。注意 close_remaining_fds 的白名单机制（5802 与 add_shifted_fd:4881）——新增要传给子进程的 fd 时忘记加入 keep 集是最常见的"服务起不来"根因。
