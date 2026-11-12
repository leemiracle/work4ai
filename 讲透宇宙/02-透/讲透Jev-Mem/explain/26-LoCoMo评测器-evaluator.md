> 标题：LoCoMo 侧评测模块——Evaluator 指标聚合器精讲 · 源文件：memory/evaluator.py（208 行）· 图谱标签：评测层 / 中转枢纽

## 角色定位

LoCoMo benchmark 的评分中枢：把"单题判分"与"指标计算"从检索/生成流程中剥离出来，组成独立可复用的评测模块。模块头（evaluator.py:1-12）明确自定位 "Handles all evaluation and scoring operations independently from memory building and querying. This module can be used standalone for evaluating any QA system outputs"——它不关心答案从哪来，只负责三件事：单题多指标判分（evaluate_answer）、批量包装（evaluate_batch）、两层统计聚合（整体 + 按类别）。

它与 `memory/longmemeval_evaluator.py` 构成双评测器家族的两个分支：本模块服务 LoCoMo（连续 0-1 LLM judge + 词面指标双轨），那边服务 LongMemEval（二值 yes/no 单轨）。两套 judge prompt、两套分数语义并存是刻意的——各 benchmark 沿用各自社区的评测惯例，跨 benchmark 数字不可直接互比。

## 内部结构

- `__init__`（evaluator.py:28-43）：`llm_controller` 参数与 `use_llm_judge` 开关解耦——只有两者同时满足才挂 LLMJudge（evaluator.py:39-40），否则降级为 "metrics only"（evaluator.py:43 的日志分支）。llm_controller 实际只被透传，LLMJudge 内部并不真用它（见外部连接）
- `evaluate_answer`（evaluator.py:45-94）：单题判分。词面指标支线：gold_answer 非空才计算 `calculate_metrics(predicted, str(gold), category=question_category)`（evaluator.py:69-75），exact_match 直接充当 is_correct（evaluator.py:76）；gold 缺失则 metrics=None、is_correct=False（evaluator.py:77-79）。judge 支线：三条件（use_llm_judge 且 llm_judge 存在且 gold 非空）才调用（evaluator.py:81-87），取 score 与 reasoning（evaluator.py:88-89），否则两个零值占位（evaluator.py:90-92）
- `evaluate_batch`（evaluator.py:96-129）：categories 缺省补 None 列表（evaluator.py:115-116），四元 zip 逐题调 evaluate_answer 并把 question/gold/predicted/category 原样回填进结果字典（evaluator.py:119-127）——聚合与留档一体
- `compute_aggregate_stats`（evaluator.py:131-163）：空表守卫（evaluator.py:141-142）；correct 按 is_correct 计数（evaluator.py:145）；三个列表推导分别抽 f1/bleu1/llm_judge_score（evaluator.py:147-152）；产出 total/correct/accuracy/avg_f1/avg_bleu1/avg_llm_judge 六键统计（evaluator.py:154-161），全部乘一百转百分数（evaluator.py:157-160）
- `compute_category_stats`（evaluator.py:165-208）：函数体内才 import defaultdict（evaluator.py:175）；defaultdict+lambda 建五槽累加器（evaluator.py:177-179）；逐结果按 category 分桶累加 total/correct/f1/bleu1/llm（evaluator.py:181-193）；收尾逐桶算同款六键统计（evaluator.py:195-206）

## 外部连接

import（evaluator.py:14-17）：`utils.utils.calculate_metrics` 是词面指标的真正实现（函数在 utils/utils.py:226，其中 utils/utils.py:241 起有 LoCoMo Category 5 对抗题的特殊处理——预测"不可回答"即判满分，这正是 12 篇讲过的去 Cat5 口径的机制源头）；`.llm_judge.LLMJudge`（类在 memory/llm_judge.py:46）提供连续判分，其 ACCURACY_PROMPT（memory/llm_judge.py:14）规定 0.0-1.0 六档语义等价评分并对时间类问题放宽日期格式。fanOut 实测仅两处，都是惰性导入：jev_mem/benchmarks/locomo.py:72（score_only_mode 分支）与 jev_mem/benchmarks/locomo.py:434（main 分支）。tests/ 目录无直接 import（grep 实测为零）——本模块的测试覆盖完全经由 locomo runner 间接达成。

## 数据流

一次 `jev-mem-eval` 跑题循环里，每道 QA 走完整链：

1. TestHarness 拿到检索上下文→LLM 生成 predicted→组 (question, gold, predicted, category) 调 evaluate_answer
2. 词面支线：calculate_metrics 算出 exact_match/f1/bleu1 全家桶（Cat5 题走特殊口径）；judge 支线：LLMJudge 按六档 rubric 给 0-1 连续分并留 reasoning 一句话
3. 结果字典逐题 append 进列表，题跑完交给 compute_aggregate_stats 出总表、compute_category_stats 出五类分表
4. `--score-only` 复评时（locomo.py:72 惰性导入即此分支）重跑第 2 步换 judge 模型，词面指标不变——换 judge 零检索成本的机制基础

注意聚合口径的镜像性：is_correct 只认 exact_match（evaluator.py:76），而 avg_llm_judge 是连续分均值——同一份结果里 accuracy 与 avg_llm_judge 天然不同轴（一个严苛词面一个宽松语义），报告时两者并列正是 LoCoMo 论文惯例。

## 设计决策

**三层降级设计**是本模块的骨架：无 gold→metrics 置 None（evaluator.py:78）；无 judge→llm_judge_score 置零（evaluator.py:91）；有 judge 无 controller→构造期就退化为 metrics only（evaluator.py:42-43）。任何一层缺失都有确定性行为，评测流水线不会因组件缺位而崩。

批判性发现两处：①`compute_aggregate_stats` 的 judge 分抽取（evaluator.py:151-152）条件用 `r.get('llm_judge_score', 0) >= 0`——对 0-1 分数域这是恒真过滤器（no-op），而循环体却用 `r['llm_judge_score']` 直接索引：条件与取值不对称，一个缺该键的字典会先通过条件再抛 KeyError。同函数的 f1/bleu1 抽取（evaluator.py:147-150）都老实用 `.get` 判键存在，唯独 judge 分这行埋雷；从外部 JSON 加载历史结果复评时若字段不全即触发。②`compute_category_stats` 的 `cat = r.get('category', 0)`（evaluator.py:182）默认值 0 永远不生效——evaluate_batch 回填的 category 键必然存在（evaluator.py:126），值为 None 时分桶键就是 None，JSON 序列化后变成字符串 "null" 桶而非默认类别零桶；`.get(default)` 形似防御实不设防。另有一处口径分裂需钉版：单题 metrics 是 0-1 小数、聚合统计乘一百变百分数（evaluator.py:157-160），同一字段两种量纲，二次聚合（多样本平均）时若把聚合值再当小数用必错。

## 新人提示

按 evaluate_answer→compute_aggregate_stats→compute_category_stats 顺序读（evaluator.py:45、131、165），三个方法就是数据流的三个阶段。calculate_metrics 的 Cat5 特殊分支在 utils/utils.py:226 起的实现必读——不理解"对抗题答不知道=满分"就不理解 LoCoMo 报表的 with/without 双口径从哪来。

三个坑：给聚合函数喂外部 JSON 结果前先验 `llm_judge_score` 键齐全（evaluator.py:151 的直接索引不设防）；比较两次实验时确认比的是同轴数字（accuracy 是词面 exact match，avg_llm_judge 是语义连续分，别混）；想让 judge 生效必须同时给 llm_controller 且 use_llm_judge=True（evaluator.py:39 的与门），只传一半会静默降级到 metrics only——日志里那句 "without LLM judge" 是唯一提示。
