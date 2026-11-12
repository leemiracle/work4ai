# 02 · KB 存储：KBService 装配、LanceDB 版本化与 HybridRetriever 混合检索

## 角色定位

KB 能力包（`datamind/capabilities/kb/`）是新栈"知识库"面：把 embedding、向量库、检索器捆成一个服务。`KBService`（`kb/service.py:36`）——"Bundle of (embedding, vector store, retriever) scoped to one profile"，换 profile 整体重建。两个向量后端：Chroma（默认）与 LanceDB（带版本回滚）；检索器 simple/multi_query/hybrid 三策略进 `retriever_registry`。

## 内部结构

**工厂** `build_kb_service`（`kb/service.py:264`）：embedding 走 `build_embedding(..., fallback_llm=settings.llm)` 复用 LLM 网关凭据（L276）；vector_store 从 `vector_store_registry.create` 拿（L280-285）；策略分发 L292-315，`rerank=true` 直接 `ConfigError`——"not implemented; disable it instead of assuming reranking is active"（L288-291）。**兼容闸门**：构造时读 `kb_index_manifest.json` 比对 embedding_provider/model/dimension/chunk_size/corpus_hash（L58-73），不匹配置 `_compatibility_error`，此后 `search` 一律 "run explicit reindex"（L84-85）——防换模型后静默查错向量。**LanceDB 后端**（`kb/providers/lancedb_store.py:20` 注册）：构造器 `try: import lancedb` 失败转 `ConfigError("LanceDB requires pip install datamind[versioning]")`（L31-35），是全仓"延迟 import+转译成配置错误"先例；重开表用 `open_table` 而非 `create_table(exist_ok=True)`——后者字面 schema 比较会误杀无害差异（L44-49）；版本历史另存 `version_history.sqlite3`（L56-58）；schema 定长 float32 向量列（L74）。

## 外部连接

上游被 `runtime.assemble_data_plane`（`datamind/runtime.py:65-68`）与 `IngestService`（增量写入直写活库再补 manifest，`kb/service.py:153-187`）消费；下游依赖 `core/protocols` 三协议与 `core/registry`。`KBConfig`（`datamind/config.py:258-271`）：`ingest_mode='cocoindex'` 必须 `vector_store='lancedb'`。

## 数据流

**检索**：`search` → `retriever.aretrieve` → chunk `model_dump`。**混合检索**（`kb/providers/hybrid_retriever.py:46`）：BM25 词法 + 稠密向量 RRF 融合，`score = weight/(rrf_k+rank+1)`（L193，rrf_k 默认 60）；BM25 进程内懒建（L84-100），`_tokenize` 是 CJK 感知零依赖切分（L27-42，中文长词追加单字）；向量路包 `recover_read`（L179-184），失败可降级 bm25，结果打 `degraded:True, retrieval_method:'bm25'` 元数据（L201）——降级可见。**重建**：`reindex()` 走 staging 事务——Chroma 有 `create_staging_store/activate_staging`（`kb/providers/chroma_store.py:129/142`），失败 discard 保旧库；manifest 原子换（L119-130）；收尾 `rebuild_lexical` 踢 BM25 缓存（L148-150）。**版本化**：`search_at_version/rollback` 仅 LanceDB（L209-210 显式拒他库）；rollback 语义是"追加新 commit 复制目标版数据"，历史全保留（L231-257）。

## 设计决策（含批判）

可抄：①指纹闸门把配置漂移变成启动即错；②非 staging 第三方 provider 保留 reset 旧行为而内置 Chroma 走事务（L100-103），诚实分层；③RRF 零超参默认融合。**批判**：BM25 全量驻内存，头注释自认 ~1M chunk 上限，之后须换 Tantivy；`_tokenize` 正则近似分词专名召回吃亏；`aretrieve_at_version` 每次全量重建历史版 BM25（L102-116 无缓存），时间旅行查询是 O(N) 重活。

## 新人提示

报 "run explicit reindex" 先查是否换了 embedding 模型/dimension——manifest 闸门在说话。直写 vector_store 的旁路代码要自己触发 `rebuild_lexical`（正常路径自动踢）。LanceDB 装不上就 `pip install 'datamind[versioning]'`。`search_at_version` 要求 version 正整数且存在（L212-219）。混合检索调参仅 rrf_k/两路权重/candidate_multiplier，在构造器 L49-60。
