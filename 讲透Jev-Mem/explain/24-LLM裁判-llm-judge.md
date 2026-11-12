> 标题：LLM 裁判——连续语义评分与离线重评 CLI · 源文件：memory/llm_judge.py（231 行）· 图谱标签：评测与答案质量模块

## 角色定位

评测与答案质量模块的核心打分器：LLM-as-judge，把生成答案与 gold answer 对比，给零到一的连续语义分（非二值），并带一句评分理由。双面身份：一面是 `LLMJudge` 类，被 memory/evaluator.py:17 导入、:40 实例化，成为 benchmark 默认裁判（jev_mem/benchmarks/locomo.py:91 与 602 都以 use_llm_judge=True 装配 Evaluator）；另一面是模块级 CLI main（memory/llm_judge.py:160-228），对已落盘的结果 JSON 批量重评——换裁判口径重跑打分而不重建记忆图，与 benchmark 的 score_only_mode（jev_mem/benchmarks/locomo.py:64）同一思路。

两套评分制并存：category 五（对抗题，问记忆里没有的事）走规则二值裁（memory/llm_judge.py:73-85），其余 category 走 LLM 连续分。这是全仓所有 headline 数字的最终出处——avg_llm_judge、分类分表全部由它供分。

## 内部结构

- 模块级状态：import 即 `dotenv.load_dotenv()`（memory/llm_judge.py:10，副作用在导入时发生）；全局懒加载 OpenAI client（12，137 行构造，吃 OPENAI_API_KEY 与可选 OPENAI_BASE_URL）。
- `ACCURACY_PROMPT`（14-44）：六级评分量规 1.0/0.8/0.6/0.4/0.2/0.0 各配语义描述（18-23）；时间题宽大处理——日期格式差异不扣分、时期错位才扣（27-30）；事实题看语义等价与实体关系保真（32-35）；输出契约 JSON 带 score 与 reasoning（41-43）。
- `LLMJudge` 类（46-126）：
  - `__init__` 收 llm_controller 参数然后不用（52-57，docstring 自认 "not used, uses global client"）
  - `evaluate_answer`（59-91）：category 五短路进 `_is_unanswerable` 判定——识别为不可答得满分、答了则零分（73-85）；否则委托 evaluate_llm_judge（87），返回 score 加一句程式化 reasoning（88-91）
  - `_is_unanswerable`（93-126）：空串与 na/none/null 集合（108）加十三条子串模式（111-124，"not mentioned"/"no information" 等），any 命中即判不可答
- `evaluate_llm_judge`（128-158）：模块级函数，system 角色声明连续打分专家（142-144）、user 填 prompt（146-150）、response_format 定 json_object（152）、temperature 零（153）、模型名硬编码 gpt-4o-mini（139）、解析后钳位到区间（157）。
- `main`（160-228）：argparse 单参数 --input_file 默认 results/default_run_v4_k30_new_graph.json（162-169）；逐条跳过 category 五（189-191）；打分入 LLM_JUDGE 分类桶（195）与 RESULTS 外层索引桶（198-206）；每答一题就全量重写输出文件（209-210）并打印各 category 当前均分（212-217）；外层循环末尾 index 加一（218）；终局再写一次文件并打印汇总（221-228）。

## 外部连接

import：argparse/json/collections 标准库（1-3）、numpy 供均分（5）、openai 官方 SDK（6）、dotenv（8-10）。仓内被引只有两处（grep 实测）：memory/evaluator.py:17 的类导入与 memory/__init__.py:25、69 的公开导出。其余大量出现的 `llm_judge_score` 键都是 evaluator 产出的下游传播，不回依赖本模块：memory/test_harness.py:145 与 344、414、491、560 的结果字典、jev_mem/benchmarks/locomo.py 的指标聚合（158、167、648、658 等）、jev_mem/benchmarks/longmemeval.py:2106-2117 的自有一套打分。外部依赖只有 OpenAI 兼容端点（137 行的环境变量对）。CLI 无注册入口，手动 `python memory/llm_judge.py --input_file ...` 调用。

## 数据流

在线主链：TestHarness/Evaluator 调 `LLMJudge.evaluate_answer`（59）→ category 五走规则路（74-85，零 API 调用）或其余走 `evaluate_llm_judge`（87）→ OpenAI 调用（138-154）→ 分数回到 evaluator 写进 llm_judge_score/llm_judge_reasoning 键（memory/evaluator.py:88-89）→ evaluator 聚合 avg_llm_judge（evaluator.py:151-160）→ benchmark 结果 JSON。best-of-N 择优同样消费这条链的分数（memory/test_harness.py:139-145）。

离线旁链：结果 JSON（question/answer/response/category 结构）→ main 逐条过滤 category 五（189-191）→ evaluate_llm_judge 重打分（194）→ 双 defaultdict 累积（195-206）→ 每步全量落盘（209-210）。注意离线链**不经过** LLMJudge 类的 category 五规则——main 直接 skip（190），两处 category 五逻辑口径独立维护。

## 设计决策

**category 五走规则不走 LLM**（73-85）是对的：对抗题的正确行为是"承认不知道"，用 LLM 判"是否承认不知道"既绕又贵还不可靠；十三条子串模式（111-124）便宜且可预测，二值满分层也符合该题型无中间态的本质。

**批判五处**。其一，**reasoning 被丢**：prompt 明确要求裁判返回 reasoning 字段（43），evaluate_llm_judge 解析时只取 score（155-158），LLMJudge.evaluate_answer 再编一句"Continuous LLM judge score" 的程式化理由（90）——裁判的真实解释从未上浮，低分case 无从诊断，这是死数据与可观测性双输。其二，**裁判模型硬编码 gpt-4o-mini**（139）：生成模型可以 --model 换、裁判不能；换裁判只能改源码，而裁判口径变了所有历史分数可比性作废，这个隐含常数没有任何运行时信号。其三，**llm_controller 形参纯装饰**（52-57）：evaluator.py:40 认真传了 controller 进来，构造器收下即弃，实际用全局 client——依赖注入的假象，测试想替身都替不进去。其四，**main 的每题全量重写**（209-210）：N 题写 N 次全文件，平方级字节开销——作为断点续跑的廉价保险可以理解（Ctrl-C 后中间结果还在），题量上千就疼。其五，**子串误判**（111-126）：答案正文含 "unknown"（如引用"an unknown species"）即被判不可答、category 五直接满分（74-79）——子串匹配没有词边界。

**值得肯定**：temperature 零加 json_object 双保险压裁判抖动（152-153）；分数钳位防模型越界（157）；时间题宽大指令（27-30）贴合 LoCoMo 时间类题的表述方差；空串与显式 NA 集合兜底（108）。

## 新人提示

先读 14-44 的 prompt——它是裁判的全部人格，六级量规的语义边界就是所有分数的口径定义；再读 59-91 看两条评分路怎么分叉。切换裁判端点用环境变量：OPENAI_BASE_URL 指向兼容端点即可（137），模型名那处必须改 139 行源码。给不可答模式表加新短语改 111-124，保持小写子串风格；动 category 编号时回查两处独立口径（73 的短路、190 的 skip）。跑离线重评：`python memory/llm_judge.py --input_file results/你的结果.json`，输出落在同目录 llm_judge_ 前缀文件（173）；记得它会跳过 category 五，别指望离线链出对抗题分数。调试低分时不要指望 reasoning 字段——它没被保留（155-158），要诊断就得手工重放 prompt。最后记住依赖关系：本模块被 evaluator 单点持有，任何 benchmark 分数异常先查 evaluator.py:81-92 的调用与 137 行的端点环境，再怀疑裁判本身。
