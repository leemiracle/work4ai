<!-- source: DeepWiki mcp.deepwiki.com · repo SamurAIGPT/llm-wiki-agent · page 5 Python Tools Reference · fetched 2026-10-26 -->

# Python Tools Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [requirements.txt](requirements.txt)
- [tools/build_graph.py](tools/build_graph.py)
- [tools/ingest.py](tools/ingest.py)
- [tools/lint.py](tools/lint.py)
- [tools/query.py](tools/query.py)

</details>



The `tools/` directory contains a suite of standalone Python scripts that provide a programmatic interface to the wiki's core workflows. While the system is designed to be driven by LLM agents (via `CLAUDE.md` or `AGENTS.md`), these scripts allow for automation, bulk processing, and fine-grained control over the wiki's state without requiring an active agent session.

### Python Toolset Overview

The following diagram illustrates how the Python tools interact with the filesystem-based wiki and external APIs to transition from raw data to a structured knowledge graph.

**Workflow: From Raw Space to Code Entity Space**

```mermaid
graph TD
    subgraph "Natural Language Space (Input)"
        [Raw_Docs] --> |"tools/ingest.py"| [Claude_API]
        [User_Query] --> |"tools/query.py"| [Claude_API]
    end

    subgraph "Code Entity Space (wiki/)"
        [Claude_API] --> |"writes"| [sources_dir]
        [Claude_API] --> |"writes"| [entities_dir]
        [Claude_API] --> |"writes"| [concepts_dir]
        [Claude_API] --> |"updates"| [index_md]
        [Claude_API] --> |"updates"| [overview_md]
    end

    subgraph "Tool Layer (Analysis)"
        [sources_dir] & [entities_dir] & [concepts_dir] --> |"scans"| [tools_lint_py]
        [sources_dir] & [entities_dir] & [concepts_dir] --> |"scans"| [tools_build_graph_py]
        [tools_lint_py] --> |"generates"| [lint_report_md]
        [tools_build_graph_py] --> |"exports"| [graph_html]
    end

    [index_md]:::file
    [overview_md]:::file
    [lint_report_md]:::file
    [graph_html]:::file
    [sources_dir]:::folder
    [entities_dir]:::folder
    [concepts_dir]:::folder

    classDef file stroke-dasharray: 5 5
    classDef folder font-style:italic
```
Sources: [tools/ingest.py:10-16](), [tools/lint.py:9-15](), [tools/build_graph.py:10-13]()

---

### Core Tools

#### [tools/ingest.py](#5.1)
The primary entry point for adding information to the wiki. It reads a source file, constructs a context window of the current wiki state, and uses `claude-sonnet-4-6` to generate structured markdown pages for sources, entities, and concepts. It also handles SHA256 hashing to track document versions and updates the global `index.md` and `overview.md`.

For details, see [tools/ingest.py](#5.1).

#### [tools/query.py](#5.2)
A retrieval and synthesis tool. It performs a two-stage retrieval: first using keyword matching against the index, and then using `claude-haiku-4-5` to select the most relevant pages if keywords fail. It synthesizes a final answer with `[[wikilink]]` citations and can optionally persist the result as a new page in `wiki/syntheses/`.

For details, see [tools/query.py](#5.2).

#### [tools/lint.py](#5.3)
The wiki health-check utility. It combines deterministic regex-based checks (for orphan pages, broken links, and missing entity pages) with a semantic pass using `claude-sonnet-4-6` to identify contradictions and data gaps. It outputs a comprehensive `lint-report.md`.

For details, see [tools/lint.py](#5.3).

#### [tools/build_graph.py](#5.4)
The visualization engine. It extracts explicit `EXTRACTED` edges from wikilinks and uses `claude-haiku-4-5` to infer implicit `INFERRED` or `AMBIGUOUS` relationships. It utilizes `networkx` for Louvain community detection and generates an interactive `vis.js` HTML graph.

For details, see [tools/build_graph.py](#5.4).

---

### Common Utilities and Dependencies

The tools share several common patterns and dependencies to ensure consistency across the wiki:

| Component | Code Reference | Description |
| :--- | :--- | :--- |
| **API Client** | `anthropic.Anthropic()` | Used by all tools for LLM interactions. |
| **Hashing** | `sha256()` | Used in `ingest.py` [36-37]() and `build_graph.py` [67-68]() for change detection. |
| **File I/O** | `read_file()`, `write_file()` | Standardized UTF-8 handling across the toolset. |
| **Link Extraction** | `extract_wikilinks()` | Regex `\[\[([^\]]+)\]\]` used in `lint.py` [41-42]() and `build_graph.py` [76-77](). |

**Dependency Mapping**

```mermaid
graph LR
    [tools/ingest.py] --> [anthropic]
    [tools/query.py] --> [anthropic]
    [tools/lint.py] --> [anthropic]
    [tools/build_graph.py] --> [anthropic]
    [tools/build_graph.py] --> [networkx]
    
    subgraph "External Libraries"
        [anthropic]
        [networkx]
    end
```
Sources: [requirements.txt:1-2](), [tools/ingest.py:26](), [tools/build_graph.py:28-31]()

---

