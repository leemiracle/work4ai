# 04-proj-config 精读手册

> 模块定位：本单元是 vide 的**项目/工作区配置层**，位于 VFS（01）与 base-db（02）之间。三个 crate 分工：`workspace-model` 定义被 salsa 输入层直接消费的共享类型（SourceRoot/角色策略、CompilationProfile、PreprocessConfig）；`project-model` 把 `vide.toml` 清单（或未配置目录）展开成 VFS loader 条目 + `FileSetConfig` + `SourceRootConfig` + `ProjectConfig`（含库依赖 BFS 闭包）；`user-config` 定义 LSP 用户配置（initialization options / didChangeConfiguration）并单源生成 JSON Schema 与 VS Code 配置产物。两个 schema JSON 是生成物（`cargo xtask generate-schemas`），不是手写源。

---

## `crates/project-model/Cargo.toml`（28 行）【配置】

**作用**：声明 `project-model` crate（"Model of a project"，version 0.0.0），workspace 依赖统一走根 Cargo.toml 的 `[workspace.dependencies]`。

**关键字段**：
- `manifest-schema` feature（L9）：拉起可选依赖 `schemars`（1.2.1，`preserve_order` feature）+ `serde_json`（L19/L25）， gating `toml_workspace.rs` 中 `TomlManifestSchema` 的 `schemars::JsonSchema` derive 与 `generated_toml_manifest_schema()` 导出（lib.rs L10-14）。平时不启用，只有 xtask 生成 schema 时启用。
- 依赖面（L12-24）：`vfs`（FileSetConfig/PathMatcher/loader）、`workspace-model`（ProjectConfig/SourceRoot 类型）、`utils`（带 `camino_serde1` feature，供 TOML 路径反序列化）、`toml = "0.8.8"`（直接固定版本，唯一非 workspace 依赖）、`regex`/`rustc-hash`/`smol_str`/`triomphe`/`const_format`。
- dev-dependencies（L27-28）：`utils` 追加 `test-support` feature（TestDir 夹具，仅测试用）。

**改动的连带影响**：给 `TomlManifestSchema` 加新字段需同步 schemars attr；调整 feature 名会破坏 xtask 的 `--features manifest-schema` 调用与 `generated_toml_manifest_schema` 导出路径（xtask/src/main.rs L370-371 直接 `project_model::generated_toml_manifest_schema()`）。

---

## `crates/project-model/src/lib.rs`（1604 行）

**角色**：crate 根；manifest→workspace 模型的核心编译器——把 `vide.toml`/未配置目录翻译成"loader 条目 + fileset 分类 + 编译 profile"三件套，供 `src/global_state/reload.rs` 喂给 VFS 与 base-db。

**关键结构与不变量**：
- `Workspace`（L33）：`{workspace_root, library_paths, kind, roots, semantic_profile}`。不变量：`semantic_profile` 为 `Some` 当且仅当任一 root `contributes_semantic_profile()`（L105-110：role 参与 && 有 source 输入）；语义 profile 是整个 workspace 一份（top_modules+preprocess 共享）。
- `WorkspaceRoot`（L53）：字段按消费者拆分——`source: PathMatcher` 分类 VFS 文件是否语义源文件、`source_directories` 驱动 loader/watcher 递归扫描、`source_files` 走 `vfs::loader::Entry::Files` 精确加载、`extra_files`（含 manifest 自身）只进 VFS 身份不做语义源、`include_dirs` 传预处理、`exclude_prefixes`/`exclude_globs` 双形态排除。不变量：`file_set_paths()`（L77）必须包含 `source_files` 精确路径——保证手动打开的文件无需父目录是加载根也能被分类。
- `WorkspaceKind`（L114）+ `ManifestSourcePolicy`（L135）：**三态政策**是本文件最重要语义——`sources` 省略（`None`）= `DefaultIndex`（默认 `**` 全扫描，但只做 best-effort 导航、不参与语义 profile，include_dirs 不默认到 sources）；`sources` 存在（含显式 `[]`）= `Explicit`（include_dirs 缺省回落到 sources 扫描根，`defaults_include_dirs_to_sources()` L158）。
- `workspace_roots()`（L348）：root 拆分规则——Library kind → 单个 `SourceRootRole::Library` root；Local + DefaultIndex → `Local(include_only())` + `BestEffortIndex(source_only())` 双 root；Local + Explicit → 单个 `Local` root（带全部 parts）。`push_workspace_root`（L380）只 push `has_load_paths()` 为真的 root。
- `ProjectModel::load`（L582）：**BFS 加载库闭包**——工作队列 `VecDeque<(manifest, is_lib)>`，每个 workspace 的 `library_paths` 逐个 `ProjectManifest::from_path` 入队（is_lib=true），`ProjectManifestIdentitySet`（L618，基于 `PathIdentitySet`）去重（Windows verbatim `\\?\` 路径与普通路径视为同一 manifest，测试 L924-940）。错误**不中断**：逐个收集进 `Vec<anyhow::Error>` 返回。
- `get_workspace_folder`（L638）：全局汇合点。不变量：①fileset 最后追加 `SourceRootRole::Ignored`（L767）作兜底分区；②`CompilationProfile.source_roots` = 自身 root ∪ 同 workspace 其他参与 root ∪ 传递依赖库 root（`collect_dependency_roots` L859 递归 + seen 去重，共享依赖只计一次）；③`root_profiles` 以 root_idx 为下标、`profiles` 以 `CompilationProfileId` 为下标，两边索引必须对齐（`root_profiles[loaded_root.root_idx] = Some(profile_id)` L794）。
- `SourceLocations`（L492）+ `source_locations_for_patterns`（L515）：把 glob 模式拆成 matcher_roots/directory_roots/directory_patterns/source_files/default_include_dirs 五类事实；字面量文件（`literal_source_file` L559：无元字符且是文件或带源扩展名）单独走 `Entry::Files`，其**父目录**进 default_include_dirs；`literal_root_prefix`（L545）在首个元字符处截断取字面前缀目录。
- `validate_manifest_patterns`（L418）：glob 安全闸——非空、无反斜杠、必须相对路径、不得含 `..`/根/盘符前缀（`must stay inside the workspace root` L441）。
- `exclude_prefixes_from_patterns`（L464）：剥掉 `/**`、`/*`、尾 `/` 后无通配符的模式展开为 loader 目录前缀（loader 层用前缀排除比 glob 快），纯通配模式跳过留给 `exclude_globs`。

**公开 API**：`Workspace::load(&ProjectManifest, is_lib) -> anyhow::Result<Workspace>`（L164）、`Workspace::roots()/(root)/is_lib()`（L273-291）、`ProjectModel::load(Vec<ProjectManifest>) -> (ProjectModel, Vec<anyhow::Error>)`（L582）、`get_workspace_folder(&[Workspace], &[AbsPathBuf]) -> (Vec<vfs::loader::Entry>, Vec<usize>, SourceRootConfig, Arc<ProjectConfig>)`（L638）、`WorkspaceRoot::{file_set_paths, directory_load_paths}`（L77/L91）、manifest-schema feature 下 re-export `TOML_MANIFEST_SCHEMA_*` 常量与 `generated_toml_manifest_schema`（L10-14）。

**依赖/被依赖**：依赖 → `macro_def.rs`、`project_manifest.rs`、`toml_workspace.rs`（crate 内）、`utils/path_identity.rs`、`utils/paths.rs`、`vfs/{file_set,path_glob,vfs_path}.rs`、`workspace-model/{project,source_root}.rs`。被依赖 →（imports 入边）`src/global_state.rs`、`src/global_state/{project_status,qihe,snapshot,qihe/tests,reload,main_loop}.rs`——即 LSP 主循环与 reload 管线。

**改动影响面**：`get_workspace_folder` 签名或返回结构变化直接破坏 `src/global_state/reload.rs` L164-170（Change::set_roots/set_project_config 挂点）与本文件 19 个内联测试；`workspace_roots` 三态政策变化会连锁改变 `SourceRootRole` 分布（base-db `file_compilation_profile` 查询 L218、ide diagnostics 的 `diagnostic_scope` 决策）；`CompilationProfile` 组装变化影响 preproc-expand 的 `preprocess_for_profile` 全链（crates/preproc-expand/src/preproc/predefines.rs L7/L23）。

**集成点**：二次开发接入新 manifest 字段 → 在 `TomlManifestSchema`（toml_workspace.rs）加字段 → `from_toml`（L183）解构扩展 → `WorkspaceRootParts`（L312）加槽位 → `get_workspace_folder` 消费。库依赖图扩展只需 manifest `libraries` 字段，BFS 自动展开；`global_excludes` 参数是 `files.excludeDirs` 用户配置注入点（reload.rs L163-164）。

---

## `crates/project-model/src/macro_def.rs`（59 行）

**角色**：manifest `defines` 字段的语义模型——宏定义集合 + TOML 源位置，转换为 slang 预定义。

**关键结构与不变量**：
- `MacroAtom`（L7）：`Flag(SmolStr)`（`NAME`）或 `KeyValue { key, value }`（`NAME=value`，value 可含空格如 `"BAZ=foo bar"`）。
- `MacroDef`（L13）：`macros: FxHashSet<MacroAtom>`（去重集）+ `sources: Vec<MacroDefSource>`（**每个出现位置都保留**，含 `range: TextRange`）。不变量：`to_predefines`（L29）只有在某 atom 的源出现**恰好一次**时才挂 `PredefineSource`（L42 `matches.next().is_none().then(...)`）——重复定义导致跳转源歧义时宁可不挂。
- `MacroAtom::predefine_string`（L53）：Flag→`name`，KeyValue→`key=value`，即 slang `--define` 参数格式。

**公开 API**：`MacroDef::to_predefine_strings() -> Vec<String>`（L25）、`MacroDef::to_predefines(Option<&AbsPathBuf>) -> Vec<Predefine>`（L29，输出按 definition 字符串排序 L47——保证 salsa 输入确定性）。

**依赖/被依赖**：依赖 → `workspace-model/project.rs`（Predefine/PredefineSource 类型）、`utils/line_index.rs`（TextRange）、`utils/paths.rs`。被依赖 → `project-model/src/lib.rs`、`project-model/src/toml_workspace.rs`（de_macros 构造它）。

**改动影响面**：`Predefine` 结构变化同步 `workspace-model/project.rs` L39；排序/去重语义变化影响 preproc-expand 预定义注入顺序（可观察的 slang 行为差异）与 `macro_predefines_are_stable` 测试（toml_workspace.rs L299）。

**集成点**：`to_predefines(manifest_path)` 是"manifest 定义跳转"特性的数据源——`PredefineSource { path, range }` 让 IDE 能把 slang 预定义宏 hover/diagnostic 定位回 vide.toml 的定义行。

---

## `crates/project-model/src/project_manifest.rs`（178 行）

**角色**：manifest 发现与身份标识——把用户给的项目路径解析为 `vide.toml` 文件或"未配置根"。

**关键结构与不变量**：
- `MANIFEST_FILE_NAME = "vide.toml"`（L7，`formatcp!` 编译期拼接）；`ProjectManifestFileName::DISCOVERY_ORDER`（L16）目前只有 `Primary` 一个条目——留作未来多种 manifest 名的扩展点。
- `ProjectManifest`（L33）：`Toml(AbsPathBuf) | UnconfiguredRoot(AbsPathBuf)`，derive Ord/Hash（BTreeSet 去重排序依赖路径序）。
- 发现不变量（`from_path` L59）：**只看给定目录自身**，不向上递归父目录（测试 `from_path_does_not_use_parent_manifest` L122）、不向下找子目录（L156）；指向非 manifest 文件 → 报错（`must be a directory` L67）；目录无 manifest → `UnconfiguredRoot`。`from_toml`（L94）要求路径文件名恰为 vide.toml 且 metadata 是文件。

**公开 API**：`ProjectManifest::from_paths(&[AbsPathBuf]) -> (Vec<ProjectManifest>, Vec<anyhow::Error>)`（L43，BTreeSet 去重+排序）、`from_path(&AbsPathBuf) -> anyhow::Result<ProjectManifest>`（L59）、`toml_file_name() -> Option<ProjectManifestFileName>`（L85）、`is_manifest_file_name(&str) -> bool`（L38）。

**依赖/被依赖**：依赖 → `utils/paths.rs`。被依赖 →（imports）`src/config.rs`、`project-model/src/lib.rs`、`project-model/src/toml_workspace.rs`、`src/global_state/handlers/notification/workspace.rs`（didChangeWatchedFiles 里判断 manifest 变更触发重载）；（related）`schemas/v1/vide.schema.json`。

**改动影响面**：改 manifest 文件名会破坏全部测试夹具（到处写 `MANIFEST_FILE_NAME`）与 `SourceFileKind::from_path` 的 `"vide"+"toml"` 硬编码（workspace-model/src/source_db.rs L19）、schema 的 `x-vide-manifest-names`；加新 manifest 名需扩 `DISCOVERY_ORDER` 并同步 schema 生成。

**集成点**：`UnconfiguredRoot` 是"零配置开箱即用"路径的入口——LSP 客户端给的任意目录都可用；`from_paths` 是多根 workspace（VS Code multi-root）的批量入口。

---

## `crates/project-model/src/toml_workspace.rs`（405 行）

**角色**：`vide.toml` 的解析层——serde 反序列化 + 宏定义校验（带 TOML span）+ 路径绝对化 + schema 生成。

**关键结构与不变量**：
- `TomlManifestSchema`（L47）：`#[serde(deny_unknown_fields)]`（L38）——未知字段直接报错，与 schema `additionalProperties: false` 对齐。六字段：`top_modules: Vec<String>`、`defines: MacroDef`（自定义 `de_macros`）、`sources: Option<Vec<String>>`（**三态**：缺省 None/显式 Some）、`include_dirs: Option<Vec<Utf8PathBuf>>`、`libraries: Vec<Utf8PathBuf>`、`exclude: Vec<String>`。
- `IDENTIFIER_RE`（L19）`[a-zA-Z_][a-zA-Z0-9$_]*|\\\S* `：普通标识符或 slang 风格转义标识符 `\foo `（反斜杠+非空白+空格）；`KV_RE`（L33）`^(IDENT)=(.*)$`。
- `de_macros`（L147）：**用 `toml::Spanned<SmolStr>` 捕获每个 define 的字节 span**（L151），转 `TextRange`（`spanned_text_range` L193，u32 溢出防护），存进 `MacroDefSource`；转义名 `\foo ` 剥壳为 `foo`（L174-181）。校验失败给 `Invalid macro definition: {macr}` 精确错误。
- `TomlWorkspace`（L202）：**已解析的中间产物**——所有相对路径（include_dirs/libraries）已用 `workspace_root.absolutize` 绝对化（L228-236），`workspace_root` = manifest 父目录（L222-225）。
- schema 生成（feature `manifest-schema`）：`generated_toml_manifest_schema()`（L134）在 schemars 输出上再注入 `x-vide-manifest-names: { primary: "vide.toml" }`；`TOML_MANIFEST_SCHEMA_URL`（L28）= `https://vide.pascal-lab.net/schemas/v1/vide.schema.json`。

**公开 API**：`TomlWorkspace::load_from_file(&AbsPathBuf) -> anyhow::Result<Self>`（L214）、`generated_toml_manifest_schema() -> serde_json::Value`（L134，feature-gated）、`TomlWorkspace` 全 pub 字段（L202-211）。

**依赖/被依赖**：依赖 → `macro_def.rs`、`project_manifest.rs`（schema feature 下用 MANIFEST_FILE_NAME）、`utils/line_index.rs`、`utils/paths.rs`。被依赖 → 仅 `project-model/src/lib.rs`（私有 `mod toml_workspace`，L3）。

**改动影响面**：任何字段增删/描述改动必须 `cargo xtask generate-schemas` 重生成 `schemas/v1/vide.schema.json`，否则 xtask `check-schemas`（xtask/src/main.rs L475-483）与内嵌测试 `checked_in_schemas_match_generated_schemas`（L524）失败；`deny_unknown_fields` 意味着加字段是**破坏性变更**（旧版 vide 拒绝新 manifest）；regex 改动影响 `MACRO_DEFINITION_SCHEMA_RE`（L21）必须同步（schema pattern 与运行时校验双份）。

**集成点**：新 manifest 字段的标准接入点（schema derive 属性即文档）；`Spanned` span 保留模式可复制给其他需要"配置错误跳转到源位置"的字段。

---

## `crates/user-config/Cargo.toml`（12 行）【配置】

**作用**：声明 `user-config` crate（L4 description "Vide user configuration model and generated editor artifacts"，L5 `publish = false` 不上 crates.io）。

**关键字段**：`[dependencies]`（L8-12）仅 4 个——`camino`（L9，`serde1` feature，Utf8PathBuf 反序列化）、`schemars` 1.2.1（L10，`preserve_order`，**非可选**：schema 生成是常态能力）、`serde`（L11）、`serde_json`（L12）。**刻意零依赖 vide 内部 crate**（不依赖 vfs/utils/base-db）——保证该 crate 可被 xtask 独立拉起生成编辑器产物。

**改动的连带影响**：加依赖会传导给 xtask 与主二进制的构建图；此 crate 的类型（如 `UserConfig`）被 `src/config/user_config.rs` `pub(crate) use user_config::*` 整体 re-export，改可见性/命名直接波及主 crate 全部配置消费点。

---

## `crates/user-config/src/lib.rs`（1316 行）

**角色**：LSP 用户配置的**单源真理**——强类型配置树 + JSON Schema 生成 + VS Code package.json/TS 产物生成 + 宽容解析（错误收集不中断）。

**关键结构与不变量**：
- `UserConfig`（L73）：12 个顶层节（files/workspace/scope/references/formatter/formatting/inlayHints/lens/semantic/diagnostics/signature/qihe），全部 `#[serde(default, deny_unknown_fields)]`——**未知字段拒收**与 schema `additionalProperties: false` 一致；`inlayHints` 等用 `#[serde(rename)]` 保持 camelCase JSON 名（L80-81）。
- 三态/默认值核心：`FilesWatcherDef`（L20，client/notify/server，默认 Client）、`ScopeVisibility`（L31，public/private，默认 Private）、`DiagnosticsUpdateUserConfig`（L50，onType/onSave，默认 OnSave）、`DiagnosticRuleSeverityUserConfig`（L58，ignore/info/warning/error/fatal）。
- `DiagnosticRuleUserConfig`（L425）：`selector` 正则 `^(code:[0-9]+:[0-9]+|option:.+|group:.+|source:(parse|semantic))$`（L427，schemars attr 与 VS Code 产物 L659 双份同步）+ `severity` + `force: bool`——slang 诊断按 code/option/group/source 四类选择器覆盖严重级。
- 默认值常量：`DEFAULT_QIHE_RUN_ARGS = ["-g", "std"]`（L9）、`DEFAULT_SLANG_WIDTH_WARNINGS = ["width-expand","width-trunc","port-width-expand","port-width-trunc"]`（L10-11）、formatter 默认 `--failsafe_success=false`（L205）。
- `ConfigSettingMeta`（L554）+ `USER_CONFIG_SETTINGS`（L690，29 项注册表)：**每条配置的 path/vscode_key/docs_group/i18n description key/default/schema 六元组**，是 schema 描述、VS Code 贡献点、生成 TS 三处产物的唯一数据源。`package_property()`（L600）产出带 `%key%` i18n 占位符的 VS Code 属性；`insert_schema()`（L629）按 `ConfigSettingSchema` 枚举（Boolean/StringOrNull/StringArray/Integer/Enum/DiagnosticRules）拼 JSON schema 片段。
- `USER_CONFIG_KNOWN_PATHS`（L1089，29 条）：形状校验路径表；`UserConfigPathNode`（L1122）构成路径树，`validate_user_config_shape`（L1165）沿树递归——已知节点继续下钻，未知 key 报 `unknown field`（JSON pointer 定位，`~`/`/` 转义 L1144），顶层 `$schema` 字段豁免（L1182）。
- `UserConfig::from_json`（L1301）：`null` → 全默认（L1305）；否则先形状校验收集 unknown-field 错误，再 `apply_user_config_fields`（L1213，`field!` 宏逐路径 `serde_json::pointer` 取值 + `parse_user_config_field` L1195 逐字段反序列化）——**单字段类型错误只进 error_sink 不影响其他字段**（部分应用语义）。

**公开 API**：`UserConfig::from_json(serde_json::Value, &mut Vec<(String, serde_json::Error)>) -> Self`（L1301）、`generated_user_config_schema() -> serde_json::Value`（L535，注入 `$id`/`x-vide-config-kind: "user"`/`$schema` 字段说明）、`generated_vscode_package_properties() -> Map<String, Value>`（L1025）、`generated_vscode_configuration_typescript() -> String`（L1033，生成 `USER_CONFIG_SETTINGS` TS 常量表）+ 全部配置结构体 pub。

**依赖/被依赖**：依赖 → 无 vide 内部依赖（仅 camino/schemars/serde/serde_json）；（related 出边）`schemas/v1/user-config.schema.json`。被依赖 →（imports）`src/config/user_config.rs`（`pub(crate) use user_config::*` 桥接到 ide/base-db 的 Config 结构）；生成产物被 xtask（`generate-config-artifacts`/`check`，xtask/src/main.rs L405-434）与 editors/vscode 消费。

**改动影响面**：加/改任何配置项需同步五处——结构体字段、`USER_CONFIG_SETTINGS` 注册表、`USER_CONFIG_KNOWN_PATHS`、`apply_user_config_fields` 的 `field!` 行、（重跑）`cargo xtask generate-schemas` + `generate-config-artifacts`（否则 CI 的 check 失败、VS Code package.json/TS 常量过期）；`deny_unknown_fields` 使新字段对旧客户端是硬错误；`src/config/user_config.rs` 的 `diagnostics_config()`（L30-48）把本类型桥到 base-db DiagnosticsConfig，字段语义变化影响全部 IDE 功能开关。

**集成点**：新配置项的标准流程（六处同步见上）；`error_sink` 模式（指针+错误对）供 LSP 层把配置错误作为 diagnostic 展示；`exposed_in_vscode: false` 通道支持仅 Neovim/Emacs initialization options 暴露、不进 VS Code 的设置。

---

## `crates/workspace-model/Cargo.toml`（12 行）【配置】

**作用**：声明 `workspace-model` crate（L4 description "Shared workspace model types"）——全仓共享的工作区类型层。

**关键字段**：`[dependencies]`（L8-12）仅 4 个——`salsa`（L9，SalsaValue unsafe impl 需要）、`triomphe`（L10，Arc）、`utils`（L11）、`vfs`（L12，FileSet/VfsPath/FileId）——刻意**不含 serde/schemars**：纯内部类型，无序列化面。

**改动的连带影响**：此 crate 被 base-db 与 project-model 双双依赖（crates/base-db/Cargo.toml L16），加依赖会同时拉进两条链；类型增删直接改 base-db salsa 输入的形状。

---

## `crates/workspace-model/src/lib.rs`（12 行）

**角色**：crate 门面——三个子模块声明 + 扁平 re-export。

**关键结构与不变量**：`pub mod project/source_db/source_root`（L1-3）；re-export 面（L5-12）：`CompilationProfile, CompilationProfileId, Predefine, PredefineSource, PreprocessConfig, ProjectConfig, SharedProjectConfig, SourceFileKind, SourceRoot, SourceRootConfig, SourceRootDiagnosticScope, SourceRootId, SourceRootRole`——外部 crate 可以 `use workspace_model::{...}` 扁平拿类型，也可以直接引子模块路径。

**公开 API**：即上述 13 个类型的 re-export；无自有逻辑。

**依赖/被依赖**：依赖 → `project.rs`、`source_db.rs`、`source_root.rs`。被依赖 → crate 依赖方 base-db 与 project-model（经 Cargo.toml）；图谱入边仅自身 Cargo.toml 的 configures。

**改动影响面**：re-export 列表是外部消费的稳定 API 面——删条目会破坏 `crates/base-db/src/lib.rs` 与 `crates/project-model/src/lib.rs` 的 `use workspace_model::{...}` 语句。

**集成点**：给共享模型加新类型时在此注册 re-export 即可让全仓扁平可用。

---

## `crates/workspace-model/src/project.rs`（130 行）

**角色**：编译 profile 数据模型——"哪些 source root 一起编译、顶层模块是什么、预处理器配置是什么"。

**关键结构与不变量**：
- `CompilationProfileId(pub u32)`（L7）+ `unsafe impl salsa::SalsaValue`（L10，SAFETY 注释：copy-only 'static 身份值）——可作 salsa 查询输入/输出。
- `ProjectConfig`（L84）：`root_profiles: Vec<Option<CompilationProfileId>>` 以 `SourceRootId.0 as usize` 为下标（`profile_for_root` L97），`profiles: Vec<CompilationProfile>` 以 `CompilationProfileId.0 as usize` 为下标（`profile` L101）——**两个平行索引必须由构造方（project-model `get_workspace_folder`）保持一致**；`Default` 为空（无 profile 状态 = best-effort 模式）。
- `CompilationProfile`（L77）：`{source_roots: Vec<SourceRootId>, top_modules: Vec<String>, preprocess: PreprocessConfig}`。
- `PreprocessConfig`（L13）：`{predefines: Vec<Predefine>, include_dirs: Vec<AbsPathBuf>}`；`Predefine`（L39）= `definition: String` + 可选 `PredefineSource { path, range }`（L71，manifest 跳转源）。不变量：predefines 排序由生产方保证（macro_def.rs L47），保证 salsa 输入确定性。
- `profile_ids()`（L113）：`u32::try_from(idx).unwrap_or(u32::MAX)`——超 2^32 profile 溢出静默坍缩（实际不可达）。

**公开 API**：`ProjectConfig::{new, profile_for_root, profile, root_profile_count, has_compilation_profiles, profile_ids, preprocess_for_profile}`（L90-127）、`PreprocessConfig::with_predefine_strings`（L19）与 `include_dir_strings/predefine_strings`（L29/L33，给 qihe 命令行拼接用）、`Predefine::{new, with_source, as_str}` + `From<String>/From<&str>`、`SharedProjectConfig = Arc<ProjectConfig>`（L130）。

**依赖/被依赖**：依赖 → `source_root.rs`（SourceRootId）、`utils/line_index.rs`、`utils/paths.rs`、triomphe/salsa。被依赖 →（imports）`crates/base-db/src/lib.rs`、`crates/base-db/src/project.rs`、`crates/project-model/src/lib.rs`、`crates/project-model/src/macro_def.rs`、`crates/workspace-model/src/lib.rs`。

**改动影响面**：`ProjectConfig` 被 base-db 包成 `ProjectConfigValue` salsa input（crates/base-db/src/source_db.rs L43-46、`set_project_config` L152 带 Durability）；`preprocess_for_profile` 是 preproc-expand 四处消费的核心查询入口（compilation_plan.rs L214、source_db/queries.rs L88、preproc/predefines.rs L7/L23）——None profile 返回 `PreprocessConfig::default()`（L126）的语义（空 predefines+include_dirs）决定未配置项目的预处理行为。

**集成点**：`SharedProjectConfig` 是跨线程共享句柄（global_state 持有 + analysis Host 同步）；新增编译开关（如 `+incdir` 以外的 slang 选项）在此扩展 PreprocessConfig 并在 project-model `semantic_profile()`（lib.rs L294）组装。

---

## `crates/workspace-model/src/source_db.rs`（72 行）

**角色**：文件级身份分类——由路径推断 SourceFileKind，驱动"哪些文件是独立编译/诊断单元"。

**关键结构与不变量**：
- `SourceFileKind`（L4）：`SystemVerilog`（默认兜底）| `IncludeHeader` | `LibraryMap` | `ProjectManifest`。
- `from_path`（L17）分类规则（大小写不敏感）：`vide.toml` → ProjectManifest（L19，与 project_manifest.rs 的 MANIFEST_FILE_NAME 硬编码耦合）；`*.map` → LibraryMap（L22）；`*.vh/*.svh/*.svi` → IncludeHeader（L23-24）；**其余一律 SystemVerilog**（L28，包括 `.v`/`.sv` 及任何未知扩展）。
- 单元判定不变量：`is_semantic_compilation_unit()` 与 `is_slang_parse_unit()`（L32-38）当前等价 = `SystemVerilog | LibraryMap`——**头文件与 manifest 不是独立 parse 诊断单元**（只能被 include 消费）；测试 L48-71 钉死这三类行为。

**公开 API**：`SourceFileKind::{from_path(&VfsPath), is_project_manifest, is_semantic_compilation_unit, is_slang_parse_unit}` + Copy/Default derive。

**依赖/被依赖**：依赖 → `vfs/src/lib.rs`（VfsPath）。被依赖 →（imports）`crates/base-db/src/source_db.rs`（包成 `SourceFileKindValue` salsa input，L27）、`crates/workspace-model/src/lib.rs`、`crates/workspace-model/src/source_root.rs`（file_kind 组合用）；行为消费方 `crates/preproc-expand/src/{db.rs L155/L375, compilation_plan.rs L249}`。

**改动影响面**：改分类规则直接改变诊断范围（preproc-expand db.rs L375 的 parse 闸门）与编译计划成员（compilation_plan.rs L249）；`vide.toml` 判定与 project_manifest.rs MANIFEST_FILE_NAME、schema `x-vide-manifest-names` 三处必须同步改。

**集成点**：新增文件类别（如未来的 `*.f` filelist、`*-pkg.sv` 特判）在此加枚举变体 + from_path 分支 + 单元判定。

---

## `crates/workspace-model/src/source_root.rs`（294 行）

**角色**：source root 运行时模型 + 角色策略中枢——VFS FileSet 的分区包装，Local/BestEffortIndex/Library/Ignored 四角色的全部行为决策集中于此。

**关键结构与不变量**：
- `SourceRootId(pub u32)`（L6）+ salsa::SalsaValue（L9）。
- `SourceRootRole`（L12）四角色 + 策略方法集（L26-67）：`is_watched` = Local|BestEffortIndex（loader watch 决策）；`participates_in_semantic_profile` = Local|Library（profile 计入与缺 profile 报告）；`supports_root_scoped_compilation`/`reports_missing_profile` 同上；`diagnostic_scope()`（L51）：Local|Library→Workspace（全工作区诊断）、BestEffortIndex→OpenFile（只诊断打开的文件）、Ignored→Disabled；`allows_workspace_edits` = !BestEffortIndex（rename 等跨文件编辑闸）；`publishes_unopened_workspace_diagnostics` = !BestEffortIndex（**Ignored 也发布空报告**，用于清除旧配置的 stale diagnostics，L63-67 注释钉版）。
- `SourceRoot`（L71）：`role + source_files: Option<Vec<FileId>> + file_set: FileSet`。**核心不变量在 `file_kind()`（L152）**：当 `source_files` 为 Some（即 manifest 显式给了 `sources` 的 source-filtered root）时，不在列表内的文件一律降级为 `IncludeHeader`（L160-166）——例外：LibraryMap/ProjectManifest 保持原类。`source_files = None` 时纯按扩展名分类。
- `SourceRootConfig`（L171）：`{fileset_config: FileSetConfig, fileset_roles: Vec<SourceRootRole>}`，`Default` = 空 fileset + `[Ignored]`（L176-183）。`partition(&Vfs) -> Vec<SourceRoot>`（L186）：`debug_assert` roles 长度 == 分区数（L188，release 下越界走 fallback）；**fallback 角色**：最后一个分区 → Ignored、其余 → Library（L200-204）；Ignored root 丢弃 source_files 跟踪（L208-210）。

**公开 API**：`SourceRoot::{new, with_source_files, new_local/library/best_effort_index/ignored, new_local_with_source_files, ...}`（L78-122）、`SourceRoot::{role, path_for_file, file_for_path, resolve_path, iter, file_kind}`（L124-167）、`SourceRootConfig::{partition}`、`SourceRootRole` 全策略方法、`SourceRootDiagnosticScope`。

**依赖/被依赖**：依赖 → `source_db.rs`、`vfs/src/lib.rs`。被依赖 →（imports）`crates/base-db/src/lib.rs`、`crates/base-db/src/source_root.rs`、`crates/project-model/src/lib.rs`、`crates/workspace-model/src/lib.rs`、`crates/workspace-model/src/project.rs`；策略消费方 `crates/ide/src/diagnostics.rs`、`src/global_state/snapshot.rs`（graph 佐证）。

**改动影响面**：角色策略方法变化连锁 ide 诊断范围（diagnostics.rs）、rename/edit 闸门、watcher 注册（reload.rs `is_watched` 语义经 project-model watch 下标传递）；`partition` 的 fallback 语义变化影响未注册分区的默认行为；`file_kind` 降级规则变化改变显式 sources 项目里同名 .sv 文件的语义身份（project-model 测试 `explicit_single_file_source_*` L1312-1402 依赖它）。

**集成点**：新增角色（如未来的 Generated/ThirdParty 混合角色）需在此补全全部策略方法（测试 `source_root_role_policies_are_explicit` L264 要求显式枚举断言）；`SourceRootConfig` 是 VFS 分区 → 语义 root 的唯一桥，集成新 VFS 分类维度时扩展 `partition_with_source` 消费即可。

---

## `schemas/v1/vide.schema.json`（97 行）【配置·生成物】

**作用**：`vide.toml` 项目清单的 JSON Schema（tombi/编辑器给 TOML 配置补全与校验用）——**由 `project_model::generated_toml_manifest_schema()` 生成、check-in、禁止手改**。

**关键字段**：`$id = https://vide.pascal-lab.net/schemas/v1/vide.schema.json`（L2）；六属性 top_modules/defines/sources/include_dirs/libraries/exclude（L8-90）与 `TomlManifestSchema` 字段一一对应（描述文本、examples 直接来自 toml_workspace.rs schemars attr）；`additionalProperties: false`（L92）；`x-tombi-table-keys-order: "schema"`（L93，指示 tombi 按 schema 声明序排列键）；`x-vide-manifest-names: {primary: "vide.toml"}`（L94-96，由 generated_toml_manifest_schema L137-143 注入）；defines 的 pattern（L26）与运行时 `MACRO_DEFINITION_SCHEMA_RE` 双份同步。

**改动的连带影响**：CI `cargo xtask check-schemas`/内嵌测试比对生成物与此文件（xtask/src/main.rs L479、L524-525），手改必被 `run cargo xtask generate-schemas` 覆盖判 stale；改 `TomlManifestSchema` 后必须重新生成，否则 tombi 补全与实际解析行为脱节。

---

## `schemas/v1/user-config.schema.json`（750 行）【配置·生成物】

**作用**：LSP 用户配置 JSON Schema（Neovim/Emacs 等直配 LSP 的编辑器用）——由 `user_config::generated_user_config_schema()` 生成、check-in。

**关键字段**：`$id`/`x-vide-config-kind: "user"`（L748-749，由 generated_user_config_schema L539-540 注入）；顶层 12 节 + `$schema` 透传字段（L159-162，"Vide ignores this field"，from_json L1182 豁免对应）；`$defs`（L165-746）完整镜像 UserConfig 结构树（约 30 个定义，全部 `additionalProperties: false`）；diagnostics.slang.rules 的 selector pattern 与 severity enum（L641-671）同 `DiagnosticRuleUserConfig` 的 schemars attr；默认值快照（如 slang warnings 四项 L623-628、qihe runArgs `["-g","std"]` L739-742）与 user-config.rs 的 Default impl 一致。

**改动的连带影响**：同上由 xtask check 强制同步；改 UserConfig 后需 `cargo xtask generate-schemas`（连带 `editors/vscode` 的 schema constants TS 与 package.json contributes 段一起由 `generate-config-artifacts` 刷新，xtask/src/main.rs L405-413）；该文件与 `USER_CONFIG_SETTINGS`/schemars 描述任何漂移都会让 CI 失败——**正确的修改路径永远是改 Rust 源再生成，而非改 JSON**。
