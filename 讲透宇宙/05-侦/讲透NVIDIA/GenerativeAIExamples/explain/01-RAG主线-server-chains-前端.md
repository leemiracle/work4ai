# 01 · RAG 主线：chain-server 六端点 + 示例链 + Playground 前端

> 覆盖 `RAG/src/chain_server/`、`RAG/examples/basic_rag/langchain/chains.py`、`RAG/src/rag_playground/`（default 模式）。全仓复用率最高的一条主线，其余示例都是它的变奏。

## 一、角色定位

主线回答：**"一个能跑的 NVIDIA 风格 RAG 应用最少需要哪几个零件？"** 三层：**chain-server**（`server.py` 491 行，FastAPI 服务，按 `EXAMPLE_PATH` 动态加载示例链）；**示例链**（实现 `BaseExample` 三抽象方法的业务类，唯一随示例变化的代码）；**rag-playground**（对话+知识库前端，HTTP/SSE 通信，对后端零耦合）。"骨架固定、业务链可插拔"是本仓最重要的架构决策——`industries/healthcare/medical-device-training-assistant` 整套拷贝此五件套即为明证。

## 二、内部结构

**server.py**：`app = FastAPI()`（server.py:44）+ CORS 全开（server.py:47-50）。启动钩子 `import_example()`（server.py:203）从 `EXAMPLE_DIR="RAG/examples/"`（server.py:52）+ `EXAMPLE_PATH`（默认 `basic_rag/llamaindex`，server.py:211）递归扫 `.py`，`importlib` 动态执行（server.py:220-222），按 `set(["ingest_docs","llm_chain","rag_chain"]).issubset(dir(cls))` 探测类（server.py:228），首个命中者挂 `app.example`；找不到即 `NotImplementedError`（server.py:238）——启动即失败不留悬空服务。

六端点：GET /health（server.py:249）、POST /documents（server.py:270，先落 `/tmp-data/uploaded_files` server.py:287-297，再 `ingest_docs` server.py:299）、POST /generate（server.py:313，SSE 流式）、POST /search（server.py:407）、GET/DELETE /documents（server.py:441/467）。后三者用 `hasattr+callable` 探测可选方法（server.py:423/456/481）——**接口分两级：三抽象方法必须实现，三文档方法按需**。

/generate：取最后一条 user 消息为 query（server.py:329）并从历史删除（server.py:332-335），其余字段打包 llm_settings（server.py:338）；`use_knowledge_base` 真走 `rag_chain` 否则 `llm_chain`（server.py:343-348）。每 token 包成 ChainResponse 的 SSE 帧 `data: {...}\n\n`（server.py:358-365），`finish_reason="[DONE]"` 收尾（server.py:369）。Milvus 异常单独捕获转友好提示（server.py:380-392）。

**base.py**（69 行）：`BaseExample(ABC)`（base.py:22）+ 三抽象方法 `llm_chain`（base.py:29）/`rag_chain`（base.py:44）/`ingest_docs`（base.py:59），全部返回 `Generator[str,None,None]`——**契约规定一切链必须流式**。

**utils.py 工厂层**（715 行，图谱 fanOut 37）：`get_llm`（utils.py:366）`server_url` 有值走本地 NIM `ChatNVIDIA(base_url=f"http://{url}/v1")`（utils.py:385-390），为空走 build.nvidia.com（utils.py:394-399），引擎白名单仅 `nvidia-ai-endpoints`（utils.py:376）。`get_embedding_model` 双引擎 huggingface/nvidia-ai-endpoints（utils.py:424-440）。`get_ranking_model` 失败返回 None（utils.py:471）——重排可选。`create_vectorstore_langchain`（utils.py:288）三分支：faiss 内存 IndexFlatL2（utils.py:305-306）/ pgvector（utils.py:307-314）/ milvus GPU_IVF_FLAT+L2+auto_id（utils.py:315-328）。LlamaIndex 侧 `get_vector_index`（utils.py:220）与 token 截断后处理 `LimitRetrievedNodesLength`（utils.py:106，`DEFAULT_MAX_CONTEXT=1500`，utils.py:103）。prompt 从示例目录 `prompt.yaml` 读（utils.py:190-205）——每示例自带 chat/rag 双模板。

**configuration.py**：`@configclass` 六节配置树（VectorStore 默认 milvus+`http://milvus:19530`，configuration.py:29-33；RetrieverConfig top_k 4+score_threshold 0.25，configuration.py:147-154），字段可被 `APP_*` 环境变量覆盖。

**示例链样板**（basic_rag/langchain/chains.py）：`NvidiaAPICatalog(BaseExample)`（chains.py:53）。ingest 白名单 `.txt/.pdf/.md`（chains.py:65）→ UnstructuredFileLoader → 懒加载 text_splitter（chains.py:76-77）→ `add_documents`（chains.py:83）。双链共用 LCEL 三段 `prompt_template | llm | StrOutputParser()`（chains.py:116/147）；rag_chain 检索先试 `similarity_score_threshold` 再 NotImplementedError 回退普通 retriever（chains.py:156-167，**milvus 不支持阈值检索的兼容分支，别清理**），`Context: {context}\n\nQuestion: {query}` 拼装（chains.py:181），空检索返回提示 iter 不抛错（chains.py:170-174）。

**tracing.py**：`ENABLE_TRACING!=true` 时 propagator 为空、callback 为基类（tracing.py:54-57）——观测零成本降级；`llamaindex_instrumentation_wrapper`（tracing.py:62）从请求头提取并 attach trace context（tracing.py:67-69）。

**playground**（default）：`api.py` 的 `APIServer(FastAPI)`（api.py:29）三件事：挂 Gradio 双页（api.py:48-51）、`/`、`/converse`、`/kb` 路由到预导出 Next.js 静态页（api.py:53-63）、static 整挂载（api.py:65）。`pages/converse.py`（119 行）流式预测用 `functools.partial(_stream_predict, client)`（converse.py:92）；`pages/kb.py:92 upload_file` 上传。**`static/_next/` 下 js 全是构建产物非手写源码**。

**chat_client.py**：`ChatClient`（chat_client.py:29）五操作——`predict` 流式 POST /generate，逐行 `json.loads(raw_resp[6:])` 剥 `data: ` 前缀（chat_client.py:83），结束 `yield None` 哨兵（chat_client.py:102）；`upload_documents`（chat_client.py:104，timeout 600）；`delete_documents`（chat_client.py:134）；`get_uploaded_documents`（chat_client.py:153）对 ConnectionError 只记日志不抛（chat_client.py:169-171）——**chain-server 未起时前端不崩只显示空列表**。

## 三、外部连接

上游：build.nvidia.com（`NVIDIA_API_KEY`）或本地 NIM（`APP_LLM_SERVERURL`）。存储：milvus/pgvector/faiss 三选一。playground↔server：`APP_SERVERURL: http://chain-server`+8081，靠 `nvidia-rag` 网络 DNS。观测：OTLP gRPC（`http://otel-collector:4317`）→ Jaeger。同级消费者：`RAG/tools/evaluation/rag_evaluator/llm_answer_generator.py` 直接打 /documents、/generate、/search——**这套 REST 契约既是前端契约也是评测契约**。

## 四、数据流

1. 上传：kb 页 → multipart POST /documents → server 落盘 → `ingest_docs` → UnstructuredFileLoader 解析 → 切块 → 向量化 → vectorstore.add_documents。
2. 提问：converse 页 → POST /generate 流式 → server 取最后 user 消息 → `rag_chain` 检索 top-4（阈值 0.25）→ 模板填充 → `chain.stream()` 逐 token。
3. 回传：每 token 一帧 `data: {...}\n\n`；chat_client 剥前缀拼 UI；`[DONE]` 收尾。
4. 全程 trace：playground 注入 carrier → server 提取 attach → LangChain callback 出子 span → OTLP 导出。

## 五、设计决策

1. **动态 import 而非注册表**（server.py:214-234）：新示例零注册接入，代价是启动时全目录 exec；类名不重要（server.py:229-233 第一个满足签名者胜出）。
2. **生成器契约统一流式**：server 无需区分处理流式/非流式。
3. **SSE 私有帧格式**：酷似 OpenAI choices 但 `[DONE]` 语义自制（server.py:369）；`raw_resp[6:]` 裸切前缀（chat_client.py:83）——序列化与解析是配对私有协议，改动两端同步。
4. **观测可整体静默**（tracing.py:54-57）：一个环境变量开关，无需条件 import。
5. **CORS 全开 + bleach 全字段消毒**（server.py:47-50/68-137）：示例仓取舍，生产化应收紧。示例间复用靠"复制后分化"而非运行时抽象（medical 五件套即证）。

## 六、新人提示

- 读码顺序：base.py（69 行）→ server.py:203-238 → server.py:313-404 → utils.py:366-489 → chains.py → api.py+chat_client.py。
- **"Next.js 前端"只对一半**：实为"预导出静态页 + Gradio 备胎"双形态；可读源码是 `pages/*.py` 与 `chat_client.py`，`static/_next/` 勿精读。
- 调"知识库为空"：先 GET /health，再查 chat_client.py:169-171 的静默降级。
- 改 prompt 不改代码：编辑示例目录 `prompt.yaml`（compose 已挂载）。
- 甄别条款：全部行号锚在 commit `203b0de` 源码核实；"Next.js 前端"表述已按源码修正；chains.py:164-167 回退是功能分支非死代码。
