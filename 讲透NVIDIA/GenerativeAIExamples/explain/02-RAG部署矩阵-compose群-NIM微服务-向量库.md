# 02 · RAG 部署矩阵：local_deploy compose 群 + NIM 微服务 ×3 + 向量库后端 ×6

> 覆盖 `RAG/examples/local_deploy/`（docker-compose-nim-ms.yaml / docker-compose-vectordb.yaml）与 `RAG/examples/` 各示例 compose（basic_rag 双实现、advanced_rag 四变体）。

## 一、角色定位

部署矩阵回答：**"同一份 chain-server/playground 代码，如何在云 API、本地 NIM、多种存储后端间切换而不改源码？"** 手段是把基础设施拆进两份**带 profile 的基础 compose**，示例 compose 只定义 chain-server + rag-playground 两应用服务并 `include:` 引入前者。三层：示例层（如 `basic_rag/langchain/docker-compose.yaml`）、NIM 微服务层（`docker-compose-nim-ms.yaml`：推理/嵌入/重排三 GPU 容器）、向量库层（`docker-compose-vectordb.yaml`：pgvector/etcd/minio/milvus/elasticsearch/postgres 六服务）。直接收益是 local_deploy README 的实证命令：`USERID=$(id -u) docker compose --profile local-nim --profile milvus up -d --build` 一条起全套本地栈；去掉 profile 回落云 API 只起 milvus。

## 二、内部结构

**示例层样板**（basic_rag/langchain/docker-compose.yaml，98 行）：`include:` 两份基础 compose（yaml:1-4）。`chain-server` 构建指向**仓库根**（yaml:12 `context: ../../../../`，dockerfile 固定 `RAG/src/chain_server/Dockerfile`），`EXAMPLE_PATH` 既当构建参数（决定 COPY 哪个示例）又当运行环境变量（决定 server 加载哪个示例，yaml:16/23）——**一变量两用，必须一致**。环境变量组（yaml:25-53）：`APP_VECTORSTORE_URL: http://milvus:19530`（yaml:25）、`APP_VECTORSTORE_NAME: milvus`（yaml:27）、`APP_LLM_MODELNAME` 默认 `meta/llama3-70b-instruct`（yaml:29）、`APP_EMBEDDINGS_MODELNAME` 默认 `nvidia/nv-embedqa-e5-v5`（yaml:33）、`APP_TEXTSPLITTER_CHUNKSIZE: 506`（yaml:40）、`NVIDIA_API_KEY`（yaml:42）、`APP_RETRIEVER_TOPK: 4`/`SCORETHRESHOLD: 0.25`（yaml:45-46）、OTEL 端点（yaml:48）。`depends_on` 对 NIM 用 `service_healthy` 且 **`required: false`**（yaml:59-65）——NIM 起了就等健康，没启用就跳过，这就是"云/本地两可"的 compose 实现。`rag-playground` 构建参数 `PLAYGROUND_MODE`（yaml:76），`APP_SERVERURL: http://chain-server` 服务名 DNS（yaml:80）。网络 `nvidia-rag`（yaml:95-97）。

**NIM 微服务层**（docker-compose-nim-ms.yaml，86 行）：

| 服务 | 镜像 | 端口 | 要点 | profiles |
|---|---|---|---|---|
| nemollm-inference | llama3-8b-instruct:1.0.3（yaml:4） | 8000 | 模型缓存卷、shm 20gb、healthcheck `/v1/health/ready` retries 100（yaml:23-27） | local-nim + nemo-retriever（yaml:28） |
| nemollm-embedding | nv-embedqa-e5-v5:1.0.1（yaml:32） | 9080→8000 | `start_period: 10m`（yaml:55，嵌入冷启动慢的诚实设定） | local-nim + nemo-retriever（yaml:56） |
| ranking-ms | nv-rerankqa-mistral-4b-v3:1.0.1（yaml:60） | 1976→8000 | healthcheck 打 `/health`（yaml:71，与前两者不同） | **仅 nemo-retriever**（yaml:82） |

三服务都要 `NGC_API_KEY` 与 `${USERID}` 非 root。ranking 不进 local-nim：README 明示重排是可选件，仅 multi_turn_rag 需要（单独 `up -d ranking-ms` + `export APP_RANKING_SERVERURL="ranking-ms:8000"`）。

**向量库层**（docker-compose-vectordb.yaml，123 行）六服务：`pgvector`（pg16，yaml:2-15，profiles `pgvector`）；`etcd` v3.5.16（milvus 元数据，yaml:18-34）；`minio`（数据 9010/控制台 9011，yaml:36-53）；`milvus-standalone` v2.4.15-**gpu**（`KNOWHERE_GPU_MEM_POOL_SIZE: 2048;4096` yaml:62，GPU device 可配 yaml:83，depends etcd+minio yaml:74-76，**healthcheck 整段被注释** yaml:65-70）；`elasticsearch` 8.12.2（yaml:86-104）与 `postgres` 16.4（yaml:106-118）仅 nemo-retriever profile。关键机制：etcd/minio/milvus 的 profiles 含**空字符串**（yaml:34/53/84）——不带 `--profile` 裸 up 也激活，"默认 milvus"由此实现；pgvector 必须显式 `--profile pgvector`。

**advanced_rag 四变体**（multimodal/multi_turn/query_decomposition/structured_data）：同构三件套（chains.py+prompt.yaml+compose），仅 EXAMPLE_PATH 与附加服务不同（multi_turn 需 ranking-ms；multimodal 自带 vectorstore/custom_pdf_parser.py）。llamaindex 与 langchain 平行目录共用本拓扑。

## 三、外部连接

两把钥匙勿混：`NVIDIA_API_KEY`（chain-server 调云 API，basic_rag yaml:42）与 `NGC_API_KEY`（拉 nvcr.io NIM 镜像）。模型缓存 `MODEL_DIRECTORY` 挂 `/opt/nim/.cache` 多 NIM 共享（README 建议 `~/.cache/model-cache`）。GPU 前提：README 要求至少两块 A100/H100/L40S + NVIDIA Container Toolkit。向量库产品矩阵（docs/vector-database.md:26-27）：LlamaIndex→Milvus/pgvector，LangChain→FAISS/Milvus/pgvector；FAISS 不进 compose（进程内 IndexFlatL2）。观测栈 otel/jaeger 在 `RAG/tools/observability/docker-compose.yaml` 单独起，不在本矩阵。

## 四、数据流

全本地模式依赖图：`rag-playground(8090) → chain-server(8081) → {nemollm-inference:8000, nemollm-embedding:8000, ranking-ms:8000(可选), milvus:19530 → etcd:2379 + minio:9010}`。启动编排：etcd/minio 先起 → milvus 等依赖（无健康条件）→ chain-server 等 NIM healthy（required:false 可跳过）→ playground 等 chain-server started。摄取：上传 → `/tmp-data/uploaded_files` → 切块/嵌入（embedding NIM）→ milvus 写入。查询：generate → 检索 milvus →（可选 rerank）→ inference NIM 流式回。

## 五、设计决策

1. **profile 而非多文件**：三档部署（云/local-nim/nemo-retriever）共用两份 yaml 靠 `--profile` 组合，避免文件矩阵爆炸；空串 profile 兜底默认体验。
2. **`required: false` 优雅降级**：本地 NIM 未配从错误降级为回落云 API。
3. **GPU 细粒度参数化**：每 GPU 服务留 `*_GPU_ID`/`GPU_COUNT` 变量（yaml:20/48/80，vectordb yaml:83），单机多卡可分卡。
4. **healthcheck 差异诚实保留**：inference/embedding 用 `/v1/health/ready`，ranking 用 `/health`，milvus 干脆注释——宁依赖启动顺序不挂不稳探针（vectordb yaml:65-70）。
5. **网络统一 `nvidia-rag`**：跨示例跨工具互访，代价是容器名/端口全局唯一——**同时起两个示例必撞名**。
6. **构建上下文置于仓库根**：chain-server Dockerfile 需同时 COPY 骨架与示例目录，context 必须覆盖两者。

## 六、新人提示

- 首跑：basic_rag/langchain 目录 `docker compose up -d --build`（默认云 LLM+milvus）→ localhost:8090；切 pgvector：`--profile pgvector` + `APP_VECTORSTORE_NAME=pgvector`。
- 切示例先 down：8081/8090 与容器名全示例复用。
- 排障：`docker compose ps`（谁没 healthy）→ `docker logs chain-server`（import_example 失败在此抛 NotImplementedError）→ `docker network inspect nvidia-rag`。
- milvus GPU 版默认占一块卡：`KNOWHERE_GPU_MEM_POOL_SIZE: 2048;4096`（vectordb yaml:62）多服务挤单卡最先爆它。
- 甄别条款：行号锚在 commit `203b0de` 核实；"向量库×6"按 compose 服务计数，**产品级向量库实际三种**（FAISS/Milvus/pgvector，docs/vector-database.md:26-27），elasticsearch/postgres 属 NeMo Retriever 配套；milvus healthcheck 注释段（vectordb yaml:65-70）是上游已知问题非遗漏。
