# 09 · RAG 进阶社区群：streaming_ingest_rag、multimodal_retrieval、knowledge_graph_rag、event-driven-rag-cve-analysis、routing-multisource-rag

## 角色定位

图谱 layer-10「RAG 进阶社区群」（178 节点）五个示例，每个都回答主线 RAG 没解决的问题：`streaming_ingest_rag`（53 节点）——**摄入怎么快起来**（Kafka+Morpheus 流水线）；`multimodal_retrieval`（47 节点）——**文档里的图和表怎么办**（多模态 LangGraph agent）；`knowledge_graph_rag`（41 节点）——**向量检索答不了多跳问题怎么办**（知识图谱+cuGraph）；`event-driven-rag-cve-analysis`（26 节点）——**RAG 怎么被事件触发而非人提问**（Morpheus CVE 分析）；`routing-multisource-rag`（11 节点）——**多源答案怎么合流**（LlamaIndex Workflow 路由）。合起来是"RAG 深水区五问"。

## 内部结构

**streaming_ingest_rag** 分两半：`producer/src/`（producer.py 229 行，`Publisher` 抽象基类封装 confluent-kafka AdminClient/Producer，L30-43，bootstrap 默认 `kafka:19092`；数据源 = Kafka 文本/URL + RSS + PDF）与 `morpheus_examples/streaming_ingest_rag/vdb_upload/`（Morpheus 官方示例的内嵌拷贝：`pipeline.py` 组装 deserialize→chunker→embedding→vdb_upload 各 stage，`schemas/` 下 Kafka source/raw chunker 等消息 schema）。

**multimodal_retrieval** 是三层包：根 `agent.py`（LangGraph 多模态问答 agent）+ `gradio/gradio_interface.py`（UI）+ `nv-mm-retrieval-app/`（FastAPI server `app/server.py` + `packages/nv-mm-document-qa/` 包，含 `chain.py`/`chain_full_collection.py`/`model_images.py`/`mongodb_utils.py` 等 8 模块）。

**knowledge_graph_rag** 前后端分离：`backend/`（FastAPI `server.py` 挂 chat/evaluation/visualization/ui_backend 四个 router；`utils/lc_graph.py` 199 行做图谱构建）+ `frontend/`（Streamlit `ui.py`，chat/visualization/evaluation 三页）+ `GTC25_DLI/`（GTC 2025 DLI 课程配套 notebook）。

**event-driven-rag-cve-analysis** 单目录 `cyber_dev_day/`（11 个 py 共 2348 行）：`pipeline.py` 用 Morpheus `InMemorySourceStage→DeserializeStage→LLMEngineStage→InMemorySinkStage`（L24-27）搭批处理管线，`checklist_node.py:230` 定义 `CVEChecklistNode(LLMNode)`，`tools.py`/`faiss_vdb_service.py` 提供检索。

**routing-multisource-rag** 五个文件 755 行：`workflow.py`（391 行核心）、`app.py`（Chainlit 入口）、`config.py`、`prompts.py`、`ingest.py`。

## 外部连接

五个示例的依赖面各自不同：streaming_ingest 要 Kafka 集群 + Milvus + Triton（embedding 可导出 HuggingFace 模型自部署）；multimodal_retrieval 连 MongoDB（存图像 base64，`mongodb_utils.get_base64_image`）+ NVIDIA API key（`agent.py:41` `os.environ["NVIDIA_API_KEY"]`）；knowledge_graph_rag 用 Milvus 向量库 + cuGraph/cuDF 加速 + Nemotron-4 340B 做合成数据与奖励评分（README 明示）；CVE 分析要 `nvcr.io/nvidia/morpheus/morpheus:v24.03.02-runtime` 容器；routing 要 `NVIDIA_API_KEY` 必需 + `PERPLEXITY_API_KEY` 可选（README 明确标注）。

## 数据流

**routing 的六步事件流**（`workflow.py`）是 LlamaIndex Workflow 事件驱动的教科书：`StartEvent` → `workflow_start`（L135）用 Pydantic 结构化输出 `RoutingChoice`（L59，`use_search` 布尔）决定走 `ShortcutEvent`（不检索直答）还是 `RawQueryEvent` → `rewrite_query`（L159）改写 → `embed_query`（L189）产 `EmbeddedQuery` → `milvus_retrieve`（L201）与 `pplx_retrieve`（L220）**并行**发 `MilvusQueryEvent`/`PerplexityQueryEvent` → `collect_nodes`（L271）用 `Context.collect_events` 等齐两路 → `synthesize_response`（L306）流式合成。文件头 docstring（L18-22）诚实列出 sharp edges：collect_events 数量不匹配会吐 None、LlamaIndex ~0.10.58 版本损坏。

**knowledge_graph_rag 的三元组流水线**（`backend/utils/lc_graph.py:34` `process_documents`）：DirectoryLoader 读 PDF → RecursiveCharacterTextSplitter（chunk_size=500/overlap=100）→ 切块存 CSV → 多路 LLM 并行抽三元组 → `save_triples_to_csvs`（L91）→ L150 起用 cuDF/cuGraph 建图 → L184 存 GraphML 给 Gephi-Lite 可视化。查询侧 `routers/chat.py:27` 的 `ChatRequest` 带 `use_kg` 开关：开则走 `GraphQAChain`+`NetworkxEntityGraph`，关则纯向量——图谱与向量是**可切换的对照实验**而非强制组合。

**multimodal_retrieval 的 agent 环**（`agent.py`）：`StateGraph`（L331）两节点——`assistant`（L334）与 `tools`（L335），典型 LangGraph ReAct 循环；解析链在 nv-mm-document-qa 包：PDF/图像经多模态 LLM 建 text/image 双索引，问答时文本走 FAISS、图表从 MongoDB 召回图像再 base64 塞 prompt。

**streaming_ingest 与 CVE 的"无提问 RAG"**：前者把"用户问→检索"倒置为"数据到→切块→embedding→入库"的常驻流水线，水平扩展靠多 worker 消费同一 topic；后者把触发器换成 CVE 公报事件，`CVEChecklistNode` 让 LLM 按清单逐步拉取 NVD 描述、依赖、补丁状态，产出可利用性判定——RAG 从问答变成**自动化研判工序**。

## 设计决策

1. **routing 的"先路由后检索"省一跳**：`use_search=False` 直接 Shortcut，闲聊不碰向量库——与 07 篇 digital-human 的 `[use_tools, use_checklist]` 二元路由同构，社区独立演进出了同一模式。
2. **knowledge_graph_rag 敢于"可关"**：`use_kg` 开关让每次问答都能 A/B 图谱检索 vs 向量检索，评测页（frontend/pages/evaluation.py）直接吃这个对照——学术示范工程的自觉。
3. **streaming_ingest 的 Morpheus 内嵌拷贝**：`morpheus_examples/` 整目录复制自 Morpheus 仓库而非 pip 依赖，好处是示例与 SDK 版本解耦、可自由魔改，代价是上游修复不会自动跟来——vendor-in 的经典取舍。
4. **CVE 分析用"清单节点"控漂移**：自由 agent 研判 CVE 容易漏步骤，`CVEChecklistNode` 把情报收集固化成 checklist 逐项执行；`pipeline.py:137-177` 还配了 `attempt_fix_list_string`/`fix_quotes` 一组 LLM 输出修补函数——对"LLM 输出不是合法 JSON/list"的防御性编程示例。
5. **multimodal_retrieval 的双前端**：gradio_interface 与 nv-mm-retrieval-app 两套 UI 并存，前者轻量演示后者接近产品——同一后端逻辑的两种包装，说明作者把"可弃置 demo"与"可部署服务"显式分层。
6. 值得注意的债：routing README 自标两处 WIP（Milvus Lite 向量查询、SQLite 历史存储），`ingest.py` 只有 41 行——入库侧远不如查询侧成熟，拿来当生产模板前要自己补全。

## 新人提示

- 想学 LlamaIndex Workflow 事件驱动就精读 `routing-multisource-rag/workflow.py` 一个文件，391 行覆盖路由/并行/汇合/流式四种模式；docstring 里的三条 sharp edges 都是踩过坑的人写的。
- 想学"图谱 RAG"先看 `lc_graph.py` 的构建侧（34-91 行），查询侧 GraphQAChain 是 LangChain 现成能力，难点全在三元组抽取质量与 cuGraph 建图。
- streaming_ingest_rag 是全仓少见的"性能导向"示例：README 有独立的 Performance Instrumentation 小节与水平扩展说明，适合与 07 篇 fm-asr 的单流 accumulator 对照——一个讲吞吐一个讲正确性。
- 甄别备注：任务书将 log_analysis_multi_agent_rag 归入本篇"agent 类示例"，但图谱把它分在 layer-11（社区应用百宝箱），本篇遵循图谱以五示例组织，log_analysis 留第 10 篇。行号锚（workflow.py:59/135/159/189/201/220/271/306、lc_graph.py:34/91/150/184、chat.py:27、agent.py:41/331、producer.py:30、pipeline.py:24/137、checklist_node.py:230）均对照源码核实。
