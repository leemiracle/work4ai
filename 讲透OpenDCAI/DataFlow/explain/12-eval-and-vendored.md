# 12 · 评估算子线与 vendored 代码：task2vec、bench 与教科书分

## 一、角色定位

本篇收束 DataFlow 评测体系的两翼：**数据集级评估器**（不产行级标注，输出数据集整体指标）与**vendored 科研代码**（从论文/公司项目整体拷入的成品实现）。主角四人：`general_text/eval/task2vec/` 三件套（Amazon task2vec 衍生，含 LLM 化改造）、`task2vec_dataset_evaluator.py`（论文 Beyond Scale 的多样性系数落地，文件头注释 L12-13 自引）、`core_text/eval/bench_dataset_evaluator.py`（bench 答案对错判定）、`text_pt/eval/textbook_sample_evaluator.py`（FastText 教科书质量打分）。它们共同构成"训练前数据勘探"工具箱：多样性（task2vec/vendi）、教育价值（textbook）、下游答案正确率（bench）。

## 二、内部结构

**task2vec vendored 三件套**：`task2vec.py`（Amazon 版权头 L1-11，Apache 2.0）是 Fisher 信息矩阵对角嵌入的实现，仓内改造点带 `## LLM DIV` 标记（L28 set_seed、L36 get_loss 支持自回归交叉熵、L91 method 参数）——探针网络从图像 CNN 换成了 GPT-2 类语言模型，`Embedding` 类持有 FIM 对角线（L50-60）；`utils.py` 是 AverageMeter/调度器等训练辅件；`task_similarity.py` 同为 Amazon 版权（L3-13），提供 pdist/cdist/距离统计等 33 个导出函数。

**Task2VecDatasetEvaluator**（task2vec_dataset_evaluator.py:15-98）：构造时下载 GPT2 tokenizer+LMHead 探针（L28-29）；`get_score`（L72-89）做 sample_nums 轮随机采样，每轮 `Task2Vec(self.probe_network, method=self.method).embed(tokenized_dataset)`（L81）得嵌入，最后 `task_similarity.pdist(embeddings, distance='cosine')` + `stats_of_distance_matrix` 出多样性系数与置信区间（L83-84）。

**BenchDatasetEvaluator**（bench_dataset_evaluator.py:24-60）：`compare_method` 二选一（L27）——`match` 走符号级数学比对：`math_verify_compare`（L54-60）用 `math_verify.parse/verify`（L10 导入）先 str 包装再裸值双 fallback；`semantic` 走 LLM 裁判：AnswerJudgePrompt 生成判词，`ResolveResponse`（L64-75）正则抽 `judgement_result: true/false`、抽不到就整串猜 true。结果落 JSON 报告并统计 accuracy（L122-129）。

**TextbookSampleEvaluator**（textbook_sample_evaluator.py:13-99）：从 HF Hub 拉 `kenhktsui/llm-data-textbook-quality-fasttext-classifer-v2`（L17-21），FastText 三分类 Low/Mid/High 映射 1.0/3.0/5.0（L29-33），`_score_func`（L71-82）按预测概率加权得连续分。

## 三、外部连接

vendored 代码的"外来性"是双刃：好处是学术实现即拿即用，坏处是与仓内规范脱节——task2vec 三件套不进 OPERATOR_REGISTRY、不走 OperatorABC，仅被 evaluator 当库调用（L1-2 相对导入）。Bench 评估器则是规范内公民：`@prompt_restrict(AnswerJudgePrompt)`（bench L18-19）+ 注册表，上游接 `BenchAnswerGenerator`（生成待评答案），下游报告路径默认 `result_bencheval/BenchDatasetEvaluator_result_<时间戳>.json`（L31-32）。textbook 评估器在 text_pt 域与 `text_book_filter.py` 成对（打分-筛除模式）。

## 四、数据流

task2vec 线：DataFrame 单列文本 → tokenize 成批（evaluator L67-70）→ 逐轮采样嵌入 → 余弦距离矩阵 → (div_coeff, conf_interval) 字典返回，不写 storage。bench 线：DataFrame 双列（预测答案/标准答案）→ 逐行 compare → `answer_match_result` 布尔列（L148）+ 数据集级 accuracy 汇总 JSON。textbook 线（设计意图）：文本列 → 逐行 FastText 分 → 分数列 TextbookScore——但实际跑不完，见下节。

## 五、设计决策（含批判）

**三条硬核勘误，全部源码实证**：

1. **task2vec 的 variational 方法是必炸选项**：`task2vec.py` 的 `variational_fisher`（L346-352）调用 `variational.make_variational`/`get_variational_vars`（另 L327 `get_compression_loss`），但**全文件从未 import `variational` 模块**（L13-26 的 import 清单里没有）——选择该方法即 NameError。构造器 `assert method in ('variational', 'montecarlo')`（L98）和 evaluator 侧白名单 `['montecarlo', 'variational']`（evaluator L26-27）却双双放行，参数校验形同虚设。上游 Amazon 原版里 variational 是独立包依赖，vendored 时被裁掉但方法入口没删。
2. **textbook 评估器的 get_desc 自曝两连 bug**（这是全仓罕见的"文档比代码诚实"案例）：中文描述 L49-50/英文 L63-64 明写——① run() 以三参调 `self.eval(dataframe, input_key, output_key)`（L96），而 `eval` 签名只收两参（L84），必 TypeError、零数据写入；② 即便修好参数，L97-98 的循环把每行的单元素分数数组赋给**整列** `dataframe[output_key]`（既没用 `.iloc[i]` 定位行，又赋 list），多于一行 pandas 直接 ValueError。也就是说这个算子当前一次也没法成功跑完，而 get_desc 把这事写进了官方描述——要么是修复 PR 的半成品文档先行，要么是有意留档待修。
3. **bench 的 semantic 裁判兜底过于激进**：`ResolveResponse` 抽不到 `judgement_result` 字段时退化为"整串包含 true 即真"（L71-74），LLM 输出格式稍漂移就可能把含"not true"字样的判词误读为对。

设计层面正面一条：match/semantic 双模（bench L40-52 按模式装配不同组件）让"有标准答案走符号比对、无标准答案走裁判"在一个算子里切换，`self.compare` 的方法引用装配是干净的条件策略模式。

## 六、新人提示

用 task2vec 评估多样性时坚持默认 `montecarlo`，`variational` 在有人补上 variational 包依赖前是死路。跑 textbook 算子前先修两处：`eval` 加 `output_key` 形参（或 run() 去掉第三参），L97-98 改为按行赋值（`dataframe.loc[i, output_key] = score_list[0]`）。读 vendored 目录记住铁律：**别假设它们遵循仓内规范**——无注册表、无 storage、异常处理自成一体；升级 task2vec 时优先对照上游 Amazon 仓库而非本仓惯例。审 bench 结果时 semantic 模式的分数建议抽查原始判词，ResolveResponse 的宽松兜底会平滑掩盖格式错误。
