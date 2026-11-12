# 04 WS 编排枢纽巨物 agent_ws_server.py（tour S06）

## 一、角色定位

`jiuwenswarm/server/agent_ws_server.py` 是全仓的依赖枢纽与最大单文件（14735 行，`AgentWebSocketServer` 单类 264 个方法，模块级还有 40 余个辅助函数/类）。它是 Gateway↔AgentServer 之间的 WebSocket 服务端：监听来自 Gateway（WebSocketAgentServerClient）的连接，按协议处理请求。类 docstring（agent_ws_server.py:1223-1236）写明线协议：收 JSON 解析为 E2AEnvelope（或过渡期 legacy 兜底信封）；`is_stream=False` 走 `process_message` 回一条 E2AResponse JSON；`is_stream=True` 逐条回 chunk/complete/error；推送（send_push）同样走 E2AResponse 线格式。

这个文件的职责清单长得惊人：WS 消息分发、会话与 Team 管理、计划模式、沙箱、MCP 注册表/凭据/OAuth、RSI harness（agent_ws_server.py:1460 `set_rsi_harness_provider`）、推荐、遥测 keepalive（StreamKeepalive 类，agent_ws_server.py:686）与诊断。**它是 god-class 现象的极端样本**——编排层集中式风格在这个仓库是系统性的，而这里是震中。

周边三个文件是它的"减负尝试"：dispatch.py 把业务 handler 外置成查表；lifecycle.py 是 8 态就绪状态机；app_services.py 是进程级服务工具箱。

## 二、内部结构

### dispatch.py：查表分发器（365 行）

docstring（dispatch.py:3-7）讲清定位：**WebSocket 查表——请求类型 → 业务函数；HTTP 以后按路由直接调 handlers 不经此表；还没搬出 WebSocket 类的请求不会出现在表里**。这最后一句话是理解分发全貌的钥匙：HANDLERS 表（dispatch.py:127 起，195 个 ReqMethod 条目）只覆盖已迁移部分，其余请求仍走 agent_ws_server.py 里的 `_handle_*` 方法（如 `_handle_session_list` agent_ws_server.py:5044、`_handle_team_delete` agent_ws_server.py:5970、`_handle_permissions_config` agent_ws_server.py:6566、`_handle_lifecycle_request` agent_ws_server.py:6034）。

`try_dispatch`（dispatch.py:355-365）命中即执行并返回 True，未登记返回 False 交回原判断——渐进迁移的安全网。企业版专家 handler 在模块导入时装配（`_install_enterprise_expert_handlers`，dispatch.py:339-349，个人版不加载该模块）。表内容按域分组：agents/extensions/mcp（11 个条目）/schedule（12 个）/session（20 余个）/team/commands/permissions/cron 回执（dispatch.py:209-216 注释：企业版 HTTP 与 WS 共用，缺项会 HTTP_METHOD_NOT_HANDLED）。

### lifecycle.py：8 态就绪状态机（205 行）

ReadinessState（lifecycle.py:12-22）八个状态：STARTING → TRANSPORT_READY → CONTROL_READY → RUNTIME_WARMING → AGENT_READY，加 DEGRADED / DRAINING / FAILED 三个旁路态。语义分层（lifecycle.py:56-62）：**Front 监听只需 TRANSPORT_READY；控制面 RPC 在 CONTROL_READY 开放；执行请求自 RUNTIME_WARMING 起可排队、AGENT_READY 才执行**。

状态集合用 frozenset 定义能力视图（lifecycle.py:25-51）：`_TRANSPORT_STATES` 含六态、`_AGENT_STATES` 仅 {AGENT_READY, DEGRADED}。`snapshot()`（lifecycle.py:76-102）把状态翻译成 transport_ready/control_ready/runtime_warming/agent_ready 四个布尔 + capabilities 三元组，供外部探测。几个迁移方法的注释值得精读：

- `mark_runtime_warming`（lifecycle.py:125-136）：**Worker 重启必须重新挡 chat**——从 AGENT_STATES 回 warming 时显式 `self._agent_ready.clear()`，让所有 waiter 重新挂起等下一个 AGENT_READY。
- `mark_failed`（lifecycle.py:158-164）与 `mark_recovering`（lifecycle.py:166-180）：FAILED 是粘性的，普通 warmup 进度出不来（防坏启动死循环）；**config reload 是唯一被认可的离场信号**——Supervisor 重启 Worker、readiness 回 RUNTIME_WARMING。
- `note_warmup_retry`（lifecycle.py:182-194）：可重试的 warmup 错误留在 RUNTIME_WARMING 且 `retrying=True`，新连接持续看到"正在热身"的控制面。
- Worker 侧的可选进度用 `note_runtime_progress`（lifecycle.py: 准入仍用旧状态；runtime_phase 取 IPC_READY/EXECUTION_MIN_READY/FULLY_WARM，lifecycle.py:52）。

### app_services.py：进程级工具箱（309 行）

docstring（app_services.py:1-10）用大白话立规矩：进程就是程序活着的那一整份；工具箱放全份共用的对象（Agent、会话运行时、定时任务、沙箱、模型缓存、流式任务）；**整个进程只造一份，WebSocket 与 HTTP 都从这份拿，不再各备一套；与单条连接绑定的东西（心跳、编辑器能力、往这条连接推消息）不放这里**。

AppServices（app_services.py:66-88）持有 agent_manager/runtime/session_message_service/proactive_engine/scheduler_service/jiuwenbox_runner/session_stream_tasks/model_cache/tokenizer_service/plan_controller/adapter_registry 等。`execution_runtime()`（app_services.py:89 起）是惰性重建逻辑：runtime 为 None 或 agent_manager 已换人就现造。工具函数 `is_tcp_port_bindable`（app_services.py:20）/`pick_free_tcp_port`（app_services.py:31）服务于端口探测；`resolve_adapter`（app_services.py:39-52）从外壳 Agent 取出真 adapter（探测 `apply_sandbox_runtime_patch` 属性）。

### agent_ws_server.py：巨物本体

结构上分两段。**模块级前奏**（agent_ws_server.py:287-1161）：约 40 个辅助构件——TurnOutcomeTracker（agent_ws_server.py:631，从 RuntimeEvent 流判定 turn 结果）、StreamKeepalive（agent_ws_server.py:686，流式遥测保活循环，`_consume_keepalive_task_result` agent_ws_server.py:541/`_stop_stream_keepalive` agent_ws_server.py:563 配套）、`_payload_to_request`（agent_ws_server.py:989，legacy 载荷兜底解析）、`_reuse_server_runtime_dependencies`（agent_ws_server.py:287）、`_inject_plan_mode_activation_reminder`（agent_ws_server.py:1161）等。

**AgentWebSocketServer 类**（agent_ws_server.py:1222 起）关键设计：

- **单例**：`_instance` 类属性（agent_ws_server.py:1236）、`get_instance`（agent_ws_server.py:1504）/`reset_instance`（agent_ws_server.py:1527）。
- **_AppField 描述符**（agent_ws_server.py:1207-1219）：14 个历史字段名（`_runtime`/`_agent_manager`/`_model_cache`...，agent_ws_server.py:1238-1251）经描述符转发到 AppServices 同名数据——旧代码和测试继续写 `server._agent_manager`，真实数据在进程工具箱里（agent_ws_server.py:1231-1234 注释明说是兼容层）。这是"巨物不动、数据先搬"的手术路径。
- **消息入口**：`_handle_message`（agent_ws_server.py:2639）解析 JSON → E2AEnvelope.from_dict（agent_ws_server.py:2659）→ 失败按旧载荷解析（`_payload_to_request`）→ E2A 内部上下文带 fallback 失败标记时退 legacy_agent_request（agent_ws_server.py:2663-2677）。流式/单发分流在 `_handle_unary`（agent_ws_server.py:3920）与 `_handle_stream`（agent_ws_server.py:4017 → `_handle_stream_impl` agent_ws_server.py:4638）。
- **连接治理**：`bind_gateway_transport`/`attach_gateway_connection`（agent_ws_server.py:1616/agent_ws_server.py:1621）、`on_gateway_disconnect`（agent_ws_server.py:1639）、`_release_current_connection`（agent_ws_server.py:1496）、send_push 无连接告警限流（agent_ws_server.py:1291-1292 附近注释：首条立即告警，之后按窗口汇总）。
- **构造期 MCP 补丁**：`__init__` 第一件事 `apply_mcp_apps_patch()`（agent_ws_server.py:1288-1289）——在任何请求能创建 MCP 工具之前 patch `MCPTool.invoke`（openjiuwen 在构造时逐实例绑定 invoke，晚了就漏）。

## 三、外部连接

- 上游：Gateway 进程的 WebSocketAgentServerClient（app_gateway.py:1932 导入）经 WS 连到这里；Front 层（server/front/server.py 的 AgentServerFront，front/server.py:23 docstring "Owns the Gateway-facing port. Does not construct Agent Runtime"）实际持有端口，本类经 attach 挂进 Front。
- 下游：HANDLERS 表指向 server/handlers/ 下约 20 个域模块（agents/bootstrap/chat/commands/extensions/mcp/mcp_hub/ops/permissions/sandbox/schedule/session/team...）；未迁移的 `_handle_*` 方法直接调用 AppServices 里的服务与 06 篇的 JiuWenSwarmDeepAdapter。
- Front 的纪律实测可查：front/ 目录七个文件（admission/connection/event_forwarder/protocol/request_registry/router/server）**零 `jiuwenswarm.common.config` import**（grep 实证）——Front 进程不加载配置是启动速度的保证，这条红线是硬的。
- lifecycle 的 Readiness 由 app_agentserver.py:130 消费（`front.readiness.snapshot().get("control_ready")`），Worker 侧经 IPC readiness 流驱动 mark_agent_ready。

## 四、数据流

一条 Gateway 请求的完整旅程：

1. Gateway 把消息发到 AgentServer WS 端口；Front 的 ConnectionHandler 完成握手（front/connection.py 的 process_handshake）。
2. MethodRouter 先问 admission（ExecutionAdmission，front/admission.py）：按 Readiness 状态决定放行/排队/拒绝——CONTROL_READY 前控制面也不开，RUNTIME_WARMING 起执行请求可排队。
3. `try_dispatch`（dispatch.py:355）查 HANDLERS：命中则 `bind_request_tenant(ctx)` 上下文内执行 handlers 模块函数；未命中落入 agent_ws_server.py 的 `_handle_lifecycle_request`（agent_ws_server.py:6034）或各 `_handle_*` 方法。
4. `_handle_message`（agent_ws_server.py:2639）解码线协议；流式请求经 `_handle_stream_impl`（agent_ws_server.py:4638）驱动底层 Runtime，StreamKeepalive（agent_ws_server.py:686）在长执行期间定期发保活帧、TurnOutcomeTracker（agent_ws_server.py:631）观察事件流判定成败。
5. 响应编码回 E2AResponse（单发一条/流式逐条）；主动推送走 send_push 同线格式，无连接时限流告警。
6. 进程级状态（模型缓存、会话服务、调度器）全部经 `_AppField` 描述符落到 AppServices 单份；连接断开只清理连接级资源，工具箱不动。

## 五、设计决策

1. **渐进式外科手术而非大爆炸重写**：HANDLERS 查表（dispatch.py:355-365 返回 False 兜底）+ `_AppField` 描述符转发（agent_ws_server.py:1207-1219）让巨物可以一块一块拆而行为不变。代价是**同一请求域可能有两份真相**——表里一条、类里一条，读代码必须两头查。
2. **8 态而非布尔**：transport/control/execution 三种能力独立开放时间线（lifecycle.py:25-51），让 Gateway 可以"先连上、再配置、最后干活"的渐进体验；FAILED 粘性 + reload 唯一离场（lifecycle.py:166-180）防抖动。
3. **进程工具箱与连接事务分离**（app_services.py:1-10）：明确"什么进工具箱"的判据是"是否属于整个进程"——这条判据比任何模式名都好用。
4. **构造期打补丁**（agent_ws_server.py:1288-1289）：openjiuwen 的 per-instance invoke 绑定使得 MCP 补丁必须抢在第一个请求之前，这类时序约束只能放在 `__init__` 最前。
5. **集中式编排的代价自洽**：14735 行单类换来了跨域 handler 共享上下文的零成本（全部 `self._xxx` 可达），但新人定位"某请求谁处理"需要三跳（ReqMethod → HANDLERS → handler 或 → `_handle_*`）。这是本仓编排层的系统性选择，见 06 篇 interface_deep 的同型现象。

## 六、新人提示

- 找"某个 ReqMethod 谁处理"的标准动线：先 grep `ReqMethod.XXX` 在 dispatch.py 的表项 → 有则跳 handlers/ 模块；无则 grep `_handle_` 系列在 agent_ws_server.py。**别只看一头**。
- 加新 RPC 时优先登记进 HANDLERS（新代码禁止再往巨物里加 `_handle_*`，这是迁移方向）；记得 handlers 函数签名统一吃 RequestContext。
- 改 Readiness 迁移逻辑前重读 lifecycle.py:125-136 的注释——`_agent_ready.clear()` 那三行是 Worker 重启期间不误放请求的关键，删了会在重启窗口漏进执行请求。
- StreamKeepalive 与 TurnOutcomeTracker 是模块级类不是内部类（agent_ws_server.py:631/:686），测试可以直接构造，别在类里找。
- 排查"Front 起得慢"：确认没有人在 front/ 目录引入 config 或重依赖——Front 的价值就是薄，import 一重整个进程可用性倒退。
- 该文件大量 handler 内部延迟导入（函数体内 import），读静态 import 图会低估其依赖面；用 grep 函数体才能看到真实耦合。
