# 01 · nvdu/core/nvdu_data.py — NDDS 数据集解析枢纽

## 角色定位

全仓最大（497 行）也最核心的模块：把 NDDS（Unreal 合成器）落在磁盘上的三样东西——数据集目录（`*.png` 帧 + 同名 `.json` 标注）、`_object_settings.json`（物体静态设置）、`_camera_settings.json`（相机内参）——解析成带 3D 位姿的 Python 对象图。它同时是 core 层的收口：模块头部连续星号导入 utils3d/transform3d/cuboid/pivot_axis/mesh/camera 六个兄弟模块（nvdu_data.py:19-24），把散落的几何基元组装成业务对象。可视化层（nvdu_visualizer.py）和资产层（nvdu_ycb.py）都只消费它。

## 内部结构

模块按四个区块组织：

**帧文件约定（nvdu_data.py:26-112）**：`FrameAspectDict` 定义 main/depth/pls/pls_no 四种画幅扩展名（`.png`/`.depth`/`.pls`/`.pls_no`）；一串路径工具函数（`get_frame_name` 六位零填充、`get_frame_image_path` 按画幅拼后缀）；最有趣的是 `get_number_of_frames`（nvdu_data.py:97-112）——在 [1, 1000000] 区间对"帧图片是否存在"做**二分查找**计数帧数，O(log n) 避免遍历百万文件，是仓里少见的算法亮点（虽然 NVDUDataset.scan 实际用的是目录枚举而非它）。

**NVDUDataset（nvdu_data.py:114-211）**：数据集目录扫描器。`scan()` 遍历目录、按图片名过滤器（默认 `*.png`）匹配、去扩展名得帧名、**只保留同名 `.json` 标注存在**的帧并排序（nvdu_data.py:144-175）；`get_frame_file_path_from_index/name` 把帧号映射到（图片路径, 标注路径）二元组；两个 staticmethod 给出 `_camera_settings.json`/`_object_settings.json` 的默认路径。

**设置解析三件套（nvdu_data.py:216-320）**：`ExportedObjectSettings` 是单个物体的静态档案——mesh 路径、`fixed_model_transform` 初始矩阵、cuboid 尺寸/中心/坐标系，构造时顺手从 `segmentation_class_id` 用位运算生成类别色（`id>>5`、`(id>>2)&7`、`id&3` 三段映射 RGB，nvdu_data.py:227-230），并预建 Cuboid3d 与 PivotAxis；`ExporterSettings` 只装 `captured_image_size`；`DatasetSettings.parse_from_json_data` 遍历 `exported_objects` 数组构建类名→设置的字典，`get_object_settings`（nvdu_data.py:309-320）精确匹配失败后用 **fuzzyfinder 模糊兜底**——对抗标注类名与设置类名的漂移。

**逐帧标注双类（nvdu_data.py:324-497）**：`AnnotatedObjectInfo(SceneObject)` 承载单物体位姿——从 object_settings 深拷贝 cuboid3d、新建 Mesh 与 PivotAxis（nvdu_data.py:339-344）；`parse_from_json_object` 解析 location/quaternion_xyzw/cuboid_centroid/projected_cuboid/keypoints，末尾 `update_transform()` 把位姿同步给三个子对象（nvdu_data.py:410-426）。`AnnotatedSceneInfo` 聚合一帧：`create_from_file`（nvdu_data.py:486-497）json.load 标注 + `cv2.imread` 帧图并 BGR→RGB（`image_data[:,:,::-1]`，nvdu_data.py:490-491），`create_from_json_data` 逐物体解析。

## 外部连接

- 被 `nvdu/tools/nvdu_ycb.py`（读 DatasetSettings 拿对齐矩阵）、`nvdu/tools/test_nvdu_visualizer.py`（装配入口）、`nvdu/viz/nvdu_visualizer.py` 与 `nvdu_viz_window.py`（消费 AnnotatedSceneInfo）四方依赖，是图谱入度最高的节点。
- 通过 `nvdu/core/__init__.py` 的星号导出对外暴露全部公开名。

## 数据流

```
磁盘                          内存
_object_settings.json ──DatasetSettings.parse_from_file──▶ obj_settings{class→ExportedObjectSettings}
帧 000123.json + png ──AnnotatedSceneInfo.create_from_file──▶ objects:[AnnotatedObjectInfo]
                              └─ 每个含 location/quaternion + cuboid2d(投影) + cuboid3d/mesh/pivot_axis(深拷贝)
```

viz 侧拿到 AnnotatedSceneInfo 后只做包装不再解析——**解析与渲染的单向分工**在这个仓里执行得很干净。

## 设计决策与坑

1. **类名缺失的硬编码兜底**：帧 JSON 缺 `class` 键时默认 `'002_master_chef_can_16k'`（nvdu_data.py:361-363）——静默给错误物体而非报错，调试时极具迷惑性。
2. **分数→像素换算被注释**：projected_cuboid 的 `img_width * vertex['x']` 换算整段注释掉（nvdu_data.py:380-382），cuboid2d 直接用原始坐标；而 `DatasetSettings.parse_from_json_data` 又从不填 `exporter_settings.captured_image_size`（留默认 [0,0]），真值由 CLI 从相机设置文件补齐（test_nvdu_visualizer.py:95-97）——两段代码合谋后的实际语义是"投影 cuboid 按 NDDS 导出的绝对像素坐标使用"。
3. **`@classmethod` 首参命名 self**（nvdu_data.py:355-356）：能跑，但当 cls 用，纯风格陷阱。
4. **import future**（nvdu_data.py:5）：Py2/3 过渡遗物，现代环境无 future 包时整个模块 import 失败——复跑第一道墙。
5. 深拷贝 cuboid3d（`copy.deepcopy`，nvdu_data.py:341）但 pivot_axis 直接共享引用——同帧多物体时 pivot_axis 是同一对象，位姿同步靠 update_transform 每次重写，语义上没错但共享/拷贝的选择没有说明。

## 新人提示

读这个模块建议自底向上：先 utils3d/transform3d/scene_object 三块数学地基，再从 `AnnotatedSceneInfo.create_from_file`（nvdu_data.py:486）倒着追——它是"一次可视化调用的完整数据剖面"。要二次利用 NDDS 解析能力，只 import 这个模块即可，core 层无 OpenGL 依赖（cv2 只在读图与投影出现）。564 帧的真实 NDDS 数据集上，scan() 的排序保证了帧序与文件名序一致，跨帧导航（窗口层 ±1/±100）依赖这个不变量。
