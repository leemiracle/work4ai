# 10 · context_mgmt：上下文压缩——长会话的生存机制

> 依据 commit 390dfb8c 源码实证。核心文件：`crates/goose/src/context_mgmt/mod.rs`（815 行）、`crates/goose/src/token_counter.rs`（327 行）、`crates/goose/src/agents/agent.rs`（触发点）、`crates/goose/src/prompts/compaction.md`（摘要模板）。

## 一、角色定位：reply 循环里的"安全气囊"

goose 是长任务的 agent：一个会话动辄几十轮工具调用，每次工具响应（文件内容、shell 输出、搜索结果）都会追加进会话，上下文只增不减。context_mgmt 子系统就是这道单行道的泄压阀——它不改变"对话看起来什么样"（用户视角历史完整保留），只改变"模型看到什么"（agent_visible 视图被重写）。

在 16 层图谱架构中，`context_mgmt/mod.rs` 被归入第 4 层「配置·安全·网关与提示词资产」（因其强依赖 `Config` 与 prompt 资产），而 `token_counter.rs` 归第 0 层「Agent 会话引擎」（knowledge-graph.json layers 实证）；就运行时行为而言，它是第 0 层 reply 循环的活体组件——每次 `Agent::reply()`（agent.rs:1406）都有三处经过它：

1. **入口预检**：reply() 在启动流之前调用 `check_if_compaction_needed`（agent.rs:1536），超阈值则先压缩再进入 `reply_internal`（agent.rs:1616）；
2. **循环中后台摘要**：reply_internal 的工具循环每轮 provider 返回后 spawn `maybe_summarize_tool_pairs`（agent.rs:1792），渐进瘦身；
3. **错误恢复**：provider 抛 `ContextLengthExceeded` 时循环内紧急压缩重试（agent.rs:2138）。

此外还有第四条手动通道：用户输入 `/compact` 命令走 `handle_compact_command`（execute_commands.rs:131，命令名注册于 :29，分发于 :109）。

一个重要边界：`manages_own_context()` 返回 true 的 provider（claude_code.rs:641、gemini_cli.rs:188、acp/provider.rs:417）自带上下文管理，goose 侧全部跳过（mod.rs:192-194、:543），base.rs:648-652 的文档注释明说"provider 的内部状态是唯一事实源"。

## 二、内部结构：四个函数各管一段

### 2.1 token_counter.rs——本地计数口径

压缩判定的分母来自 `provider.get_model_config().context_limit()`（model.rs:370-372，未配置时 `DEFAULT_CONTEXT_LIMIT = 128_000`，model.rs:11）；分子则有两条口径（mod.rs:206-221）：

- **优先真实值**：`session.total_tokens`（session_manager.rs:69 的 `Option<i32>` 字段，由 provider 每轮上报的 usage 累写）非空时直接采用，token 来源标记为 `"session metadata"`；
- **兜底估算**：为空时用 `create_token_counter()` 逐条统计 agent_visible 消息（mod.rs:213-217），标记 `"estimated"`。

估算器的实现是 OpenAI 口径的复刻：`o200k_base` 分词器经 `OnceCell` 全局单例懒加载（token_counter.rs:10、:205-213），每条消息固定加 4 token（:135），工具定义按 function-call 结构常量模型估算（FUNC_INIT=7、PROP_KEY=3、FUNC_END=12 等，:15-20），末尾再加 3 token "Reply primer"（:168）。计数结果走 blake3 哈希 + 长度做 key 的 LRU 缓存（容量 1024，:12、:27-40），纯文本计数命中缓存即免分词（:53-73）。

### 2.2 check_if_compaction_needed——阈值判定（mod.rs:186-231）

判定逻辑极简：`usage_ratio = current_tokens / context_limit`（:223），超过阈值即需压缩（:228）。阈值默认 `DEFAULT_COMPACTION_THRESHOLD = 0.8`（:20），可经 `GOOSE_AUTO_COMPACT_THRESHOLD` 覆盖（:198-202）；阈值 `<= 0.0 或 >= 1.0` 视为关闭自动压缩（:225-227）。

### 2.3 compact_messages / do_compact——压缩执行（mod.rs:66-183、:283-353）

`compact_messages` 做可见性改写与消息重组（详见第四节），真正的 LLM 调用在 `do_compact`：

- 先过滤出 agent_visible 消息（mod.rs:288-292）；
- 逐次尝试裁剪比例 `removal_percentages = [0, 10, 20, 50, 100]`（:295）——先完整送摘要，摘要请求本身超限时按 `filter_tool_responses` **middle-out**（从工具响应序列中位点向两侧扩展，:257-273）逐级丢弃工具响应，每级至少删 1 条（:255）；
- 每次尝试把消息用 `format_message_for_compacting` 展平成文本（:300-304），填入 `compaction.md` 模板渲染系统提示（:310），配一条固定的用户消息 "Please summarize the conversation history provided in the system prompt."（:312-313）；
- 调 `provider.complete_fast`（:316-318）——fast model 优先、失败回退主模型（base.rs:496-518）；
- 摘要响应的 role 被改写为 `Role::User`（:321）；usage 缺失时经 `ensure_usage_tokens` 兜底估算（:323-331）；
- 全部裁剪档位仍 `ContextLengthExceeded` 则报错放弃（:336-343）。

`format_message_for_compacting`（:355-432）是消息到文本的降维映射：文本原样（:360）、图片降为 `[image: mime]` 占位（:361）、tool_request 序列化为 `tool_request(name): args`（:362-373）、tool_response 抽取纯文本项（:374-392）、Thinking/RedactedThinking **直接丢弃**（:414-415），最终拼成 `[role]: content` 行（:427-431）。

### 2.4 工具对摘要——增量瘦身（mod.rs:434-565）

与"整场压缩"并存的轻量机制：单个工具调用对（request+response）单独让 LLM 写一句话摘要。

- **触发量 cutoff**：`compute_tool_call_cutoff(context_limit, threshold)` = `(3 * effective_limit / 20_000).clamp(10, 500)`（:440-441），即有效上限（limit×threshold）的万分之 1.5，128K 上下文得 15、200K 得 24、1M 得 120（测试 :734-750 钉版）；
- **滞回触发**：`tool_ids_to_summarize` 先保护最近 `protect_last_n` 个工具调用（agent.rs:1783-1788 传入本 turn 的工具数），剩余 eligible 数 `<= cutoff + 10` 则不动（:466-469），超出才取**最老的** 10 个（`TOOLCALL_SUMMARIZATION_BATCH_SIZE`，:22、:471-474）——保护带 + 批大小共同构成防抖；
- **执行**：`summarize_tool_call`（:477-534）把匹配 tool_id 的消息对送 `complete_fast`，系统提示是**内联 indoc! 字符串**（:512-523），不走 prompt_template 模板——与 compaction.md 的模板化路线刻意不同；摘要消息继承原消息对的 created 时间戳（:530）且 role=User（:529）、agent_only（:531）；
- **编排**：`maybe_summarize_tool_pairs`（:536-565）受 `GOOSE_TOOL_PAIR_SUMMARIZATION`（默认 true，:24-28）与 `manages_own_context`（:543）双闸控制，满足条件则 `tokio::spawn` 后台 JoinHandle 逐个摘要（:552-564），不阻塞主循环。

### 2.5 入口裁剪（上游第一道防线）

工具响应在进会话**之前**就有体量限制：`large_response_handler.rs` 的 `process_tool_response`（:16）对超过 200_000 字符的文本响应写入临时文件（`goose_mcp_responses/` 目录，:69-75），替换为"内容在文件 X 里，可用工具查看"的引用消息（:29-35）；阈值可经 `GOOSE_MAX_TOOL_RESPONSE_SIZE` 调整（:10-13）。调用点在 agent.rs:482 的 dispatch 路径上。

## 三、外部连接

**上游**：
- `Agent::reply()` 传入会话与 provider（agent.rs:1406）；会话消息经 moim 注入（agent.rs:1767）后送 provider；
- `Session` 结构（session_manager.rs:56-90）提供 total_tokens 判定输入与会话消息本体。

**下游**：
- **provider**：`complete_fast` 承载两次摘要调用；`stream_response_from_provider` 消费压缩后的会话；
- **prompt_template.rs**：`TEMPLATE_REGISTRY` 十模板（:8-49）中 `compaction.md` 在 :15-18 注册，描述为"Prompt for summarizing conversation history when context limits are reached"；`render_template` 支持用户自定义覆盖（模板目录 `include_dir` 打包 + 运行时可替换）；
- **SessionStorage**：`replace_conversation`（session_manager.rs:367-369）把压缩后会话整段落库；工具对摘要走细粒度 `update_message_metadata` + `add_message`（agent.rs:2342-2346）。

**事件面**：压缩过程向 UI 发三类 AgentEvent——InlineMessage 进度提示（"Exceeded auto-compact threshold of 80%..." agent.rs:1556-1560）、ThinkingMessage（`COMPACTION_THINKING_TEXT` = "goose is compacting the conversation..."，agent.rs:69、:1568-1572）、`HistoryReplaced`（agent.rs:1587、:2158）通知客户端整体刷新历史。

**指标面**：`update_session_metrics`（reply_parts.rs:499）对压缩 usage 特殊处理——`is_compaction_usage=true` 时"摘要输出成为新的输入上下文"（reply_parts.rs:530-533），即 total_tokens 被改写为摘要的 output_tokens，这是下一轮 `check_if_compaction_needed` 读到"真实压缩后水位"的关键闭环。

**subagent 隔离**：subagent_handler.rs:167-168 为子代理构造全新 `Conversation`（仅含任务指令一条 user 消息），不继承主会话历史——上下文天然隔离，子代理自行走独立的压缩路径，与主会话压缩无联动（此为源码事实；"因此无需跨会话压缩协调"为推断）。

## 四、数据流：一次自动压缩的完整路径

以"用户追问触发入口预检"为例：

1. **检测**：reply() 取出会话 → `check_if_compaction_needed`（agent.rs:1536-1543）→ manages_own_context 检查（mod.rs:192）→ 取 context_limit 与 total_tokens/估算值 → `usage_ratio > 0.8` 判定（mod.rs:223-229）；
2. **通知**：yield InlineMessage（阈值百分比）+ ThinkingMessage（agent.rs:1554-1572）；
3. **选取保留范围**：`compact_messages` 找最近一条 agent_visible、纯文本（无 tool 内容，mod.rs:76-88 判定）的 user 消息作为保护对象（:111-126），记录它是否是末位消息（`is_most_recent`，:119）；
4. **模板改写**：`do_compact` 渐进裁剪 + `format_message_for_compacting` 展平 + `render_template("compaction.md")`（:310）+ `complete_fast` 摘要；compaction.md 模板要求输出九节结构化摘要（User Intent / Technical Concepts / Files + Code / Errors + Fixes / Problem Solving / User Messages / Pending Tasks / Current Work / Next Step），先在 `<analysis>` 标签内 chronological 审视，并明示"这个摘要只有你自己读，可以比给人看的摘要长得多""不要遗漏任何对继续会话重要的信息"；
5. **会话替换**：原消息全部改为 `with_agent_invisible`（mod.rs:139-151，用户仍可见、模型不再看到）；末位保护消息原副本改 `MessageMetadata::invisible()`（:145）；摘要消息 `agent_only`（:153）；追加 continuation 消息——按 manual/is_most_recent/其余三选一（:157-163），内容统一是"你的上下文被压缩过，上一条消息是摘要，**不要提及**读过摘要，自然继续"（:30-43）；`merge_consecutive_messages` 合并（:170）；最后若保护的是历史位置消息，追加 fresh copy 的 user 消息（:173-177）——模型看到"摘要 + 原始最新提问"，对最新指令零损耗；
6. **落库与广播**：`replace_conversation` 整体替换（agent.rs:1584）→ `update_session_metrics(is_compaction_usage=true)` 重置水位（agent.rs:1585）→ `AgentEvent::HistoryReplaced` 通知 UI（agent.rs:1587）→ 进入 `reply_internal` 正常应答。

**恢复压缩变体**（agent.rs:2112-2163）：循环内 `ContextLengthExceeded` → attempts+1，已达 2 次则告知用户"Try using a shorter message, a larger context window, or start a new session"并退出（:2114-2122）；否则同样 compact_messages → 替换会话 → `did_recovery_compact_this_iteration = true`（:2150）→ break 后从最近 user 消息继续（:2251-2253）。

**工具对摘要变体**（agent.rs:1789-1798、:2320-2353）：每轮 spawn 后台任务，循环结束时 `task.await` 收结果；对每个 (summary, tool_id) 找到匹配的 request/response 消息对，**恰好 2 条**（:2337 的 `matching_ids.len() == 2` 校验）才把原对置 agent_invisible 并 add_message 摘要；取消时 `task.abort()`（:2321-2323）。回填后下一轮 provider 调用自然瘦身。

## 五、设计决策

1. **为何 LLM 改写而非截断**：compaction.md 模板的设计是把摘要当"给未来自己的工作交接"——九节结构覆盖 Files+Code（完整代码）、Errors+Fixes、Pending Tasks，且"truncate long tool call arguments or results"仅对工具参数降精度，用户消息与决策全程保留；结尾铁律"No new ideas unless user confirmed"防摘要器自由发挥。截断会随机丢中段信息，而结构化摘要保留任务连续性——这是 agent 会话（强依赖早前文件修改记录）的刚需。（决策动因无代码注释，标注为**推断**；模板内容为源码事实。）
2. **阈值 0.8 的安全边际**：默认在 80% 水位触发（mod.rs:20），留 20% 余量容纳"当前轮 system prompt + tools 定义 + 即将进行的工具循环"；`compute_tool_call_cutoff` 同样用 `context_limit × threshold` 做有效上限（mod.rs:440），两套机制共享同一阈值语义，用户调一处即同时影响两条防线。
3. **可见性双轨而非删除**：压缩从不删消息，只翻转 `agent_visible`（message.rs:667、:711-714）。用户 UI 完整历史与模型上下文解耦——这是"数字取证可回溯"与"模型瘦身"的兼得方案，也是 `replace_conversation` 能放心整体落库的前提。
4. **工具响应为何单独裁剪**：三层理由。其一，体量分布极不均——工具响应（文件全文、JSON 大对象）通常占上下文大头而信息密度低，`format_message_for_compacting` 把它降为一行文本、`filter_tool_responses` 只挑它裁剪、工具对摘要只处理它，用户文本永远不进裁剪名单（mod.rs:244-249 只收集含 ToolResponse 的消息）；其二，middle-out 保两端（最近的工具结果与最早的缘起请求最有价值，中段的中间态可牺牲，mod.rs:257-273）；其三，入口处 200K 字符熔断（large_response_handler.rs:8）把单点爆炸在进会话前就转为文件引用。（"最有价值"的价值判断为**推断**，裁剪算法为源码事实。）
5. **恢复压缩的双重保险**：`do_compact` 内部五档渐进（0→100%）解决"摘要请求本身超限"；agent 循环层 `compaction_attempts >= 2` 熔断（agent.rs:2114）解决"压缩后仍超限"的死循环——两层各管一种失败模式。
6. **信任边界**：CLI 包装类 provider 声明 `manages_own_context` 后，goose 侧自动压缩与工具对摘要全部让位（mod.rs:192、:543）——不做双重压缩，避免与 Claude Code/Gemini CLI 自身的 compact 机制打架。

## 六、新人提示

**调参入口**（全在 `goose configure` / 配置文件）：
- `GOOSE_AUTO_COMPACT_THRESHOLD`：0-1 之间生效，设 0 或 1 即关闭自动压缩（mod.rs:225-227）；调低会更早压缩、保留更多近期细节但摘要更频繁；
- `GOOSE_TOOL_PAIR_SUMMARIZATION`：默认 true，设 false 关闭工具对摘要（mod.rs:24-28）；
- `GOOSE_MAX_TOOL_RESPONSE_SIZE`：单条工具响应字符熔断阈值，默认 200_000（large_response_handler.rs:8-13）；
- `GOOSE_TOOL_CALL_CUTOFF`：直接钉死工具对摘要触发线，跳过按上下文比例计算（agent.rs:655-658）。

**观察压缩效果**：
- 日志：`info!("Performing message compaction")`（mod.rs:72）；失败时 `warn!("Failed to summarize tool pair: ...")`（mod.rs:559）与 `error!("Compaction failed: ...")`（agent.rs:2157）；
- UI 侧：InlineMessage 显示阈值百分比与 "Compaction complete"（agent.rs:1556、:1592），HistoryReplaced 事件触发渲染层整体刷新历史；
- 会话 JSON：`total_tokens` 字段在压缩后被摘要输出量覆盖（reply_parts.rs:530-537），可据此看真实压缩后水位。

**坑**：
- **token 口径混用**：判定分子可能是 provider 真实 usage 也可能是 o200k 估算（mod.rs:206-221），两者对同一段文本可有 10-20% 偏差；估算只数 agent_visible 消息（token_counter.rs:143-145），若会话 metadata 断档，压缩会"突然提前或滞后"；
- **摘要也会超限**：超长会话首次摘要请求可能自身 `ContextLengthExceeded`，此时静默升级裁剪比例（mod.rs:336-338），外表只是压缩变慢；五档全爆才会报错；
- **模板可被用户覆盖**：compaction.md 支持自定义（prompt_template.rs 的 user_content 机制），替换后的模板必须保留 `{{ messages }}` 占位符，否则渲染失败直接打断压缩；
- **工具对摘要的静默跳过**：matching_ids 不等于 2（如工具对被之前的压缩改写）只 warn 不重试（agent.rs:2350-2353）；后台任务失败也只逐个 warn（mod.rs:558-560）——摘要缺失不致命，但上下文会比预期大；
- **手动 /compact 不保护最新消息**：manual_compact=true 时跳过"保留最近 user 消息"逻辑（mod.rs:124-126），摘要里虽有 User Messages 节，但模型对最新指令的字面精度依赖摘要质量——手动压缩后最好重申关键诉求（行为差异为源码事实，建议为**推断**）。

---

**本篇锚点**：mod.rs:20/22/24-28/30-43/66/72/76-88/111-126/130-131/139-151/153/157-163/170/173-177/186-194/198-202/206-221/223-229/233-249/255/257-273/283-292/295/297-318/321/323-331/336-343/355-361/362-373/374-392/414-415/427-431/434-441/444-475/466-469/471-474/477-534/512-523/529-531/536-565/543/552-564/559/734-750；token_counter.rs:10/12/15-20/27-40/53-73/135/143-145/168/205-213/215-217；agent.rs:33-34/69/1406/1536-1543/1554-1572/1575/1584/1585/1587/1589-1594/1616/1681/1697/1700/1767/1783-1788/1792/1798/2112-2122/2138/2148-2150/2157/2251-2253/2320-2328/2337/2342-2346/2350-2353；prompt_template.rs:8-49/15-18；session_manager.rs:56-90/69/367-369；reply_parts.rs:499/530-537；execute_commands.rs:29/109/131/138；base.rs:496-518/648-652；claude_code.rs:641；gemini_cli.rs:188；acp/provider.rs:417；model.rs:11/370-372；large_response_handler.rs:8/10-13/16/29-35/69-75；message.rs:667/711-714；subagent_handler.rs:167-168。
