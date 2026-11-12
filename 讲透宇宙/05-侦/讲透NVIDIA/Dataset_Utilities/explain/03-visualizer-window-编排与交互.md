# 03 · nvdu_visualizer.py + nvdu_viz_window.py — 可视化编排与窗口交互

## 角色定位

viz 层的收口双模块：nvdu_visualizer.py（313 行）做**标注→渲染对象的编排**——把 core 层 AnnotatedObjectInfo/AnnotatedSceneInfo 包装成渲染器树并每帧装配进三层场景；nvdu_viz_window.py（222 行）做**pyglet 窗口与交互**——帧导航、图层快捷键、自动播放、逐帧截图导出。两者加上 CLI（test_nvdu_visualizer.py）构成 `nvdu_viz` 命令的完整实现链。

## 内部结构

### nvdu_visualizer.py：三级编排

- **AnnotatedObjectViz（nvdu_visualizer.py:30-111）**：单物体聚合器。构造时一口气建五个渲染对象——类别色的 Cuboid2dViz/Cuboid3dViz、PivotAxis、MeshViz、以及把 keypoints 的 `projected_location` 抽成点集的 PointCloud2d（nvdu_visualizer.py:36-55）；`update_settings` 按 VisualizerSettings 与位姿有效性逐个 set_visibility（nvdu_visualizer.py:86-111）；`draw` 按设置画 mesh/cuboid3d/pivot_axis（nvdu_visualizer.py:73-89）。
- **AnnotatedSceneViz（nvdu_visualizer.py:114-178）**：场景级。为每个标注对象建 AnnotatedObjectViz；背景图尺寸取 `exporter_settings.captured_image_size`，拿不到时**回退到相机内参分辨率**（nvdu_visualizer.py:128-141）；帧图非空则建 BackgroundImage，并生成 pyglet 信息文字（帧名标签，nvdu_visualizer.py:143-156）。
- **VisualizerSettings（nvdu_visualizer.py:181-214）**：七个显隐布尔 + 渲染模式 + ignore_initial_matrix，每个开关配 toggle 方法（作者 TODO 里写着"想用模板"）。
- **NVDUVisualizer（nvdu_visualizer.py:216-313）**：门面。持 Camera + Viewport + Settings；`draw()`（nvdu_visualizer.py:229-269）**每帧重建**三层场景对象表——背景图进 scene_bg，mesh/cuboid3d/pivot_axis 进 scene3d，cuboid2d/keypoint2d 进 scene_overlay，最后 viewport.draw()；`visualize_dataset_frame`（nvdu_visualizer.py:291-300）是取帧→解析→set_scene_data→draw 的完整一帧管线；对外 7 个 toggle/set 方法与窗口层键盘一一对应。

### nvdu_viz_window.py：交互层

- `dataset` 的 setter 里触发 `scan()`（nvdu_viz_window.py:39-49）——赋值即扫描，帧数打印。
- `on_draw`（nvdu_viz_window.py:68-80）：clear → 更新文字颜色 → visualizer.draw → 若在导出态则 `save_current_viz_frame` 截屏存 `viz/{帧名}_viz.png`（nvdu_viz_window.py:99-113）。
- `on_key_press`（nvdu_viz_window.py:128-160）：F3/F4 切 2D/3D cuboid、F5 切 mesh、F6 切坐标轴、F7 切信息层、F8 切关键点、F12 切导出、1/2/3 切填充/线框/点、空格切自动播放。注意 F3 是独立 if、其余是 elif 链——行为等价但风格不一致。
- `on_text_motion`（nvdu_viz_window.py:153-160）：←/→ ±1 帧、↑/↓ ±100 帧，`set_frame_index` 自动取模环绕（nvdu_viz_window.py:115-140）。
- 自动播放由 `pyglet.clock.schedule_interval(visualize_next_frame, 1/fps)` 驱动（nvdu_viz_window.py:210-222），关播 unschedule。
- 导出态可视化反馈：标题栏加 `" - Exporting ..."` 后缀 + 信息文字变红（nvdu_viz_window.py:173-179）。

## 外部连接

- 下行依赖：core/nvdu_data（标注对象）、viz 七个模块（相机/cuboid/mesh/背景/视口/点云）；上行被 nvdu_viz_window 与 CLI 消费。`tested_by` 边的汇点 test_nvdu_visualizer.py 直接驱动两者。
- PivotAxis 的引用是**星号导入链泄漏**：nvdu_visualizer.py 注释掉了 `from .pivot_axis import *`（nvdu_visualizer.py:23），实际经 `from .mesh import *`（mesh.py 又导入 pivot_axis）把 PivotAxis 名字带进来——删掉 mesh 导入会意外破坏 PivotAxis 引用。

## 数据流（一帧的生命周期）

```
按键 →/on_text_motion → set_frame_index(i)
  → visualize_current_frame → NVDUVisualizer.visualize_dataset_frame(dataset, i)
     → AnnotatedSceneInfo.create_from_file（json+png）
     → set_scene_data → AnnotatedSceneViz（含五件套 object viz + 背景图 + 文字）
  → NVDUVisualizer.draw() 装配三层场景 → Viewport.draw()
     → Scene2d(背景) → Scene3d(相机投影+世界矩阵对象) → Scene2d(覆盖层)
  → on_draw 尾部：导出态则截屏落盘
```

## 设计决策与坑

1. **每帧重建场景对象表**（draw 里 add_object 而非增量更新）：实现简单、无状态残留，代价是每帧重建 Python 列表——对 10fps 的检视工具完全可接受，是"工具代码不做过早优化"的示范。
2. **update_transform 的潜伏 bug**：引用不存在的 `self.location/self.quaternion`（nvdu_visualizer.py:57-70，真实数据在 object_info 上）——is_modified 置真即 AttributeError，当前代码路径恰好不触发。
3. **set_image_data 死路径**：引用不存在的 `self.dataset_settings`（nvdu_visualizer.py:156），该方法全仓无调用方。
4. **窗口尺寸=相机分辨率**：CLI 里 `--size` 缺省 0 时取内参 res（test_nvdu_visualizer.py:110-113），注释明言"暂不支持缩放"——背景图与窗口 1:1 是隐含约定。
5. **导出判定的双条件 property**：`should_export = _should_export and export_dir`（nvdu_viz_window.py:51-53）用 property 表达"开关+目录都就绪"，F12 只翻开关——目录默认 viz/ 在翻开关时补。

## 新人提示

加新图层（比如深度图叠加）的路径：VisualizerSettings 加开关 → AnnotatedObjectViz/SceneViz 加渲染对象 → NVDUVisualizer.draw 装配 → 窗口层加快捷键转 toggle——四步都在这两个文件里，动线极短。调键盘问题时记得 pyglet 的 `key._1/_2/_3` 命名（数字键带下划线前缀）。自动播放的 fps 由 CLI `--fps` 传入（默认 10），`set_auto_fps` 里 fps<=0 会关播——`--fps 0` 是"只看单帧"的合法用法。
