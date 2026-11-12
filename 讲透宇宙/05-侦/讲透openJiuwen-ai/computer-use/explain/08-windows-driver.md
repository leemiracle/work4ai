# 08 · Windows 驱动全栈——Driver.cs / UiaClient / WGC 截屏 / 双进程 capture worker

## 一、角色定位

`os_adapter/windows/` 用 C# 实现 protocol-6 驱动的 Windows 版，与 macOS 驱动互为镜像（tour S09 原话）。四个文件构成两级进程：

- **主驱动进程**：`Sources/Runtime/Driver.cs`（364 行）——stdin 行协议分发器：hello/版本/会话校验、请求去重三态、busy 串行、cancel 通道，全部 UIA 构造走单 MTA 工作队列；`Sources/Objects/NativeUiaClient.cs`（570 行）——UIA 客户端封装，**弃托管 System.Windows.Automation 遍历、直用 native COM 客户端**（类注释 L15-17："Managed traversal can omit cross-process hosted fragments"）。
- **capture worker 进程**（`computer-use-capture.exe`，同目录部署，NativeWindowPixels.cs:17 定位）：`Workers/Capture/Program.cs`（294 行）——截屏双路由 WGC/PrintWindow + 进程身份复检 + OCR（同进程的 `Workers/Capture/Ocr.cs`）；`Sources/Capture/NativeWindowPixels.cs`（82 行）——主驱动侧的 worker 客户端：起进程、发参数、轮询读回、降级决策。

这套设计回答：**当 UIA（COM）与 WGC（D3D/WinRT）两套重量级 COM 状态不宜共居一进程时，如何拆进程并保持身份证明**。

## 二、内部结构

**Driver.cs——分发器**
- 字段群（L15-31）：`gate`（请求/账本锁）与 `output`（写 stdout 锁）分离；`work = BlockingCollection<Action>`（L17）即 MTA 工作队列；`requests/replies` 两字典+`order` 队列+`bytes`（L18-19）构成账本；`const int version = 6`（L27）；`volatile hello/stopping/negotiating`（L29）。
- `Receive`（L128-251）：BOM 拒绝（L133-134）→ cancel 帧（L136-149，`active == cancelled && cancellation != null` 才 Cancel）→ version_mismatch（L153-156）→ **hello**（L159-193：`hello || negotiating` 双拒 L162；mode 必须等于环境变量 L168-172；**runtime 构造投进工作队列** L177-191，注释 L174-175"All UIA construction and use belongs to the same windowless MTA worker, including future COM providers"；失败回 execution_failed L186-190）→ session_mismatch（L196-199）→ `timeoutMs ∈ 1..120000`（L204）→ canonical 指纹（L205）→ **准入三态**（L207-239：同 id 异内容 `request_conflict`/同 id 同内容已回 `replies` 重放/在执行 `in_progress`；`current <= high` 水位拒 `request_expired` L221-225；`busy` 拒并 `remember: true` L229-233；通过则 `active = current` + 新 `CancellationTokenSource` + 入队 `Execute`）。
- `Execute`（L253-294）：方法白名单 begin/inspect/capture/execute/finish（L259-266）；`native.Perform` 后**成功回执原样透传**——注释 L269-271："Units journal cancellation after possible dispatch in their receipt. Do not replace that receipt with a generic error"（单元自己记账取消后可能已派发，别用通用错误覆盖）；异常翻译：`ElementNotAvailableException → stale_target`（L276），effect 三档 `r.Dispatched ? "partial" : r.Effect ? "possible" : "none"`（L277）；**响应发布在租约释放之后**（L282-285，注释："the client may immediately send its next command when it receives this response"——checkpoint 先取，锁内清 active/Dispose cancellation 再 Reply）。
- `Run`（L296-362）：reader 后台线程逐字符切行（L312-329，**64MB 请求帧上限** L325-326，无效 UTF-8 由 `UTF8Encoding(false, true)` 抛出 L307）；主循环 `work.TryTake(25ms)` 空转时 `native.Expire()`（L348-355）；EOF/异常都 `Stop()`（L339-342）。
- 附加通道：`Display`（L54-58）可主动推 `visualPointer` 通知帧；`Reply` 在有 checkpoint 钩子时给响应附加 `windowCheckpoint/recycleReadWorker/pointerCheckpoint`（L67-77），供引擎侧回收 worker 状态。

**NativeUiaClient.cs——COM 客户端**
- `[ThreadStatic] client`（L26-27）+ 惰性反射建 `CUIAutomation8Class`（L34）；**`AutoSetFocus = 0`**（L38，注释 L35-37："UIA defaults to focusing before control-pattern actions. Focus preparation belongs to our explicit desktop policy, not a hidden side effect"——拒绝 UIA 的隐式抢焦点副作用）。
- `MinimumTransactionMs = 50`（L25）：UIAutomationCore 对更小的 TransactionTimeout 回 E_INVALIDARG（注释 L22-24）；`TransactionBudget` 用 IDisposable 暂存/恢复（L109-129）。
- `PatternIds()`（L57-88）反射枚举 `UIA_Is*PatternAvailablePropertyId` 全集并配对 pattern id（含 Pattern2 的版本号在后的命名陷阱，L70-73 注释）；`ControlTypes` 也靠反射构建（L53-56，注释：`LookupById` 不触发 ControlType 注册表初始化）。
- `Call<T>`（L90-102）把 COMException `0x80040201` 翻译成 `ElementNotAvailableException`——这是 Execute 里 stale_target 翻译的源头。
- `SameCom`（L153-169）用 IUnknown 指针比较 COM 对象同一性，用于识别 `ReservedNotSupportedValue/ReservedMixedAttributeValue` 两个 COM 哨兵值（L191-194）；`DecodeValue`（L185-235）把 ControlType/BoundingRectangle（4 元组→Rect，L210-217）/六个枚举属性翻回托管类型。
- 遍历用 `RawViewWalker`（L131-144，不过滤视图）；`Cache`（L237-246）以 `RawViewCondition + AutomationElementMode=1`（Full，注释 L242："input uses the retained native object"——缓存请求保留原生对象供输入用）。
- `UiaElement`（L249-397）：FromHandle/FromPoint/TryClickablePoint/GetRuntimeId/Snapshot(BuildUpdatedCache)/CachedChildren/`TryGetCurrentPattern`（容忍 `UIA_E_NOTSUPPORTED 0x80040204`，L344-346）；`UiaTextPattern`（L401-428）双构造承接 native 与 legacy 托管两来源，注释 L399-400："Native text ranges remain objects, never inferred offsets"（文本区间保持对象身份，绝不推断偏移）。

**NativeWindowPixels.cs——worker 客户端**：`Read`（L15-80）双路由循环 `{"wgc","print"}`（L21-27）：每轮先 `request.Check()+window.Validate()`（L29-30）；向 worker 发 `route/handle/pid/started/maxDimension`（L35）；wgc 给 2500ms、print 给 1500ms 截止（L36）；读回后再 Validate+Check（L49-50）并校验 helper 像素尺寸与几何一致（L53-54）；print 路由成功时在 `Notes` 里诚实声明（L60-63）："Compositor capture unavailable … completeness of GPU-composited content is unknown. **No screen-region substitution performed**"；`cancelled/deadline_exceeded/stale_target` 三码不换路由直接上抛（L69-71），其余失败记入 `failures` 试下一路由，双败则 `observation_unavailable`（L79）。

**Workers/Capture/Program.cs——worker 主体**
- `Compositor`（wgc，L118-206）：`GraphicsCaptureItem` 经 activation factory 创建（L121-131）；`Direct3D11CaptureFramePool.CreateFreeThreaded` 双缓冲（L136）；**保留系统截屏指示器**（注释 L139-142："Keep the OS capture indicator. Reading never requests borderless capture privileges or changes foreground"，仅关光标捕获）；1500ms 等帧（L146-154）；帧尺寸≠请求尺寸即"window resized during compositor capture"（L157-158）；用 `DwmGetWindowAttribute(attr 9)` 扩展边界与 `GetWindowRect` 校验屏幕坐标映射，映射不上即拒（L159-164）；`SoftwareBitmap` 异步读回 2000ms（L165-174）逐行 `Marshal.Copy` 成 32bppPArgb（L185-195）。
- `Painted`（print，L208-244）：切线程 DPI 上下文匹配窗口（L210）；黑底+`PrintWindow(h, dc, 2)`（PW_RENDERFULLCONTENT，L226）；失败即"PrintWindow did not supply pixels"（L233-234）。
- `Device()`（L64-108）：D3D11 硬件创建失败回退 WARP 软渲染（L70-86），finally 全量 `Marshal.Release`（L94-107）。
- `Main`（L246-292）：`[MTAThread]`；PerMonitorV2 DPI（L255）；**窗口身份复检**（L260-264）——`IsWindow`+`GetWindowThreadProcessId` 比对 pid+`IsIconic` 拒最小化+`Process.StartTime` ticks 与请求携带的 `started` 严格相等（"window process changed"）；capture 前后 Bounds 不变（L265-270）；PNG 超 32MB 拒（L276-277）；`visualText = CaptureOcr.Read(...)`（L280）——**OCR 就在这个 worker 进程里**；异常回 JSON error 帧+exit 1（L287-291）。

## 三、外部连接

- **上游**：引擎侧 `connection.py` Windows 分支直接 spawn 驱动 exe（`CREATE_NO_WINDOW`，connection.py:129-133），无 POSIX fd 桥/preview 管道（环境变量 `COMPUTER_USE_PREVIEW_FD/LIFETIME_FD` 被显式 pop，connection.py:130-131）；EOF 关 stdin 是宿主的优雅退出信号（`_on_exit` 走 `stdin.close()`，04 篇）——对应本侧 reader 线程 EOF→`Stop()`。
- **进程内**：`INativeRuntime`（Driver.cs:20 工厂注入）是全部域能力的接口；`Request`（L237）携带 CancellationToken+deadline+Dispatched/Effect 标志；`NativeChildProcess`（NativeWindowPixels.cs:33）是 worker IPC 封装。
- **系统边界**：UIAutomationCore（COM）、user32/dwmapi 九个 P/Invoke（Program.cs:35-52）、D3D11+WinRT WGC 栈。

## 四、数据流

一次窗口截屏 `capture`：引擎帧 → `Receive` 准入（指纹/水位/busy）→ 入队 → `Execute` → `native.Perform` → `NativeWindowPixels.Read` → spawn `computer-use-capture.exe` → worker `Main`：身份四查（L260-264）→ wgc 路由（合成器像素）→ 失败（如 DWM 映射不上）则 print 路由（应用自绘像素+Notes 降级声明）→ PNG base64+rect+visualText 一行 JSON 回主驱动 → 主驱动再 Validate+尺寸对账（L49-54）→ Reply（remember:true）。模型端拿到的截图永远带几何与降级标注；worker 崩溃/超时被隔离在子进程，主驱动的 UIA 状态不受牵连。

## 五、设计决策与权衡

1. **双进程隔离**：UIA 的 MTA COM 线程文化与 WGC 的 D3D/WinRT 异步栈放同一进程会互相干扰（FreeThreaded 帧池、DPI 上下文切换都是进程级副作用）；worker 独立进程同时天然获得崩溃隔离与 1500/2500ms 硬超时。代价：每张截图一次进程创建 + 一行 JSON IPC——对截图频率（读屏循环）可接受。
2. **身份证明搬进 worker**：主驱动已验过窗口身份，worker 收到 handle 后仍复检 pid+StartTime+IsWindow+几何不变（Program.cs:260-270）——**TOCTOU 防线**：spawn 与截屏之间窗口可能已被销毁/复用，与 macOS BackgroundTarget 的内核出生身份思想同构（Windows 用 Process.StartTime ticks 对应 macOS 的进程出生时间）。
3. **诚实降级而非静默替换**：print 路由明言 GPU 合成内容完整性未知、且"No screen-region substitution performed"（不拿桌面区域截图冒充窗口内容）；这一句会随 Observation 送达模型，让上层自主决定是否换桌面级读取（NativeWindowPixels.cs:79 的 next 建议正是"use an explicit desktop screenshot"）。
4. **UIA native COM 而非托管**：托管遍历漏跨进程 hosted fragments（类注释 L15-17），且 `AutoSetFocus=0` 消灭 UIA 隐式抢焦点（L35-38）——把"是否聚焦"收归显式桌面策略，与 macOS 驱动"菜单弹窗要前台"的约束同源。
5. **账本与 macOS 同构**：64 条/8MB、水位线、busy 也入账（Driver.cs:229-233 vs Driver.swift:214）——三端协议行为一致性靠这套结构复刻，而非共享代码。
6. **响应发布时序**：Reply 必须晚于 input cleanup 与租约释放（L282-285）——宿主收到响应即可发下一命令，若响应先于清理发出，下一命令可能撞上未释放的输入状态。

## 六、新人提示与坑

- **勘误（真文案 bug）**：Driver.cs:267 的错误信息写 `"method '" + method + "' is not supported by protocol v5"`——本驱动 `const int version = 6`（L27），v5 是历史遗留文案。给上游提 PR 的话这是一行修复；排障时别被"v5"误导去查协议版本不匹配。
- **勘误（tour 措辞精确化）**：tour S09 说"OCR 独立 worker 进程"——OCR（`Workers/Capture/Ocr.cs`）确实在独立进程里，但那是**截屏 worker 进程**（computer-use-capture.exe），不是专门的 OCR 进程；进程边界是"驱动 vs 截屏+OCR"，不是三进程。
- **64MB 上限两侧各一半**：Driver.cs:325 限制的是**请求帧**（stdin），引擎侧 connection.py:726 的 64MB 限制的是**响应帧**（stdout）——两侧都有，方向相反，别混引。
- **`negotiating` 标志别删**：hello 处理是投进工作队列异步执行的（L177-191），`negotiating` 挡住"队列还没跑完又来一个 id=0"的窗口；去掉它会出现双 runtime。
- **UiaClient 是 `[ThreadStatic]`**：COM 客户端每线程一个；所有 UIA 调用必须发生在工作队列线程（含 hello 里的 runtime 构造），在别的线程碰 `Current` 会静默创建第二套 COM 状态。
- **PrintWindow 标志 2 = PW_RENDERFULLCONTENT**：能捕获 DirectComposition 内容，但对 GPU 合成的顶层内容仍可能不完整——这正是 Notes 降级声明存在的原因；别以为 print 路由"成功"就等价 wgc。
- **worker 的 `started` 参数是字符串 ticks**（`window.Started.ToString()`→`Int64.Parse`，NativeWindowPixels.cs:35 / Program.cs:263）：跨进程传 Process.StartTime 的 UTC ticks 字符串；精度对不上（本地 vs UTC）会恒报 "window process changed"——改这块时保 UTC 转换（`.ToUniversalTime().Ticks`）。
