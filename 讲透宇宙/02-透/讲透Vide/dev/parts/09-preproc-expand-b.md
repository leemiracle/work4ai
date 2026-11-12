# 09-preproc-expand-b 精读手册

> 模块定位：本单元是 `preproc-expand` crate 的**查询层**——`preproc/` 侧的 macro 引用索引与配置 predefine 桥接（`reference_index.rs`/`reference_queries.rs`/`predefines.rs`），纯数据类型层 `preproc/types/`，以及 `source_db/` 侧把 slang 预处理 trace 落到 salsa 增量查询的完整管线（source map 构建、双排序 range 索引、context 索引）。它向上喂 IDE 的 goto-def/find-refs/rename/semantic-tokens/hover，向下消费 `preproc` crate 的 `SourcePreprocModel`（slang trace 的事件模型）。架构位置：RootDb(salsa) → VFS FileId → 本层(trace→模型+range 映射) → macro_file/HIR。

---

## `crates/preproc-expand/src/preproc/predefines.rs`（108 行）
**角色**：把 vide.toml 里配置的 `predefines`（`FOO=1` 字符串）桥接成与源码 `\`define` 同构的 `MacroDefinition`，使配置宏也能被 goto-def/rename 定位到清单文件。
**关键结构与不变量**：
- `configured_predefine_names` L3：以 `UniqVec<SmolStr>` 收集 profile 全部 predefine 名（`db.project_config().preprocess_for_profile(profile_id)` L6-7）；不变量=名字经 `predefine_name()`（定义在 `preproc.rs` L39，`=` 前段去 `` ` `` 前缀）过滤后**去重且保持配置顺序**。
- `configured_predefine_definitions_for_name` L16：按名字精确匹配所有 predefine，产出 `UniqVec<MacroDefinition, MacroDefinitionKey>`；同一名字配置多次会全部返回（key 是 name_range，不合并）。
- `configured_predefine_definition` L79：核心构造点。只有 predefine 带 `source`（`PredefineSource{path,range}` 指向 vide.toml）且 path 能在 VFS 找到 FileId（L88-89）时才产出定义；`id: MacroDefinitionId::ConfiguredPredefine{file_id, range}` L92 与 `Source(...)` 变体区分来源；`name_range` 用 `crate::source_db::manifest_predefine_name_range` L90 换算成 TOML 里**裸宏名**的窄区间（否则 rename 会连 `=1` 一起改）。
- `configured_predefine_definitions_at` L32：按 offset 查配置定义。先经 `source_preproc_single_query_contexts` L38 拿"哪些编译模型覆盖此文件"反推 profile 集合（无 context 时回退 `db.file_compilation_profile(file_id)` L41）；命中判定 `definition.file_id == file_id && definition.source_range.contains(offset)` L75。
- `file_id_for_predefine_source_path` L103：线性扫 `db.files()` 按 path 相等找 FileId——O(文件数)，predefine 数量少所以可接受。
**公开 API**：`pub(super)` 三件套——`configured_predefine_names(db, file_id)`、`configured_predefine_definitions_for_name(db, context_file_id, name)`、`configured_predefine_definitions_at(db, file_id, offset) -> PreprocResult<Vec<MacroDefinition>>`；私有 `configured_predefine_definition/..._at`、`file_id_for_predefine_source_path`。
**依赖/被依赖**：依赖（经 `use super::*`）`preproc.rs` 的 `PreprocDb`/`MacroDefinition`/`MacroDefinitionKey`/`Predefine`、`helpers/context.rs` 的 `source_preproc_single_query_contexts`/`finish_empty_single_query`、`source_db::manifest_predefine_name_range`。被依赖（图谱入边）：`preproc.rs`（挂模块）、`definitions.rs`、`reference_index.rs` L175（Undefined 引用兜底）、`reference_queries.rs` L59（同名兜底）。
**改动影响面**：改 `MacroDefinitionId::ConfiguredPredefine` 的 key 字段会破坏 `MacroDefinitionKey` 去重与 rename；改"是否需要 source"语义（如允许无 source 的 predefine 产出定义）会同时影响 `tests/manifest.rs` 4 个测试与 ide/rename、ide/references 的 predefine 分支；`manifest_predefine_name_range` 返回 None 的路径直接决定配置宏定义是否"存在"。
**集成点**：二次开发做"配置宏跳转/重命名到 vide.toml"只需消费 `configured_predefine_definitions_at/for_name`；新增清单格式（yaml 等）只需替换 `manifest_predefine_name_range` 的 TOML 解析，本文件无需动。

## `crates/preproc-expand/src/preproc/reference_index.rs`（196 行）
**角色**：全 profile 宏引用索引——遍历 workspace 所有预处理模型，把 (定义, 引用) 对聚进 salsa 缓存的 `MacroReferenceIndex`，支撑 find-all-references。
**关键结构与不变量**：
- `macro_references` L3：单定义查引用入口；profile 解析优先级=引用处文件 profile，回退定义处文件 profile（L8-10 `or_else`）；返回带 `status`（Complete/Partial）——**部分失败不静默**。
- `macro_param_references` L15：形参引用查询。逐模型遍历 `macro_definitions()`（L36），`same_macro_definition`（helpers/mapping/definitions.rs L133）匹配后按 `param_index`+名字双确认（L50-55），再扫 `body_tokens` 里 token 值等于形参名的 token（L57-58）；`first_error` 策略 L24/80：**收集全部引用后若有错整体报错**（fail-closed，宁可不给结果也不给半截）。
- `build_macro_reference_index` L87 + `macro_reference_index_for_profile_query` L111：`#[salsa::tracked(lru = 16, returns(clone))]`，key 是 `PreprocProfileQueryKey`；经 `db.rs` L536 wrapper `macro_reference_index_for_profile` 暴露。lru=16 对应 profile 数量级。
- `collect_macro_references_in_model` L120：三分支——`Resolved` 走模型内定义映射；`Undefined`（L128-129）转 `collect_configured_predefine_reference` 兜底配置宏；`Unavailable` 记 `MacroReferenceIndexIssue::UnavailableReference`（L132-137）。任何映射失败只 `push_issue(SkippedModel)` 不中断（L142-159），索引是**尽力而为 + 状态标注**。
- `collect_configured_predefine_reference` L175：Undefined 引用 × 每个同名配置定义各记一对（L192-195，`definition, reference.clone()`）。
**公开 API**：`pub fn macro_references(db, file_id, definition) -> PreprocResult<MacroReferences>`、`pub fn macro_param_references(db, file_id, definition: &MacroParamDefinition) -> PreprocResult<MacroParamReferences>`、`pub(crate) build_macro_reference_index(db, profile_id)`、`pub(crate) macro_reference_index_for_profile_query(db, PreprocProfileQueryKey) -> Arc<MacroReferenceIndex>`。
**依赖/被依赖**：依赖 `queries.rs` 的 `workspace_preproc_model_file_ids`/`source_preproc_model`、`range_index.rs` 的 `MappedSourcePreprocModel`、helpers 的 `mapped_result`/`map_macro_definition`/`map_macro_reference`/`same_macro_definition`/`record_first_error`、`predefines.rs`。被依赖：`preproc.rs` re-export（`pub use reference_index::*`）、`tests.rs`、`types.rs`；下游 ide/rename.rs L462、ide/references/preproc.rs L103 调 `macro_references`。
**改动影响面**：`macro_reference_index_for_profile_query` 的 salsa 注解（lru/returns）变了要同步 db.rs wrapper；把 `push_issue` 改成 `return Err` 会改变"部分索引仍可用"的语义，tests/reference_index.rs 的双定义断言与 ide find-references 的 Partial 展示都要跟着改。
**集成点**：新 IDE 功能要"引用计数徽章/宏调用次数统计"直接读 `MacroReferenceIndex.references_for` + `status()`；新增引用类别（如 include 目标引用）在 `collect_macro_references_in_model` 的循环旁加平行收集器即可，不动查询入口。

## `crates/preproc-expand/src/preproc/reference_queries.rs`（83 行）
**角色**：offset/range 驱动的宏引用查询（hover、goto-def、semantic-tokens 的数据源），用 `ContextQuery` 遍历该文件的所有编译上下文模型。
**关键结构与不变量**：
- `macro_references_in_range` L3：`UniqVec<_, ()>` 按 `MacroReference` 整体相等去重；`ContextQuery::new(db, file_id)` + `for_each_model`（L9-18）对每个覆盖模型查 `macro_reference_ids_intersecting_range`，`map_macro_reference` 失败**向上抛**（`?` L15）——与索引的尽力而为相反，单点查询要求准确。
- `macro_reference_definitions_at` L24：单 offset 解析。关键过滤 L38-39：`source_mapping_range_at_offset(mapped, reference.name_range, file_id, offset)` 确认**该 offset 落在映射回本文件的名字区间**才收录（防止嵌套/跨文件命中）；`query_range` 取第一个命中区间（L43 `get_or_insert`）作为返回的 range。三分支：Resolved→模型定义（缺定义时 L51-53 直接构造 `MissingEvent` 错）；Undefined→`configured_predefine_definitions_for_name` L59 兜底；Unavailable→跳过 L67。offset 不命中任何引用→`Ok(None)` L74-76。
**公开 API**：`pub fn macro_references_in_range(db, file_id, range) -> PreprocResult<Vec<MacroReference>>`、`pub fn macro_reference_definitions_at(db, file_id, offset) -> PreprocResult<Option<MacroReferenceDefinitions>>`。
**依赖/被依赖**：依赖 `helpers/context.rs` 的 `ContextQuery`、`helpers/source.rs` 的 `source_mapping_range_at_offset`、`helpers/mapping/references.rs` 的 `map_macro_reference`、`predefines.rs`、range_index 的 id 查询。被依赖：`preproc.rs` re-export；下游 ide/semantic_tokens.rs L177（高亮）、ide/hover/macro_hover/expansion.rs L42、ide/semantic_target.rs L343。
**改动影响面**：L38-39 的 `source_mapping_range_at_offset` 过滤是"多上下文去伪"的核心，删掉会让同名宏在 include 链上命中错误定义（tests/reference_context.rs L27 断言 range 精确性会红）；返回结构 `MacroReferenceDefinitions` 字段变更波及全部 hover/semantic-target。
**集成点**：做"宏预览/快速信息"直接喂 offset 给 `macro_reference_definitions_at`；做 document highlight 语义强化可复用 `macro_references_in_range`（semantic_tokens 已这么用）。

## `crates/preproc-expand/src/preproc/types.rs`（21 行）
**角色**：类型聚合模块——声明 `types/` 五个子模块并 `pub use` 扁平化再导出，同时集中本层对外部 crate 的 import（经 `super::*` 供子模块共享）。
**关键结构与不变量**：`mod common/diagnostics/includes/macro_model/reference_index` L15-19 + `pub use self::{common::*, diagnostics::*, includes::*, macro_model::*, reference_index::*}` L21——**所有 types 子模块的公共前置依赖都在这里的 L1-13**（`preproc::source` 的 id/错误类型、`utils::line_index`、`UniqVec`、`vfs::FileId`、`crate::macro_file::Origin`、`crate::source_db::SourcePreprocQueryError`），子模块一律 `use super::*`。
**公开 API**：无自有符号；再导出全部 types/* 类型。
**依赖/被依赖**：依赖 `crates/preproc/src/source.rs`、`crates/utils/src/line_index.rs`、`crates/utils/src/uniq_vec.rs`、`crates/vfs/src/lib.rs`、本 crate `macro_file.rs`、`preproc/diagnostics.rs`、`preproc/includes.rs`、`preproc/reference_index.rs`、`source_db.rs`（图谱出边）。被依赖：`preproc.rs`（`pub use types::*`）与五个 types 子模块（入边）。
**改动影响面**：在此加 import 等于给 5 个子模块全体注入；漏改会影响所有 `use super::*` 的子模块编译。类型 re-export 集合变化直接决定 crate 外（ide）可见的 API 面。
**集成点**：新类型文件放 `types/` 下只需在此 `mod x; pub use x::*;` 两行接入。

## `crates/preproc-expand/src/preproc/types/common.rs`（64 行）
**角色**：跨查询共享的枚举与错误类型层——`PreprocError` 是整个 preproc 查询栈的统一错误货币。
**关键结构与不变量**：
- `PreprocResult<T> = Result<T, PreprocError>` L3。
- `AmbiguousKind` L6 五值（MacroReference/Expansion/Param/Definition/IncludeTarget）：标记"多个编译上下文给出冲突答案"的类别。
- `RangeFilesKind` L14（Definition/Reference）：供 `MismatchedRangeFiles` 区分映射跨文件场景。
- `PreprocError` L21 四变体：`SourceQuery(SourcePreprocQueryError)`（底层查询/映射失败）、`Ambiguous{kind,count}`（无单一上下文可选）、`MismatchedRangeFiles{kind,event_id,directive_file_id,name_file_id}` L30（指令与名字落在两个文件，`event_id` 是 slang trace 事件 id，诊断用）、`PartialPreprocContextIndex{skipped_models}` L39（context 索引部分缺失，已跑查询有效但**不具全项目权威性**——fail-closed 的形式化）。
- `MacroDefinitionId` L43：`Source(SourceMacroDefinitionId)` 与 `ConfiguredPredefine{file_id, range}`（predefines.rs L92 构造）——宏定义来源判别的唯一依据；`From` impl L48-64 提供错误类型链式转换。
**公开 API**：`PreprocResult`、`AmbiguousKind`、`RangeFilesKind`、`PreprocError`、`MacroDefinitionId` + 两个 `From`。
**依赖/被依赖**：仅依赖 `types.rs` 的公共 import。被依赖：types.rs re-export → 全 crate（reference_index.rs、reference_queries.rs、range_index 经 source_db.rs）与 ide 错误处理。
**改动影响面**：`PreprocError` 加变体是全 crate match 穷尽性破坏点（LSP 侧把错误转 diagnostic 的映射也要同步）；`MacroDefinitionId::ConfiguredPredefine` 字段变化波及 predefines.rs 与 rename。
**集成点**：外部消费方（如 LSP 层）应只 match `PreprocError` 顶层变体决定"报错/降级/静默"，不深入 SourceQuery 内部。

## `crates/preproc-expand/src/preproc/types/diagnostics.rs`（24 行）
**角色**：诊断重定向目标类型——把"宏展开产物上的诊断"指回用户源文件的具体位置。
**关键结构与不变量**：`DiagnosticTarget{origin: Origin, file_id, range}` L4（`Origin` 来自 macro_file）；`DiagnosticTargetResult{covered, target: Option<DiagnosticTarget>}` L11 的核心不变量=**covered=true 且 target=None 表示"覆盖到了但无法精确映射"（fail-closed）**，与 covered=false（范围根本不在宏展开内）语义严格区分——`uncovered()` L17 / `covered(target)` L21 两个构造器是唯一创建途径。
**公开 API**：两个 struct + `DiagnosticTargetResult::{uncovered, covered}`。
**依赖/被依赖**：依赖 types.rs 公共 import（`Origin`、`FileId`、`TextRange`）。被依赖：types.rs re-export → `preproc/diagnostics.rs` 的 `diagnostic_target_for_range`（tests/diagnostics.rs L14 调用）。
**改动影响面**：`covered`/`target` 的语义区分被 tests/diagnostics.rs L16-17、L75-77 断言；加字段会使所有构造点（diagnostics.rs）需同步。
**集成点**：诊断管线（ide 侧把 HIR 诊断映射回源码）消费此类型；新诊断源只需产出 `DiagnosticTargetResult` 即可复用现有映射链。

## `crates/preproc-expand/src/preproc/types/includes.rs`（21 行）
**角色**：include 指令与失活分支的展示类型（比 source_db 里的 trace 事件更瘦、面向 IDE）。
**关键结构与不变量**：`IncludeDirective{id: SourceIncludeDirectiveId, file_id, range, target}` L4；`InactiveBranch{file_id, range}` L12（`\`ifdef` 未走分支的连续区间）；`IncludeTarget` L18 两变体——`Literal{path, resolved_file: Option<FileId>}`（字面路径，resolved_file 可空=文件不存在）与 `Token{raw}`（宏拼接路径，不可解析）。
**公开 API**：三个类型，全字段 pub。
**依赖/被依赖**：依赖 types.rs 公共 import。被依赖：types.rs re-export → `preproc/includes.rs` 的 `include_directive_at`、`preproc/conditionals.rs` 的 `inactive_branches`（tests/manifest.rs L137 断言 InactiveBranch）。
**改动影响面**：`IncludeTarget` 变体集合变化影响 includes.rs 的构造与 LSP include 提供者；`InactiveBranch` 的 range 语义（连续区间合并）被灰显/折叠功能依赖。
**集成点**：做 include 导航/头文件补全读 `IncludeDirective.target`；做灰显未激活代码（dim inactive regions）读 `InactiveBranch`。

## `crates/preproc-expand/src/preproc/types/macro_model.rs`（84 行）
**角色**：宏模型展示类型全集——定义/引用/调用/形参的 IDE 面向数据结构（与 `preproc` crate 的 Source* 系列一一对应但坐标已映射到用户文件）。
**关键结构与不变量**：
- `MacroDefinition` L4：`id`+`file_id`+`name`+`params: Option<Vec<MacroDefinitionParam>>`（None=对象式宏）+`body_tokens: Vec<SmolStr>`+三个 range（`source_range` 整体/`directive_range` 指令/`name_range` 名字）——range 三分是 goto-def 只命中 name_range（tests/reference_index.rs L64-70）的基础。
- `MacroDefinitionParam` L16：`param_index`/`name: Option`（可无名）/`range: Option`——Option 双层因为 slang trace 对无源位置参数不给 range。
- `MacroParamDefinition` L23 / `MacroParamReference` L32：形参定义/体内使用点，都携带完整 `macro_definition`（嵌套结构，判等走 key）。
- `MacroReferenceDefinitions` L61 与 `MacroParamReferenceDefinitions` L42：`{references, range, definitions}` 三元组——range 是查询命中的名字区间。
- `MacroCall` L68 + `MacroArgument` L81（`argument_index`/`range: Option`）+ `MacroCallResolution` L75（call↔definition 配对，inlay hint/调用层级用）。
**公开 API**：11 个 pub struct/enum，全字段 pub，无方法。
**依赖/被依赖**：依赖 types.rs 公共 import。被依赖：types.rs re-export → predefines.rs/reference_index.rs/reference_queries.rs 构造、macro_hover、rename。
**改动影响面**：`range: Option` 的字段（param/argument）一旦改非 Option 必须上游 map_* 全给值；三 range 字段语义变化波及 rename 编辑计算与 tests/expansion_query.rs L78-98 的精确断言。
**集成点**：IDE 一切"宏 UI"（hover 卡片、调用参数 inlay、参数高亮配对）直接消费这组类型，无需触碰 Source* 层。

## `crates/preproc-expand/src/preproc/types/reference_index.rs`（158 行）
**角色**：宏引用索引的数据结构层——去重 key 家族 + `MacroReferenceIndex` 容器与状态。
**关键结构与不变量**：
- Key 四兄弟：`MacroDefinitionKey` L4（file_id+name_range 起止+name）、`MacroReferenceKey` L22、`MacroParamDefinitionKey` L42（嵌套 definition key + param_index + 自身 range）、`MacroParamReferenceKey` L63；`InactiveBranchKey` L86。**不变量=判等只看坐标+名字，不看 id**——同一位置的同名定义视为同一个，多上下文重复报告自动合并。`from_definition`/`from_reference` 构造器 L12/L31/L51/L73。
- `MacroReferenceIndex` L103：`BTreeMap<MacroDefinitionKey, UniqVec<MacroReference, MacroReferenceKey>>`（key 有序=输出确定）+ `issues: Vec<MacroReferenceIndexIssue>`。
- `MacroReferenceIndexStatus` L116：`Complete` / `Partial{issue_count}`；`status()` L135。
- `MacroReferenceIndexIssue` L122（crate 私有）：`SkippedModel{file_id, error}` / `UnavailableReference{file_id, reason}`；`push_issue` L153 自带 `contains` 去重。
- `push` L143：`pub(in crate::preproc)`——只有 preproc 模块（reference_index.rs 收集器）能写。
**公开 API**：`MacroReferenceIndex::{references_for(definition)->Vec<MacroReference>, status()}`、`MacroReferences{references, status}`；Key 类型 pub(crate)。
**依赖/被依赖**：依赖 types.rs 公共 import。被依赖：types.rs re-export → reference_index.rs（写入）、ide references（读 `references_for`+`status`）。
**改动影响面**：Key 字段变化=去重行为变化，直接影响 find-references 结果稳定性（tests/reference_index.rs L19-26 双定义两处断言）；`references_by_definition` 改 HashMap 会丢有序性。
**集成点**：`status()=Partial` 时 UI 应提示"结果可能不全"；新 issue 类别加变体即可被 status 计数自动覆盖。

## `crates/preproc-expand/src/source_db.rs`（48 行）
**角色**：source_db 子系统的根模块——集中 import、声明 5 个子模块、并以**精细分层的 re-export 表**控制可见性。
**关键结构与不变量**：
- 子模块声明 L22-26：`mod context/queries`、`pub(crate) mod range_index`（跨给 preproc 用）、`mod source_map/source_mapping`。
- 可见性阶梯：`pub(crate) use manifest_predefine_name_range` L28（给 predefines.rs）；`#[cfg(not(test))] use source_preproc_file_ids` vs `#[cfg(test)] pub(super) use {materialized_predefine_text, source_preproc_file_ids}` L29-32（测试可见性豁免——cfg 门控的导出差异是本文件最不显眼的行为）；`use shift_text_range, unshift_text_size` L33（私有）。`pub use` L34-44 暴露 9 个类型/函数（含 `manifest_predefine_name_range_in_text`、`preproc_virtual_predefines_path`——ide/manifest.rs L13 直接 import 后者）；`pub(super) use` L45-48 给 preproc 侧的 context/queries 入口。
- 公共 import L1-20：`preproc::source::*`（Source 模型与 id）、`base_db`、`rustc_hash`、`syntax::{SyntaxTreeOptions, preproc::{SourceBufferOrigin, Trace}}`、`triomphe::Arc`、`utils::{line_index, path_identity::PathIdentityIndex, uniq_vec}`、`vfs`、`crate::db::{PreprocDb, path_file_ids, syntax_tree_options_for_file}`——全部子模块 `use super::*` 共享。
**公开 API**：仅 re-export（见 L34-44）。
**依赖/被依赖**：依赖 base-db project/source_db、preproc source、syntax、utils、vfs、db.rs、context.rs（图谱出边 15 条）。被依赖（入边 13 条）：ide/manifest.rs、db.rs、lib.rs（`pub mod source_db` L15）、macro_file.rs、macro_file/source_map.rs、macro_file/tests.rs、preproc.rs、preproc/helpers/diagnostics.rs、preproc/types.rs + 4 个子模块。
**改动影响面**：re-export 表是 crate API 面的合同——动一行就影响 ide/db/preproc 多处 import；cfg(test) 分支错位会让测试编译失败而主构建正常。
**集成点**：外部 crate 只应通过 `preproc_expand::source_db::*` 使用这些符号；新增子模块在此登记三层可见性（pub / pub(crate) / pub(super)）。

## `crates/preproc-expand/src/source_db/context.rs`（198 行）
**角色**："文件→覆盖它的编译模型"反向索引（哪个 top 文件的预处理结果能回答这个 header 上的问题），是 include 语义查询的调度核心。
**关键结构与不变量**：
- `SourcePreprocRelevantContexts{model_file_ids, status}` L4；`SourcePreprocContextIndex{contexts_by_file: FxHashMap<FileId, Vec<FileId>>, status}` L10（**值有序**：L100-102、L177-184 两次 sort）；`SourcePreprocContextStatus` L25 Complete/Partial{skipped_models}。
- `preproc_context_file_ids` L33：从单个 mapped 模型提取"它触碰过的所有文件"——遍历 macro 定义（directive/name/param/default/body L40-65）、引用（L67-70）、调用与实参 token（L72-84）、include 指令（L86-94）、失活区间（L96-98），每个 SourceRange 经 `collect_context_source` L113 收集：`source_map.file_id` 成功才收；`DisplayOnlyVirtualSource` **静默容忍**（L122，predefine 虚拟缓冲无用户文件是正常的）；manifest_source 也收（L125-127）。
- `source_preproc_context_index_for_profile` L131：**普通函数非 salsa tracked**（db.rs L467 wrapper 直调）——每次调用重建；遍历 `compilation_plan_for_profile(profile_id).roots`，只处理 `SourceFileKind::SystemVerilog | IncludeHeader`（L140-144）；模型加载失败/收集失败都 `tracing::warn!` + `skipped_models += 1`（L157-174），从不 Err——**索引永远是 best-effort，坏模型只降级 status**。
- `source_preproc_contexts_for_file` L192：单文件查询入口（file→profile→索引→contexts_for_file L16，无记录返回空 Vec + 索引全局 status）。
**公开 API**：`pub struct SourcePreprocRelevantContexts/SourcePreprocContextIndex/SourcePreprocContextStatus`；`pub(crate) fn source_preproc_context_index_for_profile(db, profile_id) -> Arc<SourcePreprocContextIndex>`、`source_preproc_contexts_for_file(db, file_id) -> Arc<SourcePreprocRelevantContexts>`。
**依赖/被依赖**：依赖 source_db.rs 公共 import、queries.rs 的 `source_preproc_model`、source_map 的 `file_id`/`predefine_manifest_source`、range_index 的 `MappedSourcePreprocModel`、base_db 的 `compilation_plan_for_profile`/`file_kind`。被依赖：source_db.rs re-export + db.rs wrapper；preproc/helpers/context.rs 的 `SourcePreprocQueryContexts`（helpers/context.rs L46 用 `relevant.status`）消费。
**改动影响面**：L140-144 的 kind 过滤放宽会把非 SV 文件塞进索引（性能+语义双坏）；`preproc_context_file_ids` 漏收某类 range（如新增的 default token 类别）会导致该位置的查询查不到上下文（tests/include_context.rs 的 include-only 双根用例 L90-125 会暴露）。
**集成点**：做"这个头文件被哪些 top 使用"的面包屑/上下文切换 UI，直接调 `source_preproc_contexts_for_file`；`status=Partial` 可触发后台重建提示。注意它是**未缓存**查询，高频调用方应自行缓存或改造为 salsa tracked（改造需同步 db.rs wrapper）。

## `crates/preproc-expand/src/source_db/queries.rs`（105 行）
**角色**：source_db 的两个基础查询——workspace 预处理模型文件清单 + 单文件预处理模型的 salsa 入口（整个 crate 增量性的根）。
**关键结构与不变量**：
- `SourcePreprocQueryError` L5：八变体错误枚举，是 source map 层的全部失败模式——`UnsupportedFileKind(SourceFileKind)`、`TraceUnavailable`、`Model(SourcePreprocError)`、`SourceUnavailable(SourcePreprocUnavailable)`、`MissingSource{source}`、`RangeOutOfBounds{source,range,mapped_range,text_len}` L16、`DisplayOnlyVirtualSource{path,origin}` L23（虚拟源无用户文件，调用方需区别对待）、`MissingEmittedToken{token}` L28。
- `workspace_preproc_model_file_ids` L33：四路收集（FxHashSet 去重后 L71-73 **sort 保证确定性**）：① plan.roots 中的 SV/IncludeHeader L40-47；② plan.include_only 全收 L48；③ 各 source_root 内非 project-ignored 的 IncludeHeader L50-59；④ 全部文件中在 include paths 里且非 ignored 的 IncludeHeader L61-69（`file_is_project_ignored` 双重过滤 L52/L63 是性能与正确性闸门）。
- `source_preproc_model` L76：`#[salsa::tracked(lru = 128, returns(clone))]`，返回 `Arc<Result<MappedSourcePreprocModel, SourcePreprocQueryError>>`——**Result 进 Arc，错误也被缓存**（同一输入不重复失败）。流程：kind 守卫 L83-85（非 SV/IncludeHeader 直接 UnsupportedFileKind）→ profile/config/options L87-89 → `parsed_compilation_unit(file_id).preprocessor_trace` L90-92（无 trace=TraceUnavailable）→ `source_preproc_file_ids`（source_mapping.rs）建 source map L94-98 → `SourcePreprocModel::from_trace(trace)` L99-102 → `MappedSourcePreprocModel::new` L104（内部即建 range 索引）。
**公开 API**：`pub enum SourcePreprocQueryError`、`pub fn workspace_preproc_model_file_ids(db, profile_id) -> Vec<FileId>`、`pub(crate) source_preproc_model(db, PreprocFileQueryKey) -> Arc<Result<...>>`（db.rs L460 wrapper 暴露给全 crate）。
**依赖/被依赖**：依赖 source_db.rs 公共 import、macro_file 的 `SourceEmittedTokenId` L2、base_db 的 compilation_plan/file_kind/source_root/file_is_project_ignored、syntax 的 parse 链。被依赖：source_db.rs（re-export error 与 file_ids 函数）、context.rs L146、reference_index.rs L26/93、preproc/helpers/context.rs——**它是 crate 内被调用最广的 query**。
**改动影响面**：lru=128 容量与 keys 数量相关（文件数级）；四路收集少一路=索引缺文件（find-references 漏报）；错误缓存语义意味着**改错误构造逻辑也要 bump 输入**才生效。
**集成点**：新分析（如 include 图可视化）以 `workspace_preproc_model_file_ids` + `source_preproc_model` 为标准遍历对；任何新 salsa query 应效仿"kind 守卫 + Arc<Result> 缓存错误"模式。

## `crates/preproc-expand/src/source_db/range_index.rs`（319 行）
**角色**：MappedSourcePreprocModel 的查询加速层——把模型事件按用户文件分桶、双排序视图支持 O(log n + k) 的 interval-stabbing（offset/range 命中）。
**关键结构与不变量**：
- `MappedSourcePreprocModel{model, source_map, range_index}` L4：`new` L11 构造时**立即**建索引（range_index 是私有字段，外部只经 6 个委托方法访问 L16-66：reference/call/definition/param_definition/param_reference 各有 `_at(offset)` 与 `_intersecting_range(range)`）。
- `PreprocRangeIndex` L70：五个 `FxHashMap<FileId, RangeIndex<T>>` 桶（references/calls/definitions/param_definitions/param_references，后两者 value 是 `(SourceMacroDefinitionId, usize)` 复合 L75-78）。
- `RangeIndex<T>` L92：**双排序视图**——同一批 `IndexedRange` 按 `(start,end)` 与 `(end,start)` 各存一份（L93-95）；`finish` L109 排序。`ids_at(offset)` L116：`partition_point` 定位 start 前缀与 end 后缀（L117-118），**扫较小的一侧再 retain**（L120-129），end 侧命中后重排恢复 start 序（注释 L126-127 点明为嵌套宏调用 target 的稳定序）；半开区间 `start <= offset < end`。`ids_intersecting_range` L135 同构（严格交非空）。
- `from_model` L152：映射失败即丢（`mapped_file_range` L265：`DisplayOnlyVirtualSource`→None 静默，其他错误 `tracing::warn!` 后丢——**索引是只含可靠坐标的子集**）；param_references 的收录条件 L188-190：body token 值等于某形参名（`params.iter().any(...)`）——**同名巧合 token 也会被索引**，由上层 macro_param_references 再验 param_index/名字（reference_index.rs L50-55）。`definition_file_range` L295：定义桶专用——manifest predefine 先走 `predefine_manifest_source` 重映射（L299-301），与 `map_macro_definition` 报告口径对齐（文档注释 L292-294 明示）。
**公开 API**：`pub struct MappedSourcePreprocModel`（6 个查询方法）；`pub(crate) struct RangeIndex<T>` 的 `push/finish/ids_at/ids_intersecting_range`；`exports ids_at/ids_intersecting_range`（图谱）。
**依赖/被依赖**：依赖 source_db.rs 公共 import、source_map 的 `map_range`/`file_id`/`predefine_manifest_source`。被依赖（入边）：source_db.rs re-export、context.rs、macro_file/source_map.rs——preproc 侧全部 offset 查询最终落到这里。
**改动影响面**：双视图排序键或 retain 条件改动直接影响命中集（tests/reference_index.rs L64-70 "只命中 name_range"依赖精确 stabbing）；`definition_file_range` 的 manifest 重映射与 map_macro_definition（helpers）必须同步，否则定义桶与映射后定义坐标漂移=goto-def 落错文件。
**集成点**：`RangeIndex<T>` 是通用组件，新事件类型（如 include 指令桶、inactive branch 桶）加一个 map + from_model 循环即可复用同一 stabbing 算法；`MappedSourcePreprocModel` 是二次开发做自定义 preproc 查询的首选数据源（免 trace 解析）。

## `crates/preproc-expand/src/source_db/source_map.rs`（42 行）
**角色**：source map 数据结构层——slang buffer id 到用户文件/虚拟文件的映射容器（方法全在子模块 mapping.rs）。
**关键结构与不变量**：
- `SourceEntry` L4：`mapping` + `text_len`（映射目标文件文本长度，越界检查用）+ `range_offset`（虚拟缓冲拼接偏移，RealFile 恒 0）+ `manifest_source: Option<PreprocManifestSource>`（predefine 缓冲指向 vide.toml 的二级映射）。
- `PreprocSourceMap` L12：`FxHashMap<PreprocSourceId, SourceEntry>`——**一个 source 只有一条 entry，后插覆盖前插**。
- `PreprocSourceMapping` L17 三态：`RealFile(FileId)` / `VirtualFile{file_id: Option<FileId>, path, origin}`（`file_id: None` = display-only 虚拟源，L19-21 注释）/ `Unmapped(SourcePreprocUnavailable)`（知道为什么不可映射）。
- `PreprocManifestSource{file_id, range, name_range}` L30：Copy 类型——`range` 覆盖完整 TOML 字符串（供校验），`name_range` 是裸宏名（供编辑）。
- `PreprocVirtualOrigin` L37：`Predefines{profile}` / `ExternalIncludeBuffer{source}`——虚拟文件的两个来源，LSP 决定是否展示的依据。
**公开 API**：5 个 pub 类型；行为方法（insert_* / get / file_id / map_range / source_positions_for_file_offset / predefine_manifest_source）在 `mod mapping` L42 中实现于同名 impl 块。
**依赖/被依赖**：依赖 source_db.rs 公共 import。被依赖：source_db.rs re-export；mapping.rs（impl）、source_mapping.rs（构建方）、range_index.rs/context.rs（消费方）、macro_file/source_map.rs（入边）。
**改动影响面**：三态 mapping 加第四态要动 mapping.rs 的全部 match（file_id L80-95 四分支、source_positions L105-113、map_range L134）；`range_offset` 语义变化波及 shift/unshift 全链。
**集成点**：`PreprocVirtualOrigin` 是虚拟文件系统的分类钩子——UI 可据此过滤"展开缓冲"标签页。

## `crates/preproc-expand/src/source_db/source_map/mapping.rs`（157 行）
**角色**：PreprocSourceMap 的全部行为——构建插入器 + 正反向坐标查询。
**关键结构与不变量**：
- 构建四插入器：`insert_real_file(source, file_id, text_len)` L4（range_offset=0）；`insert_virtual_file` L16 → `insert_virtual_file_with_offset` L27（`pub(in crate::source_db)`，带 range_offset）；`insert_unmapped(source, reason)` L47（text_len=0）；`insert_predefine_manifest_source` L59——**只补已存在 entry 的 manifest_source 字段**（L64-66 `get_mut`），不创建 entry（构建顺序约束：必须先 insert 虚拟文件再补 manifest）。
- `file_id(source) -> Result<FileId, _>` L80：四路错误映射——RealFile/带 file_id 的 VirtualFile→Ok；display-only Virtual→`DisplayOnlyVirtualSource`（L84-89）；Unmapped→`SourceUnavailable(reason)`；无 entry→`MissingSource`。
- `source_positions_for_file_offset(file_id, offset) -> Vec<SourcePosition>` L97：**逆映射**——用户文件 offset 反查所有可能 source position：过滤映射到该文件的 entry，`unshift_text_size` 减 range_offset（L118，下溢→None），界检查 `<= text_len`（L119，注意**允许 == text_len** 的 end 位置），按 `source.raw()` 排序 L123 保证确定性。多 source 命中同一文件（多 top include 同一 header）是常态。
- `map_range(source_range) -> Result<TextRange, _>` L127：MissingSource/Unmapped 前置检查（L131-136）→ `shift_text_range` 平移（L138，溢出→RangeOutOfBounds 且 text_len 记 `usize::MAX` 作哨兵）→ **end <= text_len 才 Ok**（L146-148），否则带真实 text_len 的 RangeOutOfBounds L150-155。
**公开 API**：`insert_real_file`/`insert_virtual_file`/`insert_unmapped`/`get`/`predefine_manifest_source`/`file_id`/`source_positions_for_file_offset`/`map_range` 为 pub；`insert_virtual_file_with_offset`/`insert_predefine_manifest_source` 限 crate::source_db。
**依赖/被依赖**：依赖 source_map.rs 的类型与 source_db.rs 的 `shift_text_range`/`unshift_text_size`（source_mapping.rs）。被依赖：source_map.rs（mod 挂载）；source_mapping.rs（唯一构建方）、helpers（正向查询消费方）。
**改动影响面**：`map_range` 的 `<= text_len` 边界（含 end）改动会让 end-of-file 光标查询失败/越界；`source_positions_for_file_offset` 的排序键变化影响下游歧义报告顺序。
**集成点**：做"展开缓冲↔源文件双向跳转"：正向 `map_range`、逆向 `source_positions_for_file_offset`，这对 API 就是完整合同。

## `crates/preproc-expand/src/source_db/source_mapping.rs`（486 行）
**角色**：source map 的**构建器**——从 slang trace 的 source_buffers 逐个分类映射，含 predefine 虚拟文件合成、TOML 清单名字区间解析、路径工具；本单元最大也最核心的文件。
**关键结构与不变量**：
- `source_preproc_file_ids` L5（`pub(super)`，cfg(test) 下更宽）：主构建循环。root buffer 直映射（L15-16）；先收集 `SourceBufferOrigin::Predefine` 缓冲（L18-25）建 `PredefineVirtualMapping`（L24-25）；然后遍历 `trace.source_buffers` L27-94——`Source` origin 三分支：path 在 VFS→real（L36-44）；path 在 include buffer（未保存缓冲，L45-57）→虚拟文件 `ExternalIncludeBuffer`；否则 `DetachedSource` Unmapped（L59-62）。`Predefine` origin：entry 命中→虚拟文件 `Predefines{profile}` + range_offset + 补 manifest_source（L65-83，manifest 校验失败降级 Unmapped L68-71）；unavailable→按原因 Unmapped；都不中→DetachedSource（L84-91）。
- `manifest_predefine_name_range_in_text` L108（pub，ide/manifest.rs 也用）：从 TOML 文本+完整字符串 range 求裸宏名 range。步骤：`toml_parser` 重 lex 找**精确 span 匹配**的 LiteralString/BasicString token（L112-119）→ decode 校验无错（L125-128）→ `manifest_macro_name_len` 求解码名长度 → **逐候选端点重解码验证**（L134-160：构造 `quote+候选raw+quote` 再 decode 与已解码名相等才接受——处理转义序列导致 raw/decoded 长度错位的唯一可靠法）→ 返回 `start+1 .. start+1+raw_name_len`（L162-165，+1 跳引号）。失败返回 None=不合规宏文法。
- `manifest_macro_name_len` L168：`` \` ``-转义名（首个字节 `\`，L170-173 找空白终结符）或 `[A-Za-z_][A-Za-z0-9_$]*`（L173-178）；名字后必须是 `=` 或串尾（L182-186）。
- `PredefineVirtualMapping` L264 + `PredefineVirtualEntry` L273 + `new` L280：**slang 不给 predefine buffer 与配置的身份关联，靠物化文本匹配**。物化（`materialized_predefine_text` L248：`FOO=1`→`` `define FOO 1\n ``，无 `=` 补 ` 1` L253）后拼接共享虚拟文件 `/__vide/preproc/{profile}/predefines.sv`（L197-202，`preproc_virtual_predefines_path`）；`config_indexes_by_text` 以 rev() 顺序入栈（L305-308）使同文本配置**后配置优先**被 pop（L320）且迭代序=配置序；buffer text 或名字复核失败→`UnverifiedPredefineSource`（L327-330）。
- `PredefineVirtualEntry::manifest_source` L354：predefine 有配置 source 时三重校验——path 在 `PathIdentityIndex`（L363）→ `manifest_predefine_source_matches`（L390：TOML 值解码后与配置字符串**全等**且宏名相等 L399-402）→ 名字区间可解析（L377）；任一失败→UnverifiedPredefineSource。成功产出 `PreprocManifestSource`。
- `shift_text_range` L433 / `unshift_text_size` L442：**全 crate 唯一的 offset 平移原语**（文档注释 L426-432 钉死：source_map 与 macro_file/source_map 两层都经它，防止漂移）；checked 加减 + u32 收窄，溢出→None。
- 其余工具：`profile_path_segment` L217（default/profile-N）、`sanitize_path_segment` L229（白名单字符，空→"unnamed"）、`include_buffer_texts_by_path` L240、`decode_manifest_predefine_source` L404（借 `value = ...` 包装用 toml 解码）、`file_id_for_vfs_path` L415（**全文件线性扫描**，O(n) 但仅虚拟文件少量调用）、内联测试 L450-486。
**公开 API**：`pub fn manifest_predefine_name_range_in_text(text, range)`、`pub fn preproc_virtual_predefines_path(profile_id)`、`pub(crate) manifest_predefine_name_range(db, file_id, range)`、`pub(super) source_preproc_file_ids`、`materialized_predefine_text`（cfg(test) pub）。
**依赖/被依赖**：依赖 base_db project 的 `Predefine/PreprocessConfig`、utils line_index/path_identity、syntax 的 Trace/SourceBufferOrigin/SyntaxTreeOptions、toml_parser、db 的 `path_file_ids`。被依赖：source_db.rs（三处 re-export）、queries.rs L95（构建入口）、mapping.rs（shift 原语）、ide/manifest.rs（name range）。
**改动影响面**：`shift_text_range` 改动=全 crate 坐标系漂移（两层 map 都过它）；物化文本格式（L248-256）改动会使已存 trace 与新配置不匹配（UnverifiedPredefineSource 连锁，配置宏跳转全失效）；`/__vide/preproc/...` 路径模板是虚拟文件身份，改动等同换文件。
**集成点**：新增清单宏语法（如函数式配置宏）改 `manifest_macro_name_len`；新增虚拟源类别（如命令行 `-D` 注入展示）仿 `PredefineVirtualMapping` 做 text-matching + 共享虚拟文件 + origin 枚举扩展；`manifest_predefine_name_range_in_text` 可被任何 TOML 工具复用（ide/manifest.rs 的清单索引已是第二消费者）。

---

## `crates/preproc-expand/src/preproc/tests.rs`（194 行）
**角色**：preproc 查询层的测试基础设施（TestDb + 夹具构造 + offset 工具）与 7 个测试子模块的组织者（`#[cfg(test)] mod tests;` 由 preproc.rs L53 挂载）。
**覆盖行为**：夹具核心 `db_with_entries_and_predefine_entries` L98——固定 FileId 常量 TOP=0/HEADER=1/LEAF=2/MANIFEST=3（L27-30）、单一 SourceRoot(ROOT)+PROFILE(0)（L31-32），装配 FileSet+ProjectConfig（单 profile，`PreprocessConfig{predefines, include_dirs:["include"]}` L110-118），四组 durability 输入 L126-143（files/project/diagnostics=HIGH，per-file text/kind/root_id=LOW——**文本 LOW 是 salsa 失效测试的前提**，见 include_context.rs L36 的 set_file_text_with_durability 增量场景）。`TestDb` L34-50：`#[salsa::db]` 四 trait（Database/SourceDb/SourceRootDb/PreprocDb）+ `Deref<Target=dyn PreprocDb>` L51（测试里 `db.macro_expansion(...)` 直用 wrapper）+ 手写 FileLoader L65（resolve_path 走 SourceRoot）。offset 工具：`offset` L155 / `offset_after` L159 / `offset_after_n`（第 N 次出现，L163-176，reference_index.rs 双定义断言用）/ `text_at_range` L178 / `single_macro_file_at` L182（断言恰一个宏文件）。
**跑法**：`cargo test -p preproc-expand`（模块路径 `preproc::tests::*`；无独立 test target，全部内联 #[cfg(test)]）。
**其余**：子模块声明 L188-194（diagnostics/expansion_display/expansion_query/include_context/manifest/reference_context/reference_index）；`abs_path` L149 生成跨平台 `/repo`|`C:\repo` 前缀。改动夹具的 FileId 分配或 durability 等级会同时影响 7 个子模块约 36 个测试的有效性。

## `crates/preproc-expand/src/preproc/tests/diagnostics.rs`（84 行）
**角色**：`diagnostic_target_for_range` 的 fail-closed 语义测试。
**覆盖行为**：4 个测试——`diagnostic_target_for_range_spanning_two_macro_calls_fails_closed` L4（范围跨 `` `A ``+`` `B `` 两调用：covered=true 且 target=None）；`..._adjacent_macro_calls_only_hits_intersecting_call` L21（相邻 `` `ID(1)`ID(2) `` 只命中第二个，`Origin::MacroArg{arg_index:0}` 且 range 精确到 `"2"`）；`..._for_nested_macro_call_range_is_precise` L42（`` `WRAP``→`` `LEAF `` 嵌套：`Origin::MacroBody`，range 指向字面 `"3"`）；`..._returns_none_for_unsupported_expansion_mapping` L63（`` `` `` token paste 与 `` `" `" `` stringification 两处均 covered+None）。
**跑法**：`cargo test -p preproc-expand diagnostic_target_for`。

## `crates/preproc-expand/src/preproc/tests/expansion_display.rs`（131 行）
**角色**：宏展开**文本呈现**测试（展开缓冲的 text 保真度）。
**覆盖行为**：5 个测试——`preproc_macro_expansion_exposes_macro_file_text` L5（`MAKE_DECL(generated)` 展开文本精确 `"\nlogic generated;"`）；`preproc_macro_expansion_text_keeps_emitted_token_trivia` L26（行续接 `\` 宏展开保留缩进 trivia：`\n  always_ff`/`\n    q <= 1;`/`\n  end` 三段 contains 断言）；`preproc_maps_nested_actual_argument_macro_usage_without_dropping_expansion` L50（实参里嵌套宏 `` `NEXT(`PAYL) ``：引用解析+call 实参 range+双展开共存，`names == ["NEXT","PAYL"]` L92）；`preproc_numeric_literal_expansion_text_is_available` L96（`12'd1` 字面量）；`preproc_escaped_identifier_expansion_text_is_available` L112（`\escaped.name`）。helper `expansion_definition_name` L126 处理 Source/Builtin 双定义形态。
**跑法**：`cargo test -p preproc-expand preproc_`（本文件用 `db.macro_expansion` L21/38 与 `macro_file_expansion`）。

## `crates/preproc-expand/src/preproc/tests/expansion_query.rs`（153 行）
**角色**：宏展开**结构化查询**测试（call 区间/形参映射/builtin/空展开）。
**覆盖行为**：5 个测试——`preproc_include_usage_resolves_to_header_define` L5（含 include 解析：`include_directive_at` 只在路径串上命中 L26-27，`` `include `` 关键字处 None；`IncludeTarget::Literal{resolved_file}` L28-31）；`preproc_macro_expansion_queries_map_call_ranges` L35（对象式与嵌套 `` `WRAP `` 的 `call_file_id`/`call_range`/definition name/展开文本四轴断言）；`preproc_macro_call_resolutions_in_range_map_formal_params` L64（`MAKE(width, expr)`：形参名序列 `["width","expr"]` L83-89 与实参文本 `["8","data_q"]` L90-98）；`preproc_builtin_intrinsic_expansion_uses_structured_diagnostic_target` L102（`` `__LINE__ ``/`` `__FILE__ ``：`MacroExpansionDefinition::Builtin` + `Origin::Builtin` + diagnostic target=call_range 三对齐）；`preproc_zero_token_macro_expansion_is_available` L135（空体/丢弃形参宏：text=""且 err=None）。
**跑法**：`cargo test -p preproc-expand preproc_`。

## `crates/preproc-expand/src/preproc/tests/include_context.rs`（171 行）
**角色**：编译上下文调度语义测试——header 查询走哪个模型、include-only 文件、增量失效。
**覆盖行为**：8 个测试——`preproc_nested_include_chain_maps_to_file_ids` L4（top→defs→leaf 两级链，定义落在 LEAF）；`preproc_unsaved_include_buffer_updates_query_result` L23（**salsa 增量**：改 header 文本后同查询从 0 定义变 1 定义，L36 `set_file_text_with_durability`）；`preproc_visible_macro_names_include_predefines_without_file_mapping` L51（补全名单含无文件映射的配置宏）；`preproc_single_offset_contexts_exclude_unrelated_profile_models` L69（context 索引不含无关模型）；`preproc_include_only_sv_query_uses_all_including_roots` L90（`.sv` 被 include 时进 `plan.include_only`，两 root 的同名宏**双定义并报** L118-124）；`preproc_header_query_uses_including_context_over_standalone_model` L128（`` `ifdef FEATURE `` 由 root 上下文决定 header 内定义可见）；`preproc_header_without_including_context_uses_standalone_model` L150（无人 include 时 header 自成模型）；`preproc_partial_context_index_is_structured_unavailable` L162（空 contexts+Partial → `finish_empty_single_query` 产出 `PreprocError::PartialPreprocContextIndex{skipped_models:2}` L168-170）。
**跑法**：`cargo test -p preproc-expand preproc_`。

## `crates/preproc-expand/src/preproc/tests/manifest.rs`（141 行）
**角色**：配置 predefine × vide.toml 清单源测试（predefines.rs + source_mapping.rs 的 manifest 链路）。
**覆盖行为**：4 个测试——`preproc_manifest_predefine_definition_uses_manifest_origin` L4（引用/定义双向：`macro_reference_definitions_at` 命中 MANIFEST 文件的窄 name_range L41-46；`macro_definition_at` 在 TOML 内命中 L48-52；反查 `macro_references` 找回 TOP 引用 L54-61）；`preproc_manifest_escaped_predefine_definition_uses_manifest_origin` L65（`"MSG=\"hello\""` 转义 TOML 值：name_range 仍精确到 `MSG` L89-92）；`preproc_visible_macro_names_follow_define_undef_boundaries` L103（`` `define``/`` `undef `` 边界处的可见名集合变化）；`preproc_inactive_branch_uses_header_define` L127（header 定义的宏让 root 的 `` `ifndef `` 分支失活，`inactive_branches` 返回单区间 L137-140）。夹具用 `Predefine::with_source` + `PredefineSource{path: vide.toml, range}` L24-31 直插清单区间。
**跑法**：`cargo test -p preproc-expand manifest`。

## `crates/preproc-expand/src/preproc/tests/reference_context.rs`（150 行）
**角色**："引用解析走哪个上下文"的正交维度测试——include 展开上下文中的引用/形参解析。
**覆盖行为**：4 个测试——`preproc_included_define_references_include_root_conditionals` L4（header 定义的宏，root 的 `` `ifdef `` 激活分支内引用被 find-refs 找到 L19-21；反向 definitions_at 的 range 精确=`` `HEADER_FLAG `` L26、区间右端点不命中 L27）；`preproc_header_ifdef_reference_uses_including_root_context` L36（leaf 的 `` `ifdef FEATURE_B `` 经 root include 链解析到 header 定义 L51-54）；`preproc_header_macro_body_references_use_expansion_context` L58（宏体内引用（`` `DEMO_WIDTH→`MATH_WIDTH `` 跨 leaf、`` {`DEMO_WIDTH{...}} `` 同文件嵌套）都按展开上下文解析 L79-104）；`preproc_macro_param_references_resolve_to_formals` L108（形参四查询全链：`macro_param_definition_at` 命中+端点不命中 L124、body 使用点 `macro_param_reference_definitions_at` L127-139、`macro_param_references` 含 `value` 不含 `amount` L145-149——同名形参不串）。
**跑法**：`cargo test -p preproc-expand preproc_`。

## `crates/preproc-expand/src/preproc/tests/reference_index.rs`（150 行）
**角色**：引用索引本体语义测试——多定义并报、命中精度、ifndef 守卫、undefined 条件宏。
**覆盖行为**：6 个测试——`preproc_header_reference_reports_all_including_context_definitions` L4（同文件 include 两次+`` `undef ``/重 `` `define ``：两处定义都被报 L18-26，`offset_after_n` 定位第 N 个 `` `define ``）；`preproc_header_macro_body_reference_reports_all_expansion_context_definitions` L30（宏体内引用同样双定义并报）；`preproc_macro_definition_at_only_hits_name_range` L60（goto-def 只在名字区间命中，`` `define `` 关键字与区间右端均 None L64-69，`directive_range != name_range` L70）；`preproc_ifndef_guard_reference_resolves_to_following_define` L74（守卫宏引用→后随定义，双向闭环 L82-96）；`preproc_macro_references_in_range_includes_undefined_conditionals` L100（`` `ifdef UNKNOWN `` 的 undefined 引用进 range 查询结果且 definitions 空 L113-120，已定义的 KNOWN 有定义 L122-129）；`preproc_project_header_guard_reference_is_indexed_without_include` L133（无人 include 的 header 守卫也进索引——standalone 模型兜底）。
**跑法**：`cargo test -p preproc-expand preproc_`。
