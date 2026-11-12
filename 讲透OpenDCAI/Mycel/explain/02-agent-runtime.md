# 02 · Agent 运行时：LeonAgent / 中间件族 / ToolRunner / loop / fork / compactor

## 角色定位

`core/runtime/` 与 `core/agents/` 是 Mycel 的 agent 内核——一个自研的中间件式 coding agent 运行时（文件头自称 "Leon - AI Coding Agent with Middleware Architecture"，agent.py:2）。`core/runtime/agent.py` 的 `LeonAgent`（agent.py:92）是总装配类：把模型、沙箱后端、工具注册表和六层中间件叠成一个可对话的 agent；`core/runtime/runner.py` 的 `ToolRunner` 是所有工具调用的权限与执行中枢；`core/runtime/loop.py` 的 `QueryLoop` 是跑一轮对话的状态机（含错误恢复）；`core/runtime/fork.py` 与 `core/agents/service.py` 负责子 agent 分叉；`middleware/memory/compactor.py` 是上下文压缩器。这组代码的目标读者是"想让 agent 安全地替人写代码"的工程师：权限三态、危险命令扫描、上下文回收全在这里。

## 内部结构

**中间件栈（外→内）**：`SpillBuffer → Monitor → PromptCaching → Memory → Steering → ToolRunner`（agent.py:4-5 文档串、agent.py:975-976 重复声明）。`_build_middleware_stack`（agent.py:972-1029）逐层装配：Monitor 最靠外以保证 token 统计先于任何请求变形（agent.py:983-991）；PromptCaching 仅当解析出的 provider 是 anthropic 才挂（agent.py:998-999，@@@prompt-caching-provider-contract 注明"通用模型包装器不是安装提示缓存的安全信号"）；Memory 在记忆功能启用时插入（agent.py:1002-1004）；`IntegrationInstructionsDeltaMiddleware` 在 MCP 指引变化时注入线程级提醒（agent.py:1007-1012）；Steering 负责把排队消息注入模型调用前（agent.py:1015-1016）；ToolRunner 最内层路由一切已注册工具调用（agent.py:1018-1023）；SpillBuffer 最后插到下标 0 做最外层，捕获超大工具输出（agent.py:1025-1029）。装配完成后 LeonAgent 还把 Monitor 的 runtime 反向注入 Memory/Steering（agent.py:323-331）——中间件之间不是纯洋葱，存在运行时互取。

**ToolRunner（runner.py 全 774 行）**：类在 runner.py:45。一次工具调用的流水线是 `_validate_and_run_async`（runner.py:597-694）：schema 校验（L609-621）→ 工具自定义校验（L623-643）→ pre_tool_use 钩子扇出（L645-650）→ 权限三态裁决（L651-658）→ 上下文注入（L667）→ 执行。**权限三态**是核心：`_resolve_permission_async`（runner.py:442-517）综合 pre 钩子倾向与 `can_use_tool` 规则检查器（L455-466），产出 allow/deny/ask。deny 直接物化拒绝信封（L452-453）；ask 时先消费"一次性批准"槽 `consume_permission_resolution`（L468-479，@@@permission-resolution-precedence：只在当前状态仍是 ask 时才消费，防止旧批准被复用），没有一次性批准就调 `request_permission` 生成 request_id 并物化"许可请求"信封（L207-217）——@@@permission-ask-materialization（L212-214）写得很硬：**"只有存在具体请求面（request_id）时 ask 才诚实，否则大声按 deny 失败"**，让调用方元数据与真实运行时一致。恢复路径：用户批准后由外部写入 resolution，下一轮同一工具再进 ask 分支即被 L470-477 放行。

**DangerousCommandsHook（core/tools/command/hooks/dangerous_commands.py，224 行）**：`_unquoted_command`（dangerous_commands.py:86-123）先手写状态机剥掉单引号/双引号/反斜杠转义/`$'...'` ANSI-C 与 `$"..."` locale 引号（正则定义在 L63-64）以及注释（L115-118），@@@bash-hook-unquoted-scan（L87-88）说明动机：**危险命令正则只应检查可执行 shell 表面，不检查引号内的字面文本**——否则 `echo "rm -rf /"` 这类内容会被误杀。剥完引号后 `_find_dangerous_command_word`（L149-182）用 shlex 词法分析（`punctuation_chars=";&|()<>"`，L151）按"命令位置"扫描：环境变量前缀跳过（L171-172），命中基础黑名单词（L174-175），`rm` 需同时出现递归与强制标志才算 `rm -rf`（L126-147，`--recursive`/`--force`/短旗标 r+f 组合都认，遇 `--` 或操作符即止）。

**QueryLoop 错误恢复（loop.py，2181 行）**：模型错误交给一串按序尝试的恢复器（loop.py:1231-1233 注册表，含 `_try_context_overflow_escalate` L1239 与瞬态重试）。三类关键策略：①输出 token 上限撞墙——先升级 `max_output_tokens` 到 `_ESCALATED_MAX_OUTPUT_TOKENS = 64000`（loop.py:32，L1271-1283），升级后仍撞墙则注入一条 "Output token limit hit. Resume directly with no apology or recap." 的 HumanMessage 续跑（L1284-1299），三次（`< 3`，L1284）后转终态 model_error（L1300-1310）；②瞬态 API 错误——`_TRANSIENT_API_MAX_RETRIES = 3` 次、基础退避 0.5 秒（loop.py:35-36，_try_transient_api_retry L1253-1269，超过 3 次放行给下一恢复器）；③上下文溢出——`_recover_from_overflow`（L1474）触发反应式压缩。终态原因枚举 TerminalReason 有 11 种（loop.py:40-50），继续原因 8 种（L53-61），全是可观测的一等公民。

**fork 与子 agent**：`fork_context`（fork.py:7-33）复制 BootstrapConfig 但换新 `session_id=uuid4().hex` 并记 `parent_session_id`——成本字段（total_cost_usd 等）随迁；`create_subagent_context`（fork.py:29-68）克隆 ToolUseContext，read_file_state 优先 `clone()` 否则 deepcopy（@@@sa-04-read-file-state-clone，L41-44：浅拷贝会把子 agent 的编辑泄漏回父缓存）；`set_app_state` 默认替换成 no-op（fork.py:50），只有 `share_set_app_state=True` 才让子 agent 写父状态。`AgentService`（core/agents/service.py:438）按 subagent_type 解析工具过滤集（service.py:53）与模型（L77-92，支持继承标记），后台任务与 bash 后台运行各有独立记账（_RunningTask L308 / _BashBackgroundRun L328），取消运行的结果汇报有专门的诚实性契约（@@@cancelled-run-result-honesty，service.py:406）。

**compactor（CC L4b 对齐）**：压缩用 `COMPACT_SYSTEM_PROMPT`——一句 ~200 token 的朴素指令（compactor.py:10），**刻意不继承父对话 system prompt**（compactor.py:7-9 注释：不同 system prompt → 不同前缀哈希 → 防止复用父会话的提示缓存，同时降低输入成本）。摘要按 9 节模板生成（L12-23：Request/Concepts/Files/Errors/Problem Solving/User Messages/Pending/Current/Next Step）；切分保留最近 20000 token，边界永不把 AIMessage(tool_calls) 与其 ToolMessage 拆开（L44-48、L71-72）；压缩调用禁工具、max_tokens 封顶 20000（L87-109）；触发阈值默认上下文 70%（L40-42）。

## 外部连接

- 上游：langchain `init_chat_model`（agent.py:28）构造模型；`config/` 的 LeonSettings/AgentLoader/ModelsLoader 提供配置；沙箱 `self._sandbox.fs()` 提供文件系统后端（agent.py:981）。
- 工具族：core/tools 七族服务（filesystem/search/command/web/skills/task/tool_search，agent.py:7-16 文档串）注册进 ToolRegistry；MCP 工具经 mcp_gateway 进同一注册表，ToolRunner 用 `entry.source == "mcp"` 区分来源（runner.py:534-536）。
- 下游：backend/threads 的运行时在首条消息时创建 LeonAgent（01 篇 lifespan 契约注释）；子 agent 沙箱经 `_normalize_child_sandbox`（service.py:547）接 03 篇的 provider 体系。

## 数据流

一次用户消息：QueryLoop 取中间件列表 → SpillBuffer 兜住上一轮超大输出 → Monitor 记 token → PromptCaching（仅 Anthropic）→ Memory 判断 `estimated_tokens > limit*0.7` 决定压缩 → IntegrationInstructions 检查 MCP 指引增量 → Steering 把队列里的 owner 消息注入（若有 steer 消息，追加"非抢占"诚实性契约 system 注记，queue/middleware.py:43-62）→ ToolRunner 注入内联工具 schema（runner.py:50-63）→ 模型响应含 tool_calls → ToolRunner 逐调用走校验/钩子/权限/执行：pre 钩子可改 args 也可表达权限倾向，扇出结果按 deny>ask>allow 折叠（runner.py:390-397）；执行时同步 handler 一律 `asyncio.to_thread` 下线程（runner.py:672-675，@@@async-tool-offload：远程文件系统/shell 冷启动可阻塞数秒，绝不能占 web 事件循环）；结果信封经 post_tool_use / post_tool_use_failure / permission_denied_hooks 三类钩子（runner.py:580-586）再物化成 ToolMessage——本地工具先物化、MCP 工具保持信封让 post 钩子看到结构化输出（@@@tool-result-ordering，runner.py:750-753）。上下文逼近上限时 MemoryMiddleware 压缩，失败走熔断（@@@compaction-breaker-scope，memory/middleware.py:374）并向 owner 排通知（L416）。

## 设计决策（含批判）

1. **权限三态而非布尔**：ask 状态把"人还来得及拦"变成运行时语义，且物化必须携带 request_id，否则宁否认不假装——这是对"静默放行/静默挂起"两类事故的防御。批判：三态裁决逻辑分居 `_resolve_permission_async` 与 pre 钩子折叠两处，L442-517 分支组合已接近人脑上限，新增第四方（如审计否决）时建议先写判定表再动代码。
2. **引号外扫描**是命令安全里少见的精细活：正则只看可执行表面，同时保留 shlex 级的命令位置判断（重定向后的 token 不再当命令，L164-166）。它防误杀不防绕过——真正执行仍靠沙箱隔离，黑名单只是第一层。
3. **64k 升级 + 3 次续跑**的恢复序列承认一个现实：长输出被截断往往不是错误而是"没写完"，注入"别道歉直接续"的提示（loop.py:1286-1290）是对模型行为的针对性补丁。
4. **CC L4b 压缩的缓存意识**：换 system prompt 就能避免压缩请求吃父对话的缓存前缀，这是对 Anthropic 前缀缓存机制的逆向利用；副作用是压缩摘要风格与主对话人设完全脱节，9 节模板承担了全部结构化职责。
5. **fork 的选择性共享**：路径/成本/模型全继承，session 身份与写状态能力默认不继承——子 agent 崩溃或作恶的爆炸半径被限制在读侧。`set_app_state` no-op 化（fork.py:50）是隐式契约，调用方不读源码很难发现"为什么子 agent 改不了全局状态"。

## 新人提示

- 读 ToolRunner 先看 runner.py:597-694 的主流程，再进 `_resolve_permission_async`；所有 `@@@` 前缀注释（本仓上百处）是决策考古记录，改动前必读。
- 想加新工具：在 core/tools 对应 Service 注册（自动进 ToolRegistry），ToolRunner 侧零改动；想加"执行前拦截"逻辑用 pre_tool_use 钩子（挂在 state 上，runner.py:79-92 自动发现），别改 runner。
- 调权限问题三问：can_use_tool 规则返回了什么？有没有一次性批准被提前消费？ask 有没有 request_id？分别对应 runner.py:462-466 / L468-479 / L207-217。
- 子 agent "改了文件父 agent 看不到"多半是 fork 深拷贝语义（有意）而非 bug；反之若父缓存被子污染，查 read_file_state 是否漏 clone。
- loop.py 很长但结构是"主循环 + 错误恢复器链"，改恢复策略时只动 `_try_*` 方法与 L1231-1233 的注册顺序，别在主循环里加内联分支。
