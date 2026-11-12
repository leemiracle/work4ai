# napi_rdb_store.cpp — RdbStoreProxy：relationalStore 的 NAPI 主绑定

> `frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp`（2711 行，配 `include/napi_rdb_store.h`）

## 1. 角色定位

napi-binding 层核心：ArkTS `relationalStore.getRdbStore()` 返回的 `RdbStore` 的 native 实体。注册链：entry_point.cpp:31 模块 Init → `RdbStoreProxy::Init`（:235）用 DefineClass 定义 JS 类。JS 侧 insert/query/事务/订阅全由此承接，向下穿透到 rdb-kernel 的 `NativeRdb::RdbStore`。承担值转换、线程调度、生命周期联动三职责。勿与 `frameworks/js/napi/rdb/` 旧 API 同名文件混淆。

## 2. 内部结构

`RdbStoreProxy : JSProxy<NativeRdb::RdbStore>`（头文件 :41）经 `napi_wrap` 挂到 JS 实例（`Initialize`:241 注册 finalize）。方法四组：

- **注册**：`GetDescriptors`（:168）约 40 个方法，:216/:1620 分别追加 `xxxSync` 与分布式方法。
- **三段式异步**（主力）：`Insert`（:321）、`Update`（:467）、`Query`（:510）等，统一 input/exec/output 三 lambda + `ASYNC_CALL` 模板。
- **同步直调**：`BeginTransaction`（:865）、`Commit`（:945）。
- **事件订阅**：`OnEvent`（:1249）按 `onEventHandlers_` 表（头文件 :144）派发到 `OnRemote`（:1331）等。

Parse* 解析族在 napi_rdb_context；`ParserThis`（:311）拦 `E_ALREADY_CLOSED`；`IsNapiTypeString`（:158）分流重载（string 首参=DataShare 谓词）。

## 3. 外部连接

依赖 JSUtils、AsyncCall（napi_async_call.h）、RdbStoreContext+Parse*、ResultSet/TransactionProxy、五 observer 头、UvQueue；被 entry_point.cpp:34 与 napi_rdb_store_helper.cpp 的 `NewInstance`（:268）依赖。`ParseDataSharePredicates` 为 weak 空实现（:429），dataShare 适配层以强符号覆盖，实现可选裁剪。

## 4. 数据流：`store.insert('EMPLOYEE', values)` 到 SQLite

1. **input（JS 线程）**：`ParserThis` 解包 → `ParseTableName/ParseValuesBucket` → `HasDuplicateAssets` 校验（:330）。
2. **入队**：`ASYNC_CALL` → `AsyncCall::Call`（napi_async_call.cpp:160）：无 callback 则建 promise；`napi_create_async_work`+`napi_queue_async_work_with_qos`（:184-187）进 libuv worker 池。
3. **exec（worker 线程）**：`InsertWithConflictResolution`（:339）→ RdbStoreImpl → SqliteStatement → sqlite3_bind/step；失败取 `GetLastErrorMsg`（:342）带出 SQLite 原始错误。
4. **output（回 JS 线程）**：`napi_create_int64(rowId)`（:347）resolve；失败 `SetBusinessError`（:1978）转 `napi_create_error(code,msg)` 拒绝。

反向流：sync/数据变更经 UvQueue（:293/:1869）投回 JS 线程。

## 5. 设计决策

- **一实现双形态**：insert 与 insertSync 共用 `Insert`（:174/:220），data 指针 `&g_async/&g_sync` 决定形态；Sync 路径（napi_async_call.cpp:205）串行直调并 `napi_throw`。
- **线程纪律**：exec 在 worker 线程绝不碰 napi_*，全部 napi 调用压在 input/output。
- **悬空与泄漏防护**：context 持 `shared_ptr` 拷贝，异步窗口内 close() 不悬空；`Close`（:2436）在 exec 里 `UnregisterAll`（:80）清五类观察者。
- **错误码跨语言**：ParamError→401、InnerError 携内核码统一序列化；关键接口挂直方图打点（:383）。

## 6. 新人提示

- **切入点**：读 `GetDescriptors`（:168）建全景 → 精读 `Insert`（:321-354）→ 补 napi_async_call.cpp；配 DeepWiki 6.1。
- **易错点**：① exec 禁用 napi_*；② exec 先 move(rdbStore) 再取 GetLastErrorMsg（:338-343）；③ Sync 形态同步抛异常需 try-catch；④ 系统应用接口（:1676 等）靠 `IsSystemAppCalled()` 闸门。
- **相关测试**：test/ets 下 RdbStoreExecuteSql、RdbstoreTransactionJsunit、RdbstoreDataChangeEts 等。
