# 04 · `proot_distro/helpers/build_engine/`——把 Dockerfile 解释执行成 OCI 镜像

## 一、角色定位

`proot-distro build` 做一件通常属于 Docker daemon 的事：拿一份 Dockerfile，产出可 push、可 `docker load`、可离线 install 的 OCI 镜像。build_engine 就是这个**有状态解释器**（engine.py:21-27 自述）：遍历 `helpers/dockerfile.py` 纯解析产出的指令记录（`{name, value, flags, exec_form, heredocs, lineno, raw}`，dockerfile.py:83-86），逐条分派给 handler，一边改 rootfs 一边累计 image config。与 Docker 的两条根本差异决定全包气质：**没有 pid namespace**——RUN 留下的进程要靠自己当 child subreaper 收割（run_step.py:38-40）；**没有 overlayfs**——层增量靠 snapshot→执行→snapshot→diff 拍出来（run_step.py:27-29）。入口在 `commands/build.py:254` 构造引擎，`build.py:363` 的 `_make_build_tmp` 先以 O_NOFOLLOW 造好 0700 scratch 根连同描述符交给它。

## 二、内部结构

| 模块 | 行数 | 职责 |
|---|---|---|
| `engine.py` | 726 | BuildEngine：预扫描、分派、FROM 三分支、history 记账 |
| `handlers.py` | 390 | 13 个 metadata-only handler + HANDLERS 分派表 |
| `copy_step.py` | 1092 | COPY/ADD：file_map 中间表示、四种源、物化+打层 |
| `run_step.py` | 755 | RUN：缓存查询、proot 执行、subreaper 收割 |
| `stage.py` | 119 | Stage：每个 FROM 一份，作用域+层序列+两个描述符 |
| `constants.py` | 60 | PREDEFINED_ARGS / EXPANDS_VARS / needs_proot() |
| `parsing.py` | 155 | 无状态字符串件：split_arg/parse_chmod/is_tar_header |
| `users.py` | 103 | 对照容器内 /etc/passwd 解析 --chown 与 USER |
| `dockerignore.py` | 84 | .dockerignore 模式匹配 + 极简 glob |
| `errors.py` | 23 | 全包唯一异常 `BuildError` |

任务书十模块中的 layer_diff（771 行）与 oci_writer（283 行）物理上在上一层 `helpers/`（L03 构件），但只服务 build 链，本篇一并精讲。分派核心是 `HANDLERS` 字典（handlers.py:373-390）：16 个指令名→函数，RUN/COPY/ADD 实现体住在 run_step/copy_step，表统一挂 handlers——**一张表就是分派语义的全部**；FROM 与 ONBUILD 不在表里，由 `_dispatch` 特判（engine.py:407-421），因为它们改的是"哪个 stage 在说话"而非 stage 内容。

## 三、外部连接

**上游**：仅 `commands/build.py`——按 tag 持 BuildLock（build.py:235，按锁路径排序防死锁），跑完经 `build_manifest_and_config`（build.py:284）→ 每个 tag `store_in_cache` 落 manifest 缓存（build.py:294，此后 `install <tag>` 走 pull 的完全离线分支）→ `write_oci_archive` 输出 tar（build.py:305）。

**向下**：L04 docker 子包供 `pull_image/apply_layer/open_required_layer/manifest_config_digest`（engine.py:37-40）；L03 构件 layer_diff（快照/差分/打层）、build_cache（recipe hash 索引）、dockerfile（纯解析）、tar_extract 的 `safe_resolve_parts`（钳制走读，handlers/copy_step 共用）；底座 dirfd（描述符寻址）、atomic、guestfile（users.py:32 走读容器文件）、execenv（LD_*/PROOT_* 唯一规则源）、arch/shm/sysdata/l2s（proot 运行时适配）。

**错误契约**：`build.py:268-277` 只 catch `BuildError` 与 `OSError`，故子包把 shlex 的 ValueError（parsing.py:54-59）、越界 chmod 八进制（parsing.py:84-88）、tarfile.TarError（copy_step.py:908-916）、Popen 的 ValueError/E2BIG（run_step.py:338-345）全在最内层转译——**归一发生在产生处，不是捕获处**。

## 四、数据流：一条 Dockerfile 的完整旅程

### 4.1 预扫描与主循环（engine.py）

`run()`（engine.py:313-328）先 `_prescan`（engine.py:332-348）：收集首个 FROM 前的全局 ARG、正则抓出全部命名 stage（engine.py:54）、校验 `--target`（engine.py:350-355）。随后线性遍历：`_announce` 打 Step N/M 横幅（engine.py:381-395）→ `_dispatch`。目标 stage 的停止条件藏在 FROM 里：当前 stage 即目标时，下一个 FROM 触发 `_stop_after`（engine.py:506-512）。变量展开只作用于 shell 形态的 `EXPANDS_VARS` 指令（constants.py:41-44；CMD/RUN 留给 shell 自己展开），作用域按 Docker 语义叠层：宿主 PREDEFINED_ARGS → TARGET*/BUILD* 架构注记（engine.py:370-377）→ 本 stage ARG → ENV 永远赢（engine.py:478-499）。每条指令执行完，`_run_with_history` 比较 `stage.layers` 增量追加一条 OCI history（engine.py:432-445）——非空层 history 条数必须等于 `len(diff_ids)`，否则 Docker Hub 的 Image Layers UI 不显示（engine.py:436-441）；`created` 固定 epoch 保可复现（engine.py:457）。

### 4.2 FROM：stage 的诞生（engine.py:503-615）

`_make_stage_dirs`（engine.py:275-304）从 scratch 根描述符逐级 O_NOFOLLOW 下行造 `stage-N/rootfs`，**留下的是描述符不是名字**。三分支：`FROM scratch` 给空 config（engine.py:540-541）；`FROM <stage>` 走 `_inherit_from_stage`（engine.py:617-658）——JSON 往返深拷贝父 config（连带 history），逐层重哈希验证后 apply 到新 rootfs；否则 `_pull_base_image`（engine.py:660-714）拉镜像并把 manifest 层表抄进 `stage.layers`。拉来的 config 必过 `_adopt_image_config`（engine.py:81-198）：逐字段形状校验（`"Labels": ["a"]` 这类畸形在采纳点拒绝而非下游 AttributeError），并滤掉 Env 里的 LD_*/PROOT_* 与不可导出项（engine.py:190-196）——用户自己 Dockerfile 的 ENV 不受限（那是作者对镜像的陈述），只有陌生人 config 与 ONBUILD 触发器受限（handlers.py:95-105）。随后 Env/WorkingDir/User/Shell 灌进 stage 作用域（engine.py:550-561），全局 ARG 清零待 `ARG NAME` 重声明（engine.py:566-567），写 resolv.conf/hosts 让 apt 可用（engine.py:582-583），最后把基镜像 OnBuild 触发器当 Dockerfile 行解析执行（engine.py:587-615，`_firing_onbuild` 标志让 do_env 区分来源）。stage 以名和序号双重注册，`COPY --from=0` 按索引可查（engine.py:569-573）。

### 4.3 COPY/ADD：file_map 中间表示（copy_step.py）

`_do_copy_or_add`（copy_step.py:318-443）是唯一入口，`do_copy`/`do_add` 只是两个布尔旗（copy_step.py:308-315）。流程：解析 token → 拒绝 BuildKit 专属 flag（copy_step.py:336-341）→ `--from` 解析成另一 stage 的 rootfs 或 `_pull_throwaway_image` 现拉的临时镜像（copy_step.py:446-487，按引用 hash 开 `copyfrom-<slot>` 槽复用）→ 源分 url/ctx/rootfs 三类（copy_step.py:361-369）→ 逐源填 `file_map`（arcname→条目 dict）→ `_materialise_files` 落盘 → `write_files_layer` 打层。安全骨架三件：**`_SourceTree`**（copy_step.py:85-175）用钳制走读解析源——symlink 组件会跟（镜像里 `/usr/bin/python -> /usr/local/...` 是合法语义），绝对目标重锚 rootfs、`..` 爬不出去，末组件故意不解析（COPY 拷符号链接本身）；spec 里写 `..` 直接拒绝（copy_step.py:177-189）。**`_Spool`**（copy_step.py:197-255）让 ADD 的 URL 响应与压缩包成员全部 spool 到 scratch——旧实现整指令驻留内存，一个大 ADD 就能 OOM（copy_step.py:28-36）。**`_materialise_files`**（copy_step.py:920-1000）排序 arcname 保证父先于子，目标父目录钳制解析后以 `(dir_fd,name)` 写入：目录条目先掀掉同位符号链接（否则 ADD 的 `etc/` 会 chmod 到宿主目录上，copy_step.py:1029-1040），文件走 O_EXCL 新 inode。ADD 自动解包按魔数嗅探（parsing.py:137-155，ustar 偏移 257 与 gzip/bz2/xz），首 header 失败=不是压缩 tar，按普通文件抄（与 Docker 一致）；已记录成员后失败才是真损坏（copy_step.py:815-917）。

### 4.4 RUN：唯一执行用户代码的指令（run_step.py:82-176）

先算 recipe hash：`compute_recipe_hash`（build_cache.py:288-314）把 parent_layer_digest、指令名/flags/value/heredocs、外加 RUN 可见的 env+ARG 全景（run_step.py:192-205，含 PD_IMAGE 身份变量）串成 sha256——**父层 digest 入键意味着链式失效**：任何前缀层变，其后全 miss。未禁缓存且命中时，`open_verified_layer` 重哈希后 apply 回放层，**proot 根本不启动**（run_step.py:104-135）；坏 blob 视同 miss 重跑。miss 路径三段式：`snapshot`（layer_diff.py:247-341，指纹 `(size, mtime_ns, mode, crc32)` 四元组，lstat 字段短路、流式 crc32 兜住 touch -r 与亚秒重写；`.l2s/` 整目录跳过）→ `_exec_proot` → 再 snapshot → `diff_snapshots`（layer_diff.py:344-354）分 added/modified/deleted → `write_layer_tar` 打出含 `.wh.` whiteout 的层（layer_diff.py:357-372）→ `publish_file` 以 digest 命名入层缓存 → 记索引。零改动也产空层，维持 history/diff_ids 对齐（run_step.py:151-152）。

`_exec_proot`（run_step.py:228-365）拼 argv 要点：proot 二进制取绝对路径（防镜像 ENV PATH 劫持，run_step.py:231-236）；跨架构时 emulator 参数 + Termux 下绑定 /system 等与 $TERMUX_PREFIX（run_step.py:239-243, 302-311）；`--change-id` 的 uid/gid 由 `resolve_user_for_proot` 对照**容器内** /etc/passwd 解析（users.py:88-103，缺省回 0）；最妙的是 `--rootfs=.`——proot 按名解析 `--rootfs` 太晚（一切检查早已结束），改喂相对路径 + `preexec_fn` 在 fork 后 exec 前 `fchdir` 进钉住的 rootfs 描述符（run_step.py:271-272, 331-337, 368-389），内核从父链回答 getcwd，**proot 拿到的是本构建创建的 inode 而非名字现在的指向**。子进程环境 `_build_child_env`（run_step.py:688-755）按 PATH/HOME → 预定义代理 ARG → 本 stage ARG → ENV 赢 → 身份变量再赢 → PROOT 开关的次序合成。

### 4.5 步骤收尾：subreaper 收割（run_step.py:419-639）

Docker 拆 pid namespace 即可终止一步；proot 没有。三件套：`_become_subreaper`（run_step.py:435-458）经 prctl `PR_SET_CHILD_SUBREAPER`(36) 把孤儿重挂到本进程而非 init——`RUN service x start` daemonize 出的孤儿因此**可被发现**；`_wait_for_step`（run_step.py:519-545）不等 proot 退出而盯 `/proc/<pid>/task/<pid>/children`：proot 唯一子进程是根 tracee，children 空了说明命令本体已结束（proot 的事件循环会陪 tracee 活到天荒地老）；`_stop_step`（run_step.py:605-639）盘点重挂孤儿 + 组员（/proc stat 解析在 `rindex(')')` 之后防 comm 含括号，run_step.py:486-516），先 SIGTERM 给 2 秒宽限（run_step.py:427）再 SIGKILL，每杀带 killpg 防漏一代。收尸刻意逐 pid `waitpid` 而非 `waitpid(-1)`——后者会吃掉 proot 退出状态，失败步骤被报成干净退出（run_step.py:568-582）。

### 4.6 层产出与 OCI 组装（layer_diff.py + oci_writer.py）

`_pack_stream`（layer_diff.py:418-473）是单趟四段流水线 `tarfile → diff_id sha → gzip → digest sha → 文件`：diff_id 是未压缩 tar 的 sha256，digest 是 gzip 后的 sha256（manifest 引用的那个），一趟同时吐出双哈希+字节数，替代旧三遍扫（layer_diff.py:29-37）。RUN 层的 l2s 处理值得记：proot --link2symlink 把硬链接变成指向 `.l2s/` 中间文件的符号链接，直接打包会在别的机器上悬空——`_add_entry` 探测到链后改打包 backing 文件内容为普通文件，层自包含（layer_diff.py:644-672）。收尾在 oci_writer：`build_manifest_and_config`（oci_writer.py:57-105）补上 `architecture/os/rootfs.diff_ids`，canonical_json 哈希出 config digest，组装 schemaVersion 2 manifest；`write_oci_archive`（oci_writer.py:155-228）产标准 OCI layout tar——oci-layout 放首个成员（自家 install 探测第一个成员即判型），**额外写 Docker legacy manifest.json** 兼容 `docker load` 的退化导入路径（oci_writer.py:162-165），层 blob 装包前逐个重验——归档按内容寻址，装进去的必须仍然哈希得出名字。

## 五、设计决策：没有 daemon 的世界里守住正确性

1. **名字不可信，描述符是一等公民**。stage.py:30-44 长注释是全包灵魂：`<scratch>/stage-N/rootfs` 只是个名字，RUN 遗留进程就是本用户，换名留符号链接即可让后续构建读写别处、并把宿主文件封进 `push` 上传的层。对策贯穿始终——Stage 持双描述符（stage.py:81-95）、`_stage_rootfs_fd` 从钉住描述符 reopen（engine.py:201-211）、`--rootfs=.` 相对根、MapSources 让"定位源"与"读源"两次消费都重走 O_NOFOLLOW（layer_diff.py:92-171）。
2. **一个指令一层，file_map 是唯一中间表示**。COPY/ADD/WORKDIR 走 `write_files_layer`，RUN 走 `write_layer_tar`，但层缓存发布、`layers` 记账、history 空层判定三处协议统一；内存零驻留靠 spool。
3. **缓存键含父层 digest 链**。牺牲"只重跑变化步"的粒度换正确性简单；命中后仍重哈希 blob，缓存投毒退化为一次 miss（run_step.py:109-135），与 registry 缓存"消费前重验"纪律同源。
4. **双主人环境字典**。Popen 的 env 既是 proot 的也是 guest 的，LD_*/PROOT_* 在 proot 收容任何东西之前就被 loader 读走；拒绝规则统一收在 execenv，FROM 采纳（engine.py:190-196）、ONBUILD ENV（handlers.py:101-105）、RUN 组 env（run_step.py:642-685）三处应用同一份，且**值仍进镜像 config**——作者对镜像的陈述与宿主侧执行安全分离。
5. **错误归一为 BuildError**（见三节）——新增指令时最内层转译异常是必做的最后一步。

## 六、新人提示

- 先读 `__init__.py:21-32` 十行职责表，再按 engine → handlers → copy_step → run_step 顺序进；各文件 `# Architecture:` 头注释记录了塑造代码的攻击与 bug（本仓硬习惯），stage.py 与 run_step.py 的尤其值得逐句读。
- 改分派只动 HANDLERS 表与 `_dispatch`；新增 metadata 指令照 do_label 的样子写，**别忘了**非空层判定依赖 `stage.layers` 增量（engine.py:442-444）——只改 config 不产层的指令天然记 empty_layer。
- RUN 语义调试看三处：`_build_child_env` 叠加次序、`_wait_for_step` 的 children/adopted 判定、`_stop_step` 宽限期。
- 动 layer_diff 前先分清 diff_id（未压缩）与 digest（gzip 后）；push 的 config 自检（03 篇 4.3）依赖 canonical_json 序列化一致性。
- 测试入口：`tests/integration/` 有零 proot 零网络的 build 端到端（无 RUN 的 Dockerfile），`tests/unit/` 逐模块覆盖 parse_chmod/dockerignore/stage 作用域；全量 `pytest tests/unit tests/integration tests/security`。
