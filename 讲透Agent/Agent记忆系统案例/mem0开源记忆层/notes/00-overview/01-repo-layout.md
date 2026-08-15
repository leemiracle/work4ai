# 01 — 仓库布局与 Polyglot Monorepo 设计动机

> Mem0 是个 **polyglot monorepo**（一个仓库里同时放 Python 包 + TypeScript 包 + 两个 CLI + 6 个集成 + server + 文档）。
> 搞清楚每个目录为什么存在、跟谁有依赖关系，是后续精读所有源码的入口。

---

## 1. 顶层目录速览

按"角色"分组（不按字母序），方便理解依赖方向：

```
mem0/
├── 🧠 核心引擎（两层）
│   ├── mem0/                # Python SDK（核心）—— mem0ai @ PyPI
│   └── mem0-ts/             # TypeScript SDK（核心翻译）—— mem0ai @ npm
│
├── ⌨️ 用户入口（CLI）
│   ├── cli/python/          # mem0-cli @ PyPI（Typer + Rich）
│   └── cli/node/            # @mem0/cli @ npm（Commander + Chalk）
│
├── 🖥 自托管服务端
│   └── server/              # FastAPI REST server（Docker: PG/pgvector + Neo4j）
│
├── 🔗 第三方平台集成
│   └── integrations/
│       ├── mem0-plugin/              # AI 编辑器 MCP（Claude Code/Cursor/Codex/OpenCode）
│       ├── openclaw/                 # @mem0/openclaw-mem0
│       ├── pi-agent-plugin/          # @mem0/pi-agent-plugin
│       ├── vercel-ai-sdk/            # @mem0/vercel-ai-provider
│       ├── n8n-nodes-mem0/           # @mem0/n8n-nodes-mem0
│       └── zapier-mem0/              # Zapier Platform CLI app（不入 npm，部署到 Zapier）
│
├── 🎓 AI 工具知识
│   └── skills/             # Claude Code skill 定义（参考型 + 流水线型）
│
├── 📚 文档与示例
│   ├── docs/               # Mintlify 文档站（247 个 mdx）
│   ├── examples/           # 可跑示例（含 notebooks/）
│   └── evaluation/         # git submodule → mem0ai/memory-benchmarks
│
├── 🧪 测试
│   └── tests/              # Python SDK 的 pytest 测试
│
├── ⚙️ 元配置（项目级）
│   ├── pyproject.toml      # Python SDK 配置（hatch）
│   ├── poetry.lock         # （历史遗留，与 hatch 共存）
│   ├── Makefile            # make lint/test/format/build 等快捷命令
│   ├── .pre-commit-config.yaml
│   ├── marketplace.json    # 编辑器插件市场注册表（顶层 + 4 个 plugin 目录共 5 份）
│   ├── AGENTS.md / CLAUDE.md / LLM.md   # 给 AI assistant 看的项目说明
│   └── .github/workflows/  # CI/CD（详见 04-cicd.md）
```

---

## 2. 依赖关系图（谁依赖谁）

```mermaid
graph TD
    PySDK[mem0/<br/>Python SDK 核心]
    TSSDK[mem0-ts/<br/>TS SDK]
    PyCLI[cli/python/<br/>mem0-cli]
    NodeCLI[cli/node/<br/>@mem0/cli]
    Server[server/<br/>FastAPI]
    Integrations[integrations/*<br/>6 个集成包]
    Skills[skills/<br/>AI skill 定义]

    %% CLI 依赖 SDK
    PyCLI -.可选 [oss] extra.-> PySDK
    NodeCLI --> TSSDK

    %% Server 依赖 SDK
    Server --> PySDK

    %% 集成依赖 SDK
    Integrations --> TSSDK
    Integrations -.部分.-> PySDK

    %% Skills 是静态文档,引用 SDK 但运行时不依赖
    Skills -.引用.-> PySDK
    Skills -.引用.-> TSSDK
```

**关键观察**：
- **Python SDK 是真相之源**——Server、Python CLI、部分集成都依赖它
- **TS SDK 是另一条独立链**——Node CLI、大部分集成依赖它
- **Python CLI 和 TS CLI 不互相依赖**——两条独立入口
- **skills/ 是静态文档**（`.md` + `.json`），运行时无依赖，只是"AI 工具读它来理解 SDK"

---

## 3. 为什么是 Polyglot Monorepo 而不是两个仓库？

这是个权衡决策，看 Mem0 的选择：

| 优点 | 代价 |
|------|------|
| Python 和 TS SDK **API 同步**（`Memory.add()` / `Memory.search()` 在两边签名一致）——一处设计变更可以同时改两边 | 单仓库大、`git clone` 慢（含 lockfile 几十 MB） |
| 跨语言的**集成测试**可以共享 fixtures（examples/ + evaluation/） | CI/CD 必须区分路径触发（见 `ci-gate.yml`），不能简单"push 就全测" |
| 文档（docs/）只需维护一份，同时覆盖 Py + TS 用法 | 工具链混杂：hatch + pnpm + tsup + Docker + Mintlify 共存 |
| **跨包 breaking change** 一 PR 同步完成 | 贡献者需要懂多套工具链 |
| Issue/PR 集中追踪 | repo star/fork 单一指标（无 PyPI 下载量等分语言指标） |

Mem0 选 monorepo 是因为它的核心价值主张是 **"同一 API,多语言多平台"** ——分仓库会让"保持 API 同步"成本爆炸。

---

## 4. Python SDK (`mem0/`) 内部结构详解

最重要的目录，单独展开：

```
mem0/
├── __init__.py              # 6 行！只 re-export 4 个类（Memory/AsyncMemory/MemoryClient/AsyncMemoryClient）
├── memory/
│   ├── base.py              # MemoryBase 抽象基类（63 行,只 5 个抽象方法）
│   ├── main.py              # ⭐ Memory 类（3851 行核心引擎）+ AsyncMemory
│   ├── storage.py           # SQLiteManager（变更历史 + 最近 10 条 session 消息）
│   ├── utils.py             # 消息解析、JSON 抽取、telemetry filter 处理
│   ├── telemetry.py         # PostHog 遥测封装
│   ├── notices.py           # 用户运行时 notice（first-run/scale/slow-query/decay/temporal）
│   ├── setup.py             # 启动配置：创建 ~/.mem0 目录、加载 config 文件
│   └── __init__.py
│
├── client/                  # Hosted Platform Client
│   ├── main.py              # ⭐ MemoryClient / AsyncMemoryClient（HTTP→platform.mem0.ai）
│   └── ...
│
├── llms/                    # LLM 抽象 + 21 个 provider
│   ├── base.py              # LLMBase 抽象基类
│   ├── configs.py           # BaseLlmConfig
│   ├── openai.py            # 默认 provider
│   ├── anthropic.py gemini.py ollama.py ...
│   └── __init__.py
│
├── embeddings/              # Embedding 抽象 + 15 个 provider
│   ├── base.py
│   ├── configs.py
│   └── openai.py huggingface.py ollama.py ...
│
├── vector_stores/           # Vector Store 抽象 + 28 个 provider（最多）
│   ├── base.py              # VectorStoreBase 抽象
│   ├── configs.py
│   └── qdrant.py pinecone.py chroma.py pgvector.py ...
│
├── graphs/                  # Graph memory（Neo4j/Memgraph/Kuzu/AGE）
│   ├── base.py
│   ├── neo4j.py memgraph.py kuzu.py age.py
│   └── utils.py
│
├── reranker/                # 5 个 reranker（Cohere/HF/LLM/SentenceTransformer/ZeroEntropy）
│   ├── base.py
│   └── ...
│
├── configs/
│   ├── base.py              # ⭐ MemoryConfig（顶层配置容器）+ MemoryItem + AzureConfig
│   ├── enums.py             # MemoryType (SEMANTIC/EPISODIC/PROCEDURAL)
│   ├── prompts.py           # ⭐ 1062 行 prompt 模板系统
│   ├── embeddings/          # 各 provider 的 config 类
│   ├── llms/
│   ├── rerankers/
│   └── vector_stores/
│
├── utils/                   # 跨模块工具
│   ├── factory.py           # ⭐ 4 个 Factory 类（动态加载 provider 的核心）
│   ├── factory.py           # 已述
│   ├── entity_extraction.py # April 2026 新算法的实体抽取
│   ├── scoring.py           # BM25 + entity boost 多信号融合
│   ├── lemmatization.py     # spaCy lemmatize for BM25
│   ├── factory.py
│   ├── http.py              # HTTP client 工具
│   └── ...
│
├── proxy/                   # HTTP 代理支持
├── exceptions.py            # Mem0 异常体系
└── __init__.py
```

> 💡 **看代码顺序建议**：先 `__init__.py`（6 行）→ `memory/base.py`（63 行）→ `memory/main.py`（3851 行核心）→ `utils/factory.py`（280 行）→ 任选一个 provider 子目录（推荐 `llms/openai.py`）。

---

## 5. TypeScript SDK (`mem0-ts/`) 结构

```
mem0-ts/
├── src/
│   ├── client/              # MemoryClient —— Hosted Platform Client（HTTP）
│   ├── oss/                 # Memory —— Self-hosted OSS（与 Python 对应）
│   │   ├── llms/
│   │   ├── embeddings/
│   │   ├── vector_stores/
│   │   └── graphs/
│   ├── types/               # TypeScript 类型定义
│   └── utils/
├── test/                    # jest 测试
├── tsup.config.ts           # tsup 构建（CJS + ESM）
├── package.json             # mem0ai @ npm
└── README.md
```

**对照 Python**：模块组织几乎一对一映射，但 provider 数量较少（TS OSS 主要支持主流几个），核心是 client 模式。

详见 [`04-ts-sdk/`](../04-ts-sdk/) 系列。

---

## 6. Server (`server/`) 结构

```
server/
├── main.py                  # FastAPI app（560 行）
├── routers/                 # API 路由分模块
├── __init__.py
├── Dockerfile               # 生产构建
├── Dockerfile.dev           # 开发构建（mount 源码,auto-reload）
├── docker-compose.yml       # 3 服务编排:FastAPI + PostgreSQL/pgvector + Neo4j
├── Makefile                 # make build / make run_local / make bootstrap
└── ...
```

详见 [`05-server/`](../05-server/) 系列。

---

## 7. Skills 与 Integrations 的区别（容易混）

| 维度 | `skills/` | `integrations/` |
|------|-----------|----------------|
| 本质 | 静态文档（md + json） | 可执行的代码包 |
| 给谁看 | AI coding assistant（Claude Code 等）读取 | 第三方平台（n8n/Zapier/Vercel AI SDK 等）运行 |
| 是否发布 | 跟随主仓库（不单独 publish） | 大多发布到 npm/Zapier marketplace |
| 子目录数 | 6（mem0/mem0-cli/mem0-integrate/mem0-test-integration/mem0-oss-to-platform/mem0-vercel-ai-sdk） | 6（mem0-plugin/openclaw/pi-agent-plugin/vercel-ai-sdk/n8n-nodes-mem0/zapier-mem0） |
| 关系 | skills 教 AI **如何用** mem0 | integrations 让 **其他系统**接入 mem0 |

> 注意：`integrations/mem0-plugin/` 同时被 `skills/` 引用——它本身是 MCP server + skills 容器（包含 `.opencode-plugin/`、`.claude-plugin/` 等）。

---

## 8. 路径配置与"根目录"

Mem0 用一个全局目录存放数据，逻辑在 `mem0/memory/setup.py`：

```python
home_dir = os.path.expanduser("~")
mem0_dir = os.environ.get("MEM0_DIR") or os.path.join(home_dir, ".mem0")
```

- 默认 `~/.mem0/`
- 可用 `MEM0_DIR` 环境变量覆盖
- 里面有：`history.db`（SQLite）、`migrations_qdrant/`（telemetry）、`config.json`（用户配置）等

---

## 9. 与上游仓库的关系

这是 fork（路径 `~/ai/photo/ocr/mem0`），笔记写在 `notes/` 不污染上游。

`AGENTS.md`/`CLAUDE.md`/`LLM.md` 是上游维护的、给 AI coding assistant 看的"项目导览"，内容会随上游变动。本笔记系列是对**源码本身**的精读，独立于这份数据。

---

## 10. 关键认知点回顾

| 事实 | 含义 |
|------|------|
| `mem0/__init__.py` 只 6 行 | API 表面"窄"——只有 4 个入口类 |
| `MemoryBase` 抽象只 5 个方法 | `add`/`search` **不**在抽象基类——具体实现自由设计签名 |
| `memory/main.py` 3851 行 | 整个仓库最复杂的文件,核心引擎 |
| Provider 数量:LLM 21 / VS 28 / Embed 15 / Graph 4 / Reranker 5 | "可插拔"是 Mem0 的核心卖点 |
| 247 个 mdx 文档 | 上游已经维护了非常完整的文档站——本笔记不重复,只补"源码视角" |
| `evaluation/` 是 git submodule | 跑 benchmark 要 `git submodule update --init` |

---

📌 **下一步** → [`02-architecture.md`](./02-architecture.md) 整体架构图与组件数据流。
