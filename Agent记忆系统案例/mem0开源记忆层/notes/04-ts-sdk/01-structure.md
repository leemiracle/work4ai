# 01 — `mem0-ts/` 整体结构 + client + oss 概览

> TS SDK 是 Python SDK 的镜像。**同一份算法,两种语言**——V3 additive extraction、entity linking、multi-signal fusion 都在 TS 版 1:1 复现。
> 本篇对比 TS 与 Python 的设计差异。

---

## 1. 整体目录

```
mem0-ts/
├── package.json             # mem0ai @ npm（v3.1.5）
├── tsup.config.ts           # tsup dual build（CJS + ESM）
├── tsconfig.json
├── README.md
├── src/
│   ├── index.ts             # ⚠️ 空（实际入口在 oss/src 和 client）
│   ├── common/              # 共用代码（exceptions 等）
│   ├── client/              # ⭐ Hosted Platform Client
│   │   ├── mem0.ts          # MemoryClient（默认 export）
│   │   ├── mem0.types.ts    # 所有 type 定义
│   │   ├── config.ts        # anon ID 管理
│   │   ├── telemetry.ts     # 遥测
│   │   ├── utils.ts         # camelCase ↔ snake_case
│   │   └── tests/
│   ├── oss/                 # ⭐ OSS Memory（self-hosted）
│   │   ├── package.json     # 独立 sub-package（"mem0ai-oss"）
│   │   ├── src/
│   │   │   ├── index.ts     # 主入口（export 全部）
│   │   │   ├── memory/      # ⭐ Memory 类
│   │   │   ├── storage/     # HistoryManager（SQLite via better-sqlite3）
│   │   │   ├── config/      # ConfigManager
│   │   │   ├── prompts/     # 同 Python（ADDITIVE_EXTRACTION_PROMPT 等）
│   │   │   ├── llms/        # 19 个 LLM provider
│   │   │   ├── embeddings/  # 12 个 embedding provider
│   │   │   ├── vector_stores/ # 27 个 vector store
│   │   │   ├── rerankers/   # 5 个 reranker
│   │   │   ├── types/       # 共享类型
│   │   │   ├── utils/       # factory / scoring / lemmatization / NER
│   │   │   └── tests/
│   │   ├── examples/        # 示例代码
│   │   └── tests/
│   └── community/           # 第三方集成（@mem0/community）
├── test/                    # jest 测试
└── README.md
```

---

## 2. 双入口

```json
// package.json exports
{
  ".": {
    "types": "./dist/index.d.ts",
    "require": "./dist/index.js",     // CJS
    "import": "./dist/index.mjs"      // ESM
  },
  "./oss": {
    "types": "./dist/oss/index.d.ts",
    "require": "./dist/oss/index.js",
    "import": "./dist/oss/index.mjs"
  }
}
```

```typescript
// Hosted（client）
import { MemoryClient } from 'mem0ai'

// OSS（self-hosted）
import { Memory } from 'mem0ai/oss'
```

---

## 3. ⭐ TS vs Python 设计对比

| 维度 | Python | TypeScript |
|------|--------|-----------|
| 抽象机制 | `ABC` + `@abstractmethod` | `interface`（更轻量） |
| 配置 | Pydantic v2 BaseModel | Zod schema |
| 异步 | `asyncio` + `AsyncMemory` 独立类 | 全 `async/await`（默认） |
| HTTP | `httpx` | `axios` |
| NER | spaCy | `compromise`（轻量 JS NLP） |
| BM25 | `fastembed` / 内置 | `natural`（JS NLP lib） |
| SQLite | `sqlite3` 标准库 | `better-sqlite3` 同步 binding |
| Factory | `provider_to_class` dict + `importlib` | `import` 静态 + factory function |
| ID 生成 | `uuid.uuid4()` | `uuid.v4()`（uuid npm 包） |
| Lint | ruff | prettier（无 lint） |
| Test | pytest | jest |
| Build | hatch | tsup（dual CJS+ESM） |

### TS 用 `interface` 的好处

```typescript
// mem0-ts/src/oss/src/llms/base.ts
export interface LLM {
  generateResponse(
    messages: Array<{ role: string; content: string }>,
    response_format?: { type: string },
    tools?: any[],
  ): Promise<any>;
  generateChat(messages: Message[]): Promise<LLMResponse>;
}
```

- 不强制继承（结构性子类型）
- 实现类用 `implements LLM`
- 多实现更灵活（TS 一个 class 可 implement 多个 interface）

---

## 4. ⭐ `MemoryClient`（Hosted）

`mem0-ts/src/client/mem0.ts`：

```typescript
export default class MemoryClient {
  apiKey: string;
  host: string;

  constructor(options: ClientOptions | string) {
    // 兼容字符串（旧版）+ 对象（新版）
    if (typeof options === 'string') {
      this.apiKey = options;
      this.host = 'https://api.mem0.ai';
    } else {
      this.apiKey = options.apiKey;
      this.host = options.host ?? 'https://api.mem0.ai';
    }
    // ...
  }

  async add(messages, options?, filters?) {
    rejectTopLevelEntityParams(options, 'add');   // ⭐ 拒绝顶层 user_id
    // 调 axios POST /memories/
    return this._request('POST', '/memories/', {...});
  }

  async search(query, options?, filters?) { ... }
  async get(memoryId) { ... }
  async get_all(options?, filters?) { ... }
  // ...
}
```

### 关键差异 vs Python

| 维度 | Python `MemoryClient` | TS `MemoryClient` |
|------|---------------------|------------------|
| HTTP | httpx | axios |
| 构造 | `MemoryClient(api_key=None, host=None, client=None)` | `MemoryClient({apiKey, host?})` 或 `MemoryClient('api_key')` |
| 异步 | 独立 `AsyncMemoryClient` | 全部 `async`（默认） |
| Identity cache | per-instance | per (host, api_key) FIFO 50 |
| 拒顶层 entity params | ✅ | ✅（同时检查 snake_case + camelCase） |

### Snake/camel 双检查

```typescript
const ENTITY_PARAMS = [
  "user_id", "agent_id", "app_id", "run_id",
  "userId", "agentId", "appId", "runId",   // ⭐ camelCase 也检查
];
```

> TS 用户偏好 camelCase,但 API 收 snake_case。Mem0 接受两者,但**必须放进 filters**。

---

## 5. ⭐ `Memory`（OSS）

`mem0-ts/src/oss/src/memory/index.ts`：

```typescript
export class Memory {
  constructor(config: MemoryConfig) {
    // 5 个 Factory 创建组件（同 Python）
    this.embeddingModel = EmbedderFactory.create(config.embedder.provider, config.embedder.config);
    this.vectorStore = VectorStoreFactory.create(config.vectorStore.provider, config.vectorStore.config);
    this.llm = LLMFactory.create(config.llm.provider, config.llm.config);
    this.historyManager = HistoryManagerFactory.create(...);
    this.reranker = config.reranker ? RerankerFactory.create(...) : null;
    // entity_store 懒加载（同 Python）
  }

  async add(messages, options?, filters?) {
    // V3 PHASED BATCH PIPELINE（8 阶段,同 Python）
  }

  async search(query, options?, filters?) {
    // Multi-signal fusion（同 Python）
  }

  // ... get, get_all, update, delete, delete_all, history, reset
}
```

> 算法实现 1:1 镜像 Python 版。看 Python 的 [`06-add-pipeline.md`](../01-py-sdk-core/06-add-pipeline.md) 就懂 TS 的 add()。

---

## 6. ⭐ 关键类型定义（types/index.ts）

```typescript
// mem0-ts/src/oss/src/types/index.ts
export interface MemoryConfig {
  vector_store: VectorStoreConfig;
  llm: LLMConfig;
  embedder: EmbedderConfig;
  history_db_path?: string;
  reranker?: RerankerConfig;
  version?: string;
  custom_instructions?: string;
  // ...
}

export interface MemoryItem {
  id: string;
  memory: string;
  hash?: string;
  metadata?: Record<string, any>;
  score?: number;
  created_at?: string;
  updated_at?: string;
}

export interface SearchFilters {
  user_id?: string;
  agent_id?: string;
  run_id?: string;
  app_id?: string;
  // ... metadata
}

export type MemoryType = 'semantic_memory' | 'episodic_memory' | 'procedural_memory';
```

> 用 Zod schema 做 runtime 验证 + TypeScript type 推断（Python 用 Pydantic）。

---

## 7. 配置示例（TS）

```typescript
import { Memory } from 'mem0ai/oss';
import { OpenAILLM } from 'mem0ai/oss';
import { Qdrant } from 'mem0ai/oss';

const memory = new Memory({
  vector_store: { provider: 'qdrant', config: { host: 'localhost', port: 6333 } },
  llm: { provider: 'openai', config: { apiKey: process.env.OPENAI_API_KEY, model: 'gpt-5-mini' } },
  embedder: { provider: 'openai', config: { apiKey: process.env.OPENAI_API_KEY, model: 'text-embedding-3-small' } },
  history: { path: './history.db' },
});

await memory.add('I prefer dark mode', { user_id: 'alice' });
const results = await memory.search('preferences', { user_id: 'alice' });
```

---

## 8. ⭐ Client 端 camelCase ↔ snake_case 转换

```typescript
// mem0-ts/src/client/utils.ts
export function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
}

export function camelToSnakeKeys(obj: any): any {
  // 递归转
}

export function snakeToCamelKeys(obj: any): any {
  // 递归转
}
```

> Mem0 Platform API 用 snake_case（Python 后端）。TS 用户传 camelCase 时,client 自动转。返回的 snake_case 也自动转成 camelCase 给用户。

---

## 9. exceptions 体系

```
mem0-ts/src/common/exceptions.ts
```

```typescript
export class MemoryError extends Error { /* base */ }
export class AuthenticationError extends MemoryError { }
export class RateLimitError extends MemoryError { 
  retryAfter?: number;
}
export class ValidationError extends MemoryError { }
export class MemoryNotFoundError extends MemoryError { }
export class NetworkError extends MemoryError { }
export class ConfigurationError extends MemoryError { }
export class MemoryQuotaExceededError extends MemoryError { }

export function createExceptionFromResponse(...) { ... }
```

> 镜像 Python 的 `mem0/exceptions.py`(484 行)。

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| TS 19 个 LLM / 12 个 embedder / 27 个 vector store | [`02-providers-and-types.md`](./02-providers-and-types.md) |
| Python SDK 同位置 | [`../01-py-sdk-core/`](../01-py-sdk-core/) |
| 双模式对比 | [`../00-overview/05-two-modes.md`](../00-overview/05-two-modes.md) |

---

📌 **下一步** → [`02-providers-and-types.md`](./02-providers-and-types.md) TS 侧 providers 对照 Python。
