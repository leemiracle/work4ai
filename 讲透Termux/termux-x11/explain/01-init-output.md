# 01 · InitOutput.c — Xlorie 的 DDX 输出核心

> `lorie/src/main/cpp/lorie/InitOutput.c`（1422 行），知识图谱 L01「X server 原生核心」层最高连接度节点（fanOut 83）。未标文件的行号锚均指本文件，全部锚经源码现场核实（commit 29d4460b）。

## 1. 角色定位

InitOutput.c 是 Termux:X11 内嵌 Xorg 的 **DDX（Device Dependent X，设备相关层）输出实现**——上游里这个角色由 xf86 视频驱动扮演，本仓用一个纯 C 文件把"显卡+KMS+DRM"替换成"Android 共享缓冲 + GLES 渲染器"，是双进程架构中 X server 侧的发动机：DIX 主循环（`cmdentrypoint.cpp:222` 的 `dix_main`）的输出初始化最终都落在本文件钩子上。

与兄弟文件 InitInput.c 构成 DDX 一对入口：`InitOutput`（:879）管屏幕与渲染扩展栈，`InitInput`（`InitInput.c:271`）管三个 AddInputDevice（:272-274），二者经 `extern lorieMouse, lorieKeyboard`（:53，定义于 `InitInput.c:45`）共享设备句柄。本文件还完整履行 DDX 契约函数族：`OsVendorInit`（:146）、`ddxUseMsg`/`ddxProcessArgument`（:326/:338）、`ddxReady`（:294）、`ddxGiveUp`（:216）、`ddxRequestDone`（:548，由打补丁的 dispatch.c 每请求后回调，`patches/xserver.patch:28`）。

## 2. 内部结构

**① 全局状态**：`lorieScreenInfo`（:66-94）——damage、eventFd/stateFd、共享状态指针、root 段（尺寸/帧率/legacyDrawing）、dri3 与 gpuPresentDisabled 开关、vblank 队列与 msc 计数；静态初始化给出默认屏 1280x1024@30（:97-105）。全局 `pScreenPtr`（:96）让全文件可达屏幕对象。

**② DDX 协议函数群**：开关集中在 `ddxProcessArgument`——`-xstartup` 与 `--` 互斥（:339-359）、`-legacy-drawing`、`-disable-dri3`、`-force-sysvshm`、`-check-drawing`、`-disable-gpu-present`、`-tag` 多窗口标签（:390-394）。`OsVendorInit` 三件事：`LorieBuffer_createRegion("xserver")` 分配 memfd 并 mmap 出共享状态（:154-162）、初始化进程共享递归互斥锁（:164-168）、按 documentTag 选监听端口（:171；`lorie.h:18-19` 定义 PORT 7892 与 DOCUMENT_PORT_BASE 7900）。

**③ 屏幕与 RandR**：`lorieScreenInit`（:808）十连链——fbScreenInit 软件渲染核心接管像素操作 → dri3_screen_init（:829）→ exaDriverInit → lorieRandRInit → present_screen_init 等（:824-835）。`lorieCreateScreenResources`（:632）创建根窗口 LorieBuffer 背书 pixmap、Damage 跟踪、FPS 计时器与心跳（:640-641）。`lorieRandRInit`（:758）用 libxcvt 生成模式（:399），尺寸范围 1..32767（:772）；`lorieRRScreenSetSize`（:692）处理分辨率变更——排空 vblank、建新 pixmap、CopyArea 迁移、TraverseTree 修正引用旧 pixmap 的窗口（:730）。

**④ EXA 驱动**：关键认知——`lorieExa`（:1246-1254）里 PrepareSolid/PrepareCopy/PrepareComposite 全是 FalseNoop，**没有 GPU 加速绘制**；加速只在跨进程 GPU 拷贝（§4）与渲染器进程的 GLES 合成。EXA 在此的真实角色是 pixmap 生命周期管理员：`lorieCreatePixmap`（:1154）按 usage_hint 选后端——普通窗口 REGULAR，根窗口按 legacyDrawing 选 FD 或 AHARDWAREBUFFER（:1166）；`loriePrepareAccess`/`lorieFinishAccess`（:1211/:1234）做缓冲 lock/unlock 与跨进程锁。`lorieEnsureGpuSampleable`（:125-142）是后端互转枢纽：把 REGULAR 缓冲升级成 FD/AHB（GPU 可采样）形态，成功后修正 pixmap pitch（:136）并重新 lock。

**⑤ Present**：自述"大部分拷贝自 present_fake.c，唯一区别是把 vblank 兑现挪到 lorieRedraw 而非定时器"（:908-909）；vblank 走链表队列（:920-955）。`loriePresentFlip`（:1103）拒绝 FD 后端 + turnip 组合，除非 `TERMUX_X11_FORCE_FLIP=1`（:1109-1111）；`loriePresentAfterFlip`（:1123）依赖上游补丁新增的 after_flip 回调点（`patches/xserver.patch:557`）。

**⑥ DRI3 导入**：`loriePixmapFromFds`（:1256）用三个魔数 modifier 区分路径——1255=AHB 经 socket、1256=同上翻转色序、1274=裸可映射 fd（:1260-1262）；socket 路径先写 1 字节信号再收 AHardwareBuffer（:1297-1298）；lock 失败标记 `gpuOnly`（:1310-1312），此类像素 CPU 摸不了只能走 GPU。

**⑦ GLX 假体**：`glXDRIscreenProbe`（:1387）calloc 一个 `__GLXscreen`，挂静态 fbconfigs（`fbconfigs.h:30`），glvnd 名填 "mesa"（:1398）；代码自承没有真 GLX 支持、只是照 swrast 上报（:1401）——真 GLX 渲染由客户端侧 Mesa（turnip+DRI3）完成，这里只需协议握手不塌。导出的 `__glXDRISWRastProvider`（:1418）供 `xorgGlxCreateVendor`（:900）发现。

**软光标**：`lorieSetCursor`/`lorieMoveCursor`（:474/:435）把光标位图转 RGBA 写进共享状态 cursor 段（:449-471），尺寸上限 512（:479-481）；移动光标只写 x/y+moved 再 signal，**不拿锁**（:442-443 注释：拿锁会等渲染完成）。

## 3. 外部连接

**上游 Xorg DIX**：`dix_main` 调 `InitOutput` → `AddScreen(lorieScreenInit)`（:903）；补丁版 dispatch.c 回调 `ddxRequestDone`（`patches/xserver.patch:28`）；补丁版 present 在拷贝路径调 `lorieTryScheduleGpuCopy`/`lorieGpuCopyAck`/`lorieGpuCopyIsDone`（`patches/xserver.patch:368-512`）。

**渲染器（renderer.cpp，GUI 进程）**三个接触面：①`InitOutput` 在 AddScreen 前调 `rendererTestCapabilities`（:899，实现在 `renderer.cpp:563`，起 scratch Renderer 试探 EGL 能力）；②**rendererCond 握手**——渲染器把自建的进程共享条件变量放进 memfd（`renderer.cpp:322-331`），经 `activity.cpp:316-318` 以 EVENT_RENDERER_WAKEUP_COND + ancillary fd 发过连接 socket，`cmdentrypoint.cpp:435-438` 收到后调 `lorieSetRendererWakeupCond`（:196），经 QueueWorkProc 把 mmap+swap 挪到主线程（:177-194，swap 与 signal 同线程故永不竞争）；此前 rendererCond 指向占位符（:110-113），调用方免 NULL 检查；③GPU 拷贝环形队列的消费者在渲染器线程（`renderer.cpp:793-872`）。

**buffer.c/lorie.h**：像素都住在 LorieBuffer，三后端枚举（`buffer.h:15-19`）；共享状态定义于 `lorie.h:202`，gpuCopyQueue 容量 8、单条目最多 64 矩形（`lorie.h:190-191`）。

**cmdentrypoint.cpp 事件泵**：`handleLorieEvents`（`cmdentrypoint.cpp:262`）把 GUI 事件翻译进来——连接建立调 `lorieActivityConnected`（:201）、尺寸/名称变化调 `lorieConfigureNotify`（:849）、EVENT_GPU_COPY_DONE 调 `lorieRecheckGpuCopies`（`cmdentrypoint.cpp:441-446`；实现其实在补丁后的 present_scmd.c，`patches/xserver.patch:538`）。

**帧节拍**：AChoreographer 回调 `lorieChoreographerFrameCallback`（:800）由 `cmdentrypoint.cpp:214-216` 在 dix_main 前首次注册后自续（:801）；回调里 QueueWorkProc(lorieRedraw) + `lorieWakeServer`（:789，eventfd 写 1 唤醒主循环）。

## 4. 数据流

**启动序列**：`OsVendorInit`（共享状态+敲门监听）→ `InitOutput`（格式表 :880-897、rendererTestCapabilities、xorgGlxCreateVendor、lorieInitClipboard :899-901、AddScreen）→ `lorieScreenInit` → `lorieCreateScreenResources`（根 pixmap = LorieBuffer 背书，usage hint 5 是本仓私有常量 :55/:633）→ 分派循环 → `ddxReady`（:294）fork xstartup。`ddxReadyThread`（:223）：子进程设 `DISPLAY=:N`、从 XSTARTUP_CLASSPATH/LD_LIBRARY_PATH/LD_PRELOAD 还原变量（:232-236）、execvp；父进程 waitpid，子进程退出即 `GiveUp(SIGINT)`（:267）——**X 会话生死与 xstartup 进程绑定**。

**每帧正向流**：AChoreographer vsync → eventfd 唤醒 → `lorieRedraw`（:559）：释放请求锁、`current_msc++`、兑现到期 vblank（:565-566）；Damage 非空则 unlock+relock 缓冲刷新 CPU→GPU 一致性（:586-591）、DamageEmpty、置 drawRequested；最后把 `rootWindowTextureID` 写成缓冲 id（:598）并 signal rendererCond（:604，注释 :600-603：故意不拿 state->lock，渲染器睡前自查 drawRequested）。渲染器随后在 GUI 进程完成 GLES 合成上屏。

**GPU 拷贝流（Present 卸载）**：present_execute_copy 想把窗口像素拷到根/复合重定向 pixmap 时调 `lorieTryScheduleGpuCopy`（:969），六道闸：开关（:980）、连接与渲染面存活（:986，`lorieRendererAvailable` :960 查 surfaceAvailable）、源与目的都 `lorieEnsureGpuSampleable` 成 AHB（:993-994）、矩形数 ≤64（:1019）、队列有空位（:1027）。通过后：注册源缓冲（幂等）、`LorieBuffer_acquire` 加引用、`gpuCopyPendingInc` 防 CPU 读写与 GPU 拷贝竞争（:1034-1040）；目的是根 pixmap 时只递 `rootGpuCopyPending`（根有 pScreenPtr->devPrivate 生命周期兜底，加引用反而会在 resize 后泄漏陈旧缓冲——:1041-1057 注释是全文件最值得一读的引用计数论证）。随后填 entry、RELEASE 序发布 writeIndex（:1070）并 signal 渲染器；渲染器 drain 后写 completedSerial（`renderer.cpp:904`），X server 侧 `lorieGpuCopyIsDone`（:1079）轮询，完成事件回程走 EVENT_GPU_COPY_DONE → `lorieRecheckGpuCopies` 重执行卡住的 vblank。SPSC 环形队列（`lorie.h:209-212` 注释明确角色划分）。

**锁协议**：X server 与渲染器共画根缓冲会撕裂（`lorie.h:203-207`），故有 `state->lock`；为不让 X server 整帧持锁，设计成请求级持锁——PrepareAccess 发现会与 GPU 竞争（:1197-1204）且目的是屏幕 pixmap（:1206-1209）时 `lorieRequestLockTake`（:517），请求结束 `ddxRequestDone` → `lorieRequestLockRelease`（:524）：解锁后若 rendererWaiting 被置位，还 futex 等渲染器真正接手（100ms 超时兜底 :533-543）。

## 5. 设计决策

- **假 Present 换真节拍**：vblank 不用定时器，挂在 Choreographer 驱动的 lorieRedraw（:908-909），msc 与真实显示节拍对齐；AfterFlip 直调路径（:1123-1132）绕过 BlockHandler 消延迟。
- **EXA 降格为内存管理器**：绘制加速全让位（:1249），真"显卡"在另一进程的 GLES 里；EXA_HANDLES_PIXMAPS（:1248）声明 pixmap 由驱动托管，fb 软件路径照常跑。
- **rendererCond 占位符+主线程换入**：跨进程条件变量晚到（首次连接才有），占位符（:112-113）+ QueueWorkProc 串行化 swap（:174-176）+ swap 后立刻 signal 新 cond（:188 防信号丢失），三件套解决"唤醒通道晚于使用者"的时序问题。
- **根 pixmap 引用计数特殊化**：:1041-1057 论证为何根缓冲不加额外引用（resize 换新缓冲后旧引用让渲染器拿到已销毁对象），改用独立计数器——此不等式只对根成立。
- **两处坑**：①`lorieConfigureNotify` 里 mmWidth 与 mmHeight 都用 `mode->mode.width`（:867-868，对照 :706-707 正确写法，上游潜伏笔误，只影响 DPI 物理尺寸报告）；②`-force-bgra` 只在 :330 与 :366-367 出现，全仓无消费者——兼容性保留的死开关。
- **尺寸上限一致性**：RandR 上限 32767（:772）与 EXA maxX/maxY（:1247）必须同步改。

## 6. 新人提示

**阅读顺序**：`InitOutput`（:879）→ `lorieScreenInit`（:808）→ `lorieCreateScreenResources`（:632）→ `lorieRedraw`（:559）+ Choreographer 回调（:800）看帧循环 → 最后啃 `lorieTryScheduleGpuCopy`（:969）与 PrepareAccess/FinishAccess（:1211/:1234）。配合 `lorie.h:202-260` 共享状态定义（每条注释都是设计文档）食用。

**调试抓手**：日志 tag LorieNative（:51）；`TERMUX_X11_DEBUG=1` 开 DRI3 导入详情（:152）；FPS 计数器每 5 秒打一行，带 GPU 拷贝卸载率与回退统计（:613-625）——排查 Present 性能先看这行；`-check-drawing`（:379-383）画三色方块自检"X server→缓冲→渲染器"通路；心跳每秒一次（:627-630）。

**改代码前三提醒**：动 vblank 队列结构须同时看 `loriePerformVblanks` 调用点（:566/:697）；`lorieSetWindowPixmap`（:657）用"临时还原指针→调用→再包回"的 unwrap/wrap 模式，新增屏幕函数包装照抄此骨架；`ddxProcessArgument` 返回值是"消费的参数个数"（:358），加新开关别破坏契约。

**上游对照**：miPointerSpriteFuncRec、present_screen_info、dri3_screen_info_rec 等结构来自 Xorg DDX 接口约定；查某回调何时被调，去 `patches/xserver.patch` 找注入点（ddxRequestDone :28、after_flip :557、GPU 拷贝族 :368-512）比翻上游源码快。
