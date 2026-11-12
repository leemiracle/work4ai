# taihe rdb_store_impl.cpp — ArkTS Taihe IDL 的 RdbStore 直通层（ANI 原生实现）

> `frameworks/ets/taihe/relational_store/src/rdb_store_impl.cpp`（1682 行）；契约源头 IDL `frameworks/ets/taihe/relational_store/idl/ohos.data.relationalStore.taihe`（`interface RdbStore` L753）

## 1. 角色定位

属 10 层架构的 **arkts-taihe 层**（2025），ArkTS 走 ANI 直连 native 的 RdbStore 实现，与 NAPI 路线（`frameworks/js/napi/.../napi_rdb_store.cpp`，手工 `napi_value` 编解码）平行并存，面向 ArkTS 静态类型/AOT：签名直接用 C++ 视图类型与 holder（`weak::RdbPredicates`）。谁用：import `@ohos.data.relationalStore` 的 ArkTS 应用，store 方法全落到本文件。图谱入边为 0，仅被 IDL 生成文件构造。

## 2. 内部结构

单类 `RdbStoreImpl : public ThreadSafeBase<NativeRdb::RdbStore>`（rdb_store_impl.h L42，基类 `shared_mutex` 保护 `resource_`）。方法分组：CRUD 核心是 `InsertWithConflict`（L137），IDL 三个 insert 重载在此漏斗汇合；查询族返回 `ResultSet` 或轻量 `LiteResultSet`（L326 关 preCount）；DataShare 通道经 `RdbUtils::ToPredicates` 转换；SQL/事务 `ExecuteWithTxId`（L609）钉住同一连接；分布式/云同步 `Sync/SyncEx`（L835/L870）加四形态 `CloudSync*`；观察者 On*/Off*（L1046-1293）五类；Attach/行级锁/Returning/Rekey（L1313-1521）；收尾 `CloseSync`（L1303）→ `UnRegisterAll`（L1622）批量注销。错误全靠 `ASSERT_THROW_*` 宏族抛 ArkTS 异常，替代返回码。

## 3. 外部连接

依赖（图谱 21 条 imports）：类型转换中枢 `ani_rdb_utils.h`（`MapValuesToNative` L143、`GetNativePredicatesFromTaihe` L195）；异步骨架 `ani_async_call.h`；包装与观察者 `ResultSetImpl/TransactionImpl/taihe_*_observer`；内核 `RdbHelper::GetRdbStore`（L93）。被依赖：`ohos.data.relationalStore.impl.cpp` 的 `GetRdbStoreInner`（L68）构造本类并注册进 ANI 运行时（L305）。

## 4. 数据流

同步链：ArkTS `store.query(predicates, columns)` → IDL 骨架解参 → `Query`（L273）→ `GetResource()`（shared_lock 快照）→ `GetNativePredicatesFromTaihe` 还原谓词 → `store->Query`（L285）→ `make_holder<ResultSetImpl, ResultSet>`（L288）。异步链（`Sync` L835）：建 promise → `store->Sync` 注册 lambda → 回调线程 `env_guard` 重取 `ani_env`（L852）→ `AniAsyncCall::ReturnResult` resolve。构造链：ctor（L76）→ `RdbHelper::GetRdbStore`（L93）→ `SetResource`，失败抛错并 `ResetResource`（L96）。

## 5. 设计决策

- **双轨并存**：NAPI 保存量 JS 生态；Taihe 用 IDL 生成样板（`TH_EXPORT_CPP_API` 自动注册），类型编解码收敛进 `ani_rdbutils` 一处。
- **重载漏斗**：三个 Query 变体（L257-271）归一到 `Query`，防行为分叉。
- **ThreadSafeBase**：close 后 `GetResource()` 得 null → 统一抛 `E_ALREADY_CLOSED`（L107）；观察者由 `UnRegisterAll`（L1622）兜底注销。
- **isSystemApp_ 闸门**（L82）：DataShare 谓词、`RequestFullDataDonation`（L777）等一律 `ASSERT_THROW_NON_SYSTEM_ERROR`。
- **错误模型**：整数码出口 ThrowError 成 BusinessError，比 NDK 的 int 返回更贴 try/catch。

## 6. 新人提示

先读 IDL `interface RdbStore` 建立「ArkTS ↔ C++ 方法名」映射直觉，再按 ctor → `InsertWithConflict` → `Query` → `Sync` 四站跳读。易错：①native 回调线程操作 ANI 对象前必须 `env_guard`（L852/L887），漏掉即崩；②谓词是 `weak::RdbPredicates` holder，对象已回收时转换失败抛 ParamError（L283）；③`HasDuplicateAssets` 校验散布多处（L144/L595），新写路径记得带；④订阅必须 Off；⑤新 API 要同时改 IDL、本文件与 napi_rdb_store.cpp。测试 `test/ets/relational_store*/`（`RdbQueryByStep.test.ets` 等）。
