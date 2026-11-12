# 04 · 评估引擎与 leaderboard：论文数字的生产线

## 角色定位

`evaluation/` 是 kvpress 的"度量衡"：所有策略的论文数字、HF leaderboard（nvidia/kvpress-leaderboard Space）榜单都从这条管线产出。它把"模型×press×压缩率×benchmark"的笛卡尔积跑成 DataFrame，评分器按任务分派，配置走 YAML+CLI 双通道。附带的 `kvzap/` 训练子项目则演示"压缩策略本身可训练"的闭环——训出的门控权重被推理侧直接消费。

## 内部结构

主引擎 `evaluation/evaluate.py`（577 行）：EvaluationConfig 数据类（`evaluation/evaluate.py:38`）收拢全部旋钮（max_new_tokens `:54` 等）；EvaluationRunner（`:189`，11 方法）驱动"数据装载→press 压缩→生成→评分"——per-row 生成时 max_new_tokens 有行级覆盖（`:421/:427`）；run_evaluation（`:503`）完成收尾聚合；CliEntryPoint（`:533`）的 `__call__`（`:543`）允许 `python evaluate.py --dataset loogle --press_name expected_attention --compression_ratio 0.5` 式命令行覆盖 `evaluate_config.yaml`。名字解析集中在 `evaluation/evaluate_registry.py` 三注册表：DATASET_REGISTRY（`:54`）、SCORER_REGISTRY（`:68`）、PRESS_REGISTRY（`:82`）——YAML 按名引用，新增 press/benchmark 在此登记。多卡分派靠 `evaluation/evaluate.sh`（按 GPU 数并发跑 compression_ratios 网格，默认 ruler/4096/Llama-3.1-8B）。**leaderboard.sh**（49 行）生成榜单数据：先跑 no_press 基线（`evaluation/leaderboard.sh:13`），再分两轮循环——"无需 question 参与压缩的 press"（`:10-11`：random/knorm/snapkv/expected_attention/streaming_llm/tova/observed_attention/qfilter 等）与需要的分开计时，保证跨策略可比。基准十件套在 `evaluation/benchmarks/`（aime25/infinite_bench/longbench/longbenchv2/loogle/math500/needle_in_haystack/ruler/zero_scrolls+utils.py），每套 create_huggingface_dataset（造数）+calculate_metrics（算分）两件套；公共提取器 extract_boxed 在 `evaluation/benchmarks/utils.py`（嵌套/首个/末个 boxed 语义，`tests/test_evaluation_utils.py` 钉死口径）。

## 外部连接

**kvzap 子项目**（`kvzap/`，arXiv 2601.07891，`kvzap/README.md:4`）：KVzip（2505.23416，`kvpress/presses/kvzip_press.py:33`）的快速近似——轻量 surrogate 模型对隐状态预测重要性分，低于阈值即移除，prefill 与解码都可用（`kvpress/presses/kvzap_press.py:55` docstring）。闭环四件：train_mlp/train_linear 两种门型（`kvzap/train.py:28/:87`）与总入口 train（`:122`）；KVzapDataCollector（`kvzap/data.py:144`）从问答对采集门控样本，load_nemotron_dataset（`:22`）供数，repeat_prompt_tokenization（`:90`）处理重复提示；evaluate_aime.py 的 evaluate/calculate_metrics（`kvzap/evaluate_aime.py:34/:16`）在 AIME25 验收；推理侧 KVzapPress（ScorerPress 子类，`kvpress/presses/kvzap_press.py:53`）加载产物，推荐与 DMSPress 阈值策略联用（`kvzap/README.md:19`）。CI 侧 `.github/workflows/check-leaderboard.yml` 每日 08:00 巡检 leaderboard Space，异常自动开 issue。

## 数据流

一次评测的完整路径：读 `evaluation/evaluate_config.yaml` → CliEntryPoint 合并 CLI 覆盖 → registry 解析 press/benchmark/dataset 名 → EvaluationRunner 逐行取数据 → pipeline 前缀压缩+生成（行级 max_new_tokens）→ benchmarks 的 calculate_metrics 评分 → 聚合落盘。leaderboard 流程再包一层：脚本按两轮分组枚举 press×ratio 网格 → 数据推 HF Space → check-leaderboard workflow 次日巡检。kvzap 训练流独立成环：Nemotron 问答语料 → collector 采集 (隐状态, 保留/移除) 样本 → train_mlp/linear 得 KVzapModel → evaluate_aime 验收 → 推理侧加载。

## 设计决策

三个决策：①注册表模式让 YAML 与代码解耦——评测配置可版本化、可 diff；②leaderboard 把"question 是否参与压缩"显式分轮——不同信息可见性下的数字不可直接对比，分开跑是诚实口径；③kvzap 子项目与主库共享 press 抽象（KVzapPress 就是 ScorerPress）——训练管线与推理管线共用同一评分接口，训推一致。

## 新人提示

从 `evaluation/README.md` 的三步走起（配置 YAML→python evaluate.py→CLI 覆盖）；先跑小网格（单 press 单 ratio 的 ruler）再上全量。新增 benchmark 记得三处同步：benchmarks/ 目录两件套 + DATASET_REGISTRY 登记 + calculate_metrics 单测。复现论文数字时先看 leaderboard.sh 的分组口径再对比。kvzap 训练照 `kvzap/train.py:122` 的入口读参数流；AIME 验收口径在 `kvzap/evaluate_aime.py:16`（取最后 boxed 答案）。
