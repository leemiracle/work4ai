# 03 · USD 进出口 soma_retargeter/io/usd.py（893 行）

## 角色定位

`io/usd.py` 承担"源角色资产"双向通道：把库内 Skeleton+AnimationBuffer 导出为带 UsdSkel 的 USD（供 DCC 工具链复核），以及把源 USD（如 soma_base_skel_minimal.usd）里的骨架、绑定变换与蒙皮网格装载进库内数据结构。重度使用 pxr API（:7 `from pxr import Usd, UsdGeom, UsdSkel, Gf`），是全仓唯一与 USD 世界的接壤面。

## 内部结构

三个功能区。①单位/轴向校正族：`get_stage_meters_per_unit`（:54）、`get_stage_up_axis`（:67）、`get_up_axis_transform`（:81，Y-up→Z-up 绕 X 转 90°，:104-115 两个方向都给）、`get_import_correction`（:121）合成旋转+统一缩放（:143-146 `src_meters/target`）、`get_prim_meters_scale`（:249）再乘 prim 自身艺术缩放；②导出：`save_skeleton_and_animation_to_usd`（:382）CreateNew stage、设上轴与米制（:397-398）、SkelRoot/Skeleton/Animation 三 prim（:404-412）、逐帧写 translations/rotations 属性（:419-431）；③装载：`discover_usd_skel`（:441）遍历 stage 找 skeleton/animation/skinned_mesh 最优猜测、`extract_bind_transforms_from_usd`（:522）、`load_skinning_data_from_usd_prim`（:601）、`_load_skeletal_mesh`（:781）与外门 `load_skeletal_mesh_from_usd`（:886）。

## 外部连接

上游消费者是 GUI 与渲染链：`SkinningData`（:756）的 `remap_joint_indices`（:769）按关节名把 USD 关节索引重映射到库内 Skeleton 序——这是 USD 资产能被 renderers/mesh_renderer.py:12 的 LBS 蒙皮 kernel 驱动的关键一跳；`triangulate_mesh`（:305）把任意面片拆三角，喂给 Mesh/SkinnedMesh（animation/mesh.py:27）。批注式 TODO（:778-780）自认短板：不从 USD 建 Skeleton，骨架必须先在库内存在。

## 数据流

装载路径：stage → discover_usd_skel 拿路径与单位元数据 → get_import_correction 算"轴向旋转×米制缩放"校正 → load_skinning_data_from_usd_prim 抽顶点/索引/影响（带 `xform`）→ SkinningData.remap_joint_indices 对齐库内骨架 → SkeletalMesh 聚合进渲染器。导出路径反之：库内局部变换数组 → _wp_transform_to_gf_matrix（:373）逐帧写 Gf.Quatf/Vt 数组。蒙皮影响 remap 与 meters-per-unit 缩放被批阶段笔记标注为"跨 DCC 工具链的关键校正"——Maya（Y-up、cm）与 Isaac/Omniverse（Z-up、m）资产都能进同一条管线。

## 设计决策

1. **校正显式化**：不做隐式单位换算，而是算出 correction 交调用方决定应用面（旋转只动骨架、缩放可分 prim 独立计算，:787 的 NOTE 注释专门解释 mesh 与 skeleton scale 不许共用）。
2. **best-guess 发现**：discover_usd_skel 返回"第一个找到"的骨架/动画/网格路径（:441 docstring），牺牲严格性换零配置开箱。
3. **名字对齐而非 ID 对齐**：蒙皮重映射按 joint path 末段名字查 `skeleton.joint_index`（:773 调用），资产改名即断链——换来与 URDF/MJCF 命名体系的天然互通。
4. **用户覆盖优先**：scale 参数显式传入则覆盖自动探测（:794），自动档仅兜底（:795 打印探测值）。

## 新人提示

调试 USD 资产第一怀疑对象永远是单位：先 `get_stage_meters_per_unit` 再看 prim 自身 scale；模型"整体缩小 100 倍"几乎都是 cm 舞台的米制假设错位。第二个是 up-axis——角色躺平/竖立互换就是 :81 的旋转没被应用。
