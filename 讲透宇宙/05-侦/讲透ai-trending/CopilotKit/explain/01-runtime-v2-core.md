# 01 · runtime v2 核心：从框架适配器到 agent 运行时内核

> 定位文件：`packages/runtime/src/v2/runtime/`（图谱「runtime v2 agent 运行时」层，58 节点）

## 一、角色定位（16 层架构中位置）

本目录是 16 层中**第 7 层「runtime v2 agent 运行时」**的主体：向上以兼容 shim 承接第 4 层「runtime v1 服务端」的历史包袱，向下经 AG-UI 协议（第 6 篇）驱动 react-core v2 聊天组件（第 9 层）。一句话定位：**把"一组 agent × 一个 HTTP 框架 × 一种执行模式"正交化**——Hono/Express/裸 fetch × SSE 内存跑/Intelligence 平台托管跑任意组合。

骨架是漏斗：外层框架适配器（endpoints/ 薄壳）→ 中层框架无关 fetch handler（core/fetch-handler.ts 唯一管线）→ 里层运行时对象（core/runtime.ts 持 agents 注册表与 runner 策略）。**从 runtime.ts 往外读**最顺。

## 二、内部结构（关键文件+行号锚拆解）

### 2.1 类体系：抽象基类 + 两模式子类 + 委托 shim

`core/runtime.ts`（442 行）的三层类结构是全目录的语义中心：

- **`BaseCopilotRuntime` 抽象类（runtime.ts:216-266）**：只做三件事——存配置（agents/transcriptionService/前后置中间件/三组 UI 中间件开关，runtime.ts:246-253）、接一个 `AgentRunner` 策略对象（runtime.ts:253）、在非生产环境挂 `DebugEventBus`（runtime.ts:255-257）。`intelligence` 与 `mode` 声明为 abstract（runtime.ts:230-231），强制子类表态。
- **`CopilotSseRuntime`（runtime.ts:268-278）**：SSE 模式，runner 缺省回退 `new InMemoryAgentRunner()`（runtime.ts:276）——进程内直跑 agent。
- **`CopilotIntelligenceRuntime`（runtime.ts:280-330）**：托管模式，构造时用 `options.intelligence.ɵgetRunnerWsUrl()` 拿平台 WebSocket 地址组装 `IntelligenceAgentRunner`（runtime.ts:300-305）；线程锁参数带静态上限钳制（`MAX_LOCK_TTL_SECONDS = 3_600`，runtime.ts:293；默认 20s/15s，runtime.ts:320-328）。
- **`CopilotRuntime` 兼容 shim（runtime.ts:344-442）**：老入口名保留，构造时按 `hasIntelligenceOptions`（runtime.ts:332-336，判 `"intelligence" in options`）二选一委托（runtime.ts:352-355），随后**17 个 getter 全部转发 delegate**（runtime.ts:357-441），Intelligence 专属字段（generateThreadNames/identifyUser/lock*）还要先过 `isIntelligenceRuntime` 类型守卫（runtime.ts:393-421）。典型的"门面不持状态"委托——改模式判定只动构造函数一处。

### 2.2 agents 注册表：静态记录 | Promise | 工厂函数

任务书说"agents registry（runtime.ts:111-128）"——源码实证该区间实为 `BaseCopilotRuntimeOptions` 接口的 agents 字段文档区（runtime.ts:114-131），真正的类型定义在上方：

- `AgentsFactory = (ctx: AgentFactoryContext) => MaybePromise<NonEmptyRecord<...>>`（runtime.ts:80-82），工厂上下文只有 `request` 一个字段（runtime.ts:71-74）；
- `AgentsConfig` 三态联合类型（runtime.ts:90-92）：静态 record / Promise / 工厂函数；
- `resolveAgents`（runtime.ts:99-112）：函数则必须有 request 否则抛错（runtime.ts:104-108），非函数直接 await。

工厂形态为**多租户**设计：每请求可按 header（如 x-tenant-id）现场产出 agent 实例（runtime.ts:125-128 JSDoc 示例原文）。`NonEmptyRecord` 约束空注册表在类型层即被拒。

### 2.3 endpoints：两种框架、两种路由模式、四个入口

endpoints/hono.ts（89 行）与 endpoints/express.ts（179 行）两大主适配器共同点惊人：**都不自己处理路由，只做协议转换**。

- Hono 侧：`createCopilotHonoHandler`（hono.ts:55）内部构造框架无关 handler（hono.ts:62-68）后一行完成挂载——`app.basePath(basePath).all("*", async (c) => handler(c.req.raw))`（hono.ts:72）。**hono.ts:53 的 `createCopilotEndpoint = createCopilotHonoHandler` 是 @deprecated 别名**。CORS 配置经 toFetchCorsConfig（hono.ts:78-89）把 Hono 函数形态 origin 转成 fetch 形态。
- Express 侧：`createCopilotExpressHandler`（express.ts:91）显式传 `cors: false` 并注释 "CORS is handled at the Express middleware layer"（express.ts:104）——CORS 划给 Express 原生 cors() 中间件（express.ts:125-143，默认 `origin:"*"` 全开）。老别名 createCopilotEndpointExpress 同样 @deprecated（express.ts:88-89）。挂载三分支：single-route 单 POST（express.ts:147-148）、basePath 为 `/` 时 `router.all(/.*)`（express.ts:150）、常规路径转义正则（express.ts:152-155）。
- 桥接：Express 是 Node 回调风格，须经 `createExpressNodeHandler`（express.ts:108，实现在 express-fetch-bridge.ts）翻译 req/res ↔ fetch Request/Response。
- **single-route 模式**：`hono-single.ts:27` 的 `createCopilotEndpointSingleRoute` 已整体 @deprecated（推荐 `createCopilotHonoHandler` + `mode: "single-route"`）。信封格式 `{ method, params, body }` 由 `parseMethodCall`（single-route-helpers.ts:24）解析，METHOD_NAMES 白名单只有 5 个（single-route-helpers.ts:1-7）——run/connect/stop + info + transcribe，**线程类操作不进白名单**。

### 2.4 fetch-router：无 basePath 时的后缀匹配路由器

`matchRoute`（fetch-router.ts:20-51）双策略：给 basePath 就严格剥前缀（含"/api/copilotkit-x"误匹配防护，fetch-router.ts:40-41），不给就**后缀扫描整条路径**（fetch-router.ts:45-48）。matchSegments（fetch-router.ts:61-208）从尾部逐段试模式：/info、/transcribe、/agent/:id/run|connect|stop/:threadId、/threads/* 全家族。两个细节：cpk-debug-events 用 `cpk-` 前缀防与用户 agent 撞名（fetch-router.ts:77-83）；/threads/:threadId 与 subscribe/clear 的歧义靠排除法、最终 HTTP method 消歧（fetch-router.ts:184-195）。

### 2.5 请求管线：fetch-handler 的九步流水线

`core/fetch-handler.ts`（495 行）的 `createCopilotRuntimeHandler`（fetch-handler.ts:117）返回纯 `(Request) => Promise<Response>`（fetch-handler.ts:109-111），文件头注释明示可直连 Bun/Deno/Cloudflare Workers/Next App Router（fetch-handler.ts:18-26）。主管线九步（行号实证）：① CORS 预检（fetch-handler.ts:139）→ ② onRequest 钩子（:144）→ ③ legacy beforeRequestMiddleware，可改写 Request（:148-166）→ ④ 路由匹配：single-route 走 `resolveSingleRoute`（:171），multi-route 走 `matchRoute`（:192）→ ⑤ onBeforeHandler 钩子 → ⑥ `dispatchRoute` 分发（:189/:215，本体在 :296）→ ⑦ onResponse 钩子（:219）→ ⑧ 补 CORS 头（:228）→ ⑨ afterRequestMiddleware **非阻塞**执行，且传入 `response.clone()`（:233-235）——克隆是因为中间件要读 SSE body，不克隆会把发给客户端的流消费掉。

### 2.6 legacy 中间件：文档与实现的落差

`core/middleware.ts`（115 行）文件头注释宣称中间件"可以是回调函数**或 webhook URL**"（middleware.ts:4-8），但类型定义只有函数形态（middleware.ts:52-53），实现里非函数直接 `logger.warn` 跳过（middleware.ts:81-86、:114）。**webhook 协议是规划中/已删的路径**——枚举 `WebhookStage`（middleware.ts:63-66）保留了 before_request/after_request 两阶段命名，但无消费者。afterRequest 的增值服务是 `parseSSEResponse`（middleware.ts:101）从 SSE 流重建 messages/threadId/runId 再交给回调（middleware.ts:104-111）。

### 2.7 Open Generative UI 中间件：clarinet SAX 流式 JSON

`open-generative-ui-middleware.ts`（373 行）是最精巧的一块。背景：LLM 流式吐 `generateSandboxedUi` 工具调用的 JSON 参数（html/css/js 一大坨），等完整 JSON 再渲染会白屏数秒。解法：

- `ArgsParser`（:39-233）内嵌 **clarinet SAX 解析器**（import :13，实例化 :58），逐 token 消费参数流：顶层 key 出现即记 currentKey（:68-73），`html` 键进入流式模式（:144-150），每次 write() 后**直接读 clarinet 内部缓冲 `(this.parser as any).textNode`**（:156-163）把增量 html 切片提前发出；解析出错不清局，`parser.error=null; parser.resume()` 续命（:128-136）。
- 每完成一个参数就发 AG-UI `ACTIVITY_DELTA` 事件，patch 是标准 JSON Patch `add` 操作、数组追加用 `/-` 路径（:214-232）；首个参数（initialHeight）触发一次 `ACTIVITY_SNAPSHOT`（:201-212）。
- `OpenGenerativeUIMiddleware extends Middleware`（@ag-ui/client 的中间件基类，:242），在 RxJS 流上做**事件扣留**：genui 工具的 TOOL_CALL_START/ARGS/END 全部先扣住（heldToolCallEvents，:255、:285-313），等第一个 activity 事件发出后再 flush（:258-268）——保证前端先看到占位 UI 再看到工具调用事件，避免"工具卡先闪后变 UI"的观感错乱；RUN_FINISHED 也扣到最后（:279-282），确保 activity 流不被提前关闭；error/complete 分支都有兜底 flush（:340-367）。

### 2.8 Intelligence 平台客户端与 runner 策略

`intelligence-platform/client.ts`（923 行）的 `CopilotKitIntelligence` 类（client.ts:346）是托管模式的 API 门面：线程 CRUD（listThreads/updateThread/getThreadMessages 等，client.ts:526-786）、分布式线程锁（ɵacquireThreadLock/ɵrenewThreadLock/ɵcleanupThreadLock，client.ts:821-865）。一批 **ɵ 前缀方法**（client.ts:436-458：ɵgetApiUrl/ɵgetRunnerWsUrl/ɵgetClientWsUrl/ɵgetRunnerAuthToken…）是 Angular 风格的"内部 API"标记，专供 runtime 内部取配置（runtime.ts:301-302 就在消费）。runner URL 推导规则在 client.ts:901-915：传 `/runner` 或 `/client` 结尾则改写，否则追加 `/runner`。

runner 侧是标准策略模式：抽象基类 `AgentRunner` 四个抽象方法 run/connect/isRunning/stop（agent-runner.ts:30-34），`InMemoryAgentRunner`（in-memory.ts:81）与 `IntelligenceAgentRunner`（intelligence.ts）两个实现。线程类 handler 有"双后端策略"：isIntelligenceRuntime 走平台 REST，`instanceof InMemoryAgentRunner` 走本地 GLOBAL_STORE——本地开发不开 Intelligence 也有完整线程 API（handlers/intelligence/threads.ts，NOTES-DIGEST batch-11 条目实证）。

## 三、外部连接（imports 边上下游）

- **上游（谁调 v2）**：examples 与 skills 文档层的最小部署单元 `new CopilotRuntime({agents:{...}}) + createCopilotExpressHandler/HonoHandler`；endpoints/node.ts:28 提供 Node http 监听器形态。
- **下游（v2 调谁）**：`@ag-ui/client`（AbstractAgent/Middleware/事件枚举，runtime.ts:17）——agent 生态统一契约；`@ag-ui/mcp-apps-middleware` 与 `@ag-ui/a2ui-middleware`（runtime.ts:18-19）可组合中间件；`@copilotkit/license-verifier`（runtime.ts:9）特性门禁；`@copilotkit/shared` 提供 RuntimeMode 与 logger；clarinet/rxjs/hono/express/cors 为运行时依赖。
- **同层邻居**：handlers/（handle-run 等 9 个分发目标，fetch-handler.ts:44-61 导入）、runner/、transcription-service/、telemetry/。本层最大入度是 core/runtime.ts——endpoints/handlers/runner 都 depends_on 其 CopilotRuntimeLike 接口（runtime.ts:183-199）。

## 四、数据流（一条请求的旅程）

以 Express + SSE 模式跑 `POST /api/copilotkit/agent/support/run` 为例：

1. Express 收请求 → createExpressNodeHandler 把 (req,res) 翻译成 fetch Request（express.ts:108）；
2. fetch-handler 九步管线：CORS 预检放行 → onRequest → beforeRequestMiddleware（可改写 Request）→ matchRoute 命中 `{method:"agent/run", agentId:"support"}`（fetch-router.ts:88-97）→ dispatchRoute 进 handle-run；
3. handle-run 从 runtime.agents resolveAgents（工厂现场调用，runtime.ts:99-112）取 support agent，套上配置的中间件链（a2ui/mcpApps/openGenerativeUI 自动包装）；
4. InMemoryAgentRunner.run 进程内执行，产出 AG-UI 事件 Observable：TEXT_MESSAGE_CONTENT 增量直通；LLM 调 generateSandboxedUi 时 clarinet 逐 chunk 解析、参数边到边发 ACTIVITY_DELTA（open-generative-ui-middleware.ts:214-232）；
5. 事件流序列化为 SSE Response → Express 桥翻译回 res.write；
6. 返回前 response.clone() 交给 afterRequestMiddleware 异步消费（fetch-handler.ts:233-235，parseSSEResponse 重建 messages），主响应不受影响；
7. 前端 AG-UI client（第 6 篇）回放事件流进 thread store（第 2 篇），UI 逐帧更新。

## 五、设计决策（为什么这么设计 + 替代方案）

- **fetch-native 单管线 vs 每框架一套 handler**：v1 时代各框架 adapter 行为渐行分叉；v2 把全部逻辑压进 `(Request)=>Promise<Response>`，框架层只剩翻译——新增 Bun/Deno/Workers 零成本（fetch-handler.ts:18-26 注释即设计宣言）。代价是 Express 桥要处理流式 res 写回与错误传播边角。
- **两模式子类 + 委托 shim vs 泛型单类**：SSE 与 Intelligence 差异远不止一个开关（runner/锁/identifyUser/thread 命名全不同），单类会塞满 `if (intelligence)`；判别联合 options（runtime.ts:179-181）+ 两子类 + 顶层 shim，旧代码零改动拿到新实现。直接删 CopilotRuntime 类名会破坏海量 examples；shim 的 17 个 getter（runtime.ts:357-441）是刻意手写样板而非 Proxy——类型完整且可 grep。
- **agents 工厂 vs 静态注册表**：静态表在多租户 SaaS 会跨租户共享 agent 实例（状态泄漏）；工厂每请求现做，代价是 agent 状态不存活于请求间——这正是 Intelligence 模式用平台侧持久线程补的位置。
- **clarinet SAX vs 等完整 JSON**：后者只需 `JSON.parse` 但首字节延迟=全参数到齐；SAX+JSON Patch 增量推送把白屏时间压到第一个参数片段。读 `textNode` 私有缓冲（open-generative-ui-middleware.ts:158）是 hack，换来不维护部分字符串状态机——clarinet 升级是脆弱点。
- **扣留-再-释放 vs 透传**：透传会让前端先渲染工具卡再被 activity 替换（闪烁）；扣住 TOOL_CALL_START 到第一个 activity 事件（open-generative-ui-middleware.ts:284-298）用一次乱序换稳定 UI 语义；RUN_FINISHED 扣留（:279-282）防 activity 流被提前关流。

## 六、新人提示（坑+勘误+延伸阅读）

- **勘误 1（任务书对照）**：任务书写"agents registry（runtime.ts:111-128）"，源码该区间是 BaseCopilotRuntimeOptions 文档区；注册表本体是 AgentsConfig（runtime.ts:90-92）+ resolveAgents（runtime.ts:99-112）。语义对，行号锚需校正。
- **勘误 2（文档 vs 实现）**：middleware.ts 头注释仍宣称支持 webhook URL 中间件（middleware.ts:5-8），类型与实现均只收函数（middleware.ts:52、:81-86）——**按注释接 webhook 会静默跳过**（只有 warn 日志）。WebhookStage 枚举是死代码活化石。
- **CORS 双轨制**：Hono 把 cors 配置传进 fetch 管线（hono.ts:66），Express 强制 `cors:false` 自己挂 cors()（express.ts:104）——Express 侧改 fetch-handler 的 cors 参数不生效，要在 `createCopilotExpressHandler({cors})` 层给。
- **single-route 白名单陷阱**：线程操作只在 multi-route 暴露，single-route 的 METHOD_NAMES 只有 5 项（single-route-helpers.ts:1-7）；信封必须 `content-type: application/json` 否则 415（single-route-helpers.ts:26-30）。
- **DebugEventBus 只在非生产环境存在**（runtime.ts:255-257）：生产排障别指望 cpk-debug-events 路由（handler 生产返回 404，fetch-router.ts:83 注释）。
- **license token 双路径**：Intelligence 构造器手动做 `options.licenseToken ?? env` 回退（runtime.ts:314-315），注释明说是为让 telemetry 归因与特性门禁一致（runtime.ts:310-313）——像重复逻辑，删掉出隐性 bug。
- 延伸阅读：handlers/ 与 runner/（本层内）；第 2 篇（core 状态引擎）；第 6 篇（AG-UI 协议）；skills/runtime 文档镜像（安装/端点速查）。
