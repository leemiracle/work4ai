> 标题：答案格式化器——抽取/规范化/prompt 工厂/上下文拼装四合一 · 源文件：memory/answer_formatter.py（984 行）· 图谱标签：answer-processing / normalization / extraction / serialization（图谱 file 度数 4，实测引用面更广）

## 角色定位

`AnswerFormatter` 是读路径上的"口径守门人"，一个类管四件事：答案抽取与规范化（`extract_answer`）、按题型 QA prompt（`build_qa_prompt`）、检索节点拼上下文（`format_context_for_qa`）、adversarial 实体错配拦截（`validate_adversarial_answer`）。它同时决定 LLM 看到什么与评分器看到什么。

实例化仅一处：MemoryBuilder 创建并挂共享属性（memory_builder.py:54 与 102），TestHarness/QueryEngine/system/best_of_n_selector/jev_mem_retrieval 五方取同一实例——全无状态（纯函数打包成类），共享安全。模块零第三方依赖（answer_formatter.py:8-12），唯一局部依赖 TemporalParser（answer_formatter.py:516 与 821）。

## 内部结构

**三张配置表**（answer_formatter.py:21-51）：`answer_prefixes` 八个待剥前缀；`identity_mappings` 把 trans woman/transwoman 映射到 Transgender woman（answer_formatter.py:31-38），服务 LoCoMo 身份题；`not_found_patterns` 九种"信息不足"变体。

**抽取链**：入口 `extract_answer`（answer_formatter.py:53-82）按首字符 `{` 分流畸形/正常 JSON 两路（answer_formatter.py:84-193、195-282）。正常路按 15 个候选键捞值（collects/books/authors 等 LoCoMo 题面词汇，answer_formatter.py:222-227），嵌套展平、兜底拼接全部值；畸形路是问题类型驱动的启发式——'Do both' 类按问题大写词在响应中的出现数猜 Yes/No（answer_formatter.py:105-137）、how many 类取首个数字（answer_formatter.py:149-164）、which/what 类与引号串兜底（answer_formatter.py:166-187）。

**清洗链**：`_normalize_answer`（answer_formatter.py:284-310）→ not-found 精确等值归一与剥前缀（answer_formatter.py:312-340）→ 日期 fullmatch 命中才归一到 D Month YYYY（answer_formatter.py:307-309 与 342-368）→ 通用清洗首词大写/删孤立句点（answer_formatter.py:473-497）。answer_formatter.py:305-306 的注释钉版红线：formatting 不得删列表成员/人名/否定/解释/相对日期限定词，"Only canonicalize a standalone full date"。

**死代码**：`_normalize_duration`/`_normalize_identity`/`_normalize_name`（answer_formatter.py:370-471）与 `validate_answer`（answer_formatter.py:957-984）全仓零调用（grep 实证）——旧激进清洗路线的遗骸。

**prompt 工厂** `build_qa_prompt`（answer_formatter.py:499-662）按 category 分派六套模板：multi-hop 连线索（answer_formatter.py:524-540）、temporal 七条精度规则（answer_formatter.py:544-571）、single-hop 只给事实（answer_formatter.py:573-591）、adversarial 严禁实体替换（answer_formatter.py:593-606）、open-domain 与默认款（answer_formatter.py:608-660）。category 为 None 时用 TemporalParser 现判（answer_formatter.py:516-517）。

**节点取文**：`_get_original_text` 四级回退 original_text 属性 > EPISODE 节点 content > content_narrative > summary（answer_formatter.py:664-697）；注意 answer_formatter.py:681 用 `str(node.node_type) == 'NodeType.EPISODE'` 字符串比较枚举。`_get_semantic_enrichment` 取 semantic_facts/relationships/activities 各前两条（answer_formatter.py:699-734）。

**adversarial 校验**（answer_formatter.py:736-800）：只对 category 五生效；问题与答案各取大写实体，互找不到改判 "Information not found"（answer_formatter.py:759-782）。

**上下文拼装** `format_context_for_qa`（answer_formatter.py:802-955）三分支：temporal（answer_formatter.py:829-870）——解析 dia_id、按 (source, 会话号) 分组、组内按轮次连续性切块、按块内最小 rank 排序（answer_formatter.py:835-856），让"上周"这类相对表达与锚定日期回复不被排名拆散，每条附日期锚与时间注解（answer_formatter.py:857-869），answer_formatter.py:870 提前 return；multihop（answer_formatter.py:872-883）保留 speaker/dia_id/日期与语义增补，但不 return，落到尾部 Key Information 摘录段（answer_formatter.py:931-953）；默认分支给前几名打 `**MOST RELEVANT**` 等分级标记（answer_formatter.py:886-929）。

## 外部连接

上游：memory_builder.py:54 与 102 唯一实例化点。下游实测（grep 全仓）：jev_mem/system.py:58 与 61（问答主链）；test_harness.py:88、104、107（prompt→抽取→adversarial 校验三连）；query_engine.py:877 与 jev_mem_retrieval.py:202（两条检索出口）；best_of_n_selector.py:251（选优前校验）；memory/__init__.py:24 与 68（惰性别名注册表，延迟 import 避免 torch/FAISS 副作用）；jev_mem/benchmarks/longmemeval.py:78（装配后未用的死重）；tests/test_jev_mem.py:692 与 807（回归）。口径差：图谱 file 度数只计 file 级 import 边，以 grep 实测为准。

## 数据流

读路径主链全在问答侧：检索层产出节点 → format_context_for_qa 按题型拼上下文 → build_qa_prompt 包进配套模板 → LLM 返回裸文本 → extract_answer 抽值归一 → category 五时过 adversarial 实体复核 → 进 Evaluator 评分或 best-of-N 选优。写路径无关。一切改写以"保义"为红线（answer_formatter.py:305-306）。

## 设计决策

**保守化转向是本文件最重要的历史**。answer_formatter.py:307-309 的 fullmatch 门说明：formatting 曾会删列表成员、人名、否定、相对日期限定词，某次评测事故后收缩为"只规范独立完整日期"。回归测试 test_answer_cleaning_preserves_complete_meaning（tests/test_jev_mem.py:692-703）七组参数把红线钉死。三个死规范化器（answer_formatter.py:370-471）是旧路线遗体，跳过即可。

**数据集特化**：identity_mappings（answer_formatter.py:31-38）、候选键 collects/books（answer_formatter.py:222-227）、malformed JSON 启发式的 "Do both have pets" 原型注释（answer_formatter.py:134-136）都对应 LoCoMo 具体题面——换基准必须重审这三处，否则抽取方向性错误。

**temporal 拼装与 temporal prompt 配套**：分组重排让日期回复与提问相邻（answer_formatter.py:835-856）、锚定注解给 LLM 现成归一化时间（answer_formatter.py:862-869），与 temporal 规则"用语句自带的锚"（answer_formatter.py:544-571）闭环。对照测试 tests/test_jev_mem.py:807-821。

**multihop 与 temporal 的不对称 return**：temporal 在 answer_formatter.py:870 提前 return 不拼 Key Information 段；multihop 落到 answer_formatter.py:884 后继续进 931-953。多跳要摘要句、时间题要原文精度，方向合理但无测试钉住——被"顺手统一"会污染时间题上下文。

**伪 JSON 启发式脆弱点**：answer_formatter.py:176 用 `find(v)-5` 邻近窗口判"值不是键"，同一字符串出现两次会错位；Yes/No 推断在实体计数不足时直接猜 No（answer_formatter.py:129-137）——所幸只在 LLM 返回畸形 JSON 时触发。

## 新人提示

从 `extract_answer`（answer_formatter.py:53-82）与 build_qa_prompt 的类型判定（answer_formatter.py:513-519）读起。改清洗逻辑前先跑 tests/test_jev_mem.py:692 与 807 两组回归——保守化红线的守卫。排查"答案对却判错"先看 JSON 壳是否剥净、not_found 是否精确匹配（answer_formatter.py:312-323）。死代码可安全删除。新增 benchmark 第一件事：审三张表与候选键（answer_formatter.py:24-51、222-227）是否对新题面成立。
