# 04 · native 桥接与三值安全契约——connection/contracts/port

## 一、角色定位

Python 引擎与三平台驱动之间隔着一条子进程 JSON-lines 通道，这组文件是通道的**Python 侧全部**：

- `computer_use_engine/native/connection.py`（947 行）的 `Connection`：驱动子进程全生命周期——spawn、hello 握手、单请求串行、两级超时、取消、跨代退休。模块 docstring（connection.py:4）立宪：**"One native request at a time; cancellation and uncertain input never replay."**（一次一个 native 请求；取消与不确定的输入绝不重放）。
- `computer_use_engine/native/contracts.py`（552 行）：与驱动共享的 typed 词汇表，约 25 个 frozen dataclass。docstring（contracts.py:5-7）点明分工："Python selects routes from observed facts. Native execution units check the target and route again at dispatch time."
- `computer_use_engine/native/port.py`（142 行）：`NativePort` Protocol——把 6 个 wire 方法膨胀成读/写管线可用的 15 个语义操作（port.py:54-141），是 native 能力暴露面。

共同回答：**如何在不可靠的进程边界上，保证"不确定"永不被当作"成功"或"失败"处理**。

## 二、内部结构

**connection.py**
- 构造（L59-73）：协议版本 `type(...) is not int` 精确校验且必须等于 `NATIVE_PROTOCOL_VERSION`（L62-63）；`session_identity = (generation, session)`（L88-90，docstring："internal lease cannot migrate across process retirement/reconnect"）。
- `_connect`（L98-184）：平台白名单 darwin/linux/win32（L101-107）；Windows 直接 spawn + `CREATE_NO_WINDOW`（L129-133），POSIX 经 `python -m computer_use.native.driver_exec` 桥接 fd3 preview 管道与可选 lifetime fd（L135-145）。stderr 每行优先按 JSON 解析（L222-236），带 requestId 的行关联 traceId 进诊断流。
- `_request`（L300-721）主闸门：方法白名单（L301-304）→ 单飞检查（L305-306）→ 每方法参数 decode（L307-332）→ 预算 deadline（L333-339）→ 等退休中驱动（L352-373）→ connect+negotiate（L374-400）→ **近 20 项 capability 门禁**（L410-638，由 method+params 形态推导所需 capability，如 `begin(mode=write)` 要 `nativeBoundContracts`、launch 意图要 `nativeLaunch`；全部在写 stdin 之前，错误文案统一"no system command was sent"）→ id/trace 分配（L639-643，trace 表超 1024 先进先出）→ 两级定时器（L673-702）→ 写帧（L704-714）。
- `_receive`（L723-830）帧纪律：64MB 上限（L726-727）、BOM 拒绝（L732-733）、`parse_constant` 拒 NaN/Infinity（L735-738）、hello 后/response 后不允许多余字节（L742-743、L777-778）、version+session 一致（L762-773）、响应 id 严格匹配（L774-776）。
- `close`（L847-943）：`_generation += 1`（L849）；对 in-flight pending 按 `pure` 分流（L661 判定 capture/capturedText 为纯）；`self.invalidate()` 回调 SDK 层（L907）；Windows 走 stdin EOF、POSIX 走 terminate（L913-919，注释 L188-189：TerminateProcess 不执行驱动 finally，EOF 让驱动读端自行取消）；`retire()` 给 1000ms 宽限再 kill（L921-943）。两个宽限常量钉在 L40：`requestCleanupGraceMs=750`、`driverTerminationGraceMs=1000`。

**contracts.py**
- 枚举五连：`Knowledge`（YES/NO/UNKNOWN，contracts.py:23-26）、`Channel`（L29-33）、`Dispatch`（NOT_DISPATCHED/DISPATCHED/PARTIAL/UNKNOWN，L36-40）、`Confirmation`（L43-47）、`Cleanup`（L50-53）。
- 身份类：`Intent`（L61-71，11 种 kind 白名单，参数冻成 MappingProxyType）、`Binding`（L74-116，六字段身份；`canonical` L99-116 拒绝"Native begin changed an already bound target"）。
- 执行证据链：`Primitive`（L440-466，supported/readiness/background_preparation 全 Knowledge）→ `Facts`（L469-497，identity/within_scope/enabled 三值）→ `UnitCommand`（L515-527）→ `StepResult`（L529-552，`retry_reason` 白名单三值 + L549-552 断言"A possibly dispatched or unclean step cannot authorize retry"）。click 证据包（L343-437）的 `ClickReceipt.permits_replanning`（L408-418）是重规划的唯一放行闸。

## 三、外部连接

- 上游：`interaction/controller.py:68` 以 `Connection(self.invalidate, ...)` 构造并焊死失效回调；`native/transport.py` 的 ConnectionPort 实现本 Protocol；`native/lifecycle.py` 管 calls 准入。
- 下游：read/write 域只 import contracts 词汇与 NativePort 类型——对"驱动是子进程"零感知。
- 对端：macOS Driver.swift 的 hello 双向校验、Windows Driver.cs 的 BOM/64MB、Linux server.py 的 JSON-lines（05/06/08 篇）——同一协议的四份实现。
- `native/preview.py` 经 `_track(read_previews(...))`（connection.py:169）消费 fd3 截图预览流，与主 stdout 分离。

## 四、数据流

一次 `execute`：`request()`（L268）`_requesting` 互斥 → `decode_unit_command` 校验 → capability 推导与门禁（此刻 stdin 零字节）→ 写帧 + 两级定时器：`timeout_ms_local` 到点先发 cancel 帧并打 `request_cancelling`（L673-700），再给 750ms 清理宽限，宽限内无终态即 `close` 整条连接（L688-697）→ `_receive` 校验五连后 resolve future。**事故路径**：连接任何时刻 close，in-flight pending 被翻译——纯请求得 `execution_failed, effect="none"`；非纯请求得 `execution_unknown, effect="possible"`，detail 明言"command may have partially executed; current observation invalidated"，next 要求"reconnect by reading the target; inspect its state before retrying an action"（L874-889）。这就是"不确定输入绝不重放"的执法现场——不是禁止重试，而是强制"重试前必须重新读取"。

## 五、设计决策与权衡

1. **三值而非布尔**：`Knowledge.UNKNOWN` 分开"读不到"与"不存在"；`Dispatch.PARTIAL/UNKNOWN` 分开"部分派发"与"结果未知"；`StepResult.retry_reason` 构造期断言不可伪造——重试授权是**结构性保证**，不靠调用方自觉。
2. **门禁全部前置到发送前**：校验失败与驱动失败在 effect 语义上严格分层——前者绝对安全（effect=none），后者才进 unknown/partial 语义。
3. **单请求串行双层**：外层 `_requesting`（L269）挡并发入口，内层 `_pending is not None or _waiting_for_exit`（L305）挡 connect/retire 窗口。吞吐=1 的代价换来响应匹配、取消语义、缓冲状态机全部单线程化。
4. **generation 而非复用**：close 不复用子进程，只递增 generation 并后台收尸；下个请求全新 spawn，`_retiring` 未结束要 shield 等待（L352-373）。旧驱动 stderr 被 `if self._child is child` 守卫隔离（L246）——"retired drivers still report cleanup... never alter a successor's failure context"（L244-245 注释）。
5. **平台差异显式化**：`_child_uses_eof`（L73、L162）一个布尔承载两种进程文化（Windows EOF / POSIX SIGTERM），而非散落的 if windows。

## 六、新人提示与坑

- **勘误（图谱 tour 量词）**：S05 说"20 余项前置门禁"——实数 capability 检查块约 17 个 if（覆盖 19 个 capability 名，connection.py:410-638），写"近 20 项"更准。
- **cancel 帧≠取消成功**：`_cancel_pending` 只保证发一次（L836-845），裁决在 750ms 宽限后的 `terminal_timeout`；宽限内驱动回了终态照常 resolve（注释 L822-823："A queued reply can arrive after task.cancel()..."）。
- **`traces` 表是 1024 上限 FIFO**（L642-643）：老 id 的 traceId 被挤出后 stderr 关联（L234-235）查不到——诊断缺失≠没有 trace。
- **`finish` 是白名单里最"裸"的方法**（L301）：无 decode、无 capability 检查，params 原样透传，靠 lifecycle 租约语义兜底。
- **`Binding.same_target` 就是 `==`**（L95-97）：注释明言"Capture identity is part of the binding because it owns the pixel map"——六字段全等才是同目标，别用子集比较。
- 全篇 `missing_xxx = True if (...) else False` 模式（L450-455 等）密集——读时先找 if 主体再读条件，别从左往右硬啃。
