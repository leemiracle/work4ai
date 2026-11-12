# 06 · LorieView.java — GUI 进程侧的渲染画布与 JNI 枢纽

> `lorie/src/main/java/com/termux/x11/LorieView.java`（827 行），知识图谱 L04「Java Lorie 应用层」枢纽节点。未标文件的行号锚均指本文件，全部锚经源码现场核实（commit 29d4460b）。

## 1. 角色定位

LorieView 是双进程架构里 **GUI 进程（Java 侧）的全能枢纽**：继承 SurfaceView 并实现 InputStub（:55），一个对象拧住四个世界——Android 窗口图形（Surface 生命周期与测量布局）、原生渲染（`mNativeContext` :65 指向 activity.cpp 的 LorieViewResources，内含 GLES 渲染器与连接 socket）、输入注入（InputStub 事件族，被 InputEventSender 直接调用）、IME 与剪贴板桥接。

"枢纽"不是修辞：Java 侧对原生层的调用几乎全聚于此——**28 个 native 方法声明**（:702-822，24 个 @FastNative + 4 个 @CriticalNative），与 activity.cpp 的 JNINativeMethod 表严格一一对应（`activity.cpp:412` 的 methods[] 恰好 28 项，`:555` RegisterNatives 绑定）；反向另有 5 个 Java 方法被原生回调（第 3 节）。改渲染、改输入、改 IME 任何一条线都路过此文件。

## 2. 内部结构

**① 状态字段（:56-81）**：`rendererZoom`（100-400%）、`p`（Point，**X 屏幕尺寸**，X11 坐标系而非视图尺寸）、四个 Rect（contentInsets 嵌入区 / availableRect 可绘区 / viewport 图像落位 / inputViewport 输入映射区）、inputTransform Matrix、`dimensionsFrozen`、`commitedText`（仓内拼写就是单 t，:81，grep 别写成 committed）。

**② IME 假编辑器 mConnection（:82-296）**：文件最大的匿名类。困境写在注释里——X server 无法探查 X 窗口内聚焦元素是否可编辑（:85-86），只能把视图伪装成"只有一个空格"的编辑框骗 IME（getEditable 恒返 null :87-89；光标前后恒返空格 :145-146——句号会让 gboard 停止联想）。replaceText 是 composing 模拟心脏：新旧文本前缀比较，退差量补增量，避免全删重打（:208-230）；deleteSurroundingText 把删除翻成 DEL 按键对（:169-197）；setSelection 双路兼容三星 DPAD 与 gboard（:232-252）。

**③ Surface 回调（:297-312）**：surfaceChanged 先把 Surface 递给原生（:301），再用 **getMeasuredWidth/Height**（:302-303，非回调参数）触发 updateViewport；surfaceDestroyed 传 null 通知原生释放（:310）。

**④ 初始化与销毁**：实例初始化块（:316-332）注册回调、`nativeInit()`（:319）、设焦点；onDetachedFromWindow 调 nativeDestroy 并清零句柄，防悬挂 JNI 调用（:334-339）。

**⑤ 几何引擎**：`getDimensionsFromSettings`（:370-406）按偏好三模式算 X 屏尺寸——scaled 百分比反除 / exact 固定 WxH / custom 兜底 1280x1024（:394-396）；adjustResolution 开启时按物理横竖屏翻转（:402-405）。`setCvtDimensions`（:409-414）对齐 libxcvt 的 CVT 水平粒度 8 并特判 1366x768（:412-413）。`getInputTransform`（:416-422）三步矩阵：平移掉 viewport 原点→缩放到 X 坐标系→平移到源起点。`freezeDimensions`（:458-465）配合画中画（:791-795）：悬浮时 X 屏尺寸不变、图像缩放，zoom 临时压 100 但保留变量以便恢复。

**⑥ 按键与剪贴板**：`imeBuggyKeys` 五键集（DEL/CTRL×2/SHIFT×2，:555-561）+ keyReleaseHandler 治 IME 吞 release：PreIme 预发 50ms 延迟 release（:578），真 release 到达则撤销（:589-593）。`setClipboardText`（:612-619，原生回调）写入后时间戳加 150ms 防回环（:615-618）；`requestClipboard`（:622-633，原生回调）**无论有无内容必须应答**——X 客户端阻塞等 SelectionNotify，空串也要回（:628-629）。

**⑦ 缩放与同步**：`adjustRendererZoom/ByFactor`（:728-738）钳 100-400 后下发；捏合锚点（:741-748）让平移跟手指不跟光标；`getRealCursorPosition`（:751-754）把一个 jlong 拆高低位还原 PointF——两次坐标查询合成一次 JNI 往返。同步屏障（:756-774）见第 4 节。

## 3. 外部连接

**向下（Java→native，28 方法分五簇）**：
- **生命周期簇（4，:702-726）**：nativeInit/nativeDestroy/surfaceChanged/startLogcat。surfaceChanged 直通 `renderer.setWindow`（`activity.cpp:420-423`）；startLogcat 把 logcat fd 接进 X server 进程；
- **几何渲染簇（7，:705-715）**：setViewport（直通 `renderer.setViewport`，`activity.cpp:425-428`）、setRendererZoom、setZoomAnchor/clearZoomAnchor、setFollowCursorPan、setFiltering、getCursorPosition、sendWindowChange；
- **输入簇（7，:798-816）**：sendMouseEvent/sendTouchEvent/sendStylusEvent/requestStylusEnabled/sendLockKeysState/sendKeyEvent（:813，唯一带返回值，X server 可拒收）/sendTextEvent；
- **剪贴板簇（3，:706-708）**：setClipboardSyncEnabled/sendClipboardAnnounce/sendClipboardEvent；
- **连接全局簇（7，:716-822）**：connect（:720）/connected/requestConnection/sendSync + 无实例参静态 CriticalNative 双子 getLastInputTimestamp/markUserActivity（:821-822）。connect(-1)（`MainActivity.java:730`）与 connect(fd.detachFd())（`MainActivity.java:749`）是 AIDL 拿到 X 连接 socket 后的交接点。

**向上（native→Java，5 回调）**：`setRendererViewport`（:445-455，由 `renderer.cpp:160` 的 reportViewport 调用，带 8 字段全等去重 `renderer.cpp:165-168`）把渲染器**实际使用**的视口回传，post 主线程（:447）后更新输入映射；`setClipboardText`（`activity.cpp:231`）与 `requestClipboard`（`activity.cpp:243`）服务 X11 剪贴板协议；`resetIme`（:690，`activity.cpp:278`）在 X 窗口焦点变化时重置 IME；`onSyncReply`（:771，`activity.cpp:287`）是同步屏障回执。

**横向（Java 侧）**：Callback 接口（:59-61）仅 inputTransformChanged 一法——`MainActivity.java:359` 注册，落点 `TouchInputHandler.java:405` 喂给 RenderData 坐标矩阵，是"渲染实际视口→输入系统"唯一通路；`setCallback` 注册后立刻 `triggerCallback`（:341-344）保证首帧变换不缺席。reloadPreferences（:601-609）消费生成的 Prefs.java。静态块 `System.loadLibrary("Xlorie")`（:824-826）是地基。

## 4. 数据流

**① Surface 生命线**：Android 变更 Surface → mSurfaceCallback（:300）→ JNI surfaceChanged（:704）→ `renderer.setWindow`（`activity.cpp:423`）→ 渲染线程重建 EGL 窗口；销毁对称传 null（:310）。:302-303 故意用测量尺寸而非回调参数——浮窗/嵌入场景两者可能不同步，以视图测量为准。

**② 几何协商闭环（本文件最精巧的链）**：onMeasure（:545-548）、setContentInsets（:486-492）、setObscuredBottom（:473-479）、偏好变更……全汇入 `updateViewport`（:494）单漏斗：扣 insets 得可用区（:499）→ 未冻结则 getDimensionsFromSettings 定 X 屏尺寸（:510）→ 按需保持宽高比（:516-521）→ 软键盘遮挡下图像居中、只留滚动余量（:525-530）→ **双下发**：setViewport 告诉渲染器画在哪（:537）+ sendWindowChange 告诉 X server 屏幕多大（:440，含刷新率 :431 与显示器名 builtin/dex/external :433-438，原生侧打包 EVENT_SCREEN_SIZE 写 connFd，`activity.cpp:495`）→ X server RandR 换屏 → 渲染器按新视口绘制后 reportViewport 回传 → setRendererViewport（:445）更新输入映射 → Callback 通知 TouchInputHandler。**输入变换取自渲染器实际视口而非请求值**是闭环要害——zoom/pan 偏差由回传自动纠正（:531-536）。

**③ 事件注入（反向链）**：TouchInputHandler 翻译 MotionEvent → InputEventSender 调本类 send 事件族（:797-816，全 @FastNative）→ activity.cpp sendEvent 写 connFd → X server 进程 handleLorieEvents（`cmdentrypoint.cpp:262`）翻译成 X 输入事件。

**④ 同步屏障**：触控板光标流需确认事件已被实际应用（`TouchInputHandler.java:199` 挂 listener、`:818` 发 serial）→ sendSync（:765）→ EVENT_SYNC 入队 → X server 处理完回 EVENT_SYNC_REPLY（`cmdentrypoint.cpp:494`）→ onSyncReply（:771）→ mSyncListener。一次往返实现软件背压。

**⑤ 帧率节流（requestAnimationFrame 语义）**：仓内没有字面的 requestAnimationFrame——等价机制是跨进程共享状态里的 **drawRequested/waitForNextFrame 标志对**（`lorie.h:228`、`lorie.h:250`）。链路：X server damage 判脏 → drawRequested=TRUE 并 signal（`InitOutput.c:594-598`）→ GUI 进程渲染线程 shouldWait 检查（`renderer.cpp:1122-1126`）→ redrawLocked 合成一帧后 **waitForNextFrame=true**（`renderer.cpp:1082`）→ X server 进程侧 AChoreographer 每 vsync 回调（`cmdentrypoint.cpp:216`，`InitOutput.c:800-806` 自续期）QueueWorkProc 唤起 lorieRedraw → **waitForNextFrame=false**（`InitOutput.c:568`）放行下一帧。`lorie.h:248` 注释说透动机：eglSwapInterval(1) 下不阻塞等显示，但也不愿每 vsync 白画多于一张全屏 quad——**每垂直同步最多合成一帧**。Java 侧 surfaceChanged/setViewport 等 JNI 入口走 withStateLock 宏（`renderer.cpp:49-56`）同样置 drawRequested 并 signal，天然汇入同一节流。

## 5. 设计决策

- **公开 API 不露原生指针**：:718 注释明言——public 方法不带 ptr，内部转发到带 ptr 重载（connect/connected/startLogcat/requestConnection 四组均此模式），调用方永不必管句柄生死。
- **@FastNative/@CriticalNative 分级**：4 个静态方法升 CriticalNative 连隐式 JNIEnv*/jclass 都省（`activity.cpp:470` 附近注释专门提醒）；getLastInputTimestamp/markUserActivity 是高频心跳路径（`MainActivity.java:1103` 空闲判定、:1042/:1054 保活）。
- **updateViewport 单漏斗 + 幂等守卫**：setContentInsets（:487）、setObscuredBottom（:474）、freezeDimensions（:459）全带无变化早退，避免布局风暴反复触发两趟跨进程往返。
- **IME 假编辑器换通用性**：X11 没有"询问焦点控件可编辑性"的通路（:85-86），在 Java 侧演戏的代价是键盘方言适配（gboard 空格戏法 :139-146、IME 吞 release :571-597），换来任意 X 应用零改动获得输入法支持。
- **协议级正确性细节**：剪贴板 150ms 偏移防回环（:618）、requestClipboard 必答防 X 客户端悬挂（:628-629）、CVT 粒度 8 的 1366 特判（:412-413，否则渲染器 buffer 尺寸校验 `renderer.cpp:949-956` 持续报 mismatch）。

## 6. 新人提示

1. **分清三套坐标系**：p.x/p.y 是 X11 屏幕逻辑尺寸（传给 X server），viewport/getMeasuredWidth 是 Android 视图物理尺寸（渲染器落位），inputViewport/inputSource* 是两者映射（输入用）。搞混是改 updateViewport 时最常犯的错。
2. **文件里有两个 surfaceChanged**：Java 回调实现（:300）与 native 方法声明（:704）同名，前者调用后者，看签名区分。
3. **加 native 方法三步契约**：LorieView 声明（带 @FastNative）→ activity.cpp methods[] 注册（`activity.cpp:412`）→ proguard keep 规则覆盖。缺一运行时即 UnsatisfiedLinkError。
4. **拼写陷阱**：字段 `commitedText`（单 t，:81）、AIDL `IRemoteCmdImterface`（Imterface，仓内自带笔误）——搜索按源码原样拼。
5. **调试入口分层**：输入问题从 mConnection（:82）入手；几何/黑屏打日志在 updateViewport（:494）；性能转 02-renderer.md——本文件只是节流标志入口，合成循环在 renderer.cpp。关联：JNI 全景 05-jni-bridges.md，connect(fd) 的 AIDL 链 04-main-activity.md，共享结构 01-init-output.md。
