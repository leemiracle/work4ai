# transaction_impl.cpp 精讲 — 对象式事务的落地实现

> `frameworks/native/rdb/src/transaction_impl.cpp`（326 行）+ `include/transaction_impl.h`；基类链配 `interfaces/inner_api/rdb/include/transaction.h` / `src/transaction.cpp`、`src/base_transaction.cpp`

## 1. 角色定位

rdb-kernel 层"新式事务"的唯一实现。RDB 有两套事务 API：老式 `RdbStoreImpl::BeginTransaction()`（rdb_store_impl.cpp:2769，基于 ConnPool 内 `BaseTransaction` 栈 + SAVEPOINT 嵌套）；新式把事务提升为一等对象 `Transaction`——拿到手即可 Insert/Query/Commit，连接归属、生命周期、失败善后全部封装。本文件就是后者从抽象接口到 SQLite `BEGIN/COMMIT/ROLLBACK` 语句的落地层：为什么存在——让上层（napi/taihe/cj/NDK 四套绑定）用统一对象语义驱动物理事务，且接口层（inner_api）不反向依赖实现层。

## 2. 内部结构

继承链只有一级：`Transaction`（transaction.h:35，纯虚 Commit/Rollback/Close/Insert/QueryByStep…）← `TransactionImpl`（transaction_impl.h:27）。`BaseTransaction`（base_transaction.cpp:19）不在这条链上——它是老式栈嵌套的值对象（`GetTransactionStr()` L63：id==0 返回 `BEGIN EXCLUSIVE`，id>0 返回 `SAVEPOINT TRANS_STR<n>`）。`transaction.cpp` 是基类的"适配器仓库"：`BatchInsert(RefRows,Resolution)`(L33) 转调带 ReturningConfig 的重载、`Update(table,...)`(L46) 包装成 AbsRdbPredicates，未实现的默认返回 E_NOT_SUPPORT。

方法分四组：①工厂与生命周期——`Create`(L53，构造后立刻 `Begin`)、`Begin`(L77)、`Commit`(L104)、`Rollback`(L132)、`Close/CloseInner`(L160/L177)；②数据操作——Insert/BatchInsert×3/Update/Delete/QueryByStep×2/Execute/ExecuteExt（L197-325），全是"PerfStat 埋点→`GetStore()` 判活→转发 TransDB"三段式；③辅助——`GetStore`(L182 加锁返回 store_)、`GetLastErrorMsg`(L188)、`AddResultSet`(L268 弱引用登记)。成员六个：`path_`、`seqId_`（PerfStat 全链 id）、`recursive_mutex mutex_`、`store_`（TransDB 门面）、`connection_`、`resultSets_`；SQL 常量在头文件 L70-72（BEGIN_SQLS 按 DEFERRED/IMMEDIATE/EXCLUSIVE 排列）。

## 3. 外部连接

依赖（图谱 imports 边实证）：`connection.h`（`CreateStatement` 执行事务语句）、`trans_db.h`（TransDB :24，继承 RdbStore 但持 `weak_ptr<Connection>`，所有 CRUD 都走事务连接）、`rdb_perfStat.h`/`rdb_trace.h`/`sqlite_utils.h`（匿名化日志）。被依赖：`RdbStoreImpl::CreateTransaction`(rdb_store_impl.cpp:3500) 是唯一生产入口，经 `Transaction::Create`(transaction.cpp:18) 间接分发——`regCreator_` 静态自注册（本文件 L31-32）打破 inner_api→frameworks 的非法依赖，这是典型工厂反转。上游绑定：napi `createTransaction`(napi_rdb_store.cpp:201/2460)、taihe `transaction_impl.cpp`（`Commit()` :41/`Rollback()` :50）、cj FFI（relational_store_impl_rdbstore_extensions.cpp:344）。连接池侧：`ConnPool::CreateTransConn`(connection_pool.cpp:333) 从 `trans_` 容器（MAX_TRANS=4，L191）取连接，`Convert2AutoConn(node,true)`(L205) 包出带自定义 deleter 的 shared_ptr——归还走 `ReleaseTrans`(L1141)，尊重 `IsRecyclable()`。

## 4. 数据流

成功路径：`CreateTransaction`→`CreateTransConn`（trans_ 池空则用与写连接相同的工厂 `Connection::Create(config,true)` 建新连接，L155-158）→`TransactionImpl::Create`→ctor 记 `STEP_TRANS_START`→`Begin(type)`：建 TransDB、取 BEGIN_SQLS[type]、`CreateStatement(beginSql)`→`Execute()`。此后每个 `Insert/Update/Delete` 都经 `GetStore()` 落到同一 `connection_`——原子性即来自"全部语句共用这条连接"。`QueryByStep` 额外把 StepResultSet 塞进 `resultSets_`(L285)。`Commit()`：执行 `COMMIT;`→`CloseInner()`：`store_=nullptr`→`connection_->SetIsRecyclable(true)`→`connection_=nullptr`（shared_ptr 析构触发 deleter→`ReleaseTrans`→连接回 trans_ 池）→遍历 `resultSets_` 逐个 `sp->Close()`(L168-173)。失败路径有两类：业务失败→用户调 `Rollback()`（同构，执行 `ROLLBACK;`）；提交本身失败（建语句/执行出错）→`CloseInner(false)`——`SetIsRecyclable(false)`，连接不回池而被销毁（`total_--`），因为失败后连接的事务状态不可知，复用会污染下一个事务。用户什么都不调→析构函数兜底 `Rollback()`(L41-51，注释明言防止连接残留打开的事务)。

## 5. 设计决策

- **事务独占一条写连接**：SQLite 事务是 per-connection 的，跨连接无原子性；trans_ 容器与 writers_ 分离、上限 4，既不饿死常规写路径又给泄漏上保险丝。
- **幂等收尾**：`CloseInner` 后 `connection_` 为空，再调 Commit/Rollback 返回 E_ALREADY_CLOSED（L110/L138）而非二次执行 SQL；析构在已收尾时直接 return——Commit/Close/析构任意组合都安全。
- **回收位开关而非引用计数**：连接归还与否由 `SetIsRecyclable` 一个 bool 决定，成功路径回收、失败路径销毁，语义压进连接池的 `ReleaseTrans`。
- **弱引用追踪结果集**：`weak_ptr<ResultSet>` 不延长生命周期，但保证事务收尾时能强制关闭仍活着的游标（它们持有连接上的 statement）。
- **PerfStat 全覆盖**：每个入口都挂 `seqId_` 埋点，慢事务可端到端追溯。

## 6. 新人提示

- 切入顺序：transaction.h（读 API 契约）→ 本文件 Commit/CloseInner → connection_pool.cpp 的 CreateTransConn/ReleaseTrans → trans_db.cpp 任一方法。
- 易错点：①事务内 QueryByStep 拿的 ResultSet 在 Commit/Rollback 时被强制 Close，先取数后提交；②忘 Commit 不是自动提交而是自动回滚（析构兜底）；③本事务不支持嵌套，嵌套语义在老式 BeginTransaction（SAVEPOINT 栈）那条线；④Commit 失败后连接被销毁属预期，别当连接池泄漏修。
- 测试：`test/native/rdb/unittest/transaction_test.cpp`、`test/interface/rdb_transaction_test.cpp`、`test/ndk/unittest/rdb_transaction_capi_test.cpp`、`rdb_transaction_query_without_rowCount_test.cpp`，fuzz 见 `transaction_fuzzer`/`ohrdbtransaction_fuzzer`。
