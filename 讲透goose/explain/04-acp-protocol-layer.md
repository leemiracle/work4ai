# 04 · acp/：ACP 协议层——goose 双角色接入协议

> 锚点口径：`crates/goose/src/acp/` 下文件全部以 `acp/` 缩写引用（如 `server.rs:1004` 即 `crates/goose/src/acp/server.rs` 第 1004 行）；跨仓文件写全路径。全部行号经 sed/grep 从源码核实（2026-10-23，本地仓快照）。

## 角色定位：16 层架构中的第 4 层，一体两面的协议角色

知识图谱把 goose 切成 16 层，ACP 协议层是第 4 层（33 节点），图谱摘要描述它是"Agent Client Protocol 服务端：crates/goose/src/acp 29 文件实现 new_session 等会话桥接与 goosed 协议适配，配 goose-acp-macros 过程宏与 acp-schema.json/acp-meta.json 协议描述；桌面端 Electron 经 ACP client 与 goosed 通信"，且"重度依赖核心会话引擎（26 边）与配置/安全层（21 边）"。位置关系：向上承接第 6/7/8 层的 CLI、goosed、桌面端主进程三个入口，向下压在第 1 层 Agent 会话引擎（`agent.rs` 的 reply）和第 5 层配置·安全层之上。

这一层最独特的设计是**双角色**。同一套 `acp/` 目录里同时住着协议的两端：

- **Server 角色（`server.rs` 的 `GooseAcpAgent`）**：goose 作为 agent 后端，被 Zed 等编辑器或自家桌面端驱动。连接入口有三个——CLI 的 `goose acp` 子命令走 stdio（`crates/goose-cli/src/cli.rs:2099` 分发到 `goose::acp::server::run`）；goosed 把 ACP 路由挂进 axum（`crates/goose-server/src/commands/agent.rs:86` 的 `create_acp_router`）；`run()` 本身就是 stdin/stdout 双流（`server.rs:2927-2928`）。
- **Client 角色（`provider.rs` 的 `AcpProvider`）**：goose 作为 ACP client 去连一个外部 ACP agent 子进程，把它包装成 goose 内部的一个 Provider。子进程拉起逻辑在 `provider.rs:975` 的 `spawn_acp_process`，而 spawn 出来的既可以是第三方 agent，也可以是另一个 goose——goose 套 goose 的"套娃"模式正是靠这一侧成立。

一句话概括：server 侧让**别人驱动 goose**，provider 侧让 **goose 驱动别人**，两侧共用 `agent_client_protocol` crate 的类型与连接原语。

## 内部结构：状态机、会话表与过程宏路由

**核心状态在 `GooseAcpAgent`（`server.rs:203-220`）**。它持有 17 个字段，可分四组：会话表 `sessions: Arc<Mutex<HashMap<String, GooseAcpSession>>>`（204 行）；执行底座 `agent_manager` / `session_manager` / `permission_manager` / `provider_inventory`；六组 `OnceCell` 客户端能力缓存（208-213 行，`client_fs_capabilities`、`client_terminal`、`client_mcp_host_info`、`client_supports_goose_custom_notifications`、`use_login_shell_path`、`client_cx`）——set-once 语义天然保证了 initialize 只生效一次；以及构造注入的 `provider_factory` 与 `builtins`。构造函数 `new()` 在 `server.rs:1004-1043`，会顺手 tokio::spawn 一个 SQLite 连接池预热任务（1009-1011 行）。

**每个活跃会话是一份 `GooseAcpSession`（`server.rs:163-179`）**，除了 `agent: Arc<Agent>` 和 `cancel_token`，其余四个字段全部服务于**工具链摘要**机制：`tool_requests` 缓存请求、`chain_membership` 记录每个 tool_call_id 属于哪条链（`ToolChain` 定义在 185-191 行，"Always len() >= 2"）、`responded_tool_ids` 与 `summarized_chains` 做幂等闸。152-162 行有一段值得先读的术语注释：ACP 的 "session"（人类视角的对话）与 goose 内部 `sessions` 表的 "Session"（LLM 工作状态）是两个概念，**ACP session ID 直接映射到 sessions 表的一行**——这是理解本层会话桥接的钥匙。

**消息分发是三层漏斗（`server/dispatch.rs`）**。`GooseAcpHandler`（`server.rs:2897`）实现 `HandleDispatchFrom<Client>`（`dispatch.rs:4`），用 `MatchDispatchFrom` 链式匹配：标准 ACP 请求（initialize/new_session/load_session/prompt/cancel/set_config_option/set_mode/set_model/list_sessions/close_session/fork_session）逐个 `.if_request` 挂上，最后 `.otherwise()`（`dispatch.rs:390-416`）把所有未知方法兜底转给 `dispatch_custom_request`——自定义方法的入口就在这条兜底路径上。两个细节：17-19 行注释说明整条链生成约 85KB 的异步状态机，必须 `Box::pin` 挪到堆上防止 tokio worker 栈溢出；26-28 行注释强调 **InitializeRequest 必须内联执行**，因为它设置连接级状态，不能让流水线化的 NewSessionRequest 抢跑。每个会话级请求都用 `cx.spawn` 派生并发（如 43-51 行的 NewSessionRequest）。

**server.rs 已经膨胀到 3785 行，所以按领域拆成 14 个子模块**（`server.rs:86-99` 声明）：`new_session`（4 行入口 `handle_new_session`，见 `server/new_session.rs:13`）、`custom_dispatch`、`extensions`（790 行，扩展增删查）、`providers`（959 行，provider 目录与配置）、`onboarding`（707 行）、`dictation`（467 行，语音听写七连方法）、`load_session`/`fork_session`/`manage_sessions` 等。

**自定义方法靠过程宏消灭样板（`crates/goose-acp-macros/src/lib.rs`）**。`#[custom_methods]` 标在 impl 块上（`server/custom_dispatch.rs:4`），块内 59 个 `#[custom_method(RequestType)]` 注解（grep 实测 59 处）。宏做的事：遍历 impl 项，剥离注解并抽出请求类型（lib.rs:48-80）；为每个方法生成一条 `<ReqType as JsonRpcMessage>::matches_method(method)` 路由臂（92-110 行）——**方法名字符串在编译期从请求类型上提取，杜绝 struct 定义与 handler 两处写 method 名的漂移**（这是宏文档 8-12 行的明示设计目标）；最后把生成的 `handle_custom_request` 分发器（184-193 行）和 `custom_method_schemas`（196-202 行）追加进 impl。`custom_dispatch.rs:6` 的 `dispatch_custom_request` 只是转调宏生成的 `handle_custom_request`。唯一例外是 `ElicitationRespondRequest`：316-323 行显式返回错误，因为它必须由连接级 dispatcher 处理而非会话级。

## 外部连接：reply 引擎、ExtensionManager 与 schema 生成链

**与 agent.rs reply 引擎的衔接是单点直连**。`on_prompt`（`server.rs:2366`）拿到会话 agent 后，在 2415 行调用 `agent.reply(user_message, session_config, Some(cancel_token.clone()))`，然后 2435 行 `while let Some(event) = stream.next().await` 消费 `AgentEvent::Message` 流。也就是说 ACP 层**不含任何 LLM 循环逻辑**，它只是把 reply 引擎的事件流翻译成 ACP notification：文本→`AgentMessageChunk`（1405-1411 行）、思考→`AgentThoughtChunk`（1436-1445 行）、工具请求→`ToolCall`（1515 行）、权限→RequestPermission 反向请求。反向亦然——provider 侧的 `AcpProvider` 实现了 `Provider` trait（`provider.rs:376`），`stream()` 在 434 行把 ACP 会话的 update 流翻译回 goose 的 `MessageStream`，两侧互为镜像。

**与 ExtensionManager 的衔接走两条路**。正路是自定义方法：`_goose/unstable/session/extensions/add`（`server/extensions.rs:7-23` 的 `on_add_extension`）反序列化出 `ExtensionConfig` 后调 `agent.add_extension()`；工具调用走 `server/tools.rs:21` 的 `on_call_tool`，内部经 `extension_manager`（57 行）转发。侧路是 **developer 扩展劫持**：`server.rs:1145-1202` 的 `apply_acp_extension_overrides` 在客户端声明了 fs/terminal 能力时，用 `AcpTools`（`acp/fs.rs`）作为 `McpClientTrait` 实现替换掉 developer 扩展的本地实现，让文件读写和终端操作**穿透到编辑器侧执行**——这是 ACP 协议"客户端能力借用"的核心机关。

**Provider 工厂注入**：`server_factory.rs:37-49` 的 `create_agent` 组装一个 `AcpProviderFactory` 闭包（类型定义在 `server.rs:101-110`），把 LLM provider 创建委派回 `crate::providers::create`。这层间接让 ACP 层不必依赖 providers 子系统的构造细节。

**59 个自定义方法的构成（任务书口径修正）**：`crates/goose-sdk-types/src/custom_requests.rs`（1429 行）共 59 个 `#[request]` 注解类型，其中 **58 个走 `_goose/unstable/*` 命名空间**（如 27 行的 `_goose/unstable/session/extensions/add`、80 行的 `_goose/unstable/tools/call`、130 行的 `_goose/unstable/session/system-prompt/set`），**1 个是标准方法 `session/delete`**（145 行）——与 `custom_dispatch.rs` 的 59 个 `#[custom_method]` 一一对应。任务书写"59 个 _goose/unstable/* 方法"，按源码应为"59 个自定义方法，其中 58 个在 unstable 命名空间"。另有 1 个自定义通知 `_goose/unstable/session/update`（`custom_notifications.rs:9`），用于 usage/status 等桌面端专属回推。

**schema 生成链（生成物勿手改）**：`custom_requests.rs` 的类型注解（单一事实源）→ 过程宏在编译期产出 `custom_method_schemas()`（含 params/response 的 JSON Schema）→ 二进制 `generate-acp-schema`（`crates/goose/Cargo.toml:275-276` 注册，源码 `crates/goose/src/bin/generate_acp_schema.rs`）在 main 里调用两个 schema 函数（11-13 行）→ 落盘 `crates/goose/acp-schema.json`（241-242 行）与 `acp-meta.json`（279-280 行）供 TS 代码生成消费。

## 数据流：一次 ACP 会话的双角色全链路

**Server 角色（被 Zed 连接）**：

1. **initialize**（`dispatch.rs:29-35` 内联执行）→ `on_initialize`（`server.rs:2226-2269`）：把客户端 fs/terminal/MCP host 能力写进 OnceCell（2232-2247 行），返回 `AgentCapabilities`——load_session、会话 list/close、prompt 支持 image 与 embedded_context、MCP http（2249-2262 行），外加一条 auth_methods 提示跑 `goose configure`（2265-2268 行）。
2. **new_session**（`server/new_session.rs:13-111`）：校验绝对 cwd（20 行）；按 meta 里有无 `client` 字段区分 `SessionType::User` 与 `Acp`（22-25 行，即桌面端与外部编辑器之别）；meta 可指定 provider（27-35 行），否则落全局默认；调 `session_manager.create_session` 建库行（38-47 行），再 `activate_acp_session`（`server.rs:1306`）把 agent 激活进会话表；最后返回带 modes/models/config_options 的响应（87-93 行）并补发 setup notifications（99-103 行）。
3. **prompt**（`server.rs:2366`）：建 `CancellationToken`（2376 行）挂到会话上；先解析斜杠命令找 recipe 并提前通知（2384-2406 行）；2415 行进 reply 引擎，2435 行起循环翻译事件。多工具链在这里被 `chain_buffer` 缓冲追踪（2433 行定义，2469-2492 行：ToolRequest 入缓冲、ToolResponse 中性、文本/思考清空），链收齐后触发一次 LLM 汇总（`maybe_summarize_chain`，`server.rs:1727`）。工具请求还会 spawn 一个用 `complete_fast` 生成 3-8 词小写短语的标题任务（1551-1560 行），失败重试一次、再失败落确定性 fallback 且**不持久化**（1634-1636 行注释明示只持久化 LLM 标题）。收尾时若客户端支持，回推自定义 usage 通知，同时保留标准通知做向后兼容——2537-2539 行注释直说"Remove once all known clients have migrated"。
4. **工具审批**：reply 引擎产出 `ActionRequired::ToolConfirmation` → `handle_message_content`（`server.rs:1392`）1446-1461 行捕获 → `handle_tool_permission_request`（1918 行）构造 pending 状态的 ToolCallUpdate 和四个选项 AllowAlways/AllowOnce/RejectOnce/RejectAlways（1954-1959 行）→ 1964 行 `cx.send_request(permission_request)` **反向请求客户端** → 回调里把结果转成 `PermissionConfirmation` 交给 `agent.handle_confirmation`（1969-1973 行）；客户端不应答则一律按 Cancel 处理（1976-1987 行）。
5. **cancel**（`server.rs:2567-2586`）：通知触发，直接 `token.cancel()`，prompt 循环在 2436-2439 行检测到后置 `was_cancelled` 退出。

**Client 角色（goose 套外部 ACP agent）**：`AcpProvider::connect`（`provider.rs:178`）→ `start`（218 行）先在**独立 OS 线程里建 current_thread runtime**（`spawn_client_loop`，167-175 行；81-82 行注释解释 tokio I/O 句柄不能跨 runtime）；`spawn_acp_process`（975-993 行）以 piped stdio + `kill_on_drop(true)` 拉起子进程；`handle_requests`（1001 行）发 `InitializeRequest`（1012-1018 行），按能力过滤要转发的 mcp_servers 后发 `NewSessionRequest`（1041-1048 行）——**会话在 connect 阶段就急切建立**（251-253 行注释）。此后所有交互经 `ClientRequest` 枚举（59-79 行：NewSession/SetMode/SetConfigOption/Prompt）走 mpsc 通道进这个线程，回来的事件统一为 `AcpUpdate` 枚举（92-114 行：Text/Thought/ToolCallStart/ToolCallComplete/PermissionRequest/Complete/Error），`stream()` 在 479 行消费并转成 goose MessageStream。子 agent 发起的权限请求从 `AcpUpdate::PermissionRequest`（108-111 行）浮出，由 `handle_permission_confirmation`（421-432 行）把 goose 侧的审批结果沿 oneshot 送回。两个哨兵值得记：模型名 `ACP_CURRENT_MODEL = "current"`（45 行）在会话建立后才解析成真实模型名（256-263 行）；`manages_own_context() = true`（417-419 行）告诉 reply 引擎上下文管理权在子 agent，`permission_routing() = ActionRequired`（413-415 行）则把审批改走 ActionRequired 通道而非传统 confirmation。

## 设计决策：命名空间、生成式 schema 与双传输

- **`_goose/unstable` 命名空间**：ACP 规范保留标准方法名（`initialize`/`session/prompt` 等），goose 的扩展若不加前缀迟早撞名。`unstable` 后缀则是诚实的迁移信号——schema 生成器专门给"只被 unstable 方法引用的类型"加 `_unstable` 后缀并重写 `$ref`（`generate_acp_schema.rs:40-49、290-318`），TS 侧因此能按稳定度区分生成物；标准/自定义通知并行下发（`server.rs:2533-2539`）同样是给客户端留迁移期。
- **schema 生成而非手写**：宏文档（lib.rs:8-12 行）说得直白——方法名编译期从请求类型提取，"eliminating duplication between the request struct and the handler"。生成器还要做三层 TS 代码生成适配：`true`→`{}` 与剥掉整型 format（66-75 行注释：@hey-api/openapi-ts 的 Zod 插件会静默丢 bare true 属性、int64 format 会生成 BigInt）、给 McpServerHttp/Sse 手工补 type 判别字段（321-324 行）、按"类型被几个方法共享"决定是否打 `x-method` 标（79-91 行）。手写 schema 几乎不可能维持这层一致性。
- **双传输的分工**（源码无总述注释，分工本身是实证，动机为推断）：stdio（`server.rs:2924-2941` 的 `run`）面向 CLI 与 Zed 这类"编辑器拉起子进程"的场景，零网络开销；HTTP/SSE/WebSocket 三形态挂在同一 `/acp` 路由上（`transport/mod.rs:117-128`：POST 收 JSON-RPC、GET 视 Upgrade 头分流 WebSocket 或 SSE 流、DELETE 断连），面向桌面端与 goosed 同进程/跨进程常驻。`transport/connection.rs:1-4` 的模块注释点明扇出模型：server→client 消息按"连接级流 + 每会话流 + 全量流"三路分发，WebSocket 吃全量流，SSE 吃连接级或会话级流；订阅前到达的消息进 1024 容量的 pre-subscribe 缓冲（21-22 行）防丢。会话级方法强制要求 `Acp-Session-Id` 头（mod.rs:70-80 行的白名单：prompt/cancel/load/set_mode/set_model）。
- **Initialize 内联、其余 spawn**：dispatch.rs 26-28 行注释给出理由——连接级状态必须先于一切会话请求就位。
- **85KB 状态机上堆**：dispatch.rs 17-19 行，罕见的把"生成物体积"写进注释的工程自觉。
- **工具链摘要与 LLM 标题的克制**：只有链首个工具收到 meta（`server.rs:1906-1913`），LLM 失败不阻塞、不持久化假数据；`get_goose_disable_tool_call_summary` 配置可整体关掉（1520-1525 行）。

## 新人提示

- **调试入口**：外部连接调试先看 `goose acp`（stdio 最小闭环，cli.rs:2099）；桌面链路看 goosed 的 `/acp` 路由与 `check_acp_token` 中间件（`crates/goose-server/src/commands/agent.rs:86-88`）。代码里埋了大量 `target: "perf"` 日志（如 `server.rs:70、2442-2447` 的 ttft 打点），配合 `sid_short()`（225 行，8 字符前缀）可 `grep 'perf:' | grep 'sid=xxxx'` 抽单会话时间线——这是该层自带的观测手段。
- **schema 再生成**：`cargo run -p goose --bin generate-acp-schema`（bin 注册见 `crates/goose/Cargo.toml:275-276`），会同时刷新 `acp-schema.json` 与 `acp-meta.json`。**永远不要手改这两个文件**——它们是过程宏从 Rust 类型编译期推导的产物，手改必被下次生成覆盖。
- **坑清单**：① 术语坑——ACP session ≠ 内部 Session（`server.rs:152-162` 注释），排障时先确认说的是哪个；② SSE 一律拒绝，`McpServer::Sse` 转 ExtensionConfig 时直接报错 "migrate to streamable_http"（`server.rs:503`）；③ ElicitationRespond 不能走会话级 custom dispatch（`server/custom_dispatch.rs:316-323`），写在 agent 上必返回错误；④ 会话列表 cursor 与 filter 绑定（`server.rs:250-268` 的 `filter_hash`），换过滤条件复用旧 cursor 会得到 invalid_params；⑤ 加新自定义方法的正确姿势是先在 `custom_requests.rs` 定义带 `#[request(method = "_goose/unstable/...")]` 的类型，再在 `custom_dispatch.rs` 加 `#[custom_method]` handler，最后重跑 schema 生成——三步缺一，TS 客户端就看不到新方法；⑥ provider 侧模型名填 `current` 即可（`provider.rs:45`），connect 后自动解析，别硬编码子 agent 的模型名。
