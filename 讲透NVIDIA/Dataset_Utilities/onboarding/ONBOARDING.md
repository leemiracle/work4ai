# NVDU（NVIDIA Dataset Utilities）上手指南

> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/Dataset_Utilities`（2018 年 NVIDIA 开源，CC BY-NC-SA 4.0，commit 532b8c76）
> 图谱：仓内 `.understand-anything/knowledge-graph.json`（89 节点 / 208 边 / 10 层 / 15 步导览，validator 0 issues，fingerprints 37 文件基线）

## 1. 一句话定位

NVDU 是 **NVIDIA Deep learning Dataset Synthesizer（NDDS）合成数据集的标注检视工具**：把 NDDS（Unreal Engine 插件，姊妹仓 Dataset_Synthesizer）导出的 `_object_settings.json` / `_camera_settings.json` / 逐帧 `000000.json` 标注文件，解析成带 3D 位姿的内存对象，再用 pyglet+OpenGL 把 3D cuboid、mesh、坐标轴、关键点叠画在合成帧图上，供合成数据质检；顺带提供 YCB 模型库的下载-对齐资产管线（nvdu_ycb），是 FAT 数据集（Falling Things）的工具链组件。

两个控制台命令（`setup.py:74-79` 的 entry_points）：

| 命令 | 实现体 | 用途 |
|---|---|---|
| `nvdu_viz` | `nvdu/tools/test_nvdu_visualizer.py:37` 的 `main()` | 交互式可视化 NDDS 数据集 |
| `nvdu_ycb` | `nvdu/tools/nvdu_ycb.py:225` 的 `main()` | 下载/对齐/列举 YCB 模型 |

**命名陷阱**：`test_nvdu_visualizer.py` 不是单元测试，是 `nvdu_viz` 命令的正式产品入口（setup.py entry_points 钉板）。

## 2. 技术栈与运行环境

- **语言**：纯 Python，2018 年风格（`from x import *` 泛滥、类名小写 `transform3d`）。
- **依赖**（`setup.py:50-55`）：numpy、opencv-python、pyrr（四元数/矩阵）、**PyWavefront==0.2.0（钉死版本）**、pyglet（窗口+立即模式 OpenGL）、fuzzyfinder（类名模糊匹配）。
- **Python 版本红线**：readme 明示 OpenCV-python 当年不兼容 3.7，**只支持 Python 3.5/3.6**——现代环境直接 pip 装大概率失败，阅读价值 > 运行价值。
- **渲染技术**：pyglet 1.x 时代的**立即模式 OpenGL**（glBegin/glEnd、glVertexPointer 顶点数组、glMultMatrixf 固定管线），无 shader。
- **许可**：CC BY-NC-SA 4.0（`LICENSE.txt`），**非商用**——与 NVIDIA 多数开源仓的 Apache/MIT 不同，二开须注意。

## 3. 目录结构与模块地图

```
Dataset_Utilities/
├── setup.py                    # 打包入口 + 两个 console_scripts（L01 层）
├── readme.md                   # 安装与两命令用法 + 键盘控制表
├── nvdu/
│   ├── __init__.py             # 空包标记；nvdu_ycb 靠 nvdu.__path__[0] 定位 data/config
│   ├── core/                   # 纯数据层（不依赖 OpenGL）
│   │   ├── utils3d.py          #   CoordinateSystem + Rotator（L02）
│   │   ├── transform3d.py      #   位姿容器：位置/缩放/四元数→矩阵（L02）
│   │   ├── scene_object.py     #   SceneObject 场景图基类（L03）
│   │   ├── box.py / mesh.py / pivot_axis.py  # 轻量基元（L03）
│   │   ├── camera.py           #   CameraIntrinsicSettings 内参（L04）
│   │   ├── cuboid.py           #   CuboidVertexType 协议 + Cuboid2d/3d（L05）
│   │   ├── nvdu_data.py        #   ★核心枢纽：数据集扫描+标注解析（L06，497 行全仓最大）
│   │   └── __init__.py         #   星号导出 7 个子模块的桶文件
│   ├── viz/                    # 渲染层（pyglet/OpenGL）
│   │   ├── utils3d.py          #   OpenCV↔OpenGL 桥接 + RenderMode（L08）
│   │   ├── scene_object.py     #   SceneObjectVizBase/Viz3d 双基类（L08）
│   │   ├── scene.py            #   Scene/Scene2d/Scene3d（L08）
│   │   ├── viewport.py / camera.py / background_image.py（L08）
│   │   ├── cuboid.py / mesh.py / pivot_axis.py / pointcloud.py / image_draw.py（L09 渲染器）
│   │   └── nvdu_visualizer.py + nvdu_viz_window.py  # 编排+窗口（L10）
│   ├── tools/
│   │   ├── nvdu_ycb.py         # YCB 资产管线 CLI（L07）
│   │   └── test_nvdu_visualizer.py  # nvdu_viz CLI（L10）
│   └── config/object_settings/ # 三份 YCB 物体设置 JSON（L07）
```

37 文件，规模上属微型仓，但 core/viz 双层架构完整：**core 层无任何 OpenGL import，可独立做数据解析；viz 层只消费 core 的内存对象**。

## 4. 核心数据流

```
nvdu_viz CLI（test_nvdu_visualizer.py:37 main）
  │  ① NVDUDataset(dataset_dir).scan()          nvdu_data.py:144  枚举有 .json 标注的 *.png 帧
  │  ② DatasetSettings.parse_from_file(...)     nvdu_data.py:291  解析 _object_settings.json
  │     └─ 每物体 → ExportedObjectSettings      nvdu_data.py:216  mesh路径/初始矩阵/cuboid尺寸/类别色
  │  ③ CameraIntrinsicSettings.from_json_file  camera.py:88      解析 _camera_settings.json（含 UE 矩阵符号修正）
  │  ④ 循环每帧：AnnotatedSceneInfo.create_from_file  nvdu_data.py:487
  │     ├─ json.load 帧标注 → AnnotatedObjectInfo.parse_from_json_object  nvdu_data.py:356
  │     │    位置/四元数/cuboid_centroid/projected_cuboid/keypoints
  │     │    └─ update_transform → 同步 mesh/cuboid3d/pivot_axis 三个子对象位姿  nvdu_data.py:410-426
  │     └─ cv2.imread 帧图 BGR→RGB
  ▼
viz 侧：AnnotatedSceneViz（nvdu_visualizer.py:114）把标注包装成渲染对象
  └─ NVDUVisualizer.draw()（nvdu_visualizer.py:229）
       ├─ scene_bg   ← BackgroundImage（帧图纹理）
       ├─ scene3d    ← MeshViz + Cuboid3dViz + PivotAxis（乘世界矩阵）
       └─ scene_overlay ← Cuboid2dViz + PointCloud2d（关键点）
NVDUVizWindow（nvdu_viz_window.py:14）pyglet 事件循环驱动帧导航/图层开关/截图导出
```

YCB 资产线（独立于可视化）：`nvdu_ycb --setup` → 读 `_ycb_original.json` 的 `fixed_model_transform`（nvdu_ycb.py:181 `align_ycb_model`）→ `transform_wavefront_file`（nvdu_ycb.py:114）逐行变换 obj 顶点 → 产出对齐模型供可视化时 `Model3dManager`（viz/mesh.py:22）加载。

## 5. 关键设计决策

**（a）cuboid 顶点协议先行。** `CuboidVertexType`（core/cuboid.py:14）的 8 角点+Center 编号和 `CuboidLineIndexes`（core/cuboid.py:28）的 12 条棱索引表，是 core 数据层、viz 渲染层（viz/cuboid.py 直接 flatten 该表做 GL 索引）、OpenCV 离屏画图（image_draw.py:24）三方共享的唯一几何协议——小仓也有协议中心化意识。

**（b）OpenCV 约定为数据基准系。** `CoordinateSystem`（core/utils3d.py:12）默认 forward=Z/right=X/up=-Y，即 OpenCV 右手系；所有标注数据按此存储。渲染时由 `opencv_to_opengl_matrix`（viz/utils3d.py:26，Y/Z 双翻）与 `get_opengl_matrixf`（viz/utils3d.py:10，行/列主序转换）两处桥接进 OpenGL；2D 覆盖层在 Scene2d.draw（viz/scene.py:55-57）里平移+翻 Y 把像素坐标（Y 向下）映射到 OpenGL（Y 向上）。

**（c）UE→OpenCV 的两处"手搓修正"。** ① 四元数合成时 qx/qy/qz 取负（transform3d.py:32 附近，代码 TODO 坦承"必须翻转但原因待查"）；② 相机投影矩阵解析时手工翻转 [2,0]/[2,1]/[2,3]/[3,2] 四元素（core/camera.py:75-78）——NDDS 由 UE 导出，左手系数据的修正散落在消费端而非导出端。

**（d）惰性与缓存贯穿渲染。** transform3d 用 is_changed 脏标记惰性重算矩阵（transform3d.py:24-30）；MeshViz 首次 draw 才向模块级单例 `GlobalModelManager`（viz/mesh.py:57）要模型；投影矩阵 None 时才算（camera.py:108-111）。

**（e）类名模糊兜底。** `DatasetSettings.get_object_settings`（nvdu_data.py:309-320）精确匹配失败后用 fuzzyfinder 模糊找最近类名——对抗 NDDS 标注类名与设置文件类名的漂移（如 `_16k` 后缀差异，get_mesh_file_path nvdu_data.py:53-57 专门剥该后缀）。

**（f）半透明面+棱线+角点三合一的 cuboid 画法。** Cuboid3dViz 一次装订顶点/颜色/索引数组，先画面（顶点色除以 4 降透明度，viz/cuboid.py:55 附近 `colors_tri_gl`），再画 3px 棱线，最后 10px 角点（viz/cuboid.py:92-122 on_draw）；2D 版构造时就跳过 None 顶点（viz/cuboid.py:171-179），容忍 NDDS 遮挡导致的投影缺失。

## 6. 依赖分层（图谱视角）

10 层图谱（knowledge-graph.json layers）自底向上：L01 仓库根基 → L02 3D 数学（utils3d/transform3d，0 内部依赖）→ L03 场景图（SceneObject 挂 Mesh/PivotAxis/Box2d）→ L04 相机 → L05 cuboid 几何 → L06 数据集解析（nvdu_data 聚合 L02-L05 全部，import 6 个模块，是全仓入度最高的枢纽）→ L07 YCB 资产（依赖 L06）→ L08 渲染基座（viz 基类/场景/视口/背景，反向依赖 core 层）→ L09 对象渲染器（消费 core 的 cuboid/mesh 数据结构）→ L10 编排与入口（nvdu_visualizer 汇聚 L08/L09 + core 数据，窗口与 CLI 收口）。

要点：**viz 层每个渲染器都成对依赖"core 数据类 + viz 基类"**（如 viz/cuboid.py 同时 import core/cuboid.py 与 viz/scene_object.py），形成 core↔viz 的规整镜像结构；`tested_by` 边只有 test_nvdu_visualizer.py 一个汇点——本仓没有真正的单元测试。

## 7. 常见任务入口

- **可视化一个 NDDS 数据集**：`nvdu_viz <dataset_dir> -m <ycb_model_dir>`；数据集目录须含 `*.png` + 同名 `.json` + `_object_settings.json` + `_camera_settings.json`（缺省路径逻辑见 test_nvdu_visualizer.py:87-97）。
- **键盘**（readme 控制表 ↔ nvdu_viz_window.py:128-160 代码实证）：F3/F4 切 2D/3D cuboid、F5 切 mesh、F6 切坐标轴、F7 切信息文字、F8 切关键点、F12 开启逐帧导出到 `viz/`、1/2/3 切填充/线框/点渲染、←/→ ±1 帧、↑/↓ ±100 帧、空格自动播放（fps 由 `--fps` 定，pyglet clock 调度见 nvdu_viz_window.py:210-222）。
- **准备 YCB 模型**：`nvdu_ycb --setup`（全量 21 物体下载+对齐）、`--list` 列物体名、`nvdu_ycb <name>` 查单个物体路径；模型落到包内 `data/ycb/{original,aligned_m,aligned_cm}/`。
- **二次开发解析层**：只 import `nvdu.core`（nvdu_data.py 的类都能脱 OpenGL 使用），cv2 仅在 create_from_file 读图与 cuboid 投影处出现。

## 8. 坑与勘误清单（源码级实证）

1. **`Box2d` 是死代码**：构造函数 `super(BoundingBox2d, self)`（core/box.py:10）引用未定义类名，实例化即 NameError；`get_width/get_height/get_size`（core/box.py:20-26）还缺 self 参数。全仓无调用方。
2. **Rotator 便捷入口全坏**：`yaw/pitch/roll` 属性读 `self.angle`（应为 `self.angles`，core/utils3d.py:43-53），两个工厂方法返回未定义的 `rotator(...)`（core/utils3d.py:55-59）——只有 `to_rotation_matrix`/`to_quaternion` 可用。
3. **相机 z 范围退化**：`DEFAULT_ZFAR = DEFAULT_ZNEAR`（=1，core/camera.py:13-14），`calculate_projection_matrix` 的 zdiff=0 走 c=0/d=-zneer 退化分支（core/camera.py:114-132）；viz 层 Camera 的 DEFAULT_ZFAR=100000（viz/camera.py:24）是另一套值。
4. **`set_fovx` 是死入口**：算了新内参却没赋回 self（viz/camera.py:86-92）。
5. **`AnnotatedObjectViz.update_transform` 引用不存在属性**：读 `self.location/self.quaternion`（nvdu_visualizer.py:57-70），该类只有 `object_info.location`——`is_modified` 一旦置真即 AttributeError 的潜伏地雷。
6. **`AnnotatedSceneViz.set_image_data` 死路径**：引用不存在的 `self.dataset_settings`（nvdu_visualizer.py:156，真实路径 `_scene_info.dataset_settings`）。
7. **分数→像素换算被注释**：projected_cuboid 的 `img_width * vertex['x']` 换算整段注释掉（nvdu_data.py:380-382），cuboid2d 直接用原始坐标；且 `DatasetSettings.parse_from_json_data` 从不解析 captured_image_size（exporter_settings 留默认 [0,0]），真值由 CLI 从相机设置文件补（test_nvdu_visualizer.py:95-97）。
8. **两份对齐配置完全相同**：`_ycb_aligned_m.json` 与 `_ycb_aligned_cm.json` md5 一致（e567bc7d…），AlignedOnly 档实际未单独维护参数；`YCBModelType.AlignedOnly=1` 指向的 aligned_m 目录在 align_ycb_model 里从不写入（只产出 AlignedCm 目录，nvdu_ycb.py:190-191）。
9. **标注类名缺失的硬编码兜底**：帧 JSON 缺 `class` 键时默认 `'002_master_chef_can_16k'`（nvdu_data.py:362-363）——静默给出错误物体而非报错。
10. **import future 语句散布**：nvdu_data.py:5 等多处 `import future`（Py2/3 兼容遗物），现代 Python 无此包时整模块 import 失败，是复跑的第一道墙。
11. **`@classmethod` 用 `self` 命名首参**：AnnotatedObjectInfo.parse_from_json_object（nvdu_data.py:355-356）——能跑但违反惯例。
12. **remove_child_object 残留调试打印**：`print('***********************************')`（core/scene_object.py:31）。

## 附：图谱使用指引

- 15 步导览（tour.json）即本文第 3-4 节的动线：T01 门面 → T02-T05 数学/场景图 → T06-T08 几何与解析 → T09 资产线 → T10-T13 渲染 → T14-T15 编排与入口。
- 深读建议顺序（按依赖）：`nvdu/core/nvdu_data.py`（497 行，理解 60% 的业务）→ `nvdu/core/cuboid.py` + `nvdu/viz/cuboid.py`（几何协议与渲染成对读）→ `nvdu/viz/nvdu_visualizer.py`（编排）→ `nvdu/tools/nvdu_ycb.py`（资产线独立可读）。
