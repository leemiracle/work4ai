# 02 PPF 策略引擎与三数据源：MRD 共享内存、Redfish、D-Bus

## 角色定位

这一篇覆盖 FDR 的"配置面+数据面"。配置面：`fdr_policy.hpp`（782 行）是 PPF 平台配置的内存模式——YAML 装载后全系统按它建 Record、配定时器、定压缩策略；数据面：Record 取值的三条来源（D-Bus 属性/Redfish REST/MRD 共享内存），**组刷新走 MRD 而非 D-Bus** 是最易搞错的事实（README 勘误#5）。

## 内部结构

**策略层 21 个数据结构**（`fdr_policy.hpp:27-241`）：FingerPrint_t（:27 平台指纹）→ GeneralConfig_t（:40）→ 三来源参数 DbusParams_t/ShmemParams_t/RedfishParams_t（:74-92）→ 四级遥测树 Info_t（:98）/InfoGroup_t（:127）/Component_t（:143）/Section_t（:154）→ Preconditions（:162-172）→ DeviceDump 六结构（:181-225）→ Profile_t（:241 总根）。`fdr_policy.hpp:19-25` 的 7 个单行 struct 是前向声明（README 勘误#3）。YAML 绑定靠 17+ 个 yaml-cpp `convert<>` 特化（`fdr_policy.hpp:254` 起）——**`fdr_policy.cpp` 是 0 字节空文件**（README 勘误#2）。装载校验 `ppf_sanity.hpp:28` UniqueParamChecker 查重参数 ID。

**三来源通道**：
- D-Bus：`dbus_accessor.hpp` 抽象访问器（属性读写/信号注册），生产实现走 sdbusplus，测试用 `tests/mockDbusAccessor.hpp` 替身；
- Redfish：`fdr_redfish.hpp:20` RedfishClient（:38 login/:39 logout）会话化封装 BMC REST，底座是 `fdr_http.hpp` 的 HttpClient/HttpResponse；JSON 取值用 nlohmann json_pointer（`fdr_redfish.hpp:53` 注释明示）；
- MRD 共享内存：`fdr_grp_update.cpp:17` include telemetry_mrd_client.hpp，`fdr_grp_update.cpp:26` 注释 "only supported Fetch Method is Shmem now"，:29 调 `nv::shmem::sensor_aggregation::getAllKeyValuePair` 一次拉全命名空间键值对再分发给组内 Record（nv-bmc-shmem 生态接口）。

**Record 取值分派**（`fdr_record.cpp`）：`fdr_record.cpp:55` 按 `info.FetchMethod == "Shmem"` 分流；刷新 `fdr_record.cpp:136` Refresh → `fdr_record.cpp:83` RefreshValue 转 PropertyVariant（`property_variant.hpp` 的 std::variant 类型库）；统计引擎滚 min/max/avg 落 statfile。

## 外部连接

- 上游：`fdr.cpp:296` ConvertPPFToStruct 装载 PPF；`fdr_timers.cpp:161`/`:186` 两个定时回调分别驱动单记录刷新与组刷新。
- 平台配置：`platforms/` 9 份 PPF——`platforms/fdr_ppf_vr-nvl-hmc.yaml`（69215 行全仓最大）、`platforms/fdr_ppf_hgxb_hmc.yaml`（44772）、`platforms/fdr_ppf_example.yaml`（303 行教学样本）；生成通道 `automation/yaml_generator.py:471` expand_nvlink_entries 按变量模板展开（nvlink 0-17），原料是 `automation/TelemetryCatalog0.1.csv`（5942 行）。
- 下游：刷新后的值进 FDRStore；离线侧 `tools/data_validation/telemetry_catalog.py` 的 FetchMRDValues 也读 MRD 做覆盖校验——同一数据源两端对账。

## 数据流

PPF YAML → ConvertPPFToStruct（yaml-cpp convert<> 反序列化）→ SanityTestPPF 校验 → CreateRecords 按 Info 树建 Record（含三来源参数）→ 定时器按周期分桶 → 轮询回调：单记录走 DbusAccessor/RedfishClient 单点取值；组轮询走 MRD 一次拉全命名空间键值对再按 ShmemParams.Key 匹配分发（`fdr_grp_update.cpp:40-53` 命中/未命中两分支）→ 值入 Record 缓冲 → 统计+落盘。

## 设计决策

1. **组刷新选 MRD 批量拉取**：同组遥测点往往同一命名空间——一次共享内存读全量、进程内分发，比逐条 D-Bus 往返便宜几个量级；代价是强依赖 nv-bmc-shmem 的部署（FetchMethod 目前只支持 Shmem）。
2. **策略全部模板化在头文件**（convert<> 特化）：无 .cpp、无运行时反射——YAML 字段与结构体成员一一对应，加字段=加结构+加特化两处；0 字节的 fdr_policy.cpp 是历史占位。
3. **四级遥测树（Section/Component/InfoGroup/Info）**：与物理拓扑（机箱→GPU→链路→参数）同构，dump 目录与离线视图都继承这个层级。
4. **平台指纹+前置条件**：一份二进制跑多平台——启动期按指纹规则匹配 PPF，非每平台一构建。
5. **PPF 生成物与手编并存**：automation/generated/ 是生成通道产物，platforms/ 是基线——改平台先判断走哪条通道，手编生成物会被覆盖。

## 新人提示

- 新增遥测参数链路：TelemetryCatalog CSV 加行 → yaml_generator 重新生成 PPF → `fdr_policy.hpp` 不用动（Info 已泛化）→ sanity 查重通过。
- 调 Redfish 取值先看 `tests/fdr_redfish_stub_test.cpp` 的桩注入模式（g_stubHttpResponse 控 HTTP 层），别起真 BMC。
- ShmemParams.Key 的 `$param` 变量替换在 `fdr_record.cpp:57`（FindAndReplaceAll）——PPF 里写 `$NvlinkId` 这类占位符时记住它是运行期展开的。
- MRD 对账用 `tools/data_validation/data_validator.py`（269 行），覆盖豁免清单按平台放 `tools/data_validation/platform/`。
