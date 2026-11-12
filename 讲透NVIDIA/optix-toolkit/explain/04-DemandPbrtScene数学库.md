# 04 · DemandPbrtScene 与 FourierBsdf：旗舰示例里的解析栈与数学库

## 角色定位

DemandPbrtScene（`examples/DemandLoading/DemandPbrtScene/`，190 文件，源码平铺无 src/ 子目录）是全仓最大示例：把 DemandLoading/Memory/ShaderUtil/按需几何/MDL 全家组装成 pbrt-v3 场景按需加载查看器。它自带两个"数学资产"——FourierBsdfTable（pbrt 截断 Fourier BSDF 二进制表解析）与 ray_cone（ShaderUtil 光线锥库）——是示例层少见的算法密度高地。输入侧的 pbrtApi/PbrtSceneLoader 独立成栈，可脱离示例复用。

## 内部结构

**场景总装** `examples/DemandLoading/DemandPbrtScene/PbrtScene.cpp`（373 行）：解析编排、无限光源处理、顶层 traversable 组装、launch 参数同步。**渲染器** `examples/DemandLoading/DemandPbrtScene/OptixRenderer.cpp`（458 行）：PipelineState 构造（`OptixRenderer.cpp:93`）/析构（`OptixRenderer.cpp:107`）/recordLaunchCompleteEvent（`OptixRenderer.cpp:115`）——双缓冲热切换+SBT 六类记录。**几何缓存** `examples/DemandLoading/DemandPbrtScene/GeometryCache.cpp`（509 行）：getShape（`GeometryCache.cpp:117`，`GeometryCache.cpp:119` PLY 分支）、getObject（`GeometryCache.cpp:131`，`GeometryCache.cpp:161` 二级 PLY 处理）——PLY/网格/球解析缓存与 GAS 构建。**FourierBsdfTable** `examples/DemandLoading/DemandPbrtScene/FourierBsdfTable.cpp`（360 行）：字节层 readBytes（`FourierBsdfTable.cpp:55`）、向量层 readInt32Vector（`FourierBsdfTable.cpp:65`）/readFloatVector（`FourierBsdfTable.cpp:90`）、标量 readInt32（`FourierBsdfTable.cpp:115`），节读取错误带上下文串（`FourierBsdfTable.cpp:40` 起 "Truncated Fourier BSDF table"）；配套 FourierBsdfTableResource.cpp 资源生命周期分离。**参数总线** `examples/DemandLoading/DemandPbrtScene/include/DemandPbrtScene/Params.h`（734 行示例最大头）：Params/RayPayload/PhongMaterial/MaterialState/光源/相机全部 device POD。**MDL 材质线**十件套：MdlSdkSession/MdlBsdfCompiler/MdlShaderCache/MdlTextureGraphGenerator——NVIDIA MDL SDK 集成。辅助：SceneProxy/ProxyFactory（两级加载代理侧）、DemandTextureCache（四类纹理缓存）、`Dependencies.h`（20+ 协作类型前置声明中枢）、`Options.h`（52 行渲染开关）。

**输入栈**（独立可复用）：`examples/pbrtApi/PbrtApi.cpp`（302 行）是 C 风格入口——单例 `examples/pbrtApi/PbrtApi.cpp:16`（`static ::otk::pbrt::Api* g_api{}`），`PbrtApi.cpp:37`（pbrtObjectBegin）、`PbrtApi.cpp:47`（pbrtShape）自由函数族逐条转发；`examples/PbrtSceneLoader/include/OptiXToolkit/PbrtSceneLoader/SceneDescription.h`（194 行）定义场景 IR（19 个 POD：相机/胶片/光源/材质图/形状/实例），SceneLoader 接口+PbrtApiImpl+PLY reader 完成解析。

## 外部连接

向上消费 OptiX 7 API（管线/模块/SBT）；横向依赖 DemandLoader（纹理/几何/材质三线，`DemandLoading/DemandLoading/include/OptiXToolkit/DemandLoading/DemandLoader.h:33` 接口）、Memory（缓冲）、`ShaderUtil/include/OptiXToolkit/ShaderUtil/ray_cone.h`（218 行：三相机初始化/传播/反射/折射/曲率/纹理梯度推导——pbrt 论文方法的落地实现）、Gui/ImGuiUserInterface/Statistics；数据侧经 pbrtApi 栈读 .pbrt/.ply/.bsdf/.exr；MDL 线外接 MDL SDK（`CMake/FetchMdl.cmake` 拉取）。

## 数据流

一帧：pbrtApi 逐语句解析（`examples/pbrtApi/PbrtApi.cpp:37`/`:47` 函数族）→ 填 SceneDescription IR → PbrtScene.cpp 组装：GeometryCache 解析形状建代理 GAS（`GeometryCache.cpp:117`），DemandTextureCache 挂按需纹理，FourierBsdfTable 加载 .bsdf 表入显存 → OptixRenderer 构建管线（双缓冲当前代，`OptixRenderer.cpp:93`）→ 渲染循环：ray 经 ray_cone 传播积累锥宽 → 纹理 LOD 由锥宽决定（配合 DemandLoading 缺页拉取恰好的 mip）→ FourierBsdf 查表（先取 theta 分段系数再做截断 Fourier 求值）→ 命中 MDL 材质走 ShaderCache 缓存的 PTX → Statistics 面板回显 residency。热切换：材质参数变更 → 新管线后台编译 → 双缓冲原子切换。

## 设计决策

①**解析栈独立成库**（pbrtApi/PbrtSceneLoader 不在示例目录内）——场景 IR（SceneDescription.h）是稳定边界，换渲染器可复用；②**单例+自由函数的 C 风格 API**（`PbrtApi.cpp:16`）——对齐 pbrt 官方 API 形状，既有 .pbrt 处理代码零改接入；③**FourierBsdf 资源/表分离**（FourierBsdfTable.cpp 与 FourierBsdfTableResource.cpp）——解析纯 CPU、上传与生命周期独立，tests/ 有 FourierBsdfTableWriter 配套往返验证；④**双缓冲热切换**——编辑材质不中断渲染，示例即演示即工具。

## 新人提示

跑通前先备数据（示例 ReadMe 讲 pbrt 场景获取）；构建注意 `CMake/FetchMdl.cmake`/`CMake/FetchOptiX.cmake` 网络拉取。读码顺序：`PbrtApi.cpp:16` 单例 → `SceneDescription.h` IR → PbrtScene.cpp 总装 → `OptixRenderer.cpp:93` SBT。FourierBsdf 解析 bug 用 tests/include 的 FourierBsdfTableWriter 造已知表往返断言（对照 `FourierBsdfTable.cpp:55` 的字节层）。ray_cone 调参（锥宽初始化）对照 docs/README——纹理 LOD 过冲/欠冲先查这里。`Params.h`（734 行）是 device/host 契约总账，改结构体必须双端同步重编。
