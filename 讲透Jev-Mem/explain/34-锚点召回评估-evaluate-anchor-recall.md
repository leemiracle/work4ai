> 标题：锚点召回诊断脚本——离线扫 anchor_count 超参的种子覆盖率仪 · 源文件：scripts/evaluate_anchor_recall.py（83 行）· 图谱标签：diagnostics / retrieval / script（图谱度数 in=0 / out=2）

## 角色定位

检索种子的覆盖率诊断仪。它回答一个很窄的问题：**只看向量+关键词两路召回的 RRF 融合种子，多少金标证据能进入前 anchor_count 个节点？** 文件头三行自我划界（scripts/evaluate_anchor_recall.py:1-5）：只用已保存的图和本地 MiniLM（scripts/evaluate_anchor_recall.py:1）；"Gold dialogue IDs are used only for scoring, never to rank candidates"（scripts/evaluate_anchor_recall.py:3）——与第 30 篇适配器同款的金标隔离纪律；"This is an anchor diagnostic, not an end-to-end Jev/answer accuracy benchmark"（scripts/evaluate_anchor_recall.py:4）——明确不测 Jev 遍历也不测答题，数字只能用于解释检索端，不能当成绩引用。

它挂在 scripts/ 而非 jev_mem/benchmarks/，定位是**调参工具**：anchor_count（种子数）是 JevMemConfig 的检索超参（默认值见 memory/jev_mem_config.py:37），本脚本用五档网格离线扫出 recall 曲线，替你决定线上 anchor_count 该设多少。全仓 grep 实测没有任何代码或文档引用它——一次性诊断脚本，无 CI 覆盖，图谱 in=0 也印证这是叶子。

## 内部结构

单 main 函数，六段流水：

- **参数与离线开关（scripts/evaluate_anchor_recall.py:18-25）**：四个参数——`--memory` 缓存目录必填、`--dataset` 默认 data/locomo10.json、`--sample` 选第几个样本、`--output` 报告路径必填。接着硬设 `HF_HUB_OFFLINE`/`TRANSFORMERS_OFFLINE`（scripts/evaluate_anchor_recall.py:24-25），配合后面 `local_files_only=True`——脚本拒绝联网，MiniLM 必须已在本地缓存。第 14 行 `sys.path.insert` 把仓根塞进导入路径，scripts/ 目录直跑的常规补丁。
- **延迟导入（scripts/evaluate_anchor_recall.py:26-33）**：numpy/sentence_transformers 与五个仓内模块全部放在离线开关之后才 import——argparse 阶段零重依赖，参数打错不付 torch 级启动成本。
- **图组装（scripts/evaluate_anchor_recall.py:35-41）**：NetworkXGraphDB 加载 graph.json；TRG 用 **MockEncoder + 384 维 NumpyVectorDB + llm_backend=None** 组装（scripts/evaluate_anchor_recall.py:38-39）——这两个件是给 TRG 构造器交的"配重"，真实向量排序根本不走它们；关键词索引从 keyword_index.json 读成 set 字典（scripts/evaluate_anchor_recall.py:40）；`QueryEngine(trg, index)` 第二个位置参数就是 node_index 关键词索引（构造签名见 memory/query_engine.py:30）。
- **问题选择与查询嵌入（scripts/evaluate_anchor_recall.py:42-47）**：dataset 加载时的打印用 redirect_stdout 吞掉（scripts/evaluate_anchor_recall.py:42-43）；只留 `category != 5` 且带 evidence 的问题（scripts/evaluate_anchor_recall.py:44）——category 5 是 LoCoMo 的特殊类目（数据类里专门分支处理，jev_mem/datasets/locomo.py:19）；查询文本先过 **KeywordEnricher.enrich_query**（scripts/evaluate_anchor_recall.py:46，enricher 挂在 trg 上，memory/trg_memory.py:96，enrich_query 调用形态见 memory/trg_memory.py:249）再进 MiniLM——查询侧增强与线上口径一致，这是本脚本最讲规矩的一处。
- **双路排名（scripts/evaluate_anchor_recall.py:48-56）**：节点向量矩阵一次性堆出（scripts/evaluate_anchor_recall.py:49），维度与查询嵌入不符直接 parser.error 拒跑——只接受 MiniLM 构建的图（scripts/evaluate_anchor_recall.py:50-51）；向量路是裸 numpy 的 L2 距离全量 argsort（scripts/evaluate_anchor_recall.py:54），每题 O(N) 暴力扫，不走向量库索引；关键词路借引擎私有方法 `_keyword_search`，limit 硬编码 60（scripts/evaluate_anchor_recall.py:55，方法本体在 memory/query_engine.py:917，默认 limit 是 40——脚本显式放大了召回口径）。
- **五档网格与打分（scripts/evaluate_anchor_recall.py:58-72）**：五组 `(anchors, normal_k, multihop_k, maximum_nodes)` 配置——第一组就是 JevMemConfig 默认值组合，后四组把 anchors 从十扫到三十、top_k 与 maximum_nodes 同步放宽（scripts/evaluate_anchor_recall.py:58-59，默认值对照 memory/jev_mem_config.py:37-42）。每题选择逻辑复刻线上种子段：category 1（多跳）用 multihop_k 否则 normal_k（scripts/evaluate_anchor_recall.py:62）；两路列表按 `pool` 截断后进 `_rrf_fusion`（scripts/evaluate_anchor_recall.py:63-64，融合方法在 memory/query_engine.py:59）；融合结果取前 `min(anchors, maximum_nodes, top_k)` 个节点的 dia_id（scripts/evaluate_anchor_recall.py:65）；与金标 evidence 集合求交算 recall 与 complete（scripts/evaluate_anchor_recall.py:66-68）。两组指标聚合：mean_evidence_recall（平均证据召回率）与 all_evidence_fraction（全部证据都在种子里的题目占比）（scripts/evaluate_anchor_recall.py:69-72）。
- **报告落盘（scripts/evaluate_anchor_recall.py:73-79）**：report 带 method 自述字段，原话声明 "no Jev traversal or answer generation"（scripts/evaluate_anchor_recall.py:74）——数字被引用时口径自带；写文件并打印同内容（scripts/evaluate_anchor_recall.py:78-79）。

## 外部连接

延迟 import 五个仓内模块（scripts/evaluate_anchor_recall.py:28-33）：jev_mem/datasets/locomo 的加载器、NetworkXGraphDB、MockEncoder、QueryEngine、TemporalResonanceGraphMemory、NumpyVectorDB。对 query_engine 的依赖踩在**两个私有方法**上（_keyword_search 与 _rrf_fusion，memory/query_engine.py:917 与 memory/query_engine.py:59）——跨模块调私有成员，重构雷区。dia_id 属性的写入方在 LoCoMo 写路径（memory/memory_builder.py:484），格式 `D会话:轮次`，与数据集 evidence 字段（jev_mem/datasets/locomo.py:26）同源，这是 selected 与 gold 能求交的前提。反向被引：零——README、docs、CI、测试均未提及（grep 全仓实测），图谱 out=2 是到函数级子节点的包含边。输入依赖两个前置产物：某个 LoCoMo benchmark 跑完留下的缓存目录（graph.json + keyword_index.json + 带 embedding_vector 的节点）与 data/locomo10.json。

## 数据流

离线单向流：已保存图 →（每题）增强后的查询 → MiniLM 嵌入 → 向量路全量 L2 排名；并行关键词路倒排排名 → 两路截断入 RRF 融合 → 前 anchor_count 个 dia_id 与金标集合求交 → 单题 recall/complete → 按五档配置聚合 → JSON 报告（含 sample 编号、memory 路径、问题数、method 口径、experiments 数组）。全程无 Jev、无 LLM、无写路径——输出只描述检索种子，不描述系统行为。

## 设计决策

**为什么复刻而不是调用 engine.query**：线上 query 在种子之后还有 Jev 决策、遍历扩展、答案组装（见第 10 篇），全链路没法离线扫参。脚本把"种子选择"这一段公式抽出来冻结（scripts/evaluate_anchor_recall.py:62-65），换来可扫五档超参的自由。代价是**漂移风险**：query_engine 的种子逻辑将来一改，这里不会跟着变，数字 silently 过期——method 字段（scripts/evaluate_anchor_recall.py:74）只声明了不测什么，没声明复刻自哪个版本。

**金标隔离的贯彻方式与第 30 篇同构**：evidence 只在求交打分时出现（scripts/evaluate_anchor_recall.py:66），排序输入只有查询文本与图内容。这让它与 baseline 那种金标直取形成对照组——同一个仓里，诊断脚本比 baseline harness 更守规矩。

**值得点名的毛边**：其一，向量路用 L2 距离而线上 NumpyVectorDB 走的是各自的相似度口径，两路融合的相对次序可能因此与线上有差——诊断近似性没有声明；其二，关键词 limit 硬编码 60（scripts/evaluate_anchor_recall.py:55），与线上默认 40 不同档，scan 的口径比日常宽；其三，MockEncoder/NumpyVectorDB 是构造器配重（scripts/evaluate_anchor_recall.py:38-39），读者容易误以为向量走了它们，注释为零；其四，若缓存图节点为空，`vectors.shape[1]`（scripts/evaluate_anchor_recall.py:50）会先于友好的 parser.error 抛 IndexError——防御顺序反了；其五，单 sample 设计（scripts/evaluate_anchor_recall.py:43 的 `[args.sample]`），结论天然只代表一个对话样本，扫参结论外推到其他样本要自担风险。

## 新人提示

先读 scripts/evaluate_anchor_recall.py:1-5 的三行自白与第 74 行的 method 字段，口径意识先于代码。跑法：先有一份 MiniLM 构建的 LoCoMo 图缓存，然后 `python scripts/evaluate_anchor_recall.py --memory <缓存目录> --output reports/anchor_recall.json`；报告是纯 JSON，五档 experiments 直接对比 mean_evidence_recall 的边际增益决定 anchor_count。

四个提醒：一，图的 embedding 维度必须与 MiniLM 对得上，否则 parser.error（scripts/evaluate_anchor_recall.py:50-51），换 embedding 后的旧图别拿来跑；二，引用数字时必须带上"种子覆盖率、非端到端"的限定（scripts/evaluate_anchor_recall.py:74 原话），混进成绩表就是口径事故；三，query_engine 重构种子段或改 _keyword_search/_rrf_fusion 签名时，本脚本会静默失真或直接 AttributeError——它没有测试护栏，改检索核心后应手工重跑对数；四，想扫别的超参就改第 58-59 行的元组表，注意 anchors 大于 top_k 时实际选择数被 min 截到 top_k（scripts/evaluate_anchor_recall.py:65），网格设计时别被 "anchor_count=30" 的标签骗了——normal_k=30 档位下它取不满三十。
