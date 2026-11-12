# 12 · 测试矩阵：vitest 项目分道、conformance 夹具与信任门

## 角色定位

REA 的测试体系是一张**行为深度 × 运行边界**矩阵：`docs/testing.md:61` 的 Behavioral depths 表定义七档深度，`vitest.config.ts:17` 的 11 个 project 把每档映射到独立 lane（pool/并发/隔离策略各异）。最大块是 `tests/boundary/`——实测 315 个 .ts 文件（309 个 .test.ts），再拆三 lane：普通 boundary、`mcp-boundary`、串行 `process-boundary`。真实引擎主张（真 Ghidra/Hopper/IDA/浏览器）不属 vitest，归 `npm run verify:*` lanes（`docs/testing.md:294`）。

## 内部结构

分道逻辑：`MAX_TEST_WORKERS` 用 `availableParallelism` 封顶 2（`vitest.config.ts:15`）；domain/services 用 threads+`isolate:false`（纯模块无进程全局态，`vitest.config.ts:25`）；adapters/boundary/acceptance 用 forks（`vitest.config.ts:42`）；`process-boundary` 额外 `fileParallelism:false`——进程树观测共享宿主采样资源必须串行（`vitest.config.ts:64`）；`mcp-boundary` 复用不可变 server 图（`vitest.config.ts:72`）。全局挂自定义 runner 在 worker teardown 释放 native inspector（`vitest.config.ts:137`），超时 30s/coverage 60s（`vitest.config.ts:141`）。coverage 分层阈值：全仓 65/60/60/68、domain 80/75/75/80、contracts 85/80/80/85（`vitest.config.ts:150`），shard 模式归零防假报。

信任门在 domain 层：`evaluateTrustGate` 依 contract 维度逐个 `compareDimension`，产出 pass/fail/unknown 裁决（`src/domain/conformanceTrustGate.ts:315`、verdict 汇聚 `conformanceTrustGate.ts:355`）；语义比较把 unknown/truncated 排除出等价，分歧必须挂到观测到的 evidence_id 而非编造（`tests/conformance/providers/conformanceTrustGate.test.ts:36`，发明 ID 过不了 schema 断言 `conformanceTrustGate.test.ts:20`）。

## 外部连接

夹具工厂是供给侧：`tests/fixtures/binarySession.ts:36` 的 `createTestBinarySession` 单 provider 注入聚焦会话；`createCacheProvider` 让能力效果可观测（`binarySession.ts:59`）；`ControllableAnalysisClient` 用 pending promise 观察生命周期交错（`binarySession.ts:92`）。`tests/fixtures/fakeCdpBrowser.ts:16` 在真实 HTTP+WS 上复刻 CDP 端点并带故障注入（65KB oversized 发现响应 `fakeCdpBrowser.ts:46`、未建模命令返回 -32601 `fakeCdpBrowser.ts:187`）。CI 四分片跑 vitest（`ci.yml:93`），macOS lane 跑 verify:keyed-archive 等（`ci.yml:321`），`real-hopper.yml` 在自托管 Hopper runner 上以 npm pack 产物跑 `verify:hopper`（`real-hopper.yml:35`）。

## 数据流

测试归位流程：问"跨了哪条生产边界？"——纯模块→src 同址；注入端口→composition；真实文件系统/进程/浏览器之一→boundary；MCP SDK 传输→mcp-boundary；进程表→process-boundary；编译产物全链路→acceptance；多 provider 同契约参数化→conformance。真值主张流入 verify lanes：`verify:hopper` 经生产 stdio MCP+CLI 校验 CFG 边、引用、批注原子性、schema 对账（`docs/testing.md:157`）；`scripts/verify-real-ghidra-assertions.mjs` 提供 18 个共享断言。

## 设计决策

矩阵理由是**成本与所有权可见**：lane 名即声明允许的依赖与运行代价（docs/testing.md:29）。关键规则：Result 成功断言前先 throw error，否则隐藏类型化失败；协议夹具必须建模所支持命令、拒绝未建模命令；采集权限不可用用命名 skip 而非无断言 return；删回归前先指认替代场景。信任门三值设计（unknown≠fail）防"证据不足被当作分歧"。

## 新人提示

新测试先查深度表再选路径。boundary 只许跨**一条**边界；进程相关去 process-boundary 排队。conformance 声明能力需参数化并显式 opt-out。verify 脚本自带 `npm run build:cached`（package.json:140 起）。删"通过性 happy path"不能替代畸形输入/取消/清理覆盖；测量慢文件再优化（docs/testing.md:57）。
