# 02 · message_handler.py：5821 行消息中枢——双队列、164 方法与单例的命运

> 锚定 commit `7af202253`。本文行号均指 `agent_gateway/message_handler/message_handler.py`，另注者除外。

## 一、角色定位

`MessageHandler` 是 Gateway 进程的**消息总线与协议翻译官**，站在所有 Channel（web/tui/acp/feishu/dingtalk/…）与 AgentServer 之间。类 docstring（`agent_gateway/message_handler/message_handler.py:315-327`）一句话讲清拓扑：维护两个异步队列——`_user_messages` 收 Channel 来的消息、由内部转发循环消费并调 `agent_client.send_request`；`_robot_messages` 收 AgentServer 的响应、由 ChannelManager 消费派发到对应 Channel。协议侧 AgentServer 下行的是 **E2AResponse** 线 JSON，由 `WebSocketAgentServerClient` 里的 `wire_codec` 还原为 `AgentResponse`/`AgentResponseChunk`（message_handler.py:321-323），本类再经 `_response_to_message`/`_chunk_to_message` 转成 Channel 消费的 `Message`——所以它同时是队列管理器、流任务调度器和 E2A→Message 反向翻译器三层角色叠加。

它是 `ABC`（message_handler.py:314）却又是**进程级单例**：`__new__` 缓存 `cls._instance`（message_handler.py:331-334），`__init__` 用 `_singleton_initialized` 挡重复初始化（message_handler.py:337-339），`get_instance()`（message_handler.py:502-514）在未创建时强制要求传入 client、否则抛错，另配只读的 `try_get_instance()`（message_handler.py:517-519）。装配方 `app_gateway.py` 先 `MessageHandler(client)` 再 `start_forwarding()`，之后 ChannelManager 等子系统都经单例取它。

## 二、内部结构

**状态面（message_handler.py:336-437）是理解全类的钥匙**，粗分六组：

1. **双队列**（message_handler.py:349-350）与转发任务 `_forward_task`、`_running` 标志（message_handler.py:351-352）。
2. **流式任务账本**——足足 11 个以 request_id 为键的 dict：`_stream_tasks`/`_stream_channels`/`_stream_sessions`/`_stream_team_ids`/`_stream_metadata`/`_stream_user_ids`/`_stream_modes`/`_stream_emits_processing_status`/`_stream_methods`/`_stream_app_ids`（message_handler.py:353-376）。`_stream_user_ids` 的注释（message_handler.py:358-360）点明动机：AgentServer 的 server_push 帧只带 request_id，认证属主必须在发起时留档，cron 变更与反向 E2A 才能路由回正确用户。`_stream_methods`（message_handler.py:363-366）是 processing_status=false 守卫的依据——只有 `chat.send(emit=True)` 与 `command.goal` 长流可挡住补发，`history.get` 等短只读流不得挡。非流式 chat 另立 `_active_chat_tasks`/`_non_stream_chat_tasks`/`_non_stream_chat_messages`/`_non_stream_chat_locks` 四件套（message_handler.py:367-374），因为非流式 chat 不产生 processing_status 但同样占用"配置保存锁"语义。
3. **server_push 串行锁** `_server_push_lock`（message_handler.py:378）。
4. **会话辅助表**：`_session_last_user_query`、`_session_last_originator`（team 模式 file msg 定向投递兜底，message_handler.py:383-387）、ACP 双向别名表 `_acp_session_aliases`/`_external_session_aliases`（message_handler.py:388-391）。
5. **渠道控制态**：`_control_channel_types` 六平台集合（message_handler.py:395-402）、`_channel_states`（message_handler.py:413）、小艺 sticky 态 `_sticky_channel_state_types` + `_pending_alloc_state_key`（message_handler.py:417-418）、`SessionMap`（message_handler.py:419，落盘 session_map.json 支持跨进程重启复用）、`SessionSharingRegistry`（message_handler.py:420）、`JoinExitHandlers` 组合（message_handler.py:422，注释明示"独立文件维护，通过 self._h 访问宿主能力"——5821 行里唯一被拆出去的逻辑）。
6. **可选管线**：IM 数字分身双 pipeline（message_handler.py:425-427，None 时不执行、零影响）与 GatewayHookHandler（message_handler.py:429-437，初始化失败降级为 None 继续跑）。

**延迟导入策略**：全文件仅 33 条顶层 import，函数体内的延迟 import 多达 66 处（约 2:1）——`openjiuwen_protocol.message` 的 `Message/ReqMethod/EventType` 几乎每个大方法开头 import 一遍（message_handler.py:753、message_handler.py:1336、message_handler.py:4617…），重依赖如 cron scheduler（message_handler.py:3542）、video_duplex bridge（message_handler.py:3322）、slash_command（message_handler.py:2310）全部进函数。这是刻意的冷启动换内存策略：单例在进程装配早期就要建（`app_gateway.py:2013`），不能让它把十三渠道的重依赖全拖进来。

**方法面**：164 个方法（含 property），核心循环只有两个——`_forward_loop`（message_handler.py:4610）消费 user 队列，`_handle_agent_server_push_ordered`（message_handler.py:3304）处理下行 push；其余几乎全是为这两个循环服务的预处理器、守卫和账本操作。

## 三、外部连接

- **上游 AgentServer**：经 `agent_client` 发请求；`_register_agent_server_push_handler`（message_handler.py:472-480）把 `self._handle_agent_server_push` 注册进 client 的 `set_server_push_handler`，从此 push 帧绕过 RPC 队列直达。
- **下游 ChannelManager**：`set_channel_manager`（message_handler.py:2739）回填引用；`_dispatch_robot_messages`（channel_manager.py:419）消费 `consume_robot_messages`（message_handler.py:2780-2792）按 channel_id 投递。
- **cron 子系统**：`set_cron_controller`（message_handler.py:3533）+ `_handle_cron_push_payload`；cron 变更走 server_push 而非 RPC 响应（message_handler.py:3378-3379 注释）。
- **凭据体系（credential_ref 绑定）**：登录模型配置里只放 `credential_ref` 句柄，AgentServer 按句柄登记 id_token、发请求时才换真 token（`agent_gateway/auth/passthrough.py:56-60`）。token 过期续期后 AgentServer 会主动 push 刷新事件，`_handle_login_credential_refresh_push`（message_handler.py:3254-3269）从 payload 取 `credential_ref`、在 `asyncio.to_thread` 里调 `refreshed_credential_for_ref`（passthrough.py:89，注销/续不了时返回 `revoked: True` 让 AgentServer 弃用）。
- **配置面板的 Web/TUI 契约三处分叉**：`common/config_panel/__init__.py:4-10` 钉版——`models_handlers`（Web models/config 域）、`config_set_handlers`（Web config.set/save_all 域）、`tui_models_handlers`（TUI 侧 config 域，Auto-Harness 等专属字段）按通道分模块保留，**两侧同名 RPC 契约不一致，禁止合并实现**。MessageHandler 是这三套 handler 的公共宿主，动它时必须想到两套契约都在桌上。
- **hooks/扩展**：`UserPromptSubmit`（message_handler.py:4686-4696）、`BEFORE_CHAT_REQUEST`（message_handler.py:4072）两个注入点；evolution 审批协调器 `EvolutionApprovalCoordinator`（message_handler.py:379）+ 预解析的 `_evolution_auto_save_enabled`（message_handler.py:380-382，注释强调流式 chunk 热路径读内存值、不读盘）。

## 四、数据流

**入站主线 `_forward_loop`（message_handler.py:4610-5138）**是一条精心排序的流水线，顺序即语义：①`consume_user_messages(timeout=None)` 阻塞取消息（message_handler.py:4622，stop 时 cancel 打断 get）；②IM session input 归一化（message_handler.py:4629）；③受控通道控制指令拦截（`/new_session`、`/mode`、`/skills`，message_handler.py:4639-4641，命中即回复不再转发）；④外部渠道会话解析 → 渠道态应用 → 入站会话确保（message_handler.py:4644-4646）；⑤**busy-session 改道**：IM 的 chat.send 没有 steer 控制，处理中的 Session 来新消息就并入当前轮（`steer_busy_im_chat`，message_handler.py:4651-4659）而不是取消重开；⑥team 模式守卫——mode 只有在 `_apply_channel_state` 之后才可知，所以 unknown team mode / 非流式 team send 的拒绝必须卡在 GodView 注册**之前**（message_handler.py:4670-4679 注释：否则会为一个永远不会跑的轮订阅事件）；⑦GodView 注册（message_handler.py:4684）；⑧UserPromptSubmit hook（message_handler.py:4686）；⑨内容增富——附件解析、`@文件` 引用、`@agent-xxx` 提及转 `<system-reminder>` 提示注入（message_handler.py:5041-5083）；⑩`_prepare_agent_dispatch_message` → hook 快照对比 → `message_to_e2a`（message_handler.py:3103 静态方法）转 E2AEnvelope；⑪三分流（message_handler.py:5118-5138）：流式起后台任务不 await（注释 message_handler.py:5124：让流式任务后台跑、循环继续处理下一条）、非流式且非聊天 RPC 并行后台跑（message_handler.py:5125-5136，避免慢 RPC 如 SkillNet 阻塞队列）、其余非流式 chat 走 `_start_non_stream_chat_task`。

**流式生命周期**：`_start_stream_task`（message_handler.py:5488-5530）先写完全部账本（emit 标志、team_id、method、mode），必要时发 processing_status 事件，再 `asyncio.create_task(process_stream(...))` 并登记 6 张表；`_pop_stream_tracking`（message_handler.py:1124）在流结束时按 rid 成对弹出。取消有两条路：用户 CHAT_CANCEL 直接 cancel 任务；AgentServer 经 server_push 发终止哨兵 chunk 时 `_is_terminal_stream_chunk` 分支（message_handler.py:3407-3425）必须主动 `task.cancel()`——注释（message_handler.py:3408-3412）解释了为什么不能只丢弃：否则 `process_stream` 协程仍挂在 queue.get() 上等更多 chunk，形成**僵尸流**，会话被生命周期守卫永久锁死。

**下行 push 串行处理**：`_handle_agent_server_push`（message_handler.py:3295-3302）先拿 `_server_push_lock` 再进 ordered 版本——docstring 一语道破："Serialize server-push handling so a final cannot overtake its deltas"（final 不得越过 delta）。ordered 内部是一个事件类型分发器（message_handler.py:3304-3453）：凭据刷新（message_handler.py:3314）→ models.updated 广播（message_handler.py:3327）→ video checkpoint（message_handler.py:3330）→ trajectory/diagnosis（message_handler.py:3333-3336）→ 会话完成回调（message_handler.py:3357-3361）→ 推荐事件（message_handler.py:3362-3373）→ **cron.response 属主校验**（message_handler.py:3378-3406）→ 终止哨兵（message_handler.py:3407）→ evolution（message_handler.py:3428）→ 兜底 `_chunk_to_message` 后 `publish_robot_messages`（message_handler.py:3443-3447）。cron 属主校验值得细读：Gateway 存活的 `_stream_user_ids[rid]` 与 wire metadata 里 CronTools 带来的 `_jiuwenswarm_cron_owner_user_id` **不一致即丢弃**（message_handler.py:3392-3397），宁可拒收也不让过期/畸形帧跨用户边界。多应用 push 还要重建 app_id（message_handler.py:3431-3442，注释详细解释了不补则 feishu 多 app 场景文件发错人的完整因果链）。

## 五、设计决策与权衡

1. **单例 + ABC 的别扭组合**是拆分部署的历史产物：母仓里多个宿主进程都要拿到"那个" MessageHandler，单例是最粗粒度的共享；代价是测试隔离差、隐式全局状态遍布 11 张流账本。`try_get_instance` 的存在（message_handler.py:517）说明代码自己也知道"可能还没有"。
2. **队列 vs 任务直发**：入站坚持走队列（顺序性 + 控制指令拦截点 + busy 改道点都在循环里），出站 robot_messages 队列则把 ChannelManager 与上游解耦。而**流式与并行 RPC 不入队**、直接 create_task——message_handler.py:5124/5126 的注释给出了明确理由：不让慢流/慢 RPC 阻塞队列里的其它请求。这是一条"队列保序、任务保吞吐"的分界线。
3. **processing_status 守卫的精确口径**（message_handler.py:2633-2656）：`_is_chat_stream` 只认 emit=True 的 chat.send；`history.get` 等只读流登记 mode 供取消/回填用但不计入运行态，"否则它们退出时会让保存锁计数悬空在最后一次广播值"。team 任务用隔离 `cron_*` 会话不受配置热更影响，所以配置保存锁只看非 team 任务（message_handler.py:2658-2671）。这类计数口径注释是本文件最值钱的部分。
4. **server_push 与 RPC 共线不共队**：message_handler.py:3305 docstring"与 RPC 共用连接但不得占用 unary/stream 等待队列"，配一把锁解决 final/delta 乱序——比开第二条连接省资源，比不加锁换正确性。
5. **热路径配置预解析**：evolution 自动保存开关在启动/热重载时解析一次存内存（message_handler.py:380-382），流式 chunk 路径零磁盘 IO——典型的读多写少配置优化。

## 六、新人提示与坑

- **这个文件改一处要 grep 全仓**。164 个方法共享 20+ 实例状态；尤其 11 张以 rid 为键的表必须成对写/成对删（`_pop_stream_tracking` message_handler.py:1124 是唯一合法的删除点之一），漏删一张就是内存泄漏 + 僵尸流。
- **顺序敏感的循环别重排**：`_forward_loop` 里控制指令 → 渠道态 → team 守卫 → GodView → hook → 增富 → e2a 的顺序各有前置依赖注释（如 message_handler.py:4670-4673），"顺手提前" GodView 注册就会为死轮订阅事件。
- **加新的 server_push 事件类型**必须放进 ordered 分发器且想清楚与锁的关系；乱序到达的 final 会直接破坏前端流渲染。
- **cron push 的属主双重校验是安全边界**（message_handler.py:3385-3397），不要图省事去掉 mapped_owner 与 pushed_owner 的一致性检查。
- **测试别依赖二次构造**：单例使 `MessageHandler(new_client)` 静默返回旧实例且 client 不更新（`__init__` 直接 return，message_handler.py:337-338），单测里换 client 必须显式清 `_instance`。
- feishu 会话查找的坑写在 message_handler.py:403-408 注释里：不走 SessionMap 时 `_apply_channel_state` 清空 session_id 后，`"feishu:None"` 与 `"feishu:oc_xxx"` 永远对不上，每条消息新建 session、丢上下文——改渠道类型集合前先读懂这段。
