# rdb_store.h — RdbStore 抽象接口契约（全部件的 API 心脏）

> `interfaces/inner_api/rdb/include/rdb_store.h`（938 行）

## 1. 角色定位

属 10 层架构的 **interface-definitions 层**，部件唯一对全系统发布的关系型数据库契约。往下，rdb-kernel 层的 `RdbStoreImpl`（SQLite 全量实现）与 `TransDB`（事务内单连接实现）继承它；往上，NAPI/Taihe/Cangjie/NDK 四出口全围绕它做类型映射——应用见到的每条 RDB API 追到底是本文件一个 virtual 方法。存在意义：让绑定层与实现层在一份稳定契约下解耦并行演进。

## 2. 内部结构

**类型别名区（L44–L133）**：把 `DistributedRdb` 的 `SyncOption/AsyncDetail/SubscribeMode/RdbStoreObserver/PRIKey` 借入本命名空间（不泄漏分布式头文件）；定义业务词 `Fields/Olds(旧string,淘汰)/Values(vector<ValueObject>)/Row=ValuesBucket/Rows/RefRows/Resolution`。

**嵌套类 ModifyTime（L135–L151）**：`GetModifyTime()` 的返回包装，靠隐式转换算子（L140）支持按 `map<PRIKey,Date>` 或 `ResultSet` 消费，兼容 rowId 与 hash 两种主键形态。

**虚接口分组**：Insert 组 L167–L235——新式 pair 签名 `Insert(table,row,resolution)`（L167）、旧出参版（L175）、deprecated 版（L184）、`BatchInsert`×4（Returning 版注释警示 1024 行截断）；Update/Delete 组 L246–L365；Query 组 L380–L476——谓词 `Query`（L391）、唯一纯虚 `QuerySql=0`（L408）、`QueryByStep`×4；Execute 组——主力 `Execute(sql,args,trxId)`（L494）；事务组 L588–L614——推荐 `CreateTransaction`（L588），旧式三件全弃用，向量库走 `BeginTrans→trxId`（L595）；分布式组 L693–L794（`SetDistributedTables/Sync×3/订阅四件套`）；加密备份 `Backup/Restore/Rekey`（L547/678/641）；运维 `Count`、`GetVersion/SetVersion`（L578/583，纯虚）、`Attach/Detach`（L854/863）、`Release`（L665，L653 三旋钮含 interrupt）及 FTS/保护级钩子（L891–L929）。

## 3. 外部连接

imports 仅 13 个契约头（predicates/result_set/values_bucket(s)/transaction/rdb_store_config/rdb_errno 等），不碰内核——四出口共享的前提。被依赖（图谱入边实证）：四出口共 11 文件；内核侧 `rdb_store_impl.h`、`trans_db.h`（`inherits` 边）、`rdb_helper.h`、`rdb_open_callback.h`。实现谱系：`RdbStoreImpl` 与 `TransDB`（transaction_impl.cpp:80 实例化，仅覆写约 14 法）；非纯虚默认实现在 `frameworks/native/rdb/src/rdb_store.cpp`（778 行），大多直接返 `E_NOT_SUPPORT`。

## 4. 数据流

JS `insert`：NAPI 解 `ValuesBucket`→虚表分发到 `Insert`（L167）→返 `pair<int,int64_t>`（错误码+rowId），映射为 JS error 与返回值。查询区分两种消费模型：`Query`（L391）返共享内存结果集，`QueryByStep`（L426）返步进结果集。谓词自带 `GetDistributedPredicates()` 出口，`Sync`（L738）复用为远端同步条件。`GetModifyTime`（L820）可赋给 map 或 ResultSet。

## 5. 设计决策

- **仅 3 个纯虚**（`QuerySql` L408、`GetVersion/SetVersion` L578/583），其余默认 `E_NOT_SUPPORT`：窄实现按需覆写，新增 API 不逼旧子类改写，契约演进成本最小。
- **`[[deprecated]]` 驱动演进**：主线是出参→pair、`Olds`→`Values`、裸 whereClause→谓词对象、事务栈→`CreateTransaction` RAII。
- **错误码契约**：全用 `E_*` 整数码而非异常，适配跨 FFI/IPC 边界。
- **别名层防腐**：分布式类型经 using 引入；边界写进注释即契约。
- **无 capability 查询**：不支持的能力直接返 `E_NOT_SUPPORT`，由调用方探测。

## 6. 新人提示

先读 L44–L133 别名区再读方法，按 Insert→Query→CreateTransaction 三主线跳读覆盖 80% 用法。易错：①重载多（`Insert`×3、`BatchInsert`×4），接旧版有弃用警告；②子类漏实现纯虚 `QuerySql` 直接编译失败；③新代码一律 `CreateTransaction`；④`ReleaseOption.interrupt=true` 会打断占用者。测试：`rdb_store_impl_test.cpp`、`rdb_trans_db_test.cpp`（unittest/）。动此头需同步过四出口。
