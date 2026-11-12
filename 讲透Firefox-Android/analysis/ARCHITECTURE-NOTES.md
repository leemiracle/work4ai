# Firefox for Android（mozilla-central/mobile/android）源码实证分析

> 锚点：hg tip `3e41f4d5acb8`（2026-10-07，Bug 1846946 Android sync）。全部数字来自本地源码树实测（`/usr-data/data1/browser/mozilla-central`），与 DeepWiki 快照（gecko-dev 2025-07 停更前）可能存在一个版本代的差异。

## 1. 总体规模

| 模块 | 文件数 | 角色 |
|---|---|---|
| mobile/android 全部 | 15,285 | Android 版全部代码 |
| android-components | 9,471 | 144 个可复用组件库（两层结构） |
| fenix | 3,871 | Firefox for Android 主应用（Kotlin/Compose） |
| focus-android | 742 | Focus/Klar 隐私浏览器（同一代码库产物） |
| geckoview | 614 | Gecko 引擎的 Android 桥接层（Java API + JNI） |

语言构成：Kotlin 6,096 文件 / Java 235 / C++·IPDL 9（内核绑定在 Gecko 侧 `widget/android/`，不在 mobile/android）。

## 2. 四大子系统的依赖方向

```
fenix / focus-android  (应用层：UI、设置、Telemetry、Nimbus 实验)
        │ 依赖
        ▼
android-components  (组件层：concept* 抽象 + feature* 实现 + support* 基建)
        │ 依赖
        ▼
   concept-engine ──实现──> browser-geckoview (AC 的 GeckoView 适配)
        │ 依赖
        ▼
geckoview (org.mozilla.geckoview.*：GeckoRuntime/GeckoSession/...)
        │ JNI / EventDispatcher 消息
        ▼
Gecko 内核 (widget/android, dom, layout, js — 共享桌面代码)
```

要点：
- **concept 抽象层是关键设计**：`components/concept/`（19 个）定义 engine/storage/tabs/download 等接口，Fenix 只面向 concept 编程；换引擎（如历史 browser-engine-gecko-nightly/release 分channel）不动应用层。
- **GeckoView 不是 WebView**：自带完整 Gecko（排版/JS/网络），`geckoview/api.txt` 是公开 API 快照（lint 强制兼容性检查），`GeckoRuntime` 单例 ↔ 多 `GeckoSession`。
- 深入 Gecko↔Java 桥：`mobile/android/geckoview/src/main/java/org/mozilla/geckoview/`（GeckoSession.java、GeckoRuntime.java、ContentBlocking.java、Autofill.java、AIFeaturesController.java 等）+ Gecko 侧 `widget/android/GeckoEditable.java`、`EventDispatcher`。

## 3. android-components 组件版图（144 个，两层目录）

| 分类 | 数 | 代表组件 |
|---|---|---|
| feature | 47 | feature-downloads / feature-tabs / feature-prompts / feature-awesomebar / feature-search / feature-privatemode |
| lib | 20 | lib-crash / lib-nimbus / lib-dataprotect / lib-publicsuffixlist |
| concept | 19 | concept-engine / concept-storage / concept-fetch / concept-tabstray |
| support | 14 | support-utils / support-ktx / support-test / support-images / support-locale |
| browser | 13 | browser-state / browser-session / browser-engine-geckoview / browser-menu / browser-toolbar / browser-thumbnails |
| service | 13 | service-firefox-accounts / service-sync-autofill / service-nimbus / service-glean / service-pwnedpasswords |
| ui | 8 | ui-icons / ui-colors / ui-widgets / ui-tabcounter |
| compose | 7 | compose-base / compose-tabs / compose-awesomebar |
| tooling | 3 | lint / detekt / ktlint 规则 |

`browser-state` 是单向数据流核心（Redux 风格 `BrowserStore` + `BrowserAction` + `BrowserState`），全部 feature 组件围绕它读写。

## 4. fenix 应用层

- 入口链：`FenixApplication.kt` → `HomeActivity` → `HomeFragment`/`BrowserFragment`（Navigation 组件 `nav_graph.xml`）。
- `org.mozilla.fenix` 下 70 个 feature 包（addons/autofill/biometricauthentication/bookmarks/collections/customtabs/downloads/...），依赖注入手工装配：`components/Core.kt`、`components/UseCases.kt`。
- UI 处于 XML→Jetpack Compose 迁移中（`compose/` 包 + AC compose-* 组件双轨）。

## 5. 构建系统

- Gradle 统一入口：仓根 `build.gradle` + `gradle/libs.versions.toml`（版本目录，**AGP 9.4.1 / Kotlin 2.4.20**，2026-10 实测）。
- `mobile/android/` 下 fenix、android-components、geckoview、focus-android 共享一套 `settings.gradle`（模块化 include）。
- GeckoView 的 Gecko 内核由 mach+moz.build 编出（`mobile/android/geckoview/build.gradle` 调 `mach android-geckoview-docs` 等），产物经 Maven 本地仓供上层消费。
- Nimbus 实验框架配置：`mobile/android/nimbus.yaml` + fenix `nimbus.fml.yaml`。

## 6. 与 DeepWiki 文档的映射（勘误）

- DeepWiki `mozilla-mobile/firefox-android` 快照是 **2023-11 合仓前**的独立仓布局：源文件引用前缀 `fenix/...`、`components/...` → 本地对应 `mobile/android/fenix/...`、`mobile/android/android-components/components/...`。
- DeepWiki `mozilla/gecko-dev` 快照为 2025-07 前布局，已经是 `mobile/android/...` 路径，与当前树基本一致；但 GitHub gecko-dev 镜像已停更（最后 push 2025-07-09），此后变更只有 hg 源有。
- Focus 现目录名是 `focus-android`（DeepWiki 页内引用旧名 `focus/`）。

## 7. 快速上手命令（本地树）

```bash
cd /usr-data/data1/browser/mozilla-central
hg log -r .                      # 版本锚点
./mach bootstrap                 # 首次引导（Android 工具链）
./mach build                     # 全量构建（Gecko+GV）
cd mobile/android && ./gradlew assembleFenixDebug   # 仅 Fenix APK
```
