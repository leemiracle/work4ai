# 01 · agent.rs：reply 主循环——goose 会话引擎的心脏

> 文件：`crates/goose/src/agents/agent.rs`（3395 行）。goose 的 Agent 会话引擎核心：`reply` 主循环、`dispatch_tool_call` 工具分发、重试控制与配方生成。AGENTS.md 把它列为四大入口之一（`Agent: crates/goose/src/agents/agent.rs`）。图谱节点 `file:crates/goose/src/agents/agent.rs` 摘要钉版："reply 主循环（806 行 reply_internal）、工具分发、扩展装载、provider/模式切换、配方生成与系统提示词管理"。

## 角色定位（在 16 层架构哪一层、被谁调用、职责边界）

在 understand 图谱的 16 层架构中，本文件属于第一层 **「Agent 会话引擎（goose 核心）」**（68 节点），是该层的锚点文件。它向上屏蔽 LLM 与工具的全部细节，向下编排 Provider、扩展、权限、会话持久化四大子系统。

**被谁调用**：`Agent::reply`（agent.rs:1406）是全仓公共入口，实际调用方覆盖几乎所有前端形态（grep 实证）：CLI 会话 `crates/goose-cli/src/session/mod.rs:1167`、HTTP 服务端 `crates/goose-server/src/routes/reply.rs:314`、桌面推送 `session_events.rs:342`、ACP 协议层 `acp/server.rs:2416`、网关 `gateway/handler.rs:356`、定时调度器 `scheduler.rs:927`、平台编排器 `platform_extensions/orchestrator.rs:488`，以及 subagent 复用（见下）。一个入口服务七种宿主，这是它成为"心脏"的直接证据。

**职责边界**：本文件只负责**会话回合编排**——一轮用户输入如何变成 N 个 provider 流式回合 + M 个工具调用 + 持久化事件流。它不实现具体工具（在 goose-mcp 扩展仓）、不实现 LLM 协议（在 goose-providers 仓）、不管 Agent 实例生命周期（`execution/manager.rs:35` 的 `AgentManager` 用 LRU 缓存 100 个 `Arc<Agent>` 并持有创建锁，Agent 本身不管自己被谁缓存）。图谱 languageNotes 钉版："许多 agent/* 文件是对 Agent 的分文件 impl 扩展"——`reply_parts.rs`、`tool_execution.rs`、`execute_commands.rs`、`schedule_tool.rs` 各自续写 `impl Agent` 块，agent.rs 是这个分体式巨兽的躯干。

## 内部结构（reply/reply_internal/dispatch_tool_call/委派与重试的分段精讲）

文件呈"常量与自由函数 → 类型定义 → impl Agent 主体 → 测试模块"四段布局。

**基础段（1-300 行）**：`DEFAULT_MAX_TURNS: u32 = 1000`（agent.rs:67）是无用户输入时的回合上限；`DEFAULT_STOP_HOOK_BLOCK_CAP = 8`（agent.rs:68）防 Stop 钩子死循环。`categorize_tool`（agent.rs:80）用 `rsplit("__")` 剥扩展前缀后按工具名归类 Shell/Read/Write/Other——这决定扩展钩子事件映射（如 `BeforeShellExecution`，agent.rs:416）。`ReplyContext`（agent.rs:132）打包每轮所需的会话、双工具表（tools/toolshim_tools）、系统提示词、模式和 `tool_call_cut_off`。

**Agent 结构体（agent.rs:226）**：核心字段全部 `pub(super)`，供分文件 impl 直访：`provider: SharedProvider`（运行时可换模型）、`extension_manager`、`prompt_manager`、`retry_manager`（agent.rs:241）、五监察官组成的 `tool_inspection_manager`、`hook_manager`、以及 goal/grind 两个"持续工作"状态槽。事件枚举 `AgentEvent`（agent.rs:252）只有三个变体：Message / McpNotification / HistoryReplaced——这是引擎对外的全部词汇表。构造在 `with_config`（agent.rs:312）里一次性装配监察官链（agent.rs:534 起：Security → Egress → Adversary(LLM 审查) → Permission → Repetition，按注释顺序即优先级）。

**reply 外壳（agent.rs:1406-1614）**：做四件进主循环前的杂事。① 用户消息里若含 `ElicitationResponse`，直接提交 `ActionRequiredManager` 并返回空流（agent.rs:1429，注释钉版契约："Ok(empty) on accept, Err on reject"）；② 触发 `UserPromptSubmit` 钩子与斜杠命令 `execute_command`（agent.rs:1460）——`/compact`、`/clear` 这类改写历史的命令走旁路，直接 yield `HistoryReplaced`（agent.rs:1488）；③ 预检自动压缩 `check_if_compaction_needed`（agent.rs:1536），超阈值则先 `compact_messages` 再进循环（agent.rs:1575）；④ 最后 `reply_internal` 接管（agent.rs:1609）。

**reply_internal 主体（agent.rs:1616-2421，约 800 行）**：先 `prepare_reply_context`（agent.rs:627→1623）修复会话（`fix_conversation`）、装配工具与提示词、计算 cutoff；项目级指令追加进系统提示词（agent.rs:1636）；重置重试计数（agent.rs:1640）；`tokio::spawn` 异步生成会话名（agent.rs:1657，不阻塞回合）。然后进入真正的 `loop`（agent.rs:1706），每圈：

1. **终局出口三连**：先查 final_output_tool 是否已被调用（agent.rs:1711），有产出则 yield 终答并触发 Stop 钩子 `emit_blocking`（agent.rs:1727），Deny 则注入 nudge 消息重试，连堵超过 cap 就强退（agent.rs:1736）；回合计数（agent.rs:1756）超 `max_turns` 则礼貌询问是否继续（agent.rs:1758）。
2. **调 provider**：`inject_moim`（agent.rs:1767）注入共享记忆，`stream_response_from_provider`（agent.rs:1774，实现在 reply_parts.rs:252）起流；内层 `while let Some(next) = stream.next()`（agent.rs:1813）逐 chunk 消费。
3. **工具回合**：`categorize_tools`（agent.rs:1832 调用，结果在 agent.rs:1827 解构）把响应拆成前端请求与剩余请求；Chat 模式直接跳过所有后端工具并回填 `CHAT_MODE_TOOL_SKIPPED_RESPONSE`（agent.rs:1892）；否则五监察官审查（agent.rs:1904 `inspect_tools` + agent.rs:1913 权限归类 approved/needs_approval/denied），批准的走 `handle_approved_and_denied_tools`（agent.rs:702 定义 / agent.rs:1938 调用）→ `dispatch_tool_call`，拒绝的回填 `DECLINED_RESPONSE`（agent.rs:744 的 `handle_denied_tools`）；需审批的经 `handle_approval_tool_requests`（tool_execution.rs:77）产出确认流。
4. **工具结果泵**：`stream::select_all`（agent.rs:1967）合流所有工具流，内层 `tokio::select! { biased; ... }`（agent.rs:1979）一边收结果一边每 100ms 让位排干 elicitation 消息（agent.rs:1975 与 agent.rs:2023 的 sleep 分支）——`biased` 保证工具结果优先。
5. **错误分流**：`ContextLengthExceeded` 触发恢复性压缩，最多试 2 次（agent.rs:2109 / agent.rs:2114 `compaction_attempts >= 2`）；`CreditsExhausted` 带 top_up_url 通知（agent.rs:2167）；`NetworkError` 与通用错误分别措辞后 break（agent.rs:2191 / agent.rs:2202）。
6. **收尾**：工具集变更则重装配提示词（agent.rs:2215），子目录提示线索也会触发重装配（agent.rs:2225 `load_subdirectory_hints`）；`no_tools_called` 时走终局决策树（agent.rs:2232）：final_output 未调用则注入续跑指令（agent.rs:2242）、goal 未达标注入自查 nudge（agent.rs:2254）、grind 模式强制续干（agent.rs:2273）、否则清 goal/grind 并交 `handle_retry_logic`（agent.rs:2294）裁决重试或退场；消息统一落库（agent.rs:2372 `session_manager.add_message`）；`exit_chat` 再过一次 Stop 钩子（agent.rs:2377-2405，与终答出口共用同一套 cap 逻辑）。

**dispatch_tool_call（agent.rs:916-1058）**：单工具分发漏斗。顺序为：记录参数痕迹（prompt_manager）→ PreToolUse 阻塞钩子，Deny 返回"policy denial, not a transient failure"错误（agent.rs:948-963，明确告知模型不要重试）→ 平台调度工具旁路（agent.rs:978）→ final_output 工具旁路（agent.rs:998）→ 前端工具守卫（agent.rs:1024，引擎侧直接报"Frontend tool execution required"，等前端通过 `handle_tool_result` 回灌）→ 默认走 `extension_manager.dispatch_tool_call`（agent.rs:1031）到 MCP 客户端。所有出口统一包 `with_post_tool_hook`（agent.rs:464），在 future 内完成后处理大响应并按成败发 PostToolUse/PostToolUseFailure。

**委派与重试**：subagent 委派**不在本文件**——`subagent_handler.rs:141` 新建独立 `Agent::with_config`，换 provider、只装 `task_config.extensions` 白名单扩展、`override_system_prompt`（subagent_handler.rs:165），然后在 subagent_handler.rs:185 **复用同一个 `reply()`**。也就是说递归发生在"新 Agent 实例"层而非引擎内部循环里。重试则由 `session_config.retry_config`（types.rs:23 的 `RetryConfig`：max_retries/checks/on_failure/双超时）驱动：agent.rs:574 薄封装转发到 `RetryManager::handle_retry_logic`（retry.rs:114），后者跑 SuccessCheck（shell 命令验证配方是否真完成），失败且未超额则 `reset_status_for_retry` 把会话**整体回滚到 initial_messages**（retry.rs:99-108，含清空 final_output 状态），主循环拿到 `Retried` 后 `replace_conversation` + `HistoryReplaced` 重启（agent.rs:2294-2300）。

## 外部连接（依赖谁/被谁依赖）

图谱记录本文件 54 条出边（imports）+ 4 条入边。核心依赖五组：

- **Provider**（`providers/base.rs`，`SharedProvider = Arc<Mutex<Option<Arc<dyn Provider>>>>`）：运行时热切换（agent.rs:2449 `update_provider`）、会话恢复带回退（agent.rs:2496 `restore_provider_from_session`，会话 provider 失效时回退全局配置并落库）。注意 provider 也参与权限路由（agent.rs:1378 `PermissionRouting::ActionRequired` 时确认直接交 provider 处理）。
- **ExtensionManager**：工具的分发与清单全走它（agent.rs:1031 分发、agent.rs:1309 `list_tools` 聚合扩展工具 + 前端工具 + 调度工具 + final_output 工具）；扩展增删后状态持久化到 session（agent.rs:1062 `save_extension_state`），恢复会话时 `load_extensions_from_session` 并行装载（agent.rs:1108，`join_all` 后一次性持久化）。
- **SessionManager**：每条消息双写（内存 conversation + 落库，agent.rs:2372）；`HistoryReplaced` 事件在压缩/重试后通知 UI 重拉。
- **AgentManager**（execution/manager.rs:35）：反向持有 `Arc<Agent>` 做 LRU 池，是 server/desktop 形态的实例工厂，agent.rs 只被它用而不知道它。
- **入边 4 条**：`reply_parts.rs` / `mod.rs` / `tool_execution.rs` imports（分文件 impl 的循环引用是 Rust 同模块常态）+ `document:AGENTS.md -> agent.rs [documents]`——AGENTS.md 的 Entry Points 节直接点名本文件。

## 数据流（一次用户输入进来后函数级流转）

以 CLI 敲入"帮我重构这个函数"为例：

1. 宿主（如 goose-cli session/mod.rs:1167）调 `agent.reply(user_message, session_config, cancel_token)`（agent.rs:1406），拿回 `BoxStream<Result<AgentEvent>>`。
2. 外壳三闸：elicitation 检查（agent.rs:1419）→ UserPromptSubmit 钩子 → 斜杠命令分叉（agent.rs:1460，非命令则原样落库 agent.rs:1522）→ 自动压缩预检（agent.rs:1536）。
3. `reply_internal`（agent.rs:1616）`prepare_reply_context` 拿到修好的会话 + 工具表 + 提示词。
4. 进 `loop`（agent.rs:1706）→ `stream_response_from_provider`（agent.rs:1774；reply_parts.rs:252 先 `is_agent_visible` 过滤、toolshim 模式把工具消息转文本再调 `provider.stream`）。
5. 模型流回工具调用 chunk → `categorize_tools`（agent.rs:1827）拆分 → 监察官审查（agent.rs:1904）→ approved 直接 `dispatch_tool_call`（agent.rs:916）→ `extension_manager.dispatch_tool_call`（agent.rs:1031）发到 MCP server 进程。
6. 工具 future 经 `tool_stream`（agent.rs:276，select 合并通知流与结果 future）汇入 `stream::select_all`（agent.rs:1967），结果泵（agent.rs:1979）边收边 yield `McpNotification`/写回 `request_to_response_map`（agent.rs:2009-2012）。
7. 请求/响应消息对重组进 `messages_to_add`（agent.rs:2064 起，thinking 内容单独保真——agent.rs:2042 注释：Gemini 需回显 thinking、Kimi/DeepSeek 需 reasoning_content），落库（agent.rs:2372）并 extend 进内存会话（agent.rs:2375）。
8. 因为这轮调了工具，`no_tools_called=false`，循环回到第 4 步带着工具结果再问模型；直到模型只回文本（agent.rs:1864 `num_tool_requests == 0`），下一圈 `no_tools_called` 终局树（agent.rs:2232）→ 无 goal/grind/retry → `exit_chat` → Stop 钩子放行（agent.rs:2387）→ 流结束，宿主收到最后一条 Message 事件。

工具结果回环的关键设计：**模型永远看不到"流"**——流只面向宿主 UI；模型看到的是每圈重新组装的完整消息列表。

## 设计决策（为什么 reply_internal ~800 行不拆/重试与 SuccessCheck 的取舍/嵌套 subagent 为何禁止——从代码注释与结构推断）

**为什么 800 行不拆**：结构上，循环体内每一步都在读写同一组局部状态（`messages_to_add`/`no_tools_called`/`exit_chat`/`surfaced_thinking_in_turn` 等 11 个 loop 级变量，agent.rs:1691-1811），且 try_stream! 宏内 `yield` 无法跨函数边界——拆函数就得把这些状态装箱传递、把事件流改成显式 channel，复杂度反而升。团队的实际策略是"纵切"：把**无状态或自含**的阶段（工具分发、审批流、提示词装配、指标）切到分文件 impl（reply_parts.rs/tool_execution.rs），把**有状态闭环**留在原地。推断依据：reply_parts.rs:140 起的 `impl Agent` 与 languageNotes"分文件 impl 扩展"。

**重试与 SuccessCheck 的取舍**：重试不是"对 provider 错误重发"（那类错误在 agent.rs:2202 只提示用户重试），而是"配方任务没做对就整个回滚重来"——reset 到 initial_messages（retry.rs:105）意味着丢弃全部中间工作。代价激进，所以闸门有三重：`retry_config` 只由配方/调度场景携带（CLI 手聊通常为 None，直接 `Skipped`）；SuccessCheck 用 shell 命令做**外部可验证的完成判定**（不信模型自述）；`on_failure` 清理钩子先跑再回滚（retry.rs:159），保证副作用环境复位。推断：这套取舍服务于 scheduler.rs:927 的无人值守定时任务——无人确认时宁可重做也不能"看起来完成"。

**"嵌套 subagent 禁止"的实相（推断+实证）**：grep 全 agents 目录无 nest/depth/recursion 类守卫；agent.rs 引擎层根本**没有父子概念**（结构体无 parent 字段）。真正的机制是架构性隔离：subagent 是全新 Agent + 全新 session_id（subagent_handler.rs:141），父代理只能通过工具调用边界拿回最终字符串，子代理的工具表由 `task_config.extensions` 显式白名单（subagent_handler.rs:141-147 逐个 add_extension）决定。推断：深嵌套不被禁止而是被"每个子代理都要显式配扩展与提示词"的成本天然抑制；orchestrator 这类会生子的扩展若不进白名单，递归链在工具表层就断了。

## 新人提示（改这个文件的高频坑、测试入口、与 AGENTS.md 规约的呼应）

1. **锁不可重入**：tokio `Mutex` 非 reentrant。agent.rs:2233 注释钉版——取 `final_output_tool` 锁必须先取值 drop guard 再进 `handle_retry_logic`，因为后者内部也会锁同一把。任何新代码碰 `final_output_tool` 都要查这条。
2. **双份消息写入必须成对**：内存 `conversation.push/extend` 与 `session_manager.add_message` 落库是手工同步（agent.rs:2372-2375），漏一边就会出现 UI 与重放不一致。压缩/重试路径还要额外 `replace_conversation` + `HistoryReplaced` 事件。
3. **loop 级状态机的隐变量**：`retrying_after_stop_hook_denial`（agent.rs:1753）会抑制 `turns_taken` 递增——Stop 钩子拒绝后的重跑不计回合，改 max_turns 逻辑时别忽略。
4. **测试入口**：文件自带 `#[cfg(test)] mod tests`（agent.rs:2926），Stop 钩子 cap 行为有精确断言（agent.rs:3235 `stop_hook_block_cap_allows_configured_consecutive_blocks_then_overrides`，cap=2 时 provider 恰被调 3 次）；监察官齐全性有守卫测试（agent.rs:3340）。跑法按 AGENTS.md：`cargo test -p goose`；改动需过 `cargo fmt` + `cargo clippy --all-targets -- -D warnings`，server 无关不必重生成 openapi。
5. **AGENTS.md 规约呼应**：Entry Points 节点名本文件；"Error: Use anyhow::Result"在此文件全量执行（唯一例外是工具分发按 MCP 协议返回 `ErrorData`）；"self-documenting code"原则解释了源码注释稀疏而关键处注释极重（如 elicitation 契约 agent.rs:1423-1428）——新代码别写复述性注释，但"为什么"必须留。
6. **改工具链路先看 dispatch 顺序**：dispatch_tool_call 的六个出口（钩子拒绝/调度/final_output/前端/扩展/错误包装）有固定次序（agent.rs:934-1057），插新旁路放错位置会导致钩子被绕过或 post-hook 丢失。
7. **图谱导航**：想追某个具体行为的实现，先查分文件 impl——提示词与流（reply_parts.rs:141/252/372）、审批与前端工具（tool_execution.rs:77/163）、斜杠命令（execute_commands.rs:88）、重试（retry.rs:114）。agent.rs 里找不到的，多半在这些续写块里。

---

*行号锚基于当前工作树实测（3395 行版）；本篇锚点共 40+ 处，全部经 sed 逐行核验。*
