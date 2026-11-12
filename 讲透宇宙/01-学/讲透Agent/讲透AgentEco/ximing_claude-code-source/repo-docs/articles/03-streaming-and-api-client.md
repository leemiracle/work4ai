---
title: Claude Code 源码拆解 03：流式协议与 API 客户端——边生成边执行
date: "2026-04-04 14:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 03/20 篇 · 对应主题：流式与异步

# 流式协议与 API 客户端：边生成边执行

上一篇看过主循环的骨架之后，本篇聚焦它脚下的一层：Claude Code 如何把一次 LLM 调用拆成"流式接收"与"流式执行"两条并行流水线。主要文件是 `src/services/api/claude.ts`（3419 行，请求构造、流事件状态机、usage 累计、资源清理）和 `src/services/tools/StreamingToolExecutor.ts`（530 行，工具并发执行器），外加 `withRetry.ts` 与 `errors.ts` 两个支撑模块。本篇要拆的主线是：assistant 消息还没生成完，已经完整的 tool_use 块就开始执行了。

## 请求的出入口：queryModelWithStreaming

`queryModelWithStreaming` 本身是一个薄封装，套上 VCR 录制层后直接委托给内部的 `queryModel` 生成器（src/services/api/claude.ts:752-780）。流式请求在 `queryModel`（src/services/api/claude.ts:1017）里发出，它刻意绕开 SDK 的 `BetaMessageStream` 高级封装，直接用原始 `Stream`，原因写在代码注释里：

```typescript
// Use raw stream instead of BetaMessageStream to avoid O(n²) partial JSON parsing
// BetaMessageStream calls partialParse() on every input_json_delta, which we don't need
// since we handle tool input accumulation ourselves
const result = await anthropic.beta.messages
  .create(
    { ...params, stream: true },
    { signal, ...(clientRequestId && { headers: { [CLIENT_REQUEST_ID_HEADER]: clientRequestId } }) },
  )
  .withResponse()
```

（src/services/api/claude.ts:1818-1832）

`BetaMessageStream` 会在每个 `input_json_delta` 上调用 `partialParse()` 做增量 JSON 解析，工具输入长的时候成本是 O(n²)。Claude Code 选择自己按字符串拼接 tool input，只在 `content_block_stop` 时解析一次，这与后文 StreamingToolExecutor 的"块完整即执行"模型正好配套。客户端以 `maxRetries: 0` 创建，SDK 的自动重试被禁用，重试完全交给外层的 `withRetry` 手动实现（src/services/api/claude.ts:1781）。`.withResponse()` 同时拿到 `request_id` 和原始 `Response` 对象，后者在后面的资源清理里用到。

## 流事件状态机与 usage 累计

拿到 stream 后，`queryModel` 进入一个 for-await 循环，把 SDK 的原始事件翻译成两类产出：每个完整的 content block 立即组装成一条 `AssistantMessage` yield 出去；原始事件本身也作为 `stream_event` 透传给 UI。

逐条看几个 case：

- `message_start`：记录 `partialMessage`、计算 TTFT（time to first token）、初始化 usage（src/services/api/claude.ts:1980-1983）。
- `content_block_start`：对 tool_use 块把 `input` 重置为空字符串，后续 delta 往里拼接（src/services/api/claude.ts:1998-2001）。text 块同样清空，注释里说明了原因：SDK 有时在 start 事件里带一遍 text，delta 里再重复一遍，无法可靠区分，干脆忽略 start 里的内容（src/services/api/claude.ts:2022-2028）。
- `content_block_stop`：把这一个块组装成 `AssistantMessage` 并立即 yield（src/services/api/claude.ts:2192-2210）。这就是"边生成边执行"的供给端：下游 query.ts 每收到一条含 tool_use 的 assistant 消息，立刻把它喂给 StreamingToolExecutor。
- `message_delta`：累计 usage、写回 stop_reason、结算成本（src/services/api/claude.ts:2213-2256）。

写回 usage 的代码有一个刻意为之的坑：

```typescript
// IMPORTANT: Use direct property mutation, not object replacement.
// The transcript write queue holds a reference to message.message
// and serializes it lazily (100ms flush interval). Object
// replacement ({ ...lastMsg.message, usage }) would disconnect
// the queued reference; direct mutation ensures the transcript
// captures the final values.
stopReason = part.delta.stop_reason
const lastMsg = newMessages.at(-1)
if (lastMsg) {
  lastMsg.message.usage = usage
  lastMsg.message.stop_reason = stopReason
}
```

（src/services/api/claude.ts:2236-2248）

`message_delta` 在 `content_block_stop` 之后到达，此时 assistant 消息已经 yield 出去、被 transcript 写队列持有了引用。如果用展开运算符替换对象，队列里那份引用就永远是 `output_tokens: 0` 的初值；只有原地改属性能让延迟序列化的 transcript 拿到最终值。

usage 累计由 `updateUsage` 完成，语义是"取新值而非累加"，因为 Anthropic 流式 API 上报的是累计总量而非增量（src/services/api/claude.ts:2915-2917）。一个细节是防御 0 值覆盖：`message_delta` 可能对 input 相关字段上报显式的 0，而这些字段的真实值在 `message_start` 就已确定，所以只有非 null 且大于 0 才更新（src/services/api/claude.ts:2931-2945）。跨多轮 assistant 的总量另由 `accumulateUsage` 做加法（src/services/api/claude.ts:2993）。

## 资源清理：cleanupStream 与流看门狗

流式连接持有 V8 堆之外的资源。代码注释明确指出：`Response` 对象持有原生 TLS/socket 缓冲区，必须显式 cancel，否则在 Node/npm 路径上会泄漏（GH #32920）（src/services/api/claude.ts:1515-1518）。因此有了统一的释放函数：

```typescript
function releaseStreamResources(): void {
  cleanupStream(stream)
  stream = undefined
  if (streamResponse) {
    streamResponse.body?.cancel().catch(() => {})
    streamResponse = undefined
  }
}
```

（src/services/api/claude.ts:1519-1526）

`cleanupStream` 本体只做一件事：若 stream 的 controller 尚未 abort 则 abort，异常一律吞掉（src/services/api/claude.ts:2898-2912）。释放调用被放进 `finally` 块，注释解释了为什么必须在 finally：消费者 `break` 出 for-await 或 query.ts 触发 abort 时，生成器通过 `.return()` 提前终止，try 块后面的普通代码不会执行，只有 finally 能保证运行（src/services/api/claude.ts:2808-2815）。

另一个流式特有的失败模式是"连接悄悄死掉"：SDK 的请求超时只覆盖初始 fetch，不覆盖流式 body，一个被静默丢弃的连接会让会话无限挂起。对策是流看门狗：`CLAUDE_ENABLE_STREAM_WATCHDOG` 开启后，90 秒（`CLAUDE_STREAM_IDLE_TIMEOUT_MS` 可配）没有新 chunk 就主动 abort 流（src/services/api/claude.ts:1868-1879）。与看门狗配套的还有一套被动 stall 检测：只有当下一个 chunk 到达时才能发现"上一个 chunk 等了很久"，所以它只能事后统计，无法主动杀流，这正是看门狗必须用 setTimeout 主动触发的原因（src/services/api/claude.ts:1868-1873）。被看门狗杀掉的流不当成正常完成，而是抛出错误走非流式 fallback（src/services/api/claude.ts:2310-2335）。类似的，代理服务器返回 200 但 body 不是 SSE、或流在 content_block_stop 之前结束这两种代理故障，也会被"流结束但没有 assistant 消息"检测捕获并触发 fallback（src/services/api/claude.ts:2337-2364）。这里有个防止误报的判据：必须同时满足没有 content block 完成且没有收到 stop_reason 才算流不完整，因为结构化输出场景下模型第二轮合法地返回 end_turn 加零个内容块，不能当成故障（src/services/api/claude.ts:2346-2349）。

非流式 fallback 由 `executeNonStreamingRequest` 统一执行（src/services/api/claude.ts:818）。它复用同一个 `withRetry` 循环，但把请求参数经 `adjustParamsForNonStreaming` 裁剪到 `MAX_NON_STREAMING_TOKENS = 64_000` 以内，并施加独立的单次超时：远程会话 120 秒（压在 CCR 容器约 5 分钟的 idle-kill 之下，让挂死的 fallback 以干净的超时错误暴露而不是被 SIGKILL），本地默认 300 秒（src/services/api/claude.ts:795-811）。fallback 的成本记账被刻意放进 `finally`：流式路径在 yield 之前的 message_delta 处理里就记了账，而 fallback 是先 push 消息再 yield，记账必须在 finally 里才能在消费者于 yield 处 `.return()` 时仍然执行（src/services/api/claude.ts:2817-2830）。

## StreamingToolExecutor：边生成边执行

在 query.ts 的主循环里，每当流中 yield 出一条含 tool_use 块的 assistant 消息，立刻调用 `streamingToolExecutor.addTool(toolBlock, message)`（src/query.ts:841-843），随后用 `getCompletedResults()` 非阻塞地取回已完成的结果（src/query.ts:851）。也就是说，模型还在生成第三个工具调用的 JSON 时，第一个工具可能已经在跑了。

执行器的并发模型是两级分类（src/services/tools/StreamingToolExecutor.ts:129-135）：

```typescript
private canExecuteTool(isConcurrencySafe: boolean): boolean {
  const executingTools = this.tools.filter(t => t.status === 'executing')
  return (
    executingTools.length === 0 ||
    (isConcurrencySafe && executingTools.every(t => t.isConcurrencySafe))
  )
}
```

并发安全的工具（如 Read）可以与其他并发安全工具并行；非并发安全的工具（如 Edit、Bash 的写操作）必须独占执行。`isConcurrencySafe` 由工具定义根据解析后的输入判定，判定函数本身抛异常时保守地视为不安全（src/services/tools/StreamingToolExecutor.ts:104-113）。

结果的产出顺序严格按工具接收顺序。`getCompletedResults()` 顺序遍历工具数组，遇到"执行中且非并发安全"的工具直接 break，即使后面的并发工具已经完成，也要等前面这个非并发工具先出结果（src/services/tools/StreamingToolExecutor.ts:428-438）。progress 类型的消息走独立通道 `pendingProgress`，不等工具完成就立即 yield（src/services/tools/StreamingToolExecutor.ts:419-422）。流结束后，`getRemainingResults()` 用 `Promise.race` 在"任一执行中工具完成"与"任一 progress 到达"之间等待，直到所有工具进入 yielded 状态（src/services/tools/StreamingToolExecutor.ts:453-490）。

### Bash 失败时 abort 兄弟调用

错误传播是选择性级联的。代码注释给出了理由：Bash 命令之间常有隐式依赖链（mkdir 失败后续命令无意义），而 Read/WebFetch 彼此独立，一个失败不应株连其余（src/services/tools/StreamingToolExecutor.ts:356-358）：

```typescript
if (isErrorResult) {
  thisToolErrored = true
  // Only Bash errors cancel siblings. Bash commands often have implicit
  // dependency chains (e.g. mkdir fails → subsequent commands pointless).
  // Read/WebFetch/etc are independent — one failure shouldn't nuke the rest.
  if (tool.block.name === BASH_TOOL_NAME) {
    this.hasErrored = true
    this.erroredToolDescription = this.getToolDescription(tool)
    this.siblingAbortController.abort('sibling_error')
  }
}
```

（src/services/tools/StreamingToolExecutor.ts:354-364）

实现上是一个三级 AbortController 结构：`siblingAbortController` 是主 abortController 的子节点，每个工具又持有 `siblingAbortController` 的子节点（src/services/tools/StreamingToolExecutor.ts:59-61, 301-303）。Bash 出错时 abort 中间层，所有兄弟工具的子进程（Bash spawn 监听的就是这个信号）立即死亡，而父节点不受影响，query.ts 不会因此结束当前回合（src/services/tools/StreamingToolExecutor.ts:45-47）。反向的冒泡也存在：工具层的 abort（比如权限弹窗拒绝）如果不是 sibling_error 且父节点未 abort，会向上传播到主 controller，让 query 循环结束回合。注释里标注这是 #21056 回归的修复，否则 ExitPlanMode 会把 REJECT_MESSAGE 发给模型而不是中止（src/services/tools/StreamingToolExecutor.ts:304-318）。

被级联取消的工具不会静默消失，而是收到一条合成的 tool_result 错误消息。合成消息分三种原因：`sibling_error`（带上出错工具的描述，如 `Cancelled: parallel tool call Bash(npm test…) errored`）、`user_interrupted`（用 REJECT_MESSAGE，UI 显示"用户拒绝"）、`streaming_fallback`（流式 fallback 时 `discard()` 丢弃全部待处理结果）（src/services/tools/StreamingToolExecutor.ts:153-205）。fallback 场景在 query.ts 里对应：旧 executor 被 discard，立刻 new 一个新的，防止旧 tool_use_id 的孤儿 tool_result 混进 fallback 响应之后的消息流（src/query.ts:730-740）。

## 错误分类体系：errors.ts

`errors.ts`（1207 行）是错误到用户可见消息的映射层，中心函数是 `getAssistantMessageFromError`（src/services/api/errors.ts:425）。它按错误类型分支出不同的 AssistantMessage：SDK 超时归一为 "Request timed out"（src/services/api/errors.ts:434-443）；429 走一组 `anthropic-ratelimit-unified-*` 响应头解析，区分 five_hour / seven_day / overage 等限额类型并生成对应文案（src/services/api/errors.ts:465-494）。

prompt-too-long 的处理分两层。API 直连返回 400，Vertex 返回 413 且大小写不同，错误信息只有一个字符串，Claude Code 把它拆开使用：面向 UI 的 content 保持固定文案 `Prompt is too long`，带 token 数字的原始错误串存进 `errorDetails` 字段（src/services/api/errors.ts:560-574）：

```typescript
if (
  error instanceof Error &&
  error.message.toLowerCase().includes('prompt is too long')
) {
  // Content stays generic (UI matches on exact string). The raw error with
  // token counts goes into errorDetails — reactive compact's retry loop
  // parses the gap from there via getPromptTooLongTokenGap.
  return createAssistantAPIErrorMessage({
    content: PROMPT_TOO_LONG_ERROR_MESSAGE,
    error: 'invalid_request',
    errorDetails: error.message,
  })
}
```

下游的判定分三步：`isPromptTooLongMessage` 按 content 前缀匹配（src/services/api/errors.ts:64-77）；`parsePromptTooLongTokenCounts` 用一个宽松正则 `/prompt is too long[^0-9]*(\d+)\s*tokens?\s*>\s*(\d+)/i` 从 errorDetails 里抠出实际/上限 token 数，注释说明宽松是故意的：原始串可能包着 SDK 前缀或 JSON 信封，Vertex 大小写也不同（src/services/api/errors.ts:85-96）；`getPromptTooLongTokenGap` 算出超出量，reactive compact 用这个 gap 在一次重试里直接跳过多个分组，而不是一轮剥一层（src/services/api/errors.ts:104-118）。media-size 错误（图片/PDF 超限）有平行的判定对 `isMediaSizeError` / `isMediaSizeErrorMessage`，决定 reactive compact 是剥离媒体重试还是直接放弃（src/services/api/errors.ts:133-153）。

## withRetry：重试、529 与 fallback 模型

`withRetry` 是一个异步生成器：正常路径 return 操作结果，重试过程中 yield `SystemAPIErrorMessage` 让 UI 显示"正在第 N 次重试"（src/services/api/withRetry.ts:170-178）。默认最多 10 次（src/services/api/withRetry.ts:52）。

重试判定在内部函数 `shouldRetry`（src/services/api/withRetry.ts:696）。规则按优先级叠放：429/529 在 unattended 模式下恒可重试；CCR 远程模式下 401/403 视为瞬时抖动（基础设施 JWT 抖动而非凭证错误）；错误消息含 `"type":"overloaded_error"` 直接可重试，注释解释 SDK 在流式过程中有时丢 529 状态码，只能匹配消息体（src/services/api/withRetry.ts:719-724）；max_tokens 上下文溢出可重试（重试前会调小 max_tokens）。然后是 `x-should-retry` 响应头：服务端显式表态就服从，但 Max/Pro 订阅用户的 `true` 意味着"几小时后才行"，所以订阅用户忽略它，企业 PAYG 用户才遵循（src/services/api/withRetry.ts:731-751）。最后是无头判定：连接错误、408、409 可重试，429 对订阅用户不重试（src/services/api/withRetry.ts:753-768）。退避是 500ms 起步的指数退避加 25% 抖动，`retry-after` 头优先（src/services/api/withRetry.ts:530-548）。

529（过载）有一套独立的计数与 fallback 逻辑。连续 529 达到 `MAX_529_RETRIES = 3` 且配置了 fallbackModel 时，抛出 `FallbackTriggeredError` 触发模型降级（src/services/api/withRetry.ts:327-351）：

```typescript
consecutive529Errors++
if (consecutive529Errors >= MAX_529_RETRIES) {
  if (options.fallbackModel) {
    logEvent('tengu_api_opus_fallback_triggered', { ... })
    throw new FallbackTriggeredError(options.model, options.fallbackModel)
  }
  ...
}
```

529 还有一个反放大设计：容量雪崩期间每次重试是 3-10 倍的网关放大，所以只有用户在阻塞等待的前台 querySource（repl_main_thread、sdk、compact、agent 等，显式枚举在 `FOREGROUND_529_RETRY_SOURCES`）才重试 529；摘要、标题、建议、分类器等后台来源直接放弃，反正用户也看不到它们失败（src/services/api/withRetry.ts:57-89, 316-324）。`initialConsecutive529Errors` 参数用于流式 529 后转非流式 fallback 的场景，让流式那次 529 也计入总数，保证"几次 529 后降级"与请求模式无关（src/services/api/withRetry.ts:135-141）。

上下文溢出错误（400 + "input length and `max_tokens` exceed context limit"）走的是另一条自适应路径：正则解析出 inputTokens 与 contextLimit，留出 1000 token 安全余量后重算 max_tokens，下限 3000（`FLOOR_OUTPUT_TOKENS`），同时保证 thinking 预算 + 至少 1 个输出 token，然后写进 `retryContext.maxTokensOverride` 继续（src/services/api/withRetry.ts:384-427, 550-595）。注释说明扩展上下文窗口 beta 上线后 API 改用 `model_context_window_exceeded` stop_reason，这条 400 分支只为向后兼容保留（src/services/api/withRetry.ts:385-387）。认证类错误（401、OAuth token revoked、Bedrock/Vertex 凭证失败、ECONNRESET/EPIPE 的陈旧 keep-alive 连接）触发客户端重建与 token 刷新后再试（src/services/api/withRetry.ts:212-251）。

`CLAUDE_CODE_UNATTENDED_RETRY` 开启的 persistent 模式把重试变成无限循环：attempt 被钳制在 maxRetries，改用独立的 persistentAttempt 计数，退避上限 5 分钟，封顶 6 小时。长等待被切成 30 秒一片的 sleep，每片之前 yield 一条 `SystemAPIErrorMessage`，目的是让宿主环境看到周期性的 stdout 活动，避免无人值守会话在长退避期间被判定 idle 而回收（src/services/api/withRetry.ts:96-98, 477-506）。窗口型限额（如 5 小时 Max/Pro 额度）还带 reset 时间戳，直接睡到 reset 时刻而不是每 5 分钟空转轮询（src/services/api/withRetry.ts:435-447）。

## getExtraBodyParams 与 anti_distillation

请求体最后一个装配点是 `getExtraBodyParams`（src/services/api/claude.ts:272）。它做三件事：解析环境变量 `CLAUDE_CODE_EXTRA_BODY`（用户自定义的额外请求参数）；注入 anti-distillation 标记；合并 beta headers。

```typescript
// Anti-distillation: send fake_tools opt-in for 1P CLI only
if (
  feature('ANTI_DISTILLATION_CC')
    ? process.env.CLAUDE_CODE_ENTRYPOINT === 'cli' &&
      shouldIncludeFirstPartyOnlyBetas() &&
      getFeatureValue_CACHED_MAY_BE_STALE(
        'tengu_anti_distill_fake_tool_injection',
        false,
      )
    : false
) {
  result.anti_distillation = ['fake_tools']
}
```

（src/services/api/claude.ts:301-313）

`anti_distillation: ['fake_tools']` 只在官方 1P CLI（`CLAUDE_CODE_ENTRYPOINT === 'cli'` 且一方 beta 开关打开）下发送，是服务端识别官方客户端、注入诱饵工具以防蒸馏的 opt-in 信号。环境变量解析处有一个隐蔽的正确性修复：`safeParseJSON` 是 LRU 缓存的，同一字符串返回同一对象引用，直接改 `result` 会污染缓存，所以必须浅拷贝（src/services/api/claude.ts:283-286）。beta headers 与已有 `anthropic_beta` 数组合并时去重（src/services/api/claude.ts:316-328）。

## 小结

这一层的结构可以概括为一个流水线：`withRetry` 包住原始 SSE 流（避开 SDK 的 O(n²) 增量解析），流事件状态机把每个完整 content block 立刻变成 assistant 消息推给下游；StreamingToolExecutor 接住 tool_use 块就地并发执行、按接收顺序回吐结果，Bash 失败通过中间层 AbortController 级联杀掉兄弟进程；错误经 errors.ts 分类成"可重试 / 可降级 / 可恢复（prompt-too-long 带 gap 给 reactive compact）"三类走向；usage 按"累计量取新值、防御 0 覆盖"的规则滚动更新。整条链路上最反复出现的主题是资源确定性：原生 socket 缓冲区要显式 cancel，流要有看门狗，重试要有 querySource 白名单防放大。

## 本篇涉及的源码文件

- `src/services/api/claude.ts`：请求参数装配、流事件状态机、usage 累计、流资源清理与看门狗
- `src/services/tools/StreamingToolExecutor.ts`：流式工具并发执行器，按序发射结果、Bash 失败级联 abort 兄弟调用
- `src/services/api/withRetry.ts`：手动重试循环，x-should-retry 判定、529 计数与 fallback 模型、max_tokens 自适应
- `src/services/api/errors.ts`：API 错误到用户消息的分类映射，prompt-too-long / media-size 的 errorDetails 通道
- `src/query.ts`：主循环对流式消息与 StreamingToolExecutor 的接线（addTool / getCompletedResults / discard）
