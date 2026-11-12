> 标题：检索引擎——QueryEngine 多级检索管线精讲 · 源文件：memory/query_engine.py（2113 行）· 图谱标签：记忆存储与检索子系统 / 一级枢纽（全仓行数最大的 memory 模块）

## 角色定位

Jev-Mem 检索质量的决战之地。`trg_memory.query` 的朴素检索（向量锚点+BFS）撑不起 LoCoMo 的多跳/时序/对抗题。`QueryEngine`（memory/query_engine.py:23）在其上叠出完整管线：题型检测→三路召回→RRF 融合→自适应图遍历→题型感知重排→Q&A 与会话扩展→上下文组装。

它还内嵌实验基础设施：`ablation_config`（四档见 query_engine.py:40-44）让同一引擎可拆掉任一环节跑消融。`query` 第一行有 Jev-Mem 检索控制旁路（query_engine.py:704-706：`jev_config.read_enabled` 时整体移交给 `RetrievalController`），因此它是"基线检索"与"受控检索"的共用外壳。

## 内部结构

- `__init__`（query_engine.py:30）：收 trg_memory、node_index 关键词倒排、entity 映射、ablation_config；惰性组装 `JevMemConfig`+`JevClient`（query_engine.py:54-57）
- **题型检测族**：`detect_query_type`（query_engine.py:251，九类题型：multi_hop/temporal/entity/causal 等；multi_hop 判定最前——最特异先判，信号清单 query_engine.py:259-312）；另有粗粒度 `detect_query_intent`（query_engine.py:229）与 `is_action_question`（query_engine.py:196）
- **自适应参数**：`get_adaptive_params`（query_engine.py:371-473，每题型一套遍历深度/偏好边型/相似阈值/打分权重，如 multi_hop 是 depth=12、threshold=0.10）
- **三路召回**：向量路调 trg.query（query_engine.py:745）；`_keyword_search`（query_engine.py:917，倒排+bigram）；`_scan_all_nodes`（query_engine.py:1009，全库扫兜底）；`_temporal_keyword_search`（query_engine.py:885，IDF 式权重变体）
- **融合**：`_rrf_fusion`（query_engine.py:59，Reciprocal Rank Fusion，引 Cormack 2009；rank 从 0 起故贡献 1/(k+rank+1)，query_engine.py:100）
- **图遍历**：`_adaptive_graph_traversal`（query_engine.py:1138，BFS+双阈值剪枝+编码预算 400）；`_get_neighbors`（query_engine.py:1236，按 sub_type 分诊：CONTEXT_NEIGHBOR 永远放行、SAME_ENTITY 高优先）；`_probabilistic_beam_search`（query_engine.py:1041，论文 Algorithm 1 实现）
- **重排**：`_rerank_and_filter`（query_engine.py:1321，人名/年份硬过滤+十余种信号线性加权）；`_retrieve_multi_hop_evidence`（query_engine.py:1671，每实体保底 top3）；`_score_node_relevance`（query_engine.py:1804）
- **扩展**：`_expand_qa_context`（query_engine.py:590，问号节点沿 PRECEDES 找同对话下一句当答案）；`_expand_session_context`（query_engine.py:642，捞 SESSION 摘要排序）
- **辅助**：`extract_date_from_question`（query_engine.py:475）、LLM 问题分解 `decompose_and_answer_multi_hop`（query_engine.py:1982）

## 外部连接

import：`.trg_memory` 四类型（query_engine.py:16）、`AnswerFormatter`（query_engine.py:17）、`KeywordEnricher`（query_engine.py:18）；第 19 行是 multihop_improvements_v2 的墓碑注释（对应 query_engine.py:1695-1700）。惰性导入密集：jev_mem_config/jev_client（query_engine.py:54-55）、`RetrievalController`（query_engine.py:705）、graph_db.NodeType（query_engine.py:893）——压启动依赖、避循环引用。被引（grep 实证 9 文件）：两个 benchmark 入口（locomo.py:592 组装它）、`jev_mem/system.py`、demo 与两测试。图谱双枢纽。

## 数据流

以 `"What research did Melanie pursue?"` 走 `query(question, top_k=15)`（query_engine.py:686）为例：

1. `detect_query_type`（query_engine.py:707）命中 research 正则（query_engine.py:261）→multi_hop；`get_adaptive_params`（query_engine.py:723）取参数
2. 三路召回配额（query_engine.py:736-759，multi_hop 为 30/30/40）
3. `_rrf_fusion(k=60)`（query_engine.py:762）得唯一候选集，RRF 分×20 截 1.0 塞回 similarity_score（query_engine.py:766）——重排以此为向量信号
4. SESSION 节点当路由提示：其邻居获提振后 SESSION 自身滤出（query_engine.py:776-799）
5. 非 basic_retrieval 时 top30 走 `_adaptive_graph_traversal`（query_engine.py:812-820）：邻居过轻量过滤与双阈值剪枝（query_engine.py:1208、1228-1231），新节点并入候选池
6. multi_hop 专走 `_retrieve_multi_hop_evidence`（query_engine.py:828-834）：抽实体→每实体保底 3 节点→剩余按相关度补
7. `_expand_qa_context`（query_engine.py:848）：问号节点沿 PRECEDES 拉同 dia 前缀的后继语句——答案常紧跟问题；再捞 SESSION 摘要、裁回 top_k（query_engine.py:852-857）
8. `AnswerFormatter.format_context_for_qa`（query_engine.py:877-881）拼 answer_context，与 QueryContext 一并返回

`decompose_and_answer_multi_hop`（query_engine.py:1982）是旁路：LLM 拆子问题逐个递归检索再合成（query_engine.py:2010-2088）——自带 CoT 链。

## 设计决策

**RRF 而非分数加权和**（query_engine.py:59-119）：三路分数量纲不同，直接加权会打架；RRF 只用排名、免疫量纲与离群，代价是丢弃绝对置信信息。

**题型自适应是灵魂**（query_engine.py:251-473）：九题型×四维参数矩阵让"when 类重时间边、多跳放宽阈值深挖 12 层"。批判地看，query_engine.py:259-312 的三十多个手写信号是**对 LoCoMo 题面分布的过拟合**（如 'offer'、'common' 关键词信号）换 benchmark 就要重调；query_engine.py:181-188 的 temporal_keywords 硬编码表把特定数据集的会话编号焊进引擎，复用必须清洗。

**打分器的工程妥协**：`_rerank_and_filter`（query_engine.py:1321）单方法 350 行、十余信号线性加权，Magic Number 密布（dia_id 精确命中 50 分等）。这是"对着 badcase 打补丁"式演化的化石层（query_engine.py:983-985 的 MAJOR FIX 注释、query_engine.py:1448-1465 昵称特判为证）。可维护性差但每条规则背后有真实错误案例，动它们要跑全量回归。

**性能护栏三处**：encoding_limit=400（query_engine.py:1211）限遍历期编码调用、邻居每轮放行 8-10 个（query_engine.py:1210）、全扫取 60 条（query_engine.py:1039）。MiniLM 本地几乎不触发，OpenAI 编码器下是成本闸门。**两套图遍历并存**：`_probabilistic_beam_search`（论文 Algorithm 1 保真实现）与 `_adaptive_graph_traversal`（工程化 BFS）。主路径只用后者，读代码别把前者当实际生效逻辑。

## 新人提示

入门：先 `query`（query_engine.py:686）通读画十步管线，再钻 `detect_query_type`（query_engine.py:251）+`get_adaptive_params`（query_engine.py:371）这对"诊断-处方"——改检索行为九成只需动 query_engine.py:371-473 参数表，打分信号清单在 query_engine.py:1321。

五个常见误解：以为向量检索是主角——融合后 similarity_score 被 RRF 分覆盖（query_engine.py:766），关键词路权重常最高；以为 `_probabilistic_beam_search` 在用——主路径是 `_adaptive_graph_traversal`（query_engine.py:812 调用点）；以为 top_k 就是最终节点数——Q&A 与会话扩展会膨胀再裁剪（query_engine.py:848-857）；以为 Jev 旁路是小开关——`read_enabled=True` 时整个本地管线被跳过（query_engine.py:704-706）；`decompose_and_answer_multi_hop` 无 llm_controller 时直接返回提示串（query_engine.py:2007-2008）。
