# Mem0 上手指南（Onboarding Guide）

> 本指南由 `/understand-onboard` 基于 `.understand-anything/knowledge-graph.json` 自动生成。
> 生成时间：2026-08-11 · 基线 commit：`4debc58a` · 复杂度：very-large（1491 文件）
> 阅读对象：新加入团队、二次开发者、AI agent 接入方。

---

## 1. Project Overview（项目概览）

**Mem0**（"mem-zero"）是面向 AI agents 和 assistants 的智能记忆层，提供持久化、个性化的长期记忆。两种交付方式：

| 模式 | 入口 | 适用场景 |
|------|------|---------|
| **OSS 自托管 SDK** | `mem0.Memory`（Python）/ `mem0ai/oss` 的 `Memory`（TS） | 数据自主、私有部署、本地实验 |
| **Hosted Platform** | `mem0.MemoryClient`（Python + TS） | 免运维、graph memory、SLA 保障 |

**核心算法**（April 2026 New Memory Algorithm）：
- **Single-pass ADD-only 抽取**——一次 LLM 调用，只 ADD 不 UPDATE/DELETE
- **Entity linking**——实体抽取、嵌入、跨记忆链接
- **Multi-signal retrieval**——semantic + BM25 + entity boost 三路并行融合
- **Temporal reasoning**——Platform 独占，时间感知检索

**Benchmark**（同模型栈，single-pass retrieval，top_200 budget）：

| Benchmark | Old | New | Tokens | Latency p50 |
|-----------|-----|-----|--------|-------------|
| LoCoMo | 71.4 | **92.5** | 7.0K | 0.88s |
| LongMemEval | 67.8 | **94.4** | 6.8K | 1.09s |
| BEAM 1M | — | **64.1** | 6.7K | 1.00s |
| BEAM 10M | — | **48.6** | 6.9K | 1.05s |

**技术栈**：

| 维度 | 选择 |
|------|------|
| 主语言 | TypeScript（566 files）+ Python（366 files）+ Markdown（353 files） |
| Python 框架 | Pydantic v2、FastAPI、Typer、Hatch、pytest、Ruff、Alembic、Docker Compose |
| TypeScript 框架 | tsup、pnpm、Jest、Vitest、Biome、Next.js、React、Tailwind CSS |
| 文档 | Mintlify（247 mdx） |
| 集成协议 | MCP（Model Context Protocol）、LangChain |
| 部署 | Docker（FastAPI + PostgreSQL/pgvector + 可选 Neo4j） |
| CI/CD | GitHub Actions（OIDC trusted publishing，无 token） |

**仓库形态**：polyglot monorepo，11 个可独立发布的包（Python SDK `mem0ai`、TS SDK `mem0ai`、双 CLI、6 个集成）。约 10 万行代码。

---

## 2. Architecture Layers（15 个架构层）

知识图谱把 2071 个节点分成 15 层，按"从算法核心到外围生态"的顺序：

| # | 层 | 节点数 | 关键作用 |
|---|----|--------|---------|
| 1 | **Python SDK 核心引擎** | 33 | Memory 类、add/search pipeline、SQLite 存储、telemetry、notice 系统 |
| 2 | **Python SDK Provider 抽象** | 116 | 5 类 base + 78 个具体 provider（21 LLM × 15 embedding × 28 vector store × 5 reranker） |
| 3 | **Python SDK 配置系统** | 76 | MemoryConfig Pydantic 主模型 + provider 子配置 |
| 4 | **Python SDK 工具模块** | 19 | Factory 工厂、entity_extraction、scoring、lemmatization |
| 5 | **Python Hosted Platform Client** | 12 | MemoryClient + HTTP proxy + 匿名遥测 |
| 6 | **TypeScript SDK（平行实现）** | 346 | 与 Python 1:1 平行的完整 TS 实现 |
| 7 | **Server Dashboard（Next.js 前端）** | 149 | 独立子项目，可视化管理面板（:3000） |
| 8 | **FastAPI 自托管 Server** | 84 | REST API 包装 + JWT 认证 + PostgreSQL |
| 9 | **双 CLI** | 109 | Python Typer + Node Commander，同一 spec 规范 |
| 10 | **Agent & Editor 集成** | 332 | 6 个集成包（MCP server / OpenClaw / Pi / Vercel AI / n8n / Zapier） |
| 11 | **AI Agent Skill 体系** | 35 | 6 个 skill（3 reference always-on + 3 pipeline on-demand） |
| 12 | **Mintlify 文档站** | 251 | 247 mdx 静态站点 |
| 13 | **示例项目** | 169 | 10 个可运行 demo |
| 14 | **Python SDK 测试套件** | 285 | pytest，tested_by 网络连接生产代码 |
| 15 | **CI/CD + 顶层配置** | 55 | CI Gate + Release Router 双单入口编排 |

**架构精髓**：双 SDK 同构（Python `Memory` ↔ TS `Memory` 同 API），上层（CLI / Server / Integrations / Skills）共用相同契约。

---

## 3. Key Concepts（必须理解的设计概念）

### 3.1 OSS vs Platform 同构哲学

`mem0.Memory` 和 `mem0.MemoryClient` 暴露相同 API（`add` / `search` / `get` / `update` / `delete` / `get_all` / `history`）。用户代码只需换 import：

```python
# OSS
from mem0 import Memory
m = Memory.from_config(config)

# Platform
from mem0 import MemoryClient
m = MemoryClient(api_key="...")
```

### 3.2 Provider 插件模式

5 类抽象基类定义统一契约，78 个具体 provider 各自继承：

| 类 | base | 数量 | 实例化入口 |
|---|------|------|----------|
| LLM | `mem0/llms/base.py:LLMBase` | 21 | `Factory` |
| Embedder | `mem0/embeddings/base.py:EmbeddingBase` | 15 | `Factory` |
| VectorStore | `mem0/vector_stores/base.py:VectorStoreBase` | 28 | `Factory` |
| Reranker | `mem0/reranker/base.py:BaseReranker` | 5 | `Factory` |

`mem0/utils/factory.py:Factory` 按 `MemoryConfig` 实例化——支持任意组合。

### 3.3 add() pipeline（April 2026 核心创新）

`mem0/memory/main.py:Memory.add()` → `_add_to_vector_store` → `_create_memory` / `_link_entities_for_memory`：

1. **Fact extraction**（single-pass ADD-only）：一次 LLM 调用抽取 facts，只 ADD 不 UPDATE/DELETE
2. **UUID→整数防幻觉**：LLM 输出的 ID 视为不可信
3. **md5 hash 去重**：text hash 已存在则跳过
4. **Entity extraction + linking**：LLM 抽实体 → embed → search-or-insert → `linked_memory_ids` 挂载
5. **批量 embed + upsert**：向量化 + 入 vector store

### 3.4 search() 多信号融合

`Memory.search()` → `_search_vector_store` → `_compute_entity_boosts`：

- 三路并行（`ThreadPoolExecutor`）：semantic over-fetch + BM25 keyword + entity boost
- `mem0/utils/scoring.py:score_and_rank` 融合
- 可选 rerank（reranker provider）

### 3.5 CI Gate + Release Router 双单入口

- **CI Gate**（`.github/workflows/ci-gate.yml`）：所有 PR 触发，路径检测 + 路由到各包 CI workflow
- **Release Router**（`.github/workflows/release.yml`）：所有 release 事件触发，按 tag 前缀（`v*` / `ts-v*` / `cli-v*` / ...）路由到对应 CD workflow
- 11 个 polyglot 包的发布治理核心

### 3.6 Skill 体系（AI agent 知识）

- **Reference skill**（always-on）：`skills/mem0/`、`skills/mem0-cli/`、`skills/mem0-vercel-ai-sdk/` —— 装上后 `SKILL.md` 永远在 LLM context
- **Pipeline skill**（on-demand）：`skills/mem0-integrate/`、`skills/mem0-test-integration/`、`skills/mem0-oss-to-platform/` —— 用户主动调用

---

## 4. Guided Tour（15 步学习路径）

按以下顺序阅读，每一步对应知识图谱中的关键节点：

### Step 1 — 项目入口与定位
读 `README.md`、`AGENTS.md`、`LLM.md`（三份 AI 助手上下文文档高度同步），看 `pyproject.toml` 了解包定义。理解 Mem0 是什么、benchmark 数字、两种交付模式。

### Step 2 — Python SDK 的"门面"
看 `mem0/__init__.py` 暴露的 public API：`Memory`、`AsyncMemory`、`MemoryClient`、`AsyncMemoryClient`。这是用户接触 SDK 的第一行代码。

### Step 3 — ⭐ Memory 类（项目心脏）
`mem0/memory/main.py`（3851 行）定义 `Memory`（同步）与 `AsyncMemory`（异步）两个核心引擎类。配套读抽象基类 `mem0/memory/base.py`。所有 add/search/update/delete pipeline 的入口。

### Step 4 — add() 全链路
跟踪 `Memory.add()` → `_add_to_vector_store()` → `_create_memory()` / `_link_entities_for_memory()`。理解 single-pass ADD-only 抽取、entity linking、批量 upsert。

### Step 5 — search() 多信号融合
跟踪 `Memory.search()` → `_search_vector_store()` → `_compute_entity_boosts()`，配合 `mem0/utils/scoring.py` 理解 score_and_rank。

### Step 6 — Provider 插件体系
读 5 个 base：`mem0/llms/base.py`、`mem0/embeddings/base.py`、`mem0/vector_stores/base.py`、`mem0/reranker/base.py`。然后看 `mem0/utils/factory.py:Factory` 实例化逻辑。

### Step 7 — 配置系统
`mem0/configs/base.py:MemoryConfig`（Pydantic 主模型）+ 默认 prompt 模板 `mem0/configs/prompts.py`。April 2026 重构后 graph 字段已移除。

### Step 8 — Hosted Platform Client
`mem0/client/main.py:MemoryClient`（1838 行）+ `mem0/proxy/main.py`（HTTP proxy）+ `mem0/memory/telemetry.py`（PostHog 匿名遥测）。

### Step 9 — TypeScript SDK 平行实现
`mem0-ts/src/oss/src/memory/index.ts`（2207 行，最核心）+ `mem0-ts/src/oss/src/utils/factory.ts` + `mem0-ts/src/client/mem0.ts` + `mem0-ts/src/oss/src/types/index.ts`（Zod schema 替代 Pydantic）。

### Step 10 — 自托管 Server
`server/main.py`（FastAPI app）+ `server/auth.py`（JWT）+ `server/db.py`（PostgreSQL）+ `server/routers/requests.py`（路由示例）+ `server/Dockerfile` + `server/docker-compose.yaml`。

### Step 11 — 双 CLI（同一规范的两种实现）
`cli/python/src/mem0_cli/app.py`（Typer）+ `cli/node/src/index.ts`（Commander）+ 上游规范 `cli/CLI_SPECIFICATION.md` + `cli/cli-spec.json`。

### Step 12 — Agent & Editor 集成（MCP server）
`integrations/mem0-plugin/` 是最大的集成。看 `integrations/mem0-plugin/scripts/auto_capture.py`（lifecycle hook）+ `integrations/mem0-plugin/plugin.json`（manifest）+ `integrations/mem0-plugin/mcp_config.json`（MCP 配置）+ `integrations/vercel-ai-sdk/src/index.ts`（Vercel AI provider 入口）。

### Step 13 — AI Agent Skill 体系
`skills/mem0/SKILL.md`、`skills/mem0-integrate/SKILL.md`、`skills/mem0-oss-to-platform/SKILL.md`。每个 SKILL.md 是 AI assistant 装上后永远在 context 里的主入口。

### Step 14 — 测试与验证
`tests/test_memory.py`（Memory 类全链路）+ `tests/test_main.py`（server main）+ `tests/test_client.py`（MemoryClient）+ `tests/test_server_auth.py`（JWT 流程）。外部 benchmark 在 `evaluation/` submodule（LOCOMO/LongMemEval/BEAM）。

### Step 15 — CI/CD 双单入口编排
`.github/workflows/ci-gate.yml`（CI 单入口）+ `.github/workflows/release.yml`（Release Router）+ `.github/workflows/ci.yml`（Python SDK CI）+ `.github/workflows/cd.yml`（Python SDK CD）+ `.github/workflows/ts-sdk-ci.yml`（TS SDK CI）。

---

## 5. File Map（按层组织的文件清单）

> 标 ⭐ 的是该层最重要的文件；标 🔥 的是 complexity=complex 的热点文件。

### Layer 1 — Python SDK 核心引擎（`mem0/memory/`）

| 文件 | 行数 | 说明 |
|------|------|------|
| ⭐🔥 `mem0/memory/main.py` | 3851 | Memory + AsyncMemory 双引擎类，所有 pipeline 入口 |
| ⭐ `mem0/memory/base.py` | — | `MemoryBase` 抽象基类 |
| `mem0/memory/storage.py` | — | `SQLiteManager`（变更历史，session 最近 10 条） |
| 🔥 `mem0/memory/notices.py` | 1582 | OSS 运行时 notice 系统（first-run/temporal/decay/scale/slow-query） |
| `mem0/memory/telemetry.py` | 241 | PostHog 匿名遥测 |
| `mem0/memory/setup.py` | 166 | 启动配置（创建 `~/.mem0` 目录、加载 config） |
| 🔥 `mem0/memory/utils.py` | — | legacy graph helper + 安全深拷贝 + JSON 抽取/修复 |

### Layer 2 — Python SDK Provider 抽象（`mem0/{llms,embeddings,vector_stores,reranker}/`）

**5 个抽象基类**（必读）：

| 文件 | 类 | 抽象方法 |
|------|----|---------|
| ⭐ `mem0/llms/base.py` | `LLMBase` | `generate_response()` |
| ⭐ `mem0/embeddings/base.py` | `EmbeddingBase` | `embed()` / `embed_batch()` |
| ⭐ `mem0/vector_stores/base.py` | `VectorStoreBase` | `insert` / `search` / `update` / `delete` / `create_col` / `list_cols` / `get_col` / `delete_col` / `reset` |
| ⭐ `mem0/reranker/base.py` | `BaseReranker` | `rerank()` |

**Provider 数量分布**（具体实现只列代表，全部 78 个见源目录）：

| 类 | 总数 | 代表性 provider |
|----|------|----------------|
| LLM | 21 | `mem0/llms/openai.py`、`mem0/llms/anthropic.py`、`mem0/llms/gemini.py`、🔥 `mem0/llms/aws_bedrock.py`（713 行，最大）、`mem0/llms/ollama.py`、`mem0/llms/vllm.py`、`mem0/llms/litellm.py`、`mem0/llms/xai.py`、`mem0/llms/langchain.py` |
| Embedder | 15 | `mem0/embeddings/openai.py`、`mem0/embeddings/huggingface.py`、`mem0/embeddings/gemini.py`、`mem0/embeddings/aws_bedrock.py`、`mem0/embeddings/vertexai.py`、`mem0/embeddings/ollama.py` |
| VectorStore | 28 | `mem0/vector_stores/qdrant.py`、`mem0/vector_stores/pinecone.py`、`mem0/vector_stores/chroma.py`、🔥 `mem0/vector_stores/databricks.py`（881 行）、🔥 `mem0/vector_stores/oracledb.py`（602 行）、🔥 `mem0/vector_stores/neptune_analytics.py`（535 行）、`mem0/vector_stores/pgvector.py`、🔥 `mem0/vector_stores/cassandra.py`（503 行）、`mem0/vector_stores/faiss.py`、`mem0/vector_stores/redis.py`、`mem0/vector_stores/elasticsearch.py`、`mem0/vector_stores/milvus.py`、`mem0/vector_stores/weaviate.py`、`mem0/vector_stores/mongodb.py`、`mem0/vector_stores/supabase.py` |
| Reranker | 5 | `mem0/reranker/cohere_reranker.py`、`mem0/reranker/huggingface_reranker.py`、`mem0/reranker/llm_reranker.py`、`mem0/reranker/sentence_transformer_reranker.py`、`mem0/reranker/zero_entropy_reranker.py` |

### Layer 3 — Python SDK 配置系统（`mem0/configs/`）

| 文件 | 说明 |
|------|------|
| ⭐ `mem0/configs/base.py` | `MemoryConfig` Pydantic 主模型（all config entry） |
| `mem0/configs/enums.py` | `MemoryType` 枚举 |
| ⭐ `mem0/configs/prompts.py` | prompt 模板常量 |
| `mem0/configs/llms/<provider>.py` × 13 | 各 LLM 的 Config 子类（如 `mem0/configs/llms/azure.py`） |
| `mem0/configs/vector_stores/<provider>.py` × 26 | 各 vector store 的 Config 子类 |
| `mem0/configs/rerankers/<provider>.py` × 5 | 各 reranker 的 Config 子类 |
| `mem0/exceptions.py` | Mem0 异常体系（484 行，含 graph 移除遗留的 kuzu 错误提示） |

### Layer 4 — Python SDK 工具模块（`mem0/utils/`）

| 文件 | 说明 |
|------|------|
| ⭐ `mem0/utils/factory.py` | `Factory` 工厂——按 config 实例化 5 类 provider |
| 🔥 `mem0/utils/entity_extraction.py` | LLM 实体抽取 + `_EntityCandidate` |
| `mem0/utils/scoring.py` | 多信号融合 `score_and_rank` |
| ⭐ `mem0/configs/prompts.py` | prompt 模板系统（`ADDITIVE_EXTRACTION_PROMPT` 等，与 utils/factory.py 配合） |
| `mem0/utils/lemmatization.py` | spaCy lemmatization |
| `mem0/utils/http.py` | HTTP client 工具 |
| `mem0/utils/gcp_auth.py` | GCP 认证 helper |
| `mem0/utils/spacy_models.py` | spaCy model 单例缓存 |

### Layer 5 — Python Hosted Platform Client（`mem0/client/` + `mem0/proxy/`）

| 文件 | 说明 |
|------|------|
| ⭐🔥 `mem0/client/main.py` | `MemoryClient` / `AsyncMemoryClient`（1838 行，httpx REST） |
| 🔥 `mem0/client/project.py` | `Project` / `AsyncProject`（944 行，项目管理） |
| `mem0/client/types.py` | 类型定义 |
| `mem0/client/utils.py` | 客户端工具 |
| `mem0/proxy/main.py` | HTTP proxy 机制 |

### Layer 6 — TypeScript SDK（`mem0-ts/src/`）

| 文件 | 说明 |
|------|------|
| ⭐🔥 `mem0-ts/src/oss/src/memory/index.ts` | OSS Memory 核心类（2207 行，最核心） |
| ⭐ `mem0-ts/src/oss/src/utils/factory.ts` | Provider 工厂（297 行，4 个工厂类） |
| 🔥 `mem0-ts/src/oss/src/utils/entity_extraction.ts` | Entity 抽取（828 行，最大 utils） |
| 🔥 `mem0-ts/src/oss/src/utils/notices.ts` | OSS notice 系统（1434 行） |
| ⭐ `mem0-ts/src/oss/src/types/index.ts` | Zod schema 类型系统（替代 Pydantic） |
| 🔥 `mem0-ts/src/oss/src/prompts/index.ts` | Prompt 模板中心（1042 行） |
| `mem0-ts/src/oss/src/llms/aws_bedrock.ts` | Bedrock LLM（294 行，Converse API） |
| `mem0-ts/src/oss/src/embeddings/vertexai.ts` | Vertex AI embedder（251 行） |
| 🔥 `mem0-ts/src/oss/src/vector_stores/databricks.ts` | Databricks vector store（**1627 行，最大文件**） |
| 🔥 `mem0-ts/src/oss/src/vector_stores/neptune_analytics.ts` | Neptune（1120 行，Gremlin） |
| `mem0-ts/src/oss/src/vector_stores/memory.ts` | 内存+SQLite 默认 store（491 行） |
| ⭐ `mem0-ts/src/client/mem0.ts` | Hosted `MemoryClient`（client/ 主入口） |
| `mem0-ts/src/client/config.ts` / `mem0.ts.types.ts` / `telemetry.ts` / `utils.ts` | Client 支撑文件 |
| `mem0-ts/src/common/exceptions.ts` | 异常类（镜像 Python exceptions） |
| `mem0-ts/src/community/src/integrations/` | 第三方集成包（@mem0/community） |

### Layer 7 — Server Dashboard（`server/dashboard/`，Next.js 独立子项目）

| 文件 | 说明 |
|------|------|
| 🔥 `server/dashboard/src/app/setup/page.tsx` | /setup 引导页（763 行，多步配置向导） |
| 🔥 `server/dashboard/src/lib/auth.tsx` | `AuthProvider` 认证上下文 |
| 🔥 `server/dashboard/src/utils/api.ts` | axios 客户端（401 自动 refresh） |
| 🔥 `server/dashboard/src/middleware.ts` | Next.js 路由守卫 |
| `server/dashboard/src/hooks/use-api-query.ts` | 通用数据拉取 hook（并发去重） |
| `server/dashboard/src/app/api/auth/refresh/route.ts` | Next.js Route Handler（refresh 代理） |
| `server/dashboard/src/app/(root)/dashboard/{api-keys,memories,requests,configuration,settings}/page.tsx` | 各功能页 |
| `server/dashboard/src/app/(auth)/login/login-form.tsx` | 登录表单 |
| `server/dashboard/src/components/ui/sidebar.tsx` | shadcn/ui 侧边栏（274 行） |
| `server/dashboard/src/components/shared/data-table.tsx` | 通用数据表格 |

### Layer 8 — FastAPI 自托管 Server（`server/`，排除 dashboard）

| 文件 | 说明 |
|------|------|
| ⭐🔥 `server/main.py` | FastAPI app 入口（/memories、/search、/configure、/reset、/generate-instructions） |
| ⭐🔥 `server/auth.py` | JWT + API key 双轨认证 |
| `server/db.py` | PostgreSQL 连接 |
| `server/models.py` | SQLAlchemy ORM models |
| `server/schemas.py` | Pydantic schemas |
| `server/rate_limit.py` | 速率限制 |
| 🔥 `server/server_state.py` | 进程内全局状态（线程安全 MemoryConfig + Memory 单例） |
| `server/routers/api_keys.py` | API key 路由 |
| `server/routers/auth.py` | /auth 路由（register/login/refresh/me/change-password） |
| `server/routers/entities.py` | 实体路由 |
| `server/routers/requests.py` | 请求日志路由 |
| `server/alembic/` | DB 迁移（6 个 versions） |
| ⭐ `server/Dockerfile` + `server/docker-compose.yaml` + `server/dev.Dockerfile` | 容器化部署 |
| `server/dashboard/Dockerfile` | dashboard 独立镜像 |
| `server/requirements.txt` / `server/init-db.sh` / `server/Makefile` | 部署脚本 |

### Layer 9 — 双 CLI

**Python CLI（`cli/python/`）**：

| 文件 | 说明 |
|------|------|
| ⭐ `cli/python/src/mem0_cli/app.py` | Typer CLI 主入口 |
| 🔥 `cli/python/src/mem0_cli/commands/memory.py` | 记忆命令（718 行，cmd_add/cmd_search/cmd_get/cmd_list/cmd_update/cmd_delete/cmd_forget） |
| 🔥 `cli/python/src/mem0_cli/commands/init_cmd.py` | init 配置向导（566 行，最长） |
| `cli/python/src/mem0_cli/backend/platform.py` | PlatformBackend（420 行，httpx） |
| `cli/python/src/mem0_cli/output.py` | Rich 输出渲染（394 行） |
| `cli/python/src/mem0_cli/backend/base.py` | `Backend` 抽象基类 |
| `cli/python/src/mem0_cli/state.py` / `plugin_sync.py` / `telemetry_sender.py` | 状态/插件同步/遥测 |
| `cli/python/tests/test_commands.py` | 命令测试（1556 行，最大） |

**Node CLI（`cli/node/`）**：

| 文件 | 说明 |
|------|------|
| ⭐ `cli/node/src/index.ts` | Commander CLI 主入口 |
| `cli/node/src/commands/` | 命令实现（cmdAdd/cmdSearch/cmdInit 等） |
| `cli/node/src/utils/` | 工具（HTTP/output/state） |

**统一规范源**（必读）：

| 文件 | 说明 |
|------|------|
| ⭐ `cli/CLI_SPECIFICATION.md` | 双 CLI 共用规范 |
| ⭐ `cli/cli-spec.json` | 机器可读规范（命令对齐的权威源） |

### Layer 10 — Agent & Editor 集成（`integrations/`）

**mem0-plugin**（最大集成，MCP server）：

| 文件 | 说明 |
|------|------|
| ⭐ `integrations/mem0-plugin/plugin.json` | plugin manifest |
| ⭐ `integrations/mem0-plugin/mcp_config.json` | MCP server 配置 |
| 🔥 `integrations/mem0-plugin/scripts/on_session_start.sh` | SessionStart hook（199 行） |
| 🔥 `integrations/mem0-plugin/scripts/on_user_prompt.sh` | UserPromptSubmit hook（228 行） |
| 🔥 `integrations/mem0-plugin/scripts/enforce_metadata_defaults.sh` | PreToolUse hook（218 行） |
| 🔥 `integrations/mem0-plugin/scripts/capture_session_summary.py` | Stop hook |
| 🔥 `integrations/mem0-plugin/scripts/auto_import.py` | 启动时导入 CLAUDE.md/AGENTS.md/.cursorrules |
| 🔥 `integrations/mem0-plugin/scripts/import_competing_tools.py` | 从 cursorrules/copilot/cline 导入 |
| 🔥 `integrations/mem0-plugin/scripts/on_pre_compact.py` | PreCompact/Stop hook |
| `integrations/mem0-plugin/hooks/hooks.json` | Claude Code hooks manifest（126 行） |
| `integrations/mem0-plugin/hooks/codex-hooks.json` | Codex hooks manifest |
| 🔥 `integrations/mem0-plugin/.opencode-plugin/opencode-mem0.ts` | OpenCode 插件主入口（1000 行，9 个 MCP 工具） |
| `integrations/mem0-plugin/.opencode-plugin/dream.ts` | Dream 记忆巩固模块（225 行） |
| `integrations/mem0-plugin/skills/mem0/SKILL.md` + `references/*.md` + `client/*.md` | 嵌套 mem0 skill |

**其他 5 个集成**：

| 集成 | 主入口 | 说明 |
|------|--------|------|
| OpenClaw | ⭐🔥 `integrations/openclaw/index.ts`（1059 行） | Claude Code/OpenClaw memory plugin（kind=memory，8 个 tools） |
| | 🔥 `integrations/openclaw/cli/commands.ts`（1872 行） | CLI 子命令注册 |
| | 🔥 `integrations/openclaw/providers.ts`（641 行） | Platform/OSS 双模式 |
| | 🔥 `integrations/openclaw/recall.ts` | token 预算化召回引擎 |
| | 🔥 `integrations/openclaw/skill-loader.ts`（693 行） | Skill 加载器 |
| | 🔥 `integrations/openclaw/backend/platform.ts` | PlatformBackend HTTP 客户端 |
| | `integrations/openclaw/openclaw.plugin.json` | manifest（319 行） |
| Pi Agent | ⭐ `integrations/pi-agent-plugin/src/entry.ts` | 插件默认导出 |
| | 🔥 `integrations/pi-agent-plugin/src/commands.ts` | 8 个斜杠命令 |
| | 🔥 `integrations/pi-agent-plugin/src/memory/tools.ts` | mem0_memory 工具注册 |
| | `integrations/pi-agent-plugin/src/telemetry.ts` | PostHog 遥测 |
| Vercel AI SDK | ⭐🔥 `integrations/vercel-ai-sdk/src/mem0-generic-language-model.ts` | LanguageModelV3 实现 |
| | `integrations/vercel-ai-sdk/src/mem0-utils.ts` | Mem0 REST API 封装 |
| | `integrations/vercel-ai-sdk/src/index.ts` | 包入口（createMem0 wrapped model） |
| n8n | ⭐🔥 `integrations/n8n-nodes-mem0/nodes/Mem0/Mem0.node.ts` | n8n 节点（INodeType） |
| Zapier | ⭐ `integrations/zapier-mem0/src/index.ts` | Zapier app 入口 |
| | `integrations/zapier-mem0/src/creates/add_memory.ts` | "Create Memory" trigger |

### Layer 11 — AI Agent Skill 体系（`skills/`）

| Skill | 主入口 | 类型 |
|-------|--------|------|
| ⭐ mem0 | `skills/mem0/SKILL.md` | Reference（always-on）—— Platform + OSS Python/TS SDK |
| ⭐ mem0-cli | `skills/mem0-cli/SKILL.md` | Reference —— 终端 CLI 指南 |
| ⭐ mem0-vercel-ai-sdk | `skills/mem0-vercel-ai-sdk/SKILL.md` | Reference —— Vercel AI provider |
| ⭐ mem0-integrate | `skills/mem0-integrate/SKILL.md` | Pipeline —— TDD 接入 Mem0（10 步管线） |
| ⭐ mem0-test-integration | `skills/mem0-test-integration/SKILL.md` | Pipeline —— 验证 integrate 产出 |
| ⭐ mem0-oss-to-platform | `skills/mem0-oss-to-platform/SKILL.md` | Pipeline —— OSS→Platform 迁移 |

`skills/mem0/references/` 含 7 篇深度参考：`architecture.md` / `sdk-guide.md` / `features.md` / `integration-patterns.md` / `use-cases.md` / `api.md` / `quickstart.md`。`skills/mem0/client/{python,node,differences}.md` 是 SDK 双语言深度参考。

### Layer 12 — Mintlify 文档站（`docs/`）

| 文件 | 说明 |
|------|------|
| ⭐ `docs/docs.json` | Mintlify 站点配置 |
| ⭐ `docs/openapi.json` | OpenAPI 规范（API 参考页数据源） |
| `docs/llms.txt` | 给 LLM 用的文档索引 |
| `docs/introduction.mdx` / `docs/api-reference.mdx` / `docs/integrations.mdx` / `docs/vibecoding.mdx` | 顶层文档 |
| `docs/api-reference/memory/` × 13 | memory endpoints API 参考 |
| `docs/api-reference/{organization,project,webhook}/` | 其他 API 参考 |
| `docs/core-concepts/` + `docs/core-concepts/memory-operations/` | 核心概念 |
| `docs/platform/` + `docs/platform/features/` × 18 | Platform 功能文档 |
| `docs/open-source/` + `docs/open-source/features/` × 9 | OSS 文档 |
| `docs/integrations/` × 32 | 第三方集成文档 |
| `docs/cookbooks/{companions,essentials,frameworks,integrations,operations}/` | 食谱 |
| `docs/migration/` | 迁移指南 |
| `docs/contributing/` | 贡献指南 |

### Layer 13 — 示例项目（`examples/`）

| 项目 | 主入口 | 说明 |
|------|--------|------|
| mem0-demo | 🔥 `examples/mem0-demo/app/api/chat/route.ts`（Edge Runtime）+ `examples/mem0-demo/components/assistant-ui/thread.tsx`（561 行） | Next.js + assistant-ui 官方 demo |
| multimodal-demo | 🔥 `examples/multimodal-demo/src/hooks/useChat.ts` + `examples/multimodal-demo/src/contexts/GlobalContext.tsx` | Vite React 多模态聊天 |
| vercel-ai-sdk-chat-app | 🔥 `examples/vercel-ai-sdk-chat-app/src/hooks/useChat.ts` + `examples/vercel-ai-sdk-chat-app/src/contexts/GlobalContext.tsx` | Vercel AI SDK 版本 |
| yt-assistant-chrome | 🔥 `examples/yt-assistant-chrome/src/content.js`（657 行）+ `examples/yt-assistant-chrome/src/background.js` + `examples/yt-assistant-chrome/src/options.js`（452 行） | YouTube 助手 Chrome MV3 扩展 |
| nemoclaw | 🔥 `examples/nemoclaw/setup-mem0-nemoclaw.sh`（864 行）+ `examples/nemoclaw/install-mem0-plugin.sh`（419 行） | NemoClaw + OpenClaw 一键安装 |
| multiagents | `examples/multiagents/llamaindex_learning_system.py` | LlamaIndex AgentWorkflow 多 Agent |
| openai-inbuilt-tools | `examples/openai-inbuilt-tools/index.js` | OpenAI 内置工具集成 |
| graph-db-demo | `examples/graph-db-demo/*.ipynb` × 5 | Neo4j/Memgraph/Kuzu/Neptune/Apache AGE notebooks |
| notebooks | `examples/notebooks/mem0-autogen.ipynb`（1219 行）+ 其他 | Jupyter demos |
| misc | `examples/misc/diet_assistant_voice_cartesia.py` 等 | 杂项示例 |

### Layer 14 — Python SDK 测试套件（`tests/`）

| 文件 | 说明 |
|------|------|
| ⭐🔥 `tests/test_memory.py` | Memory 类最大测试集 |
| 🔥 `tests/test_main.py` | server main 测试 |
| 🔥 `tests/test_client.py` | MemoryClient 测试 |
| 🔥 `tests/test_server_auth.py` | JWT 认证测试 |
| `tests/test_server_params.py` | server 参数 schema 测试 |
| `tests/test_proxy.py` | proxy 测试 |
| `tests/test_telemetry.py` + `tests/test_telemetry_aliasing.py` + `tests/test_telemetry_sampling.py` | 遥测测试 |
| `tests/test_oss_to_platform_migrate.py` | OSS→Platform 迁移测试 |
| `tests/memory/test_main.py` + `tests/memory/test_notices.py` + `tests/memory/test_safe_deepcopy_config.py` | 核心模块测试 |
| `tests/llms/test_*.py` × 3 | LLM provider 测试（OpenAI/Azure/Bedrock） |
| `tests/vector_stores/test_*.py` × 17 | vector store 适配器测试（最大测试块） |
| `tests/utils/test_entity_extraction.py` + `tests/utils/test_lemmatization.py` | 工具测试 |

### Layer 15 — CI/CD + 顶层项目配置

**CI/CD workflows**（`.github/workflows/`）：

| 文件 | 说明 |
|------|------|
| ⭐ `pipeline:.github/workflows/ci-gate.yml` | CI 单入口（PR 路由） |
| ⭐ `pipeline:.github/workflows/release.yml` | Release Router（按 tag 前缀路由） |
| `pipeline:.github/workflows/ci.yml` | Python SDK CI |
| `pipeline:.github/workflows/cd.yml` | Python SDK CD（PyPI） |
| `pipeline:.github/workflows/ts-sdk-ci.yml` + `ts-sdk-cd.yml` | TS SDK CI/CD |
| `pipeline:.github/workflows/cli-python-{ci,cd}.yml` + `cli-node-{ci,cd}.yml` | 双 CLI CI/CD |
| `pipeline:.github/workflows/{openclaw,mem0-plugin,opencode-plugin,pi-agent-plugin,n8n-nodes-mem0,zapier-mem0}-{checks,cd}.yml` | 各集成 CI/CD |
| `pipeline:.github/workflows/{issue-labeler,pr-labeler,stale,docs-llms-txt-check}.yml` | 工具 workflow |

**顶层项目配置**：

| 文件 | 说明 |
|------|------|
| ⭐ `README.md` | 项目主 README |
| ⭐ `AGENTS.md` / `CLAUDE.md` / `LLM.md` | AI 助手上下文（三份高度同步） |
| `CONTRIBUTING.md` + `SECURITY.md` | 贡献与安全 |
| `pyproject.toml` | Python 包定义（`mem0ai`） |
| `Makefile` | 顶层 lint/format/test/build |
| `.pre-commit-config.yaml` | pre-commit（ruff + isort） |
| `marketplace.json` + `.claude-plugin/marketplace.json` + `.cursor-plugin/marketplace.json` + `.codex-plugin/marketplace.json` + `.agents/plugins/marketplace.json` | 编辑器插件市场注册表（5 份） |
| `scripts/check-llms-txt-coverage.py` 🔥 | docs/llms.txt 一致性校验 |
| `scripts/oss-to-platform-migrate.sh` 🔥 | OSS→Platform 迁移脚本 |
| `scripts/llms-txt-ignore.txt` | llms.txt 忽略列表 |

---

## 6. Complexity Hotspots（complexity=complex 的热点文件）

> 这些是新手应该**谨慎对待**的高复杂度文件（共 215 个，下面按层归类关键的）：

### 6.1 核心算法（必须深入理解）
- 🔥 `mem0/memory/main.py`（3851 行）— Memory 类
- 🔥 `mem0/memory/notices.py`（1582 行）— notice 系统
- 🔥 `mem0/memory/utils.py` — 工具函数集

### 6.2 Provider 适配器（complex 代表）
- 🔥 `mem0/llms/aws_bedrock.py`（713 行，最大 LLM）
- 🔥 `mem0/vector_stores/databricks.py`（881 行）
- 🔥 `mem0/vector_stores/oracledb.py`（602 行）
- 🔥 `mem0/vector_stores/neptune_analytics.py`（535 行）
- 🔥 `mem0/vector_stores/cassandra.py`（503 行）
- 🔥 `mem0/vector_stores/azure_mysql.py`（555 行）

### 6.3 TS SDK 平行实现
- 🔥 `mem0-ts/src/oss/src/memory/index.ts`（2207 行）
- 🔥 `mem0-ts/src/oss/src/utils/notices.ts`（1434 行）
- 🔥 `mem0-ts/src/oss/src/utils/entity_extraction.ts`（828 行）
- 🔥 `mem0-ts/src/oss/src/prompts/index.ts`（1042 行）
- 🔥 `mem0-ts/src/oss/src/vector_stores/databricks.ts`（**1627 行，全仓库最大**）
- 🔥 `mem0-ts/src/oss/src/vector_stores/neptune_analytics.ts`（1120 行）
- 🔥 `mem0-ts/src/client/mem0.ts` — Hosted client

### 6.4 Server + Dashboard
- 🔥 `server/main.py` / `server/auth.py` / `server/server_state.py` / `server/routers/auth.py`
- 🔥 `server/dashboard/src/app/setup/page.tsx`（763 行）
- 🔥 `server/dashboard/src/lib/auth.tsx` / `utils/api.ts` / `middleware.ts`

### 6.5 CLI
- 🔥 `cli/python/src/mem0_cli/commands/memory.py`（718 行）
- 🔥 `cli/python/src/mem0_cli/commands/init_cmd.py`（566 行）
- 🔥 `cli/python/tests/test_commands.py`（1556 行）

### 6.6 集成（OpenClaw 是最大的）
- 🔥 `integrations/openclaw/index.ts`（1059 行）
- 🔥 `integrations/openclaw/cli/commands.ts`（1872 行）
- 🔥 `integrations/openclaw/providers.ts`（641 行）
- 🔥 `integrations/openclaw/skill-loader.ts`（693 行）
- 🔥 `integrations/mem0-plugin/.opencode-plugin/opencode-mem0.ts`（1000 行）
- 🔥 `integrations/mem0-plugin/scripts/*.py / *.sh`（7 个 lifecycle hook 都 complex）

### 6.7 大型测试集
- 🔥 `tests/test_memory.py` / `tests/test_main.py` / `tests/test_client.py` / `tests/test_server_auth.py`
- 🔥 `tests/vector_stores/test_*.py` × 17（每个 vector store 都有 complex 测试集）
- 🔥 `tests/llms/test_{openai,azure_openai,aws_bedrock}.py`

### 6.8 文档热点
- 🔥 `LLM.md`（1324 行，最详尽的 AI 助手上下文）
- 🔥 `skills/mem0/SKILL.md` + `skills/mem0/references/*.md`（6 篇全 complex）

---

## 7. 推荐学习顺序（按角色）

### 7.1 SDK 使用者（接 Mem0 到自己的应用）
1. README → installation → `mem0/__init__.py` public API
2. `docs/introduction.mdx` → `docs/core-concepts/`
3. `mem0/memory/main.py:Memory.add/search` 用法
4. `mem0/configs/base.py:MemoryConfig` 配置
5. 选 provider：`mem0/llms/openai.py` + `mem0/vector_stores/qdrant.py`（最常用组合）

### 7.2 二次开发者（改 Mem0 源码）
1. 全部 Guided Tour（15 步）
2. 深入 `mem0/memory/main.py` + `_add_to_vector_store` + `_search_vector_store`
3. Provider 抽象：5 个 base.py + `mem0/utils/factory.py`
4. 看 `tests/test_memory.py` 理解契约
5. 改 `mem0-ts/` 时对照 Python 实现

### 7.3 集成开发者（接入 AI 编辑器/agent）
1. `integrations/mem0-plugin/`（MCP server）
2. `skills/` 6 个 skill
3. `integrations/openclaw/`（最大第三方集成）
4. `integrations/vercel-ai-sdk/`（Vercel AI SDK 模式）

### 7.4 自托管运维
1. `server/`（FastAPI + Docker）
2. `server/dashboard/`（Next.js 前端）
3. `pyproject.toml` + `Makefile` + `.github/workflows/`
4. `scripts/oss-to-platform-migrate.sh`（如需迁回 Platform）

---

## 附录 A：开发环境快速搭建

```bash
# Python SDK
hatch shell dev_py_3_11           # 创建带全部依赖的环境
pre-commit install                # 装 git hooks（ruff + isort）

# TypeScript
cd mem0-ts && pnpm install
cd cli/node && pnpm install
cd integrations/vercel-ai-sdk && pnpm install
cd integrations/openclaw && pnpm install

# Server（Docker Compose）
cd server && docker-compose up    # API :8888 / PostgreSQL :8432 / Neo4j :8474

# Docs
cd docs && mintlify dev
```

## 附录 B：常用命令

```bash
make lint                         # ruff check
make format                       # ruff format
make test                         # pytest tests/
make build                        # hatch build

# TS SDK
cd mem0-ts && pnpm run test       # jest
cd mem0-ts && pnpm run build      # tsup

# Server
cd server && make build           # docker build
cd server && make run_local       # docker run
```

## 附录 C：进一步阅读

- **研究论文**：[arXiv:2504.19413](https://arxiv.org/abs/2504.19413)（Mem0, 2025）
- **外部 benchmark**：[`mem0ai/memory-benchmarks`](https://github.com/mem0ai/memory-benchmarks)（LOCOMO/LongMemEval/BEAM）
- **April 2026 算法博客**：见 README 顶部 benchmark 表
- **API 规范**：`docs/openapi.json`
- **AI 助手上下文**：`AGENTS.md` / `CLAUDE.md` / `LLM.md`

---

*生成方法：基于 `.understand-anything/knowledge-graph.json`（2071 nodes / 3600 edges / 15 layers）。如需深度解释任意文件，运行 `/understand-explain <file>`。*
