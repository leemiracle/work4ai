# connection_pool.cpp 精讲 — RDB 并发访问的中枢

> `frameworks/native/rdb/src/connection_pool.cpp`（1343 行）+ `include/connection_pool.h`

## 1. 角色定位

rdb-kernel 层的并发调度中枢。调用链 `RdbStoreImpl → ConnectionPool → Connection(抽象) → SqliteConnection`：上层把 SQL 操作翻译为"拿连接→执行→归还"，本文件回答连接从哪来、给谁用、何时还。SQLite 连接昂贵且并发受限（写串行），池化+读写分离摊薄代价——`AcquireConnection(isReadOnly)` 一行拿连接，`shared_ptr` 析构自动回池。池只依赖 `connection.h` 抽象，多引擎共用同一套池逻辑。

## 2. 内部结构

三层嵌套：`ConnectionPool` → 四个 `Container` → `ConnNode`。`Init`(L142) 分工：`writers_` 恒 1 条写连接；`readers_` 容量由 `GetMaxReaders`(L195) 决定——非内存库且 WAL 才取 `config.GetReadConSize()`（默认 4），否则 0 退化单连接；`trans_` 事务连接 `MAX_TRANS=4` 惰性扩容；`temps_` 临时连接。

`Container` 是通用并发容器：`Acquire`(L932) 空闲即弹出，否则 `ExtendNode`(L984) 先解锁再建连（SQLite open 慢不能持锁）；`Release`(L1118) 校验 id 水位防旧节点回池。`ConnNode::GetConnect`(L791) 记录 `tid_/time_` 供追责。获取侧另有 `AcquireRef`(L431，ResultSet 借用)、`CreateTransConn`(L333)、`AcquireAll`(L355 独占)、`AcquireAndDisableTrans`(L307 备份前置)；生命周期含 `Create`(L63) 工厂、`HandleDataCorruption`(L94) 自愈、恢复与 Rekey 族。`ClearUnusedTrans`(L1289) 每 150s 回收空闲事务连接。

## 3. 外部连接

依赖（L19-38 实证）：`connection.h`（抽象+静态工厂注册表）、`base_transaction.h`、`delay_actuator.h`、`rdb_errno.h`、`sqlite_utils.h`、`task_executor.h`、`rdb_fault_hiview_reporter.h`。被依赖：生产代码唯一消费者 `rdb_store_impl.cpp`——`AcquireConnection`、`AcquireRef`、`CreateTransConn`(L2816/3513)、`AcquireAndDisableTrans`(L128/2456)、`GetTransactionStack/SetInTransaction`；图谱入边仅文档节点。

## 4. 数据流

读查询（WAL）：`AcquireConnection(true)`(L348)→`Acquire`(L419) 选 `readers_` 弹节点→`Convert2AutoConn`(L205) 包成自动归还的 shared_ptr→上层 CreateStatement 执行→析构触发 `ReleaseNode`(L454) 归还容器。

写事务：`RdbStoreImpl::CreateTransaction`(impl:3513)→`CreateTransConn()`(L333)：超 `MAX_TRANS` 报 E_DATABASE_BUSY 并 Dump；`Transaction::Create` 发 BEGIN...COMMIT→归还 `ReleaseTrans`(L1137)：`IsRecyclable()` 为真才回池，否则销毁。

## 5. 设计决策

- **1 写 + 4 读**：WAL 下 SQLite 仍单写者，多写连接徒增 SQLITE_BUSY；读并发收益只在 WAL 存在，非 WAL 返回 0。`MAX_TRANS=4` 是事务连接泄漏的保险丝。
- **单写者锁双重形态**：`AcquireTransaction`(L486) 用 `transactionUsed_`（2s 超时）做进程级单写闸——grep 实证生产已不调用（仅测试引用），单写约束如今由 `writers_` 容量 1 承担。
- **AutoConn 弱引用**：deleter 捕 `weak_from_this()`，池先死也不悬垂。
- **checkpoint 时机**：`ReleaseNode` L460-465 只在 `remainCount<=0`（无在途事务）时 TryCheckPoint，失败后 5 分钟冷却。
- **busy 三梯**：Container `wait_for` 超时→E_DATABASE_BUSY；池层超时即 `Dump`(L1248，含每节点 id/tid/持有 ms) 上报 HiView 定位长事务；`AcquireAll` 部分失败整体放弃。

## 6. 新人提示

- 切入点：沿 `Container::Acquire`→`Convert2AutoConn`→`ReleaseNode` 一条线读完即掌握 80% 语义。
- `AcquireRef` 借用语义(L431)：非 WAL 下取出写连接裸指针后立刻归还节点——多个 ResultSet 共享同一条写连接，依赖 `SQLITE_OPEN_FULLMUTEX` 保证安全。
- 连接泄漏：trans 连接忘还要等 150s 回收，期间备份超时——看 Dump 日志哪个 tid 长期持有。
- 测试：`connection_pool_test.cpp`、`rdb_store_impl_test.cpp`(L602-638)、`multiThread/`、`rdb_store_backup_restore_test.cpp`。
