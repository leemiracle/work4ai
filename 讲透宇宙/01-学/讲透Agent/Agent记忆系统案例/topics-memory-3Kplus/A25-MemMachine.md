# A-25 `MemMachine/MemMachine`（3.3K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\MemMachine__MemMachine
> Python（monorepo：server/client/common/skills/ts-client）+ 大量 TS 集成 / Apache-2.0 ｜ 平台级「通用记忆层」：REST + MCP + 8 框架集成三路互操作，存储侧短/长双记忆 + 向量图双库，检索侧重排器族（RRF 混合）+ 多跳检索 agent，工程成熟度为四仓之最。

## 1. 架构总览（目录地图，标出核心目录的职责）
- `packages/server/src/memmachine_server/` — 核心：
  - `episodic_memory/` — 会话记忆实例编排：
    - `episodic_memory.py`（短/长双记忆门面）、`episodic_memory_manager.py` + `instance_lru_cache.py`（实例引用计数 + LRU）、`service_locator.py`；
    - `short_term_memory/`（滚动摘要）、`long_term_memory/`（declarative/event 双后端门面）；
    - `declarative_memory/`（向量图存储，728 行）、`event_memory/`（segmenter + deriver 分段管道 + segment_store）；
  - `common/` — 可插拔资源族：
    - vector_store：qdrant/milvus/sqlite/sqlite-vec + hnswlib/usearch 搜索引擎（`common/vector_store/`）；
    - vector_graph_store：**neo4j/nebula** 双实现（`common/vector_graph_store/`）；
    - reranker：cohere/bedrock/bm25/cross-encoder/embedder/**rrf_hybrid**/identity 七种（`common/reranker/`）；
    - embedder（openai/bedrock/sentence-transformer）、language_model（litellm/openai chat+responses/bedrock）；
    - filter（属性过滤 DSL→SQL，`common/filter/`）、resource_manager（资源生命周期）、metrics_factory（Prometheus）；
  - `retrieval_agent/` — agentic 检索编排（ChainOfQuery / RARAG / split / tool-select + decomposer）；
  - `server/` — FastAPI REST（api_v2）+ **MCP http/stdio 双协议** + 领域提示（crm/financial/health/profile/coding_style）；
  - `semantic_memory/`、`episode_store/`（SQLAlchemy 会话日志 + count-caching 装饰）、`session_manager/`。
- `packages/client/`、`packages/ts-client/` — Python/TS SDK。
- `integrations/` — langchain/llamaindex/crewai/dify/fastgpt/n8n/openclaw/strands-memmachine/aws-strands 八件套。
- `packages/skills/memmachine-memory/` — 让 Claude 类 agent 经 mem-cli 用记忆的技能。
- `evaluation/` — LoCoMo/HotpotQA/WikiMultiHop 三套基准 runner；`deployments/helm/` — K8s 部署。
- deepwiki 章节（Episodic Memory / Retrieval Agents / MCP 等）与结构吻合 [deepwiki-已验证]。

## 2. 记忆机制深读（本笔记核心，每个论断钉 `相对路径:行号`）
### 2.1 写入/抽取管线（谁触发、prompt 是什么、结构化 schema）
- 写入单元 `Episode`（`packages/server/src/memmachine_server/common/episode_store/episode_model.py:44-61`）：
  - 字段：`{uid, content, session_key, created_at, producer_id, producer_role, produced_for_id, sequence_num, episode_type(MESSAGE/…), content_type, filterable_metadata, metadata}`；
  - **写入不做 LLM 事实抽取**——原文即记忆；`add_memory_episodes` 只把 metadata 中基础类型值提升为可过滤属性（`episodic_memory/episodic_memory.py:222-228`），然后**并发写短+长两个记忆库**（`episodic_memory.py:230-238`）。
- 抽取发生在「派生层」：
  - declarative 后端为每个 episode 派生 Derivative（句子级，`message_sentence_chunking` 可选，`declarative_memory/declarative_memory.py:68-71,136-150`）；
  - Derivative 建向量索引、经 `DERIVED_FROM_{session}` 边指回原 episode（`declarative_memory.py:94-97,180-192`）。
- event 后端写入管道（`long_term_memory.py:120-160`）：
  - Episode→Event：`uuid5(NAMESPACE, uid)` 确定性映射（`long_term_memory.py:60-62,632-690`）；
  - Segmenter（passthrough/Text 分段）→ Deriver（全文/句子）→ 向量库 collection + SegmentStore partition 按 session 分区。
- 短期记忆的「抽取」= 滚动摘要：
  - 容量按字符长度判满（`short_term_memory.py:174-185`）；
  - 满则异步驱逐最旧 episode 交 consolidator 摘要，先清已摘要旧消息再触发新一轮（`short_term_memory.py:222-240`）；
  - 摘要 prompt 三要求「尽量短/保留细节/实体与关系全保留」（`common/configuration/default_episode_summary_system_prompt.txt:1-5`）；
  - 摘要长度上限取整到百词（`short_term_memory.py:146-154`）。
- 安全细节：event 后端**拒绝 `_` 前缀的用户 metadata 键**，防客户端伪造 `_producer_id/_session_key` 造成跨生产者/跨会话冒名（`long_term_memory.py:644-677`）。

### 2.2 存储后端与数据模型（表/集合/文件布局，原文摘录 schema）
- **双库抽象**：
  - `VectorStore`（qdrant/milvus/sqlite/sqlite-vec，`common/vector_store/`）；
  - `VectorGraphStore`（neo4j/nebula）接口 9 方法：add_nodes/add_edges/search_similar/related/directional/matching/get_nodes/delete_nodes/delete_all_data（`common/vector_graph_store/vector_graph_store.py:19-288`）。
- declarative 后端布局（`declarative_memory.py:94-178`）：
  - 每 session 两个 collection：`Episode_{session_id}`（原文节点，properties 含 uid/timestamp/source/content_type/content/user_metadata JSON + mangled 过滤键）；
  - `Derivative_{session_id}`（带 embeddings `{model_id_dim: (vec, metric)}`）；
  - 关系 `DERIVED_FROM_{session}`：derivative→episode 边。
- event 后端布局：
  - 向量库 collection + SegmentStore partition 按 `partition_key`（session）分区，查询时用 EpisodeStorage 水合原文（`long_term_memory.py:122-150,357`）；
  - 系统属性以 `_` 前缀存 event.properties：`_episode_uid/_session_key/_producer_id/_producer_role/_produced_for_id/_sequence_num/_episode_type/_content_type/_created_at`（`long_term_memory.py:68-88`）；
  - 索引与存储非事务一致，漂移时告警并跳过缺失项（`long_term_memory.py:360-372`）。
- 会话日志走 `episode_sqlalchemy_store`（含 count-caching 装饰，`common/episode_store/count_caching_episode_storage.py`）。
- 实例生命周期：`EpisodicMemoryManager` 引用计数 + LRU 缓存（`episodic_memory/instance_lru_cache.py`）；配置体系 `EpisodicMemoryConf`（含 ShortTermMemoryConf/DeclarativeLongTermMemoryConf/EventLongTermMemoryConf 等分层 partial，`common/configuration/episodic_config.py:74-388`）。

### 2.3 检索策略（向量/关键词/混合/重排/图，参数与阈值）
- declarative 检索五步（`declarative_memory.py:344-441`）：
  - ① 查询嵌入（`search_embed`，`declarative_memory.py:348-352`）；
  - ② 在 **Derivative 层**向量检索，`limit=min(5×max_episodes, 200)` 过采样（`declarative_memory.py:355-367`）；
  - ③ `search_related_nodes` 沿 DERIVED_FROM 边回溯源 episode，dict 保序去重（`declarative_memory.py:369-390`）；
  - ④ **时间邻域扩展**：每篇命中 episode 向前后取邻居（`(timestamp, uid)` 双键方向游标），`expand_context` 按 1/3 偏分 backward（`declarative_memory.py:398-400,443-497`）；
  - ⑤ **上下文级重排**：整段 episode 上下文拼字符串交 Reranker 打分、按分排序统一（`declarative_memory.py:414-441,499-514`）。
- 重排器族与 RRF：
  - cohere/bedrock/**BM25**/cross-encoder/embedder/identity 六种单重排器（`common/reranker/`）；
  - **RRFHybridReranker**：多重排器并发、按名次 `Σ 1/(k+rank)` 融合，k=60 默认（`common/reranker/rrf_hybrid_reranker.py:11-46`）。
- 分数阈值方向感知：
  - cosine/点积/重排分是越高越好，欧氏距离是越低越好（`long_term_memory.py:186-192`）；
  - `score_threshold` 自动按度量方向裁剪，修掉了 `-inf` 哨兵在欧氏下「全删」的 bug（`long_term_memory.py:255-263,432-445`）。
- event 后端去重过采样：段级结果按 `_episode_uid` 去重，过采样系数 4 保证段多的 episode 不挤占 limit（`long_term_memory.py:102-106,319-352`）。
- **agentic 检索层**（retrieval_agent）：
  - ChainOfQueryAgent：充分性+改写合一 prompt 迭代检索——LLM 只准用已检文档判断 `is_sufficient` 并给 evidence_indices/new_query/confidence，禁止外部知识与编造实体（`retrieval_agent/agents/coq_agent.py:15-80`，方法引用 Agent Lightning RL 论文 arXiv:2508.03680）；
  - RaragQueryAgent：多跳优化版，非 LLM 跳数分解器可插、对外仍自称 "ChainOfQueryAgent" 以便原位替换（`retrieval_agent/agents/rarag_query_agent.py:1-7,27-44,169-207`）；
  - ToolSelectAgent 选工具组合、split_query_agent/decomposer 负责查询分解。
- 双记忆合并：短/长期并发查询（`asyncio.gather`，`episodic_memory.py:411-425`）后按 uid 去重、**短期优先**（`episodic_memory.py:448-456`）；查询模式 BOTH/LONG_TERM_ONLY/SHORT_TERM_ONLY（`episodic_memory.py:307-312`）。

### 2.4 遗忘·整合·演化（有无 decay/merge/re-rank/自更新）
- 遗忘原语齐全：
  - `delete_episodes(uids)`：短期逐条删 + 长期批量删（`episodic_memory.py:261-277`）；event 后端 uuid5 映射使删除幂等（`long_term_memory.py:380-389`）；
  - `delete_session_episodes()`：短清空 + 长期 drop partition/collection（`episodic_memory.py:279-288`）；
  - drop 后置空句柄令后续调用「响亮失败」而非静默脏操作（`long_term_memory.py:391-425,447-456`）。
- 短期记忆 rolling summary 即整合（`short_term_memory.py:222-240`）。
- 无 decay/置信度/merge——长期记忆不做内容演化，靠查询时重排与邻域扩展补语境（与 mem0 的写入期 UPDATE/DELETE 事件相反的取舍）。

### 2.5 注入上下文的方式（系统提示拼装、token 预算）
- `formalize_query_with_context`（`episodic_memory.py:478-548`）：
  - 检索结果 + 原查询拼成 `<Summary>…</Summary>\n<Episodes>…</Episodes>\n<Query>…</Query>` 三段 XML 风格包装；
  - episode 序列化为 `[Friday, June 06, 2025 at 02:30 PM] producer: content` 人类可读时间线（`episode_model.py:68-97`）；
  - episodes 按 created_at 时间排序（`episodic_memory.py:515-519`）。
- 无显式 token 预算打包：靠 `limit`（默认 20）+ `expand_context` 数量控制（`episodic_memory.py:371-389`）。
- 互操作三件套：
  - REST api_v2（`server/api_v2/router.py` + ts-rest 类型同步 `docs/api_reference/ts-rest/`）；
  - MCP（`server/mcp_http.py`/`mcp_stdio.py`）；
  - mem-cli 技能：SKILL.md 要求 agent「查记忆优先于 grep/rg/find」且逐条判断充分性、缺一条再查下一条（`packages/skills/memmachine-memory/SKILL.md:1-33`）；
  - 记忆层同时服务 API 程序、MCP 客户端与 CLI agent 三种消费形态。

### 2.6 过滤 DSL 与检索 agent 配置（检索三件套的参数面）
- 属性过滤是一门完整的表达式 DSL（`common/filter/filter_parser.py`）：
  - 表达式节点：`Comparison / In / IsNull / And / Or / Not`（`filter_parser.py:25-66`）+ 词法 Token（`filter_parser.py:71-104`）；
  - 过滤字段两种命名：系统字段裸名（`producer_id` 等）、用户元数据 `m.<key>`/`metadata.<key>`（`long_term_memory.py:582-612` 的校验注释）；
  - event 后端校验拼写错误的字段名直接 ValueError 而非静默零命中（`long_term_memory.py:585-612`）；
  - declarative 后端用 `metadata.` 前缀 mangle 用户键（`long_term_memory.py:544-560`）；
  - SQL 侧有 `sql_filter_util.py` 把表达式下沉为安全 SQL 片段（`common/filter/` 目录）。
- 检索 agent 配置体系（`common/configuration/retrieval_config.py`）：
  - `RetrievalAgentConf`：`llm_model / answer_llm_model / judge_llm_model / reranker / use_optimized_coq`（`retrieval_config.py:29-56`）——改写、作答、判分三个 LLM 角色可分离配置；
  - `OptimizedCoqConf`：`multi_hop_decomposer`（非 LLM 分解器开关）与 `multi_hop_sub_limit`（每子查询固定 limit，只管最终返回上限之外的子搜索）（`retrieval_config.py:8-27`）。
- 图/向量双库的查询语义对齐：
  - `VectorGraphStore` 的 `search_directional_nodes` 以属性序游标支持时间邻域（`vector_graph_store.py:165`）；
  - neo4j 与 nebula 双实现（`neo4j_vector_graph_store.py`/`nebula_graph_vector_graph_store.py`）。
- 会话数据管理器（`common/session_manager/session_data_manager_sql_impl.py`）持久化跨实例会话状态；`count_caching_episode_storage.py` 对计数查询做缓存层。
- 可观测性内建：MetricsFactory 暴露 Ingestion/query 的 latency summary 与 counter（`episodic_memory.py:130-147`），Prometheus 后端（`common/metrics_factory/prometheus_metrics_factory.py`）+ OTel 全链路（`telemetry/otel.py:114` instrument OpenAI SDK）。

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）
```python
# common/reranker/rrf_hybrid_reranker.py:32-46 — RRF 融合重排
async def score(self, query: str, candidates: list[str]) -> list[float]:
    """Score candidates by aggregating ranks from multiple rerankers."""
    rerank_tasks = [
        reranker.rerank(query, candidates) for reranker in self._rerankers
    ]
    rankings = await asyncio.gather(*rerank_tasks)
    score_map: defaultdict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, candidate in enumerate(ranking, start=1):
            score_map[candidate] += 1 / (self._k + rank)
    scores = [score_map[candidate] for candidate in candidates]
    return scores
```
```python
# episodic_memory/declarative_memory.py:355-367 — 派生层向量检索 + 5x 过采样
matched_derivative_nodes = await self._vector_graph_store.search_similar_nodes(
    collection=self._derivative_collection,
    embedding_name=(DeclarativeMemory._embedding_name(
        self._embedder.model_id, self._embedder.dimensions)),
    query_embedding=query_embedding,
    similarity_metric=self._embedder.similarity_metric,
    limit=min(5 * max_num_episodes, 200),
    property_filter=mangled_property_filter,
)
```
```python
# episodic_memory/long_term_memory.py:398-400 — 邻域扩展的 1/3 偏分
expand_context = min(max(0, expand_context), max_num_episodes - 1)
max_backward_episodes = expand_context // 3
max_forward_episodes = expand_context - max_backward_episodes
```
```python
# episodic_memory/long_term_memory.py:644-651,669-677 — 防 `_` 前缀冒名（安全注释原文）
"""
Without this check a client could send
`{"_producer_id": "victim", "_session_key": "other-session"}` and
have its content indexed under those spoofed identities, enabling
cross-producer / cross-session impersonation through
`search_scored(property_filter=...)`. We raise loudly instead of
silently dropping so the client sees the misuse.
"""
raise ValueError(
    "Episode filterable_metadata contains reserved "
    f"`_`-prefixed keys (event backend only): {reserved}. "
    "These collide with system-defined properties "
    "(`_producer_id`, `_session_key`, `_episode_uid`, ...) "
    "and are rejected to prevent cross-producer / "
    "cross-session impersonation.")
```
```python
# episodic_memory/episodic_memory.py:448-456 — 双记忆去重，短期优先
episode_uid_set = {episode.uid for episode in short_episode}
unique_scored_long_episodes = []
for score, episode in scored_long_episodes:
    if episode.uid not in episode_uid_set:
        episode_uid_set.add(episode.uid)
        unique_scored_long_episodes.append((score, episode))
```

## 4. 基准/评测声明（反虚荣视角：自封 or 第三方？可复现？数字与口径）
- 内置三套 runner（`evaluation/README.md:1-40`）：
  - LoCoMo（ingest/search 两步：`./run_test.sh locomo exp1 ingest retrieval_agent`，README:53-62）；
  - WikiMultiHop（500 例）、HotpotQA validation（200 例）（README:65-70）；
  - 设计「memmachine / retrieval_agent / 纯 LLM」三对照组（`evaluation/README.md:15-24`）[自封-带 runner，部分可复现：configuration.yml 可换本地/非 OpenAI 模型]。
- README 层面未见具体 SOTA 数字战报（与 SimpleMem 风格相反）；CoQ prompt 注明方法出处 arXiv:2508.03680（`coq_agent.py:15-18`）[自封-方法论引用]。
- 数字需自行跑出 [不可复现-未见公开结果表]；无第三方独立评测。
- 评测目录另含 `episodic_memory/`（legacy LoCoMo 工作流，标注被 retrieval_agent 取代，README:10-12）——基准体系自身在迭代，历史数字口径可能漂移。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）
1. **原文/派生两层存储**：
   - episode 原文存图库（保真+时间游标）、Derivative 句级向量存向量库、`DERIVED_FROM` 边回溯（`declarative_memory.py:99-192`）；
   - 把「检索单元」与「记忆单元」解耦，检索命中句子但返回整段上下文，比 mem0 直接向量存记忆行更干净。
2. **时间邻域扩展（1/3 偏分）**：
   - 每篇命中自动带前后邻居、backward 取 1/3（`declarative_memory.py:398-400,443-497`）；
   - 用图库的双键 `(timestamp,uid)` 方向游标实现对话记忆特有的「前后文重建」，纯向量系统做不到。
3. **重排器即资源族 + RRF 组合子**：
   - 多种重排器可配置注入，RRF 以名次倒数和融合任意多个（`rrf_hybrid_reranker.py`）；
   - 混合检索的组合语义交给运维配置而非写死代码。
4. **分数阈值方向感知**：统一处理 cosine 高优/欧氏低优（`long_term_memory.py:432-445`）——多度量向量库下极易踩的坑。
5. **确定性 uuid5 双库映射 + 响亮失败句柄**：
   - episode↔event 可逆映射、drop partition 后置空句柄（`long_term_memory.py:388,391-425,447-456`）；
   - 双存储一致性的工程范本。
6. **检索充分性判断的对抗性约束**：
   - 只准引用已检文档、禁止编实体、不确定即判不足（`coq_agent.py:22-60`）——agentic 检索防幻觉的 prompt 纪律样板；
   - RaragQueryAgent 示范「优化变体保持槽位名不变」的可替换设计（`rarag_query_agent.py:205-207`）。
7. **互操作三面**（REST/MCP/mem-cli skill）+ SKILL.md 把「先查记忆再 grep」写成行为约束（`packages/skills/memmachine-memory/SKILL.md:13-33`）——记忆层平台化的完整形态。
8. **过滤 DSL 先验证后下沉**：拼写错误的过滤字段在门面层 ValueError 而非存储层静默零命中（`long_term_memory.py:585-612`）——查询正确性的低成本保障。

## 6. 局限与风险（失败模式、安全隐患、工程债）
- 写入零抽取：长期记忆=原文堆积，无事实蒸馏/去重/冲突消解，跨会话重复与矛盾记忆靠检索期重排硬扛——与 mem0/SimpleMem 的写入智能路线相反。
- 每会话一对 collection + 图边命名带 session 后缀（`declarative_memory.py:94-97`），会话海量时 collection 数与图 Schema 膨胀，无归档/合并策略。
- event 与 declarative 双后端并存但能力不对齐：
  - 过滤语义、score 处理各自实现（`long_term_memory.py:280-378` 双份代码）；
  - declarative 的 `metadata.` mangle 与 event 的 `_` 前缀两套用户键方案并存，维护面翻倍。
- 检索成本高：向量过采样 5×/4× + 逐上下文重排 + 邻域扩展 + （可选）多轮 CoQ agent——一次查询可触发 LLM 多轮 + 重排模型多次调用。
- 索引/存储非事务（代码自认 drift 可能，`long_term_memory.py:362-366`），只有告警无自愈。
- 短期记忆容量按字符数判满（`short_term_memory.py:174-185`），无 tokenizer 校准。
- `_` 前缀防护只覆盖 event 后端；declarative 后端用户键注入面需另审（`long_term_memory.py:544-560`）。
- RRF 融合对名次并列/候选缺失的情形无加权惩罚（`rrf_hybrid_reranker.py:39-45`），k=60 写死为默认而非配置化默认。
- 失败模式补充：
  - 双记忆并发查询任一抛错即整体失败（`asyncio.gather` 无 return_exceptions，`episodic_memory.py:412-425`）；
  - declarative 检索的图边回溯按命中 derivative 逐个并发（`declarative_memory.py:370-381`），命中多时对图库压力大；
  - `drop_session_partition` 后需重建实例（`long_term_memory.py:447-456`），调用方若复用旧引用将直接 RuntimeError——正确但易误用。

## 7. 一句话对比 mem0
mem0 是「聪明的写入、简单的检索」（抽取-更新-删除+向量召回），MemMachine 是「诚实的写入、豪华的检索」（原文保真+图库+RRF 重排+多跳 agent）——它把记忆难题从写入端搬到检索端解决，并以 REST/MCP/CLI 三面互操作把自己做成可被任意框架租用的记忆基础设施，而不是嵌入应用的库。

## 附：克隆快照与周边
- commit `2d28c1c`（2026-08-14，`[Feat] add RaragQueryAgent, an optimized ChainOfQueryAgent for multi-hop retrieval (#1477)`）——行号以此快照为准。
- 周边资产：
  - `deployments/helm/`（K8s charts）+ `tools/`（运维工具）——生产部署完备度最高；
  - `examples/`（openai_agent/qwen_agent/simple_chatbot/ts_rest_client_demo + v1 五个领域示例：crm/financial_analyst/health_assistant/writing_assistant）；
  - `maintainers/` 独立维护者文档目录——多机构共治痕迹；
  - `integrations/` 八框架适配（langchain/llamaindex/crewai/dify/fastgpt/n8n/openclaw/strands 两族）——互操作矩阵最宽的记忆服务之一。
- 版本面：server/client/common/meta/skills/ts-client 五包 monorepo（`packages/`），版本由 `common/api/version.py` 统一；`docs/api_reference/` 同时维护 Python 与 ts-rest 两套 API 参考。
