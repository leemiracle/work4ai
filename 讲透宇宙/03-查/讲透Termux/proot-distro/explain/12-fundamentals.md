# 12. 基础件四件套：locking / message / progress / atomic（L01-L02）

> 覆盖 `proot_distro/locking.py`（765 行）、`message.py`（291 行）、`progress.py`（147 行）、`atomic.py`（265 行）。全部断言以 `file:line` 现场核实于 commit 737306f5 工作区。

## 一、角色定位：命令层的四根横切梁

如果把 18 个命令模块（`cli.py:64` 的 `_COMMAND_HANDLERS`）比作楼层，这四个文件就是贯穿全楼的四根管线——每个命令都要用电（输出）、用水（原子写）、通风（进度反馈）、门禁（互斥）。它们在 14 层图谱里沉在 L01/L02 基础层，fan-in 全库最高（onboarding §3）。

四件各管一件事，且互相咬合：

- **locking.py** — 回答"现在能动手吗"。POSIX flock(2) 咨询锁，双命名空间（容器锁/构建锁），非阻塞，拿不到立刻退（`locking.py:44-45`）。
- **message.py** — 回答"怎么把话说到终端上"。颜色表 + 分级日志（info/error/warn/crit）+ 不可信文本转义（`message.py:21-37`）。
- **progress.py** — 回答"长任务进行到哪了"。20 格字节/计数进度条，共享 message 的 TTY 判定，无 TTY 全静默（`progress.py:21-31`）。
- **atomic.py** — 回答"怎么写文件才不留半成品"。tmp + rename 模式的唯一实现，12 个文件 39 处调用（grep 统计）。

它们与 02 篇的 dirfd 安全面不是并列关系而是**用户**关系：locking 和 atomic 的每一步文件操作都以 `(dir_fd, name)` 寻址、O_NOFOLLOW 逐级下行，因为锁定目录和缓存目录在 Termux 上都挂在 `$TERMUX_PREFIX` 下、以读写绑定进每个非隔离容器（`locking.py:58-62`，`atomic.py:60-62`）——攻击者就坐在你正在写的目录里。

## 二、内部结构：逐件拆解

### 2.1 locking.py：flock 家族与它的失败分类学

**双命名空间**（`locking.py:23-42`）：`ContainerLock` 按容器名加锁——install/restore/remove/rename/reset 及"目的地是容器"的 copy/sync 拿排它锁，backup/login/run 及"来源是容器"的 copy/sync 拿共享锁；`BuildLock` 按 `(image_ref, arch)` 加锁、恒排它，供 build/push/`remove --image` 防止并发写竞态 manifest 缓存与 build-cache 索引。两 namespace 物理隔离：容器锁在 `RUNTIME_DIR/locks/`，构建锁在 `RUNTIME_DIR/locks/build/`（`locking.py:92-93`），永不碰撞。

**BuildLock 的 key 就是 manifest-cache key**：`canonical_ref(image_ref)_arch` 的 sha256 前 16 个 hex（`locking.py:127-129`，surrogatepass 编码容忍命令行里的孤立代理项）。docstring 记录了历史 bug：曾经按"用户敲的原文"哈希，`build -t myapp` 与 `push docker.io/library/myapp` 指向同一缓存条目却各拿各的锁、并行运行（`locking.py:118-120`）——锁身份必须与被保护资源的身份同源，这是本模块最值得抄走的一条经验。

**acquire() 主干**（`locking.py:576-651`）走五步：①查重入表 `_held_exclusive`（`locking.py:588-592`）——reset 命令内部调 install 时同进程不重拿；②逐级打开锁目录（`locking.py:595`）；③`_open_lock_file` 以 O_NOFOLLOW+类型检查开锁文件，名字被符号链接/FIFO/目录占用则先删再重建，删不掉抛 `_HostileLockPath`（`locking.py:398-432`）；④`fcntl.flock` 非阻塞加 LOCK_EX 或 LOCK_SH（`locking.py:625-629`）；⑤拿到锁**之后**才 seek+truncate 写入 `PID 命令名`（`locking.py:641-643`）——顺序反过来，输掉竞争的进程会把持有者的诊断行抹掉，它即将报告的冲突就"查无此人"。

**失败三分法**是本文件的灵魂（`locking.py:66-80` 注释整段讲透）：

- **EROFS/ENOSPC/文件系统不支持 flock** = "锁文件无法存在"，历来语义是**无锁继续**（`acquire` 里 `dir_fd is None` 返回 True，`locking.py:596-597`；flock 报非 EACCES/EAGAIN errno 也返回 True，`locking.py:632-634`）；
- **EACCES/EPERM**（`_DENIED_ERRNOS`，`locking.py:475`）= "被阻止"，抛 `_LockPathDenied` 且**拒绝执行**——因为容器 chmod 000 锁目录可以把 remove/restore 伪装成"锁文件建不出来"，让破坏性命令与活会话并排跑（`locking.py:71-77`）；
- **名字被占且删不掉** = `_HostileLockPath`，同样拒绝（fail-closed）。

与之对照，`open_lock_file_at`（`locking.py:435-457`）给 build-cache 索引锁的却是 fail-open 策略：吞掉两类异常返回 None 无锁继续——因为索引本身经 atomic_replace 发布，丢锁只损失一条并发 record，不会损坏文件（`locking.py:443-452`）。**同一把锁、两种失败策略，取决于丢锁的代价**——这是决策表而非教条。

**inheritable 与 disown**：login/run 经 `os.execvpe()` 换成 proot 进程，Python 默认给所有新 fd 设 O_CLOEXEC（PEP 446），所以显式 `os.set_inheritable(fd, True)` 让锁 fd 跟进 exec、在容器会话全程持有（`locking.py:49-51,619-623`）。detached 会话再进一步：fork 出的后代持有同一 open file description，flock 的释放条件是"任意副本显式 LOCK_UN 或全部副本关闭"（`locking.py:656-663`），所以父进程 `disown()` 标记后 `release()` 只关 fd 不发 LOCK_UN（`locking.py:679-685`），锁由后代独自撑到会话结束。

**busy_locks()**（`locking.py:346-369`）扫两个 namespace，对每个 `.lock` 文件做一次共享非阻塞 flock 探测（`_lock_is_held_at`，`locking.py:309-311`：LOCK_SH|LOCK_NB 撞 EACCES/EAGAIN 即有排它持有者），附 `_lock_info_at` 的持有者提示——读锁文件首行取 PID，用 `os.kill(pid, 0)` 判活，死 PID 不提示（`locking.py:277-278`）。两个关键设计：①只报**排它**持有者，login 会话/运行中的 backup 这类共享者不碰下载缓存、故意缺席（`locking.py:352-355`）；②答案是构造上的快照，"是并发防护不是锁"（`locking.py:358-361`）。任何一层读不出来抛 `LockStateUnknown`——"没锁"与"不让看"必须区分，因为调用方要据此删 blob（`locking.py:388-395`）。

### 2.2 message.py：分级输出与终端注入防线

**颜色系统**：`_COLORS` 把符号名映射到 ANSI 序列，每条以 `_RST`（`\033[0m`）开头（`message.py:59-103`），切换颜色即隐式归零，不会把粗体"漏"到下一段。非 TTY 或设了 `PD_FORCE_NO_COLORS` 时换成全空串字典 `_EMPTY`（`message.py:104-113`），调用方零改动。注意颜色在**模块导入时**绑定 `C`——测试环境天然无色（`test_message.py:20`）。

**四级日志**（`message.py:210-229`）：`log_info`（`[*]` 蓝绿）在 --quiet 下变 no-op；`log_error`（`[!]`）**恒显**——错误必须到达用户；`warn`/`crit_error` 黄/红。quiet 是进程级全局开关，由 cli 分派前 `set_quiet(True)` 置位（`cli.py:338`），list/ps 例外因为它们的 --quiet 语义是"只打名字/PID"（`cli.py:330-338` 注释）。

**tty_safe_for_writes()**（`message.py:116-148`）解决一个精巧的真实冲突：用户把 backup 管道进 `gpg -c`，pinentry 接管 stderr 要密码——此刻进度条的 `\r\033[K` 会把密码提示砸花。判据是 termios 的 lflag：**ECHO 与 ICANON 同时在**才算"shell 正常态"（`message.py:147-148`），读密码清 ECHO、全屏 UI 清 ICANON，任一触发即让路。妙在不点名任何程序——pinentry/sudo/ssh-askpass/less 一网打尽（`message.py:128-130`）。

**msg()** 的擦线只在 TTY 上发生（`message.py:204-205`）：重定向进日志文件时 `\r\033[K` 只会注入控制字符、没有可擦的进度行。

**quote_path()——--verbose 转义的核心**（`message.py:242-276`）：容器 rootfs、归档、镜像 metadata、registry 回复里的名字都是**内容控制方选的**；`copy`/`sync` 在 --verbose 下逐条打印条目名（`message.py:246-248`，实现见 `sync.py:146-155` 的 `shown()`/`src_shown()`），一个带 ESC 的名字能重绘终端、藏起周围行。转义规则：常用控制字符走可读形式（`\n`/`\t`/`\e`，`_QUOTE_MAP` `message.py:233-239`）；其余 <0x20 及 DEL 出 `\xNN`（`message.py:270-271`）；**孤立代理项**（argv/环境/JSON `\udcff` 里混进来的非 UTF-8 字节）出 `\uNNNN`（`message.py:272-273`）——stdout 严格编码会直接 UnicodeEncodeError；backslash 也逃逸，使逃逸输出与"名字里本来就有反斜杠"不可混淆（`message.py:253-255`）。配套 `quote_error`（`message.py:279-290`）：OSError 的 `strerror` 不含文件名（调用方自己经 quote_path 点名），其余异常的 str 整体过 quote_path。

### 2.3 progress.py：统一进度条与无 TTY 降级

头注释直言动机：install/backup/restore/copy/sync/build/push 七条命令原本各画各的 20 格 `[####----] NN% A / B`，集中后消灭约 7 份近似拷贝、宽度/节流/调色有了单点（`progress.py:21-26`）。

**三闸门**：`progress_active()` = `stderr.isatty() and not is_quiet()`（`progress.py:80-82`），再加 `tty_safe_for_writes()`（`progress.py:102`）。三个绘制函数 `draw_bytes_bar`/`draw_count_bar`/`clear_bar` 全部先过闸，**无 TTY 时一字符都不写**——重定向日志天然干净，这不是"输出难看的降级"而是"零输出的降级"。

**draw_bytes_bar 的双形态**（`progress.py:85-115`）：`total>0` 画百分比条，`pct` 用 `min(done*100//total, 100)` 钳制（`progress.py:107`）——bar 只有 20 格，超界百分比会画出越界条；`total==0`（解压流不知解压后总量的场景）退化为纯计数行 `"{label}: {fmt_size(done)} {noun}..."`（`progress.py:111-113`）。行首 `\r` 锚定、行尾 `\033[K` 擦残迹。

**ByteCounter**（`progress.py:54-77`）：包住底层文件对象的读写计数器，实现 `read` 与 `readinto` 两个口径（`progress.py:66-74`），其余属性经 `__getattr__` 透传。它存在的意义是**压缩字节口径**：tar 解包时知道的是磁盘上的压缩字节数、不知道解压后总量，于是用计数器量"吃了多少压缩流"驱动 bar（`tar_extract.py:88` 注释，`tar_extract.py:282,292` 实测使用）。

**节流常量** `REDRAW_THRESHOLD_BYTES = 262144`（256 KiB，`progress.py:40`）：调用方按原始字节差节流重绘，backup.py 拿它做 `_on_read` 的门槛（`backup.py:593-595`）。sync 在 --verbose 下干脆不画条——逐文件日志已是反馈，条会在行间闪烁（`sync.py:158-161`）。

### 2.4 atomic.py：tmp+rename 链——以及对"它有 fsync"的勘误

三个入口一个模式：`atomic_replace` 交原始 fd、`atomic_write` 交已包装的文件对象（`open(fd, mode, closefd=False)`，`atomic.py:141`）、`publish_file` 把已写完的文件改名到位（给"名字由内容 digest 决定、写完才知道叫什么"的层 blob 场景，`atomic.py:147-150`）。

**先勘误**：本模块**没有 fsync**——全包 grep `fsync|fdatasync` 零命中。它的承诺是"读者永远看不到半个文件"（rename(2) 的 POSIX 原子性），**不是**"断电后文件还在"（那需要 fsync 落盘链）。对一个 CLI 工具，丢成"保留旧版"或"重跑一次"是可接受的取舍，但读代码时别把 atomic 当 durable。

**双分支路由**（`atomic.py:116-119`）：目的地在 RUNTIME_DIR/BASE_CACHE_DIR 信任树内，走 `statedir.open_state_dir` 逐级 O_NOFOLLOW 步行拿 dir_fd，tmp 创建与发布 rename 全挂 fd（`atomic.py:121-127`）；树外的用户自选路径（`build --output`、`backup -o`）保持朴素行为 mkstemp+os.replace（`_replace_by_name`，`atomic.py:243-264`）——用户指哪是用户的事。

**tmp 的名字与打开方式**：`.{pid}.{urandom(4).hex}{suffix}` 保证并发写者不撞同一个哨兵（`atomic.py:189-191`，两个 build 共享基础镜像时真会发生）；`open_new_at(..., readable=True)` 以 O_EXCL 造**新 inode**、O_RDWR 打开（`atomic.py:192-196`）——需要回读自己字节的写者（交给解包器的层 blob）从同一描述符读，不再按名打开第二次。

**描述符而非名字**（`atomic.py:52-68` 头注释是全模块最好的教材）：把 tmp 路径交给调用方再 open，create 与 open 之间有窗口；名字不是秘密——共享目录的进程能从 readdir() 看到它、unlink 换成符号链接，调用方的 open 就把字节写进链接指向的宿主文件，rename 之后**发布的就是攻击者的链接**。描述符钉死 inode，rename 发布同一 inode，从头到尾没有"按名再打开"这个动作可供劫持。

**_publish_at 的 (st_dev, st_ino) 对账**（`atomic.py:210-240`）：字节已进 inode、无法再被重定向，但 rename 仍按名进行——共享目录的进程仍可在写完后 unlink tmp、原地留链接，写是写对了、**发布出去的却是别人的条目**。发布前 `lstat_at` 比对 `(st_dev, st_ino)` 与描述符的 fstat，把攻击窗口从"整个下载时长"压缩到"lstat 与 rename 之间的一瞬"（`atomic.py:222-227`）；不匹配抛 ESTALE，调用方清理路径顺手 unlink 现场的任何东西。

**异常清理**挂 `BaseException`（`atomic.py:203-207`）：KeyboardInterrupt 也走 tmp 清除——Ctrl-C 永远不留半写哨兵，这正是头注释列出的集中化收益之三（`atomic.py:29-31`，`test_atomic.py:52` 专测）。

## 三、外部连接：谁在消费

**locking**：copy/sync 的排它/共享矩阵在 `paths.py:865-873` 统一裁定；命令侧直接调用——install.py:185、remove.py:148、rename.py:80-81（一次拿两把锁防交叉死锁）、reset.py:72、backup.py:507（exclusive=False 共享）、login/__init__.py:92-95（共享+inheritable，detach 处 `lock.disown()` login/__init__.py:580）、build.py:235（多 tag 一把 BuildLock 一条列表式取）、push.py:101、remove.py:261。busy_locks 唯一消费者是 clear-cache 的孤儿清扫（clear_cache.py:421-422，LockStateUnknown 时拒删并明说"容器一次 chmod 就能让 build 假装不存在"）。`open_lock_file_at` 供 build_cache.py:72 给索引上锁。session.py 的会话存活判定用的是同一 flock 探测（session.py 171-188 一带，`os.set_inheritable`+`LOCK_EX|LOCK_NB`），locking.py:287-289 的 docstring 自己点明这层亲缘。

**message**：cli.py:338 是 quiet 总闸；quote_path/quote_error 的消费名单包括 download.py:207（isprintable 才直出）、search.py:129-130（registry 描述先合并空白再整体转义）、sync.py:146-155（--verbose 每文件行）、run.py:67（quote_error）、paths.py:130,181（容器目录名校验报错）。

**progress**：ByteCounter×2（tar_extract.py:282、restore.py:560）+ draw_bytes_bar 七处（download.py:643,681、layers.py:97、layer_diff.py:413 noun="packed"、backup.py:588、restore.py:493-495 双形态切换）+ draw_count_bar 两处（sync.py:161 unit="files"、copy.py:157 unit="entries"）。

**atomic**：12 文件 39 处——oci_writer/download/layer_diff/build_engine(handlers/copy_step/run_step)/docker(cache/layers)/install/install_local/build_cache/restore 全部经它写缓存、manifest、索引。

**测试**：`test_locking.py` 4 件专测 disown 的 fd 语义与 BuildLock 孤立代理项；`test_message.py` 16 件覆盖 quiet 切换、转义全分支（含"backslash 逃逸保证不歧义"一条，test_message.py:93）；`test_progress.py` 5 件（含无 TTY 静默）；`test_atomic.py` 6 件（KeyboardInterrupt 清理、tmp 名唯一性各一件）。

## 四、数据流：`proot-distro install <url>` 一次走读

1. cli 分派：`--quiet` 则 `set_quiet(True)`（cli.py:338），此后所有 log_info 与进度条静默。
2. install.py:185 进 `with ContainerLock(name, exclusive=True, command="install")`：步行创建 `RUNTIME_DIR/locks/` → O_EXCL 开 `name.lock` → flock LOCK_EX 非阻塞 → 拿到后写入 `PID install` 诊断行。撞锁则 `__enter__` 直接 `crit_error` + `sys.exit(1)`，附 holder_hint 的 `(PID 12345: backup)`（locking.py:697-699,281）。
3. 下载层 `download_file`（download.py:671）：`with atomic_write(dest, "wb") as fh` 先造出 tmp fd——注意**下载尚未开始，原子性的笼子已经关好**；chunk 循环里 `draw_bytes_bar(downloaded, total)` 三闸门放行才画；循环结束在 with 体内调 `require_complete_body(downloaded, total)`（download.py:685）做 Content-Length 对账——`declared_length` 先把服务器头的 `int()` 包进 try（`Content-Length: abc` 不再炸 ValueError，download.py:133-148），收到的少于声明的抛 IncompleteResponse：**此刻还在 atomic_write 里面**，异常把 tmp 一起带走，半个归档永远不会被当成完整归档发布（download.py:682-684 注释）。截短的 chunked body CPython 自己会报 IncompleteRead，截短的 Content-Length body 静默短读——对账函数正是为后者而生（download.py:151-163）。
4. 解包 tar：`ByteCounter(raw_fh)` 数压缩字节、`draw_bytes_bar(counter.count, total_size)` 反馈（tar_extract.py:282,292）；条目名异常路径全部经 quote_path 上报。
5. 收尾 manifest/注册文件同样走 atomic_write；with 块正常退出时逐个 lstat-对账-rename 晋升。
6. 对照 login 流程：共享锁 + inheritable=True，`os.execvpe()` 换 proot 后锁 fd 存活整个会话；detach 模式下 `lock.disown()` 让后台会话独占持有（login/__init__.py:568-580）。

## 五、设计决策与批判视角

1. **flock(2) 而非 fcntl 记录锁**：flock 锁挂在 open file description 上——fork 的后代天然共享、exec 后天然存活，这正好是 login"锁跨 exec 跟着容器会话走"与 session"锁活即会话活"两个需求的语义；记录锁挂在 (pid, inode) 上，exec 后自灭，不合适。代价是 NFS 语义各家不一——模块用"不支持 flock 的文件系统无锁继续"诚实兜底（locking.py:632-634）。
2. **"不能"与"被阻止"的哲学区分**：EROFS/ENOSPC 是物理世界说"锁文件无法存在"（历来无锁跑），EACCES 是可能有敌意的一方在"阻止你拿锁"（拒绝跑）——同一 errno 家族被拆成两类策略（locking.py:66-80,471-475）。加上 build-cache 锁的 fail-open 例外（丢锁代价仅一条并发记录），三档策略各配各的理由，读起来是一张决策表而非教条。
3. **原子性 ≠ 持久性**：无 fsync 是明确取舍（见 2.4 勘误）。若某天缓存写坏需要断电故事，补强点在 `_replace_at` 的 close 与 `_publish_at` 的 rename 之间——但那会拖慢每层 blob 的发布，对 CLI 工具大概率不值。
4. **输出层与安全模型正交但同源**：quote_path 防的是终端注入（ESC 重绘/藏行），与 dirfd 防的是目录注入，威胁模型同一条——"guest 可写目录里的一切名字不可信"推广到"一切不可信内容里的名字"。msg()/bar 的 TTY-only 擦线同理：控制字符只进真终端、不进日志。
5. **批判性缺口**（读代码时该带着的问题）：`_held_exclusive` 重入是单进程的，跨进程同链不防；`_lock_info_at` 的 PID 判活撞上 PID 复用会给出活人提示（它自我定位 cosmetic，locking.py:540-546，可接受）；busy_locks 是快照，与"clear-cache 判断后、删除前"的新启动命令存在固有竞态——docstring 直认这是防护不是锁（locking.py:358-361）；`_publish_at` 对账把窗口压到 lstat-rename 一瞬但**没有归零**，理论竞态靠"下游消费者全走 open_regular_at 拒链接"兜底（atomic.py:215-219）——纵深防御而非单点完美。
6. **ByteCounter 的 __getattr__ 透传**是鸭子类型的克制用法：只拦 read/readinto 计数，其余属性放行——包装对被包对象"透明"，tarfile 等上层完全不感知（progress.py:76-77）。

## 六、新人提示

- **改进度条宽度/配色/节流只动 progress.py 一处**（progress.py:21-26 的集中化初衷）；新增长命令直接复用 draw_bytes_bar/draw_count_bar，别再手搓 `\r` 拼 bar。
- **三条硬规矩**：新命令动容器 rootfs 前必须 ContainerLock（矩阵抄 paths.py:865-873）；写任何缓存/manifest/索引必须 atomic_write（绝不要裸 open(path,"w")——那正是 locking.py:60-62 与 atomic.py:33-37 记录的被利用形态）；打印任何来自容器/归档/registry 的名字必须过 quote_path。
- **调试利器**：`PD_FORCE_NO_COLORS=1` 强制无色看裸文本；CI/管道里进度条自动消失不是 bug 是设计；`tests/unit/test_progress.py:53` 明确测了无 TTY 静默。
- **先读头注释**是仓规（AGENTS.md/STRUCTURE.md 传统）：locking.py:21-80 与 atomic.py:21-68 两条头注释各自完整讲了一遍威胁模型，本篇不过是它们的展开——改动这两个文件前必须先证明你理解注释里的每一个场景。
- **测试即规格**：disown 的 fd 语义有专门竞态测试（test_locking.py:47"disowned 后锁活到副本关闭"）；atomic 的 KeyboardInterrupt 清理有专测；加行为先加对应用例。
- **练习**：①写一个 5 行脚本验证"两进程对同一 ContainerLock，第二个立刻退出且错误带 PID 提示"；②给 download_file 的 `_attempt` 人为短读（mock declared_length 返回偏大值），确认 tmp 被清、目标文件不存在；③解释为什么 `draw_count_bar` 在 total=0 时画满格而不是崩溃（progress.py:133）——答案在"源在计数后增长"的注释里（progress.py:131-132）。
