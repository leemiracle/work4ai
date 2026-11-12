# 06 · goose-cli：从命令行到会话的装配线

> 源码基准：`crates/goose-cli/src/`（main.rs 51 行 / cli.rs 2286 行 / session/builder.rs 700 行 / session/mod.rs 2449 行）。全部行号锚写作时已从源码逐一核实。

## 角色定位：16 层架构中的"前端之一"，goose 核心的薄壳

在 goose 仓知识图谱的 16 层架构里，goose-cli 位于第 6 层「goose-cli 命令行界面」（65 节点），它的下面是五层 goose 核心能力——Agent 会话引擎、LLM Provider 适配层、MCP 扩展子系统、ACP 协议层、配置·安全·网关层；上面则是 goose-server、桌面端、TUI 等其它前端。这个位置本身就是架构宣言：**CLI 不实现任何 agent 逻辑，它只是把命令行参数装配成一次 `Agent` 调用**。

"薄壳"规约有硬证据。看依赖方向：`crates/goose-cli/Cargo.toml:24-26` 以 path 依赖引入 `goose`、`goose-mcp`、`goose-providers` 三个本地 crate，CLI 自己没有独立的会话引擎或 provider 实现。看代码量分布：main.rs 仅 51 行、cli.rs 的 2286 行里近半是 clap 声明性定义，真正的运行时逻辑集中在 session/ 目录。看调用方式：CLI 对核心的全部诉求都收敛为对 `goose::agents::Agent` 公共 API 的调用——`reply`（agent.rs:1406-1410，签名 `(user_message, session_config, cancel_token) -> BoxStream<AgentEvent>`）、`add_extension`（agent.rs:1185）、`update_provider`（agent.rs:2449）、`update_goose_mode`（agent.rs:2471）、`handle_confirmation`（agent.rs:1371）、`extend_system_prompt`/`override_system_prompt`（agent.rs:2423/2604）。CLI 与桌面端（goosed）、ACP（`goose acp`，cli.rs:808）、HTTP 服务（`goose serve`，cli.rs:822）消费的是同一个 Agent，这正是"多前端一核心"的落地。

还有一层"壳上壳"关系值得点破：`goose tui`（cli.rs:993-1011，feature gate）本身不渲染任何 UI，它在 commands/tui.rs:68 的 `handle_tui` 里定位本地 `ui/text/dist/tui.js` 或走 `npx @aaif/goose`，然后 exec 接管进程，并通过 `cmd.env("GOOSE_BINARY", ...)`（tui.rs:75）把自己（goose CLI 二进制）注入给 Ink/React 终端 UI——也就是说 **ui/text 那套 Ink TUI 是一个 Node 进程，反过来驱动本篇讲的这条 CLI 装配线**，CLI 是 TUI 的"内核"而非平级兄弟。

## 内部结构：三段式——进程引导、clap 命令树、会话装配与 REPL

### 1. main.rs：最小进程引导（51 行）

`main()`（main.rs:32）做三件事：Windows 下先启用 VT 转义序列处理（main.rs:9-15，注释明说否则 cliclack/indicatif 的 spinner 会刷成重复新行）；然后 `std::thread::Builder` 起一个名为 `goose-cli-main`、**8 MiB 栈**的线程（main.rs:36-38），线程内构建 tokio multi-thread runtime 并 `block_on(run())`（main.rs:40-44）。8 MiB 栈没有注释说明动机——推断是为 agent 长调用链/深递归预留（默认 2 MiB 可能溢出），属推断非源码事实。`run()`（main.rs:17）只做日志初始化（失败仅警告不阻断，main.rs:18-20）、调用 `cli().await`（main.rs:22）、以及 otel 遥测优雅关闭（main.rs:24-27）。**进程入口不含任何业务分支**，这是薄壳的第一课。

### 2. cli.rs：clap 命令树与分发

顶层 `Cli` 是 `#[derive(Parser)]`，唯一的字段是 `command: Option<Command>`（cli.rs:54-59）——**Option 是关键**：`None` 分支（cli.rs:2225）落入 `handle_default_session()`，这就是裸命令 `goose` 直接进 REPL 的入口。

参数按语义切成可复用的 Args 组，用 `#[command(flatten)]` 拼装进各子命令：`Identifier`（--name/-n、--session-id、--path 三选一互斥，cli.rs:61-90）、`SessionOptions`（--debug/--max-tool-repetitions/--max-turns/--container，cli.rs:93-125）、`ExtensionOptions`（--with-extension/--with-streamable-http-extension/--with-builtin/--no-profile，cli.rs:160-195）、`InputOptions`（-i 文件或 stdin、-t 文本、--recipe、--system、--params、--sub-recipe，cli.rs:198-278）、`OutputOptions`（-q 与 --output-format text/json/stream-json，cli.rs:281-300）、`ModelOptions`（--provider/--model，cli.rs:312-331）、`RunBehavior`（-s/--interactive、--no-session、-r/--resume、隐藏的 --scheduled-job-id，cli.rs:334-372）。

`Command` 枚举（cli.rs:781-1141）是完整一级命令表：configure/info/doctor/mcp/acp/serve/session(s)/project(s)/run/recipe/skills/plugin/schedule(sched)/gateway(gw)/update/term/tui/local-models(lm)/completion/review/validate-extensions(隐藏)。其中 `session` 自带二级枚举 SessionCommand（list/remove/export/import/diagnostics，cli.rs:486-584），`run` 是参数组最多的命令（cli.rs:895-916，flatten 了六组）。

`cli()` 入口函数（cli.rs:2073）顺序做四件事：注册内建 MCP 扩展（`register_builtin_extensions`，cli.rs:2074）、`Cli::parse()`（cli.rs:2076）、更新项目跟踪器（失败仅 warn，cli.rs:2078-2080）、打命令名遥测（cli.rs:2082-2087），然后进入那个巨大的 `match cli.command` 分发（cli.rs:2089-2226）。

会话 ID 的**前置解析**也在这一层：`get_or_create_session_id`（cli.rs:374-455）处理三种形态——resume 且无标识时取最新会话（cli.rs:388-393）；非 resume 且无标识时 `SessionManager::create_session` 新建（cli.rs:418-424）；给了 --session-id 却没 --resume 直接报错（cli.rs:428-429）。它先把"要不要有会话文件"这个问题在进 builder 之前解决掉。

### 3. builder.rs：build_session 装配线（700 行的核心 140 行）

`build_session(SessionBuilderConfig)`（builder.rs:483）是一条严格有序的总装线，入参结构体有 20 个字段（builder.rs:79-119）。按执行顺序：

1. 遥测上下文（builder.rs:484-485）→ 2. 取全局配置并 `Agent::new()`（builder.rs:487-488，Agent 是便宜的结构体，重活都在后面）→ 3. 容器设置（builder.rs:490-492）→ 4. resume 时从 session 元数据捞出上次的 provider/model（builder.rs:496-507）→ 5. **解析 provider/model**（`resolve_provider_and_model`，builder.rs:232-292，下文详述）→ 6. 应用 recipe 的 response 组件（builder.rs:514-516）→ 7. **解析 session id**（`resolve_session_id`，builder.rs:294-341：--no-session 则建 `SessionType::Hidden` 会话即用即弃（builder.rs:304-316）；resume 则校验存在否则取 list[0]（builder.rs:317-337）；否则直接 clone 调用方预建好的 id（builder.rs:338-340））→ 8. resume 且工作目录漂移时交互确认是否切回原目录（`handle_resumed_session_workdir`，builder.rs:343-403）→ 9. **收集扩展配置**（`collect_extension_configs`，builder.rs:405-434，下文详述）→ 10. `goose::providers::create(provider, model_config, extensions)` 造 provider（builder.rs:534-538，失败提示查 keychain 并引导 goose configure）→ 11. `agent.update_provider` + `update_goose_mode` 写入会话（builder.rs:555-569）→ 12. recipe 持久化到 session 元数据（builder.rs:571-580）→ 13. **并行加载扩展**（builder.rs:583，见下）→ 14. 读 EDIT_MODE 配置映射 rustyline 的 Emacs/Vi（builder.rs:585-595）→ 15. debug 判定 = CLI flag OR GOOSE_DEBUG 配置（builder.rs:597）→ 16. `CliSession::new(...)` 组装 REPL 对象（builder.rs:599-609，注意 `Arc::try_unwrap`——加载扩展期间的共享 Agent 在此收回唯一所有权）→ 17. 配置系统提示词（`configure_session_prompts`，builder.rs:453-481）→ 18. 非 quiet 则打印会话信息横幅（builder.rs:613-620）。

扩展加载 `load_extensions`（builder.rs:150-224）用 `JoinSet` 把所有扩展的 `add_extension` 并发 spawn（builder.rs:158-163），cliclack spinner 实时显示"starting N extensions: 标签列表"（builder.rs:183-184），**单个扩展失败不阻断**——只黄字警告并提示"会话启动后让 goose 帮你调试该扩展"（builder.rs:200-221）。启动失败的会话照样能用，这是明确的韧性设计。

### 4. session/mod.rs：CliSession 与 REPL

`CliSession` 结构体（mod.rs:163-175）持有 agent、内存态 `Conversation`、session_id、补全缓存、run_mode（Normal/Plan 二值，mod.rs:111-114）、max_turns、edit_mode、retry_config、output_format。构造函数 `CliSession::new` 从 session_manager 把该会话的历史对话拉回内存（mod.rs:254-260）——REPL 的"恢复"就是把 JSONL 会话文件重放成 Conversation。

REPL 入口 `interactive()`（mod.rs:480）先发 SessionStart hook、结束后发 SessionEnd hook 并打印红色 session closed 横幅（mod.rs:482-499）。真正的主循环 `run_interactive`（mod.rs:502-540）：可选先处理初始 prompt（mod.rs:503-507）→ 刷新补全缓存 → 建 rustyline 编辑器（`create_editor`，mod.rs:542-559，Circular 补全 + GooseCompleter）→ 加载历史（HistoryManager，mod.rs:116-161，新路径 state_dir/history.txt，找到旧 config_dir/history.txt 会迁移后删除）→ **loop**：每轮先显示上下文 token 占用（mod.rs:516），`output::run_status_hook("waiting")`，`input::get_input` 读一行（mod.rs:531），Exit 则 break，否则 `handle_input` 分派（mod.rs:535）。

`handle_input`（mod.rs:561-677）是对 `InputResult` 枚举的大 match。InputResult（input.rs:12-33）有 21 个变体，把一行输入语义化：Message/Exit/AddExtension/AddBuiltin/ToggleTheme/SelectTheme/Retry/ListPrompts/PromptCommand/GooseMode/Model/Plan/EndPlan/Clear/Recipe/Compact/ToggleFullToolOutput/Edit/ListSkills/LoadSkills——**斜杠命令在 input.rs 解析成枚举，mod.rs 只做分派**，两层职责切得很干净。

普通消息走 `handle_message_input`（mod.rs:679-723）：Normal 模式下存历史 → push 用户消息 → 更新项目跟踪器（mod.rs:690-698）→ 取 provider → thinking spinner → `process_agent_response`（mod.rs:706）→ 计时打印；Plan 模式则克隆消息列表交给 reasoner 模型（mod.rs:714-720，`get_reasoner` 优先 GOOSE_PLANNER_PROVIDER 配置否则默认 provider，mod.rs:2118-2133）。

## 外部连接：向下的四类依赖边

**① goose 核心 Agent（最重要的一束边）**。REPL 的心脏 `process_agent_response`（mod.rs:1138-1396）先构造 `SessionConfig { id, schedule_id, max_turns, retry_config }`（mod.rs:1146-1151，结构体定义在 types.rs:85-95），spawn 一个 ctrl_c 监听任务（AbortOnDropHandle 保证清理，mod.rs:1157-1163），然后调 `self.agent.reply(user_message, session_config, Some(cancel_token))` 拿到 `BoxStream<AgentEvent>`（mod.rs:1165-1172）。此后 CLI 就是一个纯消费者：`tokio::select!`（mod.rs:1182）在"流下一个事件"与"取消令牌触发"之间二选一。图谱中 cli.rs→agent.rs 的调用边全部由此发出。

**② SessionManager（会话持久化）**。cli.rs 的 get_or_create_session_id/lookup_session_id、builder.rs 的 resolve_session_id、mod.rs 的 handle_clear（mod.rs:884-918 直接 `replace_conversation` + token 清零）、json 输出时读回 token 计数（mod.rs:1344-1369），都走 `agent.config.session_manager` 或 `SessionManager::instance()`。

**③ Config 与扩展系统**。builder.rs:421 调核心的 `resolve_extensions_for_new_session`（extensions.rs:207-225）：优先级 recipe.extensions > override > 全局 enabled 列表，再经 `is_extension_available` 过滤（extensions.rs:221）。CLI flag 扩展的字符串解析（stdio 的 ENV=var cmd args / streamable http 的 URL+timeout / builtin 逗号列表）由 `parse_cli_flag_extensions`（builder.rs:30-72）先翻译成 `ExtensionConfig`，再叠加在上述结果之后（builder.rs:424-431）。三类解析器的"真身"是 CliSession 的关联函数（mod.rs:283-318 / 320-354 / 357-382）。

**④ 输出渲染器**。session/output.rs（1605 行）独立承担终端呈现：流式 markdown（render_message_streaming，output.rs:274）、McpSpinners 进度条、会话横幅（display_session_info，output.rs:1294）、thinking 指示、主题切换。mod.rs 只在恰到好处的时机调用它们，且 json/stream-json 模式下会绕过人类可读渲染改走 `emit_stream_event`（mod.rs:1285-1287、1743-1747）。

调度线的注记：任务书提到的 session/leader.rs **在本仓此版本不存在**（session/ 目录实测无此文件），与调度相关的事实是两处——SchedulerCommand 子命令树（cli.rs:586-651，add/list/remove/sessions/run-now，处理器在 commands/schedule.rs）与 `goose run` 的隐藏参数 --scheduled-job-id（cli.rs:363-371），后者经 SessionBuilderConfig.scheduled_job_id → SessionConfig.schedule_id 一路传进核心 Agent 关联计划任务。若你拿着旧文档找 leader.rs，按源码为准：没有这个东西。

## 数据流：一条裸命令的完整启动链 + 一条输入的处理链

**启动链（`goose` 裸命令）**：main.rs:36 起 8 MiB 线程 + tokio runtime → main.rs:22 `cli().await` → cli.rs:2074 注册内建扩展 → cli.rs:2076 clap 解析得 `command = None` → cli.rs:2225 `handle_default_session()` → cli.rs:2035-2036 首次运行检测：全局配置不存在则转 `handle_configure()` 引导向导，否则继续 → cli.rs:2044-2045 取 goose_mode 并 `get_or_create_session_id` 新建会话（此时 JSONL 会话文件已落盘）→ cli.rs:2047-2069 以全默认参数调 `build_session` → builder 十八步总装（见上节）→ cli.rs:2070 `session.interactive(None)` → mod.rs:482 SessionStart hook → REPL 循环开转。

**输入处理链（用户敲一句话）**：mod.rs:531 get_input 解析 → InputResult::Message → mod.rs:688 push 用户消息进 Conversation → mod.rs:706 process_agent_response → mod.rs:1146 组 SessionConfig → mod.rs:1167 `agent.reply(...)` 返回事件流 → select! 循环逐事件消化：普通 Message（mod.rs:1280-1294，push + 流式渲染）；**工具确认**——`find_tool_confirmation`（mod.rs:1186，实现于 1800-1809）识别 ActionRequired，交互模式弹 cliclack 四选项（Allow/Always/Deny/Cancel，mod.rs:1760-1785），无头模式下若 GooseMode 是 Approve/SmartApprove 直接报错终止（mod.rs:1190-1203，注释明言这是防止绕过安全契约的非法配置），其余无头场景降级 AllowOnce 并 warn（mod.rs:1204-1208）；**elicitation 请求**（mod.rs:1234-1277）——交互模式收表单后以不可见 user 消息回推并再调一次 `agent.reply` 解锁等待中的工具调用（mod.rs:1254-1263）；MCP 通知（mod.rs:1297-1307）转进度条或子代理调用渲染；HistoryReplaced（mod.rs:1308-1310）用压缩后的对话整体替换内存 Conversation；Err → 收尾后 break（mod.rs:1311-1326）；流自然结束 None → break（mod.rs:1327）。循环后 flush markdown 缓冲、按输出格式收尾（mod.rs:1340-1393）。

**Ctrl-C 中断链**是隐藏最深的匠心：mod.rs:1158-1162 的监听任务触发 cancel_token → mod.rs:1330-1336 分支 `handle_interrupted_messages(true)`（mod.rs:1398-1470）——若最后一条是带未决 tool_request 的 assistant 消息，**伪造对应的 tool_response 错误**（"Interrupted by the user…"，mod.rs:1426-1441）再补一句助手消息"Yes — what would you like me to do?"。推断其动机：MCP 协议要求每个 tool_request 必须有配对 response，不补会让会话文件留下悬空请求、resume 后无法续跑——这与第 05 篇会话持久化的格式约束互为表里（标注：动机为推断，行为是源码事实）。

**`goose run` 分叉**：parse_run_input（cli.rs:1577-1674）先仲裁输入源（-i 文件 / `-` 读 stdin 至 EOF（cli.rs:1586-1598）/ -t 文本 / --recipe 四选一，缺一即 exit(1)）。recipe 分支（cli.rs:1622-1667）支持 --explain 与 --render-recipe 两个"看而不跑"的早退出口，真正的执行经 `extract_recipe_info_from_cli` 得到 input_config + Recipe 对象（cli.rs:1661-1667）。然后 handle_run_command（cli.rs:1676-1761）走同一条 build_session（recipe/额外系统提示词/provider/model 覆盖全在此注入），最后三分叉：`-s/--interactive` 转 `session.interactive(contents)` 先跑初始输入再进 REPL（cli.rs:1740-1741）；默认 headless 单条执行（cli.rs:1753）；无内容则报错。

## 设计决策：五个值得抄的选择

**1. 装配为何集中在 builder.rs**。对比三处调用点：handle_interactive_session（cli.rs:1504-1526）、handle_run_command（cli.rs:1716-1738）、handle_default_session（cli.rs:2047-2069）——三者都只需填一张 20 字段的 SessionBuilderConfig 表，构建逻辑（provider 解析、扩展并发装载、提示词配置、容错策略）只写一遍。这是典型的"参数对象 + 单一工厂"：新增一种入口（如 term、schedule 内部拉起 run）零成本复用。代价是 20 字段的结构体偏胖，源码为它手写了带 output_format 默认值的 Default impl 并注释原因（builder.rs:121-148）——clap derive 的 Default 会把 output_format 初始化成空串。

**2. provider/model 四级回退链**。builder.rs:243-263 显式编码：CLI flag > resume 会话里存的 > recipe settings > 全局配置，任一级缺就 `process::exit(1)` 并提示 `goose configure`。resume 且模型名一致时直接复用 saved_model_config（含上下文窗口等元数据）只允许 recipe 覆盖 temperature（builder.rs:265-275）——保证续跑会话的模型上下文参数不漂移。扩展来源同样是显式优先级：resume 用会话级 EnabledExtensionsState、--no-profile 清空、否则 recipe/enabled 列表，CLI flag 永远最后叠加（builder.rs:411-431）。

**3. REPL 与 headless 共享同一条 reply 消费管道**。interactive/headless（mod.rs:480/1123）只是外壳差异（hook、横幅、是否循环），process_agent_response 完全复用，交互性由 `interactive: bool` 参数渗透到两处行为差异：工具确认弹窗 vs AllowOnce、工作目录切换询问 vs 黄字警告（builder.rs:362-402）。这个单参数设计让 `goose run -s` 能在跑完初始输入后无缝落进 REPL（cli.rs:1740-1741）。

**4. 扩展装载的容错与顺序**。builder.rs:582 有条注释钉死了顺序约束："Extensions are loaded after session creation because we may change directory when resuming"——resume 可能 chdir（builder.rs:378-389），扩展进程的工作目录必须取切换后的，所以必须先建会话再拉扩展。并发 JoinSet + 失败仅警告（builder.rs:186-221）则把"扩展起不来"从致命错误降级为可用性损失。

**5. 无头安全契约**。mod.rs:1190-1203 那段错误信息值得整段读：headless + Approve/SmartApprove 被判定为"invalid configuration"直接终止，而不是静默 auto-allow——注释写明理由是"auto-allowing would bypass the safety contract those modes are meant to enforce"。默认 headless 下普通确认降级 AllowOnce + warn（mod.rs:1204-1208）。即：无头自动化=Auto 模式的天下，审批型模式必须有人在屏幕前。

## 新人提示

**加一个子命令的五步清单**（以现有代码为模板）：① 在 Command 枚举加变体与 #[command] 属性（cli.rs:781-1141 内选一个简单变体如 Project，cli.rs:887 为例）；② 参数要么内联要么抽 Args 组（学 ExtensionOptions 的 flatten 用法，cli.rs:160-195）；③ 在 `get_command_name` 补一行日志名（cli.rs:1280-1309，漏了会只丢遥测不报错）；④ 在 cli() 的 match 加分支（cli.rs:2089-2226）；⑤ 复杂逻辑放 commands/ 下独立文件（参考 commands/skills.rs 的薄处理器模式）。涉及 agent 会话的命令不要自己 new Agent——填 SessionBuilderConfig 走 build_session。

**调试会话恢复**：resume 全链路有两处 session id 仲裁，容易混——cli.rs 的 get_or_create_session_id 负责"建新或按 --name/--session-id/--path 解析"，builder.rs 的 resolve_session_id 负责"no_session 隐藏会话/resume 校验/直接透传"。排查 resume 问题先看会话文件是否存在（`goose session list`），再注意 builder.rs:330-336 在没给 id 时取的是 `sessions[0]`（列表默认降序即最新）。恢复后历史能拉回是因为 CliSession::new 从 session_manager 读回 conversation（mod.rs:254-260）；工作目录不一致会弹确认框（builder.rs:363-376），脚本化 resume 记得这条交互路径。

**坑清单**：① builder.rs:338-340 对 `session_config.session_id` 直接 unwrap，安全性依赖调用方先经 get_or_create_session_id 的约定——绕过 handle_* 函数直接调 build_session 且不传 id 会 panic，推断这是刻意的不防御（仓库 AGENTS.md 明言"trust Rust's type system / avoid overly defensive code"）；② `Arc::try_unwrap(...).unwrap_or_else(panic)`（builder.rs:600）同样假设扩展装载的克隆引用已全部释放；③ ctrl-C 不是退出而是"中断本轮"——伪造 tool_response + 助手追问（mod.rs:1398-1470），想要真退出用 Ctrl-D（input.rs 的 Exit 路径）；④ --output-format json 会吞掉所有人类可读输出只留最终 JSON（mod.rs:1344-1369），调试时别开着 json 模式找日志；⑤ recipe 的 --explain/--render-recipe 在 parse_run_input 里早退（cli.rs:1640-1650），返回 None 后 handle_run_command 直接 Ok(())（cli.rs:1692-1694）——表现为"命令静默成功"，不是 bug。
