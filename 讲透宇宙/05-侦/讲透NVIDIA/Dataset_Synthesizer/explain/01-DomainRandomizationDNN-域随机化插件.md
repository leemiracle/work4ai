# 01 · DomainRandomizationDNN：域随机化插件

## 角色定位

NDDS 四插件中的"变因制造者"：把仿真场景里一切可变的东西——材质、光照、位姿、缩放、可见性——变成可控随机变量，让训练出的模型对真实世界的多样性免疫。动机直通 readme 引用的域迁移论文（`readme.md:41-45`，Falling Things/ICRA2018）。单 Runtime 模块 61 文件，`DomainRandomizationDNN.uplugin` 声明 PostConfigInit 早加载且 EnabledByDefault，同时插件级依赖 NVSceneCapturer 与 NVDataObject——这条依赖被上游自认是架构债（`DomainRandomizationDNN.Build.cs:26` FIXME："should have a Core module which both of these modules share"）。

## 内部结构

三层金字塔：

- **场景编排层**：`ADRSceneManager : public ANVSceneManager`（`DRSceneManager.h:20`）持有两个 `AGroupActorManager` 引用——正式对象编排器 GroupActorManager 与噪声对象 NoiseActorManager（`:39-43`）。GroupActorManager（`GroupActorManager.h:36`）按 `FNVActorTemplateConfig`（`:16`）批量克隆 Actor（`CreateActorFromTemplate :55`），空间摆布交给 `USpatialLayoutGenerator`（`SpatialLayoutGenerator.h:14`）的 Circle/Grid2d 两派生。命令行覆盖参数（每类数量/总数上下限）在 `DRSceneManager.cpp:30-74` 逐条解析。
- **采样数据层**：`DRUtils.h` 五个 USTRUCT 采样器——FRandomRotationData（`:14`，锥体/Pitch/Roll/Yaw）、FRandomLocationData（`:64`，三轴区间）、FRandomScale3DData（`:111`，Uniform 或逐轴、下限 0.001 防退化）、FRandomColorData（`:174`，全随机/双色插值/绕基色 HSV 扰动三策略，枚举 `:165-172`）、FRandomMaterialSelection（`:241`，全部/按索引/按槽位名，枚举 `:225-238`）。
- **组件执行层**：`URandomComponentBase : public UActorComponent`（`RandomComponentBase.h:15`），对外 ShouldRandomize/Randomize/StartRandomizing/StopRandomizing 四接口（`:22-25`），随机节拍由 `RandomizationDurationInterval`（`:54-55`）控制、`bOnlyRandomizeOnce`（`:58-59`）支持一次性随机，触发点是被蓝图可覆写的 `OnRandomization` BlueprintNativeEvent（`:33-35`）。

## 外部连接

向下继承 NVSceneCapturer 的 `ANVSceneManager`（虚函数 `UpdateSettingsFromCommandLine/SetupSceneInternal`，`NVSceneManager.h:85-86`）；素材输入靠 `FRandomAssetStreamer`（`DRUtils.h:299`）扫目录异步加载；产物（随机化后的 Actor）交给 NVSceneCapturer 采集。蓝图资产 `Content/Blueprint/DR_SceneManager_BP`、`DR_AnnotatedActor_BP` 把 C++ 类装配成可拖放件。

## 数据流

以材质随机化为例：`URandomMaterialComponent`（`RandomMaterialComponent.h:20`）在 `OnRandomization_Implementation`（`:29`）里按 `FRandomMaterialSelection` 选槽位，素材二选一——`bUseAllMaterialInDirectories=true` 时扫 `MaterialDirectories`（`:50-51`），否则用手工 `MaterialList`（`:54-55`）；目录模式下 `FRandomAssetStreamer MaterialStreamer`（`:66`）以 `FStreamableManager`（`DRUtils.h:378`）分批异步加载，循环队列轮转——**材质库大小不受内存约束**。灯光组件 `URandomLightComponent`（`RandomLightComponent.h:21`）同构：强度区间+颜色（`:32-38`）。

## 设计决策

1. **组件模式而非继承**：随机化维度是 UActorComponent（可任意组合挂载），而不是 RandomizedActor 子类爆炸——`RandomizedActor.h` 存在但只是便捷壳。组合优于继承的教科书实现。
2. **采样数据与执行分离**：USTRUCT 采样器可在编辑器 inline 编辑并条件显示（`PinHiddenByDefault+InlineEditConditionToggle+EditCondition` 三件套贯穿 `DRUtils.h` 全文件），数据能被 DataObject 层复用。
3. **素材流式化**：材质/网格库常数百个，全量常驻不现实；streamer 循环队列是 2018 年 UE4 无 Niagara 时代的务实解。

## 新人提示

- 旧教程若提 "NoiseManager"，实际字段名是 `NoiseActorManager`（`DRSceneManager.h:42-43`）。
- 材质随机化超 10 对象且每帧换材质时，4.22 有 uniform buffer 内存增长卡挂已知问题（`readme.md:24-26`）——不是你的场景写错。
- 想加新随机维度：继承 `URandomComponentBase` 实现 `OnRandomization_Implementation` 即可，参考 `Components/RandomRotationComponent.h` 最小样例；采样约束尽量复用 `DRUtils.h` 既有 USTRUCT。
