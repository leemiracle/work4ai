# 08 · 类型推断：hir-ty 的 infer.rs

## 角色定位

`crates/hir-ty` 回答一个问题：「这个名字/表达式/声明是什么类型？」对 IDE 而言这不是编译器式的全局 elaborate（完整 elaboration 需要参数传播与实例图），而是 rust-analyzer 式的**按需、局部、可恢复**推断：给定 `DefId` 或 `ExprId`，从 HIR arena 出发查类型，查不动就返回 `Ty::Unknown`，绝不因一处失败拖垮整个查询。`infer.rs` 是这层的总调度：def → decl → data_ty 归一化 → 表达式递归。整层刻意保持「无 mut 状态机、无定点迭代」——SV 的大部分 IDE 场景（hover、补全过滤、成员选择）不需要完整推断链，按需展开正好匹配 Salsa 的惰性求值模型。

## 内部结构

`infer.rs`（513 行）的查询族自上而下三层：

**入口查询**（Salsa tracked）：L29-35 `ExprQueryKey{owner, local}` interned（同一套「整数需包装才能当 tracked key」的理由）；L49-53 `type_of_def_origin_query(db, DefOrigin) -> Type`；L55-65 `type_of_expr_query(db, key) -> Type`——从 owner 的 body arena 里 `nth(key.local)` 取回表达式（L57-62 的 expect 钉死「key 必须指向 owner body 内的表达式」），再进 `type_of_expr_impl`。

**def 分派**：L91-223 `type_of_def_id(db, DefId) -> TyResult` 是全文件最长函数——按 `DefKind` 巨型 match：Module/Package/Program 直接 `Ty::Module`（L97-100）；Interface 给 `Ty::VirtualInterface`（L101）；Port/Variable/Net/Param/Genvar/Specparam 走 `type_of_decl_impl`（L104-113）；Typedef 走 `type_of_typedef_impl`（L114-117）；Instance 先 `instance_target_def_id` 解析目标再按 kind 给 VirtualInterface/Module/Checker（L118-177）；Modport 组装带 modport 的虚接口（L178-187）；GenerateBlock/Block 各给自家类型（L188-195）。两批「editor-only definition kind」以 `unreachable!` 收尾（L208-221）——这些 kind 只在 IDE 查询出现，推断永远不该见到。L224-283 `type_of_non_ansi_port`：遍历 def 全部 origins，Variable/Net 类型可用即返回（L232），否则保留首个 Port 类型（L233-235）。

**核心递归**：L285-313 `type_of_expr_impl` 处理四种表达式——`Expr::Ident` 先取引用位置（L291-295，注释引用 LRS 26.3：**表达式引用在其源位置解析，后声明不得遮蔽先前的 import**）再 `resolve_name_at` + `type_of_path_resolution_impl`；`Expr::Field` 先推 receiver 再 `select_member` 并合并诊断（L297-308）；`Expr::ElementSelect` 透传 receiver 类型（L309）；`Expr::Cast` 归一化目标类型（L310）；其余一律 Unknown（L311）。

**类型归一化**：L326-355 `normalize_data_ty_inner` 把 HIR 的 `DataTy` 翻成 `Ty`：Builtin 特判 Void/Event/Chandle（L334-339），Struct 按 Union/Struct 分流（L340-346），Named 走 `type_of_named_data_ty`（L357-377：resolve_path 唯一命中且是 typedef 则递归展开，否则 `type_of_def_id`），Unsupported 给 `Ty::Error` + 诊断（L351-353）。L379-406 `type_of_typedef_inner` 用 `seen: FxHashSet` 做环检测（L384-389，环给 `TypeDiagnostic::TypedefCycle`），成功路径包成 `Ty::Alias { typedef, target }`（L400-405）。L412-437 `apply_unpacked_dimensions` 把非打包维度逐层套上：Queue/Assoc/Wildcard/Dynamic（L418-433），普通 Range/Size 不变（L433）。

支撑文件：`ty.rs` L11-33 定义 `Ty` 枚举（Unknown/Error/Void/Builtin/Struct/Enum/Union/Queue/Assoc/Dynamic/Event/Chandle/Alias/Module/Checker/Covergroup/VirtualInterface/GenerateBlock/Block——`pub(crate)` 可见性，对外经 lib.rs 的 `Type` 封装）；L35-42 `TyResult{ty, diagnostics}`（**类型与诊断同 travel**）。`db.rs` L8 `trait TyDb: HirDefDb`、L13-15 Deref 下放、L17-25 两个入口：`infer_expr(OwnerRef<ExprId>) -> Type`（内部把 ExprId 转成 `ExprQueryKey` 走 tracked 查询）与 `infer_path_resolution`。

## 外部连接

上游全部来自 hir-def：`DefKind/DefId/OwnerId/OwnerRef`、`expr::data_ty::{BuiltinDataTy, DataTy, Dimension, TypeRef}`、`pathres::{resolve_name_at, resolve_path, instance_target_def_id}`、`declarator::DeclaratorParent`。名字解析不在本层——infer 每步把「这名字是谁」外包给 pathres，自己只管「是谁 → 什么类型」。下游：`hir-semantics` 在 hover 里调 `infer_expr`；`ide::completion` 的 typed_filter 用 `is_compatible_typed_value` 做类型过滤；members.rs 的 `select_member`（infer.rs L25 引用）支持 struct/interface 成员选择。`ExprQueryKey` 只在本 crate 与 db.rs 入口使用，外界永远拿 `OwnerRef<ExprId>` 这类语义坐标。

## 数据流

hover 一个信号 `sig` 的完整链：ide 层 `Semantics` 找到表达式节点 → `db.infer_expr(OwnerRef{cont_id, value})`（db.rs L17-20）→ intern 出 `ExprQueryKey` → `type_of_expr_query`（L55-65）→ `type_of_expr_impl` → `Expr::Ident` 分支（L288-296）：`expr_reference`（L316-324）从 body source map 取 `SourceAstId` 构造 `NameRef{position, kind: Value}`——**引用位置参与解析**是 SV 顺序语义的正确建模 → `resolve_name_at` 沿作用域链找到 `Resolution<DefId>` → `type_of_path_resolution_impl`（L86-90）取唯一 def → `type_of_def_id` 的 DefKind match → 声明类落到 `type_of_decl_impl`（L70-84）：`data_ty_of_decl`（L479-495）按 DeclaratorParent 三分支取 DataTy（声明/端口头/for 初始化），`normalize_data_ty_with_owner` 归一化，`apply_unpacked_dimensions` 套数组维度。返回的 `TyResult` 一路向上，hover 只展示 ty 分量。增量性：所有入口都是 tracked 查询，body 或类型声明一变，Salsa 沿依赖图精确重算受影响的表达式类型，其余命中 LRU。

## 设计决策

**为什么 per-expression 查询而不是整 body 一遍推断？** rustc/Chalk 传统是 `infer(body)` 全量算完存表；IDE 场景用户只 hover 一处，全量是浪费。`type_of_expr_query` 以 (owner, expr) 为粒度，Salsa 天然去重共享子查询——点十个表达式只有首次付费。代价是 `nth(local)`（L60）的随机访问要求 body arena 稳定，由 body 查询的 salsa 缓存保证。

**为什么 Unknown 与 Error 分开？** `Ty::Unknown` 是「不知道但没错」（未支持的构造、解析失败），`Ty::Error` 是「确定错了」（typedef 环、Unsupported 数据类型）。下游据此决定要不要报诊断、要不要继续推——`Expr::Field` 对两者直接短路透传（L302-304），避免错误雪崩。

**为什么 typedef 展开成 Alias 而非透明替换？** `Ty::Alias { typedef, target }`（L403）保留别名层，hover 能显示「`my_t` = logic [7:0]」而非裸类型；`seen` 集合的环检测（L384-389）把 `typedef a = a;` 变成一条诊断而非死循环。

**为什么 builtin_type_name_ty 手写表？** dimension 的索引类型可以是裸 builtin 名（`assoc array [string]` 里的 string，L454-477）：这些标识符不走声明解析，直接按名字映射成 BuiltinDataTy，省一次注定失败的 resolve。

## 新人提示

1. 加新 DefKind 时三处同步：type_of_def_id 的 match（L96-222）、（若需要）type_of_non_ansi_port 的 origins match（L231-280）、以及「editor-only」unreachable 分组——放错分组会在测试里炸出 unreachable。
2. 类型诊断别在推断外单独查询：TyResult 已携带 TypeDiagnostic，直接消费 `result.diagnostics`。
3. 排查「hover 类型不对」：先看 resolve 命中了谁（pathres 层），再看 normalize 是否被 Unsupported 截断成 Error——两种病因修法完全不同。
4. `ExprQueryKey.local` 是 arena 下标强转 u32（db.rs L18-19），不要拿它做持久化或跨快照比较；语义坐标始终用 `OwnerRef<ExprId>`。
