# 09 RAG 检索线：camel/retrievers/ 与 camel/embeddings/

## 1. 角色定位

这对姊妹包构成 camel 的 RAG 基座：retrievers 管"文档进来、相关片段出去"，embeddings 管"文本变向量"。检索侧五个实现分三类——BM25Retriever（纯词频）、VectorRetriever（向量，配 BaseVectorStorage）、HybridRetriever（前两者 RRF 融合），外加 cohere/jina 两个 rerank 检索器；AutoRetriever 是唯一的高级门面（自动分集合名、建库、查库一条龙，GAIA 基准的 DefaultGAIARetriever 就是它的子类，camel/benchmarks/gaia.py:69）。嵌入侧 9 个实现共享 `BaseEmbedding`（camel/embeddings/base.py:22，`Generic[T]` 泛型——T 可以是 str 也可以是 PIL Image），分本地（SentenceTransformerEncoder/VisionLanguageEmbedding）与远程 API 两档。两条线在 VectorRetriever 处交汇：检索器持有嵌入模型实例，存储层的 vector_dim 由 `get_output_dim()` 决定。

## 2. 内部结构

**BaseRetriever**（camel/retrievers/base.py:61）只有两个方法且默认实现是模块级"未实现"哨兵函数（:70-71 赋 `process`/`query` 类属性，未覆写即抛 NotImplementedError 带类名提示）——比纯 @abstractmethod 更松的契约。

**BM25Retriever**（bm25_retriever.py:23）最薄：process 用 UnstructuredIO 解析+分块后 `str(chunk).split(" ")` 建语料（:81），query 同样 `query.split(" ")`（:117）交给 rank_bm25 打分、numpy argpartition 取 top_k。rank_bm25 是可选依赖（:42 `@dependencies_required('rank_bm25')` 装饰器守门+函数体内 import）。

**VectorRetriever**（vector_retriever.py:36）是主力：process 把 content 分四路归一化为 Element 列表（:113-141 的 if/elif 链：Element 直收 / IOBase 走 parse_bytes / str 判 URL 或本地路径走 parse_file_or_url / 纯文本 create_element_from_text），可选 chunker 分块后逐条 embed 写入向量库；query 把查询向量交 storage 查询、按 similarity threshold 过滤。

**HybridRetriever** 组合双路：process 同时喂 vr 与 bm25（hybrid_retrival.py:36-37、:54-55），`_sort_rrf_scores`（:57）按 Reciprocal Rank Fusion 融合两路排名（docstring 附 Medium 与 Colab 出处链接）。

**AutoRetriever**（auto_retriever.py:41）是零配置门面：默认 QdrantStorage+OpenAIEmbedding（:63-64），支持 Milvus/TiDB（:82-114）。核心是 `_collection_name_generator`（:120）：文件路径→`文件名前10字符_目录md5前6位`（:146-151），URL/文本→`内容尾10字符_md5前6位`（:154-156）；Milvus 模式补下划线前缀满足首字符约束（:160-164）。`run_vector_retriever` 对每个 content 生成集合名，`vector_count == 0` 才 clear+重建，否则直接复用（:232-245）。

**embeddings 包**：`BaseEmbedding.embed` 是 embed_list 的单条语法糖（camel/embeddings/base.py:58）。维度获取分三派：openai_embedding 从 `EmbeddingModelType` 枚举静态查表返回 `self.output_dim`（openai_embedding.py:106-112，零调用成本）；SentenceTransformerEncoder 读本地模型属性（sentence_transformers_embeddings.py:72）；**OpenAICompatibleEmbedding/TogetherEmbedding 是懒探测**——`output_dim is None` 时 `self.embed_list(["test"])` 真发一次 API（openai_compatible_embedding.py:98-99、together_embedding.py:128）。JinaEmbedding 是全包唯一无官方 SDK 的实现：`requests.post('https://api.jina.ai/v1/embeddings', timeout=180)` 直调（jina_embedding.py:82、:153-154），图像输入 base64 上送。VisionLanguageEmbedding（vlm_embedding.py:28）走 HF AutoModel 本地推理（默认 CLIP ViT-B/32），是 T=Image 的多模态档。

## 3. 外部连接

- **storages.vectordb_storages**：VectorRetriever/AutoRetriever 的持久层（Qdrant/Milvus/TiDB），集合的增删查全在 storage 侧——嵌入模型只供向量。
- **loaders.UnstructuredIO**：全 retrievers 包的解析/分块引擎（bm25:49、vector_retriever 的 uio 成员），chunker 体系另有 UnstructuredIOChunker。
- **types.enums.EmbeddingModelType**：openai/azure 两实现共用其 TEXT_EMBEDDING_ADA_2 特判（openai_embedding.py:91 / azure_embedding.py:97，旧模型不支持 dimensions 参数走不同分支——改动请求逻辑两处须同步）。
- **benchmarks/gaia.py**：DefaultGAIARetriever(AutoRetriever) 是检索线在基准侧的唯一继承者；memories/AgentMemory 体系另用 embeddings 而不经 retrievers。
- **导入风格分裂**：jina/vlm 经 barrel 取 `from camel.embeddings import BaseEmbedding`，其余实现直连 `.base`（图谱钉版的包内循环隐患）。

## 4. 数据流

AutoRetriever 一次调用的完整路径：`run_vector_retriever(query, contents)` → 每个 content 生成集合名 → 实例化 storage（此时即触发 `get_output_dim()`，auto_retriever.py:89/103/110——懒探测型嵌入模型在这一步就产生付费调用）→ 空库则 VectorRetriever.process（解析→分块→embed_list 批量嵌入→storage.add）→ query（query embed → storage.query → 阈值过滤）→ 多 content 结果合并、有分/无分分组排序（:257-272）→ 默认只回 `{"Original Query", "Retrieved Context"}` 文本清单。注意任何单个 content 失败都会把整批拖死（:249-252 的 except 直接 raise RuntimeError）。

## 5. 设计决策

1. **BM25 的朴素分词是刻意简化**：`split(" ")` 对中文/日文等无空格语言基本失效（整句成单 token，词频匹配退化为整串相等）；HybridRetriever 复用同一路，中文场景混合检索会退化为纯向量路——文档没提醒，选型时要自查语料形态。
2. **路径哈希集合名=内容变更不失效的缓存**：集合名由"路径+目录 md5"生成（:146），同路径文件内容更新后 `vector_count != 0` 仍走复用分支（:232）——旧向量继续被检索。想让新内容生效须手动 clear 集合或换文件名；这是"自动"的代价。
3. **get_output_dim 的三种语义**：静态查表（openai）/本地属性（st）/付费探测（compatible+together）在同一个抽象方法下并存——调用方（storage 构造）无从分辨，CI 里"只是初始化"的代码可能悄悄花钱。
4. **BaseRetriever 的哨兵函数风格**：不用 @abstractmethod 而用模块级 `_query_unimplemented` 赋类属性，好处是错误信息自带类名与"缺哪个方法"提示，坏处是 IDE/类型检查器不报未覆写。
5. **RRF 融合而非分数线性加权**：_sort_rrf_scores 用排名倒数融合（rank_smoothing_factor 平滑），规避 BM25 分数与 cosine 相似度不同量纲不可直接加权的问题——教科书式正确选择。

## 6. 新人提示

- **文件名勘误钉版**：`hybrid_retrival.py` 拼写错误（retrival→retrieval），类名 HybridRetriever 正常；全仓按错误文件名 import，改名属破坏性变更，grep 时两个拼写都要试。
- **VectorRetriever.process 有 NameError 地雷**：:113-141 的 if/elif/elif 链无 else，content 既非 Element/IOBase/str 时 `elements` 未绑定，:144 `if not elements` 直接 NameError（图谱钉版潜在 bug）——传参类型错时报错离根因远。
- **中文 RAG 别用 BM25 档**：需要混合检索时确认 bm25 路 token 化有效性，或外挂 jieba 分词预处理后再喂 process。
- **本地开发首选 Qdrant path 模式 + SentenceTransformerEncoder**：`AutoRetriever(vector_storage_local_path="./qdrant_db", embedding_model=SentenceTransformerEncoder(...))` 全链零 API 依赖零费用。
- **集合名截断可能撞车**：文件名前 10 字符+目录 6 位 md5，同目录下前 10 字符相同的不同文件（长中文文件名场景）理论可碰撞，碰撞即数据混库——重要语料用显式 collection_name 更稳。