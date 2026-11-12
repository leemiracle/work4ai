# 10. shell-loader：从 Termux 命令行到 X server 进程的引导蹦床

> 模块 `shell-loader/`（`:shell-loader` + `:shell-loader:stub`，settings.gradle:1-4 全仓四模块它占其二）。行号锚基于 commit `29d4460b` 现场核实。

## 1. 角色定位：双发布体系之间的"海关"

Termux:X11 有两条独立发布渠道：Termux 包仓库的 deb/pacman（`pkg install termux-x11`）与 GitHub/Play 的应用 APK。X server 进程必须由 Termux 命令行的 `app_process` 拉起、住在 Termux 的 uid 下，而应用代码属于另一套签名体系——shell-loader 就是横跨两边的"海关"：一个 39 行的 Java 引导器（Loader.java 全文仅 39 行）加两个 wrapper 脚本打进 deb，运行时"找到已安装 APK → 校验签名 → 把 APK 代码加载进本进程执行"。核心主张写在类注释里：loader 与应用版本完全解耦，全部业务逻辑都在目标 APK（Loader.java:9-12），deb 与 APK 可各自升级互不牵连。模块体量全仓最小，却独占知识图谱 L08 一层。

## 2. 内部结构：引导器 + 隐藏 API 桩 + wrapper 模板

### 2.1 Loader.java 三步契约

`main(String[])`（Loader.java:16）三步走：①入口类可覆盖——先读环境变量 `TERMUX_X11_LOADER_OVERRIDE_CMDENTRYPOINT_CLASS`（:17），缺省回落 `BuildConfig.CLASS_ID`（:18，构建期烧入 shell-loader/build.gradle:37），同一 loader 因此能反射进 APK 内任意带 `static void main(String[])` 的类；②签名校验——经隐藏 API `ActivityThread.getPackageManager().getPackageInfo(...)` 取签名，SDK≤32 走 int flags、≥33 走 long 双签名分支（:20-22），两条 assert 卡关：包必须存在（:23）、`signatures.length==1` 且证书哈希等于 `BuildConfig.SIGNATURE`（:24）。SIGNATURE 是构建期从 lorie-app 的 debug 密钥库算出的 `Arrays.hashCode(certificate.getEncoded())`（shell-loader/build.gradle:26-28,36）；失败文案也是 BuildConfig 常量（:38-43），由 `catch (AssertionError)` 打印（Loader.java:30-31）；③加载移交——`new PathClassLoader(sourceDir, null, getSystemClassLoader())`（:27-28）挂上目标 APK，反射 `main`（:29）。移交后控制权永不回头：目标 main 以 `Looper.loop()` 收尾（CmdEntryPoint.java:49）。

### 2.2 stub：compileOnly 隐藏 API 桩

`ActivityThread.getPackageManager()` 等框架内部 API 在公开 SDK 里不存在。解法是自造只有签名没有实现的桩库，六文件：ActivityThread（三个方法全 `throw new RuntimeException("STUB")`，ActivityThread.java:6-16）、IPackageManager（getPackageInfo 特意声明 int/long 双重载，IPackageManager.java:4-5）、IActivityManager（仅 getIntentSender，IActivityManager.java:9-12）、IIntentSender（:9-11）、IIntentReceiver（内嵌 `Stub.performReceive`，:9-11）、ContextImpl（空抽象类，ContextImpl.java:5）。

关键在 `dependencies.compileOnly project(':shell-loader:stub')`（shell-loader/build.gradle:19）——桩类绝不进 loader.apk 的 dex。运行时 `Class.forName("android.app.ActivityThread")` 命中的是 ART boot classpath 里的真框架类：app_process 是系统级宿主，不受应用侧隐藏 API 限制。桩的使命只是让 javac 通过，"STUB" 异常永远执行不到；它真正约束的是编译期签名须与 AOSP 内部签名逐参匹配，错一个参数运行期即 NoSuchMethodError。注意桩有两个消费方——lorie 模块同样 `compileOnly`（lorie/build.gradle:53），CmdEntryPoint 自己也用这套隐藏 API（见第 3 节）；stub 本身是独立 library（stub/build.gradle:1-3），manifest 只有一行 `<manifest />`。

### 2.3 wrapper 脚本与模板替换链

termux-x11.in 是 `termux-x11` 命令的真身，23 行六件事：Termux bash shebang（:1）；headless 守卫，无 /system/bin/getprop 即判定 docker 类环境并推荐 tigervnc（:2-8）；SDK<24 守卫（:9-15）；把 LD_LIBRARY_PATH/LD_PRELOAD/CLASSPATH 转存为 `XSTARTUP_*` 前缀（:16-18）；CLASSPATH 指向 loader.apk 并 unset 两个 LD 变量（:19-20）；父 shell 设有 USR1 trap 则导出 `TERMUX_X11_NOTIFY_PARENT=1`（:21）；最后 `exec /system/bin/app_process -Xnoimage-dex2oat / --nice-name="termux-x11 @APPLICATION_ID@ $*" com.termux.x11.Loader "$@"`（:22）。

两个 `@...@` 占位符由 companion-package.gradle 的 `generateWrapperScripts` Copy 任务替换：Ant ReplaceTokens 注入 `[APPLICATION_ID: com.termux.x11, EMBEDDED_APPLICATION_ID: com.termux]`（companion-package.gradle:38，值源自 shell-loader/build.gradle:30-31 的 ext 属性），rename 去掉 `.in`（:36），产物赋 0755（:39）。同一对值同时喂 BuildConfig（:33-34）——模板与常量同源，单一事实源。

termux-x11-preference.in 是偏好读写 CLI：SDK≥34 走同构的 loader 通道，仅用环境变量把入口类覆盖成 `LoriePreferences\$Receiver`（:16-21，`\$` 转义内嵌类名）；旧路走 `am broadcast`（:23）再从输出 sed 解析 `result=`/`data="..."`（:71-81）。Android 14 专修来自上游提交 efb2d97，同时引入 IRemoteCmdImterface AIDL 作新回传通道。

### 2.4 构建配置与伴侣包

模块有双重身份开关：IDE 同步时按 library、命令行构建时按 application（shell-loader/build.gradle:4-7），前者避免生成 Run 配置，后者产出固定名 `shell-loader-debug.apk`（:21-22）。debug 构建显式 `signingConfig null`（:12）——loader.apk 是未签名的，从不被安装、只当 dex 容器，签名校验在目标 APK 一侧。R8 开启但 `-dontobfuscate`、仅 keep `Loader.main`（proguard-rules.pro），并排除 kotlin-stdlib 保持零依赖（:24）。BuildConfig 还烧入 git commit（:44），Loader 启动的 logcat 行会带它（Loader.java:26）。

companion-package.gradle 的 `buildCompanionPackage` 把 wrapper 与 loader.apk 组装成 deb+pacman 双格式伴侣包：三文件落位 `data/data/com.termux/files/usr/{bin/termux-x11, bin/termux-x11-preference, libexec/termux-x11/loader.apk}`（:55-60），postinst `chmod 400 loader.apk`（:87,93）防加载器被运行中进程篡改；deb 手工拼 Ar 包（:105-113），pacman 端生成 .PKGINFO/.MTREE 并声明 `replaces/conflict/provides = termux-x11`（:147-149,179-183）；包名 termux-x11-nightly（:22），版本取自 lorie/version.gradle 拼 `-0`（:23），依赖 xkeyboard-config（:27）。

## 3. 外部连接

上游：Termux bash 是直接调用方，app_process/ART boot classpath 是运行宿主，隐藏 API 经 Binder 抵达 system_server。下游：目标 APK 双入口——`CmdEntryPoint.main`（CmdEntryPoint.java:44-48）与 `LoriePreferences$Receiver.main`（LoriePreferences.java:739）。构建期上游：签名哈希取自 lorie-app debug 密钥库（shell-loader/build.gradle:26-28），版本取自 lorie 模块（companion-package.gradle:23），模块虽独立、构建配置仍挂在两兄弟身上。发布面：CI 上传 deb/pkg.tar.xz 并挂 nightly（.github/workflows/debug_build.yml:68-74）。桩的横向复用最值一提：CmdEntryPoint 用它做三件事——`getPackagesForUid` 取本 uid 包名（CmdEntryPoint.java:105）、`ActivityManager.getService`→`ActivityManagerNative.getDefault` 双级反射取 IActivityManager 再 getIntentSender 手工投递（:112-127）、`sun.misc.Unsafe.allocateInstance(ActivityThread)` 无构造造实例再 getSystemContext() 拿 Context（:156-170，绕开"非 zygote 进程没有现成 ActivityThread"的死穴）。README 另有绕过 loader 的手动路径：`pm path` 取 APK 路径设成 CLASSPATH 后直接 `app_process / com.termux.x11.CmdEntryPoint :0`（README.md:130-135）。

## 4. 数据流：敲下 `termux-x11 :0` 之后

1. Termux bash exec wrapper（进程映像被 app_process 替换），nice-name 变为 `termux-x11 com.termux.x11 :0`。
2. app_process 以 CLASSPATH=loader.apk 构造 system class loader，反射调 `Loader.main`（termux-x11.in:19,22）；`-Xnoimage-dex2oat` 抑制 loader dex 的镜像编译——文件只读且仅 39 行，解释执行即可。
3. Loader 经 ActivityThread 桩向 PMS 要 PackageInfo，双 assert 过签名闸（Loader.java:20-24）。
4. PathClassLoader 挂目标 APK，反射 `CmdEntryPoint.main`（:27-29）；loader 此后永不再执行，是一次性蹦床。
5. CmdEntryPoint 造 Context（Unsafe 路，CmdEntryPoint.java:156-170）、按进程位数加载 APK 内 `lib/<abi>/libXlorie.so`（:199-209），`start()` native 引导进 `dix_main` Xorg 主循环——本进程从此就是 X server 进程。
6. 若 wrapper 探测到父 shell 的 USR1 trap（termux-x11.in:21），补丁后的 xserver 把 `TERMUX_X11_NOTIFY_PARENT` 视作 xinit 语义的就绪信号开关，向父进程发 SIGUSR1（patches/xserver.patch:157-161，connection.c 的 `RunFromSmartParent` 分支）。
7. fork xstartup 子进程时把 `XSTARTUP_CLASSPATH/XSTARTUP_LD_LIBRARY_PATH/XSTARTUP_LD_PRELOAD` 还原回原名（InitOutput.c:232-235 的 INHERIT_VAR 宏）——Termux 里设的环境变量穿透了 app_process 这层清洗；X server 自身补挂 libtermux-exec 前也检查 `XSTARTUP_LD_PRELOAD` 防双重注入（cmdentrypoint.cpp:123-125）。
8. GUI 进程经 knock 端口与 ACTION_START 广播被唤起、反连本进程的 Binder（详见本系列 05 篇）。

偏好通道（`termux-x11-preference list`）在 Android 14+ 走另一条流：wrapper 设 override（termux-x11-preference.in:19）→ 同一 Loader 反射进 `Receiver.main`（LoriePreferences.java:739）→ stdin/argv 解析进 CHANGE_PREFERENCE Intent 并 `bundle.putBinder(null, iface)` 塞回传 Binder（:747-751,767-779）→ 广播送 GUI 进程 onReceive（:578-580 取回 Binder）→ 结果经 `IRemoteCmdImterface.exit()` 回命令行打印并 System.exit（:723-727 出口 Binder，:782-787 广播投递与 5 秒超时兜底）。

## 5. 设计决策与批判

compileOnly 桩是三选一的甜点位。备选：藏完整框架 jar（体积与维护都重）或纯反射字符串调用（零编译期检查，上游改签名只能运行期炸）。桩拿到类型检查，代价是签名漂移风险内嵌——IPackageManager 的 int/long 双签名（IPackageManager.java:4-5）正是 Android 13 改 flags 类型的伤疤；IActivityManager 桩只声明一个重载，上游改参即断；CmdEntryPoint 的双级反射（CmdEntryPoint.java:112-119）说明作者自己也不放心单一签名假设。

安全闸压在 assert 上是全模块最脆一处。校验的执行形态是两条 assert（Loader.java:23-24）——断言开关取决于宿主运行时而非语言保证；若某环境断言被关闭，校验会被静默跳过、恶意 APK 直接被加载，比"校验失败"危险一个量级。线上证据表明断言路径当前真实可达（提交 b17064e 修的恰是这条 assert 输出的用户可见文案，此前签名不匹配被静默吞掉、只显示"未安装"），但"能跑"不等于"有保证"，改成显式 `if+throw` 是零成本加固。

未签名 + sharedUserId 构成防误装伪装面。loader.apk 声明 `android:sharedUserId="android.uid.system"` 且注释直言 "This app should not be installable"（shell-loader/src/main/AndroidManifest.xml:2-3）：非平台签名的 APK 声明系统共享 UID 会被安装器直接拒绝，叠加不签名（build.gradle:12）双保险——用户误把 loader.apk 当应用安装时快速失败，而不是装出残废应用。

版本解耦是有历史包袱的。当前只认 `APPLICATION_ID` 单一目标（Loader.java:21），但提交 7122284（"build: drop the termux-app build with Termux:X11 embedded"）之前还循环尝试 EMBEDDED/APPLICATION 两包、靠 versionName 是否含 `+x11` 区分；今天残留的 `EMBEDDED_APPLICATION_ID` 常量与 wrapper 路径占位符（termux-x11.in:1,19）是已拆通道的活化石——EMBEDDED 指"宿主 Termux"，APPLICATION 才是"目标应用"。

环境变量转存是必要洁癖。Termux 的 libtermux-exec（LD_PRELOAD）注入 app_process 会破坏 ART 链接，wrapper 必须 unset（termux-x11.in:20）；但 xstartup 子进程又活在 Termux 世界、需要这些变量，于是有 XSTARTUP_* 前缀的寄存-取回闭环（InitOutput.c:232-235）。

## 6. 新人提示

- 改启动目标类：只动 BuildConfig 的 CLASS_ID（shell-loader/build.gradle:37）；运行期用 override 环境变量可零改动试任意入口（Loader.java:17）。
- 改包名/签名相关：两个 ID 在 shell-loader/build.gradle:30-31，同时牵动 wrapper 模板与 deb 落位路径；换密钥库后用户必须同步重装 deb 与 APK，否则触发 mismatch 文案（:42-43）。
- 别去找桩的实现：stub 目录全是 `throw RuntimeException("STUB")`，运行期真身在 boot classpath；改桩只改签名不改逻辑。
- 排障入口：logcat tag `Termux:X11 loader`（shell-loader/build.gradle:35），启动行含目标 APK 路径与 commit（Loader.java:26）；stderr 三态——not found（没装 APK）、Signature verification failed（两边来源不一致）、Java 异常栈（:30-37）。
- 拼写坑两枚：AIDL 名 `IRemoteCmdImterface` 是上游自带的笔误（非 Interface），grep 照抄；`LoriePreferences\$Receiver` 的 `$` 在脚本里必须转义（termux-x11-preference.in:19）。
- 手动复现启动链（不依赖 deb）：README.md:130-135 的三行命令——验证"loader 只是包装"这一事实的最快方式。
