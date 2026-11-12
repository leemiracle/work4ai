# Jev-Mem ONBOARDING（图谱 @ 7ab0c73c，2026-10-13）

> 依据：图谱 `.understand-anything/onboard-input.json`（307 节点/641 边/9 层/15 步 tour）+`README.md`+`docs/architecture.md`+构建三件套；仓根 `/usr-data/data1/agent/Jev-Mem`，路径相对仓根。

## 1. 项目是什么 / 为什么存在

Jev-Mem（**System-One-Controlled Agentic Memory**，arXiv:2609.23986，2026-09）是面向长时运行 AI agent 的会话记忆系统，衍生自 MAGMA（MIT 保留，见 `NOTICE`）。核心思想：把「记忆管理的高频决策」与「回答问题的深度推理」拆开——**System-One 控制器 Jev**（TypeSafe 家族，经 Noul/Choice 原语输出命题概率与分类决策）管写入准入、关系判断、检索路由、预算分配与证据充分性评估；**System-Two 语言模型**只从选出证据合成答案。持久 agent 的记忆与检索充满「怎么连、去哪搜、够不够」这类高频且可类型化的决策，交给专用控制器比每次动用大模型更快更省。README 实报 LoCoMo（GPT-4o-mini）：总分 0.777 vs MAGMA 0.700（+11.0%）、构建快 6.6×（158s）、查询延迟 -36.7%（0.93s）；2026-09 起支持本地 Laya 替换 Jev 做同样决策（`docs/laya.md`）。

## 2. 仓库布局与分层地图（9 层）

| 层 | 名称 | 文件数 | 职责与代表 |
| --- | --- | ---: | --- |
| 1 | 编排、CLI 与兼容入口 | 11 | `jev_mem/cli.py`、`jev_mem/system.py`（门面）、`jev_mem/demo.py`；根目录 6 个 sys.modules 转发旧入口（`main.py` 等） |
| 2 | System-One 决策控制 | 6 | `memory/jev_mem_config.py`（约 40 项 frozen 配置，fan-in 14 全图最高）等六模块，见第 4 节（一） |
| 3 | 记忆存储与检索 | 13 | `memory/graph_db.py`、`memory/memory_builder.py` 等 13 个模块，见第 4 节（二） |
| 4 | 评测与答案质量 | 7 | `memory/test_harness.py`、`memory/evaluator.py` 等，见第 4 节（三） |
| 5 | 基准与数据集 | 6 | `jev_mem/benchmarks/locomo.py`、`jev_mem/benchmarks/longmemeval.py`（兼 MAGMA 基线入口）+`jev_mem/datasets/` loader |
| 6 | 测试 | 9 | `tests/test_jev_mem.py`（58 测试主套件）等 9 套离线 pytest |
| 7 | 共享工具与脚本 | 7 | `utils/utils.py`（指标箱）、`utils/memory_layer.py`（LLM 控制器）、`scripts/check_public_release.py`（发布守门） |
| 8 | 文档与示例 | 15 | `README.md`（17 节）、`docs/architecture.md`（fan-out 12 全图最高）、`docs/` 四份指南、`examples/` |
| 9 | 配置与支撑 | 16 | `config/` 四份实验档+`pyproject.toml`/`pytest.ini`/`.github/workflows/ci.yml` 等构建支撑 |

依赖方向大致 1→2/3→4/5，6 横切；`docs/architecture.md` 目录职责表是官方权威。

## 3. 架构总览：一条请求的旅程

**写路径（会话→记忆图）**：输入经 `jev_mem/cli.py` 或 `JevMemSystem`（`jev_mem/system.py`，角色/文本/ISO 时间戳逐项校验）进入；`memory/episode_segmenter.py` 借鉴 Nemori 语义边界切 episode；`memory/memory_builder.py` 抽取事件、创建 session/episode/event 三层节点。每条观察由 `memory/jev_questions.py` 构造准入+多标签类型问题（合并单次请求），`memory/jev_client.py` 调 Jev 取概率（可换 `memory/laya_backend.py` 本地后端），`memory/jev_mem_policies.py` 的 WritePolicy 译成准入判定与关系生成；时间戳排序等确定性链接由代码处理。图落 `memory/graph_db.py`（可替换 Neo4j），向量落 `memory/vector_db.py`，`memory/keyword_enrichment.py` 在 embedding 前增强内容。

**读路径（问题→答案）**：`memory/jev_mem_retrieval.py` 检索控制器主导——检索槽排队记时长，路由问题评估六维需求，向量+关键词（时间性问题走时间关键词搜索）RRF 融合取锚点，按图预算做受 CallBudget 双预算约束的批式遍历，真实证据上评估自适应停止。多层检索、意图/题型检测、时间推理（`memory/temporal_parser.py`）与 QA 上下文组装由 `memory/query_engine.py` 承担。证据交 System-Two LLM 合成答案，`memory/answer_formatter.py` 规范化，决策落 DecisionLog 审计（无凭据无内容）。缓存按配置哈希定位；图插入失败回滚向量侧（测试钉版不变量）。

## 4. 核心子系统深入

**（一）System-One 控制面**。`memory/jev_mem_config.py`：约 40 项 frozen 配置，`load()` 拒绝未知键、`__post_init__` 全量校验，配置错误启动即暴露。`memory/jev_client.py`：SHA256 键 LRU 缓存、外层重试+遵守 Retry-After、CallBudget 双预算、失败封闭（JevUnavailable）。`memory/jev_questions.py`：七类决策问题模板（准入/类型/关系/巩固/路由/停止/遍历）；Noul 输出「命题概率」而非分级重要性，question ID 不进模型、由指令显式引用状态字段。`memory/jev_mem_policies.py`：WritePolicy 把概率译成准入判定与关系生成，allocate_graph_budgets 分配子图配额。`memory/jev_mem_retrieval.py` 见第 3 节。

**（二）存储与检索（TRG 面）**。`memory/graph_db.py`：NodeType/LinkType 枚举、三层节点与 Link 边、TraversalConstraints，NetworkXGraphDB 实现可替换 Neo4j。`memory/trg_memory.py`（TemporalResonanceGraphMemory）：Jev-Mem 与 MAGMA 基线**共用**的图后端——快慢路径摄取、巩固、时序/语义/因果建链、邻域推断潜边。`memory/vector_db.py`：FAISS/NumPy 双实现+双通道编码器。`memory/cache_compat.py`：Sys1Mem→Jev-Mem 改名兼容（读旧写新）。`memory/local_device.py`：macOS 默认 CPU 规避 Metal abort。

**（三）评测与基准**。`memory/test_harness.py` 驱动「问题→检索→生成」，打分委托 `memory/evaluator.py`（LLMJudge 语义分+F1/BLEU/ExactMatch）；`memory/llm_judge.py` 是 0.0-1.0 评分 prompt+不可答判定。LoCoMo 走 `jev_mem/benchmarks/locomo.py`（reuse 校验、score-only 重评）；LongMemEval 每题自带 haystack，`memory/longmemeval_jev.py` 包进共享写/检管线（内容哈希缓存、gold 绝不进构建或检索），`memory/longmemeval_evaluator.py` 按题型 rubric。README 明示：论文只报 LoCoMo，LongMemEval 用宽松 scorer 非官方指标、不声称结果。

## 5. 关键文件 Top 榜（度数=入度+出度，Top15）

| # | 文件 | 度 | 一句话职责 |
| --- | --- | ---: | --- |
| 1 | `tests/test_jev_mem.py` | 95 | 58 测试=端到端不变量 |
| 2 | `memory/graph_db.py` | 33 | 图库抽象+NetworkX 实现 |
| 3 | `tests/test_longmemeval_jev.py` | 32 | LME 适配离线集成测试 |
| 4 | `memory/vector_db.py` | 23 | 向量库双实现+双编码器 |
| 5 | `memory/jev_mem_config.py` | 21 | 控制面配置（fan-in 最高） |
| 6 | `tests/test_backend_cache.py` | 19 | 缓存复用一致性校验 |
| 7 | `memory/trg_memory.py` | 18 | TRG 共享图后端 |
| 8 | `memory/jev_client.py` | 16 | Jev 适配：缓存/预算/审计 |
| 9 | `jev_mem/benchmarks/locomo.py` | 16 | LoCoMo 运行器+基线入口 |
| 10 | `memory/memory_builder.py` | 15 | 写路径中枢 |
| 11 | `memory/query_engine.py` | 13 | 多层检索+RRF+遍历 |
| 12 | `memory/cache_compat.py` | 13 | 改名缓存兼容层 |
| 13 | `jev_mem/system.py` | 8 | 公共门面 |
| 14 | `memory/mock_encoder.py` | 8 | 确定性离线编码器 |
| 15 | `jev_mem/cli.py` | 7 | build/query CLI |

（截断处 `README.md` 等节点同为 7 度。）

## 6. 导览路线（15 步 tour）

加粗标题即图谱 tour 步名，按 1-15 顺序就是学习路径（前 5 步控制面、6-10 数据面、11-15 评测工程）：

1. **项目概览：Jev-Mem 是什么** — `README.md`+`docs/architecture.md`。
2. **命令行入口与公共门面** — `jev_mem/cli.py`→`jev_mem/system.py`；跑 `python -m jev_mem.demo` 走通全管线。
3. **控制面配置：JevMemConfig** — `memory/jev_mem_config.py`+`config/README.md`。
4. **Jev 决策客户端与本地后端** — `memory/jev_client.py`+`memory/laya_backend.py`。
5. **Noul/Choice 决策协议与写入策略** — `memory/jev_questions.py`→`memory/jev_mem_policies.py`。
6. **写路径：从会话到记忆图** — `memory/memory_builder.py`+`memory/episode_segmenter.py`。
7. **存储层：TRG 图与向量库** — `memory/graph_db.py`、`memory/trg_memory.py` 等。
8. **检索与查询引擎** — `memory/query_engine.py`+`memory/jev_mem_retrieval.py`。
9. **时间解析** — `memory/temporal_parser.py`。
10. **答案格式化与 Best-of-N** — `memory/answer_formatter.py`+`memory/best_of_n_selector.py`。
11. **评测闭环：Harness、裁判与指标** — `memory/test_harness.py`、`memory/llm_judge.py`。
12. **LoCoMo 基准与数据集** — `jev_mem/benchmarks/locomo.py`+`jev_mem/datasets/locomo.py`。
13. **LongMemEval 基准与适配** — `memory/longmemeval_jev.py`。
14. **配置系统与实验档** — `config/` 三份替代档+`.env.example`。
15. **测试、CI 与发布守门** — `tests/test_jev_mem.py`+`.github/workflows/ci.yml`+`scripts/check_public_release.py`。

## 7. 构建与测试（实证）

- **安装**：Python **3.11+**（`pyproject.toml`+CI 双钉）。源码侧 `pip install -r requirements.txt`；开发 `pip install -e .`+`requirements-dev.txt`（加 pytest/matplotlib/build）；一键 `bash setup.sh`。可选组 `'.[laya]'`/`'.[mlx]'`（版本见 `pyproject.toml`，mlx 仅 Apple Silicon）。
- **入口**（`pyproject.toml` 四个 console script）：源码侧 `python -m jev_mem{,.demo,.benchmarks.locomo,.benchmarks.longmemeval}`；安装后 `jev-mem{,-demo,-eval,-longmemeval}`。
- **测试**：`pytest.ini` 仅 `testpaths = tests`；`python -m pytest -q` 全离线（MockEncoder/fake laya，无 provider 无下载）。
- **CI**（`.github/workflows/ci.yml`）：ubuntu×macos 矩阵（fail-fast 关闭），Python 3.11，env `USE_TF=0`/`HF_HUB_OFFLINE=1`/单线程保证离线确定性；四步=装 `requirements-dev.txt`→`pytest -q`→`python scripts/check_public_release.py --tracked`→`python -m build`。wheel 只含代码，sdist 经 `MANIFEST.in` 补配置与文档。

## 8. 新人上手建议

**阅读顺序**：`README.md`→`docs/architecture.md`（改代码前必读）→跑 `python -m jev_mem.demo`→按第 6 节 tour 3-8 步精读控制面与数据面模块→最后把 `tests/test_jev_mem.py` 当行为规格读（58 测试=58 条不变量）。

**常见坑**：
1. `examples/locomo_synthetic.json` 是演示 schema 的合成样本；真实数据集不随库分发，按 `data/README.md` 下载到 `data/`。
2. live 管线调付费 provider（key 只放 `.env`），离线一律用 demo。
3. LoCoMo 跑分加 `--best-of-n 1`（默认 3 有参考偏置会虚高）。
4. 缓存复用严格：backend/模型/mock 变更被拒（`tests/test_backend_cache.py`）；`--reuse-memory` 不能配 `--rebuild`。
5. 曾名 Sys1Mem：旧缓存经 `memory/cache_compat.py` 兼容读；根目录 6 个转发文件（`main.py` 等）别加逻辑，改 `jev_mem/` 下实现。
6. 新增源文件必须同时登记 `public-release-files.txt` 与 `MANIFEST.in`，否则 CI 守门/打包不一致。
7. macOS 本地模型默认 CPU 是刻意的（Metal abort 无法回退），别「修复」`memory/local_device.py`。
8. 大的算法或依赖变更先开 issue（`CONTRIBUTING.md`）；评测口径与对照要求见 `docs/evaluation.md`。
