> 标题：Jev 检索控制器——路由+束搜索图遍历精讲 · 源文件：memory/jev_mem_retrieval.py（206 行）· 图谱标签：读路径核心 / 最高阶决策点

## 角色定位

Jev-Mem 读路径的大脑，全仓决策密度最高的两百行。文件头一句话自白（jev_mem_retrieval.py:1）："Jev routing and batched traversal over MAGMA's existing graph and vectors"——它在 MAGMA 基线已有的图与向量库之上，加一层 System Two 驱动的智能检索：先用 routing 问卷判断这道题需要什么样的图证据，再以束搜索（beam search）在图上扩展，每轮用 stopping 问卷问"证据够了吗"、用 traversal 问卷给候选节点打分，全程在延迟/调用次数/预算三重硬顶下运转。

它是 `--jev-mem` 读开关的唯一执行者：`memory/query_engine.py:704` 判 read_enabled 后惰性导入并整体委托（query_engine.py:705-706）——QueryEngine 的原版多层检索在 jev 模式下完全旁路，两套检索是替换不是叠加。docs/architecture.md:82 与 README.md:129 都把它指为读路径的规范入口。

## 内部结构

单类两方法，`_query`（jev_mem_retrieval.py:31-206）是一条 176 行的五阶段状态机：

- **并发闸门 query**（21-29）：top_k 正性校验（22-23）；monotonic 计时排队（24）后进 `client.retrieval_slot()` 信号量（25），出队时刻差即 queue_seconds 写进 metadata（26-28）。tests/test_laya_backend.py:122-129 专测这个语义：本地模型后端（laya）一次只许一个 _query 占坑，后来者排队且 CallBudget 死钟不早走——排队时间不计入检索延迟
- **阶段一 路由**（32-52）：CallBudget 挂双顶——最大调用数与截止时刻（34）；TemporalParser 判时间型问题（36-37）、detect_query_intent 判 WHEN/WHY（38）；baseline 需求向量按意图预置（39-41，WHY 时 causal 需求拉满）；`client.evaluate("routing", ...)` 问 System Two，mock_values=baseline 保证后端不可用时降级到启发式（42）；产出 GraphNeeds 六维（43）；multi_hop_need 折算本轮深度上限（44）；allocate_graph_budgets 按需分配四类边预算（45）；消融开关在预算上做手术——no_causal/no_temporal 清零对应类、basic_retrieval 全零退化为纯锚点检索（47-52）
- **阶段二 锚点**（59-82）：预算有余才做（60）；关键词增广（61）→encoder.encode_with_timeout 若有则带死线编码（62-65）→向量检索 k 取 min(maximum_nodes, max(top_k, anchor_count))（69）→只留 EVENT 节点（71）→时间型问题换 _temporal_keyword_search（72-73）→RRF 融合两路（74）→锚点入 nodes/scores/单点 paths 三表，上限 min(anchor_count, maximum_nodes, top_k)（75-82）
- **阶段三 主循环**（85-187）：`while nodes` 内六道退出闸——延迟超（87-89）、stopping 判证据充分（90-105，mock 默认值随深度翻转：零轮鼓励继续、一轮后 sufficient 拉到高位即停，94-95）、Jev 调用耗尽（106-108）、节点数满（109-111）、深度到顶（112-114）、图预算耗尽（115-117）。扩展阶段：逐 frontier 节点 get_neighbors，边数与延迟双守卫在内层与外层各查一次（121-122、137-138）；过滤已入选/非 EVENT/该类边预算耗尽（125）与非 ACTIVE 边（127）；**预算在检查候选时即扣**（129-130，注释明示 "counts candidate expansions, shared across all rounds"）；结构分取边 probability/confidence 默认中值（131-132）；同节点多入边保结构分最高者（133-136）。评分阶段：每候选一组前缀化问题、relevance 默认值直接用余弦（147-152）；`client.evaluate("traversal", ...)` 一次批量问全部候选（153-157）；五元组分向量（余弦、jev relevance、需求匹配 relation_fit、新信息量 novelty、支持度 support）与 transition_weights 加权平均（163-170）；时间新近度修正——候选时间距已见最晚时间的天数衰减 recency，以小权重混入（171-175）。束推进：按分排序取 width=min(beam_width, 剩余容量) 扩入并延伸路径（177-183），深度加一（184）
- **阶段四 产出**（188-206）：末次延迟覆写 stop_reason（188-189）；重选 top_k（190-191）；metadata 二十键全量留痕——query_id 是问题 sha256 前十六（192）、graph_budgets 与实际 used 对账（193-194）、jev_calls/cache_hits/fallback_events 可观测三件套（195、198）、stop_reason 与全部 stopping 决策（197）——然后 answer_formatter 组织上下文（202）、组 QueryContext（203）、audit.emit 落审计（204）、trg.stats 计数（205）

## 外部连接

import（jev_mem_retrieval.py:3-14）：graph_db 的 NodeType/LinkStatus（10）、jev_client 的 CallBudget（11）、jev_questions 的三组问卷（12）、jev_mem_policies 的 GraphNeeds/allocate_graph_budgets/cosine/node_state（13）、trg_memory 的 QueryContext（14）、numpy（8）；TemporalParser 函数内惰性导入（36）。fanOut 实测三处：query_engine.py:705-706 的运行时分派、tests/test_laya_backend.py:126 与 171 两测（engine 传 None、monkeypatch _query，专测并发闸门与异常后释放）、README/docs 的文档引用。注意它反向伸手拿 QueryEngine 的私有方法 `_keyword_search`/`_temporal_keyword_search`/`_rrf_fusion`（72-74）与 `answer_formatter`（202）——控制器与引擎是双向耦合，图谱若只看 import 边会低估这层运行时依赖。

## 数据流

一次 `jev-mem` 模式检索的五阶段流水：问题进来→（路由）System Two 出六维需求→折算深度与四类边预算→（锚点）向量+关键词双路召回融合出种子 EVENT→（循环）扩展邻居→批量打分→束推进，直到六闸任一触发→top_k 节点+路径+二十键 metadata 打包返回。metadata 里 graph_budgets 与 graph_budget_used 的对账设计（193-194）让每次查询的预算执行率可事后审计，stop_reason 精确到六种退出原因——这是实验侧做检索行为分析的主数据源。

## 设计决策

**预算在候选检查时扣而非录取时扣**（129-130）是全文最精妙的一笔：看过即计数，防止循环用廉价候选反复试探耗尽轮次而不真正扩展——预算语义从"产出配额"改为"注意力配额"。**mock 默认值编码行为策略**（94-95）：无 System Two 时 stopping 问卷的默认答案设计成"零轮不满足、一轮后满足"，使 mock 模式自动退化为单轮扩展的确定性检索——降级路径不是坏近似而是可预期行为，这让它同时服务 laya 本地后端测试（tests/test_laya_backend.py:126）与消融实验。**键域对齐消 KeyError**：link_type 枚举四值小写化（124）恰与 allocate_graph_budgets 的 graphs 四元组（jev_mem_policies.py:163）一一对应，used[graph]（125、130）永不出错——两文件的隐式契约，改任何一侧枚举都要同步。

批判性发现三处：①`while nodes`（85）的条件永不为假——nodes 只增不减，循环全部靠 break 退出，185 行的 stop_reason="frontier_exhausted" 先无条件赋值再判空 break（185-187），语义正确但可读性差，是典型状态机内联化的代价；②176 行单方法承担五阶段，harness 视角是反巨型文件的经典反例——好在阶段间靠行号分段而非共享可变状态，重构切分成本不高；③每候选逐个生成 traversal_questions 并展平成前缀键值（147-152），候选多时单次 evaluate 的 prompt 体积线性膨胀，maximum_edges 与束宽实际兼任 prompt 尺寸的隐性控制者——调参时把 maximum_edges 拉大会先撞 prompt 上限而非图遍历瓶颈。

## 新人提示

先读 query 的闸门（21-29）再一头扎进 _query——明白"排队不计延迟"后才不会误读 latency_seconds。主循环按六道退出闸的行号立书签（87、99、103、106、109、112、115），每读一段就问"这段之后会从哪道闸出去"。做实验先认 metadata 字段表（192-198）：stop_reason 与 graph_budget_used 是检索行为差异的定位器。

三个坑：检索结果为空且 stop_reason=no_evidence（56）不一定是 bug——预算在锚点前就耗尽（60）会静默走这条路，查 max_latency_seconds 配置；调大某类边预算没效果时先看 routing 给的 needs——allocate_graph_budgets 只给超过激活阈值的需求类分预算，needs 低时预算恒为零（jev_mem_policies.py:164-166）；`ablation_config.basic_retrieval`（51-52）会把全部预算清零但保留锚点与 stopping——做消融对照时记住它砍的是图扩展不是向量检索，别把结果读成"无检索"。
