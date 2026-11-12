<!-- source: knowledge-graph tour step | files: src/process/ProcessOwnership.ts, src/process/ProviderProcess.ts, src/process/PrivateRuntimeRoot.ts -->

# 07 · 受管进程沙箱：owned process 三件套如何驯服外部引擎

### 1. 角色定位

逆向引擎（Ghidra、IDA、Hopper、kuna、LLDB）全是**长生命周期外部进程**：spawn 后自行 fork、开 socket、写临时目录。`src/process/` 是所有进程外 provider 共用的安全底座，分三块：**归属证明**（ProcessOwnership.ts，1118 行）、**生成与监督**（ProviderProcess.ts，830 行）、**私有文件边界**（PrivateRuntimeRoot.ts，93 行）。存在理由一句话：**发 SIGKILL 前先证明进程是自己的**——否则 PID 复用会误杀无辜进程。v6.5 把这层纪律升格为架构原则：AGENTS.md 新增 Architecture and Cleanup 段（`AGENTS.md:15-19`），要求"每个解释与资源都有明确 owner"、清理失败保留所有权。

### 2. 内部结构

**ProcessOwnership.ts**：`OwnedProcessGroup`（`src/process/ProcessOwnership.ts:16`）是清理前的身份证明——runId 令牌、leaderPid、processGroupId，加可选的 expectedCommand/expectedParentPid（launcher 指纹）、captureBaseline（prelaunch 身份基线）与 sampledProcessGroupIds（`:30-33` 注释钉死：采样只增清理候选，不授权发信号）。OS 缝隙收窄为 `ProcessOwnershipHost` 接口（`:87`），POSIX 走 `ps -axo` 全表快照（`src/process/ProcessOwnershipObservation.ts:260-261`），Linux 用 `/proc/<pid>/stat` starttime 作稳定身份（`:288-302`）、环境直读 `/proc/<pid>/environ`（`:391`）。

清理入口 `cleanupOwnedProcessGroup`（`:240`）三段式：`createOwnedCleanupPlan`（`:409`）圈候选组（root∪后代∪令牌命中∪采样组，signalOrder `:543`）→逐组 revalidate 复核（`:257-276`）防 TOCTOU→发 SIGKILL（`:276`）。launcher 校验比对 pgid/parentPid/command 三项（`src/process/ProcessOwnershipIdentity.ts:8-25`）；成员生死由令牌定，`REA_PROCESS_RUN_ID !== runId` 即 `run-token-mismatch`（`:787-807`），环境读不出先复查存活（`:816-850`：只有 PID 消失才能注销 unreadable）。失败优先级 mismatch>identity-unavailable>unreadable（`:578-587`）。两类豁免：ESRCH 被容忍（`:281`）；macOS 扣留环境、与 owned 树无关的进程降级 `unverified`（`:889-906`），相关进程仍 fail-closed。清理后 `verifyNoTokenOwnedProcesses`（`:301`）全表扫令牌残留。

**ProviderProcess.ts**：`spawnOwnedProviderProcess`（`src/process/ProviderProcess.ts:206`）先 OS 预检（Linux 缺 procps ps 即抛 AnalysisCapabilityUnavailableError，`ProcessOwnershipObservation.ts:376-377`），注入 `REA_PROCESS_RUN_ID`（`:227`）后分平台：win32 走 `WindowsOwnedProcess`（Job Object，schema 强制 `killOnOwnerClose` 字面量 true，`src/windows/WindowsOwnedProcess.ts:17`）；POSIX 用 `detached: true` spawn（`:262`）使子进程成为组长。`ProviderProcessSupervisor`（`:295`）只管通用进程资源，"wire protocol remains adapter-owned"（`:289`）。三个语义：`waitForExit`/`waitForOutputClose` 分离（`:461`/`:470`，exit 不代表输出写完）；输出按 `maxDiagnosticBytes` 截留（`:173`）；`stop()` 共享同一次尝试、`incomplete` 释放以允许重试（`:511-519`），incomplete 时 `unref()` 释放事件循环引用让宿主可退场（`:521-548`）。停止链路（`#stopWithin`，`:568-625`）：not-owned→有 cleanup 则令牌验证清理并复查→TERM(250ms)→KILL(1s)→仍活即 incomplete。

**PrivateRuntimeRoot.ts**：POSIX 直接 `mkdtemp`——创建即原子地 owner-only，不再 chmod 改写+失败回滚（`src/process/PrivateRuntimeRoot.ts:70-75`）；Windows 委托 `WindowsPrivateRuntime`，DACL 随目录创建同时装好（`privateDacl` 字面量，`src/windows/WindowsPrivateRuntime.ts:17`）。能力报告给证明：POSIX 返回 `proof:"posix-mkdtemp-owner-only"`（`:27-36`），Windows 须 native authority 验证，不可用直接抛（`:58-62`）；close 共享一次尝试、失败可重试（`:82-92`）。

### 3. 外部连接

`spawnOwnedProviderProcess` 被 GhidraLauncher、LldbCallTracer（`src/native/LldbCallTracer.ts:879`）及短命令封装 `runOwnedCommand`（`src/process/OwnedCommand.ts:56`）直接调用。`PrivateRuntimeRoot` 用户面大扩张：GhidraClient（`src/ghidra/GhidraClient.ts:684`）、GhidraTransport socket 根（`src/ghidra/GhidraTransport.ts:40`）、HopperClient（`src/hopper/HopperClient.ts:409`）、kuna（`src/kuna/KunaTargetCommands.ts:231`）、adb（`src/adb/AdbProvider.ts:784`）乃至 pcap/pwntools/evm/JS worker。capture/ 复用同一令牌采样：只有 `pid === pgid` 的样本才采信为组 leader（`src/process/ProcessOwnershipProcessTree.ts:43-47`）；v6.2 起进程捕获不再转换 legacy v3，必须显式 executable identity+event_journal。向上，`AnalysisProviderCandidate` 新增 `hasPendingOwnedResources()`/`closeOwnedResources()`（`src/application/AnalysisProvider.ts:294-296`）。

### 4. 数据流

一次 Ghidra headless 分析：①GhidraClient `PrivateRuntimeRoot.create` 得私有根（`src/ghidra/GhidraClient.ts:684`）；②GhidraLauncher 写 descriptor JSON（transport/endpoint_path/token/run_id/target_sha256/profile_digest，`src/ghidra/GhidraLauncher.ts:244-259`）；③启动 JVM——POSIX 设 `expectedCommand`、Windows verbatim cmd.exe 设 null（`:362`）；④立刻持久化 ownership manifest（run_id/pid/process_group_id/ownership_kind，`:376-392`），宿主崩溃后凭它对账；⑤协议通信走 socketRoot；⑥停止时 Supervisor.stop→cleanupOwnedProcessGroup：ps 快照→launcher 三连比对→逐成员令牌核对→按 signalOrder 发 `SIGKILL`（`ProcessOwnership.ts:276`）→终审全表扫令牌（`:301`）。

### 5. 设计决策

**令牌放环境变量而非 pidfile**：环境天然遗传给全部后代，无需子进程配合即可回读；代价是 macOS 扣留 platform binary 环境，故设 unverified 降级通道。**PID 复用三重防御**：runId 令牌+launcher 指纹+Linux starttime 基线——`processOwnershipFailures` 在令牌核对**前后各做一次**身份核对，专防扫描窗口内的 PID 复用（`ProcessOwnership.ts:724-780`）。**fail-closed 而非 best-effort**：身份存疑宁可报 `incomplete` 也不发信号；Windows taskkill 被注释钉死为"有界 P0 清理，不是 Job Object 归属证明"（`:180-182`），真归属走 killOnOwnerClose。**平台不对称的诚实**：Windows 未经 native authority 验证前保持 unavailable，POSIX 给可自查的 owner-only 证明。**清理失败保留所有权**（v6.5 主题）：AnalysisError 新增 `cleanupIncomplete`/`cleanupResources`（`src/domain/analysisErrorBase.ts:68-69`、`:81-82`），`analysisErrorWithCleanupFailure` 合并主失败与未完成清理（`src/domain/analysisErrorCleanup.ts:6-9`）；一次性分析可报 `cleanup_incomplete` 而非静默成功（docs/migration-6.2.md）；近期 fix 提交链（1bd5c5c87/3ed925e54/ca7ee018b 等）全是这一原则的落地。

### 6. 新人提示

上手顺序：PrivateRuntimeRoot→ProviderProcess→最后啃 ProcessOwnership 的计划/复核双段。易错点：detached 子进程不随宿主退场，忘调 `stop()` 即泄漏，ownership manifest 是恢复凭据；清理返回 `incomplete` 不是终态——所有权仍被持有，原对象重试即可，别另起进程去清；`captureStdout` 在 stdout 承载解析协议时必须显式关掉（`src/process/ProviderProcess.ts:171`）；Linux 容器别裁 procps。测试入口：identity/validation/runId 等 8 个 test 加 fixture 共 2600+ 行，与源码同目录可无 OS 依赖跑全分支。接新引擎首选 `runOwnedCommand`（短命令）或 `spawnOwnedProviderProcess`+Supervisor（长会话），不要自己 spawn。
