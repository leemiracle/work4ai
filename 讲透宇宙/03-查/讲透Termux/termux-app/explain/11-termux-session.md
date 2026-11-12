# 11 TermuxSession.java + ExecutionCommand.java —— 会话执行框架

- `termux-shared/src/main/java/com/termux/shared/termux/shell/command/runner/terminal/TermuxSession.java`（296 行）
- `termux-shared/src/main/java/com/termux/shared/shell/command/ExecutionCommand.java`（691 行）

> 勘误：派发清单所写 `app/src/main/java/com/termux/app/TermuxSession.java` 已不存在——TermuxSession 已迁入 termux-shared 的 `termux/shell/command/runner/terminal/` 包（与 onboarding 一致）。图谱层归属：ExecutionCommand 属 **L05 本地 Socket 与 Shell 命令执行框架层**，TermuxSession 属 **L06 Termux 业务核心层**。

## 角色定位

这一对类构成"一条命令如何变成一个活终端会话"的骨架：**ExecutionCommand 是数据和状态机，TermuxSession 是进程和胶水**。terminal-emulator 的 TerminalSession 只懂 PTY 字节流，ExecutionCommand 只懂字段与状态，TermuxSession 的存在理由就是把两者钉在一起（TermuxSession.java:27-31 类 Javadoc 自述）。

分工上，ExecutionCommand 是 L05 的**通用模型**：前台（Runner.TERMINAL_SESSION）与后台（Runner.APP_SHELL，即 AppShell）执行器共用，插件 socket 服务 AmSocketServer 也直接消费。TermuxSession 是 L06 的**前台专用包装器**：shell 探测、argv/环境组装、进程启动、结果回填。两者不碰 UI/通知——TermuxService 才管（其类声明实现 `TermuxSessionClient`，TermuxService.java:68）。

## 内部结构

**ExecutionState 五态状态机**（ExecutionCommand.java:33-39）：`PRE_EXECUTION(0)→EXECUTING(1)→EXECUTED(2)→SUCCESS(3)`，任意态可转 `FAILED(4)`。守卫全在 `setState()`（:264-279）：回退、或已达 SUCCESS 后再改，一律拒绝返回 false（:266-269）——状态只许前进，SUCCESS 是吸收态；FAILED 可重复设置，但**不更新 previousState**（:274-275）。

文件头注释（:24-30）钉死关键语义：**exitCode≠0 不等于 FAILED**——exitCode 是 shell 退出码，只有 errCode（框架内部错误）非零才是 app 视角失败。结果双对象分职：`resultConfig` 管"怎么回传"（:228）、`resultData` 管"回传什么"（stdout/stderr/exitCode，ResultData.java:19-23）。`shouldNotProcessResults()`（:324-331）是 test-and-set 幂等闸：首调置位（:236）返回 false，再调 true——多个结果出口共用防重复回调。

**TermuxSession 侧**：四个 final 字段（:34-37），构造私有（:41-47），唯一入口是静态工厂 `execute()`（:77-165；启动可能失败，构造函数无法返回 null）。五步：① **shell 探测**（:93-119）：executable 为空时按 `LOGIN_SHELL_BINARIES={login,bash,zsh,fish,sh}`（UnixShellEnvironment.java:56）在 $PREFIX/bin 逐个试 canExecute()，全 miss 兜底 `/system/bin/sh` 且不作登录 shell（:107-113，invalid ~/.profile 会炸启动）；② **argv 改写**（:122-131）：`arguments[0]` 换成 `-bash` 式进程名（登录 shell 加 `-` 前缀 :125）；③ **环境组装**（:137-143）：additionalEnvironment 强制覆盖（:139-140）；④ **状态闸**（:145-149）：setState(EXECUTING) 失败则 setStateFailed+处理结果+返回 null；⑤ **fork PTY**（:156-158）：`new TerminalSession(...)`。生命周期：`finish()`（:176-202，回填 exitCode :193、可选抓 transcript 为 stdout :195-196、setState(EXECUTED) :198）；`killIfExecuting()`（:212-234，setStateFailed+**硬编码 exitCode=137**（:222）再发信号 :233）；`processTermuxSessionResult()`（:252-273，幂等闸+回调 `onTermuxSessionExited` :266，无宿主时代设 SUCCESS :270-271）。

> 源内勘误：`killIfExecuting` 的 Javadoc 写"发送 SIGILL"（:205），但 :219/:233 与实现均为 **SIGKILL**（`finishIfRunning()` 里是 `Os.kill(mShellPid, OsConstants.SIGKILL)`，TerminalSession.java:234-237）。以代码为准。

## 外部连接

图谱实证：**ExecutionCommand fan-in=18 / fan-out=25**，上游横跨 L05（AppShell/IShellEnvironment）、L06（TermuxShellCommandShellEnvironment）、L08/L09（TermuxService/RunCommandService/TermuxPluginUtils）与 AmSocketServer；**TermuxSession fan-in=5 / fan-out=18**，入边仅五文件：TermuxService/TermuxShellManager/TermuxSessionsListViewController/两个 TerminalSessionClient 回调实现。ExecutionCommand 对 terminal-emulator 仅一条 Javadoc 引用（:17）：**依赖方向 app→shared→emulator 单向**。

## 数据流

以插件 Intent 开前台会话为例：Intent extras 填入新建 ExecutionCommand（TermuxService.java:395-414）→ Runner 分派 `executeTermuxSessionCommand()`（:417-419）→ shellName 缺省取 basename（:537-538）、按 ShellCreateMode（ExecutionCommand.java:108-141）复用或新建（:543-552）→ `createTermuxSession()`（:575，synchronized）调 `TermuxSession.execute(...)`（:594）→ `JNI.createSubprocess` fork 出 PTY 子进程（TerminalSession.java:127-129；pid 经 setTerminalShellPid 回填 `executionCommand.mPid`，TermuxTerminalSessionServiceClient.java:25-29）→ 三线程：InputReader 读 PTY（:133）、OutputWriter 写（:150）、**Waiter 线程 `JNI.waitFor` 阻塞等退出**（:166-172）。

退出链：Waiter 拿到退出码 → 主线程消息 → `onSessionFinished()`（TerminalSession.java:367）→ Activity 前台由 TermuxTerminalSessionActivityClient 接手（:139，exit 0/130 或插件 pending result 自动收 :177/:157-159）→ `removeFinishedSession`（:433）→ `TermuxService.removeTermuxSession()`（:629）→ **`TermuxSession.finish()`**（:176）→ `onTermuxSessionExited` 回调 TermuxService（:640）：插件结果经 pendingIntent 回传（:647-648）、会话摘出列表（:650）、刷新通知（:659）。

## 设计决策

**状态机为何这么"土"**：Waiter/UI/onDestroy killAll（TermuxService.java:228-280）三方并发改状态，int 单向闸+幂等闸就是全部并发控制。

**exitCode/errCode 双轨制**是插件协议根基：exitCode=1 表示"命令失败"，errCode≠0 表示"框架出问题"。**setStdoutOnExit 默认关**（:68-74 文档）：PTY 混流有开销，要干净 stdout 走 AppShell。

**TermuxSession 放 termux-shared 而非 app**：Termux:API/Float/Tasker 等插件 app 都依赖 termux-shared，执行框架天然复用。

**与 TermuxService 分工**：TermuxSession 管"一个会话"，TermuxService 管"一群会话"（三列表：前台 mTermuxSessions/后台 mTermuxTasks/插件待执行，TermuxShellManager.java:31/:36/:41；通知栏；前后台 swap 回调 :763-764）。TermuxSession 不持 Service 引用，只上抛 `onTermuxSessionExited`（:285-294）——依赖倒置。

## 新人提示

1. **setState 返回 false 不能装看不见**。execute() 的 :145-149 是标准姿势：检查、setStateFailed、处理结果、返回 null；跳过检查会静默卡死状态机。
2. **killIfExecuting 的 137 是伪造值**（:222）：进程被 SIGKILL 后来不及回报，框架替写 128+9；且 `hasExecuted()` 为真的会话被跳过（:214-217），击杀已退出会话不会再触发结果处理。
3. **transcript ≠ stdout**（:195-196）：resultData.stdout 混着 stderr、PS1 甚至转义序列，机器解析必翻车——要干净输出改用 APP_SHELL runner。另 mTermuxSessions 被 Activity 观察，改动须 UI 线程（TermuxShellManager.java:28-31）。
