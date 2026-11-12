# Dataset_Synthesizer（NDDS）Onboarding

> 图谱基线：1513 节点 / 1089 边 / 10 层 / 16 步 tour / validator 0 issues / fingerprints 1373 文件 @ 924b1b56。
> 本文所有行号锚均从源码逐条核实（2026-11-07），仓内路径以 `Source/` 为 UE4 工程根。

## 1. 项目定位：NDDS 是什么

**NDDS = NVIDIA Deep Learning Dataset Synthesizer**，NVIDIA 2018 年开源的 UE4 合成数据生成插件集：在 Unreal 虚幻引擎里搭好场景，批量导出**带完美真值标注的图像**——RGB、深度、实例/类分割、光流、3D 包围盒、位姿、keypoints，一次采集全都有（`readme.md:6`）。它解决的是 CV 训练数据"人工标注贵、专家标注（如 3D 框顶点）不可能规模化"的痛点（`readme.md:31-33`）：仿真器里的真值是渲染管线原生算出来的，零标注成本。

配套学术产出是 **Falling Things 数据集**（`readme.md:45`，Tremblay et al., CVPR Workshop 2018），readme 引用的两篇论文（`readme.md:41-45`）论证了"高度随机化的合成数据可训练真实世界 CV 系统"的域迁移可行性——这正是本项目域随机化子系统的动机。

一句架构话：**NVSceneCapturer 负责"采"，DomainRandomizationDNN 负责"随机"，NVDataObject 负责"把采集对象参数化成数据资产"，NVUtilities 提供导航等杂项支撑，NDDS 游戏模块把它们粘成一个 UE4 工程**。

新人第一课：这个仓**必须 git lfs clone，绝不能 zip 下载**（`readme.md:15-17`）——`.gitattributes:1-5` 把 `*.uasset/*.umap/*.fbx/*.stl/*.obj` 全部指入 LFS，共 310 个 uasset + 7 个 umap；zip 下载到手的全是 ASCII 指针文件（本仓工作区即指针态，`file Source/Content/ArchVis/Mesh/BookLP.uasset` 实证）。

## 2. 仓库形态：嵌套的 UE4 工程与四插件八模块

仓库名义根≠UE4 工程根：`.uproject` 在 `Source/NDDS.uproject`，于是游戏模块按 UE4 规范落在 `Source/Source/NDDS/`——**双层 Source 目录**是浏览时的第一视觉陷阱。

- `Source/NDDS.uproject:3` 锁定 EngineAssociation 4.22；`:8-11` 声明 NDDS 运行时模块（`LoadingPhase: PostConfigInit` 早加载）；`:13-34` 启用四插件并把 **SteamVR 显式禁用**（`:30-33`）。
- 构建目标：`Source/Source/NDDS.Target.cs`（TargetType.Game）与 `NDDSEditor.Target.cs`（Editor）双目标。
- 胶水层：`Source/Source/NDDS/NDDS.Build.cs` 以 PrivateDependencyModuleNames 拉起 NVSceneCapturer/NVSceneCapturerGame/DomainRandomizationDNN 三插件模块；`NDDS.cpp:10-11` 是 `IMPLEMENT_PRIMARY_GAME_MODULE` + `DEFINE_LOG_CATEGORY(NDDSLog)` 入口。
- 四插件八模块清单（uplugin 各一）：
  - **DomainRandomizationDNN**（`Source/Plugins/DomainRandomizationDNN/DomainRandomizationDNN.uplugin`）：单 Runtime 模块 61 文件，`EnabledByDefault:true`，且插件级再依赖 NVDataObject+NVSceneCapturer（uplugin `Plugins` 节）。
  - **NVSceneCapturer**（`Source/Plugins/NVSceneCapturer/NVSceneCapturer.uplugin`）：三模块——NVSceneCapturer（Runtime 35 文件）+ NVSceneCapturerGame（Runtime，HUD/UI）+ NVSceneCapturerEditor（Editor，细节面板定制）。
  - **NVDataObject**（`Source/Plugins/NVDataObject/NVDataObject.uplugin`）：双模块——NVDataObject（Runtime）+ NVDataObjectEditor（Editor，`PostEngineInit` 加载）。
  - **NVUtilities**（`Source/Plugins/NVUtilities/NVUtilities.uplugin`）：单模块最小插件。

依赖方向有一处上游自认的架构债：`DomainRandomizationDNN.Build.cs:26` FIXME 注释明言"本模块不该依赖 NVSceneCapturer，应抽一个共享 Core 模块"——DRSceneManager 继承 `ANVSceneManager`（`DRSceneManager.h:20`）正是这条边。

## 3. 核心管线：从随机化场景到落盘数据集

数据流一条线讲透：

1. **场景管理**：`ANVSceneManager`（`NVSceneManager.h:50`，虚函数 `UpdateSettingsFromCommandLine`/`SetupSceneInternal` 在 `:85-86`）编排全场；DR 侧 `ADRSceneManager` 继承它（`DRSceneManager.h:20`），持有 `GroupActorManager` 与 `NoiseActorManager` 两个编排器引用（`:39-43`），命令行覆盖逻辑在 `DRSceneManager.cpp:30-74`。
2. **对象生成**：`AGroupActorManager`（`GroupActorManager.h:36`）按 `FNVActorTemplateConfig`（`:16`）模板批量生成 Actor（`CreateActorFromTemplate`，`:55`）；空间布局由 `USpatialLayoutGenerator`（`SpatialLayoutGenerator.h:14`）的 Circle/Grid2d 两种生成器决定。
3. **维度随机化**：挂在 Actor 上的 `URandomComponentBase` 族（`RandomComponentBase.h:15`）按 `RandomizationDurationInterval`（`:54-55`，带 `EditCondition=bShouldRandomize`）周期触发 `OnRandomization` 蓝图事件（`:33-35`）。
4. **采集**：`ANVSceneCapturerActor`（`NVSceneCapturerActor.h:122`）驱动 `UNVSceneFeatureExtractor` 抽象（`NVSceneFeatureExtractor.h:35`）的两个分支——PixelData 像素族与 AnnotationData 标注族。
5. **落盘**：像素走 `FNVImageExporter`（同步）或 `FNVImageExporter_Thread`（异步队列，`NVImageExporter.h:68-69`）；标注走 JSON 序列化逐帧写出。

采集 Actor 的事件三连 `DECLARE_DYNAMIC_MULTICAST_DELEGATE`（`NVSceneCapturerActor.h:111-113`，OnStarted/OnStopped/OnCompleted 挂在 `:199-204`）是蓝图联动入口；`StartCapturing/StopCapturing/PauseCapturing/ResumeCapturing` 四控制见 `:141-147`。

## 4. 域随机化子系统（DomainRandomizationDNN）

**采样数据层**（`DRUtils.h`）：FRandomRotationData（`:14`，锥体内/Pitch/Roll/Yaw 四模式）、FRandomLocationData（`:64`，三轴区间）、FRandomScale3DData（`:111`，Uniform 或逐轴、最小 0.001）、FRandomColorData（`:174`，ERandomColorType 三策略：全随机/双色插值/绕基色扰动，`HSV` 可选，`:165-172`）、FRandomMaterialSelection（`:241`，按索引/按槽位名/全部三选，`:225-238`）。每个 USTRUCT 都用 `PinHiddenByDefault + InlineEditConditionToggle + EditCondition` 三件套做编辑器条件显示——这是全仓 UI 元编程范式（NOTES-DIGEST batch-1 钉版）。

**组件七件族**（全在 `Source/Plugins/DomainRandomizationDNN/Source/DomainRandomizationDNN/Public/Components/`）：RandomMaterial（整材质替换，`:20`，目录扫描或清单两种素材源 `:50-55`，素材由 `FRandomAssetStreamer` 流式加载 `RandomMaterialComponent.h:66`）、RandomMaterialParam_Color/Scalar/Texture（只随机参数不动材质，基类 `RandomMaterialParameterComponentBase.h:20`）、RandomLight（强度区间+颜色，`RandomLightComponent.h:32-38`）、RandomRotation、RandomMesh、RandomMovement/Scale/Visibility/LookAt/Animation、SpotLight 变体。素材流式加载核心 `FRandomAssetStreamer`（`DRUtils.h:299`）用 `FStreamableManager`（`:378`）异步分批加载，循环队列管理已加载/加载中两组 `FSoftObjectPath`——**随机材质库可以远大于内存**。

**数据对象层**：`URandomDataObject`（`RandomDataObject.h:14`，Abstract）派生 Movement（`:30`，bRelatedToOriginLocation 决定绕原点或体素内采样，`:42-54`）与 Rotation（`:66`）两数据对象。

## 5. 场景采集子系统（NVSceneCapturer）

**特征提取器双层抽象**：基类 `UNVSceneFeatureExtractor`（`NVSceneFeatureExtractor.h:35`，Abstract，`UpdateCapturerSettings/UpdateSettings` 是 `PURE_VIRTUAL`，`:52-54`；公共属性 bIsEnabled/DisplayName/ExportFileNamePostfix 在 `:59-69`）。两大分支：

- **PixelData 族**（`NVSceneFeatureExtractor_ImageExport.h:24`）：持 `SceneCaptureComponent2D` + 渲染目标，流程=更新后处理材质→渲染→`FNVTextureRenderTargetReader`（`NVTextureReader.h`，R8/R16/R32f/BGRA 格式回读）取回像素。四个派生：SceneDepth（`:104`，MaxDepthDistance 量化上限 `:117`，默认 3000cm、cpp 实现里把参数写进后处理材质 `NVSceneFeatureExtractor_ImageExport.cpp:221-232`）、ScenePixelVelocity（`:121`）、StencilMask（`:134`，实例遮罩）、VertexColorMask（`:148`）。
- **AnnotationData**（`NVSceneFeatureExtractor_DataExport.h:51`）：`CaptureSceneAnnotationData` 回调吐 `TSharedPtr<FJsonObject>`（`:64-67`）；视锥剔除（`IsActorInViewFrustum:77`）、2D 框三算法（`GetBoundingBox2D/Calculate2dAABB/Calculate2dAABB_MeshComplexCollision:81-85`）、坐标像素/比例两种口径（`bExportImageCoordinateInPixel:46`）。

**图像导出双轨**：`FNVImageExporter`（`NVImageExporter.h:36`）静态 `CompressImagePNG/CompressImage/ExportImage`（`:46-62`，PNG 无损恒 Z_BEST_SPEED）；`FNVImageExporter_Thread : FRunnable`（`:68-69`）用 `TQueue<FNVImageExporterData>`（`:89`）+ `FEvent` 唤醒（`:93`）做生产者-消费者异步落盘——采集不因 PNG 编码卡帧。

**实例遮罩**：`UNVObjectMaskMananger`（`NVObjectMaskManager.h:68`，**双 n 拼写**）扫描场景 Actor 分配遮罩 ID；命名来源四选（实例名/网格名/Tag/类名，`:13-37`）；ID 分配 Sequential/SpreadEvenly 两策略（`:49-62`，注释明言 SpreadEvenly 纯为肉眼可辨，训练用 Sequential）。

**运行时 UI**：NVSceneCapturerGame 模块 HUD 四件套——`ANVSceneCapturerHUD`（`NVSceneCapturerHUD.h:22`，`DrawHUD:45`）编排 Overlay/PIPPanel/ExporterControlPanel。

## 6. 数据对象与资产参数化（NVDataObject + NVUtilities + 内容层）

`UNVDataObjectAsset`（`NVDataObject.h:18`，`IsAsset() const { return true; }` 在 `:32-35`）是数据资产壳，内持 `UNVDataObject` 引用（`:40-41`）；四个静态方法 `SerializeToJsonFile/DeserializeFromJsonFile/DeserializeFromJsonString/CreateObjectFromDefinitionData`（`:25-28`）构成 JSON 双向序列化。编辑器侧：`FAssetTypeAction_NVDataObject` 提供右键菜单（`AssetTypeAction_NVDataObject.cpp:18`，含"打开源文件"动作 `:37-38,115`）；`FNVDataObjectEditorToolkit : FAssetEditorToolkit`（`NVDataObjectEditorToolkit.h:16`）定制属性编辑器。

NVUtilities 提供 `ANVNavigationPath`（`NVNavigationPath.h:29`，`WaypointList:41`）与 Movement 组件族（`Movement/NVMovementComponentBase.h`、`NVMovementComponent_Waypoint.h`、`NVWaypoint.h`）——采集对象的路径移动基础设施。

内容资产两大块：DR 插件自带 55 个 uasset（背景材质族 Backgrounds 13、Grid 6、MaterialFunctions 6 + DR_SceneManager_BP 等蓝图）；SC 插件 56 个（IntelRealSense/Zed 相机预设、`SceneCapturer_AllFeatureExtractors` 全装配演示、FE_Depth_cm_16bits/FE_ClassSegmentation 等提取器预设）。项目 Content 主体是 **ArchVis 建筑可视化库 192 个 uasset**（材质+家具网格）——Falling Things 室内场景的真实感舞台。

## 7. 引擎配置与 Doxygen 资产层

`Source/Config/DefaultEngine.ini` 是全仓勘误密度最高的文件：`13-17` 行 NVIDIA 注释明确 **Vulkan RHI 下深度/类分割提取器输出黑屏**，用 `-TargetedRHIs=SF_VULKAN_SM5` 移除 Vulkan、`+TargetedRHIs=GLSL_430` 强制 OpenGL 4.3（+/- 前缀是 UE4 ini 数组项增删语法，NOTES-DIGEST batch-24）；readme `:28` 侧证"Vulkan doesn't capture depth and class segmentation"。`24-26` 行三条 `ActiveClassRedirects` 记录类名三代变迁（详见勘误节）。`20-21` 行启动/默认地图指向 `/Game/Map/TestCapturer`。

**Doxygen 生成物占全仓文件数 65%**（895/1373）：`Documentation/ClassDetails/` 可读层 332 文件（328 html+4 css）——116 个 class_* 类详情页 + 50 个 `*_source.html` 带行号源码浏览页 + index/annotated 索引（Doxygen 1.8.8 生成，`index.html` meta 实证）；支持层 563 文件（202 dot=graphviz 类图源 + 202 md5=渲染缓存指纹 + 159 js=类列表数据与 search/ 全文索引分片）。文件名转义规则见勘误第 5 条。

## 8. 新人上手与勘误清单

**上手路径**（建议顺序）：①`readme.md` → ②`Source/NDDS.uproject` 看插件拓扑 → ③`DefaultEngine.ini` 看渲染约束 → ④ tour T07→T08→T09 走采集主线（NVSceneCapturerActor→FeatureExtractor→ImageExporter）→ ⑤ tour T04→T05 走随机化线 → ⑥开 `Documentation/ClassDetails/index.html` 查类 API → ⑦用 `Content/Map/TestCapturer.umap` 起编辑器实操。

**勘误与坑（钉版）**：

1. **类名双 n**：`UNVObjectMaskMananger`（`NVObjectMaskManager.h:68`）——文件名 MaskManager 单 n、类名 Mananger 双 n，全仓沿用，引用时勿"改正"。
2. **uplugin 尾逗号**：`NVDataObject.uplugin:27-28`，Modules 数组末对象后带逗号——标准 JSON 非法，UE4 解析器容忍。
3. **Vulkan 黑屏双证**：`DefaultEngine.ini:13-17` + `readme.md:28`；另 readme `:24-26` 记录 4.22 uniform buffer 内存增长已知问题（材质随机化>10 对象时停止 PIE 卡挂，建议重启编辑器）。
4. **三类改名重定向**（`DefaultEngine.ini:24-26`）：ObjectSegmentation→VertexColorMask、ImageExport→PixelData、DataExport→AnnotationData——旧 uasset/蓝图反序列化兼容；**看旧教程/旧资产时报的类名是改名前三代**。
5. **Doxygen 文件名双坑**：大写字母拆成 `_x`（ADRSceneManager→`class_a_d_r_scene_manager`），原文件名内下划线转义成 `__`，两者叠加产生 `___` 三连（NVSceneMarker_FocalPoint→`class_a_n_v_scene_marker___focal_point`）。手工拼 URL 时最易错。
6. **反射宏盲区**：全仓 65 个 UCLASS + 39 个 USTRUCT + 18 个 UENUM + 2 个 UINTERFACE 声明，tree-sitter 对宏内类声明近乎全盲（NOTES-DIGEST batch-1）；图谱 120 个 class 节点（U51/F47/A17/I5）由宏感知扫描补齐。
7. **include 搜索序**：Private/*.cpp 裸 include Public 头（如 `NVAnnotatedActor.cpp:5` 的 `#include "NVAnnotatedActor.h"` 实际落在 Public/），17 个 cpp 全此模式——静态分析器按常规路径解析会全报告失明。
8. **UE4 工程根嵌套**：.uproject 在 `Source/`、游戏模块在 `Source/Source/NDDS/`，双层 Source 勿混淆。
9. **上游架构债**：`DomainRandomizationDNN.Build.cs:26` FIXME 自认 DR 不应依赖 SC。
10. **DRSceneManager 字段名**：噪声编排器字段是 `NoiseActorManager`（`DRSceneManager.h:42-43`），非想当然的 "NoiseManager"。

（完）图谱与本文锚点均可回仓内 `.understand-anything/knowledge-graph.json` 复核。
