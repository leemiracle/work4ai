# A-20 `CortexReach/memory-lancedb-pro`（4.5K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\CortexReach__memory-lancedb-pro
> TypeScript，单层平铺 src/ 56 文件（store.ts 139KB / smart-extractor.ts 124KB / tools.ts 129KB），test/ 100+ 回归测试 / MIT，v1.1.0-beta.11
> 一句话定位：OpenClaw 平台的 LanceDB 长期记忆插件——向量+BM25 混合检索、跨编码器重排、多 scope 隔离、Weibull 衰减与六类记忆生命周期

## 1. 架构总览（目录地图，标出核心目录的职责）

- 平台形态：OpenClaw 插件（openclaw.plugin.json:4 `"kind":"memory"`），带 skills/lesson 与管理 CLI、`/dreaming` 命令别名（openclaw.plugin.json:17-21）
- 写入链（src/ 平铺）：
  - `smart-extractor.ts`：LLM 六类抽取 + envelope 剥离 + grounding/register 判定
  - `admission-control.ts`（44KB）+ `admission-stats.ts`：LLM 准入评审与统计
  - dedup judge（prompt-blocks.ts 共享身份/评分话术）→ merge writer
  - `store.ts`：LanceDB 持久化（bulkStore 批量 + proper-lockfile/Redis 跨进程锁）
- 检索链：
  - `embedder.ts`（50KB）：多供应商嵌入（openai-compatible/azure/ollama/voyage/jina…），429/503 重试、错误状态分类（embedder.ts:678-679, 401-402）
  - `retriever.ts`（71KB）：混合检索 + 融合 + 重排 + 衰减 + 诊断
  - `noise-filter.ts` + `noise-prototypes.ts`：噪声过滤
  - `query-expander.ts`：BM25 查询同义扩展（仅 manual/CLI）
- 治理层：
  - `scopes.ts`：多 scope ACL；`clawteam-scope.ts`、`workspace-boundary.ts`、`identity-addressing.ts`：团队/边界/身份
  - `decay-engine.ts` + `tier-manager.ts`：Weibull 衰减与 core/working/peripheral 分层
  - `dreaming-engine.ts`（31KB）：离线整理；`session-compressor.ts`、`memory-compactor.ts`：会话压缩
  - `auto-recall-tier1.ts`：自动召回"3 strikes"治理
- 运行时：`openclaw-memory-capability.ts`（插件接口+startup 健康诊断）、`reflection-*.ts`（反思事件流，独立 store）、`corpus-indexer.ts`、`migrate.ts`、`memory-upgrader.ts`

## 2. 记忆机制深读

### 2.1 写入/抽取管线（谁触发、prompt、schema）

- 触发点：
  - OpenClaw 会话钩子（openclaw.plugin.json:25-27 `hooks.allowConversationAccess:true`）
  - 会话压缩 flush：软阈值 4000 token、强制 flush 2MB 转录、预留 floor 20000 token（openclaw-memory-capability.ts:142-144）
- 抽取管线："conversation → LLM extract → candidates → dedup → persist"（smart-extractor.ts:1-5）
- 六类分类法（一句话写死在共享 prompt 块，prompt-blocks.ts:14-15）：
  `profile（用户身份）/ preferences（倾向）/ entities（长期实体状态）/ events（发生的事）/ cases（问题+解法对）/ patterns（可复用流程）`
- **三层层级内容**：每条候选带 `abstract`（L0 一句话索引）/ `overview`（L1 结构化摘要）/ `content`（L2 全文叙事）（memory-categories.ts:128-137）——检索注入可按 token 预算取浅层
- **幻觉防线（本仓独创）**：
  - 每候选自标 grounding `real|constructed`；批次级 ConversationRegister `real|mixed|fiction`（游戏/roleplay 帧检测，memory-categories.ts:83-92）
  - fiction 批次：DURABLE_CATEGORIES（profile/preferences/entities/cases/patterns）全丢（memory-categories.ts:100-106）
  - events 类在 fiction 批次需 grounding-judge 确认，缺/败 verdict **fail-closed**（memory-categories.ts:108-118）
  - REGISTER_STRICTNESS 排序：rejudge 只可收紧不可放松（memory-categories.ts:120-125）
- 抽取前剥除平台 envelope 元数据（消息 ID/sender JSON 等被弱模型原样记忆的垃圾，smart-extractor.ts:112-130）
  - 五类剥离目标：System 时间戳头、"Conversation info (untrusted metadata)" JSON 块、Sender JSON 块、Replied message 块、含 message_id/sender_id 的独立 JSON（smart-extractor.ts:119-125）
  - 剥离器用括号配对（跳过字符串字面量）判定"单一平衡 JSON 对象"才动手——保守方向失败即放行（smart-extractor.ts:272-278）
  - 抽取 prompt 的 JSON 示例要求裸写不围栏：围栏示例会诱使模型回围栏（2026-07-18 线上抓到的 fence-mimicking 缺陷，prompt-blocks.ts:34-42）
  - subagent 运行时样板（"You are running as a subagent"/"Do not use any memory tools"）也在剥离范围（smart-extractor.ts:135, 145）
- dedup 判决 7 种：`create / merge / skip / support / contextualize / contradict / supersede`（memory-categories.ts:139-154）
  - events/cases 为 APPEND_ONLY（只 CREATE/SKIP 不 MERGE，memory-categories.ts:74-78）
  - 语义记忆可 contradict→supersede 形成时间事实链
- scope 级抽取策略 `full | episodic-only | none`（纯娱乐 scope 可整体禁抽取省 LLM，smart-extractor.ts:338-343）
- 准入控制独立成层：ADMISSION_JUDGE_IDENTITY + SCORE_TIER_RUBRIC（durable 高分/事件中分/闲聊低分，prompt-blocks.ts:21-23），带 utility veto 与 lane 模型亲和（admission-control.ts）

### 2.2 存储后端与数据模型

- LanceDB 单表，行 schema（store.ts:48-57）：
```ts
id: string; text: string; vector: number[];
category: "preference" | "fact" | "decision" | "entity" | "other" | "reflection";
scope: string; importance: number; timestamp: number;
metadata?: string;  // JSON 字符串，装 SmartMemoryMetadata
```
- FTS 索引：`Index.fts({withPosition:true})`（store.ts:1240-1244）；FTS 不可用时降级 JS 词法搜索（store.ts:1983-1984）
- 写入边界约束：
  - importance 在写入处 clamp（防 CLI 导入越界值，store.ts:1263-1279）
  - **scope 为空直接拒绝写入**："scope-less rows are invisible to scoped readers"（store.ts:1271-1275）；upsert 同样拒绝并 trim scope（store.ts:1284-1294）
  - 跨进程：proper-lockfile + 可选 Redis 锁（store.ts:141-148；redis-lock.ts）；读一致性可配 readConsistencyInterval（0=强一致，>0=有界 eventual，store.ts:69-76）
  - LanceDB napi-rs 加载的 WSL2+Tailscale DNS 卡死 workaround（excludeNetwork，store.ts:159-168）——真实生产坑
- SmartMemoryMetadata（JSON 存 metadata 列，smart-metadata.ts:41-76）：
  - 内容分级：`l0_abstract / l1_overview / l2_content`
  - 生命周期：`memory_category, tier, state: pending|confirmed|archived, memory_layer: durable|working|reflection|archive, source`
  - 时间事实：`valid_from / valid_until / fact_key / supersedes / superseded_by / relations`
  - 召回治理：`access_count, injected_count, last_injected_at, last_confirmed_use_at, bad_recall_count, suppressed_until_turn, suppressed_until_ms`（undefined=从未被 Tier1 触碰的 lazy-heal 哨兵）
- 长文档切块（chunker.ts:72-78 默认）：maxChunkSize 4000 字符 / overlap 200 / minChunk 200 / 句边界语义切分 / 每 chunk ≤50 行
  - 内置嵌入模型上下文表（chunker.ts:53-70）：text-embedding-3=8192、gemini-embedding-001=2048、all-MiniLM=512…
  - 可选 AST 代码边界感知切分（js/ts/py，chunker.ts:31-36）

### 2.3 检索策略（混合检索+重排的完整参数表，本笔记重点）

默认配置（retriever.ts:215-239）：

| 参数 | 默认 | 说明与出处 |
|---|---|---|
| mode | hybrid | `hybrid \| vector` |
| vectorWeight / bm25Weight | 0.7 / 0.3 | 融合权重 |
| minScore | 0.3 | 融合前过滤 |
| rerank | cross-encoder | 另有 lightweight / none |
| rerankModel / rerankEndpoint | jina-reranker-v3 / api.jina.ai/v1/rerank | retriever.ts:226-227 |
| rerankProvider | jina | 支持 jina/siliconflow/voyage/pinecone/dashscope/tei 六协议（请求/响应/鉴权头各有差异，retriever.ts:52-64） |
| rerankTimeoutMs | 5000 | 支持 caller 覆盖 + 绝对 deadline 裁剪（retriever.ts:121-126, 1414-1424） |
| candidatePoolSize | 20 | 重排候选池 |
| recencyHalfLifeDays / recencyWeight | 14 / 0.10 | 新鲜度**加法** bonus |
| lengthNormAnchor | 500 | `score *= 1/(1+log2(len/anchor))` 长度归一（文档默认 300，retriever.ts:67-74） |
| hardMinScore | 0.35 | 重排/衰减/归一之后的**终局硬截断** |
| timeDecayHalfLifeDays | 60 | `score *= 0.5+0.5*exp(-age/HL)` 乘法惩罚（retriever.ts:80-89） |
| reinforcementFactor / maxHalfLifeMultiplier | 0.5 / 3 | 访问强化延长衰减半衰期，封顶防"永生"（retriever.ts:90-95） |
| tagPrefixes | proj/env/team/scope | 前缀查询走 BM25-only + mustContain，绕开向量语义误报（retriever.ts:96-99） |
| neighborEnrichment | off / 2 | MMR 后附带同池 BM25 近邻（默认关，retriever.ts:100-107） |

- 融合公式——**名为 RRF 实为加权融合**（trace 阶段名 rrf_fusion，retriever.ts:1095）：
  - `fused = clamp01(max(0.7×vec + 0.3×bm25, bm25≥0.75 ? bm25×0.92 : 0), 0.1)`（retriever.ts:1353-1363）
  - BM25 高分地板（0.75×0.92=0.69）保护精确关键词命中（API key、工单号）不被低向量相似度拖垮
  - 纯 BM25 结果先 `store.hasId()` 验真，防 FTS 索引滞后产生的幽灵行（retriever.ts:1331-1341）
- BM25 分数归一：LanceDB 原始 BM25 无界，sigmoid `1/(1+exp(-raw/5))` 压到 (0,1)（store.ts:2018-2022）
- **Cross-Encoder 重排混合**（retriever.ts:1481-1514）：
  - `blended = 0.6×CE分数 + 0.4×原融合分`，带 preservation floor（防 CE 把高分意外打飞）
  - CE 未返回的候选 ×0.8 保留而非丢弃（retriever.ts:1501-1510）
  - 失败全链降级 cosine，原因四分类记入 diagnostics.rerankFallback：invalid_response/http_error/timeout/request_error/cosine_error（retriever.ts:198-207）
- 诊断一等公民（RetrievalDiagnostics，retriever.ts:145-209）：
  - 10 个漏斗阶段计数（afterMinScore→afterRerank→afterRecency→afterImportance→afterLengthNorm→afterTimeDecay→afterHardMinScore→afterNoiseFilter→afterDiversity）
  - dropSummary 记录每阶段 before/after/dropped
  - failureStage 定位到具体子步骤（vector.embedQuery / hybrid.bm25Search / hybrid.rerank…）
- 查询扩展仅 manual/CLI 来源启用（auto-recall 不扩，retriever.ts:1296-1303）

### 2.4 遗忘·整合·演化

- **Weibull 拉伸指数衰减**（decay-engine.ts:48-62 默认）：
  - `composite = 0.4×recency + 0.3×frequency + 0.3×intrinsic`
  - recency = exp(-λ·days^β)，β 按 tier：core 0.8（亚指数慢衰）/ working 1.0（标准指数）/ peripheral 1.3（超指数快衰）
  - 半衰期由 importance 调制：`effectiveHL = 30d × exp(1.5×importance)`（decay-engine.ts:147-163）
  - dynamic 型记忆（temporalType）半衰期 ÷3 快衰（decay-engine.ts:157-158）
  - 三层衰减地板：core 0.9 / working 0.7 / peripheral 0.5——检索 boost 不低于地板（decay-engine.ts:216-228）
  - frequency：对数饱和 `1-exp(-accessCount/5)` × 访问间隔新鲜度 bonus（decay-engine.ts:165-183）
  - composite < 0.3（staleThreshold）判 stale 进清理队列（decay-engine.ts:231-236）
- tier：core/working/peripheral 三档（memory-categories.ts:81）；dreaming-engine 扫描时按 decay 分 + tierManager.evaluate 决定升降（dreaming-engine.ts:720-723）
- 时间事实演化：fact_key + supersedes/superseded_by 链；检索默认排除 inactive（被取代）行（store.ts:2035-2038）
- **自动召回治理 Tier1**（auto-recall-tier1.ts）：
  - 注入后未被用户行为确认（last_confirmed_use_at < last_injected_at 即 staleInjected）→ bad_recall_count+1（auto-recall-tier1.ts:65-72, 116-119）
  - 连错 3 次（TIER1_BAD_RECALL_SUPPRESSION_THRESHOLD=3，注释明确"3 strikes 是行为设计而非可调参"，auto-recall-tier1.ts:3-10）且开启去重窗口 → 抑制 30 分钟
  - bad count 24h 衰减归零（"又被需要了"），负 gap 时钟偏移不误清零（auto-recall-tier1.ts:103-114）
  - lazy-heal：suppressed_until_ms===undefined 的遗留数据先复位（auto-recall-tier1.ts:92-101）
- dreaming-engine 离线整理（报告+merge/supersede 建议）；reflection 事件流存独立 scope `reflection:agent:{id}`（scopes.ts:66）
  - reflection 子系统自成一路：event-store / item-store / slices / mapped-admission / mapped-metadata / retry / ranking——反思产物有自己的存储、准入、重试（transient 重试，test/reflection-embed-transient-retry 佐证）与排序，不与主记忆混流
  - 偏好槽位 preference-slots.ts：偏好类记忆走独立槽位管理而非自由文本堆积
- 会话压缩 + lesson 提取 worker（examples/new-session-distill：hook 入队 enqueue-lesson-extract + systemd worker 消费）
- 语料索引 corpus-indexer.ts（30KB）：文件/块级语料独立建索引（status 暴露 files/chunks 计数，openclaw-memory-capability.ts:485-503）
- 记忆升级 memory-upgrader.ts：旧 schema（1-5 整数 importance 等）迁移到 v2 统一生命周期（memory-upgrader.ts:6 注释）

### 2.5 注入上下文的方式（Multi-Scope 隔离，本笔记重点）

- scope 模式集（scopes.ts:62-69）：
  - `global`（全 agent 共享）/ `agent:{agentId}` / `custom:{name}` / `project:{projectId}` / `user:{userId}` / `reflection:agent:{agentId}`
- **ACL 语义**（MemoryScopeManager）：
  - 默认 agent 只见 `global + agent:{自己} + reflection:agent:{自己}`——私有 reflection scope 隐式自动授予，显式 ACL 也**无法撤销自己的 reflection scope**（scopes.ts:105-108, 329-330）
  - 显式 `agentAccess` 表可追加授权（getAccessibleScopes 对显式 ACL 也补 reflection，scopes.ts:196-199）
  - 默认写 scope：有私有 scope 就写私有，否则 global；bypass ID 调用 getDefaultScope 直接抛错（scopes.ts:232-251）
- **三态 filter 契约**（getScopeFilter，scopes.ts:209-230）：
  - `undefined` = 全绕过（仅保留 bypass ID：system/undefined）
  - `[]` = 显式拒绝一切（deny-all）
  - `["global",...]` = 白名单
- 防绕过加固：
  - 保留 bypass ID 禁止配置显式 ACL，构造与 import 双路拒绝；空格填充（" system "）trim 后仍拒（scopes.ts:159-175, 317-327）
  - agentId 从 OpenClaw session key 规范解析（"agent:main:discord:channel:123" → "main"，scopes.ts:91-103）
  - legacy ScopeManager 的数组返回被归一化为显式 bypass，并节流告警（scopes.ts:498-531）
- 存储层执行：
  - SQL where `scope='A' OR scope='B'` + 应用层二次过滤（store.ts:1991-2016）
  - NULL scope 遗留行不进任何过滤（防对全部 agent 可见，store.ts:1996-2000）
  - BM25 over-fetch：limit×20 封顶 200，补偿 scope/状态过滤损耗（store.ts:1978-1981）
- workspace 边界：默认 `~/.openclaw/workspace`，跨 workspace 聚合 agent 集合（openclaw-memory-capability.ts:241-269）
- 虚拟路径注入：`memory://{id}.md` 把记忆行映射为可读文件供宿主引用（openclaw-memory-capability.ts:349-356）；MEMORY.md 为 memory-root、memory/dreaming/ 为 dream-report 等文件类型分类（openclaw-memory-capability.ts:290-294）

## 3. 关键代码摘录

```ts
// src/retriever.ts:1353-1363（融合：加权融合 + BM25 高分地板 + 幽灵行验真）
if (!vectorResult && bm25Result) {
  const exists = await this.store.hasId(id);
  if (!exists) continue; // Skip ghost entry
}
const weightedFusion = (vectorScore * this.config.vectorWeight)
                     + (bm25Score * this.config.bm25Weight);
const fusedScore = vectorResult
  ? clamp01(Math.max(weightedFusion, bm25Score >= 0.75 ? bm25Score * 0.92 : 0), 0.1)
  : clamp01(bm25Result!.score, 0.1);
```

```ts
// src/retriever.ts:1485-1490（Cross-Encoder 60/40 混合 + 保底地板）
const floor = this.getRerankPreservationFloor(original, false);
// Blend: 60% cross-encoder score + 40% original fused score
const blendedScore = clamp01WithFloor(item.score * 0.6 + original.score * 0.4, floor);
```

```ts
// src/decay-engine.ts:153-162（Weibull：tier 分层 beta + importance 调制半衰期 + dynamic 3x 快衰）
const baseHL = memory.temporalType === "dynamic" ? halfLife / 3 : halfLife;
const effectiveHL = baseHL * Math.exp(mu * memory.importance);
const lambda = Math.LN2 / effectiveHL;
const beta = getTierBeta(memory.tier);   // core 0.8 / working 1.0 / peripheral 1.3
return Math.exp(-lambda * Math.pow(daysSince, beta));
```

```ts
// src/store.ts:2020-2022（LanceDB 原始 BM25 分 sigmoid 归一）
const rawScore = row._score != null ? Number(row._score) : 0;
const normalizedScore = rawScore > 0 ? 1 / (1 + Math.exp(-rawScore / 5)) : 0.5;
```

```ts
// src/scopes.ts:203-207（隐式授予：global + 私有 agent + 私有 reflection）
// Agent and reflection scopes are built-in and provisioned implicitly.
return withOwnReflectionScope([
  "global",
  SCOPE_PATTERNS.AGENT(normalizedAgentId),
], normalizedAgentId);
```

## 4. 基准/评测声明（反虚荣视角）

- README 无任何 recall@k / 精度基准数字，只有架构描述（如 README:428 "Hybrid scoring: 60% cross-encoder + 40% original fused score"）。[无基准声明]
- 质量证据以工程面替代：
  - retrieval-trace.ts 每阶段留痕（vector_search/bm25_search/rrf_fusion…，retrieval-trace.ts:13）
  - retrieval-stats.ts / admission-stats.ts 运行统计；startup 健康诊断（FTS/embedding 可用性探测，retriever.ts:1996-2013）
  - test/ 100+ 回归测试文件，package.json `test` 脚本逐文件枚举，CI 分组（cli-smoke/core-regression/storage-and-schema/llm-clients-and-auth…）
  - 回归测试名本身记录了历史缺陷谱系：embedder-error-hints、cjk-recursion-regression（CJK 递归栈溢出）、vector-search-cosine（余弦回归）、scope-owner-leak-hardening（scope 泄漏加固）、isOwnedByAgent（归属判定）、retriever-rerank-regression、memory-update-supersede、typed-array-vector-fetch——缺陷驱动测试的直接物证
  - 端到端：functional-e2e.mjs、context-support-e2e、memory-capability-runtime、smart-memory-lifecycle（生命周期全链路）
- 可复现性：无评测榜但行为回归覆盖密集——工程可信度来自测试而非论文 [自评]

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）

1. **CE 重排的生产化兜底全套**：60/40 混合+保底地板、未返回候选×0.8 保留、六种 rerank 协议适配、超时/deadline 预算感知跳过、cosine 全降级+原因上报——比"调一次 rerank API"的可用度高一个量级
2. **幻觉注入双闸门**：per-item grounding 自标 + batch 级 fiction register（fail-closed）——解决 roleplay/游戏会话污染长期记忆的真实问题，mem0 无此机制
3. **L0/L1/L2 三层内容分级**同存一行，注入侧可按 token 预算截取——比 mem0 单一 text 字段省注入成本
4. **注入反馈闭环**：injected_count/bad_recall_count/suppressed_until 三件套——"注入是否被用"成为可计量信号，自动召回被 3-strikes 抑制
5. Weibull tier 分层衰减（core 亚指数 / peripheral 超指数）+ access 半衰期强化封顶 3×——比 mem0 的一次性 LLM 重写更可解释、可调参
6. scope 三态 filter 契约（undefined/[]/白名单）+ 空写拒绝 + NULL 行不可见——多租户记忆隔离的完整细则
7. 检索漏斗 10 阶段诊断 + dropSummary——调参不再靠猜

## 6. 局限与风险

- "RRF fusion" 名不副实：阶段名叫 rrf_fusion，实现是固定 0.7/0.3 加权融合（retriever.ts:1324-1363），不同领域数据的最优配比无法自适应
- 全流程重度依赖外部 API：嵌入 + 抽取 LLM + 准入 LLM + dedup LLM + 重排 API——一次写入最多 4 次 LLM 调用；key 缺失时降级路径多但体验碎片化
- metadata 是 JSON 字符串列：supersede/fact_key 链只能在应用层解析，LanceDB SQL 层无法按 smart 字段过滤
- 单表 + 每行全量 vector；FTS 幽灵行虽已修（FIX #15）但说明索引与数据存在一致性窗口
- 与 OpenClaw 宿主深度耦合（session key 解析、workspace 布局、plugin hooks、MEMORY.md 文件分类），移植成本高
- beta 版本号（1.1.0-beta.11）+ 测试清单硬编码在 npm scripts——维护仪式重

## 7. 一句话对比 mem0

mem0 是通用记忆库；本仓是 **OpenClaw 生态内重工程化的记忆插件**——检索端参数化到牙齿（混合权重/重排混合比/长度归一/硬截断全可调），治理端有幻觉双闸门、Weibull 分层遗忘与召回 3-strikes 抑制，牺牲通用性换生产可观测性。
