<!-- source: knowledge-graph tour step | files: src/server/createServer.ts, src/server/toolResult.ts, src/server/EvidenceMcpServer.ts -->

# REA 精讲 04：MCP Server 组装与结果序列化

三文件同属 server 装配层：`createServer.ts`（919 行）把 36 组工具契约装配成 MCP server，`toolResult.ts` 的 `ToolResultDelivery` 类负责序列化与超预算转错误，`EvidenceMcpServer.ts` 的 ErrorEvidenceTransport 在 send 边界兜底。铁律：**适配层只做翻译，不做业务**。

### 1. 角色定位

`createServer` 是 server 层总枢纽，但刻意"薄"：只做依赖注入默认化、可用性计算、按固定顺序注册 36 个 register*Tools 文件（44 处调用含单工具）。签名 `(source, options?)`（src/server/createServer.ts:285-288）：source 是 `ServerAnalysisSource` 联合——传 `{kind:"session", session}` 追加目标生命周期工具族，不传则保留测试/嵌入用的"固定目标"缝（:280-284）。`toolRegistrationOptions.ts`（34 行）把契约投影为 SDK 选项（:20-34），`applicationValidatedInputSchema` 让 SDK 校验直通、application 拥有结构化输入失败（:9-17）。`toolResult.ts` 的 `ToolResultDelivery` 类（:47）统一"编码预算+恢复策略"。

### 2. 内部结构

**createServer.ts** 五块骨架：`CreateServerOptions` 声明 34 个可选注入字段（:149-184），缺省时即时走组合工厂（如 `options.evmInterface ?? evmInterfaceModule.create(environment)`，:298-299）。`createMcpServer`（:253-278）构造 `EvidenceMcpServer`：instructions 按 session 有无切换（:266-270），`session.recordEvidence` 绑进 server（:272-274），三个新轴 delivery/compactPresentation/omitOutputSchemas 一并注入。`installSessionToolAvailability`（:186-251）算 **15 项** optionalFeatures，每项是"注入了 provider"∨"平台+环境变量启发"的析取——如 binaryLayoutEnabled 要求 linuxX64 且 `REA_PWNTOOLS_PYTHON` 绝对路径（:193-196,214）；policy() 每次查询重跑并合并 frida 加载失败（:233-247）。注册顺序钉死（:444-593）：binary 六族（:444）→ RE 工具族 reverseEngineering/frida/cutter/gdb/rizinDebug（:445-505，带 evidence recorder 与 session 失效钩子）→ onclose/close 安装（:506-521）→ capture/signal（:522-535）→ configuredAnalysis 大族（:536，定义 :629-776，内含 android/jeb/go/rust/wasm/evm/sqlite 等）→ adb/pcap/flutter/apktool（:545-574）→ observation（:575）→ prompts（:576）→ session 族（:577-593）。`closeProviders` 收拢 **29 个** close（:369-413）。

**compactInputSchema（v6.5 新）**：`selectCompactInputSchemaPresentation` 解析 `REA_MCP_INPUT_SCHEMA_PROFILE`（:619-627）并在 :339 注入；`EvidenceMcpServer.registerTool` override 在注册点压缩 advertised schema、canonical parser 不动（:144-181）。预算 13KiB（src/config/mcpInputSchemaProfile.ts:11，Moonshot 单工具 schema 上限 ~13.7KB）；数组 items 用 `{type:[六种JSON类型],items:{}}` 万能 schema（src/contracts/compactInputSchema.ts:24-26）。

### 3. 外部连接

上游消费方唯一：`src/main/transport.ts:84-109` 的 serve 工厂闭包——每连接新建 android provider（:87-89）、注入 delivery 与可选 provider（:91-100），注释"SDK 可能丢弃 discovery probe 重建 server"（:86）。契约路：`TOOL_CONTRACTS` 36 组纯 spread 聚合（src/contracts/toolContracts.ts:39-76），register 文件统一走 `server.delivery.toCallToolResult/toEvidenceToolResult`（src/server/registerOfficialTools.ts:78,101）。预算路：delivery 由 `selectToolResultDelivery` 创建（src/server/createServer.ts:597-607，`REA_MCP_MAX_RESPONSE_BYTES` 非法直接 throw，server 不带病启动）；下限 10MiB（src/config/mcpResponseBudget.ts:9）。

### 4. 数据流

以 `export_web_scripts` 走全链（src/server/registerWebScriptTool.ts:34-45）：`logToolExecution` 计时包裹 → `exportWebScriptsValidated(input, {signal: context.mcpReq.signal})`（:38-40，MCP 取消信号透传）→ 失败即错误投影；成功先 `recordEvidence`（:44）→ `delivery.toEvidenceToolResult`（:45）——**完整 Evidence 直接进 structuredContent**（v6.2 废 evidenceEnvelope 信封，docs/migration-6.2.md:8-24，`value = evidence.normalized_result`）。编码在 `successResult`（src/server/toolResult.ts:152-170）：`encodeToolResult` 流式累计字节与 code units（src/server/toolResultEncoding.ts:87-119），超限即失败——**拼巨型字符串之前**即知放不下；通过则 text（JSON 全量重复）+structuredContent 双表示。超预算分支：转 `AnalysisResourceConstraintError`"操作已完成、结果未截断"（toolResult.ts:180-202），details 带 `evidence_reference`（:80-84）；`analyze_function` 还附 `inspect_analysis_view` 翻页续读 continuation（:29-44）。错误结果 `isError:true` 只带 text diagnostic，structuredContent 是私有载具（:129-150）；错误本身也超预算时 `ErrorEvidenceTransport.recoverError`（src/server/EvidenceMcpServer.ts:346-456）先把原始错误存成 Evidence（:397-413）再换约束错误带 `evidence_reference`（:434-441），同连接 `export_evidence_bundle` 取回（:447-448；migration-6.2.md:43-48）。

### 5. 设计决策

- **预算数学**：delivery 构造 `configured - 1024`（toolResult.ts:50，给 JSON-RPC envelope 留量）；编码期双约束——字节数超收缓冲或 code units 超 `MAX_STRING_LENGTH-1024`（toolResultEncoding.ts:6,106-115），V8 单字符串上限独立于接收缓冲。
- **schema 广告不改校验**：`withAdvertisedJsonSchema` 用 `Object.defineProperty` 重定义 Zod 的 `~standard.jsonSchema`（src/contracts/toolSchemaMetadata.ts:178-207），`memoizeByTarget` 缓存投影（:209）——SDK 每次 tools/list 重转换而注册后契约不可变；compact 只动 advertised 投影，canonical parser 原封。
- **关闭链原子性**：`server.close` 包成 `Promise.allSettled([closeServer(), closeProviders()])`，任一 reject 都抛（src/server/createServer.ts:516-521）；原 onclose 链保留并追加 provider 清理（:506-515）。
- **recorder 适配层**：`createSessionRecorders`（:778-802）把 evidenceById/activeTarget/recordEvidence/recordEvidenceWithUnknown 四个 session 方法包成 undefined-able 闭包，register* 文件不必感知 session 存在性。
- **transport 记账**：ErrorEvidenceTransport 跟踪 pendingTools/pendingCompletions，notifications/cancelled 即释放（EvidenceMcpServer.ts:215-249）；请求级 AbortSignal 走 AsyncLocalStorage（:46-50）。

### 6. 新人提示

**阅读顺序**：toolRegistrationOptions.ts → toolResult.ts → toolResultEncoding.ts → EvidenceMcpServer.ts → createServer.ts。**易错点**：①Evidence 无信封直读 structuredContent，先判 `isError`——错误结果不带 structuredContent（migration-6.2.md:26-37）；②超预算错误 `content` 为空数组非 bug，等 transport 接力；③预算与 profile 在 server 启动时定格，改配置须重建 server（migration-6.2.md:46-48）；④optionalFeatures 一次算定，policy 每次查询重跑；⑤新工具先加契约进 `TOOL_CONTRACTS` 再挂 register*，顺序即 tools/list 顺序。**测试入口**：`src/server/toolResultEncoding.test.ts`、`src/contracts/compactInputSchema.test.ts`、`tests/boundary/mcp/serverIdentity.test.ts:114-118`（v6.1 的 contractSnapshot.test.ts 已删）；端到端用 sessionless `createServer(analysis)` 起内存 server。
