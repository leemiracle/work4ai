# 08 · 状态树与会话注册表：constants.py / paths.py / statedir.py / session.py

> 层位：L01 基础层（图谱 14 层最底层的安全与命名地基）。覆盖四个文件：
> `proot_distro/constants.py`（124 行）、`proot_distro/statedir.py`（265 行）、
> `proot_distro/session.py`（509 行）、`proot_distro/paths.py`（874 行，本篇取其"容器存储布局"面）。
> 所有行号锚均于 2026-10-27 在仓内现场核实。

## 一、角色定位：命名世界、守门人与会话账本

如果把 dirfd.py（见本系列 02 篇）看作逐跳打开目录的"原语库"，那么本篇的四个文件就是把这些原语组织成**策略**的地方，四者各管一段：

- **constants.py 命名世界**——整个状态树在哪里。导入期一次性决定 RUNTIME_DIR、CONTAINERS_DIR、SESSIONS_DIR、两级缓存目录的绝对路径（constants.py:75-99），全库 fan-in 63（ONBOARDING §2），是所有路径的单一事实源。
- **statedir.py 守门人**——怎样安全地*到达*状态树里的任何一个目录。它定义"信任根"模型：两个根按名打开一次，其下每一个组件都逐级 O_NOFOLLOW 下行（statedir.py:21-50 头注释），并给状态 JSON 读取定 16 MiB 上限。
- **session.py 会话账本**——谁在跑。`ps` 列出、`kill` 下手的全部依据：每会话一个 `<pid>.json`，存活判定靠"清掉 O_CLOEXEC 的独占 flock 跨 exec 继承"（session.py:27-33）。
- **paths.py 容器路径中枢**——容器这一种状态树的专用门面：组合 `containers/<name>/{rootfs, manifest.json}` 布局（paths.py:93-105），并把 statedir 的步行包装成"打开容器目录/rootfs/清单"等具体动作（paths.py:108-189）。它的另一半职责（`[container:]path` spec 解析、chroot 步行、TOCTOU 钉住）属 copy/sync 线，见 07 篇。

四者的依赖方向是严格的单向链：`constants ← statedir ← paths/session`，谁也不反向 import。session.py 里的 `_SESSIONS_PARTS`（session.py:97）刻意只存 `sessions` 这一个 basename，让信任根到会话目录的整段路都走步行而不是按名拼出来。

## 二、内部结构：四个文件逐个拆

### constants.py：124 行决定全库行为

三张面孔。**版本面**：`PROGRAM_VERSION` 用 `importlib.metadata.version()` 从安装元数据读，装不上（源码直跑场景）回落 `"rolling"`（constants.py:35-38）——所以 `pd --version` 在开发仓里打印 rolling 不是 bug。**平台面**：`_detect_termux()` 要求三条特征命中至少两条才认 Termux（constants.py:55-68）——platform 串含 android（或 `/system/build.prop`、`/data/app` 存在）、`TERMUX_APP__APP_VERSION_NAME`/`TERMUX_VERSION` 环境变量在、`TERMUX_PREFIX` 可读可执行。取二防的是在 Termux 环境变量被带进 ssh 会话等边角 case 里误判。**路径面**：Termux 分支 `RUNTIME_DIR = $TERMUX_PREFIX/var/lib/proot-distro`、`BASE_CACHE_DIR = RUNTIME_DIR/cache`（constants.py:76-77，cache 嵌套在 runtime 里）；非 Termux 走 XDG data 与 cache 两个互不相干的根（constants.py:79-86）。这一个差别直接塑造了 statedir 的 STATE_ROOTS 设计（下文）。

三个容易漏看的点：其一，constants.py:40 有一行**导入即副作用**的 `os.umask(0o022)`——进程内统一 umask，让其后所有 mkdir/open_new_at 造出的文件模式可预测（644/755），不继承父 shell 的奇怪设置。其二，`DEFAULT_FAKE_KERNEL_RELEASE = "6.17.0-PRoot-Distro"` 与固定时间的 version 串（constants.py:120-123）是 login 交给 proot `-k` 的假内核标识。其三，`LEGACY_ROOTFS_DIR`（constants.py:95）只服务旧安装迁移，新代码不得触碰。

**勘误（钉版）**：任务清单里说的"constants.py 发行版表"在本仓**不存在**。上游 shell 版 proot-distro 有 `SUPPORTED_DISTRIBUTIONS`（Ubuntu/Debian/Alpine 等官方 rootfs tarball 清单），而这个 Python 3.9+ 重构版改为 Docker registry 直连，`install` 接受任意镜像引用、`search` 查 Docker Hub（cli.py:188-190 注释明说）。help 总览页的自述就是定位声明："leveraging support of Docker registries to provide distributions of any kind"（commands/help/__init__.py:68-71）。读旧版资料时切勿把发行版表套到这里。

### statedir.py：信任根 + 逐跳步行 + 16 MiB 闸

头注释（statedir.py:21-50）是全仓最好的威胁模型教材，浓缩成三句话：

1. **根按名信任一次**。RUNTIME_DIR 与 BASE_CACHE_DIR 是仅有的两个可按名打开的目录，且缺失时按名创建——首跑机器不能因为自己的状态目录不存在而失败（statedir.py:27-29，open_state_dir 的 create 分支在 statedir.py:178-182）。
2. **根以下一切都是 guest 内容**。Termux 上两个根都坐在 $TERMUX_PREFIX 下，而它被读写 bind 进每个非隔离容器；guest 可以从容留一个 `containers -> <宿主目录>` 符号链接，按名的 `os.makedirs(exist_ok=True)`、`open()`、删除起点的 `opendir()` 全都跟过去（statedir.py:29-36）。
3. **对策是逐组件 O_NOFOLLOW**，调用者拿到的是步行验证过的描述符，不是它验证过的路径（statedir.py:38-42）。

`STATE_ROOTS = tuple(sorted({RUNTIME_DIR, BASE_CACHE_DIR}, key=len))`（statedir.py:62）排序有讲究：Termux 下 cache 在 runtime *里面*，短者（RUNTIME_DIR）先匹配，`cache` 这个目录本身因此落入步行范围而非被整体信任；非 Termux 两根无包含关系，至多命中一个（statedir.py:58-61 注释）。

`open_state_dir()`（statedir.py:156-215）是步行主体：根 `dirfd.opendir()` 按名打开后，每个组件 `dirfd.opendir_at(fd, part)`——即 `os.open(name, O_RDONLY|O_DIRECTORY|O_NOFOLLOW, dir_fd=...)`（dirfd.py:140-142）——符号链接或非目录组件在 Linux 上报 ELOOP/ENOTDIR，被 `is_refusal()`（dirfd.py:102-104）识别后统一翻译成带路径的 ENOTDIR `_refuse`（statedir.py:147-153, 203-208）。create=True 时缺的级用 `os.mkdir(part, 0o777, dir_fd=fd)` 就地造（statedir.py:192）——**必须**在已验证的 fd 下造，先 `os.makedirs` 再走会把每级暴露给换名竞态。fd 逐级换手：开新关旧（statedir.py:209-210），finally 兜底防泄漏（statedir.py:213-215）。`split_state_path()`（statedir.py:114-139）先 `normpath`，想爬出根的 `..` 让结果自然落在根外、答案变 `(None, None)`——永远不会拿着验证过的 fd 去开 `..`。`open_state_parent()`（statedir.py:218-229）给"对条目本身动手"的调用者返回 `(父fd, 叶名)` 对；`remove_state_tree()`（statedir.py:232-265）让父目录也经步行到达后再 `rmtree_at`，使植入的 `containers` 无法把删除瞄准宿主目录，且作为清理路径**永不抛**（statedir.py:244-247）。

**16 MiB 闸**：`MAX_STATE_JSON_BYTES = 16*1024*1024`（statedir.py:77），`read_state_file()`（statedir.py:82-111）按 1 MiB chunk（statedir.py:79）读，超限抛 `OSError(EFBIG)`，调用者按"文件不可读"处置。两个精妙处：上限**只施加于实际读出的字节**而非 fstat 的 st_size——文件报告的 size 不是可读内容的承诺，边读边追加的文件会先过检再超限（statedir.py:90-93）；16 MiB 取的是 install_local 给 OCI 归档 JSON 的同款上限，比本程序自己写下的任何状态文件高几个数量级（statedir.py:73-76）。威胁实在：sessions 目录 guest 可写，改造前 `json.load()` 在描述符上一路读到文件尾，guest 决定了一次 `ps` 要吞多少内存（session.py:342-349 的 _read_record 注释原话）。

### session.py：`<pid>.json` 注册表与 flock 生死簿

模块头注释（session.py:21-72）值全文精读。机制骨架：

- **一个容器多个会话**：login/run 拿的是共享容器锁，所以不能一个容器一条记录，按 PID 一会话一文件（session.py:22-25）。
- **存活判定不问进程问锁**：注册时对文件持独占 flock，fd 清 O_CLOEXEC（`os.set_inheritable`，session.py:174）后跨 `os.execvpe()` 继承给 proot 及其全部 guest 子进程；内核在最后一个持有者退出时自动放锁——崩溃、`kill -9` 都不用清理钩子，也不被 PID 回收骗过（`os.kill(pid, 0)` 的经典缺陷，session.py:27-33）。
- **ps 探测用共享非阻塞 flock**：被拒=独占锁还在=活着；拿到=没人持=死了、顺手 unlink（session.py:35-40）。用*共享*探测是让两个并发 `ps` 不互锁、不把死会话误报成活（session.py:38-40）。

注册流程 `_register_at()`（session.py:141-207）五步严密：① `pid = os.getpid()`——docstring 要求调用者"must be called from the process that immediately exec's into proot"，此刻 pid 就是未来 proot 的 pid（session.py:117-120）；② 临时名 `.{pid}.{urandom(4).hex()}.tmp` 经 `open_new_at` O_EXCL 造全新 inode（session.py:145-146, 161）；③ 清 O_CLOEXEC（session.py:174）；④ `flock(LOCK_EX|LOCK_NB)`，拿不到锁（文件系统不支持 flock）直接放弃跟踪——注册永远 best-effort，绝不阻塞会话启动（session.py:179-185, 42-44）；⑤ 写 JSON 后 `os.replace` 原子晋升为 `{pid}.json`（session.py:202）。第五步的注释（session.py:195-200）解释了三个性质：flock 挂在 open file description/inode 上，rename 保锁；同 PID 的陈旧文件被覆盖；目标名上若有 guest 植入的符号链接，被**替换**而非被穿透——rename(2) 两端都不 follow。

**名字即绑定**（session.py:59-72）：文件名是记录与进程的唯一纽带，于是历史上 `fake.json` 写 `"pid": 1234` 能让 kill 给一个无关 proot 发信号。现在的对策全在读取侧：`_record_pid()` 只认十进制规范拼写（session.py:257-274）——`007.json` 因 `str(pid) != stem` 被拒，一个 PID 不可能被注册两遍；`_validate_record()`（session.py:277-339）要求记录内 pid 必须**等于**文件名 pid，container 过 `is_valid_name`（names.py:40 的正则），kind 必须是 `SESSION_KINDS = ("login", "run")` 闭集（session.py:88），command 是字符串列表、start_time 是有限数，三个旗标（`_FLAG_FIELDS`，session.py:93）缺省 False——`detach` 键比另两个晚出生，跨升级还活着的会话没有这个键。净效果：伪造记录**至多描述它所在文件的 PID**，冒充不了任何别的进程。

`active_sessions()`（session.py:210-254）把僵尸回收做成了读取的副作用：listdir 后跳过点开头与不以 .json 结尾（正在写的 tmp 名两条都中，session.py:235-236），死文件 `unlink_quietly`（session.py:244-245），活的按 `(start_time, pid)` 排序。`session_holders()`（session.py:392-453）是 kill 的关键放大器：lstat 拿 `(st_dev, st_ino)`——特意不用 readlink 目标比对，因为 fd 是在 tmp 路径上打开、之后才 rename 的（session.py:405-406）——然后扫 `/proc/*/fd` 找还开着该 inode 的进程。它比记录 PID 强两头：PID 复用者不持 fd（不复用错杀），root proot 被 SIGKILL 后 guest reparent 到 init 也能找到——那是记录 PID 永远够不着的盲区（session.py:397-402）。`_session_alive_at()`（session.py:456-485）里还有一个"宁可误活不可误杀"的取向：任何 flock 错误都算活（session.py:474-476），防 running 会话被误 prune。

### paths.py：容器存储布局的中枢门面

布局约定一句话：**`containers/<name>/` 下两样东西——`rootfs/` 目录与 `manifest.json` 哨兵**（paths.py:93-105 的三个组合函数）。哨兵是 install 写入的"这是本程序造的容器"凭证，login/run 每次都读它的 Env 与 Entrypoint/Cmd（paths.py:292-317 docstring）。

门面层的关键分寸在 `_open_container_path()`（paths.py:108-134）：**FileNotFoundError 原样上抛**——"没有此容器"和"还没有此容器"都是普通答案，只有调用者知道问的是哪种；其他任何 OSError 一律 `crit_error` + exit 1 停命令，因为走到这里的调用者接下来就要写或删这个目录，报错文案直接教用户"remove or move that entry and try again"（paths.py:128-133）。`open_container_pair()`（paths.py:147-189）的 rootfs 是从容器自己的 fd `descend_at` 下来、而非从信任根重走一遍——两个 fd 因而不可能描述不同容器，也不会对中途改名的组件得出两次不一致的意见（paths.py:152-157）。

判定族回答三种问题：`container_is_installed()` 以"能否经步行打开 rootfs"为准（paths.py:192-206），取代会跟链接的 `os.path.isdir`；`installed_container_names()` 加 `is_valid_name` 过滤——清单打到终端，而终端会把控制字符当命令执行（paths.py:267-270），且清单是全程序唯一"植入条目不得停命令"的地方，列出来正是用户发现它的方式（paths.py:272-275）；`container_entry_lstat()`（paths.py:209-239）是 `remove` 专用的第三种问法——"这名字下有没有东西"，用 lstat 在 CONTAINERS_DIR 的 fd 上问，描述条目本身。它的 docstring 记录了一个真实的历史死锁：另两种判定对植入条目都答"未安装"，于是没有任何命令能删掉它，而 `_open_container_path` 的报错却叫用户去删——`remove` 因此有了自己的眼睛。manifest 读链（`open_container_manifest`/`read_container_manifest`/`manifest_image_config`/`container_image_origin`，paths.py:292-405）层层设防：open_regular_at 拒符号链接也拒 FIFO（FIFO 的 open 会挂起等一个 guest 永不提供的 peer，dirfd.py:162-185）、读经 16 MiB 闸、字段逐个形状检查——`manifest_image_config` 两层 isinstance 防 AttributeError 崩掉不捕获它的 login/run（paths.py:346-357），`container_image_origin` 对非字符串字段回空串，护住会拿它 `startswith('/')` 与 `canonical_ref()` 的三个调用方（paths.py:380-398）。

## 三、外部连接：谁在消费这层地基

**statedir 的消费者**横跨全库：atomic.py 的原子替换（atomic.py:121, 170）、docker 缓存双目录（helpers/docker/cache.py:214, 223）、build_cache 的索引与索引锁经 `open_state_parent`（helpers/build_cache.py:67, 127, 220）、生命周期命令 reset/remove/install/build 的清理与落盘（commands/reset.py:92、commands/remove.py:98、commands/install.py:302、commands/build.py:356, 391）、clear_cache 与 rename（commands/clear_cache.py:162-379、commands/rename.py:88）。**session 的消费者**四家：login 前台路径（commands/login/__init__.py:595-599，`_session_fd` 局部变量带 `noqa: F841` 保活到 exec）、login `--detach` 的守护孙进程（commands/login/detach.py:140，其 :29 的调用时序图注释值得一看）、ps（commands/ps.py:43, 53）、kill（commands/kill.py:64-66 的三家进口与 :189-197 的 holders→is_live→记录 PID 三级回退）。**constants** 是全库 fan-in 之最之一，**names.is_valid_name** 被 session 校验与 paths 清单共用——容器名规则单一事实源（names.py:21-24 头注释自述）。

反向也一样干净：statedir 只 import dirfd 与 constants（statedir.py:52-56），session 只 import dirfd/statedir/constants/names（session.py:74-83）。L01 层不向上看一眼。

## 四、数据流：一条会话从注册到回收的全程

以 `pd login debian --detach` 为例串起全链：

1. **注册**：login 组装 reg kwargs（container/kind/command_argv/user/isolated/minimal/detach）交给 `register_session(**reg)`（commands/login/__init__.py:595-599；detach 形态在孙进程里同样调一次，commands/login/detach.py:140）。此刻 `os.getpid()` 已等于未来 proot 的 pid。
2. **落盘五步**：sessions 目录经 `_sessions_dir_fd(create=True)`——RUNTIME_DIR 按名 makedirs + opendir，`sessions` 组件 O_NOFOLLOW 下行（session.py:100-112）——到达后走 tmp 新 inode → inheritable → 独占 flock → dump → replace 晋升（session.py:141-207）。
3. **跨 exec**：`_exec_proot` 的 `os.execvpe` 带着 fd 进入 proot；proot 再 spawn 的每个 guest 进程都继承它（session.py:28-31）。这就是"锁 fd 活着即会话活着"的物理基础。
4. **观测**：`pd ps` → `active_sessions()` 步行打开 sessions、逐名 `_record_pid`/`_read_record`（16 MiB 闸内）/`_validate_record`/存活探测（session.py:210-254）；USER/COMMAND 列还要过 `quote_path` 防 ESC 重绘终端（commands/ps.py:30-35 注释）。
5. **收割**：`pd kill` 先 `session_holders` 找森林根（commands/kill.py:189），锁文件无人持时按记录 PID 回退并验 `_root_is_proot`（commands/kill.py:191-197），TERM→QUIT 升级发信号。
6. **回收**：最后一个持有者（哪怕是 guest 里 reparent 到 init 的孤儿）退出，内核放锁；下一次任何 `ps`/`kill` 都会探测到无人持锁，`unlink_quietly` 顺手摘掉文件（session.py:244-245）。全程没有一行清理钩子代码参与。

状态树解析的支线以 install 失败自清为例：`statedir.remove_state_tree(containers/<name>)`（commands/install.py:302）→ split_state_path 切出根与组件 → open_state_dir 逐级 opendir_at 到父 → `rmtree_at(parent_fd, name, force=True)`（statedir.py:254-265）。

## 五、设计决策：为什么是这副形状

- **两层信任是被迫的最小妥协**。根必须按名（首跑机器、makedirs 语义），但只有根可以按名——Termux 的 bind 使根以下每个名字都是敌意输入。statedir.py:44-50 对边界做了罕见的诚实声明：步行防不住"名字事后被换"，以 (dir_fd, name) 继续寻址的调用者免疫重指向，回到拼路径的调用者（解包器、proot 解析 bind 源）只防"启动时已存在"的持久植入——而那才是 guest 从容可安排的形态，也是本层要关掉的。
- **flock 优于一切进程探测**。三个独立优点叠加：崩溃安全、kill -9 安全、PID 回收免疫（session.py:31-33）。共享探测防并发 ps 互锁（session.py:38-40）是同一机制的第二层收益。
- **名字绑定替代鉴权**。注册表没有签名、没有权限位，防伪全靠"文件名是唯一纽带"这条物理事实加上读取侧形状校验，把伪造能力压到零增益（session.py:59-72）。
- **16 MiB 施加于读出量而非 st_size**，封死"先过检再超限"的追加窗口（statedir.py:90-93）。
- **mkdirat 就地造级**，create 路径不预先 makedirs，保住"每级都在已验证 fd 下诞生"的不变量（statedir.py:192；paths.py:793-798 讲同一件事）。
- **错误取向不对称**：清理路径永不抛（statedir.py:244-247），探测错误一律算活（session.py:474-476），注册失败静默放行（session.py:42-44）——状态层的失败永远不许打断用户真正的操作。

## 六、新人提示

1. **先读头注释再读代码**。statedir.py:21-50 与 session.py:21-72 是本仓威胁模型的原始出处，STRUCTURE.md 的安全规则表都从这里派生；跳过它们直接看函数会漏掉一半设计。
2. **加会话记录字段是双边手术**：`_register_at` 的 payload（session.py:148-158）与 `_validate_record` 的检查（session.py:293-339）必须同步改，且新字段要向后兼容缺省——否则升级后 ps 直接不再列出还活着的旧会话。
3. **动路径布局要过三关**：constants.py 一处定义、STATE_ROOTS 的包含关系（新根若嵌套在旧根内，排序决定谁先匹配）、以及 conftest 沙箱是否在导入生产模块*之前*重定向了 XDG——constants 是导入期绑定 + umask 副作用，测试里顺序错了全盘路径指错地方（tests/conftest.py:22-23，ONBOARDING §6）。
4. **验证安全直觉**：tests/security/ 41 件覆盖符号链接逃逸八命令（test_container_dir_escape.py）、session 注册表伪造等场景，改这四个文件前先跑 `pytest tests/security`。
5. 一个好的自测问题：如果把 `os.replace` 晋升换成直接以 `{pid}.json` 打开写入，会同时丢掉哪三个性质？（答案散在 session.py:161 的 O_EXCL、:195-200 的 rename 三性质、以及 tmp 名躲避 active_sessions 过滤器的 :235-236。）
