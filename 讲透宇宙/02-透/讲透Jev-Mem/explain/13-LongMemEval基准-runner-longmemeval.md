> 标题：LongMemEval 基准 runner——按题构建记忆的巨型 harness 精讲 · 源文件：jev_mem/benchmarks/longmemeval.py（2333 行，全仓最大文件）· 图谱标签：benchmark / evaluation / entry-point / harness（file 度数 15）

## 角色定位

Jev-Mem 的第二个 benchmark 入口：LongMemEval。`pyproject.toml:31` 注册 console script `jev-mem-longmemeval`。与纯编排壳的 LoCoMo runner 相反：构建记忆、检索、抽 chunk、出 prompt、评分全部内联，单类 `ChunkedLongMemEvalTester`（longmemeval.py:37）占约 2000 行。

双面孔（longmemeval.py:2202）：带 `--jev-mem`/`--jev-config` 是 "Jev-Mem LongMemEval benchmark"，否则 "MAGMA baseline"——同一 runner 服务实验组与对照组，但两组代码路径完全不同。数据集结构与 LoCoMo 相反：每题自带专属 haystack 会话与金标会话标注 `answer_session_ids`（jev_mem/datasets/longmemeval.py:37、40）——后者是本文件最大的方法论争议点。

## 内部结构

`ChunkedLongMemEvalTester` 约 19 个方法，分六族：

- **装配**（longmemeval.py:40-78）：jev_config 非空时强制 message 级且无 episodes，否则 raise ValueError 并惰性导入 `LongMemEvalJevMemory`（longmemeval.py:58-61）；再装 LLMController（缺 OPENAI_API_KEY 即拒）。
- **事实/摘要启发式**（longmemeval.py:80-345）：`extract_user_facts` 五组正则抽教育/工作/地点/家人类事实（longmemeval.py:121-215，docstring 自称 80% accuracy 关键）；`create_comprehensive_session_summary` LLM 摘要加 TOPICS 前缀，失败退化为关键词拼接（longmemeval.py:294-345）。
- **记忆构建双路**：message 级（longmemeval.py:372-504）——每条消息经 `builder.trg.add_event` 走 TRG 抽取/嵌入/建链，消息时间戳=会话日期加序号乘五分钟（longmemeval.py:445-446），缓存按会话指纹 md5 存 `./locomo_message_cache/`（longmemeval.py:376-378）；session 级（longmemeval.py:506-714）——每会话一个 EpisodeNode 装"极全摘要"，minilm 时生成三路 embedding 以复合 ID 入库（longmemeval.py:599-663），自建关键词倒排（longmemeval.py:671-678）。
- **chunk 抽取**（longmemeval.py:742-986）：按问题词选九套关键词表（clothing/bike/camping/jewelry 等，longmemeval.py:754-792）做行级筛选，兜底才用 LLM。
- **评分**：主力 `evaluate_lenient`（longmemeval.py:1058-1186）宽松阶梯——精确等值后依次放行 not-found 等价、美元差一 0.9、数字 off-by-one 0.8（longmemeval.py:1132-1135）、词重叠七成给分、同小时 0.9（longmemeval.py:1168-1179）。
- **检索与答题**：`improved_retrieval_strategy`（longmemeval.py:1374-1636）两段式——query_engine 取候选后，用 `question.answer_session_ids` 经 session_index 直取金标会话节点（longmemeval.py:1397-1404），按题型定节点数与截取策略（longmemeval.py:1408-1581）；`answer_question_improved`（longmemeval.py:1638-2038）六题型各配 prompt，计数题两遍验证（longmemeval.py:1733-1799），末段按题型清洗 JSON（longmemeval.py:1960-2037）。

主循环 `test_questions`（longmemeval.py:2040-2156）三分支：jev_memory 存在则全委托（longmemeval.py:2052-2054），否则 message 或 improved 级构建；baseline 的评分取原始/清洗两次最大值（longmemeval.py:2079-2107）。`main`（longmemeval.py:2158-2330）：15 个参数、jev 开关互斥校验（longmemeval.py:2183-2199）、六类 category 过滤、token 统计与成本估算（longmemeval.py:2296-2308）、结果落盘（longmemeval.py:2310-2330）。

## 外部连接

import（longmemeval.py:25-32）：datasets.longmemeval 的 loader 与 LongMemQuestion、trg_memory、graph_db、vector_db、query_engine、answer_formatter、longmemeval_evaluator、LLMController 八样；惰性导入 MemoryBuilder（longmemeval.py:415）与 JevMemConfig（longmemeval.py:2185）等。被引：pyproject entry point、README、仓根垫片 test_longmemeval_chunked.py:1、tests/test_project_layout.py:15。图谱基准层枢纽，file 度数 15。

## 数据流

一次 `jev-mem-longmemeval --dataset data/longmemeval_s_cleaned.json --jev-mem`：

1. main 组装 JevMemConfig 双开、加载问题、可按 category 过滤（longmemeval.py:2187-2225）
2. `test_questions` 逐题循环。与 LoCoMo 的根本差异：**每道题一张图**——缓存 key 是该题会话指纹（longmemeval.py:376），全量跑意味着 N 张独立记忆图
3. Jev 分支：build+answer 全委托 jev_memory（longmemeval.py:2052-2054），实现在 memory/longmemeval_jev.py 适配层
4. baseline 分支：构建或命中缓存 → improved_retrieval_strategy 拼上下文 → answer_question_improved 出答案
5. 评分取两次 evaluate_lenient 最大值、过半判对（longmemeval.py:2103-2107），落盘 `results/{prefix}_{时间戳}.json` 并注明口径（longmemeval.py:2319-2323）

## 设计决策

**金标会话直取是最大口径问题**。`answer_session_ids` 是数据集金标（jev_mem/datasets/longmemeval.py:37），baseline 检索却用它直取节点（longmemeval.py:1397-1404），还在给 LLM 的上下文里标注 "**CONTAINS ANSWER**"（longmemeval.py:1592-1593）。MAGMA baseline 的数字实际是"金标会话优先+启发式抽取"的成绩；而 Jev 分支不经过这条泄漏路径——对照组口径松、实验组口径严的倒挂，对比数字时必须清醒。

**数据集特化到具体题目**：topic_patterns 硬编码 Miami/Hawaii/Seattle 旅行主题（longmemeval.py:251-253）；temporal 调试写死 MoMA/Metropolitan 检查（longmemeval.py:1621-1629）；shift/rotation 排班题特判（longmemeval.py:1844-1878）——全是围绕 LongMemEval 具体 haystack 的过拟合，换数据集即失效；80% 字样注释更像调参目标。

**宽松评分与诚实声明并存**：evaluate_lenient 比 official metric 宽，但落盘时显式写 `'not the official LongMemEval metric'`，token 口径只计 harness LLM（longmemeval.py:2322-2323）——引用百分比前先看这两行。

**死代码考古层**：四个方法零调用——`_extract_facts_from_text`、`create_multi_perspective_embeddings`、`evaluate_with_llm_judge`（longmemeval.py:1188）、`evaluate_answer_smart`（longmemeval.py:1332）；`__init__` 装配的 evaluator/answer_formatter/chunk_size/use_episodes 赋值后再无引用（longmemeval.py:53-78）——多轮实验迭代的遗迹。

**缓存与异常卫生**：message 级缓存目录叫 `./locomo_message_cache`（longmemeval.py:378）——从 locomo runner 复制粘贴的痕迹；key 只取会话指纹的 md5，会话数相同的题会共享缓存（longmemeval.py:376）。会话日期解析失败静默回退 now()（longmemeval.py:433-435）、多处裸 except（longmemeval.py:963、1017）。

## 新人提示

先读 main 的 argparse（longmemeval.py:2162-2230），再读 test_questions（longmemeval.py:2040-2156）。跑 Jev 消融记住硬约束：必须 `--memory-level message` 且不加 `--use-episodes`，否则直接拒绝（longmemeval.py:58-59 与 2196-2197）。

四个坑：改检索逻辑分数不变——多半缓存命中（longmemeval.py:381），强制 `--rebuild`；引用 baseline 分数前读 longmemeval.py:2322 口径声明与 1397-1404 金标直取；80% 字样注释不是实测结论；temporal 调试打印（longmemeval.py:1610-1629）写死实体名，别误当通用逻辑。全仓最大文件不等于最重要——Jev-Mem 实验组真正的管线在 memory/longmemeval_jev.py，本文件主体是 baseline 侧历史 harness。
