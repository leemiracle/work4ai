# proot 入驻指南（ONBOARDING）

> 图谱锚：仓 /usr-data/data2/repos/termux-repo/proot@b27d81a（v5.1.107.101）；锚均经源码核实。

## 1. 一句话定位与治理

proot 是 chroot、`mount --bind` 与 binfmt_misc 的用户态仿真器：不要 root、setuid 助手与 namespace，只假设 `ptrace()` 可用（`AGENTS.md:3-5`）。被跟踪进程的每个 syscall 都被截停，参数里的 guest 文件系统视图被翻译成 host 真实路径再放行——Termux 免 root 跑完整发行版的核心 C 实现。

治理四条：① termux 对上游 proot-me/PRoot 的 fork（`README.md:5`），永久分叉不同步（`AGENTS.md:18-19`）；② GPLv2（`COPYING:35`），版权 STMicroelectronics；③ 维护态铁律（`AGENTS.md:50-62`）：只收 bug 修复/新 syscall 处理器/设备兼容改进，拒新特性与大重构、拒自动化扫描报告，doc/ 过时勿动（:14）；④ 开 PR 必附真机测试（:70-84，裸 Linux≠Android）。

## 2. 仓库全景

src/ 按子系统：`tracee/`（Tracee 状态机+事件循环）、`syscall/`（翻译链+seccomp 加速）、`path/`（canon/binding/proc/glue/f2fs-bug）、`ptrace/`（嵌套 ptrace/wait4 仿真）、`execve/`、`loader/`（freestanding 加载器，无 libc）、`extension/`（框架+fake_id0 36 文件+link2symlink/sysvipc 重型仿真+轻量钩子）、`cli/`（main+选项）；根级 arch.h/compat.h 零依赖。

数字锚：enter.c 3069 行（主分派起 :1887）；link2symlink.c 1985 行；fake_id0.c 1543 行；Tracee 结构体（`tracee.h:75-414`）fan-in 76 全仓第一。tests/：112 个 `test-*.sh`+40 个 `test-*.c`（一缺陷一 hash 回归）+29 个工具程序编入 rootfs。doc/ 为上游 v5.1.0 遗留，但 `doc/GNUmakefile:17` 从 manual 生成 `proot.h`（文档即 CLI 配置）。

## 3. 架构分层速览（14 层自底向上）

| 层 | 名称 | 要点锚 |
|---|---|---|
| L01 | 跨架构基础 | arch.h:31；sysnums.list 458 行 X-macro |
| L02 | Tracee 运行时核心 | tracee.h:75-414；event.c:314 |
| L03 | 路径翻译与绑定 | canon.c:199；binding.h:40-42 三队列 |
| L04 | Syscall 翻译链 | enter.c:1887；exit.c:58 |
| L05 | 嵌套 ptrace 仿真 | ptrace.c:233；wait.c:87/181 |
| L06 | execve 与内建 loader | execve/enter.c:596；loader.c:31-37 |
| L07 | 扩展框架与轻量钩子 | extension.h:33-176 21 事件 |
| L08 | fake_id0 特权仿真 | 193 case；.proot-meta-file. 元链 |
| L09 | 重型仿真扩展 | link2symlink.c:30；sysvipc_shm.c:495 |
| L10 | CLI 入口与诊断 | cli.c:444 |
| L11 | 构建体系与 CI | GNUmakefile:147；tests.yml:23 |
| L12 | 文档与治理 | doc/GNUmakefile:17 |
| L13 | 测试基础设施 | tests/GNUmakefile:36-39 |
| L14 | 回归用例集 | 112 sh+40 c |

心法：L01-L02 地基心脏，L03-L06 翻译主线，L07-L09 仿真层，L10-L14 外围；改内核先读 L02，改文件系统先读 L03。

## 4. 核心数据流：一次 syscall 的翻译旅程

以 `openat("/etc/hosts")` 为例：

1. **启动 attach**：main（cli.c:444）调 launch_process（event.c:95）fork 被跟踪进程，子进程在 event.c:130 PTRACE_TRACEME 后 exec 目标——此后每个 syscall 停两次（无 seccomp 时）。
2. **stop 分派**：event_loop（event.c:314）阻塞于 `waitpid(-1,...,__WALL)`（event.c:416），syscall stop 交 translate_syscall（syscall.c:140）。
3. **enter 翻译**：先经 notify_extensions(SYSCALL_ENTER_START) 让扩展截胡，再按中立 Sysnum 进巨型 switch；路径参数走 translate_path（path.c:370）→canonicalize（canon.c:199）解 symlink+绑定替换得 host 路径写回寄存器/内存（mem.c:241）；改写前后值分存 ORIGINAL/CURRENT（reg.h）。
4. **内核执行**：resume 后内核以 host 路径真执行——proot 不代理执行，只改参数。
5. **exit 修正与 restart**：第二停进 translate_syscall_exit（exit.c:58）：readlink/read 缓冲、uname、statfs 等输出要"圆谎"（detranslate_path，path.c:454）；enter 阶段登记的链式 syscall 由 chain_next_syscall（syscall.c:283）逐条推进并交还控制权（:301）。seccomp 加速（seccomp.c:109-112）让无关调用直通，只让需翻译者停机。

一句话：**enter 翻译输入、内核干活、exit 翻译输出、chain 追加注入**。

## 5. 关键机制深潜

### 5.1 tracee 生命周期
Tracee 结构体（tracee.h:75-414）集中一切状态：绑定三队列引用（:54-60）、内嵌 as_ptracer/as_ptracee 会话（:176/:194）、链式 syscall 队列与 load_info（:287-300）。生命周期归 talloc：tracee.c:187 创建、析构链自动回收子对象（:57-98）；fork/clone 经 INHERIT_PARENT/CHILD 事件继承扩展配置。近期提交集中修此层竞态。

### 5.2 路径 canon 双向翻译
canonicalize（canon.c:199）单向 guest→host：逐分量推进、实时解 symlink、处理 .. 与结尾 /./、substitute_binding 做 host 前缀替换。绑定集由 binding.h:40-42 的三条 CIRCLEQ 环形队列组织，最长前缀优先匹配。反向 detranslate_path（path.c:454）把内核输出换算回 guest 维持 ps/pwd 自洽；proc.c:43 仿真 /proc/<pid>/{fd,exe,cwd,root} 魔术链接；glue.c:106 影子目录仿真只读 rootfs 可写。f2fs-bug.c:19 fork 探测 f2fs 大小写误报 EEXIST（:56-78）并绕行受影响路径（:116）——Termux 独有。

### 5.3 fake_id0 元文件链
193 case 拦截 getuid/setuid/chown/stat 等 70+ 调用谎报 uid/gid=0；USERLAND 模式（chmod.c:13）让属主与权限位真实落盘，元文件前缀 .proot-meta-file.（helper_functions.h:12-13，非流传的 .proot.meta）。open.c:57-74 在 O_CREAT 时按 umask 写 meta；read_meta_file（helper_functions.c:344-362）读回，缺文件回退 755+当前 euid；check_dir_perms（:242-279）父目录逐级上溯校验；stat 出口由 statx.c:133 notify_extensions(STATX_SYSCALL) 挂钩。配套：exec.c:47 依 S_ISUID 实现 setuid；getsockopt.c:29/sendmsg.c:155 改 SO_PEERCRED/SCM_CREDENTIALS；chroot.c:10 转译为换根绑定。

### 5.4 link2symlink 硬链接伪装
无 root 文件系统不支持硬链接：link(2) 被实现为"原文件移入 .proot.l2s. 元数据目录（link2symlink.c:30）+原位留符号链接"，getdents（:1537-1538）/statx 出口维护 st_nlink、unlink/rename（:267）同步元数据（fix_symlink_size 补 size 维度）；.proot 前缀条目由 hidden_files（hidden_files.c:20，:51）从 getdents 流剔除。

### 5.5 execve loader 改写
translate_execve_enter（execve/enter.c:596）展开 shebang 与 QEMU runner，从 ELF 程序头收 PT_LOAD（:57）/PT_INTERP（:164）成 LoadInfo，把 execve 改写为执行内建 loader；translate_execve_exit（execve/exit.c:411）把 LoadInfo 转录成加载脚本注入栈、按 ABI 复位四个启动寄存器。loader.c 为注入侧 freestanding 解释器：无 libc，按 script.h:29-61 的 LoadStatement 协议逐条执行，syscall 桩按架构条件包含裸汇编（:31-37）。

### 5.6 扩展注册协议
ExtensionEvent 枚举实测 21 种（extension.h:33-176；图层记 23，勘误）：路径钩点、syscall 四相拦截、fork 继承协商、SIGSYS_OCC/STATX_SYSCALL 专用事件。notify_extensions（:210）约定返回 >0=PRoot 跳过自身处理、<0=报 errno；扩展以 talloc config 挂 Tracee 获生命周期与继承，filtered_sysnums 供 seccomp 布防。轻量钩子如 kompat 谎报内核版本（kompat.c:54-74）、port_switch 特权端口+2000（port_switch.c:14）等四个。sysvipc 纯用户态 SysV IPC：shm 经独立 helper（cli.c:457-458）用 SCM_RIGHTS 分发 memfd（sysvipc_shm.c:495,908）。

## 6. 构建与测试

- **构建=纯 GNUmakefile，无 CMake**（全仓无 CMakeLists，勘误钉版）。`make -C src` 编 60+ 对象；特性探测：GNUmakefile:147 CHECK_FEATURES=process_vm seccomp_filter，src/.check_process_vm.c 与 .check_seccomp_filter.c 编译链接成败生成 build.h（:163）的 HAVE_* 宏——mem 通道与 seccomp 加速由此构建期选定。
- **测试 harness**：tests/GNUmakefile:20 把全部用例展开成 check-% 目标（:36-39），make check 逐一运行、退出码 125 记 skipped（:118）。冒烟=test-00000000.sh；路径全矩阵=test-11111111.sh 两阶段 CSV 对照；嵌套跟踪=tests/test-ptrace00.c。validation.mk 编排 LTP/coreutils 等发布级大验证。
- **CI**：.github/workflows/tests.yml 三矩阵 amd64-gcc/amd64-clang/arm64-clang（:23）跑 make check。

## 7. 新人上手路径（16 步导览精简为 9 里程碑）

1. 门面：README.md+AGENTS.md（fork 身份与铁律）；manual.txt 知道即可。
2. 入口：cli.c:444 main→proot.c 选项→launch_process（event.c:95）。
3. 地基：arch.h+sysnums.list X-macro，理解"中立 Sysnum"。
4. 心脏：tracee.h 逐字段读 Tracee，再看 event.c:314-416 分派。
5. 翻译主线：syscall.c:140→enter.c:1887→exit.c:58+chain.c；重点 enter.c:573-639 netlink 伪造应答（Termux 沙箱关键补丁）。
6. 路径子系统：canon.c:199→binding.h 三队列→path.c:370/454→proc/glue/f2fs-bug。
7. 扩展体系：extension.h 21 事件+返回值约定；读 kompat/hidden_files/port_switch 找感觉。
8. 两大重型：fake_id0 从 meta 读写切入；link2symlink 从 .proot.l2s. 移动+symlink 策略切入。
9. 收尾：execve 三件套、GNUmakefile 特性探测、跑 make -C tests check——之后可改第一个 bug。

## 8. 延伸阅读

- **知识图谱**：仓内 .understand-anything/knowledge-graph.json（892 节点/1861 边@b27d81a）。
- **DeepWiki 中文精讲**：讲透Termux/proot/deepwiki/（8 章 100%）。
- **上游与生态**：proot-me/PRoot（已不同步上游）；同目录 proot-distro 是用户面消费方。
- **内核前置**：ptrace(2) 两段停机、seccomp(2) BPF、SCM_RIGHTS。

> 勘误钉版（源码实测）：①扩展事件 21 种非 23；②fake_id0 元文件前缀 .proot-meta-file. 非 .proot.meta；③构建纯 GNUmakefile 无 CMake。
