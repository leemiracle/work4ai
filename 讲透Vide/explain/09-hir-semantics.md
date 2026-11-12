# 09 · hir-semantics：面向消费方的语义门面（crates/hir-semantics/src/semantics.rs）

## 角色定位

IDE 功能作者面对的世界应当是「给我文件里的这个位置，告诉我它对应哪个语义对象」——而不是「自己拼 db 查询、自己爬 AST、自己换算 ID」。`semantics.rs` 就是这门面向消费方的 API，138 行在动辄千行的各层里显得刻意单薄：它只做**粘合**，把 parse、ast_id_map、owner_table、pathres 这些分散在三个 crate 的查询组装成四个动作（node→def、expr→def、name→def、container 查找）。rust-analyzer 里同名的 `Semantics` 也是这个角色——查询门面 + 语法树借用管理。vide 的版本还有个隐性职责：**让语法树的生命周期可控**（`ParsedFile` 持有 SyntaxTree，借用节点不得逃逸），并把 source→def 的细节封装进 `source_to_def` 子模块。

## 内部结构

文件骨架四段：

**Semantics 双层结构**（L28-31 与 L91-93）：外层 `Semantics<'db, DB: HirDefDb>` 泛型于具体 db 类型（测试可以用 TestDb，生产传 RootDb），内层 `SemanticsImpl<'db>` 只持 `&'db dyn HirDefDb`——trait 对象。L63-69 的 `Deref` 让外层直接调内层方法，泛型与动态分发两全。`new(db)` 在 L57-60 构造。这个双层与 rust-analyzer 一致：外层管理 per-query 的缓存与 span，内层是无状态查询核心（vide 尚未在外层挂缓存，留给未来）。

**ParsedFile**（L33-54）：`(HirFileId, SyntaxTree)` 的持有者。提供 `file_id()`、`syntax_tree()`、`root() -> Option<SyntaxNode>`、`compilation_unit() -> Option<ast::CompilationUnit>`（L51-53，cast 到编译单元视图）。它是语法树借用的**宿主**：所有从它借出的 `SyntaxNode<'_>` 生命周期都锚在 ParsedFile 上（tree.rs 的注释早就警告过节点不得活过树）。

**find_node_at_offset**（L71-89）：本文件唯一的算法性代码。给定 root 与 offset，找最近的 `N: AstNode`：L77-85 处理 `token_or_node_at_offset` 的 Either——Between(左/右 token) 时从两个 token 的 parent 各起一条 `SyntaxAncestors` 迭代器，`kmerge_by` 按 range 长度归并（小者优先，L80-84），`find_map(N::cast)` 取第一个可 cast 的祖先；At(node) 时单链 `find_map`。**从最近的祖先向外试探**保证了「光标在表达式里时返回表达式、在语句里时返回语句」的正确粒度。

**SemanticsImpl 的两组方法**（L95-137）：读侧 `parse_file(file_id) -> ParsedFile`（L100-103，HirFileId::from + db.parse——宏文件与普通文件统一入口）与 `container_for_node(file_id, node) -> Option<OwnerId>`（L105-107，委托 `source_to_def::find_container`）；映射侧四个 `*_to_def`：`module_to_def`（L111-117）、`block_to_def`（L119-121）、`subroutine_to_def`（L123-129）都是 `(HirFileId, ast::Xxx) -> Option<OwnerId>` 的窄接口；`expr_to_def(in_cont: OwnerRef<ExprId>) -> Resolution<DefId>`（L131-133）与 `name_to_def(OwnerRef<Ident>, NameContext::Value)`（L135-137）走 `hir_to_def` 子模块（把 HIR 侧的引用解析成 def 集合，Resolution 表达歧义多解）。

**source_to_def.rs**（152 行）承担全部脏活：`source_ast_id`（L16-22）经 `db.parse + db.ast_id_map + id_of_node_in_tree` 把语法节点换成规范 `SourceAstId`；`owner_for_node`（L26-34）查 `owner_table(file_id).owner_by_ast(ast_id, kind)`；`module_to_def`（L36-42）即「ModuleDeclaration 节点 → OwnerId」三行流水。`container_to_def`（L68-70 起）是向上爬容器的分派器：CompilationUnit 直接取 file_owner，Module/AnonymousProgram/Checker 各自 cast，`generate_owner_node`（L56-64）特判 loop generate 归属（GenerateBlock 的 owner 是外层 LoopGenerate）。

## 外部连接

依赖面极窄：`hir_def`（HirDefDb、DefId、OwnerId、OwnerRef、NameContext、Resolution）、`preproc_expand::file::HirFileId`、`syntax`（SyntaxAncestors/SyntaxNodeExt/ast/AstNode）。**它不依赖 hir-ty**——类型推断经消费方自调 db（Semantics 只保证坐标对齐）。下游是 `ide` 全家：completion/context.rs L96-97 与 engine/expr.rs L60-62 都以 `Semantics::new(db)` + `parse_file` 起步；semantic_index/build.rs L64 的 `SemanticsImpl::new(db)` 在索引构建里爬容器链；goto/hover/references 经 `container_for_node` 或 `find_node_at_offset` 进入。文件顶部 L21-26 声明四个子模块（hir_to_def/pathres/resolver/source_to_def），`is_generate_branch_member` 对外转售（L26）。

## 数据流

一次「找光标所在模块」的完整数据流（document highlight 的前置）：`Semantics::new(db)` → `sema.parse_file(file_id)`（db.parse 走 preproc-expand 查询，宏文件返回展开树）→ `parsed_file.root()` → `sema.find_node_at_offset::<ast::ModuleDeclaration>(root, offset)`（kmerge 归并双祖先链）→ 拿到 ast 节点后 `sema.module_to_def(file_id.into(), module)`（L111-117）→ `source_to_def::module_to_def`（L36-42）：`source_ast_id` 用 **db 缓存的 AstIdMap** 把节点换算成 SourceAstId（深度优先先序号，稳定于文本编辑中的合理重排）→ `db.owner_table(file_id).owner_by_ast(ast_id, OwnerKind::Module)` → `Some(OwnerId)`。此后 ide 拿 OwnerId 可查 `db.body(owner)`、`db.scope(owner)`、甚至 `source_root_semantic_index` 做引用查找。表达式路径（hover 类型）：`find_node_at_offset::<ast::Expression>` → 在 body source map 反查 ExprId → `sema.expr_to_def(OwnerRef)` 得 Resolution → db.infer_expr 出类型。两条路共享同一套 ID 换算基础设施，这正是门面存在的意义。

## 设计决策

**为什么需要这一层而不让 ide 直接调 db？** 没有 Semantics 时，每个 IDE 功能都要复写「parse→找节点→换 AstId→查 owner」四步，换算细节（generate 归属、宏文件的 HirFileId 包装）会散落几十处。门面把这些固化成四个窄方法，source_to_def 的特判集中一处——`generate_owner_node`（L56-64）这种「LoopGenerate 与 GenerateBlock 的 owner 归属」规则只写一遍。

**为什么 ParsedFile 持树而不是直接返回 SyntaxNode？** SyntaxNode 借用树（`SyntaxNode<'a>`）；若 parse_file 直接还节点，树的 SharedPtr 会被立刻 drop，节点悬垂。ParsedFile 以值语义持有树并借出节点，生命周期错误在编译期暴露。

**为什么 module_to_def 返回 Option 而非 panic？** 文本可能正处于编辑中间态（模块头残缺、节点不在 owner_table 里）。门面方法的合同是「尽力映射，失败由调用方降级」——IDE 的健壮性哲学：语法层的烂输入不能击穿语义层。

**为什么 parse_file 接 FileId 却内部 into HirFileId？** 调用方手里几乎总是 VFS 的 FileId（来自 LSP uri）；HirFileId::from 的转换点收在门面内，宏文件（HirFileId::Macro）的构造则留给 preproc 感知的地方。文件/宏的统一在 db.parse 一侧完成（db.rs L544-559 的分派）。

## 新人提示

1. 写新 IDE 功能的标准开头三行照抄 completion/context.rs L96-98：`Semantics::new(db)` → `parse_file` → `find_node_at_offset`。别自己 `db.parse` 后裸爬树——会绕过容器归属等特判。
2. 从 `find_node_at_offset` 拿到的节点 borrow 自 ParsedFile，需要长期保存时立刻换 `SyntaxNodePtr`（syntax/ptr.rs），别延长借用。
3. `Resolution<DefId>` 是集合语义：SV 的名字可多定义（同名模块多处声明）。`resolution.unique()`（infer.rs L87）是「唯一或放弃」的快捷方式，重命名/跳转要处理多解而不是 ignore。
4. 加新的「XxxDeclaration → def」映射：在 source_to_def.rs 写 `xxx_to_def`（照 L36-42 模板），再在 SemanticsImpl 加转发（L111-129 模式）。不要在 ide 层直接 import source_to_def。
5. 这层的测试跟着 hir-def/ide 的快照走；semantics.rs 本身没有独立测试模块，改动后跑 ide 全量快照最稳。
