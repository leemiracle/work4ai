# 02 · renderer.cpp：双进程架构里的 GLES2 渲染线程

> 精讲对象：`lorie/src/main/cpp/lorie/renderer.cpp`（1319 行，知识图谱 L1 X server 原生核心层）。
> 锚基准：`renderer.cpp:NNN` 指 `/usr-data/data2/repos/termux-repo/termux-x11/lorie/src/main/cpp/lorie/renderer.cpp`，同目录其余文件（lorie.h/buffer.c/InitOutput.c/activity.cpp/cmdentrypoint.cpp）同理，xserver.patch 在 `patches/`。全部锚经源码现场核实（commit 29d4460b）。

## 一、角色定位：GUI 进程的像素出口

termux-x11 是双进程架构：X server 住在 Termux 命令行进程里算像素，而 Android 的图形出口（Surface）只能住在有窗口的 Java GUI 进程里。renderer.cpp 就是 GUI 进程侧那条**独立的 GLES2 渲染线程**——把 X server 进程写好的 LorieBuffer 内容贴上 Android Surface，是"X 客户端 → 屏幕"六站链的最后一棒。每个 LorieView 持有一个 `Renderer`（结构体在 `lorie.h:276`，没有独立 renderer.h），由 activity.cpp 构造并 `renderer.init(callerEnv, view)`（`activity.cpp:161`）。

三点定性：①**消费者**——不生产像素，只做纹理导入、FBO 拷贝、视口/缩放几何与光标合成；②**跨进程共享状态持有者**——mmap 同一块 `lorie_shared_server_state`（`lorie.h:202`）与 X server 进程互斥读写；③**能力探测器**——启动前用 scratch 实例探明设备的 BGRA 采样与 CPU/GPU 内存一致性（`renderer.cpp:563`），决定 legacy drawing 与 GPU Present offload 两个降级开关。与同层的 InitOutput.c 分工明确：那边管屏幕、RandR、Present、EXA 的 X server 侧逻辑，这边只对 Android Surface 负责——两个文件隔着进程边界，靠共享状态与事件 socket 对话。文件顶部三宏 `EGL_EGLEXT_PROTOTYPES`/`GL_GLEXT_PROTOTYPES`/`__ANDROID_UNAVAILABLE_SYMBOLS_ARE_WEAK__`（`renderer.cpp:12-14`）配合弱符号 `eglGetNativeClientBufferANDROID`（`renderer.cpp:37`，API 26 才导出），让同一个 so 在 minSdk 24 老设备上照常加载。

## 二、内部结构：一条线程、两块 surface、三条链表

### 线程生命周期

`init()`（`renderer.cpp:309`）是唯一入口：缓存 JavaVM、LorieView 全局引用与 `setRendererViewport` 方法 ID（`renderer.cpp:313-317`），创建**进程间共享条件变量**——memfd 区域 mmap 出 `PTHREAD_PROCESS_SHARED` 的 `pthread_cond_t`（`renderer.cpp:324-331`），fd 留着日后发给 X server；最后 `pthread_create` 拉起线程（`renderer.cpp:337`），入口即 `initThread()`。

`initThread()`（`renderer.cpp:243`）一次性建好渲染环境：AttachCurrentThread（线程名 "LorieRendererThread"）→ `eglGetDisplay`/`eglInitialize`/`eglBindAPI`（`renderer.cpp:258-266`）→ `eglChooseConfig`（先按 `EGL_ALPHA_SIZE,0` 选，失败改 alpha=8 重选，`renderer.cpp:268-271`；configAttribs 定义在 `lorie.h:327-335`：EGL_WINDOW_BIT + GLES2 + 888）→ GLES2 context（ctxattribs `renderer.cpp:187-189`）→ **造默认窗口**并 `eglCreateWindowSurface`+`eglMakeCurrent`（`renderer.cpp:277-285`）→ 编译两套纹理 shader（RGBA 与 BGRA swizzle 版，`renderer.cpp:123-141`，bgra 版仅片元着色器采样加 `.bgra` 后缀）→ 分配光标纹理，随后进入 `threadLoop()`（`renderer.cpp:305`）。

`destroy()`（`renderer.cpp:342`）置 `stopping=true`、signal 共享 cond、`pthread_join`，最后 `ctx` 复位为 `EGL_NO_CONTEXT`（`renderer.cpp:353`）——`init()` 开头的 `if (ctx) return;` 守卫（`renderer.cpp:310`）由此放行未来的重初始化，Renderer 可随 LorieView 反复生死。

### 双 surface 设计

本文件最巧的工程点：EGL context 没有 current surface 会被部分驱动销毁，而 surfaceless context 扩展在怪设备上不可靠。解法是造一个**永不销毁的 1x1 假窗口**（`createDefaultWindow`，`renderer.cpp:198`）：API 24+ 用 1x1 `AImageReader`（listener 里 acquire 即 delete，`renderer.cpp:202-209`），更老的设备退到 Java SurfaceTexture+Surface（`renderer.cpp:223-240`）。真窗口销毁时 context 永远切回 defaultSfc（`renderer.cpp:656,727`）；假窗口与假 surface 活到 renderer 寿终（注释 `renderer.cpp:191-197` 说明了为何不用 pbuffer：不想同时要求 pbuffer+window 双能力 config）。真实窗口经 `setWindow()`（`renderer.cpp:620`）异步提交为 `pendingWin`，渲染线程在 `refreshContext()`（`renderer.cpp:709`）里重建 EGLSurface：先 `eglSwapBuffers` 归还出队 buffer 再销毁旧 surface（`releaseWinAndSurface`，`renderer.cpp:652-655`）→ `eglCreateWindowSurface` → `eglMakeCurrent` → `eglSwapInterval(0)`（`renderer.cpp:745`）→ 置 `surfaceAvailable=drawRequested=cursor.updated=true` 强制重绘一帧（`renderer.cpp:749`）→ `glViewport`（`renderer.cpp:751`）。

### 三条缓冲链表与自旋锁

`addedBuffers`/`buffers`/`removedBuffers` 三条 xorg_list（`renderer.cpp:254-256`）构成缓冲三态生命周期：刚从 X server 注册（`addBuffer`，`renderer.cpp:580`）→ 已 attach 到 GL → 待释放。`bufferLock` 是自旋锁（临界区极短且渲染线程不能睡，`renderer.cpp:334`）。关键规则：**GL 对象线程亲和**——未 attach 的缓冲可在调用方线程直接释放（`renderer.cpp:590-592`），已 attach 的必须搬进 removedBuffers、由渲染线程在循环尾部释放（`renderer.cpp:596-599,1189-1193`）。

`threadLoop()`（`renderer.cpp:1134`）是状态机主循环：`shouldWait()` 门控下睡眠（`renderer.cpp:1138`）→ 醒来依次处理 stateChanged（切换共享状态 mmap，旧块 `munmap`，`renderer.cpp:1143-1163`）、windowChanged（refreshContext）、addedBuffers 批量 `attachToGL`（`renderer.cpp:1170-1174`）→ 解锁 → 二选一执行 `redrawLocked` 或独立 `applyPendingGpuCopies`（`renderer.cpp:1182-1187`）→ 重新拿锁。退出清理全在本线程（GL/EGL 线程亲和，注释 `renderer.cpp:1198`）：删程序/纹理、销毁 surface 与 context、`ANativeWindow_release`、munmap 共享 cond、DetachCurrentThread（`renderer.cpp:1210-1223`），但**故意不调 `eglTerminate`**——EGLDisplay 是进程级驱动连接非实例资源（注释 `renderer.cpp:1218-1219`），多实例场景下谁先销毁谁就会连累别的 Renderer。

## 三、外部连接：四条通道

**① JNI 上游**：activity.cpp 的 28 个原生方法中 9 个直接落在 Renderer 上——`surfaceChanged→setWindow`、setViewport/setZoom/setZoomAnchor 等（`activity.cpp:420-448`）；连接断开时 `setSharedState(nullptr)+removeAllBuffers()`（`activity.cpp:203-204`）。Java 侧反向回调仅一条：`reportViewport()` 去重后调 `LorieView.setRendererViewport`（ID 缓存 `renderer.cpp:317`，调用 `renderer.cpp:171`），把"画了哪块源、贴到屏幕哪块"回传给触摸坐标换算。

**② 跨进程共享内存**：`lorie_shared_server_state` 由 X server 创建、经 `setSharedState` 同步移交（`renderer.cpp:568`，等 `stateChangeFinishCond` 确认切换完）。其中 `lock`+`lockingPid` 是**进程间 pthread 互斥**（动机注释 `lorie.h:203-208`：两进程同画根窗口会撕裂）；`gpuCopyQueue` 是单生产者单消费者环形队列（容量 8，`lorie.h:191`；语义注释 `lorie.h:212-216`：X server 只推进 writeIndex，渲染线程只推进 readIndex 与 completedSerial）。

**③ 反向唤醒**：渲染线程睡眠用的 `stateCond` 住在共享 memfd 里，fd 经 `ancil_send_fd(connFd, renderer.getWakeupCondFd())` 发给 X server（`activity.cpp:318`），X server 侧 `rendererCond` 指针换成这块映射（`InitOutput.c:186`）后，`lorieRedraw`（`InitOutput.c:604`）、光标移动（`InitOutput.c:432,444`）、GPU 拷贝入队（`InitOutput.c:1071`）都能**跨进程 signal** 直接叫醒渲染线程。

**④ 回执通道**：GPU 拷贝批次完成后 `notifyGpuCopyDone()` 往连接 socket 写 `EVENT_GPU_COPY_DONE`（`renderer.cpp:145-150`），X server 事件泵在 `cmdentrypoint.cpp:441` 消费——否则 Present 要等下一次 vblank 轮询才知道源 pixmap 已可释放，客户端动画会白白少一拍。

## 四、数据流：一帧从 gpuCopyQueue 到屏幕

### 前置：纹理从哪来（LorieBuffer 双轨）

X server 把 LorieBuffer 句柄经 SCM_RIGHTS 发到 GUI 进程注册，渲染线程在 `LorieBuffer_attachToGL`（`buffer.c:442`）里导入，分两条轨道：AHardwareBuffer 后端走 `eglCreateImageKHR(EGL_NATIVE_BUFFER_ANDROID)` + `glEGLImageTargetTexture2DOES`（`buffer.c:448,456`）**零拷贝**，X server 写内存即 GPU 可采样；CPU 内存后端（LORIEBUFFER_FD）attach 时只 `glTexImage2D` 占位不传像素（`buffer.c:460`），真正上传在每帧 `LorieBuffer_bindTexture` 的 FD 分支 `glTexSubImage2D`（`buffer.c:469-470`）。FD 后端每帧上传，AHB 后端导入一次终身免拷——同一帧里两条轨道的纹理采样行为完全一致，差异只在谁付搬运成本。

### 正帧：redrawLocked 流水

`redrawLocked()`（`renderer.cpp:921`）每帧执行：

1. **先清欠账**：GPU 拷贝队列非空先走独立入口（`renderer.cpp:928-929`），避免根窗口未就绪时饿死无关窗口的拷贝。
2. **找根缓冲**：按 `rootWindowTextureID` 查 buffers，查不到再查 removedBuffers——让"画完即删"的缓冲最后显示一次（`renderer.cpp:933-936`）。
3. **尺寸门**：期望宽按 `CVT_H_GRANULARITY=8`（`renderer.cpp:16`）对齐比对（`renderer.cpp:947-950`），不符则**显式清 drawRequested** 再挂起（`renderer.cpp:956-957`），否则 shouldWait 忙转重试同一块错尺寸缓冲（注释 `renderer.cpp:954`）。
4. **几何计算**：zoom 100-400% 钳制、以视口中心为锚放大（`renderer.cpp:965-982`）；软键盘遮底时裁源高而非缩整图（`renderer.cpp:994-1003`）；键盘开合瞬间交换 `hiddenPanSourceTop` 保画面位置（`renderer.cpp:1005-1014`）；捏合锚点优先（`renderer.cpp:1018-1020`），否则 `panToCursor` 的 5% 边缘带跟随（`renderer.cpp:910-919`）。
5. **锁 X server**：`lockServerState()` 置 `rendererWaiting=TRUE` 再抢进程间锁，抢到后 futex wake（`renderer.cpp:882-887`）——X server 的 ddxRequestDone 钩子见此标志会让锁（`InitOutput.c:540-544`），双方不空转。
6. **共享 fence 双任务**：锁内先 `applyPendingGpuCopiesLocked()` 排空 GPU 拷贝（`renderer.cpp:1049`），再画根纹理四边形（`renderer.cpp:1055-1059`；FD 后端用 `xfactor=width/stride` 修正 stride 宽纹理的 UV，`renderer.cpp:1053-1054`），一个 `eglCreateSyncKHR` fence + `glFlush` 覆盖两批绘制（`renderer.cpp:1060-1061`，省一次 GPU 往返）。
7. **光标**：单独小锁下 `glTexImage2D` 上传新位图（`renderer.cpp:1063-1070`），再 alpha blend 画上（`drawCursor`，`renderer.cpp:1304-1318`）。
8. **fence 等待与回执**：`waitForFence`（100ms 超时只告警不卡死，`renderer.cpp:42-48`）确认 GPU 真做完后才 RELEASE 发布 `completedSerial`（`renderer.cpp:1077-1081`）——提前发布会让客户端下一次写与在途读竞争（注释 `renderer.cpp:756-759` 把这条不变量讲透）。
9. **swap 与预热**：置 `waitForNextFrame=true`、解锁、`eglSwapBuffers`（`renderer.cpp:1082-1086`），然后**立刻画一个 1x1 scissor clear 并等 fence**（`renderer.cpp:1088-1095`）——提前把下一个 backbuffer 出队好，下帧不必等 BufferQueue。这就是本文件的"双缓冲"实态：Android 窗口原生多缓冲，渲染线程用"swap 后预提交微绘制"抹平出队延迟。

### GPU 拷贝队列：findBufferWithRetry 与 FBO 回放

Present 扩展的拷贝被 X server 延迟投递：`lorieTryScheduleGpuCopy` 把 `{serial, srcId, dstId, 偏移, ≤64 矩形}` 写进环形队列、RELEASE 发布 writeIndex 并跨进程 signal（`InitOutput.c:969,1070-1071`），vblank 到点由 present_execute.c 的补丁钩子 `lorieGpuCopyAck` 收尾（`patches/xserver.patch:412`）。渲染线程侧 `applyPendingGpuCopiesLocked()`（`renderer.cpp:787`）drain 队列，每个条目先 `findBufferWithRetry` 拿 src/dst。

`findBufferWithRetry()`（`renderer.cpp:762`）是**注册竞态的救火队**：拷贝条目可能先于缓冲注册 socket 到达，先无重试查一次（命中即顺手 attachToGL 挂入 buffers，`renderer.cpp:766-772`），未命中则 20 轮 × 5ms `usleep` 重试（`renderer.cpp:774-783`），共 100ms 有界等待——比外层循环忙转体面（注释 `renderer.cpp:760-761`）。条目绘制走 FBO：`gpuCopyFbo` 挂目标纹理当 color attachment（`renderer.cpp:821`），源纹理普通采样，逐矩形换算 NDC/UV；两处易错细节有注释钉版——FBO 写与屏幕绘制的 y 方向约定相反（`renderer.cpp:852-854`），EGLImage 纹理按逻辑宽采样而只有 CPU 上传的 FD 纹理才按 stride 宽（`renderer.cpp:856-857`）；src/dst 存储格式不同时换 BGRA shader（`renderer.cpp:863`）。目标换绑只在 dstBufferId 变化时做（`renderer.cpp:820`），排空后恢复 viewport（`renderer.cpp:875-878`）。

### vsync/workqueue 协同：两进程共用的节拍器

节流核心是 `waitForNextFrame` 标志（`lorie.h:250`），大段注释（`lorie.h:236-249`）解释动机：某些设备上 GLES2 不调 `eglSwapBuffers` 就不真正提交帧（glFinish/eglWaitGL 全无效），而 swap 会阻塞到上屏；于是渲染线程用 swapInterval=0 换取立即返回（**勘误**：`lorie.h:245` 注释仍写 "we set eglSwapInterval(dpy, 1)"，实际代码是 `renderer.cpp:286,745` 的 `eglSwapInterval(egl_display, 0)`——注释滞后于代码，节流职责已全部移交 waitForNextFrame 机制），每 vsync 至多一个全屏 quad 的预算由标志门控，GPU 时间不浪费在注定不上屏的帧上。

节拍源头在**X server 进程**：`lorieChoreographerFrameCallback`（`InitOutput.c:800`，由 `cmdentrypoint.cpp:214-216` 注册的 AChoreographer 驱动）每帧 `QueueWorkProc(lorieRedraw)` 投进 workqueue（Vyukov 无锁环形重实现，另见 05 篇）并写 eventfd 唤醒 X server 主循环（`InitOutput.c:793`）；`lorieRedraw`（`InitOutput.c:559`）在 X server 进程清 `waitForNextFrame`（`InitOutput.c:568`）、Damage 非空则置 `drawRequested=TRUE`（`InitOutput.c:594`）并刷新 `rootWindowTextureID`（`InitOutput.c:598`），最后跨进程 signal（`InitOutput.c:604`）。GUI 进程侧 `shouldWait()`（`renderer.cpp:1100`）把标志纳入五层判断：viewport 变化立即清挂起（`renderer.cpp:1102-1107`）→ 有待处理状态/窗口/缓冲/GPU 拷贝立即醒（`renderer.cpp:1108-1114`）→ 根纹理 ID 变了则等新缓冲（`renderer.cpp:1116-1120`）→ 无 surface、waitForNextFrame、等缓冲任一为真继续睡（`renderer.cpp:1122-1124`）→ 有 drawRequested 或光标动静才干活（`renderer.cpp:1126-1128`）。两进程由此形成 vsync 同步流水线：choreographer 起拍 → workqueue 排程 → 共享标志传递 → 渲染线程被跨进程 cond 叫醒。

## 五、设计决策：六个值得抄的判断

1. **假窗口保 context**：1x1 AImageReader 换 surfaceless-context 兼容性（`renderer.cpp:191-197`），代价是少量常驻内存，换来窗口反复增删时 GL 状态零丢失——比给每个真窗口重建整套纹理省得多。
2. **fence 而非 glFinish**：设备差异下 glFinish 可能空转（`lorie.h:239-241`），`eglCreateSyncKHR`+100ms 超时等待（`renderer.cpp:44-48`）既正确又不会永久卡死；completedSerial 必须等 fence 才发布（`renderer.cpp:756-759`）是全文件最重要的内存序不变量。
3. **释放两阶段移交**：GL 对象线程亲和 ⇒ removedBuffers 把释放权交还渲染线程（`renderer.cpp:596-599`）；setWindow 同步等 EGLSurface 销毁完才返回（`renderer.cpp:641-647`），否则 SurfaceView 侧炸出 "BufferQueue has been abandoned"。
4. **运行时探测代替机型清单**：BGRA 采样用 0xAABBCCDD 像素 roundtrip 验证（`renderer.cpp:484-485,550-554`）；Present GPU offload 前用 64x64 缓冲验证 CPU 映射能看见 GPU 写、unlock 不会带回旧数据（`cpuAndGpuShareAhbMemory`，`renderer.cpp:366-438`，gfxstream 类后端就倒在这）。探测失败降级 legacy drawing/CPU 拷贝而非崩溃。
5. **诊断日志对抗 GLES2 盲区**：GLES2 没有 `glGetTexLevelParameteriv` 查不了纹理实际尺寸，debug 模式直接问 AHardwareBuffer 本尊并对拍自家 desc（`renderer.cpp:827-835`）。
6. **报视口即协议**：所有影响触摸换算的几何变化经 `reportViewport` 去重上报（`renderer.cpp:160-185`），setViewport/setZoom 主动把 reported* 置 -1 强制重报（`renderer.cpp:679-688`）——渲染端与输入端的一致性靠这一个出口维护。

## 六、新人提示

- **铁律：GL/EGL 调用只许出现在渲染线程**。JNI 线程的任何入口都只写 volatile 字段 + signal（withStateLock 宏，`renderer.cpp:50-57`），threadLoop 统一消费；加功能先想清楚字段归谁写。
- **读码顺序**：initThread（243）→ threadLoop（1134）→ shouldWait（1100）→ redrawLocked（921）→ applyPendingGpuCopiesLocked（787），最后才是 drawRegion/drawCursor 两个纯绘制原语（1280/1304）。
- **调试抓手**：logcat tag `gles-renderer`（`renderer.cpp:39`）；`renderedFrames` 看 FPS（`renderer.cpp:1097`）；GPU 拷贝尺寸对拍日志需开 `lorieDebugEnabled`（`renderer.cpp:828`）；EGL 错误码有人话翻译表 `printEglError`（`renderer.cpp:61`）。
- **三个坑**：①模式切换期"合法宽"有两个值（CVT 8 像素粒度，`renderer.cpp:16,947`），改尺寸逻辑别只比等号——渲染端容忍对齐宽与原始宽两种缓冲，其余一律当错尺寸挂起；②`removeBuffer` 双分支（`renderer.cpp:587-602`）意味着"删除"是异步的，短窗口内 removedBuffers 里的缓冲仍会被画最后一帧；③在 renderer 里调 Java 必须用 `rendererEnv`（attach 于 `renderer.cpp:245`），它随线程生灭，别从别的线程借。
- **衔接阅读**：LorieBuffer 三后端看 buffer.c（03 篇）；gpuCopyQueue 生产者与 Present 集成看 InitOutput.c（04 篇）；workqueue 无锁实现看 workqueue.cpp（05 篇）。把这三篇与本篇连读，"X server 写一帧、渲染线程贴一帧"的全部接力细节就都在手里了。
