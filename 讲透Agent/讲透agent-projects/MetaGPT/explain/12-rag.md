# 12 RAG 与文档存储：llama_index 之上的薄封装及其裂缝

## 1. 角色定位

`metagpt/rag/` 与 `metagpt/document_store/` 是两条代际不同的存储检索线。rag 子系统是新一代：以 llama_index 为底座，把 index/retriever/ranker/embedding 全部 config 化（schema.py 定义 FAISS/Chroma/ES/Milvus/Qdrant/BM25 等三十余个 Config 类），核心引擎 `SimpleEngine`（engines/simple.py:64，继承 llama_index `RetrieverQueryEngine`）对外只露 from_objs/from_index 两个构造口与 retrieve/add_objs 两对操作。document_store 是旧一代 BaseStore 体系（faiss/milvus/qdrant/lancedb/chromadb 五实现），主要服务 repo_parser 代码知识库场景。全仓消费 rag 的四条线：Werewolf 经验池、exp_pool、RoleZeroLongTermMemory、web_scraping——rag 不是"给聊天加搜索"的产品功能，而是 MetaGPT 各记忆机制的公共底座。

## 2. 内部结构

SimpleEngine 四段式：`from_objs`（simple.py:138）从零建索引（先 add_objs 写 docstore 再建 retriever），`from_index`（L175）从持久化目录恢复；`retrieve`（L191）走 llama_index 检索管线（retriever→node postprocessor 即 ranker→synthesizer 可选）；`add_objs`（L216）把任意实现 `RAGObject` 协议的对象（interface.py:6，runtime_checkable Protocol，只要 `rag_key()/model_dump_json()` 两个方法）转 node 入库，node.metadata 记下 `obj_mod_name/obj_cls_name`；`_try_reconstruct_obj`（L364）检索命中后经 `metagpt.utils.common.import_class`（L368）按 metadata 动态 importlib 还原对象——存取两端零共享类型，全靠运行时数据驱动。retrievers 层是本子系统最有味道的设计：`retrievers/base.py:11` 的 RAGRetriever 继承 llama_index BaseRetriever，之上定义 Modifiable/Persistable/Queryable/Deletable 四个能力接口，各用 `__subclasshook__ + check_methods`（如 ModifiableRAGRetriever 检查 `"add_nodes"` 方法存在与否，L20-28）实现**结构化鸭子类型**——bm25/chroma/es/faiss 四个具体 retriever 对 metagpt 零 import、纯继承 llama_index 基类，却能 `isinstance` 通过四接口（bm25_retriever.py:38-62 四方法全实现），能力探测不靠继承图谱靠方法签名。工厂层三处模块级单例绑定：`get_rankers = RankerFactory().get_rankers`（factories/ranker.py:80）、`get_retriever = RetrieverFactory().get_retriever`（retriever.py:157）、get_index 同型（index.py）——import 即实例化工厂并绑定方法。

## 3. 外部连接

向上被 exp_pool/manager.py 延迟 import（未装 rag 依赖时真用到才 ImportError）；被 memory/role_zero_memory.py:46-56 与 ext/werewolf/actions/experience_operation.py（Chroma SimpleEngine 直建）消费；web_scraping 动作函数体内延迟 import engines。向下全押 llama_index：node/ retriever/ postprocessor 语义、BM25Retriever 内嵌 docstore.json 持久化（bm25_retriever.py:48-52 storage_context.persist）都来自其抽象。document_store 一支与 rag 平行不相交：`__init__.py:9-11` barrel 只导出 FaissStore——MilvusStore/QdrantStore/LanceStore 不在包出口，import metagpt.document_store 拿不到，必须深导入子模块；LanceStore（lancedb_store.py:14）全仓零生产消费者（唯一使用方在 tests/，requirements.txt 仍钉 lancedb==0.4.0）；chromadb_store.py:11 的 ChromaStore 干脆不继承 BaseStore 也不 import 任何 metagpt 模块——L12 docstring 自述"继承或导入会触发诡异的 Python 异常"，它是绕开集成问题的孤立薄封装，却被 SkillManager 直接依赖。

## 4. 数据流

写路径：业务对象（RoleExperience/Experience/任意 RAGObject）→ SimpleEngine.from_objs → add_objs 转 node（metadata 带 obj_mod_name/obj_cls_name 与 rag_key）→ 按 retriever_config 建索引（BM25 走本地 docstore.json，向量库走各自持久化）→ persist 落盘。读路径：query → retriever（top_k 截断）→ ranker 重排 → 命中 node → _try_reconstruct_obj 动态还原活对象 → 业务侧再做 tag/精确过滤（如 exp_pool 的 query_exps 就是取回后内存过滤）。document_store 老线则是 BaseStore.write/search/add 的朴素 CRUD，服务 faiss 本地向量。

## 5. 设计决策

其一，"配置对象即 DSL"：检索栈的一切组合（哪个 index、哪个 retriever、哪些 ranker、embedding 用谁）都用 pydantic Config 列表声明，SimpleEngine 只做组装——代价是 schema.py 膨胀成 28 个导出类的配置动物园。其二，协议取代基类：RAGObject 用 runtime_checkable Protocol、四能力接口用 __subclasshook__，接入方写 pydantic 模型即自动合规。六处裂缝钉版：`engines/simple.py` 的 `_from_nodes` 在 L266 与 L289 逐字重复定义两次，Python 后者静默覆盖前者，功能无影响但任何改前者的 PR 都会"莫名失效"；`milvus_store.py:85-93` 的 `add` 里 `data = dict()`（L86）在 `for i, id in enumerate(_ids)` 循环（L88-90）内反复覆盖、L93 只 upsert 一次——多 id 批量写只剩最后一条，疑似真 bug；`rag/benchmark/base.py:114` 的 mean_reciprocal_rank 中 `if text in doc:`（L119）的 `text` 未定义（对照同文件 L110 hit_rate 正确写法是 `node.text in doc`），检索结果一旦进入该分支即 NameError，且 L195 的 `__main__` demo 调 `benchmark.SemanticSimilarity(...)` 而方法实名 `semantic_similarity`（L125），demo 整体跑不通——benchmark 子系统属未验证代码；barrel 只导 FaissStore 造成"五实现四隐形"；LanceStore 死代码占着依赖位；ChromaStore 的"诡异异常"注释（chromadb_store.py:12）是没查根因的防御性隔离。

## 6. 新人提示

接 rag 优先从 `from_objs` + 一个 retriever_config 起步（BM25RetrieverConfig 零外部依赖最适合冒烟），对象只需实现 rag_key 与 model_dump_json。排查"检索不到"先看 top_k 截断与后置过滤的顺序——exp_pool 的教训是 DEFAULT_SIMILARITY_TOP_K=2 先截断、tag 过滤后置，命中项可能根本没进结果集。选型别被 barrel 骗：Milvus/Qdrant 要深导入，LanceStore 直接别用。给 SimpleEngine 提交改动前先读 simple.py 全文搜重名方法——_from_nodes 双定义证明这里有过复制粘贴史。benchmark 目录的指标（含 MRR）未经测试验证，引用其数字前先修 L119/L195 两处。document_store 与 rag 二选一时：新代码走 rag，旧 BaseStore 仅在维护 repo_parser 链路时才碰。
