> 标题：Noul/Choice 协议——jev_questions 精讲 · 源文件：memory/jev_questions.py（163 行）· 图谱标签：System-One 决策控制层

## 角色定位

这个文件是 Jev-Mem 的"问题库"：System-One 控制器问 Jev 的每一个问题都在这里定义成 `typesafe_sdk` 的类型化原语——`Noul`（求一个命题为真的概率）与 `Choice`（求一个离散选择及其完整分布）。文件头（1-5）三条纪律定义了整个协议风格："All instructions identify their state fields: question IDs are NOT model input"（问题 ID 不进模型，指令文本显式引用 state 字段名）；"Noul outputs are probabilities of defined propositions, not graded importance"（输出是命题概率，不是重要度打分）。

它存在的理由：Jev-Mem 的核心主张是把高频记忆管理决策交给轻量控制器，而这些决策必须**可复现、可审计、无隐藏上下文**。把问题措辞集中在一个纯声明式文件里，prompt 就成了代码——review、diff、版本化全走 git，而不是散落在字符串拼接里。八个问题族对应记忆生命周期的八个决策点：准入、类型标注、关系判定、巩固、检索路由、迭代停止、图遍历，外加一个 mock 夹具。

## 内部结构

唯一的 helper：`noul(instructions, yes, no)`（10-11）把"命题指令 + true/false 两侧判据文本"包成 `Noul(instructions=..., criteria={"true": yes, "false": no})`。八个问题族（全部无状态，每次调用返回新 dict）：

- `observation_questions`（14-16）：合并准入与类型两组——docstring 点明动机 "Admission and multi-label typing share state and can be evaluated together"，一次请求拿九个分数，省一次 state 序列化与网络往返。
- `admission_questions`（19-41）：五问。`should_store`（21-24，有无值得保留的具体细节）、`future_utility`（25-28，未来问题能否用上）、`importance`（29-32，是否人生事件/承诺/关系/稳定偏好）、`novelty`（33-36，相对 `recent_memories` 与 `exact_duplicate` 标志有无新事实）、`redundancy`（37-40，可召回信息是否已全部在近期记忆）。注意 novelty 与 redundancy 是互补双命题：一个问"有没有新的"，一个问"是否全是旧的"。
- `memory_type_questions`（44-63）：episodic/semantic/procedural/preference 四个独立标签；docstring（45）划清界限 "these scores never determine whether to store a turn"——类型判定不掺和准入决策。
- `relation_questions(index, infer_identity=True)`（66-83）：新记忆与第 index 个候选的四问——semantic（69-71）、causes（72-74）、caused_by（75-77，方向相反的因果）、entity（79-82，仅在 `infer_identity` 为真时追加，判别名是否同指一实体）。每问共享固定前缀（67）：`Compare \`new_memory.content\` with \`candidates[{index}].content\`.`——索引数字直接嵌进指令文本。
- `consolidation_questions(index)`（86-109）：四 Noul（redundant/contradiction/obsolete/link，89-100）加全文件唯一的 `Choice`：`representation`（101-108），四选项 keep_separate/merge/promote/uncertain，每项一段判据——例如 106 行 promote 的判据"反复出现的独立事件明确支撑稳定的一般模式，重复事件优先于 merge"。
- `routing_questions`（112-126）：六问（semantic/temporal/causal/entity/multi_hop_need/recency_importance），产出 `GraphNeeds` 的原料，决定四张图视图各分多少检索预算。
- `stopping_questions`（129-143）：四问（evidence_sufficient/continue_useful/missing_evidence/contradiction），检索迭代的停止判据。
- `traversal_questions(index)`（146-157）：四问（relevance/relation_usefulness/new_information/supports_current_evidence），图遍历时对每个候选节点的价值判定。
- `choice_fixture(question, option)`（160-163）：构造 one-hot mock 答案，docstring 风格的注释强调 "never used as a live fallback"。

## 外部连接

import 只有一行：`from typesafe_sdk import Choice, Noul`（7）——零其它依赖，纯声明式。被三处消费（全部方法内延迟 import）：`memory/jev_mem_policies.py:102/110/128`（写路径三族：memory_type/observation/relation）、`memory/jev_mem_retrieval.py:12`（读路径三族：routing/stopping/traversal）、`memory/memory_builder.py:243`（巩固族 + fixture）。图谱归 layer:system-one-control。它不 import config 也不 import client——问题定义与执行彻底分离，这使得问题库可以脱离运行时做纯文本 review，也使得 `tests/test_jev_mem.py` 能直接断言问题结构。

## 数据流

数据不"流经"这个文件，它产出**问题模板**。完整一跳：`relation_questions(0)` 返回 `{semantic: Noul(...), causes: Noul(...), ...}` → 调用方加前缀键得 `pair_0_semantic`（`memory/jev_mem_policies.py:131-137`）→ 连同 state `{new_memory: {...}, candidates: [...]}` 交给 `JevClient.evaluate` → 序列化为 wire（`question.model_dump()`，`memory/jev_client.py:239`）→ Jev 返回 `{pair_0_semantic: {type: "noul", noul: 0.72}, ...}` → 校验后落进 `ProbabilityResult.values` → `WritePolicy.relations` 在 `memory/jev_mem_policies.py:152-157` 把 ≥0.60 的概率翻译成图上的 `Link` 边。

Choice 侧例子：巩固时 `consolidation_questions(i)` 里 `representation` 的答案落在 `ProbabilityResult.choices`，`memory/memory_builder.py:255` 取 `representation.choice`（merge 或 promote）决定是否触发摘要节点生成（`memory/memory_builder.py:268-286`）。

## 设计决策

**三段式命题结构**（10-11）是全文件的灵魂：每问 = 一句无歧义指令 + 两个边界判据。判据文本写得像评分 rubric——例如 24 行 should_store 的 false 侧 "Only a greeting, acknowledgement, generic pleasantry, or content with no recallable detail"，把模糊判断拆成可对照的定义。这是把 prompt 工程变成**测量仪器**的关键：答案可解释，错误可归因到具体判据的措辞，而不是"模型心情不好"。

**无隐藏上下文原则**：所有指令只引用 state 里存在的字段名（`observation`、`recent_memories`、`candidates[0].content`、`query`、`evidence`），同批问题之间互不引用（`memory/jev_client.py:144-146` 的 docstring："No answer in this batch is used as hidden context for another question"）。好处是问题可独立并行、可单独缓存、答案可复现；代价是放弃"前一问的答案作为后一问输入"的链式推理——多跳推理被显式转移到图遍历（traversal_questions 每步重评 candidate）去做，这是刻意的架构切分。

**对称与省略的经济学**：`infer_identity` 开关（66、79-82）配合调用方——两边 entities 已有精确交集时跳过 entity 问（`memory/jev_mem_policies.py:132-133`），省一次不确定性判断；novelty/redundancy 双问（33-40）宁可多花一问也要让"新"与"旧"各有独立测量，防止单一问题的措辞偏差同时污染两个方向。

局限：全英文命题硬编码；判据措辞即协议，却只有 `decision_schema_version`（`memory/jev_mem_config.py:22`）一个粗粒度版本号——改一句 rubric 不会 bump 版本，旧缓存与旧审计无法区分语义变化；`index` 拼进指令（67）意味着候选顺序变化会改变问题文本、从而改变缓存键（`memory/jev_client.py:152` 的 SHA256 覆盖 questions 全文）——重排即缓存全失效，但顺序敏感本是合理语义。

## 新人提示

先读 10-11 行 helper 与 19-41 行五问，吃透"三段式"再扫其余族。三个常见误解：① `noul` 的输出不是 0-10 的重要度分数，是**命题为真的概率**（文件头 4 行原话），阈值比较才有意义、大小排序没有；② 问题 dict 的键（如 `pair_0_semantic`）只是外键，模型看到的只有 instructions 文本——所以改键名安全，改 instructions 才是协议变更；③ `choice_fixture` 生成的 one-hot 不属于任何降级路径（161 行注释原话 "never used as a live fallback"），它只喂 mock 模式。想增删问题：改本文件 → 确认消费方解包字段（如 `memory/jev_mem_policies.py:121`）→ 评估是否 bump schema version。
