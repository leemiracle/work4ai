# 10 · React 管理界面：配置、观测与 Playwright 保障

## 角色定位

本区域是 agentgateway 的**管理面前端**（management plane UI），在 16 层架构中位于 L15「React 管理界面」（知识图谱实测：L15 层 688 节点，仅次于 L14 Rust 基础 crate 的 448+ 与数据面各层）。它与 Rust 后端的边界划分得非常干净：

- **后端 ui.rs 只做三件事**：暴露 management JSON API（`crates/agentgateway/src/ui.rs:93-115` 的路由表：`/api/runtime`、`/api/config`、`/api/config/effective`、`/api/logs/*` 四端点、`/api/costs/*`、`/api/budgets/status`、`/cel`）、托管构建产物静态资源（`ui.rs:387` 的 `serve_ui_asset`）、以及把 `/` 重定向到 `/ui`（`ui.rs:122`）。所有业务逻辑都下沉到 `crate::telemetry::log_store` 等后端模块，`search_logs` 处理函数就是一行直通转发（`ui.rs:1119-1126`）。
- **前端只做配置编辑与观测呈现**：它不经手数据面流量，唯一的"数据面体验"是 Playground——由浏览器**直连网关数据面端口**发起对话（见下文数据流），而非经 management API 中转。

技术上这是 Vite + React 19 + TanStack Router + TanStack Query + Monaco Editor 的 SPA（`main.tsx:1-8` 同时引入 react-query 与 router；Monaco 相关见 `vite.config.ts:22` 的 worker 别名）。整个 UI 以 `/ui/` 为 base 部署（`vite.config.ts:6`），dev server 跑 19000 端口（`vite.config.ts:33-34`），e2e preview 跑 127.0.0.1:19100（`vite.config.ts:37-38`，与 `playwright.config.ts:13` 的 baseURL 对应）。

一句话定位：**它是网关运维者的驾驶舱——所有 LLM/MCP/Traffic 配置在这里编辑成 YAML config，所有请求日志/成本/分析在这里消费，而配置的真正生效仍由 Rust 后端的 xDS/文件重载机制完成**（L03-L05 各层），UI 只负责把 `/api/config` 的 POST 变成一次可审计的 diff 保存。

## 内部结构

### main.tsx：298 行的装配中枢

入口文件是全仓路由的唯一声明地。登录路由被刻意放在 Shell 之外——源码注释明说："Keep login outside Shell so it does not fetch protected application data"（`main.tsx:51-56`）：`/login` 直挂 rootRoute，其余所有页面挂 `appRoute`（id `'app'`，`main.tsx:58-62`），由 `Shell` 组件统一注入数据预取与布局。五大目标页面各自的路径绑定：`/llm/policies`→PoliciesPage（`main.tsx:106-110`）、`/llm/models`→ModelsPage（`main.tsx:76-80`）、`/llm/logs`→LogsPage 与 `/llm/analytics`→AnalyticsPage（`main.tsx:94-104`）、`/llm/costs`→CostsPage（`main.tsx:118-122`）、`/llm/playground`→PlaygroundPage（`main.tsx:130-134`）。

两处装配细节值得注意：`RawConfig` 页是全仓唯一的懒加载路由（`React.lazy` + Suspense，`main.tsx:43-47` 与 `228-240`），因为 Monaco 编辑器体积大；路由树用 `addChildren` 嵌套组装，settings 三个子路由嵌套挂载（`main.tsx:269`）。TanStack Router 的类型注册通过 module augmentation 完成（`main.tsx:275-279`）。QueryClient 全局默认 `staleTime: 5_000` 且关闭窗口聚焦重拉（`main.tsx:281-288`）——管理面数据五秒新鲜度够用，避免无谓轮询。

### types.ts：238 行的类型中枢

这是全 UI 的类型收束点，实测 **49 个文件** `import ... from '@/types'`（grep 实证，与批 95 发现一致）。它的核心策略是**"生成类型 + 本地推导"两层结构**：

- 第 1-41 行从两个**生成物** `.d.ts` 导入：`@/gateway-admin`（`types.ts:1` 的 `StoresDump`）与 `@/gateway-config`（`types.ts:2-41` 约 35 个 `Local*` 类型）。随后 43-80 行用 `Extract`/`keyof`/`Omit` 把生成类型**再导出为语义别名**——例如 `ProviderName = Extract<LocalLLMModels['provider'], string> | keyof Extract<...>`（`types.ts:43-45`）同时收窄字符串字面量与 custom 对象键；`GatewayConfig = Omit<LocalConfig, 'llm' | 'mcp'> & { llm?: LlmConfig | null; mcp?: McpConfig | null }`（`types.ts:114-117`）把 MCP target 的四种传输（sse/mcp/stdio/openapi，`types.ts:98-110`）替换成 UI 更好用的联合类型。
- 第 120 行起是**手写的观测域类型**，与后端 `log_store` 的 serde 结构一一对应：`LogEntry`（含 `genAi` 元数据、`usage` token 计数、`turn` 输入输出角色、`hasPayload` 懒加载标记，`types.ts:120-152`）、`LogFilters`（`types.ts:154-162`）、`SearchLogsRequest/Response`（游标分页 `nextCursor`，`types.ts:169-175`、`195-198`）、`TailEvent`（`types.ts:200-203`）、`AnalyticsSummaryRequest` 的 `groupBy` 枚举七字段（provider/requestModel/responseModel/httpStatus/attributes/ttft/outputTokensPerSecond，`types.ts:180-189`）、`AnalyticsTotals` 精确到 `ttftMs`/`cacheReadTokens`/`reasoningTokens`（`types.ts:205-221`）。

这样设计的收益：配置域类型随 Rust schema 演进零手工同步（见外部连接节），观测域类型手工维护换取更精确的可空性标注。

### api/ 客户端层：10 个文件按域分拆

`src/api/` 下 10 个文件按后端域分拆，`src/api.ts` 是 8 模块的桶导出（`api.ts:1-8`）。基座是 `base.ts`：

- `apiBase = import.meta.env.VITE_AGENTGATEWAY_API ?? ''`（`base.ts:1`）——空串即同源部署（生产模式 UI 由 Rust 进程托管），dev 模式可指向本地网关。
- `requestApi` 的认证处理是这个文件最精巧的部分：fetch 用 `credentials: 'include'` + `redirect: 'manual'`（`base.ts:8-12`），注释解释原因——"Authentication must use document navigation; fetch cannot follow cross-origin login redirects"（`base.ts:7`）。遇到 401 或 `opaqueredirect` 时（`base.ts:13`），校验 Location 是站内相对路径后拼接 `returnTo` 参数做整页跳转（`base.ts:26-29`）；`redirecting` 布尔闸门防多请求并发触发重复跳转（`base.ts:20-21`），`hasSuccessfulRequest` 标记确保首屏就 401 时不至于死循环 reload 而是抛出人话错误（`base.ts:17-19`）。
- `requestJson<T>` 统一错误归一：非 2xx 时尝试 JSON 解析 body 取 message，退化到 statusText（`base.ts:37-59`）。

**logsApi.ts 的 `streamLogs` 是 SSE 流式的教科书实现**（批 91 盲区补扫确认）：它是一个 `async function*` 异步生成器（`logsApi.ts:32-35`），POST `/api/logs/tail`（`logsApi.ts:36`），拿 `response.body.getReader()` + `TextDecoder` 手工解帧（`logsApi.ts:46-48`）——按 `\n\n` 切分 SSE 事件块并保留半截 buffer（`logsApi.ts:54-55`），用正则 `^event:\s*(.+)$` / `^data:\s*(.+)$` 提取字段（`logsApi.ts:57-58`），`event: log` 就 `yield JSON.parse(data)`，`event: error` 就抛异常（`logsApi.ts:59-64`）。调用方拿到的是 `AsyncGenerator<TailEvent>`，`for await` 即消费。

其余三个目标文件：`runtimeApi.ts` 定义 `RuntimeUser`（subject/name/email/canLogout，`runtimeApi.ts:3-11`）与 `RuntimeInfo`——build 五元组（version/gitRevision/rustVersion/buildProfile/buildTarget）、`ui.gatewayMode`（standalone|xds）、`ui.configStoreMode`（file|hybrid|readOnly）、`configReload.synchronized` 镜像 config_synchronized 指标（`runtimeApi.ts:13-33`），GET `/api/runtime`（`runtimeApi.ts:35-37`）。`playgroundApi.ts` 的 `sendChatCompletion` 把 baseUrl 拼 `/v1/chat/completions`（`playgroundApi.ts:11`）、可选 `Authorization: Bearer`（`playgroundApi.ts:15`）、`credentials: 'omit'`（`playgroundApi.ts:18`，见设计决策）；`sendMcpJsonRpc` 处理 `mcp-session-id` 请求/响应头对（`playgroundApi.ts:44`、`64`），`parseMcpResponse` 能解 `text/event-stream` 的 MCP SSE 响应（按 `data:` 行聚合再 parse，`playgroundApi.ts:77-90`）。

### pages/ 骨架与 policies/ 编辑器矩阵

页面消费 API 有两种模式：react-query hook（`hooks.ts:57-81` 的 `useRawGatewayConfig`/`useEffectiveGatewayConfig`/`useRuntimeInfo`，queryKey 分别为 `['config']`/`['effectiveConfig']`/`['runtime']`，全部 `retry: false`）与直接 async 调用（Logs/Playground 自己管竞态，见数据流节）。

**PolicyDrawer 的 15 路分派**（批 94 发现）实锤于两处：`PolicyEditorKind` 是恰好 15 个字面量的联合类型（`PolicyDrawer.tsx:40-55`：accessLog/authorization/backendAuth/cors/extAuthz/extProc/jwtAuth/localRateLimit/mcpAuthentication/mcpAuthorization/mcpGuardrails/oidc/remoteRateLimit/tracing/transformations）；`CustomPolicyEditor` 用条件链渲染——14 个显式分支起于 `accessLog`（`PolicyDrawer.tsx:228`）止于 `tracing`（`PolicyDrawer.tsx:331`），最后的 else 兜底渲染 `TransformationsPolicyEditor`（`PolicyDrawer.tsx:339-346`），合计 15 路。映射源头在 `registry.ts` 的 `policyUi` 表（`registry.ts:20-102`）：16 个 policyKey 各配 title/icon/lucide 图标，其中 14 个带 `customEditor`（如 `cors: { title: 'CORS', icon: Workflow, customEditor: 'cors' }`，`registry.ts:58`），`apiKey`（`registry.ts:46`）与 `basicAuth`（`registry.ts:57`）不配——落回 `GenericPolicyEditor` 的 schema 驱动表单（`PolicyDrawer.tsx:203-215`）。一个巧妙的复用：`mcpAuthorization` 直接复用 `AuthorizationPolicyEditor` 并预填示例表达式 `mcp.tool.name == "get_weather"`（`PolicyDrawer.tsx:299-306`）。

Policies 页则是这套矩阵的目录页：LLM 侧 `schemaRoot="LocalLLMPolicy"`、四节分组（Access 七键/Safety/Traffic Shaping/Mutation，`Policies.tsx:23-42`），MCP 侧 `schemaRoot="FilterOrPolicy"`（`Policies.tsx:91-113`）；policyCatalog 用 schema 的 `$defs` 属性键做**一等目录来源**、`policyUi` 只兜底（`Policies.tsx:149-167`），`customEditor: ui?.customEditor`（`Policies.tsx:164`）逐键传给 PolicyDrawer。LLM 与 MCP 的禁用语义不同：LLM 侧置 `null`（localRateLimit 特判置 `undefined`，`Policies.tsx:81-86`），MCP 侧 `delete`（`Policies.tsx:107-110`）——因为 LocalLLMPolicy 的 serde 用 `Option<Option<T>>` 区分"显式 null=禁用"。

## 外部连接

### 前端 fetch ↔ 后端 management API 的配对

每个 api/ 文件都精确对到 `ui.rs` 路由表的一行：

| 前端调用 | 源码锚 | 后端路由 | 源码锚 |
|---|---|---|---|
| `searchLogs` | `logsApi.ts:11-16` | `POST /api/logs/search` | `ui.rs:109` |
| `getLog` | `logsApi.ts:18-23` | `POST /api/logs/get` | `ui.rs:110` |
| `streamLogs` | `logsApi.ts:36` | `POST /api/logs/tail` | `ui.rs:111` |
| `analyticsSummary` | `logsApi.ts:25-30` | `POST /api/logs/analytics/summary` | `ui.rs:112` |
| `getRuntimeInfo` | `runtimeApi.ts:35-37` | `GET /api/runtime` | `ui.rs:94` |
| `getConfig`/`writeConfig` | `configApi.ts:4-6`/`12-17` | `GET/POST /api/config` | `ui.rs:95` |
| `getEffectiveConfig` | `configApi.ts:8-10` | `GET /api/config/effective` | `ui.rs:96` |
| `refreshBaseCosts`/模型目录 | `costsApi.ts:18`/`24` | `POST /api/costs/refresh-base`、`GET /api/costs/models` | `ui.rs:113-114` |
| Playground 直连 | `playgroundApi.ts:11` | `/v1/chat/completions`（数据面，**不在 ui.rs 路由表**） | — |

SSE 的服务端实现在 `tail_logs`（`ui.rs:1146-1207`）：返回 `Sse<ReceiverStream<Result<Event, Infallible>>>`，tokio 任务里 `mpsc::channel(32)` 缓冲（`ui.rs:1160`），`tokio::select!` 双定时器——poll 每 1 秒拉增量（`ui.rs:1162`）、heartbeat 每 15 秒发 `event("heartbeat")` 防 中间层断连（`ui.rs:1199`）；日志事件 `event("log")`（`ui.rs:1181`）、错误 `event("error")` 后即 return（`ui.rs:1190-1193`）。limit 在服务端 clamp 到 1-500（`ui.rs:1158`）。前端 `streamLogs` 解析的 event 名与这里逐字对应——这是一对跨语言的 SSE 契约。

### @/gateway-config 生成物的构建链

`types.ts` 消费的 `@/gateway-config` 并非手写：`scripts/generate-schema.mjs` 从 Rust 仓的 `schema/config.json` / `schema/admin.json` / `schema/cel.json` 出发（`generate-schema.mjs:14`、`17`），经 `json-schema-to-typescript` 的 `compileFromFile` 三路编译出 `src/cel.d.ts`、`src/gateway-config.d.ts`、`src/gateway-admin.d.ts`（`generate-schema.mjs:21-25`），并把 schema 拷进 `src/generated/` 供运行时 Monaco 校验消费（`generate-schema.mjs:34-35`）。编译前有一道 `sanitizeSchemaForTypes` 清洗（`generate-schema.mjs:37-54`）：递归剔除 `isImpossibleSchema` 判定的空 enum 节点（`generate-schema.mjs:60-63`），否则 `oneOf` 里残留 `enum: []` 会让 TypeScript 编译器直接报错。这五个生成文件全部 gitignore（根 `.gitignore:25-29`）——克隆后必须先跑 schema 生成才有类型。

### Playwright 拦截配对

`tests/e2e/ui.spec.ts`（1760 行）与 `tests/e2e/fixtures.ts` 的核心手法是**网络层 mock 整个 management 面**：`page.route('**/api/runtime', route => route.fulfill(...))` 出现在至少六处（`ui.spec.ts:241`、`279`、`766`、`893`、`1039` 及 fixtures 的 `mockGateway`，`fixtures.ts:389-390`），config 三件套同样拦（`fixtures.ts:433-442` 分别 mock `/api/config/effective` 与 `/api/config` 的 GET/POST 分支）。Playground 相关测试用例包括虚拟模型名透传（'LLM playground sends selected virtual model name'，`ui.spec.ts:1453`）与 CORS listener 等待重试（`ui.spec.ts:1395`、`1428`）。e2e 与 dev 的 base 差异（`vite.config.ts:6` 的 `mode === 'e2e' ? '/' : '/ui/'`）+ preview 锁 127.0.0.1（`vite.config.ts:37`）保证 Playwright `webServer` 拉起的 19100 端口是干净环境（`playwright.config.ts:16-18`）。

## 数据流

### Playground 一次带工具对话的完整 UI 流

以用户在 `/llm/playground`（路由锚 `main.tsx:130-134`）输入一句话、且勾选 MCP 工具为例，端到端链路是：

1. **状态准备**：`llmBaseUrl` 取自当前选中 endpoint 的 baseUrl（`Playground.tsx:152`）；消息列表与 `runSteps` 进度条 state 就位（`Playground.tsx:163`）。注意此处 baseUrl 是**数据面地址**，非 management API。
2. **加载 MCP 工具**（若启用且未加载）：`loadMcpTools` 走 `sendMcpJsonRpc` 初始化会话（调用点 `Playground.tsx:295`），失败即抛"没有可用工具"。
3. **首次对话**：`sendChatCompletion({ baseUrl: llmBaseUrl, model: requestModel, apiKey: selectedKeyValue, messages, tools })`（`Playground.tsx:368-374`）——浏览器直连网关 `/v1/chat/completions`，带虚拟 API key；`performance.now()` 差值记录首字延迟（`Playground.tsx:367`、`375`）。每步都同步推进 `runSteps` 四态进度条（准备→MCP 工具→发送→等待，`Playground.tsx:344-349`、`361-366`），由 `RunTimeline` 渲染（`Playground.tsx:706`）。
4. **工具循环**：`extractToolCalls` 解析响应（`Playground.tsx:382`）；有调用则把 assistant 消息入列，`executeToolCalls` 逐个 `sendMcpJsonRpc` 执行（`Playground.tsx:409-416`），tool 结果组装成 `role:'tool'` 消息（`Playground.tsx:417-425`）。
5. **二次对话收口**：`sendChatCompletion` 携带完整 `followUpMessages` 再调（`Playground.tsx:439-445`），最终 assistant 消息带 `meta`（模型/延迟/用量）入列（`Playground.tsx:458-471`）。

**勘误（按源码为准）**：任务书称"playgroundApi SSE 流式对话"，实测两处 `sendChatCompletion` 调用（`Playground.tsx:368`、`439`）**均未传 `stream` 参数**，而 API 侧 `stream: Boolean(args.stream)`（`playgroundApi.ts:24`）默认 false——**LLM 对话是非流式 JSON 请求/响应**（一次拿全文，靠 runSteps 进度条补偿体感）。真正的 SSE 消费只有两处：Logs 页 tail（`logsApi.ts:32-67`）与 MCP SSE 响应解析（`playgroundApi.ts:77-90`）。

### Logs 页的聚合查询链

`/llm/logs` 页同时跑三条查询链（`Logs.tsx:24` 一行 import 四个 API）：

- **搜索链**：`load` 回调 `searchLogs({ limit: 100, filters, includeAttributes: true })`（`Logs.tsx:151-155`），用自增 `loadSeq` 序号守卫过期响应（`Logs.tsx:146`、`156`——旧请求回来时序号不匹配直接丢弃）。
- **过滤器发现链**：独立 effect 调 `analyticsSummary({ groupBy: [], bucketCount: 1 })`（`Logs.tsx:175-179`）只为拿 `filterOptions`（provider/model 可选值），失败则退化为 models 配置目录兜底（`Logs.tsx:187-199`）。
- **tail 流链**：开启 stream 时 `AbortController` 包住 `for await (const event of streamLogs(...))`，每条 `event.entry` **前插**进列表并 `slice(0, 200)` 封顶（`Logs.tsx:210-214`），effect 清理函数 abort（`Logs.tsx:221`）；error 只在非主动 abort 时上屏（`Logs.tsx:217-218`）。

展开某条日志时 `getLog(logId)` 带 `includePayload: true`（`logsApi.ts:21`）懒拉请求/响应载荷，同样用 detailSeq 防竞态（`Logs.tsx:263-279`），180ms 延迟才显示 loading 骨架避免闪烁（`Logs.tsx:255-261`）。这条链把"列表-过滤-详情"三种时效需求分别交给一次性查询、低频聚合、持续 SSE 三种传输形态——是管理面数据消费分层的好范本。

## 设计决策

### @/ 别名与生成物类型的工程取舍

`vite.config.ts:19-24` 的 `resolve.alias` 把 `@` 钉到 `./src`（任务书"批 95 根因发现"确认：没有 tsconfig paths，别名唯一生效点就是这里），同时把 `path-browserify` 重定向到本地 ESM shim（`src/pathBrowserifyEsm.ts`，`vite.config.ts:23`）——因为 Monaco 依赖 Node 的 pathpolyfill，而 Vite 不自动 polyfill Node 内建模块。生成类型 `.d.ts` 进 `.gitignore`（`.gitignore:25-29`）意味着：**Rust schema 是唯一真相源，TS 类型是构建产物**——代价是克隆后需先跑 generate 脚本才有类型检查（新人最常踩的坑），收益是 config schema 改动（Rust 侧 serde 定义）自动传导到 UI 表单校验，永远不出现"文档说有这个字段但 UI 没跟上"的漂移。（此收益推断自构建链结构，源码无显式注释。）

### 15 路编辑器分派表 vs 每编辑器独立路由

PolicyDrawer 没有给每种 policy 开独立路由，而是单 Drawer 组件 + `customEditor` 字符串分派（`PolicyDrawer.tsx:228-346`）+ 无 customEditor 时落回 schema 驱动的 `GenericPolicyEditor`（`PolicyDrawer.tsx:203-215`）。这形成**三级编辑器形态**：零成本（Generic，纯 schema 渲染，apiKey/basicAuth 走此路）→ 标准定制（14 种专用编辑器）→ 目录页只需声明 `customEditor` 一词。对比独立路由方案：分派表让"从列表页点开抽屉"的交互统一（打开/保存/diff/删除全部复用 Drawer 的 footer 契约，`PolicyDrawer.tsx:130-151`），路由树不膨胀（`main.tsx` 全仓仅一个 `/llm/policies`）；代价是条件链 15 个分支的阅读成本与 `key={JSON.stringify(policy.value)}` 强制重挂载（`PolicyDrawer.tsx:155`）——源码注释"Raw mode ... raw edits reload the editor (key the body on value)"（`PolicyDrawer.tsx:353-355`）说明这是刻意的状态重置策略。

### SSE 用 async 生成器而非 EventSource

`streamLogs` 选 `async function*` + fetch POST（`logsApi.ts:32-67`）而非浏览器原生 `EventSource`，源码虽无注释，但从实现可推断（标注：推断）三点理由：一是 EventSource 只支持 GET，而 tail 需要携带复杂 filters 的 POST body（`logsApi.ts:39`）；二是生成器天然把"解析帧"封装在迭代器协议里，调用方 `for await` 拿到的直接是类型化 `TailEvent`，错误传播走生成器的 throw 语义；三是配合 AbortSignal 参数（`logsApi.ts:34`）实现干净的取消链路（`Logs.tsx:221` 的 cleanup abort）。半截 buffer 保留（`logsApi.ts:55`）处理了 chunk 边界切开 SSE 事件的边界情况。服务端 heartbeat 事件前端显式忽略（只处理 log/error 两类，`logsApi.ts:59-64`）——15 秒心跳只为保活 TCP，不是数据。

### base.ts 的认证重定向状态机

401 处理里的 `redirecting`/`hasSuccessfulRequest` 双布尔（`base.ts:3-4`）解决了 SPA 并发请求的整页跳转竞争：多个请求同时 401 时只放行第一个触发 reload（`base.ts:20-24` 的 pending Promise 永不 resolve，静默吸收其余请求）；首次请求即 401（会话从未建立）时宁可抛错也不跳登录页死循环（`base.ts:17-19`）。（双布尔的动机为推断，代码行为是实证。）

## 新人提示

**加一个页面的步骤**（以加 `/llm/widgets` 为例）：
1. `src/pages/Widgets.tsx` 写页面组件；
2. `main.tsx` 加 `widgetsRoute = createRoute({ getParentRoute: () => appRoute, path: '/llm/widgets', component: WidgetsPage })` 并塞进 `appRoute.addChildren([...])`（参照 `main.tsx:118-122` 的 costsRoute 三行 + 244-271 的组装点）；
3. 导航入口在 `components/Shell` 的侧边栏配置（本篇未展开，grep Shell 内的 nav 定义）；
4. 页面数据用现成 hook（`useEffectiveGatewayConfig` 等，`hooks.ts:66-73`），别直接 fetch——cookie/401 处理只在 `base.ts` 里有一份。

**生成 gateway-config 类型**：改了 Rust 侧 schema 后在 `ui/` 下重跑 `node scripts/generate-schema.mjs`（或查 `package.json` 里挂的 npm script）；没跑之前 IDE 会满屏红——因为 `src/gateway-config.d.ts` 在 `.gitignore:27` 里，克隆即缺失。日志观测类型不在此链：改 `LogEntry` 等直接编辑 `types.ts:120` 起的手写段，并同步后端 `log_store` 的 serde 定义。

**调试 e2e**：测试不连真网关，全走 `fixtures.ts` 的 `mockGateway`（`fixtures.ts:389` 起）拦截——你新页面若请求了新端点，必须先在 fixtures 补 route.fulfill，否则测试里请求会落到真实网络直接失败。跑单测：`npx playwright test tests/e2e/ui.spec.ts -g "playground"`；UI 侧调试用 `vite.config.ts:33` 的 19000 dev server（记得设 `VITE_AGENTGATEWAY_API` 指向真网关，否则同源请求 404）。

**坑**：
- `streamLogs` 是无限流，忘记 AbortController 就是内存泄漏（正确姿势见 `Logs.tsx:203-222` 的 effect 模式）；
- Playground 的 baseUrl 是数据面端口，dev 模式下 CORS 由网关侧 `cors` policy 控制（`ui.spec.ts:1395` 起的三个测试就是专门盯这个交互的）；`credentials: 'omit'`（`playgroundApi.ts:18`）是刻意的——数据面认证走 Bearer key，不能带 management 面的 session cookie；
- LLM 与 MCP 策略的"禁用"写法不同（`Policies.tsx:81-86` 置 null vs `:107-110` delete），混用会让 effective config diff 出现预期外的键；
- PolicyDrawer 的表单 id 由 schemaRoot+policyKey 清洗生成（`PolicyDrawer.tsx:77`、`392-394`），两个 Drawer 同屏时若 policyKey 相同会撞 id；
- 改路由后 `declare module '@tanstack/react-router'`（`main.tsx:275-279`）的类型推导偶发需要重启 TS server 才刷新。

（全部行号锚于写盘前经 sed/grep 从源码逐条核实；L15 层数与 688 节点数取自仓内 `.understand-anything/knowledge-graph.json` 实测。）
