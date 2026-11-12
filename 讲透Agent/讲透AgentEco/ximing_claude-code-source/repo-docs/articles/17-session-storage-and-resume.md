---
title: Claude Code 源码拆解 17：会话持久化与恢复
date: "2026-04-12 10:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 17/20 篇 · 对应主题：checkpoint 与 sessionless

# 会话持久化与恢复

Claude Code 没有会话数据库，也没有 checkpoint 快照服务。一个会话的全部状态（消息、工具结果、文件历史、标题、标签、worktree 状态）都落在本地一个 JSONL 文件里，每行一条记录，只追加不改写。恢复就是把这个文件读回来、沿 parentUuid 链反向走一遍。理解了这个文件的生命周期，就理解了 Claude Code 的 sessionless 设计：进程本身不持有任何不可重建的状态，`--resume`、`--continue`、teleport 都是同一个文件的三种读法。

## 目录布局与 JSONL 格式

会话文件存放在 `~/.claude/projects/<sanitized-cwd>/<sessionId>.jsonl`。`getProjectsDir()` 返回配置目录下的 `projects`（src/utils/sessionStorage.ts:198），`getTranscriptPath()` 拼上当前 sessionId（src/utils/sessionStorage.ts:202）。目录名由 `sanitizePath` 生成：把所有非字母数字字符替换成 `-`，超长则截断并追加 hash 后缀（src/utils/sessionStoragePortable.ts:311）。`/Users/foo/my-project` 变成 `-Users-foo-my-project`。

文件内部，每条消息被序列化成一个 `TranscriptMessage`，关键字段在写入时盖上：`parentUuid` 构成消息链，`isSidechain` 标记是否子代理消息，外加 `sessionId`、`cwd`、`gitBranch`、`version`、`userType`、`entrypoint` 等环境戳（src/utils/sessionStorage.ts:1039-1064）。注释里强调，这些戳字段必须放在 spread 之后，否则 `--fork-session` 复制旧消息时会带着旧 sessionId，导致 content-replacement 记录按新 sessionId 查找时全部落空（src/utils/sessionStorage.ts:1049-1056）。

写入由一个进程级 `Project` 单例管理（src/utils/sessionStorage.ts:532）。写路径有三级缓冲：

- `pendingEntries`：sessionFile 为 null 时先进内存缓冲，等第一条 user/assistant 消息触发 `materializeSessionFile()` 才落盘，所以纯元数据操作（如只执行了 `/rename`）不会产生空会话文件（src/utils/sessionStorage.ts:976-991, 1138-1142）。
- 每文件写队列 `writeQueues`，100ms 定时器批量 drain，单 chunk 上限 100MB（src/utils/sessionStorage.ts:559-568, 618-631）。
- `appendToFile` 用 `fsAppendFile` 以 `0o600` 权限追加，目录不存在时先建目录（src/utils/sessionStorage.ts:634-643）。

## recordTranscript 与 sidechain 分离

主会话和子代理（Task 工具 spawn 的 subagent）写不同文件。`recordTranscript` 走主 session 文件，`recordSidechainTranscript` 带 `isSidechain=true` 走 `getAgentTranscriptPath()`：`<projectDir>/<sessionId>/subagents/agent-<agentId>.jsonl`（src/utils/sessionStorage.ts:1408, 1451, 247-258）。

`recordTranscript` 有一个针对 compaction 的去重细节：已记录的消息只有在构成前缀时才更新 parentUuid 游标。压缩后 `messagesToKeep`（UUID 与压缩前相同）出现在新的 compact boundary 之后，不算前缀，因此 boundary 拿到 `parentUuid=null`，`--continue` 链在压缩点处被截断（src/utils/sessionStorage.ts:1419-1431）。

写消息时按 `isSidechain && agentId` 路由到 agent 文件，且 sidechain 写入跳过了主会话 messageSet 的去重检查。注释解释了原因：fork 继承的父消息与主 transcript 共享 UUID，若对主集合去重，持久化的 sidechain 会不完整，恢复 fork 时只能读到 10KB，而不是完整的 85KB 继承上下文（src/utils/sessionStorage.ts:1224-1245）。

`isTranscriptMessage` 是"什么算 transcript 消息"的唯一判定点：user、assistant、attachment、system 四类。progress 消息不算，因为它们是瞬时 UI 状态，进 parentUuid 链会导致链分叉，恢复时会孤立真实消息（src/utils/sessionStorage.ts:139-146）。老文件里的 progress 行由 `loadTranscriptFile` 的 progressBridge 跨越：读盘时给每条 legacy progress 建一张 uuid→parentUuid 映射，遇到其父是 progress 的消息就把父指针桥接到 progress 的父上（src/utils/sessionStorage.ts:169-178, 3623-3636）。

除 transcript 外，每个子代理还有一个 sidecar 元数据文件 `agent-<agentId>.meta.json`，记录 agentType 与 worktree 隔离路径。注释说明用途：恢复 fork 时若省略 subagent_type，靠它路由回正确的 agent 类型，否则会静默退化成 general-purpose（4KB system prompt、无继承历史）；用 sidecar 而非 JSONL 行是为了不动 transcript schema（src/utils/sessionStorage.ts:260-303）。

## file-history 快照与 content-replacement

除消息外，JSONL 还混入多种旁证记录，都在 `appendEntry` 的类型分发里有各自的分支（src/utils/sessionStorage.ts:1158-1216）：

- `file-history-snapshot`：编辑工具改写文件前的快照，`insertFileHistorySnapshot` 写入，带 `messageId` 关联到触发它的消息（src/utils/sessionStorage.ts:1085-1099）。恢复时 `buildFileHistorySnapshotChain` 沿消息链收集，交给 `fileHistoryRestoreStateFromLog` 重建撤销栈（src/utils/sessionRestore.ts:103-108）。
- `content-replacement`：大工具结果被替换为占位符的记录。路由分叉：带 `agentId` 的写进 sidechain 文件（供 AgentTool 恢复），主线程的写进 session 文件（供 `/resume`）（src/utils/sessionStorage.ts:1200-1207）。`--fork-session` 恢复时会先把源会话的 replacement 记录用新 sessionId 重盖写一遍，否则旧 tool_use_id 找不到记录会被误判为 FROZEN，全文重发导致 cache miss（src/utils/sessionRestore.ts:452-462）。
- 元数据类：`custom-title`、`ai-title`、`tag`、`agent-name`、`mode`、`worktree-state`、`pr-link` 等，各自一行，后者覆盖前者。

元数据写入有一个尾部窗口问题：`readLiteMetadata` 这类轻量读取只看文件末尾 64KB，如果 `/rename` 之后又追加了大量消息，custom-title 行会被顶出窗口，恢复列表就退化显示自动生成的 firstPrompt。解法是退出时的 cleanup handler 先 flush 写队列，再调 `reAppendSessionMetadata()` 把缓存的标题、标签重新追加到文件末尾，保证它们总落在尾窗口内（src/utils/sessionStorage.ts:449-462）。标题本身分两种记录：`custom-title` 是用户改名，`ai-title` 是 AI 生成。读侧永远优先 `customTitle` 字段，所以无论追加顺序如何，用户改名都赢；`loadTranscriptFile` 的 customTitles Map 只收 `custom-title` 条目，`reAppendSessionMetadata` 因此不会把 AI 标题重写到 EOF，避免了恢复时旧 AI 标题覆盖会话中途用户改名的 bug（src/utils/sessionStorage.ts:2617-2673）。AI 标题由 `generateSessionTitle` 调 Haiku 生成：取对话文本尾部 1000 字符，用 JSON schema 约束输出 3-7 词的 sentence-case 标题（src/utils/sessionTitle.ts:26, 56-68, 79-121）。

还有一条反向通路：`removeMessageByUuid` 处理 tombstone。快路径只在文件尾 64KB 窗口里做字节级 `"uuid":"..."` 搜索，命中即 `ftruncate` 截断再补写尾部；慢路径整文件重写，但文件超过 50MB 直接跳过，避免 OOM（src/utils/sessionStorage.ts:871-951）。

## 恢复路径：从 JSONL 重建消息链

`loadTranscriptFile` 是恢复的入口（src/utils/sessionStorage.ts:3472）。大文件（>5MB，`SKIP_PRECOMPACT_THRESHOLD`）不走全文解析：`readTranscriptForLoad` 在 fd 层做单次前向分块读，compact boundary 之前的字节直接截掉，boundary 之前的会话级元数据（agent-setting、mode、pr-link）再用廉价的字节级扫描补回（src/utils/sessionStorage.ts:3536-3555）。注释里给了动机：一个 151MB、84% 是过期 attribution-snapshot 的会话，旧路径 RSS 卡在 316MB，新路径约 155MB（src/utils/sessionStorage.ts:3521-3529）。

即使截掉了 pre-boundary 段，buffer 里仍可能有大量死分支，比如 fork 产生的旧叶子和被丢弃的旁支；反正 `buildConversationChain` 只走一条链。`walkChainBeforeParse` 在 JSON 解析之前先从文件尾部做字节级扫描找到最新非 sidechain 叶子，再沿 parentUuid 在字节层反向走链，只保留链上的行进解析器（src/utils/sessionStorage.ts:3572-3579, 3399）。带 preservedSegment 的 compact boundary 除外：保留段的 parentUuid 指向 boundary 之前的消息，得先全量解析再由 `applyPreservedSegmentRelinks` 在内存里接回，预解析走链会把它们当孤儿丢掉（src/utils/sessionStorage.ts:3561-3571）。

解析出的消息进 `Map<UUID, TranscriptMessage>`，叶子集合预先算好。`loadTranscriptFromFile` 取最新叶子，调 `buildConversationChain` 沿 parentUuid 反向走到根（src/utils/sessionStorage.ts:2316-2326, 2069-2094）。链上还有一个修补 pass：流式输出时 N 个并行 tool_use 会产生 N 条共享 `message.id` 的 assistant 消息，每个 tool_result 的 parentUuid 指向各自的 assistant，单链遍历会丢弃兄弟分支；`recoverOrphanedParallelToolResults` 把这些孤儿 tool_result 接回来（src/utils/sessionStorage.ts:2096-2122）。

除消息链外，恢复还要还原若干派生状态：file-history 撤销栈、attribution、context-collapse 的 commit 日志与快照由 `restoreSessionStateFromLog` 重建；SDK 非交互模式下连 TodoWrite 的待办列表也是从 transcript 里最后一个 TodoWrite tool_use 块的入参反解出来的，不需要单独的持久化文件（src/utils/sessionRestore.ts:99-150, 77-93）。

拿到链之后，`processResumedConversation` 完成状态接管，顺序有讲究（src/utils/sessionRestore.ts:409-488）：

```typescript
if (!opts.forkSession) {
  const sid = opts.sessionIdOverride ?? result.sessionId
  if (sid) {
    switchSession(
      asSessionId(sid),
      opts.transcriptPath ? dirname(opts.transcriptPath) : null,
    )
    await renameRecordingForSession()
    await resetSessionFilePointer()
    restoreCostStateForSession(sid)
  }
}
```

`switchSession` 切换 sessionId 与项目目录（跨项目恢复时 transcriptPath 的 dirname 就是目标项目目录）；`resetSessionFilePointer` 把 sessionFile 置空防止新写入漏到旧文件；`restoreSessionMetadata` 把标题、标签、worktree 状态灌回缓存；`restoreWorktreeForResume` 在会话崩溃于 worktree 内时 `process.chdir` 回去，目录已被删则改写缓存为"已退出"（src/utils/sessionRestore.ts:332-366）。最后 `adoptResumedSessionFile()` 直接把 sessionFile 指向已存在的旧文件并补写元数据，而不是等第一条新消息来惰性建文件；否则 `-c -n foo` 之后直接退出会丢掉标题（src/utils/sessionStorage.ts:1509-1534）。

## /resume 会话列表：stat 优先，渐进富化

`/resume` 的列表不能为每个会话解析整个 JSONL。`loadSameRepoMessageLogsProgressive` 先对所有 `.jsonl` 做纯 stat（mtime），按 mtime 降序排，然后 `enrichLogs` 只富化前 50 条（`INITIAL_ENRICH_COUNT`），滚动到底再取下一批（src/utils/sessionStorage.ts:4086-4108, 5077-5105, 4577）。富化本身也只读头尾各 64KB（`LITE_READ_BUF_SIZE`），从头部提 firstPrompt，从尾部提 customTitle、lastPrompt、gitBranch（src/utils/listSessionsImpl.ts:79-149）。firstPrompt 的提取要跳过无意义首条：以小写 XML 标签开头的消息（IDE 上下文、hook 输出、任务通知）和 `[Request interrupted by user]` 标记都由一个通用正则过滤，避免维护一个永远落后于新通知类型的白名单（src/utils/sessionStorage.ts:114-126）。

SDK 侧的 `listSessionsImpl` 是同一思路的独立实现，且明确写了预算：带 `limit` 时先做 stat-only 排序，1000 个会话的目录只需 ~1000 次 stat + ~20 次内容读；不带 limit 才全文读一遍（src/utils/listSessionsImpl.ts:439-454）。sidechain 会话靠首行 `"isSidechain":true` 字符串匹配直接剔除，无标题无摘要的元数据-only 会话也剔除（src/utils/listSessionsImpl.ts:87-94, 121-122）。worktree 感知在 `gatherProjectCandidates`：把同一 repo 的所有 worktree 路径 sanitize 后与 `projects/` 下目录名做前缀匹配，合并多个项目目录的候选（src/utils/listSessionsImpl.ts:309-401）。

`/resume` 命令本身有三条命中路径：无参数弹选择器；参数是合法 UUID 则按 mtime 取最新匹配；UUID 查不到再退到 `getLastSessionLog` 直接按文件名找；最后按自定义标题精确匹配，多命中报错让用户进选择器（src/commands/resume/resume.tsx:222-273）。选择器里排除 sidechain 和当前会话自身（src/commands/resume/resume.tsx:191-193）。交互式恢复由 `ResumeConversation` 屏承接，选中后经 `loadConversationForResume` 加载，再走与 CLI 恢复相同的一套 switchSession / restoreSessionMetadata / adoptResumedSessionFile 流程（src/screens/ResumeConversation.tsx:178-292）。

## 跨项目恢复与并发会话

会话文件按 cwd 分目录存放，意味着换目录启动的 `claude --resume` 默认看不到别处的会话。选择器里勾选"all projects"后，`checkCrossProjectResume` 做三分支判断：同目录直接恢复；同 repo 的 worktree 也可以直接恢复（文件路径与会话目录可推导）；不同项目则不尝试在进程内切换，而是生成 `cd <projectPath> && claude --resume <sessionId>` 命令复制到剪贴板，让用户在新目录起一个新进程（src/utils/crossProjectResume.ts:30-75）。这是 sessionless 设计的直接推论：会话与 cwd 强绑定（路径、git 上下文、shell 状态），跨项目恢复靠换进程完成，不在进程内搬状态。

并发会话则走另一个目录：`~/.claude/sessions/<pid>.json`。每个顶层会话注册一行 PID 文件，记录 sessionId、cwd、kind（interactive/bg/daemon），退出时删除；`--resume` 切换 sessionId 时通过 `onSessionSwitch` 回调把 PID 文件里的 sessionId 一并改掉，否则 `claude ps` 会读错 transcript（src/utils/concurrentSessions.ts:59-109）。`countConcurrentSessions` 遍历 PID 文件，`isProcessRunning` 探活，死进程的残留文件直接清扫，但 WSL 上跳过清扫，因为跨 Windows/WSL 共享配置目录时 PID 探测会误杀活会话（src/utils/concurrentSessions.ts:168-204）。这也是纯文件方案：没有中心注册服务，活跃会话集合就是文件系统里能被探活的 PID 文件集合。

会话列表里每条 `SessionInfo` 的摘要字段也有优先级链：customTitle（含 aiTitle 兜底）> 尾部 `lastPrompt`（每轮由 `insertMessageChain` 缓存的用户最近输入，截断到 200 字符，src/utils/sessionStorage.ts:1074-1081）> 尾部 `summary` > 头部 firstPrompt；createdAt 取第一条记录的 ISO timestamp 而非 `stat().birthtime`，因为后者在部分文件系统上不受支持（src/utils/listSessionsImpl.ts:95-128）。tag 的提取限定在 `{"type":"tag"` 开头的行内做，避免撞上工具入参里的 `tag` 字段（git tag、Docker tag）（src/utils/listSessionsImpl.ts:129-135）。

## teleport：本地与远程之间的会话迁移

teleport 解决的是会话跨机器移动，两个方向：

本地到远程（`teleportToRemote`）：关键不是搬 transcript，而是搬 git 状态。`createAndUploadGitBundle` 先 `git stash create` + `update-ref refs/seed/stash` 把未提交改动变成可达对象，再 `git bundle create --all` 打包上传，远程容器从 bundle clone 而非 GitHub，拿到的就是调用者的精确本地状态（src/utils/teleport/gitBundle.ts:152-260）。bundle 有降级链：`--all` 超过 100MB 退到 `HEAD`，再大就 squash 成单个无父提交的树快照，丢掉历史但保住内容（src/utils/teleport/gitBundle.ts:46-104）。

远程到本地（`teleportResumeCodeSession`）：先校验 OAuth token 与组织 UUID，拉取 session 元数据并校验当前目录是不是会话所属 repo 的 checkout，不匹配就直接拒绝，报出该去哪个 repo 下执行（src/utils/teleport.tsx:430-491）。校验通过后 `teleportFromSessionsAPI` 拉远程 transcript，`checkOutTeleportedSessionBranch` 完成 fetch + checkout 远程分支（src/utils/teleport.tsx:315-344），`processMessagesForTeleportResume` 在消息尾部追加一条 user 消息和一条 system 消息告知模型"这个会话是从别处 teleport 来的"（src/utils/teleport.tsx:301-308）。本地侧的落盘复用同一套机制：`hydrateRemoteSession` 把远程日志整体写成本地 JSONL（writeFile 截断式覆盖），然后设好 remote ingress URL，后续增量写入同时走本地文件和远程同步（src/utils/sessionStorage.ts:1587-1622）。CCR v2 协议下还有 `hydrateFromCCRv2InternalEvents`：通过注册的事件 reader 拉取主线程与子代理的内部事件，把 transcript 条目拆出来分别写进主文件和各 agent 文件，压缩过滤由服务端完成，它只返回最近一次压缩边界之后的事件（src/utils/sessionStorage.ts:1624-1632）。

## sessionless 作为架构结论

整套机制合起来看，"会话"在 Claude Code 里不是一个运行时对象，而是三份可推导数据的并集：JSONL 里的消息链（对话状态）、同一文件里的元数据行（标题/标签/模式/worktree）、文件系统布局本身（项目归属、mtime 排序）。进程内存里的 `Project` 缓存只是写优化，崩了不丢数据；恢复不依赖任何服务，读文件就够；并发协调用 PID 文件加探活；跨机器迁移用 git bundle 加远程日志覆盖。连"删除"这种唯一需要改写历史的操作（tombstone），也被设计成尾部窗口内的字节截断而非数据库删除。checkpoint 与恢复这两个在别的 agent 框架里需要专门子系统的功能，在这里退化为"append-only 日志 + 读时重建"：文件是唯一事实来源，进程随时可弃。

## 本篇涉及的源码文件

- `src/utils/sessionStorage.ts`：会话持久化核心，JSONL 写队列、消息链、sidechain 路由、tombstone、transcript 加载与恢复、会话列表渐进加载
- `src/utils/sessionStoragePortable.ts`：可移植的路径 sanitize、head/tail 轻量读取、预压缩跳过等供 SDK 复用的纯函数
- `src/utils/sessionRestore.ts`：恢复编排，switchSession、元数据/worktree 恢复、agent 与模式还原、fork-session 处理
- `src/utils/listSessionsImpl.ts`：Agent SDK 的 listSessions 独立实现，stat 排序 + head/tail 富化的两阶段列表
- `src/utils/crossProjectResume.ts`：跨项目恢复判断，同 repo worktree 直接恢复，异项目生成 cd + --resume 命令
- `src/utils/concurrentSessions.ts`：并发会话注册表，~/.claude/sessions 下 PID 文件的注册、探活与清扫
- `src/utils/sessionTitle.ts`：基于 Haiku 的 AI 会话标题生成（供 ai-title 元数据使用）
- `src/screens/ResumeConversation.tsx`：`claude --resume` 的交互式会话选择屏与恢复流程
- `src/commands/resume/resume.tsx`：`/resume` 斜杠命令，选择器、UUID/标题匹配、跨项目提示
- `src/utils/teleport.tsx`：teleport 主流程，repo 校验、远程会话拉取、分支 checkout、teleport 通知消息
- `src/utils/teleport/gitBundle.ts`：本地到远程的 git bundle 打包上传（含 stash 种子与三级降级）
