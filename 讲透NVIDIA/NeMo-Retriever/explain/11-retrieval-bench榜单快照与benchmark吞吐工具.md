# 11 retrieval-bench 榜单快照仓与 benchmark Ray 吞吐工具

## 角色定位

`retrieval-bench/` 是仓内的独立 Python 包（自带 pyproject，3238 行）：既是 agentic 检索管线的**评测框架**（dense/agentic 两种评估模式、四后端可插拔），也是两个公开榜单成绩的**快照与提交物**——截至 2026-03-13，NeMo Retriever Agentic Retrieval Pipeline 列 ViDoRe V3 Pipeline 榜第一（`README.md:20`、徽章 `submissions/vidore_v3_agentic_pipeline.md:8`）、BRIGHT 推理密集检索榜第二（`submissions/bright_agentic.md:8`）。同一管线两种配置：ViDoRe 用视觉嵌入模型 nemotron-colembed-vl-8b-v2（本身也是 ViDoRe v3 嵌入榜第一，`vidore_v3_agentic_pipeline.md:49`），BRIGHT 用 LLaMA-3.2-3B 底座的推理检索器 llama-nv-embed-reasoning-3b（`bright_agentic.md:47`），agent 均为 Claude Opus 4.5。库内 `tools/benchmark/` 则是另一回事：Ray Data 吞吐基准，扫 worker×batch 网格找 PDF 抽取各阶段最优配置。

## 内部结构

**agentic 管线**（`src/retrieval_bench/nemo_agentic/`）：ReACT 架构。`agent.py:31` 的 `Agent` 类持有 Jinja2 渲染的系统提示（`agent.py:58-65`，支持文件路径或模板名双形态）与 message_history；工具集含 `think`（规划，`tool_helpers.py:76`）、`retrieve(query, top_k)`、`final_results`。检索工具有结果保证机制：`retrieve_with_guarantees` 强制返回新文档——`ensure_new_docs` 开启时已见 docid 不重发内容只发提示（`agent.py:205-225`）。RRF 兜底：步数上限或上下文超限时，用全轨迹各次检索的排名做 Reciprocal Rank Fusion（提交文档 `vidore_v3_agentic_pipeline.md:74`，代码 `agent.py:413-425` 的 `rrf_from_subquery_results`，配置开关 `configs.py:27` 的 `calculate_rrf: bool = True`）。LLM 层 `llm_handler.py:102` 的 `LLM` 类封装 OpenAI 兼容调用，默认读 `OPENAI_API_KEY`/`OPENAI_BASE_URL`（`README.md:94-95`），429 限流自动暂停 60s 重试（`llm_handler.py:88-98`）。

**单例检索器群**（`singletons/`，五实现）：bm25s、hf_dense、colembed、nemotron_embed_vl_dense、nemotron_colembed_vl_v2。这是提交文档里最硬的工程故事的代码落点——原架构用 MCP server 连检索器与 agent，进程管理+每轮加载 GPU 嵌入+网络延迟造成"性能税"与频繁冻结，改为进程内线程安全单例（`bright_agentic.md:84`），模型与语料加载一次、reentrant lock 保护共享 GPU 访问（`bright_agentic.md:86`）。实证：每个实现的构造器里都有 `self._lock = threading.RLock()`（如 `nemotron_embed_vl_dense_retriever.py:475`、`colembed_retriever.py:229`）。GPU 预载失败安全降级：`_shared.py:35` 的 `try_preload_corpus_to_gpu` 捕 OOM 返回 None 留在 CPU，打分时分块搬运（`nemotron_embed_vl_dense_retriever.py:427-436` 的 chunk 循环）；缓存 key 用语料 id 的 10 位 sha256（`_shared.py:20`）。

**评测与 CLI**：`cli/evaluate.py` 两个主命令 dense-retrieval（`:358`）与 agentic-retrieval，`--backend` 选检索器、`--pipeline-args` JSON 传覆盖（`README.md:68-75`）。指标计算走 pytrec_eval，默认 `ndcg_cut_10`（`pipeline_evaluation/evaluator.py:74-75`、`:288`），空结果拒算指标（`evaluator.py:280`）。数据加载薄封装上游 vidore-benchmark（`dataset_loader.py:17-19` 直接 import `load_vidore_dataset`），BRIGHT 有仓外缓存目录探测（`dataset_loader.py:61-63`）；README 明说本仓是"slim snapshot"非自足框架（`README.md:10-11`）。BRIGHT 任务指令本地化（`prompts/bright_instructions.py:12` 的 `BRIGHT_TASKS_POST` 集合）。BRIGHT 提交还披露了检索器的训练数据合成管线：锚文档+top-4 近邻组文档集，Qwen3-235B-A22B 生成 ≤300 token 推理型查询、显式滤除测试集正文档防泄漏（`bright_agentic.md` SDG 节）。

**benchmark 工具**（`tools/benchmark/`）：typer 多命令（ocr/extract/page_elements/split/audio/all），核心 `common.py:160` 的 `benchmark_sweep`——workers×batch_sizes 双层循环，`rd.from_items` 造数据集、map_builder 应用阶段算子、`count()` 触发执行计时算 rows/s，全网格跑完报最优（`common.py:196-199`）；`ThroughputResult` 数据类（`common.py:24`）记录 workers/batch_size/rows/elapsed/rows_per_second。`all_actor.py:14` 串行跑全部阶段。各阶段默认扫不同网格：OCR `--batch-sizes 1,2,4,8`（`ocr_actor.py:32`）、extract/page_elements `1,2,4,8,16`（`extract_actor.py:31`）。

## 外部连接

retrieval-bench 依赖外部 `vidore-benchmark` 包（框架模块不 vendored），HF 数据集 `vidore/vidore_v3_*` 与 `xlangai/bright`（`dataset_loader.py:96` 两大小写都试），HF 模型全部 `trust_remote_code=True`——README 安全注记明确警告执行模型仓自带 Python 代码的风险（`README.md:13-17`，实例 `hf_dense_retriever.py:201`）。agent 侧连任意 OpenAI 兼容端点。benchmark 工具连本仓 operators（`common.py:20-21` import `PDFExtractionActor`/`split_pdf_batch`）与 Ray 集群（`common.py:63` 的 `maybe_init_ray`）。retrieval-bench 的语料缓存探测指向上层目录的 `BRIGHT/cache`——它是主仓的子包而非孤立工具。

## 数据流

agentic 评估一次运行：CLI 载入数据集（queries+qrels+corpus）→ 单例检索器 `init` 加载模型+预计算语料嵌入（OOM 则 CPU 留驻）→ Agent 循环：LLM 生成 thought/tool_call → retrieve 工具保证新文档地探查语料 → final_results 定稿 top-k → （兜底）RRF 聚合全轨迹排名 → pytrec_eval 算 nDCG@10 → 结果 JSON+trace。benchmark：种子行（`make_seed_extraction_row` 等，`common.py:83-96`）复制 N 份 → 双层网格每格重建 Ray 数据集 → map 阶段算子 → count() 计时 → 输出每格 rows/s 与全局最优。

## 设计决策

1. **MCP→进程内单例**：榜单提交的核心工程教训——agent 工具服务不一定该上 MCP，进程内+RLock 在评测吞吐场景完胜（`bright_agentic.md:84-86`）。
2. **RRF 永远兜底**：agent 失败（步数耗尽/上下文溢出）时退化为全轨迹排名融合，保证管线总有产出（`configs.py:27` 默认开）。
3. **结果保证机制**：retrieve 强制去重防 agent 在同一批文档上打转。
4. **榜单快照与代码同仓**：提交文档（含管线图 PNG）+复现命令+代码一体，成绩可复算。
5. **benchmark 网格扫描而非单点**：每阶段 worker/batch 最优配不同，工具化扫网格+报最优。
6. **trust_remote_code 风险显式化**：README 顶置安全注记而非埋文档。

## 新人提示

- retrieval-bench 不能独立跑：先 `pip install vidore-benchmark`，或接受它只是快照仓的定位。
- 四后端的 transformers 版本要求分裂：多数 4.51.0，`nemotron-colembed-vl-8b-v2` 要 5.0.0rc0（`README.md:33-45`）——同环境装两个版本会打架。
- 429 重试是 sleep 60s 硬等待（`llm_handler.py:98`），大批量评测预算时间时别忘算。
- benchmark 的 `count()` 是触发算子执行的 action，改 map 链不动 action 会得到假吞吐。
- 语料缓存 key 是 docid 序列的 hash（`_shared.py:20`）——改语料顺序即换缓存，别误当缓存失效 bug。
