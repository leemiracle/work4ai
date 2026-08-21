# openclaw ↔ dsh 双案例对照卡：记忆、上下文与压缩的两极设计

> 一句话：**同为"插件化 harness 即产品"，openclaw 把记忆建成 165K 行的治理子系统，dsh 干脆宣布"工作区是唯一长期记忆"——两极之间是 2026 年 agent 记忆问题的整个设计空间。**
>
> 证据：openclaw 钉版 f612675284（notes/06-09）；dsh 钉版 141eb6fef8 rc.8（notes/00-10）。
> 位置：本卡挂两侧单元互链；对照维度取自两仓源码 file:line 级深读。

## 一、身份对照

| | openclaw | dsh (DeepSeek Harness) |
|---|---|---|
| 产品形态 | 个人 AI 助手（挂在你的聊天频道 7×24） | 编码 agent harness（CLI/Web） |
| 插件哲学 | 42 挂点插件面（宿主定义挂点） | **一切皆插件**（Cordis，219 包，连 compaction 都是 seam） |
| 用户预期 | always-on、跨月记忆、会被投毒 | 会话内任务、工作区即上下文 |
| 成熟度 | 386K★、9 个月 | developer preview rc.8、无兼容承诺 |

## 二、记忆：治理系统 vs 激进不做

**openclaw**（06/07 篇）：五档 tier + SQLite 溯源列（origin_class CHECK）+ dreaming 三阶段巩固（六信号/三阈值/25% 损失上限）+ 双车道召回 + 10 个 QA 场景。动机：always-on 助手必须跨会话记你，且会被网页/群聊投毒——**写路径即安全边界**。

**dsh**：没有 memory 包（packages/README 无 memory 组）。官方哲学宣言只有一句——`packages/workflow/tool-ralph/README.md:90`："**The workspace is the only cross-round long-term memory**"（ralph 循环里 workspace 是唯一跨轮记忆，一份有界报告是显式交接）。跨会话召回靠 session-reference（单消息≤3 引用、每快照≤64KiB）+ session-query（历史 FTS）+ 事件日志本身。

**判断**：这不是谁对谁错，是**产品形态决定记忆需求**。编码任务的"记忆"本来就该沉淀在 repo（AGENTS.md/代码注释/commit），而不是 agent 的私有大脑；个人助手的记忆就是它的大脑。dsh 的选择反而避免了 openclaw 的最大成本——165K 行记忆子系统的维护负担（其 fix(memory) commit 密度全仓第一）。

## 三、上下文组装：集中引擎 vs 数据面+协议

| | openclaw | dsh |
|---|---|---|
| 架构 | `plugins.slots.contextEngine` 单 slot 可插拔引擎（Ingest/Assemble/Compact/AfterTurn 四生命周期 + outbox 幂等落账） | 组装下沉 core：SystemPrompt 服务（有序 sections）+ Session surface 派生；packages/context 只是 user-message 注入插件族 |
| 稳定前缀 | 显式 `SYSTEM_PROMPT_CACHE_BOUNDARY` 分层 + 哈希 LRU 验证 | **EpochHeader**：system+tools+config 变化才追加 request/header 事件 |
| 动态注入 | hidden prefix（active-memory 包 untrusted 框架） | "supersedes earlier snapshots" user 快照（可审计性更强） |
| 失败语义 | 引擎隔离降级 legacy + compact 原样 rethrow | 事件溯源内建（组装=纯函数派生，无独立降级路径） |

**互鉴点**：dsh 的"上下文=事件日志的纯函数投影"比 openclaw 的"引擎 assemble 返回消息"更彻底——**没有第二份真相就没有 desync**。openclaw 的 outbox 幂等是给第三方引擎的信任补偿，dsh 干脆不给第三方引擎接管组装的口子（context/ 插件只能追加 user message）。

## 四、压缩：safeguard 审计 vs 事务不变量

| | openclaw safeguard | dsh 事务不变量 |
|---|---|---|
| 判分者 | 独立纯代码审计（五段标题/标识符字面保留/重叠） | 无判分者，事务约束内建 |
| 硬约束 | 旧条目损失≤25%、预算 10K、拒写保原史 | 摘要必须严格小于被压内容、拒图、截断=失败 |
| 崩溃恢复 | pre-image 回滚 | **孤儿锁即崩溃信号**（start 无 end 可检出） |
| KV-cache | 隐式（稳定前缀设计） | **显式对齐**：摘要调用=会话真前缀+新 user 指令，省一次全量 prefill |
| 切点 | keepRecentTokens=20000 尾向 | retainTokens=16% 尾向 + **按 tool 配对不按整 turn**（可压超大 turn） |
| 免模型剪枝 | 独立 pruning 子系统（cache-ttl 门控） | compaction 内置先行步骤（8192/4096/1024） |

**同源证据**：两侧摘要模板都是 8 节结构化 checkpoint（Primary Request/Files/Errors/Pending/Next Step）——与 Claude Code 同款，**已成行业默认**。

## 五、token 计数与经济

- openclaw：`chars/4` 常数估算（英文中心，中文失准——两篇笔记共同短板）
- dsh：同样 4 chars/token 估算起步，但加 **usage 锚定**——最近成功调用的 provider usage 做基线，之后只加 surface 增量（TokenMeter per-session WeakMap）："估算起步、真值锚定、增量维护"。**值得 openclaw 偷**。

## 六、子代理：竞品即插件

openclaw `sessions_spawn`（自身子代理）vs dsh **subagent-codex / subagent-claude-code**——把 Codex 和 Claude Code 当可插拔子代理 provider（官方 SDK query()、严格 result 分类、进程树终止权归 dsh-subprocess）。rc.8 又分蘖 experimental/agent-teams。这是**"harness 联邦"路线**：dsh 不需要赢过竞品的模型，只要竞品能当它的手。

## 七、决策制度对照（工程文化层）

| | openclaw | dsh |
|---|---|---|
| 决策记录 | AGENTS.md 电报体 + VISION.md | **.agents/notes ADR 宪法**：544 篇、四态生命周期、四段骨架、PR 必带、门禁校验、故意无索引 |
| 原则口号 | "production LOC 净≤0"、Repair Doctrine | "Model-visible ⟺ logged"（运行时 stringify 逐请求断言） |
| 对你的启示 | 反模式清单文化 | **rejected 也要写、索引也可以拒绝生成**——决策记录本身可以是宪法 |

## 八、给你的三条可迁移结论

1. **记忆需求 = f(产品形态)**：做编码工具别建记忆子系统（工作区就是记忆）；做 always-on 助手没有记忆就没有产品。中间形态（如 deepseek 五成员 harness）可按需选边
2. **可审计性的两种实现**：openclaw 用"独立审计层"（safeguard/溯源列），dsh 用"结构即真相"（事件日志纯函数投影 + stringify 断言）。后者更难被绕过，前者更容易扩展——信任需求高选后者，生态需求高选前者
3. **KV-cache 对齐应显式化**：dsh 把"摘要调用复用真前缀"写成设计契约值得所有 harness 抄；usage 锚定的 TokenMeter 是 token 经济学的现成改进

## 交叉引用

- openclaw 侧：`../openclaw/notes/06-memory体系深读.md`、`07-记忆数据管线.md`、`08-context工程深读.md`
- dsh 侧：`../deepseek-harness插件化框架/notes/`（00-10 全目录）
- 谱系第三极：`../ClaudeCode源码深读/`（记忆无向量库/五层压缩——dsh 哲学的商用先例）
