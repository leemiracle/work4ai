<!-- source: DeepWiki mcp.deepwiki.com · repo actionbook/actionbook · page 5 Data Layer · fetched 2026-10-26 -->

# Data Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/db/migrations/0019_add_vector_indexes.sql](services/db/migrations/0019_add_vector_indexes.sql)
- [services/db/migrations/0020_add_chunks_fulltext_index.sql](services/db/migrations/0020_add_chunks_fulltext_index.sql)
- [services/db/src/connection.ts](services/db/src/connection.ts)

</details>



## Purpose and Scope

The Data Layer provides persistent storage for all Actionbook data, including discovered website capabilities, recorded UI elements, crawled documentation, and build pipeline state. This page covers the overall data storage architecture, including the PostgreSQL database, schema organization, version management, and the dual persistence strategy that maintains both structured database records and human-readable YAML files.

For detailed information on specific aspects of the data layer:
- Database schema tables, relationships, and fields: see [Database Schema](#5.1)
- Connection pooling, driver selection, and the `getDb()` singleton: see [Database Connection Management](#5.2)
- Full-text indexes, vector indexes, and hybrid search implementation: see [Search and Indexing](#5.3)

## Storage Architecture

Actionbook uses PostgreSQL as its primary data store with a dual persistence strategy:

| Storage Type | Purpose | Use Cases |
|--------------|---------|-----------|
| **PostgreSQL Database** | Structured querying, search, and transactional operations | API queries, task orchestration, version management, hybrid search |
| **YAML Files** | Human-readable action manuals | Direct file inspection, git version control, offline reference |

The database serves as the source of truth for all structured data, while YAML files in `output/sites/` provide portable, human-readable exports of discovered capabilities.

Sources: [Diagram 5 from architecture overview]

## Database Connection Management

### Connection Strategy

Actionbook uses different PostgreSQL drivers depending on the execution environment:

```mermaid
graph TB
    subgraph "Connection Resolution"
        getDb["getDb()"]
        createDb["createDb()"]
        shouldUsePg["shouldUsePgDriver()"]
    end
    
    subgraph "Environment Detection"
        nodeEnv["NODE_ENV !== 'production'"]
        agentCore["AWS_AGENTCORE_RUNTIME === 'true'"]
        vercel["process.env.VERCEL"]
    end
    
    subgraph "Driver Selection"
        pgDriver["node-postgres (pg)<br/>TCP connection"]
        neonDriver["@neondatabase/serverless<br/>WebSocket connection"]
    end
    
    subgraph "Connection Pools"
        pgPool["Pool<br/>max: 20 (local)<br/>max: 5 (serverless)"]
        neonPool["NeonPool<br/>WebSocket-based"]
    end
    
    subgraph "Drizzle ORM"
        drizzlePg["drizzlePg(pool, schema)"]
        drizzleNeon["drizzleNeon(pool, schema)"]
        dbType["Database<br/>(NodePgDatabase)"]
    end
    
    getDb --> createDb
    createDb --> shouldUsePg
    
    shouldUsePg --> nodeEnv
    shouldUsePg --> agentCore
    shouldUsePg --> vercel
    
    nodeEnv -->|"true"| pgDriver
    agentCore -->|"true"| pgDriver
    vercel -->|"false"| pgDriver
    vercel -->|"true"| neonDriver
    
    pgDriver --> pgPool
    neonDriver --> neonPool
    
    pgPool --> drizzlePg
    neonPool --> drizzleNeon
    
    drizzlePg --> dbType
    drizzleNeon --> dbType
```

Sources: [services/db/src/connection.ts:1-147]()

### Driver Selection Logic

The `shouldUsePgDriver()` function determines which driver to use:

| Condition | Driver Used | Reason |
|-----------|-------------|--------|
| `NODE_ENV !== 'production'` | **node-postgres** | Local development with TCP |
| `AWS_AGENTCORE_RUNTIME === 'true'` | **node-postgres** | Node.js runtime needs TCP, not WebSocket |
| `!process.env.VERCEL` | **node-postgres** | Non-Vercel production environments |
| `process.env.VERCEL` (production) | **Neon serverless** | Vercel edge/serverless with WebSocket support |

Sources: [services/db/src/connection.ts:25-40]()

### Connection Pool Configuration

Connection pool settings are optimized based on the execution environment:

```mermaid
graph LR
    subgraph "Pool Configuration"
        detect["Environment Detection"]
        
        subgraph "Serverless (Vercel/Lambda)"
            sMax["max: 5"]
            sMin["min: 0"]
            sIdle["idleTimeoutMillis: 30000"]
            sExit["allowExitOnIdle: true"]
        end
        
        subgraph "Traditional (Local/Long-running)"
            tMax["max: 20"]
            tMin["min: 2"]
            tIdle["idleTimeoutMillis: 30000"]
            tExit["allowExitOnIdle: false"]
        end
    end
    
    detect -->|"isServerless = true"| sMax
    detect -->|"isServerless = false"| tMax
```

**Key Parameters:**
- **max**: Maximum pool connections (20 for traditional, 5 for serverless)
- **min**: Minimum idle connections (2 for traditional, 0 for serverless)
- **idleTimeoutMillis**: Close idle connections after 30 seconds
- **connectionTimeoutMillis**: Timeout when acquiring connection (5 seconds)
- **allowExitOnIdle**: Allow process exit when no connections (serverless only)

Sources: [services/db/src/connection.ts:77-88]()

### Singleton Pattern

The `getDb()` function provides a singleton database instance:

```mermaid
graph TB
    app1["Service A"]
    app2["Service B"]
    app3["Service C"]
    
    getDb["getDb()"]
    singleton["_db: Database | null"]
    createDb["createDb()"]
    
    app1 --> getDb
    app2 --> getDb
    app3 --> getDb
    
    getDb --> singleton
    singleton -->|"null"| createDb
    singleton -->|"exists"| return["Return existing instance"]
    
    createDb --> pool["Connection Pool"]
    pool --> dbInstance["Database instance"]
```

The singleton pattern ensures all parts of an application share the same connection pool, avoiding connection exhaustion.

Sources: [services/db/src/connection.ts:140-147]()

## Schema Organization

The Actionbook database schema is organized into several logical groups:

```mermaid
graph TB
    subgraph "Source Management"
        sources["sources<br/>Websites tracked"]
        sourceVersions["source_versions<br/>Version snapshots"]
    end
    
    subgraph "Documentation Data"
        documents["documents<br/>Crawled pages"]
        chunks["chunks<br/>Content segments<br/>+ embeddings"]
    end
    
    subgraph "Capability Data"
        pages["pages<br/>Page types/modules"]
        elements["elements<br/>UI components<br/>+ selectors"]
    end
    
    subgraph "Build Pipeline"
        buildTasks["build_tasks<br/>Pipeline tracking"]
        recordingTasks["recording_tasks<br/>Task execution"]
    end
    
    sources --> sourceVersions
    sources --> documents
    sources --> pages
    sources --> buildTasks
    
    sourceVersions --> chunks
    
    documents --> chunks
    
    pages --> elements
    
    buildTasks --> recordingTasks
    
    style sources fill:#f0f0f0
    style chunks fill:#f0f0f0
    style elements fill:#f0f0f0
```

Sources: [Diagram 5 from architecture overview]

### Key Tables Overview

| Table | Primary Purpose | Key Fields |
|-------|----------------|------------|
| `sources` | Website tracking | `id`, `name`, `base_url`, `active_version_id` |
| `source_versions` | Version snapshots | `id`, `source_id`, `version`, `status`, `published_at` |
| `documents` | Crawled pages | `id`, `source_id`, `url`, `title`, `content` |
| `chunks` | Content segments | `id`, `document_id`, `source_version_id`, `content`, `embedding` |
| `pages` | Page types | `id`, `source_id`, `url`, `module`, `capabilities` |
| `elements` | UI capabilities | `id`, `page_id`, `action`, `selectors`, `element_type` |
| `build_tasks` | Build orchestration | `id`, `source_id`, `stage`, `stage_status`, `heartbeat_at` |
| `recording_tasks` | Recording execution | `id`, `build_task_id`, `chunk_id`, `status`, `retry_count` |

For detailed schema definitions, see [Database Schema](#5.1).

## Version Management

Actionbook implements Blue-Green deployment through the version management system:

```mermaid
graph TB
    subgraph "Version Lifecycle"
        create["New Version Created<br/>status = 'pending'"]
        build["Build Process<br/>status = 'building'"]
        complete["Build Complete<br/>status = 'completed'"]
        publish["Publish Version<br/>status = 'published'"]
    end
    
    subgraph "Active Version Tracking"
        sources["sources.active_version_id"]
        oldVersion["Old Version<br/>(unpublished)"]
        newVersion["New Version<br/>(published)"]
    end
    
    subgraph "Data References"
        chunks["chunks.source_version_id"]
        elements["elements<br/>(via pages)"]
    end
    
    create --> build
    build --> complete
    complete --> publish
    
    publish --> sources
    sources --> newVersion
    sources -.->|"previously pointed to"| oldVersion
    
    newVersion --> chunks
    newVersion --> elements
```

**Key Concepts:**

- **source_versions**: Each build creates a new version record with a unique version number
- **active_version_id**: The `sources.active_version_id` field points to the currently published version
- **Publishing**: Atomically switches `active_version_id` to the new version, enabling zero-downtime deployments
- **Rollback**: Simply revert `active_version_id` to a previous version

This design allows multiple versions to coexist in the database while only one is active for API queries.

Sources: [Diagram 5 from architecture overview, section on version management]

## Dual Persistence Strategy

Actionbook maintains data in both PostgreSQL and YAML files:

```mermaid
graph TB
    subgraph "Recording Process"
        recorder["ActionRecorder"]
        tools["RecorderToolExecutor"]
    end
    
    subgraph "Database Persistence"
        saveElement["Save to elements table"]
        savePage["Save to pages table"]
        saveChunk["Update chunks table"]
    end
    
    subgraph "YAML Persistence"
        yamlGen["Generate YAML"]
        yamlPath["output/sites/{source_name}/{page_path}.yaml"]
    end
    
    subgraph "Query Paths"
        apiQuery["API Queries<br/>GET /actions/search"]
        fileRead["Direct File Access"]
    end
    
    recorder --> tools
    tools --> saveElement
    tools --> savePage
    tools --> saveChunk
    
    tools --> yamlGen
    yamlGen --> yamlPath
    
    saveElement --> apiQuery
    savePage --> apiQuery
    saveChunk --> apiQuery
    
    yamlPath --> fileRead
```

### YAML File Structure

YAML files are organized by website and page path:

```
output/
└── sites/
    └── example.com/
        ├── index.yaml
        ├── login.yaml
        ├── dashboard/
        │   └── index.yaml
        └── settings/
            └── profile.yaml
```

Each YAML file contains:
- Page metadata (URL, title, module)
- Element capabilities (actions, selectors, descriptions)
- Human-readable formatting for manual inspection

### Benefits of Dual Persistence

| Aspect | Database | YAML Files |
|--------|----------|------------|
| **Querying** | Fast structured queries, indexes | File system traversal |
| **Search** | Hybrid search (full-text + vector) | Text search tools (grep, ripgrep) |
| **Versioning** | Built-in with `source_versions` | Git-friendly text format |
| **Portability** | Requires database connection | Self-contained files |
| **Human Readability** | Raw SQL/JSON | Formatted, documented |
| **Use Case** | Production API, automated tools | Development, debugging, documentation |

Sources: [Diagram 5 from architecture overview, Diagram 1 showing dual persistence]

## Search Infrastructure

Actionbook implements hybrid search combining full-text and vector similarity:

```mermaid
graph TB
    subgraph "Query Input"
        userQuery["User Query:<br/>'login button'"]
        embedding["Generate Embedding<br/>OpenAI/etc."]
    end
    
    subgraph "Full-Text Search"
        ginIndex["GIN Index<br/>chunks_content_gin_idx"]
        tsVector["to_tsvector('english', content)"]
        ftResults["Full-Text Results<br/>+ ts_rank scores"]
    end
    
    subgraph "Vector Search"
        hnswIndex["HNSW Index<br/>chunks_embedding_hnsw_idx"]
        cosineDist["vector_cosine_ops"]
        vecResults["Vector Results<br/>+ cosine distance"]
    end
    
    subgraph "Result Fusion"
        combine["Combine Results"]
        rerank["Re-rank by Hybrid Score"]
        topK["Return Top-K Results"]
    end
    
    userQuery --> embedding
    userQuery --> tsVector
    
    tsVector --> ginIndex
    ginIndex --> ftResults
    
    embedding --> cosineDist
    cosineDist --> hnswIndex
    hnswIndex --> vecResults
    
    ftResults --> combine
    vecResults --> combine
    combine --> rerank
    rerank --> topK
```

### Index Types

**GIN Index (Generalized Inverted Index)** - Full-Text Search
- Index name: `chunks_content_gin_idx`
- Accelerates `to_tsvector('english', content)` queries
- Improves full-text search from ~2s to ~200ms
- Partial index `chunks_content_gin_active_idx` for active versions only

**HNSW Index (Hierarchical Navigable Small World)** - Vector Similarity
- Index name: `chunks_embedding_hnsw_idx`
- Uses cosine distance (`vector_cosine_ops`)
- Parameters: `m=16`, `ef_construction=64`
- Enables fast approximate nearest neighbor search

Sources: [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19](), [services/db/migrations/0019_add_vector_indexes.sql:1-22]()

### Index Configuration

```mermaid
graph TB
    subgraph "Full-Text Indexes"
        gin1["chunks_content_gin_idx<br/>All chunks"]
        gin2["chunks_content_gin_active_idx<br/>Active versions only"]
    end
    
    subgraph "Vector Indexes"
        hnsw["chunks_embedding_hnsw_idx<br/>m=16, ef_construction=64"]
    end
    
    subgraph "Supporting Indexes"
        docIdx["chunks_document_id_idx<br/>JOIN optimization"]
        verIdx["chunks_source_version_id_idx<br/>Version filtering"]
        compIdx["chunks_version_embedding_idx<br/>Composite filter"]
    end
    
    chunks["chunks table"]
    
    chunks --> gin1
    chunks --> gin2
    chunks --> hnsw
    chunks --> docIdx
    chunks --> verIdx
    chunks --> compIdx
```

**Index Purposes:**

| Index | Purpose | Query Pattern |
|-------|---------|---------------|
| `chunks_content_gin_idx` | Full-text search on all chunks | `to_tsvector('english', content)` |
| `chunks_content_gin_active_idx` | Full-text search on active versions | Same, with `source_version_id IS NOT NULL` |
| `chunks_embedding_hnsw_idx` | Vector similarity search | `ORDER BY embedding <=> query_vector` |
| `chunks_document_id_idx` | JOIN with documents table | `JOIN documents ON chunks.document_id = documents.id` |
| `chunks_source_version_id_idx` | Filter by version | `WHERE source_version_id = ?` |
| `chunks_version_embedding_idx` | Combined version + embedding filter | `WHERE source_version_id = ? AND embedding IS NOT NULL` |

Sources: [services/db/migrations/0020_add_chunks_fulltext_index.sql:1-19](), [services/db/migrations/0019_add_vector_indexes.sql:1-22]()

### Hybrid Search Implementation

The API implements hybrid search by:

1. Executing full-text search with `ts_rank` scoring
2. Executing vector similarity search with cosine distance
3. Normalizing scores from both methods
4. Combining results with configurable weights
5. Re-ranking and returning top-K results

For implementation details, see [Search and Indexing](#5.3).

Sources: [Diagram 5 from architecture overview]

## Data Flow Summary

```mermaid
graph LR
    subgraph "Input Sources"
        crawler["Web Crawler"]
        recorder["Action Recorder"]
        embedder["Embedding Generator"]
    end
    
    subgraph "Database Tables"
        documents["documents"]
        chunks["chunks"]
        pages["pages"]
        elements["elements"]
    end
    
    subgraph "Indexes"
        ginIdx["GIN<br/>Full-text"]
        hnswIdx["HNSW<br/>Vector"]
    end
    
    subgraph "Output"
        api["API Endpoints"]
        yaml["YAML Files"]
    end
    
    crawler --> documents
    crawler --> chunks
    
    recorder --> pages
    recorder --> elements
    recorder --> yaml
    
    embedder --> chunks
    
    chunks --> ginIdx
    chunks --> hnswIdx
    
    ginIdx --> api
    hnswIdx --> api
    elements --> api
```

**Data Flow:**

1. **Web Crawler** (Playbook Builder) discovers pages and generates documentation content
2. **Content** is stored in `documents` and segmented into `chunks`
3. **Embedding Generator** produces vector embeddings for each chunk
4. **Action Recorder** discovers UI capabilities and stores them in `pages` and `elements`
5. **Indexes** (GIN and HNSW) are automatically maintained for fast search
6. **API Endpoints** query indexed data to serve search requests
7. **YAML Files** are generated alongside database records for portability

Sources: [Diagram 5 from architecture overview, Diagram 3 showing build pipeline data flow]

---

