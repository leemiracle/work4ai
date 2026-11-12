# 13-ide-core 精读手册

> 模块定位：本单元是 ide crate 的"心脏地带"——Salsa 查询体系的最顶层。`db/` 四文件把 base-db（SourceDb/SourceRootDb）、preproc-expand（PreprocDb）、hir-def（HirDefDb）、hir-ty（TyDb）全部 trait 数据库汇聚成具体 `RootDb`，并在其上加两层 IDE 专属查询面（LineIndexDb 行索引、WorkspaceSymbolIndexDb 符号/语义索引）；`AnalysisHost`/`AnalysisSnapshot` 是 rust-analyzer 同款的"一写多读"快照模型（写端 apply_change + 取消，读端 Cancelled::catch 包裹全部 LSP 功能调用）；`semantic_index(.rs + /build.rs)` 是 references/rename/call-hierarchy 的数据底座（per-file 构建 + source-root 纯内存 merge）；`diagnostics.rs` 是 parse/lowering/Vide 三源诊断的合并与抑制管道。

---

## `crates/ide/src/lib.rs`（57 行）

**角色**：ide crate 入口——模块声明、跨 crate 再导出与 `ScopeVisibility` 枚举，是外部（vide 主 crate、ide-dap）消费 ide API 的唯一门面。

**关键结构与不变量**：
- `pub type Cancellable<T> = Result<T, Cancelled>`（L10）：全部 `AnalysisSnapshot` 方法的统一返回包装；`Cancelled` 由 L7 从 base-db 再导出（实为 `salsa::Cancelled` 的 re-export，见 base-db/src/lib.rs L7）。
- `pub enum ScopeVisibility { Public, Private }`（L53-57）：rename 范围选择用的可见性二值枚举，derive Copy/Hash，被 workspace_symbol_index_db 的 `recursive_rename_closure` 透传到 `crate::rename`。
- 模块可见性纪律：`manifest`/`module_resolution`/`semantic_target`/`token` 为 `pub(crate)`（L15/L17/L44/L49），其余全 pub——对外只暴露功能面，索引用的底层工具留在 crate 内。
- 测试专用模块：`index_benchmarks`（L34-35）、`macro_hover_tests`（L37-38）、`test_utils`（L47-48）、`verilog_2005`（L50-51）均 `#[cfg(test)]`。
- 两个 nightly feature（L1-2）：`try_blocks`（诊断模块用）与 `decl_macro`。

**公开 API**：`pub use base_db::{Cancelled, analysis_snapshot::{AnalysisSnapshotId, CompilationContext}}`（L4-7）；`pub use hir_def::symbol::DefKind`（L8）；`pub use range::{ErasedFileAstId, FilePosition, FileRange, RangeInfo}`（L9）；`ScopeVisibility`。

**依赖/被依赖**：依赖（imports 出边）base-db 的 analysis_snapshot/lib 与 hir-def 的 symbol；被依赖（入边，图谱共 48 条）——crate 内几乎全部功能模块（goto_definition/hover/references/rename/workspace_symbols/manifest/completion 引擎系列等）都从这里拿 `ScopeVisibility`/`Cancellable`，另有主 crate 的 `src/global_state/handlers/request/code_action.rs` 与 `src/global_state/protocol.rs` 直接 import 本文件。

**改动影响面**：改 `ScopeVisibility` 变体或 `Cancellable` 别名会波及 rename 闭包计算与全部 snapshot 方法的签名；调整模块可见性（如把 `semantic_target` 提为 pub）会改变外部可触达面并牵动全部 in-crate 引用路径；删除再导出项会直接断主 crate（src/global_state.rs 一线）编译。

**集成点**：二开者新增 IDE 功能的标准路径——在 L12-52 加 `pub mod` 声明；需要位置参数的新功能复用 `FilePosition`/`FileRange`/`RangeInfo`（L9）而非自造坐标类型。

---

## `crates/ide/src/db/apply_change.rs`（20 行）

**角色**：`RootDb` 的写端入口——把一次 VFS/配置变更原子地灌入 Salsa，并先请求取消所有在飞查询。

**关键结构与不变量**：
- `request_cancellation`（L9-13）：调用 `self.synthetic_write(Durability::LOW)` 触发 salsa 取消。注释钉版的关键不变量：**synthetic_write 会阻塞等待所有 snapshot 被丢弃，若此时持锁等 snapshot 会死锁**——这是全 IDE 并发模型的基石约束（analysis_host 测试 `concurrent_snapshot_drop_unblocks_input_invalidation` 专门验证该路径）。
- `apply_change(&mut self, change: Change)`（L15-19）：固定顺序——先 `request_cancellation()`，`tracing::trace!` 记录，再 `change.apply(self)`。**先取消后应用**保证不会有旧查询把新输入算进缓存。
- `change.apply`（base-db/src/change.rs L35 起）按 Durability::HIGH 写 project_config/source_root/file_kind 与文件内容——本文件不含自己的状态。

**公开 API**：`RootDb::request_cancellation(&mut self)`；`RootDb::apply_change(&mut self, change: Change)`。

**依赖/被依赖**：依赖 base-db 的 change.rs（`Change::apply` 调用边）与 crate::db::root_db；被依赖（入边）0 条——但 `AnalysisHost::apply_change`（analysis_host.rs L24-27）与全部测试基建（test_utils、diagnostics tests 的 `db.apply_change`）经 `RootDb` 方法语法消费它（方法调用不产生 imports 边）。

**改动影响面**：改变"先取消后应用"顺序会造成 salsa 缓存被旧查询污染（正确性 bug）；把 synthetic_write 换成普通 set_input 会在长查询在飞时丢失取消语义，LSP 端表现为输入延迟；此文件是所有测试 `db_with_files*` helper 的隐式依赖。

**集成点**：任何想往 RootDb 写新输入（如未来增加配置面）的扩展，应继续走 `Change` 结构化批量提交而非散装 set，以保住原子性与取消语义。

---

## `crates/ide/src/db/line_index_db.rs`（23 行）

**角色**：IDE 层第一个自有 Salsa 查询——`FileId → Arc<LineIndex>`（UTF-8 offset ↔ line/col 换算的缓存层）。

**关键结构与不变量**：
- `pub trait LineIndexDb: SourceDb`（L8-16，`#[salsa::db]`）：默认方法 `fn line_index(&self, file_id) -> Arc<LineIndex> where Self: Sized`——**Sized 约束是必须的**：tracked 查询要具体数据库类型；dyn 对象经 root_db.rs 的 Deref 链绕开此限制。
- `#[salsa::tracked(lru = 256, returns(clone))] fn line_index(db, key: SourceFileQueryKey)`（L18-23）：输入用 `SourceFileQueryKey`（db.rs L8-12 的 `salsa::interned` 包装，注释说明 Salsa 0.28 tracked 函数要求 salsa-struct 参数，`FileId` 是裸整数必须 intern）；不变量：**LineIndex 永远由当前 `file_text` 派生**，文本变更自动失效重算，任何手工缓存行索引都是错的。
- LRU=256：编辑器热文件集规模的可调参数。

**公开 API**：trait `LineIndexDb`（含默认方法 `line_index`）。

**依赖/被依赖**：依赖 base-db（salsa/SourceDb）、db.rs（SourceFileQueryKey）、utils/line_index、vfs；被依赖（入边 5 条）——`analysis.rs`（snapshot 的 line_index）、`folding_ranges.rs`、`formatting.rs`、`render.rs`（offset→位置渲染）与 `root_db.rs`（impl 块注册）。

**改动影响面**：改 LRU 容量影响内存/重算平衡；把 `returns(clone)` 换掉会让每次查询走 interner 拷贝；动 `SourceFileQueryKey`（db.rs）会同时打断 db.rs 注释里强调的"唯一 tracked 化 FileId"设计。

**集成点**：新增"从文件文本派生的便宜索引"类查询（如缩进表、括号配对表）的样板模板——interned key + tracked(lru) + returns(clone) 三件套照抄即可。

---

## `crates/ide/src/db/root_db.rs`（92 行）

**角色**：全仓唯一的具体 Salsa 数据库类型——把 7 层 trait DB 装配成一个可 Clone 的 `RootDb`，IDE 一切查询的终点载体。

**关键结构与不变量**：
- `pub struct RootDb { storage: salsa::Storage<Self> }`（L19-21，`#[derive(Clone)]` + `#[salsa::db]` L17）：**clone 即 snapshot**——salsa Storage 的 clone 语义是冻结当前 revision 的只读视图，这是 AnalysisHost/AnalysisSnapshot 模型的物理基础。
- 7 个 `#[salsa::db] impl` 块（L24-45）：`salsa::Database`（L24）→ `SourceDb`（L27）→ `SourceRootDb`（L30）→ `PreprocDb`（L33）→ `HirDefDb`（L36）→ `TyDb`（L39）→ `LineIndexDb`（L42）→ `WorkspaceSymbolIndexDb`（L45）。trait 链层层叠加，RootDb 处于最顶。
- `impl fmt::Debug`（L47-51）手写空壳：避免打印 salsa Storage 内部（默认 derive 会 dump 巨量查询状态）。
- `FileLoader for RootDb`（L53-59）：`resolve_path` 用 anchor 文件的 source_root 做相对路径解析（`include` 解析的钩子），委托 `SourceRoot::resolve_path`。
- `RootDb::new(lru_capacity)`（L61-72）：三件 Durability::HIGH 输入初始化——files、diagnostics_config、project_config 全部给默认值；再 `update_parse_query_lru_capacity`。
- `update_parse_query_lru_capacity`（L74-78）：把容量分发给 preproc_expand 与 hir_def 两层 parse LRU；`DEFAULT_PARSE_LRU_CAP = 128`（L81）。
- `impl Deref for RootDb { type Target = dyn WorkspaceSymbolIndexDb }`（L86-92）：注释钉版意图——**不维护第二套转发方法**，直接 Deref 暴露 workspace 查询面；配合 workspace_symbol_index_db.rs 对 `dyn TyDb` 的 Deref 形成链式退化。

**公开 API**：`RootDb::new(lru_capacity: Option<usize>) -> RootDb`；`RootDb::update_parse_query_lru_capacity(&mut self, Option<usize>)`；`const DEFAULT_PARSE_LRU_CAP: usize = 128`；`FileLoader::resolve_path`；Deref 到 `dyn WorkspaceSymbolIndexDb`。

**依赖/被依赖**：依赖 base-db（diagnostics_config/project/source_db/source_root + salsa）、hir-def/db、hir-ty/db、preproc-expand/db、vfs（AnchoredPath/FileId）、crate 内 line_index_db 与 workspace_symbol_index_db；被依赖（入边多达 50 条）——ide crate 内几乎每个功能模块（diagnostics/definitions/goto_*/hover/references/rename/completion 引擎全部子模块/code_action 等）都 import RootDb 作参数类型，另有 db/apply_change.rs。

**改动影响面**：动 impl 块集合 = 动全 IDE 能力面（漏 impl 一个 trait db 编译即断）；`new()` 的三个 HIGH durability 默认值被所有测试与主 crate 启动路径依赖；Deref 目标换了会静默改变 `db.file_semantic_index(...)` 这类方法调用的解析结果（`src/global_state.rs` 直接持有 RootDb 场景）。

**集成点**：二开新增自己的 trait DB 层（如 lint 专属层）就照 L24-45 模式追加 `#[salsa::db] impl YourDb for RootDb {}`，一行接入即可被全链查询；LRU 容量是 IDE 内存调优的第一旋钮。

---

## `crates/ide/src/db/workspace_symbol_index_db.rs`（153 行）

**角色**：IDE 语义索引层的 trait 查询面——把 symbol/module/semantic 三种索引 + rename 闭包以方法形式挂到 `dyn WorkspaceSymbolIndexDb` 上，RootDb 经 Deref 免转发复用。

**关键结构与不变量**：
- `pub trait WorkspaceSymbolIndexDb: SourceRootDb + TyDb {}`（L17-18，`#[salsa::db]`）：本身无方法，纯粹是能力声明 + salsa 宏挂载点。
- `impl Deref for dyn WorkspaceSymbolIndexDb { Target = dyn TyDb }`（L21-27）：trait 对象间的 Deref——让 `dyn WorkspaceSymbolIndexDb` 的持有者不转型就能调 TyDb 层查询。
- `impl dyn WorkspaceSymbolIndexDb + '_`（L29-83）的 8 个方法全部是**非 salsa 薄转发**（对应自由函数 L85-153 无 `#[salsa::tracked]` 注解）——真正的 memoization 在底层 `for_source_root`/`for_file` 的调用链里由各构造函数内部逐文件查询承担，本层只提供统一入口。方法清单：`file_workspace_symbols`（L30）/`source_root_symbol_index`（L34）/`source_root_module_index`（L38）/`source_root_semantic_index`（L42）/`file_module_index`（L46）/`file_module_edges`（L50）/`file_semantic_index`（L54）/`recursive_rename_closure`（L75）。
- `workspace_source_root_ids`（L64-70）：每次现算 O(files) 的 root 列表（sort+dedup）；注释钉版理由——**底层 per-root 索引已 salsa-memoized，此处去重只花 O(files)，两个消费方（module_candidates/module_edges）共享一份实现**。
- `recursive_rename_closure(def, visibility, single_file)`（L75-82）：同名端口连接的连通分量，注释明确"一次 F2 交互只算一次"，被 rename 的 info/conflict/edit 三命令共享。
- `pub(crate) fn source_root_*_for_root`（L113-132）：给 semantic_index.rs 内部用的 crate 级直通版，绕过 dyn 方法分派。

**公开 API**：trait `WorkspaceSymbolIndexDb`；`dyn WorkspaceSymbolIndexDb` 上的 8 个 pub 方法（见上）；`workspace_source_root_ids() -> Vec<SourceRootId>`；`recursive_rename_closure(...) -> Arc<Vec<DefId>>`。

**依赖/被依赖**：依赖 base-db（source_db/source_root）、hir-def/def_id、hir-ty/db、vfs、crate::lib（ScopeVisibility）、semantic_index（六种索引类型）、workspace_symbols（SymbolIndex/WorkspaceSymbol）；被依赖（入边 10 条）——definitions/index_benchmarks/manifest/rename/module_resolution/semantic_index(.rs 与 /build.rs)/workspace_symbols/references/search 与 root_db.rs。

**改动影响面**：方法签名变更同步波及 semantic_index.rs 的 merge 与 build.rs 的 for_file 调用；`workspace_source_root_ids` 的排序稳定性被 module_resolution 的候选序依赖（去重后顺序影响歧义报告）；删 Deref impl 会迫使 root_db 补一套转发方法。

**集成点**：这是"给索引查询加新入口"的正位——新索引类型（如 class/program 索引）在此加方法 + 自由函数对，RootDb 自动经 Deref 获得，无需碰 root_db.rs。

---

## `crates/ide/src/analysis_host.rs`（145 行）

**角色**：写端句柄——独占持有 RootDb，负责 apply_change、诊断配置更新与 snapshot id 推进；rust-analyzer `AnalysisHost` 的 vide 对应物。

**关键结构与不变量**：
- `pub struct AnalysisHost { db: RootDb, snapshot_id: AnalysisSnapshotId }`（L9-12）：不变量——**db 只经 `&mut self` 方法变更，每次变更后 snapshot_id 必然 `next()`**（advance_revision L34-36）；`AnalysisSnapshotId`（base-db/src/analysis_snapshot.rs L10-11）是 u64 单调计数，checked_add 防溢出。
- `make_analysis(&self) -> AnalysisSnapshot`（L19-22）：`self.db.clone()`（salsa snapshot 语义）+ 当前 id。**同一状态多次 make 不产生新身份**（测试 `read_only_views_share_one_snapshot_identity` L131-144 断言 id 相同且从 0 起、空 Change 后变 1）。
- `apply_change(&mut self, change)`（L24-27）：`db.apply_change`（内部先 synthetic_write 取消）→ `advance_revision`。顺序保证读端看到的 id 永远对应一个完整应用完的 revision。
- `set_diagnostics_config`（L29-32）：Durability::HIGH 写配置 + 推进 id——配置变更也是"新世界"。
- 内嵌 3 个并发测试（L79-144）：`analysis_views_follow_input_revisions_after_snapshot_drop`（快照丢弃后失效生效）、`concurrent_snapshot_drop_unblocks_input_invalidation`（读写线程经 mpsc 协调，验证 apply_change 阻塞等 snapshot 释放不死锁）、`read_only_views_share_one_snapshot_identity`。测试基建 `change_with_file_text`/`modify_with_file_text`（L62-77）是 FileSet+SourceRoot::new_local+ChangedFile::create/modify 的最小样例。

**公开 API**：`AnalysisHost::new(lru_capacity: Option<usize>)`；`Default`（=new(None)）；`make_analysis(&self) -> AnalysisSnapshot`；`apply_change(&mut self, Change)`；`set_diagnostics_config(&mut self, Arc<DiagnosticsConfig>)`；`snapshot_id() -> AnalysisSnapshotId`；`raw_db() -> &RootDb`（测试/基准专用后门）。

**依赖/被依赖**：依赖 base-db（analysis_snapshot/change/diagnostics_config/source_db + Durability）、triomphe Arc、crate::analysis（AnalysisSnapshot）、db/root_db；被依赖（入边 11 条）——主 crate `src/global_state.rs`（LSP 状态机持有者）、crate 内 definitions/index_benchmarks/test_utils/verilog_2005/macro_hover_tests/semantic_tokens/document_highlight、completion/engine/tests、semantic_target/tests。

**改动影响面**：动 `advance_revision` 的调用时机会让 LSP 端（global_state 按 snapshot_id 判断诊断是否需要重推）漏推或重推；`raw_db` 是测试后门，收紧可见性会破坏 index_benchmarks。

**集成点**：二开集成 vide 到别的编辑器/CLI：持有一个 AnalysisHost，写线程 apply_change，读线程 make_analysis 拿 AnalysisSnapshot——这是唯一推荐姿势；`set_diagnostics_config` 是运行时开关诊断的入口。

---

## `crates/ide/src/analysis.rs`（338 行）

**角色**：读端门面——`AnalysisSnapshot` 把全部 IDE 功能（40+ 方法）统一为 `Cancellable<T>` 返回的薄委托，是 LSP handler 层与 ide crate 之间的全部边界。

**关键结构与不变量**：
- `pub struct AnalysisSnapshot { pub(crate) db: RootDb, pub(crate) snapshot_id: AnalysisSnapshotId }`（L45-49）：字段 crate 私有，**外部只能构造自 AnalysisHost::make_analysis**；snapshot 持有期间其 db 视图冻结（salsa clone 语义）。
- `with_db<F, T>(&self, f: F) -> Cancellable<T> where F: FnOnce(&RootDb) -> T + UnwindSafe`（L56-62）：全部方法的统一管道——进入 `tracing::debug_span!("ide.analysis", snapshot_id)` + `Cancelled::catch(|| f(&self.db))`。不变量：**任何 salsa 取消（改库时的 synthetic_write）都以 Err(Cancelled) 冒泡而非 panic**，调用方（LSP 层）重试即可。UnwindSafe 约束防闭包捕获可变借用跨 unwind。
- 输入/信息类方法（L64-142）：`line_index`/`file_text`/`file_ids`/`diagnostics`/`compilation_diagnostics`/`source_root_diagnostics`/`compilation_profile_diagnostics`/`parse_diagnostics`/`source_root_file_ids`/`source_root_role`/`source_root_id`/`file_compilation_profile`/`has_compilation_profiles`/`compilation_profile_ids`/`compilation_profile_file_ids`/`compilation_plan`——多 profile 编译（vide.toml）的完整查询面。
- 导航/编辑类方法（L144-338）：goto_definition/declaration、document_symbol、workspace_symbol（query+file_ids 过滤）、document_highlight、references、`module_incoming_calls`/`module_outgoing_calls`（call hierarchy，L187-201，走 semantic_index 的 ModuleCallEdge）、rename 全家（prepare_rename/rename/rename_expansion_info/expanded_rename/rename_conflict_info，L203-245）、format/format_on_type（带 CancellationToken，L247-271）、selection_ranges、folding_ranges、hover、inlay_hint、code_lens(+resolve)、semantic_tokens、signature_help、`completions_with_trigger`（L319，Option<TriggerChar>）、`code_action`（L327-337，带 diagnostics 切片 + resolve_strategy 延迟解析）。

**公开 API**：`AnalysisSnapshot` 的 40+ pub 方法（全部 `Cancellable<T>`）；`snapshot_id()`（L52）。

**依赖/被依赖**：依赖（52 条出边）base-db 四模块、preproc_expand（CompilationPlan）、utils 四模块（cancellation/line_index/lines/text_edit）、vfs 与 crate 内 20+ 功能模块（db/diagnostics/goto_*/hover/references/rename/...）；被依赖（入边仅 2 条）——lib.rs 与 analysis_host.rs：**刻意收窄为唯一构造路径**，LSP 层经 `global_state.rs → AnalysisHost → make_analysis` 间接到达。

**改动影响面**：任何方法签名变更直接冲击主 crate `src/global_state/handlers/request/*` 全部 handler；`with_db` 的 span 名被 tracing 侧采集逻辑匹配；漏掉 Cancelled::catch（新方法绕过 with_db）会把取消变成 panic 打穿 LSP 线程。

**集成点**：新 LSP 功能的标准落点——功能模块写自由函数 `fn xxx(db: &RootDb, ...) -> T`，这里加一行 `self.with_db(|db| xxx::xxx(db, ...))` 对外即成；`code_action` 的 `CodeActionResolveStrategy` 与 `completions_with_trigger` 的 trigger 参数是延迟计算/触发字符两类 LSP 交互范式的现成样板。

---

## `crates/ide/src/diagnostics.rs`（1308 行；主代码 L1-561 + 测试 L563-1308）

**角色**：诊断总管道——把 slang parse、slang semantic（经 compilation）、HIR lowering、Vide 自研四类来源统一成 `Diagnostic` 结构，并实现来源间抑制（去重）与 per-root 诊断域（scope）控制。

**关键结构与不变量**（8 个核心 + 测试模块）：
- 4 个 `VideDiagnosticDescriptor` 常量（L17-24）：`AMBIGUOUS_MODULE_INSTANTIATION`(code 1)/`INACTIVE_PREPROCESSOR_BRANCH`(2)/`LOWERING_INVALID_SYNTAX`(3)/`LOWERING_UNSUPPORTED_SYNTAX`(4)，全部 subsystem 0；配对的 option_name 常量字符串 L25-29（`"diagnostic.ambiguous_module.strict"` 等）是配置文件键。
- `pub enum DiagnosticSource { SlangParse, SlangSemantic, Vide }`（L31-36）：诊断溯源三分类，LSP 端据此决定呈现与 quick-fix 挂钩。
- `pub struct Diagnostic`（L38-54）：15 字段——file_id/code/subsystem/name/option_name/groups/source/range/severity/message/args/`message_key: Option<&'static str>`/message_args/tags。不变量：**slang 来源的 message_key 恒 None（保留原文），Vide 来源恒 Some（支持 i18n/参数化重渲染）**；args 是 slang 位置参数（见 expected_token）。
- `Diagnostic::expected_token`（L70-76）：parse `ExpectedToken` 诊断的 args[0] 即期望 token——注释钉版**位置性假设**：升级 slang 若 args 布局变了，`insert_expected_token` quick-fix 会静默插错 token，升级时必须回归该测试。
- `VideDiagnosticProvider` trait（L285-293）+ `vide_providers()` 注册表（L295-301）：`InactivePreprocessorBranch`/`AmbiguousModuleInstantiation`/`LoweringSyntaxDiagnostics` 三 provider；**新增 Vide 检查=新类型+一行注册**；`active()` 默认 true，`AmbiguousModuleInstantiation` 覆写为 `!slang_semantic_diagnostics_active(db, file_id)`（L499-502）——slang 语义诊断在场时自抑制（测试 `semantic_diagnostics_suppress_vide_ambiguous_module_warning` L789 验证）。
- 抑制规则一（lowering vs parse）：`lowering_diagnostic`（L343-382）对 `InvalidSyntax` 若 range 与任一 parse 诊断重叠（`ranges_overlap` L384）则丢弃——"解析器已画波浪线，lowering 恢复注记不叠床架屋"；但 parse 诊断可配置关闭，此时注记降级保留（测试 `lowering_invalid_syntax_reports_note_when_parse_diagnostics_disabled` L1218）。`UnsupportedSyntax` 是 Warning（合法 SV 但 vide 未 lower，用户唯一信号）。
- 抑制规则二（位置缺失）：`to_text_range`（L540-561）——`primary_range` 优先，退 `location`（空 range），两者皆无则**丢弃**该 slang 诊断并 debug 日志（不发布到文件头，测试 `unlocated_slang_diagnostics_are_not_published_at_file_start` L1280）。usize→u32 转 TextSize 失败同样丢弃。
- 诊断域门控 `diagnostics(db, file_id)`（L235-248）：root role 的 `diagnostic_scope() == Disabled` **且** workspace 有 compilation profiles → 返回空（注释：无 profile 的 workspace 对 ad-hoc 文件仍给 open-file 语法诊断）；`source_root_diagnostics`（L250-262）三分支 Disabled/OpenFile/Workspace——Workspace 分支 flat_map 整个 root；`vide_diagnostics_enabled`（L315-317）看 `diagnostics_config().enabled` 总闸。
- 宏定位：`module_instantiation_resolution_diagnostics`（L396-456）对宏生成的实例化，经 `preproc_expand::preproc::diagnostic_target_for_range` 把 range 重定向到宏体（target 有则改 file+range；`covered` 无 target 则跳过；Err 则 warn 跳过）——测试 `preproc_macro_generated_instantiation_diagnostic_uses_macro_body_target` L734 验证报在宏体的 `child` 而非 `` `MAKE ``；歧义严重度二分（`ambiguous_module_instantiation_diagnostic` L509-538）：Strict=Warning、BestEffortTie=Note。
- 其余管道函数：`parse_diagnostics`（L159-167，manifest 文件分流到 crate::manifest::diagnostics）；`compilation_diagnostics`（L169-174）；`compilation_profile_diagnostics`（L176-193，slang 编译诊断 + 全 profile 文件的 Vide 诊断合并）；`slang_diagnostic`（L208-233）SyntaxDiagnostic→Diagnostic 的字段搬运。
- 测试模块（L563-1308，17 个测试 + 快照）：覆盖 best-effort/strict 歧义、宏定位、profile 合并、inactive branch（含 `else` 分支标记 L850 与总闸 L864）、跨文件语义归属（`semantic_diagnostics_include_other_workspace_files` L880：未连接端口报在 top.sv 而非 child.sv）、include 头文件归属（L1000-1050）、传递 include（L1092-1150）、`include_only` 计划语义（L1048）、lowering 快照（insta `lowering_diagnostics_lsp_snapshot` L1244）。跑法：`cargo test -p ide diagnostics`。

**公开 API**：`Diagnostic`/`DiagnosticSource`/`DiagnosticTag`；`Diagnostic::expected_token`（pub(crate)）；pub(crate) 函数 `parse_diagnostics`/`compilation_diagnostics`/`compilation_profile_diagnostics`/`diagnostics`/`source_root_diagnostics`/`source_root_file_ids`/`source_root_role`。

**依赖/被依赖**：依赖 base-db（diagnostics_config/project/source_db/source_root）、hir-def/source_map（LoweringDiagnostic）、syntax/diagnostics（DiagCode/Severity/SyntaxDiagnostic）、utils/text_edit、vfs、crate 内 db/root_db 与 module_resolution；被依赖（入边 9 条）——code_action.rs 与 code_action/{action,diagnostics,collector,context,engine}.rs（quick-fix 消费 Diagnostic）、manifest.rs、lib.rs、analysis.rs。

**改动影响面**：`Diagnostic` 字段集是 LSP 序列化层（主 crate protocol）的镜像契约；suppress 规则改动会直接改变用户看到的波浪线集合（有 insta 快照钉着 lowering 面）；provider 注册表顺序影响诊断输出顺序；`expected_token` 的 args[0] 假设与 slang-sys 升级强耦合。

**集成点**：新 Vide 检查的唯二落点——实现 `VideDiagnosticProvider`（`active` + `diagnostic`）并加进 `vide_providers()`（L295）；option_name 常量模式（L25-29）让每条 Vide 诊断天然可被 vide.toml 单独开关。

---

## `crates/ide/src/semantic_index.rs`（854 行；主代码 L1-455 + 测试 L457-854）

**角色**：语义索引的数据结构层与 source-root 合并层——定义 DefId→引用组、模块定义表、模块调用图三类索引及 per-file/per-root 两级形态；references/rename/call-hierarchy 全部从这里取数。

**关键结构与不变量**（11 个核心）：
- `SemanticDefinitionRange { file_id, range }`（L28-32，pub(crate)）：定义名出现点（一个 DefId 可多 origin，故是列表）。
- `ReferenceContext`（L49-75，pub(crate) enum）：Plain / `ConnName { ident_range, collapse_range, shorthand, side, paired }` / `ConnData { name_range, collapse_range, paired }`——**命名端口连接的形状在建索引时一次性算死**（注释 L42-48：rename 等消费方永不重解析）；`paired` 语义钉版：同名连接（`.name` 与数据标识符同文本）时，name 侧配对局部定义、data 侧配对端口定义；`ConnSide { Port, Local }`（L34-40）标记 `.name` 简写连接归属哪一侧（简写 `.b` 在端口组与局部组各生成一条引用）。
- `SemanticReference`（L90-97）：file_id+range+category（ReferenceCategory 读/写分类）+`ptr: SyntaxTokenPtr`+context；`SemanticReferenceGroup`（L99-104）：name+definition_ranges+references。
- `ModuleIndex`（L130-133）：`FxHashMap<Ident, Box<[SemanticModuleDefinition]>>`——同名模块多定义（歧义源）。
- `SemanticIndex`（L135-140）：`references_by_definition: FxHashMap<DefId, SemanticReferenceGroup>` + `incoming_module_edges`/`outgoing_module_edges: FxHashMap<OwnerId, Box<[ModuleCallEdge]>>` 三个 map。
- `FileSemanticIndex`（L144-147）：per-file 切片（只有 groups，无跨文件 definition_ranges——那是 merge 时算的，L142-143 注释）；`FileModuleIndex`（L162-165）/`FileModuleEdges`（L169-172，`Vec<(OwnerId, OwnerId, ModuleCallEdge)>` 双 id 让 merge 能同时建 in/out 两 map）。
- `ModuleIndex::for_source_root`（L183-226）：遍历 root 全部文件 + **`macro_files_for_file` 展开的宏文件**（L191-197 收集 HirFileId::File+Macro 后 sort+dedup），取 `item_tree().module_headers()` 中 `kind().is_instantiable()` 的头；同名组内按 (file_id.index, name_range.start) 排序并按 module_id 或同文件同 range dedup（L216-221）——**输出顺序确定性**是歧义报告可复现的前提。
- `SemanticModuleDefinition::from_header`（L256-269）：经 `db.source_projection(...).origin(...)` 与 `nav_location` 把 HIR 侧位置投影回用户可见文件（宏展开→调用点的关键一步）；name_range 缺省回落 full_range。
- `SemanticIndex::for_source_root`（L286-325）：注释钉版——**merge 是纯内存组装，不做任何名字解析**，因此单文件变更只重跑该文件的索引+此遍。循环内 `db.unwind_if_revision_cancelled()`（L299）是 merge 长循环的取消检查点（salsa Database 方法）。definition_ranges 首见该 DefId 时经 `definition_ranges_for`（build.rs）惰性计算。
- 查询入口 `incoming_module_edges`/`outgoing_module_edges`（L358-372）→ `module_edges`（L374-391）：file_id+name_range 先经 `module_id_at_range`（L393-396）定位 OwnerId，再**跨全部 workspace source root** 聚合（`db.workspace_source_root_ids()`），`sort_and_dedup_edges`（L440-451，五元组排序键）保证稳定输出——call hierarchy 跨 root 也成立。
- `instantiation_name_range`（L398-420）：从实例化 range 内扫出第一个 name-like token（作为 call_range 的名字锚）。
- 测试模块（L457-854，4 个测试）：`container_stack_matches_find_container_for_every_token`（ContainerCache 与 find_container 全 token 一致性——含宏展开出"同显示 range 两个不同节点"的断言 L523-530）、`fast_path_agrees_with_full_resolution_chain_for_every_token`（快慢路径全 token 一致性，>20 token 门槛）、`reference_contexts_capture_named_connection_shapes`（同名/异名/简写三类连接的形状与配对逐项断言）、`semantic_index_skips_preprocessor_owned_identifiers`（宏参数/宏体标识符归属预处理器，不进 HDL 引用组）。跑法：`cargo test -p ide semantic_index`。

**公开 API**：pub 类型 `ModuleCallItem`/`ModuleCallEdge`/`ModuleIndex`/`SemanticIndex`/`FileSemanticIndex`/`FileReferenceGroup`（`references()` L156）/`FileModuleIndex`/`FileModuleEdges`；pub(crate) 自由函数 `incoming_module_edges`/`outgoing_module_edges`（L358/L366）与类型 `SemanticDefinitionRange`/`ConnSide`/`ReferenceContext`/`SemanticReference`/`SemanticReferenceGroup`/`SemanticModuleDefinition`；`mod build`（L25）私有。

**依赖/被依赖**：依赖（82 条出边，文件级）base-db、hir-def（container/def_id/item_tree/owner）、hir-ty/db、preproc-expand（file/macro_file）、rustc-hash、syntax（TokenKind/SyntaxTokenPtr/HasTextRange）、utils、vfs，crate 内 db 两模块/navigation_target/references/token；被依赖（入边 6 条）——db/workspace_symbol_index_db（查询面挂载）、index_benchmarks、lib.rs、analysis.rs（call hierarchy）、rename.rs、references/search.rs。

**改动影响面**：`ReferenceContext` 字段集被 rename 的编辑规则按位消费（collapse_range 生成折叠编辑、paired 生成递归闭包）；`SemanticIndex::for_source_root` 的"无名字解析"约束一旦破坏，增量失效粒度从单文件退化为全 root；edge 排序键改动会让 call hierarchy 顺序与快照测试漂移。

**集成点**：新的"跨文件引用类"功能（如 find all instances of parameter）应挂 SemanticIndex 而非自己扫 AST；`ModuleIndex::module_definitions(name)`（L228-230）是模块名→多定义歧义处理的现成查询；`FileSemanticIndex::for_file`/`FileModuleEdges::for_file`（build.rs）是接入自定义 per-file 索引的对接缝。

---

## `crates/ide/src/semantic_index/build.rs`（849 行）

**角色**：索引构建引擎——单文件一遍 AST 遍历产出 FileSemanticIndex/FileModuleIndex/FileModuleEdges；内含两个决定性能的缓存（容器缓存、作用域链缓存）与快慢双路径名字解析。

**关键结构与不变量**（11 个核心）：
- `FileSemanticIndex::for_file`（L43-149）：主循环 `root.elem_preorder()` 只处理 name-like token；`has_preproc_tokens` 判定（L51-58）看 preprocessor_trace 的 include_edges 或非 Source origin 的 emitted token——**注释钉版：普通源 token 也带 trace 条目，所以不能按 trace 大小判定**；有预处理 token 才构建 `emit_token_index`，此后每个 token 先过 `resolve_semantic_target_with_emitted(...).unique_for_intent(FindReferences)`，非 `SemanticTarget::Source` 即跳过（预处理器拥有的标识符不进 HDL 索引）；`target.into_tokens()` 可一对多（宏展开），逐 token `collect_token`。
- `IndexBuildTrace`（L152-242）：`VIDE_INDEX_BUILD_TRACE` 环境变量开启的分段计时（range/source_target/container/collect/resolve fast·slow/chain/nameres/definition + 10 类语法节点命中计数）——性能回归排查的唯一仪表盘。
- `ContainerCache<'tree>`（L261-302）：`FxHashMap<SyntaxNode, OwnerId>`。三条钉版不变量：①分派必须与 `hir_semantics::source_to_def::container_to_def` 镜像同步（模块/block/子程序走公共 Semantics 投影，generate 块经 intern_generate_block 以最近容器为父）；②**key 是 Slang 节点本体而非 SyntaxNodePtr——宏展开节点可共享显示 range/kind 但指针身份不同**；③`container_for`（L273-287）沿祖先链找第一个成功 lower 的容器节点，兜底 `owner_table(file_id).file_owner().expect("file owner")`。
- `is_container_node`（L336-348）：容器节点判定 11 类（Module/AnonymousProgram/Checker/Covergroup/Clocking/BlockStatement/ProceduralBlock/Function/CompilationUnit/GenerateBlock/generate-branch Member）。注释钉版：**必须用 `cast` 不能 `can_cast`**——slang 的 can_cast 接受子类关系（generate 块过 BlockStatement::can_cast），会打乱 bookkeeping。
- `container_id_for_node`（L350-394）：各节点类型→OwnerId 的分派；特例：LoopGenerate 下的 GenerateBlock 用**父节点**（LoopGenerate 本身）当 owner_node 再查 ast_id_map（L383-390）。
- `ScopeChainCache`（L309-330）：`FxHashMap<OwnerId, Arc<ResolvedScopes>>`。注释钉版动机：**per-token 的 salsa `scope_for` 查询会因 memo 对每次中间查询重验证并在 miss 时重算 O(scope size)**，改为每容器解析一次作用域链。
- `collect_token`（L405-524）：快慢双路径——`in_special_context` 走 `DefinitionClass::resolve_in`（慢，L425），否则 `nameres_ident_in_scopes_at`（快，L441-444，用 ScopeChainCache 的链）；结果两类：`Definition` 单引用入组，`PortConnShorthand { port, local }` **双侧各生成一条引用**（L480-521，分别带 ConnSide::Port/Local 的 context）。
- `token_in_special_context`（L703-732）：快慢路径分界谓词，全部 O(1) parent/grandparent 检查——MemberAccess 的 name、ModuleHeader 的 name、Primitive/HierarchyInstantiation 的 type、PackageImportItem 的 package/item、NamedParamAssignment/NamedPortConnection 的 name，以及 Name 节点挂在 ScopedName/NamedType/CheckerInstantiation 下的情形。注释记录了**旧版 subtree-walk 门被废弃的原因**（module body 内全部 token 被误标，快路径在 module 重的文件上变死代码）——与 semantic_index.rs 测试 `fast_path_agrees_with_full_resolution_chain_for_every_token` 互为安全网。
- 连接形状提取：`conn_token_role`（L535-552，data 标识符在连接节点下**固定第 3 层祖先**，因包装表达式节点是虚拟的）；`conn_data_ident`（L557-569，裸名或空 select 才算"简单标识符"）；`conn_shape`（L578-587，collapse_range=name 起点到 close_paren 终点；shorthand=无 open+close paren）；`is_same_name_conn`（L593-596，按源文本比对）；`reference_context`（L602-688）组装 ReferenceContext——同名连接时 name 侧查 `conn_port_by_name`（L69 的 `FxHashMap<TextRange, DefId>`，**利用 name token 先于 data token 出现的源序**，L67-68 注释）拿到 data 侧配对；简写单侧解析时用 nameres 判 Local/Port（L642-650）。
- `collect_definition_token`（L735-776）：定义站点判定——`definition_ranges_for` 里含 (file_id, range) 精确匹配则**不入引用组**（定义≠自引用）；引用按 (file_id, range) 去重后入组。
- `definition_ranges_for`（L780-794，pub(super)）：`DefId.origins(db)` 各 origin 的 name_range 经 `resolve_source_range`（references/search）投影到用户文件，unique 保序——**被 SemanticIndex::for_source_root 的 merge 复用**（semantic_index.rs L305），文件级调用方负责 memoization。
- `FileModuleIndex::for_file`（L797-807）/`FileModuleEdges::for_file`（L810-849）：模块头同 ModuleIndex 逻辑的 per-file 版；edges 遍历 `body_with_source_map(caller)` 的 instantiations，经 `resolve_hir_instantiation_target`（module_resolution）解析被调方，call_range 用 `instantiation_name_range` 收敛到名字 token。

**公开 API**：本文件全部 pub(super)/pub(crate) 级（`ContainerCache::new/container_for/try_id_for`、`ScopeChainCache::new/chain_for`、`token_in_special_context`、`definition_ranges_for`、三个 `for_file`）——只服务 semantic_index.rs 与其测试，无 crate 外可见性。

**依赖/被依赖**：依赖 hir-def（container/def_id/owner/pathres/symbol）、hir-semantics/semantics（SemanticsImpl + `is_generate_branch_member`）、itertools、preproc-expand/file、rustc-hash、syntax 全家（SyntaxAncestors/WalkEvent/ast/ptr/TokenKindExt/has_text_range）、triomphe、utils、vfs，crate 内 db/workspace_symbol_index_db、definitions、module_resolution、references(.rs 与 /search.rs)、semantic_target(.rs 与 /preproc.rs)；被依赖（入边 1 条）——semantic_index.rs（`mod build;` + `use build::definition_ranges_for`）。

**改动影响面**：`is_container_node`/`container_id_for_node` 与 hir-semantics 的 `container_to_def` 是**人工镜像同步**关系——一侧改动必须同步另一侧（一致性测试 `container_stack_matches_find_container_for_every_token` 是唯一防线）；`token_in_special_context` 与 `DefinitionClass::resolve_in` 的启发式链同理（`fast_path_agrees...` 测试防线）；`conn_port_by_name` 的"name 先于 data"源序假设若被未来语法（如反向连接）打破，配对会静默丢失；`definition_ranges_for` 改动同时影响 merge 层的组头。

**集成点**：索引性能调优从 `IndexBuildTrace` + `VIDE_INDEX_BUILD_TRACE` 起；给索引新增引用类别（如新 ReferenceContext 变体）在此扩展 `reference_context` + semantic_index.rs 的 enum；新容器类型接入照 `is_container_node` + `container_id_for_node` 双处镜像模式。

---

## 附注

- `crates/ide/src/semantic_index/` 目录下只有一个 `build.rs`（git ls-files 证实），不是独立子 crate——此前目录列表中的 `Cargo.toml`/`src` 属于上一条 `ls crates/ide/` 的无标题输出。
- `db.rs`（18 行，属 12 号或相邻单元）定义 `SourceFileQueryKey`（`#[salsa::interned(unsafe(no_lifetime), revisions = usize::MAX)]`，L8-12）并 re-export 本单元四个 db 子模块；其注释钉版"全 ide 其余函数均 untracked 直接收 FileId"是理解本单元只有 line_index 一个 tracked 查询的钥匙。
