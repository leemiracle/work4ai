# 09 · 读屏主链路——采集、视图与协调（read/pipeline + views + acquisition + app.py）

## 一、角色定位

读屏是整个系统里被模型消费频率最高的路径。四个文件构成主链路的三层：

- `computer_use_engine/interaction/read/pipeline.py`（191 行）：**读调用骨架**。`ApplicationObservationPipeline` 把一次 read 变成"解析请求→认领调用预算→准备作用域→菜单/窗口分支→观测"的固定形状；docstring（L4-7）钉死职责边界："AppReadPreparationPipeline only returns its selected scope. This parent owns continuation to menu or window observation, never the preparation child."（准备子管线只交还 scope，续跑归父层）。
- `computer_use_engine/interaction/read/views/pipeline.py`（380 行）：**V6 读视图**。docstring（L4）"fixed instance scope -> bounded members -> one public observation"——固定实例作用域→有界成员集→单一公开观察。`InterfaceReadPipeline` 是 SDK 句柄 `ui.read()` 的直接后端。
- `computer_use_engine/interaction/read/acquisition/pipeline.py`（346 行）：**有界采集循环**。docstring（L4）立宪："A fixed-window read is a bounded acquisition loop, never an input retry."（固定窗口读取是有界采集循环，绝非输入重试）。
- `computer_use_engine/interaction/read/app.py`（622 行）：`NativeAppReader` 服务协调者——装配 directory/reader/images/overviews/menus 五个采集服务，并兜住作用域选择/启动目录/启动回执注解等横切逻辑；docstring（L7-8）："Native operations collect facts; they neither select a new working window nor combine an old tree with a newly discovered dialog on behalf of Python."

## 二、内部结构

**read/pipeline.py 三层组装**
- `WindowObservationPipeline`（L45-70）：窗口观测三段式 `Sequence[AcquisitionPipeline(services), NumberedPresentationPipeline(services), AppDeliveryPipeline(services)]`（L63-69）——采集→编号→交付，正是 tour S11 说的"采集→编号呈现→交付"三段。
- `_ReadCallBody`（L73-144）：内嵌 `MenuReadBranch`（L106-124，`_run` 直接 `TypeError("Menu reads require arun()")`）与 `Select(name="ObservedReadBranch", branches={True: menu, False: Sequence[plan_read_components(), WindowObservationPipeline]})`（L126-136）——菜单/窗口二分支按 `select_read_components` 的布尔键分派。
- `ApplicationObservationPipeline`（L147-191）：`Sequence[parse_read_request(), Scope(CallScope, using=claim, body=_ReadCallBody)]`（L169-175）；`claim` 是 asynccontextmanager（L164-167），从 `port.calls.claim(request.timeout_ms)` 领剩余预算造 `ReadCall`；`_arun`（L178-188）持 `_StartupReceipt`，`BaseException` 时若 `receipt.launch` 非空则用 `_after_launch` 注解后重抛——**启动回执跨失败冻结**（类 docstring L151-153："so the caller can distinguish startup from observation"）。

**views/pipeline.py——单一公开观察**
- `WindowPart`（L47-65）：一个成员窗口的全部采集物（target/tree/image/menus/gaps/source）。
- `remember`（L73-101）：观测落地——`state.query_target/query_scope_kind="window"`（L87-88），**`state.selection/state.observation = None`**（L91，注释 L89-91："an old current-modal observation must not retarget a fixed member during a semantic lookup"——旧模态观察不得在语义查找时重定向固定成员）；refs 打上 `window_identity`（L95-97）；L98-101 注释：显式有界窗口读即便 AX 与像素全失败也算"观测过身份"。
- `InterfaceReadPipeline.run`（L120-344）主循环：`resolve` 后按 `instance.anchor` 是否为空走两大分支。无 anchor（App 未选实例）：`matches_view` 要求目录完整+`nativeApplicationRoots` 能力（L134-145）才直进菜单管线，否则发布实例选择目录（L150-169，提示语"Select an application instance with computer.app(id)"）。有 anchor：`ordered[:6]` 有界循环（L187）——principal 排首位（L177-181），首位成员限额 `max_nodes=1000` 其余 `200`（L241）；index==0 且无 `_anchor` 时**复用准备阶段的 AppObservation**（`first`，L198-203）省一次双读；对话框消失保护（L231-240，注释："A dialog can disappear during the principal read. Its captured surface must not be relabelled as a new member"）；未捕获成员在 `len(parts) < 6` 内补收（L244-250）；未展开窗口生成提示行（L261-263："Window {0}: not expanded (read budget); use app.window({0}).read()."）。
- 渲染段（L264-332）：目录行、Launch 行、组合截图（`InterfaceImagePipeline`，L269-273）、每窗标题/`context_notes`/`Blocked by`（modal 祖先链，L290-294）/树文档（`PrepareSnapshotPipeline` compact 渲染，L310-311）/菜单树（`remember_menu` 并把 owners 追加进 `_lookup_scopes`，L316-317）/gap 行（L322-324）。
- `member`（L346-376）：单成员采集——tree 走 `collect_component(port, "tree", ...)`（L361-365）+ `number_snapshots`（L369），image 走 `controller.reader.images.window`（L371-373），失败一律转 `ObservationGap` 保留在观察里而不是丢异常。

**acquisition/pipeline.py——有界循环**
- `_CollectComponents`（L64-118）：普通模式采集 tree+image；**refresh 模式**（L92-115）只刷树——刷新成功清 tree/view gap，失败保留旧树并追加 gap"The content refresh failed; the earlier tree and its capture interval are retained."，`image_precedes_tree` 记录采集次序。
- `_AppMenuCollection`（L121-167）：view=image 或无 `nativeApplicationRoots` 能力即跳过（L148-152）；否则在 `context=selection.root` 下收菜单摘要。
- 两个成品管线：`FullCollectionPipeline`（L170-196，Sequence[collect, menus, window_overview]）与 `TreeRefreshPipeline`（L199-215）。
- `AcquisitionPipeline.build`（L234-340）：`discover`（L237-278）解析 surface，`ambiguous_target/observation_incomplete` 时转 `_window_choices`（抛 `WindowSelectionRequired` 让模型选窗）；`recheck`（L280-308）采集后**重查目录**并对账（`_complete_scope` + surface 重选 + `window_binding` 相等则更新 target）；中段 `Select[collect Full/TreeRefresh]` + `Select[wait KEEP/SCOPE/IMAGE/TREE 四分支]`（L310-324）；顶层 `Sequence[SelectObservedScope, Repeat(ReadRefreshLoop, gate=read_refresh_gate, max_iterations=2)]`（L334-339）。

**app.py——服务协调**
- 构造（L147-155）：五个采集服务一次装配；`number_snapshots`（L157-174）的编号分配器跨读保留、driver session 变更才重建（docstring："The allocator is retained across reads and renewed when the driver session changes"）——编号稳定性是模型跨轮引用的基础。
- `window_summary_content`（L89-124）：窗口目录的 flag 词汇（root/current/observed/reported focus/modal/native window unmatched/parent=…）。
- `_selection`（L358-397）：固定根窗缺失时区分 `FixedWindowUnconfirmed`（目录不完整）与 `FixedWindowInvalidated`（完整目录中消失/身份变更，L383-396）。
- `_after_launch`（L399-441）：把启动回执缝进后续失败——非 Exception（如 CancelledError）走 `add_note`（L409-412）；`launch.dispatch != NOT_DISPATCHED 且 effect==none → possible`（L413-415，启动可能已派发，效应不许被后续观察失败抹掉）；`WindowSelectionRequired` 特殊重包保留选择目录（L431-440）。
- `_complete_scope`（L452-469）：目录完整性=无 stopReasons+parent 全 known+父链可达无环；注释 L459："A partial catalogue cannot prove that an old modal disappeared."

## 三、外部连接

- 上游：`AgentInterfacePipeline.read`（03 篇 agent/pipeline.py:165-176）→ `InterfaceReadPipeline.run`；`NativeAppReader.read`（app.py:186-233）→ `ApplicationObservationPipeline`。`controller.reader` 即 `NativeAppReader`（controller.py:73）。
- 下游：acquisition 的组件管线经 `controller.port` 进 native 层（04 篇）；编号后的树交 `PrepareSnapshotPipeline`（presentation 域，11 篇）压缩渲染；`publish`（views/publication.py）落 `session/observation` 状态。
- 横切：`FixedWindowInvalidated/Unconfirmed` 上抛后被 03 篇 `AgentInterfacePipeline.read` 的 except 捕获做 `retain_fixed_failure`；`WindowSelectionRequired` 是"错误也是观察"的载体（带目录与预览）。

## 四、数据流

一次 `ui.read(view="both")`：

1. `run` → `resolve`（目录+可能的准备产物 `first`）→ 有 anchor 走成员循环：principal 复用 `first`（或补读）→ `adopt` 对账目录 → `WindowPart(source=observed)` → `remember` 落地绑定；其余成员走 `member()`（tree+image+gaps）。
2. 成员内部即 `AcquisitionPipeline`：`discover` 选 surface → `Repeat(max_iterations=2)`：`collect`（Full 或 TreeRefresh）→ `recheck` 重查目录 → `classify_read_attempt` 分类 → `wait` 四分支 Gate（KEEP 完成/SCOPE 换作用域重采/IMAGE 等几何稳定/TREE 等内容变化）——两次迭代内不收敛就以现有 gap 收尾。
3. 回到视图层：`InterfaceImagePipeline` 拼合成 `ui._image`+screenshot；逐窗渲染树文档/菜单/blocker/gap；`publish` 打包 `Observation`（带 `trees` 元组供 diff 交付）。

## 五、设计决策与权衡

1. **有界性三连**：窗口数 `[:6]`、节点数 `1000/200` 分级、刷新循环 `max_iterations=2`——模型永远拿到"部分但有标注"的世界（"not expanded (read budget)"行、`ObservationGap` 四元组），而不是要么全量要么超时。gap 行格式 `"{component}: {code}: {detail}; next: {next}"`（views/pipeline.py:323）把恢复指引嵌进观察文本本身。
2. **采集循环≠输入重试**：acquisition 的 `Repeat` 只服务"窗口内容还在变"的场景（Gate 四分支里有三种 wait），与写路径的重试语义（StepResult.retry_reason 白名单）完全隔离；这防止了"读到一半内容变化→当作失败→无限重采"。
3. **principal 复用**：准备阶段已经采过一次 AppObservation（`first`），视图层 index==0 直接转 `WindowPart`（L198-227）——同一次调用内绝不双读主窗口；`adopt` 把它的目录当作对账基准。
4. **launch 回执的不可变性**：`_StartupReceipt` 是失败调用中唯一可变物（pipeline.py:162-163 注释），`_after_launch` 保证"应用确实启动了但观察失败"不会被误读为"启动失败"——`effect` 语义在此处手动升级（none→possible）而不是丢失。
5. **remember 的遗忘也是设计**：`state.selection/state.observation = None`（views/pipeline.py:91）——新的窗口观察主动作废旧模态上下文，防止过期 observation 在语义查找时"复活"。
6. **编号跨读稳定**：`DisplayReferences` 按 driver session 生命周期持有（app.py:171-174），同一会话内元素编号可跨轮对话复用，模型引用不失效。

## 六、新人提示与坑

- **"view" 三态贯穿全链**：`tree/image/both`（+desktop 的 `tree` 特殊目录视图）；`view != "tree"`/`view != "image"` 的补集判断遍布三个文件，改分支时先列真值表再动手。
- **`first` 的类型是联合**：`AppObservation | MenuAppObservation | dict`——L159 的 `isinstance(first, dict) and "detail" in first` 在取 Launch 详情，别当普通 dict 用。
- **principal_error 不中断读**：主窗口无法唯一定位时整个 read 照常完成，只是附注"Current input window is not uniquely confirmed"（L254-256）并清 `_context`——写侧会因 scope 不明拒绝输入，读侧永远给信息。
- **`_lookup_scopes` 是累加的**（L317 `+=`）：菜单 owners 进入查找范围；但循环开头 L184 清空重来——顺序敏感，若把菜单采集挪到循环外会破坏作用域重置。
- **`remember` 在 parts 收集时就逐个调用**（L227/243/249），不是收完批量——中途抛异常时已 remember 的成员保持有效，这是有意的不成文约定。
- **两个连续 `if TYPE_CHECKING:` 块**又出现在 acquisition/pipeline.py:343-346——本仓增量开发的普遍痕迹，无运行时语义。
