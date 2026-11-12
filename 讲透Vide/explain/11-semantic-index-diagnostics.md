# 11 · 语义索引与诊断管线（crates/ide/src/semantic_index.rs + diagnostics.rs）

## 角色定位

单点查询（hover、goto）可以现算，但「找出某定义的全部引用」「重命名要改哪些文件」「模块层级图」是工作区级问题——每次按键都全仓解析不现实。`ide/src/semantic_index.rs`（图谱度数 88）为此维护两份索引：`ModuleIndex`（模块名 → 定义）与 `SemanticIndex`（DefId → 引用组 + 模块调用边），以「per-file 构建 + merge 时纯内存装配」的两级结构把失效压到单文件。`diagnostics.rs` 是诊断总装线：把 slang parse 诊断、slang 语义诊断、HIR lowering 诊断与 vide 自有检查统一成一种 `Diagnostic` 模型，再按 source root 作用域分流发布。两者共享同一设计哲学：**索引/诊断都是派生视图，权威数据在 salsa 缓存的查询里，装配层只做搬运与合并**。

## 内部结构

**semantic_index.rs**（854 行）的值类型：`SemanticDefinitionRange{file_id, range}`（L28-32）；`ReferenceContext`（L49-75）为命名端口连接预计算上下文——`ConnName`（`.name` 侧，带 ident_range/collapse_range/shorthand/side/paired）与 `ConnData`（数据标识符侧）——L43-48 注释点明动机：rename 等消费者**永不重解析**，索引期一次算清；`paired` 正是「.name(x) 同名连接」时另一侧的定义。`SemanticReference`（L90-97）= 位置 + 类别 + `SyntaxTokenPtr` + context。三个索引结构：`ModuleIndex`（L130-133）、`SemanticIndex`（L135-140，references_by_definition + 双向模块调用边）、per-file 三件套 `FileSemanticIndex/FileModuleIndex/FileModuleEdges`（L144-172）——L142-143 注释：per-file 切片不含跨文件定义区间，那部分 merge 时一次算清。

两个 for_source_root 是装配核心：`ModuleIndex::for_source_root`（L183-226）遍历 root 全部文件，L191-197 把 `HirFileId::File` 与 `macro_files_for_file` 产出的宏文件并列排序去重——**宏生成的模块与手写模块进同一张索引**；逐文件读 `db.item_tree` 的 module_headers，可实例化的才建 `SemanticModuleDefinition`（L201-209），同名桶内按 (file_id, name_range) 排序去重（L215-223）。`SemanticIndex::for_source_root`（L286-325）逐文件取 `db.file_semantic_index(file_id)` merge 进 builder：定义区间经 `definition_ranges_for`（build.rs）一次解析（L305），引用直接 extend（L309）；文件级模块边同时推入 caller 的 outgoing 与 callee 的 incoming（L311-314）。L299 的 `db.unwind_if_revision_cancelled()` 是取消检查点。查询面 L327-356；顶层 `module_edges`（L374-391）跨 root 聚合排序去重。per-file 构建在 `semantic_index/build.rs`：`FileSemanticIndex::for_file`（L43 起）先判 `has_preproc_tokens`（L50-56，include 边或非 Source origin token 存在才建 emitted_index），随后 `root.elem_preorder()` 全树扫描 name-like token 解析归属。

**diagnostics.rs**（1308 行）：L34-38 `DiagnosticSource` 三源（SlangParse/SlangSemantic/Vide）；`Diagnostic` 结构（L41-55）统一携带 code/subsystem/name/option_name/groups/range/severity/message/args/tags；L64-75 的 `expected_token()` 把 slang `ExpectedToken` 诊断的 `args[0]` 解释为缺失 token——L66-73 注释钉版这是**位置性假设**，slang 升级需复查。vide 自有检查描述符在 L18-23。查询族：`parse_diagnostics`（L159-167，manifest 分叉 + db.parse_diagnostics 过滤）、`compilation_diagnostics`（L169-174）、`compilation_profile_diagnostics`（L176-193，slang 诊断 + vide 检查合并）、`diagnostics`（L235-248，按 source root 作用域分流）、`source_root_diagnostics`（L250-262，三档作用域 Disabled/OpenFile/Workspace）。

## 外部连接

索引上游：`db::{WorkspaceSymbolIndexDb, source_root_*_for_root}`、`macro_file::macro_files_for_file`、`item_tree/module_headers`、`db.body_with_source_map`（build.rs L820 取 caller body）。查询面挂载在 `db/workspace_symbol_index_db.rs`：trait `WorkspaceSymbolIndexDb: SourceRootDb + TyDb`（L17-18），`impl dyn` 暴露 `file_semantic_index/file_module_index/file_module_edges/source_root_semantic_index/source_root_module_index`（L29-56）与 `workspace_source_root_ids`（L64-70）。注意这些是普通函数非 tracked——增量性由底层 salsa 查询承担（ide 层唯一 tracked 查询是 line_index）。诊断上游：preproc-expand 的三类诊断查询（第 6 篇）、`module_resolution` 的歧义检测；`DiagnosticSource::Vide` 走 L280 起的可插拔 provider 注册表。下游：references/rename（引用组 + paired 连接）、call hierarchy（模块调用边）、`src/global_state/diagnostics`（发布与新鲜度治理）。

## 数据流

**索引数据流**（以 rename 为例）：用户按 F2 → ide 层定位 DefId → `db.source_root_semantic_index(root_id)` 触发 merge（若上游 body/item_tree 失效，Salsa 先重算；merge 本身重跑但只是拼 HashMap）→ `index.references_for_definition(def_id)` 拿全仓引用组 → 命名端口连接的 rename 经 `reference.context.paired()`（L81-87）找对侧定义——这正是 vscode 扩展「Rename Connected Ports/Signals」递归重命名（extension.ts 的 renameExpansionInfo 请求）的索引侧支柱，`recursive_rename_closure`（workspace_symbol_index_db.rs L75-82）求连通闭包。**诊断数据流**：主循环每轮 `process_changes` 后按文件重派诊断任务 → 后台线程对每文件调 `diagnostics(db, file_id)`（L235）：OpenFile 作用域走 `syntax_diagnostics`（parse + vide 检查），Workspace 作用域走 profile 级 slang 语义诊断（buffer→FileId 映射回第 6 篇）→ 结果封装 `PublishDiagnosticsBatch` 携带新鲜度回主循环 → 校验通过才发布（stale 批丢弃，event_loop 测试 `stale_diagnostics_batch_does_not_publish` 锁定）。

## 设计决策

**为什么索引分 per-file 与 root-merge 两级？** 单文件编辑只重跑该文件的 `file_semantic_index` 与最终 merge（L283-285 注释：merge 是纯内存装配、零名字解析）——重活（解析、lower、引用解析）在 per-file 层且被 salsa 托管。一步到位建全仓索引的话，任何编辑都是全量重扫。

**为什么 rename 语义（paired/shorthand）烧进索引？** 引用发现是高频且语义敏感的操作（`.clk` 与 `.clk(clk)` 的同名折叠、无括号简写两侧），每次现判既慢又容易各消费者判不一致。ReferenceContext 构建期定型（L43-48 注释「never re-resolve」），rename/highlight 共享同一份事实。

**为什么诊断要「作用域」概念？** 大工作区里库文件、被忽略目录不该产生诊断洪流；SourceRoot 的 role 决定三档（L250-262），配置了 profile 的工程里 Disabled root 直接静默（L239-245）。这把「诊断多少」从隐式实现细节变成显式工程配置。

**为什么 ide 层不建自己的 tracked 索引查询？** 见第 3 篇：索引查询的输入是几十个底层查询的联合，手写依赖声明极易漏；让 merge 每次重跑、底层缓存兜底，牺牲少量 CPU 换正确性。`unwind_if_revision_cancelled`（L299）保证长 merge 不卡快照切换。

## 新人提示

1. 新增引用类别：先在 ReferenceCategory 加类，再在 build.rs 的 token 扫描里归类——消费者（references.rs）自动看到，勿在消费侧重解析。
2. 改 SemanticReference 结构会波及全部快照测试；先跑 `semantic_index` 相关 insta 再说。
3. 诊断不显示的排查链：source root 作用域（L250-262）→ profile 是否解析出（第 6 篇 path_file_ids）→ 新鲜度修订号（global_state 的 DiagnosticFileRevision）→ 才是诊断本身。
4. `expected_token()` 的 args[0] 假设（L66-73）在升级 slang 后必须人工复核，快照 `insert_expected_token` 是安全网。
5. 模块调用边的排序键是五元组（L440-449），新增字段时保持确定性排序，否则快照会随机漂移。
