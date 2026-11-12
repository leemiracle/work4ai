# 07 · `src/torchio/transforms/spatial/spatial.py`：空间统一引擎

## 一、角色定位

全库最重的单文件（2762 行），module docstring（`spatial.py:1-13`）自述使命：把**重采样、全局仿射、弹性形变合并进单次 `grid_sample` 调用**。公开 API 只有一个全功能类加三个便捷子类：`Spatial`（`spatial.py:158`）、`Resample`（`spatial.py:759`）、`Affine`（`spatial.py:806`）、`ElasticDeformation`（`spatial.py:872`）。合并动机是精度与性能：连续空间变换各自独立重采样会逐级累积插值误差；统一引擎一次构网格一次插值，顺带把抗混叠、部分体积标签重采样、逐实例几何收进同一路径。注意 ONBOARDING 勘误 #3：`transforms/spatial/` 目录下**没有** affine.py/resample.py 独立源文件，按文档页文件名找源码会扑空。

## 二、内部结构

四大块：

**类型与常量**（:68-155）：`TypeParameterValue`（:68）穷举随机参数五形态（标量/二元组/三元组/六元组/Choice/分布）；插值阶数表 `_INTERPOLATION_TO_ORDER`（:140，nearest=0 到 seventh=7）；`LABEL_INTERPOLATION = "label"`（:127）是部分体积标签模式的哨兵值。

**`Spatial` 类**（:158-676）：`__init__`（:307）约 18 个参数全走解析函数（`_to_positive_range` :332 管 scales 正数、`_parse_interpolation` :2589 等），两处构造期硬校验：locked_borders=2 且 4 控制点恒等（:345-350）、`image_interpolation` 不许用 "label"（:353-358）。能力声明 `supports_per_instance_params=True`（:371-373）与 `supports_per_instance_p`（:375-380，**仅当 target 为 None**——重采样改网格，被门掉元素无法保持形状）。`_sample_one`（:382）采一次"缩放+欧拉角+平移+控制点场"几何：`_has_affine_component`（:2508）判有无仿射分量、`_resolve_control_points`（:2219）在位移全零时返回 `(None, None)`（:2235-2236）。`make_params`（:436）双路径：批共享（:468-488）或逐元素（:490-513，`_sample_per_element_geometry` :515 产 B 套，被门掉元素填 None 占位 :544-547），全部经 `_serialize_*` 族（:2427-2471）转 JSON 形态——历史回放的前提。`apply_transform`（:560）先判真空 no-op（:579-590）再进引擎。`inverse`（:617-676）：仿射**精确求逆**（:667 `np.linalg.inv`）、弹性**取负近似**（:671）、`affine_first` 翻转（:639）、逐实例逐元素反转（:654-662 走 `_invert_per_sample` :925）；产物是私有 `_SpatialInverse`（:679，`make_params` 返回空 :727-729）。

**三个便捷子类**：`Resample`（:759，`target` 默认 1mm :789）；`Affine`（:806，构造尾调 `_warn_if_noop` :862-869，`is_constant` 判定来自 `parameter_range.py:186`）；`ElasticDeformation`（:872，`max_displacement` 默认 7.5mm :906）。三者只是 `Spatial.__init__` 的参数预设，无独立执行路径。

**引擎函数族**（模块级约 40 个）：入口 `_apply_spatial_to_batch`（:1110）——按批内第一张图几何建网格，共享参数单网格（:1144-1155）或逐元素网格（:1156-1165 走 `_build_grid_per_sample_checked` :1011），然后逐图像 `_resample_image_batch`（:1194，按 `_image_class` 选插值 :1230-1235，label "label" 模式转 `_resample_label_partial_volume` :1275）。核心几何在 `_build_sampling_grid`（:1504）：输出体素坐标 meshgrid（`_output_voxel_coordinates` :1604）经 `A_in⁻¹ @ T⁻¹ @ A_out` 复合矩阵（`_output_to_input_voxel_matrix` :1582，公式 :1591）映回输入体素系；弹性场由控制点三线性上采样（`_upsample_displacement_field` :2171）成 mm 位移再除以 spacing 换体素偏移（:1558-1577），`affine_first` 决定先后（:1570-1577）。采样执行 `_sample_batch`（:1651）：nearest/linear 走 torch `grid_sample` 快路径（:1695），高阶 B-spline 走 `_sample_batch_interpol`（:1734）。周边：抗混叠 `_antialias_batch`（:1921）+ `_antialias_sigmas`（:1951，Cardoso MICCAI 2015 定 σ）；折叠预警 `_check_folding`（:2192，位移超粗网格半距即 warn，:2208）；仿射合成 `_build_forward_affine`（:2269，含 2D 切片面外分量抑制 :2289-2293）与 `_euler_to_rotation_matrix`（:2328）；越界填充 `_batch_fill_value`（:2034，minimum/mean/otsu，Otsu 阈值 :2133）。

## 三、外部连接

- **上游**：`SpatialTransform`（:46）、`ImagesBatch`/`SubjectsBatch`、`AffineMatrix`（:36）、`Choice`/`_ParameterRange`。
- **下游**：门面导出四个公开类（`src/torchio/__init__.py:71/37/76/50`）；`inverse.py` 回放它的历史；`docs/reference/transforms/` 下三页文档；图谱 fan-out 123 全库最高（引擎函数被四处复用）。
- **测试**：`tests/test_spatial*` 系列与 `tests/test_vectorization.py`。

## 四、数据流

`tio.Affine(degrees=(-10, 10))(batch)` 走读（逐实例路径）：

1. `Transform.forward`（06 篇）→ `Spatial.make_params`（:436）：取首图 shape/affine（:451-453）→ `_sample_per_element_geometry`（:515）对 B 个元素各调 `_sample_one`（:382）——`degrees.sample()`（:405）、`_build_forward_affine`（:2269）把欧拉角/缩放/平移绕 `center`（图像中心世界坐标 `_image_center_world` :2368 或原点）合成 4×4 世界矩阵。
2. `_check_shared_space`（:495 调用，实现 :2378）确认批内各图共享几何。
3. `apply_transform`（:560）→ `_apply_spatial_to_batch`（:1110）→ `_build_grid_per_sample_checked`（:1157）→ 每元素 `_build_sampling_grid`（:1504）：恒等 target 下 `T⁻¹` 就是逆仿射，输出网格每点被指回输入的旋转源位置。
4. `_resample_image_batch`（:1194）：ScalarImage 用 linear、LabelMap 用 nearest（:1230-1235），被概率门掉的元素经 `passthrough` 列表精确还原（:1170-1174，`_passthrough_indices` :1061——批量化恒等网格仍有 float32 计算路径，须显式回写才是逐位 no-op）。
5. 越界体素按 `default_pad_value`（:2034）填充，历史写入后 unwrap。

## 五、设计决策（含批判）

**"单次 grid_sample"统一引擎**是本库区别于朴素实现的核心竞争力：Resample+Affine+Elastic 任意复合只有一次插值，误差与算力都省；代价是巨石化——2762 行承载参数解析/几何/序列化/插值/填充五类关注点，函数族靠命名前缀分区，新人定位困难（本文行号地图就是解药）。

批判四点。其一，**弹性的逆只是近似**：仿射精确求逆（:667）而弹性取负（:671），大位移下回放残差可观——TTA 场景应控制 `max_displacement`。其二，`_check_folding`（:2192）只 warn 不拦：Jacobian 翻转的形变照样执行，解剖结构可能自交，医疗下游要自设更严阈值。其三，部分体积标签模式（:1275）内存随标签数线性增长——docstring（:255-260）自己承认数百标签的脑区分割需配合 GridSampler 分块，坑写在注释里而非报错里。其四，`supports_per_instance_p` 与 target 互斥（:380）造成语义分叉：`Affine(p=0.5)` 逐元素门、`Resample(..., p=0.5)` 批级门，差异只有读 docstring（:271-274）才知道。

## 六、新人提示

1. 记住导航口诀：**类在头部（158-923）、引擎在中部（1011-2100）、解析在尾部（2192 之后）**；找参数校验去尾部、找坐标数学去 `_build_sampling_grid`（:1504）。
2. 预处理用 `Resample`、增强用 `Affine`/`ElasticDeformation`，复合时直接 `Spatial(target=1, degrees=(-10,10))` 一步到位（docstring 示例 :293-298）。
3. 标签重采样优先 `label_interpolation="label"`（:781-784 示例）：降采样时标签体积保真度显著高于 nearest，但注意内存随标签数膨胀。
4. 降采样强度图记得 `antialias=True`（:268-273），σ 按 Cardoso 2015 自动算，省一次手调高斯。
5. 排查"变换后图像偏了一点"：先查 `center`（:209-211）、再查 LPS/RAS 源（`image.py:735`）、最后对照 `_output_to_input_voxel_matrix`（:1591）手算角点。
