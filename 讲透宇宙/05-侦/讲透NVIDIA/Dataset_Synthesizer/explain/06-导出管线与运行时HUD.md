# 06 · 数据落地：SceneDataHandler 导出管线与运行时 HUD

## 角色定位

合成数据的"最后一公里"：采集 Actor 产出的像素流与标注 JSON 如何变成磁盘上的数据集文件，以及采集过程中人如何在 PIE 里监控和控制。两条线分别落在 `UNVSceneDataHandler` 策略族（`NVSceneDataHandler.h:19`）与 NVSceneCapturerGame 模块的 GameMode/PlayerController/HUD 三件套上。任务书原设想的 "NVRecorder" 实体在仓内不存在——录音/录制器角色由本篇的导出线程+HUD 记录面板共同承担（甄别结论）。

## 内部结构

- **策略双轨基类**：`UNVSceneDataHandler : public UObject`（`NVSceneDataHandler.h:19`，Abstract），三个 PURE_VIRTUAL 数据入口 `HandleScenePixelsData`/`HandleSceneAnnotationData`（`:37-50`）+ 背压查询 `CanHandleMoreData`（`:28`）+ 三个生命周期钩子（`:52-54`）。采集器以 Instanced UPROPERTY 持有（`NVSceneCapturerActor.h:262-267`），导出器与可视化器可同时挂载。
- **UNVSceneDataExporter 落盘实现**（`NVSceneDataHandler.h:77`，实现 `NVSceneDataHandler.cpp`）：默认输出根目录 `NVCapturedData/`（`NVSceneDataHandler.cpp:26`）；**目录冲突默认策略是 CleanDirectory——直接递归删除旧目录**（`:32` 构造默认值，`:97-113` 的 switch：Clean 删目录 / TimestampPostfix 新建带时间戳目录 / Overwrite 覆盖写）；图像与 JSON 分别经 `HandleScenePixelsData→GetExportFilePath`（`:50-62`）与 `HandleSceneAnnotationData`（`:64-76`）落盘；导出启动时先 `ExportCapturerSettings`（`:123`）把相机内参、导出对象 cuboid、投影矩阵写成 `_settings.json`（结构见 `NVSceneCapturerActor.h:60-106` 四个 ExportData USTRUCT）；采集完成后 `bAutoOpenExportedDirectory` 可自动打开目录（`:305-308`）。
- **异步导出线程**：`FNVImageExporter_Thread : public FRunnable`（`NVImageExporter.h:68`），`TQueue<FNVImageExporterData>` 无锁队列（`:89`）+ `FEvent` 唤醒（`:93`）；背压两道闸——Exporter 侧 `MaxSaveImageAsyncCount` 默认 100、队列过半即停收（`NVSceneDataHandler.cpp:36,42`），采集器侧 `CanHandleMoreData` 返回 false 时暂停喂帧（`NVSceneCapturerActor.cpp` 的 CheckCaptureScene 消费）。
- **UNVSceneDataVisualizer 回显**（`NVSceneDataHandler.h:185`）：把捕捉数据写回 `TMap<FString, UTextureRenderTarget2D>`（`:224`），供 PIP 画中画面板实时预览。
- **Game 模块三件套**：`ANVSceneCapturerGameModeBase`（`NVSceneCapturerGameModeBase.cpp:14`）BeginPlay 时若关卡缺 SceneManager 会自动 Spawn 默认 `ANVSceneManager`（`:23-40`，Warning 日志 `:30`），再迭代收集全部采集 Actor 入 `SceneExporterList`（`:43-48`）；`ANVSceneCapturerPlayerController`（`NVSceneCapturerPlayerController.cpp:26`）绑定按键动作 `ToggleTakeOverViewport`（`:43`，触发 `:67-77`）与鼠标光标开关（`:91-93`）；`ANVSceneCapturerHUD`（`NVSceneCapturerHUD.cpp:88`）DrawHUD 驱动 Overlay 刷新+调试绘制，`DrawDebugInfo` 遍历关卡 actor 画导出调试信息与采集路径（`:124-176`，内含上游 FIXME：应让各训练 actor 自行请求 debug canvas）。
- **三个 UUserWidget**：`HUD_ExporterControlPanel`（启动/停止/暂停/接管视口四键，`NVSceneCapturerHUD_ExporterControlPanel.cpp:217-260`，FPS 读数 `:134`）、`HUD_PIPPanel` 画中画预览、`HUD_Overlay` 叠加层。

## 外部连接

Handler 策略挂在 `ANVSceneCapturerActor` 上（Instanced），像素来源是 PixelData 族提取器渲染出的 RenderTarget 经 `FNVTextureRenderTargetReader` 回读（`NVTextureReader.h`）；JSON 序列化用引擎 `FJsonObjectConverter`（`NVSceneCapturerUtils.cpp` 大量使用）；HUD 依赖 GameMode 的 `GetSceneCapturerList()`；可视化器纹理供 PIP 面板消费。DefaultEngine.ini 的 EditorStartupMap 指向 `/Game/Map/TestCapturer`（`DefaultEngine.ini` GameMapsSettings 段）——这套 HUD 就是那张测试图的运行时配套。

## 数据流

一帧完成提取后：`CaptureSceneToPixelsData` → 各特征提取器产出 `FNVTexturePixelData`/`TSharedPtr<FJsonObject>` → 采集器按 Instanced 逐个调 `HandleScenePixelsData`/`HandleSceneAnnotationData` → Exporter 生成带 FeatureExtractor 后缀与 Viewpoint 前缀的文件路径（`GetExportFilePath`，`NVSceneDataHandler.cpp:373`）→ 像素入 `FNVImageExporter_Thread` 队列异步 PNG 编码（PNG 恒 Z_BEST_SPEED，`NVImageExporter.h:42-46`），JSON 直接同步写盘 → 队列水位过半则 `CanHandleMoreData`=false → 采集器 `bPauseGameLogicWhenFlushing`（`NVSceneCapturerActor.h:271`）决定是否暂停游戏逻辑冲刷。控制流反向：HUD 按钮/快捷键 → PlayerController InputAction → CapturerActor 的 Start/Stop/Pause API → 状态事件 `OnStartedEvent/OnStoppedEvent/OnCompletedEvent` 回弹 UI。

## 设计决策

1. **策略模式而非硬编码 sink**：Exporter 与 Visualizer 都是 Instanced UObject，可同挂、可换序——零代码切换"只预览不落盘/只落盘/边落边看"。
2. **PNG 编码移出渲染线程**：FRunnable+TQueue+FEvent 三件套把压缩 IO 与渲染解耦；背压用"过半停收"而非满仓拒绝，给突发帧留缓冲。
3. **目录冲突默认 CleanDirectory 是把双刃剑**：自动化重跑友好（目录永远干净），但误指到有数据的目录会整目录删除——`NVSceneDataHandler.cpp:99-101` 的 `DeleteDirectoryRecursively` 无确认无回收站。
4. **GameMode 自动补 SceneManager**：保证"打开地图直接 PIE 就能采"的零配置体验，代价是静默 Spawn 可能掩盖关卡配置错误（仅 Warning 日志）。

## 新人提示

- 首跑前务必检查 `RootCapturedDirectoryPath`：默认策略会清空目标目录（`NVSceneDataHandler.cpp:32,99-101`）。
- 导出文件名 = Viewpoint 名 + FeatureExtractor 的 `ExportFileNamePostfix` + 帧号（`NVSceneFeatureExtractor.h:69`）——自定义新提取器时这个后缀就是文件名的区分位。
- `MaxSaveImageAsyncCount` 写 0 表示不限（`:36,42` 的短路条件），机械盘上不限流可能 IO 打满拖垮 PIE。
- HUD 面板按钮直接映射 CapturerActor 的四控制 API（`NVSceneCapturerHUD_ExporterControlPanel.cpp:217-260`），排查采集问题先看 HUD 的 FPS/剩余帧数再翻 LogNVSceneDataHandler 日志类（`NVSceneDataHandler.h:13`）。
