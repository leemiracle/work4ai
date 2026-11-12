# SOMA Retargeter 新人导航（Onboarding）

> 仓库：NVIDIA/soma-retargeter @ cbdb2b49 ｜ 版本 0.2.1（soma_retargeter/_version.py:4）｜ Python ≥3.12（pyproject.toml:10）
> 知识图谱：766 节点 / 866 边 / 10 层 / 11 步导览，fingerprints 548 文件基线
> 定位一句话：把 SOMA 骨架的 BVH 人体动作，用 Warp/Newton IK 重定向成人形机器人的关节动画 CSV（README.md:7）。

## 1. 项目定位与解决的问题

人体动捕与机器人骨骼之间存在两道鸿沟：**比例不同**（腿长臂长、根高度）与**关节结构不同**（自由度数量与命名各异）。SOMA Retargeter 的解法是一条五步流水线（README.md:15-22）：解析 BVH → 检测足部接触 → 把人体关节缩放映射到机器人比例 → IK 求解机器人关节角 → 写出根位姿+驱动关节 CSV。

三条边界要先认清：

- **只吃 SOMA 骨架**。任意 DCC 导出的 BVH 骨架命名不同，会加载错误或直接失败（README.md:62）。源角色资产是捆绑的 `soma_base_skel_minimal.usd` + 零姿势 `soma_zero_frame0.bvh`（soma_retargeter/assets/soma/）。
- **输出是运动学结果，不是动力学**。README 的 beta 警示明说：生成的动作是 kinematic 的，上真机前必须先在仿真里验证安全性、可行性与控制器兼容性（README.md:11）。
- **生态位**：它是 SOMA 生态（GEM-X 视频动捕、Kimodo 运动扩散、ProtoMotions 仿真训练、SONIC 全身控制）里"把人体动作搬上机器人"的那一环（README.md:96-102）。

## 2. 总体架构与分层

图谱 10 层，按依赖方向自底向上：

| 层 | 内容 | 代表锚点 |
|---|---|---|
| L01 工程配置 | Apache-2.0、LFS 规则 | .gitattributes:6（STL 入 LFS）、pyproject.toml:35（dynamic version） |
| L02 文档/许可 | 11 篇操作文档 + 16 份第三方许可 | documentation/robot-configuration-reference.md |
| L03 数学工具 | 姿态传播、布尔游程、四元数 twist | utils/pose_utils.py:39、utils/math_utils.py:8 |
| L04 骨架动画 | Skeleton/AnimationBuffer/接触检测 | animation/skeleton.py:10、animation/contact_detection.py:249 |
| L05 动作 IO | BVH 解析、CSV 读写、USD 进出口 | io/bvh.py:175、io/csv.py:48、io/usd.py:382 |
| L06 机器人建模 | 注册表、人体→机器人缩放 | robotics/robot_registry.py:19、robotics/human_to_robot_scaler.py:13 |
| L07 IK 重定向管线 | 编排核心（深讲见 §3） | pipelines/soma_retargeting_pipeline.py:55 |
| L08 渲染器 | 蒙皮/骨架/坐标轴三件套 | renderers/mesh_renderer.py:46 |
| L09 GUI 与调优 | 转换器、配置器、权重优化器 | app/bvh_to_csv_converter.py:36、app/tools/ik_weight_optimizer.py |
| L10 资产库 | 5 机器人 + 362 STL + 动作库 | soma_retargeter/assets/robotics/（386 文件） |

**Warp 与 Newton 是两个不同的东西**，新人最易混：Warp（warp-lang>=1.14.0，pyproject.toml:13）是 NVIDIA 的 Python→GPU kernel 框架，全库的数学热点（欧拉角转四元数 io/bvh.py:50、姿态批量传播 utils/pose_utils.py:81、足部地标投影 animation/contact_phase.py:140、LBS 蒙皮 renderers/mesh_renderer.py:12）都是 `@wp.kernel`；Newton（newton==1.3.0，pyproject.toml:12）是物理/IK 引擎，提供 ModelBuilder、IK 求解器与查看器（soma_retargeter/pipelines/utils.py:138 的 `create_robot_builder`）。

## 3. 核心子系统深讲

### 3.1 重定向主管线（608 行）

`soma_retargeting_pipeline.py` 是聚合 17 个模块的门面。`SomaRetargetingPipeline`（:55）构造时装配缩放器、IK 求解器、肢体稳定器、限位钳制器；`execute()`（:392）跑通全流程：

1. 接触处理按需补建 plant blenders（:425）；
2. `_build_model` 建 Newton 模型（:427），`_create_ik_objectives` 产出位置/旋转/限位/平滑四组目标（:433-439）；
3. 初始化+稳定化帧数决定输出裁剪量 `num_frames_to_remove`（:447，默认 10+5，:52-53）；
4. `BaseIKSolver`（:449）持有共享 `joint_q` 缓冲（:457），帧循环里 `BasePass`（:461）做基础 IK、`PostProcessPass`（:476）做肢体稳定+触地修正；
5. `trange` 主循环（:499）逐帧执行所有 pass 并 `wp.copy` 录帧（:508），最后 `JointLimitClamper.apply` 钳限位（:511），按环境返回 `CSVAnimationBuffer`（:513-514）。

### 3.2 IK 栈四件套

- **ik_solver.py**：`IKSolver`（:38）负责目标构建（位置 :88 / 旋转 :114 / 平滑滤波 :140）与 `solve()`（:188）；`BaseIKSolver`（:214）另存基础权重供后处理 pass 恢复。
- **ik_pass.py**：每个 pass 自持 **CUDA graph**——GPU 求解被捕获一次，之后逐帧只重放（类文档 :24-25）；`BasePass.execute`（:99）设帧目标并触发捕获，`PostProcessPass`（:119）叠加后处理求解。
- **ik_objectives.py**：`IKSmoothJointFilter`（:92）是自研 Newton IKObjective，把"关节角向限位中点收缩"的残差注入求解（compute_residuals :216），同时提供自动微分（:237）与解析雅可比（:257）两条路。
- **limb_stabilizer.py**：主 IK 之后追加双骨 IK 修正（solve :123），核心调用是 animation/ik.py:20 的 `wp_solve_two_bone_ik`（limb_stabilizer.py:207）。

### 3.3 触地（plant）修正：脚不滑的两级流水

接触检测（animation/contact_detection.py:249 `detect_contacts_velocity_jerk`）用速度+加加速度阈值状态机判触地帧，阈值集中在 `BaselineAThresholds`（:95，velocity_contact=0.1 m/s、jerk_contact=-0.05 m/s³、transition_frames=4）。随后：

- **plant_subsegment_detector.py**：在接触段内用足部地标（脚跟/脚尖/足底法线，animation/contact_phase.py:61）投影（:210）+ 速度稳定帧（:119）细分为 plant 子段，输出锚定目标；
- **plant_correction_blender.py**：`PlantCorrectionBlender`（:205）把脚部变换锚定到段平均姿态（`_quat_average` :72），用 smootherstep 衰减窗（:92）+ 批量 slerp（:98）向前向后扩散，且可压平旋转但保留航向（`_flatten_rotation_preserve_heading` :385，twist 提取 :150）。

### 3.4 IK 权重自动优化器（3004 行，实验特性）

app/tools/ik_weight_optimizer.py 是"用优化器调参"的坐标下降工具：`run_optimizer`（:2549）装载 BVH 语料 → 建误差模型 → 外层循环（:2776）提出权重更新、线搜索+ClipGuard 探测（probe :1518）、接受或保持。约束与守卫：对称肢体权重绑定（`SymmetryPair` :200、`_apply_symmetry_constraints` :343）、防退化剪裁守卫（`ClipGuardConfig` :779、`_ClipGuardPolicy` :1467）。产物是只改 `ik_match_table` 里 t_weight/r_weight 的可部署配置（`_build_retargeter_config` :1675）。

### 3.5 机器人资产与配置

五家捆绑机器人经 manifest 发现（robot_registry.py:93 递归扫 manifest.json）：unitree_g1 / unitree_h2 / booster_t1 / agibot_x2ultra / **agibot-a3t3**（注意连字符，README.md:74-80）。每个机器人目录 = manifest + URDF（g1 为 MJCF）+ STL 网格 + 三份配置：retargeter 配置（ik_match_table 按 Hips/Chest/四肢给源-目标关节配对与权重）、scaler 配置（human_scale_ratio 0.785 等）、post-processing 配置。

## 4. 关键数据流

```
BVH 文件 ──io/bvh.py:175 BVHJoint 层级树──> Animation(io/bvh.py:146)
  ──欧拉角→四元数（Warp kernel，io/bvh.py:50）──> AnimationBuffer(animation/animation_buffer.py:11)
  ──HumanToRobotScaler.compute_effectors_from_buffer（human_to_robot_scaler.py:129，
     按末端执行器映射缩放，Warp kernel :89）──> 机器人比例的 effector 目标
  ──SomaRetargetingPipeline.execute（接触检测→子段→修正混合→IK 两 pass）
  ──JointLimitClamper──> CSVAnimationBuffer ──io/csv.py:48 save_csv──> CSV
```

CSV 格式两条铁律（io/csv.py:11 表头）：首列 Frame，随后 root_translateX/Y/Z（**厘米**，:71 乘 100.0）+ root_rotateX/Y/Z（欧拉**度**，:73）+ 各驱动关节角（度，:76）；load_csv 反向 ×0.01（:35）。朝向约定由 `SpaceConverter`（utils/space_conversion_utils.py:54）处理 Maya/Mujoco 两种 Facing（:9 枚举）。

## 5. 构建 / 运行 / 入口

- **安装**：文档约定用 `uv`（README.md:88-89）：`git lfs pull` 先拉实体网格（installation.md:94-97，否则 362 个 STL 全是 ~134B 的 LFS 指针），再 `uv run python app/bvh_to_csv_converter.py --config assets/default_bvh_to_csv_converter_config.json --viewer gl`。
- **交互入口**：app/bvh_to_csv_converter.py:36 `Viewer`——加载 BVH/CSV、机器人 FK 播放、渲染（render :286）、单动作重定向（retarget_motion :319）。
- **无头批量**：main() 默认 viewer 即 "null"（:607），ViewerNull 分支直接走 `batched_retargeting()`（:513，按 batch_size=100 切批，:536）。默认配置 `retarget_target: unitree_g1`、facing `Mujoco`（assets/default_bvh_to_csv_converter_config.json）。
- **新机器人注册**：app/tools/robot_config_generator.py:125 `Viewer`（1764 行）交互式生成 manifest+三配置并复制网格入包。
- **包裁剪**：pip 包只含 soma_retargeter 包与包内资产（pyproject.toml:28-32），GUI 与示例动作不随 wheel 分发。

## 6. 设计决策与权衡

1. **Warp kernel 双路径**：几乎所有数学热点都备 NumPy 兜底（姿态传播 pose_utils.py:12/39、BVH 欧拉转换 io/bvh.py:50/113），CPU 也能跑、GPU 才快。
2. **CUDA graph 捕获逐帧 IK**：ik_pass.py 把目标设定（CPU）与 GPU 求解重放分离，24 次默认迭代（soma_retargeting_pipeline.py:47）下省掉重复 launch。
3. **初始化/稳定化帧牺牲**：输出掐头 15 帧（:52-53 与配置 num_initialization_frames=10/num_stabilization_frames=5）换求解收敛稳定——批量评估指标时别忘了这个口径差。
4. **配置驱动的一切**：换机器人=换 manifest+三 JSON；平滑滤波权重代码默认 5.5（:49）而 g1 配置给 40.0——调参前先看配置覆盖了什么。
5. **优化器只动权重**：模型结构、scaler 偏移、关节限位、后处理全不动（ik-weight-optimizer.md 的"What changes"节），失败可完全回退。

## 7. 已核实勘误（详见 README.md 勘误节）

① 五家 manifest 并不同构——g1 是唯一用 `targets` 数组包裹、唯一 MJCF 的（soma_retargeter/assets/robotics/unitree/g1/manifest.json:3 与 :6）；② ik-weight-optimizer.md:22-25 称默认配置 input_folder 为空串不能直接跑，实际已填相对路径；③ 两份出厂配置的 extra_robot_paths 都指向不存在的 `assets/robotics` 目录（相对解析后静默空扫，robot_registry.py:132 不校验存在性）；④ pip 安装拿不到 GUI 与捆绑动作（pyproject.toml:29 exclude）；⑤ 图谱阶段曾把 io/csv.py:6 的 stdlib `import csv` 误连为自引用假边，已剔除。

## 8. 新人上手路线（半天到一天）

1. **跑通捆绑例子**（30min）：按 documentation/first-retarget.md，用 `assets/motions/bvh/Neutral_walk_forward_002__A057.bvh`（README.md:64 推荐）转 unitree_g1，对照捆绑参考 CSV（assets/motions/csv/unitree_g1/，10 条）。
2. **读三个文件**（2h）：io/bvh.py（源入口）→ animation/skeleton.py:10/:149（全库骨骼抽象）→ pipelines/soma_retargeting_pipeline.py:392（流程总装）。配 documentation/code-overview.md 当地图。
3. **玩交互查看器**（1h）：GUI 里换机器人、播 FK、重定向一条动作，理解 SpaceConverter 朝向（Mujoco vs Maya）肉眼差异。
4. **调参入门**（1h）：documentation/foot-contact.md + contact_detection.py:95 阈值表，故意把 velocity_contact 调离谱看滑步回潮。
5. **进阶**：换新机器人走 robot-configurator.md（以公开无手 Unitree H1 为教学例）；动作质量问题再上 IK 权重优化器（ik-weight-optimizer.md，语料在 assets/motions/optimizer/ 的 15 条 BVH）。

📌 下一步：explain/ 三篇精讲——主管线、优化器、USD IO。
