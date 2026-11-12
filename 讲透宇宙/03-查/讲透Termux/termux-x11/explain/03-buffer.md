# 03 · buffer.c + buffer.h：跨进程像素搬运的统一货币

> 精讲对象：`lorie/src/main/cpp/lorie/buffer.c`（584 行）+ `buffer.h`（265 行），知识图谱 L1 X server 原生核心层。
> 锚基准：`buffer.c:NN` / `buffer.h:NN` 指 `/usr-data/data2/repos/termux-repo/termux-x11/lorie/src/main/cpp/lorie/` 下两文件，同目录 renderer.cpp/InitOutput.c/activity.cpp/cmdentrypoint.cpp 同理。全部锚经源码现场核实（commit 29d4460b）。
> 开篇勘误两条：① 篇名常被写作 buffer.cpp——仓内实际是 **buffer.c**（纯 C，buffer.h 以 `extern "C"` 包裹供 C++ 消费，`buffer.h:6-8`）；② "LorieDataTarget 消费者协议"与本文件无关——`LorieDataTarget` 是剪贴板 X11 selection 的目标链表（`clipboard.c:207` 定义、`:381-387` 填充），LorieBuffer 真正的消费者协议是本篇第四节讲的 renderer 三列表状态机与 registeredBuffers 注册表。

## 一、角色定位：双进程架构里"像素住哪、怎么搬"的唯一答案

termux-x11 的一切复杂度都源于一个约束：X server 进程（Termux 命令行侧）产像素，Android Surface 只能住在 GUI 进程（Java 应用侧）。buffer.c 就是这条进程缝上的**通用缓冲容器**——它不渲染、不合成，只回答三个问题：像素存在什么介质上（后端）、谁还活着引用它（生命周期）、怎么越过进程边界（传递）。

三点定性：①**多后端抽象**——同一套 API（分配/锁/转 GL 纹理/收发）之下三种介质可互转，从纯堆内存到 GPU 可采样 AHardwareBuffer（`buffer.h:14-19` 的类型枚举）；②**跨进程信使**——缓冲句柄经 Unix socket 的 SCM_RIGHTS ancillary 数据在两进程间漂移，`id` 字段是跨进程关联键；③**基础设施复用者兼提供者**——X server 进程的整个共享状态 `lorie_shared_server_state`（含 GPU 拷贝环形队列）本身也住在 `LorieBuffer_createRegion` 开的共享内存里（`InitOutput.c:154`，名为 "xserver"），renderer 的跨进程唤醒条件变量同样用它（`renderer.cpp:325`，名为 "renderer-cond"）——本文件的 `createRegion` 是全仓跨进程内存的统一入口，而不只是像素缓冲的分配器。

与邻居的分工：renderer.cpp 只在 GUI 进程消费 LorieBuffer（贴纹理上屏），InitOutput.c 只在 X server 进程生产与注册它（根窗口/EXA pixmap/DRI3 导入），activity.cpp 与 cmdentrypoint.cpp 是两端的搬运工。buffer.c 自己不知道任何进程的事——它被两边 include，同一份代码在两个进程里各跑一份。

## 二、内部结构：一个结构体、三种后端、一套手搓原子引用计数

### LorieBuffer 本体（buffer.c:32-49）

`struct LorieBuffer` 十个字段分四组：生命周期组 `int16_t refcount`（`:33`，刻意放在结构体第一个字段）与 `struct xorg_list link`（`:46`，嵌入 Xorg 通用双向链表节点，见下文列表管理）；后端组 `LorieBuffer_Desc desc`（`:34`）加 fd/size/offset（`:40-42`，FD 后端专用）——`desc`（`buffer.h:21-27`）持有 width/height/stride/format/type/64 位自增 `id`、AHB 指针与 CPU 映射指针；GL 组 `GLuint id`（`:44`，GL 纹理名）与 `EGLImage image`（`:45`，AHB 零拷贝导入句柄）；状态组 locked/lockedData（`:36-37`）与 `int32_t gpuCopyPending`（`:48`，在途 GPU 拷贝计数，供 X server 线程判断 CPU 访问是否可能与 GPU 拷贝竞态，`buffer.c:51-63` 三函数）。注意 `desc.id` 与 `GLuint id` 是两个东西：前者是跨进程缓冲身份，后者是本进程 GL 纹理名。

### 三种后端与选择规则

- **LORIEBUFFER_REGULAR**：`calloc(stride*height*4)` 纯堆内存（`buffer.c:141`），不可跨进程、不可 GPU 采样，是普通 EXA pixmap 的默认低成本形态；
- **LORIEBUFFER_FD**：`LorieBuffer_createRegion` 开共享内存 + `mmap(PROT_READ|PROT_WRITE, MAP_SHARED)`（`buffer.c:149`），CPU 侧跨进程共享，但每次上屏要走 `glTexSubImage2D` 整帧上传（`buffer.c:469-470`）；
- **LORIEBUFFER_AHARDWAREBUFFER**：Android 硬件缓冲，usage 同时要求 CPU 读写与 `GPU_SAMPLED_IMAGE|GPU_FRAMEBUFFER`（`buffer.c:206-207`），可经 EGLImage 零拷贝进 GPU（`buffer.c:448`）。

根窗口的选型在 InitOutput.c 一锤定音：`usage_hint == CREATE_PIXMAP_USAGE_LORIEBUFFER_BACKED` 时按 legacyDrawing 开关取 FD 或 AHB，否则 REGULAR（`InitOutput.c:1167`）——命令行 `-legacy-drawing` 最终就落在这行的三目运算上。普通 pixmap 起始为 REGULAR，等 Present 需要被 GPU 采样时再由 `lorieEnsureGpuSampleable` 现场"升级"（`InitOutput.c:125-133` 调 `LorieBuffer_convert`）。

### allocate 分配链（buffer.c:128-216）

公共入口 `LorieBuffer_allocate`（`:195`）先按类型备料：FD 后端算 `alignToPage(width*height*4)` 并 `createRegion("LorieBuffer", size)`（`:201-202`）；AHB 后端 `AHardwareBuffer_allocate`（`:205-213`，失败直接 dprintf FATAL）。随后进内部 `allocate()`（`:128`）：栈上拼一个临时 LorieBuffer，`static uint64_t id` 计数器自增赋予唯一身份（`:130`）；格式/尺寸合法性只对非 AHB 强制（`:131`，AHB 的真实参数以 `AHardwareBuffer_describe` 回填为准——分配器可能给出比请求更宽的 stride，`:159-165`）；fd 所有权按 `takeFd ? fd : dup(fd)` 决定复制还是接管（`:132`）；refcount 从 0 原子加到 1（`:137`）。三后端各自的资源获取在 switch 内完成（`:139-168`），堆上正式对象 calloc 失败时逐后端回滚（`:170-188`），成功则 `*buffer = b` 整体拷出并 `xorg_list_init(&buffer->link)`（`:190-191`）——link 自指成空节点，缓冲在入链前是"自由"的。

### 引用计数：int16 上的指针强转原子操作

`LorieBuffer_acquire` 把结构体指针强转成 `int*` 做 `__sync_fetch_and_add`（`buffer.h:96`），`LorieBuffer_release` 却强转 `int16_t*`（`buffer.h:107`），归 1 即调 `__LorieBuffer_free`。同一字段两种宽度的原子操作是个刻意 hack：refcount 必须是结构体首字段（两处注释都写明 "refcount is the first object in the struct"），小端机器上对 32 位字加 1 等效于只加低 16 位的 refcount——前提是引用数不溢出 65535 且平台小端。ARM/AArch64 Android 上两个前提恒成立，代价是这段代码不可移植到 big-endian。锁协议也按后端分层：REGULAR/FD 的 lock 只是返回 `desc.data` 指针（`buffer.c:335-336`），AHB 才真正走 `AHardwareBuffer_lock`（`:337-340`）；重复 lock/unlock 未 lock 都有 errno 级诊断（`:328-333`、`:355-358`）。

## 三、外部连接：五个消费者与一张注册表

**InitOutput.c（X server 进程，生产者）**：根窗口每次重建即 `LorieBuffer_allocate` 并 lock 住供 CPU 绘制（`InitOutput.c:1167-1172`）；屏保/重建/换屏三处把根缓冲 `lorieRegisterBuffer` 给 GUI 进程（`InitOutput.c:204/644/734`）；Present 的 GPU 拷贝调度 `lorieTryScheduleGpuCopy` 对源缓冲（及非根目标）做 acquire + `gpuCopyPendingInc` 双保险（`InitOutput.c:1034-1052`，注释言明额外引用让 LorieBuffer 结构体活到 ack 为止），完成回执 `lorieGpuCopyAck` 对称 dec + release（`InitOutput.c:1091/1093/1098/1100`）；DRI3 客户端直接递来的 AHardwareBuffer 走三件套接收（`buffer.h:246-256` 的 raw API，`InitOutput.c:1298` 收、`:1301` 查询、`:1306` wrapAHardwareBuffer 包成 LorieBuffer、`:1323` 失败路径释放），fd 形式的 DRI3 pixmap 则 `LorieBuffer_wrapFileDescriptor`（`InitOutput.c:1281`）。

**cmdentrypoint.cpp（X server 进程，注册与注销）**：`lorieRegisterBuffer` 是幂等协议——按 id 查 `registeredBuffers` 已在册即返回（`cmdentrypoint.cpp:532`），否则发 `EVENT_ADD_BUFFER` 事件、`LorieBuffer_sendHandleToUnixSocket` 漂洋过海、addToList 入册（`:535-539`）；`lorieUnregisterBuffer` 发 `EVENT_REMOVE_BUFFER`（带 id）并出册（`:547-553`）。GUI 进程断连（X_NOTIFY_ERROR）时把整张 registeredBuffers 清空（`:273-274`）。

**activity.cpp（GUI 进程，接收端）**：事件泵 `case EVENT_ADD_BUFFER` 调 `LorieBuffer_recvHandleFromUnixSocket` 重建缓冲并交 `renderer.addBuffer`（`activity.cpp:264-270`）；`EVENT_REMOVE_BUFFER` 转发 id（`:273-274`）。

**renderer.cpp（GUI 进程，最终消费者）**：三列表状态机（下节详述）+ `findBufferWithRetry` 有界等待（`renderer.cpp:767-789`，20 次×5ms——因为注册到达走的是异步 socket，GPU 拷贝条目可能先于缓冲本体入表）。

**列表管理（buffer.c:481-503）**：`addToList` 先 `xorg_list_del` 再 `xorg_list_add`（`:483-484`，天然防重复入链——已在别的链上会被摘下再挂）；`removeFromList` 只摘不销毁（`:488-491`）；`first` 判空取头（`:493-495`）；`findById` 线性扫 `desc.id`（`:497-503`）。所有链表操作本身不加锁——并发安全完全靠调用方的 bufferLock（renderer 侧 spinlock）与 X server 单线程约定。`__LorieBuffer_free` 兜底 `xorg_list_del`（`buffer.c:292`），保证缓冲死时必不在任何链上。

## 四、数据流：一块根窗口缓冲的跨进程一生

1. **出生**：X server 启动/换分辨率，`InitOutput.c:1167` 按开关选 AHB（默认）或 FD 后端 allocate，id 从 0 起单调递增；随后 lock 给 EXA 当 framebuffer 画（`:1170`），并把 id 发布进共享状态 `state->rootWindowTextureID`（`InitOutput.c:598`）——这个字段就是 GUI 进程找根纹理的钥匙。
2. **出境**：`lorieRegisterBuffer` 发 EVENT_ADD_BUFFER + `sendHandleToUnixSocket`（`buffer.c:371-382`）。协议分两截：先 `write(socketFd, buffer, sizeof(*buffer))` 把**整个结构体裸走线**（`:375`），FD 后端紧跟 `ancil_send_fd` 递 fd（`:376-377`），AHB 后端交 `AHardwareBuffer_sendHandleToUnixSocket` 让 Android 自己序列化（`:378-381`）。ancil 收发是本文件手搓的 SCM_RIGHTS 实现：1 字节哨兵 `'!'` 作 iovec、cmsghdr 装一个 int fd、sendmsg/recvmsg 完事（`buffer.c:521-550`、`:552-583`）。
3. **入境重建**：GUI 进程 `recvHandleFromUnixSocket`（`buffer.c:384-440`）read 同尺寸结构体，重置一切进程本地字段（refcount 归 1、fd=-1、image=NULL、locked 清零，`:391-398`）；FD 后端 `ancil_recv_fd` 拿到本进程新 fd 并重新 mmap（`:401-408`），AHB 后端 recv handle（`:415-418`）。**desc.id 原样过线**——两个进程从此用同一个数字称呼同一块像素。
4. **三列表流转**：IPC 线程 `renderer.addBuffer` 只挂 `addedBuffers`（`renderer.cpp:582`，GL/EGL 是线程亲和的，IPC 线程绝不能碰）；渲染线程主循环统一把 addedBuffers 逐个 `attachToGL` 后转入活跃表 `buffers`（`renderer.cpp:1170-1173`）。绘制根窗口时按 `rootWindowTextureID` 在 buffers 里 findById（`renderer.cpp:933`），找不到还去 `removedBuffers` 兜底"最后一帧"（`:936`，防止刚移除又恰好要画一帧的竞态白屏）。删除同理分两条路：还在 addedBuffers 的可当场 release（无 GL 资源，`renderer.cpp:591-593`），已 attach 的必须移入 removedBuffers 等 GL 线程释放（`:597-598`，释放点 `:1190-1192` 与线程收尾 `:1201-1202`）。
5. **上屏**：`attachToGL`（`buffer.c:442-462`）是后端分叉的终点——AHB 走 `eglCreateImageKHR(EGL_NATIVE_BUFFER_ANDROID)` + `glEGLImageTargetTexture2DOES` 零拷贝（`:447-448`、`:455-456`，依赖 weak 符号 `eglGetNativeClientBufferANDROID`，`buffer.c:29-30`，API 26 前 libEGL 不导出它）；FD/REGULAR 走 `glTexImage2D` 只分配不上传（`:457-461`，注释说明真正像素等 drawRequested 标志在 redraw 里补）。此后每帧 `bindTexture`（`buffer.c:464-471`）：AHB 纹理已绑 EGLImage 只需 `glBindTexture`；FD 后端则 `glTexSubImage2D` 从 mmap 内存整帧搬运（`:469-470`）——`drawRootBuffer` 里 `LorieBuffer_bindTexture(buffer)`（`renderer.cpp:1052`）与 GPU 拷贝回放里的 `LorieBuffer_bindTexture(src)`（`:838`）就是这条轨的两个消费点；stride≠width 时用 xfactor 修正采样坐标（`renderer.cpp:1053-1054`）。
6. **死亡**：最后一个 release 触发 `__LorieBuffer_free`（`buffer.c:288-316`）——出链、GL context 在场则 `glDeleteTextures`（`:294-295`）、有 display 则 `eglDestroyImageKHR`（`:297-298`）、按后端 free/munmap+close/AHardwareBuffer_release（`:300-313`）。

`LorieBuffer_convert`（`buffer.c:226-286`）是这张生命周期图上唯一的"变形"边：仅接受 REGULAR 起点（`:228-231`），FD 方向新建 region、mmap、`pixman_blt` 逐行搬运后弃旧堆内存（`:233-256`）；AHB 方向 allocate + lock + blt + unlock（`:257-285`）。它无返回值，成功与否只能靠"desc.type 是否真的变了"反推——InitOutput.c 的调用点注释坦承这一点（`InitOutput.c:135`）。

## 五、设计决策与批判

**为什么三种后端而不是全上 AHB**：AHB 是唯一零拷贝路径但有代价——分配慢、stride 由 Gralloc 决定不受控、API 26 才有（所以全文件 11 处 `__builtin_available(android 26, *)` 守卫）、某些设备上 lock 语义坑深（DRI3 路径专门用 lock 探测失败来标记 gpuOnly pixmap，`InitOutput.c:1314-1316`）。FD 后端是兼容与控制力的中庸档（`-legacy-drawing` 的落点），REGULAR 则让 99% 的离屏 pixmap 零成本起步、按需升级。这是典型的"快路径晚绑定"策略。

**createRegion 三级降级**（`buffer.c:94-125`）：ASharedMemory_create（API 26+）→ memfd_create → /dev/ashmem ioctl。中间层是为老内核/老 API 准备的手写 syscall shim，四个架构的 syscall 号硬编码（i386=356、x86_64=319、arm=385、aarch64=279，`buffer.c:67-77`），并带 `MFD_CLOEXEC|MFD_ALLOW_SEALING` 与 ftruncate（`:101-104`）。这层与 L2 的 shm/shmem.c ashmem 模拟形成呼应——同一个"Android 共享内存的时代分层"问题，两个文件各自答了一遍。

**结构体裸走线**：跨进程传递不用显式序列化协议，直接 `write` 整个 struct。两进程加载的是**同一个 libXlorie.so 的同一份结构体布局**，padding/ABI 天然一致，指针字段过线后由接收端重置——这是一个"用同源二进制换协议安全"的决策，换任何第三方进程接入立刻失效。它也解释了为什么 id 要设计成 desc 内的值字段而非指针。

**可指摘处三条**：① `recvHandleFromUnixSocket` 的 calloc 失败分支写的是 `outBuffer = NULL` 而非 `*outBuffer = NULL`（`buffer.c:433`）——给局部参数赋值，调用方输出参数不被清空；当前调用点 activity.cpp:266 用 static 初始化为 nullptr 的变量侥幸无恙，属潜伏 bug。② gpuCopyPending 的 `++/--` 无原子语义（`buffer.c:51-59`），安全性完全寄托在头文件注释的线程约定上（`buffer.h:113-114`"Only ever called from the X server thread"）。③ `LorieBufferList_findById` 线性扫描在缓冲数大时是 O(n)——本仓缓冲数以个位数十计，可以接受，但若未来多窗口 DRI3 爆发，这里会是第一处热点。

## 六、新人提示

- **读码路线**：buffer.h 全文（注释即协议文档，265 行里注释占一半）→ buffer.c:128-216 分配链 → :371-440 收发对 → renderer.cpp:580-617 三列表，一小时可贯通。
- **改后端先看 usage 位**：AHB usage 的 `CPU_READ_OFTEN|CPU_WRITE_OFTEN|GPU_SAMPLED_IMAGE|GPU_FRAMEBUFFER` 四件套在 allocate 与 convert 两处重复出现（`buffer.c:206-207`、`:259-260`），少一个就会出现"分配成功但采样变黑"或 lock 失败。
- **调试入口**：注册/接收两侧各有一条 INFO log 带 width/stride/height/format/type/id 全参数（`cmdentrypoint.cpp:540`、`activity.cpp:268-269`），logcat 里对齐两侧 id 即可确认传递是否成功；`lorieDebugEnabled` 打开时 renderer 还会周期性对照 AHB 真实尺寸与 LorieBuffer_Desc 的偏差（`renderer.cpp:830-845`）。
- **别踩的坑**：给 LorieBuffer 加字段时，任何插在 refcount 之前或改变 desc 布局的改动都会同时破坏"首字段强转"的引用计数 hack（`buffer.h:96/107`）与裸走线协议——两端同 so 也要重装两进程；`desc.stride` 单位是像素而 `new_fb_pitch` 是字节（`InitOutput.c:1168` 有 `*4` 换算），GL 上传尺寸永远用 stride 不用 width（`buffer.c:460/470`）。
- **延伸**：`AHARDWAREBUFFER_FORMAT_B8G8R8A8_UNORM=5` 是本仓自造的 define（`buffer.h:12`，对应 HAL_PIXEL_FORMAT_BGRA_8888，NDK 头文件没这个名字）；`LorieBuffer_isRgba` 的语义是"非 BGRA 即真"（`buffer.c:477-479`），renderer 据此在 RGBA/BGRA swizzle 双 shader 间二选一。配套阅读：本系列 02 篇（renderer 纹理轨消费侧）、01 篇（InitOutput 生产侧）与 shm/ 子目录（X 客户端自己的 MIT-SHM 段走 L2 兼容层，与本文件的共享缓冲是两条独立通路）。
