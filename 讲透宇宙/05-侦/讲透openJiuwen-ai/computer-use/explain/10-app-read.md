# 10 · 应用读取、编号与投递——app_read / numbering / delivery

## 一、角色定位

这三个文件回答读屏链条的三个"最后问题"：

- `computer_use_engine/interaction/read/app_read/pipeline.py`（353 行）：**"这次读到底读哪个应用、哪个窗口"**。`AppReadPreparationPipeline` 用三种身份源（固定工作根/进行中的启动/目录证据）解析选择，并在需要时**在读取调用内派发一次 launch 写入**。docstring（L5-7）立宪："Launching is a write branch before ReadPipeline. A failed observation never retargets a previously fixed working root or silently repeats startup input."（启动是 ReadPipeline 之前的写分支；失败的观察绝不重定向已固定的工作根、绝不静默重复启动输入）。
- `computer_use_engine/interaction/read/numbering/pipeline.py`（139 行）+ `numbering/observation/pipeline.py`：**"快照里的元素叫几号"**。docstring（L4-7）："Stable session numbers, allocated in the existing interleaved display order. Each part is previewed then assigned before the next preview. A later display failure must not undo alias touches already made for earlier parts."——会话级稳定编号，按展示顺序交错分配，部分失败不回滚。
- `computer_use_engine/interaction/read/delivery/pipeline.py`（98 行）+ `delivery/diff/pipeline.py`：**"最终交付物长什么样"**。`AppDeliveryPipeline` 把编号后的采集物组装成 `AppObservation`；`DeliverySelectionPipeline` 决定全文还是差分文本。

这一层决定模型最终看到的"世界快照"的**身份、编号与形态**。

## 二、内部结构

**app_read/pipeline.py——身份解析与启动协调**
- `DirectorySelectionPipeline`（L65-149）：目录身份源。`Scope(DirectorySelectionScope, using=lease)` 里 `lease` 认领 native operation（L83-86）；`resolve`（L88-108）三分支——selector 已是 `RunningApplication` 时直接校验 session（L92-95，跨 driver session 即 `stale_target`"belongs to a previous driver session"）；否则 `directory.collect(kind="applications")` + `select_application` + `selected_window`（窗口选择器冲突 L101-105："A window selector cannot select a different working window."）；`surfaces`（L110-124）仅 `isRunning` 才采集，`accessibility=view != "image"` 按能力协商。
- `_LaunchDispatch`（L152-190）：**读路径中的写入**。延迟 import `WritePipeline`（L170-172），动态把 `(pipeline.intent, pipeline.main)` 挂进诊断 children（L173，finally 清空 L186-187）；`run_in_call(Intent("launch"), ApplicationBinding(...), remaining)`（L175-180）在读取预算内跑写入管线；回执**双MappingProxyType 冻结**（L181-183）；`dispatch == DISPATCHED` 才保留 installation 身份（L184-185）。
- `LaunchCoordinator`（L193-240）：`Sequence[validate_explicit_startup, _LaunchDispatch, remember_starting_scope, ObserveStartedApplication]`——校验→派发→记住启动作用域→等启动目录。
- `AppReadPreparationPipeline`（L243-349）顶层组装：`identity = Select`（L321-333）三分支 `"fixed"`（固定工作根 `_discover`，view=image 时不请求 accessibility L262-275）`"starting"`（StartingApplication selector 观察**已存在的启动** L277-289）`"directory"`（DirectorySelectionPipeline）；`startup = Select`（L334-338）True→LaunchCoordinator / False→retain_running_application；`choose`（L291-319）：`WorkingWindow` 直接通过；`_selection` 失败且 `window is None` 且目录有 surfaces 且错误码是 `ambiguous_target/observation_incomplete` 时转 `_window_choices`（把选择权交还模型）；无 surfaces 但指定了 window 则 `stale_target`（L317-318）。收尾 `Sequence[identity, startup, SelectWorkingScope, bind_read_scope]`（L339-349）。

**numbering——可视序编号**
- `_PreviewSnapshot`（numbering/pipeline.py:51-73）：对每份快照先跑 `PrepareSnapshotPipeline(compact=True)` 拿投影——类 docstring L52-55："Number allocation follows its visible pre-order references."（编号分配跟随**可见的先序引用**——模型看到什么顺序，编号就是什么顺序）。
- `_PreviewAndAssign`（L76-99）：逐快照 `Sequence[PreviewSnapshot, assign_preview_references]`——"Each part is previewed then assigned before the next preview"（先序交错）。
- `NumberSnapshotsPipeline`（L102-129）：空集短路（L117-118）；主体 `Sequence[bind_numbering_session, PreviewAndAssignParts, assign_unrendered_references, rewrite_structured_refs]`（L119-127）——先绑会话分配器，再按可见序分配，再补未渲染对象，最后把结构化引用重写进快照。
- `number_snapshots` 顶层函数（L132-139）："Number one result's parts without merging their native binding scopes."（编号不合并各部分的 native 绑定作用域）。
- `numbering/observation/pipeline.py:34-61` 的 `NumberedPresentationPipeline`（三段式中间段，09 篇）：`Sequence[account_acquisition_gaps, _NumberObservedSnapshots, annotate_busy_content, _PrepareSelectedSnapshot]`；`_NumberObservedSnapshots`（L64-78）把窗口树+菜单源树放进**同一条共享编号序列**（"window tree followed by the menu source trees"，RESOURCE effect）。

**delivery——组装与差分**
- `AppDeliveryPipeline`（delivery/pipeline.py:72-98）：四步 `Sequence[assemble_observation_header, _PrepareAppMenus, append_window_overview, assemble_observation]`。`_PrepareAppMenus`（L32-69）把菜单源渲染成文档追加（标题行"Application menu (separate from the working window):"L64），并把菜单 refs 以 `replace(part.target, node=node)` 合并进 draft.refs（L57-59）——**菜单元素与窗口元素共享同一编号空间但绑定各自 target**。
- `DeliverySelectionPipeline`（delivery/diff/pipeline.py:55-76）：`Sequence[Select(ChooseDeliveryPlan, True:plan_full_delivery / False:plan_observation_diff), _RenderPlannedDelivery]`——按请求与兼容的先前 baseline 选全文或上下文树差分；`_RenderPlannedDelivery`（L31-52）对 `DisplayDocument` 走共享终态渲染（`DocumentRenderingPipeline`），否则直接取 `observation["state"]["text"]`。

## 三、外部连接

- 上游：09 篇 `ApplicationObservationPipeline` 的 `AppReadPreparationPipeline` 即本篇身份解析；`WindowObservationPipeline` 的 `NumberedPresentationPipeline/AppDeliveryPipeline` 是本篇后两段。
- 下游：`_LaunchDispatch` 延迟 import 的 `WritePipeline`（11 篇写管线）——**读域对写域的唯一入口**；`PrepareSnapshotPipeline/DocumentRenderingPipeline`（presentation 域，11 篇压缩）被编号与差分两侧复用。
- 状态侧：`bind_read_scope/remember_running_scope/remember_starting_scope` 写 `session` 状态（RunningApplication/WorkingWindow/StartingApplication 三态作用域，native/scopes.py）；编号分配器 `DisplayReferences` 由 `NativeAppReader` 持有跨读复用（app.py:157-174）。

## 四、数据流

一次带启动的读：`computer.app("id").read()` → `DirectorySelectionPipeline` 发现应用未运行 → `select_explicit_startup` 判 True → `validate_explicit_startup` 校验 → `_LaunchDispatch` 内嵌写管线派发 launch → 回执冻结进 `call.receipt.launch` → `remember_starting_scope` 记 StartingApplication → `_startup_directory` 等运行目录 → `choose` 选定工作根 → `bind_read_scope` 定绑。随后采集（09 篇）返回的快照进编号：逐份 preview→assign（可见序）→未渲染对象补号→结构化引用重写；最后 delivery 四步拼出 `AppObservation`。**任何后续失败**都会带着冻结的 launch 回执（09 篇 `_after_launch`），模型能区分"启动失败"与"启动成功但观察失败"。

## 五、设计决策与权衡

1. **启动是读前置的写分支，但有独立回执语义**：launch 在读调用预算内执行（`run_in_call`），但 receipt 与观察分离冻结（L181-185）——写入的 `dispatch` 状态不被后续读失败污染（对照 09 篇 `_after_launch` 的 effect 升级逻辑）。
2. **身份三源显式分派**：fixed/starting/directory 三分支把"作用域从哪来"变成可诊断的选择（Select 的 branch 事件留痕），而非散落的 if-else；`StartingApplication` 作为一等身份使**正在进行中的启动**可被后续读续接而不重复启动。
3. **编号按可见序而非树序**：preview 先行的成本是多跑一次压缩投影，收益是模型看到的引用顺序与编号顺序一致——跨轮对话中"7 号按钮"的锚定稳定性优先于分配效率。
4. **部分失败不回滚别名**（numbering docstring L7-8）：前一份快照的 alias 已发布就保留，后一份失败只影响后一份——编号永不回收重用，避免"同一编号此刻指向不同元素"的灾难。
5. **菜单与窗口共享编号空间**：`_NumberObservedSnapshots` 一条序列编号、`_PrepareAppMenus` 合并 refs 但保留各自 target——模型可以在同一观察里用编号同时引用窗口控件与菜单项，而绑定层不会混淆归属。
6. **全文/差分是交付期决策**：`DeliverySelectionPipeline` 独立于采集——同一份采集物可以按 baseline 兼容性选择输出形态，diff 计划（`plan_observation_diff`）与终态渲染解耦。

## 六、新人提示与坑

- **勘误（tour 措辞）**：tour S12 说"delivery 四步组装 AppObservation（baseline/diff/menu 差分）"——`AppDeliveryPipeline` 的四步实际是 `assemble_observation_header/_PrepareAppMenus/append_window_overview/assemble_observation`（delivery/pipeline.py:90-98）；baseline/diff 差分在**另一个管线** `DeliverySelectionPipeline`（delivery/diff/pipeline.py:55-76），menu 也不是差分而是文档追加。三个概念分属两处，别按 tour 的合并表述找代码。
- **`_LaunchDispatch.children` 是动态的**（L173/L186-187）：执行期挂 `(pipeline.intent, pipeline.main)`、finally 清空——诊断树的这个节点形状随执行变化，写 traverse 工具时要容忍 children 元组的瞬时性。
- **`choose` 里无 surfaces 的分支顺序敏感**（L296-318）：`directory["surfaces"] or "nativeApplicationRoots" not in capabilities` 决定是否尝试 `_selection`——capability 缺失时即使无 surfaces 也要走 `_selection`（依赖目录外的证据），别"简化"成只看 surfaces。
- **编号的两层管线别混**：`numbering/pipeline.py`（`NumberSnapshotsPipeline`，纯编号）与 `numbering/observation/pipeline.py`（`NumberedPresentationPipeline`，编号+busy 标注+冻结投影）是上下游；`NativeAppReader.number_snapshots` 走前者并注入会话分配器，绕过它直接调 `NumberSnapshotsPipeline` 会丢跨读稳定性。
- **`MappingProxyType` 嵌套冻结**（L181-183）：launch 回执外层与 `application` 子层分别包了只读代理——尝试修改会 TypeError，这是有意的；深拷贝前先 `dict(...)` 展开两层。
- **diff 的 fallback 分支**：`_RenderPlannedDelivery` 只对 `DisplayDocument` 渲染，否则读 `observation["state"]["text"]`（diff/pipeline.py:44-49）——旧版观察对象（无 DisplayDocument）仍可交付，兼容路径别删。
