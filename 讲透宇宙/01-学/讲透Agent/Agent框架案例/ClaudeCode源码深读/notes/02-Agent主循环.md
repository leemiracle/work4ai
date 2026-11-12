# 02 · Agent 主循环：queryLoop 状态机

> card_id: ccsrc-02
> universe: Agent框架案例/ClaudeCode源码深读
> burke: 场景=思考-行动-观察循环要工程化；主体=query()/queryLoop()/QueryEngine 三层；能动=显式状态机+依赖注入；行动=7 continue/10 Terminal/五级压缩链；目的=多轮工具往返可控可恢复；张力=继续推进 vs 防死循环；弧线=while(true) 裸循环到 (state,event,config)=>state reducer 蓝图
> status: 已完成（2026-08-20，钉版 `091cde4`）
> refs: articles/02 + 03（流式）+ query.ts 源码抽查（State 10 字段已验证）
> updated: 2026-08-20

## 1. 入口分层

两个异步生成器分工：`query()`（query.ts:219）管单次用户回合内的多轮模型-工具往返；`QueryEngine.submitMessage()`（QueryEngine.ts:209）管回合级编排与 SDK 事件输出。

`query()` 只做一件事：`yield*` 委托 `queryLoop()`，正常返回后给本回合消费的队列命令补发 `completed` 生命周期通知（:230-238）。放在 `yield*` 之后是刻意的：抛异常时 error 穿透、`.return()` 同时关闭两个生成器，**"started-without-completed" 的不对称信号让上层能区分 turn 是否真跑完**。

`queryLoop()`（query.ts:241）入口把参数分四类：不可变 `params` 解构 → 依赖注入 `deps`（query.ts:263）→ 跨迭代可变 `state` → `buildQueryConfig()` 把 sessionId 与 4 个运行时门控**入口快照一次**（query.ts:295，防循环中途 statsig 翻转——`streamingToolExecution` 中途翻转会让流式/批量两路径同回合混用）。

Terminal 共 10 种 reason：blocking_limit / image_error / model_error / aborted_streaming / aborted_tools / prompt_too_long / completed / stop_hook_prevented / hook_stopped / max_turns。

## 2. State：10 字段与 7 个 continue 点

`State`（query.ts:204-217，**已抽查逐字验证**）：`messages`、`toolUseContext`、`autoCompactTracking`、`maxOutputTokensRecoveryCount`、`hasAttemptedReactiveCompact`、`maxOutputTokensOverride`、`pendingToolUseSummary`、`stopHookActive`、`turnCount`、`transition`。

设计约束写在注释里：**continue 点用 `state = {...}` 一次性整体替换**而非分散赋值，每个 continue 显式列出全部 10 字段、哪些被重置一目了然。`transition` 记录"上一轮为什么 continue"——供测试断言恢复路径 + **循环内部防死循环**。

7 个 continue 点（各带行号）：

| # | reason | 行号 | 语义 |
|---|---|---|---|
| 1 | collapse_drain_retry | :1115 | 上下文溢出先排空 staged collapse |
| 2 | reactive_compact_retry | :1165 | 413/媒体错误后的反应式压缩重试 |
| 3 | max_output_tokens_escalate | :1220 | 输出上限 8k→64k 原样重试 |
| 4 | max_output_tokens_recovery | :1251 | 注入"继续输出"meta 消息 |
| 5 | stop_hook_blocking | :1305 | stop hook 阻塞错误作为 user 消息回灌 |
| 6 | token_budget_continuation | :1340 | 预算未到 90% 的 nudge 续跑 |
| 7 | next_turn | :1727 | 正常工具结果回灌进入下一轮 |

**策略差异的样本**：`next_turn` 把 `maxOutputTokensRecoveryCount` 和 `hasAttemptedReactiveCompact` 都清零（新一轮带真实工具结果，恢复配额理应刷新）；`stop_hook_blocking` 只清前者——注释说明这是修过的 bug：若重置后者，"压缩→仍超长→报错→hook 阻塞→再压缩"会烧掉数千次 API 调用（:1294-1297）。**把状态机显式化的收益：不变量写在代码里**。

## 3. 单轮生命周期五阶段

**阶段 0**：每轮先 `yield {type:'stream_request_start'}` 分界信号；queryTracking 的 chainId 贯穿回合、depth 每轮 +1（:347-355）。

**阶段 1：五级压缩链（调模型前）**：`getMessagesAfterCompactBoundary`（:365）→ `applyToolResultBudget`（:379）→ 可选 snip 裁剪（:401-410）→ `deps.microcompact`（:414）→ 可选 context-collapse 投影（:441）→ `deps.autocompact`（:454）。**顺序有讲究：collapse 在 autocompact 之前，折叠后低于阈值则 autocompact 空转，保留更细粒度上下文**（:428-431）。压缩后硬阻塞线：自动压缩关闭且触及 blocking limit → `return {reason:'blocking_limit'}`（:641-647）；**fork 出的 compact/session_memory 查询显式豁免，否则压缩 agent 自己死锁**（:600-603）。（压缩体系全文见 04 篇）

**阶段 2：API 调用与 withhold**：收敛为 `deps.callModel`（:659），signal 接 abortController（:665）。外层 fallback 重试环：捕获 `FallbackTriggeredError` 切模型、清收集器、为已发 tool_use 补占位 tool_result（:900-903）。**withhold 机制**：可恢复错误（prompt-too-long/媒体过大/max_output_tokens）先不 yield 给 SDK 调用方但 push 进 assistantMessages（:799-825）——SDK 调用方见任何 error 字段就终止会话，提前 yield 会导致"恢复循环还在跑、调用方已终止"。流式 fallback 的一致性：旧消息（带签名 thinking）对新模型无效，先逐条 yield `tombstone` 让 UI 移除，再重建 StreamingToolExecutor 防孤儿 tool_result（:712-741）。assistant 消息 yield 前过 `backfillObservableInput`：工具可在克隆 input 上补派生字段给 SDK 看，**原始消息不动——任何 mutation 都会破坏 prompt 缓存字节对齐**（:747-787）。

**阶段 3：工具分发**：`streamingToolExecution` 开启时每个 tool_use 块一到达就喂 StreamingToolExecutor（:841-844）——**模型还在生成第三个工具调用的 JSON 时，第一个工具可能已经在跑**；否则流结束后 runTools 统一执行（:1380-1382）。`needsFollowUp` 是唯一路由信号：任何 assistant 消息含 tool_use 即置真（:832-835）；**注释指出 `stop_reason==='tool_use'` 不可靠，不能作为循环退出条件**（:554-556）。

**阶段 4：收尾分岔**：abort → 上一轮 toolUseSummary 在此 await（**Haiku 摘要与主流并行跑约省 1 秒**，:1055-1060）→ 恢复/停止判定或工具回灌。第 6 号 continue 背后是 tokenBudget 独立预算控制器：主线程专用（agentId 存在即 stop）；输出未达预算 90%（COMPLETION_THRESHOLD=0.9）注入 nudge 续推；**连续 3 次续跑且增量 <500 token 判定收益递减提前停**（tokenBudget.ts:59-90）——在"模型自己决定何时停"外加外部规则。

**阶段 5：stop hooks**：`handleStopHooks` 以 `yield*` 内联（:1267-1276），本身也是生成器：保存 cacheSafeParams → 触发 prompt suggestion/记忆提取/auto-dream（fire-and-forget）→ 执行用户 Stop hooks。**hook 的 blockingError 被包成 `isMeta:true` 的 user 消息回灌触发第 5 号 continue——"hook 让模型继续干活"不重启循环，而是把返回错误当新输入**。API 错误消息跳过 stop hooks 直接 completed（:1262-1265）——防"错误→hook 阻塞→重试→错误"死亡螺旋。工具摘要跨轮流水线：本轮收集 tool_use/result → Haiku 摘要 Promise 不 await 存入 `nextPendingToolUseSummary` → 下一轮模型流式期间（5-30 秒窗口）后台完成 → 流结束才 yield（:1437-1481）——**一轮的延迟被下一轮的等待吸收**。

## 4. QueryEngine：回合级编排

一会话一实例；`mutableMessages`/`totalUsage`/`readFileState` 跨回合存续（:175-183）。回合编排序列：wrappedCanUseTool（拒绝记入 permissionDenials）→ fetchSystemPromptParts → coordinator 叠加 → 三段拼 systemPrompt（custom/default + 记忆段 + appendSystemPrompt，:321-325）→ processUserInput 处理斜杠命令/附件 → **新消息先入 mutableMessages 并立刻写 transcript——进程在 API 响应前被杀也能 `--resume`**（:436-449）。

`for await` 消费循环大 switch 翻译内部事件为 SDK 输出：message_start/delta 累计 usage、message_stop 并入 totalUsage（成本累计由此而来）；`compact_boundary` 触发 GC——**splice 掉边界前所有消息**（:922-933）；两个回合级闸门：每条消息后查 `maxBudgetUsd`、user 消息处查结构化输出重试上限。`snipReplay` 回调：headless 没有 UI 滚动条，收到 snip 边界直接在 mutableMessages 重放裁剪压平内存（:905-915）。

旁路双预取：记忆预取每轮入口启动、首轮 settle 后消费一次；技能发现预取与模型流并行——**都利用当前轮的等待时间准备下一轮输入**（:1599-1628）。

## 5. QueryDeps：为 reducer 化预留的接缝

deps.ts 全文 40 行：`{callModel, microcompact, autocompast, uuid}` 四依赖 + `productionDeps()` 工厂。注释明说 callModel/autocompact 是被 spyOn 最多的 mock 点（散落 6-8 个测试文件）。config.ts:8-11 注释直接点明意图：**让 queryLoop 最终提炼成 `(state, event, config) => state` 的纯 reducer**。`typeof fn` 声明让签名与真实实现自动同步。

## 6. 边界控制三件套

- **max-turns**：工具回灌后、构造 next_turn 前判定；abort 路径同样检查保证被打断回合不超账（:1507-1514）
- **max-output-tokens 恢复**：上限 `MAX_OUTPUT_TOKENS_RECOVERY_LIMIT=3`（:164）。两级：先升 override 到 ESCALATED_MAX_TOKENS 原样重发（:1199-1221）；仍触顶则注入 meta 消息 "Output token limit hit. Resume directly — no apology, no recap..."（:1224-1229）
- **abort 传播**：signal 沿 callModel → 流式执行器 → stop hooks；流结束后必须先消费 `getRemainingResults()` 让执行器为被中止工具**合成 tool_result，否则 API 因 tool_use 缺配对 tool_result 报错**（:1011-1014）；`signal.reason==='interrupt'` 时跳过中断提示（排队下一条用户消息已够上下文，:1044-1050）

## 7. 六组件对表 + 净室对照

| 组件 | Claude Code 实证 | claw-code 净室对照 |
|---|---|---|
| E 循环 | queryLoop 7 continue/10 Terminal 显式状态机 | ConversationRuntime run_turn 单 loop + usize::MAX |
| 压缩 | 五级链内嵌循环（最复杂） | 单级 auto_compact 100K 阈值 |
| 恢复 | withhold + transition 防死循环 | 错误直接 return |
| 编排 | QueryEngine for-await 翻译 | CLI 直接驱动 |
| 可测 | QueryDeps 注入 + reducer 蓝图 | trait C/T 注入（同构！） |

**讲透Agent 教学锚点**：这是"ReAct 循环"从论文到工业的完整距离——论文里一个 while 循环，工业里是显式状态机 + 五级压缩 + withhold + 三类恢复 + 旁路预取。

📌 下一步：03 篇看模型的手——43 个工具与 Bash 的三层防线。
