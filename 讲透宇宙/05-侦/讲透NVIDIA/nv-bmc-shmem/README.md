# 讲透 NVIDIA/nv-bmc-shmem（BMC 遥测共享内存库）

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki | ✅ 30/30 页 TRUE_100（2026-10-26 抓取） | [deepwiki/](deepwiki) |
| understand 图谱 | ✅ 120 节点 / 149 边 / 6 层 / 8 步导览，0 issues，fingerprints 68 文件 @ `e9193cbc` | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 7 节 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) |
| explain | ✅ 2 篇 | [explain/01-共享内存底座.md](explain/01-共享内存底座.md) ｜ [explain/02-metric翻译与generateURI.md](explain/02-metric翻译与generateURI.md) |

仓库一句话：**NVIDIA BMC 上的 Redfish 遥测共享内存库**（meson 工程名 `nvshmem`）——为治 bmcweb MRD 请求走 D-Bus 的 SLA 超标（PID loop outliers + TAT 越界），让 producer 守护（gpumgrd/hwmontemp）把带 Redfish URI 的 metric 值直接写进 boost::interprocess 共享段，bmcweb 按命名空间零 IPC 读取；1715 行翻译层把裸值→Redfish 语义前置进库，299 个 gtest 用例锁行为。

## 勘误清单（源码实证，2026-11-09 核实）

1. **这是 C++ 项目，不是 C 库**：图谱 L02 摘要把 `shm_common.h` 记作"公共 C 头"并打 `c-api` 标签。实测 meson 工程语言声明为 `'cpp'`（`meson.build:3`）且 `cpp_std=c++23`（`meson.build:7`）；shm_common.h 虽以 .h 为扩展名，内容用 phosphor-lg2 的 `lg2::info`（`shm_common.h:27`）、boost interprocess 的 `char_string_t/void_allocator_t`（`shm_common.h:75-82`）与 `std::string`（`shm_common.h:88-91`），是纯 C++ 头。`.h` 扩展名是跨端契约的表意，不是语言属性。
2. **sensor_map 测试是 20 个用例不是 23**：图谱节点记 sensor_map_test.cpp "23 用例"。实测 `grep -c "^TEST"` 为 **20**（335 行文件）；连带 shmem_map_extra_test 实测 **14**（图谱记 15）。全仓正确计数：16 个 gtest 文件合计 **299 用例**（124+54+20+29+8+9+5+10+14+10+6+2+3+2+3）。
3. **metric_report_utils.hpp 是 19 个 inline 函数，且"平均行数"叙事失真**：图谱记"18 函数 1715 行"。实测 `grep -c '^inline'` 为 **19**；更重要的是质量分布——`generateURI` 一个函数独占 **407 行**（`:1002-1408`），其余 18 个共约 1300 行。读这个文件的正确姿势是"一个大函数 + 一族小翻译函数"，不是均匀的翻译层。
4. **TryReadLock 不是无阻塞 try，是 1 秒绝对超时后抛异常**：名字容易读成 `try_lock` 式非阻塞探测。实测 `managed_shmem.cpp:73-85`：构造 `abs_time = now + 1s` 的 `sharable_lock`，取不到即 `throw LockAcquisitionException()`；锁对象**必须保持在作用域内**（注释明言）。写读同步靠命名 `named_upgradable_mutex`（段名+"lock"，`managed_shmem.cpp:42` 与 `managed_shmem.cpp:67`），读者并行、写者升级独占。
5. **SHM 段尺寸按命名空间各异，非单一全局段**：图谱 L03 摘要"共享内存段名/尺寸"是单数口径。实测 `configurations/shm_mapping.json` 按命名空间分级——PlatformEnvironmentMetrics 131072B（双 producer）、NVSwitchPortMetrics **1024000B**、Processor/ProcessorGPM 262144B；`ConfigReader::getSHMSize`（`config_json_reader.cpp:163`）按命名空间查表。
6. **producer/client 是库不是进程**：图谱 L04 摘要"telemetry_mrd_producer（namespaceInit 建段…）/telemetry_mrd_client（bmcweb 侧读取）"易被读成两个程序。实测 `lib/meson.build:35` 只产 `libnvshmem` static_library 一枚库目标；进程角色由使用方扮演（producer=gpumrgd/hwmontemp 等守护，client=bmcweb），仓内仅有的两个可执行在 `tools/` 且都是诊断器（`nv_shmem_tool.cpp:36`、`aggregation_service_tester.cpp`）。
7. **ErrorLogger 有抑制/限流机制，不只是"落盘+时间戳"**：图谱摘要漏了关键语义。实测 `error_logger.cpp:51` 的窗口刷新注释（"Interval elapsed: refresh timestamp so the next window suppresses"）+ meson 选项 `logSuppressInterval`（重复日志抑制窗口）与 `maxLogEntries`（错误 map 容量上限，超限跳过）——高频错误风暴不会撑爆存储。
8. **C++23 + werror 的编译门槛**：`meson.build:7-9` 声明 `cpp_std=c++23`、`warning_level=3`、`werror=true`。OpenBMC 生态惯用 C++20 假设在此不成立；以子项目吸收本库（`libonly` 选项，`meson_options.txt:1`）的工程需对齐工具链。

## 本目录导航

- 想懂动机与架构三角 → onboarding 第一、二节（README.md:9-22 的 SLA 叙事）；
- 想懂共享内存/锁语义 → explain 01（契约双轨、RAII、TryReadLock 数据流）；
- 想懂 Redfish URI 与翻译层 → explain 02（generateURI 407 行的正确打开方式）；
- 做部署排障 → onboarding 第六节 nv_shmem_tool（段内容/剩余空间/逐传感器 dump）。
