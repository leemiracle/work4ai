# localgpt 深读卡 —— 2023 隐私优先 RAG 先驱：全本地文档问答平台（混合检索+智能路由+语义缓存）

> **定位**：PromtEngineer 出品的 private/on-premise 文档智能平台（2023 爆款，本地 RAG 先驱项目之一）——文档不出内网的多格式问答系统。演进至今已非"纯 ingest+retrieve"原型：混合检索（向量+BM25）、late chunking、AI reranking、语义缓存、**RAG/直连 LLM 智能路由**、查询分解与答案验证都在——一份"企业级本地 RAG 该长什么样"的工程清单。
> **本地**：`repos/localgpt`（PromtEngineer/localGPT）｜**深读**：deepwiki 31 子页归档 `deepwiki/localgpt/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 文档处理 | 多格式摄取（PDF/DOCX/TXT/MD）、上下文富化、批处理 | ingestion pipeline、contextual enrichment |
| 检索 | **混合检索**（向量 + BM25）+ late chunking + AI reranking | hybrid search、reranker |
| 缓存 | 语义缓存（相似问题命中历史答案） | semantic cache |
| AI 集成 | Ollama 多模型 + HuggingFace embeddings + **智能路由**（RAG vs 直连 LLM） | smart routing |
| 应用层 | Web UI、会话管理、流式响应、实时进度 | web interface、session mgmt |
| API | RESTful + 健康监控 + 灵活配置 | API endpoints |
| 隐私 | 100% 本地运行，零外传 | on-premise |

## 二、核心机制

1. **智能路由（RAG vs direct LLM）**：查询先分类——闲聊/通用问题直连 LLM 省检索，文档相关问题才走 RAG 管线——2023 年即提出"不是所有查询都值得检索"的成本意识。
2. **混合检索 + late chunking + rerank 三连**：向量与 BM25 双路召回，late chunking（先全文嵌入后切块）保长文档语义完整，AI reranker 精排——本地 RAG 检索质量的完整配方。
3. **语义缓存**：嵌入相似度匹配历史问答，命中直接返回——RAG 成本工程早期实践。
4. **查询分解 + 答案验证**：复杂问题拆子查询；生成答案后验证环节防幻觉——质量护栏双件套。

## 三、与讲透系列的对位

| localgpt 概念 | 讲透系列对应概念 |
|---|---|
| 混合检索+rerank | 讲透NLP §RAG（检索质量完整链路） |
| 智能路由 | 讲透Agent/00 §成本工程 |
| 语义缓存 | 推理优化（KV cache 的应用层类比） |
| 全本地隐私部署 | ai-deployment §on-prem |

## 四、关键EntryPoint

```
localgpt/           # 核心（Ollama 集成/ingestion/retrieval）
run_localgpt.py     # Web UI 入口
API/                # REST 接口
```

## 五、深读子页地图（31 页精选 5）

Overview（能力全景表）｜Key Features｜System Architecture（多服务编排）｜检索章节（hybrid/late chunking/rerank）｜智能路由章节。

## 六、与"我们"的关系（一句话）

讲透NLP/RAG 教程的"本地隐私版参考实现"——把讲义里的每个 RAG 概念（混合检索/rerank/缓存/路由）落到可跑代码，且示范了 2023→2026 一个爆款项目如何从原型进化为企业清单。

---
生成：2026-08-21 · deepwiki 31 页全归档
