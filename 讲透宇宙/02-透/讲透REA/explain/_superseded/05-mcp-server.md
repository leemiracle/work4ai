# src/server/createServer.ts：MCP server 组装枢纽

## 角色定位

createServer.ts 是 fan-out=101 的全仓最高扇出节点（fan-in=57），图谱里唯一破百的文件。它是 MCP 服务器总装配线：接收一个分析端口与可选会话，把 contracts 层的 138 个工具契约注册成可服务的 `McpServer` 实例。注释钉住可测性承诺："Construct one MCP server without acquiring subprocess resources"（src/server/createServer.ts:162-163）——组装本身不启动任何外部引擎，全部 provider 依赖从 `CreateServerOptions` 的 17 个可选字段注入（src/server/createServer.ts:71-90），未注入的就地构造轻量默认实现。

## 内部结构

四个私有构件加一个导出：

- `createMcpServer`（src/server/createServer.ts:144-160）：实例化子类 `EvidenceMcpServer`，带 PRODUCT_IDENTITY 名字与版本；按有无 session 切换 instructions——无会话用 ACTIVE_TARGET_INSTRUCTIONS、有会话用 TARGET_FREE_INSTRUCTIONS（src/server/createServer.ts:65-69）；有会话时把 `(evidence) => session.recordEvidence(evidence)` 挂进构造器（src/server/createServer.ts:157-159）。
- `installSessionToolAvailability`（src/server/createServer.ts:92-142）：为 session 工具组装可用性策略，每项能力走双通道——provider 已注入，或平台+环境变量探测：binaryLayout 要 linux+x64 且 `REA_PWNTOOLS_PYTHON` 为绝对路径（src/server/createServer.ts:112-116）、browser 观测看 `REA_BROWSER_EXECUTABLE`（src/server/createServer.ts:104-106）。
- `createSessionRecorders`（src/server/createServer.ts:292-321）：四个闭包记录器（evidenceById/activeTarget/recordEvidence/recordEvidenceWithUnknown），无会话全为 undefined，工具层据此自适应。
- 导出 `createServer`（src/server/createServer.ts:167-290）串行注册：binary analysis 六族（official/enhanced/native/artifact/managed/workflow，src/server/createServer.ts:331-381）→ Android/diagnostics/EVM/crash/firmware → 观测工具组（实现于 src/server/createServer.ts:383-424）→ web 四件套与 JS recovery → guided prompts → 仅当有会话才注册 session 工具并带 availabilityPolicy 与 startedAt（src/server/createServer.ts:278-288）。

## 外部连接

唯一生产调用方是 src/main/transport.ts:71：`(dependencies.createServer ?? createServer)(session, session, {...})`——session 同时充当 `AnalysisOperationPort` 与 `BinarySessionPort` 双角色，并注入动态加载的五个可选 provider。下游汇 35 个 register*.ts 模块；上游从 9 个 composition 工厂取默认 provider（如 createEvmInterfaceService，src/server/createServer.ts:2）。特殊连接是 Android provider 生命周期托管：先链住 `server.onclose` 原回调再追加 `android.close()`（src/server/createServer.ts:196-205），再包装 `server.close` 用 `Promise.allSettled` 并联两者（src/server/createServer.ts:207-211）。

## 数据流

组装期：可选 provider 集合 + 会话 → 可用性策略 → 记录器闭包 → `ServerToolContext` 六件套（src/server/createServer.ts:184-194）→ 各 register 消费。运行期：MCP 客户端 tools/call → SDK 分派到注册的 handler → 调 provider 执行 → 结果连同 `createEvidence` 生成的证据经 `recordEvidence` 回写 session 账本 → 编码回客户端（src/server/registerOfficialTools.ts:70-74）。超大结果或错误由 EvidenceMcpServer 的 transport 包装保留进 Evidence 账本而非静默丢弃（src/server/EvidenceMcpServer.ts:29-40 的 connect 覆写）。

## 设计决策

- **组装零资源**：重量级 provider（Ghidra/Jadx/binwalk…）不在本文件构造，注入或延迟创建——单测可以只给两三个假 provider 验证注册拓扑。
- **可用性环境探针**：策略不要求 provider 预实例化即可报能力（src/server/createServer.ts:98-137），无头 CI 与桌面环境的工具清单自动分岔，不可用原因如实告知客户端。
- **close 双路径**：对端断开与显式 close() 都兜住 Android 清理，allSettled 保证一个失败不掩盖另一个。
- **instructions 随会话切换**：有无目标生命周期工具是两种产品形态，prompt 文案跟着变而非一份通用辞令。

## 新人提示

新增工具类：写 register 模块 + contracts 契约，再在 createServer 加一行调用并决定是否依赖 session——放进 `if (session !== undefined)` 块意味着无会话嵌入场景拿不到它。改 `CreateServerOptions` 要同步 installSessionToolAvailability 的 optionalFeatures 分支（src/server/createServer.ts:100-137），漏了工具会永远"不可用"。transport.ts 每 discovery probe 重建 server（src/main/transport.ts:68-76），createServer 必须可重入、不能持有跨调用可变全局。Android onclose 链式包装顺序敏感：先存旧回调再赋新的，反了会丢 SDK 原生清理。
