# 11 · OptiX 7 与 DXR 双后端示例：MDL 材质接入两条 GPU 光追管线

## 1. 角色定位

examples/mdl_sdk 下两个大型示例演示把 MDL SDK 生成的 GPU 代码接进真实渲染器，各选一条不同的代码生成路线。**optix7**（主程序 optix7_mdl.cpp 2477 行 + 两个 .cu closest hit 着色器）是 CUDA/OptiX 7 路径演示器：小场景路径追踪器，支持 `--direct-call` 与默认两种材质接入模式。**dxr/mdl_d3d12** 是 Windows D3D12/DXR 完整示例工程（40+ 文件），本篇主角 scene.cpp（1607 行）承担场景图、变换/包围盒数学与 **MDL scene data 特性**（材质引用场景几何数据，如 vertex color）的 D3D12 落地。两者是外部集成方最常抄的两份参考实现。

## 2. 内部结构

**optix7_mdl.cpp** 按管线阶段组织。基础设施：gpuMemDup 家族（:119-151）拷显存；initEnvironmentLight（:436）+ build_alias_map（:401）为环境光建 CDF 别名表。OptiX 样板：createContext（:872）、createRadianceClosestHitProgramGroup（:922）、buildMeshAccel/buildInstanceAccel（:1250/:1314）、createPipeline（:1482，direct call 模式 max_dc_depth=1 :1531）。**MDL 接入核心是 addMDLMaterial**（optix7_mdl.cpp:1053）：先定函数名——direct call 模式必须加 `__direct_callable__` 前缀（:1064-1070），否则固定 "mdlcode"；`Target_function_description` 声明导出 `surface.scattering` 与 `thin_walled`（:1076-1080）；compile_mdl_material（:1089-1094）拿到 PTX 后查 **optix_program_cache**（按生成代码字符串去重，optix7_mdl.cpp:1111，注释指出不同 material hash 可能生成相同代码）；direct call 路走 createDirectCallables（optix7_mdl.cpp:981，:1118-1126），为每材质建 **5 个 callable 程序组** `_init/_sample/_evaluate/_pdf/_thin_walled`（:1017-1038），并处理 OptiX 7.7 前后 API 变化（optixModuleCreate :992 vs FromPTX :1002）；非 direct call 路把 MDL 生成代码直接当 closest hit 模块（:1143-1149）。纹理经 prepare_texture 上传（:1163-1173）；scene data 硬编码支持 vertex_color/row_column（:1199-1207）；:1175 TODO 明言不支持 light profile/BSDF measurement。SBT 组装（optix7_mdl.cpp:1556）给每材质×每 ray type 一条记录，含 texture_handler、argument block、callable_base_index（:1571-1610）。showMaterialGUI（:1938）用 ImGui 暴露材质参数。

**dxr scene.cpp** 分三层。数学层：Transform（:47 构造、:66 try_from_matrix、:82 look_at、:100 get_matrix）与 Bounding_box（:112-262，Zero/Invalid 哨兵、merge/extend/transform）。场景图层：Scene_node（scene.cpp:1124）组成树，update 递归（:1171）更新变换与包围盒（:1252）；Mesh（:490）持 Geometry 列表，Instance（:631）按节点实例化（:669），位移几何有专门资源管理（:686/:768）。**Scene_data 层**是 MDL 特色：Info 结构（scene.cpp:294）描述单条 scene data 的 kind/element_type/interpolation_mode/byte_offset/byte_stride（:302-389）；Geometry::update_scene_data_infos（scene.cpp:426）把顶点布局 semantic 匹配到材质注册的 scene data 名字填 per-vertex 信息（:462-473），名字不匹配或缓冲不足走 warning（:436-449）；Instance::update_scene_data_infos（scene.cpp:839）统筹：向材质 `register_scene_data_name()` 注册 per-vertex 与 per-instance 名（:853-873），注释明言用 dense map（ID 即索引）存布局以适配 GPU（:880-882）。Scene::build_scene（scene.cpp:1307）两遍加载：先收集材质再并行创建（:1315-1318 注释"并行化但保确定性"，相同描述共享 IMaterial 实例）；其后 build_acceleration_structure（:1485）。

## 3. 外部连接

- **MDL SDK**：optix7 经 optix7_mdl_helper.h 的 Mdl_helper 封装；initMDL（optix7_mdl.cpp:1217）建 helper 时指定 num_texture_results=16（:1223-1226），非 direct call 模式还 set_renderer_module 把 closest hit 的 LLVM bitcode 交给 SDK 链接优化（:1229-1235）。dxr 侧 mdl_sdk.cpp/mdl_material*.cpp 是对等封装，scene.cpp 只 include 其头（:28-36）。
- **OptiX/CUDA**：optix7 用 CUDA driver API + OPTIX_CHECK 宏；dxr 用 D3D12 + DirectXMath（Transform 内部即 XMMATRIX）。
- **公共示例库**：`mi::examples::mdl` 的 read_resource_file/find_resource_file（:1130-1133）、GL_display、imgui。
- **外部资产**：dxr 的 gltf.cpp 实现 IScene_loader（scene.cpp 输入端）。
- 两示例互不依赖但结构同构：application 样板→材质编译→资源上传→管线组装→渲染循环（optix7 launchSubframe optix7_mdl.cpp:1709 / dxr Scene::update :1510）。

## 4. 数据流

**optix7 启动流**：main（optix7_mdl.cpp:2276）解析参数（class_compilation 默认 true :2291）→ createContext → initMDL（建 helper，可能挂 renderer module）→ loadMaterials 逐个 addMDLMaterial（编译→缓存查重→建 callable/hit group→传纹理→记 scene data）→ 建 mesh/instance 加速结构 → createPipeline/createSBT（每材质 SBT 记录取 argument block）→ 渲染循环 launchSubframe 每帧更新相机（:1646）。

**运行时分派**：direct call 模式下唯一 closest hit 程序按 `mdl_callable_base_index + slot` 经 SBT 调到具体材质的 5 个 callable；非 direct call 模式直接跳进 MDL 生成代码内的 closest hit，材质差异全在 argument block。

**dxr 场景流**：gltf loader 产出 Scene 描述 → Scene::build_scene 建 Scene_node 树与 Mesh/Instance，材质按描述去重共享 → update_scene_data_infos（每 Instance）把材质声明的 scene data 名映射为顶点通道/per-instance 数据的 Info 数组上传 GPU → 着色器里 MDL 生成的 scene data 访问按 dense Info 表取数。每帧 Scene::update 递归处理动画变换。

## 5. 设计决策

- **两种接入模式并存**（optix7 的教学核心）：非 direct call 把着色器源码交给 SDK 链接（LTO 机会、调用零开销，但每材质一个 hit group）；direct call 反过来（一个 hit group + N×5 callable，模块化但多一跳间接）。同一 closest hit 的两个 .cu 变体文件分别演示。
- **代码字符串级缓存**（optix7_mdl.cpp:1111）：以 target code 全文为 key 去重 OptixProgramGroup，注释明示 material hash 不同≠代码不同——务实省编译。
- **scene data 的 dense map**（scene.cpp:880-882）：ID-as-index 稠密数组替代哈希，GPU 端取 Info 零查找；代价是空间换时间，注释承认假设"名字少且 ID 稠密"。
- **两遍材质加载**（scene.cpp:1315-1318）：先收集去重再创建，共享实例并保证确定性——并行化与确定性的标准折中。
- **能力缺口诚实标注**：optix7 的 TODO（:1175）直说 light profile/BSDF measurement 不支持；dxr 做全（bsdf_measurement.cpp/light_profile.cpp 独立文件）——互补覆盖。
- **API 版本兼容就地处理**：OptiX 7.7 前后 module 创建 API 分叉（:991-1011），#if 包住而非分文件。

## 6. 新人提示

- 先读 README 与 main（optix7_mdl.cpp:2276）跑通示例，再回头读 addMDLMaterial——它是两个模式差异的汇聚点，其余管线代码都是 OptiX 样板。
- 选接入模式的经验法则：材质数量多、需运行时换材质 → direct call；追求极限性能、材质少 → renderer module 链接（对照 :1118-1152 与 :1229-1235）。
- dxr 的 scene data 是 MDL 1.9+ 特性，看 Scene_data::Info 四个 offset/stride 字段（scene.cpp:367-389）就明白 GPU 端如何零拷贝取顶点数据；optix7 的 :1199-1207 是极简版。
- optix7 的 texture_handler 在 .cu 定义、CPU 侧填指针（:1583-1585），加新资源类型要同时动 .h/.cu/主程序三处——TODO 注释就是从这来的。
- dxr 工程只在 Windows 编，Linux 机器读代码即可；optix7 需要真实 GPU。
- Scene_node::update 的局部/全局矩阵分离（:1171-1235）是场景图教科书实现，改动画系统前先理解缓存关系。
- 集成自己引擎时优先参考 dxr 版封装（资源类型覆盖更全）。
