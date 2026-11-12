# 02-base-db 精读手册

> 模块定位：本单元是 vide 增量编译管线（Salsa RootDb → VFS → preproc → HIR）的**最底层数据库层**——`crates/base-db` 拥有源文本、source roots、项目配置与诊断配置这些 Salsa input，向上为 preproc-expand / hir-def / hir-ty / ide 提供全部 ground-state 查询；同时附带全仓根配置（workspace Cargo.toml、toolchain、slang 子模块、C++ 侧格式化/clangd 配置）与 `crates/ide/Cargo.toml`。base-db 的架构铁律（lib.rs L1-5 doc comment）：**不得依赖 preprocessing、lowered definitions、name resolution、semantic types**。实际数据结构（ProjectConfig/SourceRoot/SourceFileKind）下沉在 `workspace-model` crate（保持 Salsa-free），base-db 通过 glob re-export（project.rs L1、source_root.rs L1）对外呈现统一门面，并用 SalsaValue wrapper（source_db.rs L22-46）把两者缝合。

---

## `crates/base-db/Cargo.toml`（16 行）

**作用**：base-db 包清单。注意 `[package] version = "0.0.0"`（L3），版本管理只在根 crate `vide` 上做（根 Cargo.toml L3 `1.3.0-beta.1`），工作区成员全部 0.0.0 占位。

**关键字段**：依赖面（L7-16）精确刻画"最底层"边界——`salsa`（增量框架）、`vfs`（FileId/FileSet/ChangedFile）、`workspace-model`（数据结构实体）、`syntax`（仅 diagnostics_config 引其 SyntaxDiagnostic/DiagnosticSeverity）、`utils`（paths/line_index）、`rustc-hash`/`smol_str`/`triomphe`/`toml`/`tracing`。**没有** hir/preproc/ide 依赖，体现分层。`toml` 依赖当前由 workspace-model 间接需求保留。

**改动的连带影响**：在此新增依赖等于把新 crate 拖入"全仓最底层"的依赖闭包（hir-def、ide、src/global_state 等 30+ 文件经 base-db 传递可见），任何引入上层 crate（如 hir-def）的改动会立刻造成循环依赖编译失败。

---

## `crates/base-db/src/lib.rs`（14 行）

**角色**：crate 门面——模块声明 + salsa 符号透传。

**关键结构与不变量**：`pub use salsa::{self, Cancelled}`（L7）是全仓约定：下游一律 `base_db::salsa::...` 引用（如 ide/db/root_db.rs L6 `base_db::salsa::{self, Durability}`），保证 salsa 版本单点升级。模块清单（L9-14）：`analysis_snapshot`/`change`/`diagnostics_config`/`project`/`source_db`/`source_root` 六个公开模块，无 `#[cfg(test)]` 之外的私有模块。doc comment（L1-5）写明"最低数据库层不得依赖 preprocessing/lowered definitions/name resolution/semantic types"，这是 review 该 crate PR 的第一判据。

**公开 API**：`base_db::salsa`、`base_db::Cancelled` + 六个模块路径。

**依赖/被依赖**：图谱出边——`imports` 到自身 6 个子模块 + `workspace-model/src/project.rs`、`workspace-model/src/source_root.rs`（经 glob re-export 间接）；`configures` 配置节点 `Cargo.toml` 与 `crates/base-db/Cargo.toml`。入边（被依赖）29 个文件：hir-def 全家（db/def_id/design_map/diagnostics/owner/pathres/region_tree/scope/ty/unit_index）、ide（db/lib/analysis/analysis_host）、preproc-expand（macro_file/context/db）、src/global_state（snapshot/reload/semantic_compiler/process_changes）、hir-semantics 与 hir-ty 测试。

**改动影响面**：改名/删任一模块会级联 30+ 文件的 use 路径；`pub use salsa` 若移除，root_db.rs 等 `base_db::salsa` 引用全部断裂。

**集成点**：二开者从此文件进入整个 DB 层；新 DB 输入类型应挂进 `source_db` 而非在 lib.rs 另立模块。

---

## `crates/base-db/src/source_db.rs`（278 行）

**角色**：Salsa 0.28 input 层核心——定义四个 `#[salsa::input]`（SourceFile/SourceFiles/SourceRoots/ProjectInputs）与两个 `#[salsa::db]` trait（SourceDb/SourceRootDb），是全仓所有 ground-state 数据（源文本、文件 kind、root 归属、项目/诊断配置）的唯一权威入口。

**关键结构与不变量**：

- `FileLoader` trait（L15-17）：`resolve_path(AnchoredPath) -> Option<FileId>`，抽象"路径→文件"解析。**base-db 不提供实现**，由最终 DB 类型实现（ide 的 RootDb 在 root_db.rs L53-59 委托 SourceRoot::resolve_path；测试在各 crate 自带 TestDb 实现，如 hir-def/src/pathres.rs L579）。设计原因：resolution 语义取决于上层，base-db 保持中立。
- SalsaValue wrapper（L22-46）：`SourceFileKindValue`/`SourceRootValue`/`DiagnosticsConfigValue`/`ProjectConfigValue` 四个 newtype，各自 `unsafe impl salsa::SalsaValue`（L27/L33/L40/L46）。**不变量**：被 salsa 持有的值要么 impl SalsaValue 要么确定不含 database-lifetime 引用（L19-21 doc）；wrapper 使 workspace-model 保持 Salsa-free 的同时把安全性声明集中在这一处——SAFETY 注释逐个声明"copy-only 'static enum"或"owned data"。给 wrapper 新增字段/换内部类型必须重审 SAFETY 断言。
- `SourceFile` input（L48-54）：`text: Arc<str>`（`#[returns(clone)]`）+ `kind: SourceFileKindValue`（`#[returns(copy)]`）。per-file 实体。
- 三个 singleton input：`SourceFiles`（L56-60，`files: FxHashMap<u32, SourceFile>` 注册表——**注册表成员资格即文件存在性**）、`SourceRoots`（L62-68，`roots: FxHashMap<u32, SourceRootValue>` + `file_root_ids: FxHashMap<u32, u32>` 双映射）、`ProjectInputs`（L70-76，diagnostics_config + project_config 打包，**一次 set 同步刷新两个配置的 revision**——依赖 salsa 的 field 粒度 set 保持另一个不动）。
- `SourceDb` trait（L82-158，`#[salsa::db]`，supertrait `salsa::Database + FileLoader + fmt::Debug`）：默认方法读侧 `file_text`(L84)/`file_kind`(L88)/`files`(L92)/`diagnostics_config`(L97)/`project_config`(L101)；写侧全部 `*_with_durability` 后缀（L105/L114/L126/L138/L150），**没有不带 durability 的写入口**——强制调用者显式选择失效粒度。
- `SourceRootDb` trait（L160-238，`#[salsa::db]`，`SourceDb` 的子 trait）：`source_root_id`（L162-170，缺 root 直接 panic 而非返回 None——契约是"先 set_roots 再查"）、`source_root`（L172）、`file_path`（L188-192，委托 VFS `FileSet::path_for_file`，doc 明确这是路径身份权威源，**故意不**在 salsa 里存冗余 PathBuf）、`file_compilation_profile`（L218-232，root→profile 映射查不到且 role 要求 profile 时 `tracing::debug!` 记录（L224），返回 None 而非报错）、`file_is_project_ignored`（L234）。
- 私有辅助：`source_file`（L240-246，注册表 miss 即 panic "missing source file input"）；`source_file_mut`（L248-259，读改写模式下不存在则注册一个空文本默认 SourceFile——**新建文件先入注册表再 set 文本**的顺序保证）；`ensure_source_files`/`ensure_source_roots`/`ensure_project_inputs`（L261-278，`try_get` + 惰性 `new`，singleton 首次访问的懒初始化模式）。

**公开 API**：`FileLoader`；`SourceDb`（含 5 读 + 5 写默认方法）；`SourceRootDb`（2 读 + 2 写 + file_path/file_compilation_profile/file_is_project_ignored）；re-export `SourceFileKind`（L7 `pub use workspace_model::source_db::SourceFileKind`）。

**依赖/被依赖**：出边——`vfs/src/lib.rs`（AnchoredPath/FileId）、`workspace-model/src/source_db.rs`（SourceFileKind）、自身 `diagnostics_config`/`project`/`source_root` 三模块。入边（图谱 47 文件，本 crate 被依赖之最）：ide 的全部 code_action handler（add_default_case_item 等 20+）、diagnostics/hover/rename/semantic_index/workspace_symbols/manifest/render/formatting、preproc-expand 全线（compilation_plan/context/preproc/source_db/db）、hir-def（diagnostics/owner/pathres/scope）、ide/db（root_db/line_index_db/workspace_symbol_index_db）、`base-db/src/change.rs` 自身。

**改动影响面**：改 `SourceFile` 字段会破坏 salsa 结构（需改 input 定义+所有 setter/getter 与 change.rs 的 apply 写入序列）；改 singleton key 类型（u32）牵动 vfs FileId::index() 对齐；`file_path` 语义变化影响 LSP textDocument uri 还原与 formatting/manifest；删除 panic 改 Option 会让 47 个下游文件错误处理级联变动。salsa 升级（0.28.2，根 Cargo.toml L117）时本文件的 `#[salsa::input]`/`#[salsa::db]`/`SalsaValue` 三个宏/ trait 都是 API 敏感点。

**集成点**：二开者实现自己的 DB 类型只需 `#[salsa::db] impl SourceDb for MyDb`（参见 root_db.rs L26-30 的最小样板）+ 实现 `FileLoader`；新增全局配置输入的最佳位置是 `ProjectInputs`（L70）加字段，或新起一个 singleton input 并配套 ensure_* 函数。

---

## `crates/base-db/src/change.rs`（86 行）

**角色**：文件系统→数据库的单向事务——把 VFS 增量（roots 结构 + project config + 逐文件 Create/Modify/Delete）原子地灌入 `dyn SourceRootDb`，是 rust-analyzer Change 模式的 vide 移植。

**关键结构与不变量**：

- `Change` struct（L12-16）：`roots: Option<Vec<SourceRoot>>`（None=本次不动 roots）、`project_config: Option<SharedProjectConfig>`、`changed_files: Vec<ChangedFile>`。`Default` derive（L11）给出全空 Change（`new()` L19-21 即 default）。
- `apply`（L35-81）的**固定顺序**：① project_config 先行（L36-38，durability 一律 HIGH）；② roots 逐个落地（L40-51）——**root_id = roots vec 的下标**（L42 `SourceRootId(idx as u32)`），每个 root 内先为所有 file 登记 root 归属与 kind（L44-48），再存 root 本体（L49）；③ changed_files 处理（L53-76）——先取 `db.files()` 快照，对每个文件**重新查其所属 root 的 durability 与 kind**（L57-60，即文件编辑的失效粒度跟随 root 角色：library=HIGH、local=LOW，见 L84-86），`VfsChange::Create` 插入注册表（L63-65）、`Delete` 移除（L66-69）、`Modify` 不动注册表只改文本（L70）；文本取 `changed_file.text().unwrap_or_else(|| Arc::from(""))`（L73）——**Delete 也走 set_text 空串**，先 set kind 再 set text 的顺序固定；④ 注册表有变化才整体 `set_files_with_durability(files, Durability::HIGH)`（L78-80）。
- 隐含不变量：roots 的枚举顺序即 SourceRootId 分配，因此**两次 apply 的 roots 顺序必须稳定**，否则所有 root→profile 映射（ProjectConfig::profile_for_root 按下标索引）整体漂移；被 Delete 的文件从注册表移除后再查 `file_text` 会 panic（source_db.rs L245），上游必须同步清理引用。

**公开 API**：`Change::{new, set_roots, set_project_config, add_changed_file, apply}`；`apply(self, db: &mut dyn SourceRootDb)`（L35）消费 self，天然单次事务语义。

**依赖/被依赖**：出边——`vfs`（VfsChange/ChangedFile）、自身 `project`（SharedProjectConfig）/`source_db`（SourceRootDb）/`source_root`。入边（图谱 21 文件）：ide 侧绝大多数功能模块（diagnostics/definitions/inlay_hint/document_highlight/folding_ranges/formatting/rename/semantic_tokens/selection_ranges/module_resolution/analysis_host/test_utils/verilog_2005/macro_hover_tests/index_benchmarks、code_action/tests、completion/engine/tests、semantic_target/tests、db/apply_change.rs）+ `base-db/src/lib.rs`。生产侧真正组装 Change 的是 `src/global_state/process_changes.rs`（L251-252 `Change::new()`）。

**改动影响面**：调整 apply 内三段顺序会造成配置与 roots/文件内容短暂不一致的中间态查询（LSP 并发快照下可见脏数据）；改 root_id 分配规则需同步 src/global_state/reload.rs 的 roots 构建顺序与 workspace-model 的 SourceRootConfig::partition 输出顺序；漏掉 L78 的 files_changed 守卫会把每次 Modify 也变成注册表级 HIGH 失效，拖垮增量性能。

**集成点**：测试与嵌入场景的标准注入通道——构造 Change→apply 即可从空 DB 建立完整分析状态（ide/src/db/apply_change.rs 即此封装）；实现文件监听回放、快照 diff 回放（undo）都应复用而非绕过 apply。

---

## `crates/base-db/src/analysis_snapshot.rs`（106 行）

**角色**：分析快照的身份与上下文值类型——`AnalysisSnapshotId`（不可变分析状态的稳定标识）与 `CompilationContext`（一次编译可见的完整输入快照），供 IDE 层做结果缓存失效与诊断去重。

**关键结构与不变量**：

- `AnalysisSnapshotId(u64)`（L13）：Clone/Copy/Ord 全派生。**不变量**（L7-11 doc）：id 只在 analysis host 应用一次 change 时前进一步；同一 host 状态派生多个只读视图**不产生**新 id。`next`（L24-26）用 `checked_add` + `expect("analysis snapshot id exhausted")`（L25）——溢出 fail-fast 而非回绕。`Default` 为 0（测试 L82 断言）。
- `CompilationContext`（L36-43）：`profile: Option<CompilationProfileId>` + 五个 `Arc<[...]>` 集合（roots/include_dirs/predefines/library_maps/top_modules）。**不变量**（L29-34 doc）：集合全部藏在 Arc 不可变切片后，调用方无法原地变异使"结果"与"编译输入"脱钩；`roots`/`library_maps` 存 **VFS FileId 而非路径**，其文本与路径归属同一 salsa 快照——脱离该快照使用这些 id 是未定义行为。构造唯一入口 `new`（L46-62，全部 `impl Into<Arc<[T]>>` 参数）；只读访问器 `root_ids`（L64）/`library_map_ids`（L67）。

**公开 API**：`AnalysisSnapshotId::{new, get, next}`；`CompilationContext::{new, root_ids, library_map_ids}` + 六个 pub 字段。

**依赖/被依赖**：出边——`workspace-model`（经 project.rs re-export 的 CompilationProfileId）、`utils`（paths::AbsPathBuf）、`vfs`（FileId）。入边（图谱 6 文件）：`ide/src/analysis.rs`（Analysis 持 snapshot_id，L48）、`ide/src/analysis_host.rs`（host 内 id 推进，L11/L16/L38）、`ide/src/lib.rs`、`preproc-expand/src/db.rs`、`src/global_state/diagnostics.rs`（诊断按 snapshot_id 分组去重，L12/L82/L184）、`base-db/src/lib.rs`。

**改动影响面**：改 id 类型宽度/溢出策略影响 ide 分析缓存键与 LSP 诊断 publish 去重（src/global_state/diagnostics.rs L274/L285 测试锚定 10→11 推进）；给 CompilationContext 加字段必须走 `new`（L46）并同步其全部调用方（analysis_host 构造点）；把 FileId 改回路径会破坏"文本与路径同快照"不变量并使 salsa 失效判定失真。

**集成点**：任何想在 base-db 之上做"按分析世代缓存"的组件（诊断、索引、补全预热）都以 AnalysisSnapshotId 为 key；CompilationContext 是把 ProjectConfig+SourceRoots 压平成单一编译视图的值对象，适合跨线程/序列化边界传递。

---

## `crates/base-db/src/diagnostics_config.rs`（168 行）

**角色**：诊断行为的 ground 配置——总开关、parse/semantic 两相开关、slang 警告选项与规则表（selector→severity 映射），并实现规则引擎 `apply_rules`。

**关键结构与不变量**：

- `NEXT_CONFIG_REVISION: AtomicU64`（L5，初值 1）+ `DiagnosticsConfig.revision: u64`（L9）：**每个新构造的 config 都领全局单调 revision**（Default impl L60-70 在 L63 `fetch_add(1, Ordering::Relaxed)`）。revision 不参与 `PartialEq` 之外的语义，专供 salsa/上层判断"配置世代变了但设置可能没变"——`has_same_settings`（L78-83）比较四个设置字段忽略 revision；`with_fresh_revision`（L73-76）用于"设置回滚到旧值也要强制失效"的场景。
- `DiagnosticsConfig`（L8-14）：`enabled` 总闸 + `parse`/`semantic: DiagnosticPhaseConfig`（L17-19，仅 enabled 字段）+ `slang: SlangDiagnosticsConfig`（L22-28，`warnings: Option<Vec<String>>`——None 保持 slang 原生默认，Some([]) 显式关全部警告，L23-25 doc 钉死；`rules: Vec<DiagnosticRule>`）。
- `DiagnosticRule`（L31-35）：`selector` + `severity` + `force: bool`（当前 apply_rules 未消费 force，是规则"未匹配也覆盖"语义的预留位）。
- `DiagnosticSelector`（L38-43）四态：`Code { subsystem, code }`（slang 数值错误码）、`Option(String)`（slang option 名）、`Group(String)`（诊断分组）、`Source(Parse|Semantic)`（按产生阶段一刀切）。
- `apply_rules`（L85-109）：`!enabled` 直接 None（L90-92）；**规则按声明顺序全部扫过**（非首个命中即停，L94-106），后声明的规则覆盖先声明规则的 severity 改写；`Ignore` 立即丢弃（L100），其余改写 diag.severity；最终 `severity != Ignored` 才保留（L108）。**不变量**：`DiagnosticRuleSeverity::Ignore` 与 `SyntaxDiagnostic::Ignored` 双语义——前者是规则动作，后者是 slang 侧已标记忽略。
- `matches`（L113-123）：Code 双字段精确匹配（L115-117）、Option 与 diag.option_name 比较（L118）、Group 在 diag.groups 里 any（L119）、Source 与调用方传入的 source 参数比较（L120）——即 Source 选择器匹配的是"规则应用时刻的阶段"，不是 diag 自带属性。

**公开 API**：上述类型全 pub；`DiagnosticsConfig::{with_fresh_revision, has_same_settings, apply_rules}`；`DiagnosticRule::matches` 为私有（仅测试经 super 可见）。

**依赖/被依赖**：出边——`syntax/src/lib.rs`（diagnostics::{DiagnosticSeverity, SyntaxDiagnostic}），这是 base-db 唯一依赖 syntax 的点，也是"syntax 层诊断类型下沉"的锚。入边（图谱 17 文件）：消费方分三类——src/config.rs + src/config/user_config.rs（从用户设置构造，user_config.rs L34 `diagnostics_config()`）、ide/diagnostics.rs 与 hir-def 四文件（应用规则过滤）、preproc-expand（context/db + 测试）、ide/db/root_db.rs（Default 初始化 L65-68）、`base-db/src/{lib, source_db}`。

**改动影响面**：改 apply_rules 的顺序语义（首中即停）会让多规则叠加行为反转，ide 诊断快照测试全量重录；改 revision 生成策略影响 src/config.rs 的 `updated_diagnostics_config`（L138）失效判断；DiagnosticSelector 加变体必须同步 matches（L113）与 src/config/user_config.rs 的规则解析。

**集成点**：新诊断来源接入时实现"规则可寻址"：在 SyntaxDiagnostic 上补 option_name/groups 字段即可被 Option/Group selector 命中；LSP settings→config 的翻译层在 src/config/user_config.rs，扩展用户可配置项从那里进。

---

## `crates/base-db/src/project.rs`（1 行）

**角色**：`workspace-model::project` 的 glob re-export 门面（L1 `pub use workspace_model::project::*;`）。

**关键结构与不变量**：实际导出面 = `workspace-model/src/project.rs`：`CompilationProfileId(pub u32)`（L7，含 `unsafe impl SalsaValue` L10——可作 salsa input 字段）、`PreprocessConfig{predefines, include_dirs}`（L13）、`Predefine{definition, source: Option<PredefineSource>}`（L38，`source` 记录 predefine 来源的文件+range 以支持跳转，L70-74 `PredefineSource{path: AbsPathBuf, range: TextRange}`）、`CompilationProfile{source_roots, top_modules, preprocess}`（L77）、`ProjectConfig{root_profiles: Vec<Option<CompilationProfileId>>, profiles: Vec<CompilationProfile>>`（L84，**root→profile 按下标映射，即 SourceRootId 必须是 root_profiles 的合法下标**）、`SharedProjectConfig = Arc<ProjectConfig>`（L130）。查询 API：`profile_for_root`（L97，越界或 None→None）、`profile`（L101）、`preprocess_for_profile`（L119，profile 缺失回退 `PreprocessConfig::default()`）。

**公开 API**：上述七个类型全部以 `base_db::project::*` 路径对外（见 ide/preproc-expand/hir-def 的 use）。

**依赖/被依赖**：出边仅 `workspace-model/src/project.rs`。入边（图谱 24 文件）：preproc-expand 五文件、ide 七文件、hir-def 四文件、src/global_state.rs、base-db 自身三文件（analysis_snapshot L5 / change L6 / source_db L11）、hir-semantics 与 hir-ty 测试。

**改动影响面**：glob re-export 意味着 workspace-model::project 里新增 pub 项自动进入 base-db API 面——在那里加 pub 类型要当作 base-db 公开 API 变更对待；删除 re-export 会让 24 文件编译失败。

**集成点**：定义新编译档位（如 per-file profile）时改 ProjectConfig 结构；二开者读 `preprocess_for_profile`（L119）即可拿到 include 目录与 predefine 全集，无需理解 profiles 内部布局。

---

## `crates/base-db/src/source_root.rs`（1 行）

**角色**：`workspace-model::source_root` 的 glob re-export 门面（L1）。

**关键结构与不变量**：实际导出面 = `workspace-model/src/source_root.rs`：`SourceRootId(pub u32)`（L6 + SalsaValue L9）、`SourceRootRole` 四态枚举（L12-17：Local/BESTEffortIndex/Library/Ignored）——**角色即策略表**（L26-68）：`is_watched`（L35，Local|BestEffortIndex）、`participates_in_semantic_profile`（L39，Local|Library）、`reports_missing_profile`（L47，同上）、`diagnostic_scope`（L51-57，Local|Library→Workspace、BestEffortIndex→OpenFile、Ignored→Disabled）、`allows_workspace_edits`（L59，非 BestEffortIndex）、`publishes_unopened_workspace_diagnostics`（L63，非 BestEffortIndex——Ignored 也发布**空报告**以便客户端清除旧诊断，L64-65 注释钉死）。`SourceRoot`（L71-75）：`role` + `source_files: Option<Vec<FileId>>`（Some=源文件过滤模式）+ `file_set: FileSet`（路径↔FileId 权威映射）。`file_kind`（L152-167）的裁决链：路径推 kind→无 source_files 过滤直接返回→有过滤时 LibraryMap/ProjectManifest 恒保留（L160），其余文件不在 source_files 列表则降级 `IncludeHeader`（L165）。`SourceRootConfig`（L171）与 `partition(&Vfs) -> Vec<SourceRoot>`（L186）：roles 与 fileset 分区长度必须相等（debug_assert L188-192），**最后一个分区默认 Ignored、其余默认 Library**（L200-204）。

**公开 API**：`SourceRootId`、`SourceRootRole`、`SourceRootDiagnosticScope`、`SourceRoot`（含 new_local/new_library/new_best_effort_index/new_ignored 及 *_with_source_files 变体、path_for_file L136/file_for_path L140/resolve_path L144/iter L148/file_kind L152）、`SourceRootConfig`。

**依赖/被依赖**：出边仅 `workspace-model/src/source_root.rs`。入边（图谱 38 文件）：ide 几乎全部功能模块、preproc-expand 三文件、src/global_state.rs、base-db 自身（change L8 / source_db L12）、各测试文件。

**改动影响面**：SourceRootRole 加变体必须补全 L26-68 的全部策略方法（测试 source_root_role_policies_are_explicit L264-283 逐条锚定）并同步 diagnostics 的 scope 分派；file_kind 裁决链（L152）变动直接影响哪些文件进入 slang parse 单元（配合 workspace-model/source_db.rs L36 `is_slang_parse_unit`：仅 SystemVerilog|LibraryMap）。

**集成点**：新增工作区形态（如只读文档根、生成代码根）= 加一个 Role 变体 + 策略表填格子；partition（L186）是 VFS→roots 的唯一装配函数，文件分组规则改动集中在 FileSetConfig。

---

## `Cargo.toml`（根，173 行）

**作用**：根包（`vide` 语言服务器二进制）+ workspace 清单二合一；全部 18 个成员与共享依赖版本的唯一锁定点。

**关键字段**：
- 根包元数据（L1-11）：`vide` `1.3.0-beta.1`（L3）、edition **2024**（L4，workspace.package L35-36 同步）、MIT、description "Language server for Verilog and System-Verilog"。
- `[workspace] members`（L14-33）：`.` 自身 + 16 个 crates + xtask，覆盖 base-db/hir-def/hir-semantics/hir-ty/ide/preproc/preproc-expand/project-model/slang-sys/syntax/user-config/utils/vfs/vide-lsp-runtime/vide-lsp-wasm/workspace-model。
- `[workspace.dependencies]`（L79-134）：path 依赖统一 0.0.0 版本（L80-92），第三方版本集中管理——salsa **0.28.2**（L117）、lsp-server 0.7.6 / lsp-types 0.95.0（L109-110）、toml 0.9.8+toml_edit+toml_parser 钉版（L129-131）、tracing/triomphe/rustc-hash 等其余。
- 编译 profile（L136-157）：dev 对 rustc-hash/smol_str/smallvec/text-size/serde/salsa 六个热依赖 opt-level=3 提速本地测试（L139-146）；release 用 thin LTO + strip symbols + codegen-units=1（L148-153）；`release-lto` 全量 LTO 继承 release（L155-157）。
- 平台与特性（L159-173）：Windows 专用 winapi（L159-160）；features `default=["server-file-watcher"]`（L167，wasm 构建关掉→`vfs/notify-backend`）、`profile-trace`（tracing-chrome，L170）；`[patch.crates-io] lsp-types` 指向 snowsignal fork 固定 rev（L172-173，上游未合的修复）。

**改动的连带影响**：动 salsa 版本（L117）直接冲击 base-db 的 input/db 宏与全部 query 定义；动 lsp-types patch 会改变全部 LSP 类型形状；新增 crate 必须同时进 members（L14）与 workspace.dependencies path 项（L79 段），否则成员间无法 `xxx.workspace = true` 引用。

---

## `build.rs`（13 行）

**作用**：根包构建脚本——把环境变量 `VIDE_BUILD_METADATA` 注入为编译期 env，用于版本串附加构建元信息。

**关键字段/逻辑**：`cargo:rerun-if-env-changed=VIDE_BUILD_METADATA`（L4，只有该变量变化才重跑）；取值 trim、空值过滤、非空加 `+` 前缀（L6-11），经 `cargo:rustc-env=VIDE_BUILD_METADATA={metadata}`（L12）导出。消费点：`src/lib.rs` L31 `formatcp!("{}_{}{}", env!("CARGO_PKG_VERSION"), BUILD_PROFILE, env!("VIDE_BUILD_METADATA"))` 组装完整版本串（release 流程借此注入 git 短哈希等）。

**改动的连带影响**：删掉此文件则 `env!("VIDE_BUILD_METADATA")` 编译失败（env! 在未定义时硬错误）；改名变量需同步 src/lib.rs L31 与 CI/release 工作流。

---

## `rust-toolchain.toml`（4 行）

**作用**：锁定全仓工具链——CI 与本地开发者无 rustup 协商直接对齐。

**关键字段**：`channel = "nightly-2026-05-24"`（L2）、`profile = "minimal"`（L3）、components rustfmt+clippy（L4）。nightly 钉版的硬需求来自 rustfmt.toml L1 `unstable_features = true` 及其 group_imports/imports_granularity 等 nightly-only 选项。

**改动的连带影响**：升级 nightly 日期是全仓事件（new formatter 输出差异会导致海量 format-only diff，clippy 新 lint 可能 CI 红板）；降到 stable 则 rustfmt.toml 大半配置失效报错。

---

## `rustfmt.toml`（14 行）

**作用**：全仓 Rust 代码风格规则，与 toolchain nightly 绑定。

**关键字段**：`unstable_features = true`（L1）开门；edition 2024 + style_edition 2024（L2-3）；`format_macro_matchers`（L5）；**import 组织三连**：`group_imports = "StdExternalCrate"`（L6，std/外部/本地三段分组）、`imports_granularity = "Crate"`（L7，同 crate import 合并成一条——与 base-db/src/lib.rs 及全仓 use 语句形态直接对应）、`wrap_comments = true`（L8）；`use_small_heuristics = "Max"`（L10，尽量不折行）、`reorder_impl_items = true`（L11，type 在前 method 在后）。

**改动的连带影响**：任何选项变动理论上应全仓重跑 `cargo fmt` 一次性提交，否则 CI format check 永久红板；imports_granularity 改 Module 会与现有代码风格大面积冲突。

---

## `.cargo/config.toml`（2 行）

**作用**：cargo 别名——`cargo xtask` 展开为 `cargo run -p xtask --`（L2）。

**关键字段/逻辑**：唯一键 `[alias] xtask`。仓内 xtask crate 承担代码生成/发布辅助等任务，文档与脚本统一以 `cargo xtask <cmd>` 调用。

**改动的连带影响**：删除后所有文档化的 xtask 命令失效；改名需同步 website 文档与 CI 脚本。

---

## `.clang-format`（40 行）

**作用**：third_party/slang（C++ 子模块）侧的 clang-format 规则——vide fork 维护 slang 源码时的统一格式。

**关键字段**：LLVM base + C++20（L2-4）；列宽 100、缩进 4、禁 Tab（L6-10）；`NamespaceIndentation: All`（L12）；参数不 BinPack、BlockIndent 续行风格（L15-19）；`PenaltyReturnTypeOnItsOwnLine: 1000000`（L26，坚决不把返回类型单独成行）；IncludeCategories 四级分组（L31-39）：系统头 → `cxx.h`（bindgen 桥接头）→ `slang/...` 自家头 → 其余，配合 `IncludeBlocks: Regroup`（L30）自动重排。

**改动的连带影响**：改动后对 slang 子模块重新 format 会制造与上游 vide 分支的海量 diff，增加同步成本；`cxx.h` 分组规则与 slang-sys 的 cxx 绑定方式耦合。

---

## `.clangd`（5 行）

**作用**：clangd LSP 配置，仅作用于 slang C++ 子目录。

**关键字段/逻辑**：`If: PathMatch: third_party/slang/.*`（L1-2）限定生效范围；`CompileFlags: CompilationDatabase: target/slang-sys/debug/build`（L4-5）指向 slang-sys build 产物里的 compile_commands.json——IDE 打开 slang C++ 源码可正确解析 include/宏。

**改动的连带影响**：删掉 If 条件会让 clangd 尝试索引 Rust 仓根的杂项 C++ 文件并报错；换 target 目录名（debug→release）需同步。

---

## `.gitattributes`（1 行）

**作用**：全仓行尾策略——`* text=auto eol=lf`（L1）。

**关键字段/逻辑**：自动检测文本文件并强制 LF 检出/提交，Windows 贡献者也不会引入 CRLF diff（配合 .clang-format UseTab: Never 的空格缩进）。

**改动的连带影响**：基本无；若为某生成文件（如二进制资源）加例外规则，注意与 CI 的 format/检查脚本无冲突。

---

## `.gitmodules`（4 行）

**作用**：声明唯一子模块 `third_party/slang`（L1）。

**关键字段/逻辑**：`url = https://github.com/pascal-lab/slang.git`（L3）——**fork 仓**而非 MikePopoloski/slang 上游；`branch = vide`（L4）跟踪 fork 上的 vide 定制分支。slang 提供解析/诊断内核，由 crates/slang-sys 经 FFI 绑定（.clang-format/.clangd 皆为其服务），README.md L30 有许可致谢。

**改动的连带影响**：升级 slang = 更新子模块指针，slang-sys 的 -sys 绑定层与 hir 层语义测试需全量回归；改指向上游原仓会丢失 vide 分支定制。

---

## `README.md`（32 行）

**作用**：英文门面 README——定位声明、徽章、许可证与致谢。

**关键内容**：产品定位（L20）："fully open-source modern SystemVerilog coding IDE"，南京大学 PASCAL 研究组出品，强调补全/注解/自动重构/语义高亮等"传统硬件 IDE 常缺"的十几项分析能力；用户手册统一指向 vide.pascal-lab.net（L22）；致谢（L30-32）：解析用 slang（MIT）、格式化可选调 Verible `verible-verilog-format`（Apache-2.0）。

**改动的连带影响**：功能表述与 website/ 文档站联动；改徽章/链接需同时看 README.zh-CN.md；新功能上线通常需同步 L20 的能力清单。

---

## `README.zh-CN.md`（32 行）

**作用**：中文镜像 README，与英文版逐段对位（logo/徽章/定位/许可证四段结构完全同构）。

**关键内容**：定位段（L20）"让硬件设计像软件开发一样流畅"；中文用户手册路径（L22）；致谢段（L30-32）同英文版——slang MIT、Verible Apache-2.0。

**改动的连带影响**：与 README.md 必须同步维护（徽章互链：中文版 L14 链向英文版，英文版 L14 链向中文版）；只改一边会造成双语内容漂移。

---

## `crates/ide/Cargo.toml`（43 行）

**作用**：ide crate（"IDE related components"，L4）清单——把 DB/HIR 各层组装为 LSP 功能的中间层。

**关键字段**：依赖面（L8-40）显式声明全部编译层：`base-db`（L10）+ hir-def/hir-semantics/hir-ty + preproc-expand——L14-15 注释钉版设计意图："Compiler layers are explicit dependencies; `hir-semantics` is a syntax-to-HIR adapter, not a high-level facade over them"（禁止把 hir-semantics 当门面绕过显式分层）。工具面：fst（符号索引）、bitflags、dissimilar（diff/TextEdit）、which（定位 verible-verilog-format 外部进程，L38）、toml 三件套（manifest 解析）。dev-dependencies（L41-43）：insta（glob 特性，快照测试）+ utils test-support。

**改动的连带影响**：ide 是 base-db 图谱入边最密集的消费方（change.rs 21 个入边文件里 20 个在 ide）；在此新增依赖注意 ide 也被 wasm 构建（vide-lsp-wasm）牵连，引入原生绑定会破坏 wasm 目标。

---

## 附：本单元内被 re-export 的实体定义位置速查

base-db 的 `project.rs`/`source_root.rs`/`source_db.rs`（L7 的 SourceFileKind re-export）三处门面指向 `crates/workspace-model/src/`：
- `project.rs`（130 行）：CompilationProfileId L7 / PreprocessConfig L13 / Predefine L38 / PredefineSource L70 / CompilationProfile L77 / ProjectConfig L84 / profile_for_root L97 / preprocess_for_profile L119 / SharedProjectConfig L130。
- `source_root.rs`（294 行）：SourceRootId L6 / SourceRootRole L12 / 角色策略方法 L26-68 / SourceRoot L71 / path_for_file L136 / file_kind L152 / SourceRootConfig L171 / partition L186。
- `source_db.rs`（72 行）：SourceFileKind L4 / from_path L17（vide.toml→ProjectManifest、.map→LibraryMap、.vh/.svh/.svi→IncludeHeader、其余 SystemVerilog）/ is_semantic_compilation_unit L32 / is_slang_parse_unit L36。
