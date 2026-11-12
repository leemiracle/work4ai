# 05 · install 三来源流水线：commands/install.py + install_local.py + helpers/{rootfs,download,tar_extract}.py

> 层位：命令在 L07「命令层」，三个 helper 在 L03「通用 helpers 层」（图谱 T06 步）。五文件合计 2632 行：install.py 420 / install_local.py 533 / rootfs.py 293 / download.py 725 / tar_extract.py 661。全部行号锚于 2026-10-27 在仓内现场核实。

## 一、角色定位：一条命令、三个来源、五份职责

`proot-distro install` 是整个工具的"入口产品"：用户第一次接触本仓，几乎都是从装一个发行版开始的。它接受的引用有三种形态，模块头注释把分工写得很清楚（install.py:21-29）——install.py 自己只做参数校验、来源分派、持锁与收尾，重活全在兄弟模块。

五份职责一句话版：

- **install.py（编排者）**：判定引用形态（本地路径 / URL / Docker 引用）→ 推导容器名 → 拿排它锁 → 调对正确的执行者 → 写 manifest.json → 跑 /etc 修正 → 失败清场。
- **install_local.py（归档解释器）**：本地文件与 URL 下载产物共用。流式探测前 500 个成员名，自动分辨 OCI image layout 与 plain rootfs tar 两 种格式，前者走 digest 信任链逐层校验，后者走 strip 启发式直接解包。
- **download.py（网络策略层）**：`install <url>` 的传输底座，但远不止——它同时是全仓（含 Docker registry transport）的 opener 工厂、重定向策略、超时与重试策略的唯一实现。
- **tar_extract.py（唯一解包引擎）**：plain tar 与 Docker/OCI 层共用一个流式解包器，仅差 `strip` 与 `handle_whiteouts` 两个参数（tar_extract.py:22-31）。防路径穿越是它的安全核心。
- **rootfs.py（装后修正器）**：解包完成后向 rootfs 写入 Termux/Android 集成所需的 `/etc` 内容——resolv.conf、hosts、Android UID/GID 注册。**勘误**：任务书说"rootfs.py 的发行版元数据"，源码实证它不含任何发行版元数据；镜像元数据（manifest/image_config/arch）由 install.py:326-342 写入 manifest.json，OCI 场景的内容产自 install_local.py:445-450 的返回字典。rootfs.py 纯粹是 /etc 修正。

三来源殊途同归：不管字节从哪来，最终都汇到同一个 `rootfs_fd` 描述符上解包、同一组 fixup、同一个失败清场路径。这是本流水线最重要的结构性质。

## 二、内部结构：五个模块的分区地图

### install.py——420 行编排者

**分流判定**是两条极简前缀规则：`_is_local_path` 只认显式路径语法 `/`、`./`、`../`、`~` 开头（install.py:74-82），`_is_url` 只认 `http://`/`https://`（install.py:85-87）。注释特意点明：裸 token `ubuntu` 一律按 Docker 引用处理，"即使 cwd 里恰好存在同名文件"（install.py:78-80）——杜绝"装错东西"的歧义。分流实现在 install.py:163-165 三行。既非本地也非 URL 的引用，先过 `parse_reference` 预校验（install.py:172-177），让 `ubuntu@sha256:<hex>` 这类 Docker 会拒的引用在**推导容器名和拿锁之前**就死掉，而不是等到 registry 报错。

**容器名推导**（install.py:192-225）：本地文件必须先 `os.path.isfile` 验存在（install.py:195）；URL 推名前剥掉 `?query` 与 `#fragment`（install.py:212）；文件名先按 `_ARCHIVE_EXTS` 十四种扩展名剥后缀（install.py:67-71），再归一化为 `[a-z0-9_.-]`、去打头非法字符、折叠连续横线（install.py:101-103）。三条路推不出合法名都统一提示 `--name NAME`。

**下载临时文件** `_cache_temp_file`（install.py:107-131）是个浓缩的安全故事：`tempfile.mkstemp(dir=BASE_CACHE_DIR)` 会解析名字，而缓存根是 guest 可重指的名字，于是改为 statedir 安步走到目录 fd、`dirfd.temp_name` 以 `pid+urandom` 拼临时名（install.py:125-127）、`open_new_at` O_EXCL 造文件（install.py:128）。注释说透了这个名字的真实作用：不是写通道，只是"预订"，防两个并发 install 撞名（install.py:117-121）——真正写入走 `atomic_replace`，而 rename(2) 替换站在目的地的符号链接而非跟随它。

### install_local.py——双格式探测与 OCI 信任链

架构注释（install_local.py:21-34）开宗明义：本地归档是"陌生人的文件"，且 `LAYER_CACHE_DIR` 与用户拉的每个镜像共享，未校验的 blob 一旦落进去就以"未来 pull 会信任的 digest"之名坐在那里。所以 OCI 分支的核心承诺是：**每个从归档读出的 blob 都对照归档自己声明的 digest 重哈希**。

入口 `install_from_local_file`（install_local.py:486-533）先用 `r|*` 流式模式读至多 500 个成员名，见 `oci-layout` 即判 OCI 并短路（install_local.py:509-514）；没见则把探测名交给 `detect_strip_count`。OCI 分支重开 `r:*` 随机访问模式并建索引（install_local.py:521-529）。三道资源护栏先于一切：JSON 成员读取上限 16 MiB（`_MAX_JSON_BYTES`，install_local.py:67）——上限加在**实际读出**的字节数而非成员自报的 size，读 cap+1 字节、多出来即拒绝（install_local.py:176-183）；成员索引上限 16384（install_local.py:77），且只索引 `_oci_open_member` 可能被问到的两类名字——`index.json` 与匹配 `blobs/<algo>/<hex>` 正则的成员（install_local.py:84-87, 481-482），后者由 `validate_digest` 先行把关，杜绝用伪造 digest 把查找路由到 `blobs/../etc/passwd` 这类穿越成员名（install_local.py:142-146）。

**信任链**自 `_extract_oci`（install_local.py:349-450）展开：`index.json` 按名读出、是归档的信任根（install_local.py:358，注释在 install_local.py:239-241）；此后每一步——镜像 manifest、镜像 config——都按 digest 寻址，`_oci_read_blob_json` 读出即 `require_data_digest` 哈希核验（install_local.py:245；实现在 cache.py:428-441）。架构选择 manifest 的三级策略（install_local.py:249-296）：单条目直接信任；多条目带 `platform.architecture` 则按 `linux/<arch>` 过滤；没有 platform 就走慢路径逐个读 manifest→config 探测架构（install_local.py:279-291）。层循环（install_local.py:404-432）每层先 `open_verified_layer(digest)` 查共享缓存（install_local.py:413）——命中即跳过；未命中走 `_oci_cache_layer` 从归档拷入缓存：边拷边 sha256（install_local.py:328-330），不匹配即 raise 且 `atomic_replace` 的临时文件自动消失、不留残骸（install_local.py:331-337 与 320-322 注释）；匹配则 `os.dup(tmp_fd)` 在 rename 前取同 inode 的第二描述符（install_local.py:342-343），调用方读的是"这些字节进去的那个 inode"而非"事后可能被顶替的名字"。最后 `apply_layer(layer_fd, rootfs_fd, digest=digest)` 逐层落盘（install_local.py:427）。

`_oci_open_member` 还拒绝硬链接与符号链接成员（install_local.py:155-159）：Python 的 `extractfile()` 会在归档内跟随它们，让精心构造的外层 tar 把一次读取重定向到无关成员（比如拿层 blob 冒充 index.json）。所有 JSON 解析错误统一归一为 RuntimeError（install_local.py:187-208），因为 install 的异常网只捕 `EOFError/OSError/TarError/RuntimeError`（install.py:385），一个裸 ValueError 就是 traceback。

**plain tar 分支**朴素得多也诚实得多：`detect_strip_count` 对前 500 个名字试 strip 0-4，按"该深度上落着多少个知名 rootfs 目录"打分取最高（install_local.py:101-119，`_ROOTFS_DIRS` 名单在 install_local.py:90-94），然后 `extract_tar_to_rootfs(strip=strip)` 直接解包、不处理 whiteout（install_local.py:122-130），返回 None——plain tar 没有 manifest 可写。另有个兼容性细节：zstd 外层归档要 Python 3.14，`require_read_support` 提前把话说清，免得探测报"corrupt tar"（install_local.py:501-502）。

### tar_extract.py——安全核心：钳制解析 + O_NOFOLLOW 逐跳落盘

架构注释 70 行（tar_extract.py:21-90）是全仓最长的威胁模型文档，值得整段精读。防穿越分两层，缺一不可：

**第一层：名字钳制**。每个成员名先 `lstrip("/").rstrip("/").split("/")`，strip 后任何 `..` 或空分量直接丢成员（tar_extract.py:365-370）；尾部 `.` 单独拒绝——它名指的是父目录本身，旧实现曾因此把一个符号链接成员 rmtree 掉整个目录内容（tar_extract.py:373-382）。父链再经 `safe_resolve_parts` 解析：逐分量 lstat，遇到符号链接读目标——绝对目标**重锚到 rootfs 根**（`resolved = []`，tar_extract.py:619-620），`..` 弹栈但永远弹不过根（tar_extract.py:594-596），链预算 40 跳防环（tar_extract.py:590）。重锚的精妙在于它同时是**语义正确**的：proot 运行时 guest 的 `/` 就是 rootfs，合法的绝对符号链接本该落在 rootfs 内（tar_extract.py:51-53）。不存在的分量原样收下——还没写的子树不可能是指向宿主的链接（tar_extract.py:603-606）。

**第二层：描述符逐跳**。注释把要害说穿了："解析只说成员*该*在哪，不使写它安全——因为解析按名字决策，而随后每个行动者又把名字重新解析一遍"（tar_extract.py:54-58）。旧实现 os.makedirs/os.remove/open(dest) 各自重新解析路径，早先成员植入 `evil -> /` 后，晚到的 `evil/passwd` 就顺着符号链接写到宿主。对策：rootfs 是**描述符**，`_Parents.get` 用 `dirfd.descend_at`（dirfd.py:316-363）从根 fd 逐级 O_NOFOLLOW 重走解析出的父链（tar_extract.py:260），每个成员以 `(dir_fd, name)` 落盘。解析后被换成符号链接的分量在 descend_at 处被拒（ELOOP/ENOTDIR）而非跟随——这正是"对归档安全的解包器"与"对同树并发写进程也安全的解包器"的差（tar_extract.py:60-68）。`_Parents`（tar_extract.py:235-271）按分量元组做一深缓存：tar 成员按树序到达，相邻成员几乎总共享父目录，缓存令开销摊到约每成员一次 openat（tar_extract.py:69-72）。

**各类型分派**（`_process_member`，tar_extract.py:360-441）：块/字符/FIFO 成员直接跳过（tar_extract.py:362）；目录成员若被符号链接占名则先 unlink 再 mkdir——overlay 语义就是替换而非穿透（tar_extract.py:410-418）；mkdir 的 exist_ok 只容忍已存在的**目录**，普通文件站着就让提取失败（tar_extract.py:419-429）；目录 chmod 强制 `| S_IRWXU` 保证后续成员写得进（tar_extract.py:430-431）。**whiteout** 是 Docker 层专属（plain rootfs 关闭）：`.wh.<name>` 删除同名兄弟、`.wh..wh..opq` 清空父目录（tar_extract.py:449-464），且 whiteout 分支取父 fd 用 `create=False`——"只删不建，不存在的目录里没有东西可删"（tar_extract.py:396-398）。注释里钉着一桩真实事故：`.wh...` 切片出 `..`，旧代码 os.path.join 进路径后 rmtree 掉了解包根的**上一级**——一个这种成员就在 install 途中清空了 `containers/<name>/`（tar_extract.py:469-476）；修复是结构性的：删除目标只以 `(dir_fd, name)` 寻址，且 `..`/`.`/空串一律不删（tar_extract.py:480-482）。

**硬链接**最讲究：linkname 与成员名同等过滤（防 `../../etc/shadow` 把宿主文件拷进 rootfs，tar_extract.py:506-528），且推迟到所有普通文件写完后才处理；拷贝时两端**重新解析**再 descend_at，防"链接成员之后才植入的符号链接"重定向任一端（tar_extract.py:294-301, 326-327）；源端 lstat 验 S_ISREG——硬链接成员名指向符号链接时它没有自己的内容可拷（tar_extract.py:336-342）。**普通文件**经 `open_new_at` O_EXCL 造新 inode（tar_extract.py:642）：这是 O_NOFOLLOW 给不了的最后一块——O_NOFOLLOW 分不清硬链接与普通文件，而 O_TRUNC 写穿硬链接会落到别的 inode 上（tar_extract.py:64-68, 630-634）。目录 mtime 最后倒序补戳（写文件会 bump 父目录 mtime，tar_extract.py:303-310）。

双入口设计：`extract_tar_to_rootfs` 收路径（install_local 用），`extract_tar_fd_to_rootfs` 收描述符+可选 `expected_sha256`（Docker 层走 layers.py:126-141 的 `apply_layer`，开 whiteout）——后者把哈希校验做成**消费时流式重哈希**：描述符钉死了 inode，但钉不住字节（inode 可被原地截断重写），所以 `_HashingReader` 边解包边算，`drain()` 把 tarfile 停在 end-of-archive 标记后剩余的压缩尾也抽干——"对前缀的 digest 不是对 blob 的 digest"（tar_extract.py:155-171，注释里那个 523 字节层只哈希到前 512 字节的教训）。校验失败是事后 raise，全树已落盘，但每个调用方都会丢弃树（tar_extract.py:204-208）。

### download.py——全仓网络策略层

架构注释（download.py:21-35）划出四条铁律：本程序所有请求都过 `http_opener()`（HTTP/HTTPS 而无其他）；重定向只跟 `RedirectPolicyHandler` 放行的；请求由 `new_request()` 构造，坏 URL 是 `InvalidRequest` 而非裸 ValueError；没有请求能永远等——默认 `NETWORK_TIMEOUT=120` 秒空转即死（download.py:114，注释论证"两分钟无一字节是死对端不是慢对端"）。

异常治理是 `NETWORK_ERRORS` 三元组（download.py:91）：urllib 的 URLError、裸 OSError、以及 http.client 的 HTTPException——最后一族**不是** OSError，chunked body 中途断掉的 IncompleteRead 曾经"穿过程序里每张网"直接把 install 打成 traceback。同类还有 `IncompleteResponse`（download.py:122-130）补 CPython 的一个著名沉默：Content-Length body 被截短时 `read()` **故意不报错**，`require_complete_body`（download.py:149-175）负责在读完对账。`download_file` 把它放在 `atomic_write` 上下文**内部**调用（download.py:685），短答案连临时文件一起带走，绝不会把半个归档当完整归档发布（download.py:682-684）。

**重定向策略** `check_redirect`（download.py:248-295）三拒：目标不是合法 URL；scheme 不在 http/https 或无主机——urllib 自家 handler 居然允许 ftp://（download.py:283-288）；HTTPS 降级到明文 HTTP——除非用户 `--allow-insecure` 显式豁免（download.py:289-295）。降级拒绝的理由写在注释里：tag 的 manifest、`install <url>` 的归档、`ADD <url>` 的文件都没有 digest 钉死，"明文那一跳上坐着的任何人决定装什么/构建什么，而用户从没被告知 TLS 已经停了"（download.py:262-268）。策略在 handler 里查两次（原始 Location 与拼好的绝对 URL，download.py:303-307）。opener 的 handler 清单刻意剔除了 ftp/file/data 三类（download.py:403-411）。

**重试策略** `retry_http`（download.py:595-631）+ `is_retryable_http_error`（download.py:553-592）：确定性失败（4xx 除 408/429、证书验证失败、RedirectRefused、InvalidRequest）立即重抛不重试；429/503 听 Retry-After 但封顶 60 秒（`MAX_RETRY_AFTER`，download.py:495），429 报 quota 耗尽（`RateLimit-Remaining: 0`）也直接放弃——"registry 的拉取配额按小时回填，隔几秒重试只是推迟同一场失败"（download.py:568-570）。这套策略是 URL 下载与 registry transport **共用**的唯一实现（download.py:603-605）。

`download_file` 本体（download.py:648-725）：UA 带 `PROGRAM_NAME/PROGRAM_VERSION`（download.py:669）、`atomic_write` 落盘、64KiB 块读+进度条、失败翻译成三类人话（降级重定向提示 --allow-insecure、证书错误提示 --allow-insecure、https 撞明文服务提示改 http://，download.py:700-717）。

### rootfs.py——装后 /etc 修正，全程对抗"镜像自己植入的符号链接"

架构注释（rootfs.py:21-40）给出定位：这些函数跑在"刚解包的、用户点名但没有写过一个字节的 rootfs"上，**它触碰的每个条目都是攻击者选定的内容**。威胁具体到四个 id 文件正是镜像最可能做成链接的名字。三件武器：`open_etc` 以 O_NOFOLLOW 打开 `etc`（rootfs.py:78）——镜像把 etc 做成指向宿主目录的链接，就能把本模块每次写都引过去，None 覆盖缺失/链接/非目录三种情形静默跳过（rootfs.py:69-75）；`_replace_at` 先 unlink 再 O_EXCL 造新文件（rootfs.py:113-115）——站在名字上的硬链接无从辨认，唯一安全姿势是不写穿任何旧 inode（rootfs.py:106-111）；`_chmod_at` **必须**走 fd 的原因很硬：Linux 的 fchmodat(2) 没有 AT_SYMLINK_NOFOLLOW，按名 chmod 等于把权限修改交给链接目标——注释记录了实证场景：镜像带 `etc/shadow -> ~/.ssh/id_rsa`，一次普通 install 就把宿主私钥放宽到 0644，"rootfs 还一个字都没运行过"（rootfs.py:167-171）。`_append_at` 则靠 `open_regular_at` 的 fstat 拒绝 FIFO——否则追加会永远阻塞等一个镜像不会提供的读者（rootfs.py:134-137）。

`register_android_ids_at`（rootfs.py:241-292）先把四个 id 文件全 chmod 成 0644（`_ID_FILE_MODE`，rootfs.py:55-57），再取真实 uid/gid/用户名拼 `aid_<user>:x:<uid>:<gid>:Termux:/:/sbin/nologin` 追加进 passwd（rootfs.py:262-265，create=True 兜底极简镜像）；shadow 用 `:*:` 锁死密码（rootfs.py:270-271）；group 按 `gid+附加组` 去重逐个追加、gshadow 可选不创建（rootfs.py:273-292）。双形态 API 设计（`*_at` 收 etc fd / 路径版收 rootfs 名）服务于两类调用方：install 一次跑全套用 `_at` 形态（etc 只解析一次），build 引擎每 stage 单项修正用路径版（rootfs.py:36-40）。

## 三、外部连接：上游入口与下游地基

**上游**：cli.py 的 `_COMMAND_HANDLERS` 把 `install` 注册到 `command_install`（cli.py:64）；`reset` 命令复用同一流水线重装。`install_from_local_file` 还有第二个隐式调用方——URL 分支先下载再交给它（install.py:314-318），"URL 只是还没到本地的本地文件"。

**download.py 的最大客户其实不在本流水线**：helpers/docker/transport.py 的 `AuthStrippingRedirectHandler` 直接继承 `RedirectPolicyHandler`（transport.py:157），registry 的 opener 也由 `http_opener` 构建（transport.py:189）。改 download.py 的重定向或重试行为，等于同时改 Docker pull 的行为——动它之前先跑 tests/unit/test_download.py（60 个测试）。

**tar_extract.py 的双向客户**：向上服务 install_local（plain tar，strip 模式）与 helpers/docker/layers.py:126 `apply_layer`（OCI 层，whiteout+流式 digest 模式）；后者同时被 registry pull 与 build_engine 的层回放使用。注意 tar_extract 刻意不 import helpers.docker（连 digest 字符串都不解析，只收裸 hex，tar_extract.py:200-202）——因为 docker 包反过来 import 它，这是防循环依赖的显式决策。

**rootfs.py 的第二客户**是 build_engine：每个 stage 创建时用路径版写 resolv.conf/hosts（rootfs.py:21-26 注释）。**install.py 的下游**是 paths.py 的 `open_container_pair`（paths.py:147，同时返回 container/rootfs 两个 fd）、sysdata.py:527 `setup_fake_sysdata`、atomic.py 的 `atomic_write`（atomic.py:131）与 locking.py:707 `ContainerLock`。缓存三件套 validate_digest/layer_cache_path/open_verified_layer 都在 helpers/docker/cache.py（cache.py:99/161/515），`oci_layers`/`oci_manifests` 布局定义在 constants.py:98-99。

## 四、数据流：三条来源线殊途同归

锁内 `_run_install`（install.py:237）的骨架对三来源完全一致，差异只在取字节那一步：

```
command_install (install.py:138)
 ├─ 分流: _is_local_path / _is_url (install.py:163-165)
 ├─ Docker 引用预校验 parse_reference (install.py:174)
 ├─ 推名 _resolve_install_name (install.py:179)
 ├─ ContainerLock 独占 (install.py:185)
 └─ _run_install (install.py:237)
     ├─ 存在性检查: container_is_installed —— 安步走而非 isdir (install.py:255)
     ├─ open_container_pair(create=True) → (container_fd, rootfs_fd) (install.py:291)
     ├─ 来源分支:
     │   A 本地: install_from_local_file(local_path, rootfs_fd) (install.py:308)
     │   B URL : _cache_temp_file → download_file → install_from_local_file (install.py:312-318)
     │   C Docker: pull_image(image_ref, rootfs_fd, dist_arch, insecure) (install.py:320-321)
     ├─ metadata 非空 → atomic_write manifest.json (install.py:326-342)
     ├─ open_etc(rootfs_fd) 一次性解析 etc (install.py:356)
     │   ├─ write_resolv_conf_at (install.py:360)
     │   ├─ write_hosts_at (install.py:363)
     │   └─ lstat 验 passwd 是普通文件 → register_android_ids_at (install.py:372-374)
     ├─ setup_fake_sysdata(rootfs_dir, container_fd) (install.py:378)
     └─ 失败: statedir.remove_state_tree 清场 (install.py:302)
```

**A 线（本地/OCI）**内部：`install_from_local_file` 探测（install_local.py:509-516）→ OCI 则索引（:526）→ index.json → 按 arch 选 manifest → 逐层 [查共享缓存 open_verified_layer → 未命中 `_oci_cache_layer` 边拷边哈希入缓存] → `apply_layer` 解包（install_local.py:404-432）。**B 线**只是 A 线前面挂了一节 download.py 车厢：临时文件名预订在缓存目录、`download_file` 原子落盘、然后完全按 A 线走。**C 线**进入 helpers/docker/pull.py:438，manifest/层双缓存与逐层流式验证在那一侧（03 篇专讲），但层落盘的最后一步仍回到 `apply_layer` → `tar_extract`。

三线交汇后的共同尾部值得再看一遍：`rootfs_fd` 从 `open_container_pair` 拿到后**全程不松手**——解包每个成员写在它下面、`open_etc` 从它解析 etc、失败清场的 remove_state_tree 也安步走到 containers 目录（install.py:281-302 注释把"为什么不能关掉 fd 改传路径"讲透：关了再按名解析，整个解包窗口就重新暴露给"会话重指名字"的攻击）。最终的镜像元数据落进 `manifest.json`：`image_ref`（OCI 场景从 annotations `io.containerd.image.name` 或 `org.opencontainers.image.ref.name` 提取，install_local.py:434-443）、`arch`（Docker arch 名经 `DOCKER_TO_ARCH` 反查，install_local.py:385-388）、manifest 与 image_config 全文（install.py:327-340）——这份文件就是后续 `run` 命令读 Entrypoint 的依据（install.py:408-411）。

## 五、设计决策：八条值得抄走的原则

1. **先验后锁**。名字推导、引用合法性、本地文件存在性全部在 `ContainerLock` 之前完成（install.py:163-181 vs :185）。错误越早死，锁越短、半成品越少。
2. **fd 是贯穿流水的针**。从 `open_container_pair` 到解包到 etc 修正，一次 pin 全程用；任何"按名再解析一次"都是窗口（install.py:344-356 注释对 fixup 阶段的同样论证）。配套纪律：校验和读取必须落在**同一个 inode** 上——`os.dup` 在 rename 前取描述符（install_local.py:342）、消费时流式重哈希（tar_extract.py:197-230）。
3. **信任根之外全按 digest 说话**。OCI 归档只有 `index.json` 按名读，其余每份文档、每个 blob 都对照 digest 重哈希；缓存命中也一样（`open_verified_layer` 名字不是证据，cache.py:24-27 注释）。同时诚实地承认 plain tar **没有密码学校验**——它的安全边界只有路径钳制，这是格式本身的局限而非实现偷懒。
4. **名字钳制与描述符重走是两道独立的闸**。`safe_resolve_parts` 防的是归档内容恶意，`descend_at` O_NOFOLLOW 防的是并发进程换组件——很多解包器只做了第一道（tar_extract.py:54-68）。
5. **资源上限加在实测值上**。16 MiB JSON 上限加在"实际读出的字节数"（防自报 size 说谎）、16384 成员上限是硬拒绝而非静默截断（install_local.py:166-184, 457-483）。
6. **确定性失败不重试**。4xx、证书错、策略拒绝的响应下一次还是同一个答案；Retry-After 封顶 60 秒尊重用户时间（download.py:553-592）。异常家族先归一（NETWORK_ERRORS/InvalidRequest/RuntimeError）再谈处理——install 的 except 元组才能保持一行（install.py:385）。
7. **安全修复要做成结构性的**。whiteout 的 `.wh...` 事故不是靠"多检查一个特例"修的，而是把删除改成 `(dir_fd, name)` 寻址后这类名字**天然无法表达**（tar_extract.py:477-482）；chmod 走 fd 同理——不是检测 `etc/shadow` 是不是链接，而是让"按名 chmod 指向别处"这件事不可能发生。
8. **一份实现服务两类调用方**。tar_extract 用两个参数（strip/handle_whiteouts）合并了原本 130/150 行的两份近似循环（tar_extract.py:22-25）；rootfs.py 用 `*_at`/路径双形态覆盖 install 与 build_engine；download.py 的策略层直接被 registry transport 继承。复用的方向永远是"共享底层、参数化差异"，而不是"复制再改"。

## 六、新人提示

**阅读顺序**：先 install.py 的 `command_install`/`_run_install` 拿到骨架（半小时），再 tar_extract.py 的架构注释 21-90 行（这是全仓威胁模型的最佳单篇读物），然后 install_local.py 的 OCI 信任链，最后 download.py 与 rootfs.py 可独立随时读。配套 ONBOARDING 第 4-5 节是同素材的更简版本。

**跑测试定位行为**：`pytest tests/security/test_tar_extract_traversal.py`（26 个测试，覆盖 `..`/绝对链接/尾部 `.`/whiteout 穿越/hardlink 目标穿越）、`tests/security/test_oci_blob_traversal.py`（12 个，专打 digest 路由穿越与缓存投毒）、`tests/security/test_rootfs_etc_escape.py`（11 个，含 `etc/shadow -> ~/.ssh/id_rsa` 场景与 FIFO 拒绝，test_rootfs_etc_escape.py:52-90）、`tests/unit/test_download.py`（60 个，重定向/重试/截断矩阵）。改任何一行为前先跑对应文件——security 测试就是行为规格。

**容易误读的三处**：① `_is_local_path` 的语义是"显式路径语法"不是"文件存在"——`./ubuntu` 与 `ubuntu` 走完全不同的线（install.py:74-82）；② `install_from_local_file` 返回 None 不是失败，是 plain tar 没有 metadata 的正常表达（install_local.py:494-495）；③ `extract_tar_to_rootfs`（路径版）不做 digest 校验，带校验的是 fd 版——别在需要完整性保证的场合调错入口（tar_extract.py:105 vs :177）。

**动手实验**：用 `tests/_builders.py` 的 `make_tar` 造一个含 `../../escape` 成员与 `evil -> /` 符号链接的归档，跑 `extract_tar_into` 后核对哨兵文件未被动——test_tar_extract_traversal.py:29-42 的 `_assert_no_escape` 就是现成断言模板。再造一个 `.wh...` 成员观察它被静默消费，对照 tar_extract.py:465-482 的事故注释理解"结构性修复"的含义。
