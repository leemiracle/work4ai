# relational_store.cpp — NDK C API 主出口（C/C++ 应用的 RDB 大门）

> `interfaces/ndk/src/relational_store.cpp`（1660 行）；契约 `interfaces/ndk/include/relational_store.h`（1794 行），产物 `libnative_rdb_ndk.so`

## 1. 角色定位

属 10 层架构的 **ndk-c-api 层**，四条对外出口（NAPI/Taihe/NDK/Cangjie）中唯一的纯 C ABI 路线，供游戏/高性能 native 应用直接链 so。与 NAPI/Taihe 的区别：无脚本运行时，调用即进 native——参数校验、类型甄别、内存契约全在本层自理，ABI 不可变（`RDB_CONFIG_SIZE_V0=41/V1=45` 是版本化石，L49-50）。图谱入边为 0，链路最外层。

## 2. 内部结构

C ABI 函数族七组：**ConfigV2 构建族**（L60-282）`CreateConfig` 加 14 个 `OH_Rdb_Set*`，每个先查 `magicNum` 再做枚举域校验（L141 的 S1-S4）；**对象工厂族**（L284-300）new 出 `RelationalPredicate/RelationalValuesBucket` 等；**开关库族**（L415-536）V1 `OH_Rdb_GetOrOpen`（selfSize 前向兼容）与 V2 `OH_Rdb_CreateOrOpen`（magicNum 校验 L455）；**CRUD 族**（L538-598，WithReturning 版 L1582）；**查询族**（L600-697）全落 `QueryByStep` 分步游标；**SQL/事务族**（L699-773）含 trxId 三件套；**分布式/云同步/损坏回调族**（L829-1566）。支撑类：`RelationalStore`（继承 `OH_Rdb_Store`，relational_store_impl.h L80，构造打 `id=RDB_STORE_CID` L304）、空回调 `MainOpenCallback`（L390）、观察者 `NDKCorruptHandler/NDKStoreObserver`（L1252/L1323）与手工管 malloc/free 的 `RelationalProgressDetails`（L942）。

## 3. 外部连接

依赖（图谱 26 条 imports）：`RdbHelper::GetRdbStore` 开真库；`RdbSqlUtils::GetDefaultDatabasePath` 拼真实路径；V2 配置转换 `RdbNdkUtils::GetRdbStoreConfig`（L462，rdb_ndk_utils 工具族）；结果包装 `RelationalCursor`（L620）与 `ModifyTimeCursor`（L869）；损坏回调挂 `CorruptedHandleManager::Register`（L1536）。被依赖：仅 `test/ndk/unittest/` 与 fuzzer。

## 4. 数据流

`OH_Rdb_Execute`（L699）：判空 → `GetRelationalStore`（L406）验 CID 后 static_cast → `GetStore()->ExecuteSql(sql, {})` → 内核 `frameworks/native/rdb/src/rdb_store_impl.cpp:2042` → `ConnectionPool` → `SqliteConnection::ExecuteSql`（sqlite_connection.cpp:1291）→ SQLite，错误码经 `NativeToNdk` 返回。查询流：`OH_Rdb_Query`（L600）→ `QueryByStep`（L616，不预取行数）→ `RelationalCursor` 包装 → 用户按 `OH_Cursor` 函数指针协议（oh_cursor.h L57）逐行消费。反向流：云同步回调（L1066）打包 `RelationalProgressDetails` 回调用户（L1077）；`NDKStoreObserver::OnChange`（L1364）单块 buffer 打包 `Rdb_ChangeInfo`（L1409）。

## 5. 设计决策

- **类型甄别指针**：`OH_Rdb_Store` 只暴露首字段 `id`（头文件 L157-162），`RelationalStore/RelationalCursor` 靠 CID（1234560/1234563）自证防混传。
- **前向兼容双轨**：V1 用 `selfSize` 判代际（L417 拒超新、L434 `>41` 才读 area），V2 改 magicNum。
- **内存所有权**：Create*/Destroy 与 `cursor->destroy` 配对；`GetTableDetails` 缓冲由析构统一 free（L974）。
- **订阅幂等**：观察者按 `context+callback` 地址判等（L1441）去重；损坏回调 `isExecuting.exchange`（L1306）防递归。
- **返回值演进**：老函数行数与错误码混用一个 int（L547），新函数一律错误码出参。

## 6. 新人提示

按 `CreateConfig → CreateOrOpen → Insert → Query → CloseStore` 主线跳读覆盖 80% 场景。易错：①cursor 忘 `destroy` 即泄漏 ResultSet；②`CloseStore` 只 delete 包装层，内核 store 由 `RdbHelper` 缓存，同库重开复用连接；③V1/V2 别混函数；④新增导出函数须继承「判空+magicNum」防御并同步 versionscript；⑤云同步回调里的进度结构仅回调期有效。测试 `test/ndk/unittest/`；对照本目录 `rdb_store.h.md`。
