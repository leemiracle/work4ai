<!-- source: knowledge-graph tour step | files: src/contracts/toolContracts.ts,src/contracts/toolEffects.ts,src/contracts/toolContractTypes.ts -->

# EXPLAIN 3 · MCP 工具契约总账：TOOL_CONTRACTS 如何成为全仓唯一真相

### 1. 角色定位

契约三件套构成图谱第 1 层「MCP 工具契约层」，夹在领域模型与应用编排、服务适配之间。它回答的问题只有一个：**REA 对外发布的每个 MCP 工具长什么样、有什么副作用、按什么顺序摆**。v6.1→v6.5 契约面扩张近半：19 group/138 工具变为 **36 group/207 工具**（TOOL_EFFECTS 与 TOOL_CONTRACTS 严格同集，实测各 207 项），契约族长成 17 子目录/88 个 .ts；但"契约先行"不变——名字、schema、10 维副作用、annotations 与示例在类型层钉死后，MCP 工具面、能力清单、doctor 自检、catalog 摘要与文档全部从 `TOOL_CONTRACTS` 派生，没有第二份手写清单。`toolContract()` 仍保留精确 schema（`toolContracts.ts:83` 的 `Extract` 投影）。

### 2. 内部结构

**toolContractTypes.ts**（68 行）是类型基准：`ToolContract`（`toolContractTypes.ts:45-68`）现为 10 个只读字段，新增 `returnsTargetContent`（:66，结果可能携带分析目标文本，按 untrusted 标记）；`TOOL_KINDS` 扩到 17 个 adapter 家族（`toolContractTypes.ts:21-39`）。

**toolEffects.ts**（780 行）是副作用审计表：`ToolEffects` 定义 **10 个布尔维度**（`toolEffects.ts:2-22`）——新增 `executesForeignCode`（:18，运行 REA 不拥有的代码）与 `mutatesDevice`（:20，改动挂接的 Android 设备）；`mutatesSession` 注释仍明示**加性 Evidence 记录也算 session 变更**（`toolEffects.ts:4`）。`effects()` 工厂默认全 false、唯 `idempotent: true`（:32-44），四个预设消灭重复声明（:46-52）。`TOOL_EFFECTS`（:55）为 207 个工具逐个登记，如 `record_unknown` 标 mutatesSession+idempotent:false（`toolEffects.ts:712`）。投影端 `annotationsFromEffects`（:718）把 10 维机械投影成 MCP 4 hint——readOnly 是 9 个变异维的或非（:721-731），destructive 除 mayDiscardData 外**新增两维也触发**（跑外部代码/改设备的影响无法限定为加性，:732-736）；`toolContractMetadata`（:767）查表缺失直接 throw（:770）。新成员 `TARGET_CONTENT_FREE_TOOLS`（:753）白名单豁免两个纯会话工具，`toolReturnsTargetContent`（:763）对未知名字默认 untrusted。

**toolContracts.ts**（95 行）是聚合中枢：按固定顺序 spread **36 个 group** 为 `TOOL_CONTRACTS`（`toolContracts.ts:39-76`），顺序即目录序；`toolContract(name)` 用类型守卫 find，找不到 throw（`toolContracts.ts:92`）。

### 3. 外部连接

向上依赖极薄（zod+领域 `JsonValue`+同层 toolEffects）；契约血肉在各 group 文件由工厂装配：`official()`（`officialToolContracts.ts:20-36`）做 `inputSchema.strict()` 拒未知键（:26）、`requireOutputSchema` 从 `officialOutputSchemas`（`toolOutputSchemaGroups.ts:114`）取输出、`examplesFor` 生成示例；`session()`（`sessionToolContracts.ts:38-53`）同构。消费端五路：① server 层 **36 个** `register*Tools.ts` 经 `toolRegistrationOptions`（`src/server/toolRegistrationOptions.ts:20`）直投 SDK，`toolInputSchemaWithMetadata`（`toolSchemaMetadata.ts:56`）挂属性描述与示例投影；② `buildCapabilityInventory` 产出逐工具可用性（`CapabilityInventory.ts:181`）；③ `mcpDoctor` 用契约名清单对比真实 listTools（`src/mcpDoctor.ts:220`）；④ `CATALOG_IDENTITY` canonicalize+sha256 摘要（`src/catalogIdentity.ts:73,143`）；⑤ build 时 `generate-mcp-tool-catalog.mjs` 从 `dist/` 引契约，Ajv2020 验证 schema（`generate-mcp-tool-catalog.mjs:29-33`）。浏览器域仍是二层聚合（`browserProviderToolContracts.ts:5`）。

### 4. 数据流

以新增 `record_unknown` 为例：在 `sessionToolContracts.ts` 调 `session()` → `toolContractMetadata` 查 `TOOL_EFFECTS`（`toolEffects.ts:712`），漏登记在模块加载即 throw → `requireOutputSchema` 从 `sessionOutputSchemas`（`toolOutputSchemaGroups.ts:481`）取输出，漏配同样 throw（`toolOutputSchemaPrimitives.ts:49`）→ `examplesFor` 真跑 `inputSchema.parse`（`toolContractHelpers.ts:26`），必填无默认输入补 `TOOL_EXAMPLE_OVERRIDES`（`toolContractExamples.ts:12`）→ 进 TOOL_CONTRACTS。运行期新增**广播压缩**：设 `REA_MCP_INPUT_SCHEMA_PROFILE=compact`（`mcpInputSchemaProfile.ts:29`；createServer :626 注入）时，`presentAdvertisedInputSchema`（`compactInputSchema.ts:354`）按 13 KiB 预算（`mcpInputSchemaProfile.ts:11`，Kimi/Moonshot 单工具 schema 实测上限 ~13.7KB，issue #1484）压缩广播 schema——先剥 annotation 文案再内联 $refs，超预算或超 10 层深度降级 reduced（只广播根 properties，:329-338），数组 items 用 {type:[六种 JSON 类型],items:{}} 万能 schema（:28）；**服务端 canonical 校验不动**（:7-9 注释钉版）。广播示例另把内嵌完整 Evidence 换成 retained-evidence 引用（`advertisedInputExamples.ts:40,61`）。发布链末端 build 生成 catalog 目录+digest。

### 5. 设计决策

**catalog 计数闸取代 floor**：v6.1 的 `PUBLISHED_TOOL_NAME_FLOOR` 只防删除不防新增，已随 `toolContracts.test.ts` 整体删除（b71a591a6）；防漂移改由 boundary 断言承担——`tests/boundary/mcp/serverIdentity.test.ts:114-118` 校验 `CATALOG_IDENTITY.counts` 的 cli_commands/mcp_tools/mcp_prompts 与真实清单相等，:122-140 验证 returnsTargetContent 翻转改变 digest。**显式审计拒绝启发式**：`annotationsFromEffects` 注释仍写 "without tool-name or tool-family heuristics"（`toolEffects.ts:717`）；TOOL_EFFECTS 键集与契约名**完全相等**的快照断言迁至 `toolEffects.test.ts:101-106`，并新增措辞审查（:107 起：描述提 executes/device 的必须登记对应维度）。**保守标注**：`observe_native_calls` 全维 true，注释 "The owned process can change files, show UI and use the network"（`toolEffects.ts:579-580`）。**strict 只在 official 输入**（`officialToolContracts.ts:26`）：官方代理面向第三方 client 需拒未知键，内部面保留演进空间。**示例即测试**（`toolContractHelpers.ts:26`）；不可引用化的示例退出广播但不退出契约（`advertisedInputExamples.ts:67-71`）。**压缩不撒谎**：compact 只删 annotation 与嵌套校验细节，reduced 形态自带"服务器仍完整校验"声明（`compactInputSchema.ts:253-254`）。

### 6. 新人提示

阅读顺序：`toolContractTypes.ts` → `toolEffects.ts` 头 50 行+任选 20 条 → `officialToolContracts.ts` 看工厂 → `toolContracts.ts` → `toolEffects.test.ts` 与 `serverIdentity.test.ts`。加契约 checklist：① 输出 schema 进 `toolOutputSchemaGroups.ts` 对应 Record（八组，:114-596）；② `TOOL_EFFECTS` 登记十维（忘=启动 throw）；③ group 数组追加；④ 必填无默认输入补 `TOOL_EXAMPLE_OVERRIDES`；⑤ 新工具默认 returnsTargetContent=true，确属纯会话产出才进 `TARGET_CONTENT_FREE_TOOLS`。删除工具是 group+catalog digest 两处联动。易错点：TOOL_EFFECTS 是精确集合，多登记已下线工具名也 fail；浏览器工具有二层聚合，改组别只改内层。测试入口：`npx vitest run src/contracts/toolEffects.test.ts tests/boundary/mcp/serverIdentity.test.ts`；conformance 目录随 `npm run build` 重生成，CI 用 `--check` 核对未漂移。
