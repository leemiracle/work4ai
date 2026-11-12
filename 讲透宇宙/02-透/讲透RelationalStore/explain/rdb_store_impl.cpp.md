# rdb_store_impl.cpp — RdbStoreImpl 门面实现

> `frameworks/native/rdb/src/rdb_store_impl.cpp`（3806 行；声明 rdb_store_impl.h）

## 1. 角色定位

属 **rdb-kernel 层**，`rdb_store.h` 契约的 SQLite 全量实现。定位是门面：把本地 SQL 执行、分布式云同步（RdbService 代理）、可靠性与加密（主备双写/Rekey）收进一个类，NAPI/Taihe/NDK 出口只面对 `RdbStore*`。实例化在 `rdb_store_manager.cpp` L64/71/89：按路径 weak_ptr 缓存，config 不一致报 `E_CONFIG_INVALID_CHANGE`。

## 2. 内部结构

- **生命周期（L1542–L1736）**：`Init()`（L1659）开机主入口；`CreatePool`（L1617）遇 `E_SQLITE_CORRUPT` 先 `TryAsyncRepair`（L1589）再重建；随后 `ExchangeSlaverToMaster()`（L3466）、`ProcessOpenCallback`（L1550 分派 OnCreate/OnUpgrade/OnOpen）、`InnerOpen()`（L170）；`Release`（L284）限时排空硬关闭；`AfterOpen` 异步化（L381）+`WaitAfterOpen()`。
- **CRUD/查询/Execute（L1755–L2280）**：`Insert`（L1755）委托 `ExecuteForLastInsertedRowId`（L2223）；`BatchInsert`（L1778）按 `GetMaxVariable()` 切批；Returning 版三接口（L1841/1908/1930）强制单组 SQL 保原子（L1863）；`QuerySql` 加读引用即返 `SqliteSharedResultSet`（L1966）；`Execute`（L2078）按 sqlType 分派（DDL→`HandleSchemaDDL` L2013）。
- **事务**：旧式 `BeginTransaction/Commit`（L2769/2932）操作池内事务栈；向量库 `BeginTrans→trxId`（L2805）绑专连接；`CreateTransaction`（L3500）产出 RAII 事务。
- **备份/加密（L2282–L2722）**：`Backup`（L2324）进程锁+.tmp 防半写；`InnerBackup`（L2397）=ATTACH→EXPORT→DETACH；`Rekey`（L844）停同步换密钥；`Attach`（L2633）先 `DisableWal`。
- **分布式/通知（L603–L1539）**：`SetDistributedTables`（L707）灌 `syncerParam_` 交 service；`Sync` 收敛到 `InnerSync`（L1055）；`DoCloudSync`（L3065）配 `CloudTables` 200ms 去抖云同步。

## 3. 外部连接

39 个 include 分五束：执行链（connection_pool 等）、分布式代理（rdb_service，`GetRdbService` 20+ 次）、结果集三形态、通知异步、DFX 安全。被依赖：`rdb_store_manager.cpp` 实例化缓存；NAPI/Taihe/NDK/data_share 经 `shared_ptr<RdbStore>` 间接触达（门面价值）。

## 4. 数据流

**Insert(table,row)**：L1755 拒只读→`ExecuteForLastInsertedRowId`（L1770）→`GetStatement(sql,false)`（L3380 拿写连接；slave 恢复中则 L3341 降级 `CreateReplicaStatement`）→落 SQLite（触发变更回调→`DelayNotify`）→返 rowId→`DoCloudSync`（L1773）200ms 去抖同步，一次插入最多一班车。

**QuerySql**：L1951 只加读计数即返 `SqliteSharedResultSet`；取数在游标推进时借读连接、取满即还。

## 5. 设计决策

- **门面+委托**：不碰 sqlite3 句柄，全经 Pool→Connection→Statement；分布式一律 service 代理，门面专心横切（统计/通知/去抖）。
- **读写分治**：读多连接并发（WAL）、写单连接串行（单写者）；`BeginExecuteSql`（L2472）纠偏：只读语句占写连接立即改借读连接。
- **错误码稳定**：`E_NOT_SUPPORT/E_ALREADY_CLOSED/E_DATABASE_BUSY`；`E_SQLITE_BUSY` 统一 `TryDump`（L3611）。
- **异步等待点**：后台任务走 TaskExecutor；`WaitAfterOpen()`（L439）收敛注册与关闭竞态。
- **主备双写 HA**：`slaveStatus_`+binlog 重放（L3756），坏库备库顶上；入口 HITRACE、慢查询打点、日志匿名化、密钥用后即擦（L1635）。

## 6. 新人提示

从 `Init()`（L1659）读生命线，再走 `Insert→GetStatement` CRUD 链。易错：①池随时可能被 Close/Release 置空，长用路径须持 shared_ptr 快照；②三套事务 API（栈式/trxId/CreateTransaction）别混用；③`config_` 是 `*configHolder_` 引用（L344），拷贝危险。测试（unittest/）：`rdb_store_impl_test.cpp`、`mockservice/`、`rdb_store_backup_restore_test.cpp`。
