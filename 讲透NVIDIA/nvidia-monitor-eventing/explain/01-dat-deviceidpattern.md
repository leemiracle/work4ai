# 01 · DAT 设备关联树与 DeviceIdPattern 模式语言

## 角色定位

DAT（Device Association Tree）与 DeviceIdPattern 是本仓的两个"世界模型基元"：前者回答"这台整机里有哪些设备、它们怎么分层关联"（selftest 定位故障设备、健康上卷的骨架），后者回答"一条事件配置如何用一行模式覆盖一组设备"（`GPU[0-3]`、`NVS[0,2-3]`）。检测引擎（02 篇）的一切匹配都以这两个基元的展开结果为坐标。文档锚：doc/dat_traverse.md 与 doc/device_id_user_guide.md（896 行权威语法参考）。

## 内部结构

**DAT 线**（include/dat_traverse.hpp + src/dat_traverse.cpp 780 行）：

- 数据类五件套：Status（dat_traverse.hpp:41）、TestPoint（dat_traverse.hpp:49）、TestLayer（dat_traverse.hpp:56）、DeviceType（dat_traverse.hpp:74）、Device（dat_traverse.hpp:103）——设备节点携带测试层/测试点与状态。
- 设备类型映射 `populateMap`：声明 dat_traverse.hpp:155（两个重载 :155/:157），实现 dat_traverse.cpp:86 与 dat_traverse.cpp:115，从 JSON 构造类型→设备映射。
- 遍历器 `DATTraverse`（dat_traverse.hpp:235，L235-523）：深度优先遍历全树测试点、按路径/类型查找设备——它本身继承 event_handler::EventHandler（可插进处理器框架）。
- 配套 `src/device_util.cpp`/`include/device_util.hpp`：设备区间展开 `expandDeviceRange`（device_util.cpp:45 接收 DeviceIdPattern 对象、device_util.cpp:73 接收字符串模式，声明 device_util.hpp:50-51）与 D-Bus 对象路径推断。

**模式语言线**（include/device_id.hpp 985 行 + src/device_id.cpp 837 行）：

- `PatternIndex`（device_id.hpp:184，构造即 normalize :199/:220）——模式解析后的索引结构；
- `PatternInputDomain`（:225）与 `CartesianProductRange`（:253）——定义输入域与笛卡尔积展开；
- `DeviceIdPattern`（:305，L305-586）——对外主类：解析、迭代展开为具体设备名、规范化与序比较。
- Python 同构实现 `tools/device-id-lang/ids.py`（605 行）：`DeviceIdPattern`（ids.py:197）/`InvDeviceIdPattern`（ids.py:421）双类，range/map/indexed_map 域函数族 + 反向查询，用于跨语言语义对拍；单头复用版 `DeviceIdPattern.hpp` 供工具脚本 include。
- 名称规范维护在 tools/device_id_mapping/（ids-map.csv、ids-map.py、json-gen.py、device-id-norm-gen.sh、device-id-norm-test.sh）。

## 外部连接

上游：examples/dat.json（4153 行蓝本）是配置作者的世界快照，生产管线 tools/DAT-json-exporter（Code.js/Apps Script + spreadsheets-install.sh）从 Google Sheets 生成 DAT JSON，tools/sub-dat.py 抽子树，tools/device_association_editor 编辑关联。下游：EventInstantiator（event_instantiator.hpp:72 instantiateEvent）展开事件模式时要查 DAT；selftest（selftest.hpp:183）按树逐设备执行测试点；device_status_handler.hpp:46-47 的 Health/HealthRollup 沿树上卷；check_accessor.hpp:27 的 AssertedDevice 定位要回查树。json_proc.cpp:28 的 evalJson 在求值时用 PatternIndex（device_id.hpp:184）解析模式值。

## 数据流

装载期：main（eventing_main.cpp:374）→ loadDAT（eventing_main.cpp:109）读 dat.json → populateMap（dat_traverse.cpp:86）建类型映射 → DATTraverse（dat_traverse.hpp:235）可遍历整树。事件实例化期：event_info.json 里的 `device_id` 字段（如 `GPU[0-3]`）→ DeviceIdPattern（device_id.hpp:305）解析为 PatternIndex → PatternInputDomain/CartesianProductRange 展开成具体设备实例列表 → 每个实例与 accessor 绑定成运行时事件集合。自检期：DAT 树驱动 Selftest 遍历，失败测试点由 RootCauseTracer（selftest.hpp:406）回溯根因设备。

## 设计决策

- **模式语言而非枚举**：一行 `GPU[0-3]` 代替四条配置，设备规模（GB200 级整机几十个 GPU/NVSwitch/PCIe 设备）下配置体积与一致性都赢——性能线 performance-test-results/ 的 original/optimized device-id-norm 对照 CSV（2022-10）就是这语言规范化优化的实测证据。
- **双实现对拍**：C++ 运行时实现与 Python 工具实现（ids.py）同构，跨语言一致性由 device-id-lang 测试维护——生成器/验证器（Python 世界）与守护（C++ 世界）必须对同一模式给出同一展开。
- **树而非平表**：设备关联用树表达层级（GPU 挂 NVSwitch 下），健康上卷与根因回溯都是树操作（device_status_handler 的 rollup 缓存、RootCauseTracer）。
- **配置源头外部化**：DAT 从 Google Sheets 生产（DAT-json-exporter），硬件团队维护表格而非手写 4153 行 JSON。

## 新人提示

先读 doc/device_id_user_guide.md 的语法节再碰 device_id.hpp；用 ids.py 交互展开几个模式建立直觉（`GPU[0,2-3]`、索引引用、笛卡尔积）；test/device_id_test.cpp（2028 行）是最全的语义边界教材；改 populateMap 时注意两个重载（dat_traverse.cpp:86/:115）的分工；DAT 编辑走 Sheets 管线而不是手改 examples/dat.json。
