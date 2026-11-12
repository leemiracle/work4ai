> 标题：LongMemEval 专用 LLM 评测器——题型感知 judge 精讲 · 源文件：memory/longmemeval_evaluator.py（210 行）· 图谱标签：评测层 / 叶子模块

## 角色定位

Jev-Mem 双评测器家族中的 LongMemEval 侧裁判：用 LLM 对 LongMemEval 基准的问答对做 yes/no 判分，核心卖点是**题型感知**——不同 question_type 配不同评分 rubric。模块头（longmemeval_evaluator.py:1-6）自述 "Evaluates answers using question-type-specific prompts following LongMemEval standards"：四套 prompt 模板复刻 LongMemEval 论文官方评测口径（temporal-reasoning 容忍 off-by-one、knowledge-update 只认更新后的答案、preference 用 rubric 而非标准答案），这使 Jev-Mem 的 LongMemEval 分数与社区基线可比。

与 LoCoMo 侧的 `memory/evaluator.py` 是平行关系不是替代关系：LoCoMo 侧是"指标计算 + 连续 0-1 LLM judge"双轨，本文件是"纯 LLM 二值 judge"单轨，且自带 OpenAI client 不依赖 LLMController——一条刻意独立、可单独抽走的评测支线。

## 内部结构

- `__init__`（longmemeval_evaluator.py:18-26）：默认 judge 模型 gpt-4o-mini；`OpenAI(base_url=os.getenv("OPENAI_BASE_URL") or None)`（longmemeval_evaluator.py:26）支持用环境变量切兼容端点，`load_dotenv()`（longmemeval_evaluator.py:13）在 import 时就执行
- 四套 prompt 模板，全部 `{question}/{gold_answer}/{response}` 三占位符：
  - `TEMPORAL_REASONING_PROMPT`（longmemeval_evaluator.py:29-43）：关键条款在 longmemeval_evaluator.py:30——天数 off-by-one 不扣分（答 19 天真值 18 天仍算对）、包含中间步骤也算对、只答出部分信息算错
  - `KNOWLEDGE_UPDATE_PROMPT`（longmemeval_evaluator.py:45-59）：longmemeval_evaluator.py:46 规定回答里混着旧信息没关系，只要含更新后的正确答案即算对
  - `SINGLE_SESSION_PREFERENCE_PROMPT`（longmemeval_evaluator.py:61-75）：占位符标签换成 `<RUBRIC>`（longmemeval_evaluator.py:67），gold_answer 位置放的是期望回应的评分要点而非事实答案；longmemeval_evaluator.py:62 说明不必覆盖 rubric 全部要点
  - `DEFAULT_PROMPT`（longmemeval_evaluator.py:77-97）：兜底模板，longmemeval_evaluator.py:78-84 是一组宽松判分指引（主事实内容命中即 yes，冠词/大小写/附加上下文不影响，只有事实错误或完全缺失才 no）——这是本仓自加的宽松化，非 LongMemEval 原文
- `evaluate_single_response`（longmemeval_evaluator.py:99-158）：判分主路径。固定 system prompt（longmemeval_evaluator.py:113）；四路 if/elif/else 选模板（longmemeval_evaluator.py:115-130）；调 chat.completions，temperature=0、max_tokens=10（longmemeval_evaluator.py:133-141）——只为拿一个 yes/no，token 成本压到最低；解析 `result_text == 'yes' or result_text.startswith('yes')`（longmemeval_evaluator.py:143-144）映射为 is_correct 与 0/1 score
- `evaluate_answer`（longmemeval_evaluator.py:160-189）：**兼容接口垫片**——签名对齐 `memory/evaluator.py` 的同名方法（longmemeval_evaluator.py:163 注释明言 "compatible interface with existing Evaluator"），内部转发 evaluate_single_response（longmemeval_evaluator.py:174-179），返回结构里把 accuracy/f1/bleu1 三个 metrics 全部塞同一个 judge 分（longmemeval_evaluator.py:184-188）
- `get_question_type_category`（longmemeval_evaluator.py:191-210）：七种题型到可读名称的映射表（longmemeval_evaluator.py:201-209），未命中原样返回（longmemeval_evaluator.py:210）

## 外部连接

import（longmemeval_evaluator.py:8-13）：os/typing/OpenAI/dotenv 四样，零仓内依赖——评测支线的独立性即由此来。fanOut 仅 grep 实测两条：`jev_mem/benchmarks/longmemeval.py:31` 的 import 与 `jev_mem/benchmarks/longmemeval.py:75` 的实例化；另有 `public-release-files.txt:63` 把它列入公开发布清单。图谱若显示更大 fanIn 属口径差——`get_question_type_category` 与 `evaluate_answer` 在仓内均无其他调用点（实测 grep 全仓仅上述两行）。

## 数据流

设计中的完整链路：LongMemEval benchmark（jev_mem/benchmarks/longmemeval.py）加载问题→按 question_type 分流→每题把 (question, answer, model_response, question_type) 四元组送 evaluate_single_response→judge LLM 输出 yes/no→is_correct 与 1.0/0.0 分数进结果 JSON。

实际现状（关键发现）：**`self.evaluator` 在 jev_mem/benchmarks/longmemeval.py 全文只出现一次（第 75 行的构造），此后零调用**。benchmark 真正的判分走的是另外两条路：主循环用 `self.evaluate_lenient`（宽松字符串匹配，jev_mem/benchmarks/longmemeval.py:1058 定义、2103-2107 调用），题型特化 judge 走类内方法 `evaluate_with_llm_judge`（jev_mem/benchmarks/longmemeval.py:1188 起，1199/1219/1241/1260 四分支）——后者与本文件四模板高度同源但自成一份实现。所以本模块目前是"建好了裁判席、裁判没上场"的状态：构造即闲置，每次 benchmark 初始化白白实例化一个 OpenAI client。

## 设计决策

**题型 rubric 分化**是本文件的全部价值所在：temporal 的 off-by-one 豁免（longmemeval_evaluator.py:30）与 knowledge-update 的"旧信息不惩罚"（longmemeval_evaluator.py:46）都是 LongMemEval 官方口径，直接决定分数能否与论文基线对表。**metrics 伪造垫片**（longmemeval_evaluator.py:184-188）是激进选择：让下游聚合代码（期待 metrics.f1/metrics.bleu1 结构的）无改动跑通，代价是这三个数字语义全部退化为 judge 二值分——任何把 LongMemEval 的 avg_f1 当真 F1 读的人都会被误导，报告口径时必须注明。

批判性发现三处：①解析式 `== 'yes' or startswith('yes')`（longmemeval_evaluator.py:144）前半子句恒被后半覆盖（startswith 蕴含 ==），且 startswith 会把 "yes, but actually no" 这类输出误判为对——宽松方向的偏差；②异常处理（longmemeval_evaluator.py:152-158）broad except 一把抓、print 不走 logger、API 失败一律记 0 分——限流抖动会直接压低总分且无重试无计数，跑大规模评测时这是最现实的分数污染源；③max_tokens=10（longmemeval_evaluator.py:140）对 reasoning 型 judge 模型可能截断到空输出（空串 != yes → 0 分），换 judge 模型时先小样本验证输出格式。

## 新人提示

先读四套模板正文（longmemeval_evaluator.py:29-97）——它们是 LongMemEval 论文评测协议的忠实拷贝，读模板等于读协议。再读 evaluate_single_response（longmemeval_evaluator.py:99-158）看判分闭环，最后看 evaluate_answer 垫片（longmemeval_evaluator.py:160-189）理解它如何伪装成 LoCoMo 评测器接口。

三个坑：想改判分口径时别只改这里——jev_mem/benchmarks/longmemeval.py:1188 的 evaluate_with_llm_judge 是平行的另一份实现，两处要同步；结果里 f1/bleu1 不是真指标（longmemeval_evaluator.py:184-188 的垫片），横向对比时只用 is_correct/llm_judge_score 字段；OPENAI_BASE_URL 环境变量（longmemeval_evaluator.py:26）会让 judge 静默走代理端点，复现实验时先确认它指向哪个服务。
