# 07 · goose-server（goosed）：桌面端背后的 HTTP+SSE 后端

> 源码基线：本仓 `/usr-data/data2/repos/aaif-projects/repos/goose/crates/goose-server/`。所有行号锚均经 sed/grep 现场核实。文中"推断"标记处为无注释佐证的分析性结论。

## 一、角色定位：三种宿主共享一个 Agent 引擎，goosed 是"桌面专座"

在 16 层知识图谱中，goosed 落在第 7 层「goose-server 与 Rust SDK」（60 节点）：向下依赖第 1 层 Agent 会话引擎（`crates/goose/src/agents/`）与第 3 层 MCP 扩展子系统，向上被第 8 层桌面端主进程（`ui/desktop/src/goosed.ts`）当作子进程拉起。

goose 的同一个 `Agent` 引擎有三种宿主形态：**goosed**（HTTP+SSE，服务 Electron 桌面端）、**goose-cli**（终端交互，如 `crates/goose-cli/src/session/mod.rs:1263` 直接调 `self.agent.reply(...)`）、**ACP 宿主**（agent-client-protocol，`crates/goose/src/acp/server.rs:28` 引入同一个 `AgentManager`）。三者不重复实现引擎，只各自做"协议翻译"——把 `Agent::reply` 返回的事件流翻译成 HTTP/SSE、终端渲染或 ACP JSON-RPC。goosed 的二进制入口极薄：`main.rs:29-44` 定义 `Commands` 枚举只有三个子命令（`Agent`/`Mcp`/`ValidateExtensions`），`main.rs:84-85` 把 `agent` 子命令直接分派给 `commands::agent::run()`；`main.rs:87-94` 的 `mcp` 子命令则复用 goose-mcp 的 `serve()` 起四个内置 MCP server，不经过 axum。启动过程布满 `main.rs:46-48` 的 `GOOSED_BOOT:` eprintln 与 `main.rs:50-70` 的 panic hook（带 `Backtrace::force_capture`），都是给桌面端启动诊断（`startupDiagnostics.ts`）看的。

## 二、内部结构：启动链、路由全景与两代 SSE 实现

### 2.1 启动链（commands/agent.rs）

`commands/agent.rs:39` 的 `run()` 做七件事：①`agent.rs:44-45` 最先安装 rustls crypto provider（注释明言 ring 与 aws-lc-rs 同时被传递依赖启用，必须显式选一）；②`agent.rs:52-53` 从 `GOOSE_SERVER__SECRET_KEY` 取密钥，缺省则随机生成 32 字节 hex——**每次启动随机，意味着桌面端与 goosed 必须同生命周期**；③`agent.rs:56` 构造全局唯一 `AppState`；④`agent.rs:65-68` CORS 全开（`Any/Any/Any`，因为已有 X-Secret-Key 认证兜底）；⑤`agent.rs:70-81` 在同一进程内桥接 ACP 服务（注释 `TODO(acp-migration)` 说明这是迁移过渡：桌面端将改直连 `goose serve`，此处以 `GoosePlatform::GooseDesktop` 标识平台身份）；⑥`agent.rs:83-91` 把 REST 路由挂 `check_token` 中间件、ACP 路由挂 `check_acp_token`，merge 成单个 app；⑦`agent.rs:105-129` 或 `agent.rs:146-154` 二选一：TLS 分支走 `axum_server::bind_rustls`，非 TLS 分支走 `TcpListener` + graceful shutdown。默认配置在 `configuration.rs:74-84`：`127.0.0.1:3000` 且 **tls 默认 true**；环境变量用 `GOOSE_` 前缀 + `__` 嵌套分隔（`configuration.rs:38-41`），所以才有 `GOOSE_SERVER__SECRET_KEY` 这种拼法。

### 2.2 路由全景（routes/mod.rs:31-57）

`routes::configure()` 合并 19 个子路由模块（local-inference 为 feature 门控）。按职责分四类：

- **会话生命周期**：`routes/agent.rs:1364-1380` 注册 `/agent/start|resume|restart|stop`、工具直调 `/agent/tools|read_resource|call_tool`、扩展管理 `/agent/add_extension|remove_extension`；`routes/session.rs:616-641` 注册 `/sessions` 的 list/search/get/delete/export/import/fork/rename/insights 全家桶；`routes/schedule.rs` 是调度器 CRUD。
- **对话**：两代 reply 端点并存（见 2.3）。
- **配置**：`config_management.rs`（1801 行，本目录最大）管理 provider/秘钥/权限。
- **周边**：status/telemetry/tunnel/gateway/dictation/mcp 代理。`status.rs:16-18` 的 `/status` 只回一个 `"ok"` 字符串，是桌面端 `checkServerStatus` 的探活点。

认证中间件 `auth.rs:15-38`：`/status`、`/features`、`/mcp-ui-proxy`、`/mcp-app-proxy`、`/mcp-app-guest` 五条路径免认证（`auth.rs:20-27`），其余请求必须带 `X-Secret-Key` 头（`auth.rs:28-31`），比对用 subtle 的常数时间比较（`auth.rs:9-13`）防时序侧信道；ACP 路由额外接受 `?token=` query（`auth.rs:50-54`）以支持浏览器直连场景。

### 2.3 两代 SSE 实现（本文核心）

**第一代 `/reply`**（`reply.rs:461-468` 注册，`DefaultBodyLimit` 50MB）：`ChatRequest`（`reply.rs:79-90`）带 `session_id` + `user_message`，POST 的 HTTP 响应体本身就是 SSE 流——`SseResponse::into_response`（`reply.rs:112-124`）手工设 `text/event-stream`/`no-cache`/`keep-alive` 三头。handler 内 `reply.rs:243-245` 建 `mpsc::channel(100)` 与 `CancellationToken`，`reply.rs:253` spawn 后台任务：取 agent → 读 session → `reply.rs:313-334` 调 `agent.reply(user_message, session_config, cancel)` 拿到 `BoxStream<AgentEvent>`，然后在 `reply.rs:337-393` 的 `tokio::select!` 三臂循环里消费：取消臂、500ms 心跳臂（发 `MessageEvent::Ping`，`reply.rs:343-345`）、`timeout(500ms, stream.next())` 臂。`reply.rs:184-194` 的 `stream_event` 把事件序列化成 `data: {json}\n\n` 帧写 channel；发送失败即"client hung up"，立刻 `cancel_token.cancel()` 反向叫停 agent。流结束发 `Finish` 事件收尾（`reply.rs:448-457`）。**致命局限：事件只进这条 POST 响应，连接一断事件就丢，无法重连补发。**

**第二代 `/sessions/{id}/reply` + `/sessions/{id}/events`**（`session_events.rs:628-637` 注册）把"提交"与"订阅"拆开：POST reply 立即返回 `{"request_id": ...}` JSON（`session_events.rs:41-43`），所有事件改走常开的 GET SSE 流。基础设施是 `state.rs:138-144` 的 `get_or_create_event_bus`——每会话一个 `SessionEventBus`，挂在 `AppState.session_buses`（`state.rs:34`）。总线三件套：

1. **发布**（`session_event_bus.rs:50-64`）：在 buffer 锁内分配单调递增 `seq`（注释明言防止并发发布乱序），写入 512 容量环形重放缓冲（`session_event_bus.rs:8`）后 broadcast 给订阅者（容量 256，`session_event_bus.rs:7`）。
2. **订阅**（`session_event_bus.rs:82-111`）：先 `tx.subscribe()` 拿 live 接收器再快照 buffer（注释解释：保证锁内发布的事件必然出现在 rx 里，靠调用方用 `replay_max_seq` 去重）；客户端带 `Last-Event-ID` 则重放 `seq > last_id` 的部分；若 last_id 已被逐出缓冲，返回 `ClientTooFarBehind`（`session_event_bus.rs:99-101`）。
3. **单飞控制**（`session_event_bus.rs:128-140`）：`try_register_request` 原子地"清理已取消请求 + 检查空 + 注册新请求"，同一会话同时只允许一个在飞请求，冲突返回 "Session already has an active request"。

GET 流 handler（`session_events.rs:132-252`）先验证会话存在，`session_events.rs:144-147` 解析 `Last-Event-ID` 头，然后 spawn 推送循环，顺序极讲究：先发 `ActiveRequests`（`session_events.rs:177-192`，**不带 SSE id: 字段**，注释明言避免拉低客户端 Last-Event-ID 游标，且先于重放发出以便前端先注册 handler）；再逐条重放；再进入 live 循环，心跳用注释帧 `: ping N`（`session_events.rs:204-218`，注释说明 ping 不进重放缓冲、不污染 id 游标）；live 事件跳过 `seq <= replay_max_seq` 去重（`session_events.rs:225-227`）；broadcast `Lagged` 时主动断流逼客户端带 Last-Event-ID 重连补齐（`session_events.rs:237-241`）。帧格式 `id: {seq}\ndata: {json}\n\n`（`session_events.rs:87-89`），且 `session_events.rs:98-111` 在 JSON 里注入 `chat_request_id` 供前端按请求路由。POST 侧则要求客户端自生成 UUID（`session_events.rs:281-285` 校验，结构体注释明言 "Client-generated UUIDv7"）；elicitation 应答走短路通道不注册新请求（`session_events.rs:322-346`）；后台任务由 `RequestGuard` RAII 兜底清理（`session_events.rs:363-364`，Drop 实现在 `session_event_bus.rs:194-204`）；取消走 `/sessions/{id}/cancel`（`session_events.rs:613-624`）。

## 三、外部连接

**下游**：所有对话路由经 `state.rs:158-160` 的 `get_agent` → `AgentManager::get_or_create_agent`（`execution/manager.rs:114-116`）。AgentManager 是进程级单例（`manager.rs:63-93`），内部 LRU 缓存上限 100 个活跃 agent（`manager.rs:18`），慢路径用 per-session 创建锁防并发双建（`manager.rs:40-50` 注释点名 issue #9031：start_agent 的后台扩展加载与前端 resume_agent 竞争会向每个 MCP server 发两次 initialize）。`Agent::reply` 签名在 `agents/agent.rs:1406-1411`，返回 `BoxStream<Result<AgentEvent>>`；`AgentEvent` 仅三变体：`Message`/`McpNotification`/`HistoryReplaced`（`agent.rs:252-256`），被两个路由文件映射成 `MessageEvent` 八变体（`reply.rs:126-154`，含 `Error`/`Finish`/`UpdateConversation`/`ActiveRequests`/`Ping`）。会话持久化经 `state.rs:119-121` 的 `session_manager()`。**勘误（与任务书不符，按源码为准）**：`agent-session-id`/`agent-working-dir`（`session_context.rs:3-4`）**不是 goosed 的入站 HTTP 请求头**，而是 goose 核心 crate 里 (a) 注入 MCP `CallToolRequest._meta` 的字段（`mcp_client.rs:753-767`，让扩展知道调用来自哪个会话/工作目录）和 (b) 一个 task-local（`session_context.rs:6-8`）。goosed 入站请求头只认 `X-Secret-Key` 与 `Last-Event-ID`。

**上游（桌面端）**：`ui/desktop/src/goosed.ts` 主进程先 `findAvailablePort`（`goosed.ts:269`）随机选端口，`goosed.ts:123-134` 的 `buildGoosedEnv` 把 `GOOSE_PORT` 与 `GOOSE_SERVER__SECRET_KEY` 塞进子进程环境，`goosed.ts:290-315` 以 `spawn(goosedPath, ['agent'])` 拉起并固定连接 `https://127.0.0.1:${port}`（`goosed.ts:272`）。TLS 信任靠证书指纹钉扎：goosed 在 `tls.rs:82` 向 stdout 打印 `GOOSED_CERT_FINGERPRINT={sha256}`（自签证书生成于 `tls.rs:30-43`），桌面端 `goosed.ts:322-345` 解析后作为 pinned fingerprint。渲染进程侧，`useChatStream.ts:664` 用 `uuidv7()` 生成 requestId 并 `sessionReply()` POST（`useChatStream.ts:696-703`）；`useSessionEvents.ts:55-67` 的重连循环从 SSE `id:` 记录 `lastEventId` 并在重连时回发 `Last-Event-ID` 头，指数退避 500ms→10s（`useSessionEvents.ts:29-31`），收到的事件按 `chat_request_id ?? request_id` 路由到对应请求的 listener（`useSessionEvents.ts:82-88`；服务端注入点即 `session_events.rs:98-111`）。

**openapi 契约链**：路由 handler 上的 `#[utoipa::path]` 宏（如 `reply.rs:198-209`）+ `openapi.rs:388-442` 起的 `ApiDoc` paths 注册（reply 在 439、session_events 三端点在 440-442）→ `generate_schema()`（`openapi.rs:719-726`）→ `bin/generate_schema.rs:9-15` 把 JSON 写到 `ui/desktop/openapi.json` → `Justfile:167-172` 的 `generate-openapi` 再跑 `@hey-api/openapi-ts` 生成前端 `src/api/sdk.gen.ts`。**生成物严禁手改**（AGENTS.md 钉版），前端所有类型来自这条链。

## 四、数据流：桌面端发一条消息的全链路

1. 用户在聊天框回车 → 渲染进程 `useChatStream.ts:664` 生成 `requestId = uuidv7()`，注册 listener，`useChatStream.ts:696-703` `POST /sessions/{id}/reply`（body 含 request_id/user_message）。
2. `session_events.rs:273` handler 校验 UUID 与会话存在（`:281-292`），elicitation 检查（`:322-331`）后 `state.rs:138-144` 取/建事件总线，`session_event_bus.rs:128-140` `try_register_request` 占位（并发第二条消息被 400 拒绝）。
3. 立即返回 `{"request_id"}` JSON——**提交与推流解耦，POST 生命周期结束**。
4. `session_events.rs:363` spawn 的后台任务：`get_agent` 命中 LRU 或走创建锁慢路径（`manager.rs:121-176`）→ `session_events.rs:434-454` `agent.reply(...)` 进入引擎 reply-loop（planner→extend→reply，详见本系列 01 篇）。
5. 引擎每产出一个 `AgentEvent`，`:464-501` 映射为 `MessageEvent`（Message 附带 `get_token_state` 从 SessionManager 读的 token 用量，`reply.rs:156-177`）→ `bus.publish()` 分配 seq、入重放缓冲、broadcast。
6. 常开的 GET SSE 循环（`session_events.rs:208-249`）从 broadcast 收到事件，`serialize_session_event` 注入 `chat_request_id`，`id: {seq}\ndata: {...}\n\n` 帧写出。
7. 前端 `useSessionEvents.ts:71` 的 `for await` 消费，按 routingId 分发到 `useChatStream` 的 listener，增量渲染消息/工具调用；`Finish` 事件（`session_events.rs:584-591`）触发清理，`:593-594` 注销请求。
8. 任意时刻刷新/断网：重连时带 `Last-Event-ID`，`session_event_bus.rs:91-107` 重放缓冲补齐；断流期间在飞的请求由 `ActiveRequests` 事件（`:177-192`）告知前端重新挂 listener 实现续看。

## 五、设计决策

- **桌面端走 HTTP 子进程而非链接库**：推断——Electron 主进程是 Node 而非 Rust，进程边界不可避免；goosed 随机端口+随机密钥+自签证书钉扎（`agent.rs:52-53`、`tls.rs:82`、`goosed.ts:322-345`）把攻击面收窄到"本机知道密钥的父子进程对"，CORS 才敢全开。`goosed.ts:355-366` 的注释是罕见的文档级坑：长期挂着 stdout data 监听会因 V8 字符串转换崩溃主进程，指纹拿到后必须摘监听——跨语言进程边界连"读日志"都有内存语义代价。
- **SSE 而非 WebSocket**：推断+注释佐证——需求本质是**服务器单向推流 + HTTP 语义**（POST 提交、GET 订阅、断线重连补发）。SSE 免费获得三样东西：Last-Event-ID 自动重连语义（浏览器 EventSource 原生支持；本仓自实现于 `useSessionEvents.ts:55-67`）、纯 HTTP 可穿任何代理/中间件、与 axum 的 `Body::from_stream` 零额外依赖。代价是需要自己解决"双向"（取消走独立 POST `/cancel`，`session_events.rs:613-624`）。两代端点并存则是渐进迁移的活标本：第一代把事件绑死在 POST 响应上无法重连，第二代用"总线+重放缓冲+单调 seq"补齐 Exactly-once 语义，但 `/reply` 仍在路由表与 openapi 里（`reply.rs:461-468`、`openapi.rs:439`）。
- **seq 在锁内分配**（`session_event_bus.rs:46-49` 注释）：并发发布若在锁外取号会出现 seq=2 先于 seq=1 入缓冲，重放就乱序——用 buffer 锁串行化"取号+入队"是正确性关键，不是性能优化。
- **契约先行**：`#[utoipa::path]` 与 handler 同文件共生（如 `session_events.rs:119-131`），路由注册（`:628-637`）、openapi 注册（`openapi.rs:440-442`）、前端 SDK 三者由 `just generate-openapi` 单向生成，杜绝手写类型漂移；`check-openapi-schema.sh` 在 CI 里强制生成物与源码一致（`Justfile:164-165`）。
- **单飞请求**（`session_event_bus.rs:128-140`）：一个会话同一时刻只允许一个 agent reply-loop 在跑，避免了引擎侧会话状态（conversation 持久化）被并发写坏，把"取消旧的"显式化为客户端责任。

## 六、新人提示

1. **新增路由三步**（AGENTS.md 钉版）：①在 `routes/` 建文件实现 handler（加 `#[utoipa::path]` 宏与 `ToSchema` 类型）+ `routes()` 函数；②`routes/mod.rs` 声明模块并在 `configure()`（`mod.rs:31-57`）merge，同时在 `openapi.rs` 的 `ApiDoc` paths/components 注册；③跑 `just generate-openapi` 重新生成 `ui/desktop/openapi.json` 与前端 SDK——**绝不手改生成物**，CI 会拦。
2. **调试 SSE**：`curl -N -k https://127.0.0.1:<port>/sessions/<id>/events -H "X-Secret-Key: <key>"` 可裸看帧流；注意区分 `id:` 帧（真实事件，进重放缓冲）与 `: ping` 注释帧（心跳，`session_events.rs:214`）。查 goosed 日志先盯 `GOOSED_BOOT:` 前缀（`main.rs:46-48`）与 stderr 尾部（桌面端 `goosed.ts:368-381` 采集）。
3. **坑**：①本地起服务想走 http 必须显式 `GOOSE_TLS=false`，因为 `configuration.rs:82-84` 默认 true；②`ClientTooFarBehind`（断线超 512 事件）时服务端只发一条 Error 事件叫你整段重载（`session_events.rs:156-166`），前端不要试图续传；③改 `/reply` 老端点时注意它与新端点是**两份独立循环**（`reply.rs:337-393` vs `session_events.rs:456-524`），遥测、token_state 逻辑是复制的不是共享的，改一处要看另一处；④同会话并发第二条消息必 400（`session_events.rs:350-355`），测试脚本要串行发；⑤`mcp` 子命令与 `agent` 子命令共用二进制但完全不同路径（`main.rs:83-95`），排查"端口起不来"先确认跑的是 `goosed agent`。

---

### 附：本篇关键锚点速查

| 主题 | 锚 |
|---|---|
| 入口分派 | main.rs:29-44, main.rs:84-85 |
| 启动/TLS/密钥 | commands/agent.rs:39, agent.rs:52-53, agent.rs:126-129, tls.rs:82, configuration.rs:74-84 |
| 认证 | auth.rs:20-27, auth.rs:28-31, auth.rs:9-13 |
| 路由全景 | routes/mod.rs:31-57, routes/agent.rs:1364-1380, routes/session.rs:616-641 |
| 一代 SSE | reply.rs:79-90, reply.rs:112-124, reply.rs:243-245, reply.rs:313-334, reply.rs:337-393, reply.rs:448-457, reply.rs:461-468 |
| 事件总线 | session_event_bus.rs:7-8, session_event_bus.rs:50-64, session_event_bus.rs:82-111, session_event_bus.rs:128-140, session_event_bus.rs:194-204 |
| 二代 SSE | session_events.rs:87-89, session_events.rs:98-111, session_events.rs:144-149, session_events.rs:177-192, session_events.rs:204-218, session_events.rs:225-227, session_events.rs:237-241, session_events.rs:281-285, session_events.rs:322-346, session_events.rs:350-355, session_events.rs:363-364, session_events.rs:584-594, session_events.rs:613-637 |
| 引擎下游 | manager.rs:18, manager.rs:63-93, manager.rs:114-116, agents/agent.rs:252-256, agents/agent.rs:1406-1411 |
| 桌面上游 | goosed.ts:123-134, goosed.ts:269-272, goosed.ts:322-345, goosed.ts:355-366, useSessionEvents.ts:29-31, useSessionEvents.ts:55-67, useSessionEvents.ts:82-88, useChatStream.ts:664, useChatStream.ts:696-703 |
| openapi 链 | openapi.rs:388-442, openapi.rs:719-726, generate_schema.rs:9-15, Justfile:167-172 |
| 勘误 | session_context.rs:3-4, mcp_client.rs:753-767 |
