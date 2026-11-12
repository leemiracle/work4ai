# Termux:X11（termux-x11）新人上手文档（ONBOARDING）

> 基于知识图谱（519 节点 / 923 边 / 12 层 / 16 步导览，commit `29d4460b`）自动生成，全部行号锚经源码现场核实。
> 仓库：`/usr-data/data2/repos/termux-repo/termux-x11`（termux/termux-x11）

## 1. 一句话定位与治理

**一句话**：termux-x11 在 Android 设备上原生实现了一个完整的 X server（Xlorie），让 Termux（含 proot/chroot 发行版）里的 X11 图形应用不经 VNC/RDP 远程协议、直接在本机显示与交互。README 的自述只有一行且极尽傲慢——"How does it work? Just like any other X server."（`README.md:24-25`）。

三点事实钉住它的身份：① 它是 Termux 官方组织（github.com/termux）的 X11 方案，与 termux-app/termux-packages 同仓治理，安全报告引流至 Termux 统一政策（`SECURITY.md`），漏洞不接受 issue 只接受私密渠道；② 它不是模拟帧缓冲的简单投屏——原生层真的跑着一套打了补丁的 Xorg xserver DIX/DDX 全栈，RandR/Present/EXA/DRI3/GLX 一样不缺（`lorie/src/main/cpp/lorie/InitOutput.c:62`）；③ 双进程架构（Java GUI 进程 + X server 原生进程）是理解全仓一切设计的钥匙，第 4、5 节反复回到这一点。

为什么必须是两个进程？Android 的图形出口（Surface/SurfaceView）只能住在有窗口的 Java 应用进程里，而 X server 需要常驻 Termux 命令行环境、继承 DISPLAY 语义并服务任意数量的客户端——把两者塞进一个进程既不符合 Android 进程模型，也无法让 X server 在 GUI 退出后继续存活。于是本仓几乎全部工程复杂度都花在"两个进程如何高效共享像素与事件"这一件事上：第 4 节的数据流、第 5 节的桥接机制，都是这个约束的产物。与 `pkg install tigervnc` 的 VNC 路线相比（wrapper 脚本在 headless 环境检测里两次推荐它，`shell-loader/scripts/termux-x11.in:3-7`），本地方案没有远程协议的编码与往返开销、输入延迟更低、还支持每显示器独立 Android 窗口（`README.md:89` 的 -tag），代价则是这套庞大的原生工程。

## 2. 仓库全景：四个模块与"影子"依赖

`settings.gradle` 声明四个 Gradle 模块：

- **lorie**（主模块，库）：一半是 Java 应用层（`lorie/src/main/java/com/termux/x11/` 下 MainActivity/LorieView/LoriePreferences/输入系统/额外按键），一半是 cpp 原生层（`lorie/src/main/cpp/lorie/` 下 14 个源文件：InitOutput.c、renderer.cpp、buffer.c、lorie.h、workqueue.cpp 等），最终链成 `libXlorie.so`；
- **lorie-app**（打包模块）：application 壳，双 productFlavor（standalone / sharedUid），见第 6 节；
- **shell-loader**：Termux 命令行启动通路（wrapper 脚本 + Loader.java）；
- **shell-loader:stub**：android.app 隐藏 API 的编译期桩，见第 5 节。

最重要的结构事实：**xserver 本体是空 submodule**。`.gitmodules` 声明 16 个 X11 生态子模块（xserver/pixman/xorgproto/libx11/libxtrans/libepoxy/xkbcomp/libxcvt/libxfont/libxfont 家族等），clone 后 `lorie/src/main/cpp/xserver/` 目录是空的（实测 0 文件）——`README.md:11` 的 "Submodules caveat" 专门警告这一点。构建期才拉取，而本仓对上游的全部改动以"影子"形式存在：8 个补丁（`lorie/src/main/cpp/patches/`：xserver.patch、Xtrans.patch、x11.patch、pixman.patch、libepoxy.patch、xkbcomp.patch、xkbfile.patch + dix-config.h.in 模板）和 11 个 CMake 配方（`lorie/src/main/cpp/recipes/`）。**想看"Termux:X11 与上游 Xorg 有何差异"，答案不在 xserver/ 目录（它是空的呢），而在 patches/ 与 recipes/ 这两层影子里。**

## 3. 架构分层速览（12 层自底向上）

图谱 12 层按依赖方向自底向上：

**L1 X server 原生核心（Xlorie NDK C 层）**：InitOutput.c 承载屏幕/RandR/Present/EXA/DRI3/GLX 初始化（`InitOutput.c:331-334` 还暴露 `-disable-dri3`、`-force-bgra`、`-legacy-drawing` 等运行时开关）；renderer.cpp 是 GLES2/EGL 渲染线程；buffer.c 管理跨进程共享缓冲；lorie.h 是协议中枢；InitInput.c 注册鼠标/触摸屏/键盘三个 X 输入设备（`InitInput.c:272-274` 的三连 AddInputDevice）与触控笔（`InitInput.c:245,252`）；InputXKB.c 源自 TigerVNC 血统，把 KeySym 反查回 X 键码并维护修饰键状态机（`InputXKB.c:77` 的 pressedKeys[256]）；clipboard.c 钩住 X11 SendEvent/ConvertSelection 协议处理（`clipboard.c:201-202`）。

**L2 SysV 共享内存兼容子层**：`lorie/src/main/cpp/lorie/shm/` 以 ashmem 为后备完整模拟 SysV IPC——shmget/shmat/shmdt/shmctl 四调用（`shm/shmem.c:194` 直接 open("/dev/ashmem")），段句柄经 Unix socket + ancillary fd 跨进程传递；sys/shm.h 用 include_next 拦截式宏重定向系统符号，让 proot 里的 X 客户端无感使用 SysV 共享内存，shm/README.md 还记录了与原生语义的差异（如进程死亡自动销毁段）。

**L3 JNI/Binder 跨进程桥接层**：activity.cpp（GUI 进程侧）+ cmdentrypoint.cpp（X server 进程侧）双入口，AIDL 双接口（ICmdEntryInterface / IRemoteCmdImterface），CmdEntryPoint.java 作为 Binder Stub 负责按 ABI 加载 liblorie 并引导原生服务器，详见第 5 节。

**L4 Java Lorie 应用层**：MainActivity 是用户看到的入口——承载 LorieView 渲染表面、管理多实例（-tag 每显示器一实例）、画中画与服务器心跳看门狗；LorieView（SurfaceView）是全仓 Java 侧枢纽，渲染、视口缩放（100%-400%，`LorieView.java:729`）、剪贴板与 IME 桥接都聚在这一个类；LoriePreferences 提供 7 个子屏设置；LorieApp 持有双偏好存储（builtInPrefs + secondaryPrefs，`LorieApp.java:65-66`）并把 ACTION_START/STOP 广播路由给对应 tag 的实例（`LorieApp.java:130-138`）；ImeHeightProvider 探测软键盘高度、SamsungDexUtils 以静态块反射探测 SemWindowManager 封装 DeX 专有 API，是两个平台适配样本。

**L5 输入系统**：源自 Chromium Remoting 的成熟触摸管线——TouchInputHandler 按设备类型（手指/触控笔/硬件鼠标/DeX 触控板）分派 MotionEvent，InputStrategyInterface 三策略，InputEventSender 翻译为 InputStub 低级注入；SwipeDetector 用双指位移向量数量积甄别滑动与捏合，TapGestureDetector 补齐原生 GestureDetector 只支持单指的短板，RenderData 维护屏幕坐标与 X 坐标间的 Matrix 变换；KeyInterceptor 走另一条路——无障碍服务系统级拦截硬件按键。

**L6 额外按键（ExtraKeys）**：没有物理键盘时屏幕底部工具栏就是 X11 会话的生命线。数据侧 ExtraKeysInfo/ExtraKeyButton 把 JSON 配置解析为按钮矩阵（宏按空格拆分、逐键别名替换），ExtraKeysConstants 维护键码映射与五套 Unicode 显示表；视图侧 ExtraKeysView 以 GridLayout 渲染并支持长按连发调度（`ExtraKeysView.java:204` 的 ScheduledExecutorService），X11ToolbarViewPager 提供按键页+文本输入页两页容器，TermuxX11ExtraKeys 把按钮翻译成 X11 事件序列。

**L7 Android 资源层**：preferences.xml 是 63 个偏好 key 的单一事实源（实测 63 个 `app:key`，7 个 PreferenceScreen：main/output/pointer/kbd/other/ekbar/userActions），5 个 layout、16 个 drawable；accessibility_service_config.xml 声明 canRequestFilterKeyEvents="true"（`:9`）使 KeyInterceptor 能过滤硬件按键；shortcuts.xml 是构建期占符替换的快捷方式模板。

**L8 shell-loader 启动器模块**：wrapper 脚本 + Loader.java + 隐藏 API 桩 + 伴侣包打包，详见第 5.5 节。

**L9 xserver 构建影子层**：.gitmodules 声明 16 个子模块，CMakeLists 编排原生构建，8 个补丁驯服上游，11 个配方定义交叉编译规则——第 5.3 节深潜。

**L10 Gradle 构建与打包体系**：三模块 + stub 组合、双 flavor、debug 密钥库与 R8 保留策略（JNI 注册的类与方法必须 keep），详见第 6 节。

**L11 CI 与仓库治理**：debug_build.yml 主流水线（master 推送时刷新 nightly 发布，`.github/workflows/debug_build.yml:83-84`）、update-wrapper.yml 保持 wrapper 同步、cleanup-runs.yml 清理陈旧运行、dependabot.yml 自动升级依赖。

**L12 项目文档**：README 23 节覆盖安装双件套（Termux:X11 + termux-x11 包）、三种启动方式与 proot/chroot 集成，SECURITY.md 引流安全报告。

## 4. 核心数据流：一帧 X11 输出的完整旅程

**正向链（X 客户端 → 屏幕）**，六站：

1. **X 客户端**（Termux 里的 xfce4-session 等）经 Unix domain socket 连上 Xlorie server，PutImage/渲染请求进入 DIX 分派（打补丁后的 dispatch.c 注入了 `ddxRequestDone()` 钩子，`patches/xserver.patch:28`）。
2. **Xlorie server 进程**（cmdentrypoint.cpp 引导）：命令行入口经 app_process 拉起后，`cmdentrypoint.cpp:222` 调 `exit(dix_main(...))` 正式进入 Xorg 主循环；Present 扩展执行拷贝时把 GPU 拷贝请求写进跨进程环形队列 `lorie_shared_server_state.gpuCopyQueue`（struct 定义于 `lorie.h:202`，环形队列成员 :215-222，容量 8：`#define LORIE_GPU_COPY_QUEUE_CAPACITY 8` 于 `lorie.h:191`）。
3. **共享 buffer**：根窗口像素住在 LorieBuffer 里——三种后端 `LORIEBUFFER_REGULAR / LORIEBUFFER_FD / LORIEBUFFER_AHARDWAREBUFFER`（`buffer.h:16-18`），X server 进程把缓冲句柄经 Unix socket 的 SCM_RIGHTS ancillary 数据发给 GUI 进程（`buffer.c:545` 发、`:576` 收，cmdentrypoint.cpp:530 的 lorieRegisterBuffer 配 ADD_BUFFER 事件做幂等注册）。
4. **GUI 进程 Java 层**：LorieView（SurfaceView）持有 Surface，nativeInit 建立原生上下文（`LorieView.java:702`），surfaceChanged 直接把 Surface 交给 renderer。
5. **GLES2 渲染线程**（renderer.cpp）：收到 drawRequested 后锁住共享状态（X server 与渲染器同画根窗口会撕裂，`lorie.h:204-207` 的注释详述了 pthread 进程间互斥的设计），把 gpuCopyQueue 里的延迟拷贝经 FBO 回放（`renderer.cpp:793-872` 的 drain 循环），根窗口纹理绑定为 GL 纹理（AHB 后端走 EGLImage 零拷贝导入）。
6. **Android Surface** 合成上屏；光标是独立位图，在共享状态里另有互斥锁与 x/y/热点坐标。

**反向链（触摸 → X 事件）**：Android MotionEvent 进 TouchInputHandler 按设备类型分派（`TouchInputHandler.java:101` 的 mInputStrategy 持策略），三种策略实现在 `InputStrategyInterface.java`——NullInputStrategy（触屏直连，:50）、SimulatedTouchInputStrategy（触摸模拟鼠标，:62）、TrackpadInputStrategy（触控板 tap-to-click，:243）；InputEventSender 把事件翻成 InputStub 低级注入调用，进 LorieView 的 sendKeyEvent/sendTextEvent（@FastNative 声明于 `LorieView.java:813,816`），JNI 落到 activity.cpp 注册的原生方法，经连接 socket 写成 lorieEvent（cmdentrypoint.cpp:487 的 `write(conn_fd, &e, sizeof(e))`），最终被事件泵 `handleLorieEvents`（`cmdentrypoint.cpp:262`，从 :281 的 EVENT_SCREEN_SIZE 起按 type 分发）翻译成 X 输入事件注入 X server。

## 5. 关键机制深潜

### 5.1 JNI 双桥：activity.cpp 与 cmdentrypoint.cpp

系统跑在**两个进程**里：Java GUI 进程（正常 Android 应用）与由 Termux 命令行 app_process 拉起的 X server 进程。两桥分工：

- **activity.cpp**（GUI 侧）：`activity.cpp:412` 的 JNINativeMethod 表向 LorieView 注册 28 个原生方法（sendKeyEvent/setClipboardSyncEnabled（:475）/surfaceChanged/getCursorPosition 等），`:574` 另向 MainActivity 注册 1 个（nativeSetLaunchWindowingModeFreeform，反射 ActivityOptions.setLaunchWindowingMode 进自由窗口模式），`:555` 的 RegisterNatives 完成绑定。
- **cmdentrypoint.cpp**（X server 侧）：CmdEntryPoint.java 作为 `ICmdEntryInterface.Stub` 提供 Binder 服务（`CmdEntryPoint.java:32`），按进程位数加载原生库（`CmdEntryPoint.java:199`：is64Bit ? SUPPORTED_64_BIT_ABIS[0] : 32 位，路径 lib/&lt;abi&gt;/libXlorie.so）；MainActivity 经 `ICmdEntryInterface.Stub.asInterface`（`MainActivity.java:711`）拿到代理后 `service.getXConnection()`（`:746`）取得 X 连接 socket 的 ParcelFileDescriptor 交给 LorieView。命名冷知识：AIDL 文件 `IRemoteCmdImterface.aidl`（lorie/src/main/aidl/com/termux/x11/）——"Imterface" 是仓库自带的拼写笔误，生成类名跟着错，搜索时别写成 Interface。
- 多实例握手走"敲端口"协议：cmdentrypoint 在预定义端口上听 knock socket，对端发 MAGIC 串即触发 sendBroadcast 唤醒/定向对应 tag 的 Activity（`cmdentrypoint.cpp:618-670`）。

### 5.2 buffer 共享与 workqueue：无锁优先的性能层

- **LorieBuffer**：统一 API（分配/锁/绑纹理/跨进程发送）下三种后端可互转；跨进程传递靠 ancillary fd（SCM_RIGHTS），X 客户端自己的 MIT-SHM 段则由 L2 的 SysV 兼容层接住。xshmfence.c 按 X 客户端共享段大小在 futex 与 pthread 两套围栏实现间分发（`xshmfence.c:6,10`），为 Present 提供同步。
- **workqueue.cpp**：用 Vyukov 无锁 MPMC 环形缓冲重实现 X server WorkQueue（`workqueue.cpp:15` 注释言明动机：单字原子内建在 armeabi-v7a 上也保持 lock-free；`:41` kRingSize=128 必须是 2 的幂）。溢出路径：环形满时溢出到 spinlock 保护的 malloc 链表，排空即释放——稳态零分配。这也是 xserver.patch 给上游 `ProcessWorkQueue/QueueWorkProc` 加下划线前缀重命名的原因（`patches/xserver.patch:38-40`），避免符号冲突。

### 5.3 xserver 影子构建：16 submodule + 8 补丁 + 11 配方

`recipes/xserver.cmake:279` 把补丁后的 xserver 源码切成 24 个静态库再 whole-archive 链进 `Xlorie SHARED`（`:298`，与 EGL/GLESv2/log/android 系统库链接，C++ 侧 -fno-exceptions -fno-rtti，`:299`）。xserver.patch 全 635 行改 18 个文件：dispatch.c 注入 ddxRequestDone（:28）、dixutils.c 重命名 WorkQueue 系列（:38-40）、present_execute.c 挂 lorieGpuCopyAck GPU 拷贝回执链（:337 起）、xkb/ddxLoad.c 组装 xkbcomp_argv 支持进程内调用（:599）。根 CMakeLists.txt 定义 `target_apply_patch` 函数（`CMakeLists.txt:22-24`：先 dry-run 检测已打过就跳过），`CMakeLists.txt:80` 依依赖序 include 11 个配方（xorgproto→fontenc→md→pixman→tirpc→xshmfence→Xdmcp→Xau→Xfont2→xkbcomp→xserver）。xorgproto 配方还现场生成 XlibConf.h 并 symlink libxtrans（`recipes/xorgproto.cmake:5-6`）——X11 头文件体系大半是构建期合成的。

### 5.4 Xau/Xdmcp 配方笔误（勘误）

`recipes/Xau.cmake:4` 写着 `target_compile_options(Xdmcp PRIVATE ...)`——在 Xau 库的配方里把编译选项（-D_GNU_SOURCE/-DHAVE_EXPLICIT_BZERO/-fPIC）错安到 Xdmcp 目标头上（Xdmcp.cmake 自己 :3 已有一份），Xau 实际没吃到这组选项。目前 Xau 仅两个源文件（AuDispose.c/AuRead.c）侥幸无症状，但这是上游潜伏的复制粘贴笔误，改造构建链时须知道。

### 5.5 shell-loader：签名校验 + 隐藏 API 桩

启动脚本 `shell-loader/scripts/termux-x11.in` 校验非 headless 环境与 SDK≥24 后，转存 LD_LIBRARY_PATH/CLASSPATH 环境变量（:16-18），把 CLASSPATH 指向 loader.apk（:19）并 `exec /system/bin/app_process ... com.termux.x11.Loader`（:22）。Loader.java 的三步契约（`Loader.java:9-10` 注释）：取包信息 → **断言目标 APK 签名哈希与构建期烧入的 BuildConfig.SIGNATURE 一致**（`:24` 的 assert，防 loader.apk 被恶意 APK 调包投毒）→ 以 PathClassLoader 加载并反射调用 main（`:28-29`）——loader 与应用版本完全解耦。stub 模块提供 ActivityThread/IActivityManager/ContextImpl/IIntentSender/IIntentReceiver/IPackageManager 六个 android.app 隐藏 API 桩（shell-loader/stub/src/main/java/ 下），编译期占位、运行时被系统真实 Binder 代理替换，免去隐藏 SDK 依赖。

## 6. 构建与调试

- **工具链**：Gradle + CMake ≥3.22 + NDK（两模块 `ndkVersion termuxX11NdkVersion`，由 gradle.properties/version.gradle 统一管理），C11/C++17（`CMakeLists.txt:7-8`）+ ASM（:5），RelWithDebInfo（:9），38 个编译警告选项逐个探测可用性后批量启用（`CMakeLists.txt:80` 前的 foreach）。compileSdk/targetSdk 34、minSdk 24（`lorie-app/build.gradle:26-31`）。
- **双 flavor**：`flavorDimensions "uid"` 下 standalone 与 sharedUid（`lorie-app/build.gradle:36-44`）。sharedUid 与 Termux:API 共享 com.termux UID 且 targetSdk 降到 28（`:43`，共享 UID 应用必须同版本发布）；自定义任务 VerifySharedUidProcess（`:7`）在构建期强制该变体所有组件声明同一进程，违规直接 GradleException。debug 也用固定密钥库 testkey_untrusted.jks 签名（`:46-50`）并开 R8（JNI 注册的类必须 keep，见 proguard-rules.pro）。
- **代码生成**：lorie/build.gradle 的 `generatePrefs` 任务（`:56` 起）解析 preferences.xml 按节点类型（EditText→String、SeekBar→Int、List→List、Switch→Boolean）生成强类型 `Prefs.java`（build/generated/java/，`preBuild.dependsOn` 于 :116），extra_keys_config 特判接 TermuxX11ExtraKeys 默认值；`generateShortcuts`（`:118`）从模板渲染快捷方式 XML。**改偏好先改 preferences.xml，生成的 Prefs.java 是产物不是源码。**
- **调试入口**：debug_build.yml 产出带符号 so（ndk-stack 排障）；`termux-x11-preference.in` 提供 `dump`/`restore` 命令行读写偏好；lorie 日志 tag 为 LorieNative（`InitInput.c:242`），logcat 一抓一个准。

## 7. 新人上手路径（16 步 tour 精简为 9 个里程碑）

1. **README 全景**（T01）：23 节读 About/Submodules caveat/How does it work 三节即可，重点记三种启动方式——`-xstartup`、`--` 分隔、TERMUX_X11_XSTARTUP 环境变量（`README.md:47-71`）。
2. **应用骨架**（T02）：MainActivity 如何经 AIDL 拿 fd（`MainActivity.java:746`），LorieApp 如何按 ACTION_START 广播路由 tag 实例（`LorieApp.java:130-138`）。
3. **LorieView 与偏好链**（T03）：SurfaceView 枢纽 + "preferences.xml → generatePrefs → Prefs.java → LorieView 消费"这条全仓最典型的代码生成链。
4. **触摸输入管线**（T04）：TouchInputHandler 分派 → 三策略 → InputEventSender 注入；KeyInterceptor 另走无障碍（`KeyInterceptor.java:90` FLAG_REQUEST_FILTER_KEY_EVENTS，失焦后 120 秒降载，`:96`）。
5. **跨进程双桥**（T05）：activity.cpp 28+1 个原生方法、cmdentrypoint 事件泵与 knock 握手——把 T02 的伏笔闭环。
6. **DDX 核心 + 渲染**（T06-T07）：InitOutput.c 的 Present/EXA/GLX 挂接、lorieEvent 20 余种事件（`lorie.h:129-186`）、renderer.cpp 的 gpuCopyQueue 回放与 fbconfigs.h（头注释自述：动态生成的 GLX 配置在 glxgears/glmark 上会坏，故静态化百余条）。
7. **buffer 与 SysV**（T08）：三种后端 + SCM_RIGHTS 传递 + shm/ 的 ashmem 模拟。
8. **额外按键双面**（T09-T10）：数据模型（五套 Unicode 显示映射，`ExtraKeysConstants.java:106-122`）与视图/翻译（修饰键宏展开成 X11 事件序列）。
9. **影子构建收官**（T12-T15）：shell-loader 签名校验 → xserver.patch 驯服上游 → 11 配方组装 → 双 flavor 打包。至此从一条命令到一帧画面全链贯通。

## 8. 延伸阅读

- **知识图谱**：`/usr-data/data2/repos/termux-repo/termux-x11/.understand-anything/knowledge-graph.json`（519 节点/923 边/12 层/16 步 tour，commit 29d4460b）；本仓 30 个枢纽节点中最高连接度集中在 MainActivity/LorieView/lorie.h/buffer.c 四处，即上文反复出现的四个名字。
- **DeepWiki 快照**：`~/ai/work4ai/讲透Termux/termux-x11/deepwiki/`（21/21 页 100%，2026-10-26 抓取；2.4 节 Shared memory and IPC 与本文第 5.2 小节互为印证）。
- **上游**：Xorg xserver（gitlab.freedesktop.org/xorg/xserver）——读本仓 patches/xserver.patch 时开着上游源码对照；Chromium Remoting 输入管线是 input/ 目录的血统来源；libandroid-shmem 独立子项目在 GitHub 另有上游（本仓 shm/ 为内嵌版）。
- **姊妹仓**：termux-packages 的 x11-packages/ 是 X11 应用生态的打包侧；termux-app 是宿主终端。
