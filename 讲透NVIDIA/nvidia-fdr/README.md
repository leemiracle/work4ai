# 讲透 nvidia-fdr

NVIDIA [nvidia-fdr](https://github.com/NVIDIA/nvidia-fdr)——OpenBMC Flight Data Recorder：BMC 上的 GPU 服务器"飞行记录仪"。C++ 记录器（`FlightDataRecorder_c`，fdr.hpp+fdr.cpp 1482 行）按平台 PPF 配置轮询 D-Bus/Redfish/MRD 共享内存三来源遥测，protobuf+C 面编码落盘；Python fdrtool 离线经 Redfish 收 dump，cobsr+varint 解码进 JSON/SQLite/Influx 三后端。9 平台 PPF 配置最大单文件 69215 行（VR-NVL HMC）。

## 全链状态表

| 阶段 | 状态 | 明细 |
|---|---|---|
| understand 图谱 | ✅ | 288 节点 / 478 边 / 5 层 / 6 步 tour，validator 0 issues（仓内 `.understand-anything/knowledge-graph.json`） |
| fingerprints | ✅ | 133 文件基线 @81d77403 |
| onboarding | ✅ | [ONBOARDING.md](onboarding/ONBOARDING.md) 7774 字（不计空格）7 节 46 锚（全路径行号锚终验 0 坏） |
| explain | ✅ | 3 篇六节结构：[01 FlightDataRecorder_c 核心](explain/01-FlightDataRecorder_c核心.md) / [02 MRD 与 Redfish 与策略引擎](explain/02-MRD与Redfish与策略引擎.md) / [03 fdrtool 解码链](explain/03-fdrtool解码链.md) |

（DeepWiki 收录状态见仓内 deepwiki/ 目录；本图谱与讲透产物为源码级知识源。）

## 结构速览

- **C++ 记录器**：`fdr.hpp:39` FlightDataRecorder_c（52 方法）+ `fdr.cpp`（1482 行）——RecList 三索引（轮询/订阅/组轮询）+ 四 keeper 写手（BootEvent/Compactor/BookOfErrors/ParamDescription .dat）+ sd-event 定时器（`fdr_timers.cpp` 三回调引擎）
- **策略层**：`fdr_policy.hpp`（782 行 21 数据结构 + 17+ yaml-cpp convert<> 特化）定义 PPF 四级遥测树（Section/Component/InfoGroup/Info）；`ppf_sanity.hpp` 装载期查重
- **平台配置**：`platforms/` 9 份 PPF（example 303 行教学样本 → VR-NVL 69215 行）；生成通道 `automation/yaml_generator.py`（1061 行）吃 TelemetryCatalog0.1.csv（5942 行）
- **数据面**：Record 三来源取值（`fdr_record.cpp:55` 分派）；存储 `fdr_store.cpp`（protobuf delimited 追写/游标读回）；线格式 `fdr_logs_schema.proto`（proto3/11 message，C++/Python 共用）
- **生命周期**：压缩器 `fdr_compact.cpp`（937 行 HighFidelity 合并）、设备 dump 状态机 `fdr_device_dump.cpp`（909 行）、事件 `fdr_events.cpp`（502 行）、LeakyBucket 限流（`fdr_common.hpp:60`）
- **Python 线**：`fdrtool/`（fdrtool.py 587 + catalog.py 613）解码三后端；`tools/data_validation/` 校验臂；`tools/dbus_dump/dbus_dump.sh`（413 行）PPF 侦察
- **测试**：`tests/` 13 个 .cpp / 6 个 gtest 套件（FdrCommon/FdrHttp/FdrLog/FdrPolicy/FdrRedfish/PropertyVariant），stub 注入可脱离 BMC 单测

## 勘误清单（源码实证，全部行号已核）

1. **运行时主体是 C++ 记录器，不是 Python**：任务书初始认知"Python 记录器"被源码推翻——Python 只占离线工具线（fdrtool 解码 + data_validation 校验），记录器/存储/定时器/压缩器全是 C++（`fdr.cpp` 1482 行为全仓最大源文件）。
2. **`fdr_policy.cpp` 是 0 字节空文件**（wc -c 实证）：策略逻辑全部在 `fdr_policy.hpp` 的 yaml-cpp `convert<>` 模板特化（`:254` 起 17+ 个）里，没有独立实现文件；图谱初稿曾按正常源文件建节点。
3. **前向声明误计为类**：`fdr_policy.hpp:19-25` 的 7 个单行 struct（Profile_t/GeneralConfig_t/Section_t/Component_t/InfoGroup_t/Info_t/DeviceDumpProfile_t）是前向声明，tree-sitter 误计为类定义——批阶段甄别不建节点（NOTES batch-4）；真实数据结构 21 个（:27-241）。
4. **json 自引用是误报已剔除**：`fdrtool/catalog/json.py` 顶部 `import json` 是 stdlib，scanner 误报为仓内 json.py 自引用边；仅 `from catalog.catalog import` 是真依赖（NOTES batch-5 甄别记录）。同批甄别：`fdrtool/fdrtool.py:163-164` 的延迟 import 校验臂为 scanner 漏采手补；`fdr_logs_schema_pb2` 是 protoc 生成物不发仓内边。
5. **bash 函数可提取，修正规范预期**：`tools/dbus_dump/dbus_dump.sh`（413 行）14 个函数被 tree-sitter bash 解析器全部抓到——"shell/PowerShell 需正则手扫"的预期在 bash script 类别不成立（NOTES batch-14-2 实证修正；PowerShell .psm1 仍需手扫，参照 nvbench 仓）。
6. **proto 是 11 个 message 不是 12**：`fdr_logs_schema.proto` grep -c "^message" = 11（fdr_sample/fdr_stat/fdr_params/fdr_compactor_bookkeep/fdr_book_of_errors/fdr_event/fdr_event_details/fdr_boot_event/fdr_device_dump_failure/fdr_device_dump_record/fdr_device_dump）；图谱节点摘要写 12。
7. **组刷新数据源是 MRD 共享内存，不是 D-Bus**：`fdr_grp_update.cpp:17` include telemetry_mrd_client.hpp，`:26` 注释明示 "only supported Fetch Method is Shmem now"，`:29` 调 `nv::shmem::sensor_aggregation::getAllKeyValuePair`——组轮询批量拉共享内存命名空间，D-Bus 只服务单记录轮询线。
8. **FlightDataRecorder_c 是 52 个方法声明，不是 54**：`fdr.hpp:39-185` 逐行实测 52 个成员方法声明；图谱 hub 节点写"54 方法"（口径差可能来自构造/析构计法）。
9. **`fdr_git.bb` 是 recipetool 原始模板，不可直接构建**：`:12` LICENSE="CLOSED" 占位（注释自认需人工修订）；`:27` `inherit cmake` 但仓内**没有 CMakeLists.txt**（构建走 meson）；`:30` `EXTRA_OECMAKE="-DYOCTO=ON"` 全仓 grep 零消费者——Yocto 集成是未完成的骨架。
10. **重复拷贝与薄壳**：`tools/TestingAndyamlgeneration/newparamIDarrange.py` 与 `tools/newparamIDarrange.py` 逐字节同内容（历史目录遗留）；`tools/TestingAndyamlgeneration/yaml-generator.py` 是 27 行薄壳，真实逻辑在 `automation/yaml_generator.py`（NOTES batch-13/14 甄别）。

## 工艺备注

- 批阶段 29 条甄别笔记已收割至仓内 `.understand-anything/NOTES-DIGEST.md`（PPF 四级树/MRD 甄别/imports 对账/生成物通道等）。
- 任务书"C++ 手扫 519 条/.cuh 全盲"系 nvbench 仓工艺数字；本仓 C++ 以 .hpp/.cpp 为主，tree-sitter 盲区集中在前向声明（勘误#3）与 TEST 宏展开（NOTES batch-2：TEST 名即测试用例名）。
- 字数口径：onboarding/explain 均按"不计空格字符"统计；锚点为全路径 `path:line`，终验对 133 文件基线全量界内检查 0 坏。
