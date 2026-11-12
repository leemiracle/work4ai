# 03 · health rollup 健康上卷与 selftest 自检体系

## 角色定位

事件检测（02 篇）回答"现在发生了什么"，健康上卷与 selftest 回答"这台设备整体怎么样、配置本身是否可信"。健康线把逐设备错误计数沿 DAT 树聚合成 Health/HealthRollup 写回 D-Bus（Redfish 消费者直接可读）；selftest 线让守护可以按设备树主动执行测试点评估——两者共用 DAT 世界模型，一个被动聚合、一个主动探测。

## 内部结构

**健康上卷链**：

- `include/device_status_handler.hpp`：每设备 `Health`/`HealthRollup` 两个 Severity（:46-47），全局 rollup 缓存（:82 起注释），按 deviceId 查 rollup 设备（:94-106 的查找与 [Other] 兜底逻辑）。
- `device-health-service/device_health_service.cpp`（353 行独立守护）：`updateDeviceHealth`（:52）入口——`computeHealthForDevice`（:107）按错误计数算健康值，写 D-Bus 失败告警（:57-59）；监听新日志条目触发聚合。
- 支撑件：`data_structures.hpp`（199 行）——`AssertedErrorsForDevice`（data_structures.hpp:59）每设备错误表 + `TmpFileManager`（data_structures.hpp:73）RAII 临时文件管理；`dbus.hpp/.cpp`（484/223 行）封装 Health 属性读写。
- 遥测旁路 `include/tal_singleton.hpp`：namespace event_tal（:32 起）的 updateChassisHealthOnSHM 等 helper——经 TelemetryAggregator 把 chassis 健康写共享内存（/health/chassis/<dev> 路径，xyz.openbmc_project.State.Decorator.Health 接口），供 SHM（State Health Manager）侧聚合。
- 验证器 `tools/device_healthrollup_validator.py` 专测上卷规则正确性；`tools/health_presence_check.py`（paramiko 远程执行）做在场性检查。

**selftest 线**：

- 引擎 `include/selftest.hpp`（471 行）+ `src/selftest.cpp`（669 行）：`Selftest` 类（selftest.hpp:183，继承 EventHandler）按 DAT 树逐设备执行测试点评估，`updateDeviceHealth`（声明 selftest.hpp:206，实现 selftest.cpp:142）把结果回写 D-Bus Health；`RootCauseTracer`（selftest.hpp:406）从失败测试点沿树回溯根因设备；数据结构 TestPointResult/DeviceResult/Report 支撑聚合。
- 上卷关联协议：DAT 设备间的 health_rollup 关联在 dat_traverse.cpp:707-764（"Associations" 属性下的 `("health_rollup", "", devicePath)` 元组，:759 按 "health_rollup" 过滤）。
- CLI 版 `tools/selftest_tool.cpp`（278 行）复用引擎做离线自检；`tools/selftest_json_generator` 与 `tools/selftest-report-schema.json` 定义报告格式（样例 examples/selftest-report.json）；`tools/dat_and_report_merge_tool/dat_and_report_merger.py` 把自检报告按 DAT 树合并出汇总 CSV。
- **配置诊断** `include/diagnostics.hpp`（772 行）+ `src/diagnostics.cpp`（936 行）：JsonReadTest（diagnostics.hpp:574）/JsonSchemaTest/DatParseTest 等配置体检测试族（:222-225 列出清单，:492-493 的 DependentOn<> 组合子表达测试依赖）——启动前自证 dat.json/event_info.json 健康。

## 外部连接

上游：CheckAccessor（check_accessor.hpp:27 AssertedDevice）与 EventDetection 的匹配结果是错误计数的来源；phosphor-logging 的日志条目（interfacesAddedCallback 监听新条目）驱动 device-health-service 聚合。下游：Health/HealthRollup 属性被 Redfish/Hardware-Health 消费；tal_singleton 的 SHM 通道对接 NVIDIA 整机健康管理。selftest 的 DAT 遍历复用 DATTraverse（dat_traverse.hpp:235）；测试点执行用 accessor 三层（02 篇）取值——selftest 是"把事件配置当测试用例跑"的机制。

## 数据流

被动链：EventDetection 匹配 → MessageComposer 写 phosphor-logging 条目 → device-health-service 监听 interfacesAdded → AssertedErrorsForDevice 累计 critical/warning → computeHealthForDevice（device_health_service.cpp:107）算档位 → updateDeviceHealth（:52）写 Health 属性 → device_status_handler 沿树 rollup 成 HealthRollup（含 [Other] 兜底）→ Redfish 可见；旁路 tal_singleton 同步 chassis 健康进 SHM。主动链：selftest_tool 启动 → Selftest（selftest.hpp:183）遍历 DAT → 每设备执行 TestPoint（经 DataAccessor/CMDLINE wrapper 取真值）→ TestPointResult 聚合成 DeviceResult → updateDeviceHealth（:206）回写 → RootCauseTracer（:406）标根因 → 报告 JSON（schema 自校验）→ dat_and_report_merger.py 合并出 CSV。开机链：diagnostics（JsonReadTest/JsonSchemaTest/DatParseTest）先跑，配置不健康直接拒绝起服务。

## 设计决策

- **Health 与 HealthRollup 分两级**：本设备状态与" subtree 聚合状态"分开表达（device_status_handler.hpp:46-47）——Redfish 语义里两者消费者不同（换件决策 vs 整机健康）。
- **独立守护而非线程**：device-health-service 是 353 行独立进程——健康聚合挂掉不能拖垮事件检测主守护，故障域隔离。
- **自检复用检测基元**：selftest 不另造数据通道，测试点就是 accessor 声明——同一份配置既当检测规则又当自检用例，语义不会漂移。
- **配置体检前置**：diagnostics 的 DependentOn 组合子（diagnostics.hpp:492）把"schema 过了才能 parse、parse 过了才能语义检查"表达成依赖图——坏配置在装载前就死。
- **RAII 临时文件**：TmpFileManager（data_structures.hpp）管聚合中间文件的生死——BMC 存储小，泄漏即故障。

## 新人提示

读序 doc/event_handler.md → selftest.hpp:183-230 → device_health_service.cpp:52-107；跑 tools/selftest_tool.cpp 编译产物对 examples/dat.json 出一份报告，再用 dat_and_report_merger.py 合并；改上卷规则必须过 device_healthrollup_validator.py；test/selftest_test.cpp 是引擎行为的金标准；[Other] 兜底分支（device_status_handler.hpp:106）是历史兼容点，动它前先查 Redfish 消费方。
