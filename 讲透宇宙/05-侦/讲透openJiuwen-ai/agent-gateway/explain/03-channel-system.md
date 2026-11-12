# 03 · channel_manager：13 渠道体系——BaseChannel 直系与 BaseWsChannel 反查两条线

> 锚定 commit `7af202253`。行号指 `agent_gateway/channel_manager/` 下各文件，另注者除外。

## 一、角色定位

`channel_manager` 包是 Gateway 的**全部出站世界的抽象层**：13 种渠道类型在 `channel_manager/base.py:26-40` 的 `ChannelType` 枚举里一锤定音——acp、web、feishu、xiaoyi、dingtalk、telegram、discord、slack、whatsapp、wecom、wechat、ssh、tui（注意 CLI 的 value 是 `"tui"`）。包内三套角色分明：`base.py` 给出契约（`RobotMessageRouter` 总线 + `BaseChannel`/`BaseWebChannel` 抽象），`channel_manager.py` 的 `ChannelManager` 负责注册/查找/配置/派发循环，四个子目录（`web/`、`tui/`、`im_platforms/`、`protocol/`）落具体渠道实现。

一个关键的架构事实：**协议定义不在本包**。`protocol/__init__.py` 是 0 字节空文件，`Message`/`E2AEnvelope`/wire codec 全部来自外部 git 依赖 `openjiuwen-protocol`（pyproject.toml:17，`git+https://gitcode.com/openJiuwen/agent-protocol.git`）；本地 `channel_manager/protocol/` 只装"连接器"——a2a、acp、ssh、web_proxy 四个子包共约 4900 行适配代码（如 `protocol/acp/acp_connect.py:19-37` 成批导入 `openjiuwen_protocol.e2a.acp.*` 的构造器做 ACP JSON-RPC 桥接）。所谓"protocol 空壳"精确的含义是：协议本体外部化，本包只剩连接工程。

## 二、内部结构

**两条继承线是本包的骨架**：

- **BaseChannel 直系**（`channel_manager/base.py:119-215`）：抽象方法只有 `start`/`stop`，`send()` 基类默认实现打 warning 丢消息（channel_manager/base.py:167-171）。`is_allowed`（channel_manager/base.py:173-190）实现 allow_from 白名单，还专门处理 `sender|extra` 竖线分隔的复合 sender。IM 九平台走这条线（各自持有平台 SDK/webhook 长连接，send 直接调平台 API）。
- **BaseWebChannel → BaseWsChannel 线**：`BaseWebChannel`（`channel_manager/base.py:218-284`）在直系上加连接钩子与握手鉴权——`on_connect`/`on_disconnect`（channel_manager/base.py:229-233）、`set_handshake_auth` + `authenticate_handshake`（channel_manager/base.py:238-253）、`unauthorized_handshake_response` 兼容新旧 websockets 两代 `process_request` API 的 401 构造（channel_manager/base.py:269-284，参数首项是否为 str 区分新旧签名）。`BaseWsChannel`（`routing/base_ws_channel.py:32`，物理放在 routing 包但逻辑归属渠道体系）再叠加 **ws 反查体系**：五维 `_clients_by_key: dict[RoutingKey, list[ws]]` 逻辑索引 + `_ws_by_id`/`_id_by_ws` 物理双向映射（routing/base_ws_channel.py:48-51）。WebChannel（`web/web_connect.py:192`）与 TuiChannel（`tui/tui_channel.py:41`）是它的两个子类。

**TuiChannel 是"宿主/出站分离"的范本**。模块 docstring（`tui/tui_channel.py:3-13`）把定位写透：GatewayServer 仍是 `/tui` ws 宿主 + 入站帧解析 + local handler 派发；TuiChannel 继承 BaseWsChannel 只负责出站 send（按 `delivery.ws_id` 物理寻址 / 五维 routing_keys 精确查）+ 被 GatewayServer 委托 register_ws/unregister_ws 维护五维索引；**不起端口**（`start()` 仅标记 running，tui_channel.py:65-68）。这样 tui 出站与 web 出站共用同一套 `_ws_by_id + _clients_by_key` 反查机制，"消除「GatewayServer 既是 ws 宿主又是 Channel」的架构断裂"。委托机制的上游在 `app_gateway.py` 的 `RouteConfig.ws_channel` 字段（app_gateway.py:713-718）与 `tui/tui_connect.py:399-402` 的 `ws_channel` 绑定参数。

**ChannelManager 的注册表**（`channel_manager.py:60`）以 `ChannelKey(channel_id, app_id)` 为键（channel_manager.py:131），这是多应用的第一道支持：同一 `channel_id="feishu"` 可挂多个 app 实例。查找分三档：`get_by_key` 精确（channel_manager.py:331）、`_get_channel_by_id` O(n) 扫描取第一个（channel_manager.py:89-94，注释自称"渐进式兼容用"）、`get_channels_by_id` 全量（channel_manager.py:349-355，fan-out 用）。配置面带**单调递增 revision**（`_conf_revisions`，channel_manager.py:66-71 注释解释：把"回调失败的写入"也计入版本，后台重试用它区分自己的 reset-to-empty 与用户改配置）；`set_conf` 失败回滚 `_config` 快照（channel_manager.py:388-394）；`mark_channel_restart_pending`（channel_manager.py:96-105）支持"配置 diff 不变但内存凭据已变"（微信解绑场景，channel_manager.py:73 注释）的强制重启。

## 三、外部连接

- **上游 MessageHandler**：`_on_channel_message`（channel_manager.py:107-126）是所有渠道入站的总漏斗——同步签名回调转 `asyncio.create_task(handle_message)`，注释（channel_manager.py:110-112）点明保持同步是为避免飞书 webhook 这类旧调用方产生 "coroutine was never awaited"；channel 已注销的消息直接取消（channel_manager.py:122-124）。它还透传 `feishu_create_time` 用于度量"飞书侧创建→我方收到"的投递延迟（channel_manager.py:113-121），排查延迟补推旧消息造成的幽灵 /join。
- **下游 ws/平台**：WebChannel 19000 端口独立服务；TuiChannel 无端口；IM 各平台长连接；protocol/ 下 a2a、web_proxy 是对外 HTTP/WS 面。
- **附件落盘钩子** `_try_wire_file_persist_hook`（channel_manager.py:150-271）是本包最重的方法：给支持 `set_file_persist_hook` 的 IM 渠道注入"附件落盘到目标 AgentServer"的钩子。三条硬决策写进注释：①AgentOS 多用户路由未实现时装**明确失败的 hook**（channel_manager.py:175-182），绝不让 FileService 回退到 Gateway 部署目录；②小附件 base64 E2A（`IM_FILE_PERSIST`）、大附件分块上传（`FILE_UPLOAD_CHUNK` 2MB/块），因为超限 base64 帧会超过内部 WS 8MB 帧限制、`PayloadTooBig` 会**击穿整个 Gateway↔AgentServer 连接**（channel_manager.py:206-210）；③上传失败按可重试错误抛出、绝不回退本地落盘（决策 D6，channel_manager.py:230-236）。企业飞书多 bot 的 `feishu_enterprise:<bot_key>` 冒号被投影为安全目录名（channel_manager.py:190-193）。
- **连接事件订阅**（channel_manager.py:285-313）：`ChannelEvent`（channel_manager.py:26-32）只有 connected/disconnected 两态，供上层（如桌面端 UI）订阅。

## 四、数据流

**出站派发循环 `_dispatch_robot_messages`**（channel_manager.py:419-591）是全包的心脏，每 1s 超时轮询消费 robot_messages，四段分发顺序不能乱：

1. **文件 fan-out 注入**（channel_manager.py:448，`_inject_file_delivery_fanout` channel_manager.py:618-701）：`chat.file`/`chat.media` 默认只到发起 channel，team 模式下其他 /join 渠道收不到。注入算法三级：上游显式 `fan_out_targets` 不干预（channel_manager.py:640-642）→ `send_file_targets` 显式目标只走 **mention 精确定向**（channel_manager.py:660-682，注释解释为什么不能追加 godview intent：dispatch 层 godview 是全 session 广播，点名 ["feishu"] 会顺带发给 web godview）→ 自动模式发起者优先（`get_session_last_originator` 定向到最近人类发起者，无人则仅 godview 不误投 feishu，channel_manager.py:683-694）。
2. **fan_out_targets 分发**（channel_manager.py:450-491）：本进程产出的目标直接挂 `LogicalTarget` 对象、跨进程 E2A 过来的 dict 按字段重建（channel_manager.py:455-469）；`dispatch_to_session` 带 15s 超时（channel_manager.py:473-478），超时**跳过该消息继续循环**而不是卡死派发（channel_manager.py:479-484）。
3. **飞书 cron/心跳 fan-out**（channel_manager.py:493-540）：普通飞书多 app 共享 channel_id，精确路由只到创建 app；此分支清掉创建 app 的七个身份 metadata 键（feishu_chat_id 等，channel_manager.py:520-525）让各 app 回退到自己的 `last_*`。企业飞书明确**不进**此分支（channel_manager.py:498-500 注释：其一 channel_id 一 bot 无需 fan-out，且其 cron 绑定的是建任务时的特定群，清掉会误投）。
4. **单 channel 兜底**（channel_manager.py:542-583）：先 `resolve_app_id` 精确 `ChannelKey` 路由（channel_manager.py:545-552），miss 再 O(n) 扫描（channel_manager.py:553-554）；投递失败的 cron 推送（`cron-push-` 前缀）转 `_notify_cron_delivery_error`（channel_manager.py:577-578，channel_manager.py:593-616）经 web channel 发 chat.error 告知前端。

**WebChannel.send 的广播例外清单**（`web/web_connect.py:1070-1151`）展示了"精确路由为默认、广播为例外"的纪律：health_check relay 广播（探活是全局态，web_connect.py:1093-1107）、cron 推送按 `job.user_id` 限定接收者、空 user_id 历史任务保持广播（web_connect.py:1109-1131）、proactive_notification 系统提醒广播（web_connect.py:1133-1151）——每个广播分支都带完整的"为什么按 session 路由会被丢弃"的因果注释。TuiChannel.send（`tui/tui_channel.py:81-122`）有对称的 cron 广播分支，识别条件是 `CHAT_FINAL + payload.cron`，注释（tui_channel.py:94-103）解释了 scheduler 对 tui 置空 session_id 的原因（TUI 重启后旧 session 与新不同会被前端过滤）。

## 五、设计决策与权衡

1. **五维索引 vs 简单 channel_id 字典**：`_clients_by_key` 以 RoutingKey（channel/user/session/agent_ref 等五维）为键换来精确投递与多 session 共存——`register_ws` 默认 `evict_previous=False`（routing/base_ws_channel.py:95-107），一个 ws 可挂多个 session 桶（Web 多 tab 语义），投递精度由 `delivery.ws_id` 物理寻址保证而不依赖摘链；只有显式窗口级切换（`\new_session`、ACP 单用户）才摘链。代价是 register/unregister 要全表扫描（base_ws_channel.py:156-163）。
2. **ChannelKey 二元组 vs channel_id 字符串**：多应用（一个 feishu 多 app、企业飞书多 bot）迫使键升级，但保留 `_get_channel_by_id` O(n) 兼容路径——"渐进式兼容"（channel_manager.py:90）的诚实标注说明迁移未完，新代码必须用 `get_by_key`。
3. **钩子注入用 duck typing**（`getattr(channel, "set_file_persist_hook", None)`）：不强推基类接口，老渠道零改动即可获得新能力；代价是能力发现靠运行时反射，grep 静态分析看不见。
4. **渠道配置的 revision 机制**（channel_manager.py:66-71/379）：看似多余的单调计数解决了真实竞态——后台重试睡着期间用户改了配置，revision 对比防止重试覆盖用户意图。这是"状态同步问题用版本号而非锁"的典型解。
5. **protocol 外部化**：把 Message/wire codec 抽到独立 `openjiuwen-protocol` 包（git 依赖钉 commit），Gateway 与 AgentServer 两侧共享同一协议定义，避免双侧各写一份解析器漂移；本包 `protocol/` 只留连接适配，空 `__init__.py` 是"这里没有协议定义"的无声声明。

## 六、新人提示与坑

- **加新 IM 渠道**：在 `ChannelType` 枚举（channel_manager/base.py:26-40）注册只是第一步；还要在 `message_handler.py` 的 `_control_channel_types`/`_session_map_channel_types` 集合里决定是否纳入控制指令与 SessionMap 体系（feishu 的教训见 message_handler.py:403-408），以及 `_try_wire_file_persist_hook` 的 duck typing 面是否实现 `set_file_persist_hook`。
- **改 `send()` 先查广播例外清单**：WebChannel/TuiChannel 的 send 里每个提前 return 的广播分支都有存在理由（cron/心跳/proactive/health_check），删掉任何一个对应消息会静默消失；新增"无 session 的后端主动推送"大概率要加新分支而不是走通用路径。
- **`_dispatch_robot_messages` 的循环体异常只 log 不退出**（channel_manager.py:586-591）：这是刻意的健壮性——单条消息处理炸了不能停整个出站管道；但也意味着 bug 会以"某些消息没到"的形式隐匿，出问题时看 `[ChannelManager] dispatch loop iteration error` 日志。
- **feishu 与 feishu_enterprise 是两个世界**：前者多 app 共享 channel_id 需要 fan-out 清身份，后者一 channel_id 一 bot 且 cron 群绑定不可清（channel_manager.py:493-500 注释整段都在划这条界）。
- **文件投递的 mention/godview 语义**（channel_manager.py:655-694）：godview intent 在 dispatch 层等于"全 session 广播"，把它与 mention 混用会造成跨渠道泄漏——显式目标永不追加 godview 是写死的规则。
- **`BaseChannel.send` 基类默认实现是丢弃 + warning**（channel_manager/base.py:167-171）：新渠道忘实现 send 不会有类型错误，只有运行时消息黑洞，冒烟测试必须覆盖出站方向。
