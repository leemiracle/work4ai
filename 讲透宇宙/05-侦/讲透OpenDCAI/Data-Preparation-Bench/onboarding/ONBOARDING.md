# Data-Preparation-Bench ONBOARDING

> 基于图谱（274 节点/544 边/12 层/15 步 tour@2508319）+ 源码行号核实。

## 1. 一句话定位

DataPrep-Bench 是首个"以下游效果为锚"的数据准备统一基准（README.md:33），三赛道：**Data Construction**（md_to_qa 四平行方案+data_construction_skill 技能包，Markdown 书转 concept/process/case 三形态 QA）、**Data Selection**（data-selection 子项目，单一 `Selector` 协议下十选择器，README.md:39）、**Data Evaluation**（distflow 的 MMD/DAS 分布距离+Data-Agent-Evaluation 六域下游评测）。distflow 是根 pyproject.toml:3 的 PyPI 包；十选择器与 DAS 是官方强基线，全部在共享域/底座/训练协议/下游基准下对比——比"选出的数据真训得更好"。

## 2. 心智模型

- **Protocol 结构化满足**：typing.Protocol 定契约、不要求继承。`Selector` 只要求 `select(samples)->带 meta 子集`、参数全在 `__init__`（protocol.py:7-24）；distflow 侧 `MetricsProtocol.score`（metrics/protocol.py:8）、`BaseEmbed.embed` 同理——十选择器平行演化、嵌入器互换、指标可插拔的根。
- **Registry 装配**：`data_selection/__init__.py:4-15` 聚协议+十选择器成 barrel，`__all__`（:17-29）即公共 API；上游一行导入即用。
- **昂贵计算必可断点续跑**：ScoreCache（score_cache.py:21，put 即落盘 :49-56）；distflow 的 CachedEmbed（cache_wrapper.py:19）/AsyncCachedOpenAIEmbed（async_cached_embed.py:26）；judge.py 增量续跑（:962-967）。

一句话：**协议定契约→barrel 做装配→缓存保断点→下游精度当最终裁判**。

## 3. 代码地图（12 层）

| 层 | 内容 | 代表文件 |
|---|---|---|
| L01 | 工程基座 | pyproject.toml:3、.gitmodules |
| L02 | data-selection 核心 | data_selection/{protocol.py:7, score_cache.py:21} |
| L03 | 十选择器族 | selectors/{perplexity_based.py:16, composite.py:11} |
| L04 | distflow 数据基座 | src/distflow/data/{dataset.py:11, data_formatter.py} |
| L05 | 嵌入与缓存 | embed/{base.py, openai_embed.py:16}、cache/ |
| L06 | 距离度量与指标 | mmd.py:13、metrics/{protocol.py:8, dsa.py:9} |
| L07 | 基准核心+示例 | benchmark.py:20、examples/compute_mmd.py |
| L08 | 六域评测流水线 | simple-evaluation/{judge.py:772, run_evaluation.sh:154} |
| L09 | 评测数据资产 | MedRBench-extra.json、lex-glue-extra/ |
| L10 | Text2QA 技能包 | data_construction_skill/SKILL.md |
| L11 | md_to_qa 四方案 | md_to_qa/{Agent/, DataFlow/, LLM/, SKILL/} |
| L12 | 示例集+总览 | examples/、Experiment.md |


## 4. 核心链路走读

### 4.1 一条数据选择之旅

examples/random.py:7-11：`RandomSelector(k=100)` 交给 `run_selection`。

1. **归一化**：runner.py:38→read_jsonl（utils.py:11-19）逐行过 `DatasetConfig.format`（dataset.py:15-48）：conversations 键展开消息（兼容 role/content 与 ShareGPT 的 from/value，`_role_map` 映射 human/gpt→user/assistant），否则 instruction/output 平铺两条——下游只见统一 messages。
2. **编排**：runner.py:47 探测类标志 `_score_based`（perplexity_based.py:17 等四类）；多 k 时分数类只按 max(k) 跑一次再截断（runner.py:49-58），随机类逐 k 独立跑保种子；路径支持 `{k}` 模板（:73-77）。
3. **select 本体**（perplexity_based.py:41-107）：查缓存缺口（:43-47）→missing 分批过 Kenlm 打分器（:57）即写缓存（:66）→low/high/mid 排序，**mid 是对数空间离均值最近（:89-90）非线性空间**；返回带 meta。
4. **断点续跑**：ScoreCache 加载存量（score_cache.py:29-39），重跑只补 missing（:73-75）。

模型驱动档：EmbeddingSimilaritySelector=NEAR，目标集三级解析 query_path（推荐）→domain_proxy_text→候选自身（embedding_similarity.py:26-40）；CompositeSelector 串"先质量后多样性"漏斗（composite.py:11-28）。

### 4.2 一条评测之旅（simple-evaluation 三步）

入口 run_all_bench.sh:14-28 的 `MODELS=("domain|model_path")` 数组（分派 :202-218）：math/general/science 三线 cd 进 submodule 并 conda activate（:35-37、:62-63）；business/law/medicine 共用 simple-evaluation（:212-213）。

1. **起服务**：run_evaluation.sh 校验输入与 safetensors（:60-76）后 `vllm serve` 拉起+轮询 /health（:154-171）。
2. **推理**：inference.py AsyncOpenAI+Semaphore（:25）、三次重试（:26）、失败注入占位回复（:49-55）。
3. **裁判**：judge.py:779-794 按 `metadata.source` 分派七裁判（fincdm/xfinbench/legalbench/lexglue/medcasereasoning/medmcqa/medrbench）；lexglue 读本地快照（:336）；`--debug-limit`（:913）/`--mock-openai`（:915）贯通用；按 judge_id 增量 resume（:962-967）。
4. **聚合**：extract_score.py 按 source/dataset_name 派聚合器（legalbench 用 balanced_accuracy）。

distflow 线：compute_mmd.py:107-129 装配 OpenAIEmbed→MMDDistance.compute（mmd.py:101-130）嵌入两集、失败>2% 抛异常（:93-97）、三 RBF 核矩阵（:152-154）、有偏 MMD（:166-170）；DASMetric 取负成相似度分（dsa.py:32-34）；benchmark.py:28-52 指标分 vs 手工 accuracy 做 Pearson/Spearman 拟合。

## 5. 运行与调试

**环境**：三套独立 uv 工程——根 distflow（>=3.10，pyproject.toml:6）；data-selection 锁 `>=3.12,<3.13`、依赖 open-dataflow 与 git 源 dataflex（data-selection/pyproject.toml:26）；simple-evaluation 自带 pyproject。

**先贯通评测线（免真模型）**：自备几行 inference 格式 JSONL（source 用 medmcqa 等无外部依赖项）→`uv run judge.py --debug-limit 5 --mock-openai`（judge.py:913/:915）→`uv run extract_score.py` 聚合。

**再跑选择线（零 GPU）**：`uv run main.py` 5 条样本冒烟（main.py:7-17）；仿 examples/random.py 换自己的数据；GPU 选择器记得给 scores_cache_path。

**调试锚**：distflow 日志=logger.py:87-114 模块级函数；timing_context 报两段耗时（mmd.py:114、:150）；MMD 超参=Experiment.md:5-12。

## 6. 已知坑（第一次跑必读）

1. **三 submodule 未 init，math/general/science 线不可运行**：.gitmodules 声明 lm-evaluation-harness/lm-open-science-evaluation/Qwen2.5-Math，`git submodule status` 全 `-` 前缀、目录空。run_all_bench.sh:35-37 三线正 cd 进这些目录跑评测，且各需 `conda activate math|general|science`（:62-63）。先 `git submodule update --init`。
2. **acc_diagnose.txt 缺失，medrbench 裁判恒 0.5**：judge_medrbench 读相对路径 `MedRBench_instructions/acc_diagnose.txt`（judge.py:735），不存在时**静默返回 0.5 不报错**（:736-738），仓内无此文件——medrbench 分全失真、只以 0.5 流入 error.jsonl；LLM 裁判异常同回 0.5（:756-758）。排查先看 error.jsonl。
3. **DASMetric.compute 与 Protocol.score 名不匹配**：协议要求 `score`（metrics/protocol.py:8），实现却叫 `compute`（metrics/dsa.py:28），benchmark.py:31 硬调 `metrics.score(dataset)`——直接传 DASMetric 必 AttributeError，需自包适配层（examples/run_benchmark.py:26-28 才合规）。
4. **distflow logger 导入（任务书说法勘误，以源码为准）**：`utils/__init__.py` 确为 0 字节，但 `from distflow.utils import logger`（compute_mmd.py:17、mmd.py:8）**实测可运行**——`from package import submodule` 导入的是 logger 子模块，其恰好有模块级 info/debug 函数（logger.py:87-114）；真雷是反向写法 `from distflow.utils.logger import logger`：模块内只有 `_logger`（logger.py:84）无裸名，必 ImportError。
5. **./data/*.jsonl 需自行下载**：run_evaluation.sh:60 要求 `./data/${DOMAIN}.jsonl`，缺失 exit 1，数据在 HF lhpku20010120/Data-Prep-Bench；examples 同引 `data/input.jsonl`（random.py:10），部分硬编码作者集群路径（perplexity_based.py:16）。
6. 次级：依赖约束很新，pip 直装可能解析失败，走 uv。

## 7. 上游与生态

**外部 Scorer 家族（不在本仓图内）**：高阶选择器是薄封装——Perplexity/FineWebEdu/PairQual/DEITA 打分器来自 **open-dataflow**（OpenDCAI DataFlow 框架），offline_near_Selector 来自 **DataFlex**（git 依赖）；低依赖档纯 stdlib 可跑。

**OpenDCAI org 关系**：本仓是 org 基准总仓，与 DataFlow（方法框架，另有讲透OpenDCAI/DataFlow 全套产物）构成"方法 vs 评测"配对；submodule 承担 general/science 域评测；六域参考数据集见 Experiment.md:14-20。

## 8. 学习路径

tour 15 步分四段，配 explain 六篇精讲：

- **第 1 天·选择器线**（t02-t06）：protocol→runner→ScoreCache→十选择器→示例；动手跑 main.py 冒烟。
- **第 2 天·distflow 数学线**（t07-t11）：Dataset 门面→三嵌入引擎→缓存→MMD/DAS→benchmark；读懂 mmd.py:166-179 有偏/无偏分叉，DummyMetrics 跑 run_benchmark.py。
- **第 3 天·评测流水线**（t12-t13）：分派→三步脚本→七裁判→本地资产；动手 --mock-openai 贯通（防坑 1/2/5）。
- **第 4 天·技能线收官**（t01+t14-t15）：按"md_to_qa 四方案竞速→SKILL 胜出升格"演化史读 L10/L11。

出师检验：能为新选择器说清接入点（实现 select+meta、按需置 _score_based、两个 __init__ 各加一行），并解释 DAS 与 MMD 的符号关系。
