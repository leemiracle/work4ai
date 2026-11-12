---
title: Claude Code 源码拆解 13：MCP 客户端——连接、OAuth 与工具命名空间
date: "2026-04-11 11:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---

> 系列第 13/20 篇 · 对应主题：MCP 实战

# MCP 客户端：连接、OAuth 与工具命名空间

MCP（Model Context Protocol）是 Claude Code 扩展能力的标准入口：本地子进程、远程 HTTP 服务、IDE 内嵌通道都通过它接入。本文拆解客户端一侧的实现：`client.ts`（3348 行）负责三种传输与结果变换，`auth.ts`（2465 行）实现完整的 OAuth 授权码流程，`config.ts`（1578 行）做四作用域的配置加载与策略过滤，而 `ToolSearchTool` 则解决大规模 MCP 工具集带来的工具描述膨胀问题。

## 连接层：一个 memoize 的 connectToServer

所有连接的入口是 `connectToServer`，被 `memoize` 包裹，同一个 server 名反复请求只建一次连（src/services/mcp/client.ts:595）。函数主体是一串按 `serverRef.type` 分派的传输构造分支：

- `sse`：构造 `ClaudeAuthProvider`，`fetch` 被两层包装：内层 `wrapFetchWithStepUpDetection` 捕获 403 做 scope 升级检测，外层 `wrapFetchWithTimeout` 给每个请求 60 秒超时（`MCP_REQUEST_TIMEOUT_MS`，src/services/mcp/client.ts:463）。`eventSourceInit` 处有一个实现细节：SSE 长连接必须用一个不带超时包装的 `fetch`，否则 60 秒超时会把常驻事件流杀掉（src/services/mcp/client.ts:643-647）。
- `http`：走 `StreamableHTTPClientTransport`，同样的双层 fetch 包装；若 server 已存有 OAuth token，则不注入 session ingress 的 Authorization 头，避免覆盖 SDK 的鉴权（src/services/mcp/client.ts:812-839）。
- `stdio`：`StdioClientTransport` 直接 spawn 子进程，`stderr: 'pipe'` 防止 server 的错误输出污染 UI（src/services/mcp/client.ts:950-957），stderr 内容被累计（上限 64MB）用于连接失败时的诊断（src/services/mcp/client.ts:971-982）。
- `ws`/`ws-ide`：自建 `WebSocketTransport`，Bun 与 Node 走不同构造路径（Node 侧经 `createNodeWsClient` 支持代理 agent 与 TLS 选项）；ws 分支在日志输出前把 `authorization` 头改写为 `[REDACTED]`（src/services/mcp/client.ts:708-783, 752-755）。
- `claudeai-proxy`：claude.ai 托管 connector 经 Anthropic 的 MCP proxy 转发，`createClaudeAiProxyFetch` 每次请求先 `checkAndRefreshOAuthTokenIfNeeded` 再注入 bearer token；401 时仅在 token 确实变更后重试一次，避免每个 connector 翻倍往返（src/services/mcp/client.ts:868-904, 372-399）。
- 另有两条特殊分支：`sse-ide`/`ws-ide` 走 IDE 内嵌通道；Chrome 与 Computer Use 两个官方 server 用 `InProcessTransport` 跑在进程内，注释明确说明是为了避免 spawn 一个约 325MB 的子进程（src/services/mcp/client.ts:909-924）。

```typescript
transport = new StdioClientTransport({
  command: finalCommand,
  args: finalArgs,
  env: { ...subprocessEnv(), ...serverRef.env } as Record<string, string>,
  stderr: 'pipe', // prevents error output from the MCP server from printing to the UI
})
```

`Client` 实例声明的能力里有一个兼容性 hack：`elicitation: {}` 必须发空对象而不是 `{form:{},url:{}}`，因为 Spring AI 的 Java MCP SDK 的 `Elicitation` 类没有字段，遇到未知属性会直接反序列化失败（src/services/mcp/client.ts:996-999）。连接本身是 `Promise.race(connectPromise, timeoutPromise)`，超时后主动 `transport.close()` 并抛出带 server 名的错误（src/services/mcp/client.ts:1048-1077）。

握手完成后有两个防御性处理：server 的 `instructions` 超过 2048 字符会被截断并记日志（src/services/mcp/client.ts:1161-1170）；在 UI 层 `registerElicitationHandler` 覆盖之前，先注册一个默认 elicitation 处理器直接返回 `cancel`，避免初始化窗口内的 elicitation 请求把连接挂住（src/services/mcp/client.ts:1188-1197）。

多 server 并发连接用 `processBatched`（`pMap` 的薄封装）按批处理，本地与远程 server 有不同的批大小（src/services/mcp/client.ts:2218-2224, 552-561）。`getMcpToolsCommandsAndResources` 在装配前先把 disabled server 分出来，它们直接以 `{ type: 'disabled' }` 上报，不产生任何网络连接（src/services/mcp/client.ts:2226-2255）。

连接缓存的失效路径也要配对清理：`clearServerCache` 同时删掉 `connectToServer` 的 memoize 条目和 tools/resources/commands 三个 LRU 缓存，否则重连后拿到的还是旧工具列表（src/services/mcp/client.ts:1648-1673）。运行期所有工具调用前都过 `ensureConnectedClient`：健康时是 memoize 命中零开销，`onclose` 清缓存后则透明重连；SDK 类型的进程内 server 直接短路返回（src/services/mcp/client.ts:1688-1704）。

## Elicitation 处理链

MCP 的 elicitation 能力允许 server 在工具调用中途向客户端索要用户输入。Claude Code 的处理链分两层。传输层在 `registerElicitationHandler` 里先跑 `runElicitationHooks`，配置的 hook 可以以编程方式直接给出响应，完全绕开 UI；hook 不处理才落入交互队列，abort 信号到达时解析为 `cancel`（src/services/mcp/elicitationHandler.ts:68-117）。

工具调用层处理的是 URL 模式的变体：`callMCPToolWithUrlElicitationRetry` 捕获错误码 -32042（`UrlElicitationRequired`）。这里不能用 `instanceof UrlElicitationRequiredError`，因为 SDK 的 Protocol 层把它实例化成了普通 `McpError`，只能比对 `error.code`（src/services/mcp/client.ts:2862-2869）。从 `error.data.elicitations` 里逐条校验出合法的 URL elicitation（`mode === 'url'` 且 url 为字符串），展示给用户、等完成通知后重试原调用，上限 3 次（src/services/mcp/client.ts:2850, 2876-2892）。

## OAuth：本地回调服务器 + PKCE provider

远程 server 返回 401（`UnauthorizedError`）时，连接不直接失败，而是经 `handleRemoteAuthFailure` 转成 `{ type: 'needs-auth' }` 状态并写入 15 分钟的 auth 缓存（src/services/mcp/client.ts:340-361, 257）。授权流程的主体是 `performMCPOAuthFlow`（src/services/mcp/auth.ts:847）：

1. 若配置了 `oauth.xaa`（SEP-990 企业 IdP 路径），走 `performMCPXaaAuth` 且明确不做静默回退，注释解释这是安全相关的决定（src/services/mcp/auth.ts:864-876）。
2. 清掉旧凭证，但先读缓存的 `stepUpScope` 与 `resourceMetadataUrl`：transport 侧的 provider 收到 step-up 401 时会持久化 scope，新一轮流程可以直接用而不必额外探测（src/services/mcp/auth.ts:903-935）。
3. 用配置端口或 `findAvailablePort()` 起本地回调，构造 `ClaudeAuthProvider` 并拉取授权服务器元数据（src/services/mcp/auth.ts:960-999）。
4. 起一个 Node `createServer` 监听 `/callback`，校验 `state` 防 CSRF（src/services/mcp/auth.ts:1099-1118）；错误信息经 `xss()` 消毒后才写进 HTML 响应（src/services/mcp/auth.ts:1122-1128）。

针对无浏览器环境（SSH、远程容器），流程还提供 `onWaitingForCallback`：用户可以手动粘贴回调 URL，客户端从中解析 `code` 与 `state` 完成同样的校验（src/services/mcp/auth.ts:1054-1097）。

`ClaudeAuthProvider` 实现了 SDK 的 `OAuthClientProvider` 接口（src/services/mcp/auth.ts:1376）。它注册为公开客户端（`token_endpoint_auth_method: 'none'`，src/services/mcp/auth.ts:1423），并支持 CIMD（SEP-991）：授权服务器声明 `client_id_metadata_document_supported` 时用 URL 作为 `client_id`，跳过动态客户端注册（src/services/mcp/auth.ts:1439-1452）。`markStepUpPending` 处理 RFC 6749 §6 的一个硬约束：refresh token 不能提升 scope，所以收到 403 `insufficient_scope` 时，`tokens()` 会故意不返回 refresh token，迫使 SDK 走完整的重新授权（src/services/mcp/auth.ts:1460-1471）。`redirectToAuthorization` 在打开浏览器前先把 URL 通过回调通知 UI 显示，浏览器打不开时用户还能手动复制（src/services/mcp/auth.ts:1922-1937）。

token 刷新要跨进程互斥：多个 Claude Code 进程可能同时刷新同一个 server 的 refresh token，而多数授权服务器的 refresh token 是一次性的，竞争会直接互相踢掉。`refreshAuthorization` 用 `mcp-refresh-<serverKey>.lock` 文件锁串行化（拿不到锁最多重试 `MAX_LOCK_RETRIES` 次，间隔 1-2 秒随机抖动）；拿到锁后先清 keychain 缓存重读存储，若 token 剩余有效期超过 300 秒说明别的进程刚刷过，直接复用，不再发请求（src/services/mcp/auth.ts:2090-2159）。XAA 路径的静默刷新 `xaaRefresh` 目前还没有跨进程锁，只有进程内的 `_refreshInProgress` 去重。注释里留着 `TODO(xaa-ga)`，要求 GA 前镜像 `refreshAuthorization` 的 lockfile 模式，并明确引用了仓库 CLAUDE.md 的 "Token/auth caching across process boundaries" 守则（src/services/mcp/auth.ts:1743-1751）。

## 配置：四作用域与策略过滤

`getMcpConfigsByScope` 按作用域加载（src/services/mcp/config.ts:888）。project 作用域会从 CWD 一路向上走到文件系统根，收集沿途所有 `.mcp.json`，再从根向下合并，离 CWD 越近优先级越高（src/services/mcp/config.ts:914-950）。`getClaudeCodeMcpConfigs` 是总装配：enterprise 配置存在时具有排他控制权，直接忽略其他所有来源（src/services/mcp/config.ts:1082-1096）；否则按 plugin < user < project < local 的顺序合并，project server 还须用户批准（`getProjectMcpServerStatus === 'approved'`）才进入连接池（src/services/mcp/config.ts:1166-1170, 1231-1238）。plugin server 与手动配置的 server 之间按内容签名去重，被压制的重复项以 `mcp-server-suppressed-duplicate` 错误类型上报给 `/plugin` UI（src/services/mcp/config.ts:1211-1229）。

配置值在解析阶段做环境变量展开：`expandEnvVars` 按传输类型展开 command/args/env 或 url/headers，缺失的变量去重后以 `missingVars` 返回，IDE 与 SDK 类型原样透传（src/services/mcp/config.ts:556-616）。企业策略过滤支持三种匹配维度：server 名精确匹配、stdio 的 command 数组匹配、远程 server 的 URL 模式匹配（`urlPatternToRegex`），denylist 绝对优先于 allowlist（src/services/mcp/config.ts:364-422）。

`officialRegistry.ts` 是一个 72 行的小模块：启动时 fire-and-forget 拉取 `https://api.anthropic.com/mcp-registry/v0/servers`，把所有官方 server 的 remote URL 归一化（去 query 和尾斜杠）后存进 `Set`，`isOfficialMcpUrl` 在 registry 未加载时 fail-closed 返回 `false`（src/services/mcp/officialRegistry.ts:33-68）。

## 命名空间与 MCPTool 包装

MCP 工具通过 `mcp__<server>__<tool>` 前缀进入 Claude Code 的工具命名空间。`buildMcpToolName` 与 `mcpInfoFromString` 互逆（src/services/mcp/mcpStringUtils.ts:50, 23）；注释说明一个已知限制：server 名含 `__` 时解析会错位（src/services/mcp/mcpStringUtils.ts:14-17）。权限校验始终用全限定名，这样针对内建工具的 deny 规则不会误伤同名的 MCP 工具（src/services/mcp/mcpStringUtils.ts:60-67）。

`MCPTool.ts` 本身只是一个模板：`name: 'mcp'`、`maxResultSizeChars: 100_000`、所有方法都被注释标为"Overridden in mcpClient.ts"（src/tools/MCPTool/MCPTool.ts:27-55）。实例化发生在 `fetchToolsForClient`（memoizeWithLRU 缓存，src/services/mcp/client.ts:1743）：对每个 server 返回的工具做 Unicode 消毒后，把 MCP 注解映射到 Tool 接口，`readOnlyHint` 同时决定 `isConcurrencySafe` 与 `isReadOnly`，`destructiveHint`、`openWorldHint` 一一对应（src/services/mcp/client.ts:1795-1809）。`_meta` 里两个 Anthropic 扩展键被特殊处理：`anthropic/searchHint` 作为搜索提示（空白折叠成单行，防止污染 deferred tool 列表），`anthropic/alwaysLoad` 让工具绕过延迟加载（src/services/mcp/client.ts:1776-1785）。描述超 2048 字符同样截断（src/services/mcp/client.ts:1790-1794）。

## classifyForCollapse：手工维护的工具白名单

MCP 工具的 UI 折叠分类不靠 AI 推断，而是两张静态集合：`SEARCH_TOOLS` 与 `READ_TOOLS`，覆盖 Slack、GitHub、Linear、Datadog、Sentry、Notion、Gmail、Jira、Asana、Grafana、PagerDuty、Stripe、Kubernetes 等几十个常见 server 的工具名（src/tools/MCPTool/classifyForCollapse.ts:14-139, 142-586）。匹配前把 camelCase/kebab-case 归一化成 snake_case，未知工具保守地不折叠（src/tools/MCPTool/classifyForCollapse.ts:588-604）。工具名跨安装稳定，所以这里枚举比启发式可靠，白名单不会误判。

## ToolSearchTool：工具定义的延迟加载

挂上几个大 server 后，MCP 工具动辄上百个，全部展开 JSONSchema 会把系统提示撑爆。Claude Code 的解法是延迟加载：`isDeferredTool` 规定 MCP 工具默认全部 deferred，只有 `alwaysLoad: true`（来自 `_meta['anthropic/alwaysLoad']`）能豁免；`ToolSearch` 自身永不 deferred（src/tools/ToolSearchTool/prompt.ts:62-71）。deferred 工具在提示里只有名字、没有 schema，模型需要时调用 ToolSearch 取回完整定义。

ToolSearch 支持两种查询。`select:A,B,C` 直接按名选取，支持逗号多选；如果名字在全量工具集里而不在 deferred 集里，也照常返回。注释说明这是为了消化 subagent 和压缩后直接发裸工具名的场景，避免无谓的重试（src/tools/ToolSearchTool/ToolSearchTool.ts:358-406）。关键词搜索是手写的打分器：把工具名拆成 parts（`mcp__slack__send_message` → `[slack, send, message]`），精确 part 命中 MCP 工具 +12 分、部分命中 +6，`searchHint` 命中 +4，描述按词边界正则命中 +2（src/tools/ToolSearchTool/ToolSearchTool.ts:266-291）。`+term` 前缀表示必选词，先做过滤再打分（src/tools/ToolSearchTool/ToolSearchTool.ts:220-257）。描述经 `memoize` 缓存，deferred 集合变化时以名字拼接串为 key 整体失效（src/tools/ToolSearchTool/ToolSearchTool.ts:91-100）。

结果映射回 `tool_result` 时不是文本，而是一组 `tool_reference` block，即客户端侧的引用，由 API 展开成真实工具定义（src/tools/ToolSearchTool/ToolSearchTool.ts:462-469）。没有命中且还有 server 在连接中（`type === 'pending'`）时，结果里附带 `pending_mcp_servers`，提示模型稍后重试（src/tools/ToolSearchTool/ToolSearchTool.ts:448-455）。

## Rich output：结果变换与大输出落盘

MCP 结果经 `transformMCPResult` 归一成三种形态：`toolResult` 字符串、`structuredContent`（JSON 序列化并附 `inferCompactSchema` 生成的 jq 风格类型签名，深度 2、每对象最多 10 个键）、以及 `content` 数组逐项变换（src/services/mcp/client.ts:2662-2697, 2644-2660）。`transformResultContent` 处理富媒体：图片 base64 解码后经 `maybeResizeAndDownsampleImageBuffer` 压到 API 尺寸限制内；音频与非图片 blob 不再塞进上下文，而是 `persistBlobToTextBlock` 落盘后只回一个文件路径（src/services/mcp/client.ts:2490-2523, 2593-2627）。

超大文本结果走 `processMCPResult`：超过阈值时，若含图片则退回截断（图片落盘会破坏压缩与可视性）；否则以 `mcp-<server>-<tool>-<timestamp>` 为 ID 调 `persistToolResult` 存盘，返回给模型的是一段读取指引加上格式描述（src/services/mcp/client.ts:2720-2799）。这条路径可用 `ENABLE_MCP_LARGE_OUTPUT_FILES` 环境变量关掉。

## 辅助工具：resources 与 authenticate 伪工具

`ListMcpResourcesTool` 标记 `shouldDefer: true`，自己也走延迟加载（src/tools/ListMcpResourcesTool/ListMcpResourcesTool.ts:50）。调用时对每个 server 先 `ensureConnectedClient`（健康时是 memoize 命中，断线后返回新连接），再取 LRU 缓存的资源列表；单个 server 重连失败只记日志返回空数组，不拖垮整体结果（src/tools/ListMcpResourcesTool/ListMcpResourcesTool.ts:79-96）。

`McpAuthTool` 是一个生成的伪工具：server 处于 needs-auth 状态时，它的真工具不在列表里，取而代之的是 `mcp__<server>__authenticate`（src/tools/McpAuthTool/McpAuthTool.ts:63）。模型调用它时，以 `skipBrowserOpen` 启动 `performMCPOAuthFlow`，把授权 URL 作为工具结果返回给模型转达用户；OAuth 回调在后台完成后，`reconnectMcpServerImpl` 重连，再按 `mcp__<server>__` 前缀整体替换 appState 里的工具集，伪工具因为共享同一前缀被自动清掉（src/tools/McpAuthTool/McpAuthTool.ts:126-166）。

## 本篇涉及的源码文件

- `src/services/mcp/client.ts`：连接管理（stdio/SSE/HTTP 传输、elicitation、结果变换与大输出落盘）
- `src/services/mcp/auth.ts`：MCP server OAuth 授权码流程与 `ClaudeAuthProvider`
- `src/services/mcp/config.ts`：四作用域 server 配置加载、去重与企业策略过滤
- `src/services/mcp/officialRegistry.ts`：官方 MCP registry 拉取与 URL 判定
- `src/services/mcp/mcpStringUtils.ts`：`mcp__server__tool` 命名空间的构造与解析
- `src/services/mcp/elicitationHandler.ts`：elicitation 请求处理器注册与 hook 执行
- `src/tools/MCPTool/MCPTool.ts`：MCP 工具的 Tool 接口模板
- `src/tools/MCPTool/classifyForCollapse.ts`：search/read 工具白名单，驱动 UI 输出折叠
- `src/tools/ToolSearchTool/ToolSearchTool.ts`：延迟工具的关键词检索与 schema 按需加载
- `src/tools/ToolSearchTool/prompt.ts`：`isDeferredTool` 延迟判定规则与搜索提示词
- `src/tools/ListMcpResourcesTool/ListMcpResourcesTool.ts`：跨 server 资源枚举
- `src/tools/McpAuthTool/McpAuthTool.ts`：needs-auth 状态下的 authenticate 伪工具
