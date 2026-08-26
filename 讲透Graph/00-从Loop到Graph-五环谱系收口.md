# 00 · 开场白：从 Loop 到 Graph——五环谱系的收口

> 讲透Graph 第 00 章 | 建章 2026-08-26
> 前情提要：讲透Prompt（怎么问）→ 讲透Context（给什么）→ 讲透Harness（挂什么）→ 讲透Loop（怎么循环）。四环都在优化**一个**模型或**一个** agent。本章讲为什么第五环必然出现，以及它为什么偏偏是"图"。

## 1. 直觉层：一张桌子坐不下的智能

一个类比：**单干户 → 作坊 → 公司**。

- Prompt/Context Engineering 是把一个员工培训好（怎么给他说清楚任务、给他什么资料）；
- Harness/Loop 是给这个员工配工具、教他自我检查（draft→check→redo）；
- 但当任务需要** heterogeneous 专业分工、子任务互相依赖、并行执行、独立验证、持久状态**时，单个员工再强也不行——你需要一家公司：有组织架构（谁向谁汇报）、有流程图（先做什么后做什么）、有台账（现在做到哪了）。

**Graph Engineering 就是给 agent 系统画组织架构图、流程图和台账的学科**——而且这三样东西恰好都是图：任务图（流程）、agent 拓扑（组织）、运行状态（台账）。

arXiv 2608.21156 给的正式说法：个体智能（individual intelligence）存在结构性上限，单纯增强单个 agent 的能力或上下文无法突破——智能必须**分布**到多个专门组件并在**系统层**组织起来（System Intelligence）。而这个组织层最自然的数学载体就是图。

## 2. 一个词，两个灵魂：双分支

"Graph Engineering" 在 2026-07 被引爆时，实际上有两群人在用同一个词说两件事：

| | **Execution Graph 分支** | **Context Graph 分支** |
|---|---|---|
| 图里的节点 | 任务、LLM 调用、工具、审批门 | 实体、事实、决策、事件 |
| 图里的边 | 控制/数据依赖（接着做什么） | 类型化领域关系（怎么相关） |
| 回答的问题 | "What runs next?" | "What is known & how related?" |
| 代表 | LangGraph、AutoGen GraphFlow、AFlow | GraphRAG、Neo4j、Zep/Graphiti |
| 血统 | 状态机、工作流引擎、编译器 | 知识图谱、语义网、RAG |

SurrealDB 2026-08-13 的批判一针见血：**"graph engineering is missing a graph"**——大家在图上画 agent，脚下却还是向量库里一堆扁平 chunk。完整形态必须双图齐备且跨轮一致（每轮 read→think→write：从 context graph 读，在 execution graph 里想，写回两边的图）。ContextOS 进一步分成四张图：Execution / Message（谁能告诉谁什么）/ Knowledge / Decision-lineage（这动作为什么发生）。

**本单元的立场**：把两支都讲透，再把综述的三支柱（Task Organization / Agent Coordination / Runtime State Management）当作统一骨架。

## 3. 类型边：一个比特的差，一个世界的差

Context Graph 分支最深的洞察（vanja.io）：

- 无类型边说"这两个东西**相关**"；
- 类型边说"**怎么**相关"：`supersedes`（替代）、`depends_on`（依赖）、`caused`（导致）、`decided_by`（由谁决定）、`blocks`（阻塞）。

"ADR-007 supersedes ADR-003" 是一条**可以据此行动的声明**；"ADR-007 在嵌入空间里靠近 ADR-003" 是一个**需要人猜的邻近信号**。这就是为什么"需要图的问题都是藏着动词的问题"——那些动词（导致/替代/依赖/批准/阻塞）就是穿着人类衣服的边。由此得出本单元最反直觉的口号：

> **Representation, not prompting, is the leverage.** 把知识表示做对，prompt 就变无聊了——无聊的 prompt 才是好 prompt。

## 4. 术语战争 34 天：一次术语考古（2026-07-18 → 08-21）

| 日期 | 事件 | 性质 |
|------|------|------|
| 07-18 | Steinberger 发问 + "Loop Engineering Is Dead" | 引爆 |
| 07-22 | LangChain：我们做了三年，65M+/月下载 | 厂商收编 |
| 07-24 | vanja.io：typed edges 论 | 独立思考 |
| 07-30 | 四条件 preprint | 形式化 |
| 07-31 | ContextOS 生产 playbook | 落地 |
| 08-13 | SurrealDB 双图批判 | 反思 |
| 08-21 | arXiv 综述（35 作者） | 学术收编 |

LangChain 自己说得很诚实：这些术语"半营销"，但每个都对应真实的设计难题。**判别方法**：看有没有独立收敛——Neo4j（数据库厂商）、Zep（记忆创业公司）、LangChain（编排框架）三家利益完全不同，却在"结构化关系优于扁平相似"上独立收敛，这是迁移为真的最强信号。同时记住 GEM 2026 的反例实测：**简单场景 plain RAG 够用，GraphRAG 只在复杂关系查询占优**——图是税，别为不需要多跳的问题交图税。

## 5. 与四个姊妹篇的精确接口

1. **← 讲透Context**：CE 问"窗口里放什么"，但**决定什么进窗口的越来越是图**（context graph 是 CE 的上一楼层）。CE 的 compaction/memory/sub-agent 三逃生通道，在图世界里对应 fact invalidation / 图外持久化 / 子图隔离；
2. **← 讲透Loop**：loop = 最简单的有向**环**图（LangChain 原话，LangChain 就建在 LangGraph 上）。讲透Loop E1-E3 的全部教训（早停/漏检放大/熔断）在图上的推广就是：**每跳准确率的乘法灾难**（E5 要跑）；
3. **← 讲透Harness**：harness 组织单个 agent 的工具环境；execution graph 组织多个 agent 的协作拓扑。综述把 Harness Engineering 列为 GE 的前置台阶；
4. **← 讲透Prompt**：四条件里的"结构/内容分离"——图拓扑不变，prompt 可换。prompt 是节点里的内容，图是节点间的宪法。

## 6. 为什么 work4ai 自己就是活案例

vanja.io 的判断：互链的 markdown 知识库 = **proto-graph-engineering**（"你的 wikilinks 就是边"）。本仓库完全符合：

- "新卡必须挂网"宪法 = **加边操作**（孤儿文件 = 死亡内容 ≈ 孤立节点）；
- 孤儿率 <10% 健康线 = **死节点监控**；
- MATH_LOOP_ENGINE 的知识森林（多父 DAG）= 显式的学习进度图；
- AGENTS.md 的"改动讲透系列须保持五幕结构" = **prescribed ontology**（前置类型系统）；
- 本记忆系统（updated 时间戳 + 有效/过期标记）≈ 朴素的 **bi-temporal**。

E6 将实测这张图：节点数、边数、孤儿率、度分布、hub 节点。这是全仓库第一个用图论工具照镜子自己的实验。

## 7. 本单元的批判预告（Ch12 详述）

- **图税**：实体抽取的 LLM 调用成本 + 本体维护人力 + 图数据库运维（GraphRAG 索引一个语料库 = 数百次 LLM 调用起步）；
- **本体腐化**：类型系统没人维护就烂（"没有治理的活图不是记忆，是 undead knowledge——活的、持久的、且不再连着真相"）;
- **retrieval-generation gap**：检索增强不按比例转化为生成质量（GEM 2026 实测）——评测要**数 hops（每跳都对才算对），别数 top-10**；
- **不是所有任务都要图**：deep research 类开放式任务硬塞进确定性路径是错的（LangChain 自曝：自家 deep research 从 LangGraph 工作流迁到了 agentic core loop）。

---

📌 **下一步**：Ch01 图的解剖学 + E1（类型边 vs 相似度命中的规则模拟）。
✍️ **练习**（建单元首批）：
1. 在你的 work4ai 里找 3 对文件：一对只有"主题相似"关系、一对有真实引用关系、一对引用关系还带类型（如"替代了/细化了"）——分别写出问什么问题时必须靠第三种；
2. 把讲透Loop 的 E1（自评停止 87.3% 早停）翻译成图语言：那个 loop 是几边形？哪条边带"验证通过"的谓词？
3. 数字题：每跳准确率 0.95 的 8 跳链，链路正确率多少？（E5 会给答案，先手算：0.95^8 ≈ ?）
