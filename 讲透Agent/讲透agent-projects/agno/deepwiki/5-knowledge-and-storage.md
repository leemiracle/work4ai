<!-- source: DeepWiki mcp.deepwiki.com · repo agno-agi/agno · page 5 Knowledge and Storage · fetched 2026-11-09 -->

# Knowledge and Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cookbook/07_knowledge/01_getting_started/05_website_per_page.py](cookbook/07_knowledge/01_getting_started/05_website_per_page.py)
- [cookbook/91_tools/knowledge_management_tools.py](cookbook/91_tools/knowledge_management_tools.py)
- [libs/agno/agno/context/backend.py](libs/agno/agno/context/backend.py)
- [libs/agno/agno/context/web/parallel.py](libs/agno/agno/context/web/parallel.py)
- [libs/agno/agno/knowledge/knowledge.py](libs/agno/agno/knowledge/knowledge.py)
- [libs/agno/agno/knowledge/reader/page_fetcher.py](libs/agno/agno/knowledge/reader/page_fetcher.py)
- [libs/agno/agno/knowledge/reader/sitemap_reader.py](libs/agno/agno/knowledge/reader/sitemap_reader.py)
- [libs/agno/agno/knowledge/reader/utils/urls.py](libs/agno/agno/knowledge/reader/utils/urls.py)
- [libs/agno/agno/os/routers/knowledge/knowledge.py](libs/agno/agno/os/routers/knowledge/knowledge.py)
- [libs/agno/tests/unit/knowledge/test_folder_content_rows.py](libs/agno/tests/unit/knowledge/test_folder_content_rows.py)
- [libs/agno/tests/unit/knowledge/test_knowledge_content_hash.py](libs/agno/tests/unit/knowledge/test_knowledge_content_hash.py)
- [libs/agno/tests/unit/knowledge/test_knowledge_encoding.py](libs/agno/tests/unit/knowledge/test_knowledge_encoding.py)
- [libs/agno/tests/unit/knowledge/test_knowledge_readers.py](libs/agno/tests/unit/knowledge/test_knowledge_readers.py)
- [libs/agno/tests/unit/knowledge/test_per_page_content_rows.py](libs/agno/tests/unit/knowledge/test_per_page_content_rows.py)
- [libs/agno/tests/unit/os/routers/test_knowledge_upload_chunker.py](libs/agno/tests/unit/os/routers/test_knowledge_upload_chunker.py)
- [libs/agno/tests/unit/os/test_knowledge_upload_validation.py](libs/agno/tests/unit/os/test_knowledge_upload_validation.py)
- [libs/agno/tests/unit/os/test_knowledge_url_input.py](libs/agno/tests/unit/os/test_knowledge_url_input.py)
- [libs/agno/tests/unit/reader/test_page_fetcher.py](libs/agno/tests/unit/reader/test_page_fetcher.py)
- [libs/agno/tests/unit/reader/test_sitemap_reader.py](libs/agno/tests/unit/reader/test_sitemap_reader.py)
- [libs/agno/tests/unit/tools/test_knowledge_management_tools.py](libs/agno/tests/unit/tools/test_knowledge_management_tools.py)

</details>



This page introduces Agno's knowledge management system (RAG) and multi-database persistence architecture. The knowledge system enables document ingestion, vector search, remote content loading, and document-to-vector transformation, allowing agents to ground their responses in factual data. The persistence layer abstracts a variety of relational and NoSQL databases to store sessions, runs, user memories, knowledge metadata, and execution traces.

For deep technical details, see the following child pages:
- [Knowledge Base and Agentic RAG](#5.1)
- [Vector Database Integrations](#5.2)
- [Search Types and Strategies](#5.3)
- [Database Backends](#5.4)
- [Session Storage and Schema](#5.5)

---

## 5.1 Knowledge Base and Agentic RAG

The `Knowledge` class acts as the central interface for managing document ingestion, chunking, embedding, and retrieval [libs/agno/agno/knowledge/knowledge.py:70-150](). It coordinates between two distinct storage engines: `contents_db` for metadata and status tracking, and `vector_db` for semantic similarity search [libs/agno/agno/knowledge/knowledge.py:91-92](). 

Key capabilities include format-aware document parsing via pluggable readers [libs/agno/agno/knowledge/knowledge.py:94](), semantic or recursive chunking strategies, remote content synchronization from sources like S3 or GitHub [libs/agno/agno/knowledge/knowledge.py:95](), and vector search isolation via `isolate_vector_search` [libs/agno/agno/knowledge/knowledge.py:100](). Additionally, the page subsystem supports transactional catalog publication and a shell-like page filesystem for markdown documentation corpora.

For complete documentation on insert/search methods, content processing pipelines, and agent integration, see [Knowledge Base and Agentic RAG](#5.1).

Sources: [libs/agno/agno/knowledge/knowledge.py:70-150]()

---

## 5.2 Vector Database Integrations

Agno unifies vector database interactions under the `VectorDb` interface, allowing developers to switch seamlessly between local vector stores and distributed cloud databases. The framework supports over 11 vector database implementations, providing a consistent API for inserting document chunks, managing collections, and executing vector searches.

Supported integrations include PgVector, LanceDB, ChromaDB, Milvus, Qdrant, Pinecone, Couchbase, Redis, and Weaviate. Each backend maps Agno's high-level vector operations into native provider queries while handling metadata filters and indexing options (such as HNSW or Ivfflat).

For details on configuration parameters and unified insertion/search APIs, see [Vector Database Integrations](#5.2).

Sources: [libs/agno/agno/knowledge/knowledge.py:91-92]()

---

## 5.3 Search Types and Strategies

Retrieval quality in Agno is governed by flexible search types and ranking mechanisms. The framework supports `SearchType.vector`, `SearchType.keyword`, and `SearchType.hybrid` modes, combining dense vector embeddings with sparse keyword matches using Reciprocal Rank Fusion (RRF).

To refine retrieval pools before feeding them to models, Agno supports pluggable rerankers (such as MMR, recency-based, or model-based rerankers) configured directly on the `Knowledge` instance rather than restricted by vector database adapters [libs/agno/agno/knowledge/knowledge.py:117-118](). Similarity score normalization ensures consistent thresholds across heterogeneous search results.

For implementation details on hybrid search, RRF algorithms, and reranking strategies, see [Search Types and Strategies](#5.3).

Sources: [libs/agno/agno/knowledge/knowledge.py:113-118]()

---

## 5.4 Database Backends

Agno provides a comprehensive multi-database storage architecture built on top of `BaseDb` and `AsyncBaseDb` interfaces [libs/agno/agno/db/base.py:31](). These adapters abstract schema management, connection pooling, and CRUD operations across 9+ database backends, including relational databases (PostgreSQL, SQLite, MySQL, SingleStore) and NoSQL/document stores (MongoDB, Redis, DynamoDB, Firestore).

Each database backend manages a standardized set of tables or collections—such as sessions, runs, memories, metrics, evaluations, traces, and knowledge metadata—ensuring consistent application state across deployments.

Title: Database Abstraction and Backend Hierarchy
```mermaid
graph TB
    subgraph "Database Abstraction Layer"
        BaseDb[""BaseDb [agno/db/base.py]""]
        AsyncBaseDb[""AsyncBaseDb [agno/db/base.py]""]
    end

    subgraph "SQL Backends"
        SqliteDb[""SqliteDb [agno/db/sqlite/sqlite.py]""]
        PostgresDb[""PostgresDb [agno/db/postgres/postgres.py]""]
        MySQLDb[""MySQLDb [agno/db/mysql/mysql.py]""]
        SingleStoreDb[""SingleStoreDb [agno/db/singlestore/singlestore.py]""]
    end

    subgraph "NoSQL Backends"
        MongoDb[""MongoDb [agno/db/mongo/mongo.py]""]
        FirestoreDb[""FirestoreDb [agno/db/firestore/firestore.py]""]
    end

    BaseDb --> SqliteDb
    BaseDb --> PostgresDb
    BaseDb --> MySQLDb
    BaseDb --> SingleStoreDb
    BaseDb --> MongoDb
    BaseDb --> FirestoreDb
```

For complete integration guides, connection string formats, and table configuration, see [Database Backends](#5.4).

Sources: [libs/agno/agno/db/base.py:31]()

---

## 5.5 Session Storage and Schema

Agent execution state, conversation history, and user memories are persisted via session management APIs. Sessions are categorized into session types and are stored alongside run outputs in dedicated database tables.

The storage layer handles schema versioning and automated migrations, supporting pagination, user-scoped queries, and high-performance CRUD operations across all supported database backends.

For detailed schema definitions, migration flows, and session persistence patterns, see [Session Storage and Schema](#5.5).

Sources: [libs/agno/agno/db/base.py:31]()

---

## Diagrams: Natural Language to Code Entity Space

Title: Natural Language Search to Knowledge Retrieval Path
```mermaid
graph TD
    NL[""Natural Language Query: 'Find system architecture details'""] --> Agent[""Agent.run() [agno/agent/agent.py]""]
    Agent --> KnowledgeSearch[""Knowledge.search() [agno/knowledge/knowledge.py]""]
    KnowledgeSearch --> VectorAdapter[""VectorDb.search() [agno/vectordb/base.py]""]
    VectorAdapter --> SqlStore[""PostgresDb / SqliteDb [agno/db/postgres/postgres.py]""]
```
Sources: [libs/agno/agno/knowledge/knowledge.py:70-150](), [libs/agno/agno/db/base.py:31]()

Title: Session State Persistence Architecture
```mermaid
graph TB
    RunOutput[""RunOutput Object [agno/run/agent.py]""] --> SessionMgr[""BaseDb.upsert_session() [agno/db/base.py]""]
    SessionMgr --> SqliteTarget[""SqliteDb [agno/db/sqlite/sqlite.py]""]
    SessionMgr --> PostgresTarget[""PostgresDb [agno/db/postgres/postgres.py]""]
    SessionMgr --> MongoTarget[""MongoDb [agno/db/mongo/mongo.py]""]
```
Sources: [libs/agno/agno/db/base.py:31]()

---

