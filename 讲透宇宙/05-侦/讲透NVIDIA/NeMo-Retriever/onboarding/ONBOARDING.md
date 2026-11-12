# NeMo-Retriever ONBOARDING（图谱 commit 3a4162cf · 1702 节点/2834 边/16 层）

> 路径约定：未特别注明的路径均相对 `nemo_retriever/src/nemo_retriever/`；`skills/`、`examples/`、`retrieval-bench/`、`agent_eval/` 为仓库根目录。

## 1. 定位：RAG 全家微服务（原 nv-ingest）

NeMo-Retriever 是 NVIDIA 的多模态文档 RAG 全家桶：抽取（PDF/Office/HTML/音视频/图像 19 种文件类型）→ 嵌入 → 重排 → 入库 LanceDB → 查询/Agentic 检索一条链全包。根 README.md 明示它由 nv-ingest 改名而来；`nemo_retriever/README.md`（875 行）是最重要的上手文档。三种产品形态：**库模式**（`ingestor/core.py:43` `create_ingestor` 按 `run_mode` 三分发：`service`→ServiceIngestor 走 HTTP，`inprocess/batch`→GraphIngestor 本地图，见 `ingestor/core.py:58,70`）、**服务模式**（`service/app.py:252` `create_app` FastAPI 工厂）、**评测模式**（harness+retrieval-bench 双轨）。16 层图谱：L01-L02 治理与 CI，L03-L08 六条核心代码线，L09-L16 服务、入口、评测与部署。

## 2. 算子体系：一切皆 AbstractOperator

全仓最重要的心智模型在 `operators/abstract_operator.py:15`——所有算子继承 `AbstractOperator(ABC)`，强制三段式 `preprocess`/`process`/`postprocess`（`abstract_operator.py:23-30`），`run()` 顺序串联（`abstract_operator.py:32-36`），`__call__` 委托 `run()` 使算子可作 Ray `map_batches` 的 callable class（`abstract_operator.py:38-40`）。构造 kwargs 存 `_graph_init_kwargs`（`abstract_operator.py:18-21`），`get_constructor_kwargs()`（`:42-57`）用 `inspect.signature` 补齐默认值——执行器侧"worker 懒构造"的关键：图只传类名+kwargs，重模型在 worker 上才实例化。CPU/GPU 声明是两个纯 mixin 标记类：`operators/cpu_operator.py:8` 与 `operators/gpu_operator.py:8`，执行器用 `isinstance` 决定 GPU 份额调度（`graph/executor.py:571`）。第三块基石 `operators/operator_archetype.py:26` `ArchetypeOperator`：图里放原型算子，`resolve_operator_class()`（`:50-67`）按探测 GPU 数挑变体，`_resolve_delegate()`（`:93-111`）带缓存键避免重复实例化。多模态共享逻辑在 `common/modality/`（30 节点 12 子包）：PDF 转换（`common/modality/convert/to_pdf.py:47`）、HTML 转 markdown（`common/modality/html/convert.py:69`）、token 切分（`common/modality/txt/split.py:45`）、ffmpeg 媒体接口（`common/modality/audio/media_interface.py:243`）、caption 画像（`common/modality/caption/model_profiles.py:51`）、表格重建（`common/modality/table_and_chart.py:408`）——`operators/extract/` 下每个模态算子都是这三件的组合。

## 3. 管线编排：graph + graph_ops 两层

`graph/pipeline_graph.py` 定义 Node/Graph：`Node`（`:30`）包算子持 children，`Graph`（`:84`）持 roots 深度优先执行。`>>` 三处实现：`AbstractOperator.__rshift__`（`operators/abstract_operator.py:59-70`）自动包 Node，`Node.__rshift__`（`graph/pipeline_graph.py:64-77`）返回新 Graph，`Graph.__rshift__`（`:132-149`）向 tail 追加。双执行器（`graph/executor.py` 893 行）：`InprocessExecutor`（`:408`）单线程 pandas 顺序跑，`_linearize`（`executor.py:422-439`）拒绝多根/fan-out；`RayDataExecutor`（`:509`）把每个 Node 折成 `map_batches` stage（`executor.py:883-891`），五类调度智能——GPU 份额启发式（`:567-587`，基线 `OCR_GPUS_PER_ACTOR=0.1` 见 `common/ray_resource_hueristics.py:42`）、vLLM 类 actor 批放大 64（`:826-829`，常量 `common/ray_resource_hueristics.py:36`）、`REQUIRES_GLOBAL_BATCH` 自连接算子强制单块（`:834-853`）、Ray 2.49 并发默认 1（`:816-819`）、Arrow↔pandas 偏移适配器（`:860-877`）。管线级算子 `operators/graph_ops/`（14 个）：`react_agent_operator.py:80`、`rrf_aggregator_operator.py:18`、`selection_agent_operator.py:44`、`subquery_operator.py:77` 等——与模态算子同构，只是作用在整条管线粒度。

## 4. 查询与 Agentic 检索：双模式

经典查询走 `query/workflow.py`：`ResolvedQueryPlan`（`:94`）把 QueryRequest 一次解析成可复用配置（`resolve_query_plan` `:139`），可反复 `create_retriever()`。Agentic 是上层形态，入口双算子：`query/agentic.py:110` `AgenticQueryInputOperator` 把输入 DataFrame 归一到 `query_id`+`query_text` 两列（`agentic.py:119-131`）；`:138` `AgenticSelectionOutputOperator` 把 agent 选择结果按 rank 组装成 hit 列表（`agentic.py:147-166`）。核心配置 `AgenticRetrievalConfig`（`:174`）冻结 dataclass，`__post_init__`（`agentic.py:225`）校验 `llm_backend` 两值集（`agentic.py:60-61`）与 `invoke_url` 互斥。Agent 本体在私有库 `_agentic/nemo_agent/`（30 节点）：`loop.py:178` `_BaseAgentLoop` 通用循环（工具异常分类 `:69`），`agent.py:72` `Agent` 加 select/answer 双模式。管线适配器 `operators/graph_ops/react_agent_operator.py:80` 把 nemo_agent 包成 CPU 算子，`_retrieve_adapter`（`:243`）注入检索回调，输出按"每查询×每文档×每步"爆行供 RRF 融合（schema `:94-110`）。资源卫生：`query/workflow.py:271,286` 在 finally 里 `retriever.unload()` 释放本地 vLLM。

## 5. 模型接入：nim/local/llm/inference 四路

`models/` 统一全部推理后端。`models/nim/nim.py`（600 行）是 NIM HTTP 客户端核心：OTel span 注入、429 指数退避、批量图像推理多端点轮转；primitives/ 六类 model_interface（vlm/yolox/parakeet/text_embedding/nemotron_parse）。`models/local/` 15 个本地 HF 直跑模型（nemotron_ocr_v1/v2、page_elements_v3、rerank_v2/rerank_vl_v2、vlm_captioner、parakeet_ctc、embed 三变体、agent_llm）。`models/inference/vllm.py` 是无 HTTP 的 vLLM 批式嵌入引擎（NVLink 探测自动降级防 NCCL 崩溃）。`models/llm/` clients（litellm/judge）+ tasks（rag_answer 等）；根层 `warmup_registry.py` 预热、`hf_model_registry.py` 注册、`embed_model_spec.py` 规格。嵌入算子样例：`operators/embed/text_embed.py:187,238`（GPU 变体与原型，`:239` 挂 `_gpu_variant_class`）。

## 6. LanceDB 参考实现：common/vdb 与 RetrievalHit 契约

`common/vdb/`（14 节点）是向量库抽象：`adt_vdb.py` 定义 VDB 接口与能力契约，`factory.py:8` `get_vdb_op_cls` 懒注册后端（`:14` 唯一内置键 `lancedb`），算子侧 `operators/vdb.py:113,215,274` Ingest/Put/Retrieve 三算子。参考实现 `common/vdb/lancedb.py`（2311 行，全仓最大单文件）`class LanceDB(VDB)` 在 `:704`：构造含三检索模式互斥校验（`:742`）、IVF_HNSW_SQ 默认（`:712`）；写入侧 `_json_str`（`:213`）JSON 编码 metadata、`merge_insert(key).when_matched_update_all()`（`lancedb.py:2116`）稳定键 upsert、流式摄取状态机（`lancedb.py:1383,1464,1575`）；检索侧 `retrieval`（`:2183`）稠密/混合、`sparse_retrieval`（`:2126`）稀疏、融合 `hybrid_fusion.py:37`（默认 policy `:34`，打分 `weight/(rrf_k+rank)` `:59`）。**最重要契约 `common/vdb/records.py:112` `RetrievalHit(TypedDict, total=False)`**：docstring `:115-118` 明定 `metadata` 在此边界是原生 dict——绝不许 JSON 字符串泄漏回 API；执行点 `_normalize_hit`（`:565`）在 `:589-605` 构造 normalized hit，`:591-597` 注释记录历史教训（曾让下游人人 json.loads，产生大量静默 `metadata.type=="?"` 假查询）。能力探测 `lancedb_capabilities.py:42`（FTS 列探测 `:111`）。

## 7. 微服务群：app.py 工厂 + ingest.py 主路由

服务本体 42 节点三层。`service/app.py:252` `create_app(config)` FastAPI 工厂：先 `_configure_logging`（`app.py:27`）与 `_apply_resource_limits`（`app.py:53`，CUDA_VISIBLE_DEVICES `app.py:57-59`、CPU 亲和 `app.py:61-67`、RLIMIT_AS `app.py:69-77`）；`_lifespan`（`:123`）按 standalone/gateway/realtime/batch 四模式装九个服务单件——gateway 只装 proxy+work_broker（`app.py:172-179`），其余模式装 pipeline_pool 与双 work_fn（`app.py:181-198`），本地模型可选预热（`app.py:200-212`），shutdown 全序逆拆（`app.py:225-239`）；中间件 requestId（`:243`）+ Bearer 鉴权（`:295-302`）+ 可选 FastMCP（`:259-275`）；gateway 独享 dashboard 静态目录（`:328-342`）；探针 `/v1/live`（`app.py:344`）与 `/v1/health` 深就绪（`app.py:349`，聚合双后端健康 `app.py:367-386`）。主路由 `service/routers/ingest.py`（2467 行，`:132` router）承担作业聚合生命周期：幂等指纹（`ingest.py:246`）、页数路由（`ingest.py:606`，音视频恒 batch `:625-626`、text/html/image 恒 realtime `:627`、PDF 按阈值 `:635`）、document/page/whole 三种上传（`ingest.py:1196,1273,1415`）、SSE 事件流（`ingest.py:2306`）、`/v1/answer`（`ingest.py:1725`）与 `/v1/query`（`ingest.py:1886`）、worker 回调（`ingest.py:2084`）与结果拉取（`ingest.py:2061`）。旁路由 collections/metrics/admin/work/dashboard + services/ 十一件（job_tracker、work_queue、pipeline_executor、event_bus、sidecar_store…）。

## 8. 陷阱与勘误

1. **skills 双包带 sigstore 签名 = agent-first 第 11 例**：`skills/nemo-retriever/` 与 `skills/nemo-retriever-mcp/` 各带 SKILL.md+evals.json+skill-card.md+`skill.oms.sig` 完整签名束——"给 agent 用的技能包"产品线又一实证。
2. **examples 遗留 nv_ingest 导入面**：`examples/launch_libmode_service.py:8-9` 与 `examples/launch_libmode_and_run_ingestor.py:9-13` 仍从 `nv_ingest.*`/`nv_ingest_client.*` 导入——改名后对新包名失效，照跑 ImportError。
3. **retrieval-bench 是榜单快照仓**：独立子包，README 自述 2026-03-13 ViDoRe V3 检索管线榜第一 + BRIGHT 榜第二，代码是冻结快照，依赖外部 vidore-benchmark。
4. **portal/dashboard 是无构建 CDN SPA**：`harness/portal/static/index.html:10-15` 与 `service/dashboard/static/index.html:193-195` 直接引 jsdelivr/unpkg 的 React/Babel/Chart.js，portal `index.html:274` 用 Babel standalone 浏览器内转译 JSX——离线白屏是预期不是 bug。
5. 小坑：双执行器都只支持单根无 fan-out 图（`executor.py:428,611`）；ffmpeg 缺失时音视频上传 501（`app.py:80-120`）；vLLM 类 actor 享受 64 行大 batch 与更高 GPU 份额（`executor.py:574-578,826-829`），调参别按普通算子预期。

**上手路径**：`nemo_retriever/README.md` → `graph/README.md`（>> 链式权威出处）→ `operators/abstract_operator.py`（70 行）→ `graph/executor.py` → 跑 `tests/test_readme_typical_use.py` 对应用例 → 深入 L06-L09 主线。
