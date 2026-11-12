# 10 · 测试基础设施与安全测试层：conftest / _builders / _registry + tests/security 41 件套

> 层位：L09「测试地基」（conftest/_builders/_registry 三件）与 L11「security 测试层」。覆盖
> `tests/conftest.py`（179 行）、`tests/_builders.py`（471 行）、`tests/_registry.py`（502 行）、
> `tests/tls/`（CA+服务器证书对）与 `tests/security/` 全部 41 个文件（557 个测试函数、34 处
> parametrize）。所有行号锚均于 2026-10-27 在仓内现场核实。

## 一、角色定位：威胁模型的可执行证明

ONBOARDING 把本仓灵魂定在 dirfd 安全模型（"guest 可写目录里的一切名字都不可信"），而
`tests/security/` 就是这句话的**可执行形式**：41 件不是按模块划分的功能测试，而是按**攻击面**
划分的遏制测试——每个文件头注释先陈述一段攻击叙事（谁、在什么窗口、把什么名字换成什么），
再用测试证明现状不中招。`tests/README.md:22-26` 给出官方定义："证明恶意的第三方 tar / OCI 镜像
/ 备份归档无法逃出目标 rootfs 或 containers 目录"。任务书归纳的六类威胁在文件层一一对应：

| 威胁类 | 代表文件 | 核心断言 |
|---|---|---|
| tar 穿越 | test_tar_extract_traversal.py、test_oci_blob_traversal.py、test_layer_arcname_traversal.py、test_copy_step_traversal.py、test_restore_dest_path.py | 解包/成员名/摘要/arcname 永不落 rootfs 外 |
| 容器目录逃逸 | test_container_dir_escape.py、test_guest_dir_escape.py、test_state_dir_walk.py、test_clear_cache_escape.py、test_image_cache_escape.py、test_build_dest_escape.py | 植入的 `containers/<name>` 符号链接被拒被绕开 |
| 缓存投毒 | test_layer_cache_integrity.py、test_build_index_paths.py | blob 按内容重哈希，不信文件名 |
| pin 拉取 | test_pinned_pull.py、test_build_stage_pin.py | `ref@sha256:…` 全链摘要校验，缓存条目不算数 |
| login 钉住 | test_login_rootfs_pin.py、test_login_host_side_pin.py | `--rootfs=.` + fchdir，fd 钉住 inode |
| TOCTOU 竞态 | test_copy_pin_toctou.py、test_build_write_toctou.py、test_backup_live_race.py、test_transfer_stale_stat.py | swap 被确定性重演，写入只认 fd |

与 unit 层（36 件，纯函数正确性）和 integration 层（17 件，真命令管线）的分工边界也写在
`tests/README.md:19-33`：security 测试不做"功能对不对"，只做"恶意输入出不去"。

## 二、内部结构：三件地基

### 2.1 conftest.py——时序敏感的沙箱

`proot_distro.constants` 在**导入期**一次性绑定 RUNTIME_DIR/CONTAINERS_DIR/IS_TERMUX，多数模块又以
`from ...constants import X` 按值绑定（`conftest.py:3-10` 的头注释把这条时序钉为 CRITICAL）。
因此 conftest 在 import 任何生产模块**之前**、在模块顶层完成三件事：把
`XDG_DATA_HOME/XDG_CACHE_HOME/HOME` 指进一次性沙箱（`conftest.py:21-24`）；清掉
TERMUX_VERSION/PD_DOCKER_AUTH 等八个环境变量强制非 Termux、匿名认证（`conftest.py:32-42`）；
把 tests/ 根插进 sys.path 让 `_builders` 可顶层导入（`conftest.py:47`）。随后 `_assert_sandboxed()`
（`conftest.py:61-69`）做防呆：解析出的路径不在沙箱内或 IS_TERMUX 为真就拒绝运行整个会话。

两条从实战里长出来的护栏：其一，清场不用 `shutil.rmtree`——深树会让它抛 RecursionError，而
RecursionError 不是 OSError，`ignore_errors=True` 接不住，一个测试留下的深树能把整场报告埋掉
（`conftest.py:75-91` 注释原文）；改用 `dirfd.remove_tree` 显式栈遍历，清不干净就**点名残余**让
下一个测试的 setup 失败（`conftest.py:141-149`）。其二，`_clear_child_subreaper()`
（`conftest.py:115-132`）：run_step 设置的 PR_SET_CHILD_SUBREAPER 是进程级且跨测试存活，会改变
后续所有孤儿进程的归宿、干扰 kill 的进程树遍历，故 autouse fixture `_clean_runtime`
（`conftest.py:135-157`）每个测试前后都复位 subreaper、清空 `locking._held_exclusive`、抹平
RUNTIME_DIR/BASE_CACHE_DIR 两棵树。live 测试由 `RUN_LIVE_TESTS=1` 门控跳过（`conftest.py:99-108`）。

### 2.2 _builders.py——"高层 API 拒造之物"的工厂

头注释一句话定位（`_builders.py:1-7`）：构造程序**吞进去**的原始构件，尤其是高层 API 拒绝创建
的敌意成员。四组能力：

- **敌意 tar**：`make_tar`（`_builders.py:104-114`）接收成员字典表，`_add_members`
  （`_builders.py:70-93`）绕过 tarfile 的路径清洗直接 `TarInfo(name)` 塞 `../../escape`、
  硬链接 linkname 穿越（`test_tar_extract_traversal.py:85`）、字符/块设备与 FIFO——
  `_TYPE_MAP`（`_builders.py:59-67`）覆盖全部七种成员类型。这是 tarfile.add() 做不到的。
- **OCI 构件**：`make_layer_blob`（`_builders.py:189-195`）产出 gzip 层并同步算 digest/diff_id；
  `seed_cached_layer`（`_builders.py:198-206`）直接把层写进 LAYER_CACHE_DIR 模拟"缓存已有"；
  `make_oci_archive`（`_builders.py:217-301`）从 index.json→manifest→config→blobs 全链按
  canonical_json 构造合法 OCI layout，`bad_index_digest` 参数（`_builders.py:278`）专供"伪造
  index 摘要"实验。
- **fd 适配器**：生产 API（apply_layer/pull_image/extract_tar_to_rootfs）一律收**描述符**而非路径，
  `dir_fd` 上下文（`_builders.py:136-149`）是测试持路径侧的适配器，注释明言"把所有权规则放在
  一个地方"——`apply_layer_file`/`pull_image_into`/`install_local_into`/`extract_tar_into` 四个
  包装（`_builders.py:152-186`）是安全测试最常用的入口。
- **容器/登录桩**：`make_rootfs`/`make_container`（`_builders.py:321-353`）造带 passwd/group/ELF
  shell 的最小容器；`file_map_entry`（`_builders.py:380-398`）造 COPY/ADD 的 file_map 条目——
  注释强调条目"只名组件树，永不名路径"，双消费者用 O_NOFOLLOW 重走组件（TOCTOU 防线在数据
  结构里）；`login_args`（`_builders.py:431-445`）给齐 login 全部旗标让测试只覆盖关心的。

### 2.3 _registry.py——进程内三源 OCI registry + TLS fixture

让 pull/push **不 mock 一行网络代码**地跑完探测、challenge、凭证、token 交换、重定向、上传全
流程（`_registry.py:1-4`）。`FakeRegistry`（`_registry.py:112`）在 127.0.0.1 起三个各自独立端口
（即三个 origin）的服务器：`registry` 走 /v2/ API（探针 401 带 Bearer challenge 指向 auth，
`_registry.py:375-394`；blob GET 一律 307 重定向到 cdn，`_registry.py:440-442`）、`auth` 是
token 服务（校验 Basic 凭证、按 scope 发 token，`_registry.py:316-333`）、`cdn` 模拟 S3 式
预签名存储——**带 Authorization 的请求一律 400**（`_registry.py:484-489`），这正是验证
transport 跨 origin 剥凭证头（`AuthStrippingRedirectHandler`）的关键机关。

策略旋钮专测真实 registry 的多样性：`reject_code` 可模拟 GHCR 的 403、ECR 的 400
（`_registry.py:308-313`）；`outsiders` 集合模拟"能登录但无权拉取"的账号（`_registry.py:227-230`
的 allowed 逻辑）；`grant_keys` 兼容 token/access_token 两种返回键（`_registry.py:126-128`）；
`upload_origin` 切换上传会话是否移交另一 origin（`_registry.py:130-131`）；`deny` 集合模拟
"token 中途被吊销"（`_registry.py:132-134`）。每个请求连 Authorization 头一起记录进
`Seen`（`_registry.py:255-270`），测试能精确断言"哪个服务器见到了哪份凭证"。

TLS 来自 `tests/tls/`：为套件单独造的 CA（私钥已销毁）签发 localhost/127.0.0.1 证书，P-256、
有效期 2000-2100、带齐 Python 3.13 VERIFY_X509_STRICT 要求的字段，再生命令在头注释
（`_registry.py:36-56`）；测试把 `SSL_CERT_FILE` 指向 ca.pem 即让**程序自身的证书校验**信任它，
不设则测"证书不受信"分支。服务器实现两处工程细节：`server_bind` 跳过 getfqdn 反查防慢 DNS
（`_registry.py:236-240`），`handle_error` 吞掉客户端半路走掉的 TLS 断连（`_registry.py:242-245`）。

## 三、外部连接：谁钉住谁

security 层向上咬合的生产模块形成一张精确的攻击面-防线对照表：tar 五件钉
`helpers/tar_extract.py` + `install_local.py` + `layer_diff.py` + `copy_step.py`；目录逃逸诸件钉
`statedir.py`（信任根步行）、`paths.py`（resolve/pin）、`atomic.py`；缓存两件钉 `docker/cache.py`
的 `open_verified_layer/open_required_layer`；pin 两件钉 `docker/pull.py` 与 `build_engine/stage.py`；
login 两件钉 `commands/login/__init__.py` 的 `open_container_pair` + `proot_cmd.py`；TOCTOU 四件钉
`dirfd.py` 的 openat 族与 `copy_tree_at`。向下它与 integration 层共享同一套地基（_registry 同时
服务 `integration/test_registry_auth.py` 的认证矩阵），与 unit 层共享 builders 的纯构件——
`test_add_spooling.py` 这类资源类测试也靠 `make_tar` 喂大归档。CI 侧（tests.yml）四类 pytest 分列
跑 3.9/3.12/3.15 三版本，security 是唯一按"威胁"而非"模块"组织的层。

## 四、六类威胁的测试手法深讲

### 4.1 test_tar_extract_traversal.py——穿越战术总纲与"活写者竞态"

断言骨架 `_assert_no_escape`（`test_tar_extract_traversal.py:33-44`）是全层范式：哨兵文件原封
不动 + `set(os.listdir(tmp_path)) <= {"root","outside","evil.tar"}` + 经典落点一二级父目录为空。
覆盖 `..` 成员（`:47`）、嵌套 `a/../../b`（`:57`）、空分量、前导斜杠落 rootfs 内（`:74`）、
硬链接 linkname 穿越整条丢弃（`:85`）。最精彩的是三段递进：符号链接写穿（writethrough）——
先植 `evil -> /abs/host-dir` 再写 `evil/pwned`，跨层版本（`:147-169`）正是真实 OCI 攻击向量，
断言宿主目录零写入且链接本身保留在 rootfs 内；whiteout 特判——`.wh...` 剥出 `..` 恰指向解包根
**上一级**（install 时即 containers/<name>/），`:250-268` 放一个 manifest.json 哨兵证明它删不动；
活写者竞态（`:351-365` 注释）——resolve 与 write 之间目录可被换名+植链，`_swap_after_resolve`
（`:367-384`）包住 `safe_resolve_parts` 在其应答瞬间换目录，`:387` 断言写入因 fd 寻址失败而非
落进宿主。`:424` 补硬链接盲区：guest 给宿主文件造的第二名字，openat 分辨不出，防线是
"文件成员替换名字、绝不写进链接的 inode"。

### 4.2 test_container_dir_escape.py——八命令对同一植入的反应

头注释（`:1-11`）讲透攻击前提：Termux 上 containers/ 在每个非隔离 guest 的可写绑定里，会话可
把 `containers/<name>` 留成指向任意可写目录的符号链接，而旧代码 `os.path.isdir()` 说"未安装"、
`os.makedirs(exist_ok=True)` 收下链接。测试矩阵覆盖八命令：install 拒（`:56`）、reset 拒（`:176`）、
remove 是唯一**该**动手的——只 unlink 链接本身不碰目标（`:190`），且修掉了"旧门槛 isdir 跟随
链接导致谁也删不掉植入物"的死锁（`:204`）；list 清单不把植入物算作已安装（`:277`）；
login/backup/copy/sync 全拒（`:370-426`）。两条深化：`test_post_extraction_fixups_follow_the_pin`
（`:109-159`）在 install_from_local_file 返回瞬间换目录，证明 resolv.conf/hosts/passwd 三项后处理
写入被换走的真 inode 而非新链接所指的诱饵 etc（诱饵 passwd 的 0600 也没被放松）；
`test_failed_install_does_not_clean_through_a_planted_parent`（`:162`）点出失败清理比写入更危险——
清理即删除。

### 4.3 test_layer_cache_integrity.py——"按内容不信名字"的全消费者矩阵

`_poison`（`:43-49`）把缓存里某 digest 名下的 blob 换成另一层，然后逐一证明**每个消费者都重哈希**：
pull 命中坏层→驱逐重拉（`:69-95`）；`_swap_between_check_and_apply`（`:98-109`）在验证与 apply
之间换名字下的 inode——fd 携带救得了换名（`:112-142`），救不了同 inode 截断重写，于是第二层
防线是流式消费哈希、失败弃树（`:145-166`）；离线时坏层宁可失败不应用（`:202`）；不可计算算法
的 digest（sha512）直接拒绝（`:222`）。install 路线证明归档声明别人镜像的 digest + 塞不同字节
会被拒且**坏 blob 不进共享缓存**（`:337-356`）——否则毒会在后续 pull 复用；好归档反过来"修复"
坏缓存（`:379`）。push/oci_writer/build stage 继承同样拒（`:404/:431/:446`）；build cache 命中
坏层=miss 重跑而非回放（`:488/:506`）。末节"blob 的目录也是名字"（`:530-597`）：O_NOFOLLOW 只盖
最后分量，`oci_layers` 整目录被植链时读取与**驱逐 unlink** 都不得穿透——`hijacked_layer_cache`
fixture（`:540-556`）造名字对、内容不对的诱饵，五个测试证明读不到、删不掉、不误报存在。

### 4.4 test_pinned_pull.py——`ref@sha256:…` 的内容寻址全链

进程内 `_Registry`（`:54-100`）按 digest 供文档并记录请求序列。`:145-159` 证明 pin 落在 index 上
时按摘要逐级取（index→manifest→config 的 URL 序列可断言），且**每一份文档字节原样入缓存**；
`:172` 证明 pin 旁的 tag 从不被咨询、两种拼法共享一个缓存键；`:183` registry 对 pin 答别的字节
→"does not match its digest"；`:193` pin 命名的 config 取不到是致命错（tag 可降级空 config，
pin 不行——"取不到 config 的就不是这张镜像"）。缓存侧的原则是**条目字段是 guest 可改的**：
`:224` 改写缓存条目的 layers/Env 指向毒层，离线第二次 pull 仍拿到真内容（文档重验、条目字段根本
不读）；`:247` parametrize 三处文档任一被篡改→重取而非使用，离线则失败绝不将就；`:277` 没有
documents 字段的条目=miss；`:291` tag 条目永远不能冒充 pin 应答；`:308` 语法不收的引用
（大写名、#frag、sha512）在网络前就被拒。

### 4.5 login 双件——rootfs 钉住与宿主侧钉住

`test_login_rootfs_pin.py` 头注释（`:1-15`）还原攻击：检查走过的路径进了 argv，而 proot 在一切
检查之后**按名字**解析 `--rootfs`。修复是 argv 改写为 `--rootfs=.`（`:87` 断言）+ 进程 fchdir 进
校验过的描述符，proot 于是对 getcwd()（inode）而非名字做规范化。`:94-114` 在 `_detect_dist_type`
返回瞬间换目录+植链，断言 exec 时 cwd 的 `(st_dev, st_ino)` 仍是真 rootfs——用 inode 身份而非
路径字符串证明钉住。`:117-147` 是配套的诚实性设计：`--get-proot-cmd` 打印的是**路径**形态，
无法携带 pin（"描述符不是 shell 行装得下的"），于是 stderr 追加"inspection"告示而 stdout 保持
纯命令可重定向——文档不冒充分离保证。`test_login_host_side_pin.py` 把同一手法铺到 exec 前的
**每个宿主侧步骤**：`swappable` fixture（`:43-78`）造真假两个完整容器（真 rootfs 的 passwd 写
uid 4242/REALSH，诱饵写 9999/DECOYSH），在 pin 之后换名，断言 `--change-id=4242:4242`、
`HOME=/realhome`、`/bin/REALSH`、且输出串里 `9999/DECOY` 零出现（`:95-121`）；dist_type 判定
（`:124`）、profile.d 片段落点（`:171`）、sysdata 目录（`:188`）、shm 0700/1777 权限落点
（`:203-218`）同理。`:155-168` 是罕见的"双断言"：同一 read_guest_file 调用，带 root_fd 参数得
真内容、不带得诱饵内容——钉与不钉的对照在同一测试里。

### 4.6 TOCTOU 四件——竞态的确定性重演

共同方法论：**不真赛跑**。`test_copy_pin_toctou.py:6` 记录实测基线——无防护 copy 面对单攻击
线程 15% 成功率——但测试用 `_racing_resolver`（`:140-156`）包住 resolve 在其应答瞬间注入 swap，
"这就是竞态输家的处境"。pin_path 机制四测：换件被检出报 "changed while it was being resolved"
（`:44`）、pin 后换名写入仍落真 inode（`:61`）、O_NOFOLLOW 盖住 fd 盖不住的末分量（`:87`，断言
errno.ELOOP）、host 形态与 inside 形态的契约（`:105/:114`）。命令级：copy/sync 在 resolve 后换件
中止（`:159/:190`）、末分量植链 ELOOP（`:224`）；"makedirs 窗口"一节（`:254-260` 注释）记录
第二层修复——先 makedirs 再 pin 仍有窗口，改为 pin_path(create=True) 沿 O_NOFOLLOW 步行**造**
父目录，窗口归零；根下换件靠逐层携带 dir_fd（`:344` 的 copy_tree_at 中途换 sub、`:379` 命令级
递归 copy、`:414` sync 且报"changed to a symlink during the transfer"）；`:456` 证明
sync --delete 对指向宿主的 extra 链接只删链接不枚举目标。`test_build_write_toctou.py` 同法覆盖
COPY 物化器与层打包器双半（`:43` 拒已变链的父、`:140` 组件拒绝、`:164` 层打包跳过链父下条目、
`:204` snapshot 不降入链目录）；`test_backup_live_race.py` 针对"backup 只持共享锁所以会话可同时
活动"的前提（`:1-13`），把 walk 取到的 stat 传入后换条目再调消费函数——chmod 不穿（`:55/:68`）、
硬链接宿主文件不被 chmod（`:103`）、打包读被换目标（`:205`）、换入 FIFO 不阻塞（`:251`）、
容器目录检查后换链仍拒（`:312`）。`test_transfer_stale_stat.py` 则抓住**陈旧 stat**而非 swap：
lstat 与读字节之间源被替换，旧 size/mtime 判"已最新"漏传、旧 mode 盖新内容（0600 变人人可读），
修复是"描述字节的 stat 是读它的描述符的 fstat"。

### 4.7 其余代表件

`test_copy_symlink_escape.py`（41 件中最大，33 个测试）专打 `escape -> /` 类容器内链接与端点
文件类型：绝对/相对/父组件/递归/移动五形态全钉 rootfs 内（`:69-146`）、源链接读不出宿主文件
（`:197`）、rmtree --force 不 chmod 链接目标（`:316`）；工程亮点是 `_Blocked` 故意**不是**
OSError（`:25-33`）——被测代码会把 OSError 收拾成干净的 exit(1)，挂死和拒绝就分不清了，
`_deadline`（`:35-47`）用 SIGALRM+itimer 把"卡住的 open"变成测试失败，`:387` 的 FIFO 测试
正是"O_NOFOLLOW 管不了管道"的实证。`test_build_stage_pin.py` 把 stage rootfs 从路径改成描述符
后逐操作验证（snapshot/层打包/物化/COPY --from/WORKDIR/USER/RUN 全部落 pinned inode，
`:62-233`）。`test_deep_trees.py` 是 DoS 侧：`DEPTH = 1200`（`:51`）越过默认 1000 递归限与 1024
fd 软限，copy/sync/backup/remove 各 walk 必须显式栈完成且 fd 全数归还（`:164-311`）。
tar 穿越三兄弟收口：`test_oci_blob_traversal.py:15-21` parametrize 四种伪造 digest
（`sha256:../../../etc/passwd` 等）全被 `_oci_blob_path` 拒；`test_layer_arcname_traversal.py`
管 WORKDIR/COPY 目标侧——绝对路径的 `..` 曾直通 os.makedirs 与层打包器（"层是离开机器的构件"）；
`test_copy_step_traversal.py` 管 COPY/ADD 源侧——词法前缀检查看不见链接，改用与解包器同一套
钳制步行加描述符重走。`test_guest_dir_escape.py` 头注释给出一条结构性决策：/dev/shm 商店放
rootfs **兄弟**而非其内，因为 proot 挂载绑定源时按名字解析发生在一切检查之后。

### 4.8 其余 26 件归类速览

**状态树步行族**：test_state_dir_walk（信任根下不得按名触达任何组件）、test_atomic_state_paths
（atomic_replace 目标目录与临时名都可被植链/被 readdir 偷看后替换）、test_lock_path_escape
（`<name>.lock` 名字完全可预测，open(w) 会截断宿主文件、FIFO 会挂死）、test_build_index_paths
（构建缓存索引与锁同病）、test_session_registry_escape（假 sessions 目录 + `ps` 曾清空所有
.json）、test_state_json_caps（合法但巨大的 JSON 撑内存——上限测试）、test_rename_migrate_paths
（rename/迁移的 isdir+rename 双跟随）。**缓存目录族**：test_clear_cache_escape（测量遍的
os.walk/stat/chmod 全跟随链接）、test_image_cache_escape（清单/删除/孤儿计算三消费端）、
test_layer_publish_path（层晋升的 makedirs+replace 窗口）。**guest 内容族**：test_guest_file_reads
（读容器 /etc/passwd 的 chroot 语义）、test_rootfs_etc_escape（解包后 host 侧 chmod/open 修正）、
test_arch_probe（ELF 探测曾按 host 解析路径中段且 FIFO 阻塞）、test_container_manifest_read
（manifest.json 既是符号链接诱饵又是 FIFO）、test_l2s_escape（link2symlink 两跳链可由 guest 伪造）、
test_sysdata_escape（假 /proc 条目被会话替换后不得 chmod/绑定宿主文件）、test_verbose_escapes
（名字里的 ESC 序列不得上终端）、test_bind_validation（--bind 规格）。**build 配置族**：
test_base_image_config（FROM 收养的 config 字段类型错误→命名报错而非 traceback）、
test_add_spooling（ADD 大归档的内存接管→落盘 spool）、test_image_env_injection（镜像 Env 里的
LD_PRELOAD 类名字按**出处**过滤——LD_* 对未受限的加载器意味着宿主代码执行）。**元数据族**：
test_sync_hardlink_metadata（硬链接是 O_NOFOLLOW 的盲区——"传输绝不写非自己创建的 inode"，
连 fchmod 修 mode 也不行）。

## 五、设计决策

1. **确定性竞态重演优于概率赛跑**：所有 TOCTOU 测试都用"包装函数在关键应答点注入 swap"
   （`_swap_after_resolve`/`_racing_resolver`/`_swap_between_check_and_apply`），注释统一表述
   "这就是竞态输家的处境"——测试永不闪烁，且每个测试都带 `assert swapped` 自证真的触发了
   注入（如 `test_copy_pin_toctou.py:288`）。15% 的实测成功率只留在注释里作为威胁现实性论据。
2. **断言用 inode 身份而非路径字符串**：`(st_dev, st_ino)` 对（login_rootfs_pin:114、
   host_side_pin:229-233）与 `os.path.lexists` 配合，是"钉住"唯一诚实的证明方式。
3. **哨兵+白名单目录断言**：`_assert_no_escape` 式的"外面什么都没多"比逐条断言攻击产物不存在
   更强——它兜住尚未发明的落点。
4. **异常类型即测试语义**：`_Blocked` 非 OSError（防被测代码把挂死收拾成拒绝）、conftest 的
   RecursionError 教训（ignore_errors 接不住非 OSError）——两层都把"错误分类学"当设计输入。
5. **拒收但不销毁**：毒层驱逐后文件检查仍在（layer_cache_integrity:199）、植入链接"不是我们
   能靠哈希它来删的"（`:595-596`）、push 拒毒层但本地构建层无处可再取故绝不删（`:404-428`）——
   丢失后果与威胁等级配对。
6. **_registry 的三 origin 独立端口**是教具决策：跨 origin 剥凭证（cdn 拒 Authorization）只有在
   origin 真的不同时才可断言，单端口 mock 永远测不出 transport 的重定向策略。

## 六、新人提示

- **改任何 dirfd/paths/tar_extract/cache 代码前，先跑对应 security 件**：ONBOARDING 第 7 步
  "改代码前先读对应 security 测试"是硬规矩；这些测试的注释就是漏洞史（CVE 级叙事全在文件头）。
- **新增安全测试的模板**：conftest 沙箱与 autouse 清场自动生效；敌意构件先查 _builders 有没有
  （七类 tar 成员/OCI 全链/ELF 桩/容器桩/login 桩均有）；竞态类照抄 `_racing_resolver` 模式并
  务必带 `assert done/swapped` 自证触发。
- **别用 shutil.rmtree 清 tmp_path 下的深树**（pytest 自己的 reaper 就是 rmtree，深树要测试
  自己清，`tests/README.md:47-53`）；也别在深树 helper 里每层持 fd（软限 1024 会先于被测代码
  耗尽，`tests/README.md:54-56`）。
- **已知覆盖边界**（`tests/README.md:76-85`）：真 login/run 的 execvpe→proot→发行版 shell 不可
  单测，由 `--get-proot-cmd` 断言 argv + live 门控测试兜底；run_step 的真实 proot 调用仅 live
  build 测试触达；IS_TERMUX 分支靠纯函数直调加 per-module monkeypatch。TLS 测试注意 Python
  3.12 起 HTTPS handler 建立马 context，须在设 SSL_CERT_FILE 后重建 transport 的 opener
  （`tests/README.md:72-74`）。
- 一个自检问题：为什么 `test_login_rootfs_pin.py:117` 打印路径形态反而是**更诚实**的设计？
  答案在 `:128-147`——打印件无法携带 pin，与其假装等价，不如明示降级；这是"保证的边界也要
  被测试陈述"的范例。
