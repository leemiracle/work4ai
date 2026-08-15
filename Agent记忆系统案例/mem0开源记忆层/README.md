# Mem0 · 开源 Agent 记忆层 · 源码精读文档导航

> 本目录是基于上游 [`mem0ai/mem0`](https://github.com/mem0ai/mem0) 完整 clone 的**源码精读 + 知识图谱导览**复合文档。
> 目的：① 学懂 Mem0 的工程设计 ② 为基于 Mem0 的二次开发提供内部技术文档 ③ 作为 Agent 记忆系统案例的"开源标准实现"参考。
> 范围：全仓库（Python SDK + TypeScript SDK + 双 CLI + Server + 6 个 Integrations + 6 个 Skills）。
> 文档生成日期：**2026-08-11** · 基线 commit：`4debc58a` · 算法版本：**April 2026 New Memory Algorithm**

---

## 一句话定位

**Mem0 = AI Agent 的「长期记忆层」中间件**——给任何 LLM 应用加上跨会话、个性化、可治理的记忆能力。两种交付：① OSS 自托管 SDK（`Memory` 类，本地跑 LLM+embed+vector_store）② Hosted Platform（`MemoryClient` 类，薄 HTTP 客户端，服务端跑全套 pipeline）。两者 **API 同构**。

---

## 核心数字（April 2026 算法）

| Benchmark | 分数 | Tokens | Latency p50 |
|-----------|------|--------|-------------|
| LoCoMo | **92.5** | 7.0K | 0.88s |
| LongMemEval | **94.4** | 6.8K | 1.09s |
| BEAM 1M | **64.1** | 6.7K | 1.00s |
| BEAM 10M | **48.6** | 6.9K | 1.05s |

**论文**：[arXiv:2504.19413](https://arxiv.org/abs/2504.19413)（Mem0, 2025）

---

## 三个核心创新（April 2026 V3）

1. **Single-pass ADD-only 抽取**——一次 LLM 调用只做 fact 抽取，不再有 UPDATE/DELETE/NOOP 事件。旧记忆的"失效"交给搜索端 score+threshold+rerank
2. **Entity linking**——LLM 抽实体 → batch embed → search-or-insert → `linked_memory_ids` 挂载；`ThreadPoolExecutor(max_workers=4)` 并行
3. **Multi-signal retrieval**——三路并行（semantic over-fetch + BM25 keyword + entity boost）经 `score_and_rank` 融合，可选 reranker

---

## 文档总览（共 44 个文件）

### 📘 入口三件套（先读这个）

| 文件 | 内容 | 行数 |
|------|------|------|
| **[README.md](./README.md)**（本文件） | 目录导航 + 三案例对比定位 + 快速入门 | — |
| [ONBOARDING.md](./ONBOARDING.md) | `/understand-onboard` 生成的 15 层架构全景 + 15 步学习路径 + File Map + 复杂度热点 | 612 |
| [ONBOARDING-EXPLAINED.md](./ONBOARDING-EXPLAINED.md) | 226 个 ONBOARDING 提及文件逐个深度解释（11 个 ⭐🔥 文件源码级 + 187 个分层批解释） | ~700 |

### 📊 知识图谱

| 文件 | 内容 |
|------|------|
| [knowledge-graph-summary.json](./knowledge-graph-summary.json) | 图谱摘要（2071 节点 / 3600 边 / 15 层 / 15 步 tour） |

### 📓 源码精读笔记（`notes/`，41 篇）

> 📁 [`notes/`](./notes/) · 13 子目录 / 15036 行 / 676K · 中文 / 三层讲透宪法（直觉→公式→代码 bash 跑通）

按"从算法核心到外围生态"的顺序组织，与 15 层架构一一对应：

#### 🏛 [00-overview](./notes/00-overview/) — 项目全景（6 篇，必读）

| 文档 | 内容 |
|------|------|
| [01-repo-layout.md](./notes/00-overview/01-repo-layout.md) | Polyglot monorepo 的目录布局与设计动机 |
| [02-architecture.md](./notes/00-overview/02-architecture.md) | 整体架构图、双模式（OSS vs Hosted）、组件分层 |
| [03-build-system.md](./notes/00-overview/03-build-system.md) | Hatch + pnpm + tsup + Docker 构建链 |
| [04-cicd.md](./notes/00-overview/04-cicd.md) | **CI Gate 单入口编排 + Release Router 单入口发布**（11 包治理核心） |
| [05-two-modes.md](./notes/00-overview/05-two-modes.md) | OSS 自托管 vs Platform 托管的 **API 同构哲学** |
| [06-deepwiki-cross-reference.md](./notes/00-overview/06-deepwiki-cross-reference.md) | deepwiki.com 站点交叉引用 |

#### 🧠 [01-py-sdk-core](./notes/01-py-sdk-core/) — Python SDK 核心（8 篇，最重要）

| 文档 | 内容 |
|------|------|
| [01-memory-base.md](./notes/01-py-sdk-core/01-memory-base.md) | `MemoryBase` 抽象基类（63 行但极关键） |
| [02-memory-main.md](./notes/01-py-sdk-core/02-memory-main.md) ⭐🔥 | **`Memory` 类（3851 行核心引擎）** |
| [03-storage.md](./notes/01-py-sdk-core/03-storage.md) | SQLiteManager（变更历史，session 最近 10 条） |
| [04-configs.md](./notes/01-py-sdk-core/04-configs.md) | `MemoryConfig` / `MemoryItem` / `MemoryType` |
| [05-prompts.md](./notes/01-py-sdk-core/05-prompts.md) | Prompt 模板系统（1062 行常量库） |
| [06-add-pipeline.md](./notes/01-py-sdk-core/06-add-pipeline.md) ⭐🔥 | **`add()` 全链路 8 阶段深度剖析（V3 PHASED BATCH PIPELINE）** |
| [07-search-pipeline.md](./notes/01-py-sdk-core/07-search-pipeline.md) ⭐🔥 | **`search()` 多信号融合（semantic + BM25 + entity boost 三路并行）** |
| [08-update-delete.md](./notes/01-py-sdk-core/08-update-delete.md) | update/delete 全链路 + soft-delete 模型 |

#### 🔌 [02-py-sdk-providers](./notes/02-py-sdk-providers/) — Provider 插件模式（8 篇）

| 文档 | 内容 |
|------|------|
| [01-base-pattern.md](./notes/02-py-sdk-providers/01-base-pattern.md) | **5 类抽象基类的设计模式**（LLM/Embedder/VectorStore/Graph/Reranker） |
| [02-llms.md](./notes/02-py-sdk-providers/02-llms.md) | 21 个 LLM provider（OpenAI/Anthropic/Gemini/Bedrock/Ollama/vLLM/...） |
| [03-embeddings.md](./notes/02-py-sdk-providers/03-embeddings.md) | 15 个 embedding provider |
| [04-vector-stores.md](./notes/02-py-sdk-providers/04-vector-stores.md) | 28 个 vector store（Qdrant/Pinecone/Chroma/pgvector/Databricks/...） |
| [05-graphs.md](./notes/02-py-sdk-providers/05-graphs.md) | Graph store（Neo4j/Memgraph/Kuzu/Apache AGE） |
| [06-rerankers.md](./notes/02-py-sdk-providers/06-rerankers.md) | 5 个 reranker（Cohere/HuggingFace/LLM-based/SentenceTransformer/Zero Entropy） |
| [07-factory.md](./notes/02-py-sdk-providers/07-factory.md) | `Factory` 工厂模式——按 config 字符串实例化 |
| [08-utils.md](./notes/02-py-sdk-providers/08-utils.md) | 工具函数（entity_extraction/scoring/lemmatization/http/gcp_auth/spacy_models） |

#### ☁️ [03-py-sdk-client](./notes/03-py-sdk-client/) — Hosted Platform Client（3 篇）

| 文档 | 内容 |
|------|------|
| [01-client.md](./notes/03-py-sdk-client/01-client.md) ⭐🔥 | **`MemoryClient`（1838 行 HTTP 薄客户端）** |
| [02-proxy.md](./notes/03-py-sdk-client/02-proxy.md) | OpenAI 兼容 proxy（`mem0.proxy.main`） |
| [03-telemetry.md](./notes/03-py-sdk-client/03-telemetry.md) | PostHog 匿名遥测 + aliasing |

#### 🌀 [04-ts-sdk](./notes/04-ts-sdk/) — TypeScript SDK 平行实现（2 篇）

| 文档 | 内容 |
|------|------|
| [01-structure.md](./notes/04-ts-sdk/01-structure.md) | TS SDK 目录结构 + Zod schema 替代 Pydantic + deferred init |
| [02-providers-and-types.md](./notes/04-ts-sdk/02-providers-and-types.md) | TS Provider 工厂 + 类型系统 |

#### 🖥 [05-server](./notes/05-server/) — FastAPI 自托管 Server（2 篇）

| 文档 | 内容 |
|------|------|
| [01-architecture.md](./notes/05-server/01-architecture.md) ⭐🔥 | **FastAPI + JWT + API key 双轨认证 + PostgreSQL/pgvector** |
| [02-vs-hosted.md](./notes/05-server/02-vs-hosted.md) | 自托管 Server vs Hosted Platform 决策矩阵 |

#### ⌨️ [06-cli-python](./notes/06-cli-python/) — Python Typer CLI（1 篇）

| 文档 | 内容 |
|------|------|
| [01-entry-and-commands.md](./notes/06-cli-python/01-entry-and-commands.md) | Typer app 主入口 + 命令实现 + Rich 渲染 |

#### ⌨️ [07-cli-node](./notes/07-cli-node/) — Node Commander CLI（1 篇）

| 文档 | 内容 |
|------|------|
| [01-entry-and-commands.md](./notes/07-cli-node/01-entry-and-commands.md) | Commander program + Biome lint + vitest |

#### 🔗 [08-integrations](./notes/08-integrations/) — Agent & Editor 集成（2 篇）

| 文档 | 内容 |
|------|------|
| [01-mem0-plugin.md](./notes/08-integrations/01-mem0-plugin.md) ⭐🔥 | **mem0-plugin（MCP server + lifecycle hooks + OpenCode 插件）** |
| [02-other-integrations.md](./notes/08-integrations/02-other-integrations.md) | OpenClaw / Pi Agent / Vercel AI SDK / n8n / Zapier |

#### 🎓 [09-skills](./notes/09-skills/) — AI Agent Skill 体系（1 篇）

| 文档 | 内容 |
|------|------|
| [01-skills-overview.md](./notes/09-skills/01-skills-overview.md) | 6 个 skill（3 reference always-on + 3 pipeline on-demand） |

#### 🧪 [10-examples-eval](./notes/10-examples-eval/) — 示例与评测（1 篇）

| 文档 | 内容 |
|------|------|
| [01-examples-and-eval.md](./notes/10-examples-eval/01-examples-and-eval.md) | 10 个 demo + 外部 benchmark（LOCOMO/LongMemEval/BEAM） |

#### 🔍 [11-layer-surveys](./notes/11-layer-surveys/) — 层级综述（4 篇，深度专题）

| 文档 | 内容 |
|------|------|
| [01-L10-integrations.md](./notes/11-layer-surveys/01-L10-integrations.md) | L10 集成层综述 |
| [02-L2-providers-patch.md](./notes/11-layer-surveys/02-L2-providers-patch.md) | L2 Provider 抽象层补丁 |
| [03-L11-skills.md](./notes/11-layer-surveys/03-L11-skills.md) | L11 Skills 层综述 |
| [04-L7-dashboard.md](./notes/11-layer-surveys/04-L7-dashboard.md) | L7 Dashboard 层（Next.js 前端） |

#### 📚 [99-appendix](./notes/99-appendix/) — 附录（1 篇）

| 文档 | 内容 |
|------|------|
| [index.md](./notes/99-appendix/index.md) | 数据流图汇总、关键常量速查 |

---

## 快速入门路径

### 路径 A：先建立全景（3–4 小时速通）
```
README.md（本文件）→ ONBOARDING.md → notes/00-overview/ → notes/01-py-sdk-core/02-memory-main.md
```

### 路径 B：完整精读（建议 1–2 周）
```
按 notes/ 子目录自上而下（00 → 01 → 02 → ... → 11 → 99）
每个章节配合 ONBOARDING-EXPLAINED.md 查对应层的关键文件
```

### 路径 C：直接看核心算法（最短路径）
```
notes/01-py-sdk-core/06-add-pipeline.md（add() 8 phase）
↓
notes/01-py-sdk-core/07-search-pipeline.md（search() 9 step）
↓
notes/02-py-sdk-providers/07-factory.md（Provider 工厂）
```

### 路径 D：接业务侧 SDK
```
ONBOARDING.md §3.1（OSS vs Platform 同构哲学）
↓
notes/03-py-sdk-client/01-client.md（MemoryClient HTTP 调用）
↓
notes/04-ts-sdk/01-structure.md（TS SDK）
```

### 路径 E：自托管运维
```
notes/05-server/01-architecture.md（FastAPI + JWT）
↓
notes/05-server/02-vs-hosted.md（决策矩阵）
↓
notes/00-overview/04-cicd.md（CI/CD）
```

### 路径 F：AI 编辑器集成
```
notes/08-integrations/01-mem0-plugin.md（MCP server）
↓
notes/08-integrations/02-other-integrations.md（5 个集成）
↓
notes/09-skills/01-skills-overview.md（6 个 skill）
```

---

## Mem0 在 Agent 记忆系统谱系中的定位

**Mem0 = 最简洁的"扁平记忆"开源标准实现**——单层 memory、API 同构双 SDK（Python + TypeScript）、生态最广（11 个独立发布的包）。

**核心设计选择**：
- **单层扁平记忆**（vs 企业级的 L0→L3 分层提炼）：简洁，但缺少跨会话的语义抽象
- **Single-pass ADD-only 算法**（April 2026）：一次 LLM 调用完成抽取 + 实体链接 + 去重
- **28 种 vector store 后端**：从 Qdrant/Pinecone 到 pgvector，可插拔
- **完全开源（Apache-2.0）**：可自托管，也有 Hosted Platform

> 📌 想对比其它形态的 Agent 记忆系统（如企业级分层提炼、端侧多模态），可参考业界公开的学术资料和开源项目。

---

## 与 work4ai 其他系列的关系

| work4ai 系列 | 关系 |
|-------------|------|
| [讲透Agent](../../讲透Agent/) | 本案例是 Agent 记忆子系统的真实开源标准实现 |
| [讲透RAG](../../讲透RAG/) | Mem0 本质是 **"记忆即 RAG"** 的特殊形态——自身文档作为持久化语料库 |
| [讲透Prompt](../../讲透Prompt/) | Mem0 的 V3 single-pass 抽取 prompt 是工业级 prompt 工程样本（`ADDITIVE_EXTRACTION_PROMPT`） |
| [讲透基础模型](../../讲透基础模型/) | Mem0 的 21 个 LLM provider 适配器是 LLM 抽象层的实战参考 |
| [讲透PyTorch](../../讲透PyTorch/) | （间接）Mem0 的 embedding provider 中 HuggingFace 等用 PyTorch |
| [讲透微调](../../讲透微调/) | （间接）Mem0 支持 LangChain ChatModel 接入微调后的模型 |
| [讲透AI应用全景](../../讲透AI应用全景/) | 本案例是 AI 应用中「记忆」维度的深度展开 |
| [Agent架构模式参考](../../Agent架构模式参考/) | 本案例是 Provider 插件模式 + 双 SDK 同构的具体系统深度分析 |
| 项目案例-OpenPhone（待写/未落盘） | 互补——OpenPhone 是"产品级"项目案例，本案例是"基础设施级" |

---

## 元数据

| 项 | 值 |
|---|---|
| 上游 HEAD（笔记起点） | `4debc58a` — `fix(security): patch 8 HIGH + 18 MEDIUM Vanta vulnerabilities...` |
| 算法版本 | **April 2026 New Memory Algorithm**（single-pass ADD-only、entity linking、multi-signal retrieval、temporal reasoning） |
| 论文 | [arXiv:2504.19413](https://arxiv.org/abs/2504.19413) (Mem0, 2025) |
| Benchmark | LoCoMo 92.5 / LongMemEval 94.4 / BEAM 1M 64.1 / BEAM 10M 48.6 |
| 行数（约） | Python SDK 31.7K + TS SDK 59.7K + CLI/Server/Integrations ≈ **10 万行** |
| 知识图谱 | 1491 文件 / 2071 节点 / 3600 边 / 15 层 / 15 步 tour |

> ⚠️ 上游每天变动。阅读时如发现 `main.py` 行号对不上，先 `git log --oneline mem0/memory/main.py` 看是否有更新。
> 所有引用行号基于上述 HEAD；函数名/类名比行号稳定，优先按名字定位。

---

*文档生成方法：源码精读（41 篇手写讲透笔记）+ `/understand` 知识图谱（2071 节点 / 15 层）+ `/understand-onboard`（15 步导览）+ `/understand-explain`（226 文件深度解释）。*
