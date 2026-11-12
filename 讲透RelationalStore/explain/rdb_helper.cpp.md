# rdb_helper.cpp — RdbHelper：应用侧打开/删除数据库的门面

> `frameworks/native/rdb/src/rdb_helper.cpp`（193 行，配 `interfaces/inner_api/rdb/include/rdb_helper.h`）

## 1. 角色定位

rdb-kernel 层（frameworks/native/rdb）最外圈门面，所有语言栈 getRdbStore 的最底层收敛点。grep 实证四路调用：napi/relationalstore（:105/164）、napi/rdb（旧 API，带 onCreate/onUpgrade）、ets/taihe、frameworks/cj。全文件不碰 sqlite3，价值在**组合**：全局初始化、损坏处理、故障上报收拢一处，开库委托 `RdbStoreManager` 单例，避免四套绑定各自编排漂移。

## 2. 内部结构

三组静态方法：

- **生命周期**：`GetRdbStore`（:39-57）、`Init`（:65）、`Destroy`（:72-97，清全局资源）、`GetRdb`（:163，只查缓存不 Init）。
- **删除**：`DeleteRdbStore`（:104/:119）——name 版三连删磁盘/内存/向量库同名形态。
- **能力查询**：`IsSupportArkDataDb`（:168）、`IsSupportedTokenizer`（:177）。

主方法五步：① InitSqliteGlobalConfig（:43）；② PauseCallback（:44 防误触损坏回调）；③ 委托 Manager::GetRdbStore（:45）；④ ResumeCallback；⑤ E_SQLITE_CORRUPT 转 HandleCorrupt（:47），失败 ReportFault 上报（:50-54，路径匿名化）。删除：内存库 `Remove`（:128），磁盘库 `Delete`+`DelAllKeyFiles`（:133-144）。

## 3. 外部连接

依赖 rdb_store_manager.h（开库+实例缓存，最重边）、sqlite_global_config.h、corrupted_handle_manager.h、rdb_fault_hiview_reporter.h、rdb_security_manager.h、global_resource.h、security_policy.h（:29 平台宏）。返回抽象 `shared_ptr<RdbStore>`，门面签名稳定。

## 4. 数据流：getRdbStore(context, config) 到拿到实例

1. **input（JS 线程）**（napi_rdb_store_helper.cpp:76）：argv[0]→`ContextParam`（baseDir/bundleName），argv[1]→`RdbConfig`；`GetRealPath`（napi_rdb_js_utils.cpp:560）算路径——dataGroupId→`GetSystemDatabaseDir`，rootDir→`GetCustomDatabasePath`，默认 `GetDefaultDatabasePath`。**Context 在此被消费成纯路径**。
2. **exec（worker 线程）**：`GetRdbStoreConfig`（napi_rdb_js_utils.cpp:610）译成 native `RdbStoreConfig` → `RdbHelper::GetRdbStore(cfg, -1, DefaultOpenCallback, errCode)`（:105）。version=-1+空回调：新 API 弃用 onCreate/onUpgrade。
3. **Manager**（rdb_store_manager.cpp:95）：`GetDbPath` 复算路径 → `CheckConfig` → 漂移检测（:107）→ `GetStoreFromCache`（:56-93）：`storeCache_`（path→weak_ptr）命中同配置**复用同一 RdbStoreImpl**，过期重建，漂移报 E_CONFIG_INVALID_CHANGE → ACL 判定（:118）→ `Init`（:126）打开 SQLite。
4. **output（JS 线程）**：`RdbStoreProxy::NewInstance` 包装回 JS，交接给 napi_rdb_store.cpp。

## 5. 设计决策

- **Facade 无状态**：全静态零成员，缓存全在 Manager 单例，多语言绑定共享。
- **路径 key+weak_ptr**：同路径同配置二次打开免重建；引用归零自动允许重建。
- **配置漂移拦截**：加密/安全等级变更直接报 `E_CONFIG_INVALID_CHANGE`，共库一致性底线。
- **多进程可见性**：OWNER/VISITOR 与代理 ACL 都在 Manager 层（:118-123），Helper 无感知。
- **损坏自愈**：Pause/Resume 防误报；三连删=同名所有库形态消失；`Destroy` 单点失败不中断。

## 6. 新人提示

- **切入点**：先通读 193 行 → Manager 的 GetStoreFromCache → RdbStoreImpl::Init；NAPI 侧对照 napi_rdb_js_utils.cpp。
- **易错点**：① 同路径换配置再开会 WARN 或报错，非缓存 bug；② `DeleteRdbStore` 传文件名非全路径；③ `GetRdb`≠`GetRdbStore`（前者不 Init）；④ GetDbPath 在 Helper（:123）与 Manager（:96）各调一次，须同 config 才同文件。
- **相关测试**：test/ets 的 RdbStoreGetRdbStoreSyncEts、test/native/rdb/unittest；配 DeepWiki 2.2。
