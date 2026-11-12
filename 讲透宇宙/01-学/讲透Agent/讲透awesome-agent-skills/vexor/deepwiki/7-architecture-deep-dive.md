<!-- source: DeepWiki mcp.deepwiki.com · repo scarletkc/vexor · page 7 Architecture Deep Dive · fetched 2026-10-26 -->

# Architecture Deep Dive

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [tests/unit/test_cache.py](tests/unit/test_cache.py)
- [tests/unit/test_search_service.py](tests/unit/test_search_service.py)
- [vexor/cache.py](vexor/cache.py)
- [vexor/services/search_service.py](vexor/services/search_service.py)

</details>



## Purpose and Scope

This document provides detailed technical documentation of Vexor's internal architecture, covering the implementation details of core services, data storage, configuration management, and execution flows. This page is intended for developers who want to understand how Vexor works internally, contribute to the codebase, or debug complex issues.

For user-facing concepts like indexing modes and providers, see [Core Concepts](#3). For API usage patterns, see [Python API Reference](#5). For CLI command details, see [CLI Reference](#4).

---

## System Architecture Overview

```mermaid
graph TB
    subgraph "Entry Points"
        CLI["cli.py<br/>Typer CLI"]
        API["api.py<br/>VexorClient"]
    end
    
    subgraph "Service Layer"
        SearchSvc["search_service.py<br/>perform_search()<br/>search_from_vectors()"]
        IndexSvc["index_service.py<br/>build_index()<br/>build_index_in_memory()"]
    end
    
    subgraph "Core Logic"
        Searcher["search.py<br/>VexorSearcher<br/>embed_texts()"]
        Strategies["modes/<br/>ModeStrategy<br/>payloads_for_files()"]
    end
    
    subgraph "Storage Layer"
        CacheModule["cache.py<br/>store_index()<br/>load_index_vectors()"]
        SQLite["~/.vexor/index.db<br/>index_metadata<br/>indexed_chunk<br/>chunk_embedding"]
        MemCache["_EMBED_MEMORY_CACHE<br/>OrderedDict<br/>LRU 2048 entries"]
    end
    
    subgraph "Configuration"
        ConfigModule["config.py<br/>load_config()<br/>Config dataclass"]
        ConfigFile["~/.vexor/config.json"]
    end
    
    subgraph "External"
        Providers["OpenAI/Gemini/Voyage/Local"]
        Rerankers["BM25/FlashRank/Remote"]
    end
    
    CLI --> SearchSvc
    CLI --> IndexSvc
    API --> SearchSvc
    API --> IndexSvc
    
    SearchSvc --> CacheModule
    SearchSvc --> Searcher
    IndexSvc --> CacheModule
    IndexSvc --> Strategies
    IndexSvc --> Searcher
    
    Searcher --> Providers
    SearchSvc --> Rerankers
    
    CacheModule --> SQLite
    CacheModule --> MemCache
    
    ConfigModule --> ConfigFile
    SearchSvc --> ConfigModule
    IndexSvc --> ConfigModule
```

**Sources:** [vexor/services/search_service.py:1-842](), [vexor/services/index_service.py:1-1049](), [vexor/cache.py:1-1533](), [vexor/config.py:1-710]()

---

## Core Components

### Service Layer

The service layer implements the two primary workflows: indexing and search. Both services are stateless and coordinate between configuration, storage, and external providers.

| Component | Responsibilities | Key Functions |
|-----------|-----------------|---------------|
| `search_service.py` | Query execution, cache checking, reranking | `perform_search()`, `search_from_vectors()` |
| `index_service.py` | File discovery, content extraction, index building | `build_index()`, `build_index_in_memory()` |
| `cache_service.py` | Cache validation, staleness detection | `is_cache_current()`, `load_index_metadata_safe()` |

**Sources:** [vexor/services/search_service.py:358-708](), [vexor/services/index_service.py:126-375]()

### Request/Response Pattern

Both services use dataclass-based request/response objects for explicit parameter passing:

```mermaid
classDiagram
    class SearchRequest {
        +str query
        +Path directory
        +str mode
        +int top_k
        +str provider
        +str rerank
        +bool auto_index
    }
    
    class SearchResponse {
        +Path base_path
        +Sequence results
        +bool is_stale
        +str reranker
    }
    
    class IndexResult {
        +IndexStatus status
        +Path cache_path
        +int files_indexed
    }
    
    SearchRequest --> perform_search
    perform_search --> SearchResponse
    build_index --> IndexResult
```

**Sources:** [vexor/services/search_service.py:33-70](), [vexor/services/index_service.py:34-44]()

---

## Storage Architecture

### SQLite Schema

Vexor uses a normalized SQLite schema with foreign key cascades for referential integrity:

```mermaid
erDiagram
    index_metadata ||--o{ indexed_file : "has"
    index_metadata ||--o{ indexed_chunk : "has"
    index_metadata ||--o{ query_cache : "has"
    indexed_file ||--o{ indexed_chunk : "contains"
    indexed_chunk ||--|| chunk_embedding : "has"
    indexed_chunk ||--|| chunk_meta : "has"
    
    index_metadata {
        int id PK
        text cache_key
        text root_path
        text model
        int dimension
        text extensions
        text exclude_patterns
    }
    
    indexed_file {
        int id PK
        int index_id FK
        text rel_path
        real mtime
        int size_bytes
    }
    
    indexed_chunk {
        int id PK
        int index_id FK
        int file_id FK
        int chunk_index
        int position
    }
    
    chunk_embedding {
        int chunk_id PK_FK
        blob vector_blob
    }
    
    chunk_meta {
        int chunk_id PK_FK
        text preview
        text label_hash
        int start_line
        int end_line
    }
    
    query_cache {
        int id PK
        int index_id FK
        text query_hash
        blob query_vector
    }
```

**Sources:** [vexor/cache.py:314-399]()

### Cache Key Generation

Cache keys uniquely identify indices based on configuration:

```python
# Pseudocode from _cache_key()
key = f"{root.resolve()}|hidden={include_hidden}|gitignore={respect_gitignore}"
      f"|recursive={recursive}|mode={mode}|ext={extensions}|exclude={patterns}"
digest = sha1(key.encode("utf-8")).hexdigest()
```

**Sources:** [vexor/cache.py:51-71]()

### Two-Tier Cache System

Vexor implements a two-tier caching strategy for embeddings:

| Tier | Implementation | Size Limit | Eviction |
|------|---------------|------------|----------|
| Memory | `_EMBED_MEMORY_CACHE` OrderedDict | 2048 entries | LRU |
| Disk | `embedding_cache` SQLite table | 50,000 entries | TTL (30 days) + capacity |

The memory cache is dimension-aware to prevent cross-dimension pollution:

```python
# Cache key includes dimension
key = (model, dimension, text_hash)
```

**Sources:** [vexor/cache.py:33-159](), [vexor/cache.py:728-777]()

---

## Search Execution Flow

```mermaid
sequenceDiagram
    participant Client
    participant perform_search
    participant Cache as load_index_vectors
    participant build_index
    participant VexorSearcher
    participant Reranker
    
    Client->>perform_search: SearchRequest
    perform_search->>Cache: load vectors
    
    alt Index Missing
        Cache-->>perform_search: FileNotFoundError
        perform_search->>build_index: auto_index=True
        build_index-->>perform_search: IndexResult
        perform_search->>Cache: load vectors (retry)
    else Index Stale
        Cache-->>perform_search: old metadata
        perform_search->>build_index: incremental update
    end
    
    Cache-->>perform_search: paths, vectors, metadata
    
    perform_search->>perform_search: check query_cache
    
    alt Query Cache Miss
        perform_search->>VexorSearcher: embed_texts([query])
        VexorSearcher-->>perform_search: query_vector
        perform_search->>Cache: store_query_vector
    end
    
    perform_search->>perform_search: cosine_similarity(vectors @ query)
    perform_search->>perform_search: top_k candidates
    
    alt Reranking Enabled
        perform_search->>Reranker: rerank(candidates)
        Reranker-->>perform_search: reordered results
    end
    
    perform_search-->>Client: SearchResponse
```

**Sources:** [vexor/services/search_service.py:358-708]()

### Cache Lookup Strategy

The search service implements a sophisticated cache lookup strategy with superset fallback:

1. **Exact Match**: Try loading with exact parameters
2. **Superset Search**: If not found, search for a compatible parent index
3. **Filter In-Memory**: Apply extension/directory filters to superset
4. **Auto-Index**: Optionally rebuild if stale or missing

The superset selection algorithm prioritizes:
- Same root or parent directory (minimum distance)
- Recursive flag compatibility
- Extension superset matching
- Exclude pattern subset matching

**Sources:** [vexor/services/search_service.py:876-1020]()

---

## Index Building Pipeline

```mermaid
flowchart TD
    Start["build_index()"] --> Collect["collect_files()<br/>respect gitignore/patterns"]
    Collect --> CheckCache["load_index_metadata_safe()"]
    
    CheckCache --> Diff{Compare<br/>Cached Files}
    
    Diff -->|Up to Date| UpToDate["IndexStatus.UP_TO_DATE"]
    Diff -->|< 50% Changed| Incremental["Incremental Update Path"]
    Diff -->|≥ 50% Changed| Full["Full Rebuild Path"]
    
    Full --> Extract["_payloads_for_files()<br/>ThreadPool/ProcessPool"]
    Extract --> Embed["_embed_labels_with_cache()<br/>batch embedding"]
    Embed --> Store["store_index()<br/>SQLite transaction"]
    
    Incremental --> DiffFiles["Identify added/modified/removed"]
    DiffFiles --> ExtractChanged["Extract changed files only"]
    ExtractChanged --> LabelMatch{Label Hash<br/>Match?}
    LabelMatch -->|Yes| Touch["Update mtime only"]
    LabelMatch -->|No| ReEmbed["Re-embed chunks"]
    ReEmbed --> Apply["apply_index_updates()"]
    Touch --> Apply
    
    Store --> Return["IndexResult"]
    Apply --> Return
    UpToDate --> Return
```

**Sources:** [vexor/services/index_service.py:126-375](), [vexor/services/index_service.py:641-726]()

### Incremental Update Optimization

The incremental update path avoids re-embedding unchanged content by comparing label hashes:

```python
# From _split_payloads_by_label()
for payload in payloads:
    cached_hash = cached_chunks.get(payload.chunk_index)
    new_hash = embedding_cache_key(payload.label)
    if cached_hash == new_hash:
        to_touch.append(payload)  # Only update metadata
    else:
        to_embed.append(payload)  # Re-embed
```

**Sources:** [vexor/services/index_service.py:830-863]()

---

## Configuration Resolution

### Five-Layer Hierarchy

Vexor resolves configuration through a strict precedence system:

```mermaid
flowchart TD
    Request["1. Explicit Function Args<br/>(highest priority)"] --> Runtime["2. Runtime Config Override<br/>set_config_json()"]
    Runtime --> File["3. Config File<br/>~/.vexor/config.json"]
    File --> Env["4. Environment Variables<br/>VEXOR_API_KEY, etc."]
    Env --> Defaults["5. Built-in Defaults<br/>(lowest priority)"]
    
    Defaults --> Result["Effective Config"]
```

**Sources:** [vexor/config.py:123-149](), [vexor/config.py:469-504]()

### Provider-Specific Resolution

Different providers use different environment variables:

| Provider | Config Key | Env Fallback | Default Model |
|----------|-----------|--------------|---------------|
| `openai` | `api_key` | `OPENAI_API_KEY` | `text-embedding-3-small` |
| `gemini` | `api_key` | `GOOGLE_GENAI_API_KEY` | `gemini-embedding-001` |
| `voyageai` | `api_key` | `VOYAGE_API_KEY` | `voyage-3-large` |
| `local` | None | None | `intfloat/multilingual-e5-small` |

**Sources:** [vexor/config.py:397-407](), [vexor/config.py:469-493]()

---

## Reranking Architecture

### Reranking Pipeline

When reranking is enabled, the search service retrieves more candidates than requested and reranks them:

```python
# From perform_search()
if use_rerank:
    candidate_limit = _resolve_rerank_candidates(top_k)  # 2x, min 20, max 150
else:
    candidate_limit = top_k

# After cosine similarity
if rerank == "bm25":
    candidates = _apply_bm25_rerank(query, candidates)
elif rerank == "flashrank":
    candidates = _apply_flashrank_rerank(query, candidates)
else:  # remote
    candidates = _apply_remote_rerank(query, candidates)

results = candidates[:top_k]
```

**Sources:** [vexor/services/search_service.py:624-700]()

### BM25 Score Fusion

The BM25 reranker fuses lexical and semantic scores:

```python
# Normalize both score types
semantic_norm = normalize_by_max(semantic_scores)
bm25_norm = normalize_by_max(bm25_scores)

# Weighted fusion (70% semantic, 30% lexical)
fused_score = 0.7 * semantic_norm + 0.3 * bm25_norm
```

**Sources:** [vexor/services/search_service.py:144-163]()

---

## Embedding Dimension Management

### Dimension Validation

Vexor validates embedding dimensions at multiple points to prevent mismatches:

```mermaid
flowchart LR
    A["User sets<br/>embedding_dimensions"] --> B["validate_embedding_dimensions_for_model()"]
    B --> C{Model<br/>Supports?}
    C -->|No| Error1["ValueError:<br/>Model doesn't support dimensions"]
    C -->|Yes| D{Value in<br/>Supported List?}
    D -->|No| Error2["ValueError:<br/>Dimension not supported"]
    D -->|Yes| E["Store in Config"]
    
    E --> F["build_index()"]
    F --> G["Embed with dimension"]
    G --> H["Store in SQLite"]
    H --> I["dimension column"]
    
    I --> J["perform_search()"]
    J --> K["Load index"]
    K --> L{Index dimension<br/>== Query dimension?}
    L -->|No| Error3["ValueError:<br/>Dimension mismatch"]
    L -->|Yes| M["Compute similarity"]
```

**Sources:** [vexor/config.py:434-467](), [vexor/services/search_service.py:635-644]()

### Cache Segmentation

Embedding caches are segmented by dimension to prevent cross-pollution:

```python
# Cache key includes dimension
text_hash = embedding_cache_key(text, dimension=512)

# Memory cache key
key = (model, dimension, text_hash)

# Different dimensions = different cache entries
cache_key("hello", dim=512) != cache_key("hello", dim=1024)
```

**Sources:** [vexor/cache.py:92-106](), [vexor/cache.py:137-159]()

---

## Concurrency and Parallelism

### Content Extraction Backend

The index service supports three extraction backends:

| Backend | Implementation | Use Case |
|---------|---------------|----------|
| `thread` | `ThreadPoolExecutor` | I/O-bound, small files |
| `process` | `ProcessPoolExecutor` | CPU-bound, large files |
| `auto` | Automatic selection | ≥16 files + CPU-heavy mode → process |

**Sources:** [vexor/services/index_service.py:51-123]()

### Extraction Backend Selection Logic

```python
def _resolve_extract_backend(value, *, mode, file_count, concurrency):
    if value == "auto":
        if (concurrency > 1 and 
            file_count >= 16 and 
            mode in {"auto", "code", "outline", "full"}):
            return "process"
        return "thread"
    return value
```

**Sources:** [vexor/services/index_service.py:51-69]()

---

## Error Handling and Edge Cases

### Dimension Mismatch Detection

The search service validates dimension compatibility before computing similarities:

```python
# From perform_search()
index_dimension = file_vectors.shape[1]
query_dimension = query_vector.shape[0]

if index_dimension != query_dimension:
    raise ValueError(
        f"Embedding dimension mismatch: index has {index_dimension}-dim vectors, "
        f"but query embedding is {query_dimension}-dim. "
        "Rebuild the index with: vexor index {directory}"
    )
```

**Sources:** [vexor/services/search_service.py:635-644](), [tests/unit/test_search_service.py:995-1046]()

### Staleness Detection

Cache staleness is detected by comparing file metadata:

```python
# From _has_entry_changed()
if abs(entry.mtime - cached_mtime) > MTIME_TOLERANCE:
    if cached_size == entry.size:
        return False  # Size match, likely same content
    return True

if cached_size != entry.size:
    return True
```

**Sources:** [vexor/services/index_service.py:627-638]()

---

## Summary of Key Patterns

| Pattern | Implementation | Purpose |
|---------|---------------|---------|
| Two-tier caching | Memory LRU + SQLite | Balance speed and durability |
| Incremental updates | Label hash comparison | Avoid redundant re-embedding |
| Superset fallback | Parent index reuse | Reduce redundant indexing |
| Dimension segmentation | Dimension-aware cache keys | Prevent cross-dimension pollution |
| Request/Response objects | Dataclasses | Explicit parameter passing |
| Provider abstraction | `VexorSearcher` | Unified embedding interface |
| Foreign key cascades | SQLite constraints | Automatic cleanup on deletion |

**Sources:** [vexor/cache.py:1-1533](), [vexor/services/search_service.py:1-842](), [vexor/services/index_service.py:1-1049]()

---

