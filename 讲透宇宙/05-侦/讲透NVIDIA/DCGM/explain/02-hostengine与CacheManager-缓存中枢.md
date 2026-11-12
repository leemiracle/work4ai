# 02 · hostengine 守护进程与 DcgmCacheManager：16530 行的缓存调度心脏

## 角色定位

nv-hostengine 是 DCGM 的守护进程宿主，dcgmi CLI、NVML 客户端、容器内 SDK 全部经它与 GPU 世界对话。入口 hostengine/src/main.cpp（580 行）只管进程形态：pidfile、daemonize、信号与连接类型；真正的引擎在 dcgmlib 的 DcgmHostEngineHandler.cpp（5482 行）里装配，心脏是 DcgmCacheManager.cpp——**全仓最大文件 16530 行**，承担字段值缓存、采样调度、watch 管理、MIG 实例追踪与 GPM 集成。TCP 默认端口 5555（dcgm_structs.h:289 DCGM_HE_PORT_NUMBER；HostEngineCommandLine.cpp:382 的 default 5555）。

## 内部结构

main 的装配链（hostengine/src/main.cpp:423）：dcgmInit（main.cpp:476）→ 填 dcgmStartEmbeddedV2Params_v3 含模块 denylist（main.cpp:484-498）→ dcgmStartEmbedded_v2（main.cpp:510）→ 按连接类型 dcgmEngineRun：DomainSocket / TCP / Vsock（main.cpp:525-541）→ 主线程 100ms 睡眠等 g_stopLoop（main.cpp:574-577）。守护化 heDaemonize（main.cpp:467），SIGPIPE 显式忽略（main.cpp:379-381）。HostEngineHandler 构造后 new DcgmCacheManager（DcgmHostEngineHandler.cpp:2466）并注入 NVML 事件线程（:2467），对外以 mpCacheManager 指针全量代理（DcgmHostEngineHandler.cpp:763，如 GetCacheManagerFieldInfo :1364-1366）。

CacheManager 自身是 DcgmThread 子类：Init（DcgmCacheManager.cpp:2128）→ Start（DcgmCacheManager.cpp:2598）拉起线程。主循环 RunWrapped（DcgmCacheManager.cpp:6893-6966）：先跑任务队列 TaskRunner::Run(true)（:6907），再 DoOneUpdateAllFields（:6924）；睡眠策略为"最长 10 秒"上限（wakeTimeInterval，:6896）+ earliestNextUpdate 自适应（:6950-6951），不足 1ms 干脆跳过睡眠（:6953-6957），lock-step 模式睡 1 小时（:6931-6934）。DoOneUpdateAllFields（:6862-6890）持 DcgmLockGuard 调 ActuallyUpdateAllFields（:6877-6881），有在线订阅者时额外缓冲 fvBuffer 并 UpdateFvSubscribers（:6869-6885）。

## 外部连接

三个方向：① 对客户端——HostEngineHandler 处理连接分发与模块消息路由：denylist 模块直接拒绝（DcgmHostEngineHandler.cpp:1327-1331），未装载模块懒加载（:1337-1346），pause/resume 特殊地按序广播给全部模块（:1349-1352），其余 SendModuleMessage（:1358）。② 对模块——LoadModule（DcgmHostEngineHandler.cpp:2669）dlopen RTLD_NOW（:2729）取三个 C 符号 dcgm_alloc_module_instance / dcgm_free_module_instance / dcgm_module_process_message（:2741-2744），再以 allocCB(&m_coreCallbacks) 把回调表注入模块（:2764）——这是全仓唯一的 DI 注入点。③ 对 NVML——GPU 字段经 NvmlTaskRunner 任务线程串行化执行（详见篇 5）。

## 数据流

ActuallyUpdateAllFields（DcgmCacheManager.cpp:6024-6151+）是节拍机的引擎侧实现：入口断言已持锁（:6032-6036），hashtable_iter 遍历自管 watch 表 m_entityWatchHashTable（:6044-6045，结构 dcgmcm_watch_info_t 见 DcgmCacheManager.h:125-158）；pushedByModule 的字段（nvswitch/prof 等模块推送型）跳过（:6058-6063）；到龄判定 age < monitorIntervalUsec（:6065-6075）；GPU 实体先查存活状态，丢失/分离的 GPU 后续补空值（:6090-6103）。采集分两路：映射到 NVML 的 GPU 字段攒进 threadCtx.fieldValueFields[gpuId] 批量执行（:6139-6148），其余实体**解锁后**采集、Defer 回锁（:6120-6132）。样本写入 timeSeries（DcgmCacheManager.h:145），读取走 GetLatestSample / GetMultipleLatestLiveSamples（DcgmHostEngineHandler.cpp:594-604 代理）。MIG 追踪由 GpuInstanceProfiles/GpuInstances/ComputeInstances 三组内嵌类承担（DcgmCacheManager.cpp:733-886）；practicalEntityGroupId/practicalEntityId 字段对（DcgmCacheManager.h:150-158）让 MIG 实例字段的"呈现实体"与"轮询实体"解耦——多数数据只在 GPU 级可取。GPU 热插拔经 MergeNewlyDetectedGpuList（101 行）与 AttachGpus（189 行）合并。

## 设计决策

1) **主循环即任务线程**：CacheManager 同时是 DcgmTaskRunner，采集与 API 任务同队列串行，天然免锁竞争一部分状态。2) **自适应睡眠**：以 earliestNextUpdate 精确睡到下一个到期字段，同时用 10 秒兜底防时钟漂移，m_runStats（sleepTimeUsec/awakeTimeUsec/numSleepsSkipped，:6913、:6962）把循环自身也监控起来。3) **驱动调用前解锁**（:6120 注释）避免 NVML 慢调用拖死全局锁，批量映射字段例外，攒批后统一处理。4) **两套 watch 表并存**（DcgmWatchTable 归模块、dcgmcm 表归 core）是模块化改造过渡产物，改 watch 语义要两边对齐。5) watch 记录自带 execTimeUsec/fetchCount（DcgmCacheManager.h:141-144）——每个字段的采集成本可观测，是调 updateInterval 的直接依据。

## 新人提示

读 16530 行的文件不要线性读：先 RunWrapped → ActuallyUpdateAllFields 主干，再按 watch 生命周期（AddEntityFieldWatch 166 行 :3597 附近 → PrecheckWatchInfoForSamples → RemoveEntityFieldWatch 66 行）补全。调节拍问题看 GetCacheManagerFieldInfo 输出的 per-field fetchCount/execTimeUsec。改 watch 结构体必读 DcgmCacheManager.h:120-123 的 AllocWatchInfo 注释（不能 memset）。5555 是 TCP 契约，dcgmi -u 远程依赖；本机默认 DomainSocket。断连路径 OnConnectionRemove（DcgmHostEngineHandler.cpp:1381-1383）是理解 watch 生命周期的最短入口。
