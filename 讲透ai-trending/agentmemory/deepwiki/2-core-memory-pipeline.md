<!-- source: DeepWiki mcp.deepwiki.com · repo rohitg00/agentmemory · page 2 Core Memory Pipeline · fetched 2026-10-30 -->

# Core Memory Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/functions/compress.ts](src/functions/compress.ts)
- [src/functions/consolidate.ts](src/functions/consolidate.ts)
- [src/functions/diagnostics.ts](src/functions/diagnostics.ts)
- [src/functions/disk-size-manager.ts](src/functions/disk-size-manager.ts)
- [src/functions/enrich.ts](src/functions/enrich.ts)
- [src/functions/image-quota-cleanup.ts](src/functions/image-quota-cleanup.ts)
- [src/functions/image-refs.ts](src/functions/image-refs.ts)
- [src/functions/migrate.ts](src/functions/migrate.ts)
- [src/functions/observe.ts](src/functions/observe.ts)
- [src/functions/remember.ts](src/functions/remember.ts)
- [src/functions/search.ts](src/functions/search.ts)
- [src/state/hybrid-search.ts](src/state/hybrid-search.ts)
- [src/state/memory-utils.ts](src/state/memory-utils.ts)
- [src/state/search-index.ts](src/state/search-index.ts)
- [src/triggers/events.ts](src/triggers/events.ts)
- [test/diagnostics.test.ts](test/diagnostics.test.ts)
- [test/hybrid-search.test.ts](test/hybrid-search.test.ts)
- [test/multimodal.test.ts](test/multimodal.test.ts)
- [test/search-index.test.ts](test/search-index.test.ts)
- [test/search.test.ts](test/search.test.ts)
- [test/session-end-triggers-graph.test.ts](test/session-end-triggers-graph.test.ts)
- [test/sliding-window.test.ts](test/sliding-window.test.ts)

</details>



The **Core Memory Pipeline** is the backbone of `agentmemory`, responsible for transforming the ephemeral "noise" of an agent's session into structured, persistent, and searchable knowledge. It bridges the gap between raw tool outputs and long-term architectural understanding.

This pipeline operates in four distinct stages that manage the lifecycle of data from the moment a tool is executed to its eventual consolidation into the agent's global knowledge base.

### The Four-Stage Lifecycle

```mermaid
graph LR
    subgraph "Capture"
        [A] -- "mem::observe" --> [B] -- "Dedup & Scrub" --> [B2]
    end
    subgraph "Compress"
        [B2] --> [C] -- "mem::compress" --> [D] -- "LLM Distillation" --> [D2]
    end
    subgraph "Consolidate"
        [D2] --> [E] -- "mem::remember" --> [F] -- "Tiered Storage" --> [F2]
    end
    subgraph "Retrieve"
        [F2] --> [G] -- "mem::smart-search" --> [H] -- "Hybrid Retrieval" --> [I]
    end

    style [A] stroke-width:2px
    style [C] stroke-width:2px
    style [E] stroke-width:2px
    style [G] stroke-width:2px
```

**Sources:** [src/functions/observe.ts:40-47](), [src/functions/compress.ts:67-74](), [src/functions/remember.ts:22-33](), [src/functions/search.ts:17-27]()

---

### 1. Observation & Capture
The pipeline begins with `mem::observe`. This stage intercepts `HookPayload` data from agent lifecycle events (like `pre_tool_use`, `post_tool_use`, or `prompt_submit`) [src/functions/observe.ts:4-47](). It performs critical "hygiene" tasks:
*   **Deduplication:** Uses a `DedupMap` to generate SHA-256 hashes of tool inputs, preventing redundant storage of identical operations [src/functions/observe.ts:66-90]().
*   **Privacy Scrubbing:** Invokes `stripPrivateData` to redact secrets and API keys using `SECRET_PATTERN_SOURCES` [src/functions/observe.ts:92-99]().
*   **Multimodal Handling:** Detects and extracts image data (base64 or file paths) via `extractImage`, saving them to a managed image store via `saveImageToDisk` [src/functions/observe.ts:17-38](), [src/functions/observe.ts:173-175]().
*   **Concurrency:** Employs `withKeyedLock` to ensure session-scoped KV writes are atomic [src/functions/observe.ts:146-155]().

For details, see [Observation & Capture](#2.1).

**Sources:** [src/functions/observe.ts:40-193](), [src/state/schema.ts:5-15]()

---

### 2. Compression & Summarization
Raw observations are often too verbose for long-term storage or context injection. The `mem::compress` function uses an LLM to distill a `RawObservation` into a `CompressedObservation`.
*   **Structured Extraction:** Extracts facts, concepts, narrative, and importance scores (1-10) using XML-based parsing via `parseCompressionXml` [src/functions/compress.ts:44-65]().
*   **Quality Control:** Validates output against `CompressOutputSchema` and uses `compressWithRetry` for self-correction [src/functions/compress.ts:123-142]().
*   **Vision Integration:** If an image is present, the pipeline uses `provider.describeImage` to generate a textual description before compression [src/functions/compress.ts:84-109]().
*   **Search Indexing:** Immediately adds the compressed result to the `SearchIndex` (BM25) and `VectorIndex` for retrieval [src/functions/compress.ts:178-194]().
*   **Event Propagation:** Triggers `event::session::stopped` to initiate post-session summarization and graph extraction [src/triggers/events.ts:96-118]().

For details, see [Compression & Summarization](#2.2).

**Sources:** [src/functions/compress.ts:67-206](), [src/triggers/events.ts:96-148]()

---

### 3. Memory Persistence & Lifecycle
Once compressed, data can be promoted to long-term memory via `mem::remember`. This stage manages the transition from session-specific observations to global knowledge.
*   **Versioning & Superseding:** Supports replacing old memories with new information, maintaining a version history and using `jaccardSimilarity` to detect duplicates (>0.7) [src/functions/remember.ts:108-134](), [src/state/schema.ts:3-3]().
*   **Tiered Indexing:** Every saved memory is indexed in both `SearchIndex` (BM25) and `VectorIndex` (Embeddings) via `vectorIndexAddGuarded` to ensure it is immediately discoverable [src/functions/remember.ts:79-88](), [src/functions/remember.ts:189-194]().
*   **Agent Scoping:** Memories are stamped with an `agentId` (from environment or payload) to allow multi-agent isolation [src/functions/remember.ts:147-150]().
*   **Audit Logging:** Records changes via `recordAudit` for transparency and rollback capabilities [src/functions/remember.ts:178-187]().

For details, see [Memory Persistence & Lifecycle](#2.3).

**Sources:** [src/functions/remember.ts:22-205](), [src/state/memory-utils.ts:6-9]()

---

### 4. Consolidation & Forgetting
The final stage ensures the memory stays relevant and manageable over time, preventing context window bloat and resource exhaustion.
*   **Synthesis:** Groups related observations by concept and synthesizes them into long-term memories via `mem::consolidate` [src/functions/consolidate.ts:70-125]().
*   **Pipeline Orchestration:** `mem::consolidate-pipeline` manages multi-tier consolidation and is debounced by `consolidationDue` to prevent LLM cost storms [src/triggers/events.ts:13-41](), [src/triggers/events.ts:141-146]().
*   **Resource Management:** Monitors disk usage for images via `mem::disk-size-delta` and handles image reference counting via `incrementImageRef` and `decrementImageRef` to allow safe cleanup [src/functions/disk-size-manager.ts:11-43](), [src/functions/image-refs.ts:12-38]().
*   **Quota Cleanup:** `mem::image-quota-cleanup` evicts unreferenced images when disk limits are exceeded [src/functions/image-quota-cleanup.ts:12-98]().

For details, see [Consolidation & Forgetting](#2.4).

**Sources:** [src/functions/consolidate.ts:70-210](), [src/functions/image-quota-cleanup.ts:12-98](), [src/functions/disk-size-manager.ts:11-43]()

---

### Data Flow: Code Entity Space
The following diagrams map the logical pipeline stages to the specific code entities and KV namespaces they interact with.

**Ingestion and Refinement Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        [Input] -- "Agent Tool Output" --> [Fact] -- "Extracted Fact" --> [Knowledge]
    end

    subgraph "Code Entity Space"
        [Payload] -- "HookPayload" --> [ObsFunc] -- "mem::observe" --> [CompFunc] -- "mem::compress" --> [MemFunc] -- "mem::remember" --> [Final]
        
        [KV_OBS] -- "KV.observations" --> [CompFunc]
        [ObsFunc] -- "set" --> [KV_OBS]
        
        [CompFunc] -- "add()" --> [SearchIdx] -- "SearchIndex" --> [Ret]
        [CompFunc] -- "vectorIndexAddGuarded()" --> [VecIdx] -- "VectorIndex" --> [Ret]
        
        [MemFunc] -- "set" --> [KV_MEM] -- "KV.memories" --> [Final]
    end

    [Input] --> [Payload]
    [Payload] --> [ObsFunc]
    [Fact] --> [CompFunc]
    [Knowledge] --> [MemFunc]
    
    [ObsFunc] -- "Uses" --> [Dedup] -- "DedupMap" --> [ObsFunc]
    [CompFunc] -- "Uses" --> [LLM] -- "MemoryProvider" --> [CompFunc]
```

**Storage and Retrieval Architecture**
```mermaid
graph TD
    subgraph "Code Entity Space"
        [KV_MEMS] -- "KV.memories" --> [HybridSearch]
        [KV_SESS] -- "KV.sessions" --> [HybridSearch]
        
        [SmartSearch] -- "mem::smart-search" --> [HybridSearch]
        [HybridSearch] -- "HybridSearch.search()" --> [SearchIndex]
        [HybridSearch] -- "HybridSearch.search()" --> [VectorIndex]
        
        [Remember] -- "mem::remember" --> [KV_MEMS]
        [Remember] -- "vectorIndexAddGuarded" --> [VectorIndex]
        [Remember] -- "getSearchIndex().add" --> [SearchIndex]
    end

    [KV_MEMS] --> [SmartSearch]
    [KV_SESS] --> [SmartSearch]
```

**Sources:** [src/functions/observe.ts:40-193](), [src/functions/compress.ts:73-203](), [src/functions/remember.ts:22-205](), [src/functions/search.ts:17-31](), [src/triggers/events.ts:43-183]()

---

