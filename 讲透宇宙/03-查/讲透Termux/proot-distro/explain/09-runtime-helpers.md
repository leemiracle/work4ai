# 09 · L02 运行时支持层六件套 — guestfile / execenv / l2s / shm / sysdata / compress

> 图谱定位：L02 运行时支持层 · guestfile 402 行 / sysdata 641 行 / l2s 269 行 / compress 176 行 / shm 118 行 / execenv 123 行 · 行号锚现场核实。

## 一、角色定位：把"guest 眼中的世界"搬进宿主侧代码

L02 层六件套回答同一个问题的六个侧面：**宿主侧进程如何在不可信的容器内容上，做出与 guest/proot 语义一致的行为**。它们都站在 L01 的 dirfd 肩上（六件全部 `from proot_distro import dirfd` 或间接依赖），却各自对抗一种"宿主直觉与 chroot 语义错位"：

- **guestfile**（402 行）：按 chroot 语义走读容器内文件——login 在 exec proot 前要从 guest 的 `/etc/passwd` 取 uid/home/shell，arch 探测要读容器内 shell 的 ELF 头，而 guest 视角的路径解析规则（绝对符号链接回到 rootfs、`..` 停在 rootfs）与宿主内核完全不同（proot_distro/guestfile.py:21-35）。
- **execenv**（123 行）：一个 dict 伺候两个主人——交给 `os.execvpe(proot_bin, ...)` 的环境既是 proot 的也是 tracee 的，哪些变量属于"宿主侧 exec"必须按**出处**而非名字划分（proot_distro/execenv.py:30-45）。
- **l2s**（269 行）：proot 的 `--link2symlink` 扩展把硬链接改写为指向 `<rootfs>/.l2s/` 后备文件的符号链接，rootfs 移动后全部断链——本模块负责原地重写与安全解析（proot_distro/l2s.py:21-27）。
- **shm**（118 行）：Android 的 `/dev` 无可用共享内存，proot 把宿主 `/dev` 整体绑入 guest，需另造目录绑定成 `/dev/shm`——且绝不能是 rootfs 里的名字（proot_distro/shm.py:21-28）。
- **sysdata**（641 行）：伪造 `/proc`/`/sys` 静态内容让 top/htop 等 distro 工具在 Android 的受限 /proc 上正常工作（proot_distro/sysdata.py:21-26）。
- **compress**（176 行）："本程序关于 zstd 知道的一切"——Python 3.14 前后两种解释器的读写双形态支持（proot_distro/compress.py:21-27）。

六件套的共同底色是 ONBOARDING 第 4 节那句话的展开：威胁模型"guest 可写目录里的一切名字都不可信"，但**跟随与否要看语义**——dirfd 层对符号链接一律 O_NOFOLLOW 拒绝，而 guestfile 反其道行之：合法镜像本来就带符号链接（Nix 把 /etc/passwd 指向 store 绝对路径），chroot 语义要求跟随、只把锚点钉在 rootfs（guestfile.py:30-35）。

## 二、内部结构：六个模块的分区地图

**guestfile** 三层金字塔：公共 API 四个（`open_guest_file`/`read_guest_bytes`/`read_guest_file`/`guest_file_exists`，guestfile.py:297,315,356,373）→ 中枢 `_open_guest_fd`（guestfile.py:271-294，walk 到位后经 `open_regular_at` 开常规文件）→ 核心 `_resolve` 走读器（guestfile.py:114-260）。三重预算常量：`_MAX_SYMLINK_HOPS=40`（guestfile.py:63）、`_MAX_PATH_COMPONENTS=4096`（guestfile.py:70，40 跳链接之间可夹任意数量组件，每步都计入）、`MAX_ID_FILE_BYTES=1<<20`（guestfile.py:77，镜像的 passwd 大小无人约束，"再读下去就不是 passwd 文件了"）。辅助件 `_l2s_parts`（guestfile.py:80-102）与 `_dir_key`（guestfile.py:105-111，取 (dev,ino) 作目录身份）。

**execenv** 无状态纯规则模块，导出五件：`_HOST_EXEC_PREFIXES=("LD_","PROOT_")`（execenv.py:60，前缀而非清单——"下一个 libc 再加什么 LD_* 也自动覆盖"）、`IDENTITY_ENV_KEYS` 四键（execenv.py:72，PD_CONTAINER/PD_IMAGE/PD_IMAGE_ID + systemd/podman/lxc 惯用的小写 `container` 标记）、`CONTAINER_MARKER="proot-distro"`（execenv.py:73）、`MAX_ENV_STRING_BYTES=32*4096`（execenv.py:81，即 execve(2) 的 MAX_ARG_STRLEN，32 页 4KiB 留 1 字节 NUL）、两个判定函数 `is_host_exec_var`/`is_exportable`（execenv.py:84,96）。

**l2s** 读写两半：读侧 `resolve_l2s_target`（l2s.py:56-113，识别+全链解析+圈禁）与 `open_l2s_backing`（l2s.py:116-160，O_NOFOLLOW 重走已解析路径）；写侧 `rewrite_l2s_targets`（l2s.py:163-211，信号拦截外壳）→ `_rewrite_walk`（l2s.py:214-253，显式栈遍历）→ `_rewrite_link`（l2s.py:256-269，unlink+symlink 单链接重写）。识别依据 `_L2S_NAME_PREFIXES=(".proot.l2s.",".l2s.")`（l2s.py:53），两拼写对应 proot 源码 link2symlink.c 的 userland 构建与默认构建。

**shm** 仅 118 行三常量三函数：`SHM_DIR_NAME="shm"`（shm.py:61）、`SHM_DIR_MODE=0o1777`（shm.py:65，sticky bit 的 /dev/shm 标准形态）、`shm_dir` 返回 rootfs 的**兄弟**路径（shm.py:72-74）；`make_shm_dir` 与 `make_guest_tmp` 各带 `container_fd`/`rootfs_fd` 可选参数走 fd 路线（shm.py:77-97,100-115）。

**sysdata** 分四区：内容区（`_FAKE_LOADAVG` sysdata.py:63、八行 `_FAKE_CPU_ROWS` 快照 sysdata.py:72-81、`_FAKE_VMSTAT` 巨表 sysdata.py:160-339、`_FAKE_VERSION` sysdata.py:341-345、九条 `_FAKE_ENTRIES` 表 sysdata.py:352-365——loadavg/stat/uptime/version/vmstat 加三条 sysctl 与 cap_last_cap）；内容生成区（`host_cpu_ids` sysdata.py:103-126、`fake_stat` sysdata.py:135-147、`fake_uptime` sysdata.py:150-157）；写入区（`_ensure_dir_at` sysdata.py:373-409、`_is_own_file` sysdata.py:412-422、`_write_if_missing` sysdata.py:425-464、`_holds`/`_write_current` sysdata.py:467-482,485-524）；消费区（`setup_fake_sysdata` sysdata.py:527-569、`fake_sysdata_bindings` sysdata.py:604-641）。

**compress** 一个探针两个家族：`ZSTD_AVAILABLE` 要求两半齐全（compress.py:62——`compression.zstd` 模块在且 tarfile 认 `'zst'` 模式；无 libzstd 的解释器仍带 `TarFile.zstopen`，调用才抛 CompressionError，故不能只探一半）；读家族 `header_is_zstd`/`file_is_zstd`/`require_read_support`/`require_read_support_fd`（compress.py:105-149，fd 版用 `os.pread` 不动文件位置）；写家族 `require_write_support`/`open_tar_writer`（compress.py:152-176）。诊断文案区分两种语境：`unsupported_msg` 给"数据原来是 zstd"（compress.py:87-93），`unavailable_msg` 给"用户点名要 zstd"（compress.py:96-102）。

## 三、外部连接：上游两个地基，下游四条命令线

**上游**：dirfd（guestfile/l2s/shm/sysdata 直接用其 opendir_at/open_regular_at/makedirs 族/lstat_at/temp_name/unlink_quietly，l2s.py:214-223 还复用 dirfd 的 Levels 帧布局）；constants 给 sysdata 提供 `DEFAULT_FAKE_KERNEL_RELEASE/VERSION`（sysdata.py:58-61）；tarfile/stdlib 给 compress。

**下游**（grep 实证 18 处生产导入）：
- **login 线**五连：passwd.py:53 用 `read_guest_file` 走读 guest passwd/group；`__init__.py:113` 用 `guest_file_exists` 判断容器类型（有无 /data/.locale 即 termux 型）；`__init__.py:408` install 后补 sysdata 桩；`__init__.py:520-522` 在 rootfs_fd 下 `makedirs_at` 造 `.l2s` 并注入 `PROOT_L2S_DIR`（注释直言：guest 留下的 `.l2s` 符号链接会让 proot 写穿）；proot_cmd.py:227,237-238 消费 `fake_sysdata_bindings`+`make_guest_tmp`+`make_shm_dir`。
- **build 线**五连：run_step.py:284,294-295 与 login 同构消费 shm/sysdata，run_step.py:736-742 给 proot 设 `PROOT_L2S_DIR`；users.py:51,59 用 `open_guest_file`+`read_capped` 解析 USER/COPY --chown（与 login 读同一个文件，同一走读器）；engine.py:193-194 与 handlers.py:103 在采纳基础镜像 config 与 ENV 行时过 `is_host_exec_var`+`is_exportable` 双闸。
- **backup/restore 线**：backup.py:312,318 对每个符号链接问 `resolve_l2s_target`、命中则 `open_l2s_backing` 取后备字节打包；layer_diff.py:49 同一对函数用于构建增量层；restore/rename/migrate 三命令收尾时调 `rewrite_l2s_targets`（rename.py:42、login/migrate.py:34）。
- **压缩线**：pull.py:46 拿 `ZSTD_AVAILABLE`+`unsupported_msg` 诊断 zstd 层；tar_extract.py:99、install_local.py:44、backup.py:57、restore.py:64 全部 `require_read_support` 前置嗅探——同一个探针答所有调用方"这台解释器能不能 zstd"。

## 四、数据流：一次 login 组装 argv 时六件套里五件的接力

login 在 exec proot 前的组装序列（login/`__init__.py:324` 已用 O_NOFOLLOW 钉住 container/rootfs 目录对，`rootfs_fd` 一路下传）：

1. **sysdata 落桩**（login/`__init__.py:408`→sysdata.py:527）：从钉住的 container_fd 开 sysdata/（0o700，sysdata.py:552），先造 `sys_empty`，再按 `_FAKE_ENTRIES` 表写九条——静态条目走 `_write_if_missing`（已是自己写的文件则不碰，sysdata.py:443-445），stat/uptime 走 `_write_current` 按 `host_cpu_ids()` 现算重写（sysdata.py:562-567）。
2. **passwd 走读**（login/passwd.py:53→guestfile.py:356）：`_resolve` 从 rootfs_fd 起步（调用方持有 pin 必须传入——按名再开一次会把 `containers/<name>` 这个 guest 可写组件重新解析一遍，guestfile.py:148-156），逐组件消费 `/etc/passwd`：遇目录 fd 下行并记 (name,(dev,ino)) 足迹；遇符号链接读目标，l2s 后备优先判（guestfile.py:216）、相对目标插回队首继续（:217-220）、绝对目标或 l2s 解析结果**回到 guest 的 "/" 重启**（:221-229）；`..` 经 `opendir_at(cur,"..")` 上行并核对落点 (dev,ino) 与下行时记录一致——目录被 guest 移动会换爹，不一致即弃（:186-193）。全程仅两个 fd 打开（rootfs+当前层，:137-141），深度不决定 fd 数。
3. **环境组装**（login/env.py:38 消费 execenv）：`is_host_exec_var` 过滤来自镜像描述文件的 LD_*/PROOT_*（env.py:138），`is_exportable` 对每个键值做 NUL/编码/E2BIG 三查（env.py:143,288）——三条中任何一条的裁决都是"这个条目不导出"而非"会话不启动"；`IDENTITY_ENV_KEYS` 注入四键身份（env.py:85,166-172）。
4. **l2s 目录注入**（login/`__init__.py:520-522`）：rootfs_fd 下造 `.l2s` 真目录，`PROOT_L2S_DIR` 进 child env——proot 此后所有硬链接仿真都落在受控目录里。
5. **bind 参数合成**（proot_cmd.py:227-243）：`fake_sysdata_bindings` 只绑宿主真读不到的条目（sysdata.py:631-634 先试读真文件）且只绑"恰好一链接"的文件（:637）；`make_shm_dir` 在 container_fd 下造兄弟 shm/，None 则**宁可不绑**并警告（proot_cmd.py:239-243）。

compress 不在 login 链上，它的主战场在 backup：`open_tar_writer` 让 `-o out.tar.zst` 与 `> out.tar.zst` 走同一条 `w|` 流、同一 level=10（compress.py:158-176），关闭顺序注释钉死"先写 tar 收尾块、再收 zstd 帧、最后关文件"（:172-174）。

## 五、设计决策：五个值得抄的判断

**1. O_EXCL 造新 inode 与"恰好一链接"判定（sysdata 的灵魂）。** 硬链接对 O_NOFOLLOW 是隐形的——它不是"指向文件的链接"，它**就是**那个文件的第二个名字（sysdata.py:43-47）。guest 把宿主文件 `link()` 进 sysdata/loadavg，此后每个会话都把它当自己写的桩接受，bindings 再把它绑成 /proc/loadavg——proot 没有只读 bind，guest 可读**可写**宿主文件（:47-52）。对策两层：写入侧 `_write_if_missing` 发现非"自己写的文件"即 unlink 名字，再用 `O_CREAT|O_EXCL|O_NOFOLLOW` 保证字节只进**本目录内的新 inode**（sysdata.py:452-454）；unlink 只动名字不动 inode，宿主文件内容无损、只是不再充当本容器的 /proc/loadavg（:430-435）。消费侧 `_is_own_file` 把判定定义为 `S_ISREG and st_nlink == 1`（sysdata.py:422）——本模块从不给自己写的文件造第二个链接，nlink≠1 必是植入。`_write_current` 的 temp+`os.replace` 同理：rename 换目录项、目标端什么也不跟随，植入的符号/硬链接被换掉而非写穿（sysdata.py:496-518）。

**2. 语义 chroot 而非语法拒绝（guestfile 与 dirfd 的分工）。** dirfd 的规则是"名字不可信，一概 O_NOFOLLOW"；guestfile 的规则是"内容是镜像的，chroot 怎么解析我就怎么解析"（guestfile.py:30-35）。历史上两步错法各留一笔：拼宿主路径再 open，中间组件 `etc -> /etc` 一次越狱就让 login 把宿主用户的 uid/home/shell 递给会话（:40-44）；即便逐组件检查，共享锁下另一会话仍可在 check 与 open 之间换名（:44-48）。终局答案："**解析的走读就是打开的走读**"——组件一次一个从目录描述符上消费，决定路径含义与读取之间没有窗口（:37-39,129-131）。

**3. 按出处立法，不按名字立法（execenv）。** `PROOT_NO_SECCOMP=1 proot-distro login debian` 是用户对自己命令的选择，照常工作；同值若来自镜像 config 或 Dockerfile ENV 行，则是"陌生人的陈述"经拷贝流传——三类调用方统一在此丢弃（execenv.py:45-58）。立法难度在于 dict 双重身份：proot 无力单独设 guest 环境，exec 传给 proot 的就是 proot 自己的环境、由它转交 tracee，镜像设中一个 LD_PRELOAD 即可在**任何容器外**以调用者身份执行代码（:30-43）——"install 然后 login 一次就够，连竞争都不需要"（:42-43）。注意 PD_ 前缀的存在理由：PROOT_* 整个命名空间已划为宿主侧，程序自身变量只能换前缀（:69-71）。

**4. 兄弟目录优于 rootfs 内名字（shm 与 sysdata 同构）。** bind 源是**名字**，proot 在 mount 时解析它——那已在检查完成、本程序退出之后（shm.py:26-28,228-230 注释）。rootfs 内的 `/tmp` 可被会话翻成符号链接，共享锁下窗内一换，下个会话就把 guest 自选的宿主目录读写挂进容器，--isolated 模式的全部承诺就此清零（shm.py:32-38）。兄弟路径 `containers/<name>/shm` 换名须写其**父**目录，rootfs 内的会话够不着：guest 只能透过 bind 看到该目录，而 proot 先规范化 guest 路径，`/dev/shm/..` 就是 `/dev`（shm.py:40-47）。sysdata 同住兄弟位、随容器一起删除（sysdata.py:25-26,368-370）；reset.py:92 删 `shm_dir`、restore.py:74 按 `SHM_DIR_NAME` 排除，均消费这一布局。guest 自己的 /tmp 仍然照造（shm.py:49-54）——两者曾同一目录，共享内存文件漏进 guest /tmp 与构建层；Docker 也是 tmpfs 分开，RUN 步写进 /dev/shm 的东西不属于镜像。

**5. 压缩双形态：一次探针+一条写路径（compress）。** 读侧免费（3.14 的 tarfile `r|*` 自动识别 zstd 魔数），费的是诊断——否则死在 tarfile 深处的 `ReadError('truncated header')` 与四行 dump 都不提 zstd（compress.py:31-37），故 `require_read_support` 抢在 tarfile 接手前嗅 4 字节魔数 `28 b5 2f fd`（RFC 8878 §3.1.1，:64-65）。写侧 tarfile 自相矛盾：`w|zst` 拒绝 level、`w:zst` 接受，放着不管则 `-o` 与管道两种 backup 压缩参数不同（:38-45）；`open_tar_writer` 自己造 `ZstdFile(level=10)` 喂给 tarfile 一个朴素 `w|` 流（:175-176）。level=10 有实测依据：101MiB 文件系统上 22MiB/3.8s，胜 gzip -9 的 27MiB/23s；15 级多花 6 倍时间只省 1MiB，xz 18MiB 但 61s——各自守住曲线拐点（:67-75）。

另记一笔 l2s 的历史漏洞（升维到"语义答案只决定去哪看，不决定怎么去"）：旧前缀测试被 guest 内两次 `ln -s` 打穿——`innocent.txt -> .proot.l2s.evil0001`、`.proot.l2s.evil0001 -> /absolute/host/path`，normpath 不问文件系统地折叠 `..`，第一跳在 rootfs 内+第二跳出去的组合通过了旧测试，backup 把宿主字节打进归档、build engine 打进层再由 push 上传 registry（l2s.py:79-91）。现行 `resolve_l2s_target` 全链 realpath、两侧 realpath、圈禁在 rootfs 真身下（:107-113）；`open_l2s_backing` 再把词法答案用 O_NOFOLLOW 从 rootfs 描述符重走一遍——"解析与读取是两步，backup 只持共享锁，两步之间 guest 还能换组件"（:116-127）。重写遍历的细节同样有账：os.walk 把指向目录的符号链接当目录、整代漏出重写（:179-181）；lstat 定分界（:243-250）；SIGINT/SIGQUIT 整程拦截——半途终止留下指向已逝路径的死链，宁可打警告走完（:29-32,183-186）；走树写操作吃 fd 而非路径，因为树刚被移动且验证过落点，重解析一次 guest 可写的 `containers/<name>` 等于把已钉死的组件再放开（:170-177）。

## 六、新人提示

- **改 guestfile 先背预算**：40 跳/4096 组件/1MiB 三顶帽子（guestfile.py:63,70,77）各自防"镜像决定本进程吃多少资源"；`read_capped` 超限时按最后一个完整换行截断，绝不把切一半的行递给 passwd 解析器（:347-353）。
- **"自己写的文件"是可判定谓词，不是感觉**：sysdata 的判定 = 常规文件且 st_nlink==1（sysdata.py:422），目录无此测试因目录不可硬链接（:572-578）；改写入路径时保住不变量"本模块从不造第二个链接"。
- **execenv 的过滤器不碰用户自己的环境**：`is_host_exec_var` 只用于"来自描述镜像的文件"的值（execenv.py:84-92），把用户 --env 也滤掉是理解反了立法对象。
- **新 bind 源一律兄弟目录**：凡要交给 proot `--bind` 的名字，先问"rootfs 内的会话能不能改到这个名字的上游"——shm/sysdata 的答案都是搬出 rootfs（shm.py:40-47）。
- **zstd 相关改动先过 `ZSTD_AVAILABLE` 双半检查**（compress.py:58-62），别只探模块存在；给 tarfile 加新压缩格式时记得 `require_read_support` 前置嗅探这条纪律。
- **l2s 前缀两个拼写都要认**（l2s.py:47-53）：`.proot.l2s.` 是 userland 构建（Termux 默认），`.l2s.` 是其他；只认一个就读不懂另一种 proot 产的层。
- **测六件套优先看 security 件**：guestfile 的逃逸场景与 sysdata 的植入场景在 tests/security/ 有现成重现器，新写入路径先跑它们。
