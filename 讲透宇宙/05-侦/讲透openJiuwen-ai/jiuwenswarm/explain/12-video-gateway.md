# 12 双工视频扩展与 Gateway 渠道

> 对应导览 S15+S16。代表文件：`jiuwenswarm/extensions/video_duplex/`、`gateway/channel_manager/`、`gateway/app_gateway.py`、`jiuwenswarm/channels/web/`。

## 一、角色定位

本文覆盖接入面的两端。**video_duplex 是"应用插件如何挂进 server/gateway 双端"的标准样本**（tour-15 原话）：一个全双工实时音视频问答扩展，plugin_id="video-duplex"（video_duplex/extension.py:22-23，video_duplex/extension.yaml:2-6 声明 name/version/min_jiuwenswarm_version），经 `gateway.extensions.sdk` 的 ApplicationPluginExtension 契约注入 Web 渠道。**Gateway 渠道层**是所有消息的进出口：channel_manager 统一管理各渠道连接、robot_messages 分发循环、飞书 fan-out；web 渠道另有 app_web.py（2759 行）静态服务+反代与前端的 App.tsx（5151 行）应用外壳。两者共享"jiuwenswarm/ + gateway/ 双顶层包同根部署"的物理布局——pyproject.toml:181-184 的 packages.find `where=[".", "jiuwenbox/src"]`、`include=["jiuwenswarm*", "jiuwenbox*", "gateway*"]` 把两棵顶层树打进同一发行版。

## 二、内部结构

**video_duplex 插件四挂点**（extension.py）：`is_enabled` 读环境开关（默认 true，video_live.py:180-186）；`bind_web_channel` 注册 video.live 处理器并挂四个设置 RPC——video.duplex.settings.get/update/test/set_enabled，全部 `local_only=True, available_when_disabled=True`（video_duplex/extension.py:109-146），即插件禁用时设置页仍可配置；`websocket_routes` 贡献 Qwen-Omni 代理路由（video_duplex/extension.py:148-155）；`frontend_contributions` 贡献前端导航项，但 `render_mode="none"`——独立插件页刻意隐藏，配置迁到 Settings > Experimental（video_duplex/extension.py:157-170）。

**双 provider 双架构**：①Qwen-Omni 路线是**WS 认证中继**——`qwen_omni_gateway.py` 把浏览器 WS 帧直转阿里云 Qwen-Omni Realtime 上游（模块 docstring，qwen_omni_gateway.py:2），配置纯环境变量 QWEN_OMNI_REALTIME_URL/API_KEY/MODEL_NAME/VOICE（:32-38），validate 强校验 ws/wss scheme、拒绝 URL 内嵌凭据（:40-51），错误消息经 `_safe_upstream_error` 把 api_key 替换成 `******` 再截断 1000 字符（:73-77）——**api_key 永不出现在浏览器侧**。②JoyAI 路线是**HTTP completion + 原生语音 WS 混合**——joyai_provider.py 用 httpx 发 request_completion/request_frame（:160,198,227），带 JoyAIRateLimitError（:64）、parse_action 标记解析（:96）、response_language 指令（:121-139）；语音走"native JoyAI channel ASR/TTS WebSocket"（:77-78），客户端做 WAV↔PCM16 重采样（:248-300）；TTS 指令钉死普通话（繁体/港式用词先解释成简体普通话再读、1.2x 语速，joyai_provider.py:8-14）。模式切换由 `_video_live_mode()` 决定（realtime/joyai），video_search.VideoSearchManager 的 qwen_active 回调按模式联动（video_live.py:189-204）。

**checkpoint 协议两半分居（勘误级结构）**：任务修改协议被拆在两处——**契约半边**在 qwen_omni_tools.py 的工具描述里：jiuwen_task_modify 声明"queued 输入直接更新；running 的修改等待 model checkpoint；finished 工作创建 linked revision；**回执永远不证明需求已满足**"（qwen_omni_tools.py:276-289），配套 jiuwen_task_query 强调"query 是任务原文的字面子串而非问题；无匹配**不**证明完成或文件不存在"（:245-267）——认识论纪律全写进 prompt；**执行半边**在 tasks/checkpoint.py：TaskCheckpoint 挂 before_model/after_model 钩子，把需求变更施加到"精确的根 Agent model context"边界（video_duplex/backend/tasks/checkpoint.py:2,6-20,23,50），状态由 tasks/service.py 的 checkpoint_open 生命周期管理——任务转 running 时开 checkpoint（video_duplex/backend/tasks/service.py:658），变更落定后关（video_duplex/backend/tasks/service.py:749）。读这个协议必须两半对照，缺一半都会误判"modify 为什么没立即生效"。

**Gateway 渠道层**：`BaseChannel(ABC)` 定义 name/start/stop/send/is_allowed 契约（channel_manager/base.py:119-150），入站消息统一打 `ChannelMetadata(channel_id=self.name)`（channel_manager/base.py:202）。`ChannelType` 枚举 13 值：acp/web/feishu/xiaoyi/dingtalk/telegram/discord/slack/whatsapp/wecom/wechat/ssh/cli（channel_manager/base.py:26-40）。**子类账目**：BaseChannel 的具体直接子类 12 个——feishu/xiaoyi/dingtalk/telegram/discord/slack/whatsapp/wecom/wechat 九 IM + ssh + acp + a2a（各自 *_connect.py，如 feishu_connect.py:235、a2a_connect.py:273）；web 与 tui 不在其中，走 `BaseWebChannel`（channel_manager/base.py:218，加 connect/disconnect 钩子与握手鉴权）分支——web 由 `GatewayServer(BaseWebChannel)` 承担（app_gateway.py:748，channel_id="web" 硬编码于 :1850,:2466），tui 由 `TuiChannel(BaseWsChannel)`（tui_channel.py:41，`channel_id = "tui"` :49）。A2AChannel 虽占一个子类名额但 channel_id 是**配置动态覆盖**：`str(self.config.channel_id or self.name)`（a2a_connect.py:286），不占枚举位。`ChannelManager` 持 RoutingKey→channel 索引、dispatch 循环消化 robot_messages（channel_manager.py:119,558-588），普通飞书多 app 共享 channel_id 时精确路由到创建 app 并 fan-out（channel_manager.py:494-536）。

## 三、外部连接

插件 SDK 桥：video_duplex/extension.py:5-10 从 `gateway.extensions.sdk` import ApplicationPluginExtension/Services/FrontendContribution/WebSocketRouteContribution——**jiuwenswarm 包的扩展依赖 gateway 包的 SDK**，反向地 `jiuwenswarm/extensions/__init__.py` 以懒加载门面转出 gateway.extensions 的 Loader/Manager/Registry（"Extension public surface with transport adapters loaded lazily"）。GatewayServer 是多路路由 WS 网关：每条路径独立 channel_id 与本地 handler，本地优先、未处理才 forward 到 MessageHandler（app_gateway.py:749-754）；V2 路由 key 升级为 (channel_id, session_id, agent_ref) 三元组兼容旧 2-tuple（:765-767）；ACP 延迟绑定——握手期 session 先挂起，等首个 agent 请求 promote（:770-772）。web 渠道的 app_web.py 提供 SPA 静态服务（_SpaStaticHandler:311）与入口 main()（:2569）；前端 main.tsx 78 行装配 `A2UIProvider`（@a2ui/react，web/frontend/src/main.tsx:3,61）与 `installDesktopLocalFilesBridge`——"持久桌面拖放桥必须在 ChatPanel 挂载前存在"（web/frontend/src/main.tsx:14,20-21）。

## 四、数据流

视频问答流（Qwen 模式）：浏览器采集音视频帧 → WSS 连 `/ws/video/qwen-omni` → gateway 校验配置、把 model 参数拼进上游 URL（qwen_omni_gateway.py:53-58）→ 双向中继（_relay_browser_to_upstream:80-84 等）→ 上游错误脱敏后回传。设置流：前端 Settings > Experimental 调 video.duplex.settings.update → 插件本地校验（values 必须对象、clear_secrets 必须 bool，video_duplex/extension.py:56-81）→ settings.py 落盘 → test 走 check_saved_connection，失败只回固定文案不暴露 endpoint/key（video_duplex/extension.py:116-129）。Gateway 消息流：渠道 start 监听 → `_handle_message` 打 ChannelMetadata 入 bus → MessageHandler 消费 → 回复进 robot_messages 队列 → dispatch 循环按 channel_id 找订阅回调投递；web/tui 的 WS 客户端经 RoutingKey 五维索引精确寻址（base_ws_channel.py:32-40），出站队列 512 帧硬顶防对端停读堆内存（base_ws_channel.py:27-29，issue #4946）。

## 五、设计决策

①**插件可用性优先**：settings 四方法 `available_when_disabled=True`——禁用态仍可预配 endpoint/key，启用即用；`test_connection` 失败不回显任何 provider 信息（防凭据/拓扑泄漏）。②**凭据零下行**：Qwen 中继架构让 api_key 只活在服务端进程，浏览器只见脱敏错误。③**认识论写入工具描述**：modify/query 的"回执不证明满足/无匹配不证明不存在"把分布式任务的不确定性显式教给模型，配合 checkpoint 两半分居实现"running 任务的修改在模型边界原子生效"。④**渠道命名双轨**：类属性 name 是默认 channel_id，A2A 允许配置覆盖——支持多租户/多实例共用一个类；飞书 fan-out 是同 channel_id 多 app 的刻意例外（channel_manager.py:494）。⑤**双顶层包同根**：jiuwenswarm 与 gateway 互为依赖（extension 用 gateway SDK、extensions/__init__ 转出 gateway loader），打包同根保证 `pip install` 一次到位，代价是两包不可独立发布——重构拆包前必须先解开这两条交叉引用。

## 六、新人提示

- 写新应用插件照抄 video_duplex 四挂点骨架（extension.py 176 行是完整模板）：is_enabled/initialize/shutdown/bind_web_channel + websocket_routes + frontend_contributions；`register_extensions(registry)` 是被发现入口（video_duplex/extension.py:173-176）。
- 查"任务修改没生效"先看 checkpoint_open 状态（service.py），再看模型是否到了 before_model 边界——不是 bug，是协议设计。
- 加渠道：IM 类直接继承 BaseChannel 设 `name`；需要 WS/握手鉴权走 BaseWebChannel/BaseWsChannel；channel_id 要进 ChannelType 枚举得同步 channel_manager/base.py:26-40，A2A 式动态 id 则不必。
- 前端启动顺序坑：桌面文件桥必须先于 ChatPanel 安装（web/frontend/src/main.tsx:20-21 注释），挪动 main.tsx 结构前先读该注释。
- GatewayServer 的请求路由 key 是三元组，老代码写 2-tuple 兼容是刻意保留（app_gateway.py:765-767），别"顺手清理"。
