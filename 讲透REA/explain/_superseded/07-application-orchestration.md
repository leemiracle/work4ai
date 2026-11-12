# 07 · 应用编排层：AnalysisProvider、BinarySession 与 DirectAnalysis

## 角色定位

`src/application/` 是 REA 的应用层：不感知 Hopper/Ghidra/IDA 细节，只定义"provider 必须长什么样"与"会话如何持有目标"。契约中枢 `AnalysisProvider.ts` 图谱 fan-in 161，grep 实测 80+ 文件直接 import。三件套分工：`AnalysisProvider.ts` 定义类型契约；`binary/BinarySession.ts:63` 是 CLI 与 MCP 共享的有状态会话门面；`DirectAnalysis.ts:78` 是 CLI 一次性命令引擎。

## 内部结构

`AnalysisOperation` 是封闭联合：五组工具名加 `"health"`（`AnalysisProvider.ts:25`）。成功调用产出 `AnalysisExecution`——result/rawResult/provider 身份/limitations/locations（`AnalysisProvider.ts:34`），由 `createAnalysisExecution` 在适配器边界 `jsonValueSchema.parse` 强制校验（`AnalysisProvider.ts:45`）。provider 契约分两级：`AnalysisProvider`（identity/capabilities/createClient，`AnalysisProvider.ts:174`）与可深度探测的 `AnalysisProviderCandidate`（加 inspectAvailability/inspectTargetSupport，`AnalysisProvider.ts:224`）；`CapabilityDescriptor.cachePolicy` 区分 snapshot/live（`AnalysisProvider.ts:164`），live 能力禁快照重放。`BinarySession` 持唯一 `#active`（target+client+profile+route+runId）：`#open` 先 `#drainCalls` 排空在途调用，关旧 client、新建后立即执行 `"health"` 探活，失败则 `#restore` 重建旧目标（`BinarySession.ts:224`、`BinarySession.ts:265`）；`execute` 可并发，但目标迁移期间新调用被挡（`BinarySession.ts:400`）。

## 外部连接

依赖全指向内层：contracts 工具名、domain 的 Result/Evidence/错误类、process 的 `ProcessLineageObservation`（`AnalysisProvider.ts:16`）。被 `composition/binary.ts`（真实 provider 注册表）、`DirectAnalysis.ts`、`server/createServer.ts`（MCP 工具族）消费；`EnhancedTools` 与 `FunctionAnalysisEvidence` 是其分诊下游（`DirectAnalysis.ts:344`）。

## 数据流

CLI 路径：`runDirectAnalysis` 把 SIGINT 包成 AbortSignal（`DirectAnalysis.ts:384`）→`runAnalysis`（`DirectAnalysis.ts:168`）parseConfig→`prepareSnapshot`（快照与目标 sha 不符抛 `EvidenceIntegrityError`，`DirectAnalysis.ts:422`）→有快照先 `previewTarget` 尝试缓存命中（`DirectAnalysis.ts:229`）→否则 open→`executeAnalysisTool` 分诊→`recordEvidence`+快照落盘（`DirectAnalysis.ts:267`），finally 必关 session。session 内 `#execute` 查会话快照（四个 artifact 操作显式排除，`BinarySession.ts:429`），成功后 `createEvidence`+`recordSnapshot`（`BinarySession.ts:457`）；能力声明 `mutatesArtifact` 则反向 `invalidateSnapshot`（`BinarySession.ts:479`）。

## 设计决策

三个防御：①目标迁移用 `#serialize` promise 链串行化（`BinarySession.ts:558`），按代数过滤 drain 防后到 open 把先到调用算进自己的排空集；②health 失败不丢旧目标，`#restore` 重建而非保留已关闭 client（`BinarySession.ts:582`）；③`#observeRuntimeAvailability` 把 CapabilityUnavailable/Hopper 进程错误转成 per-operation 不可用状态并通知监听器，让 MCP discovery 实时降级（`BinarySession.ts:485`）。错误统一 `projectAnalysisError` 投影为 JSON（`DirectAnalysis.ts:518`）。

## 新人提示

新增工具名必须五组契约同步改 `AnalysisOperation`；快照重放黑白名单散在 `BinarySession.ts:429` 与 `DirectAnalysis.ts:441` 两处，漏改一边会 CLI/MCP 行为分叉。`structuredClone` 防外部可变引用，别删。测试用 `tests/fixtures/binarySession.ts` 的 `createTestBinarySession` 注入单 provider，勿手工拼 router。
