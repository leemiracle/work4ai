# 09 · xserver 影子构建层：空 submodule 之上的 83 行入口、11 配方与 8 补丁

> 精讲对象：`lorie/src/main/cpp/CMakeLists.txt`（83 行）+ `recipes/` 11 配方 + `patches/` 8 文件（7 patch + dix-config.h.in），知识图谱 L09。前提：`lorie/src/main/cpp/xserver/` 是**空目录**（16 submodule 未检出时实测 0 文件）。锚约定：入口 CMakeLists 简写 `root:NN`，`recipes/xserver.cmake` 简写 `xs:NN`，均经源码现场核实（commit 29d4460b）。

## 一、角色定位：上游 Xorg 的"就地驯化"车间

本仓不 fork 上游，改动以三层影子存在：**声明**——`.gitmodules` 钉住 16 个 submodule 的 URL 与精确 commit（xserver `65d790bd`），clone 后目录为空；**编排**——11 个 recipe 无视上游 autotools/meson，直接抄上游 `.c` 路径进自己的 `add_library` 用 NDK 重编；**修改**——7 个 patch 在 configure 阶段就地改 submodule 工作区，dix-config.h.in 替代 `./configure` 探测。与上游的差异因此压缩成 7 个文件（约 68KB），可 diff、可随指针升级。`root:80-82` 依依赖序 include 11 配方（xorgproto→…→xserver），纯头文件的 xorgproto INTERFACE 库先行（`xorgproto.cmake:5-6`），302 行 xserver 配方收官。

## 二、内部结构

### 2.1 入口 83 行：警告探测、幂等 patch、配方编队

`root:26-65` 列 38 个警告选项，`root:71-77` 用 `check_c_compiler_flag` 逐个试编译、只留 NDK clang 真支持的进 `common_compile_options`。find_package Python3/BISON（`root:19-20`）服务代码生成。核心是 `root:22-24` 的 `target_apply_patch`：先 `patch -R --dry-run` 反向演练——成功说明已应用过则跳过；失败才正向 `-N -r -`。configure 重跑多少次都不重复打补丁。`.gitmodules` 16 条目全部 `ignore = dirty`，patch 改脏 submodule 后 git status 保持安静。

### 2.2 16 submodule 拉取策略：纯 git 层，构建系统不代劳

`README.md:11` 的 Submodules caveat 专警：必须 `--recurse-submodules`（`README.md:15`）或 `git submodule update --init --recursive`（`README.md:21`）。Gradle 与 CMake **均无自动 clone 逻辑**（原生构建唯一定义在 `build.gradle:41`）——缺 submodule 时 configure 报源文件找不到，是新环境首构建最常见事故。**bzip2 是唯一零消费孤儿**：全仓 grep 无引用，且 `Xfont2.cmake:59` 明确 `-UX_BZIP2_FONT_COMPRESSION`，纯历史遗留。

### 2.3 11 配方速览

- **xorgproto.cmake**：INTERFACE 头文件库；生成 `X11/XlibConf.h`（`:2`）与 Xpoll.h（`:7-8`）、symlink libxtrans 为 `X11/Xtrans`（`:3`）；`:9` 应用 Xtrans.patch——X11 头体系大半构建期合成。
- **fontenc.cmake**：3 源文件直编 STATIC（`:1`）。
- **md.cmake**：无上游——公有域 SHA-1 内嵌为两个 `file(GENERATE)`（`:1-190`）编成 md 库（`:192`）。
- **pixman.cmake**：32 源文件（`:25-57`）+ 按 ABI 增删 NEON/SIMD 汇编（`:68-88`）；`:93` 应用 pixman.patch。
- **tirpc.cmake**：44 源文件（`:1-44`），`-D` 宏伪造整套 config.h（`:46-50`，含 `getdtablesize()=sysconf(_SC_OPEN_MAX)`）。
- **xshmfence.cmake**：同一份源码编两遍（pthread `:3-5`/futex `:7-9`），各用 8 个 `-D` 宏改名符号；`:11` 编入 `lorie/xshmfence.c` 分发器。
- **Xdmcp.cmake / Xau.cmake**：前者 9 源文件配 Bionic 适配宏（Xdmcp.cmake:3）；后者仅 2 文件，`:4` 有笔误（§五）。
- **Xfont2.cmake**：44 源文件五段编队（`:1-44`），关 Freetype/bzip2 只留 PCF/BDF+gzip（`:56-60`）。
- **xkbcomp.cmake**：libx11+libxkbfile+xkbcomp 三仓合体一个 STATIC（`:14-54`）；`:1` 注释直陈 "Normally xkbcomp is build as executable, but in our case it is better to embed it"；宿主 `/usr/bin/gcc` 现编 makekeys 生成 ks_tables.h（`:5-11`）；`:69-71` 连打三个 patch。
- **xserver.cmake**：24 静态库切分 + Xlorie 链接（§四）。

## 三、外部连接：8 个 patch 各驯服什么冲突

### 3.1 符号重命名

上游各库按独立二进制设计，whole-archive 单体链接下符号撞车致命。`xserver.patch:37-40` 用 `#define ClearWorkQueue _ClearWorkQueue` 等四条宏给上游 WorkQueue 加下划线前缀——lorie 用 Vyukov 无锁环形缓冲自实现了 WorkQueue（`workqueue.cpp:15`），两套须共存。`xserver.patch:119-147` 给 27 个 Xkb 文本函数加 X 前缀（`XkbInternAtom→XXkbInternAtom`）消与嵌入 xkbcomp 的同名冲突；配套 `xs:213` 的 `-DXkbFreeGeomOverlayKeys=XkbFreeGeomOverlayKeysInternal`，`xkbcomp.patch:67` 把 xkbcomp 的 `groupNames` 改 `xkbcomp_groupNames`（`:66-94`）。xshmfence 是编译期改名（§2.3），运行时由 `xshmfence.c:56` 按 fstat 大小路由；`xshmfence.c:42-46` 的 alloc_shm 返回 -1——无法探测客户端用哪套，索性不提供分配。

### 3.2 路径 extern 化：写死的 "/tmp" 变运行时变量

`Xtrans.patch:6-11` 把 `#define UNIX_PATH "/tmp/.X11-unix/X"` 替换成 `extern char* xtrans_unix_path_x11; #define UNIX_PATH xtrans_unix_path_x11`——宏变全局变量引用，XIM/FS/ICE 三组同样（`:13-35`）。Android 无 `/tmp`，Termux tmpdir 因 proot/chroot 而异，路径须运行时注入。配套 `:44-45` 把 `if (geteuid() != 0)` 改 `if (0)`（应用永非 root，原检查拒绝建 socket 目录）、`:53` 追加 `updateOwner = updateMode = 0;`。同类在 xserver.patch：LOCK_DIR 改 `getenv("TMPDIR") ?: "/tmp"`（`:196-197`）、锁文件 link() 改 rename()（`:206`）、osinit 信号表去 SIGSEGV/SIGABRT/SIGBUS/SYS 防 tombstone 被抢（`:178`）、OsSignal 在 `__ANDROID__` 直返 SIG_DFL（`:187-188`）、`TERMUX_X11_NOTIFY_PARENT` 旁路 SIGUSR1（`:157-163`）。

### 3.3 进程内嵌入：xkbcomp 与 GL stub 两场手术

**xkbcomp 嵌入链**横跨三 patch。上游用 `Popen("xkbcomp ...")` fork+exec `/bin/sh`——Android 无 /bin/sh、无独立二进制、selinux 限 exec。改造：①`xkbcomp.patch:832` 把 main() 改 `xkbcomp_main(int, char**)`，砍掉全部 Display 依赖（`:870-1010`），只留"解析 .xkb→XkbWriteXKMFile（`:892`）"单一路径；`:9-53` 从 xserver 搬来 `XkbComputeEffectiveMap` 注入 alias.c 补缺符号。②`xserver.patch:617-631` 把 shell 命令行拆 13 参数填进 ddxLoad.c 的 `xkbcomp_argv` 数组（`:604-605` 声明）。③`xserver.patch:284-294` 劫持 Popen：子进程 dup2 输出管道后 `_exit(xkbcomp_main(...))`；ReportXkbcompOutput（`:226-245`）按成败分流——失败进 stderr，成功逐行 `__android_log_write(ANDROID_LOG_DEBUG, "xkbcomp", ...)`（`:244`）：缺失 keysym 的抱怨无价值，只有失败的 keymap 值得上报。管道 O_NONBLOCK（`:261-263`）——没人排空，满管不能阻塞子进程。

**libepoxy stub 化**方向相反：GLX 扩展大量调 GL 函数，但 GLES 上下文由 lorie 的 renderer.cpp 独管。patch 改 gen_dispatch.py 输出为纯 stub 头：移除 APIENTRY/GLAPIENTRY（`libepoxy.patch:9-10,19`），给每个 GL 函数生成 `#define glXXX(...) 0`（`:116`）。`xs:28-34` 生成 `xserver/GL/gl.h` 把 xserver 的 GL 引用整体短路——glx 代码照样编译，运行时零真调用。

### 3.4 行为改写：DDX 钩子与 Present GPU 卸载

给主循环开钩子：dispatch.c 每请求处理完注入 `ddxRequestDone()`（`xserver.patch:28`）、main.c 就绪注入 `ddxReady()`（`:83`）、enterleave.c 焦点变化注入 `DDXNotifyFocusChanged()`（`:72-73`），实现都在 lorie/ DDX 层。

最深的 **Present GPU 拷贝卸载**（`:337-598` 跨 present 五文件）：vblank 加 `gpu_copy_pending/serial/dst_buffer/damage` 四字段（`:500-503`），present_execute_copy 从同步 CPU CopyArea 改为"先 `lorieTryScheduleGpuCopy`（`:403`）压进渲染进程命令队列，下一 vblank 轮询完成再 ack（`:412`）"；渲染进程死掉/退后台走 present_vblank_scrap 如实告知跳过（`:414-419`）。GPU 直写绕过 Damage 故手动补 DamageDamageRegion（`:432-441`），vblank 销毁补 ack 防泄漏（`:569-594`）；`lorieRecheckGpuCopies()`（`:537-547`）供渲染侧完成通知时重扫，after_flip 回调（`:324,557`）补 flip 通知。这是 02 篇 gpuCopyQueue 回放在 X server 侧的对接面。

小 patch：`x11.patch:9-12,25-30` 把 libx11 三个锁宏置空（进程内单线程）、`:39-42` 绕 locale 探测；`xkbfile.patch:12,24` 让 XkbAtom 函数无视 Display 直走 server 侧 atom 表；`pixman.patch:31` 把 ARM 特性硬编码全开（minSdk 24 全支持）。

**dix-config.h.in**（208 行）是 ./configure 的静态替代：写死全部 HAVE_*（21 个扩展开关 `:107-141`），仅 `SIZEOF_UNSIGNED_LONG` 经 `xs:1` 动态注入决定 `_XSERVER64`（`xs:81-83`）。`:180-199` 手写 memfd_create syscall 号表（i386=356、arm=385、aarch64=279）；`:204-206` 把 `setgid/setuid` 置空——应用无权换 uid，但 server 逻辑要求降权"成功"才继续。

## 四、数据流：从 git clone 到 libXlorie.so

1. **检出**：手工 `git submodule update --init --recursive`；
2. **configure**：`build.gradle:41` 触发 CMake → `root:80` 依序 include → 先生成物（dix-config/version-config/xkb-config `xs:2-24`、Xpoll.h、ks_tables.h、GL/gl.h）→ 幂等打补丁（`xs:300-301` 最后打 xserver+libepoxy）；
3. **编译**：11 基础库 + xserver 的 **24 个静态库** = `xs:274-275` foreach 的 23 个 part + `xs:95` 的 xserver_main——后者**编而未链**（XSERVER_LIBS `xs:273-277` 不含它，是孤儿目标：入口由 cmdentrypoint.cpp 提供，dix_main 来自 xserver_dix，stubmain 多余）；
4. **链接**：`xs:279` 以 13 个 lorie 自有源文件为主体建 `Xlorie SHARED`，`xs:298` 把 XSERVER_LIBS 夹在 `--whole-archive/--no-whole-archive` 之间链入，再接 android/log/m/z/EGL/GLESv2。whole-archive 是点睛：X server 符号经 ScreenPtr/extension 入口表间接注册、无显式引用者，不加则整片被裁，运行时才发现扩展缺失。

## 五、设计决策

**-nostdlib++：不依赖 libc++ 的 C++ 共享库**。`xs:294-297` 注释直陈：三个 C++ 文件被限制在 runtime-free 子集——无异常、无 RTTI、无 STL（`xs:299`），换 `-nostdlib++` 资格。收益：libXlorie.so 不携带 libc++，APK 更小，且 app_process 环境的 System.load 避开 NDK 运行时库路径问题（05 篇）。

**patch 就地改 submodule**：`-d` 目标是 submodule 工作区（`xs:300`），改动不进 git 索引。升级上游 = 移指针 + 重放 patch。

**Xau.cmake:4 笔误（勘误钉版）**：Xau 配方里写着 `target_compile_options(Xdmcp PRIVATE ...)`——选项错安到 **Xdmcp** 目标头上（Xdmcp.cmake:3 自有一份），Xau 本体没吃到这组选项。当前仅 2 文件侥幸无症状，动 Xau 前先修。

**宿主 gcc 编 makekeys**（`xkbcomp.cmake:7`）：生成物是构建期表头不进目标机，宿主编一次最快。

**生成优于配置**：一切 HAVE_* 由 `-D` 宏与三个 file(GENERATE) 产物写死，升级 NDK 需人工重审（`HAVE_MEMFD_CREATE 1` 在 minSdk 24 不可用，由 dix-config.h.in:180 补上）。

## 六、新人提示

1. **改 patch 的陷阱**：dry-run 检测意味着改 patch 内容后，旧版已应用会被静默跳过——须 `git submodule foreach git checkout -- .` 重置后重跑 configure。
2. **新增上游库**：.gitmodules 加条目 → recipes/ 加配方（照抄 Xdmcp.cmake 起步）→ `root:80` 按依赖位置插队；库自带构建系统直接无视，抄源文件路径进 add_library。
3. **排障**：patch 失败在 configure 阶段 stderr 现场打印；构建期 xkbcomp 输出在 logcat 的 `xkbcomp` tag；whole-archive 类裁剪问题的症状是运行时 "extension not found" 而非编译错误。
4. **别在 xserver/ 目录找本仓改动**——那里是空的，差异全在 patches/ 与 recipes/。读 xserver.patch 开上游源码对照；present 段配合 02 篇读。
5. **升级雷区**：submodule 指针前移必撞 patch（present 五文件组重构频繁）；Xau.cmake:4 笔误动 Xau 前先修。
