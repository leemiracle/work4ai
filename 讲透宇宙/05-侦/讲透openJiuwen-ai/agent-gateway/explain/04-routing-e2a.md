# 04 · routing：五维路由键、DeliveryTarget 工厂与 e2a_proxy 统一转发面

> 锚定 commit `7af202253`。行号指 `agent_gateway/routing/` 下各文件，另注者除外。

## 一、角色定位

routing 包是 Gateway 的**寻址层**：它回答两个问题——"这条消息在逻辑上属于谁"（RoutingKey 五维）与"物理上送到哪里"（DeliveryTarget 各渠道子类）。同时它还托管 `e2a_proxy.py`——Gateway→AgentServer 的**统一薄代理**，把 Web/TUI/IM 入口的用户业务请求经 E2A 协议转发到目标 AgentServer（模块 docstring `routing/e2a_proxy.py:1-21`）。包内 17 个文件里，`keys.py` 是值对象层、`session_sharing.py` 是订阅/反查层、`base_ws_channel.py` 是 ws 渠道共享基类（见 03 篇）、`agent_client.py` 是上游 WebSocket 客户端、其余（session_map、interaction_context、mcp_remote、session_metadata_remote、container_files、agent_http_bridge、third_agent、agent_request_timeout、route_binding）各管一条专项通道。

e2a_proxy 的身份约束写得很硬（e2a_proxy.py:7-16）：Gateway 不直接读写用户态文件、不保留依赖用户 `.jiuwenswarm` 的业务逻辑；目标 AgentServer 不可达时返回可重试错误 `SERVICE_UNAVAILABLE`（e2a_proxy.py:48），**禁止**用部署侧目录代替用户目录执行；user_id 只用于路由/观测关联。这组约束是拆分部署后"Gateway 无状态化"的宪法条款。

## 二、内部结构

**RoutingKey 五维**（`routing/keys.py:18-46`）：`(user_id, channel_id, app_id, agent_ref, session_id)` 的 frozen dataclass，docstring 注明通配符 `'*'` 为监管等高级场景预留、主干路径全用精确值。它派生两个投影：`channel_key` 属性 → `ChannelKey(channel_id, app_id)`（keys.py:31-33，ChannelManager 注册表的键）；`identity` 属性 → `IdentityKey` 三元组（keys.py:35-37，SessionSharingRegistry 按 user 反查用）。`AgentRef` 本体在 `openjiuwen_protocol.e2a.agent_models`，此处仅转发保持引用稳定（keys.py:10-12 注释：source of truth 在 common/schema/agent）。

**DeliveryTarget 家族**（keys.py:72-293）：物理投递地址基类只有两个抽象面——`container_kind`（容器类型："ws"/"cli"/"group"/"p2p"）与 `get_container_id()`（keys.py:86-88，物理容器去重标识，用于同容器合并投递）。12 个 frozen 子类覆盖 13 个 channel_id：Web/Tui 用 `ws_id`（keys.py:94-119）、Acp 用 `request_id`（keys.py:122-133）、Xiaoyi 五字段双通道（agent_id/push_id/xiaoyi_session_id/conversation_id/url_key，keys.py:136-160，注释逐字段对齐小艺真实消息样本，去重主键选 per-user 稳定的 agent_id 而非随请求可能为空的 push_id）、飞书与企业飞书**共用** `FeishuDeliveryTarget`（keys.py:166-181，按 channel_id 区分，群/私聊用 chat_type）——这就是"12 子类覆盖 13 channel_id"的由来；其余 wecom/dingtalk/telegram/discord/slack/whatsapp/wechat 各自按平台语义定义（telegram 用 chat_id 正负区分群私聊 keys.py:225-227，whatsapp 用 jid 后缀 `@g.us` 判群 keys.py:276，slack 用 `channel:thread_ts` 复合容器 id keys.py:263-265，wechat 仅私聊 keys.py:284-290）。

**工厂 `make_delivery_target`**（keys.py:299-379）：按 channel_id 分发构造，公共入参（chat_id/receive_id/physical_user_id/ws_id）+ 渠道私有 kwargs；飞书分支还做群/私聊推导（`chat_type="group" if chat_id else "p2p"`，keys.py:331）与 receive_id 回退链（keys.py:333）；未知渠道 fallback 到 WebDeliveryTarget 并注释"不推荐"（keys.py:378-379）。

**逻辑/物理目标两级**（`routing/session_sharing.py`）：`LogicalTarget`（session_sharing.py:73-84）是线协议概念——intent（godview/mention/private）+ mention_all + member_names + speaker，**不含任何物理寻址**；`RoutingTarget`（session_sharing.py:92-115）是 Registry 反查后的聚合结果——routing_keys 升级为 list（V2 容器级聚合多成员）、`mention_member_ids` 装物理 @ 用户 ID（飞书 open_id/企微 userid）、`delivery` 与 routing_keys 配对。两者靠 `from_logical` 衔接（session_sharing.py:108-115）。订阅侧 `Subscription`（session_sharing.py:40-70）以 sub_id 为精确单位、同一 member 可多设备多条；`SessionSharingRegistry`（session_sharing.py:128-146）纯内存 + asyncio.Lock，**Gateway 重启需重新 /join**（session_sharing.py:141 注释）。订阅角色二分（session_sharing.py:25-37）：GODVIEW 上帝视角收全部消息，MEMBER 只收 @mention 自己的。

**request_id 撞号防护**是这条链上的精密件：`WebSocketAgentServerClient` 以 request_id 为路由响应的唯一键，同一连接两个在途请求撞号时拒绝注册第二个队列并抛 `DuplicateRequestIdError`（`agent_client.py:56-69`，docstring 钉死安全性依据：拒绝发生在**发送之前**、AgentServer 零副作用，换号重试安全；不换号会"mis-route responses, e.g. stream chunks to unary waiters"）。`_new_fetch_request_id`（`e2a_proxy.py:52-67`）解释了为什么不能只用 `time.time_ns()`：Windows 墙钟实测只有 100ns 步进且非单调（NTP 校正/休眠回拨会重放旧值），归档等长耗时 RPC 与 2s 轮询共用连接时撞号直接表现为偶发失败——方案是时间戳前缀 + 8 位随机量后缀。

## 三、外部连接

- **上游**：`agent_client.py` 的 `WebSocketAgentServerClient`（ping_interval 20s/ping_timeout 600s，见 app_gateway.py:1989）；扩展可替换为 `AgentOSRouterClient`/`AdxRouterClient`——`is_agentos_routing_client`（e2a_proxy.py:70-86）刻意用"稳定的模块/类名字符串"判定而不是 import 扩展类型，注释（e2a_proxy.py:72-76）说明这是为了不让常规单用户安装依赖可选扩展。
- **下游 Channel.send**：`base_ws_channel.py` 的 send 消费 RoutingTarget（见 03 篇）；IM 各渠道 send 消费各自的 DeliveryTarget 子类（isinstance 判别，keys.py:77）。
- **per-ws writer 512 帧背压**（`base_ws_channel.py:27-29`）：`_SEND_QUEUE_MAX_FRAMES = 512` 是 per-ws 出站队列硬顶——注释写明"writer 正常时队列几乎恒空；触顶说明对端已停止读取，继续排队只堆内存。丢弃并告警（停滞 transport 由写停滞看门狗回收，issue #4946）"。配套机制全在同一文件：register_ws 时建队列并起常驻 writer（base_ws_channel.py:116-120）、`_enqueue_send` 非阻塞入队 + QueueFull 丢帧告警（base_ws_channel.py:249-267）、`_writer_loop` 串行 send 保序且单帧 10s 超时只丢该帧不杀 writer（base_ws_channel.py:269-327，注释解释杀 writer 会留下无人排水的无界队列，后续 unary res 帧永远到不了 TUI）、`_coalesce` chunk 合并扩展点（base_ws_channel.py:329-335）、`_drain_and_cleanup_writer` 先 flush 残余帧再退出的收尾顺序（base_ws_channel.py:337-368）。
- **超时策略**：`agent_request_timeout.py:11-17` 定义 `AGENT_SERVER_TIMEOUT_CODE` 与 TUI 专属三档（默认 25s/上限 55s/客户端宽限 5s），`resolve_agent_request_timeout_seconds`（agent_request_timeout.py:72）按 method 分档，豁免方法集在 agent_request_timeout.py:39。
- **reasoning_injector 五路径咽喉**与转发面交汇于模型配置：Gateway 校验路径经 `common/model_routing_registry.py:87` 调 `build_reasoning_model_request_kwargs`（`common/reasoning_injector.py:145`，其 docstring 点名 AgentServer/Gateway validation/TUI validation/AgentOS/team models 五消费方），改模型构造参数时这条统一转发面上的五条路径要一起回归。

## 四、数据流

**unary 转发主路径 `proxy_unary_request`**（e2a_proxy.py:99-227）：①可达性检查——`agent_client is None` 或显式 `server_ready is False` 才判不可达（e2a_proxy.py:140-143 注释：兼容扩展客户端不暴露 server_ready，只有显式 False 才算传输不可用），回 `SERVICE_UNAVAILABLE`；②params 清洗——drop_params 剔除内部字段（如内部 session_id）、extra_params 追加（如 create_token）、独立 user_id 非空时移除 params 里重复的 user_id 防止适配器遍历时意外吸入用户身份（e2a_proxy.py:153-162）；③`e2a_from_agent_fields` 构造 E2AEnvelope（e2a_proxy.py:164-173，user_id 经 envelope 承载、是路由/观测唯一权威）；④`send_agent_request_with_timeout` 发送（e2a_proxy.py:175-180），超时回 `AGENT_SERVER_TIMEOUT`（e2a_proxy.py:181-189）、其它异常回 `SERVICE_UNAVAILABLE`（e2a_proxy.py:190-205）；⑤成功后先跑非阻塞 `on_done` 维护回调（连接预热/watcher 唤醒，失败只 warning 不影响业务，e2a_proxy.py:212-218），再 `channel.send_response` 按原外部协议回写——error/code 映射规则保持各入口迁移前的外部协议 code 不变（e2a_proxy.py:219-226，`default_error_code="BAD_REQUEST"` 兜底）。返回 True 表示"已回写"，调用方不用再发。

**Gateway 主动发起的 `fetch_agent_unary`**（e2a_proxy.py:230-326）：不回写通道、返回 `(ok, payload)` 供桥接场景自行决策（Git watch 快照、IM 附件落盘都走它）。与 proxy 版的关键差异在撞号重试：`for attempt in (0, 1)` 循环内每次**重新生成** request_id（e2a_proxy.py:257-259），`DuplicateRequestIdError` 第一次换号重试、第二次放弃（e2a_proxy.py:281-296），注释（e2a_proxy.py:255-256）说明不做这层重试的话"id 生成器偶发重复会直接变成用户可见的失败"。失败 payload 自带整数 `status` 时一并转发（e2a_proxy.py:322-324）。专用封装还有两个：`resolve_agent_cron_project_binding`（e2a_proxy.py:329-351，docstring 钉死 Gateway 是 cron job-store 属主、只持久化目标 AgentServer 返回的绑定、绝不探测自己的部署侧项目库）与 `fetch_git_diff_status`（e2a_proxy.py:354-388，Git 轮询与 /ws/git 首次快照共用同一构造）。

**出站寻址两级**（base_ws_channel.py:196-245）：`send(msg, routing_target)` 优先按 `delivery.ws_id` 物理寻址 `_ws_by_id`（base_ws_channel.py:215-222，V2 §3.1 职责分界），miss 才按 routing_keys 五维查 `_clients_by_key`（base_ws_channel.py:224-230），仍未命中且子类开启广播兜底才广播（base_ws_channel.py:232-236，默认关闭）。命中后 `_enqueue_send` 非阻塞入队即返回（base_ws_channel.py:241-245，dispatch loop 不 await IO）。

## 五、设计决策与权衡

1. **逻辑/物理两级目标的强制分离**：LogicalTarget 不含物理寻址、AgentServer 能从 interaction.payload 直接得知；RoutingTarget 才装 RoutingKey/DeliveryTarget。这使跨进程传输的目标描述（dict 形态）永远不携带 Gateway 内部索引，重建即可（channel_manager.py:455-469 的 dict→LogicalTarget 重建正是吃这个红利）。
2. **frozen dataclass 全家**：RoutingKey/DeliveryTarget/Subscription 全部 frozen——五维键要当 dict 键用，可变性会破坏索引；DeliveryTarget 子类带默认值又是 frozen，构造即终态，杜绝"改一半的地址"。
3. **撞号"预防+自愈"双层**：预防靠 `_new_fetch_request_id` 的随机后缀（时间戳只保排序不保唯一）；自愈靠 fetch 路径的一次换号重试。两层都建立在"拒绝发生在发送前"这一前提上——如果未来改客户端把注册队列挪到发送后，重试就不安全了，这个前提必须跟着 `DuplicateRequestIdError` 的 docstring 一起维护。
4. **512 帧丢帧优于无界排队**：对端停止读取时（CLOSE-WAIT 前兆），丢帧 + 告警 + 交给写停滞看门狗回收（06 篇）比把内存堆爆诚实得多；单帧 10s 超时只丢该帧不杀 writer，是因为杀 writer 的代价（unary res 永不到达、客户端报 request timeout 而 AgentServer 一切正常）比丢帧更难排查（base_ws_channel.py:305-315 注释原文场景）。
5. **薄代理不做业务**：proxy_unary_request 里唯一的"业务"是 on_done 维护回调且显式声明失败不影响请求（e2a_proxy.py:128-131）；Gateway 侧任何想做"顺手处理一下响应"的冲动都被这个边界挡住。

## 六、新人提示与坑

- **新增渠道要动三处**：`ChannelType` 枚举（channel_manager/base.py:26-40）+ `DeliveryTarget` 子类（keys.py，含 container_kind/get_container_id 语义）+ `make_delivery_target` 工厂分支（keys.py:299-379）。漏掉工厂分支会静默 fallback 到 WebDeliveryTarget（keys.py:379），字段全错但不会报错。
- **`get_container_id` 的去重语义**：同容器合并投递依赖它，slack 的 `channel:thread_ts` 复合键（keys.py:263-265）提示新渠道要想清楚"什么算同一物理容器"。
- **fetch_agent_unary 的重试只救撞号**：普通异常（e2a_proxy.py:297-305）与超时（e2a_proxy.py:276-280）都不重试、直接返回失败——调用方（如 Git watcher）要有自己的退避。
- **改 timeout 常数先读 `agent_request_timeout.py` 的三档关系**（25/55/5s）：TUI 客户端自身超时 < Gateway 侧超时的关系是调好的，单独改一处会出现"客户端已放弃、Gateway 还在等"的空转。
- **SessionSharingRegistry 是纯内存**（session_sharing.py:141）：Gateway 重启后所有 /join 席位消失，依赖共享会话的自动化流程要有重新 join 的预案；排查"重启后 mention 不投递"先想到这里。
- **不要在 e2a_proxy 里加用户目录逻辑**：e2a_proxy.py:8-10 的禁令配合 `SERVICE_UNAVAILABLE` 可重试语义是这个代理的立身之本，历史教训都浓缩在 docstring 引用的方案 §4/§6/§8 里。
