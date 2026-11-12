# A-21 `CaviraOSS/OpenMemory`（4.4K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\CaviraOSS__OpenMemory
> TypeScript + Python 双 SDK：packages/openmemory-js（server+core 90 文件）+ openmemory-py + VS Code 扩展 + Next.js dashboard / MIT
> 一句话定位：本地优先（SQLite/Postgres）"认知记忆引擎"——五扇区 HSG 图记忆 + 时间知识图谱，经 HTTP context-provider 或 MCP 双通道喂给 Claude Code/Codex/Copilot/Cursor/Windsurf
> ⚠️ README:1-3 自述 "currently being rewritten, expect breaking changes"——main 处于重写过渡态，贡献引导到 rewrite 分支

## 1. 架构总览（目录地图，标出核心目录的职责）

- `packages/openmemory-js/src/core/`：基础设施层
  - `db.ts`（38KB）：SQLite/Postgres 双后端建表 + 预编译语句表（q_type 定义 20+ 语句，db.ts:21-59）
  - `vector/postgres.ts`：pgvector 后端；`vector/valkey.ts`：Redis 族向量后端（SCAN 游标遍历，valkey.ts:49-61）
  - `cfg.ts`：OM_TIER 分层配置（fast/smart/deep/hybrid）
  - `identifiers.ts`：assertSafeIdentifier 防 SQL 注入；`migrate.ts`：迁移
- `packages/openmemory-js/src/memory/`：记忆核心
  - `hsg.ts`（45KB）：五扇区分类 + waypoint 图 + hsg_query 混合评分 + add_hsg_memory 写入
  - `decay.ts`：冷热分层衰减 + 向量/摘要物理压缩
  - `reflect.ts`：定时聚类反思；`embed.ts`：多供应商嵌入；`user_summary.ts`：用户画像摘要
- `packages/openmemory-js/src/temporal_graph/`：temporal_facts/edges 时间知识图谱与 timeline/as-of 查询
- `packages/openmemory-js/src/server/`：
  - `routes/ide.ts`：IDE 事件/上下文 HTTP 适配面（本笔记重点）
  - `routes/`：memory/dynamics/dashboard/temporal/sources/users 等
  - `middleware/`：auth（API key）、tenant（租户校验）、validate（schema 校验）、webhook
- `packages/openmemory-js/src/ai/`：LLM/记忆适配层——`graph.ts`（LangGraph 集成）、`mcp.ts`（36KB，MCP server）、`mcp_tools.ts`（ToolRegistry）
- `packages/openmemory-js/src/sources/`：数据源连接器——github / notion / google_drive / google_sheets / google_slides / onedrive / web_crawler（与 py 版 connectors 一一对应）
- `packages/openmemory-js/src/ops/`：ingest（摄取）/ extract（抽取）/ compress（压缩）/ dynamics（动态）四操作
- `packages/openmemory-js/src/utils/`：chunking / keyword（BM25 式关键词）/ text（canonical_token_set、stable_text_fallback_hash）
- `apps/vscode-extension/src/`：**多客户端配置写入器** writers/（claude/codex/copilot/cursor/windsurf 五件套）+ IDE 事件钩子 + Dashboard 面板
- `packages/openmemory-py/`：Python 镜像实现（migrations/001_initial.sql 为其初始 schema，与 JS 版已有漂移）
- `dashboard/`：Next.js 管理台（memories/decay/timeline/settings）

## 2. 记忆机制深读

### 2.1 写入/抽取管线

- 统一入口 `add_hsg_memory(content, tags, metadata, user_id, project_id)`（hsg.ts:1146）：
  1. **simhash 去重先行**：compute_simhash 后按 simhash 查已有记忆，海明距离 ≤3 视为重复——不新建而是 salience+0.15（封顶 1）并刷新 last_seen，返回 `deduplicated:true`（hsg.ts:1159-1171）——去重零 LLM 成本，重复本身成为强化信号
  2. 内容切 chunk（长文本多向量）；classify_content 正则分扇区
  3. `extract_essence()` 按扇区抽取精华文本存储（受 summary_max_length 限制，hsg.ts:1196-1200）
  4. 初始 salience = 0.4 + 0.1×附加扇区数（hsg.ts:1202-1205）
  5. 多扇区嵌入：primary+additional 各存一条向量（vectors 表）；softmax(β×扇区权重) 加权 mean_vec 存回 memories 行（hsg.ts:1227-1245, 528-554）
  6. smart 档另存 128 维压缩向量（hsg.ts:1247-1251）
  7. 建 waypoint 边 + 事务提交（hsg.ts:1253-1254）
- **segment 物理分片轮转**：每段 seg_size 条，满了 segment 自增（hsg.ts:1185-1195）——为冷段批量扫描/归档预留的廉价分片
- IDE 自动捕获（无 LLM）：
  - VS Code 扩展监听文档 open/save/close → POST /api/ide/events → 事件文本（"Saved file: {path}\n\n{content}"）直接进 HSG（ide.ts:60-87）
  - 会话 start/end 生成会话级摘要记忆（"Session started: user in project using ide"/含 sector 分布与文件清单的统计摘要，ide.ts:185-201, 270-286）
  - 事件元数据带 ide_event_type/ide_file_path/ide_session_id/ide_mode:true（ide.ts:73-80）
- 嵌入可全离线：`OM_EMBEDDINGS` 默认 "synthetic"（哈希伪向量，cfg.ts:40），可配 OpenAI/Gemini/AWS/MiniMax/Siray/Ollama（ai/ 目录各 adapter）
  - 嵌入失败降级链 OM_EMBEDDING_FALLBACK（逗号分隔供应商列表，cfg.ts:41-44）；嵌入延迟 200ms 节流（cfg.ts:47）
  - 用户画像 user_summary.ts：写入/会话事件异步更新 users.summary（ide.ts:89-91 的 fire-and-forget 模式）——画像即最高层"记忆摘要"
  - 压缩 ops/compress.ts：OM_COMPRESSION_ALGORITHM 四档 semantic/syntactic/aggressive/auto，min_length 100（cfg.ts:33-39）
- 写入管线基本**零 LLM**——与 mem0 的"LLM 抽取"路线根本不同

### 2.2 存储后端与数据模型（本地持久化 schema，本笔记重点）

- 后端选择：默认 SQLite（`data/openmemory.sqlite`，cfg.ts:25-28；db.ts:501）；`OM_METADATA_BACKEND=postgres` 切 pg（db.ts:73-81）
  - pg 自动建库（3D000 时连 postgres 库 CREATE DATABASE，db.ts:162-180）、自动 `create extension vector`（db.ts:181）
  - 库名/表名/schema 名全过 assertSafeIdentifier（db.ts:84, 96-107）；占位符 `?`→`$n` 自动转换兼容两方言（db.ts:75-79）
  - 初始化失败不 process.exit：捕获为 DbInitError 经 wait_ready 轮询暴露给宿主（db.ts:148-161, 278-287）——SDK 嵌入宿主进程的礼貌行为
  - Valkey 向量后端：向量不落 SQL 表，走 Redis 族存储（SCAN 游标遍历 + 相似度计算，valkey.ts:49-61, 132-147）
- Postgres 完整 DDL（db.ts:181-234）：
  - **memories**：`id uuid PK, user_id text, project_id text, segment int default 0, content text, simhash text, primary_sector text, tags text, meta text, created_at/updated_at/last_seen_at bigint, salience double precision, decay_lambda double precision, version int default 1, mean_dim int, mean_vec bytea, compressed_vec bytea, feedback_score double precision default 0`（db.ts:184）
    - decay_lambda 按行存——写入时取该记忆扇区的默认 λ（hsg.ts:1220），支持逐条调速率
    - 索引：primary_sector / segment / simhash / user_id（db.ts:236-246）
  - **vectors**：`(id uuid, sector text, user_id, project_id, v vector, dim int)` PK(id,sector)；pgvector **HNSW 索引 vector_cosine_ops**（db.ts:187-192）；向量后端可整体切 Valkey（db.ts:264-276）
  - **waypoints**（记忆图边）：`(src_id, dst_id, user_id, project_id, weight double, created_at, updated_at)` PK(src_id,user_id)（db.ts:194）
  - **temporal_facts**：`(id uuid, user_id, project_id, subject, predicate, object, valid_from bigint, valid_to, confidence double CHECK 0..1, last_updated, metadata)` + `unique(subject,predicate,object,valid_from)`（db.ts:206）
  - **temporal_edges**：`(id, source_id FK, target_id FK, relation_type, valid_from, valid_to, weight, metadata)`（db.ts:212）
  - 时间索引：(valid_from,valid_to)、(subject,predicate,valid_from,valid_to)、source/target/validity（db.ts:217-234）——支持 as-of 时间点查询
  - 辅助表：embed_logs（嵌入失败重试队列）、openmemory_users（summary+reflection_count）、stats（type/count/ts）
- SQLite 全套镜像 DDL（db.ts:550-592）：同构但 vector 为 BLOB、时间列为 integer；遗留 `vectors` 表名迁移告警（db.ts:516-529）；显式开 foreign_keys（db.ts:543）
- Python 版 001_initial.sql 无 project_id 列、多 vectors/stats 旧结构（001_initial.sql:2-24）——双语言 schema 已漂移

### 2.3 检索策略（HSG 混合评分的参数与阈值）

- **五扇区认知分类**（sector_configs，hsg.ts:50-138）：每扇区 = {model 标签, decay_lambda, weight, 中英文正则 patterns[]}
  - episodic：λ=0.015, w=1.2（"yesterday/remember when/昨天/上周/周X"…）
  - semantic：λ=0.005, w=1.0（"is a/defined as/指的是/概念/事实"…）
  - procedural：λ=0.008, w=1.1（"how to/step by step/怎么安装/第一步"…）
  - emotional：λ=0.02, w=1.3（"feel/happy/!!!/开心/讨厌"…）
  - reflective：λ≈, w=1.1（"learned/lesson/复盘/教训/领悟"…）
- 跨扇区关系惩罚矩阵 sector_relationships（0.3~0.8，如 semantic→procedural 0.8、emotional→procedural 0.3，hsg.ts:166-197）
- 查询流（hsg_query，hsg.ts:832-1011）：
  1. 查询文本先分类（classify_content）+ 时间标记检测
  2. **对每个扇区分别嵌入查询向量**（embedQueryForAllSectors）
  3. 每扇区检索 k×3 近邻（vector_store.searchSimilar）
  4. 自适应扩容：`eff_k = k + ceil(0.3×k×(1-avg_top))`——top 平均相似度低时多检（hsg.ts:894-901）
  5. avg_top < 0.55（低置信）时触发 waypoint 图扩展 expand_via_waypoints（hsg.ts:902-907）
  6. hybrid 档：对候选跑 keyword_filter_memories（阈值 0.05）
  7. 逐条复合评分 + 项目过滤 + 时间过滤
- 混合评分（compute_hybrid_score，hsg.ts:471-488）：
  `sigmoid(0.35×boosted_sim + 0.2×token重叠 + 0.15×waypoint权重 + 0.1×recency + 0.2×tag匹配 + keyword_boost×2.5)`
  （权重表 scoring_weights，hsg.ts:140-146；keyword_boost cfg.ts:117）
- 扇区惩罚：记忆扇区 ≠ 查询主扇区且不在附加集时，相似度 ×sector_relationships 系数（默认 0.3，hsg.ts:962-972）
- 项目隔离：命中当前 project_id、或 `system_global`、或 legacy null 才通过；匹配项目再 logit +0.2 加成（hsg.ts:936-941, 998-1001）
- 多向量融合分 calc_multi_vec_fusion_score：查询各扇区向量与记忆各扇区向量按维度权重融合（查询主扇区权重 1.1~1.5、非主 0.5~0.8，hsg.ts:870-878）
- 工程参数：查询缓存 TTL 60s（hsg.ts:774）；并发限流 max_active 按 tier 32/64/128/64（hsg.ts:844-848；cfg.ts:21）；OM_TIER 四档（fast/smart/deep/hybrid，dims 全 1536、cache 2/3/5/3，cfg.ts:8-21）

### 2.4 遗忘·整合·演化

- **冷热分层 + 物理压缩**（decay.ts）：
  - pick_tier：`hot`（<6 天 且 coactivations>5 或 salience>0.7）/ `warm`（<6 天 或 salience>0.4）/ `cold`（decay.ts:88-95）
  - 日衰减 λ：hot 0.005 / warm 0.02 / cold 0.05（decay.ts:74-76）；cold_threshold=0.25（decay.ts:65）
  - cold 记忆降分辨率：向量均值池化压缩到 64~1536 维（compress_vector，decay.ts:97-116）；摘要按保留率分级退化——f>0.8 截 200 字、f>0.4 摘要 80 字、再低退化为 top 关键词（compress_summary，decay.ts:118-128）
  - 终态 fingerprint：32 维 FNV 哈希伪向量 + 3 个关键词（decay.ts:131-137）——"记忆变冷即降分辨率"，仍可命中但精度让位
  - 支持 regeneration 反向恢复（decay.ts:70）；衰减线程数 OM_DECAY_THREADS=3、冷却 60s（decay.ts:64, 84）
- waypoint 图演化（hsg.ts:158-164, 498-649）：
  - 三种建边：跨扇区边（w=0.5 双向）/ 同扇区高相似边（cos≥0.75，w=0.5 双向）/ 上下文边（同批相关，w=0.3 起，重复共现 +0.1 封顶 1.0）
  - 检索路径 reinforce（waypoint_boost 0.05）；弱边 <0.05（prune_threshold）剪枝（prune_weak_waypoints）
  - 查询命中 reinforce：salience +0.1（salience_boost）封顶 1.0
- **自动反思**（reflect.ts:113-159）：定时（默认 10 分钟）聚类近期记忆（最少 20 条否则跳过），每组生成 reflect:auto 摘要记忆（meta.sources 记录成员 id、freq），源记忆 salience×1.1 提升并更新——"反思产生新记忆且反哺旧记忆"
  - 反思摘要 salience 由簇频率决定（`sal(c)`）；源记忆被 mark 标记已反思防重复（reflect.ts:129-141）
  - 反思计数存 users.reflection_count（db.ts:200），维护操作记 log_maint_op("reflect", n)（reflect.ts:145）
  - 定时器由 env.auto_reflect 开关、reflect_interval 分钟间隔（reflect.ts:152-159）
- 时间事实演化：temporal_graph 存 SPO+有效期三元组；temporal 路由做 as-of 求值（temporal_graph/query.ts）；confidence CHECK 约束 0..1
  - timeline.ts 提供时间线重构（dashboard /timeline 页消费）
  - temporal_edges.relation_type 区别于 waypoints 的纯相似度边——是带语义类型的实体关系边
- 语义压缩双轨：ops/compress.ts 的内容压缩（semantic/syntactic/aggressive/auto）与 decay.ts 的冷记忆降分辨率是两层独立机制

### 2.5 注入上下文的方式（多客户端适配层，本笔记重点）

双通道适配——同一后端 `node dist/ai/mcp.js`（stdio MCP）或 HTTP `POST /api/ide/context`：

- **writers 五件套**（VS Code 扩展 setup 一键全写，extension.ts:192-196）：
  - **Claude Code** → `~/.claude/providers/openmemory.json`（claude.ts:40-52）
    - HTTP 模式：`{provider:'http', base_url:'<url>/api/ide/context', api_key}`
    - MCP 模式：`{mcpServers.openmemory:{command:'node', args:[mcp.js], env:{OM_API_KEY}}}`（claude.ts:18-29）
  - **Codex** → `~/.codex/context.json`（codex.ts:57-69）
    - HTTP：`{contextProviders.openmemory:{enabled:true, endpoint, method:'POST', headers:{x-api-key}, queryField:'query'}}`
    - MCP：`{mcpServers.openmemory:{command:'node',args:[mcp.js]}}` + env（codex.ts:24-38）
  - **Copilot** → `~/.github/copilot/openmemory.json`（copilot.ts:53-65）
    - MCP：`{name:'OpenMemory', type:'mcp', mcpServer:{...}}`
    - HTTP：`{type:'context_provider', endpoint, authentication:{type:'header', header:'x-api-key: ...'}}`
  - **Cursor / Windsurf** 同构（cursor.ts / windsurf.ts）
  - 全部走"生成配置对象 → 建目录 → JSON.stringify 写文件"三步，返回配置路径
- **HTTP 适配面** `/api/ide/context`（ide.ts:105-165）：
  - 入参 `{query(必填,≤8192), k|limit(默认 5,≤200), session_id, file_path}`
  - hsg_query 后按 meta.ide_session_id 过滤 + content 含 file_path 过滤（应用层后过滤）
  - 返回 `{memory_id, content, primary_sector, sectors, score, salience, last_seen_at, path}` JSON——由各客户端宿主原生注入机制消费
- 其余 IDE 端点：/api/ide/events（事件入库）、/api/ide/session/start|end（会话摘要）、/api/ide/patterns/:session_id（procedural 扇区的模式提取，ide.ts:313-351）
  - patterns 端点把"本会话干了什么"抽象为 procedural 扇区记忆列表：`{pattern_id, description, salience, detected_at, last_reinforced}`（ide.ts:333-339）——工作流模式的显式产出面
- 通用 REST 面：memory / dynamics / temporal / sources / users / dashboard / vercel / langgraph 等路由（routes/index.ts），供 SDK 与 dashboard 消费
- MCP 面：server 名 "openmemory-mcp"（mcp.ts:122），七工具 openmemory_query / store / store_project / reinforce / delete / list / get（mcp.ts:130-864）
  - 工具参数内嵌 user_id/project_id 隔离描述（"Isolate results to a specific user identifier"，mcp.ts:199, 206）
  - store 与 store_project 分离：后者显式带 project_id 写项目级全局记忆（注释提议未来改名 store_global，mcp.ts:339, 488）
  - reinforce 工具：按 id 手动强化记忆（"Memory identifier to reinforce"，mcp.ts:600）
  - temporal 查询支持 min_confidence 过滤（默认 0.0）与置信度 4 位小数格式化（mcp.ts:262-273）
  - ToolRegistry 统一 zod→jsonSchema2019-09 转换与校验（mcp_tools.ts:43-56）
  - MCP SDK 1.27 拒绝重复初始化 → 多客户端连接复用同一 server 实例（mcp.ts:920 注释）
- **多租户**：`require_tenant` + `reject_tenant_mismatch`（body user_id 必须匹配认证租户，ide.ts:6, 39-50, 176）；MCP 侧同样拒绝（"tenant_mismatch: user_id does not match authenticated tenant"，mcp.ts:100-111）；openmemory_store_project 写全局需 project_id（mcp.ts:339, 488）
  - API 鉴权：OM_API_KEY + auth 中间件（cfg.ts:29；middleware/auth.ts 7KB）；速率限制 OM_RATE_LIMIT_*（默认 60s 窗口 100 次，cfg.ts:30-32）
  - 租户中间件独立成 tenant.ts（2KB），validate 中间件做 schema 长度/类型校验（max_length 防超长注入，ide.ts:9-35）

## 3. 关键代码摘录

```ts
// packages/openmemory-js/src/memory/hsg.ts:1159-1171（simhash 去重：重复→强化）
const simhash = compute_simhash(content);
const existing = await q.get_mem_by_simhash.get(simhash);
if (existing && hamming_dist(simhash, existing.simhash) <= 3) {
    const now = Date.now();
    const boosted_sal = Math.min(1, existing.salience + 0.15);
    await q.upd_seen.run(existing.id, now, boosted_sal, now);
    return { id: existing.id, primary_sector: existing.primary_sector,
             sectors: [existing.primary_sector], deduplicated: true };
}
```

```ts
// packages/openmemory-js/src/memory/hsg.ts:140-146 + 471-487（混合评分权重与公式）
export const scoring_weights = {
    similarity: 0.35, overlap: 0.2, waypoint: 0.15, recency: 0.1, tag_match: 0.2,
};
const raw = scoring_weights.similarity * s_p + scoring_weights.overlap * tok_ov
          + scoring_weights.waypoint * wp_wt + scoring_weights.recency * rec_sc
          + scoring_weights.tag_match * tag_match + keyword_score;
return sigmoid(raw);
```

```ts
// packages/openmemory-js/src/memory/decay.ts:88-95 + 74-76（冷热分层判据与衰减速率）
const recent = dt < 6 * 86_400_000;
const high = (m.coactivations || 0) > 5 || (m.salience || 0) > 0.7;
if (recent && high) return "hot";
if (recent || (m.salience || 0) > 0.4) return "warm";
return "cold";
// lambda_hot: 0.005, lambda_warm: 0.02, lambda_cold: 0.05（time_unit_ms: 86400000 即按天）
```

```sql
-- packages/openmemory-js/src/core/db.ts:206（时间事实表：SPO + 有效期 + 置信度约束 + 唯一性）
create table if not exists "${sc}"."temporal_facts"(id uuid primary key, user_id text,
  project_id text, subject text not null, predicate text not null, object text not null,
  valid_from bigint not null, valid_to bigint, confidence double precision not null
  check(confidence >= 0 and confidence <= 1), last_updated bigint not null, metadata text,
  unique(subject, predicate, object, valid_from))
```

```ts
// apps/vscode-extension/src/writers/claude.ts:32-37 与 codex.ts:44-53（双通道配置生成）
// Claude HTTP:  { provider: 'http', base_url: `${backendUrl}/api/ide/context` }
// Codex  HTTP:  { contextProviders: { openmemory: { enabled: true,
//                endpoint: `${backendUrl}/api/ide/context`, method: "POST",
//                headers: { "x-api-key": apiKey }, queryField: "query" } } }
```

## 4. 基准/评测声明（反虚荣视角）

- README 无任何基准数字（无 LoCoMo/LongMemEval 类评测）。[无基准声明]
- deepwiki 叙述聚焦架构（三接口：HTTP API / MCP / SDK）与"非 RAG、非向量库"定位，未见评测表 [deepwiki-未验证]
- examples/（node/python 的 agents/integrations/patterns/rag）可人工验证；dashboard 提供人工检视面
- 项目自宣重写中（README:1-3），API 稳定性差，第三方复现意义有限；测试存在但覆盖密度远低于 A20

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）

1. **冷记忆降分辨率**：不删旧记忆，而是向量均值池化到 64 维、摘要退化到关键词、终态 32 维哈希指纹——存储与召回成本随温度连续变化，比 mem0 的"全量保留 or 删除"更平滑
2. **simhash+海明 ≤3 预去重门**：在嵌入/LLM 之前拦截重复，重复内容转化为 salience 强化信号——把去重从成本项变成强化机制
3. **每扇区独立嵌入查询**（同一 query 在 5 个扇区空间各算相似度）+ 跨扇区惩罚矩阵——认知类型先验进入向量检索本身；mem0 只有单一语义空间
4. **低置信触发图扩展**：top 平均相似度 <0.55 才沿 waypoint 扩散 + 自适应 eff_k——图检索作为向量检索的兜底而非常驻成本
5. **五客户端 writer + 双通道适配矩阵**：一份 generateXxxConfig(useMCP) 覆盖 HTTP context-provider 与 MCP stdio 两种宿主协议，写入各客户端约定路径（~/.claude/providers/、~/.codex/context.json…）——比 A19 的标记块注入更"配置原生"（不改写用户文件内容）
6. segment 物理分片轮转：为大批量冷扫描/归档预留的廉价分片设计
7. temporal_facts 用关系型约束（CHECK + unique + 复合有效期索引）保证时间知识图谱一致性——不引入图数据库

## 6. 局限与风险

- 扇区分类纯正则（中英文模式表硬编码）——领域外文本（代码、小语种）分类噪声大且不可配置
- hsg_query 对候选逐条 `q.get_mem.get`（hsg.ts:930-931）、/api/ide/session/end 拉全量 10000 条内存过滤（ide.ts:241-249）——N+1 与全扫描，规模上千后明显退化
- SQLite 路径向量检索为 JS 手写线性扫描，仅 Postgres+pgvector 有 HNSW——"本地优先"默认配置恰是性能最弱路径
- 双语言实现 schema 已漂移（py 无 project_id，001_initial.sql:2-24 vs db.ts:184）；扩展代码含自我怀疑式注释（extension.ts:179-184 "I need to be careful…"）——工程质量波动明显
- 默认嵌入 synthetic（哈希伪向量，cfg.ts:40）：开箱语义检索质量有限，需显式配真实嵌入供应商
- README 自述重写中：API 随时 breaking，生产采用需绑定 commit

## 7. 一句话对比 mem0

mem0 用"LLM 抽取-更新"换记忆质量；OpenMemory 走**零 LLM 系统化路线**——正则扇区分类 + simhash 去重 + 图扩散 + 冷热压缩全确定性，靠 HSG 五扇区与时间图谱模拟认知结构，把 LLM 完全踢出热路径，代价是语义理解上限被嵌入与正则锁死。
