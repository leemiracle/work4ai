# 01 FlightDataRecorder_c 核心：记录器的中枢与四写手

## 角色定位

`FlightDataRecorder_c` 是 FDR 运行时的中枢（`fdr.hpp:39` 声明、`fdr.cpp` 1482 行实现，全仓最大源文件）：持有全部 Record 记录、四个 keeper 元数据写手、定时器表与平台指纹，把"平台配置装载→记录创建→定时采样→落盘压缩"整条生命周期握在手里。进程入口是 `main.cpp`——sd-event 事件循环 + 信号处理，FDR 是 OpenBMC 上典型的单进程守护。

## 内部结构

**三索引记录表**（`fdr.hpp:43-52`）：全量 `RecList` vector（`fdr.hpp:43`），三个 map 按用途建索引——轮询表 `RecListPollMap`（`fdr.hpp:46`，key=轮询周期秒）、订阅存储表 `RecListSubscribeStoreMap`（`fdr.hpp:49`）、组轮询表 `RecListGrpPollMap`（`fdr.hpp:52`）；另有 O(1) 查找优化 map（`fdr.hpp:137`）。**四大 keeper 写手**（`fdr.hpp:61-64`）：BootEvent.dat（开机事件）、Compactor.dat（压缩簿记）、BookOfErrors.dat（错误账本）、ParamDescription.dat（参数描述）——都经 `CreateKeeperWriter`（`fdr.hpp:84`）创建 FDRStore 追加器；压缩簿记三操作 RemoveEntry/AppendEntry/CleanEntries 在 `fdr.hpp:103-106` 一组。

**启动链**（`fdr.cpp`）：构造 `fdr.cpp:55` → `InitExceptionRateLimiter`（`fdr.cpp:168`，配 LeakyBucket）→ `FindAndLoadPlatformProfile`（`fdr.cpp:211`，平台发现）→ `ConvertPPFToStruct`（`fdr.cpp:296`，PPF YAML→结构体）→ `ExecuteFingerPrintRules`（`fdr.cpp:322`，指纹规则定平台）→ `CheckAvailableFdrPartitionDiskSize`（`fdr.cpp:342`，磁盘配额）。

**定时器引擎**（`fdr_timers.cpp` 396 行）：按 PPF 周期注册 sd-event 定时源，三个回调引擎——单记录轮询 `PollRecordTimerCBEngine` 触发 RefreshAndStore（`fdr_timers.cpp:161`）、组轮询触发 GroupRefreshAndStore（`fdr_timers.cpp:186`）、订阅存储 `SubscribeStoreRecordTimerCBEngine`（`fdr_timers.cpp:194`）；压缩双窗口回调 `CompactionWindowTimerCBEngine`/`CompactionSubWindowTimerCBEngine` 声明在 `fdr.hpp:89-90`。

## 外部连接

- 上游：`main.cpp:24` signalHandler + `main.cpp:96` SIGINT 注册；`main.cpp:61`/`main.cpp:67` 注册 AML 事件与 D-Bus 属性变更信号；`main.cpp:125` 主循环排空 dbus 消息。
- 下游：Record 层（`fdr_record.hpp`）承接采样；FDRStore（`fdr_store.hpp`）承接落盘；`ppf_sanity.hpp:20` 在装载期校验 PPF。
- 横向：`fdr_log.hpp` 日志（配置来自 profile）、`fdr_common.hpp:60` LeakyBucket 限流。

## 数据流

sd-event 醒来 → 定时回调按索引取 Record 列表 → 逐条 Refresh（读 D-Bus/Redfish/MRD）→ FDRStore.append 追写样本文件 → 统计引擎（RunningStatisticEngine 滚动 min/max/avg 落 statfile）→ 压缩窗口到期时 CompactorEngine 合并最老目录为 HighFidelity 文件并更新 Compactor.dat/BookOfErrors.dat。开机路径：UpdateBootEventLog 写 BootEvent.dat，dump 事件路径转 DeviceDumpHandler 状态机。

## 设计决策

1. **多 map 索引而非单表遍历**：同周期的 Record 聚一个桶，定时回调零扫描——万级遥测点下这是必须的；代价是三索引与 O(1) map 的内存冗余。
2. **keeper 与样本分离**：元数据（事件/簿记/参数描述）走四个专职 keeper 文件，遥测值走样本文件——离线工具可只读 keeper 快速定位，不必扫全量样本。
3. **异常限流内建**（`fdr.cpp:168`+LeakyBucket）：BMC 日志风暴会淹掉真正要记录的事件，漏桶+消息节流（`fdr_log.cpp`）是黑匣子设备的自保机制。
4. **sd-event 单线程事件循环**：不引线程池——BMC 单核资源下确定性优先，Redfish 等慢操作靠异步状态机（device dump 的 pollAsyncStatus 模式）而非并发。
5. **磁盘配额前置检查**（`fdr.cpp:342`）：启动即确认分区可用，配合压缩器，样本永不无限增长——黑匣子"环形覆盖"语义的实现。

## 新人提示

- 读启动顺序从 `fdr.cpp:55` 构造函数顺藤摸瓜；改 Record 行为先看 `fdr.hpp:43-52` 的三索引——加字段要同时顾三处。
- 全部磁盘文件名（.dat keeper/样本/statfile）的命名约定散在 fdr.cpp 与 fdr_store.cpp，离线解码端 `fdrtool/catalog/catalog.py:592` 对 'Bookkeeper' 文件名有特判，改名两边都要动。
- 测试不启 BMC：`tests/test_stubs.cpp` 提供链接桩，`tests/fdr_redfish_stub_test.cpp:1` 起用全局桩变量注入 HTTP 行为——新功能的可测性先想桩。
- 图谱口径提醒：类方法实测 52 个（`fdr.hpp:39-185`），图谱节点写 54（README 勘误#8）。
