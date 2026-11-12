# 讲透 nv-bmc-shmem 之二：metric 翻译层与 407 行的 generateURI

## 一、角色定位

`lib/utils/metric_report_utils.hpp` 是全仓最大的文件（**1715 行，实测 19 个 inline 函数**），承担 Redfish 语义的最后一公里：把 BMC 传感器的**裸值**（数字码、枚举原值、纳秒时长）翻译成 Redfish Telemetry 期望的**语义值与 URI**。bmcweb 从共享内存拿到的不只是 "37" 这样的读数，而是带 `metricProperty` URI 的完整条目——`SensorMapValue.metricProperty` 字段（`lib/include/shm_common.h:76` 附近的第三个字符串成员）就是本文件 `generateURI` 的产出。没有这一层，bmcweb 还得自己懂平台拓扑；有了它，**Redfish 知识被前置进 producer 侧的库**，客户端保持通用。

## 二、内部结构

文件是典型的**数据表驱动翻译层**，两大件：

**翻译函数族**（约 965 行之前 + 1408 之后）：PCIe 链路状态/速率翻译、功耗与在位判定、温控时长处理等，代表作 `getCpuPortMetricNames`（`:965`，从 devicePath 解出 portId 与 metric 名）。每个函数都是"查表+分支"的纯函数形态，输入输出全 `std::string`/整型，不碰共享内存——**纯函数性是 124 个单测能铺开的前提**。

**generateURI 巨无霸**（`:1002-1408`）：单个 **407 行**的 inline 函数，六参数签名 `(deviceType, deviceName, subDeviceName, devicePath, metricName, ifaceName)`（`:1002-1004`），体内按 `deviceType` 逐分支拼 URI——首分支 "PlatformEnvironmentMetrics" 从 `:1007` 开始。它把 Redfish URI 规范（`/redfish/v1/Chassis/.../Sensors/...` 或 MetricReport 内的 metricProperty 形态）按 NVIDIA 平台拓扑（机箱/设备/子设备/端口四级）硬编码展开。三处调用点在 `:1520/:1543/:1557`（不同聚合路径各自调用）。配套常量表（PDI→Redfish 映射、单位换算）内联在同文件。

兄弟件：`port_utils.hpp`（115 行，链路状态/电源输入类型两个枚举翻译）与 `time_utils.hpp`（599 行 12 个 inline 函数：duration 字符串↔数值、日期时间打包 uint、纳秒格式化——温控时长类 metric 的时间底座）。

## 三、外部连接

- **向上**：聚合器在组装对象时调用翻译族与 generateURI——`shm_sensor_aggregator.cpp` 的 `handleObjectInsertion`（`:359`）/`handleArrayUpdates`（`:412`）路径里 metricProperty 的填充即源于此；
- **向左（bmcweb）**：产出的 URI/语义值经 `SensorMapValue` 驻留段内，被 `getAllMRDValues`（`lib/telemetry_mrd_client.cpp:62`）读走组装 Redfish 响应——bmcweb 对 MRD 的 TAT（README.md:9-12 的 SLA 痛点）直接受益于"翻译前置"；
- **平台耦合**：meson 选项 `platformSystemId` 与 `deviceNamePrefix`（`meson_options.txt:4-11`，"Platform specific ... required to fill redfish metric property"）是 URI 平台段的注入点——翻译层不硬编码平台标识，构建期注入；
- **测试耦合**：`test/metric_report_utils_test.cpp`（**1212 行、124 用例**，全仓最大测试文件）逐函数锁行为，翻译表的每一格几乎都有对应用例；
- **横向**：`time_utils` 的 54 用例（`test/time_utils_test.cpp`，466 行）与 `port_utils` 的 9 用例（`test/port_utils_test.cpp`）构成工具箱的完整防锁。

## 四、数据流

一条 GPU 温度读数变成 Redfish metric 的路径：

1. producer 守护（如 gpumgrd）采到裸值，连同 devicePath（如 `/xyz/openbmc_project/sensors/temperature/GPU0Temp` 形态）交给 `AggregationService::updateTelemetry`（`telemetry_mrd_producer.cpp:83`）；
2. 聚合器 `parseDevicePath`（`shm_sensor_aggregator.cpp:63`）把路径解析成命名空间匹配（MatchingNameSpaces），确定该值属于哪个 MRD 命名空间；
3. 需要翻译的值进 metric_report_utils：数值单位/枚举码由翻译函数族归一为 Redfish 语义值（功耗、PCIe 链路状态走各自函数，端口类经 `getCpuPortMetricNames` `:965` 取名）；
4. `generateURI`（`:1002`）按 deviceType 分支拼 metricProperty URI——平台段来自 meson 注入的 systemId/前缀，设备四级（device/subDevice/port）来自路径，ifaceName 决定属性后缀；
5. 组装成 `SensorMapValue{sensorValue, timestampStr, metricProperty, timestamp}`（`shm_common.h:73-84`）经 Map 的 `updateValue`（`shmem_map.cpp:155`）写入段内；
6. bmcweb 侧 `getAllMRDValues` 批量取走，直接填进 MetricReport 响应——**零翻译零 D-Bus**，这正是 SLA 优化的落点。

## 五、设计决策

1. **翻译前置到 producer 侧**：把 Redfish 语义知识放进共享库而非 bmcweb——代价是库变厚（1715 行），收益是客户端通用且读路径零计算；这是"SLA 优化=把工作搬出热路径"的教科书执行；
2. **407 行单函数而非拆分**：generateURI 的各 deviceType 分支共享大量局部上下文（propSuffix、metricURI 前缀复用），拆分要把上下文参数化；测试靠输入/输出对锁行为（124 用例），重构安全网是测试而非函数体积——**"行数坏味道"在这里让位于表驱动的平铺可读性**；
3. **全 inline 头文件**：作为 header-only 库被 producer 侧多种守护包含，避免链接多个静态库版本；代价是每次包含都全量编译，CI 时长被 1715 行放大；
4. **平台参数构建期注入**：systemId/前缀走 meson 选项（`meson_options.txt:4-11`），同一份代码服务多平台——运行时零平台探测；
5. **纳秒级时间戳三重表示**：uint64 timestamp + timestampStr + metricProperty 并存（`shm_common.h:75-78`）——消费端排序用整型、展示用字符串、关联用 URI，一次写入三方受益，避免读侧格式化。

## 六、新人提示

- **别顺读 1715 行**：先看 `test/metric_report_utils_test.cpp` 的用例名（124 个即 124 个行为规约），按需跳到对应函数；generateURI 则直接跳 `:1002` 读签名与首个分支，其余分支同构；
- 改 generateURI 必须先加用例：407 行分支森林没有测试覆盖的改动等于盲飞——三处调用点（`:1520/:1543/:1557`）各自对应不同聚合路径，别只测一条；
- 新增平台支持时查 meson 选项而非源码：systemId 与设备名前缀是 URI 平台段的唯一注入点；
- 时间相关 metric 先读 `time_utils.hpp` 的 duration 互转（12 个函数），温控时长类翻译全部建立在它上面，54 个 time_utils 用例是最快的行为参考；
- 判断"某裸值该翻译成什么"时，PDI→Redfish 映射表（文件内的常量区）是权威——与 Redfish schema 的命名对齐以表为准，不要凭记忆拼 URI。
