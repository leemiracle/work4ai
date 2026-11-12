# 01 重定向引擎（retargeting_engine）——遥操作数据流的"计算图内核"

## 一、角色定位

IsaacCapture 的链路是"设备输入 → 重定向 → 机器人动作"，`retargeting_engine` 是中间层内核：不关心数据来自哪个硬件、动作发给哪个机器人，只提供**类型化、可组合、可缓存的计算图框架**。三层约 80 文件：`retargeting_engine/`（52 个 .py：interface 抽象核心 / tensor_types 词汇表 / deviceio_source_nodes 设备源节点 / utilities 变换工具）；`retargeters/`（顶层 20 个 .py 加 G1/SO101/joint_space 子包，懒加载于 `retargeters/__init__.py:56`，不强依赖 nlopt/torch）；`retargeting_engine_ui/`（ImGui 调参窗）。扇入 grep 实测：interface 106 / tensor_types 86 / retargeter_core_types 80 文件——遥操作栈公共底座。

## 二、内部结构

### 2.1 双层抽象与四层 API

`retargeter_core_types.py` 定义两个 ABC 与通用语言：`RetargeterIO = Dict[str, OptionalTensorGroup]`（`retargeter_core_types.py:14`）。`BaseExecutable`（L77）是单节点契约（compute 原地填充输出）；`GraphExecutable`（L115）是图级契约——公开侧 `execute_pipeline` 接收叶节点名→输入返回合并输出（一切 runner 的调用口），内部侧 `_compute_with_cache`/`get_leaf_nodes` 支撑 DAG 遍历与缓存。

`BaseRetargeter`（`base_retargeter.py:40`）同时实现两者，四层 API 阶梯（docstring L9-14）：子类只实现抽象的 `_compute_fn`（L125），外部选 `compute`/`__call__`/`execute_pipeline`。组合入口 `connect()`（L181）：本节点输入名映射到上游 `OutputSelector`，三重校验（L223-228）后返回 `RetargeterSubgraph`（`retargeter_subgraph.py:23`），子图也是 GraphExecutable 可无限嵌套；`OutputCombiner`（`output_combiner.py:24`）反向合流。子图 `_compute_with_cache`（`retargeter_subgraph.py:76-112`）：缓存命中即返回，否则递归算上游再算本节点——菱形共享节点只算一次。

### 2.2 类型系统与 Optional 语义

词汇表三层：`scalar_types`/`ndarray_types`（DLPack 风格）/领域类型 `standard_types.py`——`HandInput()`（L29）是 26 关节四张量（positions/orientations/radii/valid），`NUM_HAND_JOINTS = 26` 来自 OpenXR（L19）；`indices.py` 枚举下标免魔法数字。运行期 `Tensor`（`tensor.py:29`）校验，未赋值读到 `UNSET_VALUE` 哨兵（L24）抛错；环境变量可关校验（L34-36）。

**Optional 是最有工程味的设计**：`OptionalType()` 工厂（`tensor_group_type.py:138`）声明"运行时可能缺席"，生产者 `set_none()`、消费者查 `.is_none`；兼容规则（L58）唯一禁区是**Optional 输出不能接 Required 输入**（L77-81，connect 时抛错）——追踪丢失须无损穿过流水线而非崩掉整帧。

### 2.3 deviceio 源节点与可调参

`IDeviceIOSource`（`deviceio_source_nodes/interface.py:21`）继承 BaseRetargeter 加两个抽象方法：`get_tracker()`（L66，暴露 tracker 供会话发现）与 `poll_tracker()`（L76，每帧打包原生数据）。样本 `HandsSource`（`hands_source.py:28`）：构造即建 tracker（L63），input_spec 两个 `DeviceIOHandPoseTracked()` 槽（L100-101，装 flatbuffer 原生对象而非 ndarray），output_spec `OptionalType(HandInput())`（L107-108）；`_update_hand_data`（L128-141）极薄——strided view 按 `HandInputIndex` 赋值，未追踪 `set_none()`。全包 23 文件覆盖 head/hands/controllers/gamepad/keyboard/spacemouse/pedals/joint_state/full_body/soma/tactile/message_channel 十二类源与两个反向 sink。参数侧：`ParameterState.sync_all()`（`parameter_state.py:134`）在每次 `_compute_fn` 前刷最新值到成员变量（`base_retargeter.py:417-421`），UI 线程写/计算线程读不撕裂；消费者样本 `Se3AbsRetargeter`（`se3_retargeter.py:72`）。

### 2.4 末端跳变守卫

`EePoseJumpGuard`（`ee_pose_jump_guard.py:134`）是安全语义范本：五态状态机（L36-43）+ 八种逐帧裁决（L46-56）。阈值**节拍感知**：`max(distance_floor, velocity * effective_dt)`（L267-270），dt 取相邻帧实际间隔并夹窗——采样率跌到 20Hz 阈值自动放大，不把丢帧误判成跳变。帧步超阈值即 HOLDING、输出冻结在上个被接受位姿；恢复需**连续 3 样本**回到 0.08m 内（配置 L87-88，判定 L392-397）。`ExecutionState` 非 RUNNING 时 disarm 直通（L275-296）；另输出 14 元素 status 张量（L185-204）外发遥测，安全机制自带黑匣子。同族 `EePoseRateLimiter`（`rate_limiter.py:352`）做速度上界，语义不同、可串联。

## 三、外部连接

上游只依赖 numpy/scipy（`se3_retargeter.py:38`）与标准库，重型依赖被懒加载挡在 pip extra 后；与 C++ 唯一接触点是 flatbuffer 对象（`hands_source.py:25`）。下游最大消费者 `teleop_session_manager`：`teleop_session.py:643-651` 每帧构造**共享** `ExecutionCache`，先跑主 pipeline 再跑全部 sink 子图——共享节点每帧只推进一次（推进两次=滤波器时间常数减半）；sink 统一 `flush_to_device` 且契约 non-throwing，设备抖动不撕裂主循环。

## 四、数据流

一帧双手遥操作：① 调每个源的 `poll_tracker(session)`（`hands_source.py:74-95`）拿 tracked 对象；② 连同共享 `ComputeContext`（`GraphTime` 双时钟 + `ExecutionEvents`，`retargeter_core_types.py:18-41`）进 `ExecutionCache`；③ 子图递归求值；④ 源节点把 flatbuffer strided-view 成 `HandInput`（或 set_none）；⑤ Se3/Dex 等 retargeter 产出 7D 位姿，jump guard/rate limiter 串联在后；⑥ `OutputCombiner` 汇总下发，sink 子图写回硬件。时序契约：`execution_events.reset` 清状态（`ee_pose_jump_guard.py:257`）；`_compute_fn` 禁读 outputs 跨步状态（`base_retargeter.py:143-147`），状态存实例变量。

## 五、设计决策

- **类型即契约、连接即编译**：connect 时做完所有校验，运行期零图校验开销——接线错误从运行时崩溃提前到构建时异常。
- **Optional 贯通而非 sentinel 值**：追踪丢失用类型系统表达，消灭"NaN 沿流水线污染下游滤波器"整类事故。
- **per-step 缓存以 `id()` 为键**（`retargeter_core_types.py:44`）：主图与 sink 图缝成一张逻辑图执行，有状态节点单次推进是正确性保障而非优化。
- **源节点自治 tracker + vendor 随源走**（`deviceio_source_nodes/interface.py:43-55`）：会话无需平行注册表，管线自省直接从图上读；**jump guard 把裁决作为正式输出张量**——安全事件可录制回放、可审计。

## 六、新人提示

1. 写新 retargeter：继承 `BaseRetargeter` 实现 `input_spec/output_spec/_compute_fn`，类型复用词汇表，跨步状态放 `self._xxx`。
2. 接新设备：写 `IDeviceIOSource` 子类，input 用对应 `DeviceIO*Tracked` 原始类型，转 ndarray 留在 `_compute_fn`。
3. 调试分层：先 `__call__` 单节点，再 `connect` 成图 `execute_pipeline`，最后接 TeleopSession。
4. 写安全节点前先读 `ee_pose_jump_guard.py`——状态机/节拍阈值/恢复窗口/disarm/状态遥测一个文件全示范。

## 源码实证勘误

1. **扇入口径**：任务书称 `tensor_types/__init__.py` 扇入 92 最高；实测 interface 106 / tensor_types 86——interface 才最高（图谱可能只统计 src/）。
2. **陈旧 schema 路径**：`standard_types.py:7` 引用 "IsaacTeleop/src/core/schema/fbs/"——本仓实际在 `src/core/schema/fbs/`，旧仓残留。
3. **`HandsSource.poll_tracker` 子串分发**：`hands_source.py:90-93` 以 `"left"/"right" in input_name` 匹配左右手——命名约定的隐式契约。
4. **retargeters 文件数**：任务书称 27；实测顶层 20 个 .py + 三个机型子包。
5. **jump guard 与 rate limiter 是两套安全件**：不连续拒绝与速度上界语义不同，勿混。

---
`路径约定`：行号锚相对 `src/python/isaaccapture/`（`base_retargeter.py:40` 即 `retargeting_engine/interface/base_retargeter.py` 第 40 行）；`teleop_session.py` 指 `teleop_session_manager/teleop_session.py`。
`元数据`：chars=4945（不计空格）；anchors=26（file:line）；勘误=5。
