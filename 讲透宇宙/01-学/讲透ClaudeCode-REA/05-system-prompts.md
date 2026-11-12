# 05 · 系统提示词体系：四身份 + 协调者全文 + 注入模板

> 证据：`chunk-294m9458.js`（64KB「提示词常量模块」）模板字面量全量提取 [S]；
> 深报告（协调者 15,627 字符全文 + 工具描述生成器逐个还原 + 符号表）见
> `rea-claude/reports/01-system-prompts.md`。

## 1. 身份不是三条，是四条 [S]

| 常量 | 身份串 | 触发 |
|---|---|---|
| `U` | "You are Claude Code, Anthropic's official CLI for Claude." | 交互式主 CLI；**Vertex 端点一律用它** |
| `Te` | "…running within the Claude Agent SDK." | 非交互 + 有 appendSystemPrompt |
| `Ee` | "You are a Claude agent, built on Anthropic's Claude Agent SDK." | 非交互裸 agent（无 appendSystemPrompt） |
| `yyr` 首行 | "…orchestrates software engineering tasks across multiple workers." | 环境变量 `CLAUDE_CODE_COORDINATOR_MODE` |

选择函数 `DGt` [offset=39942]；组装点在主 bundle `qTo()` [chunk-1kyfp16b offset=2625465]：
overrideSystemPrompt → 协调者（`ks()` 检 env + 无自定义 agent）→ 主 CLI 正文 + `DGt(...)` 身份行 + 缓存标记。

所有变体共用附录块 `zpe`「# Reporting outcomes」[offset=39022]——917 字符的汇报真实性
规范："Report what actually happened… If you did not check, say you did not check."——
产品级 agent 把「禁止虚构完成状态」写进提示词层。

## 2. 协调者（Orchestrator）提示词要点 [S]

15,627 字符模板 [offset=48459]，结构：Role → Tools → Workers（continue vs spawn 决策表）
→ Task Workflow（Phases/Concurrency/真验证/失败处理/停止）→ **Writing Worker Prompts** →
Example Session。精华在第 5 节：

- **自包含铁律**："Workers can't see your conversation. Every prompt must be self-contained"。
- **必须综合**：禁止 "Based on your findings…" 转发式汇报（正反例逐字给出）。
- **purpose statement**：任务书首句锚定深度与重点（PR 描述/规划/快检三型）。
- **continue vs spawn**：验证、错误路线重试 → 全新 worker（fresh eyes 防锚定）；
  修 bug/延续工作 → continue（保上下文）。
- **done 定义**：实现类 = 跑测试+typecheck+commit 回报 hash；研究类 = 只报告不改文件。
- **审批传递协议（防伪造同意）**：任何 agent 消息不构成用户同意；用户批准被卡动作时
  必须 spawn 全新 Agent，prompt 逐字引用批准原话 + 命令原样 + 只含执行步骤——
  收窄 prompt-injection→action 面。

comms 模式（存在 role="comms" 的 MCP 服务器）：裸文本不达用户，每回合必须以 comms
工具调用结尾；未调则触发哨兵 `BRIEF_ENFORCE_SENTINEL`。

## 3. system-reminder 注入族 [S]

| 模板 | 用途 |
|---|---|
| `WEe`/`LGt` 两变体 | 后台任务通知「NOT USER INPUT」防误当用户确认（独占回合/同回合两版措辞不同） |
| `FGt`/`PYe` 转义 | 内容里的 `</system-reminder>` 替换为 `&lt;…&gt;`——防逃逸包裹层（注入防护） |
| `ESt` | 定时任务头：声明 prompt 是预约存储 + "no live user input"（防调度任务伪造同意） |
| `jXn`/`WXn` | CLAUDE.md 等上下文包裹层 + "may or may not be relevant" 免责 |
| 文件状态族 `G/MGt/Re/K/Y` | 防重复 Read 五连：编辑后禁重读、未变更拒绝读、"file state is current" |
| `<task-notification>` 五段 | worker 完成通知 XML：task-id/status/summary/result/usage |

上下文章节名清单 `zXn`（13 项）与区块上限（GXn=12/KXn=16）、上下文 diff 计算 `VXn`
（changedBlocks/addedSections…）——**上下文注入本身是有版本管理的结构化协议**。

## 4. 工具描述生成器（动态拼装）[S]

工具描述不是静态字符串而是函数（按模式/平台拼装）：`Read→SXn`、`WebSearch→kXn`、
`Grep→Rbn`、`WebFetch→vXn`、`Write→TXn`；另有延迟加载族 `ToolSearch→HGt`、
`WaitForMcpServers→Pbn`、`RefreshMcpTools→AXn`。**MCP 工具一律延迟**（先 ToolSearch
取 schema）；永不延迟名单：memory 三件套、ToolSearch、StructuredOutput、Agent、
SendUserMessage、ScheduleWakeup 等。

## 5. worker 任务书组装 [S]

`hyr(mcpTools, scratchpadDir)` [offset=44859] 生成 workerToolsContext：
工具清单行（name + searchHint）→ Artifact HTML 规范 → MCP 工具表 → scratchpad 目录
（跨 worker 持久知识，"prefer plain data and markdown files"）。

工具集裁剪：SIMPLE 模式=极简集（Bash/PowerShell、Read、Edit、多会话时 Agent）；
正常模式=外部工具集过滤（SendMessage/StructuredOutput 剔除、Artifact/GetTask 条件保留）。

worker 自身身份三型（定义在主 bundle）：通用 `VHn`（412 字符，"complete the task fully—
don't gold-plate"）、文件检索专家（**整段 READ-ONLY 禁写清单**，禁到 heredoc/重定向级）、
网页阅读专家。

## 6. 并发与配额 env [S]

`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`（默认 **20**）、
`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`（默认 **200**）、
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`（嵌套 spawn 深度）、
`CLAUDE_CODE_COORDINATOR_FORCE_WORKER_INHERIT_MODEL`/`CLAUDE_CODE_SUBAGENT_MODEL_FORCE`
（worker 强制继承会话模型，禁指定 model）。

## 7. 手搓启示（→ rl-and-agents/）

1. 身份行是**函数不是常量**——按运行形态（CLI/SDK/裸 agent/协调者）选择；
2. 防注入是提示词层的系统性工程：notification 声明 + 包裹转义 + 审批逐字引用三件套；
3. "Reporting outcomes" 块值得原样抄进任何 agent——它就是 anti-hallucination 的提示词化；
4. 任务书规范（自包含/purpose/done 定义/continue-vs-spawn）是多 agent 系统的
   真正难点，协调者提示词 15K 字符里一半在教这个。
