# 01 · DeepWiki 对照与增补

> 来源：https://deepwiki.com/deepseek-ai/deepseek-harness （Devon 自动生成 wiki，索引于 2026-08-13，commit `47f94385`——与本案例笔记钉版一致）
> 本篇定位：① DeepWiki 10 章 → 本案例笔记的映射；② DeepWiki 提供、而本案例首版笔记未覆盖的**增补事实**；③ DeepWiki 的错误/缺口记录。

## 1. 章节映射

| DeepWiki 章节 | 对应本案例笔记 | 增补程度 |
|---|---|---|
| 1 Overview / 1.1 Setup / 1.2 Monorepo | `00-overview/01-定位与全景` | 新增构建面/门禁细节（§2.1） |
| 2 Core / 2.1 Cordis / 2.2 Composition / 2.3 Events | `02-capability-seams/01+02`、`04-assembly/01` | 新增 isolate realm、fiber 加固细节 |
| 3 Agent / 3.1 Loop / 3.2 Tools / 3.3 Session / 3.4 Subagent / 3.5 LLM | `01-core-runtime/01+02+03`、`04-assembly/02` | EpochHeader、Code Mode、subagent 细节、LLM 错误码（§2.2-2.4） |
| 4 Execution / 4.1 fs / 4.2 shell / 4.3 sandbox | `02-capability-seams/01`、`03-trust/01` | 常量与边界矩阵（§2.5） |
| 5 API / 5.1 apiproxy / 5.2 Typert / 5.3 client | `04-assembly/01` | RPC 方法表、客户端细节（§2.6） |
| 6 Web UI / 6.1-6.4 | `04-assembly/01`（Web 节） | 大量 UI 细节（§2.7）——本案例未深读 UI，此节为首证 |
| 7 Extensions / 7.1-7.4 | `04-assembly/02`、`02-capability-seams/02` | hooks/skills/goal/todo/schedule 细节（§2.8） |
| 8 Testing / 8.1-8.3 | `05-lessons`（工程文化节） | 测试基础设施全景（§2.9）——首证 |
| 9 Docs / 9.1-9.2 | `05-lessons` | i18n 三件套机制（§2.10） |
| 10 Glossary | `00-overview/01` | 术语表全文收录（§3） |

## 2. 增补事实（本案例首版笔记未覆盖）

### 2.1 构建与门禁（DeepWiki 1.1/8.3）

- **双聚合构建面**：Host（`tsconfig.host.json`：Node/agent/tools）与 Client（`tsconfig.client.json`：浏览器/UI）两个隔离 TS 程序——避免 Cordis `Context` 声明合并冲突。构建序：host tsc → tsdown **生成 Typert RPC 契约** → client tsc 消费生成的类型 → client bundle。
- CI job 拓扑（ci.yml）：`node-24`（静态门禁）、`node-24-coverage`（100% per-file，`DSH_COVERAGE_MAX_WORKERS` 防 OOM）、`node-24-consumers`（publint）、`windows`（**Linux+Wine 阻塞门**）、`windows-native`（Windows 2025 非阻塞观察：NTFS/DACL/ConPTY）、`all-checks-passed` 聚合。
- **双 Windows 策略** + 失败切换 runbook：repo 变量 `DSH_CI_FAILOVER_LINUX/WINDOWS` 一键切自托管池（64/96 核）。自托管待命演练随每次 master push 跑、豁免于 cancel-in-progress。
- CI workflow 本身有单测（`scripts/ci-workflow.spec.ts`）。

### 2.2 Agent loop 增补（3.1）

- 三相位：`idle / maintenance / running`；维护期间到来的唤醒**闩锁**（`wakeRequested`）并在收敛后重放。
- **EpochHeader**：每个模型请求前置锚定 LLM 配置（model/provider/maxTokens）入日志；配置变更 ⇒ 记新 header——`deriveMessages()` 可精确重建"模型当时看到的上下文"。这是"model-visible⟺logged"的时间维实现。
- 发布事务：未发布的私有 session+agent → 可选 `AgentSetup` → 进注册表（id 冲突即回滚）→ `agent/created` → 启动驱动。

### 2.3 工具与 Code Mode（3.2）

- `tools.mode = native | code | both`：code 模式把全部工具投影成类型安全 SDK 嵌入系统提示（TS `renderToolsSdk` / Python `renderToolsSdkPy` 生成 `TypedDict`），模型经保留的 `run_code` 传输工具**写代码调工具**而非直接调用。
- 并行条件：工具声明 `isConcurrencySafe(args)` 为真才并行，否则独占（默认）。
- 工具目录（`docs/tool-catalog.md`）是**真的启动全部插件调 `ctx.tools.schemas()` 生成**的。
- 快照 fixture 按模式：`code-mode-turn / both-mode-turn / text-turn / pty-tools / lsp-definition / web-fetch …`。

### 2.4 Subagent 与 LLM（3.4/3.5）

- subagent 两模式：**one-shot**（单轮，返回 `SubagentRun {id, result, dispose}`）与 **continuable**（跨轮持久会话，`SubagentContinuationManager` 管理 Activation；冷恢复从持久日志重建）。
- 深度控制：`delegationDepth` 经会话血统追踪，`SubagentDepthError`，**默认 maxDepth ≈ 3**。
- 子→父汇报策略 `quiet`（注入上下文）| `wakeup`（触发父新轮）。ACP teardown 阶梯：`stdin.end() → SIGTERM → SIGKILL`。
- LLM 错误码规范化：HTTP 401/403→`AUTH`、429→`RATE_LIMIT`、400 上下文超限→`CONTEXT_WINDOW_EXCEEDED`、另有 `INVALID_CREDENTIAL/TIMEOUT/UNKNOWN_MODEL`。
- DeepSeek 适配器：单路由 `deepseek-official`；自动注入 `x-deepseek-harness-user-id/session-id` 遥测头；**空闲看门狗默认 5 分钟**（无 chunk 即中止）。推理档词表 `off/high/max` 映射各 provider 方言。

### 2.5 执行环境常量（4.x）

- fs：read 默认 **2000 行 / 51200 字节**，>10 MiB 流式；`FsVersion = dev:ino:size:mtime:ctime`；原子写 = staging 临时文件 + `fsync` + Windows `ReplaceFileW`（DACL 随拷）；**读后写护栏**——`fs/observed` 事件 → `fs/write-intent` 瀑布 → 未读先写抛 `FS_NOT_OBSERVED`。
- subprocess：输出收集 64KB 内存尾 + 溢出文件；`terminateForHostExit` 在 Node exit 同步杀全树。
- 沙箱边界矩阵：Linux 写=full/partial、读限制✅、网络限制✅；**Windows 读限制❌、网络限制❌**；升级 = 拒绝签名匹配 → 审批暂停 → **恰好一次**更宽策略重试。

### 2.6 API 层（5.x）

- 遗留 apiproxy RPC 方法表：`session.{list,create,history,prompt,rename,fork,models,selectModel,updateQueue,cancel}`、`host.{describe,pickDirectory,listDirectory,openPath}`、`events.{mux,host}`；Zod 双重校验（信封+载荷）；`GET /api/session.export` 流式 ZIP（先 flush）。
- Typert 增补：`@RemoteScope`（授权作用域，此前只记了 `@Remote`）；分析器只接受返回 `Promise`/`AsyncIterable` 的方法，后者→SSE 流；缺生成制品 CLI 直接启动失败。
- 客户端：历史分页默认 50 条/页；seq 空洞 → `stitching` 状态 + `liveBuffer` 缓冲直至补页；投影存储 **higher-seq-wins**；空会话复用语义（`SessionSummary.blank`，首 prompt 才翻 false）。

### 2.7 Web UI（6.x，本案例首证）

- 关键 slot 名：`conversation.view`（ChatView/Trajectory/Artifacts 占据）、`conversation.chat.node`（按 `ChatNodeKind` keyed 渲染）、`conversation.composer`（InputBar；审批时被 ApprovalPanel 接管）、`conversation.session.header.actions`、`sidebar.settings`、`settings.onboarding`（单步升序、可见步拥有 app-root `inert`）。
- 侧栏状态点语义：**amber=审批/计划评审待决、blue=运行中、green=未选中时完成**；子代理会话从侧栏过滤（经父会话页访问）。
- Trajectory 表：>100 行虚拟化；单元格类型 `system/user/context/compacted/message/tool/subtool`。
- 预设四内置：**Standard / Code / Minimal / Creator**（Creator 用于运行时巡检地创作 preset）；会话开始后 preset 钉死。
- 遥测默认 `DISABLED`，opt-in `FEEDBACK_ONLY|FULL`，且从 env `DSH_TELEMETRY_MODE` **在执行前冻结**——项目代码不能自我授权。

### 2.8 扩展集成（7.x）

- hooks 五拦截点：`SessionStart→agent/session-start`、`UserPromptSubmit→agent/pre-step`、`PreToolUse→tools/pre-execute`、`PostToolUse→tools/post-execute`、`Stop→agent/turn-stopping`；**exit 2 = block**，stdout 作为 additionalContext 以 `plugin` 来源入 transcript。
- MCP 工具名 64 字符预算，超长确定性截断哈希；同步两段式 **Fetch（只读列出）/ Swap（原子换代）**。
- goal：CAS 更新（`GoalRef` = id+revision）；`get_goal` 必须先于 `update_goal`；`blocked` 需持续阈值（默认 3 轮）。todo：全量快照式 `todo/write` 事件、`turn/start` 清空、可配单 in-progress。schedule：`schedule/change` 事件 + 到期经 `agent.followup()` 开新轮。plan：`plan/mode` 会话事件 + `exit_plan_mode` 工具门控。
- skill 目录重发布以 `skill-catalog` 消息源的 **digest 变更**为条件（不刷屏）。

### 2.9 测试基础设施（8.x，本案例首证）

- Vitest 双工程：`thread-safe`（forks 池，纯逻辑/组合）vs `process-bound`（进程池：持久化/ACP/适配器/子进程）；平台门控动态排除（Windows 排除 bash 套件、Linux 排除 `sandbox-windows-acl`）。
- 自定义覆盖率报告器打印精确 `path:line:col` 未覆盖位置；豁免清单 `coverage-exempt.ts`。
- **HMR 安全规则**：每个注册表必须有"处置贡献 fiber 后断言清理"的测试。
- **构建制品冒烟**：验证 `lib/bin.js` 在纯 node 下可跑（抓 tsx 掩盖的破损）。
- 浏览器 E2E：启动**真实组合**（dsh-base+dsh-web-app over 临时 profile）；三模式 `DSH_SNAPSHOT=replay|record|refresh`；确定性屏障——`expect.poll` + `whenTurnSettled()`；**ARIA 快照黄金文件**（非原始 HTML）；确定性改造：持久化/工作区重定向临时目录、禁 session-title-llm 与 agent-instructions（防本地 AGENTS.md 泄入 fixture）。
- 测试支持三件套：`llm-mock-server`（本地实现 provider API）、`llm-replay`（拦截请求、从快照确定性回放）、`acp-snapshot`（场景工厂 + 固定 mtime 播种工作区——让 ripgrep/glob 结果确定）。

### 2.10 文档 i18n（9.x，本案例首证）

- **三件套**：`foo.md` + `foo.zh.md` + `foo.i18n.yaml`（后者存两语最后一致态的 **git blob hash**，可 pre-commit 校验）。
- 自定义 **git merge driver**（`dsh-translation-pairing`）：两语 `.md` 干净合并后自动重算 sidecar。
- 结构镜像强制：标题层级/列表数/表格维度/代码块**字节一致**。
- **Type Equivalence 门**：markdown 里 ```ts type-equiv / ts public-api``` 围栏粘贴的类型声明与源码比对（`verify-type-equiv` + manifest）。
- **文档预算**：AGENTS.md 1900 词、architecture.md 2400、testing.md 1150、packages/README 994（`doc-budgets.manifest.json`）——文档膨胀是可执行门禁。
- VitePress 网站是**投影**（`website/docs.ts` 为发布清单）；缺译页面以可用源投影到两 locale 防死链。

## 3. Glossary 全录（DeepWiki 10 章）

| 术语 | 定义 |
|---|---|
| Cordis | 底层插件框架；"一切皆插件"；管理带服务/事件/可逆 effect 的共享 Context |
| Context (ctx) | 中央 Cordis 对象；服务挂其上（ctx.llm/ctx.tools），注入插件可访问 |
| Service | Context 上的命名能力；接口（Definition）+ 实现（Provider）+ 消费（Consumer） |
| Profile | dsh 的命名组合；列出堆叠的 bundle + 用户配置（web/headless） |
| Bundle | Cordis 配置行 + 所挂代码的发行格式；dsh-base 是每个 profile 的首层 |
| Capability Seam | Definition/Provider/Consumer 相会的可替换架构点 |
| Turn | 输入被认领时开启、agent 无欠账时关闭 |
| Step | 单次 turn 迭代：一个模型请求 + 其工具调用 |
| Inbox | 输入到达驱动的机制：用户消息/followup/注入上下文 |
| Waterfall | 顺序监听器链，可改结果或调 next()；关键：agent/pre-step、tools/execute |
| Code Mode | 给模型 run_code 工具 + 工具 SDK，写代码而非直接调工具 |
| Session Log | append-only 持久事件记录；模型上下文唯一事实源 |
| Surface | 日志的内存投影/视图，服务 UI 与模型历史 |
| deriveMessages() | 从原始日志投影模型可见历史 |
| SESSION_FORMAT_VERSION | 磁盘会话 schema 版本；预发布期钉 0、无兼容承诺 |
| Tool Registry | ctx.tools：工具 schema + 执行管线 |
| Approval Seam | 用户/策略须批准工具执行的可选交互点 |
| ACP | Agent Client Protocol；驱动 agent 的自动化协议 |
| BFF | Backend-for-Frontend；服务 web 客户端的 API 层 |
| DSH_HOME | dsh 配置与 profile 的主目录 |
| Landlock | Linux 文件系统沙箱特性 |
| MCP | Model Context Protocol；桥接外部工具提供者 |
| Typert | host↔client 间的类型安全 RPC 生成 |
| Zstandard | 会话工件存储压缩算法 |

## 4. DeepWiki 的错误与缺口（诚实记录）

1. **`SESSION_FORMAT_VERSION=0` 全文未出现**——尽管引用了机制笔记文件；本案例笔记（types.ts:56 实测）**领先** DeepWiki。
2. **事件名不一致**：2.3 章写 `tool/pre-execute`（单数），3.2 章写 `tools/pre-execute`（复数）——源码为复数 `tools/*`。
3. **校验库混淆**：2.2 章称配置校验用"Zod（从 TS 接口生成）"，2.1 章又 vendored schemastery——实情是**两层并存**：loader/插件 Config 走 schemastery（Standard Schema），wire/API 载荷走 Zod。
4. 覆盖缺口：per-lane vitest 配置（e2e/snapshot/web 独立文件）、run-gates 完整门禁清单、release.yml 均未展开——本案例 README 命令表已覆盖。

**结论**：DeepWiki 适合做"第二入口"（章节全、有图表、源文件链接丰富），但引用行号需回源码复核；本案例笔记以本地实测为准，本篇增补内容已按 DeepWiki 引用的源文件位置抽查核对。

## 5. 验证命令（增补事实抽查）

```bash
$ rg -n "DSH_COVERAGE_MAX_WORKERS" .github/workflows/ci.yml | head -2
$ rg -n "deepseek-official" packages/llm/llm-deepseek/src/index.ts | head -1
$ rg -n "isConcurrencySafe" packages/core/tools/src/index.ts | head -2
$ rg -n "FS_NOT_OBSERVED" packages/fs/fs/src/types.ts | head -1
119:export const FS_NOT_OBSERVED = 'FS_NOT_OBSERVED'
$ rg -n "git hash-object" docs/i18n/README.md | head -1
$ rg -n "SubagentDepthError|assertSubagentMaxDepth" packages/subagent -l
```

→ 生态分析见 [07-ecosystem](../07-ecosystem/01-dsh-plugin生态分析.md)
