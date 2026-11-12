# 讲透 nv-bmc-shmem：BMC 共享内存遥测库 Onboarding

> 仓库：`NVIDIA/nv-bmc-shmem` @ commit `e9193cbc`｜图谱 120 节点/149 边/6 层/8 步导览，fingerprints 68 文件
> 本文所有 `file:line` 锚均为主会话对源码逐一核实的结果（2026-11-09）。

## 一、这个仓库是什么：把 bmcweb 的 MRD 请求从 D-Bus 搬进共享内存

这是 NVIDIA BMC（板管控制器）生态里的**遥测共享内存库**，meson 工程名 `nvshmem`（`meson.build:2`，语言声明 `'cpp'` 在 `:3`）。动机写在 README 开头：现有架构中 bmcweb（OpenBMC 的 Redfish HTTP 服务）对 MRD（Metric Report Definition）请求走 Object manager 风格 D-Bus 调用，逐属性取值导致 "% PID loop outliers and maximum MRD TAT crossing the SLAs"（`README.md:9-12`）——Redfish 遥测接口的尾延迟击穿 SLA。解法：各传感器生产者把 Redfish 响应所需的 metric 数据直接写进**POSIX 共享内存**，bmcweb 作为客户端按命名空间读取，"significant reduction in processing time of MRD requests in bmcweb"（`:17-22`）。角色三角：**producer（gpumgrd/hwmontemp 等守护）→ 共享内存段（boost::interprocess）→ client（bmcweb）**，库为两端各提供一组 API（`README.md:35-39` 的 External API requirements）。

三个立即要钉住的事实：其一，**这是纯 C++ 项目**——meson 声明 `'cpp'`（`meson.build:3`）、`cpp_std=c++23`（`meson.build:7`）、`warning_level=3` + `werror=true`（`meson.build:8-9`）；其二，producer/client 都是**库**而非进程（`lib/meson.build:35` 只产 `libnvshmem` static_library，进程角色由使用方扮演）；其三，遥测就绪语义有明确约定——Redfish 客户端应先经 Telemetry 就绪信号再查 MRD 属性（`README.md:329-333`）。

## 二、分层全景：六层地图与工程配置

| 层 | 内容 | 代表文件（锚） |
|---|---|---|
| L01 工程配置（13 文件） | meson 构建/选项、十种 linter 忽略清单、clang-format | `meson.build:3`、`meson_options.txt:1-3`、`.clang-format` |
| L02 共享内存底座（9 文件） | 契约结构 + RAII 段管理 + 驻留 map | `lib/include/shm_common.h:73`、`lib/impl/managed_shmem.hpp:47`、`lib/impl/shmem_map.hpp:52` |
| L03 配置与聚合（7 文件） | 两份运行时 JSON + ConfigReader + 聚合器 + 门面 | `lib/config_json_reader.cpp:29`、`lib/shm_sensor_aggregator.cpp:63` |
| L04 MRD 接口与翻译（7 文件） | producer/client API + 值翻译工具箱 | `lib/telemetry_mrd_producer.cpp:28`、`lib/utils/metric_report_utils.hpp:1002` |
| L05 诊断工具（3 文件） | 两个独立 main | `tools/nv_shmem_tool.cpp:36`、`tools/aggregation_service_tester.cpp` |
| L06 测试与文档（29 文件） | 16 组 gtest + JSON 夹具 + 离线桩 | `test/metric_report_utils_test.cpp`、`test/stubs/phosphor-logging/lg2.hpp` |

运行时配置两份 JSON：`configurations/shm_namespace_config.json`（194 行，SensorNamespaces：命名空间/传感器类型/producer 映射）与 `configurations/shm_mapping.json`（36 行，Namespaces：**按命名空间**给段尺寸与 producer 绑定——PlatformEnvironmentMetrics 131072B 双 producer（gpumgrd+hwmontemp）、NVSwitchPortMetrics 1024000B、ProcessorMetrics 262144B……并非单一全局段）。meson 选项除 `libonly/tests/nvidia-shmem`（`meson_options.txt:1-3`）外还有五个平台项：平台 system id、设备名前缀（填 Redfish metric property 用）、debug traces、**logSuppressInterval 与 maxLogEntries**（日志抑制窗口与上限，`:4-33`）。

## 三、共享内存底座：契约、RAII 与驻留容器

三层底座自下而上：

**数据契约**（`lib/include/shm_common.h`，115 行）：`SensorMapValue`（`:73-84`）是驻留共享内存的值类型——用 boost interprocess 的 `char_string_t`（带分配器的字符串）存 sensorValue/timestampStr/metricProperty，`uint64_t timestamp`；`SensorValue`（`:86-94`）是进程本地的镜像类型（std::string）。debug 宏 `SHMDEBUG` 直通 phosphor-lg2（`:27-29`）。**注意这是 C++ 头**（lg2/boost/std 都在用），尽管扩展名是 .h。

**段管理**（`lib/impl/managed_shmem.hpp` 88 行 + `lib/managed_shmem.cpp` 85 行）：`ManagedShmem`（`:47`）以 RAII 持有 `managed_shared_memory` 段与**命名 upgradable 互斥**（段名+"lock"，创建路径 `managed_shmem.cpp:31`，打开路径 `:62`）。读锁 `TryReadLock`（声明 `hpp:60`，实现 `cpp:73-85`）返回 `shmem_read_lock_t`（`hpp:39`，`sharable_lock<named_upgradable_mutex>`）——语义是**带 1 秒绝对超时的尝试**：`microsec_clock::universal_time()+seconds(1)` 构造，取不到直接抛 `LockAcquisitionException`（`hpp:70`）；返回的锁对象必须保持在作用域内。另两个异常 `BadMapException`（`:77`）与 `PermissionErrorException`（`:82`）。

**驻留容器**（`lib/impl/shmem_map.hpp` 190 行 + `lib/shmem_map.cpp` 224 行）：模板 `Map<MapType, ValueType>`（`shmem_map.hpp:51-52`，类注释 "Shared Memory Implementation for object type Map"）**继承 ManagedShmem**，把关联容器直接构造进共享段——分配器用段管理器的 `void_allocator_t`。显式实例化 `Map<SensorMap, SensorValue>` 的双构造器在 `shmem_map.cpp:26` 与 `shmem_map.cpp:46`，操作面：`getAllKeyValuePair`（`shmem_map.cpp:57`）、`getAllValues`（`shmem_map.cpp:72`）、`getValue`（`shmem_map.cpp:113`）、`updateTimestamp`（`shmem_map.cpp:129`）、`updateValue`（`shmem_map.cpp:155`），析构在 `shmem_map.cpp:87`。

## 四、配置装载、聚合器与库门面

**ConfigReader**（`lib/impl/config_json_reader.hpp` 110 行 + `lib/config_json_reader.cpp` 253 行）是静态门面：两份 JSON 各一个加载入口 `loadNamespaceConfig`（`config_json_reader.cpp:29`）/`loadSHMMappingConfig`（`config_json_reader.cpp:57`，惰性触发点在 `config_json_reader.cpp:227`），产出接口 `getProducers`（`config_json_reader.cpp:85`）、`getNameSpaceConfiguration`（`config_json_reader.cpp:114`）、`getSHMSize`（`config_json_reader.cpp:163`）与 **MRD 命名空间查找表** `getMRDNamespaceLookup`（`config_json_reader.cpp:222`）。异常路径按五类畸形各有独立测试（nofile/null/malformed/no_ns/no_producers，见第六节）。

**SHMSensorAggregator**（`lib/impl/shm_sensor_aggregator.hpp` 234 行 + `lib/shm_sensor_aggregator.cpp` 623 行）是写面主力，方法链即数据流水线：`parseDevicePath`（`shm_sensor_aggregator.cpp:63`，设备路径→命名空间匹配）→ `createShmemNamespace`（`shm_sensor_aggregator.cpp:159`）→ `insertShmemObject`（`shm_sensor_aggregator.cpp:201`）→ `handleObjectInsertion`（`shm_sensor_aggregator.cpp:359`）/`handleArrayUpdates`（`shm_sensor_aggregator.cpp:412`）→ `updateSHMObject`（`shm_sensor_aggregator.cpp:509`）统一入口；辅助件 `getMatchCount`（`shm_sensor_aggregator.cpp:31`）、`getSensorMapKey`（`shm_sensor_aggregator.cpp:273`）、`updateNanValue`（`shm_sensor_aggregator.cpp:280`，NaN 遥测值的特殊处理）。

**ShmSensorMapIntf**（`lib/impl/shm_sensormap_intf.hpp:39`，302 行）是库的 C++ 门面：把"命名空间存在性/创建/增删改查/时间戳更新"收敛成单一入口，`updateTimestamp` 的命名空间遍历在 `:142`，未知命名空间走 lg2 错误日志（`:155/:163` 等四处）。

## 五、MRD 接口与值翻译：从裸值到 Redfish URI

**producer 侧**（`lib/include/telemetry_mrd_producer.hpp` 161 行 + `lib/telemetry_mrd_producer.cpp` 113 行）：`AggregationService` 是服务对象（静态聚合器指针在 `cpp:26`），两个入口 `namespaceInit`（`:28`，按进程名建命名空间与段）与 `updateTelemetry`（`:83`，周期写入遥测值；聚合器实例化在 `:50`）。

**client 侧**（`lib/include/telemetry_mrd_client.hpp` 103 行 + `lib/telemetry_mrd_client.cpp` 136 行）：两个自由函数 `getAllMRDValues`（声明 `hpp:62`，实现 `cpp:62`——bmcweb 按 MRD 命名空间取全量 `SensorValue` 列表）与 `getAllKeyValuePair`（`hpp:76`/`cpp:40`）；异常契约 `NameSpaceNotFoundException`（`cpp:58/:118` 两处抛点）与 `NoElementsException`（`:110`）——README `:199` 明言客户端应预期异常而非错误码。

**值翻译工具箱**是全仓最大的头：`lib/utils/metric_report_utils.hpp` **1715 行、实测 19 个 inline 函数**（`grep -c '^inline'`），把 BMC 传感器裸值翻译为 Redfish 语义（PCIe 链路状态/速率、功耗、在位、温控时长……）并构造 MRD URI。**巨无霸是 `generateURI`（`:1002-1408`）——单个 407 行函数**，按 deviceType 分支（如 "PlatformEnvironmentMetrics" 在 `:1007` 起）拼 Redfish URI，三处调用点在 `:1520/:1543/:1557`。配套小件：`port_utils.hpp`（115 行，链路状态/电源输入枚举翻译）、`time_utils.hpp`（599 行 12 个 inline 函数，duration 字符串互转、日期时间打包 uint、纳秒格式化）、`getCpuPortMetricNames`（`metric_report_utils.hpp:965`）。

## 六、诊断工具与测试体系：299 个用例的防线

**两个诊断 main**：`tools/nv_shmem_tool.cpp`（183 行）带 trace 计时地枚举/读出传感器库内容——`steady_clock` 别名 `:25`、变参 `trace()` `:29`、`main` `:36`，输出段创建/剩余空间/逐传感器 `metricProperty:timestampStr:value`（`:53-59`）；`tools/aggregation_service_tester.cpp`（256 行）手动驱动 AggregationService 全流程的冒烟驱动器。

**测试面是本仓的硬资产**：16 个 gtest 文件、合计 **299 个用例**（实测 `TEST`/`TEST_F` 计数：metric_report 124 + time_utils 54 + sensor_map 20 + producer 29 + client 8 + port_utils 9 + error_logger 5 + shm_sensormap_intf 10 + shmem_map_extra 14 + config_json_reader 主套 10 + 五类异常路径 16）。三巨头：`test/metric_report_utils_test.cpp`（**1212 行 124 用例**，翻译/URI/枚举全覆盖）、`test/time_utils_test.cpp`（466 行 54 用例）、`test/telemetry_mrd_producer_test.cpp`（375 行 29 用例）。工程化细节：phosphor-lg2 被最小桩替换（`test/stubs/phosphor-logging/lg2.hpp`，57 行——真 lg2 的模板转换器在离线环境拉不动）；异常路径测试用 `test/cfg_*/meson.build` 注入对应夹具（如 `test/cfg_malformed/meson.build`）；分支覆盖由 `gcovr.cfg`（13 行）统计，README 有专门章节说明。`lib/meson.build:7` 依赖 `phosphor-logging`（OpenBMC 标准日志库）——这是本仓与 OpenBMC 生态的接缝。

## 七、设计决策、坑与新人路线

**五个关键设计决策**：

1. **共享内存换 D-Bus**：MRD 请求路径从"逐属性 Object manager 调用"变成一次段读取，SLA 优化的本质是**把 N 次 IPC 摊平成 0 次**（数据已在内存）；
2. **boost::interprocess + 命名 upgradable 锁**：多读单写场景 sharable_lock 并行读、写侧独占升级；TryReadLock 的 1 秒超时把"锁饥饿"转成显式异常让调用方决策，而非无限等；
3. **按命名空间分段**：段尺寸随数据量分级（131072B vs NVSwitchPortMetrics 的 1024000B），坏域隔离与容量规划都以命名空间为单位；
4. **翻译表全内联头文件**：1715 行 metric_report_utils.hpp 是数据表驱动的翻译层，124 个用例锁行为——平台差异（system id/设备名前缀）外置到 meson 选项而非硬编码；
5. **C++23 + werror + 全量 gtest**：库以 OpenBMC 子项目（libonly 选项，`meson_options.txt:1`）和独立工程双形态存在，质量门槛对齐 bmcweb 生态。

**新人路线**（对应图谱 8 步导览）：README 动机段（`:9-22`）→ `shm_common.h`（115 行契约）→ `managed_shmem.cpp`（85 行 RAII/锁全貌）→ `shmem_map.hpp` 模板（190 行）→ 跑 `nv_shmem_tool` 看真实段内容 → producer/client 头文件（161+103 行）→ 按需深入 metric_report_utils（从 124 用例反推函数行为比顺读 1715 行快）。

**三个坑**：把 `SensorMapValue`（interprocess 布局）与 `SensorValue`（进程本地）混用——前者带分配器不能跨段直接拷；以为 TryReadLock 是无阻塞 try——它是 1 秒绝对超时后抛异常；以为 SHM 有全局单一尺寸——每个命名空间各一段各一尺寸，`getSHMSize`（`config_json_reader.cpp:163`）按命名空间查。
