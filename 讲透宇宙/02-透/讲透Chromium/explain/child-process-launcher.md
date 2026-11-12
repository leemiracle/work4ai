# child_process_launcher.cc 精讲 —— Chromium 子进程统一孵化器

> 源码：`content/browser/child_process_launcher.cc`（463 行）+ 同名 `.h`（400 行），commit 8fe2331。
> 图谱：8 节点（1 file + 7 function），16 步导览第 2 步「启动与进程孵化」代表文件。

## 一、角色定位

Chromium 多进程架构下所有子进程的"出生"走同一入口——`ChildProcessLauncher`。类注释写明动机：异步孵化并在完成时通知 client，因为 OS 建进程"can take > 100 ms"，不能阻塞调用线程（`.h` L219-221）。

两类宿主都持有它：`RenderProcessHostImpl::Init()`（render_process_host_impl.cc L2161）孵化 renderer；`BrowserChildProcessHostImpl`（browser_child_process_host_impl.cc L342）服务 utility/GPU 等非 renderer 子进程。除"生孩子"外还管**收尸归因**（`GetChildTerminationInfo`）与**优先级仲裁**（`RenderProcessPriority` 聚合可见性/媒体/XR/service worker 等十余信号）。平台脏活委托 `ChildProcessLauncherHelper` 五平台实现，本文件只做跨平台编排。

## 二、内部结构

**构造函数（L107-151）——"构造即启动"。** 收十余参数（delegate/命令行/回调/mojo invitation/共享内存 region，L108-120）；sanitizer 构建下 `terminate_child_on_shutdown_` 置 false 让子进程活到 dump 完（L123-128）；L131 `CHECK_CURRENTLY_ON(BrowserThread::UI)` 钉死线程契约；L139-149 组装 `helper_`（L141 传 `WeakPtr`），L150 交棒。

**Notify（L185-226）——启动完成分发。** private（`.h` L341 `friend` 授权）。置 `starting_ = false` 接管 `process_`（L196-197）；成功记 `process_start_time_`（L200）、Mac task port 未就绪挂观察者（L202-212）、L215 `OnProcessLaunched()`——注释 "May delete |this|"（L214）：回调后 `this` 可能已死；失败置 `TERMINATION_STATUS_LAUNCH_FAILED`（L217）并回调（L224）。

**GetChildTerminationInfo（L273-320）——终止归因。** `known_dead` 语义见 `.h` L299-305：Linux 已知死亡置 true，避免死进程被看成活着。句柄无效返回缓存（L277-285），否则 `helper_->GetTerminationInfo()` 回填（L293-300）。L302-317 是关键坑：crash 时其 `waitpid(WNOHANG)` 已 reap 子进程，子进程仍活则需 ProcessWatcher 兜底，故仅非 STILL_RUNNING 才 Close（L308-309）并释放 helper 侧副本。

**优先级三件套。** ①`RenderProcessPriority` 构造（L358-395）：纯字段赋值，尾部分叉——Android 收 `ChildProcessImportance`，其余收 `std::optional<base::Process::Priority> priority_override`（L368-375）。②`is_background()`（L403-432，`.h` L113 已 DEPRECATED）：无 override 时为七布尔全否定与（L428-431），有 override 仍留例外——前台 service worker 不得饿死（L419-423，crbug.com/484218883）。③`GetProcessPriority()`（L434-458）：唯一正确出口，override 例外返 kUserBlocking（L441），兜底三目（L456-457）。

**其余成员**：`SetProcessPriority`（L173-182）幂等去重后 PostTask 到 launcher 线程设 OS 优先级（L251-259），Mac 需 task port、`OnReceivedTaskPort`（L229）到货补设；析构（L153-160）按 `terminate_child_on_shutdown_` 异步杀活进程（L157）；`Terminate`（L322-332）IsStarting 拒绝、否则转静态 `TerminateProcess`；另有 Android 辅助段与 trace 序列化（L334-349/L64-87）。

## 三、外部连接

**依赖**：base 工具件；content 层 sandbox delegate 头、`browser_thread.h`、`child_process_launcher_utils.h`（L18 定义 `GetProcessLauncherTaskRunner()`，本文件四处 PostTask 全靠它）。

**被依赖**：两大消费方 RPH 与 BCHI 头文件、五平台 helper、browsertest。调用点：RPH 构造（L2161）与终止转发（L5709）；BCHI 构造（L342）与 `SetProcessPriority`（L365）。

**与 helper 双向持有是骨架**：本文件持 `helper_`（L139），helper 持 `WeakPtr`（L141）——launcher 先死不悬空，helper 回报时判空、孤儿进程直接杀（helper.cc L467-469）。

## 四、数据流：从构造到子进程就绪

1. **UI 线程**：宿主构造 launcher 并启动 helper（L139-150）；helper 跑平台钩子 `BeforeLaunchOnClientThread`（helper.cc L267）后把 `LaunchOnLauncherThread` Post 到 launcher 线程（L269）。
2. **launcher 线程·主战**：`LaunchOnLauncherThread`（helper.cc L275）建 mojo 平台通道（L285-288）→ 透传 histogram/field-trial/tracing 句柄与 trace UUID（L330-348）→ **sandbox 先行**：`BeforeLaunchOnLauncherThread`（L356，平台做 sandbox 初始化）返回 true 才 `LaunchProcessOnLauncherThread`（L357）。
3. **平台孵化分叉**：Linux 有 Zygote 走 `ForkRequest`（helper_linux.cc L93）fork 出沙箱化子进程并调 `AdjustRendererOOMScore`（L105）；无 Zygote 才 `base::LaunchProcess` 直接 spawn（L112），判定即 `!GetZygoteForLaunch()`（L52）；Android/Windows 各走 ChildProcessConnection/sandboxed spawn。
4. **回报与交付**：`PostLaunchOnLauncherThread`（helper.cc L378）→ `PostLaunchOnClientThread`（L451）记总耗时（L459-460）后调 `Notify`（L462）；Notify 按句柄有效性二分（L199/L216），成功则 `OnProcessLaunched`——宿主拿到 `base::Process`，子进程就绪。

**优先级通道**是第二条流：RPH 聚合 `RenderProcessPriority` →（非 Android）`SetProcessPriority`（L173）→ launcher 线程设 OS 优先级（L254-258）；Mac task port 到货补枪（L229-246）；Android 整条直传 helper（L163-171）。

## 五、设计决策

**为什么统一孵化器而非各自 spawn？** ①防 UI 卡顿是硬指标，统一入口才能统一保证"构造即异步、结果必回调"，方法全 CHECK 在 UI 线程（L131 为代表）、阻塞调用全在 launcher 线程；②横切能力一处注入——histogram/field-trial/tracing 共享内存与 trace UUID 每个子进程都要，各宿主自 spawn 得复制五遍；③终止归因统一，crash/kill/退出的判别（含 Zygote 代理 reap）高度平台相关，收敛一份维护。

**Linux Zygote fork vs 直接 spawn**：renderer 沙箱需先 drop 权限，从 Zygote fork 复用已初始化镜像（ICU 等不重复初始化）且 fork 在已降权进程中更安全；故"有 Zygote 必走 Zygote"（helper_linux.cc L52/L88-93），终止状态亦经 Zygote 代理查询（L139-140）。

**priority_override 例外清单**（L436-454）体现治理演进：正路迁 performance manager 投票（L437/L443 两处 TODO），迁移完成前"service worker 不得被 override 压死"以例外硬编码。

## 六、新人提示

**三条铁律**：①线程契约——UI 侧加 `CHECK_CURRENTLY_ON`，碰进程句柄的 OS 操作 Post 到 launcher 线程。②Notify 的 `OnProcessLaunched()` 之后 `this` 可能已死（L214），回调后不得再访问成员。③优先级只动 `GetProcessPriority`，消费侧禁读字段自算（`.h` L124-125）。

**坑**：POSIX 下 GetChildTerminationInfo 不能无条件关句柄（L302-317）；Windows `last_error` 要从 launcher 线程带回 UI 线程（helper.cc L367-372）；Client 的 Android 三默认实现（`.h` L241-252）embedder 可覆写；`LAUNCH_RESULT_START = 1001` 避开 `sandbox::ResultCode` 数值区间（`.h` L70-87），新枚举只能加尾。

**测试与调试**：唯一用例 `ChildSpawnFail`（browsertest L54，故意 spawn 失败）；优先级回归在 RPH 与 performance manager 侧。调试用 `--wait-for-debugger-children[=<type>]`（helper.cc L319-327）与 `MPArch.ChildProcessLauncher.*` 直方图。

**一句话总结**：`child_process_launcher.cc` 是 content 层所有子进程的"产房+户籍科"——UI 线程异步孵化、跨平台委托 helper、Notify 交付句柄、GetChildTerminationInfo 归因善后，RenderProcessPriority 垄断优先级换算。
