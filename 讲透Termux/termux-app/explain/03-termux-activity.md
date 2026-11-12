# 03 TermuxActivity.java —— 主界面装配与终端交互控制器

`app/src/main/java/com/termux/app/TermuxActivity.java`（1013 行；下文锚未注明文件者均指此文件）

## 角色定位

Termux 的"门面"：整个 App 唯一的 LAUNCHER 入口（AndroidManifest.xml:52-70，`launchMode="singleTask"` :57，同时挂 LAUNCHER 与 LEANBACK_LAUNCHER 两个 intent-filter :61-70），用户点图标后看到的第一个（通常也是唯一一个）界面。图谱 14 层中属 **L08 App 主界面与终端交互层**，onboarding 定性"L08 主界面=TermuxActivity+五大控制器+设置 Fragment"（ONBOARDING.md L08 段）——本文件是那"五大控制器"的宿主与装配点。图谱节点 tags 给了四个标签：`entry-point / ui / activity / session-management`，complexity 评 `complex`。

存在理由是一个 Android 特有的结构性矛盾：**终端会话必须活得比界面久**。Activity 转屏、切后台、被系统回收都会销毁重建，而 ssh 会话里跑着的编译任务不能跟着死。所以本类实现 `ServiceConnection`（:80），自己只做三件事——装配视图栈、把 TermuxService 绑进来、把 Activity 生命周期事件转发给两个 client（TermuxTerminalViewClient :98 与 TermuxTerminalSessionActivityClient :104）。类头 Javadoc 直接链接了两篇关于 "bind service 内存泄漏" 的老文章（:70-79），点明作者的自我定位：一个必须小心持有服务引用的薄壳。

## 内部结构

**字段四组**。服务组：`mTermuxService`（:87，包级可见，client 们经 `getTermuxService()` :876 取用）；视图栈组：`mTerminalView`（:92）、`mTermuxActivityRootView`（:119）、`mTermuxActivityBottomSpaceView`（:124）、`mExtraKeysView`（:129）、`mTermuxSessionListViewController`（:139）、`mLastToast`（:149）；双 client 组（:98/:104/:134）；状态布尔组：`mIsVisible`（:155）、`mIsOnResumeAfterOnCreate`（:160）、`mIsActivityRecreated`（:167）、`mIsInvalidState`（:172）。

**onCreate 是一条 10 步装配流水线**（:198-280）：删 14 天前的崩溃报告缓存（:206）→ 加载 termux.properties（:209-210）→ 设日夜主题（:212，经 `TermuxThemeUtils.setAppNightMode` :456）→ setContentView（:216）→ 构建 SharedPreferences，失败即置 `mIsInvalidState=true` 提前 return（:220-225）→ 设边距（:227，读属性里的终端 margin :464-469）→ root view 挂 insets 监听并记导航栏高度（:229-238）→ 全屏开关（:240-242）→ 装配终端视图与双 client（:244）→ 装配工具栏/设置键/新会话键/键盘切换键四个交互件（:246-252）→ 注册上下文菜单（:254）→ **startService+bindService 双轨启动服务**（:260-266）→ 广播 "Termux 已打开"（:279）。三处失败出口全部殊途同归：置 `mIsInvalidState` 后 return（:221-225、:267-275），后续每个生命周期方法开头 `if (mIsInvalidState) return`（:288/:310/:331/:353）。

**onServiceConnected 是真正的业务起点**（:387-430，异步回调，不在 onCreate 里）。取 `((TermuxService.LocalBinder) service).service`（:390，LocalBinder 定义在 TermuxService.java:71）后走三分支状态机：①会话空且可见 → `TermuxInstaller.setupBootstrapIfNeeded`（:399，定义在 TermuxInstaller.java:65）解压 bootstrap rootfs，完成后 `addNewSession(launchFailsafe, null)` 开首个 shell（:403-406），并捕获 BadTokenException 容忍 Activity 已死（:407-409）；②会话空且不可见（服务在后台连上）→ 直接 `finishActivityIfNotFinishing()`（:411-414）；③已有会话 → 若 intent 是 Android 7.1 快捷方式的 `ACTION_RUN` 且 Activity 非重建（:419），按 extra 开 failsafe 新会话（:421-422），否则恢复存储的当前会话（:424，`getCurrentStoredSessionOrLast`）。末行 `mTermuxService.setTermuxTerminalSessionClient(...)`（:429）把会话回调挂回 Activity 侧——自此双向通道打通。注意 `setIntent(null)`（:395）：消费一次即焚，防重投递。

**广播接收器**（内部类 :941-966）监听三 action（注册于 :918-925）：崩溃通知 `ACTION_NOTIFY_APP_CRASH`、样式重载 `ACTION_RELOAD_STYLE`、权限请求 `ACTION_REQUEST_PERMISSIONS`；全部包在 `if (mIsVisible)` 门内（:946）——后台时静默丢弃。`fixTermuxActivityBroadcastReceiverIntent`（:931-939）是历史兼容层：旧版用 `EXTRA_RELOAD_STYLE="storage"` 的广播被改写成 `ACTION_REQUEST_PERMISSIONS`。

**上下文菜单系统**（:630-704）：11 个常量项（:179-190），含条件项——选中文本才显示"分享选中文本"（:638-639）、Autofill 可用才显示用户名/密码项（:640-643）、"杀进程"标签实时带 PID 且 `setEnabled(currentSession.isRunning())`（:645）。最巧的一笔是 `onCreateOptionsMenu` 钩住 `mTerminalView.showContextMenu()` 并返回 false（:655-657）——硬件菜单键直接弹长按菜单，App 不存在任何 OptionsMenu。

**收尾是一整面 getter 门面**（:812-906）：20 余个访问器把自身当服务定位器暴露给五大控制器（`getDrawer()` :836、`getTerminalToolbarViewPager()` :841 都是现场 `findViewById` 不缓存字段）。静态出口两个：`updateTermuxActivityStyling`（:911，发样式重载广播）与 `startTermuxActivity`（:1003，`FLAG_ACTIVITY_NEW_TASK` :1009，供服务从后台拉起）。

## 外部连接

图谱（1284 节点/2762 边）对该文件节点实证：**fan-in=12**（7 imports + 4 configures + 1 related）、**fan-out=63**（32 imports / 19 contains / 10 exports / 2 calls）。

**fan-in 7 条 imports 全部来自 `app/.../terminal/` 子包**：TermuxTerminalExtraKeys、TermuxActivityRootView、TermuxSessionsListViewController、TermuxTerminalSessionActivityClient、TermuxTerminalViewClient、FullScreenWorkAround、TerminalToolbarViewPager——即五大控制器互相之间靠持有 `TermuxActivity` 引用（而非直接互引）通信，本类是它们的公共上下文总线。4 条 configures 来自 AndroidManifest.xml、themes.xml、strings.xml、shortcuts.xml，1 条 related 来自布局 activity_termux.xml。

**口径勘误一**：TermuxService 实际也引用本类——`TermuxActivity.startTermuxActivity(this)`（TermuxService.java:721，由通知的 sessionAction 分支 :692/:697 触发），但图谱 fan-in 无此边。原因：两者同在 `com.termux.app` 包，无需 import 语句，而 scanner 的 imports 边靠 import 语句建立，同包引用天然漏计。

**口径勘误二**：fan-out 的 2 条 calls 边标为 TermuxActivity→TermuxService / →TermuxInstaller，但运行时调用方向恰相反（是 TermuxService 调 `TermuxActivity.startTermuxActivity` 静态方法）。图谱 calls 边是"静态依赖"口径而非运行时调用方向，读图时勿当调用图。

**fan-out 32 条 imports 分三簇**：app 模块内 5（HelpActivity/SettingsActivity/FileReceiverActivity/TermuxService/TermuxInstaller）；跨模块 UI/仿真 4（terminal-view 的 TerminalView/TerminalViewClient、terminal-emulator 的 TerminalSession/TerminalSessionClient）；termux-shared 多达 21（Logger/TermuxConstants/ExtraKeysView/权限/主题/偏好等）。结构呈"依赖全部向下（shared/视图/仿真），被依赖全部来自自己辖下的 UI 子包"——一个干净的倒挂，无环。反向注释锚亦有实证：ExtraKeysView.java:71 注释"view height is adjusted in TermuxActivity.setTerminalToolbarHeight()"、TermuxShellManager.java:27 提及本类的 mTermuxSessionListViewController。

## 数据流

**冷启动主链（点图标→shell 提示符）**：Launcher intent → onCreate 流水线至 :260-266 `startService` + `bindService`（前者让服务"无论谁绑定都运行"，见 :258-259 注释）→ 系统异步回调 `onServiceConnected`（:387）→ 首次运行会话空（TermuxService.java:873 `isTermuxSessionsEmpty`）→ `setupBootstrapIfNeeded`（TermuxInstaller.java:65）解压 Alpine rootfs 与 bootstrap → `addNewSession(false, null)`（TermuxTerminalSessionActivityClient.java:364）——该方法内含 MAX_SESSIONS=8 上限对话框（:45/:368）、工作目录继承当前会话 cwd 或默认目录（:378-384）、调 `service.createTermuxSession` 真正 fork PTY（:385）→ `setCurrentSession`（:293）→ `TerminalView.attachSession`（TerminalView.java:290）把仿真器接到渲染 View。此后进入 01/02 篇已拆的热路径：按键经 TerminalView 写 PTY，shell 回吐字节流经 ByteQueue → `TerminalEmulator.append` 状态机 → onDraw 上屏。

**后台拉活回程**：用户点通知的 sessionAction → TermuxService.java:716 `startTermuxActivity` 先验 Android 10+ 悬浮窗权限（:719-720，无权只留通知不拉 Activity）→ `TermuxActivity.startTermuxActivity(this)`（:1003）经 NEW_TASK 重进前台（singleTask 复用实例，走 onNewIntent 之外的既有会话恢复分支 :424）。

**样式热重载环**：termux:style 插件或属性变化 → 静态 `updateTermuxActivityStyling`（:911）发 `ACTION_RELOAD_STYLE` 广播 → 接收器 :946 可见性门 → `reloadActivityStyling`（:968）重读属性、刷新 extra keys 按钮大写与高度（:972-975）、重设边距（:981）→ `recreateActivity=true` 时 `recreate()`（:995-997）整树重建——注释言明代价与保留物："会销毁包括所有存储变量与视图在内的一切，extra keys 输入文本、终端会话与 transcript 将保留"（:992-994）。

**存储权限旁路**：`requestStoragePermission`（:768-790）开子线程做权限检查（:769），授予后顺手 `setupStorageSymlinks`（:782，TermuxInstaller.java:277 建 ~/storage 软链）；`onActivityResult`/`onRequestPermissionsResult` 双入口（:793-808）都以 `isPermissionCallback=true` 回调同法，避免重复弹窗（:773 requestCode 传 -1）。

## 设计决策

1. **薄 Activity、厚 Client**。本类自身几乎不含终端交互逻辑：键盘/手势/参数在 TermuxTerminalViewClient，会话 CRUD/重命名/杀进程确认在 TermuxTerminalSessionActivityClient，本类只装配并把 onStart/onResume/onStop 成对转发（:292-296/:312-316/:335-339）。对照常见"God Activity"写法（把全部逻辑塞进 Activity），收益是 recreate() 与配置变更后代码路径完全不变——重建的只是壳，client 随壳重建、逻辑无状态化沉淀在各 client。代价是阅读时要在三四个文件间跳。

2. **startService+bindService 双轨而非纯绑定**（:258-266）。纯 bindService 方案下 Activity 解绑即服务销毁，会话全灭；加 startService 后服务生命周期独立于界面，用户按返回键 `finishActivityIfNotFinishing()`（:603-608 经 onBackPressed，抽屉开着先关抽屉）后 shell 继续在通知栏里跑。这是全 App "后台不死"能力的地基。

3. **mIsInvalidState 早退而非直接 finish**。onCreate 中段（偏好构建失败 :221、服务启动失败 :273）已弹 AlertDialog 提示杀进程，若立即 finish()，后续仍会到达的生命周期回调会在半初始化对象上跑。选择置标志位 + 每个生命周期方法开头早退（:288/:310/:331/:353），让残缺实例安静走完销毁流程。

4. **双向防泄漏，且不信对方**。Activity 侧 onDestroy 主动 `unsetTermuxTerminalSessionClient()` 并置空引用（:355-359）；但 TermuxService 在 onUnbind 里还有第二道防线——注释明言 "Since we cannot rely on TermuxActivity.onDestroy() to always complete, we unset clients here as well"（TermuxService.java:195-199）。服务持 Activity 引用是经典泄漏/崩溃源，两层都拆。

5. **会话恢复的防重投递设计**。`setIntent(null)`（:395）消费即焚 + `mIsActivityRecreated`（:419，由 onSaveInstanceState 写入 :374）联合判断：Android 7.1 桌面快捷方式的 `ACTION_RUN` intent 在 Activity 重建时会被系统重新投递，不拦截就会每次转屏多开一个会话（:416-418 注释描述的正是这个 bug 模式）。

6. **文档漂移小勘误**：`mIsVisible` 注释称 "If between onResume() and onStop()"（:152-153），但置 true 实际在 onStart()（:290）——真实可见窗口比注释宽一截（onStart 先于 onResume）。广播注册窗口（onStart :301 / onStop :343）与代码行为一致，与注释不符。改代码前以行为为准。

## 新人提示

1. **`mTermuxService` 在 onCreate 结束时仍是 null**。bindService 的回调是异步的（:263-265 注释），onCreate 与 onServiceConnected 之间隔着一整个消息循环。任何"在 onCreate/onStart 里直接 `getTermuxService()` 干活"的新代码都是定时 NPE——现有代码的防御姿势是 client 内判空早退（如 addNewSession :366-367 `if (service == null) return`）。需要服务就绪才做的事，放进 onServiceConnected 分支或其触发的回调里。

2. **recreate() 后的状态只有两个 outState 键**：工具栏文本输入（`ARG_TERMINAL_TOOLBAR_TEXT_INPUT` :192，save :554-562/restore :522-526）与"已重建"标志（`ARG_ACTIVITY_RECREATED` :193，save :374/restore :202-203）。其余一切（含 `mExtraKeysView`）都靠 onCreate 流水线重建——extra keys 视图由 ViewPager 的 PageAdapter 在 `instantiateItem` 里重新 inflate 并经 `setExtraKeysView` 回填（TerminalToolbarViewPager.java:41-49，本类 :832-834）。给 Activity 加"跨重建要保住"的新状态时，必须同步动 onSaveInstanceState 与恢复点两处，漏一处就是静默丢数据。

3. **新生命周期方法别忘了 mIsInvalidState 守卫**。类里 onCreate/onStart/onResume/onStop/onDestroy 五个 override 全部以 `if (mIsInvalidState) return` 开头（:288/:310/:331/:353）。新增 override（如 onNewIntent、onConfigurationChanged）若不加守卫，会在半初始化实例上执行——onCreate 里 :221-225 与 :267-275 两条失败路径都可能产生这种实例。同类陷阱：广播接收器靠 `mIsVisible` 门（:946）丢弃后台广播，新加 action 时若需要"后台也处理"要明确绕开这个门，别默认照抄。

---

*字数（不计空格）：8587；锚数量：129 处实例 / 113 个唯一（TermuxActivity.java 裸行锚 116 + 跨文件 .java:NN 锚 13）；抽验 3 锚全命中（TermuxActivity.java:419=ACTION_RUN 与 mIsActivityRecreated 联合判断行、TermuxService.java:721=`TermuxActivity.startTermuxActivity(this)`、TerminalToolbarViewPager.java:46-49=instantiateItem 经 setExtraKeysView 回填 extra keys 视图）。*
