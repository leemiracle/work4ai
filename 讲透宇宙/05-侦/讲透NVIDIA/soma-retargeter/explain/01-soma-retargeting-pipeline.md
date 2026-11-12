# 01 · 重定向主管线 soma_retargeting_pipeline.py（608 行）

## 角色定位

`soma_retargeter/pipelines/soma_retargeting_pipeline.py` 是整个库的门面与总装配车间：上游接 BVH/缩放器产出的 effector 目标，下游产出每个输入动作一个 `CSVAnimationBuffer`。图谱 866 条边中它一个文件就聚合了 17 个模块的 import（:12-44 从 io/newton_utils/pose_utils/robot_registry 到接触与修正全家桶）。

## 内部结构

`SomaRetargetingPipeline`（:55）单一类承担全部编排。`__init__`（:65）装配 HumanToRobotScaler、IKSolver/BaseIKSolver、LimbStabilizer（:29 import）、JointLimitClamper、PlantCorrectionBlender 族；类级默认超参集中在 :47-53（IK 迭代 24、限位权重 10.0、平滑滤波权重 5.5、初始化帧 10、稳定帧 5）。`execute()`（:392）是唯一总入口：空输入早退（:403）→ 权重下限钳制（:408-410）→ 按需补建 plant blenders（:424-425）→ `_build_model`（:427）建 Newton 模型 → `_create_ik_objectives`（:433-439）产出位置/旋转/限位/平滑四组目标 → 装配双 pass（:461 BasePass、:476 PostProcessPass）→ `trange` 帧循环（:499）。

## 外部连接

- 上游：`add_input_motions`（:359）收 AnimationBuffer 列表+根偏移+缩放开关；缩放后的目标映射由 `_build_target_mapping`（:534）按 retarget 配置的 ik_match_table 建立。
- Newton：`_build_model`（:516 起实现）走 soma_retargeter/pipelines/utils.py:138 的 `create_robot_builder`——g1 走 `builder.add_mjcf`（:143），其余机器人 `builder.add_urdf`（:148/:153）并做地面偏移校正（:154 调 newton_utils.py:129）。
- 下游：每环境一个 `CSVAnimationBuffer.create_from_raw_data`（:513-514），IO 层 save_csv 落盘。

## 数据流

逐帧视角：所有 pass 共享同一个 `joint_q` 缓冲（:457 `wp.clone(base_ik_solver.joint_q)` 注释明说）。每帧先 BasePass 设帧目标并执行 CUDA graph 捕获的基础求解，再 PostProcessPass 追加肢体稳定与触地修正；帧号 ≥ num_frames_to_remove（:447，初始化 10+稳定 5）才开始 `wp.copy` 录帧（:508）。循环外 `JointLimitClamper.apply`（:511）统一钳限位后返回（:513）。接触检测可显式预跑：`detect_contacts`（:305）/`set_contact_data`（:241），`_detect_contacts_and_plants`（:252）串起检测+子段+blender 构建，`_build_plant_blenders`（:332）落实例化。

## 设计决策

1. **共享 joint_q**：双 pass 写同一缓冲而非各自拷贝，省显存也保证后处理读到最新解；代价是 pass 顺序成为隐式契约。
2. **掐头 15 帧**：初始化+稳定帧从输出剥离（:447），收敛瞬态不外泄——评估指标必须记住这个口径。
3. **接触/后处理皆可关**：`_needs_contact_processing`（:233）与配置开关决定 pass 列表长度，优化器评估时就整体关闭（retargeter_overrides）。
4. **打印即文档**：execute 开头把全部生效设置打到 stdout（:412-422），复现实验时直接抄日志。

## 新人提示

读这个文件先看 `execute()` 再回头看 `__init__`；调试时 `_DEFAULT_*` 常量（:47-53）与 g1 配置（smooth_joint_filter_weight=40.0）的差异是第一坑——代码默认值只是没有配置时的兜底。改管线顺序时盯住 :457 的共享缓冲语义。
