# 02 核心运行时内核与 Agent Harness/Rails（tour S03+S04）

## 一、角色定位

`jiuwenswarm/runtime/` 是引擎心脏，但注意它管的**不是 agent 行为**，而是"让 agent 行为得以发生"的机器性资源：任务级执行上下文（context.py）、Worker 级资源复用内核（kernel.py）、Plan 模式状态机（plan.py）、持久化 checkpoint 生命周期（checkpointer.py）、Skill 知识图谱构建（symphony/build.py）。行为规约则住在另一处——`jiuwenswarm/agents/harness/`：code/spec.py 把配置变成声明式 DeepAgentSpec，Rails 是贯穿执行周期的"干轨"，拦截 model 调用前后与 tool 调用前后。

一条好用的分界线：**runtime/ 回答"资源与状态放在哪、活多久"；harness/ 回答"这个 agent 有什么能力、什么被禁止"**。前者是 landlord，后者是行为法典。

## 二、内部结构

### context.py：ContextVar 二元组（76 行）

RuntimeExecutionContext（context.py:17-21）是 frozen dataclass，只装两个字段：runtime 与 agent_manager。模块级 ContextVar（context.py:24-27）持有它，set/reset(token)/get 严格配对（context.py:30-50），子 asyncio task 自动继承——这是"任务级执行上下文"的全部实现，刻意薄。context.py:58-63 的注释解释了为什么 AgentManager 不单独设 ContextVar：多租户下 Manager 由 AgentRuntime 局部持有、经 set_runtime_context 传下游，避免第二份请求级可变全局。

### kernel.py：ResourceKernel 资源内核（405 行）

Worker 内可复用资源（模型客户端、Context Engine 实例等）的登记处。docstring（kernel.py:3-7）先立规矩：**可变 Agent/session 状态留在内核之外；Key 携带可信部署身份与不透明配置引用；retire 资源从不在既有执行下关闭它**。

- **身份与键**：进程启动即生成随机盐（kernel.py:23），`identity_reference`（kernel.py:26-28）用 HMAC-SHA256 把任意 JSON 值压成十六进制摘要——配置指纹不落明文。`KernelIdentity.for_agent`（kernel.py:41-57）组合 owner/data_dir/project_dir/work_mode 与 definition/capabilities/configuration 三份摘要构成资源身份；enterprise 下 data_root 切到 TenantContext 的租户根（kernel.py:48-51）。kernel.py:54 的注释是安全红线：**user_id 只是路由声明，绝不作为数据目录输入**。
- **acquire 双路径合一**：同步 `acquire`（kernel.py:133-160）与异步 `acquire_async`（kernel.py:295-336）共享同一次在途构造——`_Preparation`（kernel.py:79-86）持有一个 loop-neutral 的 `concurrent.futures.Future`（kernel.py:124-126 注释），两族调用者 join 同一次构造而不必 await 别的 loop 的 Task。同步路径的自等待会明确报错而非死锁（kernel.py:147-148），异步递归构造同样显式拒绝（kernel.py:331-333）。
- **LRU 空闲淘汰**：`release_entry`（kernel.py:380-393）在引用归零后，把超出 `max_idle`（默认 128，kernel.py:120）的最久未用条目移入 disposals 队列（kernel.py:388-392 的 `idle[:-self._max_idle]` 切片）。
- **跨事件循环安全处置**：`close_entries`（kernel.py:271-293）按资源的 `close_loop` 归属地执行 close——同 loop 直接 await；owner loop 还活着就 `run_coroutine_threadsafe` 投递过去；loop 已死则报错，绝不假装清理成功。
- **进程单例**：`process_kernel()`（kernel.py:404）返回模块级 `_PROCESS_KERNEL`（kernel.py:401），全 Worker 一份。

### plan.py：PlanModeController（284 行）

Plan 模式（Claude Code 式"只规划不动手"）的进程内状态机。它被 AgentServer 与 process CLI 共用（plan.py:3）。三个数据结构：每 session 的 WeakValueDictionary 锁缓存（plan.py:43、:79-85——session 死则锁被 GC）、exited_sessions 与 active_sessions 两个集合（plan.py:44-45）。

核心逻辑两段。`ensure_state`（plan.py:177-259）在执行前同步 plan 状态机：先经 `open_state_session`（plan.py:94-144）拿到 live agent session（plan.py:115-118 的注释解释了为何首 turn 必须绑定同一个 live adapter——临时 session 会与首 turn 绑定赛跑，让运行中的交互停留在过期快照上），然后按 previous/target 状态迁移、必要时发 exit 事件。`inject_activation_reminder`（plan.py:150-175）是教科书级 system-reminder 注入：把 plan 约束（只读、禁改、`enter_plan_mode`/`exit_plan_mode` 流程）前缀到 query 前，原文存进 `PLAN_REMINDER_ORIGINAL_QUERY_KEY`。`check_post_process_exit`（plan.py:261-281）在工具执行后检测 exit_plan_mode 迁移并广播退出事件。

### checkpointer.py：持久 checkpoint 生命周期（175 行）

`ensure_persistent_checkpointer`（checkpointer.py:73-129）幂等地以 sqlite 后端初始化 CheckpointerFactory 默认实例：db 路径来自 `get_checkpoint_dir()`（checkpointer.py:100-101），journal_mode 取 `checkpoint.sqlite_journal_mode` 配置、缺失时按 workspace 推断（checkpointer.py:104-108）。

本文件最有教学价值的是 `_get_persistent_checkpointer_lock`（checkpointer.py:32-70）：asyncio.Lock 绑定首次 acquire 它的 loop，之后从别的 loop acquire 会炸 "bound to a different event loop"。解法是 threading.Lock 守护下的懒构造 + **死 loop 检测重建**（checkpointer.py:59-69）——锁绑定的 loop 已死或漂移就丢弃重建，稳态后 READY 翻 True 无人再 acquire，重建成为 no-op。`close_persistent_checkpointer`（checkpointer.py:132-175）dispose 引擎连接池并强制下次冷启动——checkpointer.py:159-163 注释强调：即便 dispose 半途失败，也必须把 READY 压回 False，杜绝复用可能已关闭的连接池。

### symphony/build.py：Skill 知识图谱构建（872 行）

SymphonyGraphBuilder（build.py:161）驱动扫描→指纹→编排→构建流水线。`status`（build.py:174-199）对比当前 capability 哈希与图谱 active_entries 的差集，算出 added/changed/removed 三个列表判定 stale。`build_graph`（build.py:580-612）是外部入口，CancelledError 时取消活动 checkpoint（build.py:608-610）、finally 里清理（build.py:611-612）——_BuildCheckpoint（build.py:679）支撑断点续建。

### harness/code/spec.py：声明式能力冻结（355 行）

`convert_code_config_to_deep_agent_spec`（spec.py:250-344）把一份 config.yaml 快照转换为 DeepAgentSpec：能力以三个 bundle 形式声明——rails 装进 `CODE_RAIL_BUNDLE`（spec.py:301-306）、tools 装进 `CODE_TOOL_BUNDLE`（spec.py:307-312）、subagents 装进 `CODE_SUBAGENT_BUNDLE`（spec.py:313-323）。**能力冻结在 Spec 参数里，物化推迟到 `spec.build(context)`**——三个 provider（spec.py:81-119 / :122-163 / :173 起）在 build 时才真正调 adapter 的构造器。CodeBuildContext（spec.py:63-72）携带不可序列化的运行时值（adapter 引用、config 快照、artifacts）。两个值得注意的细节：spec.py:150-155 工具实例须 `register_tool` 挂到 session 限定的 owner 上（DeepAgentSpec 尚无 tool_owner_id 字段的补偿）；spec.py:335 `restrict_to_sandbox=True` 保留 code 模式历史默认。

### Rails：行为规约的干轨

**StructuredAskUserRail**（ask_user_rail.py:273）：上游 openjiuwen 的 AskUserRail 只支持纯文本 query，本子类扩展 schema 增加可选 `questions` 参数，让 LLM 呈现多选题。StructuredAskUserTool（ask_user_rail.py:240-265）按语言（cn/en）装配扩展 schema；interrupt 载荷经 `ToolCallInterruptRequest.tool_args` 保留结构化问题数据（ask_user_rail.py:280-283 docstring），由 interrupt_helpers 抽取供前端 TUI 渲染可点击选项。StructuredAskUserPayload（ask_user_rail.py:223-232）定义单选 str / 多选 list[str] 的 answers 映射。

**CircuitBreakerRail**（circuit_breaker_rail.py:304）：agent 循环检测断路器。CircuitBreakerConfig（circuit_breaker_rail.py:31-35）五个阈值：warning 10 / critical 20 / global 30 / unknown_tool 10，history_size 取三者最大公约放大（circuit_breaker_rail.py:37-43）。`_detect`（circuit_breaker_rail.py:454-496）四类检测按优先级排：global_breaker（同工具无进展连击）→ unknown_tool_repeat（错误工具连调）→ ping_pong（双工具交替，critical 与 warning 双档）→ generic_repeat（相同工具+参数重复）。命中即以 ToolInterruptException 中断。两个工程细节：args 哈希前先剥离不影响语义的 metadata 键（circuit_breaker_rail.py:79-84 只列 bash/powershell/Agent 的 description，:498-506 canonicalize）；报错文案 cn/en 双语模板（circuit_breaker_rail.py:52-75），且 config 的 "zh" 要归一成内部 "cn"（circuit_breaker_rail.py:96-101）。ToolResultErrorDetector（circuit_breaker_rail.py:104 起）统一从结构化字段推断工具结果成败，供"无进展"判定使用。

**AvatarPromptRail**（avatar_rail.py:29-37）：数字分身 Rail，双钩子。`before_model_call`（avatar_rail.py:43-119）先撤掉上次注入的 sections（:52-54——幂等清理），再按 ContextVar 里的权限上下文动态注入四类提示节：avatar_identity（分身身份）、group_chat_memory_notice（群聊禁写记忆）、memory_fully_disabled（记忆完全禁用）、interaction_guidance（交互指引），priority 递增（avatar_rail.py:69/90/106/116）。`before_tool_call`（avatar_rail.py:121-161）不依赖工具白名单直接检查所有调用：记忆完全禁用时五个记忆工具全拦（avatar_rail.py:151-155 write/edit/read/search/get）；群聊分身模式只拦写入（:159）。拒绝方式是 `_reject_tool`（avatar_rail.py:163-168）置 `ctx.extra["_skip_tool"]` 跳过执行、直接返回拒绝消息。

## 三、外部连接

- context.py 被 runtime/service.py（AgentRuntime）与 server/runtime/agent_manager.py 的 AgentManager 引用（context.py:11-13 TYPE_CHECKING），下游用 `get_current_runtime()` 拿到"当前正在执行我这单请求的 Runtime"。
- kernel.py 的 process_kernel 由 Worker 侧 runtime 服务消费；KernelIdentity.for_agent 依赖 common/utils 与 enterprise 租户上下文（kernel.py:44-51）。
- plan.py 上承 gateway/common/mode_matrix 的模式判定（plan.py:14），下接 harness/code/prompt/plan_approval 的事件常量（plan.py:15-18）与 openjiuwen 的 `create_agent_session`（plan.py:100）。
- checkpointer.py 的初始化日志以 "[JiuWenSwarmDeepAdapter]" 为前缀（checkpointer.py:62、:87、:118）——它实际由 06 篇的 interface_deep 巨物驱动，这是内核文件与适配器耦合的痕迹。
- spec.py 的三个 bundle provider 都回调 adapter（interface_deep）的私有构造器（spec.py:113-117 大量 `# pylint: disable=protected-access`）——声明式外壳 + 集中式实现的组合。
- 三条 Rail 都继承 openjiuwen 的 DeepAgentRail/AskUserRail 基类，经 spec.py 的 rail bundle 装配进 DeepAgentSpec。

## 四、数据流

一次 code 模式请求的资源轨迹：

1. Worker dispatcher 把执行交给 Runtime，`set_runtime_context(runtime, agent_manager)` 绑定上下文（context.py:30），token 存好待 finally reset。
2. Runtime 解析模式，若命中 plan 模式走 `PlanModeController.ensure_state`（plan.py:177）：取锁 → open live session → 迁移状态 → 注入 system-reminder。
3. 构造 DeepAgent：`convert_code_config_to_deep_agent_spec`（spec.py:250）产出 spec + context；`spec.build(context)` 触发三个 bundle provider 物化 rails/tools/subagents 到 CodeBuildArtifacts（spec.py:54-59）。
4. 模型客户端等重资源经 `process_kernel().acquire(key, factory)`（kernel.py:133）获取——key 由 KernelIdentity 加 kind/resource_id 组成；命中缓存则引用计数 +1 并 LRU 前移（kernel.py:173-177），未命中则构造一次、同 flight 的并发等待者共享结果。
5. agent 循环运行：每次 model 调用前 AvatarPromptRail 注入/清理提示节；每次 tool 调用前 CircuitBreakerRail 记录 ToolCallRecord 并跑 `_detect`，ask_user 调用被 StructuredAskUserRail 转成带 options 的 interrupt 挂起等待用户。
6. 会话状态经 checkpointer 持久化（ensure 在 Runtime 启动时已完成）；空闲资源在 release 时按 LRU 淘汰入 disposals，由 acquire 路径顺带 drain（kernel.py:335）。

## 五、设计决策

1. **配置指纹用 HMAC 而非明文哈希**（kernel.py:23-28）：资源键里的 definition/capabilities/configuration 可能含凭据形态的配置，HMAC 加进程盐既去敏感又保等值比较语义。
2. **"retire 不关活资源"**（kernel.py:5-6、:222-233）：retire 只标记 + 版本 +1，等最后一个引用 release 才真关——热重载配置时进行中的执行不受打扰，新 acquire 自然拿到新版本。
3. **同步/异步共享 in-flight 构造**（kernel.py:124-126）：避免双路径各造一份重资源的经典 bug；代价是必须显式诊断自等待死锁（kernel.py:147、:331），宁可报错不可挂死。
4. **锁的 loop 漂移重建**（checkpointer.py:32-70）：不引入 nanhors 级复杂度，用"检测-丢弃-重建"处理 asyncio.Lock 的 loop 亲和性，是测试 harness 与真实服务共存场景的实用解。
5. **声明式 Spec + 延迟物化**（spec.py:297-343）：配置快照 deepcopy 后冻结进 Spec，物化时才触碰 adapter——配置在构造期与执行期之间不会中途变异，可重建、可缓存。
6. **Rails 覆盖而非侵入**：ask_user 扩展、断路器、分身注入全部以 Rail 子类挂进执行周期，openjiuwen 核心循环零改动——上游 SDK 升级时 jiuwenswarm 侧的合并面最小。

## 六、新人提示

- 判断"该改 kernel 还是该改 harness"：资源生命周期/复用问题进 runtime/；agent 行为规约进 rails。改错层会立刻撞到 god-class 墙（adapter 私有方法满天飞，见 06 篇）。
- kernel.py 的并发语义是全仓最精细的一块，改前先读懂 `_publish_preparation`（kernel.py:191-220）里"version 不匹配 / 中间代已发布 / 正常发布"三分支——retirement 与 construction 竞态的胜负手都在这里。
- 排查 plan 模式"不生效"：先看 `should_sync`（plan.py:67-69，只有 chat turn 方法参与）与 `may_hold_state`（plan.py:87-92），多数误报是请求根本不进同步门。
- circuit breaker 的 args 哈希**故意**忽略 bash 的 description 字段（circuit_breaker_rail.py:80-84）——加新工具的 metadata 豁免时要确认该字段真的不影响执行语义，否则会把"参数其实变了"误判为重复。
- avatar_rail 的 before_model_call 每轮都先清后注（avatar_rail.py:52-54），写新 Rail 时照抄这个幂等模式，否则 sections 会跨请求泄漏。
- 日志前缀混用是历史痕迹：checkpointer.py 里 "[JiuWenSwarmDeepAdapter]" 前缀并不代表它属于 interface_deep.py——按文件位置理解职责，别按日志前缀 grep 归类。
