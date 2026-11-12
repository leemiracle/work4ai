# 06 · login 子包：会话进入核心——从共享锁到 fchdir+exec 的全程

> 层位：L06「login 子包层」（图谱 14 层中 fan-out 最大的命令层）。覆盖八文件共 1830 行：
> `proot_distro/commands/login/__init__.py`（671 行，主编排）、`proot_cmd.py`（311 行，argv 组装）、
> `env.py`（320 行，环境合成与 profile.d 注入）、`passwd.py`（113 行，容器内账本查询）、
> `bindings.py`（84 行，Android 域 bind 表）、`detach.py`（179 行，双 fork 守护化）、
> `quoting.py`（45 行，POSIX 双引号）、`migrate.py`（107 行，legacy 目录迁移）。
> 所有行号锚均于 2026-10-27 在仓内现场核实。

## 一、角色定位：全仓的"终点命令"与它的七位助手

install/build/copy 的一切准备，最终都为了让 `proot-distro login <name>` 把用户送进容器。login 子包是图谱里 fan-out 最大的命令实现：`run` 命令读完镜像 Entrypoint/Cmd 后注入 `args._run_inner`（run.py:150）**完全委托** login 执行，所以这里同时是 login 与 run 两条命令的运行时。

模块头的分工自述（`__init__.py:21-32`）把这个子包切成七块：主编排（`__init__.py`）、passwd 账本查询、Android bind 表、环境合成、argv 组装、detach 守护化、legacy 迁移，外加一个 45 行的引号工具。这个切法不是按代码量，而是按**信任边界**：每块都对应一类"名字不可信"的输入（容器内文件、宿主 Android 路径、镜像 Env、用户 --bind），各自在自己的模块里把拒绝逻辑收口。

主编排 `_command_login_inner`（`__init__.py:313`）的骨架是一条直线：迁移 legacy 目录 → 钉住 container/rootfs 两个 fd → 判发行版类型 → 解析用户 → 合成环境 → 组装 argv → 写 profile.d 片段 → 探测架构 → 注册会话 → `os.fchdir` + `execvpe` 变身 proot（`__init__.py:601`）。前台的 Python 进程到 exec 那一刻就消失了——"login 是 exec 不是 spawn"是理解全模块的第一把钥匙。

## 二、内部结构：八模块逐个拆

### 1. `__init__.py`：编排主线与三个决策函数

入口 `command_login`（`__init__.py:81`）先做两件事：`require_valid_name` 校验容器名，然后以**共享锁**（`exclusive=False`）包住全部流程（`__init__.py:92-95`）。`inheritable=True` 清掉 O_CLOEXEC，使锁 fd 能穿过 execvpe 被 proot 继承——注释（`__init__.py:86-91`）点明：exec 成功则进程被替换、`__exit__` 永不调用，锁随会话全程存活；这正是 ONBOARDING 第 5 节"锁 fd 活着即会话活着"的源头。共享而非排它是设计选择：多个会话可以同时进同一容器。

`_detect_dist_type`（`__init__.py:98`）以"rootfs 里是否存在 `$TERMUX_PREFIX/bin/login` 这个**文件**"区分 termux 型/普通型（`__init__.py:113-115`）。两个坑写进了 docstring：一要查文件不能查目录（并发会话会把 bind 目标目录实体化到宿主，目录检查会误判）；二必须走 guestfile 按 chroot 语义问 rootfs，不能拼宿主路径——`os.path.isfile("<rootfs>/data/...")` 会顺着 guest 植入的 `data -> /` 直达**宿主的** Termux login 二进制（`__init__.py:106-111`）。这个判定决定整个会话的形态（环境、bind、是否传 --change-id），错了全错。

`_resolve_login_user`（`__init__.py:118`）把 `--user name[:group]` 翻译成 uid/gid/home/shell 四元组（`__init__.py:193-199`）。有 /etc/passwd 时按名字或数字查（数字走 `find_passwd_by_uid`，`__init__.py:139`），home/shell 缺省回退 `/` 与 `/bin/sh`（`__init__.py:142-143`）；没有 passwd 文件时只认 `root` 与纯数字 UID，一律 home=`/`、shell=`/bin/sh`（`__init__.py:173-191`）。

两个环境构造器 `_build_termux_env`（`__init__.py:202`）与 `_build_normal_env`（`__init__.py:243`）共享同一套叠层次序（详见第四节），差别只在基线：termux 型给 `HOME/PATH/PREFIX/TMPDIR` 四件套（`__init__.py:206-209`）；normal 型给 `DEFAULT_PATH_ENV`（constants.py:109-115，Termux 上额外拼 `$PREFIX/bin:/system/bin:/system/xbin`）加三个 Termux 兼容变量 `MOZ_FAKE_NO_SANDBOX/MOZ_SHM_NO_SEALS/PULSE_SERVER`（`__init__.py:253-255`）。

### 2. `passwd.py`：容器内账本，按 guest 语义读

全部查询走 `guestfile.read_guest_file`/`guest_file_exists`（passwd.py:48），即 ONBOARDING 所说"按 chroot 语义走读容器内文件"：逐分量 fd 步行、绝对符号链接在 rootfs 重锚、40 跳符号链接/4096 分量/1MiB 三个上限（guestfile.py:63,70,77）。模块头（passwd.py:23-46）记着历史 bug：旧实现拼 `<rootfs><guest path>` 交给 open()，host 内核解析中间分量，镜像带一个 `etc -> /etc` 就让 login 读到**宿主**的 passwd 并采用宿主用户的 uid/home/shell；FIFO 植入能把 login 永久挂死。现在每次入口都接受 `root_fd`——从 login 钉住的 rootfs 描述符起步（passwd.py:42-46）。`read_passwd_entry` 一次读全行字段（passwd.py:70-80），注释说明动机：逐字段重开文件给了账本四次在登录底下换内容的机会。

### 3. `env.py`：环境合成三源一闸 + profile.d 持久化

环境变量有四个来源，按固定优先级叠放：proot-distro 基线 → 镜像 Env → 身份变量 → 用户 `--env`。其中镜像 Env 被单独闸在 `image_env_pairs`（env.py:119）：`IMAGE_ENV_BLOCKED` 名单（env.py:83-88，含 Android 九变量、身份键、TERM/COLORTERM 等）拒之门外，`LD_*`/`PROOT_*` 前缀由 `is_host_exec_var` 拒绝（execenv.py:84）——docstring 给出攻击场景：镜像 `Env: ["LD_LIBRARY_PATH=/evil/lib"]` 加自带 libtalloc.so.2 等于**在容器外**以调用者身份执行代码（env.py:126-130）。`is_exportable` 再按 execve(2) 的硬约束过滤（NUL/不可编码/超 `MAX_ENV_STRING_BYTES`=32×4096，execenv.py:81,96）。

身份变量 `identity_env_pairs`（env.py:148）产出 `PD_CONTAINER` 与 `container=proot-distro`（env.py:165-166），有 manifest 时再给 `PD_IMAGE`/`PD_IMAGE_ID`（env.py:173,176）——guest 因此知道自己跑在哪个容器里。

`inject_termux_profile`（env.py:179）解决"登录 shell 会重置环境"：/etc/profile 重初始化环境，proot 传进来的一切会丢，所以往容器 `/etc/profile.d/` 投一个 `termux-profile.sh`（env.py:53），由每次 normal 型会话重写（`__init__.py:429-433`），内容是当前会话的环境快照。写入本身是 login 在宿主侧**写进 guest 领地**的唯一动作，所以全程持 fd：`_open_profile_d` 从 rootfs_fd 起步逐级 opendir_at（env.py:242-247），`_write_profile_snippet` 用 unlink+O_EXCL 造新 inode 而非覆写（env.py:302-304），chmod 走 `os.fchmod` 而非名字（env.py:316）——防止 guest 留一个 `termux-profile.sh -> 宿主文件` 的符号链接让下次登录截断宿主文件（env.py:209-215）。PATH 用 case 守卫追加保住系统 PATH 优先（env.py:267-273），每会话变量与 proot 内部变量经 `_PROFILE_INJECT_SKIP` 排除（env.py:96-101）。

### 4. `proot_cmd.py`：argv 组装的固定七段

`build_proot_args`（proot_cmd.py:55）按头注释规定的固定顺序吐参数（proot_cmd.py:24-33）：proot 二进制+QEMU 旗标 → Termux proot 扩展 → `--change-id` → `--rootfs/--cwd` + /dev /proc /sys 三基线 bind（proot_cmd.py:109）→ 非 minimal bind 域 → 用户 `--bind` + `-p` → 内部命令。关键行：

- `--change-id={login_uid}:{login_gid}`（proot_cmd.py:105）只在 normal 型出现——proot 靠它伪造 root 身份（真实 uid 0 由宿主内核拒绝），termux 型共享前缀路径不需要也不可用（`__init__.py:378-379`）。
- `--rootfs={rootfs_arg or rootfs}`（proot_cmd.py:107）：正常路径传 `.`（`__init__.py:474`），防换名劫持的关键在第五节详述。
- 假内核串 `--kernel-release=\Linux\{hostname}\{release}\{version}\{machine}\localdomain\-1\`（proot_cmd.py:151-156）：guest 的 uname 假装成 `6.17.0-...`（constants.py:120-122），绕过检查内核版本太老的包管理器；`-L` 修 dpkg 的 lstat 符号链接告警（proot_cmd.py:158）。
- `--link2symlink`（proot_cmd.py:146）给 normal 型：proot 的硬链接替换机制，让 guest 里的硬链接表现为真硬链接。
- 用户 bind 走 `_add_custom_binds`（proot_cmd.py:278）：src 强制 `os.path.abspath`（proot_cmd.py:300）、dst 必须绝对路径（proot_cmd.py:301-305）、与已有 bind 目的地图重叠只警告不拒绝（proot_cmd.py:307-309）——顺序在系统 bind 之后，因此用户可以用后写的 bind 覆盖默认（proot 尊重后出现者）。

非 minimal bind 域由 `_add_non_minimal_binds`（proot_cmd.py:161）编排：Termux 设备文件补丁（urandom→random、/proc/self/fd→/dev/fd、三个 std fd，proot_cmd.py:221-226）+ `fake_sysdata_bindings`（proot_cmd.py:227，/proc/cpuinfo 等伪文件）+ 容器专属 shm 仓 bind 成 /dev/shm（proot_cmd.py:238-240，仓建在 rootfs 旁的 `containers/<name>/shm/`，shm.py:61,77——不用 rootfs 内名字是防 guest 把它换成符号链接指到宿主任意目录）；Dalvik/ART 缓存（proot_cmd.py:246-261，目录必须带 world-execute 位 1/5/7 才可从 guest 遍历）；`storage_bindings`（bindings.py:35，/sdcard /storage，按授权形态两套打法）与 `system_bindings`（bindings.py:58，/apex /system /vendor 等，realpath+stat 过滤）；`--bind={TERMUX_PREFIX}` 让 guest 能调宿主 Termux 工具（proot_cmd.py:190）。

### 5. `bindings.py`、`detach.py`、`quoting.py`、`migrate.py`：四个小特化件

bindings.py 纯查询零状态：storage 探测 Termux 存储授权（先试 /storage 整体 bind，失败降级到逐路径 /mnt/sdcard 映射，bindings.py:38-54）；system 域逐路径 realpath+存在性+可读/可遍历三关（bindings.py:61-83）。

detach.py 实现教科书双 fork（头注释图示 detach.py:26-33）：fork→setsid→fork，孙进程即守护。三个精妙点：一是**管道回报协议**（detach.py:36-40）——孙进程 std 已是 /dev/null，管道写端 CLOEXEC，exec 成功则管道关闭、前台只读到 PID；exec 被拒（E2BIG/ENOMEM/argv 有 NUL）则在 PID 后写原因，前台据此报错而不是拿到一个从未启动的"会话"（detach.py:104-109,149-155）。二是 `register_session` 在孙进程里调用（detach.py:140），此时 `os.getpid()` 已等于未来 proot PID，`ps` 注册表文件名正确。三是 chdir 进钉住的 rootfs_fd 也发生在孙进程（detach.py:136-137），不扰动前台工作目录。前台拿到 PID 后必须 `lock.disown()`（`__init__.py:580`）——否则 with 块的 release() 会把守护进程脚下的共享锁 LOCK_UN 掉（locking.py:653）。

quoting.py 只有一个 `dq()`：POSIX 双引号引法，白名单字符（字母数字 `_-+./:@=`，quoting.py:27-32）裸放，其余转义 `\ " $ \``（quoting.py:39-44）。不用 `shlex.quote` 的理由写在头注释（quoting.py:22-24）：shlex 偏好单引号，而 `--get-proot-cmd` 的输出是给用户读改的，双引号里的 `$VAR` 引用可以保留。

migrate.py 处理旧版 `installed-rootfs/<name>` 布局到 `containers/<name>/rootfs` 的一次性搬迁（migrate.py:66）：两端都以 fd 定位（`lstat_at` 拒符号链接，migrate.py:56-63），`os.rename` 用 `src_dir_fd/dst_dir_fd` 形式（migrate.py:84-85），最后 `rewrite_l2s_targets` 重写所有指向旧路径的 l2s 符号链接（migrate.py:100-103）。已迁移则静默跳过，所以每次登录都要付出一次 lstat 的代价。

## 三、外部连接：login 站在谁的地基上

- **paths.py**：`open_container_pair`（paths.py:147）返回 `(container_fd, rootfs_fd)`，rootfs 从 container fd **下降**得到而非从信任根二次步行——两次步行可能对换名期间的名字给出不同答案（paths.py:156-158）。login 在 `__init__.py:324` 拿到这对 fd，try/finally 保证关闭（`__init__.py:332-334`）。
- **guestfile.py**：passwd 查询、发行版判定、shell 可用性检查（`__init__.py:294`）与架构探测（`__init__.py:436`）全部走它，共享同一个 `root_fd` 起点。
- **session.py**：前台路径 `register_session(**reg)`（`__init__.py:599`）写 `<pid>.json` 并持有可继承 flock；reg 含 kind="run"/"login" 区分（`__init__.py:558`）。fd 引用必须保活到 execvpe，否则被 GC 提前释放锁（session.py:126-128）。
- **arch.py**：`detect_installed_arch` 读容器 shell 的 ELF 头（`__init__.py:436`），与宿主 `get_device_cpu_arch` 比较后由 `get_emulator_args` 决定 QEMU 旗标（`__init__.py:443`）；termux 型不可仿真（`__init__.py:446-456`，宿主与容器共享同一前缀路径，仿真会看到宿主架构的二进制）。`get_proot_bin`（arch.py:221）**永远返回绝对路径**——execvpe 对裸名会拿 child_env 的 PATH 查找，而镜像 Env 恰好能改 PATH（arch.py:226-240）。
- **sysdata.py/shm.py**：伪 /proc 文件桩与 shm/tmp 目录制作，全部接受 fd 参数从钉住点起步。
- **run.py**：`args._run_inner` 注入（run.py:150）后走 login 全流程，inner 数组直接替换默认 shell 命令（`__init__.py:372-373,397-398`）。

## 四、数据流：一条命令穿过八模块的完整旅程

以 `pd login debian --user alice:dev --detach -- bind /data` 为例：

1. **锁与钉住**：共享锁+inheritable（`__init__.py:92`）→ migrate 探测（无旧布局，一次 lstat）→ `open_container_pair` 拿两个 fd。
2. **形态判定**：`_detect_dist_type`=normal → `_resolve_login_user` 走 guestfile 读 /etc/passwd 得 alice 的 uid/gid/home/shell；`_check_shell_available` 确认 shell 存在（`__init__.py:400`）。
3. **环境合成**（`_build_normal_env`，叠层自下而上）：PATH 基线+三 Termux 变量 → 镜像 Env（过滤后）→ 身身变量 → Android 九变量（仅默认模式从宿主继承，`__init__.py:270-274`）→ 用户 --env → HOME/USER/TERM（TERM 宿主缺省回退 `xterm-256color`，`__init__.py:284`）。随后主流程追加：Termux bin 去重后**追加到 PATH 末尾**（`__init__.py:414-421`，guest 工具可调宿主工具但不遮蔽）；proot 自身变量 `PROOT_NO_SECCOMP/PROOT_VERBOSE` 从宿主透传（`__init__.py:504-508`）；`PROOT_L2S_DIR` 钉到容器内 `.l2s/`（`__init__.py:520-522`，防两并发会话竞态+防符号链接注入，失败则 unset 并警告 `__init__.py:527-529`）；最后无条件弹出宿主 `LD_PRELOAD`（`__init__.py:530`）——镜像的 LD_* 在 env.py 闸过，宿主自己的也不能带进 proot。
4. **profile.d 快照**：`inject_termux_profile` 把当前环境写成 termux-profile.sh（PATH 追加是否含 Termux bin 依模式而定，`__init__.py:432`）。
5. **argv 组装**：`build_proot_args` 按七段拼出完整 argv；`--rootfs=.`、`--cwd=<home>`、`--change-id=<uid>:<gid>`、系统 bind 域、用户 /data bind、`-p`（若有）、inner=`[shell, "-l"]`。
6. **分岔**：--detach 走 `spawn_detached`（孙进程里 fchdir+register+exec，前台打印 PID 与 kill 提示后返回，`__init__.py:582-592`）；否则 register_session 后 `_exec_proot`。

## 五、设计决策：为什么是 fchdir + `--rootfs=.`

本子包最深的决策是**用 inode 而非名字锚定 guest 根**。威胁：`containers/<name>` 在 Termux 上 guest 可写，login 只持共享锁，活会话可以把 rootfs 目录挪走、在原名下留一个指向宿主任意目录的符号链接——proot 对 `--rootfs` 按名字解析，一切检查届时早已结束（`__init__.py:631-638`）。对策：argv 携带 `.`，进程在 exec 前 `os.fchdir(rootfs_fd)` 进入钉住描述符（`__init__.py:663`）；proot 对相对路径按 getcwd() 规范化，而内核答 getcwd 走目录自身的父链——**说出的是我们持有打开的那个 inode，不管名字底下剩了什么**（`__init__.py:641-646`）。注释记录了对抗验证：换名攻击下 `--rootfs=<path>` 落进植入目录，`--rootfs=.` 落进真 rootfs。fd 本身 CLOEXEC 不外泄（`__init__.py:648-649`）；rootfs 被删则 getcwd 失败、proot 拒启——"这是该有的结局"。

两个诚实的例外也钉在代码里：`--get-proot-cmd` 打印的命令给用户从自己的工作目录跑，只能写真路径——**描述符拼不进 shell 命令行**，所以 warn 明说"这不是本程序所跑命令的拷贝"（`__init__.py:543-547`），打印经 `os.fsencode` 保字节级一致（`__init__.py:620-625`）。bind 源同理：路径是给 proot 自己解析的名字，fd 只保住我们这一半（proot_cmd.py:89-91）。

其余决策同样成对出现：**exec 而非 spawn**（进程消失，锁与终端自然继承，E2BIG/ENOMEM/EACCES/ValueError 全收敛成一行错，`__init__.py:653-661`）；**profile.d 每会话重写**（防 rename 后旧会话的 `su -` 广播前任容器名，env.py:192-199）；**环境分层固定次序**且镜像 Env 的拒绝集中在 `image_env_pairs` 一处（env.py:121-124）；**用户 bind 只警告重叠不拒绝**（覆盖默认是合法用例）。

## 六、新人提示：改 login 代码前的五条军规

1. **任何新读容器内文件的需求，先看 guestfile 能不能接**。拼宿主路径是这个子包的 historical bug 之王（passwd.py:28-34、`__init__.py:106-111`、env.py:209-215 三处头注释都是同一死法的墓碑）。传 `root_fd` 参数不是风格，是安全边界。
2. **改环境叠层次序前重读 env.py 三段注释**。次序承载语义：镜像 Env 抢不过身份变量、用户 --env 抢过一切、TERM 归启动终端。新增变量先问归哪层、是否要进 `IMAGE_ENV_BLOCKED`/`_PROFILE_INJECT_SKIP` 两个名单。
3. **argv 组装顺序是 proot 的语义**（proot_cmd.py:24-33）：后写的 bind 覆盖先写的，`-p` 必须在 bind 之后、inner 之前。加旗标先确认它在 proot 手册里的位置语义。
4. **detach 路径的错误处理只有管道一条出口**：孙进程里任何 Python 异常都到不了用户（std 已 /dev/null），所以全程 os._exit + try/except BaseException 包底（detach.py:131-160）。改动时保持"失败必写管道"的约定。
5. **测试看 security 件**：`test_container_dir_escape.py` 覆盖八命令的换名逃逸，login 的 `--rootfs=.` 钉住形态在其中（tests/README）；改 `_exec_proot`/`spawn_detached`/`inject_termux_profile` 任何一个，先跑它。现场核实锚时注意 `__init__.py` 的行号在头注释改动后会整体平移，引用时以函数名+行为特征双重定位。
