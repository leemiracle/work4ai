# rdb_service_proxy.cpp — RdbServiceProxy 分布式服务 IPC 代理

> `frameworks/native/rdb_service_adapter/src/rdb_service_proxy.cpp`（803 行；声明同目录 `include/rdb_service_proxy.h`）

## 1. 角色定位

属 **native-adapters 层**，RDB 客户端进程到 distributeddata 服务的 IPC 代理：`RdbServiceProxy : IRemoteProxy<IRdbService>`（h L31）。契约链：`RdbService`（`interfaces/inner_api/rdb/include/rdb_service.h` L32-122，30+ 纯虚 + `Option`）→ `IRdbService : RdbService + IRemoteBroker`（`irdb_service.h` L26-29，descriptor `OHOS.DistributedRdb.IRdbService`）。存在原因：应用进程只有本地 SQLite 引擎，分布式同步引擎住在 distributeddata 服务进程，靠 binder 沟通。本文件把 40+ 分布式操作序列化成 IPC 请求，并反向接通服务推送的回调；服务端 stub 不在本仓。

## 2. 内部结构

- **IPC broker 封装**：`IPC_SEND` 宏（L30-53，GCC statement expression）四步——写 InterfaceToken → `ITypesUtil::Marshal` 变参 → `remote_->SendRequest` → reply 首 int32 恒为 status。20+ 命令共享：`ObtainDistributedTableName` L61、`SetDistributedTables` L191、`BeforeOpen` L396（回读 param 协商路径/加密）、`QuerySharingResource` L479、云族 L251/720/655、DFX 族 L750/765/456 等。
- **同步族**：`Sync` L242 按 `option.isAsync` 分派。`DoSync` L121 发 `RDB_SERVICE_CMD_SYNC` 阻塞取 `Details`（带回调版 L142）；`DoAsync` L157/169 用 `GetSeqNum`（L112，atomic 自增跳 0）登记 seqNum→回调进 `syncCallbacks_`（ConcurrentMap），发 `RDB_SERVICE_CMD_ASYNC` 即返。
- **订阅族**：`Subscribe` L262（L268 校验 mode 范围）先 `DoSubscribe` L289 再登记 `observers_`（key=`RemoveSuffix(storeName)` → `list<ObserverParam{weak_ptr<observer>, bundleName, option}>`，h L33-38）；`UnSubscribe` L300 对称。`RegisterAutoSyncCallback` L503 管进度观察者 `syncObservers_`（shared_ptr）。
- **回调通道**：`InitNotifier` L75 new `RdbNotifierStub` 挂三 lambda（seqNum 完成/storeName 完成/数据变更），notifier binder 经 L101 交服务侧长期持有。`OnSyncComplete(seqNum)` L616 回调后 `!finished` 保留条目（支持多次进度）；`OnDataChange` L579 按归一化 store 名分发，非末位观察者复制 `ChangeInfo`（L594）。
- **容灾**：`Export/ImportObservers` L360/370 及 Sync 版 L365/383 迁移订阅；`OnRemoteDeadSyncComplete` L601 给挂起回调补发 UNKNOWN_ERROR 的 SYNC_FINISH；析构 L792 自旋 ≤100×1ms 等 notifier 引用归 1。

## 3. 外部连接

依赖（imports 实证）：`itypes_util.h`、`rdb_notifier_stub.h`、`result_set_proxy.h`、`sqlite_utils.h`（日志脱敏 `Anonymous`）、接口码 `RdbServiceCode`（`distributeddata_relational_store_ipc_interface_code.h` L79+）。创建者：`rdb_manager_impl.cpp` `GetRdbService`——samgr 取 `DISTRIBUTED_KV_DATA_SERVICE_ABILITY_ID` → `GetFeatureInterface("relational_store")`（L195）→ new 代理 + `InitNotifier` + `LinkToDeath`。消费者：`RdbStoreImpl`（`InnerSync` rdb_store_impl.cpp L1055 等 20+ 处）、`rdb_store_manager.cpp`、`sqlite_connection.cpp` L1606。图谱 contains 边收录 Sync/DoSync/DoAsync/Subscribe/RemoteQuery/OnDataChange 等 13 函数节点。

## 4. 数据流：sync(deviceIds, mode) 跨进程链路

1) `RdbStoreImpl::Sync`（rdb_store_impl.cpp L1037）：`SyncOption`→`RdbService::Option`（mode 直传、`isAsync=!isBlock`）→ `InnerSync` L1055 → `GetRdbService`。
2) `RdbManagerImpl::GetRdbService`（rdb_manager_impl.cpp L180+）：samgr→KvDataService→GetFeatureInterface→new 代理→InitNotifier 建回调通道。
3) `Sync` L242 异步走 `DoAsync` L169：分配 seqNum、登记回调、`IPC_SEND(RDB_SERVICE_CMD_ASYNC, param, option, predicates)`——**deviceIds 装在 `PredicatesMemo` 设备列表随谓词序列化**，非独立参数；同步走 `DoSync` L121 等 reply 反序列化 `Details`。
4) 服务侧执行推拉（SyncMode PUSH/PULL/PULL_PUSH/CLOUD_FIRST…，rdb_types.h L156），按 seqNum 经 notifier 回调 `OnSyncComplete(seqNum)` L618 查表触发 `AsyncDetail`，SYNC_FINISH 后条目删除。
5) 服务死亡：`RdbManagerImpl::OnRemoteDied`——ExportObservers → 补偿 → 重取服务 → ImportObservers 重放订阅。
对比 `RemoteQuery` L331：reply 里 `ReadRemoteObject()` 拿结果集 binder 包成 `ResultSetProxy`，空 deleter + sptr 捕获防误删（L357）。

## 5. 设计决策

- **代理模式隔离 IPC**：上层只见 `RdbService*`；`!remote->IsProxyObject()` 时（rdb_manager_impl.cpp L201-204）`isProxy_=false`——RDB 编进服务进程时同一接口直接进程内调用，一套代码两种部署。
- **反向回调独立建模**：请求单向，订阅/进度需服务→客户端推送，故造客户端侧 stub（`RdbNotifierStub`）；数据观察者用 weak_ptr 由 store 生命周期兜底、进度观察者用 shared_ptr，语义刻意不同（h L34/L40）。
- **seqNum + ConcurrentMap 进度模型**：`!finished` 保留条目支持多次进度上报；死亡补偿不丢回调。
- **enableErrorDetail 门禁**（L186）：异步失败默认只回 `RDB_ERROR`，开开关才透传真实错误码。
- **key 归一化**：登记（L275）与分发（L586）都用 `RemoveSuffix`，两处必须同步改否则静默失配。

## 6. 新人提示

- **切入点**：`IPC_SEND` 宏（L30）+ `Sync/DoSync/DoAsync`（L121-189）→ `InitNotifier`/`OnSyncComplete`（L75/616）回调闭环 → `rdb_manager_impl.cpp` `GetRdbService`/`OnRemoteDied` 看代理生死。
- **易错点**：①死亡重订阅不在本文件——改 `ObserverParam` 必须同步改 Import/Export 对（L370/383 重建 param 只回填两字段）；②回调在 `ComputeIfPresent` 持锁内执行，回调里再调 proxy 方法有死锁风险；③`RemoteQuery` 返回的 shared_ptr 是空 deleter，不能 delete 裸指针；④同一 observer 重复 Subscribe 被静默拒绝（L278）只打日志。
- **测试**：`test/native/rdb_service_adapter/unittest/rdb_service_proxy_test.cpp`（`OnRemoteDeadSyncComplete` L119、`DoSync_UnmarshalSuccess` L148、`RequestFullDataDonation` 三例）；`rdb_manager_impl_test.cpp`；端到端 `rdb_distributed_test.cpp`。
