# 07 · HIR lowering：语法的去语法化（crates/hir-def/src/lib.rs + lower.rs）

## 角色定位

slang 给出的是「忠实于书写」的语法树：每个括号、每个 keyword 都有节点。但类型推断与名字解析需要「忠实于语义」的模型：声明就是声明、引用就是引用，语法糖剥掉。`hir-def` 就是这道去语法化工序，L1-8 的 crate 文档自我定位为「ECS 风格的定义实现：arena、局部索引、container id、作用域、source map 与解析结果都在这里；可依赖 preproc-expand，但不得依赖类型推断、语义适配或 IDE 功能」。它把整棵 AST 压平成一组 Arena（`Body` 是容器，`ExprId/StmtId/DeclId` 是下标），并以 `OwnerId` 划分「结构所有者」（module/block/subroutine/generate…）——每个 owner 的 body 独立 lowering、独立缓存、独立失效。这份「ID 是显式的 workspace 内部接口，不是稳定的面向对象门面」（L7-8）的克制，是它能被 hir-ty/ide 两层反复组合的前提。

## 内部结构

**lib.rs**（211 行）是整座车间的零件目录。L12-53 列出 40 个子模块（aggregate 到 unit_index）；L55-68 的 `impl_arena_getters!` 声明宏批量生成 `GetRef<Id> for Container` 实现，L70-83 的 `impl_source_map_getters!` 同理生成 source map 查询——两行宏消灭上百个样板 impl。基础类型：L89 `pub type Ident = SmolStr`、L91 `DEFAULT_NAME = "unnamed"`（缺失名的统一占位）。L93-108 定义 `PackageImport/PackageExport`（保留 source 位置的 `SourceAstId`，供「按引用点解析」）。L110-132 是 package export 的两个 lower 函数。**最通用的工具函数**在 L134-211：`lower_ident`（L134-137，token 文本转 SmolStr）与 `lower_ident_opt`（L141-144，空串归 None——注释：空标识符代表缺失）；`alloc_with_optional_source_entry`（L169-183）是「Arena 分配 + source map 登记」的原子操作——**每个 HIR 节点出生时就拿到源身份**；`alloc_with_source`（L197-211）的泛型版本接收任意 AstNode，经 `ast_ids.id_of_node_in_tree` 换 SourceAstId 再登记。

**lower.rs**（408 行）是 lowering 的机械骨架。L31-37 `LoweringSyntax` 打包一次 lowering 的四份共享输入（file_id、SyntaxTree、AstIdMap、OwnerTable）——L28-30 注释点明动机：ItemTree 的发现阶段与 lower 阶段复用同一份 parse/AST map/owner 表，「防止查询环」。L55-69 `LoweringStore` trait 暴露六对 `(Arena, SourceMap)` 访问器（expressions/event_expressions/declarators/statements/declarations/body），L71-173 三个宏批量为 `BodyStore` 实现 LoweringStore/CheckerStore/ProcStore/ModuleItemStore——**加一种 HIR 类别只需 trait 加一对方法 + 宏一处**。L176-188 `LoweringCtx<Store>` 是一次 lowering 的全部可变状态：scope_stack（OwnerId 栈）、store、diagnostics，以及 L186-187 的 `default_nettype: Arc<[(TextSize, Option<NetKind>)]>`（文件内 `` `default_nettype `` 指令的源序表，None 表示 none）。L190-221 构造函数建根作用域（L219 `scope_graph.ensure_root(owner)`）。作用域管理 L253-264：`enter_body_scope` 断言父链符合 owner 图（L256——作用域栈必须镜像权威 owner 图）、L261-264 LIFO 弹出。登记族 L266-293（push_body_item/record_body_declaration/declarator/typedef/statement）统一写 `scope_graph`。诊断族 L295-313（report_unsupported/report_invalid）；L319-328 `implicit_net_kind`：隐式线网在 `` `default_nettype none `` 下仍按 wire lower 但报诊断（注释：保持 body 一致、诊断携带源位置）；L227-232 `net_kind_at` 用 `partition_point` 二分找光标前最近指令。L330-343 `emit_diagnostics` 取走并逐条打 warn。

**body.rs**（991 行）持有产物容器：L100-105 `BodyScopeData`（owner/parent/items/declarators/typedefs/statements 五槽 SmallVec），L110-114 `BodyScopeGraph`（root + scopes + by_owner 索引）——**作用域身份直接复用 OwnerId，不另设块 id**（L98-99 注释）。db.rs 把这一切挂上 Salsa：`dyn HirDefDb` 查询面（db.rs L28-115）暴露 `syntax_file`（L31）、`ast_id_map`（L36）、`owner_table`（L41）、`body_with_source_map`（L46）、`item_tree`（L59）、`scope`（L91）、`design_map`（L113）等；L117-131 `set_lru_capacity` 一次调齐 11 个查询的 LRU。

## 外部连接

上游 `preproc_expand::file::HirFileId`（lower.rs L2）——lowering 的输入既可以是真文件也可以是宏文件；`syntax` 的 ast 类型贯穿所有 lower 函数。下游 `hir-ty` 从 `DefKind/DefId` 出发做类型（infer.rs 的巨型 match 全部消费本层枚举）；`hir-semantics` 用 `owner_table` 做 source_to_def；`ide` 的 semantic_index 消费 `body_with_source_map`。`la_arena::Arena/Idx`（lib.rs L85）是全层统一容器；`utils::get::GetRef` 是统一读取 trait（L60-66）。

## 数据流

一个 module 的 lower 全程：查询 `db.body_with_source_map(owner)` → `LoweringSyntax::for_owner(db, owner)`（lower.rs L49-53）一次取齐 parse/ast_id_map/owner_table → 构造 `LoweringCtx::new_with_syntax`（L202-221，scope_stack=[owner]，装载 default_nettype 指令表）→ 遍历 module 成员：每遇到数据声明，`alloc_with_source::<_, _, Declaration>`（lib.rs L197）把 AST 折成 Declaration 值进 arena 并登记 source map，再 `record_body_declaration(declaration_id)`（lower.rs L271-276）挂进当前作用域；表达式统一经 `ctx.expressions()`（L347）拿 `(Arena<Expr>, SourceMap<Expr>)` 分配 ExprId；进入 begin/end 块时 `enter_body_scope(child_owner)`（L253）压栈，离开时 L261 弹出。产物 `Lowered<Body>` 同时含 data 与 sources，同一下标对齐——IDE 的「HIR→源码」回溯就查这张表。失效粒度：改一个字符只重跑该文件受影响 owner 的 body 查询，其余 owner 从 LRU 命中。

## 设计决策

**为什么 Arena + 下标而不是树状 struct？** 编译期语义数据是稠密图（表达式互相引用、声明被多处引用），树状 struct 会逼出 Rc/RefCell。Arena 方案让 ExprId 是 Copy 的 u32，HashMap key、快照存储、跨查询传递零成本——rustc/chalk 一脉的经典选择，vide 在 SV 语境复刻。

**为什么 owner 划分 body？** 模块内文本改动不应失效别的模块。`body_with_source_map(owner)` 以 OwnerId 为键，Salsa 只重算被改 owner；AstIdMap/OwnerTable/ItemTree 又是更细的共享层（发现与 lower 复用，lower.rs L28-30 注释同时点破「防查询环」——先建表后 lower，依赖单向）。

**为什么 source map 出生即登记？** IDE 一切「从 HIR 回到光标」的功能（hover 区间、rename 范围、诊断定位）都依赖双向映射。`alloc_with_optional_source_entry`（lib.rs L169）把「分配 + 登记」锁成原子步骤，杜绝「忘了登记导致回溯丢定位」的静默 bug；`source_id`（lower.rs L239-243）用 expect 钉死「每个被 lower 的 AST 节点必须有规范源身份」。

**为什么作用域身份复用 OwnerId？** 见 body.rs L98-99 注释：另设块 id 会造出两套需同步的身份体系。OwnerId 已由 OwnerTable 权威分配、被 db 层缓存，作用域图直接引用，L256 断言保证栈序与权威父图一致——一处事实，多处投影。

## 新人提示

1. 新加一种 HIR 节点的固定四步：定义值类型 + Arena 字段进 Body → LoweringStore trait 加访问器（lower.rs L62-69）→ 宏表加一行（L71-99）→ 写 lower 函数只用 `alloc_with_source*` 分配。绕过它会得到没有源身份的孤儿节点。
2. `lower_ident_opt` 的空串归 None 语义贯穿全层；判断「匿名」用 `ident == DEFAULT_NAME`。
3. 作用域栈的 assert（L256、L262-263）在 debug 下才拦截，release 下错序会产生畸形 scope graph——开发期跑 debug 版。
4. 查「某语法构造被 lower 成什么」最快路径是 snapshot 测试与 `db.item_tree`/`db.body` 的 debug 输出，不必通读 body.rs。
5. `default_nettype` 示范「指令影响语义」的通用模式：源序表 + partition_point 二分（L227-232）——支持 `` `unconnected_drive `` 等指令可照抄。
