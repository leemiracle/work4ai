# 06 · macOS 驱动——Swift 单可执行体的基座、读屏与身份证明

## 一、角色定位

`os_adapter/macos/` 是一个 Swift Package（`Package.swift:6-9`：swift-tools 6.0，唯一 executable target `ComputerUseDriver`，产物名 `computer-use-driver`，平台钉死 macOS 14+）。它与 Windows 驱动互为镜像，回答同一组问题的 Swift 版：**如何在主线程 actor 约束下实现 protocol-6 的 JSON-lines 服务端，并且在给任何进程发输入之前证明"我观察到的进程还是当初那个进程"**。

本篇覆盖两层：

- **基座层（S07）**：`Runtime/Driver.swift`（296 行）——协议入口与请求准入；`Runtime/Failure.swift`（77 行）——12 错误码×恢复指引×三档 effect；`Contracts/NativeIntent.swift`（54 行）——不可变意图契约；`Runtime/main.swift`——进程文化适配（AppKit 激活策略/SIGPIPE/信号排水）。
- **读屏与控制层（S08）**：`Read/ReadPipeline.swift`（44 行）——inspect 八 case 分派；`Control/BackgroundTarget.swift`（244 行）——进程身份双通道证明；`Control/Routes/NativeRoutePipeline.swift`（37 行）——12 契约分支的路由选择。

辅助件 `Runtime/RequestLedger.swift`（57 行）实现请求去重五态准入，是 `requestDedup` 能力的本体。

## 二、内部结构

**Driver.swift——协议 6 连接入口**
- 类头（L7-17）：`@MainActor final class Driver`，`session = UUID().uuidString`（L8）、`wireVersion = 6`（L9）、lazy 的 `NativeExecution`（L11-12，cancelActive 闭包回流 RequestLifetime）、`ledger = RequestLedger()`（L13）、单活跃 `activeID: Int64?`（L14）。
- `receive`（L79-235）是协议状态机核心：BOM/UTF-8 拒绝（L83）→ cancel 单向控制帧（L88-103，必须 `handshaken`+session 匹配+id 命中 `activeID` 才 `native.cancel()+requests.cancelActive()`）→ id 范围 `0...9_007_199_254_740_991`（L104-105）→ version_mismatch（L109-116）→ **hello**（L117-160：只许一次 L118-120；`desktopMode` 必须等于驱动侧环境变量 `COMPUTER_USE_DESKTOP` 否则 `mode_mismatch` L127-135；回显 41 项 capabilities L142-156）→ session_mismatch（L161-168）→ `timeoutMs ∈ 1...120000`（L170-173）→ **账本五态准入**（L175-208：canonical JSON（sortedKeys+withoutEscapingSlashes）SHA256 指纹 → `replay` 直接回缓存/inProgress/expired/conflict/start）→ **busy 拒绝**（L209-216，注意 `remember: true`——busy 回复本身入账本，重放同 id 会拿到同一条 busy）→ `requests.start(timeoutMs:onTimeout:)` 起任务（L220-222）。
- `performWithinBudget`（L248-294）：defer 清 activeID；`DriverPipeline.validate(method)`（L264，委托 `ValidateNativeMethodPass`）；执行后 **execute 回执的 `errorCode` 或 `cleanup != complete` 只改 metrics 状态不改协议语义**（L267-271 注释："Metrics report that failure, never an application-effect confirmation"）；异常路径把 `cancellationCode`（cancelled/deadline_exceeded）排在分类码之前（L291），effect 用 `including(state.effectPossible)` 单调合并（L283-284，注释："Never let a later no-action validation erase earlier preparation or input"）。
- `shutdown`（L45-58）：先卸 decoration（L48-50 注释：装饰层无输入清理责任，连接一断就该走），再 `await operation?.value` 等输入清理展开，最后 `exit(code)`。

**Failure.swift——事实与恢复指引分离**
- `FailureCode` 12 个（L5-12），每个 case 一句 `next` 恢复话术（L14-37）——例如 `executionFailed/executionUnknown` 共用"read the target before continuing; do not replay input automatically"（L34-35）。这些话术会原样进入 wire 帧，成为喂给模型的错误提示的一部分。
- `FailureEffect.including`（L40-48）：`partial > possible > none` 单调合并——与引擎侧 Dispatch/Effect 语义对齐。
- `NativePreparationUnavailable`（L55-58）：docstring 点明刻意比 `inputUnavailable` 窄——"boundary/focus continuity failures must not grant permission to activate another receiver or replay"。
- `DriverError`（L60-76）：保留 `errorDescription` 防 Foundation Error bridge 把分类信息抹成 NSError 泛文（L66-68 注释）。

**NativeIntent.swift——意图不可变**：docstring（L5-7）"The caller's complete, immutable intent belongs to the operation. A later step selects a native contract; it cannot replace the payload or the intent"。init（L12-25）校验 read↔`kind=read`、write↔11 种 kind、`read/launch/focus` 必须 parameters 空。`NativeBeginRequest`（L28-46）允许 `clickContract v1/v2` 且只配 write click（L41-43）——比 Linux 驱动多一档 v2。

**ReadPipeline.swift——inspect 分派**：`ResolveNativeReadRequestPass` 解析后按八 case switch（L12-42）：五直达 Pass（launch/applications/capturedText/surfaces/roots）、两走 `NativeNodeQueryPipeline`（relation/nodes，前置 `ValidateNativeRelationProfilePass/ValidateNativeNodeProfilePass` 白名单校验 L22、L30-31）、inputContext 走 `NativeInputContextPipeline`。44 行文件是纯分派器，无状态。

**BackgroundTarget.swift——进程身份双通道**（详见第四节）。`ApplicationRegistrationHistory`（L9-29）用 `NSMapTable<NSRunningApplication, Proof>.weakToStrongObjects()`（L19）——weak 键不阻止进程句柄释放；`BackgroundTarget`（L32-47）持 `desktopMode` 静态缓存、`isForeground`（L43-45）、`allowsMenuPopup`（L46）。

**NativeRoutePipeline.swift——路由选择**：`select`（L7-36）按 `resolved.contract.unit` 12 分支派给 `Build*RoutePass`；`launch` 与 `selection` 两契约直接 `invalidRequest`（L15-17——selection 必须走协商过的 click pipeline）。

## 三、外部连接

- **上游**：引擎侧 `native/connection.py` spawn 本可执行体（POSIX 路径经 driver_exec fd 桥，capabilities 对端是 Driver.swift:142-156 的 41 项硬编码清单——与 Linux 驱动的"探测式"生成不同，macOS 全量声明）。
- **进程文化适配在 main.swift**：`ForegroundActivation.runIfRequested`（main.swift:9）先拦截短命激活模式；`app.setActivationPolicy(.prohibited)`（L15）禁止驱动自己抢前台；`signal(SIGPIPE, SIG_IGN)`（L17）防宿主关闭输出管道时驱动提前死亡——注释（L16、L38-39）反复强调"closed pipes/hangup must not terminate us before input cleanup can unwind"；SIGTERM/SIGINT/SIGHUP 转 DispatchSource 排水进 `driver.shutdown`（L40-46）；stdin 用 POSIX `read` 在全局队列阻塞读、按换行切帧回投 MainActor（L48-60，注释 L55：FileHandle 会等缓冲填满而 POSIX read 有多少读多少）。
- **下游依赖**：AppKit（NSRunningApplication/NSWorkspace）、ApplicationServices（AX UI API，`@preconcurrency` 导入 L4——AX API 未标注 Sendable，靠 MainActor 隔离）、CoreGraphics（截屏/事件 tap 权限三连 `CGPreflightScreenCaptureAccess/CGRequestScreenCaptureAccess/CGPreflightPostEventAccess`，Driver.swift:36-37）。
- **被消费**：`NativeExecution`（Driver.swift:11 lazy 构造）消费 BackgroundTarget 与 ReadPipeline；`NativeWindows.belongs`（BackgroundTarget.swift:235）把辅助窗口归属判定下沉到窗口目录服务。

## 四、数据流

**读链路**（inspect/nodes）：stdin 帧 → `receive` 准入 → `perform`（L237-246，`RequestDiagnostics.$id/$metrics/$deadline` 三级 withValue 注入任务局部诊断上下文）→ `native.perform` → DriverPipeline → `ReadPipeline.collect`（ReadPipeline.swift:7-43）：解析 → Profile 白名单（防越权字段/关系）→ `NativeNodeQueryPipeline.collect` 逐节点 → `access.objects.nativeFacts(...)` 读 AX 属性 → 组装 result 帧 → `reply(id, ["result": result], remember: true)`（Driver.swift:272）——**每个终态响应都 remember 进账本**，供重放。

**身份证明链路**（BackgroundTarget.validate，L138-243）——本篇最核心的设计：
1. 构造期（init L106-124）：从**观测现场**（不是查前台）读 `NativeProcessIdentity.read(pid)`（内核进程出生身份：pid+起始秒/微秒+可执行路径）；同时用 `applicationForPID` 查 AppKit 注册表，`isEqual+launchDate` 双匹配则写入注册史。
2. 校验期六连：`isTerminated` 拒（L188）→ AppKit 注册表存在则 `isEqual+launchDate` 必须双匹配（L196-203）→ 注册表缺失时**容忍**当且仅当"内核出生身份可读且注册史已确认"（L204-206，注释 L189-192："AppKit's application registry is metadata, not a complete process table. A missing entry must not invalidate an unchanged kernel birth identity. ... a PID alone never authorizes a target"）→ 内核身份重读比对（L207-215，pid 复用/进程替换在此被抓）→ owner（宿主应用）身份+窗口归属双重校验（L232-240）→ input 时再过 `validateDesktop`（L241）。
3. 任一失败走 `identityFailure`（L154-187）——诊断字段逐项标注"not evaluated"，注释（L147-149）："a later lookup must not replace missing process data"（后查不得顶替缺失证据）。错误码一律 `staleTarget`。
4. 双通道互补：AppKit 注册史（易失、用户态）+ 内核出生身份（权威、可重读）。`launchRegistrationReady`（L131-136）返回 false 只表示"等待"，docstring："False means wait, never permission to observe or send input"。

## 五、设计决策与权衡

1. **账本水位线独立于缓存淘汰**：`RequestLedger` 注释（L6-7）"The high-water mark survives cache eviction: forgotten requests are rejected, never admitted as new work"——64 条/8MB 的缓存会淘汰旧响应（trim 只逐已响应条目，L48-55），但 `highest` 水位永存，旧 id 永远 `expired` 而非误当新工作。这与 Linux 驱动的 `high_id`（05 篇）语义一致、实现更精细（字节数预算）。
2. **busy 回复也入账本**（L214）：同 id 重放 busy 场景拿到确定性的同一条回复，幂等重试安全；`inProgress`/`expired`/`conflict` 三态区分"在执行/记不得/内容变了"（L181-206），全部 `no duplicate was dispatched`。
3. **mode_mismatch 而非自动切换**：hello 要求 SDK 请求的 desktopMode 与驱动环境变量一致（L127-135）；`FailureCode.modeUnsupported` 的恢复话术明言"do not switch modes automatically"（Failure.swift:31）。共享/独占是部署决策不是运行时探索。
4. **读路径的 Profile 白名单前置**：ReadPipeline 在碰任何 AX 对象前先 `ValidateNative*ProfilePass`（L22、L30-31）——字段清单、遍历关系（followRelations 上限 16）等先过白名单，再进节点查询管线；防住"请求什么读什么"的越权面。
5. **诊断通道永不污染协议**：`diagnose` 全走 stderr（与 Linux 侧一致）；`performWithinBudget` 的 metrics 只记 `status`，不掺进 wire 结果（L267-271）；错误 detail 与恢复 next 分开存放的原因写得很直白（L286-287 注释）："Application labels may contain arbitrary prose, including 'Effect:' and 'Next:'"——应用文本里可能出现任意散文，结构化字段不能靠字符串拼接传递语义。
6. **权限请求≠授权**（Driver.swift:29-31 注释）："Requesting access is not evidence of a grant: AX prompts asynchronously, and macOS can require restarting the responsible launcher after approval"——`--request-permissions` 只触发系统弹窗，状态查询与状态请求是两条路径。

## 六、新人提示与坑

- **capabilities 是硬编码的 41 项**（Driver.swift:142-156），含 macOS 独有项（`nativeMenuActions/nativeMenuShortcuts/nativeAXAttributeQueries/nativeVirtualFocus/nativeFocusMembers/nativeFocusScopes/nativeEditorPreparation/nativeSelectedText/nativeBusyFacts` 等）；对照 Linux 的探测式生成（05 篇 native.py:192-204），**不要假设三端能力集合同构**——跨平台调试先 diff capabilities。
- **勘误（易误解处）**：tour S07 说"RequestLedger 五态准入"——五态是 `start/replay/inProgress/expired/conflict`（RequestLedger.swift:9），其中 `busy` 不在五态里，而是五态 `start` 之后的另一道 `activeID` 闸（Driver.swift:209-216）。两层常被混为一谈。
- **cancel 只对活跃请求生效**：`activeID == Int64(n)` 才取消（Driver.swift:97-101）——排队中的请求（已在账本但未 start）收到 cancel 帧是 no-op；引擎侧单请求串行使得该场景罕见，但自定义宿主并发发帧时会踩。
- **AppKit 注册表缺失不是失败**：BackgroundTarget 的核心容错（L189-226）——进程刚启动未注册、或注册表抖动时，只要内核出生身份没变就放行并发 `process_identity_kernel_confirmed` 诊断。看到这条诊断不是 bug，是双通道设计在工作。
- **`@preconcurrency import ApplicationServices`**（Driver.swift:4）：AX C API 无 Sendable 标注，全靠 `@MainActor` 隔离；新加跨 actor 的 AX 调用会撞并发检查——保持 AX 调用在 MainActor 内。
- **hello 之后 session 必须逐帧匹配**（L161-168）：引擎侧重连后 `_next_id` 归 1 会撞 `expired`（水位），好在引擎重连必然换驱动进程；直接对驱动做集成测试时记得 id 单调递增。
- **menu 弹窗的前台约束**：`allowsMenuPopup = isExclusive || isForeground`（L46）——shared 模式下后台应用的菜单操作会被拒；这是产品语义（菜单弹窗会抢用户焦点）不是缺陷。
