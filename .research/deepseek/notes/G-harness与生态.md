# G · deepseek-harness 与 awesome 生态三仓：harness 工程深读笔记

> 深读对象：`C:\workspace\work4ai\.tools\deepseek-repos\` 下 4 个本地浅克隆仓库：deepseek-harness（重点）、awesome-deepseek-integration、awesome-deepseek-agent、awesome-deepseek-coder。
> 方法：README/中英双语文档全读 + docs/ 全目录扫描（architecture/cordis-primer/tool-execution-pipeline/agent-lifecycle/capability-seams/glossary/user guide）+ packages/ 目录结构（219 个 package.json 实测）+ 核心包 README 与关键源码头段（core/tools、core/agent-loop、core/session、llm、sandbox、approval、subagent、mcp、compaction、skill、ralph、tool-cordis、hooks、vendor、python）。7412 文件未全读，按 README→docs→packages 结构→核心包文档的抽样策略执行。
> 诚实约束：星数（104k/39k/5.8k/807）来自任务简报的外部元数据，仓库内无法验证；deepseek-harness 处于 developer preview，`README.md:11` 明示"将出现破坏兼容性的变更"，一切细节以当时 commit 为准。awesome-integration 条目数为自动正则计数（约 250，含少量图标链接误差）。没读到的源码细节不编造，引用一律给文件路径。

---

## 1. deepseek-harness（dsh）：DeepSeek 的官方开源 agent harness

### 1.1 定位与形态：一句话与基本盘

**dsh 是 DeepSeek AI 官方开源的 agent harness（`README.md:5`），口号 "Everything is a Plugin"，底层由 Cordis 插件框架驱动（其设计论文为《A Programming Paradigm for Spatiotemporal Composability》，`README.md:7`）。MIT 协议，TypeScript，monorepo。**

产品形态是"一个启动器 + 多种运行面"（`apps/cli/README.md`）：

| 入口 | 形态 |
|---|---|
| `npx @deepseek-ai/dsh web` | 启动 Web UI（默认 `http://127.0.0.1:3080`），主推形态 |
| `dsh --profile headless "job"` | 一次性任务跑完打印最终答案即退出，无服务器 |
| `dsh --profile <name>` | 启动任意自定义 profile（插件层叠） |
| `dsh plugin --profile <name> <pnpm args>` | 通过 pnpm 管理该 profile 的树外插件 |
| Python SDK（`python/`） | `deepseek-harness-sdk`，以子进程方式驱动打包好的运行时，newline-delimited JSON-RPC over stdio（`python/README.md:5`），自带捆绑 Node 运行时无需系统 Node |
| ACP server（`packages/acp/`） | automation-only 的 Agent Client Protocol 服务器 |
| JSON-RPC SDK（`packages/sdk/`） | 进程外运行时协议 + TS 客户端 + 服务器插件 |

即：**它不是"又一个 CLI"，而是 CLI 启动器 + Web 应用 + headless runner + Python/JSON-RPC/ACP 三种进程外协议的组合，全部由同一棵插件树组装出来**。

当前模型接入面（`docs/user/guide/providers.md`）：DeepSeek 官方 API 是默认一等公民，但**不是唯一**——`dsh-llm-pi-ai` 适配器提供目录化 provider（Anthropic、OpenAI、Bedrock、Vertex、Azure、Codex OAuth）+ 任意 OpenAI 兼容自定义端点（baseURL + `GET /models` 发现）；测试用 `llm-replay` 回放适配器。密钥只写不读（UI 拿到 redacted descriptor），存 `$DSH_HOME/.credentials.yaml`，settings 只留 credential 引用（providers.md:13）。文档还细致处理了多模态声明：手填模型默认 text-only，vision 需在 settings.yaml 给模型加 `input: [text, image]`（providers.md:33-50）。

### 1.2 Cordis：被"买断"的依赖注入插件框架

**Cordis 是关键中的关键**：它不是 dsh 内部发明的模块系统，而是 cordiverse/cordis——Koishi 生态（聊天机器人框架）作者 shigma 一系的插件框架，有一篇学术化定位论文（"时空可组合性编程范式"）。dsh 的做法非常重：

- **vendor 而非依赖**：整个 Cordis + 基础库（cosmokit、schemastery、loader、include、group、timer、hmr、logger-console）以源码形式钉进 `vendor/`，pin 到具体 upstream commit（cordis 4.0.0-rc.7，commit 56b3d4f…，`vendor/README.md:17`），全部重命名进 `@deepseek-ai` scope，每个 harness 包把 cordis 声明为 peerDependency——"发布 harness 即发布框架层，且不占用上游 npm 名"（vendor/README.md:5）。
- **18 条本地修改日志**（vendor/README.md:29-50）：包括 fiber 生命周期加固（三个重入销毁缺口）、事务性 Loader/Include 配置和解、HMR 精确配置监听（Windows 短名路径防碰撞）、`disabled: !!js` 惰性插值等——每一处 divergence 都有测试文件引用。这是一份"如何严肃对待供应链"的范本。

Cordis 五个核心思想（`docs/cordis-primer.md:9-13`）：

1. **插件 = 实现 Service 的对象**：函数（带可选 `inject`/`apply(ctx)`）或 `Service` 子类；
2. **上下文 = 服务仓库**：服务认领稳定 `ctx.<key>`（`ctx.tools`、`ctx.llm`、`ctx.sessions`），其他插件按键查找而非 import 具体实现；
3. **`inject` 声明依赖**：命名了所需服务的插件会等到服务存在才加载——**加载顺序用服务需求表达，不做手工 boot 序列**；
4. **类型化事件**：TS declaration merging 声明事件，四种派发模式各司其职；
5. **注册皆可逆 effect**：prompt section、tool schema、监听器全部通过 `ctx.effect()`/`ctx.on()` 安装，卸载时按栈展开（HMR 安全的根基）。

事件派发模式是公共契约的一部分（cordis-primer.md:19-24）：

| 模式 | 等待? | 顺序 | 返回值 |
|---|---|---|---|
| `emit` | 否 | 注册序观察 | 无 |
| `waterfall` | 否 | 注册序**环绕中间件**（必须 `next()` 委托，不调即短路） | 有 |
| `parallel` | 是 | 并行 | 无 |
| `serial` | 是 | 注册序 | 有 |

### 1.3 架构地图：profile → bundle → patch → 插件树

（来源：`docs/architecture.md` + `apps/cli/README.md` + `packages/README.md`）

- **运行的 dsh = 启动时按有序层叠组装出的一棵插件树**。**profile** 是 Harness home 里的命名组合（`web`/`headless` 为出厂模板）；**bundle** 是"Cordis 配置行 + 它挂载的代码"的发行格式（`package.json` 的 `dsh.bundle` 字段指向 patch 文件），`dsh-base` 是所有 profile 的第一层（模型适配器、工具、持久化、沙箱与审批策略、settings、credentials、telemetry），`dsh-web-app`/`dsh-headless` 各自追加。
- **补丁序**：空根 → 各 bundle 按 profile 列序 → profile 的 `cordis.patch.yml` → home 级 patch → `--patch` overlay。patch 按 id 整行替换或插入新行。`dsh --profile web --dump-config` 可打印实际启动树——**任何一行都能被用户 patch 掉**（architecture.md:29-35）。
- **无特权核心**："没有可打补丁的特权核心；你在别的插件旁边挂一个插件就是在扩展 dsh"（architecture.md:13）。连 agent loop 本身都是插件（`ctx.agentLoop`），README 明言 "Plugins, not loop changes"——新行为必须落在文档化扩展点上（AGENTS.md）。

**核心包七柱**（architecture.md:43-51）：

| 包 | 职责 | ctx key |
|---|---|---|
| `core/session` | append-only `SessionEvent` 日志 + 内存 store | `ctx.sessions` |
| `core/system-prompt` | prompt 分节与工具 schema 组装 | `ctx.systemPrompt` |
| `core/tools` | 带 scope 的工具注册表 + 守卫执行管线 | `ctx.tools` |
| `core/agent` | `Agent` 接口、活注册表、`agent/*` 事件 | `ctx.agents` |
| `core/agent-loop` | 默认驱动器（**全仓唯一具体循环逻辑**） | `ctx.agentLoop` |
| `core/scope` | 每 agent 的 scoped 注册原语 | 库，无 key |
| `llm/llm` | 消息/流词汇 + 适配器缝 | `ctx.llm` |

monorepo 共 **219 个包**（packages/ 下 depth-1 实测 package.json 计数），52 个组：core/api/typert/llm/e2b/shell/subprocess/terminal/fs/lsp/skill/web/compaction/context/subagent/bundle/workflow/todo/plan/preset/guard/self-modification(extensions)/hooks/session/identity/settings/credentials/acp/interaction/boot/sdk/host/client/…每组 README 拥有该组的包/ctx-key 映射（`packages/README.md`）。

**能力缝（capability seam）是全仓最重要的架构词**（architecture.md:100，glossary.md:9）：一个可替换能力 = 三个角色——**Service Definition**（声明接口与 `ctx.<key>`，如 `dsh-shell` 的抽象类 `ShellExecutor`）、**Service Provider**（实现，如 `dsh-bash-local`/`dsh-bash-sandbox`）、**Consumer**（使用，通常是模型面工具，如 `dsh-tool-bash`）。"缝是完整能力，绝不是单个角色；加一个能力意味着设计齐三件套"。generate 的 `docs/capability-seams.md` 有全部 ~60 个 ctx key 的角色表。

**换 provider 即换产品**：fs 与 subprocess provider 共享同一执行世界，把它们指向远程沙箱（如 E2B），Bash、PTY、LSP 一起搬走，无 provider 分叉（architecture.md:102）。这是 seam 设计的直接红利。

### 1.4 Agent 循环：turn/step 两级 + 单一收件箱 + 会话日志事件溯源

（来源：architecture.md "Turn flow"、docs/agent-lifecycle.md、`packages/core/agent-loop/README.md`、`packages/core/session/README.md`）

**词汇表**（glossary.md）：**turn** = 一次排空被接纳输入的会话段；**step** = 一次模型请求 + 其引发的工具执行；**round** = 包住一个 turn 的外层策略迭代（goal round 或 Ralph round）。

循环骨架（architecture.md:67-84）：

```
turn/start
  claim（认领 next-step 输入 + 一条排队消息）
  组装 prompt sections + tool schemas
  → agent/pre-step（waterfall：reject | enter(messages)）
     拒绝/首进改写为空 → 关闭 turn 但不花 step（日志仍记录尝试）
    step/start
    user/message 逐条入日志
    从日志 derive 模型历史
    agent/request → llm/stream → assistant/chunk* → assistant/message
    tool/call* → tools/pre-execute → tools/execute → tools/post-execute → tool/result*
    step/end
    工具欠新请求或有新 next-step 输入 → 再 claim → 下一个 step
  → agent/turn-stopping（serial，无 next() 的终局检查点）
turn/end
```

关键机制：

- **单一 `send()` 原语**：`followup`（next-turn FIFO，唤醒）/`steer`（next-step 收件箱，唤醒）/`inject`（同收件箱，**不**唤醒，等下次唤醒顺带捎上）是同一原语的三档预设（agent-loop README:58）。收件箱每次变更发 `agent/inbox/spliced`，claim 发 `agent/inbox/claimed`。
- **`agent/pre-step` 决定模型看什么**：监听者可改写认领消息或直接拒绝；注入的上下文静静躺在收件箱直到有唤醒消息到来（architecture.md:86-88）。steering 与注入走同一 waterfall。
- **事件三域**（architecture.md:55-60）：**session 事件**（durable 事实，进日志，`session/event` 广播，reload 后存活）；**agent 事件**（`agent/*`，活的：inbox/step/status/request/validation/continuation）；**能力事件**（`fs/*`、`tools/*`、`telemetry/*`，挂策略与适配器）。其中 `agent/pre-step`、`agent/request`、`llm/stream`、三个 `tools/*` 是 waterfall；`agent/turn-stopping` 是 serial。
- **会话日志 = 模型上下文的唯一权威源**：`deriveMessages()` 从日志投影模型历史；原始 `assistant/chunk` 保流式重放与 UI 保真。**"Model-visible ⟺ logged"是运行时断言的不变量**——任何到达模型请求的东西必须可从日志重建，所以新的模型可见输入必须伴随新的 session 事件（architecture.md:92-96）。fork、resume、transcript、telemetry、持久化全部从这条流派生。
- **会话是事件溯源的**：`Session.append()` 快照冻结、单调 seq、turn/step 包络与 tool call/result 配对校验（`core/session/README.md:39`）；**surface 层**（消息产生事件的有序投影）支撑高效派生与压缩重写（replaceGeneration 代数递增）；`ctx.sessions.fork(source, boundary?)` 在事件 seq 边界分叉（session README:17）。持久化后端 JSONL/SQLite 二选一（`session-persistence-jsonl`/`-sqlite`），`chunk-rows.ts` 提供有损压缩行编解码。
- **并行工具调用**：exclusive 调用形成 barrier；parallel-safe 调用进有界滚动池（`maxParallelToolCalls` 默认 10，agent-loop README:52），启动前重新分类；策略、durable 结果、结果上下文保持模型序（agent-loop README:72）。
- **取消语义极尽严苛**：`cancel(cause)` 清 pending（除非 `keepInbox`）+ 协作 abort；abort 后到收敛点之间到达的唤醒输入被 latch 重放（`wakeRequested`，附 Agent Note 2026-08-07）；未派发的模型工具调用补合成 `tool/call` + `ABORTED_BEFORE_DISPATCH` 结果对，保证重放时 call/result 配对完整。
- **错误分层**：provider 终态错误进 `agent/request-error` waterfall（监听者可返回 `{kind:'retry'}`，`dsh-llm-retry` 在此实现精确 backoff）；中间件/工具/其他扩展失败直接抛出关闭当前 turn——**插件失败结束 turn，不结束 loop**（agent-loop README:70）。

**上下文管理（compaction）**——`dsh-compaction-basic`（README 全读）：

- 触发：step 边界压力（`agent/pre-step`，在请求派生**之前**测压）+ canonical 上下文溢出（`agent/request-error`）双通道；单例 `ctx.tokenMeter` 按"已消费日志修订"一次定价整个 envelope（含 system prompt、tools、路由、补全、工具结果、缓冲上下文、steering）。
- 策略：`thresholdRatio` 默认 0.8（按路由模型的实际上下文窗口解析成绝对预算），`retainRatio` 默认 0.16 保真保留近期尾部，按 model 精确覆盖（`modelPolicies`）；先走**免模型工具结果修剪**（`ctx.toolResultPruner` 单节点表面替换）再摘要。
- **KV-cache 意识的摘要调用**：摘要直接 `ctx.llm.stream()` 回放对话自身的 system prompt + tools + 被遮蔽区消息（含图片引用 verbatim），压缩指令作为最后一条 user 消息追加——**复用 provider 的暖前缀缓存而不是打爆它**；DeepSeek 适配器还会打 `x-deepseek-harness-compact: 1` 归因头（compaction-basic README:18）。摘要不收缩即拒绝、有界重试、失败保留原始 provider 错误。替换消息用 `<compacted-summary>` 标签框定，原始摘要存 `compaction/summary` 事件。
- 溢出恢复不需容量元数据：prune → 一次最大化平衡头部削减 → `surface.replaceGeneration` 前进才授权重试。

### 1.5 工具管线与安全审批

**工具执行管线**（`docs/tool-execution-pipeline.md`，生成图 + `packages/core/tools/src/index.ts:137-208` 的事件声明）：

```
tool/call（先记日志再执行）
→ tools/pre-execute（waterfall：hooks、permission、sandbox —— allow/deny/ask）
→ 单调守卫（tools.guard()：deny 或弃权，身份受保护，不可被重排）
→ ctx.approval（ask 时的一次性提问；缺席或不可答 → 拒绝，fail closed）
→ tools/execute（waterfall：超时、重试、metrics —— 环绕 dispatch）
→ 工具体
→ fs/write-intent | fs/edit-intent（仅 tool-fs 变更走 fs 门）
→ tools/post-execute（waterfall：accept/block/replace/add context）
→ 注册表外层规范化（快照 throw → isError）
→ ToolDefinition.finalizeContent（最后的 content-only 不变量）
→ tools/result（同步观察冻结结果）
→ 活跃批次 additionalContexts FIFO（在已记 tool 结果后注入 user/message）
→ tool/result 单一模型面结果
```

管线图的核心理念（tool-execution-pipeline.md:60）：generic pre/post waterfall 承载 hooks 与审批策略，owner 策略必须不可重排的注册为 guard，超时等 around 关注点包 `tools/execute`——**hooks 跨工具族而不把工具耦合到某个策略服务**。

**审批（`dsh-user-approval`）**：channel-neutral 一次性审批缝，`ctx.approval.request()` 返回 `allowed-once`/`rejected`/`cancelled`/`unavailable`；**无应答者或失败即 fail closed**；`ApprovalPolicy` 只有 `ask`/`never` 两档；每次问答落一对 `approval/asked`+`approval/decided` 审计事件（log-only，模型只看最终工具结果）；审批策略变化会往运行时上下文快照里注入一段模型可见的说明文本（user-approval README:21-33）。**没有 allow-always/记忆规则/吊销**——刻意极简（Known Limitations 自认）。

**沙箱（`dsh-sandbox`）**：契约一句话——`ctx.sandbox.confine(argv, policy)` 返回**应该去 spawn 的 argv**（被包裹后受限），外加 backend 的执行完备性与拒绝方言；**无可用 backend 时抛 `SANDBOX_UNAVAILABLE` 拒绝裸跑**（fail closed）。`SandboxMode`：`read-only`/`workspace-write`/`danger-full-access`（仅文件效果维度）；backend：Linux bwrap / Landlock（含自研 `native/node-addon-landlock-run`）、macOS Seatbelt、**Windows ACL restricted-token**。**只做同世界限制**：容器/microVM/远程执行不是这个缝的 backend，而是整组替换 `ctx.shell`/`ctx.fs` 的 provider（sandbox README:11）。policy 随调用走而非随 provider：同一瞬间 bash 在 read-only 下跑、子 agent 的状态目录可写（sandbox README:9）。权限预设 `workspace-write`/`danger-full-access` 一键写穿 sandbox-mode + approval-policy 双旋钮（`permission-presets`）。

**guard 族**（`packages/guard/`）：`repeat-tool-reminder`（重复调用的 advisory 提醒，走 `additionalContexts`）+ `timeout-policy`（部署级每调用截止时间）。loop-hygiene 也是插件不是内核。

### 1.6 插件系统详解："一切皆插件"到底什么意思

**插件的三种形态**（`docs/user/develop/basic/index.md:105-138`）：函数模块（`export const name/inject/Config` + `apply(ctx)`）、对象字面量、`Service` 子类（提供 `ctx.<key>` 服务给他人）。最小插件就是一个带 `apply` 的 TS 模块，经 `cordis.yml` 挂载（绝对路径），`--patch` overlay 即可热载入 Web UI。

**Scope 体系**（glossary.md "agent-scope"）：注册（工具/prompt 节/变量/限制/监听器）要么全局要么属于恰一个 scope key（约定：活 agent 就是自己 scope 的 key）；**shadowing = 最近层同名胜出**——per-agent persona 与 per-agent 工具变体的机制；`tools.restrict()` 交集过滤全局工具集，被滤掉的工具在 prompt 与执行两侧同样消失（与不存在不可区分）；**lineage 是数据不是结构**（`parentSession`、`delegationDepth`），scope 不向子 agent 继承——两层扁平。`CreateAgentOptions.setup` 是"setup window"：agent 对象已建、未发布、未跑第一步，创作者在此组装该 agent 的 scoped 世界。

**模型面工具全家桶**（从 capability-seams 表与包目录归纳）：bash/pwsh（本地/沙箱/persistent 三态）、terminal（PTY 持久会话）、fs（read/write/edit/搜索 + str-replace-editor）、web（search: deepseek/exa/perplexity + fetch:http）、lsp（恰四个规范化操作，无协议逃生口）、skill、todo、ask-user、plan、goal、jobs（后台 bash/PTY/子 agent 的统一 `job_*` 控制器）、subagent、subagent-control、session-query、workflow、ralph、cordis（自省五件套）、run_code（Code Mode）。

**几个特别值得 work4ai 注意的子系统**：

1. **Code Mode / `run_code`**（`packages/core/tools/src/code-mode.ts` 32KB + `dsh-code-runtime`）：把"模型直接调 N 个工具"坍缩成"模型写一个程序，程序里通过生成的 SDK 调工具"——`RUN_CODE` 是唯一可直接调用的工具，其余工具调用一律在程序内发生（code-mode.ts:58 的模型面声明）。SDK 按语言渲染（`renderToolsSdk` TS / `renderToolsSdkPy` Python，tools/src/index.ts:60-63）；运行时契约 = "对一组 host 提供的 async bindings 跑一段模型写的程序，报告 `{value, logs, error}`"（code-runtime README:5）；程序被当作**敌对 peer**（恶意绑定名、畸形流量不得崩宿主）；目前唯一 backend 是 Node worker-thread，container 是声明值无实现。子调用走同一条工具管线并记 `tool/code-dispatch`。这是"tool use vs code as action"路线的工业级实现样本。

2. **MCP client**（`packages/mcp/mcp-client`）：每服务器一实例；工具注册名 `mcp__<serverName>__<rawName>`——**刻意与 Claude Code/Codex 同形**（README:32）；stdio + streamable-http 两种传输；名称归一到 DeepSeek 函数名契约（64 字符），冲突时附 `(serverName, rawName)` 的确定性 12 位 hex 哈希防坍缩；断线重连带预算（指数退避封顶 + 连续失败 10 次永弃 + 存活超 maxDelay 重置预算——"偶尔崩的服务器无限恢复，崩循环的终会耗尽"）；list_changed 增量重同步整代替换。**只桥接 tools，Resources/Prompts 明确缓办**。

3. **Hook 桥**（`packages/hooks/`）：`dsh-hooks-claude-code` 跑用户已有 Claude Code `hooks.json` 的 command-hook 子集，映射到 dsh 的类型化拦截点（SessionStart→`agent/session-start`、PreToolUse→`tools/pre-execute`、Stop→`agent/turn-stopping` 经 `steer()` 强制再加一步……完整映射表见 hooks-claude-code README:37-46）；`dsh-hooks-codex` 同理。README:7 说得很直白：原生 cordis 插件能做这一切且更强，**桥存在的唯一理由是兼容存量 CC 生态**。

4. **子 agent 缝**（`packages/subagent/`）：一个 `ctx.subagents` API，六个 provider——`spawn-in-process`（全新子会话）、`fork-in-process`（继承父上下文）、`subagent-acp`、`subagent-codex`、**`subagent-claude-code`**、`subagent-dsh-sdk`——**dsh 可以把 Codex 和 Claude Code 当作自己的子 agent 后端进程来 spawn**（经 `ctx.subprocess`）。除 one-shot 外还有 **continuable children**：durable Session + 至多一个进程内 Activation（驻留纪元），`followup` 追加对话、`interrupt` 按 durable 父地址打断、结算通知无条件送达（token 上限/模型失败/取消这些"孩子来不及说话"的结局恰恰最需要交代，subagent README:81）。**委托策略**：子 agent 的审批策略在委托边界被钉死为 `never`、沙箱范围快照继承——"被委托的孩子只在被继承的沙箱范围内行动，任何 ask 都被确定性拒绝而不是等一个没人在看的提示"（subagent README:61）。

5. **Ralph 循环**（`packages/workflow/tool-ralph`）：`ralph({objective, maxRounds?})` 给一串**全新子 agent** 依次下发同一不可变目标；孩子只收到目标 + 当前轮次 + 上一轮的结构化 handoff（status/summary/evidence/next-steps/blocker，≤16384 字符），**共享工作区是唯一长期记忆**，父对话与既往子会话不播种；默认 `maxRounds` 256；完成/阻塞是 worker 自报而非独立认证（模型面 guidance 原话）。它示范了"专业化编排策略 = 普通 plugin over workflowEngine + subagents，而非 agent-loop 的新模式"（README:5）。同一会话内的长目标另有独立的 goal 域（revisioned 阶段状态 + goal round 上限 + process-local 的 goal activation 需人类经 `/goal` 重新武装——resume/fork 不自动续跑）。

6. **自修改工具集**（`packages/extensions/tool-cordis`）：五个模型面工具 `cordis_inspect/define/run/stop/undefine`——**agent 检查并挂载自己的插件**：host half 在 vm 沙箱里跑（Node globals 缺席或重定向到 `ctx.fs`/`ctx.web` 等 Cordis 服务），browser half 经广播注入每个打开的网页；动态包只在进程内存里、session-scoped、重启即逝、不能自动转正——要保留就请 agent 走正常开发流程写一个真插件（README:19）。信任立场诚实："沙箱隔离 globals 但不是安全边界，把它当 bash 权限对待"（README:23）。API 报告来自 AST 生成的编译期目录与活服务 store 的交集——**反射数据忠于代码，报告必须对模型有用**是两条独立的判断（README:41-46）。

7. **Skill 系统**（`packages/skill/`）：纯 provider 注册表（本地实现 `skill-filesystem`），host+per-scope 分层；`SkillSummary.invocation` 是**四象限显式策略**（modelInvocable/userInvocable 独立布尔）——同一发现结果可同时服务模型工具、人类命令与内部调用者而不混目录；`renderSkillContent()` 渲染 canonical `<skill_content>` 块，`skill` 工具结果与用户显式手势注入**共用同一形状**（skill README:44）；runtime skills rank 250：项目 provider 可覆盖它，它覆盖本地 provider。

8. **流式与表现层**：`ctx.llm` 的 stream vocabulary + `llm/stream` waterfall；**工具的 UI 渲染意图是一等设计维度**（`generic`/`terminal`/`diff`/`locations`，AGENTS.md："A tool's UI render intent is part of its design, decided up front"；presentation 是 args 的纯函数）。Web UI 是 Vite/React 浏览器半 + node:http 宿主半（`webserver`/`modules`/`hmr`/`connection`/四十余 `ui-*` 插件），插件可带浏览器 half 注册 UI slot。

### 1.7 与主流 harness 的对比定位

仓库内可直接取证的对比锚点：

| 维度 | dsh 的选择 | 与 Claude Code / Codex / opencode / gemini-cli 的关系 |
|---|---|---|
| 产品形态 | **Web UI 优先**（`dsh web`），CLI/headless/Python SDK/ACP/JSON-RPC 全都从同一插件树派生 | CC/Codex/opencode 以终端优先；dsh 反向：终端只是启动器之一 |
| 扩展模型 | **一切皆插件**（Cordis DI + 类型化事件 + 可逆 effect），无特权核心 | CC 是 hooks+skills+MCP+plugins 的分层但核心闭源；opencode 插件+Svelte 客户端；dsh 把"内核"本身也做成可 patch 的行 |
| 生态兼容 | 主动兼容：CC hooks 桥、Codex hooks 桥、MCP 同名规范 `mcp__server__tool`、**把 Claude Code/Codex 当子 agent provider 驱动**、ACP 服务器 | 不重造生态而是**双向寄生**：吃掉 CC 的 hook/skill 存量，同时把自己变成其他 harness 的模型后端与宿主 |
| 模型接入 | DeepSeek 默认 + 目录化多 provider（Anthropic/OpenAI/Bedrock/Vertex/Azure/Codex）+ 任意 OpenAI 兼容 | 与 gemini-cli（Google 系）同款"自家中立化"策略：官方 harness 但模型开放 |
| 沙箱 | bwrap/Landlock/Seatbelt/Windows ACL 四平台 + fail-closed + E2B 远程 POC（整组换 fs/subprocess provider） | CC 原生沙箱较弱（靠权限模式）；Codex 有 OS 级沙箱；dsh 的差异点是 **policy 随调用走 + 拒绝方言结构化** |
| 会话 | 事件溯源日志为唯一权威，"model-visible ⟺ logged"运行时断言 | 多数 harness 的 transcript 是副产品；dsh 把它升格为架构公理 |
| 文档工程 | 双语文档 + 生成目录（freshness-gated）+ 文档字数预算 + Agent Notes + postmortems | 业界罕见的文档即代码纪律（见 1.8） |

一句话定位：**dsh = "Cordis 化的 Claude Code"——用 Koishi 系插件框架把 Claude Code 已验证的 harness 形态（turn/step、hooks、MCP、skills、subagents、plan/todo、沙箱审批）重构为全插件架构，并以 Web UI 与 Python SDK 为一等入口**。它对 harness 竞争的回答不是"更多功能"而是"更彻底的可组合性 + 对存量生态的双向兼容"。

### 1.8 设计模式清单（可直接入 Agent架构模式参考）

1. **依赖注入服务仓库**：`ctx.<key>` 认领 + `inject` 声明等待（加载顺序隐式化）。
2. **能力缝三角色**（Service Definition / Provider / Consumer）：接口、实现、消费分包，"换 provider 即换产品"。
3. **注册皆可逆 effect**：`ctx.effect()`/`ctx.on()` 返回 disposer，卸载按栈展开 → HMR/热重载安全。
4. **四种事件派发模式**（emit/waterfall/parallel/serial）作为公共契约，waterfall = 环绕中间件（must-`next()`，短路即决策）。
5. **事件溯源会话**：append-only 事实日志 + surface 投影 + deriveMessages，fork/resume/telemetry 全派生。
6. **"Model-visible ⟺ logged" 不变量**：模型上下文可重建性成为运行时断言而非文档承诺。
7. **管线分层策略**：extensible pre/post waterfall（hooks/审批）+ 单调 owner guard（不可重排）+ around waterfall（超时/重试）+ finalizeContent + 冻结 result 观察——四段五关。
8. **fail-closed 安全缺省**：审批缺席即拒、沙箱不可用即拒（绝不裸跑）。
9. **Scope + shadowing**：全局/单 agent 两层扁平 scope，同名最近层胜出，lineage 走数据。
10. **KV-cache 意识工程**：每个包 README 强制"Model Experience"三段式（模型看到什么/Token 效应/**KV Cache 效应**）；compaction 摘要刻意回放前缀复用暖缓存。
11. **一次性审批 + 审计事件对**：allowed-once 词汇表 + asked/decided 落日志 + 策略变化注入模型可见快照。
12. **委托策略钉死**：子 agent 审批钉 `never`、沙箱快照继承——委托边界即权限边界。
13. **Code Mode**：工具面坍缩为单一 `run_code` + 生成的 SDK，敌对程序契约。
14. **确定性命名**：MCP 工具名 = 纯函数(serverName, rawName) + 哈希防坍缩。
15. **profile/bundle/patch 层叠组合**：产品 = 配置行的有序补丁叠加，`--dump-config` 可见即可改。
16. **自省式扩展**：agent 经 `cordis_inspect/define/run` 挂载自己的插件（进程内存、session-scoped、可弃）。
17. **新鲜 agent 循环（Ralph）作为插件**：fresh-agent 迭代 + 结构化 handoff + 工作区即记忆，不改内核。
18. **结算通知无条件送达**：子 agent 的失败终局由运行时（而非孩子自己）向父交代。

### 1.9 工程实践（monorepo/测试/CI/发布/文档）

- **工具链**：pnpm workspace（node ^22.19 || >=24）+ tsc（lib/types）+ tsdown 打包运行时 + vitest（unit/e2e/snapshot/web/stress 五套配置）+ oxlint（两套 rc）+ jscpd 跨文件克隆检测 + knip 死代码 + publint + lefthook git hooks + tsx ESM-only 源码启动（`node --import tsx/esm`）。CI 是 **GitLab CI**（.gitlab-ci.yml）。
- **测试纪律**（docs/testing.md + AGENTS.md）：`test:coverage` 是 CI 门——**packages/*/*/src 逐文件 100% 覆盖**；`test:e2e` 真 API、无 `DEEPSEEK_API_KEY` 自跳过；**`test:snapshot` 无密钥**：ACP/headless 回放对拍期望输出；"每个非平凡模型/用户可见行为变更，同一 PR 内必须经真实可运行例子补一条 keyless snapshot——包测试、e2e 断言、mock fixture 都不能替代组装后的应用 transcript"。另有 REAL-composition 测试要求（产品可见插件必须经 Loader 启真 cordis.yml，禁止手搓 `ctx.plugin()` 充数）。
- **文档即代码**（docs/AGENTS.md 全读）：文档分 8 层（根 AGENTS.md 站令 / 子树 AGENTS.md / architecture.md 有序地图 / subsystems 类型参考 / **Agent Notes** 决策记录 / postmortems 事故叙事 / cookbook 步骤书 / 包 README 契约），**one home per fact**；**字数预算硬门**（`verify-doc-budgets`：根 AGENTS.md ≤1600 词、architecture.md ≤1800、子树 ≤600…）；生成目录（tool-catalog/config-catalog/persistence-catalog/module-graph/event-map/capability-seams）从源码再生且 CI freshness-gated；双语文档配对工作流（i18n/）；"slop checklist" 打击重复、叙事史、状态注记、推理誊写。**这套文档治理本身就是 agent 时代的工程发明**——仓库甚至建议"用 agent 探索本代码库"（architecture.md:7），根目录有 `.agents/skills/`（dsh-pre-push-checks、dsh-prose-standard、dsh-doc-standards）与 `.claude/`，AGENTS.md 面向 agent 写（"For agents, follow AGENTS.md"）。
- **决策记录**：`.agents/notes/implemented/` 按 architecture/feature/process/bug-fix 分类，"非平凡变更必须同 PR 附 Agent Note"；已实施 note 用现在时描述现实、禁止 spec-speak；postmortem 单独一层（如 `0001-acp-default-export-drops-inject.md`——默认导出会吞掉函数插件 namespace 的血泪教训，直接固化成包规则）。
- **发布**：全部包 `@deepseek-ai/dsh-*` 私有域；vendored 包 rescoped 私有；Python 侧打包捆绑运行时二进制（`deepseek-harness-runtime-bin`）。
- **其他亮点门**：`pnpm run duplication`（跨文件 TS 克隆检测）、`verify-cordis-config`（Raw/Web cordis.yml bare 插件必须在 resolver manifest dependencies 里）、`verify-vendored-links`、workspace constraints、每包 `./invariant` 伴生（"Every package owns ./invariant"——包级运行时不变量注册表）。

### 1.10 work4ai 可吸收的工程决策

1. **"一切皆插件"不是口号而是三层兑现**：框架层（Cordis vendor）、组合层（profile/bundle/patch）、扩展层（事件+scope）。讲透Agent 可用它做"harness 可组合性谱系"的极端样本：CC（闭源核+开放钩子）↔ opencode（插件+客户端）↔ dsh（全插件含内核）。
2. **"Model-visible ⟺ logged"** 应进 prompt工程手册/orchestration 精华笔记：可重建的模型上下文是可回放、可分叉、可审计的前提——比"记忆系统"更底层的公理。
3. **Model Experience 三段式**（模型看到什么/Token 效应/KV Cache 效应）是每个模型面组件的文档模板，值得作为 work4ai 评审 agent 组件的 checklist。
4. **compaction 的暖缓存摘要**（回放前缀 + 末位追加指令）是讲透Prompt 可引用的具体 KV-cache 技巧；`<compacted-summary>` 框定与"摘要不收缩即失败"也值得收录。
5. **委托即权限边界**（子 agent 审批钉 never + 沙箱快照）适合 Agent编排案例 的安全小节。
6. **Ralph 循环**：fresh-agent + 结构化 handoff + 工作区即记忆的工业化参数（256 轮、16K handoff、worker 自报非独立认证）——讲透学习型Agent 的"无记忆迭代"对照组。
7. **dsh 把 Claude Code/Codex 当子 agent provider**——"harness 吃 harness"是 2026 生态嵌套信号，直接支撑"harness 是新共识词"的论点。
8. **文档治理**（tier taxonomy + 字数预算 + 生成目录 freshness 门 + Agent Notes + slop checklist）可整段吸收进 work4ai 的知识卡治理（对照"孤儿文件 = 死亡内容"宪法，dsh 的"one home per fact"是同一哲学的工程化）。
9. **keyless snapshot 测试**：模型行为变更的回归测试不一定要 API key——录放对拍。skills 工程手册可引用。
10. **vendor 而非依赖**：把关键框架层钉进仓库 + 18 条修改日志全审计——供应链工程范本。

---

## 2. awesome-deepseek-integration：DeepSeek API 的需求侧地图

**仓库**：deepseek-ai/awesome-deepseek-integration（39k 星，简报数字），五语 README（en/cn/zh-tw/ja/es），`docs/` 下 93 个项目文件夹（各带 logo + 说明）。定位："Integrate the DeepSeek API into popular softwares"（README.md:9）。

**分类学与条目数**（自动计数，约 250 条，20 类）：

| 类别 | 约数 | 类别 | 约数 |
|---|---|---|---|
| Applications（聊天/桌面客户端） | ~123（含少量计数误差） | VS Code Extensions | 9 |
| Others | 36 | JetBrains Extensions | 6 |
| Browser Extensions | 22 | IM Application Plugins（微信/钉钉/飞书系） | 6 |
| AI Agent frameworks | 18 | RAG frameworks | 6 |
| neovim Extensions | 4 | Synthetic data curation | 3 |
| Office Addin | 3 | Visual Studio Extensions | 3 |
| Native AI Code Editor | 3 | Emacs | 2 |
| Security / Providers / Discord Bots / FHE / Solana / Data AI | 各 1-2 | | |

**著名条目抽样**（README 实读）：聊天客户端（OpenRouter、Chatbox、ChatGPT-Next-Web、Cherry Studio、DeepChat、DingTalk、ChatDOC、SwiftChat[aws-samples]、4EVERChat）；agent 框架（**smolagents**[HF]、**Upsonic**、anda[TEE 链上 agent]、Daydreams、rig、Just-Agents、YoMo、SuperAgentX、BotSharp、dbgpt、agentUniverse、eino[CloudWeGo]）；RAG（**ragflow**、Casibase、huixianghou）；编码（**cline**、**continue**、cursor、avante.nvim/codecompanion.nvim/llm.nvim/minuet-ai.nvim、refact）；浏览器/翻译（immersive translate、Relingo、沉浸式阅读指南）；测试（promptfoo）；链上（solana-agent-kit）；隐私（fhe.mind-network——全同态加密跑 DeepSeek）；Zotero/SiYuan 等知识管理。

**生态需求侧信号**：
1. **长尾在客户端不在框架**：Applications 一类独大（约半数条目），说明 DeepSeek API 的最大需求面是"廉价强模型塞进现有聊天壳"。
2. **编码工具集成密度高**：编辑器四强（VS Code/JetBrains/neovim/Visual Studio）+ 浏览器 + 原生编辑器共 ~45 条——开发者是第一批规模化用户，与后来 dsh 的出现（DeepSeek 自己下场做 harness）形成"需求先行、官方跟进"的叙事线。
3. **中国生态权重高**：钉钉、飞书、微信 RPA、openEuler Intelligence、OpenXLab/书生、UOS AI、腾讯系条目密集——DeepSeek 的集成需求有强烈的国产软件栈底色。
4. **长尾奇特长**：FHE 推理、Solana agent、watchOS 客户端、RPA 客服——"API 便宜到什么都能试"的信号。

---

## 3. awesome-deepseek-agent：DeepSeek 作为 harness 世界的模型后端

**仓库**：deepseek-ai/awesome-deepseek-agent（5.8k 星，简报数字），双语（en/zh-CN），定位是"**把 DeepSeek 模型接进流行 AI agent 与编码助手工具的指南清单**"——每条是安装/配置/首跑的 walkthrough（README.md:7-9）。**注意：它不是 agent 框架清单，而是"DeepSeek 模型 × 第三方 harness"的接线手册**，与 awesome-deepseek-integration 的泛软件清单互补。

**22 个工具指南**（README.md:16-40 表格 + docs/ 实查）：

- 终端编码 agent：**Claude Code**、**Codex**（OpenAI）、**OpenCode**、Crush、Qwen Code（阿里）、Kilo Code、Copilot CLI、Langcli（CC 兼容）、Oh My Pi（Pi fork）、Pi、Reasonix（DeepSeek 原生 cache-first）、DeepSeek-TUI（Rust，Codex 式架构+沙箱+MCP+1M 上下文）、Deep Code（V4 深度思考+Agent Skills）、deepseek-droid（docs 里有但未列入主表）
- 编辑器/平台：Cline、GitHub Copilot、WorkBuddy/CodeBuddy、Cherry Studio、LobeHub（"Chief Agent Operator"，把 agent 组织成 7×24 值班团队）
- 通用 agent：AstrBot、nanobot、OpenClaw（接飞书/微信）、Hermes（Nous Research 自改进 agent）

**关键信号**：
1. **README 第一句就点名 "DeepSeek-V4-Pro / DeepSeek-V4-Flash"**（README.md:9）——V4 双型号命名（Pro/Flash）+ Python SDK 示例里的 `deepseek-v4-flash`（dsh python-sdk.md:36）相互印证，是 2026 模型线的可靠命名证据。
2. **官方为 Claude Code/Codex/opencode 写接入教程**——DeepSeek 明确认可"自家模型跑在别人 harness 里"的路线，与 dsh（自家 harness）并行不悖：**模型公司同时押注"被集成"与"自建壳"两条腿**。
3. 指南粒度到 `claudeCode.disableLoginPrompt` 这种具体设置项（docs/claude_code.md），说明需求量足够大、值得官方维护逐工具手册。

---

## 4. awesome-deepseek-coder：2023 时代的化石层

**仓库**：deepseek-ai/awesome-deepseek-coder（807 星，简报数字），中英双语，**内容停留在 DeepSeek Coder v1（2023-11 发布期）**，无后续更新迹象——与上面两仓的活跃形成鲜明断层。

**内容结构**（README.md 全读）：
- 官方模型：1.3B / 5.7bmqa / 6.7B / 33B 四档 base+instruct（README.md:18-23）；
- 社区微调：**Magicoder**（ise-uiuc）、**WizardCoder-33B-V1.1**（WizardLM，改用 DS-33B 底座）、**OpenCodeInterpreter**（m-a-p）、**CodeFuse-DeepSeek-33B**、openbuddy 系（README.md:27-33）——这是"DeepSeek Coder 作为微调底座"一代的化石记录；
- 量化：TheBloke 全家桶 AWQ/GGUF/GPTQ；
- Copilot 侧：**Tabby**（其排行榜显示 DS-6.7B 补全第一）、refact、AutoDev（JetBrains）。

**信号**：证明 DeepSeek 在 coder 时代的开源策略（放权重+社区微调+自托管补全）就已成型，-awesome-coder 是该策略的墓碑，而 V2/V3/R1 之后的重心已转向 API 生态（integration 仓）与 harness（dsh）。

---

## 5. 对 work4ai 的输入映射

| work4ai 单元 | 本簇可输入 |
|---|---|
| **讲透Agent** | dsh 是"harness 形态"的最新全插件样本：turn/step/round 三级词汇、事件三域、单一收件箱（followup/steer/inject）、" Plugins, not loop changes"扩展哲学；§1.4/1.5 可直接做"现代 harness 内核解剖"一章的实例 |
| **讲透学习型Agent** | Ralph 循环（fresh-agent 无对话播种 + 结构化 handoff + 工作区即记忆 + 轮次上限）、goal 域（revisioned 目标状态 + 人类重新武装的 activation）、自修改工具集（cordis_define 五件套）——三个"学习/迭代"机制的正反面教材 |
| **Agent架构模式参考** | §1.8 十八条设计模式清单（DI 服务仓库、能力缝三角色、可逆 effect、四派发模式、事件溯源、管线四段五关、fail-closed、scope+shadowing、KV-cache 文档化…）可整节收录，每条都有 dsh 文件路径锚点 |
| **Agent框架案例** | deepseek-harness 深读卡（104k 星/TS/219 包/全插件），对照已有 Claude Code/opencode 案例；三个 awesome 仓做生态位小卡 |
| **Agent编排案例** | subagent 六 provider（含驱动 Claude Code/Codex）、continuable children + Activation 驻留、workflow worker-thread 引擎、jobs 后台注册表、Ralph——编排原语的工业实现集 |
| **prompt工程手册 / 讲透Prompt** | system-prompt 分节组装（prompt section 注册表 + `system-prompt/assemble` waterfall）；approval policy 的模型可见快照文本；compaction 的 `<compacted-summary>` 框定与暖缓存摘要技巧；"模型面契约从模型视角书写"原则 |
| **skills工程手册** | dsh-skill 的 provider 注册表 + 四象限 invocation policy + `<skill_content>` canonical 渲染 + rank 分层（runtime 250）——与 Claude skills 对照的第二个工业级 skill 系统样本 |
| **orchestration精华笔记** | 12-factor 对照：errors-as-events（request-error waterfall）、显式状态机（Activation 三态）、上下文管理（inbox + inject）、幂等（确定性命名）；"结算通知无条件送达"是新的可靠性模式 |
| **用例库** | 新增深读卡：deepseek-harness（G 簇主卡）；用例坐标建议挂 DSH 生态观测锚点 |
| **视角库** | "harness 是 2026 共识词"的又一实锤：DeepSeek 官方 README 直接以 agent harness 自我定义（README.md:5），且 model 公司下场做 harness = 价值链垂直整合视角的案例 |

---

## 6. 附：关键文件路径速查

- 架构总图：`deepseek-harness/docs/architecture.md`（≤1800 词的自律范本）
- Cordis 入门：`docs/cordis-primer.md`；vendoring：`vendor/README.md`（18 条修改日志）
- 循环时序：`docs/agent-lifecycle.md`；工具管线：`docs/tool-execution-pipeline.md`；能力缝总表：`docs/capability-seams.md`；词汇表：`docs/glossary.md`
- 源码：`packages/core/agent-loop/src/{index,agent,tool-calls}.ts`、`packages/core/tools/src/{index,code-mode,schema,presentation}.ts`、`packages/core/session/src/{index,surface,chunk-rows}.ts`
- 词汇化安全：`packages/sandbox/sandbox/README.md`、`packages/interaction/user-approval/README.md`
- 插件教程：`docs/user/develop/basic/{index,tool,config}.md`；模型配置：`docs/user/guide/providers.md`；Python：`docs/user/guide/python-sdk.md`
- awesome 三仓：`awesome-deepseek-integration/README.md`（20 类）、`awesome-deepseek-agent/README.md`（22 指南）+ `docs/*.md`、`awesome-deepseek-coder/README.md`（2023 化石）
