# A-14 `holaboss-ai/holaOS`（7.3K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\holaboss-ai__holaOS
> TypeScript（bun monorepo：Electron 桌面端 + runtime api-server + harnesses）｜ 一句话定位：本地优先的多 Agent 一体化工作台（Claude Code/Codex/内置 agent 并跑），卖点是"所有工具、文件、**一份共享记忆**"。

## 1. 架构总览（目录地图，标出核心目录的职责）

```
apps/desktop/         Electron 前端（memoryPaneModel.ts 记忆树 UI）
runtime/api-server/   本地 API 服务器：记忆子系统全部实现（20+ 个 memory-*.ts）
runtime/state-store/  SQLite 状态库（store.ts + 33 个 migration）
runtime/harnesses/    Agent 适配层：runtime-agent-tools.ts 定义 memory_retrieve/remember 工具
runtime/harness-host/ harness 宿主；channel-gateway/ 外部通道（connectors/）
packages/remote-api/  远程 API 契约（contract/memory.ts + server/memory.ts）
packages/app-sdk/ app-host/ runtime-client/ editor/ ui   应用与 SDK 面
```

记忆子系统文件分层（runtime/api-server/src/，按体量）：
- 服务面：`memory.ts`（FilesystemMemoryService，20KB）
- 检索面：`memory-recall.ts` / `memory-recall-index.ts`（词法+元数据打分器）/ `memory-hybrid-retrieval.ts` / `memory-reranker.ts`（LLM 重排）/ `memory-embedding-index.ts` / `memory-retrieval-pack.ts` / `memory-retrieval-intent.ts`
- 写入面：`turn-memory-writeback.ts`（回写管线）/ `workspace-memory-writer.ts`
- 图模型：`workspace-memory-graph.ts`（统一图读模型）+ 三棵源树：`interaction-memory.ts`(169KB) / `integration-memory.ts`(217KB) / `workspace-attachment-memory.ts`(222KB)
- 治理：`memory-governance.ts` / `user-memory-proposals.ts`
- 辅助：`memory-artifact-context.ts` / `memory-related-entities.ts` / `memory-browser.ts`（树浏览）/ `workspace-memory-repair.ts`（读模型修复）

## 2. 记忆机制深读（本笔记核心：共享记忆的实现与隔离边界）

### 2.1 写入/抽取管线（谁触发、路径布局、schema）

**双写入路径**，2026-07-14 起明确分工（`runtime/api-server/src/turn-memory-writeback.ts:89-94` 注释：旧的"每 turn 一次 gpt-5.4 事后抽取"已删除）：

1. **Agent 主动写入**（durable facts）：
   - Agent 调 `remember` 工具 → `recordDurableMemoryFromInput()`（turn-memory-writeback.ts:399-434）。
   - 复用抽取路径的候选塑造 `durableCandidateFromExtracted`，但 `modelContext: null`——**写入本身零 LLM 调用**（注释 :391-397："The brain already decided what is worth remembering; the server keeps the deterministic quality"）。
   - 工具 schema 在 `runtime/harnesses/src/runtime-agent-tools.ts:135`：入参 title/summary/scope('workspace'|'user')/memory_type(fact|preference|identity|procedure|blocker|reference)/subject_key/evidence/tags/confidence；工具描述明令"Do NOT use it for transient turn state, tool output, or anything already in context"。

2. **服务端被动索引**（recall substrate）：
   - 每 turn 结束 `writeTurnDurableMemory()`（turn-memory-writeback.ts:514-576）只把输入附件、引用图片 URL、输出工件索引为文档（各自的 persist*AsDocuments，:524-565）。
   - **集成工具结果被刻意排除**——:546-554 大段注释："They are transcript/evidence, not durable semantic knowledge: high-volume, machine-fetched, and stale-prone (the live integration is the source of truth — re-query it rather than recall a snapshot). Indexing every result floods the single global graph that all contexts recall from."

**物理存储是 Markdown 文件**（"stored locally, as plain files you can read and edit"，README.md:59）：
- 路径由 `extractedMemoryPath` 决定（turn-memory-writeback.ts:172-190）：
  - user 级 → `identity/{subject}.md` / `preference/{subject}.md`
  - workspace 级 → `workspace/{workspace_id}/knowledge/{facts|procedures|blockers|reference}/{subject}-*.md`
- 文件内容为结构化 Markdown（turn-memory-writeback.ts:192-228）：H1 标题 + `- Scope/Type/Subject/Workspace ID/Session ID/Updated at` 元数据行 + `## Summary` + 可选 `## Evidence` + 相关实体小节（appendDurableMemoryRelatedSections）。
- memoryId 确定性：`extracted:sha256(scope:type:subjectKey:path)[:24]`（:236-239）——同 subject 重写即 upsert，天然去重。
- 候选还会做"相关实体富化"：`enrichDurableCandidateWithRelatedInfo`（:273-331）只对 workspace 级候选，把解析出的 relatedEntities/relations 织回 Markdown 内容。
- 正则捕获显式偏好（零 LLM）：`detectExplicitResponseStylePreference`（:135-170）从用户消息识别"keep responses concise/detailed"类指令。

### 2.2 存储后端与数据模型（共享与隔离边界）

**两层存储，一冷一热**：
- **冷层（真相源）**：文件系统。`FilesystemMemoryService`（`runtime/api-server/src/memory.ts:388`）实现 `search/get/upsert/status/sync` 五接口（memory.ts:22-28）。后端解析 `resolveMemoryBackend`（:250-262）：MEMORY_BACKEND 环境变量请求任何非 builtin 后端都会 fallback 并附原因"ts runtime only supports the builtin filesystem memory backend"——共享记忆只有文件一种真相源。
- **热层（读模型）**：SQLite 语义图 + 向量。
  - `workspace-memory-graph.ts:41-114` 把六类源树统一为图描述符：interaction（人/系统实体）、integration（外部账号树）、attachment、image_url、tool_result、output_artifact。
  - `rebuildWorkspaceMemoryGraph()`（:229-278）全量重建：交互树摘要 + 集成树摘要 + 工件关系同步（syncWorkspaceArtifactRelations）。
  - `memory.ts:571-591` status() 在有 store 时附图统计（roots/leaves/semantic_nodes/internal_nodes/edges/relations）并置 `provider: "workspace_graph"`。

**隔离边界（重点，共五层）**：
1. **路径白名单**：`isMemoryPath`（memory.ts:121-136）只允许 `MEMORY.md`、`workspace/{workspace_id}/*`、`preference/*`、`identity/*` 四类；错误信息硬编码 memory.ts:17-18。
2. **workspace 作用域单 token 校验**：`workspaceScopePrefix`（memory.ts:108-119）要求 workspace_id 必须是单一路径段（`parts.length !== 2` 拒绝），防 `workspace/a/b` 逃逸。
3. **路径穿越双重防御**：`normalizeRelPath` 拒绝绝对路径与 `..`（memory.ts:93-106）；解析后再验证 `absolutePath.startsWith(storageRoot + path.sep)` 否则抛"path escapes memory root"（:496-501、536-541）。
4. **树级授权**：integration 图是 control-plane-only，store 层忽略 workspaceId（workspace-memory-graph.ts:138-139 注释）；跨 workspace 集成树由 `accessibleIntegrationTreesForWorkspace` 显式授权（:66-73）；检索时 `allowedTreeIds` 硬过滤候选（memory-hybrid-retrieval.ts:332-337）。
5. **工具面封装**：Agent 只能走 memory_retrieve/remember 两个工具，`runtime-capability-tools.ts:1488` 明示"Do not inspect backing memory files with generic file tools unless a future dedicated memory follow-up tool explicitly requires it"。

**共享 vs 隔离的落点**：user 级（preference/identity）**跨 workspace 共享**（存 globalMemoryRoot），workspace 级互相隔离（memory.ts:318-335 `resolveMemoryTargetPath` 按 workspace 前缀分流两根目录）；检索时两根合并排序（:411-458）。

**向量索引细节**（`memory-embedding-index.ts`）：
- `RECALL_EMBEDDING_DIM = 1536`（:13）；只在 `store.supportsVectorIndex()` 且有 embedding 客户端时启用（:106-108），否则纯词法降级。
- embedding 文本拼接 `Title/Type/Summary/Tags/Excerpt` 五行（:70-85）；Excerpt 取正文去 frontmatter 去标题行前 480 字符（:14、49-56）。
- SHA-256 内容指纹 + 模型 ID + 维度一致才跳过重嵌（:131-142）——指纹变更检测避免无谓 embedding 调用；scope bucket 按 workspace/preference/identity 分桶（:33-47），向量层同样按作用域隔离。

### 2.3 检索策略（三级：词法兜底 → 打分索引 → 混合重排）

**一级：内置词法兜底**（`FilesystemMemoryService.search`，memory.ts:399-476）：
- `scoreText` 全串命中 +1、token 命中率归一（:197-218）；token 化 `[a-z0-9]{2,}`（:189-195）。
- snippet 取命中行±2 行、截 700 字符（:220-248）；默认 max_results=6、min_score=0。
- 排序：score → path 字典序 → start_line（:460-470）。

**二级：词法+元数据打分索引**（`KeywordMetadataMemoryRecallIndex`，memory-recall-index.ts:171-286）：
- 起评分为治理 recallBoost（preference +4 / identity +3 / blocker +3 / fact +2 / procedure +2 / reference +1，memory-governance.ts:25-68）。
- user 域恒 +6（:199-202）；**意图加成表** `queryIntentBoost`（:31-111）：procedure 记忆遇 how/steps/procedure 问句 +6；fact 记忆遇 business 问句（owner/approval/deadline/sla 等 26 词）+3，且 title/tags 含 approval/cadence 再 +2/+2；blocker 记忆遇 blocked/permission +3；reference 遇 docs/url +2。
- 字段加权：title 命中 +3、tag +3、subject_key +2、summary +2、path +1、haystack +0.5（:215-243）；整 query 子串命中 title/summary +4（:209-213）。
- 惩罚：stale -3（:249-252）；**stale 的 reference 直接置 -1 过滤**（:253-256）。
- 排序键五元组：scopePriority(user 优先) → typePriority(问句类型与记忆类型匹配优先) → score → freshness → updatedAt（:270-284）。
- 全程输出 trace（matchedTokens/reasons），供 selection_trace 上抛（memory-recall.ts:140-147）。

**三级：混合检索 + LLM 重排 + 检索包**（`buildMemoryHybridRetrievalResult`，memory-hybrid-retrieval.ts:321-415）：
1. 意图推断 `inferMemoryRetrievalIntent`（fact_lookup/procedure_lookup/briefing/delta 等）。
2. 候选按 `tree_id:node_id` 合并去重、分数取 max、reasons 并集（:169-191）。
3. LLM 重排 `rerankMemoryCandidatesWithLlm`（:355-365）；启发式兜底 `highSignalScore`：urgent/blocker/deadline 类词 +1.5，owner/policy 类 +0.8（memory-reranker.ts:106-116）；query overlap 最高 1.2（:78-96）；新鲜度偏好 low/medium/high 三档（memory-hybrid-retrieval.ts:153-167）。
4. 新鲜度推断：preference/identity 永远 stable，其余 >45 天 stale（:90-106）。
5. evidence 上限 max_evidence 默认 8、钳 20（:165）；coverage 标注 used_lexical/used_vector/used_neighbors 与置信度 ≥5 high / ≥2.5 medium（:402-412）。

**选择预算（防单源淹没）**：`memory-recall.ts:23-93`：
- user 级条目最多占 2 条（有非 user 候选时，:33-34）。
- 类型多样性预算 maxPerType=⌈max/2⌉（:35-37）。
- 三重去重：memoryId / path / 语义键 `scope:type:subject`（:46-79）；预算装不满时降级重填（:84-91）。
- 默认 maxEntries=5（:115）；结果只取 status="active"（:102）。

**检索包（retrieval pack）**：`buildPack`（memory-hybrid-retrieval.ts:269-319）重组为 LLM 友好分节：known_facts(≤4) / recent_high_signal_items(≤5) / constraints(≤4，正则识别 policy/permission/deadline/review) / blockers(≤4) / open_questions / recommended_next_source / recommended_next_step（type: verify_live_state vs answer_from_memory）。`buildGaps`（:234-267）对 fact_lookup 且 top 分 <5 且非 stable 的证据生成"应去活数据源核实"的 gap 问题。

### 2.4 遗忘·整合·演化（治理规则）

`memory-governance.ts:25-68` 按 memory_type 硬编码治理表：

| type | verification | staleness | stale_after | recallBoost |
|---|---|---|---|---|
| preference | none | stable | ∞ | +4 |
| identity | none | stable | ∞ | +3 |
| fact | check_before_use | workspace_sensitive | 30d | +2 |
| procedure | check_before_use | workspace_sensitive | 14d | +2 |
| blocker | check_before_use | workspace_sensitive | 14d | +3 |
| reference | must_reconfirm | time_sensitive | 7d | +1 |

- 新鲜度评估 `assessMemoryFreshness`（:83-118）输出 stable/fresh/stale + 人话 note（"Verify this memory against the current workspace state before acting on it"，:127-131）；stale 的 reference 直接"must be reconfirmed before use"（:137-139）。
- 无删除/decay；但工具结果被排除在 durable 之外（2.1）本身就是最强遗忘策略。stale reference 在打分层即被过滤（memory-recall-index.ts:253-256）——事实上的软遗忘。
- 整合：`sync()` 全量重建图（memory.ts:595-617）；`refreshMemoryIndexes` 可按实体增量重建并等待 pending 队列（turn-memory-writeback.ts:436-512）。

### 2.5 注入上下文的方式（Agent 工具面）

- Agent 侧只见两个工具（runtime-agent-tools.ts:127-135）：
  - `memory_retrieve`："Resolve workspace memory into a reasoning-ready retrieval pack with recalled facts, recent high-signal items, supporting evidence, unresolved gaps, and a recommended next source...not for tree browsing"。
  - `remember`："Record ONE durable memory the moment you learn something worth keeping across sessions"。
- 工具经 HTTP 走 sidecar：`/api/v1/capabilities/runtime-tools/memory/retrieve|remember`（runtime-tool-capability-client.ts:25-26）——任何 harness（含外部 Claude Code/Codex）都通过同一 REST 面共享记忆，这是"跨 Agent 共享"的机制本质。
- 使用指引写在工具描述里（runtime-capability-tools.ts:1482-1495）："Treat returned summaries as compressed memory context and leaf hits as the underlying evidence"、"Set `scope: 'user'` for stable facts about the person; leave it as `workspace` for project/task knowledge"。
- 面向远程/多端：packages/remote-api 有独立 memory 契约与测试（remote-api/src/contract/memory.ts、__tests__/memory.test.ts）。
- 前端有专门记忆树浏览面（apps/desktop/src/components/panes/memoryPaneModel.ts + 测试）。

## 3. 关键代码摘录

**① 路径白名单与穿越防御**（`runtime/api-server/src/memory.ts:93-136`）：
```ts
function normalizeRelPath(value: string): string {
  const raw = value.trim().replaceAll("\\", "/");
  if (raw.startsWith("/")) throw new MemoryServiceError(400, "absolute paths are not allowed");
  const parts = raw.split("/");
  if (parts.includes("..")) throw new MemoryServiceError(400, "parent path segments are not allowed");
  return parts.filter((part) => part.length > 0).join("/");
}
function isMemoryPath(relPath: string, workspaceId: string): boolean {
  const normalized = normalizeRelPath(relPath);
  if (normalized === "MEMORY.md") return true;
  if (normalized.startsWith(workspaceScopePrefix(workspaceId))) return true;
  if (normalized.startsWith("preference/")) return normalized.length > "preference/".length;
  if (normalized.startsWith("identity/")) return normalized.length > "identity/".length;
  return false;
}
```

**② 确定性 memoryId + 治理注入**（`runtime/api-server/src/turn-memory-writeback.ts:234-239,261-263`）：
```ts
const governance = governanceRuleForMemoryType(params.extracted.memoryType);
const pathValue = extractedMemoryPath(params.turnResult, params.extracted);
const memoryId = `extracted:${createHash("sha256")
    .update(`${params.extracted.scope}:${params.extracted.memoryType}:${params.extracted.subjectKey}:${pathValue}`)
    .digest("hex").slice(0, 24)}`;
...
verificationPolicy: governance.verificationPolicy,
stalenessPolicy: governance.stalenessPolicy,
staleAfterSeconds: governance.staleAfterSeconds,
```

**③ 检索预算选择（user 条目不超 2 + 三重去重）**（`runtime/api-server/src/memory-recall.ts:33-37,58-61`）：
```ts
const hasNonUserCandidates = ranked.some((item) => item.entry.scope !== "user");
const maxUserEntries = hasNonUserCandidates ? Math.min(2, Math.max(1, maxEntries - 1)) : maxEntries;
const distinctTypes = new Set(ranked.map((item) => item.entry.memoryType));
const enforceTypeBudget = distinctTypes.size > 1;
const maxPerType = enforceTypeBudget ? Math.max(1, Math.ceil(maxEntries / 2)) : maxEntries;
...
const semanticKey = semanticDedupKey(entry);   // `${scope}:${memoryType}:${subject}`
if (selectedSemanticKeys.has(semanticKey)) return false;
```

**④ 意图加成：问句类型 × 记忆类型**（`runtime/api-server/src/memory-recall-index.ts:75-110` 摘要）：
```ts
if (entry.memoryType === "procedure" && hasProcedureCue) return 6;    // how/steps/procedure...
if (entry.memoryType === "fact" && hasCommandCue) return 2;           // run/verify/test/build...
if (entry.memoryType === "fact" && hasBusinessFactCue) { /* base 3, approval/schedule 再+2 */ }
if (entry.memoryType === "blocker" && hasBlockerCue) return 3;        // blocked/permission/policy...
if (entry.memoryType === "reference" && hasReferenceCue) return 2;    // docs/dashboard/url...
// stale 惩罚：score -= 3；stale 的 reference 直接 score = -1（:249-256）
```

**⑤ 集成工具结果刻意不入 durable 记忆**（`runtime/api-server/src/turn-memory-writeback.ts:546-554`）：
```ts
// Integration tool results are intentionally NOT indexed as durable memory.
// They are transcript/evidence, not durable semantic knowledge: high-volume,
// machine-fetched, and stale-prone (the live integration is the source of
// truth — re-query it rather than recall a snapshot). Indexing every result
// floods the single global graph that all contexts recall from.
```

## 4. 基准/评测声明（反虚荣视角）

- 无任何性能/质量基准。README.md:59-62 的主张（"Never start from zero"、"Local-first & yours"）为产品宣言 [自封]。
- 工程可信度靠测试：memory-*.test.ts 覆盖近 20 个文件（含 memory-ingestion-bounds.test.ts 写入边界、memory-recall-manifest.test.ts），隔离逻辑（路径白名单、workspace 逃逸）有 regression 测试背书 [可复现：bun test]。
- 桌面前端另有 memoryPaneModel.test.ts，记忆树 UI 也有测试面。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）

1. **"Agent 决定记什么、服务器保证怎么记"**（turn-memory-writeback.ts:391-397）：remember 工具写入零 LLM 调用，治理规则（路径、schema、去重、staleness）全部确定性——比"每 turn 后台 LLM 抽取"便宜且可控，是 mem0 抽取管线的有力替代架构。
2. **Markdown 文件为真相源 + SQLite 图/向量为读模型**：可读可编辑（用户信任）与可检索（机器效率）兼得；sync() 全量重建、status() 附图统计（memory.ts:595-617）。
3. **检索预算三重去重 + user/workspace 配额**（memory-recall.ts:23-93）：防"用户偏好条目淹没工作区事实"，mem0 的 top-k 检索没有这层。
4. **治理表按记忆类型分级**（memory-governance.ts:25-68）：verification/staleness/recallBoost 三轴，reference 7 天必须重确认、stale 即打分过滤——把"记忆可信度"做成一等公民字段而非事后补丁。
5. **检索打分的"问句类型×记忆类型"矩阵**（memory-recall-index.ts:31-111）：how 问句拉 procedure、blocked 问句拉 blocker——不需要 embedding 就能做意图路由，可作为向量检索前的粗排。
6. **retrieval pack 直接产出"下一步行动建议"**（memory-hybrid-retrieval.ts:304-318）：open_questions + recommended_next_source + verify_live_state vs answer_from_memory——检索器不仅返回证据，还返回"该不该去查活数据源"的决策。
7. **记忆文件对通用工具不可见**（runtime-capability-tools.ts:1488）：Agent 只能走 memory_retrieve 面——隔离不是靠权限系统而是靠"答案面封装"。

## 6. 局限与风险

- 内置词法检索是全文读文件+子串匹配（memory.ts:411-458），记忆文件多时 O(N) 全读；向量层需要外部 embedding 客户端才启用，无嵌入时检索质量上限低。
- LLM 重排依赖外部模型客户端（memory-model-client.ts），超时/失败的降级细节藏在 reranker 内部（memory-reranker.ts:121-632）。
- 单 workspace 记忆与全局 user 记忆在检索时合并排序（memory.ts:437-470），workspace 间通过 preference/identity 有信息侧信道——多租户场景需注意。
- 33 个 migration 的 SQLite schema 仍在高速演化（state-store/src/migrations/），内部 API 无稳定性承诺。
- interaction/integration/attachment 三棵树源文件 170-220KB 级单文件，工程债明显；打分魔法数（+6/+3/+2/-3）全部硬编码，无调参面。

## 7. 一句话对比 mem0

mem0 是"给单个 Agent 的记忆库"，holaOS 是"给一组并跑 Agent 的工作台级共享记忆"——真相源从向量库换成可编辑的 Markdown 文件、抽取从后台 LLM 改为 Agent 主动 remember、隔离从 user/agent 二元升级为 workspace/user/树/路径/工具面五层白名单，代价是记忆检索能力（无图遍历、词法兜底弱）明显朴素。

## 8. 附录：关键文件钉版地图（runtime/api-server/src/ 记忆子系统）

**服务与真相源**
- `memory.ts:22-28`：MemoryServiceLike 五接口
- `memory.ts:93-136`：路径白名单 + 穿越防御
- `memory.ts:250-262`：后端解析（只有文件系统）
- `memory.ts:318-335`：workspace/global 双根分流
- `memory.ts:388-476`：search 实现（词法兜底）
- `memory.ts:478-555`：get/upsert（root 内包含校验、append 语义）
- `memory.ts:557-617`：status/sync（图统计与全量重建）

**打分与检索**
- `memory-recall-index.ts:31-111`：意图加成表（问句类型×记忆类型）
- `memory-recall-index.ts:196-256`：recallBoost 起评 + 字段加权 + stale 惩罚
- `memory-recall-index.ts:270-284`：五元组排序（scope→type→score→freshness→updatedAt）
- `memory-recall.ts:14-21`：语义去重键 `scope:type:subject`
- `memory-recall.ts:23-93`：预算选择器（user≤2、类型配额、三重去重）
- `memory-recall.ts:95-149`：召回上下文组装 + selection_trace
- `memory-hybrid-retrieval.ts:90-106`：新鲜度推断（45 天阈值）
- `memory-hybrid-retrieval.ts:153-167`：策略归一化（max_evidence 钳 20）
- `memory-hybrid-retrieval.ts:234-267`：gap 生成（何时要求核验活数据源）
- `memory-hybrid-retrieval.ts:269-319`：retrieval pack 分节组装
- `memory-hybrid-retrieval.ts:321-415`：混合检索主管线 + coverage
- `memory-reranker.ts:78-116`：query overlap / highSignalScore 启发式
- `memory-embedding-index.ts:70-97`：embedding 文本模板与指纹
- `memory-embedding-index.ts:99-174`：同步状态机（disabled/deleted/skipped/indexed）

**写入与治理**
- `turn-memory-writeback.ts:89-94`：抽取路径退役注释（agent-invoked 转向）
- `turn-memory-writeback.ts:135-170`：显式风格偏好正则
- `turn-memory-writeback.ts:172-190`：记忆文件路径布局
- `turn-memory-writeback.ts:234-271`：确定性 memoryId + 治理注入
- `turn-memory-writeback.ts:399-434`：recordDurableMemoryFromInput（零 LLM 写入）
- `turn-memory-writeback.ts:514-576`：turn 工件索引 + 工具结果排除注释
- `memory-governance.ts:25-68`：六类记忆治理表
- `memory-governance.ts:83-144`：新鲜度评估与 note 文案
- `workspace-memory-graph.ts:41-114`：六类源树统一图
- `workspace-memory-graph.ts:229-278`：全量重建

**Agent 工具面（runtime/harnesses/src/）**
- `runtime-agent-tools.ts:127-135`：memory_retrieve/remember 定义
- `runtime-capability-tools.ts:444-495`：remember 参数 schema
- `runtime-capability-tools.ts:1482-1495`：工具使用指引（禁直读文件）
- `runtime-tool-capability-client.ts:25-26`：sidecar HTTP 路径
