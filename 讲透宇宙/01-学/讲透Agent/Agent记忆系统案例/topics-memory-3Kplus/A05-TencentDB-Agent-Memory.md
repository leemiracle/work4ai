# A-05 `TencentCloud/TencentDB-Agent-Memory`（21.7K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\TencentCloud__TencentDB-Agent-Memory
> TypeScript 为主（少量 Python SDK）/ ~918 文件 / Apache-2.0 ｜ 面向团队 Agent 的四类记忆资产（Chat Memory / Skill / LLM-Wiki / Code-Graph）统一存储与治理平面：MemoryCore 存储+处理，MemoryKnowledge 解析+索引，MemoryProxy 透明 LLM 代理注入，MemoryPanel 管理 UI

## 1. 架构总览（目录地图，标出核心目录的职责）
- `MemoryCore/` — 记忆与元数据核心，HTTP Gateway（:8420）。`src/core/record/`（L1 抽取/去重/写入）、`src/core/conversation/`（L0 记录）、`src/core/hooks/`（auto-recall 自动召回注入）、`src/core/skill/`（Skill 资产）、`src/core/store/`（SQLite FTS5 + vec0 + 腾讯云 VectorDB 客户端）、`src/gateway/`（REST）、`src/offload*/`（上下文卸载/压缩）
- `MemoryKnowledge/` — 知识内容引擎：`src/engines/wiki/`（LLM-Wiki 摄取 v2 + BM25/图谱检索）、`src/engines/code/`（封装 @colbymchenry/codegraph 做 Code-Graph）、`src/db/schema.ts`（Drizzle/SQLite 元数据）、`src/routes/`（wiki/code-graph/auto-sync REST）、`src/mcp/`（MCP 工具）
- `MemoryProxy/` — 透明 LLM 请求代理（:8096）：改写 OpenAI/Anthropic 协议两侧做会话初始化、上下文注入、对话回写，"Agent 零改码接入"（`MemoryProxy/README.md:1-8`）
- `MemoryPanel/` — 管理面板；`sdk/memory-core` — TS/Py SDK

## 2. 记忆机制深读（本笔记核心）

### 2.1 Chat Memory（L0→L1→L2→L3）写入/抽取管线
- **L0 全量捕获**：agent_end 钩子把原始对话逐条写入 `conversations/YYYY-MM-DD.jsonl`（每行一条消息，日分片、全 session 合并），消息先 sanitize 去注入标签防反馈回路、过滤短/长/命令噪声（`MemoryCore/src/core/conversation/l0-recorder.ts:1-15`）
- **L1 LLM 抽取**：`extractL1Memories` 先过质量门 `shouldExtractL1`（长度/符号/prompt-injection 过滤，`MemoryCore/src/core/record/l1-extractor.ts:161-175`），取最近 10 条新消息+5 条背景消息（`:149-150,178-182`），**单次 LLM 调用同时完成场景切分+记忆抽取**（SceneSegment{scene_name, message_ids, memories[]}，`:51-62`），每会话上限 10 条记忆（`:152,256-261`）
- 记忆类型枚举 v3：persona/episodic/instruction + 工作态 work_fact/work_task/work_method/work_artifact；旧类型 preference 折叠进 persona（`MemoryCore/src/core/record/l1-writer.ts:30-38`；`l1-extractor.ts:726-737`）
- **LLM 判重（两阶段）**：候选召回（向量余弦优先→FTS5 BM25 降级→都无则直接 store，`MemoryCore/src/core/record/l1-dedup.ts:36-42,99-130`）→ 单次批量 LLM 判决，动作四选一 store/update/merge/skip，带 merged_content/merged_type/merged_priority 跨类型合并字段（`l1-writer.ts:114-130`）；判重失败降级为全量 store（`l1-dedup.ts:186-195`）
- **双写策略**：JSONL 追加式为备份/恢复真源，SQLite 向量库为主检索引擎；update/merge 实时删旧行，JSONL 由 memory-cleaner 周期清理（`l1-writer.ts:7-12`）
- 全链路溯源：每次生成写 MemoryGenerationLog（layer/model/prompt_mode/latency/input_refs→output_refs），prompt 版本可追责（`l1-extractor.ts:344-379`）

### 2.2 Skill（技能资产）：数据模型与治理
- 模型：单表多行多版本——`skills` 表每行 = (skill_id, version) 不可变快照，UNIQUE(skill_id,version)+head 唯一索引 `(team_id, owner_agent_id, name) WHERE is_head=1 AND status='active'`（`MemoryCore/src/core/skill/skill-store-ddl.ts:21-65`）；`skill_fts`（FTS5，unicode61 分词，content 截 4000 字，`:71-104`）+ `skill_vec`（sqlite-vec vec0 虚拟表，cosine，`:92-97`）
- 治理机制（6 写 4 读动作）：create/update/patch/delete(归档 status=archived)/writeFiles/removeFiles；写前 `assertTeamMatch / assertOwner / assertVersionFresh` 三重权限校验（`MemoryCore/src/core/skill/skill-core.ts:1-23,26-37`）；skill_id 用 CSPRNG base62 71-bit 熵（`:100-104`）；旧版本 TTL 可过期（versionTtlSeconds）
- Skill 从对话中抽取：`conversation-add` 队列 + skill-extractor + 审阅 prompt（`src/core/skill/conversation-add/`、`skill-extractor.ts`）

### 2.3 LLM-Wiki（MemoryKnowledge/engines/wiki）
- 元数据模型：`knowledge_wiki` 表（serviceId+teamId 唯一名，status: draft→…，version 单调递增，软删 deletedAt+部分唯一索引）+ append-only `knowledge_wiki_audit` 审计表（action/version/user/agent/detail，`MemoryKnowledge/src/db/schema.ts:55-106`）
- 摄取 v2：源扫描→chunker→LLM 生成 wiki 页（frontmatter: title/type/sources/description + [[wikilink]]，`engines/wiki/manager.ts:52-95`）；每 wiki 私有 `index.db`（SQLite：wiki_fts + page_meta + graph_edge 三表，写独立事务、读 LRU 连接池，根治内存常驻 OOM，`manager.ts:5-9`）
- **合并治理（核心）**：同 slug 页命中旧页时——locked:true（用户手工编辑）**绝不覆盖**（硬约束 §3.7-1）；规则判重（候选正文是旧页子串→不调 LLM 仅并集 sources）；小页（≤4000 字）整页重写、大页追加增量片段省 output token（`engines/wiki/ingest-v2/merge.ts:1-34,55-60,70-88`）
- 检索：BM25 全文 + wikilink 图多跳 BFS（深度 0~5，0=纯 BM25，`manager.ts:99-101`）
- LLM 路由治理：`llm_binding` 表按 service 实例选 proxy（内部 knowledge 专用 key）或 byo（用户自备 OpenAI 兼容端点，`db/schema.ts:126-139`）

### 2.4 Code-Graph（MemoryKnowledge/engines/code）
- 数据模型：`knowledge_code_graph` 表（serviceId+teamId+repoUrl+branch 唯一，commitHash/version/lastSyncAt 跟踪同步）+ append-only `knowledge_code_graph_audit`（`db/schema.ts:18-51,108-124`）
- 实现是**外包封装**：bridge 动态加载 npm 包 `@colbymchenry/codegraph` 及平台二进制，openIndex/indexAll/executeTool 透传（`engines/code/bridge.ts:25-39,89-130`）——代码图构建不在本仓库内
- auto-sync 调度器 + build 队列做仓库重建（`store/auto-sync-scheduler.ts`、`store/build-queue.ts`、`routes/auto-sync.ts`）

### 2.5 检索与注入
- auto-recall 钩子三策略：keyword（FTS5 BM25）/ embedding（cosine）/ hybrid（RRF 融合，RRF_K=60，`MemoryCore/src/core/hooks/auto-recall.ts:1-11`；`src/core/store/search-utils.ts:15-41`），超时 5s 且结构化失败信号（error code 20001 区分"无结果"与"超时"，`auto-recall.ts:107-120`）
- 注入分两条路：L1 相关记忆 **prepend 到 user prompt**（每轮动态）；persona/场景导航/工具指南 **append 到 system prompt**（可缓存，`auto-recall.ts:63-67`）；注入带预算（maxCharsPerMemory / maxTotalRecallChars 截断，`:835-861`），并注入"记忆工具指南"教主 Agent 主动调 `tdai_memory_search`/`tdai_conversation_search`（**每轮合计≤3 次**防搜索成瘾，`:41-54`）
- MemoryProxy 路线：L2/L3/Skill/Knowledge 注入 system prompt，L0/L1 只暴露为只读工具**避免打爆上游 KV-cache**（`MemoryProxy/README.md:23-25`）；Skill/Memory Bridge 反代时注入 serviceToken，**凭证不进 LLM 可见 prompt**（`README.md:31`）
- 多租户隔离：MemoryRecord 带 teamId/userId/agentId 三维隔离字段，SQLite 缺省回填 `__legacy__`（`l1-writer.ts:84-97`）；dedup 候选召回强制带 IsolationFilter 不跨租户（`l1-dedup.ts:70-71`）

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）

① L1 三级降级候选召回决策树（`MemoryCore/src/core/record/l1-dedup.ts:93-119`）：
```ts
if (!hasVectorData && !hasFts) { return storeAll(); }
let matches: CandidateMatch[];
if (hasVectorData && embeddingService) {
  matches = await findCandidatesByVector(memories, vectorStore!, embeddingService, topK, ...);
} else if (hasFts) {
  matches = await findCandidatesByFts(memories, vectorStore!, logger, filter);
} else {
  return storeAll();
}
```

② 记忆记录 schema（`MemoryCore/src/core/record/l1-writer.ts:55-79`）：
```ts
export interface MemoryRecord {
  id: string;
  content: string;
  type: MemoryType;            // persona/episodic/instruction/work_*
  priority: number;            // 0-100，-1 = 强全局指令
  scene_name: string;
  source_message_ids: string[];
  metadata: EpisodicMetadata | Record<string, never>;
  timestamps: string[];        // merge 历史轨迹
  version?: number;            // 单调递增
  sessionKey: string; sessionId: string; taskId?: string;
  teamId?: string; userId?: string; agentId?: string;  // 三维租户隔离
}
```

③ Wiki 合并硬约束（`MemoryKnowledge/src/engines/wiki/ingest-v2/merge.ts:76-90`）：
```ts
if (existingContent == null) return { action: "write", content: candidateContent };
const oldParsed = parseFrontmatter(existingContent);
if (oldParsed.frontmatter.locked === true) {
  return { action: "skip", reason: "目标页 locked，跳过合并" };
}
```

④ Skill 版本化主表（`MemoryCore/src/core/skill/skill-store-ddl.ts:22-49`）：
```sql
CREATE TABLE IF NOT EXISTS skills (
  row_id TEXT PRIMARY KEY, skill_id TEXT NOT NULL, version INTEGER NOT NULL,
  is_head INTEGER NOT NULL DEFAULT 1,
  user_id TEXT NOT NULL, owner_agent_id TEXT NOT NULL, team_id TEXT NOT NULL,
  name TEXT NOT NULL, content TEXT NOT NULL, content_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  UNIQUE(skill_id, version)
);
CREATE UNIQUE INDEX uniq_skills_team_agent_name_head
  ON skills(team_id, owner_agent_id, name) WHERE is_head=1 AND status='active';
```

⑤ 注入工具指南限流（`MemoryCore/src/core/hooks/auto-recall.ts:50-53`）：
```
每轮对话中，tdai_memory_search 和 tdai_conversation_search 合计最多调用 3 次。
若 3 次搜索后仍无结果，说明该信息不在记忆中，请直接根据已有信息回复用户，不要继续搜索。
```

## 4. 基准/评测声明（反虚荣视角）
- **无公开基准数字**。仓库做的是"生产评测指标管道"而非排行榜：Kafka metricProducer 上报 l1_extraction_rate、dedup 决策分布（store/update/merge/skip 计数）、L1 延迟（`l1-extractor.ts:300-316,422-432`），langfuse trace 钩子埋点（`l1-extractor.ts:481-483`）。无 LongMemEval/LoCoMo 类对外口径 → 声明级别：[无基准声明]，评测为内部可观测性
- 亮点是**可信度审计基础设施**：MemoryGenerationLog 记录每次记忆生成用哪个 prompt 版本/模型/延迟（`l1-extractor.ts:344-365`），wiki/code-graph 各有 append-only audit 表——记忆可回溯"谁在何时用什么 prompt 生成"

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）
- **单次 LLM 调用做"场景切分+记忆抽取"**，并以 previousSceneName 传递场景连续性（`l1-extractor.ts:5,115`）——比逐条抽取省调用且记忆天然带场景聚类标签
- **四动作 LLM 判重**（store/update/merge/skip + merged_* 字段）显式建模"新事实与旧记忆的关系"，取代 mem0 式 ADD/UPDATE/DELETE 三分类；merge 保留 timestamps 轨迹可看合并史
- **locked 页硬约束**：用户手工编辑的知识页机器永不覆盖——人机共同治理记忆的最小安全阀（`merge.ts:5,81-85`）
- **分层注入缓存感知**：稳定内容进 system prompt（可命中 KV-cache），易变内容 prepend user prompt，L0/L1 下沉为按需工具——直接优化推理成本（`MemoryProxy/README.md:23-25`；`auto-recall.ts:63-67`）
- **检索工具调用限额写进注入 prompt**（≤3 次/轮）是对"Agent 搜索成瘾"失效模式的直接工程对策（`auto-recall.ts:50-53`）
- **技能即记忆资产**：Skill 带版本快照+owner+团队命名空间+FTS/vec 双索引，把"程序性记忆"做成可治理配置项而非自由文本

## 6. 局限与风险（失败模式、安全隐患、工程债）
- L1 抽取强依赖 LLM JSON 输出：靠 sanitize+repair 抢救（弱模型会把 `"priority": sheet` 这类裸标识符写进数值字段，`l1-extractor.ts:539-551,592-599`），弱模型下抽取质量不可控；判重失败静默降级全量 store（`l1-dedup.ts:335-337`）可能造成记忆膨胀
- Code-Graph 核心是第三方闭源-ish npm 包（@colbymchenry/codegraph 平台二进制），桥接层任何 API 漂移都直接断（`bridge.ts:34-38`）；wiki/code-graph 大仓重建经 build-queue 串行，repo 多时同步延迟未知
- 三维租户隔离是"分支中途"状态：字段 optional、旧行 `__legacy__` 回填（`l1-writer.ts:86-94`），说明隔离是后补的，历史数据边界模糊
- 每轮对话两次 LLM 调用（抽取+判重各 180s 超时，`l1-extractor.ts:491`）在长对话高频回写下成本显著；skill FTS content 截 4000 字（`skill-store-ddl.ts:104`）长技能检索不完整
- 腾讯云绑定：tcvdb-client 为腾讯云 VectorDB 私有 HTTP API（`src/core/store/tcvdb-client.ts:203-236`），虽默认本地 SQLite 可跑，但云上能力迁移成本高

## 7. 一句话对比 mem0
mem0 是"个人 Agent 的记忆层"，TencentDB-Agent-Memory 是"团队 Agent 的记忆资产治理平台"：用 L0-L3 分层+四动作判重保持对话记忆新鲜度，再把 mem0 没有的 Skill（版本化）、LLM-Wiki（locked 硬约束+审计）、Code-Graph（元数据注册）纳入同一套租户隔离、审计溯源和代理注入体系——代价是组件多、强 LLM 依赖、无公开基准。
