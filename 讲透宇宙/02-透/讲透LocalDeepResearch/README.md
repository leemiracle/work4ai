# 讲透 Local Deep Research · 本地深度研究引擎全量知识库

> **LearningCircuit/local-deep-research** @ commit `2915dc05`（2026-09-03）· 收官补齐 2026-09-21
> 三步流水线：DeepWiki 全量镜像（09-05 已抓）→ understand 中文知识图谱（本轮）→ onboard + explain 精讲（本轮）

Local Deep Research 是 OpenAI Deep Research 的**开源本地替代**：本地/自托管、隐私优先，把"深度研究"做成可迭代的 搜索→阅读→综合 循环。多 LLM（Ollama/llama.cpp 本地 + 云端 API）、30+ 搜索引擎（SearXNG/DuckDuckGo/Tavily/本地库）、RAG 个人文献库、MCP 工具、每用户加密 SQLite。

**版本考古勘误（图谱实证钉版）**：web 入口是 `web/app.py` + `web/fastapi_app.py`（FastAPI 工厂）非老文档的 web/utils/app.py；研究编排在 `api/research_functions.py` + `search_system.py` + `strategies/` 家族非 web_models；RAG 主线在 `embeddings/` + `research_library/services/`。

---

## 📦 资产导航

| 资产 | 内容 | 位置 |
|---|---|---|
| **DeepWiki 镜像** | 52 页（09-05 抓取）：架构/研究管线/LLM 配置/搜索引擎/部署 | [`deepwiki/`](./deepwiki) |
| **知识图谱** | **3879 节点 / 7187 边 / 16 层架构 / 15 步导览**（file 870 + function 2299 + class 556；imports 1465 + contains 2994；0 issues，fingerprints 752 code 基线） | 仓内 `.understand-anything/knowledge-graph.json`（3.4MB） |
| **新人上手指南** | 8 节 5954 字 | [`onboarding/ONBOARDING.md`](./onboarding/ONBOARDING.md) |
| **重要文件精讲** | 6 篇×六节结构 | [`explain/`](./explain) 见下表 |

### explain 六篇（按学习顺序）

| # | 文件 | 主题 |
|---|---|---|
| 1 | [setting-manager.md](./explain/setting-manager.md) | database-first SettingsManager：三层解析链 env>DB>defaults |
| 2 | [web-app.md](./explain/web-app.md) | FastAPI 应用工厂：路由/SSE/Socket.IO 进度/认证 |
| 3 | [research-orchestrator.md](./explain/research-orchestrator.md) | 研究编排心脏：三层接力与 analyze_topic 迭代循环 |
| 4 | [research-strategies.md](./explain/research-strategies.md) | 策略家族：quick/focused/source-based/langgraph 差异与注册 |
| 5 | [llm-providers.md](./explain/llm-providers.md) | LLM 抽象：LLMRegistry + 16 实现 + 八步供应商选择链 |
| 6 | [search-engines.md](./explain/search-engines.md) | 搜索抽象：32 引擎注册表 + 两阶段检索 + egress 治理 |

---

## 🗺️ 十六层架构速览

```
研究主干          web-frontend 182 · web-server 67 · research-engine 92
                 · research-library 74 · news 27
三大抽象          llm-providers 23 · search-engines 54 · rag-retrieval 25
横切              data-persistence 83 · security 37 · config 56 · utility 55
                 · infrastructure 50
工程              benchmarks 41 · ci-quality 142 · documentation 16
```

一句话主线：**FastAPI 收请求 → 研究队列 → 策略家族跑迭代循环（LLM 生成问题 → 搜索引擎取源 → RAG/阅读消化 → 综合）→ SSE/Socket.IO 回传**；配置三层动态生效，数据每用户加密。

## 🚀 推荐路径

1. **30 分钟版**：ONBOARDING §1-3 → explain #3/#4（编排+策略）
2. **半天版**：+ explain #5/#6（LLM/搜索抽象）+ DeepWiki 研究管线章
3. **深度版**：图谱 tour 15 步（概览→配置→Web 入口→队列→编排→策略→LLM→搜索→抓取→RAG→MCP→前端→持久化→安全→容器化）

## 关联

- 上游：https://github.com/LearningCircuit/local-deep-research
- 姊妹单元：[讲透LocalDeepResearch 同类] [讲透DeepResearch](讲透宇宙/01-学/讲透Agent//讲透DeepResearch/README.md)（概念篇）· [讲透Xinference](讲透宇宙/02-透/讲透Xinference//README.md)（推理平台对照）
- 13 仓流水线收官仓之四（2026-09-21）
