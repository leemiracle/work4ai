# 11 · 呈现压缩与写入执行——compression/ir 与 WritePipeline

## 一、角色定位

这是喂给模型前的最后一道读工序（S13），与把模型意图变成原生输入的第一道写工序（S14）：

- **呈现压缩**：`read/presentation/compression/pipeline.py`（270 行）+ `presentation/records.py`（99 行）+ `presentation/ir.py`（729 行）。回答：**如何把可能上千节点的无障碍树压成模型可负担的文本，同时保证每个字都有出处、每个删除都有账**。docstring（compression L4-7）："One source-preserving compression traversal with explicit pure rules. The traversal owns ordering. Rules receive a read-only view plus a narrow editor, never the input graph or execution ports as mutable shared state."（一次保源压缩遍历；规则只拿只读视图+窄编辑器，绝不拿可变的输入图或执行端口）。
- **写入执行**：`write/pipeline.py`（198 行）+ `write/engine.py`（66 行）+ `write/routes/selection/pipeline.py`（137 行）。回答：**一个意图如何在预算内完成"解析→绑定→选路由→执行→（必要时）重规划→回执"**。docstring（write L4）："fixed intent, resolution, one route and a Gate"。

两侧共享同一条纪律：**压缩不发明值、写入不掩盖不确定性**。

## 二、内部结构

**压缩侧**
- `RULES` 注册表（compression/pipeline.py:115-156）：**恰好 11 条规则**，每条是 `(handler, reads, writes)` 三元组——`associate_labels/promote_description/merge_editors/merge_control_labels/merge_repeated_text/merge_region_labels/flatten_redundant_hierarchy/prune_layout/prune_empty_rows/reconstruct_outlines/finalize_sources`；`Rule.pass_node()`（L95-107）把声明转成 `Pass` 契约：`Effect.PURE`、`requires=reads`、`writes=writes`、`failures=("presentation_contract",)`。
- 两组编排位（L77-78）：`BEFORE_CHILDREN` 三规则（promote_description/merge_editors/merge_control_labels，进入子树前）；`AFTER_CHILDREN` 五规则（merge_repeated_text/merge_region_labels/flatten_redundant_hierarchy/prune_layout/prune_empty_rows，子树完成后可拼接/删节点）。
- `CompressionTraversal`（L189-241）：单遍遍历。`visit`（L203-226）先序跑 BEFORE、`edit.children` 重写子序列（L221）、后序跑 AFTER——任何规则返回非 `[node]` 即替换/删除该节点（L224-225）；table 上下文判定（L213-218，row 多于 1 cell 或继承）；应用视图全展开重排根（L228-231），并把 roots 重排为 windows→others→menuBar（L232-237）。
- `CompressionPipeline`（L244-266）：`Sequence[build_presentation_ir, whole_rule(associate_labels), CompressionTraversal, whole_rule(reconstruct_outlines), whole_rule(finalize_sources), validate_projection]`——整树规则两条夹着遍历，终以校验导出。
- `records.py` 是词汇层：五个 TypeAlias（L24-47，`SemanticNode` docstring 明言"open dictionaries…without coercion or copying"——开放字典不强制拷贝）；`SnapshotFacts` Protocol 11 属性（L50-78）；`ReferenceAllocator` Protocol（L81-99，`reference(native)` 返回别名"without rebinding it"）。
- `ir.py` 是防护层：frozen 词根 `FactKey/ValuePart/PresentedValue/Elision/ProjectionInput`（L32-114）；**两个白名单** `DISPLAY_FIELDS`（5 个展示字段）与 `ANNOTATIONS`（4 个注释键，L196-197）；`ViewNode`（L282-339）是活只读 Mapping——`children` 递归视图（L297-298）、`native` 直读原始图（L299-300）、`textSources` freeze（L304）；`ProjectionEditor`（L417-）只开五个口子——`children/roots/annotate`（键白名单 L436-437）/`targets/set_field`，其中 `set_field`（L443-470）**强制"值必须与某不可变源字段完全相等"**（L466-468，否则 `ValueError("Presentation value has no matching source field")`）；`validate_projection`（L632-664）五连查——未知/重复 ref、未知 source、caption 无源（L647-652）、elision 无宿主、**"Projection removed an element without recording its source"**（L660-661，守恒律）；`ProjectionResult`（L667-687）是 dict 子类，把 `source/provenance` 作为不可序列化属性随身携带。

**写入侧**
- `WritePipeline.build`（write/pipeline.py:65-117）五段组装：`intent`（L61，仅 `parse_write_intent`）；`binding = Sequence[resolve_requested_path, pin_operation_target]`（L100-106，路径解析+目标钉住）；`Scope(NativeOperationScope, using=operation_scope, body=[binding, repeat])`（L110-114，native 租约包住整个尝试循环）；`repeat = Repeat(WriteReplanLoop, body, gate=write_replan_gate(state), on_decision=self.consume_decision, bounded_by="existing total deadline, semantic RouteKeys and shared Attempts limits")`（L93-99）；收尾 `format_write_result`（L115）。body 内部（L83-92）：`snapshot_resolution_input → TargetResolutionPipeline → record_resolution → completed → record_step_outcome`；`completed`（L73-82）按 `recognize_existing_completion` 分 `empty`（目标已是期望值→`complete_empty_input`）与 `route`（`observe_selected_pair` + 路由执行）。
- 路由选择（routes/selection/pipeline.py）：`CandidateGenerationPipeline`（L52-71，枚举意图兼容单元→动作语义→平台偏好→按 supported 排序）；`RouteChoicePipeline`（L74-126）的**四层回退链**用 `choice()` 工厂（L90-91，每层一个 `Select(has_selected_route)`）织成：ready→background→property→foreground→refused（L93-104、118-121）；顶层再嵌 `ClickOrLegacyRoute` Select（L110-124）——`"click"` 走协商 click 契约（`select_click_offer`），`"legacy"` 走历史策略过滤+ready 选择。
- 路由执行（routes/pipeline.py）：`RouteExecutionPipeline`（L83-120）按 route family `Select` 到 `Sequence[build_unit_command, unit]`——每个 family 一个执行单元分支。
- `WritePipeline.run_in_call`（L119-180）：`native.calls.validate_claim(remaining)`（L144）先验租约；control 三态拼接（L145-151）；异常翻译三档——`CancelledError` 原样、`ComputerUseError` 经 `failure()` 带 `dispatched/preparation/minimum_effect`（L158-167）、其余按 `self.state.dispatched != NOT_DISPATCHED` 分 `execution_unknown/execution_failed`（L168-175）；原异常 `__notes__` 全量转移（L178-179）。
- `Engine`（engine.py:23-66）：窄门面，`execute`（新预算）与 `execute_in_call`（借预算）双入口，全部委托 `EngineCallPipeline`。

## 三、外部连接

- **压缩侧被消费**：09 篇的 `PrepareSnapshotPipeline`、10 篇编号的 `_PreviewSnapshot` 都以压缩为核心（preview 即 compact 投影）；`ProjectionResult.document` 属性支撑 delivery diff 的 `DisplayDocument`；`RenderedTree` 别名被渲染层引用——图谱中 records.py 入度 46、ir.py 入度 30 为 read 域最高。
- **写入侧被消费**：03 篇 `ControllerWritePipeline` 与共享 write 实例；10 篇 `_LaunchDispatch` 的 `run_in_call`（读内嵌写的唯一通道）；`InterfacePointerPipeline`（agent/pipeline.py:503-506）复用 write。
- **共用底座**：`WriteRunState`（progress.py）是 Gate 与异常翻译共享的"账本"（dispatched/preparation/attempts）；`native.calls` 租约（operation/claim）两侧读写同一生命周期。

## 四、数据流

**压缩**：`ProjectionInput.build(root, context)` → `build_presentation_ir`（源图→IR：nodes/fields/annotations/elisions 四账本）→ 整树 `associate_labels` → 单遍遍历（先序合并编辑器/标签、后序合并重复文本/剪层级/剪空行）→ 整树 `reconstruct_outlines`（披露关系重建大纲深度）→ `finalize_sources`（省略项的最终去向）→ `validate_projection` 五查 → `export_projection` 出 `ProjectionResult`（可见节点+溯源路由）。

**写入**：`(intent, target, path, ...)` → `intent.run` 解析 → Scope 开租约 → 绑定（路径解析+目标钉住）→ `Repeat` 每轮：快照解析输入→目标/接收者解析→记录→（已完成则空补全；否则观察选中对+选路由+执行）→ 记录步果 → Gate 读 `WriteRunState` 决定 `Continue`（换路由重试，reason 限定 routeUnavailable/preparationUnavailable/preconditionChanged）或 `Done`（回执）→ `format_write_result`。

## 五、设计决策与权衡

1. **契约化纯规则**：11 条规则全部 `Effect.PURE` 且声明 reads/writes——诊断系统能静态回答"这次压缩谁动了什么"；违规写入在编辑器白名单处硬失败（ValueError），而非静默通过。
2. **守恒压缩**：`set_field` 的值必须逐字来自源字段（L466-468）、删除必须记 elision（L660-661）、折叠必须记 fold 的源与宿主（L662-664）。**压缩管线可能在任何一步崩溃，但产出的每个字符都可溯源**——这是对抗模型幻觉"读到的内容"的根基。
3. **一次遍历而非多趟**：先序 3+后序 5 规则共享单次 DFS（L189-226），避免多趟遍历的顺序耦合；两条真正需要全树视角的规则（outlines/finalize）以 whole_rule 形式独立成步。代价是规则间有隐式顺序依赖（BEFORE 组产出供 AFTER 组消费），调整规则次序要读 `reads/writes` 声明。
4. **重规划循环的预算外置**：`Repeat` 的 `bounded_by` 是语义说明串而非数字（L98）——真实上限来自调用预算+RouteKeys+共享 Attempts；Gate 决策通过 `on_decision=consume_decision` 回写共享态（L190-194），循环体与决策的副作用分家。
5. **四层路由回退链**：ready（直接执行）→background（后台准备）→property（属性路由）→foreground（需前台授权的准备）→refused——每层 `Select(has_selected_route)` 先问"选到了吗"，选择失败自动降层；foreground 放最末与 `HostPolicy.foreground_allowed`（04 篇 contracts.py:510-512）呼应：能后台绝不前台。
6. **异常即状态函数**：`run_in_call` 的翻译只依赖 `self.state.dispatched`——派发过就 `execution_unknown`（可能已生效），没派发才 `execution_failed`；这与 native 层 `StepResult.retry_reason` 白名单（04 篇）构成两级"不确定不许重放"。

## 六、新人提示与坑

- **RULES 是 dict 不是 list**（L115-156）：键是 handler 函数对象；`apply_rule/whole_rule` 都按键取——加新规则时若忘写进 RULES，`pass_node()` 在运行时 KeyError 而不是 import 期报错。
- **`ViewNode.__eq__` 是身份比较**（ir.py:330-333）：两个内容相同的 ViewNode 若 IR 不同即不等——测试断言请用 `dict(node)` 比较。
- **压缩里"删除"是替换语义**：`visit` 后序规则返回 `replacement`，只有 `len!=1 or replacement[0] is not node` 才算删除/替换（L224-225）；写自定义规则时返回 `[node]` 表示保留，返回空列表表示剪枝——剪掉的节点必须已被记入 elision，否则 validate 阶段炸"removed an element without recording its source"。
- **`WritePipeline.run_in_call` 的 control 三态**（L145-151）：无 `_control` 新建、`_control.call_id is None` 走 `scope_control` 包装、已有 call_id 只 `with_remaining`——三条路径语义不同（新作用域/借作用域/续作用域），写调用方时对号入座。
- **`Engine` 与 `WritePipeline` 是两个入口族**：`Engine.execute*`（桌面级、自带 call 管线）与 `WritePipeline.run_in_call`（会话内、必须已有 claim）——读内嵌写（launch）只能走后者，`validate_claim` 会拒绝无租约调用。
- **压缩的根重排只对 app 全视图**（L232-237 的 `if "app" in view.context`）：menuBar 永远排最后；子树投影（subtreeRef）不重排——改根顺序前先确认视图上下文。
