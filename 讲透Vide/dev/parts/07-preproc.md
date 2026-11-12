# 07-preproc 精读手册

> 模块定位：`preproc` crate 是 vide 的**数据库无关源码预处理模型层**——把 slang 预处理器产出的 `Trace`（经 `syntax::preproc` 来自 slang-sys FFI）在单趟内重放成可查询的 `SourcePreprocModel`（宏定义表 / 宏引用表 / 宏调用表 / include 图 / 宏可见性时间线）。它位于 syntax 之上、`preproc-expand` 之下：不碰 Salsa 数据库、VFS、编译计划与宏文件展开（lib.rs L1-5 文档注释明确划界），是 IDE 宏补全/跳转/条件编译分析的纯数据底座。唯一外部消费者是 `preproc-expand`（8 个文件 import `source.rs`），公开 API 由 `lib.rs` 白名单刻意收窄。

---

## `crates/preproc/Cargo.toml`（9 行）【配置·简版】

**作用**：声明 `preproc` crate，workspace 成员（根 Cargo.toml L21）。
**关键字段**：依赖仅 3 个——`smol_str.workspace` / `syntax.workspace` / `utils.workspace`（L7-9）。**刻意无 salsa、无 preproc-expand、无 serde**，即"纯模型"约束由依赖图强制：本 crate 无法反向依赖它的消费者。
**改动连带**：新增依赖前先自问是否破坏"纯模型"边界（lib.rs L5 的职责声明）；`syntax` 版本升级会连带 `Trace`/`Token` 结构变化，`trace.rs` 的投影代码需同步。

---

## `crates/preproc/src/lib.rs`（7 行）

**角色**：crate 根，只有一段职责文档 + `pub mod source`（L7）。

**关键结构与不变量**：无类型定义；文档注释 L1-5 是本 crate 的宪法："owns preprocessing events, trace identifiers, macro records, and source ranges"，数据库集成/VFS/编译计划/宏文件展开归 `preproc-expand`。

**公开 API**：`pub mod source`；实际类型全部经 `source.rs` 重导出。

**依赖/被依赖**：出边→`source.rs`。入边：图谱报 `slang-sys/src/lib.rs` imports 本文件——**这是图谱误报**（slang-sys L11 的 `pub use preproc::{...}` 是其内部 `pub mod preproc` 模块重导出，与 crates/preproc 无关，已源码核实）；真实入边是 `configures` ← `preproc/Cargo.toml`。

**改动影响面**：改文档注释=改 crate 边界契约。

**集成点**：无直接钩子；理解本 crate 从这 5 行文档开始。

---

## `crates/preproc/src/source.rs`（18 行）

**角色**：模块树根 + **唯一公开面守门人**——`mod model/tables/types` 全部私有，L10-18 的两条 `pub use` 白名单是 crate 对外的全部符号。

**关键结构与不变量**：不变量="公开符号必须逐个列举"（L7-9 注释：防止 glob re-export 让 dead-code 分析失效；新增公开符号是**刻意的 API 决策**）。导出清单：tables 侧 12 个（`SourceIncludeDirective/Id/Status`、`SourceMacroArgument/Call/CallId/Definition/DefinitionId/Reference/ReferenceId/Resolution`、`SourcePreprocUnavailable`），types 侧 7 个（`MacroIncludeTarget`、`PreprocSourceId`、`SourceMacroParam`、`SourcePosition`、`SourcePreprocError`、`SourcePreprocModel`、`SourceRange`）。**注意 `SourceMacroStateTimeline/State/Checkpoint` 等未导出**——宏时间线是 crate 内部机制，外部只能经 `SourcePreprocModel::visible_macros_at` 间接触达。

**公开 API**：即上述 19 个类型的 re-export。

**依赖/被依赖**：出边→`tables.rs`、`types.rs`。入边（图谱+grep 双核实）：`preproc-expand` 的 `macro_file.rs`、`compilation_plan.rs`、`macro_file/source_map.rs`、`preproc.rs`、`source_db.rs`、`db.rs`、`preproc/types.rs` 共 7 文件 + 本 crate `lib.rs`。

**改动影响面**：白名单增删 = preproc-expand 编译面变化；删一个符号会直接打断上述 7 个消费文件。

**集成点**：二次开发者 import preproc 时只认这张白名单；`builder.rs` 的 `SourcePreprocModelBuilder` 以 `pub(in crate::source)` 出口（tables.rs L81），确保 builder 永不外泄。

---

## `crates/preproc/src/source/model.rs`（48 行）

**角色**：`SourcePreprocModel` 的 impl 块——入口工厂 + 6 个只读查询方法。

**关键结构与不变量**：
- `from_trace` L7：`collect(trace)?.build()` 两阶段，`Result<_, SourcePreprocError>`；构建是**单趟+派生**结构（collect 投影 → build 派生表）。
- 查询方法全是只读借用：`macro_definitions()` L11、`macro_references()` L15、`macro_calls()` L19、`include_graph()` L23、`inactive_ranges()` L27（返回 `&[SourceRange]`）。
- `visible_macros_at(SourcePosition)` L31：委托 `state_timeline.state_at_position` → `definitions_for_state`（L38：`BTreeMap` 值→table get，缺失项静默 filter_map 跳过）。位置查询失效时 `unwrap_or_default()` 返回空 Vec（L35）——**永不 panic** 是该 API 的契约。

**公开 API**：`pub fn from_trace(trace: Trace) -> Result<Self, SourcePreprocError>`；5 个表访问器 + `visible_macros_at`。

**依赖/被依赖**：出边→`tables.rs`（`Trace` 类型）、`types.rs`、`syntax/src/lib.rs`（`syntax::preproc::Trace`）。入边←`model/tests.rs`。

**改动影响面**：`from_trace` 签名变化直接打断 preproc-expand 的 `compilation_plan.rs` L358 与 `source_db/queries.rs` L99 两个调用点；`visible_macros_at` 是 IDE 宏补全数据源，语义变化影响下游补全测试。

**集成点**：这是整个 crate 的**消费入口**——外部世界唯一构造 `SourcePreprocModel` 的路径。

---

## `crates/preproc/src/source/types.rs`（11 行）

**角色**：types 子模块聚合器：`mod events/ids/index/macros/sources` + glob `pub use *`（L7-11）。

**关键结构与不变量**：glob re-export 仅在**crate 私有模块层**使用（types 自身对 source.rs 是私有 mod）；最终对外可见性仍受 source.rs 白名单约束——双层收窄设计。

**公开 API**：5 个子模块的全部 pub 符号（crate 内可见）。

**依赖/被依赖**：出边→types 五个子文件。入边←`source.rs`、`model.rs`、`tables.rs`（tables/items.rs 经 `use super::types::*` 间接）及各子文件回环。

**改动影响面**：新文件加入 types/ 需在此登记 mod+use 两行。

**集成点**：types 家族的命名空间根。

---

## `crates/preproc/src/source/types/index.rs`（23 行）

**角色**：**核心聚合结构体 `SourcePreprocModel` 的定义处**（方法 impl 在 model.rs——结构体与 impl 分离布局）。

**关键结构与不变量**：L13 `#[derive(Debug, Clone, PartialEq, Eq)]`（全值语义，无生命周期参数，可整体 clone 缓存）。9 个字段全部 `pub(in crate::source)`（L15-22）：`root_source: PreprocSourceId`、`sources: Vec<PreprocSource>`、`inactive_ranges: Vec<SourceRange>`、4 张表、`include_graph`、`state_timeline`。不变量：①字段只允许 builder 写——外部无 setter，模型不可变；②`PartialEq` 全字段比对，preproc-expand 可用相等性做 memoization 判等；③文档注释 L9-12：raw event 投影"不存活进模型"，只存活派生表（builder 的 `event_records/defines/...` 在 build 后丢弃）。

**公开 API**：结构体本身（经白名单导出）；字段 crate 内可见。

**依赖/被依赖**：出边→`tables.rs`（4 张表类型）。入边←`types.rs`。

**改动影响面**：加字段必须同步 `trace.rs` L51-60 的零值初始化与 `PartialEq` 语义；外部无字段访问器意味着加字段不破坏 API（通过访问器方法渐进暴露）。

**集成点**：二次开发想暴露新查询时：加字段（builder 填充）+ model.rs 加访问器 + source.rs 白名单导出，三步成链。

---

## `crates/preproc/src/source/types/ids.rs`（74 行）

**角色**：全 crate 的**坐标原语层**——source id、事件 id、位置/区间、事件/条件分类枚举。

**关键结构与不变量**：
- `PreprocSourceId(u32)` L6：newtype 封装 slang trace 的 buffer_id；`From<u32>` L64 + `raw()` L53。不变量：数值空间=slang `SourceBufferRange.buffer_id`，语义由 trace 侧保证。
- `SourcePreprocEventId(pub(in crate::source) u32)` L46：**内部元组字段仅 crate::source 可见**，外部只能 `raw()` 读数（L58-62）；`From<EventId>` L70 直取 slang EventId 内部值——两 crate 的事件 id 数值等值。
- `MacroEventKind` L9-16 六分类：Define/Undef/Include/Conditional/Branch/Usage（Include 与 Branch 在状态重放中被跳过，见 references.rs L12）。
- `MacroConditionalKind` L25-31 五分类：IfDef/IfNDef/ElsIf/Else/EndIf。
- `SourcePosition { source, offset: TextSize }` L34、`SourceRange { source, range: TextRange }` L40——**带源归属的位置/区间**，一切表格的定位语言；TextRange/TextSize 来自 `utils::line_index`。

**公开 API**：上述类型 + `new/raw/from`；`MacroIncludeTarget`（Literal/Token）在 macros.rs。

**依赖/被依赖**：出边→`syntax/src/lib.rs`（re-export slang-sys 的 `EventId/MacroCallId/MacroDefinitionId` L2）、`utils/src/line_index.rs`。入边←`types.rs`。

**改动影响面**：`PreprocSourceId`/`SourcePosition`/`SourceRange` 是 preproc-expand `source_db`/`source_mapping` 的通用货币（grep 证实 30 文件引用），改语义=全下游重写。

**集成点**：二次开发的宏补全查询入口参数 `SourcePosition`；跨 buffer 定位一律 `SourceRange`。

---

## `crates/preproc/src/source/types/macros.rs`（79 行）

**角色**：**原始事件投影记录**（builder 私有输入的数据载体）——从 slang `Event` 逐字段搬运的中间形态。

**关键结构与不变量**：
- `SourcePreprocEventRecord` L6：`event_id + kind + range + index`——不变量：`index` 是**同类事件桶内下标**（defines/undefs/... 各 Vec 的下标），非全局序（全局序叫 source_order，只存在于枚举时刻，不落库）。
- `SourceMacroDefine` L14：`trace_definition: Option<MacroDefinitionId>`（slang 侧定义 id，可为 None）+ `name/name_range` 均为 Option（缺名 define 会被 definitions.rs L6-11 跳过）+ `params: Option<Vec<SourceMacroParam>>`（空 params 存 None，见 trace.rs L208-209 的 `(!is_empty).then()`）+ `body: Vec<SourceMacroToken>`。
- `SourceMacroParam` L25：name/name_range/default/range 四 Option——**每个字段都可能缺失**是 trace 现实（slang 可能给不出 range）。
- `SourceMacroUndef` L33、`SourceMacroInclude` L41（`target: MacroIncludeTarget` + `target_range` Option）、`SourceMacroConditional` L49（`expr: Vec<SourceMacroToken>` 条件表达式 token 流）、`SourceMacroUsage` L57（`trace_call`+`trace_definition` 双 Option 关联 slang 侧调用/定义）。
- `SourceMacroActualArgument` L68 / `SourceMacroToken` L75：token 的 `raw`（原文）与 `value`（去 `` ` `` 后值）分离；`range: Option` 可缺。

**公开 API**：全部 pub struct/字段（crate 内使用；`SourceMacroParam`/`SourceMacroToken` 经白名单外泄给 preproc-expand——分别作为 definition.params/body_tokens 的元素类型被间接带出）。

**依赖/被依赖**：出边→`types.rs`。入边←`types.rs`。

**改动影响面**：这些记录的 Option 语义被 builder 各处 `let Some(...) else { return/continue }` 消费，收紧为非 Option 需重写 trace.rs 投影层。

**集成点**：想接入新 slang 事件字段时在此扩投影结构 + trace.rs 补搬运。

---

## `crates/preproc/src/source/types/sources.rs`（20 行）

**角色**：预处理源文件（buffer）的元数据三类型。

**关键结构与不变量**：
- `PreprocSource` L2：`id + path: SmolStr + origin`。
- `PreprocSourceOrigin` L9-14 四态：`Root`（根文件）/ `Predefine`（slang 预定义宏源）/ `Included { include_event_id }`（被 include 的文件，锚到 include 事件）/ `Detached`（不在 include 链上——通常来自展开缓冲）。不变量：**每个非根、非 Predefine 的 buffer 若无 include 边即 Detached**（trace.rs L177-196 source_origin 的 fallback），resolution.rs L66 据此判定可达性。
- `SourceIncludeEdge` L17：`include_event_id + included_source`，include 图的原始边。

**公开 API**：三个 pub 类型（crate 内；未入白名单）。

**依赖/被依赖**：出边：无 import（仅用 super 路径）。入边←`types.rs`。

**改动影响面**：origin 四态是 `source_is_reachable`（resolution.rs L66）与 `record_source_order_scopes`（state.rs L34-44）的分支依据，加第五态需同步这两处 match。

**集成点**：`Predefine` 态让"slang 内建宏源"在模型中有明确身份，诊断时可区分对待。

---

## `crates/preproc/src/source/types/events.rs`（8 行）

**角色**：错误类型——名字叫 events，实际是 `SourcePreprocError`（文件名与内容错位，勿被误导）。

**关键结构与不变量**：L4-8 三变体：`MissingRootSource`（root buffer 不在 sources，trace.rs L46-48 抛出）、`MissingEventRange { source_order, kind }`（事件缺 range 即 fail-closed，trace.rs L244-251）、`MissingEvent { event_id: u32 }`（当前 crate 内**无产生点**，为对齐 trace 语义预留——grep 全 crate 仅定义+测试引用）。不变量：错误携带定位信息（source_order/kind），下游可精确诊断。

**公开 API**：`pub enum SourcePreprocError`（Debug/Clone/PartialEq/Eq），入白名单。

**依赖/被依赖**：出边→`types.rs`。入边←`types.rs`。

**改动影响面**：preproc-expand `source_db/queries.rs` L99 与 `compilation_plan.rs` L358 match 此错误，加变体是 breaking。

**集成点**：模型构建失败的唯一协议通道。

---

## `crates/preproc/src/source/tables.rs`（81 行）

**角色**：tables 家族根：**两个声明宏**（id newtype 工厂 + 表工厂）+ 子模块聚合。

**关键结构与不变量**：
- `source_table_id!` L7-22：生成 `$name(usize)` newtype + `new/raw`——5 个 id 类型共用（L65-69：Definition/Reference/IncludeDirective/MacroState/Call）。不变量：**id == 表 Vec 下标**（storage.rs L33 `get(id.raw())`）。
- `source_table!` L24-63：生成表 struct（内部一个 Vec）+ `get/iter/len/is_empty`（L32-46）+ `push`（L48，可见性 `pub(in crate::source::tables)`——**只允许 builder 家族写**）。第二变体 `,mutable`（L54-62）追加 `get_mut`。不变量：表构建完成后外部只读；id 稠密连续。
- `builder` 模块以 `pub(in crate::source) use`（L81）导出 `SourcePreprocModelBuilder`——builder 不出 source 模块。

**公开 API**：5 个 id 类型 + 经子模块 re-export 的全部条目/表类型。

**依赖/被依赖**：出边→builder/items/storage/unavailable + `types.rs`。入边←`source.rs`、`model.rs`、builder 家族、items/storage/unavailable（回环 `use super::*`）、`types/index.rs`。

**改动影响面**：宏改动 = 5 张表全部重编译；`push` 的可见性收紧/放宽直接决定谁能绕过 builder 写表。

**集成点**：二次开发新增一种预处理条目表（如 `MacroExpansionTable`）时复用这两个宏最省力。

---

## `crates/preproc/src/source/tables/items.rs`（103 行）

**角色**：**解析后的条目类型**——模型最终对外承载的数据形态（与 macros.rs 的"原始投影"相对）。

**关键结构与不变量**：
- `SourceMacroDefinition` L4：与原始 `SourceMacroDefine` 的差异是**去 Option 化**（`name: SmolStr`、`name_range: SourceRange` 必有）+ `id` + `directive_range`；不变量：能进此表的 define 必有名字与 range（definitions.rs L6-11 的过滤）。
- `SourceMacroReference` L16 + `SourceMacroResolution` L26 三态：`Resolved { definition }` / `Undefined` / `Unavailable(SourcePreprocUnavailable)`——**引用解析结果的所有情况**，Unavailable 保留失败原因。
- `SourceIncludeGraph` L33：默认 `{ directives: Vec<SourceIncludeDirective> }`（字段 `pub(in crate::source::tables)`，builder 写、`SourceIncludeGraph::directives()` 只读，storage.rs L13）。
- `SourceIncludeDirective` L38 + `SourceIncludeStatus` L49 三态：`Resolved { source }` / `Unresolved` / `Unavailable`。不变量：`resolved_source` 与 `status` 冗余存储（L104-106 同步赋值），读侧可任选。
- `SourceMacroStateTimeline` L56-64：五字段——`states`（宏名→定义 id 的快照序列）、`checkpoints`（source_order→state id 锚点）、`source_order_scopes`（每个 source 的有效序上限）、`source_order_boundaries`（每 source 内 offset→source_order 分段）、`final_source_order`（事件总数）。**位置查询的二段索引结构**。
- `SourceMacroState` L67（`definitions: BTreeMap<SmolStr, SourceMacroDefinitionId>`——快照即"该时刻可见宏全集"）、`SourceMacroStateCheckpoint` L73、内部 `SourceMacroStatePositionBoundary` L79 / `SourceMacroStateSourceScope` L85（`pub(in ...)` 双字段）。
- `SourceMacroCall` L90：`trace_call: Option<MacroCallId>` + `reference` + `arguments: Vec<SourceMacroArgument>`（L99：index+range+tokens，tokens 可空——多事件投递时首非空生效）。

**公开 API**：上述全部 pub 类型（多数入白名单；State 家族未入）。

**依赖/被依赖**：出边→`tables.rs`（`use super::*` 拿 types 宏与 id）。入边←`tables.rs`。

**改动影响面**：`SourceMacroResolution` 三态被 preproc-expand diagnostics 消费，改枚举=诊断链重写；`SourceMacroCall` 是宏调用高亮/展开定位的数据源。

**集成点**：IDE 的"查找宏引用/跳转定义"直接扫 `macro_references`/`macro_definitions` 两表即可，无需重放。

---

## `crates/preproc/src/source/tables/storage.rs`（47 行）

**角色**：表的**实例化**（三张表落位）+ `SourceMacroStateTimeline` 的位置查询算法。

**关键结构与不变量**：
- L3-10 表实例化：Definition 表（只读）、Reference 表（只读）、Call 表（**`,mutable`** 变体——唯一可变表，因 `record_macro_actual_argument` 要回填参数，references.rs L151）。
- `state_at_position` L19：`source_order_at_position` → `state_at_source_order` 二段定位。
- `source_order_at_position` L24-36：①取该 source 的 `end_order`（无 scope 则 `final_source_order`）；②无 boundaries 直接返回 end_order；③`boundaries.partition_point(|b| b.boundary.offset <= position.offset)`（L34）二分找**首个 offset 越过查询点**的边界，取其 source_order，越界回退 end_order。不变量：boundaries 已按 `(offset, source_order)` 排序（state.rs L20），且 boundary 是"指令结束位置"（`boundary_after`，builder.rs L60-64）。
- `state_at_source_order` L38-46：`checkpoints.partition_point(|c| c.source_order <= order)` 取**最后一个不晚于查询序的 checkpoint**；`index == 0` 返回 None（查询点在首个 checkpoint 之前=无状态记录）。

**公开 API**：`state_at_position`、`SourceIncludeGraph::directives`；表类型实例。

**依赖/被依赖**：出边→`tables.rs`。入边←`tables.rs`。

**改动影响面**：partition_point 的 `<=` 边界语义是"指令结束点即生效"的基石（macro_state.rs L17-23 测 include 行后立即可见）；改成 `<` 会全链错位。

**集成点**：`state_at_position` 是 `visible_macros_at` 的引擎——IDE 任意光标位置的宏可见性查询。

---

## `crates/preproc/src/source/tables/unavailable.rs`（11 行）

**角色**：`SourcePreprocUnavailable` 六变体——解析失败原因协议。

**关键结构与不变量**：L4-11：`DetachedSource{source}`（定义在 include 链外的源上）、`MissingPredefineSourceText{source}`、`UnverifiedPredefineSource{source}`、`MissingMacroCall{call}`、`MissingMacroExpansion{call}`、`UnknownMacroUsageDefinition{definition: MacroDefinitionId}`（slang 给的定义 id 在模型中查无——resolution.rs L22-25 唯一产生点）。不变量：**本 crate 只产生 2 种**（DetachedSource、UnknownMacroUsageDefinition），其余 4 种是 preproc-expand 宏展开阶段回填的占位——两 crate 共用此诊断词汇表。

**公开 API**：pub enum，入白名单。

**依赖/被依赖**：出边→`tables.rs`。入边←`tables.rs`。

**改动影响面**：preproc-expand `helpers/diagnostics.rs` 消费；加变体 breaking。

**集成点**：IDE 可据变体区分"宏不可见"（Undefined）与"宏在不可达源上"（DetachedSource）两种 UX。

---

## `crates/preproc/src/source/tables/builder.rs`（64 行）

**角色**：builder 聚合根——`SourcePreprocModelBuilder` 结构体 + 六步构建流水线编排。

**关键结构与不变量**：
- L7-22 builder 状态：`model`（半成品）+ 6 个**临时投影桶**（event_records/defines/undefs/includes/conditionals/usages）+ include_edges + 3 个索引（`definition_ids_by_define_index`、`definitions_by_trace_id`、`calls_by_trace_id`）+ `current_state: BTreeMap<SmolStr, SourceMacroDefinitionId>`（重放中的活宏状态）。不变量：临时桶在 `build()` 后随 builder 一起丢弃（doc 注释 L9-10）。
- `build` L32：`build_tables()` 后移出 model。
- `build_tables` L37-44 **六步定序**：①build_definition_table ②build_include_graph ③record_position_boundaries ④record_state_checkpoint(0, 首事件位置)（初始空态锚点） ⑤scan_references_and_state（核心重放） ⑥record_macro_body_references_for_calls。**顺序敏感**：③④ 必须先于 ⑤（重放中 `resolve_visible_reference_at_position` 要用 timeline），⑤ 先于 ⑥（body 引用按 call site 回填）。
- `SourcePosition::from_first_event` L48-58：无事件时回退 `{root_source, 0}`。
- `boundary_after` L60-64：指令 range 末端=生效边界（被 state.rs/references.rs 共用）。

**公开 API**：`pub(in crate::source)` 的 `build`/`collect`（后者在 trace.rs）。

**依赖/被依赖**：出边→`tables.rs`。入边←tables.rs + 6 个 builder 子模块。

**改动影响面**：六步重排会改变 id 分配序与 checkpoint 语义；这是全 crate 最脆的一处。

**集成点**：新增派生表时在此插一步（注意时序依赖）。

---

## `crates/preproc/src/source/tables/builder/trace.rs`（338 行）【本 crate 最大文件】

**角色**：**采集阶段**——slang `Trace` → builder 原始投影的完整搬运层，含全部 trace→source 的类型换算函数。

**关键结构与不变量**：
- `collect` L17-79：①root/include_edges/sources 三大顶层投影（L18-44），`PreprocSourceId::from(trace.root_buffer_id)` L18；②**root 存在性校验** L46-48（fail-closed：`MissingRootSource`）；③构造 builder 后逐事件 `collect_trace_event(source_order, event)`（L74-76）——**source_order 即此枚举下标**，是全局唯一序。
- `collect_trace_event` L81-159：先收集 `disabled_ranges`→`inactive_ranges`（L86-92，**过滤空 range**）；`event_kind` L94 识别不了的事件直接跳过（返回 Ok）；`required_event_range` L98/L244-251 缺 range 报 `MissingEventRange`；六类事件各自 push 进桶 + `push_source_event_record`（L161-174）登记 event_records。不变量：**每条 event_record.index = 该桶当前长度**（L102/108/118/129/139 的 `let event_index = self.xxx.len()`）。
- `source_origin` L177-196：判定序 root→Predefine→included_by→Detached（见 sources.rs 卡片）。
- `collect_trace_define` L198-213 + `macro_param_from_trace` L215 + `macro_actual_argument_from_trace` L226 + `macro_token_from_trace` L236：逐字段搬运，String→SmolStr（`to_smolstr`）。
- `TraceTokenOptionExt` L253-278：`Option<Token>` 四扩展——`value`/`macro_name`（剥 `` ` `` 前缀，经 L336-338 `macro_name`）/`source_range`/`include_target`（**无 token 时 include target 记为空 Token 原文** L276，不 panic）。
- `trace_range` L280 / `source_range_from_trace` L284-292：`Option<SourceBufferRange>`→`Option<SourceRange>`；**usize→u32 try_from 失败即整体丢弃为 None**（L288-289，防 >4GB buffer 溢出）。
- `event_kind` L294-306：SyntaxKind 六类映射（IFDEF/IFNDEF/ELSIF→Conditional，ELSE/ENDIF→Branch）；`trace_conditional_kind` L308-317 五细分（`_ => unreachable!()`——前置 event_kind 已保证）。
- `include_target_from_raw` L319 + `strip_include_delimiters` L327-334：`"..."`/`<...>` 成对定界符剥壳成 `Literal{path}`，否则 `Token{raw}`（**不成对（如只有引号一头）也归 Token**）。

**公开 API**：`pub(in crate::source) fn collect`；其余自由函数模块私有。

**依赖/被依赖**：出边→builder.rs、`syntax/src/lib.rs`（Trace/Event/Token/SourceBufferOrigin/SourceBufferRange + SyntaxKind）、`utils/src/line_index.rs`（TextRange/TextSize）。入边←builder.rs。

**改动影响面**：slang-sys `preproc.rs` 的 `Trace` 结构（L8-13 五字段）升级必改此文件；inactive_ranges 过滤规则变化影响条件编译灰显（inactive range 是 IDE 灰显数据源）。

**集成点**：接入新 slang 事件类型的唯一施工点（映射函数三件套：event_kind 加臂→此处加桶→references.rs 重放加臂）。

---

## `crates/preproc/src/source/tables/builder/definitions.rs`（30 行）

**角色**：派生第①步——defines 桶 → `SourceMacroDefinition` 表 + 双索引。

**关键结构与不变量**：`build_definition_table` L4-29：逐 define **过滤无名/无 name_range 者**（L6-11 `let Some(...) else { continue }`）；id 按 `macro_definitions.len()` 分配（L13）→ `definition_ids_by_define_index.insert(define_index, id)` L24（桶序→表 id 映射，重放时经 event_record.index 反查）；有 trace_definition 时 `definitions_by_trace_id` L25-27（slang id→表 id，usage 解析用）。不变量：**表内条目序 = 有效 define 的 trace 顺序**；被丢弃的 define 不占 id（测试 macro_state.rs L86 断言 root 重定义 id=1 依赖此稠密性）。

**公开 API**：`pub(in ...tables::builder) fn build_definition_table`。

**依赖/被依赖**：出边→builder.rs。入边←builder.rs（仅经 `impl` 块关联，无文件级入边——图谱 IN=0）。

**改动影响面**：过滤条件放宽（允许无名宏）需同步 `SourceMacroDefinition` 去_option 化的字段类型。

**集成点**：无独立钩子；索引双写是 usage/body 引用解析的前提。

---

## `crates/preproc/src/source/tables/builder/state.rs`（119 行）

**角色**：派生第②③步——include 图构建 + 宏状态时间线的位置索引铺设（"include 作用域"算法核心）。

**关键结构与不变量**：
- `record_position_boundaries` L4-22：`final_source_order = event_records.len()`（L5）；**每条事件**在其 source 名下登记 `boundary_after(range)` 边界；随后按 `(offset, source_order)` 排序（L20）——storage.rs 二分的前提。
- `record_source_order_scopes` L24-51：对每个 source 求 `end_order`——Root/Predefine/Detached = 事件总数（L35-37，即"全程有效"）；Included = `included_source_end_order(...)`（L38-44；找不到 include 事件的 `continue` **留空**该 source 的 scope，storage.rs L26-29 将回退 final_source_order——一个静默的宽容行为）。
- `source_parents_by_include` L53-75：include 事件所在 source = 被 include source 的 parent（BTreeMap）。
- `included_source_end_order` L77-92：从 include 事件序+1 起，找**首个不属于"该 source 或其后代"的事件序**——即 included source 的事件窗口右端。配合 `source_is_descendant_or_same` L121-135（沿 parent 链上溯，**循环依赖安全**：链上没有 ancestor 匹配最终走出 map 返回 false）。
- `build_include_graph` L94-118：include_edges（event→included source）建 BTreeMap；逐 include 桶条目生成 directive，`status` 与 `resolved_source` 同步三态化（L104-106：有边 Resolved / 无边 Unresolved）。

**公开 API**：六个 `pub(in ...builder)` 方法 + 模块级 `source_is_descendant_or_same`。

**依赖/被依赖**：出边→builder.rs。入边←builder.rs。

**改动影响面**：include 作用域窗口算错 → "included 文件里可见哪些 root 宏"全错（macro_state.rs L116/L131 两测即锚此行为：BEFORE 可见、AFTER 不可见）。

**集成点**：嵌套 include 的作用域传递（孙文件窗口落在子窗口内）由此自动成立。

---

## `crates/preproc/src/source/tables/builder/references.rs`（208 行）

**角色**：派生第⑤步——**核心重放循环**：按 source_order 重放事件，维护 current_state、产出引用/调用表、记录状态 checkpoint。

**关键结构与不变量**：
- `scan_references_and_state` L4-15：**先 clone event_records**（L5，因循环内要 &mut self）逐条 match：Define→apply_define、Undef→apply_undef、Conditional→record_conditional_references、Usage→record_usage_reference、Include|Branch→显式空臂跳过（L12）。
- `apply_define` L17-31：经 `definition_ids_by_define_index` 反查 → `current_state.insert(name, id)` → **checkpoint(source_order+1)**（指令之后生效）。`.expect("definition id should point at inserted definition")` L27——索引与表的一致性由 definitions.rs 构造保证。
- `apply_undef` L33-45：`current_state.remove` + checkpoint；**无名 undef 静默跳过**。
- `record_usage_reference` L47-76：usage → `resolve_usage_reference` → `push_reference` → `push_call` → 逐实参 `record_macro_actual_argument`。Usage 是唯一同时产 reference+call 的事件。
- `record_conditional_references` L78-104：对条件表达式**每个 token**建引用；解析优先级：current_state 有 → Resolved；否则 `include_guard_definition_after_ifndef`（ifndef 守卫特例）；否则 Undefined（L92-101）。
- `push_reference` L106 / `push_call` L126-144：表追加 + `calls_by_trace_id` 登记。
- `record_macro_actual_argument` L146-172：**同 argument_index 重复到达时合并**——range 用 `merge_optional_same_source`（同 source 取并集区间 L192-207，异 source 保留旧值 L198）、tokens 取**首个非空**（L161-163），最后按 index 排序（L171）。这吸收了 slang 对宏实参分多事件投递的现实。
- `SourceRangeOptionExt`/`SourceRangeExt` L175-207：Option 区间合并小工具，`merge_same_source` 异源时**丢新保旧**（返回 Some(existing)）。

**公开 API**：八个 `pub(in ...builder)` 方法 + 两个私有 trait。

**依赖/被依赖**：出边→builder.rs。入边←builder.rs。

**改动影响面**：checkpoint 时机（order+1）与 boundary_after 语义耦合（storage.rs 卡片）；参数合并规则变化影响宏调用实参高亮。

**集成点**：新事件类型重放时在此加 match 臂。

---

## `crates/preproc/src/source/tables/builder/resolution.rs`（144 行）

**角色**：解析策略族——引用→定义的四种解析入口 + 可达性判定 + include 守卫特例 + checkpoint 落盘。

**关键结构与不变量**：
- `resolve_visible_reference` L4-12：查 current_state，无则 Undefined。
- `resolve_usage_reference` L14-28：usage 有 slang 定义 id 时走 `definitions_by_trace_id`（**缺失 → Unavailable::UnknownMacroUsageDefinition**，fail-explicit）；无 id 退化到按名查 current_state。
- `resolve_visible_reference_at_position` L30-44：**按时间线历史查询**（`state_at_position` 后查该快照）——与 current_state（"当前重放点"）相对，服务 body 引用（定义处的宏环境≠调用处，必须回定义处位置查）。
- `resolve_definition` L46-63：定义源 `source_is_reachable` 通过 → Resolved；否则 **Unavailable::DetachedSource**（不因源不可达而丢引用，降级保留）。`source_is_reachable` L66-90：沿 origin 链上溯——Root/Predefine 即真、Detached 即假、Included 找对应 directive 换到父 source 继续（**directive 查无也返回 false**，L83-85）。循环 include 会在此死循环吗？——不会无限：链每步换一个 source，环会绕回已走过的 source 但无 visited 集合——**理论上自 include 环会无限循环**，但 slang trace 的 include_edges 对环有自身约束（预处理器 include guard 语义），此处依赖上游不产环。
- `include_guard_definition_after_ifndef` L92-127：`ifndef X` 之后**同 source** 顺序扫：遇 `define X` 返回其定义 id（L113-117）；遇 **Branch（else/endif）即终止**（L119）；跨 source 的事件跳过（L109-110）。语义：经典 `ifndef/define/endif` 守卫里，ifndef 处的 X 引用能解析到守卫自己的 define（当前 current_state 里还没有它）。
- `record_state_checkpoint` L129-143：快照 current_state **整体 clone** 进 states + checkpoint 登记。注意 `_boundary` 参数（L132）已废弃不用——边界信息改由 record_position_boundaries 统一登记，签名保留是历史兼容。

**公开 API**：七个 `pub(in ...builder)` 方法。

**依赖/被依赖**：出边→builder.rs。入边←builder.rs。

**改动影响面**：解析优先级顺序（current_state → 守卫 → Undefined）改变直接改变引用表内容；DetachedSource 降级策略是诊断正确性关键。

**集成点**：三种解析语义（按名/按 trace id/按位置）是二次开发新引用类型的模板。

---

## `crates/preproc/src/source/tables/builder/body_references.rs`（66 行）

**角色**：派生第⑥步——**宏体内部引用**回填：对每个宏调用，把定义 body 里的 `` `X `` token 也登记为引用。

**关键结构与不变量**：
- `record_macro_body_references_for_calls` L6-51：遍历所有 call（**先 clone 全表** L10——迭代中要 &mut self.push_reference）；只处理 `Resolved` 的调用；`call_position` = 调用点起始（L21-24）；对定义 body 每个有 range 的宏名 token：**按 call site 去重**（`emitted: BTreeMap<CallId, Vec<(name, range)>>` L9，注释言明旧线性扫描 O(n²) 已优化）→ `resolve_visible_reference_at_position`（**在调用位置查宏环境**——body 里引用的宏按展开点而非定义点解析，语义与 C 预处理器一致）→ push_reference（挂在 `definition.event_id` 名下，L42-48）。
- `SourceMacroTokenExt::macro_reference_name` L58-66：判据——**raw 以 `` ` `` 开头**；name 取 value 剥 `` ` `` 前缀；空名返回 None。

**公开 API**：`pub(in ...builder) fn record_macro_body_references_for_calls` + 私有 trait。

**依赖/被依赖**：出边→builder.rs。入边←builder.rs。

**改动影响面**：nested_expansion.rs L4 测试锚定"每 call site 一条 body 引用、name_range 相同、resolution 相同"；去重键改错会产生重复引用污染 IDE 查找。

**集成点**：`WRAP` 调用点跳转 `LEAF` 的数据基础（宏嵌套导航）。

---

## `crates/preproc/src/source/model/tests.rs`（107 行）【测试·简版】

**角色**：模型测试的组织者——公共 fixture 家族 + 三个子模块入口（L104-106）。
**覆盖什么**：fixture 体系——`source_model(root,header)` L26（include_buffers 注入 header，返回 model+root_source+header_source）；`preprocessor_trace` L17（`SyntaxTree::from_text_with_options_and_trace` 取真 slang trace，**测试走真解析器**）；`source_by_path_suffix` L46；`source_model_from_root` L58；`offset_before/after` L68-74、`text_at_range` L76、`visible_macro_names/definition` L80-102（全部经公开 API 断言，无内部字段偷看——白名单即被测面）。Windows 路径 `cfg!` 分支 L13-15。
**跑法**：`cargo test -p preproc`（需工具链 g++≥11/C++20 编译 slang-sys；本机 g++ 不支持 `-std=c++20` 时编译失败属环境问题）。

---

## `crates/preproc/src/source/model/tests/include_resolution.rs`（136 行）【测试·简版】

**角色**：include 解析与解析健壮性测试（4 例）。
**覆盖什么**：`source_model_resolves_conditional_tokens_to_visible_defines` L6（`` `ifdef`` token 解析到 header 里的 define——跨 buffer 引用链）；`source_model_resolves_ifndef_include_guard_to_following_define` L32（**守卫特例**：ifndef X → 后随 define X 也 Resolved）；`source_model_nested_include_resolution_carries_definition_chain` L57（root→header→leaf 两级 include，root 用法解析到 leaf 定义）；`source_model_fails_closed_when_directive_event_range_is_missing` L96（**手工构造畸形 Trace**——DEFINE 事件 range=None → 精确断言 `MissingEventRange{source_order:0, kind:Define}` L132-135，fail-closed 协议的回归锚）。
**跑法**：`cargo test -p preproc source_model_`（或全量）。

---

## `crates/preproc/src/source/model/tests/macro_state.rs`（193 行）【测试·简版】

**角色**：宏可见性状态机行为测试（8 例，本 crate 行为语义最密的测试文件）。
**覆盖什么**：`source_model_applies_include_define_after_include_point_only` L4（include **之前**的 offset 查不到 header 宏、之后查得到——boundary 生效语义）；`source_model_undef_removes_included_define` L38（undef 删除后不可见）；`source_model_same_name_define_overrides_included_define` L71（同名重定义：两定义并存、按位置取后者、body 各自正确 8/16）；`included_plain_source_uses_include_scope_macro_state` L116 与 `included_source_after_last_directive_uses_include_scope_macro_state` L131（**include 作用域窗口**：header 内查宏见 BEFORE/FROM_HEADER 不见 AFTER——state.rs 窗口算法回归锚）；`source_model_preserves_inactive_range_sources` L147（inactive range 的 **buffer 归属**正确分离 root/header，逐字符断言灰显文本 L162/L166）；`source_model_resolves_root_usage_to_included_define` L170（root 用法→header 定义的完整链 + body 值）。
**跑法**：`cargo test -p preproc`。

---

## `crates/preproc/src/source/model/tests/nested_expansion.rs`（28 行）【测试·简版】

**角色**：宏体引用按调用点登记的专项测试（1 例）。
**覆盖什么**：`source_model_keeps_macro_body_references_for_each_call_site` L4——`WRAP` 定义体引用 `LEAF`，两次调用 `` `WRAP `` → 恰好 2 条 `LEAF` body 引用（L25 `references.len()==2`），且以"**无 call 反指**"区分 body 引用与 usage 引用（L20-22 谓词：`!model.macro_calls().iter().any(|call| call.reference == reference.id)`），同名同 range 同 resolution（L26-27）。
**跑法**：`cargo test -p preproc source_model_keeps_macro_body_references`。

---

## 附：单元级速览

- **构建流水线**：`from_trace`(model.rs L7) → `collect`(trace.rs L17) → `build_tables` 六步(builder.rs L37-44)。
- **两套数据形态**：原始投影（types/macros.rs，Option 宽松）→ 解析条目（tables/items.rs，去 Option 严格）；中间态不落模型。
- **坐标语言**：`PreprocSourceId`(buffer) × `TextSize/TextRange`(utils) = `SourcePosition/SourceRange`；全局序 source_order 驱动状态时间线。
- **公开面**：lib.rs→source.rs 白名单 19 类型 + `SourcePreprocModel` 6 方法；builder/时间线/原始投影全部 crate 内部。
- **错误协议**：`SourcePreprocError`(3 变体，构建期) + `SourceMacroResolution`/`SourceIncludeStatus`/`SourcePreprocUnavailable`(查询期三态)。
