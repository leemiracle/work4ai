<!-- source: DeepWiki mcp.deepwiki.com · repo mastra-ai/mastra · page 7 Memory and Storage Architecture · fetched 2026-10-26 -->

# Memory and Storage Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.changeset/silent-steaks-yell.md](.changeset/silent-steaks-yell.md)
- [docs/src/content/en/docs/memory/message-history.mdx](docs/src/content/en/docs/memory/message-history.mdx)
- [docs/src/content/en/docs/memory/observational-memory.mdx](docs/src/content/en/docs/memory/observational-memory.mdx)
- [docs/src/content/en/docs/memory/overview.mdx](docs/src/content/en/docs/memory/overview.mdx)
- [docs/src/content/en/docs/memory/semantic-recall.mdx](docs/src/content/en/docs/memory/semantic-recall.mdx)
- [docs/src/content/en/reference/memory/memory-class.mdx](docs/src/content/en/reference/memory/memory-class.mdx)
- [docs/src/content/en/reference/memory/observational-memory.mdx](docs/src/content/en/reference/memory/observational-memory.mdx)
- [packages/core/src/loop/test-utils/aimock/scenarios/working-memory-gemini-thought-signature.scenario.test.ts](packages/core/src/loop/test-utils/aimock/scenarios/working-memory-gemini-thought-signature.scenario.test.ts)
- [packages/core/src/memory/memory.ts](packages/core/src/memory/memory.ts)
- [packages/core/src/memory/mock-working-memory-merge.test.ts](packages/core/src/memory/mock-working-memory-merge.test.ts)
- [packages/core/src/memory/mock.ts](packages/core/src/memory/mock.ts)
- [packages/core/src/memory/types.ts](packages/core/src/memory/types.ts)
- [packages/core/src/memory/working-memory-utils.test.ts](packages/core/src/memory/working-memory-utils.test.ts)
- [packages/core/src/memory/working-memory-utils.ts](packages/core/src/memory/working-memory-utils.ts)
- [packages/core/src/processors/memory/message-history.test.ts](packages/core/src/processors/memory/message-history.test.ts)
- [packages/core/src/processors/memory/message-history.ts](packages/core/src/processors/memory/message-history.ts)
- [packages/core/src/storage/domains/memory/base.ts](packages/core/src/storage/domains/memory/base.ts)
- [packages/core/src/storage/domains/memory/inmemory.ts](packages/core/src/storage/domains/memory/inmemory.ts)
- [packages/core/src/storage/types.ts](packages/core/src/storage/types.ts)
- [packages/memory/src/index.test.ts](packages/memory/src/index.test.ts)
- [packages/memory/src/index.ts](packages/memory/src/index.ts)
- [packages/memory/src/processors/observational-memory/__tests__/idle-buffering.test.ts](packages/memory/src/processors/observational-memory/__tests__/idle-buffering.test.ts)
- [packages/memory/src/processors/observational-memory/__tests__/message-utils.test.ts](packages/memory/src/processors/observational-memory/__tests__/message-utils.test.ts)
- [packages/memory/src/processors/observational-memory/__tests__/mid-loop-observation.test.ts](packages/memory/src/processors/observational-memory/__tests__/mid-loop-observation.test.ts)
- [packages/memory/src/processors/observational-memory/__tests__/mock-om-agent.test.ts](packages/memory/src/processors/observational-memory/__tests__/mock-om-agent.test.ts)
- [packages/memory/src/processors/observational-memory/__tests__/observation-groups.test.ts](packages/memory/src/processors/observational-memory/__tests__/observation-groups.test.ts)
- [packages/memory/src/processors/observational-memory/__tests__/observational-memory-api.test.ts](packages/memory/src/processors/observational-memory/__tests__/observational-memory-api.test.ts)
- [packages/memory/src/processors/observational-memory/__tests__/observational-memory.test.ts](packages/memory/src/processors/observational-memory/__tests__/observational-memory.test.ts)
- [packages/memory/src/processors/observational-memory/index.ts](packages/memory/src/processors/observational-memory/index.ts)
- [packages/memory/src/processors/observational-memory/message-utils.ts](packages/memory/src/processors/observational-memory/message-utils.ts)
- [packages/memory/src/processors/observational-memory/observation-groups.ts](packages/memory/src/processors/observational-memory/observation-groups.ts)
- [packages/memory/src/processors/observational-memory/observation-strategies/async-buffer.ts](packages/memory/src/processors/observational-memory/observation-strategies/async-buffer.ts)
- [packages/memory/src/processors/observational-memory/observation-strategies/base.ts](packages/memory/src/processors/observational-memory/observation-strategies/base.ts)
- [packages/memory/src/processors/observational-memory/observation-strategies/resource-scoped.ts](packages/memory/src/processors/observational-memory/observation-strategies/resource-scoped.ts)
- [packages/memory/src/processors/observational-memory/observation-strategies/sync.ts](packages/memory/src/processors/observational-memory/observation-strategies/sync.ts)
- [packages/memory/src/processors/observational-memory/observation-strategies/types.ts](packages/memory/src/processors/observational-memory/observation-strategies/types.ts)
- [packages/memory/src/processors/observational-memory/observation-turn/step.ts](packages/memory/src/processors/observational-memory/observation-turn/step.ts)
- [packages/memory/src/processors/observational-memory/observation-turn/turn.ts](packages/memory/src/processors/observational-memory/observation-turn/turn.ts)
- [packages/memory/src/processors/observational-memory/observational-memory.ts](packages/memory/src/processors/observational-memory/observational-memory.ts)
- [packages/memory/src/processors/observational-memory/observer-agent.ts](packages/memory/src/processors/observational-memory/observer-agent.ts)
- [packages/memory/src/processors/observational-memory/observer-runner.ts](packages/memory/src/processors/observational-memory/observer-runner.ts)
- [packages/memory/src/processors/observational-memory/processor.ts](packages/memory/src/processors/observational-memory/processor.ts)
- [packages/memory/src/processors/observational-memory/reflector-agent.ts](packages/memory/src/processors/observational-memory/reflector-agent.ts)
- [packages/memory/src/processors/observational-memory/reflector-runner.ts](packages/memory/src/processors/observational-memory/reflector-runner.ts)
- [packages/memory/src/processors/observational-memory/types.ts](packages/memory/src/processors/observational-memory/types.ts)
- [packages/memory/src/tools/working-memory.test.ts](packages/memory/src/tools/working-memory.test.ts)
- [packages/memory/src/tools/working-memory.ts](packages/memory/src/tools/working-memory.ts)
- [packages/server/src/server/handlers/memory.test.ts](packages/server/src/server/handlers/memory.test.ts)
- [packages/server/src/server/handlers/memory.ts](packages/server/src/server/handlers/memory.ts)
- [packages/server/src/server/schemas/memory.test.ts](packages/server/src/server/schemas/memory.test.ts)
- [packages/server/src/server/schemas/memory.ts](packages/server/src/server/schemas/memory.ts)
- [stores/dsql/src/storage/domains/memory/index.ts](stores/dsql/src/storage/domains/memory/index.ts)
- [stores/dsql/src/storage/domains/memory/save-timestamps.test.ts](stores/dsql/src/storage/domains/memory/save-timestamps.test.ts)
- [stores/dsql/src/storage/domains/workflows/index.ts](stores/dsql/src/storage/domains/workflows/index.ts)
- [stores/libsql/src/storage/domains/memory/index.ts](stores/libsql/src/storage/domains/memory/index.ts)
- [stores/mongodb/src/storage/domains/memory/index.ts](stores/mongodb/src/storage/domains/memory/index.ts)
- [stores/mssql/src/storage/domains/workflows/index.ts](stores/mssql/src/storage/domains/workflows/index.ts)
- [stores/mysql/src/storage/domains/memory/index.ts](stores/mysql/src/storage/domains/memory/index.ts)
- [stores/oracledb/src/storage/domains/workflows/index.ts](stores/oracledb/src/storage/domains/workflows/index.ts)
- [stores/pg/src/storage/domains/memory/index.ts](stores/pg/src/storage/domains/memory/index.ts)
- [stores/spanner/src/storage/domains/memory/index.ts](stores/spanner/src/storage/domains/memory/index.ts)
- [stores/spanner/src/storage/domains/memory/list-messages-where.test.ts](stores/spanner/src/storage/domains/memory/list-messages-where.test.ts)
- [stores/spanner/src/storage/domains/workflows/index.ts](stores/spanner/src/storage/domains/workflows/index.ts)
- [stores/spanner/src/storage/domains/workflows/update-workflow-state.test.ts](stores/spanner/src/storage/domains/workflows/update-workflow-state.test.ts)

</details>



## Purpose and Scope

This page provides a high-level overview of Mastra's memory and persistence subsystems, which enable agents to maintain contextual awareness, persist conversation history across sessions, execute semantic recall, and integrate with diverse storage adapters, vector stores, and external tools.

The architecture is divided into decoupled layers:
- **Memory Abstraction Layer**: Manages working memory, observational memory, semantic recall, and message history via `MastraMemory` and the user-facing `Memory` class [packages/core/src/memory/memory.ts:114-128](), [packages/memory/src/index.ts:10-10]().
- **Storage Domain Architecture**: Provides pluggable multi-domain persistence through `MastraCompositeStore` and domain-specific interfaces like `MemoryStorage` [packages/core/src/storage/types.ts:20-30]().
- **Vector and Embedding Layer**: Handles embedding generation, vector indexing, and semantic search via `MastraVector` and embedding provider integrations [packages/core/src/memory/memory.ts:170-193]().

For detailed technical specifications, refer to the child pages covering each subsystem.

---

## 7.1 Memory System Architecture

The memory system is built around the abstract base class `MastraMemory` [packages/core/src/memory/memory.ts:114-128]() and implemented concretely by the `Memory` class [packages/memory/src/index.ts:10-10](). It coordinates multiple memory tiers—including raw message history, structured working memory, vector-backed semantic recall, and advanced observational memory—to supply optimal context to agents during execution.

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        UserConversation[""User Conversation & Context""]
    end

    subgraph "CodeEntitySpace"
        Memory_Class[""Memory (@mastra/memory)""] -->|extends| MastraMemory_Abstract[""MastraMemory (@mastra/core/memory)""]
        MastraMemory_Abstract -->|processes via| MessageHistory_Proc[""MessageHistory""]
        MastraMemory_Abstract -->|manages| WorkingMemory_Proc[""WorkingMemory""]
        MastraMemory_Abstract -->|queries| SemanticRecall_Proc[""SemanticRecall""]
        MastraMemory_Abstract -->|integrates| ObservationalMemory_Engine[""ObservationalMemory Engine""]
    end

    UserConversation --> Memory_Class

    classDef code font-family:monospace, font-size:12px;
```

For detailed class designs, configuration options, and memory type breakdowns, see [Memory System Architecture](#7.1).

**Sources**: [packages/core/src/memory/memory.ts:114-128](), [packages/memory/src/index.ts:10-10]()

---

## 7.2 Thread Management and Message Storage

Conversations in Mastra are organized hierarchically into resources (representing users or entities) and threads (representing distinct conversation sessions). Threads store serialized lists of messages (`MastraDBMessage`), support metadata tagging (such as pinned titles), and allow history persistence via the `saveMessages` and `listMessages` flows [packages/core/src/storage/types.ts:132-145](). The `MemoryStorage` interface defines operations for managing threads and messages [packages/core/src/storage/types.ts:20-30]().

For comprehensive details on threads, message lists, cloning, and storage flows, see [Thread Management and Message Storage](#7.2).

**Sources**: [packages/core/src/storage/types.ts:132-145](), [packages/core/src/storage/types.ts:20-30]()

---

## 7.3 Storage Domain Architecture

Mastra decouples persistence concerns using a domain pattern managed by `MastraCompositeStore` [packages/core/src/storage/types.ts:20-30](). Storage domains isolate memory, workflows, observability, and entity data, allowing different backends to power different parts of an application through uniform interfaces like `MemoryStorage`.

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        AppPersistence[""Application Data & Memory Persistence""]
    end

    subgraph "CodeEntitySpace"
        CompositeStore[""MastraCompositeStore (@mastra/core/storage)""] -->|resolves domain| MemoryStorage_Interface[""MemoryStorage interface""]
        MemoryStorage_Interface -->|implemented by| PgMemoryStore[""PgMemoryStore (stores/pg)""]
        MemoryStorage_Interface -->|implemented by| LibSQLMemoryStore[""LibSQLMemoryStore (stores/libsql)""]
        MemoryStorage_Interface -->|implemented by| InMemoryMemoryStore[""InMemoryMemory (packages/core/storage)""]
    end

    AppPersistence --> CompositeStore

    classDef code font-family:monospace, font-size:12px;
```

For complete documentation on the composite store, domain interfaces, and adapter patterns, see [Storage Domain Architecture](#7.3).

**Sources**: [packages/core/src/storage/types.ts:20-30]()

---

## 7.4 PostgreSQL Storage Provider

The `@mastra/pg` package provides a robust PostgreSQL storage adapter that implements `MemoryStorage` and other domain interfaces [stores/pg/src/storage/domains/memory/index.ts:13-30](). It features specialized schema designs optimized for high-throughput message storage, thread metadata indexing, vector similarity support via `pgvector`, and ACID-compliant transaction handling. The `OBSERVATIONAL_MEMORY_TABLE_SCHEMA` is also defined here for OM persistence [stores/pg/src/storage/domains/memory/index.ts:18-18]().

For schema definitions, connection pooling, and Postgres-specific optimizations, see [PostgreSQL Storage Provider](#7.4).

**Sources**: [stores/pg/src/storage/domains/memory/index.ts:13-30](), [stores/pg/src/storage/domains/memory/index.ts:18-18]()

---

## 7.5 LibSQL and Edge Storage

The LibSQL adapter (`@mastra/libsql`) and in-memory storage options provide lightweight, edge-compatible persistence for serverless runtimes, local development, and embedded environments. They implement the full `MemoryStorage` contract while supporting local file URLs and remote LibSQL/Turso instances [stores/libsql/src/storage/domains/memory/index.ts:1-1]().

For details on configuring LibSQL, edge runtimes, and in-memory fallback stores, see [LibSQL and Edge Storage](#7.5).

**Sources**: [stores/libsql/src/storage/domains/memory/index.ts:1-1]()

---

## 7.6 Vector Storage and Semantic Search

Semantic recall allows agents to query historical conversation context based on vector similarity rather than strict chronological windows [packages/core/src/memory/memory.ts:170-193](). The vector subsystem relies on the `MastraVector` interface for upserting and querying embedding vectors generated by configured embedders.

For details on vector indexing, distance metrics, and similarity queries, see [Vector Storage and Semantic Search](#7.6).

**Sources**: [packages/core/src/memory/memory.ts:170-193]()

---

## 7.7 RAG System and Document Processing

The `@mastra/rag` package provides document parsing, chunking strategies, metadata extraction, and vector query tools via `Mdoc` (`MDocument`). It transforms unstructured documents into cleanly chunked and embedded knowledge items consumable by agents and vector stores.

For chunking strategies, parser configurations, and document query tools, see [RAG System and Document Processing](#7.7).

---

## 7.8 Model Context Protocol (MCP) Integration

The `@mastra/mcp` package implements the Model Context Protocol, enabling Mastra agents to discover and execute tools hosted on external MCP servers. It provides client and server abstractions for seamless interoperability with MCP-compliant documentation servers and registries.

For protocol specifications, server configuration, and tool discovery flows, see [Model Context Protocol (MCP) Integration](#7.8).

---

## 7.9 Observational Memory System

Observational Memory (OM) maintains long-term context for agents by employing a three-tier architecture featuring background **Observer** and **Reflector** agents [packages/memory/src/processors/observational-memory/observational-memory.ts:16-33](). OM buffers conversation turns, periodically compresses them into durable observation logs, and manages token budgets dynamically. The `ObservationalMemoryProcessor` integrates OM into the agent's processing pipeline [packages/memory/src/processors/observational-memory/processor.ts:149-166]().

```mermaid
graph TD
    AgentExecution[""Agent Execution Loop""] --> ObservationalMemoryProcessor[""ObservationalMemoryProcessor""]
    ObservationalMemoryProcessor --> OM_Engine[""ObservationalMemory Engine""]

    subgraph "Observational Memory Tiers"
        OM_Engine --> BufferingCoordinator[""BufferingCoordinator""]
        OM_Engine --> ObserverRunner[""ObserverRunner""]
        OM_Engine --> ReflectorRunner[""ReflectorRunner""]
    end

    ObserverRunner --> LLM_Observer[""LLM (Observer Agent)""]
    ReflectorRunner --> LLM_Reflector[""LLM (Reflector Agent)""]
    OM_Engine --> MemoryStorage[""MemoryStorage (for OM records)""]

    classDef code font-family:monospace, font-size:12px;
```

For details on background runners, buffering coordinators, and activation triggers, see [Observational Memory System](#7.9).

**Sources**: [packages/memory/src/processors/observational-memory/observational-memory.ts:16-33](), [packages/memory/src/processors/observational-memory/processor.ts:149-166]()

---

## 7.10 Working Memory and Tool Integration

Working memory provides structured agent state scoped to either resources or threads [packages/core/src/memory/types.ts:180-205](). It supports Markdown template or JSON schema modes and exposes the `updateWorkingMemory` tool, protected by mutex concurrency control, allowing agents to self-update their structured workspace during execution [packages/memory/src/tools/working-memory.ts:69-69](). The `WorkingMemoryExtractor` can be used with Observational Memory to manage working memory state [packages/memory/src/index.ts:78-78]().

For scoping rules, template configuration, and mutex protection mechanisms, see [Working Memory and Tool Integration](#7.10).

**Sources**: [packages/core/src/memory/types.ts:180-205](), [packages/memory/src/tools/working-memory.ts:69-69](), [packages/memory/src/index.ts:78-78]()

---

## 7.11 Extended Storage Providers

In addition to PostgreSQL and LibSQL, Mastra supports a wide array of storage adapters including MongoDB [stores/mongodb/src/storage/domains/memory/index.ts:1-1](), DynamoDB, Upstash, Cloudflare D1, MSSQL, ClickHouse, DuckDB, Redis, Convex, MySQL [stores/mysql/src/storage/domains/memory/index.ts:1-1](), OracleDB, Elasticsearch, Qdrant, Pinecone, Chroma, and others. Each adapter implements domain storage interfaces to fit specialized deployment environments.

For a comprehensive list of extended providers and connection examples, see [Extended Storage Providers](#7.11).

**Sources**: [stores/mongodb/src/storage/domains/memory/index.ts:1-1](), [stores/mysql/src/storage/domains/memory/index.ts:1-1]()

---

## 7.12 Embedders and Embedding Providers (FastEmbed, VoyageAI)

Mastra integrates various embedding provider packages—such as FastEmbed for local ONNX-based vector generation and VoyageAI for hosted semantic models—to power semantic recall, vector stores, and RAG pipelines. The `embedMany` functions from various AI SDK versions are used for embedding generation [packages/memory/src/index.ts:1-5]().

For wiring embedders into memory instances, vector stores, and RAG systems, see [Embedders and Embedding Providers (FastEmbed, VoyageAI)](#7.12).

**Sources**: [packages/memory/src/index.ts:1-5]()

---

