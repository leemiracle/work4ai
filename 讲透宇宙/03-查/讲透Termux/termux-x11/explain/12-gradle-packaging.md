# 12. Gradle 构建与打包体系（L10）

> 仓库 `/usr-data/data2/repos/termux-repo/termux-x11`（commit 29d4460b），行号锚经现场核实（2026-10-27）。覆盖任务书五文件+shell-loader 两份。

## 1. 角色定位：一条命令长出四种工件

全仓出厂流水线：上游吃 `lorie/src/main/cpp/` 原生源码与 Java 应用层，下游吐四类工件——standalone APK、sharedUid APK、Termux 伴侣包（.deb + .pkg.tar.xz）、带符号 so。CI 一条命令 `./gradlew assembleDebug`（`.github/workflows/debug_build.yml:55`）收走全部产物，master 推送刷新 nightly（`:79` 起）。

版本三处钉死：Gradle 9.8.2（`gradle/wrapper/gradle-wrapper.properties:4`）、AGP 9.3.1（根 `build.gradle:11`）、NDK 29.0.14206865（`lorie/version.gradle:11`）。`gradle.properties` 仅三行，末行 `android.enableR8.fullMode=true`：debug 也跑 full mode R8，keep 缺失无兜底。

## 2. 内部结构：四模块依赖图与"反向宿主探测"

`settings.gradle:1-4` 声明四模块：

```
lorie-app ──implementation→ lorie ──compileOnly→ shell-loader:stub
(lorie-app/build.gradle:83)   (lorie/build.gradle:53)
shell-loader：compileOnly stub（:19）· 读 :lorie-app 签名（:26）· apply companion（:46）
```
显式依赖外三条结构耦合：

**其一，lorie 反向宿主探测**。库模块要知道被谁打包（快捷方式 targetPackage 依赖宿主 applicationId），Gradle 没有"向上问宿主"的内建机制。`lorie/build.gradle:11-16` 遍历兄弟项目，找"apply 了 application 插件且 implementation 里有指向自己的 ProjectDependency"者——为何不用"有 application 插件"判据：shell-loader 也 apply 但非宿主（`:9-10` 注释）。找不到或多个都 `GradleException` 拒构建（`:18`、`:20`）；`:6` 先 `evaluationDependsOn` 才能在配置期读兄弟依赖。探测结果 `hostApplicationId`（`:22`）喂给 buildConfigField（`:34`）与 generateShortcuts。

**其二，签名横向依赖**。shell-loader 配置期从 `:lorie-app` 取 `signingConfigs.debug`（`shell-loader/build.gradle:26`），把证书的 `Arrays.hashCode` 烧进 `BuildConfig.SIGNATURE`（`:36`）——运行期 Loader 签名断言的构建期对侧。

**其三，版本单源**。`lorie/version.gradle` 以 ext 闭包生成版本名：`1.03.01`+git short commit+日期（`:3-4`）；`lorie-app/build.gradle:33` 与 `lorie/build.gradle:32` 都引用它，伴侣包版本号也从该文件正则抠出（`companion-package.gradle:23`）。NDK 单源动机见 `version.gradle:7-10` 注释：宿主不引用同一 `termuxX11NdkVersion` 时 CMake 配置两侧漂移、原生码编译两遍。

根 `build.gradle` 极薄：AGP classpath（`:11`）、三仓库含 jitpack（`:15-21`）、clean（`:23-25`）——重逻辑全下沉模块脚本。

## 3. 外部连接：NDK/CMake 挂接与产物命名

原生构建挂接一行：`lorie/build.gradle:41` 的 `externalNativeBuild.cmake.path "src/main/cpp/CMakeLists.txt"`，NDK 版本由 `:28` 的 `ndkVersion termuxX11NdkVersion` 钉住。CMakeLists 头部：CMake ≥3.22（`CMakeLists.txt:1`）、ASM（`:5`）、C11/C++17（`:7-8`）、RelWithDebInfo（`:9`，CI 带符号工件来源）。xserver 影子补丁也从这里挂接（`target_apply_patch`，`CMakeLists.txt:22-24`，dry-run 幂等）。
两个 APK 形态开关：`useLegacyPackaging false`（`lorie/build.gradle:42`）让 so 不解压、直接从 APK 加载；`buildFeatures.aidl true`（`:43`）驱动 `IRemoteCmdImterface.aidl` 生成 Binder 接口（Imterface 拼写笔误系仓库自带）。

产物命名不走默认：`lorie-app/build.gradle:65-78` 用 Variant API 把输出改名 `termux-x11-universal-${name}.apk`，standalone 只拼 buildType、其余拼 `${flavorName}-${buildType}`（`:67`）——`:64` 注释：release 链接指向此名，不跟模块走。

## 4. 数据流：构建期代码生成的两条产线

**产线一 generatePrefs（偏好 XML → 强类型 Java）**。任务在 `lorie/build.gradle:56` 注册，`DOMBuilder` 解析 `preferences.xml`（`:58`），按节点名四路映射（`:64-75`）：EditTextPreference→String、SeekBarPreference→Int、ListPreference→List（含 entries/entryValues，`:69-72`）、SwitchPreferenceCompat→Boolean。输出 `build/generated/java/com/termux/x11/Prefs.java`（`:78`）：每 key 一个 `public final` 字段（`:90-97`）加 `keys` HashMap（`:99-102`），继承 `LoriePreferences.PrefsProto`（`:89`，基类定义 `LoriePreferences.java:799`）。

两个特判：**extra_keys_config 被排除在通用循环外**（`:64` 的 `!= "extra_keys_config"`），在 `:98` 单独生成——默认值是 `TermuxX11ExtraKeys.DEFAULT_IVALUE_EXTRA_KEYS` 而非 XML 字面量。**生成类埋了一次性迁移**（`:109-111`）：attach 时发现旧布尔键 `keepScreenOn` 且新键 `screenIdleTimeout` 未写入，就翻译成 "never"/"system" 提交——旧用户升级不丢设置。对账：preferences.xml 实测 63 个 `app:key`；类型化节点 = 17 List + 3 SeekBar + 30 Switch + 1 EditText 共 51，加特判 1，Prefs.java 共 52 字段；余下 4 Preference 与 7 PreferenceScreen 只做导航。

入编译：`:115` 把 `build/generated/java` 追加进 sourceSets，`:116` 挂 `preBuild.dependsOn`——`assembleDebug` 自动先生成再编译。

**产线二 generateShortcuts（模板替换）**。`lorie/src/main/templates/xml/shortcuts.xml:12` 的 `android:targetPackage` 是占位符 `@@APPLICATION_ID@@`；任务（`lorie/build.gradle:118-123`）替换成宿主探测的 `hostApplicationId` 落到 `build/generated/templateRes/`，`:124-125` 注入 res 并挂 preBuild。不写死包名：lorie 是库，targetPackage 必须等于宿主真实包名，只有构建期能定。

## 5. 设计决策：双 flavor、进程断言、签名与 R8

**双 flavor（`lorie-app/build.gradle:36-45`）**。`flavorDimensions "uid"` 分 standalone 与 sharedUid。后者差异不止 sharedUserId：`targetSdkVersion 28`（`:43`）——共享 UID 应用须同 targetSdk，Termux 主应用锁 28，sharedUid 陪降。其余在 flavor 专属 manifest：`lorie-app/src/sharedUid/AndroidManifest.xml:3` 声明 `android:sharedUserId="com.termux"`，`:6` 把 application 钉进 `android:process="com.termux"`（`:5` 注释：否则进程被划进独立 cpuset）。

**VerifySharedUidProcess 进程断言（`lorie-app/build.gradle:7-22`）**。打包前用 `XmlSlurper` 解析 merged manifest，对五类组件（`:15`）核对进程名，违规抛 `GradleException` 列肇事组件（`:20`）。挂接走 Variant API：仅 sharedUid 注册并让 `package<Variant>` 依赖它（`:71-76`），standalone 不跑。

**签名策略（`lorie-app/build.gradle:47-52`）**。debug 也用固定密钥库 `testkey_untrusted.jks`（密码明文在仓库）。目的不是安全而是契约链起点：本地构建的 APK 与 shell-loader 烧录的证书哈希互相可验，nightly 装机混用来源会得到 reinstall 提示（`shell-loader/build.gradle:42-43`）。

**R8：debug 也开，规则分两层**。`buildTypes.debug` 同开 `minifyEnabled` + `shrinkResources`（`:58-59`，nightly 即 debug）。应用层规则仅一行 `-dontobfuscate`（`lorie-app/proguard-rules.pro:1`）：裁剪照做、类名不混淆。真正的 keep 规则以 consumerProguardFiles 住库里（`lorie/build.gradle:36`）：LorieView native 方法（`lorie/proguard-rules.pro:4-7`，被裁即 UnsatisfiedLinkError）、CmdEntryPoint.main（`:9-11`，app_process 入口）、七个隐藏类 `-dontwarn`（`:15-21`）、performReceive（`:23-25`）、onSetInitialValue（`:28-30`）。

**shell-loader 插件切换戏法（`shell-loader/build.gradle:4-7`）**。按 `startParameter.taskNames` 是否为空二选一：sync 时 library、构建时 application——阻止 Android Studio 生成 run 配置（`:3` 注释）。构建态输出固定名 `shell-loader-debug.apk`（`:22`），签名置 null（`:12`）但 minify+shrink 全开（`:13-14`）、排除 kotlin-stdlib（`:24`）。companion-package.gradle 把它与两个 wrapper 脚本（ReplaceTokens 同样替换 APPLICATION_ID，`:33-40`）按 `data/data/com.termux/files/usr` 前缀（`:55`）打成 .deb（`:105-113`）与 pacman 包（`:179`）。这一切由 `lorie-app/build.gradle:80` 的 `assembleDebug dependsOn buildCompanionPackage` 收编。

## 6. 新人提示

1. **改偏好先改 preferences.xml**。Prefs.java 在 `build/generated/` 下是产物，直接改会被静默覆盖；类型由 XML 节点名决定。
2. **新偏好 key 看三处**：preferences.xml、生成的 Prefs 字段、LoriePreferences/LorieView 读取点。extra_keys_config 是唯一不走通用映射的 key。
3. **本地只出 APK** 跑 `:lorie-app:assembleStandaloneDebug`；`assembleDebug` 连带打伴侣包（`lorie-app/build.gradle:80`）。无 git 环境版本名退化 nongit（`version.gradle:4`）。
4. **sharedUid 加组件**若须独立进程：standalone 可以、sharedUid 直接构建失败（`:7-22` 断言），刻意的。
5. **R8 裁出运行期崩溃**先查 `lorie/proguard-rules.pro`——规则住库里不住 app。
6. **NDK 升级只改 `version.gradle:11`**，别处硬编码致原生码编译两遍（`:7-10`）。
7. **产物名是对外契约**：`termux-x11-universal-*` 被 release 链接、CI、loader 提示三处引用。
