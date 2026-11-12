# 02 · proot_distro/dirfd.py — openat(2) 安全访问层：三条规则、一个 fd 栈

> 图谱定位：L01 基础层 · fan-in 44（31 生产模块 + 13 测试文件）。

## 一、角色定位：全命令共用的文件系统安全底座

dirfd.py 是一切触碰容器、镜像、缓存内容的命令共同踩着的那层。文件头自述（dirfd.py:21-25）：为 `copy`/`sync` 而生，如今锁、会话、`backup`、`remove`、层解包与 build engine 全建其上——凡把"guest 内容"当输入的读写删都汇到这里。

威胁模型写在架构注释（dirfd.py:27-35）：**路径解析的结果不可信任**——path 在解析与使用之间有时间窗，容器内进程可在窗里把某组件换成符号链接，让操作落到宿主文件。对策即第一公民形式：**一切条目以 (dir_fd, name) 寻址，目录一律 O_NOFOLLOW 打开**。fd 引用 inode 而非名字（dirfd.py:33-35）：名字随时可换，fd 永远指打开时确定的 inode。即本文件的安全模型——**"解析 ≠ 可写"**：对名字的检查（lstat/access）不构成写操作的许可，唯一可信的许可是描述符本身，每个操作从"打开即验证"拿 fd，之后只跟 fd 打交道。两端点由 `pin_path()`（proot_distro/paths.py:771）钉住（dirfd.py:32 指名），端点以下由 fd 逐跳下行保证。

## 二、内部结构：原语族分区

源码分节注释划出 Opening/Inspecting/Metadata/Copying/Removing 五区（dirfd.py:131-133、1118-1120）。**常量区**：`_O_RD_DIR=O_RDONLY|O_DIRECTORY`（dirfd.py:73）；`_O_PATH_ANY`（dirfd.py:78-79）让 chmod 能指向权限位打不开的条目；`REFUSED=frozenset((ELOOP,ENOTDIR))`（dirfd.py:82）兼收两种拒链 errno（:37-38、:102-104）。

**打开原语族**是门面，从严到宽：`opendir(path)`（dirfd.py:135-137）是唯一不挑符号链接的路径入口（信任根的名字是宿主的）；`opendir_at(dir_fd,name)`（dirfd.py:140-142）`_O_RD_DIR|O_NOFOLLOW` 是下行的一跳；`reopen()`（dirfd.py:145-154）把 O_PATH pin 换成可扫描 fd；`open_file_at()`（dirfd.py:157-159）强制补 O_NOFOLLOW；`open_regular_at()`（dirfd.py:162-185）承载规则一；`open_new_at()`（dirfd.py:188-215，O_CREAT|O_EXCL :210）承载规则二。

**下行族**四函数（`makedirs_under/makedirs_at/opendir_under`）共享走梯 `descend_at()`（dirfd.py:316-363）：每级从上级 fd `opendir_at` 下来，缺级就在同一 fd 下 mkdirat（dirfd.py:348）；path 版（:218-249）与 fd 版（:280-313）两类契约都按 fd 语义走。**检视族** `listdir_at/lstat_at/exists_at`（dirfd.py:378-395，lstat 带 `follow_symlinks=False`）只回答"是什么"，不构成许可。**元数据族**以 `_chmod_fd()`（dirfd.py:444-466）为枢纽：先 `fchmod`，O_PATH fd 上 EBADF（:452-454），回退 `/proc/self/fd/{fd}`（:463）；`chmod_at()`（dirfd.py:478-523）承载规则三；`copy_metadata()`（dirfd.py:416-432）是 fd 版 copystat（:419-421）。**fd 预算设施**（`MAX_OPEN_LEVELS=64`/`Levels`/`_revive_level`/`close_frames`，dirfd.py:792、801-908、911-934、753-772）详见第五节。

## 三、外部连接：上游两个信任根，下游三十一处

上游只有两类入口。一是 paths.py：`pin_path()` 钉 copy/sync 两端，`open_container_pair`（proot_distro/paths.py:147）给 login/remove 容器目录的 fd。二是 statedir.py：RUNTIME_DIR 与 BASE_CACHE_DIR 两个信任根按名打开一次（locking.py:167、199），其下组件经 `descend_at/opendir_at` 逐级下行（locking.py:205、219）——这些 $TERMUX_PREFIX 下的目录被非隔离容器读写绑定，组件与 rootfs 的一样是 guest 内容（statedir.py:35-39、dirfd.py:290-294）。

下游 31 个生产模块三档：轻档只拿检视/打开原语（session/sysdata/guestfile 等）；重档拿复制删除大招（copy/sync/backup/restore/remove/rename、build_engine、layer_diff、tar_extract、rootfs）；中档自己组走梯（locking、l2s、shm、atomic）。测试侧 13 个文件最有说服力：tests/unit/test_dirfd.py 648 行 32 个测试直接打本模块；tests/security/ 七文件围攻容器逃逸/pin TOCTOU/stale stat——test_copy_symlink_escape.py:387-410 埋 FIFO 验证"拒绝而非挂死"，test_deep_trees.py:424/:454 压 MAX_OPEN_LEVELS 到 8 并断言 fd 峰值在 `2*8+40` 内。

## 四、数据流：一次 `copy` 的 fd-chain 逐跳旅程

以 `proot-distro copy` 复制进容器为例，数据流是**逐跳打开、从不回头解析**的 fd 链：

1. **钉端点**：`pin_path()`（proot_distro/paths.py:771）对两端各解析一次产出根 fd——链条上仅有的路径解析，此后名字不再被解析（dirfd.py:32-33）。
2. **下行**：容器内路径由 `descend_at()`（dirfd.py:316-363）逐级 `opendir_at`，每跳一个 openat+O_NOFOLLOW——guest 窗内换掉任一级为符号链接，openat 当场 ELOOP/ENOTDIR 拒绝（:328-330），TOCTOU 被压缩进单次系统调用的原子性。
3. **枚举分派**：`copy_tree_at()`（dirfd.py:982-1115）显式栈循环，`listdir_at` 取名表（:1036）、`lstat_at` 判型（:1065）后四路分派——符号链接重造（:1068-1070）、目录 0o700 压栈（:1079/:1087）、文件 `copy_file_at`（:1098）、特殊文件 on_skip（:1101-1102）。
4. **端点读写**：`copy_file_at()`（dirfd.py:660-725）源端 `open_regular_at` 拿 (fd,stat)（:697）——O_NONBLOCK+fstat 双闸；目标端 `open_new_at` 造新 inode（:710）。数据经 `copy_data()`（:631-657），稀疏源按洞图复制（:553-588、:650）。
5. **元数据收尾**：`copy_metadata` 盖 mode/时间/xattr 到目标 fd（:714），replace 场景 `os.replace` 原子换名（:718-719）。mode/时间取自打开着的源 fd 的 fstat，绝不用调用方早先对名字的 lstat（:670-676，防 0644→0600 窗口换文件的 stale-stat 落盘，test_transfer_stale_stat.py:4-11 即此历史 bug）。目录元数据**回程**才盖：栈弹出（:1046）先 `copy_metadata` 再关 fd（:1055-1058）——源目录 0555 时先盖 mode 会拒掉自己的内容（:1049-1054）。

删除是同构镜像：`rmtree_at()`（dirfd.py:1176-1311）非目录直接 unlink、目录经 `_opendir_for_removal` 强穿权限下行（:1140-1151），rmdir 一律**从栈取父级 fd** 命名（:1266）——被停放层 fd 已关，帧内副本会指到复用的 fd（:1229-1233）。path 前门 `remove_tree()`（dirfd.py:1314-1361）只解析父目录（:1348）、拒 "/"（:1345-1346）。

## 五、设计决策：三条"看起来 fd 化了其实没有"的规则

文件注释（dirfd.py:40-58）点明灵魂：三条规则的"显然写法"看起来基于 fd，实际都挡不住植入条目。

**规则一：chmod 只经描述符**（dirfd.py:43-47）。Linux 的 fchmodat(2) 无 AT_SYMLINK_NOFOLLOW，`os.chmod(name)` 跟随符号链接——guest 窗内换条目为链接，chmod 落到宿主任意文件。`chmod_at()` 先 `O_PATH|O_NOFOLLOW` 打开（dirfd.py:508）在打开时拒绝链接，再交 `_chmod_fd`。加锁两道：`only_dir=True` 连类型一起拒（:491-493）；`single_link=True` 拒 st_nlink≠1 的非常规条目（:519）——硬链接到宿主文件正处于此状态，且 nlink 取自**刚打开的 fd** 而非名字的 lstat（:502-504），链接晚于检查才种下也被拒。

**规则二：O_NONBLOCK 拒 FIFO**（dirfd.py:48-52）。O_NOFOLLOW 对命名管道一言不发——打开读端 FIFO 阻塞等 peer，敌意 guest 永不给 peer，命令挂死。`open_regular_at()` 加 O_NONBLOCK 让 open 立即返回（写无读者的管道回报 ENXIO，:170-171），随后 fstat 拒掉一切非常规类型（:179-181）——设备、socket、带读者的管道一概进不来；该 flag 对常规文件无影响（:174-175）。

**规则三：写一律造新 inode**（dirfd.py:53-58）。对 openat 来说**硬链接根本不是链接**——它是同一文件的第二个名字，guest 把宿主文件链进 rootfs 后 O_NOFOLLOW 无物可拒，O_TRUNC 写穿直接改写宿主 inode。对策：`open_new_at` 用 O_EXCL 保证绝不"穿过既有名字写"（dirfd.py:210），撞残留先 unlink 名字再重试（:213-215）——unlink 删名字，inode 其他链接无损（:200-203）。已存在的目标走 temp+rename：`temp_name()` 处理 255 字节上限（dirfd.py:107-128），`os.replace` 原子换入（:717-719）；代价是硬链接目标失链（:682-684）。

**fd 预算：Levels 停放**（dirfd.py:775-908）。树深由 guest 决定，Android 软限 1024 个 fd，几秒就能造出删不掉的容器（:780-787）。超 64 层即停放**最浅**的层——关 fd、记 (dev,ino) 身份（:879-908）；回程经 `openat(child,"..")` 复活，内核从目录自身父链回答（:917-921），但目录可被**移动**换爹，身份不符即 ESTALE 拒走（:923-927）。**显式栈替代递归**（dirfd.py:1015-1022）：千层嵌套曾把 shutil.rmtree 打成 RecursionError——它不是 OSError，except 接不住（:1325-1330）；走树全改 while+栈，帧布局 `[fd,fd,...,owned]`（:758-762）供 `close_frames` 解中断现场。

## 六、新人提示

- **先接受威胁模型再改文件**：任何"对名字检查、再对名字操作"的两步写法都是回归；评审口径是"名字在我两次使用之间被换掉会怎样"。
- **拒链 errno 与 O_PATH 语义**：O_NOFOLLOW|O_DIRECTORY 对符号链接报 ENOTDIR（dirfd.py:37-38），判"被拒"走 `is_refusal()`（:102-104）；O_PATH fd 不能 fchmod（EBADF）/scandir，用 /proc 回退（:452-466）与 `reopen()`（:145-154）两个转换器。
- **端点别绕过 open_regular_at，写路径别落在名字上**：FIFO 挂死与设备读写由前者兜底（dirfd.py:165-176）；新增写必须 `open_new_at` 或 temp+rename——O_TRUNC 都是硬链接写穿的复活（:192-198）。
- **走树复用 Levels 帧布局**（dirfd.py:756-762）：前两槽 fd、末槽 owned，压栈在第二次打开**之前**（:1087-1091）；目录元数据**回程**盖（:1049-1055），mkdir 恒 0o700（:1077-1079）。
- **动名字 ≠ 写穿**：unlink/rename 作用名字而非 inode，这是 `copy_symlink_at` 先 unlink 再重建（dirfd.py:741-746）与残留清理（:213-215）的安全前提。
