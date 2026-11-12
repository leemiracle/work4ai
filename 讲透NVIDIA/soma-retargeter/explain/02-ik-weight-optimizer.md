# 02 · IK 权重优化器 app/tools/ik_weight_optimizer.py（3004 行）

## 角色定位

全仓最大的单文件，一个"语料级校准工具"：反复对一组 BVH 跑重定向、测跟踪误差、提出新的 effector IK 权重、只接受满足目标与剪裁策略的更新（documentation/ik-weight-optimizer.md 开篇定义）。它不改模型结构与限位，最终产物只覆盖 ik_match_table 的 t_weight/r_weight（`_build_retargeter_config` :1675）。

## 内部结构

五段式布局。①配置与数据类：`_validate_config`（:87）+ 一排 frozen dataclass——`OptimizerParameters`（:176）可变参数向量、`SymmetryPair`（:200）左右对称对、`IkWeightUpdateConfig`（:720）、`LineSearchConfig`（:754）、`ClipGuardConfig`（:779，from_config :820）；②评估：Warp kernel `_extract_body_poses_kernel`（:508）+ `BodyEvaluator`（:532）从求解结果抽 body 姿态算指标，`_compute_metrics_from_poses`（:886）；③守卫：ClipGuard 全家（`_clip_guard_violations` :1093、`_aligned_frame_regression` :1252、`_catastrophic_violations` :1390、决策 `_ClipGuardPolicy.probe` :1518）；④主循环 `run_optimizer`（:2549）+ CLI `main`（:2980）；⑤仪表盘（`_draw_dashboard` :1854、PNG 渲染 :1987）。

## 外部连接

对内完全复用主管线：`_make_pipeline`（:317）按 retargeter_overrides 造关闭后处理的评估管线，`OptimizerConfigWorkspace`（:251）持有目标机器人的基础 retargeter 配置；机器人发现走 `robot_registry.register_robots_path`（:163 调 robot_registry.py:132）。输入语料 `_gather_bvh_files`（:136）默认 15 条优化动作（assets/motions/optimizer/）。指标聚合 `_aggregate_metrics`（:377）+ 按跟踪损失改善排名 `_rank_motions_by_tracking_loss_improvement`（:408）导出 CSV（:481）。

## 数据流

外层迭代（`for outer_idx in range(outer_iterations)` :2776）：以当前 anchor 为基点，`_updated_params`（:1030）按学习率与步长缩放提出 trial 权重 → 线搜索 n_probes 次（:2785，max_backtracks 可配）→ `_ClipGuardPolicy.probe`（:1518）对 clip 帧损失 p95、对齐帧损失回归、灾难加速度尖点（配置 catastrophic_accel_spike_regression=1.5）给出 blocking/advisory 两级裁决 → 接受则更新 anchor 并记 ACCEPT/REJECT/HOLD 日志（:2255/:2295/:2329）→ 收敛或耗尽迭代后 `_finalize_run`（:2425）写出优化版配置与迭代指标 CSV（:1829）。

## 设计决策

1. **对称约束压参数量**：`_apply_symmetry_constraints`（:343）强制 Left*/Right* effector 同步，搜索空间近似减半且天然防左右漂移。
2. **接受/保持而非回滚**：拒绝时保持 anchor（HOLD 路径 :2329），基线永不劣化——工程上"宁可不进步也不退化"。
3. **误差模型流式构建**：`_build_error_model_streamed`（:1602）+ `_load_bvh_batch`（:2103）分批装载，语料增长不受显存限制。
4. **effector 优先级注入**：`_apply_effector_priorities`（:1573）把 Hips/Feet 等部位先验乘进目标（配置 position_weights Hips=5.0）。

## 新人提示

实验特性（文档加粗声明）：采纳前必须与基线目测对比。跑之前先读出厂配置 app/tools/assets/ik_optimizer/ik_weight_optimizer_config.json（target_type=unitree_h2、outer_iterations=50、learning_rate=0.075）；文档示例里的 unitree_h1 是"配置器新增机器人"教学语境，仓内并无 H1 资产。
