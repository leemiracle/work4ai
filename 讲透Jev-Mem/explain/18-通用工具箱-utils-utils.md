> 标题：通用工具箱——utils/utils.py 精讲 · 源文件：utils/utils.py（375 行）· 图谱标签：评测子系统 / 指标计算叶子模块（全仓指标唯一权威源）

## 角色定位

Jev-Mem 的指标计算唯一权威源：把 (prediction, reference) 一对文本变成十二维指标 dict，再聚合成整体与分题型的统计表。它不 import 任何项目内业务模块（仅 memory.local_device 做设备选择，utils/utils.py:2、87、149），是干净的叶子；消费方 grep 实证仅一处——memory/evaluator.py:16 只 import calculate_metrics，在 evaluate_answer 内调用（memory/evaluator.py:70）。utils/__init__.py 一句 docstring "Shared model-provider adapters and evaluation utilities" 说明 utils 包的定位就是共享工具，本文件承担其中"evaluation utilities"半边。

文件的特殊价值在两处设计：重模型的懒加载单例（SBERT 首次用到才载入），以及 category 5 对抗题的指标塌缩规则——后者直接决定跑分榜上对抗题分数的含义。

## 内部结构

**可选依赖区**（utils/utils.py:14-55）：五个 try-import 各带 warning——rouge_score、nltk（BLEU+METEOR）、bert_score、sentence_transformers、openai。注意两处死代码：`OPENAI_AVAILABLE` 旗标设完无人读（utils/utils.py:45-50，全文件无第二处引用）；`from jev_mem.datasets.locomo import ...` 拉进 load_locomo_dataset/QA/Turn/Session/Conversation 五个名字，正文一次没用（utils/utils.py:52-55）——纯粹为了"缺库时打一行 warning"的副作用 import，还把数据集层耦进了指标层。

**懒加载单例区**（utils/utils.py:57-91）：模块级 sentence_model 缓存、`_resource_lock` 与 `bert_score_lock` 两把线程锁（utils/utils.py:60-61）。`_initialize_nltk` 一次性下载 punkt/punkt_tab/wordnet（utils/utils.py:64-76）；`_get_sentence_model` 双检锁加载 all-MiniLM-L6-v2 到 local_model_device（utils/utils.py:79-91）。细节：`_sentence_model_initialized` 在 try 外置位（utils/utils.py:90），加载失败也标记已初始化——每进程只试一次、失败后永久返回 None，避免反复重载大模型的抖动，是刻意的"一次失败永久放弃"。

**单指标函数组**（utils/utils.py:94-187）：simple_tokenize 做小写+四种标点替换+split（utils/utils.py:94-98）；calculate_rouge_scores 检查 ROUGE_AVAILABLE 出零兜底（utils/utils.py:100-108）；calculate_bleu_scores 检查 NLTK_AVAILABLE、四组 n-gram 权重各带平滑（utils/utils.py:118-138）；calculate_bert_scores **不检查** BERT_SCORE_AVAILABLE，直接靠宽 except 兜住 NameError 返回零（utils/utils.py:140-161）——bert_score 全局锁串行化（utils/utils.py:147）；calculate_meteor_score 与 calculate_sentence_similarity 同款"异常即零"（utils/utils.py:163-187）。

**不可答判定**（utils/utils.py:189-224）：`is_unanswerable` 先精确匹配空值集合（""/n/a/na/none/null/unanswerable，utils/utils.py:205），再子串匹配十三条模式（not mentioned/insufficient/no information 等，utils/utils.py:209-222）。

**总入口**（utils/utils.py:226-333）：`calculate_metrics(prediction, reference, category)` 三段式——category 5 时指标塌缩为纯二值：预测被判"不可答"则全部指标给满（utils/utils.py:241-260），给出具体答案（视为幻觉）则全零（utils/utils.py:261-277）；空值短路全零（utils/utils.py:280-294）；正常路径算 exact_match（不区分大小写全等，utils/utils.py:301）、集合版 token F1（utils/utils.py:304-313）、再调齐五个单指标函数合并成十二键 dict（utils/utils.py:316-331）。**聚合函数**（utils/utils.py:335-375）：`aggregate_metrics` 对每指标出 mean/std/median/min/max/count，overall 加分 category 拆分——但 grep 全仓它**零调用方**，是导出即死公共 API（聚合逻辑实际由 locomo 跑分脚本自行完成）。

## 外部连接

被引仅 memory/evaluator.py:16、70 一线（Evaluator.evaluate_answer 每题调一次 calculate_metrics）；测试 tests/test_metric_resources.py:49 直接断言 calculate_sentence_similarity 行为（验证资源缺失时返回 0.8 之类约定的降级值）。图谱视角它是 evaluator 的专属叶子；口径上要注明：answer_formatter、test_harness 都不直接碰本文件，一切指标流经 evaluator 中转。反向依赖里 `memory.local_device`（utils/utils.py:2）决定 SBERT/BERTScore 跑在哪个设备——工具箱也参与设备的全局拓扑。

## 数据流

LoCoMo 一题的指标流：test_harness 拿到 predicted 与 qa.final_answer → evaluator.evaluate_answer → calculate_metrics(pred, ref, category)。category 非 5 时：两文本各自 simple_tokenize 成集合 → 交并算 F1 → ROUGE/BLEU 走库 → BERTScore 在全局锁内起一次 transformer 前向（utils/utils.py:147-149）→ METEOR 分词对齐 → SBERT 编码两句算余弦（utils/utils.py:179-183）→ 十二键合并返回。category 5 时短路：`is_unanswerable(predicted)` 一票定生死，命中全一、未命中全零——F1/BLEU 在对抗题上已不具备文本相似度语义，只是正确性的镜像。

配套流：Evaluator 同时把 prediction 交给 LLMJudge 打连续分（llm_judge_score），与这里的离散指标在 test_harness 的 result dict 汇合（memory/test_harness.py:413-414），构成"文本指标+模型评委"双轨评测。

## 设计决策

**category 5 塌缩规则**（utils/utils.py:238-277）是本文件最重要的语义决策：对抗题的"正确答案"是承认不可答，任何文本相似度指标在此都是噪声源，干脆用 is_unanswerable 一刀切成全一/全零。代价是分题型统计里 category 5 的 std/median 全部退化，且整个判定押在十三条子串模式的召回上——模式外的委婉拒绝（"the transcript does not say"）会被误判为幻觉零分。**双检锁懒加载**（utils/utils.py:79-91）把"重型模型只在首次使用时进内存"做到进程级，两把锁分别守护 SBERT 加载与 BERTScore 前向，是并行测试（test_harness 的 ThreadPoolExecutor 路径）能安全共用的前提。**异常即零**的一致风格（utils/utils.py:155-161、168-170、185-187）保证缺任何依赖时跑分不中断，指标悄悄归零。

批判点：其一，**不可答判定双实现口径分裂**——本文件 is_unanswerable（utils/utils.py:189-224）与 memory/llm_judge.py:93 起的 `_is_unanswerable` 逻辑同源复制（同样的空值集合与模式表），改词表必须两处同步，否则 category 5 的指标轨与评委轨会给出矛盾的"幻觉"判定；其二，BERTScore 全局锁是并行评测的串行热点——每个答案一次锁内前向（utils/utils.py:147-149），test_questions_parallel 三 worker 时指标计算退化为单线程排队，跑分加速比被这把锁吃掉一截；其三，best-of-N 的 f1 机制（memory/test_harness.py:167-181）用裸 `.split()` 分词，与本文件 simple_tokenize 的去标点版本（utils/utils.py:94-98）是两套 token 口径，同一答案两处 F1 不等值；其四，aggregate_metrics 全零消费（utils/utils.py:335-375）加 openai/locomo 两组死 import（utils/utils.py:45-55），说明本文件经历过"从大杂烩向纯指标"的瘦身但没剪干净。

## 新人提示

先读 calculate_metrics 的三段式主干（utils/utils.py:226-333），对照 category 5 分支理解"指标塌缩"的评测语义；再读 `_get_sentence_model`（utils/utils.py:79-91）看双检锁加"失败永久放弃"的取舍。

四个常见误解：以为十二个指标相互独立——category 5 下它们全是一个二值判定的复读（utils/utils.py:241-277）；以为指标缺失会报错——一切异常静默归零，跑分 json 里全零行既可能是真差也可能是 bert_score 没装（utils/utils.py:155-161）；以为改 is_unanswerable 词表只改一处——llm_judge.py 有一份复制实现，必须同步；以为 aggregate_metrics 是跑分聚合入口——没人调它，真正的聚合在 benchmarks 脚本里另写（utils/utils.py:335-375）。
