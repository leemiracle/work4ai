# 02 · NVSceneCapturer：采集 Actor、特征提取器与导出双轨

## 角色定位

四插件中的"采集引擎"：把 UE4 场景一帧一帧变成数据集——RGB/深度/光流/遮罩图像 + JSON 标注。三模块分工（`NVSceneCapturer.uplugin`）：NVSceneCapturer 运行时核心（35 文件）、NVSceneCapturerGame 运行时 HUD、NVSceneCapturerEditor 编辑器定制。readme 宣称的能力清单（images/segmentation/depth/pose/bbox/keypoints/stencils，`readme.md:6`）全部落在这一个插件。

## 内部结构

- **采集主 Actor**：`ANVSceneCapturerActor : public AActor`（`NVSceneCapturerActor.h:122`），UCLASS 带 `Config=Engine`（`:119`，属性可被 ini 覆盖）。生命周期事件三连 DECLARE_DYNAMIC_MULTICAST_DELEGATE（`:111-113`：Started/Stopped/Completed），蓝图可绑（属性 `:199-204`）；四控制 StartCapturing/StopCapturing/PauseCapturing/ResumeCapturing（`:141-147`）。关键配置：`FeatureExtractorSettings` 数组（`:236-237`）决定本采集器启用哪些特征、`bAutoStartCapturing`+`TimeBetweenSceneCapture`（`:245-250`）决定采集节拍、`MaxNumberOfFramesToCapture`（`:254-255`，0=无限）、Instanced 的 `SceneDataHandler/SceneDataVisualizer`（`:262-267`）决定数据去向。
- **特征提取器抽象**：`UNVSceneFeatureExtractor : public UObject`（`NVSceneFeatureExtractor.h:35`，Abstract），`UpdateCapturerSettings/UpdateSettings` 为 PURE_VIRTUAL（`:52-54`），公共属性 bIsEnabled/DisplayName/Description/ExportFileNamePostfix（`:59-69`）——文件名后缀（如 "depth"/"mask"）从这里来。两大分支：
  - **PixelData 像素族**（`NVSceneFeatureExtractor_ImageExport.h:24`）：`CreateSceneCaptureComponent2d`（`:42`）建取景组件，`CaptureSceneToPixelsData` 回调（`:34,36`）回传 `FNVTexturePixelData`。四派生：SceneDepth（`:104`，`MaxDepthDistance:117` 量化上限，实现里默认 3000cm 且 `SetScalarParameterValue` 写入后处理材质，`NVSceneFeatureExtractor_ImageExport.cpp:221-232`）、ScenePixelVelocity（`:121`）、StencilMask（`:134`）、VertexColorMask（`:148`）。渲染细节全开放：OverrideShowFlagSettings（`NVSceneFeatureExtractor_ImageExport.h:63-64`）、PostProcessMaterial（`:69-70`）、独立图像格式覆盖（`bOverrideExportImageType+ENVImageFormat :73-77`）。
  - **AnnotationData 标注族**（`NVSceneFeatureExtractor_DataExport.h:51`）：`CaptureSceneAnnotationData` 吐 `TSharedPtr<FJsonObject>`（`:64-67`）。工程含量最高的一层：视锥剔除 IsActorInViewFrustum（`:77`）、3D→2D 投影 ProjectWorldPositionToImagePosition（`:79`）、三种 2D 框算法（`:81-85`，含 mesh 复杂碰撞逐顶点法）、像素/比例坐标双口径（`bExportImageCoordinateInPixel :46`）。
- **实例遮罩**：`UNVObjectMaskMananger`（`NVObjectMaskManager.h:68`，类名双 n 勘误）ScanActors 分配 ID；命名来源四选（实例名/网格名/Tag/类名，`:13-37`）；ID 策略 Sequential/SpreadEvenly（`:49-62`）——注释明言 SpreadEvenly 只为肉眼可辨，训练该用 Sequential。

## 外部连接

被 DomainRandomizationDNN 继承（ADRSceneManager→ANVSceneManager）；被 NDDS 游戏模块私有依赖（`NDDS.Build.cs`）。相机预设资产（Content/Capturers 下 IntelRealSense/Zed）喂给 `UNVSceneCapturerViewpointComponent`（`NVSceneCapturerViewpointComponent.h:64`）；`NVSceneCaptureComponent2D.cpp` 的 BuildProjectionMatrix 函数节点把真实相机内参写成 UE4 投影矩阵——sim2real 相机一致性关键。

## 数据流

Tick→CheckCaptureScene→各提取器 `CaptureSceneToPixelsData`：PixelData 族先 `UpdateMaterial`（`NVSceneFeatureExtractor_ImageExport.cpp:138`）更新后处理材质参数→SceneCapture 渲染到 RenderTarget→`FNVTextureRenderTargetReader`（`NVTextureReader.h`，R8/R16/R32f/BGRA 回读）取像素→交付导出。AnnotationData 族走 GatherActorData（`NVSceneFeatureExtractor_DataExport.h:75`）→投影/裁剪/算框→JSON 序列化。

## 设计决策

1. **提取器=UObject 插件而非硬编码**：每个特征是 Instanced 子对象，采集器数组自由组合——L06 层 `SceneCapturer_AllFeatureExtractors.uasset` 一键全装即是此设计的资产化展示。
2. **导出双轨**：`FNVImageExporter`（`NVImageExporter.h:36`）静态同步压缩（PNG 恒 Z_BEST_SPEED，`:42-46`）；`FNVImageExporter_Thread : FRunnable`（`:68-69`）`TQueue<FNVImageExporterData>`（`:89`）+ FEvent 唤醒（`:93`）异步落盘——渲染帧率与 PNG 编码解耦。
3. **图像格式受 ini 约束**：Vulkan RHI 下深度/类分割黑屏，DefaultEngine.ini 强制 GLSL_430（详见 03 篇）。

## 新人提示

- `NVObjectMaskManager.h` 文件名单 n、类名 `Mananger` 双 n（`:68`）——代码引用勿改正拼写。
- 加新图像特征：继承 `UNVSceneFeatureExtractor_PixelData` 覆写 `UpdateMaterial`（参考 SceneDepth，`NVSceneFeatureExtractor_ImageExport.h:103-118` 全套搞定）。
- 遮罩 ID 想肉眼检查用 SpreadEvenly，跑训练换回 Sequential（`NVObjectMaskManager.h:39-48` 注释原话）。
