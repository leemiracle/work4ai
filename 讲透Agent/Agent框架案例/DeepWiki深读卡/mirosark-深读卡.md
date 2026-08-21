# mirosark 深读卡 —— 把文档变成数百 Agent 的模拟社会：图谱接地 × 三平台联动 × 预测市场

> **定位**：MiroShark 自称 "Universal Swarm Intelligence Engine"——上传一份文档/政策草案，系统抽取 Neo4j 知识图谱，实例化数百个接地（grounded）的 AI Agent，在模拟的 Twitter/Reddit/Polymarket 上多轮互动，最终由 ReACT 分析 Agent 产出后验报告。差异化在于 persona 完全由图谱拓扑生成（非零样本）、启发式 BeliefState 认知模型、市场-媒体双向桥；模拟栈 Wonderwall 基于 CAMEL/OASIS 社会模拟框架，作者 aaronjmars（与 aeon 同作者），Flask+Vue3+Docker 全套工程完成度高。
> **本地**：`repos/mirosark`（aaronjmars/MiroShark）｜**深读**：deepwiki 31 子页归档 `deepwiki/mirosark/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 前端 Vue 3 | 5 步向导（上传→建图→环境→运行→报告）+ 实时时间线 | `Home.vue`、`Step1-5*.vue`、Hyperstitions v2.0 设计系统（EVA 橙绿风） |
| 后端 API（Flask） | 长任务编排与轮询 | `graph_bp`/`simulation_bp`/`report_bp`、`TaskManager` |
| 知识图谱 | 文档→本体→NER/RE→图谱 | `OntologyGenerator`、`NERExtractor`、`GraphBuilderService`（UNWIND 批量写 Neo4j） |
| Agent 生成 | 图节点→persona | `OasisProfileGenerator`（五层上下文 + web enrichment） |
| 模拟引擎 Wonderwall | 三平台并行多轮模拟 | `SocialAgent`（包装 CAMEL `ChatAgent`）、`Platform`、RecSys（twhin-bert/Reddit 算法） |
| 认知与记忆 | 信念演化/记忆压缩/跨平台意识 | `BeliefState`、`RoundMemory`、`CrossPlatformLog`、`RoundAnalyzer` |
| 分析报告 | ReACT 后验分析 | `ReportAgent`、`GraphToolsService`（InsightForge/interview_agents 等） |
| 存储 | 图 + 平台运行数据 | Neo4j（图谱）+ SQLite（每平台每 run 独立库） |

## 二、核心机制

1. **知识图谱接地（KG Grounding）**：与"零样本"社会模拟不同，每个 Agent 锚定一个 Neo4j 图节点，persona 由五层上下文合成——图属性、关系、语义检索、相邻节点、可选网络增强——"模拟世界里的每个人设都源自你上传的文档"，metric（影响力/活跃度）也从图拓扑推导。（来源：MiroShark Overview、OASIS Profile Generator）
2. **Market-Media Bridge 双向桥**：三平台 `asyncio.gather` 同步推进；Twitter/Reddit 的聚合情绪作为"Market News"注入 Polymarket 交易者 prompt，AMM 市场价格反向注入社交 Agent prompt（"市场认为该结果 70% 概率"）——社会舆论与预测市场价格互相驱动，这是区别于同类社会模拟框架的关键耦合。（来源：System Architecture & Data Flow、Belief State 页）
3. **启发式认知架构（省 LLM 钱）**：`BeliefState` 用公式而非 LLM 更新内部状态：stance(-1~+1)/confidence/trust 三维，resistance = 0.3 + confidence×0.7，nudge = (post_stance − current_pos) × trust × social_proof × novelty × 0.08 / resistance；配套 `RoundMemory` 滑动窗口压缩防上下文溢出、`CrossPlatformLog` 摘要让 Agent"知道自己在别的平台发过什么"、`RoundAnalyzer` 产出收敛/极化/转折点/病毒传播轨迹。（来源：Belief State, Round Memory & Cross-Platform Awareness）
4. **带硬约束的 ReACT 报告 Agent**：每节 min 2 / max 6 次工具调用、max 10 轮 Thought/Action/Observation——下限防幻觉（必须查图）、上限防死循环；工具含 InsightForge 深度洞察、PanoramaSearch、interview_agents（访谈模拟中的 Agent）、market_state（查 P&L）。（来源：ReportAgent: ReACT Loop & Report Lifecycle）

## 三、与讲透系列的对位

| MiroShark 概念 | 讲透系列对应概念 |
|---|---|
| ReportAgent 的 Thought/Action/Observation 循环 | 讲透Agent · ReAct 循环（同一模式，额外加了 min/max 工具调用硬约束） |
| GraphToolsService 工具集（InsightForge/interview_agents） | 讲透Agent · 工具调用/Function Calling |
| RoundMemory 滑动窗口 + CrossPlatformLog 摘要注入 | 讲透Agent · 记忆机制（上下文压缩/摘要式记忆） |
| SimulationManager 多进程隔离 + IPC 协议 + 多平台同步 | 讲透多Agent协作 · 编排模式（进程级环境隔离、回合制调度） |
| KG grounding + 语义检索组装 persona prompt | 上下文工程（检索增强的 prompt 组装） |
| BeliefState 信念轨迹 / 涌现行为分析 | 讲透学习型Agent · Agent 内部状态建模（用启发式更新替代学习） |

## 四、关键入口

```python
backend/app/services/ontology_generator.py       # LLM 从文档生成本体（JSON 校验+清洗）
backend/app/services/graph_builder.py            # NER/RE 抽取→Neo4j UNWIND 批量 upsert，线程池并行
backend/app/services/oasis_profile_generator.py  # 图节点→OASIS persona：五层上下文+web enrichment
backend/app/services/simulation_manager.py       # prepare_simulation 三段式：profiles→config→rounds
backend/scripts/run_parallel_simulation.py       # 三平台并行入口；belief/跨平台/市场上下文注入点（L162-170）
backend/wonderwall/social_agent/belief_state.py  # stance/confidence/trust + resistance 公式（L140-148）
backend/wonderwall/simulations/polymarket/platform.py  # AMM 预测市场：交易执行与价格源
backend/app/services/report_agent.py             # ReACT 报告：_generate_section_with_react（L560-575 约束）
```

## 五、深读子页地图（31 页精选 6）

1. **MiroShark Overview**（p1）— 5 步流水线 + 组件地图，10 分钟建立全局观
2. **Knowledge Graph Pipeline**（p4）— 文档→本体→NER→Neo4j 全链路
3. **OASIS Profile Generator**（p9）— persona grounding 五层上下文，"图怎么变成人"
4. **Belief State, Round Memory & Cross-Platform Awareness**（p15）— 全库最核心一页：认知/记忆/跨平台架构与全部公式
5. **ReportAgent: ReACT Loop & Report Lifecycle**（p17）— 带硬约束的 ReACT 参考实现
6. **Glossary**（p31）— 术语速查（Reality Seeds / Round Memory / Market-Media Bridge）

## 六、与"我们"的关系（一句话）

它是"知识图谱 × 社会模拟 × 受限 ReACT"三种 Agent 技术缝合进一个产品的完整工程样本——在别处很难同时看到 persona 图谱接地、可计算的观点演化公式和多平台耦合编排的落地细节。

---
生成：2026-08-21 · deepwiki 31 页全归档
