# 02 · core/cuboid.py + viz/cuboid.py — cuboid 几何协议与渲染成对读

## 角色定位

cuboid（3D 包围盒）是 NDDS 合成数据的核心标注物：NDDS 导出的每帧 JSON 里有 `projected_cuboid`（图像平面 2D 投影）与位姿（由 cuboid 尺寸重建 3D 盒）。这两个文件构成"协议+实现"的标准分层——core/cuboid.py（178 行）定义**几何数据与顶点协议**，无 OpenGL 依赖；viz/cuboid.py（245 行）定义**顶点数组渲染器**，是 viz 层里最重的绘制代码。两者与 image_draw.py 构成三方共享同一协议的镜像结构。

## 内部结构

### core/cuboid.py：协议层

- **CuboidVertexType（cuboid.py:14-25）**：8 角点编号（Front/Rear × Top/Bottom × Left/Right）+ `Center=8`，`TotalCornerVertexCount=8`/`TotalVertexCount=9`。注意它是**普通类常量**而非 IntEnum（注释保留了 IntEnum 的残迹）——因为顶点号要直接当 numpy 数组索引用。
- **CuboidLineIndexes（cuboid.py:28-45）**：12 条棱的端点索引表（前面 4 + 后面 4 + 左右连接 4）。这张表被三处消费：viz/cuboid.py:76 `np.array(...).flatten()` 做 3D 线索引、viz/cuboid.py:171-179 按 None 过滤做 2D 线索引、image_draw.py:29-35 逐条 cv2.line。
- **Cuboid2d（cuboid.py:48-70）**：投影顶点容器，numpy 数组 + get_vertex/get_vertices 两个查询。
- **Cuboid3d（cuboid.py:73-178）**：核心在 `generate_vertexes` 的**双路径**——`coord_system is None` 时按 OpenCV 轴向（X 右/Y 下/Z 前）从中心±半尺寸展开（cuboid.py:96-121）；显式给 CoordinateSystem 时按 forward/up/right 三向量×对应半尺寸组合（cuboid.py:122-130，注意尺寸分量与轴向的错位搭配：forward 配 sy、up 配 sz、right 配 sx）。`get_projected_cuboid2d`（cuboid.py:153-178）把 9 顶点乘世界矩阵后 `cv2.projectPoints`（rvec/tvec 恒零，因为旋转平移已含在矩阵里）。

### viz/cuboid.py：渲染层

- **Cuboid3dViz（viz/cuboid.py:15-124）**：构造时一次性装订全部 GL 数组——顶点 GLfloat 数组、按角点配色或类别单色的 GLubyte 颜色（viz/cuboid.py:35-53）、**面用颜色除以 4 的降透明版**（`colors_tri_gl`，viz/cuboid.py:55）、36 索引的三角面表（逆时针，viz/cuboid.py:56-71）、棱线索引、角点索引，最后打包成 ctypes 数组（viz/cuboid.py:82-93）。`on_draw`（viz/cuboid.py:92-122）一次装订三连画：半透明面 → 3px 平滑棱线 → 10px 角点。
- **Cuboid2dViz（viz/cuboid.py:127-245）**：2D 覆盖层版本。关键差异是**None 容忍**：NDDS 遮挡时投影顶点可为空，构造时把 None 顶点写成 0 坐标（viz/cuboid.py:135-160），棱与角点索引只收两端都有效的条目（viz/cuboid.py:171-179）；on_draw 只画棱线+角点不画面。

## 外部连接

- core 侧：Cuboid3d 由 `ExportedObjectSettings` 构造（nvdu_data.py:237）、`AnnotatedObjectInfo` 深拷贝并同步位姿（nvdu_data.py:341,418-421）；Cuboid2d 由帧标注的 `projected_cuboid` 构造（nvdu_data.py:385）。
- viz 侧：`AnnotatedObjectViz` 用类别色构造两个 Viz（nvdu_visualizer.py:37-38），3D 版进 `scene3d`、2D 版进 `scene_overlay`（nvdu_visualizer.py:270-274）。
- image_draw.py 的 `draw_cuboid2d` 是第三条消费线（OpenCV 离屏画法），见 explain 05 之外可单独参考。

## 数据流

```
object_settings(cuboid_dimensions/center/coord_system)
   → Cuboid3d.generate_vertexes ──(每帧) set_relative_transform──▶ 世界矩阵顶点
        └─ get_projected_cuboid2d(世界矩阵, 内参) ──cv2.projectPoints──▶ Cuboid2d
帧 JSON projected_cuboid ────────────────────────────────────────▶ Cuboid2d（免投影直用）
Cuboid3d ─▶ Cuboid3dViz（GL_TRIANGLES+LINES+POINTS）──▶ scene3d
Cuboid2d ─▶ Cuboid2dViz（GL_LINES+POINTS, None 跳过）─▶ scene_overlay（正交+Y 翻转）
```

两条到 Cuboid2d 的路（本地投影 vs NDDS 导出值）并存，可视化默认用导出值。

## 设计决策

1. **协议表驱动**：棱索引表一处定义三处消费，新增绘制端零协议改动——微型仓里的接口中心化样板。
2. **ctypes 数组预建**：构造时建好 `GLfloat*`/`GLubyte*`，draw 只调 glVertexPointer/glDrawElements，避免每帧 Python 循环——立即模式时代为数不多的性能意识。
3. **面/线/点三合一**：一次 on_draw 画完，颜色数组切换（降透明版 vs 原版）实现"面透线实"的标注视觉惯例。
4. **None 容忍放在索引生成期**而非 draw 期：把遮挡缺失的分支成本移出渲染循环。
5. **双路径顶点生成**：默认 OpenCV 轴向方便手写测试，CoordinateSystem 路径承接 NDDS 任意朝向物体——但两条路径的尺寸分量搭配不同（sy↔forward），改动时易踩。

## 新人提示

改 cuboid 相关代码先读 cuboid.py:14-45 的 25 行协议——所有下游（渲染、离屏画图、标注导出对齐）都押在编号顺序上。Cuboid3dViz 的颜色是 RGBA 的 GLubyte（0-255），类别色从 `ExportedObjectSettings` 的位运算生成（nvdu_data.py:227-230）一路传到 GL 数组，中途没有色彩空间转换。想验证投影正确性，最快的办法是用 image_draw.draw_cuboid2d 在原图上离屏画一遍与 NDDS 导出的 2D 标注对比——三者共用同一张棱表，结果应当逐像素一致。
