# 108 · Graph Engineering 五环谱系专题（2026-08 术语战争与架构收敛）

> 前沿与媒体 专题清单 | 核实 2026-08-26，全部一手来源 | 深读单元：[`讲透Graph/`](../讲透Graph/README.md)（README + papers.md + E5/E6 实验）

## 一句话

继 prompt engineering（2022）→ context engineering（2025）之后，2026-07-18 X 引爆 **graph engineering**：用显式、动态、演化的图结构组织任务、agent 与运行状态——34 天内完成 术语引爆→厂商收编→形式化→学术综述（arXiv 2608.21156，35 位作者）。

## 五环谱系（arXiv 2608.21156 官方分层）

| 环 | 管什么 | work4ai 对应单元 |
|----|--------|-----------------|
| Prompt Engineering | 引出模型能力（怎么问） | 讲透Prompt |
| Context Engineering | 管理信息访问（给什么） | 讲透Context |
| Harness Engineering | 组织工具资源（挂什么） | 讲透Harness |
| Loop Engineering | 持续反思自进（怎么循环；loop=有向环图） | 讲透Loop |
| **Graph Engineering** | **组织任务/agent/状态成系统（System Intelligence）** | **讲透Graph** |

## 双分支（同一个词，两个灵魂）

- **Execution Graph**（LangGraph 65M+/月下载）：节点=任务/调用/工具，边=控制依赖，答 "What runs next?"；agent graph 通常**不是 DAG**（生产需要环）
- **Context Graph**（GraphRAG→Neo4j→Zep/Graphiti 20k★）：节点=实体/事实/决策，边=类型化关系，答 "What is known & how related?"；核心机制 **typed edges / bi-temporal / fact invalidation / provenance**
- SurrealDB 批判（08-13）：只做一半="missing a graph"，双图须跨轮一致（read-think-write）

## 关键一手资源

- 综述：arXiv 2608.21156 + github.com/DEEP-JLU/Awesome-Graph-Engineering（159★）
- 记忆图：arXiv 2501.13956（Zep：DMR 94.8%、LongMemEval +18.5%/-90% 延迟）
- 生产 playbook：ContextOS（四图分类：Execution/Message/Knowledge/Decision-lineage）
- 批判：GEM 2026 "Is GraphRAG Needed?"（简单场景 plain RAG 够用；retrieval-generation gap）

## 给本仓的启示（讲透Graph E6 实测）

work4ai 自己就是 proto-graph（wikilinks=edges）：3058 节点/7321 边/自产层孤儿率 31.5%（超标，最大孤儿簇 ad-mastery/）——"新卡必须挂网"宪法即加边操作，孤儿率即死节点监控。
