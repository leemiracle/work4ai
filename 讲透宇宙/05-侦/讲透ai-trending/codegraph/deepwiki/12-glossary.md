<!-- source: DeepWiki mcp.deepwiki.com · repo colbymchenry/codegraph · page 12 Glossary · fetched 2026-10-30 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/agent-eval/corpus.json](.claude/skills/agent-eval/corpus.json)
- [CHANGELOG.md](CHANGELOG.md)
- [__tests__/daemon-client-liveness.test.ts](__tests__/daemon-client-liveness.test.ts)
- [__tests__/daemon-silent-holder.test.ts](__tests__/daemon-silent-holder.test.ts)
- [__tests__/daemon-socket-fallback.test.ts](__tests__/daemon-socket-fallback.test.ts)
- [__tests__/extraction.test.ts](__tests__/extraction.test.ts)
- [__tests__/mcp-daemon.test.ts](__tests__/mcp-daemon.test.ts)
- [__tests__/proxy-liveness-watchdog.test.ts](__tests__/proxy-liveness-watchdog.test.ts)
- [__tests__/proxy-shutdown.test.ts](__tests__/proxy-shutdown.test.ts)
- [__tests__/resolution.test.ts](__tests__/resolution.test.ts)
- [src/db/queries.ts](src/db/queries.ts)
- [src/extraction/grammars.ts](src/extraction/grammars.ts)
- [src/extraction/index.ts](src/extraction/index.ts)
- [src/extraction/languages/index.ts](src/extraction/languages/index.ts)
- [src/extraction/tree-sitter.ts](src/extraction/tree-sitter.ts)
- [src/index.ts](src/index.ts)
- [src/mcp/daemon-paths.ts](src/mcp/daemon-paths.ts)
- [src/mcp/daemon.ts](src/mcp/daemon.ts)
- [src/mcp/engine.ts](src/mcp/engine.ts)
- [src/mcp/index.ts](src/mcp/index.ts)
- [src/mcp/proxy.ts](src/mcp/proxy.ts)
- [src/mcp/session.ts](src/mcp/session.ts)
- [src/resolution/import-resolver.ts](src/resolution/import-resolver.ts)
- [src/resolution/index.ts](src/resolution/index.ts)
- [src/resolution/name-matcher.ts](src/resolution/name-matcher.ts)
- [src/resolution/types.ts](src/resolution/types.ts)
- [src/types.ts](src/types.ts)

</details>



This page defines codebase-specific terms, domain concepts, jargon, and abbreviations used throughout the CodeGraph system. It serves as a comprehensive reference for terminology found in the source code, database schemas, and documentation.

---

## Core Entities and Data Model

### Node
A **Node** represents a discrete code symbol extracted from source files, such as a function, class, interface, method, struct, or file.
*   **Implementation**: Defined by the `Node` interface in [src/types.ts:132-201]().
*   **Key Attributes**: Includes a unique `id` (hash combining file path, kind, name, and line), `kind`, `name`, `qualifiedName`, and location coordinates (`startLine`, `startColumn`, `endLine`, `endColumn`) [src/types.ts:134-161]().

### Edge
An **Edge** represents a directed relationship between two nodes in the knowledge graph.
*   **Implementation**: Defined by the `Edge` interface in [src/types.ts:206-227]().
*   **Kinds**: Relationships include `contains`, `calls`, `imports`, `extends`, `implements`, and `type_of` [src/types.ts:57-70]().
*   **Provenance**: Tracks how an edge was generated or verified (e.g., precise import mapping, exact name match, or heuristic synthesis) [src/types.ts:226]().

### Unresolved Reference
An **Unresolved Reference** is a symbol reference extracted from code during parsing that has not yet been bound to a target node ID.
*   **Implementation**: Defined by the `UnresolvedRef` interface in [src/resolution/types.ts:12-35]().
*   **Purpose**: Enables parallel, file-level extraction without requiring the entire project graph or all symbols to be loaded in memory simultaneously.

**Sources:**
* [src/types.ts:132-227]()
* [src/resolution/types.ts:12-35]()

---

## Node and Edge Kinds

### Node Kinds
Symbols are categorized into specific types defined in `NODE_KINDS` [src/types.ts:22-46]().
*   **Container Kinds**: Parent symbols that encapsulate other nodes, such as `class`, `struct`, `interface`, `trait`, `protocol`, `enum`, `namespace`, and `module` [src/types.ts:25-36]().
*   **Specialized Kinds**: Includes `route` (web endpoints), `component` (UI elements), `type_alias`, and `file` [src/types.ts:38-44]().

### Edge Kinds
Edges define the semantics of code interactions [src/types.ts:57-70]().
*   `contains`: Parent-child containment (e.g., file contains a class, class contains a method) [src/types.ts:58]().
*   `calls`: Function or method invocation [src/types.ts:59]().
*   `imports`: Module or file dependency [src/types.ts:60]().
*   `extends` / `implements`: Inheritance and interface realization relationships [src/types.ts:61-62]().

**Sources:**
* [src/types.ts:22-70]()

---

## Resolution and Matching Jargon

### Ambiguous Name Ceiling
To prevent O($K^2$) performance degradation in large codebases with thousands of identically-named definitions (such as vendored themes or third-party UI component libraries), fuzzy name matching declines to score symbols defined more times than `AMBIGUOUS_NAME_CEILING` (default: 500) [src/resolution/name-matcher.ts:28-47]().
*   **Configuration**: Tunable via the `CODEGRAPH_AMBIGUOUS_NAME_CEILING` environment variable [src/resolution/name-matcher.ts:48-54]().

### Provenance
Metadata attached to edges or resolution results recording the exact strategy or mechanism that established a relationship (e.g., `exact-match`, `import`, `qualified-name`, `framework`, or `fuzzy`) [src/resolution/types.ts:48]().

### Deferral
The mechanism by which complex type inference or chained-method resolutions (such as fluent API builder patterns or deep type parameter bounds) are postponed to a secondary resolution pass after all primary declarations and basic imports are loaded into the graph [src/resolution/index.ts:80-92]().

### Buffer Contract v1
The binary wire protocol and memory layout used by the native Rust extraction kernel (`codegraph-kernel`) to pass extracted nodes, edges, and parse buffers across the FFI boundary to Node.js via `napi-rs`.

### Brace Scopes
A lightweight structural scanner used during C/C++ parsing and macro expansion that tracks block boundaries (`{` and `}`) to resolve out-of-line method definitions and member scoping without performing heavy AST re-allocations [src/extraction/tree-sitter.ts:24-25]().

### Segment Vocab
The tokenization and vocabulary dictionary used for identifier segmentation (splitting camelCase, snake_case, and kebab-case identifiers into discrete searchable tokens for SQLite FTS5 searches) [src/search/identifier-segments.ts]().

Diagram: Natural Language Space to Code Entity Space Resolution
```mermaid
graph TD
    subgraph "Natural-Language-Space"
        UserQuery[""Find the implementation of user login""]
    end

    subgraph "Context-Orchestration"
        NS[""extractQueryPaths()""]
        QB[""QueryBuilder.searchNodes()""]
    end

    subgraph "Code-Entity-Space"
        NodeTable[""Node (src/types.ts)""]
        Matcher[""matchReference()""]
        Resolver[""ReferenceResolver""]
    end

    UserQuery --> NS
    NS -- "Normalized Tokens" --> QB
    QB --> NodeTable
    NodeTable --> Matcher
    Matcher --> Resolver
```
*Sources: [src/types.ts:132-201](), [src/resolution/index.ts:1-10](), [src/db/queries.ts:21-27]()*

**Sources:**
* [src/resolution/name-matcher.ts:28-54]()
* [src/extraction/tree-sitter.ts:24-25]()
* [src/resolution/types.ts:40-50]()

---

## Architectural and Operational Concepts

### Explore Budget
An adaptive numeric budget calculated by the context builder that determines the maximum recommended number of tool explorations or subgraph expansions for a given agent task, preventing token exhaustion and infinite context loops.

### Writer Lock
A file-system-level mutual exclusion lock (`codegraph.lock`) placed inside the `.codegraph/` directory to prevent concurrent write operations and race conditions across multiple processes (e.g., CLI commands, background MCP servers, auto-sync file watchers, and Git hooks) [src/index.ts:187-190]().

### Daemon, Proxy, and Direct Modes
*   **Direct Mode**: The CLI or SDK directly opens the SQLite database and performs queries or indexing in-process.
*   **Daemon Mode**: A long-running background process spawned by the MCP server or CLI that holds the database connection, monitors file changes, and serves requests.
*   **Proxy Mode**: The lightweight MCP front-end routing client requests through the background daemon or spawning it lazily when needed [src/mcp/daemon.ts]().

### WAL Valve
A checkpoint management utility (`WalCheckpointValve`) that controls SQLite Write-Ahead Log (WAL) flushing thresholds, checkpointing frequency, and disk space usage during heavy bulk-indexing operations [src/index.ts:31]().

### Framework Resolvers
A pluggable system of language-specific and framework-aware matchers that inspect routing annotations and dependency structures (e.g., Express, Next.js, NestJS, Spring, Laravel, Rails) to synthesize connection edges between URLs/routes and handler functions [src/resolution/index.ts:39-48]().

### Synthesizers
Heuristic rule engines (Dispatch and Callback Synthesizers) that infer control flow and callback relationships for dynamic dispatch patterns, such as event emitters, framework event buses, function-pointer tables, and UI render bridges [src/resolution/callback-synthesizer.ts:40]().

Diagram: Extraction Pipeline Architecture and Kernel Wire Contract
SourceFile --> DetectLang --> NativeKernel --> BufferContractV1 --> StoreWriter
*Sources: [src/extraction/index.ts:20-28](), [src/extraction/tree-sitter.ts:40-41]()*

**Sources:**
* [src/index.ts:31-190]()
* [src/resolution/index.ts:39-48]()
* [src/resolution/callback-synthesizer.ts:40]()

---

## Telemetry and Viewer Concepts

### Telemetry Terms
*   **Opt-out Collector**: First-party telemetry client that records anonymous CLI usage metrics while respecting `CODEGRAPH_TELEMETRY=0`, `DO_NOT_TRACK=1`, or `codegraph telemetry off` [CHANGELOG.md:14-15]().
*   **Ingest Worker**: Cloudflare Worker endpoint (`telemetry.getcodegraph.com`) responsible for validating event schemas and storing anonymized telemetry in a D1 database with automatic 90-day retention rollups.

### Viewer Steps and Screens
*   **Steps Model**: A graph visualization construct used by the local web UI (`codegraph ui` / `ui/`) that linearizes complex execution flows and branch guards into chronological or logical navigation steps [ui/src/lib/steps-model.ts]().
*   **Screens Model**: UI visualization abstraction representing screen-level or route-level component trees mapped from front-end framework routes to underlying data models [ui/src/lib/screens-model.ts]().

**Sources:**
* [CHANGELOG.md:14-15]()
* [ui/src/lib/steps-model.ts]()
* [ui/src/lib/screens-model.ts]()