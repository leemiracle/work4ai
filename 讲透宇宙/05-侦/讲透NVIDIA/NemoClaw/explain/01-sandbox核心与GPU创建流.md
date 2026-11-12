# 01 · sandbox 核心与 GPU 创建流

对象：`src/lib/onboard/sandbox-gpu-create-run-attempt.ts`（1178 行）、`src/lib/sandbox/create-stream.ts`（549 行）、`src/lib/onboard/docker-gpu-sandbox-create.ts`（739 行）。

## 角色定位

三件套是沙箱创建链路的执行核：`create-stream.ts` 为子进程层，把 `openshell sandbox create` 当可观测输出流跑（阶段识别、Ready 门、心跳、宿主退出联动）；`docker-gpu-sandbox-create.ts` 为事务层，把"重建 Docker 容器以附加 GPU/ulimits"封装成可回滚可提交的 patch 对象；`sandbox-gpu-create-run-attempt.ts` 为编排层（图谱"sandbox 核心域与 GPU 创建流"层代表节点），把两者组装成带身份治理的创建尝试，供 onboard、rebuild、snapshot 恢复共用。

## 内部结构

run-attempt 骨架是 `createSandboxGpuCreateAttemptRunner`（run-attempt.ts:410）返回的 `{state, runAttempt}` 闭包。身份体系贯穿全文件：`resolveCreateAttemptNonce`（:216）生成 nonce，恢复续跑时强校验持久权威、缺证据拒绝续跑（:239）；`probeExactOpenShellSandboxId`（:148）返回 `identified/not_ready/failed` 三态，用 `OPENSHELL_SANDBOX_NOT_READY` 正则（:83）区分"未就绪"与"真失败"。就绪四级递进：`waitForCreatedOpenShellSandboxPublication`（:246）轮询到持久 ID 可见且不变；`settleCreatedIdentity`（:608）要求 Ready 交接前后 ID 一致（:618）；`checkSandboxExecutableReadiness`（:319）在沙箱内跑 `["true"]`；`waitForCreatedSandboxReadyWithTrace`（:1001）带 `REPLACEMENT_STABLE_READY_POLLS=2`（:78）防读到陈旧 Ready 行。中断恢复 `restartInterruptedFinalHandoff`/`acknowledgeInterruptedFinalHandoff`（:352/:378）双段完成，均须先证明替换容器是唯一 Docker 运行时。create-stream 双 overload：argv 直 spawn 为可信路径，字符串命令走 `bash -lc` 已 `@deprecated`（create-stream.ts:82，#6258）；阶段机 `setPhase`（:269）覆盖 pull/build/upload/create/ready；`onPoll` 无 `failureCheck` 直接抛错（:112）。patch 工厂 `createDockerGpuSandboxCreatePatch`（docker-gpu-sandbox-create.ts:242）维护 `result/patchError/cutoverFinalization` 事务位（:246-254），commit 与 rollback 互斥竞态即抛错（:320/:546）；`recoverInstalledReplacementSupervisor`（:102）是唯一有界恢复，须 Docker 证据三连验证（Running+同名+日志含 supervisor success :93）。

## 外部连接

上游 `sandbox-gpu-create-flow.ts` 是调用方（图谱 imports_rev），onboard 编排与 rebuild-recreate 阶段都经它进入。侧翼：`openshell-docker-sandbox-containers`（容器 ID 查询）、`sandbox-identity`（nonce 模式 ID 解析）、`created-sandbox-failure`（恢复证据持久化）。下游：`docker-gpu-patch.ts` 门面提供 recreate/finalizeBackup（docker-gpu-sandbox-create.ts:14-17）、`docker-gpu-pre-rollback-diagnostics` 回滚前取证（:27）、`docker-gpu-local-inference` GPU 验证（run-attempt.ts:1101）。create-stream 另有 24 个连接节点，输出脱敏统一走 `security/redact`（create-stream.ts:6）。

## 数据流

主链：createRequest 加 nonce label（run-attempt.ts:551）→ `streamCreate` 组装 readyCheck/onPoll/failureCheck（:732）→ create-stream spawn 子进程（detached 进程组 :118-124）→ 行流喂阶段机与 trace → Ready 且输出模式匹配后 SIGTERM（create-stream.ts:444），`waitForReadyTermination` 模式等子进程退出、5 秒超时改 SIGKILL 置 `readyTerminationTimedOut`（:447-452）→ run-attempt 收到该标志先持久化恢复证据再抛错（run-attempt.ts:811-824）→ 身份 settle+publication → `runtimePatch.ensureApplied`（:995）→ supervisor 重连（docker-gpu-sandbox-create.ts:445）→ readiness trace → GPU proof（run-attempt.ts:1093）→ `commitAfterReady` 删备份容器（docker-gpu-sandbox-create.ts:525）。失败分支：native 被拒且基线干净返回 `fallbackEligible`（run-attempt.ts:902-917）；patch 失败先取证再 rollback（#7996，docker-gpu-sandbox-create.ts:489-498）；结果模糊走 `settleAmbiguousCreateResult`（:623）强制终局判定。

## 设计决策

①**可变名陷阱**：OpenShell 只能按可变名删沙箱，恢复提示强调"do not delete by mutable name"（:1081-1084），治理手段是 nonce+ID 指纹持久化为 retained recovery 证据，持久化失败即错误（:513-519，fail-closed）。②**Ready 门双条件**：readyCheck 为真还需一行输出匹配 `readyCheckOutputPatterns`（create-stream.ts:429-438）防假 Ready 提前脱管。③**宿主退出联动**：进程组 detached + exit/SIGINT/SIGTERM 三监听（:358-379）。④**降级须显式授权**：compatibility 交换放松隔离，仅 `NEMOCLAW_DOCKER_GPU_PATCH=fallback` 放行（run-attempt.ts:474-476）；沙箱自报 GPU 输出无宿主证据佐证时拒绝降级重试（:1141-1146）。⑤**回滚不可逆点**：`backupRemoved` 后自动回滚失效，直说"Rebuild the sandbox"（docker-gpu-sandbox-create.ts:618-620）。⑥**proof 前置相态检查**：Error 相时跳过 proof，防 exec 错误伪装成 nvidia-smi 失败（#4316，:664-698）。

## 新人提示

阅读顺序 create-stream → docker-gpu-sandbox-create → run-attempt，复杂度递增。三份文件都重度依赖注入（`overrides` 测试缝 docker-gpu-sandbox-create.ts:184-192），单测不碰真实 Docker。改动前先查 issue 锚：#6258（legacy 退役）、#4316、#4231、#7996、#5512（Docker Desktop WSL 跳过 CDI 模式 :171-176）。portable 生命周期与 compatibility 路由互斥（run-attempt.ts:425-434）；`managedImage` 走 `externalRecreation` 分支保留 OpenShell 原生运行时（:572-591 注释块解释三条路由差异）。
