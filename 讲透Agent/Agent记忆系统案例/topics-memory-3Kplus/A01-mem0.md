# A-01 `mem0ai/mem0`（63K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\mem0ai__mem0
> Python 2.0.18（pyproject.toml:7）｜Python SDK ≈1.18MB/148 文件 + TS SDK + Server + CLI ｜ Apache-2.0 ｜ 一句话定位：生产级 Agent 记忆层，"ADD-only 抽取 + 三信号混合检索"算法已成事实标准参照物

**本篇性质：增量核对**。本地已有精读专档 `..\mem0开源记忆层\notes\`（基准 HEAD `4debc58a`，覆盖至 April 2026 新算法）。本篇核对当前 HEAD `001c235`（2026-08-14）相对专档的差异，全部论断标注 **[已覆盖]**（专档已有）/ **[新增]**（专档之后出现）/ **[微移]**（内容一致、行号漂移）。

## 0. 增量核对结论（先说答案）

| 维度 | 核对结果 |
|---|---|
| 核心算法 | **[已覆盖]** 无算法级变化。`main.py` 3854 行 vs 专档记录 3851 行，仅 ±3 行漂移 |
| Provider 数量 | **[已覆盖]** 完全一致：LLM 21 / Embedding 15 / VectorStore 28 / Reranker 5，与专档 `02-py-sdk-providers` 计数逐项吻合 |
| 检索管线 | **[已覆盖]** 三信号融合（semantic+BM25+entity boost）与专档 `07-search-pipeline.md` 一致 |
| 文档层 | **[新增-微小]** `docs/open-source/features/reranker-search.mdx` 与 `docs/components/rerankers/` 文档树为最近补齐（HEAD 提交即 "remove duplicate reranking redirect"，#6975）；代码本身专档已覆盖 |
| 基准口径 | **[已覆盖]** README.md:49-52 数字（LoCoMo 92.5 / LongMemEval 94.4 / BEAM-1M 64.1 / BEAM-10M 48.6）与专档 `05-two-modes.md:245-248` 完全相同，未刷新 |

结论：**距专档基准约 3 个月的增量几乎为零**，处于算法稳定期 + 文档打磨期。以下 §1-§6 按模板结构给出钉版行号（以当前 HEAD 重新校准，供专档行号漂移时对照）。

## 1. 架构总览（目录地图）

```
mem0ai__mem0/
├── mem0/                  # Python SDK 核心（本次核对重点）
│   ├── memory/main.py     # Memory + AsyncMemory 双类（3854 行）
│   ├── memory/storage.py  # SQLite 变更历史 [已覆盖]
│   ├── memory/notices.py  # 1582 行用户 notice 系统（首跑/规模/慢查询/时序）[已覆盖]
│   ├── configs/prompts.py # 1062 行 prompt 模板（含 ADDITIVE_EXTRACTION_PROMPT）[已覆盖]
│   ├── reranker/          # 5 个 reranker [已覆盖]
│   ├── utils/             # scoring / lemmatization / entity_extraction [已覆盖]
│   └── client/project.py  # 944 行 org/project 托管台管理 [已覆盖]
├── mem0-ts/               # TS SDK（OSS + hosted 双模式）[已覆盖]
├── server/                # FastAPI 自托管 [已覆盖]
├── evaluation/            # git submodule → memory-benchmarks [已覆盖]
├── integrations/ skills/ cli/  # MCP 插件 / 编辑器 skills / 双 CLI [已覆盖]
```

## 2. 记忆机制深读（行号以 HEAD `001c235` 校准）

### 2.1 写入/抽取管线 [已覆盖，微移]
- 入口 `Memory.add()`：`mem0/memory/main.py:760`；内部转 `_add_to_vector_store()`：`main.py:879`。
- 抽取 prompt 按 actor 分流：`_should_use_agent_memory_extraction()` `main.py:739`，对应 `USER_MEMORY_EXTRACTION_PROMPT`（`configs/prompts.py:63`）与 `AGENT_MEMORY_EXTRACTION_PROMPT`（`configs/prompts.py:124`）。
- 核心 ADD-only 模板 `ADDITIVE_EXTRACTION_PROMPT`（`configs/prompts.py:468-537+`）：注释自述 "V3 Additive Extraction Prompt (ADD-only with memory linking)，从 platform/backend 移植"（`configs/prompts.py:463-466`）。关键规则原文：*"Your sole operation is ADD"*（prompts.py:472）；去重参照为 "Recently Extracted Memories (up to 20)"（prompts.py:501-503）；关联规则 `linked_memory_ids`（prompts.py:513）；相对时间锚定 `Observation Date`（prompts.py:524-535）。
- **V3 分阶段批处理管线**（`_add_to_vector_store()` main.py:879-1207，注释自述 "V3 PHASED BATCH PIPELINE" main.py:916）：
  - Phase 0 上下文收集：`db.get_last_messages(scope, limit=10)` 取近 10 条历史消息做指代消解（main.py:918-921）；
  - Phase 1 现有记忆检索：语义 top-10 作为去重/链接参照（main.py:923-931）；
  - **UUID→整数映射防幻觉**：把现有记忆 id 重编号为 "0","1",... 喂给 LLM，防其编造 UUID（main.py:933-938）；
  - Phase 2 单次 LLM 抽取调用（main.py:940-969）；agent 场景追加 `AGENT_CONTEXT_SUFFIX`（main.py:941-944）；LLM 失败**显式抛 `LLMError`** 而非静默空返回（注释 main.py:963-969 记录了这一行为修正）；
  - Phase 3 批量嵌入（`embed_batch`，失败逐条回退，main.py:991-1003）；
  - Phase 4/5 MD5 哈希去重（跨库存量 + 批内 `seen_hashes` 双重，main.py:1005-1024）；同时写入 `text_lemmatized`（BM25 用）与 `hash` 字段（main.py:1026-1032）；
  - Phase 6 批量持久化 + 批量 history（均带逐条回退，main.py:1045-1084）；
  - Phase 7 批量实体链接：`extract_entities_batch` → 全局实体去重归一（`_normalize_entity_text` main.py:583）→ 单次批量嵌入 → entity_store upsert（main.py:1086-1107+）。
- `infer=False` 快路径：逐消息原样入库（跳过 system 消息），保留 role/actor_id（main.py:880-914）。
- 实体落库：`_upsert_entity()` `main.py:605`，`_link_entities_for_memory()` `main.py:707`。

### 2.2 存储后端与数据模型 [已覆盖]
- 记忆本体存 vector store（28 个后端可选），payload 键：`data/hash/created_at/updated_at/text_lemmatized/attributed_to/user_id/agent_id/run_id/actor_id/role/expiration_date`——见 `_search_vector_store` 的 promoted keys 白名单 `main.py:1690-1699`。
- 实体表复用同一 vector store provider、独立 collection：`entity_store` 懒加载 property `main.py:559`。
- 变更历史 SQLite（`mem0/memory/storage.py`，347 行）：两表 schema 原文——
```sql
CREATE TABLE IF NOT EXISTS history (          -- storage.py:108-119
    id TEXT PRIMARY KEY, memory_id TEXT, old_memory TEXT, new_memory TEXT,
    event TEXT, created_at DATETIME, updated_at DATETIME,
    is_deleted INTEGER, actor_id TEXT, role TEXT)
CREATE TABLE IF NOT EXISTS messages (         -- storage.py:134-141
    id TEXT PRIMARY KEY, session_scope TEXT, role TEXT,
    content TEXT, name TEXT, created_at DATETIME)
```
  `messages` 表即 Phase 0 的 `get_last_messages` 数据源（storage.py:298）；`history` 批量写入口 `batch_add_history`（storage.py:193）。
- 工程规模旁证：tests/ 101 个 py 文件；SQLite 线程锁 + 迁移逻辑（`_migrate_history_table` storage.py:20）。

### 2.3 检索策略 [已覆盖，微移]
- 入口 `Memory.search()`：`main.py:1379-1522`。参数：`top_k=20, threshold=0.1, rerank=False, explain=False`（main.py:1383-1389）。
- 九步流水线 `_search_vector_store()`：`main.py:1628-1731`：
  1. 预处理：词元化 `lemmatize_for_bm25` + 实体抽取 `extract_entities`（main.py:1634-1635）；
  2. 语义检索**过采样** `internal_limit = max(limit*4, 60)`（main.py:1641）；
  3. 关键词检索 `vector_store.keyword_search()`（main.py:1647，后端不支持则返回 None 优雅降级）；
  4. BM25 sigmoid 归一化 `normalize_bm25`（main.py:1659）；
  5. 实体加护 `entity_boosts`（main.py:1662-1664）；
  6. 融合打分 `score_and_rank()`（main.py:1680）。
- 融合公式钉死在 `mem0/utils/scoring.py:60-139`：`combined = (semantic + bm25 + entity_boost)/max_possible`，除数自适应 1.0/2.0/2.5/1.5（scoring.py:77-81,97-101）；`ENTITY_BOOST_WEIGHT = 0.5`（scoring.py:57）；**threshold 语义分前置门槛**——低于阈值者 BM25/entity 再高也被踢除（scoring.py:74-75,110-112）。
- BM25 sigmoid 参数按查询长度分档（≤3 词: 5.0/0.7 … >15 词: 12.0/0.5）：`scoring.py:16-40`。
- Rerank 为**可选后置**段：`rerank=True` 且配置了 reranker 时生效，失败静默回退原序（main.py:1499-1505）。
- 元数据过滤 DSL：eq/ne/in/nin/gt/gte/lt/lte/contains/icontains/通配/AND/OR/NOT（main.py:1402-1417），编译入口 `_process_metadata_filters()` main.py:1524。

### 2.4 遗忘·整合·演化 [已覆盖]
- 无时间衰减权重；有**显式过期**：`_payload_is_expired()` 过滤（main.py:1670），`show_expired` 可豁免（main.py:1389）。
- 演化走 update 路径 `Memory.update()`：`main.py:1815`，LLM 仲裁模板 `DEFAULT_UPDATE_PROMPT`（configs/prompts.py:176），LLM 在 ADD/UPDATE/DELETE/NONE 四事件中裁决，事件由 `get_update_memory_messages()` 组装（configs/prompts.py:406）；`_update_memory()` main.py:2032 负责改写 payload 并写 history。
- 过程性记忆独立通道：`_create_procedural_memory()` main.py:1993，模板 `PROCEDURAL_MEMORY_SYSTEM_PROMPT`（configs/prompts.py:326）。
- 删除时同步清理实体链接：`_remove_memory_from_entity_store()` main.py:652；`reset()` 全清 main.py:2124。
- async 镜像类 `AsyncMemory`（main.py:2167 起，3854 行的后半），逐方法与同步版对称（如 `_bulk_clear_entity_store` main.py:2313、`_compute_entity_boosts_async` main.py:3390）——双轨维护是此文件膨胀主因。

### 2.5 注入上下文方式 [已覆盖]
- `MEMORY_ANSWER_PROMPT`（configs/prompts.py:4）+ `AGENT_CONTEXT_SUFFIX`（configs/prompts.py:947）；历史截断 `PAST_MESSAGE_TRUNCATION_LIMIT = 300`（configs/prompts.py:965）。SDK 本身不提供自动注入编排——注入责任在调用方（与 mem0 平台版 `mem0.search→prompt 拼装`不同）。

## 3. 关键代码摘录

摘录①（融合打分核心，`mem0/utils/scoring.py:110-119`）：
```python
semantic_score = result.get("score") or 0.0
if semantic_score < threshold:
    continue
mem_id_str = str(mem_id)
bm25_score = bm25_scores.get(mem_id_str, 0.0)
entity_boost = entity_boosts.get(mem_id_str, 0.0)
raw_combined = semantic_score + bm25_score + entity_boost
combined = min(raw_combined / max_possible, 1.0)
```

摘录②（过采样策略，`mem0/memory/main.py:1640-1644`）：
```python
# Step 3: Semantic search (over-fetch for scoring pool)
internal_limit = max(limit * 4, 60)
semantic_results = self.vector_store.search(
    query=query, vectors=embeddings, top_k=internal_limit, filters=filters
)
```

摘录③（rerank 失败静默回退，`mem0/memory/main.py:1499-1505`）：
```python
if rerank and self.reranker and original_memories:
    try:
        reranked_memories = self.reranker.rerank(query, original_memories, limit)
        original_memories = reranked_memories
    except Exception as e:
        logger.warning(f"Reranking failed, using original results: {e}")
```

摘录④（ADD-only 立场声明，`mem0/configs/prompts.py:470-472`）：
```python
# ROLE
You are a Memory Extractor — a precise, evidence-bound processor ...
Your sole operation is ADD: identify every piece of memorable information
and produce self-contained, contextually rich factual statements.
```

摘录⑤（UUID→整数防幻觉映射，`mem0/memory/main.py:933-938`）：
```python
# Map UUIDs to integers (anti-hallucination)
existing_memories = []
uuid_mapping = {}
for idx, mem in enumerate(existing_results):
    uuid_mapping[str(idx)] = mem.id
    existing_memories.append({"id": str(idx), "text": mem.payload.get("data", "")})
```

## 4. 基准/评测声明（反虚荣视角）
- README.md:49-52：LoCoMo 92.5（vs 基线 71.4）、LongMemEval 94.4（vs 67.8）、BEAM-1M 64.1、BEAM-10M 48.6，附延迟 0.88-1.09s —— **[自封]**（自家 evaluation submodule `memory-benchmarks`，README.md:66-68 自我表述 "+21 points"）。BEAM 基线列标 "—"（无对手数字），**口径存疑**。第三方独立复现仍缺。
- `evaluation/` 是空壳 submodule（需 `git submodule update --init`），克隆内不可直接复现 → **[不可复现-本地]**（可拉子模块后评估）。

## 5. 可借鉴模式（相对本系列其余仓库的增量）
- **[已覆盖但值得重申]** threshold 前置门槛 + 归一化除数自适应（scoring.py:74-81）：解决"三路分数量纲不一致"这一混合检索最常见翻车点，且 `explain=True` 时输出全部分量（scoring.py:126-135）便于调试——比黑盒 fusion 可审计性强。
- **[已覆盖]** "抽取 prompt 分 actor（user/agent）" 双模板（prompts.py:63/124）：记忆归属（attributed_to/role）在写入时定型，而非检索时猜测。
- **[已覆盖]** UUID→整数防幻觉映射（main.py:933-938）：LLM 引用存量记忆时只允许返回批内序号，由代码侧回查真 UUID——所有"LLM 需要引用库内对象"场景的通用防护。
- **[已覆盖]** MD5 硬去重 + 语义软去重双层：哈希挡完全重复（main.py:1020-1024），prompt 内 "Recently Extracted Memories" 挡语义重复（prompts.py:501-503），成本低且可解释。
- **[已覆盖]** 时效性在 prompt 层解决：Observation Date 锚定相对时间（prompts.py:524-535），而非检索期重写查询。
- **[新增-微小]** reranker 官方文档化（`docs/open-source/features/reranker-search.mdx`）说明 rerank 已从实验特性转为推荐配置项，但仍默认关闭、失败即回退（main.py:1504）——"可降级的增强层"工程姿态。

## 6. 局限与风险
- [已覆盖] BM25 依赖后端实现 `keyword_search()`（main.py:1647），28 个 vector store 中不支持者静默降级为纯语义——不同后端检索质量**不可比**，评测换后端即换结果。
- [已覆盖] notices 系统 1582 行（`mem0/memory/notices.py`，实测行数与专档一致）本质是 OSS→付费平台的转化漏斗（专档 `03-telemetry.md` 已剖析），代码占比可观。
- 哈希去重对改写免疫：同一事实换个措辞即绕过 MD5（main.py:1020），语义去重全押在 prompt 自觉上，无嵌入级近重复检测。
- 抽取单点依赖：LLM 抽取失败即整条 add 失败（main.py:969 抛 LLMError），无本地降级路径（对照 mempalace 的零 LLM 管线）。
- 无 decay/重要性分层的长期演化仍缺位：记忆只增（ADD-only）+ 显式过期，规模上万后的噪声靠 top_k 过采样硬扛（main.py:1641）。
- 增量风险提示：本仓当前处于稳定期（3 个月算法零变化），**专档结论有效期长**，但 reranker 文档化暗示下一阶段可能默认开启 rerank，届时 search 延迟口径将变。

## 7. 一句话对比 mem0
（本篇即 mem0）——作为对照组：mem0 = "抽取端做重（ADD-only LLM 抽取+实体链接）、检索端做轻（三信号线性融合，无图）"；后两仓（mempalace / supermemory）分别押注"空间隐喻结构化"与"检索端重排管线"，三者代表记忆系统三种截然不同的复杂度投放方向。
