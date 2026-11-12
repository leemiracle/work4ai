# 04 · Threads 与 Chat 编排：threads 路由 / streaming 门面 / 适配层 / messaging

## 角色定位

`backend/web/routers/threads.py`（1554 行，21 个端点）是 agent 会话（thread）的 HTTP 面：建线程、发消息、排队 steer、读历史、裁决权限、取消运行、管任务。`backend/threads/streaming.py` 是 run 子系统的装配门面；`backend/threads/chat_adapters/` 是 chat 域与 agent 运行时之间的适配层（gateway 端口模式）；`messaging/service.py` 与 `backend/chat/api/http/` 构成社交消息域（群聊/私聊/已读/入群申请）。四个部分合起来回答一个问题：**一条用户消息如何变成一次 agent 运行，运行过程如何流回浏览器，社交消息如何在人 agent 混合的会话里投递**。

## 内部结构

**threads.py 端点家族**（router 前缀 `/api/threads`，threads.py:68）。21 个端点分六族：线程 CRUD（POST ""/:822 建 child thread、POST /main:847、GET 列表/单条:904/915、DELETE:941）；消息入口（POST messages:977 发消息启动 agent run、queue:1015/1029 排队 steer 消息）；历史与事件（history:1039、events:1306 SSE）；权限（GET permissions:1106、resolve:1127、rules 增删:1195/1224——直接对接 02 篇 ToolRunner 的 ask 挂起/恢复：`resolve` 端点写入一次性批准，下一轮工具调用被 runner.py:468-479 消费）；运行时观测（runtime:1251、sandbox:1280、runs/cancel:1361、tasks 三兄弟:1413-1464 对接子 agent）。SSE 端点 `stream_thread_events`（threads.py:1306-1360）用标准 Authorization 头（注释原话），断线重连以 `Last-Event-ID` 或 `after` 游标续读，**没有内存 buffer 时先从 SQLite 回放历史事件再接实时流**（threads.py:1330-1352）。

**streaming.py：monkey-patch 装配门面（178 行）**。run 子系统被拆成 backend/threads/run/ 下 13 个模块（execution/cancellation/emit/entrypoints/followups/lifecycle/buffer_wiring 等），模块间相互调用全部通过"模块属性槽"完成——streaming.py 在调用前一刻把真实函数写进对方的模块命名空间：`_run_buffer_wiring._append_event = _append_event`（streaming.py:26）、`_run_buffer_wiring._start_agent_run = start_agent_run`（L27）、`_run_execution.ensure_thread_handlers = _ensure_thread_handlers` 及九个槽（L98-107）、`_run_emit.append_event = _append_event`（L108）、`_run_entrypoints._run_agent_to_buffer = _run_agent_to_buffer`（L143）、`_run_followups._start_agent_run = start_agent_run`（L130）。这是与 01 篇 idle_reaper 同款的晚绑定手法，动机也相同：**execution 要调 entrypoints、entrypoints 要调 execution，直接 import 即成环；用回调槽互注，环就断了**。streaming.py 对外只暴露三个入口：`start_agent_run`（L134）、`run_child_thread_live`（L156）、以及内部主循环 `_run_agent_to_buffer`（L87，@@@nu59-complexity-honesty 自嘲复杂度靠 pyright 豁免活着）——它还从 `app.state.threads_runtime_state` 借 chat 域的 typing_tracker（L110-125，@@@run-buffer-borrowed-typing-tracker）。

**事件缓冲**：`ThreadEventBuffer`（backend/threads/events/buffer.py:52-67）是 deque 环（maxlen=2000）+ asyncio.Condition + 单调计数 `_total_count`；`finished` 事件永不置位（@@@thread-buffer-never-finishes，L56-58：保持与 RunEventBuffer 相同的观察者协议面，但线程缓冲永不标完成——线程是长命的）。事件同时落 SQLite（store.append_event）供重连回放。

**chat_adapters：gateway 端口模式**。核心是 `AgentRuntimeGatewayPort`（chat_adapters/port.py:13-18，typing.Protocol，仅两方法 `dispatch_notification` / `dispatch_thread_input`）；`get_agent_runtime_gateway(app)` 从 `app.state.threads_runtime_state.agent_runtime_gateway` 借出实现（port.py:21-26，@@@agent-runtime-port-borrowed-state：web 路由不再读顶层散属性）。chat 域各入口（关系申请/工作流事件/外部收件箱/线程输入）各自实现成 inlet，把社交事件计划（plan）成 `RuntimeAction` 信封再经 gateway 分派（runtime_action.py:41-60 `dispatch_runtime_actions`）。协议本体在 `protocols/agent_runtime.py`：`AgentThreadInputEnvelope`（thread.input.v1，携带 thread_id/sender/message/transport，L57-64）与 `AgentRuntimeNotificationEnvelope`（agent.runtime.notification.v1，L44-52），返回值带路由语义 `routing: Literal["cancelled","steer","direct"]`（L76）——通知可能变成 steer 注入而不是新开 run。

**messaging：schema 不含身份参数**。HTTP 侧 `SendMessageBody`（backend/chat/api/http/chats_router.py:38-46）`model_config = ConfigDict(extra="forbid")`，字段只有 content/mentioned_ids/delivery_scope/addressed_to_user_ids/reply_to/enforce_caught_up——**没有任何 sender/身份字段**；`sender_id = user_id` 一律来自 `Depends(get_current_user_id)` 的 bearer token（chats_router.py:322-325），随后还要过 `_verify_user_ownership`（L123-129，@@@thread-social-owner-check：sender_id 可以是线程属 agent 的社交身份，但必须被当前 viewer 拥有）。CreateChatBody 的 user_ids 字段描述写得更直白："Do not include the authenticated user; the backend adds it from the bearer token"（chats_router.py:30-34）。模型侧同理：进 agent 运行时的信封 sender 由服务端 `make_runtime_actor` 从 user_repo 反查构造（chat_adapters/runtime_identity.py:23-34），用户/类型/显示名缺失直接 RuntimeError——**身份永远是服务端派生的一等事实，不收客户端自报**，模型无法通过消息参数伪造"我是谁"。发送还有因果一致性闸：`enforce_caught_up` 未读先发会被 409 拒绝（chats_router.py:349-350，ChatNotCaughtUpError→"Read unread messages before sending."）。

## 外部连接

- 上游：01 篇 lifespan 装配 threads_runtime 与 chat_runtime 并做五组通知接线（wire_chat_delivery 等）；前端 app SPA（06 篇）消费 SSE 与 REST。
- 下游：POST messages 最终调 streaming.start_agent_run → 02 篇 LeonAgent/QueryLoop；权限 resolve 端点对接 ToolRunner 的 consume_permission_resolution 槽；sandbox 端点对接 03 篇 manager；子 agent tasks 对接 core/agents AgentService。
- 横向：messaging 的投递回调（`set_delivery_fn`，messaging/service.py:167）在 lifespan 里被 wire 成"投递到线程活动流"，@@@notification-mention-delivery（service.py:36）把通知定义为持久 chat 消息而非易失推送。

## 数据流

用户在网页发一条消息：POST /api/threads/{id}/messages（threads.py:977）→ 校验线程所有权与 agent_user 归属 → 构造输入（run/input_construction.py）→ streaming.start_agent_run：先互注回调槽 → entrypoints 建/取 ThreadEventBuffer → execution 跑 agent（02 篇中间件栈），工具调用/文本增量全部 emit 进 buffer（ring 2000 条 + SQLite 双写）→ 浏览器经 GET events SSE 持续读（EventSourceResponse），断线用 Last-Event-ID 回放。同时运行的 steer 消息走 queue 端点入 SQLite 队列，由 SteeringMiddleware 在下一次模型调用前注入。社交侧：人在群聊 @agent → messaging.send 落库 → delivery 动作经 adapter 计划成 AgentRuntimeNotificationEnvelope → gateway.dispatch_notification 决定 wake/transport → 变成 thread.input 或 steer 进入同一条 run 管线。权限 ask：ToolRunner 物化 request_id → 前端弹卡 → POST permissions/{request_id}/resolve → 一次性批准落槽 → 下轮工具调用放行。

## 设计决策（含批判）

1. **回调槽互注 vs 依赖注入容器**：没有引入 DI 框架，用"模块属性赋值"这个 Python 最原生的机制解环。好处是零依赖、grep 可见；代价是**槽必须在每次调用前重新互注**（streaming.py 每个入口函数开头都重赋值一遍）——因为别的入口可能以不同组合赋过槽；忘一次就是 AttributeError，且错误延迟到运行期。
2. **SSE 混合回放**：内存 ring 保热数据、SQLite 保全程，重连先回放再接流。批判：回放与实时之间没有事务边界，极端时序下可能重复或漏一条（seq 单调性靠客户端按 `_seq` 去重兜底）。
3. **身份服务端派生**是这层最值得抄的安全设计：extra="forbid" + bearer 派生 + ownership 三重验证，把"模型谎报身份""客户端冒充他人"两类伪造在 schema 层就判死。注意 MuteChatBody 仍带 user_id 字段（chats_router.py:48）——那是管理动作的目标参数而非消息身份，别混为一谈。
4. **routing 三值语义**（cancelled/steer/direct）让"通知"有了节流智慧：agent 正在跑时新消息降级为 steer 注入，不开新 run——省钱且保上下文连续。副作用是用户消息可能"看起来没触发运行"，前端必须解释 routing 值而不是只看是否出现新 run。
5. **threads.py 1554 行单文件 21 端点**违背小文件美学，但端点间共享极多 helper（sandbox 解析/序列化/权限校验）；拆分的收益会被 import 面扩大抵消。改它时按"六族"定位，别通读。

## 新人提示

- 找"消息发出去之后发生了什么"：从 threads.py:977 端点进 → streaming.py:134 → run/execution.py，三跳即到 agent；不要从 chat 域找（那是社交消息，不是 agent 消息）。
- run/ 模块里的"裸函数引用"（如 `_run_execution.ensure_thread_handlers`）不是死代码，是等待 streaming.py 注入的槽——单测里直接调这些模块要先手动补槽，否则 AttributeError。
- SSE 不出数据三查：buffer 是否被创建（app.state.thread_event_buffers）、`after` 游标是否大于 total_count、线程是否属于当前用户（403 静默发生在 headers 前）。
- 给 chat 加新消息类型时，先问"sender 从哪来"——答案必须是 token 或 user_repo 反查；schema 里加任何身份字段前先读 chats_router.py:30-46 的两个 forbid 配置。
- enqueue 的 steer 消息不会立刻有回音，去 GET queue 端点看状态，或等下一轮 run 的 SSE 里出现 steer 注入事件。
