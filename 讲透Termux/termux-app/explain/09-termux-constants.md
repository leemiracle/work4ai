# 09 · TermuxConstants —— 全家桶的"常量宪法"与插件契约中枢

> `termux-shared/src/main/java/com/termux/shared/termux/TermuxConstants.java` ·1338 行·v0.53.0·L06 Termux 业务核心层

## 1. 角色定位

Termux 不是一个 app，而是共享 `sharedUserId=com.termux` 的 **1+6 应用家族**（主应用 + Termux:API/Boot/Float/Styling/Tasker/Widget 六个插件），外加不安装任何插件的第三方 app 通过 RUN_COMMAND intent 远程驱动。跨进程、跨 APK 的协作全靠**字符串契约**——intent action 名、extra 键名、文件/socket 路径、包名、通知渠道 ID。任何一处两端拼写不一致，插件不是报错而是**静默失效**（intent action 对不上 = 石沉大海）。本文件就是这份契约的唯一事实源：javadoc 自述"hosted by termux-shared lib and should be imported by other termux plugin apps as is instead of copying constants to random classes. The 3rd party apps can also import it"（TermuxConstants.java:288-291）。

图谱实证其枢纽地位：**fan-in 33 条 imports 边，全仓扇入第二**（仅次于 Logger 的 82，onboarding 第 3 节三巨头榜），出边仅 3 条（contains/exports/一条对 ExecutionCommand 的 import）——纯提供者，零运行时逻辑。归 L06 业务核心层，却被 L06-L09 四层共同消费：L06 的 properties/preferences 家族、L08 的 TermuxActivity、L09 的 TermuxService/RunCommandService/Installer 全部引用。它还是一份**版本化规范**：文件头 v0.53.0（:15）+ 53 条变更日志（:20-284），javadoc 明令"If changes are made to this file, increment the version number and add an entry in the Changelog"（:291-292）——把 API 演进纪律写进了文件本体。

## 2. 内部结构

1338 行里没有一个方法、没有一行逻辑，组织法是**"扁平区 + 嵌套类区"两段式**。

**扁平区（:329-908）**按块注释分八个主题区：

- **身份块 ×7**：每个 app 一组"APP_NAME + PACKAGE_NAME + GITHUB_REPO_NAME/URL/ISSUES_URL + FDROID_URL"六件套（:350-444）。包名全部从根推导：`TERMUX_PACKAGE_NAME = "com.termux"`（:352），API=.api（:366）、Boot=.boot（:380）、**Float=.window 而非 .float**（:394，仓库名叫 termux-float 但包名历史定格在 com.termux.window）、Styling=.styling（:408）、Tasker=.tasker（:422）、Widget=.widget（:436）。
- **插件名单**：两个 `Arrays.asList` 把六插件名/包名收进 List（:454-468），供 TermuxPluginUtils 等遍历。
- **APK 签名指纹**：四个发布渠道（F-Droid :479、GitHub :485、Google Play :491、Termux Devs :497）各配 SHA-256 签名证书摘要（:482/:488/:494/:500）——共享 uid 的家族必须同签名才互通，常量让任何一方能校验对方 APK 出身。
- **路径体系**：四级推导链 `/data/data/com.termux`（:581，`@SuppressLint("SdCardPath")` :580 压掉硬编码路径的 lint）→ `/files`（:588）→ `$PREFIX=/files/usr`（:595）→ bin/etc/include/lib/libexec/share/tmp/var 八个子目录（:601-645），另有 staging（:650）、`$HOME`（:657）、config home `.config/termux`（:663）、config prefix `usr/etc/termux`（:668）、data home `.termux`（:674）、storage（:680）、apps（:687）。**String 与 File 孪生成对**（如 :595-597），路径字符串供再拼接、File 对象供直接用。
- **配置文件**：七 app 的 SharedPreferences 文件基名（:703-721，如 `com.termux.window_preferences` :712）；termux.properties 主/副双轨——`~/.termux/`（:726）与 `~/.config/termux/`（:731），XDG 惯例晚接入故成 secondary；Float 专属属性同构（:746-761）；colors/font 交由 Termux:Styling 共写（:766-773）；crash log（:777-780）；`termux.env` 及其 tmp 文件（:784/:787）。
- **插件脚本目录**：Boot 的 `~/.termux/boot`（:797）、Widget 的 `~/.shortcuts`（:804）+ tasks/（:811-814）+ icons/（:821-824）、Tasker 的 `~/.termux/tasker`（:832）——每个插件的"用户界面"就是一个被监视的目录，路径定义权收在主应用侧。
- **通知**：四组 channel id/name + 三个 int 通知 ID 1337/1338/1339（:849/:856/:874，Termux→RunCommand→Float 顺序编排）。
- **杂项闸门**：`PERMISSION_RUN_COMMAND`（:886）、`PROP_ALLOW_EXTERNAL_APPS`（:890，默认 "false" :892）、`BROADCAST_TERMUX_OPENED`（:895）、FileProvider authority `com.termux.files`（:898）、逗号替身字符 U+201A（:901/:905）、环境变量根前缀 `TERMUX`（:908）。

**嵌套类区（:918-1336）**按"app → 组件 → intent 语义"三级组织：`TERMUX_APP`（:918）是主应用命名空间，独占第三级嵌套 `TERMUX_ACTIVITY`（:943）/`TERMUX_SERVICE`（:984）/`RUN_COMMAND_SERVICE`（:1128）；六插件类各一层（:1200-1336），其中 Float 有 `TERMUX_FLOAT_SERVICE`（:1245）、Widget 有 `TERMUX_WIDGET_PROVIDER`（:1321）两个二级。`TERMUX_SERVICE` 是最大嵌套类：4 个 action（stop/wake_lock/wake_unlock/execute，:987-999）、URI scheme `com.termux.file`（:1002）、约 20 个 extra（:1004-1053）、`EXTRA_SESSION_ACTION` 的 4 个 int 值 0-3 配 MIN/MAX 边界（:1062-1094）、7 个结果 Bundle 键（:1100-1114）。`RUN_COMMAND_SERVICE` 镜像一套全前缀 extra（:1135-1191）。消费端甚至直接静态导入嵌套类省前缀：`import ...TermuxConstants.TERMUX_APP.TERMUX_SERVICE`（TermuxService.java:36、RunCommandService.java:21-22）。

## 3. 外部连接

**出边**只有一条真 import：`ExecutionCommand`（:6-7），仅为 javadoc 引用其 `Runner` 枚举（EXTRA_RUNNER :1013、已废弃 EXTRA_BACKGROUND :1010-1011）。`android.content.Intent`（:4）也只服务 javadoc。

**入边 33（图谱 imports 边）+ 1 漏网 = 34 个文件**（源码 grep 实证；差异源 = `TermuxBootstrap.java`——scanner 漏边，其 `import ...TermuxConstants.TERMUX_APP` 在 TermuxBootstrap.java:9，onboarding 的"fan-in 34"按文件数口径成立）。消费方分四组：①app 模块 10 个——TermuxActivity/TermuxService/RunCommandService/TermuxApplication/TermuxInstaller/TermuxOpenReceiver/TermuxDocumentsProvider/FileReceiverActivity 等；②shared 业务类——TermuxUtils/TermuxPluginUtils/TermuxCrashUtils/TermuxShellUtils/TermuxFileUtils/TermuxNotificationUtils；③**preferences 家族 ×7**（TermuxAppSharedPreferences.java:29-31 等，每个 app 一个类，靠 `getContextForPackage(TERMUX_PACKAGE_NAME)` 拿主应用包上下文跨进程读同一份 prefs 文件，:45）；④shell 环境 + am socket（TermuxShellEnvironment/TermuxAppShellEnvironment/TermuxAPIShellEnvironment/TermuxAmSocketServer）。

传播通道是**库发布**：termux-shared 挂 `maven-publish`（termux-shared/build.gradle:2,67）经 JitPack 出包（jitpack.yml:1-3），插件仓与任意第三方 app 以依赖坐标引入同一份常量类——这是"import as is"策略的物理基础。另有 README documents 边（图谱）。

## 4. 数据流

**链路一：RUN_COMMAND intent（第三方 app → Termux 执行）**——本文件契约的完整闭环：

1. 第三方 app 构造 Intent：action = `RUN_COMMAND_SERVICE.ACTION_RUN_COMMAND`（值 `com.termux.RUN_COMMAND`，:1135），塞 `EXTRA_COMMAND_PATH`/`EXTRA_ARGUMENTS`（:1138/:1140）；若参数含逗号，用 `EXTRA_COMMA_ALTERNATIVE_CHARS_IN_ARGUMENTS` 传替身字符（:1142/:1144），发送端把 `,` 换成 U+201A（:905）。
2. `RunCommandService.onStartCommand` 校验 action（RunCommandService.java:75），逐 extra 解包进 ExecutionCommand（:117-125），替身字符逆向还原为普通逗号（:99-101）。
3. **安全闸**：`checkIfAllowExternalAppsPolicyIsViolated` 读 `PROP_ALLOW_EXTERNAL_APPS`（:890）——必须双满足"对方持 PERMISSION_RUN_COMMAND（:886）+ 用户在 termux.properties 显式放行"（RunCommandService.java:132，违反时强制通知用户）。
4. 转发主服务：action 换 `TERMUX_SERVICE.ACTION_SERVICE_EXECUTE`（:999），extra 全套换成 `TERMUX_SERVICE.*` 键名（:1004-1053）——**同一份数据过一道键名翻译**，这正是两套前缀必须共存在一个文件里的原因。
5. 结果回传：调用方的 pendingIntent（:1170）+ 结果 Bundle 键 stdout/stderr/exitCode/err/errmsg（:1100-1114）。

**链路二：am-socket 路径约定**。Android 12 起禁止直接 exec `/system/bin/am`，Termux 自建 socket 服务：路径常量 `TERMUX_APP.TERMUX_AM_SOCKET_FILE_PATH = APPS_DIR_PATH + "/termux-am/am.sock"`（:924），即 `/data/data/com.termux/files/apps/com.termux/termux-am/am.sock`——注意 APPS_DIR_PATH 是 files/ 下按**包名**命名的目录（:921，0.44.0 才从 `termux-app` 改成 `com.termux`，:250-251）。`TermuxAmSocketServer.start` 把它交给 AmSocketServerRunConfig 监听（TermuxAmSocketServer.java:106）。同路径体系还长出环境变量链：根前缀 `TERMUX`（:908）拼出 `TERMUX_APP__`（TermuxAppShellEnvironment.java:34）再拼 `ENV_TERMUX_APP__AM_SOCKET_SERVER_ENABLED`（:77，写入 :132）；`termux.env` 本体走 tmp→final 原子落盘（:784/:787 → TermuxShellEnvironment.java:56），tmp 与 env 文件同在"prefix 空目录判定"忽略清单里（:693-694，TermuxInstaller 用它区分"干净安装"与"残留安装"，TermuxInstaller.java:106）。

## 5. 设计决策

**为何常量类而非资源/BuildConfig？**四个硬理由：①**跨 APK 可发布**——插件和第三方 app 需要同一份契约，`public static final String` 经 JitPack 打进消费方；资源要走 createPackageContext 且每个 app 资源表独立，BuildConfig 是各模块构建产物、天然不同步，都不能当契约。②**编译期内联零开销**——常量直接进消费方字节码，无运行时查表；但这也是双刃剑：**消费方不重编译就永远带着旧值**，所以才有 :291-292 的强制版本纪律，以及 0.53.0（2025-01-12）给四插件类加 `_APP` 后缀这种"改名的代价=逼全生态重编译"的破坏性变更显式记账（:282-284）。③**人可 grep 的规范**——每个常量带 `// Default: "..."` 尾注（如 :352/:595），不看 IDE 也能对表；包名迁移步骤整段写在 javadoc（:304-318）。④**替代方案的存在本身就是反例**——文档明言 binaries 里硬编码了 `$PREFIX`（:294-296），改动半径远超一个文件。

**勘误两处（注释 ≠ 实际值，现场核实）**：①`TERMUX_FLOAT_SERVICE` 三个 action 的 Default 注释写 `com.termux.float.*`，实际表达式 `TERMUX_FLOAT_PACKAGE_NAME + ".ACTION_STOP_SERVICE"` 算出 **`com.termux.window.*`**（:1248/:1251/:1254 对照包名 :394）——注释是旧包名时代的残尸；②`EXTRA_PLUGIN_API_HELP` 值算出 `com.termux.execute.plugin_api_help`，注释却写 `plugin_help`（:1029）。两处都以表达式为准；**千万别照注释"修复"常量值**，线上对端认的是算出的那个串。

**命名学的双层逻辑**：`RUN_COMMAND_SERVICE` 的 extra 全部 `com.termux.RUN_COMMAND_*` 前缀（:1138-1191），因为它们是 intent **顶层** extra，必须命名空间防撞；而 `TERMUX_SERVICE` 的结果键 `pendingIntent`/`result`/`stdout` 是裸键（:1032/:1100-1114）——它们藏在 Bundle **内部**一层，天然有壳。同理 int 值 0-3 是线上协议编号（:1062-1088），永不重排。废弃不删除：`EXTRA_BACKGROUND`（:1010-1011/:1151-1152）由 `EXTRA_RUNNER` 接棒但保留兼容；`EXTRA_RELOAD_STYLE` 与 `ACTION_RELOAD_STYLE` 同值 `com.termux.app.reload_style`（:954/:957），一个串历史上身兼 action 与 extra 两职的活化石。另有细节：Float 通知 ID 的 javadoc 错写着"used by TERMUX_APP.TERMUX_SERVICE"（:873），实为 Float service 用——第三处注释瑕疵。

## 6. 新人提示

1. **内联陷阱 + 版本纪律**：改任何常量值，消费方（尤其外部插件仓）必须重编译才生效；加常量/改值必须升版本号并写 changelog（:291-292），否则下游按旧 JitPack 版本引入时两头对不上。删常量前先 `@Deprecated` 挂一个版本周期（参照 :1010）。
2. **注释不是真相**：`// Default:` 尾注是手工维护的，已实证三处错（:1248-1254、:1029、:873）。读值先在 IDE 里看表达式求值结果或自己拼一遍；写新常量时尾注必须与推导式同步。
3. **改包名 ≠ 改一行**：推导链看着优雅，javadoc :304-318 诚实列出了真清单——build.gradle 的 applicationId/manifestPlaceholders（app/build.gradle:54）、strings.xml 的 ENTITY、**shortcut.xml 与 *_preferences.xml（文档明言"dynamic variables don't work in it"）**，且 bootstrap 二进制硬编码 `$PREFIX`（:294-296）。另外新路径常量务必遵守 0.2.0 起的 `_DIR`/`_FILE` 后缀命名规约（:23-24），新插件常量按"每 app 一个嵌套类、每组件再嵌一层"的既有拓扑放（0.53.0 刚统一过 `_APP` 后缀，:282-284，别再引入第三种命名代）。
