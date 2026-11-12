# src/contracts/：MCP 工具契约总账

## 角色定位

src/contracts/ 是全部公开 MCP 工具的**单一事实源**：每个工具的名字、输入/输出 schema、副作用审计、annotations、示例都以声明式数据固化于此，server 层注册时只做投影、不自行定义。中枢 `TOOL_CONTRACTS` 注释自称 "Complete ordered public inventory used by registration and verification"（src/contracts/toolContracts.ts:23-24）。图谱中该文件 fan-in=76（全仓引用密度最高之一）、fan-out=36（展开 19 个分组），文档目录生成、契约快照测试、审计缺漏检查全从它派生。

## 内部结构

- **聚合总账**：`TOOL_CONTRACTS` 按固定顺序展开 19 组常量，从 OFFICIAL（桥接直代理）、ENHANCED 到 SESSION（src/contracts/toolContracts.ts:24-44）。
- **类型化检索**：`toolContract<Name>()` 用 `Extract` 在类型级保留精确 schema 类型，找不到抛 `Missing tool contract`（src/contracts/toolContracts.ts:47-62）。
- **契约形状**：`ToolContract` 八字段——name/title/description/kind/inputSchema/outputSchema/effects/annotations/examples（src/contracts/toolContractTypes.ts:40-58）；`TOOL_KINDS` 枚举 12 个适配器家族（src/contracts/toolContractTypes.ts:21-34）。
- **效果审计**：`ToolEffects` 用 8 个布尔位描述全部副作用（src/contracts/toolEffects.ts:2-12）；`TOOL_EFFECTS` 对 **138 个工具**逐一登记（src/contracts/toolEffects.ts:43-322）；`annotationsFromEffects` 纯函数推导 MCP hints，无名称启发式（src/contracts/toolEffects.ts:324-340）。
- **共享输出 schema**：toolOutputSchemas.ts 仅 re-export primitives+groups（src/contracts/toolOutputSchemas.ts:1-2），配 `requireOutputSchema` 强制登记输出（src/contracts/officialToolContracts.ts:5-9）。

## 外部连接

四路消费：① server 注册器——`registerOfficialTools` 遍历 `OFFICIAL_TOOL_CONTRACTS` 逐个 `server.registerTool`（src/server/registerOfficialTools.ts:44-54），专用工具按名取用（src/server/registerWebModuleTool.ts:17），`toolRegistrationOptions` 投影成 SDK 注册参数（src/server/toolRegistrationOptions.ts:13-23）。② 基建——scripts/generate-mcp-tool-catalog.mjs:8 从 dist 导入总账生成目录，contractSnapshot.test.ts 对账分组并集与效果审计。③ application 层复用输入 schema 预校验（src/application/FunctionAnalysisEvidence.ts:21）。④ helpers 提供 `document`/`address` 等共享原语（src/contracts/toolContractHelpers.ts:9-36）。

## 数据流

定义侧：分组文件用局部工厂组契约，如 `official(name, desc, schema)` 先 `inputSchema.strict()`，再取 `toolContractMetadata(name)` 注入审计过的 title/effects/annotations，最后挂 outputSchema 与示例（src/contracts/officialToolContracts.ts:20-33）。消费侧：各 register 把契约展平进 SDK，运行时由 `contract.inputSchema` 解析参数（src/server/registerOfficialTools.ts:67-68）；效果字段另驱动可用性策略与文档——声明一次，三处受益。

## 设计决策

- **effects 先于 annotations**：readOnly/destructive 等 hint 从 8 位效果矩阵推导而非手填（src/contracts/toolEffects.ts:325-340），杜绝"标 read-only 实际写文件"；缺审计直接抛错（src/contracts/toolEffects.ts:343-346）。
- **`as const` + Extract 检索**：总账保持字面量元组类型，按名取契约可自动补全且返回精确 schema 类型，拼错名是编译错。
- **strict schema**：official 工厂统一 `.strict()`（src/contracts/officialToolContracts.ts:24），未知字段直接拒绝，防客户端幻觉参数混入。
- **描述即防幻觉文案**：description 写满能力边界（如 annotate_native_function 明示 Windows P0 不支持，src/contracts/officialToolContracts.ts:38-44），原样进入 LLM 工具清单。

## 新人提示

新增工具顺序：分组文件写契约 → TOOL_EFFECTS 登记效果（src/contracts/toolEffects.ts:43）→ register 模块挂行为。输出 schema 同形时复用 toolOutputSchemaGroups——HEAD 提交 441813c0 "perf(mcp): share repeated output schema definitions" 正是消除这类重复。改工具名要全仓 grep：TOOL_CONTRACTS、TOOL_EFFECTS、各 `toolContract("...")` 字面量、catalog 生成物四处联动。contracts 里不要 import server/application 实现模块。
