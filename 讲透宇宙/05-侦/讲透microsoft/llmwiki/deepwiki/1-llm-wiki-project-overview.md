<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/llmwiki · page 1 LLM Wiki — Project Overview · fetched 2026-10-26 -->

# LLM Wiki — Project Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [README.md](README.md)
- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



LLM Wiki is a technical solution for building personal knowledge bases where the burden of maintenance—summarization, cross-referencing, and indexing—is shifted from the human to a Large Language Model (LLM). Unlike traditional RAG (Retrieval-Augmented Generation) systems that synthesize information from raw documents at query time, LLM Wiki maintains a persistent, structured markdown-based wiki that evolves as new sources are added [README.md:8-12]().

## System Architecture

The system is built on a **Three-Layer Architecture** designed to separate human-curated data from LLM-generated synthesis, governed by a shared schema [ARCHITECTURE.md:21-33]().

| Layer | Owner | Purpose |
| :--- | :--- | :--- |
| **Raw Sources** | Human | Immutable source documents (PDFs, notes, articles) [ARCHITECTURE.md:38-46](). |
| **Wiki** | LLM | Generated markdown files (Entities, Concepts) and internal tracking (`index.md`, `log.md`) [ARCHITECTURE.md:47-57](). |
| **Schema** | Human + LLM | The `AGENTS.md` file defining structure, naming conventions, and workflows [ARCHITECTURE.md:58-66](). |

### Logical Data Flow

The following diagram illustrates how raw information is transformed into structured knowledge through the system's core entities.

**Diagram: Data Transformation Pipeline**
```mermaid
graph TD
    subgraph "Natural Language Space (Human)"
        [RawSource] --> [IngestPipeline]
    end

    subgraph "Code Entity Space (@llmwiki/core)"
        [IngestPipeline] -- "ingestSource()" --> [WikiPage]
        [WikiPage] -- "updateIndexEntry()" --> [IndexEntry]
        [IndexEntry] -- "appendEntry()" --> [WikiLog]
    end

    subgraph "Storage Layer (.wiki)"
        [WikiPage] --> [wiki_dir/"*.md"]
        [IndexEntry] --> [wiki_index/"index.md"]
        [WikiLog] --> [wiki_log/"log.md"]
    end

    [AGENTS.md] -. "Governs" .-> [IngestPipeline]
```
Sources: [ARCHITECTURE.md:7-34](), [packages/core/src/ingest.ts:1-10](), [packages/core/src/index-ops.ts:1-10]()

## Monorepo Layout

The project is managed as an npm workspaces monorepo [package.json:16-19]().

*   **`packages/core` (`@llmwiki/core`)**: The engine of the system. It contains the logic for file I/O, search, linting, and the Model Context Protocol (MCP) server [README.md:38]().
*   **`packages/vscode` (`llmwiki`)**: The VS Code extension providing the user interface, tree views, and integration with GitHub Copilot [README.md:39]().

**Diagram: Package Dependency and Components**
```mermaid
graph LR
    subgraph "packages/vscode"
        [extension.ts] -- "uses" --> [llmIngest.ts]
        [extension.ts] -- "renders" --> [WikiPagesTreeDataProvider]
        [extension.ts] -- "registers" --> [chatParticipant.ts]
    end

    subgraph "packages/core"
        [wiki.ts] -- "IO" --> [index-ops.ts]
        [lint.ts] -- "validates" --> [wiki.ts]
        [mcp/server.ts] -- "exposes" --> [wiki.ts]
    end

    [packages/vscode] -- "depends on" --> [packages/core]
```
Sources: [README.md:41-43](), [ARCHITECTURE.md:84-125]()

## Key Features

*   **Zero-Bookkeeping Maintenance**: The LLM handles the creation of entity/concept pages and maintains the `index.md` catalog [README.md:8-12]().
*   **Weighted Search**: A custom query engine in `query.ts` that scores matches across titles, summaries, and body text [ARCHITECTURE.md:105]().
*   **Automated Health Checks**: A linting system in `lint.ts` that detects broken links, orphaned pages, and stale index entries [ARCHITECTURE.md:98]().
*   **MCP Integration**: An MCP server allowing any compatible agent (like Claude Desktop) to interact with the wiki via standard tools [README.md:122-124]().

## Child Pages

For detailed technical documentation, refer to the following sections:

*   **[Getting Started](#1.1)**: Prerequisites, installation, and workspace initialization [README.md:45-68]().
*   **[Three-Layer Architecture](#1.2)**: Deep dive into the relationship between `raw/`, `wiki/`, and `AGENTS.md` [ARCHITECTURE.md:36-66]().

Sources: [README.md:1-125](), [ARCHITECTURE.md:1-130](), [package.json:1-48]()

---

