---
title: Claude Code 源码拆解 10：记忆系统——文件记忆、自动提取与"做梦"整理
date: "2026-04-07 22:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 10/20 篇 · 对应主题：Agent 的记忆怎么做

# 记忆系统：文件记忆、自动提取与"做梦"整理

Claude Code 的记忆不是向量数据库，不是 KV 存储，而是一套以 Markdown 文件为核心、由多个后台子代理分工维护的体系。源码里至少有五条相互独立的记忆链路：memdir 文件记忆（长期）、findRelevantMemories 查询时召回、extractMemories 每轮自动提取（EXTRACT_MEMORIES）、autoDream 后台整理、SessionMemory 会话内笔记，以及 teamMemorySync 团队共享（TEAMMEM）。它们共享同一个文件目录约定，但触发时机、权限约束、提示词各不相同。

## memdir：文件即记忆

记忆的物理位置由 `getAutoMemPath()` 决定，默认落在 `~/.claude/projects/<sanitized-git-root>/memory/`（src/memdir/paths.ts:223-235）。路径解析有三级覆盖：`CLAUDE_COWORK_MEMORY_PATH_OVERRIDE` 环境变量、settings.json 的 `autoMemoryDirectory`（仅限 policy/local/user 等可信来源，项目级 settings 被刻意排除，防止恶意仓库把记忆目录指向 `~/.ssh`，src/memdir/paths.ts:168-186）、以及默认的 git 根目录推导。`validateMemoryPath` 拒绝相对路径、根路径、UNC 路径和含 null 字节的路径（src/memdir/paths.ts:109-150），因为记忆目录同时充当文件写入工具的豁免白名单根。

记忆目录内有一个固定入口文件 `MEMORY.md`，承担"索引"角色。它被无条件注入系统提示词，因此必须有硬上限：

```typescript
export const ENTRYPOINT_NAME = 'MEMORY.md'
export const MAX_ENTRYPOINT_LINES = 200
// ~125 chars/line at 200 lines. At p97 today; catches long-line indexes that
// slip past the line cap (p100 observed: 197KB under 200 lines).
export const MAX_ENTRYPOINT_BYTES = 25_000
```

（src/memdir/memdir.ts:34-38）注释里直接写了设定依据：200 行 × 约 125 字符是 p97 分位，字节上限是为抓出"行数没超但单行超长"的索引。`truncateEntrypointContent` 先按行截断、再按字节在最后一个换行处截断，并附加一条 WARNING 告知模型哪个上限被触发、指引它"把细节挪进 topic 文件"（src/memdir/memdir.ts:57-103）。提示词层面也反复强调：`MEMORY.md` 是索引不是记忆，每条一行、约 150 字符以内，格式为 `- [Title](file.md) — one-line hook`（src/memdir/memdir.ts:227）。

系统提示词的组装入口是 `loadMemoryPrompt()`（src/memdir/memdir.ts:419）。它按特性开关分发：KAIROS 常驻助手模式走 append-only 的日期日志提示词（src/memdir/memdir.ts:432-438）；TEAMMEM 开启时走私有+团队双目录的组合提示词；否则走单目录的 `buildMemoryLines`。无论哪条路径，harness 都先 `ensureMemoryDirExists` 把目录建好，提示词里明示"目录已存在，直接用 Write 写，不要 mkdir"（src/memdir/memdir.ts:116-119），注释说明这是为了省掉模型每次写记忆前跑 `ls`/`mkdir -p` 的轮次。

## 四类记忆的类型学

记忆内容被约束在一个封闭的四类分类法里（src/memdir/memoryTypes.ts:14-19）：

```typescript
export const MEMORY_TYPES = [
  'user',
  'feedback',
  'project',
  'reference',
] as const
```

每类记忆文件带 frontmatter（name / description / type），description 是一行描述，注释明确说它"用于在未来对话中决定相关性，所以要具体"（src/memdir/memoryTypes.ts:261-271）。配套的 `WHAT_NOT_TO_SAVE_SECTION` 把可从当前项目状态推导的内容全部排除：代码模式、架构、git 历史、CLAUDE.md 已有内容、临时任务状态（src/memdir/memoryTypes.ts:183-195）。feedback 和 project 两类还规定了正文结构：规则先行，然后 `**Why:**` 和 `**How to apply:**` 两行，理由是"知道 why 才能在未来判断边界情况，而不是盲目遵守规则"（src/memdir/memoryTypes.ts:63）。

召回侧同样有防漂移设计。`TRUSTING_RECALL_SECTION` 要求模型：记忆提到文件路径就先确认文件存在，提到函数或 flag 就先 grep，"记忆说 X 存在"不等于"X 现在存在"（src/memdir/memoryTypes.ts:240-256）。这段提示词是 eval 驱动调出来的，注释记录了 H1 假设从 0/2 到 3/3 的验证过程，以及"放在 When to access 小节下就掉到 0/3，位置很重要"的教训。

## findRelevantMemories：查询时召回

`MEMORY.md` 是常驻上下文的索引，topic 文件则按需召回。`findRelevantMemories` 在用户每轮输入时跑一次：先扫描记忆目录里所有 `.md` 文件的 frontmatter（排除 MEMORY.md，最多 200 个，按 mtime 倒序，src/memdir/memoryScan.ts:35-77），把文件名+类型+时间戳+description 拼成清单，然后发一个 side query 给 Sonnet，让它从清单里挑最多 5 个"明确有用"的文件（src/memdir/findRelevantMemories.ts:39-75）。

选择提示词里有两条反噪音规则：拿不准就不要选；如果用户最近在用的某个工具的记忆只是该工具的使用文档，不要选，但关于该工具的警告、坑点仍然要选，"正在使用时恰恰是这些最重要的时候"（src/memdir/findRelevantMemories.ts:18-24）。选择结果通过 JSON schema 结构化输出，返回的文件名再用 `validFilenames` 集合过滤一遍，防止模型幻觉出不存在的文件（src/memdir/findRelevantMemories.ts:129-130）。

召回的第二个维度是时间。`memoryAge` 把 mtime 转成"today / yesterday / N days ago"（src/memdir/memoryAge.ts:15-20），注释解释了为什么不用 ISO 时间戳："模型不擅长日期算术，原始 ISO 时间戳不会像 '47 days ago' 那样触发陈旧度推理"。超过一天的记忆会被附加一段陈旧度警告：记忆是时间点观察而非实时状态，涉及代码行为或 file:line 的断言可能已过期，断言前先对当前代码验证（src/memdir/memoryAge.ts:33-42）。召回结果以 `relevant_memories` 附件注入，header 里就带着这段警告或"(saved N days ago)"（src/utils/attachments.ts:2327-2332）。同一文件在同一轮已展示过的会被 `alreadySurfaced` 过滤，把 5 个名额留给新候选（src/utils/attachments.ts:2231-2234）。召回本身不阻塞主流程：选择器的 promise 在用户一轮开始时预取（prefetch），与主模型的流式输出和工具执行并行，到收集点只读取已 settle 的结果，没就绪就跳过、下一轮再试，预取不阻塞当前轮（src/utils/attachments.ts:2334-2339）。

记忆目录之外还有一条搜索过去上下文的备用路径：当 GrowthBook 的 `tengu_coral_fern` 开启时，提示词会附加一段 `## Searching past context`，告诉模型先在记忆目录里 grep `*.md`，实在不行再去 grep 项目转录目录里的 `*.jsonl`，并提醒转录文件大且慢、是最后手段，要用窄关键词（报错信息、文件路径、函数名）而不是宽泛词（src/memdir/memdir.ts:375-407）。

## extractMemories：每轮结束的自动提取

`MEMORY.md` 提示词给了主代理完整的保存指令，但主代理经常忙着干活忘了存。extractMemories 是兜底：每次查询循环结束（模型产出无工具调用的最终回复）时，从 stopHooks 以 fire-and-forget 方式触发（src/services/extractMemories/extractMemories.ts:1-14）。

实现用的是 forked agent 模式，即主对话的分叉，共享父对话的 prompt cache（`runForkedAgent`，src/services/extractMemories/extractMemories.ts:415-427）。状态全部闭包封装在 `initExtractMemories()` 里：一个 UUID 游标记录上次处理到哪条消息，一个 `inProgress` 标志防重入，一个 `pendingContext` 存放下运行期间到达的请求、结束后跑一次尾随提取（src/services/extractMemories/extractMemories.ts:296-326）。

互斥逻辑在 `hasMemoryWritesSince`：如果主代理本轮自己写过记忆文件（assistant 消息里有指向 auto-mem 路径的 Write/Edit tool_use），后台提取整轮跳过并把游标推过这段区间，主代理与后台代理在每轮上互斥（src/services/extractMemories/extractMemories.ts:121-148）。

提取代理的工具权限被 `createAutoMemCanUseTool` 收紧：Read/Grep/Glob 不限；Bash 只放行 `isReadOnly` 判定通过的命令；Edit/Write 仅限 auto-mem 目录内的路径；其余全部拒绝（src/services/extractMemories/extractMemories.ts:171-222）。提示词也配合这个约束：告知代理只有有限轮次预算，最优策略是第一轮并行发所有 Read、第二轮并行发所有 Write/Edit，且"只用最近 N 条消息的内容，不要花轮次去 grep 源码验证"（src/services/extractMemories/prompts.ts:37-43）。硬上限 `maxTurns: 5`（src/services/extractMemories/extractMemories.ts:426）。提取前还会把现有记忆清单预先注入提示词，省掉代理自己 `ls` 的一轮（src/services/extractMemories/extractMemories.ts:398-400）。

游标的推进策略也考虑了失败与压缩两种情况：提取成功才把游标推到最新一条消息，失败则保持不动，下次提取会重新考虑这批消息（src/services/extractMemories/extractMemories.ts:429-435）；如果游标指向的消息已被上下文压缩移除，计数函数回退为统计全部可见消息而不是返回 0，否则提取会在会话剩余时间里被永久禁用（src/services/extractMemories/extractMemories.ts:103-109）。非交互模式（print 模式）下，print.ts 在响应冲刷后调用 `drainPendingExtraction`，带 60 秒软超时等待在途提取完成，避免 forked 代理被 5 秒优雅关停保险丝杀死（src/services/extractMemories/extractMemories.ts:605-615）。

## autoDream：睡眠时的四阶段整理

单轮提取解决"别漏记"，但记忆文件会随时间腐化：重复、矛盾、索引膨胀。autoDream 是定期触发的后台整理，触发条件三道门，从便宜到贵依次检查（src/services/autoDream/autoDream.ts:5-9）：

1. 时间门：距上次整理 ≥ minHours（默认 24 小时），只需一次 stat；
2. 会话门：mtime 晚于上次整理的会话数 ≥ minSessions（默认 5 个，排除当前会话）；
3. 锁：没有其他进程正在整理。

锁的设计很经济：锁文件 `.consolidate-lock` 的 mtime 本身就是"上次整理时间"，文件内容是持有者 PID（src/services/autoDream/consolidationLock.ts:1-23）。获取锁 = 写入自己的 PID 使 mtime 变为 now；失败回滚 = 用 `utimes` 把 mtime 拨回获取前的值；进程崩溃 = mtime 卡住但 PID 已死，下一个进程检查 `isProcessRunning` 后回收，超过 1 小时即使 PID 活着也视为过期（防 PID 复用，src/services/autoDream/consolidationLock.ts:46-84）。

门全过后，consolidation 提示词以一个 forked 子代理跑"做梦"流程，提示词按四阶段组织（src/services/autoDream/consolidationPrompt.ts:26-61）：

- Phase 1（Orient）：`ls` 记忆目录、读 `MEMORY.md`、浏览现有 topic 文件，目标是改进而非新建重复文件；
- Phase 2（Gather recent signal）：按优先级找新信息，依次是 daily logs、与代码现状矛盾的旧记忆、必要时窄关键词 grep 会话 JSONL 转录（"不要穷尽地读转录"）；
- Phase 3（Consolidate）：合并新信号进已有 topic 文件，相对日期转绝对日期，删除被证伪的事实；
- Phase 4（Prune and index）：修剪 `MEMORY.md` 到 200 行 / 25KB 以内，删掉过期指针，超过 200 字符的索引行说明内容放错了地方，缩短并下沉到 topic 文件。

做梦代理复用 extractMemories 的 `createAutoMemCanUseTool`，Bash 同样只读、写入仅限记忆目录（src/services/autoDream/autoDream.ts:227）。整理过程中的每个 assistant 轮次被 `makeDreamProgressWatcher` 监视，收集 Edit/Write 的 file_path（src/services/autoDream/autoDream.ts:281-313），完成后在主转录里以 "Improved N memories" 的形式内联汇报（src/services/autoDream/autoDream.ts:238-248）。KAIROS 常驻模式不走这条路，它用 append-only 日志 + 每夜 /dream 蒸馏的另一套范式（src/services/autoDream/autoDream.ts:96）。

## SessionMemory：会话内的滚动笔记

与跨会话的长期记忆不同，SessionMemory 维护的是当前会话的笔记文件，主要服务于 compaction（自动压缩时提供上下文摘要）。它在 `initSessionMemory` 里注册为 post-sampling hook，且只在 auto-compact 开启时注册（src/services/SessionMemory/sessionMemory.ts:357-375）。

触发不看消息条数而看 token 增长，与 autocompact 用同一套 `tokenCountWithEstimation` 计量：首次提取要求上下文达到 `minimumMessageTokensToInit`（默认 10000），之后每次提取要求相对上次增长 `minimumTokensBetweenUpdate`（默认 5000）且工具调用数 ≥ 3；或者 token 阈值满足且最后一轮没有工具调用（自然停顿点）时也提取（src/services/SessionMemory/sessionMemoryUtils.ts:32-36, src/services/SessionMemory/sessionMemory.ts:134-181）。token 阈值是硬条件，注释强调即使工具调用数达标也不会提前提取，防止过度提取。

提取同样走 `runForkedAgent`，但权限比 extractMemories 更紧：`createMemoryFileCanUseTool` 只放行对那一个记忆文件本身的 Edit，其余一切拒绝（src/services/SessionMemory/sessionMemory.ts:460-482）。`/summary` 命令可以绕过阈值手动触发同一条链路（src/services/SessionMemory/sessionMemory.ts:387-453）。

## teamMemorySync：团队共享记忆（TEAMMEM）

团队记忆是 auto-mem 目录下的 `team/` 子目录（src/memdir/teamMemPaths.ts:84-86），按 git remote 标识的 repo 维度在组织内共享。开启前提是 auto memory 已开，再叠加 GrowthBook 的 `tengu_herring_clock` 开关（src/memdir/teamMemPaths.ts:73-78）。类型系统为此扩展出 `<scope>` 维度：user 永远私有；feedback 默认私有、只有项目级约定才进 team；project 倾向 team；reference 通常 team（src/memdir/memoryTypes.ts:44-101）。

同步语义在文件头注释里写得很清楚：pull 以服务端为准按 key 覆盖本地；push 只上传内容 hash 与 `serverChecksums` 不同的 key（增量上传，服务端 upsert）；删除不传播：本地删文件不会删服务端，下次 pull 会恢复（src/services/teamMemorySync/index.ts:14-20）。增量比较靠 `sha256:<hex>` 内容 hash，与服务端 `entryChecksums` 格式一致，直接字符串相等比较（src/services/teamMemorySync/index.ts:134-136）。上传有两道体积闸门：单文件 250KB（src/services/teamMemorySync/index.ts:75）、单个 PUT 请求体 200KB，后者是为了躲开网关 256~512KB 的非结构化 413，超限就拆成多个顺序 PUT，靠服务端 upsert-merge 语义保证安全（src/services/teamMemorySync/index.ts:80-89）。条目数上限不在客户端写死，而是从服务端结构化 413 的 `extra_details.max_entries` 里学习（src/services/teamMemorySync/index.ts:111-118）。

本地写入侧，`watcher.ts` 对 team 目录起 `fs.watch`，变更去抖 2 秒后触发 push（src/services/teamMemorySync/watcher.ts:35）。永久性失败（无 OAuth、无 repo、除 409/429 外的 4xx）会置 `pushSuppressedReason` 彻底停止重试直到会话重启或文件删除，注释记录了动机：一台无 OAuth 的设备曾在 2.5 天内发出 16.7 万次 push 事件（src/services/teamMemorySync/watcher.ts:45-73）。

安全上客户端做两层校验。路径 key 经 `sanitizePathKey` 拒绝 null 字节、URL 编码穿越、NFKC Unicode 归一化穿越、反斜杠和绝对路径（src/memdir/teamMemPaths.ts:22-64）；内容上，上传前过一遍 `scanForSecrets`，即 gitleaks 高置信规则的精选子集（AWS/GCP/Azure key、各类 PAT、Anthropic API key 等），命中的文件直接不上传，密钥不出本机（src/services/teamMemorySync/secretScanner.ts:1-19, 48-80）。

## 工程取舍

这套系统里没有向量检索，没有专门的数据库。长期记忆是纯文件，`MEMORY.md` 索引常驻上下文换 O(1) 的"知道有什么"，相关性靠一个小模型读 frontmatter 清单做选择；写入侧主代理与后台代理按轮互斥，权限收窄到"只读一切、只写记忆目录"；整理侧用 mtime 当锁、用四阶段提示词当流程；共享侧用 hash 增量同步加密钥扫描。每条链路的提示词里都留着 eval 驱动的修改记录（某个 bullet 放在哪个小节、用什么措辞，背后是 0/3 到 3/3 的通过率差异），这是它比"存起来再说"类记忆方案更像工业系统的地方：记忆的读写行为本身被当作需要评测和迭代的产品功能。

## 本篇涉及的源码文件

- `src/memdir/memdir.ts`：记忆目录提示词组装、MEMORY.md 截断、loadMemoryPrompt 分发入口
- `src/memdir/paths.ts`：记忆目录路径解析、开关判定、路径安全校验
- `src/memdir/memoryTypes.ts`：user/feedback/project/reference 四类记忆的类型学与提示词段落
- `src/memdir/memoryScan.ts`：记忆文件 frontmatter 扫描与清单格式化
- `src/memdir/memoryAge.ts`：记忆年龄格式化与陈旧度警告文案
- `src/memdir/findRelevantMemories.ts`：基于 Sonnet 选择器的查询时记忆召回
- `src/memdir/teamMemPaths.ts`：团队记忆路径、开关与 key 安全校验
- `src/memdir/teamMemPrompts.ts`：私有+团队双目录组合提示词
- `src/services/extractMemories/extractMemories.ts`：每轮结束的 forked-agent 自动记忆提取与权限收窄
- `src/services/extractMemories/prompts.ts`：提取代理的提示词模板
- `src/services/autoDream/autoDream.ts`：后台记忆整理的时间/会话/锁三重门控与触发
- `src/services/autoDream/consolidationPrompt.ts`：做梦整理的四阶段提示词
- `src/services/autoDream/consolidationLock.ts`：以 mtime 为时间戳、PID 为主体的整理锁
- `src/services/autoDream/config.ts`：autoDream 开关
- `src/services/SessionMemory/sessionMemory.ts`：会话内滚动笔记的触发判定与提取
- `src/services/SessionMemory/sessionMemoryUtils.ts`：会话记忆阈值配置与状态
- `src/services/teamMemorySync/index.ts`：团队记忆的服务端拉取/增量推送协议
- `src/services/teamMemorySync/watcher.ts`：本地变更的 fs.watch 去抖推送
- `src/services/teamMemorySync/secretScanner.ts`：上传前的客户端密钥扫描
