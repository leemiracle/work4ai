# 02 — TS 侧 Providers 对照 Python

> TS SDK 的 providers 是 Python 的"翻译版",但有几个**故意差异**——比如 NLP 用 `compromise`/`natural` 而非 spaCy,embed_batch 用 Promise.all 并发。

---

## 1. Provider 数量对比

| 类别 | Python | TS |
|------|-------|-----|
| LLMs | 21 | 19 |
| Embeddings | 15 | 12 |
| Vector Stores | 28 | 27 |
| Rerankers | 5 | 5 |
| Graphs | ❌ 移除 | ❌ 移除 |

> TS 略少（移除了部分小众 provider 如 `langchain`、`litellm`、`azure_openai_structured` 等）。

---

## 2. LLMs（19 个）

```
mem0-ts/src/oss/src/llms/
├── base.ts            # LLM interface
├── openai.ts          # 默认
├── openai_structured.ts
├── anthropic.ts
├── azure.ts           # Azure OpenAI
├── google.ts          # Gemini
├── groq.ts
├── ollama.ts
├── lmstudio.ts
├── mistral.ts
├── deepseek.ts
├── minimax.ts
├── sarvam.ts
├── together.ts
├── vllm.ts
├── xai.ts
├── aws_bedrock.ts
├── langchain.ts
└── litellm.ts
```

### `LLM` interface

```typescript
export interface LLM {
  generateResponse(
    messages: Array<{ role: string; content: string }>,
    response_format?: { type: string },
    tools?: any[],
  ): Promise<any>;
  generateChat(messages: Message[]): Promise<LLMResponse>;
}
```

> 比 Python 简化：**没有 `_is_reasoning_model` / `_get_supported_params` 等智能 helper**——TS 直接让每个 provider 自己处理 reasoning model 适配。

---

## 3. Embeddings（12 个）

```
mem0-ts/src/oss/src/embeddings/
├── base.ts            # Embedder interface
├── openai.ts
├── azure.ts
├── ollama.ts
├── huggingface.ts
├── google.ts
├── vertexai.ts
├── together.ts
├── lmstudio.ts
├── aws_bedrock.ts
├── fastembed.ts       # 浏览器端轻量
└── langchain.ts
```

### `Embedder` interface

```typescript
export interface Embedder {
  embed(text: string, memoryAction?: "add" | "search" | "update"): Promise<number[]>;
}
```

> 注意：**没 `embedBatch` 方法**！每个 provider 自己实现 batch（在 client 调用层用 `Promise.all([...])` 并发）。

---

## 4. Vector Stores（27 个）

```
mem0-ts/src/oss/src/vector_stores/
├── base.ts                    # VectorStore interface
├── qdrant.ts / pinecone.ts / chroma.ts / pgvector.ts / ...
├── memory.ts                  # ⚠️ 内存 vector store（开发用）
├── vectorize.ts               # Cloudflare Vectorize
├── s3_vectors.ts / neptune_analytics.ts / turbopuffer.ts
└── ...
```

### `VectorStore` interface

```typescript
export interface VectorStore {
  createCol(...): Promise<void>;
  insert(...): Promise<void>;
  search(...): Promise<SearchResult[]>;
  delete(...): Promise<void>;
  update(...): Promise<void>;
  get(...): Promise<any>;
  listCols(...): Promise<any>;
  deleteCol(...): Promise<void>;
  // ...
}
```

> 跟 Python 12 个 abstract method 一致。但 TS 用 Promise（全 async）。

### `memory.ts`（内存开发用）

```typescript
// mem0-ts/src/oss/src/vector_stores/memory.ts
// 完全在内存的 vector store,不持久化
// 用途：开发、测试、示例
```

> Python 没这个等价物（开发用 FAISS 本地文件）。TS 加内存版是为了**浏览器端可用**。

---

## 5. Rerankers（5 个）

```
mem0-ts/src/oss/src/rerankers/
├── base.ts           # Reranker interface
├── cohere.ts
├── cross_encoder.ts  # = Python 的 sentence_transformer
├── llm.ts            # = Python 的 llm_reranker
├── zeroentropy.ts
└── (Python 的 huggingface 没在这里——TS 用 cross_encoder 替代)
```

---

## 6. ⭐ NLP 替代方案

| 用途 | Python | TypeScript |
|------|--------|-----------|
| NER（entity 抽取） | spaCy (`en_core_web_sm`) | **`compromise`** 14KB 轻量 |
| BM25 lemmatize | spaCy lemmatizer | **`natural`** JS NLP |
| BM25 sparse vector | `fastembed` `Qdrant/bm25` | `natural` BM25 / Qdrant sparse |

### 为什么换

| 维度 | spaCy | compromise |
|------|-------|----------|
| 包大小 | 几百 MB（含 model） | **14 KB** |
| 启动时间 | 1-2s | <100ms |
| 浏览器端 | ❌ | ✅ |
| 准确度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

> Mem0 TS 主要服务前端/Node.js 场景,spaCy 太重。`compromise` 牺牲少量精度换便携性。

---

## 7. ⭐ Factory 模式

```typescript
// mem0-ts/src/oss/src/utils/factory.ts（精简）
import { OpenAILLM } from "../llms/openai";
import { AnthropicLLM } from "../llms/anthropic";
// ... 静态 import 所有 provider

export class LLMFactory {
  static create(provider: string, config: LLMConfig): LLM {
    switch (provider) {
      case "openai": return new OpenAILLM(config);
      case "anthropic": return new AnthropicLLM(config);
      // ...
      default: throw new Error(`Unsupported LLM provider: ${provider}`);
    }
  }
}
```

### Python vs TS Factory

| 维度 | Python | TS |
|------|--------|-----|
| Provider 注册 | dict + `importlib.import_module` | `switch` + 静态 import |
| 懒加载 | ✅（只用到的才 import） | ❌（全 bundle,但 tree-shake 帮一点） |
| 第三方扩展 | `register_provider()` API | ❌（要改源码或 PR） |
| Bundle 大小 | 0 影响（运行时 import） | 受 peerDependencies 影响 |

> TS 用静态 import 因为 ESM 没有等价的 `importlib`（动态 import 是 `await import()` 但异步不便）。

---

## 8. ⭐ Prompts 系统

```
mem0-ts/src/oss/src/prompts/
└── index.ts
```

```typescript
// 包含所有 Python prompts.py 的等价物
export const ADDITIVE_EXTRACTION_PROMPT = `...`;     // 同 Python
export const AGENT_CONTEXT_SUFFIX = `...`;
export const PROCEDURAL_MEMORY_SYSTEM_PROMPT = `...`;
// ... 

export function generateAdditiveExtractionPrompt(...): string { ... }
export function getFactRetrievalMessages(...): any[] { ... }
export function getUpdateMemoryMessages(...): any[] { ... }
export function parseMessages(...): any[] { ... }
export function extractJson(text: string): string { ... }
```

> Prompt 文本和 Python 完全一致（一字不差）——确保跨语言行为一致。

---

## 9. ⭐ Storage（HistoryManager）

```
mem0-ts/src/oss/src/storage/
├── base.ts                    # HistoryManager interface
├── DummyHistoryManager.ts     # 内存版（fallback）
└── SQLiteHistoryManager.ts    # better-sqlite3 实现
```

```typescript
export interface HistoryManager {
  addHistory(...): Promise<void>;
  getHistory(memoryId: string): Promise<MemoryHistory[]>;
  saveMessages(...): Promise<void>;
  getLastMessages(...): Promise<Message[]>;
  reset(): Promise<void>;
  close(): Promise<void>;
}
```

> Python 用 sqlite3 标准库,TS 用 `better-sqlite3`（同步 native binding,比 `sqlite3` 异步包快 10x）。

### 浏览器端 fallback

```typescript
// 浏览器没 SQLite,用 DummyHistoryManager（什么都不存）
if (typeof window !== 'undefined') {
  historyManager = new DummyHistoryManager();
}
```

---

## 10. 一个完整示例

```typescript
import { Memory } from 'mem0ai/oss';

const m = new Memory({
  vector_store: {
    provider: 'qdrant',
    config: {
      host: 'localhost',
      port: 6333,
      collectionName: 'mem0',
      embeddingModelDims: 1536,
    },
  },
  llm: {
    provider: 'openai',
    config: {
      apiKey: process.env.OPENAI_API_KEY!,
      model: 'gpt-5-mini',
    },
  },
  embedder: {
    provider: 'openai',
    config: {
      apiKey: process.env.OPENAI_API_KEY!,
      model: 'text-embedding-3-small',
    },
  },
  history: {
    path: './mem0-history.db',
  },
});

// 跟 Python 几乎一致
await m.add('I prefer dark mode and vim keybindings', { user_id: 'alice' });

const results = await m.search('preferences', { user_id: 'alice' }, 5);
console.log(results);
```

---

## 11. 已知差异 / 局限

| 局限 | 影响 | 计划 |
|------|------|------|
| 没有 graph memory | 跟 Python v1.1+ 一致（都删了） | — |
| NER 用 compromise | entity 抽取精度略低 | 可换 `@tensorflow-models/universal-sentence-encoder` 但更重 |
| Factory 不能运行时注册 | 第三方扩展不便 | 可加 `registerProvider()` API |
| 不支持全部 Python provider | 部分 provider 缺 TS 版 | PR welcome |
| 浏览器端 SQLite 不可用 | 用 DummyHistoryManager fallback | 可用 `absurd-sql` 但稳定性差 |

---

## 12. 接下来

| 想看 | 去哪 |
|------|------|
| Python SDK 详情 | [`../01-py-sdk-core/`](../01-py-sdk-core/) |
| Hosted client | [`01-structure.md`](./01-structure.md) §4 |
| 双模式 | [`../00-overview/05-two-modes.md`](../00-overview/05-two-modes.md) |

---

📌 **下一步** → [`../05-server/`](../05-server/) FastAPI 自托管 server。
