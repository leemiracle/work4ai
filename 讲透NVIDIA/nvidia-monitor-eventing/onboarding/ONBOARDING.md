# nvidia-monitor-eventing 新人上手指南（ONBOARDING）

> 知识底座：understand 图谱 324 节点 / 393 边 / 11 层 / 14 步 tour，validate 0 issues，fingerprints 237 文件基线 @ commit `69f6f8e6`（2026-08-11，"Add standalone event qualifier and resolve ranged accessors"）。
> 本文行号锚全部源码 grep 实证；本仓是 C++/OpenBMC 工程，引用以 `include/xxx.hpp:行` 与 `src/xxx.cpp:行` 区分。

## 1. 项目定位与数字底座

**nvidia-monitor-eventing 是跑在 BMC（基板管理控制器）上的 GPU/NVSwitch 事件监控与 Redfish 上报守护**：读 D-Bus 遥测与命令行工具输出，按事件配置匹配故障条件，经 phosphor-logging 生成 Redfish 标准日志，并维护设备 Health 状态。README.md 只有一句话定位（"NVIDIA Device Monitoring and Eventing"）加构建说明——真正的架构知识在 `doc/` 十篇模块文档（config_parser/data_accessor/dat_traverse/event_detection/event_handler/event_instantiator/logger/message_composer/message_dispatcher + rascat_spec2code）与 `doc/device_id_user_guide.md`（896 行，模式语言权威参考）。

数字底座（wc 实证）：

| 事实 | 数值 | 锚 |
|---|---|---|
| 实现侧最大件 | `src/event_info.cpp` 1038 行 | 声明侧 `include/event_info.hpp` 772 行 |
| 模式语言主实现 | `include/device_id.hpp` 985 + `src/device_id.cpp` 837 | DeviceIdPattern 类 device_id.hpp:305 |
| Python 同构实现 | `tools/device-id-lang/ids.py` 605 行 | 与 C++ 跨语言对拍 |
| 检测引擎 | `include/event_detection.hpp` 770 行 | EventDetection 类 event_detection.hpp:109 |
| 数据抽象 | `include/data_accessor.hpp` 783 行 | DataAccessor 类 data_accessor.hpp:83 |
| DAT 参考蓝本 | `examples/dat.json` 4153 行 | 事件蓝本 examples/event_info.json 1515 行 |
| 生成器之王 | `spec2code/rascat_spec2code` 1156 行 | 手册 spec2code/rascat_spec2code.md 300 行 |
| 测试共享桩 | `test/tests_common_defs.cpp` 1788 行 | 注意：hpp 仅 34 行声明 |

## 2. 构建体系与技术栈

- **meson/ninja**：根 `meson.build`（258 行）用 wrap 机制钉版四个子项目——sdbusplus（D-Bus C++ 绑定）、phosphor-logging（OpenBMC 日志）、sdeventplus（sd-event）、googletest（meson.build:94 sdbusplus、:168 googletest subproject 调用；subprojects/ 四个 .wrap 各 3 行）。`meson builddir && ninja -C builddir` 两步出产物。
- **两条环境路径**：`scripts/setup_bldenv` 装 OpenBMC SDK 交叉工具链（README.md Environment Setup 表：Ubuntu 18.04/Cygwin 双支持）；`Dockerfile` 是 Yocto 风格容器构建。`buildenv/` 存环境脚本，`eventing_config.h.in` 是配置头模板。
- **项目选项**：`meson_options.txt` 暴露 debug_log 等开关（README.md "Enable Project Options" 节，`-Ddebug_log={0..4}`）。
- **语言生态**：核心 C++17（nlohmann::json、boost::lockfree、sdbusplus）；工具链大量 Python/Bash/JS（Apps Script 导出 DAT）；Doxygen 文档工程（Doxyfile）。
- **格式化矩阵**：仓根十个语言各自的 ignore 文件（.clang-format/.flake8-ignore/.beautysh-ignore/.eslintignore 等）——多语言仓库的 lint 边界。

## 3. 架构分层地图（图谱 11 层收敛为四条线）

图谱 11 层（L01-L11）收敛成四条线记忆：

1. **运行时主线（L03-L09）**：配置装载（eventing_main/config_*/json_*）→ 设备世界模型（DAT）→ 设备寻址（device-id 模式语言）→ 数据访问（accessor 三层）→ 事件模型与实例化（EventNode/EventInstantiator）→ 检测引擎（EventDetection）→ 出口（MessageDispatcher/MessageComposer/日志）→ 自检与健康（selftest/diagnostics/device-health-service/device_status_handler）。
2. **配置生产侧（L04/L09）**：spec2code 生成器家族 + vulcan-faults + DAT-json-exporter/设备关联编辑器——事件配置不是手写的，是从规范生成的。
3. **验证侧（L09/L11）**：event_injector 注入器家族 + event_validation.py 端到端验证 + nvidia-xid-event-handler。
4. **包装与调试（L10）**：wrapper-tools 生成器与五个成品 wrapper + dbus_tester/jtag。

主循环一句话：`eventing_main.cpp:374`（main）解析命令行 → `loadDAT`（eventing_main.cpp:109）建设备树 → `loadEvents`（:141）装载并实例化事件 → EventDetection 双线程消费 D-Bus 信号 → 匹配/恢复/开机对账 → MessageComposer 出 Redfish 日志。

## 4. 核心链路一：DAT 设备关联树与 device-id 模式语言

- **DAT（Device Association Tree）**是全仓的设备世界模型：`include/dat_traverse.hpp` 定义 Status（dat_traverse.hpp:41）、TestPoint（dat_traverse.hpp:49）、TestLayer（dat_traverse.hpp:56）、DeviceType（dat_traverse.hpp:74）、Device（dat_traverse.hpp:103）与遍历器 `DATTraverse`（dat_traverse.hpp:235，L235-523，继承 EventHandler）；设备类型映射 `populateMap`（声明 dat_traverse.hpp:155，实现 dat_traverse.cpp:86 与重载 dat_traverse.cpp:115，cpp 共 780 行），health_rollup 设备关联协议在 dat_traverse.cpp:707-764。`src/device_util.cpp` + `include/device_util.hpp` 做设备区间展开（`expandDeviceRange` device_util.cpp:45/:73）与对象路径推断。
- **配置蓝本**：`examples/dat.json`（4153 行多层级树）+ `device_mctp_eid.csv`（MCTP 端点映射）；`tools/sub-dat.py` 抽子树；`tools/DAT-json-exporter`（Code.js + appsscript.json + spreadsheets-install.sh）从 Google Sheets 生产 DAT JSON——配置源头在表格里。
- **device-id 模式语言**是"事件如何覆盖一组设备"的寻址语言：`GPU[0-3]`、`NVS[0,2-3]` 类括号区间 + 索引引用 + 笛卡尔积。C++ 实现四件套：`PatternIndex`（device_id.hpp:184，含 normalize device_id.hpp:199）、`PatternInputDomain`（device_id.hpp:225）、`CartesianProductRange`（device_id.hpp:253）、`DeviceIdPattern`（device_id.hpp:305，L305-586，含迭代展开与序比较）；实现侧 device_id.cpp 837 行。Python 同构解释器 `tools/device-id-lang/ids.py`（605 行，`DeviceIdPattern` ids.py:197 / `InvDeviceIdPattern` ids.py:421，range/map/indexed_map 域函数族）用于跨语言语义对拍；单头复用版 `DeviceIdPattern.hpp` 服务工具脚本。
- **映射维护**：`tools/device_id_mapping/`（ids-map.csv/ids-map.py/json-gen.py/device-id-norm-gen.sh/device-id-norm-test.sh）管设备名规范。权威语法参考就是 `doc/device_id_user_guide.md`（896 行）。

## 5. 核心链路二：accessor 三层、事件模型与检测引擎

- **accessor 三层**（数据面）：`DataAccessor`（data_accessor.hpp:83）统一描述数据来源——D-Bus 属性/命令行/文件/正则四类，`operator==`（:154）与 `getDataValue`（:627）；实现 data_accessor.cpp 378 行。D-Bus 中间层 `include/dbus_accessor.hpp`（733 行）：CRTP 模板 `ObjectMapper`（:160）+ `DirectObjectMapper`（:515）/`CachingObjectMapper`（:535）两种解析策略 + `DbusDelayer`（:600）/`DbusDelayerConstLowerBound`（:641）/`DbusDelayerStateGuard`（:675）/`DelayedMethod`（:689）可注入延迟测限流。判定层 `CheckAccessor`（check_accessor.hpp:51）：等于/范围/位图/查表判定，`AssertedDevice`（:27）标记哪些设备满足条件，`buildSingleAssertedDeviceName`（:194）构造单设备断言（hpp 230 + cpp 345 行）。值语义在 `property_accessor.hpp`：`PropertyValueDataHelper`（property_accessor.hpp:80）、`PropertyValue`（property_accessor.hpp:301，支持 string/integer/double 变体与 bitmap/bitmask 之分，注释 property_accessor.hpp:294）、`PropertyString`（property_accessor.hpp:515）。
- **事件模型**：`EventNode`（event_info.hpp:334，L334-666）定义单事件全貌——匹配条件、Redfish 消息模板 `MessageArgPattern`（:75）、`OriginOfCondition` 设备定位（:369，setter :497/getter :506/`hasFixedOriginOfCondition` :488）、类别与严重度；实现侧 event_info.cpp 1038 行。`EventInstantiator`（event_instantiator.hpp:33）把 JSON 定义展开设备模式、绑定 accessor 产出运行时集合（`instantiateEvent` :72；实现 event_instantiator.cpp:38 起）。
- **检测引擎**：`EventDetection`（event_detection.hpp:109，770 行）是心脏——双 worker 线程 `workerThreadMainLoop`（:128）/`workerThreadProcessEvents`（:134），实现 event_detection.cpp:68/:59（:76 有 "thread2: exiting" 诊断日志）；匹配判定 `IsEvent`（:574，调用点 event_detection.cpp:443）；恢复语义 `recoverFromPowerCycleEvents`（:260）与 `resolveDeviceLogs`（:282）做开机对账；每个触发事件另起处理线程（:640、:694 的 std::thread）。
- **辅助件**：`pc_event.hpp:35`（PcQueueType，掉电前事件队列，核心 boost::lockfree::spsc_queue 外套 std::scoped_lock）；`standalone_qualifier.hpp:43`（standaloneQualifierPassed——无整机上下文模式下抑制哪些事件，实现 standalone_qualifier.cpp:26，最新 commit 主题）；`event_handler.hpp`（EventHandler 基类 + EventHandlerManager 注册表，RunAllHandlers 分发）。
- **公共底座**：`json_proc.hpp:48`（JsonPattern）+ `src/json_proc.cpp:28`（evalJson，事件匹配与 accessor 展开的 JSON 求值器）；`include/json_schema.hpp`（473 行轻量 schema 校验器）+ `src/config_schemas.cpp`（180 行，内置六个 JSON schema 常量，装载前校验 dat.json/event_info.json）；`include/log.hpp`（570 行，Log 单例多级别分离输出）；`include/util.hpp`（446 行：DeviceIdData :82、Severity :324 Redfish 严重度枚举）；cmd_line.hpp 命令行框架与 threadpool_manager.hpp 线程池。

## 6. 核心链路三：出口、健康上卷与 selftest

- **消息出口**：匹配事件经 `MessageDispatcher`（message_dispatcher.hpp:24）路由到 `MessageComposer`（message_composer.hpp:42，实现 message_composer.cpp 125 行）组装 phosphor-logging CreateEntry——Redfish MessageId/Severity 映射靠 `dbus_log_utils.hpp` 的 translateSeverityDbusToRedfish。
- **健康上卷**：`include/device_status_handler.hpp`（Health/HealthRollup Severity :46-47 + 全局 rollup 缓存 :82 起）把设备状态沿 DAT 树上卷；`device-health-service/device_health_service.cpp`（353 行）是独立守护——`updateDeviceHealth`（:52）按设备聚合 critical/warning 错误计数，`computeHealthForDevice`（:107）算健康值写 D-Bus；`data_structures.hpp`（199 行，`AssertedErrorsForDevice` data_structures.hpp:59 每设备错误表 + `TmpFileManager` data_structures.hpp:73 RAII 临时文件）与 dbus.cpp/hpp（223/484 行）支撑。
- **selftest 自检**：`include/selftest.hpp`（471 行）——`Selftest` 类（selftest.hpp:183，继承 EventHandler）按 DAT 树逐设备执行测试点评估，`updateDeviceHealth`（selftest.hpp:206，实现 selftest.cpp:142）回写健康；`RootCauseTracer`（selftest.hpp:406）从失败测试点回溯根因设备；实现 selftest.cpp 669 行。CLI 版 `tools/selftest_tool.cpp`（278 行）复用引擎离线自检；`tools/dat_and_report_merge_tool/dat_and_report_merger.py` 把报告按设备树合并出汇总 CSV；`tools/device_healthrollup_validator.py` 验证上卷正确性；`tools/health_presence_check.py`（paramiko 远程执行）做在场检查。
- **配置诊断**：`include/diagnostics.hpp`（772 行）+ `src/diagnostics.cpp`（936 行）——JsonReadTest（diagnostics.hpp:574）/JsonSchemaTest/DatParseTest 等配置体检测试族（清单见 :222-225），诊断配置文件本身是否健康。

## 7. 核心链路四：spec2code 生成器、注入验证与 wrapper 体系

- **spec2code 家族**（仓根 `spec2code/`，注意不在 tools/ 下）：`rascat_spec2code`（1156 行，RAS 类别规范→事件配置+文档，家族最大，手册 rascat_spec2code.md 300 行）；`fpga_alert_spec2code`（571 行，寄存器规范→事件）；`gpiomon_event_generator`（192 行）、`glacier_spec2code`（46 行）、`redfish_eventing_recipe_validator`（284 行，配方合规校验）。姊妹目录 `tools/vulcan-faults/`（3436 行故障汇总 CSV `data/in/vulcan-faults-summary.csv` → event_info 骨架，产出 `data/out/vulcan-faults-smbpbi-op-code.tsv`）。
- **事件注入与验证**：`tools/event_injector`（394 行调度器）+ `tools/modules/` 两注入器——event_accessor_script.py（428 行，改写设备属性模拟 BMC 侧故障）与 event_logging_script.py（155 行，直接向 D-Bus Logging 注条目），基类 injector_script_base.py（232 行），共享判定 com.py（399 行：expand_range/compare_mandatory_event_fields）；端到端验证 `tools/event_validation.py`（865 行，注入后 Redfish 日志/健康断言）；`tools/nvidia-xid-event-handler`（442 行）消费 Xid 错误码。解析器家族：fpga_pwrfail_parser/gb200_pwrfail_parser/glacier_boot_status_parser/ocp_recovery_status_parser/mcu_event_parser + mctp-error-detection + mctp-vdm-util-wrapper。
- **wrapper 体系**：`tools/wrapper-tools/`——generate-wrappers.py 从 mockup 定义模板（`wrappers-mockup-definition_dat-obmc=adf4a8847.tsv`）生成 bash 设备访问包装脚本（统一接口供测试点 CMDLINE accessor 消费），jq 四件（testpoints.jq/commands-list.jq/tabular-testpoints*.jq）做查询；性能线 performance-test-deploy-pkg/wrappers-exec-time.sh + performance-test-results/ 三机型 CSV（2022-10 LunaDP-B1-12、Sravanthi、VikingDP2 系列，含 original/optimized device-id-norm 对照——模式语言优化的实证数据）。成品五件：`tools/wrapper_nvlink_wp_status/nvlink-wp-status-wrapper`（686 行最大）+ wrapper_pcie_status/wrapper_i2c_status/wrapper_fpga_register_table，各带测试脚本与 profile。
- **调试**：`tools/dbus_tester.cpp` 裸 D-Bus 探测；`tools/jtag`（jtag.h 598 行寄存器访问）；`tools/json-to-nlohman.py` JSON 转换。

## 8. 测试体系与新人上手路径

- **googletest 基座**：`test/` 18 个 *_test.cpp——device_id_test.cpp（2028 行，模式语言最重）、event_detection_test.cpp（1621 行）、accessor_test.cpp（812 行）、dat_traverse_test/dat_test/dat_to_dbus_test/dbus_accessor_test/event_instantiator_test/event_test/eventing_main_test/json_proc_test/propertyvalue_string_test/propertyvalue_variant_test/selftest_test/standalone_qualifier_test/util_test/accessor_expansion_test。共享桩在 tests_common_defs.cpp（1788 行 mock 对象映射+标准事件样本；hpp 仅 34 行）+ event_info_accessors_fixture.json。
- **配置自证**：examples/ 自带 schema（event_info-schema.json）与样例报告（selftest-report.json + tools/selftest-report-schema.json），diagnostics 引擎让守护在启动时自检配置。

五天路径：

1. **Day 1 定位**：README.md → doc/event_detection.md → doc/dat_traverse.md；对照 examples/dat.json 顶层结构。
2. **Day 2 世界模型**：dat_traverse.hpp:41-235 五个类 → device_util.cpp；用 tools/sub-dat.py 抽 examples/dat.json 的一棵子树观察。
3. **Day 3 寻址语言**：doc/device_id_user_guide.md 前半 → device_id.hpp:184-586 四件套 → ids.py 对拍；跑 test/device_id_test.cpp 理解边界。
4. **Day 4 数据面与检测**：data_accessor.hpp:83 → dbus_accessor.hpp:160-689 → check_accessor.hpp:27-194 → event_detection.hpp:109-574 主线；画一次"属性变更信号→断言→Redfish 日志"时序。
5. **Day 5 质量线**：event_injector + event_validation.py 跑一次注入-验证闭环；selftest_tool.cpp 离线自检一遍 dat.json；读 diagnostics.hpp:222-225 的测试清单。

练习：(a) 给 dat.json 里某 NVSwitch 设备手写一个 `NVS[0-1]` 模式事件并用 ids.py 展开验证；(b) 解释 pc_event.hpp:35 的队列为何要掉电前持久化比对（提示：recoverFromPowerCycleEvents event_detection.hpp:260）；(c) 用 rascat_spec2code 生成一份最小事件配置并过 redfish_eventing_recipe_validator。

> 勘误警示：本仓类名与行数存在多处"文档挂错边"（DbusAccessorCore 不存在、tests_common 行数在 cpp、event_info/diagnostics 行数挂 hpp），详见上级 README.md 勘误清单（8 条）。
