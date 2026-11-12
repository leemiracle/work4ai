# 01 · app_gateway.py：3978 行编排中枢——独立 Gateway 进程的装配与自愈

> 锚定 commit `7af202253`。本文行号均指 `agent_gateway/app_gateway.py`，另注者除外。

## 一、角色定位

`app_gateway.py` 是拆分部署（split deployment）形态下独立 Gateway 进程的**唯一入口与总装车间**。模块 docstring 开宗明义（`agent_gateway/app_gateway.py:2-12`）：这个进程要拉起四样东西——Gateway MessageHandler + ChannelManager、WebChannel WebSocket 服务（浏览器入站）、Heartbeat 服务、Cron 调度服务（经 ws 触发远端 AgentServer），再以 WebSocket 客户端身份连到一个远端/本地 AgentServer。母仓 jiuwenswarm 的一体化部署由 Desktop 在 spawn 前做好工作区准备，独立安装时这份工作落回本文件（app_gateway.py:75-85 的 `JIUWENSWARM_RUNTIME_WORKSPACE_READY` 标记就是为了去重这层磁盘工作）。

它有三个身份叠加：**CLI 入口**（`main()` app_gateway.py:3870 起，argparse 定义 `--agent-server-url/-u`、`--host/-H`、`--port/-p` 等，AgentServer 默认端口取 `AGENT_SERVER_PORT` 或 `AGENT_PORT` 回落 `18092`，app_gateway.py:3937-3938）；**装配函数 `_run()`**（app_gateway.py:1884 起，近 2000 行，把十几个子系统按依赖序接线）；**多路路由 WS 宿主 `GatewayServer`**（app_gateway.py:748 起，继承 `BaseWebChannel`，一条 ws 服务器承载 `/acp`、`/cli` 等多条 route）。进程名与包名对齐的历史（近期 commit "修改进程名为 agent-gateway"）也体现在 app_gateway.py:3874 的 `prog="agent-gateway"`。

## 二、内部结构

**启动分相仪表。** app_gateway.py:34-39 定义 `_PROCESS_START_T0` 与 `_STARTUP_IMPORT_PHASES`，`_mark_startup_import_phase()` 在每个早期阶段打点：`dotenv_parsed`（app_gateway.py:67）、`logging_ready`（app_gateway.py:73）、`runtime_workspace_ready`（app_gateway.py:85）、`openjiuwen_and_channel_base_imported`（app_gateway.py:93）。进入 `_run` 后再把整张表连同耗时逐行打日志（app_gateway.py:1938-1943），并切换到 `log_startup_stage()`（app_gateway.py:1947）打 `run_elapsed`。注释明说这是为"冻结 EXE 排查启动超时要用各阶段时间戳对齐 Desktop 日志"（app_gateway.py:1944）——PyInstaller 单文件发行版的冷启动是真实运维痛点，这份仪表就是为此埋的。

**导入序即依赖序。** 文件头部的导入顺序被精心编排：`--dotenv` 早期解析必须发生在 jiuwenswarm 重依赖导入**之前**（app_gateway.py:63-66 注释 "-- Early --dotenv parsing (before jiuwenswarm imports)"），日志初始化自带双路径（母仓已配则复用，独立安装自建，app_gateway.py:69-72），然后才敢动 `openjiuwen.core` 与各 channel 模块。协议层则完全依赖外部包 `openjiuwen_protocol`（app_gateway.py:41-49 导入 `Message`/`Mode`/`ReqMethod` 与 `e2a_from_agent_fields`）——本仓 `channel_manager/protocol/` 只是薄壳。

**`_run()` 的装配主线**（app_gateway.py:1884-3837）可压缩为十五步：①扩展系统 `ExtensionRegistry.create_instance` + `ExtensionManager.load_all_extensions`（app_gateway.py:1959-1972）；②AgentServer 客户端选择——优先扩展（如 Yuanrong/adx_router），否则 `WebSocketAgentServerClient(ping_interval=20.0, ping_timeout=600.0)`（app_gateway.py:1989）；③`_connect_with_retry` 连接（默认 20 次 × 3s，来自 `AGENT_CONNECT_RETRY`/`AGENT_CONNECT_RETRY_INTERVAL` 环境变量，app_gateway.py:1974-1975）；④`MessageHandler(client)` + `start_forwarding()`（app_gateway.py:2013-2014）；⑤IM 双 pipeline 挂接（app_gateway.py:2019-2022）；⑥cron 三件套 `create_gateway_cron_store` → `CronSchedulerService` → `CronController.get_instance` 单例 + `bind_agent_client`（app_gateway.py:2024-2042），并把 cron 工厂注册进 provider 注入点 `"cron_store_factory"`（app_gateway.py:2048）；⑦`session_metadata` 与 `mcp_registry` 两域远端实现的客户端绑定（app_gateway.py:2054-2058）；⑧Heartbeat 只留代理——Store/Controller/Scheduler/Execution 全在 AgentServer，Gateway 持 `HeartbeatControllerProxy(client)`（app_gateway.py:2060-2062 注释钉死了这条边界）；⑨健康检查 `GatewayHealthCheckService`（app_gateway.py:2124-2129）；⑩`ChannelManager(message_handler, config={})` 初始化后**回填** `message_handler.set_channel_manager`（app_gateway.py:2139-2141 注释解释：MessageHandler 实例化早于 ChannelManager，广播全局事件需经它取 web channel）；⑪GatewayServer/ACP/TUI/web 等 ws 服务逐一起任务；⑫`_apply_initial_channel_config()` 以后台任务方式套用可选渠道（app_gateway.py:3654）；⑬`_wait_for_gateway_tasks_or_restart` 主等待循环（app_gateway.py:3668）；⑭finally 里按序拆除近 20 项资源；⑮`restart_requested` 为真则 `_exec_gateway_restart()`（app_gateway.py:3833-3835）。

**GatewayServer 的路由模型。** 每条路由是一个 `RouteConfig`（app_gateway.py:699-718）：`path`、`channel_id`、可转发的 method 集合、本地 handler 表、入/出站 interceptor、cleanup/disconnect/session_bind 钩子，以及关键的 `ws_channel` 委托字段——app_gateway.py:713-717 注释写明 V2 设计：GatewayServer 仍作 ws 宿主 + 入站帧解析，但把 ws + RoutingKey 委托注册进外部 Channel（如 tui 的 TuiChannel）的五维索引，出站由 ChannelManager 按 `delivery.ws_id` 物理寻址派发到该 Channel.send；`None` 表示无需委托（acp 自带 `_session_to_client` 反查，web 有独立 WebChannel 不经此路径）。`GatewayServerConfig` 默认 `127.0.0.1:19001`（app_gateway.py:722-728）。

## 三、外部连接

- **上连 AgentServer**：WebSocket 客户端（app_gateway.py:1989），也可被扩展替换为 adx_router（选了却加载失败直接 `RuntimeError`，app_gateway.py:1982-1984）或 Yuanrong HTTP 客户端（`client.connect("")` 无需真连，app_gateway.py:2008-2010）。
- **下挂 ChannelManager 十三渠道**：经 `channel_manager.set_conf(name, conf)` 逐渠道启用（app_gateway.py:3615），IM 平台全部惰性导入——app_gateway.py:1891-1893 注释列出 dingtalk/feishu/whatsapp/wechat/xiaoyi/telegram/discord/slack/wecom 九平台，只在对应 enabled 分支内导入，避免冷启动为禁用平台读 slack_bolt/telegram/redis/aiohttp 重依赖。
- **对 supervisor**：退出码契约 vendored 在 `agent_gateway/common/process_supervision.py:13-23`——`GATEWAY_RESTART_EXIT_CODE=75`（请求 respawn）、`CRASH_EXIT_CODE=70`（EX_SOFTWARE，Windows 区分崩溃与 taskkill 用）、`SUPERVISOR_PID_ENV="JIUWENSWARM_SUPERVISOR_PID"`。
- **注入点网络**：`external_providers.register("cron_store_factory", ...)`（app_gateway.py:2048）让 common 层 model_resource 处理器能反向创建 gateway 侧 cron store；`main()` 里预装 `install_session_metadata_remote()` 与 `install_mcp_registry_remote()`（app_gateway.py:3934-3935），注释钉版：a2ui/team/mcp_state/mcp_credential 域在本进程零消费、保持未注册，调用会得 `ExternalProviderUnregistered` 降级（app_gateway.py:3925-3928）。
- **reasoning_injector 五路径咽喉**：模型构造参数（reasoning 注入）统一走 `agent_gateway/common/reasoning_injector.py:145` 的 `build_reasoning_model_request_kwargs()`，其 docstring 注释（reasoning_injector.py:150-152）点名五个消费方——AgentServer、Gateway validation、TUI validation、AgentOS、team models；本仓内的直接调用者是 IM 入/出站（`im_inbound.py:413`、`im_outbound.py:127`）与模型路由注册表（`model_routing_registry.py:87`）。改 reasoning 参数语义必须过这五条路径的回归。

## 四、数据流

**入站（浏览器/ACP/TUI → AgentServer）**：ws 帧进 `_connection_handler`（app_gateway.py:1366）——先 `_resolve_route` 匹配路径，不认识的路径直接 `ws.close(code=1008)`（app_gateway.py:1374）；握手阶段从查询串抽 `session_id`、从头部抽 X-User-Id（`_SAFE_USER_ID_RE` 白名单 app_gateway.py:62 只放行字母数字与 `_-`，拒绝路径遍历），打 `[Gateway] WS handshake` 日志（app_gateway.py:1388-1396）；连接钩子执行后立刻回 `connection.ack` 事件帧（协议版本 1.0，app_gateway.py:1438-1446）。随后 `async for raw in ws` 把每帧交给 `_handle_raw_message`（app_gateway.py:1453-1455 → app_gateway.py:1533），最终经 `_normalize_and_forward_message`（app_gateway.py:351）规范化后由 MessageHandler 转发上游。

**出站（AgentServer → 前端）三级级联**：`GatewayServer.send()`（app_gateway.py:1206-1364）是全文件最重要的派发函数。app_gateway.py:1213-1217 注释明示三级：第 1 级 `routing_target`（team fan_out 投递，按 routing_keys 的 session_id 维查 `_session_to_client`，app_gateway.py:1219-1238，保证 TUI/ACP 误入 team 路径时 GodView/mention fan_out 不因签名不符静默丢弃）；第 2 级 `request_id` 精确回响应（查 `_request_to_client`，app_gateway.py:1239-1246）；第 3 级 session_id 兜底（app_gateway.py:1247-1255）。三级全 miss 时还有 channel 级广播退路：无 session_id 的消息（如 cron 推送到多 TUI 窗口）广播给该 channel 全部活跃 client（app_gateway.py:1283-1296），最后仍失败则打出带 `sess_table_keys` 反查信息的 dropped 警告（app_gateway.py:1297-1305）。命中 ws 后，`res` 帧构造在 app_gateway.py:1335-1350（含 payload.code 提升为顶层 code 的前端契约，注释引设计文档 §1.3），event 帧构造在 app_gateway.py:1353-1364。

**重启数据流**：`.env` 变更等触发 `_schedule_gateway_restart`（app_gateway.py:632）→ 默认 2s 延迟后 set `GatewayRestartRequest.ready_event`（app_gateway.py:640-644）→ `_wait_for_gateway_tasks_or_restart`（app_gateway.py:653）的 `asyncio.wait(FIRST_COMPLETED)` 竞速返回 True → 逆序拆除 → `_exec_gateway_restart()`（app_gateway.py:592）。

## 五、设计决策与权衡

1. **supervisor 判活不做孤证**。`_running_under_supervisor()`（app_gateway.py:573-589）不满足于 env 匹配：Windows 上 `os.getppid()` 在 supervisor 死后仍报旧 PID（无 reparenting），仅凭 env 会让我们 `os._exit(75)` 却没人 respawn。解法是 psutil 比对父进程 `create_time() <=` 自己的创建时间——PID 被回收复用必属于更年轻的进程，一招同时拒绝两种假阳性。
2. **execv vs exit 75 的平台分叉**。裸跑时 `_exec_gateway_restart` 走 `os.execv` 原地换进程（app_gateway.py:623）；supervisor 之下则必须 `os._exit(75)`（app_gateway.py:600）——因为 Windows 的 execv 会起新 PID 并让旧进程以 0 退出，supervisor 读 0 = "Gateway 停了" → 把整栈（含 AgentServer）拆掉。env 说有 supervisor 但父进程校验失败时，宁打警告也走 execv，并把判定值全部落日志供事后验尸（app_gateway.py:601-621）。
3. **可选渠道故障隔离**。app_gateway.py:2136-2138 注释："Start with no applied integration config... prevents one bad optional channel from suppressing every later channel or terminating the Gateway"。`ChannelManager` 初始传空 config（app_gateway.py:2139），每个渠道独立 try/except，失败后还要**回灌空配置对齐变更检测器**再排重试（app_gateway.py:3624-3641 的注释解释了 set_conf 回滚与 callback 自身 detector 状态漂移的微妙不一致）。
4. **启动节奏优化**：`_wait_for_web_channel_listening`（app_gateway.py:542-570）解释了为什么不能"起了 task 就算数"——`WebChannel.start` 在 uvicorn 真正 bind 之前就 return，Desktop 与静态代理冷启动都依赖 19000 端口，必须轮询 `_uvicorn_server.started` 或 `_server` 非空（10ms 间隔）后才能去做耗时的渠道配置。`_apply_initial_channel_config`（app_gateway.py:3591）则等"首个 homepage 请求进入 MessageHandler"再留 0.75s 窗口给项目/会话 RPC 批（app_gateway.py:3598-3600），让用户先看到页面、慢渠道后置——感知性能工程。
5. **拆除顺序即依赖逆序**：finally 块（app_gateway.py:3675-3831）从 a2a/gateway_server/acp/tui/web 一路拆到 feishu 多 bot、xiaoyi、dingtalk 等 20 项，最后才是 `cron_scheduler.stop()` → `channel_manager.stop_dispatch()` → `heartbeat_service.stop()` → `message_handler.stop_forwarding()` → `client.disconnect()`（app_gateway.py:3821-3825）——先断流量入口、再停调度、最后断上游连接。

## 六、新人提示与坑

- **改导入顺序前先读文件头**。dotenv 解析、日志初始化、工作区准备三件事卡在所有 jiuwenswarm 导入之前，把某个 import "顺手"上移会破坏多实例 `.env` 隔离（app_gateway.py:12 注明 `--dotenv <path>` 支持多实例隔离）。
- **`_run` 是单函数大车间，不是分层架构**。近 2000 行里有 30+ 局部闭包函数（`log_startup_stage`、`_sync_agent_prewarm_channels`、`_on_config_saved`、`_apply_channel_config`…），它们靠闭包共享 `message_handler`/`channel_manager`/`restart_request` 等状态；抽函数重构时这些隐式依赖最容易漏。
- **send() 的三级查找有优先级语义**，不要"优化"成一次 session 查找：request_id 精确回响应保证了多开窗口下响应回到发起者；广播兜底只对无 session_id 消息合法（cron 推送），有 session 的消息走广播会串窗口。
- **退出码 75/70 是跨进程契约**（process_supervision.py），改动前必须同步 supervisor 侧；`SUPERVISOR_PID_ENV` 可能经保存的环境泄漏进无关进程，消费方永远要过 `_running_under_supervisor` 的双校验。
- **启动慢的排查入口**是 `[App] startup import stage=` 与 `startup stage=` 两组日志（app_gateway.py:1938/app_gateway.py:1947），不是加 print。
