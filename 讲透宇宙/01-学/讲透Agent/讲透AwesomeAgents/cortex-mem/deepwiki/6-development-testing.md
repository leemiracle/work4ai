<!-- source: DeepWiki mcp.deepwiki.com · repo sopaco/cortex-mem · page 6 Development & Testing · fetched 2026-10-26 -->

# Development & Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/rust.yml](.github/workflows/rust.yml)
- [scripts/publish-crates.js](scripts/publish-crates.js)

</details>



This section provides resources for developers contributing to Cortex Memory and researchers evaluating memory system performance. It covers the evaluation framework, architecture decisions, and contribution guidelines.

For integration with external frameworks, see [Integration Guides](#5). For API usage, see [API Reference](#7).

## Overview

Cortex Memory includes a comprehensive evaluation framework for benchmarking memory system performance against industry standards. The system enables:

- **Comparative Benchmarking**: Test Cortex Memory against LangMem, Simple RAG, and other memory systems.
- **Standard Metrics**: Recall@K, Precision@K, MRR, NDCG, semantic similarity, and keyword F1 scores.
- **Multiple Datasets**: Small (10 conversations, 40 questions) and full (50 conversations, 150 questions) test sets.
- **HTML Reports**: Visual comparison reports with statistical analysis and confidence intervals.

The evaluation framework is located in `examples/lomoco-evaluation/` and is Python-based to facilitate interoperability with multiple memory system implementations.

**Sources:** [examples/lomoco-evaluation/README.md:1-50]()

## Evaluation Framework Architecture

The `lomoco-evaluation` framework is designed for cross-system comparison, enabling benchmarking of Cortex Memory against other memory management systems using identical test datasets and evaluation metrics.

**Evaluation Framework Architecture**

```mermaid
graph TB
    subgraph "Entry Points"
        CORTEX_SCRIPT["run_cortex_mem_evaluation.py"]
        LANGMEM_SCRIPT["run_langmem_evaluation.py"]
        RAG_SCRIPT["baselines/simple_rag.py"]
    end
    
    subgraph "System-Specific Modules"
        CORTEX_ADD["cortex_mem/add.py<br/>Memory Addition via CLI"]
        CORTEX_SEARCH["cortex_mem/search.py<br/>Memory Search via CLI"]
        
        LANGMEM_ADD["langmem_eval/add.py<br/>LangMemAdd class"]
        LANGMEM_SEARCH["langmem_eval/search.py<br/>LangMemSearch class"]
        
        RAG_BASELINE["simple_rag.py<br/>Baseline Implementation"]
    end
    
    subgraph "Shared Infrastructure"
        QDRANT_CLIENT["QdrantClient<br/>Vector Database"]
        OPENAI_CLIENT["OpenAI Client<br/>Embeddings & Completions"]
        CONFIG["config.toml<br/>Shared Configuration"]
        RATE_LIMITER["RateLimiter<br/>Token Bucket (30/min)"]
    end
    
    subgraph "Datasets"
        LOCOMO10["locomo10.json<br/>10 conversations, 40 questions"]
        LOCOMO50["locomo50.json<br/>50 conversations, 150 questions"]
    end
    
    subgraph "Evaluation"
        MEMORY_EVAL["metrics/memory_evaluation.py<br/>MemorySystemEvaluator"]
        LLM_JUDGE["metrics/improved_llm_judge.py<br/>0-5 Score Evaluation"]
    end
    
    subgraph "Output"
        RESULTS_JSON["results/*.json<br/>Evaluation Results"]
        REPORT_GEN["generate_report.py"]
        HTML_REPORT["results/*.html<br/>Visual Reports"]
    end
    
    CORTEX_SCRIPT --> CORTEX_ADD
    CORTEX_SCRIPT --> CORTEX_SEARCH
    LANGMEM_SCRIPT --> LANGMEM_ADD
    LANGMEM_SCRIPT --> LANGMEM_SEARCH
    
    CORTEX_ADD --> CONFIG
    CORTEX_SEARCH --> CONFIG
    LANGMEM_ADD --> QDRANT_CLIENT
    LANGMEM_ADD --> OPENAI_CLIENT
    LANGMEM_ADD --> RATE_LIMITER
    LANGMEM_SEARCH --> QDRANT_CLIENT
    LANGMEM_SEARCH --> OPENAI_CLIENT
    LANGMEM_SEARCH --> RATE_LIMITER
    RAG_BASELINE --> OPENAI_CLIENT
    
    CORTEX_ADD --> LOCOMO10
    CORTEX_ADD --> LOCOMO50
    LANGMEM_ADD --> LOCOMO10
    LANGMEM_ADD --> LOCOMO50
    RAG_BASELINE --> LOCOMO10
    RAG_BASELINE --> LOCOMO50
    
    CORTEX_SEARCH --> RESULTS_JSON
    LANGMEM_SEARCH --> RESULTS_JSON
    RAG_BASELINE --> RESULTS_JSON
    
    RESULTS_JSON --> MEMORY_EVAL
    MEMORY_EVAL --> RESULTS_JSON
    RESULTS_JSON --> REPORT_GEN
    REPORT_GEN --> HTML_REPORT
```

**Sources:** [examples/lomoco-evaluation/README.md:17-45](), [examples/lomoco-evaluation/src/langmem_eval/add.py:1-68](), [examples/lomoco-evaluation/src/langmem_eval/search.py:1-104]()

## CI/CD and Publishing

Cortex Memory utilizes GitHub Actions for continuous integration and custom Node.js scripts for managing workspace-wide crate publishing to crates.io.

**CI and Publishing Workflow**

```mermaid
graph LR
    subgraph "GitHub Actions"
        RUST_YML[".github/workflows/rust.yml"]
        BUILD["cargo build --verbose"]
        TEST["cargo test --verbose"]
    end

    subgraph "Publishing Tool"
        PUBLISH_JS["scripts/publish-crates.js"]
        DEP_ORDER["Dependency Order Resolution"]
        PATH_CONV["Path to Version Conversion"]
        CARGO_PUB["cargo publish --allow-dirty"]
    end

    subgraph "Crates.io"
        REGISTRY["Crates Registry"]
    end

    RUST_YML --> BUILD
    BUILD --> TEST
    PUBLISH_JS --> DEP_ORDER
    DEP_ORDER --> PATH_CONV
    PATH_CONV --> CARGO_PUB
    CARGO_PUB --> REGISTRY
```

### Automated Testing
The project maintains a Rust CI workflow [`.github/workflows/rust.yml:1-27`]() that triggers on every push and pull request to the `main` branch. It installs necessary system dependencies like `libasound2-dev` and `libxcb1-dev` [`.github/workflows/rust.yml:19-22`]() before executing `cargo build` and `cargo test` [`.github/workflows/rust.yml:23-26`]().

### Workspace Publishing
The `scripts/publish-crates.js` utility automates the release of the modular monolith crates in a specific dependency order to satisfy registry requirements [`scripts/publish-crates.js:27-38`]().

1.  **Dependency Ordering**: Crates are published in the order: `config` -> `core` -> `tools` -> `rig` -> (`service`, `cli`, `mcp`) [`scripts/publish-crates.js:28-38`]().
2.  **Path Dependency Conversion**: The script dynamically converts local path dependencies (e.g., `{ path = "../cortex-mem-core" }`) into versioned dependencies (e.g., `{ version = "0.1.0" }`) before publishing [`scripts/publish-crates.js:87-130`]().
3.  **Registry Verification**: It polls the crates.io API to ensure a crate is fully available before attempting to publish its dependents [`scripts/publish-crates.js:179-205`]().

**Sources:** [scripts/publish-crates.js:27-38](), [scripts/publish-crates.js:87-130](), [scripts/publish-crates.js:179-205](), [.github/workflows/rust.yml:1-27]()

## Child Pages

For deep technical details on specific development areas, refer to the following sub-pages:

- **[Evaluation Framework](#6.1)**: Detailed architecture of the `lomoco-evaluation` framework, dataset schemas, and performance comparison methodology.
- **[Architecture Decisions](#6.2)**: Documentation of key design choices including the use of MCP, the modular monolith pattern, and lazy agent loading.
- **[Contributing Guidelines](#6.3)**: Comprehensive guide for contributors, covering code style, PR processes, and detailed usage of the `scripts/publish-crates.js` tool.

**Sources:** [scripts/publish-crates.js:220-223](), [examples/lomoco-evaluation/README.md:431-456]()

---

