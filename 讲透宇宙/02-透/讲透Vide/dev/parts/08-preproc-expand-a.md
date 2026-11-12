# 08-preproc-expand-a 精读手册

> 模块定位：本单元是 `preproc-expand` crate 的主体（Salsa 查询层+宏展开层）。在 vide 三层架构（base-db VFS/SourceRoot → preproc-expand 预处理/解析/宏展开 → hir-def/hir-semantics 语义）中，它位于**第一语义数据库层**：持有 `PreprocDb` trait（slang 解析、编译计划、诊断、宏展开的全部 salsa query），把 slang 的预处理 trace 翻译成 VFS FileId+TextRange 世界，并为 IDE 层提供 `HirFileId`（真实文件 vs 宏展开虚拟文件）这一统一文件抽象。crate 铁律（lib.rs L1-7 doc）：只准依赖 `base-db` 与纯模型 crate `preproc`，禁止依赖 lower 层（hir-def/hir-semantics），也不得把底层 crate 当兼容命名空间 re-export——这保证 `base-db -> preproc-expand` 依赖在 Cargo 上不可能（db.rs L416-420 注释）。

---

## `crates/preproc-expand/Cargo.toml`（18 行）【配置】

**作用**：声明 crate `preproc-expand` v0.0.0、edition 走 workspace（2024）。依赖面刻意收窄：`base-db`（RootDb 基座）+ `preproc`（slang trace 纯模型）+ `syntax`（slang 绑定：SyntaxTree/Trace/TokenOrigin）+ `salsa`（增量查询）+ `vfs`/`utils`/`rustc-hash`/`smol_str`/`triomphe`（基础设施）+ `toml`/`toml_parser`（manifest 解析，供 predefines 源信息）+ `tracing`。
**关键字段**：`preproc.workspace = true`（L8）是分层关键——纯 trace 模型与本 crate 的 Salsa 胶合层分离；无任何 dev-dependencies（测试全用内部 TestDb）。
**改动连带**：新增依赖若引入 hir-def/hir-semantics 会破坏 lib.rs L1-7 声明的分层铁律（ide/hir 层反向依赖会成环）；workspace root Cargo.toml L22（成员）、L42（vide 主程序直接依赖）、L86（workspace.dependencies 定义）三处引用此 crate。

## `crates/preproc-expand/src/lib.rs`（15 行）

**角色**：crate 门面，仅声明 6 个公开模块 + 分层契约文档。
**关键结构与不变量**：无类型。不变量即 doc 注释（L1-7）：本 crate 拥有 `PreprocDb`、编译计划、源预处理集成、宏文件、展开 source map、宏引用索引；"may depend on base-db and the pure preproc model, but must not depend on lowered definitions or semantic types"。
**公开 API**：`pub mod compilation_plan / context / db / file / macro_file / preproc / source_db`（L9-15）。
**依赖/被依赖**：无 imports 出边；入边=vide 主程序 `src/global_state/qihe.rs`（+其 tests）与两个 Cargo.toml（configures 边）。
**改动影响面**：模块增删直接改变 crate 公开面；删除任一 re-export 会瞬间破坏 ide/hir-semantics/主程序三方编译。
**集成点**：二次开发新功能应挂靠现有模块而不是新建顶层 mod，保持 6 模块边界。

## `crates/preproc-expand/src/db.rs`（1511 行）

**角色**：本 crate 的核心——`PreprocDb` trait 定义 + 全部权威 salsa query（slang 解析、profile 编排、诊断映射、宏展开入口）+ 一半篇幅的内嵌测试（L782-1511）。

**关键结构与不变量**：
- `PreprocFileQueryKey`（L41-45）/`PreprocProfileQueryKey`（L47-51）：`#[salsa::interned]` 包装。不变量（L37-40 注释）：Salsa 0.28 tracked fn 要求 salsa-struct 参数，`FileId`/`Option<CompilationProfileId>` 是裸整数，必须经 interned 包装才能当 tracked key；untracked fn 直接收裸类型。
- `CompilationDiagnostic`（L53-60）：诊断+`file_id` 归属+`DiagnosticSource`（Parse/Semantic）。不变量：file_id 是 buffer→VFS 映射**成功后**才填的，映射不到的诊断不进结果（计数后丢弃，L662-664）。
- `ParsedCompilationUnit`（L62-66）：`syntax_tree`+`preprocessor_trace: Option<Trace>`；LibraryMap/ProjectManifest 无 trace（L232-239）。
- `ParsedProfile`/`ParsedProfileUnits`（L68-73）：`(FileId, ParsedCompilationUnit, SyntaxTreeBufferIds)` 三元组数组——FileId 是编译根，buffer_ids 用于诊断反查映射。
- `parsed_compilation_unit` query（L172-241，lru=128）：**核心不变量**——若 file 在 `plan.roots` 里，直接从 `parsed_profile` 权威解析复用同一棵 SyntaxTree（L177-194，找不到则 panic "missing from authoritative parse"）；非根文件才独立 parse（`SyntaxTree::from_file_in_memory_with_options_and_trace` L221）。
- `parsed_profile` query（L243-308，lru=128）：建 `Compilation::new_with_top_modules` session（L258），先 `register_source_buffers`（L259，保证 `include buffer 先注册再解析宏 include`——测试 L1002 钉版）再逐根 parse；IncludeHeader/ProjectManifest 出现在 roots 中直接 panic（L282-284）。
- `parser_expected_syntax` query（L328-363，lru=64）：completion-only 期望信息**不进权威树**（L322-327 注释），cursor 处独立 parse；LibraryMap 走专门入口（L339-351）。
- `PreprocDb` trait（L420-421）：`#[salsa::db] pub trait PreprocDb: SourceRootDb {}`，全部查询以 `impl dyn PreprocDb + '_` 固定方法暴露（L423-542）。
- `parse_diagnostics`（L373-414）：只保留 root buffer 的诊断（`diag.buffer_id` 非根即丢，L395-397），再过 `config.apply_rules`。
- `compilation_profile_diagnostics`（L603-631）+`compilation_diagnostics_from_compilation`（L633-731）：profile 级 parse+semantic 诊断批量收集；`insert_buffer_file_ids`（L99-111）用 `path_file_ids`（L87-97，跳过 project-ignored）路径对账建立 slang buffer_id→FileId。
- 测试模块（L782-1511）：内嵌 `TestDb`（salsa::Storage+四 trait impl+Deref 到 `dyn PreprocDb` L818-847），关键测试：`root_scoped_compilation_units_reuse_the_authoritative_parse`（L1019）、`profile_registers_root_buffers_before_macro_include_resolution`（L1002）、`parser_expectations_are_cursor_scoped_outside_authoritative_tree`（L990）、`source_preproc_mapping_records_predefines_by_verified_source_text`（L1156，predefine 虚拟源只显示不可映射）、`preproc_virtual_paths_use_reserved_namespace`（L1505，`/__vide/preproc/...` 保留命名空间）。

**公开 API**：`PreprocDb`、`CompilationDiagnostic`、`ParsedCompilationUnit`、`ParsedProfile`、`CompilationProfileDiagnostics`、`set_parse_lru_capacity(db, capacity)`（L316-319，调 parsed_profile/parse_src_for_compilation 两个 query 的 `set_lru_capacity`）；`dyn PreprocDb` 上的 18 个方法（compilation_plan_for_root/for_profile、compilation_context(_for_file)、parsed_compilation_unit、parsed_profile、parse、parse_diagnostics、file_compilation_diagnostics、semantic_diagnostics、source_root_semantic_diagnostics、macro_expansion、trace_index、file_macro_coverage、macro_reference_index_for_profile、parser_expected_syntax、source_preproc_model 系列）。

**依赖/被依赖**：依赖→`compilation_plan`、`context`、`file`、`macro_file`、`preproc`、`source_db`（本 crate 全部兄弟模块）+ base-db（CompilationContext/DiagnosticsConfig/SourceRootDb）+ syntax（slang）+ vfs/utils/triomphe。被依赖→ide（semantic_index、semantic_target、db/root_db）、hir-semantics（preproc_integration_tests）、hir-ty/tests、本 crate file/macro_file/context/preproc/source_db——是整个 ide 层的基座 query 集。

**改动影响面**：任何 query 签名变化波及 ide/hir-semantics 全部调用点；`parsed_compilation_unit` 的"根复用权威解析"不变量被破坏会导致同一文件出现两棵不同树→语义与诊断不一致；删除 `PreprocProfileQueryKey` 的 interned 包装会让 salsa 编译失败；`set_parse_lru_capacity` 与 LRU 数值（128/64/32）影响大仓内存行为。

**集成点**：新 salsa query 的标准姿势=写 tracked fn + interned key + 在 `impl dyn PreprocDb` 加薄包装（L423-542 模式）；测试直接复用内嵌 TestDb 的四 trait derive 模式。

## `crates/preproc-expand/src/compilation_plan.rs`（403 行）

**角色**：编译计划——决定"哪些文件是语义根、哪些只是 include 供给、include 目录/predefine/top module 是什么"，是 slang 解析的输入编排器。

**关键结构与不变量**：
- `CompilationPlan`（L17-29）：`roots`（语义编译根）与 `include_only`（L21-24 注释：仅经字面 `include` 指令到达的文件，喂给 slang 当 include buffer，**不作为独立语义根**）严格分离；`include_scan_issues` 记录扫描期失败。
- `all_file_ids`（L45-51）：roots+include_only 按 FileId.index 排序去重——稳定顺序不变量。
- `is_include_header_in_include_paths`（L55-64）：kind==IncludeHeader 且路径在 include_dirs 前缀下才算 buffer 供给。
- `for_source_root`（L66-80）vs `for_profile`（L82-89）：前者=根作用域路径（无 manifest 的 workspace 用 `role().supports_root_scoped_compilation()` 兜底，L72-76）；后者=profile 路径，profile 无 source_roots 时回退 `all_non_ignored_roots`（L86-87、L219-230）。
- `source_buffer_path`（L127-135）+`synthetic_source_buffer_path`（L137-145）：无文件系统路径的 fixture/editor 文件给确定性合成路径（`/__vide_virtual__/<index>`）——不变量：slang `SourceManager::assignText` 按 path 键控，空 path 非法，且同一 snapshot 内必须确定。
- `include_buffers_for_plan_with_roots`（L147-198）：同一路径两个 FileId 文本不同直接 **panic**（L180-187）——路径唯一性不变量；`include_buffers_for_plan`（L113，不含 roots）与 `compilation_source_buffers_for_plan`（L120，含 roots+LibraryMap）两个口径。
- `include_targets_for_source_roots`（L277-331）：工作栈式闭包扫描字面 include；`literal_include_targets`（L333-361）用 `SyntaxTreeOptions::without_include_expansion()` 干跑一次预处理拿 include 图（不展开宏 include）；`resolve_include_target`（L363-390）解析顺序=绝对路径 normalize → includer 所在目录 → 逐 include_dir。
- 内嵌测试 `synthetic_source_buffer_paths_are_absolute`（L396-402）。

**公开 API**：`CompilationPlan::{all_file_ids, is_include_header_in_include_paths, for_source_root, for_profile}`；free fn `include_buffers_for_plan(db,&plan)->Vec<SyntaxTreeBuffer>`、`compilation_source_buffers_for_plan`、`source_buffer_path(db,file_id)->AbsPathBuf`；类型 `IncludeScanIssue{file_id,reason}`、`IncludeScanIssueReason::Model(SourcePreprocError)`。

**依赖/被依赖**：依赖→base-db（ProjectConfig/SourceRootDb）、preproc::source（SourcePreprocModel/SourceIncludeDirective/MacroIncludeTarget）、syntax、utils（PathIdentityIndex/AbsPath）、vfs。被依赖→仅 db.rs 与 lib.rs（图谱入边），但 db.rs 又把它包装成 `compilation_plan_for_profile` query 供 ide 层消费。

**改动影响面**：roots/include_only 判定逻辑变化会改变 slang 编译单元集合→诊断/语义索引/补全全变；`synthetic_source_buffer_path` 格式变化会使 path→FileId 对账（db.rs `path_file_ids`）失配→诊断丢失；panic 点（L180-187）在重复路径+异文本时会击穿整个查询。

**集成点**：新增文件类别（如新 SourceFileKind）须同时改 `compile_roots_for_source_roots`（L232-262）的 `is_semantic_compilation_unit` 过滤和 `include_targets_for_source_roots` 的 kind 白名单（L299-304）。

## `crates/preproc-expand/src/file.rs`（59 行）

**角色**：`HirFileId`——全 IDE 层通用的"文件"抽象：真实源文件 or 宏展开虚拟文件。
**关键结构与不变量**：`HirFileId` enum（L8-12）`File(FileId)|Macro(MacroFileId)`，derive 全序+Hash（可当 map key/salsa 参数）。不变量：`Macro` 变体经 `macro_file_call_site` 回溯到**调用点所在文件**（L30-37 `source_file_id`），回溯失败返回 None（调用方必须处理）。
**公开 API**：`as_file()->Option<FileId>`（L15）、`expect_file()->FileId`（L22，panic "HirFileId is not a source file"）、`source_file_id(db:&dyn PreprocDb)->Option<FileId>`（L30）、`From<FileId>`（L40）。
**依赖/被依赖**：依赖→vfs::FileId、db::PreprocDb、macro_file::{MacroFileId, macro_file_call_site}。被依赖→ide 层 10+ 文件（signature_help/selection_ranges/rename/references/semantic_tokens/completion/...）与 hir-semantics（semantics/source_to_def/pathres/resolver）——是 ide↔preproc 的桥梁类型。
**改动影响面**：加变体（如 include 虚拟文件）会迫使全 ide 层 match 更新；`source_file_id` 语义变化影响 hover/rename 归属。
**集成点**：所有"把宏展开当文件"的功能从这里拿统一 ID；测试 `as_file_returns_source_file_when_hir_file_is_real_file`（L50-58）示范用法。
**内嵌测试**：跑法 `cargo test -p preproc-expand file::`。

## `crates/preproc-expand/src/context.rs`（315 行）

**角色**：per-file 宏调用覆盖索引——把"这个 offset 落在哪些宏调用里"从逐 token 文本回扫变成一次 salsa query + 二分查找。

**关键结构与不变量**：
- `MacroContext` enum（L21-30）：`NoInvocation`（回退普通语法解析）/`Invocation{macro_files:Vec<MacroFileId>}`（可能多个：嵌套展开内外都覆盖该点，按源序）。
- `MacroCoverage`（L33-50）：`spans: RangeIndex<MacroFileId>`；不变量：必须 `push` 完调 `finish()`（L43-45）构建索引后才能查询（`macro_files_at` L47-49）。
- `macro_context_at`（L52-59）：`file_macro_coverage_query` 的薄入口。
- `file_macro_coverage_query`（L61-159）：**fail-empty 语义**——任一相关 model 的 model 查询失败/无 trace/call 无 trace 身份/无 emitted range/range 映射失败都 warn+返回空 coverage（L63-72 的 Partial 状态检查、L107-150 的五处早退）；遍历 `contexts.model_file_ids`+自身（L74-79），把每个映射到本文件的 call_range push 进索引（L125-153）。
- 模块 doc（L1-9）钉版设计动机：取代 IDE 侧文本启发式 `source_macro_invocation_may_cover_offset`。
- 测试（L161-314）：`plain_identifier_has_no_invocation_context`（L266）、`outer_arguments_after_nested_macros_are_covered`（L290，外宏参数尾仍属外层）、`nested_invocations_report_both_expansions`（L304，嵌套处返回 2 个 expansion）。

**公开 API**：`MacroContext`、`MacroCoverage`（push/finish 为 pub(crate)）、`macro_context_at(db,file_id,offset)`；`file_macro_coverage_query` 为 pub(crate)（由 db.rs 包装成 `file_macro_coverage`）。
**依赖/被依赖**：依赖→db、macro_file（MacroCallLoc/MacroFileId）、source_db::range_index::RangeIndex、base-db、utils、vfs。被依赖→db.rs（query 注册）、ide/src/semantic_target/preproc.rs 与 semantic_target/tests/bench_context.rs。
**改动影响面**：fail-empty 改成部分返回会让 IDE 在 partial 上下文里给出错误归属；RangeIndex 的 push/finish 协议破坏会 panic 或二分错位。
**集成点**：任何需要"offset 是否在宏内"的 IDE 功能（hover/goto/rename/补全上下文）应查 `macro_context_at` 而非自己扫文本。

## `crates/preproc-expand/src/macro_file.rs`（756 行）

**角色**：宏文件层——`MacroCallId`/`MacroFileId` intern、从 slang trace 提取展开文本+source map、TraceIndex 加速索引、面向 IDE 的调用点/展开元数据查询。

**关键结构与不变量**：
- `SourceEmittedTokenId`（L28-39）与 `SourceEmittedTokenRange{start,len}`（L45-49）：**核心不变量**（L41-44 注释）——slang 把一次展开的全部 token（含嵌套展开与 predefine token）**连续**发射，因此展开=首 token+长度即可完整描述。
- `MacroCallLoc{model_file,trace_call}`（L51-55）：宏调用地址=哪个模型文件+哪个 trace call。
- `MacroCallId`（L57-61）/`MacroFileId`（L75-79）：两个 salsa interned 结构，同 loc；Ord 按 salsa AsId（L63-91）——稳定排序不变量。
- `ExpandResult<T>{value,err}`（L100-118）：错误不中断，value 里总有部分结果（map 保留 err）。
- `ExpandErrorKind`（L135-144）：8 类错误源（SourcePreprocModel/MissingTraceCall/ExpansionUnavailable/InvalidEmittedTokenRange/MissingEmittedToken/TraceUnavailable/SourceMap）。
- `macro_files_at_offset`（L170-238）：offset→候选 MacroFileId 列表；前置校验失败（model err/无 trace/call 无 trace_call/emitted range 缺）**整表返回空**（fail-empty）；`macro_files_for_file`（L247-316）为工作区索引返回全部映射到本文件的展开（L240-246 注释：让宏生成的 design unit 与源码单元进同一索引，不发明第二套名字解析）。
- `relevant_model_files`（L318-338）：contexts Partial 时 None（fail-empty 源头）；否则自身+contexts 并集。
- `macro_file_call_site`（L340-379）/`macro_file_expansion`（L381-423）：调用点（file+range 已映射）与展开元数据（含 `MacroExpansionDefinition::Source|Builtin`，L164-168）。
- `macro_expansion_query`（L425-431，lru=128）→`macro_expansion`（L433-483）：text 与 source_map 各自出 `ExpandResult` 再合并（`expansion_info_from_parts` L485-491，err 取先到者、双方 value 都保留）；text 用 `SyntaxTree::from_file_in_memory(&text,"macro-expansion","")` 重解析（L506）。
- `expansion_definition`（L510-550）：Resolved 引用走 `map_macro_definition`；**builtin 判定**=扫描 emitted token 的 `TokenOrigin::Builtin{name}`，恰好一个不重名 name 才算 Builtin（L534-549），否则 None。
- `TraceIndex`（L552-615）：`expansion_by_call`+`emitted_range_by_expansion` 两张 FxHashMap，单遍构建（L565-598）；嵌套展开的 token 计入自身+全部祖先 expansion 的范围（L580-590 注释 "A token belongs to its own expansion and every ancestor expansion"）；`emitted_range_for_call`（L602-614）无 expansion 记录时返回 `len=0` 空范围而非 None（零 token 展开合法）。
- `expansion_parents`（L633-643）：父子链从 token origin 提取而非 usage events（L630-632 注释钉版）。
- `expansion_text_for_range`（L676-711）：越界/溢出→`InvalidEmittedTokenRange`，缺 token→`MissingEmittedToken`，否则拼接 `display_text`。
- `expansion_text_for_empty_call`（L713-756）：零 token 展开的回退——取 call 事件的 body_tokens；空则找同 definition 的定义事件 body（L725-738）；同 buffer 时直接从 buffer 文本切片（L745-753），否则拼 raw_text。

**公开 API**：`SourceEmittedTokenId/Range`、`MacroCallLoc/Id`、`MacroFileId`、`ExpansionInfo{text,parse,source_map}`、`ExpandResult`、`ExpandError(Kind)`、`MacroFileCallSite`、`MacroFileExpansion`、`MacroExpansionDefinition`、`TraceIndex::new`；fn `macro_files_at_offset`、`macro_files_for_file`、`macro_file_call_site`、`macro_file_expansion`；pub(crate) `macro_expansion_query`、`trace_index_query`、`TraceIndex::emitted_range_for_call`。
**依赖/被依赖**：依赖→::preproc::source（SourceMacroCall/Resolution/Model）、db、preproc（map_macro_definition）、source_db（MappedSourcePreprocModel/QueryError）、syntax（Trace/TokenOrigin）、base_db::salsa、utils、vfs。被依赖→ide（rename/semantic_index/hover macro_hover expansion+markup/references search/semantic_target+tests）、hir-semantics preproc_integration_tests、本 crate file/context/db/preproc.types/source_db.queries——IDE 宏功能的唯一后端。
**改动影响面**：`SourceEmittedTokenRange` 连续性假设若被 slang 上游打破（token 非连续发射），文本提取与范围索引全错；MacroCallLoc 字段变更=全部 intern key 失效（缓存全弃）；`emitted_range_for_call` None/空范围语义区分被 macro_files_at_offset（L222）与 macro_file_expansion（L409）分别依赖。
**集成点**：新 IDE 宏功能的标准链路=`macro_files_at_offset`→`db.macro_expansion`→`ExpansionInfo.source_map.source_hits`；builtin 宏（`__FILE__` 等）识别走 `MacroExpansionDefinition::Builtin`。

## `crates/preproc-expand/src/macro_file/source_map.rs`（365 行）

**角色**：展开 token↔源码位置双向映射的 `ExpansionSourceMap`（rust-analyzer ExpansionMap 的 vide 版）。

**关键结构与不变量**：
- `Origin` enum（L18-26）：File/MacroBody/MacroArg/TokenPaste/Stringify/Builtin 六种展开 token 溯源，range 均为 hir 侧 TextRange。
- `ExpansionSourceMap`（L28-32）：`origins: Vec<Option<OriginSlot>>`（**下标=展开后 token 序号**，与展开文本 token 一一对应；None=该 token 无源）+`source_ranges: FxHashMap<FileId, RangeIndex<usize>>`（文件→(源 range→token 下标) 反查索引）。不变量：`source_ranges` 由 `source_ranges_for`（L184-199）从 origins 派生且必须 finish。
- `OriginSlot`（L34-44）：emitted_token+origin+`source:Option<OriginSource>`（file-backed 位置；TokenPaste/Stringify 经 `OperationSourceResolver` 解析参数 token 位置后才有）。
- `ExpansionSourceMapError`（L47-51）：InvalidEmittedTokenRange/MissingTraceToken 两类。
- `source_hits(file,offset)->Vec<ExpansionSourceHit>`（L88-107）：源位置→命中展开 token（goto-def/rename 逆查入口），结果按下标排序。
- `from_trace_range`（L109-157）：从 trace 的 emitted token 区间构建；边界校验与 macro_file.rs 文本提取同构；缺失 token 时**保留已构建前缀**再报错（L140-145，"preserves valid prefix"）。
- `Origin::from_token_origin`（L245-283）：slang `TokenOrigin`→hir `Origin` 翻译；Predefine/无名 Builtin/Unavailable 一律 None（L270、L281）。
- `origin_slot_from_token_origin`（L286-318）：origin+source 双提取；TokenPaste/Stringify 的 source 走 `OperationSourceResolver::source_for_operation`（L224-237，按 call_id→arguments→argument_index/argument_token_index 定位参数 token 的源 range）。
- `source_location`（L328-354）：`DisplayOnlyVirtualSource` 错误静默丢 origin（L335、L345），其他映射错误 warn 后丢——**不变量：映射失败的 origin 宁可缺失不可错挂**。
- `#[cfg(test)] from_token_origins`（L159-182）与 `map_up/map_down`（L70-86）仅供测试。

**公开 API**：`Origin`、`ExpansionSourceMap::{empty,is_empty,source_hits}`、`ExpansionSourceHit{emitted_token,expanded_token_index,range,origin}`（L53-59）、`ExpansionSourceMapError`；pub(crate) `from_trace_range`。
**依赖/被依赖**：依赖→super（macro_file 类型）、::preproc::source、syntax::preproc（TokenOrigin/ActualArgument 等）、source_db（PreprocSourceMap/RangeIndex）。被依赖→仅 macro_file.rs（经 `pub use` L25 再透出给 ide/hir）。
**改动影响面**：Origin 变体增删波及 ide hover/rename 的 match 全集；`origins` 下标与展开文本 token 的对齐若破坏（如 expansion_text_for_empty_call 的 body 回退路径多/少 token）会让 map_up/map_down 错位。
**集成点**：二次开发做"宏内诊断映射/语义高亮"直接消费 `source_hits`+`map_up`（测试 only）；新增 slang TokenOrigin 种类须在 `from_token_origin` 与 `origin_slot_from_token_origin` 两处同步。

## `crates/preproc-expand/src/macro_file/tests.rs`（539 行）【测试】

**角色**：macro_file+source_map 的行为级测试：自建 TestDb（L39-75，四 salsa trait impl+Deref 模式）+ 20 个测试。
**覆盖什么行为**（关键测试名归纳）：origin 六类映射与缺失槽（`expansion_source_map_maps_trace_origins_and_missing_slots` L139，含 `map_up(4)==None`、`source_hits` 精确命中）；未映射宏区间丢弃（`expansion_source_map_drops_unmapped_macro_ranges` L233）；slang argument_index 精确性（`trace_macro_argument_origin_indices_are_exact` L253）；端到端展开解析出 `from_macro` module（`macro_file_expansion_parses_emitted_tokens_and_maps_origins` L269，含 `db.parse(HirFileId::Macro(..))` L298）；predefine 宏有 call_site 但 definition 不可用（`macro_hir_source_file_id_does_not_require_mapped_definition` L309）；错误路径全覆盖（MissingTraceCall L346 / SourcePreprocModel L361 / MissingEmittedToken L379 / MissingTraceToken L395）；零长范围边界（L421 文本、L445 source_map）；**部分结果保留语义**（`expansion_source_map_preserves_valid_prefix_before_missing_trace_token` L484、`expansion_info_preserves_source_map_when_text_extraction_fails` L512）。
**跑法**：`cargo test -p preproc-expand`（全在 crate 内联测试，macro_file::tests 模块）。

## `crates/preproc-expand/src/preproc.rs`（53 行）

**角色**：preproc 查询门面的模块组织者：声明 9 个子模块（本单元含 5 个+helpers 树，`predefines/reference_index/reference_queries/types/tests` 属兄弟单元）、定义 `predefine_name`、控制 re-export。
**关键结构与不变量**：`predefine_name`（L39-43）：`"FOO=1"->FOO`、trim+去 `` ` `` 前缀、空名 None——predefine 配置串到宏名的唯一权威解析。re-export 策略（L45-50）：`helpers::mapping::definitions::map_macro_definition` 显式 pub(crate)；子模块 `pub use self::{conditionals::*,definitions::*,diagnostics::*,expansion::*,includes::*,reference_index::*,reference_queries::*,types::*}` 全透出。
**公开 API**：`predefine_name`（pub(crate)）；经 `pub use` 透出各子模块全部 pub 项（MacroDefinition/MacroCall/InactiveBranch/IncludeDirective/DiagnosticTarget/MacroReferenceIndex 等类型在兄弟单元的 types.rs/reference_index.rs）。
**依赖/被依赖**：依赖→base-db、preproc::source（类型导入）、smol_str/triomphe/utils/vfs、db、source_db。被依赖→ide 六文件（verilog_2005/rename/semantic_target/semantic_tokens/completion engine preproc/hover include+macro_hover/references preproc）+hir-semantics+本 crate db/macro_file——是 IDE 消费预处理查询的**唯一入口路径**。
**改动影响面**：子模块 mod 声明与 `pub use` 星号集决定 crate 外可见名；`predefine_name` 语义变化影响补全（predefine 名单）与定义跳转。
**集成点**：新增 IDE 侧预处理查询=在子模块写 fn+在此 `pub use`（或新子模块 mod 行 L27-36）。

## `crates/preproc-expand/src/preproc/conditionals.rs`（23 行）

**角色**：`inactive_branches`——查询文件中预处理禁用分支（`ifdef/else` 未选中侧）区间。
**关键结构与不变量**：`UniqVec<InactiveBranch, InactiveBranchKey>` 去重（L7）；只收映射到查询文件本身的分支（L13 `branch_file_id == file_id`）；`require_file_backed_source` 拒绝虚拟源（L12）——禁用分支必须真实可定位。
**公开 API**：`pub fn inactive_branches(db:&dyn PreprocDb, file_id:FileId) -> PreprocResult<Vec<InactiveBranch>>`（L3-23）。
**依赖/被依赖**：依赖→super（ContextQuery/map_source_mapping_range/require_file_backed_source/InactiveBranch 类型）。被依赖→preproc.rs（`pub use self::conditionals::*`）；最终消费者=ide 语义着色/折叠（灰显未激活代码）。
**改动影响面**：过滤条件放宽（允许虚拟源）会让灰显区间落到不可跳转的位置；`InactiveBranchKey::from_branch` 去重键变化影响重复分支合并。
**集成点**：IDE"灰显 `ifdef 未选中分支"功能的直接数据源。

## `crates/preproc-expand/src/preproc/definitions.rs`（186 行）

**角色**：宏定义类查询：可见宏集、定义定位（含 predefine 回退）、宏参数定义/引用定义。
**关键结构与不变量**：
- `visible_macros_at`（L6-25）：经 `mapped.source_map.source_positions_for_file_offset`（一个用户 offset 可能对应**多个**模型侧 position——include/宏折叠所致）逐一取 `model.visible_macros_at`，`MacroDefinitionKey` 去重。
- `visible_macro_names_at`（L27-41）：宏名 = 展开位置可见宏 ∪ 配置 predefine 名单（`configured_predefine_names` L36）。
- `macro_definition_at`（L43-79）：先查模型侧（`name_range.contains(offset)` L56 精确命中即取 first）；**无命中回退配置 predefine**（L69-76），多上下文时 `PreprocError::Ambiguous{kind:MacroDefinition}`。
- `macro_param_definitions_at`（L91-123）：`macro_param_definition_ids_at(file_id,offset)`→`(definition_id,param_index)` 对，逐个 `map_macro_param_definition` 且 `range.contains(offset)` 过滤。
- `macro_param_reference_definitions_at`（L125-186）：宏体内参数**引用**点→(参数定义集+引用集+查询 range)；token 与 param 按 `param.name == token.value` 匹配（L155）；`query_range.get_or_insert(range)` 取首个命中 range（L170）；返回 None 表示该 offset 不是参数引用。
**公开 API**：`visible_macros_at`、`visible_macro_names_at`、`macro_definition_at`、`macro_param_definition_at`（L81-89，单结果或 Ambiguous(MacroParam)）、`macro_param_definitions_at`、`macro_param_reference_definitions_at`。
**依赖/被依赖**：依赖→super（ContextQuery/UniqVec/map_macro_definition/map_macro_param_definition/map_macro_param_reference/source_mapping_range_at_offset）+`predefines::{configured_predefine_definitions_at,configured_predefine_names}`（兄弟单元）。被依赖→preproc.rs re-export；下游=ide completion（宏名补全）/goto-def（宏与参数定义、`include` 后宏参数 hover）。
**改动影响面**：predefine 回退顺序（模型优先、配置兜底）改变会改变跳转目标；Ambiguous 错误构造变化影响 ide 层错误展示。
**集成点**：补全引擎的宏名来源就是 `visible_macro_names_at`；参数跳转/重命名用 `macro_param_reference_definitions_at`。

## `crates/preproc-expand/src/preproc/diagnostics.rs`（46 行）

**角色**：`diagnostic_target_for_range`——range→诊断重定向目标（展开区诊断应显示在哪）。
**关键结构与不变量**：判定规则（L12-45）：0 个相交 call=uncovered；**恰好 1 个**且有 target=返回它；多 call/多 target/有 call 无 target=`covered(None)`（有宏覆盖但说不清归属→抑制原诊断）。`ambiguous_targets` 累计跨模型（L26）。
**公开 API**：`pub fn diagnostic_target_for_range(db,file_id,range)->PreprocResult<DiagnosticTargetResult>`（L3-46；DiagnosticTargetResult::{covered(Option),uncovered} 类型在 types.rs）。
**依赖/被依赖**：依赖→super（ContextQuery/source_macro_calls_intersecting_range/diagnostic_target_for_call）。被依赖→preproc.rs；types.rs 与 helpers.rs 反向 import 本模块（图谱循环由 mod 树吸收）；最终消费者=ide 诊断桥（宏展开区 slang 诊断映射回源文件）。
**改动影响面**：covered(None) 语义（抑制而非透传）改变会直接改变用户看到的宏区诊断数量。
**集成点**：诊断流水线把 slang 宏区诊断交给此函数决定重定向或丢弃。

## `crates/preproc-expand/src/preproc/expansion.rs`（42 行）

**角色**：`macro_call_resolutions_in_range`——range 内全部宏调用及其解析到的定义（call:definition 对）。
**关键结构与不变量**：引用 Unresolved 静默跳过（L15-20）；`Unavailable(reason)` **上抛错误**（L16-18 `source_model_error`）；Resolved 但 definition 缺失→`MissingEvent` 错误（L21-31，含 event_id 定位）；`push_unique_eq(MacroCallResolution{call,definition})` 全等去重（L35）。
**公开 API**：`pub fn macro_call_resolutions_in_range(db,file_id,range)->PreprocResult<Vec<MacroCallResolution>>`（L3-42）。
**依赖/被依赖**：依赖→super（ContextQuery/source_macro_calls_intersecting_range/map_macro_call/map_macro_definition/source_model_error）+::preproc::source（SourceMacroResolution）。被依赖→preproc.rs re-export；下游=ide hover（宏调用展示展开摘要）与 inlay/引用高亮。
**改动影响面**：Unavailable 上抛改跳过会掩盖模型缺陷；MacroCallResolution 字段变化波及 hover markup。
**集成点**：任何"把 range 内宏调用连同定义一起看"的功能（hover、批量重命名预检）。

## `crates/preproc-expand/src/preproc/includes.rs`（49 行）

**角色**：include 指令查询：offset 处的 `include` 指令（目标字面量或宏 token、是否解析到文件）。
**关键结构与不变量**：无 `target_range` 的指令跳过（L22-24）；`source_mapping_range_at_offset` 保证只返回落在查询文件+offset 上的指令（L25-29）；`map_include_resolved_file` 把 `SourceIncludeStatus::Resolved{source}` 翻成 FileId，Unresolved/Unavailable→None（不报错）；去重键=file_id+range+target 三元组（L38-42）。
**公开 API**：`include_directive_at`（L3-11，单结果或 `Ambiguous{kind:IncludeTarget}`）、`include_directives_at`（L13-49）。
**依赖/被依赖**：依赖→super（ContextQuery/source_mapping_range_at_offset/map_include_resolved_file/IncludeDirective/IncludeTarget 类型）。被依赖→preproc.rs；types.rs 反向 import；下游=ide hover/include（include 文件预览）与 goto-def（include 路径跳转）。
**改动影响面**：`IncludeTarget::Token{raw}` 分支（宏 token include，L35）若被改成也尝试解析，会与 predefines 展开链路重复。
**集成点**：IDE include 悬浮/跳转/补全（相对路径建议）数据源。

## `crates/preproc-expand/src/preproc/helpers.rs`（11 行）

**角色**：helpers 子树聚合器：声明 context/diagnostics/expansion/mapping/source 五个私有子模块并统一以 `pub(in crate::preproc)` 可见度 re-export。
**关键结构与不变量**：`pub(in crate::preproc) mod mapping`（L6）——mapping 及其子项永不出 crate::preproc 之外；其余经 L9-11 的星号 re-export 保持 `pub(in crate::preproc)` 封装。
**公开 API**：无对外；对 preproc 内部=全部 helper fn/类型。
**依赖/被依赖**：依赖→super（preproc.rs 的 `use self::helpers::*` L46 形成父环，图谱显示 helpers.rs imports preproc.rs/diagnostics.rs/expansion.rs 属同一 glob 环）。被依赖→preproc.rs 唯一入口。
**改动影响面**：可见度放宽会破坏"helpers 是 preproc 私有"的边界；新增 helper 子模块必须在此加 mod+use 两行。
**集成点**：无直接；是给 preproc 查询 fn 提供共享基础设施的挂载点。

## `crates/preproc-expand/src/preproc/helpers/context.rs`（150 行）

**角色**：helper 核心——多上下文查询协议 `ContextQuery`：确定"哪些模型文件覆盖此查询文件"，遍历它们并 fail-closed 收集首个错误。

**关键结构与不变量**：
- `SourcePreprocQueryContexts`（L10-13）：`model_file_ids`+`status`；`partial_error()`（L16-22）把 `SourcePreprocContextStatus::Partial{skipped_models}` 翻成 `PreprocError::PartialPreprocContextIndex`。
- `source_preproc_single_query_contexts`（L24-47）：**include_self 规则**（L33-39）：SystemVerilog 非 include_only→包含自身；SystemVerilog(include_only)/IncludeHeader→仅当无其他相关 model 时包含自身；其他 kind→不包含。即：一个文件要么自己是模型宿主，要么被别人的模型覆盖，二者必有其一。
- `ContextQuery`（L76-131）：`for_each_model`（L91-109）——model 加载失败或回调 `?` 出错都**不中断迭代**，错误进 `first_error` 槽（`record_first_error` L62-69 只记第一个）；`finish`（L112-130）=有错必返 Err（L111 注释 "Fails closed when any relevant context could not be queried"，绝不把部分成功当完全成功）。
- `PreprocSingleExt::into_single_or_none`（L133-150）：0→None、1→Some、N→Err(ambiguous(count))——所有"单目标"查询（定义/指令/参数）共用的歧义协议。
- `mapped_result`（L3-7）：`Result<Arc<Result<..>>,..>` 双层 Result 拆解。

**公开 API**：全部 `pub(in crate::preproc)`：`SourcePreprocQueryContexts`、`source_preproc_single_query_contexts`、`ContextQuery::{new,for_each_model,finish}`、`record_first_error`、`finish_empty_single_query`（L49-60）、`PreprocSingleExt`。
**依赖/被依赖**：依赖→super（PreprocError/MappedSourcePreprocModel/SourcePreprocQueryError/UniqVec 等 glob）+db+base-db。被依赖→helpers.rs 聚合→conditionals/definitions/diagnostics/expansion/includes 全部查询 fn。
**改动影响面**：fail-closed 改 best-effort 会让 partial 索引下的 IDE 查询给出误导性"无结果"；include_self 规则变化直接影响 include-only 文件能否查到宏/定义。
**集成点**：preproc 内新增查询 fn 的标准骨架=`ContextQuery::new`→`for_each_model`（闭包内放心 `?`）→`finish()?`。

## `crates/preproc-expand/src/preproc/helpers/source.rs`（56 行）

**角色**：PreprocSourceMapping（模型侧 source id→文件映射）的五个基础访问器。
**关键结构与不变量**：`require_file_backed_source`（L3-19）：RealFile/VirtualFile{Some(file_id)}→Ok；VirtualFile 无 file_id（display-only，如 predefines 虚拟源）→`DisplayOnlyVirtualSource` 错；Unmapped→`SourceUnavailable` 错。**不变量：调用方拿到的 FileId 必然真实存在于 VFS**。`map_source_mapping_range`（L28-35）=先 map range 再 map source（错经 `PreprocError::SourceQuery` 包装）。`source_mapping_range_at_offset`（L37-46）=映射+文件匹配+offset 包含三合一过滤器。`map_source_mapping_id`（L48-56）：映射缺失→`MissingSource{source}` 错。
**公开 API**：`require_file_backed_source`、`map_source_id`、`map_source_mapping_range`、`source_mapping_range_at_offset`、`map_source_mapping_id`（均 `pub(in crate::preproc)`）。
**依赖/被依赖**：依赖→super（PreprocSourceMapping/PreprocSourceId/SourceRange 类型 glob）+vfs。被依赖→helpers 聚合→mapping/* 与各查询模块的底座。
**改动影响面**：这是所有"模型源→文件"翻译的单点；错误类型变化波及全部上层查询的错误面。
**集成点**：新查询需要 file-backed 源时一律走这五个 fn，禁止直接摸 `source_map` 内部。

## `crates/preproc-expand/src/preproc/helpers/expansion.rs`（13 行）

**角色**：单 helper——range 相交的源宏调用集合。
**关键结构与不变量**：`source_macro_calls_intersecting_range`（L3-13）：`mapped.macro_call_ids_intersecting_range(file_id,source_range)` 拿 id 再查 `model.macro_calls()`，缺 id 静默过滤——**不变量：只返回调用点确实映射进查询文件区间的 call**。
**公开 API**：`pub(in crate::preproc) fn source_macro_calls_intersecting_range(mapped,&file_id,source_range)->Vec<&SourceMacroCall>`。
**依赖/被依赖**：依赖→super（MappedSourcePreprocModel/SourceMacroCall）。被依赖→diagnostics.rs（L13）与 expansion.rs（L11）两个查询。
**改动影响面**：几乎无独立影响面；过滤策略变化（不过滤缺 id）会让上层 panic 风险增大。
**集成点**：无；内部复用件。

## `crates/preproc-expand/src/preproc/helpers/diagnostics.rs`（185 行）

**角色**：诊断重定向目标的 token 级解析：一个宏调用的展开里，找第一个可挂诊断的源位置。
**关键结构与不变量**：
- `diagnostic_target_for_call`（L11-35）：trace_call/trace/emitted_range 任一缺失→Ok(None)（不可重定向不报错）。
- `TokenDiagnosticTarget`（L37-41）三态协议：`Target`（找到挂点）/`Skip`（该 origin 无源，看下一个 token）/`Blocked`（该 token 有源但映射失败——**整个调用放弃**）。
- `diagnostic_target_for_token`（L43-130）逐 origin 翻译：Source→File origin；MacroBody→predefine buffer 跳过（L64-66 `source_is_predefine`，L142-150 判定），否则 MacroBody origin；MacroArgument→arg_index 非法 Blocked、映射失败 warn+Blocked（L86-100）；Predefine/无名 Builtin/Unavailable→Skip；TokenPaste/Stringify→Blocked；有名 Builtin→挂到调用点（L116-127）。
- `diagnostic_target_for_source_expansion`（L152-177）：线性扫 emitted range，缺 token→`MissingEmittedToken` 错；第一个 Target 即返回——**不变量：诊断挂首个可定位 token，Skip 可越过、Blocked 不可**。
**公开 API**：`diagnostic_target_for_call`、`diagnostic_target_for_source_expansion`（`pub(in crate::preproc)`）；私有 `TokenDiagnosticTarget`/`diagnostic_target_for_token`/`source_range_from_trace`/`source_is_predefine`/`hir_macro_call`（L179-185，trace_call→interned MacroCallId）。
**依赖/被依赖**：依赖→super+macro_file（MacroCallId/Loc/Origin/SourceEmittedTokenId/Range）+source_db（PreprocSourceMapping/PreprocVirtualOrigin）+syntax::preproc。被依赖→helpers 聚合→diagnostics.rs 查询。
**改动影响面**：三态协议（尤其 Blocked 语义）决定宏区诊断是被抑制还是错挂；predefine 跳过规则变化会让 `define 体内的诊断跑到虚拟文件。
**集成点**：与 diagnostics.rs 的 `covered(None)` 协议配套，是"宏展开区诊断归因"的完整实现，二次开发可直接复用三态模式。

## `crates/preproc-expand/src/preproc/helpers/mapping.rs`（7 行）

**角色**：mapping 子树聚合器（definitions/includes/references 三子模块，`pub(in crate::preproc)` re-export）。
**关键结构与不变量**：`pub(in crate::preproc) mod definitions`（L3）显式放宽（definitions 被 preproc.rs 直接 import `map_macro_definition`）。
**公开 API**：星号 re-export 三子模块全部项。
**依赖/被依赖**：依赖→三个子模块。被依赖→helpers.rs；preproc.rs 另有对 definitions 子模块的直接路径（L45）。
**改动影响面**：纯结构文件；子模块增删在此同步。
**集成点**：无。

## `crates/preproc-expand/src/preproc/helpers/mapping/definitions.rs`（138 行）

**角色**：`SourceMacroDefinition`（模型侧宏定义）→`MacroDefinition`（hir 侧，真实文件+range）的翻译器。
**关键结构与不变量**：
- `map_macro_definition`（L3-51）：directive/name 双 range 必须同源（`map_definition_ranges` L111-131，不同→`MismatchedRangeFiles` 错）；**predefine 定义改写**（L13-19）：若 name_range 的源有 `predefine_manifest_source`（manifest 中的定义处），source/directive_range/name_range 全部改挂 manifest 文件——`FOO=1` 定义的跳转目标=vide.toml 里的字符串字面量；body_tokens 只取 raw 文本（L46）。
- `definition_source_range`（L53-72）：source_range=directive 起点到**同文件**最远 body token 终点的包络（跨文件 token 不计入）。
- `map_macro_param_definition`（L74-109）：无名/无 name_range 参数→None；参数名文件≠宏定义文件→`MismatchedRangeFiles`（L89-96）；返回 param_index/name/range/param_range。
- `same_macro_definition`（L133-138）：经 `MacroDefinitionKey` 等价比较（供去重键复用）。
**公开 API**：`map_macro_definition`（pub(crate)——crate 级，macro_file.rs 也用）、`map_macro_param_definition`/`map_definition_ranges`/`same_macro_definition`（pub(in crate::preproc)）。
**依赖/被依赖**：依赖→super（map_source_mapping_range/require_file_backed_source/MacroDefinition/Param/Key 类型）。被依赖→preproc.rs L45 直接路径、definitions.rs/expansion.rs 查询、helpers 聚合；macro_file.rs（expansion_definition L519）。
**改动影响面**：predefine→manifest 改写是 goto-def 的关键行为（跳到 vide.toml 而非虚拟源）；MismatchedRangeFiles 错误面变化影响上层。
**集成点**：一切需要"用户可见宏定义"的功能经此翻译；新增定义属性（如默认参数）在 MacroDefinition 与此函数同步。

## `crates/preproc-expand/src/preproc/helpers/mapping/includes.rs`（15 行）

**角色**：include 状态翻译+模型错误包装，两个小 helper。
**关键结构与不变量**：`map_include_resolved_file`（L3-11）：Resolved→`map_source_id` 得 FileId（可 Err）；Unresolved/Unavailable→Ok(None)——**解析失败≠查询失败**。`source_model_error`（L13-15）：`SourcePreprocUnavailable`→`PreprocError::SourceQuery(SourceUnavailable)` 单一包装点。
**公开 API**：两 fn 均 `pub(in crate::preproc)`。
**依赖/被依赖**：依赖→super（map_source_id/PreprocError/SourceIncludeStatus）。被依赖→helpers/mapping 聚合→includes.rs 查询、expansion.rs（source_model_error）。
**改动影响面**：极小；错误包装点收敛于此。
**集成点**：无。

## `crates/preproc-expand/src/preproc/helpers/mapping/references.rs`（78 行）

**角色**：宏引用/调用/参数引用的模型侧→hir 侧翻译（references 五件套）。
**关键结构与不变量**：`map_macro_reference`（L27-34）与 `map_macro_call`（L36-48）：directive 与 name/call range 必须同源（`map_reference_ranges` L61-78 不同源→`MismatchedRangeFiles`）；调用参数逐个 `map_macro_argument`（仅映射 argument_range，L50-59，无 range 的参数保留 index 无位置）。`map_macro_param_reference`（L3-25）：param 缺失→`MissingEvent` 错（带 definition.event_id 定位）；返回 MacroParamReference{macro_definition,file_id,param_index,token_index,name,range}。
**公开 API**：`map_macro_param_reference`/`map_macro_reference`/`map_macro_call`/`map_macro_argument`/`map_reference_ranges`（均 `pub(in crate::preproc)`）。
**依赖/被依赖**：依赖→super（map_source_mapping_range/require_file_backed_source/MacroCall/MacroArgument/MacroReference/MacroParamReference 类型）。被依赖→helpers/mapping 聚合→definitions.rs（参数引用查询）与 expansion.rs（map_macro_call/map_macro_definition 组合）。
**改动影响面**：MacroCall/MacroReference 结构变化直接改 hover/引用搜索的展示字段。
**集成点**：find-references（宏）与 call-hierarchy 的数据形态在此定型。

---

### 附：跑法与行号锚自检

- 单元全部测试：`cargo test -p preproc-expand`（db.rs/file.rs/context.rs/compilation_plan.rs 内嵌 tests + macro_file/tests.rs + preproc/tests.rs（兄弟单元））。
- 行号锚自检（抽 5 处核实）：db.rs L420 `pub trait PreprocDb: SourceRootDb {}` ✓；db.rs L177 `if plan.roots.contains(&file_id)`（权威解析复用）✓；macro_file.rs L41-44（emitted token 连续性注释）与 L602 `emitted_range_for_call` ✓；compilation_plan.rs L133 `pub fn source_buffer_path` ✓；helpers/context.rs L111 `/// Fails closed when any relevant context could not be queried.`（紧邻 L112 `finish` 签名）✓。
