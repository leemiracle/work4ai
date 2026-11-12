---
title: Claude Code 源码拆解 11：权限决策管线
date: "2026-04-09 22:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 11/20 篇 · 对应主题：安全护栏

# 权限决策管线：从工具调用到一次 allow/deny/ask

Claude Code 的每一次工具调用都要经过同一条决策管线，产出三值结果：`allow`、`deny`、`ask`。管线分两层：纯函数式的规则求值在 `src/utils/permissions/permissions.ts`，带 UI 副作用的分流在 `src/hooks/useCanUseTool.tsx`。本篇按数据流顺序拆解这条管线：入口封装、模式语义、规则语法、编号求值步骤、分类器层、拒绝追踪，以及三种运行形态下的 handler 分流。

## 入口：useCanUseTool 的 Promise 封装

`useCanUseTool` 是一个 React hook，返回 `CanUseToolFn`。它把决策包进一个 `new Promise(resolve => ...)`，先构造 `PermissionContext`，再调用核心求值函数（src/hooks/useCanUseTool.tsx:32-37）：

```typescript
const ctx = createPermissionContext(tool, input, toolUseContext, ...)
if (ctx.resolveIfAborted(resolve)) return
const decisionPromise = forceDecision !== undefined
  ? Promise.resolve(forceDecision)
  : hasPermissionsToUseTool(tool, input, toolUseContext, assistantMessage, toolUseID)
```

`forceDecision` 参数允许调用方注入一个预决定的结果，跳过整条管线，重放或测试场景用它。`resolveIfAborted` 在每个异步边界后被反复调用（useCanUseTool.tsx:40、61、110），保证用户按 Esc 后不会有"过期对话框"弹出。拿到结果后按 `result.behavior` 三路分流：`allow` 直接 `ctx.buildAllow` 放行（useCanUseTool.tsx:39-53）；`deny` 记录日志后原样返回（useCanUseTool.tsx:65-91）；`ask` 最复杂，要依次尝试 coordinator handler、swarm-worker handler、推测性分类器宽限，最后才落到交互对话框（useCanUseTool.tsx:93-168）。整条链的 `finally` 里固定调用 `clearClassifierChecking(toolUseID)` 清理分类器进行中的 UI 指示（useCanUseTool.tsx:180-182）。

## 四种 PermissionMode 的语义

模式定义在 `PERMISSION_MODE_CONFIG` 表中（src/utils/permissions/PermissionMode.ts:42-91）。四个对外模式：

- `default`：无符号无颜色，一切按规则与用户确认走。
- `acceptEdits`：`⏵⏵`、`autoAccept` 色。文件编辑类工具在各自 `checkPermissions` 里直接放行工作目录内的修改。
- `plan`：`PAUSE_ICON`、`planMode` 色。只读规划，写操作被拦。
- `bypassPermissions`：`⏵⏵`、`error` 色（红色），跳过模式层拦截。

表内还有两个隐藏模式：`dontAsk`（把所有 `ask` 改写成 `deny`，见 permissions.ts:505-517，注释说明这个改写故意放在管线末尾，"so it can't be bypassed by early returns"）和 ant-only 的 `auto`（`TRANSCRIPT_CLASSIFIER` feature gate 下才注入配置，PermissionMode.ts:80-90）。`isExternalPermissionMode` 显式把 `auto` 和 `bubble` 排除在对外模式之外（PermissionMode.ts:97-105），说明 auto mode 当前是内部实验功能，外部构建的 `EXTERNAL_PERMISSION_MODES` 枚举里根本没有它。

模式生效的位置在 `hasPermissionsToUseToolInner` 的步骤 2a（src/utils/permissions/permissions.ts:1268-1281）：

```typescript
const shouldBypassPermissions =
  appState.toolPermissionContext.mode === 'bypassPermissions' ||
  (appState.toolPermissionContext.mode === 'plan' &&
    appState.toolPermissionContext.isBypassPermissionsModeAvailable)
if (shouldBypassPermissions) {
  return { behavior: 'allow', ..., decisionReason: { type: 'mode', mode: ... } }
}
```

注意第二行：plan 模式下如果用户原本带 `--dangerously-skip-permissions` 启动（`isBypassPermissionsModeAvailable`），bypass 语义依然保留，plan 只是 UI 层提示，不会暗中收紧权限。另注意步骤 2a 前重新调用了一次 `context.getAppState()`（permissions.ts:1263-1264），注释 "IMPORTANT: Call getAppState() to get the latest value"，因为工具自己的 `checkPermissions` 是异步的，期间用户可能已切换模式。

## 规则语法与解析器

规则是字符串，格式 `Tool` 或 `Tool(content)`，例如 `Bash(npm install)`、`Bash(git:*)`。解析器 `permissionRuleValueFromString`（src/utils/permissions/permissionRuleParser.ts:93-133）的核心难点是括号转义：内容里允许 `\(` 和 `\)`，所以首尾括号必须用"前面反斜杠个数为偶数"来判定（permissionRuleParser.ts:158-198 的 `findFirstUnescapedChar` / `findLastUnescapedChar`）。解析失败有多个兜底：找不到配对右括号、右括号不在串尾、工具名为空，全部按整工具规则处理（permissionRuleParser.ts:104-122）。`Bash()` 和 `Bash(*)` 也被归一化为整工具规则（permissionRuleParser.ts:126-128）。工具改名由 `LEGACY_TOOL_NAME_ALIASES` 兜底，例如 `Task` → Agent 工具、`KillShell` → TaskStop（permissionRuleParser.ts:21-33），保证老配置文件里的规则继续生效。

规则按来源聚合：`getAllowRules` / `getDenyRules` / `getAskRules` 对 `PERMISSION_RULE_SOURCES` 做 flatMap，把每条字符串规则解析成带 `source` 与 `ruleBehavior` 的结构化对象（permissions.ts:122-131、213-231）。整工具匹配由 `toolMatchesRule` 完成，它只认无内容的规则：`Bash` 匹配 Bash 工具，`Bash(ls:*)` 不匹配（permissions.ts:238-245）；MCP 工具按完全限定名 `mcp__server__tool` 匹配。Agent 工具另有 `Agent(agentType)` 语法按子 agent 类型拒绝，`filterDeniedAgents` 一次性把 deny 规则解析进 Set 再过滤，注释里明确说这是对 O(agents×rules) 重复解析的性能修正（permissions.ts:325-343）。

shell 类工具的内容规则有三种形态，`parsePermissionRule` 给出判别（src/utils/permissions/shellRuleMatching.ts:159-184）：结尾 `:*` 是 legacy 前缀规则；含未转义 `*` 是通配符规则；其余是精确匹配。通配符匹配 `matchWildcardPattern`（shellRuleMatching.ts:90-154）先把 `\*`、`\\` 换成 null 字节哨兵占位，再把其余正则元字符转义、把 `*` 翻译成 `.*`，最后用带 `s`（dotAll）标志的全串正则测试。`s` 标志是为 heredoc 这类内嵌换行的命令准备的（shellRuleMatching.ts:147-151）。一个细节：当模式以空格加单个 `*` 结尾时（如 `git *`），尾部会被改写为 `( .*)?`，使 `git *` 同时匹配裸 `git`，与前缀规则 `git:*` 语义对齐；多通配符模式如 `* run *` 明确排除这个优待，否则会错误匹配 `npm run`（shellRuleMatching.ts:136-145）。

## 影子规则检测

规则集合可能自相矛盾：deny 先于 ask 先于 allow 求值，所以 `Bash` 进 deny 列表后，`Bash(ls:*)` 的 allow 规则永远不可达。`detectUnreachableRules` 扫描全部 allow 规则，先查 deny 遮蔽（更严重），再查 ask 遮蔽（src/utils/permissions/shadowedRuleDetection.ts:193-234）：

```typescript
const denyResult = isAllowRuleShadowedByDenyRule(allowRule, denyRules)
if (denyResult.shadowed) {
  unreachable.push({ rule: allowRule, shadowType: 'deny', ... })
  continue // Don't also report ask-shadowing if deny-shadowed
}
const askResult = isAllowRuleShadowedByAskRule(allowRule, askRules, options)
```

每条不可达规则附带 `reason` 与 `fix` 文案，fix 直接告诉用户删掉哪条规则（shadowedRuleDetection.ts:79-92）。ask 遮蔽有一个沙箱豁免：当 Bash 沙箱自动放行开启、且 ask 规则来自个人配置（userSettings/localSettings 等）时，具体 allow 规则不算被遮蔽，因为沙箱命令本就会自动放行；但共享配置（projectSettings、policySettings、command，见 `isSharedSettingSource`，shadowedRuleDetection.ts:61-67）一律告警，因为队友不一定开了沙箱（shadowedRuleDetection.ts:135-146）。

## hasPermissionsToUseToolInner：编号求值步骤

核心求值函数把规则层写成带编号的顺序步骤（src/utils/permissions/permissions.ts:1158-1319），每个编号都对应一个提前返回点：

1. 1a：整工具 deny 规则命中 → `deny`（permissions.ts:1171）
2. 1b：整工具 ask 规则命中 → `ask`，除非 Bash 沙箱自动放行生效。`canSandboxAutoAllow` 同时要求沙箱启用、`autoAllowBashIfSandboxed` 开启、该命令适合沙箱（permissions.ts:1184-1206）
3. 1c：调用工具自己的 `checkPermissions`（先过 `inputSchema.parse`），例如 Bash 的子命令级规则；解析或执行出错只记日志、按 passthrough 继续（permissions.ts:1210-1223）
4. 1d：工具实现返回 `deny` → 直接透传（permissions.ts:1226）
5. 1e：`tool.requiresUserInteraction()` 且结果为 `ask` → 强制询问，bypass 也不可跳过（permissions.ts:1231-1236）
6. 1f：内容级 ask 规则（如 `Bash(npm publish:*)`）优先于 bypassPermissions，注释把它与 1d 的 deny 并列："just as deny rules are respected at step 1d"（permissions.ts:1244-1250）
7. 1g：safetyCheck（`.git/`、`.claude/`、`.vscode/`、shell 配置等路径）bypass 免疫，必须弹窗（permissions.ts:1252-1260）
8. 2a：模式层 bypass（上文已引）
9. 2b：整工具 allow 规则 → `allow`（permissions.ts:1284-1297）
10. 3：工具返回 `passthrough` 兜底改写成 `ask`，消息由 `createPermissionRequestMessage` 生成（permissions.ts:1300-1310）

这个步骤顺序体现了安全策略的取舍：deny 永远最先，safetyCheck 与用户交互类工具不可被模式跳过，allow 规则排在模式之后。bypassPermissions 尊重的规则子集被单独抽成 `checkRuleBasedPermissions`（permissions.ts:1071-1156），复刻 1a-1g 中除 1e 外的步骤（注释说明 1e 的 `requiresUserInteraction` 需调用方自行预检），但不跑分类器、模式变换与 hooks，供需要在 bypass 下仍执行规则检查的调用方复用。

`createPermissionRequestMessage` 按 `decisionReason.type` 分派文案：classifier 引用分类器名与理由、hook 引用 hookName、rule 把规则值重新序列化并标注来源、mode 标注当前模式（permissions.ts:137-211）。`subcommandResults` 分支处理复合 Bash 命令，逐个列出需要批准的子命令，并在展示前剥离输出重定向，避免把重定向文件名当成命令显示（permissions.ts:165-182）。

外层 `hasPermissionsToUseTool` 在 inner 结果之上叠加模式变换（permissions.ts:473-956）：`allow` 时清零 auto mode 的连续拒绝计数，哪怕这次放行来自普通规则，也要打断连续拒绝 streak（permissions.ts:486-501）；`ask` 时依次应用 dontAsk 改写、auto mode 分类器、headless 兜底。

## 分类器层：推测性自动决策

规则层之上叠了两类分类器，分别由 feature gate 控制。

`bashClassifier`（`BASH_CLASSIFIER`）处理 `Bash(prompt: ...)` 形式的自然语言规则。外部构建里整个模块是桩（src/utils/permissions/bashClassifier.ts:1 注释 "classifier permissions feature is ANT-ONLY"），`classifyBashCommand` 直接返回 `matches: false`（bashClassifier.ts:40-53），`createPromptRuleContent` 只保留 `prompt: ` 前缀的拼串逻辑（bashClassifier.ts:20-22）。真正的调用点在 useCanUseTool 的 ask 分支：主 agent 弹出对话框前有一个 2 秒宽限期，`Promise.race` 等待推测性分类器结果（useCanUseTool.tsx:126-158，超时值在 useCanUseTool.tsx:193 的 `setTimeout(res, 2000, ...)`）。若宽限期内返回 `matches && confidence === 'high'`，则消费这次推测检查、跳过对话框直接放行，decisionReason 记为 `classifier: 'bash_allow'`，理由文本引用命中的规则描述（useCanUseTool.tsx:135-156）。超时或不匹配则照常弹窗。

`yoloClassifier` / `transcriptClassifier`（`TRANSCRIPT_CLASSIFIER`）是 auto mode 的分类决策来源。`classifyYoloAction` 把整段会话压缩成 transcript entries，连同当前动作一起发给一个分类模型（src/utils/permissions/yoloClassifier.ts:1012-1066）。入口先调工具的 `toAutoClassifierInput` 把输入压成安全相关摘要，返回空串意味着"该工具声明无分类器相关输入"，直接放行且避免空 action 块触发 API 400（yoloClassifier.ts:1019-1029）。分类器支持两阶段模式：stage 1 快速判定，放行即返回（fast path，yoloClassifier.ts:806）；存疑则升级到带思维链的 stage 2 以降低误报，两个阶段也可以独立启用（'fast' 只用 stage 1、'thinking' 只用 stage 2，yoloClassifier.ts:700-710 的注释）。两阶段共享同一系统提示与前缀，action 块上放 `cache_control` 断点，保证 stage 2 命中整段前缀缓存；预算注释写明 system + CLAUDE.md + action 共 2-3 个断点，低于 API 的 4 个上限（yoloClassifier.ts:1094-1106）。

在跑 yolo 分类器之前有两条省钱快路径。第一条用 acceptEdits 模式试算一次 `checkPermissions`，能放行就不调 API；Agent 和 REPL 工具被显式排除，注释给出的理由是 REPL 的胶水 JavaScript 里可能藏着 inner tool call 之间的 VM 逃逸，分类器必须拿到完整代码（permissions.ts:600-604）。第二条查安全工具白名单 `SAFE_YOLO_ALLOWLISTED_TOOLS`：Read、Grep、Glob、TodoWrite、Task 系列、Sleep 等只读或纯元数据工具直接放行（src/utils/permissions/classifierDecision.ts:56-98，调用点 permissions.ts:660-686）；swarm 协调工具（TeamCreate、SendMessage）也在列，注释说明队友自己有独立权限检查，白名单不构成实际绕过（classifierDecision.ts:78-83）。

auto 模式还有两个硬性守卫。`decisionReason.type === 'safetyCheck'` 且不可被分类器批准的决策对所有自动放行路径免疫，包括快路径与分类器本身（permissions.ts:526-548）；PowerShell 工具在未开 `POWERSHELL_AUTO_MODE` 构建开关时完全不进分类器，注释说明配套的 permissionSetup 会剥离 `PowerShell(*)` 过宽规则与 `iex`/`pwsh`/`Start-Process` 前缀规则（permissions.ts:560-591）。

分类器的失败语义是显式可配置的：API 不可用（`unavailable`）时查 `tengu_iron_gate_closed` gate，true 则 fail-closed 拒绝并附重试指引，false 则 fail-open 回落到正常弹窗（permissions.ts:845-876）。transcript 超长属于不可恢复错误，headless 下直接抛 `AbortError`，注释解释 deny-retry-deny 只会浪费 token 且永远到不了拒绝上限；交互模式回落人工审批（permissions.ts:822-842）。

危险前缀模式在分类器之外做静态过滤。`Bash(python:*)` 这类 allow 规则等于允许任意代码执行，会绕过 auto mode 分类器，所以 `DANGEROUS_BASH_PATTERNS` 列出了解释器（python/node/deno/ruby/perl/php/lua）、包运行器（npx/bunx/npm run 等）、shell（bash/sh/zsh/fish）、`eval`/`exec`/`sudo`/`xargs` 等前缀（src/utils/permissions/dangerousPatterns.ts:18-52），由 permissionSetup.ts 在进入 auto mode 时剥离。跨平台子集 `CROSS_PLATFORM_CODE_EXEC` 单独抽出，注释说明是为防止 Unix 与 Windows 两份清单漂移（dangerousPatterns.ts:14-17）。ant 用户还有一份基于内部沙箱 dotfile 数据的经验清单：curl、wget、gh、git、kubectl、aws 等，注释坦承这是"empirical-risk call"而非普适判断（dangerousPatterns.ts:58-79）。

## denialTracking 与 autoModeState

分类器拒绝不是无限进行的。`denialTracking.ts` 维护 `{consecutiveDenials, totalDenials}` 两个计数，上限硬编码为连续 3 次、累计 20 次（src/utils/permissions/denialTracking.ts:12-15）。`recordSuccess` 只清连续计数且在无变化时返回原引用，配合 `persistDenialState` 里 `prev.denialTracking === newState` 的 `Object.is` 短路，避免无变化的 store 通知（permissions.ts:963-978）。触限后 `handleDenialLimitExceeded` 把决策降级为 `ask` 让用户复核，累计上限触发时顺手把两个计数清零重新开始；headless 下直接 abort（permissions.ts:984-1040）。异步子 agent 的 `setAppState` 是 no-op，所以它们用 `context.localDenialTracking` 原地 `Object.assign` 保存计数（permissions.ts:555-558、967-968）。分类器 deny 时还会向用户推送 `auto-mode-denied` 通知，提示可在 `/permissions` 查看（useCanUseTool.tsx:77-89）。

`autoModeState.ts` 是三个模块级布尔位：`autoModeActive`（当前是否激活）、`autoModeFlagCli`（CLI 显式传入）、`autoModeCircuitBroken`（GrowthBook 把 `tengu_auto_mode_config.enabled` 翻成 disabled 后熔断，阻止 SDK 重新进入）（src/utils/permissions/autoModeState.ts:4-33）。plan 模式下若 `isAutoModeActive()` 为真，ask 决策也会走分类器（permissions.ts:520-525），这是 plan 与 auto 两个模式的交点。

## 三种 permission handler 分流

`ask` 决策最终去向由运行形态决定，三个 handler 按序尝试（useCanUseTool.tsx:95-168）。

`coordinatorHandler`：`awaitAutomatedChecksBeforeDialog` 为真时启用。先顺序 await 权限 hooks（快、本地），再 await 分类器（慢、推理），任一命中即返回；两者都未决则返回 null 落回对话框，注释强调此时"hooks already ran, classifier already consumed"，不会重复执行（src/hooks/toolPermission/handlers/coordinatorHandler.ts:26-62）。自动化检查抛错也只记日志并落回对话框，不让后台 worker 因检查失败而卡死（coordinatorHandler.ts:47-57）。

`swarmWorkerHandler`：swarm worker 先尝试分类器自动批准（与主 agent 的 race 不同，worker 是 await 结果），失败后把权限请求通过 mailbox 转发给 leader（src/hooks/toolPermission/handlers/swarmWorkerHandler.ts:52-57、122-123）。回调在发送请求之前注册，避免 leader 响应早于回调注册的竞态（swarmWorkerHandler.ts:79-81）；等待期间设置 `pendingWorkerRequest` 指示，abort 信号触发时 resolve 一个取消决策防止悬挂（swarmWorkerHandler.ts:126-146）。

`interactiveHandler`：主 agent 的默认路径。它不返回 Promise，而是把 `ToolUseConfirm` 推入 UI 队列并挂一组回调（src/hooks/toolPermission/handlers/interactiveHandler.ts:57-108）。`createResolveOnce` 的 `claim()` 做原子占位，保证用户点击、hooks、分类器、bridge/channel 远程响应多条路径里只有一条能 resolve（interactiveHandler.ts:70、154-203）。`onUserInteraction` 带 200ms 宽限期：对话框弹出后的头 200ms 内忽略按键，防止误触提前取消正在进行的分类器自动批准（interactiveHandler.ts:113-121）。bridge（`BRIDGE_MODE`）与 channel（`KAIROS`）回调允许从手机等远程端审批，本地任一路径胜出后通过 `channelUnsubscribe` 注销远程监听（interactiveHandler.ts:76-81、162-170）。

headless 场景不走这三个 handler：`shouldAvoidPermissionPrompts` 为真时，外层函数先跑 `runPermissionRequestHooksForHeadlessAgent`：hook 返回 allow 时落盘 `updatedPermissions` 并更新 appState，deny 且带 `interrupt` 时直接 abort 整个 agent；hook 抛错只记日志并落到自动 deny，注释说明这是"fall through to auto-deny rather than crashing"（permissions.ts:400-470、932-952）。

## 小结

这条管线的设计要点有四条：deny 优先于一切；模式只放宽不收紧（plan 不覆盖 bypass）；分类器是决策来源而不是绕过通道，所有分类器放行都带 `decisionReason` 审计标记；每条自动化路径都有回落，分类器超时回落对话框、分类器不可用按 gate 决定 fail-open/closed、拒绝触限回落人工、handler 失败落回本地 UI。这些提前返回点的排列顺序决定了 deny、模式、分类器、allow 的相对优先级，调整顺序就会改变哪些检查可以被跳过。

## 本篇涉及的源码文件

- `src/hooks/useCanUseTool.tsx`：权限决策的 React 入口，按 allow/deny/ask 分流到各 handler
- `src/utils/permissions/permissions.ts`：核心求值函数 hasPermissionsToUseTool(Inner)，编号步骤与模式变换
- `src/utils/permissions/PermissionMode.ts`：六种权限模式的 UI 配置与对外模式过滤
- `src/utils/permissions/PermissionRule.ts`：规则行为（allow/deny/ask）与规则值的 zod schema
- `src/utils/permissions/permissionRuleParser.ts`：`Tool(content)` 规则字符串的解析、转义与旧工具名别名
- `src/utils/permissions/shellRuleMatching.ts`：shell 规则的精确/前缀/通配符三态匹配
- `src/utils/permissions/bashClassifier.ts`：Bash 自然语言规则分类器（外部构建为 ANT-ONLY 桩）
- `src/utils/permissions/classifierDecision.ts`：auto mode 安全工具白名单
- `src/utils/permissions/dangerousPatterns.ts`：危险 allow 前缀清单，进 auto mode 时剥离
- `src/utils/permissions/shadowedRuleDetection.ts`：不可达规则（deny/ask 遮蔽 allow）检测
- `src/utils/permissions/denialTracking.ts`：分类器拒绝计数与回落阈值
- `src/utils/permissions/autoModeState.ts`：auto mode 激活/熔断的模块级状态
- `src/utils/permissions/yoloClassifier.ts`：transcript 分类器，两阶段判定与缓存断点
- `src/utils/permissions/PermissionResult.ts`：决策类型的再导出与行为文案
- `src/hooks/toolPermission/handlers/coordinatorHandler.ts`：后台 worker 的 hooks→分类器顺序求值
- `src/hooks/toolPermission/handlers/interactiveHandler.ts`：交互对话框与多路 resolve 竞态保护
- `src/hooks/toolPermission/handlers/swarmWorkerHandler.ts`：swarm worker 经 mailbox 转发权限请求给 leader
