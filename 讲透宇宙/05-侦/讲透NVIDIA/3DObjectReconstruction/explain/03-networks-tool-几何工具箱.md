# 03 · networks/tool.py — 几何工具箱（PointCloudProcessor 等）

## ① 角色定位

`src/nvidia/objectreconstruction/networks/tool.py`（612 行）是管线的**几何基础工具箱**：真实世界↔归一化训练空间的尺度换算、点云去噪聚类、网格平滑、张量/位姿四组静态工具类 + set_seed。最关键职责是**场景归一化**——NerfRunner 要求输入落在 [-1,1]³（对应 schema 的 bounding_box/near/far），由 compute_translation_scales 算出 (translation, sc_factor) 贯穿"深度→点云→SDF→网格→真实世界还原"全链。路径甄别：任务书写的 `objectreconstruction/tool.py` 不存在，实际在 networks/ 子包下。

## ② 内部结构

**模块级基础**（未注文件名的行号均指 networks/tool.py）：`GL_CAM_TO_CV_CAM`（:29-34）OpenGL→OpenCV 相机系 y/z 翻转矩阵，全仓相机约定转换唯一常量；`depth2xyzmap`（:35-54）深度反投影成 XYZ map（针孔模型，zmin=0.1 置零）；`toOpen3dCloud`（:56-66）数组转 Open3D 点云，colors>1 自动按 255 归一。

**PointCloudProcessor**（:68-344，核心类）：
- `find_biggest_cluster`（:71-113）：DBSCAN（eps=0.06、min_samples=1）取最大簇——聚类当"主物体提取 + 离群一锅端"。
- `compute_translation_scales`（:115-164）：包围盒中心为 translation、`sc_factor=max_dim/最长边`，**再乘 0.9 预留边距**（:162）防贴死 [-1,1] 边界。
- `compute_scene_bounds_worker`（:166-218）：单帧清洗——深度/掩码联合有效区 → 0.01 体素降采样 → 30 邻域统计离群移除（:212-213）→ 右乘 GL_CAM_TO_CV_CAM（:215）转世界系。
- `make_transform`（:220-243）：构造"先平移后缩放"4x4（tf1@tf，:243）。
- `compute_scene_bounds`（:245-344，模块级别名 :589）：joblib 5 线程并行（:299-303）→ 合并 → eps/5 再降采样（:317）→ 无参时 DBSCAN 出 keep_mask，**有参时改 |xyz|<1 几何过滤**（:337）→ 返回 (sc_factor, translation, 实尺度/归一化点云)。

**MeshProcessor**（:347-452）：`smooth_mesh`（:350-418）读 cfg 的 mesh_smoothing 段做 Laplacian + Taubin（λ=0.330/μ=-0.331 硬编码，:399-400）双平滑并落盘；`mesh_to_real_world`（:420-452）按 `v/sc_factor - translation`（:447-450）还原后套 pose_offset。

**TensorUtils**（:455-523）：ensure_tensor_type(s) dtype 校正器，nvbundlesdf.py:116-147 的同名包装只转发到这里。**PoseUtils**（:526-585）：`get_optimized_poses_in_real_world`（:529-585）把归一化空间优化位姿（:571 左乘修正）逆缩放还原（:574-575），以首帧对齐 offset（:577-578）校正全局漂移，逐帧右乘 GL_CAM_TO_CV_CAM（:583）。**set_seed**（:592-612）统一种子。

## ③ 外部连接

上游 import：numpy/joblib/open3d/torch/trimesh/sklearn.DBSCAN（:17-22）。下游：nvbundlesdf.py:44-53 引入 TensorUtils/compute_scene_bounds/set_seed（NVBundleSDF 场景初始化直接调 compute_scene_bounds）；nerf_runner.py 存在同名 `mesh_to_real_world`/`get_optimized_poses_in_real_world`（nvbundlesdf.py:51 引的是 NerfRunner 版处理 NeRF 输出），两套实现语义相同但独立维护；TheseusOptimizer 的位姿经 PoseUtils 还原。

## ④ 数据流

进入：多帧 (rgb, depth, mask, glcam_in_world, K)（BundleTrack 位姿是 OpenGL 约定）。加工：逐帧清洗→世界系合并→DBSCAN 主簇→归一化参数。出去两条：① 归一化点云 + (translation, sc_factor) 交 NerfRunner 锚定训练空间；② 参数在管线末端反向流动，mesh_to_real_world 与 get_optimized_poses_in_real_world 把网格与位姿还原回米制真实世界（供 USD 导出）。

## ⑤ 设计决策

1. **归一化放中间层而非改网络**：位置编码与八叉树体素（0.02）对尺度敏感，把任意物体先折进 [-1,1] 再训练使超参与场景解耦；0.9 系数（:162）给 near/far 留采样余量。
2. **DBSCAN 当分割器**（min_samples=1，:75）：选最大连通块而非去噪，贴合"桌上一个物体"的 retail 场景先验。
3. **有参/无参两分支**（:321-337）：translation/sc_factor 已定时用 `|x|<1` 几何窗替代聚类——保证跨调用一致（同一物体两次算出不同 sc_factor 会让增量重建错位）。
4. **joblib prefer="threads"**（:299）：Open3D 释放 GIL，线程并行免序列化开销。
5. **静态方法类 + 模块级别名**（:589）：沿用 BundleSDF 时代类名血统，别名是显式向后兼容补丁。

## ⑥ 新人提示

- **重磅勘误：smooth_mesh 配置键失配**——代码读 `cfg.get('lambda')`（:386-388）而 schema.py 字段名是 `lambda_`（schema.py:303，lambda 是关键字）。dataclass 默认值路径永远取不到该参数，只有 yaml 手写 `lambda:` 才生效；且代码默认 iterations=5/lambda=0.3 与 schema 默认 2/0.5（schema.py:302-303）不一致。改平滑行为前先确认改的是哪份默认值。
- GL_CAM_TO_CV_CAM 是**右乘**进位姿（:215,583），左乘会翻转相机自身而非坐标系。
- depth2xyzmap 的 zmin=0.1 与 schema 的 near=0.1 呼应但无联动——改 near 不改这里会出现光线与点云口径不一致。

---
*甄别：任务书路径 src/nvidia/objectreconstruction/tool.py 实为 networks/tool.py；图谱节点与源码逐一对上，无其他冲突。smooth_mesh 键名失配为源码级实证发现。*
