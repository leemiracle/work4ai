# 03 — 构建系统（Hatch + pnpm + tsup + Docker）

> 这是 polyglot monorepo 的代价：**每个子包用不同的构建工具**。本篇把每个包的构建链一次讲清楚,以及为什么这么选。

---

## 1. 全仓库构建工具一览

| 包 | 语言 | 构建工具 | 包管理 | Lint | 测试 |
|----|------|---------|--------|------|------|
| `mem0/` (Python SDK) | Python 3.10+ | **hatchling** + hatch | hatch env | ruff (120) | pytest |
| `mem0-ts/` (TS SDK) | TS | **tsup** (CJS+ESM) | **pnpm** | prettier | jest |
| `cli/python/` | Python 3.10+ | hatchling + hatch | hatch env | ruff (100) + 额外规则 | pytest |
| `cli/node/` | TS | tsup (ESM only) | pnpm | **biome**（不是 ESLint） | vitest |
| `integrations/vercel-ai-sdk/` | TS | tsup (CJS+ESM) | pnpm | ESLint + Prettier | jest + vitest |
| `integrations/openclaw/` | TS | tsup (ESM) | pnpm | — | vitest |
| `integrations/mem0-plugin/` | Python + TS | Python 用 venv / TS 用 bun | mixed | ruff / tsc | pytest / bun |
| `integrations/pi-agent-plugin/` | TS | tsup | pnpm | tsc | vitest |
| `integrations/n8n-nodes-mem0/` | TS | tsc | pnpm | ESLint (n8n-rules) | — |
| `integrations/zapier-mem0/` | TS | tsc | pnpm | — | zapier CLI |
| `server/` | Python 3.12 | Docker + uvicorn | pip + requirements.txt | — | — |
| `docs/` | mdx | Mintlify | npm | — | — |

**注意几个反直觉点**：
- `mem0/` 和 `cli/python/` 都是 Python 但 **ruff line-length 不同**（120 vs 100），规则集也不同
- `mem0-ts/` 不用 ESLint，只用 Prettier
- `cli/node/` 用 Biome（不是 ESLint），用 vitest（不是 jest）
- TS 包**全部用 pnpm**——README/AGENTS.md 反复强调"不要用 npm/yarn"

---

## 2. Python SDK 构建（`mem0/`）

### 2.1 pyproject.toml 核心结构

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mem0ai"
version = "2.0.17"
requires-python = ">=3.10,<4.0"

# 核心 8 个依赖（启动用，所有 provider 不在这里）
dependencies = [
    "qdrant-client>=1.12.0",   # 默认 vector store
    "pydantic>=2.7.3",          # 配置/数据模型
    "openai>=1.90.0",           # 默认 LLM + embedding
    "httpx>=0.28.0",            # HTTP client
    "posthog>=7.14.0",          # 遥测
    "pytz>=2024.1",
    "sqlalchemy>=2.0.31",
    "protobuf>=5.29.6,<7.0.0",
]

# Optional extras —— 用户按需安装
[project.optional-dependencies]
nlp = ["spacy>=3.7.0"]              # 用于 entity extraction/BM25 lemmatize
vector-stores = [...]                # ~20 个 vector store 客户端
llms = [...]                         # 6 个 LLM 客户端
extras = [...]                       # langchain / transformers / opensearch 等
test = [...]                         # pytest 全家桶
dev = ["ruff==0.16.0", "isort", "pytest"]
```

> **核心 8 个依赖保证 `pip install mem0ai` 即装即用**（默认走 OpenAI + Qdrant）。所有其他 provider 都是 optional extras。

### 2.2 Hatch 多版本 Python 环境

```toml
[tool.hatch.envs.dev_py_3_10]
python = "3.10"
features = ["test", "vector-stores", "llms", "extras"]

[tool.hatch.envs.dev_py_3_11]
python = "3.11"
features = ["test", "vector-stores", "llms", "extras"]

[tool.hatch.envs.dev_py_3_12]
python = "3.12"
features = ["test", "vector-stores", "llms", "extras"]
```

- Hatch 给每个 Python 版本建独立环境（**矩阵测试**）
- 每个环境都装 `test + vector-stores + llms + extras`（完整覆盖）
- 使用：`hatch shell dev_py_3_11` 进入 3.11 完整环境

### 2.3 hatchling 的 include/exclude（坑点）

```toml
[tool.hatch.build]
include = ["mem0/**/*.py"]
exclude = ["**/*", "!mem0/**/*.py"]   # 先全排除,再白名单 mem0/

[tool.hatch.build.targets.wheel]
packages = ["mem0"]
only-include = ["mem0"]
```

**这个 exclude/include 反直觉**：先 `**/*` 全排除，再 `!mem0/**/*.py` 反向白名单。结果：wheel 里**只有 `mem0/` 下的 .py**——tests/、docs/、README、LICENSE 等都不进 wheel。

### 2.4 Makefile（开发快捷方式）

```makefile
format:    hatch run format         # ruff format
sort:      hatch run isort mem0/
lint:      hatch run lint           # ruff check
test:      hatch run test           # pytest tests/
test-py-3.10/3.11/3.12:             # 矩阵测试
docs:      cd docs && mintlify dev  # 本地文档
build:     hatch build
publish:   hatch publish
```

---

## 3. TypeScript SDK 构建（`mem0-ts/`）

### 3.1 dual CJS+ESM 输出（tsup）

```json
{
  "main": "./dist/index.js",         // CJS 入口
  "module": "./dist/index.mjs",      // ESM 入口
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "require": "./dist/index.js",
      "import": "./dist/index.mjs"
    },
    "./oss": { /* 同结构 */ }
  }
}
```

**两个入口**：
- `mem0ai` 主入口 → `MemoryClient`（hosted）
- `mem0ai/oss` 子路径 → `Memory`（self-hosted）

### 3.2 tsup.config（内嵌 package.json）

```json
"tsup": {
  "entry": ["src/index.ts"],
  "format": ["cjs", "esm"],
  "dts": { "resolve": true },
  "splitting": false,
  "sourcemap": true,
  "clean": true,
  "treeshake": true,
  "minify": false,                   // 不压缩！调试友好
  "external": ["@mem0/community"],
  "noExternal": ["!src/community/**"]
}
```

**关键选择**：
- `minify: false` —— 生产包不压缩，方便用户调试和报错栈追溯
- `splitting: false` —— 不做代码分割，单 bundle
- `treeshake: true` —— 但开 tree-shake
- dual CJS+ESM —— 同时支持 CommonJS 和 ES Modules

### 3.3 pnpm peerDependencies（核心设计）

所有 provider 客户端都是 `peerDependencies` + `peerDependenciesMeta.optional = true`：

```json
"peerDependencies": {
  "@anthropic-ai/sdk": "^0.40.1",
  "@qdrant/js-client-rest": "^1.18.0",
  "redis": "^4.6.13",
  // ... 30+ 个
},
"peerDependenciesMeta": {
  "@qdrant/js-client-rest": { "optional": true },
  "redis": { "optional": true },
  // 全部 optional
}
```

**含义**：
- 用户不安装就不引入（**懒依赖**）
- 用户用到哪个 provider 才 `pnpm add @qdrant/js-client-rest`
- TS SDK 本身体积小，不会拖一堆客户端

### 3.4 大量 pnpm.overrides（安全补丁）

```json
"pnpm": {
  "overrides": {
    "form-data@<4.0.6": ">=4.0.6",      // 安全漏洞
    "minimatch@<3.1.3": "^3.1.3",
    "uuid@<11.1.1": ">=11.1.1",
    // ... 30+ 个
  }
}
```

每次 npm 包出 CVE，Mem0 通过 pnpm overrides 强制提升 transitive dep 版本。最近的 commit (`4debc58a`) 就是 "patch 8 HIGH + 18 MEDIUM Vanta vulnerabilities across 4 pnpm workspaces"。

### 3.5 测试矩阵（jest）

```json
"scripts": {
  "test": "jest",
  "test:ci": "jest --coverage --ci",
  "test:unit": "jest --coverage --ci --testPathIgnorePatterns='/node_modules/' '/dist/' 'integration'",
  "test:integration": "jest --config jest.integration.config.js --forceExit",
  "test:watch": "jest --config jest.config.js --watch"
}
```

单测和集成测分开跑——集成测需要真实 `MEM0_API_KEY` 打 hosted API。

---

## 4. Python CLI 构建（`cli/python/`）

跟主 SDK 类似但有几个差异：

| 维度 | mem0/ | cli/python/ |
|------|-------|-------------|
| Python 版本 | ≥3.10 | ≥3.10（一致） |
| ruff line-length | 120 | **100** |
| ruff 规则 | E4/E7/E9/F（极简） | E/F/I/W/UP/B/SIM/RUF（严格） |
| ignore | — | E501, B008, SIM108 |
| 入口 | import | **console script** `mem0 = "mem0_cli.app:main"` |
| `mem0ai` 依赖 | — | optional `[oss]` extra |

```toml
[project.scripts]
mem0 = "mem0_cli.app:main"   # pip install 后直接命令行 mem0

[project.optional-dependencies]
oss = ["mem0ai>=0.1.0"]      # OSS 模式可选
```

> **设计选择**：CLI 默认是 hosted client 模式（httpx → api.mem0.ai），不需要装 mem0ai 全家桶；用户想用 OSS 模式才 `pip install mem0-cli[oss]`。

---

## 5. Node CLI 构建（`cli/node/`）

ESM only + Biome + vitest（全反主流）：

```json
{
  "name": "@mem0/cli",
  "type": "module",                          // ESM only
  "bin": { "mem0": "./dist/index.js" },
  "scripts": {
    "build": "tsup",
    "test": "vitest run",                    // 不是 jest
    "lint": "biome check src/",              // 不是 eslint
    "lint:fix": "biome check --write src/",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "commander": "^12.0.0",                  // 命令框架
    "chalk": "^5.3.0",                       // 颜色
    "cli-table3": "^0.6.4",                  // 表格
    "ora": "^8.0.0",                         // spinner
    "boxen": "^7.1.0"                        // box 输出
  }
}
```

> 为什么 Biome 不是 ESLint？Biome 是 Rust 实现的单二进制 linter/formatter，比 ESLint+Prettier 快几十倍。新的 TS 包倾向于用它。

---

## 6. Server 构建（`server/`）

### 6.1 Dockerfile（极简生产镜像）

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

> 注意：生产 Dockerfile 还带 `--reload`（dev 友好但生产略有开销）。

### 6.2 docker-compose.yaml（3 服务）

实际文件名是 `docker-compose.yaml`（不是 `.yml`），需要：
- **FastAPI**（端口 8888）
- **PostgreSQL + pgvector**（端口 8432）
- **Neo4j**（端口 8474 / 8687） —— 注意 Neo4j 在 server 还在用（即使 SDK 移除了 graph）

### 6.3 dev.Dockerfile（开发用）

`dev.Dockerfile`（不是 `Dockerfile.dev`）—— mount 源码进容器，auto-reload。

### 6.4 server/ 内部子目录

```
server/
├── Dockerfile             # 生产镜像
├── dev.Dockerfile         # 开发镜像（mount）
├── docker-compose.yaml    # 3 服务编排
├── Makefile               # up/down/seed/bootstrap/...
├── main.py                # FastAPI app
├── auth.py                # 鉴权
├── db.py                  # SQLAlchemy 引擎
├── models.py              # ORM 模型
├── schemas.py             # Pydantic schemas
├── rate_limit.py          # 限流
├── server_state.py        # 应用全局状态
├── errors.py
├── telemetry.py
├── init-db.sh             # 启动脚本
├── alembic/               # DB migration
├── alembic.ini
├── dashboard/             # 独立 dashboard 子项目
├── routers/               # API 路由分模块
├── scripts/               # 运维脚本（seed/reset-password/prune-logs）
├── requirements.txt
└── README.md
```

### 6.5 Makefile 关键命令

```makefile
up:        # 启动 + 等 API+Dashboard 就绪
bootstrap: up wait-api wait-dashboard seed   # 一键起 + 注册 admin
down / clean / logs / health
build:     docker build -t mem0-api-server .
run_local: docker run -p 8000:8000 -v $(pwd):/app mem0-api-server --env-file .env
seed:      # 注入初始数据（创建 admin + API key）
```

---

## 7. 构建工具选择的"为什么"

| 决策 | 替代方案 | Mem0 的选择理由 |
|------|---------|---------------|
| Python 用 hatch 而不是 poetry | poetry | hatch 支持多 Python 版本矩阵环境，且更接近 PEP 621 标准 |
| TS 用 pnpm 不是 npm | npm/yarn | pnpm 节省磁盘（hardlink）、workspace 强、安全补丁 overrides 强 |
| TS SDK dual CJS+ESM | ESM only | 兼容老 Node 项目（CJS）+ 现代项目（ESM） |
| TS SDK 不 minify | minify | 调试友好；用户报错栈可读 |
| TS SDK `peerDependencies` 全 optional | 全 hard dep | 用户只装用得到的 provider 客户端 |
| Node CLI 用 Biome 不是 ESLint | ESLint+Prettier | Biome 单工具快几十倍 |
| 不同包用不同 line-length | 全仓库统一 | 历史原因；统一改造工作量大 |
| Server 用 Dockerfile + compose | K8s | 自托管用户起点低；K8s 交给用户自己包 |

---

## 8. 一个完整的开发流程示例

假设要给 Python SDK 加一个新 LLM provider：

```bash
# 1. 进入 hatch 环境（3.11 为例）
hatch shell dev_py_3_11

# 2. 写代码 mem0/llms/new_provider.py + tests/llms/test_new_provider.py

# 3. 装依赖（如果新 provider 需要新包）
# 编辑 pyproject.toml 在 [project.optional-dependencies] llms 加上
pip install -e '.[llms]'

# 4. 跑 lint + test
make lint
make format
make test
# 或矩阵测试
make test-py-3.10 && make test-py-3.11 && make test-py-3.12

# 5. pre-commit hook 自动跑 ruff + isort
git add . && git commit -m "feat(llms): add new_provider support"

# 6. 本地 build 验证
make build    # hatch build → dist/mem0ai-*.whl

# 7. 推 + PR
git push origin feature/new-provider
# CI Gate 会自动检测 mem0/** 变动,跑 ci.yml
```

---

## 9. 文档构建（`docs/`）

```bash
make docs   # = cd docs && mintlify dev
```

[Mintlify](https://mintlify.com/) 是文档专用静态站点生成器：
- 用 `.mdx` 写（247 个）
- 自动从 `openapi.json` 生成 API reference
- 主题精美，搜索/导航内置
- 部署在 Mintlify CDN（不是 GitHub Pages）

> ⚠️ 改 `.mdx` 必须同步 `docs/llms.txt`（这是给 LLM 用的文档索引）。`docs-llms-txt-check.yml` workflow 会在 PR 上强制检查。本地用 `python scripts/check-llms-txt-coverage.py --write` 修复。

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| CI/CD 编排细节 | [`04-cicd.md`](./04-cicd.md) |
| Server 怎么把 SDK 包成 REST | [`05-server/01-architecture.md`](../05-server/01-architecture.md) |
| 命令行入口怎么实现 | [`06-cli-python/01-entry-and-commands.md`](../06-cli-python/01-entry-and-commands.md) |

---

📌 **下一步** → [`04-cicd.md`](./04-cicd.md) CI Gate 单入口编排 + Release Router 单入口发布。
