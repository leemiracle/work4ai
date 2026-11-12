---
title: Claude Code 源码拆解 19：任务系统与自动化
date: "2026-04-12 16:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 19/20 篇 · 对应主题：异步 Agent 架构

# Claude Code 源码拆解 19：任务系统与自动化

前几篇讨论的 Agent 工具、权限、上下文压缩都围绕"单轮对话"展开。本篇换一个视角：Claude Code 如何让工作脱离当前对话轮次独立运行，覆盖后台 shell、后台子 agent、远程云端会话、定时任务、团队收件箱。这套异步能力的底层是一个统一的 Task 状态框架，外加一族面向模型的 Task 工具。

## 统一任务框架与三类后台任务

所有后台执行体都被抽象为 `TaskState` 联合类型，共 7 种具体状态（src/tasks/types.ts:12）：本地 shell、本地 agent、远程 agent、进程内 teammate、本地 workflow、MCP monitor、Dream 任务。是否计入"后台任务指示器"由单一谓词判定：

```typescript
export function isBackgroundTask(task: TaskState): task is BackgroundTaskState {
  if (task.status !== 'running' && task.status !== 'pending') {
    return false
  }
  if ('isBackgrounded' in task && task.isBackgrounded === false) {
    return false
  }
  return true
}
```

（src/tasks/types.ts:37）注意第二个条件：前台运行中的任务即使 status 是 running 也不显示在后台 pill 里，`isBackgrounded` 标志把"前台执行"和"后台执行"区分开。

### 本地 agent 任务

`LocalAgentTaskState` 是三类任务中字段最多的（src/tasks/LocalAgentTask/LocalAgentTask.tsx:116），除了 prompt、agentType、result 外，还维护了增量汇报游标（`lastReportedToolCount`/`lastReportedTokenCount`）、`pendingMessages` 队列（SendMessage 在 agent 回合中途投递的消息，在工具轮边界被 `drainPendingMessages` 排空，src/tasks/LocalAgentTask/LocalAgentTask.tsx:181）、以及 UI 持有/驱逐语义（`retain`、`evictAfter`）。

注册入口 `registerAsyncAgent` 做三件事：把任务的磁盘输出文件初始化成指向 agent 会话 transcript 的 symlink（src/tasks/LocalAgentTask/LocalAgentTask.tsx:483）；若有父 abort controller 则创建子 controller，父 agent 中止时子 agent 自动级联中止（src/tasks/LocalAgentTask/LocalAgentTask.tsx:486）；然后以 `isBackgrounded: true` 注册初始状态。

运行期间的进度统计由 `ProgressTracker` 承担。token 记账区分输入输出：API 返回的 input_tokens 是按回合累计的，只保留最新值；output_tokens 是单回合增量，逐回合累加（src/tasks/LocalAgentTask/LocalAgentTask.tsx:73）。每次 assistant 消息到达时遍历 content 里的 tool_use 块计数，并把最近 5 条工具活动（含预计算的活动描述、是否搜索/读取的分类）保留在环形窗口里供 UI 展示（src/tasks/LocalAgentTask/LocalAgentTask.tsx:83）。周期性摘要服务写入的 1-2 句 progress summary 还会通过 `emitTaskProgress` 推给 SDK 消费者（如 VS Code 子 agent 面板），但只在显式开启 `getSdkAgentProgressSummariesEnabled` 时发送，避免未订阅的消费者收到泄漏事件（src/tasks/LocalAgentTask/LocalAgentTask.tsx:390）。

完成通知采用"原子置位 + 条件入队"模式防止重复通知：

```typescript
let shouldEnqueue = false;
updateTaskState<LocalAgentTaskState>(taskId, setAppState, task => {
  if (task.notified) {
    return task;
  }
  shouldEnqueue = true;
  return { ...task, notified: true };
});
if (!shouldEnqueue) {
  return;
}
```

（src/tasks/LocalAgentTask/LocalAgentTask.tsx:227）通知正文是 XML 包裹的 `<task-notification>`，携带 taskId、输出文件路径、status、摘要、usage 与 worktree 信息（src/tasks/LocalAgentTask/LocalAgentTask.tsx:252），通过 `enqueuePendingNotification` 进入消息队列，在下一轮注入模型上下文。kill 路径上，`killAsyncAgent` 只中止 running 状态的任务，置 `evictAfter = Date.now() + PANEL_GRACE_MS` 给 UI 留一段展示宽限期（src/tasks/LocalAgentTask/LocalAgentTask.tsx:294），并异步驱逐磁盘输出。

### 本地 shell 任务

`LocalShellTaskState` 的 type 字段保留字面量 `'local_bash'` 以兼容持久化会话状态（src/tasks/LocalShellTask/guards.ts:12），并用 `agentId` 记录 spawn 它的 agent；agent 退出时 `killShellTasksForAgent` 会清扫其遗留的后台进程，防止僵尸脚本跑十天（src/tasks/LocalShellTask/killShellTasks.ts:53）。

这个文件里还有一个"停滞看门狗"机制。后台命令如果只是慢（长构建、`git log -S`）不该打扰模型，但如果是卡在交互式提示符上等待键盘输入，模型需要被告知。实现是每 5 秒 stat 一次输出文件，45 秒无增长后 tail 最后 1024 字节，用一组正则匹配末行：

```typescript
const PROMPT_PATTERNS = [/\(y\/n\)/i,
/\[y\/n\]/i,
/\(yes\/no\)/i, /\b(?:Do you|Would you|Shall I|Are you sure|Ready to)\b.*\? *$/i,
/Press (any key|Enter)/i, /Continue\?/i, /Overwrite\?/i];
```

（src/tasks/LocalShellTask/LocalShellTask.tsx:32）命中后才发送一条无 `<status>` 标签的通知。注释解释了原因：print.ts 把 `<status>` 当作终态信号，未知值会落到 'completed'，会错误关闭 SDK 消费者眼中的任务（src/tasks/LocalShellTask/LocalShellTask.tsx:76）。通知里还直接给出修复建议："Kill this task and re-run with piped input (e.g., `echo y | command`)"（src/tasks/LocalShellTask/LocalShellTask.tsx:88），诊断和修复动作写在同一条通知里。

spawn 路径 `spawnShellTask` 的数据流很短：注册任务后调用 `shellCommand.background(taskId)` 把进程转入后台，输出数据经由 TaskOutput 对象自动落盘，任务层不需要挂任何流监听器（src/tasks/LocalShellTask/LocalShellTask.tsx:218）。进程结束的 result promise 里先停看门狗，再按退出码把状态翻成 completed/failed、发通知、驱逐磁盘输出（src/tasks/LocalShellTask/LocalShellTask.tsx:222）。前台命令也能升级：`registerForeground` 以 `isBackgrounded: false` 注册（src/tasks/LocalShellTask/LocalShellTask.tsx:259），用户按 Ctrl+B 时 `backgroundTask` 把 shellCommand 转后台并补挂看门狗和结果处理器（src/tasks/LocalShellTask/LocalShellTask.tsx:293）。前台/后台共用同一条完成路径，只是初始标志不同。

### 远程 agent 任务

`RemoteAgentTaskState` 对应 Claude Code Remote（CCR）云端会话，子类型有五种：`remote-agent`、`ultraplan`、`ultrareview`、`autofix-pr`、`background-pr`（src/tasks/RemoteAgentTask/RemoteAgentTask.tsx:60）。与本地任务最大的区别是生命周期跨越进程：注册时把 taskId、sessionId、命令等写入会话 sidecar（src/tasks/RemoteAgentTask/RemoteAgentTask.tsx:442），`--resume` 时 `restoreRemoteAgentTasks` 扫描 sidecar、向 CCR 拉取实时状态、重建 AppState 并重启轮询（src/tasks/RemoteAgentTask/RemoteAgentTask.tsx:477）；404 的会话清理 sidecar，401 则视为可恢复。

轮询循环 `startRemoteSessionPolling` 间隔 1 秒（src/tasks/RemoteAgentTask/RemoteAgentTask.tsx:540）。远程会话在每个工具回合之间会短暂翻转成 idle，单次观测到 idle 不能当真，代码要求连续 5 次轮询无日志增长且状态 idle 才认定"稳定 idle"（src/tasks/RemoteAgentTask/RemoteAgentTask.tsx:545）。ultraplan 和长生命周期任务（autofix-pr）每个 CCR 回合都会发 result 事件，因此 result 事件不能驱动完成判定，被显式跳过（src/tasks/RemoteAgentTask/RemoteAgentTask.tsx:610）。远程 review 任务则以 `<remote-review>` 标签为完成信号，且只扫描增量事件保持 O(new) 复杂度（src/tasks/RemoteAgentTask/RemoteAgentTask.tsx:619）。此外每种远程任务类型可注册自己的完成检查器，`registerCompletionChecker` 存入 Map，每次轮询 tick 调用（src/tasks/RemoteAgentTask/RemoteAgentTask.tsx:84）。

## Task 工具族与 TodoWrite 的分工

面向模型有两套任务清单工具，二者互斥开启：TodoWrite 的 `isEnabled` 返回 `!isTodoV2Enabled()`（src/tools/TodoWriteTool/TodoWriteTool.ts:53），TaskCreate 返回 `isTodoV2Enabled()`（src/tools/TaskCreateTool/TaskCreateTool.ts:69）。V1 是会话内 todo 清单，V2 是带 owner、blocks/blockedBy 依赖和 hook 的任务系统。

TodoWrite 的 call 逻辑只有一步：整个 todos 数组覆盖写入 `appState.todos[todoKey]`，key 是 agentId 或 sessionId（src/tools/TodoWriteTool/TodoWriteTool.ts:67）。另外有一处结构性引导：主线程 agent 一次性关闭 3 个以上任务且其中没有验证步骤时，工具结果尾部追加一条提醒，要求 spawn verification agent。触发点精确选在"最后一个任务关闭、循环即将退出"的时刻（src/tools/TodoWriteTool/TodoWriteTool.ts:76）。

TaskCreate 的步骤多得多：`createTask` 落库后执行 `executeTaskCreatedHooks`，任何 hook 返回 blockingError 都会回滚，回滚方式是 `deleteTask` 删除刚建的任务并抛错（src/tools/TaskCreateTool/TaskCreateTool.ts:104）。任务创建成功后还会自动把 UI 展开到 tasks 视图（src/tools/TaskCreateTool/TaskCreateTool.ts:116）。

## TaskOutput：阻塞读取后台输出

`TaskOutputTool` 是后台任务结果的统一读取口，保留 `AgentOutputTool`/`BashOutputTool` 两个历史别名（src/tools/TaskOutputTool/TaskOutputTool.tsx:150）。它的 description 已标注 Deprecated，推荐直接 Read 任务输出文件（src/tools/TaskOutputTool/TaskOutputTool.tsx:158），但阻塞读取的实现本身没有删，下面按代码讲它的流程。

输入三个参数：`task_id`、`block`（默认 true）、`timeout`（默认 30 秒，上限 600 秒）（src/tools/TaskOutputTool/TaskOutputTool.tsx:30）。阻塞路径是一个手写轮询循环：

```typescript
const startTime = Date.now();
while (Date.now() - startTime < timeoutMs) {
  if (abortController?.signal.aborted) {
    throw new AbortError();
  }
  const state = getAppState();
  const task = state.tasks?.[taskId] as TaskState | undefined;
  if (!task) {
    return null;
  }
  if (task.status !== 'running' && task.status !== 'pending') {
    return task;
  }
  await sleep(100);
}
```

（src/tools/TaskOutputTool/TaskOutputTool.tsx:121）每 100ms 检查一次 AppState，任务离开 running/pending 即返回；等待开始前先通过 `onProgress` 上报 `waiting_for_task` 进度事件让 UI 显示等待状态（src/tools/TaskOutputTool/TaskOutputTool.tsx:243）。数据装配按类型分派：local_bash 优先从内存中的 `taskOutput` 对象读 stdout/stderr，local_agent 优先返回内存中 result 的干净文本而非磁盘上的完整 JSONL transcript（src/tools/TaskOutputTool/TaskOutputTool.tsx:98）。拿到终态结果后顺手把 `notified` 置位，抑制后续重复的完成通知（src/tools/TaskOutputTool/TaskOutputTool.tsx:272）。返回给模型的 tool_result 也是结构化 XML：`<retrieval_status>`（success/timeout/not_ready）加 task_id、task_type、status、exit_code、output、error 等标签，output 经 `formatTaskOutput` 截断压缩（src/tools/TaskOutputTool/TaskOutputTool.tsx:285）。

## ScheduleCronTool、AGENT_TRIGGERS 与 Sleep

定时调度由 CronCreate/CronDelete/CronList 三工具组成，总开关 `isKairosCronEnabled` 叠加三层：构建期 `feature('AGENT_TRIGGERS')` 死代码消除、运行时 GrowthBook `tengu_kairos_cron` 门控（5 分钟刷新窗口）、本地环境变量 `CLAUDE_CODE_DISABLE_CRON` 覆盖（src/tools/ScheduleCronTool/prompt.ts:36）。GrowthBook 默认值取 true 是有意的：Bedrock/Vertex 用户和禁用遥测的用户拿不到 GB 配置，默认 false 会直接打断已 GA 的 /loop（src/tools/ScheduleCronTool/prompt.ts:27）。

CronCreate 的 validateInput 做四道校验：cron 表达式可解析、未来一年内有匹配日期、任务总数不超 50、teammate 上下文禁止 durable（teammate 不跨会话持久化，durable cron 重启后会变成孤儿）（src/tools/ScheduleCronTool/CronCreateTool.ts:82）。durable 与 session-only 的区别在于是否写入 `.claude/scheduled_tasks.json`；call 里还有一个运行时 kill switch：durable 门控关闭时强制降级为会话内任务而不改 schema，模型不会因门控中途翻转看到校验错误（src/tools/ScheduleCronTool/CronCreateTool.ts:120）。创建后调用 `setScheduledTasksEnabled(true)` 启动调度 tick 循环（src/tools/ScheduleCronTool/CronCreateTool.ts:133）。

工具 prompt 里有一段少见的"面向机群"的引导：避免 :00 和 :30 整点，因为全球用户的"每小时""早上 9 点"会同时砸向 API；调度器自身也加确定性抖动，周期任务最多晚 10%（上限 15 分钟），整点的一次性任务最多提前 90 秒（src/tools/ScheduleCronTool/prompt.ts:105）。周期任务 7 天后自动过期，最后一次触发后删除（src/tools/ScheduleCronTool/prompt.ts:118）。

配套的 SleepTool 是纯提示层工具，prompt 明确要求用它替代 `Bash(sleep ...)`，理由是它不占 shell 进程，可与其它工具并发调用，并提醒 prompt cache 5 分钟过期，醒得太勤会丢缓存（src/tools/SleepTool/prompt.ts:15）。

## 计划模式：Enter/ExitPlanMode 的状态切换

EnterPlanMode 没有输入参数，call 做两件事：拒绝 agent 上下文调用（子 agent 不能自行进入计划模式，src/tools/EnterPlanModeTool/EnterPlanModeTool.ts:78），然后把权限模式切到 'plan'：

```typescript
context.setAppState(prev => ({
  ...prev,
  toolPermissionContext: applyPermissionUpdate(
    prepareContextForPlanMode(prev.toolPermissionContext),
    { type: 'setMode', mode: 'plan', destination: 'session' },
  ),
}))
```

（src/tools/EnterPlanModeTool/EnterPlanModeTool.ts:88）`prepareContextForPlanMode` 处理用户默认模式为 auto 时的分类器激活副作用。工具结果里直接附行为指令："DO NOT write or edit any files yet"（src/tools/EnterPlanModeTool/EnterPlanModeTool.ts:118）。两个工具的 `isEnabled` 都有一道 channels 门：`--channels` 激活时用户在 Telegram/Discord 上，审批对话框会挂死，入口和出口一起禁用，防止模型进入出不来（src/tools/EnterPlanModeTool/EnterPlanModeTool.ts:60）。

ExitPlanModeV2 在执行前有两项前置检查。`validateInput` 先检查当前权限模式：deferred 工具列表在任何模式下都向模型宣告这个工具，模型可能在计划已获批后再次调用它，此时直接拒绝并报"你不在计划模式中"，避免无谓弹出审批框，同时打一条 `tengu_exit_plan_mode_called_outside_plan` 分析事件（src/tools/ExitPlanModeTool/ExitPlanModeV2Tool.ts:204）。`requiresUserInteraction` 对 teammate 返回 false，因为审批走 leader 邮箱或本地自愿退出，不需要终端交互（src/tools/ExitPlanModeTool/ExitPlanModeV2Tool.ts:185）。

退出路径分三类。teammate 且要求计划审批：把 `plan_approval_request`（含计划文件路径和全文）写入 team-lead 的 mailbox，置 `awaitingLeaderApproval` 后返回，由 leader 异步批复（src/tools/ExitPlanModeTool/ExitPlanModeV2Tool.ts:287）。普通用户：`checkPermissions` 返回 ask 弹确认框（src/tools/ExitPlanModeTool/ExitPlanModeV2Tool.ts:234）。主流程则恢复进入计划模式前的 `prePlanMode`；若原模式是 auto 但 TRANSCRIPT_CLASSIFIER 门控已关闭（熔断器或设置禁用），降级回 default 并弹通知，防止借退出计划模式绕过熔断器（src/tools/ExitPlanModeTool/ExitPlanModeV2Tool.ts:347）。恢复 auto 时保留剥离的危险权限，恢复非 auto 时还原 `strippedDangerousRules`（src/tools/ExitPlanModeTool/ExitPlanModeV2Tool.ts:383）。

## EnterWorktree：git worktree 隔离

EnterWorktree 是会话中途切换工作目录的隔离工具。call 的流程严格按序：已在 worktree 会话中直接抛错（src/tools/EnterWorktreeTool/EnterWorktreeTool.ts:79）；先 `findCanonicalGitRoot` 解析主仓库根并 chdir 过去，保证从嵌套 worktree 里调用也能正确建树（src/tools/EnterWorktreeTool/EnterWorktreeTool.ts:84）；`createWorktreeForSession` 建好后 chdir 进新 worktree、`setOriginalCwd` 记录原目录、`saveWorktreeState` 持久化（src/tools/EnterWorktreeTool/EnterWorktreeTool.ts:92）；最后清掉三类缓存：系统 prompt 段落（env_info 需要按 worktree 重算）、memory 文件缓存、plans 目录缓存（src/tools/EnterWorktreeTool/EnterWorktreeTool.ts:99）。名称经 `validateWorktreeSlug` 校验：每段只允许字母数字点下划线短横线，总长 64 字符（src/tools/EnterWorktreeTool/EnterWorktreeTool.ts:27）。

## useInboxPoller：团队收件箱轮询

多 agent 团队的异步通信走文件邮箱：每个成员一个 JSON 收件箱，路径为 `~/.claude/teams/{team_name}/inboxes/{agent_name}.json`，写入侧用同名 `.lock` 文件做互斥（src/utils/teammateMailbox.ts:54、src/utils/teammateMailbox.ts:142）。`useInboxPoller` 是消费侧的 React hook，每 1 秒轮询一次未读消息（src/hooks/useInboxPoller.ts:107）。

轮询身份由 `getAgentNameToPoll` 决定：进程内 teammate 返回 undefined（它们有共享 React 上下文，走自己的 waitForNextPromptOrShutdown，双轮询会导致消息路由错乱），进程外 teammate 用自己的 agent 名，team lead 用 teammates 表里的名字（src/hooks/useInboxPoller.ts:81）。

读到未读消息后先按类型分桶，权限请求/响应、沙箱权限、shutdown、模式切换、计划审批各走各的处理函数，剩下的才是常规消息（src/hooks/useInboxPoller.ts:216）。计划审批响应有一处安全校验：只接受 `from === 'team-lead'` 的批准，防止 teammate 伪造审批退出自己的计划模式（src/hooks/useInboxPoller.ts:162）。

权限桥接的流程如下。team lead 侧收到 teammate 的权限请求后，不是简单转发文本，而是构造一个完整的 `ToolUseConfirm` 条目塞进 leader 的 ToolUseConfirmQueue：查找真实 Tool 对象、带上 workerBadge（agent 名 + cyan 颜色），让 tmux 里跑的 worker 在 leader 终端上得到和进程内 teammate 完全相同的权限 UI（src/hooks/useInboxPoller.ts:266）。allow/reject/abort 三个回调都通过 `sendPermissionResponseViaMailbox` 回写请求方的收件箱（src/hooks/useInboxPoller.ts:298）。去重靠 toolUseID：上一轮 markMessagesAsRead 失败时同一条消息会被重读，已在队列里的直接跳过（src/hooks/useInboxPoller.ts:340）。空闲时还会为第一条请求发桌面通知（src/hooks/useInboxPoller.ts:355）。worker 侧收到权限响应则按 request_id 查注册回调，分 approved/rejected 两路走 `processMailboxPermissionResponse` 完成本地 promise（src/hooks/useInboxPoller.ts:367）。常规消息的投递分忙闲两路：会话空闲且无对话框时直接 `onSubmitTeammateMessage` 作为新回合提交；忙或提交被拒时写入 `AppState.inbox` 队列，等回合结束由另一个 useEffect 补投（src/hooks/useInboxPoller.ts:843）。`markMessagesAsRead` 刻意放在投递或可靠入队之后：如果在投递前进程崩溃，下一轮轮询会重读这些消息而不是静默丢失（src/hooks/useInboxPoller.ts:860）。

本篇覆盖的异步机制可以归成五块：统一 Task 框架负责状态，Task 工具族负责模型侧的创建与读取，cron/Sleep 负责时间触发，计划模式和 worktree 负责执行边界，文件邮箱负责跨进程通信。下一篇是本系列最后一篇，讲剩下的主题。

## 本篇涉及的源码文件

- `src/tasks/types.ts`：TaskState 联合类型与后台任务判定谓词
- `src/tasks/LocalAgentTask/LocalAgentTask.tsx`：本地子 agent 任务的注册、进度、通知与终止
- `src/tasks/LocalShellTask/LocalShellTask.tsx`：后台 shell 任务与交互式提示停滞看门狗
- `src/tasks/LocalShellTask/guards.ts`：LocalShellTaskState 类型与守卫
- `src/tasks/LocalShellTask/killShellTasks.ts`：shell 任务终止与 agent 退出时的孤儿清扫
- `src/tasks/RemoteAgentTask/RemoteAgentTask.tsx`：CCR 远程会话任务、sidecar 持久化与 1s 轮询循环
- `src/tools/TodoWriteTool/TodoWriteTool.ts`：V1 会话 todo 清单工具（含验证引导）
- `src/tools/TodoWriteTool/prompt.ts`：TodoWrite 的使用规范 prompt
- `src/tools/TaskCreateTool/TaskCreateTool.ts`：V2 任务创建工具与 TaskCreated hook 回滚
- `src/tools/TaskCreateTool/prompt.ts`：TaskCreate 的使用规范 prompt
- `src/tools/TaskOutputTool/TaskOutputTool.tsx`：后台任务输出的阻塞/非阻塞读取
- `src/tools/ScheduleCronTool/CronCreateTool.ts`：cron 任务创建、校验与 durable 降级
- `src/tools/ScheduleCronTool/prompt.ts`：AGENT_TRIGGERS 门控与调度行为 prompt
- `src/tools/SleepTool/prompt.ts`：Sleep 工具 prompt
- `src/tools/EnterPlanModeTool/EnterPlanModeTool.ts`：进入计划模式与权限模式切换
- `src/tools/ExitPlanModeTool/ExitPlanModeV2Tool.ts`：退出计划模式、leader 审批与模式恢复
- `src/tools/EnterWorktreeTool/EnterWorktreeTool.ts`：会话内 git worktree 创建与切换
- `src/hooks/useInboxPoller.ts`：团队文件邮箱的 1s 轮询与忙闲投递
- `src/utils/teammateMailbox.ts`：文件邮箱路径与锁文件机制
