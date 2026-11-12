# 03 · 传感器 SE3 与 lietorch 垫片：几何层的工程决策样本

## 角色定位

`instant_nurec/utils/sensors/` + `instant_nurec/utils/se3.py` + `merge_covariances.py`/`cubemap.py` 构成几何基元层：相机投影内核、相机模型 dataclass、李群运算与协方差合并。图谱 fanOut 之王 ray_gen.py（36 个消费方）在这层——cubemap、渲染器、数据集全吃它的投影。而 se3.py 是全仓最有代表性的**工程决策样本**：一份"为什么要自己写数学库"的注释钉版。

## 内部结构

**投影内核 ray_gen.py（660 行，纯 torch）**：反投影主链 `_ftheta_image_points_to_camera_rays`:75（F-Theta 多项式正/逆求值走 Horner 与 Newton 迭代 :45/:56）与 `_opencv_pinhole_image_points_to_camera_rays`:156（畸变计算 :119），`_image_points_relative_frame_times`:205 承接卷帘快门（同一帧不同行外参与时间相关，按行插值位姿），`_numerically_stable_xy_norm`:229 是数值稳定小工具；NCore 参数到投影的归一在 `_ncore_ftheta_to_projection_and_resolution`:247 与 `_ncore_opencv_pinhole_to_projection_and_resolution`:316，格式探测 `_looks_like_ncore_opencv_pinhole_parameters`:344。正投影 `camera_rays_to_image_points` 供 cubemap 消费。

**相机模型 kernel_types.py**：相机模型 dataclass 家族——`ShutterType`:32/`FThetaPolynomialType`:42 枚举 + `CameraProjection`:57/`ExternalDistortion`:62（挡风玻璃畸变）等，fanOut=24，是 ray_gen 与配置层（config_schema/dataset.py）之间的类型契约；NCore 相机转换器与 `RectSubsampledSensor` 也在 sensors/ 内。

**SE3/SO3 垫片 se3.py（271 行）**：lietorch API 子集的纯 torch 实现。头注释（se3.py:15-22）把动机写得明明白白：PyPI `lietorch==0.8.2` 硬钉 `torch==2.6.*`/`torchvision==0.21.*`，本仓 pin `torch==2.7.0+cu128`（pyproject.toml:24）——装 lietorch 就得降级 torch、毁掉 cu128 wheel 选择，于是只重实现 predict 路径实际用到的子集：`SE3(data)`/`SE3.InitFromVec`（(...,7) [tx,ty,tz,qx,qy,qz,qw]）、`.data/.vec()/.shape/.dtype/.device/__getitem__`、指数对数/求逆/向量接口与 xyzw 四元数 slerp/旋转矩阵工具。轨迹骨架在 utils/trajectory.py（`transform_rig_trajectories`:28、`merge_rig_trajectories`:53）与 utils/types.py（图谱 fanIn 之王，28 入边）。

**协方差合并 merge_covariances.py（143 行）**：KL 最优的高斯协方差合并，注释钉版 cusolver 的 batched eigh 在 ~18M 个 3x3 矩阵时报 `CUSOLVER_STATUS_INVALID_VALUE`（:28-29），`_chunked_eigh`:34 按 `_EIGH_MAX_BATCH` 分块规避（:39-40），特征分解处再注释一次（:126）。

## 外部连接

- 消费方：ray_gen 被 cubemap.py（fanOut=19，`build_observed_sky_cubemap_with_mask`:206）、训练渲染器 renderer.py:55-76、数据集相机处理消费；se3.py fanOut=15，服务于轨迹插值（trajectory.py:28/:53）与动态层运动——utils/motion.py 的 `associate_points_with_cuboid_tracks`:99/`warp_points_with_cuboid_tracks`:210/`TimeRemapping`:31，其对 CuboidTracks 用 TYPE_CHECKING-only 导入防循环依赖。
- 测试防线：ray_gen 分支与挡风玻璃畸变 551 行测试 + SE3 往返（单位测试）锁死数值行为。

## 数据流

相机参数（kernel_types dataclass）→ ray_gen 反投影出 per-pixel 世界射线（F-Theta 多项式/pinhole 内参 + 畸变 + 卷帘快门位姿插值）→ 下游三类消费：cubemap 天空投影、可微渲染相机适配、数据集几何标注。位姿侧：rig 轨迹（trajectory.py）以 SE3 表达 → se3 垫片做插值/变换 → 动态层 `KelvinDynamicLayer._interpolation_segment`（kelvin_primitive.py:354）按时间分段插值。合并侧：voxelize/降数时逐高斯协方差走 merge_covariances 的分块 eigh。

## 设计决策

1. **垫片优于 fork/降级**：se3.py 选择"子集自实现"而不是 fork lietorch 或降 torch——与 pyproject.toml:9-11 的全 pin 策略同源：任何漂移必须显式归因。
2. **纯 torch 内核**：ray_gen 不写 CUDA 扩展，可移植性与可微性优先；性能敏感的 splat 在渲染层交给 gsplat/3DGUT（README.md:16）。
3. **分块 eigh 而非换库**：cusolver 批量上限是已知行为，分块是零依赖解法（merge_covariances.py:39）。
4. **F-Theta 一等公民**：车载鱼眼是常态而非例外，渲染侧 `_ftheta_gsplat_parameters`（renderer.py:59）与导出侧 `_looks_like_ftheta`（render_preview.py:102）双端适配，Newton 逆求值（ray_gen.py:56）保证多项式反投影可微。

## 新人提示

动 se3.py 前先跑 SE3 往返测试——数值细节（xyzw 顺序、slerp 边界）全靠测试锁死；merge_covariances 改批大小要留 cusolver 上限余量（~18M 是观测值不是文档值，merge_covariances.py:28）；新增相机模型先看 kernel_types.py:57 是否已有近似契约再改 ray_gen.py:75/:156 双投影函数；docs/camera_rectification.md 是相机矫正专题的入口文档。
