# A-04 `rohitg00/agentmemory`（27K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\rohitg00__agentmemory
> TypeScript / ~635 文件 / MIT ｜ 面向编码 Agent 的持久记忆引擎 + MCP 服务器，构建在 iii-engine（Worker/Function/Trigger 三原语）之上，零外部数据库

## 1. 架构总览（目录地图，标出核心目录的职责）
- `src/hooks/` — 15 个 Claude Code 生命周期钩子入口（session-start/post-tool-use/pre-compact/stop…），是记忆**自动捕获**的入口；每个钩子是一个独立 Node 脚本，stdin 读 JSON → POST 到守护进程
- `src/functions/` — 60+ 个 `mem::*` Function（observe/remember/search/smart-search/consolidate-pipeline/retention/graph/context…），全部经 `sdk.registerFunction` 注册进 iii-engine，是记忆业务逻辑主体
- `src/state/` — 存储层：`kv.ts`（对 iii `state::get/set` 的薄封装）、`schema.ts`（KV 命名空间）、`search-index.ts`（BM25）、`vector-index.ts`（进程内余弦向量）、`hybrid-search.ts`（三路融合）
- `src/mcp/` — MCP stdio 服务器（43+ 工具），优先代理到运行中的 REST 守护进程，失败回退本地 `InMemoryKV`（`src/mcp/standalone.ts`）
- `src/triggers/api.ts` — REST API（/observe /remember /smart-search /context /graph…），viewer 与钩子共用
- `benchmark/` + `eval/` — LongMemEval-S / 自建 coding-agent-life-v1 / 负载压测
- `integrations/`、`plugin/`、`src/cli/connect/` — 对 12+ 编码 Agent（Codex/Cursor/Gemini CLI/OpenCode…）的接线器

## 2. 记忆机制深读（本笔记核心，每个论断必须钉 `相对路径:行号`）

### 2.1 写入/抽取管线（谁触发、prompt 是什么、结构化 schema）
- 捕获触发者是**宿主 Agent 的钩子**而非 LLM 决策：PostToolUse 钩子读 stdin JSON，把 tool_name/tool_input/tool_output（截断 8000 字符）POST 到 `/agentmemory/observe`，3 秒超时后 fire-and-forget（`src/hooks/post-tool-use.ts:41-58`）
- `mem::observe` 入口先做会话内去重（DedupMap 对 sessionId+toolName+toolInput 哈希，重复直接返回 `deduplicated:true`，`src/functions/observe.ts:64-79`），再过隐私清洗 `stripPrivateData`（API key/秘密脱敏，`src/functions/observe.ts:81-88`）
- **默认零 LLM 抽取**：`AGENTMEMORY_AUTO_COMPRESS` 关闭时走 `buildSyntheticCompression(raw)`——从 tool 名/输入/输出直接派生 type/title/narrative/files，随即写入 BM25 索引与向量索引（`src/functions/observe.ts:287-310`）。背景是 #138 事故：旧版每次工具调用都烧用户 Claude API token，被社区骂后改为 opt-in（`CHANGELOG.md:1023`）
- opt-in 的 LLM 路径 `mem::compress` 才调 provider；整合层 prompt 在 `src/prompts/consolidation.js`（SEMANTIC_MERGE_SYSTEM / PROCEDURAL_EXTRACTION_SYSTEM），要求模型按 `<fact confidence="...">` / `<procedure name="..." trigger="...">` 标签输出（解析见 `src/functions/consolidation-pipeline.ts:86-91,169-171`）
- 显式记忆写入 `mem::remember`：type 枚举 pattern/preference/architecture/bug/workflow/fact（`src/functions/remember.ts:50-60`），带 ttlDays 时写 `forgetAfter` 截止时间（`src/functions/remember.ts:129-131`）

### 2.2 存储后端与数据模型
- **没有独立数据库**：一切走 iii-engine 的 KV scope。命名空间约 50 个（`src/state/schema.ts:4-76`）：`mem:sessions`、`mem:obs:{sessionId}`（每会话一 scope）、`mem:memories`（显式记忆）、`mem:summaries`、`mem:semantic`、`mem:procedural`、`mem:graph:nodes/edges`、`mem:retention`、`mem:access`（访问日志）、`mem:lessons`、`mem:crystals` 等
- StateKV 是对 `state::get/set/update/delete/list` 触发器的薄封装（`src/state/kv.ts:6-46`）；BM25 倒排与向量经 `index-persistence.ts` 序列化到 KV（向量 Float32→base64，`src/state/vector-index.ts:8-21`）
- 版本/取代链：`mem::remember` 对已有 isLatest 记忆做 Jaccard 相似度比对，>0.7 视为同一事实的更新——旧记忆 `isLatest=false`，新记忆带 `version+1`、`parentId`、`supersedes[]`（`src/functions/remember.ts:86-96,107-127`）。Jaccard 对 CJK 做分词+二元 shingle，空 token 集回落精确匹配防空串误判（`src/state/schema.ts:102-154`）
- lesson 用内容 SHA256 指纹做幂等键：重复导入只 `reinforcements++`（`src/state/schema.ts:90-93`；机制描述见 `CHANGELOG.md:841`）

### 2.3 检索策略（向量/关键词/混合/重排/图，参数与阈值）
- 三路混合检索：BM25（权重 0.4）+ 向量（0.6）+ 知识图（0.3），RRF 融合 K=60（`src/state/hybrid-search.ts:20,30-33`；RRF 公式 `:215-218`）。某一路空结果时权重归一化重分配（`:194-206`）
- BM25 为手写实现，k1=1.2、b=0.75，Porter 词干+同义词扩展（`src/state/search-index.ts:19-20,118-123,258`）；向量为进程内暴力余弦（`src/state/vector-index.ts:23,38-50`），embedding 默认本地 all-MiniLM-L6-v2（384 维，免 API key）
- 图检索双通道：查询实体命中图节点 BFS（深度 2），再从向量 top-5 的 chunk 做图扩展（`src/state/hybrid-search.ts:100-126`）
- 后处理：按 session 多样性约束（每 session 最多 3 条，`src/state/hybrid-search.ts:242-276`）+ 可选 LLM 重排（`RERANK_ENABLED=true`，窗口 20，`:228-237`）
- 查询扩展 `searchWithExpansion`：把改写/时间具体化/实体抽取出的多查询并发检索后按最高分合并（`src/state/hybrid-search.ts:42-75`）

### 2.4 遗忘·整合·演化
- 四层整合管线 `mem::consolidate-pipeline`：semantic（≥5 条会话摘要才触发，取最近 20 条让 LLM 合成 `<fact>`；命中已有事实则 accessCount++ 且 confidence 取 max，`src/functions/consolidation-pipeline.ts:63-121`）、reflect、procedural（≥2 条频次≥2 的 pattern 才触发，抽 `<procedure>` 步骤；重复则 strength+0.1 封顶 1，`:150-229`）、decay
- retention 是类艾宾浩斯模型：`score = min(1, salience·e^(−λ·Δt) + boost)`，λ=0.01/天，boost=σ·Σ(1/距访问天数)（σ=0.3），分层阈值 hot≥0.7 / warm≥0.4 / cold≥0.15（`src/functions/retention.ts:20-28,65-95`）；salience 由记忆类型加权（architecture 0.9 > preference 0.85 > pattern 0.8 > bug 0.7 > fact 0.5）+ 访问加成（`:97-120`）
- 强化信号来自**真实读取**：每个检索端点 fire-and-forget 写 `mem:access`（每条记忆保留最近 20 次访问时间戳的环形缓冲，`CHANGELOG.md:1103`），`retention-evict` 对低于阈值的记忆做驱逐并按 source 字段路由到正确的 KV 删除（`CHANGELOG.md:905,968`）
- 每个结构化删除都写 `mem:audit` 审计行（治理策略块见 `src/functions/audit.ts` 头部；`CHANGELOG.md:903`）

### 2.5 注入上下文的方式
- `mem::context` 组装 `<agentmemory-context project="...">…</agentmemory-context>` XML 块：pinned slots → 项目画像（topConcepts/topFiles/conventions/commonErrors）→ Lessons（项目内×1.5 加权×confidence，取前 10）→ 最近 10 个会话摘要或高重要度观察（importance≥5 取前 5）（`src/functions/context.ts:73-231`）
- token 预算：estimateTokens = ceil(len/3)，块按 recency 降序装包，放不下整块跳过（`src/functions/context.ts:22-24,234-250`）
- 注入默认**关闭**（`AGENTMEMORY_INJECT_CONTEXT`，`.env.example:109`）：钩子只捕获不改写对话——这是 #143 教训（SessionStart stdout 会真的进入模型上下文，`CHANGELOG.md:966`）
- 多 Agent 隔离：`AGENTMEMORY_AGENT_SCOPE=isolated` 时 context/search 全部 fail-closed，解析不出 agentId 直接拒绝读（`src/functions/context.ts:54-71`）

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）

① 默认零 LLM 的合成压缩写入路径（`src/functions/observe.ts:297-310`）：
```ts
} else {
  const synthetic = buildSyntheticCompression(raw);
  await kv.set(KV.observations(payload.sessionId), obsId, synthetic);
  getSearchIndex().add(synthetic);
  await vectorIndexAddGuarded(
    synthetic.id, synthetic.sessionId,
    synthetic.title + " " + (synthetic.narrative || ""),
    { kind: "synthetic", logId: synthetic.id },
  );
```

② RRF 三路融合（`src/state/hybrid-search.ts:208-219`）：
```ts
const combined = Array.from(scores.entries()).map(([obsId, s]) => ({
  obsId, sessionId: s.sessionId,
  bm25Score: s.bm25Score, vectorScore: s.vectorScore, graphScore: s.graphScore,
  graphContext: s.graphContext,
  combinedScore:
    effectiveBm25W * (1 / (RRF_K + s.bm25Rank)) +
    effectiveVectorW * (1 / (RRF_K + s.vectorRank)) +
    effectiveGraphW * (1 / (RRF_K + s.graphRank)),
}));
```

③ 记忆保留分（艾宾浩斯衰减+强化，`src/functions/retention.ts:81-95`）：
```ts
function computeRetention(salience, createdAt, accessTimestamps, config) {
  const deltaT = (Date.now() - new Date(createdAt).getTime()) / (1000*60*60*24);
  const temporalDecay = Math.exp(-config.lambda * deltaT);
  const reinforcementBoost = computeReinforcementBoost(accessTimestamps, config.sigma);
  return Math.min(1, salience * temporalDecay + reinforcementBoost);
}
```

④ Jaccard 版本取代（`src/functions/remember.ts:86-96`）：
```ts
const similarity = jaccardSimilarity(lowerContent, existing.content.toLowerCase());
if (similarity > 0.7) {
  supersededId = existing.id;
  supersededVersion = existing.version ?? 1;
  supersededMemory = existing;
  break;
}
```

⑤ 基准口径：recall_any@K（`benchmark/longmemeval-bench.ts:48-55`）：
```ts
function recallAny(retrievedSessionIds, goldSessionIds, k) {
  const topK = new Set(retrievedSessionIds.slice(0, k));
  return goldSessionIds.some((gid) => topK.has(gid)) ? 1.0 : 0.0;
}
```

## 4. 基准/评测声明（反虚荣视角：自封 or 第三方？可复现？数字与口径）
- 头条数字：LongMemEval-S R@5 = 95.2%（BM25+Vector，all-MiniLM-L6-v2），BM25-only 86.2%（`benchmark/LONGMEMEVAL.md:15-18`）。口径为 **retrieval-only recall_any@K，无 LLM、无答案生成、无 judge**（`benchmark/LONGMEMEVAL.md:9-11`），README 自己声明"不 claim 为 LongMemEval 分数"（`:59-61`）
- **判定：[自封]（self-run，可复现但非第三方、非同数据横比）**。95.2% 是其自跑数字；对比表里 MemPalace 自报 96.6% 实际**高于** agentmemory，且 mem0/Letta 用的是另一个数据集 LoCoMo——repo 自己在 COMPARISON.md 写明"apples vs oranges caveat… Treat them as ballpark vendor claims"（`benchmark/COMPARISON.md:22`）。"#1 编码 Agent 记忆"式表述即使按其自家表格也不成立，属营销性自封
- 可复现性较好：数据集 HF 公开、脚本入库（`npm run bench:longmemeval`，`benchmark/LONGMEMEVAL.md:64-79`）；基准用 MockKV 内存态跑干净管线（`benchmark/longmemeval-bench.ts:92-111`）。load 基准可播种子复现（`benchmark/README.md:86-94`）
- Token 效率声明（~170K vs 650K/19.5M tokens/年，`benchmark/COMPARISON.md:57-64`）是推算型口径，无外部审计

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）
- **零 LLM 默认管线**：工具调用的结构化输出本身就是"已压缩记忆"，synthetic compression 让捕获成本恒为 0——比 mem0 的"每次 add 都过 LLM 抽取"更适合高频编码场景（`src/functions/observe.ts:283-310`）
- **读取即强化**：把"被检索命中"作为记忆强化的第一信号源，环形缓冲 20 次访问时间戳驱动 retention——遗忘不是定时删除而是连续分数（`src/functions/retention.ts:65-95`）
- **钩子侧捕获 + 默认不注入**：捕获（写路径）与注入（读路径）解耦，注入默认 off 防止 token 隐性膨胀（`.env.example:109`）——大多数记忆系统默认双向打开
- **fail-closed 的多租户过滤**：isolated 模式解析不出 agentId 就拒绝读而非放行（`src/functions/smart-search.ts:118-130`）
- **会话多样性约束**（maxPerSession=3）作为廉价 MMR 替代，防止一个长会话淹没结果页（`src/state/hybrid-search.ts:242-276`）
- **删除必审计**：所有结构性删除写 audit 行，遗忘可追责（`CHANGELOG.md:903`）

## 6. 局限与风险（失败模式、安全隐患、工程债）
- 向量检索是进程内暴力余弦，无 ANN（HNSW/IVF）；100K 规模靠引擎整体快照与预计算图快照续命（`src/state/schema.ts:19-40` 注释承认 75K 节点时 kv.list 会阻塞 worker）
- 版本取代用 Jaccard>0.7 单阈值：词面相似但语义相反的两条记忆（"用 X"/"别用 X"）会被误取代——无语义级冲突检测
- 历史安全债实锤：v0.8.2 有 6 份 CVE 草案（viewer XSS、curl-sh RCE、默认 0.0.0.0 绑定、未认证 mesh 同步、Obsidian 导出路径穿越、秘密脱敏不完整，`CHANGELOG.md:899`）；跨 Agent 记忆泄漏 #1057（`CHANGELOG.md:60`）
- 强耦合 iii-engine（pin v0.11.2，`README.md:104`），自托管等于连带部署一套 Rust 引擎；MCP standalone 回退 InMemoryKV 意味着无守护进程时记忆不可持久共享
- 基准口径偏软：recall_any@K（任一 gold 命中即 1 分）宽松于全量召回；95.2% 是会话级检索而非答案准确率（`benchmark/LONGMEMEVAL.md:57-62`）

## 7. 一句话对比 mem0
agentmemory 把 mem0 的"API 层记忆"换成"钩子自动捕获 + 零 LLM 默认压缩 + RRF 三路混合 + 连续衰减分"的本地编码 Agent 基建：写入几乎免费、检索更工程化，但基准是自跑的检索口径而非 mem0 的 LoCoMo QA 口径，且用暴力向量与单阈值 Jaccard 换来了零依赖。
