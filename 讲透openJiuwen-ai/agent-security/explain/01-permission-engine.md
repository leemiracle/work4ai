# 01 · PermissionEngine：九组件聚合与原子换装

> 定位：`agent_shield/tool_permission/engine.py` 是整个 agent_shield 权限体系唯一的应用层入口。它不实现任何具体的安全判定逻辑，而是**拥有全部九个安全组件的生命周期**，把一次工具调用展开成候选视图、分发给组件投票、按最严原则合并裁决。理解了这一篇，后面五篇（import 守卫、toolguard、fileguard、netguard、detection）才有坐标系。

## 一、角色定位

`PermissionEngine` 的类 docstring 一句话讲清了自己的边界："Own component lifecycle and aggregate security decisions"（`agent_shield/tool_permission/engine.py:64`）——拥有组件生命周期、聚合安全决策。组件的构造是私有的，应用只通过这个 facade 获得三类能力：执行决策（`check_permission`）、裸策略查询（`evaluate_global_policy_directly` / `evaluate_component`）与原子配置更新（`update_config`）。

它之上有 `PermissionManager`（`agent_shield/tool_permission/manager.py:26`）维护 `key -> PermissionEngine` 表——每 key 一份完整配置、进程级单例、default key 永在且不可删。引擎之下是九个 `PermissionComponent`。这个三层结构（Manager → Engine → Component）是典型的"每层只管一件事"：Manager 管多租户配置表，Engine 管单份配置下的决策编排，Component 管单一安全域的判定。

值得先钉一个本仓的分区判据（后面各篇反复引用）：**fail-open vs fail-closed 的三层分区**。第一层，引擎总开关：`enabled=False` 时 `check_permission` 直接返回 ALLOW（`engine.py:129-133`），这是"安全系统整体被关掉"的 fail-open，属于部署者主权；第二层，组件聚合：所有组件都无意见（返回 `None`）时合并结果落 ASK "No permission component is configured"（`engine.py:439-443`），这是"没人做决定 ≠ 允许"的 fail-closed；第三层，组件内部各自决定，例如 TieredPolicy 对 shell 命令无配置时落 ASK、非 shell 工具返回 None 弃权（`toolguard/tiered.py:393-395`），DeletionGuard 计数失败 fail-open 返回 None（`delguard/deletion_guard.py:9`）。判据就是**"该决定是否直接阻断主业务"**：阻断路径上默认从严（ASK/DENY），旁路增强路径上默认从宽（None 弃权、告警兜底）。

## 二、内部结构

### 九组件固定序列

`_build_components()` 返回一个不可变 tuple，顺序是硬编码的（`engine.py:80-95`）：

1. `InjectionComponent` —— shell 注入语法（反引号/`$()`/进程替换/PowerShell iex）直接 DENY（`toolguard/injection.py:24-37`）
2. `CommandAllowlistComponent` —— 首 token 命令白名单，命中 ALLOW / 未命中 DENY（`toolguard/command_allowlist.py:73-88`）
3. `DestructiveWarningComponent` —— 只挂 warning 不改权限（`toolguard/destructive_warning.py:108-142`）
4. `TieredPolicyComponent` —— 五级裁决链主力和 approval 短路（详见第 03 篇）
5. `HostGuardComponent` —— 宿主可用性守卫，硬编码保护 jiuwenswarm/jiuwenclaw 进程（`hostguard/safety.py:21-49`）
6. `FileGuardComponent` —— 路径层防护 Pipeline B（详见第 04 篇）
7. `DeletionGuardComponent` —— 批量删除数量守卫（详见第 04 篇）
8. `ImmutableControlPlaneComponent` —— 控制面写保护，独立于 file_guard.enabled（`fileguard/component.py:99-100`）
9. `NetGuardComponent` —— 网络工具基线 + URL/地址策略（详见第 05 篇）

注意这个顺序**不是优先级**——合并取最严，顺序只影响日志里谁先出现。真正的优先级机制是 approval 短路（见下文数据流）。

### 候选展开：RouteContext 与三种视图

引擎把一次调用展开成至多三类候选（`engine.py:215-273`）：

- `ORIGINAL`：原始 command；
- `UNWRAPPED`：剥掉一层 launcher（`bash -c '…'`/`cmd /c`/`powershell -Command`，见 `toolguard/command_canonicalize.py:69-95`）后的视图，仅当剥壳结果与原文不同才追加；
- `SUBCOMMAND`：对 POSIX/UNKNOWN 方言用 bash AST 拆出的每个子命令（`engine.py:253-272`；方言判定在 `routing.py:120-127`，PowerShell/CMD 暂不拆分）。

单叶子与整体相同时不追加（`engine.py:259-261` 注释 "a single leaf identical to the whole view is redundant"）。每个候选携带 `RouteContext(kind, command_dialect, is_shell)`（`routing.py:37-43`），组件据此自行决定"这个视图我要不要管"——引擎不做订阅过滤（`routing.py:193-197` 的 `route_matches` 已退化为恒 True，老 API 保留只为兼容）。

### 组件协议：新旧两代签名共存

`_evaluate_component` 用 `inspect.signature` 探测组件的 `evaluate` 是否接受 `route` 关键字（`engine.py:401-408`），接受则传三代签名、否则回落两代签名。这是"路由改造不强制迁移所有组件"的兼容层。

### 组件名单注册表只有三个名字

`_COMPONENT_BY_NAME` 只注册了 `host_guard`/`file_guard`/`deletion_guard`（`engine.py:36-40`）——`evaluate_component` 隔离 API 与 `component_active` 只对这三个名字开放，因为宿主（jiuwenswarm）确实只需要单独询问这三个域。`_named_component` 对未注册名抛 `ValueError`、对未安装抛 `RuntimeError`（`engine.py:199-206`）。

## 三、外部连接

- **上游**：`PermissionManager` 持有引擎表（`manager.py:49-51` 构造时即建 default 引擎）；宿主 jiuwenswarm/jiuwenbox 通过 `agent_shield.tool_permission` facade 拿 `PermissionEngine`（facade 纪律见第 02 篇）。
- **下游**：九个组件及其各自的私有模块树。引擎是它们唯一的聚合点；组件之间不互相调用（唯一例外：DeletionGuard 跨层复用 fileguard 的 `tool_categories.is_shell_tool`，见第 04 篇）。
- **配置来源**：`configure(config)` 收到的整份引擎配置 dict 会原样（deepcopy 后）下发给每个组件，组件各自认领自己的段（`file_guard`/`net_guard`/`soft_delete`/`tools`/`rules`/`shell_allowlist`…），组件间不共享解析结果。
- **日志**：决策日志走 `permission.engine.decision` 单行结构（见数据流），`label` 参数只用于标记这条日志属于哪个配置 key（`engine.py:70-71`）。

## 四、数据流

一次 `check_permission(tool_name, tool_args)` 的完整链路：

1. **校验**：`_validate_call` 要求 tool_name 非空字符串、tool_args 是 Mapping（`engine.py:208-213`）。
2. **总开关**：`enabled=False` 直接 ALLOW（`engine.py:129-133`）。
3. **候选展开**：`build_candidates` 产出 ORIGINAL（+UNWRAPPED）（+SUBCOMMAND×N）。
4. **整调用 approval 短路**：ORIGINAL/UNWRAPPED 任一命中 approval override 即刻返回该 ALLOW 结果，不再问任何组件（`engine.py:286-299`）。这是用户"已批准过这条命令"的加速路径。
5. **逐候选投票**：SUBCOMMAND 候选先单独查 approval，命中则以该候选结果（ALLOW 为最高级）计入，跳过组件轮询（`engine.py:307-316`）；否则九个组件依次 `evaluate`，异常直接 `logger.exception` 后 **re-raise**（`engine.py:325-333`）——组件崩溃不允许被吞掉，由上层决定 fail 策略。
6. **两级合并**：候选内合并组件结果（过滤 None）→ 跨候选再合并（`engine.py:337-340`）。`_merge_results` 取 `permission` 非 None 的结果按 `_permission_rank` 取 max（ALLOW=0 < UNDETERMINED=1 < ASK=2 < DENY=3，`engine.py:467-477`），即**最严者胜**；`warnings` 与 `external_paths` 则跨结果全量拼接（`engine.py:452-453`）；`matched_rule/reason` 取胜者。空列表合并落 ASK（前文 fail-closed 层）。
7. **日志**：`_log_decision` 每次决策一行：谁被问了（components= 名单）、各自结论（含 matched_rule）、谁赢了（winner 取第一个与合并结果 permission+matched_rule 双等的组件，`engine.py:364-373`）。**tool_args 刻意不落日志**——"they may carry secrets"（`engine.py:355-357`）。

一个容易忽略的细节：`evaluate_global_policy_directly` 跑同样的 `_evaluate`，但**不受 enabled 开关短路**（`engine.py:136-149`）——供宿主在系统关闭时仍能查询"如果开着会怎么判"。而 `evaluate_component` 是隔离 API：只跑指定组件、只喂 ORIGINAL 候选、其他组件无权投票（`engine.py:151-175`）。它的实现用了一个小技巧——`outcome.send(None)` 驱动 generator、捕获 `StopIteration.value` 拿返回值（`engine.py:170-175`），这是把 async 函数当 coroutine 手动驱动以支持 close 语义的写法。

### 原子换装：_install

`_install` 是配置更新的核心（`engine.py:97-119`）：

```python
snapshot = copy.deepcopy(dict(config))   # 1) 深拷贝，配置从此与调用方解耦
components = self._build_components()     # 2) 全新组件集
for component in components:
    component.configure(snapshot)          # 3) 全部配置成功才继续
self._components = components              # 4) 一次性换入
```

第 3 步任何组件 `configure` 抛异常，第 4 步不会执行——**旧组件集与旧配置完整在位**。而且组件 tuple 是不可变的，已经在跑的调用持有的旧 tuple 不受影响（docstring："Calls already running keep the component tuple they started with"，`engine.py:101-103`）。`update_config` 只是 `_install` 的带类型校验包装（`engine.py:410-415`）。`config` property 返回的是内部 snapshot 的引用（read-only view 语义靠约定而非 MappingProxyType，`engine.py:417-421`）。

## 五、设计决策与权衡

**为什么组件顺序硬编码而不是可配置？** 安全组件的组合顺序如果暴露为配置，就多了一条"通过配置削弱防线"的攻击面。九组件固定序列让审计者只需读一处代码。

**为什么合并取最严而不是加权？** 多组件意见冲突时（FileGuard 说 ALLOW、NetGuard 说 ASK），加权/优先级都需要人工维护权重表且难以解释。max-by-strictness 的语义是"任何一个安全域有异议，就按有异议办"，可解释性最强。代价是组件误报会全局放大——所以本仓给旁路组件（DestructiveWarning、DeletionGuard）的返回形态刻意设计成"只挂 warning / 只在阈值处才 ASK"。

**UNDETERMINED 的位置为什么比 ALLOW 严、比 ASK 松？**（`models.py:12-18` 定义四级，rank 表 `engine.py:471-476`）它表达"这个组件无法判定"——不该像 ALLOW 一样信任（否则一个弃权组件会稀释其他组件的 ASK），也不该像 ASK 一样打断用户（否则弃权等于问询）。目前主链路组件实际很少返回它，更多是留给扩展位。

**approval 短路为什么绕过所有组件？** 用户对某条命令的显式批准是最强的授权信号，若仍走九组件轮询，任何一个组件的 ASK 都会把已批准的命令再次打断，HITL 体验崩坏。风险由 approval_overrides 自身的匹配严格性承担（`tiered.py:398-411`，只认显式 `action=allow`）。

**为什么组件异常 re-raise 而不是吞掉降级？** 这是最严的一层：权限引擎内部的意外错误直接抛给宿主，由宿主决定"这次调用要不要放行"。相比在引擎里静默 fail-open（吞异常返回 ASK）或 fail-closed（吞异常返回 DENY），显式抛出让故障可见且策略归位到宿主层。

## 六、新人提示与坑

1. **"九组件"是 `engine.py:84-94` 的硬清单**，别数错：Injection、CommandAllowlist、DestructiveWarning、TieredPolicy、HostGuard、FileGuard、DeletionGuard、ImmutableControlPlane、NetGuard。`_COMPONENT_BY_NAME` 只有 3 个名字，不代表引擎里只有 3 个组件。
2. **改配置不会部分生效**：`update_config` 要么全量成功要么完全不动。测试配置合法性时不要期待"坏配置里好的那半生效"。
3. **候选展开只剥一层壳、只对 POSIX/UNKNOWN 拆子命令**：`bash -c "bash -c 'rm'"` 只得到一个 UNWRAPPED 视图，不会递归剥两层（`command_canonicalize.py:69-95` 一次 `subn(count=1)`）；PowerShell/CMD 方言没有 SUBCOMMAND 候选（`routing.py:120-127` Phase-1 注释）。
4. **日志里找不到命令参数是特性不是缺陷**：`_log_decision` 有意不记 args（`engine.py:355-357`）。排障时靠 matched_rule 的 pattern 名对回规则表，而不是去日志里翻命令。
5. **`check_permission` 与 `evaluate_global_policy_directly` 的唯一区别是 enabled 短路**。给禁用态系统写"预演"功能时用后者；但别用它做执行裁决——它绕过总开关。
6. **合并结果的 `matched_rule` 只属于胜者**，`warnings/external_paths` 是全体累计。断言测试时别把 warning 的来源误当 permission 的来源。
7. **manager 层的坑**：`PermissionManager` 对未注册 key 的决策抛 KeyError 且**不回落 default**（`manager.py:60-64`）——多租户场景忘了注册 key 会直接炸，这是有意的（fail-loud 而非静默用错配置）。
