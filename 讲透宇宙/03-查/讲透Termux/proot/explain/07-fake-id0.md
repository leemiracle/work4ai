# 07 · fake_id0：uid=0 特权身份仿真与 .proot-meta-file. 元数据全链路

> 图谱锚：/usr-data/data2/repos/termux-repo/proot@b27d81a（v5.1.107.101）。所有 file:line 锚均经源码现场核实（2026-10-26）。本篇覆盖 L08 层（36 文件，全仓最大扩展），主文件 fake_id0.c 1543 行。

## 一、角色定位：PRoot 的第二重谎言

PRoot 核心只撒一个谎——路径（L03 canon/binding 把 guest 坐标系翻译给内核）。但在无 root 的 Android 上只有路径幻觉不够：Termux 里一切进程的真实 uid 是应用沙箱 uid（常大于 65535），而 rootfs 里的 apt、dpkg、systemd 脚本、`install -o root` 全都期待 uid 0。`fake_id0` 扩展补上第二重谎言——**身份**：让 tracee 的 `getuid()` 返回 0、`chown root:root` 不报 EPERM、`ls -l` 显示 root 属主，而内核那边自始至终是同一个真实 app uid。

入口在 CLI：`-i uid:gid` 直接调 `initialize_extension(tracee, fake_id0_callback, value)`（proot.c:175-188，重复指定只保留最后一个，proot.c:181-182）；`-0` 是糖，硬编码 `"0:0"` 走同一条路（proot.c:190-193）；`-S` 则叠加 `-0` + `-r rootfs` + 推荐绑定三件事（proot.c:267-282），即 Termux "伪 su" 一键形态。初始化时 `INITIALIZATION` 事件解析 `"uid:gid"` 字符串填 Config（fake_id0.c:1339-1349），`caps_active = (uid == 0)`（fake_id0.c:1364）——伪装成 0 号用户的进程从一开始就持有仿真版 CAP_SETUID/DAC_OVERRIDE。

该扩展有**两套编译形态**，由 `USERLAND` 宏开关：非 USERLAND（桌面 Linux 无 root 场景）只做轻量伪装——谎报 stat 里的 uid/gid、把 EPERM 改成成功、chown 参数换名（chown.c:9-26）；USERLAND（Android/Termux 打包形态，仓内 src/GNUmakefile 并无 `-DUSERLAND`，由 Termux 打包侧传入）才是重头戏——用 `.proot-meta-file.` 边车元数据文件把属主与权限位**真实落盘**（ONBOARDING.md 5.3 节）。分派表 `filtered_sysnums` 注册了约 77 个被滤系统调用（fake_id0.c:323-413，USERLAND 段 17 项 + 公共段 60 项），onboarding 数字锚 "193 case" 指的是全扩展分派 case 总数（ONBOARDING.md:28）。

## 二、内部结构：一个 Config、一套 meta 协议、两组仿真面

### 2.1 Config：每个 tracee 一份的假身份状态机

`Config`（config.h:7-43）是全部状态：r/e/s/fs 四组 uid 加四组 gid 共八元（严格镜像内核 per-process 凭证）、`umask`、两个能力位，USERLAND 下再挂 `pending_path`/`pending_mode`（config.h:40-41，chmod/ACL 的延迟落盘槽）。fork 时 `INHERIT_CHILD` **深拷贝**而非共享——uid 变更不该跨进程传染（fake_id0.c:1397 memcpy，注释解释 glibc 靠信号让线程组各自重调 syscall，PRoot 因此无须关心 clone flags）；`pending_path` 清 NULL 因它属于父进程的当前 syscall（fake_id0.c:1400）。

`caps_active`（config.h:27）是这套仿真的灵魂：模拟内核"setuid 族永久降权即清能力"规则——r/e/s uid 从"至少一个 0"变为"全非 0"时清掉（`MAYBE_DROP_CAPS`，fake_id0.c:116-121），`keep_caps` 镜像 `prctl(PR_SET_KEEPCAPS)`（fake_id0.c:1053-1066 只观测成功的调用），execve 一律清 keep_caps（fake_id0.c:1300），而执行 setuid-root 二进制则重授（fake_id0.c:1306-1311）。没有这两个位，`su` 类程序 drop 回普通用户后仍能无限次 `setuid(0)` 回去，与真实内核语义不符。

### 2.2 身份伪装面：把 8 个 get 与 16 个 set 全部接住

**读侧**在 exit 改写：`getuid/geteuid/getgid/getegid` 直接 poke `config->ruid/euid/...`（fake_id0.c:1068-1086）；`getresuid/getresgid` 要写 tracee 内存，经 `POKE_MEM_ID` 宏按 ABI 选 16/32 位宽度（fake_id0.c:98-106）——32 位 ABI 上的旧版 getresuid 只写 16 位，而 Android 应用 uid 普遍超 65535，窄写会留下高位残留脏数据（fake_id0.c:92-97 注释）。execve 出口还调 `adjust_elf_auxv` 改写栈上 ELF 辅助向量 AT_UID/AT_EUID/AT_GID/AT_EGID（fake_id0.c:552-568），否则静态链接或早起的程序会从 auxv 读到真实 uid 绕过 libc。

**写侧**在 enter 一律 `set_sysnum(tracee, PR_void)` 完全仿真（fake_id0.c:782-803，涵盖 setuid/setgid/setre*/setres*/setfs* 及 USERLAND 的 umask），真正的状态机由四个宏在 exit 阶段执行：`SETXID`（fake_id0.c:126-161）、`SETREXID`（:176-235）、`SETRESXID`（:247-290）、`SETFSXID`（:295-315）。每个宏逐条抄 man page 的权限规则注释——非特权调用者只能把 id 设成 r/e/s 三者之一（:136-139），特权调用者改 euid 连带 ruid/suid（:146-149），euid 变化连带 fsuid（:151-155）。setfsuid 特殊：它**从不报错**，失败时返回当前值（:310-313），与真实内核怪癖一致。

**stat 伪装**：非 USERLAND 下 `handle_stat_exit_end` 只做一件事——若内核返回的属主等于真实 uid 就改写成 `config->suid`（stat.c:44-50），即"自己创建的文件在 guest 里显示为伪装身份"；USERLAND 下则优先走 meta 文件覆写（见 2.4）。statx 系统调用单独挂钩：statx.c:133 `notify_extensions(STATX_SYSCALL)` 把缓冲区交给扩展，`fake_id0_handle_statx_syscall` 用 meta 覆写 stx_mode/stx_uid/stx_gid（stat.c:184-194）。

### 2.3 meta 元文件协议：三行文本的影子 inode

USERLAND 的核心问题：host 上所有仿真用户实际是**同一个真实 uid**，真实权限位只能表达一种属主关系。解法是给需要"非默认身份"的文件配一个边车元文件，命名约定 `<dir>/<name>` → `<dir>/.proot-meta-file.<name>`（`META_TAG`，helper_functions.h:13；`get_meta_path` 负责 cwd/尾部斜杠规整与拼接，helper_functions.c:307-337）。注意前缀是 **`.proot-meta-file.`** 而非流传的 `.proot.meta`（ONBOARDING.md:95 勘误钉版）。

文件格式是三行十进制文本：`fprintf(fp, "%d\n%d\n%d\n", dtoo(mode), owner, group)`（write_meta_file，helper_functions.c:385）。mode 先经 `dtoo` 从内部二进制转成"八进制数值的十进制书写"（如 0600→"600"，helper_functions.c:22-33），读回用 `fscanf("%d %d %d")` + `otod` 还原（helper_functions.c:357-358, 38-53）。属主字段存的就是**伪装的** uid/gid。关键回退：meta 不存在时 `read_meta_file` 不报错，而是返回 755 + 当前 euid（helper_functions.c:349-355）——默认信任真实文件系统的权限视图，meta 只记录"想说谎的部分"。`is_creat` 为真时写入前套 umask（helper_functions.c:382-383），对应 open/mkdir 这类真实 syscall 内核本会做同样的事。

**谁创建 meta**：open/creat 带 O_CREAT 且目标不存在时（open.c:57-74）、mkdir/mknod 时（mk.c:42-43），内容是 `mode & ~umask & 0777` + euid/egid。**谁移动/删除**：rename 在 exit 阶段跟着搬（rename.c:46-50 注释说明 enter 只查双父目录写权限、exit 才动 meta；RENAME_EXCHANGE 交换双方 meta，rename.c:16-44）；unlink/rmdir 删除对应 meta（unlink.c:101-102），rmdir 前还要扫掉"目标文件已不存在的孤儿 meta"否则目录清不掉（`remove_orphaned_meta_files` 两遍扫描先验后删，unlink.c:17-62）；open 出口另有一道兜底——文件不存在而 meta 存在时顺手清理（fake_id0.c:1206-1238）。link2symlink 扩展仿真硬链接时，经 `LINK2SYMLINK_RENAME/LINK2SYMLINK_UNLINK` 事件请求 meta 沿符号链接链迁移或删除（fake_id0.c:1422-1463）——Android 无硬链接能力，文件被替换成 symlink 链后 meta 必须跟着链尾走，否则权限查询断链。

### 2.4 `mode|0700`：真实文件上的强制访问权

因为一切仿真用户实际共享一个真实 uid，任何文件若真实权限位不含 owner 读写，PRoot 自己（以及 tracee 借真实 uid 发起的后续 open）就打不开它。所以创建类 syscall 的 mode 参数在 enter 阶段被改写：`poke_reg(tracee, mode_sysarg, (mode|0700))`（open.c:73、mk.c:42）。0700 是"owner rwx"——目录还需要 x 位才能穿越，一并给足。内核真正落盘的是这个放大后的 mode，guest 视角的"真实" mode 存在 meta 里。

读路径的对称物是 `get_real_mode`（chmod.c:45-55）：`(mode & 01777) | S_IRUSR | S_IWUSR`——真实文件只保留 meta mode 的低 12 位并恒加 owner rw，目录或有任一 x 位时再加 S_IXUSR；**set-id 位不落到真实文件**（注释 chmod.c:39-44 明说：set-id 留在 meta 里）。chmod 的完整协议是延迟两拍：enter 校验属主（euid 等于 meta owner 或为 0，chmod.c:98-99，非特权改他人文件报 EPERM）后只记 `pending_path/pending_mode` 并把改写后的 real_mode 交给内核（chmod.c:107-113）；exit 若内核成功且 meta 仍在，才把 pending_mode 写回 meta（chmod.c:119-139）。顺序不能反——内核可能失败，meta 必须只记已生效的模式。POSIX ACL 亦同构：setxattr(`system.posix_acl_access`) 会改权限位，enter 挂 pending（chmod.c:141-178），exit 从真实文件 st_mode 抠出 0777 位并回写 meta、再补 chmod 把 owner 访问权还给真实 uid（chmod.c:184-210）。

### 2.5 meta 读路径：三层权限校验

带 meta 的文件被访问时，内核权限检查**形同虚设**（真实 mode 恒含 owner rw），真实把关的是扩展自己在 userspace 重放的一套迷你 DAC：

1. **逐级上溯**：`check_dir_perms`（helper_functions.c:242-279）从目标父目录开始，对路径每个 guestfs 祖先目录查 meta 取 x 位（'r' 类型还要求父目录 w，'w' 类型要求直接父目录 w），任何一级缺 x 即 EACCES——这是 userspace 版的目录搜索权限。
2. **三档选择**：`get_permissions`（helper_functions.c:191-234）按 `emulated_uid==owner || emulated_uid==0` 取 OWNER 档、`emulated_gid==group` 取 GROUP 档、否则 OTHER 档，再用 `doo` 后除法取模剥出对应一位八进制（:218-226）。
3. **root 补 rw**：伪装 uid 0 时 `omode |= 6`（:231-232），对齐 root 的 DAC_OVERRIDE；注释还诚实记下怪癖：su 与 sudo 对 400 文件行为不同（:228-230）。

消费方：open 的 access_mode 对照表（O_WRONLY 需 w、O_RDONLY 需 r、O_RDWR 需 rw，open.c:84-92，缺则 EACCES）；execve 查 x 位（exec.c:41-43）并按 meta 的 S_ISUID/S_ISGID 位切换 Config 到全 0 身份（exec.c:46-57，setuid-root 二进制的仿真）；utimensat 查 owner（utimensat.c:53-58）；chown 按 euid==0 可改属主、普通 owner 只能改组、否则 EPERM 三分支落 meta（chown.c:84-95，:87-88 的 TODO 承认未校验"组必须是本人所属组"）。

### 2.6 伪装面的外围：chroot、网络凭证、SIGSYS

**chroot**（chroot.c:10-125）：euid==0 且内核报 EPERM 时接管——目标 realpath 与现根相等则直接伪造成功（:57-63）；目标是目录则**整个换掉 tracee 的绑定命名空间**：talloc_unlink 旧 `tracee->fs`、`new_binding(path_host_absolute, "/")`、`initialize_bindings`、恢复 cwd（:104-115）。新根下若嵌有其他绑定则不支持（:84-94 检测，返回 ENOSYS/放行），因为一套绑定表表达不了"挂载点在 chroot 外"。

**网络凭证双向改写**：入向 `getsockopt(SO_PEERCRED)` 在 exit 把对端 ucred 的 uid/gid 换成**对端 tracee 自己的 Config**（getsockopt.c:36-44，按 cred.pid 查 `get_fake_id_for_pid`；对端不在本 PRoot 下但真实 uid 相同时借用本 tracee 身份，:40-41）——两个都伪装 0 的进程互看 uid 0，一致成立。出向 `sendmsg` 的 SCM_CREDENTIALS 反向操作：enter 阶段遍历 cmsg 把 ucred **还原成真实 getuid()/getgid()**（sendmsg.c:164-168）——不还原的话内核会以"凭证与真实 uid 不符"拒绝消息。一进一出，对内谎报、对外诚实。另 socket(AF_NETLINK, NETLINK_AUDIT) 在 euid==0 且 EPERM 时改报 EPROTONOSUPPORT（socket.c:14-20），安抚探测 audit 的程序。

**SIGSYS 通道**：Android 沙箱的 seccomp 策略直接封杀 setuid 族等调用（不走 EPERM 而是投递 SIGSYS）。扩展在 `SIGSYS_OCC` 事件里对 setuid 族与 chroot 复用同一套仿真宏（fake_id0.c:1483-1515 → handle_sigsys :1246-1283），返回 1 吞掉信号。seccomp.c:67-69 注释钉版了这里的一个真实 bug 教训：SIGSYS 时没有 sysenter 停靠点，寄存器快照是上一个 syscall 的，曾把 statx 误当 chmod 处理——修复是 `set_original_regs_after_seccomp` 用 CURRENT 覆盖 ORIGINAL。

## 三、外部连接

**上游**：cli/proot.c 的 `-i/-0/-S`（proot.c:175-193, 267-282）是唯一实例化入口；syscall 主循环经 extension.c 事件分发把 SYSCALL_ENTER_END/SYSCALL_EXIT_END/SYSCALL_EXIT_START/INITIALIZATION/INHERIT_* 送达 `fake_id0_callback`（fake_id0.c:1325-1534）。路径翻译每经过一个 host 路径都触发 `HOST_PATH` 事件（fake_id0.c:1405-1414）：euid==0 时 `override_permissions` 临时 chmod 加 rw（目录加 x）模拟 CAP_DAC_OVERRIDE（fake_id0.c:432-531），并靠 **talloc 析构器逆序回调**恢复原 mode（restore_mode :420-424 + `talloc_set_destructor` :526，注释 :524-525）；final 分量的恢复模式按 syscall 语义区分——chmod 类恢复成"新 mode"、stat 类完全不动（否则 stat 前临时改权限就穿帮）、其余恢复原样（:470-514）。

**协同**：link2symlink（meta 沿链迁移，见 2.3）；hidden_files 扩展把 `.proot-meta-file.*` 从 guest 目录列表里隐去（unlink.c:12-15 注释点明没有它孤儿 meta 会让 rmdir 报 ENOTEMPTY）；path/ 的 `translate_path`/`belongs_to_guestfs` 判定 meta 链只在 guestfs 内生效（helper_functions.c:92, 167）；f2fs-bug.c 规避 Termux 设备 f2fs 的 stat 误报（fake_id0.c:440-441）。

**下游**：真实内核——所有 chmod/chown/open 的**真实动作仍然执行**（参数被换写后），meta 与真实文件双轨并行；statx.c 的 STATX_SYSCALL 钩子（statx.c:133）是新式 stat 的统一出口。

## 四、数据流

**链路一：`proot -0` 下 `chmod 0600 /etc/shadow`**。INITIALIZATION 已把八元 id 全设 0（fake_id0.c:1356-1363）。chmod enter：算出 meta 路径 `$rootfs/etc/.proot-meta-file.shadow`；meta 存在（之前 open 落的），读出 owner=0；euid==0 通过属主检查（chmod.c:98-99）；mode 参数 0600 截取 07777 位存入 pending（:103-110）；真实 mode 被改写为 `get_real_mode(0600)` = 0700（:45-55, :112）交给内核。内核对真实文件 chmod 0700 成功。exit：`handle_perm_err_exit_end` 放行、`handle_chmod_exit_end` 见 pending 且成功，把 "600\n0\n0\n" 写入 meta（:130-135）。此后 `ls -l /etc/shadow` 走 stat exit：meta 命中，`st_mode = meta_mode | (真实文件的类型位|07000)`、`st_uid/st_gid = meta 的 0/0`（stat.c:130-146）——guest 看到 `-rw------- root root`，而 host 上该文件实际是 0700 属主为 app uid。

**链路二：普通用户新建文件**（`-i 10233:10233` 打开仿真非 root 会话）。`echo x > /tmp/a` → openat 带 O_CREAT：目标不存在，走创建分支——check_dir_perms('w') 逐级查 /tmp 链的 meta x/w 位（open.c:68）；mode 参数被 poke 成 `mode|0700`（:73）；`write_meta_file(meta, mode&~umask, euid=10233, egid)` 落盘（:74）。umask 仿真在 exit：`PR_umask` 被整个 void 掉，返回旧值、Config 更新（fake_id0.c:1097-1100）。

**链路三：daemon 降权**。`setuid(65534)` 在 enter 被 void（fake_id0.c:782-803），exit 走 `SETXID`：euid==0 所以 r/e/s 全设 65534（fake_id0.c:146-149）；`MAYBE_DROP_CAPS` 发现从"有 0"到"无 0"，caps_active 清 false（:116-121）——此后再 setuid(0) 会因 `allowed=false` 收到 EPERM（:136-141），除非执行了 setuid-root 二进制重新点亮（fake_id0.c:1306-1311）。

## 五、设计决策

1. **两套形态而非一套**：桌面 Linux 上真实 uid 唯一但权限模型完整，轻量伪装（EPERM→0 + stat 换 uid）就够；Android 上跨 uid 的文件共享全走同一个真实 uid，才需要 meta 全链路。`#ifdef USERLAND` 遍布 36 文件，fake_id0.c:829-830 注释点破约束：非 USERLAND 连 helper_functions.h 都不包含，openat 处理只能用裸 `read_string`。
2. **边车文件而非 xattr/数据库**：同目录隐藏文件让 meta 与目标同生共死——rename 原子性天然继承、删除/归档自动跟随、无全局索引要维护；Android 共享存储上 xattr 的权限与支持度都不可靠。代价是目录里多了可见文件（交给 hidden_files 扩展擦除）与孤儿清理负担（unlink.c:17-62 + fake_id0.c:1206-1238 两道防线）。
3. **`mode|0700` 与 get_real_mode 的"越狱方向"**：真实文件权限被故意放大、真实 set-id 位不落盘（chmod.c:50-54）——越狱的永远是 guest 视角。这套设计自洽的前提是"host 上只有一个真实 uid 在操作这些文件"；若有真实 root 进程按真实权限位审计，看到的将是被污染的 mode。
4. **能力位镜像内核而非拍脑袋**：caps_active/keep_caps/execve 清除/setuid-root 重授四条规则（2.1）严格复刻内核 capability 语义，setuid 族仿真因此能在 su/sudo/passwd 这类多级降权提权程序下不穿帮。config.h:20-32 的注释本身就是一份内核规则摘要。
5. **网络凭证不对称策略**：入向谎报（SO_PEERCRED 查对端 Config）、出向还原真实（SCM_CREDENTIALS）——方向搞反任何一个，要么对端内核拒收、要么本地进程识破。getsockopt.c:37-41 还处理了"对端不在本 PRoot"的边界。
6. **EPERM/EACCES 选择性伪造**（fake_id0.c:596-602）：只把权限类错误改成成功，ENOENT/ENOTDIR 等照实透传——mknod/sethostname 等"伪特权"调用失败于权限时视作成功，其他失败必须诚实。xattr 分支甚至传 `even_if_not_root=true`（fake_id0.c:1158），因为 ACL 无特权限制语义更宽。
7. **PR_getuid 当"drop 哨兵"**：guestfs 外的路径要静默丢弃 chmod/chown，做法是 `set_sysnum(PR_getuid)`（chmod.c:81, chown.c:52/97），exit 端把该伪 syscall 的非零结果统一归 0（fake_id0.c:590-593）。选 getuid 是因为它无副作用、成本最低。
8. **ARM 寄存器别名防御**：ARM/ARM64 上 syscall 结果写 SYSARG_1（与第一参数别名），读路径参数须用 MODIFIED 版本（helper_functions.c:131-136 注释），fstat 更是被整个转译成 readlinkat("/proc/pid/fd/N") 再回填（stat.c:60-76 + fake_id0.c:988-1016 链式 newfstatat 补刀）。

## 六、新人提示

**阅读路径**：config.h（40 行，全部状态）→ helper_functions.h:10-13（两个关键宏）→ helper_functions.c 的 `get_meta_path`/`read_meta_file`/`write_meta_file`/`check_dir_perms`（协议四件套，helper_functions.c:307-388, 242-279）→ open.c（95 行，创建+校验最典型）→ chmod.c（延迟落盘范式）→ 最后 fake_id0.c 的 callback 大分派（:1325-1534）。ONBOARDING.md 5.3 节是现成的索引地图。

**钉版坑位**：① `dtoo/otod` 是纯算术进制互转不是格式化——meta 文件里 "600" 是八进制值的十进制书写，直接 `stat -c %a` 对照时别被绕晕（helper_functions.c:22-53）；② `check_dir_perms` 的 `rel_path` 参数是**相对基点**（通常 dirfd 对应路径），上溯循环条件 `strlen(rel_path) < strlen(shorten_path)`（helper_functions.c:263）决定爬多高，传错会漏查或多查层级；③ `pending_path` 生命周期短于单次 syscall——enter 末尾与 exit 开头都有 `TALLOC_FREE` 清场（chmod.c:73, 137），嵌套/链式 syscall 想复用必须重新挂；④ chmod 的 meta 写入是**条件成功**——内核失败或 meta 中途被删都不写（chmod.c:130-132 三重与条件），改这段时别把顺序"优化"掉；⑤ 非 USERLAND 构建没有 helper_functions，`handle_sysenter_end` 里两段 `#ifndef USERLAND` 的 openat/chown 代码用裸 API（fake_id0.c:805-906），与 USERLAND 分支同名函数签名不同（chown.h 双签名）；⑥ 真实边界：绑定到 guestfs 之外的路径（`-b /sdcard`）上 meta 链不生效（`read_sysarg_path` 返回 1 即放行，helper_functions.c:166-168），那里只有真实 uid 的真实权限；⑦ chown 的 owner 校验有已知 TODO——普通用户改组未校验组成员资格（chown.c:87-88），"完整 chown(2) 语义"在这个扩展里是有意的近似。

**与真实 rootfs 权限的边界**（收尾钉版）：fake_id0 改变的是 tracee 的**观测与请求**，内核仍是最终守门人——真实 root 进程、其他 PRoot 实例、host 上的 audit 子系统看到的都是真实 uid 与被 0700 放大过的 mode。元文件三行文本也毫无加密，host 侧 `ls -a` 一眼见底。它仿真的是"单机单用户假装多用户"的权限**语法**，而不是权限**强制力**。
