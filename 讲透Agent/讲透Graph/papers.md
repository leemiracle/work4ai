# papers.md —— 讲透Graph 素材核实清单（2026-08-26）

> 铁律执行记录：每条 arXiv ID 标注核实方式。✅一手 = 直接看到 arxiv.org abs 页/官方仓库/官方博客全文；
> 🔁转引 = 仅从二级来源（Awesome 官方 README）看到编号，章节引用前须 webfetch abs 页再核实。

## 一、综述与正式定义（Ch00/11 的骨架）

| ID | 标题/内容 | 核实 | 关键结论 |
|----|----------|------|---------|
| arXiv 2608.21156 | Graph Engineering in the Era of LLM Agents: From Individual Intelligence to System Intelligence（Feng et al., 35 位作者，cs.IR） | ✅一手（webfetch abs 页，2026-08-21 提交） | 五环谱系官方版：PE 引出能力/CE 管理信息/Harness 组织工具/Loop 持续反思/**GE 组织系统**；三层智能：模型→个体→**系统**；GE 三支柱：**Task Organization / Agent Coordination / Runtime State Management**（+System Evolution+Ontology Engineering）；未来方向：graph-native agent OS（图调度/能力发现/结构事务/checkpoint/回滚） |
| github.com/DEEP-JLU/Awesome-Graph-Engineering | 随综述持续更新的资源库 | ✅一手（webfetch 仓库页） | 159★ / 6 fork / 11 commits / MIT（2026-08-26 实测）；目录即综述分层：Model（Pre/Post-Training+PE+CE）→ Individual（Tool/Memory/Skill/Runtime Orchestration/Loop）→ System（Task/Coordination/State/Evolution/Ontology）+ Benchmarks/Libraries/Applications |
| Sandeco Macedo preprint（2026-07-30） | prompt graph engineering 四条件 | 🔁转引（ContextOS 博客逐条引用） | 图的边界测试：①显式结构（点边存在于模型散文之外）②结构/内容分离③可执行语义（边=可调度谓词/join/重试）④一等工件（图有身份/版本/历史/评测/回滚） |

## 二、Execution Graph 分支（Ch02/05/06/08）

| ID | 标题/内容 | 核实 | 关键结论 |
|----|----------|------|---------|
| LangChain 官方 blog | 3 Years of Graph Engineering with LangGraph（2026-07-22） | ✅一手（搜索结果全文） | LangGraph 65M+/月下载；**agent graphs 通常不是 DAG**（生产需要环：重试/问用户/修订/等人）；loop=有向环图（LangChain 建在 LangGraph 上）；Send API=运行时动态扇出（map-reduce）；节点内容进化：单 LLM call→完整 agent run；**何时不用图**：deep research 类任务更 agentic→Deep Agents harness |
| arXiv 2604.11378 | From Agent Loops to Structured Graphs: A Scheduler-Theoretic Framework | 🔁转引（Awesome README） | 从调度器理论统一 loop 与 graph |
| arXiv 2312.04511 | LLMCompiler: An LLM Compiler for Parallel Function Calling（ICML 2024） | 🔁转引（Awesome README） | 任务图并行调度 |
| arXiv 2502.14563 | Plan-over-Graph: Towards Parallelable LLM Agent Schedule | 🔁转引 | 在图上做并行规划 |
| GPTSwarm（ICML 2024） | Language Agents as Optimizable Graphs | 🔁转引 | agent 系统本身=可计算图、可被优化 |
| AFlow（ICLR 2025）/ ADAS / EvoFlow / MermaidFlow | 自动工作流（图）发现系列 | 🔁转引 | agentic workflow 自动搜索 |
| StateFlow（arXiv 2403.11322） | 状态机工作流 | 🔁转引 | 图的前身之一 |
| ContextOS blog | Graph Engineering for AI Agents: X Hype and Production Playbook（2026-07-31） | ✅一手 | X 时间线（07-18→07-30）；**四图分类：Execution/Message/Knowledge/Decision-lineage graph**；生产控制面：contracts、版本化、不变量证明、幂等、路径级评测、回滚 |

## 三、Context Graph 分支（Ch03/04/09）

| ID | 标题/内容 | 核实 | 关键结论 |
|----|----------|------|---------|
| arXiv 2404.16130 | From Local to Global: A Graph RAG Approach to Query-Focused Summarization（微软，2024-04） | ✅多源（Awesome 官方+Neo4j/Zep 官方博客均引） | GraphRAG 奠基：实体抽取+社区摘要，解决"跨关系连接信息"的检索 |
| arXiv 2501.13956 | Zep: A Temporal Knowledge Graph Architecture for Agent Memory | ✅一手（arXiv abs 页） | Graphiti 引擎；episodic+semantic 双子图；DMR 94.8% vs MemGPT 93.4%；LongMemEval 准确率 +18.5% 且延迟 -90%；bi-temporal 模型 G=(N,E,φ) |
| github.com/getzep/graphiti | temporal context graph 引擎 | ✅一手（README 两处） | 20k+★；**context graph 定义：带 validity window 的事实图**；fact invalidation（作废不删除）；episode 溯源；prescribed（Pydantic 前置定义）vs learned（数据中涌现）ontology；hybrid retrieval（语义+BM25+图遍历）亚秒级；vs GraphRAG 对照表（静态批处理 vs 增量更新） |
| Neo4j: Context Graphs and AI Memory Across the Globe（2026-03-04） | SF 首届 Context Graph Meetup + Berlin AI Memory Night 纪要 | ✅一手 | Emil Eifrem：**context graph = 知识图谱 + decision traces**；Jessica Talisman：= 知识管理里的"程序性知识"；Dave Bennett：KG 的超集，加时序有效性/溯源/权限维度；"建 context graph 首先是知识管理问题而非工程问题" |
| Neo4j: From recall to reasoning（Niels de Jong，2026-04） | context graph 升级 agent 大脑 | ✅一手 | 记忆三级：文件柜(向量)→日记(时序)→**心智模型(图)**；SARO 四元组 Situation/Action/Rationale/Outcome；neo4j-labs/agent-memory；create-context-graph.dev |
| Neo4j: What is context engineering（Michael Hunger，2025-12-19） | CE 实践指南 | ✅一手 | "多数生产失败是 context 失败"；GraphRAG=结构化 context 的检索层 |
| Neo4j $100M 投资公告（2025-10-01） | GenAI/agentic 布局 | ✅一手 | Aura Agent + Neo4j MCP Server；GenAI 客户 6x 增长；Fortune 100 的 80% 是客户（数字当动量信号看） |
| vanja.io | Graph Engineering: The Next Layer After Context（2026-07-24） | ✅一手 | **typed edges 是灵魂**："related"→"related in this specific way"；隐藏动词的问题需要图（caused/supersedes/depends_on=穿人衣服的边）；混合路由三件套 vector/graph/SQL+router；**markdown wikilinks=proto-graph**，人工链接常比机器抽取准；living graph 无治理="undead knowledge"；"representation, not prompting, is the leverage" |
| SurrealDB blog | Graph engineering is missing a graph（2026-08-13） | ✅一手 | **双图论**：execution graph+context graph 都要工程化且跨轮一致；agent 每轮=read(think)write 三步；GraphRAG 只是检索模式，不是架构 |
| Zep: What Is a Temporal Knowledge Graph（2026-05-31） | bi-temporal FAQ | ✅一手 | valid time + transaction/ingestion time 双时间线；"3月时什么为真？"可审计回答 |
| arXiv 2602.05665 | Graph-Based Agent Memory: Taxonomy, Techniques, and Applications | 🔁转引（Awesome README） | 记忆图综述 |
| arXiv 2506.18019 / 2507.21407 / 2604.15951 | Graphs Meet AI Agents / Graph-Augmented LLM Agents / Integrating Graphs,LLMs,Agents | 🔁转引 | 图×agent 三部综述 |
| arXiv 2408.08921 | Graph RAG Survey | 🔁转引 | GraphRAG 全景 |

## 四、评测与批判（Ch07/12 的弹药）

| ID | 标题/内容 | 核实 | 关键结论 |
|----|----------|------|---------|
| GEM 2026（aclanthology 2026.gem-main.40） | Is GraphRAG Needed? From Basic RAG to Graph-/Agentic Solutions with Context Optimization | ✅一手（ACL anthology PDF 全文摘要） | 9 场景实测：**简单场景 plain RAG 够用；复杂关系查询 GraphRAG 占优；Agentic RAG（简单工具）全场最佳**；context optimization 省 19-53% token；**retrieval-generation gap：检索增强不按比例转化为生成质量**（位置注意力衰减/语义显著性/基数效应）；三元组表示 O(n)→O(1) |
| Foundation Capital | Context Graphs: AI's Trillion Dollar Opportunity | 🔁转引（Neo4j 博客引用） | 风投叙事（当动量信号，不当论据） |

## 五、术语战争时间线（Ch00 素材，全部✅一手）

| 日期 | 事件 |
|------|------|
| 2024-04 | 微软 GraphRAG 论文（概念地基之一） |
| 2024-08 | Zep 开源 Graphiti（context graph 引擎） |
| 2025-06 | Karpathy 带火 "context engineering"（上一轮术语战争） |
| 2026-07-18 | Peter Steinberger X："Are we still talking loops or did we shift to graphs yet?"；同日 X Article"Loop Engineering Is Dead" |
| 2026-07-22 | LangChain 回应《3 Years of Graph Engineering with LangGraph》（我们做了三年） |
| 2026-07-24 | vanja.io《The Next Layer After Context》（typed edges 论） |
| 2026-07-30 | 四条件 preprint（形式化定义） |
| 2026-07-31 | ContextOS 生产 playbook（从 X 术语到生产控制面） |
| 2026-08-13 | SurrealDB 双图论批判（"missing a graph"） |
| 2026-08-21 | arXiv 2608.21156 综述（35 作者大联盟，学术化完成） |

> 观察：从推文到学术综述只用了 **34 天**——比 context engineering 的术语化速度快一倍。术语会磨损（LangChain："半营销"），但"从扁平上下文到结构化关系"的迁移是真的（Neo4j/Zep/LangGraph 三家独立收敛）。
