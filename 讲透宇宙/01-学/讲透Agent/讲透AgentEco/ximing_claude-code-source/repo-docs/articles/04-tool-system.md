---
title: Claude Code 源码拆解 04：工具系统架构：注册、调度与并发
date: "2026-04-04 16:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 04/20 篇 · 对应主题：工具调用的手艺

# 工具系统架构：注册、调度与并发

Claude Code 的工具系统由四层组成：`Tool.ts` 定义接口契约，`tools.ts` 负责注册与过滤，`toolOrchestration.ts` 做并发分区调度，`toolExecution.ts` 与 `toolHooks.ts` 承担单次调用的全生命周期。

## Tool 接口：一个超宽的契约

`Tool` 类型是一个泛型对象字面量接口，参数化为 `Input`（zod schema）、`Output` 和 `P`（进度数据类型）（src/Tool.ts:362）。它的字段可以分成五组：

1. 身份与检索：`name`、`aliases`（重命名后的向后兼容别名）、`searchHint`（供 ToolSearch 关键词匹配）、`mcpInfo`（MCP 工具的原始 server/tool 名）。
2. 执行：`call()`、`inputSchema`、`validateInput()`、`checkPermissions()`。
3. 调度决策：`isConcurrencySafe()`、`isReadOnly()`、`isDestructive()`、`interruptBehavior()`。
4. 提示词面：`description()`、`prompt()`、`inputJSONSchema`（MCP 工具直接给 JSON Schema，不走 zod 转换）。
5. 渲染面：`renderToolUseMessage`、`renderToolResultMessage`、`renderGroupedToolUse` 等近十个 React 渲染钩子。

执行入口 `call` 的签名除了 args 和 context，还接收 `canUseTool` 回调和父消息（src/Tool.ts:379-385）：工具在执行过程中可以再次发起权限询问（例如 BashTool 对子命令逐个确认），也能拿到触发自己的那条 assistant 消息用于归因。

两个上下文类型把工具运行时可访问的外部资源显式建模成类型。`ToolPermissionContext` 是不可变的权限快照：`mode`、三组规则（alwaysAllow/alwaysDeny/alwaysAsk）、`additionalWorkingDirectories` 等，整体被 `DeepImmutable` 包裹（src/Tool.ts:123-138）。`ToolUseContext` 则是运行时大杂烩：`abortController`、`readFileState` 缓存、`getAppState/setAppState`、MCP 连接列表、消息历史、十几个 UI 回调（src/Tool.ts:158-300）。工具不 import 全局状态，一切经由 context 注入，因此同一套工具实现可以在主线程、子代理、SDK 三种宿主中复用。

进度上报走类型化通道：`Progress = ToolProgressData | HookProgress`（src/Tool.ts:305），每种工具声明自己的进度负载类型（`BashProgress`、`AgentToolProgress`、`MCPProgress` 等），通过 `call` 的第五个参数 `onProgress` 回传（src/Tool.ts:338-340）。工具进度与 hook 进度在同一通道里靠 `type` 字段区分，`filterToolProgressMessages` 负责在渲染侧把 hook 进度滤掉（src/Tool.ts:312-319）。

`ToolResult` 除了 `data` 还有三个可选载荷（src/Tool.ts:321-336）：`newMessages` 允许工具往对话里追加额外消息（AgentTool 用它注入子代理的转写）；`contextModifier` 允许工具修改后续调用的上下文；`mcpMeta` 透传 MCP 协议的 `structuredContent` 与 `_meta` 给 SDK 消费者。工具的结果大小由 `maxResultSizeChars` 自报上限，超出部分落盘，模型只收到预览和文件路径；注释特别说明 Read 必须设为 `Infinity`，否则会出现"结果落盘→模型再 Read 落盘文件"的循环（src/Tool.ts:458-466）。

一个容易踩的坑由 `buildTool` 兜底。接口里 `isConcurrencySafe`、`isReadOnly` 等七个方法是调度与权限的安全判断依据，漏写任何一个都可能改变行为。`TOOL_DEFAULTS` 给出 fail-closed 默认值：不并发安全、不是只读、不是破坏性、`checkPermissions` 直接放行交还给通用权限系统（src/Tool.ts:757-769），`buildTool` 用展开运算符合并定义与默认值（src/Tool.ts:783-792）。默认不信任，是这套默认值的设计取向。

## tools.ts：feature-gated 注册表

工具注册没有 plugin loader，没有依赖注入容器，就是一个函数返回一个数组。`getAllBaseTools()` 返回当前环境下所有可能可用的工具（src/tools.ts:193-251）。注册表的特殊之处在于大量条件 `require`：

```typescript
const SleepTool =
  feature('PROACTIVE') || feature('KAIROS')
    ? require('./tools/SleepTool/SleepTool.js').SleepTool
    : null
const cronTools = feature('AGENT_TRIGGERS')
  ? [
      require('./tools/ScheduleCronTool/CronCreateTool.js').CronCreateTool,
      require('./tools/ScheduleCronTool/CronDeleteTool.js').CronDeleteTool,
      require('./tools/ScheduleCronTool/CronListTool.js').CronListTool,
    ]
  : []
```

（src/tools.ts:25-35）`feature()` 来自 `bun:bundle`，是构建期常量。条件不满足时 `require` 根本不执行，bundler 把对应模块做 dead code elimination，同一棵源码树由此裁剪出 external 版与 ant 内部版两套二进制，差异完全由编译期决定。`process.env.USER_TYPE === 'ant'` 的运行时判断（src/tools.ts:16-19）则覆盖构建后仍需区分的场景。数组里用展开运算符按需插入：`...(isTodoV2Enabled() ? [TaskCreateTool, ...] : [])`（src/tools.ts:218-220），运行时 feature flag 也走同一模式。

从"全部"到"本轮可用"经过三道过滤（src/tools.ts:271-327）：

1. 模式过滤：`CLAUDE_CODE_SIMPLE` 环境下只留 Bash/Read/Edit；REPL 模式启用时，REPL 独占的原语工具被隐藏（`REPL_ONLY_TOOLS`），模型只能通过 REPL 的 VM 间接使用。
2. deny 规则过滤：`filterToolsByDenyRules` 用与运行时权限检查相同的 matcher，把被 settings 里 blanket deny 的工具在列表发给模型之前就摘掉，包括 `mcp__server` 前缀规则整批剥掉某个 MCP server 的工具（src/tools.ts:262-269）。
3. `isEnabled()` 过滤：每个工具自查环境（如 WebSearch 检查 API 可用性）。

`assembleToolPool()` 把内置工具与 MCP 工具合成最终工具池（src/tools.ts:345-367），其中排序逻辑是为 prompt cache 服务的：

```typescript
const byName = (a: Tool, b: Tool) => a.name.localeCompare(b.name)
return uniqBy(
  [...builtInTools].sort(byName).concat(allowedMcpTools.sort(byName)),
  'name',
)
```

内置工具排序后作为连续前缀，MCP 工具排序后追加。注释解释了原因：服务端的缓存策略在最后一个前缀匹配的内置工具后放置全局 cache breakpoint，如果扁平排序让 MCP 工具插入内置工具之间，任何 MCP 工具变动都会使其后的所有缓存键失效。`uniqBy` 保留插入序，因此重名时内置工具胜出。工具列表的稳定性直接等于缓存命中率，缓存失效的约束就这样写进了排序函数。

文件里还有一个易混淆的 `getMergedTools()`（src/tools.ts:383-389）：它只是简单拼接内置与 MCP 工具、不排序不去重，注释说明它服务于 ToolSearch 阈值计算与 token 计数这类"只需要全量列表"的场景；真正给模型用的工具池必须走 `assembleToolPool`。REPL.tsx 的 `useMergedTools` 与 coordinator worker 的 `runAgent.ts` 都调后者，保证两条入口的工具池一致（src/tools.ts:330-334 的 doc comment）。

## toolOrchestration：按 isConcurrencySafe 分区调度

模型一次响应可能返回多个 tool_use block。`runTools` 的调度策略是把序列切成两种批次：连续的并发安全调用合并成一个并发批，其余每个调用自成一个串行批（src/services/tools/toolOrchestration.ts:86-116）：

```typescript
function partitionToolCalls(toolUseMessages, toolUseContext): Batch[] {
  return toolUseMessages.reduce((acc: Batch[], toolUse) => {
    const tool = findToolByName(toolUseContext.options.tools, toolUse.name)
    const parsedInput = tool?.inputSchema.safeParse(toolUse.input)
    const isConcurrencySafe = parsedInput?.success
      ? (() => {
          try {
            return Boolean(tool?.isConcurrencySafe(parsedInput.data))
          } catch {
            return false
          }
        })()
      : false
    if (isConcurrencySafe && acc[acc.length - 1]?.isConcurrencySafe) {
      acc[acc.length - 1]!.blocks.push(toolUse)
    } else {
      acc.push({ isConcurrencySafe, blocks: [toolUse] })
    }
    return acc
  }, [])
}
```

三个防御性细节：判定前先 `safeParse` 输入（解析失败保守地视为不安全）；`isConcurrencySafe` 本身可能抛异常（注释举例 shell-quote 解析失败），catch 后同样降级为串行；`isConcurrencySafe` 接收 input 参数，意味着安全性可以按输入判定：BashTool 对 `ls` 和对 `rm` 可以给出不同答案。分区是保序的：模型输出 [Read, Read, Edit, Read] 会被切成 [并发批×2, 串行×1, 串行×1]，批次之间严格顺序执行，批次的边界就是同步点。

并发批的执行委托给 `all()` 生成器组合子（src/utils/generators.ts:32-68），并发上限取自 `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`，默认 10（src/services/tools/toolOrchestration.ts:8-12）。`all` 的实现是手写的 race 循环：维护一个 promise 集合，每轮 `Promise.race` 取最先产出值的生成器，yield 其值并推进它的下一步；某个生成器结束时从等待队列补一个进来（src/utils/generators.ts:50-67）。没有用 p-limit 之类的库，因为这里限流的对象是"生成器的 next()"而不是普通 promise：进度消息和结果消息流经同一条流，限流必须发生在生成器粒度。

两条路径对 context 修改的处理不同。`ToolResult` 允许工具返回 `contextModifier`（src/Tool.ts:329-330），但注释明确说它"only honored for tools that aren't concurrency safe"。串行路径里 modifier 立即应用（src/services/tools/toolOrchestration.ts:140-142）；并发路径里 modifier 被按 toolUseID 排队，等整个并发批结束后才按序应用（src/services/tools/toolOrchestration.ts:42-62）。并发执行期间 context 对批内所有工具保持一致，避免了半应用状态被并发读取。

调度层还维护一份"正在执行"集合：每个工具开始前加入 `setInProgressToolUseIDs`，结束后由 `markToolUseAsComplete` 移除（src/services/tools/toolOrchestration.ts:126-129、179-188）。这份集合是 UI 层 spinner 与中断行为的依据；并发路径里注意 `setInProgressToolUseIDs` 用的是函数式更新（`prev => new Set(prev).add(...)`），多个并发工具同时修改不会互相覆盖；如果这里写成读-改-写，并发下就会丢更新。

## runToolUse：单次调用的生命周期

`runToolUse` 是一个 async generator，把一次 tool_use 块变成一串 `MessageUpdateLazy`（src/services/tools/toolExecution.ts:337）。整个调度层是生成器化的：进度、附件、权限拒绝、最终结果都是流上的事件，UI 边消费边渲染，不需要等工具跑完。

第一步是别名解析与存在性检查。先在当前工具池里按名字或别名查找；找不到再退到 `getAllBaseTools()` 全量表，且只有当名字命中的是别名（而非主名）才接受，这覆盖了旧 transcript 里调用已改名工具的场景，例如旧名 `KillShell` 映射到 `TaskStop`（src/services/tools/toolExecution.ts:345-356）。真正的未知工具直接产出 `<tool_use_error>` 结果并记录 `tengu_tool_use_error`（src/services/tools/toolExecution.ts:369-411）。同时这里完成 MCP server-type 归因：`getMcpServerType` 从 `mcp__server__tool` 命名反查连接表，取出传输类型（stdio/sse/http/ws/sdk…，src/services/tools/toolExecution.ts:272-320），之后每一条遥测事件都带上它。

第二步是输入验证。zod `safeParse` 失败返回 `InputValidationError`（src/services/tools/toolExecution.ts:615-680）；若是 deferred 工具且 schema 未发送，`buildSchemaNotSentHint` 追加提示让模型先走 ToolSearch 加载（src/services/tools/toolExecution.ts:578-597）。随后是工具自定义的 `validateInput`（src/services/tools/toolExecution.ts:683）。对 Bash 还有一个投机优化：在 hooks 和权限检查之前提前启动 allow 分类器，让它与后续阶段并行（src/services/tools/toolExecution.ts:740-752）。

第三步是 PreToolUse hooks。`runPreToolUseHooks` 把外部 hook 的各种产出翻译成统一的事件流：progress 消息、权限裁定（allow/ask/deny）、`hookUpdatedInput`（只改输入不做裁定）、`preventContinuation`、`stop`（src/services/tools/toolHooks.ts:435-461）。hook 返回 `stop` 时整个调用终止（src/services/tools/toolExecution.ts:848-860）。

第四步是权限裁定。`resolveHookPermissionDecision` 是 hook 与常规权限系统的胶水，它封装了一条不变式：hook 的 allow 不绕过 settings.json 的 deny/ask 规则。hook 放行后仍要过 `checkRuleBasedPermissions`，deny 规则胜出，ask 规则仍然弹窗（src/services/tools/toolHooks.ts:347-405）。`requiresUserInteraction()` 为真的工具（如 AskUserQuestion）即使 hook 放行也必须走 `canUseTool`，除非 hook 用 `updatedInput` 代替了用户交互（src/services/tools/toolHooks.ts:344-370）。这个函数被主循环和 REPLTool 内部调用共享，保证两条路径权限语义一致（src/services/tools/toolHooks.ts:329-331）。裁定不是 allow 就构造拒绝消息返回，不再执行工具（src/services/tools/toolExecution.ts:995-1104）。

第五步是执行。`tool.call` 被调用，context 里补上 `toolUseId` 和 `userModified`（src/services/tools/toolExecution.ts:1207-1213）。进度回调与最终结果通过 `streamedCheckPermissionsAndCallTool` 里手搓的 `Stream` 汇合到同一条 async iterable。注释承认这是"a bit of a hack"，理想情况下进度与结果应该走两条通道（src/services/tools/toolExecution.ts:504-509）。执行前后各有一对埋点钩子：`startToolSpan`/`startToolBlockedOnUserSpan` 在权限询问前开启，裁定后结束 blocked span 并开启 execution span（src/services/tools/toolExecution.ts:909-914、1171-1176），"等用户"与"真执行"的耗时在 OTel 里是分开的两段，不会被权限弹窗的等待时间污染执行时长统计。

执行前还有一段围绕 `backfillObservableInput` 的输入整形（src/services/tools/toolExecution.ts:783-793、1189-1205）：hooks 与权限系统看到的输入是打过补丁的浅拷贝（例如文件工具把 `file_path` 展开成绝对路径），但真正传给 `call()` 的必须是模型发出的原始路径，因为工具结果字符串里嵌着这个路径，改动它会改变序列化后的转写、使 VCR fixture 哈希失配。代码用"backfill 克隆是否被 hook/权限替换"做分支判断，只在未被替换时把原始 `file_path` 恢复回去。这是可观测性与确定性之间的显式权衡。

第六步是 PostToolUse hooks 与 MCP 的输出改写。结果落消息的顺序对 MCP 工具与非 MCP 工具不同：非 MCP 工具先 `addToolResult` 再跑 PostToolUse hooks；MCP 工具反过来，因为 hook 可以返回 `updatedMCPToolOutput` 改写输出，必须等 hooks 跑完再落最终结果（src/services/tools/toolExecution.ts:1477-1542，src/services/tools/toolHooks.ts:146-151）。

第七步是错误分类与失败 hooks。catch 分支里，MCP 鉴权错误会把对应 client 状态置为 `needs-auth` 驱动 `/mcp` 界面提示重新授权（src/services/tools/toolExecution.ts:1601-1629）；遥测侧不用 `error.constructor.name`（minify 后变成无意义的三字符标识符），而是 `classifyToolError`：TelemetrySafeError 用预审过的 `telemetryMessage`，fs 错误用 errno（ENOENT/EACCES），已知错误类用构造器里显式设置的 `.name`（src/services/tools/toolExecution.ts:150-171）。随后跑 `runPostToolUseFailureHooks`（src/services/tools/toolExecution.ts:1700），用户中断（AbortError）以 `isInterrupt` 标记传入，失败信息同样以 `tool_result` 形式进入消息流，模型在下一轮生成时可以据此修正。

权限被拒绝的路径也有后续动作：auto 模式下被分类器否决时会执行 `executePermissionDeniedHooks`，若 hook 返回 `{retry: true}`，系统追加一条 meta 消息告知模型"该命令现已批准，可以重试"（src/services/tools/toolExecution.ts:1073-1101）。拒绝不再是一次性终态，而成为 hook 可参与的协商过程。

## toolHooks：胶水层的两条设计线

`toolHooks.ts` 本身不执行 hook（那在 `utils/hooks.ts`），它做两件事：把底层 hook 执行的原始产出翻译成上游 generator 能消费的判别联合类型，以及兜住所有异常。翻译上有一个具体的 bug 修正痕迹：JSON `{decision:"block"}` 型 hook 会同时产出 `blockingError` 和 `hook_blocking_error` 附件，直接转发会导致 block 原因在 UI 上显示两次，代码显式跳过附件路径只保留 blockingError 路径，并标注了 issue 编号 #31301（src/services/tools/toolHooks.ts:90-104）。

异常兜底分两层：单个 hook 产出处理出错时，记录 `tengu_pre_tool_hook_error` 并 yield 一条 `hook_error_during_execution` 附件，PreToolUse 场景下还会 yield `stop` 终止本次工具调用；整个 hook 循环本身抛错时只 log 不抛出（src/services/tools/toolHooks.ts:604-649、188-190）。hook 是用户配置的外部进程，它的失败不应 crash 主循环；PreToolUse 阶段遇到不确定性则宁可中止工具执行，取值方向与 `TOOL_DEFAULTS` 一致，fail-closed。

## 小结

这套架构里每个决策点都可追溯：注册是编译期 feature flag 加运行时 flag 的两级过滤；调度只认工具自报的 `isConcurrencySafe`，且所有不确定情况一律降级串行；单次调用被切成验证、hooks、权限、执行、hooks、归因六段，每段失败都产出结构化消息而不是抛出。生成器贯穿调度层，让进度、权限拒绝与结果共用一条流，UI 与遥测在同一条事件流上各取所需。

## 本篇涉及的源码文件

- `src/Tool.ts`：Tool 接口契约、ToolUseContext/ToolPermissionContext 类型与 buildTool 默认值
- `src/tools.ts`：工具注册表 getAllBaseTools、模式/deny/isEnabled 三级过滤与 assembleToolPool 工具池合成
- `src/services/tools/toolOrchestration.ts`：runTools 按 isConcurrencySafe 分区、并发批与串行批调度
- `src/services/tools/toolExecution.ts`：runToolUse 单次调用全生命周期：别名解析、验证、权限、执行、错误分类与 MCP 归因
- `src/services/tools/toolHooks.ts`：PreToolUse/PostToolUse/PostToolUseFailure hooks 的执行胶水与 resolveHookPermissionDecision 权限不变式
- `src/utils/generators.ts`：all() 生成器组合子，并发批的限流 race 循环
