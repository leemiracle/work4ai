---
title: Claude Code 源码拆解 15：Subagent 与多 Agent 体系
date: "2026-04-11 16:30"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 15/20 篇 · 对应主题：多 Agent 协作的账

# Subagent 与多 Agent 体系

Claude Code 的多 Agent 能力不是单一机制，而是三层叠起来的体系：底层是 AgentTool/runAgent 提供的「隔离上下文的子代理循环」；中层是 spawnMultiAgent 与 swarm 提供的「可寻址、可持久、有终端形态的 teammate」；顶层是 coordinatorMode 把主 Agent 降级为「只能用编排工具的调度者」。本篇按这三层拆解，最后回到上下文隔离与共享这笔账。

## AgentTool：一个入口，四条路由

AgentTool（1397 行）是对模型暴露的统一入口，输入 schema 由基础字段（description、prompt、subagent_type、model、run_in_background）与多 Agent 字段（name、team_name、mode、isolation、cwd）合并而成，后者通过 `.omit()` 按 feature gate 动态裁剪，不把不可用参数暴露给模型（src/tools/AgentTool/AgentTool.tsx:110-125）。

`call()` 内部先做路由分发，四条路径在源码里是一条 if 链：

1. teammate 派生：`team_name` 可解析且带 `name` 时，直接转给 `spawnTeammate()`，返回 `teammate_spawned`（src/tools/AgentTool/AgentTool.tsx:284-316）。
2. fork 分叉：`subagent_type` 缺省且 fork 实验开启时走 FORK_AGENT，省略时退回 general-purpose（src/tools/AgentTool/AgentTool.tsx:322-335）。
3. remote 隔离：`isolation: 'remote'` 走 CCR 远程会话（ant-only，外部构建被死代码消除，src/tools/AgentTool/AgentTool.tsx:435-482）。
4. 常规子代理：同步或后台异步执行，由 `shouldRunAsync` 决定，`run_in_background`、agent 定义的 `background: true`、coordinator 模式、fork 实验或 proactive 任一为真即异步（src/tools/AgentTool/AgentTool.tsx:567）。

路由之前还有两条护栏：teammate 不能再派生 teammate（团队花名册是扁平的，src/tools/AgentTool/AgentTool.tsx:272-274）；in-process teammate 不能派生后台 agent，因为它的生命周期绑在 leader 进程上（src/tools/AgentTool/AgentTool.tsx:278-280）。这两条错误信息本身就是对多 Agent 拓扑约束的陈述。

worktree 隔离是 AgentTool 自己做的：派生前 `createAgentWorktree()` 建临时 worktree，结束后 `hasWorktreeChanges()` 检查，无改动就删除并清掉 metadata，有改动则保留并把 worktreePath 写回，供 resume 恢复 cwd（src/tools/AgentTool/AgentTool.tsx:590-593, 644-685）。

## runAgent：隔离上下文循环的实现

runAgent（973 行）是所有子代理真正的执行体，一个 AsyncGenerator，核心是给 `query()` 喂一套独立构造的上下文。隔离体现在四个层面。

上下文构造上，fork 路径继承父会话消息（先 `filterIncompleteToolCalls` 避免残缺 tool_use 触发 API 错误），普通路径只有一条用户消息；文件读取状态缓存对 fork 是 `cloneFileStateCache`，对普通子代理是全新空缓存（src/tools/AgentTool/runAgent.ts:370-378）。这是「共享」与「隔离」的第一个分岔点。

上下文瘦身只针对只读 agent（Explore、Plan），它们被剥掉 CLAUDE.md 和 gitStatus。注释里给了量化理由：每周 34M+ 次 Explore 派生，省 5-15 Gtok（src/tools/AgentTool/runAgent.ts:385-410）。这不是优化洁癖，是把「子代理不需要写代码规范」这个判断固化成代码。

权限作用域由 `agentGetAppState()` 实现，它是一个包了一层的状态访问器：agent 定义了 permissionMode 就覆盖（但 bypassPermissions/acceptEdits 优先）；异步 agent 打 `shouldAvoidPermissionPrompts`；`allowedTools` 存在时整体替换 session 级 allow 规则，注释明确写着「parent approvals don't leak through」，但保留 cliArg 规则（src/tools/AgentTool/runAgent.ts:296-299, 415-479）。

控制面的差异在 abort controller，分三支：override 优先，异步 agent 拿全新独立 controller（ESC 主线程不杀后台 agent），同步 agent 共享父 controller（src/tools/AgentTool/runAgent.ts:524-528）。普通子代理 `thinkingConfig` 强制 disabled 控制输出成本，fork 子代理继承父配置以命中 prompt 缓存（src/tools/AgentTool/runAgent.ts:679-684）。

MCP 扩展上，agent 定义的 frontmatter 可以声明自己的 MCP server，按名字引用（复用父会话已连接的 memoized client）或内联定义（新建连接、子代理结束时清理）。两类 client 分开记账，`cleanup()` 只断开内联新建的，引用来的共享 client 不能动（src/tools/AgentTool/runAgent.ts:135-217）。plugin-only 锁定时，用户来源的 agent 被跳过、plugin 与内置 agent 作为 admin-trusted 放行（src/tools/AgentTool/runAgent.ts:112-127）。

```typescript
const agentToolUseContext = createSubagentContext(toolUseContext, {
  options: agentOptions,
  agentId,
  agentType: agentDefinition.agentType,
  messages: initialMessages,
  readFileState: agentReadFileState,
  abortController: agentAbortController,
  getAppState: agentGetAppState,
  shareSetAppState: !isAsync,
  shareSetResponseLength: true,
  ...
})
```

`createSubagentContext` 是隔离的收口：同步 agent 共享 setAppState，异步完全隔离，但都通过 `setAppStateForTasks` 拿到 root store 写通道（src/tools/AgentTool/runAgent.ts:337-338, 700-714）。随后进入 query 循环，每条可记录消息写入 sidechain transcript（父链 uuid 串行维护，O(1) 追加），这就是子代理可被 resume、可被查看的持久化基础（src/tools/AgentTool/runAgent.ts:748-806）。

异步路径还有一层任务注册。AgentTool 在派生前先 `registerAsyncAgent` 拿到任务句柄和独立 abortController，注释明确说不挂父 controller：后台 agent 要在用户按 ESC 取消主线程后继续存活，只能由 chat:killAgents 显式杀掉（src/tools/AgentTool/AgentTool.tsx:686-698）。带了 `name` 的异步 agent 还会写入 `agentNameRegistry`，建立名字到 agentId 的映射供 SendMessage 路由（src/tools/AgentTool/AgentTool.tsx:703-712）。完成时以 `<task-notification>` 形式回注主会话，这与 coordinator 模式的消息协议是同一条管道。

## loadAgentsDir 与 forkSubagent：定义从哪来，分叉怎么省

`.claude/agents` 下的 markdown 定义由 `getAgentDefinitionsWithOverrides` 加载：memoize 缓存，`loadMarkdownFilesForSubdir('agents', cwd)` 扫目录，frontmatter 经 Zod 校验（tools、model、permissionMode、mcpServers、hooks、maxTurns、memory、isolation 等字段，src/tools/AgentTool/loadAgentsDir.ts:73-99, 296-308）。最终 agent 列表是 built-in + plugin + custom 三类合并，再按来源优先级去重（src/tools/AgentTool/loadAgentsDir.ts:357-365）。解析失败只记录不致命：没有 `name` 字段的文件静默跳过，有 `name` 的记 `tengu_agent_parse_error`（src/tools/AgentTool/loadAgentsDir.ts:320-338）。

forkSubagent 回答的是另一个问题：如果子代理需要的是父代理的全部上下文，怎么避免重新付一遍 token？方案是让所有 fork 子代理产生字节级相同的 API 请求前缀。`buildForkedMessages` 克隆父 assistant 消息的全部 tool_use 块，为每个块生成内容完全一致的占位 tool_result（`FORK_PLACEHOLDER_RESULT = 'Fork started — processing in background'`），唯一不同的是末尾追加的 per-child 指令（src/tools/AgentTool/forkSubagent.ts:93, 107-168）。FORK_AGENT 定义 `tools: ['*']` 配合 `useExactTools`，系统提示词直接复用父代理已渲染的字节而不是重算，注释说明重算会因 GrowthBook 冷温状态不同而炸缓存（src/tools/AgentTool/forkSubagent.ts:54-58）。递归防护用双保险：context.options 上的 querySource（抗 autocompact）加消息里扫描 boilerplate tag（src/tools/AgentTool/AgentTool.tsx:332-334; src/tools/AgentTool/forkSubagent.ts:78-89）。

resume 是 fork/子代理体系的另一半。`resumeAgentBackground` 从磁盘读 sidechain transcript 和 metadata，清洗消息（过滤未配对 tool_use、纯空白 assistant 消息），重建 content replacement state，worktree 目录不存在则退回父 cwd 并 bump mtime 防清理（src/tools/AgentTool/resumeAgent.ts:63-97）。agent 类型按 metadata 恢复，找不到就退 general-purpose（src/tools/AgentTool/resumeAgent.ts:100-112）。

fork 子代理的行为约束不是靠工具裁剪，而是靠一段写死在代码里的 boilerplate 提示词：`buildChildMessage` 生成的指令块以「STOP. READ THIS FIRST」开头，列出十条规则：不许再派生子代理、不许对话、不许编辑腔、报告以「Scope:」开头、500 词以内、结构化输出格式固定为 Scope/Result/Key files/Files changed/Issues 五个标签（src/tools/AgentTool/forkSubagent.ts:171-198）。提示词工程在这里替代了运行时强制：fork 子代理的工具池和父代理完全一致（缓存要求），「不许再 fork」这条约束只能靠提示词加 `isInForkChild` 的运行时拒绝双保险。

## spawnMultiAgent 与 swarm：teammate 的三种形态

`spawnTeammate()` 入口只做转发，逻辑全在 `handleSpawn` 的分派：in-process 开关开启就走 `handleSpawnInProcess`；否则先 `detectAndGetBackend()` 探测 pane 后端，auto 模式下探测失败静默回退 in-process 并 `markInProcessFallback()`，用户显式配置的模式则抛错（src/tools/shared/spawnMultiAgent.ts:1040-1078）。

后端探测的优先级写在 registry 注释里：在 tmux 内永远用 tmux；iTerm2 有 it2 CLI 用 iTerm2；否则 tmux 起外部 session；都没有则报错（src/utils/swarm/backends/registry.ts:128-135）。三个后端共享 PaneBackend 接口：TmuxBackend（764 行）用 pane 创建锁串行化并发派生，pane 建好后等 200ms 让 shell rc 加载完再发命令（src/utils/swarm/backends/TmuxBackend.ts:29-37）；ITermBackend 与 InProcessBackend 分别对应 it2 脚本接口与同进程协程。

pane 形态的 teammate 是独立 CLI 子进程，`buildInheritedCliFlags` 把父会话的权限模式、--model、--settings、--plugin-dir、--chrome 逐项翻译成 CLI flag 传下去；plan_mode_required 时特意不继承 bypassPermissions（src/tools/shared/spawnMultiAgent.ts:208-260）。

in-process 形态则是同进程的另一个 `runAgent` 循环。`handleSpawnInProcess` 生成确定性的 `name@team` agentId、分配颜色，然后 fire-and-forget 调 `startInProcessTeammate`，最后把 member 写进 team file 的 members 数组。这里它把 `toolUseContext.messages` 置空再传，注释说明：teammate 自己用 allMessages 建历史，传父会话全文会把整段对话 pin 在内存里，/clear 和 autocompact 都释放不掉（src/tools/shared/spawnMultiAgent.ts:910-938, 989-1009）。inProcessRunner 的主循环是「跑一轮 → 500ms 轮询 mailbox/内存消息 → 等下一条 prompt 或 shutdown」，历史超阈值时自己 compact，且用隔离的 toolUseContext 拷贝避免污染主会话的 readFileState（src/utils/swarm/inProcessRunner.ts:697, 1048, 1071-1104）。

还有一个细节：模型解析时 `inherit` 字面量的坑被单独修了。agent frontmatter 里的 `model: inherit` 曾经被原样传给 `--model` 触发「模型不存在」错误，`resolveTeammateModel` 现在把 inherit 替换成 leader 的模型，leader 模型未设置时落回默认值（src/tools/shared/spawnMultiAgent.ts:84-101）。teammate 重名时不报错，`generateUniqueTeammateName` 追加数字后缀（tester-2、tester-3）（src/tools/shared/spawnMultiAgent.ts:267）。这些都是多进程派生才会遇到的边界，单进程子代理不需要名字，也不需要 CLI 参数翻译。

## mailbox 与 permissionSync：跨进程的最小共享面

teammate 之间不共享内存，共享的是文件系统。mailbox 是 `~/.claude/teams/{team}/` 下的 per-agent inbox 文件，`writeToMailbox`/`readUnreadMessages`/`markMessagesAsRead` 构成全部通信原语（src/utils/teammateMailbox.ts:134, 115, 279）。

权限代理协议建在 mailbox 之上。worker 遇到权限提示时，把请求序列化成 JSON 写到 `teams/{team}/permissions/pending/`，leader 轮询检测、用户在 leader 的 UI 里批准/拒绝，结果落到 `permissions/resolved/`，worker 再轮询拿走（src/utils/swarm/permissionSync.ts:1-19, 108-141）。请求 schema 带 toolName、input、permissionSuggestions，解决结果可以带 `updatedInput`（leader 改过的输入）和 `permissionUpdates`（「总是允许」规则）（src/utils/swarm/permissionSync.ts:49-106）。in-process teammate 共享终端，走捷径：`leaderPermissionBridge` 是个模块级注册表，REPL 把自己的 `setToolUseConfirmQueue` 注册进去，teammate 的权限请求直接进 leader 的确认队列，跳过 mailbox（src/utils/swarm/leaderPermissionBridge.ts:25-54）。

断线重连由 reconnection.ts 负责：新进程启动时从 CLI 参数读 teamName/agentName 计算初始 teamContext；resume 旧会话时从 transcript 存的 team 信息查 team file 恢复（src/utils/swarm/reconnection.ts:23-66, 75-119）。两条路径都不信任内存，team file 是唯一事实源，member 找不到时只记 debug 日志继续跑（src/utils/swarm/reconnection.ts:92-97），因为 teammate 可能已被从花名册移除，此时崩溃比降级更糟糕。

## coordinatorMode：只保留编排工具的主 Agent

coordinator 模式（`CLAUDE_CODE_COORDINATOR_MODE`）把主 Agent 的工具池砍到只剩编排工具。worker 可用工具是 `ASYNC_AGENT_ALLOWED_TOOLS` 减去 `INTERNAL_WORKER_TOOLS`（TeamCreate、TeamDelete、SendMessage、SyntheticOutput），也就是说团队管理、消息、结构化输出是编排者的专属（src/coordinator/coordinatorMode.ts:29-34, 88-97）。scratchpad 目录由 `tengu_scratch` gate 控制，注入 userContext 供 worker 之间持久交换知识（src/coordinator/coordinatorMode.ts:25-27, 104-106）。

它的系统提示词有 258 行，内容接近一份多 Agent 工程手册，几条硬规则直接对应代码行为：

- worker 结果以 `<task-notification>` XML 的 user-role 消息回来，与真人消息区分（src/coordinator/coordinatorMode.ts:144-160）；
- 「Workers can't see your conversation」，每个 prompt 必须自包含，禁止写「based on your findings」（src/coordinator/coordinatorMode.ts:253-270）；
- continue vs. spawn 按上下文重叠度决策，验证代码的 worker 必须新开「fresh eyes」（src/coordinator/coordinatorMode.ts:280-293）。

coordinator 模式下所有派生强制异步（`isCoordinator` 进 `shouldRunAsync`，src/tools/AgentTool/AgentTool.tsx:567），与 fork 实验互斥（src/tools/AgentTool/forkSubagent.ts:34）。`matchSessionMode` 还处理了 resume 时的模式漂移：会话存的模式与当前环境变量不一致就直接翻转 `CLAUDE_CODE_COORDINATOR_MODE` 环境变量。`isCoordinatorMode()` 每次现读不缓存，翻转立即生效（src/coordinator/coordinatorMode.ts:49-78）。

coordinator 与 swarm 对比可以看出两种不同的编排分工。swarm 的 leader 自己还是完整 agent，可以直接读写代码，teammate 是「帮忙的终端窗口」；coordinator 被抽掉执行工具，只能派 worker、发消息、收 task-notification，是「纯调度者」。前者的瓶颈是 leader 的上下文，后者的瓶颈是消息协议的带宽，所以 coordinator 的提示词反复强调「synthesize，不要把理解外包给 worker」，是在为消息带宽不足做人工补偿。

## TeamCreate 与 SendMessage：建团队与发消息

TeamCreate 做的事比「建团队」多：生成唯一队名（冲突时用词组 slug）、写 team file（lead 作为第一个 member）、注册会话结束清理、重置对应 task list 让编号从 1 开始、把 teamName 写进 AppState.teamContext（src/tools/TeamCreateTool/TeamCreateTool.ts:64-72, 157-191）。一个 leader 同时只能带一个团队，重复创建直接抛错（src/tools/TeamCreateTool/TeamCreateTool.ts:136-140）。

SendMessage 是统一消息路由。纯文本走 `writeToMailbox`；`to: '*'` 走广播（读 team file 逐个写）；结构化消息是 shutdown_request/response 与 plan_approval_response 三种（src/tools/SendMessageTool/SendMessageTool.ts:46-65, 149-220）。发送者身份从环境变量取：`CLAUDE_CODE_AGENT_NAME` 存在则是 teammate，否则记为 team-lead（src/tools/SendMessageTool/SendMessageTool.ts:157-159），这与 TeamCreate 故意不给 lead 设 `CLAUDE_CODE_AGENT_ID` 的注释互相印证：lead 不是 teammate，`isTeammate()` 必须返回 false，否则 inbox 轮询逻辑会走错分支（src/tools/TeamCreateTool/TeamCreateTool.ts:224-228）。

SendMessage 对 in-process 异步 agent 有专门的路由：收件人在 `agentNameRegistry` 里且任务在跑，就 `queuePendingMessage` 排到下一个工具回合注入；任务停了则自动 `resumeAgentBackground` 用新消息续跑；任务被驱逐出内存就从磁盘 transcript 恢复（src/tools/SendMessageTool/SendMessageTool.ts:802-872）。「给已停止的 worker 发消息等于 resume」是协议行为，不是 UI 巧合。这条路径让 coordinator 提示词里「continue 比 spawn 新 worker 更省上下文」的建议有了机制支撑：续跑的 worker 带着全部历史，新派的是白纸。

## 隔离还是共享：代码里的取舍清单

把全篇的取舍摊开，可以看出一条一致的算账逻辑：

| 决策点 | 隔离派 | 共享派 | 依据 |
|---|---|---|---|
| 消息历史 | 普通子代理只有 prompt | fork 继承全部 + 占位 tool_result | 缓存命中率 vs 上下文成本 |
| readFileState | 空缓存起步 | fork 克隆父缓存 | 重复读文件的成本 |
| allow 规则 | allowedTools 整体替换 | cliArg 规则保留 | 父批准不泄漏，SDK 显式授权例外 |
| thinking | 子代理禁用 | fork 继承 | 输出 token 成本 vs 缓存前缀一致 |
| teammate 通信 | 各自独立进程/协程 | mailbox 文件 + permissionSync | 跨进程唯一可行通道 |
| worktree | 每 agent 独立工作副本 | 同仓同分支结构 | 写操作并行不互相踩 |

隔离的代价是重复（每个 worker 重读文件、重建上下文），共享的代价是污染（错误上下文锚定、缓存击穿、权限泄漏）。代码里每一处选择都有注释级别的理由，且大多附了量化估算或具体 bug 编号，这正是「多 Agent 协作的账」在源码里的形态。

## 本篇涉及的源码文件

- `src/tools/AgentTool/AgentTool.tsx`：子代理统一入口，负责路由（teammate/fork/remote/常规）、worktree 隔离与异步注册
- `src/tools/AgentTool/runAgent.ts`：子代理执行体：上下文构造、权限作用域、query 循环与 sidechain 持久化
- `src/tools/AgentTool/loadAgentsDir.ts`：.claude/agents markdown 定义加载、Zod 校验与来源优先级合并
- `src/tools/AgentTool/forkSubagent.ts`：fork 分叉实验：缓存共享的消息构造、递归防护与 FORK_AGENT 定义
- `src/tools/AgentTool/resumeAgent.ts`：从 sidechain transcript 恢复已停止的后台 agent
- `src/tools/shared/spawnMultiAgent.ts`：teammate 派生总线：后端分派、CLI flag 继承、in-process 派生与 team file 登记
- `src/utils/swarm/backends/registry.ts`：Tmux/ITerm2/InProcess 后端探测与回退
- `src/utils/swarm/backends/TmuxBackend.ts`：tmux pane 后端：创建锁、布局与 swarm session 管理
- `src/utils/swarm/inProcessRunner.ts`：in-process teammate 主循环：mailbox 轮询、compact 与任务认领
- `src/utils/swarm/permissionSync.ts`：基于 mailbox 文件的跨 agent 权限请求/响应协议
- `src/utils/swarm/leaderPermissionBridge.ts`：in-process teammate 借用 leader 权限确认队列的模块级桥
- `src/utils/swarm/reconnection.ts`：新派生与 resume 两条路径的 teamContext 重建
- `src/coordinator/coordinatorMode.ts`：编排者模式：工具裁剪、scratchpad 与 worker 管理手册式系统提示词
- `src/tools/TeamCreateTool/TeamCreateTool.ts`：建团队：team file、task list 与 teamContext 初始化
- `src/tools/SendMessageTool/SendMessageTool.ts`：团队消息路由：mailbox、广播、结构化消息与停止 agent 的自动 resume
