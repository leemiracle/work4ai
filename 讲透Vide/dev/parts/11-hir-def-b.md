# 11-hir-def-b 精读手册

> 模块定位：本单元是 `crates/hir-def` 的骨架层（29 文件，共 10,534 行），覆盖 crate 门面（lib.rs）、AST→HIR 降级基础设施（lower.rs/source_map.rs/source_projection.rs/owner.rs）、按 SV 语法域拆分的降级器（module/stmt/literal/subroutine/generate/port 等）、名字解析三件套（symbol.rs/scope.rs/pathres.rs）以及外围设施（region_tree.rs/unit_index.rs/ty.rs 等）。在 vide 三层架构（Salsa RootDb + VFS + HIR）中处于 HIR 层核心：向下消费 slang 风格 syntax 树（`crates/syntax`）与预处理产物（`preproc-expand` 的 HirFileId），向上为 `hir-ty`（类型推断）与 `ide`（LSP 功能）提供位置无关的 arena 化 HIR、canonical owner 身份与 Salsa query。crate 约束（lib.rs L1-8）：只可依赖 `preproc-expand`，不得依赖 type inference / semantic adapters / IDE features。

---

## `crates/hir-def/src/lib.rs`（211 行）

**角色**：crate 门面——声明全部 40 个子模块、定义 `Ident` 别名与 package import/export 降级，以及所有降级器共用的 arena 分配辅助函数。

**关键结构与不变量**：
- 模块声明块 L12-53：`lower` 是 `pub(crate)`（L36），其余全公开；`#![feature(decl_macro)]`（L10）支撑两个 pub(crate) 宏。
- `impl_arena_getters!`（L55-68）：为 container 批量生成 `GetRef<$id>` 实现，是全 crate "arena + Idx 查询" 模式的宏入口。
- `impl_source_map_getters!`（L70-83）：批量生成 `Get<$id> -> Option<SourceAstId>`，source map 反查的标准形状。
- `Ident = SmolStr`（L89）、`DEFAULT_NAME = "unnamed"`（L91）。
- `PackageImport { package, item: Option<Ident>, source }`（L94-101）：`item=None` 表示 `pkg::*`；`source` 记录声明点 SourceAstId，供 pathres 的 point-of-reference 过滤。
- `PackageExport`（L103-108）：`Package{package,item,source}` 或 `All{source}`（`export *::*` 再导出全部导入项）。
- `lower_ident`（L135）/`lower_ident_opt`（L141）：后者把空 ident 归一为 `None`（缺失标识符）——全 crate "缺失名不产生 Def" 的不变量源头。

**公开 API**：`lower_package_exports`（L110，pub(crate)）、`lower_package_export_all`（L127）、`lower_package_imports`（L152）、`lower_ident`/`lower_ident_opt`（L134/L141，pub）、`lower_named_label_opt`（L147）、`alloc_with_optional_source_entry`（L169）、`alloc_with_source_entry`（L185）、`alloc_with_source`（L197，自动取 ast_ids 中节点身份再入 arena+source map）。

**依赖/被依赖**：依赖 `crates/syntax/src/lib.rs`（ast/Token）、`crates/utils`（get/text_edit 经宏）与 crate 内全部模块；被依赖 56 个（图谱：54 imports + Cargo.toml×2）——crate 内所有文件 + `hir-semantics`/`hir-ty`/`ide`/`src/lsp_ext/to_proto.rs` 的通用 re-import 汇点。

**改动影响面**：改 `alloc_with_*` 系列或两个宏会波及所有降级器（lower.rs 的 store 层依赖其分配语义）；改 `PackageImport/Export` 字段会同时破坏 scope.rs 的 `insert_package_import`（L157）、pathres.rs 的 ImportCollector 与 design_map 的 `resolve_import`；模块增删需同步 db.rs 的 LRU 注册表（db.rs L149-154）。

**集成点**：二次开发者新增 HIR 节点类型时，先在此挂模块，再用 `impl_arena_getters!` 接入 Body 的查询面；跨模块复用的 ident 降级一律走 `lower_ident_opt` 保持"空即缺"语义。

## `crates/hir-def/src/lower.rs`（408 行）

**角色**：降级基础设施中枢——定义共享语法输入 `LoweringSyntax`、store trait 分层（`LoweringStore`/`ProcStore`/`ModuleItemStore`/`CheckerStore`）与降级上下文 `LoweringCtx<Store>`，所有按语法域拆分的降级器都写成它的扩展方法。

**关键结构与不变量**：
- `LoweringSyntax`（L32-53）：缓存 `(file_id, tree, ast_ids, owners)` 四元组，注释 L29-30 明确动机——ItemTree 发现阶段与 body 降级复用同一份 canonical source 身份以防 Salsa query cycle。
- `LoweringStore` trait（L62-69）：暴露 exprs/event_exprs/declarators/stmts/declarations/body 六对 `(Arena, SourceMap)`；`impl_lowering_store!` 宏（L71）为 `BodyStore<'_>` 统一实现，字段名与 `Body`/`BodySourceMap` 严格对齐。
- `CheckerStore`（L103）/`ProcStore`（L118）/`ModuleItemStore`（L134-141）：按需叠加 checker/procs/cont_assigns/defparams/instantiations/param_assigns/instances/port_connections——store 分层决定了"某语法域降级器需要哪些 arena"的编译期约束。
- `LoweringCtx<Store>`（L176-188）：`scope_stack: Vec<OwnerId>`（body 作用域栈）+ `default_nettype: Arc<[(TextSize, Option<NetKind>)]>`（文件级指令表）。不变量：栈底恒为 root owner（`new_with_syntax` L219 `ensure_root`；`leave_body_scope` L263 断言不可弹出根）。
- `enter_body_scope`（L253）：断言新 owner 的图父 == 当前栈顶（L257 "body scope must follow the canonical owner graph"），并同步插入 `scope_graph`——降级期作用域树与 owner 图一致性由该断言守护。
- `net_kind_at`（L227）：`partition_point` 二分定位 offset 之前最近的 `` `default_nettype ``；无指令时回落 SV 默认 `wire`。
- `implicit_net_kind`（L319-328）：`default_nettype none` 下隐式 net 非法——仍降级为 `wire` 保持 body 一致，诊断另行上报（L324）。
- `emit_diagnostics`（L330-343）：take 出诊断并对每条 `tracing::warn!` 留痕。

**公开 API**：`LoweringSyntax::new/for_owner`（L40/L49）、`LoweringCtx::new/new_with_syntax`（L191/L202）、`owner_for_node`（L234）、`source_id`（L239，expect 每个 AST 节点必有身份）、`current_scope/current_owner`（L245/L249）、`push_body_item/record_body_declaration/record_body_declarator/record_body_typedef/record_body_statement`（L266-293）、`report_unsupported/report_invalid`（L295/L305）、以及 L346-408 按 store 分层的六组 arena 访问器转发。

**依赖/被依赖**：依赖 body.rs/checker.rs/declaration.rs/expr.rs/module 子域/proc.rs/stmt.rs/ty.rs/ast_id_map.rs/db.rs/owner.rs/source_map.rs 与 `crates/syntax`、`crates/utils`、`preproc-expand`；被依赖 24 个文件——aggregate/assertion/bind/body/constraint/covergroup/declaration/dpi/elab_system_task/expr 全家/external/let_decl/lib/module 六个语法域文件/net_alias/net_type_decl/time_units。

**改动影响面**：store trait 方法签名变化会级联全部 24 个下游降级器；`scope_stack` 语义变化会破坏 scope.rs 的 per-owner scope 构建（其遍历依赖降级时写好的 scope_graph）；`default_nettype` 字段去掉会直接让 ty.rs 的 `default_nettype_directives`（L52）查询悬空。

**集成点**：新增语法域降级器的方式是定义新 store trait（若有新 arena）+ 为 `LoweringCtx<ThatStore>` 写扩展方法（continuous_assign.rs/defparam.rs 是最小样例）；`LoweringSyntax::for_owner` 是自建降级入口的标准工厂。

## `crates/hir-def/src/let_decl.rs`（55 行）

**角色**：`let` 声明（sequence 上下文的参数化表达式绑定）降级器。

**关键结构与不变量**：`LetDecl { name, ports: SmallVec<[AssertionPort; 4]>, expr: ExprId }`（L17-21）——不变量：三重前置校验全过才 alloc（let 关键字 L27、名字 L31、等号 L35，任一失败 `report_invalid` + 返回 None，即"残缺 let 不入 arena"）。

**公开 API**：`LetDeclId = Idx<LetDecl>`（L23）、`LoweringCtx<BodyStore>::lower_let_decl`（L26，pub(crate)，Option 返回）。

**依赖/被依赖**：依赖 assertion.rs（AssertionPort）、expr.rs、lower.rs、lib.rs、syntax；被 body.rs 与 lib.rs 引用。

**改动影响面**：改字段会破坏 body.rs 的 BodyItem::LetDeclId 消费与 symbol.rs DefOriginLoc 无关（let 声明走 Decl 通道）。

**集成点**：AssertionPort 复用 assertion.rs 的端口降级，是 assertion 域与 module 域共享端口形状的范例。

## `crates/hir-def/src/literal.rs`（95 行）

**角色**：字面量 HIR 类型与降级——SV 全部字面量形态到 `Literal` 的映射。

**关键结构与不变量**：
- `Literal`（L9-17）：Int(SVInt)/Float/Time{val,unit}/Str/UnbasedUnsized(Bit)/Null/Unbounded 七变体。
- `FloatTypeWrapper(u64)`（L20）：f64 位模式存储，实现 f32↔f64 无损互转（L32-54）与 Display（L56）——不变量：Hash/Eq 按 bit 语义（非数值语义），-0.0 与 0.0 不等。
- `lower_literal`（L62-91）：八种 ast literal 一一对应；`DefaultPatternKeyExpression` 显式返回 None（L89，pattern key 不是值字面量）。

**公开 API**：`Literal`、`FloatTypeWrapper`（含 `to_bits` L27）pub；`lower_literal`（L62）/`lower_integer_vector`（L93）pub(crate)。

**依赖/被依赖**：仅依赖 syntax（value::{Bit,SVInt,TimeUnit}）；被 expr.rs、lib.rs、hir-ty 的 compatibility.rs/display.rs、ide 的 render.rs 消费。

**改动影响面**：加字面量变体会牵动 hir-ty 常量折叠与 ide render 的穷尽 match。

**集成点**：SVInt 由 syntax crate 负责（宽度/符号/四态），HIR 层不做二次解释——跨层边界的干净样例。

## `crates/hir-def/src/proc.rs`（50 行）

**角色**：过程块（initial/always*/final）降级器。

**关键结构与不变量**：`ProcType`（L15-21，`#[default] Initial`）+ `AlwaysKeyword`（L7-12 四变体）；`Proc { proc_ty, owner: OwnerId }`（L24）——不变量：`owner_for_node(..., ProceduralBlock)` 必须 Some（L35 expect），即每个过程块降级前必已在 OwnerTable 注册 canonical owner。

**公开 API**：`ProcId = Idx<Proc>`（L29）、`LoweringCtx<Store: ProcStore>::lower_proc`（L32）。

**依赖/被依赖**：依赖 lower.rs/owner.rs/syntax；被 body.rs、diagnostics.rs、lib.rs、ide 的 document_symbols.rs 引用。

**改动影响面**：Proc.owner 字段是 owner.rs 测试链（owner.rs L575 `block_statements_store_their_canonical_owner`、L607 `nested_blocks_share_one_body`）与 body.rs 分派（L559 `lower_procedural_body`）的枢纽。

**集成点**：泛型 `<Store: ProcStore>` 使 module 域与 generate 域都能降级过程块（module.rs L250 / generate.rs L164 都调用）。

## `crates/hir-def/src/typedef.rs`（58 行）

**角色**：typedef HIR 数据与前向 typedef（forward typedef）限制类型降级。

**关键结构与不变量**：`Typedef { name: Option<Ident>, ty: Option<DataTy>, forward_kind: Option<ForwardTypedefKind> }`（L8-12）——三者皆 Option，对应"前向声明无体"的合法形态；`ForwardTypedefKind`（L17-24）五变体，`from_restriction`（L27-42）按 keyword_1/keyword_2 组合判定（interface+class 双关键字 L36-38 是唯一两键组合）。

**公开 API**：`TypedefId = Idx<Typedef>`（L14）、`lower_typedef_data_ty<Ctx>`（L44-58）——泛型回调注入 `lower_struct_type`/`lower_data_ty`，把 struct 联合体提升为 `DataTy::Struct(OwnerRef)` 而不依赖具体 ctx 类型。

**依赖/被依赖**：依赖 aggregate.rs（StructId）、expr/data_ty.rs、container.rs（OwnerRef）、owner.rs；被 block.rs/body.rs/diagnostics.rs/file.rs/lib.rs/symbol.rs/hir-ty×3/ide×2 共 12 个文件消费。

**改动影响面**：Typedef 是 scope.rs `insert_body_typedefs`（L101）与 symbol DefOriginLoc::Typedef 的数据源；改 forward_kind 判定会影响前向声明与实定义匹配的诊断。

**集成点**：`lower_typedef_data_ty` 的回调注入模式让 checker 域与 module 域共用 typedef 体降级而互不依赖。

## `crates/hir-def/src/net_alias.rs`（42 行）

**角色**：`alias` 网络别名语句降级器。

**关键结构与不变量**：`NetAlias { nets: SmallVec<[ExprId; 4]> }`（L15-17）；不变量：必须含 `ALIAS_KEYWORD`（L23）且至少两个 net（L29-31），否则 report_invalid + None。

**公开 API**：`NetAliasId = Idx<NetAlias>`（L19）、`LoweringCtx<BodyStore>::lower_net_alias`（L22）。

**依赖/被依赖**：依赖 expr.rs/lower.rs/lib.rs/syntax；被 body.rs、lib.rs 引用。

**改动影响面**：极小；BodyItem::NetAliasId 的消费方是 symbol/scope 的 Def 通道。

**集成点**：与 let_decl.rs 同为"校验即降级"最小降级器模板。

## `crates/hir-def/src/net_type_decl.rs`（66 行）

**角色**：用户自定义 nettype（`nettype` 声明）降级器。

**关键结构与不变量**：`NetTypeDecl { name, ty: DataTy, with_function: Option<Ident> }`（L15-19）；不变量：`with_function` 存在时函数名必须可取（L46-52 否则 report_invalid），名字缺失即拒绝（L35）。

**公开 API**：`NetTypeDeclId = Idx<NetTypeDecl>`（L21）、`lower_net_type_decl`（L24）。

**依赖/被依赖**：依赖 expr/data_ty.rs/lower.rs/lib.rs/syntax；被 body.rs、lib.rs 引用。

**改动影响面**：nettype 的解析函数名（with_function）是 hir-ty 类型系统潜在的解析钩子数据源。

**集成点**：`with_function` 指向的自定义分辨率函数留给类型系统消费。

## `crates/hir-def/src/ty.rs`（127 行）

**角色**：网络类型 HIR（NetType/NetKind/Strength 系）+ 文件级 `` `default_nettype `` 指令的 Salsa 提取。

**关键结构与不变量**：
- `NetType { kind: NetKind, ty: DataTy }`（L10）；`NetKind`（L16-28）11 变体覆盖全部 SV 网络关键字；`lower_net_kind`（L30-46）token→kind 单射。
- `default_nettype_directives` query（L52-86，`#[salsa::tracked(lru = 128)]`）：遍历 root 全部 token 的 trivia 找 `DEFAULT_NET_TYPE_DIRECTIVE` 结构化 trivia 节点——不变量：指令 offset 取其首个 child token 的 range.start（L70-73，trivia 节点自身无 range）；`none` 词素经 `lower_net_kind` 映射为 `None`（L79）；产出按 offset 排序去重（L83-84）。
- `Strength`（L93）/`DriveStrength(Option, Option)`（L102）/`ChargeStrength`（L123）及 `lower_strength`（L104）/`lower_drive_strength`（L116）。

**公开 API**：NetType/NetKind/Strength/DriveStrength/ChargeStrength pub；`default_nettype_directives`（pub(crate)，经 db.rs L130 转发）、`set_default_nettype_lru_capacity`（L88）。

**依赖/被依赖**：依赖 base-db（salsa）、syntax、utils、ast_id_map/db/expr::data_ty；被 declaration.rs、lib.rs、module/continuous_assign.rs、module/port.rs、hir-ty/display.rs 消费。

**改动影响面**：该 query 被 lower.rs 的 `LoweringCtx` 构造消费（lower.rs L217）与 port.rs 隐式端口判定（port.rs L552）依赖；scope.rs 的测试 `default_nettype_selects_implicit_port_net_kind`（L1898）与 `default_nettype_directive_switches_mid_file`（L1919）直接钉死其行为。

**集成点**：新增编译指令若需"位置敏感、per-file、Salsa 缓存"，此文件是标准模板（trivia 提取 + offset 排序 + lru）。

## `crates/hir-def/src/time_units.rs`（128 行）

**角色**：`timeunit`/`timeprecision` 声明降级器。

**关键结构与不变量**：
- `TimeScaleMagnitude`（L10）只有 1/10/100 三档，`from_literal`（L17-25）严格匹配 f64 值。
- `TimeScaleValue { unit, magnitude }`（L28）；`TimeUnitsDecl { kind, value, precision }`（L40）。
- 不变量：`lower_time_scale_value`（L48-57）要求 token 必须是 `TIME_LITERAL` 且 real 值合法；`timeprecision` 声明不允许带 divider（L109-114 report_invalid），`timeunit` 的 divider 值非法亦拒绝（L98-105）。

**公开 API**：全部类型 pub；`lower_time_units_decl`（L60，`impl<Store: LoweringStore> LoweringCtx` 泛型）。

**依赖/被依赖**：依赖 lower.rs/lib.rs/syntax；被 body.rs、diagnostics.rs、lib.rs 引用。

**改动影响面**：diagnostics.rs 对 timeunit 重复声明等语义检查以此为数据源。

**集成点**：`lower_time_scale_value` 亦可被 time literal 表达式路径复用。

## `crates/hir-def/src/source_map.rs`（433 行）

**角色**：双核数据结构——`Lowered<T>`（位置无关 HIR + canonical 源身份 + 诊断的统一包装）与 `SourceMap<Hir>`（HIR arena ↔ SourceAstId 双向映射），是全 crate "语义身份与位置数据分离"原则的载体。

**关键结构与不变量**：
- `LoweredData` trait（L16）：`type SourceMap` 关联类型，约束 Debug+Eq。
- `LoweredDiagnostic`（L27）：kind（Invalid/Unsupported L21）+ syntax_kind + source + range + message；不变量：降级时 range 留 None，`diagnostics()`（L83-98）才从 `source_projection` 惰性回填 full_range。
- `Lowered<T>`（L41-46）：`Arc<T>` data + `Arc<T::SourceMap>` + `Arc<[LoweringDiagnostic]>`——L36-39 注释钉版设计：指针/range 是 revision-local，住在 AstIdMap 与 SourceProjection，语义降级与整文件位置变更解耦。
- `SourceMap<Hir>`（L306-309）：`src2hir: FxHashMap<SourceAstId, Idx>` + `hir2src: ArenaMap<Idx, SourceAstId>`。三条硬不变量（L312-339 的 debug assert）：`insert` 要求一个 HIR 值不得换 canonical source（L332）；`insert_alias` 要求 alias 目标已有 canonical source（L328）；`insert_preferred_alias` 才允许把 hir2src 改指向别名（L323）。
- 查询 trait 族：`HirLookup`（L239）、`SourceLookup`（L256）、`NamedSourceLookup`（L270）、`AstLookup`（L284，经 ast_id_map 反解 AST 节点）。
- `SourceInfo`（L195）：kind+full_range+focus_range，`from_origin`（L202）要求 full_range 必在。

**公开 API**：`Lowered::{new, file_id, data, data_ref, source_map, diagnostics, raw_diagnostics, source_map_arc, source, source_range, source_name_range, source_name_or_full_range, source_info, hir_id, hir_id_for_node, get}`（L48-177）、`Deref/AsRef<T>`（L180/L188）、`SourceMap::{insert, insert_alias, insert_preferred_alias, shrink_to_fit, iter, ranges, named_ranges, src_to_hir, hir_to_src}`（L312-375）。

**依赖/被依赖**：依赖 ast_id_map/db/source_projection/syntax/utils；被 20 个文件消费——crate 内 body/covergroup/db/diagnostics/file/has_source/lib/lower/module 四域 + ide 的 convert_port_declarations/code_lens/diagnostics/document_symbols/folding_ranges/inlay_hint/module_resolution/semantic_tokens。

**改动影响面**：alias 语义（测试 L407 `aliases_do_not_change_the_canonical_source`、L425 `a_hir_value_cannot_have_two_canonical_sources` should_panic）是 port.rs 隐式端口与 non-ANSI 端口反查的根基；改 `Lowered` 字段会波及所有 `lower_*_owner` 出口（module.rs L536 等）。

**集成点**：新语法域接入 IDE 的标准路径 = 定义 arena + 在 BodySourceMap 挂 SourceMap 字段 + `impl_source_map_getters!`（lib.rs L70）+ 在 `Lowered<T>` 上即可免费获得 source_range/hir_id_for_node 等 IDE 反查能力。

## `crates/hir-def/src/source_projection.rs`（109 行）

**角色**：canonical AST 身份 → 编辑器友好的源数据（指针/kind/range）的投影层，Salsa query 包装。

**关键结构与不变量**：
- `SourceOrigin`（L15-21）：file_id + `Option<SyntaxNodePtr>` + kind + full_range + focus_range。L12-13 注释钉版：**可导航性（node+full_range）与语义身份分离**——`is_navigable()`（L58）要求二者齐备。
- `SourceProjection`（L65）：`FxHashMap<SourceAstId, SourceOrigin>` 纯只读快照。
- `source_projection` query（L99-105，lru=128）：委托 `item_tree::build_source_projection(file_id, &tree, &ast_ids)` 构建。

**公开 API**：`SourceOrigin::{file_id, node, kind, full_range, focus_range, focus_or_full_range, is_navigable}`（L34-60）、`SourceProjection::{origin, node, origins, len, is_empty}`（L74-96）、`set_source_projection_lru_capacity`（L107）。

**依赖/被依赖**：依赖 ast_id_map/db/syntax::ptr/utils；被 db.rs、diagnostics.rs、item_tree.rs、lib.rs、ide/folding_ranges.rs 消费；source_map.rs 的 `Lowered::diagnostics/source_range` 全系方法都经 db 间接依赖它。

**改动影响面**：focus_range（名字高亮锚）缺失会导致 IDE hover/rename 退化到 full_range；item_tree.rs 的构建逻辑变更直接改变投影内容。

**集成点**：任何需要"HIR id → 源码 range"的 IDE 功能（semantic_tokens、inlay_hint、folding）都从这里取数而非直查语法树——保持 query 增量性。

## `crates/hir-def/src/stmt.rs`（600 行）

**角色**：过程语句 HIR（`Stmt`/`StmtKind` ~30 变体）与全部过程语句降级器。

**关键结构与不变量**：
- `Stmt { label, kind }`（L20）；`StmtKind`（L42-110）：Missing（缺源码）/Invalid/Unsupported(SyntaxKind)/Empty 四个错误态 + Expr/VoidCastedCall/TimingCtrl/ProcAssign/EventTrigger/Block(OwnerId)/Cond/Case/RandCase/CheckerInstance/循环六种（Forever/DoWhile/Repeat/While/For/Foreach）/断言两种/Wait 族/Disable/Jump。
- 不变量 1：`lower_stmt`（L190-206）**先 alloc 空 Stmt 占位再填 kind**（L193-205 两段式）——保证嵌套语句递归时 StmtId 已存在，环状引用安全。
- 不变量 2：`StmtKind::Block(owner)` 的 owner 必来自 `owner_for_node(..., OwnerKind::Block)`（L569-571 expect），语句块与 owner 图严格同步；`lower_nested_block` 把内容降级进**共享 body**（owner.rs 测试 L607 验证 nested blocks share one body）。
- `ForInit`（L141）：Init(声明列表) / Assign(表达式列表) / Missing 三态，由首 initializer 的 SyntaxKind 判定（L312-339）；for 变量声明可携带继承类型（L321-325）。
- `AssertionAction { pass, fail }`（L37）+ `AssertionKind` 五变体（L28），`lower_assertion_kind`（L591-600）未知关键字回落 Assert。
- 辅助降级：`lower_unique_or_priority`（L581）、`lower_block_stmt`（L568）、`alloc_missing`（L576，Missing 语句无 source 记录——scope.rs 测试 L1283 钉版）。

**公开 API**：Stmt/StmtId、全部 kind 枚举、`lower_stmt_opt`（L186）/`lower_stmt`（L190）、`lower_immediate_assertion_member`（L391）/`lower_concurrent_assertion_member`（L400）。

**依赖/被依赖**：依赖 expr 全家（ExprId/DataTy/DeclId/TimingControl）、instantiation.rs（CheckerInstance）、lower.rs、owner.rs、lib.rs；被 13 个文件消费——block/body/def_id/design_map/expr::declarator/lib/scope/symbol + hir-ty/infer.rs + ide 四个（document_symbols/folding_ranges/navigation_target/verilog_2005）。

**改动影响面**：StmtKind 变体增删是穷尽 match 灾区（hir-ty infer、ide document_symbols、scope.rs L124 的 Block 分支）；两段式 alloc 顺序改动会破坏自引用语句（label 引用自身所在块）。

**集成点**：新增过程语句的标准入口是 `lower_stmt_kind` 大 match（L208-249）加一支 + 枚举加变体；`CheckerInstance` 变体演示了语句层复用模块域 arena 的做法。

## `crates/hir-def/src/subroutine.rs`（141 行）

**角色**：function/task 签名 HIR 与降级——无 LoweringCtx 依赖的独立函数，供多处复用。

**关键结构与不变量**：
- `Subroutine { name: Option<Ident>, kind, ports, has_body }`（L14）+ Default（L21-30，Task/无端口/无体）。
- `SubroutineKind::Function { return_ty }`（L33-36）：**降级即求返回类型**（L113-114 `lower_ty(prototype.return_type())` 直接调用，注释语义：返回类型节点必存在，缺省即 void builtin）。
- `SubroutinePort { direction, ty, name, source }`（L39-44）逐端口带 SourceAstId；`SubroutinePortDir`（L49-57）六向，默认 Unknown；`map_direction`（L133-141）：INPUT 或缺失→Input、未知→Unknown。
- 不变量：`Ref` 方向 + `const` 关键字 → ConstRef（L90-92）；default 函数端口降为无名 Input 端口（L98-106）。
- `lower_name`（L120-131）：IdentifierName/IdentifierSelectName/ScopedName（递归取 right）三态。

**公开 API**：`lower_subroutine`（L59，pub——被 db.rs/aggregate/dpi/external 调）、`lower_subroutine_prototype`（L75，pub(crate)）+ 全部类型。

**依赖/被依赖**：仅依赖 lib.rs 的 ident 辅助、ast_id_map、expr::data_ty、syntax；被 15 个文件消费——crate 内 9 个 + hir-ty×3（display/infer/type_system）+ ide×3（navigation_target/render/signature_help）。

**改动影响面**：SubroutinePortId(u32) 是 scope.rs `build_subroutine_scope`（L396-399）与 DefOriginLoc::SubroutinePort 的索引基础；改动端口顺序语义会破坏签名补全（ide/signature_help.rs）。

**集成点**：独立函数签名（ast_ids+tree 显式传参）使 DPI 声明、extern 声明、prototype 都能复用同一降级；新声明形态接入只需调 `lower_subroutine_prototype`。

## `crates/hir-def/src/module.rs`（537 行）

**角色**：module/interface/program/package 声明的降级总入口（`lower_module_decl` 巨型成员分派）+ 参数/端口位置索引 API + `lower_module_owner` 出口。

**关键结构与不变量**：
- 位置索引函数族：`param_port_id_by_idx`（L31-55）——参数端口位置对齐参数列表，**type parameter 占位但无 declarator**（L38-45 返回 None）；`param_port_count`（L58-69）；`overridable_param_id_by_idx`（L71-84，只数 is_overridable 且 is_port 的）；`non_ansi_port_id_by_idx`（L86）/`ansi_port_decl_id_by_idx`（L93）。scope.rs 测试 L1880/L1981 钉死这些对齐语义。
- `ModuleKind`（L100-137）：from_header/from_ast 按 header/decl cast 判定；`is_instantiable` = Module|Interface|Program（L134，**Package 不可例化**）。
- `lower_module_decl`（L142-504）三段：①参数端口（L144-167）——`inherited_kind` 沿参数列表继承 localparam/parameter 语境，`param_ports` 记为 declarator arena 的 IdxRange（L159-166 首尾闭区间）；②端口列表三分派 Ansi/NonAnsi/Wildcard（L169-174）；③成员 match（L176-501）：可降级成员产出 BodyItem，unsupported 成员（嵌套 module L306、specify 项 L490、coverage 成员 L364 等 ~15 类）统一 `report_unsupported` + continue。
- modport 声明特例（L399-405）：一个声明产生多个 ModportId，逐个 push 进 items 后 continue。
- `lower_module_owner`（L507-537）：`debug_assert_eq!(owner.kind(db), OwnerKind::Module)`（L512）；AST cast 失败返回空 Lowered（L518-522）；`body.name` 从 header 取（L523）；收尾 shrink_to_fit + 带诊断构造。

**公开 API**：`ModuleKind` 全方法、五个位置索引函数（pub）、`LowerModuleCtx<'a> = LoweringCtx<BodyStore<'a>>`（L139）、`lower_module_decl`/`lower_module_owner`（pub(crate)）。

**依赖/被依赖**：依赖 port.rs/declaration.rs/body.rs/db.rs/owner.rs/source_map.rs/syntax + 子模块声明（L19-26）；被 14 个文件消费——container/def_id/external/lib/module 五个子文件/owner/unit_index + ide 的 module_resolution/references::search/render。

**改动影响面**：成员 match 是 SV 语法覆盖面清单——新增语法支持第一改点；`param_ports` IdxRange 语义变化会破坏 ide 补全（completion/engine/instantiation.rs）与 scope.rs 测试；`lower_module_owner` 被 body.rs L566 按 OwnerKind::Module 分派，AnonymousProgram 走 file.rs（body.rs L568）而非此处。

**集成点**：`param_port_id_by_idx`/`overridable_param_id_by_idx` 是参数覆盖（实例化 `#(.A(...))`）匹配的公共 API；`ModuleKind::is_instantiable` 是 unit_index 与 pathres 共同的例化门槛。

## `crates/hir-def/src/module/port.rs`（600 行）

**角色**：端口系统降级——ANSI/非 ANSI/通配三种端口表、端口头继承规则、非 ANSI 端口与体内声明的绑定。

**关键结构与不变量**：
- `PortDecl { header, decls: DeclsRange, name }`（L40）；`PortDirection`（L48，**默认 Inout**）；`PortHeader`（L57-74）Var{dir,var_kw,ty}/Net{dir,net_ty}/Interface{dir} 三态，`ty()`（L85-95）Interface 口返回默认 builtin 类型而非继承前头（L89-92 注释钉版）。
- `Ports` enum（L115-123）：NonAnsi{ports,refs,decls,bindings} 四 arena vs Ansi(Arena<PortDecl>)；Default = 空 Ansi（L127-131）。三个 `GetRef` 实现（L148-179）使两种形态统一按 Idx 取值（Ansi 下取 refs 会 unreachable）。
- `NonAnsiPort { label, refs: Option<IdxRange<PortRef>> }`（L182）/`PortRef { ident, select }`（L190）；`PortSrcs`（L198）双形态源映射。
- **非 ANSI 绑定**：`non_ansi_binding_role`（L102-112）把声明分为 port_decl 角色（0）/data|net 声明角色（1）/语句内（None 不可绑）；`bind_nonansi_declarations`（L436-492）按名匹配唯一 label 的端口——多 label 匹配跳过（L459-461），同角色冲突时整组撤销既有绑定（L480-488）。scope.rs 测试 L894/L922/L945 钉死这些消歧规则。
- **端口头继承**：`lower_port_header`（L496-559）——`ty_omitted` 且全 omitted 继承前头类型（L534-535）；input/inout 且类型隐式 → 隐式 net（L547-553，经 `implicit_net_kind` 尊重 default_nettype）；output+ImplicitType 同理；显式类型 → 变量口。`lower_explicit_ansi_header`（L561-578）`.name(expr)` 形态只覆盖方向保留前头类型。
- `lower_ansi_ports`（L274-325）：header 变量沿端口表滚动携带（L278-320）；`lower_nonansi_port`（L334-408）：Explicit 带 label+exprs、Implicit 取唯一 ref 的 ident 作 label（L379-387 debug_assert 恰一个）、Empty 双 None；PortConcatenation 折叠为 IdxRange（L361-366）。

**公开 API**：全部类型与 `lower_ansi_ports`/`lower_wildcard_ports`/`lower_nonansi_port`/`lower_port_decl`/`bind_nonansi_declarations`/`lower_port_header`/`lower_explicit_ansi_header`（均 pub(crate)）；`Ports::shrink_to_fit`（L134）。

**依赖/被依赖**：依赖 declaration.rs/expr 全家/ty.rs/utils::get/module.rs/lib.rs；被 19 个文件消费——crate 内 body/expr::declarator/external/module 三子文件/scope/symbol + hir-ty×2 + ide×9（convert_port_declarations、module_members、completion/instantiation、inlay_hint、navigation_target、semantic_tokens/port、signature_help 等）。

**改动影响面**：端口头继承规则是 ide `convert_port_declarations` code action 的直接依据；`Ports` 枚举形状改动波及 hir-ty/infer 的端口类型推导与 module.rs L86/L93 的索引函数。

**集成点**：`bind_nonanni_declarations` 在 module.rs 四处调用点（数据/网络/自定义网络/局部变量声明，L186-207）演示了"声明落地后回绑端口"的钩子模式；IDE 端口功能统一走 GetRef 面。

## `crates/hir-def/src/module/instantiation.rs`（192 行）

**角色**：模块/原语/checker 例化语句降级——Instantiation/Instance/ParamAssign/PortConn 四个 arena 的唯一生产者。

**关键结构与不变量**：
- `Instantiation { module_name, param_assigns, instances }`（L16-20）；`Instance { name, dimensions, connections, parent: InstantiationId }`（L25-30）——instance 反向持有父 Instantiation，pathres `instance_target_def_id`（pathres.rs L356-371）据此回溯。
- `ParamAssign`（L35-38）与 `PortConn`（L43-48）同构：Ordered/Named（Named 端口连接允许 `.a` 缺表达式与 `.(b)` 缺名，L46 注释）；PortConn 另有 Empty（`,,`）与 Wildcard（`.*`）。
- 不变量：**两段式分配**——`reserve_instantiation`（L53-60）先 alloc 空 Instantiation 占位，子实例降级时携带该 parent id，`finish_instantiation`（L62-64）最后回填（L70-76），保证 instance.parent 在 alloc 时即有效。
- `lower_name`/`rightmost_name_token`（L181/L185）：ScopedName 递归右取（checker 例化的名字可能是限定名）。

**公开 API**：四类型 + Idx 别名（L22/L32/L40/L50）、`lower_instantiation`（L66）/`lower_primitive_instantiation`（L79）/`lower_checker_instantiation`（L92）（pub(crate)）。

**依赖/被依赖**：依赖 expr.rs/expr::data_ty（Dimension）/lower.rs/lib.rs；被 17 个文件消费——bind/body/pathres/symbol + hir-semantics/resolver + ide 十二个（add_missing_connections、add_missing_parameters、convert_ordered_connections、sort_named_instantiation_items、folding_ranges、inlay_hint、navigation_target、semantic_tokens、signature_help 等）。

**改动影响面**：本文件是 ide 例化类 code action 的数据底座；`PortConn::Named` 的双 Option 语义改动会同时破坏四个 code action。

**集成点**：新例化形态（如 program 例化）只需加一个 `lower_*_instantiation` 分支；两段式占位法可复用于任何"父先于子"的递归 arena 结构。

## `crates/hir-def/src/module/modport.rs`（139 行）

**角色**：interface modport 声明降级。

**关键结构与不变量**：
- `ModportDef { name, ports }`（L9-12）；`ModportPortKind`（L23-27）：Simple{dir}/Subroutine{dir}/Clocking 三态——subroutine 口的 import/export 映射为 PortDirection（export→Output，L134-138）。
- 不变量：一条 modport 声明可产出多个 ModportDef（`items().children()` 逐 item alloc，L34-51）；`lower_modport_ports`（L56-102）只接受 ModportSimplePortList/ModportSubroutinePortList/ModportClockingPort 三类成员，其余 report_unsupported（L92-97）。
- clocking 口必须有名字（L83-89）；L59-60 注释明确对齐 slang 的建模方式。

**公开 API**：三类型 + `ModportId`（L14）、`lower_modport_declaration`（L30）。

**依赖/被依赖**：依赖 module.rs/port.rs（PortDirection）/lib.rs；被 body.rs、symbol.rs 引用。

**改动影响面**：ModportId 进 DefOriginLoc::Modport（symbol.rs L53）与 scope.rs 模块作用域（L243-245）；pathres 测试 `resolve_path_descends_interface_instances_to_modports`（L1382）覆盖其层次可达性。

**集成点**：modport 是 interface 例化后层次下降的终点之一（pathres.rs L1382 测试）。

## `crates/hir-def/src/module/clocking.rs`（153 行）

**角色**：clocking block 声明降级 + scope-only owner 的 body 出口。

**关键结构与不变量**：
- `ClockingBlockKind`（L23：Regular/Default/Global）；`ClockingBlockDef { name, kind, event: EventExprId, signals }`（L31）；`ClockingSignal { name, dir, name_range, source }`（L41-46）——dir 二值化：有 output 关键字→Output，否则 Input（L120-122，**无 Inout clocking 口**）。
- `DefaultClockingRef`（L51）：default clocking 引用存进 body 单槽（L85-87），source 记录在 `default_clocking_src`。
- `lower_clocking_owner`（L124-153）：`debug_assert_eq!(owner.kind(db), OwnerKind::ClockingBlock)`（L129）；AST 反解失败返回空 Lowered（L133-139）；该 owner 的 body 只含一个 clocking def（scope-only owner 模式）。

**公开 API**：上述类型 + `lower_clocking_declaration`（L56）/`lower_default_clocking_reference`（L80）/`lower_clocking_owner`（L124）。

**依赖/被依赖**：依赖 body/db/expr::timing_control/lower/port.rs（PortDirection）/owner/source_map/syntax；被 body.rs、container.rs、scope.rs、symbol.rs、ide 的 document_symbols/render.rs 消费。

**改动影响面**：`owner_region_tree`（region_tree.rs L304-308）把 ClockingBlock 重定向到父 owner；scope.rs `build_clocking_block_scope`（L312）与 pathres `descend_scope`（pathres.rs L340）依赖其 signals 结构。

**集成点**：ClockingSignalId(u32)（L49）是 DefOriginLoc::ClockingSignal 的索引；name_range 直接给 IDE hover 用。

## `crates/hir-def/src/module/continuous_assign.rs`（44 行）

**角色**：`assign` 连续赋值语句降级。

**关键结构与不变量**：`ContAssign { strength, delay, assigns }`（L15-19）；不变量：delay 只接受 DelayControl 形态，其它 TimingControl（事件控制等）静默丢弃为 None（L29-35）。

**公开 API**：`ContAssignId`（L21）、`LoweringCtx<Store: ModuleItemStore>::lower_continuous_assign`（L24）。

**依赖/被依赖**：依赖 expr.rs/timing_control/ty.rs/lower.rs；仅被 body.rs 引用（BodyItem 通道）。

**改动影响面**：极小；strength/delay 数据留给 hir-ty 与后续仿真语义。

**集成点**：与 defparam.rs 同为 ModuleItemStore 泛型降级器最小样例。

## `crates/hir-def/src/module/defparam.rs`（39 行）

**角色**：`defparam` 语句降级。

**关键结构与不变量**：`DefParam { assignments }`（L11）/`DefParamAssignment { target, value }`（L16-19）；target 经 `lower_expr_opt`（L29）——defparam 目标是层次路径表达式，缺失时为占位 expr。

**公开 API**：`DefParamId`（L21）、`lower_defparam`（L24）。

**依赖/被依赖**：依赖 expr.rs/lower.rs；仅被 body.rs 引用。

**改动影响面**：defparam 在 generate 域同样可降级（generate.rs L183/L409）。

**集成点**：无外部钩子；纯数据承载。

## `crates/hir-def/src/module/generate.rs`（509 行）

**角色**：generate 域降级——generate region、if/case/loop generate、裸 generate block 的 owner 化降级。

**关键结构与不变量**：
- `generate_block_source_node`（L30-36）：**loop-generate 的 owner 是 loop 节点而非其嵌套 begin/end 块**（parent 是 LoopGenerate 则上提）；`generate_block_name`（L38-43）：label 优先，其次 begin_name。owner.rs L263-265 的 `intrinsic_owner_kind` 与此镜像（GENERATE_BLOCK 父为 LoopGenerate → None）。
- `GenerateBlockKind`（L45-55）：Block 或 Loop{genvar, initial, stop, iteration}——loop 的三个表达式在 owner body 里降级（L222-230）。
- 两套并行的成员降级路径：`generate_block_item_from_branch`（L59，块 owner 内部用）与 `generate_item_from_branch`（L255，模块域直接嵌 generate 用）——if/case 条件表达式都先 `lower_expr`（L83/L98/L276/L291）保证表达式进 arena，分支成员统一 `intern_generate_node`（L250-253，owner_for_node + expect）升级为 GenerateBlockOwner。
- `lower_generate_member`（L127-200）：generate 块内可降级成员的清单（比模块域窄：无端口/无 clocking 声明等）；IfGenerate/CaseGenerate 例外地把产出 items 直接 push 进当前 body 并返回 None（L171-182）。
- `lower_generate_owner`（L456-509）：按 owner 节点 cast 三分派 GenerateBlock/LoopGenerate/SingleMember（L468-481，else 分支 unreachable!）；**SingleMember** 形态对应 owner.rs L237-251 的"unwrapped generate branch 成员提升为合成 generate-block owner"。

**公开 API**：`GenerateRegion`/`GenerateRegionId`（L22/L26）、`GenerateBlockKind`、`generate_block_source_node`/`generate_block_name`（L30/L38，被 owner.rs 复用）、`intern_generate_node`（L250）、`lower_generate_region`（L423）/`lower_direct_generate_region`（L443）/`lower_generate_owner`（L456）。

**依赖/被依赖**：依赖 body/db/expr/lib/lower/module.rs/owner/source_map/syntax；被 body.rs（L573 分派）、owner.rs（generate_block_name）、ide/document_symbols.rs 消费。

**改动影响面**：`generate_block_source_node` 与 owner.rs 的 `intrinsic_owner_kind`/`is_unwrapped_generate_branch`（owner.rs L263/L283）是**同一规则的两侧**，改一处必改另一处，否则 owner 表与降级 body 漂移（enter_body_scope 的断言会炸）。

**集成点**：新增 generate 成员语法支持时在 `lower_generate_member` 与 `lower_generate_region_member`（L320-421）两处同步加分支。

## `crates/hir-def/src/module/specify.rs`（213 行）

**角色**：specify 块降级——路径声明/条件路径/ifnone 路径/pulsestyle/系统时序检查。

**关键结构与不变量**：
- `SpecifyBlock { items }`（L10）；`SpecifyBlockItem`（L18-22）经 `define_enum_deriving_from!`（utils 宏）：DeclarationId（specparam）|SpecifyItemId 二态。
- `SpecifyItem`（L25-31）五变体；`SpecifyPath { inputs, outputs, edge_expr, delays }`（L36-41）——edge_expr 仅 EdgeSensitivePathSuffix 存在（L184-188）；`TimingCheckArg`（L44-48）：Empty/Event{terminal,condition}/Expr。
- `lower_specify_path`（L175-193）：SimplePathSuffix 无 edge；`lower_name_expr`（L208-212）：Name 节点 cast 失败时降级为 missing expr 占位（保证 spec 路径端点总有 ExprId）。
- specify 块外的同语法成员在 module.rs L490-500 被 report_unsupported（specify 项只属于 specify 块内）。

**公开 API**：上述类型 + `lower_specify_block`（L51）及五个 item 降级方法。

**依赖/被依赖**：依赖 declaration/expr/lib/module.rs；被 body.rs、（图谱另计入 lib）；消费面在 symbol/scope 的 specparam Def 通道。

**改动影响面**：specparam 走 Declaration arena，scope.rs `insert_specify_declarators`（L80-99）枚举 specify 块内声明。

**集成点**：TimingCheckArg 的 Event 形态保留 condition 表达式，供后续时序检查语义使用。

## `crates/hir-def/src/symbol.rs`（607 行）

**角色**：语义定义的统一身份层——`DefOrigin`（Salsa 实习的位置枚举）、`DefKind`、`ScopeData`（三命名空间词法作用域）与 `Resolution<T>`（三值解析结果）。

**关键结构与不变量**：
- `DefOrigin`（L33-36，`#[salsa::interned]`）包裹 `DefOriginLoc`（L40-64）22 变体——注释 L30-32 钉版：origins 实习进数据库而非进程级池，**身份 scoped to database**。变体分两形：owner 直持（Module/Block/GenerateBlock/Subroutine）与 `OwnerRef<Id>`（容器+arena 索引）与 `InFile<Id>`（config/library/udp）。
- `trivial_kind!`（L103-121）：除 Module/Decl 外每个变体的 DefKind 可不查库推导；`container_id`（L124-155）：任意 origin → 所属 scope owner（Module 取 parent 即 file owner，L126）。
- `DefKind`（L207-251）43 变体；`symbol_kind()`（L265-297）把细粒度 kind 折叠成 LSP SymbolKind 用的粗类；`is_instantiable_def`（L254）；`from_syntax_kind`（L299）/`name_context`（L323：模块类/typedef→Type，property/sequence→Assertion，其余 Value）。
- `ScopeData`（L361-366）：types/values/assertions 三张 `FxHashMap<Ident, SmallVec<[DefId;1]>>` + imports。注释 L357-359 钉版核心不变量：**多个 origin 合并进同一 DefId 后不算 Ambiguous，只有多个不同 DefId 才 Ambiguous**（scope.rs 测试 L721 验证）。
- `Resolution<T>`（L388-473）：Unresolved/Unique/Ambiguous；`from_candidates`（L459）去重后 0/1/N 分箱；`and_then`（L441-449）**禁止子代解析为歧义父代消歧**（测试 L599）。
- `ScopeData::lookup`（L526-538）：Type/Value/Assertion 各查各表不回退（scope.rs 测试 L1623 验证 value 不落到 type 桶）；`lookup_listing`（L540）跨 type+value 合并（补全用）；`iter_listing`（L551）；`typedef_names`（L569）。

**公开 API**：DefOrigin 及 21 个 `as_*` cast（L159-204）、DefKind 全方法、ScopeKind（L340）、ScopeData 全部 insert/lookup、Import（L369）、NameContext（L378）、Resolution 全方法。

**依赖/被依赖**：依赖 crate 内 15 个模块（assertion/checker/container/covergroup/db/def_id/expr/file 三子/module 四子/owner/stmt/subroutine/typedef）+ syntax/utils；被 35 个文件消费——crate 内 9 个 + hir-semantics×3 + hir-ty×5 + ide×17（completion 五引擎、rename、references、semantic_tokens 等），是全 crate 被依赖最广的文件之一。

**改动影响面**：DefOriginLoc 加变体需同步 trivial_kind!/impl_from!/container_id 三处宏清单与 DefKind；Resolution 语义是 pathres/diagnostics/hir-ty infer 的共同前提。

**集成点**：新增 HIR 定义类别的标准流程 = DefOriginLoc 加变体 + DefKind 加 kind + scope.rs 对应 build_* 里插表；`lookup_listing` 是补全引擎（ide/completion/engine/typed_filter.rs 等）的入口。

## `crates/hir-def/src/scope.rs`（1993 行；源码 436 行 + 测试 1556 行）

**角色**：词法作用域构建——per-owner 的 `scope_for` Salsa query、`$unit` 全局作用域，以及十种 OwnerKind 各自的 build 函数。

**关键结构与不变量**：
- `scope_for` query（L41-43，lru=128）：**每个 owner 独立构建独立失效**（doc 注释 L39）；`unit_scope` query（L47-56）：合并全部 file-owner scopes 为显式 `$unit`（resolution 的最后作用域）。
- 五个共用插入器：`insert_body_declarators`（L67）/`insert_specify_declarators`（L80，枚举 specify 块内 specparam）/`insert_body_typedefs`（L101）/`insert_body_statements`（L114——语句 label 与 `StmtKind::Block` 的块名都入 value 表）/`insert_proc_bodies`（L133，过程块 body 的语句再插一遍）。
- `build_file_scope`（L166-224）：module 名入 type 表（L172-175）、package imports、顶层 declarators/typedefs、config/udp/library 声明、checker/covergroup 入 type 表。
- `build_module_scope`（L226-310）：**非 ANSI 端口 label 入 value 表**（L231-235）、modports、clocking/checker/covergroup/property/sequence（property/sequence 入 assertion 表 L272-283）、instances、generate region 里的 block 名（L293-306 逐层展开）。
- `build_clocking_block_scope`（L312）/`build_checker_scope`（L326，checker 端口按枚举序号造 CheckerPortId）/`build_covergroup_scope`（L346，coverpoint+cross）/`build_generate_block_scope`（L364，块自身名字+imports+子块）/`build_subroutine_scope`（L391，端口+局部）/`build_block_scope`（L407）/ProceduralBlock 内联（L424-431）。
- `build_owner_scope`（L416-436）：OwnerKind→build 函数的唯一分派表；AnonymousProgram 复用 module 版（L420）。
- `ScopeData::non_ansi_port_decl_id_by_name`（L141-155）：value 唯一命中后过滤出 PortDeclId 母体。
- 命名空间注释 L25-30：types=模块/接口/包/程序/typedef；values=nets/vars/params/ports/subroutines/instances/blocks；assertions 预留；层次查找走 pathres 独立通道。

**公开 API**：`scope_for`/`unit_scope`（Salsa tracked）、`set_scope_lru_capacity`（L58）、`build_owner_scope` 及全部 build_*（pub(crate)）、`ScopeData::non_ansi_port_decl_id_by_name`。

**依赖/被依赖**：依赖 crate 内 16 个模块 + base-db/utils/vfs；仅被 db.rs（L98/L101 转发）与 lib.rs 依赖——它是 query 出口，下游一律经 `db.scope(owner)`。

**改动影响面**：新增定义类别的 scope 可见性在此落地（对照测试 L592 `scope_graph_context_lookup_covers_current_scope_shapes` 全景用例）；DefId 稳定性测试（L836 non_ansi_port_def_id_is_stable_when_origins_change、L1721 declaration_def_id_survives_preceding_declaration_insertion）钉死增量编辑不迁移身份的核心承诺。

**集成点**：`ScopeData::insert_*` 族与 symbol.rs 的三命名空间表是新增可见性规则的全部接入面；测试模块（L438-1993，30+ 用例）同时是本 crate 大量降级行为的回归床（default_nettype、streaming、assertion、covergroup、package export 闭包等）。

## `crates/hir-def/src/pathres.rs`（1494 行；源码 511 行 + 测试 983 行）

**角色**：名字/路径解析器——词法作用域链查找、package import 解析、IEEE 1800-2017 §26.3 point-of-reference 规则、多段层次路径下降。

**关键结构与不变量**：
- 头注释 L15-25 钉版路径形状：dot 式层次选择（`a.b`、select）由本解析器处理；`::` package/class 域作用不在其中。
- `resolve_name`（L72）→ `resolve_name_at`（L84，带引用位置）→ `resolve_name_inner`（L142-199）核心循环：沿 `ScopeChain` 逐 scope，**每 scope 内先 lexical 声明、再 named import、后 wildcard import，整个 scope 搜完才进下一层**（注释 L173-175，测试 L865 inner_scope_wildcard_shadows_outer_named_import）；最后查 `$unit`（L190）。
- `NameRef { position, kind }`（L67）+ `RefKind`（L57）：Value/Call。point-of-reference 规则（`AtFilter` L381-401）：普通引用只见引用点之前的声明与显式导入（`filter_named` L393）；**Call 引用搜索到 scope 末尾**（IEEE 26.3，测试 L1308 call_reference_searches_to_scope_end）；wildcard 导入对一切引用按位置过滤（`filter_wildcard` L398）。
- `before_reference`（L113-126）：跨文件恒可见（L118-120）；同文件用 AstIdMap 的 preorder 序数比较（L121-125）。
- `resolve_path_at`（L270-292）：首段 `resolve_name_at`，未解出且是多段 value 路径时回落 `resolve_top_level_module_root`（L294-317，**编译单元顶层模块可作显式层次根**，单段名不回落、嵌套模块不外泄，测试 L1330/L1355）；中间段一律用 Value 语境、末段用原语境（L284）。
- `descend_scope`（L332-350）：Module/Interface/Program/Package→owner 本身；ClockingBlock/Checker/Covergroup/Block/GenerateBlock→origin owner；**Instance→递归** `instance_target_def_id`（L356-371，经 Instantiation.module_name 查 unit_index 的 instantiable_ids_in）。
- `resolve_child_name`（L319）走 `Resolution::and_then`——歧义父代不被子代消歧（symbol.rs 不变量，测试 L687）。
- `ImportCollector`（L404-435）+ `resolve_scope_imports`（L437-479）：named 与 wildcard 两轮，均经 design_map 的 `resolve_import`（package export 传递闭包在 design_map 侧，测试 L941/L1040 环状导入定点）。
- `resolve_wildcard_at`（L484-511）：只走 wildcard 通道并返回命中 scope（诊断用）。
- `ResolutionTrace`（L44）+ `resolve_name_with_trace`（L99）：四阶段（Lexical/NamedImport/WildcardImport/Unit）决策留痕，常规路径零分配（L96-98 注释）。

**公开 API**：`resolve_name`/`resolve_name_at`/`resolve_name_with_trace`、`ResolvedScopes` + `resolve_in_resolved_scopes(_at)`（L202/L214/L225，预解析链复用）、`resolve_path`/`resolve_path_at`、`resolve_child_name`、`descend_scope`、`instance_target_def_id`、NameRef/RefKind/ResolutionPhase/ResolutionTrace。

**依赖/被依赖**：依赖 container（ScopeChain/InFile）/db/def_id/instantiation/owner/symbol/unit_index（经 db）+ base-db/utils/vfs；被 9 个文件消费——diagnostics/lib/scope + hir-semantics×2 + hir-ty×2 + ide×2（semantic_index/build、semantic_tokens）。

**改动影响面**：IEEE 26.3 的三条 point 规则与 scope 搜索顺序是 20+ 个测试的钉版行为；`descend_scope` 的 kind 清单与 DefKind::is_instantiable_def、unit_index 的 instantiable_ids_in 三方联动。

**集成点**：`resolve_name_with_trace` 是写"名字未解析"诊断的官方缝隙；`ResolvedScopes` 允许 IDE 预解析作用域链后批量查询（semantic_index/build.rs 的用法）。

## `crates/hir-def/src/owner.rs`（769 行；源码 436 行 + 测试 333 行）

**角色**：canonical owner 身份体系——`OwnerId`（Salsa 实习的 (file, ast_id, kind) 三元组）、per-file `OwnerTable` 的构建，及"哪些语法节点开 owner"的规则中心。

**关键结构与不变量**：
- `OwnerKind`（L37-48）10 变体。`OwnerId`（L50-58，`#[salsa::interned(unsafe(no_lifetime), revisions = usize::MAX)]`）——头注释 L1-15 钉版设计：身份=不可变源锚点；parentage/name 是 revision 数据住在 OwnerTable，**不进身份**；`unsafe(no_lifetime)` + `revisions = usize::MAX` 使实习字段跨修订不可变，可作 query key。同节点可开多 owner（unwrapped generate branch 内的 subroutine），靠 kind 区分而非引入新序数体系。
- `OwnerId::parent/name/module_kind`（L62-76）：每次经 OwnerTable 查询（非身份字段）；Ord 按 Salsa AsId（L85-89）。
- `OwnerTable`（L105-109）：`owners: Vec<OwnerData>` + by_id + `by_source: (SourceAstId, OwnerKind) → OwnerId`。`file_owner()`（L125）恒为首项（builder L150 先入）；`owners_of_kind`（L130）保持源序。
- `OwnerTableBuilder`（L139-198）：栈式构建。`enter`（L167-186）对 `owner_kinds_of` 的每个 kind 建一条 OwnerData 入栈（同一节点两 kind = 栈两层，L184）；`leave`（L188）按 kinds 数弹出；`finish`（L194）debug_assert 栈只剩 file owner。双 debug_assert（L181-183）保证无重复身份/源键。
- `owner_table` query（L200-226）：elem_preorder 全树遍历；root 必须是 COMPILATION_UNIT 或 LIBRARY_MAP（L206-209 assert）。
- `owner_kinds_of`（L237-251）+ `intrinsic_owner_kind`（L253-281）+ `is_unwrapped_generate_branch`（L283-301）：三函数合成核心规则——①GENERATE_BLOCK 若父是 LoopGenerate 则不开 owner（L263-265，loop 拥有块）；②if/case-generate 分支的直接成员（未被 GenerateBlock/LoopGenerate/Module 隔断）提升为 GenerateBlock owner，若成员本身有 intrinsic owner（如 function）则双 owner 同源异 kind（L242-248）。
- `owner_name`（L310-336）：每 kind 的取名规则（GenerateBlock 复用 generate.rs 的 `generate_block_name`，L319-323）；`owner_module_kind`（L303）。
- 测试 L338-769 共 12 个：owner 表枚举/父链/名字（L460）、body 编辑下 id 稳定（L506）、subroutine body 重降级（L522）、兄弟追加保序（L542）、Block 语句持 canonical owner（L575）、嵌套块共享单 body 且 scope 独立（L607）、item_tree 排除源 range（L744）等——这些是 crate 增量语义的权威规格。

**公开 API**：OwnerKind/OwnerId（含三查询方法与 Ord）、OwnerData/OwnerTable 全部查询、`owner_kinds_of`/`intrinsic_owner_kind`/`is_unwrapped_generate_branch`（pub(crate)）、`set_owner_table_lru_capacity`（L228）。

**依赖/被依赖**：依赖 base-db×5/ast_id_map/db/module.rs（ModuleKind 与 generate_block_name）/syntax/vfs/utils；被 54 个文件消费（crate 全域 + hir-semantics×4 + hir-ty×5 + ide×16）——**全 crate 被依赖之最**。

**改动影响面**：`owner_kinds_of` 规则变更必须与 generate.rs 的 `generate_block_source_node`（L30）同步；OwnerId 实习参数改动影响所有以它为 key 的 query（body_with_source_map/scope_for/owner_region_tree）。

**集成点**：新语法域引入新 owner 类型 = OwnerKind 加变体 + intrinsic_owner_kind 加映射 + body.rs 分派表加行 + scope.rs build 函数；`OwnerTable::owner_by_ast` 是降级器把 AST 节点换 owner 的唯一通道（lower.rs L234）。

## `crates/hir-def/src/region_tree.rs`（523 行；源码 477 行 + 测试 46 行）

**角色**：编辑器折叠区树——SV 注释区标记（`// region`/`// endregion`）与"连续同描述声明"伪区的 per-owner 构建。

**关键结构与不变量**：
- `RegionKind`（L22）：`Region{name, begin_range}`（显式标记）或 `PseudoRegion{description}`（注释+声明聚合）；`RegionNode`（L34）：range/kind/children/parent。
- `RegionTree::find`（L69-83）：`find_in_node`（L85-96）用 `partition_point` 二分——**依赖 normalize（L98-121）后子节点按 start 升序、同 start 按 end 降序**（嵌套在前）；测试 L489/L502 钉版"查找与插入序无关"。
- `RegionTreeBuilder`（L143-297）：三状态（tree/stack/pseudo_region=(cnt,range,description)）。`stage`（L174-189）：end token 的 trivia 先处理（`// endregion` 贴在收尾 token 上必须先关自己的区，否则被下面的强制收拢吞掉，L176-178 注释），随后把栈上全部 open region 强制收拢到 root 末 token——**树在 owner 范围结束时必然闭合**。
- `handle_pseudo_region`（L214-274）：仅 DataDeclaration/NetDeclaration/ParameterDeclaration/ImplicitAnsiPort/PortDeclaration 五类节点可聚合（L219-229 match_ast）；聚合条件=注释描述相同且声明间恰一个 EOL（L235-247）；`finish_pseudo_region`（L276-284）要求 cnt>1（**单个带注释声明不成区**）。
- `owner_region_tree` query（L302-320，lru=512）：**scope-only owner（Checker/Covergroup/ClockingBlock）重定向到父 body owner**（L304-309）；AST 反解失败返回空树。
- `collect_owner_regions`（L326-414）：per-OwnerKind 决定遍历哪些子节点（Module：header 参数+端口表+成员 L339-365；GenerateBlock：块成员或 loop 块成员 L374-386；scope-only 三 kind：全部直接子节点 L406-412）。
- `RegionTreeIterator`（L425-454，WalkEvent Enter/Leave 先序）与 `RegionParent`（L457-476，祖先链迭代）。

**公开 API**：RegionTree 全查询（root_count/nodes/walk/find）、RegionNode::name/focus_range、RegionParent、`owner_region_tree`（pub(crate)，经 db.rs L82 转发）、`set_region_tree_lru_capacity`（L322）。

**依赖/被依赖**：依赖 base-db/db/owner/syntax（trivia API）/utils；被 lib.rs、ide 的 document_symbols/folding_ranges/render.rs 消费。

**改动影响面**：normalize 排序被 find 的二分前提依赖；pseudo region 的五类节点清单变化直接改变 IDE 折叠呈现。

**集成点**：RegionParent/RegionTreeIterator 是 IDE 折叠与 outline 的两个遍历入口；新 owner kind 需在 collect_owner_regions 加遍历分支。

## `crates/hir-def/src/unit_index.rs`（199 行）

**角色**：文件级设计单元索引——module/interface/program/package/checker/covergroup 头的名字→owner 反查，供例化与层次解析。

**关键结构与不变量**：
- `UnitKind`（L24-28）+ 判定（L30-42）：is_module（Module 且 is_instantiable，即排除 Package）、is_package、is_instantiable（module 或 checker/covergroup）。
- `UnitData { owner, kind, parent, top_level }`（L45-50）：top_level = parent 是 file owner（L149/L164）——**只有编译单元直系声明可作层次根**。
- `UnitIndex`（L58-62）：units + by_name（SmallVec 容纳重名）+ module_names（排序去重 L120-133）。头注释 L52-56 钉版：**刻意不建词法作用域、不降级 body、不分配 DefId**；重复声明保留为 `Resolution::Ambiguous`。
- `instantiable_ids_in`（L80-91）：**先查 scope 局部 checker/covergroup，再查编译单元级可例化单元**（IEEE 层次优先级）；`top_level_module_ids`（L70）只回 top_level 模块。
- `unit_index` query（L110-136，lru=128）：遍历 `db.files()` 全部文件的 item_tree module_headers + owner_table 的 Checker/Covergroup owner；`insert_unit`（L169-183）空名跳过。
- 内嵌测试 `empty_index_has_no_targets`（L192-198）。

**公开 API**：`module_ids`（L64）、`top_level_module_ids`（L70）、`package_ids`（L74）、`instantiable_ids_in`（L80）、`module_names`（L93）、`unit_index`（L110）、`set_lru_capacity`（L185）。

**依赖/被依赖**：依赖 db/item_tree/module.rs（ModuleKind）/owner/symbol（Resolution）；被 db.rs（L105 转发）与 lib.rs 依赖；真正消费方经 db：pathres（L311/L365）、scope 测试、diagnostics。

**改动影响面**：top_level 判定与 pathres 的 `resolve_top_level_module_root`（pathres.rs L294）直接耦合；module_names 是补全模块名的数据源。

**集成点**：新可例化单元类别（如未来 UDP 例化）在此扩 UnitKind；`Resolution` 返回值让调用方自决歧义处理。

---

### 单元内文件协作速览

- **降级主干**：`lib.rs`（alloc 辅助）→ `lower.rs`（ctx/store）→ `module.rs`（成员分派）→ 各语法域文件（port/generate/instantiation/…）→ `source_map.rs`（Lowered 出口）；`owner.rs`/`source_projection.rs` 在旁提供身份与投影，`body.rs`（不在本单元）按 OwnerKind 分派调用 `lower_module_owner`/`lower_generate_owner`/`lower_clocking_owner`（body.rs L566/L573/L586）。
- **解析主干**：`owner.rs`（scope 链的图基础）→ `scope.rs`（per-owner ScopeData）→ `symbol.rs`（DefId/Resolution 语义）→ `pathres.rs`（查找算法）→ `unit_index.rs`（跨文件单元名）。
- **三个全部经 db.rs 暴露的 LRU query 群**：owner_table/source_projection/unit_index/default_nettype_directives/owner_region_tree/scope_for/unit_scope（db.rs L50-153 统一注册容量调节）。
