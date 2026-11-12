# sqlite_connection.cpp 精讲 — SQLite 连接实体与全量配置中枢

> `frameworks/native/rdb/src/sqlite_connection.cpp`（2591 行，配 include/sqlite_connection.h）

## 1. 角色定位

`Connection` 抽象接口的 SQLite 实现，是 ConnectionPool 调度下的连接实体：connection_pool.cpp 管分配回收，本文件管连接的全部职责——打开配置、加密换钥、语句创建、检查点、主备双写、备份恢复。它还是工厂注册方：L84-104 静态注册量把 Create/Repair 登记进 `Connection::RegisterCreator(DB_SQLITE,...)`，池层 `Connection::Create` 经此路由到本文件——"池不知引擎"。

## 2. 内部结构

单类，核心成员 `dbHandle_`、`isWriter_/isReadOnly_`（L350，独立两标志）、`slaveConnection_`。五组：

- **打开与配置**：`Create`(L106)→`InnerCreate`(L2026)→`InnerOpen`(L337)：`CheckDbNotExist`(L318)→`OpenDatabase`(L390，open_v2+FULLMUTEX)→`Configure`(L490) 依序设 busy_timeout/权限/PERSIST_WAL/加密/journal/autocheckpoint/函数/扩展，写连接再做 integrity_check(L370-386)。
- **执行原语**：`ExecuteSql`(L1291)/`ExecuteForValue`(L1300)；`CreateStatementInner`(L661) prepare 出 SqliteStatement，双写且非 binlog 时备库同步 prepare 镜像。**事务原语不在本文件**——BEGIN/COMMIT 由上层 Transaction 在独占连接上执行，"事务=普通语句+独占连接"是钥匙。
- **检查点**：`TryCheckPoint`(L1395) 分级——小于 `GetStartCheckpointSize()` 直接返回，两级之间且非超时返回 E_INNER_WARNING；执行时 busy_timeout 临时降 500ms 跑 TRUNCATE。
- **加密**：`SetEncrypt`(L1045) 三段兜底：应用密钥→新密钥→服务侧密钥(L1587)；`SetEncryptKey`(L1098) 后读 user_version 验证 codec；Rekey 支持密文↔明文。
- **主备双写**：`InnerCreate` 对写连接自动建备库(L2042，HaMode!=SINGLE)；Backup/Restore→`ExchangeSlaverToMaster`(L1628)→`SqliteNativeBackup`(L1715) 分步重试；另有 SetBinlog/ReplayBinlog/Interrupt。

## 3. 外部连接

依赖（L30-53 实证）：SQLite C API 与定制扩展 `relational_store_sqlite_ext.h`（binlog/hook）；单例 RdbSecurityManager（HKS 密钥）、RdbICUManager、DistributedRdb::RdbManager、TaskExecutor；伴生 SqliteStatement。被依赖：经 Connection 抽象被 connection_pool.cpp 消费。

## 4. 数据流

打开写连接：池 Init→creator→InnerCreate→InnerOpen→Configure→integrity_check→建备库+SetBinlog；任一步失败整条作废，错误码回池。写语句：池拿连接→CreateStatementInner 主备双 prepare→Execute。checkpoint：池 ReleaseNode 无在途事务时触发 TryCheckPoint(true)→实测 WAL 大小→超阈 TRUNCATE。

## 5. 设计决策

- **FULLMUTEX 是全局前提**：连接可跨线程共享，支撑池 AcquireRef 借用语义，互为因果。
- **PRAGMA 先读后写再验证**：`SetJournalMode`(L1170) 不同才设置，且 L1200 校验设置后返回值，不信 SQLite 静默失败；SetPageSize 同款。
- **PERSIST_WAL + user_version 写入 WAL**(L1125)：WAL 常驻避免删除重建引发权限漂移。
- **密钥零残留**：三段兜底之外，密钥 vector 用完 `assign(size,0)` 抹除（十余处）。
- **阈值与 busy 分层**：checkpoint 两级阈值+池侧 5 分钟冷却；busy 默认 2000ms、checkpoint 降 500ms。

## 6. 新人提示

- 切入点：先读 `InnerOpen`→`Configure`(L337-546)，即"RDB 打开时发生了什么"的权威答案。
- `isWriter_`≠`isReadOnly_`：只读库的写连接两标志同真，Set* 多以此开头 `if (isReadOnly_) return E_OK`。
- `slaveConnection_` 三处创建（InnerCreate/Backup/L2116），`ReleaseTempSlaveConnection`(L1784) 只释放临时那份，排查双写先确认来源；
- ExecuteSql/ExecuteForValue 是 protected，外部必须走语句路径。
- 测试：`connection_test.cpp`、`rdb_encrypt_decrypt_test.cpp`、`rdb_double_write*_test.cpp`、`rdb_store_backup_restore_test.cpp`。
