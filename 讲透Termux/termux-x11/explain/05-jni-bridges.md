# 05 · activity.cpp + cmdentrypoint.cpp：JNI 双入口桥

> 精讲对象：`lorie/src/main/cpp/lorie/activity.cpp`（586 行）与 `lorie/src/main/cpp/lorie/cmdentrypoint.cpp`（699 行），知识图谱 L03「JNI/Binder 跨进程桥接层」双节点。未标文件的行号锚指这两个文件之一（文内用 `act:NNN` 记 activity.cpp、`cmd:NNN` 记 cmdentrypoint.cpp），Java 侧锚 `LorieView.java:NNN` / `CmdEntryPoint.java:NNN` / `MainActivity.java:NNN`，协议锚 `lorie.h:NNN`，全部经源码现场核实（commit 29d4460b）。

## 一、角色定位：一个 .so，两个进程，两条 JNI 通路

termux-x11 的双进程架构（onboarding 第 4 节反复强调的那把钥匙）落到 JNI 层，就是这对文件：**activity.cpp 是 GUI 进程（包名 `com.termux.x11`）的原生侧**，把 LorieView 的渲染/输入/剪贴板调用翻译成 socket 事件；**cmdentrypoint.cpp 是 X server 进程（Termux 命令行经 app_process 拉起）的原生侧**，引导 Xorg 启动并把 socket 事件翻译回 X 输入事件。

先钉死一个最容易被想错的事实：**两个进程加载的是同一个 `libXlorie.so`**，而且 `JNI_OnLoad` 全仓只有一个，长在 activity.cpp（`act:388`）。加载方式不同——GUI 进程走标准 `System.loadLibrary("Xlorie")`（`LorieView.java:825`，static 块）；X server 进程没有 ApplicationInfo 上下文，app_process 环境里 loadLibrary 的搜索路径不适用，于是 `CmdEntryPoint.initEntryPoint()` 自己拼 `"lib/" + (is64Bit ? SUPPORTED_64_BIT_ABIS[0] : SUPPORTED_32_BIT_ABIS[0]) + "/libXlorie.so"`（`CmdEntryPoint.java:199`），用 classloader 资源定位出 APK 内路径后 `System.load(libPath)`（`CmdEntryPoint.java:205`）。位数判断是因为 universal APK 同时装着 32/64 两套库，而宿主 app_process 的位数必须与被 dlopen 的 so 严格一致，否则直接 dlopen 失败退出 134（`CmdEntryPoint.java:206-209`）。

`JNI_OnLoad` 被两种进程各跑一次，且无条件注册**三张表**：LorieView 的 28 个方法（`act:412-552`，`act:555` RegisterNatives）、MainActivity 的 1 个（`act:574-580`）、CmdEntryPoint 的 5 个（`act:582` 转调 `cmd:680` 的 `registerCmdEntryPointNatives`）。GUI 进程里 CmdEntryPoint 的方法注册了但闲置，X server 进程里 LorieView 的 28 个方法同样如此——一个 .so 统一注册，两侧都齐，这是"共用二进制"换来的冗余。区分进程身份的唯一开关是 `strcmp(__progname, "com.termux.x11")`（`act:391`）：只有 GUI 进程（进程名即包名）会把 stdout/stderr dup2 进管道、由后台线程逐行转投 logcat（`act:393-409`）；X server 进程的 stderr 保持原样，所以 `cmd:141`、`cmd:201` 的 `dprintf(2, ...)` 才能直通 Java 侧捕获。

## 二、内部结构

### 2.1 activity.cpp：GUI 侧的 28 方法表 + ALooper 事件泵

**全局缓存四组**（`act:39-58`）：`MainActivity`（class + `clientConnectedStateChanged`/`resetIme` 两个 jmethodID + `lastServerHeartbeat` jfieldID）、`Charset`/`CharBuffer`（剪贴板字节转 String 的两步桥）、`ActivityOptions`（freeform 反射）。全部在 `nativeInit` 首次调用时惰性初始化（`act:140-153`），`FindClassOrDie`/`FindMethodOrDie`（`act:76-100`）找不到即 `FatalError`，宁死不静默。

**`LorieViewResources`**（`act:62-74`）是本文件的灵魂重构：Renderer、GUI 线程 JNIEnv、LorieView/MainActivity 的全局引用、`connFd`、`destroyed` 标志，全部捆成 per-instance 一体。`act:24-25` 的 `sendEvent` 宏注释挑明动机——"the connection fd is per-instance state, not a process global"：多实例（-tag 每显示器一实例）下每条连接互不干扰。分配用 placement new（`act:155` 的 malloc + 构造），销毁走显式析构 + free（`act:414-419`）。构造函数里 `AttachCurrentThread` 拿到 GUI 线程 JNIEnv（`act:164-165`）、NewGlobalRef 锁住 view 与 activity（`act:166-171`）、先 `connect(-1)` 占位（`act:173`）。`onDetachedFromWindow` 触发 Java 侧 `nativeDestroy(mNativeContext)`（`LorieView.java:337`），实例生命周期与视图严格对齐。

**`connect(jint fd)`**（`act:302-322`）是连接状态的唯一写口：旧 fd 先摘（removeFd + close + `renderer.setSharedState(nullptr)` + `removeAllBuffers()`，`act:303-309`）；新 fd 用 `ALooper_addFd` 挂到当前线程（GUI 主线程）的 ALooper 上，回调 lambda 转发进 `xcallback`（`act:312-313`）；随后立刻发一条 `EVENT_RENDERER_WAKEUP_COND` 并把 renderer 的条件变量 fd 经 `ancil_send_fd` 送过对岸（`act:316-318`）——注释强调 "resent on every reconnect"（`act:315`），重连必须重发。

**`xcallback`**（`act:198-300`）就是 GUI 侧事件泵，与 Android 主线程 Looper 同栖一巢。ERROR/HANGUP 分支做断连清理并回调 `clientConnectedStateChanged`（`act:199-209`）；正常分支 `read` 出一个 `lorieEvent`（定长 union，`lorie.h:128-186`），按 type 分发八个 case：CLIPBOARD_SEND/REQUEST（§四）、SHARED_SERVER_STATE（ancil 收 memfd 后 mmap 成共享状态，`act:246-262`）、ADD_BUFFER（收 LorieBuffer 句柄交 renderer，`act:264-272`）、REMOVE_BUFFER、WINDOW_FOCUS_CHANGED（触发 `resetIme`，`act:277-280`）、HEARTBEAT（写 `lastServerHeartbeat` 字段喂看门狗，`act:281-284`）、SYNC_REPLY（回调 `onSyncReply(int)`，`act:286-289`）。处理完用 `ioctl(fd, FIONREAD)` 查剩余字节，超过一个事件就 `goto again` 排空（`act:294-296`），减少 looper 唤醒次数。

**28 方法表**（`act:412-552`）按功能分五簇：渲染参数（surfaceChanged/setViewport/setRendererZoom/setZoomAnchor/clearZoomAnchor/setFollowCursorPan/setFiltering/getCursorPosition）、连接管理（connect/connected/requestConnection/startLogcat）、输入注入（sendMouseEvent/sendTouchEvent/sendStylusEvent/sendKeyEvent/sendTextEvent/sendLockKeysState/requestStylusEnabled）、剪贴板（setClipboardSyncEnabled/sendClipboardAnnounce/sendClipboardEvent）、杂项（nativeInit/nativeDestroy/sendWindowChange/sendSync/getLastInputTimestamp/markUserActivity）。表内大量条目直接写成立即调用的 lambda（C++17 风格），`r->destroyed` 前置守卫防 use-after-free。

### 2.2 cmdentrypoint.cpp：X server 侧的引导 + 输入线程事件泵

**`start()`**（`cmd:56-225`，注册名 `"start"` 签名 `([Ljava/lang/String;)Z`，`cmd:682`）是 X server 的产房，Java 构造器一进来就调（`CmdEntryPoint.java:53-55`，失败即 `System.exit(1)`）。它先锁住 CmdEntryPoint 实例的全局引用与三个回调 jmethodID：`sendBroadcast`/`sendBroadcastDelayed`/`setDocumentTag`（`cmd:60-65`），然后走一条九步环境整理流水线：TracerPid 探测防 LD_PRELOAD 干扰调试器（`cmd:66-87`）；Java String[] 转 `char** argv` 且 `argv[0]="Xlorie"`（`cmd:89-99`）；CPU 亲和性钉到高编号半数核（`cmd:101-110`）；可选 fork logcat（`cmd:112-118`）；无 tracer 且未设 `XSTARTUP_LD_PRELOAD` 时注入 `libtermux-exec.so`（`cmd:123-125`，proot 环境下会被跳过的注释写得很清楚）；TMPDIR 修正——adb 给的 `/data/local/tmp` 被显式 unset（`cmd:128-129`），依次探测 `/tmp`、Termux usr/tmp，全失败则返回 JNI_FALSE（`cmd:138-143`）；拼 Xtrans 的 Unix socket 路径 `$TMPDIR/.X11-unix/X`（`cmd:151-152`）；字体路径按容器 root 探测（`cmd:157-174`）；XKB_CONFIG_ROOT 三态探测——chroot 相对路径、proot 的 xkeyboard-config-2、Termux native 路径（`cmd:176-196`）。最后 `pthread_create` 拉起 X server 线程：AttachCurrentThread 后 `exit(dix_main(argc, argv, ...))`（`cmd:219-223`）——dix_main 不返回，这一行就是命令进程的真正归宿。AChoreographer 帧回调在进 dix_main 前已挂好（`cmd:214-216`）。

**`handleLorieEvents`**（`cmd:262-481`）是 X server 侧事件泵，注册进 Xorg 自己的输入线程（详见 §四连接链）。`X_NOTIFY_ERROR` 时摘 fd、关连接、关剪贴板同步、清空 buffer 注册表（`cmd:267-276`）。正常路径同样 FIONREAD 排空（`cmd:477-479`），13 个 case 处理"客户端→服务器"方向的事件。**泵内最要紧的纪律是线程转交**：凡是触碰 X server 内部状态的 case，一律 `QueueWorkProc` 投回 X server 主线程执行再 `lorieWakeServer()` 唤醒，代码里七处 "This must be done only on X server thread" 注释（`cmd:288`、`cmd:389`、`cmd:417`、`cmd:428`、`cmd:443`、`cmd:452`、`cmd:466`）——SCREEN_SIZE、TOUCH、KEY/UNICODE、CLIPBOARD_ANNOUNCE/SEND、GPU_COPY_DONE、SYNC、LOCK_KEYS_STATE 全走这条路；MOUSE 与 STYLUS 则因 `QueuePointerEvents` 本身线程安全而就地入队（MOUSE 分支 `cmd:350-383`、STYLUS 分支 `cmd:305-345`）。KEY/UNICODE 分支还有一手打包技巧：keycode/state 或 unicode codepoint 压进一个 `uintptr_t`（低位 tag 位区分类型，`cmd:386-387`），免去堆分配地穿过队列。

**寄生函数群**（`cmd:483-562`）：`lorieSendClipboardData`/`lorieSendSyncReply`/`lorieSendHeartbeat`/`lorieRequestClipboard`/`lorieSendSharedServerState`/`lorieRegisterBuffer`/`lorieUnregisterBuffer`/`DDXNotifyFocusChanged`——全是 InitOutput.c/clipboard.c 等 X server 侧代码的出口，共同形态是"若 conn_fd 有效则 write 一条事件（可附带 ancillary fd）"。`conn_fd` 是 `__LIBC_HIDDEN__ volatile` 进程全局（`cmd:39`），与 GUI 侧的 per-instance connFd 恰成镜像（§五）。

**`getXConnection`**（`cmd:564-578`）与 **`lorieListenForKnocks`**（`cmd:619-678`）是两条握手通路的主角，§四展开。**`abort`/`exit` 覆盖**（`cmd:692-698`）是一记狠招：把 libc 的两个退出函数替换成裸 `_exit`，因为 Xorg 大量内部错误路径会调 `FatalError→exit`，而 app_process 宿主里跑 Java 运行时的 atexit 清理会直接炸——`reportFatalError`（`cmd:602-615`）就是给 Java 侧的对称入口：连接还没建立时（`cmd:603` 的 conn_fd 守卫）把错误字符串 QueueWorkProc 交给 X server 线程以标准 FatalError 路径收尾。

## 三、外部连接：与 Java 双子及协议中枢的对应

**LorieView.java ↔ act 方法表逐条对齐**：Java 侧 28 个 native 声明集中在 `LorieView.java:702-826`，修饰符分布是全表 `@FastNative`、四个 `@CriticalNative`（connected :723、requestConnection :819、getLastInputTimestamp :821、markUserActivity :822）。签名一一对应，例如 `connect(long ptr, int fd)`（`LorieView.java:720`）对 `{"connect", "(JI)V"}`（`act:464`）；被 native 反向回调的 Java 方法也都在 LorieView 里备好：`setClipboardText`（`LorieView.java:612`，注释 "It is used in native code"）、`requestClipboard`（:622）、`resetIme`（:690，KDoc 注释 "It is called from native code, not from Java" 在 :687）、`onSyncReply`（:771，SyncListener 接口 :756）。nativeInit 在实例初始化块里调用（`LorieView.java:319`），`mNativeContext` 这个 long 句柄是 Java→native 的唯一凭证。

**CmdEntryPoint.java ↔ cmd 五方法**：`start/getXConnection/getLogcatOutput/reportFatalError` 四个普通 native（`CmdEntryPoint.java:180-183`）加 `@CriticalNative connected()`（:184），注册表在 `cmd:681-687`。`connected()` 无参——X server 进程全局只有一条 conn_fd，这也是它能做 CriticalNative 的原因。

**fd 如何跨进程**：X server 进程的 CmdEntryPoint 是 `ICmdEntryInterface.Stub`（`CmdEntryPoint.java:32`），MainActivity 经 `ICmdEntryInterface.Stub.asInterface(ibinder)` 拿代理（`MainActivity.java:711`），`service.getXConnection()` 取回 ParcelFileDescriptor（`MainActivity.java:746`），再 `getLorieView().connect(fd.detachFd())`（`MainActivity.java:749`）把整数 fd 递进 native。Binder 驱动在事务里自动完成 fd 的跨进程转译（等价 SCM_RIGHTS），于是 §2.1 的 socketpair 两岸各持一端。断链时 MainActivity 用 `connect(-1)` 复位（`MainActivity.java:730`）。

**lorie.h 是两泵共用的协议中枢**：`PORT 7892`（`lorie.h:18`）、knock 暗号 `MAGIC "0xDEADBEEF"`（`lorie.h:20`）、21 种有效事件枚举（`lorie.h:104-126`）、定长 union `lorieEvent`（`lorie.h:128-186`）。两泵消费的事件集合几乎互补：GUI 侧 xcallback 只处理"服务器→客户端"八种，server 侧 handleLorieEvents 只处理"客户端→服务器"十三种，唯一双向重叠的是 CLIPBOARD_SEND——剪贴板内容两个方向都要流。**加一种事件要同时动三处**：lorie.h 枚举、双侧 switch、至少一个发送方。

## 四、数据流：三条生命线

**① 连接建立**。X server 侧 dix_main 就绪后 `OsVendorInit` 解析出端口与 -tag，回调 `lorieListenForKnocks`（`cmd:619`，触发点见 `InitOutput.c`）——先 `setDocumentTag` 回报标签（`cmd:623`），再在 7892 上 bind/listen（`cmd:637-649`，SO_REUSEPORT 兜底），`SetNotifyFd` 挂 accept 回调（`cmd:651`）：收到对端 write 的 MAGIC 前缀匹配就 `sendBroadcast` 唤醒/定向对应 tag 的 Activity（`cmd:668-672`）。对端敲门的正是 GUI 侧 `requestConnection`（`act:103-137`，@CriticalNative）：非阻塞 connect 127.0.0.1:7892，20ms poll 超时（`act:118`），ECONNREFUSED 静默忽略（服务器没起是常态，`act:124`），成功即写 MAGIC（`act:127`）。这条 knock 通路只传暗号不传数据；真正的事件通道要等 MainActivity 经 Binder 调 `getXConnection`（`cmd:564`）：socketpair 出 AF_UNIX 双端，`client[1]` 经 QueueWorkProc 在 X server 主线程里 `InputThreadRegisterDev(client[1], handleLorieEvents, nullptr)` 并置 `conn_fd`（`cmd:569-574`），`client[0]` 包成 ParcelFileDescriptor 还给 Java（`cmd:577`）。此后 GUI 侧 `connect(fd)` 挂 ALooper 并回赠 renderer 唤醒 fd（`act:316-318`），X server 侧在 EVENT_RENDERER_WAKEUP_COND 里 ancil 收下、交给 `lorieSetRendererWakeupCond`（`cmd:435-439`）——GPU 拷贝完成后 X server 才有能力踢醒对面渲染线程。

**② clipboard 通道**（双方向四条路，本文件对最精彩的一组对称）：

- **GUI→X 内容直发**：LorieView 调 `sendClipboardEvent(ptr, byte[])`（`act:483-492`）——写一条 `clipboardSend` 头（count=长度）紧跟裸字节 `write`；server 泵 CLIPBOARD_SEND 分支读头后补读 count 字节（`cmd:423-426`），QueueWorkProc 交 `lorieHandleClipboardData`（`cmd:427-431`）注入 X selection。
- **GUI→X 宣告**：`sendClipboardAnnounce`（`act:479-482`）发 EVENT_CLIPBOARD_ANNOUNCE；server 泵转交 `lorieHandleClipboardAnnounce`（`cmd:415-421`），X 客户端粘贴时才反向要数据。
- **X→GUI 数据请求**：X server 需要内容时发 EVENT_CLIPBOARD_REQUEST；GUI 泵收到后回调 Java `requestClipboard()`（`act:242-244`），Java 读 Android ClipboardManager 并把文本经上面的直发路回传（`LorieView.java:622-626`）。
- **X→GUI 内容推送**：server 调 `lorieSendClipboardData`（`cmd:483-490`，同样"头+裸字节"两跳写）；GUI 泵 CLIPBOARD_SEND 分支（`act:217-240`）calloc 接收（`__builtin_add_overflow` 防长度溢出，`act:221`），然后用 nativeInit 缓存好的 Charset/CharBuffer 桥把字节解码成 jstring——`Charset.forName("UTF-8").decode(NewDirectByteBuffer(...))` 再 `CharBuffer.toString`（`act:232-237`）——回调 `setClipboardText` 写进系统剪贴板（`LorieView.java:612-616`，顺带把 lastClipboardTimestamp 推后 150ms 防回环）。总开关 `setClipboardSyncEnabled` 走 EVENT_CLIPBOARD_ENABLE（`act:475-478` → `cmd:412-413` `lorieEnableClipboardSync`）。

**③ 一次触摸 + sync 屏障 + 心跳**。TouchInputHandler 产出 MotionEvent → LorieView.sendTouchEvent（`LorieView.java:801`）→ `act:513-518` 打包 touch 事件写入 socket；server 泵的 EVENT_TOUCH 分支深拷贝后 QueueWorkProc 给 `handleTouchEvent`（`cmd:298-304`，函数体 `cmd:227-260`）：坐标 clamp 到屏幕、去重（touch 活跃且坐标未变则丢弃，`cmd:236-243`）、漏发 TouchBegin 的修补（`cmd:245-247`），归一到 0..0xFFFF 后 `QueueTouchEvents`。sync 屏障用于测试与状态确定性：GUI 发 `sendSync(serial)`（`act:455-458`）→ server 泵在 X server 线程 `mieqProcessInputEvents()` 排干队列后 `lorieSendSyncReply`（`cmd:449-461`，注释明言这是 "the server has applied every event sent so far" barrier）→ GUI 泵 EVENT_SYNC_REPLY 回调 `onSyncReply(serial)`（`act:286-289`）。心跳则是 server 周期 `lorieSendHeartbeat`（`cmd:499-504`）→ GUI 泵 SetLongField 更新 `MainActivity.lastServerHeartbeat`（`act:281-284`），Java 看门狗靠它判活。断连对称清理：GUI 侧摘 ALooper 清 renderer 回调 `clientConnectedStateChanged`（`act:199-209`），server 侧摘输入线程清 buffer 表（`cmd:267-276`）。

## 五、设计决策

**为什么一个 .so 吃两个进程**：把 LorieView 桥与 CmdEntryPoint 桥拆成两个 so 看似更干净，但两者共享 lorie.h 协议、buffer 传递原语与 X server 链接体（cmdentrypoint.cpp 依赖 dix/globals.h，`cmd:19-29`，只能在链入 xserver 的 so 里编译），拆开就要么复制协议要么引入第三个公共 so；统一成 libXlorie.so 后，一个 JNI_OnLoad 注册三张表（`act:412-582` 区间）即可，代价只是每个进程多注册一组闲置方法与 `__progname` 一次 strcmp。`registerCmdEntryPointNatives` 做成被 JNI_OnLoad 调用的普通函数（`act:582`）而非 cmdentrypoint 自己的 JNI_OnLoad，正是同一 so 只能有一个 JNI_OnLoad 的直接后果。

**@CriticalNative 的选位**：四个 Critical（connected/requestConnection/getLastInputTimestamp/markUserActivity，`act:470-473`、`act:103`、`act:546-551`）+ server 侧 connected（`cmd:686`）清一色是"只碰原始类型、不碰 JNIEnv"的极短函数——CriticalNative 硬性要求 static 且参数全是原始类型，换来跳过 JNI 状态切换的最小调用开销，适合每帧高频或 Looper 上的快速判活；其余全表 @FastNative 折中。`act:102`、`act:469` 两处注释专门解释这个差别。

**两级队列纪律**：server 泵跑在 Xorg 输入线程（InputThreadRegisterDev 注册，`cmd:570`），而 XKB 状态、mieq、present vblank 队列只能 X server 主线程碰——于是泵内"就地 QueuePointerEvents（mieq 自带锁）+ 状态修改走 QueueWorkProc"的混合策略，五处线程注释就是这纸契约的正文。KEY/UNICODE 的 uintptr_t 打包（`cmd:386-387`）与 Touch 的深拷贝（`cmd:299-301`）都是为无泄漏穿越队列。

**connFd per-instance vs conn_fd 进程全局的不对称镜像**（`act:67` vs `cmd:39`）：GUI 进程可同时跑多个 tag 实例、各持一条连接，所以连接状态必须住进 LorieViewResources；X server 进程一进程一 display，连接天然单条，全局 volatile 反而让 483-562 一整排寄生发送函数无需携带上下文。同一协议两种粒度，各自贴合进程模型。

**杂项三刀**：`sendTextEvent` 逐 UTF-8 字符 mbrtowc 解码，回车翻译成 KEY_ENTER+8 的按下/抬起对（X keycode = evdev code + 8，`act:370-371`、`act:540`），每字符 `usleep(2500)` 节流模拟真人打字速度（`act:379`）；`JNI_OnLoad` 里的 freeform 查找特意放进一次性 pthread（`act:557-570`），完成后把 methodID 存全局、以 `nativeSetLaunchWindowingModeFreeform` 注册给 MainActivity（`act:575-578`，值 5 即 WINDOWING_MODE_FREEFORM）；`startLogcat` fork+dup2+PR_SET_PDEATHSIG 保证 logcat 子进程随 GUI 进程陪葬（`act:328-341`）。

## 六、新人提示

**调试抓手**：native 日志 tag 统一 "LorieNative"（`act:23`、`cmd:35`）；X server 侧设 `TERMUX_X11_DEBUG` 环境变量可让 start() fork logcat（`cmd:112-118`）、`getLogcatOutput` 开 stderr 管道（`cmd:580-600`），GUI 侧 `startLogcat` 把 fd 接进来（`act:324-342`）。改协议先读 lorie.h 枚举（`lorie.h:104-126`），事件枚举追加在尾部以免破坏两侧行为对齐。

**三个现场小勘误**：①`act:106` 注释说 "timeout to 20 msec" 而 `act:118` 注释说 "50ms"，实际 poll 参数是 20ms——两处注释打架，以代码为准；②AIDL 文件名 `IRemoteCmdImterface.aidl` 的 "Imterface" 是上游自带拼写错误，生成类名跟着错，搜索时别写成 Interface；③`cmd:102-110` 的 CPU 亲和性把 X server 钉在编号较高的一半核上，读代码时别误以为它在让核——它在避开 GUI 进程常驻的低编号核。

**改动清单**：新增 native 方法须同步三处——LorieView.java 声明（`LorieView.java:702-826`）、act 方法表（`act:412-552`）、proguard-rules.pro 的 keep 规则（R8 会剥掉反射/JNI 引用的方法，onboarding 第 6 节）；新增事件类型按 §三末尾的"三处联动"走；动剪贴板逻辑先画一遍 §四②的四条路，漏掉 `lastClipboardTimestamp` 那类防回环细节就会出现剪贴板自我复制。

**上手路径**：先读 `JNI_OnLoad`（`act:388-585`）建立三张表的地图 → 读 `cmd:56-225` 的 start 看环境整理 → 拿 §四①的连接建立链当主线把 Binder/knock/ALooper/InputThread 四种机制串一遍 → 最后用 clipboard 四条路验证自己已经能在两文件间自由往返。至此 L03 层闭环，第 04 篇（MainActivity）的 AIDL 伏笔与第 02 篇（renderer）的唤醒 fd 消费端都接上了。
