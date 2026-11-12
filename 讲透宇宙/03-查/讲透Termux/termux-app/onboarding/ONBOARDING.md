# termux-app 入驻文档（ONBOARDING）

> 图谱 `8629e632`·1284 节点/2762 边/14 层/16 步 tour·2026-10-26·锚均经源码核实

## 1. 项目一句话定位与治理

**Termux 是 Android 自包含的终端模拟器 + Linux 环境**：手机上得到带 apt 的完整命令行。本仓只含应用本体，引导文件系统与软件包由 `termux/termux-packages` 外部提供（README.md 开篇）。

- **许可证分层**：主体 GPLv3-only（LICENSE.md:1）；terminal-view/emulator 例外 Apache 2.0（LICENSE.md:5-7）；termux-shared 主体 MIT，`termux/*` 子包 GPLv3、`file/filesystem/*` 为 GPLv2+CE（termux-shared/LICENSE.md:1-19）。
- **签名即生态**：全家桶共享 `sharedUserId=com.termux`，三渠道签名互不兼容（README.md:61）；README.md:55 钉 v0.118.0 前漏洞告示。
- **贡献纪律**：Conventional Commits；常量收敛到 termux-shared。

## 2. 仓库全景

`settings.gradle:1` 一行 include 四模块，依赖：terminal-emulator（仿真引擎，零依赖）←api· terminal-view（自绘 View）← termux-shared（业务核心+JNI）← app（宿主）。**terminal-emulator**：TerminalEmulator 状态机、TerminalBuffer/Row、KeyHandler、Sixel、JNI 挂 PTY 的 TerminalSession，独立发布 `com.termux:terminal-emulator`；**terminal-view**：TerminalView/TerminalRenderer+手势/文本选择，23 方法 TerminalViewClient 解耦；**termux-shared**：TermuxConstants（fan-in 34）、TermuxSession/TermuxShellManager、ExtraKeysView、ExecutionCommand/AppShell、LocalSocketManager、Logger（fan-in 82）/FileUtils/Error/Errno；**app**：TermuxActivity、TermuxService、TermuxInstaller、RunCommandService、bootstrap 原生嵌入（app/src/main/cpp/termux-bootstrap-zip.S）。版本 0.118.0（app/build.gradle:46-47）。

## 3. 架构分层速览（14 层自底向上）

L01 仿真引擎=terminal-emulator：状态机+缓冲+PTY 宿主，零依赖。L02 渲染视图=terminal-view 自绘 View，手势/缩放/选择。L03 通用工具=Logger/Error/Errno/DataUtils/设置框架。L04 文件与系统=FileUtils（约 2000 行）+POSIX 属性+权限/崩溃报告。L05 Socket/Shell=ExecutionCommand 状态机、AppShell、LocalSocket JNI。L06 业务核心=`termux/` 包常量契约、会话/环境变量、ExtraKeysView。L07 共享资源=布局/图标/主题。L08 主界面=TermuxActivity+五大控制器+设置 Fragment。L09 服务与入口=TermuxService/RunCommand/Installer/Receiver/SAF。L10 资源与原生=布局+Manifest+termux-bootstrap.c/zip.S。L11 Gradle=四模块 build.gradle/proguard/testkey/jitpack。L12 CI/CD=六条 workflow+dependabot。L13 测试=仿真器 19 个回归测试类+app 单测。L14 文档=README/LICENSE/SECURITY。扇入三巨头：Logger(82)/TermuxConstants(34)/DataUtils(28)。

## 4. 核心数据流

### 4.1 按键→PTY→仿真→渲染（热路径）

- **输入**：软键盘经 IME `commitText` 进 `sendTextToTerminal`（TerminalView.java:356-381）；硬件键 `onKeyDown`→`handleKeyCode`（:770,802），KeyHandler.getCode 映射转义序列（:922→KeyHandler.java:156）后 `writeCodePoint` 写 PTY（:908）。
- **回程**：InputReader 线程读 PTY→64KB `mProcessToTerminalIOQueue`（TerminalSession.java:44,133-148），`MSG_NEW_INPUT` 唤醒主线程排空喂 `mEmulator.append`（:337-346→TerminalEmulator.java:688-690）；`processByte` 驱动状态机——UTF-8 拼装（:693）、CSI/OSC/DCS 分发、主/备屏切换（:246-254,:1856）。写入向 4KB 队列（:49,178-179）。
- **渲染**：`notifyScreenUpdate` 触发 TerminalView.onScreenUpdated（:455-459）重绘。

双向管道经 ByteQueue 解耦、仿真只在主线程——不丢字的关键设计。

### 4.2 会话生命周期

TermuxActivity 先 startService 再 bindService（TermuxActivity.java:260-266），经 LocalBinder 取 TermuxService（:387-390）；会话登记进 TermuxShellManager 三列表（TermuxShellManager.java:31,36,41=前台/后台/插件待执行）。登录 shell 探测失败兜底 `/system/bin/sh`（TermuxSession.java:108-114）并以 `-` 前缀启动（:125）；退出由 Waiter 线程捕获（TerminalSession.java:166-172）。

### 4.3 Bootstrap 首装

TermuxInstaller 查 $PREFIX（默认 `/data/data/com.termux/files/usr`，TermuxConstants.java:595）：缺失则 `loadZipBytes` 调 native `getZip`（TermuxInstaller.java:379-387；termux-bootstrap.c:6-11，zip 由 termux-bootstrap-zip.S:1-18 按架构 `.incbin` 内嵌 .rodata），流式解压到 $STAGING_PREFIX（:154-160）、解析 SYMLINKS.txt（:163,208）、原子 rename 到 $PREFIX（:215）。变体由 env `TERMUX_PACKAGE_VARIANT` 决定（app/build.gradle:12,52）。

## 5. 关键机制深潜

### 5.1 TerminalEmulator 状态机

单类吃下 VT100/xterm 全量序列（fan-out 65）：`append`→`processByte` 解 UTF-8 进 ESC 状态（TerminalEmulator.java:688-693）再分发 CSI/OSC/DCS；SGR/DEC 模式/鼠标报告/字符集/Sixel 皆在此。主/备双 TerminalBuffer（:498-499）让 vim 切屏不污染滚回区；样式打包 64 位 long（TextStyle），宽度 WcWidth 判 0/1/2。19 个测试类守回归。

### 5.2 ExtraKeys 与插件契约（含疑似 bug）

ExtraKeysView 按 ExtraKeysInfo 解析 termux.properties JSON 矩阵重建按钮网格（ExtraKeysView.java:386；ExtraKeysInfo.java:139-151）。交互三类：普通键直发；**repetitive 键长按连发**（`scheduleWithFixedDelay` 周期 `mLongPressRepeatDelay`，:535-545）；**特殊键两态**——CTRL/ALT/SHIFT/FN 单击激活、长按锁定（:546-556），ACTION_UP 撤销（:560-570）。宿主经 `IExtraKeysView` 注入（app 侧 TermuxTerminalExtraKeys 桥到 TerminalView），Termux:Float 复用——键定义留 properties、行为留 shared、注入留宿主。

**疑似 bug（worker 发现，源码实证）**：`setLongPressRepeatDelay` 区间校验读**字段旧值**而非参数——条件两操作数均为字段 `mLongPressRepeatDelay`，参数只在赋值右侧（ExtraKeysView.java:356-362，病灶 :357）。首调字段为 0，`0>=5` 恒假落默认 80（:225，恰与传参一致故无人察觉）；此后旧值恒在区间，**新值免检生效**（-1/10000 照收），MIN/MAX 防线（:140-142）失效。修一行：条件两字段改参数；常量名双下划线系上游残留；对照 `setLongPressTimeout`（:342-348）正确用法，是笔误。

### 5.3 TermuxService 进程模型

前台 Service 承载全部会话：`onStartCommand` 分发 STOP/WAKE_LOCK/WAKE_UNLOCK/SERVICE_EXECUTE（TermuxService.java:141-160），返回 `START_NOT_STICKY` 被杀不重启（:163-165）；WakeLock/WifiLock 成对管理（:102-103,314-320）。"UI 可死、会话不死"：Activity 只 bind 设回调（TermuxActivity.java:355-358）。RunCommandService 收 RUN_COMMAND intent 先校验 `allow-external-apps` 再转发（RunCommandService.java:58,127-128）——插件生态闸门。

### 5.4 AmSocket 直连

Android 12 禁直接 exec `/system/bin/am`，Termux 自建：TermuxApplication 启动 am socket 服务（TermuxApplication.java:63）→AmSocketServer 监听 Unix 域套接字，命令经 termux-am-library 执行，按 **`exit_code\0stdout\0stderr\0`** 回传（AmSocketServer.java:40,:136-144）。底层 LocalSocketManager 全走 JNI（termux-shared/src/main/cpp/local-socket.cpp，603 行 9 native 方法），对端 `SO_PEERCRED` 校验（local-socket.cpp:552），PeerCred 初始化 -1 防误判 root（PeerCred.java:38-39）。全仓 JNI 工程化之最。

## 6. 构建与调试

- `./gradlew assembleDebug`；debug 用 `testkey_untrusted.jks`（app/build.gradle:80-97），勿用于发布。
- 变体 env `TERMUX_PACKAGE_VARIANT=apt-android-7|apt-android-5`（app/build.gradle:12）。
- AGP 8.13.2（build.gradle:7）+Gradle 9.2.1+NDK 29.0.14206865、compileSdk 36/minSdk 21/targetSdk 28（gradle.properties:18-21）；ABI splits+universalApk（app/build.gradle:69-75）；versionName semver 强校验（:160-164）。
- 测试 `./gradlew test`，CI .github/workflows/run_tests.yml:22-26；三库发 JitPack（jitpack.yml:1-3）；调试 TERMUX_DEBUG，proguard 不混淆（app/proguard-rules.pro）。

## 7. 新人上手路径（16 步 tour 精简 9 里程碑）

1. **读治理**（tour 1）：README+两级 LICENSE。
2. **仿真内核**（tour 2-4）：TerminalEmulator→Buffer/Row→TerminalOutput，再看 KeyHandler/Sixel。
3. **PTY 管道**（tour 3）：TerminalSession 三线程（TerminalSession.java:133-172）+JNI 四方法（JNI.java:26-39）。
4. **渲染手势**（tour 5）：TerminalView/Renderer；TerminalViewClient 接口=app 接入点。
5. **shared 设施**（tour 6-7）：Logger/Error/Errno/DataUtils/SharedProperties/FileUtils。
6. **命令框架**（tour 8-9）：ExecutionCommand 状态机（ExecutionCommand.java:33-39，守卫 :265-271）+AppShell（:131）。
7. **业务契约**（tour 10-11）：TermuxConstants 一处改全家桶生效；ExtraKeysView（顺看 5.2）。
8. **App 门面**（tour 12-13）：TermuxActivity 装配+TermuxService 七组件。
9. **质量发布**（tour 14-16）：Installer 链路+测试+发布；加新序列惯例**先补测试**（TerminalTestCase 断言 DSL）。

## 8. 延伸阅读

- 图谱：`termux-app/.understand-anything/knowledge-graph.json`
- DeepWiki：`../deepwiki/`（44 页，INDEX.md 全目录）；本档 ExtraKeysView bug 为图谱侧增量
- 上游：github.com/termux/termux-app（8629e632）·termux.dev/security
- 姊妹库：`../../../../../讲透宇宙/03-查/讲透Termux//` 63 仓索引见顶层 README.md；插件仓入口回调本档 L05/L06 契约
