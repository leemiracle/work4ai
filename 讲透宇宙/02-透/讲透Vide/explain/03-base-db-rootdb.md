# 03 · Salsa 增量查询底座与 RootDb 组合（crates/base-db + crates/ide/src/db/root_db.rs）

## 角色定位

vide 的全部语义计算建立在一个「自底向上的增量数据库」之上：`base-db` 定义最底层输入（源文本、source root、工程配置），`root_db.rs` 则把分散在各 crate 的数据库 trait 组装成一个具体可实例化的 `RootDb`。L1-5 的 crate 文档钉死了分层宪法：base-db「拥有源文本、source root、工程配置与共享数据库原语；最底层数据库不得依赖预处理、lowering、名字解析或类型」。这条单向依赖链（base-db → preproc-expand → hir-def → hir-ty → ide）是整个仓库最重要的架构不变量——每一层的 Db trait 只继承下层，具体实现只在最顶端 RootDb 出现一次。Salsa 0.28 的查询调度（变更失效、LRU、durability 分级）在此层完成全部接线。

## 内部结构

base-db 七个模块（lib.rs L9-14）：`analysis_snapshot`（快照 id）、`change`（变更搬运）、`diagnostics_config`、`project`（ProjectConfig/CompilationProfile）、`source_db`（核心输入 trait）、`source_root`。L7 `pub use salsa::{self, Cancelled}` 把 salsa 直接转售给上层，避免各 crate 各自依赖版本漂移。

**source_db.rs 的输入建模**是本层精华。Salsa 0.28 要求输入是 `#[salsa::input]` 结构：`SourceFile`（L48-54，text + kind 两个字段，`returns(clone)`/`returns(copy)` 控制 getter 形态）、三个 singleton 输入 `SourceFiles`（L56-60，`FxHashMap<u32, SourceFile>` 全量注册表）、`SourceRoots`（L62-68，roots + file_root_ids 双映射）、`ProjectInputs`（L70-76，诊断配置 + 工程配置）。由于 Salsa 值要求 `'static` 且无数据库生命周期引用，L22-46 用四个 newtype wrapper（`SourceFileKindValue` 等）配 `unsafe impl SalsaValue` 显式担保——每个都有 SAFETY 注释声明理由。

消费接口是两个 trait：`SourceDb`（L82-158）提供 `file_text(file_id) -> Arc<str>`（L84-86，经 `source_file` 私有函数 L240-246 查注册表）、`file_kind`、`files()`，以及一组 `set_*_with_durability` 写入器（如 L105-112 的 `set_file_text_with_durability`）；`SourceRootDb: SourceDb`（L160-238）追加 `source_root_id`（L162-170，缺 root 直接 panic）、`source_root`、`file_path`（L188-192，委托 VFS FileSet 的 `path_for_file`——注释强调「不再存储冗余 PathBuf 副本」）、`file_compilation_profile`（L218-232，root→profile 映射并报告缺失）。L261-278 的 `ensure_*` 辅助函数实现「singleton 输入不存在则现场创建」的惰性初始化。

**change.rs** 是 VFS→Salsa 的翻译官：`Change` struct（L11-16）携带 `roots/project_config/changed_files` 三组可选载荷；`apply(self, db: &mut dyn SourceRootDb)`（L35-81）按序写入——先 project config（L36-38），再逐 root 注册 `set_source_root_id/file_kind/source_root`（L40-51），最后逐 changed file 设 text（L55-76），文件集合有增删时刷新 `set_files_with_durability`（L78-80）。L84-86 的 `durability()` 把 library root 定为 `Durability::HIGH`（库文件极少变，失效广播可跳过）、本地 root 为 `Durability::LOW`。

**root_db.rs** 只有 92 行却完成整座积木的合体：L17-21 `pub struct RootDb { storage: salsa::Storage<Self> }`；L23-45 用八个 `#[salsa::db] impl` 块依次实现 `salsa::Database`、`SourceDb`、`SourceRootDb`、`PreprocDb`、`HirDefDb`、`TyDb`、`LineIndexDb`、`WorkspaceSymbolIndexDb`——每块两行，声明式到近乎配置文件。L53-59 手写 `FileLoader for RootDb`（路径解析委托 source root 的 resolve_path）。`RootDb::new`（L61-72）初始化三个 HIGH durability 输入并调 `update_parse_query_lru_capacity`（L74-78）统一设 parse/HIR 查询 LRU（默认 128，L81）。

## 外部连接

上层与 RootDb 的交互全走 `ide::analysis_host`：`AnalysisHost { db: RootDb, snapshot_id }`（analysis_host.rs L9-12），`make_analysis`（L19-22）clone 出 `AnalysisSnapshot { db, snapshot_id }` 交给只读消费者（RootDb 是 `#[derive(Clone)]`，Salsa Storage 的 Arc 结构使 clone 廉价且共享缓存）；`apply_change`（L24-27）→ `db.apply_change(change)` + 修订号自增。`src/global_state.rs` L199-201 在启动时创建 host 并写入诊断配置。各中间 crate 只写 trait：`PreprocDb: SourceRootDb`（preproc-expand/db.rs L420-421）、`HirDefDb: PreprocDb`（hir-def/db.rs L20）、`TyDb: HirDefDb`（hir-ty/db.rs L8）——组合后的 trait 面通过 `impl Deref for dyn X` 逐层下放（root_db.rs L86-92、hir-def/db.rs L23-27），避免为每层重写转发方法。

## 数据流

一次文档修改在数据库层的传播链：`GlobalState.process_changes`（process_changes.rs L26 起）拿 VFS 变更 → 组装 `base_db::Change`（`add_changed_file`，change.rs L31-33）→ `AnalysisHost::apply_change` → `Change::apply(db)`：对每个 changed file，先经 `db.source_root_id(file_id)` 定位 root（change.rs L57），取 durability（L59），再 `db.set_file_text_with_durability(file_id, text, durability)`（L73-75）——text 来自 `changed_file.text().unwrap_or_else(|| Arc::from(""))`，删除即空串。Salsa 检测到该输入变更后，所有依赖该 file_text 的 tracked 查询（parse → 宏展开 → body → 类型）在下次访问时按依赖图精确重算；durability 为 HIGH 的输入不触发全局失效。查询侧最简例子是 `LineIndexDb::line_index`（line_index_db.rs L18-21）：`#[salsa::tracked(lru = 256, returns(clone))]`，输入是 interned 的 `SourceFileQueryKey`（ide/db.rs L8-12，注释解释了 FileId 整数需包装才能当 tracked 函数 key 的原因）。

## 设计决策

**为什么 trait 分层而不是一个大 Db trait？** 每个 crate 只依赖它需要的查询面：preproc-expand 的代码签名只接受 `&dyn PreprocDb`，编译期就杜绝它调用 HIR 查询形成环。 trait 层次与 crate 依赖同构，Cargo 的依赖图即架构图。代价是 trait 漂亮但「具体类型唯一」——RootDb 因此成为唯一需要维护 impl 块的地方，新增一层 Db 时 root_db.rs 加两行即可。

**为什么用 singleton 输入聚合而不是每文件一个顶层输入？** Salsa 0.28 里输入修改即产生新 revision。若 files 逐个 set，revision 爆炸；`SourceFiles` singleton（L56-60）把「文件集合变更」收敛为一次输入写（change.rs L78-80 只在增删时写），文本变更仍走 per-file 的 `SourceFile` 输入保持细粒度失效。这是精确失效与低广播成本的折中。

**为什么 `ensure_*` 惰性初始化？** 测试里常见裸 `TestDb`（见 preproc-expand/db.rs L818-842 的四行 impl 模式）不预置输入；ensure 系列让 set 永远合法、get 缺失才 panic，容错面集中到读侧。

**为什么 ide 层大多不再建 tracked 查询？** 见 root_db 组合的 `LineIndexDb` 与 `WorkspaceSymbolIndexDb`：ide 的索引（语义引用、模块图）以普通函数暴露（workspace_symbol_index_db.rs L85-153 无 tracked 标注），增量性由其调用的底层 salsa 查询（item_tree、body）承担——ide 层只做「装配」，把缓存责任下推，避免索引自身再维护一套依赖声明。唯一例外 line_index 是纯文本派生且高频，值得独立 LRU。

## 新人提示

1. 新增输入字段时三处同步：source_db.rs 的 wrapper + input struct + trait getter/setter，缺一处会拿到默认值而非编译错误（singleton ensure 兜底会静默创建空表）。
2. durability 语义要谨慎：误把 LOW 数据标 HIGH（如打开的文档），客户端编辑将不触发重算——表现为「改了代码诊断不动」。排查时先看 change.rs L84-86 走到哪个分支。
3. RootDb 的 Clone 是 Salsa 的快照机制核心（storage 内部以 Arc 共享查询缓存），别在 Clone 上手工复制大字段。
4. 单测数据库照抄 preproc-expand/db.rs L818-855 的 TestDb 模板：Storage + 五个 impl 块 + FileLoader + Debug，二十行内搭好可查询的 db。
