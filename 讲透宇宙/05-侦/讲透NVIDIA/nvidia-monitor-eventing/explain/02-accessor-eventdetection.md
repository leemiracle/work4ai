# 02 · accessor 三层数据访问与 EventDetection 检测引擎

## 角色定位

accessor 三层是守护的"数据面"——把 BMC 上四类数据源（D-Bus 属性、命令行工具、文件、正则）统一成一个可声明的抽象；EventDetection 是"控制面心脏"——订阅 D-Bus 信号，按事件配置匹配条件，触发恢复与上报。数据面回答"值是多少"，控制面回答"这是不是事件"。文档锚：doc/data_accessor.md、doc/event_detection.md。

## 内部结构

**数据面三层**：

- 声明层 `DataAccessor`（include/data_accessor.hpp:83，文件 783 行）：统一描述来源与读取方式，`operator==`（:154）支持配置去重，`getDataValue`（:627）返回真实值；实现 src/data_accessor.cpp 378 行。
- D-Bus 中间层 `include/dbus_accessor.hpp`（733 行）：CRTP 模板 `ObjectMapper`（:160）为核心，两种解析策略 `DirectObjectMapper`（:515，每次直查）与 `CachingObjectMapper`（:535，缓存对象映射）；限流测试注入件 `DbusDelayer`（:600）/`DbusDelayerConstLowerBound`（:641）/`DbusDelayerStateGuard`（:675）/`DelayedMethod`（:689）。注意：图谱与文档常写的 "DbusAccessorCore" 在源码中不存在（见 README 勘误 1）。连接获取走 `dbus_singleton.hpp`——它不是类，只是 `crow::connections::systemBus` 的 extern 指针声明（借 bmcweb 约定，初始化责任在 main）。
- 判定层 `CheckAccessor`（include/check_accessor.hpp:51）：对取回值执行等于/范围/位图/查表判定，`AssertedDevice`（:27）与 `AssertedDeviceList`（:42）记录哪些设备满足条件，`hasAssertedDevices`（:104）/`getAssertedDevices`（:153）查询，`buildSingleAssertedDeviceName`（:194）构造单设备断言；实现 check_accessor.cpp 345 行。值语义在 property_accessor.hpp：`PropertyValueDataHelper`（:80）、`PropertyValue`（:301，string/integer/double 变体；bitmap 与 bitmask 语义差异见 :294 注释）、`PropertyString`（:515）。

**控制面 EventDetection**（include/event_detection.hpp 770 行 + src/event_detection.cpp 546 行）：

- 类声明 event_detection.hpp:109；双 worker 线程函数 `workerThreadMainLoop`（:128）与 `workerThreadProcessEvents`（:134），实现 event_detection.cpp:68/:59（:76 留有 "thread2: exiting" 诊断日志）。
- 匹配判定 `IsEvent`（event_detection.hpp:574，调用点 event_detection.cpp:443）。
- 恢复与对账：`recoverFromPowerCycleEvents`（:260）开机后对账掉电前事件，`resolveDeviceLogs`（:282）解析已恢复设备的日志。
- 每个触发事件另起处理线程（:640 与 :694 的 std::make_unique<std::thread>），长操作不阻塞主循环。
- 辅助件：`pc_event.hpp:35` PcQueueType（PcDataType :27 携带 accessor+事件指针；核心 boost::lockfree::spsc_queue，但 push/pop/write_available 全部加 std::scoped_lock——"无锁"只在库内核意义上成立）；`standalone_qualifier.hpp:43` standaloneQualifierPassed（实现 standalone_qualifier.cpp:26）决定 standalone 模式抑制哪些事件——正是基线 commit 69f6f8e 的主题；事件处理器框架 event_handler.hpp（EventHandler 基类 + EventHandlerManager）。

## 外部连接

上游消费 DAT/DeviceIdPattern（01 篇）展开的设备实例与 EventInstantiator（event_instantiator.hpp:33）产出的运行时事件集合；匹配用 json_proc.cpp:28 的 evalJson（JsonPattern 定义 json_proc.hpp:48）求值条件表达式；配置装载前经 config_schemas.cpp（180 行，六个 schema 常量）+ json_schema.hpp（473 行校验器）体检。下游把匹配结果交给 MessageDispatcher/MessageComposer（03 篇）出 Redfish 日志；CheckAccessor 的 AssertedDevice 喂给健康上卷；掉电前队列 pc_event 与 phosphor-logging 持久化日志配合做开机对账。

## 数据流

运行时主链：D-Bus PropertiesChanged/日志信号 → EventDetection 双线程消费（event_detection.cpp:68 主循环 → :59 事件处理）→ 取候选事件的 accessor → DataAccessor（data_accessor.hpp:627 getDataValue）读值（D-Bus 经 ObjectMapper :160 解析服务/对象；CMDLINE 来源经 wrapper 脚本执行）→ CheckAccessor（check_accessor.hpp:51）按配置判定 → 命中则 IsEvent（:574）为真 → 起处理线程（:640）→ MessageComposer 组日志 → 更新 AssertedDevice 状态。掉电场景：断电前 PcQueueType（pc_event.hpp:35）暂存事件 → 复电后 recoverFromPowerCycleEvents（:260）从持久日志与队列比对恢复 → resolveDeviceLogs（:282）清理已解决项。

## 设计决策

- **声明式数据源**：事件配置写"数据从哪来、怎么判"，引擎统一执行——新增一类故障只需加配置不需改代码。
- **CRTP 双策略 ObjectMapper**：直查（简单部署）与缓存（高频读）编译期二选一，零虚函数开销。
- **延迟可注入**：DbusDelayer 家族（dbus_accessor.hpp:600-689）让限流/重试行为可在测试里精确复现。
- **匹配与处理分离**：匹配在线程池循环内，处理另起线程（:640）——慢的 Redfish 上报不拖垮信号消费。
- **开机对账是一等公民**：BMC 世界掉电重启是常态，pc_event+恢复路径（:260/:282）保证跨重启的事件状态一致。

## 新人提示

读序 doc/data_accessor.md → doc/event_detection.md → event_detection.cpp:59-76 感受双线程分工；用 test/accessor_test.cpp（812 行）与 event_detection_test.cpp（1621 行）对照学断言语义；查 "DbusAccessorCore" 会查空——正确的类名入口是 ObjectMapper（dbus_accessor.hpp:160）；跑 daemon 前先让 diagnostics（04 篇）过一遍配置。
