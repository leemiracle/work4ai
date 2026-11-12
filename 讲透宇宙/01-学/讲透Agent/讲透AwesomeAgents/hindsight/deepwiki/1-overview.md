<!-- source: DeepWiki mcp.deepwiki.com · repo vectorize-io/hindsight · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docker/standalone/start-all.sh](docker/standalone/start-all.sh)
- [docker/standalone/test-start-all.sh](docker/standalone/test-start-all.sh)
- [helm/hindsight/Chart.yaml](helm/hindsight/Chart.yaml)
- [hindsight-api-slim/hindsight_api/http_probe.py](hindsight-api-slim/hindsight_api/http_probe.py)
- [hindsight-api-slim/tests/test_http_probe.py](hindsight-api-slim/tests/test_http_probe.py)
- [hindsight-api/pyproject.toml](hindsight-api/pyproject.toml)
- [hindsight-cli/Cargo.toml](hindsight-cli/Cargo.toml)
- [hindsight-clients/python/pyproject.toml](hindsight-clients/python/pyproject.toml)
- [hindsight-clients/typescript/package.json](hindsight-clients/typescript/package.json)
- [hindsight-control-plane/bin/cli.js](hindsight-control-plane/bin/cli.js)
- [hindsight-control-plane/package.json](hindsight-control-plane/package.json)
- [hindsight-control-plane/tests/lib/cli-bind-host.test.ts](hindsight-control-plane/tests/lib/cli-bind-host.test.ts)
- [hindsight-dev/pyproject.toml](hindsight-dev/pyproject.toml)
- [hindsight-docs/docs/developer/api/quickstart.mdx](hindsight-docs/docs/developer/api/quickstart.mdx)
- [hindsight-docs/docs/developer/installation.md](hindsight-docs/docs/developer/installation.md)
- [hindsight-docs/versioned_docs/version-0.8/developer/installation.md](hindsight-docs/versioned_docs/version-0.8/developer/installation.md)
- [hindsight-docs/versioned_docs/version-0.9/developer/api/quickstart.mdx](hindsight-docs/versioned_docs/version-0.9/developer/api/quickstart.mdx)
- [hindsight-docs/versioned_docs/version-0.9/developer/installation.md](hindsight-docs/versioned_docs/version-0.9/developer/installation.md)
- [hindsight-embed/hindsight_embed/__init__.py](hindsight-embed/hindsight_embed/__init__.py)
- [hindsight-embed/pyproject.toml](hindsight-embed/pyproject.toml)
- [hindsight-integrations/litellm/pyproject.toml](hindsight-integrations/litellm/pyproject.toml)
- [skills/hindsight-docs/references/developer/api/quickstart.md](skills/hindsight-docs/references/developer/api/quickstart.md)
- [skills/hindsight-docs/references/developer/installation.md](skills/hindsight-docs/references/developer/installation.md)

</details>



## Purpose and Scope

Hindsight™ is an agent memory system designed to build smarter agents that learn and evolve over time. Moving beyond mere conversation history, Hindsight uses a **biomimetic long-term memory architecture** that distinctly organizes stored knowledge into three core fact types: world facts (external objective knowledge), experience facts (agent's interactions and actions), and mental models (curated knowledge summaries) [README.md:22-28](). This structure supports persistent, nuanced agent state, entity resolution across sessions, and autonomous reflection to synthesize new insights [README.md:22-28]().

This page provides a high-level introduction to Hindsight’s core concepts, operations, and monorepo architecture. For expanded technical details on package layout and documentation tooling, please refer to the child pages:
- **[Package Structure](#1.1)** — Overview of the monorepo composition including core engine variants, client SDKs, integrations, and distribution targets.
- **[Documentation and Skills Sites](#1.2)** — Explanation of the documentation site (`hindsight-docs`), the `skills/` AI-agent consumable references, and LLM provider metadata generation.

Sources: [README.md:22-28]()

---

## Biomimetic Memory Architecture

Hindsight’s design is inspired by human cognition, structuring memory into distinct but interconnected layers to foster comprehensive and adaptable agent reasoning.

### Memory Types and Their Representation

| Memory Type | Code Representation | Role and Purpose |
|---|---|---|
| **World Facts** | `MemoryUnit` entries with `fact_type = world` | Objective external facts about the environment or general knowledge [README.md:35](). |
| **Experience Facts** | `MemoryUnit` entries with `fact_type = experience` | Records of the agent's own actions, interactions, and experiences [README.md:35](). |
| **Observations** | `MemoryUnit` entries with `fact_type = observation` | Synthesized patterns and higher-level insight formed by consolidating related facts [README.md:35](). |
| **Mental Models** | `MentalModel` entities (stored separately) | Curated, stable knowledge pages or summaries established for common queries or persona definition [README.md:35](). |

The system supports interlinking these fact types, with reflection operations primarily operating on mental models and observations to prioritize relevant, distilled knowledge [README.md:35]().

### Diagram: Biomimetic Memory Hierarchy Mapping
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        MM_NL["Mental Model (Curated Knowledge)"]
        OBS_NL["Observation (Pattern Synthesis)"]
        WORLD_NL["World Fact (Objective Knowledge)"]
        EXP_NL["Experience Fact (Agent Actions)"]
    end

    subgraph "CodeEntitySpace"
        MM["MentalModel<br/>(\"mental_models\" table)"]
        OBS["MemoryUnit (Observation)<br/>(\"memory_units\" table)"]
        WORLD["MemoryUnit (World Fact)<br/>(\"memory_units\" table)"]
        EXP["MemoryUnit (Experience Fact)<br/>(\"memory_units\" table)"]
    end
    
    MM_NL -.-> MM
    OBS_NL -.-> OBS
    WORLD_NL -.-> WORLD
    EXP_NL -.-> EXP
    
    MM -->|Reflect Priority 1| OBS
    OBS -->|Synthesized from| WORLD
    OBS -->|Synthesized from| EXP
```

Sources: [README.md:35]()

---

## Core Operations

Hindsight defines a concise set of operations as the backbone for memory interaction:

| Operation | Description |
|---|---|
| **RETAIN** | Ingest new information by extracting facts from inputs, performing entity resolution, and generating vector embeddings [README.md:35](). |
| **RECALL** | Retrieve relevant memories using a multi-strategy retrieval system that combines semantic vector search, BM25 text search, graph traversal, and temporal proximity [README.md:35](). |
| **REFLECT** | Perform autonomous reasoning by iteratively querying recall results, consulting mental models and directives, and synthesizing answers [README.md:35](). |

Sources: [README.md:35]()

---

## Monorepo Structure

Hindsight is developed and distributed as a monorepo consisting of specialized packages, SDKs, integration libraries, control plane UI, and developer tools.

For details on package organization, distribution targets, and interdependencies, see [Package Structure](#1.1).

### Diagram: Mapping Natural Language Components to Code Entities and Packages
```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        CoreEngine_NL["Core Memory Engine"]
        ClientSDKs_NL["Multi-language Clients and CLI"]
        ControlPlane_NL["Control Plane UI"]
    end

    subgraph "CodeEntitySpace"
        API_SLIM["hindsight-api-slim<br/>(\"hindsight_api\" package)"]
        API_FULL["hindsight-api<br/>(\"hindsight_api.main\")"]
        ALL_PACKAGES["hindsight-all / hindsight-all-slim / hindsight-all-npm"]
        PYTHON_SDK["hindsight-clients/python"]
        TS_SDK["hindsight-clients/typescript"]
        GO_SDK["hindsight-clients/go"]
        RUST_CLI["hindsight-cli (Rust CLI)"]
        EMBEDDED["hindsight-embed"]
        CONTROL_PLANE["hindsight-control-plane<br/>(\"@vectorize-io/hindsight-control-plane\")"]
    end

    CoreEngine_NL -.-> API_SLIM
    API_SLIM --> API_FULL
    API_FULL --> ALL_PACKAGES

    ClientSDKs_NL --> PYTHON_SDK
    ClientSDKs_NL --> TS_SDK
    ClientSDKs_NL --> GO_SDK
    ClientSDKs_NL --> RUST_CLI
    ClientSDKs_NL --> EMBEDDED

    ControlPlane_NL -.-> CONTROL_PLANE
    ALL_PACKAGES --> PYTHON_SDK
    ALL_PACKAGES --> TS_SDK
    ALL_PACKAGES --> RUST_CLI
    ALL_PACKAGES --> CONTROL_PLANE
```

Sources: [hindsight-api/pyproject.toml:7](), [hindsight-control-plane/package.json:3]()

---

## Documentation and Skills Sites

Hindsight includes comprehensive documentation (`hindsight-docs`), Docusaurus sites, versioned docs, an `skills/` directory containing AI-agent-consumable references, and automated `llms.txt` generation.

For details on documentation tooling, layout, and agent skills, see [Documentation and Skills Sites](#1.2).

Sources: [README.md:56-60]()

---

## Child Pages

- **[Package Structure](#1.1)** — Detail the monorepo organization: `hindsight-api-slim`, `hindsight-api`, `hindsight-all`, client SDKs, integrations, control plane, Rust CLI, `hindsight-embed`, and extensions.
- **[Documentation and Skills Sites](#1.2)** — Cover `hindsight-docs` Docusaurus site, `skills/` directory, and `llms.txt` generation.

Sources: [README.md:22-120]()

---

