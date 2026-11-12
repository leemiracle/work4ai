# 10-hir-def-a 精读手册

> 模块定位：本单元是 `hir-def` crate（Salsa HIR 第一层"定义层"）的核心骨架与通用 lowering——AST 身份系统（`ast_id_map`/`def_id`）、owner 局部的 HIR 存储仓（`body`/`container`）、Salsa 查询门面（`db`）、表达式/类型/声明/说明符四条 lowering 主线（`expr` 家族、`declaration`）、文件级结构摘要（`item_tree`）、包导出图（`design_map`）、文件级诊断聚合（`diagnostics`），以及 class/断言/bind/checker/constraint/covergroup/DPI/extern/文件级构造等各语法域的降级器。crate 铁律（lib.rs L1-9）：ECS 风格 arena+本地索引+容器 ID，只准依赖 `preproc-expand`，禁止依赖类型推断/IDE；标识符是 workspace 内部接口而非稳定 OO 门面。

---

## `crates/hir-def/Cargo.toml`（20 行）
**作用**：定义 `hir-def` crate（v0.0.0）的依赖面。
**关键字段**：dependencies 全部走 workspace 继承（L7-19）——`base-db`（Salsa storage 宏）、`preproc-expand`（HirFileId/PreprocDb 上游）、`syntax`（slang AST）、`vfs`、`utils`（text_edit/get/宏）+ 工具库 `itertools/la-arena/parking_lot/rustc-hash/salsa/smallvec/smol_str/tracing/triomphe`。无 dev-dependencies、无 features、无 `[lib]` 段（默认 src/lib.rs）。
**改动的连带影响**：此 crate 被 `hir-ty`/`hir-semantics`/`ide` 直接依赖；新增依赖等于放宽 lib.rs L6-8 声明的分层边界（禁止依赖推断/语义适配/IDE），review 时该文件是分层契约的第一检查点。`parking_lot` 目前仅在 crate 内同步原语使用，动它不影响下游编译面。

---

## `crates/hir-def/src/db.rs`（155 行）
**角色**：`HirDefDb` Salsa 数据库 trait 与全部文件级/owner 级查询的统一门面（`impl dyn HirDefDb` 上挂方法）。
**关键结构与不变量**：
- `HirDefDb: PreprocDb`（L25）——空 trait，仅作 Salsa `#[salsa::db]` 组合点；`impl Deref for dyn HirDefDb -> dyn PreprocDb`（L29-35）让下层查询在组合后的 dyn trait object 上直接可用（注释 L27-28 明说是为避免逐个转发）。
- `set_lru_capacity(db, capacity)`（L143-155）：11 个 tracked query 的 LRU 统一调容入口（ast_id_map/body/def_id/design_map/item_tree/owner/unit_index/scope/source_projection/region_tree/default_nettype）——IDE 内存预算的唯一旋钮。
**公开 API**（`impl dyn HirDefDb + '_` L37-140）：`syntax_file(HirFileId)->SyntaxFileId`（L39，HirFileId→数据库 intern 键）、`ast_id_map`（L45）、`owner_table`（L50）、`body_with_source_map(OwnerId)->Arc<Lowered<Body>>`（L54）、`body`（L58，`.data()` 投影）、`definition_table`（L62，pub(crate)）、`item_tree`/`item_for_owner`/`signature_for_owner`（L66/70/74）、`source_projection`（L78）、`owner_region_tree`（L82）、`file_lowering_diagnostics`（L90）、`scope`/`unit_scope`（L97/101）、`unit_index`（L105）、`subroutine`（L109，debug_assert OwnerKind::Subroutine + expect 有签名）、`package_export_signature`/`package_exports`（L119/123，expect "package owner must be present in the design map"）、`default_nettype_directives`（L130，pub(crate)）、`design_map`（L137）。
**依赖/被依赖**：依赖（出边）→ `base-db/src/lib.rs`、ast_id_map、body、def_id、design_map、diagnostics、item_tree、owner、scope、source_map、source_projection、subroutine、unit_index、utils/text_edit；被依赖（入边，34 个）→ crate 内几乎所有查询实现文件（ast_id_map/body/container/covergroup/def_id/design_map/diagnostics/file/has_source/item_tree/lower/module/module::clocking/module::generate/owner/pathres/region_tree/scope/source_map/source_projection/symbol/ty/unit_index）以及 `hir-semantics`（semantics.rs/hir_to_def/pathres/source_to_def、preproc_integration_tests）、`hir-ty/src/db.rs`、`hir-ty/tests/type_system.rs`、`ide/src/db/root_db.rs`、`ide/src/definitions.rs`、`ide/src/module_resolution.rs`。
**改动影响面**：新增/删除门面方法必须同步 `set_lru_capacity` 清单（漏一个即 LRU 失控）；改 `subroutine`/`package_exports` 的 expect 语义会让畸形 owner 从 panic 变静默错误面；`Deref` 实现若被改成显式转发会破坏"Salsa 把 tracked 方法挂在 dyn Db 上"的机制（注释 L27-28）。
**集成点**：二开者从这里拿全量 HIR 查询；`RootDb`（ide 侧）组合本 trait 后 IDE 各 feature 只经此 seam 访问定义层，不触内部 arena。

---

## `crates/hir-def/src/ast_id_map.rs`（367 行）
**角色**：文件级"稳定 AST 身份"系统——`SourceAstId` 用结构路径哈希（非 arena 序号）标识语法节点，是全部 HIR↔source 映射的锚点。
**关键结构与不变量**：
- `SyntaxFileId`（L25，`#[salsa::interned]`）：HirFileId 的数据库 intern 包装，"给每个文件级查询一个真正的 Salsa key"（注释 L21-24）。
- `SourceAstId(pub u128)`（L33）：128 位稳定身份。**不变量**（doc L1-7）：路径 = (SyntaxKind, 同 kind 兄弟出现序) 链；无关 body 增长不改变已有 id，结构性插入只允许改变同 kind 后继的 id。
- `StablePath`（L52）：`Vec<StableSegment>`，child() 追加段。
- `AstIdMap`（L68-75）：六张表——`nodes`(id→ptr，唯一 ptr 才收)、`by_ptr`、`by_identity`(usize 语法节点身份)、`by_path`、`paths`(id→path)、`by_preorder`(id→DFS 序，**仅同 revision 内可比**，注释 L147-151)。`from_source`（L78-132）：preorder 遍历建路径；id 冲突时 salt 递增重哈希（L112-120）；重复显示指针（宏展开产物）不进 ptr 表、走 path/identity 回退。
- `stable_id(path, salt)`（L226-235）：双 FxHasher（第二个掺 0x9e37_79b9 golden ratio）拼 128 位。
**公开 API**：`len/is_empty`（L134/138）、`ptr(id)->Option<SyntaxNodePtr>`（L142）、`preorder(id)->Option<u32>`（L149）、`node(id, &tree)`（L153，ptr 命中优先，miss 则按 StablePath 重走 preorder 定位——跨 revision 找回节点）、`id_of_node`（L184，identity 优先 ptr 兜底）、`id_of_node_in_tree`（L192，先验证 target 根==tree 根）、`id_of_ptr`（L205）。查询 `ast_id_map(db, SyntaxFileId)`（L238，tracked lru=1024）；`set_ast_id_map_lru_capacity`（L242）。
**依赖/被依赖**：依赖 → `db.rs`、`syntax`（SyntaxKind/SyntaxNode/ptr/has_text_range）、`preproc_expand::file::HirFileId`、rustc-hash、triomphe；被依赖（19 入边）→ body/checker/db/def_id/diagnostics/expr::data_ty/has_source/item_tree/lib/lower/module::port/owner/source_map/source_projection/ty + hir-semantics（resolver/source_to_def）+ ide（folding_ranges/inlay_hint）。
**改动影响面**：id 算法变了 = 所有缓存 OwnerId/DefId/source map 一次性作废（等效全量重 lower）；`node()` 的 path 回退被删则宏展开节点在 revision 变更后解析不出；内嵌 6 个测试（L258-351，`stable_ids_are_unique_and_round_trip`/`appending_a_member_does_not_renumber_existing_nodes`/`body_edits_keep_later_owner_ids` 等）是稳定性的回归闸，`cargo test -p hir-def` 跑。
**集成点**：任何要"跨编辑保持身份"的新 HIR 实体（新 owner 类型、新 arena）都必须用 SourceAstId 做 source 锚（alloc_with_source* 系列已封装）；`by_preorder` 提供同 revision 内源码序比较，供排序类 IDE 功能复用。

---

## `crates/hir-def/src/container.rs`（169 行）
**角色**：容器寻址原语（`OwnerRef`/`InFile`）+ OwnerId 到 checker/covergroup/clocking/scope-kind 的投影 + 词法作用域链（`ScopeChain`/`ScopeParent`）。
**关键结构与不变量**：
- `OwnerRef<T>`（L17-21）：`{value: T, cont_id: OwnerId}`——**owner 局部 arena 索引**，`value` 只在该 owner 的 store 内有意义；`with_value`/`map` 保容器投影（L28-34）。Copy 只对 `T: Copy`。
- `define_container_id!` 宏（L39-66）产出 `InFile<T>{value, file_id: HirFileId}`（L68-70）；注释 L62-63 钉死：typed wrapper 不隐式转 owner-local 引用。
- `OwnerId::as_checker/as_covergroup/as_clocking_block`（L74-87）：**只对对应 OwnerKind** 成立（`.then_some`），取 `body(db).checkers/covergroups/clocking_blocks` 首元素——隐含不变量：这三种 owner 的 body 里恰有一个该类定义。
- `scope_kind`（L89-108）：OwnerKind×ModuleKind → `symbol::ScopeKind` 全映射（Module→Module/Interface/Program/Package；AnonymousProgram→Program；…）。
- `OwnerId::data/source_map`（L113-119）：`db.body_with_source_map` 的两个投影——全 crate 读 Body 的规范入口。
- `ScopeChain`（L127-147）：SmallVec<[OwnerId;4]>，**从最内层向外**排序（doc L122-125：用值对象防止调用方各自重建 parent 遍历而改变遮蔽优先级）；`ScopeParent`（L150-168）是 `owner.parent(db)` 的懒迭代器。
**公开 API**：如上 + `ScopeChain::from_inner(db, owner)`（L132）/`ids/iter/is_empty`。
**依赖/被依赖**：依赖 → body/checker/covergroup/db/module（ModuleKind、clocking）、owner、symbol、smallvec、preproc_expand、triomphe；被依赖（**47 入边，全 crate 之最**）→ crate 内 aggregate/body/def_id/design_map/diagnostics/expr::data_ty/file/has_source/pathres/scope/symbol/typedef + hir-semantics 全线（semantics/hir_to_def/pathres/resolver/source_to_def）+ hir-ty 全线（db/display/infer/members/ty/type_system）+ ide 十余文件（code_action 各 handler/hover/goto_definition/rename/semantic_index/signature_help…）。
**改动影响面**：`ScopeChain` 内外序倒置 = 全部名字解析遮蔽规则反转；`as_*` 三投影的不变量（owner body 内首元素即唯一定义）被 module/checker/covergroup 的 owner 构造逻辑共享，改动需联动 owner.rs；`InFile` 字段名变更会波及 hir-ty/ide 大面积编译。
**集成点**：新构造若挂在现有 owner 下，其 id 一律包 `OwnerRef`；需要"文件内位置"语义用 `InFile`；做作用域相关功能必须走 `ScopeChain` 而非手写 parent 循环。

---

## `crates/hir-def/src/def_id.rs`（810 行）
**角色**：**规范定义身份**——`DefId` = (OwnerId, LocalDefId) 的 Salsa intern 对；DefinitionTable 按 owner 收集"源 AST→定义"映射；DefOriginLoc 各变体的 name/kind/source/range 全投影。
**关键结构与不变量**：
- 私有解引用 helper（L25-69）：`clocking_signal_of/checker_of/checker_port_of/coverpoint_of/cross_of`——OwnerRef→(定义数据, 所在文件)。
- `DefOriginLoc::kind`（L77-106）：Module→DefKind 四分类；Decl 按 `DeclaratorParent` 判 Port/Variable/Net/Param/Genvar/Specparam；其余 `trivial_kind()`。
- `DefOriginLoc::name`（L108-177）/`source_ast`（L179-240，`owner_source` 泛型 helper L180-190 要求 `BodySourceMap: Get<Id, Output=Option<SourceAstId>>`）/`name_range`（L242，经 source_projection 的 focus_range）/`range`（L248，full_range）。
- `LocalDefId(DefinitionKey)`（L279）：key = {kind, name} + **同 (kind,name) 内递增 ordinal**（doc L277："stable identity derived from semantic source order, never a vector ordinal"）。
- `DefinitionTable`（L300-304）：`definitions`(local→data{primary, additional SmallVec})、`by_source`:(SourceAstId, DefKind)→local、`next_ordinals`。**不变量**：`allocate`/`alias` 都 assert 同 (source,kind) 不得插两次（L314/348）；alias 追加 `additional` origins 且要求目标已存在（L357）。
- `definition_table` tracked query（L372-514）：按 OwnerKind 分支插入 owner 自身/ports/instances/modports/clocking；File 级加 config/library/udp/property/sequence；末尾扫 body scope 的 declarators/typedefs/statements——**非 ANSI 端口别名**（L484-500）：decl 与 non-ANSI port 绑定时 `table.alias` 到端口定义（port 必须先收集，L497 expect）。
- `InternedDefId`（L517）+ `DefId`（L525，Ord 走 `as_id()`）；`intern`（L540-554）要求 origin 必有 source AST 且被 owner 表收集（L546/552 两个 expect）。
- `DefId::from_owner`（L561-576）：**只有语言级定义的 owner kind** 能投影（File/ProceduralBlock/AnonymousProgram 显式 None，doc L558-560）；`origins`（L587）/`primary_origin`（L598）；`declaration_origin(s)`（L606/618）——非 ANSI 端口改指向 Decl origin；`type_container`（L671-678，doc：subroutine port 经父模块、普通声明/typedef 用自身 body）；`data_type`（L681-710，Typedef/Decl(含 for 初始化器 L691-700)/SubroutinePort 三路取 DataTy）；`display_label`（L713-765，IDE 标题的 26 分支映射）。
**公开 API**：DefId 全套（from_owner/from_source/from_origin/origins/primary_origin/declaration_origin(s)/name_range/range/is_non_ansi_port/is_port/container_id/kind/name/type_container/data_type/display_label）+ DefOrigin 转发包装（L255-276）+ `definition_owner`（L767-793，Config/Library/Udp 归 file_owner）+ `set_definition_table_lru_capacity`（L808）。
**依赖/被依赖**：依赖（26 出边）→ ast_id_map/checker/container/covergroup/db/declaration/expr::data_ty/expr::declarator/module/owner/stmt/subroutine/symbol/base-db/utils；被依赖（31 入边）→ db/design_map/has_source/lib/pathres/scope/symbol + hir-semantics×4 + hir-ty×7 + ide×13（references/rename/render/semantic_tokens/inlay_hint/…）。
**改动影响面**：ordinal 语义或 by_source assert 改动会直接 panic 在合法输入上；新增 DefOriginLoc 变体必须同时补 `definition_owner`、`source_ast`、`name`、`display_label` 四处 match（漏一臂编译错是护栏）；`definition_table` 的插入顺序敏感（non-ANSI port 先于 declarations，L497 注释钉版）。
**集成点**：所有跨 owner 引用定义（rename/goto-def/references/补全）的规范键是 DefId 而非裸 arena id；`data_type`/`type_container` 是 hir-ty 求类型时的官方入口，二开新定义种类在此挂 origin 即自动获得 IDE 导航能力。

---

## `crates/hir-def/src/body.rs`（991 行）
**角色**：HIR 的**中央存储仓**——`Body`（owner 局部全量 arena 集合）、`BodySourceMap`（每 arena 的 SourceAstId 映射）、`BodyScopeGraph`（嵌套块作用域分区）、`body_input` salsa 分派器与过程/子程序体 lowering。
**关键结构与不变量**：
- `BodyScopeData`（L74-81）：{owner, parent, items, declarators, typedefs, statements}——doc L71-72："canonical OwnerId 是唯一 scope 身份，图不再并行分配 block id"。
- `BodyScopeGraph`（L111-187）：`ensure_root` assert 单根（L137）、`insert` assert 不重复插且父先在（L145-147）、push_* 四个添加器、`shrink_to_fit`。
- `BodyItem`（L191-231）：39 变体（ModuleOwner…ClockingBlockOwner），`impl_body_item_from!`（L233-278）批量 From。
- `Body`（L283-340）：**约 50 个 pub arena 字段**（declarations/typedefs/enums/structs/exprs/event_exprs/classes/bind_directives/dpi_*/extern_*/checkers/covergroups/coverpoints/crosses/instantiations/instances/inst_port_conns…）+ `name`/`items`/`root_stmt`/`ports: Ports`/`subroutine: Option<Subroutine>`/`param_ports`/`default_clocking`/`default_disable`/`generate_kind`。**不变量**（doc L280-281）：一个 Body 归属一个 canonical OwnerId；嵌套词法块共享这些 arena、由 BodyScopeGraph 分区。`shrink_to_fit`（L393-443）逐 arena 收缩——所有 lower_* 出口必须调用（见 file.rs L462 等）。
- `BodySourceMap`（L449-497）：与 arena 一一对应的 ~45 个 SourceMap + `default_clocking_src/default_disable_src`；doc L446-447："当前指针与 range 只属于 AstIdMap/SourceProjection"。
- `body_input`（L557-592，tracked lru=512）：按 OwnerKind 十一路分派（ProceduralBlock→lower_procedural_body、Subroutine→lower_subroutine_body、Block→`body_owner` 上升后委托、File/Module/AnonymousProgram/GenerateBlock/Checker/Covergroup/ClockingBlock→各自模块的 lower_*_owner）；`body_with_source_map`（L594）二次包装（给 salsa 两级缓存）；`body_owner`（L598-603）：Block 一路 `parent()` 直到非 Block。
- `lower_procedural_body`（L605-625）：ProceduralBlock cast 失败给空 Body；成功则 `record_stmt(proc.statement())` 存 root_stmt。
- `lower_subroutine_body`（L627-654）：**无 end 的函数直接空 body**（L633-635）——增量解析中间态防御；`lower_subroutine` 存签名、`lower_subroutine_items`（L796-824）只认 Statement/DataDecl/PortDecl/LocalVarDecl/ParamDeclStmt/TypedefDecl 六类。
- `lower_body_struct_type/enum_type/typedef/local_variable_decl`（L669-763）：typedef 先占位再回填 ty（L724-743，两段式防递归）；`lower_nested_block`（L767-788，impl ModuleItemStore）：enter/leave body scope 配对。
- `BodySourceMap::item_to_source`（L828-876）：39 臂 BodyItem→SourceAstId；`block_item_to_source`（L878-885）四臂。
- `impl_arena_getters!`（L893-941，宏在 lib.rs L55）/`impl_source_map_getters!`（L943-991，lib.rs L70）：给 Body/BodySourceMap 批量生成 `Get<Id>` trait impl——`body.get(id)`/`src_map.get(id)` 的泛型基础。
**公开 API**：Body::scope/module_owners/subroutine_owners/declaration/typedef/struct_def/enum_def/expr/event_expr/declarator/stmt + getter 宏产物（约 45 个 GetRef impl）+ `set_body_lru_capacity`（L888，两个 query 都设）。
**依赖/被依赖**：**出边 51 个**（本 crate 几乎全部构造模块 + syntax）；被依赖（19 入边）→ container/covergroup/db/design_map/diagnostics/file/lib/module/module::clocking/module::generate/scope + ide×10（code_action/code_lens/document_symbols/folding_ranges/inlay_hint/module_resolution/semantic_tokens…）。
**改动影响面**：加新 arena 必须"五处同步"——Body 字段、BodySourceMap 字段、shrink_to_fit×2、impl_arena_getters、impl_source_map_getters，漏一处即 Get impl 缺失编译断；`body_input` 分派表漏新 OwnerKind 会在查询该 owner 时落空；`lower_subroutine_body` 的 end 检查删除会让半截函数产出垃圾 HIR。
**集成点**：新语法构造的落地套路（本 crate 的标准操作）：定义 struct → Body 加 arena → 定义表加 `BodyItem::XxxId` 变体 → 写 lower_xxx（用 `alloc_with_source_entry`）→ BodyItem 分派处挂进 items → item_to_source 加臂。defs 的 name/type 查询（def_id.rs）与 symbol/scope 收集自动跟进。

---

## `crates/hir-def/src/block.rs`（12 行）
**角色**：嵌套块 item 的四选一标签（block statement 内允许的四类成员）。
**关键结构**：`BlockItem` 枚举（L6-11，`define_enum_deriving_from!` 生成）：`DeclarationId | TypedefId | StructId | StmtId`——块内可声明/类型定义/匿名 struct/语句。
**公开 API**：仅该 enum（宏生成 Debug/PartialEq/Eq/Clone）。
**依赖/被依赖**：依赖 → utils（define_enum_deriving_from 宏）、aggregate::StructId、declaration::DeclarationId、stmt::StmtId、typedef::TypedefId；被依赖 → body.rs（BodyScopeData.items/LoweringCtx::push_body_item）、lib、ide（document_symbols/folding_ranges）。
**改动影响面**：加变体须同步 `body.rs` 的 `block_item_to_source`（L878-885）与 lower_nested_block 的 match（L770-781），否则新块成员静默丢弃。
**集成点**：块作用域内允许的新成员种类在此声明，是"块内可以有什么"的唯一清单。

---

## `crates/hir-def/src/expr.rs`（1030 行）
**角色**：表达式 HIR 的定义与 lowering 主体——`Expr` 36 变体、运算符表、sequence/property 表达式（SVA）、名字/选择器/参数表的完整降级。
**关键结构与不变量**：
- 运算符枚举：`UnaryOp`（L23，10 种含归约）、`BinaryOp`（L47，含 `Assign(AssignOp)` 复合变体 L107——**赋值被编码为二元运算**）、`AssignOp`（L119，15 种）、`IncDecOp`（L111）、`StreamOp`（L151）。
- `SequenceExpr`（L209-217，7 变体：Simple/Binary/Delayed/Event/Clocking/FirstMatch/Parenthesized）；`PropertyExpr`（L226-237，10 变体含 Case/StrongWeak/AcceptOn）；`PropertyCaseItem`（L220）。
- `Expr`（L240-348，36 变体）：Missing（#[default]）/Error(SyntaxKind)/Unsupported(SyntaxKind) 三态错误面 + Binary/AssignmentPattern/Inside/Dist/TimingControl/Sequence/Property/Call/NewClass/CopyClass/NewArray/EmptyQueue/ArrayOrRandomizeMethod/TaggedUnion/SuperNewDefaulted/Concat/Cond/Field/Ident/Literal/Cast/SignedCast/MinTypMax/MultiConcat/PostfixIncDec/PrefixIncDec/ElementSelect/Stream/Unary。`to_assign`（L353-365）只对 `Binary{op: Assign}` 返回 Assign 结构。
- `Arg`（L368）/`Selector`（L375，Bit/Range/Ascending/Descending）。
- `LoweringCtx::lower_expr`（L387-402）：**统一出口**——inner 失败→`Expr::Error(kind)` 并 report_invalid；Unsupported→report_unsupported；alloc 进 arena+src map。
- `lower_expr_inner`（L548-579）：25 臂 ast::Expression 分派；ValueRange/DataType 显式 Unsupported。
- `lower_name`（L704-782）：Name 七形态；`lower_ident_select` 内嵌函数（L705-743）把 `scope::member[sel]` 降为 Field{receiver, field} 再逐个选择器包 ElementSelect（**每层 select 重新 alloc 并复用同一 source id**，L733-738）；ScopedName 左侧 cast 成 Expression 递归（L757）。
- `lower_binary_expr`（L784-838）：TokenKind→BinaryOp 全表；**`<=` 双义**（L811-817）：父节点是 NONBLOCKING_ASSIGNMENT_EXPRESSION 则 NonBlockAssign 否则 Le。
- `lower_argument`（L986-1003）：Named/Ordered/Empty；Named 与 Ordered 的值都走 `lower_property_expr`（L992/998）——让 `f(a dist {...})` 类语法在实参位可用。
**公开 API**：上述类型 + `pub type ExprId = Idx<Expr>`（L350）+ `pub mod data_ty/declarator/timing_control`（L18-20）+ LoweringCtx 的 pub(crate) 方法族（lower_expr/lower_expr_opt/lower_sequence_expr/lower_property_expr/lower_assign/lower_selector）。
**依赖/被依赖**：依赖 → literal.rs（lower_literal）、lower.rs、syntax；被依赖（31 入边）→ crate 内 assertion/bind/body/constraint/covergroup/diagnostics/elab_system_task/expr::data_ty/expr::declarator/external/let_decl/module/*（continuous_assign/defparam/generate/instantiation/port/specify）/net_alias + hir-semantics×3 + hir-ty×6（compatibility/display/infer/ty/type_system）+ ide×3（hover/inlay_hint/semantic_tokens）。
**改动影响面**：加 Expr 变体必须同步 hir-ty 的 infer/display/compatibility 与 ide semantic_tokens（编译器穷尽性检查兜底）；`<=` 判定依赖父 SyntaxKind，语法层改 nonblocking 节点编码会翻转语义；lower_name 的 Field 链构造决定 hir-ty 成员访问解析路径。
**集成点**：新运算符/新 primary 在 lower_expr_inner 加臂即可获得完整管线（lowering→HIR→infer→IDE 高亮）；`lower_property_expr` 是所有"表达式位置但要 SVA 语法"（dist、sequence instance）的复用点（assertion.rs L165、covergroup bins、constraint 均走它）。

---

## `crates/hir-def/src/expr/data_ty.rs`（452 行）
**角色**：数据类型 HIR（`DataTy`）与类型路径（`TypeRef`）的 lowering——builtin/命名/struct/enum 四路 + unpacked 维度语义。
**关键结构与不变量**：
- `DataTy`（L28-34）：Builtin(BuiltinDataTyId)/Named(TypeRef)/Struct(OwnerRef<StructId>)/Enum(OwnerRef<EnumId>)/Unsupported(SyntaxKind)。**struct/enum 不内联**：降级为 owner arena 引用（注释 L19-26 详述 slang AST 形态与维度语义：`[]` dynamic、`[$]`/`[$:N]` queue、`[string]` 等 builtin key associative、`[expr]` 固定尺寸；typedef-key/wildcard associative 留待后续 PR）。
- `BuiltinDataTy`（L50-58）+ Default=Vector{Logic}（L60-68）；`IntKind`（L71，6 种）、`VecKind`（L81，Bit/Logic/Reg，默认 Logic）、`Real`（L89，3 种）。
- `Dimension`（L96-103）：Range/Size/Queue/Assoc/Wildcard/Dynamic 六态。
- `TypePathKind`（L106：Unqualified/Package/Hierarchical）+ `TypePathRecovery`（L113：Selectors/UnsupportedName/MissingIdentifier/MixedSeparators）；`TypeRef`（L121-173）：segments+segment_sources+path_kind+source+recovery，`is_valid()`=recovery.is_none()（L170-172）。
- `LoweringCtx::lower_data_ty`（L176-198）：DataType 八臂；StructUnionType→`lower_body_struct_type`+OwnerRef（L187-191）。
- `lower_keyword_ty`（L200）：String/Real/ShortReal/RealTime/Void/Event/CHandle 直映；Property/Untyped/Sequence 报 Unsupported。
- `lower_named_ty`（L218-254）：收集 segments；**recovery 时清空 segments 再报错**（L233-245）——坏类型路径降为空段+标记，不猜。
- `lower_name_segments`（L256-326）：ScopedName 递归展开；**分隔符一致性检查**（`::` Package / `.` Hierarchical，混用→MixedSeparators L302-308）。
- `lower_integer_type`（L334-355）：int 族→Int，reg/bit/logic→Vector；**signing 缺省规则**：int 族默认 signed、vector 族默认 unsigned（L348）。
- `lower_implicit_type`（L357-362）：隐式类型默认 Logic（注释 L360 引 SV spec 6.7.1）。
- `lower_dimension`（L377-387）/`lower_range_dimension`（L389-407）：BitSelect 内 builtin key token→`Dimension::Assoc`（合成 `Expr::Ident` L394-398）；否则 Size；RangeSelect→Range。
- `first_token`（L415）/`is_builtin_dimension_key_token`（L427-441）：10 个关键字白名单。
- `DataTy::is_ast_missing`（L444-451）：ImplicitType 且无 signing 无 dimensions → 视为源码缺失（供 port 推断等使用）。
**公开 API**：DataTy/BuiltinDataTy(BuiltinDataTyId)/TypeRef 全部读取器（segments/segment_sources/path_kind/source/recovery/is_valid）、`lower_implicit_data_ty`（L364，pub(crate)）。
**依赖/被依赖**：依赖（34 出边）→ aggregate/ast_id_map/container/expr.rs/lib/lower/syntax；被依赖（19 入边）→ assertion/def_id/diagnostics/expr::declarator/external/module::instantiation/module::port/net_type_decl + hir-ty×6 + ide×4（module_resolution/render/semantic_tokens/semantic_tokens::port）。
**改动影响面**：Dimension 语义（尤其 Assoc 合成 Expr::Ident）被 hir-ty 的类型系统直接消费；TypeRef recovery 策略改动影响 IDE 对残缺类型的提示行为；改 BuiltinDataTy 形状会波及 hir-ty/compatibility.rs 的赋值兼容检查。
**集成点**：新类型关键字（如未来 SV 扩展）在 lower_keyword_ty/lower_integer_type 加臂；带作用域感知的 associative key（typedef-key）是注释 L25-26 标注的预留扩展位。

---

## `crates/hir-def/src/expr/declarator.rs`（142 行）
**角色**：说明符（declarator）HIR——名字+维度+初始化器+父声明回链；声明与说明符解耦的枢纽。
**关键结构与不变量**：
- `Declarator`（L17-23）：{name, dimensions, initializer, secondary_initializer, parent: DeclaratorParent}。`secondary_initializer` 仅 specparam（mintyp:max 双值）使用（L118）。
- `DeclaratorParent`（L27-31，define_enum_deriving_from）：`PortDeclId | DeclarationId（Param/Net/Data）| StmtId（for-init 类 DataDecl）`——**每个 declarator 恰有一个父**，def_id.rs 的 DefKind 判定与 data_type 回溯都依赖它。
- `DeclsRange = IdxRange<Declarator>`（L40）+ `empty_decls_range()`（L36-39，raw 0..0 哨兵——**空 range 不是 Option**，声明先占位后回填的模式依赖它）。
- `lower_declarators/lower_declarator`（L43-69）：批量→连续 IdxRange；单个 alloc 后**必 `record_body_declarator`**（L67，进当前 body scope——def_id/symbol 收集的数据源）。
- `lower_identifier_names`（L71-99，genvar/端口名表用，无维度无初始化）；`lower_specparam_declarators`（L101-133，initializer=Some(value_1)、secondary=value_2）；`decls_range`（L136-142）：iterator→首尾闭区间（**假定 lower 连续分配**，中间不夹杂其他 arena 写入）。
**公开 API**：Declarator/DeclaratorParent/DeclId/DeclsRange + 上述 pub(crate) lowering。
**依赖/被依赖**：依赖（14 出边）→ declaration/expr.rs/expr::data_ty/lib/lower/module::port/stmt/syntax/utils；被依赖（14 入边）→ body/def_id/module::port/scope/symbol + hir-ty×2（display/infer）+ ide×6（convert_port_declarations/completion/instantiation/document_symbols/module_resolution/navigation_target/render/semantic_tokens）。
**改动影响面**：DeclaratorParent 加变体须同步 def_id.rs 的 kind（L87-102）/data_type（L686-701）/display_label（L732-750）三处 match；`decls_range` 的连续性前提被破坏（比如在 lower_declarators 回调里插别的 alloc）会导致 range 覆盖错位。
**集成点**：所有"名字表"式语法（genvar、端口引用表）复用 lower_identifier_names；IDE 端口重构 code action 依赖 Declarator↔PortDecl 的父子链。

---

## `crates/hir-def/src/expr/timing_control.rs`（169 行）
**角色**：时序控制 HIR（delay/event control/repeated event）与事件表达式（EventExpr）的 lowering。
**关键结构与不变量**：
- `TimingControl`（L12-16）：DelayControl/EventControl/RepeatedEventControl(ExprId, Option<EventControl>)。
- `DelayControl`（L19-23）：OneStep（`#0`步进）/Value(ExprId)/Delay3(SmallVec<[ExprId;3]>，rise/fall/turn-off 三段，缺省即短——L130-143 逐段 push)；`EventControl`（L26-31）：Implicit（`@(*)`）/Event(ExprId)/EventExpr(EventExprId)。
- `EventExpr`（L38-44）：Missing/Atom{sensitivity, expr, iff}/Or/And；**`or` 关键字→Or、逗号→And**（L76-77，SV 语义二者等价但保留区分）；Sensitivity（L47：Posedge/Negedge/Edge）；TODO 注释 L43：sequence_instance 未支持。
- `lower_timing_control`（L96-120）七臂全分派；`lower_repeated_event_control`（L156-168）：内层必须降成 EventControl 否则丢（L161-166）。
**公开 API**：上述类型 + `EventExprId`（L35）+ pub(crate) lower_event_expr/lower_timing_control。
**依赖/被依赖**：依赖 → expr.rs（ExprId）、lower.rs、syntax；被依赖 → assertion/body/declaration/module::clocking/module::continuous_assign（5 入边）。
**改动影响面**：Delay3 段数语义被 hir-ty/net 延迟推断消费；Or/And 合并策略改动影响敏感列表 IDE 补全（ide/completion/engine/sensitivity_list 引用同一 EventExpr）。
**集成点**：net 声明延迟（declaration.rs L165-171）、模块 clocking 块、过程语句三类宿主共用本 lowering。

---

## `crates/hir-def/src/declaration.rs`（362 行）
**角色**：五类声明（Data/Net/Param/Genvar/Specparam）的 HIR 与统一 lowering；`Declaration` 是声明 arena 的存储枚举。
**关键结构与不变量**：
- `Declaration`（L17-24，define_enum_deriving_from）：DataDecl/NetDecl/ParamDecl/GenvarDecl/SpecparamDecl；`decls()`（L29-37）与 `ty()`（L39-47）是五变体统一投影（**每类声明都必有 ty 与 decls range**）。
- `DataDecl`（L51：ty/const_kw/var_kw/decls）；`NetDecl`（L59：ty/net_kind/delay/strength/decls）；`NetStrength`（L68：Pull/Drive/Charge）；`ParamDecl`（L75：ty/kind/is_port/decls）；`ParamDeclKind`（L83：Parameter/LocalParam + `is_overridable()` L89 + `keyword()` L93）；GenvarDecl/SpecparamDecl（L102/107）。
- `alloc_declaration`（L114-129）+ `finish_declaration_decls`（L131-139）：**占位-回填两段式**——先 alloc 空 decls，lower 完 declarators（需要 parent id 做回链）再写回 range。
- `lower_data_decl`（L141-160）：const/var 修饰收集（L144-149）；`lower_net_decl`（L162-193）：net_kind/lower_data_ty/delay（非 DelayControl 丢弃 L167-171）/strength 三态；`lower_user_defined_net_decl`（L195-232）：nettype 名降为 `DataTy::Named(TypeRef::single(..))`（L214），delay 非 delay-control 报 unsupported 并放弃（L216-223）；`lower_port_decl_as_data_decl`（L234-252）：Variable/Net header 取 ty，**InterfacePortHeader 返回 None**（L242）。
- `lower_param_decl_base_with_context`（L261-277）：四参（inherited_kind/force_local/is_port）穿透到值参数与类型参数；`lower_type_param_decl`（L279-295）：**类型参数的 ty 是 `BuiltinDataTy::default()`（即 Logic 向量）占位**（L292）——类型参数的"值类型"无意义，靠 ParamDeclKind+无 decls 区分；`lower_param_decl_kind`（L348-362）：force_local 压倒一切→LocalParam，否则看关键字，再否则继承上下文（`parameter` 端口列表继承规则的实现点）。
- `lower_genvar_decl`（L320-333）：ty 硬编码 `Int{Integer, signed}`（L324-327）；`lower_specparam_decl`（L335-345）：ty 走 implicit。
**公开 API**：上述全部类型 + pub(crate) lowering 方法族。
**依赖/被依赖**：依赖（13 出边）→ expr::timing_control（DelayControl）、lower.rs、ty.rs（NetKind/Strength/lower_net_kind 等）、syntax/utils；被依赖（16 入边）→ assertion/block/body/def_id/diagnostics/expr::declarator/external/lib/module::port/module::specify + ide×6（module_members/completion/instantiation/document_symbols/module_resolution/render/signature_help）。
**改动影响面**：ParamDeclKind 的继承逻辑（lower_param_decl_kind）决定 localparam/parameter 归属，错则 hir-ty 参数覆盖与 IDE 补全（add_missing_parameters code action）全错；`ty()`/`decls()` 投影被 def_id.rs data_type 直连。
**集成点**：新声明种类加 Declaration 变体 + finish_declaration_decls 臂；端口声明复用 DataDecl（is_port 标记在 ParamDecl，PortDecl 的 Ansi/NonAnsi 在 module::port.rs——本文件的 lower_port_decl_as_data_decl 是 subroutine 端口声明的数据化入口）。

---

## `crates/hir-def/src/item_tree.rs`（714 行）
**角色**：文件级**结构摘要**查询——位置无关的 item 清单（含 function 签名与 header 指纹），是"只看头不进 body"的增量边界。
**关键结构与不变量**：
- `SignatureId(u32)`（L25）；`SignatureKind`（L38：Task/Function）；`SignaturePortDirection`（L44，6 态含 Unknown）；`SignaturePort`（L54：direction/name/type_ast: Option<SourceAstId>)；`Signature`（L75：kind/return_type_ast/ports）。
- `ItemTreeItem`（L96-103）：{id: SourceAstId, parent, kind, name, signature, header_fingerprint}；`header_fingerprint`（L135-137，doc L131-134："**body 故意不参与指纹**——未来语义身份层的第一道增量边界"）。
- `ModuleHeader`（L145-150：owner/name/kind/source，doc L140-143：**无 range**，range 属 SourceProjection）。
- `ItemTree`（L174-180）：{file_id, owners: Arc<OwnerTable>, items, by_id, signatures}；`module_headers()`（L195-204，doc："文件级声明 seam，只要头的消费者不得进入 scope/body 查询"）。
- `item_tree_input`（L238-247，tracked lru=128）：doc L234-236——"equality backdating 防止 body-only 变更使 item_tree 失效"（Salsa 返回相等值即不触发下游重算）；`item_tree`（L250）二级包装；`item_for_owner`（L261）/`signature_for_owner`（L266）。
- `build_source_projection`（L272-295）：preorder 全节点→`SourceOrigin::new(file_id, ptr, kind, full_range, focus_range)`——**focus 来自 item_name 的名字 token**；这是 SourceProjection 的唯一生产端。
- `is_body_boundary`（L297-299）：FunctionDeclaration 与 ProceduralBlock 是 body 边界；`build_item_tree_data`（L301-361）：elem_preorder 中 `body_depth==0 && Member::can_cast` 才入树（**body 内成员不进 item tree**），parent 栈维护层级，root 必须 COMPILATION_UNIT（assert L311-315）。
- `lower_signature`（L374-410）：function/task 判别（`as_task_declaration()` L376）；端口方向缺省 Input（L417）；default function port → Input+无名单口（L399-404）。
- `ItemName` trait + 两宏（L422-522）为 27 种 AST 节点提供名字 token；`item_name`（L524-565）match_ast 分派，**多声明节点宁可无名字也不猜**（doc L561-564）；`fingerprint`（L582-599）：kind+name+header 源文本哈希。
**公开 API**：ItemTree 全读取器（file_id/root_owner/module_headers/items/item/signature(s)/len/is_empty）+ ItemTreeItem/Signature/ModuleHeader/SignaturePort 读取器 + `set_item_tree_lru_capacity`（L254）。
**依赖/被依赖**：依赖（20 出边）→ ast_id_map/db/owner/source_projection/syntax（has_name/has_text_range）/utils/text_edit/vfs；被依赖（4 入边）→ db/lib/unit_index + ide/src/semantic_index.rs。
**改动影响面**：body_boundary 集合变化改变哪些 item 被索引（语义索引/工作区符号直接受影响）；fingerprint 算法变更 = 全部 header 缓存失效；内嵌 4 个测试（L618-713，`item_tree_excludes_body_local_members` 断言 before==after、`source_projection_focuses_named_ast_nodes` 验证 focus 指向名字）是增量语义的闸门，`cargo test -p hir-def`。
**集成点**：工作区级功能（unit_index、ide 语义索引）只消费本摘要即可列出模块/函数/参数——避免触碰重的 body 查询；新"有头"构造在 ItemName 两宏+item_name 加臂即可获得导航名。

---

## `crates/hir-def/src/design_map.rs`（401 行）
**角色**：**设计单元导出图**——全库 package 的固定点导出命名空间（自有声明 + package import/export 闭包），包导入解析的唯一权威。
**关键结构与不变量**：
- `PackageExports`（L33-37）：types/values/assertions 三张 `FxHashMap<SmolStr, SmallVec<[DefId;1]>>`；doc L27-31：**与词法 ScopeGraph 分离**——本值只表达包的公开绑定。
- `lookup`（L40-54）：按 NameContext 选表，Listing 合并三表；`lookup_listing`（L56）/`iter_listing`（L70-100，三表去重并集迭代）；`insert_resolution`（L114-131）：Listing 双插 type+value。
- `package_bindings`（L145-230）：单包直接导出——declarators→values、typedefs→types、subroutines→values、语句 label 与命名块→values（L171-184）、Checker/Covergroup→types、Property/Sequence→assertions、ClockingBlock→values。
- `DesignMap`（L237-239）：`package_exports: FxHashMap<OwnerId, Arc<PackageExports>>`，**只含 package owner**（doc L231-235）；`resolve_import`（L247-267）：具名 import 名不匹配→Unresolved；包查 `unit_index().package_ids()`（保留歧义父包 Resolution）。
- `design_map` tracked query（L271-365）：从 `db.files()` 收集所有 Package module_headers（L272-284，sort+dedup 保证确定性）；初始 exports/imports/reexports；**固定点循环**（L310-357）——doc L307-309："每轮只增不删，有限命名空间必然收敛，含互相导入的包，无需递归限制或静默环回退"；`PackageExport::All` 把该包全部 import 的名字逐一 re-export（L340-346）。
- `resolve_package_member`（L367）/`imported_names`（L381-397，排序去重）。
**公开 API**：PackageExports::lookup/lookup_listing/iter_listing；DesignMap::package_exports/resolve_import；`design_map(db)` 查询；`set_lru_capacity`（L399）。
**依赖/被依赖**：依赖（18 出边）→ base-db/body/container/db/def_id/owner/stmt/symbol/utils::get；被依赖（2 入边）→ db.rs、lib.rs（**出口极窄**：全 crate 只有 db 门面暴露它）。
**改动影响面**：固定点循环若被改成定深迭代，互相导入包的传递导出会截断；PackageExports 三表分类变化影响 NameContext::Type/Value/Assertion 的解析结果（hir-semantics/pathres 与 scope.rs 消费 resolve_import）。
**集成点**：新可导出构造在 package_bindings 加臂即自动进入包命名空间与 import 解析；db.package_exports 是 hir-ty/IDE 查包成员的入口。

---

## `crates/hir-def/src/diagnostics.rs`（1319 行，其中主代码约 L1-383，L385-1319 为 19 个内嵌测试）
**角色**：文件级 lowering 诊断聚合——把所有 owner 的 raw diagnostics 拍平到一个文件，并为无 range 诊断解析保守显示范围；外加两类 IEEE 1800-2017 26.3 导入冲突检查。
**关键结构与不变量**（主代码无 struct，全为函数管线）：
- doc L7-16 钉死无 range 诊断的四级回退序：①lowerer 自带 range ②SourceAstId 的投影 root-buffer range ③owning container 起点的零宽标记 ④文件起点。
- `file_lowering_diagnostics`（L44-99）入口：file owner → collect 自身 + import 冲突；**收集一次全文件 ident 引用**（L62-64，注释：wildcard 检查复用）→ 逐 subroutine/module/generate owner 收集；module 内再递归 generate 块与 proc 体。
- `collect_module`（L101-128）/`collect_generate_block`（L130-152，递归嵌套 generate）：owner_range 取自 `owner.source(db).full_range`。
- `collect_import_conflicts`（L154-206）：**显式 import 两条非法**——与同 scope 声明同名（L178-186）/与另一包显式 import 同名（L187-192）；`reported` 去重防一报多。
- `collect_ident_references`（L210-243）：递归 module/generate/subroutine/proc 收集全部 `Expr::Ident`（三元组 owner+Ident+InFile<SourceAstId>）。
- `collect_wildcard_activation_conflicts`（L268-324）：**wildcard 激活规则**（doc L265-267：一旦某引用使 wildcard 导入符号在 scope 可见，该 scope 后续同名声明非法）——判定 = 存在解析命中且 `resolve_wildcard_at` 的激活 scope==本 owner（L290-298）且该引用先于声明（`before_reference` L300-304）。
- `collect`（L352-370）：range 缺失时按 ②③回退填；`resolve_range`（L374-383）：owner 起点零宽/文件起点。
**公开 API**：`file_lowering_diagnostics(db, SyntaxFileId) -> Arc<[LoweringDiagnostic]>`（pub(crate)，经 db.rs L90 暴露）。
**依赖/被依赖**：依赖（**36 出边**，诊断聚合要摸全 crate：base-db×5/vfs/pathres/proc/source_map/source_projection/symbol/time_units/typedef/expr/bind/dpi/external/declaration…）；被依赖（2 入边）→ db.rs、lib.rs。
**改动影响面**：回退序变化直接改变编辑器里诊断落点；wildcard 检查的 `references` 全文件预收集是性能敏感点（每次诊断查询重算）；19 个测试（`supported_constructs_produce_no_lowering_diagnostics` L534 用 ~50 种 SV 构造的巨型源断言零诊断；`wildcard_activated_then_declared_is_illegal` L534+ 序列；`range_resolution_*` 三连验证回退序）是全部 lowering 行为的快照闸，`cargo test -p hir-def`。
**集成点**：新 owner kind 必须在 file_lowering_diagnostics 加收集分支，否则其诊断对 IDE 不可见；`collect_ident_references` 的引用清单可复用为"全文件引用索引"雏形。

---

## `crates/hir-def/src/has_source.rs`（51 行）
**角色**：`HasSource` trait——OwnerId/DefOrigin/DefOriginLoc/DefId 四类身份到 `InFile<SourceInfo>`（含 focus range）的统一源定位。
**关键结构与不变量**：
- `trait HasSource { fn source(&self, db) -> Option<InFile<SourceInfo>> }`（L11-13）。
- `project`（L15-18）：SourceAstId→SourceProjection.origin→SourceInfo::from_origin——**纯投影，无语法树重走**。
- `impl DefOrigin`（L25-39）：source_ast 后投影，再以 `name_range` 覆盖 focus（L30-36，**仅当 focus 与 name range 同文件**才替换）——保证定义的 focus 恒指向名字 token 而非节点头。
- `impl DefId`（L47-51）：委托 primary_origin。
**公开 API**：HasSource trait + 四个 impl。
**依赖/被依赖**：依赖（9 出边）→ ast_id_map/container/db/def_id/owner/source_map/symbol；被依赖（11 入边）→ diagnostics/lib/scope + ide×8（code_lens/sensitivity_list/document_symbols/folding_ranges/inlay_hint/navigation_target/references/search、semantic_tokens）。
**改动影响面**：focus 覆盖逻辑改动会让 IDE 高亮/rename 预选范围偏移（如指向整个声明头）。
**集成点**：任何"从定义跳源码"的功能统一走本 trait，不要自己查 source_map 拼范围。

---

## `crates/hir-def/src/aggregate.rs`（537 行）
**角色**：聚合类型 HIR——struct/union（StructDef）、enum（EnumDef）、class（ClassDef 及参数/成员/限定符全套）的定义与 lowering。
**关键结构与不变量**：
- `StructKind`（L27）；`StructMember`（L33：name/ty: Option<OwnerRef<DataTy>>/dimensions/initializer/random）；`StructDef`（L42：kind/name/packed/signing/tagged/members）。`lower_struct_def`（L53-87）：**纯函数接受 lower_member 回调**（ctx 与无 ctx 两处复用：body.rs L671、file.rs L33）；**成员 ty 的 cont_id 强制改写为 container**（L79-82）——防跨 owner 引用。
- `EnumMember`（L90）/`EnumDef`（L97：base_ty/members/dimensions）；EnumId（L103）。
- Class 族：`ClassMemberKind`（L106）、`ClassKind`（L115：Class/Virtual/Interface）、`ClassVisibility`（L122）、`ClassRandomQualifier`（L129：Rand/RandC）、`ClassPropertyQualifiers`（L135）、`ClassMethodQualifiers`（L143：is_pure/is_virtual/is_extern/is_static/visibility）、`ClassTypeParameterRestriction`（L152，5 种）、`ClassParameter`（L161：Value/Type）、`ClassMember`（L177：name/kind/ty/两组 qualifiers/method: Option<Subroutine>/constraint/owner）、`ClassDef`（L189：name/kind/is_final/parameters/base_class_name/implemented_interfaces/members）。
- `LoweringCtx::lower_class_decl`（L202-210）：lower_class_def（骨架）→ lower_class_parameters（参数）→ lower_class_members（方法/约束回填）三段。
- `lower_class_parameters`（L212-257）：**inherited_local 粘性**——一个 localparam 关键字使后续同列表参数全 local（L224-226/240-242，SV 列表继承语义）。
- `lower_class_members`（L284-370）：**member_index 与骨架顺序对齐**——骨架（lower_class_def）先按 AST 顺序产 members 占位，此处逐 member `member_index` 回填 method/constraint/owner（L311-317 `.get_mut(member_index).expect("class method must have a matching class member")`）；纯虚原型用 `lower_subroutine_prototype`（L326-334）；类方法经 `owner_for_node(.., OwnerKind::Subroutine)` 取 canonical owner（L302-304 expect）。
- `lower_class_def`（L373-488）：kind/final/extends/implements/骨架 members（Property 取首个 declarator 名 L408-413）；`lower_class_property_qualifiers`（L494）/`lower_class_method_qualifiers`（L517）逐 token 收集。
**公开 API**：StructDef/StructMember/EnumDef/EnumMember/ClassDef/ClassMember/ClassParameter 及限定符类型 + 全部 Idx 别名（StructId/EnumId/ClassId）+ `lower_struct_def`/`lower_class_def`/`lower_checker_decl` 等纯函数。
**依赖/被依赖**：依赖（17 出边）→ constraint/container/lib/lower/owner/subroutine/syntax/has_name；被依赖（10 入边）→ block/body/expr::data_ty/lib/lower/owner/subroutine + hir-ty×4（display/infer/members/ty）+ hir-ty tests + ide/document_symbols。
**改动影响面**：lower_class_members 的 index 对齐若与骨架产 member 的 filter 失配直接 expect panic（新增可回填成员类型必须两处同步）；ClassParameter 的 local 继承语义被 hir-ty 参数化类实例化消费。
**集成点**：struct/enum 定义同时落在 owner 的 structs/enums arena（body.rs lower_body_struct_type/enum_type），DataTy 以 OwnerRef 引用——新增聚合类型照此挂接即可被 hir-ty members 解析。

---

## `crates/hir-def/src/assertion.rs`（168 行）
**角色**：SVA 断言构造——property/sequence 声明与 default disable iff 的 HIR 与 lowering。
**关键结构与不变量**：
- `AssertionPort`（L17：name/local/direction: Option<TokenKind>/ty/default）——**direction 保留原始 token kind**（不做枚举化）。
- `PropertySpec`（L26：clocking: Option<TimingControl>/disable/expr）；`PropertyDef`（L33：name/ports/variables: SmallVec<DeclarationId>/spec）；`SequenceDef`（L43：name/ports/variables/expr）。
- `lower_property_decl`（L53-82）：ports→variables（复用 lower_body_local_variable_decl）→spec 三件套（clocking/disable/property_expr）；`lower_sequence_decl`（L84-108）同构但 expr 走 `lower_sequence_expr`。
- `lower_default_disable_declaration`（L110-157）：**三关键字逐个校验**（default/disable/iff，L114-138 缺一报 invalid）+ **每 scope 至多一条**（L140-150 查 `body.default_disable.is_some()` 报 "more than one"）；成功写 `body.default_disable`/`sources.default_disable_src`（L152-156）。
- `lower_assertion_port`（L159-167）：default 值走 `lower_property_expr`（断言端口语法域）。
**公开 API**：AssertionPort/PropertySpec/PropertyDef/PropertyId/SequenceDef/SequenceId + 四个 pub(crate) lowering。
**依赖/被依赖**：依赖（13 出边）→ declaration/expr.rs/expr::data_ty/expr::timing_control/lib/lower/syntax；被依赖（5 入边）→ body/let_decl/lib/symbol + ide/document_symbols。
**改动影响面**：default_disable 单条约束的判重依赖 body 字段（body.rs L334），Body 序列化/复用改动需保留该字段语义；ports/variables 的 DeclarationId 挂在 owner declarations arena，改 body 收集顺序会影响 def_id 的 by_source assert。
**集成点**：property/sequence 的名字经 BodyItem::PropertyId/SequenceId 进入 definition_table（def_id.rs L473-478）与 package assertions 命名空间（design_map.rs L201-218）。

---

## `crates/hir-def/src/bind.rs`（174 行）
**角色**：bind directive 的 HIR 与 lowering——target 名字链 + 可选实例表 + 层级/checker 两类实例化。
**关键结构与不变量**：
- `BindPathKind`（L14：Simple/Package/Hierarchical）；`BindNameSegment`（L21：name+selectors）；`BindName`（L27：segments+kind）；`BindInstantiationKind`（L33：Hierarchy/Checker）；`BindDirective`（L39：target/target_instances/instantiation: InstantiationId/instantiation_kind）。
- `lower_bind_directive`（L49-88）：target 必须可降（`?` 传播，L53）；实例化只认 HierarchyInstantiation/CheckerInstantiation 两 Member，其他 report_unsupported 放弃整个 directive（L71-77）。
- `lower_bind_name_parts`（L97-158）：Name 六形态递归展开；**分隔符一致性**（`::`→Package、`.`→Hierarchical，混用 report_unsupported，L142-149）；IdentifierSelectName 的 selectors 逐个降级并挂在该 segment 上（L110-120）；任何段缺 identifier→invalid 放弃（L167-170）。
**公开 API**：上述类型 + BindDirectiveId + lower_bind_directive。
**依赖/被依赖**：依赖（8 出边）→ expr.rs（Selector）、lib/lower/module::instantiation/syntax；被依赖 → body/diagnostics/lib（3 入边）。
**改动影响面**：diagnostics.rs 的测试直接断言 bind 降级结果（`bind_directives.len()==2`、hierarchy_bind.instantiation_kind 等，diagnostics.rs 测试段 L86/132-134）；instance 归 module::instantiation arena，其 Id 语义变更连带此处。
**集成点**：bind 的 target 名字解析（hir-semantics）消费 BindName 的 path_kind 区分包/层级前缀。

---

## `crates/hir-def/src/checker.rs`（178 行）
**角色**：SVA checker 声明的 HIR 与 lowering——CheckerDef（name/ports/declarations）+ checker owner 的 body 查询实现。
**关键结构与不变量**：
- `CheckerDef`（L31：name/ports/declarations: SmallVec<DeclarationId>）；`CheckerPort`（L40：name: **Ident 非可选**/dir/name_range/source）；`CheckerPortId(pub u32)`（L47——**u32 序号而非 arena Idx**，def_id.rs 按 `ports.get(index)` 使用 L50）。
- 双入口：纯函数 `lower_checker_decl`（L49-59，只做骨架）与 ctx 版（L62-77，追加 declarations 并 alloc 进 checkers arena）；**双函数同名重载**是本文件特殊设计（covergroup.rs 同模式）。
- `lower_checker_owner`（L79-106）：OwnerKind::Checker 的 body 查询实现——cast 失败给空 Body；成功建 LoweringCtx 调 ctx 版 lower_checker_decl。
- `lower_checker_ports`（L108-138）：**无名端口跳过**（L123-125）、无 SourceAstId 跳过（L126-128）——宽松收集；name_range 经 SyntaxTokenWithParent 相对 checker 语法节点求（L120-122）。
- `lower_checker_declarations`（L140-161）：只收 CheckerDataDeclaration（包装形态）/DataDeclaration/NetDeclaration 三类成员；`lower_checker_port_direction`（L168-178）：四关键字→PortDirection，缺省 Input。
**公开 API**：CheckerDef/CheckerPort/CheckerPortId/CheckerId + `lower_checker_decl` 纯函数 + `lower_checker_owner` 查询体。
**依赖/被依赖**：依赖（9 出边）→ ast_id_map/lib/syntax/has_text_range/utils::text_edit（CheckerPort 内嵌 TextRange）；被依赖（7 入边）→ body/container/def_id/lib/scope/symbol + ide/document_symbols。
**改动影响面**：CheckerPortId 若改成 Idx 会破坏 def_id.rs L44-52 的 Vec 索引；checker owner 的 body 里 `checkers` arena 必须恰一个元素（container.rs as_checker 的不变量，L76）。
**集成点**：新 checker 成员种类（如 clocking/coverpoint）在 lower_checker_declarations 的 match 加臂。

---

## `crates/hir-def/src/constraint.rs`（247 行）
**角色**：constraint 块 HIR——8 种约束形态递归树 + dist 约束表 + 约束声明/原型/内联块的 lowering。
**关键结构与不变量**：
- `DistWeight`（L20：op/extra_op/expr）/`DistItem`（L27：Range{range: InsideRange, weight}/Default{weight}）/`DistConstraintList`（L33）。
- `Constraint`（L38-70，8 变体）：Expression{soft}/Uniqueness{ranges}/Implication{left, constraint: Idx<Constraint>}/Conditional{condition, constraint, else_constraint}/Loop{array, variables, constraint}/Disable{soft, name}/SolveBefore{before, after}/Block(Box<[Idx]>)——**自引用 arena 树**（constraint 引用同 arena 内 Idx）。
- `ConstraintDef`（L75：name/constraint/prototype: bool）——原型=true 且约束体是空 Block（L159）。
- `lower_expression_or_dist`（L84-88）：产 `Expr::Dist`（expr.rs 的变体载体——dist 不是独立 Constraint）。
- `lower_inside_range`（L118-132）：括号内剥皮（L119-124）、ValueRangeExpression→Range、否则 Expr。
- `lower_constraint_decl`（L134-152）/`lower_constraint_prototype`（L154-171）/`lower_inline_constraint_block`（L173-178，randomize with 用）；`lower_constraint_item`（L180-231）八臂全递归；`alloc_constraint`（L233-246）统一进 body.constraints + src。
**公开 API**：Dist 族/Constraint/ConstraintDef + ConstraintId/ConstraintDefId + 上述 pub(crate) lowering。
**依赖/被依赖**：依赖（9 出边）→ expr.rs/lib/lower/syntax；被依赖（5 入边）→ aggregate（class 成员）/body/lib + hir-ty×2（display、tests）。
**改动影响面**：Constraint 自引用结构要求 constraints arena 在 Body 内稳定（PartialEq 递归比较由 arena Idx 语义保证）；class 约束成员（aggregate.rs L349-365）与 randomize-with 内联块（expr.rs L973-975）是两个消费端。
**集成点**：新的约束语法形态加 Constraint 变体 + lower_constraint_item 臂；hir-ty 的 constraint 求值与 display 直接遍历此树。

---

## `crates/hir-def/src/covergroup.rs`（307 行）
**角色**：功能覆盖构造——covergroup/coverpoint/cross/coverage bin 的 HIR、lowering 与 covergroup owner body 查询。
**关键结构与不变量**：
- `CovergroupDef`（L21：name/options/coverpoints/crosses）；`CoverpointDef`（L31：name: Option（label 来）/expr/iff/options/bins）；`CrossDef`（L42：name/items/iff/options/bins）；`CoverageBin`（L53：name/wildcard/size/initializer/iff）；`CoverageBinInitializer`（L62，6 变体：Default/Expr/Ranges{ranges, with}/IdWithExpr/Transitions/Unsupported）；`TransitionSet`（L72）/`TransitionRange`（L77：items+repeat: Option<Selector>）；`CrossBin`（L83：name+selector: **SyntaxKind 原样保留**，不展开 cross bin 选择器语义）。
- 双入口模式：纯 `lower_covergroup_decl`（L88-95 骨架）+ ctx 版（L98-146）：遍历 members——CoverageOption→options、Coverpoint/CoverCross 逐个 alloc 进 coverpoints/crosses arena 并挂 id、EmptyMember 跳过、其他 report_unsupported。
- `lower_coverpoint`（L148-169）：name 走 `lower_named_label_opt`（coverpoint 无名时用 label，与 item_tree.rs L493-497 的 ItemName 对应）；`lower_cross`（L171-199）：items 是名字表达式列表（L174-177）；`lower_coverage_initializer`（L211-265）六臂，Transitions 递归 sets→ranges→items/repeat。
- `lower_covergroup_owner`（L278-307）：OwnerKind::Covergroup 的 body 查询体（同 checker 模式：cast 失败空 Body）。
**公开 API**：上述类型 + CovergroupId/CoverpointId/CrossId + `lower_covergroup_decl` + `lower_covergroup_owner`。
**依赖/被依赖**：依赖（15 出边）→ body/db/expr.rs/lib/lower/owner/source_map；被依赖（7 入边）→ body/container/def_id/lib/symbol + hir-ty tests + ide/document_symbols。
**改动影响面**：coverpoint/cross 落在**covergroup owner 自己的 body**（而非父 owner），def_id.rs L431-443 依赖该布局；CrossBin 的 SyntaxKind 透传若展开为结构会改 hir-ty 测试快照。
**集成点**：新 coverage 成员（如 option with expression 扩展）在 ctx 版 lower_covergroup_decl 的 match 加臂。

---

## `crates/hir-def/src/dpi.rs`（170 行）
**角色**：DPI import/export 声明的 HIR 与 lowering——foreign 函数接口的声明侧。
**关键结构与不变量**：
- `DpiSpec`（L16：Dpi/DpiC）；`DpiImportProperty`（L22：Context/Pure）；`DpiImport`（L28：spec/property/c_identifier/method: **Subroutine 完整签名**）；`DpiExportKind`（L38：Function/Task）；`DpiExport`（L44：spec/c_identifier/kind/name）。
- `lower_dpi_import`（L54-109）：spec 字符串校验（"DPI"/"DPI-C" 精确匹配，lower_spec L153-170）→property 二关键字→method 必须 task/function 关键字（L73-83）→`lower_subroutine_prototype` 失败报 invalid 放弃（L92-95）；`lower_dpi_export`（L111-150）：kind 关键字必须存在（L125-131）、name 必须有（L133-138）。
**公开 API**：上述类型 + DpiImportId/DpiExportId + 两个 pub(crate) lowering。
**依赖/被依赖**：依赖（8 出边）→ lib/lower/subroutine/syntax；被依赖 → body/diagnostics/lib（3 入边）。
**改动影响面**：diagnostics.rs 测试断言 DPI 双向降级（context/pure import 的 spec/property/c_identifier/ports 计数，测试段 L87-99、124-128）；Subroutine 结构改动连带 method 字段。
**集成点**：DPI 导入的 method 是普通 Subroutine——hir-semantics 调用解析无需特判；c_identifier 供未来外部符号链接使用。

---

## `crates/hir-def/src/elab_system_task.rs`（104 行）
**角色**：elaboration 系统任务（$fatal/$error/$warning/$info/$static_assert）的 HIR 与 lowering。
**关键结构与不变量**：
- `ElabSystemTaskKind`（L12，5 种）+ `from_name`（L21-30，五个名字精确映射，其他 None）；`ElabSystemTaskArgument`（L34：Ordered(ExprId)/Empty）；`ElabSystemTask`（L40：kind+SmallVec<[Arg;4]>）。
- `lower_elab_system_task`（L48-103）：缺名（L52-58）或未知名（L60-66）报 invalid 放弃；参数逐个降级——Ordered 走 **lower_property_expr**（L75，elab 任务实参允许 SVA 表达式域）、Empty 保留、**NamedArgument 非法**（L81-87 报错放弃）；alloc 进 elab_system_tasks arena。
**公开 API**：三类型 + ElabSystemTaskId + lowering。
**依赖/被依赖**：依赖（6 出边）→ expr.rs/lib/lower/syntax；被依赖 → body/lib（2 入边）。
**改动影响面**：$static_assert 等名字集合改动需同步 hir-ty 常量求值（如果消费实参）。
**集成点**：新 elaboration 任务名在 from_name 加臂即可。

---

## `crates/hir-def/src/external.rs`（391 行）
**角色**：extern 声明族——extern module（含参数/端口全表）、extern UDP、extern interface method 的 HIR 与 lowering。
**关键结构与不变量**：
- `ExternInterfaceMethod`（L19：method+fork_join）；`ExternParameter`（L27：Type{name,default}/Value{kind,name,ty,default}）；`ExternModulePort`（L33：header: PortHeader+name）；`ExternNonAnsiPort`（L39：label+references）；`ExternModulePortList`（L46：Ansi/NonAnsi）；`ExternModuleDecl`（L52：kind/name/imports/parameters/ports）；`ExternUdpDecl`（L63：name+ports）。
- `lower_extern_udp_decl`（L71-141）：primitive 关键字必须存在（L75）；三种 UdpPortList——Ansi 逐口（output 单名/input 多名，缺名均 invalid 放弃 L91-113）、NonAnsi 逐名、**Wildcard 非法**（L125-131）。
- `lower_extern_module_decl`（L143-184）：**Package kind 非法**（L149-155）；imports 复用 lower_package_imports；参数/端口委托两个 helper。
- `lower_extern_parameters`（L186-238）：类型参数/值参数两路，值参数关键字必须是 parameter/localparam（L213-219）；`lower_extern_ports`（L240-314）：Ansi——ImplicitAnsiPort 走 `lower_port_header(port.header(), previous)`（**前一口 header 继承**，L249）+ExplicitAnsiPort 走 lower_explicit_ansi_header；NonAnsi——Implicit/Explicit 两态，**Empty 非法**（L283-289）、label 与 references 全空非法（L295-301）；Wildcard 非法（L306-312）。
- `lower_extern_port_expression`（L316-330）：PortReference 单名/PortConcatenation 多名；`lower_extern_interface_method`（L332-390）：task/function 关键字必须（L344-354）+ prototype 失败 invalid（L365-369）+ fork_join 限定（L371-380）。
**公开 API**：上述类型 + ExternModuleDeclId/ExternUdpDeclId/ExternInterfaceMethodId + 四个 pub(crate) lowering。
**依赖/被依赖**：依赖（16 出边）→ declaration/expr.rs/expr::data_ty/lib/lower/module（ModuleKind/port::PortHeader）/subroutine/syntax；被依赖 → body/diagnostics/lib（3 入边）。
**改动影响面**：diagnostics.rs 测试断言 extern module 参数两型（Value/Type{default:Some}）与端口 in_a/out_b（测试段 L99-113）；PortHeader 结构（module/port.rs）改动连带 ExternModulePort。
**集成点**：extern 声明给模块解析（hir-semantics/ide module_resolution）提供"库外模块"的签名来源；端口 header 继承复用 module::port 的同一套 helper——两处行为保持一致的关键复用点。

---

## `crates/hir-def/src/file.rs`（465 行）
**角色**：**文件级 compilation-unit / library-map 的顶层 lowering 分派器** + typedef/forward typedef/config/UDP/library/匿名 program 的具体降级 + file/anonymous-program 两个 owner body 查询体。
**关键结构与不变量**：
- `LowerFileCtx = LoweringCtx<BodyStore>`（L28）。
- `lower_struct_type`（L31-60）：file 级 struct（与 body.rs lower_body_struct_type 镜像但用 alloc_with_source 取 ast）。
- `lower_typedef`（L62-86）：**先占位（ty:None）→ record_body_typedef → 回填 ty**（L64-83，两段式，与 body.rs L722-744 同型）；`lower_forward_typedef`（L88-131）：typedef 关键字校验 + ForwardTypedefKind::from_restriction（枚举/struct/union/class/interface class，L108-120）。
- `lower_subroutine_decl`（L133-139）：**不降签名与体**——只 `owner_for_node(OwnerKind::Subroutine)` 取 owner（注释 L137：body 查询负责真正降级）。
- `lower_anonymous_program`（L141-173）：只认 function/class/covergroup 三类成员。
- `lower_config_decl`（L175-194）/`lower_udp_decl`（L196-239，端口三态收集 + UdpEntry 的 input_kinds/current/next 全以 **SyntaxKind** 记录 L226-229——语义求值留待下游）/`lower_library_decl`（L241-261）/`lower_library_include`（L263-277）。
- `lower_file`（L279-386）：**compilation-unit 成员总分派 ~28 臂**——Module/AnonymousProgram/Checker/Covergroup 经 owner_for_node 取 owner（每处 expect "must have a canonical owner"）；各声明族失败（None）`continue` 跳过该 item；PackageImport 直接 alloc 进 package_imports 不产 BodyItem（L354-361）；不支持成员 report_unsupported。
- `lower_library_map`（L388-404）：library 声明/include 两类。
- `lower_anonymous_program_owner`（L407-434）/`lower_file_owner`（L436-465）：两个查询体——file owner 按 root kind 二分（CompilationUnit→lower_file / LibraryMap→lower_library_map，L452-458）。
**公开 API**：上述 pub(crate) 函数族 + `pub use HirFileId`（L3，re-export）+ `pub mod config/library/udp`（L24-26）。
**依赖/被依赖**：依赖（14 出边）→ aggregate/body/container/db/lower/owner/source_map/typedef/syntax；被依赖（1 入边）→ lib.rs——**body.rs 的 body_input 是唯一消费者**（crate 内最大分派汇聚点却只被 body 查询引用）。
**改动影响面**：新增 compilation-unit 级构造必须在此加臂（否则 file_lowering_diagnostics 会把它报成 "unsupported compilation-unit member"，diagnostics.rs 巨型测试直接红）；owner_for_node 的 expect 意味着 owner_table 未登记该节点即 panic——新构造要同步 owner.rs 的收集规则。
**集成点**：file owner 是所有顶层内容的宿主；config/udp/library 的降级目前是"结构骨架"级（SyntaxKind 透传），是语义深化的预留接口位。

---

## `crates/hir-def/src/file/config.rs`（18 行）
**角色**：config 声明的最小 HIR 载体。
**关键结构**：`ConfigDecl`（L7-11：name/top_cells: Box<[Ident]>/rules: Box<[ConfigRule]>）；`ConfigRule`（L14-16：**kind: SyntaxKind 单字段**——规则体只记语法类别，不展开语义）；`ConfigDeclId`（L18）。
**公开 API**：三个类型。
**依赖/被依赖**：依赖 → crate::Ident；被依赖 → body/symbol（BodyItem 与 DefOriginLoc::Config）+ ide（document_symbols/navigation_target）。
**改动影响面**：加字段需同步 file.rs lower_config_decl（L175-194）与 def_id.rs DefOriginLoc::Config 的 name 投影。
**集成点**：config 语义（design/liblist 规则求值）未来在此扩 ConfigRule。

---

## `crates/hir-def/src/file/library.rs`（20 行）
**角色**：library map 的最小 HIR 载体。
**关键结构**：`LibraryDecl`（L7-11：name/file_paths/include_dirs，路径全以 Ident 承载）；`LibraryInclude`（L16-18：file_path: Option<Ident>）；两个 Idx 别名（L13/20）。
**公开 API**：三个类型。
**依赖/被依赖**：依赖 → crate::Ident；被依赖 → body/symbol + ide（document_symbols/navigation_target）。
**改动影响面**：file.rs lower_library_decl/lower_library_include（L241-277）是唯一生产端。
**集成点**：未来库文件装载（把 file_paths 解析为 FileId）以这两结构为输入。

---

## `crates/hir-def/src/file/udp.rs`（27 行）
**角色**：UDP（user-defined primitive）声明的 HIR 载体。
**关键结构**：`UdpDecl`（L8-13：name/ports/initial/entries）；`UdpInitialValue`（L16：name）；`UdpEntry`（L21-25：input_kinds: SmallVec<[SyntaxKind;4]>/current/next——**真值表条目全以 SyntaxKind 编码**，语义求值留下游）；`UdpDeclId`（L27）。
**公开 API**：四个类型。
**依赖/被依赖**：依赖 → crate::Ident + syntax::SyntaxKind；被依赖 → body/symbol + ide（document_symbols/navigation_target）。
**改动影响面**：条目编码改动会破坏 diagnostics.rs 测试 `file_declarations_preserve_config_and_udp_structure`（L592-615 断言 entries.len()==1）。
**集成点**：UDP 语义表求值（LFT 表展开）的扩展位。

---

## 自检记录

行号锚抽 3 处核验（全部来自本会话 Read 输出）：
1. `body.rs` L283 `pub struct Body`（arena 集合起点）、L557 `fn body_input`（tracked 分派器）——与读文件时行号一致；
2. `def_id.rs` L525 `pub struct DefId(InternedDefId)`、L372 `definition_table` tracked query——一致；
3. `item_tree.rs` L135 `header_fingerprint` 访问器、L310 固定点循环不在此文件（在 design_map.rs L310 `loop {`）——design_map.rs L310-357 为固定点循环，一致。

（另：ast_id_map.rs L33 `SourceAstId(pub u128)`、expr.rs L811-817 `<=` 双义分支、diagnostics.rs L44 `file_lowering_diagnostics`、db.rs L143 `set_lru_capacity` 均已在正文标注。）
