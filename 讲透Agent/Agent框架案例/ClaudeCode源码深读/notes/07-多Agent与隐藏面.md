# 07 · 多 Agent 体系与隐藏面

> card_id: ccsrc-07
> universe: Agent框架案例/ClaudeCode源码深读
> burke: 场景=单上下文不够用与产品不想让你看见的部分；主体=AgentTool/swarm/coordinator 三层 + feature 双层门控；能动=隔离共享按账分配 + DCE/GrowthBook 分发；行动=fork 缓存共享/mailbox 通信/undercover 缄默/anti-distillation 投毒；目的=并行而不互相污染、内外有别；张力=重用前缀 vs 权限泄漏；弧线=子代理到纯调度者、公开仓到双面产品
> status: 已完成（2026-08-20，钉版 `091cde4`）
> refs: articles/15/19/20 全文
> updated: 2026-08-20

## 1. 三层多 Agent 体系

底层 **AgentTool/runAgent**（隔离上下文的子代理循环）→ 中层 **spawnMultiAgent/swarm**（可寻址、可持久、有终端形态的 teammate）→ 顶层 **coordinatorMode**（主 Agent 降级为只能用编排工具的调度者）。

### AgentTool：一个入口四条路由（AgentTool.tsx）

if 链：①teammate 派生（team_name+name → spawnTeammate）②fork 分叉（subagent_type 缺省且实验开）③remote 隔离（CCR，ant-only 外部构建 DCE）④常规子代理（同步/后台异步，`run_in_background`/background:true/coordinator/fork/proactive 任一真即异步）。**两条拓扑护栏**：teammate 不能再派 teammate（花名册扁平）；in-process teammate 不能派后台 agent（生命周期绑 leader 进程）。worktree 隔离自己做：派生前建临时 worktree，结束无改动删除、有改动保留写回 path 供 resume。

### runAgent：隔离的四个层面（runAgent.ts:973 行）

- **上下文构造**：fork 继承父会话消息（先 filterIncompleteToolCalls 防残缺 tool_use 触发 API 错误）+ cloneFileStateCache；普通子代理只有一条用户消息+全新空缓存——**共享与隔离的第一个分岔点**
- **上下文瘦身**：只读 agent（Explore/Plan）剥掉 CLAUDE.md 和 gitStatus——**注释量化：每周 34M+ 次 Explore 派生，省 5-15 Gtok**。把"子代理不需要写代码规范"固化成代码
- **权限作用域**：agent 定义 permissionMode 可覆盖；allowedTools 整体替换 session 级 allow 规则——**"parent approvals don't leak through"** 但保留 cliArg 规则
- **控制面**：异步 agent 拿全新独立 abortController（**ESC 主线程不杀后台 agent**，只能 chat:killAgents 显式杀）；普通子代理 thinking 强制 disabled 控成本、**fork 继承父配置以命中 prompt 缓存**

**forkSubagent 的核心问题**：子代理需要父全部上下文时怎么避免重付 token？答案——**让所有 fork 子代理产生字节级相同的 API 请求前缀**：克隆父 assistant 的全部 tool_use 块并为每块生成一致的占位 tool_result（'Fork started — processing in background'），唯一不同是末尾 per-child 指令；系统提示词直接复用父代理已渲染字节（重算会因 GrowthBook 冷温状态不同而炸缓存）。**fork 子代理的行为约束靠提示词不靠工具裁剪**（缓存要求工具池一致）：boilerplate 以 "STOP. READ THIS FIRST" 开头列十条规则（不许再派生/不许对话/报告以 Scope: 开头/500 词内/Scope/Result/Key files/Files changed/Issues 五标签结构化输出）+ isInForkChild 运行时拒绝双保险。

resume 是另一半：从磁盘读 sidechain transcript+metadata，清洗消息（滤未配对 tool_use/纯空白），重建 content replacement state，worktree 不存在退父 cwd 并 bump mtime 防清理。

### swarm：teammate 三种形态

后端探测：tmux 内永远 tmux → iTerm2 有 it2 用 iTerm2 → tmux 起新 session → 报错；auto 探测失败静默回退 in-process。pane 形态是**独立 CLI 子进程**——buildInheritedCliFlags 把权限模式/--model/--settings 逐项翻译成 CLI flag 传下去（plan_mode_required 时特意不继承 bypassPermissions）；in-process 形态是同进程另一个 runAgent 循环（**把 toolUseContext.messages 置空再传——传父会话全文会把整段对话 pin 在内存里，/clear 和 autocompact 都释放不掉**）。

**mailbox 是跨进程唯一通道**：`~/.claude/teams/{team}/` 下 per-agent inbox 文件。权限代理协议建于其上：worker 权限请求写 `permissions/pending/` → leader 轮询、用户在 leader UI 批准 → `permissions/resolved/` → worker 取走（可带 updatedInput 和 permissionUpdates）；in-process 走捷径 leaderPermissionBridge（模块级注册表直接进 leader 确认队列）。**team file 是唯一事实源**，断线重连两条路径都不信任内存；member 找不到只记 debug 继续（teammate 可能已被移除，崩溃比降级更糟）。

**SendMessage 统一路由**：纯文本走 mailbox、`to:'*'` 广播、结构化三种（shutdown_request/plan_approval_response）；**给已停止的 worker 发消息 = 自动 resumeAgentBackground 用新消息续跑**——coordinator 提示词"continue 比 spawn 省"有了机制支撑：续跑带全部历史，新派是白纸。

### coordinatorMode：纯调度者

主 Agent 工具池砍到只剩编排工具（ASYNC_AGENT_ALLOWED_TOOLS 减 INTERNAL_WORKER_TOOLS——**团队管理/消息/结构化输出是编排者专属**）；258 行系统提示词接近多 Agent 工程手册：worker 结果以 `<task-notification>` XML 区分真人；"Workers can't see your conversation"——**每个 prompt 必须自包含，禁止写 based on your findings**；continue vs spawn 按上下文重叠度决策、验证代码的 worker 必须新开 fresh eyes。swarm leader 自己还是完整 agent、coordinator 被抽掉执行工具——**前者瓶颈是 leader 上下文，后者瓶颈是消息协议带宽**（提示词反复强调 synthesize 不要把理解外包给 worker，是为带宽不足做人工补偿）。

### 隔离 vs 共享取舍账本（15 篇原表浓缩）

| 决策点 | 隔离派 | 共享派 | 依据 |
|---|---|---|---|
| 消息历史 | 普通子代理只有 prompt | fork 继承+占位 | 缓存命中 vs 上下文成本 |
| readFileState | 空缓存起步 | fork 克隆父缓存 | 重复读文件成本 |
| allow 规则 | allowedTools 整体替换 | cliArg 保留 | 父批准不泄漏 |
| thinking | 子代理禁用 | fork 继承 | 输出成本 vs 前缀一致 |
| teammate 通信 | 独立进程/协程 | mailbox 文件 | 跨进程唯一可行 |
| worktree | 每 agent 独立副本 | 同仓结构 | 写并行不互踩 |

**隔离的代价是重复，共享的代价是污染**——每处选择都有注释级理由且大多附量化估算或 bug 编号。任务系统（19 篇）：后台 shell/后台子 agent/远程会话/定时任务/团队收件箱统一在一个 Task 状态框架下。

## 2. 隐藏面（20 篇）

**双层门控**：编译期 `feature()`（bun:bundle 常量折叠 DCE——**外部构建里内部功能不只是不执行，而是不存在**；全仓 940 余处调用去重 89 个 flag：KAIROS_DREAM/PROACTIVE/VOICE_MODE/COORDINATOR_MODE/TEAMMEM/ULTRAPLAN/TREE_SITTER_BASH/WEB_BROWSER_TOOL...）+ 运行时 GrowthBook（remoteEval 服务端求值本地无规则可反推）。GrowthBook 防御工程各对应真实事故：空 payload 守卫（transient bug 的 `{}` 整体写盘=total flag blackout）；磁盘缓存+热路径 MAY_BE_STALE 读；曝光每 feature 每会话一次；**ant 20 分钟刷新 vs 外部 6 小时**。三种读取策略按语义分：门禁宁可旧 true（stale false 会不公平拦截）、安全限制宁可旧 false、登录切换必须等新值。

**buddy 电子宠物**：Mulberry32 种子 PRNG（注释自嘲 "good enough for picking ducks"）、SALT='friend-2026-401'（已抽查验证）；稀有度权重 60/25/10/4/1、闪光独立 1%、五维 DEBUGGING/PATIENCE/CHAOS/WISDOM/SNARK；**防作弊设计：磁盘只存 Soul（名字性格），bones 每次从 hash(userId) 重生成——改配置文件改不出 legendary，同 userId 任何机器孵出同一只**。18 物种名用 charCode 运行时构造——与 excluded-strings.txt 的模型代号金丝雀（Capybara/Tengu）相撞，运行时构造让字面量不进 bundle 且检查继续生效。

**undercover 缄默协议**：ant 用内部构建给公共仓库提 PR 时不泄代号/未发布版本/内部仓名/go 短链/"Claude Code"字样/AI 身份暗示/Co-Authored-By——"1-shotted by claude-opus-4-6" 明确列为 BAD。**默认开、无强制关**：只有 remote 命中 22 个确认私有仓白名单才关；连 cwd 不是 git 仓库也保持 undercover（"Claude may push to public remotes from a CWD that isn't a git checkout"）。白名单刻意 repo 级而非 org 级（anthropics org 下有公共仓库）。

**anti-distillation 反蒸馏投毒**（claude.ts:301-313）：四重门控全过后在请求体写 `anti_distillation: ['fake_tools']`——**服务端在响应里注入虚假工具定义；抓包第一方流量去蒸馏的人学到的工具集混着不存在的工具**。投毒在服务端、客户端透明（本机抓包看到的响应同样带假工具）；只针对 1P（Bedrock/Vertex 天然免疫）；运行时 flag 可灰度可急停。**客户端代码里少见的主动对抗：不信任自己流量会被怎样使用**。

**/insights**：3200 行最重单文件命令——读全部历史会话日志、Opus 提取结构化 facet（根本目标/达成度/满意度/摩擦点）、并行 prompt 生成叙事章节（第二人称 + copyable_prompt 可直接粘回试用）；cc_team_improvements/model_behavior_improvements 让**用户自己的数据反哺产品团队**；detectMultiClauding 用 30 分钟滑窗检测多开模式——multi-clauding 成为被正式命名量化的行为。彩蛋：moreright 存根（25 行空操作 + 自带 base64 source map 出生证明）；spinnerVerbs 190 词 loading 动词表（含 Clauding/Honking/Flibbertigibbeting）。

## 3. 收束：这份源码教会我们什么

1. **同一仓库、两种构建、三种用户**（外部/ant/评测 harness）看到的不同程序——读泄露源码必须先辨 feature 门
2. **多 Agent 的本质是一本账**：每处隔离/共享选择都要量化理由（Gtok/缓存命中/权限泄漏）
3. **字节级一致是最强约束**：fork 共享缓存、工具排序、系统提示哨兵、thinking 继承——全服务于同一件事
4. **对抗性是产品需求**：anti-distillation/undercover/金丝雀检查——2026 年的头部 agent 已经把"被抄"当工程输入
5. 与姊妹卡三角互证：openclaw（插件宿主路线）/claw-code（净室重写路线）/本卡（原版全貌）——**harness 即产品的三条演化路径在同一坐标系可比**

📌 系列完。回[总纲](../README.md)。
