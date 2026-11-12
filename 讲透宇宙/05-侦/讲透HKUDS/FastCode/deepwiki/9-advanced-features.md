<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/FastCode · page 9 Advanced Features · fetched 2026-11-09 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This page is an index for FastCode capabilities that extend beyond basic single-repository indexing and querying. Each section introduces a feature area and directs you to the detailed sub-page.

The features covered here operate across the pipeline: from how retrieval candidates are selected ([Two-Stage Retrieval](#9.5)), to how context is pruned before reaching the LLM ([Code Skimming](#9.4)), to how results and sessions are persisted across requests ([Caching System](#9.1), [Multi-Turn Dialogue](#9.2)), and how the system can be tuned for throughput ([Performance Optimization](#9.3)).

For configuration knobs that control these features, see the [Configuration](#8) reference pages. For the agent-mode iterative loop, see [Agent System](#5).

---

## Feature Map

The diagram below shows which code module implements each advanced feature and where it sits in the request lifecycle.

**Advanced Features: Module Mapping**

```mermaid
flowchart TD
    Q["Incoming Query"] --> QP["QueryProcessor\nquery_processor.py"]
    QP -->|"resolve references\nfrom history"| MT["Multi-Turn Dialogue\n(session store in cache.py)"]
    QP --> RS["RepositorySelector\nrepo_selector.py"]

    subgraph Retrieval["Retrieval Phase"]
        RS -->|"stage 1: repo overview match"| OVERVIEW["repo_overviews.pkl\n+ LLM ranking"]
        OVERVIEW -->|"stage 2: element search"| HR["HybridRetriever\n(semantic + BM25 + graph)"]
    end

    HR -->|"ranked candidates"| SKIM["Code Skimming\n(answer_generator.py\ncontext truncation)"]
    SKIM --> AG["AnswerGenerator\nanswer_generator.py"]

    subgraph Caching["Cache Layer (cache.py)"]
        EMBED_CACHE["embedding cache\n(cache_embeddings flag)"]
        QUERY_CACHE["query result cache\n(cache_queries flag)"]
        SESSION_CACHE["dialogue session store\n(dialogue_ttl)"]
    end

    QP -.->|"check query cache"| QUERY_CACHE
    AG -.->|"write query cache"| QUERY_CACHE
    MT -.->|"read/write"| SESSION_CACHE
```

Sources: [README.md:85-116]()

---

## Summary of Advanced Features

| Feature | Primary Module(s) | Config Section | Page |
|---|---|---|---|
| Caching System | `cache.py` (`CacheManager`) | `cache:` | [9.1](#9.1) |
| Multi-Turn Dialogue | `cache.py`, `query_processor.py`, `answer_generator.py` | `query:`, `generation:` | [9.2](#9.2) |
| Performance Optimization | `embedder.py`, `cache.py`, `loader.py` | `embedding:`, `cache:`, `repository:` | [9.3](#9.3) |
| Code Skimming | `answer_generator.py` | `generation:` | [9.4](#9.4) |
| Two-Stage Retrieval | `repo_selector.py`, `query_processor.py` | `retrieval:` | [9.5](#9.5) |

---

## 9.1 — Caching System

`CacheManager` in `cache.py` provides three independent caches backed by either disk or Redis:

- **Embedding cache** — stores computed embedding vectors keyed by content hash; avoids re-running `SentenceTransformer` on unchanged code.
- **Query result cache** — stores full `(question, repo_filter)` → `answer` mappings with a configurable TTL.
- **Dialogue session store** — persists ordered turn lists keyed by `session_id`, enabling multi-turn conversations to survive server restarts.

See [Caching System](#9.1) for the full implementation details including backend initialization, TTL management, and failure handling.

---

## 9.2 — Multi-Turn Dialogue

Multi-turn mode links sequential queries through a shared `session_id`. The key interactions are:

1. `QueryProcessor` resolves pronouns and implicit references against stored history.
2. `AnswerGenerator` prepends a windowed context of prior turns (governed by `context_rounds` in `config.yaml`).
3. Each completed turn is written back to the session store via `CacheManager`.
4. `AnswerGenerator` emits a `<SUMMARY>` tag in its output; this tag is extracted and stored as the compressed history entry, keeping token costs bounded.

**Multi-Turn Dialogue Flow**

```mermaid
sequenceDiagram
    participant Client
    participant QP as "QueryProcessor\n(query_processor.py)"
    participant CM as "CacheManager\n(cache.py)"
    participant AG as "AnswerGenerator\n(answer_generator.py)"

    Client->>QP: "question + session_id"
    QP->>CM: "get_dialogue_history(session_id)"
    CM-->>QP: "prior turns (up to context_rounds)"
    QP->>QP: "resolve_references(question, history)"
    QP->>AG: "ProcessedQuery + history context"
    AG->>AG: "build prompt with prior summaries"
    AG-->>Client: "streamed answer + SUMMARY tag"
    AG->>CM: "store_dialogue_turn(session_id, turn)"
```

See [Multi-Turn Dialogue](#9.2) for the full session lifecycle and SUMMARY tag extraction.

---

## 9.3 — Performance Optimization

Performance-critical paths and their tuning handles:

| Bottleneck | Tuning Handle | Location |
|---|---|---|
| Embedding latency | `device: auto/cuda/mps/cpu`, `batch_size` | `embedding:` in `config.yaml` |
| Re-indexing on restart | `index scan cache` TTL + `sample_size` | `vector_store:` in `config.yaml` |
| Clone time | `clone_depth: 1` (shallow clone) | `repository:` in `config.yaml` |
| Repeated query cost | `cache_queries: true` | `cache:` in `config.yaml` |
| Retrieval precision vs. recall | `semantic_weight`, `keyword_weight`, `graph_weight` | `retrieval:` in `config.yaml` |

`CodeEmbedder` in `embedder.py` auto-detects the best available device (CUDA → MPS → CPU) at startup. Batch size directly controls throughput during initial indexing.

See [Performance Optimization](#9.3) for guidance on each tuning lever.

---

## 9.4 — Code Skimming

Code skimming is the mechanism by which `AnswerGenerator` in `answer_generator.py` reduces token consumption when the retrieved context exceeds the configured `max_context_tokens` budget.

Instead of truncating full file contents arbitrarily, skimming retains only the structural skeleton of lower-priority elements — function signatures, class definitions, and type annotations — discarding bodies. This preserves navigability of the context while reducing token count substantially.

**Context Budget Management**

```mermaid
flowchart LR
    R["Retrieved Elements\n(ranked list)"]
    R --> FULL["Full content\n(high-score elements)"]
    R --> SKIM["Skimmed content\n(signatures only,\nlower-score elements)"]
    R --> DROP["Dropped\n(over budget)"]

    FULL --> PROMPT["LLM Prompt\n(within max_context_tokens)"]
    SKIM --> PROMPT
```

The `reserve_tokens_for_response` setting in `config.yaml` under `generation:` carves out a guaranteed portion of the context window for the model's output before the skimming budget is calculated.

See [Code Skimming](#9.4) for implementation details.

---

## 9.5 — Two-Stage Retrieval

When multiple repositories are indexed, FastCode uses a two-stage selection strategy to avoid searching every repository for every query:

**Stage 1 — Repository Selection (`RepositorySelector` in `repo_selector.py`):**  
`RepositorySelector` uses pre-computed repository overviews (stored in `repo_overviews.pkl`) and LLM-assisted ranking to identify the `top_repos_to_search` most relevant repositories. Fuzzy name matching via Jaccard token overlap supplements the LLM ranking when repository names appear in the query.

**Stage 2 — Element Retrieval (`HybridRetriever`):**  
Fine-grained retrieval (semantic + BM25 + graph) runs only against the repositories selected in Stage 1.

**Two-Stage Retrieval Flow**

```mermaid
flowchart TD
    Q["User Query"]

    subgraph Stage1["Stage 1: Repository Selection"]
        RO["repo_overviews.pkl\n(RepositoryOverviewGenerator)"]
        RS["RepositorySelector.select_repositories()"]
        LLM1["LLM ranking call"]
        FUZZY["Jaccard token overlap\n(fuzzy name match)"]
        Q --> RS
        RS --> RO
        RS --> LLM1
        RS --> FUZZY
        LLM1 --> TOPK["top_repos_to_search\nrepo subset"]
        FUZZY --> TOPK
    end

    subgraph Stage2["Stage 2: Element Retrieval"]
        HR["HybridRetriever\n(semantic + BM25 + graph)"]
        TOPK --> HR
        Q --> HR
        HR --> RESULTS["Ranked CodeElements"]
    end

    RESULTS --> AG["AnswerGenerator"]
```

This is controlled by the `select_repos_by_overview`, `top_repos_to_search`, and `min_repo_similarity` knobs in the `retrieval:` section of `config.yaml`.

See [Two-Stage Retrieval](#9.5) and [Repository Selector](#5.4) for full details.

---

## How the Advanced Features Interact

All advanced features operate concurrently within a single query lifecycle. The diagram below shows their combined contribution to a multi-turn, multi-repo query.

**Full Advanced Feature Interaction (Multi-Turn, Multi-Repo Query)**

```mermaid
flowchart TD
    REQ["POST /api/query-stream\n(session_id, multi_turn=true, repo_filter)"]

    REQ --> CM_READ["CacheManager.get_dialogue_history()"]
    CM_READ --> QP["QueryProcessor.process_query()\n- resolve_references\n- expand_query\n- detect_intent"]

    QP --> QCACHE{"query cache\nhit?"}
    QCACHE -->|"yes"| CACHED_ANS["return cached answer"]
    QCACHE -->|"no"| RS["RepositorySelector\n(stage 1)"]

    RS --> HR["HybridRetriever\n(stage 2)"]
    HR --> SKIM["context budget\n+ skimming\n(answer_generator.py)"]
    SKIM --> AG["AnswerGenerator.generate_answer()\nstreaming SSE"]
    AG --> CM_WRITE["CacheManager.store_dialogue_turn()\nSUMMARY tag extraction"]
    AG --> QCACHE_WRITE["CacheManager.cache_query_result()"]
```

Sources: [README.md:99-116](), [README.md:638-643]()

---

