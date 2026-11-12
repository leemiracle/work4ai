# GenerativeAIExamples 仓库 ONBOARDING（新人导航）

> 图谱基线：2660 节点 / 3328 边 / 15 层 / 15 步 tour，commit `203b0de`（2026-11 快照）。
> 本文档所有行号锚均从源码逐一核实，与 `docs/` 文档站互补：docs 讲"怎么用"，本文讲"为什么长这样、哪里有暗礁"。

---

## 1. 一句话定位与心智模型

NVIDIA GenerativeAIExamples 是一个**示例矩阵仓库，不是单一应用**：RAG 主线（`RAG/`）、行业示例（`industries/`）、社区贡献（`community/`）、NeMo 数据微服务教程（`nemo/`）、微调 notebook（`finetuning/`）与 OSS 教程（`oss_tutorials/`）六大板块共享同一套骨架——**chain-server + playground 前端 + docker-compose 三件套**。

理解本仓的钥匙有三把：

1. **BaseExample 插件协议**（`RAG/src/chain_server/base.py:22`）：实现 `llm_chain`（base.py:29）、`rag_chain`（base.py:44）、`ingest_docs`（base.py:59）三方法即被启动时动态发现（`server.py:228` 用 `set([...]).issubset(set(dir(cls)))` 扫描）——"一个 server 吃下全部示例变体"的机制核心。
2. **compose profile 矩阵**：local_deploy 两份基础 compose 用 profiles（`local-nim`/`nemo-retriever`/`milvus`/`pgvector`）组合 3 NIM 微服务 + 6 后端服务成十余种拓扑，示例 compose 只 `include:` 一行引入（`basic_rag/langchain/docker-compose.yaml:1-4`）。
3. **目录即历史**：0.8.0 大重组把 `RetrievalAugmentedGeneration/` 改为 `RAG/examples/` 按示例分目录（CHANGELOG.md 0.8.0 节）；旧博客/issue 里的旧路径即 0.8.0 前坐标。

根 `README.md` 是总入口；各板块示例深度差异极大（最大 181 文件、最小几个 notebook），以各层 README 为准，勿假设结构均匀。

## 2. 仓库布局与目录语义

按图谱 15 层归并后的语义地图（文件数为图谱统计口径）：

| 目录 | 语义 | 规模 |
|---|---|---|
| `RAG/src/` | 主线源码：chain_server 骨架 + rag_playground 前端 + pandasai 适配器 | 91 文件 |
| `RAG/examples/` | 部署矩阵：basic_rag 双实现 + advanced_rag 四变体 + local_deploy 拓扑 | 72 文件 |
| `RAG/tools/` + `notebooks/` | 评测（合成数据→Ragas）、观测（OTel+Jaeger）、入门 notebook | 60 文件 |
| `industries/` | 能源模拟（181 文件）、医疗、资产全生命周期 | 299 文件 |
| `community/` | 30+ 社区示例：VWS 顾问（162 文件）、数字人安全、流式 ASR、5G 三件套、RAG 纵深五仓 | 688+ 文件 |
| `nemo/` | Evaluator、Data-Designer、retriever-SDG、data-flywheel 数据侧微服务 | 102 文件 |
| `finetuning/` `nemotron/` 等 | 模型侧：LoRA/SFT notebook、bash computer-use agent、49B 深度思考 | 25 文件 |
| `oss_tutorials/` `docs/` | 独立教程与文档站 | 31 文件 |

**新人必读的三份导航文档**：根 `README.md`（板块入口）、`RAG/examples/README.md`（部署矩阵说明）、`community/README.md`（社区收录标准与全量索引）。

两个易踩的目录语义坑：

- **顶层没有 `agent/` 目录**。Agent 示例实际分布在 `industries/`（资产全生命周期、能源编排）与 `community/`（日志多 Agent、5G 运营商 Agent），`nemotron/LLM/bash_computer_use_agent/` 另有从零与 LangGraph 双版本计算机使用 Agent。按目录名找"agent 专区"会扑空。
- **medical-device-training-assistant 是 RAG 模板五件套的分化副本**：compose + prompt.yaml + `app_chain/chains.py` + `src/chain_server/` 全套 + `src/rag_playground/` 与主线同构，但 `src/chain_server/utils.py` 的 md5 与主线不同——**结构同源、内容已分化**，互不能替代。

## 3. 核心架构：chain_server 六端点与工厂层

**服务端**（`RAG/src/chain_server/server.py`，491 行）：`app = FastAPI()`（server.py:44）+ CORS 全开（server.py:47-50）。启动钩子 `import_example()`（server.py:203-238）：从 `RAG/examples/` + 环境变量 `EXAMPLE_PATH`（默认 `basic_rag/llamaindex`，server.py:211）递归扫 `.py` 动态 import，按三方法签名实例化示例类挂 `app.example`。六端点：GET /health（server.py:249）、POST /documents（server.py:270，落盘 `/tmp-data/uploaded_files` 再调 `ingest_docs`，server.py:296-299）、POST /generate（server.py:313）、POST /search（server.py:407）、GET/DELETE /documents（server.py:441/467）。/generate 分发在 server.py:343-348（`use_knowledge_base` 真→rag_chain 假→llm_chain），输出 SSE `data: {ChainResponse}` 帧（server.py:350-378）以 `finish_reason="[DONE]"` 收尾（server.py:369），Milvus 异常单独捕获转友好提示（server.py:380-392）。输入消毒 bleach 全字段 validator（server.py:68-137）。

**工厂层**（`RAG/src/chain_server/utils.py`，715 行，fanOut 37 的全仓最高枢纽之一）：

- `get_llm`（utils.py:366）只支持 `nvidia-ai-endpoints` 引擎；`server_url` 有值走本地 NIM（`ChatNVIDIA(base_url=f"http://{url}/v1")`，utils.py:385-390），为空走 build.nvidia.com 托管（utils.py:394-399）。**这决定了"云/本地"切换只是环境变量的事**。
- `get_embedding_model`（utils.py:407）双引擎：`huggingface` 本地推理 / `nvidia-ai-endpoints`（utils.py:424-440）。
- `get_ranking_model`（utils.py:448）返回 NVIDIARerank，失败时返回 None（utils.py:471）——重排是可选件。
- `create_vectorstore_langchain`（utils.py:288）三分支：faiss（内存 + IndexFlatL2，utils.py:305-306）/ pgvector（utils.py:307-314）/ milvus（GPU_IVF_FLAT 索引 + L2 + nlist/nprobe，utils.py:315-328）。`get_vector_index`（utils.py:220）则是 LlamaIndex 侧入口。
- LlamaIndex 侧的 token 预算由 `LimitRetrievedNodesLength`（utils.py:106）后处理保证，默认 `DEFAULT_MAX_CONTEXT=1500`（utils.py:103）。
- prompt 从示例目录的 `prompt.yaml` 读入（utils.py:190-205，路径拼 `EXAMPLE_PATH`），即**每个示例自带 chat/rag 双模板**。

**示例实现样板**（`RAG/examples/basic_rag/langchain/chains.py`）：`NvidiaAPICatalog(BaseExample)`（chains.py:53）演示了全部五接口——ingest 白名单 `.txt/.pdf/.md`（chains.py:65）、LCEL 三段链 `prompt_template | llm | StrOutputParser()`（chains.py:116/147）、检索时先试 `similarity_score_threshold` 再退普通 retriever（milvus 不支持阈值检索，chains.py:164-167 的 NotImplementedError 回退是常见兼容姿势）、`Context: {context}\n\nQuestion: {query}` 拼装（chains.py:181）。

**可观测性**（`RAG/src/chain_server/tracing.py`）：`ENABLE_TRACING=true` 时挂 OTLP gRPC exporter（tracing.py:38-41），LangChain/LlamaIndex 各有 callback handler（tracing.py:49-52）；端点统一用 `llamaindex_instrumentation_wrapper` 装饰（tracing.py:62）负责从请求头提取 trace context。观测栈 compose 在 `RAG/tools/observability/docker-compose.yaml`（otel-collector 0.102.0 + jaeger all-in-one 1.52 + cassandra 4.0）。

## 4. 前端形态：playground 双模式与双 UI 真相

`RAG/src/rag_playground/` 按 `PLAYGROUND_MODE` 构建参数分 `default` / `speech` 两种容器（`RAG/src/rag_playground/Dockerfile` 末段 `COPY $PLAYGROUND_MODE /app/frontend` + `ENTRYPOINT ["python3.10","-m","frontend"]`；speech 模式额外装 `nvidia-riva-client==2.14.0`）。

**一个常见误解要提前拆掉**："Next.js 前端"只对一半。`default/api.py:29` 的 `APIServer(FastAPI)` 三件事：挂 Gradio 双页（api.py:48-51）、`/`、`/converse`、`/kb` 路由到**预导出的 Next.js 静态页**（api.py:53-63）、`static/` 整体挂载（api.py:65）。`static/_next/` 全是**构建产物**，勿精读；可读源码是 `pages/converse.py`（119 行，`functools.partial(_stream_predict, client)` 流式回调，converse.py:92）与 `pages/kb.py`（115 行，上传/删除文档）。

后端交互全在 `default/chat_client.py` 的 `ChatClient`（chat_client.py:29）：`predict` 流式 POST `/generate`（chat_client.py:75），逐行剥 SSE 前缀 `raw_resp[6:]`（chat_client.py:83，即跳过 `"data: "`）；文档 CRUD 走 `upload_documents`/`delete_documents`/`get_uploaded_documents`（chat_client.py:104/134/153）。`get_uploaded_documents` 对 ConnectionError 只记日志不抛（chat_client.py:169-171），**这是为了 playground 比 chain-server 先起时前端不崩**——排查"知识库列表为空"时先看 chain-server 是否就绪。

## 5. 部署矩阵：compose profile 的组合学

示例部署统一三件套：`docker-compose.yaml` + `prompt.yaml` + `chains.py`。`basic_rag/langchain/docker-compose.yaml` 是样板：

- `include:` 引入 local_deploy 两份基础 compose（yaml:1-4），自己只定义 `chain-server`（8081）与 `rag-playground`（8090）。
- 镜像构建把 context 设到仓库根（yaml:12 `context: ../../../../`），`EXAMPLE_PATH='basic_rag/langchain'` 同时作为构建参数（决定 COPY 哪个示例进镜像）与运行环境变量（决定 server 启动时 import 哪个示例，yaml:16/23）。
- 配置全靠 `APP_*` 环境变量：`APP_VECTORSTORE_NAME=milvus`（yaml:27）、`APP_LLM_MODELNAME`（yaml:29）、`APP_TEXTSPLITTER_CHUNKSIZE: 506`（yaml:40）等；`depends_on` 对 NIM 用 `condition: service_healthy` + `required: false`（yaml:59-65）——**NIM 不在也能起，走云上 API**。
- 全部服务挂同一 `nvidia-rag` 网络（yaml:95-97），跨 compose 互访（playground→chain-server、chain-server→milvus）靠服务名。

**NIM 微服务层**（`docker-compose-nim-ms.yaml`）：`nemollm-inference`（llama3-8b-instruct:1.0.3，8000，shm 20gb，healthcheck 打 `/v1/health/ready`，profiles `local-nim`+`nemo-retriever`，yaml:2-28）；`nemollm-embedding`（nv-embedqa-e5-v5:1.0.1，宿主 9080→容器 8000，start_period 10 分钟，yaml:30-56）；`ranking-ms`（nv-rerankqa-mistral-4b-v3:1.0.1，1976，**仅 nemo-retriever profile**，yaml:58-82）。

**向量库层**（`docker-compose-vectordb.yaml`）共 6 个服务：pgvector（pg16，profiles `pgvector`，yaml:2-15）、etcd v3.5.16（milvus 元数据，yaml:18-34）、minio（milvus 对象存储，控制台 9011/数据 9010，yaml:36-53）、milvus-standalone v2.4.15-**gpu**（`KNOWHERE_GPU_MEM_POOL_SIZE: 2048;4096`，yaml:55-84）、elasticsearch 8.12.2 与 postgres 16.4（仅 nemo-retriever profile，yaml:86-118）。注意 `profiles: ["nemo-retriever","milvus",""]` 里的空串 profile——不带 `--profile` 裸 `docker compose up` 时 etcd/minio/milvus 也会被拉起，这是"默认 milvus"的机制实现。

**支持矩阵**（`docs/vector-database.md:26-27`）：LlamaIndex 支持 Milvus/pgvector，LangChain 支持 FAISS/Milvus/pgvector。FAISS 是进程内方案不进 compose（utils.py:306）。advanced_rag 四变体（multimodal/multi_turn/query_decomposition/structured_data）复用同一骨架，multi_turn 需要 ranking-ms（local_deploy README "Deploy Reranking service" 节）。

## 6. 数据侧：评测链与 NeMo 合成管线

**RAG 质量保障线**（`RAG/tools/evaluation/`）是"合成数据→填答案→评测"三段流水：

1. `synthetic_data_generator/data_generator.py:43` 的 `generate_synthetic_data`：UnstructuredFileLoader 读文档 → RecursiveCharacterTextSplitter（chunk 3000/overlap 100，data_generator.py:46）→ ChatNVIDIA 生成 QA 对（默认 `ai-mixtral-8x7b-instruct`，data_generator.py:47）→ **正则抽取**（`"question":\s*"([^"]*)"`，data_generator.py:74-77）→ 落 JSON 四键（question/ground_truth_answer/ground_truth_context/document，data_generator.py:80-86）。
2. `rag_evaluator/llm_answer_generator.py:58` 的 `generate_answers`：把数据集 PDF 上传到 `/documents`（llm_answer_generator.py:70-72），逐题打 `/generate` 收集 `generated_answer`、打 `/search` 收集 `retrieved_context`（llm_answer_generator.py:94/114），写 eval.json。
3. `rag_evaluator/evaluator.py` 两条评测路：`eval_ragas`（evaluator.py:97，六指标 faithfulness/context_precision/context_relevancy/answer_relevancy/answer_similarity/context_recall，evaluator.py:144-151，再取四指标调和平均为 ragas_score，evaluator.py:154-158）与 `eval_llm_judge`（evaluator.py:165，Likert 1-5 双示例 few-shot）。

**两处源码级缺陷**（judge 路线慎用）：evaluator.py:204 读 `response_body["Explanantion"]`——键名拼写错（prompt 要求的是 "Explanation"，见 evaluator.py:52），LLM 守规矩返回正确键时这里抛 KeyError 被 except 吞掉、rating 记 None（evaluator.py:208-210）；且 evaluator.py:171-179 精心构造的 llm_params 最终没接进 `llm = ChatNVIDIA()`（evaluator.py:181 裸构造），`--judge_llm_model` 参数实际不生效。compose 默认 `--metrics ${METRICS:-ragas}`（`docker-compose.yaml` 的 command 行）绕开了 judge 路线，`compose.env` 里 METRICS 默认 ragas。

**NeMo 数据侧**（`nemo/`）：`retriever-synthetic-data-generation` 是抽象最干净的一条（详见 explain 第 6 篇）——Processor/Filter/Evaluator/QAGenerator/Analyzer 五个 ABC + `scripts/run_pipeline.py` 的 OmegaConf instantiate 组装，SQuAD/BEIR 双格式进出。Evaluator（LLM-as-a-Judge + Live Evaluation compose 带 nemo-postgresql）、NeMo-Data-Designer、data-flywheel（评测→微调→护栏闭环）各自独立成仓内目录。

## 7. 行业与社区示例群：分层导读

**industries/**：
- `energy/simulation-workflow-agent/`（全仓最大，181 文件）：`orchestration_agent` 把查询路由给 `sim_agent`（交互式油藏问答，LangGraph 七节点 `graph/build.py:38`）或 `workflow_agent`（确定性优化循环，LangGraph 六节点 `workflow_graph.py:419`）。模拟器是 OPM Flow（`sim_agent/EXAMPLES.md:3`），算例 SPE10（EXAMPLES.md:97 的 SPE10_TOPLAYER.DATA）。`docker-compose-full.yml` 的 ocr-vllm 跑 **zai-org/GLM-OCR**（compose:32/36，`--max-model-len 32768`；vllm nightly + transformers 源码装，`sim_agent/Dockerfile.ocr:9-10`）——手册摄取走 VLM OCR，本仓少见的非 NVIDIA 模型。Milvus 栈自成版本（etcd v3.5.5 compose:53 / milvus v2.5.4 compose:88）。注意 `sim_agent/scripts/milvus/nvidia_embedding.py` 与 `skills/rag_skill/scripts/nvidia_embedding.py` 是 **md5 相同的双副本**，改一必查二。
- `asset_lifecycle_management_agent/`：Agentic 工作流 + 评测集（llm_judge_evaluator.py 等）+ 绘图子系统（plot_utils.py 618 行）。
- `healthcare/`：medical-device-training-assistant（模板副本见第 2 节）+ agentic-healthcare-front-desk（占位导航）。

**community/**（30+ 示例，四梯队）：
1. 产品级工具：`ai-vws-sizing-advisor/`（162 文件，容量顾问：RAG + 正则解析 `parse_vgpu_query`（chains.py:84）+ `VGPUCalculator`（calculator.py:322）+ Next.js 真源码 `frontend/src/`）。deploy 拉 **blueprint 预构建镜像** 2.1.0（`deploy/compose/docker-compose-rag-server.yaml:17`），且 ingestor 的 build 段被注释（`docker-compose-ingestor-server.yaml:20-23`）——**改 src/ingestor_server 代码默认不生效**，新人最易踩的坑。ingestor 有全套路径安全层（`path_security.py:20` 白名单正则 + `is_relative_to(UPLOAD_ROOT)` 防穿越，path_security.py:76-83）。
2. 多 NIM 流水线：digital-human-security-analyst（Morpheus DFP + MLflow）、fm-asr-streaming-rag（Riva 流式 ASR→Milvus）。
3. 电信三件套：autonomous_5g_slicing_lab、oran-chatbot-multimodal、5g-network-operator-agent。
4. RAG 纵深五仓（streaming_ingest_rag/knowledge_graph_rag/event-driven-rag-cve-analysis/routing-multisource-rag/multimodal_retrieval）+ 20 余个长尾应用（log_analysis_multi_agent_rag 等）。

## 8. 上手路线图与工程坑清单

**60 分钟路线**：
1. （10 min）根 README + CHANGELOG 0.8.0 节 + `docs/architecture.md` 建立地图感。
2. （15 min）精读 `RAG/src/chain_server/server.py` 的 import_example 与 /generate，对照 `base.py` 23 行抽象——这是全仓复用率最高的 500 行。
3. （10 min）读 `basic_rag/langchain/chains.py` + 同目录 compose，理解 EXAMPLE_PATH 双重身份。
4. （10 min）图谱 tour step-4/step-5 走部署矩阵与评测线；`docs/vector-database.md` 确认向量库选择。
5. （15 min）按兴趣深入：Agent 方向读 simulation-workflow-agent 的两张 LangGraph 图；数据方向读 nemo/retriever-SDG；前端方向读 rag_playground 的 api.py+chat_client.py。

**工程坑清单（全部源码核实）**：
- 根 `.pre-commit-config.yaml:5-8` 的 insert-license hook `files: ^RetrievalAugmentedGeneration/` 指向 0.8.0 前旧目录，**当前是死钩子**（black/isort 两钩子只覆盖 `^RAG/`，其余目录不格式化——提 PR 前自己跑 black）。
- compose 网络名统一 `nvidia-rag`；跨示例复用容器时记得同网络。
- `get_llm` 仅支持 `nvidia-ai-endpoints` 引擎（utils.py:376-403），换引擎要改 utils 而不是配置。
- milvus retriever 不支持 `similarity_score_threshold`，chains.py:164-167 的回退分支是故意保留的兼容代码，别"清理"它。
- playground 前端 `static/_next/` 是构建产物；speech 模式需 Riva 凭据。
- `NVIDIA_API_KEY`（云）与 `NGC_API_KEY`（拉 NIM 镜像）是两把不同的钥匙，local_deploy README 与 basic_rag compose（yaml:42）各用各的。
- vws-sizing-advisor 的 ingestor compose 默认不 build 本地代码（见第 7 节）；其 rag-server 是 `--workers 8`（rag-server.yaml:22），并发行为与主线单 worker 不同。
- medical-device-training-assistant 与主线 chain_server 已分化，修 bug 要两处同步评估。

**贡献流向**：主线 `RAG/` 由 NVIDIA 维护（pre-commit 只管它），`community/` 各仓自带 README/CHANGELOG（部分是 git submodule 或迁入仓，见 `.gitmodules`），`industries/` 介于两者之间。跨示例通用改动（如 utils.py 工厂）影响面以图谱 fanIn 计：utils.py 13 / server.py 8 / base.py 6，动前三思。

---

*本 ONBOARDING 由 understand-anything 图谱流水线生成（2026-11）；六篇 explain 深讲见 `../explain/`。*
