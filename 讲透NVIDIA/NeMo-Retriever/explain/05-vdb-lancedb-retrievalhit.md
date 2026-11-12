# 05 · 向量库：common/vdb 抽象 + LanceDB 参考实现 + RetrievalHit 契约

> 路径相对 `nemo_retriever/src/nemo_retriever/`。

## 角色定位

`common/vdb/`（图谱 14 节点）是存储-检索层：`adt_vdb.py` 定义 VDB 接口与能力契约，`lancedb.py`（2311 行，全仓最大单文件）是唯一内置参考实现，`records.py`（666 行）定义读写记录形态与 `RetrievalHit` 契约，`factory.py` 懒注册后端，`hybrid_fusion.py` 提供混合融合策略。参考实现的意义：它是"任何向量库想接入本框架该长什么样"的样板——接口、能力上报、写读路径全套示范。

## 内部结构

**接入面**：`factory.py:8` `get_vdb_op_cls` 按字符串取实现类，`available_vdb_ops` 硬编码唯一键 `["lancedb"]`（`:14`）——懒 import 避免循环依赖。算子侧三件套在 `operators/vdb.py`：`IngestVdbOperator`（`:113`）、`PutVdbOperator`（`:215`）、`RetrieveVdbOperator`（`:274`），管线里的入库/检索站（见 03 篇）。

**LanceDB 主类**（`common/vdb/lancedb.py:704` `class LanceDB(VDB)`）：构造参数 30 余个（`:707-730`），默认 `index_type="IVF_HNSW_SQ"`（`:712`）；模式三选一互斥——`sparse and hybrid` 同传直接 ValueError（`:742`）。表管理：`create_collection`（`:938`）到 `delete_collection`（`:988`）七个 CRUD、文档级三操作（`:1003-1035`）、`health`（`:1088`）、`reconcile_collections`（`:1083`）对账。

**写入路径**：图行 → `_to_service_lancedb_row`（`:597`）展宽成服务表行，metadata/source 两个字段被 `_json_str`（`:213`）JSON 编码（`:639-640`）——**这是 metadata 在存储层的字符串化点**。索引建在 `create_index`（`:1165`）/`write_to_index`（`:1302`）；upsert 用稳定键：`table.merge_insert(key).when_matched_update_all().execute(rows)`（`:2116`）。流式摄取是完整状态机：`_iter_stream_rows`（`:1383`）按字节批量迭代、指纹去重 `_stream_request_fingerprint`（`:1439`）、`_mutate_stream_data`（`:1464`）变更应用、`_finalize_stream_write`（`:1575`）收尾、崩溃恢复 `_prepare_durable_stream_recovery`（`:1662`）与持久 schema `_durable_stream_schema`（`:1627`）；索引维护在 `_maintain_indexes`（`:1966`），IVF 分区数按行数自适应 `_effective_ivf_num_partitions`（`:256`）。并发防护用文件锁：`_table_mutation_lock`（`:119`）/`_table_index_lock`（`:132`）。

**检索路径**：`retrieval`（`:2183`）稠密/混合检索——hybrid 需要同时传 query_texts 且 `query_type='hybrid'`（`:2231-2242` 校验并 setdefault），fts 列默认 text（`:2243`）；hybrid_fusion 给定时每查询取 `max(top_k, candidate_depth)` 候选再融合（`:2287`）。`sparse_retrieval`（`:2126`）走稀疏向量列（schema 由 `_sparse_lancedb_arrow_schema :321` 定义）。读回的 JSON 由 `_maybe_parse_json`（`:230`）解码。FTS 有旧索引回退：`_run_fts_query_with_legacy_index_fallback`（`:150`）处理短语语法与索引代差；FTS 索引保障 `_ensure_fts_index`（`:821`）与未索引行探测 `_fts_unindexed_rows`（`:830`）。

**融合策略**（`common/vdb/hybrid_fusion.py`）：`HybridFusionPolicy` 冻结 dataclass（`:17-31` 校验 depth>0、0≤weight≤1、k>0）；默认 `DEFAULT_HYBRID_FUSION_POLICY`（`:34`）= candidate_depth 50 / dense_weight 0.8 / rrf_k 10。`WeightedRRFReranker(Reranker)`（`:37`）实现 `rerank_hybrid`（`:44-70`）：对两路 `_rowid` 列表按 `weight/(rrf_k+rank)` 累计得分（`:53-59`），附加 `_relevance_score` 列后按分数降序、融合序升序排（`:63-69`）——平分时偏稠密序。

**RetrievalHit 契约**（`common/vdb/records.py:112`）：`TypedDict(total=False)`，19 个可选字段（`:129-147`：text/metadata/source/source_id/path/page_number/pdf_basename/pdf_page/stored_image_uri/content_type/bbox_xyxy_norm/_distance/_score/_relevance_score/chunk_id/document_id/filename/document_version/content_sha256）。docstring（`:115-126`）钉死两条语义：①`metadata` 在此边界是**原生 dict，绝不许 JSON 字符串泄漏**，编码解码是 LanceDB 存储层的私事；②三个分数字段语义分工——`_distance` 向量距离、`_score` FTS/BM25 分、`_relevance_score` 混合融合分。**执行点是 `_normalize_hit`（`:565`）**：`:589-605` 构造 normalized dict，`:591-597` 的注释是契约活化石——历史上这里曾把 metadata 再编码回字符串，逼得所有下游（Retriever.query 调用方、CLI、SKILL.md 的 jq 配方）各自 json.loads，多数人没做，产生大量静默 `metadata.type=='?'` 假查询——修复即今契约。外层 `normalize_retrieval_results`（`:647`）批量套用。写方向契约在 `_client_record_from_graph_row`（`:288`）与 `to_client_vdb_records`（`:462`）/`to_sparse_client_vdb_records`（`:519`）。

**能力契约**：`lancedb_capabilities.py:42` `LanceTableCapabilities` 从表 schema 探测实际能力——`_metadata_retrieval_mode`（`:55`）读建表时写入的模式标记（`_with_retrieval_mode_metadata :278` 写入侧）、`_detect_fts_columns`（`:111`）、`wait_for_column_index`（`:146`）等索引就绪、`_mode_from_capabilities`（`:201`）按有无向量/FTS 列推断可用模式——服务层据此决定对旧表能开哪种检索。

## 外部连接

上游：`operators/vdb.py` 三算子与 `operators/graph_ops/lancedb_write_operator.py` 把图行送进来；`service/vectordb_app.py`（993 行独立服务）的集合 CRUD 与 `/v1/query` 直接建在本类上；查询侧 `query/workflow.py` 的 ResolvedQueryPlan 产 vdb_kwargs。下游：lancedb pip 包（`lancedb.rerankers.base.Reranker` 被 hybrid_fusion 继承）；sidecar 元数据在 `common/schemas/collections.py`。

## 数据流

写：图行（text/metadata/向量/稀疏）→ records.py 转 client 记录（剔除无嵌入无内容行 `:354`）→ JSON 编码 metadata → merge_insert upsert / 流式状态机分批落盘 → 索引后台维护（IVF/FTS）。读：查询向量+文本 → retrieval/sparse/hybrid → 原生 hit（`_distance`/`_score`）→ 可选 WeightedRRF 融合加 `_relevance_score` → `_normalize_hit` 归一成 RetrievalHit → 上层消费。

## 设计决策

1. **字符串化收在存储层**：JSON 编解码是 LanceDB 实现细节，接口边界全 dict——教训直接写进 docstring 与注释（`records.py:115-118,591-597`），属于"踩过的坑变契约"的教科书案例。
2. **模式显式三选一**：dense/sparse/hybrid 在构造期互斥校验（`lancedb.py:742`），宁可早炸不许跑一半换语义。
3. **稳定键 upsert 而非盲 append**：merge_insert 按 key 更新（`:2116`），重复摄取幂等——服务模式断点续跑的前提。
4. **融合策略 dataclass 化**：RRF 参数不是散 kwargs 而是 HybridFusionPolicy 值对象（校验集中、可序列化随请求传递），tie-break 规则显式（偏稠密序 `:68`）。
5. **能力探测代替版本协商**：不维护表版本号，每次按 schema 实探（capabilities），旧表自动降级到可用模式。

## 新人提示

- 任何下游代码里出现 `json.loads(hit["metadata"])` 都是 bug——metadata 已保证是 dict，遇到即上游破坏契约。
- 排查"分数看不懂"：先分清三字段（distance 越小越好、score/relevance 越大越好），混合模式才可能有 `_relevance_score`。
- 旧集合想开 hybrid：确认建表时带过 FTS 索引与模式标记，否则 capabilities 探测不到，得重建表。
- 新后端接入清单：继承 VDB（`adt_vdb.py`）→ 实现集合/写/读全家 → factory 注册键 → 补 capabilities 探测——照 LanceDB 方法签名抄骨架最稳。
