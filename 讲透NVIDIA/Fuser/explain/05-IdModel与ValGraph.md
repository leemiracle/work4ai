# 05 · IdModel 与 ValGraph：调度分析的中枢

## 角色定位

`csrc/id_model/` 是 nvFuser 把"哪些 IterDomain 是同一个"形式化的地方。IdModel（id_model.h:107，class NVF_API IdModel，类体 [107,365]）维护一组按语义分层的等价图：EXACT/ALMOSTEXACT/BROADCAST/PERMISSIVE/LOOP；每张图都是 ValGraph（val_graph.h:56）——在 DisjointSet 之上维护 Val/Expr 到分组的双向映射与定义-使用链。图谱甄别把它称作"调度分析的中枢"：loop_promotion、indexing、contiguity、predicate_indexing 全部消费其产物；它也是旧 ComputeAtMap（compute_at_map.h:182）的替代者——id_model.h 构造函数注释明言 validate 参数是"从当前 ComputeAtMap 迁移期间的临时选项"。

## 内部结构

图的分层在 id_model.h 注释与构建器序列里写死：buildExactGraph（id_model.h:190，实现 id_model.cpp:285）只映射输入-输出精确对应的域；buildAlmostExactGraph（id_model.h:195）在 Exact 之上合并"与 size-1 merge/split"；buildBroadcastGraph（id_model.h:200）允许穿过 broadcast；buildPermissiveGraph（id_model.h:205）再放行 forward 映射；buildLoopGraph（id_model.h:214，实现 id_model.cpp:1073）是 Permissive 的子图、只收内联相关的域；buildAllGraphs（id_model.cpp:1100）串起全流水。访问走 idGraph(IdMappingMode)（id_model.h:148），元数据有 idUses/idDefinitions（id_model.h:151/:156）；产物 loopPromotionMap（id_model.h:239）由 buildLoopPromotionMap（id_model.h:296）产出；addReplayAs 支持把域变换回放进图；validateAndPropagatePType 保证每个 LOOP 等价类只有一种非串行并行类型。ValGraph 本体（val_graph.cpp 844 行）：mapVals（val_graph.h:242）合并两个 Val 所在组，mapThroughExpr（val_graph.h:352）沿表达式继续传播（可由 propagate_through_exprs_ 关闭，:358-362 注释解释递归风险），exprsMap（val_graph.h:226）判表达式等价，toGroup/areMapped（val_graph.cpp:80/:90）是查询面。节点类型 ValGroup/ExprGroup 是 shared_ptr\<VectorOfUniqueEntries\>（val_graph_nodes.h:18-21）。遍历家族平行于 iter_visitor：ValGraphVisitor（val_graph_visitor.h:59）/ValGraphStmtSort（:111）/ValGraphBFS（:202）/ValGraphPermissiveBFS（:241）。

## 外部连接

上游：Fusion 的全部 IterDomain 与 inlining 决策（StatefulInliningInfo，id_model.h:25）。下游：loop_promotion.h:27 CoveredGroup 与 :126 LoopPromotionMapBuilder（实现 1453 行）在 IEL 图上算每个循环的覆盖域；indexing.h:48 TensorIndexer（实现 indexing.cpp 1123 行）按"找循环域→找分配域→找路径→双向传播"生成访问索引（IndexingInfo，indexing.h:25）；contiguity.cpp 的 ContigIDGroups 推导可连续 ID 组；id_model/schedule.h:41/:49/:64 提供 ValGroup 级 merge/split/swizzle，是 06 篇 AbstractTensor 的图端后端。

## 数据流

构建期：Fusion 表达式集合进构造函数（id_model.cpp:51/:82 两个重载，后者带 validate）→平凡映射初始化 initializeIdGraph →逐表达式按 split 可整除性、broadcast 语义合并等价类 → LOOP 图再叠加内联信息。查询期：indexing/loop_promotion 以 ValGroup 为单位提问，图保证"同组即同索引变量"。回放期：调度器在图上 addReplayAs 记录的变换与 TensorView 侧变换保持同构。

## 设计决策

用 disjoint-set 组织而非直接建图遍历，是"等价"这一高频查询的常数级化；五层图按语义严格分层（每层都是上一层的收紧或放宽），调用方按需取最便宜的一层，避免一刀切 Permissive 造成的过度合并。ValGraph 与 IR 分离（Val 不是图节点、组才是），使分析可丢弃可重建、不污染 IR。宏前缀 NVF_API（visibility.h:15-20 定义，全仓约 50 处类声明）是自动分析的系统性盲区：`class NVF_API X : public Y` 形态让 tree-sitter 丢类——base_nodes.h 三根、TensorView、IdModel 本尊都中招，本图谱对它们全部人工补齐行区间，其他工具链统计本仓类数会系统性偏小。

## 新人提示

先读 id_model.h 头部 ~100 行注释，五种 IdMappingMode 的语义边界写得比任何文档清楚。调试用 id_model/to_string.cpp 的 toString 家族打印 ValGraph。分不清该查哪张图时记住：索引正确性用 EXACT，调度合法性用 PERMISSIVE，循环唯一性用 LOOP。图上做变换前确认目标图允许（schedule.h 的函数自带"已有同因子 split 则复用"的幂等性）。引用 [107,365] 这类区间以本图谱为准。
