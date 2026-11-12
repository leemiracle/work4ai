> 标题：写读策略——jev_mem_policies 精讲 · 源文件：memory/jev_mem_policies.py（185 行）· 图谱标签：System-One 决策控制层

## 角色定位

如果说 `jev_questions.py` 定义"问什么"，这个文件定义"**怎么用答案**"。文件头（1）一句话定分工："Typed System-One decisions; graph nodes and edges remain MAGMA objects"——Jev 只产出决策，落到图里的节点与边仍是 MAGMA 的 `EventNode`/`Link` 对象。这个决定让 Jev-Mem 与基线共享同一存储层（消融实验可比），且每条边带 `origin` 元数据可追溯来源是 jev / laya / mock / 精确标识（150、157）。

它承载三块职责：写路径的打分与建边（`MemoryAdmission` 与 `WritePolicy`）、候选集裁剪（`find_candidates`）、读路径的图预算分配（`allocate_graph_budgets`）。文件名叫 policies，实际是"决策 → 图操作"的翻译层：上游是纯问题定义，下游是纯存储对象，策略逻辑夹在中间。

## 内部结构

- `MemoryAdmission`（11-22）：frozen dataclass，五字段对应 admission 五问。核心是 `score(weights)`（19-22）：`a, b, c, d = weights`；`utility = (a·future_utility + b·importance + c·novelty) / (a + b + c)`；返回 `should_store × max(0, utility − d·redundancy)`。
- `MemoryTypeScores`（25-30）与 `GraphNeeds`（33-39）：两组纯分数载体，后者六字段对应 routing 六问。
- `timestamp_value`（43-47）：naive 时间统一补 UTC 时区（docstring："Normalize legacy naive dates as UTC for consistent ordering"），保证时间序比较不因混用 aware/naive 抛错。
- `node_state(node, include_temporal=False)`（50-58）：把图节点投影成 Jev 可读的 state dict（id/content/timestamp/entities）；`include_temporal` 时附加 `timestamp_role` 声明"观察时间 ≠ 事件时间"（56-57）与 `TemporalParser().describe_references` 的相对时间描述——给读路径的多跳时间推理用。
- `cosine`（61-66）：None 安全、clip 到 [0,1]。
- `find_candidates(trg, node, top_k)`（69-93）：多信号手工加权的候选裁剪，见数据流。
- `WritePolicy`（96-158）：三个方法。`memory_type`（100-106，admission 关闭时单独做 typing）、`assess_observation`（108-123，一次 evaluate 同拿 admission + typing，121-122 行按 `__dataclass_fields__` 字段名解包）、`relations`（125-158，逐对建边；内嵌 `add()` 闭包 145-150：过 `relation_threshold` 才建 `Link`，properties 带 sub_type/confidence/probability，metadata 带 `controller: "jev-mem"` 与 origin）。
- `allocate_graph_budgets(needs, config)`（161-185）：最大余数法整数分配，docstring（162）保证 "the total never exceeds B"。

## 外部连接

import：`numpy`（6）、`.graph_db` 的 `EventNode/Link/LinkType/NodeType`（8）；方法内延迟 import `.jev_questions` 三处（102、110、128）与 `.temporal_parser`（55）——延迟既避免导入环也降低加载成本。被 import：写侧 `memory/memory_builder.py:129/140`（`find_candidates`/`node_state`）与 `:234`（consolidate 复用同两件）；读侧 `memory/jev_mem_retrieval.py:13` 一行拿走 `GraphNeeds/allocate_graph_budgets/cosine/node_state/timestamp_value` 五件；再加 `tests/test_jev_mem.py`。图谱归 layer:system-one-control。一个细节：它 import 了 `EventNode`（8）却几乎不在本文件构造——真正 new `EventNode` 的是 `memory/memory_builder.py:161`，本文件只构造 `Link`，这正呼应文件头"nodes remain MAGMA objects"。

## 数据流

**写入打分例**：观察 "[Alice]: I moved to Berlin last month"，recent_memories 里已有旧城信息。`assess_observation`（108）一次发九问，假设拿回 should_store=0.92、future_utility=0.85、importance=0.75、novelty=0.88、redundancy=0.15，weights=(0.4,0.3,0.3,0.2)：utility=(0.34+0.225+0.264)/1.0=0.829，score=0.92×max(0, 0.829−0.03)≈0.736 ≥ 0.60 → 通过（判定点在 `memory/memory_builder.py:150-152`；不通过则 audit `memory_rejected` 并返回 None）。

**候选裁剪**（69-93）：四路信号手工加权——向量检索 top_k 结果记 2×cosine（73-76）；实体精确交集 +2.0（84）；关键词覆盖率 `len(keywords∩other)/len(keywords)`（85-86）；时间接近度 `0.25/(1+Δ秒/86400)`（87-89，一天内约 0.12-0.25 的弱信号）。按 (−score, id) 排序（91）后只留 EVENT 且非自身（92-93）。

**建边**（125-158）：对 top-10 候选逐对发 3-4 问，`pair_i_` 前缀展开成约 30-40 个问题一次 evaluate（138-139）；SEMANTIC/RELATED_TO（152）、CAUSAL/LEADS_TO 正反两向（153-154）、ENTITY/SHARED_ENTITY（156-157，实体精确交集时直接 1.0 且 origin="exact_identifier"，跳过 LLM 判断）。

**读路径预算**（161-185）：`GraphNeeds` 六分量 → 激活条件 `need > 0 且 ≥ graph_activation_threshold`（165）→ 小预算时只留头部 `B//min` 个图（170-173）→ 权重 `(need/max)^probability_exponent`（177-178，指数 1.5 强化马太效应）→ 整数份额分配 + 按小数部分大者补余（180-184），总和恒 ≤ total_graph_budget。

## 设计决策

**打分公式的形状**（19-22）值得细品：utility 三项除以 (a+b+c) 归一，使权重是"相对比例"而非绝对分数；redundancy 用**减法**而非乘法惩罚——高价值高冗余的内容（更新类信息："我搬到柏林了"相对"我住巴黎"既新又旧）可以被 utility 盖过去；`should_store` 作外层门，措辞空洞的内容一票否决。这同时解释了 config 的两条校验：权重和不为零（`memory/jev_mem_config.py:80-81`）、前三个 utility 权重至少一个正（82-83）——配置层在替运行期防除零。

**候选裁剪用手工加权而非学习排序**（69-93）：2.0/2.0/1.0/0.25 的权重透明可复现，论文好写、消融好做；代价是权重硬编码无配置项，且 80 行对 `trg.graph_db.nodes.values()` 全图 O(N) 扫描——向量那一路是 ANN 快的，实体/关键词/时间三路是全扫，大图下每次写入的候选阶段线性变慢。

**决策与存储解耦**（1）：`WritePolicy.relations` 只返回 `Link` 列表不落库，插入与回滚统一在 `memory_builder._store_jev_node`（189-218）——策略层可以纯函数式测试，不需要图数据库。

局限：`assess_observation` 的 mock 启发式（113-116，词数 ≥4、prefer/like 关键词）语义粗糙，mock 模式的指标只能当冒烟测试；`relations` 的问题量随 `candidate_top_k` 线性放大（10 候选约 34 问一批），延迟敏感时这个 top_k 是第一旋钮；`node_state` 的 `include_temporal` 分支每次 new 一个 `TemporalParser()`（55-57），高频调用有浪费。

## 新人提示

先读 19-22（公式）与 69-93（候选裁剪），这两段是理解写路径的钥匙。三个误解：① `allocate_graph_budgets` 是**读路径**的（被 `jev_mem_retrieval.py` 消费），别在写路径里找它的调用；② `relations` 返回 None 是"Jev 不可用请降级"的信号（140-141），返回 `[]` 才是"没有过阈值的关系"——两者下游处理完全不同（`memory/memory_builder.py:173-174` 转 MAGMA vs 正常入库）；③ `find_candidates` 的分数不是概率，量纲混合（cosine×2、布尔交集×2、关键词比例、时间核），只用于排序，不要解读绝对值。改阈值时记得 `JevMemConfig` 里两个 0.60（29-30）语义不同：admission 管节点、relation 管边，别一起动。
