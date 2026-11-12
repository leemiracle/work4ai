<!-- source: knowledge-graph tour step | files: tests/fixtures/binarySession.ts, scripts/verify-real-ghidra-assertions.mjs, scripts/lib/verifier-run.mjs, tests/fixtures/fakeCdpBrowser.ts, scripts/lib/test-projects.mjs, docs/testing.md, .github/workflows/ci.yml -->

# REA 精讲 12：测试矩阵与真实引擎验证

### 1. 角色定位

REA 的核心价值主张——"Ghidra/IDA/kuna 真能分析出正确结果"——无法用 mock 证明。docs/testing.md:169-172 把证据钉成优先级链：真实 CLI/MCP 工作流 > 生产边界集成 > 真实产出者 golden > 模块测试，并明言路径、编译导入与套件名不构成证据深度。质量体系按"证明什么"分四层：

- **Vitest 项目矩阵**：十二类 project（清单外置 scripts/lib/test-projects.mjs:6-76，新增 cli-boundary），对应 docs/testing.md:240-251 行为深度表；tests/boundary 已长到 730 个 .ts 文件（v6.1 时 315），acceptance 102，conformance 数据驱动 15 子目录（新增 psp/）；
- **逆向工具专线**：vitest.reverse-tools.config.ts 圈定 13 个逆向工具源文件（GDB/Rizin/Cutter/objdump 等）的 36 个测试文件（forks maxWorkers 2），vitest.reverse-tools-semantics.config.ts 3 文件走 processOwnershipRunner 专测进程语义；
- **真实引擎 lane**：`npm run verify:*`（实测 99 个）绕过 Vitest 直接 import `dist/`，对已安装引擎无 mock 验证；
- **CI 信任门**：ci.yml 实测 27 个 job；workflows 目录 30 个文件，其中 real-*.yml 手动 lane 16 个——一种证据不能顶替另一种。

### 2. 内部结构

**tests/fixtures/binarySession.ts**（227 行）是会话测试工厂：`createTestBinarySession`（:117）把自备 provider/client factory 组成单 provider 聚焦会话；`createBinarySessionTargets`（:124）物化目标文件供生命周期用例；`createCacheProvider`（:135）声明只读 `address_name` 与改 artifact 的 `set_address_name` 两个 capability，`execute` 把操作名 push 进外部数组实现调用可观测；`ControllableAnalysisClient`（:167）能让 `health` 按需失败（`HopperStartError`）或挂起。

**scripts/verify-real-ghidra-assertions.mjs**（462 行）是 Ghidra 断言库。核心 `assertDossier`（:52-70）串八项子断言：procedure 溯源、native API 边界、p-code 值流、typed references、callees、strings、assembly、多块 CFG；`assertSession`（:248）钉会话承诺：provider 版本必须等于 `SUPPORTED_GHIDRA_VERSION`、capabilities 与 `GHIDRA_SESSION_CAPABILITIES` 逐一对应（import 自 `dist/`，:6-7）。四类 fixture 断言：debug（:297）、stripped（:333 断言符号确实没了）、cross（:346）、malformed（:361 必须在 provider 启动前被 `parseBinaryTarget` 拒绝）。

**scripts/lib/verifier-run.mjs**（214 行）是运行遥测：`createVerifierRun`（:8）分配 UUID 写入 `REA_PROCESS_RUN_ID`（:10/:18）并随环境传播给子进程；`completeVerifierRun`（:28）收尾观察进程谱系——直读 `/proc/<pid>/stat` 抽 ppid/pgid，其他平台回退 `ps`；`descendantMembers`（:181）不动点求后代闭包，每个后代的 environ 必须带相同 run token，不匹配则整体降级 `unavailable` 并给原因（:119）。

**tests/fixtures/fakeCdpBrowser.ts**（265 行）在真实 `node:http`+`ws` 传输上起假 Chrome：`/json/version`、`/json/list` 走真 HTTP（:147/:169），WebSocket upgrade 在 :38，故障注入覆盖命令级错误、挂起、畸形消息 `{not-json}`（:71）、`-32601` 不支持方法（:76），`replyToCommand`（:205）产出原生线格式回复。

### 3. 外部连接

binarySession.ts 的 import 全向内（`src/domain/*`+`src/application/*`），被 MCP boundary（tests/boundary/mcp/clientCapabilities.test.ts:39 用 `createTestBinarySession(createCacheProvider([]))` 建空会话）与 acceptance lane 两侧消费，印证 docs/testing.md:261-263 的 fixture 归置规则（builder 与 recording port 以 `src/**/*.fixture.ts` 与生产 owner 同居）。verifier-run.mjs 是 verify 生态最大公约数，verify-real-ghidra.mjs:45/:341 是标准用法（领 run_id → 收尾谱系进 JSON 报告）。CI 形状 v6.5 重构：ci.yml 以 `changes` 分类 job 开场（:34），产出 tier/code/sqlite/reverse_tools 等输出门控后续全部 lane——static 以 `tier != 'reused'` 才跑（:117），专设 reverse-tools-quality（:258）与 sqlite-runtime（:368）job；30 个 workflow 新增 real-cutter/real-go-binary/real-packet-capture/real-signal-recording/real-termux/real-web-network-captures 等。Stryker 突变测试全新：stryker.config.mjs（vitest-runner+related+perTest，:8/:12/:19）、stryker.semantics.config.mjs（commandRunner）、scripts/lib/reverse-tools-mutation-targets.mjs 用 TS AST 按方法/构造器声明选突变区间（:9，无手工行号），入口 test:mutation:reverse-tools。

### 4. 数据流

`npm run verify:ghidra` 的完整路径：

1. verify-real-ghidra.mjs:45 调 `createVerifierRun()`，verifier-run.mjs:10 写入 `REA_PROCESS_RUN_ID`，之后 spawn 的 JVM 与 bridge 子进程全部继承它，作收尾对账锚。
2. 前置校验：`GHIDRA_INSTALL_DIR` 绝对路径 + `inspectGhidraInstallation` 版本匹配（verify-real-ghidra.mjs:47-52），失败即点名缺失角色。
3. 宿主编译器现场编译 fixture 产出 debug/stripped/cross/malformed 四类二进制；生产 `GhidraClient` 真实启动 JVM 导入分析，CLI 与独立 stdio MCP 子进程双通道取证。
4. 断言库逐项核对；`finally` 清空 fixture 根目录后 verify-real-ghidra.mjs:341 调 `completeVerifierRun`，谱系随 `ok:true` 报告打到 stdout——"先等 owned cleanup 完成才发成功报告"是 docs/testing.md:193 的纪律。

CI 侧还有一层排序：tests/ciTestSequencer.ts（vitest.config.ts:11 注入）读历史耗时报告给测试文件排序，冷热差被显式建模。

### 5. 设计决策

**假浏览器为何跑在真传输上**：mock 掉 WebSocket 层会让生产传输解析器零覆盖，故保留真 HTTP+WS、只在语义层造假，另注入 `{not-json}` 等畸形消息打容错路径。

**断言库为何是 `.mjs` 而非测试文件**：verify lane 在 Vitest 外运行且 import `dist/`（verify-real-ghidra-assertions.mjs:6-7），断言须被多个 lane 的 Node 脚本直接 import；断言风格是"漂移检测"而非 golden 对拍，错误信息带完整 JSON。

**lineage 只做点态观察**：verifier-run.mjs 注释是罕见的诚实声明——空后代列表不证明"verifier 从未起过子进程"；Windows 直接返回 `unavailable` 并解释原因。

**突变测试锁逆向工具**：13 个源文件是进程/超时/清理语义最脆的面；mutation targets 从当前 TS 源解析具名 owner、缺失或歧义目标在生成前即停——拒绝手工行号清单腐化。docs/testing.md:318 列明突变覆盖清单：信号终止命令、Cutter descriptor identity、调试器清理所有权、GDB 退出/取消、Rizin 启动/超时 Evidence/进程退出。

**反模式禁令**（docs/testing.md:174-186）：禁止镜像实现细节的测试与笛卡尔积矩阵；协议 fixture"必须对未建模命令返回拒绝而非泛化成功"（:185-186），fakeCdpBrowser 的 `-32601` 分支即该条款落地。agent 评估 fixture 也升级：被引用 Evidence 直接参与评分，路由或措辞对了不再过关（migration-6.2.md:123-125）。

### 6. 新人提示

先读行为深度表（docs/testing.md:240-251）再写第一个测试，否则易把 boundary 测试写成隐藏依赖的模块测试。日常用 `test:local`（脏文件经 import 图选择，不构建）与 `test:focused -- 精确路径`（不存在的路径直接失败，docs/testing.md:16-19）；改 provider 必须跑对应 `verify:*` lane，CI 不替你证明引擎行为。

易错点：①`process-boundary` 强制串行（vitest.config.ts:75 fileParallelism:false），因进程树观测共享宿主采样资源；②coverage 阈值分域且 glob 特定（vitest.config.ts:151-175：全局 statements 65%/src/domain 80%/src/contracts 85%；分片 lane 用 ZERO_COVERAGE_THRESHOLDS :101-117 因为分片不拥有全局阈值）；③`GHIDRA_INSTALL_DIR` 必须绝对路径，引擎挂了先跑 `rea doctor --json`；④verifier 子进程继承 `REA_PROCESS_RUN_ID`，收尾前不清完则 lineage 断言失败；⑤windows-curated 的路径清单与 tests/process-global/curatedWindowsLane.test.ts 钉在一起（ci.yml:726-730 注释明言 Vitest 会静默忽略不匹配路径——清单改动不改测试就红）。
