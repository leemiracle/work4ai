# browser_use/mcp/server.py — MCP 服务器

## ① 角色定位

server.py 把 browser-use 的能力包装成 Model Context Protocol 服务：外部 MCP 客户端（Claude Desktop、Claude Code 等）通过 stdio JSON-RPC 连进来，列举工具、调用工具。工具面分两档（文件头 docstring，server.py:3-7）：**直接浏览器控制**（browser_navigate/browser_click/browser_type/browser_get_state/browser_screenshot/browser_scroll/browser_get_html/browser_extract_content/页签管理五件套）走预置会话，模型一步一动作；**自治兜底** `retry_with_browser_use_agent`（工具定义在 server.py:392）起一个完整 Agent 跑多步任务，描述里明确"Only use this as a last resort if you fail to interact with a page multiple times"——设计意图是让客户端 LLM 先自己动手，反复失败才升级给专职 agent。另配 browser_list_sessions/browser_close_session/browser_close_all 三个会话管理工具。同类目录还有 cli_mcp.py（另一台面向 CLI 的 MCP 服务器）、controller.py、client.py 和 Claude Desktop 扩展的 manifest.json。

## ② 内部结构

文件前 150 行是**日志防御工事**，比例之大本身就是教训的化石：导入 browser_use 之前先设 BROWSER_USE_LOGGING_LEVEL=critical（server.py:30-31），`_configure_mcp_server_logging`（61）把 root 与所有已存在 logger 的 handler 换成 stderr，`logging.disable(logging.CRITICAL)`（90）兜底，再 `_ensure_all_loggers_use_stderr`（103）在每次 import 波后重扫——因为 stdio 通道同时是 JSON-RPC 传输层，任何一行日志漏进 stdout 都会腐蚀协议帧。核心类 BrowserUseServer（186）持五个协作者：mcp SDK 的 Server、config（load_browser_use_config）、BrowserSession、Tools、ChatOpenAI，外加 FileSystem（内容抽取落盘用）与 ProductTelemetry。`_setup_handlers`（211）注册四个 request handler（tools/list、resources/list、prompts/list、tools/call），工具清单是手写的 types.Tool 数组（216-455），每只带 input_schema，只读工具标 ToolAnnotations(read_only_hint=True)。`_execute_tool`（502）是大分发器：retry 工具与会话管理工具先截留，`browser_` 前缀的工具统一懒初始化会话后按名分派到 `_navigate`/`_click`/`_type_text` 等私有方法。会话管理块（1116-1243）维护 active_sessions 字典（id→session/created_at/last_activity/url），`_start_cleanup_task`（1230）起每 120 秒一轮的后台清理循环，超时（默认 10 分钟，构造参数 session_timeout_minutes）未活动的会话被自动关闭。入口 main（1264）打 start 遥测（含 get_parent_process_cmdline 采集的父进程链，155）、run、finally 里 stop 遥测加 flush。

## ③ 外部连接

向上：`browser-use --mcp` 命令（cli.py:75-77 经 `_run_mcp_stdio_server` 静默日志后 import 本模块跑 main）。向下大量复用主库：Agent/ActionModel（93）、BrowserProfile/BrowserSession（94）、Tools（98）、FileSystem（96）；LLM 侧默认 ChatOpenAI，retry 工具在 model_provider=bedrock 时切换 ChatAWSBedrock（669-679）；配置经 config.py 的 load_browser_use_config/get_default_profile/get_default_llm（95）读 config.json 与环境变量。工具执行全部经 BrowserSession 的 **event_bus.dispatch** 下发（NavigateToUrlEvent/ClickElementEvent/TypeTextEvent/ScrollEvent 等，766/793/877/1047），即 MCP 层与 watchdog 执行层完全解耦——server.py 自己几乎不直接摸 CDP，唯一例外是 `_get_html`（946）直接 Runtime.evaluate 取 outerHTML。遥测走 telemetry.MCPServerTelemetryEvent，tools/call 的 finally 块（484-495）逐调用记录工具名、时长、错误。

## ④ 数据流

**直接控制流**：客户端 tools/call → handle_call_tool（466）计时 → _execute_tool 分发 → 无会话则 `_init_browser_session`（585）：拼默认 profile（downloads 指向 ~/Downloads/browser-use-mcp、user_data_dir 指向 ~/.config/browseruse/profiles/default、wait_between_actions=0.5、keep_alive=True、有头，599-608）→ BrowserSession.start → 建 Tools/LLM/FileSystem → 后续每次调用 dispatch 事件 → watchdog 执行 → 结果字符串（或 _get_browser_state/_screenshot 的 [文本+ImageContent] 混合列表，546-560）回 CallToolResult。**Agent 兜底流**（651-753）：读 LLM 配置（Bedrock 分支/OpenAI 分支，OPENAI_API_KEY 缺失返回错误字符串）→ 关键安全逻辑：仅当客户端传了**非空** allowed_domains 才覆盖 profile（706-707），空列表视同未传——因为 SecurityWatchdog 把 `allowed_domains=[]` 解释为"无限制"，放行空列表等于静默解除管理员配置的白名单（注释 702-705 讲透了这层）→ 新建 BrowserProfile+Agent → agent.run(max_steps) → 汇总步数/is_successful/final_result/errors/urls → finally 里 agent.close。**生命周期流**：每个 browser_ 调用刷新 last_activity（_update_session_activity），清理循环按 10 分钟阈值回收。

## ⑤ 设计决策与取舍

一是**stdout 神圣不可侵犯**：三层日志压制+两次全局扫描的成本，换来 stdio 传输的绝对纯净——这是所有 stdio MCP 服务器的第一戒律，本文件是最详尽的实现样本。二是**事件总线作为唯一执行通道**：MCP 不直接调用浏览器方法，好处是安全策略（SecurityWatchdog 域名白名单）、下载处理、缓存失效等横切逻辑对 MCP 流量天然生效。三是**两档工具分级**：直接控制给客户端 LLM 精细操控权（配 browser_get_state 的 index 体系），agent 兜底用"last resort"话术约束滥用，兼顾成本与成功率。四是**返回错误字符串而非抛异常**：_navigate 等方法大量返回 'Error: No browser session active' 文本（758 等），把错误留给客户端 LLM 阅读、决策重试，而不是让 MCP 层反复重建会话。五是**敏感信息启发式**（855-875）：`_type_text` 对"含 @ 且像域名后缀"或"≥16 位混合字母数字加 .-_"的文本标 is_sensitive，回执只写 `Typed <email>`/`Typed <credential>`——刻意宽松的假阳性换日志不泄密，key_name 也只用泛化词防暴露检测模式。六是**空列表≠解除限制**的 allowed_domains 语义（见数据流），是安全设计与用户体验碰撞后选了安全。

## ⑥ 新人提示（坑/勘误）

- **logging.disable(CRITICAL)（90）把 logger.error 也吞了**：server.py:149 的"MCP SDK not installed"用 logger.error 打印，理论上被 90 行压制后不可见——调试 MCP 启动问题时优先看进程退出码而非日志；要加日志请直接 print(..., file=sys.stderr)。
- **browser_close 工具是半具尸体**：工具定义被注释掉（383-390），但 `_execute_tool` 里 `browser_close` 分支（571-572）还活着——客户端若手工构造 tools/call 请求仍能触发 `_close_browser`（1067），只是它不在 list_tools 清单里。
- **默认 LLM 型号字串是 'gpt-o4-mini'**（639）：与 retry 流程的 'gpt-4o'（686）拼写不一致，疑似笔误但如实在源码中，引用时别"顺手改正"。
- **单会话模型**：self.browser_session 只有一个，browser_close 后下一次 browser_ 调用会重新 _init_browser_session（528-529）；而 retry agent 每次调用新建独立 profile+session，不复用这个单例——两条流的会话彼此隔离。
- **_extract_content 动态造 ActionModel**（1018-1029）：用 pydantic create_model 现场拼 'ExtractAction' 再走 Tools.act，这是接 Tools 执行管的 hack 路径，改 ActionModel 结构时记得这条隐式依赖。
- **session_timeout_minutes=10 很短**：空闲 10 分钟浏览器就被后台循环杀掉，长间隔交互的客户端会莫名丢会话，list_sessions 的 age_minutes 字段可用来诊断。
- 遥测采集父进程命令行（1274）：这是有意为之（区分宿主是 Claude Desktop 还是别的），隐私敏感环境记得设 ANONYMIZED_TELEMETRY=false。
