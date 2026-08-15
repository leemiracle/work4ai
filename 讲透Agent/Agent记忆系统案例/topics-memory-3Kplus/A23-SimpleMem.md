# A-23 `aiming-lab/SimpleMem`（3.7K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\aiming-lab__SimpleMem
> Python / simplemem+cross+OmniSimpleMem+EvolveMem 四支柱 / MIT ｜ 论文驱动（arXiv:2601.02553 等）的「压缩优先」终身记忆系统：文本走三阶段管线（语义结构化压缩→在线语义合成→意图感知检索规划），多模态走 MAU 统一原子单元，另附跨会话注入与检索自演化两个扩展支柱。

## 1. 架构总览（目录地图，标出核心目录的职责）
- `simplemem/core/` — 文本记忆核心：
  - `memory_builder.py`（433 行，阶段 1+2 写入）、`hybrid_retriever.py`（969 行，阶段 3 检索规划与反思）、`answer_generator.py`（问答生成）；
  - `models/memory_entry.py`（多视图索引数据模型）、`database/`（LanceDB 默认后端 + 可插拔 backend 接口）、`utils/`（LLM/嵌入）。
- `simplemem/router.py` — 注册表式工厂：
  - `text` / `omni` 两模式显式注册（`router.py:221-246`）；
  - `AutoMemory` 按首次调用自动选后端，选定后不可切换（`router.py:253-308`）。
- `simplemem/multimodal/` — Omni-SimpleMem（约 60 文件）：
  - `core/mau.py`（多模态原子单元）、`processors/`（text/image/audio/video 四处理器）、`triggers/`（熵触发选择性摄取）；
  - `storage/`（mau_store/semantic_store/cold_storage/vector_store）、`retrieval/`（pyramid_retriever 金字塔检索 + bm25_store + expansion_manager）；
  - `knowledge/`（知识图谱：knowledge_graph/entity_extractor/graph_retriever）、`parametric/`（蒸馏为参数记忆）、`evolution/`（experience_engine/meta_controller/strategy_optimizer）、`evaluation/`（benchmarks 47KB + evaluator 52KB）。
- `cross/` — 跨会话记忆（13 源文件 + 8 测试）：
  - `orchestrator.py`、`context_injector.py`（token 预算打包）、`storage_lancedb.py`/`storage_sqlite.py`、`collectors.py`、`hooks.py`、`consolidation.py`；
  - `api_http.py`/`api_mcp.py` 双出口。
- `simplemem/evolver/` — EvolveMem 自演化引擎：
  - `evolution.py`（76KB 闭环引擎）、`manager.py`（193KB 门面）、`store.py`（71KB）、`diagnosis.py`（48KB 失败诊断）；
  - `multi_retriever.py`、`policy_optimizer.py`、`self_upgrade.py`（36KB）、`replay.py`、`benchmarks/`（locomo/longmemeval/membench 适配器）。
- `OmniSimpleMem/`、`MCP/` — 独立部署副本（云服务/Docker）；`SKILL/`、`SimpleMem.skill` — Claude 技能集成。
- deepwiki 的 Three-Stage Pipeline / Omni-SimpleMem / Cross-Session / Memory Evolution 章节划分与本地目录一一对应 [deepwiki-已验证]。

## 2. 记忆机制深读（本笔记核心，每个论断钉 `相对路径:行号`）
### 2.1 写入/抽取管线（谁触发、prompt 是什么、结构化 schema）
- **阶段 1·语义结构化压缩**（Section 3.1，`simplemem/core/memory_builder.py:1-9`）：
  - 滑动窗口：`window_size` 对话 + `overlap_size` 重叠保证跨窗指代连续，step=window-overlap（`memory_builder.py:41-45,139-142`）；
  - 缓冲区攒满窗口即触发 LLM 抽取（`memory_builder.py:58-66`）；
  - 批量大于 2×窗口时切多窗口 ThreadPoolExecutor（max 3 workers）并行抽取，失败回退顺序处理并恢复缓冲区快照（`memory_builder.py:72-74,85-130,338-371`）。
- 抽取 prompt 三铁律（`memory_builder.py:238-306`）：
  - ①**完整覆盖**：生成足够条目覆盖窗口内全部信息（对应阶段 2 的写时合成，`memory_builder.py:29`）；
  - ②**强制消歧**：绝对禁止代词（he/she/it/this/that）与相对时间（yesterday/today/last week）（`memory_builder.py:248`）；
  - ③**无损复述**：lossless_restatement 必须是主宾/时间/地点齐全、独立可懂的完整句（`memory_builder.py:249,263-265`）。
- 输出 schema 即 `MemoryEntry` 字段：`lossless_restatement / keywords / timestamp(ISO8601) / location / persons / entities / topic`（`memory_builder.py:259-274`；`simplemem/core/models/memory_entry.py:13-53`）。
- 抽取温度 0.1、可选 `response_format=json_object`、JSON 解析失败重试 3 次（`memory_builder.py:201-227`）。
- **阶段 2·在线语义合成**（Section 3.2）：写入时即做会话内整合——上一窗口前 3 条记忆作为去重上下文传入 prompt（`memory_builder.py:179-184`）；并行模式下保留最后 10 条做跨批上下文（`memory_builder.py:369-371`）。
- Omni 侧选择性摄取：
  - 处理器先跑熵触发（`TriggerResult`，熵增量低于阈值即跳过冗余帧/段），拒绝时 `skipped=True`，`force=True` 可越过（`simplemem/multimodal/processors/base.py:19-28,69-88`）；
  - 质量分 `trigger_score/entropy_delta` 记入 `QualityMetrics`（`simplemem/multimodal/core/mau.py:27-40`；`base.py:204-207`）。

### 2.2 存储后端与数据模型（表/集合/文件布局，原文摘录 schema）
- 文本通道：LanceDB 单表（表名走 settings）：
  - 每条记录 `VectorStoreRecord(entry_id, vector, metadata={lossless_restatement, keywords, timestamp, location, persons, entities, topic})`——**向量只对 lossless_restatement 编码**，其余字段作元数据（`simplemem/core/database/vector_store.py:55-79`）；
  - 后端可插拔：`VectorStore` 门面接受 `backend_factory`，默认 `LanceDBVectorStoreBackend`（`vector_store.py:16-43`）。
- 多模态通道·**MAU（Multimodal Atomic Unit）统一表示**——本仓最有价值的模式，任何模态归一为：
  ```
  id / timestamp / modality_type(text|visual|audio|video|multimodal)
  summary(粗检索短文) + embedding(稠密向量)   ← 轻量字段常驻 RAM
  raw_pointer(原始数据冷存储指针)              ← 重数据外置
  details(深度查询时才惰性加载)
  metadata(session/source/tags/quality/persons/entities/keywords/location/topic)
  links(event_id 父事件, prev/next 时序, related 跨模态关联)
  region_pointers(图像区域指针) / status(ACTIVE|ARCHIVED|PINNED) / storage_tier(HOT|COLD)
  ```
  （字段定义 `simplemem/multimodal/core/mau.py:118-160`；「RAM 只存轻字段、重数据走冷存储、details 惰性加载 = Memory-Compute Decoupling」设计原则 `mau.py:121-129`；轻量导出 `get_lightweight_dict` `mau.py:209-222`）。
- MAU 元数据同样抽取 persons/entities/keywords/topic，与文本 MemoryEntry 的符号层字段**同构**（`mau.py:54-59`）——这是「统一表示」的落点。
- 跨会话通道：SQLite（会话摘要/观察/条目）+ LanceDB（向量）双库（`cross/storage_sqlite.py`、`cross/storage_lancedb.py`；类型定义 `cross/types.py` 中 `ContextBundle/SessionSummary/CrossObservation/CrossMemoryEntry`）。

### 2.3 检索策略（向量/关键词/混合/重排/图，参数与阈值）
- **阶段 3·意图感知检索规划** `P(q,H)→{q_sem,q_lex,q_sym,d}`（`simplemem/core/hybrid_retriever.py:1-8`），五步流水（`hybrid_retriever.py:75-127`）：
  - ① LLM 分析信息需求 `_analyze_information_requirements`（`hybrid_retriever.py:650`）；
  - ② 生成靶向查询 `_generate_targeted_queries`（`hybrid_retriever.py:719`）；
  - ③ 多查询并行语义检索（max 3 workers，`hybrid_retriever.py:94-101,559-604`）；
  - ④ 补关键词检索（BM25 词法层 `R_lex = Top-n(BM25(q_lex, m_i))`，`hybrid_retriever.py:28,106-109`）+ 结构化检索（符号层，dateparser 解析时间表达式→时间范围过滤，`hybrid_retriever.py:292`）；
  - ⑤ 合并去重（`hybrid_retriever.py:116-118`）。
- 合并无 RRF 加权，是**优先级去重**：structured > semantic > keyword 顺序入列、按 entry_id 去重（`hybrid_retriever.py:326-343`）。
- **反思循环**：
  - `_retrieve_with_intelligent_reflection` 让 LLM 对照信息计划检查答案充分性，缺什么补查（`hybrid_retriever.py:794`）；
  - 默认 `max_reflection_rounds=2`（`hybrid_retriever.py:41,54`）；
  - `retrieve(query, enable_reflection=False)` 可对对抗性问题关闭反思（`hybrid_retriever.py:58-73`）。
- 三路 top_k 独立配置：SEMANTIC/KEYWORD/STRUCTURED_TOP_K 走 settings（`hybrid_retriever.py:47-49`）。
- Omni 检索：**金字塔渐进检索**——`retrieve_preview` 只返回 SUMMARY 级轻量结果并标记 `expansion_candidates`，`expand()` 按需加载 EVIDENCE 原文（`simplemem/multimodal/retrieval/pyramid_retriever.py:30-84,220-234`）；FAISS/BM25 混合（README:309）；另有知识图谱多跳检索 `knowledge/graph_retriever.py`。

### 2.4 遗忘·整合·演化（有无 decay/merge/re-rank/自更新）
- 文本通道无 decay/merge——写入即终态（阶段 2 在写时一次成型）；遗忘只存在于 Omni：
  - MAU 生命周期 `ACTIVE→ARCHIVED（带 archive_reason/archive_run_id）/PINNED`、分层 `HOT/COLD`（`mau.py:155-160`）；
  - `consolidate_memories(force)` 归并入口（`simplemem/multimodal/orchestrator.py:1142`）。
- **参数记忆蒸馏**：`distill_to_parametric()` 把记忆蒸馏进参数存储（`orchestrator.py:1152`；`parametric/memory_distiller.py` 18KB）。
- **EvolveMem 自演化**（区别于一切静态系统）：
  - 闭环 `Extract→Index→Retrieve→Answer→Evaluate→Diagnose→Adjust→Repeat`，LLM 按题诊断失败根因并改检索配置（`simplemem/evolver/evolution.py:23-33`）；
  - 回归自动回滚 + 停滞期探索激励（README:313）；
  - 刻意从弱初始配置起步换大提升空间（`evolution.py:50-52` `weak_initial_config()`）；
  - 演化中发现原设计没有的检索维度：查询分解、实体交换、答案验证（README:313）。
- Omni 在线演化引擎：`evolution/experience_engine.py`、`meta_controller.py`、`strategy_optimizer.py`；`query_with_evolution`/`record_answer_feedback` 把答案反馈回灌检索策略（`orchestrator.py:1226,1290`）。

### 2.5 注入上下文的方式（系统提示拼装、token 预算）
- 跨会话注入是本仓注入侧精华，`ContextInjector.build_context()` 按**优先级三层贪心装箱**（`cross/context_injector.py:147-241`）：
  - ①会话摘要（最高优先，`context_injector.py:174-188`）；
  - ②细粒度观察（`context_injector.py:190-204`）；
  - ③针对当前 prompt 的语义检索结果（仅当 prompt 提供且预算有余，`context_injector.py:206-225`）；
  - token 预算默认 `max_tokens=2000`，逐层扣减（`context_injector.py:133-141`）。
- 装箱函数 `_budget_items`：零成本项免费放行、超预算即停（`context_injector.py:98-110`）。
- token 估算用最朴素的分词计数 `len(text.split())`（`context_injector.py:33-40`）——便宜到可调千次，但中文会严重低估。
- 文本通道问答走 `answer_generator.py` 把检索条目拼上下文交 LLM 生成；Omni 的 `answer()` 含 JSON 答案抽取（`orchestrator.py:850-1107`）。

### 2.6 Omni 查询编排与反馈闭环（统一表示之上的消费端）
- `OmniMemoryOrchestrator.query()`（`simplemem/multimodal/orchestrator.py:700`）：
  - `_generate_search_queries` 先生成多查询（`orchestrator.py:619`）；
  - `_merge_retrieval_results` 融合多路命中（`orchestrator.py:664`）；
  - `expand()` 对外暴露 MAU 深度扩展（`orchestrator.py:828`），`answer()` 出最终答案并 `_extract_answer_from_json`（`orchestrator.py:850,1062`）。
- 检索路径分派：`_hybrid_retrieval`（`orchestrator.py:1391`）、`_graph_retrieval` 知识图谱通道（`orchestrator.py:1375`）、`_parametric_retrieval` 参数记忆通道（`orchestrator.py:1349`）——三种记忆形态（MAU/图谱/参数）在查询期并列可选。
- 反馈闭环：`query_with_evolution`（`orchestrator.py:1226`）+ `record_answer_feedback`（`orchestrator.py:1290`）把答案质量回灌 evolution 引擎；`get_evolution_stats` 暴露统计（`orchestrator.py:1410`）。
- 图谱侧：`graph/event_manager.py`/`event_store.py` 维护事件层（EventNode/EventLevel，`retrieval/pyramid_retriever.py:21` 引用），MAU 经 `links.event_id` 挂到事件（`mau.py:232-234`）。
- 会话生命周期：`start_session/end_session`（`orchestrator.py:227-244`）+ `get_events/get_event_details/get_stats` 供 UI（`orchestrator.py:1109-1140`）。
- 图像摄取两种策略：`add_image_with_caption_averaged`（caption+区域均值嵌入）与 `add_image_on_demand_caption_only`（仅按需 caption）（`orchestrator.py:390,443`）——多模态嵌入成本的三档选择。

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）
```python
# simplemem/core/models/memory_entry.py:13-31 — 多视图索引的记忆单元
class MemoryEntry(BaseModel):
    """Indexed via: I(m_k) = {s_k (Semantic), l_k (Lexical), r_k (Symbolic)}"""
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # [Semantic Layer] - Dense embedding base (v_k = E_dense(S_k))
    lossless_restatement: str = Field(...,
        description="Self-contained fact with Φ_coref (no pronouns) and "
                    "Φ_time (absolute timestamps)")
    # [Lexical Layer] - Sparse keyword vectors (h_k = Sparse(S_k))
    keywords: List[str] = Field(default_factory=list,
        description="Core keywords for BM25-style exact matching")
    # [Symbolic Layer] - Metadata constraints (R_k = {(key, val)})
    timestamp: Optional[str] = Field(None,
        description="Standardized time in ISO 8601 format")
```
```python
# simplemem/multimodal/core/mau.py:121-146 — MAU：统一原子单元与存算解耦
"""
Design Principles:
1. RAM stores only lightweight fields (summary, embedding, metadata)
2. Heavy raw data stored in cold storage via raw_pointer
3. Details field is lazily populated only when deep query requires it
This achieves Memory-Compute Decoupling for efficient multimodal storage.
"""
# Lightweight indexing fields (always in RAM)
summary: str = ""      # Short text summary for coarse retrieval
embedding: Optional[List[float]] = None
# Cold storage pointer (raw data stored externally)
raw_pointer: Optional[str] = None
# Lazily loaded details (populated only on deep query)
details: Optional[Dict[str, Any]] = None
```
```python
# simplemem/core/hybrid_retriever.py:326-343 — 三路合并：优先级去重而非 RRF
def _merge_and_deduplicate(self, results):
    seen_ids = set()
    merged = []
    # Merge by priority (structured > semantic > keyword)
    for source in ['structured', 'semantic', 'keyword']:
        for entry in results.get(source, []):
            if entry.entry_id not in seen_ids:
                seen_ids.add(entry.entry_id)
                merged.append(entry)
    return merged
```
```python
# cross/context_injector.py:98-110 — 预算装箱：零成本免费、超支即停
def _budget_items(items, text_fn, remaining_tokens):
    accepted, consumed = [], 0
    for item in items:
        cost = _estimate_tokens(text_fn(item))
        if cost == 0:
            accepted.append(item)   # Zero-cost items are free to include
            continue
        if consumed + cost > remaining_tokens:
            break
        accepted.append(item)
        consumed += cost
    return accepted, consumed
```
```python
# simplemem/evolver/evolution.py:23-33 — EvolveMem 闭环自演化
"""
    Extract -> Index -> Retrieve -> Answer -> Evaluate -> Diagnose -> Adjust -> Repeat
Each round automatically:
1. Extracts memories from conversation data (via MemoryExtractor)
2. Builds multi-view index (via MultiViewIndex)
3. Answers evaluation questions using retrieved context
4. Scores predictions against references (token-level F1)
5. Diagnoses failures and identifies root causes (via MemoryDiagnostics)
6. Adjusts retrieval parameters based on diagnosis
7. Repeats until convergence or max rounds
"""
```

## 4. 基准/评测声明（反虚荣视角：自封 or 第三方？可复现？数字与口径）
- LoCoMo：
  - 文本通道宣称平均 F1 较先前系统 +26.4%、推理 token 消耗约降 30×（README:305）[自封：口径为自跑对比，未给绝对 F1]；
  - Omni 版「SOTA F1=0.613 (+47%)」（README:134）[自封]。
- Mem-Gallery：F1=0.810 (+51%)（README:134）[自封]。
- EvolveMem：LoCoMo 较最强基线相对 +25.7%、MemBench +18.9%（README:133）[自封，但带 runner：`run_evolution.py --data data/locomo10.json --max-rounds 7`（README:501）]。
- 跨会话：「超 Claude-Mem 64%」（README:135）[自封：对手实现细节未公开]。
- 可复现性中上：三支柱各有 benchmark runner（README:483-512），数据依赖 LoCoMo 公开集；
  - 但 LLM 模型/温度未锁定则数字不可严格复现 [部分可复现]；
  - 无第三方独立评测。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）
1. **无损复述作为第一公民**：
   - 把「消解指代 + 绝对时间」做成抽取 prompt 的硬约束（`memory_builder.py:247-249`）；
   - 使每条记忆上下文无关——这是多视图检索（向量搜复述、BM25 搜关键词、元数据做过滤）能同时成立的前提；
   - mem0 的 fact 抽取并不强制这一点。
2. **MAU 统一多模态表示**：
   - summary+embedding 常驻、raw_pointer 冷存、details 惰性、region_pointers 细到图像区域（`mau.py:118-160`）；
   - 「模态归一为原子单元 + 存算解耦」是对多模态终身记忆最干净的一次建模。
3. **金字塔渐进检索**：
   - 先 SUMMARY 级预览、标记 expansion_candidates、按需 expand 到 EVIDENCE（`pyramid_retriever.py:6,220-234`）；
   - 把「检索深度」变成两级 API 而非一次性全量。
4. **三层贪心 token 装箱注入**：
   - 摘要>观察>语义命中的固定优先级 + 词数估 token + 零成本免费（`context_injector.py:121-141`）；
   - 跨会话冷启动注入的极简可复用方案。
5. **检索基础设施自演化**（EvolveMem）：
   - 诊断→提案→守卫（回归回滚）→停滞激励的闭环（`evolution.py:23-33`）；
   - 且证明「架构修复 > 超参调优」（README:309）——把 AutoResearch 用于检索配置而非记忆内容，方向独特。
6. 熵触发选择性摄取（`triggers/`、`QualityMetrics.trigger_score`）：用信息增量过滤冗余传感器帧，终身流式场景必备。
7. `AutoMemory` 惰性定模工厂：首个 add_* 调用决定 text/omni 后端、错调即报错并提示重建（`router.py:253-308`）——多后端产品的 API 收敛技巧。

## 6. 局限与风险（失败模式、安全隐患、工程债）
- 合并策略偏朴素：
  - 无 RRF/学习型融合，优先级写死 structured>semantic>keyword（`hybrid_retriever.py:336`），三路分数不可比时排序武断；
  - `_check_answer_adequacy` 等中间判断全靠 LLM，无校准。
- token 估算 `len(text.split())`（`context_injector.py:33-40`）对中文/代码场景系统性低估，2000 预算可能实际超支数倍。
- 检索规划+反思一次查询触发 5-10+ 次 LLM 调用（需求分析、靶向查询生成×N、充分性检查、补充查询），延迟与成本随反思轮数放大（`hybrid_retriever.py:75-127`）。
- 写入端质量风险：
  - `memory_builder.py` 大量 `print` 而非 logger（`memory_builder.py:112-113,144-155`）；
  - `previous_entries[:3]` 去重上下文窗口极小，长会话仍可能重复记忆（`memory_builder.py:183`）；
  - LLM 解析三连败即整窗丢弃返回 []（`memory_builder.py:224-227`）——静默丢记忆。
- 仓库冗余严重：`OmniSimpleMem/`、`MCP/reference/`、`simplemem/integrations/reference/` 与主包代码多副本并存，四支柱各自为政，统一 API（`router.py`）只覆盖 text/omni 两支。
- 无安全扫描/隐私脱敏层；冷存储 raw_pointer 落盘路径无加密。
- README 战报式宣称（"SOTA""outperforming by 64%"）均无第三方复核（见第 4 节）。

## 7. 一句话对比 mem0
mem0 用「抽取-更新-删除」的运维式记忆生命周期换生产稳定性；SimpleMem 用「写入时一次压到无损 + 检索时规划反思 + 基础设施自演化」的研究式激进管线换检索上限——它证明记忆质量大头在写入端（Φ_coref/Φ_time 消歧）与检索端（intent planning），而 mem0 的重心在存储端的增删改查编排。

## 附：克隆快照与论文对应度
- commit `db80b6a`（2026-07-24，合并 dense-vector-backend-interface PR #76）——行号以此快照为准。
- 论文对应度：代码注释直接标注论文章节号（`memory_builder.py:3-8` 的 Section 3.1/3.2、`hybrid_retriever.py:1-7` 的 Section 3.3、`memory_entry.py:4-6` 的多视图索引），Φ_gate/Φ_coref/Φ_time 等符号与 README 口径一致 [deepwiki-已验证：Three-Stage Pipeline 章节与代码注释互证]。
- 论文列表：SimpleMem=arXiv:2601.02553、Omni=arXiv:2605.13941、EvolveMem=arXiv:2604.01007（README:545-565）。
