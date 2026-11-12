# 08 · context 工程深读：每轮上下文的组装、瘦身与人机抢跑

> 一句话：**openclaw 把"模型每轮看什么"当成一条完整流水线——排队→转向→预检（flush+压缩）→组装（引擎插件化）→系统提示（缓存边界分层）→修剪——每个环节都有预算、超时和降级路径。**
>
> 证据基准：钉版 `f612675284`。缩写 `AC`=packages/agent-core/src · `SAR`=src/auto-reply/reply。姊妹篇：[06-memory体系](06-memory体系深读.md)（记什么）/[07-数据管线](07-记忆数据管线.md)（数据怎么流）；本篇=**每轮看什么**。与 `Agent上下文案例/`（代码智能层：给模型看什么代码）是不同抽象层。

## 0. memory vs context 的分界线

Memory 可落盘、可跨会话；**context = 本次 run 发给模型的全部 token**（context.md:10）。两条线在三个点交汇：bootstrap 注入（MEMORY/USER 进稳定前缀）、memory flush（压缩前抢救）、post-compaction refresh（压缩后补 AGENTS.md）。

## 1. 全景：一条消息到模型的旅程

```
入站消息 → lane FIFO 队列(session:<key> 保证每会话单 run)
  ├─ 运行中? → steer/followup/collect/interrupt 四模式(默认 steer)
  │     steer: 工具批 checkpoint 前检查 → 未启动的调用合成跳过结果 → 插话先于工具进模型
  → 预检 preflight: ①memory flush(静默抢救 turn) ②强制压缩(阈值: 窗口-20000-4000)
  → 组装 assemble(context engine 插件, 默认 legacy 直通)
  → 系统提示 buildAgentSystemPrompt(稳定前缀|缓存边界|易变后缀)
  → 修剪 pruning(cache-ttl 模式, 只剪旧 toolResult 的内存回放视图)
  → 发送 → 溢出错误? → compact-and-retry
```

## 2. System prompt：缓存边界是第一工程决策

`src/agents/system-prompt.ts:buildAgentSystemPrompt`（~1530 行）把提示切成两半：

**稳定前缀**（跨 turn 字节一致，prompt cache 可复用；哈希 LRU 64 条做缓存键 :98,1176-1219）：
identity → Tooling（工具表+委派模式）→ Tool Call Style → Execution Bias → Safety → Skills 列表 → **memory section**（插件化）→ Workspace → Sandbox → **`# Project Context`**（按 `CONTEXT_FILE_ORDER` :85-93 注入 AGENTS→SOUL→IDENTITY→USER→TOOLS→BOOTSTRAP→MEMORY）

**`SYSTEM_PROMPT_CACHE_BOUNDARY`**（:1432）以下是易变后缀：Temporal Context（日期变化不炸缓存）→ Messaging/Reactions/审批 → `## Conversation Context`（post-compaction refresh 落点 :1500-1504）→ heartbeat → Runtime。

**预算体系**（实测常量）：

| 层 | 上限 | 证据 |
|---|---|---|
| bootstrap 单文件 | 20,000 chars | `bootstrap.ts:89` |
| bootstrap 总量 | 60,000 chars | `bootstrap.ts:90` |
| USER.md | **固定 4,000**（独立更小预算） | `bootstrap-budget.ts:46-50` |
| MEMORY.md（提示注入层） | 无专属上限，受 20K/60K 通用约束 | —— |
| MEMORY.md（dreaming 重写校验层） | 10,000（memory-core 插件自己的预算） | `memory-budget.ts:33` |
| 摘要硬上限 | 16K chars | `compaction.ts:92-104` |

**截断不是简单头尾切**：普通文件 head 75% + tail 25%；**AGENTS.md 专门走 policy digest**——head 45% + 策略摘要 35% + tail 15%，正则挑 `must/never/security/credential` 类策略行保真（`bootstrap.ts:99-107,156-171`）。截断必注入提示"文件被截断，请直接读原文件"（不可配置）。

**子代理瘦身**：`promptMode=minimal` 砍掉 memory/Self-Update/Messaging/Heartbeats 等段；子代理只注入 AGENTS.md 一个 bootstrap 文件（system-prompt.md:75,124）。

## 3. Compaction：四路触发 + 纯代码审计的 safeguard

**触发**：①阈值维护（`contextTokens > 窗口-16384`，`compaction.ts:243-252`）②溢出恢复（识别几十种 provider 溢出错误串→compact-and-retry）③手动 `/compact`（owner-only，可带指令）④preflight 强制（`窗口-20000-4000`，SAR/agent-runner-memory.ts:786-800）+ 2MB transcript 字节熔断。

**切点算法**：从尾部按 `keepRecentTokens=20000` 累计，只在合法消息边界落刀；**tool-call 与 toolResult 永远配对**——切在 turn 中间就走 split-turn 路径单独摘要前缀（compaction.ts:366-484,702-833）。

**safeguard 模式**（新配置默认开启，`defaults.ts:654`）的质量审计是本篇最值得偷的设计：

- **判分者是纯代码函数 `auditSummaryQuality`，不是 LLM judge**（compaction-safeguard-quality.ts:198-226）
- 审三项：①必需五段标题齐全（`## Decisions/Open TODOs/Constraints/Rules/Pending user asks/Exact identifiers` :14-20）②strict 策略下 12 类不透明标识符（≥8位hex/URL/绝对路径/host:port/≥6位数字）**字面保留**（:148-160）③最新用户请求与摘要有 token 重叠（:162-196）
- 不过关→失败原因包成指令块重生成（默认重试 1 次）→仍不过→**cancel：不写摘要、原历史保持权威**（compaction-safeguard.ts:1347-1428）
- `identifierPolicy:"strict"` 默认开——摘要里丢一个 commit hash 都算事故

**持久化**：append-only SQLite 转录树节点 `{summary, firstKeptEntryId, tokensBefore}`；回放=最新 boundary 的摘要+保留尾（session.ts:84-135）。**没有 `/restore`**——磁盘不删，旧历史经 `sessions_history` 树分支可回看。这与 memory 篇"遗忘=降权不删除"同构。

## 4. Pruning：为 Anthropic prompt cache 量身定制的经济学

与 compaction 互补的轻量瘦身（只剪**旧 toolResult 的内存视图**，磁盘不动）：

1. 等 cache TTL 过期（Anthropic 插件自动配 1h；TTL 内绝不剪——保缓存复用）
2. 上下文 <30% 窗口不剪（`tool-result-truncation.ts:196-198`）
3. **soft-trim**：>4000 字符的结果保首尾各 1500（:161-165）
4. 仍 ≥50% 且可剪内容 ≥50K → **hard-clear** 为 `[Old tool result content cleared]`（:218-232）
5. 铁律：最近 3 个 assistant turn 永不剪；首条 user 消息之前永不剪（保护 bootstrap 读取）
6. 图像清理是独立通道：旧图像块替换为占位符防 prompt cache 反复炸（session-pruning.md:37-43）

token 估算=`chars/4`（:195）——与 memory 篇同一个英文中心的常数估算，中文场景同样失准。

## 5. Context engine：可插拔组装器 + 幂等落账

**契约**（`src/context-engine/types.ts:351`）：`ingest/assemble/compact` 三必选 + info；可选 `afterTurn/maintain/prepareSubagentSpawn/onSubagentEnded/commitTurn`。四个生命周期点在 `agents/harness/context-engine-lifecycle.ts` 驱动。

- **legacy 引擎**（默认）：ingest/afterTurn 无操作，assemble 直通（sanitize→validate→limit 管线仍在），compact 委托内置摘要（legacy.ts:14-43）
- **第三方接入**（如 lossless-claw）：assemble 可返回 `systemPromptAddition`——宿主先把异步 memory prompt 备好，插件经 `buildMemorySystemPromptAddition` 把 memory 段桥接进自己的组装（delegate.ts:241；memory 与 context engine 唯一的耦合点）
- **commitTurn 幂等落账 = SQLite outbox**：表 `context_engine_turn_outbox`，advancementKey=logicalTurnId，`onConflict doNothing`；commitTurn 成功删行、失败 attempt_count+1 留队；崩溃恢复 admitted 丢弃/不可读置 blocked（outbox.ts:102-477）——**崩溃重试下恰好一次生效**
- **失败隔离双层 proxy**：10 个受管方法逐调用 try/catch，抛错→quarantine（首次失败赢，跨进程持久化）→本进程降级 legacy；**compact 失败原样 rethrow 不静默**；每逻辑 turn 重新解析，坏引擎下一 turn 自动重试（registry.ts:99-257,712-781）
- 转录维护 `maintain()` 可声明 background 模式 deferred 跑，持锁 branch-and-reappend 安全重写

## 6. Steering 与 queue：人 > 任务完成度的上下文实现

02 号笔记讲过"steering 优先于任务"的原则，本篇给全上下文机制：

- **双重复查**：agent 主循环末尾复查两次 steering（`agent-loop.ts:504-516`，注释明言"so agent_end cannot strand an accepted steer"）+ 每个顺序工具启动前检查（:787）
- 被跳过的工具调用收到**配对的合成错误结果** `"Skipped due to queued user message."`（:74）——转录保持 append-only 且结构配对，模型能看到"什么被跳了、为什么"
- 已过 launch checkpoint 的并行批**继续跑完**——不回收已开始的工作
- 队列四模式默认 `steer`+500ms debounce+cap 20+满队 `drop:"summarize"`（旧消息折成合成 prompt 注入）；compaction 换 session 后队列自动跟绑新 session（agent-runner-memory.ts:1045-1054）

## 7. 批判性评估

**值得偷的**：
1. **缓存边界分层**——稳定/易变二分 + 日期放边界之下 + 哈希 LRU 验证前缀稳定性，是 prompt cache 时代的系统提示组织法范本
2. **纯代码质量审计**——LLM 产物用确定性函数判分（标题/标识符/重叠），不过关宁可取消压缩也不写坏摘要；与 dreaming 的确定性 gate 一脉相承（"模型判断永远在界内"）
3. **outbox 幂等落账**——把分布式事务的 exactly-once 问题下沉到 SQLite 队列，插件崩溃恢复后不丢不重
4. **标识符保真**——摘要丢 commit hash/路径算事故，这是踩过坑的人写的规则

**风险与短板**：
1. **摘要模板双轨**：safeguard 审计要求五段（Decisions/TODOs/...），summarization 提示模板却是六段（Goal/Constraints/Progress/Key Decisions/Next Steps，branch-summarization.ts:157-177）——两套标题体系并存，审计算分靠标题匹配，模板漂移会让审计误杀
2. `chars/4` token 估算英文中心（中文同预算实际 token 翻倍）
3. 复杂度继续膨胀：context 这条线又是 16+ 文件引擎层 + 1469 行 safeguard + 478 行 outbox，与 memory 篇同一病灶
4. pruning/compaction/maintain/flush 四种"上下文变小"机制并存，交互矩阵（flush 失败→preflight 救→rotate session）调试成本高
5. 无 `/restore` 命令——历史虽在树上可查，但"回到压缩前"没有一等公民操作

**一句话定位**：如果说 memory 篇是"写路径即安全边界"，context 篇就是"**缓存边界即成本边界**"——所有设计（分层/修剪/占位符/TTL）都围绕"稳定前缀复用最大化、易变尾部最小化"展开；而 steering 机制是这条流水线上唯一的"人因工程"：用户插话可以推翻整批未执行的工具计划。

## 审计命令

```bash
cd ~/ai/agent/awesome-agents/repos/openclaw
git log -1 --format=%h                                    # f612675284
grep -n "SYSTEM_PROMPT_CACHE_BOUNDARY" src/agents/system-prompt.ts        # 缓存边界
grep -n "DEFAULT_BOOTSTRAP_MAX_CHARS" src/agents/embedded-agent-helpers/bootstrap.ts  # 20K/60K
grep -n "auditSummaryQuality" src/agents/agent-hooks/compaction-safeguard*.ts          # 纯代码审计
grep -n "Skipped due to queued" packages/agent-core/src/agent-loop.ts     # steering 跳过
grep -n "0.3\|50_000" src/agents/embedded-agent-runner/tool-result-truncation.ts       # 修剪阈值
grep -n "context_engine_turn_outbox" src/state/*outbox*.ts               # 幂等落账
```
