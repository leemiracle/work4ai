# 04 · MainActivity：双进程架构里的"窗口管家"

> 文件：`lorie/src/main/java/com/termux/x11/MainActivity.java`（1326 行，L4 Java 应用层）
> 行号锚经源码现场核实（commit 29d4460b）。

## 1. 角色定位：不渲染一帧像素，却决定一切何时开始

在双进程架构（Java GUI 进程 + app_process 拉起的 X server 进程）里，MainActivity 是用户可见那一半的总调度：**X 会话的宿主窗口——管理 Activity 实例与 Android 窗口、把 X server 的连接 fd 交给 LorieView、把按键与偏好变化路由到正确组件，自己不画任何 X11 内容**。像素在 LorieView（SurfaceView）与 renderer.cpp，事件翻译在 TouchInputHandler/InputEventSender。

三个事实钉住分量：①连接中枢——Binder 经 LorieApp 广播路由过来后，`service.getXConnection()`（`MainActivity.java:746`）拿到 X 连接 socket fd，`getLorieView().connect(fd.detachFd())`（`:749`）才让像素流动；②多实例注册表——每个 `-tag` 显示器窗口一个实例，全登记在静态弱引用表 `instances`（`:145`）；③全仓最高连接度四枢纽之一，10+ 文件回调它的公开方法。

## 2. 内部结构：静态注册表 + 四组职责域

### 2.1 多实例管理

**tag 解析与转发**（`MainActivity.java:150-164`）：tag 来自启动 Intent 的 data——`termux-x11-window://<tag>` URI 取 host，或裸 schemeless 值（`-d <tag>` 产物）。普通 MainActivity 收到带 tag 的 Intent 时，`relaunchAsTaggedIfNeeded` 会 finish 自己并转启 `MainActivityTagged`（`:157-163`）。后者只是空子类（`:1324-1325`），但 Manifest 赋予完全不同的窗口语义：`taskAffinity=""` + `documentLaunchMode="intoExisting"` + `autoRemoveFromRecents`（`AndroidManifest.xml:39,41,43`），每 tag 一个独立 recents 条目、同 tag 复用；主入口则是 `taskAffinity=".MainActivity"` + `launchMode="singleInstance"`（`AndroidManifest.xml:17,22`），全局唯一。

**弱引用注册表**（`:145`）：弱持使"窗口死掉未注销也不被钉在内存里"。四查询：getInstance(tag)（`:171`）、getFocusedInstance()（`:177`，找 hasWindowFocus）、getInstances()（`:187`）、getFocusedOrAnyInstance()（`:235`）。onCreate 注册（`:309`），onDestroy 以 `ref.get() == this` 身份比对清除（`:424`），避免 tag 复用误删。

**按键归属表**（`:247-283`）：每实例持 `Set<Integer> pressedKeys`，配套 `getInstanceWithPressedKey`（`:258`）找到"认为该键还按着"的窗口——用户按住 Ctrl 切窗口再松开时，UP 事件必须路由回原窗口，否则 X 会话里 Ctrl 永远按下。

### 2.2 连接域：tryConnect 状态机 + 心跳看门狗

`connectToService(IBinder)`（`:710-724`）是 LorieApp 广播的落点：先把 logcat fd 交给 `LorieView.startLogcat`（`:715-717`，X server 进程日志由此回流），再 tryConnect。`tryConnect()`（`:733-763`）是自恢复状态机：无 service 则 `requestConnection()` 触发 knock（`:740`）后 250ms 轮询（`:765-768`）；有 service 则取 fd 连接并 reloadPreferences（`:746-753`）；异常一律置空 service 重试（`:756-761`）。断线由 `disconnectService()`（`:726-731`）以 `connect(-1)` 通知 native，`clientConnectedStateChanged()`（`:1260-1288`）刷新 UI 并再 tryConnect 自愈。

**心跳看门狗**（`:837-848`）：200ms 一查、3 秒静默判死；静默只亮 `no_server_signal` 覆盖层（`:846`），不杀连接——死亡判定交给 Binder linkToDeath（`LorieApp.java:163-170`）。线程停滞补偿见第 5 节。

### 2.3 按键协议：双入口汇聚 handleKey

普通路径是 LorieView 的 `dispatchKeyEventPreIme` 调 `activity.handleKey(event)`（`LorieView.java:584`）；无障碍路径是 KeyInterceptor 系统级拦截硬件按键后路由（`KeyInterceptor.java:105-129`）。

`handleKey`（`MainActivity.java:1007-1011`）：`filterOutWinKey` 开启且是 Meta 键（`KEYCODE_META_LEFT/RIGHT` 或 `isMetaPressed()`）直接丢弃——把 Win 键还给 Android；否则转发 `mLorieKeyListener`，本体是 `mInputHandler.sendKeyEvent(e)`（`:333-341`），由 InputEventSender 翻成 X11 事件。Termux EK bar 行为下且事件来自虚拟设备时 `mExtraKeys.unsetSpecialKeys()`（`:338-339`）——不偷全尺寸外接键盘的专用键。

**拦截闸门** `shouldInterceptKeys()`（`:1300-1306`）：无 handler、无窗口焦点、或 EK 文本框聚焦时返回 false——无障碍拦截让位 Android 自身输入。KeyInterceptor 侧 `recheck()`（`KeyInterceptor.java:79-97`）按"有焦点或有按住的键"决定挂 `FLAG_REQUEST_FILTER_KEY_EVENTS`，失焦后 120 秒延迟降载（`:96`，注释说明：切 service info 会拖住拖拽进程，无法下拉通知栏）。MainActivity 在 `onWindowFocusChanged` 驱动 recheck（`:1037`）。无障碍自动启停在偏好回调：开则 `KeyInterceptor.launch(this)`——写 `Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES` 需 WRITE_SECURE_SETTINGS，失败弹 ADB 授权指引（`KeyInterceptor.java:26-51`）；关且持权限则 shutdown（`:801-804`）。UP 事件的跨窗口归属（KeyInterceptor.java:107、`:124`）直接消费 2.1 的按键归属表。

**软键盘仲裁**：`setExternalKeyboardConnected`（`:1308-1316`）由 TouchInputHandler 设备扫描回调（`TouchInputHandler.java:287`）——检测到外接键盘后按 `showIMEWhileExternalConnected` 偏好决定 EK 文本框是否还弹软键盘。

### 2.4 窗口/偏好域

`applyWindowSettings()`（`:1128-1186`）处理 fullscreen/hideCutout/强制方向/cutout/常亮/沉浸；fullscreen 或 cutout 变化时直接 `recreate()`（`:1139`），因为"布局计算会错且无效，没找到简单可靠的修法"（注释原话）。EK bar 几何在 `setTerminalToolbarViewLayout()`（`:918-956`）：左右放置时整条 bar 旋转 ±90°（`:946`）；`applyContentInsets()`（`:961-983`）把 EK bar 占位与 IME 高度换算成 LorieView 内容内缩。鼠标/触控笔辅助按钮（`:613-708,430-520`）把触摸直接翻成 `sendMouseEvent`、以模式位 1/2/4 表左/中/右。画中画（`:1211-1230`）：PIP 偏好开、有权限、已连接时进 PiP；宽高比按系统范围 clamp——上下限读系统资源 `config_pictureInPictureMin/MaxAspectRatio`（`:117-118`），越界时**截断**而非四舍五入（`:1222-1223`，防落回范围外被拒）。PiP 中断连即 finish（`:1269-1272`）——从 PiP 无法回正常尺寸，只能关窗。

## 3. 外部连接：谁调它、它调谁

**被依赖**（grep 实证）：KeyInterceptor 按键路由与 pressedKeys 维护（`KeyInterceptor.java:105-129`）；LorieApp 四路由——ACTION_START 落 connectToService（`LorieApp.java:168`）、ACTION_STOP 落 finishAffinity（`:177-179`）、ACTION_PREFERENCES_CHANGED 遍历实例刷偏好（`:181-186`）、ACTION_CUSTOM 执行用户动作（`:187-192`）；TouchInputHandler 回调 setExternalKeyboardConnected/setCapturingEnabled/toggle*（`TouchInputHandler.java:287,518-521`）；视图层经 `findActivity` 反查宿主（`ExtraKeysView.java:220`，LorieView.java:69 同款手法）；LoriePreferences 找活动实例执行命令（`LoriePreferences.java:585`）。**依赖**：LorieView、TouchInputHandler + InputEventSender（构造于 `:332`）、LorieApp（prefs 与 pendingConnections）、LoriePreferences（preferences 按钮，`:324`）、native libXlorie（`:1320-1322`）。

**DeX 与快捷方式的准确位置**：SamsungDexUtils **不**由 MainActivity 直接调用——DeX Meta 键捕获经 `setCapturingEnabled` → `TouchInputHandler.java:442-443` 走 `SamsungDexUtils.dexMetaKeyCapture`（反射 `SemWindowManager.requestMetaKeyEvent`，静态块探测 `SamsungDexUtils.java:16-27`）；MainActivity 只是持有 handler 并转发驱动（`:1295-1298`）。桌面快捷方式全在资源层：launcher 长按图标出现 Preferences 项（模板 `lorie/src/main/templates/xml/shortcuts.xml:9-15`，经 `AndroidManifest.xml:35` 挂载），直达 LoriePreferences 不经 MainActivity；SECONDARY_HOME 类别（`AndroidManifest.xml:33`）让它出现在桌面模式应用抽屉。

## 4. 数据流：三次生命周期叙事

**冷启动**（onCreate，`:295-409`）：relaunch 检查 → 注册实例表 → 取 prefs → 布局与四按钮（`:324-327`）→ 构造输入管线并挂五路触摸监听（含 `requestUnbufferedDispatch` 降批处理延迟，`:343-356`）→ 摘取 LorieApp 里等着的 `pendingConnections` 直连（`:386-388`，覆盖"Activity 未起 X server 已敲门"的时序）→ tryConnect 成功则挂 **PreDraw 首帧门**（`:390-394`）：`mOnPredrawListener` 在未连接时 onPreDraw 返回 false 挡住整帧绘制，连接成立即撤门；另有 500ms 兜底（`:393`），服务起不来也不白屏卡死。这是 Surface 生命周期绑定的第一环：MainActivity 不碰 Surface，但用 PreDraw 门保证 LorieView 首帧一定晚于 X 连接建立。

**连接后稳态**：像素链路完全绕开 MainActivity（LorieView ↔ renderer）；常驻工作三件——200ms 心跳巡检（onResume 启动、onPause 撤销，`:833-834`）；屏幕常亮检查（onUserInteraction → `LorieView.markUserActivity`，`:1049-1057`，按"模式分钟数−系统超时"的空闲判定动态保持/释放 FLAG_KEEP_SCREEN_ON）；onConfigurationChanged（`:1016-1031`，Manifest 声明全量 configChanges 故不重建）收键盘、重算 EK bar。

**偏好变更联动全链**：LoriePreferences 改动 → ACTION_PREFERENCES_CHANGED 广播 → LorieApp 遍历实例 `a.onPreferencesChanged(key)`（`LorieApp.java:181-186`）→ 100ms 去抖（`MainActivity.java:770-776`）→ `onPreferencesChangedCallback`（`:779-819`）依次：PiP 一致性检查、applyWindowSettings、inputHandler/lorieView/extraKeys 三连 reloadPreferences、Win 键过滤与 KeyInterceptor 启停、辅助按钮与 EK bar 透明度、刷新常驻通知。偏好每次经 `app.getPrefs(this)` 重取引用（`:780`）——LorieApp 支持双偏好存储，偏好源可能运行期切换。

## 5. 设计决策：五处值得抄的工程判断

1. **弱引用注册表而非强引用单例**（`:145`）：目录只是索引不是 owner，Activity 生死由系统管；清除用身份比对而非 tag 匹配（`:424`）。
2. **recreate() 逃离布局污染**（`:1134-1141`）：承认平台怪癖选最朴素解法，好过在错误状态上打补丁。同类还有 letterbox 检测（`:1155-1162`）：显示器拒绝旋转时 letterbox 而非旋转，记录 orientationDeniedAt 临时退回 UNSPECIFIED，等显示器变化再重试。
3. **心跳与死亡判定分离**：应用层 3 秒静默只亮提示（`:844-846`），真断连交给 Binder linkToDeath——native 卡顿与进程死亡是两种故障。线程停滞补偿（`:840-842`）再把"看门狗自己迟到"与"服务器静默"分开。
4. **按键归属的窗口路由**（`:247-283`）：解决的 bug 场景写在 KeyInterceptor 注释（`KeyInterceptor.java:121-122`）——Win+Tab 或按着 Ctrl 切窗口时 UP 必须回原窗口；120 秒延迟降载（`:96`）同样是踩坑产物。
5. **时序防御不用锁**：pendingConnections（`:386-388`）解决"Binder 先到、Activity 后到"的排队；PreDraw 门+500ms 兜底（`:390-394`）解决"连接未成、首帧已至"。都是"迟到者自取/超时放行"的最终一致思路。

## 6. 新人提示：上手顺序与五个易错点

**阅读顺序**：先 onCreate（`:295-409`）看组件装配 → 跟 tryConnect（`:733-763`）理解连接状态机 → 读 clientConnectedStateChanged（`:1260-1288`）看断线自愈 → 最后读 onPreferencesChangedCallback（`:779-819`），全 App 偏好生效的总闸。

易错点：

1. **onBackPressed 是故意的空实现**（`:1188-1190`）——Back 不退出 X 会话（先被 LorieView 拦成 X 事件）；退出走 stub 页 Exit 按钮或 ACTION_STOP 广播。
2. **改窗口参数留意 recreate() 路径**：fullscreen/cutout 变化触发整 Activity 重建（`:1134-1141`），调试断点会失效；PiP 下刻意跳过重建，重建会把窗口带出 PiP。
3. **多窗口调试用静态查询**：getFocusedInstance/getInstances（`:177-195`）是理解按键路由与广播去向的钥匙；logcat "Got new ACTION_START intent"（`LorieApp.java:167`）是连接路由发生的标志。
4. **Prefs 是生成代码**：`prefs.touchMode.get()` 等强类型访问来自 build 期 generatePrefs 从 preferences.xml 生成的 Prefs.java——改偏好先改 XML，别手改生成物。
5. **无障碍服务手动开关**：`adb shell pm grant <pkg> android.permission.WRITE_SECURE_SETTINGS` 是自动启用 KeyInterceptor 的前置（`KeyInterceptor.java:44` 弹窗文案即此命令）；没授权时改偏好只弹提示，拦截不生效。

**下一篇**：05 篇进入 LorieView——本文所有 `getLorieView()` 调用的落点，Surface 生命周期、knock 协议与视口变换在那里闭环。
