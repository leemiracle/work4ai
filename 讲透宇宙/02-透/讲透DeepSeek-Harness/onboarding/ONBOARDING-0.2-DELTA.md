# ONBOARDING 0.2 增量蒸馏（0.1.2 → 0.2.2-alpha.3）

> 依据：仓内 `docs/*.zh.md`（22 主题双语中文侧，@8bd073392e）。只写 0.2 相对 0.1.2 的**增量**；既有 `ONBOARDING.md` 主线仍成立，读法修正见 §8；代差背景见上级 `refresh-20261103.md`。

## 1. 概念增量总览

| 主题（docs/xxx.zh.md） | 一句话 | 0.1 时代对应物 |
| --- | --- | --- |
| capability-seams | 109 个 ctx 服务键全景表：定义/实现/消费包，角色四分类 | "约 40 个能力缝"口述版 |
| agent-lifecycle | 轮次-步骤时序图：认领→pre-step→请求派生→流→工具池 | turn-flow 一笔带过（全新） |
| event-producer-consumer | 90 声明事件×派发/监听矩阵，四 dispatch mode | 无；词汇散在各包 |
| tool-catalog | 72 工具 Schema 目录（**启动真实插件**生成） | 无；schema 只能读源码 |
| tool-execution-pipeline | 共享流水线：pre-execute→守卫→审批→execute→post | 只描述"有守卫" |
| persistence-catalog | 63 持久事件+SHA-256 指纹+机器 schema | 无；词汇在类型文件里 |
| session-format-status | 格式治理：定稿 V4+发布记录 dsh-v0.2.0-rc.2 | 无版本治理（全新） |
| graph-atlas / module-graph | 文档图索引+peer 依赖图；三种维护模式 | 无；架构自检靠人工 |
| config-catalog | 160 包 Config 目录，可交叉核对 schema | 无；配置散在 cordis.yml |
| api-gateway | Typert Gateway：@Remote 严格生成 Host/Client 约定 | sdk stdio JSON-RPC 为主 |

贯穿性信号：**文档成为生成产物并进 CI 门禁**（`gen-doc-graphs`/`verify-*`/`doc-sync`）——文档漂移从"靠 review"变成"靠生成器+守卫"。

## 2. 能力接缝（capability seam）协议——0.2 最重头

### 2.1 接缝定义（glossary.zh.md#capability-seam）

seam = **三角色可替换能力**：①**Service Definition**——拥有自身 `ctx.<key>` 和词汇类型的 Cordis `Service`（抽象类或具体注册表，**绝不是 TS `interface`**）；②一个或多个 **Service Provider**；③一个或多个 **Consumer**。范例 `packages/shell`：`dsh-shell`（定义）+`dsh-bash-local`/`dsh-bash-sandbox`（提供方）+`dsh-tool-bash`（消费方）。关键规则：**seam 是完整能力，绝不是其中一个角色**；一个包可兼多角色（`dsh-user-approval` 同包定义+实现）。AGENTS.md 原文："It is complete, never one role."

### 2.2 全景表与角色四分类（capability-seams.zh.md 全景表）

109 个 ctx 键分四类（实测统计）：**seam 36 个**——多实现可替换接缝（`ctx.shell`/`ctx.fs`/`ctx.subprocess`/`ctx.llm`/`ctx.storage`/`ctx.subagents`/`ctx.web`/`ctx.sandbox`/`ctx.compaction`/`ctx.jobs`…）；**core 62 个**——核心主干无替换语义（`ctx.sessions`/`ctx.tools`/`ctx.systemPrompt`…）；**service 10 个**——普通服务；**bundle 1 个**——`ctx.agentLoop`，"唯一的具体循环插件；扩展包依赖 dsh-agent 的事件和服务，而不依赖此包"。"Plugins, not loop changes"的物化：连循环都只是 bundle。

### 2.3 替换规则（seam 实现清单实证）

- **`ctx.subprocess`**：local/ssh 两后端；bash 执行器、PTY、LSP Host、进程外 ACP/Codex/Claude Code subagent 后端**全部**经它 spawn（统一进程坐标、生命周期、stdio、kill 升级）。本地→SSH 只换后端。
- **`ctx.subagents`**：六后端并列（spawn/fork-in-process、acp、codex、claude-code、dsh-sdk）。**`ctx.storage`**：后端**以不同名称并列注册**（json 与 sqlite 互不遮蔽）。
- **`ctx.credentials`**：配置只携带对机密的**引用**，提供方持有实际值；轮换后下一次请求即生效。

### 2.4 与执行环境的关系（沙箱三件套）

`ctx.sandbox` 契约最能体现 seam 与环境的关系：**消费方交出即将执行 spawn 的确切 argv**，后端按每次调用的策略包装并报告强制执行情况。`ctx.sandboxPolicy` 统一保存部署默认模式和工作区根——bash 与 fs 两类强制组件都读它，"因此 bash 与 fs 不会限制到不同的根目录"。另一机制是**配套插件**：`ctx.fs` 的 `fs-observation-policy` 经 `fs/*` 事件门禁贡献"基于观测状态的检查"（先读后写），**不改 schema、不动 seam 本体**。

## 3. Agent 生命周期 + 事件模型

### 3.1 轮次-步骤时序（agent-lifecycle.zh.md 时序图）

链路：`turn/start` → 认领 next-step 输入+排队 prompt → `system-prompt/assemble` waterfall（带本步工具集）→ **`agent/pre-step` waterfall（权威 reject 或 enter）** → `step/start` → `agent/request` waterfall → `prepareCall` → **同步准入** `system/message`+`user/message` → **从日志派生并冻结请求** → `llm/stream` waterfall → 成功落 `assistant/message`，失败/重试/取消落 `assistant/attempt` → 工具按 `executionMode` 进 barrier 与有界滚动池（**开始前重分类**）→ `tool/call`（执行前记录）→ 模型顺序 `tool/result` → `step/end` → 自然停止且 inbox 空时 `agent/turn-stopping` 终检点 → 循环认领 → `turn/end`。

三条硬规则（图后散文）：①**空 assistant 内容不进派生历史**；取消轮次把已投递前缀 finalize 为 `interrupted: true` 的 `assistant/message`。②**压缩恢复在仍打开的步骤内**：`agent/pre-step` 处理压力、`agent/request-error` 仅管上下文溢出；先剪枝再摘要；重试不重复组装/用户准入。③**双通道**：可回放 transcript 走 `session/event`；`agent/*` 是 steering 与错误处理的**实时协调**接口。

### 3.2 事件矩阵（event-producer-consumer.zh.md）

90 个已声明事件，四 mode：`emit` / `waterfall`（必须调 `next()`）/ `serial` / `parallel`；覆盖绕过 `ctx.emit` 的内含派发位（subagent 生命周期封装）。中枢 `session/event` 有 **31 个包监听**；`agent/pre-step` 有 20 个监听包（compaction、plan-mode、goal-round-driver…），是事实上的"每步策略总线"。表末还列 11 个未声明事件字符串（`internal/*` 等）作治理待办。

## 4. 工具目录与执行管线

### 4.1 工具目录（tool-catalog.zh.md）

72 个工具，生成方式特别：生成器**在真实上下文中启动每个工具插件读 `ctx.tools.schemas()`**——工具 schema 无法静态完全确定（运行时枚举、配置名、MCP 原始 JSON Schema）。完整性守卫 glob `packages/*/tool-*`，漏包即失败（首节）。映射表：模型可见名称 | 依赖 seam | 写入事件 | 别名 | 部署说明。

部署规则精选：`exit_plan_mode` 规划未激活仍留在 schema（状态转换不引起目录变动）；工具**名称**可为加载时配置（`toolName`，别名 `subagent_fork`）；shell 家族分层——一次性 `bash`/`pwsh` + 持久 PTY 版 `*-persistent`（按所有者隔离）+ 六个 `terminal_*`（选择启用）+ 三个 `job_*`（**任务种类无关**的后台控制器）。

### 4.2 执行流水线（tool-execution-pipeline.zh.md 流程图）

顺序：`tool/call`（执行前记录）→ `tools/pre-execute` waterfall（钩子/权限/沙箱）→ **单调守卫**（deny 或弃权，身份受保护）→ `ctx.approval` 一次性询问（无回答方=deny）→ `tools/execute` waterfall（超时/重试/指标）→ execute() 主体 → fs 变更经 `fs/write-intent`/`fs/edit-intent` 门 → 工具自有事件 → `projectContent` → `tools/post-execute`（accept/block/replace/add context）→ 规范化（快照 throw 变 `isError`）→ `finalizeContent` → `tools/result`（冻结权威结果）→ `tool/result` 事件 → `additionalContexts` FIFO 注入。设计意图："钩子可跨越不同工具系列，而无需让工具与某个策略服务耦合。"被拒调用也走 `projectContent`（UI 卡片仍有内容）。PTC 子调用同入管线：记 `tool/ptc-dispatch` 对、拒绝=有约束力驳回。

## 5. 持久化目录与会话格式治理

### 5.1 persistence-catalog（63 事件 + 指纹）

信封 = `type/seq/time/data`+可选 `ignorable`+条件字段 `surfaceOp`/`sourceEventSeqs`。**核心二分：surface 事件产生模型历史，log-only 不产生**——surface 仅五种（`system/message`/`developer/message`/`user/message`/`assistant/message`/`tool/result`，信封节 SurfaceEventType）。`SurfaceOp` 为 `append` 或 `{op:'replace', startSeq, endSeq}`（压缩替换）。`ignorable` 缺省=必须：未识别且无标记时读者**拒绝重建**而非静默丢事件。每事件带 SHA-256 指纹（机器目录 persistence-schema.json）。

### 5.2 session-format-status（版本治理）

单一真源：`SESSION_FORMAT_VERSION` 是代码中唯一手工写入器版本。当前 **latestFinalizedVersion = 4**（检查点 `finalized/v4.json`）、**latestReleasedVersion = 4，evidenceTag = dsh-v0.2.0-rc.2**。升版本须新头版本转换，不能复用已接受的 3→4；已提交代际永不移动/覆盖/删除。红线原文："GitHub 的 prerelease 标记不会让持久化用户数据成为可丢弃数据"——alpha/beta/rc 发布也确立格式义务。

## 6. graph-atlas / module-graph：架构自检工具化

graph-atlas.zh.md 是七类图的索引（模块依赖/工具目录/能力 seam/共享组合/事件矩阵/agent 生命周期/工具流水线），每图声明维护模式：`generated`（module-graph、tool-catalog）/ `hybrid generated`（capability-seams、事件矩阵、组合）/ `curated`（两张生命周期图）。module-graph.zh.md 画 **peer 依赖**（共享实例供给）。工具链：`gen-doc-graphs`+`verify-doc-graphs`+各目录生成器并入 doc-sync——新工具包漏文档、新事件漏声明直接挂 CI。

## 7. config-catalog 与 api-gateway

### 7.1 配置目录（config-catalog.zh.md）

160 个包的 `config:` 块原样列出（含 JSDoc），每个均可由 `cordis.yml` 设置。三条治理：①生成器把运行时 schemastery schema 与粘贴声明**交叉核对**——每个经 schema 验证的键（含嵌套）必须能在声明类型中找到，"粘贴内容无法隐藏加载器接受的字段"；②每包标注 `inject`（注入服务键——其 cordis.yml 树还须加载这些服务的**提供者**）/`refs`/`source`；③运行时 schema 有意排除的字段是"仅运行时 seam"（AGENTS.md "No hardcoded tunables" 的文档面）。

### 7.2 Typert API Gateway（api-gateway.zh.md）

程序化访问面。编程模型：`@Remote`（调根 Host Context 服务）或 `@RemoteScope(key)`（先解析作用域 Context 再取服务）；复杂 Host 对象不能过 wire，须以 `TypertLookupMap` 声明 wire identity（`agent: Agent`→`agentId`）。**严格生成流水线**：构建先跑仅源码 Host 分析，生成物写入各包 `lib/`（typert.host.js/typert.remote-client.js 等 5 文件）；方法须公开、非静态、非泛型，参数具名必填。运行时：`POST /api/<namespace>/<method>`，payload 只有具名 `args`；**每次调用重新解析描述符与实时服务（不缓存）**；非 owner Peer 经 `ctx.remoteAccess.decide()`，被拒不解析 lookup、不激活 Agent。`agent`/`session` lookup 共享冷恢复策略。源码启动走 **SRC 弱回退**，Client 拒绝挂载。边界：Remote 只管一元+Host→Client 流；会话事件流、分页、增量 reduce **不得**伪装成 Remote 方法。

## 8. 对旧 ONBOARDING.md 结论的修正表

| 旧说法（0.1.2 基线） | 0.2 事实（锚） |
| --- | --- |
| "约 40 个能力缝" | 全景表 **109 个 ctx 键**：36 seam+62 core+10 service+1 bundle（capability-seams.zh.md） |
| "换能力 = 换组合文件" | 三角色协议：Definition（非 TS interface）/Provider/Consumer，seam=完整能力（glossary.zh.md） |
| 程序化访问 = sdk stdio JSON-RPC | 主干变 Typert Gateway：@Remote 严格生成；"会话事件流不得伪装成 Remote 方法"（api-gateway.zh.md 边界节） |
| "模型可见⟺已记录"（规则级） | 落地为 surface/log-only 二分：仅 5 种 SurfaceEventType 产生模型历史（persistence-catalog.zh.md） |
| 工具面 = bash 等枚举 | **72 工具成目录**；shell 家族四层；工具名可为加载时配置（tool-catalog.zh.md） |
| 会话格式无版本治理 | 定稿/发布双记录：V4+evidenceTag；已提交代际不可变（session-format-status.zh.md） |
| 文档 = 架构+subsystems+cookbook | 22 主题+生成目录族全进 doc-sync 门禁（graph-atlas.zh.md） |
| 事件只提 waterfall | 四 mode×90 事件矩阵；`agent/pre-step` 是 20 包共用的策略总线（event-producer-consumer.zh.md） |

仍成立的旧结论：everything-is-a-plugin 主线、cordis.yml 组合层叠、invariant.ts 伴生插件、`--dump-config` 诊断、无 key 测试政策。

## 9. 术语表增量（0.1 时代没有或未成词）

- **capability seam / Definition / Provider / Consumer**：三角色可替换能力（§2）。
- **surface vs log-only 事件**：是否产生模型历史的二分；**SurfaceOp**（append/replace）、**sourceEventSeqs**、**ignorable**。
- **单调守卫**：工具流水线中 deny-or-abstain、身份受保护、不得重排。
- **轮次/步骤/Round/交互段**（glossary.zh.md 循环层级）：turn=排空已接纳输入；step=一次模型请求+工具执行；Round=外层策略迭代；exchange=连续轮次段。
- **Goal Round / 目标激活**：目标续行周期与进程本地续行权限（armed/disarmed，不持久回放）。
- **Ralph 循环 / Ralph Round / Ralph 交接**：不可变目标的全新 agent 工作流、其子会话、结构化交接报告。
- **scope / shadowing / restriction / setup window / lineage**：按 agent 的注册单位体系；两层扁平、不向下继承，子树关系用 lineage 数据表达。
- **Typert / @Remote / SRC 回退**：Gateway 的类型图、装饰器、身份解析与源码启动弱描述符。
- **PTC / run_code / ptc-dispatch 对**：程序化工具调用执行器；子调用 start/settle 事件，log-only 不重入模型上下文。**spill（ctx.spillStore）**：过大工具文本外溢。**会话投影**：状态驱动折叠单元+检查点缓存。
- **配套插件**：不改 seam 本体、经事件门禁附加策略（fs-observation-policy）。

（完 · 锚点=docs/*.zh.md 文档名+小节/表行）
