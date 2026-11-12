> 标题：最佳答案选择器——best-of-N 择优精讲 · 源文件：memory/best_of_n_selector.py（300 行）· 图谱标签：评测与答案质量模块

## 角色定位

评测链路里的"答案质量放大器"：每道题生成 N 次而非一次，再按 llm_judge 得分 / 多数投票 / 置信度代理三种策略择优。模块头（memory/best_of_n_selector.py:1-9）交代动机——LLM 回答有方差，best-of-N 缓解抖动、提升 multi-hop 准确率。它属于"评测与答案质量模块"层，与 LLMJudge（精讲 24）、TestHarness 同族，只服务 benchmark 打分，不参与线上记忆读写。

必须先钉一个事实：本模块在主评测路径上是**装配未用**的。benchmark 确实在 jev_mem/benchmarks/locomo.py:610 惰性导入、jev_mem/benchmarks/locomo.py:614 实例化并挂到 `tester.best_of_n_selector`，但真正执行 best-of-N 的循环在 memory/test_harness.py:115 的 `_answer_question_best_of_n` 里**内联重写了一遍**，从未调用本模块任何方法——test_harness.py:76 只用 `hasattr(self, 'best_of_n_selector')` 当开关判据。所以这是一套自洽完整、当前无人消费的并行实现（详见设计决策）。

## 内部结构

- `BestOfNSelector`（best_of_n_selector.py:20）：构造器只收 `n_attempts`（默认三次）与 `selection_method`（best_of_n_selector.py:25-34）。
- `get_best_answer`（best_of_n_selector.py:36-121）主循环：逐次调 `answer_generator(question)` 并计时（best_of_n_selector.py:65-67）；三种返回形态归一化——tuple 取 answer/context、dict 取 answer 键、其余 str 化（best_of_n_selector.py:70-78）；评分分支（best_of_n_selector.py:81-88）method 为 llm_judge 时调 `evaluator.evaluate_single`（best_of_n_selector.py:85）、否则 `calculate_f1`（best_of_n_selector.py:88）；每次尝试记录 attempt/answer/score/time/metadata（best_of_n_selector.py:90-96），异常被宽 except 吞成零分占位（best_of_n_selector.py:98-106）；收尾把 all_answers/all_scores、均值、标准差塞进 statistics（best_of_n_selector.py:112-119）。
- `_select_best`（best_of_n_selector.py:123-157）纯函数三策略：llm_judge 取最高分（best_of_n_selector.py:137-139）；voting 用 Counter 对答案做精确字符串多数投票、同票再比 score（best_of_n_selector.py:141-148）；confidence 拿答案长度当置信度代理与分数相乘（best_of_n_selector.py:150-153）；未知 method 落默认最高分（best_of_n_selector.py:155-157）。
- `_calculate_std`（best_of_n_selector.py:159-166）手写总体标准差。
- `CachedBestOfNSelector`（best_of_n_selector.py:169-216）：命中缓存直接返回（best_of_n_selector.py:190-196），未命中走父类再写入（best_of_n_selector.py:199-204）；缓存键是 `question|expected` 的 MD5（best_of_n_selector.py:208-211，显式 usedforsecurity=False）；`clear_cache`（best_of_n_selector.py:213-216）。
- `create_robust_answer_generator`（best_of_n_selector.py:219-301）工厂：返回 generate_answer 闭包（best_of_n_selector.py:233）；内嵌 answer_gen 走查询、上下文格式化、生成、category 五对抗校验（best_of_n_selector.py:240-255）；内嵌 SimpleEvaluator 手写 F1（best_of_n_selector.py:258-278）；最终把结果展平成 benchmark 友好 dict（best_of_n_selector.py:289-299）。

## 外部连接

import 仅标准库（logging/time/typing/collections/hashlib，best_of_n_selector.py:11-15）——零仓内依赖、零 LLM 依赖。被引关系（grep 全仓实测）：唯一消费方是 jev_mem/benchmarks/locomo.py:610 的惰性导入与同文件 614 行的实例化；memory/test_harness.py:76 引用了它挂载的属性名但不调方法。`CachedBestOfNSelector` 与 `create_robust_answer_generator` 在仓内**零调用方**。tests/ 目录没有任何文件引用本模块——零测试覆盖。

## 数据流

设计中的数据流（模块自身视角）：question → answer_generator 生成 N 份答案与元数据 → evaluator 逐份打分 → `_select_best` 择优 → 返回携带 statistics 的最佳尝试字典（best_of_n_selector.py:109-121）。

实际生效的数据流（benchmark 视角）：`--best-of-n` 大于一时（jev_mem/benchmarks/locomo.py:609 判定），jev_mem/benchmarks/locomo.py:612-618 把三个属性挂上 TestHarness；答题时 test_harness.py:76 的开关把请求转进 `_answer_question_best_of_n`（memory/test_harness.py:115）：N 次复用 `_answer_question_single`（test_harness.py:127），全错短路（test_harness.py:134-135），llm_judge 分支改调 `evaluator.evaluate_answer` 取 llm_judge_score（test_harness.py:139-145），voting 分支现场 Counter 投票（test_harness.py:157-160）。本模块的 get_best_answer 在主路径上一次都没跑。

## 设计决策

**休眠的并行实现**是最大的工程问题。三套择优逻辑并存且互不一致：本模块、TestHarness 内联版（memory/test_harness.py:115-160）、以及 jev_mem/benchmarks/locomo.py:393-395 CLI 暴露的 `--best-of-n-method`（choices 为 llm_judge/voting/f1）。口径分裂一：模块支持的第三种方法是 `confidence`（best_of_n_selector.py:31），CLI 根本选不到；CLI 的 f1 落进模块 default 分支（best_of_n_selector.py:155-157）纯属巧合等价。口径分裂二：模块 llm_judge 分支调 `evaluator.evaluate_single`（best_of_n_selector.py:85），而标准 `Evaluator` 没有这个方法（只有 evaluate_answer；名字最接近的是 memory/longmemeval_evaluator.py:99 的 evaluate_single_response）——真接回主路径会当场 AttributeError，说明模块早已与消费方漂移。

**两处潜伏 bug**：其一在工厂闭包（best_of_n_selector.py:244-255）——`formatted_context` 只在 anchor_nodes 非空分支赋值，若 context 真值但锚点为空，best_of_n_selector.py:255 引用未绑定变量直接 UnboundLocalError；且三元表达式因优先级只作用于元组第二元素，守卫判的还是错的对象（该判 anchor_nodes 而非 context）。其二在评分前置（best_of_n_selector.py:82）：expected_answer 为 None 时整轮不打分，voting/confidence 退化为纯字符串/长度比较，调用方无任何提示。

**值得肯定**：statistics 保留全部 all_answers/all_scores（best_of_n_selector.py:117-118）供事后分析方差；标准差给出答案稳定性度量；MD5 键显式声明非安全用途（best_of_n_selector.py:211）。**批判**：缓存是无界 dict（best_of_n_selector.py:176 与 204），对比 jev_client.py:199-204 的 OrderedDict LRU 上限，长 benchmark 有内存增长风险；voting 用精确字符串相等（best_of_n_selector.py:143-144），LLM 措辞差异让多数票几乎永不聚拢；confidence 拿长度当置信度（best_of_n_selector.py:150-153）等于奖励啰嗦与幻觉，注释自认是 proxy。

## 新人提示

先读 `_select_best`（best_of_n_selector.py:123-157）——纯函数、三分支一目了然，是全模块唯一值得单独测的单元；再读 `get_best_answer`（best_of_n_selector.py:36-121）。三个常见误区：看到 jev_mem/benchmarks/locomo.py:614 实例化就以为本模块在跑——真正执行体在 test_harness.py:115，改择优逻辑请改那边或改接线；想复用本模块跑 llm_judge 择优——先补 best_of_n_selector.py:85 的 evaluate_single 缺口；想读工厂闭包——注意 best_of_n_selector.py:255 的未绑定变量雷。成本提醒：best-of-N 是 N 倍检索加 N 倍生成的刷分机制，消融对比两侧必须同 N 同方法，否则结论无效。
