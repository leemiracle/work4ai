# 07 · 触摸输入管线：TouchInputHandler 与 InputEventSender

> 对象：`lorie/src/main/java/com/termux/x11/input/`（L05 输入系统层）
> 主角：`TouchInputHandler.java`（1291 行）+ `InputEventSender.java`（324 行）；配角：InputStrategyInterface / TapGestureDetector / SwipeDetector / RenderData / InputStub
> 全部行号锚经源码现场核实（commit 29d4460b 工作树）

## 一、角色定位：反向链的 Java 侧总闸

渲染的正向链把 X 客户端的像素送上 Android 屏幕；本篇讲反向链——手指落在屏幕上，如何变成 X server 里的鼠标/触摸/键盘事件。这条链的 Java 侧总闸就是 TouchInputHandler：MainActivity 用**五路 listener** 把所有输入事件汇到它一个入口 `handleTouchEvent(view0, view, event)`（触摸 `MainActivity.java:349`、悬停 `:351`、generic motion `:352`、双路 captured pointer `:354-355`），实例本身在 `MainActivity.java:332` 构造。

血统是这个包最显眼的身份特征：`grep -rln "Chromium Authors"` 在全 Java 树命中恰好 7 个文件，全在 input/ 包内——TouchInputHandler/TapGestureDetector/SwipeDetector/RenderData（2013）、InputStrategyInterface（2015）、InputStub/InputEventSender（2016）。这套代码源自 Chromium Remoting（Chrome Remote Desktop 的 Android 客户端），Termux:X11 把"远端主机"换成了本机的 Xlorie server。加上 Termux 自研、走无障碍系统级拦截的 `utils/KeyInterceptor.java`，共同构成 L05 层的八件套。

分工沿 Chromium 原注释（`TouchInputHandler.java:54-58`）：操纵本地画布的手势（滚屏、捏合缩放）在本类处理，发给"远端"的输入交给 InputStrategyInterface 实现；InputEventSender 是"Android 事件 → InputStub 低级注入"的翻译层（`InputEventSender.java:24-27`），InputStub 七函数接口（`InputStub.java:14-48`）由 LorieView 实现（`LorieView.java:55`），经 @FastNative 方法（`LorieView.java:797-816`）落进 JNI。

## 二、内部结构：一handler 四识别器 三策略 三专用监听器

### 2.1 分派主干 handleTouchEvent（`TouchInputHandler.java:304-403`）

一次事件的完整路由顺序：

1. **手柄过滤**：`ignoreGamepadEvents` 时直接吃掉 gamepad/joystick（`:305-306`）；
2. **修饰键卫生**：真实设备事件（deviceId≥0）先 `releaseStuckModifiers` + `syncLockKeysState`（`:308-311`），把被系统吞掉 key-up 的"卡死修饰键"和锁键状态先纠正；
3. **触控板委派**：SOURCE_TOUCHPAD 的手指事件或 DeX 伪鼠标事件，整体转给嵌套的 `mTouchpadHandler`（`:315-317`）；
4. **坐标重基**：view0≠view（事件从父容器转发）时按两 view 窗口位置差平移坐标（`:319-330`）；
5. **触控笔**：TOOL_TYPE_STYLUS/ERASER → StylusListener（`:338-340`）；
6. **物理鼠标**：TOOL_TYPE_MOUSE 或 SOURCE_MOUSE/MOUSE_RELATIVE（且非 DeX）→ HardwareMouseListener（`:342-345`）；
7. **手指**：进入策略+识别器管线（`:347-399`，下详）。

### 2.2 自嵌套双实例：触控板的"分身"技巧

最反直觉的结构是 `mTouchpadHandler`：主实例构造时再 new 一个 `isTouchpad=true` 的 TouchInputHandler（`TouchInputHandler.java:225`），触控板手指事件全部委派给它。妙处在于分身内部 `mTouchpadHandler==null`，于是 `setInputMode` 的第一分支命中，策略**恒为 TrackpadInputStrategy**（`:417-419`）——无论用户把触屏模式设成什么，触控板永远按触控板语义（相对移动+tap-to-click）处理。递归在这里天然终止（`:225` 的三目表达式），避免了在单个 handler 里塞满 if-touchpad 分支。isTouchpad 还决定是否挂 cursor 同步 listener（`:198-199`，只有主实例挂）。

### 2.3 三策略（`InputStrategyInterface.java`）

策略回答"这类触摸在语义上是什么"，由 `setInputMode`（`TouchInputHandler.java:417-426`）按 `touchMode` 偏好切换，pref 值 1/2/3 对应 Trackpad/Simulated touchscreen/Direct touch（`arrays.xml:3-12`）：

- **NullInputStrategy**（`InputStrategyInterface.java:50-55`，Direct touch 模式）：四方法全空。手指事件在 `handleTouchEvent:355-356` 直接走 `mInjector.sendTouchEvent(event, mRenderData)` 透传为 XI2 触摸事件，多点触控直达 X 客户端——这正是 `:363-366` 注释解释的：该模式下禁用捏合缩放（mZoomer 不喂事件，`:365-366`），否则两根手指会同时被 X 客户端和本地缩放抢走。
- **SimulatedTouchInputStrategy**（`:62`）：触摸仿真鼠标。`onMotionEvent` 里手指位移超出 touch slop 即按下左键并让光标跟手（`:181-194`），得到"按住拖拽"效果；`onTap` 用**双击坐标复用**保证双击成功率（`:134-151`：第二次 tap 强制用第一次的坐标注入，因为两次点击中心点的距离常会让远端 OS 认成两次独立单击——注释 `:135-142` 详述此动机）。
- **TrackpadInputStrategy**（`:243`）：手机屏幕当触控板。tap 即 `sendMouseClick(button, true)`（相对坐标，`:255-257`）；`onPressAndHold` 被 `tapToMove` 偏好门控（`:260-263`），不开启时长按/双击拖动直接按下按钮。

### 2.4 四个识别器

- **mScroller**（系统 GestureDetector）：单指滚动→光标移动。长按被显式禁用（`TouchInputHandler.java:206`），注释说明否则长按后 onScroll 停发、光标卡死；
- **mZoomer**（系统 ScaleGestureDetector）：捏合缩放，quick-scale 双击拖也禁用（`:210`）避免与本类自己的双击拖处理打架；
- **TapGestureDetector**（`TapGestureDetector.java:21`）：补齐原生检测器只认单指的短板（类注释 `:18-20`）。状态机极简：DOWN 记初始位置+排 long-press 定时（`:105-112`），POINTER_DOWN 取 max 指数（`:114-117`），任一指出 slop 平方距离即取消（`:180-200`），UP 时回调 `onTap(pointerCount, x, y)`（`:128-133`）。**指数即按钮**：`mouseButtonFromPointerCount` 把 1/2/3 指映射为左/右/中键（`TouchInputHandler.java:893-904`）；
- **SwipeDetector**（`SwipeDetector.java:17`）：双指手势的 swipe/pinch 甄别器。两指位移向量的**数量积**为正判 SWIPE、为负判 PINCH（`:130-131`），一旦判定锁定到手势结束（`:88-89`）；单指未动另一指远移的场合按 PINCH 倾向处理（`:119-123`）。

四个识别器**必须都看到每个事件**（`TouchInputHandler.java:360-368` 的注释：避免短路求值导致识别器状态错乱），这是 Chromium 传下来的纪律。

### 2.5 三专用监听器

- **HardwareMouseListener**（`:995-1069`）：物理鼠标。未捕获时绝对定位（`:1024-1027`）；pointer capture 后走相对轴，累加 historical 批采样（`:1036-1039`）、按 capturedPointerTransformation 旋转（`:1042-1051`）、乘速度因子×density（`:1053-1054`）；按钮用 savedBS/currentBS 差分只发变化沿（`:1062-1066`）；
- **StylusListener**（`:1071-1154`）：触控笔全息转发——压强 ×65535（`:1144`）、倾角经 asin 投影到 ±63.5（`:1137-1138`）、方向角弧度转角度（`:1075-1080`）、按钮位图（bit1=侧键二、bit2=侧键一，`:1086-1107`，含 stylusButtonContactModifierMode 两种模式）、eraser 与 stylusIsMouse 旗标（`:1149-1150`）。无变化事件在 `:1130-1132` 去重；
- **DexListener**（`:1157-1290`）：三星 DeX 触控板非捕获模式。靠 vendor flags 魔数分流：`0x14000000`=双指滚（`:1203`，Q 以上加 CLASSIFICATION_TWO_FINGER_SWIPE 双保险）、`0x4000000`=拖拽（`:1229`）；ACTION_DOWN 无旗标无按钮则视为 tap 按下左键、UP 时释放（`:1232-1235`, `:1246-1249`）；HOVER_MOVE 悬停移动光标（`:1218-1223`）；HOVER_EXIT/CANCEL 复位全部状态（`:1261-1266`）。双击被翻译成两次完整单击（`:1278-1282`）。

## 三、外部连接

**上游**：MainActivity 五路 listener（`MainActivity.java:349-355`）；偏好链 reloadPreferences（`MainActivity.java:791` 调 `TouchInputHandler.java:461-510`）——`touchMode`（`preferences.xml:28`）决定策略，六个用户动作键 `swipeUpAction`/`swipeDownAction`/`volumeUpAction`/`volumeDownAction`/`backButtonAction`/`mediaKeysAction`（`preferences.xml:72-76,80`）经 `extractUserActionFromPreferences`（`TouchInputHandler.java:512-529`）变成 BiConsumer<Integer,Boolean> 闭包表：八种动作——切软键盘/切额外按键栏/开设置/释放指针键盘捕获/切全屏/退出/转发音量/转发媒体键（`:518-526`）。同一偏好键还有两个静态变体供通知栏复用：extractIntentFromPreferences（`:531-561`，PendingIntent 版）与 extractTitleFromPreferences（`:564-572`，资源名反射版），setupNotification（`:574-587`）组装。

**下游**：InputEventSender 的所有出口都压到 InputStub 七方法上（`InputStub.java:23-47`）：sendMouseEvent/sendMouseWheelEvent/sendKeyEvent/sendTextEvent/sendTouchEvent/sendStylusEvent/sendLockKeysState。实现者是 LorieView：`sendMouseEvent` 等 public 方法包装 @FastNative 私有方法（`LorieView.java:797-816`）；滚轮是特化（`:551-552` 把 wheel 翻成 BUTTON_SCROLL 的相对 mouse 事件）。

**与 KeyInterceptor 的协作**：`shouldInterceptKeys()`（`TouchInputHandler.java:589-591`）是 MainActivity 决定是否让无障碍服务拦硬件键的依据（`MainActivity.java:1300-1305`）；ESC 抬键自动释放捕获在 `InputEventSender.java:304-305`，与 pauseKeyInterceptingWithEsc 偏好（`:49`）联动。

**原生对岸**：JNI sendTouchEvent 把事件封成 `EVENT_TOUCH` lorieEvent（`activity.cpp:513-517`）写 socket；X server 侧 `handleTouchEvent`（`cmdentrypoint.cpp:227`）查 `TouchFindByDDXID` 去重（`:233-243`）、**把只收到 Update 没 Begin 的序列修复成 Begin**（`:245-248`）、坐标归一化到 0..0xFFFF 绝对值域（`:252-253`），最后 `QueueTouchEvents` 注入 lorieTouch 设备（`:254`）。设备侧 InitInput.c 三连 AddInputDevice 注册 mouse/touch/keyboard（`InitInput.c:272-274`），触摸屏挂 XI_TOUCHSCREEN 名（`:276`），触控笔 pen/eraser 按需启停（`:245,252`）。

## 四、数据流：三种典型旅程

**旅程 A · Direct touch 手指事件（Null 策略）**：MainActivity onTouch → handleTouchEvent 过五关到 `:355-356` → `InputEventSender.sendTouchEvent`（`InputEventSender.java:171-207`）：MOVE 事件按 pointer×history 双层循环逐点变换（`RenderData.mapScreenPoint` Matrix 逆映射 + clamp，`:181-191`）；非 MOVE 事件**只取 action pointer**（`:193-205`，注释说明全量转发会搅乱远端手势）；XI_TouchBegin/Update/End 常量 18/19/20（`:29-31`）；TouchEnd 前先补一发 TouchUpdate（`:202-203`）；`releaseMissingPointers`（`:154-161`）对 32 槽位指针表（`:152`）兜底补 End，防指针泄漏。到 native 后被 :245-248 的修复逻辑二次兜底——两侧互相不信任，双保险。

**旅程 B · Trackpad 模式单指移动**：mScroller 产 onScroll → 双指/三指分支不命中 → Trackpad 分支按 scaleTouchpad 决定是否乘 `mRenderData.scale`（`TouchInputHandler.java:712-717`）→ `moveCursorByOffset`（`:593-595`）→ `sendCursorMove(-deltaX, -deltaY, relative=true)` → `InputEventSender.java:144-146` 翻成 BUTTON_UNDEFINED 的 mouse 事件 → native 累加进光标位置。注意 `:595` 的负号：Android distance 语义是"上一次到这一次的位移"，与拖拽方向相反。

**旅程 C · 物理键盘按键**：MainActivity dispatchKeyEvent → `TouchInputHandler.sendKeyEvent`（`:937-993`）先截胡：未连接时 BACK 直接 finish（`:943-947`）；媒体/音量/BACK 三类走用户动作闭包（`:953-990`，其中鼠标 BACK 翻译成右键点击 `:978-984`）；其余落 `InputEventSender.sendKeyEvent`（`:214-309`）：FLAG_CANCELED 丢弃（`:221-224`）；ACTION_MULTIPLE 产 TextEvent（`:236-242`）；无修饰键且有 unicode 的软键盘按键走文本注入并记入 mPressedTextKeys、其 key-up 被吞掉（`:251-267`）；AltGr 布局先松再按右 Alt 包夹文本（`:244-245`, `:254-260`）；上古 @/#/*/+ 键码翻成 Shift+数字（`:274-291`）；自动重复过滤（`:296-297`）；`preferScancodes` 或带修饰键时带 scancode 注入（`:249`）——对应 XKB 物理键码路径。

## 五、设计决策

1. **识别器与策略分离**：四个识别器只回答"用户做了什么手势"（ tap/scroll/pinch/long-press ），策略回答"这手势对 X 会话意味着什么"。手势识别是平台问题（Android 定制），事件语义是产品问题（三种触摸模式），Chromium 用一个接口切开两者，Termux 因此能用同一套手势层服务三种模式。
2. **自嵌套分身替代分支地狱**：触控板事件与其余事件在"哪个策略、哪些 detector、哪些旗标"上全方位不同，复制一个 handler 实例比在每个方法里加 isTouchpad 分支干净得多；代价是两实例共享同一 injector 与 RenderData（`:225` 传同一个），状态不会分叉。
3. **isDexEvent 的宽容匹配**（`:290-302`）：注释引 issue #1011——部分蓝牙键鼠二合一把 tap 报成 SOURCE_MOUSE+TOOL_TYPE_FINGER，归入触控板手势路径（tap-to-click、多指 tap 可用）而非只转发物理按钮状态的鼠标路径。真鼠标用 TOOL_TYPE_MOUSE、真触控板报 SOURCE_TOUCHPAD，互不影响。这是"按行为聚类而非按名义类型分流"的典范。
4. **捏合缩放的增量锚定 + serial 确认**（`:627-654`, `:736-819`）：onScale 频率高于 Renderer 回报帧率，从 LorieView 上报矩形重推导会丢中间态，故 pan/zoom 状态在 Java 侧增量维护（`:728-735` 注释）；结束时光标夹回图像边缘 5%（PAN_EDGE_FRACTION=0.05，`:63`，注释要求与 renderer.cpp 的 panToCursor 边缘比例一致），并经 `view.sendSync(serial)`（`LorieView.java:765-766`）等 X server 回执，`onCursorMoveSynced`（`:647-654`）核对 serial 后才解除锚定，300ms 超时兜底（`:639-644`）。
5. **tap-to-move 的延迟点击**（`:843-846`, `:852-872`）：Trackpad+tapToMove 下单击不立即注入，挂 getDoubleTapTimeout 的消息（`:846`）；若第二指在窗口内落下则撤回单击、改走 `onPressAndHold(LEFT, true)` 进入拖拽（`:856-859`），后续 MOVE 手工喂给 onScroll（`:862-863`）。用一个超时窗口完成单击/拖拽二义性消解。
6. **触控板坐标旋转矩阵**（`:80-87`, `:671-690`, `:1042-1051`）：触控板上报物理坐标系、无视屏幕旋转，捕获模式下相对位移须按 `capturedPointerTransformation`（AUTO 用 DisplayListener 缓存的 mDisplayRotation，`:150-165`）旋转后再用；速度因子乘 density（`:1053-1054`）统一不同 dpi 手感。
7. **按钮差分三胞胎与防御性注入**：savedBS/currentBS 差分在主类（`:168-177`）、HardwareMouseListener（`:995-1011`）、DexListener（`:1170-1195`）出现三次——重复但隔离彻底，三路事件流永不相混；InputEventSender 侧再加按钮白名单（`:114-119`）、shouldBlockKeyEvent 滤掉触摸面板固件串入的伪按键（`:316-323`，BACK/HOME/APP_SWITCH 放行，`:33-37`）、releaseStuckModifiers 先删后发防重入双释放（`:83-85` 注释）。

## 六、新人提示

- **改触摸行为先改 preferences.xml**：touchMode/六用户动作/tapToMove 全在 `preferences.xml:28-80`，Prefs.java 是 generatePrefs 产物不是源码（全仓铁律，本篇 `:462-472` 的每个字段都来自它）；
- **测试矩阵至少五路**：手指、触控笔、物理鼠标、触控板（含捕获/非捕获）、DeX 触控板（捕获走 :315-317 委派、非捕获走 :349 DexListener），路由分支彼此纠缠，单测一路极易在另一路回归；isDexEvent 的判定三条件（`:298-301`）改动影响面最大；
- **魔数 flags 勘误**：`0x14000000`（两指滚动）与 `0x4000000`（拖拽）是未公开的 MotionEvent flags（`:1203`, `:1229`），Android SDK 无常量名，上游变更时 grep 这两个字面量；
- **KEY_BACK≠KEYCODE_BACK**：`:114` 的 `KEY_BACK=158` 是 USB 扫描码（键盘控制器视角），`:986` 用它区分硬件 BACK 键与软件 BACK 键码（scanCode==0），命名极易误读；
- **按钮映射表位序陷阱**：`buttons` 表里 PRIMARY→LEFT、**TERTIARY→MIDDLE**、SECONDARY→RIGHT（`:168-172`）——Android 语义 Tertiary 才是中键，直觉写 SECONDARY→MIDDLE 会反；
- **mSwipeThreshold=40×density**（`:215-219`）必须大于手势识别器的 ScaledTouchSlop，否则同一手势既算 tap 又算 swipe；
- **调试日志 tag**：设备枚举打在 "DEVICES" 与 "InputDeviceListener"（`:233,267`），热插拔键盘/笔触发 refreshInputDevices（`:264-288`）可快速验证设备识别；
- **两处坐标负号**：onScroll 的 distance 语义反向（`:693-698` 累计 `mTotalMotionY -= distanceY`；`:595` 相对移动取负），改手势代码先读注释再动手。

## 结论

TouchInputHandler 是"手势识别器 × 输入策略 × 事件注入器"三层正交组合的调度场：识别器层继承自 Android/Chromium 的成熟判定，策略层把判定翻译成三种产品语义，注入层（InputEventSender）统一翻译成 InputStub 的七个原语再经 LorieView 的 FastNative 直落 socket。读懂它的钥匙有两把：一是 handleTouchEvent 的七步路由表（§2.1），二是"策略实例随 touchMode 偏好整体切换、触控板分身恒 Trackpad"的实例几何（§2.2）。与之配套的 pinch serial 同步、tap-to-move 延迟窗、native 侧 Touch 序列修复，共同构成了一条在真实设备矩阵上被反复打磨的输入管线。
