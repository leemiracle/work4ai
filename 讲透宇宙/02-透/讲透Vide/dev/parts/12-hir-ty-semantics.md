# 12-hir-ty-semantics 精读手册

> 模块定位：本单元是 vide（SystemVerilog LSP，Salsa RootDb + VFS + slang 解析 + HIR 三层）HIR 层之上的两个平行消费 crate。**hir-ty** 把 `hir-def` 的定义/表达式解释为语义类型 `Ty`（Salsa 查询推断、成员枚举、兼容性判定、源码级类型渲染），对外只暴露窄接口 `TypeSystem`；**hir-semantics** 是 syntax→HIR 语义适配器，把语法节点/offset 映射为 `hir-def` 的 `DefId`/`OwnerId`/arena id，是 IDE 几乎所有交互功能（hover、goto、completion、references、rename、semantic tokens）的统一入口。二者互不依赖（hir-semantics/src/lib.rs L5-6 明言 "It intentionally does not depend on hir-ty"），类型感知的 IDE 功能由 ide crate 自行组合两者。

---

## `crates/hir-semantics/Cargo.toml`（18 行）

**作用**：声明 `hir-semantics` crate（"Syntax-to-HIR semantic adapter"）。
**关键字段**：deps = hir-def + preproc-expand（HirFileId/宏展开）+ syntax（AST/遍历）+ vfs + utils + itertools + rustc-hash（L7-14）；dev-deps = base-db + triomphe（L16-18，仅供 `preproc_integration_tests` 搭测试 db）。**刻意无 salsa、无 hir-ty**——本 crate 不定义查询，也不做类型。
**改动连带**：新增依赖若引入 salsa 会被 lib.rs 文档约束（"not a stable, high-level HIR facade"）打脸；给 dev 加依赖只影响测试编译。

## `crates/hir-semantics/src/lib.rs`（17 行）

**角色**：crate 门面，只有模块声明与架构约束文档。
**关键内容**：`pub mod semantics`（L14）+ `#[cfg(test)] mod preproc_integration_tests`（L16-17）。doc comment（L1-12）钉死三条边界：① 映射 syntax node/source range → hir-def 的定义与容器 id，用 preproc-expand 的 file/expansion id；② 刻意不依赖 hir-ty，类型感知 IDE 功能在 ide crate 里组合本适配器与类型层；③ 编译器实现层禁止反向依赖本适配器。
**改动影响面**：任何新公开 API 都应挂到 `semantics` 模块；违反"编译器层不得依赖本 crate"会破坏分层。

## `crates/hir-semantics/src/preproc_integration_tests.rs`（184 行）

**角色**：集成测试——验证语义层与宏展开（preproc-expand）的 source-map 往返正确性。
**覆盖行为**（4 个测试，内联 SV 源码 + 真实 salsa db）：
- `macro_generated_declaration_hir_range_resolves_to_diagnostic_target`（L113）：`` `MAKE_DECL`` 宏生成的声明经 `body.source_range` 投影后，`diagnostic_target_for_range` 指回 `Origin::MacroBody`（诊断跳宏体）。
- `diagnostic_target_for_unbacked_predefine_expansion_fails_closed`（L136）：`+define` 注入的展开无宏体可指，断言 `target.is_none()` 但 `covered=true`（fail closed 语义）。
- `macro_expanded_module_keeps_macro_hir_file_id`（L163）：宏展开出的 module owner 的 `owner.file()` 是 `HirFileId::Macro`，且 `source_file_id` 归一到宿主 FileId。
- `semantics_accepts_hir_def_only_database`（L179）：`Semantics::new` 只要求 `HirDefDb`（无需完整 RootDb），`parse_file` 即可用。
**跑法**：`cargo test -p hir-semantics`。测试 db 装配模式（L31-70 五个 salsa trait impl + FileLoader + Deref；L76-101 组 SourceRoot/ProjectConfig/DiagnosticsConfig）是本仓集成测试的通用脚手架。

## `crates/hir-semantics/src/semantics.rs`（138 行）

**角色**：适配器主入口——`Semantics<'db, DB>` 门面 + `ParsedFile` + AST 定位工具。
**关键结构与不变量**：
- `Semantics<DB>`（L28-31）：持具体 db 引用 + `SemanticsImpl`，通过 `Deref`（L63-69）把泛型壳降到 `dyn HirDefDb` 实现——IDE 只构造一次 `Semantics::new(&db)`（L57-60）即拿到全部方法。
- `ParsedFile`（L33-54）：`HirFileId + SyntaxTree` 对，`root()`/`compilation_unit()` 供 AST 遍历；不变量：file_id 经 `FileId::into()`（L101）升级，宏文件与实文件统一。
- `SemanticsImpl`（L91-108）：`parse_file`（L100）走 `db.parse` salsa 查询（带缓存）；`container_for_node`（L105）委托 `source_to_def::find_container`。
**公开 API**：`find_node_at_offset<N: AstNode>`（L72-88）——token/节点命中后沿祖先链 `kmerge_by` 按 range 最小优先 `N::cast`（offset 命中最内层目标节点）；`module_to_def`/`block_to_def`/`subroutine_to_def`（L111-129）；`expr_to_def(OwnerRef<ExprId>) -> Resolution<DefId>`（L131）；`name_to_def(OwnerRef<Ident>)`（L135，固定 Value 上下文）。
**依赖/被依赖**：依赖 hir-def（container/db/def_id/expr/owner/symbol）、preproc-expand file、syntax、utils text_edit、vfs。**被依赖**：ide crate 30+ 文件（hover/goto_definition/goto_declaration/references/rename/document_highlight/completion 全家/signature_help/semantic_tokens/semantic_index/formatting/code_lens/selection_ranges/verilog_2005/render…），是 IDE 事实上的标准后端。
**改动影响面**：`find_node_at_offset` 的最内层优先语义、`Deref` 结构、`Semantics::new` 签名（泛型 DB）任何变化都会波及全部 IDE 功能；`pub use source_to_def::is_generate_branch_member`（L26）被 ide semantic_index build 消费，改名即断。
**集成点**：新 IDE 功能的标准姿势 = `Semantics::new(db)` + `parse_file` + `find_node_at_offset` + `nameres_ident`/`resolve_expr` 系列；要新加"AST→HIR id"通道就往 `SemanticsImpl` 加方法并保持薄委托。

## `crates/hir-semantics/src/semantics/hir_to_def.rs`（114 行）

**角色**：HIR 表达式/名字 → `Resolution<DefId>` 的解析桥（值上下文）。
**关键结构与不变量**：
- `expr_to_def`（L14-50）：核心不变量 = **引用点感知解析**（IEEE 1800-2017 26.3）——表达式在其源码位置处解析，"后置声明不遮蔽 import"；`Expr::Field` 先把整条链当 path 解析（`resolve_expr_path` L26），失败再回退"receiver 解析 + `resolve_child_name`"两步法（L28-30）；`ElementSelect` 透传到 receiver（L33-36）。
- `expr_reference`（L55-66）：从 source map 取 `expr_srcs.hir_to_src` 位置；**扫描整个 body arena 判断该 expr 是否恰为某 `Expr::Call` 的 callee**（L58-63），是则 `RefKind::Call`（callee 解析要搜索到作用域末尾），否则 `RefKind::Value`。
- `expr_path`（L98-109）：把 `Ident`/`Field`/`ElementSelect` 链折叠回 `Vec<Ident>` path，无法折叠返回 None。
**公开 API**（pub(super)）：`expr_to_def`、`name_to_def`（L68，无位置版）、`name_to_def_at`（L76，带 NameRef）。
**依赖/被依赖**：依赖 hir-def pathres 全家（NameRef/RefKind/resolve_child_name/resolve_name/resolve_name_at/resolve_path_at）。被 semantics.rs 与 pathres.rs（本 crate）消费。
**改动影响面**：Field 的"path 优先、child 回退"顺序决定层级引用（`a.b.c`）与类静态成员两种写法谁赢；改掉会改变 goto/references 结果。26.3 引用点语义同时被 hir-ty/src/infer.rs 复刻（那边注释同样引用 26.3），两处必须同步演进。
**集成点**：需要"点一个表达式拿到它指向的定义"（hover/定义跳转）都走 `expr_to_def`；调用解析特殊性（RefKind::Call）由本文件自动处理，调用方无需感知。

## `crates/hir-semantics/src/semantics/pathres.rs`（149 行）

**角色**：token 级名字解析入口——把 offset 处的 ident token 解析为 `Resolution<DefId>`，含语义索引专用的性能通道。
**关键结构与不变量**（全部挂在 `impl SemanticsImpl`）：
- `nameres_ident`（L20-37）：完整链 = `lower_ident_opt` 降 token → `find_container` 找容器 → `token_reference` 算引用点 → `name_to_def_at`。
- `nameres_ident_in`（L44-61）：调用方自带容器（语义索引建索引时边走树边记容器，免得每 token 重走祖先链），文档钉死"结果与 `nameres_ident` 一致"。
- `nameres_ident_in_scopes`（L68-79）：直接查**已解析好的 scope 链**（`ResolvedScopes`），绕开 per-token 的 salsa `scope_for` 查询——注释 L64-67 说明动机：那些查询的 memo 在索引构建期间会对每个中间查询做 revalidate，是热点。
- `nameres_ident_in_scopes_at`（L84-99）：token 版三合一（自算 reference）。
- `token_reference`（L132-149，自由函数 pub）：**结构化判别**——token 的 parent 是 `ast::Expression` 才算引用（声明名在 declarator 里，拿到 None→按无位置解析）；沿祖先找最近 `InvocationExpression`，若本表达式恰为其 `left()` 则 `RefKind::Call`。
**依赖/被依赖**：依赖 hir-def pathres（ResolvedScopes/resolve_in_resolved_scopes_at）、syntax。被 semantics.rs 转发；消费方为 ide 的 semantic_index/build.rs（三条 nameres 通道的选择就在那里做）。
**改动影响面**：三条通道"结果恒等"的契约（L39-44、L63-67 doc）是语义索引与交互式查询一致性的根基；改 `token_reference` 的 Call 判定会同时改变函数调用与同值变量的引用着色/补全。
**集成点**：批量建索引用 `nameres_ident_in_scopes(_at)`（性能），单点交互（光标处）用 `nameres_ident`/`nameres_ident_in`——这是二次开发选通道的明确分界。

## `crates/hir-semantics/src/semantics/resolver.rs`（86 行）

**角色**：AST 实例化节点 → HIR arena id 的反查（模块实例/实例化/端口连接/表达式）。
**关键结构与不变量**：
- 公共模式（`resolve_instance` L25-39 / `resolve_instantiation` L41-55 / `resolve_port_connection` L57-71）：① `find_container` 找 owner；② **守卫 `owner.kind(db) == OwnerKind::Module`**，非 module 容器一律返回 None（L32-34 等）——实例化只存在于 module 体内是硬约束；③ `source_ast_id`（L15-22，`db.parse` + `ast_id_map().id_of_node_in_tree`）拿源侧 id；④ source map `src_to_hir` 反查 arena id，包成 `OwnerRef`。
- `resolve_expr`（L73-85）：无 Module 守卫，任意容器内表达式均可（`container_id.source_map(db).expr_from_source`）。
**公开 API**：见上四个方法，返回 `Option<OwnerRef<InstanceId/InstantiationId/PortConnId/ExprId>>`。
**依赖/被依赖**：依赖 hir-def module::instantiation、ast_id_map、preproc-expand file。仅被本 crate semantics.rs 的 Deref 间接暴露；消费者在 ide（层级实例的 goto/rename、端口连接高亮）。
**改动影响面**：Module-kind 守卫放宽（如 checker 内实例化）需同步 hir-def lowering；`source_ast_id` 的"parse 后 id_of_node_in_tree"要求传入 node 必须来自同一棵 parse 树，换树会静默失配。
**集成点**：处理 `foo u_inst(.clk(clk))` 这类语法时，`resolve_instantiation` 拿 `InstantiationId`、`resolve_port_connection` 拿 `PortConnId`，配合 hir-def 的 instantiation 数据可做端口名补全/连接检查。

## `crates/hir-semantics/src/semantics/source_to_def.rs`（152 行）

**角色**：AST 节点 → owner 容器 `OwnerId` 的分派核心（"这个语法节点属于哪个 HIR owner"）。
**关键结构与不变量**：
- `owner_for_node`（L22-30）：`db.ast_id_map(file_id).owner_by_ast(ast_id, kind)`——所有转换最终落到 owner_table 查表，本文件零自算。
- `container_to_def`（L75-114）：**容器判定按序 cast，顺序即优先级**：CompilationUnit（→file_owner，L80-82）→ ModuleDeclaration → AnonymousProgram → CheckerDeclaration → CovergroupDeclaration → ClockingDeclaration → BlockStatement → ProceduralBlock → FunctionDeclaration → GenerateBlock/LoopGenerate（L107-109，`generate_owner_node` L56-64 把"LoopGenerate 直接包裸 GenerateBlock"提升为父 LoopGenerate）→ Member（当且仅当 `is_generate_branch_member`）。命中即止。
- `is_generate_branch_member`（L120-141，**pub 从 crate 根 re-export**）：单成员 generate 分支判定——沿祖先先遇 IfGenerate/CaseGenerate 则 true；先遇 GenerateBlock/GenerateRegion/Module/Block/Checker/Covergroup/Clocking 任一更强容器则 false。注释 L117-119 钉死：ide semantic_index build 镜像同一分派、**必须复用此谓词不得重实现**。
- `find_container`（L143-152）：`SyntaxAncestors` 从 node 之上（skip(1)）第一个可映射祖先；兜底 file_owner；`expect` 断言"每个语法文件必有 canonical owner"（panic 是设计选择：损坏输入也该有文件级 owner）。
**公开 API**：pub(super) 的 `module_to_def`/`block_to_def`/`subroutine_to_def`/`find_container`；pub 的 `is_generate_branch_member`。
**依赖/被依赖**：依赖 hir-def ast_id_map/container/owner(OwnerKind)、preproc-expand file、syntax。被 semantics.rs（门面）、pathres.rs、resolver.rs（crate 内）消费；`is_generate_branch_member` 被 ide semantic_index/build.rs 消费。
**改动影响面**：新增 owner 种类（如未来 class 独立 owner）必须同时改 `container_to_def` 分派序与 ide semantic_index 的镜像分派；`find_container` 的 expect 意味着 owner_table 必须始终能给出 file_owner，动 hir-def owner_table 时要保证这点。
**集成点**：任何"从语法位置定位 HIR 上下文"的功能都间接经过这里；新容器类型在此注册一次即对全 IDE 生效。

---

## `crates/hir-ty/Cargo.toml`（18 行）

**作用**：声明 `hir-ty` crate（语义类型、推断与显示）。
**关键字段**：deps = base-db + hir-def + salsa + syntax + utils + vfs + rustc-hash + smol_str + triomphe（L7-15）；dev-deps = preproc-expand（L17-18，测试需要宏展开 db）。与 hir-semantics 相反：这里**有 salsa**（定义推断查询），**无 itertools/preproc-expand（编译期）**。
**改动连带**：加编译期依赖会扩 crate 编译面；`salsa` 版本随 workspace。

## `crates/hir-ty/src/lib.rs`（16 行）

**角色**：crate 门面 + 分层契约文档。
**关键内容**：私有模块 compatibility/infer/members/ty/type_system，公开模块 db/display（L8-14）；`pub use type_system::{Compatibility, Member, Type, TypeDiagnostic, TypeSystem};`（L16）——**crate 的全部稳定面就是这 5 个类型**（外加 db/display 两模块）。doc（L1-6）两条硬约束：① 本 crate 对 hir-def 的 DefKind 匹配是穷尽的，**新增定义种类会强制类型层分类**（编译器驱动）；② 禁止依赖语义适配器（hir-semantics）与 IDE 功能。
**改动影响面**：新公开符号应先问"是否属于稳定类型接口"；违反依赖方向（引 hir-semantics/ide）即破坏分层。
**集成点**：外部消费统一从 crate 根 import 这 5 个类型 + `db::TyDb` + `display::HirDisplay`。

## `crates/hir-ty/src/ty.rs`（64 行）

**角色**：语义类型的私有表示——crate 内部通货，外界不可见。
**关键结构与不变量**：
- `BuiltinTy`（L14-16，仅 `Data { id: BuiltinDataTyId, container: OwnerId }`）：内建数据类型句柄 + **承载 container**（维度常量折叠需要在哪个 owner 里求值，见 compatibility.rs L89-93）。
- `Ty`（L19-39，19 个变体）：`Unknown`（温和失败）/`Error`（带诊断的失败）/`Void`/`Builtin`/`Struct(OwnerRef<StructId>)`/`Enum(DefId)`/`Union(DefId)`（enum/union 用 DefId 因为要经 owner 归属）/`Queue{elem,size}`/`Assoc{key,elem}`（key=Unknown 表示 `[*]` 通配）/`Dynamic`/`Event`/`Chandle`/`Alias{typedef,target}`（**保留 typedef 名字 + 目标双份**，显示用名字、运算走 target）/`Module(OwnerId)`/`Checker`/`Covergroup`/`VirtualInterface{def,modport}`/`GenerateBlock`/`Block`。不变量：`Ty` 无 Hash（L18 只 derive PartialEq/Eq）——它不进 salsa key，只进 query 输出。
- `TyResult`（L42-51）：`{ty, diagnostics}` 对，诊断随类型一起流动。
- `TyMember`（L53-57）与 `TyClass`（L59-64：Integral/Real/String 三值分类，compatibility 的基石）。
**公开 API**：全 pub(crate)——这是封装不变量本身（"Type 的表示保持私有"，type_system.rs L33-34）。
**依赖/被依赖**：依赖 hir-def（aggregate/container/def_id/expr/data_ty/owner/typedef）+ type_system（TypeDiagnostic）。被本 crate 五个兄弟模块消费；被 ide/completion/engine/typed_filter.rs 间接消费（经 Type）。
**改动影响面**：加 `Ty` 变体会使 compatibility.rs（L16-43）、members.rs（L17-42）、infer.rs、display.rs（L104-191）四处 match 全部编译失败——这就是 lib.rs 说的"穷尽匹配强制分类"机制。
**集成点**：无直接外部入口；新类型语义（如 future class 类型）在此加变体，编译器会列出全部需补的 match。

## `crates/hir-ty/src/db.rs`（30 行）

**角色**：Salsa 数据库 trait `TyDb` + 两个便捷推断方法。
**关键结构与不变量**：
- `TyDb: HirDefDb`（L6-7）空 trait——只作 salsa 组合点；`Deref for dyn TyDb → dyn HirDefDb`（L10-16）沿用 hir-def 的组合模式，让 `dyn TyDb` 上直接调用全部 hir-def 查询。
- `infer_expr(&self, expr: OwnerRef<ExprId>) -> Type`（L19-23）：把 `ExprId::into_raw()` 压成 `ExprQueryKey::new(db, cont_id, u32)` 走 `type_of_expr_query`——**ExprId 的 arena 序号即查询键**。
- `infer_path_resolution(&self, res: Resolution<DefId>) -> Type`（L25-29）：`res.unique()` 唯一命中才推断，否则 `Type::unknown()`（多候选/未解析不猜）。
**公开 API**：以上两个 + trait 本身。
**依赖/被依赖**：依赖 hir-def（OwnerRef/HirDefDb/DefId/ExprId/Resolution）与 type_system::Type。**被依赖（图谱入边最重）**：`implements → crates/ide/src/db/root_db.rs`（RootDb 组合链的成员）；imports 入边覆盖本 crate 全部兄弟 + hir-ty 测试 + ide 九个文件（document_symbols/navigation_target/workspace_symbols/semantic_index/references search/semantic_tokens port/code_action convert_port_declarations/db 两个）。
**改动影响面**：`TyDb` trait 或两方法签名变化会迫使 ide/src/db/root_db.rs 的 `#[salsa::db]` 组合重写；所有走 RootDb 的 IDE 功能编译失败。
**集成点**：二次开发在 ide 侧持有 `dyn TyDb`（RootDb 自动满足）即可直接 `db.infer_expr(...)`；更推荐经 `TypeSystem` 门面（见 type_system.rs）。

## `crates/hir-ty/src/type_system.rs`（152 行）

**角色**：类型层唯一稳定门面——`TypeSystem<'db>`（Copy 的瘦包装）封装全部类型查询。
**关键结构与不变量**：
- `TypeDiagnostic`（L25-29）：`TypedefCycle(OwnerRef<TypedefId>)` | `InvalidTypePath(TypePathRecovery)` | `UnsupportedDataType(SyntaxKind)`——类型层仅有的三种诊断。
- `Type(Arc<TyResult>)`（L36）+ `From<TyResult>`（L52-56）：**表示与查询结果全私有**，外部只能 `diagnostics()`（L43-45）与黑盒传递；`ty()` 是 pub(crate)（L47-49）。
- `Member { name: Ident, ty: Type }`（L60-77）：名字只读访问 + `into_name()` 消耗式取名。
- `Compatibility`（L81-85）：Compatible/Incompatible/Unknown 三值——**Unknown 不是失败而是"证据不足"**（类别或位宽未知时）。
- `TypeSystem`（L92-152）九个方法全为一行薄委托：`type_of_expr`（L101→db.infer_expr）、`type_of_resolution`（L105）、`type_of_def`（L109，包 Resolution::Unique）、`type_of_subroutine_return`（L113-120，Function 有返回类型→`normalize_data_ty`，Task/无返回→unknown）、`members`（L122-127，TyMember→Member 装箱）、`compatibility`（L129）、`is_typed_value`（L133）、`display_source`（L137）、`display_declaration`（L141-151：Unknown/Error/Void/Module/GenerateBlock/Block 这六种**不构成声明**返回 None）。
**依赖/被依赖**：imports 覆盖本 crate 全部兄弟（compatibility/db/display/infer/members/ty）+ hir-def（container/def_id/expr/data_ty/owner/subroutine/symbol/typedef）+ syntax SyntaxKind + triomphe Arc。被依赖：本 crate lib.rs（re-export）+ ide/completion/engine/typed_filter.rs。
**改动影响面**：这是 ide typed_filter、extract_variable、completion expr/member 的直接依赖面；方法签名变化直接改 IDE 补全过滤行为。`display_declaration` 的 None 列表决定"哪些类型能生成声明文本"（convert_port_declarations 等 code action 的边界）。
**集成点**：**二次开发消费类型层的标准姿势就是 `TypeSystem::new(&db)`**——所有内部（salsa/HIR arena/normalize/Ty 表示）都被这层挡住。

## `crates/hir-ty/src/members.rs`（136 行）

**角色**：类型 → 成员列表（`TyMember`）的枚举引擎，补全/字段选择的语料源。
**关键结构与不变量**：
- `members_of_ty`（L17-43）按 Ty 变体分派：`Alias` 透明穿透到 target（L19）；`Struct`/`Union`→`struct_members`；`Module`→`module_members`（package 走 `package_exports`，普通 module 走 `scope`，L90-99）；`Checker`/`Covergroup`/`GenerateBlock`/`Block`→各自容器 scope；`VirtualInterface`→剥 modport 取底 module 的成员（L25-29）；**值类型（Builtin/Enum/Queue/Assoc/Dynamic/Event/Chandle/Unknown/Error/Void）一律空成员**（L32-41）。
- `select_member`（L45-51）：按名取一，缺名返回 `Ty::Unknown`（不报错——字段不存在与未知类型同待遇，IDE 友好）。
- `struct_members`（L53-71）：无名成员过滤（`member.name.clone()?`）+ 类型 normalize + **`apply_unpacked_dimensions` 把成员自带维度并入类型**（`logic data[]` 的 `[]` 是成员类型一部分，测试 `struct_member_dimensions_are_part_of_member_type` 钉版）。
- `scope_members`（L121-136）：scope 名字→`Resolution::from_candidates`→逐个 `type_of_path_resolution_impl` 求类型；**结果按名排序 + 去重**（L133-134）——补全列表天然有序。
- `union_members`（L73-78）守卫 `StructKind::Union`（防 DefId 指向非 union 的 struct 数据）。
**公开 API**：pub(crate) `members_of_ty`/`select_member`。
**依赖/被依赖**：依赖 hir-def（aggregate/container/def_id/expr/data_ty/owner/symbol）+ infer（apply_unpacked_dimensions/normalize_data_ty/type_of_path_resolution_impl）+ db/ty。被 type_system.rs（members 门面）与 infer.rs（select_member 用于字段推断）消费。
**改动影响面**：`scope_members` 的排序去重顺序变化直接改补全快照；Alias 穿透若被移除会破坏 typedef 包装类型的字段访问（`payload_t.data` 类代码）。
**集成点**：`select_member` 是 `a.b` 字段类型推断（infer.rs L305）与成员补全共用的唯一入口；新增"有成员的类型"在此注册。

## `crates/hir-ty/src/compatibility.rs`（173 行）

**角色**：类型兼容性三值判定 + packed 位宽常量折叠。
**关键结构与不变量**：
- `type_class`（L16-43）：Alias 穿透；Int/Vector→Integral、Real→Real、String→String；**Enum 视作 Integral**（L25）；Struct/Union/复合容器/命名空间类型全部 None（无类别=不可比）。
- `compatibility`（L45-63）判定序：任一侧无类别→`Unknown`；类别不同→`Incompatible`；同类别非 Integral（Real/String）→`Compatible`；Integral → 比 `packed_bit_width`，等宽 Compatible、不等 Incompatible、任一侧算不出 Unknown。
- `packed_bit_width`（L69-125）：Alias 穿透；Int 按种类查表（`int_kind_width` L127-136：byte 8…longint/time 64）；Vector 维度连乘（空维度=1 位）；Range 宽度=|left-right|+1（L88-91）；Size 直取；Queue/Assoc/Wildcard/Dynamic 维度→None（不定宽）；**全程 checked 运算**（L91/101-102）溢出即 None。
- `eval_const_i128`（L138-173）：维度表达式的常量折叠器——单字面量（`get_single_word`）、一元 +/-、二元 Add/Sub/Mul/Div/Mod/Shift（除零/移位越界守卫 L157-163）、`Cast`/`SignedCast` 透传内层；其余表达式 None。**所以 `logic [1+2:0]` 的宽度推断依赖这套折叠**（测试 `members_and_compatibility_hide_classification_and_width_calculation` L215 钉版）。
**公开 API**：pub(crate) `type_class`/`compatibility`/`is_typed_value`（L65-67 = type_class().is_some()，"是值类型"判定）/`packed_bit_width`。
**依赖/被依赖**：依赖 hir-def（expr BinaryOp/UnaryOp/data_ty Dimension/IntKind、literal）+ db/ty/type_system(Compatibility)。被 type_system.rs 门面转发；经 lib.rs re-export 被 ide/completion/engine/typed_filter.rs 消费。
**改动影响面**：`eval_const_i128` 支持的表达式集决定哪些维度能算宽（参数化宽度 `logic [W-1:0]` 中 W 为 literal 表达式时可判）；compatibility 的 Unknown/Incompatible 边界变化直接改补全过滤与 IDE 提示。
**集成点**：typed completion 的过滤谓词（`is_typed_value` + `compatibility`）即此文件；新比较维度（如 signedness）在 `compatibility` 里加分支即可。

## `crates/hir-ty/src/infer.rs`（513 行）

**角色**：推断引擎本体——DefKind→Ty 的穷尽分派、DataTy 归一化、表达式类型推断（本 crate 最大最核心的逻辑文件）。
**关键结构与不变量**：
- `ExprQueryKey`（L29-35）：`#[salsa::interned(unsafe(no_lifetime), revisions = usize::MAX, debug)]`，字段 owner+local(u32)；**local 就是 ExprId 的 raw 序号**（db.rs L21 压入）。
- `type_of_expr_query`（L55-65，salsa tracked）：从 `body_with_source_map` 的 exprs arena `nth(local)` 取回表达式——**键与 arena 序号的一致性由 `expect`（L62）守卫**，坏键直接 panic 而非静默错类型。
- `type_of_def_origin_query`（L49-53，tracked）：DefOrigin→DefId→`type_of_def_id`，是 `infer_path_resolution` 的落点。
- `type_of_def_id`（L91-223）：**DefKind 穷尽 match**（lib.rs 契约的落点）。要点：非 ANSI 端口先走专用路径（L92）；Module/Package/Program→`Ty::Module`；Interface→`VirtualInterface{modport:None}`（接口名作类型即虚接口）；Port/CheckerPort/Variable/Net/Param/Genvar/Specparam→`type_of_decl_impl`；Typedef→typedef 归一化；**Instance→经 `instance_target_def_id` 找实例化目标再按目标 DefKind 归类**（L122-176，模块实例的类型=目标模块）；Modport→`VirtualInterface{def:容器, modport:Some}`；editor-only DefKind→`unreachable!`（L208-221，编译期防线）。未知化的 DefKind（Subroutine/ClockingBlock/Property/Sequence 等）统一 `Ty::Unknown`（L196-207）。
- `type_of_non_ansi_port`（L224-283）：非 ANSI 端口类型从同源 Variable/Net 声明回填——**Variable/Net 优先（遇到非 Unknown 即返回，L232），Port 结果仅作保底**（`get_or_insert` L233-235）。
- `type_of_expr_impl`（L285-313）：`Ident`→`resolve_name_at`（引用点感知，注释 L289-291 引 IEEE 26.3，与 hir-semantics 侧同源）；`Field`→receiver 递归 + `select_member` + **诊断合并**（`selected.diagnostics.extend(base.diagnostics)` L306）；`ElementSelect`→透传 receiver；`Cast`→按目标 DataTy 归一化；其余表达式（二元运算、调用、字面量等）暂 `Unknown`。
- `normalize_data_ty_inner`（L326-355）：DataTy→Ty 归一化。Builtin 三特判（Void/Event/Chandle 直接对应 Ty，其余包 BuiltinTy::Data）；**Struct+StructKind::Union 且有 owner→`Ty::Union(owner)`，无 owner→Unknown**（union 身份要 DefId）；Struct(kind 未知也按 Struct)→`Ty::Struct(struct_id)`；Named→路径解析（`type_of_named_data_ty` L357-377：recovery→Error+InvalidTypePath 诊断；typedef 命中→递归展开）；Enum 同 union 需要 owner；Unsupported→Error+诊断。
- `type_of_typedef_inner`（L379-406）：**typedef 环检测**——`seen: FxHashSet<OwnerRef<TypedefId>>` 跨归一化传递，重访即 `Ty::Error`+`TypedefCycle` 诊断（L384-389）；正常路径产出 `Ty::Alias{typedef, target}`，target 为 Error 时不再包 Alias（L400-404）；**seen 的 insert/remove 配对**（L384/L393/L399）保证"同 typedef 在非环的钻石结构里可重复出现"。
- `apply_unpacked_dimensions`（L412-437）：把声明器的 unpacked 维度逐层包到 Ty 外侧——Queue/Assoc(key)/Wildcard(assoc unknown)/Dynamic；**Size(key) 若 key 是内建类型名（`string`/`int`/…）也按 Assoc 处理**（L427-433，`builtin_dimension_key_ty` L446-452 + `builtin_type_name_ty` L454-477 的 12 个内建名表）；Range/Size(数字) 是 packed 维度，**留在 Builtin 的 dimensions 里不动 ty**（L433）。
- `data_ty_of_decl`（L479-495）：声明器类型的来源三分派——DeclaratorParent::DeclarationId→declaration.ty()；PortDeclId→`port_decl_ty`（L497-500 从 body.ports 的 header 取）；StmtId→**仅 for 循环 init**（L486-493，其他语句内声明返回 None）。
- `type_of_subroutine_port_impl`（L502-513）：函数/任务端口按序号取 `subroutine.ports`，有类型→归一化，无→Unknown。
**公开 API**：pub(crate) 的 `normalize_data_ty`（L36）/`type_of_path_resolution_impl`（L86）/`type_of_def_id`（L91）/`apply_unpacked_dimensions`（L412）/`data_ty_of_decl`（L479）+ 两个 salsa 查询。
**依赖/被依赖**：imports 最广（hir-def 13 个模块 + utils::get::GetRef + rustc-hash + 本 crate 5 兄弟）；被 db.rs（calls）、members.rs（calls）、type_system.rs（calls）、lib.rs 依赖。
**改动影响面**：DefKind 新增 → L91-223、L124-176、L208-221 三处 match 编译失败（设计使然）；`type_of_expr_impl` 未覆盖的表达式种类（Binary/Call/Literal）都是静默 Unknown，补全/兼容性功能对它们退化为 Unknown 通道；26.3 引用点语义与 hir-semantics/src/semantics/hir_to_def.rs 必须同步。
**集成点**：表达式类型推断目前只做 Ident/Field/ElementSelect/Cast 四类——**扩展推断能力（如二元运算结果宽度、方法调用返回类型）的入口就在 `type_of_expr_impl`**；新 DataTy 种类在 `normalize_data_ty_inner` 注册。

## `crates/hir-ty/src/display.rs`（1161 行）

**角色**：HIR→SystemVerilog 源码文本的渲染器（hover 文本、签名帮助、类型显示的唯一来源；本 crate 最大文件）。
**关键结构与不变量**（>2000 行规则不触发，但按重要性选列）：
- `HirFormatter`（L32-36）：`db + HirWrite + simplified_ty` 三件套；`simplified_ty=true`（`display_signature` L90-94）时 **bit/logic 头与 wire 前缀被省略**（L280-289、L378-381），`display_source`（L84-88）全量——同一类型两种渲染。
- `HirDisplay` trait（L81-95）：`hir_fmt` 核心 + `display_source`/`display_signature` 两个组装方法；`HirDisplayError`（L72-79）包 `fmt::Error`。
- `Ty` 渲染（L103-191）：Alias 显示 typedef 名（无名回退 target，L142-149）；Queue→`elem [$[:max]]`（L117-125）；Assoc→`elem [key]`、key 为 Unknown→`[*]`（L126-135）；Dynamic→`elem []`；VirtualInterface→`virtual interface Name[.modport]`（L160-173）；Enum/Union→`hir_fmt_def_backed_type`（L193-206，**仅当 DefKind::Typedef 才拼名**）；Module/GenerateBlock/Block→owner 名或泛称。
- `OwnerRef<DataTy>` 渲染（L258-344）：Int 种类名+signed；Vector 按 VecKind（bit/logic 受 simplified_ty 抑制，reg 恒显）+ signed + 维度列表；Struct/Union 拼 kind+名；Named 走 `fmt_type_ref`（L54-70，按 `TypePathKind` 选分隔符：Unqualified 无、Package `::`、Hierarchical `.`）。
- `OwnerRef<&Expr>` 渲染（L674-1021）：全表达式种类逆渲染（assignment pattern / inside / dist / call(named `.name(expr)` 参数) / cast `'()` / stream `{<<{a with [3:0]}}` / sequence / property…），是"HIR 表达式→源码"的完备反演，测试 `streaming_with_range_display_preserves_with_keyword`（tests L483-501）钉版 stream with-range 输出。
- 辅助 impl：`PortDirection`/`SubroutinePortDir`（L234-256）、`NetKind`（L1023-1039）、`TimeUnit`（L1041-1052）、`Literal`（L1054-1069，Int 按 serialize(10) 十进制）、`OwnerRef<Dimension>`（L1071-1094）、`OwnerRef<DeclId>`（L1096-1112，名+维度）、`OwnerRef<TypedefId>`（L1114-1134，`typedef <ty> <name>`）、`OwnerRef<Selector>`（L1136-1161）、`BinaryOp`/`UnaryOp`（L410-474 含全部赋值/归约算子）。
- `ty_expr_container`（L221-232）：为 Queue size 表达式找回求值容器（Builtin 带 container、Struct/Alias 带 cont_id、复合递归 elem）。
**公开 API**：`HirDisplay`/`HirFormatter`/`HirWrite`/`HirDisplayError` 全 pub（mod display 公开）。
**依赖/被依赖**：依赖 hir-def 十余模块（expr 全家/constraint/literal/module::port/subroutine/symbol/ty/typedef）+ syntax TimeUnit + db/ty。被依赖：本 crate type_system（display_source 门面）+ 测试 + ide/render.rs、ide/signature_help.rs、ide/code_action/handlers/convert_port_declarations.rs。
**改动影响面**：所有渲染字符串都有 IDE 快照测试兜着；simplified_ty 的省略集合变化会批量改 hover/签名帮助快照。
**集成点**：任何需要把 HIR 类型/表达式变成人读文本的功能（hover、inlay、签名、code action 生成代码）直接对目标值调 `.display_source(db)`；自定义渲染偏好（如更激进的省略）扩展 `simplified_ty` 的分支即可。

## `crates/hir-ty/tests/type_system.rs`（501 行）

**角色**：类型层端到端测试——真实 salsa db（SourceDb→PreprocDb→HirDefDb→TyDb 五层组合，L37-59）上跑公开接口，同时**守护 hir-def lowering 的保真度**（enum/constraint/coverpoint/class 四个测试实际断言的是 lowering 结构）。
**覆盖行为**（12 个测试，关键者）：
- `semantic_types_render_through_the_public_interface`（L143）：queue/bounded queue/assoc/dyn/event/chandle/enum/union 八种类型经 `TypeSystem::display_source` 渲染成 `logic [$]`、`logic [$:4]`、`logic [string]`、`logic []` 等源码形。
- `members_and_compatibility_hide_classification_and_width_calculation`（L188）：struct 成员枚举 `["flag","code"]`；`logic [1+2:0]` 与 `logic [3:0]` Compatible（**常量折叠宽度**）、4 位 vs 8 位 Incompatible、int vs real Incompatible、与 Unresolved 比较 Unknown——三值兼容性语义的钉版。
- `type_path_selectors_are_explicit_recovery`（L421）：`t[0] value;` 产生 `InvalidTypePath(Selectors)` 诊断（类型路径里的选择器是显式恢复节点）。
- `definition_backed_types_render_without_exposing_definition_kinds`（L456）：实例 `u_if`→`virtual interface bus_if`、modport→`virtual interface bus_if.host`、program 实例→`p`。
- 另有 struct 成员维度并入（L225）、enum 基类型/成员/初始化器保留（L253）、constraint dist+unique 降级（L279）、`[*]` 通配关联数组（L311）、coverpoint bins（L329）、class 基类/成员种类（L356）、限定类型路径分隔符与 source projection（L378）、struct 类型无诊断（L441）。
**跑法**：`cargo test -p hir-ty`（dev-dependency preproc-expand 供 db 组合）。
