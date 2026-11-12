> 标题：向量存储——VectorDBInterface 双实现与 VectorEncoder 精讲 · 源文件：memory/vector_db.py（625 行）· 图谱标签：记忆存储与检索子系统 / 一级枢纽（文件级+VectorDBInterface 类级双枢纽）

## 角色定位

Jev-Mem 的语义定位层：文本变向量、向量存起来、按相似度找回来。图遍历需要起点（anchor）——起点从"问题向量和记忆向量谁最像"来。`trg_memory` 每次 `add_event` 双写图+向量库（trg_memory.py:202-213），每次 `query` 先 `vector_db.search` 拿锚点（trg_memory.py:260-263）——本文件就是那条"语义雷达"。

它还兼任编码器门面：`VectorEncoder`（vector_db.py:534）统一封装 OpenAI embedding 与本地 SentenceTransformer 双通道，工厂 `create_vector_db`（vector_db.py:601）做后端自动降级——FAISS 缺失退 NumPy 暴力搜索。整文件是"接口+双实现+工厂"三层，职责边界干净：不知道图、不知道 LLM、不知道业务。

## 内部结构

**守卫与枚举**：faiss 导入守卫（vector_db.py:23-28）、sentence_transformers 守卫（vector_db.py:30-35）；`IndexType`（vector_db.py:37-41，HOT/WARM/COLD 温度分层）。

**`VectorEntry`**（vector_db.py:43-81）：vector_id/vector/metadata/index_type/access_count/last_accessed。后两字段是访问埋点：每次命中自增/刷新（vector_db.py:263-264、275-276）。

**`VectorDBInterface`**（vector_db.py:83-132）九个抽象方法：add_vector（vector_db.py:87）、add_vectors 批量（vector_db.py:93）、search（vector_db.py:98，返回 (id, similarity, metadata) 三元组），其余 get_vector/update_vector/delete_vector/exists/size/clear 见 vector_db.py:104-130。

**`FAISSVectorDB`**（vector_db.py:134-389）：`__init__`（vector_db.py:137-171）按 index_type 建三种索引——flat 精确 L2（vector_db.py:159）、ivf 倒排（vector_db.py:160-163）、hnsw（vector_db.py:164-165）。双映射 `id_to_index`/`index_to_id`（vector_db.py:150-151）弥合"FAISS 连续 int 行号 vs 业务 uuid"。add_vector（vector_db.py:173）、add_vectors 批灌（vector_db.py:197）、search（vector_db.py:235，vector_db.py:266 处 `1/(1+dist)` 换算 L2→相似度）、update_vector/delete_vector（vector_db.py:279、295）、`_rebuild_index`（vector_db.py:323，reset 后全量重灌）、save/load（vector_db.py:341/363，index.faiss+metadata.json）。

**`NumpyVectorDB`**（vector_db.py:391-532）：纯字典+暴力 cosine（vector_db.py:429-462），save（vector_db.py:504）单 JSON。

**`VectorEncoder`**（vector_db.py:534-599）：`__init__`（vector_db.py:537）先试 OpenAI（vector_db.py:546-556，失败降级打日志），降级后模型名是 `text-embedding-*` 则回退 `all-MiniLM-L6-v2`（vector_db.py:563-565）；本地通道用 `local_model_device()` 选设备（vector_db.py:567）。encode_batch（vector_db.py:581）、encode_with_timeout 超时护栏（vector_db.py:595）。

**`create_vector_db`**（vector_db.py:601-625）：auto 时 FAISS 可用选 faiss 否则 numpy（vector_db.py:614-615），显式要 faiss 但不可用 warning+降级（vector_db.py:617-620）。

## 外部连接

import：stdlib+numpy+两个守卫依赖+项目内仅 `.local_device.local_model_device`（vector_db.py:19）；`.openai_encoder.OpenAIVectorEncoder` 惰性导入（vector_db.py:549，在 OpenAI 分支内），保证无 API key 环境不炸。被引（grep 实证 9 文件）：`trg_memory.py`（接口+Encoder+工厂全拉，vector_db.py:32-36）、`memory_builder.py`、`jev_mem/demo.py`、`longmemeval.py`、`evaluate_anchor_recall.py`、三测试。图谱双枢纽。注意 `query_engine.py` 不直接 import 它——查询侧经 trg.encoder 间接使用，层次刻意收窄在 trg_memory 一处。

## 数据流

入库（add_event 驱动）：富化文本 `"Mel adopted a Labrador. Keywords: adopted..."` →`VectorEncoder.encode`→MiniLM 返回 (1,384) 或 OpenAI 返回 (1,1536)→`add_vector(vector_id=节点uuid, vector, metadata={'timestamp':iso,'keywords':[...]})`（vector_db.py:173）→FAISS index.add 与双映射登记（vector_db.py:188-193）。

查询（query 驱动）：问题富化→编码→`search(query_vector, k=15)`（vector_db.py:235）：FAISS 返回 distances+indices→`index_to_id` 翻回 uuid（vector_db.py:251）→metadata 后过滤（vector_db.py:255-261）→命中条目 access_count+=1（vector_db.py:263-264）→`1/(1+dist)` 换算（vector_db.py:266）→返回三元组列表。上游拿 uuid 去 graph_db 换节点，相似度进 QueryContext.metadata 的 search_scores。

持久化：`save(dir)`（vector_db.py:341）写 index.faiss（vector_db.py:350）+metadata.json（vector_db.py:352-361，entries 全量+双映射+next_index+dimension）；`load`（vector_db.py:363）读回时 387 行把 JSON 字符串键转回 int。NumPy 后端一个 JSON 打天下（vector_db.py:510-516）。

## 设计决策

**双实现+工厂自动降级**（vector_db.py:601-625）是环境适应性核心：没装 faiss-cpu 也能跑，装了无痛升级。代价是两实现的相似度语义**不同**——FAISS 是 L2 换算的 `1/(1+dist)`（vector_db.py:266，MiniLM 向量未归一化时 L2 与 cosine 不等价），NumPy 是纯 cosine（vector_db.py:454）。跨后端比较分数或调阈值时要意识到这点。

**删除/更新=全量重建**（vector_db.py:323-339）是最重取舍：IndexFlat 不支持删除，delete/update 都走 `_rebuild_index` 的 O(N) 重灌。对"构建一次、查询多次、几乎不删"的 benchmark 够用；对在线记忆系统是性能悬崖。vector_db.py:285 的 warning "Vector update requires index rebuild" 是诚实自白。

**metadata 后过滤而非索引内过滤**（vector_db.py:255-261）：实现简单、对索引零侵入，但命中率高时召回缩水；目前上游 search 基本不传 filter，能力处于"接口在、没用上"状态。**access_count/last_accessed 与 HOT/WARM/COLD**（vector_db.py:37-52）：为温度分层存储预留的观测数据，search/get 自动埋点（vector_db.py:263-264），但无代码据此迁移条目——和 graph_db 的 LinkStatus 一样是"为论文机制预留的地基"。**编码器降级链**（vector_db.py:546-569）：OpenAI→异常→SentenceTransformer 且模型名自动纠正（vector_db.py:563-565），保证无网环境不炸；但 384 与 1536 维向量**不互通**，换模型=换记忆库（缓存目录因此加 `_openai` 后缀分开）。

## 新人提示

先读 `create_vector_db`（vector_db.py:601）与 `VectorEncoder.__init__`（vector_db.py:537），五分钟搞清实际跑哪个后端与编码器——日志判据见 vector_db.py:552、569。再读 FAISSVectorDB.search（vector_db.py:235）与 `_rebuild_index`（vector_db.py:323），前者热路径，后者解释删改为何贵。

四个常见误解：以为 search 返回 cosine——FAISS 路径是 `1/(1+L2)`（vector_db.py:266），与 NumPy 路径的 cosine（vector_db.py:454）量纲语义不同，调阈值别混；以为重复 add_vectors 能覆盖——已存在的 vector_id 直接跳过（vector_db.py:176-177），更新必须走 update_vector 触发重建；以为顶部 import 的 pickle（vector_db.py:14）用于持久化——save 用 faiss 格式+JSON，pickle 是死导入；以为 encode 单文本返回一维——返回 (1,d)，上游到处出现的 `if len(embedding.shape)==2` 拆包（trg_memory.py:197）就是在拆这层包装。
