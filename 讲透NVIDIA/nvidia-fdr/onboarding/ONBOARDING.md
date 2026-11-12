# nvidia-fdr Onboarding（OpenBMC Flight Data Recorder）

> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-fdr` @81d77403（133 文件）
> 图谱：`.understand-anything/knowledge-graph.json`（288 节点/478 边/5 层/6 步 tour，fingerprints 133@81d77403）
> 全部行号锚已对源码核实。

## 1. 定位：BMC 上的"飞行数据记录仪"（C++ 主体 + Python 工具线）

nvidia-fdr 是 NVIDIA 为 OpenBMC 生态写的 **Flight Data Recorder**——像飞机黑匣子一样在 BMC 上持续记录 GPU 服务器（HGX/GB200 NVL 机架）的遥测数据：按平台配置轮询 D-Bus/Redfish/共享内存三来源的数千个遥测点，protobuf 序列化落盘成 keeper/sample 文件，故障发生后离线解码分析。仓内两条语言线分工明确：

- **C++ 记录器（运行时主体）**：`fdr.hpp`+`fdr.cpp`（185+1482 行）为核心的 sd-event 守护进程，这是本仓的"产品本体"——**不是 Python 项目**（Python 只是离线工具线，任务书"Python 记录器"认知被源码推翻，README 勘误#1）；
- **Python fdrtool（离线解码）**：`fdrtool/fdrtool.py`（587 行）从 BMC 经 Redfish 拉 dump，`fdrtool/catalog/catalog.py`（613 行）解码成 JSON/SQLite/Influx 三后端。

构建面：meson（`meson.build:8` **cpp_std=c++23**，OpenBMC 生态的新标准档位）；依赖 sdbusplus/protobuf 3.20.3/yaml-cpp/spdlog（`README.md` 的 Ubuntu 22.04 环境清单）。

## 2. C++ 记录器核心：FlightDataRecorder_c

主类 `FlightDataRecorder_c`（`fdr.hpp:39` 声明，实测 52 个成员方法声明；图谱称 54，README 勘误#8），实现集中 in `fdr.cpp`（1482 行全仓最大）。三块关键状态：

- **RecList 三索引**（`fdr.hpp:43-52`）：全量 `RecList` vector（:43）+ 三个 map 索引——按轮询周期 `RecListPollMap`（:46）、按订阅存储周期 `RecListSubscribeStoreMap`（:49）、组轮询 `RecListGrpPollMap`（:52）；另有 O(1) 查询优化 map（`fdr.hpp:137`）。
- **四大 keeper 写手**（`fdr.hpp:61-64`）：BootEvent.dat / Compactor.dat / BookOfErrors.dat / ParamDescription.dat 四个元数据文件名常量，经 `CreateKeeperWriter`（`fdr.hpp:84`）创建 FDRStore 追加器。
- **生命周期方法链**（`fdr.cpp`）：构造 `fdr.cpp:55` → 限流器初始化 `fdr.cpp:168`（InitExceptionRateLimiter）→ 平台发现 `fdr.cpp:211`（FindAndLoadPlatformProfile）→ PPF 装载 `fdr.cpp:296`（ConvertPPFToStruct）→ 指纹规则 `fdr.cpp:322`（ExecuteFingerPrintRules）→ 磁盘配额检查 `fdr.cpp:342`。

入口 `main.cpp`（155 行）：`main.cpp:24` signalHandler、`main.cpp:96` 注册 SIGINT、`main.cpp:61`/`:67` 注册 AML 事件与 D-Bus 属性变更信号、`main.cpp:125` 主循环处理 dbus 消息。定时器引擎 `fdr_timers.cpp`：单记录轮询回调走 RefreshAndStore（`fdr_timers.cpp:161`）、组轮询走 GroupRefreshAndStore（`fdr_timers.cpp:186`）、订阅刷出走 `fdr_timers.cpp:194` SubscribeStoreRecordTimerCBEngine。

## 3. PPF 平台配置与策略层：数据字典

PPF（Platform Profile File）是 FDR 的"数据字典"——`fdr_policy.hpp`（782 行）定义其内存模式：`fdr_policy.hpp:19-25` 的 7 个单行 struct 是**前向声明**（tree-sitter 误计为类，README 勘误#3），真实数据结构从 :27 FingerPrint_t 到 :241 Profile_t 共 21 个（Section/Component/InfoGroup/Info 四级遥测树 + Dbus/Redfish/Shmem 三来源参数 + DeviceDump 全配置），YAML 绑定靠文件后半部的 17+ 个 yaml-cpp `convert<>` 特化（`fdr_policy.hpp:254` 起）。**`fdr_policy.cpp` 是磁盘 0 字节空文件**（README 勘误#2）——策略逻辑全在 hpp 的模板特化里。装载期防线 `ppf_sanity.hpp:20` PPFSanity（:28 UniqueParamChecker 模板查重、:32 SanityTestPPF）。

平台清单 `platforms/` 共 9 份 PPF：教学样本 `platforms/fdr_ppf_example.yaml`（303 行）+ 8 个真实平台——`platforms/fdr_ppf_gb200nvl_hmc_1GPU.yaml`（13441 行）/`_2GPU`（13449）、`platforms/fdr_ppf_gh200_hmc.yaml`（1368）、`platforms/fdr_ppf_hgxb300_hmc.yaml`（43212）、`platforms/fdr_ppf_hgxb_hmc.yaml`（44772）、`platforms/fdr_ppf_hgxr_hmc.yaml`（44255）、`platforms/fdr_ppf_vr-nvl-hmc.yaml`（**全仓最大 69215 行**）、`platforms/fdr_ppf_vulcan.yaml`（14183）。生成通道：`automation/yaml_generator.py`（1061 行 20 函数）读 `automation/TelemetryCatalog0.1.csv`（5942 行，多行表头 CSV，NOTES batch-8 甄别）+ dbus-expansion.csv + ppf_input.yaml，展开变量（nvlink 0-17）产出四级树——:471 expand_nvlink_entries、:860 读 TelemetryCatalog 命名空间、:950 load_platform_config、:1007 main；产物落 `automation/generated/`（如 fdr_ppf_gb200nvl-hmc.yaml，勿手编）。

## 4. 数据面：三来源取值 + protobuf 存储

**Record 记录单元**（`fdr_record.hpp` 声明，`fdr_record.cpp` 700 行实现）：每条遥测参数一个 Record。取值按 `FetchMethod` 分派三来源（`fdr_record.cpp:55` 判 "Shmem"）：D-Bus（经 `dbus_accessor.hpp` 抽象，测试用 `tests/mockDbusAccessor.hpp` 替身）、Redfish（`fdr_redfish.hpp:20` RedfishClient，:38 login/:39 logout，基于 `fdr_http.hpp` 的 HttpClient）、共享内存 MRD（`fdr_grp_update.cpp:17` include telemetry_mrd_client.hpp；组刷新数据源**实为 MRD 共享内存而非 D-Bus**——`fdr_grp_update.cpp:26` 注释明示 "only supported Fetch Method is Shmem"，:29 调 `nv::shmem::sensor_aggregation::getAllKeyValuePair`，README 勘误#5）。值刷新入口 `fdr_record.cpp:83` RefreshValue / `fdr_record.cpp:136` Refresh；类型库 `property_variant.hpp` 用 std::variant 全类型别名覆盖 OpenBMC 属性。

**存储引擎 FDRStore**（`fdr_store.hpp` 声明，`fdr_store.cpp` 208 行）：protobuf 编码的样本文件读写器——`fdr_store.cpp:74` append 用 `SerializeDelimitedToOstream`（:101）长度前缀追写，`fdr_store.cpp:110` readnext 用 `ParseDelimitedFromZeroCopyStream`（:139）游标读回，另支持 JSON 编码模式（:82 MessageToJsonString）。**线格式契约 `fdr_logs_schema.proto`**（143 行 proto3，package fdrpb，实测 **11 个 message**，图谱称 12，README 勘误#7）：`fdr_logs_schema.proto:5` fdr_sample（oneof 三型值）、:15 fdr_stat、:27 fdr_params、:37 fdr_compactor_bookkeep、:41 fdr_book_of_errors、:53 fdr_event、:68 fdr_boot_event、:83/:106/:130 device_dump 三件套——C++ 记录器与 Python fdrtool 共用同一份序列化契约（fdrtool 侧 protoc 生成 fdr_logs_schema_pb2.py，属生成物不发仓内边，NOTES batch-5 甄别）。

## 5. 生命周期机制：压缩/设备 dump/事件/限流

- **压缩器**（`fdr_compact.cpp` 937 行）：CompactorEngine 把最老目录的样本合并成 HighFidelity 高保真文件腾空间——`fdr.cpp` 的 CompactionWindowTimerCBEngine/CompactionSubWindowTimerCBEngine（`fdr.hpp:89-90`）双窗口定时驱动，BookOfErrors 记录压缩期错误事件。
- **设备 dump 状态机**（`fdr_device_dump.hpp:46` `enum class DumpState`；`fdr_device_dump.cpp` 909 行）：`fdr_device_dump.hpp:95` DeviceDumpHandler 按事件触发 GPU 诊断收集——:152 collectDump → :169 callGetDiagnostics → :186 tickContext → :195 pollAsyncStatus → :207 cleanupContext → :218 onDumpComplete；异常恢复 :252 startupRecoveryScan、失败记录 :274 recordCollectionFailure、:301 appendDumpRecord。存储管理 `fdr_device_dump_store.cpp`（350 行）管 dump 文件入库/索引/逐出。
- **事件子系统**（`fdr_events.hpp:21` EventRecord / :35 EventSignalHandler，:43 sdbusplus::bus::match_t 信号匹配）：监听 D-Bus InterfacesAdded 等信号转事件记录，`fdr_events.cpp`（502 行）实现解析与注册。
- **异常限流**（`fdr_common.hpp:60` LeakyBucket；`fdr_common.cpp:207` 实现）：漏桶算法限制错误日志频率，配合 `fdr_log.cpp`（125 行）的相同消息按窗口计数节流——BMC 上防日志风暴的标准姿势。
- 公共工具 `fdr_common.hpp`：exec/split/转换/低磁盘告警 + 组轮询 key 解析（getGroupPollRecordKey/splitGroupFetchKeys）。

## 6. fdrtool 解码链与数据校验（Python 线）

**主流程**（`fdrtool/fdrtool.py`）：`fdrtool/fdrtool.py:381` CollectFdrDump 经 Redfish 从 BMC 收 dump（:391 调 LogService.CollectDiagnosticData action；:25 import redfish 库），`fdrtool/fdrtool.py:83` decodingDump 调 Catalog 解码，`fdrtool/fdrtool.py:153` main 串起收集→解包→多后端入库；DEMO 模式 :531 CollectFdrDump_DEMO 走本地样例；`-ul/--use_local` 支持离线 tar（:176）。配置 `fdrtool/config.yaml`（BMC 地址/凭据/后端，configargparse 消费）。

**解码核心**（`fdrtool/catalog/catalog.py:70` class Catalog）：dump 包装载 → cobsr 解包 + protobuf varint 解码——`fdrtool/catalog/catalog.py:422` `_DecodeVarint32` 读长度前缀、`:452` `cobsr.decode` 去 COBS-R 帧封装 → 版本校验（:104 VersionMisMatch）→ CatalogEntry 按 keeper/样本文件分流到三后端：`fdrtool/catalog/json.py`（JSON 文件）、`fdrtool/catalog/influx.py`（InfluxDB 时序，LineProtocol+批量回调）、`fdrtool/catalog/sqlite.py`（SQLite 建表+跨 dump 联合视图 CreateCombinedViews）。注意 `fdrtool/catalog/json.py` 顶部 `import json` 是 stdlib——scanner 曾误报为仓内 json.py 自引用已剔除（README 勘误#4）。

**数据校验臂**（`tools/data_validation/`）：`tools/data_validation/data_validator.py`（269 行）双向 diff 比对 telemetry-agent 输出与 FDR dump 数值一致性；`tools/data_validation/check_fdr_telemetry_coverage.py`（355 行）+`telemetry_catalog.py`（1007 行，Catalog/CatalogEntry/URIExpansion 三类、GetMrdList/FetchMRDValues 取 MRD 值）做平台级覆盖检查；四平台豁免清单 `tools/data_validation/platform/exempt_telemetry_list_*.yaml`（VR-NVL 89 行最全）。PPF 编写期侦察工具 `tools/dbus_dump/dbus_dump.sh`（413 行 bash **14 个函数**，tree-sitter 全部抓到——script 类别非盲区，README 勘误#6）：get_all_services→introspect_object→create_yaml_output 把 D-Bus 树转 YAML。

## 7. 构建测试与生态位 + 上手路线

- **测试**：`tests/` 13 个 .cpp——**真 gtest**（与 nvbench 的自研断言相反，`meson.build:124` googletest subproject），6 个套件：FdrCommon（`tests/fdr_common_test.cpp:25` TEST(FdrCommon, SplitBasic) 等）/FdrHttp/FdrLog/FdrPolicy/FdrRedfish/PropertyVariant + `tests/fdr_redfish_stub_test.cpp`（g_stubHttpResponse 全局桩注入 HTTP 行为）+ `tests/test_stubs.cpp` 链接桩（脱离 BMC 环境单测）。仓根还有 BLOCKED_TESTS.md/FAILING_TESTS.md/COVERAGE_NOTES.md 三份测试状态文档与 `benchmarkCode/benchmarkTest.cpp`（419 行 protobuf 编解码基准，google benchmark 框架）。
- **部署**：`Dockerfile` 容器化；Yocto 集成走 `fdr_git.bb`——**recipetool 原始模板**（`fdr_git.bb:12` LICENSE="CLOSED" 占位、:27 `inherit cmake` 但仓内无 CMakeLists（构建走 meson）、:30 EXTRA_OECMAKE="-DYOCTO=ON" 全仓零消费者，README 勘误#9）。
- **生态位**：OpenBMC phosphor 生态的 NVIDIA 增量——D-Bus 访问经 sdbusplus（系统依赖），MRD 共享内存对接 nv-bmc-shmem 的 sensor_aggregation 命名空间，遥测语义与 TelemetryCatalog 对齐。

**上手路线**：① 读 `README.md` 装依赖，meson 编译跑通 6 套件；② 从 `platforms/fdr_ppf_example.yaml`（303 行教学样本）对照 `fdr_policy.hpp` 的结构读懂 PPF 四级树；③ 跟 fdr.cpp:55 构造链走一遍启动流程（平台发现→PPF 装载→指纹→建 Record→定时器）；④ 离线侧用 fdrtool DEMO 模式（--use_local）跑通解码三后端；⑤ 改平台配置前先看 automation/yaml_generator.py 的生成通道——手编 PPF 会被生成物覆盖。
