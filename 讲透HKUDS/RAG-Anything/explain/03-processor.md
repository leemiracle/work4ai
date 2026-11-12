# 03 · processor.py —— 2677 行处理引擎与 process_document_complete 主线

> 源码：`raganything/processor.py`（2677 行，commit 2cd2b332）。`ProcessorMixin`（`processor.py:62`）承载全仓最复杂的状态机：解析缓存、内容指纹 doc_id、文本排队语义、页码回填、多模态分发、doc_status 全生命周期簿记。

## 1. 角色定位

ProcessorMixin 是三 Mixin 里的「发动机」：`process_document_complete`（`processor.py:1985`）是单文档摄入公开主线；`process_document_complete_lightrag_api`（:2180）是给 LightRAG 反向调用的姊妹入口（带 `@document_context` 装饰器做 contextvars 隔离，:2179）。文件后半部（:1333-1980）是 type-aware 实体入库工具族（chunk 模板、实体抽取、belongs_to 关系、合并落库），把多模态 chunk 写进 LightRAG 图谱。三个静态工具奠定身份体系：`_file_content_fingerprint` 流式 SHA-256（1MB 分块，:71-77）、`_generate_content_based_doc_id`（:458）、`_generate_cache_key`（:94）。

## 2. 内部结构

**（a）缓存与身份**。`_generate_cache_key`（:94-128）把五元组——绝对路径、mtime、`file_sha256`、parser、parse_method——加上**影响解析结果的 kwargs 白名单**（`_relevant_parser_kwargs` :66，源自 `parse_options.py` 共享的 `PARSER_CACHE_KWARGS`）哈成 md5；内容指纹与 mtime 同时入键（:110,116），改内容必失效。doc_id 侧 `_generate_content_based_doc_id` 按块类型抽特征串（text 正文/image img_path/table table_body/equation text，:471-486），`compute_mdhash_id(signature, prefix="doc-")` 生成（:494）——字节级变化必改 doc_id，天然幂等。缓存读写 `_get/_store_cached_result`（:497,561）落在 parse_cache 上；`parse_document`（:614）先算键查缓存（:662-665），未命中才调 parser 并回写。

**（b）doc_status 簿记**。`_ensure_doc_status_record`（:135）补最小记录；`_drop_placeholder_doc_status`（:168）处理微妙约定：LightRAG 丢弃 doc_id 已存在的 insert、且不重试没存过文本的 FAILED 记录——RAG-Anything 自己写的占位记录必须先删，否则文本被永久阻塞（:169-176）。`_upsert_doc_status`（:394）与多模态完成标记三件套（:417,:427,:445,:1863）维护「文本完成≠多模态完成」的两段式状态。

**（c）排队语义——历史回归重灾区**。`_wait_for_text_processing`（:193-256）docstring 记录教训：LightRAG 管线忙时 `ainsert` 只入队就返回；LightRAG 只捞 PENDING/PROCESSING/FAILED，若提前写自己的 HANDLING（后来的 PROCESSED）状态，文本就被永久踢出队列（:199-208）。现行为：0.2s 起步指数退避到 2s 轮询（:222-233）、每 300s 心跳告警（:247-252）；管线空闲且文档仍在队里则主动跑 `apipeline_process_enqueue_documents`（:243-245）；管线被用户取消则抛错（:234-241）；终态 FAILED 上抛不静默（:253-256）。

**（d）页码回填**。`_annotate_text_chunk_pages`（:258）+`_text_chunk_page_labels`（:329）调 `utils.py` 的 `replay_chunk_spans`（utils.py:459），用与 LightRAG 相同的 chunk 几何参数**回放**分块位置映射回源页区间——几何推导而非文本搜索，规避同文重复误匹配。

**（e）多模态分发**。`_process_multimodal_content`（:867-1003）：already-processed 短路（:918-955，`force_reprocess=True` 可绕过——换存储后端重写多模态实体的场景，issue #154，:885-891）；主路 `_process_multimodal_content_batch_type_aware`（:970）；批处理抛异常降级逐条（:998-1000）并照样标记完成（:1003）——批故障不废整篇文档。跳过时若状态停在 HANDLING 也要补完成标记（:935-941）。

**（f）实体入库工具族**（:1333-1862）：chunk 转换（:1333）、chunk 模板（:1388）、chunk 落库（:1500）、主实体（:1517）并入全实体表（:1611）、批量实体抽取（:1671）、belongs_to 加边（:1700）、增量合并（:1764）、带 chunks 状态回写（:1801）。自省出口 `is_document_fully_processed`/`get_document_processing_status`（:1904,:1932）。

## 3. 外部连接（对齐图谱边）

- → `lightrag`：doc_status 读写、`insert_text_content`（:2091）、`apipeline_process_enqueue_documents`（:243）、图谱/向量存储写入、`compute_mdhash_id`（import :43）。
- → `parser.py`：`parse_document` 内部经 parser 实例调用（import :18-24）。→ `utils.py`：`separate_content_with_page_map`（import :25，调用 :2054-2056）拆文本流/多模态条目/页面区间；`replay_chunk_spans` 页码回放。
- → `parse_options.py`：`PARSER_CACHE_KWARGS` 白名单（import :38），与 batch_parser 增量 manifest 共享同一对象。→ `document_context.py`：装饰 lightrag_api 入口（:17 import，:2179 使用）。→ `base.py`：`DocStatus` 枚举（:16）。
- → `callbacks.py`：parse/text_insert/multimodal/document 四组事件全程派发（:2082-2088,:2116-2123,:900-906,:2160-2177）。
- ← `raganything.py`/`batch.py`：主类组合与批量入口消费 `process_document_complete`。

## 4. 数据流

`process_document_complete` 八步（:2026-2177）：①`_ensure_lightrag_initialized`（:2028）→ ②`parse_document`（:2045，缓存命中跳过解析）→ ③三分离（:2054）→ 纯多模态文档提前写 HANDLING 占位（:2062-2068）→ ④`set_content_source_for_context` 喂上下文源（:2075）→ ⑤文本线：删占位（:2090）→insert（:2091）→等待（:2099）→页码回填（:2102）→状态升 HANDLING（:2110）→ ⑥多模态线（:2131）或无多模态直接标记完成（:2140）→ ⑦异常统一落 FAILED+error_msg+stage（:2146-2154）后 re-raise → ⑧成功派发 on_document_complete 计时事件（:2170-2177）。`stage` 变量（:2023）随流程推进改值，异常时精确报告死在哪个阶段。

## 5. 设计决策

- **内容指纹优先于 mtime**：缓存键双保险（:110,116），doc_id 干脆只用内容签名（:458）——同名不同内容是不同文档，同内容不同路径幂等去重。
- **两段式完成语义**：LightRAG 的 PROCESSED 只代表文本完成，多模态标记独立存储（:417-455）——`is_document_fully_processed`（:1904）两侧都查才放行，杜绝「文本进了图谱、图表没描述」的半成品。
- **先等待后写状态**：自有状态写入严格排在 `_wait_for_text_processing` 之后（:2099→:2110 顺序不可换），这是排队语义修复后的钉版顺序，`test_queued_text_insert` 守护。
- **降级而非失败**：批处理崩→逐条（:996-1000）；缓存查询崩→继续（:957-959）。容错取向是「尽量往前走」。
- **lightrag_api 入口独立成方法**：需要 doc-pre- 前缀 id（:2210）、pipeline_status 直传、初始化失败持久化记账（`mark_initialization_failed` :2215-2253，created_at 必须真时间戳——空串被日期型后端静默丢弃，issue #328，:2236-2239）。

## 6. 新人提示

1. 排查「文档卡住不索引」先查 doc_status：HANDLING 卡死多半是旧版排队语义回归（对照 :193 docstring），FAILED 无重试多半是占位记录没删（:168）。
2. `force_multimodal_reprocess=True`（:1995）是换存储后端后的标准操作，否则多模态实体永远缺失（issue #154）。
3. 改 `PARSER_CACHE_KWARGS` 要意识到它同时影响解析缓存与 batch 增量 manifest 两处口径。
4. 调页码回填记住它是**几何回放**：LightRAG 的 chunk_token_size/overlap 改过而 RAG-Anything 没同步，页码就会漂。
5. 新埋点走 callback_manager.dispatch，四组事件钩子已覆盖 parse/text/multimodal/document 全周期。
