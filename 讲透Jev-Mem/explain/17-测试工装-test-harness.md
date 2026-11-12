> 标题：测试工装——TestHarness 精讲 · 源文件：memory/test_harness.py（631 行）· 图谱标签：评测子系统 / 测试执行层（QA 生成 + 结果取证）

## 角色定位

LoCoMo 跑分的现场指挥：驱动"检索→作答→评估→取证"四步流水，把每题结果落成结构化 record。文件头（memory/test_harness.py:1-10）钉死边界——只管 QA 生成与测试执行，**评估本身已剥离给独立的 Evaluator 模块**（memory/test_harness.py:9），这行注释是重构史化石：早期评估内联在 harness 里，拆分后降为纯执行器。

它是典型的"借器官"类：构造器（memory/test_harness.py:32-46）不建重资产——qa_llm 直接拿 memory_builder.llm_controller（memory/test_harness.py:43），answer_formatter 拿 memory_builder.answer_formatter（memory/test_harness.py:46）。好处是 QA 与建图共用模型端点与答案格式化纪律；代价是无法脱离 builder 独立构造（tests/test_jev_mem.py:736-745 实证）。

## 内部结构

单类 TestHarness，四组方法：

**参数与诊断组**：`retrieval_top_k`（memory/test_harness.py:48-52）按题型定召回深度——category 1 多跳给 30（或 jev_config.multihop_top_k），其余给 15（或 answer_top_k）；关键细节是仅当 `config.read_enabled` 才走配置值，读策略关闭时回落硬编码默认——Jev-Mem 消融开关在评测侧的投影。`retrieval_diagnostics`（memory/test_harness.py:54-61）静态方法算 evidence_recall（召回片段对金标证据的覆盖率），docstring 明言 "never used for selection"——只进报告不进检索参数，防"用测试集答案调系统"泄漏。

**作答组**：`answer_question`（memory/test_harness.py:63-79）是入口，用 hasattr 鸭子类型探测 best_of_n 属性决定走单次还是 N 选一——属性由 locomo 跑分脚本事后注入（jev_mem/benchmarks/locomo.py:612-616），非构造参数。`_answer_question_single`（memory/test_harness.py:81-113）：build_qa_prompt 组题面（memory/test_harness.py:88），text 格式 temperature 0.0 调 LLM（memory/test_harness.py:91-95），成功后向 Jev 审计通道 emit system_two_answer 事件、query_id 取问题 sha256 前 16 位（memory/test_harness.py:97-101）；随后 extract_answer 抽答案（memory/test_harness.py:104）、validate_adversarial_answer 对 category 5 做"不可答"校验（memory/test_harness.py:107），全链 try 包住、失败返回固定错误串（memory/test_harness.py:111-113）。`_answer_question_best_of_n`（memory/test_harness.py:115-188）串行生成 N 候选再择优：llm_judge 用 Evaluator 评分取最高（memory/test_harness.py:132-153）、voting 用 Counter 投票（memory/test_harness.py:155-161）、f1 用词元重叠打分（memory/test_harness.py:163-183），兜底取第一个非错误候选（memory/test_harness.py:185-188）。

**无 LLM 兜底组**：`_extract_answer_simple`（memory/test_harness.py:190-296）是纯正则抽取器，qa_llm 缺席时的防线。按疑问词分派：when 定位 DETAILED MEMORIES 段、抓 "Event dates mentioned" 的括号计算值（四种日期格式瀑布加去前导零，memory/test_harness.py:218-237）；who 抓人名/介词宾语（memory/test_harness.py:253-259）；where 抓介词后大写地点（memory/test_harness.py:261-264）；how many 抓数字（memory/test_harness.py:266-269）；what 词元重叠选句加表语正则（memory/test_harness.py:271-280），通用最大重叠兜底（memory/test_harness.py:282-294）。

**执行组**：`test_questions` 串行版（memory/test_harness.py:298-434）与 `test_questions_parallel` 并行版（memory/test_harness.py:436-631）。两版每题同构：定深度→查上下文→作答→打分→组 record（详见数据流）。并行版用 ThreadPoolExecutor（默认三 worker，memory/test_harness.py:445）加 threading.Lock 护住单元素列表计数器（memory/test_harness.py:455-460、494-503），单题异常返回降级 record（memory/test_harness.py:574-582）。

## 外部连接

上游两件：memory_builder（借 llm_controller 与 answer_formatter）、query_engine（query 接口）；横向 evaluator（evaluate_answer 返回 metrics/is_correct/llm_judge_score 三键）；下游是 jev_mem/benchmarks/locomo.py:606 实例化与 612-616 best_of_n 注入，tests/test_jev_mem.py:736-745 验证 top_k 与 diagnostics 契约。**口径分裂必须点名**：memory/best_of_n_selector.py:246-247 调 `test_harness._format_context` 和 `test_harness._generate_qa_answer`——这两个方法在 TestHarness 上**不存在**（grep 全文为空），且 create_robust_answer_generator 本身全仓零调用方，是一条双重死亡的幽灵适配路径，不要被它误导成"还有另一条作答流"。

## 数据流

以一题为例：`qa.category=2` → top_k=15 → query_engine 返回 (query_context, answer_context) → best_of_n 未注入走单次作答 → build_qa_prompt 拼题面 → LLM 温度零回答 → extract_answer 剥壳 → 对抗题校验 → evaluator 产出 metrics dict（F1/BLEU/ROUGE 来自 utils/utils.py 的 calculate_metrics）与 llm_judge_score。

最有工程味的是**错题取证流**：llm_score 低于阈值（memory/test_harness.py:356）时，harness 把 query_context.metadata 拷进 search_details（剔除过肥的 adaptive_params，memory/test_harness.py:360-361），再给前十个 anchor_node 造摘要——rank/node_id/node_type/score 加 80 字符截断（memory/test_harness.py:363-395），dia_id 缺失标 MISSING 或 SESSION 前缀（memory/test_harness.py:384-387），answer_context 只对错题保留（memory/test_harness.py:419-421）。"错题现场拍照"：对题只留元数据、错题带全量现场，跑分 json 不爆炸又能复盘。

## 设计决策

**评估与执行解耦**（memory/test_harness.py:28-29）让 Evaluator 可复用于任意 QA 输出。**duck-typing 注入而非构造参数**（memory/test_harness.py:76-77 + locomo.py:612-616）保持构造签名稳定，best-of-N 纯可选——但"注了 n 忘了 method"这类半配置会静默走兜底。**错题取证阈值化**折中体积与可复盘性。**best-of-N 串行生成**（memory/test_harness.py:121-127）简单可靠，代价 N 倍 LLM 时延（llm_judge 下评估也乘 N）。

批判点三处：其一，两版循环口径漂移——串行版节点摘要带 SESSION 回退与 NO_ATTRIBUTES 分支（memory/test_harness.py:384-392），并行版只剩 dia_id（memory/test_harness.py:538-541）；其二，串行版 424-426 算了 accuracy/avg_f1/avg_bleu1 三个死变量（postfix 只显 F1 与 LLM，memory/test_harness.py:428-431），并行版 609 的 accuracy 同样算而不用；其三，并行版注释宣称 "Collect results as they complete"（memory/test_harness.py:600），实际按提交顺序逐个 future.result() 阻塞收集（memory/test_harness.py:601-603），且多线程共享 query_engine 的线程安全性在本文件无保证。

## 新人提示

先读 retrieval_top_k 与 retrieval_diagnostics（memory/test_harness.py:48-61）——理解 Jev-Mem"读策略开关+防泄漏纪律"的最短路径；再顺着 test_questions_parallel 的 worker 闭包走一题的生命周期。

四个常见误解：以为 harness 负责打分——分数全部来自注入的 evaluator；以为 best_of_n 是构造参数——是事后属性注入，直接 new TestHarness 永远走单次作答（memory/test_harness.py:76-79）；以为 result dict 字段稳定——并行版错误分支缺 metrics/search_details 键（memory/test_harness.py:574-582），下游聚合要先 get 兜底；以为 `_extract_answer_simple` 是可选优化——它是 qa_llm 为 None 时的唯一作答路径（memory/test_harness.py:85-86），删掉它无模型跑分直接崩。
