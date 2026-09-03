# 讲透 Graph：从个体智能到系统智能（Graph Engineering）

> 知识卡宇宙：`讲透X` 系列 | 三层宪法：**直觉 → 公式 → 代码（bash 跑通）** | 五幕：直觉→数学→代码→不足→应用
> 定位：`讲透Prompt` `讲透Context` `讲透Harness` `讲透Loop` 四个姊妹篇的**收口环**——前四环优化"一次调用/一个 agent"，本单元讲"怎么用图把多个智能组件组织成一个系统"。
> 谱系依据：arXiv 2608.21156（2026-08-21，35 位作者大联盟）官方分层：**Prompt 引出能力 → Context 管理信息 → Harness 组织工具 → Loop 持续反思 → Graph 组织系统**。
> 本章证据标准：每个知识点配一个真实可跑实验（`experiments/`），arXiv ID 一律 webfetch 核实（见 `papers.md`）。

## 互链

> 图的第一性原理（图论/谱/GNN/WL/马尔可夫）见 [`讲透图`](../../讲透图/README.md)——本单元是「系统之图」象限，与「数学·学习·状态之图」互补。

## 为什么要有这个单元

"Graph Engineering" 这个词 2026-07-18 才在 X 上被引爆（Peter Steinberger："Are we still talking loops or did we shift to graphs yet?"），**12 天内**走完 术语引爆（07-18）→ LangChain 回应（07-22）→ 独立文章（07-24）→ 形式化定义 preprint（07-30）→ 生产 playbook（07-31）→ 双图论批判（08-13）→ 学术综述（08-21）全程。但架构本身已有三年积累（LangGraph 65M+/月下载、Graphiti 20k★）。

本单元的三个增量：

1. **双图统一视角**：Graph Engineering 一词实为两个分支的合流——**Execution Graph**（把 agent 系统建成图，LangGraph 路线）与 **Context Graph**（把知识/记忆建成图，GraphRAG/Neo4j/Zep 路线）。SurrealDB 的批判（"graph engineering is missing a graph"）：只做一半 = 半个想法；
2. **数学下场**：per-hop accuracy 的乘法灾难（每跳 0.9，五跳只剩 0.59）——图系统的可靠性是链式乘法，这决定了"数 hops，别数 top-10"的评测哲学；
3. **活案例**：**work4ai 自己就是 proto-graph**——"新卡必须挂网"宪法 = 加边，孤儿率 <10% = 死节点监控，MATH_LOOP_ENGINE 知识森林 = 多父 DAG，本记忆系统 ≈ bi-temporal（valid time + 记录时间）。vanja.io 的判断："你的 wikilinks 就是边，人类维护的链接通常比机器抽取的更准"。

## 核心心智模型（一图流）

```
  五环谱系（arXiv 2608.21156：模型智能 → 个体智能 → 系统智能）
  ┌────────────────────────────────────────────────┐
  │ 模型智能  Prompt(怎么问) Context(给什么)          │ ← 讲透Prompt/Context
  │ 个体智能  Harness(挂什么) Loop(怎么循环)          │ ← 讲透Harness/Loop
  │ 系统智能  Graph(怎么组织成系统) ★ 本单元           │ ← 收口环
  └────────────────────────────────────────────────┘
                    图 = 系统的骨架，两根支柱：
        ┌───────────────────┬─────────────────────┐
        │ Execution Graph    │ Context Graph        │
        │ 任务图/agent拓扑/   │ 实体/类型边/时序事实/  │
        │ 运行状态(做什么)     │ decision traces(知道什么)│
        └─────────┬─────────┴──────────┬──────────┘
                  └──── 每轮 read-think-write 保持一致 ────┘
  关键机制：typed edges(怎么相关) · bi-temporal(何时为真) ·
           fact invalidation(作废不删除) · provenance(从哪来)
```

## 篇目表（目录宪法）

| # | 章节 | 核心实验 | 状态 |
|---|------|---------|------|
| 00 | [开场白：从 Loop 到 Graph——五环谱系收口与术语战争时间线](00-从Loop到Graph-五环谱系收口.md) | — | ✅ |
| 01 | [图的解剖学：节点、边、类型边——为什么偏偏是图](01-图的解剖学.md) | E1 类型边 vs 相似度命中（规则模拟）✅ 5/5 vs 0/5 | ✅ |
| 02 | [★ Execution Graph：把系统建成图](02-ExecutionGraph把系统建成图.md)（环不是 DAG、Send 动态扇出、节点内进化） | E2 拓扑模拟：线性/并行/DAG+join 成本 ✅ 49%省/验证税1.4× | ✅ |
| 03 | [★ Context Graph：把知识建成图](03-ContextGraph把知识建成图.md)（GraphRAG→Graphiti、bi-temporal、fact invalidation） | E3 bi-temporal 事实作废模拟器 ✅ 8/8 vs 6/8 vs 4/8 | ✅ |
| 04 | [记忆即图：episodic+semantic 双子图与 SARO 四元组](04-记忆即图.md) | E4 三元组抽取成本测算 ✅ 图税 6×/增量 7× | ✅ |
| 05 | [任务图：分解、依赖与调度](05-任务图.md)（LLMCompiler / Plan-over-Graph / AFlow） | 用 E2 | ✅ |
| 06 | [多 Agent 拓扑：supervisor、swarm 与可优化图](06-多Agent拓扑.md) | — | ✅ |
| 07 | [★ 混合检索三路由：vector/graph/SQL 与 retrieval-generation gap](07-混合检索三路由.md) | E5 每跳精度乘法灾难 ✅ p=0.9十跳剩34.9% | ✅ |
| 08 | [状态与溯源：decision lineage、checkpoint 与 graph-native OS](08-状态与溯源.md) | — | ✅ |
| 09 | [★ Ontology Engineering：类型系统是产品](09-OntologyEngineering.md)（POLE+O、prescribed vs learned） | 用 E1 的 edge_index | ✅ |
| 10 | [★ 活案例：work4ai 自己就是 proto-graph](10-活案例-work4ai就是proto-graph.md) | E6 仓库图健康度实测 ✅ 3058节点/7321边/真孤儿831/断链2155 | ✅ |
| 11 | [★ 前沿：综述 2608.21156 深读](11-综述深读.md)——三层智能、三支柱与未来方向 | — | ✅ |
| 12 | [不足与批判收尾：图税、本体腐化与 "Is GraphRAG Needed?"](12-不足与批判收尾.md) | E1-E6 负面结果汇总 | ✅ |

★ = 用户重点主题（双图 / 检索数学 / 本体 / 活案例 / 前沿）。
**诚实状态（2026-08-26 当日收官）**：00-12 章 + E1-E6 全部完成（6 实验可复现，`experiments/` 下 py + json + png）。素材核实见 `papers.md`。篇目表为物理链接（Ch10 的"逻辑边落成物理边"自我治理示范）。

## 实验环境（与前几个姊妹篇同一基座）

- **行为模拟器**：E1-E3/E5 用纯 Python 规则模拟（诚实标注：非 LLM 实验——讲透Loop 的教训：0.5B 在循环任务上退化为噪声，行为模拟器反而能干净地隔离变量）
- **活案例实测**：E4/E6 直接扫本仓库（LLM 调用数测算 / markdown 互链图健康度）
- 铁律：torch 小矩阵 set_num_threads(1)；matplotlib 中文字体 Noto Sans CJK SC；模型文件不进 git

## 与姊妹篇的分工（互链网）

| 单元 | 管什么 | 一句话 |
|------|--------|--------|
| 讲透Prompt | 单次调用里一句话怎么写 | 怎么问 |
| 讲透Context | 整个窗口里放什么 | 给什么（**图决定什么进窗口**——本单元是它的"上一楼层"） |
| 讲透Harness | 挂什么工具与资源 | 挂什么 |
| 讲透Loop | 怎么循环反思（loop = 最简单的有向环图） | 怎么循环 |
| **讲透Graph** | **怎么把任务/agent/状态/知识组织成系统** | **怎么组织** |

## 参考

- 综述与资源：`papers.md`（全部一手核实或官方转引标注）
- 断点续传：`RESUME-0826.md`
