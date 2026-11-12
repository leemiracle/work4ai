# agent-gateway 新人上手指南（ONBOARDING）

> 图谱口径：1445 节点 / 2961 边 / 16 层 / 15 步 tour @7af20225，fingerprints 329 文件。行号锚均经源码核实（2026-11-02，develop）。

## ① 项目定位：一句话与生态位

**Agent Gateway 是（Gateway + AgentServer）分离部署中的网关进程**：位于用户侧频道与 AgentServer 之间，接收 Web UI、TUI、ACP 客户端与 9 家 IM 平台的连接，把请求归一化后经**单条 WebSocket（E2A 协议）**路由给 AgentServer，并承载定时任务、心跳、健康检查与多实例隔离等公共服务。它**自己不跑 Agent 循环**——工具执行与用户态文件读写全在 AgentServer 侧。

三名并存（母仓 jiuwenswarm 拆分中间态）：发行名 **agent-gateway**、import 包名 **agent_gateway**、母仓 **jiuwenswarm**——大量文件头带「Gateway 侧副本，源文件 jiuwenswarm/...；改动请同步两侧」。桌面产品名是 **WorkSwarm**（agent_gateway/common/_build_config.py:7），而工作区是 `~/.jiuwenswarm`、对端入口叫 `jiuwenswarm-agentserver`——三名同一条产品线。

## ② 技术栈与代码形态

Python ≥3.11，setuptools + uv。依赖两朵云（pyproject.toml）：**协议内核是 git 源钉 commit 的外部包** openjiuwen 与 openjiuwen-protocol——Message/EventType/ReqMethod、E2AEnvelope 等线协议本体**不在本仓**（docs/zh/reference/e2a-protocol.md §0：真源在 `openjiuwen_protocol/e2a/models.py`）；服务面 FastAPI/uvicorn/websockets；配置 pydantic + ruamel.yaml；调度持久化 aiosqlite/portalocker/croniter/psutil；OpenTelemetry 与七家 IM SDK。两个入口：`agent-gateway`（网关+频道）与 `agent-gateway-acp`（ACP stdio 桥）。

代码形态三特征：巨型文件多（app_gateway.py 3978 行、message_handler.py 5821 行、app_web_handlers.py 6173 行）；母仓镜像副本带同步注释；多见 sys.modules 别名 shim 与惰性 re-export barrel（迁移地层痕迹）。

## ③ 目录结构导览（对应图谱 16 层）

| 层 | 目录 | 内容 |
|---|---|---|
| L01 | 根目录 | pyproject/pytest.ini/run_tests.sh、双语 README |
| L02-03 | common/ | config.py 2689 行配置中枢、模型目录与选择链 |
| L04 | app_gateway.py 等 | 编排入口 + gateway_lock.py 单例锁 |
| L05 | channel_manager/ | base.py（ChannelType/BaseChannel/RobotMessageRouter）+ im_platforms 九平台 |
| L06 | web/ | WebChannel 24 文件：web_connect.py 2243 行、app_web_handlers.py 6173 行、transport_stall_guard |
| L07 | protocol/ + tui/ | a2a/acp/ssh/web_proxy 接入面 + TuiChannel |
| L08 | routing/ | agent_client/e2a_proxy/keys/session_map/session_sharing |
| L09 | message_handler/ 等 | 双队列枢纽 + slash 解析 + 席位/演化审批 |
| L10 | cron/ + runtime/cron/ | 调度线（scheduler.py 2501 行）与存储真身（文件/etcd 双后端） |
| L11 | runtime/ 其余 | events/evolution/work_mode/agent_prewarm |
| L12 | auth/ + health_check/ | OAuth2+PKCE、AES-256-GCM 会话、凭据句柄 |
| L13-14 | extensions/ | loader→manager→registry + sdk；agentos_router（88 方法 RouterClient）、etcd 热更 |
| L15-16 | adx/、docs/ 等 | ADX 沙箱、视频双工；双语文档与 mock-agent-server |

## ④ 核心数据流：一条消息的完整旅程

1. **接入**：客户端连 GatewayServer（app_gateway.py:748 `class GatewayServer(BaseWebChannel)`，start :1163）；WebChannel 由 FastAPI 同端口组装（web_channel_app.py:3）。TuiChannel 与 WebChannel 同走 BaseWsChannel 线（routing/base_ws_channel.py:32；tui_channel.py:41）而非 BaseChannel 直系。
2. **归一化入站**：`_normalize_and_forward_message`（app_gateway.py:351）刷新过期登录凭据→归一化→session.create 注入 work_mode→`deliver_to_message_handler`。
3. **枢纽双队列**：MessageHandler 单例（message_handler/message_handler.py:314，守卫 :337）两条 asyncio.Queue——`_user_messages`（:349，内部循环消费后调 agent_client）与 `_robot_messages`（:350，ChannelManager 消费后按路由扇出）。
4. **定址**：RoutingKey 五维 `(user_id, channel_id, app_id, agent_ref, session_id)`（routing/keys.py:19-20）；IM 身份经 session_map（session_map.py:9）持久映射到 agent 会话；session_sharing 支撑多窗口与 GodView 订阅（session_sharing.py:33）。
5. **南向转发**：WebSocketAgentServerClient（routing/agent_client.py:117）单条 WebSocket 连 AgentServer，握手等 connection.ack（:269-276）；响应按 request_id 复用回收，撞号抛 DuplicateRequestIdError（:56）。e2a_proxy.py 是统一薄代理：**认证后只转发不读**，不可达报可重试错误、禁止部署侧目录代跑。Gateway 主动请求用 `fetch-` 前缀防撞号（e2a_proxy.py:52-56），撞号未发出故可换号重试（:255）。
6. **cron 定时线**：scheduler.py heapq 事件堆调度（:651）到点前唤醒 agent；任务绑定凭据句柄 credential_ref（cron/scheduler.py:93-123）；推送经出站队列回创建渠道。

## ⑤ 关键模块深潜

### 5.1 app_gateway.py——3978 行编排中枢
`_run()`（app_gateway.py:1884）总装：ChannelManager、GatewayServer（:1163）、Cron 调度（:2035）、心跳代理（:2062）、健康检查（:2124）、连远端 AgentServer。进程级前提：dotenv 早期解析（:64-66，在 jiuwenswarm import 之前）；工作区单例锁（gateway_lock.py:24 `.gateway.lock`，与桌面 preflight 的互斥契约）。

### 5.2 message_handler.py——5821 行单例枢纽
双队列见 §4；周边四件套：command_parser（受控通道 /branch 分叉会话 :2371）、join_exit_handlers（席位进出）、evolution_approval（演化审批）、im_pipeline（群发/私发判定与忙碌 steer）。

### 5.3 channel 13 渠道体系
ChannelType 13 成员（base.py:26-40：acp/web/feishu/xiaoyi/dingtalk/telegram/discord/slack/whatsapp/wecom/wechat/ssh/cli）。9 家 IM 各成子包、**均惰性 import**（app_gateway.py:1898：禁用平台不读重依赖）。飞书最重（feishu_connect.py 3863 行，流式卡片+群聊数字分身 :69-72）；钉钉 Stream 模式 1202 行；企微 WSClient 长连接；个人微信走 ClawBot 桥；小艺是华为 A2A 客户端。MessageStore（platform_adapter/message.py:44）是共享群聊记忆底座。WebChannel 以 `register_method` 注册 RPC 处理器（web_connect.py:347）。

### 5.4 cron 双后端存储
调度线在 cron/，**存储真身在 runtime/cron/**：cron/store.py 等 6 文件是 sys.modules 别名 shim（cron/store.py:7，占包内一半）。工厂（runtime/cron/factory.py:27-31）默认个人版文件存储；etcd 显式 opt-in（`gateway.cron.store_backend=etcd`），**不从 AgentOS 路由或非空 endpoints 推断**，缺 endpoints 报错不回退本地文件（:49-50）。

### 5.5 transport_stall_guard——生产事故结晶
issue #4946：客户端停读后 TCP 零窗口 ACK，socket 永久 CLOSE-WAIT，实测 **1888 个**（transport_stall_guard.py:11）——各占一个 fd 加全部缓冲，还钉死 uvicorn 优雅关闭。修法 TransportStallGuardMixin（:35）：pause_writing 越高水位 60 秒（:32）即 abort。

## ⑥ 设计决策与权衡

1. **母仓镜像副本**：带同步注释的副本而非共享库——代价是双仓漂移，收益是三方独立引用且无循环依赖。
2. **Web/TUI 同名 RPC 契约三处分叉禁合并**：config.set / config.validate_model / models.list 三个方法两侧 env 键集、必填项、回包字段皆不同——config_panel/__init__.py:5-6 与 tui_models_handlers.py:10 明示「禁止合并实现」；E2A 代理分叉由 gateway 包装器另包一层。
3. **etcd 显式 opt-in 不静默降级**：HA 语义下静默换后端会双写/漏调度，宁可启动失败（见 5.4）。
4. **fail-loud 守卫**：类级 `@staticmethod __getattr__`（session_metadata_remote.py:82-89）让远端模式误调写方法直接 RuntimeError（写方法在 AgentServer 进程）；request_id 撞号注册即抛（routing/agent_client.py:56）而非路由错乱。
5. **凭据句柄化**：模型配置只放 `jiuwen-login:<ref>` 占位（login_credentials.py:13/:51），请求前由 httpx 钩子（:384）换最新 id_token（1 小时轮换）经 passthrough 透传；登录会话 AES-256-GCM 信封落盘（session_store.py:6）。
6. **reasoning 注入五路径共享咽喉**：AgentServer/Gateway 校验/TUI 校验/AgentOS/team 模型构建统一走 common/reasoning_injector.py 的 build_reasoning_model_request_kwargs（仓内四个 import 消费点），context_window 过渡期兼容只此一处维护。
7. **文件名安全双闸**：BIDI 控制字符让名字显示成另一扩展名（`evil‮gnp.md` 显示为 evil.md），一律剥除（attachment_safety.py:19/:40）；文件名 180 **字节**预算（180 个 CJK 是 540 字节会被拒）。

## ⑦ 常见任务上手

- **加新 IM 渠道**：ChannelType 加枚举（base.py:26）→ im_platforms/<name>/ 实现 Channel（长连接继承 BaseChannel，WS 类走 BaseWsChannel）→ channel_manager 注册 → `_run` enabled 分支加惰性 import（照 app_gateway.py:1898 模式）→ config.yaml 渠道块。参考最薄实现 telegram/discord。
- **改 cron 存储**：动 runtime/cron/（store.py / etcd_store.py / factory.py），**不要动 cron/ 顶层 shim**（被 sys.modules 整体替换，改了不生效）。系统 `proactive.tick` 禁止手动创建修改。
- **本地校验**（docs/zh/how-to/local-validation.md）：终端 A `uv run python examples/mock-agent-server/mock_agent_server.py 19501`；终端 B 设 `JIUWENSWARM_HOME` 后 `uv run agent-gateway --port 19500`；再跑 `gw_client.py ws://127.0.0.1:19502/tui`，期望 connection.ack → chat.send res → 3 条 chat.final。回归用 `./run_tests.sh`（-c 覆盖率/-u 单测/-p xdist 并行）。

## ⑧ 新人提示与坑

1. **cron 存储真身已迁 runtime/cron/**，docs/zh/explanation/architecture.md:48 仍写「cron/ 定时任务存储」——文档滞后，找存储代码认 runtime/cron/。
2. **protocol/ 不是协议源**：channel_manager/protocol/ 只放通道实现（a2a/acp/ssh/web_proxy，各 __init__ 均 0 字节）；协议本体在外部包 openjiuwen_protocol，仓内 grep 不到 Message 定义属正常。
3. **examples/ 被图谱裁剪**（.understandignore 含 `/examples/`），mock 脚本直接看盘上 examples/mock-agent-server/。
4. **凭据是句柄不是 token**：api_key 形如 `jiuwen-login:<ref>` 是设计如此，写 id_token 进配置一小时内过期。
5. **Gateway hooks 只挂四类生命周期**（hooks/handler.py:31-105），超时 10s 短于 AgentServer 的 30s，失败只记日志不阻塞转发；executor 只认 command/prompt 两类。
6. **改 config_panel/镜像文件先读文件头**：同步警示在前两行；Web/TUI 契约分叉是刻意的，别好心合并。
7. **health_check 与 heartbeat 是两回事**：前者周期探活 AgentServer（旧名迁移，app_gateway.py:164-200 兼容）；后者是线程续跑任务。
8. **多实例**：`JIUWENSWARM_HOME`/`JIUWENSWARM_DATA_DIR` 隔离 + `.gateway.lock` 单例；模型选型链在 common/，是 Web/TUI 面板共同后端。

---

**Tour 15 步**：鸟瞰 → 进程入口 → 配置中枢 → 模型目录 → 渠道基座 → WebChannel → IM 巡礼 → 协议/TUI → 南向 E2A → 消息枢纽 → cron 双线 → 登录认证 → 扩展框架 → AgentOS/ADX → 运维收尾。
