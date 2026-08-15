# A-08 `MemoriLabs/Memori`（15.9K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\MemoriLabs__Memori
> Python（SDK）+ Rust core（加速引擎）+ TS SDK ｜ 一句话定位：包裹 LLM invoke 的"记忆中间件"——拦截每轮对话，先注入召回事实、后持久化对话并异步抽取结构化事实/三元组，云/自托管双形态。

## 1. 架构总览（目录地图，标出核心目录的职责）

```
memori/                       # Python SDK（核心）
├── llm/invoke/               # invoke 包装器：进入前注入记忆，出来后写库+触发抽取
│   └── pipelines/            # recall_injection（前）/post_invoke（后）/conversation_injection
├── memory/
│   ├── _manager.py/_writer.py    # 对话消息持久化（cloud POST 或本地驱动事务）
│   ├── recall.py                 # 事实检索入口（cloud/rust/python 三路）
│   ├── _struct.py                # Memories 结构：Conversation/Entity/Process + SemanticTriple
│   └── augmentation/             # 异步"增强"管线：对话→云API抽取→facts/triples/summary 落库
├── storage/                  # 8 种 DB 驱动（sqlite/mysql/postgres/mongodb/oracle/oceanbase/tidb/cockroachdb）+ 迁移
├── search/                   # FAISS 余弦 + 内存 BM25 + 加权融合
├── embeddings/               # TEI 文本嵌入（分块/格式化）
├── agent.py                  # Memori Cloud agent 端点客户端
├── provisioning/             # 零配置 DB 供给（tidb_zero）
└── _network.py               # api/collector 双子域 HTTP 客户端
core/                         # Rust 编排核心（同名管线的原生实现，含 node/python 绑定）
integrations/                 # Claude Code / OpenClaw / Hermes 插件
memori-ts/                    # TypeScript SDK
```

## 2. 记忆机制深读（本笔记核心，每个论断必须钉 `相对路径:行号`）

### 2.1 写入/抽取管线（谁触发、prompt 是什么、结构化 schema）

每轮 invoke 的完整数据流：

```
用户 query ──recall_injection──> embed(query) → FAISS 余弦(≤1000 嵌入) → BM25 加权融合
                                   → 阈值过滤(≥0.1) → <memori_context> 注入 system
LLM invoke（带注入上下文）
response ──post_invoke──> Manager.execute（持久化消息：cloud POST 或本地驱动事务）
                        └─> handle_augmentation（异步、best-effort）
                              cloud: collector 子域 cloud/augmentation
                              local: rust core 线程池 / python 队列 → 仍调云 sdk/augmentation
                              ← facts/triples/summary → 本地 embed → UPSERT 落库
```

- 触发点：包装后的 LLM invoke 返回后 `handle_post_response` 先 `MemoryManager.execute` 持久化对话，再 `handle_augmentation` 异步抽取（memori/llm/pipelines/post_invoke.py:94-144）。
- 双身份模型：`entity_id`（用户/实体）与 `process_id`（执行过程/agent 进程）两级归属（memori/llm/pipelines/post_invoke.py:39-42）；无 entity 且无 process 则直接不抽取（memori/memory/augmentation/_handler.py:165-166）。
- **抽取 LLM 不在本地**：`AdvancedAugmentation.process` 把消息打包发到 Memori 云端 `sdk/augmentation` 端点（memori/memory/augmentation/augmentations/memori/_augmentation.py:133,159；端点定义 memori/_network.py:61-62）；Rust core 同样调 `client.augmentation_raw_async`（core/src/augmentation/pipeline.rs:32-46，日志原文 `augmentation calling Memori API: sdk/augmentation`）。仓库内**没有抽取 prompt 的本地实现**——闭源服务侧。
- 抽取结果 schema：`Memories{conversation.summary, entity.facts/fact_embeddings/semantic_triples, process.attributes}`（memori/memory/_struct.py:102-126）；三元组要求 subject/predicate/object 各带 name+type，缺失即丢弃（memori/memory/_struct.py:75-99）。
- 抽取窗口裁剪：已有 summary 时只送最后一对 user/assistant 消息（`_select_messages_for_summary`，memori/memory/augmentation/augmentations/memori/_augmentation.py:53-84）。
- facts 回本地后自行 embed（`_embed_facts`，失败则无嵌入裸写，_augmentation.py:201-215），随后调度三类写：entity_fact.create / knowledge_graph.create / process_attribute.create / conversation.update（_augmentation.py:246-285）。

### 2.2 存储后端与数据模型（表/集合/文件布局，原文摘录 schema）
- 本地模式 8 库驱动注册（memori/storage/drivers/：sqlite/mysql/postgresql/mongodb/oracle/oceanbase/tidb + cockroachdb 集群管理），每库独立迁移脚本。
- 核心表（SQLite 迁移原文，memori/storage/migrations/_sqlite.py:24-145）：
  ```sql
  memori_entity(id, uuid, external_id UNIQUE, ...)            -- 外部实体ID隔离边界
  memori_process(id, uuid, external_id UNIQUE, ...)
  memori_session(id, uuid, entity_id FK, process_id FK, ...)
  memori_conversation(id, uuid, session_id FK UNIQUE, summary)
  memori_conversation_message(id, conversation_id FK, role, type, content)
  memori_entity_fact(id, entity_id FK, content, content_embedding BLOB,
                     num_times, date_last_time, uniq,
                     UNIQUE(entity_id, uniq))                   -- 事实去重键=entity+内容哈希
  ```
- 知识图谱表：`memori_subject(name,type,uniq)` / `memori_predicate` / `memori_object` + `memori_knowledge_graph(entity_id, subject_id, predicate_id, object_id, num_times, … UNIQUE(entity_id,subject,predicate,object))`（_sqlite.py:186-276）。
- 迁移 v2 增加溯源表 `memori_entity_fact_mention(entity_id, fact_id, conversation_id)` 记录事实在哪次对话出现（_sqlite.py:278-311）。
- **隔离机制**：所有事实/图谱行都带 entity_id 外键且 `ON DELETE CASCADE`（_sqlite.py:140-144），检索 SQL 一律 `WHERE entity_id = ?`（驱动 get_embeddings，memori/storage/drivers/sqlite/_driver.py:326-343）——单租户=一库，租户内实体按 external_id 唯一约束隔离（_sqlite.py:31）。

### 2.3 检索策略（向量/关键词/混合/重排/图，参数与阈值）
- 入口 `Recall.search_facts` / rust `retrieve_facts(query, entity_id, limit, dense_limit)`（memori/llm/pipelines/recall_injection.py:141-163）。
- 默认参数：`recall_facts_limit=5`、`recall_relevance_threshold=0.1`、`recall_embeddings_limit=1000`（memori/_config.py:86-88）。
- 向量层：FAISS `IndexFlatIP` + L2 归一化=余弦，且**每次查询现建索引**（memori/search/_faiss.py:65-78）——暴力扫描，无 ANN 结构。
- 词法层：候选池内内存 BM25（k1=1.2, b=0.75，max 归一化到 [0,1]，memori/search/_lexical.py:100-124）。
- 融合：`rank_score = w_cos*cos + w_lex*bm25`；默认 w_lex=0.15，≤2 词短查询升到 0.30，夹在 [0.05,0.40]（memori/search/_lexical.py:127-148；打分实现 memori/search/_core.py:127-145）。
- 候选池放大：有查询文本时候选数 `max(limit, min(total, max(limit*10, 50)))`（memori/search/_core.py:85-90）；嵌入取出顺序 `date_last_time DESC, num_times DESC`（_driver.py:334-336）——**频率+新近度先验 baked into 候选池**。
- 无图检索：知识图谱只写不读（检索路径无 triple 查询）。

### 2.4 遗忘·整合·演化（有无 decay/merge/re-rank/自更新）
- 重复事实合并靠 UPSERT：`ON CONFLICT(entity_id, uniq) DO UPDATE SET num_times = num_times + 1, date_last_time = datetime('now')`（memori/storage/drivers/sqlite/_driver.py:275-277）——同一事实再说一次=频次+1、时间刷新，内容不更新。
- 无 decay/遗忘：num_times 与 date_last_time 只增不减，仅用于排序先验（_sqlite.py:150-151 频率索引）。
- 会话演化：conversation.summary 每轮由云端抽取覆写（_augmentation.py:274-285）。
- 删除能力：`delete_entity_memories` 实体级整删（memori/memory/recall.py:193-200），无单条冲突消解/更正语义（对比 mem0 的 ADD/UPDATE/DELETE 决策，Memori 无事实级更新路径）。

### 2.5 注入上下文的方式（系统提示拼装、token 预算）
- `inject_recalled_facts` 在 invoke 前运行：阈值过滤（`_score_for_recall_threshold >= 0.1`，recall_injection.py:170-181）后拼装：
  ```python
  "<memori_context>\nOnly use the relevant context if it is relevant to the user's query. "
  + "Relevant context about the user:\n- {fact}. Stated at {ts}" + "## Summaries"
  ```
  （recall_injection.py:191-199；事实行格式 :26-50）。
- 按提供商适配注入位置：Anthropic/Bedrock→`kwargs["system"]`，Google→system_instruction，OpenAI→messages[0] 系统消息（recall_injection.py:201-224）。**无 token 预算控制**——上限=recall_facts_limit(5) 条事实+摘要。

### 2.6 部署形态与 Rust core（补充）
- 云模式（`cloud=True`）：对话/抽取全走 `api.memorilabs.ai`（写 `cloud/conversation/messages` 期望 201，memori/memory/_manager.py:44-74；抽取走 collector 子域 `cloud/augmentation`，memori/memory/augmentation/_handler.py:74-99），成功后仍镜像消息到本地库（`_persist_cloud_messages_locally`，_manager.py:85-141）——云主存+本地副本的双写。
- 自托管（`cloud=False`）：存储经 `StorageBuilder` 构造（memori/storage/_builder.py），8 库驱动同构迁移；对话与消息写本地库，但抽取仍调云（见 2.1）。API 基址可整体替换（`MEMORI_API_URL_BASE`/`config.api_url_base`，_network.py:44-57）——这是"单租户/VPC"的官方接缝：换基址+自带 key，但对方服务代码不在仓库。
- Rust core（默认启用，`MEMORI_DISABLE_RUST_CORE` 可关，_config.py:97-102）：core/src 以原生代码复刻同等管线——storage 层三驱动（sqlite/postgresql/mysql，core/src/storage/drivers/）+ 方言抽象（dialect.rs）+ 迁移；augmentation 仍调同一云 API（core/src/augmentation/pipeline.rs:36）；有 python/node 双绑定（core/bindings/）。契约测试锁行为一致性（core/tests/orchestrator_contract.rs、storage_sqlite_integration.rs）。
- Rust runtime：worker + state 机（core/src/runtime/worker.rs、state.rs），后台任务（augmentation 队列）与检索（core/src/retrieval/pipeline.rs，AA 契约测试 core/tests/retrieval_aa_contract.rs 锁定）在原生线程池运行。
- 供给层：`provisioning/` 支持零配置拉起托管库（tidb_zero provider，memori/provisioning/providers/tidb_zero.py），带注册表与缓存（_registry.py/_cache.py）——"连 DB 都没有"的极简上手路径。
- CockroachDB 专项：集群管理器/文件布局/展示模块（memori/storage/cockroachdb/_cluster_manager.py 等），面向全球分布部署；examples/ 覆盖 postgres/neon/tidb/oceanbase/cockroachdb/mongodb/digitalocean/nebius/agno 十种部署样例。
- 嵌入层：TEI（Text Embeddings Inference）客户端与分块器（memori/embeddings/_tei.py、_chunking.py），SDK 不绑死 OpenAI。
- 配额：匿名 key 有服务端配额，429 触发 `QuotaExceededError`（_network.py:105-114）；memori-ts 与 openclaw 插件均有 signup/quota 命令（integrations/openclaw/src/tools/memori-quota.ts、memori-signup.ts）。

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）

**摘录 1：事实 UPSERT=频率+新近度整合（memori/storage/drivers/sqlite/_driver.py:275-277）**
```sql
ON CONFLICT(entity_id, uniq) DO UPDATE SET
    num_times = num_times + 1,
    date_last_time = datetime('now')
```

**摘录 2：稠密+词法自适应加权（memori/search/_lexical.py:140-148）**
```python
if len(q_tokens) <= 2:
    w_lex = float(os.environ.get("MEMORI_RECALL_LEX_WEIGHT_SHORT", "0.30") or "0.30")
w_lex = max(0.05, min(0.40, w_lex))
return (1.0 - w_lex, w_lex)
```

**摘录 3：注入上下文模板（memori/llm/pipelines/recall_injection.py:194-199）**
```python
recall_context = (
    "\n\n<memori_context>\n"
    "Only use the relevant context if it is relevant to the user's query. "
    + context_body
    + "\n</memori_context>"
)
```

**摘录 4：抽取外包给云 API（memori/memory/augmentation/augmentations/memori/_augmentation.py:157-159）**
```python
logger.debug("AA submitting payload to API")
try:
    api_response = await api.augmentation_async(payload)
```

**摘录 5：硬编码匿名 API key（memori/_network.py:46-57）**
```python
if test_mode:
    self.__x_api_key = "c18b1022-7fe2-42af-ab01-b1f9139184f0"
    self.__base = f"https://staging-{subdomain.value}.memorilabs.ai"
else:
    self.__x_api_key = "96a7ea3e-11c2-428c-b9ae-5a168363dc80"
    self.__base = f"https://{subdomain.value}.memorilabs.ai"
```

## 4. 基准/评测声明（反虚荣视角）
- README.md:134 引用 benchmark overview/results 链接（docs/memori-cloud/benchmark/），但仓库内 docs/ 只有 claude-code/hermes/mcp/openclaw 的 skills 文档，**无基准数据与脚本**。[自封][不可复现]。
- tests/memory/test_recall_eval_harness.py 存在召回评测 harness（自用），无公开数字。
- 每轮对话明文发往 memorilabs.ai（post_invoke payload 含 query/response 全文，memori/llm/pipelines/post_invoke.py:38-62；Collector.fire_and_forget 打 `/rec` 端点，memori/memory/_collector.py:100-107）——"本地部署"隐私声明需打折。
- attribution 做 hash 混淆：Rust core 上报前对 entity_id/process_id 过 Sha256（core/src/augmentation/pipeline.rs:11,86-90 的 `hash_id`），Python 侧同构（memori/memory/augmentation/augmentations/memori/models.py 的 hash_id）——云端看不到原始用户 ID，但仍见对话内容。
- openclaw 插件带 recall-summary/compaction/feedback 工具面（integrations/openclaw/src/tools/，8 个工具），提供"摘要/压缩/反馈"入口，对应云端 `/v1/agent/*` 端点（agent.py:23-92）——compaction 是云端会话压缩能力，本地无对应实现。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）
1. **entity（用户）与 process（执行过程）双轴归属**（post_invoke.py:39-42；两张对称的 external_id 唯一表）：把"谁的记忆"与"哪次执行的轨迹"分离，天然支持"跨会话个人记忆 + 按执行过程隔离的过程记忆"，比 mem0 单一 user_id 维度更细。
2. **频率+新近度作为一等排序信号**：候选池 SQL `ORDER BY date_last_time DESC, num_times DESC`（_driver.py:334-336）+ 表级频率索引（_sqlite.py:150-151）——不改打分函数就让"常被提及的事实"更易召回。
3. **mention 溯源表**：fact↔conversation 多对多（_sqlite.py:278-311）使"这条记忆来自哪几次对话"可审计——记忆可解释性的廉价实现。
4. **查询长度自适应的混合权重**（≤2 词升词法权重，_lexical.py:140-148）：比固定 0.5/0.5 融合更符合短查询精确词信号强的直觉。
5. **写路径异步化三态**：cloud POST / rust core 线程池 / python 队列（_handler.py:157-200），对话持久化（必须成功）与增强抽取（best-effort）分级可靠性（agent.py:108-112 注释明示）。

## 6. 局限与风险（失败模式、安全隐患、工程债）
- **"本地部署"名不副实**：事实/三元组抽取必须调 Memori 云 `sdk/augmentation`（Python 与 Rust 两条路径皆然，_augmentation.py:159；core/src/augmentation/pipeline.rs:36-40）；断网本地模式=只存原文无抽取。企业 VPC 部署需自建该服务，仓库不含其代码。
- 硬编码生产/预发匿名 API key 进源码（_network.py:49,53,57）——密钥管理债+匿名配额滥用面。
- FAISS IndexFlatIP 每查询重建（_faiss.py:65-78）：召回候选上限 1000 嵌入（_config.py:86），事实超千条后旧事实静默退出候选池（隐性遗忘）。
- 无冲突消解：事实只增频次不改内容（_driver.py:275-277），"用户搬家了"会与新事实并存，靠 date_last_time 排序部分缓解。
- 会话窗口裁剪只看最后一对消息（_augmentation.py:53-84）：多轮上下文中的事实（如"刚才说的那个项目"）可能漏抽。
- 对话明文外发（_collector.py:100-107）+ telemetry（meta 含模型/SDK 版本，_augmentation.py:101-120）。
- Rust core 与 Python 双实现并行维护（core/src 与 memori/ 同构），行为一致性靠契约测试锁定（core/tests/），漂移风险长期存在；TS SDK 第三份实现（memori-ts/src/engines/）。
- 写路径依赖缓存 ID 链（`_ensure_cached_id` 链式 ensure entity→process→session→conversation，_writer.py:66-98）：config.cache 为进程内状态，多进程/多线程共享同一 Config 时缓存 ID 可能错配会话。
- `conversation.create` 幂等窗口由 `session_timeout_minutes=30` 控制（_config.py:93）：30 分钟内的新对话复用同一 conversation_id，跨天长会话被切成多段，事实 mention 归属随之分段。
- 知识图谱表写入走 subject/predicate/object 三张维表的 uniq 查找-插入（_driver.py:415-463），无批量 upsert，大规模三元组抽取时写放大。

## 7. 一句话对比 mem0
mem0 把"抽取 LLM"放在本地可换模型、带 ADD/UPDATE/DELETE 决策闭环；Memori 把抽取做成闭源云服务、本地只做 UPSERT 累积，但用 entity/process 双轴 + mention 溯源 + 频率先验把"企业可审计的持久状态"做得更像数据库、更不像 prompt 工程。
