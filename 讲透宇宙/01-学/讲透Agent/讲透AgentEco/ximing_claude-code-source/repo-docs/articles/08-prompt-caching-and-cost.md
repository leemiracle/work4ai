---
title: Claude Code 源码拆解 08：提示缓存与成本工程
date: "2026-04-05 17:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---

> 系列第 08/20 篇 · 对应主题：上下文窗口的成本课

# 提示缓存与成本工程

Agent 会话的经济学由两个数字决定：每次请求要重算多少前缀 token，以及这些 token 按什么价格计费。Claude Code 对这两件事都做了显式工程：前者是 `addCacheBreakpoints` 的断点放置与 `promptCacheBreakDetection.ts` 的失效归因，后者是从 `cost-tracker` 到 `modelCost.ts` 的一条完整计费链。本篇沿这两条链读源码。

## 断点放置：每个请求恰好一个 cache_control

Anthropic 提示缓存的语义是"从请求开头到 cache_control 标记处为止的前缀可被缓存"。断点放错位置，缓存要么不命中，要么白占 KV 空间。`addCacheBreakpoints` 的核心约束写在注释里：每个请求恰好放一个消息级 cache_control 标记（src/services/api/claude.ts:3078）。

```typescript
const markerIndex = skipCacheWrite ? messages.length - 2 : messages.length - 1
const result = messages.map((msg, index) => {
  const addCache = index === markerIndex
  if (msg.type === 'user') {
    return userMessageToMessageParam(msg, addCache, enablePromptCaching, querySource)
  }
  return assistantMessageToMessageParam(msg, addCache, enablePromptCaching, querySource)
})
```

（src/services/api/claude.ts:3089-3106）标记落在最后一条消息。注释解释了为什么不是两个：服务端 Mycro 的轮次淘汰会释放不在保护边界上的 KV 页，两个标记会让倒数第二个位置的局部注意力页多活一轮，但不会有任何后续请求从那里恢复，纯属浪费（src/services/api/claude.ts:3078-3088）。`skipCacheWrite` 用于 fire-and-forget 的分支查询，标记前移一位到倒数第二条消息，使写操作变成对已有前缀的 no-op 合并，分支不会把自己的尾巴留在缓存里。

标记具体落在消息的最后一个内容块上。user 消息若是字符串则包成单块加标记，若是块数组则只给最后一块加（src/services/api/claude.ts:594-620）；assistant 消息同样只标记最后一块，且跳过 `thinking` 与 `redacted_thinking` 块（src/services/api/claude.ts:653-666）。thinking 块不参与跨轮复用，标在上面没有意义。

消息级断点之外还有系统提示级断点。`buildSystemPromptBlocks` 把系统提示交给 `splitSysPromptPrefix` 切块，按块的 `cacheScope` 决定加不加 `cache_control`，并在注释里警告"不要再加缓存块，否则会 400"（src/services/api/claude.ts:3213-3237）。切分逻辑把系统提示分成计费头、CLI 前缀、静态段、动态段：找到 `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` 时，边界前的静态内容打 `global` scope 的缓存标记（跨组织共享），边界后的动态内容不缓存；3P provider 或边界缺失时退化为 `org` scope（src/utils/api.ts:321-360）。

工具在请求中的摆放位置同样影响缓存命中。advisor 的服务端工具 schema 追加在 `toolSchemas` 之后，注释说明原因：cache_control 标记在 toolSchemas 上，把 advisor 放后面，切换 /advisor 只扰动小后缀而不动已缓存的前缀（src/services/api/claude.ts:1386-1389）。反过来，deferred tools 列表若以临时消息 prepend 进对话头部，则"每次工具池变化都打爆缓存"，因此改成了持久化的 attachment 通道（src/services/api/claude.ts:1327-1345）。Chrome 工具搜索指令同理：改成 client 侧 attachment 之前，"chrome 连接晚了导致每请求追加系统提示"会打爆缓存（src/services/api/claude.ts:1347-1355）。两处对照，原则一致：易变的东西往请求尾部放，或者移出缓存键。

`useCachedMC`（cached microcompact）开启时，`addCacheBreakpoints` 还要处理缓存编辑块的摆放：历史 pin 住的 `cache_edits` 按原 user 消息索引重插，新的删除指令插进最后一条 user 消息并立即 pin 住，保证后续请求在同一位置重发（src/services/api/claude.ts:3127-3162）。随后给位于最后 cache_control 标记之前的 tool_result 块补上 `cache_reference`。API 要求 cache_reference 出现在最后一个 cache_control"之前或之上"，实现取严格的"之前"，规避 cache_edits 拼接导致块索引漂移的边界情形；且复制新对象而非原地修改，避免污染被不支持缓存编辑的次要查询复用的消息块（src/services/api/claude.ts:3164-3207）。

## 1 小时 TTL 的闩锁

`getCacheControl` 返回的标记体很小：`type: 'ephemeral'`，条件性附加 `ttl: '1h'` 和 `scope: 'global'`（src/services/api/claude.ts:358-374）。是否启用 1 小时 TTL 由 `should1hCacheTTL` 决定，这里有一个典型的成本工程细节：

```typescript
// Latch eligibility in bootstrap state for session stability — prevents
// mid-session overage flips from changing the cache_control TTL, which
// would bust the server-side prompt cache (~20K tokens per flip).
let userEligible = getPromptCache1hEligible()
if (userEligible === null) {
  userEligible =
    process.env.USER_TYPE === 'ant' ||
    (isClaudeAISubscriber() && !currentLimits.isUsingOverage)
  setPromptCache1hEligible(userEligible)
}
```

（src/services/api/claude.ts:403-412）用户的 1h 资格取决于"订阅且未进入超额计费"，这个状态可能在会话中途翻转。如果 live 读取，TTL 会从 1h 变回 5m，cache_control 内容改变直接使服务端缓存键失效，注释量化了代价：每次翻转约打爆 20K token。解法是把资格和 GrowthBook allowlist 都在首次求值时闩进 bootstrap state，会话内不变（src/services/api/claude.ts:415-424）。同样的闩锁模式出现在 thinking 清理上：距上次 API 完成超过 `CACHE_TTL_1HOUR_MS` 后才闩住"清 thinking"的行为（src/services/api/claude.ts:1446-1455）。原则不变：凡是会进缓存键的东西，都必须是会话稳定的。

## promptCacheBreakDetection.ts：727 行的失效归因

放了断点不等于缓存命中。这个文件是一套两阶段的缓存失效检测与上报系统，回答"这次缓存没命中，是客户端改了什么，还是服务端自己的事"。

第一阶段 `recordPromptState` 在请求发出前调用（src/services/api/claude.ts:1460-1474 处的调用点），对一切可能影响服务端缓存键的输入算哈希：strip 掉 cache_control 后的系统提示与工具 schema、带 cache_control 的系统提示（专抓 scope/TTL 翻转）、模型、fast mode、beta 头列表、effort、extra body 等（src/services/api/promptCacheBreakDetection.ts:267-294）。哈希函数在 Bun 下用 `Bun.hash`，Node 下退到 djb2（src/services/api/promptCacheBreakDetection.ts:170-179）。调用点有一个细节：参与哈希的工具列表先过滤掉 `defer_loading` 的工具，因为 API 会把它们从 prompt 里剥掉，本就不进缓存键，留着会在工具被发现或 MCP 重连时产生"工具 schema 变了"的假阳性（src/services/api/claude.ts:1460-1467）。与上一份快照逐项比较，差异记入 `pendingChanges`，但不发事件，因为此刻还不知道缓存是否真的没命中（src/services/api/promptCacheBreakDetection.ts:332-410）。跟踪按 querySource 分键，`compact` 归并到 `repl_main_thread`（两者共享服务端缓存），subagent 用 agentId 隔离，防止同类 agent 并发互报假警；speculation 等短命 fork 源不跟踪，因为"跑 1-3 轮就结束，没有可比较的基线"（src/services/api/promptCacheBreakDetection.ts:149-158）。快照 map 上限 10 条，因为每条存约 300KB 的可 diff 内容，不限量会随 subagent 数量无限膨胀（src/services/api/promptCacheBreakDetection.ts:103-107）。

第二阶段 `checkResponseForCacheBreak` 在响应回来后执行（调用点 src/services/api/claude.ts:2383-2392），用真实的 cache read token 数判定失效：

```typescript
// Detect a cache break: cache read dropped >5% from previous AND
// the absolute drop exceeds the minimum threshold.
const tokenDrop = prevCacheRead - cacheReadTokens
if (
  cacheReadTokens >= prevCacheRead * 0.95 ||
  tokenDrop < MIN_CACHE_MISS_TOKENS
) {
  state.pendingChanges = null
  return
}
```

（src/services/api/promptCacheBreakDetection.ts:483-492）双阈值：相对跌幅超 5% 且绝对跌幅超 2000 token（`MIN_CACHE_MISS_TOKENS`，src/services/api/promptCacheBreakDetection.ts:120），小波动不报警。Haiku 被整体排除，因为缓存行为不同（src/services/api/promptCacheBreakDetection.ts:129-131）。

确认失效后做归因。若 `pendingChanges` 非空，按标志位拼出原因串（模型变了、系统提示变了多少字符、工具增删、beta 头增删、effort 变化等，src/services/api/promptCacheBreakDetection.ts:494-563）；若客户端一切未变，则按距上一条 assistant 消息的时间间隔落到 TTL 假设：超 1 小时记"possible 1h TTL expiry"，超 5 分钟记"possible 5min TTL expiry"，5 分钟以内则直接标"likely server-side"。注释引用了 BQ 分析结论：客户端标志全假且间隔小于 TTL 时，约 90% 的失效是服务端路由/淘汰或计费与推理不一致，不应再按客户端 bug 排查（src/services/api/promptCacheBreakDetection.ts:573-588）。最终结果发 `tengu_prompt_cache_break` 事件，工具名经 `sanitizeToolName` 脱敏（MCP 工具名可能含路径，统一折叠为 'mcp'，src/services/api/promptCacheBreakDetection.ts:181-185），并写一份前后 prompt-state 的 diff 文件供 `--debug` 排查（src/services/api/promptCacheBreakDetection.ts:649-660）。

两个主动豁免接口收尾：cached microcompact 删除缓存前缀前调 `notifyCacheDeletion`，下一次 cache read 下降是预期行为（src/services/api/promptCacheBreakDetection.ts:673-682）；压缩后调 `notifyCompaction` 重置基线，因为压缩合法地缩短了上下文（src/services/api/promptCacheBreakDetection.ts:689-698）。

## 计费链：从 usage 到计数器

响应流结束时，usage 数据进 `calculateUSDCost` 算钱，再进 `addToTotalSessionCost` 累计（src/services/api/claude.ts:2251-2256）。usage 本身在流式合并时做了细分：`cache_creation` 拆出 `ephemeral_1h_input_tokens` 与 `ephemeral_5m_input_tokens`，对应 1h 与 5m 两种 TTL 的写入量（src/services/api/claude.ts:2956-2964）。

`addToTotalSessionCost` 做三件事：按模型累加 `ModelUsage`（输入、输出、cache read、cache write、web search、costUSD），写入全局 STATE，再喂给两个 OpenTelemetry 计数器（src/cost-tracker.ts:278-301）：

```typescript
getCostCounter()?.add(cost, attrs)
getTokenCounter()?.add(usage.input_tokens, { ...attrs, type: 'input' })
getTokenCounter()?.add(usage.output_tokens, { ...attrs, type: 'output' })
getTokenCounter()?.add(usage.cache_read_input_tokens ?? 0, { ...attrs, type: 'cacheRead' })
getTokenCounter()?.add(usage.cache_creation_input_tokens ?? 0, { ...attrs, type: 'cacheCreation' })
```

（src/cost-tracker.ts:291-301）计数器在 bootstrap 初始化为 `claude_code.cost.usage` 与 `claude_code.token.usage` 两个 metric（src/bootstrap/state.ts:968-973），属性带模型名，fast mode 时再加 `speed: 'fast'`，因为 Opus 4.6 的 fast 档单价不同，属性必须区分。advisor 工具产生的嵌套 usage 递归走同一入口累加，并单独发 `tengu_advisor_tool_token_usage` 事件（src/cost-tracker.ts:304-321）。

STATE 侧很薄：`addToTotalCostState` 只是 `STATE.modelUsage[model] = modelUsage; STATE.totalCostUSD += cost`（src/bootstrap/state.ts:557-564），各 token 总量 getter 都是对 `modelUsage` 的即时求和（src/bootstrap/state.ts:704-718）。会话成本在切换会话前落盘到项目配置（`lastCost`、`lastModelUsage` 等字段，src/cost-tracker.ts:143-175），恢复会话时按 sessionId 匹配读回（src/cost-tracker.ts:87-137）。`/cost` 的展示由 `formatTotalCost` 拼接：总成本（若用过未知模型则附"成本可能不准"的提示）、API 时长、墙钟时长、代码行数变化，以及按 canonical 短名聚合的分模型用量（src/cost-tracker.ts:181-244）。显示层对金额做了分级取整：超过 $0.5 保留两位小数，否则保留四位，避免小额会话被四舍五入成零（src/cost-tracker.ts:177-179）。

## tokenBudget：用输出 token 预算拉住轮次

`feature('TOKEN_BUDGET')` 开启后，查询循环每轮结束检查一次输出预算（src/query.ts:1308-1341）。预算从用户输入解析，`parseTokenBudget` 支持 `+500k` 简写与 "use 2M tokens" 自然语言两种形式，k/m/b 映射到千/百万/十亿（src/utils/tokenBudget.ts:3-29）。简写正则锚定句首或句尾，避免把自然语言里的 "+500k" 式片段误判为预算指令；`findTokenBudgetPositions` 在 UI 高亮时还要剔除首尾正则的重叠命中，防止同一处被算两次（src/utils/tokenBudget.ts:31-64）。轮次输出量不是单次响应的 output_tokens，而是全局累计输出减轮次起点的快照差：`getTurnOutputTokens() = getTotalOutputTokens() - outputTokensAtTurnStart`，快照由 `snapshotOutputTokensForTurn` 在每轮开始时拍下并同时记录当轮预算（src/bootstrap/state.ts:724-737）。tracker 本身在循环入口惰性创建，未开 feature 时为 null（src/query.ts:280）。

`checkTokenBudget` 的决策逻辑（src/query/tokenBudget.ts:45-93）：

```typescript
const isDiminishing =
  tracker.continuationCount >= 3 &&
  deltaSinceLastCheck < DIMINISHING_THRESHOLD &&
  tracker.lastDeltaTokens < DIMINISHING_THRESHOLD

if (!isDiminishing && turnTokens < budget * COMPLETION_THRESHOLD) {
  tracker.continuationCount++
  ...
  return { action: 'continue', nudgeMessage: getBudgetContinuationMessage(pct, turnTokens, budget), ... }
}
```

未达预算 90%（`COMPLETION_THRESHOLD`）就注入一条 meta 用户消息把模型推回去继续干活："Stopped at N% of token target... Keep working — do not summarize."（src/utils/tokenBudget.ts:66-73）。但有一个反失控阀：连续续推 3 次以上且最近两次的输出增量都低于 500 token（`DIMINISHING_THRESHOLD`，src/query/tokenBudget.ts:4），判定为收益递减，停止续推并带 `diminishingReturns: true` 上报完成事件（src/query/tokenBudget.ts:59-90）。subagent（`agentId` 非空）不参与预算续推，直接停（src/query/tokenBudget.ts:51-53）。

## 没有 tokenizer 时的估算

上下文阈值判断（自动压缩等）需要当前窗口大小，但 CLI 不内置 tokenizer。`tokenCountWithEstimation` 是规范入口：从消息尾部找最近一条带真实 usage 的 assistant 消息，用其 `input + cache_creation + cache_read + output` 做基准（src/utils/tokens.ts:46-53），加上其后新增消息的粗估（src/utils/tokens.ts:226-261）。usage 的可信度由 `getTokenUsage` 把关：合成消息（如 API 错误占位、压缩生成的假 assistant 记录）的内容首块命中 `SYNTHETIC_MESSAGES` 或模型名为 `SYNTHETIC_MODEL` 时不算数（src/utils/tokens.ts:7-20）。文件注释里明确反对另外两种口径：累计求和会随上下文增长重复计数，只取 output_tokens 则根本不是窗口大小（src/utils/tokens.ts:208-213）。有一个并行工具调用的坑：并行 tool_use 时流式层会为每个内容块各发一条同 message.id 的 assistant 记录，tool_result 交错其间；若停在最后一条，前面交错的 tool_result 会漏估。解法是命中 usage 后向前走到同 id 的第一条兄弟记录再切估算区间（src/utils/tokens.ts:235-252）。

粗估本身按块类型分治（src/services/tokenEstimation.ts:391-435）：文本类一律 `Math.round(content.length / 4)`（src/services/tokenEstimation.ts:203-208）；JSON 系文件因 `{`, `}`, `:`, `,`, `"` 大量单字符 token，比例收紧到 2 字节/token（src/services/tokenEstimation.ts:215-224）；image 与 document 块不按 base64 长度估：1MB PDF 的 base64 约 133 万字符会估出 32.5 万 token，而 API 实收约 2000，所以直接返回常量 2000（src/services/tokenEstimation.ts:400-411）；tool_use 把 name 加 input 序列化后按 4 字节/token 估（src/services/tokenEstimation.ts:416-422）。需要精确值时走 `countTokens` API，主循环模型不可用时退化到 Haiku 发一个 `max_tokens: 1` 的真实请求换 usage 数字（src/services/tokenEstimation.ts:251-325）。三个 provider 各有分支：Bedrock 没有 SDK 级 countTokens 支持，要动态加载约 279KB 的 AWS SDK 走 `CountTokensCommand`（src/services/tokenEstimation.ts:437-495）；Vertex 要按允许列表过滤 beta 头，否则某些端点直接 400（src/services/tokenEstimation.ts:167-170）；消息含 thinking 块时计数请求必须带上 `budget_tokens: 1024` 的 thinking 配置，否则参数不合法（src/services/tokenEstimation.ts:30-33, 181-186）。

## modelCost：定价表与兜底

计费公式是五种量的加权和（src/utils/modelCost.ts:131-142）：输入、输出、cache read、cache write 按每 Mtok 单价折算，web search 按每次 $0.01 计。定价以常量表硬编码：Sonnet 档 $3/$15（cache write $3.75、cache read $0.3），Opus 4/4.1 档 $15/$75，Opus 4.5 档 $5/$25，Opus 4.6 fast 档 $30/$150，Haiku 3.5 档 $0.8/$4，Haiku 4.5 档 $1/$5（src/utils/modelCost.ts:36-87）。`MODEL_COSTS` 把各模型的 first-party 名映射到档（src/utils/modelCost.ts:104-126）。表中 cache write 单价恒为输入价的 1.25 倍、cache read 恒为 0.1 倍，即缓存的定价结构是把"省下的重算"折成 90% 的折扣。

三个边界处理：Opus 4.6 按 usage 上的 `speed` 字段在 fast 档与普通档间切换（src/utils/modelCost.ts:144-153）；查不到定价的模型发 `tengu_unknown_model_cost` 事件、置 `hasUnknownModelCost` 标志（`/cost` 据此显示"成本可能不准"），并回退到默认主循环模型的定价，再退到 `COST_TIER_5_25`（src/utils/modelCost.ts:89, 155-173）；`calculateCostFromTokens` 允许 side query 不构造完整 BetaUsage 也能算钱（src/utils/modelCost.ts:186-202）。

## 小结

这条链上的设计可以归约为三条：其一，缓存键的每个组成部分（断点位置、TTL、scope、beta 头、effort）都被当作稳定性约束来管理，易变内容一律后置或闩锁；其二，缓存失效是可观测、可归因的，双阈值过滤噪声，时间间隔区分客户端变更与服务端淘汰；其三，token 计数分三层：流式 usage 做权威基准、字节比例做增量粗估、countTokens API 做按需精确值；计费则在统一的 ModelUsage 结构上累计并向 OTel 双计数器导出。成本在这里不是事后统计，而是参与请求构造的输入。

## 本篇涉及的源码文件

- `src/services/api/claude.ts`：请求构造入口，含 cache_control 断点放置、TTL 闩锁、usage 合并与成本累加调用
- `src/services/api/promptCacheBreakDetection.ts`：两阶段缓存失效检测、归因与 `tengu_prompt_cache_break` 上报
- `src/cost-tracker.ts`：会话成本累计、OTel 计数器导出、`/cost` 展示与成本落盘/恢复
- `src/query/tokenBudget.ts`：输出 token 预算的续推/停止决策与收益递减判定
- `src/utils/tokenBudget.ts`：用户输入中的预算表达式解析与续推提示语
- `src/utils/tokens.ts`：基于 usage 的上下文窗口计量与 `tokenCountWithEstimation` 规范入口
- `src/services/tokenEstimation.ts`：无 tokenizer 时的分块粗估与 countTokens API 精确计数
- `src/utils/modelCost.ts`：模型定价表、五量加权计费公式与未知模型兜底
- `src/bootstrap/state.ts`：全局成本/token 状态、OTel 计数器与轮次输出快照
- `src/utils/api.ts`：系统提示按 static/dynamic 边界切块并分配缓存 scope
