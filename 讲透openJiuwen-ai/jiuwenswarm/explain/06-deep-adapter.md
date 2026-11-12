# 06 Deep Adapter 适配层（tour S08）

## 一、角色定位

`server/runtime/agent_adapter/` 是 jiuwenswarm 的 server 层与 openjiuwen DeepAgent SDK 之间的桥。三个文件构成一个漏斗：**interface.py（6223 行）是统一门面**——对外只暴露 `JiuWenSwarm` 类，管 SDK 工厂路由、session 调度、Skills 路由、heartbeat、历史落盘与流式包装；**agent_adapters.py（159 行）是协议与工厂**——`AgentAdapter` runtime_checkable Protocol 定义八个必需能力，`create_adapter` 按环境变量分发实现；**interface_deep.py（22839 行）是巨物实现**——`JiuWenSwarmDeepAdapter` 封装 openjiuwen DeepAgent 的全部专属逻辑，改 agent 行为必经之路。

一句话概括分工：门面管"请求怎么排队与回执"，协议管"后端可替换"，巨物管"Deep SDK 的一切细节"。

## 二、内部结构

### agent_adapters.py：协议 + 工厂（159 行）

`AgentAdapter` Protocol（agent_adapters.py:24-96）定义八个必需能力：`create_instance`（agent_adapters.py:32，启动时与技能装卸后各调一次）、`reload_agent_config`（agent_adapters.py:40-55，热重载——支持 config_base 快照/env_overrides/target_session_id 限定扇出/reload_scopes 定向）、`process_message_impl`（agent_adapters.py:57 单发）、`process_message_stream_impl`（agent_adapters.py:68 流式）、`process_interrupt`（agent_adapters.py:79 暂停/恢复/取消/补充）、`handle_user_answer`（agent_adapters.py:83 演进审批或权限审批）、`handle_swarmflow_reply`（agent_adapters.py:87-93，swarmflow human-session 轮次的人答复，构造 `HumanAgentMessage(target="swarmflow:<run_id>:<corr>")`）、`handle_heartbeat`（agent_adapters.py:95）。

SDK 选择（agent_adapters.py:99-125）：环境变量 `JIUWENSWARM_AGENT_SDK`，默认 harness，`pi` 为保留位（未实现），未知值告警回退。工厂 `create_adapter`（agent_adapters.py:128-159）：harness + mode="agent" → `JiuWenSwarmDeepAdapter`（agent_adapters.py:148-149）；mode="code" → `JiuwenSwarmCodeAdapter`（agent_adapters.py:146-147）；pi 直接 NotImplementedError（agent_adapters.py:151-155）。

### interface.py：JiuWenSwarm 门面

类 docstring（interface.py:1528-1534）自述三职：SDK 工厂路由、统一对外 API、公共编排。结构要点：

- **有界流队列**（interface.py:1536-1540）：`STREAM_QUEUE_MAXSIZE = 64`——注释讲透理由：无界队列会让快的 Team runtime 在慢客户端消费时囤积全部 chunk，短命 TUI 会话也会推高 RSS。
- **构造与懒创建**：`__init__`（interface.py:1552-1575）先 `_prepare_skill_library()`（interface.py:1589-1613 钉死单一 Skill 库、迁移 legacy 团队视图——注释强调 agent-teams home 必须在任何扫描前钉位，否则会看 openJiuWen 默认根），再持 SessionManager/SkillManager 等；adapter 本体延迟到 `_ensure_adapter`（interface.py:1653-1666）——解析 SDK 名、create_adapter、注入 skill_manager 与 heartbeat。set_heartbeat_service（interface.py:1577-1587）在 adapter 创建前也可调用，快照先存门面、懒创建时继承。
- **双执行入口**：`process_message`（interface.py:3330-3335）走门面持有的 session 调度器（schedule_session=True）；`execute_message`（interface.py:3337-3342）供 AgentRuntime 自持调度时直通（False）。调度语义在 `_process_message` docstring（interface.py:3350-3352）与 SessionManager（session_manager.py:6/interface.py:24）三处一致钉版：**多 session 并发，同 session 内任务先进后出——新任务优先**（同会话用户连发消息，最新一句先跑）。实际提交在 interface.py:3647-3652 的 `submit_and_wait`。
- **请求分流**（interface.py:3354-3368）：CHAT_CANCEL 转 interrupt、CHAT_ANSWER 走 handle_user_answer（先过 auto-permission workspace 校验）、CHAT_SWARMFLOW_REPLY 走 swarmflow 答复、COMMAND_GOAL 走 goal 能力（interface.py:3371 起，set 动作才落历史）。
- **durable receipt + gateway announce**（interface.py:304-365）：`_complete_history_request` 把终态行入历史队列拿 completion receipt；`_announce_durable_completion`（interface.py:304-347）在 receipt 完成回调里给 Gateway 发 `SESSION_REQUEST_COMPLETED_EVENT` 推送——注释（interface.py:309-313）点明动机：**停止等待的 Gateway（取消/传输错误）没有其它途径知道 AgentServer 何时收尾**。receipt 用 done_callback 观察（interface.py:341-347），被取消的 waiter 不能取消历史写入者还要解决的 receipt。
- **流式侧装备**（interface.py:3937 注释自述 process_message_stream 有完整的 a2ui/durable/dedup 落盘机制约 700 行；interface.py:4424-4433 的 durable_pending 状态组：final chunks/reasoning chunks/首 delta 时刻/顺序表）。A2UI 后处理失败有 `retry_without_a2ui` 回退（interface.py:3668-3669）。

### interface_deep.py：JiuWenSwarmDeepAdapter 巨物

22839 行、575 个方法、单类（interface_deep.py:1799）。docstring（interface_deep.py:1826-1835）：封装 DeepAgent 实例生命周期、runtime tools 注册、stream event 解析、evolution 绑定、interrupt/user_answer 处理。类属性先立预算（interface_deep.py:1800-1802）：session adapter 空闲 TTL 2 小时、逐出批 3、reload 重试间隔 30s。

`__init__`（interface_deep.py:1846 起）是"补丁栈"：`apply_mcp_call_timeout_patch`（用 asyncio.wait_for 包 MCP 客户端、尊重 timeout_s 配置——远端 MCP server 被杀时快速失败而非挂 300s SSE 读超时）、`apply_mcp_apps_patch`（给 UI 关联的 MCP 工具结果打 mcp_app 块）、`install_project_lsp_leases`、`apply_task_tool_event_patch`（interface_deep.py:1857-1866 的注释是 issue #4861 档案：SDK TaskTool 静默消费 subagent 流导致 Web 端 10 分钟无事件帧，补丁加 roster 帧/活动镜像/心跳；特意在 __init__ 而非模块导入时打，保证无全局副作用且先于任何 DeepAgent 创建）、`apply_mcp_dynamic_token_patch`。

模块级还有前置构件生态（interface_deep.py:723-1769）：_RuntimeCronContextTokens、_GitSnapshot/_StableGitFacts、_RailBuildInfo、_GeneralPurposeStreamRail/_GeneralPurposeAskUserRail 等。**`build_model_from_entry`（interface_deep.py:1180-1233）是被全仓复用的模块级公开函数**——docstring 明示 agent_ws_server 的模型缓存与 auto_harness 调度器、图像模态预热都按同一规则从 models.defaults 造 Model。两处精细适配：endpoint_profile 按 api_base host 推断补全（interface_deep.py:1201-1206，DashScope 风格自建网关的线格式选择）；context_window 的过渡期出口 pop（interface_deep.py:1208-1225 的长注释——core 未加正式字段时防 unexpected keyword 发厂商、已加则留给 core，自动适配）。

会话级装配的代表样本是 heartbeat rail 的三重门（interface_deep.py:2212-2260）：`_build_heartbeat_rail` 无 service 不挂；**cron 执行会话不挂**（interface_deep.py:2217-2226，注释：cron 派生心跳与"禁止 cron 派生 cron"同理，且会话回收会连带收走心跳任务）；**渠道不支持不挂**（interface_deep.py:2227-2240，小艺等渠道无主动投递路径，"模型看不到该能力"比"模型答了却送不到"诚实）。`_is_cron_execution_session`（interface_deep.py:2180-2204）的判定口径与 `_ensure_cron_tools_registered` 对齐取并集：`__cron__` 渠道、`__cron__`/`cron` 前缀会话、或元数据 cron_id；heartbeat/health_check 调度器会话不算。

## 三、外部连接

- 上游消费方：AgentServer 的 Runtime（经 Worker dispatcher 的 `bind_runtime` 拿到的就是这层——05 篇 gateway_bridge 被注入 adapter 的 bind_gateway_transport）；process CLI 与 cron/heartbeat 调度器也直接构造。
- interface_deep 被 server 其它模块反向依赖：`build_model_from_entry` 的消费方包括 agent_ws_server 模型缓存与 auto_harness.scheduler（:1183-1185 docstring）；02 篇 spec.py 的三个 bundle provider 回调它的私有构造器——**门面在协议上隔离后端，巨物在实现上被全仓直接引用**，这是"协议化未完成"的活体证据。
- 下游：openjiuwen SDK（DeepAgent、ModelRequestConfig、ModelClientConfig）；Skills 系统（SkillManager/SkillDevService）；A2UI 协议（05 篇的推送通道承载 announce）。
- 平行实现：interface_code.py 的 JiuwenSwarmCodeAdapter 是 mode="code" 的子类变体（_is_code_agent 标志在 :1889-1897 注释中说明其决定沙箱主写入根是 project_dir 还是 workspace）。

## 四、数据流

一次 chat.send 从门面到 SDK：

1. `process_message`（interface.py:3330）带租户上下文进入 `_process_message`；非 chat turn 的特殊方法（CANCEL/ANSWER/SWARmFLOW_REPLY/GOAL）先分流。
2. `submit_and_wait`（interface.py:3648）进 SessionManager 的 per-session PriorityQueue——LIFO 语义让同会话新任务插队。
3. 队列轮到时执行 `adapter.process_message_impl`（interface.py:3644）——即 JiuWenSwarmDeepAdapter 的实现：按 session 懒建/复用 session adapter（TTL 2h 逐出），组装 rails（含三重门的 HeartbeatRail）、tools、Context Engine 配置后驱动 DeepAgent。
4. 流式路径 process_message_stream（interface.py:4110）边产出 chunk 边做 A2UI 后处理与 durable/dedup 落盘（interface.py:3937/:4424 状态组）；A2UI 失败走 retry_without_a2ui。
5. 终态：`_complete_history_request`（interface.py:350）持久化请求边界行 → receipt 完成回调 → gateway announce 推送 SESSION_REQUEST_COMPLETED_EVENT（interface.py:304-347）。
6. 热路径之外：技能装卸触发 create_instance 重建；配置变更走 reload_agent_config 的定向 scopes；模型条目统一经 build_model_from_entry（interface_deep.py:1180）物化。

## 五、设计决策

1. **Protocol + 工厂的后端可替换性**（agent_adapters.py:24-159）：门面只依赖八能力协议，pi 后端是显式保留位。代价是协议必须保持最小——八个方法之外的一切（6223+22839 行的绝大部分）都是"门面编排"与"Deep 专属"的私相授受。
2. **懒创建 adapter**（interface.py:1653）：Skill 库准备、heartbeat 注入都发生在 adapter 诞生前，首个请求才付创建成本；快照式继承（_personal_context_runtime_enabled，interface.py:1555-1558）保证懒创建不丢先到的状态。
3. **LIFO 会话队列**（session_manager.py:6）：同会话新任务优先是对话产品的正确偏置——用户追加的纠正/补充比排队中的旧请求更有价值，老任务自然被取代。
4. **durable receipt 先于 announce**（interface.py:304-365）：推送"完成"前先保证终态行在盘上，Gateway 侧的任何重连重放都拿得到一致历史；receipt 的 done_callback 隔离取消传染。
5. **补丁栈集中在 __init__**（interface_deep.py:1846-1866）：对上游 SDK 的行为修补（超时/事件帧/令牌）幂等且显式排序，每个补丁注释都带动机与 issue 编号——这是与无法修改的上游共存的工程范式。
6. **god-class 的经济学**：22839 行单类不是失控而是选择——rails/tools/team/沙箱/OAuth/演化全部共享 adapter 的会话态与指纹缓存，拆分要付出跨对象传状态的税。02 篇 spec.py 已示范"声明式外壳 + 回调巨物"的温和改良路线。

## 六、新人提示

- 改 agent 行为的标准入口排序：优先加 Rail（02 篇）或配置；确实需要 Deep SDK 深度交互才动 interface_deep.py——先 grep 是否已有等价方法（575 个方法里大概率有近亲）。
- `process_message` vs `execute_message` 的区别是"谁拥有调度"：AgentServer 场景用前者（门面排队），AgentRuntime/特殊宿主自管并发时用后者。用错会出现双重排队或无排队。
- 同会话"后发先至"是特性不是 bug（session_manager.py:6）——测试断言顺序时别按 FIFO 写。
- 模型不生效/线格式怪异：查 `build_model_from_entry` 的两处自动适配（endpoint_profile 推断 interface_deep.py:1201-1206、context_window pop interface_deep.py:1208-1225），多数"配置没传下去"的幻觉源于这里的静默补全。
- 心跳工具"有时有有时没有"：三重门（无 service/cron 会话/渠道不支持，interface_deep.py:2212-2240）都是设计行为；排查看 `[JiuWenSwarmDeepAdapter] skip HeartbeatRail` 日志。
- 读巨物先读 :1846-1900 的 __init__ 补丁栈与类属性预算区——巨物的全局行为（超时、事件帧、TTL）都在这两段声明，方法体只是它们的局部展开。
