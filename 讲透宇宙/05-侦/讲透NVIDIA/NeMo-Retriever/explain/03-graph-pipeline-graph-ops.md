# 03 · 管线编排：pipeline_graph + executor + graph_ops 图算子

> 路径相对 `nemo_retriever/src/nemo_retriever/`。

## 角色定位

这一篇回答"算子怎么连成数据流并跑起来"。三个组件各管一段：`graph/pipeline_graph.py`（208 行）定义 Node/Graph 数据结构与 `>>` 语法；`graph/executor.py`（893 行）提供双执行器（进程内 pandas 与 Ray Data 两种执行形态）；`operators/graph_ops/`（14 个算子）是管线粒度的功能站——它们本身也是 AbstractOperator（见 01 篇），只是不再按模态抽取内容，而是做入库、融合、agent 循环等整链动作。graph/README.md 是 `>>` 链式组合与 UDF 的官方文档。

## 内部结构

**Node/Graph**：`Node`（`graph/pipeline_graph.py:30`）包一个算子，`__init__`（`:42-56`）做类型断言（非 AbstractOperator 直接 TypeError `:50-51`）、记 name/children、并把 `operator.get_constructor_kwargs()` 冻结为 `operator_kwargs`（`:56`）。`add_child`（`:58-62`）追加子节点。`Graph`（`:84`）持 roots 列表与 `_tail` 指针；`add_root`（`:107`）支持合并另一张图的 roots（`:109-114`），`add_chain`（`:119`）一次挂一条链。`>>` 的三处实现构成完整链式体验：算子上（`operators/abstract_operator.py:59-70`）自动包 Node；Node 上（`graph/pipeline_graph.py:64-77`）建新 Graph 返回；Graph 上（`:132-149`）向 `_tail` 追加并返回自身。裸算子传进任何挂载点都会被 `_ensure_node`（`:14-27`）自动包装。

**执行入口**：`Graph.execute`（`:165-172`）先 `resolve_for_local_execution`（`:192-196`，把 archetype 原型解析成具体变体）再 `execute_in_place`（`:174-184`）逐根深度优先；`_execute_node`（`:198-204`）父输出喂子输入、叶输出收进列表。

**双执行器**：`AbstractExecutor`（`graph/executor.py:390`）只约定 `ingest()`（`:402-405`）。`InprocessExecutor`（`:408`）零 Ray 依赖：`_linearize`（`executor.py:422-439`）把单根链拉平成序列（多根或 fan-out 直接 ValueError `:428,434-437`）；`ingest`（`executor.py:441-489`）接受 DataFrame/路径/路径列表，路径经 `_load_files`（`executor.py:491-506`）读成 bytes+path 列，然后 `resolve_graph`（`executor.py:468`）+ 逐节点 `operator_class(**operator_kwargs)` 重建（`executor.py:472`）+ tqdm 顺序跑（`:480-487`）——调试与单测首选。`RayDataExecutor`（`:509`）把每个 Node 折成一个 `map_batches` stage（`:883-891`），`fn_constructor_kwargs` 保证算子在 worker 上懒构造。调度智能五处：`_scheduled_num_gpus`（`:567-587`）按 `GPUOperator` 类型与远程端点探测（`_has_remote_endpoint :557-565`）分配 GPU 份额，基线 `OCR_GPUS_PER_ACTOR=0.1`（`common/ray_resource_hueristics.py:42`），vLLM 系 actor（NemotronParse/Caption）抬高到 `VLLM_GPUS_PER_ACTOR`（`:574-578`）；vLLM 系 actor 批量放大到 `NEMOTRON_PARSE_BATCH_SIZE=64`（`:826-829`，常量 `common/ray_resource_hueristics.py:36`）；`REQUIRES_GLOBAL_BATCH` 类标记的自连接算子强制 `repartition(num_blocks=1)` 或按 `GLOBAL_BATCH_GROUP_KEYS` 哈希分块（`:842-853`）；Ray 2.49 要求 callable class 显式并发，默认补 `concurrency=1`（`:816-819`）；pandas 格式时用 `_ArrowPandasOperatorAdapter`（`:176`，构造点 `:860-877`）压缩 Arrow 批防切片偏移，且一旦算子产出异构行就全程保持 pandas 不回 Arrow（`:866-877` 注释解释 bbox 张量分裂问题）。

**graph_ops 十四算子**（`operators/graph_ops/`）：`react_agent_operator.py:80` ReActAgentOperator（510 行，agentic 主力，见 04 篇）；`rrf_aggregator_operator.py:18` RRFAggregatorOperator 倒数秩融合多路检索；`selection_agent_operator.py:44` SelectionAgentOperator；`subquery_operator.py:77` SubQueryGeneratorOperator 查询改写；`lancedb_write_operator.py` 入库、`store_operator.py` 内容外存、`scoring_operator.py` 打分、`eval_operator.py` 评测、`webhook_operator.py` 回调、`custom_operator.py`/`file_loader_operator.py`/`multi_type_extract_operator.py`/`content_operators.py` 骨架与内容站。配套机制：`graph/graph_pipeline_registry.py` 登记可复用管线，`graph/designer.py` 按参数设计整图，`graph/ingestor_runtime.py`+`graph/retriever.py` 是库模式运行时。

## 外部连接

上游：`ingestor/core.py:43` `create_ingestor`（inprocess/batch 分支）→ GraphIngestor（`ingestor/graph_ingestor.py`）→ 执行器；`ingest/plan.py`（804 行 `resolve_ingest_plan`）把 CLI 参数解析成图配置。下游：每个 Node 的算子是 01/02 篇的模态算子+本篇图算子；Ray 资源探测依赖 `common/ray_resource_hueristics.py`（ClusterResources/BatchTuningParams）。服务模式的 `service/services/pipeline_executor.py` 以进程池包裹本执行器。

## 数据流

库模式一次摄取：文件清单 → `resolve_ingest_plan` 产配置 → designer 组图（file_loader → multi_type_extract → 各模态算子 → embed → lancedb_write）→ GraphIngestor 选执行器 → InprocessExecutor 单机顺序跑 或 RayDataExecutor 折成 Ray Data 流水线逐 stage `map_batches` → 叶输出聚合。查询方向：query 图（AgenticQueryInputOperator → embed/检索 → react/selection → AgenticSelectionOutputOperator）同样走这套执行器。

## 设计决策

1. **两执行器共享同一张图**：同一 Node/Graph 结构在 pandas 单进程与 Ray 集群两种后端无损切换，代价是两者都显式放弃 fan-out（`:428,611`）——图结构刻意保持线性，分支需求下沉为算子内部并行（如 react 算子内的 ThreadPoolExecutor）。
2. **kwargs 冻结在 Node 构造时**：图一旦建好，参数即快照，后改算子实例属性不影响执行器重建——可预期的同时意味着改参要重建图。
3. **批放大只认 vLLM 系**：普通 GPU 算子批 1，vLLM actor 批 64（连续批处理自己消化），白名单硬编码在 executor（`:574-578,826-829`），新增 vLLM 后端要记得登记。
4. **global-batch 约定用类属性**：自连接算子（音视融合/跨帧去重）声明需求而非执行器嗅探——需求方声明优于调度方猜测。
5. **Arrow↔pandas 边界单点处理**：所有格式转换集中在 adapter 一处，配合 preserve_pandas_output 状态位，把 Ray schema 分裂类 bug 关在笼子里。

## 新人提示

- 想看懂任何一条预置管线，从 `graph/graph_pipeline_registry.py` 找登记名 → designer 看组装逻辑 → executor 看资源策略，三步定位。
- 调试图用 InprocessExecutor（错误栈干净、pandas 可断点）；性能验证才上 RayDataExecutor。
- `graph >> node` 与 `node_a >> node_b` 混用合法但注意 `Graph.__rshift__` 只挂到 `_tail`——手动 add_root 之后再 `>>`，落点可能与直觉不符（`:142-148`）。
- 排查"算子在 worker 上重建失败"时对照 `get_constructor_kwargs` 的反射规则（01 篇），八成是参数名与实例属性名不一致。
- Ray 2.49+ 报 callable class 并发错误时查 node_overrides 里是否漏 `concurrency`（`:816-819` 的默认补丁只在 executor 内生效）。
