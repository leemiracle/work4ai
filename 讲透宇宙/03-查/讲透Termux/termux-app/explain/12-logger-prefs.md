# 12 · 日志与配置底座：Logger.java + TermuxAppSharedPreferences.java

> 目标：`termux-shared/src/main/java/com/termux/shared/logger/Logger.java`（502 行）+ `termux-shared/src/main/java/com/termux/shared/termux/settings/preferences/TermuxAppSharedPreferences.java`（261 行），L03 通用基础工具库层。

## 一、角色定位

两文件是四模块树（terminal-emulator←terminal-view←termux-shared←app）的"开机第一步"。**Logger** 是全仓统一日志门面，五组静态方法（logError/Warn/Info/Debug/Verbose 及 Extended/Private/Toast 变体）覆盖全部 logcat 输出。图谱实测文件级 fan-in **82 边、全仓第一**（第二名 TermuxConstants 34），grep 口径 80 文件 import。派发令写 79 与图谱 82 不符，以实测为准。**TermuxAppSharedPreferences** 是主应用配置封装（工具栏/字号/日志级别/通知/boot 计数器等），fan-in 13 文件（图谱记 12）。两者在启动点交汇：`TermuxApplication.setLogConfig()` 先设默认 tag，再 `preferences.setLogLevel(null, preferences.getLogLevel())` 把持久化配置灌进 Logger 档位（TermuxApplication.java:75-84）。

## 二、内部结构

**Logger 四级体系**：OFF=0/NORMAL=1/DEBUG=2/VERBOSE=3（Logger.java:25-28），自定义序数而非 Log 位常量。静态可变 `CURRENT_LOG_LEVEL`（:32）是唯一开关，门控在 `logMessage()` 的 if-else 链（:56-67）。三条特殊通道：`logVerboseForce` 无条件直写（:215-217）；`logErrorPrivate` 反向加压，ERROR 也要求 ≥DEBUG 才落盘（:123-141），用于敏感信息；`logXxxAndShowToast` 经 `Handler(Looper.getMainLooper())` 任意线程弹 Toast（:221-256、:398-402）。长消息按 `LOGGER_ENTRY_MAX_PAYLOAD=4068`（AOSP liblog 上限，:34-44）切分：每段 `4068-8-tag-4`（:77），换行处截断（:84-87），多段加 `(i/n)` 前缀（:98）。tag 约束：`setDefaultLogTag` 截到 22 字符（Nougat 前超 23 抛异常，:453-455）；tag 禁冒号否则 logcat filterspecs 报错（:475-480）；`getFullTag` 拼成 `Termux.xxx`（:481-486）。堆栈格式化有纯文本/Markdown 两套（:284-380）。`shouldEnableLoggingForCustomLogLevel()`（:494-500）做单命令级判定：全局 OFF 一律 false；custom 为 null 按全局 VERBOSE 档；custom 无效按 VERBOSE 兜底。

**prefs 封装模式四件套**：①私有构造+双通道——同一文件 `com.termux_preferences`（TermuxConstants.java:703）开 `MODE_PRIVATE` 与 `MODE_PRIVATE|MODE_MULTI_PROCESS` 两份实例（SharedPreferenceUtils.java:25-26、39-40），存进基类（AppSharedPreferences.java:10-30）；②build 工厂——`PackageUtils.getContextForPackage(context, "com.termux")`（:44-50）让插件进程也能读主应用私有 prefs，`exitAppOnError` 重载失败弹窗退出（:61-67）；③每设置=KEY+get/set 对+commitToFile 标志（如工具栏 :71-77），写入 false 走 apply()、true 走同步 commit()（SharedPreferenceUtils.java:80-92）；④getter 捕获 ClassCastException 记日志返默认值（:153-171），配置类型被改坏不崩。典型条目：字号三界构造时算好（4×dp 最小、12×dp 取偶、256 上限，:125-152），读取 clamp（:154-157），步进 ±2（:163-170）；boot 计数器 synchronized+溢出钉 MAX_VALUE 不归零（:204-224，实现 SharedPreferenceUtils.java:206-221）；通知开关 getter 带 `readFromFile` 参数选多进程实例或缓存实例（:237-259）。

## 三、外部连接

**Logger（fan-in 82/fan-out 25）**：TermuxService 建会话前查档位决定是否打印完整命令对象（TermuxService.java:477、588）；SharedPreferenceUtils 的 getter 异常兜底也调 Logger——"基础设施的基础设施"；StreamGobbler/AppShell 读子进程流前问 custom 档（StreamGobbler.java:194、AppShell.java:124）；TermuxPluginUtils 两处决定插件结果是否记日志（:70、169）。**TermuxAppSharedPreferences（fan-in 13）**：app 模块 7 个——TermuxApplication（启动灌档）、TermuxService/TermuxActivity（运行时读写，TermuxActivity.java:545）、4 个设置 Fragment（DebuggingPreferencesFragment.java:110 一次调用完成持久化+内存+Toast）；termux-shared 6 个——TermuxShellManager 开机重置计数器（:88-89）、TermuxShellCommandShellEnvironment 起壳导出环境变量（:32、38）、TermuxCrashUtils 判崩溃报告通知（:154、302）等。另有 6 个同构兄弟类（API/Boot/Float/Styling/Tasker/Widget）构成插件生态配置骨架。

## 四、数据流

**链 A（启动配置流）**：进程起→setLogConfig→`getLogLevel()` 读 key `"log_level"`（TermuxPreferenceConstants.java:143），默认 NORMAL（:184-186）→ `setLogLevel(null, level)` 先调 `Logger.setLogLevel` 灌内存并校验（无效回退默认，Logger.java:463-473）再持久化（:188-191）；启动传 null context 跳过 Toast。**链 B（extra 启动 intent 的命令级日志开关）**：第三方 RUN_COMMAND intent 带 `EXTRA_BACKGROUND_CUSTOM_LOG_LEVEL`（TermuxConstants.java:1156）→ RunCommandService 解析进 executionCommand（RunCommandService.java:117）→ 转发 TermuxService 透传（:227，对端键 TermuxConstants.java:1015；TermuxService.java:388 接收）→ 执行时三处消费 `shouldEnableLoggingForCustomLogLevel` 决定该命令 I/O 是否记日志，不动全局档位。**链 C（boot 计数流）**：BOOT_COMPLETED→重置计数器（TermuxShellManager.java:88-89）→每起会话/壳 getAndIncrement 并导出 `ENV_SHELL_CMD__*_NUMBER_SINCE_BOOT`（TermuxShellCommandShellEnvironment.java:32、38）；`KEY_CURRENT_SESSION`（TermuxTerminalSessionActivityClient.java:420）支撑 Activity 重建后找回当前会话。

## 五、设计决策

**int 单调级别而非位掩码**：可直接存 prefs、直接列 ListPreference（`getLogLevelsArray()/getLogLevelLabelsArray()`，Logger.java:406-441），代价是门控硬编码。**静态全局档位**：80 文件零注入共享开关，这就是 fan-in 82 的成因——门面把打印做到零成本，模块自然只认它。代价同源：改签名=全仓波及；粒度只能进程级；非 volatile 有可见性风险（写少读多）。环味：SharedPreferenceUtils 依赖 Logger，Logger 只依赖 DataUtils/R，环未闭合。**MODE_MULTI_PROCESS 兜底**：官方已 deprecated 且不保证可靠，termux 留作插件跨进程读配置的通道，真正一致性靠"写侧 commit() 同步落盘+读侧 readFromFile=true 重读"（SharedPreferenceUtils.java:75-78、:237-242）——明知的权宜，选错通道就默默读旧值。**4068/4000 双常量**：普通路径留 68 字节给 tag，Extended 按实际 tag 精确切分（:34-52）。**勘误两条**：①`toogleShowTerminalToolbar` 拼写错误（应为 toggle）钉在公共 API（:79），TermuxActivity.java:545 在消费，改不得；②`Logger.setLogLevel` 与 prefs `setLogLevel` 同名不同职责（内存 vs 持久化），后者串行调前者。

## 六、新人提示

1. **tag 两雷**：tag 含冒号会让 logcat 过滤表达式失效；`setDefaultLogTag` 超 23 字符在 Android 7.0 及以下抛异常，新测试机不炸不代表老设备不炸（Logger.java:453-486）。
2. **commitToFile 别传错**：第 4 参 false=apply() 异步、true=commit() 同步；跨进程读的 key 忘传 true，对方长期读旧值。boot 计数器还叠加 synchronized，新增同类计数器照抄 :204-224 全套防御，漏一个就丢号。
3. **build() 可返回 null**（:46-47），调用方必须判空（TermuxShellManager.java:83-84 是标准姿势）；新增设置走三件套——TermuxPreferenceConstants 加 KEY+DEFAULT、封装类加 get/set 对、需跨进程再加 readFromFile 重载，漏第一件 key 就散落各处。
