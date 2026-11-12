---
title: Claude Code 源码拆解 02：Agent 主循环，queryLoop 状态机
date: "2026-04-04 10:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 02/20 篇 · 对应主题：思考-行动-观察循环

# Agent 主循环：queryLoop 状态机

Claude Code 的"思考-行动-观察"循环集中在两个异步生成器上：`query()`（src/query.ts:219）负责单次用户回合内的多轮模型-工具往返，`QueryEngine.submitMessage()`（src/QueryEngine.ts:209）负责回合级的编排与 SDK 事件输出。前者是一个 `while (true)` 状态机，靠 7 个 `continue` 点推进；后者是一个 `for await` 消费器，把内部消息流翻译成 SDKMessage。本篇按这两条线索拆解。

## 一、入口分层：query() 与 queryLoop()

`query()` 只做一件事：用 `yield*` 委托给 `queryLoop()`，然后在正常返回后给本回合消费掉的队列命令补发 `completed` 生命周期通知（src/query.ts:230-238）。注释说明了为什么放在 `yield*` 之后：抛异常时 error 会穿透 `yield*`，`.return()` 会同时关闭两个生成器，因此这段代码只在"正常终态"执行，天然构成 started-without-completed 的不对称信号。

```typescript
export async function* query(
  params: QueryParams,
): AsyncGenerator<StreamEvent | RequestStartEvent | Message | TombstoneMessage | ToolUseSummaryMessage, Terminal> {
  const consumedCommandUuids: string[] = []
  const terminal = yield* queryLoop(params, consumedCommandUuids)
  for (const uuid of consumedCommandUuids) {
    notifyCommandLifecycle(uuid, 'completed')
  }
  return terminal
}
```

循环体 `queryLoop()`（src/query.ts:241）在入口处把参数分为三类：不可变的 `params` 解构（systemPrompt、maxTurns 等，src/query.ts:253-262）、依赖注入的 `deps`（src/query.ts:263）、以及跨迭代可变的 `state`。此外还有第四类：`buildQueryConfig()` 在入口把 sessionId 与四个运行时门控快照一次（src/query.ts:295），避免循环中途读到翻转的 statsig 值。`streamingToolExecution` 门控一旦中途翻转，流式执行器与批量执行两条路径会在同一回合混用。生成器返回类型是 `Terminal`（从 `./query/transitions.js` 导入，src/query.ts:104；该文件不在本仓库快照中，但所有 `return { reason: ... }` 字面量在 query.ts 内可见，共十种：blocking_limit、image_error、model_error、aborted_streaming、aborted_tools、prompt_too_long、completed、stop_hook_prevented、hook_stopped、max_turns），yield 类型则是五种事件的并集。

## 二、State：跨迭代状态与 7 个 continue 点

`State` 类型（src/query.ts:204-217）共 10 个字段：`messages`、`toolUseContext`、`autoCompactTracking`、`maxOutputTokensRecoveryCount`、`hasAttemptedReactiveCompact`、`maxOutputTokensOverride`、`pendingToolUseSummary`、`stopHookActive`、`turnCount`、`transition`。设计约束写在注释里：循环体在每轮顶部解构 state 以保持裸名读取，continue 点用 `state = { ... }` 一次性整体替换，而不是 9 次分散赋值（src/query.ts:266-267）。`transition` 字段记录"上一轮为什么 continue"，供测试断言恢复路径被触发，也被循环内部用于防死循环（见下文 collapse 防重入）。

通读全函数，`state = next; continue` 恰好出现 7 次，对应 7 种继续理由：

1. `collapse_drain_retry`（src/query.ts:1115）：上下文溢出时先排空 staged collapse。
2. `reactive_compact_retry`（src/query.ts:1165）：413/媒体错误后的反应式压缩重试。
3. `max_output_tokens_escalate`（src/query.ts:1220）：输出上限从 8k 升到 64k 原样重试。
4. `max_output_tokens_recovery`（src/query.ts:1251）：注入"继续输出"的 meta 消息。
5. `stop_hook_blocking`（src/query.ts:1305）：stop hook 返回阻塞错误，作为 user 消息回灌。
6. `token_budget_continuation`（src/query.ts:1340）：token 预算未到 90% 阈值时的 nudge 续跑。
7. `next_turn`（src/query.ts:1727）：正常的"工具结果回灌、进入下一轮"。

每个 continue 点都显式列出全部 10 个字段，哪些被重置一目了然。对比两处就能看到策略差异：`next_turn`（正常推进）把 `maxOutputTokensRecoveryCount` 和 `hasAttemptedReactiveCompact` 都清零（src/query.ts:1720-1721），因为新一轮带着真实工具结果，恢复配额理应刷新；而 `stop_hook_blocking` 只清前者、保留后者。注释说明这是修过的 bug：若重置后者，"压缩→仍然超长→报错→hook 阻塞→再压缩"会烧掉数千次 API 调用（src/query.ts:1294-1297）。同理，`collapse_drain_retry` 通过检查 `state.transition?.reason !== 'collapse_drain_retry'`（src/query.ts:1092）防止对同一批 collapse 重复排空。这正是 `transition` 字段除测试断言外的第二个用途：记录"上一轮试过什么"，避免在同一恢复路径上空转。这就是把状态机显式化的收益：不变量写在代码里，而不是散落在赋值语句间。

## 三、单轮生命周期：while(true) 里做什么

一轮迭代可以划成五个阶段。

阶段 0：轮开始。每轮第一件事是 `yield { type: 'stream_request_start' }`（src/query.ts:337），给消费者一个"新请求开始"的分界信号。随后更新 `queryTracking`（chainId 贯穿整个回合、depth 每轮 +1，src/query.ts:347-355），供分析事件关联同一逻辑链。

阶段 1：上下文整形与压缩检查。在调用模型之前，消息数组要依次经过五级处理：`getMessagesAfterCompactBoundary` 截取压缩边界之后的消息（src/query.ts:365）→ `applyToolResultBudget` 按 tool_use_id 限制聚合工具结果大小（src/query.ts:379）→ 可选的 snip 历史裁剪（src/query.ts:401-410）→ `deps.microcompact`（src/query.ts:414）→ 可选的 context-collapse 投影（src/query.ts:441）→ `deps.autocompact`（src/query.ts:454）。顺序有讲究：collapse 在 autocompact 之前，若折叠后已低于阈值，autocompact 空转，保留颗粒度更细的上下文（src/query.ts:428-431）。若 autocompact 真的触发，`buildPostCompactMessages` 产出摘要消息并逐条 yield，随后本迭代就用压缩后的消息继续（src/query.ts:528-535）。压缩之后还有一道硬性阻塞线：当自动压缩关闭且 token 数触及 blocking limit 时，直接 yield 合成错误消息并 `return { reason: 'blocking_limit' }`（src/query.ts:641-647）；fork 出的 compact/session_memory 查询被显式豁免，否则压缩 agent 自己会死锁（src/query.ts:600-603）。

阶段 2：API 调用与 withhold。模型调用收敛为 `deps.callModel`（src/query.ts:659），参数里传入 `signal: toolUseContext.abortController.signal`（src/query.ts:665）。外层套着 `while (attemptWithFallback)` 的 fallback 重试环：捕获 `FallbackTriggeredError` 后切换 `currentModel`、清空已收集的 assistant/toolUse 块、给已发出的 tool_use 补占位 tool_result（`yieldMissingToolResultBlocks`，src/query.ts:900-903），再以 fallbackModel 重试。流式消费时有一个 withhold 机制：可恢复错误（prompt-too-long、媒体过大、max_output_tokens）先不 yield 给 SDK 调用方，但仍 push 进 `assistantMessages` 供后续恢复逻辑检查（src/query.ts:799-825）。注释解释了原因：SDK 调用方（如 cowork/desktop）见到任何 `error` 字段就终止会话，提前 yield 会导致恢复循环还在跑、调用方却已经终止会话（src/query.ts:166-173）。

流式 fallback 还有一层一致性处理：若第一次尝试已流出一部分 assistant 消息才触发降级，旧消息（尤其是带签名的 thinking 块）对新模型无效，循环先为它们逐条 yield `tombstone` 事件让 UI 与 transcript 移除，再清空 `assistantMessages`/`toolResults`/`toolUseBlocks` 三个收集器并重建 StreamingToolExecutor，防止旧 tool_use_id 的孤儿 tool_result 混入重试（src/query.ts:712-741）。另外，assistant 消息在 yield 前会过一次 `backfillObservableInput`：工具可以在克隆的 input 上补派生字段给 SDK 流和消费者看，原始消息保持不动，因为它要回灌给 API，任何 mutation 都会破坏 prompt 缓存的字节对齐（src/query.ts:747-787）。

```typescript
let withheld = false
if (feature('CONTEXT_COLLAPSE')) {
  if (contextCollapse?.isWithheldPromptTooLong(message, isPromptTooLongMessage, querySource)) {
    withheld = true
  }
}
if (reactiveCompact?.isWithheldPromptTooLong(message)) withheld = true
if (mediaRecoveryEnabled && reactiveCompact?.isWithheldMediaSizeError(message)) withheld = true
if (isWithheldMaxOutputTokens(message)) withheld = true
if (!withheld) {
  yield yieldMessage
}
```

阶段 3：工具分发。流式过程中，若启用了 `streamingToolExecution` 门控，每个 tool_use 块一到达就喂给 `StreamingToolExecutor`（src/query.ts:841-844），工具执行与模型流并行；否则在流结束后由 `runTools` 统一执行（src/query.ts:1380-1382）。两条路径汇合成同一个 `toolUpdates` 异步迭代器，消费时 yield 消息、收集 tool_result、并合并 `update.newContext`（工具可以改写上下文，如刷新工具列表，src/query.ts:1402-1407）。`needsFollowUp` 是唯一的路由信号：只要任何 assistant 消息含 tool_use 块就置真（src/query.ts:832-835），注释指出 `stop_reason === 'tool_use'` 不可靠，不能作为循环退出条件（src/query.ts:554-556）。

阶段 4：收尾分岔。流结束后按优先级处理：abort 信号（见第六节）→ 上一轮的 toolUseSummary 在此 await 并 yield（src/query.ts:1055-1060，Haiku 摘要与主流并行跑约省 1 秒）→ `needsFollowUp === false` 时进入恢复/停止判定，即第 1-6 号 continue 点与 stop hooks；`needsFollowUp === true` 则走工具结果回灌，构造第 7 号 continue。

第 6 号 continue 背后是 `checkTokenBudget`（src/query/tokenBudget.ts:45）实现的一个独立预算控制器：仅对主线程生效（`agentId` 存在即 stop，tokenBudget.ts:51）；当前回合输出 token 未达预算 90%（`COMPLETION_THRESHOLD = 0.9`，tokenBudget.ts:3）时返回 `continue` 并附带一条 nudge 消息；但连续 3 次续跑且相邻两次检查的增量都低于 500 token（`DIMINISHING_THRESHOLD`，tokenBudget.ts:4）时判定为收益递减，提前 stop 并上报 `diminishingReturns`（tokenBudget.ts:59-62、78-90）。效果是在"模型自己决定何时停"之外加了一条外部规则：预算没花完就推模型继续，连续几轮产出过低就提前停。

阶段 5：stop hooks。无工具调用且无可恢复错误时，`handleStopHooks` 以 `yield*` 内联执行（src/query.ts:1267-1276）。它在 src/query/stopHooks.ts:65 定义，本身也是生成器：先保存 cacheSafeParams 供 /btw 等 fork 场景读取（stopHooks.ts:96-98），触发 prompt suggestion、记忆提取、auto-dream 等后台任务（fire-and-forget，stopHooks.ts:136-157），然后执行用户配置的 Stop hooks。hook 返回 `blockingError` 时被包成 `isMeta: true` 的 user 消息（stopHooks.ts:257-263），回到 query.ts 后触发第 5 号 continue。这就是"hook 让模型继续干活"的机制：不重启循环，而是把 hook 返回的 blockingError 作为新输入进入下一轮。`preventContinuation` 则直接终结回合：`return { reason: 'stop_hook_prevented' }`（src/query.ts:1278-1280）。注意 API 错误消息会跳过 stop hooks 直接 `return { reason: 'completed' }`（src/query.ts:1262-1265），注释说明这是为了防止"错误→hook 阻塞→重试→错误"的无限循环。

工具摘要采用跨轮流水线。工具批次结束后，若 `emitToolUseSummaries` 门控开启且不是子 agent，循环会收集本轮每个 tool_use 的名字、输入和对应 tool_result 内容，调用 `generateToolUseSummary` 生成 Haiku 摘要，但不 await，而是把 Promise 存进 `nextPendingToolUseSummary`（src/query.ts:1437-1481）。这个 Promise 经第 7 号 continue 写入 `state.pendingToolUseSummary`，在下一轮模型流式输出期间（5-30 秒窗口）后台完成，流结束后才 await 并 yield（src/query.ts:1055-1060）。一轮的延迟被下一轮的等待吸收，这是循环体内一处典型的流水线优化。

## 四、QueryEngine：回合级编排

`QueryEngine`（src/QueryEngine.ts:184）是会话级对象：一个会话一个实例，`submitMessage()` 每调用一次就是一个用户回合，`mutableMessages`、`totalUsage`、`readFileState` 等状态跨回合存续（src/QueryEngine.ts:175-183）。

回合开始时的编排按序进行：先用 `wrappedCanUseTool` 包装权限回调，每次拒绝都记入 `permissionDenials` 供 SDK 结果上报（src/QueryEngine.ts:243-271）；`fetchSystemPromptParts` 拉取默认系统提示词与 user/system context（src/QueryEngine.ts:288-300）；coordinator 模式叠加额外 userContext（:302-308）；若 SDK 调用方提供 customSystemPrompt 且设置了记忆路径覆盖，追加记忆机制提示词（:316-319），最终 systemPrompt 由 custom/default、记忆段、appendSystemPrompt 三段拼成（:321-325）。`processUserInput` 处理斜杠命令与附件（:410-428），新消息先入 `mutableMessages` 并立刻写 transcript。注释解释这是为了让进程在 API 响应前被杀也能 `--resume`（:436-449）。

随后引擎调用 `query()` 并进入 `for await` 消费循环（:675-686），一个大 switch 把内部事件翻译成 SDK 输出：assistant/user/progress 消息推入 `mutableMessages` 并 `normalizeMessage` 后透传（:761-787）；`stream_event` 在 `message_start`/`message_delta` 时累计 `currentMessageUsage`，`message_stop` 时并入 `totalUsage`（:788-816），成本累计由此而来；`compact_boundary` 触发 GC 优化，splice 掉边界前的所有消息（:922-933）；`max_turns_reached` 附件被翻译成 `error_max_turns` 结果并 return（:842-874）；`stream_request_start` 被显式吞掉（:894-896）。消费循环内还有两个回合级闸门：每条消息后检查 `maxBudgetUsd`（:972-1002），user 消息处检查结构化输出重试上限（:1005-1048）。循环正常结束后从消息尾部提取最终文本结果，yield `result: success`（:1058-1155）。引擎还预留了 `snipReplay` 回调（:169-172）：headless 会话没有 UI 滚动条需要保留完整历史，收到 snip 边界消息时直接在 `mutableMessages` 上重放裁剪，把内存占用压平（:905-915）。队列命令的转换发生在 query.ts 一侧：每轮工具结束后按 agentId 过滤队列快照（主线程只取 `agentId === undefined`，子 agent 只取发给自己的 task-notification，斜杠命令被排除在中途消费之外，src/query.ts:1570-1578），转成附件喂给模型、并从队列移除（:1580-1643），`consumedCommandUuids` 就是在那里回填、最终在 `query()` 出口处统一通知 completed。工具结果之后还挂着两个旁路：记忆预取在每轮入口启动、首轮 settle 后消费一次（`consumedOnIteration` 防重复，src/query.ts:1599-1614），技能发现预取则与模型流并行、在附件阶段收集（:1620-1628），两者都利用当前轮的等待时间完成下一轮输入的准备。

## 五、QueryDeps：依赖注入的可测试性设计

`query()` 的参数里有一个可选的 `deps?: QueryDeps`（src/query.ts:198），缺省时取 `productionDeps()`（src/query.ts:263）。deps.ts 全文仅 40 行：

```typescript
export type QueryDeps = {
  callModel: typeof queryModelWithStreaming
  microcompact: typeof microcompactMessages
  autocompact: typeof autoCompactIfNeeded
  uuid: () => string
}
export function productionDeps(): QueryDeps {
  return { callModel: queryModelWithStreaming, microcompact: microcompactMessages,
           autocompact: autoCompactIfNeeded, uuid: randomUUID }
}
```

设计意图写在文件头注释里：`callModel`、`autocompact` 是目前被 spyOn 最多的两个 mock 点，散落在 6-8 个测试文件中，每个都要写 module-import-and-spy 样板（src/query/deps.ts:9-11）。用 `typeof fn` 声明类型可以让签名与真实实现自动同步；范围刻意收窄到 4 个依赖以验证模式，后续再扩展 runTools、handleStopHooks 等（:19-20）。配合 `buildQueryConfig()`（src/query/config.ts:29）把 env/statsig 门控在入口快照一次、以及 `State` 的整体替换写法，这条路径指向一个写在注释里的目标：让 queryLoop 最终能提炼成 `(state, event, config) => state` 的纯 reducer（config.ts:8-11 的注释直接点明了这个意图）。

## 六、边界控制：max-turns、max-output-tokens 恢复、abort 传播

max-turns 的判定在工具结果回灌之后、构造 `next_turn` 之前：`maxTurns && nextTurnCount > maxTurns` 时 yield `max_turns_reached` 附件并 `return { reason: 'max_turns' }`（src/query.ts:1705-1712）。abort 路径上也有一次同样的检查（src/query.ts:1507-1514），保证被打断的回合也不超账。QueryEngine 侧把该附件转成 `error_max_turns` 的 SDK result（src/QueryEngine.ts:842-874）。

max-output-tokens 恢复的上限为 `MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3`（src/query.ts:164）。恢复分两级：若实验门控开启且未设 override，先把 `maxOutputTokensOverride` 升到 `ESCALATED_MAX_TOKENS` 原样重发同一请求，不发任何 meta 消息（src/query.ts:1199-1221）；若升级后仍触顶，则注入一条 `isMeta` user 消息："Output token limit hit. Resume directly — no apology, no recap..."（src/query.ts:1224-1229），计数器 +1 后 continue。三次用尽才把 withhold 的错误消息真正 yield 出去（src/query.ts:1254-1256）。

abort 的传播路径上，`AbortController` 在 QueryEngine 构造时创建（src/QueryEngine.ts:203），`interrupt()` 只是调 `abort()`（:1158-1160）。信号沿 `toolUseContext.abortController.signal` 传入 `deps.callModel`（src/query.ts:665）、流式工具执行器（每次 addTool/getCompletedResults 前检查，src/query.ts:839、849）、stop hooks（src/query/stopHooks.ts:182、283）。循环体内有三个显式检查点：流结束后（src/query.ts:1015），此时必须先消费 `getRemainingResults()` 让执行器为被中止的工具合成 tool_result，否则 API 会因 tool_use 缺少配对 tool_result 而报错（:1011-1014）；工具执行后（:1485）；以及 stop hooks 循环内每次迭代（stopHooks.ts:283-294）。两处 return 理由分别是 `aborted_streaming` 和 `aborted_tools`。细节上，`signal.reason === 'interrupt'` 时跳过中断提示消息，因为排队的下一条用户消息已提供足够上下文（src/query.ts:1044-1050）。

## 小结

queryLoop 把"思考-行动-观察"实现为一个显式状态机：每轮先整形上下文（五级压缩链），再调模型（withhold 可恢复错误），再分发工具（流式或批量），最后在收尾处分岔到 7 种 continue 或 10 种 Terminal reason。所有跨迭代状态收敛在一个 `State` 结构里整体替换，恢复路径用 `transition` 字段自我标记以防死循环。QueryEngine 在上一层做回合编排：提示词拼装、transcript 落盘、usage 累计、SDK 事件翻译。`QueryDeps` 与 `buildQueryConfig` 则是为可测试性与未来 reducer 化预留的接缝。

## 本篇涉及的源码文件

- `src/query.ts`：Agent 主循环，query()/queryLoop() 异步生成器，压缩链、API 调用、工具分发、7 个 continue 点
- `src/QueryEngine.ts`：回合级编排，系统提示词构建、processUserInput、SDK 事件转换、成本与预算闸门
- `src/query/config.ts`：QueryConfig，入口快照一次的 env/statsig 门控
- `src/query/deps.ts`：QueryDeps 依赖注入与 productionDeps 工厂
- `src/query/stopHooks.ts`：Stop/SubagentStop/TaskCompleted/TeammateIdle hooks 的执行与 blockingError 回灌
- `src/query/tokenBudget.ts`：token 预算检查，90% 阈值续跑与递减收益早停
