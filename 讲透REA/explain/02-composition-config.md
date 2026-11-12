<!-- source: knowledge-graph tour step | files: src/composition/binary.ts, src/config/parseConfig.ts, src/composition/directAnalysis.ts -->

# REA 精讲 02：组合根与配置解析

### 1. 角色定位

REA 是"application 层定义接口、composition 层给生产实现"的 DI 布局。本篇三块处在装配层：配置解析入口 `src/config/` 目录（v6.1 的 `src/config.ts` barrel 已删除）、全仓唯一生产装配点 `src/composition/binary.ts`（59 行）、把工厂绑定成 CLI 直调函数的 `src/composition/directAnalysis.ts`。

为什么需要组合根？REA 有两个互斥宿主：长驻 MCP server（进程持有一个 session，src/main.ts:38-40）与一次性 CLI 命令（每次开-用-关一个隔离 session，"intentionally isolated"，src/application/DirectAnalysis.ts:89-93）。若各自拼装 provider 语义必漂移，故 `src/composition/binary.ts:15-19` 钉版 "the sole production wiring point"。v6.5 组合根扩成"一族薄装配文件"：每个新分析域各有 6-59 行 `src/composition/<area>.ts`（captures/wasm/sqlite/adb/pcap/jeb/reverseEngineering 等），被 createServer 与 CLI 注册器消费；深度 provider 装配仍唯 binary.ts 一处。

### 2. 内部结构

**config 目录与解析管线。** 入口 `parseConfig`（src/config/parseConfig.ts:43-103）返回 `Result<AppConfig, ConfigurationError>`，`AppConfig` 在 src/config/types.ts:8-28；无 barrel，消费者直接 import（src/main.ts:10）。三级解析：① zod `environmentSchema`（src/config/environment.ts:23-79）——`REA_ANALYSIS_PROVIDER` 默认 "auto"（:24），新增 `REA_MCP_INPUT_SCHEMA_PROFILE`/`REA_MCP_OUTPUT_SCHEMA_PROFILE`（:26-27），路径类变量一律 `min(1)`+`isAbsolute` refine（:28-70），失败包 `ConfigurationError` 走 Result 不 throw（:114-127），另有跨字段校验：Ghidra compiler spec 必须伴随 language id（:156-171）；JEB 超时排除在 AppConfig 外、自成 `parseJebMcpTimeoutMs`（parseConfig.ts:46-50）。② JSON 解析器（src/config/parsers.ts:9-27，`parseLoaderArgs` undefined 时 `ok([])`）。③ 装配（parseConfig.ts:54-102）失败短路、可选字段条件展开；`defaultHopperLauncherPath`（:25-40）三参可注入，解析时同步探测文件系统。

**binary.ts 三个工厂。** `createBinarySession(config, logger, selectedEnvironment)`（src/composition/binary.ts:20-39）：四个深度 provider——Hopper/Ghidra（收 config+logger+environment，:26-27）、`IdaProvider(config, environment)`（:28）与 **`KunaProvider(environment)`**（:29，v6.5 唯一新增深度 provider，BYO 反编译器可执行文件）→ `AnalysisProviderRegistry([hopper, ghidra, ida, kuna], ...)`（:31-34）→ 辅助 provider 声明表逐个包 `LazyAnalysisProvider`（:35-37）→ `composeBinarySession`（src/application/binary/BinarySessionComposition.ts:11-18，`SessionProviderRouter.selectable`）。`createManagedBinarySession()`（binary.ts:42-45）免执行变体：空 registry + 仅 `ManagedStaticProvider`；新 `createArtifactBinarySession()`（:48-59）异步 import `ArtifactProvider`、空候选 registry。

**directAnalysis.ts 的工厂闭包。** `createDirectAnalysis(selectedEnvironment)`（src/composition/directAnalysis.ts:17-62）先 `snapshotEnvironment` 捕获一次环境，再组 `DirectAnalysisDependencies`（src/application/DirectAnalysisDependencies.ts:7-21：`readConfiguration`+三个 session 工厂），全部 `await import("./binary.js")` 惰性求值（:22-34）；`BoundOperation` 剥掉首参（:9-14），导出三个直调入口（:36-61），application 模块推迟到首调才加载；`runManagedProviderExecution`（:68-82）独立绑定，被 `src/server/registerManagedTools.ts:12` 消费。

### 3. 外部连接

MCP 侧：`src/main.ts:11` 导入 `createBinarySession`、:45 用 `parseConfig`；可选观测 provider 走 `createOptionalObservationFactories`（src/composition/optionalObservationProviders.ts:24-50 五端口全动态 import；load :67-108 并行保留健康同伴）。CLI 侧：`src/cli.ts:5,78` 一次 `createDirectAnalysis`，:102/:111-112 把入口分交 coreAnalysis/artifact/managed 注册器，状态查询在 `src/cli/utilityCommands.ts:157`。server 侧 createServer 消费各 `composition/<area>.ts` 工厂。依赖方向铁律：composition import application，application 永不反向。

### 4. 数据流

以 `rea analyze /tmp/sample` 为例：① `withProcessCancellation` 把 SIGINT/SIGTERM 转 AbortController（src/application/DirectAnalysis.ts:497-514）。② `runAnalysis`（:212）`readConfiguration`（:237-238）→ `createBinarySession`（:239）→ `withSessionCleanup`（:241）。③ `prepareSnapshot` 校验快照与目标匹配（:244，定义 :516-554）。④ `session.open`（:322-325）触发 select：`auto` 并行评估候选（src/application/binary/AnalysisProviderRegistry.ts:303-331），多于一个可用报 `ambiguous`（:358），恰好一个则 `auto-single-candidate`（:363）。⑤ `executeAnalysisTool`（:328，定义 :393-495）三路由：`analyze_function` 专项（:406）；workflow 族走 `EnhancedTools`+`createWorkflowEvidence`（:419-441）；其余 `session.execute`+`createEvidence`（:442-494）。⑥ `recordEvidence`（:337）+ 快照导出（:365-386）。⑦ 清理失败不再静默，可报 `cleanup_incomplete`（src/application/DirectAnalysisCleanup.ts；docs/migration-6.2.md:118-125）。

### 5. 设计决策

**registry 构造器为何凶？** `src/application/binary/AnalysisProviderRegistry.ts:81-133` 构造期即 throw：ID 非法（:92）、重复（:94）、capability provenance 与 identity 不匹配（:102）、同一操作声明两次（:106）——不变量前推到最早判定点。构造器按码点排序（:115-118），:79-80 钉版 "Registration order never affects selection"，两个 adapter 候选列表逐字节一致。v6.5 新增清理归属协议：provider 可声明 `hasPendingOwnedResources`/`closeOwnedResources`（:140-152），auto 选择先查 cleanupIncomplete（:334-338）。

**辅助 provider 为何懒加载？** `src/application/binary/LazyAnalysisProvider.ts:24-28` 注释说破：保住同步发现，实现模块推迟到 target-bound client 首次执行才 import。

**为何用动态 import 而非 bind？** 641 行 DirectAnalysis 及其依赖不随 CLI 启动加载；接口注入保留——`tests/composition/directAnalysisFactories.test.ts` 注入假 session 数 close 次数验证释放，生产绑定只在 composition 一处。

**parseConfig 为何返回 Result？** MCP 与 CLI 各自决定错误呈现。**environment 为何快照？** caller-selected 让测试不改 `process.env` 驱动全部分支。

### 6. 新人提示

- 上手顺序：`src/config/environment.ts`（配置面唯一真相）→ `src/composition/binary.ts`（59 行）→ `AnalysisProviderRegistry.ts`。
- 易错一：路径类环境变量必须绝对路径，zod refine 拒绝且报错带变量名（src/config/environment.ts:28-70）。
- 易错二：`auto` 多 provider 同时可用时报 `ambiguous` 而非"挑最好的"（AnalysisProviderRegistry.ts:358），显式设 `REA_ANALYSIS_PROVIDER` 才是正解。
- 易错三：四个深度 provider 构造签名各不相同——Kuna 只收 environment、Ida 收 config+environment、Hopper/Ghidra 收 config+logger+environment（binary.ts:26-29），改构造器逐一核对。- 测试入口：`src/config.test.ts`；`tests/composition/directAnalysisFactories.test.ts`；`tests/composition/analysis-sessions/binarySession.test.ts`。
