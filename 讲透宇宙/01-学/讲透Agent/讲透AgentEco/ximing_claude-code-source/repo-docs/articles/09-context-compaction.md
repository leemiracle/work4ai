---
title: Claude Code 源码拆解 09：上下文压缩体系——五层压缩策略
date: "2026-04-05 21:30"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 09/20 篇 · 对应主题：长任务的失忆与对策

# 上下文压缩体系：五层压缩策略

Agent 跑长任务时的"失忆"不是模型问题，是工程问题：200K token 的上下文窗口（src/utils/context.ts:9）注定会被填满，问题只在于客户端用什么策略、在什么时机、以多大信息损失为代价把上下文塞回去。Claude Code 的答案不是单一压缩器，而是一个从"写入时刻"到"溢出时刻"按粒度由细到粗排列的多层体系。按触发顺序和损失粒度，可以梳理出五层：工具结果落盘卸载、微压缩（microcompact / API context management）、会话记忆压缩、摘要压缩（autoCompact / compact.ts），以及一组 feature-gated 的实验性策略（reactiveCompact、snipCompact、contextCollapse）。本篇逐层拆解。

## 阈值体系：autoCompact 的触发逻辑

整套压缩体系的触发判定集中在 autoCompact.ts。要回答的第一个问题是：在多少 token 时触发压缩？答案由 `getEffectiveContextWindowSize` 给出（src/services/compact/autoCompact.ts:33）：

```typescript
const MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000

export function getEffectiveContextWindowSize(model: string): number {
  const reservedTokensForSummary = Math.min(
    getMaxOutputTokensForModel(model),
    MAX_OUTPUT_TOKENS_FOR_SUMMARY,
  )
  let contextWindow = getContextWindowForModel(model, getSdkBetas())

  const autoCompactWindow = process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW
  if (autoCompactWindow) {
    const parsed = parseInt(autoCompactWindow, 10)
    if (!isNaN(parsed) && parsed > 0) {
      contextWindow = Math.min(contextWindow, parsed)
    }
  }
  return contextWindow - reservedTokensForSummary
}
```

有效窗口 = 模型上下文窗口 - 摘要输出预留。预留量封顶 20,000 token，注释说明依据是"p99.99 的压缩摘要输出为 17,387 tokens"（src/services/compact/autoCompact.ts:29），这个数字是用线上分位数反推出来的工程常量。`getContextWindowForModel` 本身支持 `[1m]` 后缀模型返回 1,000,000，也支持 `CLAUDE_CODE_MAX_CONTEXT_TOKENS` 环境变量覆盖（src/utils/context.ts:51-72），所以有效窗口是可调的。

在有效窗口之上再叠四层 buffer 常量（src/services/compact/autoCompact.ts:62-65）：`AUTOCOMPACT_BUFFER_TOKENS = 13_000`（自动压缩触发线）、`WARNING_THRESHOLD_BUFFER_TOKENS = 20_000`（UI 警告线）、`MANUAL_COMPACT_BUFFER_TOKENS = 3_000`（阻塞线）。`getAutoCompactThreshold` 返回 `effectiveWindow - 13_000`，另留 `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 百分比覆盖用于测试（src/services/compact/autoCompact.ts:72-91）。

`shouldAutoCompact` 的判定里有一组递归守卫（src/services/compact/autoCompact.ts:160-183）：`querySource === 'session_memory'` 或 `'compact'` 时直接返回 false，因为这两个都是 forked agent，若允许它们内部再触发 autoCompact 会死锁；`marble_origami`（context-collapse 的 ctx-agent）同样被豁免，因为它一旦触发压缩，`runPostCompactCleanup` 会调用 `resetContextCollapse()` 销毁主线程的已提交日志（模块级状态跨 fork 共享）。

失败处理上有一个熔断器：连续 3 次压缩失败即放弃本回合后续重试（src/services/compact/autoCompact.ts:70, 260-265）。注释里给出了动机数据：2026-03-10 当天有 1,279 个会话出现 50+ 次连续失败（最高 3,272 次），全局每天浪费约 25 万次 API 调用。`autoCompactIfNeeded` 的主流程是先尝试 `trySessionMemoryCompaction`（实验路径），失败或不可用才回退到 `compactConversation` 的传统摘要压缩（src/services/compact/autoCompact.ts:288-321），成功后调用 `runPostCompactCleanup` 清理各类缓存状态。

## compact.ts：摘要压缩主路径

compact.ts 共 1,705 行，承载摘要压缩的完整主流程。`compactConversation`（src/services/compact/compact.ts:387）的流程：执行 PreCompact 钩子并合并用户/钩子自定义指令 → 构造压缩 prompt → 调模型生成摘要 → 重建消息列表。

摘要生成走 `streamCompactSummary`（src/services/compact/compact.ts:1136），有两条路径。首选是 forked agent 缓存共享路径：用 `runForkedAgent` 以与主对话完全相同的 cache-key 参数（system、tools、model、消息前缀、thinking 配置）发起请求，命中主线程的提示缓存（src/services/compact/compact.ts:1188-1200）。注释明确禁止在这条路径设置 `maxOutputTokens`，因为它会通过 `Math.min(budget, maxOutputTokens-1)` 钳制 thinking 的 budget_tokens，造成 thinking 配置不匹配从而使缓存失效。这条路径由 GrowthBook 标志 `tengu_compact_cache_prefix` 控制，默认 true；注释记录了实验结论：false 路径缓存命中率仅 2%（98% miss），占全量 cache_creation 的 0.76%（约每天 38B token）（src/services/compact/compact.ts:431-438）。fork 路径失败则回退到普通流式路径 `queryModelWithStreaming`，此时才安全地设置 `maxOutputTokensOverride`（src/services/compact/compact.ts:1292-1320）。

压缩请求本身也可能 prompt-too-long（待摘要的内容就超窗）。`compactConversation` 内有一个重试循环（src/services/compact/compact.ts:450-491）：检测到摘要响应以 PTL 错误开头时，调 `truncateHeadForPTLRetry` 按 API-round 分组从头丢弃最旧的消息组：能解析出 token 缺口就按缺口丢，解析不出就丢 20% 分组，最多重试 3 次（src/services/compact/compact.ts:227-291）。这是 CC-1180 的兜底：宁可有损地丢掉最老上下文，也不让用户卡死。

发给摘要模型的内容经过两道清洗：`stripImagesFromMessages` 把图片/文档块替换成 `[image]`/`[document]` 文本标记（src/services/compact/compact.ts:145-200），`stripReinjectedAttachments` 滤掉压缩后反正会重新注入的 skill_discovery / skill_listing 附件（src/services/compact/compact.ts:211-223）。

压缩 prompt 在 prompt.ts 中定义，结构是 `NO_TOOLS_PREAMBLE + BASE_COMPACT_PROMPT + 自定义指令 + NO_TOOLS_TRAILER`（src/services/compact/prompt.ts:293-303）。前置的禁工具声明针对一个实测问题：缓存共享 fork 路径继承了父会话的完整工具集（cache-key 匹配要求），Sonnet 4.6+ 的 adaptive-thinking 模型有 2.79% 的概率无视指令尝试工具调用，而 `maxTurns: 1` 下被拒绝的工具调用意味着没有文本输出、直接掉到回退路径（4.5 上仅 0.01%）（src/services/compact/prompt.ts:12-18）。摘要模板要求模型先输出 `<analysis>` 草稿块再输出 `<summary>`，九个固定小节（主要意图、技术概念、文件与代码、错误与修复、全部用户消息、待办、当前工作、下一步等）（src/services/compact/prompt.ts:61-143）；`formatCompactSummary` 在写回上下文前剥掉 `<analysis>`，它只是提升摘要质量的草稿，没有保留价值（src/services/compact/prompt.ts:311-335）。

阈值判定结果不仅驱动压缩，也驱动 UI 的三种状态提示。`calculateTokenWarningState` 用同一套 buffer 常量算出 `percentLeft`、`isAboveWarningThreshold`、`isAboveErrorThreshold`、`isAboveAutoCompactThreshold` 与 `isAtBlockingLimit` 五个量（src/services/compact/autoCompact.ts:93-145）；autoCompact 关闭时，警告与错误阈值改用有效窗口本身做基准，阻塞线则是"有效窗口 - 3,000"，即留给手动 /compact 的最后余量。这意味着"上下文快满了"的黄色警告（剩 20K）与自动压缩触发（剩 13K）之间存在约 7K token 的缓冲带，用户看到警告后还有几个回合可以主动干预。

## 压缩后的消息重建：buildPostCompactMessages

压缩产物统一由 `CompactionResult` 承载，`buildPostCompactMessages` 以固定顺序重建消息列表（src/services/compact/compact.ts:330-338）：

```typescript
export function buildPostCompactMessages(result: CompactionResult): Message[] {
  return [
    result.boundaryMarker,
    ...result.summaryMessages,
    ...(result.messagesToKeep ?? []),
    ...result.attachments,
    ...result.hookResults,
  ]
}
```

`boundaryMarker` 是由 `createCompactBoundaryMessage` 生成的系统边界消息，记录触发类型（auto/manual）、压缩前 token 数和锚点 UUID，还会把压缩前已发现的 deferred 工具名写入 `compactMetadata.preCompactDiscoveredTools`，因为摘要不会保留 tool_reference 块，压缩后的 schema 过滤需要这份清单继续向 API 发送已加载工具（src/services/compact/compact.ts:598-611）。`summaryMessages` 是一条 `isCompactSummary: true` 的用户消息，内容包含格式化摘要、完整 transcript 路径（供模型回读压缩前细节）以及"不要寒暄、直接续上"的续接指令（src/services/compact/prompt.ts:337-374）。`attachments` 部分按预算恢复上下文：最多 5 个文件、文件总预算 50K token、单文件 5K、技能总预算 25K（src/services/compact/compact.ts:122-130），外加 plan 附件、plan-mode 指令、已调用技能内容和 deferred 工具/agent 列表/MCP 指令的 delta 重播（src/services/compact/compact.ts:532-585）。

## 微压缩：microCompact 与 apiMicrocompact

摘要压缩代价大，而且会打断当前流程，适合作为最后手段。在它触发之前，粒度更细的微压缩在每次请求前运行。`microcompactMessages`（src/services/compact/microCompact.ts:253）只处理白名单工具的产出：FileRead、Shell、Grep、Glob、WebSearch、WebFetch、FileEdit、FileWrite（src/services/compact/microCompact.ts:41-50）。

微压缩内部有三条路径，按优先级短路。第一条是 time-based 触发：若距上一条 assistant 消息的间隔超过阈值（GrowthBook 配置 `tengu_slate_heron`，默认 60 分钟），说明服务端 1 小时提示缓存 TTL 已过期、前缀无论如何要全量重写，此时直接把除最近 N 条（默认 5）外的可压缩工具结果内容替换为 `[Old tool result content cleared]`（src/services/compact/microCompact.ts:446-529；src/services/compact/timeBasedMCConfig.ts:30-34）。注释点明了设计逻辑：缓存已冷，content-clear 不需要保守，清得越多重写量越小。保留数下限钳制为 1，因为 `slice(-0)` 会保留全部，而清空全部结果会让模型失去全部工作上下文（src/services/compact/microCompact.ts:458-461）。

第二条是 cached microcompact（ant-only，`feature('CACHED_MICROCOMPACT')`）：不改本地消息内容，而是注册工具结果、按计数阈值选出待删工具，生成 `cache_edits` 块交给 API 层做缓存编辑删除（src/services/compact/microCompact.ts:305-399）。只对主线程启用，防止 forked agent 把自己的工具结果注册进全局状态。代码注释还记录了一个修复：querySource 判定从 `=== 'repl_main_thread'` 改为 `startsWith` 前缀匹配，因为非默认 output style 会把 source 变成 `repl_main_thread:outputStyle:<style>`，旧判定让这部分用户被静默排除（src/services/compact/microCompact.ts:243-251）。

第三条在 apiMicrocompact.ts，是服务端原生 context management 的客户端配置：`getAPIContextManagement` 构造 `clear_tool_uses_20250919` 策略，默认 180K input token 触发、清到保留 40K 的目标（`clear_at_least = trigger - target`），可清结果的工具与可清调用的工具分成两个清单（src/services/compact/apiMicrocompact.ts:16-32, 112-150）。thinking 块单独走 `clear_thinking_20251015` 策略：空闲超 1 小时（缓存必然 miss）时只保留最近 1 个 thinking turn（src/services/compact/apiMicrocompact.ts:82-87）。工具清理策略目前是 ant-only（`USER_TYPE !== 'ant'` 直接跳过）。

## 会话记忆压缩：sessionMemoryCompact

`trySessionMemoryCompaction` 是 autoCompact 流程里先于传统摘要压缩尝试的实验路径（src/services/compact/autoCompact.ts:288），由 `tengu_session_memory` 与 `tengu_sm_compact` 双标志门控（src/services/compact/sessionMemoryCompact.ts:403-432）。思路：会话记忆（session memory）本就在持续抽取会话要点，压缩时直接拿它当摘要，省掉一次摘要 API 调用；只需决定保留多少近期原文。

保留窗口由 `calculateMessagesToKeepIndex` 计算：默认至少保留 10K token、至少 5 条含文本块的消息，上限 40K token（src/services/compact/sessionMemoryCompact.ts:57-61, 324-397）。从 `lastSummarizedMessageId` 之后开始向前扩展直到满足下限，且不回退越过上一个压缩边界。切点确定后还要经 `adjustIndexToPreserveAPIInvariants` 修正：若保留区间里的 tool_result 找不到配对的 tool_use，或 assistant 消息与前面的 thinking 块共享 `message.id`（流式按块拆消息产生），就把起点前移，避免产生孤儿 tool_result 导致 API 报错（src/services/compact/sessionMemoryCompact.ts:232-314，注释里有两个具体 bug 场景）。这条路径没有摘要调用，因此 `postCompactTokenCount` 与 `truePostCompactTokenCount` 收敛为同一估算值（src/services/compact/sessionMemoryCompact.ts:498-502）；若保留后仍超过 autoCompact 阈值，返回 null 回退到传统压缩（src/services/compact/sessionMemoryCompact.ts:605-614）。

## 工具结果卸载与预算：toolResultStorage

最前面一层发生在工具结果写入上下文的那一刻。`maybePersistLargeToolResult` 将超过阈值的结果整体落盘到 `tool-results/` 目录，上下文里只留 `<persisted-output>` 包裹的 2KB 预览和文件路径（src/utils/toolResultStorage.ts:272-334, 189-199）。阈值按工具解析：GrowthBook 覆盖（`tengu_satin_quoll`）优先，否则取工具自声明上限与全局默认的较小值；`maxResultSizeChars: Infinity`（如 Read）硬性不持久化，把输出写盘再让模型用 Read 读回来等于循环（src/utils/toolResultStorage.ts:55-78）。空结果被替换成 `(xxx completed with no output)`，因为 inc-4586 发现 prompt 尾部的空 tool_result 会让某些模型匹配到回合边界停止符、零输出结束回合（src/utils/toolResultStorage.ts:280-295）。

单条限流之上还有按消息的聚合预算 `enforceToolResultBudget`（`tengu_hawthorn_steeple` 门控，额度由 `tengu_hawthorn_window` 覆盖）：按 API 线级用户消息分组（连续 user 消息会被 `normalizeMessagesForAPI` 合并，预算必须按合并后的口径统计），同一条消息内工具结果总量超限时，从最大的 fresh 结果开始落盘替换，直到达标（src/utils/toolResultStorage.ts:769-909）。关键设计是 `ContentReplacementState` 的三分区（src/utils/toolResultStorage.ts:649-667）：`mustReapply` 每回合从 Map 重放字节级一致的替换串，`frozen` 永不替换，只有 `fresh` 参与当回合的替换决策。一旦某个结果以原文发给过模型，它之后就不再被替换，否则前缀变化会打爆提示缓存。替换决策以 `ContentReplacementRecord` 写入 transcript，resume 时重建同一状态（src/utils/toolResultStorage.ts:960-988）。

## 部分压缩与压缩后清理

除全量压缩外，`partialCompactConversation` 支持以用户选中的消息为轴做方向性压缩：`direction: 'from'` 摘要选中点之后的消息、保留更早前缀（前缀缓存得以保留）；`direction: 'up_to'` 摘要之前、保留之后（摘要插到保留段前面，前缀缓存失效）（src/services/compact/compact.ts:765-800）。'up_to' 方向必须先从保留段里剥掉旧的压缩边界与旧摘要，否则加载器反向扫描定位边界时会被旧边界截获、丢掉新摘要。两种方向对应 prompt.ts 里两套不同的模板：'up_to' 模板明确告知模型"摘要将置于会话开头，更新的消息会跟在其后（你看不到它们）"，并把第 9 节从"下一步"换成"继续工作所需上下文"（src/services/compact/prompt.ts:206-267）。

压缩成功后，`runPostCompactCleanup` 集中清理被压缩失效的各类模块级状态：microcompact 注册表、系统 prompt 分节缓存、分类器审批、Bash 投机权限检查、会话消息缓存等（src/services/compact/postCompactCleanup.ts:31-77）。还有两处刻意的"不清理"。一是不重置 `sentSkillNames`，因为重新注入约 4K token 的完整技能清单是纯 cache_creation 开销，而模型 schema 里仍有 SkillTool。二是 `getUserContext` 与 `getMemoryFiles` 缓存只在主线程压缩时清理，因为子 agent 与主线程同进程共享模块级状态，子 agent 压缩时清这些会损坏主线程（src/services/compact/postCompactCleanup.ts:36-61）。contextCollapse 的 store 同理，仅主线程压缩才 `resetContextCollapse()`。

## Feature-gated 实验与缓存张力

在外部构建中，reactiveCompact、snipCompact（HISTORY_SNIP）、contextCollapse 的实现文件被 `feature()` 死码消除，但它们的行为契约留在门控代码的注释里。reactiveCompact 是"被动模式"：`tengu_cobalt_raccoon` 开启时 `shouldAutoCompact` 直接返回 false，放弃主动阈值压缩，等 API 返回 prompt-too-long 后兜底（src/services/compact/autoCompact.ts:189-199）。snipCompact 做消息级裁剪，`shouldAutoCompact` 的 `snipTokensFreed` 参数专门为它存在：snip 删除消息后，存活 assistant 消息的 usage 仍反映裁剪前的上下文，估算器看不到省下的量，需要把 snip 已算的粗差值减去（src/services/compact/autoCompact.ts:163-167, 225）。contextCollapse 启用时同样抑制 autoCompact，注释记录了精确的理由：autoCompact 触发线约在有效窗口的 93%，正好卡在 collapse 的 90% 提交线与 95% 阻塞线之间，会和 collapse 抢跑并"炸掉 collapse 正要保存的细粒度上下文"（src/services/compact/autoCompact.ts:201-223）。

这几层设计背后是同一个约束：提示缓存。每次压缩都要在"省 token"和"缓存失效"之间取舍。time-based MC 专挑缓存已失效的时刻动手，cached MC 用 cache_edits 在不动前缀的前提下删内容，预算系统冻结历史决策保证前缀稳定，摘要压缩用 forked agent 共享主线程缓存来降低压缩本身的成本。压缩点不是越早触发越好，而是要尽量与缓存生命周期对齐，这条取舍贯穿了整套 compact 源码的各个层次。

## 本篇涉及的源码文件

- `src/services/compact/autoCompact.ts`：有效窗口计算、阈值常量、自动压缩触发判定与熔断器
- `src/services/compact/compact.ts`：摘要压缩主流程 compactConversation、消息重建 buildPostCompactMessages、PTL 重试
- `src/services/compact/microCompact.ts`：请求前微压缩：time-based 清理与 cached-MC 缓存编辑路径
- `src/services/compact/apiMicrocompact.ts`：服务端原生 context management 策略配置（clear_tool_uses / clear_thinking）
- `src/services/compact/sessionMemoryCompact.ts`：基于会话记忆的压缩实验路径与保留窗口计算
- `src/services/compact/postCompactCleanup.ts`：压缩后模块级状态清理（含 contextCollapse 重置）
- `src/services/compact/prompt.ts`：压缩 prompt 模板、禁工具前置声明与摘要格式化
- `src/services/compact/timeBasedMCConfig.ts`：time-based 微压缩的 GrowthBook 配置与默认值
- `src/utils/toolResultStorage.ts`：大工具结果落盘、空结果标记与按消息聚合预算
- `src/utils/context.ts`：模型上下文窗口解析与 COMPACT_MAX_OUTPUT_TOKENS 常量
