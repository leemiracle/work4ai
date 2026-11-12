# 04 · NVDataObject 与 NVUtilities：参数化资产、uplugin 尾逗号与移动导航

## 角色定位

两个最小插件，分工一句话：**NVDataObject 把"采集对象长什么样"参数化成可版本管理的数据资产（JSON 双向）；NVUtilities 提供采集对象的移动/导航基础设施**。前者是 DomainRandomizationDNN.uplugin 插件级依赖之一（与 NVSceneCapturer 并列），后者最边缘——uplugin 里 EnabledByDefault:false，仅 NDDS.uproject 显式启用。

## 内部结构

**NVDataObject 双模块**（`NVDataObject.uplugin`）：

- 运行时模块仅 5 文件。核心 `UNVDataObjectAsset : public UObject`（`NVDataObject.h:18`），覆写 `IsAsset() const { return true; }`（`:32-35`）让 UObject 被资产注册表当真资产；内持 `UNVDataObject* DataObject` 引用（`:40-41`）。四个静态方法构成 JSON 双向门面（`:25-28`）：SerializeToJsonFile / DeserializeFromJsonFile / DeserializeFromJsonString / CreateObjectFromDefinitionData——后两者是"从 JSON 定义直接造出游戏对象"的工厂。`UNVDataObject`（`:53-54`）本身也带同构四静态（`:61-64`），壳与核各自可序列化。
- 接口层 `UNVDataObjectOwner/INVDataObjectOwner`（`:74-87`）：SetDataObject/GetDataObject 两纯虚，任何想"被数据对象驱动"的 Actor 实现它。
- 编辑器模块 9 文件：`FAssetTypeAction_NVDataObject` 注册右键菜单——GetActions（`AssetTypeAction_NVDataObject.cpp:18`）挂"打开源文件"动作（`:37-38`，实现 `:115` OpenSourceFiles 直跳 JSON 源文件），OpenAssetEditor 双击行为（`:43`）、源文件路径解析走 `GetResolvedSourceFilePaths`（`:59`）；`FNVDataObjectEditorToolkit : public FAssetEditorToolkit`（`NVDataObjectEditorToolkit.h:16`）定制双栏属性编辑器（PropertyView+DefaultValueView，`:25-26`），CreateEditor 双重载（`:28-29`）+ InitEditor（`:31`），RegisterTabSpawners 在 `:44-45`。
- **uplugin 尾逗号勘误**（`NVDataObject.uplugin:27-28`）：Modules 数组最后一个对象后带逗号再闭 `]`——标准 JSON 非法，UE4 自带解析器容忍。同文件还藏两个事实：描述"Parametric Dataset Exporter"（`:6`）、编辑器模块 LoadingPhase=PostEngineInit（`:26`）。

**NVUtilities 单模块**（`NVUtilities.uplugin`，仅 13 文件）：

- `ANVNavigationPath : public AActor`（`NVNavigationPath.h:29`）持 `TArray<ANVWaypoint*> WaypointList`（`:40-41`）——编辑器里摆一串路点即成路径；`bClosedPath`（`:45-46`）控制尾路点是否回连首路点成环。
- Movement 组件族三件套：`NVMovementComponentBase.h`（移动抽象基类）、`NVMovementComponent_Waypoint.h`（按路点行走实现）、`NVWaypoint.h`（路点 Actor）——全部在 `Private/Movement/`+`Public/Movement/` 子目录。
- 另有 `NVZone.h`（区域工具）。

## 外部连接

NVDataObject 被 DR 插件依赖（`DomainRandomizationDNN.uplugin` Plugins 节）——随机化组件的素材清单可走数据对象；`UNVDataObjectOwner` 接口把参数化能力开放给任意 Actor。NVUtilities 的路径/移动件喂给 DR 的 RandomMovementComponent（对象沿路径随机游走）与采集场景的动态对象；NVZone 支撑 GroupActorManager 的体积采样域（`RandomDataObject.h:53-54` 的 RandomLocationVolume 即 AVolume*）。

## 数据流

JSON→对象正向：`DeserializeFromJsonString`（`NVDataObject.h:27`）解析→`UNVDataObjectAsset` 装填→`CreateObjectFromDefinitionData`（`:28`）按 `LogicHandlerClassType`（`:70-71`，TSubclassOf<UObject>）实例化逻辑处理器→对象进场景被随机化/采集。反向：编辑器里调好资产→右键 SerializeToJsonFile（`:25`）落盘→git 版本管理/程序化批量生成。**数据集的"对象定义"从此与 uasset 二进制解耦**——文本 diff 可读、可外部工具生成。

## 设计决策

1. **壳/核分离**：UNVDataObjectAsset（资产身份）与 UNVDataObject（数据本体）拆两个类——资产系统的注册、图标、编辑器关注壳；JSON schema 演化只动核。
2. **JSON 而非 uasset 做交换格式**：uasset 二进制且引擎版本绑定；JSON 跨版本、可 diff、可脚本生成——数据管线的标准选择。
3. **尾逗号不修**：UE4 解析器容忍已 8 年，修了反而制造无意义 diff——上游事实上的"勿动"区。
4. NVUtilities 刻意保持零依赖最小集（Build.cs 仅 Core/CoreUObject/Engine），避免工具件反向污染插件依赖图。

## 新人提示

- uplugin/uproject 都是"JSON 方言"：见尾逗号（`NVDataObject.uplugin:27-28`）别急着修；但自己写新 uplugin 建议守标准 JSON，兼容性赌局不必新开。
- `NVDataObject.h` 的类名与插件同名极易混淆：文件里有两个类——Asset 壳（`:18`）与数据核（`:54`），搜符号时看清是哪个。
- 路点导航三件套在 `Movement/` 子目录，扁平 grep 会漏——按目录结构搜（`Public/Movement/NVMovementComponent_Waypoint.h`）。
- NVUtilities 默认不启用：单独抽这个插件到别的工程用时，记得在目标 uproject 显式 `"Enabled": true`（对照 `NDDS.uproject:15-17` 的启用写法）。
