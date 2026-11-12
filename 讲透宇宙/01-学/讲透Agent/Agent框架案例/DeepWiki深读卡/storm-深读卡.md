# storm 深读卡 —— 多视角提问+检索+大纲驱动的维基级长文自动写作系统

> **定位**：斯坦福 Oval 组的 STORM（Synthesis of Topic Outlines through Retrieval and Multi-perspective question asking），LLM 驱动从零写出带引用的维基式长文，NAACL 2024 最佳论文；同仓衍生人机协作版 Co-STORM。核心差异化：不直接让 LLM 提问，而是"先发现视角、再用视角引导提问"。
> **本地**：`repos/storm`（stanford-oval/storm）｜**深读**：deepwiki 24 子页归档 `deepwiki/storm/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 抽象接口层 `interface.py` | 全系统契约 | `Retriever`/`Module`/`Engine`/`Agent`/`InformationTable`/`Article` |
| LM 基础设施 `lm.py` | 100+ 提供商统一接入 | `LitellmModel`（LRU 3000 + 磁盘两级缓存、线程安全 token 计数） |
| 检索层 `rm.py` + `encoder.py` | 11 种检索后端 + 嵌入 | `YouRM`/`BingSearch`/`VectorRM`(Qdrant)/`StanfordOvalArxivRM`、`Encoder` |
| STORM 引擎 `storm_wiki/` | 线性 4 阶段流水线 | `STORMWikiRunner`（knowledge curation→outline→article→polish） |
| Co-STORM 引擎 `collaborative_storm/` | 迭代协作话语循环 | `CoStormRunner`（`warm_start()`→`step()`→`generate_report()`） |
| Agent 层 | 话语参与者 | `CoStormExpert`/`Moderator`/`SimulatedUser`/`PureRAGAgent`(基线) |
| 数据结构 | 全程信息载体 | `Information`/`DialogueTurn`/`StormInformationTable`/`KnowledgeBase`(mind map) |
| 前端 `frontend/demo_light/` | Streamlit 演示 | 状态机式文章生成进度页 |

## 二、核心机制

1. **视角引导提问（本仓库的灵魂）**：先检索相似主题的维基条目、抓其目录树，用 DSPy `GenPersona` 生成一组"编辑人设"；每个人设驱动一场 `WikiWriter`×`TopicExpert` 模拟对话（专家走 QuestionToQuery→检索→`is_valid_wikipedia_source` 可靠性过滤→AnswerQuestion 的 retrieve-then-generate，检索不到就明说不会而非幻觉），多场对话 ThreadPool 并行。创新点：提问的广度来自"视角多样性"这个显式变量，而非一次性 prompt。（来源：Knowledge Curation Module 页）
2. **URL 索引信息表**：所有对话产物聚合成 `StormInformationTable`——按 URL 聚合 + 向量语义检索，让"研究阶段"的原始积累可被大纲生成和逐节写作持续复用；写作为大纲驱动、逐节检索引用，引用管理贯穿到底。（来源：STORM Data Structures / Outline and Article Generation 页）
3. **Co-STORM 协作话语 + 动态 mind map**：`DiscourseManager` 按轮次策略调度 Expert/Moderator/User；Moderator 用"未被引用信息重排序"——`score = (1-query_sim)^0.5 × (1-cited_sim)^0.5 × claim_filter`——挑出检索到但没人用的片段生成接地问题，专治对话僵化；`KnowledgeBase` 树随话语不断 insert/expand/reorganize，最终报告由遍历知识树合成，而非对话历史拼接。（来源：Agent System / Collaborative Modules 页）
4. **多 LM 成本工程**：按任务分级配模型——STORM 5 个 LM（对话模拟/提问用便宜模型，正文写作用最强模型）、Co-STORM 6 个（含专门的 discourse_manage_lm 和 knowledge_base_lm），叠加两级缓存与 token 追踪，是"多 LLM 系统"范式的教科书实现。（来源：Overview / Language Model Integration 页）

## 三、与讲透系列的对位

| STORM/Co-STORM 概念 | 讲透系列对应概念 |
|---|---|
| WikiWriter→TopicExpert 每轮"提问→转查询→检索→答" | 讲透Agent 的 ReAct 循环（提问即 Thought，检索即 Action，带引用回答即 Observation） |
| personas 并行多场模拟对话（fan-out 后聚合） | 讲透多Agent协作 的角色分工与并行编排模式 |
| DiscourseManager 轮次策略 + Moderator 介入 | 编排模式：orchestrator 调度 + 主持者防止跑偏 |
| KnowledgeBase mind map 持续重组 | 记忆机制：共享结构化长期记忆（对比对话历史=纯工作记忆） |
| Moderator 未用信息检测、2500 词历史截断 | 上下文工程：信息利用率控制与上下文预算管理 |

## 四、关键入口

```python
knowledge_storm/storm_wiki/engine.py                        # STORMWikiRunner.run()：4 阶段流水线总控
knowledge_storm/storm_wiki/modules/knowledge_curation.py    # 核心创新：ConvSimulator/WikiWriter/TopicExpert + DSPy 签名
knowledge_storm/storm_wiki/modules/persona_generator.py     # 视角发现：找相似条目→抄目录→生成 personas
knowledge_storm/storm_wiki/modules/storm_dataclass.py       # StormInformationTable：URL 索引+语义检索的信息底座
knowledge_storm/collaborative_storm/engine.py               # CoStormRunner：warm_start()/step()/generate_report()
knowledge_storm/collaborative_storm/modules/co_storm_agents.py        # 4 类 Agent + Moderator 重排公式
knowledge_storm/collaborative_storm/modules/information_insertion_module.py  # KB 生长：嵌入排序/逐层导航插入
knowledge_storm/interface.py + lm.py + rm.py                # 抽象契约 / 多 LM 分级 / 11 种检索后端
```

## 五、深读子页地图（24 页精选 6）

1. **STORM Wiki Generation System**（第 4 页）——全自动流水线鸟瞰，两阶段（pre-writing/writing）设计动机
2. **Knowledge Curation Module**（第 6 页）——灵魂机制逐行解剖：persona 生成、对话时序图、并行策略、信源过滤
3. **Knowledge Base System**（第 11 页）——mind map 数据结构：KnowledgeNode 树、UUID 引用、两种插入策略与重组
4. **Agent System**（第 12 页）——四类 Agent 接口与 Moderator 未用信息重排序算法（含完整公式）
5. **Collaborative Modules**（第 13 页）——DiscourseManager 轮次策略、warm start 管线、模块集成模式
6. **Language Model Integration**（第 15 页）——多 LM 任务分级配置与两级缓存实现细节

## 六、与"我们"的关系（一句话）

对学 Agent 的人，这是"把 RAG 从一次问答推向完整研究写作流程"的最佳论文级参考实现——提问工程、大纲驱动编排、共享结构化记忆三条经验可直接迁移到任何长任务 Agent。

---
生成：2026-08-21 · deepwiki 24 页全归档
