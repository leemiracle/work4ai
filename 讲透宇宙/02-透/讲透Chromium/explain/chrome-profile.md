# chrome-profile：ProfileImpl —— Chrome 浏览器壳的用户配置聚合根

> 源文件：`chrome/browser/profiles/profile_impl.cc`（1818 行）
> chrome 产品外壳层 · 图谱 12 节点 · 71 条 import 边

## 1. 角色定位

`content::BrowserContext` 是 content 层"一个独立浏览上下文"（存储/cookie 隔离边界）的抽象；`class Profile : public content::BrowserContext`（profile.h:68）把它具体化为 chrome 层的用户配置，本文件实现 `class ProfileImpl : public Profile`（profile_impl.h:65）——**普通（非隐身）profile 的唯一实现**。一个实例聚合四类资产：①磁盘 profile 目录（内含 Preferences JSON、Cookies、History）；②`PrefService`；③`ProfileKey`（KeyedService 框架的 key）；④数百个 per-profile 服务。分工：`Profile` 是接口，`ProfileManager` 管生命周期，入口是静态工厂 `Profile::CreateProfile()`（L367）。隐身不是独立 profile：`OffTheRecordProfileImpl`（off_the_record_profile_impl.h:37）作为衍生物挂在本类 `otr_profiles_` map 之下。

## 2. 内部结构

**工厂与目录**：`Profile::CreateProfile()`（L367）建序列化文件操作的 `io_task_runner`（L376-378），异步/同步两路建目录（L380-399），L401 构造 ProfileImpl。目录创建**故意同步**（L316；L319-324 注释：若异步，之后本可并行的 I/O 都得与它排序）。

**构造函数**（L479）：类型三判定写 metrics——guest（L506-508）/system（L510-512）/regular（L514-516）。关键分支 L532-539：Android 上 prefs 等已在 `StartupData` 提前建好，走 `TakePrefsFromStartupData()`（L595）接管；其余平台走 `LoadPrefsForNormalStartup()`（L617，建 ProfileKey L618、pref 注册表 L619、策略 schema L623、云政策管理器按平台三选一 L640/L679/L690，最终 `CreateProfilePrefService` L730）。随后 `UserPrefs::Set`（L542）与 `SimpleKeyMap::Associate`（L544）；异步挂 `AddPrefInitObserver`（L577）等 JSON 载完，同步直调 `OnPrefsLoaded`（L581）。

**初始化链**：`OnPrefsLoaded()`（L1250）失败或关机中快速返回（L1252），并启动 500ms 的 SessionService 延迟定时器（L1288，常量 L300，防 use-before-init race）。`OnLocaleReady()`（L1173）迁移废弃 prefs 与 sync→signin 迁移——前置 7 个连续 `CHECK`（L1195-1203）断言受影响服务**均未创建**，迁移必须先行。随后 L1218 依次执行 `SimpleDependencyManager::CreateServices`（L1234）→ `BrowserContextDependencyManager::CreateBrowserContextServices`（L1241）——**全部 per-profile 服务在此批量孵化**——再进 `DoFinalInit`（L1247）。`DoFinalInit()`（L740）：`pref_change_registrar_` 注册 7 个偏好监听（L753-791，名字/头像变化镜像到全局存储）；默认 StoragePartition 的 ProtoDatabaseProvider 注入 `key_`（L834）；显式 warm 必须随 profile 创建的服务（L916-925）；OptimizationGuide 推迟到启动后（L943）；最后 `OnProfileCreationFinished`（L902）收口——L904 注释警告：delegate 可能当场销毁本对象，其后不得再有代码。

**析构序**（`~ProfileImpl` L986）：销毁通知（L987）→ **先灭全部 OTR**（L1015-1016）→ `PerformInterlockedTwoPhaseShutdown`（L1035；注释 L1031-1034：Simple 图的服务可能被 BrowserContext 图引用，必须后拆）→ policy 关停（L1041）→ `ShutdownStoragePartitions()`（L1047）。

## 3. 外部连接（图谱边取证）

71 条 import 出边归纳五组：**KeyedService 框架**（`browser_context_dependency_manager.h` 等）；**content 层**（`storage_partition.h` 等，连接点 L834 `GetDefaultStoragePartition()`——StoragePartition 是 content 持有 cookie/cache/leveldb 的分舱，profile 目录即默认分舱根）；**prefs 体系**（`pref_service.h` 等）；**策略体系**（`profile_policy_connector.h` 等）；**profile 家族**（`profile_manager.h`、`profile_attributes_storage.h`）。与 ProfileAttributesStorage 是单向镜像：`UpdateNameInStorage()`（L1755）等把偏好变化推到全局 Local State，供切换器在 profile 未加载时显示元数据。与姊妹文件耦合点：`GetOffTheRecordProfile()`（L1089）调 `Profile::CreateOffTheRecordProfile(this, ...)`（L1103），实现在 off_the_record_profile_impl.cc:647。本文件还是几十个 `*Factory` 的消费枢纽：十几个 content delegate getter（L1439/L1458/L1469 等）一行转发 `GetForProfile(this)`。

## 4. 数据流

**冷启动装配时序**：ProfileManager 调 `Profile::CreateProfile`（L367）→ 同步建目录（L383）→ 构造 ProfileImpl（L401）→ prefs 异步从磁盘 JSON 载入 → 回调 `OnPrefsLoaded`（L1250）→ 迁移（L1173）→ 两管理器批量孵化服务（L1234/L1241）→ `DoFinalInit`（L1247）→ 创建完成通知（L902/912）——各步细节见第 2 节。写路径示例：改 profile 名 → 回调 `UpdateNameInStorage`（L1755）→ 写 ProfileAttributesStorage——profile 数据与全局展示元数据单向同步。

**隐身（OTR）衍生**：开隐身窗口走 `GetOffTheRecordProfile`（L1089）：已有直接返回（L1091）；否则 `Profile::CreateOffTheRecordProfile(this, ...)`（L1103）造 `OffTheRecordProfileImpl`，存入 `otr_profiles_`（L1106）并广播（L1108）。OTR 无磁盘 prefs，读时用 parent 只读包装 `GetReadOnlyOffTheRecordPrefs()`（L1354）。窗口全关走 `DestroyOffTheRecordProfile()`（L1120）；parent 析构兜底全灭（L1015）。

## 5. 设计决策

**KeyedService 延迟创建 vs 全量单例**：全局单例无法多 profile；KeyedService 把生命周期绑到 key 上，`GetForProfile()` 首次调用才构造，依赖由 `DependsOn()` 声明、两个 DependencyManager 拓扑排序，本文件是总开关（L1234/L1241 孵化、L1035 关停）。延迟的代价是"没人碰的服务不初始化"，故有时序要求的服务要显式 warm——PrivacySandbox 必须创建时做偏好协调（L916-925）；OriginTrialsController 反而因依赖默认 StoragePartition，不能走常规随 profile 创建路径，只能手动 Get（L966-971 注释）。

**profile 目录自描述**：名字/头像/创建时间都先写进 profile 自己的 `Preferences`（唯一真相源），ProfileAttributesStorage 只是单向镜像的展示缓存（L1747-1806）——拷贝一个目录即完整迁走身份，Local State 损坏不丢 profile；代价是未加载 profile 列表信息滞后，用创建时间兜底写入（L750-751）压平。**同步/异步取舍**：prefs 异步、目录同步（L319-324）、SessionService 延 500ms（L1288）；Android 的 StartupData 接管是激进版本。**析构序制度化**：双管理器两阶段互锁（L1035）把"谁先拆"变成框架强制。

## 6. 新人提示

**加 per-profile 服务标准步骤**：①写 `XxxServiceFactory`（继承 `BrowserContextKeyedServiceFactory`）并 `DependsOn()` 声明依赖；②用 `ProfileSelections` 声明服务在 original/OTR/guest/system 下的可用性——L809 `AreKeyedServicesDisabledForProfileByDefault()` 的判断依据；③常规到此为止（首个 `GetForProfile` 触发创建），仅当必须随 profile 创建才在 DoFinalInit 尾部加显式 Get；④依赖默认 StoragePartition 时参考 OriginTrials 特例（L966-971）。

**测试与调试**：`profile_impl_unittest.cc`、`profile_manager_unittest.cc`；浏览器级测试用 `TestingProfile` 替身；偏好问题开 `prefs_internals`（L881-882）看 pref 来源链。

**三个坑**：①初始化顺序敏感——L1195-1203 的 7 个 CHECK 是活例；②`OnProfileCreationFinished`（L902）后本对象可能已销毁，其后不写逻辑；③析构只走 ProfileDestroyer/ProfileManager 通道，勿手动 delete。延伸阅读：`profile.h` 顶部注释与官方 "Keyed Service" 设计文档。
