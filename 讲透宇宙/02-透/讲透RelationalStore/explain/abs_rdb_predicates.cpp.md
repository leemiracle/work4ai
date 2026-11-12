# abs_rdb_predicates.cpp 精讲

> 源码：frameworks/native/rdb/src/abs_rdb_predicates.cpp（432 行）；配套 abs_predicates.cpp / rdb_predicates.cpp

## 1. 角色定位

rdb-kernel 层，导览第 4 步枢纽。三层继承的中间层：AbsPredicates（通用 WHERE 状态积累）→ AbsRdbPredicates（表名＋JOIN 槽位＋分布式镜像）→ RdbPredicates（JOIN 语法落地）。根因是双轨需求：本地查询要把链式调用拼成 WHERE 字符串（基类职责），分布式同步/云共享需要可序列化的 PredicatesMemo（predicates_，h L385）随 IPC 发往远端。

## 2. 内部结构

构造（L27-47）把表名同时写入 tableName_ 与 predicates_.tables_。核心模式是双写：谓词方法先 predicates_.AddOperation(...) 记 memo，再调基类版本拼本地子句。按功能分：

- 条件：EqualTo（L232，string/double→int64/int64/Asset 四路分派）、GreaterThan 等（L104）、Contains/Like 等（L340）、IsNull（L362）、In/NotIn（L305/L402）；逻辑 And/Or/BeginWrap（L267-303）。
- 排序 OrderByAsc/Desc（L279）；去重 Distinct（L392）；索引 IndexedBy（L397）。
- 分页：Limit/Offset 用基类（L429：limit<=0 归 -1）；GetDistributedPredicates（L222）导出时补写 LIMIT。

JOIN 状态四数组（h L378-381）本层只做存取（L63-187）；GetJoinClause() 返回空串（L168-171），留给 RdbPredicates 覆写（rdb_predicates.cpp L18）——模板方法钩子。

## 3. 外部连接

依赖：SqliteSqlBuilder（L431）、基类 AbsPredicates、PredicatesMemo（rdb_types.h）。

被依赖（grep 实证）：①子类 RdbPredicates；②本地查询链 RdbStore::Query（rdb_store.cpp L272，含 #_ 字段时改走 BuildCursorQueryString）、RemoteQuery（L645）；③分布式/云链 QuerySharingResource（L630）与 InnerSync（L1051）取 GetDistributedPredicates()。

## 4. 数据流：一条谓词到 SELECT SQL

以 RdbPredicates("EMPLOYEE").EqualTo("NAME","张三").OrderByAsc("AGE").Limit(10) 为例：

1. EqualTo（L232）：memo 记 EQUAL_TO/NAME/"张三" → 基类 EqualTo（abs_predicates.cpp L54）：CheckParameter（仅查非空）→CheckIsNeedAnd（后续条件自动前补 " AND "）→ whereClause += "NAME = ? "、bindArgs.push_back。
2. OrderByAsc（L279）：memo 记 ORDER_BY/AGE/"true" → 基类 L388 拼 "AGE ASC "（逗号续接）；Limit（基类 L429）置 limit=10。
3. Query 入口（rdb_store.cpp L272）→ BuildQueryString（sqlite_sql_builder.cpp L134）："SELECT * FROM EMPLOYEE"＋BuildClauseFromPredicates（L59-71）依次拼 JOIN/WHERE/GROUP BY/ORDER BY/LIMIT（L110）。
4. 产物 SELECT * FROM EMPLOYEE WHERE NAME=? ORDER BY AGE ASC LIMIT 10＋bindArgs 绑定执行。

## 5. 设计决策

- 建造者模式：方法全返回 this 链式调用；Clear()（L49-53）先清基类再 InitialParam()（L55-61）清 JOIN 状态。
- 分层理由：基类沉淀与引擎无关的 WHERE 语义；本层加表名/JOIN/分布式镜像并稳定导出 inner_api；RdbPredicates 才实现 INNER/LEFT/CROSS JOIN...ON/USING。
- 双写不对称：EqualTo 对 double 截断（L237）；In 有 memo 镜像（L325），NotIn(vector<ValueObject>)（L407-428）却从未 AddOperation——本地 SQL 正确但该条件不随分布式同步，远端多数据排障优先怀疑。
- 转义责任上移：值全走 ? 绑定防注入，但 CheckParameter 只防空（abs_predicates.cpp L561-577），字段名与 % 不转义。

## 6. 新人提示

- 切入顺序：先读 abs_predicates.cpp（isNeedAnd 状态机），再读本类（双写），最后 rdb_predicates.cpp（JOIN）。
- 易错点：①Or() 后再 Or() 被基类 L138-146 拒绝（仅 WARN），需 BeginWrap/EndWrap；②Limit(0) 或负数归 -1 不生效不报错；③EqualTo 传 double 截断成整数比较；④字段名含引号不清洗，调用方自行约束；⑤调试用 GetStatement()。
- 测试：unittest/rdb_predicates_test.cpp、interface/rdb_predicates_join_test.cpp、fuzz 三件套 abspredicates/absrdbpredicates/rdbpredicates。
