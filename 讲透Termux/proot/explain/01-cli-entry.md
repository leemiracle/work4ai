# 01 · CLI 入口链：main → 选项解析 → launch_process（L10）

> 图谱锚：L10 CLI 入口与诊断。目标文件 `src/cli/cli.c`（606 行，main 与解析框架）+ `src/cli/proot.c`（397 行，proot 工具的选项语义）。锚均经源码现场核实。

## 一、角色定位

这对文件是 proot 可执行程序的出生证明：翻译引擎（L02-L06）在这里被装配并点火。分工是**框架与语义分离**——`cli.c` 是通用 CLI 框架（main、扫描器、usage/version 打印、初始化编排），`proot.c` 是"proot 这一个工具"的选项处理器。契约在 `cli.h`：`Cli` 结构体带选项表与六个初始化钩子（cli.h:36-49），工具实现 handler 后经 `get_proot_cli()` 交回实例（proot.c:393-397，返回常量 `proot_cli`）。此框架历史上服务过两个前端（doc/GNUmakefile:1 的 OUTPUTS 同列 proot.h 与 care.h），fork 后只剩 proot。本链终点只有两步：`launch_process`（cli.c:486）fork 出首个被跟踪进程，`event_loop()`（cli.c:505）进入翻译循环。一句话：**把 argv[] 翻译成 Tracee 上的配置，然后点火**。

## 二、内部结构

**main（cli.c:444-516）** 八步：①`talloc_enable_leak_report()`（:451）；②`--shm-helper` 短路（:457-459，一个二进制两用，直进 sysvipc 助手主循环 sysvipc_shm.c:820）；③`get_tracee(NULL, 0, true)` 预创建首 Tracee（:462）填 `tracee->pid`（:465）；④`PROOT_VERBOSE` 预置详细级别（:469-474）；⑤`parse_config`（:477）；⑥无 `PROOT_NO_MOUNTINFO` 则挂 mountinfo 扩展（:481-482）；⑦`launch_process`（:486）；⑧`exit(event_loop())`（:505）。

**parse_config（cli.c:296-440）** 是手写三重循环扫描器（选项组 j × 别名 k × 参数 i）。参数四种归宿：前一选项等待的值（:319-325，handler 延迟消费）；非 `-` 开头即选项区结束（:327-328）；匹配别名后三种取值形态——无值直调 handler（:357-362）、`--rootfs=path` 粘连值（:365-371）、`-r path` 分离值（:380 记 handler 等下轮）；全不中报 unknown option（:385）。防呆两处：`-rfoo` 类歧义（:350-354）与末尾缺值（:389-392）。随后 HOOK_CONFIG 编排（:396-435）：pre_initialize_bindings → `initialize_bindings`（:410，binding.c:711）→ `initialize_cwd`（:420）→ `initialize_exe`（:430）→ post_initialize_exe，返回命令偏移 `argc_offset`（:394,439）。

**proot.c 处理器群**三类。路径类：`handle_option_r`（:39）把 chroot 翻译成 `new_binding(tracee, value, "/", true)`（:45，注释明言 chroot ≡ mount --bind $PATH /）；`handle_option_b` 按第一个 `:` 切 host:guest（:52-71，切分 :63-67）；`handle_option_w` 写 `tracee->fs->cwd`（:147-154）。组合别名：`-R` = `-r` + 推荐绑定表（:254-265；表在 proot.h:12-34，`$HOME` 与 `*path*` 占位符由 new_bindings 展开于 proot.c:239-252，`*path*` 替换成根路径本身）；`-S` = `-0 -r` + 精简 su 表（:267-282，proot.h:36-49）；`-0` = `-i 0:0` 的糖（:190-193）。扩展类：`-k` kompat（:156-173）、`-i` fake_id0（:175-188）、`--link2symlink`（:284-294）、`--sysvipc`（:310-320）、Android 专属 `--ashmem-memfd`（:296-308，`#if defined(__ANDROID__)`）、`-L/-H/-p`（:322-338）——全走 `initialize_extension()` 进扩展框架（L07）。

## 三、外部连接

上游依赖四个子系统。**path/binding.c**：`new_binding`（binding.c:457）只懒入队——首次才分配 `bindings.pending` 环形队列（:462-469），canonicalize 推迟到 `initialize_bindings`（binding.c:711，入口 assert rootfs 非空）；host 侧 realpath2 规范化，/proc/self 前缀特判保留原样（binding.c:486 起，避免绑定固化到 proot 自己的 PID）。**path/path.c**：`which()`（path.c:152）做 $PATH 查找，被 `initialize_exe`（cli.c:279）与 qemu 路径解析（proot.c:356）复用；`expand_front_variable`（cli.c:541）展开绑定表的 `$HOME`。**path/canon.c**：`initialize_cwd` 用 `canonicalize()` 校验 -w 目录（cli.c:248），失败降级 "/"（:250-253），成功回写 `setenv("PWD")`（:265）。**tracee/event.c**：launch_process（event.c:95）点火，见下节。

与构建相连：`proot.h` 头部声明自动生成（proot.h:1），规则在 doc/GNUmakefile:17-18（xsltproc 从 manual.xml 经 cli.xsl 出 C 源）；`VERSION` 兜底 "5.1.0"（proot.h:8-10），实际值由 src/GNUmakefile:142-144,168 的 `git describe` 注入 build.h。与诊断相连：`print_usage`（cli.c:55-105）遍历同一张 Option 表打印（:67-99），并经 `notify_extensions(PRINT_USAGE)`（:101）让扩展追加选项说明；`print_version`（cli.c:110-125）顺带报告 process_vm/seccomp_filter 两个内建加速器的可用性（:113-124）。

## 四、数据流

配置流：argv[] → parse_config 逐参消费 → handler 写 Tracee 字段（`tracee->qemu` proot.c:102、`fs->cwd` :149、`verbose` :205、`killall_on_exit` :197）与 pending 绑定队列 → HOOK 按依赖序固化（bindings 先于 cwd 先于 exe，cli.c:408-429 注释明言因果）→ 返回 argc_offset → main 取 `&argv[status]`（cli.c:486）。

点火一跃在 launch_process（event.c:95-163）：`fork()`（:109）后子进程四件事——恢复 SIGPIPE 默认处置（:126，防上层继承的 SIG_IGN 让 guest 管道噪音化，:116-125 注释）；`PTRACE_TRACEME`（:130）；`kill(getpid(), SIGSTOP)`（:141）同步停机等 tracer 就位；无 `PROOT_NO_SECCOMP` 时装 seccomp 过滤器（:145-146）；最后 `execvp(tracee->exe, argv)`（:152）。命令缺省时 exe 为 "/bin/sh"（cli.c:279）、argv 缺省 `{ "-sh", NULL }`（event.c:97）——登录 shell 语义。父进程记 `tracee->pid`（:157）返回，main 随即进 `event_loop()`（event.c:314），CLI 层使命终结。

观测流：`print_config`（cli.c:193-213）在点火前打印最终生效配置（:206-210）；`PROOT_VERBOSE` 先于命令行生效（cli.c:469-474），`-v` 可覆盖并同步全局 `global_verbose_level`（proot.c:205-209）。

## 五、设计决策

**手写扫描器而非 getopt_long**：核心需求是选项区/命令区分界（第一个非 `-` 参数即终止，cli.c:327-328），getopt 会重排 argv 且难表达"同 handler 多别名 + 双取值形态"（`-r path` 与 `--rootfs=path` 共用一个 handler，proot.h:95-98）。**文档即配置**：解析与 usage 共用一张 Option 表（proot.h:76-348）——但此链在 Termux fork 已事实断裂（见下节）。**收集与固化两阶段**：handler 只收集原始字符串，canonicalize 推迟到 rootfs 已知的 `initialize_bindings`（cli.c:408-412 注释），六个 HOOK_CONFIG 钩子（:396-404 宏）让工具在关键节点注入默认值（proot 的 pre_initialize_bindings 补 cwd="."、rootfs="/"，proot.c:377-388）。**退出码与解析中止解耦**：全局 `exit_failure` 默认 true（cli.c:442），`-h`/`-V` 置 false 后 return -1 中止（proot.c:228-229,235-236），main 据此区分"用户要的信息"与"真失败"（cli.c:510-515）。**失败现场的父子身份判定**：launch_process 失败返回时可能身处子进程（fork 成功 execve 失败），`getpid() != pid` 分支直接 `_exit` 绕过 talloc 析构（cli.c:497-500）——子进程 syscall 已被父进程翻译，析构器删 glue/绑定占位目录会误删 guest 内被绑定路径的真实内容（:490-496 注释）。**许可证内嵌**：`-V` 直接 write 出链接进二进制的 licenses 对象段（proot.c:213-214,224-226）。

## 六、新人提示

①**读码顺序**：cli.c:444 main → cli.c:296 parse_config → proot.h:76 proot_cli 选项表 → event.c:95 launch_process，四站即全链。②**改选项的真相**：proot.h:1 声称自动生成，但 fork 新增的 `-H`/`-p`/`-L`/`--link2symlink`/`--sysvipc`（proot.h:237-290）在 doc/proot/manual.txt 里 grep 不到（manual 仍是上游 v5.1.0 遗留 669 行）——本 fork 事实上手改 proot.h。③**排障第一站**是 `print_execve_help`（cli.c:127-153）：termux-exec 的 LD_PRELOAD 劫持 execve 路径（:132-137，建议 unset）、Ubuntu 内核 seccomp bug 触发 EPERM（:140-145，建议 `PROOT_NO_SECCOMP=1`）、通用五因清单（:147-152，脚本解释器/ELF loader/qemu 缺失等）。④环境变量速查：`PROOT_VERBOSE`（:469）、`PROOT_NO_SECCOMP`（event.c:145）、`PROOT_NO_MOUNTINFO`（:481）、`PROOT_IGNORE_MISSING_BINDINGS`（binding.c:492），四个都改变入口链行为。⑤argc==1 只打简短 usage（cli.c:310-313），`-h` 才是全量版。⑥`-q` 处理器（proot.c:73-145）顺带建两个绑定：host rootfs 绑到 `/host-rootfs`（HOST_ROOTFS 宏 tracee.h:416）+ `/dev/null` 盖住 `/etc/ld.so.preload`（:141-142），防 guest 的 preload 配置毒害 qemu。⑦彩蛋：`__cyg_profile_func_enter/exit`（cli.c:577-606）是 GCC `-finstrument-functions` 插桩钩子，按 :573-575 注释重编译可打印函数调用流。
