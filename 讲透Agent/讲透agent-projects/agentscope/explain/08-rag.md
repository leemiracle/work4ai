# 08 rag 检索增强：Knowledge/Reader/Store 三层与 ReActAgent 检索主链

> **勘误（以源码为准）**：任务来源所称的 `rrag/` 子包在本仓是**空目录**（`src/agentscope/rrag/` 无任何文件，全仓 grep "rrag" 零命中，知识图谱亦无 rrag 节点）；"retriever/re-rank" 也不是独立模块——检索抽象在 `rag/_knowledge_base.py`，重排发生在消费端 ReActAgent。本文按实际的 `rag/` 子包讲解。（锚相对 `src/agentscope/`，短名为唯一简写）

## 1. 角色定位

rag 子包是一个刻意做薄的 RAG 基座：`Document` 定义数据单元、`Reader` 负责分块、`KnowledgeBase` 抽象检索、`VDBStoreBase` 对接五家向量库（Qdrant/MilvusLite/OceanBase/MongoDB/阿里云 MySQL）。它不做 rerank 模型、不做查询路由，重排与注入策略全部上收到 agent 层。

## 2. 内部结构

**数据单元**：`Document`（`rag/_document.py:35`）是 dataclass，`metadata.content` 直接复用 message 包的 ContentBlock（`rag/_document.py:21`）——TextBlock/ImageBlock/VideoBlock 皆可入库，多模态 RAG 与文本 RAG 共用一条管线；`embedding` 与 `score` 字段分别由入库与检索回填，id 默认 shortuuid。

**知识库**：`KnowledgeBase`（`rag/_knowledge_base.py:13`）组合 `embedding_store` 与 `embedding_model` 两个注入点，只抽象 `retrieve`/`add_documents` 两方法；`retrieve_knowledge`（`rag/_knowledge_base.py:77`）是现成工具函数——把检索结果拼成带 Score 前缀的 ToolResponse，可直接注册给 agent。唯一实现 `SimpleKnowledge` 的检索就是"embed 查询（`rag/_simple_knowledge.py:38`）→ store.search"，入库前校验模态匹配（`rag/_simple_knowledge.py:67`）。

**存储层**：`VDBStoreBase`（`rag/_store/_store_base.py:10`）只抽象 add/search/delete，`get_client`（`rag/_store/_store_base.py:43`）是逃生舱——返回原生 client 让开发者用全量 VDB 功能。QdrantStore 的 point id 由 doc_id+chunk_id+content 的 JSON 哈希成 UUID（`rag/_store/_qdrant_store.py:104`），天然幂等 upsert；检索走 `query_points` 且透传 `score_threshold`（`rag/_store/_qdrant_store.py:140`）。

**读取层**：`TextReader` 按 `chunk_size`（默认 512 字符）与 `split_by`（char/sentence/paragraph）分块。

## 3. 外部连接

ReActAgent 原生消费：构造参数 `knowledge` 接收单个或列表（`agent/_react_agent.py:193`）；检索前可用 LLM 把口语 query 改写为具体检索式（`agent/_react_agent.py:959`）；多知识库结果汇总后按 `doc.score` 排序重排（`agent/_react_agent.py:981`）；命中文档包进 `<retrieved_knowledge>` 标签作为 user Msg 写入 working memory（`agent/_react_agent.py:1009`）。上游依赖 embedding 子包七家模型；五家 VDB 均为 optional extra（pyproject `qdrant`/`milvus`/`mongodb`/`oceanbase`/`ali_mysql`）。

## 4. 数据流

入库：原始文件 → Reader.`__call__` 分块 → 生成共享 doc_id 的 Document 列表 → `add_documents` 校验模态 → embedding_model 批量向量化 → store.add 落库（point id=内容哈希）。查询：用户 Msg → `get_text_content` 取查询文本 → （可选 LLM 改写）→ query 向量化 → store.search（score_threshold 过滤）→ 返回带 score 的 Document → agent 端重排 → 块内容拼进 Msg 注入对话。整条链无 reranker 模型参与。

## 5. 设计决策

①**content 复用 ContentBlock 而非裸 str**：多模态检索与消息体系零转换，图文混检直通。②**内容哈希 point id**：重复入库自动覆盖而非堆叠，幂等性由数据结构保证。③**不做 rerank**：跨知识库统一排序只在消费端做（`sorted` by score），保持子包零模型依赖。④**get_client 逃生舱**：抽象不覆盖的 VDB 高级特性直接放行原生 client，避免抽象层膨胀。

## 6. 新人提示

- 坑 1：`TextReader` 类 docstring 宣称按 "fixed chunk size and **chunk overlap**" 分块（`rag/_reader/_text_reader.py:14`），但实现**没有任何 overlap**——超长句/段在 chunk_size 处硬切（`rag/_reader/_text_reader.py:103`）。对切分敏感的任务需自写 Reader。
- 坑 2：`Document.id` 注释称 "unique ID of the data chunk"（`rag/_document.py:42`），但 TextReader 产出的一批 chunk **共享同一 doc_id**，唯一性实际由 store 的内容哈希 point id 承担——别拿 `Document.id` 当 chunk 主键去重。
- 坑 3：`split_by="sentence"` 依赖 nltk 且仅支持英文（`rag/_reader/_text_reader.py:30`），中文应选 char/paragraph。
- 坑 4：qdrant-client 被钉在 1.15.1——pyproject 注释明说 ≥1.16 与 pymilvus 冲突（`pyproject.toml:120`），同时装 milvus extra 时别随手升级。
- 坑 5：`QdrantStore.delete` 未实现（`rag/_store/_qdrant_store.py:159`），需要删除语义要走 `get_client()` 原生接口。
