# 04 · fileguard 双管线与 delguard 复合枢纽

> 定位：`tool_permission/fileguard/` 是路径层安全（自称 Pipeline B，与命令级 tool_policy 的 Pipeline A 相对）。核心是**同一判定器、两种编译语义**：Legacy 模式复刻现网 ExternalDirectory 行为（workspace 隐式全放行 + 固定命令清单抽路径），Native 模式是三轴（read/write/exec）+ glob 的完整路径策略。`delguard` 则是一个横跨 toolguard（拆命令）与 fileguard（判定 shell 工具）的复合枢纽，靠**文件系统递归计数**把"批量删除"抬升为 ASK。

## 一、角色定位

模块 docstring 钉死三个事实（`fileguard/file_guard.py:3-9`）：独立于工具级 tool_policy；`file_guard.enabled=false` 时整层路径防护不参与判定；配置编译入口 `normalize_path_guard_config`、判定入口 `FileGuardChecker`。

FileGuardComponent 在 engine 里的发言权很克制：`evaluate` 无意见或全部 ALLOW 时返回 `None`——docstring 明言"不抬升 Pipeline A"（`file_guard.py:725`），路径层只是**加严方**。它还提供 `collect_ask_accesses`（`fileguard/component.py:70-82`，engine 的 `collect_file_guard_ask_accesses` 直接转发，`engine.py:186-197`），供 HITL"总是允许"按 (path, axis) 精确落盘。

DeletionGuard 的定位在 docstring 里写得更直白（`delguard/deletion_guard.py:3-10`）：仅在软删除开关开启时参与；一次 shell 调用删除数达阈值 → ASK `del_guard:batch_delete`；未达阈值/非删除命令/软删除关闭 → None；**解析失败 → fail-open** 返回 None 只告警。它是"旁路增强不阻断主业务"的标准样本：真正的删除拦截靠 toolguard 的 18 条规则，delguard 只负责"数量规模"这一个维度。

## 二、内部结构

### 双模式的判定开关：_has_native_file_guard

Legacy 还是 Native 不由配置显式声明，而由**配置形态推断**（`file_guard.py:187-207`）：

- 显式 `defaults.read/write/exec` 或 `workspace.read/write/exec` → Native；
- `paths` 里有 `match: glob` → Native；
- 只有 `paths` 且**没有**旧 `external_directory` → Native；
- 有 `paths` 但仍有 `external_directory` → **保持 Legacy** 并把 paths 编译进 Legacy 规则（注释：避免误取消 workspace 隐式放行，L192-196）。

这个"形态嗅探"是兼容期的产物：老配置文件不用改一行就能继续跑出老语义，新语法一旦出现自动切新语义。

### Legacy 编译：三段隐式放行

`_normalize_legacy`（L312-403）构造规则表的顺序：1) **workspace 隐式全放行**（三轴全 allow，L338-347，"仅 Legacy"注释钉死）；2) **trusted_dirs**（r/w allow + exec ask，L349-359，运行时 `/add-dir` 热更新）；3) **external_directory 具名键**（allow 键→r/w allow+exec ask，ask/deny 键→三轴同值，L361-373）；4) **file_guard.paths 无 glob 项**并入（L375-394）。

Legacy 抽路径用**固定命令清单**：`_PATH_AWARE_COMMANDS` 24 个命令名（`file_guard.py:47-51`），首 token 不在清单 → 无路径意见；`extract_paths_legacy`（L573-618）对 shell 工具用 `_extract_paths_from_command`（shlex 分词 + `_looks_like_path` 启发，L543-570）；动作轴不分（`_tool_default_action`：写工具 write、其余 read，L621-630）。

### Native 编译：三轴 + glob + 组合源

`_normalize_native`（L406-529）：**defaults 迁移**（未写时从 `external_directory["*"]` 继承，L416-427）；**paths**（每条可指定三轴 + match prefix/glob + layer，L429-464）；**workspace 规则**（路径不写 YAML，由运行时 `workspace_root` 绑定，`_compile_workspace_axis_rule` L210-239——拿不到 root 时 WARN 跳过不瞎猜）；**旧 ext 具名键迁移**（不与已有规则重复时编译并打 WARN，L488-518）。

**read-deny 蕴含**：`_apply_implications` 让 read=deny 蕴含 write/exec=deny（L140-141）；`read_deny_only=true` 关闭蕴含改冲突告警（L128-139）。**前缀过短防误配**：prefix 无 `/` 直接丢弃——防 `"C:"` 误匹配整盘（L167-171）。**组合模式**（`composition.source_order` 存在时，L261-266）：`_resolve_composed`（L868-899）先扫全部源，任一源 DENY 即返回；否则依 source_order 取第一个有命中源（前缀最长+glob 取最严）；组合模式下 trusted_dirs 不在 source_order 里则整体丢弃（L264-266）。

### Native 抽路径：PowerShell 感知

`path_extract.py` 的 native 抽取（源自 enterprise `permissions/files/extract.py`，docstring L3-7）是双管线里"感知力"的差距所在：

- 命令清单从 24 个扩到 34 个，**加入 PowerShell 动词**：`get-content/gc`、`set-content/add-content/out-file/tee-object/sc`、`remove-item/ri`、`new-item/ni`（`path_extract.py:40-47`）；
- **PS 路径旗标**：`-path/-literalpath/-filepath` 后的 token 才是路径（`_PS_PATH_FLAGS` L74，`_collect_ps_path_tokens` L133-152），首个非旗标 positional 也收；
- **读命令裸操作数放宽**：`shell_type in {cmd, powershell}` 且命令在 `_READ_CMDS` 时，无路径形状的 token 也收（L231-232 `bare_read_operand`）——PS 的 `Get-Content file.txt` 不带斜杠也是路径；
- **cmd.exe `/b` 型开关识别跨平台**：Linux 上 `dir /b`（经 `cmd //c`）也把 `/b` 当开关，但 `cat /tmp` 的 `/tmp` 仍是路径（`_nt_cmd_exe_switch_token` L92-108 白名单判定）；
- **cmd /s /c 引号剥除**只在权限视图做一份拷贝（L311-317）；**重定向目标** `>`/`>>` 计 write、`<` 计 read（L344-352），fd 别名（`2>&1`）不算目标（`_FD_ALIAS_RE` L75）；**解释器脚本参数** `python script.py` 第二 token 计 exec（L358-366，`_INTERPRETER_BASENAMES` L49-53）；
- **cd 语义**：cd 目标计 read 且**推进后续段的 cwd**（L262-273 返回 new_cwd，L292-298 段间传递）——`cd /etc && cat passwd` 的 passwd 解析到 /etc/passwd；
- **glob 工具根**：GlobTool 相对路径按 agent_cwd 而非 workspace 解析（L473-486）。

**read_deny_only 专属通道**：该开关打开时抽取切换到 `listed_commands.py`——docstring 明言 "used only when file_guard.read_deny_only is true. Paths come from a fixed list of command names"（L3-7），命令清单缩回 24 个、不剥 launcher 壳（L37, L113）。意图：read_deny_only 场景宁可少抽也不错抽。

### delguard：横跨两线的复合枢纽

DeletionGuard 的依赖图是它"复合枢纽"身份的证据：判定是不是 shell 工具 → import **fileguard** 的 `tool_categories.is_shell_tool`（`deletion_guard.py:18`）；拆命令段 → import **toolguard** 的 `command_canonicalize` + `shell_ast.parse_shell_for_permission`（`del_count.py:27-30`）；计数 → 直接 **os.scandir 递归文件系统**（`del_count.py:230-253`）。

三套删除命令表按 shell 方言分（L33-35）：bash `{rm, unlink}`、cmd `{del, erase, rd, rmdir}`、PowerShell `{remove-item, ri, rm, del, erase, rd, rmdir}`；auto 时三表并集。PowerShell 逗号列表的处理是亮点：`shlex(posix=False)` 会把逗号粘到后一个参数上（`,'b'`），`_peel_shlex_comma`（L108-123）先剥前导逗号、`_split_unquoted_commas`（L126-161）再按**引号外**逗号拆分——`'foo,bar.txt'` 仍是一个路径。计数语义（docstring L8-14）：文件/符号链接计 1（symlink 不追踪指向）、目录不自身计、递归内部、多命令去重累加；glob 操作数直接展开（L215-227）。

阈值 `soft_delete.batch_delete_threshold` 默认 100、0 关闭（`deletion_guard.py:97-111`）；开关缺省 false（L43-48）；`_shell_type_for_delete` 处理 powershell 工具没有 shell_type 参数的特例（L51-56）。DeletionGuardComponent 在 engine 里**不受候选路由影响**（`del route`，`delguard/component.py:44`）——它自己拆段。

## 三、外部连接

- **engine**：FileGuardComponent 与 ImmutableControlPlaneComponent 是 engine 第 6/8 号组件；FileGuard 对 SUBCOMMAND 候选弃权（`fileguard/component.py:91-93`，注释："Native extract already peels launchers and splits compound commands"——native 抽取自己拆，engine 的子命令叶子是重复视图）。
- **config_access**：`runtime_workspace_root`/`runtime_trusted_dirs`/`runtime_immutable_roots`/`runtime_path(config, "cwd")` 是运行时信息的统一取用口（`fileguard/component.py:12-18`）。
- **ImmutableControlPlane**：控制面写保护**独立于 file_guard.enabled**（`fileguard/component.py:99-100`）；没有 workspace 和 cwd 时 ValueError 拒绝构造（L119-123——缺基准时相对写会绕过控制面，fail-loud 而非静默失守）。
- **hostguard**：其删除守卫（pkill jiuwenswarm 模式，`hostguard/safety.py:21-49`）与本篇构成三层删除防线：命令模式（toolguard 18 条）→ 数量规模（delguard）→ 宿主进程名（hostguard 硬编码）。

## 四、数据流

一次 `FileGuardChecker.evaluate(tool_name, tool_args)`（L720-789）：

1. enabled=false → None；glob 工具的 pattern 先做合法性校验（`validated_glob_patterns`），非法直接 DENY `file_guard:glob_pattern`（L728-743）——glob 注入是路径层的注入面；
3. **workspace 为 None → 直接 skip**（L744-747，debug 日志 `skip reason=no_workspace`）——路径防护强依赖基准目录，没有基准宁可不发声（这是 fail-open，但前提是配置层已用 ValueError 挡住 immutable_control_roots 这类必须有基准的场景）；
4. `_listed_accesses` 按 read_deny_only × mode 四象限选抽取器（L689-718）；
5. 逐 (path, action) `_resolve_one`：最长前缀命中（`contains_path` 兼容 Windows 盘符怪癖，L838-844）+ glob 命中累计，candidates 取 `deny > ask > allow` 最严（L846-858）；未命中 → defaults 按轴（L860-866）；
6. 全 ALLOW → None；否则 Legacy 给 `external_directory.*` 老 label，Native 给 `file_guard:prefix:<path>`/`file_guard:glob` 细粒度 label + external_paths 样例（L768-789）。

delguard 侧 `DeletionGuard.evaluate`（`deletion_guard.py:113-156`）：enabled → threshold>0 → is_shell_tool → 取 command/workdir/shell_type → `count_deletion_targets`（try 包裹，异常 fail-open L136-140）→ count≥threshold 时返回 ASK `del_guard:batch_delete`，reason 直接给中文（"本次操作将删除 N 个文件，达到阈值 T，需要确认"，L154）+ external_paths 供审批展示。

## 五、设计决策与权衡

**双管线并存而不是一次性迁移。** Legacy 模式存在的意义是**行为兼容**：现网 ExternalDirectory 的判定被完整保留，迁移期新老配置混跑不改变既有判定。代价是同一文件里两条编译路径、两套抽取器，维护面积近乎翻倍。`report_legacy_path_rules_at_load`（L946-976）的加载期 WARN 是推迁移的软手：不破坏，但每次加载都在日志里提醒。

**Native 抽取"多抽不错抽"与 listed 通道"少抽不错抽"取向相反。** Native 三轴下多抽一个路径最多抬到该路径规则的级别；read_deny_only 误抽会直接 DENY 读操作阻断主业务，宁可缩回固定清单。判据仍是"是否阻断主业务"。

**delguard 为什么 fail-open？** 它是第三道防线（前有 toolguard 模式规则），失灵不等于删除无人管；若 fail-closed，任何让解析器出错的命令都会被打断。旁路组件的失效策略由主防线是否存在决定。

**删除计数为什么同步做（evaluate 内递归 scandir）？** 大目录递归计数可能上万 entry，设计者接受这个成本：只有删除命令才触发；阈值 100 意味着多数场景几百 entry 内；换异步/缓存会引入"计数与实际删除的竞态"。

**`_match_glob` 手写而非 fnmatch。** `**/` 跨目录、`*` 不跨 `/`（L633-657）——语义贴近 gitignore 而非 shell glob，fnmatch 会把 `*` 放宽成跨斜杠，误配面变大。

## 六、新人提示与坑

1. **Legacy/Native 是"编译产物形态"而非配置开关**。排查"为什么 file_guard.paths 没生效/生效得不对"第一步永远是 `_has_native_file_guard`（L187-207）五条判定走一遍——尤其"有 paths 但还残留 external_directory → 强制 Legacy"最反直觉。
2. **workspace_root 为 None 时 FileGuard 整体静默**（L744-747）。单测里忘传 workspace 会得到"全 None"的假绿——断言前先确认 checker 真的 active。
3. **Legacy 的 workspace 全放行是隐式的**（L338-347），Native 没有这条——同一个"workspace 内任意写"需求，Legacy 下默认满足，Native 下要显式写 `workspace: {write: allow}`。迁移配置时最容易踩的语义差。
4. **`read=deny` 默认蕴含三轴全 deny**（L140-141）：想"只禁读但允许写"必须显式 `read_deny_only: true`，且要接受组合模式/冲突告警语义（L128-139）。
5. **delguard 默认整条关闭**（`soft_delete.enabled` 缺省 false）：没开软删除的部署里 DeletionGuardComponent `active()` 为 False，测试批量删除审批前先确认配置。
6. **PowerShell 逗号列表的处理链**（剥前导逗号→引号外拆分→旗标过滤）改动一处全链回归：`del_count.py:108-187` 四个函数是一条流水线，单测在 `tests/test_deletion_guard.py`。
7. **`external_paths` 字段的意义**：delguard 与 fileguard 都往里放"触达的绝对路径"，engine 合并时全量拼接（第 01 篇）——HITL 审批 UI 直接消费这个字段展示"将影响哪些路径"，别在组件里省略。
