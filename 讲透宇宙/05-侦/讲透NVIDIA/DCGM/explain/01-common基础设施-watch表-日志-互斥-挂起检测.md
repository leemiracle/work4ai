# 01 · common 基础设施：watch 表采集节拍 + 日志/互斥/挂起检测

## 角色定位

common/ 是全仓被依赖最深的地基：按图谱 fingerprints 口径共 **189 个文件，占 1178 基线的 16%**，hostengine、dcgmlib、全部 modules、nvvs 诊断套件都直接链它。核心四件套：DcgmWatchTable（字段订阅调度表，决定"什么时候采哪个字段"）、DcgmLogging（plog 日志门面）、DcgmMutex（带超时与持有者诊断的互斥锁）、HangDetect（进程/线程挂起检测）。它是"采集节拍"这一 DCGM 核心语义的第一定义处。

## 内部结构

**watch 表**以三元组为键：`dcgm_entity_key_t`（common/DcgmWatchTable.h:52-58，注释标明 8 字节：entityId + fieldId + entityGroupId），配套 std::hash 特化把三元组打包进一个 uint64（DcgmWatchTable.h:64-71，entityId<<32 | fieldId<<16 | entityGroupId）。每个 watch 记录为 `dcgm_watch_info_t`（DcgmWatchTable.h:80-107），含 lastQueriedUsec / updateIntervalUsec / maxAgeUsec 与观察者向量；每个观察者自带独立间隔与最大年龄（`dcgm_watcher_info_t`，DcgmWatchTable.h:40-48）。存储就是一张 unordered_map（m_entityWatchHashTable，DcgmWatchTable.h:315）。节拍求解在 GetFieldsToUpdate（DcgmWatchTable.cpp:292-345）：遍历 hash 表，age < updateInterval 则记下 nextUpdate 继续睡（DcgmWatchTable.cpp:318-323），到期者经 DcgmFieldGetById 校验后收入 toUpdate（DcgmWatchTable.cpp:326-331）。多观察者聚合在 UpdateWatchFromWatchers（DcgmWatchTable.cpp:245-280）：updateInterval 与 maxAge 都取观察者的 **min**。

**互斥**：DcgmMutex 构造即带 timeoutMs（common/DcgmMutex.h:68），Lock 宏携带 __FILE__/__LINE__（DcgmMutex.h:93-94），实现是 100us 步进自旋 + 超时报错并打印持有者 tid（DcgmMutex.cpp:111-172）；RAII 封装 DcgmLockGuard 标注 [[nodiscard]]（DcgmMutex.h:174），条件等待走 CondWait（DcgmMutex.h:142）。**日志**：双通道 BASE_LOGGER/SYSLOG_LOGGER（common/DcgmLogging.h:92-95），DCGM_LOG_* 直通宏（DcgmLogging.h:107-112）与 IF_DCGM_LOG_* 惰性求值宏（DcgmLogging.h:114-119）；plog 1.1.4 的宏与 syslog 冲突必须在 syslog 之前 include（DcgmLogging.h:22-23）。**挂起检测**：HangDetect 按进程/线程注册指纹（common/HangDetect.cpp:97-131 RegisterTask），核心判定 IsHungImpl 比对当前指纹与存量指纹——相同即无进展（HangDetect.cpp:187-233）；巡检线程 CheckTasks 周期扫描（common/HangDetectMonitor.cpp）。

## 外部连接

DcgmWatchTable 的真实消费者是 **modules 侧**：nvswitch 的两个管理器各持一份 m_watchTable（modules/nvswitch/DcgmNvSwitchManagerBase.h:387、DcgmNscqManager.h:204），节拍调用在 DcgmNvSwitchManagerBase.cpp:327；sysmon 同款（modules/sysmon/DcgmModuleSysmon.cpp:890、:905、:1549）。注意甄别：dcgmlib 的 DcgmCacheManager **不用**这个类，它维护自己的 C hashtable watch 表（DcgmCacheManager.h:1626-1628）与 dcgmcm_watch_info_t（DcgmCacheManager.h:125-158），但 include DcgmWatchTable.h:29 复用键类型词汇——两套并行 watch 表是模块化改造的历史产物。HangDetect 的最大消费方在 nvvs（nvvs/include/Plugin.h、TestFramework.h 等）与 NvmlTaskRunner::run（dcgmlib/src/NvmlTaskRunner.cpp:640-664，把 NVML 线程注册进监控）。

## 数据流

模块主循环周期调用 GetFieldsToUpdate(模块ID, now, toUpdate, earliestNextUpdate)（DcgmWatchTable.cpp:292），拿到到期字段集合后执行采集，样本经 CoreProxy::AppendSamples 推回 core 入 cache；earliestNextUpdate 决定模块下一轮睡眠时长。断连路径：连接消亡 → RemoveConnectionWatches 清掉该连接全部观察者（DcgmWatchTable.cpp:69-117），若 watch 因此归零，把 (gpuId→fieldId) 写进 postWatchInfo（DcgmWatchTable.cpp:89-105）供上层补 NVML 反注册。字段归属划界由 IsFieldIgnored 硬编码：Core 忽略 NVSwitch 段（DcgmWatchTable.cpp:184-185），NvSwitch 只认 700-899 段与固件版本字段（DcgmWatchTable.cpp:187-190），Profiling/Sysmon 同理按字段 ID 段过滤（DcgmWatchTable.cpp:191-194）。

## 设计决策

1) **min 聚合**：多订阅者竞争同一字段时取最快间隔——高频消费者绑架低频者，代价换实时性；maxAge 同样取 min 以满足最严格的留存要求。2) **字段 ID 段做模块路由**（IsFieldIgnored 的 switch）零元数据开销，但强依赖 dcgm_fields.h 的 ID 分段纪律（NVSwitch 700-899、PROF 1001 起），新增模块字段必须同步这里。3) **nextUpdate = lastQueriedUsec + interval** 而非 now + interval（DcgmWatchTable.cpp:321 与 :333-334 注释），驱动调用耗时不会累积漂移节拍。4) DcgmMutex 的超时+持有者行号诊断把死锁从"挂死"变成"可定位日志"。5) postWatchInfo 把"watch 归零"事件交给上层做 NVML 收尾，watch 表自身不碰驱动。

## 新人提示

改 dcgmcm_watch_info_t（CacheManager 侧表）务必同步 AllocWatchInfo 初始化——头文件注释明示因含 class 成员不能 memset（DcgmCacheManager.h:120-123）。dcgm_entity_key_t 的 fieldId/entityGroupId 只有 16 位，字段 ID 上限 65535，尾加字段时先看分段余量。RemoveWatcher 有公有 5 参与私有 3 参两个重载（DcgmWatchTable.cpp:46-66 与 :203-242），删错重载编译器会替你兜住，但断连清理只走公有路径。读 GetFieldsToUpdate 时盯住三个 continue（未 watch :306-309、他模块字段 :312-315、未到期 :318-324），它们就是节拍机的全部状态转移。
