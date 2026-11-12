# 讲透 NVIDIA Dataset_Synthesizer（NDDS）

> NVIDIA Deep Learning Dataset Synthesizer——UE4.22 合成数据生成插件集（NVIDIA 2018 开源，Falling Things 数据集生产工具）。
> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/Dataset_Synthesizer` @ 924b1b56 · CC BY-NC-SA 4.0。

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`：**554 节点 / 862 边 / 12 层 / 14 步 tour** / validator 0 issues 0 warnings（finalize 内置+ua-inline-validate 双验）/ fingerprints 161 源文件 @ 924b1b56（本轮 11 批源码体系；旧轮 1373 文件大图谱含 Doxygen/资产层已被本轮覆盖，勘误清单经源码复核仍有效） |
| 批甄别笔记 | ✅ | 仓内 `.understand-anything/NOTES-DIGEST.md`（7 条） |
| ONBOARDING | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（9307 字符·不计空格 / 43 唯一文件名锚 / 8 节） |
| explain | ✅ 6 篇 | [explain/01](explain/01-DomainRandomizationDNN-域随机化插件.md)·[02](explain/02-NVSceneCapturer-采集与特征提取.md)·[03](explain/03-引擎配置与改名重定向.md)·[04](explain/04-NVDataObject与NVUtilities.md)·[05](explain/05-Doxygen资产层.md)·[06](explain/06-导出管线与运行时HUD.md)（六节结构，行号锚全源码核实，合计 19263 字符不计空格） |

图谱分层速览（本轮 12 层·161 文件全覆盖零重复）：L01 工程入口与配置(13) → L02 插件清单与构建(11) → L03 NVUtilities(12) → L04 NVDataObject 运行时与编辑器(12) → L05 DR 框架核心(19) → L06 DR 材质网格(12) → L07 DR 灯光位姿动画(16) → L08 DR 布局与标记(12) → L09 SC 公共接口(17) → L10 SC 运行时实现(17) → L11 SC 编辑器扩展(4) → L12 SC Game HUD(16)；14 步 tour 从 NDDS.uproject 一路走到 HUD 收官。

## 一图流架构

```
NDDS.uproject（Source/ 工程）
 └─ NDDS 游戏模块（Source/Source/NDDS/，胶水）
     ├─ NVUtilities      导航路径/路点移动（最底层）
     ├─ NVDataObject     对象定义参数化（JSON 双向）＋Editor 工具
     ├─ NVSceneCapturer  采集 Actor → FeatureExtractor(PixelData×4|AnnotationData)
     │                   → FNVImageExporter(同步)/_Thread(异步) ＋ HUD ＋ Editor 定制
     └─ DomainRandomizationDNN  ADRSceneManager 编排
                                 ├─ GroupActorManager×2(正式+噪声) + SpatialLayoutGenerator
                                 ├─ RandomComponent 七件族(材质/参数/灯/旋转/网格/移动/可见性)
                                 └─ FRandomAssetStreamer 流式素材加载
内容：DR 55 + SC 56 uasset(相机/提取器预设) + ArchVis 192 uasset(室内舞台)
文档：Documentation/ClassDetails 895 生成文件(116 类页+50 源页+图源缓存) = 全仓 65%
```

## 勘误与坑清单（钉版，全部源码实证）

1. **类名双 n**：`UNVObjectMaskMananger`（`NVObjectMaskManager.h:68`）——文件名单 n、类名双 n，全仓沿用；README/docs 引用勿"改正"，改了反而编译错。
2. **uplugin 尾逗号**：`Source/Plugins/NVDataObject/NVDataObject.uplugin:27-28`——Modules 数组末对象后带逗号，标准 JSON 非法、UE4 解析器容忍；属上游事实冻结区，勿修。
3. **Vulkan 黑屏注释实证**：`Source/Config/DefaultEngine.ini:13-17`——NVIDIA 注释明言"VULKAN RHI 下 Depth/ClassSegmentation 提取器输出黑屏"，`-TargetedRHIs=SF_VULKAN_SM5` 删 Vulkan、`+TargetedRHIs=GLSL_430` 强制 OpenGL4.3；第二证 `readme.md:28`（Vulkan 采不了深度/类分割）。另 `readme.md:24-26` 记录 4.22 uniform buffer 内存增长已知问题（>10 对象每帧换材质时停 PIE 卡挂）。
4. **三类改名 ActiveClassRedirects**（`DefaultEngine.ini:24-26`）：ObjectSegmentation→**VertexColorMask**（`NVSceneFeatureExtractor_ImageExport.h:148`）、ImageExport→**PixelData**（`:24`）、DataExport→**AnnotationData**（`NVSceneFeatureExtractor_DataExport.h:51`）。旧教程/旧资产的类名是改名前三代，源码零命中须按表换算。
5. **Doxygen 文件名双坑**（`Documentation/ClassDetails/`）：大写字母拆 `_x`（ADRSceneManager→`class_a_d_r_scene_manager`）+ 原名下划线转义 `__`，叠加出 `___` 三连（NVSceneMarker_FocalPoint→`class_a_n_v_scene_marker___focal_point`）；`*_8h_source.html` 的 `8h` 是 `.h` 的点转义。手拼 URL 必先解码。
6. **UCLASS 反射宏手补**：全仓 65 个 UCLASS + 39 USTRUCT + 18 UENUM + 2 UINTERFACE（=124 反射类型声明），tree-sitter 对宏内类声明近乎全盲（NOTES-DIGEST batch-1 钉版）；图谱 120 个 class 节点（U51/F47/A17/I5）全部由宏感知扫描补齐——凡用静态分析器解析 UE4 仓皆遇此坑。
7. **UE4 include 搜索序 Private→Public 失明**：SC 插件 17 个 `Private/*.cpp` 裸 include `#include "NVAnnotatedActor.h"`（`NVAnnotatedActor.cpp:5`）而头文件实际在 `Public/`——UE4 编译时 Private 与 Public 目录都进 include 搜索路径，常规静态解析器只查同目录会全部报"找不到"。
8. **LFS 指针陷阱**：310 个 uasset + 7 个 umap 全走 LFS（`.gitattributes:1-5`），**zip 下载到手是 ASCII 指针文件**（`readme.md:15-17` 警告 "DO NOT DOWNLOAD AS .ZIP"；本机工作区 file 命令实证 BookLP.uasset 为 ASCII text）。
9. **UE4 工程根嵌套**：.uproject 在 `Source/NDDS.uproject`、游戏模块在 `Source/Source/NDDS/`——双层 Source 目录，仓库名义根≠UE4 工程根。
10. **上游自认架构债**：`DomainRandomizationDNN.Build.cs:26` FIXME："This module shouldn't depend on the NVSceneCapturer, we should have a Core module"——DR→SC 的继承耦合（`DRSceneManager.h:20`）至今未偿。
11. **字段名微勘误**：DRSceneManager 噪声编排器字段是 `NoiseActorManager`（`DRSceneManager.h:42-43`），非直觉的 "NoiseManager"；`NDDS.uproject:30-33` SteamVR 被显式禁用（Enabled:false）。
12. **DefaultEditor/DefaultEditorSettings/DefaultGame 三个 ini 近乎空壳**：DefaultGame.ini 仅 ProjectID 一节——真正的配置地雷全在 DefaultEngine.ini，别平均用力。

## 相关产物

- 上游配套：[Dataset_Utilities (NVDU)](https://github.com/NVIDIA/Dataset_Utilities)——标注可视化工具（`readme.md:12` 指引）。
- 深入单点：explain/02（提取器双层抽象与导出双轨）· explain/03（改名三代史）· onboarding 第 3 节（数据集生产全管线）。
- 图谱复核：`python3 -c "import json; g=json.load(open('<repo>/.understand-anything/knowledge-graph.json')); print(len(g['nodes']), len(g['edges']))"`。
