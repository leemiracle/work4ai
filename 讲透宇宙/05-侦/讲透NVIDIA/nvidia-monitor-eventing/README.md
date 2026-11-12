# 讲透 nvidia-monitor-eventing（BMC 侧 GPU 事件监控与 Redfish 上报）

NVIDIA GPU/NVSwitch 的 BMC 侧监控守护：DAT 设备关联树 + DeviceIdPattern 模式语言 + accessor 三层数据面 + EventDetection 检测引擎 + 健康上卷/selftest + spec2code 配置生产线。C++/OpenBMC（meson + sdbusplus + phosphor-logging）。仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-monitor-eventing`。

## 全链状态表

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki 全量 | 完成（18 页 TRUE_100） | `deepwiki/`（INDEX.md + _coverage-check.md + wiki_full.md） |
| understand 图谱 | 完成：324 节点 / 393 边 / 11 层 / 14 步 tour，validate 0 issues | 仓内 `.understand-anything/knowledge-graph.json` |
| fingerprints 基线 | 237 文件 @ `69f6f8e6`（2026-08-11） | 仓内 `.understand-anything/fingerprints.json` |
| ONBOARDING | 完成（8 节，行号锚 60+，全部 grep 实证） | `onboarding/ONBOARDING.md` |
| explain 系列 | 完成 4 篇（六节结构，行号锚 12+/篇） | `explain/01..04` |
| 本 README | 状态表 + 勘误 8 条 | 本文 |

explain 索引：01-dat-deviceidpattern（世界模型两基元）/ 02-accessor-eventdetection（数据面与检测心脏）/ 03-health-rollup-selftest（健康上卷与自检）/ 04-spec2code-wrappers（配置生产与 wrapper 体系）。

## 阅读顺序建议

新人：README（仓根，仅构建）→ doc/event_detection.md → onboarding/ONBOARDING.md → doc/device_id_user_guide.md；深潜按 explain 01→02→03→04；硬件接入者从 04 篇的生成管线进。

## 勘误清单（源码实证，引用前必读）

1. **"DbusAccessorCore" 不存在**：图谱 L06 描述与 DeepWiki 2.2 使用的类名 DbusAccessorCore 在全仓 grep 为零命中。dbus_accessor.hpp（733 行）的真实主体是 CRTP 模板 `ObjectMapper`（dbus_accessor.hpp:160）及其特化 `DirectObjectMapper`（:515）/`CachingObjectMapper`（:535），配 DbusDelayer 家族（:600-689）。引用数据面中间层请用 ObjectMapper。
2. **dbus_singleton.hpp 不是单例类**：该文件只有一个 extern 指针声明 `crow::connections::systemBus`（借 bmcweb 的命名约定，dbus_singleton.hpp:22-32 的 namespace crow 段）——没有类、没有 get 函数，连接初始化责任在调用方。按"单例模式"找实现会扑空。
3. **"无锁环形队列"只对内核成立**：pc_event.hpp:35 PcQueueType 的成员是 boost::lockfree::spsc_queue，但 push/pop/write_available 全部套 std::scoped_lock（pc_event.hpp:42/:48/:54，write_available 处源码自带 TODO "is this necessary?"）。锁语义上这是有锁队列；且 spsc（单生产者单消费者）语义与 EventDetection 双 worker 线程的用法值得对照审视。
4. **tests_common 的 1788 行在 .cpp 不在 .hpp**：图谱 L11 把 "1788 行 mock 对象映射" 挂在 tests_common_defs.hpp 上，实际 hpp 仅 34 行声明，1788 行在 tests_common_defs.cpp。引用行数注意挂对边。
5. **spec2code 在仓根不在 tools/ 下；vulcan-faults 也不在 spec2code 里**：`tools/spec2code/` 目录不存在，生成器家族在仓根 `spec2code/`（rascat 1156/fpga_alert 571/redfish 校验器 284/gpiomon 192/glacier 46）；vulcan-faults（3436 行 CSV 在内）是 `tools/vulcan-faults/` 独立目录。把两者并置引用时须写全路径。
6. **event_info 与 diagnostics 的"行数"普遍挂 hpp 边**：EventNode 常被引作"772 行"（那是 event_info.hpp），实现侧 event_info.cpp 实为 1038 行（全仓最大实现件）；diagnostics 同病：hpp 772 行 / cpp 936 行。反序列化与匹配逻辑的改动点都在 cpp 侧。
7. **"双线程消费"不完整**：EventDetection 的 workerThreadMainLoop（event_detection.hpp:128）+ workerThreadProcessEvents（:134）是两个常驻 worker，但每个触发事件还会另起 std::thread（:640、:694）做异步处理——并发模型是"双消费者 + 每事件一短线程"，只说双线程会低估。
8. **event_validation.py 与 event_injector 是两件东西**：注入器 event_injector 只有 394 行（调度 modules/ 下的两个注入脚本），端到端验证器 event_validation.py 是独立的 865 行工具；nvidia-xid-event-handler（442 行）又是第三个独立消费者。DeepWiki 5.4 把它们混叙为"注入工具"时注意区分。

## 口径备注

- 行数 wc -l 实证；include/ 与 src/ 的 .hpp/.cpp 总量约 20.7k 行（不含 tools/spec2code/test）。
- "六个 JSON schema 常量"指 src/config_schemas.cpp（180 行）内置常量，配 json_schema.hpp（473 行）轻量校验器。
- wrapper 性能 CSV 的时间戳（2022-10）是历史实测数据留存，非当前基线；mockup 模板文件名内嵌基线 commit adf4a8847。
- test/ 共 18 个 *_test.cpp（googletest），最重三件：device_id_test.cpp 2028 行、event_detection_test.cpp 1621 行、accessor_test.cpp 812 行。
