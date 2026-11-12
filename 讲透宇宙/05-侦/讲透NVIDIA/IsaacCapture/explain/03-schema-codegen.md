# 03 数据契约与代码生成（schema / schema_compat / codegen）——schema 即代码

## 一、角色定位

一个遥操作系统的所有组件——C++ tracker、Python 重定向引擎、MCAP 录制、跨进程推流——凭什么对"一只手"有相同理解？答案是 `src/core/schema/`（105 文件）：32 个 FlatBuffers `.fbs` 是全仓**唯一权威的数据契约**，C++ 与 Python 各自生成代码；`golden/` 快照守卫契约演化；`schema_compat/` 判定"旧录制还能不能读"；`codegen/` 再推一步——**从一行 TOML 生成整个 tracker 的 C++ 骨架与 Python 绑定**。`schema/CMakeLists.txt:6-7` 即宣言："FlatBuffer schemas are this module's language-neutral contract"。加一个"flatbuffer 可表达、tensor 可拉取"的新设备只需一个 `.fbs` 加一行 `trackers.toml`——第 2 篇的追踪三轨是消费者，本篇讲生产线。

## 二、内部结构

### 2.1 契约的组织：fbs/ 的 32 个文件

三层结构。**基元层**：可复用 struct——`pose.fbs`（`struct Pose`，pose.fbs:10，position + orientation，米制）、point/quaternion/float4/twist。**时间层**：`timestamp.fbs` 的 `struct DeviceDataTimestamp`（timestamp.fbs:10）三个 int64 三个时钟域——available（运行时收到）、sample_local（跨设备同步公共域）、raw_device（设备自家时钟）。**领域层**：hand/head/controller/tactile 等 20 余个设备 schema。

`hand.fbs` 是惯用法范本：`enum HandJoint : uint8`（hand.fbs:16）26 关节**逐字对齐 OpenXR `XrHandJointEXT` 顺序**，`NUM_JOINTS = 26`（hand.fbs:44）钉死长度；`struct HandJointPose`（hand.fbs:53）= Pose + is_valid + radius，坐标系是共享追踪参考系（session base space 非父节点局部）；`struct HandJoints` 用**固定数组** `poses: [HandJointPose:26]`（hand.fbs:68）——26 关节是 OpenXR 物理事实不是可配置参数；`table HandPose`（hand.fbs:73）仅一个 `joints` 字段。两层分离：`table HandPoseRecord`（hand.fbs:84）包装 `data + timestamp`，`root_type HandPoseRecord`（hand.fbs:89）——**Record 只是 MCAP 录制外壳，tracker 公共查询 API 返回内层数据表**（hand.fbs:81-83）。

### 2.2 C++ 消费：Serialized<T>，反 object-API

`serialized.hpp` 的 `Serialized<T>`（serialized.hpp:54）是三字段小类（L202-204：类型擦除 owner + 表指针 + 可选 buffer span），文件头注释（L4-37）是全仓最值得读的设计文档。核心论点：flatc 的 object-API（`-T`）是 UnPack 后的 vector/string/unique_ptr 树，交给调用者意味着 tracker 要么每读一次拷贝整棵树、要么借出下帧被覆写的存储；`Serialized<T>` 直指编码字节——**无 unpack、无逐字段分配、公共签名零 -T**。衍生性质：**拷贝即引用计数加一**，本帧快照在 tracker 前进后仍有效（L19-23：不可变是契约非强制，Python 侧交出可写 NumPy 视图）；**`narrow()` 视图树**（L139-159）；**两种 `adopt()`**（L101-105 / L114-118）让已编码字节直达 sink 免重编码；`pack<T>()`（L214-220）反向桥；move 构造坑手写填（L76-93，`std::exchange` 双清）。

### 2.3 Python 消费：绑定层与零拷贝 NumPy 视图

`schema/python/`（33 文件）**全是 C++ 源码**——pybind11 绑定编译成 `_schema` 扩展模块（`schema_module.cpp:38` 注册 27 个绑定头）。脚手架 `schema_serialized.h`（L4-17）：Python 每表一类、背后 `Serialized<T>`，读走生成访问器直进缓冲；**构造反向**——先拼 -T 再用生成的 Pack 编码返回视图，编码器永远诚实（布局恒与 C++ 读者一致）。`serialized_class()`（schema_serialized.h:33）与 `field()/vector_field()/narrow_vector()` 模板族覆盖字段形态。

`schema_array_views.h` 是性能关键：FlatBuffers 的 struct 数组是 interleaved（AoS），字段暴露为 **strided NumPy 视图**（L6-10）——NumPy 与 DLPack 原生带 strides，直接满足重定向引擎的 `NDArrayType` 契约，**零拷贝**。这正是第 1 篇 `HandsSource` 把 `joints.positions` 塞进 HandInput 的底层机制。细节：取址优先走生成访问器成员地址（改字段名编译报错，L14-18），标量才回退查偏移；小端假设（L33-36）——视图绕过 `EndianScalar()`，仅在小端主机（x86_64/ARM64）正确。

### 2.4 契约演化守卫：golden/ 与 schema_compat

`golden/` 存每个 schema"上次议定修订"时的编译 `.bfbs`，与 `McapTrackerChannels` 嵌进每份 MCAP 录制的 schema **逐字节相同**（README.md:11-13）。刻意不进 LFS（README.md:15-18）：漏拉 LFS 的克隆会报"unparseable"而非"missing fetch"误导排查。守卫双端同函数：CI 端 `test_schema_conform.cpp`（schema/golden 成对 L50 + stay readable L57）；回放端 `McapTrackerViewers` 构造时校验（tracker_channels.hpp:261/270/403）。判级三态（schema_compat.hpp:13-22）：Identical / Compatible（异但读者要读的字段 id、类型、偏移未变）/ Incompatible（会误读）。规则（L34-46）：struct 加字段、id 复用、标量加宽都 Incompatible；表仅尾部加字段 Compatible。`enforce_schema_compat`（L49）：Incompatible 抛异常，Compatible 记日志（schema_compat.cpp:222）。struct inline 无 vtable，尺寸烙死在嵌套布局里，专门函数 `struct_layout_conflict`（schema_compat.cpp:49）盯 bytesize/minalign。

演化纪律（README）：加字段=尾部追加 optional + 全新 id；**struct 永不改动**；**`root_type` 不改名**（README.md:49，录制带旧名回放按名匹配）；goldens 只在破坏被明确接受后刷新（README.md:58 `schema_golden_update`）。坑：conform 测试读 **build 树** .bfbs，先 build 再 ctest（README.md:26）。旁路契约 `tracker_metadata.hpp`：元数据走伴生 collection `<id>/metadata`（L24-27），上限 68864（L19），周期重推（tactile 走此线）。

### 2.5 codegen：从 TOML 到 tracker 骨架

入口 `generate_trackers.py`，两段式。**manifest.py 解析**：`REQUIRED_KEYS = {name, table}`（manifest.py:15），解析后须齐 14 键（L19-36）；占位符 `%key%`/`%key_CamelCase%`/`%%` 一个正则统一处理（L38-40）；`snake_to_camel` 连数字后首字母大写（L43-61）；默认值三层合并（L100-114）。**渲染**：每 tracker 一套**七文件捆绑**（`_render_tracker_set`，generate_trackers.py:48-71），模板分 pull/push 各 7 个 + 11 个 fragments；产物 L232-266：13 个 `.inc`（forward_decls、dispatch_rows、recording_traits、pybind 块等）+ `_generated_tracker_exports.py`——第 2 篇 `k_tracker_dispatch` 表尾与绑定 generated 块全产自这里；`_write_if_changed`（L24）保 mtime、`_PRUNE_SUFFIXES`（L311）清孤儿。闭环：**fbs 定义数据 → flatc 生成双栈代码 → trackers.toml 一行声明设备 → codegen 生成三轨骨架与绑定 → golden/compat 保证今天的录制明天可读**。

## 三、外部连接

上游：flatc；codegen 只用标准库（tomllib/argparse，manifest.py:8-12）。下游：`mcap/`（录制嵌 golden bfbs、回放调 compat 校验）；追踪三轨（第 2 篇）；Python `isaaccapture.schema` 包与 retargeting_engine 的 `tensor_types`（`HandInput` 26 关节与 `HandJoint::NUM_JOINTS = 26` 互为镜像）。CI：conform 套件 + codegen 自带 `test_manifest.py`/`test_generate_prune.py`。

## 四、数据流

**编译期**：fbs → flatc → C++ 生成头与绑定层。**构建配置期**：CMake 跑 `generate_trackers.py` 读 TOML → 渲染比对落盘 → 编进三个 tracker 库。**运行期写路径**：impl 组装 -T 局部 → `pack<T>()` 编码一次 → `Serialized::adopt` 持有 → 录制时 payload 嵌 Record 字节随 golden bfbs 写进 MCAP。**读路径**：Python 拿 `Serialized<HandPose>` 视图 → `joints.positions` 经 `schema_array_views.h` 变 strided NumPy 数组（零拷贝）→ retargeting_engine TensorGroup 直接收编。**回放路径**：MCAP 内嵌 bfbs 与编译侧 bfbs 交 `check_schema_compat` 三态判级 → Identical/Compatible 放行、Incompatible 构造期拒绝。

## 五、设计决策

- **契约单源、生成多靶**：C++ 与 Python 没有各自维护的数据结构，布局漂移在源头不可能；Python 构造反向走生成的 Pack，"编码器永远诚实"。
- **零拷贝一以贯之**：`Serialized<T>` 反 object-API、strided NumPy 视图满足 DLPack——从设备到重定向算法一帧数据全程不复制。
- **契约演化有法典**：三态判级 + 双端同函数 + golden 快照 + 成文纪律——格式兼容从"祈祷"变"机械检查"。
- **Record/数据两层分离**：录制外壳不污染查询 API。
- **codegen 克制在骨架**：结构同构的拉取/推流 tracker 才生成，真自定义（keyboard 合并、head 的 VALID/TRACKED 语义）仍手写——生成代码承担重复，人承担差异。

## 六、新人提示

1. **改 schema 标准动作**：尾部追加 optional 字段 + 新 id → 跑 conform 测试 → 破坏被接受后才 `schema_golden_update`。永不动 struct、不改 root_type、不复用 id。
2. **跑测试先 build**：conform 测试读 build 树 .bfbs，裸 ctest 拿旧构建骗你绿。
3. **找 Python 侧数据类**：不在 `.py` 里——`schema/python/*.h` 是 pybind 绑定源码；读字段定义永远回 `fbs/`。
4. **NumPy 视图共享可变**：`joints.positions` 指向 tracker 缓冲，要改先 `.copy()`。加新设备走清单路线：.fbs（复用基元）+ TOML 行；struct 数组字段配 `schema_array_views.h` 视图绑定才能零拷贝。

## 源码实证勘误

1. **codegen 文件数**：任务书称 32；实测 30（含 2 个测试 py 与 .clang-format）。
2. **`python/schema_serialized.h` 扇入 23 属实**：grep 实测一致。
3. **`python/` 目录名易误导**：`src/core/schema/python/` 下全是 C++ 头（pybind 绑定）非 Python 源码；Python 生成物只有 codegen 的 `_generated_tracker_exports.py`。
4. **`cpp/inc/schema/` 同层还有 5 个头**：任务书只列 `serialized.hpp`；实际还有 tracker_metadata/tactile_metadata_validation/metadata_validation/full_body_compat/joint_se3_pose_family。
5. **golden 的 LFS 决策是反向的**：其他二进制走 LFS，golden 刻意走普通 git 对象（README.md:15-18）——让漏拉 LFS 的克隆失败得可诊断。

---
`路径约定`：`hand.fbs` 等 = schema/fbs/ 同名；`serialized.hpp` = schema/cpp/inc/schema/；`schema_serialized.h` = schema/python/；`README.md` = schema/README.md；compat 两文件 = schema_compat/cpp/；`tracker_channels.hpp` = mcap/。
`元数据`：chars=6320（不计空格，超 4800 上限 31%——schema 主线密度取舍，锚与勘误全保）；anchors=27；勘误=5。
