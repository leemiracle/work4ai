# 11 · 受管进程沙箱：所有权令牌、监督器与私有运行时根

## 角色定位

`src/process/` 回答逆向工具特有的安全问题：REA 会拉起 Ghidra JVM、Hopper GUI、Electron 应用等长命子进程，如何保证"杀得干净且只杀自己的"？答案是把进程清理做成**需要证据的合同**：`ProcessOwnership.ts:14` 定义 `OwnedProcessGroup`（runId+leaderPid+processGroupId+身份期望），清理前每个活成员必须出示 `REA_PROCESS_RUN_ID` 令牌或身份证明。`ProviderProcess.ts` 管"生"（`spawnOwnedProviderProcess`）与"养"（`ProviderProcessSupervisor`），`PrivateRuntimeRoot.ts` 提供 0700 私有目录边界。

## 内部结构

`ProcessOwnership.ts`（1002 行）类型先行：`ProcessTableEntry`（`ProcessOwnership.ts:40`）、verified/unavailable 二态的 `ProcessLineageObservation`（`ProcessOwnership.ts:69`）、带 per-member 失败原因与 unverified 名单的 `ProcessCleanupResult`（`ProcessOwnership.ts:149`）。核心算法 `createOwnedCleanupPlan`（`ProcessOwnership.ts:341`）：收集根组+launcher 后代组+令牌扫描组+采样组→逐组验证成员令牌→只把全过的组放进 `signalOrder`（根组排最前，`ProcessOwnership.ts:474`）；发信号前还要对每组**再验证一次**防 TOCTOU（`ProcessOwnership.ts:250`）。`verifyNoTokenOwnedProcesses` 收尾审计：仍有令牌进程即 `cleaned:false`（`ProcessOwnership.ts:281`）。无法归因的进程不连坐——记为 unverified 证据而非失败（`ProcessOwnership.ts:136`）。

`spawnOwnedProviderProcess` 注入 `REA_PROCESS_RUN_ID`（`ProviderProcess.ts:151`），POSIX `detached: true` 建独立进程组（`ProviderProcess.ts:180`），Windows 走 job object 的 `WindowsOwnedProcess` 且禁止协议 stdin（`ProviderProcess.ts:153`）。`ProviderProcessSupervisor.stop` 升级：优先 token 验证清理，否则 SIGTERM→250ms→SIGKILL（`ProviderProcess.ts:371`），五态枚举精确报告（`ProviderProcess.ts:123`）。`PrivateRuntimeRoot.create` POSIX 走 mkdtemp+chmod 0700，Windows 走已验证 DACL，不可用即抛错拒绝启动（`PrivateRuntimeRoot.ts:63`）；`close` 幂等共享 promise（`PrivateRuntimeRoot.ts:90`）。

## 外部连接

`ProcessOwnershipHost` 是唯一 OS 缝隙接口（listProcesses/environment/runTokens/signalGroup，`ProcessOwnership.ts:85`）。上游消费者：GhidraClient（运行时根+监督器+谱系，`GhidraClient.ts:8`）、Hopper BridgeLauncher（ownership.json 落盘）、`PlaywrightElectronActiveProvider.ts:109`（sweepTokenOwnedProcesses）、EVM worker。下游：`BinarySession.status()` 透出 lineage/activity 快照成 MCP 可观测性（`BinarySession.ts:375`）。vitest 配专用 runner 在 worker teardown 释放 native inspector（`vitest.config.ts:137`）。

## 数据流

生成：随机 runId→spawn 注入令牌→子树任何成员可被读环境验证。观测：`observeOwnedProcessLineage` 只读不信号，verified 谱系挂上 Evidence。清理：所有权声明→读进程表→建计划（令牌+身份+基线三方核对）→按序 SIGKILL→Windows 树用 taskkill /T /F（`ProcessOwnership.ts:182`）→终审计。失败闭环：`incomplete` 时 GhidraClient 保留 supervisor 与文件供重试并告警（`GhidraClient.ts:517`）。

## 设计决策

三条红线：①**fail closed**——验证不了就不发信号，宁报 `cleaned:false` 不盲杀（PID 复用下可能命中无辜进程）；②**最小宣称**——Windows 明说 taskkill 是 bounded P0 cleanup 而非 Job Object 所有权证明（`ProcessOwnership.ts:175`），native authority 验证前能力保持 unavailable；③**观察与授权分离**——采样到的组只进候选，每个活成员仍需令牌（`ProcessOwnership.ts:27`）。串行 lane 的代价被显式接受，换取进程树测试不互相污染采样。

## 新人提示

新增 provider 进程必须经 `spawnOwnedProviderProcess` 或显式给 ownership+cleanup，手工 spawn 会漏清理。进程树测试只能放串行 lane `tests/boundary/process/`（`vitest.config.ts:64`）。macOS 坑：npm 进程改 display title 后变 token-unreadable，unverified 名单非空是预期不是 bug。`ProcessCleanupResult.reason` 字符串是钉版契约，别改措辞。
