# 05 · community/ai-vws-sizing-advisor：AI vWS 容量顾问（RAG + 解析器 + 前端 + ingestor）

> 覆盖 `community/ai-vws-sizing-advisor/`（162 文件，社区最大单仓）：`src/` 后端、`src/ingestor_server/` 摄取服务、`frontend/src/` Next.js 源码、`deploy/compose/` 十余分体 compose。README:23 定位："RAG-powered tool that helps you determine the optimal NVIDIA vGPU sizing configuration for AI workloads"。

## 一、角色定位

回答的问题：**"用户一句'50 并发跑 Llama-3-70B 做 RAG，FP8'，系统怎么给出可执行的 vGPU/显存/内存配置？"** 选择三引擎混合而非纯 RAG：**RAG 引擎**（`src/chains.py` 2299 行，从 vGPU 官方文档检索佐证与引用）、**确定性引擎**（`parse_vgpu_query` chains.py:84 + `VGPUCalculator` calculator.py:322，正则抽参 + 查表算显存吞吐）、**交互引擎**（`apply_configuration.py` 1101 行 + configuration_wizard，向导收集/生成配置/验证部署）。粘合剂是主线基因：`src/base.py:24` 的 `BaseExample` 与主线同构，`UnstructuredRAG(BaseExample)`（chains.py:299）实现全接口。README:13 直链 NVIDIA 官方 Sizing Advisor 文档站——社区示例向产品级工具演进的标本。

## 二、内部结构

**chains.py 三段式**：
- `parse_vgpu_query`（chains.py:84-183）纯正则抽六槽位：Workload（RAG/Inference，chains.py:96-99）、Model（先 HF `org/model-name` 格式 chains.py:102-104，再 VALID_MODELS 弹性匹配，再 small/medium/large/extra 关键词兜底 chains.py:113-125）、Concurrent Users（`(\d+)\s*(?:concurrent...)?\s*users?` chains.py:127-128）、Precision（fp16/fp8/fp4/int8 chains.py:131-142）、Prompt/Response Size（chains.py:147-155）。默认 FP8/Llama-3-8B/1 用户/1024/256（chains.py:158-170）——**宁用保守默认不反问**。
- `StructuredResponse`（chains.py:186-267）：schema 即函数调用规范——`vgpu_profile` enum 白名单 L4-12Q…DC-96Q（chains.py:210-214），`gpu_memory_size` description 内嵌公式 "model_params_billions × bytes_per_param × 1.2. FP16=2 bytes, INT8=1 byte"（chains.py:224），八字段全 required（chains.py:256）。**领域知识写进 schema**，结构化输出天然合法。
- 模块级装配（chains.py:272-288）：embedder/ranker/query_rewriter_llm import 时初始化；`VECTOR_DB_TOPK` 默认 40（chains.py:279，主线是 4——先宽召回再 rerank 压）；`get_streaming_filter_think_parser()`（chains.py:288）。

**think 标签流式过滤**（`utils.py` 1430 行，fanOut 62 全仓第一）：`streaming_filter_think`（utils.py:897-1033）是 136 行状态机生成器——完整 `<think>`/`</think>`（utils.py:909-910）与**跨 chunk 部分标签**（`END_TAG_PARTS=["</","think",">"]` utils.py:914）都处理；`FILTER_THINK_TOKENS` 默认 true（utils.py:1049）。存在原因：默认模型 `nvidia/llama-3.3-nemotron-super-49b-v1` 是推理模型，裸流会把思考链吐给用户。utils.py 其余是主线 utils 增强版：LLM/embedding/ranker 工厂、Milvus 集合管理、NIM URL 消毒、全服务健康检查。

**calculator.py**（1390 行）：`VGPUCalculator`（calculator.py:322）三表——GPU 表从 `gpu_specs.json` **强制加载**（calculator.py:337，缺文件 CRITICAL 日志+RuntimeError 不降级 calculator.py:364-366）；模型表 = 硬编码默认（Llama-3 系/Mistral-7B/Falcon 系/Qwen-14B/`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8` 等 calculator.py:367-378）+ **HF 动态拉 top 15 热门模型**（calculator.py:380-397，失败仅 warning）；embedding/reranker 规格表硬编码。`fetch_model_config_from_hf`（calculator.py:23）+ `estimate_model_spec_from_params`（calculator.py:70）保证没见过的模型也能按参数量估算。

**server.py**（1819 行）：主线 server 超集——保留四主端点，新增健康聚合（`HealthResponse` 带数据库/NIM/存储三类，server.py:600-622）、静态 vGPU 引用（server.py:743）、citations 组装（server.py:793）、`/api/download-citation`（server.py:1785）；`error_response_generator`（server.py:637）统一错误为 SSE 帧。

**ingestor_server**：与 rag-server 分体的蓝图式摄取——`NVIngestIngestor(BaseIngestor)`（main.py:67）走 **nv-ingest 微服务**（deploy 里 `nvcr.io/nvidia/nemo-microservices/nv-ingest:25.4.1`）解析；`_put_content_to_minio`（main.py:416）把图表 base64 转存 MinIO；`_prepare_langchain_documents`（main.py:342）转 LangChain 文档入 Milvus；redis-stack 任务队列，上传异步可轮询（server.py:385 get_task_status）。**安全层独立成章**（`path_security.py`）：`UPLOAD_ROOT` 禁锢（path_security.py:17）、集合名白名单正则（path_security.py:20）、`safe_collection_dir` 的 `is_relative_to(UPLOAD_ROOT)` 防穿越双保险（path_security.py:76-83）、`validate_safe_filename` 单段消毒（path_security.py:43-69）——多集合多租户的路径攻击面被系统性封堵。

**frontend**（真源码）：`api.ts` 的 `API_CONFIG`（api.ts:18）把后端分 VDB 簇（8082）与 CHAT 簇（8081）；`buildQueryUrl` 自动附 `vdb_endpoint`（api.ts:52）；`AppContext.tsx` 的 `AppProvider`/`useApp`（AppContext.tsx:46/87）管 collections/documents/chatMessages/loading/error 五态；`types/chat.ts` 的 `Citation`（chat.ts:16）/`StreamState`（chat.ts:31）/`GenerateRequest`（chat.ts:43）——**引用是一等公民类型**，回答必须可溯源到 vGPU 文档页。`app/api/` 目录是 BFF 薄层。

**deploy/compose/**（十余分体）：rag-server / ingestor-server / vectordb / nims / guardrails / observability / bootstrap + 四 env profile。`x-model-config` 锚点集中声明模型（`llm-model: nvidia/llama-3.3-nemotron-super-49b-v1`、`embedding-model: nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1`，rag-server.yaml:6-9）。

## 三、外部连接

**blueprint 血缘**：rag-server 与 ingestor-server 镜像都是 `nvcr.io/nvidia/blueprint/*:${TAG:-2.1.0}`（rag-server.yaml:17、ingestor-server.yaml:14）。**关键不对称**：rag-server 保留 `build: context: ../../src`（rag-server.yaml:18-21，`--workers 8`）；**ingestor-server 的 build 段整段被注释**（ingestor-server.yaml:20-23）——默认永远拉预构建镜像，改 `src/ingestor_server/` 源码不生效，自测需解开注释重建。NIM 生态全家：llm/embedding/rerank NIM + nv-ingest + Guardrails + MinIO + Milvus + redis-stack。HuggingFace：动态模型表（calculator.py:380-397）。语料：`vgpu_docs/` 官方文档。主线基因：base.py/configuration_wizard/tracing/prompt.yaml 全同构。

## 四、数据流

**问答线**：自然语言 → `parse_vgpu_query` 抽六槽位 → RAG 链：query rewriter 改写（chains.py:277）→ Milvus 宽召回 top-40 → reranker 压排 → nemotron-super-49b 生成 → `streaming_filter_think` 过滤（utils.py:897）→ StructuredResponse + citations 组装 → 前端 StreamState 增量渲染。**确定性路径并行**：calculator 按显存公式查表给 profile——RAG 负责解释与引用，calculator 负责数字正确。

**摄取线**：上传 → ingestor（8082）路径消毒 → redis 入队 → nv-ingest 解析 → 图表转 MinIO、文本嵌入 → Milvus `multimodal_data` 集合（GPU 索引+hybrid 默认开）→ 任务状态轮询。

**向导线**：Wizard 逐项收集 → `apply_configuration.py` 生成 → `/api/test-configuration` 验证 → `/api/download-citation` 导出。

## 五、设计决策

1. **三引擎而非纯 RAG**：显存公式是可验证数学（查表），文档语义是 RAG 的解释引用；正则先行让参数明确的查询零 LLM 成本。
2. **schema 即提示词**（chains.py:186-267）：enum 白名单 + 计算公式内嵌 description，合法性与领域正确性一并约束。
3. **摄取与服务分体**：摄取重 IO（nv-ingest/MinIO/队列）、问答重 GPU（NIM），独立扩缩；代价是部署面翻倍。
4. **blueprint 镜像优先、本地构建留门（不对称）**：rag-server 留 build、ingestor 注释 build——稳定优先但可介入；这种不对称是否有意值得向上游求证。
5. **think 过滤默认开**（utils.py:1049）：推理模型进 RAG 前端的必备件；136 行状态机处理跨 chunk 标签（utils.py:897-1033）说明作者踩过"标签切在 chunk 边界"的坑。
6. **路径安全独立模块**：白名单正则 + is_relative_to 双保险是教科书式封堵。

## 六、新人提示

- 阅读顺序：README → chains.py:84-267 → calculator.py:322-440 → utils.py:897-1055 → rag-server.yaml → frontend api.ts/AppContext.tsx。
- **最大的坑**：改 ingestor 代码不生效（build 被注释 ingestor-server.yaml:20-23）；`TAG` 变量决定 blueprint 版本，升级=改 TAG 非改代码。
- `src/vgpu_validation.py` 是 0 字节空文件、`vgpu_calculator.py` 仅 39 行薄壳——真逻辑在 `calculator.py`，勿被文件名误导。
- `--workers 8`（rag-server.yaml:22）意味着模块级全局态每 worker 一份，Milvus 连接与首 token 延迟按 8 估。
- 回答慢先降 `VECTOR_DB_TOPK=40`（chains.py:279）再考虑换模型。
- 甄别条款：行号锚在 commit `203b0de` 核实；"前端 Next.js"在本仓指 `frontend/src/` 真源码（区别于主线 playground 的 `_next` 构建产物）；ingestor build 注释、空文件、blueprint 血缘均为盘上实证。
