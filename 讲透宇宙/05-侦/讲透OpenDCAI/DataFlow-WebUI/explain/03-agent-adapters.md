# 03 · Agent 适配器线：claude/codex 双活与 80 行中文系统提示词

## 角色定位

`backend/app/services/agents/` 让后端以子进程驱动编码 Agent CLI，把 stream-json 输出翻译成统一 `NormalizedEvent` 流经 WebSocket 透传给前端 ChatPanel——"对话式建 pipeline"的地基：用户说需求 → Agent 经 MCP 工具查算子/建 pipeline → `render_pipeline_in_editor` 把图同步回画布。`agent_session.py` 管会话（持久化/切换/终止），`base.py` 定契约，`factory.py` 分发，三个 adapter 各包一个 CLI。

## 内部结构

`base.py:3-11` 钉死六种事件：session/text_chunk/tool_call_start/tool_call_end/error/done；L30 `AGENT_KINDS = ("claude", "codex")`，L23-29 长注释解释 Cursor 为何不在此列。`ClaudeAdapter.chat_stream`（claude_adapter.py:41）拼命令行：`--print --output-format stream-json --verbose --include-partial-messages --mcp-config --append-system-prompt --allowedTools --permission-mode acceptEdits`，`--resume` 续会话（L69-70），10MB stdout 上限防大 MCP 结果（L77）。`_translate`（L118）把 stream_event/text_delta 转 text_chunk、拆 assistant 块的文本与 tool_use、提 user 块的 tool_result，result 块识别 `kvcache_no_enough`/`max_turns_exceeded` 给中文修复建议（L166-175）。`CodexAdapter`（codex_adapter.py:47）跑 `codex exec --json --sandbox workspace-write`——无 `--resume`（每轮无状态）、无系统提示词 flag（规则前置进 user message，L44-52）。`CursorAdapter`（cursor_adapter.py:48）191 行完整实现（含 `chat_id` 提取 L106-112、`model_call_id` 去重 L140-145），但 factory 不注册。

## 外部连接

`factory.py:43-68` 是唯一入口：env var `DATAFLOW_CLAUDE_CLI`/`DATAFLOW_CODEX_CLI` 可换 CLI 路径（L20-23），非法 kind 落回 `DEFAULT_AGENT="claude"`；请求 cursor 直接 raise 并指路 AGENT_SETUP.md（L64-68）。`agent_session.py:45-126` 是约 80 行中文 `SYSTEM_PROMPT`，核心纪律：算子查询走"categories→recommend→带 category 的 list_operators→按名查详情"四步且一轮 `list_operators` ≤2 次（L63-73）；`Write` 建 jsonl 后必须紧跟 `register_dataset` 并用返回的真实 id（L80-89）；create 前必须 `validate_pipeline_config`（L91-95）、严禁主动执行 pipeline（L97-100）、create/update 后立刻同步编辑器且一轮最多一次 create（L111-121）。L41 `ALLOWED_TOOLS = "mcp__dataflow__*,Read,Write,Edit"`；会话持久化 `backend/data/agent_sessions.json`（L38）；`endpoints/agent.py:103` 的 `/ws` 端点 + L51 `WebSocketManager` 单例负责定向推送。

## 数据流

前端 ws 消息（chat/abort/clear/new/switch，协议见 agent.py 文件头 docstring）→ `AgentSessionManager.chat_stream`（agent_session.py:265）归一 kind（切换 agent 等于换会话，L284-287）→ factory 造 adapter → 子进程跑 CLI（cwd=仓根，自动读 `.mcp.json` 与 `.claude/skills/`）→ stdout 逐行 json → `_translate` 归一化 → 首个 session 事件落盘建历史（L302-330，不透传前端）→ 其余事件 yield 给 ws 端点；MCP 侧 `render_pipeline_in_editor`（mcp_server.py:61-89 自定义路由）经 WebSocketManager 推 `sync_pipeline` 到画布。

## 设计决策（含批判）

- **钉版·dontAsk 陷阱**：claude_adapter.py:61-67 注释钉死 bug-003——`dontAsk` 自动批 MCP 工具但**拒绝内置 Write/Edit**，Agent 建不了数据集 .jsonl，整轮空转 `stop_reason=None`；改用 `acceptEdits`（L67）自动接受文件编辑同时保留其他护栏。选权限模式先问"内置工具批不批"，不是"越自动越好"。
- **钉版·真流式**：L52-57 注释钉死 bug-004——不加 `--include-partial-messages` 时整轮文本一次性到达，前端永远看不见"打字机"。两个 flag 都是踩坑后写进注释的运行时契约。
- **勘误·CursorAdapter 死代码**：base.py:23-29 与 factory docstring 明言 Cursor 官方用法是在 Cursor IDE 里连本仓 MCP（`.cursor/mcp.json`），后端不 headless 拉起 `cursor-agent`；类保留"for parity"但无生产路径可达。`model_call_id`/`timestamp_ms` 去重逻辑（L140-145）仍记录了 Cursor 流协议的坑，有文档价值。
- **勘误·DataFlowEngineError 双定义**：`dataflow_engine.py:28` 与 `ray_pipeline_executor.py:27` 各定义一个同名异常类——Python 里是两个不同类对象。`endpoints/tasks.py:238` 只 import 前者做 isinstance——ray 执行器抛的"自家"异常不会被认成同类型，错误分类降级（推断：影响文案不影响正确性；合并到一个模块才是正解）。
- **系统提示词即产品**：80 行中文 prompt 全是可执行纪律（配额/顺序/闭环），比"你有帮助的助手"类提示词工程化一个量级；代价是绑死中文，且与 skills/canonical 的英文 SKILL.md 存在双真源风险。

## 新人提示

调 Agent 不出活，先查两处：CLI 命令行 flag（adapter L47-68）和 SYSTEM_PROMPT 配额条款；`stop_reason=None` 空转九成是权限模式。加新 Agent 三步：继承 `AgentAdapter` 实现 `chat_stream`/`kill`/`is_running`、在 `_CLI_ENV_VARS` 与 `AGENT_KINDS` 注册、factory 加分支。会话问题先看 `agent_sessions.json`。改系统提示词要同步评估 skills 体系（见 06 篇）是否需要再生成。
