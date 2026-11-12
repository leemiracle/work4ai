<!-- source: DeepWiki mcp.deepwiki.com · repo supermemoryai/supermemory · page 8 SDKs & Client Libraries · fetched 2026-10-30 -->

# SDKs & Client Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/memory-api/sdks/native.mdx](apps/docs/memory-api/sdks/native.mdx)
- [apps/docs/memory-api/sdks/python.mdx](apps/docs/memory-api/sdks/python.mdx)
- [apps/docs/memory-api/sdks/typescript.mdx](apps/docs/memory-api/sdks/typescript.mdx)
- [packages/tools/README.md](packages/tools/README.md)
- [packages/tools/package.json](packages/tools/package.json)
- [packages/tools/src/vercel/index.ts](packages/tools/src/vercel/index.ts)
- [packages/tools/src/vercel/memory-prompt.ts](packages/tools/src/vercel/memory-prompt.ts)
- [packages/tools/src/vercel/middleware.ts](packages/tools/src/vercel/middleware.ts)
- [packages/tools/src/vercel/util.ts](packages/tools/src/vercel/util.ts)

</details>



This document provides a high-level overview of the official Supermemory SDKs available for TypeScript/JavaScript and Python, as well as specialized integration libraries for AI frameworks. These SDKs wrap the Supermemory REST API to provide idiomatic, type-safe interfaces for managing memories, documents, and user profiles.

For deep technical details on specific methods, refer to the child pages:
- [TypeScript/JavaScript SDK](#8.1) — Installation and core methods for web/Node.js.
- [Python SDK](#8.2) — Installation and method parity for Python environments.
- [Migration from Mem0](#8.3) — Transitioning from Mem0 to Supermemory.
- [Agent Framework Integrations](#8.4) — Middleware for Vercel AI SDK, Mastra, and Pipecat.
- [Memory Router & Model Enhancement](#8.5) — Transparent proxying via `api.supermemory.ai/v3/`.
- [LangChain, LangGraph & Multi-Agent Frameworks](#8.6) — Injecting context into complex agent pipelines.
- [Automation & No-Code Integrations](#8.7) — n8n, Zapier, and ViaSocket support.
- [Voice & Cartesia Integration](#8.8) — Real-time memory for voice agents.

---

## SDK Architecture

The official SDKs bridge the gap between your application code and the Supermemory backend. They handle authentication via API keys, request formatting, and response parsing.

### System Flow: SDK to Backend
This diagram maps the SDK methods to the corresponding backend API entities and endpoints.

```mermaid
graph TD
    subgraph "Application Code"
        [App_Logic]
    end

    subgraph "Supermemory SDKs"
        [supermemory_NPM]
        [supermemory_PyPI]
    end

    subgraph "Backend API (api.supermemory.ai)"
        [POST_v3_add]
        [POST_v4_profile]
        [POST_v3_search]
        [GET_v3_documents_list]
    end

    [App_Logic] -->|"client.add()"| [supermemory_NPM]
    [App_Logic] -->|"client.add()"| [supermemory_PyPI]
    [App_Logic] -->|"client.search.execute()"| [supermemory_NPM]
    [App_Logic] -->|"client.search.execute()"| [supermemory_PyPI]

    [supermemory_NPM] --> [POST_v3_add]
    [supermemory_NPM] --> [POST_v4_profile]
    [supermemory_PyPI] --> [POST_v3_add]
    [supermemory_PyPI] --> [POST_v4_profile]
    
    subgraph "AI Tools Package (@supermemory/tools)"
        [searchMemoriesTool]
        [addMemoryTool]
        [withSupermemory]
    end

    [searchMemoriesTool] --> [POST_v3_search]
    [addMemoryTool] --> [POST_v3_add]
    [withSupermemory] --> [POST_v4_profile]

    style [supermemory_NPM] stroke-width:2px
    style [supermemory_PyPI] stroke-width:2px
```
Sources: [apps/docs/memory-api/sdks/typescript.mdx:18-29](), [apps/docs/memory-api/sdks/python.mdx:21-29](), [packages/tools/src/vercel/index.ts:111-140]()

---

## Available SDKs

### TypeScript/JavaScript SDK
The TypeScript SDK is the primary library for web and Node.js applications. It provides full type safety and is used for both browser extensions and server-side integrations.

**Key Features:**
- **Client Initialization**: Uses `new Supermemory({ apiKey })` [apps/docs/memory-api/sdks/typescript.mdx:18-20]().
- **Core Methods**: Includes `client.add` for storing content, `client.search.execute` for retrieval, and `client.documents.uploadFile` for binary data [apps/docs/memory-api/sdks/typescript.mdx:43-48](), [apps/docs/memory-api/sdks/typescript.mdx:71-82]().
- **Error Handling**: Uses a subclass of `APIError` for 4xx/5xx responses [apps/docs/memory-api/sdks/typescript.mdx:95-103]().

For details, see [TypeScript/JavaScript SDK](#8.1).

### Python SDK
The Python SDK offers parity with the TypeScript version, allowing Python developers to integrate Supermemory into AI agents, data pipelines, and frameworks.

**Key Features:**
- **Installation**: Available via `pip install --pre supermemory` [apps/docs/memory-api/sdks/python.mdx:11]().
- **Async Support**: Includes `AsyncSupermemory` for non-blocking I/O [apps/docs/memory-api/sdks/python.mdx:43-47]().
- **Type Safety**: Uses Pydantic models for responses and TypedDicts for request parameters [apps/docs/memory-api/sdks/python.mdx:64-67]().

For details, see [Python SDK](#8.2).

---

## Framework Integrations

The `@supermemory/tools` package provides specialized middleware and function-calling tools for modern AI frameworks.

### Tool-Calling & Middleware Flow
This diagram shows how the `withSupermemory` middleware intercepts model calls to inject context.

```mermaid
graph LR
    subgraph "AI Framework (e.g. Vercel AI SDK)"
        [generateText]
    end

    subgraph "Supermemory Middleware"
        [withSupermemory]
        [transformParamsWithMemory]
        [saveMemoryAfterResponse]
    end

    [generateText] -->|"intercepts"| [withSupermemory]
    [withSupermemory] -->|"calls"| [transformParamsWithMemory]
    [transformParamsWithMemory] -->|"injects context"| [LLM_Provider]
    [LLM_Provider] -->|"response"| [saveMemoryAfterResponse]
```
Sources: [packages/tools/src/vercel/index.ts:146-187](), [packages/tools/src/vercel/middleware.ts:232-265]()

**Supported Submodules:**
- `@supermemory/tools/ai-sdk`: For Vercel AI SDK, featuring `withSupermemory` and `supermemoryTools` [packages/tools/README.md:20-23]().
- `@supermemory/tools/openai`: For OpenAI SDK integration [packages/tools/README.md:17]().
- `@supermemory/tools/mastra`: For Mastra AI agents [packages/tools/README.md:18]().
- `@supermemory/tools/voltagent`: For VoltAgent configurations [packages/tools/package.json:55]().

---

## Summary Table

| Library | Platform | Exports / Submodules |
| :--- | :--- | :--- |
| `supermemory` | TS/JS | Core client, `toFile` helper [apps/docs/memory-api/sdks/typescript.mdx:66-68]() |
| `supermemory` | Python | `Supermemory`, `AsyncSupermemory` [apps/docs/memory-api/sdks/python.mdx:19-45]() |
| `@supermemory/tools` | TS/JS | `/ai-sdk`, `/openai`, `/mastra`, `/voltagent`, `/claude-memory` [packages/tools/package.json:49-57]() |
| `supermemory-pipecat` | Python | Pipecat voice agent service |
| `supermemory-cartesia` | Python | Cartesia voice model integration |

Sources: [packages/tools/package.json:49-57](), [apps/docs/memory-api/sdks/typescript.mdx:16-18](), [apps/docs/memory-api/sdks/python.mdx:19-45]()

---

