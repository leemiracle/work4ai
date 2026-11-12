---
title: Claude Code 源码拆解 16：Hooks 引擎——5022 行的用户扩展点
date: "2026-04-11 20:30"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 16/20 篇 · 对应主题：扩展面

# Hooks 引擎：5022 行的用户扩展点

`src/utils/hooks.ts` 单文件 5022 行，是 Claude Code 暴露给用户的全部扩展点：shell 命令、LLM 判断、HTTP 回调、SDK 回调、函数钩子五种形态，挂在 27 个生命周期事件上。本篇按"事件目录 → 匹配 → 执行 → 结果回流主循环"的顺序拆解这条管线，以及配套的安全边界（trust 检查、SSRF 防护、配置快照）。

## 事件目录与配置 Schema

全部生命周期事件枚举定义在 `HOOK_EVENTS` 常量中（src/entrypoints/sdk/coreSchemas.ts:355-383），共 27 个：`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`Notification`、`UserPromptSubmit`、`SessionStart`、`SessionEnd`、`Stop`、`StopFailure`、`SubagentStart`、`SubagentStop`、`PreCompact`、`PostCompact`、`PermissionRequest`、`PermissionDenied`、`Setup`、`TeammateIdle`、`TaskCreated`、`TaskCompleted`、`Elicitation`、`ElicitationResult`、`ConfigChange`、`WorktreeCreate`、`WorktreeRemove`、`InstructionsLoaded`、`CwdChanged`、`FileChanged`。settings.json 中的 `hooks` 字段是 `{事件名: [{matcher, hooks: [...]}]}` 的 partialRecord（src/schemas/hooks.ts:211-213）。

钩子本身是一个以 `type` 为判别字段的 union：`command`（shell 命令）、`prompt`（单次 LLM 判断）、`agent`（多轮 agent 验证）、`http`（POST 回调），四种可持久化形态由 `HookCommandSchema` 聚合（src/schemas/hooks.ts:176-189）。运行期还存在第五种 `callback`/`function`（SDK 注册与内部钩子），不进 settings 文件。`command` 类型的 schema 直接暴露了执行模型的全部参数（src/schemas/hooks.ts:32-65）：`shell` 选 bash 或 powershell、`timeout` 秒级超时、`once` 执行一次后移除、`async` 后台执行、`asyncRewake` 后台执行且退出码 2 时唤醒模型。

## 配置快照与热更新

引擎不直接读 settings，而是读快照。`getHooksConfig` 从 `getHooksConfigFromSnapshot()` 取 settings 钩子，再合并 SDK 注册的钩子和当前 session 的派生钩子（agent/skill frontmatter 注册的 `SessionDerivedHookMatcher` 与函数钩子）（src/utils/hooks.ts:1492-1566）。快照逻辑在 `hooksConfigSnapshot.ts`：启动时 `captureHooksConfigSnapshot()` 固化一份（src/utils/hooks/hooksConfigSnapshot.ts:95-97），策略检查也在这一层完成：`policySettings.disableAllHooks` 为真则返回空表，`allowManagedHooksOnly` 为真则只保留 managed settings 的钩子；非 managed 来源设置 `disableAllHooks` 只能禁用非 managed 钩子，managed 钩子仍然执行（src/utils/hooks/hooksConfigSnapshot.ts:18-53）。

热更新走 `updateHooksConfigSnapshot()`：先 `resetSettingsCache()` 强制从磁盘重读，再重建快照（src/utils/hooks/hooksConfigSnapshot.ts:104-112）。注释说明了原因：用户外部编辑 settings.json 后立刻跑 `/hooks`，文件 watcher 的稳定性阈值可能还没到，session 缓存未失效，不重置就会拿到旧配置。`shouldAllowManagedHooksOnly()` 在合并阶段还有一次执行期过滤：`getHooksConfig` 遍历时跳过带 `pluginRoot` 的注册钩子与全部 session 钩子，保证企业策略下插件与 agent frontmatter 注入的钩子不会绕过 managed-only 限制（src/utils/hooks.ts:1516-1541）。

## 匹配：matcher 与 if 条件

每个事件有一个 `matchQuery`：`PreToolUse`/`PostToolUse` 等用 `tool_name`，`SessionStart` 用 `source`，`PreCompact` 用 `trigger`，`FileChanged` 用 `basename(file_path)`，等等（src/utils/hooks.ts:1616-1670）。`matchesPattern` 对 matcher 做三级解释：空或 `*` 全匹配；纯字母数字加 `|` 视为精确名列表（如 `Write|Edit`）；其余按正则处理，并额外对 legacy 工具名做一次匹配保证 `^Task$` 这类旧模式不破（src/utils/hooks.ts:1346-1381）。

`if` 字段是 matcher 之后的第二级过滤，直接复用权限规则语法。schema 注释写明格式为 `"Bash(git *)"`、`"Read(*.ts)"`（src/schemas/hooks.ts:19-27）。求值分两步：`prepareIfConditionMatcher` 在批量执行前把开销大的部分提前做掉，用工具自身的 inputSchema 校验 `tool_input`，再调用工具的 `preparePermissionMatcher` 得到模式匹配闭包；返回的闭包对每个钩子的 `if` 字符串做轻量判定（src/utils/hooks.ts:1390-1421）：

```typescript
return ifCondition => {
  const parsed = permissionRuleValueFromString(ifCondition)
  if (normalizeLegacyToolName(parsed.toolName) !== toolName) {
    return false
  }
  if (!parsed.ruleContent) {
    return true
  }
  return patternMatcher ? patternMatcher(parsed.ruleContent) : false
}
```

工具名不匹配直接 false；没有规则内容（裸工具名）直接 true；有规则内容则交给该工具的权限匹配器。这意味着 `if: "Bash(git *)"` 的 glob 语义与 settings 里 `allow: ["Bash(git *)"]` 完全同源，只对 `PreToolUse`/`PostToolUse`/`PostToolUseFailure`/`PermissionRequest` 四个事件生效，其余事件不构造匹配器（src/utils/hooks.ts:1394-1401）。

匹配结果还按来源去重：key 为 `pluginRoot/skillRoot + shell + command + if条件`，settings 钩子共享空前缀使同一命令在多级配置中只执行一次，而两个插件共享 `${CLAUDE_PLUGIN_ROOT}/hook.sh` 模板不会互相吞掉（src/utils/hooks.ts:1453-1455, 1735-1795）。去重按类型分桶进行：command、prompt、agent、http 各建一个 Map，callback 与 function 钩子天然唯一不参与去重；全 callback/function 批次直接短路返回，省去 4 个 Map 的构建开销（src/utils/hooks.ts:1723-1729）。

每个事件的可匹配字段与退出码语义并不统一，这份差异集中定义在 `hooksConfigManager.ts` 的 `getHookEventMetadata` 里（src/utils/hooks/hooksConfigManager.ts:26-267）。例如 `PreToolUse` 的退出码 2 会阻断工具调用并把 stderr 发给模型，`UserPromptSubmit` 的退出码 2 会丢弃原始输入只把 stderr 给用户看，`Stop` 的退出码 2 则把 stderr 发给模型并让它继续对话；`StopFailure` 是 fire-and-forget，输出与退出码全部被忽略；`InstructionsLoaded` 明确标注为仅观测、不支持阻断。`SessionEnd` 有专门的超时常数 `SESSION_END_HOOK_TIMEOUT_MS_DEFAULT = 1500` 毫秒，因为它在进程退出路径上执行，不能沿用工具钩子 10 分钟的默认值，可用环境变量 `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` 覆盖（src/utils/hooks.ts:168-182）。

## 执行管线：executeHooks

`executeHooks` 是所有事件的公共生成器（src/utils/hooks.ts:1952）。入口三道短路：managed 层 `disableAllHooks` 直接返回；`CLAUDE_CODE_SIMPLE` 环境变量为真时整个钩子系统关闭；trust 检查，交互模式下未接受 workspace trust 对话框则全部钩子跳过，注释明确标注这是防 RCE 的集中检查点（src/utils/hooks.ts:1978-1999, 286-296）。之后对每个匹配的钩子并行启动，各自带 `createCombinedAbortSignal` 叠加的超时（默认 `TOOL_HOOK_EXECUTION_TIMEOUT_MS = 10 分钟`，src/utils/hooks.ts:166），按 `type` 分派到 `execCommandHook`、`execPromptHook`、`execAgentHook`、`execHttpHook` 或 callback/function 路径（src/utils/hooks.ts:2143-2462）。`hookInput` 的 JSON 序列化是惰性一次性的，同批钩子共享一份字符串，纯 callback 批次则完全不需要付出 stringify 成本（src/utils/hooks.ts:2121-2140）。全内部 callback 批次另有快速路径，跳过 span/progress 直接逐个 await，单次 PostToolUse 命中从 6µs 降到 1.8µs（src/utils/hooks.ts:2036-2067）。

## command 钩子：shell、PowerShell 与 env 文件

执行前还有一层可见性处理：对每个匹配的钩子先 yield 一条 `hook_progress` 进度消息（含 `getHookDisplayText` 生成的展示文本与可选的 `statusMessage`），UI 据此渲染 spinner；beta tracing 开启时整批钩子还会包在一个 span 里并上报 OTel 事件（src/utils/hooks.ts:2094-2116, 2070-2092）。

`execCommandHook` 是管线的重心（src/utils/hooks.ts:747）。两条 spawn 路径完全分离：bash 走 `spawn(command, [], { shell: <gitBashPath | true> })`，整串交给 shell 解析；PowerShell 走 `spawn(pwshPath, ['-NoProfile', '-NonInteractive', '-Command', cmd])`，显式 argv，跳过用户 profile（src/utils/hooks.ts:957-984）。Windows bash 下所有注入 env 的路径都要经 `windowsPathToPosixPath` 转成 `/c/...` 形式，因为 Git Bash 无法解析 Windows 路径（src/utils/hooks.ts:794-811）。

环境变量注入包含 `CLAUDE_PROJECT_DIR`（稳定项目根，不随 worktree 切换）、`CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA` 与命令串里的 `${CLAUDE_PLUGIN_ROOT}` 模板替换，以及插件选项的 `CLAUDE_PLUGIN_OPTION_*` 大写导出（src/utils/hooks.ts:882-906）。env 文件机制仅对 bash 的 `SessionStart`/`Setup`/`CwdChanged`/`FileChanged` 四个事件开放：

```typescript
if (
  !isPowerShell &&
  (hookEvent === 'SessionStart' ||
    hookEvent === 'Setup' ||
    hookEvent === 'CwdChanged' ||
    hookEvent === 'FileChanged') &&
  hookIndex !== undefined
) {
  envVars.CLAUDE_ENV_FILE = await getHookEnvFilePath(hookEvent, hookIndex)
}
```

钩子往 `CLAUDE_ENV_FILE` 指向的 .sh 文件写 export，后续 BashTool 命令启动时注入这些内容（src/utils/hooks.ts:911-926）。PowerShell 被排除，因为它写的 `$env:FOO = 'bar'` 语法 bash 无法解析。

输入协议是 stdin 单行 JSON（`jsonStringify(hookInput)`）。所有事件的输入共享一个基座：`createBaseHookInput` 注入 `session_id`、`transcript_path`、`cwd`、`permission_mode`，子 agent 场景额外带 `agent_id` 与 `agent_type`，后者优先取 toolUseContext 里的子 agent 类型，让钩子能区分主线程调用与 `--agent` 会话里的子 agent 调用（src/utils/hooks.ts:301-328）。输出协议分两档：退出码语义与 stdout JSON。退出码 0 成功；退出码 2 是 blocking，stderr 作为反馈发给模型（src/utils/hooks.ts:2647-2668）；其他非零码是 non_blocking_error 只展示给用户。stdout 若以 `{` 开头则按 `hookJSONOutputSchema` 校验，`decision: "block"` 或 `hookSpecificOutput.permissionDecision: "deny"` 等价于 block，`continue: false` 设置 `preventContinuation`（src/utils/hooks.ts:518-541）。`hookSpecificOutput` 按事件分流：`PreToolUse` 可返回 `updatedInput` 改写工具入参，`PostToolUse` 可返回 `updatedMCPToolOutput` 改写 MCP 工具结果，`SessionStart` 可返回 `additionalContext`、`initialUserMessage` 与 `watchPaths`（注册文件监视），`UserPromptSubmit` 可注入 `additionalContext` 追加进用户输入（src/utils/hooks.ts:592-649）。校验失败时错误信息里直接附期望 schema 提示（src/utils/hooks.ts:416-444）。`async: true` 的钩子在写完 stdin 后转入 `executeInBackground` 由 AsyncHookRegistry 托管，`asyncRewake` 在退出码 2 时重新唤醒模型（src/utils/hooks.ts:995-1030）。

command 钩子与主进程之间还有一条反向通道：当调用方传入 `requestPrompt` 回调时，执行器会按行扫描钩子 stdout，符合 `promptRequestSchema` 的行被识别为钩子向用户发起的提问请求，应答通过 `promptChain` 串行化后写回钩子 stdin，已处理的行在最终输出中按内容剔除（src/utils/hooks.ts:1060-1105）。这让一个长驻的 shell 钩子可以在执行中途向用户索要输入而不必退出。

## prompt、agent、http 三类钩子

prompt hook 是单次 LLM 调用。`$ARGUMENTS` 占位符替换为钩子输入 JSON，拼上对话历史后用 `getSmallFastModel()`（默认小快模型）发 `queryModelWithoutStreaming`，通过 `outputFormat: json_schema` 强制返回 `{ok: boolean, reason?: string}`（src/utils/hooks/execPromptHook.ts:62-99）。`ok: false` 转为 blocking 结果，`reason` 作为 `stopReason`（src/utils/hooks/execPromptHook.ts:154-167）。注意它直接构造 user message 而不走 `processUserInput`，否则会递归触发 `UserPromptSubmit` 钩子（src/utils/hooks/execPromptHook.ts:40-42）。

agent hook 是完整的多轮子查询。它调用主循环同款 `query()`，系统提示告诉验证 agent 转录文件路径、允许它读代码库自查，工具集过滤掉 `ALL_AGENT_DISALLOWED_TOOLS`（防止 hook agent 再派生子 agent 或进入 plan 模式）并追加一个 StructuredOutput 工具作为返回通道，同时注册 session 级 stop hook 强制结构化输出（src/utils/hooks/execAgentHook.ts:100-160）。上限 50 轮，拿到 `{ok, reason}` 即中止（src/utils/hooks/execAgentHook.ts:119, 197-227）。权限上它构造了一个改写过的 `getAppState`：模式强制为 `dontAsk`，并向 session 级 alwaysAllow 规则追加 `Read(/<transcriptPath>)`，保证验证 agent 读转录不触发权限弹窗（src/utils/hooks/execAgentHook.ts:137-153）。默认超时 60 秒，超时与父 abort 信号通过 `createCombinedAbortSignal` 汇合后再驱动钩子自己的 AbortController（src/utils/hooks/execAgentHook.ts:74-85）。查询循环正常结束后调用 `clearSessionHooks` 清掉注册的结构化输出强制钩子，避免泄漏到后续轮次（src/utils/hooks/execAgentHook.ts:233）。典型用途写在 AgentHookSchema 的 prompt 字段描述里："Verify that unit tests ran and passed"（src/schemas/hooks.ts:141）。

http hook 把输入 JSON POST 到配置的 URL。三层防护依次生效：先做 `allowedHttpHookUrls` 通配符 allowlist 检查，不匹配直接拒绝（src/utils/hooks/execHttpHook.ts:137-145）；header 值里的 `$VAR`/`${VAR}` 只对 `allowedEnvVars` 白名单内的变量插值，且与全局 `httpHookAllowedEnvVars` 策略取交集，插值后剥掉 CR/LF/NUL 防 header 注入（src/utils/hooks/execHttpHook.ts:89-108, 161-172）；最后 axios 请求挂 `ssrfGuardedLookup` 做 DNS 层 SSRF 防护，`maxRedirects: 0` 禁止重定向绕过（src/utils/hooks/execHttpHook.ts:201-217）。sandbox 开启时改走 sandbox 网络代理，由代理执行域名白名单。

三类钩子的失败语义可以对照着看：prompt hook 的模型输出不符合 JSON schema 时降级为 non_blocking_error（src/utils/hooks/execPromptHook.ts:113-151）；agent hook 跑满 50 轮或没调用 StructuredOutput 工具时返回 `cancelled` 且不向用户展示错误，只上报 `tengu_agent_stop_hook_max_turns` 遥测（src/utils/hooks/execAgentHook.ts:236-268）；http hook 的非 2xx 响应由调用方按 body 解析，`parseHttpHookOutput` 把空 body 当作空 JSON 对象、非 JSON body 直接判为校验错误（src/utils/hooks.ts:453-487）。同一种"失败"，在三个执行器里分别是静默取消、降级报错、协议错误，颗粒度与各自的使用场景匹配。

## ssrfGuard：DNS 解析即拦截

`ssrfGuardedLookup` 是 axios `lookup` 选项的兼容实现：校验发生在 DNS 解析函数内部，socket 连接的就是被验证过的 IP，消除"先校验后解析"的 DNS rebinding 窗口（src/utils/hooks/ssrfGuard.ts:206-216）。IP 字面量直接校验；域名解析到全部地址后逐个检查，任何一个落在封锁段即整体拒绝：

```typescript
for (const { address } of addresses) {
  if (isBlockedAddress(address)) {
    callback(ssrfError(hostname, address), '')
    return
  }
}
```

封锁清单：IPv4 的 0.0.0.0/8、10/8、169.254/16（云元数据）、172.16/12、192.168/16、100.64/10（CGNAT，阿里云元数据 100.100.100.200 在此段）；IPv6 的 `::`、fc00::/7、fe80::/10，以及 IPv4-mapped IPv6，`::ffff:a9fe:a9fe` 这种十六进制写法会先展开提取内嵌 v4 再走 v4 判定，防止绕过（src/utils/hooks/ssrfGuard.ts:55-125, 187-204）。loopback（127/8、::1）显式放行，因为本地开发策略服务器是 http hook 的主要场景。走代理时 guard 跳过，DNS 由代理解析，在本地校验解析结果反而会误杀内网代理（src/utils/hooks/execHttpHook.ts:211-216）。

## Stop 钩子与主循环的 block-continue 决策

Stop 事件是钩子改变主循环行为的入口。`executeStopHooks` 构造 `StopHookInput` 时除了 `stop_hook_active` 防循环标记，还会提取最后一条 assistant 消息的纯文本放进 `last_assistant_message` 字段，让钩子不必读转录文件就能检查最终回复；有 `subagentId` 时同一函数改发 `SubagentStop` 事件并附加 `agent_transcript_path`（src/utils/hooks.ts:3653-3685）。`handleStopHooks` 消费结果流：blockingError 被包装成 `isMeta` user message 收集起来，`preventContinuation` 单独置位（src/query/stopHooks.ts:257-280）。UI 层面，只要至少跑了一个钩子就生成一条汇总系统消息，列出每个钩子的命令、耗时与错误；存在错误时再通过 `addNotification` 提示按 ctrl+o 查看详情（src/query/stopHooks.ts:297-323）。主循环拿到 `StopHookResult` 后分两种走法（src/query.ts:1278-1306）：

```typescript
if (stopHookResult.preventContinuation) {
  return { reason: 'stop_hook_prevented' }
}

if (stopHookResult.blockingErrors.length > 0) {
  const next: State = {
    messages: [
      ...messagesForQuery,
      ...assistantMessages,
      ...stopHookResult.blockingErrors,
    ],
    ...
    stopHookActive: true,
    transition: { reason: 'stop_hook_blocking' },
  }
  state = next
  continue
}
```

`preventContinuation`（来自 JSON 的 `continue: false`）直接终结 turn；blockingErrors（退出码 2 或 `decision: "block"`）则把错误文本作为新消息拼回上下文，置 `stopHookActive: true` 后 `continue` 进入下一轮 query，这就是"Stop 钩子让 Claude 继续干活"的机制。`stopHookActive` 传入下一轮的 hook input，用户脚本可据此决定何时停止再阻塞，防止无限循环。query.ts 附近还有一处针对 prompt-too-long 的护栏注释：`hasAttemptedReactiveCompact` 必须保留，否则 compact 失败后 stop hook 阻塞会触发 compact→block→compact 的死循环（src/query.ts:1292-1297）。teammate 场景下 Stop 通过后还会接着跑 TaskCompleted 与 TeammateIdle 钩子（src/query/stopHooks.ts:335-453）。

`handleStopHooks` 还承担了 turn 结束时的后台簿记：保存 fork 用的 cache-safe 参数、触发 prompt suggestion、记忆抽取与 auto-dream，全部 fire-and-forget，`--bare` 模式下整体跳过（src/query/stopHooks.ts:92-157）。另一条分支是 API 错误收尾：主循环在调用 `handleStopHooks` 之前先检查最后一条消息是否为 API 错误，是则改跑 `executeStopFailureHooks` 并直接结束。注释说明原因：让钩子去评估一条错误响应会产生 error→阻塞→重试→error 的死亡螺旋（src/query.ts:1260-1265）。执行中途用户按 Esc 时，abort signal 触发后循环立即 yield 打断消息并返回 `preventContinuation: true`，保证取消路径不被钩子结果覆盖（src/query/stopHooks.ts:282-294）。

## 结语

5022 行里真正的执行逻辑只占一半，另一半是边界处理：Windows 路径转换、插件模板替换、去重命名空间、trust 闸门、SSRF 段表、快照策略。设计上有两条主线。一是协议分层：stdin JSON 输入、退出码与 stdout JSON 双通道输出，让 shell 脚本和结构化程序都能挂在同一事件上。二是决策归一：无论钩子返回 blockingError 还是 preventContinuation，最终都收敛为 `AggregatedHookResult` 上的统一字段，由主循环单点消费。五种钩子形态对应五档接入成本：callback 是进程内函数调用，command 是一次 spawn，prompt 是一次模型调用，http 是一次跨网络往返，agent 是一个完整的子查询循环。接入成本递增的同时，钩子能造成的破坏面也在递增，安全机制（trust、allowlist、SSRF 段表、managed 策略）正是按这条梯度逐层加上去的。

## 本篇涉及的源码文件

- `src/utils/hooks.ts`：Hooks 引擎主体：匹配、去重、并行执行、command 钩子 spawn 与输出协议
- `src/schemas/hooks.ts`：四种可持久化钩子的 Zod schema 与 `if` 条件定义
- `src/entrypoints/sdk/coreSchemas.ts`：`HOOK_EVENTS` 27 个生命周期事件枚举
- `src/utils/hooks/execAgentHook.ts`：agent 钩子：多轮 query + StructuredOutput 工具的 LLM 验证器
- `src/utils/hooks/execHttpHook.ts`：http 钩子：URL 白名单、env 插值、header 净化与代理路由
- `src/utils/hooks/execPromptHook.ts`：prompt 钩子：单次 LLM 调用返回 `{ok, reason}`
- `src/utils/hooks/ssrfGuard.ts`：HTTP 钩子的 DNS 层 SSRF 防护与私网段封锁表
- `src/utils/hooks/hooksConfigManager.ts`：各事件的 matcher 元数据与 UI 分组（/hooks 菜单数据源）
- `src/utils/hooks/hooksConfigSnapshot.ts`：配置快照、managed 策略闸门与热更新
- `src/query/stopHooks.ts`：Stop/TeammateIdle/TaskCompleted 钩子在主循环的消费与 block-continue 决策
- `src/query.ts`：主循环：根据 StopHookResult 决定结束 turn 或携带阻塞反馈继续
