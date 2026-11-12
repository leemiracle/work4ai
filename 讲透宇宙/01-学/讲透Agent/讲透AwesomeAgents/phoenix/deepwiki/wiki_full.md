# Page: Phoenix Overview

# Phoenix Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-tracing/README.md](.agents/skills/phoenix-tracing/README.md)
- [.agents/skills/phoenix-tracing/SKILL.md](.agents/skills/phoenix-tracing/SKILL.md)
- [.agents/skills/phoenix-tracing/references/annotations-python.md](.agents/skills/phoenix-tracing/references/annotations-python.md)
- [.agents/skills/phoenix-tracing/references/instrumentation-atif-python.md](.agents/skills/phoenix-tracing/references/instrumentation-atif-python.md)
- [.agents/skills/phoenix-tracing/references/setup-python.md](.agents/skills/phoenix-tracing/references/setup-python.md)
- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [docs/phoenix.mdx](docs/phoenix.mdx)
- [docs/phoenix/evaluation/concepts-evals/evaluating-multi-agent-systems.mdx](docs/phoenix/evaluation/concepts-evals/evaluating-multi-agent-systems.mdx)
- [docs/phoenix/evaluation/llm-evals.mdx](docs/phoenix/evaluation/llm-evals.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/completeness.mdx](docs/phoenix/evaluation/pre-built-metrics/completeness.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/conciseness.mdx](docs/phoenix/evaluation/pre-built-metrics/conciseness.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/pii-detection.mdx](docs/phoenix/evaluation/pre-built-metrics/pii-detection.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/refusal.mdx](docs/phoenix/evaluation/pre-built-metrics/refusal.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/user-friction.mdx](docs/phoenix/evaluation/pre-built-metrics/user-friction.mdx)
- [docs/phoenix/integrations/python/pydantic/pydantic-evals.mdx](docs/phoenix/integrations/python/pydantic/pydantic-evals.mdx)
- [docs/phoenix/production-guide.mdx](docs/phoenix/production-guide.mdx)
- [docs/phoenix/release-notes/01-2025/01-18-2025-automatic-and-manual-span-tracing.mdx](docs/phoenix/release-notes/01-2025/01-18-2025-automatic-and-manual-span-tracing.mdx)
- [docs/phoenix/resources/frequently-asked-questions.mdx](docs/phoenix/resources/frequently-asked-questions.mdx)
- [docs/phoenix/resources/frequently-asked-questions/what-is-the-difference-between-phoenix-and-arize.mdx](docs/phoenix/resources/frequently-asked-questions/what-is-the-difference-between-phoenix-and-arize.mdx)
- [docs/phoenix/resources/phoenix-to-arize-ax-migration.mdx](docs/phoenix/resources/phoenix-to-arize-ax-migration.mdx)
- [docs/phoenix/self-hosting.mdx](docs/phoenix/self-hosting.mdx)
- [docs/phoenix/self-hosting/architecture.mdx](docs/phoenix/self-hosting/architecture.mdx)
- [docs/phoenix/self-hosting/features/management.mdx](docs/phoenix/self-hosting/features/management.mdx)
- [docs/phoenix/self-hosting/security/privacy.mdx](docs/phoenix/self-hosting/security/privacy.mdx)
- [docs/phoenix/settings/access-control-rbac.mdx](docs/phoenix/settings/access-control-rbac.mdx)
- [docs/phoenix/settings/data-retention.mdx](docs/phoenix/settings/data-retention.mdx)
- [docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/importing-existing-traces.mdx](docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/importing-existing-traces.mdx)
- [docs/phoenix/tracing/llm-traces/metrics.mdx](docs/phoenix/tracing/llm-traces/metrics.mdx)
- [docs/phoenix/tracing/llm-traces/projects.mdx](docs/phoenix/tracing/llm-traces/projects.mdx)
- [docs/phoenix/user-guide.mdx](docs/phoenix/user-guide.mdx)
- [internal_docs/specs/online-evals.md](internal_docs/specs/online-evals.md)
- [internal_docs/specs/playground.md](internal_docs/specs/playground.md)
- [internal_docs/specs/prompts.md](internal_docs/specs/prompts.md)
- [internal_docs/specs/server_evaluators.md](internal_docs/specs/server_evaluators.md)
- [js/packages/phoenix-client/README.md](js/packages/phoenix-client/README.md)
- [js/packages/phoenix-evals/README.md](js/packages/phoenix-evals/README.md)
- [js/packages/phoenix-mcp/README.md](js/packages/phoenix-mcp/README.md)
- [js/packages/phoenix-mcp/src/index.ts](js/packages/phoenix-mcp/src/index.ts)
- [js/packages/phoenix-mcp/src/projectTools.ts](js/packages/phoenix-mcp/src/projectTools.ts)
- [kustomize/README.md](kustomize/README.md)
- [packages/phoenix-client/CHANGELOG.md](packages/phoenix-client/CHANGELOG.md)
- [packages/phoenix-client/README.md](packages/phoenix-client/README.md)
- [packages/phoenix-client/pyproject.toml](packages/phoenix-client/pyproject.toml)
- [packages/phoenix-evals/CHANGELOG.md](packages/phoenix-evals/CHANGELOG.md)
- [packages/phoenix-evals/README.md](packages/phoenix-evals/README.md)
- [packages/phoenix-evals/pyproject.toml](packages/phoenix-evals/pyproject.toml)
- [packages/phoenix-otel/README.md](packages/phoenix-otel/README.md)
- [pyproject.toml](pyproject.toml)
- [requirements/ci.txt](requirements/ci.txt)
- [requirements/packages/phoenix-evals.txt](requirements/packages/phoenix-evals.txt)
- [requirements/type-check.txt](requirements/type-check.txt)
- [requirements/unit-tests.txt](requirements/unit-tests.txt)
- [src/phoenix/__init__.py](src/phoenix/__init__.py)
- [src/phoenix/version.py](src/phoenix/version.py)
- [tox.ini](tox.ini)
- [uv.lock](uv.lock)

</details>



## Purpose and Scope

This wiki page serves as the parent overview for **Arize Phoenix**, an open-source AI observability platform designed for tracing, evaluating, and experimenting with large language model (LLM) applications [README.md:47](). This page provides a high-level summary of Phoenix's purpose, key features, and overall architecture. For detailed technical specifications, refer to the child pages:
- [Package Structure & Monorepo](#1.1) — Detailed breakdown of Python and TypeScript packages, monorepo layout, versioning, and extensions.
- [Core Concepts & Terminology](#1.2) — Reference guide for domain concepts like spans, traces, datasets, experiments, and evaluators.

Sources:
- [README.md:47]()
- [src/phoenix/__init__.py:20-25]()

---

## What is Phoenix?

Arize Phoenix is a comprehensive AI observability platform built on OpenTelemetry standards [README.md:47](). The platform is organized as a monorepo containing a FastAPI-based server, database ORM layers, client libraries in Python and TypeScript, evaluation harnesses, and a React-based single-page application (SPA) user interface [README.md:47]().

The core components span several directories in the codebase:
- **Server Layer** (`src/phoenix/server/`): Manages application startup, HTTP routers, gRPC endpoints, and API schemas [src/phoenix/server/main.py:1-45]().
- **Data Layer** (`src/phoenix/db/`): Implements SQLAlchemy ORM models, migration scripts via Alembic, and database engines [src/phoenix/db/models.py:1-50]() [src/phoenix/db/engines.py:1-50]().
- **Client Libraries** (`packages/` and `js/packages/`): Provides programmatic access across Python (`arize-phoenix-client`, `arize-phoenix-evals`, `arize-phoenix-otel`) and TypeScript [.release-please-manifest.json:1-1]().

Sources:
- [README.md:47-50]()
- [src/phoenix/server/main.py:1-45]()
- [src/phoenix/db/models.py:1-50]()
- [.release-please-manifest.json:1-1]()

---

## Key Capabilities

Phoenix provides several primary capabilities for AI engineering:

1. **Tracing**: OpenTelemetry OTLP protocol ingestion via gRPC (port 4317) or HTTP (port 6006) with auto-instrumentation support for major frameworks [README.md:49]() [src/phoenix/config.py:40-75]().
2. **Evaluation**: LLM-as-judge evaluators for quality assessment, hallucinations, toxicity, and retrieval relevance [README.md:50]() [packages/phoenix-evals/CHANGELOG.md:20-25]().
3. **Datasets**: Versioned collections of examples for experimentation and testing [README.md:47-53]().
4. **Experiments**: Track and evaluate changes to prompts, models, and retrieval pipelines [README.md:47-53]().
5. **Playground**: Interactive model playground supporting streaming responses and multi-provider credentials [README.md:47-53]().
6. **Prompt Management**: Version control, tagging, and storage for prompt templates [README.md:47-53]().
7. **Phoenix Intelligence (PXI)**: Built-in AI assistant chat interface for debugging traces and navigating the platform [README.md:47-53]().
8. **Remote MCP Server**: Model Context Protocol integration exposing `/mcp` endpoints for AI coding assistants like Cursor and Claude Code [README.md:43-43]().

Sources:
- [README.md:43-53]()
- [packages/phoenix-evals/CHANGELOG.md:20-25]()

---

## Package Structure

Phoenix is organized as a monorepo with independently versioned packages managed via `release-please` [.release-please-manifest.json:1-1](). 

### Phoenix Monorepo Structure

```mermaid
graph TB
    subgraph "Python Packages"
        ARIZE_PHOENIX["arize-phoenix<br/>v20.24.0<br/>src/phoenix/"]
        CLIENT_PKG["arize-phoenix-client<br/>v3.5.0<br/>packages/phoenix-client/"]
        EVALS_PKG["arize-phoenix-evals<br/>v3.9.2<br/>packages/phoenix-evals/"]
        OTEL_PKG["arize-phoenix-otel<br/>v0.17.2<br/>packages/phoenix-otel/"]
        SQLEAN_PKG["arize-phoenix-sqlean<br/>v0.2.1<br/>packages/phoenix-sqlean/"]
    end
    
    subgraph "TypeScript Packages"
        TS_CLIENT["@arizeai/phoenix-client<br/>js/packages/phoenix-client/"]
        TS_MCP["@arizeai/phoenix-mcp<br/>js/packages/phoenix-mcp/"]
    end
    
    subgraph "Frontend"
        REACT_APP["React SPA<br/>app/"]
    end
    
    ARIZE_PHOENIX -->|"serves UI"| REACT_APP
    ARIZE_PHOENIX -->|"depends on"| CLIENT_PKG
    ARIZE_PHOENIX -->|"depends on"| EVALS_PKG
    ARIZE_PHOENIX -->|"depends on"| OTEL_PKG
    ARIZE_PHOENIX -->|"uses extension"| SQLEAN_PKG
```

| Package | Version | Location | Purpose |
| :--- | :--- | :--- | :--- |
| `arize-phoenix` | 20.24.0 | Root directory | Full platform: server, APIs, React UI [src/phoenix/version.py:1-1]() |
| `arize-phoenix-client` | 3.5.0 | `packages/phoenix-client/` | Python client for REST/GraphQL API [.release-please-manifest.json:1-1]() |
| `arize-phoenix-evals` | 3.9.2 | `packages/phoenix-evals/` | LLM evaluation framework [.release-please-manifest.json:1-1]() |
| `arize-phoenix-otel` | 0.17.2 | `packages/phoenix-otel/` | OpenTelemetry registration helpers [.release-please-manifest.json:1-1]() |
| `arize-phoenix-sqlean` | 0.2.1 | `packages/phoenix-sqlean/` | SQLite extension package [.release-please-manifest.json:1-1]() |

For details, see [Package Structure & Monorepo](#1.1).

Sources:
- [.release-please-manifest.json:1-1]()
- [src/phoenix/version.py:1-1]()

---

## High-Level Architecture & Ingestion Flow

Phoenix follows a client-server architecture where instrumented client applications send telemetry data to a central server via the OpenTelemetry Protocol (OTLP).

### Mapping Natural Language Space to Code Entity Space

```mermaid
graph LR
    PythonApp["UserPythonLLMApplication"]
    TypeScriptApp["UserTypeScriptLLMApplication"]
    PhoenixOtel["phoenix.otel.register() (packages/phoenix-otel)"]
    TSRegister["@arizeai/phoenix-otel register (js/packages/phoenix-otel)"]

    GRPCServer["grpc_server.py (src/phoenix/server/grpc_server.py)"]
    HTTPServer["main.py (src/phoenix/server/main.py)"]
    BulkInserter["BulkInserter (src/phoenix/db/insertion/bulk_inserter.py)"]
    DBModels["SQLAlchemy Models (src/phoenix/db/models.py)"]
    ReactFrontend["React SPA UI (app)"]

    PythonApp -->|"emit OTLP traces"| PhoenixOtel
    TypeScriptApp -->|"emit OTLP traces"| TSRegister

    PhoenixOtel -->|"send OTLP/gRPC"| GRPCServer
    PhoenixOtel -->|"send OTLP/HTTP"| HTTPServer

    GRPCServer --> BulkInserter
    HTTPServer --> BulkInserter
    BulkInserter --> DBModels

    ReactFrontend -->|"query data"| HTTPServer
    HTTPServer --> DBModels
```

The server runs two primary ingestion pathways:
1. **gRPC Server**: OTLP trace ingestion on port `4317` managed by `src/phoenix/server/grpc_server.py`.
2. **FastAPI HTTP Server**: Handles the React UI, REST/GraphQL APIs, and OTLP HTTP ingestion on port `6006` managed by `src/phoenix/server/main.py`.

Incoming spans are processed through `BulkInserter` and persisted using SQLAlchemy models (`src/phoenix/db/models.py`).

Sources:
- [src/phoenix/server/main.py:1-45]()
- [src/phoenix/server/grpc_server.py:1-50]()
- [src/phoenix/db/models.py:1-50]()

---

## Quick Start

### Installation

```bash
pip install arize-phoenix
```

### Launch Server

```python
import phoenix as px
session = px.launch_app()  # Starts server on http://localhost:6006
```
[src/phoenix/__init__.py:7-14]()

### Instrument Your Application

```python
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer_provider = register()
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```
[src/phoenix/__init__.py:38]()

For details on core entities, terminology, and data models, see [Core Concepts & Terminology](#1.2).

Sources:
- [src/phoenix/__init__.py:7-38]()
- [src/phoenix/version.py:1-1]()

---

# Page: Package Structure & Monorepo

# Package Structure & Monorepo

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-sqlean/SKILL.md](.agents/skills/phoenix-sqlean/SKILL.md)
- [.github/workflows/phoenix-sqlean-build.yml](.github/workflows/phoenix-sqlean-build.yml)
- [.github/workflows/phoenix-sqlean-ci.yml](.github/workflows/phoenix-sqlean-ci.yml)
- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [internal_docs/specs/online-evals.md](internal_docs/specs/online-evals.md)
- [internal_docs/specs/playground.md](internal_docs/specs/playground.md)
- [internal_docs/specs/prompts.md](internal_docs/specs/prompts.md)
- [internal_docs/specs/server_evaluators.md](internal_docs/specs/server_evaluators.md)
- [js/examples/apps/cli-agent-starter-kit/package.json](js/examples/apps/cli-agent-starter-kit/package.json)
- [js/examples/apps/phoenix-experiment-runner/package.json](js/examples/apps/phoenix-experiment-runner/package.json)
- [js/package.json](js/package.json)
- [js/packages/phoenix-cli/CHANGELOG.md](js/packages/phoenix-cli/CHANGELOG.md)
- [js/packages/phoenix-cli/package.json](js/packages/phoenix-cli/package.json)
- [js/packages/phoenix-client/CHANGELOG.md](js/packages/phoenix-client/CHANGELOG.md)
- [js/packages/phoenix-client/package.json](js/packages/phoenix-client/package.json)
- [js/packages/phoenix-config/CHANGELOG.md](js/packages/phoenix-config/CHANGELOG.md)
- [js/packages/phoenix-config/package.json](js/packages/phoenix-config/package.json)
- [js/packages/phoenix-evals/CHANGELOG.md](js/packages/phoenix-evals/CHANGELOG.md)
- [js/packages/phoenix-evals/package.json](js/packages/phoenix-evals/package.json)
- [js/packages/phoenix-mcp/CHANGELOG.md](js/packages/phoenix-mcp/CHANGELOG.md)
- [js/packages/phoenix-mcp/package.json](js/packages/phoenix-mcp/package.json)
- [js/packages/phoenix-otel/CHANGELOG.md](js/packages/phoenix-otel/CHANGELOG.md)
- [js/packages/phoenix-otel/package.json](js/packages/phoenix-otel/package.json)
- [js/pnpm-lock.yaml](js/pnpm-lock.yaml)
- [js/pnpm-workspace.yaml](js/pnpm-workspace.yaml)
- [kustomize/README.md](kustomize/README.md)
- [packages/phoenix-client/CHANGELOG.md](packages/phoenix-client/CHANGELOG.md)
- [packages/phoenix-client/pyproject.toml](packages/phoenix-client/pyproject.toml)
- [packages/phoenix-evals/CHANGELOG.md](packages/phoenix-evals/CHANGELOG.md)
- [packages/phoenix-evals/pyproject.toml](packages/phoenix-evals/pyproject.toml)
- [packages/phoenix-sqlean/CHANGELOG.md](packages/phoenix-sqlean/CHANGELOG.md)
- [packages/phoenix-sqlean/Makefile](packages/phoenix-sqlean/Makefile)
- [packages/phoenix-sqlean/cibuildwheel.toml](packages/phoenix-sqlean/cibuildwheel.toml)
- [packages/phoenix-sqlean/scripts/check-wheelhouse.py](packages/phoenix-sqlean/scripts/check-wheelhouse.py)
- [packages/phoenix-sqlean/setup.py](packages/phoenix-sqlean/setup.py)
- [packages/phoenix-sqlean/src/blob.c](packages/phoenix-sqlean/src/blob.c)
- [packages/phoenix-sqlean/src/connection.c](packages/phoenix-sqlean/src/connection.c)
- [packages/phoenix-sqlean/src/cursor.c](packages/phoenix-sqlean/src/cursor.c)
- [packages/phoenix-sqlean/src/microprotocols.c](packages/phoenix-sqlean/src/microprotocols.c)
- [packages/phoenix-sqlean/src/module.c](packages/phoenix-sqlean/src/module.c)
- [packages/phoenix-sqlean/src/module.h](packages/phoenix-sqlean/src/module.h)
- [packages/phoenix-sqlean/src/util.c](packages/phoenix-sqlean/src/util.c)
- [packages/phoenix-sqlean/tests/driver_regressions.py](packages/phoenix-sqlean/tests/driver_regressions.py)
- [pyproject.toml](pyproject.toml)
- [requirements/ci.txt](requirements/ci.txt)
- [requirements/packages/phoenix-evals.txt](requirements/packages/phoenix-evals.txt)
- [requirements/type-check.txt](requirements/type-check.txt)
- [requirements/unit-tests.txt](requirements/unit-tests.txt)
- [src/phoenix/__init__.py](src/phoenix/__init__.py)
- [src/phoenix/version.py](src/phoenix/version.py)
- [tox.ini](tox.ini)
- [uv.lock](uv.lock)

</details>



This document describes the monorepo organization of the Phoenix codebase, covering both Python and TypeScript packages, their versioning, workspace management, and interrelations. It details how Phoenix’s modular components are structured, developed, and released within a unified repository.

---

## Monorepo Overview

Phoenix employs a **dual-language monorepo** architecture:
- **Python packages** managed via `uv` workspaces [uv.lock:26-33] and tracked in release manifests [.release-please-manifest.json:1].
- **TypeScript packages** managed via `pnpm` workspaces [js/packages/phoenix-client/package.json:115-116] (with package configurations referencing workspace protocols [js/packages/phoenix-client/package.json:123-124]).

Each package maintains independent versioning while sharing version control, development tooling, and CI/CD pipelines.

### System Components to Code Entities

The following diagram maps high-level system components to their concrete Python and TypeScript code entities and monorepo directories:

```mermaid
graph TB
    subgraph "Python Monorepo Space"
        MainPkg["arize-phoenix<br/>phoenix.server.main:main<br/>src/phoenix/"]
        ClientPkg["arize-phoenix-client<br/>phoenix.client<br/>packages/phoenix-client/"]
        EvalsPkg["arize-phoenix-evals<br/>phoenix.evals<br/>packages/phoenix-evals/"]
        OtelPkg["arize-phoenix-otel<br/>phoenix.otel<br/>packages/phoenix-otel/"]
        SqleanPkg["phoenix-sqlean<br/>phoenix.sqlean<br/>packages/phoenix-sqlean/"]
    end

    subgraph "TypeScript Monorepo Space"
        TSClient["@arizeai/phoenix-client<br/>js/packages/phoenix-client/"]
        TSConfig["@arizeai/phoenix-config<br/>js/packages/phoenix-config/"]
        TSMCP["@arizeai/phoenix-mcp<br/>js/packages/phoenix-mcp/"]
        TSCLI["@arizeai/phoenix-cli<br/>js/packages/phoenix-cli/"]
    end

    subgraph "Schemas & Artifacts"
        OpenAPI["schemas/openapi.json"]
    end

    MainPkg -.-> ClientPkg
    MainPkg -.-> EvalsPkg
    MainPkg -.-> OtelPkg
    MainPkg -.-> SqleanPkg
    TSClient -- "openapi-typescript" --> OpenAPI
    TSClient -- "workspace:*" --> TSConfig
    TSMCP -- "workspace:*" --> TSClient
    TSCLI -- "workspace:*" --> TSClient
```

**Sources:** [.release-please-manifest.json:1](), [pyproject.toml:84-85](), [uv.lock:26-33](), [js/packages/phoenix-client/package.json:115-124]()

---

## Python Package Structure

The Python ecosystem comprises several core packages sharing the `phoenix` namespace. They are coordinated through `uv` workspace manifests [.release-please-manifest.json:1] and `uv.lock` [uv.lock:26-33].

### Main Package: `arize-phoenix`

This core package implements the Phoenix web application server, background daemons, storage handlers, and API layers [pyproject.toml:23-80].

| Attribute          | Value                         |
|--------------------|-------------------------------|
| Package Name       | `arize-phoenix`               |
| Version            | `20.24.0`                     |
| Location           | `src/phoenix/`                |
| Python Support     | `>=3.11, <3.15`               |

**Key Implementation Details:**
- **Entry Points:** Configured under `[project.scripts]` to launch via `arize-phoenix = "phoenix.server.main:main"` and `phoenix = "phoenix.server.main:main"` [pyproject.toml:83-85].
- **Namespace Extension:** Utilizes `pkgutil.extend_path` in `src/phoenix/__init__.py` to support multi-package namespace sharing [src/phoenix/__init__.py:5].
- **Database Subsystem Dependencies:** Integrates `sqlalchemy`, `alembic`, `aiosqlite`, and `arize-phoenix-sqlean` [pyproject.toml:50-55].

**Sources:** [src/phoenix/version.py:1](), [pyproject.toml:23-86](), [src/phoenix/__init__.py:1-5]()

### Client Package: `arize-phoenix-client`

The programmatic client library for interacting with Phoenix REST and GraphQL endpoints [packages/phoenix-client/pyproject.toml:2-4].

| Attribute          | Value                         |
|--------------------|-------------------------------|
| Package Name       | `arize-phoenix-client`        |
| Version            | `3.5.0`                       |
| Location           | `packages/phoenix-client/`    |

**Key Implementation Details:**
- Exposes `pytest` plugin entry points under `[project.entry-points.pytest11]` [packages/phoenix-client/pyproject.toml:51-52].
- Registers Harbor job runner integration via `[project.entry-points."harbor.plugins"]` [packages/phoenix-client/pyproject.toml:55-56].

**Sources:** [.release-please-manifest.json:1](), [packages/phoenix-client/pyproject.toml:2-56]()

### Evaluations Package: `arize-phoenix-evals`

Provides the server-side and client-side evaluation framework for LLM responses [packages/phoenix-evals/pyproject.toml:2-3].

| Attribute          | Value                      |
|--------------------|----------------------------|
| Package Name       | `arize-phoenix-evals`      |
| Version            | `3.9.2`                    |
| Location           | `packages/phoenix-evals/`  |

**Key Implementation Details:**
- Relies on `openinference-semantic-conventions`, `openinference-instrumentation`, and `opentelemetry-api` [packages/phoenix-evals/pyproject.toml:31-34].
- Implements async execution logic, rate limiting, and evaluation templates [packages/phoenix-evals/CHANGELOG.md:1-115].

**Sources:** [.release-please-manifest.json:1](), [packages/phoenix-evals/pyproject.toml:2-34](), [packages/phoenix-evals/CHANGELOG.md:1-115]()

### OpenTelemetry Package: `arize-phoenix-otel`

Provides specialized OpenTelemetry trace collection and exporter helpers.

| Attribute          | Value                      |
|--------------------|----------------------------|
| Package Name       | `arize-phoenix-otel`       |
| Version            | `0.17.2`                   |
| Location           | `packages/phoenix-otel/`   |

**Sources:** [.release-please-manifest.json:1]()

### SQLite Extension Package: `phoenix-sqlean`

A specialized extension package providing `sqlean` SQLite functions and modules required for advanced trace filtering and JSON operations within the database layer [pyproject.toml:55].

| Attribute          | Value                      |
|--------------------|----------------------------|
| Package Name       | `phoenix-sqlean`           |
| Version            | `0.2.1`                    |
| Location           | `packages/phoenix-sqlean/` |

**Sources:** [.release-please-manifest.json:1](), [pyproject.toml:55]()

---

## TypeScript Package Structure

The TypeScript packages reside in `js/packages/` and are managed through `pnpm` workspaces [js/packages/phoenix-client/package.json:123-124].

### TypeScript Client Package: `@arizeai/phoenix-client`

| Attribute          | Value                         |
|--------------------|-------------------------------|
| Package Name       | `@arizeai/phoenix-client`     |
| Version            | `7.16.2`                      |
| Location           | `js/packages/phoenix-client/` |

**Key Scripts & Build Flow:**
- `generate`: Invokes `openapi-typescript` against `schemas/openapi.json` to generate type definitions in `src/__generated__/api/v1.ts` [js/packages/phoenix-client/package.json:112].
- `build`: Compiles TypeScript outputs for both ESM and CommonJS distributions [js/packages/phoenix-client/package.json:36-43,110].

**Sources:** [js/packages/phoenix-client/package.json:1-175]()

### Model Context Protocol Package: `@arizeai/phoenix-mcp`

| Attribute          | Value                         |
|--------------------|-------------------------------|
| Package Name       | `@arizeai/phoenix-mcp`        |
| Version            | `4.3.17`                      |
| Location           | `js/packages/phoenix-mcp/`    |

**Features:**
- Implements the Model Context Protocol server, linking AI assistants to Phoenix datasets and traces [js/packages/phoenix-mcp/package.json:2-4].

**Sources:** [js/packages/phoenix-mcp/package.json:1-48]()

---

## Version Manifest & Release Automation

Monorepo package versions are centrally registered in `.release-please-manifest.json` [.release-please-manifest.json:1] to coordinate automated releases via Release Please.

```mermaid
graph LR
    subgraph "Release Flow"
        Manifest[".release-please-manifest.json"] --> RP["Release Please Automation"]
        RP --> PyPI["PyPI Registry<br/>arize-phoenix*"]
        RP --> NPM["NPM Registry<br/>@arizeai/phoenix*"]
    end
```

**Current Manifest Version Table:**

| Package Name | Version |
| :--- | :--- |
| `arize-phoenix` (Root) | `20.24.0` [src/phoenix/version.py:1]() |
| `arize-phoenix-evals` | `3.9.2` [.release-please-manifest.json:1]() |
| `arize-phoenix-otel` | `0.17.2` [.release-please-manifest.json:1]() |
| `arize-phoenix-client` | `3.5.0` [.release-please-manifest.json:1]() |
| `phoenix-sqlean` | `0.2.1` [.release-please-manifest.json:1]() |

**Sources:** [.release-please-manifest.json:1](), [src/phoenix/version.py:1]()

---

## Dependency Management & Tooling

### Python (`uv`)
- Managed via `pyproject.toml` [pyproject.toml:1-80] and `uv.lock` [uv.lock:1-33].
- Uses dependency groups for testing, linting (`ruff`), and type checking (`mypy`) [pyproject.toml:87-187].
- Implements `exclude-newer-package` rules in `uv.lock` to lock internal dependencies against premature upgrades [uv.lock:18-23].

### TypeScript (`pnpm`)
- Workspace packages reference each other locally using the `workspace:*` specifier [js/packages/phoenix-client/package.json:123-124].
- Exact dependency resolution is tracked via `js/pnpm-lock.yaml`.

**Sources:** [pyproject.toml:1-187](), [uv.lock:1-33](), [js/packages/phoenix-client/package.json:121-129]()

---

# Page: Core Concepts & Terminology

# Core Concepts & Terminology

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cspell.json](cspell.json)
- [docs/phoenix/get-started.mdx](docs/phoenix/get-started.mdx)
- [docs/phoenix/get-started/get-started-evaluations.mdx](docs/phoenix/get-started/get-started-evaluations.mdx)
- [docs/phoenix/get-started/get-started-tracing.mdx](docs/phoenix/get-started/get-started-tracing.mdx)
- [docs/phoenix/sdk-api-reference.mdx](docs/phoenix/sdk-api-reference.mdx)
- [docs/phoenix/sdk-api-reference/python/arize-phoenix-otel.mdx](docs/phoenix/sdk-api-reference/python/arize-phoenix-otel.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/overview.mdx](docs/phoenix/sdk-api-reference/rest-api/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/overview.mdx](docs/phoenix/sdk-api-reference/typescript/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx)
- [docs/phoenix/tracing/concepts-tracing/otel-openinference/phoenix-otel-helpers.mdx](docs/phoenix/tracing/concepts-tracing/otel-openinference/phoenix-otel-helpers.mdx)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing.mdx)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-using-phoenix-otel.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-using-phoenix-otel.mdx)
- [docs/snippets/agent-assisted-onboarding-prereq.mdx](docs/snippets/agent-assisted-onboarding-prereq.mdx)
- [docs/snippets/agent-assisted-onboarding.mdx](docs/snippets/agent-assisted-onboarding.mdx)
- [docs/snippets/connect-to-phoenix-env.mdx](docs/snippets/connect-to-phoenix-env.mdx)
- [scripts/data/generate_traces.py](scripts/data/generate_traces.py)
- [src/phoenix/config.py](src/phoenix/config.py)
- [src/phoenix/db/alembic.ini](src/phoenix/db/alembic.ini)
- [src/phoenix/db/engines.py](src/phoenix/db/engines.py)
- [src/phoenix/db/migrate.py](src/phoenix/db/migrate.py)
- [src/phoenix/db/migrations/__init__.py](src/phoenix/db/migrations/__init__.py)
- [src/phoenix/db/migrations/env.py](src/phoenix/db/migrations/env.py)
- [src/phoenix/db/migrations/versions/10460e46d750_datasets.py](src/phoenix/db/migrations/versions/10460e46d750_datasets.py)
- [src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py](src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py)
- [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py](src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py)
- [src/phoenix/db/models.py](src/phoenix/db/models.py)
- [src/phoenix/server/api/context.py](src/phoenix/server/api/context.py)
- [src/phoenix/server/api/dataloaders/__init__.py](src/phoenix/server/api/dataloaders/__init__.py)
- [src/phoenix/server/api/dataloaders/trace_root_spans.py](src/phoenix/server/api/dataloaders/trace_root_spans.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/routers/v1/experiment_evaluations.py](src/phoenix/server/api/routers/v1/experiment_evaluations.py)
- [src/phoenix/server/api/routers/v1/experiment_runs.py](src/phoenix/server/api/routers/v1/experiment_runs.py)
- [src/phoenix/server/api/routers/v1/experiments.py](src/phoenix/server/api/routers/v1/experiments.py)
- [src/phoenix/server/api/types/Experiment.py](src/phoenix/server/api/types/Experiment.py)
- [src/phoenix/server/api/types/MimeType.py](src/phoenix/server/api/types/MimeType.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/ProjectSession.py](src/phoenix/server/api/types/ProjectSession.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/settings.py](src/phoenix/settings.py)
- [src/phoenix/trace/fixtures.py](src/phoenix/trace/fixtures.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [src/phoenix/trace/utils.py](src/phoenix/trace/utils.py)
- [tests/unit/_helpers.py](tests/unit/_helpers.py)
- [tests/unit/db/test_engines.py](tests/unit/db/test_engines.py)
- [tests/unit/server/api/routers/v1/test_experiments.py](tests/unit/server/api/routers/v1/test_experiments.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/types/test_Experiment.py](tests/unit/server/api/types/test_Experiment.py)
- [tests/unit/server/api/types/test_Project.py](tests/unit/server/api/types/test_Project.py)
- [tests/unit/server/api/types/test_ProjectSession.py](tests/unit/server/api/types/test_ProjectSession.py)
- [tests/unit/server/api/types/test_Span.py](tests/unit/server/api/types/test_Span.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)
- [tutorials/quickstarts/python_quickstart.ipynb](tutorials/quickstarts/python_quickstart.ipynb)

</details>



This page defines the core data entities, domain concepts, and architectural abstractions used throughout Phoenix. It serves as a comprehensive conceptual reference for onboarding engineers, detailing the primary data structures involved in tracing LLM applications, managing datasets, executing experiments, and evaluating model outputs.

---

## Overview of Core Entities

Phoenix's backend persistence and GraphQL API layers are built around several interconnected relational models and types that enable deep observability, experimentation, and evaluation of AI applications.

### Entity Relationship Diagram

```mermaid
graph TB
ProjectEntity["models.Project"] -->|"contains"| TraceEntity["models.Trace"]
TraceEntity -->|"contains"| SpanEntity["models.Span"]
SpanEntity -->|"parent_id"| SpanEntity
SessionEntity["models.ProjectSession"] -->|"groups"| TraceEntity
ProjectEntity -->|"has"| SessionEntity

DatasetEntity["models.Dataset"] -->|"versioned by"| DatasetVersionEntity["models.DatasetVersion"]
DatasetEntity -->|"contains"| DatasetExampleEntity["models.DatasetExample"]
DatasetExampleEntity -->|"versioned by"| DatasetExampleRevisionEntity["models.DatasetExampleRevision"]
DatasetExampleRevisionEntity -->|"belongs to"| DatasetVersionEntity
DatasetExampleEntity -->|"references"| SpanEntity

ExperimentEntity["models.Experiment"] -->|"uses"| DatasetVersionEntity
ExperimentEntity -->|"produces"| ExperimentRunEntity["models.ExperimentRun"]
ExperimentRunEntity -->|"for"| DatasetExampleEntity
ExperimentRunEntity -->|"creates"| TraceEntity

SpanEntity -->|"annotated by"| SpanAnnotationEntity["models.SpanAnnotation"]
TraceEntity -->|"annotated by"| TraceAnnotationEntity["models.TraceAnnotation"]
ExperimentRunEntity -->|"annotated by"| ExperimentRunAnnotationEntity["models.ExperimentRunAnnotation"]

EvaluatorEntity["models.Evaluator"] -->|"subtype"| LLMEvaluatorEntity["models.LLMEvaluator"]
EvaluatorEntity -->|"subtype"| CodeEvaluatorEntity["models.CodeEvaluator"]

LLMEvaluatorEntity -->|"uses"| PromptEntity["models.Prompt"]
LLMEvaluatorEntity -->|"uses"| PromptVersionEntity["models.PromptVersion"]

PromptEntity -->|"has versions"| PromptVersionEntity
```

Sources: `[src/phoenix/db/models.py:602-712]()`, `[src/phoenix/db/models.py:887-1163]()`, `[src/phoenix/db/models.py:1644-2087]()`, `[src/phoenix/db/models.py:1165-1428]()`

---

## Traces and Spans

### Trace

A **Trace** represents a complete, end-to-end execution flow through an LLM application. Each trace is uniquely identified by a `trace_id` and belongs to a **Project**. Traces act as the high-level containers for observability data.

- **Implementation**: The `models.Trace` SQLAlchemy ORM model defines columns such as `trace_id`, `project_rowid`, `start_time`, and `end_time`. `[src/phoenix/db/models.py:659-712]()`
- **Data Flow**: Traces are ingested during runtime through OpenTelemetry protocols (OTLP) via HTTP or gRPC and persisted to the underlying database. `[src/phoenix/server/app.py:171-172]()`
- **Key Class**: `models.Trace` manages database representation, while the GraphQL `Trace` type exposes it for client queries. `[src/phoenix/server/api/types/Trace.py:1-50]()`

| Property | Type | Description |
|----------|------|-------------|
| `trace_id` | `str` | Globally unique identifier for the trace |
| `project_rowid` | `int` | Foreign key referencing the owning project |
| `start_time` | `datetime` | Timestamp when the trace execution began |
| `end_time` | `datetime` | Timestamp when the trace execution completed |

Sources: `[src/phoenix/db/models.py:659-712]()`, `[src/phoenix/server/api/types/Trace.py:1-50]()`

---

### Span

A **Span** is the fundamental unit of work within a trace. Spans form a hierarchical tree structure via the `parent_id` foreign key relationship, where root spans have `parent_id=None`. Spans capture detailed execution metadata including inputs, outputs, token counts, timing, and error status.

- **Implementation**: The `models.Span` ORM model stores span data, including identifiers, names, timing, status codes, and OpenTelemetry attributes. `[src/phoenix/db/models.py:714-885]()`
- **Data Flow**: Spans are collected via distributed tracing instrumentation, processed by batch inserters, and fetched via `DataLoaders` to prevent N+1 queries. `[src/phoenix/server/api/dataloaders/__init__.py:85-86]()`
- **Key Classes**:
  - `models.Span` defines the database schema. `[src/phoenix/db/models.py:714-885]()`
  - GraphQL `Span` type exposes fields with data loader batching. `[src/phoenix/server/api/types/Span.py:127-150]()`
  - `SpanKind` enum categorizes span operations for UI rendering and analytics. `[src/phoenix/server/api/types/Span.py:57-80]()`

| Property | Type | Description |
|----------|------|-------------|
| `id` | `SpanRowId` | Internal database row ID |
| `parent_id` | `Optional[ID]` | Parent span identifier (null for root spans) |
| `name` | `str` | Human-readable operation name |
| `span_kind` | `SpanKind` | Category of work (LLM, RETRIEVER, TOOL, etc.) |
| `start_time` | `datetime` | Execution start timestamp |
| `end_time` | `datetime` | Execution end timestamp |
| `status_code` | `SpanStatusCode` | Status code (`OK`, `ERROR`, `UNSET`) |

Sources: `[src/phoenix/db/models.py:714-885]()`, `[src/phoenix/server/api/dataloaders/__init__.py:85-86]()`, `[src/phoenix/server/api/types/Span.py:127-150]()`, `[src/phoenix/server/api/types/Span.py:57-80]()`

---

### Natural Language to Code Entity Mapping: Tracing

This diagram maps high-level tracing concepts to specific code entities within the Phoenix codebase.

```mermaid
graph LR
subgraph "Natural Language Space"
    UserTrace["'A full user request'"]
    UserSpan["'A specific model call'"]
    UserProject["'The production app'"]
end

subgraph "Code Entity Space"
    TraceEntity["models.Trace"]
    SpanEntity["models.Span"]
    ProjectEntity["models.Project"]
    
    GqlTrace["GraphQL Trace"]
    GqlSpan["GraphQL Span"]
    
    IngestFunc["BulkInserter"]
end

UserTrace --- TraceEntity
UserSpan --- SpanEntity
UserProject --- ProjectEntity

TraceEntity --- GqlTrace
SpanEntity --- GqlSpan
SpanEntity --- IngestFunc
```

Sources: `[src/phoenix/db/models.py:602-885]()`, `[src/phoenix/server/api/types/Span.py:127-150]()`, `[src/phoenix/server/api/types/Trace.py:1-50]()`, `[src/phoenix/db/bulk_inserter.py:1-50]()`

---

### SpanKind Enumeration

`SpanKind` categorizes the nature of work represented by a span, driving filtering, UI representation, and evaluation logic.

| Value | Description |
|-------|-------------|
| `CHAIN` | Orchestration or workflow span |
| `LLM` | LLM inference invocation |
| `RETRIEVER` | Document retrieval operation |
| `RERANKER` | Document reranking operation |
| `EMBEDDING` | Embedding generation |
| `TOOL` | Tool or function execution |
| `AGENT` | Agent decision-making loop |
| `EVALUATOR` | Evaluation logic execution |
| `GUARDRAIL` | Guardrail validation check |
| `UNKNOWN` | Uncategorized operation |

- Defined as `SpanKind` enum in `src/phoenix/server/api/types/Span.py`. `[src/phoenix/server/api/types/Span.py:57-80]()`
- Supports case-insensitive normalization and fallback handling.

Sources: `[src/phoenix/server/api/types/Span.py:57-80]()`

---

## Projects and Sessions

### Project

A **Project** is the top-level organizational namespace in Phoenix. All traces, sessions, datasets, and experiments are scoped to a project, allowing isolation between different applications or environments.

- **Implementation**:
  - `models.Project` ORM model stores project metadata. `[src/phoenix/db/models.py:602-640]()`
  - GraphQL `Project` type exposes project fields and aggregate metrics. `[src/phoenix/server/api/types/Project.py:61-122]()`
  - Default project name is provided by `DEFAULT_PROJECT_NAME`. `[src/phoenix/config.py:60-60]()`

| Property | Type | Description |
|----------|------|-------------|
| `id` | `int` | Unique project identifier |
| `name` | `str` | Project name |
| `description` | `Optional[str]` | Optional project description |

Sources: `[src/phoenix/db/models.py:602-640]()`, `[src/phoenix/server/api/types/Project.py:61-122]()`, `[src/phoenix/config.py:60-60]()`

---

### ProjectSession

A **ProjectSession** groups related traces into a logical unit—typically representing a multi-turn user conversation or workflow session within a project.

- **Implementation**:
  - `models.ProjectSession` stores session metadata. `[src/phoenix/db/models.py:642-657]()`
  - GraphQL `ProjectSession` type exposes session properties and aggregates. `[src/phoenix/server/api/types/ProjectSession.py:1-50]()`
  - Session filtering utilizes a custom domain-specific language (DSL). `[src/phoenix/server/api/types/Project.py:77-83]()`

| Property | Type | Description |
|----------|------|-------------|
| `id` | `int` | Unique session identifier |
| `project_id` | `int` | Foreign key to owning project |
| `name` | `str` | Session name or identifier |
| `start_time` | `datetime` | Session start timestamp |
| `end_time` | `datetime` | Session end timestamp |

Sources: `[src/phoenix/db/models.py:642-657]()`, `[src/phoenix/server/api/types/ProjectSession.py:1-50]()`, `[src/phoenix/server/api/types/Project.py:77-83]()`

---

## Datasets and Experiments

### Dataset

A **Dataset** contains a versioned collection of structured examples used for evaluations and benchmarking experiments. Datasets support example revisions and split management.

- **Implementation**:
  - `models.Dataset` and `models.DatasetVersion` manage datasets and versions. `[src/phoenix/db/models.py:887-936]()`
  - `models.DatasetExample` stores individual benchmark examples. `[src/phoenix/db/models.py:938-964]()`
  - GraphQL `Dataset` type exposes dataset entities and relationships. `[src/phoenix/server/api/types/Dataset.py:44-146]()`

| Property | Type | Description |
|----------|------|-------------|
| `id` | `int` | Unique dataset identifier |
| `name` | `str` | Dataset name |
| `description` | `Optional[str]` | Optional description |

Sources: `[src/phoenix/db/models.py:887-936]()`, `[src/phoenix/server/api/types/Dataset.py:44-146]()`

---

### Experiment

An **Experiment** executes evaluations of task functions over a specific dataset version, tracking individual run results, performance metrics, and comparisons.

- **Implementation**:
  - `models.Experiment` stores experiment configurations and metadata. `[src/phoenix/db/models.py:1041-1100]()`
  - The `ExperimentRunner` daemon handles execution of experiment jobs. `[src/phoenix/server/app.py:126-126]()`
  - GraphQL `Experiment` type exposes run results. `[src/phoenix/server/api/types/Experiment.py:1-50]()`

Sources: `[src/phoenix/db/models.py:1041-1100]()`, `[src/phoenix/server/app.py:126-126]()`, `[src/phoenix/server/api/types/Experiment.py:1-50]()`

---

## Annotations

Annotations attach feedback, labels, scores, or metadata to spans, traces, or experiment runs. They can be generated by humans, LLM judges, or code-based evaluators.

### Annotation Interface (GraphQL)

The core annotation types share a common interface defining feedback attributes:

| Property | Type | Description |
|----------|------|-------------|
| `name` | `String!` | Annotation name (e.g., `hallucination`, `qa_correctness`) |
| `annotatorKind` | `AnnotatorKind!` | Originator kind (`LLM`, `HUMAN`, `CODE`) |
| `label` | `String` | Categorical label value |
| `score` | `Float` | Numeric score value |

- **Implementation**:
  - `models.SpanAnnotation` `[src/phoenix/db/models.py:1359-1428]()`
  - `models.TraceAnnotation` `[src/phoenix/db/models.py:1288-1357]()`
  - `models.ExperimentRunAnnotation` `[src/phoenix/db/models.py:1165-1286]()`

Sources: `[src/phoenix/db/models.py:1165-1428]()`, `[src/phoenix/server/api/types/SpanAnnotation.py:1-50]()`

---

## Evaluators

Evaluators assess LLM outputs by applying metrics, prompt-based grading, or programmatic assertion functions.

### Natural Language to Code Entity Mapping: Evaluation

```mermaid
graph LR
subgraph "Natural Language Space"
    UserEval["'An LLM-based judge'"]
    UserMapping["'Input field mapping'"]
    UserResult["'The evaluation score'"]
end

subgraph "Code Entity Space"
    LLMEval["models.LLMEvaluator"]
    CodeEval["models.CodeEvaluator"]
    InputMap["InputMapping"]
    Annotation["models.SpanAnnotation"]
    
    TemplateInfer["infer_input_schema_from_template"]
end

UserEval --- LLMEval
UserEval --- CodeEval
UserMapping --- InputMap
UserMapping --- TemplateInfer
UserResult --- Annotation
```

Sources: `[src/phoenix/db/models.py:1732-1846]()`, `[src/phoenix/db/models.py:1165-1428]()`, `[src/phoenix/db/types/evaluators.py:1-1]()`, `[src/phoenix/server/api/evaluators.py:39-45]()`

---

### LLMEvaluator

An `LLMEvaluator` prompts an LLM with structured criteria and templates, parsing the output into quantitative scores or qualitative labels.

- **Implementation**:
  - Stored in `models.LLMEvaluator`. `[src/phoenix/db/models.py:1732-1846]()`
  - References prompt templates and version configurations.
  - Conforms to annotation configurations defined in `AnnotationConfig`. `[src/phoenix/db/types/annotation_configs.py:57-64]()`

Sources: `[src/phoenix/db/models.py:1732-1846]()`, `[src/phoenix/server/api/types/Evaluator.py:80-86]()`, `[src/phoenix/db/types/annotation_configs.py:57-64]()`

---

## Prompts and Versions

### Prompt

A **Prompt** organizes prompt templates into version-controlled entities, enabling iterative prompt engineering and tracking.

- **Implementation**:
  - `models.Prompt` stores prompt metadata and links to version history. `[src/phoenix/db/models.py:1866-1896]()`

Sources: `[src/phoenix/db/models.py:1866-1896]()`

### PromptVersion

A **PromptVersion** contains the concrete template definition, model invocation parameters, and response format specifications.

- **Implementation**:
  - Stored in `models.PromptVersion`. `[src/phoenix/db/models.py:1898-2087]()`
  - Supports chat and text templates, variables, and model provider configurations.
  - Exposed via the GraphQL `PromptVersion` type. `[src/phoenix/server/api/types/PromptVersion.py:123-123]()`

Sources: `[src/phoenix/db/models.py:1898-2087]()`, `[src/phoenix/server/api/types/PromptVersion.py:1-50]()`

---

## Summary Table of Core Concepts

| Concept | Description | Key Code Entities |
|---------|-------------|-------------------|
| Project | Top-level container for all artifacts | `models.Project`, GraphQL `Project` |
| ProjectSession | Grouping of related traces (e.g., user session) | `models.ProjectSession`, GraphQL `ProjectSession` |
| Trace | Complete LLM request execution flow | `models.Trace`, GraphQL `Trace` |
| Span | Fundamental unit of work within a trace | `models.Span`, GraphQL `Span`, `SpanKind` enum |
| Dataset | Versioned collection of benchmark examples | `models.Dataset`, `models.DatasetVersion`, GraphQL `Dataset` |
| Experiment | Execution of evaluations over a dataset version | `models.Experiment`, GraphQL `Experiment` |
| ExperimentRun | Single task example run within an experiment | `models.ExperimentRun`, GraphQL `ExperimentRun` |
| Annotation | Feedback, scores, or metadata on spans or runs | `models.SpanAnnotation`, `models.TraceAnnotation`, `models.ExperimentRunAnnotation` |
| Evaluator | Logic applying scoring or classification | `models.Evaluator`, `models.LLMEvaluator`, `models.CodeEvaluator` |
| Prompt | Versioned prompt template collection | `models.Prompt`, `models.PromptVersion`, GraphQL `Prompt` |

Sources: `[src/phoenix/db/models.py:602-2087]()`, `[src/phoenix/server/api/types/Span.py:57-267]()`, `[src/phoenix/server/api/types/Trace.py:1-50]()`

---

# Page: Server Architecture

# Server Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cspell.json](cspell.json)
- [scripts/data/generate_traces.py](scripts/data/generate_traces.py)
- [src/phoenix/config.py](src/phoenix/config.py)
- [src/phoenix/db/engines.py](src/phoenix/db/engines.py)
- [src/phoenix/server/api/context.py](src/phoenix/server/api/context.py)
- [src/phoenix/server/api/dataloaders/__init__.py](src/phoenix/server/api/dataloaders/__init__.py)
- [src/phoenix/server/api/dataloaders/trace_root_spans.py](src/phoenix/server/api/dataloaders/trace_root_spans.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/types/Experiment.py](src/phoenix/server/api/types/Experiment.py)
- [src/phoenix/server/api/types/MimeType.py](src/phoenix/server/api/types/MimeType.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/ProjectSession.py](src/phoenix/server/api/types/ProjectSession.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/trace/fixtures.py](src/phoenix/trace/fixtures.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [src/phoenix/trace/utils.py](src/phoenix/trace/utils.py)
- [tests/unit/_helpers.py](tests/unit/_helpers.py)
- [tests/unit/db/test_engines.py](tests/unit/db/test_engines.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/types/test_Experiment.py](tests/unit/server/api/types/test_Experiment.py)
- [tests/unit/server/api/types/test_Project.py](tests/unit/server/api/types/test_Project.py)
- [tests/unit/server/api/types/test_ProjectSession.py](tests/unit/server/api/types/test_ProjectSession.py)
- [tests/unit/server/api/types/test_Span.py](tests/unit/server/api/types/test_Span.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)

</details>



## Purpose and Scope

This document provides a high-level overview of the Phoenix server architecture, outlining its FastAPI application structure, API layers, data storage approach, and background services. The Phoenix server is designed to:

- Serve HTTP/gRPC endpoints for ingesting OpenTelemetry traces via the OTLP protocol.
- Host GraphQL and REST APIs for querying and managing observability, evaluation, and experiment data.
- Serve the React-based frontend web UI static assets.
- Manage asynchronous background daemons for batch insertions, cost calculations, experiment execution, and model synchronization.

This is a parent-level overview. For deep technical details, refer to the individual child subsystems:

- [Application Server & Configuration](#2.1) — FastAPI app structure, startup lifecycle, configuration management, and session handling.
- [GraphQL API](#2.2) — Strawberry-based schema, resolvers, context injection, and DataLoader N+1 query optimization.
- [REST API & OpenAPI](#2.3) — REST endpoints, OpenAPI specs, and v1 routers for spans, traces, datasets, and prompts.
- [OTLP Ingestion & gRPC Server](#2.4) — Ingestion via OpenTelemetry OTLP over HTTP and gRPC, with the `GrpcServer` and `BulkInserter`.
- [Database Layer & Migrations](#2.5) — SQLAlchemy ORM models, Alembic migrations, PostgreSQL and SQLite support, and `phoenix-sqlean`.
- [Authentication & Authorization](#2.6) — OAuth2, LDAP, RBAC, API keys, and JWT store management.
- [Cost Tracking & Model Pricing](#2.7) — Model cost manifests, `GenerativeModelStore`, and `SpanCostCalculator`.

**Sources:** [src/phoenix/server/main.py:17-44](), [src/phoenix/server/app.py:1-177](), [src/phoenix/server/api/context.py:40-164]()

---

## Application Lifecycle & Startup

The server initializes by configuring logging and settings [src/phoenix/server/main.py:17-43](), establishing an asynchronous database engine [src/phoenix/db/engines.py:109-132](), constructing the FastAPI application via `create_app()` [src/phoenix/server/app.py:1-177](), and spinning up background daemon tasks within its lifespan context.

```mermaid
sequenceDiagram
    participant CLI as "main() [src/phoenix/server/main.py]"
    participant Engine as "create_async_engine() [src/phoenix/db/engines.py]"
    participant App as "create_app() [src/phoenix/server/app.py]"
    participant Lifespan as "FastAPI Lifespan Context"
    participant Daemons as "Background Daemons"

    CLI->>Engine: Initialize Async Engine & Migrations
    CLI->>App: Build FastAPI App & Middleware Stack
    App->>Lifespan: Register Lifespan Manager
    CLI->>Lifespan: Start Uvicorn Server
    Lifespan->>Daemons: Start BulkInserter, GrpcServer, SpanCostCalculator
    Note over Lifespan,Daemons: Server ready to ingest telemetry and serve requests
```
**Sources:** [src/phoenix/server/main.py:17-44](), [src/phoenix/db/engines.py:109-132]()

For further details on configuration management, environment variables, the `serve` command, and boot sequences, see [Application Server & Configuration](#2.1).

---

## API Subsystems

Phoenix provides three primary interface layers to support programmatic clients, UIs, and telemetry collectors:

- **GraphQL API**: Powered by `strawberry` and structured around Relay-compliant nodes and connections. Resolvers are organized in modules such as `src/phoenix/server/api/queries.py` [src/phoenix/server/api/queries.py:1-154](). For details, see [GraphQL API](#2.2).
- **REST API (v1)**: Exposes endpoints for spans, traces, datasets, prompts, and experiments using FastAPI routers [src/phoenix/server/app.py:98-109](). For details, see [REST API & OpenAPI](#2.3).
- **OTLP Ingestion & gRPC Server**: Ingests OpenTelemetry traces via `GrpcServer` and bulk insertion pipelines [src/phoenix/server/app.py:90-134](). For details, see [OTLP Ingestion & gRPC Server](#2.4).

**Sources:** [src/phoenix/server/app.py:98-134](), [src/phoenix/server/api/queries.py:1-154]()

---

## Data Storage & Database Layer

Phoenix uses SQLAlchemy 2.0 to support both **SQLite** (leveraging the `phoenix-sqlean` extension package for advanced math and text functions) and **PostgreSQL** [src/phoenix/db/engines.py:14-28](). 

Database migrations are managed via Alembic. To eliminate N+1 query performance bottlenecks during complex GraphQL resolutions, Phoenix relies heavily on the `DataLoader` pattern implemented across `src/phoenix/server/api/dataloaders/__init__.py` [src/phoenix/server/api/dataloaders/__init__.py:1-117] and injected via the request `Context` [src/phoenix/server/api/context.py:40-164]().

For details on ORM models, database schemas, and DDL tools, see [Database Layer & Migrations](#2.5).

**Sources:** [src/phoenix/db/engines.py:14-28](), [src/phoenix/server/api/context.py:40-164](), [src/phoenix/server/api/dataloaders/__init__.py:1-117]()

---

## Authentication, Authorization & Cost Tracking

The server integrates robust security and tracking subsystems:
- **Authentication & Authorization**: Supports OAuth2 flows, LDAP, local credentials, and role-based access control (RBAC) governed by `JwtStore` and bearer token middleware. For details, see [Authentication & Authorization](#2.6).
- **Cost Tracking & Model Pricing**: Computes LLM token costs dynamically using `SpanCostCalculator` backed by model pricing manifests and the `GenerativeModelStore` daemon [src/phoenix/server/app.py:123-128](). For details, see [Cost Tracking & Model Pricing](#2.7).

**Sources:** [src/phoenix/server/app.py:123-128]()

---

## Architecture Bridging Diagrams

### Code-to-System Mapping: Ingestion Path

```mermaid
graph LR
    subgraph "Client / Exporter"
        OTLP["OTLP Exporter"]
    end

    subgraph "Server Ingestion Layer"
        GRPC["GrpcServer [src/phoenix/server/grpc_server.py]"]
        REST["REST API v1 [src/phoenix/server/api/routers/v1]"]
    end

    subgraph "Processing Pipeline"
        BI["BulkInserter [src/phoenix/db/bulk_inserter.py]"]
    end

    subgraph "Persistence"
        DB["SQLAlchemy AsyncEngine [src/phoenix/db/engines.py]"]
    end

    OTLP -->|gRPC OTLP| GRPC
    OTLP -->|HTTP OTLP| REST
    GRPC --> BI
    REST --> BI
    BI --> DB
```
**Sources:** [src/phoenix/server/app.py:90-134](), [src/phoenix/db/engines.py:14-132]()

### Code-to-System Mapping: GraphQL Query Execution

```mermaid
graph TD
    subgraph "HTTP Request"
        REQ["Starlette Request [src/phoenix/server/app.py]"]
    end

    subgraph "GraphQL Router"
        GQL["GraphQLRouter [src/strawberry/fastapi]"]
        CTX["build_context() [src/phoenix/server/api/context.py]"]
    end

    subgraph "Query Resolution"
        QUERY["queries.py [src/phoenix/server/api/queries.py]"]
        LOADERS["DataLoaders [src/phoenix/server/api/dataloaders/__init__.py]"]
    end

    subgraph "Database"
        ORM["SQLAlchemy ORM [src/phoenix/db/models.py]"]
    end

    REQ --> GQL
    GQL --> CTX
    CTX --> QUERY
    QUERY --> LOADERS
    LOADERS --> ORM
```
**Sources:** [src/phoenix/server/app.py:1-177](), [src/phoenix/server/api/context.py:119-164](), [src/phoenix/server/api/queries.py:1-154](), [src/phoenix/server/api/dataloaders/__init__.py:1-117]()

---

## Notebook Session Management

For interactive development within Jupyter or cloud notebooks, Phoenix provides the `Session` abstraction (`ThreadSession` and `ProcessSession`) which maintains a 1-to-1 shared state with the Phoenix App service [src/phoenix/session/session.py:70-218]().

**Sources:** [src/phoenix/session/session.py:70-218]()

---

# Page: Application Server & Configuration

# Application Server & Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cspell.json](cspell.json)
- [docs/phoenix/self-hosting/configuration.mdx](docs/phoenix/self-hosting/configuration.mdx)
- [scripts/data/generate_traces.py](scripts/data/generate_traces.py)
- [src/phoenix/config.py](src/phoenix/config.py)
- [src/phoenix/db/engines.py](src/phoenix/db/engines.py)
- [src/phoenix/logging/_config.py](src/phoenix/logging/_config.py)
- [src/phoenix/server/api/context.py](src/phoenix/server/api/context.py)
- [src/phoenix/server/api/dataloaders/__init__.py](src/phoenix/server/api/dataloaders/__init__.py)
- [src/phoenix/server/api/dataloaders/trace_root_spans.py](src/phoenix/server/api/dataloaders/trace_root_spans.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/types/Experiment.py](src/phoenix/server/api/types/Experiment.py)
- [src/phoenix/server/api/types/MimeType.py](src/phoenix/server/api/types/MimeType.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/ProjectSession.py](src/phoenix/server/api/types/ProjectSession.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/cli/boot_message.py](src/phoenix/server/cli/boot_message.py)
- [src/phoenix/server/cli/commands/serve.py](src/phoenix/server/cli/commands/serve.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/telemetry.py](src/phoenix/server/telemetry.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/trace/fixtures.py](src/phoenix/trace/fixtures.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [src/phoenix/trace/utils.py](src/phoenix/trace/utils.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/unit/_helpers.py](tests/unit/_helpers.py)
- [tests/unit/conftest.py](tests/unit/conftest.py)
- [tests/unit/db/test_engines.py](tests/unit/db/test_engines.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/types/test_Experiment.py](tests/unit/server/api/types/test_Experiment.py)
- [tests/unit/server/api/types/test_Project.py](tests/unit/server/api/types/test_Project.py)
- [tests/unit/server/api/types/test_ProjectSession.py](tests/unit/server/api/types/test_ProjectSession.py)
- [tests/unit/server/api/types/test_Span.py](tests/unit/server/api/types/test_Span.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)
- [tests/unit/server/cli/commands/test_serve.py](tests/unit/server/cli/commands/test_serve.py)
- [tests/unit/server/cli/test_boot_message.py](tests/unit/server/cli/test_boot_message.py)
- [tests/unit/server/test_app_docs_mcp_lifespan.py](tests/unit/server/test_app_docs_mcp_lifespan.py)
- [tests/unit/server/test_app_evaluations.py](tests/unit/server/test_app_evaluations.py)
- [tests/unit/server/test_app_fastapi_dependants.py](tests/unit/server/test_app_fastapi_dependants.py)
- [tests/unit/server/test_app_fastapi_type_adapters.py](tests/unit/server/test_app_fastapi_type_adapters.py)
- [tests/unit/server/test_app_graphql_schema_build.py](tests/unit/server/test_app_graphql_schema_build.py)
- [tests/unit/server/test_app_routers.py](tests/unit/server/test_app_routers.py)
- [tests/unit/server/test_telemetry.py](tests/unit/server/test_telemetry.py)

</details>



## Purpose and Scope

This document describes the Phoenix application server architecture, including its FastAPI setup, startup lifecycle, configuration management, and session handling. The server serves as the foundation for all Phoenix HTTP/GraphQL endpoints and manages crucial background daemons and request middleware.

For details on the GraphQL API, see [GraphQL API](2.2). For REST API endpoints, see [REST API & OpenAPI](2.3). For gRPC and OTLP ingestion, see [OTLP Ingestion & gRPC Server](2.4).

Sources: [src/phoenix/server/app.py:1-177](), [src/phoenix/config.py:1-172]()

---

## Server Architecture Overview

Phoenix's server is a FastAPI application constructed and configured in `create_app()` [src/phoenix/server/app.py]() (specifically across the file where application routes and middleware are registered). It supports two primary deployment modes:

- **Thread-based server (`ThreadServer`)**: Used for environments such as interactive notebooks where the server runs in the same process but on a background thread [src/phoenix/server/thread_server.py]().
- **Process-based server (`AppService`)**: Used for production use, launched as a standalone process with full daemon management via the CLI [src/phoenix/server/main.py:17-45](), [src/phoenix/session/session.py:148-183]().

The server architecture integrates several important elements: GraphQL and REST API endpoints, gRPC OTLP trace ingestion, a React web UI served as static assets, authentication and middleware stacks, and background daemons for ingestion, trace retention, cost calculation, and experiment execution.

### Phoenix Application Server - Component Architecture

```mermaid
graph TB
    subgraph EntryPoints["Entry Points"]
        main["main()<br/>phoenix.server.main"]
        launch_app["launch_app()<br/>phoenix.session.session"]
    end
    
    subgraph ServerRuntime["Server Runtime"]
        uvicorn_server["uvicorn.Server<br/>production"]
        ThreadServerClass["ThreadServer<br/>notebook mode"]
    end
    
    subgraph AppCreation["FastAPI Application Creation"]
        create_app["create_app()"]
        FastAPIApp["FastAPI instance<br/>with lifespan"]
        lifespan_func["_lifespan()<br/>context manager"]
    end
    
    subgraph MiddlewareStack["Middleware Stack"]
        cors["CORSMiddleware<br/>allowed_origins"]
        auth_mw["AuthenticationMiddleware<br/>BearerTokenAuthBackend"]
        headers_mw["HeadersMiddleware"]
        gzip_mw["GZipMiddleware"]
        csrf_mw["RequestOriginHostnameValidator"]
        user_mw["user_fastapi_middlewares()"]
    end
    
    subgraph Routes["Mounted Routes"]
        graphql["create_graphql_router()<br/>/graphql"]
        rest_v1["create_v1_router()<br/>/v1/*"]
        auth_router["create_auth_router()<br/>/auth/*"]
        oauth2["oauth2_router<br/>/oauth2/*"]
        agents_router["create_agents_router()<br/>/agents"]
        static["StaticFiles()<br/>fallback to index.html"]
    end
    
    subgraph Daemons["Background Daemons (via lifespan)"]
        bulk_inserter["BulkInserter<br/>span ingestion queue"]
        grpc_server["GrpcServer<br/>:4317 OTLP collector"]
        dml_handler["DmlEventHandler<br/>database change events"]
        span_cost["SpanCostCalculator<br/>token cost tracking"]
        trace_sweeper["TraceDataSweeper<br/>retention policies"]
        model_store["GenerativeModelStore<br/>model metadata"]
        disk_monitor["DbDiskUsageMonitor<br/>storage alerts"]
        exp_runner["ExperimentRunner<br/>eval execution"]
    end
    
    main --> uvicorn_server
    launch_app --> ThreadServerClass
    
    uvicorn_server --> FastAPIApp
    ThreadServerClass --> FastAPIApp
    
    create_app --> FastAPIApp
    create_app --> lifespan_func
    
    FastAPIApp --> cors
    cors --> auth_mw
    auth_mw --> headers_mw
    headers_mw --> gzip_mw
    gzip_mw --> csrf_mw
    csrf_mw --> user_mw
    
    user_mw --> graphql
    user_mw --> rest_v1
    user_mw --> auth_router
    user_mw --> oauth2
    user_mw --> agents_router
    user_mw --> static
    
    lifespan_func --> bulk_inserter
    lifespan_func --> grpc_server
    lifespan_func --> dml_handler
    lifespan_func --> span_cost
    lifespan_func --> trace_sweeper
    lifespan_func --> model_store
    lifespan_func --> disk_monitor
    lifespan_func --> exp_runner
```

Sources: [src/phoenix/server/app.py](), [src/phoenix/server/main.py:17-45](), [src/phoenix/session/session.py:148-216](), [src/phoenix/server/thread_server.py]()

---

## FastAPI Application Creation

### `create_app()` Factory Function

The `create_app()` function is the core factory responsible for building and configuring the FastAPI application instance [src/phoenix/server/app.py](). It accepts parameters like a database session factory, flags for authentication and read-only mode, a secret for token signing, initial spans for startup, and the working directory.

**Stepwise Execution Flow of `create_app()`**

```mermaid
graph TB
    subgraph Inputs["Key Input Parameters"]
        db["db: DbSessionFactory"]
        auth_enabled["authentication_enabled: bool"]
        read_only["read_only: bool"]
        secret["secret: Optional[SecretStr]"]
    end
    
    subgraph Steps["Execution Steps"]
        step1["verify_server_environment_variables()"]
        step2["user_gql_extensions()<br/>load custom gql extensions"]
        step3["build_graphql_schema(extensions)"]
        step4["create_graphql_router()<br/>with Context factory"]
        step5["create_v1_router() for REST"]
        step6["create_auth_router() if auth enabled"]
        step7["create_agents_router() if enabled"]
        step8["user_fastapi_middlewares() loads custom middleware"]
        step9["FastAPI(lifespan=_lifespan, middleware)"]
        step10["app.include_router() for each API router"]
        step11["app.mount('/', StaticFiles) for UI"]
    end
    
    db --> step1
    auth_enabled --> step1
    
    step1 --> step2
    step2 --> step3
    step3 --> step4
    step4 --> step5
    step5 --> step6
    step6 --> step7
    step7 --> step8
    step8 --> step9
    step9 --> step10
    step10 --> step11
```

#### Key Components Instantiated in `create_app()`:

| Component              | Role                                                     | Location/Function                              |
|------------------------|----------------------------------------------------------|------------------------------------------------|
| Database               | `DbSessionFactory` - encapsulates async sessions         | Passed into `create_app()` [src/phoenix/server/app.py]() |
| Authentication Backend | `BearerTokenAuthBackend` - for bearer token auth         | Activated if `authentication_enabled=True` [src/phoenix/server/app.py]() |
| GraphQL Schema         | Constructed with extensions, queries, mutations, subscriptions | `build_graphql_schema()` [src/phoenix/server/api/schema.py]() |
| GraphQL Router         | Strawberry GraphQL router at `/graphql`                   | `create_graphql_router()` [src/phoenix/server/app.py]() |
| REST API Router        | Versioned V1 REST API at `/v1`                            | `create_v1_router()` [src/phoenix/server/app.py]() |
| Auth Router            | Authentication endpoints at `/auth`                       | `create_auth_router()` if auth enabled [src/phoenix/server/app.py]() |
| OAuth2 Router          | OAuth2 routes at `/oauth2`                                | Always included [src/phoenix/server/app.py]() |
| Agents Router          | Agent endpoints at `/agents`                              | Conditional via `create_agents_router()` [src/phoenix/server/app.py]() |
| Static Files           | Serves React SPA User Interface at root path              | Starlette `StaticFiles` mount [src/phoenix/server/app.py]() |
| Lifespan Context       | Manages startup/shutdown lifecycle and background tasks  | `_lifespan()` async context manager [src/phoenix/server/app.py]() |

Sources: [src/phoenix/server/app.py](), [src/phoenix/server/api/schema.py](), [src/phoenix/config.py:58-138]()

---

## Server Lifecycle Management (Lifespan)

Phoenix manages its startup and shutdown cleanly using an async context manager `_lifespan()` defined in `src/phoenix/server/app.py`.

This context manager:
- Verifies required environment variables on startup.
- Starts multiple async background daemons in a specific order using an `AsyncExitStack`.
- Provides ingestion queue functions (e.g., `enqueue_span`, `enqueue_annotation`, `enqueue_operation`) back to the FastAPI internal state.
- Ensures graceful shutdown and cleanup of all async contexts.

### Background Daemons Managed by `_lifespan()`

| Daemon                     | Purpose                                      | Code Reference |
|----------------------------|----------------------------------------------|----------------|
| `BulkInserter`             | Manages async ingestion of spans and annotations | [src/phoenix/db/bulk_inserter.py]() |
| `GrpcServer`               | gRPC OTLP server listening on port 4317       | [src/phoenix/server/grpc_server.py]() |
| `DmlEventHandler`          | Handles DB change events and cache invalidations | [src/phoenix/server/dml_event_handler.py]() |
| `SpanCostCalculator`       | Calculates token costs for spans               | [src/phoenix/server/cost_tracking/span_cost_calculator.py]() |
| `TraceDataSweeper`         | Applies trace retention policies               | [src/phoenix/server/retention.py]() |
| `GenerativeModelStore`     | Manages metadata for generative models         | [src/phoenix/server/daemons/generative_model_store.py]() |
| `DbDiskUsageMonitor`       | Monitors and warns about DB storage usage      | [src/phoenix/server/daemons/db_disk_usage_monitor.py]() |
| `ExperimentRunner`         | Runs scheduled experiment evaluations          | [src/phoenix/server/daemons/experiment_runner.py]() |

### Lifespan Startup/Shutdown Sequence Diagram

```mermaid
sequenceDiagram
    participant FastAPI
    participant lifespan["_lifespan()"]
    participant stack["AsyncExitStack"]
    participant bulk["BulkInserter"]
    participant grpc["GrpcServer"]
    participant dml["DmlEventHandler"]
    participant daemons["Other Daemons"]
    
    FastAPI->>lifespan: "Application startup"
    lifespan->>stack: "Initialize AsyncExitStack"
    
    lifespan->>bulk: "stack.enter_async_context(BulkInserter)"
    Note over bulk: "Handles async span and annotation insertion"
    
    lifespan->>grpc: "stack.enter_async_context(GrpcServer)"
    Note over grpc: "Listens for OTLP traces on gRPC port 4317"
    
    lifespan->>dml: "stack.enter_async_context(DmlEventHandler)"
    Note over dml: "Handles database change events"
    
    lifespan->>daemons: "Start cost tracking, model store, disk monitor, experiment runner"
    
    lifespan-->>FastAPI: "yield ingestion functions: enqueue_span, enqueue_annotation, enqueue_operation"
    
    Note over FastAPI: "Server Running"
    
    FastAPI->>lifespan: "Application shutdown"
    lifespan->>stack: "Exit all contexts in reverse order"
    lifespan-->>FastAPI: "Complete shutdown"
```

Sources: [src/phoenix/server/app.py](), [src/phoenix/db/bulk_inserter.py](), [src/phoenix/server/grpc_server.py]()

---

## Middleware Stack

Phoenix composes its HTTP request handling with several middleware layers to provide security, authentication, and performance optimizations.

| Middleware                    | Purpose                                      | Code References                        |
|-------------------------------|----------------------------------------------|-------------------------------------|
| **CORSMiddleware**            | Manages Cross-Origin Resource Sharing (CORS) policies | [src/phoenix/server/app.py]() |
| **AuthenticationMiddleware**  | Validates bearer tokens, API keys, sets user context | [src/phoenix/server/app.py](), [src/phoenix/server/bearer_auth.py]() |
| **RequestOriginHostnameValidator** | CSRF protection; validates origin and host for protected routes | [src/phoenix/server/app.py]() |
| **GZipMiddleware**            | Compresses HTTP responses with GZip            | [src/phoenix/server/app.py]() |
| **Custom Middleware Loader**  | Loads additional user-defined middleware from config paths | [src/phoenix/config.py](), [src/phoenix/server/app.py]() |

Sources: [src/phoenix/server/app.py](), [src/phoenix/config.py]()

---

## Configuration Management

Phoenix centralizes configuration through environment variables managed in `phoenix.config` [src/phoenix/config.py]().

### Key Environment Variables

| Variable                         | Purpose                              | Default Value / Notes                              |
|---------------------------------|------------------------------------|--------------------------------------------------|
| `PHOENIX_PORT`                  | HTTP server port                   | `6006` [src/phoenix/config.py:51-53]()           |
| `PHOENIX_GRPC_PORT`             | gRPC port (OTLP trace ingestion)  | `4317` [src/phoenix/config.py:52-54]()           |
| `PHOENIX_SQL_DATABASE_URL`       | Database connection URL            | SQLite by default [src/phoenix/config.py:170-175]() |
| `PHOENIX_ENABLE_AUTH`            | Enables authentication             | [src/phoenix/config.py]()  |
| `PHOENIX_WORKING_DIR`            | Directory for CSV/dataset storage  | [src/phoenix/config.py:139-143]() |
| `PHOENIX_ALLOW_EXTERNAL_RESOURCES` | Enable external resources in UI  | [src/phoenix/config.py:164-169]() |

### Runtime Settings Singleton

Runtime settings are encapsulated in the `Settings` class in `src/phoenix/settings.py`. At launch, `initialize_settings()` in `src/phoenix/server/main.py` reads environment variables and configures global settings [src/phoenix/server/main.py:33-42]().

Sources: [src/phoenix/config.py:1-172](), [src/phoenix/server/main.py:17-45](), [src/phoenix/settings.py]()

---

## Session and Notebook Handling

Phoenix supports interactive notebook usage by abstracting the application lifecycle behind a `Session` class hierarchy [src/phoenix/session/session.py:70-216]().

### Session Classes

| Session Type     | Description                                                                                         |
|------------------|----------------------------------------------------------------------------------------------------|
| **ThreadSession**| Runs the FastAPI server in a background daemon thread for the notebook process [src/phoenix/session/session.py:185-210](), [src/phoenix/server/thread_server.py]() |
| **ProcessSession**| Creates and manages a standalone server subprocess encapsulated in an `AppService` instance [src/phoenix/session/session.py:148-184]() |

### `Session` Base Class

The `Session` base class [src/phoenix/session/session.py:70-143]() stores host, port, database URL, and notebook environment type. It provides the `view()` method to embed the UI in notebooks via an IFrame [src/phoenix/session/session.py:114-133]().

### Dataflow: Notebook Session Integration

```mermaid
graph LR
    subgraph NotebookEnvironment["Notebook Environment"]
        UserCode["User calls px.launch_app()"]
        Client["Phoenix Python Client"]
    end
    
    subgraph ServerProcess["Server Process / Thread"]
        ThreadServer["ThreadServer (background thread)"]
        FastAPIApp["FastAPI Application"]
        Database["SQLite/PostgreSQL DB"]
    end
    
    UserCode --> ThreadServer
    ThreadServer --> FastAPIApp
    Client --> FastAPIApp
    FastAPIApp --> Database
```

Sources: [src/phoenix/session/session.py:70-216](), [src/phoenix/server/thread_server.py]()

---

## Database Configuration & Engines

Phoenix uses SQLAlchemy for database interactions, supporting both SQLite and PostgreSQL. The `create_engine` function in `src/phoenix/db/engines.py` handles connection string parsing and applies specific pragmas for SQLite performance, such as `WAL` mode and `busy_timeout` [src/phoenix/db/engines.py:53-78]().

### SQLite Optimization
When using SQLite, Phoenix loads the `phoenix-sqlean` extensions (`text`, `stats`, `time`, `crypto`) to provide advanced SQL functions required for analytics [src/phoenix/db/engines.py:26-28](). It also implements a dual-engine strategy for high-concurrency environments:
- **Writer Engine**: Configured with a larger cache and WAL mode for sustained ingestion [src/phoenix/db/engines.py:68]().
- **Reader Engine**: Optimized for read-only queries with bounded thread pools [src/phoenix/db/engines.py:44-49]().

Sources: [src/phoenix/db/engines.py:1-174]()

---

# Page: GraphQL API

# GraphQL API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/phoenix/db/migrations/versions/02463bd83119_add_evaluators.py](src/phoenix/db/migrations/versions/02463bd83119_add_evaluators.py)
- [src/phoenix/server/api/dataloaders/annotation_summaries.py](src/phoenix/server/api/dataloaders/annotation_summaries.py)
- [src/phoenix/server/api/dataloaders/document_evaluation_summaries.py](src/phoenix/server/api/dataloaders/document_evaluation_summaries.py)
- [src/phoenix/server/api/dataloaders/latency_ms_quantile.py](src/phoenix/server/api/dataloaders/latency_ms_quantile.py)
- [src/phoenix/server/api/dataloaders/min_start_or_max_end_times.py](src/phoenix/server/api/dataloaders/min_start_or_max_end_times.py)
- [src/phoenix/server/api/dataloaders/record_counts.py](src/phoenix/server/api/dataloaders/record_counts.py)
- [src/phoenix/server/api/dataloaders/token_counts.py](src/phoenix/server/api/dataloaders/token_counts.py)
- [src/phoenix/server/api/input_types/CreateProjectInput.py](src/phoenix/server/api/input_types/CreateProjectInput.py)
- [src/phoenix/server/api/input_types/ProjectSessionSort.py](src/phoenix/server/api/input_types/ProjectSessionSort.py)
- [src/phoenix/server/api/mutations/dataset_mutations.py](src/phoenix/server/api/mutations/dataset_mutations.py)
- [src/phoenix/server/api/mutations/evaluator_mutations.py](src/phoenix/server/api/mutations/evaluator_mutations.py)
- [src/phoenix/server/api/mutations/experiment_mutations.py](src/phoenix/server/api/mutations/experiment_mutations.py)
- [src/phoenix/server/api/mutations/project_mutations.py](src/phoenix/server/api/mutations/project_mutations.py)
- [src/phoenix/server/api/routers/auth_md.py](src/phoenix/server/api/routers/auth_md.py)
- [src/phoenix/server/api/routers/oauth2_authorization_server.py](src/phoenix/server/api/routers/oauth2_authorization_server.py)
- [src/phoenix/server/api/schema.py](src/phoenix/server/api/schema.py)
- [src/phoenix/server/api/types/AnnotationSummary.py](src/phoenix/server/api/types/AnnotationSummary.py)
- [src/phoenix/server/api/types/Dataset.py](src/phoenix/server/api/types/Dataset.py)
- [src/phoenix/server/api/types/EvaluationSummary.py](src/phoenix/server/api/types/EvaluationSummary.py)
- [src/phoenix/server/api/types/Evaluator.py](src/phoenix/server/api/types/Evaluator.py)
- [src/phoenix/server/session_filters.py](src/phoenix/server/session_filters.py)
- [tests/unit/db/insertion/test_helpers.py](tests/unit/db/insertion/test_helpers.py)
- [tests/unit/db/test_models.py](tests/unit/db/test_models.py)
- [tests/unit/graphql.py](tests/unit/graphql.py)
- [tests/unit/server/api/dataloaders/conftest.py](tests/unit/server/api/dataloaders/conftest.py)
- [tests/unit/server/api/dataloaders/test_annotation_summaries.py](tests/unit/server/api/dataloaders/test_annotation_summaries.py)
- [tests/unit/server/api/dataloaders/test_latency_ms_quantiles.py](tests/unit/server/api/dataloaders/test_latency_ms_quantiles.py)
- [tests/unit/server/api/dataloaders/test_record_counts.py](tests/unit/server/api/dataloaders/test_record_counts.py)
- [tests/unit/server/api/dataloaders/test_token_counts.py](tests/unit/server/api/dataloaders/test_token_counts.py)
- [tests/unit/server/api/mutations/test_dataset_mutations.py](tests/unit/server/api/mutations/test_dataset_mutations.py)
- [tests/unit/server/api/mutations/test_evaluator_mutations.py](tests/unit/server/api/mutations/test_evaluator_mutations.py)
- [tests/unit/server/api/mutations/test_experiment_mutations.py](tests/unit/server/api/mutations/test_experiment_mutations.py)
- [tests/unit/server/api/mutations/test_project_mutations.py](tests/unit/server/api/mutations/test_project_mutations.py)
- [tests/unit/server/api/routers/test_auth_md.py](tests/unit/server/api/routers/test_auth_md.py)
- [tests/unit/server/api/types/test_AnnotationSummary.py](tests/unit/server/api/types/test_AnnotationSummary.py)
- [tests/unit/server/api/types/test_Dataset.py](tests/unit/server/api/types/test_Dataset.py)
- [tests/unit/server/api/types/test_DatasetExample.py](tests/unit/server/api/types/test_DatasetExample.py)
- [tests/unit/server/api/types/test_Evaluator.py](tests/unit/server/api/types/test_Evaluator.py)
- [tests/unit/server/api/types/test_ExperimentRun.py](tests/unit/server/api/types/test_ExperimentRun.py)

</details>



## Purpose and Scope

The GraphQL API serves as the primary programmatic interface for querying, mutating, and subscribing to Phoenix's core observability artifacts—including traces, spans, datasets, experiments, prompts, and evaluators. Built using **Strawberry GraphQL**, the API leverages Python type hints to generate a strictly typed schema, integrates with FastAPI via context injection, and implements the DataLoader pattern to resolve N+1 query performance bottlenecks.

Related documentation:
- REST API endpoints: [2.3 REST API & OpenAPI](2.3)
- OTLP and gRPC ingestion: [2.4 OTLP Ingestion & gRPC Server](2.4)
- Frontend GraphQL integration: [4.1 Application Structure & Build System](4.1)

Sources: [src/phoenix/server/api/schema.py:37-66]()

---

## Schema Construction

The GraphQL schema is initialized via `build_graphql_schema()` [src/phoenix/server/api/schema.py:37-66](), which ties together the root `Query`, `Mutation`, and `Subscription` classes, custom execution contexts, custom scalar maps, and schema extensions like `get_mask_errors_extension()` [src/phoenix/server/api/schema.py:47-49]().

```mermaid
graph TB
    subgraph "Schema Entity Space"
        BuildSchema["build_graphql_schema()"]
        QueryRoot["Query"]
        MutationRoot["Mutation"]
        SubRoot["Subscription"]
        MaskExt["get_mask_errors_extension()"]
        ExecutionContext["RetainFieldDetailsExecutionContext"]
        SchemaObj["strawberry.Schema"]
    end

    BuildSchema --> QueryRoot
    BuildSchema --> MutationRoot
    BuildSchema --> SubRoot
    BuildSchema --> MaskExt
    BuildSchema --> ExecutionContext
    BuildSchema --> SchemaObj

    Sources: [src/phoenix/server/api:37-98]
```
Sources: [src/phoenix/server/api/schema.py:37-98]()

- **Custom Scalars**: Custom scalar types like `Identifier`, `CronExpression`, `SecretStr`, and `RedactedString` are mapped via `StrawberryConfig` [src/phoenix/server/api/schema.py:51-57]().
- **Cache Collision Mitigation**: `RetainFieldDetailsExecutionContext` [src/phoenix/server/api/schema.py:69-98]() subclasses `StrawberryGraphQLCoreExecutionContext` to prevent use-after-free caching bugs in `graphql-core 3.3.0` by retaining transient field detail lists during execution.
- **Interface Introspection**: The helper function `_implementing_types()` dynamically resolves all subclasses of Strawberry interfaces (such as `Evaluator`) for schema registration [src/phoenix/server/api/schema.py:100-120]().

Sources: [src/phoenix/server/api/schema.py:37-120]()

---

## Core Type System

Phoenix adopts Strawberry’s Relay-compliant `Node` interface, ensuring every domain object has a globally unique ID (`NodeID[int]`).

```mermaid
graph TB
    subgraph "Code Entity Space"
        Node["Node (strawberry.relay.Node)"]
        DatasetClass["Dataset<br/>[src/phoenix/server/api/types/Dataset.py]"]
        EvaluatorClass["Evaluator<br/>[src/phoenix/server/api/types/Evaluator.py]"]
        CodeEval["CodeEvaluator"]
        LLMEval["LLMEvaluator"]
        BuiltInEval["BuiltInEvaluator"]
    end

    Node --> DatasetClass
    Node --> EvaluatorClass
    EvaluatorClass --> CodeEval
    EvaluatorClass --> LLMEval
    EvaluatorClass --> BuiltInEval

    Sources: [src/phoenix/server/api/types/Dataset.py:46-48], [src/phoenix/server/api/types/Evaluator.py:71-73]
```
Sources: [src/phoenix/server/api/types/Dataset.py:46-48](), [src/phoenix/server/api/types/Evaluator.py:71-73]()

### Primary Domain Types

| GraphQL Type | Description | Key Code Source |
|---|---|---|
| `Dataset` | Collection of evaluated examples and versions | [src/phoenix/server/api/types/Dataset.py:46-48]() |
| `Evaluator` | Polymorphic interface for scoring components | [src/phoenix/server/api/types/Evaluator.py:71-73]() |
| `CodeEvaluator` | Evaluator executing arbitrary code in sandboxes | [src/phoenix/server/api/types/Evaluator.py:128-135]() |
| `DatasetVersion` | Immutable snapshot of dataset examples | [src/phoenix/server/api/types/Dataset.py:150-178]() |

Sources: [src/phoenix/server/api/types/Dataset.py:46-178](), [src/phoenix/server/api/types/Evaluator.py:71-135]()

---

## Query Operations & Relay Pagination

Queries are exposed via the `Query` root type. Connections follow the Relay cursor-based pagination specification using `connection_from_list` and `ConnectionArgs` [src/phoenix/server/api/types/Dataset.py:158-178]().

For instance, `Dataset.versions` accepts sorting arguments (`DatasetVersionSort`) and slicing arguments (`first`, `last`, `after`, `before`) to return a paginated `Connection[DatasetVersion]` [src/phoenix/server/api/types/Dataset.py:150-178]().

Sources: [src/phoenix/server/api/types/Dataset.py:150-178]()

---

## DataLoader Architecture & N+1 Optimization

Phoenix utilizes `strawberry.dataloader.DataLoader` paired with custom caches (such as `TokenCountCache` [src/phoenix/server/api/dataloaders/token_counts.py:45-60]()) to batch database lookups and prevent N+1 query issues during recursive object traversal.

```mermaid
graph LR
    subgraph "Execution Flow"
        Resolver["Resolver Field<br/>(e.g., Dataset.updated_by)"]
        Context["Context<br/>(src/phoenix/server/api/context.py)"]
        Loader["TokenCountDataLoader<br/>(src/phoenix/server/api/dataloaders/token_counts.py)"]
        DbSession["AsyncSession<br/>(SQLAlchemy)"]
    end

    Resolver -->|load| Loader
    Loader -->|Batch Stream| DbSession
    DbSession -->|Results| Loader
    Loader -->|Promise Resolve| Resolver

    Sources: [src/phoenix/server/api/dataloaders/token_counts.py:62-95]
```
Sources: [src/phoenix/server/api/dataloaders/token_counts.py:45-95]()

- **`TokenCountDataLoader`**: Batches prompt, completion, and total token aggregation queries across multiple projects and time windows [src/phoenix/server/api/dataloaders/token_counts.py:62-95]().
- **Two-Tier Caching**: Caches utilize combination keys mapped over `TwoTierCache` structures to minimize redundant database round-trips [src/phoenix/server/api/dataloaders/token_counts.py:45-60]().

Sources: [src/phoenix/server/api/dataloaders/token_counts.py:45-95]()

---

## Mutation Operations

State-modifying operations are organized into mixin classes (e.g., `DatasetMutationMixin` [src/phoenix/server/api/mutations/dataset_mutations.py:162-170](), `ProjectMutationMixin` [src/phoenix/server/api/mutations/project_mutations.py:32-38](), and evaluator mutations).

- **Permission Classes**: Mutations enforce security policies using classes like `IsNotReadOnly`, `IsNotViewer`, and `IsLocked` [src/phoenix/server/api/mutations/dataset_mutations.py:163-163](), [src/phoenix/server/api/mutations/project_mutations.py:33-33]().
- **Conflict Handling**: Unique constraint violations (such as duplicate dataset external IDs or project names) catch SQLAlchemy/Sqlean `IntegrityError` exceptions and raise structured `Conflict` HTTP/GraphQL errors [src/phoenix/server/api/mutations/dataset_mutations.py:139-153](), [src/phoenix/server/api/mutations/project_mutations.py:53-54]().

Sources: [src/phoenix/server/api/mutations/dataset_mutations.py:125-170](), [src/phoenix/server/api/mutations/project_mutations.py:32-57]()

---

## Subscription Operations & Context Injection

- **Subscriptions**: Real-time operations such as chat completions rely on async generator resolvers returning payloads like `ChatCompletionSubscriptionPayload` [src/phoenix/server/api/schema.py:18-20]().
- **Context**: Every resolver receives a `Context` instance containing the database session factory (`db`), data loader registry (`data_loaders`), and the authenticated user profile (`user`) [src/phoenix/server/api/context.py]() [src/phoenix/server/bearer_auth.py:63-63]().

Sources: [src/phoenix/server/api/schema.py:18-20](), [src/phoenix/server/api/context.py]()

---

# Page: REST API & OpenAPI

# REST API & OpenAPI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-rest-api/SKILL.md](.agents/skills/phoenix-rest-api/SKILL.md)
- [.agents/skills/phoenix-rest-api/references/endpoint-patterns.md](.agents/skills/phoenix-rest-api/references/endpoint-patterns.md)
- [.agents/skills/phoenix-rest-api/references/openapi-codegen.md](.agents/skills/phoenix-rest-api/references/openapi-codegen.md)
- [.agents/skills/phoenix-rest-api/references/testing-patterns.md](.agents/skills/phoenix-rest-api/references/testing-patterns.md)
- [.mintignore](.mintignore)
- [docs/openapi.json](docs/openapi.json)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-session-annotations-by-filter.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-session-annotations-by-filter.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-span-annotations-by-filter.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-span-annotations-by-filter.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-trace-annotations-by-filter.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-trace-annotations-by-filter.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/get-session-annotations-for-a-list-of-session_ids.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/get-session-annotations-for-a-list-of-session_ids.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/get-trace-annotations-for-a-list-of-trace_ids.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/get-trace-annotations-for-a-list-of-trace_ids.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/delete-experiment-by-id.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/delete-experiment-by-id.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/get-incomplete-evaluations-for-an-experiment.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/get-incomplete-evaluations-for-an-experiment.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/get-incomplete-runs-for-an-experiment.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/get-incomplete-runs-for-an-experiment.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/secrets.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/secrets.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/secrets/upsert-or-delete-secrets.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/secrets/upsert-or-delete-secrets.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/create-session-annotations.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/create-session-annotations.mdx)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx)
- [js/app/src/api/__generated__/v1.ts](js/app/src/api/__generated__/v1.ts)
- [js/packages/phoenix-client/src/__generated__/api/v1.ts](js/packages/phoenix-client/src/__generated__/api/v1.ts)
- [js/packages/phoenix-testing/src/__generated__/api/v1.ts](js/packages/phoenix-testing/src/__generated__/api/v1.ts)
- [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py](packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py)
- [schemas/openapi.json](schemas/openapi.json)
- [src/phoenix/db/insertion/dataset.py](src/phoenix/db/insertion/dataset.py)
- [src/phoenix/server/api/dataloaders/session_io.py](src/phoenix/server/api/dataloaders/session_io.py)
- [src/phoenix/server/api/dataloaders/session_num_traces.py](src/phoenix/server/api/dataloaders/session_num_traces.py)
- [src/phoenix/server/api/dataloaders/session_token_usages.py](src/phoenix/server/api/dataloaders/session_token_usages.py)
- [src/phoenix/server/api/dataloaders/trace_by_trace_ids.py](src/phoenix/server/api/dataloaders/trace_by_trace_ids.py)
- [src/phoenix/server/api/helpers/secrets.py](src/phoenix/server/api/helpers/secrets.py)
- [src/phoenix/server/api/mutations/secret_mutations.py](src/phoenix/server/api/mutations/secret_mutations.py)
- [src/phoenix/server/api/routers/v1/__init__.py](src/phoenix/server/api/routers/v1/__init__.py)
- [src/phoenix/server/api/routers/v1/annotations.py](src/phoenix/server/api/routers/v1/annotations.py)
- [src/phoenix/server/api/routers/v1/datasets.py](src/phoenix/server/api/routers/v1/datasets.py)
- [src/phoenix/server/api/routers/v1/projects.py](src/phoenix/server/api/routers/v1/projects.py)
- [src/phoenix/server/api/routers/v1/secrets.py](src/phoenix/server/api/routers/v1/secrets.py)
- [src/phoenix/server/api/routers/v1/sessions.py](src/phoenix/server/api/routers/v1/sessions.py)
- [src/phoenix/server/api/routers/v1/spans.py](src/phoenix/server/api/routers/v1/spans.py)
- [src/phoenix/server/api/routers/v1/traces.py](src/phoenix/server/api/routers/v1/traces.py)
- [src/phoenix/server/api/routers/v1/utils.py](src/phoenix/server/api/routers/v1/utils.py)
- [src/phoenix/server/api/types/GenerativeProvider.py](src/phoenix/server/api/types/GenerativeProvider.py)
- [src/phoenix/server/api/types/Secret.py](src/phoenix/server/api/types/Secret.py)
- [tests/integration/_helpers.py](tests/integration/_helpers.py)
- [tests/integration/client/conftest.py](tests/integration/client/conftest.py)
- [tests/integration/client/test_projects.py](tests/integration/client/test_projects.py)
- [tests/integration/client/test_secrets.py](tests/integration/client/test_secrets.py)
- [tests/unit/db/insertion/test_dataset.py](tests/unit/db/insertion/test_dataset.py)
- [tests/unit/server/api/mutations/test_secret_mutations.py](tests/unit/server/api/mutations/test_secret_mutations.py)
- [tests/unit/server/api/routers/v1/test_annotations.py](tests/unit/server/api/routers/v1/test_annotations.py)
- [tests/unit/server/api/routers/v1/test_datasets.py](tests/unit/server/api/routers/v1/test_datasets.py)
- [tests/unit/server/api/routers/v1/test_list_project_traces.py](tests/unit/server/api/routers/v1/test_list_project_traces.py)
- [tests/unit/server/api/routers/v1/test_projects.py](tests/unit/server/api/routers/v1/test_projects.py)
- [tests/unit/server/api/routers/v1/test_secrets.py](tests/unit/server/api/routers/v1/test_secrets.py)
- [tests/unit/server/api/routers/v1/test_sessions.py](tests/unit/server/api/routers/v1/test_sessions.py)
- [tests/unit/server/api/routers/v1/test_spans.py](tests/unit/server/api/routers/v1/test_spans.py)
- [tests/unit/server/api/routers/v1/test_traces.py](tests/unit/server/api/routers/v1/test_traces.py)
- [tests/unit/server/api/types/test_GenerativeProvider.py](tests/unit/server/api/types/test_GenerativeProvider.py)

</details>



The purpose of this document is to comprehensively document the Phoenix REST API endpoints, the OpenAPI specification, and how client libraries are automatically generated from the spec. It covers the v1 FastAPI routers handling spans, traces, datasets, prompts, experiments, annotations, and projects.

## Architecture Overview

Phoenix utilizes [FastAPI](https://fastapi.tiangolo.com) to implement its RESTful interface. The API is structured under the `/v1` prefix and is organized into functional sub-routers aggregated by the router factory `create_v1_router` [src/phoenix/server/api/routers/v1/__init__.py:33-87]().

### Request Flow and Data Transformation

1. **Routing**: Incoming requests are handled by individual routers defined in `src/phoenix/server/api/routers/v1/` and included in the main v1 router [src/phoenix/server/api/routers/v1/__init__.py:10-28]().
2. **Validation**: Pydantic models (subclasses of `V1RoutesBaseModel`) validate request payloads, path parameters, and query parameters [src/phoenix/server/api/routers/v1/models.py:39]().
3. **Authorization**: FastAPI dependencies enforce authentication (Bearer tokens via `APIKeyHeader` and `is_authenticated`) and role-based permissions, restricting viewers from write operations via `restrict_access_by_viewers` [src/phoenix/server/api/routers/v1/__init__.py:35-64]().
4. **Database Interaction**: Routers query or mutate the underlying SQL database using SQLAlchemy sessions obtained from `request.app.state.db` [src/phoenix/server/api/routers/v1/datasets.py:120-132](), [src/phoenix/server/api/routers/v1/traces.py:148-161]().
5. **Response Formatting**: Data is serialized using Pydantic models into JSON or streamed as CSV/Arrow for large payloads using `StreamingResponse` [src/phoenix/server/api/routers/v1/datasets.py:1-21](), [src/phoenix/server/api/routers/v1/spans.py:1-15]().

Title: "REST_API_Code_Mapping"
```mermaid
graph TD
    subgraph "REST_Endpoints"
        R_SPANS["/v1/spans"]
        R_TRACES["/v1/projects/{id}/traces"]
        R_DATASETS["/v1/datasets"]
        R_PROMPTS["/v1/prompts"]
        R_ANNOTATIONS["/v1/annotation_configs"]
    end

    subgraph "FastAPI_Routers"
        RT_SPANS["spans.py"]
        RT_TRACES["traces.py"]
        RT_DATASETS["datasets.py"]
        RT_PROMPTS["prompts.py"]
        RT_ANNOTATIONS["annotation_configs.py"]
    end

    subgraph "SQLAlchemy_Models"
        M_SPAN["models.Span"]
        M_TRACE["models.Trace"]
        M_DATASET["models.Dataset"]
        M_PROMPT["models.Prompt"]
        M_CONFIG["models.AnnotationConfig"]
    end

    R_SPANS --> RT_SPANS
    R_TRACES --> RT_TRACES
    R_DATASETS --> RT_DATASETS
    R_PROMPTS --> RT_PROMPTS
    R_ANNOTATIONS --> RT_ANNOTATIONS

    RT_SPANS --> M_SPAN
    RT_TRACES --> M_TRACE
    RT_DATASETS --> M_DATASET
    RT_PROMPTS --> M_PROMPT
    RT_ANNOTATIONS --> M_CONFIG
```
Sources: [src/phoenix/server/api/routers/v1/__init__.py:10-27](), [src/phoenix/server/api/routers/v1/spans.py:147-147](), [src/phoenix/server/api/routers/v1/traces.py:62-62](), [src/phoenix/server/api/routers/v1/datasets.py:88-88](), [src/phoenix/server/api/routers/v1/prompts.py:1-1]().

---

## OpenAPI Specification

Phoenix maintains an OpenAPI 3.1.0 specification located at `schemas/openapi.json` [schemas/openapi.json:1-6](). This JSON file serves as the single source of truth for the API schema and contracts.

* **Operation IDs**: Every endpoint defines unique operation identifiers such as `listAnnotationConfigs`, `listDatasets`, and `listProjectTraces` [schemas/openapi.json:16-16](), [src/phoenix/server/api/routers/v1/datasets.py:105-107](), [src/phoenix/server/api/routers/v1/traces.py:142-144]().
* **Security Definitions**: Bearer token authentication schema is registered globally on the v1 router [src/phoenix/server/api/routers/v1/__init__.py:41-51]().
* **Component Schemas**: Pydantic models automatically generate schema components in the JSON file for objects like `SpanQuery`, `Dataset`, and pagination structures [src/phoenix/server/api/routers/v1/spans.py:150-157](), [src/phoenix/server/api/routers/v1/datasets.py:91-102]().

Sources: [schemas/openapi.json:1-7](), [src/phoenix/server/api/routers/v1/__init__.py:35-61]()

---

## Client Generation Pipeline

Phoenix utilizes code generation to keep client libraries synchronized with backend changes.

### TypeScript Client Generation
The frontend and Node.js packages use `openapi-typescript` to build static TypeScript definitions from `schemas/openapi.json`.
* **Target Files**: `js/packages/phoenix-client/src/__generated__/api/v1.ts` and `js/app/src/api/__generated__/v1.ts` [js/packages/phoenix-client/src/__generated__/api/v1.ts:1-4](), [js/app/src/api/__generated__/v1.ts:1-4]().
* **Mechanism**: Generates an `interface paths` mapping URL paths to request methods, query params, request bodies, and response types [js/packages/phoenix-client/src/__generated__/api/v1.ts:6-110]().

### Python Client Generation
The Python client (`arize-phoenix-client`) includes generated `TypedDict` definitions to provide static type checking when interfacing with the REST API.
* **Target File**: `packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py` [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py:1-11]().
* **Key Definitions**: Defines request and response dictionaries such as `Dataset`, `Experiment`, `ApiKeyData`, and `CreateExperimentRequestBody` [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py:43-146](), [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py:207-215]().

Sources: [js/packages/phoenix-client/src/__generated__/api/v1.ts:1-10](), [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py:1-25]()

---

## Key API Subsystems & V1 Routers

The v1 router aggregates routers for distinct functional subsystems:

### Spans & Traces
Managed via `src/phoenix/server/api/routers/v1/spans.py` and `src/phoenix/server/api/routers/v1/traces.py`.
* **Attribute Filtering**: The `_parse_attribute` function parses dot-path queries (e.g., `llm.model_name:gpt-4`) into SQLAlchemy expressions supporting string, integer, float, and boolean values [src/phoenix/server/api/routers/v1/spans.py:72-130]().
* **Trace Listing**: Supports filtering project traces by start/end times, sort orders, inclusion of spans, and session identifiers [src/phoenix/server/api/routers/v1/traces.py:148-183]().

### Datasets & Experiments
Managed via `src/phoenix/server/api/routers/v1/datasets.py`, `src/phoenix/server/api/routers/v1/experiments.py`, and related sub-routers.
* **Dataset Pagination**: Uses cursor-based pagination encoded via base64 `GlobalID` strings [src/phoenix/server/api/routers/v1/datasets.py:113-151]().
* **Dataset Management**: Exposes endpoints for creating, listing, exporting, and deleting datasets and their underlying revisions [src/phoenix/server/api/routers/v1/datasets.py:105-185]().

### Prompts, Projects, and Annotations
* **Prompts**: Managed via `prompts.py`, supporting chat and string template types and versioning [src/phoenix/server/api/routers/v1/prompts.py:1-1](), [src/phoenix/server/api/routers/v1/__init__.py:24-24]().
* **Projects**: Managed via `projects.py`, providing project identification, creation, and metadata management [src/phoenix/server/api/routers/v1/projects.py:1-1](), [src/phoenix/server/api/routers/v1/__init__.py:23-23]().
* **Annotations**: Managed via `annotations.py` and `annotation_configs.py`, supporting span, trace, and session annotations with custom annotator kinds [src/phoenix/server/api/routers/v1/__init__.py:10-11]().

Sources: [src/phoenix/server/api/routers/v1/spans.py:72-147](), [src/phoenix/server/api/routers/v1/traces.py:142-183](), [src/phoenix/server/api/routers/v1/datasets.py:105-185](), [src/phoenix/server/api/routers/v1/__init__.py:10-28]()

---

## Implementation Data Flow

Title: "REST_API_Data_Flow"
```mermaid
sequenceDiagram
    participant Client as "Python/TS Client"
    participant Router as "FastAPI Router traces.py"
    participant Auth as "Bearer Auth Dependency"
    participant DB as "SQLAlchemy PostgreSQL/SQLite"

    Client->>Router: GET /v1/projects/{id}/traces
    Router->>Auth: is_authenticated(token)
    Auth-->>Router: PhoenixUser
    Router->>DB: select(models.Trace).filter(...)
    DB-->>Router: List[models.Trace]
    Router-->>Client: GetTracesResponseBody JSON
```
Sources: [src/phoenix/server/api/routers/v1/traces.py:148-158](), [src/phoenix/server/api/routers/v1/__init__.py:40-51](), [src/phoenix/server/bearer_auth.py:1-40]()

---

# Page: OTLP Ingestion & gRPC Server

# OTLP Ingestion & gRPC Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [requirements/integration-tests.txt](requirements/integration-tests.txt)
- [src/phoenix/db/bulk_inserter.py](src/phoenix/db/bulk_inserter.py)
- [src/phoenix/db/constants.py](src/phoenix/db/constants.py)
- [src/phoenix/db/helpers.py](src/phoenix/db/helpers.py)
- [src/phoenix/db/insertion/span.py](src/phoenix/db/insertion/span.py)
- [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py](src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py)
- [src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py](src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py)
- [src/phoenix/db/types/trace_retention.py](src/phoenix/db/types/trace_retention.py)
- [src/phoenix/server/grpc_server.py](src/phoenix/server/grpc_server.py)
- [src/phoenix/server/prometheus.py](src/phoenix/server/prometheus.py)
- [src/phoenix/server/retention.py](src/phoenix/server/retention.py)
- [src/phoenix/trace/gen_ai/conversion.py](src/phoenix/trace/gen_ai/conversion.py)
- [src/phoenix/trace/otel.py](src/phoenix/trace/otel.py)
- [tests/integration/conftest.py](tests/integration/conftest.py)
- [tests/integration/db_migrations/__init__.py](tests/integration/db_migrations/__init__.py)
- [tests/integration/db_migrations/conftest.py](tests/integration/db_migrations/conftest.py)
- [tests/integration/db_migrations/test_data_migration_4ded9e43755f_create_project_sessions_table.py](tests/integration/db_migrations/test_data_migration_4ded9e43755f_create_project_sessions_table.py)
- [tests/integration/db_migrations/test_db_schema_6a88424799fe_update_users_with_auth_method.py](tests/integration/db_migrations/test_db_schema_6a88424799fe_update_users_with_auth_method.py)
- [tests/integration/db_migrations/test_db_schema_a20694b15f82_cost.py](tests/integration/db_migrations/test_db_schema_a20694b15f82_cost.py)
- [tests/integration/db_migrations/test_db_schema_for_annotations.py](tests/integration/db_migrations/test_db_schema_for_annotations.py)
- [tests/integration/db_migrations/test_up_and_down_migrations.py](tests/integration/db_migrations/test_up_and_down_migrations.py)
- [tests/integration/project_sessions/test_project_sessions.py](tests/integration/project_sessions/test_project_sessions.py)
- [tests/integration/server/test_launch_app.py](tests/integration/server/test_launch_app.py)
- [tests/unit/db/insertion/test_span.py](tests/unit/db/insertion/test_span.py)
- [tests/unit/db/types/test_trace_retention.py](tests/unit/db/types/test_trace_retention.py)
- [tests/unit/server/test_prometheus.py](tests/unit/server/test_prometheus.py)
- [tests/unit/server/test_retention.py](tests/unit/server/test_retention.py)
- [tests/unit/trace/gen_ai/test_conversion.py](tests/unit/trace/gen_ai/test_conversion.py)
- [tests/unit/trace/test_otel.py](tests/unit/trace/test_otel.py)

</details>



## Purpose and Scope

This document describes the mechanisms by which Phoenix ingests OpenTelemetry traces using the OpenTelemetry Protocol (OTLP) over both HTTP and gRPC. Phoenix acts as an OTLP-compatible collector, accepting binary protobuf-encoded trace data, decoding it into its internal span representation, and efficiently persisting it to the database. This page covers implementation details, data flow, key classes like `GrpcServer`, `Servicer`, `BulkInserter`, span insertion pipeline (`insert_span`), capacity management, and Prometheus metrics.

---

## Architecture Overview

Phoenix runs two primary ingestion pathways:

- **gRPC Server**: A dedicated OTLP trace ingestion server, usually listening on port 4317, implementing the `TraceService` servicer.
- **HTTP Server**: Handled via FastAPI, which can also receive OTLP traces (typically via `/v1/traces`).

The gRPC server exposes the OTLP `Export` method for trace export requests from instrumented applications.

### System Components Diagram: From Ingestion to Code

```mermaid
graph TB
    subgraph "Server Process"
        GrpcServer["GrpcServer (src/phoenix/server/grpc_server.py)"]
        Servicer["Servicer (src/phoenix/server/grpc_server.py)"]
        ExportMethod["Export() method (src/phoenix/server/grpc_server.py)"]
    end
    
    subgraph "Processing Pipeline"
        BulkInserter["BulkInserter (src/phoenix/db/bulk_inserter.py)"]
        SpanQueue["_spans deque (src/phoenix/db/bulk_inserter.py)"]
        EnqueueSpan["_enqueue_span() (src/phoenix/db/bulk_inserter.py)"]
    end
    
    subgraph "Authentication"
        ApiKeyInterceptor["ApiKeyInterceptor (src/phoenix/server/bearer_auth.py)"]
    end

    GrpcServer -->|"creates and manages"| Servicer
    Servicer -->|"implements OTLP Export RPC"| ExportMethod
    ExportMethod -->|"decodes spans and calls"| EnqueueSpan
    
    EnqueueSpan --> SpanQueue
    SpanQueue -->|"batch inserts spans"| BulkInserter
    
    GrpcServer -.->|"optionally uses"| ApiKeyInterceptor
```

#### GrpcServer Class
The `GrpcServer` class in `src/phoenix/server/grpc_server.py` [src/phoenix/server/grpc_server.py:55-122]() manages the server lifecycle:
- **Lifecycle**: Implements async context manager methods `__aenter__` and `__aexit__` [src/phoenix/server/grpc_server.py:75-122]().
- **Security**: Configures TLS using `get_env_tls_config()` and `get_env_tls_enabled_for_grpc()` [src/phoenix/server/grpc_server.py:95-107]().
- **Interceptors**: Supports `ApiKeyInterceptor` for bearer token validation and OpenTelemetry instrumentation via `GrpcAioInstrumentorServer` [src/phoenix/server/grpc_server.py:79-90]().

**Sources:** [src/phoenix/server/grpc_server.py:55-122](), [src/phoenix/db/bulk_inserter.py:115-165]()

---

## OTLP Protocol Support

Phoenix implements the OTLP trace export interface defined in the OpenTelemetry proto specifications.

### Data Flow Diagram: OTLP Trace Export Request to Phoenix Span Insertion

```mermaid
graph LR
    subgraph "Client Side"
        OTLPExporter["OTLP gRPC Exporter (OpenTelemetry SDK)"]
    end
    
    subgraph "Network & Wire"
        ProtoReq["ExportTraceServiceRequest (protobuf)"]
    end
    
    subgraph "Phoenix Server Decoding"
        DecodeOtlp["decode_otlp_span() (src/phoenix/trace/otel.py)"]
        ProjectNameUtil["get_project_name() (src/phoenix/utilities/project.py)"]
    end
    
    subgraph "Internal Data Representation"
        PhoenixSpan["Span (src/phoenix/trace/schemas.py)"]
        ProjectName["ProjectName (str)"]
    end
    
    OTLPExporter -->|gRPC sends| ProtoReq
    ProtoReq --> DecodeOtlp
    ProtoReq --> ProjectNameUtil
    DecodeOtlp --> PhoenixSpan
    ProjectNameUtil --> ProjectName
```

### OTLP Export Method Processing
The `Servicer.Export` method [src/phoenix/server/grpc_server.py:41-52]() processes incoming `ExportTraceServiceRequest` objects:
1. **Resource Iteration**: Loops through `resource_spans` to extract `resource.attributes` [src/phoenix/server/grpc_server.py:46-47]().
2. **Project Resolution**: Calls `get_project_name()` to determine the destination project [src/phoenix/server/grpc_server.py:47]().
3. **Span Decoding**: Iterates through `scope_spans` and calls `decode_otlp_span` within a threadpool to prevent blocking the async loop [src/phoenix/server/grpc_server.py:48-50]().
4. **Enqueueing**: Passes the resulting `Span` object to the `_enqueue_span` callback [src/phoenix/server/grpc_server.py:51]().

**Sources:** [src/phoenix/server/grpc_server.py:33-52](), [src/phoenix/trace/otel.py:97-134]()

---

## Request Processing Pipeline

Phoenix uses a decoupled ingestion pipeline to handle high-volume trace data without stalling the network interface.

### Bulk Inserter Mechanism
The `BulkInserter` class in `src/phoenix/db/bulk_inserter.py` [src/phoenix/db/bulk_inserter.py:115-165]() is the central engine for data persistence:
- **Queueing**: Decoded spans are added to an internal collection/queue via `_enqueue_span`.
- **Batching**: It dequeues operations and performs database writes in batches to optimize I/O and transaction throughput.
- **Retry Handling**: Includes retry logic for retryable database errors such as serialization failures or deadlocks via `_is_retryable_span_error()` [src/phoenix/db/bulk_inserter.py:47-50]().

### Database Insertion Logic
Spans are persisted via `insert_span()` in `src/phoenix/db/insertion/span.py` [src/phoenix/db/insertion/span.py:128-188]():
- **Trace/Project Linking**: It looks up or creates `models.Trace` and `models.Project` records [src/phoenix/db/insertion/span.py:136-156]().
- **Session Handling**: If a `session_id` attribute is present, it links the span to a `models.ProjectSession` [src/phoenix/db/insertion/span.py:161-188]().

**Sources:** [src/phoenix/db/bulk_inserter.py:115-165](), [src/phoenix/db/insertion/span.py:128-188]()

---

## Capacity Management & Monitoring

Phoenix uses Prometheus metrics to track the health of the ingestion pipeline and queue capacities.

| Metric Name | Type | Description |
| :--- | :--- | :--- |
| `phoenix_span_queue_size` | Gauge | Current number of spans in the processing queue [src/phoenix/server/prometheus.py:113-117](). |
| `phoenix_span_queue_rejections_total` | Counter | Total requests rejected due to a full span queue [src/phoenix/server/prometheus.py:107-111](). |
| `phoenix_bulk_loader_span_insertion_time_seconds` | Histogram | Time taken for database insertion [src/phoenix/server/prometheus.py:43-48](). |
| `phoenix_bulk_loader_span_exceptions_total` | Counter | Count of exceptions during span insertion [src/phoenix/server/prometheus.py:50-54](). |
| `phoenix_bulk_loader_last_activity_timestamp_seconds` | Gauge | Unix timestamp when bulk loader last processed items [src/phoenix/server/prometheus.py:138-142](). |

**Sources:** [src/phoenix/server/prometheus.py:43-142]()

---

## Summary of Key Entities

| Code Entity | File Path | Role |
| :--- | :--- | :--- |
| `GrpcServer` | `src/phoenix/server/grpc_server.py` | Orchestrates the gRPC server and middleware. |
| `Servicer` | `src/phoenix/server/grpc_server.py` | Implements the OTLP `Export` RPC. |
| `BulkInserter` | `src/phoenix/db/bulk_inserter.py` | Manages the background batch insertion task. |
| `Span` | `src/phoenix/trace/schemas.py` | Internal data model for a single unit of work. |
| `insert_span` | `src/phoenix/db/insertion/span.py` | Logic for SQL insertion and attribute propagation. |
| `decode_otlp_span` | `src/phoenix/trace/otel.py` | Transformer from OTLP protobuf to Phoenix `Span`. |

### OTLP Ingestion Pipeline: Natural Language to Code Entities

```mermaid
graph TB
    subgraph "OTLP Trace Export"
        OTLPRequest["ExportTraceServiceRequest (protobuf)"]
        OTLPSpan["OTLP Span (protobuf)"]
    end
    
    subgraph "Phoenix Server - gRPC Layer"
        Servicer["Servicer.Export() (src/phoenix/server/grpc_server.py)"]
        Decode["decode_otlp_span() (src/phoenix/trace/otel.py)"]
    end
    
    subgraph "Phoenix Server - Ingestion Pipeline"
        BulkInserter["BulkInserter (src/phoenix/db/bulk_inserter.py)"]
        EnqueueSpan["_enqueue_span()"]
        SpanQueue["_spans deque"]
    end
    
    subgraph "Storage Layer"
        Database["PostgreSQL / SQLite"]
        InsertSpan["insert_span() (src/phoenix/db/insertion/span.py)"]
    end

    OTLPRequest -->|contains| OTLPSpan
    OTLPSpan --> Servicer
    Servicer --> Decode
    Decode --> BulkInserter
    BulkInserter --> EnqueueSpan
    EnqueueSpan --> SpanQueue
    SpanQueue --> InsertSpan
    InsertSpan --> Database
```

**Sources:** [src/phoenix/server/grpc_server.py:33-52](), [src/phoenix/db/bulk_inserter.py:115-165](), [src/phoenix/db/insertion/span.py:128-188]()

---

# Page: Database Layer & Migrations

# Database Layer & Migrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-release-please/SKILL.md](.agents/skills/phoenix-release-please/SKILL.md)
- [MIGRATION.md](MIGRATION.md)
- [scripts/README.md](scripts/README.md)
- [scripts/ddl/compare_schemas.py](scripts/ddl/compare_schemas.py)
- [scripts/ddl/generate_ddl_postgresql.py](scripts/ddl/generate_ddl_postgresql.py)
- [scripts/ddl/generate_ddl_sqlite.py](scripts/ddl/generate_ddl_sqlite.py)
- [src/phoenix/db/alembic.ini](src/phoenix/db/alembic.ini)
- [src/phoenix/db/ddl/__init__.py](src/phoenix/db/ddl/__init__.py)
- [src/phoenix/db/ddl/postgresql_schema.sql](src/phoenix/db/ddl/postgresql_schema.sql)
- [src/phoenix/db/ddl/sqlite_schema.sql](src/phoenix/db/ddl/sqlite_schema.sql)
- [src/phoenix/db/migrate.py](src/phoenix/db/migrate.py)
- [src/phoenix/db/migrations/__init__.py](src/phoenix/db/migrations/__init__.py)
- [src/phoenix/db/migrations/env.py](src/phoenix/db/migrations/env.py)
- [src/phoenix/db/migrations/versions/10460e46d750_datasets.py](src/phoenix/db/migrations/versions/10460e46d750_datasets.py)
- [src/phoenix/db/migrations/versions/132d988c5bef_add_oauth2_authorization_server_tables.py](src/phoenix/db/migrations/versions/132d988c5bef_add_oauth2_authorization_server_tables.py)
- [src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py](src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py)
- [src/phoenix/db/migrations/versions/6a88424799fe_update_users_with_auth_method.py](src/phoenix/db/migrations/versions/6a88424799fe_update_users_with_auth_method.py)
- [src/phoenix/db/migrations/versions/a1b2c3d4e5f6_ldap_schema_migration.py](src/phoenix/db/migrations/versions/a1b2c3d4e5f6_ldap_schema_migration.py)
- [src/phoenix/db/migrations/versions/bc8fea3c2bc8_add_prompt_tables.py](src/phoenix/db/migrations/versions/bc8fea3c2bc8_add_prompt_tables.py)
- [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py](src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py)
- [src/phoenix/db/migrations/versions/f1a6b2f0c9d5_add_span_session_id_index.py](src/phoenix/db/migrations/versions/f1a6b2f0c9d5_add_span_session_id_index.py)
- [src/phoenix/db/models.py](src/phoenix/db/models.py)
- [src/phoenix/server/api/routers/v1/experiment_evaluations.py](src/phoenix/server/api/routers/v1/experiment_evaluations.py)
- [src/phoenix/server/api/routers/v1/experiment_runs.py](src/phoenix/server/api/routers/v1/experiment_runs.py)
- [src/phoenix/server/api/routers/v1/experiments.py](src/phoenix/server/api/routers/v1/experiments.py)
- [src/phoenix/settings.py](src/phoenix/settings.py)
- [tests/integration/db_migrations/test_autoincrement_primary_keys.py](tests/integration/db_migrations/test_autoincrement_primary_keys.py)
- [tests/unit/server/api/routers/v1/test_experiments.py](tests/unit/server/api/routers/v1/test_experiments.py)

</details>



This page documents the database layer architecture, SQLAlchemy ORM models, schema management, and Alembic migration system. It covers the data persistence layer that stores traces, spans, projects, datasets, experiments, agent sessions, and all other Phoenix entities.

For information about data ingestion and bulk insertion, see [OTLP Ingestion & gRPC Server](2.4).

## Overview

Phoenix uses SQLAlchemy 2.0+ with async support for database operations. The database layer provides:

- **ORM Models**: Declarative models for all entities (projects, traces, spans, datasets, experiments, agent sessions, etc.) [src/phoenix/db/models.py:602-1590]().
- **Dual Database Support**: SQLite for development/local execution, PostgreSQL for production.
- **Type Safety**: Custom `TypeDecorator`s for JSON, timestamps, identifiers, and domain types [src/phoenix/db/models.py:210-559]().
- **Schema Migrations**: Alembic-based migration system for schema evolution [src/phoenix/db/migrate.py:37-70]().
- **Async Operations**: Full async/await support with `AsyncEngine` and `AsyncSession` [src/phoenix/db/models.py:38-48]().
- **SQLite Extension**: Use of the `phoenix-sqlean` package to provide advanced SQLite features like JSONB support [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:23-39]().

The database layer strives for backend dialect agnosticism, with tailored code paths and type handling to achieve compatibility for both SQLite and PostgreSQL.

Sources: [src/phoenix/db/models.py:1-600](), [src/phoenix/db/migrate.py:37-70]()

---

## Database Architecture

Phoenix structures its database interactions in layered components:

Title: Database Architecture Data Flow
```mermaid
graph TB
    subgraph ApplicationLayer["Application Layer"]
        API["GraphQL API"]
        REST["REST API Routers<br/>src/phoenix/server/api/routers/v1"]
        Insertion["Insertion Layer<br/>src/phoenix/db/insertion/span.py"]
    end
    
    subgraph DatabaseLayer["Database Layer"]
        Session["AsyncSession<br/>SQLAlchemy"]
        Models["ORM Models<br/>src/phoenix/db/models.py"]
        Helpers["insert_on_conflict()<br/>src/phoenix/db/insertion/helpers.py"]
    end
    
    subgraph EngineLayer["Engine Layer"]
        AsyncEngine["AsyncEngine<br/>SQLAlchemy"]
        SQLiteEngine["aiosqlite / sqlean"]
        PostgresEngine["asyncpg"]
    end
    
    subgraph MigrationSystem["Migration System"]
        Alembic["Alembic Engine"]
        MigrateFunc["migrate()<br/>src/phoenix/db/migrate.py"]
        Versions["Migration Versions<br/>src/phoenix/db/migrations/versions/"]
    end
    
    subgraph PhysicalStorage["Physical Storage"]
        SQLite["SQLite DB File"]
        Postgres["PostgreSQL Server"]
    end
    
    REST -- "request.app.state.db()" --> Session
    Insertion -- "session: AsyncSession" --> Session
    
    Session --> Models
    Models --> Helpers
    Helpers --> AsyncEngine
    
    AsyncEngine --> SQLite
    AsyncEngine --> Postgres
    
    MigrateFunc --> Alembic
    Alembic --> Versions
    Versions --> SQLite
    Versions --> Postgres
```

- The **REST API** and **GraphQL API** layers interact with the async SQLAlchemy `AsyncSession` for database transactions [src/phoenix/server/api/routers/v1/experiments.py:163-166]().
- The **Insertion Layer** contains optimized logic for safe, idempotent span insertion with conflict handling [src/phoenix/db/insertion/span.py:137-161]().
- The **ORM Models** declare all entities and relationships, used by the session [src/phoenix/db/models.py:41-48]().
- The **Engine Layer** abstracts actual DB implementation with drivers: `aiosqlite` for SQLite and `asyncpg` for PostgreSQL [src/phoenix/db/env.py:70-82]().
- The **Migration System** uses Alembic, invoked on startup to apply pending migrations [src/phoenix/db/migrate.py:80-80]().
- Physical storage is either a local file for SQLite or a remote PostgreSQL server.

Sources: [src/phoenix/db/insertion/span.py:25-30](), [src/phoenix/db/migrate.py:37-70](), [src/phoenix/db/models.py:39-48](), [src/phoenix/server/api/routers/v1/experiments.py:163-166]()

---

## Database Support

Phoenix supports two relational database backends configured via connection string:

| Dialect   | Driver / Package | Use Case                              |
|-----------|------------------|-------------------------------------|
| SQLite    | `aiosqlite` / `sqlean` | Development, single-node, notebooks |
| PostgreSQL| `asyncpg`        | Production, high-concurrency         |

### PostgreSQL Specifics
- Supports schemas via `get_env_database_schema()`, enabling namespace separation in multi-tenant deployments [src/phoenix/config.py:1-50](), [src/phoenix/db/models.py:54]().
- Uses native `JSONB` type for efficient JSON operations and indexing [src/phoenix/db/models.py:36](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:29-39]().
- Supports transactional DDL and version table schema isolation [src/phoenix/db/migrations/env.py:51-114]().

### SQLite Specifics & `phoenix-sqlean`
- Phoenix utilizes the `sqlean` extension package to bring PostgreSQL-like functionality to SQLite, specifically for `JSONB` support [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:23-27]().
- Implements a workaround for SQLite's `VALUES` clause rendering for multi-row inserts using `UNION ALL` via custom compiled classes `SubValues` and compiler overrides [src/phoenix/db/models.py:110-174]().
- Maps `JSONB` to standard `JSON` or the `sqlean` variant and overrides dialect behavior for compatibility [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:29-39]().

Sources: [src/phoenix/db/models.py:110-174](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:23-39](), [src/phoenix/db/migrations/env.py:51-114]()

---

## SQLAlchemy ORM Models

### Core Entity Relationships

Title: Entity Relationship Diagram
```mermaid
erDiagram
    Project ||--o{ Trace : "contains"
    Project ||--o{ Dataset : "owns"
    Trace ||--o{ Span : "composed_of"
    Trace }o--|| ProjectSession : "belongs_to"
    Span ||--o{ SpanAnnotation : "has"
    Dataset ||--o{ DatasetVersion : "versioned"
    Dataset ||--o{ DatasetExample : "contains"
    Dataset ||--o{ Experiment : "basis_for"
    Experiment ||--o{ ExperimentRun : "generates"
    ExperimentRun }o--|| DatasetExample : "evaluates"
    ExperimentRun ||--o{ ExperimentRunAnnotation : "annotated_by"
    AgentSession ||--o{ AgentSessionMessage : "contains"
    AgentSession ||--o{ AgentSessionSnapshot : "retains"
    
    Project {
        int id PK
        string name UK
        timestamp created_at
    }
    
    Trace {
        int id PK
        int project_rowid FK
        string trace_id UK
        timestamp start_time
    }
    
    Span {
        int id PK
        int trace_rowid FK
        string span_id UK
        jsonb attributes
        int cumulative_error_count
    }
```

- `Project`: Top-level organizational unit; owns traces and datasets [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:49-79]().
- `Trace`: Groups spans representing a full execution flow; belongs to a project [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:80-93]().
- `Span`: Unit of work within a trace; stores OTel attributes and status, with cumulative aggregation fields [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:95-126]().
- `ProjectSession`: Represents an application-level session grouping traces [src/phoenix/db/models.py:602-700]().
- `Dataset`, `DatasetVersion`, `DatasetExample`: Entities representing evaluation data with version control [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:49-111]().
- `Experiment`: Represents a systematic set of runs on a dataset version [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:153-199]().
- `ExperimentRun`: Individual execution in an experiment linked to an example [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:201-246]().
- `ExperimentRunAnnotation`: Stores evaluation results (labels, scores) annotated on experiment runs [src/phoenix/server/api/routers/v1/experiment_evaluations.py:107-128]().
- `AgentSession`, `AgentSessionMessage`, `AgentSessionSnapshot`: Persisted chat conversation entities for Phoenix Intelligence [MIGRATION.md:17-18]().

Sources: [src/phoenix/db/models.py:602-1590](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:48-220](), [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:48-246](), [MIGRATION.md:17-18]()

---

### Key Model Classes

| Model Class              | Table Name                 | Primary Purpose                                                       |
|--------------------------|----------------------------|---------------------------------------------------------------------|
| `Project`                | `projects`                 | Organizational grouping for tracing and evaluations [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:49-79]()   |
| `Trace`                  | `traces`                   | Aggregate of spans forming a trace [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:80-93]()         |
| `Span`                   | `spans`                    | Individual trace unit storing attributes and status [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:95-126]() |
| `Dataset`                | `datasets`                 | Versioned data collection for experiments [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:49-68]() |
| `Experiment`             | `experiments`              | Stores experiment metadata and setup [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:153-199]()|
| `ExperimentRun`          | `experiment_runs`          | Records results of experiment executions [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:201-246]() |
| `ExperimentRunAnnotation`| `experiment_run_annotations` | Evaluation results on experiment runs [src/phoenix/server/api/routers/v1/experiment_evaluations.py:121-127]() |
| `AgentSession`           | `agent_sessions`           | Persisted server-side assistant chat sessions [MIGRATION.md:17-18]() |

Sources: [src/phoenix/db/models.py:602-1560](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:80-126](), [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:49-246](), [MIGRATION.md:17-18]()

---

## Custom Type Decorators

Phoenix enhances SQLAlchemy with custom types to improve serialization, timezone handling, and domain-specific validation:

| TypeDecorator           | Purpose & Behavior                                                                                      |
|------------------------|-------------------------------------------------------------------------------------------------------|
| `UtcTimeStamp`          | Normalizes datetime values to UTC, enforces timezone-aware timestamp storage [src/phoenix/db/models.py:241-255]()              |
| `PromptTemplate`        | Validates and serializes structured prompt templates safely [src/phoenix/db/models.py:397-414]()                               |

These decorators integrate into models to enforce data integrity and representation consistency across database backends.

Sources: [src/phoenix/db/models.py:210-414]()

---

## Migration System

Phoenix employs Alembic for managing schema migrations to evolve the database safely and transparently.

### Alembic Integration

- The `migrate()` function programmatically runs database migrations during server startup [src/phoenix/db/migrate.py:37-67]().
- It loads Alembic config from `alembic.ini` and migration scripts directory [src/phoenix/db/migrate.py:53-57]().
- Runs `alembic upgrade head` asynchronously on the provided engine [src/phoenix/db/migrate.py:63-65]().
- Supports running in a separate thread (`migrate_in_thread`) for environments like notebooks where main thread async migrations are problematic [src/phoenix/db/migrate.py:83-100]().

Title: Migration System Flow
```mermaid
flowchart TD
    Start["Application Startup"]
    MigrateFunc["migrate(engine, log_migrations)"]
    Alembic["Alembic Migration Engine"]
    Scripts["Migration Version Scripts<br/>src/phoenix/db/migrations/versions"]
    DB["Database<br/>(SQLite or PostgreSQL)"]

    Start --> MigrateFunc --> Alembic --> Scripts --> DB
```

### Migration Evolution Highlights

- **Initial migration `cf03bd6bae1d_init.py`**: Creates foundational observability schema tables—Projects, Traces, Spans, Annotations [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:48-220]().
- **Datasets and Experiments `10460e46d750_datasets.py`**: Adds evaluation framework tables (Datasets, DatasetVersions, DatasetExamples, Experiments, ExperimentRuns) [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:48-245]().

Sources: [src/phoenix/db/migrate.py:37-100](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:1-220](), [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:1-245]()

---

## DDL Generation and Schema Comparison

Phoenix includes tooling for generating deterministic DDL files for both PostgreSQL and SQLite. This is used for schema snapshots and comparison.

- **PostgreSQL DDL**: `scripts/ddl/generate_ddl_postgresql.py` extracts schema info from a live or ephemeral database using `psycopg` and validates it with `pglast` [scripts/ddl/generate_ddl_postgresql.py:108-166]().
- **SQLite DDL**: `scripts/ddl/generate_ddl_sqlite.py` performs similar extraction for SQLite databases.
- **Comparison**: `scripts/ddl/compare_schemas.py` allows developers to detect drift between current models and snapshot DDL.

Sources: [scripts/ddl/generate_ddl_postgresql.py:1-166]()

---

## Insertion Logic & Helpers

Insertion operations leverage async SQLAlchemy sessions with conflict handling to ensure data integrity during concurrent writes.

### Experiment Run and Annotation Upsert

The API for `upsert_experiment_evaluation` uses `insert_on_conflict` to handle evaluations for experiment runs:

- Maps input results (label, score, explanation) to the `ExperimentRunAnnotation` model [src/phoenix/server/api/routers/v1/experiment_evaluations.py:91-119]().
- Uses `unique_by=("experiment_run_id", "name")` to ensure only one evaluation of a specific name exists per run [src/phoenix/server/api/routers/v1/experiment_evaluations.py:121-127]().

Sources: [src/phoenix/server/api/routers/v1/experiment_evaluations.py:77-128]()

---

# Appendix: Natural Language to Code Entity Associations

### From Natural Language Concepts to Database Layer Components

Title: Concept to Code Mapping
```mermaid
flowchart LR
    NL_Project["Project (Organization)"]
    NL_Trace["Trace (Execution Flow)"]
    NL_Span["Span (Work Unit)"]
    NL_Dataset["Dataset (Versioned Data)"]
    NL_Experiment["Experiment (Task Runs)"]
    NL_Migrations["Database Migrations"]

    DB_Project["models.Project<br/>ORM"]
    DB_Trace["models.Trace<br/>ORM"]
    DB_Span["models.Span<br/>ORM"]
    DB_Dataset["models.Dataset<br/>ORM"]
    DB_Experiment["models.Experiment<br/>ORM"]
    DB_Alembic["Alembic Engine"]

    NL_Project --> DB_Project
    NL_Trace --> DB_Trace
    NL_Span --> DB_Span
    NL_Dataset --> DB_Dataset
    NL_Experiment --> DB_Experiment
    NL_Migrations --> DB_Alembic
```

### From Phoenix System Names to Database Code Artifacts

Title: System to File Mapping
```mermaid
flowchart TB
    API_REST["REST API<br/>src/phoenix/server/api/routers/v1/experiments.py"]
    ORM_Model["ORM Models<br/>src/phoenix/db/models.py"]
    Migration["migrate()<br/>src/phoenix/db/migrate.py"]
    Alembic_Versions["Alembic Versions<br/>src/phoenix/db/migrations/versions"]

    API_REST --> ORM_Model
    Migration --> Alembic_Versions
    Alembic_Versions --> ORM_Model
```

Sources:
- [src/phoenix/db/models.py:1-600]()
- [src/phoenix/db/migrate.py:37-100]()
- [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:1-220]()
- [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:1-245]()
- [src/phoenix/server/api/routers/v1/experiment_evaluations.py:77-128]()
- [src/phoenix/server/api/routers/v1/experiments.py:160-166]()
- [scripts/ddl/generate_ddl_postgresql.py:1-166]()

---

# Page: Authentication & Authorization

# Authentication & Authorization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [docs/phoenix/self-hosting/features/authentication.mdx](docs/phoenix/self-hosting/features/authentication.mdx)
- [release-please-config.json](release-please-config.json)
- [src/phoenix/auth.py](src/phoenix/auth.py)
- [src/phoenix/db/facilitator.py](src/phoenix/db/facilitator.py)
- [src/phoenix/db/migrations/versions/cd164e83824f_users_and_tokens.py](src/phoenix/db/migrations/versions/cd164e83824f_users_and_tokens.py)
- [src/phoenix/server/api/auth.py](src/phoenix/server/api/auth.py)
- [src/phoenix/server/api/dataloaders/span_annotations.py](src/phoenix/server/api/dataloaders/span_annotations.py)
- [src/phoenix/server/api/input_types/CreateSpanAnnotationInput.py](src/phoenix/server/api/input_types/CreateSpanAnnotationInput.py)
- [src/phoenix/server/api/input_types/CreateTraceAnnotationInput.py](src/phoenix/server/api/input_types/CreateTraceAnnotationInput.py)
- [src/phoenix/server/api/input_types/PatchAnnotationInput.py](src/phoenix/server/api/input_types/PatchAnnotationInput.py)
- [src/phoenix/server/api/mutations/api_key_mutations.py](src/phoenix/server/api/mutations/api_key_mutations.py)
- [src/phoenix/server/api/mutations/model_mutations.py](src/phoenix/server/api/mutations/model_mutations.py)
- [src/phoenix/server/api/mutations/span_annotations_mutations.py](src/phoenix/server/api/mutations/span_annotations_mutations.py)
- [src/phoenix/server/api/mutations/trace_annotations_mutations.py](src/phoenix/server/api/mutations/trace_annotations_mutations.py)
- [src/phoenix/server/api/mutations/user_mutations.py](src/phoenix/server/api/mutations/user_mutations.py)
- [src/phoenix/server/api/routers/auth.py](src/phoenix/server/api/routers/auth.py)
- [src/phoenix/server/api/routers/oauth2.py](src/phoenix/server/api/routers/oauth2.py)
- [src/phoenix/server/api/types/Annotation.py](src/phoenix/server/api/types/Annotation.py)
- [src/phoenix/server/api/types/SpanAnnotation.py](src/phoenix/server/api/types/SpanAnnotation.py)
- [src/phoenix/server/api/types/TraceAnnotation.py](src/phoenix/server/api/types/TraceAnnotation.py)
- [src/phoenix/server/api/types/User.py](src/phoenix/server/api/types/User.py)
- [src/phoenix/server/cost_tracking/cost_model_lookup.py](src/phoenix/server/cost_tracking/cost_model_lookup.py)
- [src/phoenix/server/cost_tracking/regex_specificity.py](src/phoenix/server/cost_tracking/regex_specificity.py)
- [src/phoenix/server/daemons/generative_model_store.py](src/phoenix/server/daemons/generative_model_store.py)
- [src/phoenix/server/jwt_store.py](src/phoenix/server/jwt_store.py)
- [src/phoenix/server/oauth2.py](src/phoenix/server/oauth2.py)
- [src/phoenix/server/types.py](src/phoenix/server/types.py)
- [tests/integration/auth/conftest.py](tests/integration/auth/conftest.py)
- [tests/integration/auth/test_auth.py](tests/integration/auth/test_auth.py)
- [tests/integration/auth/test_oidc.py](tests/integration/auth/test_oidc.py)
- [tests/unit/db/test_facilitator.py](tests/unit/db/test_facilitator.py)
- [tests/unit/db/test_template_seeding.py](tests/unit/db/test_template_seeding.py)
- [tests/unit/server/api/dataloaders/test_user_credential_counts.py](tests/unit/server/api/dataloaders/test_user_credential_counts.py)
- [tests/unit/server/api/mutations/test_model_mutations.py](tests/unit/server/api/mutations/test_model_mutations.py)
- [tests/unit/server/api/mutations/test_span_annotation_mutations.py](tests/unit/server/api/mutations/test_span_annotation_mutations.py)
- [tests/unit/server/api/mutations/test_trace_annotation_mutations.py](tests/unit/server/api/mutations/test_trace_annotation_mutations.py)
- [tests/unit/server/api/routers/test_oauth2.py](tests/unit/server/api/routers/test_oauth2.py)
- [tests/unit/server/api/types/test_SpanAnnotation.py](tests/unit/server/api/types/test_SpanAnnotation.py)
- [tests/unit/server/api/types/test_TraceAnnotation.py](tests/unit/server/api/types/test_TraceAnnotation.py)
- [tests/unit/server/cost_tracking/test_cost_model_lookup.py](tests/unit/server/cost_tracking/test_cost_model_lookup.py)
- [tests/unit/server/cost_tracking/test_regex_specificity.py](tests/unit/server/cost_tracking/test_regex_specificity.py)
- [tests/unit/server/daemons/test_agent_session_sweeper.py](tests/unit/server/daemons/test_agent_session_sweeper.py)
- [tests/unit/server/daemons/test_generative_model_store.py](tests/unit/server/daemons/test_generative_model_store.py)
- [tests/unit/server/test_oauth2.py](tests/unit/server/test_oauth2.py)
- [tests/unit/test_config.py](tests/unit/test_config.py)

</details>



This document describes Phoenix's authentication and authorization system, including supported authentication methods, role-based access control, token management, and security configuration options. For configuration details of the Phoenix server, see [Application Server & Configuration](#2.1). For API access patterns, see [REST API & OpenAPI](#2.3).

## Overview

Phoenix supports multiple authentication methods that can be enabled simultaneously:

- **Local Authentication**: Password-based authentication where user credentials are stored securely as hashed passwords in the database with salts. Handled mainly via `models.LocalUser` [src/phoenix/db/models.py:348-355](). System initialization creates default admin and system users automatically [src/phoenix/db/facilitator.py:113-162]().
- **OAuth2/OIDC**: Supports integration with multiple identity providers using OAuth2 authorization code flow. Handles login, token exchange, nonce/state verification, and user provisioning as `models.OAuth2User` [src/phoenix/db/models.py:357-363](). The `login` and `create_tokens` endpoints in `src/phoenix/server/api/routers/oauth2.py` manage this flow [src/phoenix/server/api/routers/oauth2.py:98-276]().
- **LDAP**: Enterprise directory services integration. Supports user provisioning during login and role mapping via LDAP groups. Users are represented as `models.LDAPUser` [src/phoenix/db/models.py:365-372]().
- **API Keys**: Provides programmatic access through system and user API keys represented as JWTs and stored hashed in the database as `models.ApiKey` [src/phoenix/db/models.py:404-447]().

Authorization is enforced via Role-Based Access Control (RBAC) with predefined roles `ADMIN`, `MEMBER`, and `VIEWER`. The internal `SYSTEM` role is reserved for automated processes [src/phoenix/config.py:42-45]().

**Sources:**
[src/phoenix/db/models.py:348-355, 357-363, 365-372, 404-447](); [src/phoenix/server/api/routers/oauth2.py:98-276](); [src/phoenix/db/facilitator.py:113-162](); [src/phoenix/config.py:42-45]()

---

## Authentication Architecture

### Code Entity Space Mapping of Authentication Components

```mermaid
graph TB
    subgraph "Client Layer"
        WebUI["Web Browser"]
        APIClient["API Client<br/>(Python/TypeScript)"]
        OTLPExporter["OTLP Exporter<br/>(Traces)"]
    end
    
    subgraph "Authentication Methods"
        LocalAuth["Local Auth<br/>_login<br/>(src/phoenix/server/api/routers/auth.py)"]
        OAuth2["OAuth2/OIDC<br/>login/create_tokens<br/>(src/phoenix/server/api/routers/oauth2.py)"]
        LDAPAuth["LDAP Auth<br/>_ldap_login<br/>(src/phoenix/server/api/routers/auth.py)"]
        APIKeyAuth["API Key Auth<br/>(src/phoenix/server/bearer_auth.py)"]
    end
    
    subgraph "Token Management"
        JWTIssuer["JWT Token Issuer<br/>create_access_and_refresh_tokens<br/>(src/phoenix/server/bearer_auth.py)"]
        JwtStore["JwtStore<br/>(src/phoenix/server/jwt_store.py)"]
        CookieManager["Cookie Manager<br/>set_access_token_cookie<br/>(src/phoenix/auth.py)"]
    end
    
    subgraph "Authorization Layer"
        RBACCheck["RBAC Enforcement<br/>PhoenixUser<br/>(src/phoenix/server/bearer_auth.py)"]
        PermissionCheck["Permission Check<br/>IsAdmin, IsNotReadOnly<br/>(src/phoenix/server/api/auth.py)"]
    end
    
    subgraph "Data Layer"
        UserDB["models.User<br/>models.LocalUser<br/>models.OAuth2User<br/>models.LDAPUser<br/>(src/phoenix/db/models.py)"]
        APIKeyDB["models.ApiKey<br/>(src/phoenix/db/models.py)"]
    end
    
    WebUI --> LocalAuth
    WebUI --> OAuth2
    WebUI --> LDAPAuth
    APIClient --> APIKeyAuth
    OTLPExporter --> APIKeyAuth
    
    LocalAuth --> JWTIssuer
    OAuth2 --> JWTIssuer
    LDAPAuth --> JWTIssuer
    
    JWTIssuer --> JwtStore
    JwtStore --> CookieManager
    
    CookieManager --> RBACCheck
    APIKeyAuth --> RBACCheck
    
    RBACCheck --> PermissionCheck
```

**Sources:**
[src/phoenix/server/api/routers/oauth2.py:98-156](); [src/phoenix/server/bearer_auth.py:37-53](); [src/phoenix/server/jwt_store.py:73-90](); [src/phoenix/db/models.py:348-447](); [src/phoenix/auth.py:101-122]()

---

## Authentication Methods

### Local Authentication (Password-Based)

Local authentication uses password hashes stored in `models.LocalUser` [src/phoenix/db/models.py:348-355](). Password hashing uses PBKDF2-HMAC-SHA256 [src/phoenix/auth.py:22-34](). Password validation compares user-supplied input hashed with stored salt against the stored hash using `is_valid_password` [src/phoenix/auth.py:37-50]().

**Key Implementation Details:**
- **Credentials**: Stored in `password_hash` and `password_salt` [src/phoenix/db/models.py:348-355]().
- **Login Endpoint**: `_login` in `src/phoenix/server/api/routers/auth.py` validates credentials and issues tokens [src/phoenix/server/api/routers/auth.py:144-186]().
- **Seeding**: `Facilitator` ensures that default `SYSTEM` and `ADMIN` users are present in the database during startup [src/phoenix/db/facilitator.py:113-162]().

**Configuration:**
- `PHOENIX_ENABLE_STRONG_PASSWORD_POLICY`: Enforces 12+ characters, mixed case, and special characters [src/phoenix/auth.py:96-98]().
- `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD`: Sets initial password for the seeded admin user [docs/phoenix/self-hosting/features/authentication.mdx:56-70]().

**Sources:**
[src/phoenix/db/models.py:348-355](); [src/phoenix/auth.py:22-50, 96-98](); [src/phoenix/server/api/routers/auth.py:144-186](); [src/phoenix/db/facilitator.py:113-162](); [docs/phoenix/self-hosting/features/authentication.mdx:56-70]()

---

### OAuth2/OIDC Integration

Phoenix supports external identity providers via the `OAuth2Client` class [src/phoenix/server/oauth2.py:54-138]().

**Workflow:**
1. **Login Initiation**: `GET /oauth2/{idp_name}/login` generates an authorization URL with PKCE `code_verifier`, `state`, and `nonce` stored in secure cookies [src/phoenix/server/api/routers/oauth2.py:100-140]().
2. **Callback Handling**: `GET /oauth2/{idp_name}/tokens` validates the `state` and `nonce` cookies, exchanges the `authorization_code` for tokens, and extracts user claims using JMESPath [src/phoenix/server/api/routers/oauth2.py:144-276]().
3. **Claim Extraction**: Uses `search_claim_path` to evaluate JMESPath expressions against ID token claims for email, groups, and roles [src/phoenix/server/oauth2.py:21-51]().

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Phoenix as Phoenix_Server:<br/>src/phoenix/server/api/routers/oauth2.py
    participant IDP as Identity_Provider
    
    User->>Browser: "ClickLogin"
    Browser->>Phoenix: "GET/oauth2/{idp_name}/login"
    Phoenix->>Phoenix: "create_authorization_url()"
    Phoenix->>Browser: "Redirect+SetState/NonceCookies"
    Browser->>IDP: "AuthRequest"
    IDP->>Browser: "Redirectwithcode&state"
    Browser->>Phoenix: "GET/oauth2/{idp_name}/tokens?code&state"
    Phoenix->>Phoenix: "ValidateState/NonceCookies"
    Phoenix->>IDP: "ExchangecodeforIDToken"
    Phoenix->>Phoenix: "search_claim_path()foremail/roles"
    Phoenix->>Phoenix: "create_access_and_refresh_tokens()"
    Phoenix->>Browser: "SetJWTCookies"
```

**Sources:**
[src/phoenix/server/api/routers/oauth2.py:100-276](); [src/phoenix/server/oauth2.py:21-51, 54-138]()

---

## Role-Based Access Control (RBAC)

Phoenix uses roles to control access to GraphQL mutations and queries.

| Role | Permissions | Code Entity |
| :--- | :--- | :--- |
| **ADMIN** | Full system access, user management, and API key creation. | `models.UserRoleName.ADMIN` |
| **MEMBER** | Read/write access to projects, traces, and datasets. | `models.UserRoleName.MEMBER` |
| **VIEWER** | Read-only access to observability data. | `models.UserRoleName.VIEWER` |

### Enforcement
Permissions are enforced using Strawberry permission classes:
- `IsAdmin`: Restricts access to admins [src/phoenix/server/api/auth.py:99]().
- `IsNotViewer`: Prevents viewers from executing mutations [src/phoenix/server/api/auth.py:99]().
- `IsNotReadOnly`: Prevents operations if the server is in a read-only state [src/phoenix/server/api/auth.py:99]().
- `IsLocked`: Prevents operations if the account is temporarily locked due to brute force protection [src/phoenix/server/api/auth.py:99]().

These permission classes are applied to GraphQL mutations, for example, in `UserMutationMixin` [src/phoenix/server/api/mutations/user_mutations.py:121]() or `DatasetMutationMixin`.

**Sources:**
[src/phoenix/server/api/mutations/user_mutations.py:121](); [src/phoenix/server/api/auth.py:99](); [src/phoenix/config.py:42-45]()

---

## Token & API Key Management

### JwtStore
The `JwtStore` manages the lifecycle of all JWTs used in the system [src/phoenix/server/jwt_store.py:73-90](). It utilizes specialized sub-stores for:
- **Access Tokens**: Short-lived session tokens [src/phoenix/server/jwt_store.py:88]().
- **Refresh Tokens**: Used for token rotation; spent tokens are retained as tombstones to detect reuse [src/phoenix/server/jwt_store.py:116-129]().
- **API Keys**: Long-lived tokens for programmatic access [src/phoenix/server/jwt_store.py:90]().

### API Keys
API keys are stored as hashed records in `models.ApiKey` [src/phoenix/db/models.py:404-447](). 
- **System API Keys**: Created for the `SYSTEM` user to allow OTLP ingestion.
- **User API Keys**: Linked to specific users, inheriting their RBAC permissions.

API key mutations are handled by `ApiKeyMutationMixin`, allowing creation, patching, and deletion of API keys.

**Sources:**
[src/phoenix/server/jwt_store.py:73-129](); [src/phoenix/db/models.py:404-447]()

---

## Facilitator Pattern

The `Facilitator` class is responsible for ensuring the database is in a consistent state upon application startup [src/phoenix/db/facilitator.py:59-65](). It performs idempotent operations to seed necessary records.

| Task | Description | Function |
| :--- | :--- | :--- |
| **Enums** | Ensures all values defined in `ENUM_COLUMNS` exist in the DB. | `_ensure_enums` [src/phoenix/db/facilitator.py:94-111]() |
| **User Roles** | Seeds the `SYSTEM` and `ADMIN` roles and default users. | `_ensure_user_roles` [src/phoenix/db/facilitator.py:113-162]() |
| **OAuth2 Clients** | Seeds the first-party Phoenix CLI OAuth2 client. | `_ensure_oauth2_clients` [src/phoenix/db/facilitator.py:168-189]() |
| **Retention** | Sets up the default project trace retention policy. | `_ensure_default_project_trace_retention_policy` [src/phoenix/db/facilitator.py:337-353]() |

**Sources:**
[src/phoenix/db/facilitator.py:59-189, 337-353]()

---

## Security Features

### Brute Force Login Protection
Phoenix tracks failed login attempts per email using `BruteForceLoginRateLimiter` [src/phoenix/server/api/routers/auth.py:69-75]().
- After a configurable number of attempts (`PHOENIX_BRUTE_FORCE_LOGIN_PROTECTION_MAX_ATTEMPTS`), the account is locked [docs/phoenix/self-hosting/features/authentication.mdx:90-92]().
- Success resets the failure counter [src/phoenix/server/api/routers/auth.py:94-96]().

### Rate Limiting
API endpoints are protected by `fastapi_ip_rate_limiter` and `fastapi_route_rate_limiter` [src/phoenix/server/api/routers/oauth2.py:68-85](). This prevents denial-of-service and credential stuffing on authentication routes.

**Sources:**
[src/phoenix/server/api/routers/auth.py:69-75, 94-96](); [src/phoenix/server/api/routers/oauth2.py:68-85](); [docs/phoenix/self-hosting/features/authentication.mdx:90-92]()

---

# Page: Cost Tracking & Model Pricing

# Cost Tracking & Model Pricing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/cost_tracking/sync_models.py](scripts/cost_tracking/sync_models.py)
- [scripts/verify_threshold_cost.py](scripts/verify_threshold_cost.py)
- [src/phoenix/auth.py](src/phoenix/auth.py)
- [src/phoenix/db/facilitator.py](src/phoenix/db/facilitator.py)
- [src/phoenix/db/migrations/versions/cd164e83824f_users_and_tokens.py](src/phoenix/db/migrations/versions/cd164e83824f_users_and_tokens.py)
- [src/phoenix/server/api/evaluators.py](src/phoenix/server/api/evaluators.py)
- [src/phoenix/server/api/helpers/evaluators.py](src/phoenix/server/api/helpers/evaluators.py)
- [src/phoenix/server/api/helpers/playground_clients.py](src/phoenix/server/api/helpers/playground_clients.py)
- [src/phoenix/server/api/input_types/EvaluatorPreviewInput.py](src/phoenix/server/api/input_types/EvaluatorPreviewInput.py)
- [src/phoenix/server/api/mutations/chat_mutations.py](src/phoenix/server/api/mutations/chat_mutations.py)
- [src/phoenix/server/api/mutations/model_mutations.py](src/phoenix/server/api/mutations/model_mutations.py)
- [src/phoenix/server/api/mutations/user_mutations.py](src/phoenix/server/api/mutations/user_mutations.py)
- [src/phoenix/server/api/routers/auth.py](src/phoenix/server/api/routers/auth.py)
- [src/phoenix/server/api/subscriptions.py](src/phoenix/server/api/subscriptions.py)
- [src/phoenix/server/api/types/User.py](src/phoenix/server/api/types/User.py)
- [src/phoenix/server/cost_tracking/cost_model_lookup.py](src/phoenix/server/cost_tracking/cost_model_lookup.py)
- [src/phoenix/server/cost_tracking/model_cost_manifest.json](src/phoenix/server/cost_tracking/model_cost_manifest.json)
- [src/phoenix/server/cost_tracking/regex_specificity.py](src/phoenix/server/cost_tracking/regex_specificity.py)
- [src/phoenix/server/daemons/generative_model_store.py](src/phoenix/server/daemons/generative_model_store.py)
- [tests/unit/db/test_facilitator.py](tests/unit/db/test_facilitator.py)
- [tests/unit/db/test_template_seeding.py](tests/unit/db/test_template_seeding.py)
- [tests/unit/server/api/dataloaders/test_user_credential_counts.py](tests/unit/server/api/dataloaders/test_user_credential_counts.py)
- [tests/unit/server/api/helpers/test_evaluators.py](tests/unit/server/api/helpers/test_evaluators.py)
- [tests/unit/server/api/helpers/test_playground_clients.py](tests/unit/server/api/helpers/test_playground_clients.py)
- [tests/unit/server/api/mutations/test_evaluator_preview_mutation.py](tests/unit/server/api/mutations/test_evaluator_preview_mutation.py)
- [tests/unit/server/api/mutations/test_model_mutations.py](tests/unit/server/api/mutations/test_model_mutations.py)
- [tests/unit/server/api/test_create_llm_evaluator_from_inline.py](tests/unit/server/api/test_create_llm_evaluator_from_inline.py)
- [tests/unit/server/api/test_subscriptions.py](tests/unit/server/api/test_subscriptions.py)
- [tests/unit/server/cost_tracking/test_cost_model_lookup.py](tests/unit/server/cost_tracking/test_cost_model_lookup.py)
- [tests/unit/server/cost_tracking/test_model_cost_manifest.py](tests/unit/server/cost_tracking/test_model_cost_manifest.py)
- [tests/unit/server/cost_tracking/test_regex_specificity.py](tests/unit/server/cost_tracking/test_regex_specificity.py)
- [tests/unit/server/daemons/test_agent_session_sweeper.py](tests/unit/server/daemons/test_agent_session_sweeper.py)
- [tests/unit/server/daemons/test_generative_model_store.py](tests/unit/server/daemons/test_generative_model_store.py)

</details>



The cost tracking subsystem in Phoenix provides automated calculation and reporting of LLM token costs across spans, traces, and projects. It integrates a static manifest of model prices, a background daemon to synchronize model metadata, a cache lookup mechanism to resolve model pricing, and specialized calculators that compute costs based on token usage.

Sources:
[src/phoenix/server/cost_tracking/model_cost_manifest.json:1-34]()
[src/phoenix/db/facilitator.py:82-83]()

---

## System Architecture

The cost tracking system consists of four major components managing cost data from ingestion to cost computation and storage:

1.  **Model Cost Manifest**: A static JSON file defining baseline pricing configurations for known LLM models and providers [src/phoenix/server/cost_tracking/model_cost_manifest.json:1-34]().
2.  **CostModelLookup**: A utility class that matches raw model names reported in spans/traces to standardized model pricing information using regex patterns and database cache entries [tests/unit/server/cost_tracking/test_model_cost_manifest.py:23-23]().
3.  **GenerativeModelStore Daemon**: A server-side background daemon that periodically fetches generative model metadata and pricing from the database, maintaining an in-memory cache [tests/unit/server/api/helpers/test_evaluators.py:74-74]().
4.  **SpanCostCalculator**: A background process that scans ingested spans for LLM usage, resolves their models through `CostModelLookup`, and calculates USD cost contributions based on token counts and pricing tiers.

### Overview Diagram: Cost Tracking System Components and Data Flow

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserTrace["UserLLMTrace(gpt-4o)"]
    end

    subgraph "Code Entity Space"
        Manifest["model_cost_manifest.json"]
        Lookup["CostModelLookup"]
        Store["GenerativeModelStore"]
        Calculator["SpanCostCalculator"]
        DB_Models["models.GenerativeModel"]
        DB_SpanCosts["models.SpanCost"]
    end

    Manifest -->|"seeds"| Store
    Store -->|"syncs models & prices"| DB_Models
    UserTrace -->|"OTLP span ingestion"| Calculator
    DB_Models -->|"pricing lookup"| Calculator
    Lookup -->|"model name matching"| Calculator
    Calculator -->|"writes calculated cost"| DB_SpanCosts
```

Sources:
[src/phoenix/server/cost_tracking/model_cost_manifest.json:1-34]()
[src/phoenix/db/facilitator.py:82-83]()
[tests/unit/server/cost_tracking/test_model_cost_manifest.py:23-23]()
[tests/unit/server/api/helpers/test_evaluators.py:74-74]()

---

## Model Cost Manifest

The core reference for pricing is the `model_cost_manifest.json` file located in the server cost tracking directory. This JSON manifest provides canonical LLM model entries along with detailed token price attributes.

### Structure and Content

Each model entry contains:

*   **name**: The canonical internal model name identifier [src/phoenix/server/cost_tracking/model_cost_manifest.json:4-4]().
*   **name_pattern**: A regex pattern to match variants and aliases of the model name as reported in incoming span attributes [src/phoenix/server/cost_tracking/model_cost_manifest.json:5-5]().
*   **source**: The origin source of the pricing data (e.g., "litellm") [src/phoenix/server/cost_tracking/model_cost_manifest.json:6-6]().
*   **token_prices**: An array of objects specifying per-token pricing by type and whether tokens contribute to prompt (input) or output costs [src/phoenix/server/cost_tracking/model_cost_manifest.json:7-18]().

#### Advanced Pricing: Threshold-Based Customization
Certain models support `threshold_based` customization via the `TokenPriceCustomizationParser` [src/phoenix/db/types/token_price_customization.py:29](). This allows the system to adjust rates based on token counts, such as increasing the `base_rate` once a prompt exceeds a specific threshold [src/phoenix/server/cost_tracking/model_cost_manifest.json:152-158]().

Sources:
[src/phoenix/server/cost_tracking/model_cost_manifest.json:1-192]()
[src/phoenix/db/types/token_price_customization.py:29]()

---

## CostModelLookup Class

`CostModelLookup` is designed to match fuzzy model names from span attributes to canonical models stored in the database. It uses regex matching against the `name_pattern` field of cached generative models.

### Key Responsibilities

*   On initialization or upon model data refresh, it caches the set of generative models from the database with their regex patterns compiled [tests/unit/server/cost_tracking/test_model_cost_manifest.py:23-23]().
*   Given a model name string and timestamp of the span, it resolves the best matching generative model, which includes token pricing information [tests/unit/server/cost_tracking/test_model_cost_manifest.py:23-23]().
*   Supports quick lookup for repeated queries without hitting the database on each span processing.

Sources:
[tests/unit/server/cost_tracking/test_model_cost_manifest.py:23-23]()

---

## GenerativeModelStore Daemon

The `GenerativeModelStore` is a long-running background daemon within the Phoenix server responsible for synchronizing generative model data from the database into an in-memory cache for efficient pricing lookups [tests/unit/server/api/helpers/test_evaluators.py:74-74]().

### Functionality and Implementation

*   Periodically queries the `generative_models` and associated token prices from the relational database using SQLAlchemy `joinedload` for efficiency [tests/unit/server/api/helpers/test_evaluators.py:74-74]().
*   Employs incremental fetching using timestamp filters (`updated_at`, `deleted_at`) with a buffer to minimize redundant database queries [tests/unit/server/api/helpers/test_evaluators.py:74-74]().
*   The synchronization strategy trades memory for reduced DB calls, optimized to support frequent queries at computation time without incurring remote database overhead.

Sources:
[tests/unit/server/api/helpers/test_evaluators.py:74-74]()

---

## SpanCostCalculator Overview

`SpanCostCalculator` is a subsystem daemon that processes ingested spans to compute and persist LLM token usage costs [tests/unit/server/api/helpers/test_evaluators.py:73-73]().

### Process Steps

1.  **Span Fetching**: Iterates over spans marked with `span_kind` of type `LLM` which typically contain token usage details [tests/unit/server/api/helpers/test_evaluators.py:73-73]().
2.  **Model Name Extraction & Lookup**: Extracts model identifying information from span attributes, uses `CostModelLookup` to resolve to a canonical model with known pricing [tests/unit/server/api/helpers/test_evaluators.py:73-73]().
3.  **Token Counts & Pricing**: Reads token counts for prompt (input), completion (output), and optionally other categories such as cache reads/writes [src/phoenix/server/cost_tracking/model_cost_manifest.json:7-33]().
4.  **Cost Computation**: For each token type present, multiplies token count by the matching price rate [tests/unit/server/api/helpers/test_evaluators.py:73-73]().
5.  **Cost Recording**: Creates `SpanCost` records reflecting USD amounts for the associated span [tests/unit/server/api/helpers/test_evaluators.py:73-73]().

### Span Cost Calculation Sequence Diagram

```mermaid
sequenceDiagram
    participant D as "SpanCostCalculator"
    participant DB as "models.Span"
    participant L as "CostModelLookup"
    participant C as "models.SpanCost"

    D->>DB: "Fetch spans missing cost where span_kind == LLM"
    loop For each span
        D->>DB: "Extract model_name and token counts"
        D->>L: "Lookup generative model by model_name"
        L-->>D: "Return matching model with pricing"
        D->>D: "Compute cost = tokens * base_rate"
        D->>C: "Insert computed cost into SpanCost table"
    end
```

Sources:
[src/phoenix/server/cost_tracking/model_cost_manifest.json:7-33]()
[tests/unit/server/api/helpers/test_evaluators.py:73-73]()

---

## Database Seeding and Facilitation

Phoenix provides a `Facilitator` class that runs at server startup to ensure all required database records, including model cost data, are seeded correctly [src/phoenix/db/facilitator.py:59-65]().

### Model Cost Initialization

*   The `_ensure_model_costs` function is one of the standard callbacks in `Facilitator` [src/phoenix/db/facilitator.py:83-83]().
*   It reads the `model_cost_manifest.json` and inserts new or missing generative models and token prices into the database, ensuring idempotency [src/phoenix/db/facilitator.py:83-83]().
*   This process handles complex price types, including `input`, `output`, `cache_read`, and `cache_write` [src/phoenix/server/cost_tracking/model_cost_manifest.json:7-60]().

Sources:
[src/phoenix/db/facilitator.py:59-91]()
[src/phoenix/server/cost_tracking/model_cost_manifest.json:1-60]()

---

## Managing Models via GraphQL API Mutations

Cost tracking data can be managed interactively with GraphQL mutations, facilitating manual override or addition of cost models. The system ensures that only authorized users (e.g., via `IsAdmin`) can modify pricing data [src/phoenix/server/api/mutations/user_mutations.py:121-121]().

### Key Mutations Supported

*   **createModel**: Adds a new generative model with associated pricing details [src/phoenix/server/api/mutations/user_mutations.py:121-121]().
*   **updateModel**: Modifies existing models, allowing updates to name patterns or token costs [src/phoenix/server/api/mutations/user_mutations.py:121-121]().
*   **deleteModel**: Soft deletes models, ensuring removal from the lookup cache [src/phoenix/server/api/mutations/user_mutations.py:121-121]().

These mutations allow dynamic control over model pricing, supplementing the static manifest. The `UserMutationMixin` handles user operations while permissions like `IsAdmin` gate sensitive pricing modifications [src/phoenix/server/api/mutations/user_mutations.py:120-121]().

Sources:
[src/phoenix/server/api/mutations/user_mutations.py:120-180]()

---

## Cost-Sync Workflow

Upstream model pricing data is synchronized via scripts and automation workflows (such as `scripts/cost_tracking/sync_models.py`), ensuring that the platform remains up-to-date with latest pricing tiers without manual JSON editing.

Sources:
[src/phoenix/server/cost_tracking/model_cost_manifest.json:1-34]()

---

# Summary

The Phoenix cost tracking and model pricing subsystem offers fully automated, accurate LLM cost computation by:

*   Utilizing a comprehensive static JSON manifest with regex-based model matching [src/phoenix/server/cost_tracking/model_cost_manifest.json:1-34]().
*   Providing an in-memory cache and lookup via `CostModelLookup` for efficient runtime price resolution [tests/unit/server/cost_tracking/test_model_cost_manifest.py:23-23]().
*   Synchronizing model state continuously with `GenerativeModelStore` to reflect the latest database state [tests/unit/server/api/helpers/test_evaluators.py:74-74]().
*   Calculating costs through span processors that compute per-span USD token usage [tests/unit/server/api/helpers/test_evaluators.py:73-73]().

Sources:
[src/phoenix/server/cost_tracking/model_cost_manifest.json:1-34]()
[src/phoenix/db/facilitator.py:59-91]()
[src/phoenix/server/api/mutations/user_mutations.py:120-180]()
[tests/unit/server/cost_tracking/test_model_cost_manifest.py:23-23]()
[tests/unit/server/api/helpers/test_evaluators.py:73-74]()

---

# Page: Client Libraries

# Client Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-tracing/README.md](.agents/skills/phoenix-tracing/README.md)
- [.agents/skills/phoenix-tracing/SKILL.md](.agents/skills/phoenix-tracing/SKILL.md)
- [.agents/skills/phoenix-tracing/references/annotations-python.md](.agents/skills/phoenix-tracing/references/annotations-python.md)
- [.agents/skills/phoenix-tracing/references/instrumentation-atif-python.md](.agents/skills/phoenix-tracing/references/instrumentation-atif-python.md)
- [.agents/skills/phoenix-tracing/references/setup-python.md](.agents/skills/phoenix-tracing/references/setup-python.md)
- [README.md](README.md)
- [docs/phoenix/evaluation/pre-built-metrics/completeness.mdx](docs/phoenix/evaluation/pre-built-metrics/completeness.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/conciseness.mdx](docs/phoenix/evaluation/pre-built-metrics/conciseness.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/pii-detection.mdx](docs/phoenix/evaluation/pre-built-metrics/pii-detection.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/refusal.mdx](docs/phoenix/evaluation/pre-built-metrics/refusal.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/user-friction.mdx](docs/phoenix/evaluation/pre-built-metrics/user-friction.mdx)
- [docs/phoenix/release-notes/03-2026/03-05-2026-sdk-session-retrieval.mdx](docs/phoenix/release-notes/03-2026/03-05-2026-sdk-session-retrieval.mdx)
- [docs/phoenix/sdk-api-reference/python/arize-phoenix-client.mdx](docs/phoenix/sdk-api-reference/python/arize-phoenix-client.mdx)
- [docs/phoenix/sdk-api-reference/python/arize-phoenix-evals.mdx](docs/phoenix/sdk-api-reference/python/arize-phoenix-evals.mdx)
- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-client.mdx](docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-client.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/overview.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/secrets.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/secrets.mdx)
- [js/packages/phoenix-client/README.md](js/packages/phoenix-client/README.md)
- [js/packages/phoenix-client/src/secrets/index.ts](js/packages/phoenix-client/src/secrets/index.ts)
- [js/packages/phoenix-client/src/secrets/upsertOrDeleteSecrets.ts](js/packages/phoenix-client/src/secrets/upsertOrDeleteSecrets.ts)
- [js/packages/phoenix-client/test/entryPoints.test.ts](js/packages/phoenix-client/test/entryPoints.test.ts)
- [js/packages/phoenix-client/test/secrets/upsertOrDeleteSecrets.test.ts](js/packages/phoenix-client/test/secrets/upsertOrDeleteSecrets.test.ts)
- [js/packages/phoenix-evals/README.md](js/packages/phoenix-evals/README.md)
- [js/packages/phoenix-mcp/README.md](js/packages/phoenix-mcp/README.md)
- [js/packages/phoenix-mcp/src/index.ts](js/packages/phoenix-mcp/src/index.ts)
- [js/packages/phoenix-mcp/src/projectTools.ts](js/packages/phoenix-mcp/src/projectTools.ts)
- [packages/phoenix-client/README.md](packages/phoenix-client/README.md)
- [packages/phoenix-evals/README.md](packages/phoenix-evals/README.md)
- [packages/phoenix-otel/README.md](packages/phoenix-otel/README.md)

</details>



Overview of client libraries available for interacting with Phoenix programmatically, across Python and TypeScript. Links to child pages for each library.

Phoenix provides comprehensive client libraries for programmatic interaction with the platform. These libraries enable developers to instrument applications with OpenTelemetry, manage datasets and experiments, run evaluations, and query trace data without using the web UI. All packages are independently versioned and distributed through PyPI (Python) or NPM (TypeScript) [README.md:25-36]().

## Ecosystem Architecture

```mermaid
graph TB
    subgraph "Python Ecosystem"
        PyApp["Python Application"] -->|"Instrument spans"| PythonOtel["arize-phoenix-otel"]
        PyApp -->|"Query/mutate data"| PythonClient["arize-phoenix-client"]
        PyApp -->|"Run evaluations"| PythonEvals["arize-phoenix-evals"]
    end
    
    subgraph "TypeScript Ecosystem"
        TSApp["TypeScript Application"] -->|"Instrument spans"| TSOtel["@arizeai/phoenix-otel"]
        TSApp -->|"Query/mutate data"| TSClient["@arizeai/phoenix-client"]
        TSApp -->|"Run evaluations"| TSEvals["@arizeai/phoenix-evals"]
        
        TSCLI["@arizeai/phoenix-cli"] -->|"Uses"| TSClient
        TSMCP["@arizeai/phoenix-mcp"] -->|"Uses"| TSClient
    end
    
    subgraph "Phoenix Server"
        OTLPIngestion["OTLP Ingestion"]
        RESTAPI["REST API"]
        GraphQLAPI["GraphQL API"]
    end
    
    PythonOtel -->|"OTLP/HTTP or gRPC"| OTLPIngestion
    TSOtel -->|"OTLP/HTTP or gRPC"| OTLPIngestion
    
    PythonClient -->|"HTTP"| RESTAPI
    TSClient -->|"HTTP"| RESTAPI
    
    PythonClient -.->|"Optional"| GraphQLAPI
    TSClient -.->|"Optional"| GraphQLAPI
```

Sources: [README.md:44-53](), [js/packages/phoenix-client/package.json:2-13](), [js/packages/phoenix-mcp/package.json:33-40](), [packages/phoenix-otel/src/phoenix/otel/otel.py:65-210]()

---

## 3.1. Python Client (`arize-phoenix-client`)

The `arize-phoenix-client` package provides an interface for interacting with the Phoenix platform via its REST and GraphQL APIs [packages/phoenix-client/README.md:23-27](). It enables developers to manage datasets, run experiments, analyze traces, and collect feedback programmatically using Python objects and pandas DataFrames [packages/phoenix-client/README.md:27-35]().

For deep technical details, installation options, resource models, Harbor contract testing, and ATIF helpers, see [Python Client (arize-phoenix-client)](#3.1).

Sources: [packages/phoenix-client/README.md:23-35](), [docs/phoenix/sdk-api-reference/python/arize-phoenix-client.mdx:12-24]()

---

## 3.2. Python OpenTelemetry (`arize-phoenix-otel`)

The `arize-phoenix-otel` package supplies a lightweight wrapper around OpenTelemetry primitives with Phoenix-aware defaults [packages/phoenix-otel/README.md:25-26](). It simplifies OpenTelemetry configuration via the `register()` function and supports auto-instrumentation for popular AI frameworks [packages/phoenix-otel/README.md:29-35]().

For detailed configuration parameters, TracerProvider initialization, endpoint inference, and auto-instrumentation setup, see [Python OpenTelemetry (arize-phoenix-otel)](#3.2).

Sources: [packages/phoenix-otel/README.md:25-36]()

---

## 3.3. Python Evaluations (`arize-phoenix-evals`)

The `arize-phoenix-evals` package provides lightweight, composable building blocks for writing and running evaluations on LLM applications [packages/phoenix-evals/README.md:13-14](). It includes built-in metrics (hallucination detection, toxicity, faithfulness), prompt templates, and adapters for model SDKs like OpenAI, LiteLLM, and LangChain [packages/phoenix-evals/README.md:17-21]().

For complete evaluation metrics, custom classifier creation, DataFrame evaluation helpers, and the async executor pattern, see [Python Evaluations (arize-phoenix-evals)](#3.3).

Sources: [packages/phoenix-evals/README.md:13-21]()

---

## 3.4. TypeScript Client

The `@arizeai/phoenix-client` package is a type-safe TypeScript/JavaScript client generated from Phoenix's OpenAPI schema [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/overview.mdx:3-7](). It offers modular entrypoints for projects, prompts, datasets, experiments, spans, sessions, and traces [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/overview.mdx:6-53]().

For comprehensive usage examples, SDK converters for Vercel AI SDK and OpenAI, and type definitions, see [TypeScript Client](#3.4).

Sources: [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/overview.mdx:3-53]()

---

## 3.5. Command Line Interface (CLI)

The command-line tool (`px`/`pxi`) provides administrative capabilities and developer workflows directly from the terminal. It includes commands for project management, dataset ingestion, prompt versioning, annotations, and the interactive PXI terminal agent [js/packages/phoenix-cli/package.json:2-24]().

For command syntax, configuration profiles, and instrumentation scaffolding, see [Command Line Interface (CLI)](#3.5).

Sources: [js/packages/phoenix-cli/package.json:2-24]()

---

## 3.6. MCP Server

The `@arizeai/phoenix-mcp` package implements the Model Context Protocol (MCP) to integrate Phoenix directly with AI coding assistants like Claude Desktop and Cursor [js/packages/phoenix-mcp/README.md:29-44](). It exposes tools for querying projects, traces, spans, sessions, prompts, datasets, and experiments [js/packages/phoenix-mcp/README.md:31-39]().

For transport configuration, tool coverage details, and setup instructions, see [MCP Server](#3.6).

Sources: [js/packages/phoenix-mcp/README.md:29-44]()

### Code Entity Mapping

```mermaid
graph LR
    subgraph "Code Entity Space"
        createClient["phoenix-client.createClient()"] --> PhoenixClientClass["PhoenixClient Class"]
        updatePrompt["phoenix-client.updatePrompt()"] --> PromptManagementAPI["Prompt Management API"]
        pxi["phoenix-cli pxi command"] --> AgentChatTerminal["PXI Terminal Agent"]
    end
    
    subgraph "Natural Language Space"
        InitializeSDK["Initialize Phoenix SDK"]
        ManagePromptVersions["Manage Prompt Versions"]
        InteractiveDebugging["Interactive Debugging"]
    end
    
    InitializeSDK --> createClient
    ManagePromptVersions --> updatePrompt
    InteractiveDebugging --> pxi
    
    PhoenixClientClass --> "REST v1 Endpoints"
    PromptManagementAPI --> "PATCH /v1/prompts/{prompt_identifier}"
    AgentChatTerminal --> "Phoenix Intelligence (PXI)"
```

Sources: [js/packages/phoenix-client/CHANGELOG.md:13-35](), [js/packages/phoenix-client/README.md:66-130]()

---

# Page: Python Client (arize-phoenix-client)

# Python Client (arize-phoenix-client)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/phoenix/integrations/llm-providers/anthropic/anthropic-tracing.mdx](docs/phoenix/integrations/llm-providers/anthropic/anthropic-tracing.mdx)
- [js/packages/phoenix-client/examples/dataset_get_by_name.ts](js/packages/phoenix-client/examples/dataset_get_by_name.ts)
- [js/packages/phoenix-client/examples/get_session_turns.ts](js/packages/phoenix-client/examples/get_session_turns.ts)
- [js/packages/phoenix-client/src/datasets/appendDatasetExamples.ts](js/packages/phoenix-client/src/datasets/appendDatasetExamples.ts)
- [js/packages/phoenix-client/src/datasets/createDataset.ts](js/packages/phoenix-client/src/datasets/createDataset.ts)
- [js/packages/phoenix-client/src/datasets/getDataset.ts](js/packages/phoenix-client/src/datasets/getDataset.ts)
- [js/packages/phoenix-client/src/datasets/getDatasetExamples.ts](js/packages/phoenix-client/src/datasets/getDatasetExamples.ts)
- [js/packages/phoenix-client/src/datasets/getDatasetInfo.ts](js/packages/phoenix-client/src/datasets/getDatasetInfo.ts)
- [js/packages/phoenix-client/src/datasets/getDatasetInfoByName.ts](js/packages/phoenix-client/src/datasets/getDatasetInfoByName.ts)
- [js/packages/phoenix-client/src/experiments/getExperimentInfo.ts](js/packages/phoenix-client/src/experiments/getExperimentInfo.ts)
- [js/packages/phoenix-client/src/experiments/getExperimentRuns.ts](js/packages/phoenix-client/src/experiments/getExperimentRuns.ts)
- [js/packages/phoenix-client/src/projects/getProjects.ts](js/packages/phoenix-client/src/projects/getProjects.ts)
- [js/packages/phoenix-client/src/sessions/getSessionTurns.ts](js/packages/phoenix-client/src/sessions/getSessionTurns.ts)
- [js/packages/phoenix-client/src/sessions/index.ts](js/packages/phoenix-client/src/sessions/index.ts)
- [js/packages/phoenix-client/src/spans/getSpans.ts](js/packages/phoenix-client/src/spans/getSpans.ts)
- [js/packages/phoenix-client/src/types/datasets.ts](js/packages/phoenix-client/src/types/datasets.ts)
- [js/packages/phoenix-client/src/types/projects.ts](js/packages/phoenix-client/src/types/projects.ts)
- [js/packages/phoenix-client/test/datasets/appendDatasetExamples.test.ts](js/packages/phoenix-client/test/datasets/appendDatasetExamples.test.ts)
- [js/packages/phoenix-client/test/datasets/createDataset.test.ts](js/packages/phoenix-client/test/datasets/createDataset.test.ts)
- [js/packages/phoenix-client/test/datasets/getDataset.test.ts](js/packages/phoenix-client/test/datasets/getDataset.test.ts)
- [js/packages/phoenix-client/test/experiments/createExperiment.test.ts](js/packages/phoenix-client/test/experiments/createExperiment.test.ts)
- [js/packages/phoenix-client/test/experiments/getExperimentRuns.test.ts](js/packages/phoenix-client/test/experiments/getExperimentRuns.test.ts)
- [js/packages/phoenix-client/test/experiments/listExperiments.test.ts](js/packages/phoenix-client/test/experiments/listExperiments.test.ts)
- [js/packages/phoenix-client/test/experiments/resumeExperiment.test.ts](js/packages/phoenix-client/test/experiments/resumeExperiment.test.ts)
- [js/packages/phoenix-client/test/projects/getProjects.test.ts](js/packages/phoenix-client/test/projects/getProjects.test.ts)
- [js/packages/phoenix-client/test/sessions/getSessionTurns.test.ts](js/packages/phoenix-client/test/sessions/getSessionTurns.test.ts)
- [js/packages/phoenix-client/test/spans/getSpans.test.ts](js/packages/phoenix-client/test/spans/getSpans.test.ts)
- [packages/phoenix-client/examples/sessions/get_session_turns_example.py](packages/phoenix-client/examples/sessions/get_session_turns_example.py)
- [packages/phoenix-client/src/phoenix/client/client.py](packages/phoenix-client/src/phoenix/client/client.py)
- [packages/phoenix-client/src/phoenix/client/harbor/__init__.py](packages/phoenix-client/src/phoenix/client/harbor/__init__.py)
- [packages/phoenix-client/src/phoenix/client/harbor/_errors.py](packages/phoenix-client/src/phoenix/client/harbor/_errors.py)
- [packages/phoenix-client/src/phoenix/client/harbor/_naming.py](packages/phoenix-client/src/phoenix/client/harbor/_naming.py)
- [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py](packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py)
- [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py](packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py)
- [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py](packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py)
- [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py](packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py)
- [packages/phoenix-client/tests/client/resources/datasets/test_datasets.py](packages/phoenix-client/tests/client/resources/datasets/test_datasets.py)
- [packages/phoenix-client/tests/client/resources/experiments/test_experiment_urls.py](packages/phoenix-client/tests/client/resources/experiments/test_experiment_urls.py)
- [packages/phoenix-client/tests/client/resources/sessions/__init__.py](packages/phoenix-client/tests/client/resources/sessions/__init__.py)
- [packages/phoenix-client/tests/client/resources/sessions/test_sessions.py](packages/phoenix-client/tests/client/resources/sessions/test_sessions.py)
- [packages/phoenix-client/tests/client/resources/spans/test_spans.py](packages/phoenix-client/tests/client/resources/spans/test_spans.py)
- [packages/phoenix-client/tests/client/test_client.py](packages/phoenix-client/tests/client/test_client.py)
- [packages/phoenix-client/tests/client/utils/test_annotation_hepers.py](packages/phoenix-client/tests/client/utils/test_annotation_hepers.py)
- [requirements/canary/sdk/anthropic.txt](requirements/canary/sdk/anthropic.txt)
- [requirements/packages/phoenix-client.txt](requirements/packages/phoenix-client.txt)
- [tests/integration/client/test_datasets.py](tests/integration/client/test_datasets.py)
- [tests/integration/client/test_spans.py](tests/integration/client/test_spans.py)

</details>



## Purpose and scope

`arize-phoenix-client` provides synchronous and asynchronous Python interfaces for accessing Phoenix resources through the server API. This page covers client construction, resource APIs, DataFrame-oriented workflows, compatibility checks, and the Harbor and ATIF support identified for this package. [packages/phoenix-client/src/phoenix/client/client.py:20-70]()

Sources: [packages/phoenix-client/src/phoenix/client/client.py:20-70](), [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:112-116]()

---

## Architecture and Client Structure

`Client` and `AsyncClient` wrap `httpx` clients and expose resource handlers as properties. The synchronous client constructs one `ServerVersionGuard` and shares it across its resource objects; `Sessions` also receives the `Spans` resource. The resource layer uses generated API types from `phoenix.client.__generated__.v1` where available. [packages/phoenix-client/src/phoenix/client/client.py:5-15](), [packages/phoenix-client/src/phoenix/client/client.py:20-70](), [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:30-42]()

### Client and resource mapping

**Diagram: Client object graph and resource APIs**

```mermaid
graph TD
    Client["Client"] --> HTTP["httpx.Client"]
    AsyncClient["AsyncClient"] --> AsyncHTTP["httpx.AsyncClient"]
    Client --> Spans["Spans"]
    Client --> Traces["Traces"]
    Client --> Sessions["Sessions"]
    Client --> Datasets["Datasets"]
    Client --> Experiments["Experiments"]
    Client --> Prompts["Prompts"]
    Client --> Projects["Projects"]
    AsyncClient --> AsyncSpans["AsyncSpans"]
    AsyncClient --> AsyncTraces["AsyncTraces"]
    AsyncClient --> AsyncSessions["AsyncSessions"]
    AsyncClient --> AsyncDatasets["AsyncDatasets"]
    AsyncClient --> AsyncExperiments["AsyncExperiments"]
    AsyncClient --> AsyncPrompts["AsyncPrompts"]
    AsyncClient --> AsyncProjects["AsyncProjects"]
    Client --> Guard["ServerVersionGuard"]
    AsyncClient --> AsyncGuard["AsyncServerVersionGuard"]
    Sessions --> Spans
```

The synchronous client’s resource properties are initialized when its HTTP client is assigned. The asynchronous client uses `httpx.AsyncClient`; its resource classes have corresponding asynchronous variants. [packages/phoenix-client/src/phoenix/client/client.py:56-70](), [packages/phoenix-client/src/phoenix/client/client.py:136-170]()

Sources: [packages/phoenix-client/src/phoenix/client/client.py:56-70](), [packages/phoenix-client/src/phoenix/client/client.py:136-170]()

### Natural-language concepts mapped to code entities

**Diagram: “Client resource” terminology to Python entities**

```mermaid
graph LR
    User["Python caller"] --> Entry["Client"]
    Entry --> SpanDomain["Span operations"]
    SpanDomain --> SpanClass["Spans"]
    Entry --> DatasetDomain["Dataset operations"]
    DatasetDomain --> DatasetResource["Datasets"]
    DatasetResource --> DatasetModel["Dataset"]
    Entry --> ExperimentDomain["Experiment operations"]
    ExperimentDomain --> ExperimentResource["Experiments"]
    Entry --> PromptDomain["Prompt operations"]
    PromptDomain --> PromptResource["Prompts"]
    Entry --> SessionDomain["Session operations"]
    SessionDomain --> SessionResource["Sessions"]
    SessionResource --> SpanClass
    Entry --> TraceDomain["Trace operations"]
    TraceDomain --> TraceResource["Traces"]
```

The resource mapping shown here follows the `Client` initialization and property definitions. `Dataset` is a data wrapper for dataset metadata and examples, distinct from the `Datasets` API handler. [packages/phoenix-client/src/phoenix/client/client.py:63-70](), [packages/phoenix-client/src/phoenix/client/client.py:72-133](), [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:83-105]()

Sources: [packages/phoenix-client/src/phoenix/client/client.py:63-70](), [packages/phoenix-client/src/phoenix/client/client.py:72-133](), [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:83-105]()

---

## Initialization and Configuration

`Client` accepts `base_url`, `api_key`, additional `headers`, or an already-created `httpx.Client`. If no HTTP client is supplied, it resolves a base URL through `get_base_url()` when needed and builds a wrapped HTTP client. The configured default timeout is 10 seconds for connect, write, and pool operations, and 30 seconds for reads. [packages/phoenix-client/src/phoenix/client/client.py:17-17](), [packages/phoenix-client/src/phoenix/client/client.py:20-54]()

`AsyncClient` similarly accepts a base URL, API key, headers, or an existing `httpx.AsyncClient`; when it constructs the client, it uses the same default timeout configuration. [packages/phoenix-client/src/phoenix/client/client.py:136-169]()

| Configuration input | Client behavior |
|---|---|
| `base_url` | Selects the API endpoint; when omitted, the client calls `get_base_url()`. [packages/phoenix-client/src/phoenix/client/client.py:45-49]() |
| `api_key` | Passed into `_update_headers()` when the client creates its own HTTP client. [packages/phoenix-client/src/phoenix/client/client.py:49-52]() |
| `headers` | Passed into `_update_headers()` for a newly constructed client. [packages/phoenix-client/src/phoenix/client/client.py:49-52]() |
| `http_client` | Uses the supplied `httpx.Client` directly rather than constructing one. [packages/phoenix-client/src/phoenix/client/client.py:45-54]() |
| Default timeout | Connect 10s, read 30s, write 10s, pool 10s. [packages/phoenix-client/src/phoenix/client/client.py:17-17]() |

The synchronous client’s `_client` setter initializes the shared server-version guard and resource objects. This lets resource implementations check server capabilities where required. [packages/phoenix-client/src/phoenix/client/client.py:56-70]()

Sources: [packages/phoenix-client/src/phoenix/client/client.py:17-54](), [packages/phoenix-client/src/phoenix/client/client.py:56-70](), [packages/phoenix-client/src/phoenix/client/client.py:136-169]()

---

## Resource APIs

### Spans and annotations

`Spans` exposes methods for retrieving, logging, and managing spans and their annotations. Its API supports list-based and DataFrame-oriented workflows, and it receives an HTTP client plus an optional `ServerVersionGuard`. [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:112-116](), [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:168-175]()

`get_spans_dataframe()` accepts a `SpanQuery` and filters such as start and end time, project identifier or name, result limit, and root-span selection. The module also defines typed span attributes and serialization helpers for attribute filter values; non-finite float values are rejected, and booleans are JSON-serialized. [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:46-83](), [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:177-188]()

For annotation DataFrames, helper functions validate and chunk span and document annotation data. The annotation helper module supports IDs in DataFrame columns or index levels, including `span_id`, `trace_id`, `document_position`, and `session_id`. [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:13-20](), [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:27-60]()

The integration tests exercise both `Client` and `AsyncClient` for annotation creation and retrieval, including list and DataFrame results. [tests/integration/client/test_spans.py:37-97](), [tests/integration/client/test_spans.py:105-121]()

| Capability | Client API or implementation |
|---|---|
| Query spans as a DataFrame | `Spans.get_spans_dataframe()` accepts a `SpanQuery` and query filters. [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:177-188]() |
| Represent annotation kinds | `_AnnotatorKind` includes `LLM`, `CODE`, and `HUMAN`. [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:105-109]() |
| Validate annotation DataFrame IDs | `_IdConfig` and related helpers define ID handling and validation. [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:30-60](), [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:151-165]() |
| Test list and DataFrame annotation retrieval | Integration tests verify both response forms and annotation result fields. [tests/integration/client/test_spans.py:92-133]() |

Sources: [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:13-24](), [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:46-83](), [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:112-188](), [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:27-60](), [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:151-165](), [tests/integration/client/test_spans.py:37-133]()

### Datasets and examples

`Datasets` is the client resource for dataset operations. The `Dataset` wrapper combines dataset metadata with the examples data returned for a version. Its properties expose identifiers, name, description, version ID, examples, metadata, timestamps, and example count. It supports iteration, indexing, length queries, and conversion to a pandas DataFrame. [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:83-105](), [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:107-179]()

The upload request type `_InputDatasetExample` is defined manually because compiled request types are not available for the dataset upload route. It requires `input` and `output` mappings and optionally carries metadata, span ID, splits, and an ID. [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:45-58]()

Integration tests cover creating and retrieving a dataset with JSON examples, adding examples, and checking that adding examples produces a new dataset version. They run against both synchronous and asynchronous clients and include generator inputs. [tests/integration/client/test_datasets.py:19-73](), [tests/integration/client/test_datasets.py:75-116]()

| Dataset concept | Python representation |
|---|---|
| Dataset resource handler | `Datasets`, exposed through `Client.datasets`. [packages/phoenix-client/src/phoenix/client/client.py:69-70](), [packages/phoenix-client/src/phoenix/client/client.py:117-124]() |
| Dataset data wrapper | `Dataset`, initialized from dataset information and example data. [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:83-105]() |
| Example record | `_InputDatasetExample`, requiring `input` and `output`. [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:45-58]() |
| Tabular conversion | `Dataset.to_dataframe()` imports pandas on demand and raises an `ImportError` if pandas is unavailable. [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:179-208]() |
| Version behavior | Integration tests assert that appending examples changes `version_id`. [tests/integration/client/test_datasets.py:106-116]() |

Sources: [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:42-80](), [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:83-208](), [tests/integration/client/test_datasets.py:19-73](), [tests/integration/client/test_datasets.py:75-116]()

### Experiments and prompts

`Client` exposes `Experiments` and `Prompts` resource handlers, with asynchronous counterparts exposed by `AsyncClient`. [packages/phoenix-client/src/phoenix/client/client.py:7-13](), [packages/phoenix-client/src/phoenix/client/client.py:63-70](), [packages/phoenix-client/src/phoenix/client/client.py:72-133]()

The files provided for this page establish the resource wiring, but do not include the implementations of the experiment or prompt resource APIs. Accordingly, this page does not assert method-level behavior for those resources. The package requirements include provider SDK dependencies and `arize-phoenix-evals`; the Harbor dependency is conditional on Python 3.12 or later. [requirements/packages/phoenix-client.txt:1-9]()

Sources: [packages/phoenix-client/src/phoenix/client/client.py:7-13](), [packages/phoenix-client/src/phoenix/client/client.py:63-70](), [packages/phoenix-client/src/phoenix/client/client.py:72-133](), [requirements/packages/phoenix-client.txt:1-9]()

### Sessions and traces

`Sessions` is initialized with the HTTP client, `Spans`, and a server-version guard. Its `get()` method checks the `GET_SESSION` requirement, requests `v1/sessions/{session_id}`, raises for HTTP errors, and returns the response’s `data` value. [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:102-136]()

`list()` requires exactly one of `project_id` and `project_name`, returns an empty list for non-positive limits, and paginates using `next_cursor`. When a filter expression is provided, it checks the corresponding server capability before issuing the request. [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:138-193]()

`SessionTurn` and `SessionTurnIO` are typed experimental structures. A turn corresponds to a trace; its input and output are derived from root-span `input.value` and `output.value` attributes when present. [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:43-83]()

Sources: [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:43-83](), [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:102-193]()

---

## Implementation Details

### Request flow and compatibility guards

Resource handlers hold an HTTP client and, where applicable, a server-version guard. The synchronous client constructs the guard once and passes it into its resource objects. Individual resource methods can require a named capability before making a request; for example, `Sessions.get()` requires `GET_SESSION`, while `Sessions.list()` requires `LIST_PROJECT_SESSIONS` and conditionally requires `LIST_SESSIONS_FILTER_EXPRESSION`. [packages/phoenix-client/src/phoenix/client/client.py:60-70](), [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:102-112](), [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:132-165]()

**Diagram: Resource call path and capability check**

```mermaid
sequenceDiagram
    participant Caller["Python caller"]
    participant Client["Client"]
    participant Resource["Sessions or Spans"]
    participant Guard["ServerVersionGuard"]
    participant HTTP["httpx.Client"]
    participant API["Phoenix API"]

    Caller->>Client: "Select resource property"
    Client->>Resource: "Initialize with HTTP client and guard"
    Caller->>Resource: "Call resource method"
    Resource->>Guard: "require capability when needed"
    Resource->>HTTP: "Send HTTP request"
    HTTP->>API: "REST request"
    API-->>HTTP: "JSON response"
    HTTP-->>Resource: "HTTP response"
    Resource-->>Caller: "Parsed data or HTTP error"
```

For session retrieval, the resource performs the guard check before the request, calls `raise_for_status()`, and extracts `data` from the JSON response. [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:132-136]()

Sources: [packages/phoenix-client/src/phoenix/client/client.py:60-70](), [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:102-112](), [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:132-136]()

### Natural-language operations mapped to request paths

**Diagram: Session operations and concrete API paths**

```mermaid
graph LR
    User["Get a session"] --> GetMethod["Sessions.get"]
    GetMethod --> GetGuard["GET_SESSION"]
    GetGuard --> GetPath["v1/sessions/{session_id}"]
    User2["List project sessions"] --> ListMethod["Sessions.list"]
    ListMethod --> ProjectCheck["project_id XOR project_name"]
    ProjectCheck --> ListGuard["LIST_PROJECT_SESSIONS"]
    ListMethod --> ListPath["v1/projects/{project_identifier}/sessions"]
    ListMethod --> FilterCheck["LIST_SESSIONS_FILTER_EXPRESSION"]
    ListMethod --> Cursor["next_cursor pagination"]
```

The path, project-identifier validation, capability checks, and pagination behavior are implemented in `Sessions.get()` and `Sessions.list()`. [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:114-136](), [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:138-193]()

Sources: [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:114-136](), [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:138-193]()

### DataFrame annotation handling

Annotation helpers define ID configurations for span, trace, document, and session annotations. They can extract identifiers from DataFrame columns or index levels, with configured fallback columns such as `context.span_id` and `context.trace_id`. Validation rejects missing IDs and empty string identifiers; annotation DataFrames are chunked in batches of 100. [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:25-60](), [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:87-148](), [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:151-165]()

Tests verify that missing annotation cells are omitted from serialized results and that invalid document annotation identifiers are rejected before a request is sent. [packages/phoenix-client/tests/client/resources/spans/test_spans.py:37-56](), [packages/phoenix-client/tests/client/resources/spans/test_spans.py:59-97]()

Sources: [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:25-60](), [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:87-165](), [packages/phoenix-client/tests/client/resources/spans/test_spans.py:37-97]()

---

## Harbor and ATIF Support

The package requirements list `harbor>=0.21.0` when Python is 3.12 or later. The provided file listing also identifies `phoenix.client.harbor` modules, including `__init__.py`, `_errors.py`, and `_naming.py`. The supplied contents do not show their implementation, so this page does not describe specific plugin classes, entry points, or execution behavior. [requirements/packages/phoenix-client.txt:1-9](), [packages/phoenix-client/src/phoenix/client/harbor/__init__.py:1-5]()

ATIF (Agent Trace Import Format) helpers are in the requested scope, but their implementation was not included in the provided file contents. No helper names or conversion behavior are asserted here.

Sources: [requirements/packages/phoenix-client.txt:1-9](), [packages/phoenix-client/src/phoenix/client/harbor/__init__.py:1-5]()

---

## Testing and verification

The client tests exercise both transport-level behavior and integration with a running Phoenix server. Unit tests use `httpx.MockTransport` to inspect request paths and parameters, validate that invalid annotation input does not trigger a request, and check handling of missing annotation fields. [packages/phoenix-client/tests/client/resources/spans/test_spans.py:37-97](), [packages/phoenix-client/tests/client/resources/spans/test_spans.py:116-133]()

Integration tests parameterize span annotation and dataset workflows over synchronous and asynchronous clients. Dataset tests also cover iterable generators, retrieval by name, and version changes after adding examples. [tests/integration/client/test_spans.py:37-97](), [tests/integration/client/test_datasets.py:19-73](), [tests/integration/client/test_datasets.py:75-116]()

Sources: [packages/phoenix-client/tests/client/resources/spans/test_spans.py:37-97](), [packages/phoenix-client/tests/client/resources/spans/test_spans.py:116-133](), [tests/integration/client/test_spans.py:37-97](), [tests/integration/client/test_datasets.py:19-116]()

---

## References

- Client construction and resource properties: [packages/phoenix-client/src/phoenix/client/client.py:20-70](), [packages/phoenix-client/src/phoenix/client/client.py:72-170]()
- Span resource declarations and DataFrame query entry point: [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:30-42](), [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:112-188]()
- Dataset wrapper and example input shape: [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:42-58](), [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:83-208]()
- Annotation DataFrame ID handling: [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:25-60](), [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py:87-165]()
- Session retrieval and pagination: [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:102-193]()
- Span resource tests: [packages/phoenix-client/tests/client/resources/spans/test_spans.py:37-97](), [tests/integration/client/test_spans.py:37-133]()
- Dataset integration tests: [tests/integration/client/test_datasets.py:19-116]()
- Client package requirements: [requirements/packages/phoenix-client.txt:1-9]()

---

# Page: Python OpenTelemetry (arize-phoenix-otel)

# Python OpenTelemetry (arize-phoenix-otel)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/phoenix/get-started.mdx](docs/phoenix/get-started.mdx)
- [docs/phoenix/get-started/get-started-evaluations.mdx](docs/phoenix/get-started/get-started-evaluations.mdx)
- [docs/phoenix/get-started/get-started-tracing.mdx](docs/phoenix/get-started/get-started-tracing.mdx)
- [docs/phoenix/sdk-api-reference.mdx](docs/phoenix/sdk-api-reference.mdx)
- [docs/phoenix/sdk-api-reference/python/arize-phoenix-otel.mdx](docs/phoenix/sdk-api-reference/python/arize-phoenix-otel.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/overview.mdx](docs/phoenix/sdk-api-reference/rest-api/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/overview.mdx](docs/phoenix/sdk-api-reference/typescript/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx)
- [docs/phoenix/tracing/concepts-tracing/otel-openinference/phoenix-otel-helpers.mdx](docs/phoenix/tracing/concepts-tracing/otel-openinference/phoenix-otel-helpers.mdx)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing.mdx)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-using-phoenix-otel.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-using-phoenix-otel.mdx)
- [docs/snippets/agent-assisted-onboarding-prereq.mdx](docs/snippets/agent-assisted-onboarding-prereq.mdx)
- [docs/snippets/agent-assisted-onboarding.mdx](docs/snippets/agent-assisted-onboarding.mdx)
- [docs/snippets/connect-to-phoenix-env.mdx](docs/snippets/connect-to-phoenix-env.mdx)
- [js/packages/phoenix-config/src/envFile.test.ts](js/packages/phoenix-config/src/envFile.test.ts)
- [js/packages/phoenix-config/src/envFileParser.ts](js/packages/phoenix-config/src/envFileParser.ts)
- [packages/phoenix-client/src/phoenix/client/utils/config.py](packages/phoenix-client/src/phoenix/client/utils/config.py)
- [packages/phoenix-client/tests/.gitignore](packages/phoenix-client/tests/.gitignore)
- [packages/phoenix-client/tests/client/resources/experiments/test_get_func_name.py](packages/phoenix-client/tests/client/resources/experiments/test_get_func_name.py)
- [packages/phoenix-client/tests/client/utils/test_config.py](packages/phoenix-client/tests/client/utils/test_config.py)
- [packages/phoenix-client/tests/client/utils/test_template_formatters.py](packages/phoenix-client/tests/client/utils/test_template_formatters.py)
- [packages/phoenix-otel/CHANGELOG.md](packages/phoenix-otel/CHANGELOG.md)
- [packages/phoenix-otel/pyproject.toml](packages/phoenix-otel/pyproject.toml)
- [packages/phoenix-otel/src/phoenix/otel/__init__.py](packages/phoenix-otel/src/phoenix/otel/__init__.py)
- [packages/phoenix-otel/src/phoenix/otel/otel.py](packages/phoenix-otel/src/phoenix/otel/otel.py)
- [packages/phoenix-otel/src/phoenix/otel/settings.py](packages/phoenix-otel/src/phoenix/otel/settings.py)
- [packages/phoenix-otel/tests/test_exports.py](packages/phoenix-otel/tests/test_exports.py)
- [packages/phoenix-otel/tests/test_otel.py](packages/phoenix-otel/tests/test_otel.py)
- [packages/phoenix-otel/tests/test_settings.py](packages/phoenix-otel/tests/test_settings.py)
- [src/phoenix/trace/attributes.py](src/phoenix/trace/attributes.py)
- [tests/unit/trace/test_attributes.py](tests/unit/trace/test_attributes.py)
- [tutorials/quickstarts/python_quickstart.ipynb](tutorials/quickstarts/python_quickstart.ipynb)

</details>



The `arize-phoenix-otel` package provides a lightweight wrapper around OpenTelemetry primitives with Phoenix-aware defaults. It simplifies the configuration of OpenTelemetry tracing for Phoenix users by providing drop-in replacements for standard OpenTelemetry classes and a streamlined registration function that handles protocol inference, authentication, and auto-instrumentation.

For information about the full Phoenix platform server and UI, see [1. Phoenix Overview](). For REST/GraphQL API access, see [3.1. Python Client (arize-phoenix-client)](). For evaluation frameworks, see [3.3. Python Evaluations (arize-phoenix-evals)]().

## Package Overview

The `arize-phoenix-otel` package (version 0.17.2) is a standalone Python package that depends on OpenTelemetry SDK components and OpenInference semantic conventions [packages/phoenix-otel/pyproject.toml:1-34](). It provides Phoenix-specific defaults while maintaining full compatibility with the OpenTelemetry ecosystem.

**Key Dependencies:**
- `opentelemetry-sdk`: Core OpenTelemetry SDK [packages/phoenix-otel/pyproject.toml:29-29]().
- `opentelemetry-exporter-otlp`: OTLP exporters [packages/phoenix-otel/pyproject.toml:27-27]().
- `openinference-semantic-conventions`: OpenInference resource attributes [packages/phoenix-otel/pyproject.toml:30-30]().
- `openinference-instrumentation`: Auto-instrumentation framework [packages/phoenix-otel/pyproject.toml:31-31]().

**Supported Python Versions:** 3.11 - 3.14 [packages/phoenix-otel/pyproject.toml:5-5]().

Sources: [packages/phoenix-otel/pyproject.toml:1-34](), [packages/phoenix-otel/CHANGELOG.md:1-24]()

## Module Structure

The package architecture maps Phoenix-specific logic onto standard OpenTelemetry components. It re-exports OpenInference helpers and semantic conventions to provide a unified tracing surface [packages/phoenix-otel/src/phoenix/otel/otel.py:10-24]().

Title: arize-phoenix-otel Module Architecture
```mermaid
graph TB
    subgraph "phoenix.otel Package"
        Otel["otel.py<br/>Core Implementation"]
        Settings["settings.py<br/>Environment Config"]
    end
    
    subgraph "Exported Classes"
        TracerProvider["TracerProvider"]
        HTTPExporter["HTTPSpanExporter"]
        GRPCExporter["GRPCSpanExporter"]
        SimpleProc["SimpleSpanProcessor"]
        BatchProc["BatchSpanProcessor"]
        Register["register()"]
    end
    
    subgraph "OpenTelemetry SDK"
        OTelProvider["OTel TracerProvider"]
        OTelHTTP["OTel HTTPSpanExporter"]
        OTelGRPC["OTel GRPCSpanExporter"]
        OTelSimple["OTel SimpleSpanProcessor"]
        OTelBatch["OTel BatchSpanProcessor"]
    end
    
    Otel --> Settings
    Otel --> TracerProvider
    Otel --> HTTPExporter
    Otel --> GRPCExporter
    Otel --> SimpleProc
    Otel --> BatchProc
    Otel --> Register
    
    TracerProvider -.wraps.-> OTelProvider
    HTTPExporter -.wraps.-> OTelHTTP
    GRPCExporter -.wraps.-> OTelGRPC
    SimpleProc -.wraps.-> OTelSimple
    BatchProc -.wraps.-> OTelBatch
    
    Register --> TracerProvider
    Register --> HTTPExporter
    Register --> GRPCExporter
```

Sources: [packages/phoenix-otel/src/phoenix/otel/otel.py:10-24](), [packages/phoenix-otel/src/phoenix/otel/settings.py:1-26]()

## Core Components

### The `register()` Function

The `register()` function is the primary entry point for configuring OpenTelemetry tracing with Phoenix defaults [packages/phoenix-otel/src/phoenix/otel/otel.py:65-77](). It creates and configures a `TracerProvider` with automatic protocol inference, authentication, and optional auto-instrumentation.

**Function Signature:**
```python
def register(
    *,
    endpoint: Optional[str] = None,
    project_name: Optional[str] = None,
    batch: bool = False,
    set_global_tracer_provider: bool = True,
    headers: Optional[Dict[str, str]] = None,
    protocol: Optional[Literal["http/protobuf", "grpc"]] = None,
    verbose: bool = True,
    auto_instrument: bool = False,
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> _TracerProvider
```

Title: register() Execution Flow
```mermaid
graph TB
    Start["register() called"]
    ResolveProject["Resolve project_name<br/>from args or get_env_project_name()"]
    CreateResource["Create Resource with<br/>PROJECT_NAME attribute"]
    ResolveEndpoint["Resolve endpoint<br/>from args or environment"]
    InferProtocol["Infer protocol from endpoint<br/>or use explicit protocol arg"]
    ResolveAuth["Resolve authentication<br/>API key or custom headers"]
    CreateExporter["Create HTTPSpanExporter<br/>or GRPCSpanExporter"]
    CreateProcessor["Create SimpleSpanProcessor<br/>or BatchSpanProcessor"]
    CreateProvider["Create TracerProvider<br/>with resource and processor"]
    AutoInstrument{"auto_instrument<br/>== True?"}
    LoadInstrumentors["Load and instrument<br/>via entry points"]
    SetGlobal{"set_global_tracer_provider<br/>== True?"}
    RegisterGlobal["Set as global<br/>tracer provider"]
    PrintDetails{"verbose<br/>== True?"}
    LogConfig["Print configuration<br/>details to stdout"]
    Return["Return TracerProvider"]
    
    Start --> ResolveProject
    ResolveProject --> CreateResource
    CreateResource --> ResolveEndpoint
    ResolveEndpoint --> InferProtocol
    InferProtocol --> ResolveAuth
    ResolveAuth --> CreateExporter
    CreateExporter --> CreateProcessor
    CreateProcessor --> CreateProvider
    CreateProvider --> AutoInstrument
    AutoInstrument -->|Yes| LoadInstrumentors
    AutoInstrument -->|No| SetGlobal
    LoadInstrumentors --> SetGlobal
    SetGlobal -->|Yes| RegisterGlobal
    SetGlobal -->|No| PrintDetails
    RegisterGlobal --> PrintDetails
    PrintDetails -->|Yes| LogConfig
    PrintDetails -->|No| Return
    LogConfig --> Return
```

Sources: [packages/phoenix-otel/src/phoenix/otel/otel.py:145-243](), [packages/phoenix-otel/src/phoenix/otel/settings.py:15-31]()

### TracerProvider

The `TracerProvider` class is a drop-in replacement for the OpenTelemetry `TracerProvider` with Phoenix-aware defaults. It extends the OpenInference `TracerProvider` to add verbose logging and default configuration.

**Key Features:**
- **Resource Management**: Automatically merges project name into resource attributes [packages/phoenix-otel/src/phoenix/otel/otel.py:151-159]().
- **Verbose Logging**: Provides detailed configuration logging when `verbose=True`, including exporter and endpoint details.
- **Context Helpers**: Re-exports context management helpers like `using_session`, `using_user`, and `using_tags`.

Sources: [packages/phoenix-otel/src/phoenix/otel/otel.py:147-160]()

### Span Exporters

The package provides two span exporter classes with Phoenix-aware defaults:

#### HTTPSpanExporter
Exports spans using OTLP over HTTP/protobuf protocol. It defaults to using the `PHOENIX_COLLECTOR_ENDPOINT` environment variable and automatically appends `/v1/traces` if missing.

#### GRPCSpanExporter
Exports spans using OTLP over gRPC protocol. It defaults to port 4317 if no endpoint is specified.

Title: Protocol Selection Logic
```mermaid
graph TD
    Start["Determine Exporter Type"]
    ExplicitProtocol{"Protocol<br/>specified?"}
    HTTP["protocol == 'http/protobuf'"]
    GRPC["protocol == 'grpc'"]
    InferFromEndpoint["Infer from endpoint"]
    HasPort{"Endpoint has<br/>port?"}
    Port4317{"Port<br/>== 4317?"}
    HasV1Traces{"Endpoint contains<br/>'/v1/traces'?"}
    DefaultGRPC["Default to gRPC<br/>port 4317"]
    UseGRPC["Use GRPCSpanExporter"]
    UseHTTP["Use HTTPSpanExporter"]
    
    Start --> ExplicitProtocol
    ExplicitProtocol -->|Yes| HTTP
    ExplicitProtocol -->|Yes| GRPC
    ExplicitProtocol -->|No| InferFromEndpoint
    HTTP --> UseHTTP
    GRPC --> UseGRPC
    InferFromEndpoint --> HasPort
    HasPort -->|Yes| Port4317
    HasPort -->|No| HasV1Traces
    Port4317 -->|Yes| UseGRPC
    Port4317 -->|No| HasV1Traces
    HasV1Traces -->|Yes| UseHTTP
    HasV1Traces -->|No| DefaultGRPC
    DefaultGRPC --> UseGRPC
```

Sources: [packages/phoenix-otel/src/phoenix/otel/otel.py:37-63]()

## Configuration & .env.phoenix Discovery

Phoenix supports hierarchical configuration discovery via environment variables and a `.env.phoenix` file [packages/phoenix-otel/src/phoenix/otel/settings.py:28-29]().

### Environment Variables

| Environment Variable | Purpose | Default |
|---------------------|---------|---------|
| `PHOENIX_COLLECTOR_ENDPOINT` | Collector endpoint URL | `None` (OTel fallback) [packages/phoenix-otel/src/phoenix/otel/settings.py:15-15](). |
| `PHOENIX_PROJECT` | Canonical project name | `"default"` [packages/phoenix-otel/src/phoenix/otel/settings.py:18-18](). |
| `PHOENIX_PROJECT_NAME` | Alias for project name | `None` [packages/phoenix-otel/src/phoenix/otel/settings.py:21-21](). |
| `PHOENIX_API_KEY` | API key for authentication | `None` [packages/phoenix-otel/src/phoenix/otel/settings.py:23-23](). |
| `PHOENIX_DISCOVER_CONFIG` | Enable/Disable `.env.phoenix` | `True` [packages/phoenix-otel/src/phoenix/otel/settings.py:26-26](). |

### Discovery Logic
The package walks up from the current working directory to find the nearest `.env.phoenix` file [packages/phoenix-otel/src/phoenix/otel/settings.py:90-105](). Process environment variables always take precedence over values in the `.env.phoenix` file [packages/phoenix-otel/src/phoenix/otel/settings.py:121-125]().

Sources: [packages/phoenix-otel/src/phoenix/otel/settings.py:1-125](), [packages/phoenix-otel/tests/test_settings.py:104-168]()

## Auto-Instrumentation

The `register()` function supports automatic instrumentation of installed OpenInference libraries through Python entry points.

Title: Auto-Instrumentation Entry Point Flow
```mermaid
graph TB
    Start["register(auto_instrument=True)"]
    GetEntryPoints["entry_points(group='openinference.instrumentation.instrumentor')"]
    IterateEPs["For each entry point"]
    LoadEP["Load entry point"]
    GetInstrumentor["Get Instrumentor class"]
    CheckInstrumented{"Already<br/>instrumented?"}
    SkipEP["Skip entry point"]
    CallInstrument["instrumentor.instrument(<br/>tracer_provider=tp)"]
    HandleError["Catch and log errors"]
    NextEP["Next entry point"]
    Done["Auto-instrumentation complete"]
    
    Start --> GetEntryPoints
    GetEntryPoints --> IterateEPs
    IterateEPs --> LoadEP
    LoadEP --> GetInstrumentor
    GetInstrumentor --> CheckInstrumented
    CheckInstrumented -->|Yes| SkipEP
    CheckInstrumented -->|No| CallInstrument
    SkipEP --> NextEP
    CallInstrument --> HandleError
    HandleError --> NextEP
    NextEP -->|More EPs| IterateEPs
    NextEP -->|Done| Done
```

Sources: [packages/phoenix-otel/src/phoenix/otel/otel.py:1-100](), [packages/phoenix-otel/pyproject.toml:31-31]()

---

# Page: Python Evaluations (arize-phoenix-evals)

# Python Evaluations (arize-phoenix-evals)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/phoenix-evals/src/phoenix/evals/__init__.py](packages/phoenix-evals/src/phoenix/evals/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/evaluators.py](packages/phoenix-evals/src/phoenix/evals/evaluators.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/__init__.py](packages/phoenix-evals/src/phoenix/evals/llm/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/__init__.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/anthropic/adapter.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/anthropic/adapter.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/google/adapter.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/google/adapter.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/langchain/__init__.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/langchain/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/langchain/adapter.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/langchain/adapter.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/langchain/factories.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/langchain/factories.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/__init__.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/adapter.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/adapter.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/client.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/client.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/factories.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/factories.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/openai/adapter.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/openai/adapter.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/openai/factories.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/openai/factories.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/prompts.py](packages/phoenix-evals/src/phoenix/evals/llm/prompts.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/registries.py](packages/phoenix-evals/src/phoenix/evals/llm/registries.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/types.py](packages/phoenix-evals/src/phoenix/evals/llm/types.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py](packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py)
- [packages/phoenix-evals/src/phoenix/evals/tracing.py](packages/phoenix-evals/src/phoenix/evals/tracing.py)
- [packages/phoenix-evals/src/phoenix/evals/utils.py](packages/phoenix-evals/src/phoenix/evals/utils.py)
- [packages/phoenix-evals/tests/phoenix/evals/llm/adapters/anthropic/test_build_messages.py](packages/phoenix-evals/tests/phoenix/evals/llm/adapters/anthropic/test_build_messages.py)
- [packages/phoenix-evals/tests/phoenix/evals/llm/adapters/google/test_build_content.py](packages/phoenix-evals/tests/phoenix/evals/llm/adapters/google/test_build_content.py)
- [packages/phoenix-evals/tests/phoenix/evals/llm/adapters/langchain/test_build_prompt.py](packages/phoenix-evals/tests/phoenix/evals/llm/adapters/langchain/test_build_prompt.py)
- [packages/phoenix-evals/tests/phoenix/evals/llm/adapters/litellm/test_build_messages.py](packages/phoenix-evals/tests/phoenix/evals/llm/adapters/litellm/test_build_messages.py)
- [packages/phoenix-evals/tests/phoenix/evals/llm/adapters/openai/test_build_messages.py](packages/phoenix-evals/tests/phoenix/evals/llm/adapters/openai/test_build_messages.py)
- [packages/phoenix-evals/tests/phoenix/evals/llm/test_prompts.py](packages/phoenix-evals/tests/phoenix/evals/llm/test_prompts.py)
- [packages/phoenix-evals/tests/phoenix/evals/test_evaluators.py](packages/phoenix-evals/tests/phoenix/evals/test_evaluators.py)
- [packages/phoenix-evals/tests/phoenix/evals/test_utils.py](packages/phoenix-evals/tests/phoenix/evals/test_utils.py)
- [src/phoenix/experimental/evals/models/openai.py](src/phoenix/experimental/evals/models/openai.py)

</details>



The `arize-phoenix-evals` package is a comprehensive Python evaluation framework designed to enable automatic and customizable evaluation of large language model (LLM) outputs and AI applications. It provides abstractions for defining evaluators, supports multiple LLM providers via adapters, offers a templating system for prompt construction, and includes many pre-built evaluation metrics. The package integrates seamlessly with OpenTelemetry for tracing and performance instrumentation.

**Scope**: This page documents the internal architecture, key abstractions, LLM integration, pre-built metrics, and data flow within the evaluation framework. It focuses on the Python package `arize-phoenix-evals`. For client usage to log and query evaluations, see the Python client documentation [3.1]().

**Package Version**: `3.5.1` [packages/phoenix-evals/src/phoenix/evals/__init__.py:23-23]()

---

## Architecture Overview

The evaluation framework is layered to separate concerns between evaluation abstraction, LLM integration, prompt templating, and execution concurrency.

### Evaluation Data Flow

This diagram shows the flow of data from input datasets and prompts through the evaluation layers and finally to scored outputs, bridging the natural language space with code entities.

Title: Evaluation Data Flow
```mermaid
graph TB
    subgraph "Natural_Language_&_Data_Space"
        InputDF["pandas.DataFrame"]
        PromptText["Natural Language Prompt"]
    end
    
    subgraph "Evaluator_Layer"
        Evaluator["Evaluator (ABSTRACT)"]
        LLMEvaluator["LLMEvaluator"]
        ClassEval["ClassificationEvaluator"]
        CreateEval["create_evaluator()"]
        CreateClass["create_classifier()"]
    end
    
    subgraph "LLM_Abstraction_Space"
        LLM_Wrapper["LLM (Unified Wrapper)"]
        ProviderRegistry["PROVIDER_REGISTRY"]
        Adapter["BaseLLMAdapter"]
        OpenAIAdapter["OpenAIAdapter"]
        LiteLLMAdapter["LiteLLMAdapter"]
        LangChainAdapter["LangChainModelAdapter"]
    end
    
    subgraph "Execution_&_Tracing"
        AsyncExecutor["AsyncExecutor"]
        ConcurrencyController["ConcurrencyController (AIMD)"]
        TraceDecorator["@trace decorator"]
    end
    
    InputDF --> CreateEval
    InputDF --> CreateClass
    PromptText --> LLMEvaluator
    CreateEval --> LLMEvaluator
    CreateClass --> ClassEval
    LLMEvaluator --> LLM_Wrapper
    LLM_Wrapper --> ProviderRegistry
    ProviderRegistry --> Adapter
    Adapter --> OpenAIAdapter
    Adapter --> LiteLLMAdapter
    Adapter --> LangChainAdapter
    LLMEvaluator --> AsyncExecutor
    AsyncExecutor --> ConcurrencyController
    LLM_Wrapper --> TraceDecorator
    ClassEval --> Score["Score"]
```

**Sources**:  
- [packages/phoenix-evals/src/phoenix/evals/evaluators.py:328-330]()  
- [packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py:97-122]()  

---

## Core Abstractions

### Evaluator Base Class

The `Evaluator` abstract base class defines the protocol for evaluation logic. Subclasses implement specific evaluation methods — either with LLM prompts or code.

| Class                  | Role                                       | Reference                                       |
|------------------------|--------------------------------------------|------------------------------------------------|
| `Evaluator`            | Base abstract class for all evaluators.   | [packages/phoenix-evals/src/phoenix/evals/evaluators.py:328-330]()                      |
| `LLMEvaluator`         | Uses an LLM + prompt template for eval.   | [packages/phoenix-evals/src/phoenix/evals/evaluators.py:535-537]()                      |
| `ClassificationEvaluator` | Extends `LLMEvaluator` for categorical classification tasks (labels). | [packages/phoenix-evals/src/phoenix/evals/evaluators.py:738-740]()  |

Key capabilities include:

- **Input Mapping**: Evaluators accept arbitrary complex input dicts and use JSONPath or callable mappings to remap input fields to template variables or code params via `remap_eval_input` [packages/phoenix-evals/src/phoenix/evals/utils.py:175-187]().

- **Variable Binding**: The `bind_evaluator` utility produces a new evaluator instance with some template variables partially applied for reusability [packages/phoenix-evals/src/phoenix/evals/evaluators.py:1260-1262]().

- **Async Support**: Evaluators provide both synchronous `evaluate()` and asynchronous `async_evaluate()` interfaces, facilitating batch evaluation at scale [packages/phoenix-evals/src/phoenix/evals/evaluators.py:382-384]().

### Score Model

`Score` encapsulates evaluation results including numeric, categorical label, explanatory text, and metadata.

```python
@dataclass(frozen=True, init=False)
class Score:
    name: Optional[str] = None
    score: Optional[Union[float, int]] = None
    label: Optional[str] = None
    explanation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    kind: Optional[KindType] = None
    direction: DirectionType = "maximize"
```

- Useful for representing accuracy scores, label classifications, boolean checks, or detailed explanations.
- Includes a `to_dict()` method that excludes `None` values for clean serialization [packages/phoenix-evals/src/phoenix/evals/evaluators.py:284-304]().

**Sources**: [packages/phoenix-evals/src/phoenix/evals/evaluators.py:158-216]()

---

## LLM Provider Support

`LLM` is a unified wrapper class providing a consistent API for multiple LLM providers. It handles client instantiation, synchronous and asynchronous calls, and schema-driven object generation.

### Provider Registry and Adapters

The architecture supports multiple provider adapters through a registry system.

Title: Provider Adapter Hierarchy
```mermaid
graph LR
    subgraph "Code_Entity_Space"
        LLM["LLM class"]
        PR["PROVIDER_REGISTRY"]
        AR["AdapterRegistry"]
        subgraph "Adapters"
            OAI["OpenAIAdapter"]
            LIT["LiteLLMAdapter"]
            LC["LangChainModelAdapter"]
        end
    end

    LLM --> PR
    PR --> AR
    AR --> OAI
    AR --> LIT
    AR --> LC
```

- `OpenAIAdapter`: Manages OpenAI and Azure OpenAI clients and API interaction [packages/phoenix-evals/src/phoenix/evals/llm/adapters/openai/adapter.py:60-60]().
- `LiteLLMAdapter`: Wraps the LiteLLM client, enabling access to 100+ models/providers with capability probing [packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/adapter.py:66-66]().
- `LangChainModelAdapter`: Adapts LangChain chat models, using their `invoke` or `predict` methods, including structured outputs and tool calls [packages/phoenix-evals/src/phoenix/evals/llm/adapters/langchain/adapter.py:63-63]().

This system supports dynamic adapter registration and enables seamless switching between providers or concurrent multi-provider evaluation.

**Sources**:  
- [packages/phoenix-evals/src/phoenix/evals/llm/registries.py:39-147]()  
- [packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py:97-122]()  
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/openai/adapter.py:29-80]()  
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/adapter.py:66-151]()  
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/langchain/adapter.py:63-112]()  

### Execution & Concurrency

Efficient evaluation involves managing concurrency and API rate limits:

- **ConcurrencyController**: Implements an AIMD (Additive Increase Multiplicative Decrease) algorithm to adjust concurrency dynamically based on successes and failures, preventing rate limiting.

- **AsyncExecutor**: Uses a producer-consumer async model to batch and dispatch evaluation jobs, supporting high-throughput evaluation scenarios.

This combination helps maximize throughput while respecting provider limits.

**Sources**:
- [packages/phoenix-evals/src/phoenix/evals/evaluators.py:1-1262]()

---

## Built-in Metrics

The framework provides several pre-built evaluation metrics accessible as reusable evaluator instances or factory functions focused on common quality criteria.

| Evaluator                  | Purpose                                             | Reference                       |
|----------------------------|-----------------------------------------------------|--------------------------------|
| `FaithfulnessEvaluator`    | Checks if responses are factually consistent with data. | [packages/phoenix-evals/src/phoenix/evals/metrics/faithfulness.py:1]()  |
| `CorrectnessEvaluator`     | Checks correctness of outputs given references.      | [packages/phoenix-evals/src/phoenix/evals/metrics/correctness.py:1]()   |
| `DocumentRelevanceEvaluator` | Measures relevance of documents to queries.          | [packages/phoenix-evals/src/phoenix/evals/metrics/document_relevance.py:1]() |
| `ToolSelectionEvaluator`   | Validates whether correct tools were chosen in a pipeline. | [packages/phoenix-evals/src/phoenix/evals/metrics/tool_selection.py:1]() |
| `MatchesRegex`             | Static code evaluation via regex pattern matching.   | [packages/phoenix-evals/src/phoenix/evals/metrics/matches_regex.py:1]() |
| `PrecisionRecallFScore`    | Computes precision, recall, and F1 classification metrics. | [packages/phoenix-evals/src/phoenix/evals/metrics/precision_recall.py:8]() |
| `HallucinationEvaluator`   | Detects if the LLM output contains information not supported by the provided context. | [packages/phoenix-evals/src/phoenix/evals/metrics/hallucination.py:1]() |
| `RetrievalRelevanceEvaluator` | Assesses the relevance of retrieved documents to a given query. | [packages/phoenix-evals/src/phoenix/evals/metrics/retrieval_relevance.py:1]() |
| `ToxicityEvaluator`        | Identifies toxic content in LLM responses.           | [packages/phoenix-evals/src/phoenix/evals/metrics/toxicity.py:1]() |
| `UserFrictionEvaluator`    | Measures the perceived difficulty or frustration a user might experience. | [packages/phoenix-evals/src/phoenix/evals/metrics/user_friction.py:1]() |
| `ConcisenessEvaluator`     | Evaluates if the LLM response is brief and to the point. | [packages/phoenix-evals/src/phoenix/evals/metrics/conciseness.py:1]() |
| `RefusalEvaluator`         | Detects if the LLM refuses to answer a query.        | [packages/phoenix-evals/src/phoenix/evals/metrics/refusal.py:1]() |

Many use `ClassificationEvaluator` under the hood with curated prompt templates and choices for classification tasks.

**Sources**: [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:1-31]()

---

## Templating and Data Handling

### Prompt Templates

Phoenix uses an extensible prompt templating system to support flexible input composition:

- `PromptTemplate` manages structured prompt construction, supports variable substitution, and can handle multiple messages [packages/phoenix-evals/src/phoenix/evals/llm/prompts.py:1]().

- `SmartString`, a Pydantic type, ensures non-string fields like dicts/lists are JSON serialized for insertion into prompt templates, preserving semantic correctness [packages/phoenix-evals/src/phoenix/evals/evaluators.py:80-87]().

### Evaluation Execution Functions

Functions for batch evaluation of datasets:

| Function                | Description                                      | Reference               |
|-------------------------|------------------------------------------------|------------------------|
| `evaluate_dataframe`    | Runs synchronous batch evaluation on a DataFrame, returning a DataFrame of Scores. | [packages/phoenix-evals/src/phoenix/evals/evaluators.py:18]()   |
| `async_evaluate_dataframe` | Runs asynchronous batch evaluation with concurrency controls. | [packages/phoenix-evals/src/phoenix/evals/evaluators.py:14]()   |

They simplify the typical input/output pattern for automated benchmarking and evaluation for entire datasets.

**Sources**:  
- [packages/phoenix-evals/src/phoenix/evals/evaluators.py:1-154]()  
- [packages/phoenix-evals/src/phoenix/evals/llm/prompts.py:1]()  
- [packages/phoenix-evals/src/phoenix/evals/utils.py:175-187]()  

---

## Tracing and Instrumentation

The evaluation framework integrates rich OpenTelemetry tracing instrumentation to track evaluation operations end-to-end.

- Decorator `@trace` wraps key evaluation methods to create spans [packages/phoenix-evals/src/phoenix/evals/tracing.py:34]().

- Evaluator spans capture:
  - Input remapped data serialized as JSON (`remapped_eval_input` attribute) [packages/phoenix-evals/src/phoenix/evals/evaluators.py:113-115]().
  - Metadata such as `evaluator.kind`, evaluator class name [packages/phoenix-evals/src/phoenix/evals/evaluators.py:103-110]().
  - Output list of `Score` objects serialized to JSON [packages/phoenix-evals/src/phoenix/evals/evaluators.py:118-120]().

- The `LLM` wrapper extracts relevant tracing attributes such as model name and serialized prompt text with internal helpers `_get_llm_model_name` and `_get_prompt` for span attributes [packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py:19-70]().

This allows detailed visibility into evaluation performance, failures, request latencies, and trace correlation with model APIs.

**Sources**:  
- [packages/phoenix-evals/src/phoenix/evals/tracing.py:34-34]()  
- [packages/phoenix-evals/src/phoenix/evals/evaluators.py:91-121]()  
- [packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py:19-70]()  

---

# Summary

The `arize-phoenix-evals` Python package offers a modular, extensible framework for evaluation of LLM outputs and AI system behavior. It provides:

- Abstract and concrete evaluators for LLM-based and code-driven metrics.
- A unified LLM interface supporting multiple providers via adapters.
- Pre-built prompt templates and metrics for common evaluation tasks.
- Concurrency and rate-limit-aware execution engines.
- OpenTelemetry instrumentation for monitoring and observability.

This makes Phoenix evaluations a powerful toolkit for AI developers seeking programmatic, scalable, and pluggable evaluation workflows.

---

**Sources**:
- [packages/phoenix-evals/src/phoenix/evals/__init__.py:1-56]()
- [packages/phoenix-evals/src/phoenix/evals/evaluators.py:1-1262]()
- [packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py:1-180]()
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/openai/adapter.py:1-185]()
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/adapter.py:1-195]()
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/langchain/adapter.py:1-185]()
- [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:1-31]()
- [packages/phoenix-evals/src/phoenix/evals/utils.py:1-193]()
- [packages/phoenix-evals/src/phoenix/evals/tracing.py:1-34]()

---

# Page: TypeScript Client

# TypeScript Client

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx](docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/sessions.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/sessions.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/traces.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/traces.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx)
- [docs/phoenix/tracing/how-to-tracing/add-metadata/customize-spans.mdx](docs/phoenix/tracing/how-to-tracing/add-metadata/customize-spans.mdx)
- [docs/phoenix/tracing/how-to-tracing/add-metadata/instrumenting-prompt-templates-and-prompt-variables.mdx](docs/phoenix/tracing/how-to-tracing/add-metadata/instrumenting-prompt-templates-and-prompt-variables.mdx)
- [docs/phoenix/tracing/how-to-tracing/advanced/masking-span-attributes.mdx](docs/phoenix/tracing/how-to-tracing/advanced/masking-span-attributes.mdx)
- [docs/phoenix/tracing/how-to-tracing/filter-expressions.mdx](docs/phoenix/tracing/how-to-tracing/filter-expressions.mdx)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing/instrument.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing/instrument.mdx)
- [internal_docs/specs/session-filter-dsl.md](internal_docs/specs/session-filter-dsl.md)
- [internal_docs/specs/trace-filter-dsl.md](internal_docs/specs/trace-filter-dsl.md)
- [js/examples/apps/phoenix-experiment-runner/index.ts](js/examples/apps/phoenix-experiment-runner/index.ts)
- [js/examples/notebooks/phoenix_prompts_cross_sdk_tutorial.ipynb](js/examples/notebooks/phoenix_prompts_cross_sdk_tutorial.ipynb)
- [js/examples/notebooks/phoenix_prompts_openai_tutorial.ipynb](js/examples/notebooks/phoenix_prompts_openai_tutorial.ipynb)
- [js/examples/notebooks/phoenix_prompts_vercel_ai_sdk.ipynb](js/examples/notebooks/phoenix_prompts_vercel_ai_sdk.ipynb)
- [js/packages/phoenix-cli/src/commands/options.ts](js/packages/phoenix-cli/src/commands/options.ts)
- [js/packages/phoenix-client/examples/apply_prompt_vercel.ts](js/packages/phoenix-client/examples/apply_prompt_vercel.ts)
- [js/packages/phoenix-client/examples/resume_experiment.ts](js/packages/phoenix-client/examples/resume_experiment.ts)
- [js/packages/phoenix-client/src/config.ts](js/packages/phoenix-client/src/config.ts)
- [js/packages/phoenix-client/src/constants/serverRequirements.ts](js/packages/phoenix-client/src/constants/serverRequirements.ts)
- [js/packages/phoenix-client/src/experiments/helpers/toExperimentEvaluationRequestBody.ts](js/packages/phoenix-client/src/experiments/helpers/toExperimentEvaluationRequestBody.ts)
- [js/packages/phoenix-client/src/experiments/logging.ts](js/packages/phoenix-client/src/experiments/logging.ts)
- [js/packages/phoenix-client/src/experiments/resumeEvaluation.ts](js/packages/phoenix-client/src/experiments/resumeEvaluation.ts)
- [js/packages/phoenix-client/src/experiments/resumeExperiment.ts](js/packages/phoenix-client/src/experiments/resumeExperiment.ts)
- [js/packages/phoenix-client/src/experiments/runExperiment.ts](js/packages/phoenix-client/src/experiments/runExperiment.ts)
- [js/packages/phoenix-client/src/logger.ts](js/packages/phoenix-client/src/logger.ts)
- [js/packages/phoenix-client/src/prompts/sdks/constants.ts](js/packages/phoenix-client/src/prompts/sdks/constants.ts)
- [js/packages/phoenix-client/src/prompts/sdks/toAI.ts](js/packages/phoenix-client/src/prompts/sdks/toAI.ts)
- [js/packages/phoenix-client/src/prompts/sdks/toSDK.ts](js/packages/phoenix-client/src/prompts/sdks/toSDK.ts)
- [js/packages/phoenix-client/src/prompts/sdks/types.ts](js/packages/phoenix-client/src/prompts/sdks/types.ts)
- [js/packages/phoenix-client/src/schemas/llm/constants.ts](js/packages/phoenix-client/src/schemas/llm/constants.ts)
- [js/packages/phoenix-client/src/schemas/llm/converters.ts](js/packages/phoenix-client/src/schemas/llm/converters.ts)
- [js/packages/phoenix-client/src/schemas/llm/openai/converters.ts](js/packages/phoenix-client/src/schemas/llm/openai/converters.ts)
- [js/packages/phoenix-client/src/schemas/llm/types.ts](js/packages/phoenix-client/src/schemas/llm/types.ts)
- [js/packages/phoenix-client/src/schemas/llm/utils.ts](js/packages/phoenix-client/src/schemas/llm/utils.ts)
- [js/packages/phoenix-client/src/schemas/llm/vercel/messagePartSchemas.ts](js/packages/phoenix-client/src/schemas/llm/vercel/messagePartSchemas.ts)
- [js/packages/phoenix-client/src/schemas/llm/vercel/toolSchemas.ts](js/packages/phoenix-client/src/schemas/llm/vercel/toolSchemas.ts)
- [js/packages/phoenix-client/src/sessions/getSession.ts](js/packages/phoenix-client/src/sessions/getSession.ts)
- [js/packages/phoenix-client/src/sessions/listSessions.ts](js/packages/phoenix-client/src/sessions/listSessions.ts)
- [js/packages/phoenix-client/src/sessions/sessionUtils.ts](js/packages/phoenix-client/src/sessions/sessionUtils.ts)
- [js/packages/phoenix-client/src/spans/getSpanAnnotations.ts](js/packages/phoenix-client/src/spans/getSpanAnnotations.ts)
- [js/packages/phoenix-client/src/testing/phoenix-test-tracking.ts](js/packages/phoenix-client/src/testing/phoenix-test-tracking.ts)
- [js/packages/phoenix-client/src/traces/getTraces.ts](js/packages/phoenix-client/src/traces/getTraces.ts)
- [js/packages/phoenix-client/src/types/experiments.ts](js/packages/phoenix-client/src/types/experiments.ts)
- [js/packages/phoenix-client/src/types/sessions.ts](js/packages/phoenix-client/src/types/sessions.ts)
- [js/packages/phoenix-client/src/utils/noopLogger.ts](js/packages/phoenix-client/src/utils/noopLogger.ts)
- [js/packages/phoenix-client/test/experiments/helpers/getExperimentEvaluators.test.ts](js/packages/phoenix-client/test/experiments/helpers/getExperimentEvaluators.test.ts)
- [js/packages/phoenix-client/test/experiments/helpers/toExperimentEvaluationRequestBody.test.ts](js/packages/phoenix-client/test/experiments/helpers/toExperimentEvaluationRequestBody.test.ts)
- [js/packages/phoenix-client/test/experiments/resumeEvaluation.test.ts](js/packages/phoenix-client/test/experiments/resumeEvaluation.test.ts)
- [js/packages/phoenix-client/test/experiments/runExperiment.test.ts](js/packages/phoenix-client/test/experiments/runExperiment.test.ts)
- [js/packages/phoenix-client/test/experiments/runExperimentTracing.test.ts](js/packages/phoenix-client/test/experiments/runExperimentTracing.test.ts)
- [js/packages/phoenix-client/test/prompts/sdks/toAI.test.ts](js/packages/phoenix-client/test/prompts/sdks/toAI.test.ts)
- [js/packages/phoenix-client/test/sessions/getSession.test.ts](js/packages/phoenix-client/test/sessions/getSession.test.ts)
- [js/packages/phoenix-client/test/sessions/listSessions.test.ts](js/packages/phoenix-client/test/sessions/listSessions.test.ts)
- [js/packages/phoenix-client/test/testing/phoenix-test-tracking.test.ts](js/packages/phoenix-client/test/testing/phoenix-test-tracking.test.ts)
- [js/packages/phoenix-client/test/traces/getTraces.test.ts](js/packages/phoenix-client/test/traces/getTraces.test.ts)
- [js/packages/phoenix-config/src/env.test.ts](js/packages/phoenix-config/src/env.test.ts)
- [js/packages/phoenix-config/src/env.ts](js/packages/phoenix-config/src/env.ts)
- [js/packages/phoenix-mcp/src/config.ts](js/packages/phoenix-mcp/src/config.ts)
- [js/packages/phoenix-otel/README.md](js/packages/phoenix-otel/README.md)
- [js/packages/phoenix-otel/src/config.ts](js/packages/phoenix-otel/src/config.ts)
- [js/packages/phoenix-otel/src/index.ts](js/packages/phoenix-otel/src/index.ts)
- [js/packages/phoenix-otel/src/register.ts](js/packages/phoenix-otel/src/register.ts)
- [js/packages/phoenix-otel/test/register.test.ts](js/packages/phoenix-otel/test/register.test.ts)
- [js/packages/phoenix-otel/test/suppressTracing.test.ts](js/packages/phoenix-otel/test/suppressTracing.test.ts)
- [packages/phoenix-client/src/phoenix/client/constants/server_requirements.py](packages/phoenix-client/src/phoenix/client/constants/server_requirements.py)
- [packages/phoenix-client/src/phoenix/client/resources/prompts/__init__.py](packages/phoenix-client/src/phoenix/client/resources/prompts/__init__.py)
- [packages/phoenix-client/src/phoenix/client/resources/traces/__init__.py](packages/phoenix-client/src/phoenix/client/resources/traces/__init__.py)
- [packages/phoenix-client/tests/client/resources/experiments/test_evaluation_request_body.py](packages/phoenix-client/tests/client/resources/experiments/test_evaluation_request_body.py)
- [packages/phoenix-client/tests/client/resources/prompts/test_prompts.py](packages/phoenix-client/tests/client/resources/prompts/test_prompts.py)
- [packages/phoenix-client/tests/client/resources/traces/test_traces.py](packages/phoenix-client/tests/client/resources/traces/test_traces.py)

</details>



The `@arizeai/phoenix-client` package is the TypeScript SDK for the Phoenix REST API. It exposes resource APIs for datasets, experiments, spans, prompts, traces, sessions, and projects; performs schema validation; handles authentication and server-version gating; and provides converters that transform Phoenix prompt versions into OpenAI and Vercel AI SDK request shapes. It is the programmatic foundation for TypeScript integrations, automation, and the CLI/MCP tooling in this repository.

For the equivalent Python package, see [3.1 Python Client (arize-phoenix-client)]. For the tracing setup package used alongside the client, see [3.2 Python OpenTelemetry (arize-phoenix-otel)] and the `@arizeai/phoenix-otel` package described below.

Sources: [js/packages/phoenix-client/package.json:1-167](), [js/packages/phoenix-client/src/client.ts:40-80,110-180](), [js/packages/phoenix-otel/README.md:24-35]()

---

## Package Structure

The package is organized by domain, with each submodule re-exported from the package entry point:

| Area | Location | Role |
|---|---|---|
| Core client | `src/client.ts` | `createClient`, base URL/header resolution, server version checks |
| Datasets | `src/datasets/` | `createDataset`, `getDataset`, `appendDatasetExamples` |
| Experiments | `src/experiments/` | `runExperiment`, `resumeExperiment`, `resumeEvaluation`, tracing helpers |
| Prompts | `src/prompts/` | prompt get/create/update, `toSDK` and per-SDK converters |
| Spans / Traces / Sessions / Projects | `src/spans/`, `src/traces/`, `src/sessions/`, `src/projects/` | resource APIs |
| Testing | `src/testing/` | Vitest/Jest integration, `phoenix-test-tracking.ts` |
| Schemas | `src/schemas/llm/` | Zod schemas and LLM converters |
| Constants | `src/constants/serverRequirements.ts` | route/parameter version gates |
| Generated | `src/__generated__/api/v1.ts` | OpenAPI-generated types |

Key dependencies: `openapi-fetch` for typed REST calls, `zod` for runtime validation, `@arizeai/phoenix-config` for environment resolution, `@arizeai/phoenix-otel` for experiment tracing, and `async` for concurrency queues.

### Module Dependency Diagram

The diagram below maps the client's modules to the concrete directories and files in the source tree.

```mermaid
graph TB
    Index["src/index.ts entry"]
    Client["src/client.ts createClient"]
    Datasets["src/datasets/*"]
    Experiments["src/experiments/runExperiment.ts"]
    Prompts["src/prompts/sdks/toSDK.ts"]
    Constants["src/constants/serverRequirements.ts"]
    Generated["src/__generated__/api/v1.ts"]
    OtelPkg["@arizeai/phoenix-otel register"]
    ConfigPkg["@arizeai/phoenix-config"]

    Index --> Client
    Index --> Datasets
    Index --> Experiments
    Index --> Prompts
    Client --> Generated
    Client --> ConfigPkg
    Client --> Constants
    Experiments --> Datasets
    Experiments --> OtelPkg
    Prompts --> Generated
```

Sources: [js/packages/phoenix-client/src/index.ts:1-20](), [js/packages/phoenix-client/package.json:81-100](), [js/packages/phoenix-client/src/client.ts:1-80](), [js/packages/phoenix-client/src/experiments/runExperiment.ts:1-60]()

---

## Client Initialization and Configuration

`createClient(options?)` returns a `PhoenixClient` whose `config` carries the resolved `baseUrl` and headers, and whose methods are typed `openapi-fetch` calls against `/v1/...` routes.

### Configuration Resolution

Resolution order:

1. Explicit options passed to `createClient`.
2. Environment variables, read through `@arizeai/phoenix-config`:
   - `PHOENIX_ENDPOINT` (canonical base URL)
   - fallbacks such as `PHOENIX_COLLECTOR_ENDPOINT`
   - `PHOENIX_API_KEY` for bearer auth
   - `PHOENIX_PROJECT` for default project context
3. Default base URL `http://localhost:6006`.

| Option | Env variable | Default |
|---|---|---|
| `baseUrl` | `PHOENIX_ENDPOINT` | `http://localhost:6006` |
| `apiKey` | `PHOENIX_API_KEY` | `undefined` |
| `projectName` | `PHOENIX_PROJECT` | `undefined` |

Sources: [js/packages/phoenix-client/src/client.ts:20-90,110-180](), [js/packages/phoenix-config/src/env.ts:40-60]()

### Server Version Gating

Version-gated features are declared as constants in `src/constants/serverRequirements.ts`. Each `RouteRequirement` or `ParameterRequirement` records the minimum server version that supports it; calling functions such as `ensureServerCapability` produces a clear error when the connected server is too old. The client determines the server version from `/arize_phoenix_version` or the `x-phoenix-server-version` response header.

```ts
// Shape of a gate (see serverRequirements.ts)
// { kind: "route", method, path, minServerVersion: [major, minor, patch] }
```

Example requirements include `GET_SESSION` (13.5.0), `ADD_SESSION_NOTE` (14.17.0), `TRANSFER_TRACES` (20.4.0), and `CREATE_DATASET_SPLIT` (19.20.0).

Sources: [js/packages/phoenix-client/src/constants/serverRequirements.ts:1-236](), [js/packages/phoenix-client/src/experiments/resumeEvaluation.ts:166-200]()

---

## Dataset Management API

| Function | Purpose |
|---|---|
| `createDataset` | Create a dataset with optional initial examples |
| `getDataset` | Fetch dataset metadata and examples by name or ID |
| `appendDatasetExamples` | Append examples, producing a new dataset version |

Datasets are versioned and selectable by `splits` (for example `train`, `test`). Dataset types and Zod validators live in `src/types/datasets.ts`.

```ts
import { createClient, createDataset, getDataset } from "@arizeai/phoenix-client";

const client = createClient();
await createDataset({
  client,
  name: "my-dataset",
  description: "Sample dataset",
  examples: [{ input: { q: "Hello" }, output: { a: "Hi" } }],
});
const dataset = await getDataset({ client, dataset: { datasetName: "my-dataset" } });
```

Sources: [js/packages/phoenix-client/src/datasets/createDataset.ts:1-40](), [js/packages/phoenix-client/src/datasets/getDataset.ts:1-29](), [js/packages/phoenix-client/src/datasets/appendDatasetExamples.ts:1-20](), [js/packages/phoenix-client/src/types/datasets.ts:1-50]()

---

## Experiment Framework

### `runExperiment`

`runExperiment` in `src/experiments/runExperiment.ts` orchestrates a full run:

1. Resolve the dataset via `getDataset`.
2. Create the experiment record with `POST /v1/datasets/{dataset_id}/experiments` (see `prepareRecordedExperiment`, which sets `project_name`, `repetitions`, `splits`, and `version_id`).
3. Set up a tracer. `setupTracer` calls `register({ ..., global: false })` from `@arizeai/phoenix-otel` and optionally attaches it globally via `attachGlobalTracerProvider`.
4. Execute the task over examples using an `async` queue for concurrency.
5. Run evaluators on each output and upload results, unless `dryRun` or `record: false` is set.

`prepareDryRunExperiment` builds a local-only experiment object with a no-op tracer when recording is disabled.

| Parameter | Description | Default |
|---|---|---|
| `dataset` | `DatasetSelector` (name or ID, optional splits) | required |
| `task` | `ExperimentTask`: `(example: Example) => TaskOutput` | required |
| `evaluators` | `ExperimentEvaluatorLike[]` | `[]` |
| `experimentName` / `experimentDescription` / `experimentMetadata` | Experiment labeling | auto |
| `concurrency` | Parallel task executions | 5 |
| `repetitions` | Repeats per example | 1 |
| `dryRun` | `boolean` or example count | `false` |
| `record` | Upload results | `true` |
| `setGlobalTracerProvider` | Attach tracer globally | `true` |
| `useBatchSpanProcessor` | Batch span export | `true` |

Task output types are declared as `TaskOutput = string | boolean | number | object | null` in `src/types/experiments.ts`.

```ts
import { runExperiment } from "@arizeai/phoenix-client";

const result = await runExperiment({
  dataset: { datasetName: "my-dataset" },
  task: async (example) => ({ answer: `${example.input.q} world` }),
  evaluators: [
    {
      name: "length",
      kind: "CODE",
      evaluate: async ({ output }) => ({
        score: (output as { answer: string }).answer.length,
      }),
    },
  ],
});
```

Sources: [js/packages/phoenix-client/src/experiments/runExperiment.ts:64-232](), [js/packages/phoenix-client/src/types/experiments.ts:117-194](), [js/packages/phoenix-client/src/experiments/runExperiment.ts:174-190]()

### Resume Support

`resumeExperiment` and `resumeEvaluation` continue interrupted work. Both use a producer/consumer `Channel` (`src/utils/channel.ts`) with capacity `CHANNEL_CAPACITY_MULTIPLIER = 2`:

- The producer pages through incomplete runs (`DEFAULT_PAGE_SIZE = 50`) by calling the server.
- Workers run the task or evaluator on each item.
- `stopOnFirstError` aborts via `TaskAbortedError` or `EvaluationAbortedError`; fetch failures surface as `TaskFetchError` / `EvaluationFetchError` regardless of that flag.

`handleFetchError` turns JSON parse failures (typically an HTML 404 from an older server) into an upgrade message that includes the server version.

```mermaid
sequenceDiagram
    participant Caller as resumeExperiment
    participant Producer as Producer loop
    participant Chan as Channel
    participant Worker as Task workers
    participant API as Phoenix REST

    Caller->>Producer: start with experimentId
    loop pages of incomplete runs
        Producer->>API: GET incomplete runs (page size 50)
        API-->>Producer: ExampleWithId items
        Producer->>Chan: push TaskItem
    end
    Chan->>Worker: pop TaskItem
    Worker->>Worker: run task
    Worker->>API: record run output
```

Sources: [js/packages/phoenix-client/src/experiments/resumeExperiment.ts:44-240](), [js/packages/phoenix-client/src/experiments/resumeEvaluation.ts:41-210](), [js/packages/phoenix-client/src/utils/channel.ts]()

### Experiment Flow Diagram

```mermaid
flowchart TD
  User["User code"] -->|calls| runExperiment["runExperiment()"]
  runExperiment -->|getDataset| getDataset["getDataset()"]
  getDataset --> PhoenixAPI["Phoenix REST /v1"]
  runExperiment -->|POST experiments| PhoenixAPI
  runExperiment -->|setupTracer| Register["register() from phoenix-otel"]
  Register -->|OTLP export| TraceEndpoint["/v1/traces"]
  runExperiment -->|queue concurrency| Task["ExperimentTask"]
  Task --> Evaluators["Evaluator.evaluate"]
  Evaluators --> PhoenixAPI
```

Sources: [js/packages/phoenix-client/src/experiments/runExperiment.ts:174-380](), [js/packages/phoenix-otel/src/register.ts:1-60]()

---

## Prompt Management and SDK Converters

### Prompt Resource API

The prompt helpers in `src/prompts/` read, create, and update prompt versions via the generated v1 routes. Updates such as `PATCH /v1/prompts/{prompt_identifier}` are gated by `PATCH_PROMPT` (19.18.0) and deletes by `DELETE_PROMPT` (13.20.0) in `serverRequirements.ts`.

### SDK Converters

`toSDK({ sdk, prompt, variables })` in `src/prompts/sdks/toSDK.ts` dispatches to per-SDK converters. The conversion uses Phoenix's template format and substitutes `variables` into the messages.

| SDK | Output | File |
|---|---|---|
| `openai` | Chat completion params (`messages`, `model`, invocation params) | `src/prompts/sdks/toAI.ts` / `src/schemas/llm/openai/converters.ts` |
| `ai` (Vercel AI SDK) | `CoreMessage`-shaped messages plus tools | `src/prompts/sdks/toAI.ts` |

```ts
import { toSDK } from "@arizeai/phoenix-client/prompts";

const openaiParams = toSDK({
  sdk: "openai",
  prompt: myPhoenixPrompt,
  variables: { question: "What is Deno?" },
});
```

The Vercel AI SDK converter also translates Phoenix tool definitions into Zod schemas so that tool parameters are validated at call time.

Sources: [js/packages/phoenix-client/src/prompts/sdks/toSDK.ts:1-60](), [js/packages/phoenix-client/src/prompts/sdks/toAI.ts:1-40](), [js/packages/phoenix-client/src/schemas/llm/converters.ts:1-80](), [js/packages/phoenix-client/src/schemas/llm/openai/converters.ts:1-60](), [js/examples/notebooks/phoenix_prompts_openai_tutorial.ipynb:170-185](), [js/packages/phoenix-client/src/constants/serverRequirements.ts:195-221]()

### Converter Flow

```mermaid
graph LR
    PhoenixPrompt["PromptVersion (Phoenix format)"] --> ToSDK["toSDK()"]
    ToSDK -->|sdk openai| OpenAIConv["schemas/llm/openai/converters.ts"]
    ToSDK -->|sdk ai| AIConv["prompts/sdks/toAI.ts"]
    OpenAIConv --> OpenAIParams["ChatCompletionCreateParams"]
    AIConv --> VercelMessages["CoreMessage[] and tools"]
```

Sources: [js/packages/phoenix-client/src/prompts/sdks/toSDK.ts:1-60](), [js/packages/phoenix-client/src/prompts/sdks/toAI.ts:1-40]()

---

## Tracing Integration with `@arizeai/phoenix-otel`

`@arizeai/phoenix-otel` wraps OpenTelemetry for Node.js. Its root export re-exports `trace`, `context`, `SpanStatusCode`, `OTLPTraceExporter`, `NodeTracerProvider` types, the OpenInference semantic conventions, and the `@arizeai/openinference-core` helpers (`withSpan`, `traceChain`, `traceAgent`, `traceTool`, `observe`, and others).

`register(params)` in `src/register.ts` builds a `NodeTracerProvider`, resolves the endpoint from `url` or `PHOENIX_COLLECTOR_ENDPOINT`, adds a `LazyOpenInferenceSpanProcessor` (batch by default), and optionally registers globally. `RegisterParams` includes `projectName`, `url`, `apiKey`, `headers`, `batch`, `instrumentations`, `spanProcessors`, `global`, and `diagLogLevel`.

```mermaid
graph LR
    AppCode["Experiment task code"] --> Tracer["Tracer from NodeTracerProvider"]
    Tracer --> Processor["LazyOpenInferenceSpanProcessor"]
    Processor --> OTLP["OTLPTraceExporter"]
    OTLP --> Collector["Phoenix /v1/traces"]
```

Sources: [js/packages/phoenix-otel/src/index.ts:1-25](), [js/packages/phoenix-otel/src/register.ts:35-180](), [js/packages/phoenix-otel/README.md:45-110]()

---

## Integration Patterns

- **Experiments and evaluations:** `runExperiment` / `resumeExperiment` with concurrency and tracing.
- **Prompt portability:** store prompts in Phoenix and convert with `toSDK` at runtime.
- **Span and trace access:** `src/spans/` and `src/traces/` for querying and writing.
- **Sessions and annotations:** `src/sessions/listSessions.ts` and annotation helpers.
- **Downstream tooling:** the CLI and MCP server are built on this client.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant TS as "@arizeai/phoenix-client"
    participant API as Phoenix server

    Dev->>TS: createClient({ baseUrl, apiKey })
    Dev->>TS: getDataset({ dataset })
    TS->>API: GET /v1/datasets/...
    API-->>TS: dataset + examples
    Dev->>TS: runExperiment({ dataset, task, evaluators })
    TS->>API: POST /v1/datasets/{id}/experiments
    loop each example x repetition
        TS->>Dev: invoke task
        TS->>Dev: invoke evaluators
        TS->>API: record runs and evaluations
    end
```

Sources: [js/packages/phoenix-client/src/client.ts:110-180](), [js/packages/phoenix-client/src/experiments/runExperiment.ts:189-240]()

---

## Natural Language to Code Entity Mapping

```mermaid
graph TB
  subgraph "Concepts"
    Dataset["Dataset"]
    Experiment["Experiment"]
    Span["Span"]
    Prompt["Prompt"]
  end
  subgraph "Code entities"
    DatasetAPI["getDataset / createDataset in datasets/"]
    ExperimentAPI["runExperiment / resumeExperiment in experiments/"]
    SpanAPI["spans/ resource module"]
    PromptSDK["toSDK in prompts/sdks/toSDK.ts"]
  end
  Dataset --> DatasetAPI
  Experiment --> ExperimentAPI
  Span --> SpanAPI
  Prompt --> PromptSDK
```

Sources: [js/packages/phoenix-client/src/experiments/runExperiment.ts:174-190](), [js/packages/phoenix-client/src/datasets/getDataset.ts:1-29](), [js/packages/phoenix-client/src/prompts/sdks/toSDK.ts:1-60]()

---

## Summary

`@arizeai/phoenix-client` provides typed, validated access to Phoenix resources, an experiment runner with resume support and tracing, prompt conversion for OpenAI and the Vercel AI SDK, and server-version gating. Paired with `@arizeai/phoenix-otel`, it covers both programmatic evaluation workflows and instrumentation from TypeScript.

Sources: [js/packages/phoenix-client/package.json](), [js/packages/phoenix-client/src/client.ts](), [js/packages/phoenix-client/src/experiments/runExperiment.ts](), [js/packages/phoenix-client/src/prompts/sdks/toSDK.ts](), [js/packages/phoenix-otel/src/index.ts](), [js/packages/phoenix-client/src/constants/serverRequirements.ts]()

---

# Page: Command Line Interface (CLI)

# Command Line Interface (CLI)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-cli/SKILL.md](.agents/skills/phoenix-cli/SKILL.md)
- [.agents/skills/phoenix-evals/references/evaluate-dataframe-python.md](.agents/skills/phoenix-evals/references/evaluate-dataframe-python.md)
- [.agents/skills/phoenix-evals/references/experiments-datasets-python.md](.agents/skills/phoenix-evals/references/experiments-datasets-python.md)
- [.agents/skills/phoenix-evals/references/experiments-datasets-typescript.md](.agents/skills/phoenix-evals/references/experiments-datasets-typescript.md)
- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-cli.mdx](docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-cli.mdx)
- [js/packages/phoenix-cli/README.md](js/packages/phoenix-cli/README.md)
- [js/packages/phoenix-cli/src/banner.ts](js/packages/phoenix-cli/src/banner.ts)
- [js/packages/phoenix-cli/src/cli.ts](js/packages/phoenix-cli/src/cli.ts)
- [js/packages/phoenix-cli/src/commands/api.ts](js/packages/phoenix-cli/src/commands/api.ts)
- [js/packages/phoenix-cli/src/commands/auth.ts](js/packages/phoenix-cli/src/commands/auth.ts)
- [js/packages/phoenix-cli/src/commands/dataset.ts](js/packages/phoenix-cli/src/commands/dataset.ts)
- [js/packages/phoenix-cli/src/commands/experiment.ts](js/packages/phoenix-cli/src/commands/experiment.ts)
- [js/packages/phoenix-cli/src/commands/formatNoteMutation.ts](js/packages/phoenix-cli/src/commands/formatNoteMutation.ts)
- [js/packages/phoenix-cli/src/commands/formatSpans.ts](js/packages/phoenix-cli/src/commands/formatSpans.ts)
- [js/packages/phoenix-cli/src/commands/formatTraces.ts](js/packages/phoenix-cli/src/commands/formatTraces.ts)
- [js/packages/phoenix-cli/src/commands/index.ts](js/packages/phoenix-cli/src/commands/index.ts)
- [js/packages/phoenix-cli/src/commands/project.ts](js/packages/phoenix-cli/src/commands/project.ts)
- [js/packages/phoenix-cli/src/commands/prompt.ts](js/packages/phoenix-cli/src/commands/prompt.ts)
- [js/packages/phoenix-cli/src/commands/self.ts](js/packages/phoenix-cli/src/commands/self.ts)
- [js/packages/phoenix-cli/src/commands/session.ts](js/packages/phoenix-cli/src/commands/session.ts)
- [js/packages/phoenix-cli/src/commands/span.ts](js/packages/phoenix-cli/src/commands/span.ts)
- [js/packages/phoenix-cli/src/commands/trace.ts](js/packages/phoenix-cli/src/commands/trace.ts)
- [js/packages/phoenix-cli/src/curl.ts](js/packages/phoenix-cli/src/curl.ts)
- [js/packages/phoenix-cli/src/oauth.ts](js/packages/phoenix-cli/src/oauth.ts)
- [js/packages/phoenix-cli/src/pxi/App.tsx](js/packages/phoenix-cli/src/pxi/App.tsx)
- [js/packages/phoenix-cli/src/pxi/commands.ts](js/packages/phoenix-cli/src/pxi/commands.ts)
- [js/packages/phoenix-cli/src/pxi/draftEditor.ts](js/packages/phoenix-cli/src/pxi/draftEditor.ts)
- [js/packages/phoenix-cli/src/pxi/options.ts](js/packages/phoenix-cli/src/pxi/options.ts)
- [js/packages/phoenix-cli/src/pxi/tokenUsage.ts](js/packages/phoenix-cli/src/pxi/tokenUsage.ts)
- [js/packages/phoenix-cli/src/setup/deps/oauthLogin.ts](js/packages/phoenix-cli/src/setup/deps/oauthLogin.ts)
- [js/packages/phoenix-cli/src/trace.ts](js/packages/phoenix-cli/src/trace.ts)
- [js/packages/phoenix-cli/test/annotate.test.ts](js/packages/phoenix-cli/test/annotate.test.ts)
- [js/packages/phoenix-cli/test/annotationConfigGetCreate.test.ts](js/packages/phoenix-cli/test/annotationConfigGetCreate.test.ts)
- [js/packages/phoenix-cli/test/annotationConfigUpdate.test.ts](js/packages/phoenix-cli/test/annotationConfigUpdate.test.ts)
- [js/packages/phoenix-cli/test/api.test.ts](js/packages/phoenix-cli/test/api.test.ts)
- [js/packages/phoenix-cli/test/auth.test.ts](js/packages/phoenix-cli/test/auth.test.ts)
- [js/packages/phoenix-cli/test/banner.test.ts](js/packages/phoenix-cli/test/banner.test.ts)
- [js/packages/phoenix-cli/test/cli.test.ts](js/packages/phoenix-cli/test/cli.test.ts)
- [js/packages/phoenix-cli/test/datasetCommand.test.ts](js/packages/phoenix-cli/test/datasetCommand.test.ts)
- [js/packages/phoenix-cli/test/experimentCommand.test.ts](js/packages/phoenix-cli/test/experimentCommand.test.ts)
- [js/packages/phoenix-cli/test/notes.test.ts](js/packages/phoenix-cli/test/notes.test.ts)
- [js/packages/phoenix-cli/test/output.test.ts](js/packages/phoenix-cli/test/output.test.ts)
- [js/packages/phoenix-cli/test/projectList.test.ts](js/packages/phoenix-cli/test/projectList.test.ts)
- [js/packages/phoenix-cli/test/promptCommand.test.ts](js/packages/phoenix-cli/test/promptCommand.test.ts)
- [js/packages/phoenix-cli/test/pxiApp.test.tsx](js/packages/phoenix-cli/test/pxiApp.test.tsx)
- [js/packages/phoenix-cli/test/pxiCommands.test.ts](js/packages/phoenix-cli/test/pxiCommands.test.ts)
- [js/packages/phoenix-cli/test/pxiOptions.test.ts](js/packages/phoenix-cli/test/pxiOptions.test.ts)
- [js/packages/phoenix-cli/test/pxiTokenUsage.test.ts](js/packages/phoenix-cli/test/pxiTokenUsage.test.ts)
- [js/packages/phoenix-cli/test/self.test.ts](js/packages/phoenix-cli/test/self.test.ts)
- [js/packages/phoenix-cli/test/sessionAnnotationsNotes.test.ts](js/packages/phoenix-cli/test/sessionAnnotationsNotes.test.ts)
- [js/packages/phoenix-cli/test/sessionCommand.test.ts](js/packages/phoenix-cli/test/sessionCommand.test.ts)

</details>



The Phoenix CLI (`@arizeai/phoenix-cli`) is a Node.js-based command-line tool designed for interacting with Phoenix servers. It provides a terminal interface for managing Phoenix resources such as projects, traces, spans, datasets, experiments, prompts, and annotations. It is optimized for both interactive human use and programmatic consumption by AI coding agents (e.g., Claude Code, Cursor), or for piping into Unix utilities like `jq` [.agents/skills/phoenix-cli/SKILL.md:25-26](), [js/packages/phoenix-cli/README.md:25-26]().

The CLI is implemented in TypeScript, leveraging the `commander` library for command parsing, and wraps the `@arizeai/phoenix-client` SDK for API interactions [js/packages/phoenix-cli/src/cli.ts:3-24]().

---

## Installation and Configuration

### Installation

The CLI is released as an NPM package providing the executable named `px`. It can be installed globally or run transiently with `npx`:

```bash
npm install -g @arizeai/phoenix-cli
# Or run without installing:
npx @arizeai/phoenix-cli
```
Sources: [js/packages/phoenix-cli/README.md:29-32]()

### Configuration

The CLI determines connection details via a layered configuration resolution strategy. Configuration precedence is: CLI flags, process environment, active profile, `.env.phoenix`, then built-in defaults [js/packages/phoenix-cli/README.md:61-67]().

The environment variables supported include:

| Variable | Description |
| :--- | :--- |
| `PHOENIX_ENDPOINT` | Phoenix base URL (canonical) [js/packages/phoenix-cli/README.md:50]() |
| `PHOENIX_COLLECTOR_ENDPOINT` | Trace-export base URL; used if `PHOENIX_ENDPOINT` is unset [js/packages/phoenix-cli/README.md:51]() |
| `PHOENIX_HOST` | Legacy fallback for the base URL [js/packages/phoenix-cli/README.md:52]() |
| `PHOENIX_PROJECT` | Project name or ID (canonical) [js/packages/phoenix-cli/README.md:53]() |
| `PHOENIX_PROJECT_NAME` | Project name or ID (alias for above) [js/packages/phoenix-cli/README.md:54]() |
| `PHOENIX_API_KEY` | API key for authentication (if enabled) [js/packages/phoenix-cli/README.md:55]() |
| `PHOENIX_CLIENT_HEADERS` | Custom headers as JSON string [js/packages/phoenix-cli/README.md:56]() |
| `PHOENIX_CLI_DANGEROUSLY_ENABLE_DELETES` | Must be set to `true` to enable deletion commands [js/packages/phoenix-cli/README.md:57]()
| `PHOENIX_DISCOVER_CONFIG` | Set to `false` to disable `.env.phoenix` discovery [js/packages/phoenix-cli/README.md:67]()

Sources: [js/packages/phoenix-cli/README.md:48-67]()

### Profiles

Profiles save settings for different Phoenix instances (e.g., `prod`, `staging`). Active profiles are stored in a `settings.json` file, which includes a `$schema` field for editor autocompletion and validation [js/packages/phoenix-cli/README.md:69-97]().

```bash
px profile create prod --endpoint https://phoenix.example.com --project main --activate
px profile use prod
px profile edit prod
```
The `px profile` command supports `create`, `list`, `show`, `use`, `edit`, and `delete` operations [js/packages/phoenix-cli/README.md:74-81]().

Sources: [js/packages/phoenix-cli/README.md:69-104](), [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-cli.mdx:74-171]()

---

## Interactive PXI Terminal Agent

**PXI** (Phoenix Intelligence) is an interactive terminal chat interface. It connects to the same server-side agent that powers the in-browser assistant, allowing users to investigate traces and iterate on prompts directly from the terminal [js/packages/phoenix-cli/README.md:119-125](). `pxi` requires a Phoenix server on version **20.0.0 or newer** [js/packages/phoenix-cli/README.md:131-133](), as it leverages persisted agent sessions [MIGRATION.md:5-10]().

### PXI Implementation

The PXI interface is built using `ink` (React for CLI) and communicates with the Phoenix server via a dedicated agent API [js/packages/phoenix-cli/src/pxi/App.tsx:2-12]().

- **Session Management**: PXI maintains session state, handling busy or stale session errors when the same session is accessed via multiple clients (e.g., CLI and Browser) [js/packages/phoenix-cli/src/pxi/App.tsx:138-152](). Sessions are persisted server-side, allowing conversations to survive reloads and be continued across different clients [MIGRATION.md:8-10]().
- **Streaming**: Responses are streamed from the server-side agent. PXI handles markdown rendering and inline tool progress indicators [js/packages/phoenix-cli/src/pxi/App.tsx:56-60]().
- **Slash Commands**: Local commands like `/help`, `/clear`, `/new`, `/temporary`, `/sessions`, `/model`, `/compact`, and `/exit` allow users to manage the agent's context without leaving the chat [js/packages/phoenix-cli/README.md:135-138](). The `/compact` command summarizes older context into a checkpoint for long-running sessions [MIGRATION.md:13]().

Sources: [js/packages/phoenix-cli/README.md:119-139](), [js/packages/phoenix-cli/src/pxi/App.tsx:1-194](), [MIGRATION.md:5-15]()

---

## Architecture and Data Flow

The CLI is architected as a modular command-oriented tool structured around the `commander` framework. The main entrypoint creates a `Command` program that registers subcommands grouped by resource (noun) and actions (verbs) [js/packages/phoenix-cli/src/cli.ts:33-61]().

### Component Overview Diagram

```mermaid
graph TD
    subgraph "CLI Layer (Node.js)"
        Main["main() [js/packages/phoenix-cli/src/cli.ts:96-126]"]
        Program["createProgram() [js/packages/phoenix-cli/src/cli.ts:33-61]"]
        PXI["pxi command [js/packages/phoenix-cli/src/pxi/App.tsx:1-184]"]
        Commands["Command Handlers [js/packages/phoenix-cli/src/commands/*]"]
        ClientFactory["createPhoenixClient() [js/packages/phoenix-cli/src/client.ts]"]
        ConfigResolver["resolveConfig() [js/packages/phoenix-cli/src/config.ts]"]
    end

    subgraph "Phoenix SDK"
        PhoenixClient["PhoenixClient API Wrapper [@arizeai/phoenix-client]"]
    end

    subgraph "Phoenix Server"
        RESTAPI["REST API Endpoints (/v1/*)"]
        AgentAPI["Agent/PXI API (/v1/agent_sessions)"]
        MCPEndpoint["MCP Server (/mcp)"]
    end

    Main --> Program
    Program --> Commands
    Program --> PXI
    Commands --> ConfigResolver
    Commands --> ClientFactory
    ClientFactory --> PhoenixClient
    PhoenixClient --> RESTAPI
    PXI --> AgentAPI
    Commands --> MCPEndpoint
```

Sources: [js/packages/phoenix-cli/src/cli.ts:33-61](), [js/packages/phoenix-cli/src/pxi/App.tsx:5-12](), [docs/phoenix/integrations/remote-mcp.mdx:7-21](), [MIGRATION.md:27-28]()

---

## Command Reference

The CLI exposes commands grouped by resource nouns:

### Traces and Spans
- `px trace list` — List traces with filters [js/packages/phoenix-cli/src/commands/trace.ts:174-212]().
- `px trace get <id>` — Fetch a single trace by ID [js/packages/phoenix-cli/src/commands/trace.ts:157-167]().
- `px trace annotate <id>` — Add/update trace annotations [js/packages/phoenix-cli/src/commands/trace.ts:309-310]().
- `px trace add-note <id>` — Add a note to a trace [.agents/skills/phoenix-cli/SKILL.md:25]().
- `px trace delete <id>` — Delete a trace [.agents/skills/phoenix-cli/SKILL.md:26]().
- `px trace-annotations delete` — Delete trace annotations [.agents/skills/phoenix-cli/SKILL.md:27]().
- `px span list` — List spans with kind filters (e.g., `LLM`, `TOOL`) [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-cli.mdx:57]().
- `px span annotate <id>` — Add/update span annotations [.agents/skills/phoenix-cli/SKILL.md:30]().
- `px span add-note <id>` — Add a note to a span [.agents/skills/phoenix-cli/SKILL.md:31]().
- `px span delete <id>` — Delete a span [.agents/skills/phoenix-cli/SKILL.md:32]().
- `px span-annotations delete` — Delete span annotations [.agents/skills/phoenix-cli/SKILL.md:33]().

### Sessions
- `px session list` — List sessions [.agents/skills/phoenix-cli/SKILL.md:34]().
- `px session get <id>` — Fetch a single session by ID [.agents/skills/phoenix-cli/SKILL.md:35]().
- `px session annotate <id>` — Add/update session annotations [.agents/skills/phoenix-cli/SKILL.md:36]().
- `px session add-note <id>` — Add a note to a session [.agents/skills/phoenix-cli/SKILL.md:37]().
- `px session delete <id>` — Delete a session [.agents/skills/phoenix-cli/SKILL.md:38]().
- `px session-annotations delete` — Delete session annotations [.agents/skills/phoenix-cli/SKILL.md:39]().

### Datasets and Experiments
- `px dataset list|get|delete` — Manage trace datasets [js/packages/phoenix-cli/src/commands/dataset.ts](), [.agents/skills/phoenix-cli/SKILL.md:40-42]().
- `px experiment list|get|delete` — Manage evaluation experiments [js/packages/phoenix-cli/src/commands/experiment.ts](), [.agents/skills/phoenix-cli/SKILL.md:43-45]().

### Prompts
- `px prompt list|get|delete` — Manage prompt versions [js/packages/phoenix-cli/src/commands/prompt.ts](), [.agents/skills/phoenix-cli/SKILL.md:46-48]().

### Projects
- `px project list|get|delete` — Manage projects [.agents/skills/phoenix-cli/SKILL.md:49-51]().

### Annotation Configurations
- `px annotation-config list|get|create|update|delete` — Manage annotation configurations [.agents/skills/phoenix-cli/SKILL.md:52-56]().

### Authentication and Profiles
- `px auth login|logout|status` — Manage authentication sessions, including OAuth2 login [MIGRATION.md:33-39](), [.agents/skills/phoenix-cli/SKILL.md:57-59]().
- `px profile list|show|create|use|edit|delete` — Manage CLI profiles [.agents/skills/phoenix-cli/SKILL.md:60-65]().

### Setup and MCP
- `px setup` — Interactive flow to instrument apps. It can launch coding agents (Claude, Cursor) to apply OpenTelemetry instrumentation [js/packages/phoenix-cli/.agents/skills/phoenix-cli/SKILL.md:94-129](). The process involves writing a `.env.phoenix` file and optionally instrumenting the application source code [js/packages/phoenix-cli/README.md:176-193](). The command provides detailed exit codes to indicate success, unverified traces, or cancellation [js/packages/phoenix-cli/README.md:198-205]().
- `px setup mcp` — Configures the Phoenix **Model Context Protocol (MCP)** server for external agents. This allows agents to query Phoenix data directly [docs/phoenix/integrations/remote-mcp.mdx:37-41]().

### Other Commands
- `px api graphql <query>` — Execute GraphQL queries directly [.agents/skills/phoenix-cli/SKILL.md:66]().
- `px docs fetch` — Fetch documentation [.agents/skills/phoenix-cli/SKILL.md:67]().
- `px self update` — Update the CLI to the latest version [.agents/skills/phoenix-cli/SKILL.md:69]().

Sources: [.agents/skills/phoenix-cli/SKILL.md:23-69](), [js/packages/phoenix-cli/src/commands/index.ts:1-17](), [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-cli.mdx:50-60](), [MIGRATION.md:33-39]()

---

## Implementation Details

### Setup and Instrumentation Scaffolding
The `px setup` command automates the "Day 0" experience. When run with `--instrument`, it detects the project language, downloads Phoenix coding "skills", and hands off to a supported AI agent (like Claude Code) to perform the actual source code modifications [js/packages/phoenix-cli/.agents/skills/phoenix-cli/SKILL.md:94-129](). The process involves writing a `.env.phoenix` file and optionally instrumenting the application source code [js/packages/phoenix-cli/README.md:176-193](). The command provides detailed exit codes to indicate success, unverified traces, or cancellation [js/packages/phoenix-cli/README.md:198-205]().

### Safety Guards on Deletes
Delete commands are gated by the `PHOENIX_CLI_DANGEROUSLY_ENABLE_DELETES` environment variable. Even when enabled, the CLI prompts for confirmation unless the `-y` or `--yes` flag is provided [.agents/skills/phoenix-cli/SKILL.md:72-76]().

### Open Coding and Axial Coding
The CLI supports workflows for qualitative analysis of traces, spans, and sessions through "Open Coding" and "Axial Coding".
- **Open Coding**: Involves free-form note-taking against sampled traces, spans, or sessions to identify initial observations and failure modes. The unit of analysis (trace, span, or session) is chosen based on the nature of the problem [references/open-coding.md:1-17](). Notes are stored in a local sidecar file (`.px/coding/<sanitized-identifier>.jsonl`) [references/open-coding.md:64-67]().
- **Axial Coding**: Groups these open-ended observations into structured failure taxonomies. It reuses the `coding annotation identifier` from open coding and allows for attributing labels at different levels (trace, span, or session) than the original notes [references/axial-coding.md:1-29](). Axial labels are also recorded in a local sidecar file (`.px/coding/<sanitized-identifier>-axial.jsonl`) [references/axial-coding.md:16-17]().

Sources: [js/packages/phoenix-cli/.agents/skills/phoenix-cli/SKILL.md:72-129](), [js/packages/phoenix-cli/README.md:176-205](), [references/open-coding.md:1-89](), [references/axial-coding.md:1-95]()

---

## Bridging Natural Language to Code Entities

### CLI Command Dispatch Flow

```mermaid
graph TD
    NL_Input["User: 'px dataset list'"] --> Main["main() [js/packages/phoenix-cli/src/cli.ts:96-126]"]
    Main --> CreateProg["createProgram() [js/packages/phoenix-cli/src/cli.ts:33-61]"]
    CreateProg --> DatasetCmd["createDatasetCommand() [js/packages/phoenix-cli/src/commands/dataset.ts:1-20]"]
    DatasetCmd --> ListVerb["Command.command('list')"]
    ListVerb --> Action["Handler: client.GET('/v1/datasets')"]
    Action --> SDK["PhoenixClient [packages/phoenix-client]"]
    SDK --> API["REST Endpoint: /v1/datasets"]
```

Sources: [js/packages/phoenix-cli/src/cli.ts:33-61](), [js/packages/phoenix-cli/src/commands/dataset.ts:1-20]()

### PXI Agent Interaction Flow

```mermaid
graph TD
    UserChat["User Input: 'Why did trace X fail?'"] --> PxiApp["PxiApp [js/packages/phoenix-cli/src/pxi/App.tsx:1-184]"]
    PxiApp --> PxiClient["createPxiChatClient [js/packages/phoenix-cli/src/pxi/client.ts:6-12]"]
    PxiClient --> ServerAgent["Phoenix Server Agent API [/v1/agent_sessions]"]
    ServerAgent --> Tools["Agent Tools (Search, Trace Fetch)"]
    Tools --> PhoenixDB["Phoenix Database"]
    ServerAgent --> Stream["SSE/Streaming Response"]
    Stream --> PxiApp
    PxiApp --> Terminal["Ink Terminal Output"]
```

Sources: [js/packages/phoenix-cli/src/pxi/App.tsx:5-60](), [js/packages/phoenix-cli/src/pxi/client.ts:6-12](), [MIGRATION.md:27-28]()

---

### Sources
- [.agents/skills/phoenix-cli/SKILL.md:1-170]()
- [.agents/skills/phoenix-cli/references/axial-coding.md:1-95]()
- [.agents/skills/phoenix-cli/references/open-coding.md:1-89]()
- [MIGRATION.md:5-30]()
- [docs/phoenix/integrations/remote-mcp.mdx:1-190]()
- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-cli.mdx:1-205]()
- [js/packages/phoenix-cli/README.md:1-150]()
- [js/packages/phoenix-cli/src/cli.ts:1-126]()
- [js/packages/phoenix-cli/src/commands/dataset.ts:1-20]()
- [js/packages/phoenix-cli/src/commands/index.ts:1-17]()
- [js/packages/phoenix-cli/src/commands/trace.ts]()
- [js/packages/phoenix-cli/src/pxi/App.tsx:1-184]()
- [js/packages/phoenix-cli/src/pxi/client.ts:6-12]()

---

# Page: MCP Server

# MCP Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-tracing/README.md](.agents/skills/phoenix-tracing/README.md)
- [.agents/skills/phoenix-tracing/SKILL.md](.agents/skills/phoenix-tracing/SKILL.md)
- [.agents/skills/phoenix-tracing/references/annotations-python.md](.agents/skills/phoenix-tracing/references/annotations-python.md)
- [.agents/skills/phoenix-tracing/references/instrumentation-atif-python.md](.agents/skills/phoenix-tracing/references/instrumentation-atif-python.md)
- [.agents/skills/phoenix-tracing/references/setup-python.md](.agents/skills/phoenix-tracing/references/setup-python.md)
- [README.md](README.md)
- [docs/phoenix/evaluation/pre-built-metrics/completeness.mdx](docs/phoenix/evaluation/pre-built-metrics/completeness.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/conciseness.mdx](docs/phoenix/evaluation/pre-built-metrics/conciseness.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/pii-detection.mdx](docs/phoenix/evaluation/pre-built-metrics/pii-detection.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/refusal.mdx](docs/phoenix/evaluation/pre-built-metrics/refusal.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/user-friction.mdx](docs/phoenix/evaluation/pre-built-metrics/user-friction.mdx)
- [docs/phoenix/pxi.mdx](docs/phoenix/pxi.mdx)
- [evals/harbor/jobs/trail-benchmark-dev-no-code-mode.yaml](evals/harbor/jobs/trail-benchmark-dev-no-code-mode.yaml)
- [js/packages/phoenix-client/README.md](js/packages/phoenix-client/README.md)
- [js/packages/phoenix-evals/README.md](js/packages/phoenix-evals/README.md)
- [js/packages/phoenix-mcp/README.md](js/packages/phoenix-mcp/README.md)
- [js/packages/phoenix-mcp/src/index.ts](js/packages/phoenix-mcp/src/index.ts)
- [js/packages/phoenix-mcp/src/projectTools.ts](js/packages/phoenix-mcp/src/projectTools.ts)
- [packages/phoenix-client/README.md](packages/phoenix-client/README.md)
- [packages/phoenix-evals/README.md](packages/phoenix-evals/README.md)
- [packages/phoenix-otel/README.md](packages/phoenix-otel/README.md)
- [src/phoenix/server/agents/agent_factory.py](src/phoenix/server/agents/agent_factory.py)
- [src/phoenix/server/agents/capabilities/tools/external/__init__.py](src/phoenix/server/agents/capabilities/tools/external/__init__.py)
- [src/phoenix/server/agents/capabilities/tools/internal/bash.py](src/phoenix/server/agents/capabilities/tools/internal/bash.py)
- [src/phoenix/server/agents/prompts/__init__.py](src/phoenix/server/agents/prompts/__init__.py)
- [src/phoenix/server/agents/prompts/skills/phoenix-graphql/SKILL.md](src/phoenix/server/agents/prompts/skills/phoenix-graphql/SKILL.md)
- [src/phoenix/server/agents/prompts/static/base/BASE_INSTRUCTIONS.xml](src/phoenix/server/agents/prompts/static/base/BASE_INSTRUCTIONS.xml)
- [src/phoenix/server/agents/prompts/tools/PHOENIX_MCP_TOOL_INSTRUCTIONS.xml.j2](src/phoenix/server/agents/prompts/tools/PHOENIX_MCP_TOOL_INSTRUCTIONS.xml.j2)
- [src/phoenix/server/api/graphql_execute.py](src/phoenix/server/api/graphql_execute.py)
- [src/phoenix/server/mcp/graphql/__init__.py](src/phoenix/server/mcp/graphql/__init__.py)
- [src/phoenix/server/mcp/graphql/output.py](src/phoenix/server/mcp/graphql/output.py)
- [src/phoenix/server/mcp/graphql/tools.py](src/phoenix/server/mcp/graphql/tools.py)
- [src/phoenix/server/mcp/skills/__init__.py](src/phoenix/server/mcp/skills/__init__.py)
- [src/phoenix/server/mcp/sql/__init__.py](src/phoenix/server/mcp/sql/__init__.py)
- [src/phoenix/server/mcp/sql/allowlist.py](src/phoenix/server/mcp/sql/allowlist.py)
- [src/phoenix/server/mcp/sql/execute.py](src/phoenix/server/mcp/sql/execute.py)
- [src/phoenix/server/mcp/sql/manifest.py](src/phoenix/server/mcp/sql/manifest.py)
- [src/phoenix/server/mcp/sql/parse.py](src/phoenix/server/mcp/sql/parse.py)
- [src/phoenix/server/mcp/sql/rewrite.py](src/phoenix/server/mcp/sql/rewrite.py)
- [src/phoenix/server/mcp/sql/tools.py](src/phoenix/server/mcp/sql/tools.py)
- [src/phoenix/server/mcp_server.py](src/phoenix/server/mcp_server.py)
- [tests/unit/server/agents/capabilities/test_external_tools.py](tests/unit/server/agents/capabilities/test_external_tools.py)
- [tests/unit/server/agents/capabilities/test_phoenix_mcp.py](tests/unit/server/agents/capabilities/test_phoenix_mcp.py)
- [tests/unit/server/agents/capabilities/tools/internal/test_bash.py](tests/unit/server/agents/capabilities/tools/internal/test_bash.py)
- [tests/unit/server/agents/prompts/test_static_prompts.py](tests/unit/server/agents/prompts/test_static_prompts.py)
- [tests/unit/server/agents/test_agent_factory.py](tests/unit/server/agents/test_agent_factory.py)
- [tests/unit/server/mcp/sql/admission_corpus.py](tests/unit/server/mcp/sql/admission_corpus.py)
- [tests/unit/server/mcp/sql/admission_fixtures.py](tests/unit/server/mcp/sql/admission_fixtures.py)
- [tests/unit/server/mcp/sql/conftest.py](tests/unit/server/mcp/sql/conftest.py)
- [tests/unit/server/mcp/sql/test_ddl.py](tests/unit/server/mcp/sql/test_ddl.py)
- [tests/unit/server/mcp/sql/test_execute.py](tests/unit/server/mcp/sql/test_execute.py)
- [tests/unit/server/mcp/sql/test_liveness.py](tests/unit/server/mcp/sql/test_liveness.py)
- [tests/unit/server/mcp/sql/test_manifest.py](tests/unit/server/mcp/sql/test_manifest.py)
- [tests/unit/server/mcp/sql/test_node_coverage.py](tests/unit/server/mcp/sql/test_node_coverage.py)
- [tests/unit/server/mcp/sql/test_parse.py](tests/unit/server/mcp/sql/test_parse.py)
- [tests/unit/server/mcp/sql/test_rewrite.py](tests/unit/server/mcp/sql/test_rewrite.py)
- [tests/unit/server/mcp/test_skills.py](tests/unit/server/mcp/test_skills.py)
- [tests/unit/server/test_app_mcp_mount.py](tests/unit/server/test_app_mcp_mount.py)

</details>



## Purpose and Scope

The MCP server exposes Phoenix capabilities to AI assistants through the Model Context Protocol. The JavaScript package, `@arizeai/phoenix-mcp`, runs as a stdio server and uses the Phoenix TypeScript client to access the Phoenix API. Phoenix also implements an in-process MCP server mounted at `/mcp`; it derives tools from the REST API and dispatches calls back into the Phoenix application. These are distinct implementations: the package is a standalone client-facing server, while the mounted server is part of the Phoenix backend. [js/packages/phoenix-mcp/README.md:29-45](), [js/packages/phoenix-mcp/src/index.ts:1-18](), [src/phoenix/server/mcp_server.py:1-8](), [src/phoenix/server/mcp_server.py:82-87]()

Sources: [js/packages/phoenix-mcp/README.md:29-45](), [js/packages/phoenix-mcp/src/index.ts:1-18](), [src/phoenix/server/mcp_server.py:1-8](), [src/phoenix/server/mcp_server.py:82-87]()

---

## Architecture Overview

The standalone package initializes configuration and a Phoenix client, creates an MCP server, registers tool groups, and connects the server to `StdioServerTransport`. The backend implementation instead creates a `FastMCP` server from Phoenix’s REST API schema and mounts its ASGI app at `/mcp`. [js/packages/phoenix-mcp/src/index.ts:20-55](), [src/phoenix/server/mcp_server.py:1-8](), [src/phoenix/server/mcp_server.py:82-87]()

### MCP Server Data Flow

**Diagram: Standalone package tool-call path**

```mermaid
flowchart LR
    User["Natural-language request"]
    Assistant["MCP client"]
    Transport["StdioServerTransport"]
    Server["McpServer"]
    Initializers["initializePromptTools / initializeProjectTools / initializeTraceTools"]
    Client["createPhoenixClient"]
    API["Phoenix REST API"]

    User --> Assistant --> Transport --> Server
    Server --> Initializers
    Initializers --> Client --> API
```

Sources: [js/packages/phoenix-mcp/src/index.ts:3-18](), [js/packages/phoenix-mcp/src/index.ts:28-44](), [js/packages/phoenix-mcp/src/index.ts:46-55]()

**Diagram: Backend MCP dispatch path**

```mermaid
flowchart LR
    Assistant["MCP client"]
    Mount["MCP_MOUNT_PATH /mcp"]
    FastMCP["FastMCP server"]
    OpenAPI["Phoenix REST OpenAPI schema"]
    Dispatch["In-process ASGI transport"]
    App["Phoenix FastAPI app"]
    Endpoint["/v1 REST operation"]

    Assistant --> Mount --> FastMCP
    OpenAPI --> FastMCP
    FastMCP --> Dispatch --> App --> Endpoint
```

Sources: [src/phoenix/server/mcp_server.py:1-8](), [src/phoenix/server/mcp_server.py:82-87]()

The backend server’s tools mirror `/v1` operations and are generated from the OpenAPI schema, keeping the tool surface aligned with the REST API. Dispatch uses an in-process ASGI transport rather than a network hop, and the authenticated principal is carried in the internal request scope rather than replaying the caller’s bearer token. [src/phoenix/server/mcp_server.py:1-16]()

Sources: [src/phoenix/server/mcp_server.py:1-16]()

---

## Package Configuration

The npm package is named `@arizeai/phoenix-mcp`. It can be launched through `npx` and configured in an MCP client with a Phoenix base URL and API key. The package README describes integrations with clients such as Claude Desktop and Cursor. [js/packages/phoenix-mcp/README.md:15-24](), [js/packages/phoenix-mcp/README.md:42-62]()

| Setting | Purpose |
|---|---|
| `PHOENIX_ENDPOINT` | Phoenix base URL. [js/packages/phoenix-mcp/README.md:102-111]() |
| `PHOENIX_API_KEY` | API key for the Phoenix instance. [js/packages/phoenix-mcp/README.md:102-111]() |
| `PHOENIX_PROJECT` | Optional default project for project-scoped tools; `PHOENIX_PROJECT_NAME` is an alias. [js/packages/phoenix-mcp/README.md:102-109]() |
| `PHOENIX_CLIENT_HEADERS` | Optional JSON-encoded request headers. [js/packages/phoenix-mcp/README.md:102-111]() |
| `PHOENIX_DISCOVER_CONFIG` | Set to `false` to disable `.env.phoenix` discovery. [js/packages/phoenix-mcp/README.md:113-117]() |
| `--baseUrl`, `--apiKey`, `--project` | Command-line options passed to `resolveConfig`. [js/packages/phoenix-mcp/src/index.ts:20-27]() |

At runtime, the package discovers the nearest `.env.phoenix` file at or above the working directory. Command-line options and process environment variables take precedence; the server can warn if a higher-priority API key is paired with an endpoint from the discovered file. [js/packages/phoenix-mcp/README.md:113-117]()

The server uses `minimist` to parse command-line arguments, passes the supported options to `resolveConfig`, and supplies the result to `createPhoenixClient`. It registers tool groups before connecting the server to stdio. [js/packages/phoenix-mcp/src/index.ts:3-18](), [js/packages/phoenix-mcp/src/index.ts:20-44](), [js/packages/phoenix-mcp/src/index.ts:46-55]()

Sources: [js/packages/phoenix-mcp/README.md:42-62](), [js/packages/phoenix-mcp/README.md:102-117](), [js/packages/phoenix-mcp/src/index.ts:3-18](), [js/packages/phoenix-mcp/src/index.ts:20-55]()

---

## Available Tools

The standalone package registers tool initializers for prompts, experiments, datasets, projects, traces, spans, sessions, annotation configurations, and support. The README lists the exposed tool names by domain. [js/packages/phoenix-mcp/src/index.ts:7-18](), [js/packages/phoenix-mcp/src/index.ts:36-44](), [js/packages/phoenix-mcp/README.md:119-139]()

| Domain | Tools |
|---|---|
| Prompts | `list-prompts`, `get-prompt`, `get-latest-prompt`, `get-prompt-by-identifier`, `get-prompt-version`, `list-prompt-versions`, `get-prompt-version-by-tag`, `list-prompt-version-tags`, `add-prompt-version-tag`, `upsert-prompt`. [js/packages/phoenix-mcp/README.md:123]() |
| Projects | `list-projects`, `get-project`. [js/packages/phoenix-mcp/README.md:125]() |
| Traces | `list-traces`, `get-trace`. [js/packages/phoenix-mcp/README.md:127]() |
| Spans | `get-spans`, `get-span-annotations`. [js/packages/phoenix-mcp/README.md:129]() |
| Sessions | `list-sessions`, `get-session`. [js/packages/phoenix-mcp/README.md:131]() |
| Annotation configurations | `list-annotation-configs`. [js/packages/phoenix-mcp/README.md:133]() |
| Datasets | `list-datasets`, `get-dataset`, `get-dataset-examples`, `get-dataset-experiments`, `add-dataset-examples`. [js/packages/phoenix-mcp/README.md:135]() |
| Experiments | `list-experiments-for-dataset`, `get-experiment-by-id`. [js/packages/phoenix-mcp/README.md:137]() |

The package README directs documentation-search requests to a separate Phoenix Docs MCP server rather than this package. [js/packages/phoenix-mcp/README.md:139]()

Sources: [js/packages/phoenix-mcp/src/index.ts:7-18](), [js/packages/phoenix-mcp/src/index.ts:36-44](), [js/packages/phoenix-mcp/README.md:119-139]()

---

## Project Tools

Project tools are registered by `initializeProjectTools`. Trace, span, and session tool initializers separately receive `defaultProject: config.project`, allowing the configured project to supply default context for those project-scoped operations. [js/packages/phoenix-mcp/src/index.ts:36-42]()

The package README identifies `list-projects` and `get-project` as the project tools. [js/packages/phoenix-mcp/README.md:125]()

Sources: [js/packages/phoenix-mcp/src/index.ts:36-42](), [js/packages/phoenix-mcp/README.md:125]()

### Project Tool Mapping

**Diagram: Project requests mapped to package entities**

```mermaid
flowchart LR
    Intent["Natural-language request: find a project"]
    Tool["list-projects / get-project"]
    Registration["initializeProjectTools"]
    Client["createPhoenixClient"]
    Backend["Phoenix project API"]

    Intent --> Tool --> Registration --> Client --> Backend
```

Sources: [js/packages/phoenix-mcp/README.md:119-125](), [js/packages/phoenix-mcp/src/index.ts:8-13](), [js/packages/phoenix-mcp/src/index.ts:28-42]()

---

## SQL Query Tools

The backend MCP implementation identifies analytics SQL tools as read-oriented tools, alongside code-mode discovery tools. Their metadata marks them read-only and non-destructive, supporting client-side treatment as safe reads. [src/phoenix/server/mcp_server.py:120-124]()

The available source excerpts do not specify the SQL tool names, query syntax, schema exposure, or execution pipeline; those details are implemented under `src/phoenix/server/mcp/sql/` and should not be inferred from the package tool inventory. [src/phoenix/server/mcp_server.py:120-124]()

Sources: [src/phoenix/server/mcp_server.py:120-124]()

---

## Implementation Details

### Standalone Entry Point and Initialization

The entry point parses `process.argv` with `minimist` and resolves `apiKey`, `baseUrl`, and `project` through `resolveConfig`. It passes the resolved configuration to `createPhoenixClient`, then creates an MCP server named `phoenix-mcp-server`. [js/packages/phoenix-mcp/src/index.ts:3-9](), [js/packages/phoenix-mcp/src/index.ts:20-34]()

It registers prompt, experiment, dataset, project, trace, span, session, annotation-config, and support tools. Trace, span, and session registration receive the configured default project. [js/packages/phoenix-mcp/src/index.ts:36-44]()

During startup, readme resources are initialized only when `DANGEROUSLY_READ_README_FILES` is exactly `"true"`. The process then connects `StdioServerTransport`; startup failures are logged and cause exit status `1`. [js/packages/phoenix-mcp/src/index.ts:46-60]()

Sources: [js/packages/phoenix-mcp/src/index.ts:3-9](), [js/packages/phoenix-mcp/src/index.ts:20-60]()

### Backend MCP Server and Code Mode

The backend `mcp_server.py` builds a `FastMCP` server from the REST API. With code mode enabled, the server exposes discovery tools and a sandboxed execution tool rather than advertising every REST operation individually; code mode is described as the default for both consumers. With code mode disabled, each `/v1` operation is exposed as its own tool. [src/phoenix/server/mcp_server.py:1-8](), [src/phoenix/server/mcp_server.py:18-23]()

The module imports code-mode transforms including `GetSchemas`, `GetTags`, `GetToolCatalog`, `ListTools`, and `Search`, and imports `MontyPoolSandboxProvider` for sandbox support. [src/phoenix/server/mcp_server.py:33-43](), [src/phoenix/server/mcp_server.py:69]()

REST method semantics determine tool annotations: `GET` is read-only; `POST` is treated as a non-read-only creation; and `PUT`, `PATCH`, and `DELETE` carry destructive hints. Unknown methods receive conservative annotations. Analytics SQL and code-mode discovery tools use read-oriented metadata. [src/phoenix/server/mcp_server.py:89-124]()

Sources: [src/phoenix/server/mcp_server.py:18-23](), [src/phoenix/server/mcp_server.py:33-43](), [src/phoenix/server/mcp_server.py:69](), [src/phoenix/server/mcp_server.py:89-124]()

### Tool Descriptions and REST Semantics

For generated tools, `_agent_facing_description` prefers a route’s concise summary. If no summary exists, it uses the first paragraph of the endpoint description, removing structured docstring sections and collapsing indentation. [src/phoenix/server/mcp_server.py:133-157]()

The backend also defines a route map for `POST` operations on `/v1/span_notes`, `/v1/trace_notes`, and `/v1/session_notes`. [src/phoenix/server/mcp_server.py:126-131]()

Sources: [src/phoenix/server/mcp_server.py:126-157]()

---

## Code Entity to Natural Language Space Mapping

### Diagram 1: Package Startup and Tool Registration

This diagram maps an assistant’s request to the standalone package’s startup and registration entities. [js/packages/phoenix-mcp/src/index.ts:20-44]()

```mermaid
flowchart LR
    Request["Natural-language request"]
    Client["MCP client"]
    Main["main"]
    Transport["StdioServerTransport"]
    Server["McpServer"]
    ProjectTools["initializeProjectTools"]
    TraceTools["initializeTraceTools"]
    SessionTools["initializeSessionTools"]
    PhoenixClient["createPhoenixClient"]
    Config["resolveConfig"]

    Request --> Client --> Transport --> Server
    Main --> Transport
    Config --> PhoenixClient
    Server --> ProjectTools
    Server --> TraceTools
    Server --> SessionTools
    ProjectTools --> PhoenixClient
    TraceTools --> PhoenixClient
    SessionTools --> PhoenixClient
```

Sources: [js/packages/phoenix-mcp/src/index.ts:20-44](), [js/packages/phoenix-mcp/src/index.ts:46-55]()

### Diagram 2: Backend Tool Generation and Internal Dispatch

This diagram maps questions about Phoenix REST operations to the backend MCP entities that generate and dispatch tools. [src/phoenix/server/mcp_server.py:1-16](), [src/phoenix/server/mcp_server.py:82-87]()

```mermaid
flowchart LR
    Intent["Natural-language request about Phoenix data"]
    Mount["MCP_MOUNT_PATH"]
    FastMCP["FastMCP"]
    Schema["OpenAPI schema"]
    CodeMode["CodeMode discovery and sandboxed execute"]
    ASGI["In-process ASGI transport"]
    Identity["INTERNAL_PRINCIPAL_SCOPE_KEY"]
    API["Phoenix /v1 REST operation"]

    Intent --> Mount --> FastMCP
    Schema --> FastMCP
    FastMCP --> CodeMode
    FastMCP --> ASGI --> API
    Identity --> ASGI
```

Sources: [src/phoenix/server/mcp_server.py:1-16](), [src/phoenix/server/mcp_server.py:33-43](), [src/phoenix/server/mcp_server.py:82-87]()

---

## Development and Deployment

### Development Workflow

The package is managed in the JavaScript pnpm workspace. Its README documents `pnpm install` and `pnpm build` from the `js/` directory, `pnpm dev` for development mode, and `pnpm inspect` for the MCP inspector. [js/packages/phoenix-mcp/README.md:64-99]()

Sources: [js/packages/phoenix-mcp/README.md:64-99]()

### Environment Variables and Configuration

The package accepts `PHOENIX_API_KEY`, `PHOENIX_ENDPOINT`, optional `PHOENIX_PROJECT` (alias `PHOENIX_PROJECT_NAME`), and optional JSON-encoded `PHOENIX_CLIENT_HEADERS`. It also supports `.env.phoenix` discovery, which can be disabled with `PHOENIX_DISCOVER_CONFIG=false`. [js/packages/phoenix-mcp/README.md:102-117]()

The entry point explicitly passes CLI values for `apiKey`, `baseUrl`, and `project` into `resolveConfig`. [js/packages/phoenix-mcp/src/index.ts:20-27]()

Sources: [js/packages/phoenix-mcp/README.md:102-117](), [js/packages/phoenix-mcp/src/index.ts:20-27]()

### Integration with AI Assistants

An MCP client configuration can invoke the package via `npx -y @arizeai/phoenix-mcp@latest` and supply `--baseUrl` and `--apiKey`. [js/packages/phoenix-mcp/README.md:42-62]()

Sources: [js/packages/phoenix-mcp/README.md:42-62]()

---

# Page: Frontend Application

# Frontend Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [js/app/package.json](js/app/package.json)
- [js/app/src/hooks/index.ts](js/app/src/hooks/index.ts)
- [js/app/src/hooks/useRefetchOnStreamAdvance.ts](js/app/src/hooks/useRefetchOnStreamAdvance.ts)
- [js/app/src/hooks/useUnsavedChangesBlocker.ts](js/app/src/hooks/useUnsavedChangesBlocker.ts)
- [js/app/src/pages/examples/ExamplesPage.tsx](js/app/src/pages/examples/ExamplesPage.tsx)
- [js/app/src/pages/project/AnnotationSummary.tsx](js/app/src/pages/project/AnnotationSummary.tsx)
- [js/app/src/pages/project/ProjectOnboardingOverlay.tsx](js/app/src/pages/project/ProjectOnboardingOverlay.tsx)
- [js/app/src/pages/project/ProjectPage.tsx](js/app/src/pages/project/ProjectPage.tsx)
- [js/app/src/pages/project/ProjectPageQueries.tsx](js/app/src/pages/project/ProjectPageQueries.tsx)
- [js/app/src/pages/project/ProjectSpansPage.tsx](js/app/src/pages/project/ProjectSpansPage.tsx)
- [js/app/src/pages/project/ProjectTracesPage.tsx](js/app/src/pages/project/ProjectTracesPage.tsx)
- [js/app/src/pages/project/SessionAnnotationSummary.tsx](js/app/src/pages/project/SessionAnnotationSummary.tsx)
- [js/app/src/pages/project/TraceAnnotationSummary.tsx](js/app/src/pages/project/TraceAnnotationSummary.tsx)
- [js/app/src/pages/project/__generated__/ProjectOnboardingOverlayRefetchQuery.graphql.ts](js/app/src/pages/project/__generated__/ProjectOnboardingOverlayRefetchQuery.graphql.ts)
- [js/app/src/pages/project/__generated__/ProjectPageQueriesSpansQuery.graphql.ts](js/app/src/pages/project/__generated__/ProjectPageQueriesSpansQuery.graphql.ts)
- [js/app/src/pages/project/__generated__/ProjectPageQueriesTracesQuery.graphql.ts](js/app/src/pages/project/__generated__/ProjectPageQueriesTracesQuery.graphql.ts)

</details>



Phoenix's frontend is a React 19 single-page application (SPA) located in the `js/app/` directory [js/app/package.json:1-123](). The user interface is bundled using Vite and served as static assets by the FastAPI server at runtime [js/app/package.json:8](). This page provides a high-level architectural overview of the frontend application and links to detailed child pages covering the build system, state management, playground, and AI assistant interfaces.

For deeper technical details, refer to the child pages:
- [Application Structure & Build System](#4.1) — React app structure, Vite build system, Relay integration, routing, and component architecture.
- [State Management & Theming](#4.2) — Zustand state management, Relay cache, theming system, and the filter DSL.
- [Playground Interface](#4.3) — LLM interaction interface, instance management, streaming responses, and chat completion subscriptions.
- [AI Assistant (PxI) Interface](#4.4) — Built-in AI assistant chat interface (`AgentChatPanel`), tool registry, capability flags, and generative UI components.

Sources: [js/app/package.json:1-123]()

## Technology Stack

The frontend utilizes a modern TypeScript-based stack optimized for performance, type safety, and efficient data synchronization via GraphQL.

| Technology | Purpose | Code Pointers |
|------------|---------|---------------|
| `react` | UI framework (v19) | [js/app/package.json:101-104]() |
| `vite` | Build tool and dev server | [js/app/package.json:8-17]() |
| `react-relay` | GraphQL client & data fetching | [js/app/package.json:108](), [js/app/package.json:114]() |
| `react-router` | Client-side routing and blockers | [js/app/package.json:111](), [js/app/src/hooks/useUnsavedChangesBlocker.ts:1-33]() |
| `zustand` | Client-side state management | [js/app/package.json:122]() |
| `@emotion/react` | CSS-in-JS styling | [js/app/package.json:69]() |

Sources: [js/app/package.json:51-123](), [js/app/src/hooks/useUnsavedChangesBlocker.ts:1-33]()

## Application Architecture & Routing

The application relies on `react-router` for navigation and route organization. Key route containers like `ProjectPage` ([js/app/src/pages/project/ProjectPage.tsx:136]()), `ProjectTracesPage` ([js/app/src/pages/project/ProjectTracesPage.tsx:57]()), and `ProjectSpansPage` ([js/app/src/pages/project/ProjectSpansPage.tsx:49]()) manage tabbed views, query parameters, and data preloading. Unsaved work across forms or tables is guarded by custom hooks such as `useUnsavedChangesBlocker` ([js/app/src/hooks/useUnsavedChangesBlocker.ts:11-33]()).

### Diagram: Navigation Routing Architecture
```mermaid
graph TD
    Root["App Root"] --> ProjectPage["ProjectPage (js/app/src/pages/project/ProjectPage.tsx)"]
    ProjectPage --> ProjectTracesPage["ProjectTracesPage (js/app/src/pages/project/ProjectTracesPage.tsx)"]
    ProjectPage --> ProjectSpansPage["ProjectSpansPage (js/app/src/pages/project/ProjectSpansPage.tsx)"]
    ProjectPage --> ExamplesPage["ExamplesPage (js/app/src/pages/examples/ExamplesPage.tsx)"]
    ExamplesPage --> ConfirmNavigationDialog["ConfirmNavigationDialog"]
    ProjectTracesPage --> TracesTable["TracesTable"]
    ProjectSpansPage --> SpansTable["SpansTable"]
```
Sources: [js/app/src/pages/project/ProjectPage.tsx:136-154](), [js/app/src/pages/project/ProjectTracesPage.tsx:57-117](), [js/app/src/pages/project/ProjectSpansPage.tsx:49-105](), [js/app/src/pages/examples/ExamplesPage.tsx:26-59]()

## Data Fetching and Relay Integration

Data flows from the server GraphQL schema to the React components via `react-relay` preloaded queries and fragment containers. Queries are centralized in modules such as `ProjectPageQueries.tsx` ([js/app/src/pages/project/ProjectPageQueries.tsx:13-70]()), supplying pre-filtered arguments to child summary components like `AnnotationSummary` ([js/app/src/pages/project/AnnotationSummary.tsx:49-89]()) and `TraceAnnotationSummary` ([js/app/src/pages/project/TraceAnnotationSummary.tsx:26-66]()).

### Diagram: Relay Query and Summary Architecture
```mermaid
graph TD
    ProjectPageQueries["ProjectPageQueries.tsx"] --> ProjectPageQueriesTracesQuery["ProjectPageQueriesTracesQuery"]
    ProjectPageQueries --> ProjectPageQueriesSpansQuery["ProjectPageQueriesSpansQuery"]
    ProjectPageQueriesTracesQuery --> TracesTable_spans["TracesTable_spans Fragment"]
    ProjectPageQueriesSpansQuery --> SpansTable_spans["SpansTable_spans Fragment"]
    AnnotationSummary["AnnotationSummary.tsx"] --> AnnotationSummaryQuery["AnnotationSummaryQuery"]
    AnnotationSummaryQuery --> AnnotationSummaryValueFragment["AnnotationSummaryValueFragment"]
    TraceAnnotationSummary["TraceAnnotationSummary.tsx"] --> TraceAnnotationSummaryQuery["TraceAnnotationSummaryQuery"]
    TraceAnnotationSummaryQuery --> TraceAnnotationSummaryValueFragment["TraceAnnotationSummaryValueFragment"]
```
Sources: [js/app/src/pages/project/ProjectPageQueries.tsx:13-70](), [js/app/src/pages/project/AnnotationSummary.tsx:49-89](), [js/app/src/pages/project/TraceAnnotationSummary.tsx:26-66]()

---

# Page: Application Structure & Build System

# Application Structure & Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-design/references/icons.md](.agents/skills/phoenix-design/references/icons.md)
- [js/app/package.json](js/app/package.json)
- [js/app/schema.graphql](js/app/schema.graphql)
- [js/app/src/components/core/card/styles.ts](js/app/src/components/core/card/styles.ts)
- [js/app/src/components/core/disclosure/styles.tsx](js/app/src/components/core/disclosure/styles.tsx)
- [js/app/src/components/dataset/DatasetLabelConfigButton.tsx](js/app/src/components/dataset/DatasetLabelConfigButton.tsx)
- [js/app/src/components/evaluators/EvaluatorMappingSourceEditor.tsx](js/app/src/components/evaluators/EvaluatorMappingSourceEditor.tsx)
- [js/app/src/hooks/index.ts](js/app/src/hooks/index.ts)
- [js/app/src/hooks/useRefetchOnStreamAdvance.ts](js/app/src/hooks/useRefetchOnStreamAdvance.ts)
- [js/app/src/hooks/useUnsavedChangesBlocker.ts](js/app/src/hooks/useUnsavedChangesBlocker.ts)
- [js/app/src/openInference/tracing/types.ts](js/app/src/openInference/tracing/types.ts)
- [js/app/src/pages/datasets/DatasetsTable.tsx](js/app/src/pages/datasets/DatasetsTable.tsx)
- [js/app/src/pages/evaluators/DatasetEvaluatorsTable.tsx](js/app/src/pages/evaluators/DatasetEvaluatorsTable.tsx)
- [js/app/src/pages/evaluators/EvaluatorsTable.tsx](js/app/src/pages/evaluators/EvaluatorsTable.tsx)
- [js/app/src/pages/examples/ExamplesPage.tsx](js/app/src/pages/examples/ExamplesPage.tsx)
- [js/app/src/pages/examples/ExamplesTable.tsx](js/app/src/pages/examples/ExamplesTable.tsx)
- [js/app/src/pages/project/AnnotationSummary.tsx](js/app/src/pages/project/AnnotationSummary.tsx)
- [js/app/src/pages/project/ProjectOnboardingOverlay.tsx](js/app/src/pages/project/ProjectOnboardingOverlay.tsx)
- [js/app/src/pages/project/ProjectPage.tsx](js/app/src/pages/project/ProjectPage.tsx)
- [js/app/src/pages/project/ProjectPageQueries.tsx](js/app/src/pages/project/ProjectPageQueries.tsx)
- [js/app/src/pages/project/ProjectSpansPage.tsx](js/app/src/pages/project/ProjectSpansPage.tsx)
- [js/app/src/pages/project/ProjectTracesPage.tsx](js/app/src/pages/project/ProjectTracesPage.tsx)
- [js/app/src/pages/project/SessionAnnotationSummary.tsx](js/app/src/pages/project/SessionAnnotationSummary.tsx)
- [js/app/src/pages/project/SessionsTable.tsx](js/app/src/pages/project/SessionsTable.tsx)
- [js/app/src/pages/project/SpansTable.tsx](js/app/src/pages/project/SpansTable.tsx)
- [js/app/src/pages/project/TraceAnnotationSummary.tsx](js/app/src/pages/project/TraceAnnotationSummary.tsx)
- [js/app/src/pages/project/TracesTable.tsx](js/app/src/pages/project/TracesTable.tsx)
- [js/app/src/pages/project/__generated__/ProjectOnboardingOverlayRefetchQuery.graphql.ts](js/app/src/pages/project/__generated__/ProjectOnboardingOverlayRefetchQuery.graphql.ts)
- [js/app/src/pages/project/__generated__/ProjectPageQueriesSpansQuery.graphql.ts](js/app/src/pages/project/__generated__/ProjectPageQueriesSpansQuery.graphql.ts)
- [js/app/src/pages/project/__generated__/ProjectPageQueriesTracesQuery.graphql.ts](js/app/src/pages/project/__generated__/ProjectPageQueriesTracesQuery.graphql.ts)
- [js/app/src/pages/projects/ProjectsPage.tsx](js/app/src/pages/projects/ProjectsPage.tsx)
- [js/app/src/pages/prompt/PromptLabelConfigButton.tsx](js/app/src/pages/prompt/PromptLabelConfigButton.tsx)
- [js/app/src/pages/prompt/PromptLatestVersionsList.tsx](js/app/src/pages/prompt/PromptLatestVersionsList.tsx)
- [js/app/src/pages/prompt/PromptLayout.tsx](js/app/src/pages/prompt/PromptLayout.tsx)
- [js/app/src/pages/prompt/PromptVersionsList.tsx](js/app/src/pages/prompt/PromptVersionsList.tsx)
- [js/app/src/pages/prompts/PromptsTable.tsx](js/app/src/pages/prompts/PromptsTable.tsx)
- [js/app/src/pages/settings/SystemAPIKeysTable.tsx](js/app/src/pages/settings/SystemAPIKeysTable.tsx)
- [js/app/src/pages/trace/compare/CompareTracesPage.tsx](js/app/src/pages/trace/compare/CompareTracesPage.tsx)
- [js/app/src/pages/trace/span/DecisionSpanInfo.tsx](js/app/src/pages/trace/span/DecisionSpanInfo.tsx)
- [js/app/src/pages/trace/span/LLMMessage.tsx](js/app/src/pages/trace/span/LLMMessage.tsx)
- [js/app/src/pages/trace/span/MessageContentsList.tsx](js/app/src/pages/trace/span/MessageContentsList.tsx)
- [js/app/src/pages/trace/span/ReasoningMessageContent.tsx](js/app/src/pages/trace/span/ReasoningMessageContent.tsx)
- [js/app/src/pages/trace/span/SpanInfo.tsx](js/app/src/pages/trace/span/SpanInfo.tsx)
- [js/app/src/pages/trace/span/SpanInput.tsx](js/app/src/pages/trace/span/SpanInput.tsx)
- [js/app/src/pages/trace/span/__tests__/utils.test.ts](js/app/src/pages/trace/span/__tests__/utils.test.ts)
- [js/app/src/pages/trace/span/index.ts](js/app/src/pages/trace/span/index.ts)
- [js/app/src/pages/trace/span/types.ts](js/app/src/pages/trace/span/types.ts)
- [js/app/src/pages/trace/span/utils.ts](js/app/src/pages/trace/span/utils.ts)
- [js/app/src/utils/__tests__/urlUtils.test.ts](js/app/src/utils/__tests__/urlUtils.test.ts)
- [js/app/stories/constants/spanInfoFixtures.ts](js/app/stories/constants/spanInfoFixtures.ts)
- [js/app/stories/domains/tracing/SpanInfo.stories.tsx](js/app/stories/domains/tracing/SpanInfo.stories.tsx)
- [src/phoenix/server/api/mutations/dataset_label_mutations.py](src/phoenix/server/api/mutations/dataset_label_mutations.py)
- [tests/unit/server/api/mutations/test_dataset_label_mutations.py](tests/unit/server/api/mutations/test_dataset_label_mutations.py)

</details>



This page documents the frontend application's architecture, the Vite-based build system, and the integration of React Relay and Zustand. The Phoenix frontend is a modern React application built with TypeScript, designed for high-performance AI observability visualizations.

## Build System Overview

The Phoenix frontend uses **Vite** as its primary build tool and development server, with **pnpm** as the package manager. The build system is optimized for the monorepo structure where the frontend assets are eventually served by the Python FastAPI backend.

### Package Management & Scripts

The application is defined in `js/app/package.json` and uses **pnpm** as the package manager. The frontend source is primarily located in `js/app/src`.

Key scripts for the build lifecycle include:

- `build`: Runs the Relay compiler then builds the application with Vite for production [js/app/package.json:8]().
- `build:relay`: Runs `relay-compiler` which generates TypeScript GraphQL types for Relay [js/app/package.json:11]().
- `dev`: Typically starts both the Vite dev server and the Python backend, enabling full-stack development [js/app/package.json:13]().
- `generate:openapi`: Generates TypeScript types from the OpenAPI JSON schema for API typing support [js/app/package.json:29]().

### Vite Configuration

The Vite configuration defines the build and development environment for the React application:

#### Build Pipeline & Plugins

```mermaid
graph TD
    subgraph "Vite_Build_Process"
        Entry["js/app/src/index.tsx"]
        ReactFallbackThrottlePlugin["vite-plugin-react-fallback-throttle"]
        ReactPlugin["@vitejs/plugin-react"]
        BabelPlugin["@rolldown/plugin-babel (with React Compiler)"]
        RelayPlugin["vite-plugin-relay"]
        LezerPlugin["@lezer/generator/rollup"]
        CircleDependencyPlugin["vite-plugin-circular-dependency"]
        Rollup["Rollup Bundler"]
        StaticOutput["src/phoenix/server/static/"]
    end

    subgraph "Code_Splitting_Manual_Chunks"
        VendorCodemirror["vendor-codemirror"]
        VendorRecharts["vendor-recharts"]
        VendorShiki["vendor-shiki"]
        VendorAISDKReact["vendor-ai-sdk-react"]
        VendorStreamdown["vendor-streamdown"]
        VendorCatchAll["vendor"]
    end

    Entry --> ReactFallbackThrottlePlugin
    ReactFallbackThrottlePlugin --> ReactPlugin
    ReactPlugin --> BabelPlugin
    BabelPlugin --> RelayPlugin
    RelayPlugin --> LezerPlugin
    LezerPlugin --> CircleDependencyPlugin
    CircleDependencyPlugin --> Rollup

    Rollup -- "Code Splitting" --> VendorCodemirror
    Rollup -- "Code Splitting" --> VendorRecharts
    Rollup -- "Code Splitting" --> VendorShiki
    Rollup -- "Code Splitting" --> VendorAISDKReact
    Rollup -- "Code Splitting" --> VendorStreamdown
    Rollup -- "Code Splitting" --> VendorCatchAll
    Rollup -- "Output Directory" --> StaticOutput
```

- The pipeline starts at the app entry (`js/app/src/index.tsx`).
- The `vite-plugin-react-fallback-throttle` improves UI responsiveness by disabling default suspense delays.
- The Rollup Babel plugin integrates the `babel-plugin-react-compiler` for pre-compilation.
- Relay transforms GraphQL literals within the code for efficient data fetching.
- The output directory is `src/phoenix/server/static/` within the Python package so the FastAPI backend can serve the static frontend resources via `StaticFiles` [js/app/package.json:12]().

Sources: [js/app/package.json:8-14](), [js/app/package.json:29]()

---

## Application Architecture

The frontend app is a single-page React application structured with clear concerns for routing, state management, and UI components.

### Routing System

Phoenix uses `react-router` to define its navigation routes. The routing logic maps browser URLs to specific page components. The main application routes are defined in `js/app/src/Routes.tsx`.

```mermaid
graph TD
    Router["createBrowserRouter (js/app/src/Routes.tsx)"]
    RootRoute["Route path='/' (RootLayout)"]
    AuthRoutes["Auth routes (e.g. /login)"]
    AuthenticatedRoot["AuthenticatedRoot component"]
    Layout["Layout component (Layout.tsx)"]

    Router --> RootRoute
    RootRoute --> AuthRoutes
    RootRoute --> AuthenticatedRoot
    AuthenticatedRoot --> Layout

    subgraph "Main Application Features"
        Layout --> ProjectsPage["/projects (ProjectsPage)"]
        Layout --> TracesPage["/projects/:projectId/traces/:traceId (TracePage)"]
        Layout --> DatasetsPage["/datasets (DatasetsPage)"]
        Layout --> PlaygroundPage["/playground (PlaygroundPage)"]
        Layout --> EvaluatorsPage["/evaluators (EvaluatorsPage)"]
        Layout --> SettingsPage["/settings (SettingsPage)"]
        Layout --> ProfilePage["/profile (ProfilePage)"]
    end

    style ProjectsPage fill:#ace,stroke:#333,stroke-width:2px
    style TracesPage fill:#ace,stroke:#333,stroke-width:2px
    style DatasetsPage fill:#ace,stroke:#333,stroke-width:2px
    style PlaygroundPage fill:#ace,stroke:#333,stroke-width:2px
    style EvaluatorsPage fill:#ace,stroke:#333,stroke-width:2px
    style SettingsPage fill:#ace,stroke:#333,stroke-width:2px
    style ProfilePage fill:#ace,stroke:#333,stroke-width:2px
```

- Routes support loader functions fetching data before rendering, such as `datasetEvaluatorDetailsLoader` [js/app/src/pages/evaluators/DatasetEvaluatorsTable.tsx:1-10]() (example of a loader-related component).
- Custom revalidation logic, like `revalidateOnPathChange` (not directly shown in provided files, but a common pattern in `react-router`), prevents unnecessary loader execution on minor URL changes (e.g., only search params changing).
- The layout is served by the Python backend's `index.html` template.
- Route metadata is used for navigation and search, defined in `handle.navigation` within `Route` objects. This metadata includes `section`, `label`, `description`, and `icon`.
- The `buildRouteNavigationCatalog` function processes the `RouteObject` array to create a catalog of navigable destinations. This catalog is used by features like the search palette.

Sources: [js/app/src/pages/evaluators/DatasetEvaluatorsTable.tsx:1-10]()

### State Management Strategy

Phoenix uses a multi-layered approach to state:

| Layer | Technology | Responsibility |
|---|---|---|
| Server Data | React Relay | GraphQL data fetching, caching, and normalization|
| Global UI State | Zustand | Cross-component UI state (e.g., sidebars) |
| Context & Theming| React Context| Theme modes (dark/light) and user session context|

Sources: [js/app/package.json:108](), [js/app/package.json:114](), [js/app/package.json:122]()

---

## Relay Integration & Data Flow

Relay is the key data-layer technology, ensuring the UI fetches precisely the data it needs from the Strawberry-based GraphQL API [js/app/schema.graphql:1-5256]().

1. The `relay-compiler` extracts GraphQL literals and generates TypeScript types [js/app/package.json:11]().
2. Components use fragments to declare data dependencies, for example, `TracesTable_spans` in `js/app/src/pages/project/TracesTable.tsx` [js/app/src/pages/project/TracesTable.tsx:87]().
3. The Relay environment manages network requests to the `/graphql` endpoint.

```mermaid
graph LR
    subgraph "Frontend (js/app/src)"
        Component["React Component"]
        RelayEnv["Relay Environment"]
        RelayStore["Relay Store"]
    end

    subgraph "Server (src/phoenix/server)"
        GraphQL["GraphQLRouter (/graphql)"]
        Schema["GraphQL Schema (js/app/schema.graphql)"]
        Resolvers["Resolvers (e.g., DatasetLabelMutationMixin)"]
    end

    Component -- "Query/Fragment" --> RelayEnv
    RelayEnv -- "HTTP POST" --> GraphQL
    GraphQL --> Schema
    Schema --> Resolvers
    Resolvers -- "JSON" --> RelayEnv
    RelayEnv -- "Update" --> RelayStore
    RelayStore -- "Data" --> Component
```

Sources: [js/app/schema.graphql:1-5256](), [js/app/package.json:11](), [js/app/src/pages/project/TracesTable.tsx:87](), [src/phoenix/server/api/mutations/dataset_label_mutations.py:61]()

---

## Component Architecture & Theming

### Theming System

Phoenix uses root CSS variables for consistent dimensions, spacings, and colors. The system supports light and dark modes, with the dark theme setting `color-scheme: dark` to synchronize browser system colors. Global styles are defined in `js/app/src/GlobalStyles.tsx`.

### Component Organization

The frontend source is organized into several key directories under `js/app/src`:

- **pages/**: Contains top-level page components (e.g., `ProjectsPage` [js/app/src/pages/projects/ProjectsPage.tsx:1-10](), `TracesTable` [js/app/src/pages/project/TracesTable.tsx:116](), `SpansTable` [js/app/src/pages/project/SpansTable.tsx:120](), `SessionsTable` [js/app/src/pages/project/SessionsTable.tsx:165](), `ExamplesPage` [js/app/src/pages/examples/ExamplesPage.tsx:26](), `ExamplesTable` [js/app/src/pages/examples/ExamplesTable.tsx:867]()) and their associated loaders. This directory also includes layout components.
- **components/**: Reusable UI components (e.g., `Flex`, `Heading`, `Icon`, `Icons`, `Link`, `OverflowRow`, `Text`, `View` [js/app/src/pages/project/TracesTable.tsx:19-27]()). This includes core UI elements and specialized components.
- **hooks/**: Custom React hooks for shared logic, exported from `js/app/src/hooks/index.ts` [js/app/src/hooks/index.ts:1-25](). Examples include `useDebouncedChange`, `useDeferredVisibility`, `usePersistedState`, `useUnsavedChangesBlocker` [js/app/src/hooks/index.ts:6-25]().
- **agent/**: Components and logic for the Phoenix Intelligence (PxI) assistant.
- **contexts/**: React Context providers for global state.
- **routing/**: Contains utilities for route management.
- **utils/**: General utility functions.

### External Libraries

- **React Aria Components**: For accessible UI primitives [js/app/package.json:102]().
- **CodeMirror**: Powers the JSON and Python editors used in Playground and Evaluators [js/app/package.json:57-65]().
- **Recharts**: Used for rendering observability metrics and dashboards [js/app/package.json:113]().
- **AI SDK**: Integrates generative AI capabilities for the assistant [js/app/package.json:53]().

Sources: [js/app/package.json:53-113](), [js/app/src/pages/project/TracesTable.tsx:19-27](), [js/app/src/pages/projects/ProjectsPage.tsx:1-10](), [js/app/src/pages/project/TracesTable.tsx:116](), [js/app/src/pages/project/SpansTable.tsx:120](), [js/app/src/pages/project/SessionsTable.tsx:165](), [js/app/src/pages/examples/ExamplesPage.tsx:26](), [js/app/src/pages/examples/ExamplesTable.tsx:867](), [js/app/src/hooks/index.ts:1-25]()

---

This summary details the critical aspects of the Phoenix frontend app structure, including its build system with Vite, routing, state management with Relay and Zustand, and the component and theming architecture.

---

# Page: State Management & Theming

# State Management & Theming

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-frontend/SKILL.md](.agents/skills/phoenix-frontend/SKILL.md)
- [.agents/skills/phoenix-llms-txt/SKILL.md](.agents/skills/phoenix-llms-txt/SKILL.md)
- [.agents/skills/phoenix-playwright-tests/SKILL.md](.agents/skills/phoenix-playwright-tests/SKILL.md)
- [.agents/skills/phoenix-pr-description/SKILL.md](.agents/skills/phoenix-pr-description/SKILL.md)
- [.agents/skills/phoenix-pr-description/examples.md](.agents/skills/phoenix-pr-description/examples.md)
- [.agents/skills/phoenix-pr-screenshot/SKILL.md](.agents/skills/phoenix-pr-screenshot/SKILL.md)
- [.agents/skills/phoenix-typescript/SKILL.md](.agents/skills/phoenix-typescript/SKILL.md)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/datasets/download-dataset-examples-as-jsonl-file.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/datasets/download-dataset-examples-as-jsonl-file.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/prompts/delete-a-prompt.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/prompts/delete-a-prompt.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/prompts/delete-a-tag-from-a-prompt-version.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/prompts/delete-a-tag-from-a-prompt-version.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/bulk-delete-sessions.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/bulk-delete-sessions.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/create-a-session-note.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/create-a-session-note.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/delete-a-session-by-identifier.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/delete-a-session-by-identifier.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/traces/create-a-trace-note.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/traces/create-a-trace-note.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/traces/list-traces-for-a-project.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/traces/list-traces-for-a-project.mdx)
- [internal_docs/specs/span-filter-dsl.md](internal_docs/specs/span-filter-dsl.md)
- [js/app/src/agent/uiOperations/operations/spansFilter.ts](js/app/src/agent/uiOperations/operations/spansFilter.ts)
- [js/app/src/components/chart/AnnotationMetricsChart.tsx](js/app/src/components/chart/AnnotationMetricsChart.tsx)
- [js/app/src/components/chart/MetricChartsPanel.tsx](js/app/src/components/chart/MetricChartsPanel.tsx)
- [js/app/src/components/chart/index.tsx](js/app/src/components/chart/index.tsx)
- [js/app/src/components/chart/metricChartsViewSetting.ts](js/app/src/components/chart/metricChartsViewSetting.ts)
- [js/app/src/components/chart/types.ts](js/app/src/components/chart/types.ts)
- [js/app/src/components/experiment/ExperimentNameWithColorSwatch.tsx](js/app/src/components/experiment/ExperimentNameWithColorSwatch.tsx)
- [js/app/src/components/table/TableViewSettingsButton.tsx](js/app/src/components/table/TableViewSettingsButton.tsx)
- [js/app/src/components/table/index.tsx](js/app/src/components/table/index.tsx)
- [js/app/src/pages/dataset/metrics/DatasetMetricsPage.tsx](js/app/src/pages/dataset/metrics/DatasetMetricsPage.tsx)
- [js/app/src/pages/dataset/metrics/ExperimentAnnotationMetricsGrid.tsx](js/app/src/pages/dataset/metrics/ExperimentAnnotationMetricsGrid.tsx)
- [js/app/src/pages/experiment/ExperimentCompareGridPage.tsx](js/app/src/pages/experiment/ExperimentCompareGridPage.tsx)
- [js/app/src/pages/experiment/ExperimentCompareMetricsCharts.tsx](js/app/src/pages/experiment/ExperimentCompareMetricsCharts.tsx)
- [js/app/src/pages/experiment/ExperimentComparePage.tsx](js/app/src/pages/experiment/ExperimentComparePage.tsx)
- [js/app/src/pages/experiments/ExperimentsMetricsCharts.tsx](js/app/src/pages/experiments/ExperimentsMetricsCharts.tsx)
- [js/app/src/pages/experiments/ExperimentsPage.tsx](js/app/src/pages/experiments/ExperimentsPage.tsx)
- [js/app/src/pages/experiments/ExperimentsTable.tsx](js/app/src/pages/experiments/ExperimentsTable.tsx)
- [js/app/src/pages/project/TableMetricsCharts.tsx](js/app/src/pages/project/TableMetricsCharts.tsx)
- [js/app/src/pages/project/traceFilterDSL.ts](js/app/src/pages/project/traceFilterDSL.ts)
- [js/app/src/store/__tests__/datasetStore.test.ts](js/app/src/store/__tests__/datasetStore.test.ts)
- [js/app/src/store/__tests__/experimentCompareChartsStore.test.ts](js/app/src/store/__tests__/experimentCompareChartsStore.test.ts)
- [js/app/src/store/datasetStore.tsx](js/app/src/store/datasetStore.tsx)
- [js/app/src/store/experimentCompareChartsStore.ts](js/app/src/store/experimentCompareChartsStore.ts)
- [js/app/stories/domains/experiments/ExperimentMetricsCharts.stories.tsx](js/app/stories/domains/experiments/ExperimentMetricsCharts.stories.tsx)
- [src/phoenix/server/api/helpers/experiment_run_filters.py](src/phoenix/server/api/helpers/experiment_run_filters.py)
- [src/phoenix/server/api/input_types/SpanSort.py](src/phoenix/server/api/input_types/SpanSort.py)
- [src/phoenix/trace/dsl/filter.py](src/phoenix/trace/dsl/filter.py)
- [src/phoenix/trace/dsl/query.py](src/phoenix/trace/dsl/query.py)
- [tests/unit/server/api/helpers/test_experiment_run_filters.py](tests/unit/server/api/helpers/test_experiment_run_filters.py)
- [tests/unit/server/api/types/test_Trace_span_aggregates.py](tests/unit/server/api/types/test_Trace_span_aggregates.py)
- [tests/unit/trace/dsl/test_filter.py](tests/unit/trace/dsl/test_filter.py)
- [tests/unit/trace/dsl/test_filter_error_messages.py](tests/unit/trace/dsl/test_filter_error_messages.py)
- [tests/unit/trace/dsl/test_filter_span_cost.py](tests/unit/trace/dsl/test_filter_span_cost.py)
- [tests/unit/trace/dsl/test_filter_spec_conformance.py](tests/unit/trace/dsl/test_filter_spec_conformance.py)
- [tests/unit/trace/dsl/test_query.py](tests/unit/trace/dsl/test_query.py)
- [tests/unit/trace/dsl/test_session_filter.py](tests/unit/trace/dsl/test_session_filter.py)

</details>



This page documents the Phoenix frontend state management architecture, which utilizes Zustand for client-side state stores, Relay for GraphQL data caching, and a theming system built on CSS custom properties. It also covers the domain-specific filter DSL implemented for UI span and session filtering, as well as context providers that tie these parts together.

---

## State Management Architecture

Phoenix employs a layered approach to state management in its React frontend:

- **Zustand** is used for managing ephemeral UI state or user preferences, often persisted locally using middleware like `persist` [js/app/src/store/experimentCompareChartsStore.ts:1-3]() and `devtools`.
- **React Context** provides domain-specific state and configuration with hooks for access [js/app/src/contexts/PreferencesContext.tsx:8-30]().
- **Relay** manages server-synchronized, normalized cache for GraphQL data fetching [js/app/src/RelayEnvironment.ts:1-182]().

### Provider Tree Hierarchy

The React root component organizes various providers in a hierarchy to set up theming, feature flags, authentication, and data fetching layers before rendering the main application routes.

Title: React Provider Hierarchy and Application Root
```mermaid
graph TD
    App["App.tsx: App"] --> FunctionalityProvider["FunctionalityProvider"]
    FunctionalityProvider --> ThemeProvider["ThemeProvider"]
    ThemeProvider --> AppContent["App.tsx: AppContent"]
    AppContent --> RelayEnv["RelayEnvironmentProvider"]
    RelayEnv --> GlobalStyles["GlobalStyles.tsx: GlobalStyles"]
    GlobalStyles --> FeatureFlagsProvider["FeatureFlagsProvider"]
    FeatureFlagsProvider --> PreferencesProvider["PreferencesProvider"]
    PreferencesProvider --> CredentialsProvider["CredentialsProvider"]
    CredentialsProvider --> AppRoutes["Routes.tsx: AppRoutes"]
```

- `FunctionalityProvider` handles initial experimental or feature-flag gating.
- `ThemeProvider` manages theme state for light/dark theme toggling.
- `RelayEnvironmentProvider` provides the Relay store and network for GraphQL.
- `FeatureFlagsProvider`, `PreferencesProvider`, and `CredentialsProvider` supply domain-specific contexts accessible to child components.
- Finally, `AppRoutes` renders the routed pages of the application.

**Sources:**
[js/app/src/App.tsx:15-40]()

---

### Zustand Stores

Phoenix utilizes Zustand for lightweight client-side stores. These often use middleware like `persist` to cache state in `localStorage` for persistence across page reloads.

| Store Name | Purpose | Persistence | Key Managed Entities/Keys |
| :--------- | :-------------------------------------- | :----------------- | :---------------------------------------- |
| **PreferencesStore** | Global UI options and user preferences | Yes (localStorage) | `isAssistantAgentEnabled`, `themeMode`, UI toggles |
| **AgentContext** | PXI assistant agent config and UI mode | No (in-memory) | `fabMode`, `agentsConfig` |
| **CredentialsStore** | API keys for LLM providers | Yes (localStorage) | Mapped credentials per `ModelProvider` |
| **ChatModelStorage** | Last-used chat model selection | Yes (localStorage) | `provider`, `modelName`, `customProvider` |
| **ChatParametersStorage** | Last-used chat parameters | Yes (localStorage) | `systemPrompt`, `temperature`, `topP`, `maxOutputTokens` |
| **ExperimentCompareChartsStore** | Experiment compare chart & delta state | Yes (localStorage) | `metricChartKeysByDatasetId`, `areMetricChartsVisibleByDatasetId`, `areDeltasVisibleByDatasetId` |

These stores offer hooks for synchronous or asynchronous React components to access and modify relevant state with minimal boilerplate.

#### Interaction Example: Assistant Agent Toggle

- The `PreferencesStore` holds a boolean `isAssistantAgentEnabled` tracked by the `AssistantAgentEnabledSetting` UI control.
- The `AgentContext` manages the agent configuration and UI mode, used internally by PXI.
- User toggling updates persist in `PreferencesStore` and trigger UI updates accordingly.

Title: Agent State Flow and Zustand Integration
```mermaid
graph LR
    subgraph "Agent State Flow"
        AgentCtx["AgentContext.tsx: useAgentContext"] -- "provides config" --> AgentForm["AgentSettingsForm.tsx"]
        PrefStore["PreferencesContext.tsx: usePreferencesContext"] -- "isAssistantAgentEnabled" --> AgentSwitch["SettingsAgentsPage.tsx: AssistantAgentEnabledSetting"]
        AgentSwitch -- "onChange event" --> PrefStore
    end
```

The decoupling allows different features to centrally read or update relevant user preferences or agent state independently, while Relay manages server-derived data.

**Sources:**
[js/app/src/pages/settings/SettingsAgentsPage.tsx:76](),
[js/app/src/contexts/PreferencesContext.tsx:8-30](),
[js/app/src/contexts/AgentContext.tsx:22-25](),
[js/app/src/pages/chat/chatModelStorage.ts:26-34](),
[js/app/src/pages/chat/chatParametersStorage.ts:20-28](),
[js/app/src/store/experimentCompareChartsStore.ts:66-154]()

---

### Relay Cache & Data Flow

Relay manages synchronization of server data, caching results client-side according to the Relay store model. It enables declarative data dependencies using GraphQL fragments.

Key points:

- The Relay environment is set up in `RelayEnvironment.ts`, configuring `Store`, `RecordSource`, and a `Network` interface that uses an `authFetch` helper to attach authentication headers on requests [js/app/src/RelayEnvironment.ts:1-182]().
- The environment uses a garbage collection buffer (`gcReleaseBufferSize: 20`) to retain recently visited pages in cache, improving user experience.
- The application root loader `authenticatedRootLoader` pre-fetches the current viewer and agent configuration before rendering routes [js/app/src/pages/authenticatedRootLoader.ts:33-48]().
- Components that need refreshed user information use `useRefetchableFragment` to enable reloading of the viewer fragment post mutation, such as updating API keys or profile [js/app/src/contexts/ViewerContext.tsx:97-133]().

The Relay cache is the single source of truth for server data, scoped by project or user session, and is combined with Zustand UI state for interactivity.

**Sources:**
[js/app/src/RelayEnvironment.ts:161-172](),
[js/app/src/pages/authenticatedRootLoader.ts:9-28](),
[js/app/src/contexts/ViewerContext.tsx:91-133]()

---

## Theming System

Phoenix uses CSS-in-JS (Emotion) coupled with CSS custom properties to implement a flexible theming system supporting light and dark modes, and dynamic application of theme variables.

---

### CSS Custom Properties Architecture

The foundation of theming lies in cascading CSS variables defined on the `:root` selector as part of the global styles:

- The system defines dimension scales such as `--global-dimension-size-200` with a consistent sizing scheme to unify spacing and component sizing [js/app/src/components/filter/styles.ts:43-49]().
- Core colors for backgrounds, interactive components, status colors, borders, and text are declared using variables like `--global-background-color-primary`, `--global-border-color-default`, `--global-focus-color`, and background overlays [js/app/src/components/filter/styles.ts:55-59]().
- Global rounding radii variables such as `--global-rounding-medium` are used to style card corners and inputs for consistent UI visuals [js/app/src/components/filter/styles.ts:57]().

This approach allows theme switching by simply overriding these variables at the root level.

**Sources:**
[js/app/src/components/filter/styles.ts:42-77](),
[js/app/.storybook/preview.tsx:19-24]()

---

### Theme Selection & Application

The `ThemeProvider` component manages whether the `light` or `dark` theme is applied by:

- Setting CSS variables on the root HTML element (`:root`) with `.light` or `.dark` classes.
- Integrating with a custom hook `useSystemTheme` to detect the user’s OS/browser-level preferred color scheme and respond to changes dynamically.
- The Storybook preview configuration injects Phoenix color tokens defining background grays such as `gray-75` to match production UI [js/app/.storybook/preview.tsx:21-40]().

Title: Theming Logic and Root Variable Injection
```mermaid
graph TD
    subgraph "Theming Logic"
        Provider["ThemeProvider.tsx"] -- "provides theme context" --> ThemeContext["ThemeContext"]
        ThemeContext -- "consumed by" --> App["App.tsx"]
        App -- "renders" --> GlobalStyles["GlobalStyles.tsx"]
        GlobalStyles -- "injects CSS variables into" --> RootVars[":root CSS Variables"]
    end
```

This separation allows UI components to access theme values via CSS directly or through helper classes while allowing theme toggling to be globally consistent.

**Sources:**
[js/app/src/App.tsx:4-20](),
[js/app/.storybook/preview.tsx:56-57](),
[js/app/.storybook/preview.tsx:25-40]()

---

## Domain Filter DSL: Span and Session Filtering

Phoenix implements a powerful domain-specific language (DSL) to define expressive filters used in the UI and API to query and filter **Spans** and **Sessions** by attributes, annotations, and nested conditions.

### SpanFilter DSL

- The `SpanFilter` class represents compiled filters on spans.
- Filters are text expressions parsed as Python-like boolean/conditional expressions over span fields, e.g., `"span_kind == 'LLM' and latency_ms > 1000"` [src/phoenix/trace/dsl/filter.py:1-126](), [tests/unit/trace/dsl/test_filter.py:84-158]().
- It translates expressions into SQLAlchemy predicates against the `Span` model and related joined tables such as annotations.
- Supports aliasing, nested attributes (`attributes['key']`), evaluation of span annotations, and parent span conditions [src/phoenix/trace/dsl/filter.py:37-101]().
- Special handling for numeric, string, and boolean attributes ensures correct SQL types and semantics.
- Filters compile into safe, efficient SQL conditions applicable in GraphQL resolvers or direct SQL queries [src/phoenix/trace/dsl/query.py:14-180]().
- Uses dataclasses like `AliasedAnnotationRelation` to represent annotation table aliases for safe multi-join queries over annotations [src/phoenix/trace/dsl/filter.py:34-95](), [tests/unit/trace/dsl/test_filter.py:74-183]().

### SessionFilter DSL

- Symmetric to `SpanFilter`, the `SessionFilter` applies filters at a granularity of sessions.
- It binds to `ProjectSession` columns and session-level aggregates implemented as SQL subqueries (e.g. `num_traces`, `token_count_total`).
- Supports comprehensions like `any(s.status_code == "ERROR" for s in spans)` over nested element tables.
- Joins session aggregates on demand while compiling the filter expression into SQLAlchemy conditions.
- Provides high-level filtering primitives specific to session-centric UI views [src/phoenix/server/session_filters.py:78-83](), [src/phoenix/server/api/types/Project.py:112-116]() (for `_SESSION_FILTER_CONDITION_NOTE`).

---

### Flow from User Filter String to SQL Predicate and UI Filtering

The filter DSL for spans and sessions is tightly integrated with the UI:

Title: Filter DSL Execution Flow
```mermaid
graph TD
    UserInput["UI Filter Input (Python-like expression string)"] --> Parse["Parse & Validate AST (ast.parse)"]
    Parse --> Compile["Compile to SQLAlchemy Expressions (SpanFilter / SessionFilter)"]
    Compile --> DBQuery["Use in Relay GraphQL Resolvers / SQL Queries"]
    DBQuery --> DataFrame["Return & Display Filtered Data in React"]
```

- Users type filter expressions in dashboards or query builders.
- The frontend Relay layer sends filters as strings to the backend API.
- Backend compiles filters into efficient SQL conditions on `Span` or `ProjectSession`.
- Filtered data is returned and displayed in React data tables or charts driven by Relay cache and Zustand UI state.

**Sources:**
[src/phoenix/trace/dsl/filter.py:34-95](),
[src/phoenix/server/session_filters.py:78-83](),
[tests/unit/trace/dsl/test_filter.py:74-183]()

---

## React Context Providers and Hooks

The application defines multiple React contexts to distribute and manage state:

- **ViewerContext** tracks the currently authenticated user and profile [js/app/src/contexts/ViewerContext.tsx:19-54]().
- **PreferencesContext** uses Zustand internally to manage user UI preferences [js/app/src/contexts/PreferencesContext.tsx:8-30]().
- **AgentContext** provides PXI assistant and agent UI mode/config state [js/app/src/contexts/AgentContext.tsx:22-25]().
- **CredentialsContext** manages API key information scoped by LLM provider name.

These contexts provide typed React hooks such as `useViewer()`, `usePreferencesContext()`, and `useAgentContext()` for components to consume without prop-drilling.

They often collaborate with Relay data and Zustand stores for a complete picture of domain and UI state.

**Sources:**
[js/app/src/contexts/ViewerContext.tsx:19-54](),
[js/app/src/contexts/PreferencesContext.tsx:8-30](),
[js/app/src/contexts/AgentContext.tsx:22-25]()

---

## Summary

This page provides a technical deep dive into how Phoenix manages frontend state and theming:

- Zustand handles transient and persisted UI state with per-domain stores.
- Relay caches and normalizes GraphQL server data with preloading and refetching capabilities.
- CSS custom properties and a `ThemeProvider` enable light/dark theming through root-level variables.
- The span and session filter DSL compiles Python-like expressions into SQL predicates for efficient backend filtering.
- React context providers tie these state layers together into a coherent app environment.

Together, these systems enable a reactive, themeable, filterable UI delivering an expressive AI observability experience.

---

## References and Source Citations

| Topic | Files & Lines |
| :----------------------------- | :---------------------------------------- |
| React Provider Hierarchy | [js/app/src/App.tsx:15-40]() |
| Zustand Stores | [js/app/src/pages/settings/SettingsAgentsPage.tsx:76](), [js/app/src/contexts/PreferencesContext.tsx:8-30](), [js/app/src/contexts/AgentContext.tsx:22-25](), [js/app/src/pages/chat/chatModelStorage.ts:26-34](), [js/app/src/pages/chat/chatParametersStorage.ts:20-28](), [js/app/src/store/experimentCompareChartsStore.ts:66-154]() |
| Relay Environment & Cache | [js/app/src/RelayEnvironment.ts:1-182](), [js/app/src/pages/authenticatedRootLoader.ts:9-28](), [js/app/src/contexts/ViewerContext.tsx:91-133]() |
| CSS Custom Properties & Theming | [js/app/src/components/filter/styles.ts:42-77](), [js/app/.storybook/preview.tsx:19-40]() |
| Span and Session Filter DSL | [src/phoenix/trace/dsl/filter.py:34-95](), [src/phoenix/server/session_filters.py:78-83](), [tests/unit/trace/dsl/test_filter.py:74-183]() |
| React Context Providers & Hooks | [js/app/src/contexts/ViewerContext.tsx:19-54](), [js/app/src/contexts/PreferencesContext.tsx:8-30](), [js/app/src/contexts/AgentContext.tsx:22-25]() |

---

## Additional Technical Diagrams

Title: Filter DSL Natural Language to Code Entity Mapping
```mermaid
flowchart LR
    NL["Natural Language Space<br>Filter Expressions<br>(e.g., 'span_kind == LLM and latency_ms > 1000')"] --> Parser["ast.parse (tests/unit/trace/dsl/test_filter.py)"]
    Parser --> Compiler["SpanFilter / SessionFilter (src/phoenix/trace/dsl/filter.py)"]
    Compiler --> SQL["SQLAlchemy Predicate Expressions (sqlalchemy.sql.expression)"]
    SQL --> DB["PostgreSQL/SQLite Database (phoenix.db.models)"]
    DB --> GraphQL["Relay GraphQL Resolver (phoenix.server.api)"]
    GraphQL --> UI["React Components - Data Display (js/app/src)"]

classDef codeEntity fill:#f9f9f9,stroke:#333,stroke-dasharray: 5;
class Parser,Compiler,SQL codeEntity
```
**Sources:**
[src/phoenix/trace/dsl/filter.py:1-100](),
[tests/unit/trace/dsl/test_filter.py:73-82]()

Title: Frontend Domain Contexts and Zustand State Architecture
```mermaid
flowchart TD
    subgraph "Phoenix Frontend Domain Contexts & Stores"
        Preferences["PreferencesStore (Zustand localStorage)"] -->|hook| Components["UI Components"]
        Agents["AgentContext (Zustand in-memory)"] --> Components
        Credentials["CredentialsStore (Zustand localStorage)"] --> Components
        ChatModel["ChatModelStorage (Zustand localStorage)"] --> Components
        ChatParams["ChatParametersStorage (Zustand localStorage)"] --> Components
        ViewerCtx["ViewerContext (Relay + React Context)"] --> Components
    end
    Components --> RelayEnv["RelayEnvironment: Server Data Cache"]
    RelayEnv --> Server["Phoenix GraphQL API Server"]

    style Preferences fill:#eee,stroke:#333
    style Agents fill:#eee,stroke:#333
    style Credentials fill:#eee,stroke:#333
    style ChatModel fill:#eee,stroke:#333
    style ChatParams fill:#eee,stroke:#333
    style ViewerCtx fill:#eee,stroke:#333
    style RelayEnv fill:#ddd,stroke:#222,stroke-width:2px
```
**Sources:**
[js/app/src/contexts/ViewerContext.tsx:19-54](),
[js/app/src/contexts/PreferencesContext.tsx:8-30](),
[js/app/src/contexts/AgentContext.tsx:22-25](),
[js/app/src/RelayEnvironment.ts:1-182]()

---

Sources:
[src/phoenix/trace/dsl/filter.py:1-100](),
[src/phoenix/trace/dsl/query.py:14-180](),
[src/phoenix/server/api/input_types/SpanSort.py:1-170](),
[tests/unit/trace/dsl/test_filter.py:73-183](),
[js/app/src/store/experimentCompareChartsStore.ts:1-154](),
[js/app/src/RelayEnvironment.ts:1-182]()

---

# Page: Playground Interface

# Playground Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/phoenix/evaluation/llm-evals/executors.mdx](docs/phoenix/evaluation/llm-evals/executors.mdx)
- [docs/phoenix/prompt-engineering/how-to-prompts/configure-ai-providers.mdx](docs/phoenix/prompt-engineering/how-to-prompts/configure-ai-providers.mdx)
- [docs/phoenix/prompt-engineering/how-to-prompts/using-the-playground.mdx](docs/phoenix/prompt-engineering/how-to-prompts/using-the-playground.mdx)
- [docs/phoenix/release-notes/01-2026/01-05-2026-appended-messages-for-playground-experiments.mdx](docs/phoenix/release-notes/01-2026/01-05-2026-appended-messages-for-playground-experiments.mdx)
- [docs/phoenix/release-notes/02-2026/02-11-2026-custom-providers.mdx](docs/phoenix/release-notes/02-2026/02-11-2026-custom-providers.mdx)
- [docs/phoenix/release-notes/02-2026/02-12-2026-dataset-evaluators.mdx](docs/phoenix/release-notes/02-2026/02-12-2026-dataset-evaluators.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/create-a-system-api-key.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/create-a-system-api-key.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/create-an-api-key-for-the-authenticated-user.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/create-an-api-key-for-the-authenticated-user.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/delete-a-system-api-key.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/delete-a-system-api-key.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/delete-a-user-api-key.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/delete-a-user-api-key.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/list-all-user-api-keys.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/list-all-user-api-keys.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/list-system-api-keys.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/list-system-api-keys.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/list-the-authenticated-users-api-keys.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/api-keys/list-the-authenticated-users-api-keys.mdx)
- [docs/phoenix/tracing/how-to-tracing/feedback-and-annotations/annotating-in-the-ui.mdx](docs/phoenix/tracing/how-to-tracing/feedback-and-annotations/annotating-in-the-ui.mdx)
- [js/app/src/components/experiment/ExperimentCompareDetails.tsx](js/app/src/components/experiment/ExperimentCompareDetails.tsx)
- [js/app/src/components/experiment/ExperimentInputCell.tsx](js/app/src/components/experiment/ExperimentInputCell.tsx)
- [js/app/src/components/experiment/__generated__/ExperimentCompareDetailsQuery.graphql.ts](js/app/src/components/experiment/__generated__/ExperimentCompareDetailsQuery.graphql.ts)
- [js/app/src/pages/experiment/ExperimentCompareDetailsDialog.tsx](js/app/src/pages/experiment/ExperimentCompareDetailsDialog.tsx)
- [js/app/src/pages/experiment/ExperimentCompareListPage.tsx](js/app/src/pages/experiment/ExperimentCompareListPage.tsx)
- [js/app/src/pages/experiment/ExperimentCompareTable.tsx](js/app/src/pages/experiment/ExperimentCompareTable.tsx)
- [js/app/src/pages/experiment/TraceDetailsDrawer.tsx](js/app/src/pages/experiment/TraceDetailsDrawer.tsx)
- [js/app/src/pages/experiment/__generated__/ExperimentCompareListPageQuery.graphql.ts](js/app/src/pages/experiment/__generated__/ExperimentCompareListPageQuery.graphql.ts)
- [js/app/src/pages/experiment/__generated__/ExperimentCompareListPage_aggregateData.graphql.ts](js/app/src/pages/experiment/__generated__/ExperimentCompareListPage_aggregateData.graphql.ts)
- [js/app/src/pages/experiment/__generated__/ExperimentCompareListPage_comparisons.graphql.ts](js/app/src/pages/experiment/__generated__/ExperimentCompareListPage_comparisons.graphql.ts)
- [js/app/src/pages/experiment/__generated__/ExperimentComparePageQueriesCompareGridQuery.graphql.ts](js/app/src/pages/experiment/__generated__/ExperimentComparePageQueriesCompareGridQuery.graphql.ts)
- [js/app/src/pages/experiment/__generated__/ExperimentComparePageQueriesCompareListQuery.graphql.ts](js/app/src/pages/experiment/__generated__/ExperimentComparePageQueriesCompareListQuery.graphql.ts)
- [js/app/src/pages/experiment/__generated__/ExperimentCompareTableQuery.graphql.ts](js/app/src/pages/experiment/__generated__/ExperimentCompareTableQuery.graphql.ts)
- [js/app/src/pages/experiment/__generated__/ExperimentCompareTable_comparisons.graphql.ts](js/app/src/pages/experiment/__generated__/ExperimentCompareTable_comparisons.graphql.ts)
- [js/app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx](js/app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx)
- [js/app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableFragment.graphql.ts](js/app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableFragment.graphql.ts)
- [js/app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableQuery.graphql.ts](js/app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableQuery.graphql.ts)
- [js/app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableRefetchQuery.graphql.ts](js/app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableRefetchQuery.graphql.ts)
- [js/app/src/utils/datasetEvaluatorUtils.ts](js/app/src/utils/datasetEvaluatorUtils.ts)

</details>



The Playground Interface is Phoenix's frontend system enabling users to interactively test LLM prompts in real time across multiple model providers. It supports streaming AI-generated outputs, managing multiple prompt instances and their repetitions, integrating internal credential management, and linking to span data for reproduction and debugging of inference calls.

This page documents the frontend React components, Zustand state management, backend communication via GraphQL streaming subscriptions, instance lifecycle management, credential handling, and the chat completion subscription flow in detail.

---

## Component Architecture

The Playground UI is implemented as a modular React component tree. The main responsibilities and file locations of key components are:

| Component | File | Responsibility |
| :------------------------ | :--------------------------------------- | :------------------------------------------------------------------------------------------------ |
| `Playground` | `app/src/pages/playground/Playground.tsx` | Root entrypoint; initiates loading of model providers, manages URL params, provides Playground context |
| `PlaygroundContent` | `app/src/pages/playground/Playground.tsx` | Layout with movable panels; renders prompt editor, input fields, output display, dataset controls |
| `PlaygroundTemplate` | `app/src/pages/playground/PlaygroundTemplate.tsx` | Manages chat prompt template editor, model config UI, tool settings, and response format selection |
| `PlaygroundChatTemplate` | `app/src/pages/playground/PlaygroundChatTemplate.tsx` | Displays/edit chat message sequences with drag-and-drop, role selection, and tool call handling |
| `PlaygroundOutput` | `app/src/pages/playground/PlaygroundOutput.tsx` | Shows streaming response completions, handles incremental tool call streaming, repetition selection |
| `PlaygroundInput` | `app/src/pages/playground/PlaygroundInput.tsx` | Input UI for providing template variables |
| `PlaygroundDatasetSection` | `app/src/pages/playground/PlaygroundDatasetSection.tsx` | Dataset selection UI and batch experiment run interface |
| `PlaygroundDatasetExamplesTable` | `app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx` | Displays batch experiment run results table with virtualization |

### Component Hierarchy Diagram

```mermaid
graph TB
    Playground["Playground<br/>app/src/pages/playground/Playground.tsx:136"]
    PlaygroundProvider["PlaygroundProvider<br/>contexts/PlaygroundContext"]
    PlaygroundContent["PlaygroundContent()<br/>app/src/pages/playground/Playground.tsx:232"]
    
    subgraph "Prompt_Section"
        PlaygroundTemplate["PlaygroundTemplate<br/>PlaygroundTemplate.tsx"]
        PlaygroundChatTemplate["PlaygroundChatTemplate<br/>PlaygroundChatTemplate.tsx:77"]
        PlaygroundConfigButton["PlaygroundConfigButton<br/>PlaygroundConfigButton.tsx"]
        PlaygroundTools["PlaygroundTools<br/>PlaygroundTools.tsx"]
        PlaygroundResponseFormat["PlaygroundResponseFormat<br/>PlaygroundResponseFormat.tsx"]
    end
    
    subgraph "Input_Section"
        PlaygroundInput["PlaygroundInput<br/>PlaygroundInput.tsx"]
        PlaygroundDatasetSelect["PlaygroundDatasetSelect<br/>PlaygroundDatasetSelect.tsx"]
    end
    
    subgraph "Output_Section"
        PlaygroundOutput["PlaygroundOutput<br/>app/src/pages/playground/PlaygroundOutput.tsx:149"]
        PlaygroundOutputMessage["PlaygroundOutputMessage()<br/>PlaygroundOutput.tsx:84"]
        PlaygroundToolCall["PlaygroundToolCall<br/>PlaygroundToolCall.tsx"]
    end
    
    subgraph "Dataset_Mode"
        PlaygroundDatasetSection["PlaygroundDatasetSection<br/>PlaygroundDatasetSection.tsx"]
        PlaygroundDatasetExamplesTable["PlaygroundDatasetExamplesTable<br/>PlaygroundDatasetExamplesTable.tsx"]
    end
    
    Playground --> PlaygroundProvider
    PlaygroundProvider --> PlaygroundContent
    PlaygroundContent --> PlaygroundTemplate
    PlaygroundContent --> PlaygroundInput
    PlaygroundContent --> PlaygroundOutput
    PlaygroundContent --> PlaygroundDatasetSection
    
    PlaygroundTemplate --> PlaygroundChatTemplate
    PlaygroundTemplate --> PlaygroundConfigButton
    PlaygroundChatTemplate --> PlaygroundTools
    PlaygroundChatTemplate --> PlaygroundResponseFormat
    
    PlaygroundOutput --> PlaygroundOutputMessage
    PlaygroundOutputMessage --> PlaygroundToolCall
    
    PlaygroundDatasetSection --> PlaygroundDatasetExamplesTable
```

Sources:
[app/src/pages/playground/Playground.tsx:136-210]()
[app/src/pages/playground/PlaygroundChatTemplate.tsx:77-181]()
[app/src/pages/playground/PlaygroundOutput.tsx:149-548]()
[app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx:182-211]()

---

## State Management

The Playground frontend implements centralized reactive state management via Zustand.

### Store Structure Overview

- **Instances:** Each `PlaygroundNormalizedInstance` holds:
  - A unique instance ID.
  - Template data with normalized chat messages (`PlaygroundNormalizedChatTemplate`).
  - Model configuration (provider, model name, repetition count).
  - Tool and response format settings.
  - Multiple repetitions output storage and related metadata.
- **allInstanceMessages:** A flat dictionary mapping message IDs to `ChatMessage` objects to avoid duplication and enable granular updates.
- **Dirty flags:** Fields tracking whether an instance's prompt or settings are unsaved.
- **Template format:** Tracks which prompt template formatting system is used (Mustache, None, etc.).
- **Streaming flag:** Whether real-time streaming of responses is enabled.

### Key Store Actions

- `addInstance`, `updateInstance`, `deleteInstance`: Manage lifecycle of playground instances.
- `runPlaygroundInstances`: Trigger execution of playground runs for given instances.
- `appendRepetitionOutput` and `setRepetitionSpanId`: Update streaming output and link spans to repetitions.
- Management of selected repetition per instance for UI display.

### Normalized Messages Pattern Diagram

```mermaid
graph TB
    PlaygroundInstance["PlaygroundNormalizedInstance<br/>id: 0"]
    Template["template.messageIds: [2, 3]<br/>PlaygroundNormalizedChatTemplate"]
    MessageStore["allInstanceMessages<br/>Record&lt;number, ChatMessage&gt;"]
    Msg2["2: ChatMessage<br/>{role: 'system', content: '...'}"]
    Msg3["3: ChatMessage<br/>{role: 'user', content: '...'}"]
    
    PlaygroundInstance --> Template
    Template --> MessageStore
    MessageStore --> Msg2
    MessageStore --> Msg3
```

### Instance Initialization Logic

New instances are created using `createNormalizedPlaygroundInstance()` function in the playground store. This factory seeds instances with a default two-message chat template:

```typescript
export const generateChatCompletionTemplate = (): PlaygroundChatTemplate => ({
  __type: "chat",
  messages: [
    { id: generateMessageId(), role: "system", content: "You are a chatbot" },
    { id: generateMessageId(), role: "user", content: "{{question}}" },
  ],
});

export function createNormalizedPlaygroundInstance() {
  const template = generateChatCompletionTemplate();
  const normalizedTemplate = normalizeChatTemplate(template);
  return {
    instance: {
      id: generateInstanceId(),
      template: normalizedTemplate.template,
      ...DEFAULT_INSTANCE_PARAMS(),
      selectedRepetitionNumber: 1,
    } as PlaygroundNormalizedInstance,
    instanceMessages: normalizedTemplate.messages,
  };
}
```

Sources:
[app/src/store/playground/types.ts:247-457]()
[app/src/store/playground/playgroundStore.tsx:80-170]()

---

## Communication and Streaming Flow

The Playground frontend communicates with the backend via a GraphQL subscription that streams partial LLM completion chunks incrementally.

### Backend Streaming

The backend provides the `chatCompletion` subscription in `src/phoenix/server/api/subscriptions.py`, which uses `_stream_single_chat_completion` to:

- Resolve the LLM client matching the provider/model using `get_playground_client` [src/phoenix/server/api/subscriptions.py:40]().
- Invoke `chat_completion_create` on the client [src/phoenix/server/api/subscriptions.py:106](), which returns an async iterator of streamed chunks.
- Stream each chunk back to the client wrapped in `ChatCompletionSubscriptionPayload` types [src/phoenix/server/api/subscriptions.py:115]().
- On completion, yield a `ChatCompletionSubscriptionResult` containing metadata and span ID [src/phoenix/server/api/subscriptions.py:129]().
- Handle errors with `ChatCompletionSubscriptionError` payloads [src/phoenix/server/api/subscriptions.py:118]().

The backend tracks spans via the OpenTelemetry `Tracer` that records the LLM call and flushes tracing data to the database [src/phoenix/server/api/subscriptions.py:123-125]().

### Frontend Subscription and Chunk Handling

The frontend subscribes to this stream using Relay's `requestSubscription()` in `app/src/pages/playground/PlaygroundOutput.tsx`. Incoming chunks are handled asynchronously:

- **TextChunk:** Partial text output appended to the display buffer [app/src/pages/playground/PlaygroundOutput.tsx:290]().
- **ToolCallChunk:** Streaming partial tool call arguments integrated progressively [app/src/pages/playground/PlaygroundOutput.tsx:300]().
- **ChatCompletionSubscriptionResult:** Signals completion, contains reference to stored span for UI linkage [app/src/pages/playground/PlaygroundOutput.tsx:310]().
- **ChatCompletionSubscriptionError:** Displays error messages for user [app/src/pages/playground/PlaygroundOutput.tsx:313]().

### Sequence Diagram of Full Streaming Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "PlaygroundOutput.tsx"
    participant Relay as "Relay Environment"
    participant Backend as "subscriptions.py"
    participant LLM as "PlaygroundClient"
    
    User->>Frontend: Click Run
    Frontend->>Relay: requestSubscription(ChatCompletionInput)
    Relay->>Backend: chatCompletion(input)
    Backend->>LLM: chat_completion_create()
    
    loop Streaming Chunks
        LLM-->>Backend: TextChunk / ToolCallChunk
        Backend-->>Relay: ChatCompletionSubscriptionPayload
        Relay-->>Frontend: onNext(payload)
        Frontend->>Frontend: appendRepetitionOutput()
    end
    
    Backend-->>Relay: ChatCompletionSubscriptionResult (Span ID)
    Relay-->>Frontend: onNext(result)
```

Sources:
[src/phoenix/server/api/subscriptions.py:76-134]()
[app/src/pages/playground/PlaygroundOutput.tsx:187-377]()
[src/phoenix/server/api/helpers/playground_clients.py:166-209]()

---

## Template Editing and Message Handling

The prompt template editor is centralized in `PlaygroundChatTemplate`, which manages the chat-style prompt message sequence.

Key features:

- **Drag-and-drop reordering:** Uses `@dnd-kit/react` sortable utilities to reorder messages visually and update the normalized message ID array.
- **Role selection:** Each message can be assigned a role (system, user, assistant, tool).
- **Editing modes:** Messages can be edited either as textual content or as tool call invocation data.
- **Template formats:** Supports multiple template formats (Mustache, f-string) with validation for syntactic correctness [docs/phoenix/prompt-engineering/how-to-prompts/using-the-playground.mdx:18-22]().

Sources:
[app/src/pages/playground/PlaygroundChatTemplate.tsx:67-157]()
[docs/phoenix/prompt-engineering/how-to-prompts/using-the-playground.mdx:18-22]()

---

## Instance Management

Phoenix Playground supports multiple simultaneously open playground instances to compare prompt versions or separate experiments side-by-side [docs/phoenix/prompt-engineering/how-to-prompts/using-the-playground.mdx:45-48]().

Features:

- Up to a configurable maximum instances (default 4).
- Each instance maintains independent state: model config, prompt template, tools, repetition runs.
- Repetitions allow running multiple independent runs within one instance for variance/seed testing.

Sources:
[app/src/store/playground/playgroundStore.tsx:20-87]()
[docs/phoenix/prompt-engineering/how-to-prompts/using-the-playground.mdx:45-48]()

---

## Credential Handling and Use

API credentials for various LLM providers are managed securely through four resolution options [docs/phoenix/prompt-engineering/how-to-prompts/configure-ai-providers.mdx:8-16]():

1. **Browser**: Stored in local storage via the `PlaygroundCredentialsDropdown` UI [docs/phoenix/prompt-engineering/how-to-prompts/configure-ai-providers.mdx:10]().
2. **Database (Secrets)**: Saved encrypted in the `secrets` table via the settings page [docs/phoenix/prompt-engineering/how-to-prompts/configure-ai-providers.mdx:11-28]().
3. **Database (Custom Providers)**: Named provider configurations stored server-side with custom routing and endpoints [docs/phoenix/prompt-engineering/how-to-prompts/configure-ai-providers.mdx:12-34]().
4. **Environment Variables**: Set directly in the server environment (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.) [docs/phoenix/prompt-engineering/how-to-prompts/configure-ai-providers.mdx:13-48]().

When initiating a run, `getChatCompletionInput` packages credentials and provider details safely [app/src/pages/playground/playgroundUtils.ts:750-830]().

Sources:
[docs/phoenix/prompt-engineering/how-to-prompts/configure-ai-providers.mdx:8-67]()
[app/src/pages/playground/playgroundUtils.ts:750-830]()

---

## Span Integration for Playground Hydration

The Playground supports initializing an instance from a previously stored LLM span trace to recreate the prompt environment.

- `transformSpanAttributesToPlaygroundInstance` parses OpenInference semantic conventions in span attributes [app/src/pages/playground/playgroundUtils.ts:140-220]().
- Extracts input messages, model configuration, and tool calls into the normalized playground instance state.
- `processAttributeToolCalls` converts provider-specific tool call representations into internal formats [app/src/pages/playground/playgroundUtils.ts:620-780]().

Sources:
[app/src/pages/playground/playgroundUtils.ts:140-220]()
[app/src/pages/playground/playgroundUtils.ts:620-780]()

---

## System Names to Code Entities

```mermaid
graph TB
    PlaygroundInterface["Playground Interface (System)"]
    PlaygroundComponent["Playground React Component<br/>app/src/pages/playground/Playground.tsx"]
    PlaygroundStore["Playground Zustand Store<br/>app/src/store/playground/playgroundStore.tsx"]
    GraphQLSubscription["ChatCompletion GraphQL Subscriptions<br/>src/phoenix/server/api/subscriptions.py"]
    PlaygroundStreamingClient["PlaygroundClient (LLM Client Abstraction)<br/>src/phoenix/server/api/helpers/playground_clients.py"]
    CredentialsContext["CredentialsContext<br/>app/src/contexts/CredentialsContext.tsx"]
    SpanHydrationUtil["transformSpanAttributesToPlaygroundInstance<br/>app/src/pages/playground/playgroundUtils.ts"]
    ToolCallProcessing["processAttributeToolCalls<br/>app/src/pages/playground/playgroundUtils.ts"]
    
    PlaygroundInterface --> PlaygroundComponent
    PlaygroundInterface --> PlaygroundStore
    PlaygroundInterface --> GraphQLSubscription
    PlaygroundInterface --> PlaygroundStreamingClient
    PlaygroundInterface --> CredentialsContext
    PlaygroundInterface --> SpanHydrationUtil
    PlaygroundInterface --> ToolCallProcessing
```

Sources:
[src/phoenix/server/api/helpers/playground_clients.py:166-178]()
[src/phoenix/server/api/subscriptions.py:192-200]()

---

## Playground Data Flow Detail

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "Playground.tsx / PlaygroundOutput.tsx"
    participant Store as "Zustand Playground Store"
    participant Relay as "Relay Environment"
    participant Backend as "subscriptions.py"
    participant LLMClient as "PlaygroundClient (LLM API)"
    participant DB as "Phoenix DB (SQLAlchemy models)"
    
    User->>Frontend: Configure prompt, model, tools, repetitions
    Frontend->>Store: Update instances & normalized messages
    User->>Frontend: Click Run
    Frontend->>Relay: requestSubscription(ChatCompletionInput)
    Relay->>Backend: Resolve chatCompletion subscription
    Backend->>LLMClient: chat_completion_create (stream)
    LLMClient->>Backend: Stream text and toolcall chunks
    Backend->>Relay: Stream chunks as ChatCompletionSubscriptionPayload
    Relay->>Frontend: Stream chunks to PlaygroundOutput
    Frontend->>Store: appendRepetitionOutput, update status
    Backend->>DB: Flush span/traces after completion
    Backend->>Relay: ChatCompletionSubscriptionResult with span metadata
    Relay->>Frontend: Update with span info & finalize output display
```

Sources:
[src/phoenix/server/api/helpers/playground_clients.py:160-210]()
[src/phoenix/server/api/subscriptions.py:70-135]()
[app/src/pages/playground/Playground.tsx:136-210]()
[app/src/store/playground/playgroundStore.tsx:20-170]()
[app/src/pages/playground/PlaygroundOutput.tsx:150-380]()
[app/src/pages/playground/playgroundUtils.ts:100-220]()

---

# Page: AI Assistant (PxI) Interface

# AI Assistant (PxI) Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/phoenix/pxi.mdx](docs/phoenix/pxi.mdx)
- [evals/harbor/jobs/trail-benchmark-dev-no-code-mode.yaml](evals/harbor/jobs/trail-benchmark-dev-no-code-mode.yaml)
- [js/app/src/components/agent/AgentChatInput.tsx](js/app/src/components/agent/AgentChatInput.tsx)
- [js/app/src/components/agent/Chat.tsx](js/app/src/components/agent/Chat.tsx)
- [js/app/src/components/agent/SkillPromptInput.tsx](js/app/src/components/agent/SkillPromptInput.tsx)
- [js/app/src/components/agent/SkillPromptInputBoundary.tsx](js/app/src/components/agent/SkillPromptInputBoundary.tsx)
- [js/app/src/components/agent/__tests__/SkillPromptInput.test.tsx](js/app/src/components/agent/__tests__/SkillPromptInput.test.tsx)
- [js/app/src/components/agent/__tests__/agentChatPlaceholder.test.ts](js/app/src/components/agent/__tests__/agentChatPlaceholder.test.ts)
- [js/app/src/components/agent/__tests__/promptHistory.test.ts](js/app/src/components/agent/__tests__/promptHistory.test.ts)
- [js/app/src/components/agent/agentChatPlaceholder.ts](js/app/src/components/agent/agentChatPlaceholder.ts)
- [js/app/src/components/agent/promptHistory.ts](js/app/src/components/agent/promptHistory.ts)
- [js/app/tests/app-frame-overlays.spec.ts](js/app/tests/app-frame-overlays.spec.ts)
- [js/app/tests/overlay-audit.spec.ts](js/app/tests/overlay-audit.spec.ts)
- [src/phoenix/server/agents/agent_factory.py](src/phoenix/server/agents/agent_factory.py)
- [src/phoenix/server/agents/capabilities/tools/external/__init__.py](src/phoenix/server/agents/capabilities/tools/external/__init__.py)
- [src/phoenix/server/agents/capabilities/tools/internal/bash.py](src/phoenix/server/agents/capabilities/tools/internal/bash.py)
- [src/phoenix/server/agents/prompts/__init__.py](src/phoenix/server/agents/prompts/__init__.py)
- [src/phoenix/server/agents/prompts/skills/phoenix-graphql/SKILL.md](src/phoenix/server/agents/prompts/skills/phoenix-graphql/SKILL.md)
- [src/phoenix/server/agents/prompts/static/base/BASE_INSTRUCTIONS.xml](src/phoenix/server/agents/prompts/static/base/BASE_INSTRUCTIONS.xml)
- [src/phoenix/server/agents/prompts/tools/PHOENIX_MCP_TOOL_INSTRUCTIONS.xml.j2](src/phoenix/server/agents/prompts/tools/PHOENIX_MCP_TOOL_INSTRUCTIONS.xml.j2)
- [src/phoenix/server/api/graphql_execute.py](src/phoenix/server/api/graphql_execute.py)
- [src/phoenix/server/mcp/graphql/__init__.py](src/phoenix/server/mcp/graphql/__init__.py)
- [src/phoenix/server/mcp/graphql/output.py](src/phoenix/server/mcp/graphql/output.py)
- [src/phoenix/server/mcp/graphql/tools.py](src/phoenix/server/mcp/graphql/tools.py)
- [src/phoenix/server/mcp/skills/__init__.py](src/phoenix/server/mcp/skills/__init__.py)
- [src/phoenix/server/mcp_server.py](src/phoenix/server/mcp_server.py)
- [tests/unit/server/agents/capabilities/test_external_tools.py](tests/unit/server/agents/capabilities/test_external_tools.py)
- [tests/unit/server/agents/capabilities/test_phoenix_mcp.py](tests/unit/server/agents/capabilities/test_phoenix_mcp.py)
- [tests/unit/server/agents/capabilities/tools/internal/test_bash.py](tests/unit/server/agents/capabilities/tools/internal/test_bash.py)
- [tests/unit/server/agents/prompts/test_static_prompts.py](tests/unit/server/agents/prompts/test_static_prompts.py)
- [tests/unit/server/agents/test_agent_factory.py](tests/unit/server/agents/test_agent_factory.py)
- [tests/unit/server/mcp/test_skills.py](tests/unit/server/mcp/test_skills.py)
- [tests/unit/server/test_app_mcp_mount.py](tests/unit/server/test_app_mcp_mount.py)

</details>



The Phoenix Intelligence (PxI) interface provides a built-in AI assistant chat system integrated directly into the Phoenix frontend UI and backed by a robust server-side agent framework (`pydantic-ai`). It enables users to interact with their observability data via natural language, perform ad hoc investigations, query traces, spans, and datasets, and execute safe code/GraphQL operations through specialized tools.

This page documents the technical details of the PxI interface, covering the React chat components in `js/app/src/components/agent/Chat.tsx`, the server-side agent factory (`src/phoenix/server/agents/agent_factory.py`), the Model Context Protocol (MCP) tool registry (`src/phoenix/server/mcp_server.py`), capabilities like `BashCapability`, and the prompt and skills systems.

---

## System Overview

PxI combines a React-based chat interface with a Python agent backend built on top of `pydantic_ai`. The agent is pointed directly at your observability datastore, allowing it to read context from the active page, invoke tools, run GraphQL queries via a virtual shell, and inspect traces.

### Key Architectural Components

- **Frontend Chat (`Chat.tsx`)**: Renders the conversation transcript, empty states, thinking indicators, and message components [js/app/src/components/agent/Chat.tsx:1-120]().
- **Agent Factory (`agent_factory.py`)**: Assembles the `Agent[AgentDependencies, AgentOutput]` instance, attaching capabilities based on runtime configurations and UI context [src/phoenix/server/agents/agent_factory.py:69-94]().
- **In-Process MCP Server (`mcp_server.py`)**: Generates an ASGI-compatible `FastMCP` server from Phoenix's REST API routes, allowing zero-network-hop tool calls [src/phoenix/server/mcp_server.py:1-24]().
- **Bash & GraphQL Toolset (`bash.py`)**: Provides a sandboxed virtual shell (`bashkit`) equipped with the `phoenix-gql` utility for querying the Phoenix GraphQL API [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95]().

Sources: [js/app/src/components/agent/Chat.tsx:1-120](), [src/phoenix/server/agents/agent_factory.py:69-94](), [src/phoenix/server/mcp_server.py:1-24](), [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95]()

---

## Data Flow: Natural Language to Code Entities

The PxI request lifecycle bridges user natural language intent with server-side code execution, database lookups, and OpenTelemetry tracing.

```mermaid
flowchart TD
    subgraph Natural_Language_Space["Natural Language Space"]
        UserNL["User natural language input: 'Why did trace X fail?'"]
        ChatUI["React Chat Component (js/app/src/components/agent/Chat.tsx)"]
    end

    subgraph API_And_Runtime_Space["API & Runtime Space"]
        AgentRuntime["Pydantic-AI Agent Runtime (src/phoenix/server/agents/agent_factory.py)"]
        OITracer["OpenInference Tracer (OITracer)"]
    end

    subgraph Code_Entity_Space["Code Entity Space"]
        BashTool["BashToolset & BashCapability (src/phoenix/server/agents/capabilities/tools/internal/bash.py)"]
        PhoenixGQL["phoenix-gql CLI utility"]
        MCPToolset["PhoenixMCPToolset (src/phoenix/server/mcp_server.py)"]
        GraphQLAPI["Phoenix GraphQL Schema & Resolvers"]
    end

    UserNL --> ChatUI
    ChatUI --> AgentRuntime
    AgentRuntime --> OITracer
    AgentRuntime --> BashTool
    AgentRuntime --> MCPToolset
    BashTool --> PhoenixGQL
    PhoenixGQL --> GraphQLAPI
    MCPToolset --> GraphQLAPI
```

Sources: [src/phoenix/server/agents/agent_factory.py:63-126](), [src/phoenix/server/mcp_server.py:1-24](), [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95](), [js/app/src/components/agent/Chat.tsx:1-120]()

---

## Server-Side Agent Factory

The server-side agent is instantiated via `build_agent()` in `src/phoenix/server/agents/agent_factory.py` [src/phoenix/server/agents/agent_factory.py:69-94](). It wires together core capabilities and optional toolsets depending on user permissions, edit permissions, and feature flags.

### Capabilities and Toolsets

- **`GetCurrentDatetimeCapability`**: Injects current timestamp awareness [src/phoenix/server/agents/agent_factory.py:104-105]().
- **`UIContextsCapability`**: Injects UI context instructions (`AgentPrompts.ui_contexts`) representing the page the user is currently viewing [src/phoenix/server/agents/agent_factory.py:107-114]().
- **`BashCapability`**: Provides a sandboxed virtual shell (`bash`) executing `phoenix-gql` and script utilities [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95]().
- **`PhoenixMCPCapability`**: Exposes Phoenix REST endpoints as MCP tools via `PhoenixMCPToolset` [src/phoenix/server/agents/agent_factory.py:136-151]().
- **`MintlifyDocsMCPCapability`**: Integrates documentation searching tools for Phoenix docs [src/phoenix/server/agents/agent_factory.py:129-135]().

```mermaid
flowchart TD
    subgraph Agent_Initialization["Agent Initialization"]
        BuildAgent["build_agent() (src/phoenix/server/agents/agent_factory.py)"]
        ResolvedPrompts["AgentPrompts (src/phoenix/server/agents/prompts/__init__.py)"]
    end

    subgraph Capability_Mounting["Capability Mounting"]
        TimeCap["GetCurrentDatetimeCapability"]
        UIContextCap["UIContextsCapability"]
        BashCap["BashCapability"]
        PhoenixMCPCap["PhoenixMCPCapability"]
        DocsMCPCap["MintlifyDocsMCPCapability"]
    end

    BuildAgent --> ResolvedPrompts
    BuildAgent --> TimeCap
    BuildAgent --> UIContextCap
    BuildAgent --> BashCap
    BuildAgent --> PhoenixMCPCap
    BuildAgent --> DocsMCPCap
```

Sources: [src/phoenix/server/agents/agent_factory.py:69-151](), [src/phoenix/server/agents/prompts/__init__.py:43-53](), [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95]()

---

## Tool Registry and In-Process MCP Server

Phoenix derives its agent tools directly from its OpenAPI / REST specifications and mounts an in-process FastMCP server at `/mcp` [src/phoenix/server/mcp_server.py:1-24]().

### Key Design Aspects

- **Internal Dispatch**: Tool calls are dispatched back into the Phoenix FastAPI application in-process via an ASGI transport, avoiding network hops and preserving middleware security [src/phoenix/server/mcp_server.py:1-17]().
- **Identity Propagation**: The authenticated principal is carried directly in the internal request's ASGI scope (`INTERNAL_PRINCIPAL_SCOPE_KEY`) via `_InternalIdentityDispatch`, ensuring proper authorization [src/phoenix/server/mcp_server.py:11-16]().
- **Code Mode**: To prevent context window bloat from advertising hundreds of REST endpoints individually, code-mode discovery tools (`search`, `execute`, `list_tools`) are used [src/phoenix/server/mcp_server.py:18-24]().

Sources: [src/phoenix/server/mcp_server.py:1-24](), [tests/unit/server/agents/capabilities/test_phoenix_mcp.py:1-35]()

---

## Bash Capability and GraphQL Execution

The `BashCapability` runs commands inside a server-side virtual shell (`bashkit`) [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-62](). It exposes the `phoenix-gql` command-line utility for running GraphQL queries and mutations against Phoenix.

### Execution Constraints & `phoenix-gql`

- **Sandboxed Execution**: Runs in a virtual shell with general-purpose network access disabled; host binaries (like `apt`, `brew`, `git`) are absent [src/phoenix/server/agents/capabilities/tools/internal/bash.py:56-62]().
- **Schema Discovery**: `phoenix-gql schema --search <text>` discovers types and fields without full introspection [src/phoenix/server/agents/capabilities/tools/internal/bash.py:67-68]().
- **Mutation Policies**: `GraphQLMutationPolicy` enforces approval requirements for state-changing operations [src/phoenix/server/agents/capabilities/tools/internal/bash.py:40-50]().

Sources: [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95](), [tests/unit/server/agents/capabilities/tools/internal/test_bash.py:1-50]()

---

## Skills and Prompts System

PxI utilizes a structured skill and prompt template catalog located in `src/phoenix/server/agents/prompts/` and `src/phoenix/server/mcp/skills/`.

### Skill Structure

- **`phoenix-graphql` Skill**: Teaches the agent how to write efficient GraphQL queries, use entrypoints (`node(id:)`, connections, by-name helpers), and paginate properly [src/phoenix/server/agents/prompts/skills/phoenix-graphql/SKILL.md:1-49]().
- **Agent Prompts (`AgentPrompts`)**: Dataclass aggregating base instructions, viewer access rules, subagent instructions, and UI context prompt templates [src/phoenix/server/agents/prompts/__init__.py:43-53]().

Sources: [src/phoenix/server/agents/prompts/__init__.py:43-53](), [src/phoenix/server/agents/prompts/skills/phoenix-graphql/SKILL.md:1-49](), [tests/unit/server/mcp/test_skills.py:1-30]()

---

## Frontend Chat Interface (`Chat.tsx`)

The React frontend component `Chat` in `js/app/src/components/agent/Chat.tsx` manages the chat layout, input actions, thinking indicators, and scroll states [js/app/src/components/agent/Chat.tsx:1-120]().

### Key UI Features

- **Thinking Indicator**: `shouldShowThinkingIndicator()` dynamically tracks whether a request is in flight or waiting for assistant parts [js/app/src/components/agent/Chat.tsx:95-117]().
- **Scroll Management**: Coordinates turn placement, auto-scrolling during streaming, and user scroll interruptions without competing with native browser scroll anchoring [js/app/src/components/agent/Chat.tsx:204-212]().
- **Elicitation & Prompts**: Integrates prompt history, slash commands, and elicitation carousels for interactive tool outputs [js/app/src/components/agent/Chat.tsx:22-31]().

Sources: [js/app/src/components/agent/Chat.tsx:1-120](), [js/app/src/components/agent/Chat.tsx:95-117]()

---

# Page: Feature Systems

# Feature Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/phoenix.mdx](docs/phoenix.mdx)
- [docs/phoenix/evaluation/concepts-evals/evaluating-multi-agent-systems.mdx](docs/phoenix/evaluation/concepts-evals/evaluating-multi-agent-systems.mdx)
- [docs/phoenix/evaluation/llm-evals.mdx](docs/phoenix/evaluation/llm-evals.mdx)
- [docs/phoenix/integrations/python/pydantic/pydantic-evals.mdx](docs/phoenix/integrations/python/pydantic/pydantic-evals.mdx)
- [docs/phoenix/production-guide.mdx](docs/phoenix/production-guide.mdx)
- [docs/phoenix/release-notes/01-2025/01-18-2025-automatic-and-manual-span-tracing.mdx](docs/phoenix/release-notes/01-2025/01-18-2025-automatic-and-manual-span-tracing.mdx)
- [docs/phoenix/resources/frequently-asked-questions.mdx](docs/phoenix/resources/frequently-asked-questions.mdx)
- [docs/phoenix/resources/frequently-asked-questions/what-is-the-difference-between-phoenix-and-arize.mdx](docs/phoenix/resources/frequently-asked-questions/what-is-the-difference-between-phoenix-and-arize.mdx)
- [docs/phoenix/resources/phoenix-to-arize-ax-migration.mdx](docs/phoenix/resources/phoenix-to-arize-ax-migration.mdx)
- [docs/phoenix/self-hosting.mdx](docs/phoenix/self-hosting.mdx)
- [docs/phoenix/self-hosting/architecture.mdx](docs/phoenix/self-hosting/architecture.mdx)
- [docs/phoenix/self-hosting/features/management.mdx](docs/phoenix/self-hosting/features/management.mdx)
- [docs/phoenix/self-hosting/security/privacy.mdx](docs/phoenix/self-hosting/security/privacy.mdx)
- [docs/phoenix/settings/access-control-rbac.mdx](docs/phoenix/settings/access-control-rbac.mdx)
- [docs/phoenix/settings/data-retention.mdx](docs/phoenix/settings/data-retention.mdx)
- [docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/importing-existing-traces.mdx](docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/importing-existing-traces.mdx)
- [docs/phoenix/tracing/llm-traces/metrics.mdx](docs/phoenix/tracing/llm-traces/metrics.mdx)
- [docs/phoenix/tracing/llm-traces/projects.mdx](docs/phoenix/tracing/llm-traces/projects.mdx)
- [docs/phoenix/user-guide.mdx](docs/phoenix/user-guide.mdx)

</details>



This document provides a high-level overview of Phoenix's major feature areas and how they integrate across client libraries, server components, and the user interface. Phoenix's functionality is organized into primary feature systems that work together to provide comprehensive AI observability, evaluation, and experimentation capabilities.

For detailed information about each system:
- Tracing and instrumentation setup: see [Tracing & Observability](#5.1)
- Evaluation framework implementation: see [Evaluation Framework](#5.2)
- Dataset and experiment management: see [Datasets & Experiments](#5.3)
- Prompt versioning and templating: see [Prompt Management](#5.4)
- LLM Playground and provider abstraction: see [Playground System](#5.5)
- AI Agent Backend: see [AI Agent Backend (PxI)](#5.6)
- Sessions and Annotations: see [Sessions & Annotations](#5.7)

## Feature System Architecture

Phoenix is organized into major feature systems that span the entire stack from client instrumentation to server storage to UI visualization. The following diagram bridges natural language feature spaces to underlying code entities:

Title: Feature System Architecture

```mermaid
graph TB
    subgraph "Feature Systems (Natural Language Space)"
        Tracing["Tracing & Observability"]
        Evals["Evaluation Framework"]
        Datasets["Datasets & Experiments"]
        Prompts["Prompt Management"]
        Playground["Playground System"]
        AIAgent["AI Agent Backend (PxI)"]
        Sessions["Sessions & Annotations"]
    end

    subgraph "Client Entities (Code Space)"
        PyClient["[Client SDK] PhoenixClient"]
        PyOtel["[arize-phoenix-otel] register_phoenix_otel()"]
        PyEvals["[arize-phoenix-evals] Evaluator"]
    end

    subgraph "Server Entities (Code Space)"
        FastAPIApp["[src/phoenix/server/app.py] create_app()"]
        GraphQLAPI["[src/phoenix/server/api/schema.py] build_graphql_schema()"]
        RESTAPI["[src/phoenix/server/api/routers/v1/__init__.py] v1_router"]
        DBModels["[src/phoenix/db/models.py] SQLAlchemy Models"]
        AgentRouter["[src/phoenix/server/api/routers/agents.py] create_agents_router()"]
    end

    Tracing --> PyOtel
    Evals --> PyEvals
    Datasets --> PyClient
    Prompts --> PyClient
    Playground --> PyClient
    AIAgent --> AgentRouter
    Sessions --> PyClient

    PyClient --> GraphQLAPI
    PyClient --> RESTAPI
    AgentRouter --> DBModels
    GraphQLAPI --> DBModels
    RESTAPI --> DBModels
```

Sources:  
[src/phoenix/server/app.py:97-115](),  
[src/phoenix/server/api/queries.py:118-119](),  
[src/phoenix/db/models.py:1-100](),  
[pyproject.toml:2-3](),  
[packages/phoenix-evals/pyproject.toml:2-3]()

## Core Feature Overviews

### Tracing & Observability

Phoenix provides an OpenTelemetry-native tracing backend that ingests spans via the OTLP protocol over gRPC and HTTP. It organizes spans into traces, which are grouped by projects representing different environments or applications. The tracing system supports complex AI architectures—such as Retrieval-Augmented Generation (RAG) pipelines and multi-agent workflows—by capturing detailed span attributes including inputs, outputs, intermediate steps, and metadata.

Span types are categorized using the `SpanKind` enum with values like `CHAIN`, `LLM`, `TOOL`, and `AGENT`, facilitating precise instrumentation and analysis of different stages in an AI pipeline. Status codes of spans are mapped via the `SpanStatusCode` enum to represent success, error, or unset statuses.

For details, see [Tracing & Observability](#5.1).

Sources:  
[src/phoenix/server/app.py:145-145]()

### Evaluation Framework

The evaluation system supports running automated assessments on traces and datasets using multiple evaluator types, including LLM-based, code-based, and heuristic evaluators. Evaluators transform span and trace data into evaluation inputs via input mapping functions and use templates to generate evaluation prompts.

Evaluation results are stored as annotations associated with spans, traces, or sessions, allowing rich feedback and metric computation (e.g., hallucination detection, toxicity scoring, faithfulness checks). Phoenix provides prebuilt classification evaluator configurations under prompt templates for standardized criteria.

For details, see [Evaluation Framework](#5.2).

Sources:  
[src/phoenix/server/api/queries.py:38-43](),  
[packages/phoenix-evals/CHANGELOG.md:22-23](),  
[packages/phoenix-evals/CHANGELOG.md:14-15]()

### Datasets & Experiments

Phoenix supports version-controlled datasets comprising `DatasetExample` entities. These datasets can be split into training/testing subsets with labeling support to facilitate systematic experimentation.

The experimentation framework runs defined tasks—such as prompt versions or evaluators—against dataset examples, recording results as `ExperimentRun` entities. Experiment lifecycle management, including execution and pruning of obsolete experiments, is handled by background daemons like `ExperimentRunner` and `ExperimentSweeper`.

For details, see [Datasets & Experiments](#5.3).

Sources:  
[src/phoenix/server/app.py:123-123](),  
[src/phoenix/server/api/dataloaders/__init__.py:20-20]()

### Prompt Management

Prompt management provides centralized versioning, templating, and tagging for prompt assets. The prompt system treats prompts as first-class entities with multiple versions defined via `PromptVersion`. Prompts include rich templates such as `PromptChatTemplate` supporting complex conversation structures, tool calls, and variable placeholders.

Prompts can be linked to evaluators and experiments for repeatable testing, and SDK helpers in the client libraries simplify prompt application at runtime.

For details, see [Prompt Management](#5.4).

Sources:  
[src/phoenix/server/api/queries.py:121-134]()

### Playground System

The Playground is an interactive environment for developers to test prompt variations and model responses in real-time. It abstracts multiple LLM providers including OpenAI, Anthropic, Google, and AWS Bedrock via a unified interface `PlaygroundStreamingClient` that supports streaming token-by-token responses over GraphQL subscriptions.

The Playground manages rate limiting, provider initialization, and exposes a registry for custom provider integrations, such as `AWSBedrockCustomProviderConfig`.

For details, see [Playground System](#5.5).

Sources:  
[src/phoenix/server/api/queries.py:159-160]()

### AI Agent Backend (PxI)

Phoenix Intelligence (PxI) is the server-side AI agent backend enabling intelligent automation, conversational flows, and tool orchestration. It includes an agent factory based on `pydantic-ai` for creating agents with selected language models and registered tools.

Context resolution facilitates retrieving relevant knowledge and session context for agent decisions. The system exposes `/agents` REST endpoints for agent interactions and introspection, along with evaluation harnesses in `evals/pxi/` and `evals/harbor/`.

For details, see [AI Agent Backend (PxI)](#5.6).

Sources:  
[src/phoenix/config.py:97-102](),  
[pyproject.toml:66-66](),  
[src/phoenix/server/app.py:100-100]()

### Sessions & Annotations

Sessions group related traces into multi-turn conversational contexts as `ProjectSession` objects, providing structured views into conversation history and AI interactions.

Annotations provide a flexible mechanism to attach metadata, feedback, labels, and evaluation results at the level of spans, traces, or sessions. Annotation configurations define schemas for annotation types and usage contexts, and the session filter DSL enables filtering sessions by annotation attributes.

For details, see [Sessions & Annotations](#5.7).

Sources:  
[src/phoenix/server/api/dataloaders/__init__.py:79-79]()

## Data Model Integration

The feature systems are unified by a shared database schema managed with SQLAlchemy ORM models. The following table shows key domain entities per feature system and their approximate database tables:

| Feature Area | Primary Code Entities | Database Table (Approximate) |
|---|---|---|
| **Tracing** | `Span`, `Trace`, `Project` | `spans`, `traces`, `projects` |
| **Evaluations** | `Annotation`, `Evaluator` | `span_annotations`, `trace_annotations`, `evaluators` |
| **Experiments** | `Dataset`, `Experiment`, `ExperimentRun` | `datasets`, `experiments`, `experiment_runs` |
| **Prompts** | `Prompt`, `PromptVersion` | `prompts`, `prompt_versions` |
| **Sessions** | `ProjectSession` | `project_sessions` |

Sources:  
[src/phoenix/db/models.py:1-100](),  
[src/phoenix/server/api/queries.py:72-145]()

## Cross-System Data Flow Example

The following sequence diagram bridges natural language runtime concepts to specific code entities across client, server, and database layers:

Title: Cross-System Data Flow

```mermaid
sequenceDiagram
    participant User as "User (Client/UI)"
    participant Sub as "GraphQL Subscription Resolver<br/>[src/phoenix/server/api/queries.py]"
    participant PGC as "PlaygroundStreamingClient<br/>[src/phoenix/server/api/helpers/playground_registry.py]"
    participant Tracer as "Tracer Component<br/>[src/phoenix/tracers.py]"
    participant DB as "Database Layer<br/>[src/phoenix/db/models.py]"

    User->>Sub: "Subscribe to chatCompletion"
    Sub->>PGC: "chat_completion_create()"
    PGC-->>Sub: "AsyncIterator[ChatCompletionChunk]"
    Sub-->>User: "Streamed Text and Tool Chunks"
    Sub->>Tracer: "Record trace spans"
    Sub->>DB: "Insert spans and traces"
```

Sources:  
[src/phoenix/server/api/queries.py:159-160](),  
[src/phoenix/server/api/queries.py:115-115](),  
[src/phoenix/tracers.py:1-1](),  
[src/phoenix/db/models.py:1-100]()

## Common Infrastructure Features

### Cost Tracking

Phoenix estimates token usage and cost metrics for generative model spans via the `SpanCostCalculator` daemon, which runs asynchronously to process spans in batches. It relies on the `GenerativeModelStore` daemon to maintain the cost and pricing information of supported LLM models.

Token usage and cost information is stored in related span cost tables and summarized per project, session, or experiment.

Sources:  
[src/phoenix/server/app.py:126-127]()

### Authentication & Authorization

A unified authentication mechanism protects all feature systems. The `BearerTokenAuthBackend` middleware enforces token-based access control for API requests. Role-based permissions like `IsAdmin` guard sensitive operations across API layers.

Sources:  
[src/phoenix/server/app.py:116-117](),  
[src/phoenix/server/api/context.py:108-109](),  
[src/phoenix/server/api/queries.py:36-36]()

### DML Events and Real-Time Updates

Phoenix employs a `DmlEventHandler` to broadcast database insert, update, and delete events throughout the system. This event-driven mechanism enables real-time UI updates via GraphQL subscriptions, ensuring that client UIs reflect the latest state of traces, annotations, and experiments seamlessly.

Sources:  
[src/phoenix/server/app.py:129-129]()

---

# Page: Tracing & Observability

# Tracing & Observability

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-tracing/references/fundamentals-required-attributes.md](.agents/skills/phoenix-tracing/references/fundamentals-required-attributes.md)
- [.agents/skills/phoenix-tracing/references/instrumentation-manual-python.md](.agents/skills/phoenix-tracing/references/instrumentation-manual-python.md)
- [.agents/skills/phoenix-tracing/references/instrumentation-manual-typescript.md](.agents/skills/phoenix-tracing/references/instrumentation-manual-typescript.md)
- [docs/phoenix/integrations/llm-providers/openai/openai-node-js-sdk.mdx](docs/phoenix/integrations/llm-providers/openai/openai-node-js-sdk.mdx)
- [docs/phoenix/integrations/llm-providers/openai/openai-tracing.mdx](docs/phoenix/integrations/llm-providers/openai/openai-tracing.mdx)
- [docs/phoenix/integrations/llm-providers/typesafe.mdx](docs/phoenix/integrations/llm-providers/typesafe.mdx)
- [docs/phoenix/integrations/llm-providers/typesafe/typesafe-python.mdx](docs/phoenix/integrations/llm-providers/typesafe/typesafe-python.mdx)
- [docs/phoenix/integrations/llm-providers/typesafe/typesafe-typescript.mdx](docs/phoenix/integrations/llm-providers/typesafe/typesafe-typescript.mdx)
- [docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx](docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx)
- [docs/phoenix/tracing/concepts-tracing/otel-openinference/semantic-conventions.mdx](docs/phoenix/tracing/concepts-tracing/otel-openinference/semantic-conventions.mdx)
- [docs/phoenix/tracing/concepts-tracing/otel-openinference/span-kinds.mdx](docs/phoenix/tracing/concepts-tracing/otel-openinference/span-kinds.mdx)
- [internal_docs/specs/span-filter-dsl.md](internal_docs/specs/span-filter-dsl.md)
- [js/app/src/agent/uiOperations/operations/spansFilter.ts](js/app/src/agent/uiOperations/operations/spansFilter.ts)
- [js/app/src/pages/project/traceFilterDSL.ts](js/app/src/pages/project/traceFilterDSL.ts)
- [js/examples/apps/ai-sdk-agent/README.md](js/examples/apps/ai-sdk-agent/README.md)
- [js/examples/apps/ai-sdk-agent/instrumentation.ts](js/examples/apps/ai-sdk-agent/instrumentation.ts)
- [src/phoenix/exceptions.py](src/phoenix/exceptions.py)
- [src/phoenix/server/api/helpers/experiment_run_filters.py](src/phoenix/server/api/helpers/experiment_run_filters.py)
- [src/phoenix/server/api/input_types/SpanSort.py](src/phoenix/server/api/input_types/SpanSort.py)
- [src/phoenix/trace/dsl/filter.py](src/phoenix/trace/dsl/filter.py)
- [src/phoenix/trace/dsl/query.py](src/phoenix/trace/dsl/query.py)
- [src/phoenix/trace/gen_ai/conversion.py](src/phoenix/trace/gen_ai/conversion.py)
- [src/phoenix/trace/otel.py](src/phoenix/trace/otel.py)
- [src/phoenix/trace/span_evaluations.py](src/phoenix/trace/span_evaluations.py)
- [src/phoenix/trace/trace_dataset.py](src/phoenix/trace/trace_dataset.py)
- [tests/unit/server/api/helpers/test_experiment_run_filters.py](tests/unit/server/api/helpers/test_experiment_run_filters.py)
- [tests/unit/server/api/types/test_Trace_span_aggregates.py](tests/unit/server/api/types/test_Trace_span_aggregates.py)
- [tests/unit/trace/dsl/test_filter.py](tests/unit/trace/dsl/test_filter.py)
- [tests/unit/trace/dsl/test_filter_error_messages.py](tests/unit/trace/dsl/test_filter_error_messages.py)
- [tests/unit/trace/dsl/test_filter_span_cost.py](tests/unit/trace/dsl/test_filter_span_cost.py)
- [tests/unit/trace/dsl/test_filter_spec_conformance.py](tests/unit/trace/dsl/test_filter_spec_conformance.py)
- [tests/unit/trace/dsl/test_query.py](tests/unit/trace/dsl/test_query.py)
- [tests/unit/trace/dsl/test_session_filter.py](tests/unit/trace/dsl/test_session_filter.py)
- [tests/unit/trace/gen_ai/test_conversion.py](tests/unit/trace/gen_ai/test_conversion.py)
- [tests/unit/trace/test_otel.py](tests/unit/trace/test_otel.py)
- [tests/unit/trace/test_span_evaluations.py](tests/unit/trace/test_span_evaluations.py)
- [tests/unit/trace/test_trace_dataset.py](tests/unit/trace/test_trace_dataset.py)

</details>



## Purpose and Scope

This document explains the tracing and observability architecture within Phoenix. It covers how Phoenix integrates OpenTelemetry (OTel) for instrumenting AI applications, the OTLP span ingestion pipeline, trace storage models, OpenInference semantic conventions, span kinds, the `TraceDataset` abstraction, and the custom Python AST-based domain-specific language (DSL) filter system.

Sources: `[src/phoenix/trace/otel.py:97-134]`, `[src/phoenix/trace/dsl/filter.py:1-126]`, `[src/phoenix/trace/trace_dataset.py:101-166]()`

---

## Architecture Overview

Phoenix adopts OpenTelemetry (OTel) standards and the OTLP protocol over HTTP and gRPC to collect distributed trace data from instrumented AI applications. The ingestion pipeline buffers and batch-inserts spans into relational databases via SQLAlchemy ORM models, while triggering asynchronous cost calculation and event emission.

```mermaid
graph TB
    subgraph "Application Layer"
        App["InstrumentedApplication"]
        PYOTEL["arize-phoenix-otel<br>(src/phoenix/trace/otel.py)"]
        TSOTEL["@arizeai/phoenix-otel"]
        OpenInf["openinference-instrumentation-*"]
    end

    subgraph "Phoenix Server"
        HTTPCollector["HTTPEndpoint<br>:6006/v1/traces"]
        GRPCCollector["GRPCEndpoint<br>:4317"]
        SpanQueue["SpanQueue<br>(_enqueue_span)"]
        BulkInserter["BulkInserter<br>(phoenix.db.bulk_inserter)"]
        EventQueue["EventQueue<br>(DmlEvent)"]
        CostCalc["SpanCostCalculator<br>(phoenix.server.daemons.span_cost_calculator.py)"]
    end

    subgraph "Storage"
        DB["Database<br>(SQLAlchemy ORM)"]
        SpansTable["models.Span<br>(src/phoenix/db/models.py)"]
        TracesTable["models.Trace"]
        ProjectsTable["models.Project"]
    end

    App -->|"uses"| PYOTEL
    App -->|"uses"| TSOTEL
    App -->|"uses"| OpenInf

    PYOTEL -->|"OTLP/HTTP"| HTTPCollector
    PYOTEL -->|"OTLP/gRPC"| GRPCCollector
    TSOTEL -->|"OTLP/HTTP"| HTTPCollector
    TSOTEL -->|"OTLP/gRPC"| GRPCCollector
    OpenInf -->|"OTLP"| HTTPCollector
    OpenInf -->|"OTLP"| GRPCCollector

    HTTPCollector --> SpanQueue
    GRPCCollector --> SpanQueue

    SpanQueue -->|"_enqueue_span()"| BulkInserter

    BulkInserter -->|"insert_span()"| DB
    DB --> SpansTable
    DB --> TracesTable
    DB --> ProjectsTable

    BulkInserter -->|"Emit DmlEvent"| EventQueue
    EventQueue --> CostCalc
    CostCalc --> DB
```
**Diagram: Phoenix Tracing Architecture (Natural Language to Code Entity Space)**

Sources: `[src/phoenix/db/bulk_inserter.py:51-175]()`, `[src/phoenix/trace/otel.py:97-134]()`

---

## Phoenix OTEL Packages and Span Ingestion

Phoenix provides native OpenTelemetry integration packages (`arize-phoenix-otel` in Python and `@arizeai/phoenix-otel` in TypeScript) to simplify configuration and trace exporting.

### Python OTLP Decoding (`src/phoenix/trace/otel.py`)
Incoming OTLP protocol buffers are decoded into Phoenix `Span` domain objects. The function `decode_otlp_span` extracts identifiers, timestamps, attributes, events, and status codes:

- **Identifiers:** Hexadecimal encoding is decoded for trace IDs and span IDs (`_decode_identifier`) `[src/phoenix/trace/otel.py:137-142]()`.
- **Attributes:** Key-value pairs are coerced and unflattened (`decode_otlp_span`, `_merge_synthesized_attributes`) `[src/phoenix/trace/otel.py:97-134]()`.
- **GenAI Conversions:** OpenTelemetry GenAI semantic conventions (`gen_ai.*`) are automatically converted back into OpenInference attributes via `get_openinference_attributes` `[src/phoenix/trace/gen_ai/conversion.py:58-82]()`.

Sources: `[src/phoenix/trace/otel.py:59-134]()`, `[src/phoenix/trace/gen_ai/conversion.py:58-82]()`

---

## Data Model & Trace Representation

Phoenix models spans, traces, and datasets using SQLAlchemy ORM models and pandas dataframes.

### Core Schemas (`phoenix.trace.schemas`)
- `Span`: Represents a single unit of execution containing:
  - `name`, `context` (`SpanContext` with `trace_id` and `span_id`), `span_kind`, `parent_id`, `start_time`, `end_time` `[src/phoenix/trace/schemas.py:134-145]()`.
  - `status_code`, `status_message` `[src/phoenix/trace/schemas.py:146-147]()`.
  - `attributes` (nested dictionary conforming to OpenInference conventions) `[src/phoenix/trace/schemas.py:148-162]()`.
  - `events`: List of `SpanEvent` or `SpanException` items `[src/phoenix/trace/schemas.py:163-172]()`.

### TraceDataset (`phoenix.trace.trace_dataset`)
`TraceDataset` wraps a pandas DataFrame containing flattened representations of spans for bulk processing, evaluations, and visualization:
- Validates required columns (`REQUIRED_COLUMNS` including `name`, `span_kind`, `parent_id`, `start_time`, `end_time`, `context.span_id`, `context.trace_id`) `[src/phoenix/trace/trace_dataset.py:34-44]()`.
- Normalizes timestamps via `normalize_timestamps` and handles serialization conversions via `get_serializable_spans_dataframe` `[src/phoenix/trace/trace_dataset.py:59-98]()`.

Sources: `[src/phoenix/trace/schemas.py:134-172]()`, `[src/phoenix/trace/trace_dataset.py:34-166]()`

---

## OpenInference Semantic Conventions & Span Kinds

OpenInference extends OpenTelemetry semantic conventions with AI-specific attributes and span kinds.

### The Twelve Span Kinds
Span kinds drive UI icons and expected attribute sets (`docs/phoenix/tracing/concepts-tracing/otel-openinference/span-kinds.mdx`):
- **`LLM`**: Calls to large language models.
- **`CHAIN`**: Orchestration workflows or component links.
- **`AGENT`**: Multi-step reasoning loops encompassing LLMs and tools.
- **`TOOL`**: External function or API calls.
- **`RETRIEVER`**: Vector store or document database queries.
- **`EMBEDDING`**: Text-to-vector encodings.
- **`RERANKER`**: Relevance-based document re-ordering.
- **`GUARDRAIL`**: Input/output policy validations.
- **`EVALUATOR`**: Evaluation execution.
- **`DECISION`**: Decision model routing and classification calls.
- **`PROMPT`**: Prompt templating and construction.
- **`UNKNOWN`**: Fallback kind.

Sources: `[docs/phoenix/tracing/concepts-tracing/otel-openinference/span-kinds.mdx:32-50]()`

---

## Filtering System Using Custom DSL

Phoenix provides a domain-specific language (DSL) for filtering spans, traces, and sessions. Implemented in Python AST (`src/phoenix/trace/dsl/filter.py`), the DSL translates Python-like filter expressions into SQLAlchemy query criteria.

```mermaid
graph LR
    FilterExpr["AST Filter Expression<br>(e.g. 'latency_ms > 1000 and span_kind == \"LLM\"')"]
    SpanFilter["SpanFilter<br>(src/phoenix/trace/dsl/filter.py)"]
    SQLExpr["SQLAlchemy Column Element<br>(sqlalchemy.sql.expression.ColumnElement)"]
    Query["Database Query<br>(sqlalchemy.orm.Session / Select)"]
    ResultSet["Filtered Results"]

    FilterExpr --> SpanFilter
    SpanFilter --> SQLExpr
    SQLExpr --> Query
    Query --> ResultSet
```
**Diagram: Span Filtering DSL Flow (Natural Language to Code Entity Space)**

### Implementation Details (`src/phoenix/trace/dsl/filter.py`)
- **AST Parsing:** Filter strings are parsed using Python's `ast` module, validating operations (comparisons, logical operators, membership, and null checks) `[tests/unit/trace/dsl/test_filter.py:28-158]()`.
- **Column Mappings:** Reserved identifiers like `span_kind`, `latency_ms`, `start_time`, `status_code`, and `parent_id` map directly to `models.Span` columns (`_STRING_NAMES`, `_FLOAT_NAMES`, `_DATETIME_NAMES`) `[src/phoenix/trace/dsl/filter.py:114-140]`.
- **JSON Casting & Attributes:** Unstructured attributes and metadata are accessed dynamically and safely cast using helpers like `SafeJsonFloat` and `SafeJsonBoolean` `[src/phoenix/trace/dsl/filter.py:19-20]`.
- **Aliasing:** Backward-compatibility mappings translate deprecated paths (e.g., `context.span_id` $\to$ `span_id`) `[src/phoenix/trace/dsl/filter.py:150-159]`.

Sources: `[src/phoenix/trace/dsl/filter.py:1-164]`, `[tests/unit/trace/dsl/test_filter.py:28-158]()`

---

## Observability Features and UI Components

Phoenix exposes tracing and observability data through rich React UI components and GraphQL/REST APIs:
- **Trace Tree & Span Details:** The `TraceTree` component reconstructs parent-child execution hierarchies using `parent_id` properties `[app/src/components/trace/TraceTree.tsx]`. `SpanDetails` and `TraceDetails` display inputs, outputs, token counts, and latency metrics.
- **Annotations & Evaluations:** `SpanAnnotationsEditor` enables viewing and editing annotations (scores, labels, explanations) across spans and traces `[app/src/components/trace/SpanAnnotationsEditor.tsx]`.
- **Sorting & Metrics:** Table views support sorting by latency, token counts, evaluation scores, and total cost (`SpanColumn` in `[src/phoenix/server/api/input_types/SpanSort.py:18-31]()`).

Sources: `[src/phoenix/server/api/input_types/SpanSort.py:18-31]()`

---

# Page: Evaluation Framework

# Evaluation Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-evals/SKILL.md](.agents/skills/phoenix-evals/SKILL.md)
- [.agents/skills/phoenix-evals/references/common-mistakes-python.md](.agents/skills/phoenix-evals/references/common-mistakes-python.md)
- [.agents/skills/phoenix-evals/references/evaluators-llm-python.md](.agents/skills/phoenix-evals/references/evaluators-llm-python.md)
- [.agents/skills/phoenix-evals/references/evaluators-pre-built.md](.agents/skills/phoenix-evals/references/evaluators-pre-built.md)
- [.agents/skills/phoenix-evals/references/evaluators-rag.md](.agents/skills/phoenix-evals/references/evaluators-rag.md)
- [.agents/skills/phoenix-evals/references/fundamentals-anti-patterns.md](.agents/skills/phoenix-evals/references/fundamentals-anti-patterns.md)
- [.agents/skills/phoenix-evals/references/observe-tracing-setup.md](.agents/skills/phoenix-evals/references/observe-tracing-setup.md)
- [.agents/skills/phoenix-evals/references/validation-evaluators-python.md](.agents/skills/phoenix-evals/references/validation-evaluators-python.md)
- [.agents/skills/phoenix-evals/references/validation-evaluators-typescript.md](.agents/skills/phoenix-evals/references/validation-evaluators-typescript.md)
- [.agents/skills/phoenix-evals/references/validation.md](.agents/skills/phoenix-evals/references/validation.md)
- [docs/phoenix/evaluation/pre-built-metrics.mdx](docs/phoenix/evaluation/pre-built-metrics.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-evals/classification.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-evals/classification.mdx)
- [js/packages/phoenix-evals/examples/decision_model_example.ts](js/packages/phoenix-evals/examples/decision_model_example.ts)
- [js/packages/phoenix-evals/src/__generated__/default_templates/index.ts](js/packages/phoenix-evals/src/__generated__/default_templates/index.ts)
- [js/packages/phoenix-evals/src/decision/decideClassification.ts](js/packages/phoenix-evals/src/decision/decideClassification.ts)
- [js/packages/phoenix-evals/src/decision/decisionPrompt.ts](js/packages/phoenix-evals/src/decision/decisionPrompt.ts)
- [js/packages/phoenix-evals/src/llm/ClassificationEvaluator.ts](js/packages/phoenix-evals/src/llm/ClassificationEvaluator.ts)
- [js/packages/phoenix-evals/src/llm/generateClassification.ts](js/packages/phoenix-evals/src/llm/generateClassification.ts)
- [js/packages/phoenix-evals/src/llm/index.ts](js/packages/phoenix-evals/src/llm/index.ts)
- [js/packages/phoenix-evals/src/telemetry/index.ts](js/packages/phoenix-evals/src/telemetry/index.ts)
- [js/packages/phoenix-evals/src/types/evals.ts](js/packages/phoenix-evals/src/types/evals.ts)
- [js/packages/phoenix-evals/src/utils/index.ts](js/packages/phoenix-evals/src/utils/index.ts)
- [js/packages/phoenix-evals/test/llm/generateClassificationTelemetry.test.ts](js/packages/phoenix-evals/test/llm/generateClassificationTelemetry.test.ts)
- [packages/phoenix-evals/src/phoenix/evals/__generated__/classification_evaluator_configs/__init__.py](packages/phoenix-evals/src/phoenix/evals/__generated__/classification_evaluator_configs/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py](packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py)
- [packages/phoenix-evals/tests/phoenix/evals/metrics/test_classification_evaluators.py](packages/phoenix-evals/tests/phoenix/evals/metrics/test_classification_evaluators.py)
- [src/phoenix/__generated__/classification_evaluator_configs/__init__.py](src/phoenix/__generated__/classification_evaluator_configs/__init__.py)
- [src/phoenix/db/migrations/versions/02463bd83119_add_evaluators.py](src/phoenix/db/migrations/versions/02463bd83119_add_evaluators.py)
- [src/phoenix/server/api/mutations/evaluator_mutations.py](src/phoenix/server/api/mutations/evaluator_mutations.py)
- [src/phoenix/server/api/schema.py](src/phoenix/server/api/schema.py)
- [src/phoenix/server/api/types/Dataset.py](src/phoenix/server/api/types/Dataset.py)
- [src/phoenix/server/api/types/Evaluator.py](src/phoenix/server/api/types/Evaluator.py)
- [tests/unit/db/test_models.py](tests/unit/db/test_models.py)
- [tests/unit/server/api/mutations/test_evaluator_mutations.py](tests/unit/server/api/mutations/test_evaluator_mutations.py)
- [tests/unit/server/api/types/test_Dataset.py](tests/unit/server/api/types/test_Dataset.py)
- [tests/unit/server/api/types/test_Evaluator.py](tests/unit/server/api/types/test_Evaluator.py)

</details>



## Purpose and Scope

The Evaluation Framework provides a comprehensive system to define, execute, and manage automated evaluators that assess the performance and behavior of LLM applications and code executions within Phoenix. It supports diverse evaluator types including:

- **LLM Evaluators**: Prompt-based evaluations leveraging generative language models from providers such as OpenAI, Anthropic, Google, Bedrock, and others (`src/phoenix/server/api/types/Evaluator.py:51-52`) [src/phoenix/server/api/types/Evaluator.py:51-52]().
- **Code Evaluators**: Execution of custom Python or TypeScript code within secure sandboxed environments for deterministic or programmatic evaluation metrics (`src/phoenix/server/api/types/Evaluator.py:53-53`) [src/phoenix/server/api/types/Evaluator.py:53-53]().
- **Built-in Evaluators**: Predefined standard evaluators implementing common metrics like hallucination detection, toxicity scoring, faithfulness, and more (`src/phoenix/server/api/types/Evaluator.py:54-54`) [src/phoenix/server/api/types/Evaluator.py:54-54]().
- **Flexible Input Mapping**: JSONPath-based and literal input mapping encapsulated by `EvaluatorInputMapping` allowing evaluation variables to be extracted or transformed from rich inputs including OpenTelemetry spans, traces, and dataset examples (`src/phoenix/server/api/types/Evaluator.py:58-63`) [src/phoenix/server/api/types/Evaluator.py:58-63]().

This evaluation framework underpins key Phoenix features including the Playground interactive interface, experiment execution, annotation management, and AI agent evaluation pipelines.

**Sources:**  
[src/phoenix/server/api/types/Evaluator.py:50-63]()

---

## Architecture Overview

The evaluation framework integrates closely with Phoenix's GraphQL API server and internal evaluator implementations. Evaluations are invoked primarily via GraphQL mutations and processed through concrete evaluator classes that produce scores or annotations persisted in the database.

### Evaluation Framework Architecture Diagram

```mermaid
graph TD
    subgraph "GraphQL API Layer"
        Mutations["phoenix.server.api.mutations.evaluator_mutations"]
        PreviewMutation["phoenix.server.api.mutations.chat_mutations"]
    end

    subgraph "Evaluator Classes (Python)"
        BaseEvaluator["phoenix.server.api.types.Evaluator.Evaluator"]
        CodeEvaluatorVersion["phoenix.server.api.types.Evaluator.CodeEvaluatorVersion"]
    end

    subgraph "Evaluators Data Models (DB & GraphQL Types)"
        InputMapping["phoenix.server.api.types.Evaluator.EvaluatorInputMapping"]
        EvaluatorKind["phoenix.server.api.types.Evaluator.EvaluatorKind"]
        OutputConfig["phoenix.db.types.annotation_configs.OutputConfigType"]
        SandboxConfig["phoenix.server.api.types.SandboxConfig.SandboxConfig"]
    end

    PreviewMutation --> Mutations
    Mutations --> |"evaluator_mutations.py"| EvaluatorKind
    Mutations --> |"resolve_mappings"| InputMapping
    Mutations --> |"validate_code_evaluator_sandbox_config"| SandboxConfig
    CodeEvaluatorVersion --> |"inference & versioning"| BaseEvaluator
    LLMEvaluator --> |"uses"| OutputConfig
```

This diagram connects the GraphQL API mutations with evaluator implementations and their associated data structures such as input mappings, annotations, and sandbox configuration for code execution.

**Sources:**  
[src/phoenix/server/api/mutations/evaluator_mutations.py:18-72](), [src/phoenix/server/api/types/Evaluator.py:50-102]()

---

## Evaluator Implementations

Phoenix implements three primary kinds of evaluators extending a shared abstract base class (`src/phoenix/server/api/types/Evaluator.py:71-73`) [src/phoenix/server/api/types/Evaluator.py:71-73]():

### LLMEvaluator

- Represents prompt-driven evaluators that interact with LLM APIs (`src/phoenix/server/api/types/Evaluator.py:52-52`) [src/phoenix/server/api/types/Evaluator.py:52-52]().
- Holds references to prompt versions and related invocation parameters (`tests/unit/server/api/types/test_Evaluator.py:31-46`) [tests/unit/server/api/types/test_Evaluator.py:31-46]().
- Validates prompt and output config consistency during creation/update (`src/phoenix/server/api/helpers/evaluators.py:41-42`) [src/phoenix/server/api/helpers/evaluators.py:41-42]().
- Executes evaluations by sending prompts, receiving responses, and parsing outputs into typed scores or annotations.

### CodeEvaluator

- Executes evaluation logic written in Python or TypeScript (`src/phoenix/server/api/types/Evaluator.py:53-53`) [src/phoenix/server/api/types/Evaluator.py:53-53]().
- Source code included with each evaluator version (`src/phoenix/server/api/types/Evaluator.py:132-132`) [src/phoenix/server/api/types/Evaluator.py:132-132]().
- Supports input schema inference via `_infer_code_evaluator_input_schema()` to validate inputs conformant with function signatures (`src/phoenix/server/api/types/Evaluator.py:137-145`) [src/phoenix/server/api/types/Evaluator.py:137-145]().
- Runs code securely within sandboxed environments validated by `_validate_code_evaluator_sandbox_config()` (`src/phoenix/server/api/mutations/evaluator_mutations.py:131-139`) [src/phoenix/server/api/mutations/evaluator_mutations.py:131-139]().
- Robust validation to ensure sandbox and evaluator language alignment (`src/phoenix/server/api/mutations/evaluator_mutations.py:172-172`) [src/phoenix/server/api/mutations/evaluator_mutations.py:172-172]().

### BuiltInEvaluator

- Wraps predefined evaluators implementing standard metrics (`src/phoenix/server/api/types/Evaluator.py:54-54`) [src/phoenix/server/api/types/Evaluator.py:54-54]().
- Accessed via key lookups internally.
- Provides evaluation functions embedded in Phoenix for common use cases.

**Sources:**  
[src/phoenix/server/api/types/Evaluator.py:50-145](), [src/phoenix/server/api/mutations/evaluator_mutations.py:131-172]()

---

## Input Mapping and Context Resolution

Evaluations require transforming rich context data into the input schema expected by the evaluator. Phoenix supports flexible input mappings encapsulated in the `EvaluatorInputMapping` type (`src/phoenix/server/api/types/Evaluator.py:58-62`) [src/phoenix/server/api/types/Evaluator.py:58-62]().

### GraphQL Input Mapping Schema

```python
@strawberry.type
class EvaluatorInputMapping:
    literal_mapping: JSON  # direct key-value mappings to evaluator inputs
    path_mapping: JSON     # JSONPath expressions to extract dynamic values from context
```

- **Literal Mapping:** Static values directly assigned to evaluator input keys (`src/phoenix/server/api/types/Evaluator.py:59-60`) [src/phoenix/server/api/types/Evaluator.py:59-60]().
- **Path Mapping:** JSONPath expressions evaluated on the context to dynamically select or compute input variables (`src/phoenix/server/api/types/Evaluator.py:61-62`) [src/phoenix/server/api/types/Evaluator.py:61-62]().

### Input Mapping Data Flow

```mermaid
sequenceDiagram
    participant UI as "EvaluatorOutputPreview UI"
    participant API as "evaluator_mutations.py"
    participant IM as "EvaluatorInputMapping"
    participant Eval as "CodeEvaluator / LLMEvaluator"

    UI->>API: "evaluatorPreviews(inputMapping, evalInputContext)"
    API->>IM: "resolve_mappings(context, inputMapping)"
    IM-->>API: "mapped_input_vars"
    API->>Eval: "evaluate(mapped_input_vars)"
    Eval-->>API: "EvaluationResults (Scores/Annotations)"
    API-->>UI: "PreviewOutputs + Annotations + Errors"
```

This mechanism enables evaluator inputs to be derived from complex inputs like spans, traces, or dataset examples.

**Sources:**  
[src/phoenix/server/api/types/Evaluator.py:58-63]()

---

## Annotation Storage and Output Configuration

Evaluation results are serialized as annotations linked to spans or datasets. Output configurations govern the structure and semantics of the annotations (`src/phoenix/server/api/mutations/evaluator_mutations.py:75-110`) [src/phoenix/server/api/mutations/evaluator_mutations.py:75-110]().

### OutputConfig Types

| Type                     | Description                                | Notable Fields                      |
|--------------------------|--------------------------------------------|-----------------------------------|
| `CategoricalOutputConfig` | Categorical nominal labels (classification) | `name`, `values` (labels with scores), `optimization_direction` (`src/phoenix/server/api/mutations/evaluator_mutations.py:80-88`) [src/phoenix/server/api/mutations/evaluator_mutations.py:80-88]() |
| `ContinuousOutputConfig`  | Numeric scores with defined boundaries     | `name`, `lower_bound`, `upper_bound`, `optimization_direction` (`src/phoenix/server/api/mutations/evaluator_mutations.py:89-98`) [src/phoenix/server/api/mutations/evaluator_mutations.py:89-98]()  |
| `FreeformOutputConfig`    | Free-text or threshold-based outputs       | `name`, `thresholds`, `lower_bound`, `upper_bound` (`src/phoenix/server/api/mutations/evaluator_mutations.py:99-109`) [src/phoenix/server/api/mutations/evaluator_mutations.py:99-109]()              |

### OptimizationDirection Enum

- `MAXIMIZE` - Higher scores are better (`js/packages/phoenix-evals/src/types/evals.ts:148-148`) [js/packages/phoenix-evals/src/types/evals.ts:148-148]().
- `MINIMIZE` - Lower scores are better (`js/packages/phoenix-evals/src/types/evals.ts:148-148`) [js/packages/phoenix-evals/src/types/evals.ts:148-148]().
- `NEUTRAL` - Neutral direction (`js/packages/phoenix-evals/src/types/evals.ts:148-148`) [js/packages/phoenix-evals/src/types/evals.ts:148-148]().

### Annotations

- Stored as `SpanAnnotation` or dataset annotation entities in the database.
- Can represent scalar scores, categorical labels, explanations, and metadata.
- Used to drive experiment result aggregation and span-level insights.

**Sources:**  
[src/phoenix/server/api/mutations/evaluator_mutations.py:75-111](), [js/packages/phoenix-evals/src/types/evals.ts:145-149]()

---

## Built-in Metrics and Pre-built Classification Evaluator Configurations

Phoenix provides a suite of built-in metrics and pre-configured classification evaluators to streamline common evaluation tasks. These are available in both Python and TypeScript client libraries (`.agents/skills/phoenix-evals/references/evaluators-pre-built.md:5-7`) [.agents/skills/phoenix-evals/references/evaluators-pre-built.md:5-7]().

### Python Built-in Metrics

The `phoenix.evals.metrics` module offers a collection of evaluators for various aspects of LLM performance (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:1-17`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:1-17]():

- `CompletenessEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:1-1`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:1-1]()
- `ConcisenessEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:2-2`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:2-2]()
- `CorrectnessEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:3-3`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:3-3]()
- `DocumentRelevanceEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:4-4`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:4-4]()
- `FaithfulnessEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:6-6`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:6-6]()
- `HallucinationEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:7-7`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:7-7]()
- `RefusalEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:11-11`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:11-11]()
- `RetrievalRelevanceEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:12-12`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:12-12]()
- `ToxicityEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:16-16`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:16-16]()
- `UserFrictionEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:17-17`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:17-17]()
- `ToolInvocationEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:13-13`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:13-13]()
- `ToolResponseHandlingEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:14-14`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:14-14]()
- `ToolSelectionEvaluator` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:15-15`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:15-15]()
- `exact_match` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:5-5`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:5-5]()
- `MatchesRegex` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:8-8`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:8-8]()
- `PrecisionRecallFScore` (`packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:10-10`) [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:10-10]()

### TypeScript Built-in Metrics

The TypeScript client library exposes matching evaluators (`js/packages/phoenix-evals/src/llm/index.ts:1-20`) [js/packages/phoenix-evals/src/llm/index.ts:1-19]():

- `ClassificationEvaluator` (`js/packages/phoenix-evals/src/llm/index.ts:1-1`) [js/packages/phoenix-evals/src/llm/index.ts:1-1]()
- `createClassificationEvaluator` (`js/packages/phoenix-evals/src/llm/index.ts:2-2`) [js/packages/phoenix-evals/src/llm/index.ts:2-2]()
- `createClassifierFn` (`js/packages/phoenix-evals/src/llm/index.ts:3-3`) [js/packages/phoenix-evals/src/llm/index.ts:3-3]()
- `createConcisenessEvaluator` (`js/packages/phoenix-evals/src/llm/index.ts:5-5`) [js/packages/phoenix-evals/src/llm/index.ts:5-5]()
- `createCorrectnessEvaluator` (`js/packages/phoenix-evals/src/llm/index.ts:6-6`) [js/packages/phoenix-evals/src/llm/index.ts:6-6]()
- `createDocumentRelevanceEvaluator` (`js/packages/phoenix-evals/src/llm/index.ts:7-7`) [js/packages/phoenix-evals/src/llm/index.ts:7-7]()
- `createFaithfulnessEvaluator` (`js/packages/phoenix-evals/src/llm/index.ts:8-8`) [js/packages/phoenix-evals/src/llm/index.ts:8-8]()
- `createHallucinationEvaluator` (`js/packages/phoenix-evals/src/llm/index.ts:9-9`) [js/packages/phoenix-evals/src/llm/index.ts:9-9]()
- `createRefusalEvaluator` (`js/packages/phoenix-evals/src/llm/index.ts:11-11`) [js/packages/phoenix-evals/src/llm/index.ts:11-11]()
- `createRetrievalRelevanceEvaluator` (`js/packages/phoenix-evals/src/llm/index.ts:12-12`) [js/packages/phoenix-evals/src/llm/index.ts:12-12]()
- `createToxicityEvaluator` (`js/packages/phoenix-evals/src/llm/index.ts:16-16`) [js/packages/phoenix-evals/src/llm/index.ts:16-16]()

**Sources:**  
[packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:1-37](), [js/packages/phoenix-evals/src/llm/index.ts:1-19](), [.agents/skills/phoenix-evals/references/evaluators-pre-built.md:5-7]()

---

## Summary Diagrams Bridging Natural Language Evaluation Concepts to Code Entities

### 1. LLM Evaluator Code Entity Mapping

```mermaid
flowchart TD
    NL_LLMEval["Natural Language: LLM Judge Evaluator"] --> Code_LLMEval["phoenix.server.api.types.Evaluator.LLM"]
    Code_LLMEval --> Code_Prompt["phoenix.server.api.types.PromptVersion.PromptVersion"]
    Code_Prompt --> Code_Params["phoenix.db.types.prompts.PromptOpenAIInvocationParameters"]
    Code_LLMEval --> Code_Configs["phoenix.db.types.annotation_configs.OutputConfigType"]
    Code_Configs --> Code_Categorical["CategoricalOutputConfig"]
    Code_Configs --> Code_Continuous["ContinuousOutputConfig"]
```

**Sources:**  
[src/phoenix/server/api/types/Evaluator.py:51-52](), [src/phoenix/server/api/mutations/evaluator_mutations.py:75-111]()

### 2. Code Evaluator Sandbox Validation Flow

```mermaid
flowchart TD
    NL_CodeEval["Natural Language: Code Evaluator Execution"] --> Code_Validate["phoenix.server.api.mutations.evaluator_mutations._validate_code_evaluator_sandbox_config"]
    Code_Validate --> Code_SandboxConfig["phoenix.db.models.SandboxConfig"]
    Code_Validate --> Code_Provider["phoenix.db.models.SandboxProvider"]
    Code_Provider --> Code_Adapter["phoenix.server.sandbox.SANDBOX_ADAPTERS"]
    Code_Adapter --> Code_EvalVersion["phoenix.server.api.types.Evaluator.CodeEvaluatorVersion"]
    Code_EvalVersion --> Code_Infer["_infer_code_evaluator_input_schema"]
```

**Sources:**  
[src/phoenix/server/api/mutations/evaluator_mutations.py:131-172](), [src/phoenix/server/api/types/Evaluator.py:128-145]()

---

# End of Evaluation Framework Documentation

---

# Page: Datasets & Experiments

# Datasets & Experiments

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/phoenix-client/examples/experiments/experiment_trace_evaluator.py](packages/phoenix-client/examples/experiments/experiment_trace_evaluator.py)
- [packages/phoenix-client/src/phoenix/client/experiments/__init__.py](packages/phoenix-client/src/phoenix/client/experiments/__init__.py)
- [packages/phoenix-client/src/phoenix/client/resources/experiments/__init__.py](packages/phoenix-client/src/phoenix/client/resources/experiments/__init__.py)
- [packages/phoenix-client/src/phoenix/client/resources/experiments/evaluators.py](packages/phoenix-client/src/phoenix/client/resources/experiments/evaluators.py)
- [packages/phoenix-client/src/phoenix/client/resources/experiments/types.py](packages/phoenix-client/src/phoenix/client/resources/experiments/types.py)
- [packages/phoenix-client/src/phoenix/client/utils/executors.py](packages/phoenix-client/src/phoenix/client/utils/executors.py)
- [packages/phoenix-client/src/phoenix/client/utils/rate_limiters.py](packages/phoenix-client/src/phoenix/client/utils/rate_limiters.py)
- [packages/phoenix-client/tests/client/resources/experiments/test_example_proxy.py](packages/phoenix-client/tests/client/resources/experiments/test_example_proxy.py)
- [packages/phoenix-client/tests/client/resources/experiments/test_trace_id_binding.py](packages/phoenix-client/tests/client/resources/experiments/test_trace_id_binding.py)
- [packages/phoenix-client/tests/client/utils/test_executors.py](packages/phoenix-client/tests/client/utils/test_executors.py)
- [packages/phoenix-evals/src/phoenix/evals/executors.py](packages/phoenix-evals/src/phoenix/evals/executors.py)
- [packages/phoenix-evals/tests/phoenix/evals/test_executor.py](packages/phoenix-evals/tests/phoenix/evals/test_executor.py)
- [src/phoenix/db/migrations/versions/01a8342c9cdf_add_user_id_on_datasets.py](src/phoenix/db/migrations/versions/01a8342c9cdf_add_user_id_on_datasets.py)
- [src/phoenix/db/migrations/versions/0df286449799_add_session_annotations_table.py](src/phoenix/db/migrations/versions/0df286449799_add_session_annotations_table.py)
- [src/phoenix/db/migrations/versions/58228d933c91_dataset_labels.py](src/phoenix/db/migrations/versions/58228d933c91_dataset_labels.py)
- [src/phoenix/db/migrations/versions/699f655af132_experiment_tags.py](src/phoenix/db/migrations/versions/699f655af132_experiment_tags.py)
- [src/phoenix/db/migrations/versions/ab513d89518b_add_user_id_on_dataset_versions.py](src/phoenix/db/migrations/versions/ab513d89518b_add_user_id_on_dataset_versions.py)
- [src/phoenix/db/migrations/versions/d0690a79ea51_users_on_experiments.py](src/phoenix/db/migrations/versions/d0690a79ea51_users_on_experiments.py)
- [src/phoenix/db/migrations/versions/deb2c81c0bb2_dataset_splits.py](src/phoenix/db/migrations/versions/deb2c81c0bb2_dataset_splits.py)
- [src/phoenix/server/api/dataloaders/dataset_example_splits.py](src/phoenix/server/api/dataloaders/dataset_example_splits.py)
- [src/phoenix/server/api/helpers/dataset_helpers.py](src/phoenix/server/api/helpers/dataset_helpers.py)
- [src/phoenix/server/api/mutations/dataset_split_mutations.py](src/phoenix/server/api/mutations/dataset_split_mutations.py)
- [src/phoenix/server/api/types/AnnotatorKind.py](src/phoenix/server/api/types/AnnotatorKind.py)
- [src/phoenix/server/api/types/ExperimentRun.py](src/phoenix/server/api/types/ExperimentRun.py)
- [src/phoenix/server/api/types/ExperimentRunAnnotation.py](src/phoenix/server/api/types/ExperimentRunAnnotation.py)
- [src/phoenix/server/daemons/db_disk_usage_monitor.py](src/phoenix/server/daemons/db_disk_usage_monitor.py)
- [tests/integration/_mock_llm_server.py](tests/integration/_mock_llm_server.py)
- [tests/integration/client/test_experiments.py](tests/integration/client/test_experiments.py)
- [tests/integration/experiments/conftest.py](tests/integration/experiments/conftest.py)
- [tests/integration/experiments/test_playground.py](tests/integration/experiments/test_playground.py)
- [tests/unit/db/test_helpers.py](tests/unit/db/test_helpers.py)
- [tests/unit/server/api/helpers/test_dataset_helpers.py](tests/unit/server/api/helpers/test_dataset_helpers.py)

</details>



This page documents Phoenix's dataset and experiment management functionality, which enables users to create test datasets, run experiments against those datasets, and evaluate the results. These capabilities are essential for benchmarking, comparing, and improving LLM application performance through structured testing.

For information about LLM evaluations outside the context of experiments, see [5.2. Evaluation Framework]().

## Overview

Phoenix datasets and experiments provide a structured approach to testing LLM applications:

1.  **Datasets** are collections of examples, each containing input data, reference output, and optional metadata.
2.  **Dataset versions** capture the evolution of datasets over time.
3.  **Dataset splits** allow grouping examples into logical subsets (e.g., train, test) via crosswalk tables (`src/phoenix/db/migrations/versions/deb2c81c0bb2_dataset_splits.py`).
4.  **Experiments** run LLM applications against dataset examples and collect results.
5.  **Experiment runs** are individual executions of an LLM application on a specific dataset example (`src/phoenix/server/api/types/ExperimentRun.py`).
6.  **Experiment evaluations** analyze the quality of experiment run outputs (`src/phoenix/server/api/types/ExperimentRunAnnotation.py`).

### Natural Language to Code Entity Mapping

The following diagram maps high-level concepts central to datasets and experiments to their specific implementations in the Phoenix codebase.

```mermaid
flowchart TD
    subgraph NLC["Natural Language Concepts"]
        DS["Dataset"]
        EX["Experiment"]
        RUN["Experiment Run"]
        EVAL["Evaluation Result"]
        SPLIT["Dataset Split"]
    end

    subgraph CE["Code Entity Space"]
        Dataset["Dataset (class Dataset)"]
        DatasetVersion["DatasetVersion (class DatasetVersion)"]
        DatasetExample["DatasetExample (class DatasetExample)"]
        DatasetExampleRevision["DatasetExampleRevision (class DatasetExampleRevision)"]
        DatasetSplit["DatasetSplit (class DatasetSplit)"]
        Experiment["Experiment (class Experiment)"]
        ExperimentRun["ExperimentRun (class ExperimentRun)"]
        ExperimentRunAnnotation["ExperimentRunAnnotation (class ExperimentRunAnnotation)"]
    end

    DS -.-> Dataset
    DS -.-> DatasetVersion
    DS -.-> DatasetExample
    DS -.-> DatasetExampleRevision
    SPLIT -.-> DatasetSplit
    EX -.-> Experiment
    RUN -.-> ExperimentRun
    EVAL -.-> ExperimentRunAnnotation

    Dataset -->|"has versions"| DatasetVersion
    Dataset -->|"contains"| DatasetExample
    DatasetExample -->|"has revisions"| DatasetExampleRevision
    DatasetSplit -->|"contains examples via"| DatasetSplitMapping["dataset_splits_dataset_examples"]
    DatasetVersion -->|"used in"| Experiment
    Experiment -->|"produces"| ExperimentRun
    ExperimentRun -->|"evaluated by"| ExperimentRunAnnotation
```

Sources:  
[src/phoenix/db/models.py:804-1017](), [src/phoenix/db/migrations/versions/deb2c81c0bb2_dataset_splits.py:54-135]()

---

## Database Schema

The dataset and experiment system is organized around core database tables, including dataset splits introduced in `deb2c81c0bb2_dataset_splits.py`.

```mermaid
erDiagram
    Dataset ||--o{ DatasetVersion : "has"
    Dataset ||--o{ DatasetExample : "contains"
    DatasetExample ||--o{ DatasetExampleRevision : "has"
    DatasetSplit ||--o{ DatasetSplitExample : "maps"
    DatasetExample ||--o{ DatasetSplitExample : "maps"

    Experiment }o--|| Dataset : "uses"
    Experiment }o--|| DatasetVersion : "uses"
    Experiment ||--o{ ExperimentRun : "has"

    ExperimentRun }o--|| DatasetExample : "uses"
    ExperimentRun ||--o{ ExperimentRunAnnotation : "annotated_by"

    Dataset {
        int id PK
        string name UK
        string description
        json metadata_
        datetime created_at
        datetime updated_at
    }

    DatasetVersion {
        int id PK
        int dataset_id FK
        string description
        json metadata_
        datetime created_at
    }

    DatasetExample {
        int id PK
        int dataset_id FK
        int span_rowid FK (nullable)
        datetime created_at
    }

    DatasetSplit {
        int id PK
        string name UK
        string description
        string color
        json metadata_
        datetime created_at
    }

    Experiment {
        int id PK
        int dataset_id FK
        int dataset_version_id FK
        string name
        string description
        int repetitions
        json metadata_
        string project_name (indexed)
        datetime created_at
        datetime updated_at
    }

    ExperimentRun {
        int id PK
        int experiment_id FK
        int dataset_example_id FK
        int repetition_number
        string trace_id (nullable)
        json output
        datetime start_time
        datetime end_time
        int prompt_token_count (nullable)
        int completion_token_count (nullable)
        string error (nullable)
    }

    ExperimentRunAnnotation {
        int id PK
        int experiment_run_id FK
        string name
        string annotator_kind
        string label (nullable)
        float score (nullable)
        string explanation (nullable)
        string trace_id (nullable)
        string error (nullable)
        json metadata_
        datetime start_time
        datetime end_time
    }
```

Sources:  
[src/phoenix/db/models.py:804-1017](), [src/phoenix/db/migrations/versions/deb2c81c0bb2_dataset_splits.py:54-135]()

---

## Datasets

Datasets are collections of input-output example pairs used to systematically test and evaluate LLM applications over time.

### Dataset Components & Example Extraction

-   **Dataset**: Represents a named collection with metadata, description, creation, and update timestamps.  
-   **DatasetVersion**: Captures a snapshot of the dataset at a specific point.  
-   **DatasetExample**: Abstract entity representing an example with a possible origin span linkage (`span_rowid`).  
-   **DatasetExampleRevision**: Stores the actual example content (`input`, `output`), metadata, and revision kind.  

The server extracts dataset inputs and outputs from spans using dedicated helper functions such as `get_dataset_example_input` and `get_dataset_example_output` [src/phoenix/server/api/helpers/dataset_helpers.py:20-79]().

### Dataset Splits

Dataset splits (e.g., `train`, `validation`) are managed via mutations defined in `src/phoenix/server/api/mutations/dataset_split_mutations.py`. These allow grouping examples using the `dataset_splits_dataset_examples` crosswalk table:
- `create_dataset_split` [src/phoenix/server/api/mutations/dataset_split_mutations.py:106-126]()
- `patch_dataset_split` [src/phoenix/server/api/mutations/dataset_split_mutations.py:129-168]()
- `SetDatasetExampleSplitsInput` [src/phoenix/server/api/mutations/dataset_split_mutations.py:46-49]()

### REST API Endpoints

-   `GET /v1/datasets`: Lists datasets with example counts aggregated by joining `DatasetExample` and `DatasetExampleRevision`.  
    [src/phoenix/server/api/routers/v1/datasets.py:103-173]()
-   `DELETE /v1/datasets/{id}`: Deletes a dataset by ID, cleaning associated projects and trace data.  
    [src/phoenix/server/api/routers/v1/datasets.py:176-202]()

Sources:  
[src/phoenix/server/api/helpers/dataset_helpers.py:20-79](), [src/phoenix/server/api/mutations/dataset_split_mutations.py:23-126](), [src/phoenix/server/api/routers/v1/datasets.py:103-202]()

---

## Experiments

Experiments are structured runs of user-defined tasks on datasets to evaluate model behavior and outputs.

### Experiment Model & Runs

-   An experiment is tied to a specific dataset and dataset version, containing a name, repetitions count, and project name.
-   Individual executions against examples are stored as `ExperimentRun` entities [src/phoenix/server/api/types/ExperimentRun.py:31-49](), capturing output, latency, errors, token counts, and trace IDs.
-   Evaluations are stored as `ExperimentRunAnnotation` entities [src/phoenix/server/api/types/ExperimentRunAnnotation.py:18-31](), which store quality scores, labels, explanations, and annotator kinds (`CODE` or `LLM`).

### Creating Experiments and Recording Runs

-   `POST /v1/datasets/{dataset_id}/experiments` creates an experiment snapshot.
-   `POST /v1/experiments/{experiment_id}/runs` records individual run results, enforcing uniqueness on `(experiment_id, dataset_example_id, repetition_number)`.
-   `POST /v1/experiment_evaluations` upserts experiment run evaluations.

Sources:  
[src/phoenix/server/api/types/ExperimentRun.py:31-183](), [src/phoenix/server/api/types/ExperimentRunAnnotation.py:18-172](), [tests/integration/client/test_experiments.py:74-157]()

---

## Python & TypeScript Experiment Runners

Phoenix provides client experiment runners in both Python (`packages/phoenix-client/src/phoenix/client/experiments/__init__.py`) and TypeScript (`js/packages/phoenix-client/src/experiments/runExperiment.ts`) to execute tasks concurrently using underlying execution utilities (`packages/phoenix-client/src/phoenix/client/utils/executors.py`).

### Key Features of `run_experiment` (Python)

-   Executes synchronous or asynchronous user tasks against dataset examples.
-   Supports automatic binding of arguments like `input`, `expected`, `metadata`, and `example` [packages/phoenix-client/src/phoenix/client/experiments/__init__.py:43-52]().
-   Supports evaluators returning scores, labels, and explanations [packages/phoenix-client/src/phoenix/client/experiments/__init__.py:54-76]().
-   Controls concurrency using AIMD (Additive Increase/Multiplicative Decrease) concurrency controllers (`ConcurrencyController` in `packages/phoenix-client/src/phoenix/client/utils/executors.py`).
-   Handles retries and error tracking via `ExecutionDetails` and `AsyncExecutor` [packages/phoenix-client/src/phoenix/client/utils/executors.py:58-200]().

### Data Flow for Experiment Execution

```mermaid
sequenceDiagram
    participant User as "Client Code"
    participant Runner as "run_experiment (Python/TS)"
    participant Executor as "AsyncExecutor / ConcurrencyController"
    participant API as "Phoenix REST API"
    participant DB as "SQLAlchemy / DB"

    User->>Runner: run_experiment(dataset, task, evaluators)
    Runner->>API: POST /v1/datasets/{id}/experiments
    API->>DB: Create Experiment & Snapshot Examples
    DB-->>API: Experiment Object
    API-->>Runner: Experiment ID
    
    loop For Each Dataset Example & Repetition
        Runner->>Executor: Execute Task with Backpressure
        Executor->>Runner: Task Output / Latency / Error
        Runner->>API: POST /v1/experiments/{id}/runs
        API->>DB: Insert ExperimentRun
        Runner->>API: POST /v1/experiment_evaluations
        API->>DB: Upsert ExperimentRunAnnotation
    end

    Runner-->>User: RanExperiment Summary
```

Sources:  
[packages/phoenix-client/src/phoenix/client/experiments/__init__.py:17-112](), [packages/phoenix-client/src/phoenix/client/utils/executors.py:58-200](), [tests/integration/client/test_experiments.py:74-157]()

---

## Database Migrations & Observability

-   Dataset and split migrations are executed via Alembic scripts such as `deb2c81c0bb2_dataset_splits.py` [src/phoenix/db/migrations/versions/deb2c81c0bb2_dataset_splits.py:54-135]().
-   Traces and spans link directly to experiment runs via `trace_id` on `ExperimentRun`, enabling deep inspection into why an experiment failed or succeeded.

Sources:  
[src/phoenix/db/migrations/versions/deb2c81c0bb2_dataset_splits.py:54-135](), [src/phoenix/server/api/types/ExperimentRun.py:62-69]()

---

# Summary Tables of Key Entities

| Entity                  | Description                                   | Key Attributes                                      |
| :---------------------- | :-------------------------------------------- | :-------------------------------------------------- |
| Dataset                 | Collection of testing examples                | `id`, `name`, `description`, `metadata_`            |
| DatasetVersion          | Snapshot/version of a dataset                 | `id`, `dataset_id`, `description`, `metadata_`      |
| DatasetExample          | Example record associated with a dataset      | `id`, `dataset_id`, `span_rowid`                    |
| DatasetSplit            | Logical subset grouping of dataset examples   | `id`, `name`, `color`, `metadata`                   |
| Experiment              | Execution config on dataset version           | `id`, `dataset_id`, `dataset_version_id`, `name`    |
| ExperimentRun           | A single run output of the experiment task    | `experiment_id`, `dataset_example_id`, `output`     |
| ExperimentRunAnnotation | Evaluation or annotation on an experiment run | `experiment_run_id`, `name`, `label`, `score`       |

---

Sources:  
- [src/phoenix/db/models.py:804-1017]()  
- [src/phoenix/db/migrations/versions/deb2c81c0bb2_dataset_splits.py:54-135]()  
- [src/phoenix/server/api/routers/v1/datasets.py:103-202]()  
- [src/phoenix/server/api/helpers/dataset_helpers.py:20-79]()  
- [src/phoenix/server/api/types/ExperimentRun.py:31-183]()  
- [src/phoenix/server/api/types/ExperimentRunAnnotation.py:18-172]()  
- [packages/phoenix-client/src/phoenix/client/experiments/__init__.py:17-112]()  
- [packages/phoenix-client/src/phoenix/client/utils/executors.py:58-200]()

---

# Page: Prompt Management

# Prompt Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [js/packages/phoenix-client/src/prompts/createPrompt.ts](js/packages/phoenix-client/src/prompts/createPrompt.ts)
- [js/packages/phoenix-client/test/prompts/createPrompt.test.ts](js/packages/phoenix-client/test/prompts/createPrompt.test.ts)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py)
- [packages/phoenix-client/src/phoenix/client/types/prompts.py](packages/phoenix-client/src/phoenix/client/types/prompts.py)
- [packages/phoenix-client/tests/canary/sdk/anthropic/test_messages.py](packages/phoenix-client/tests/canary/sdk/anthropic/test_messages.py)
- [packages/phoenix-client/tests/canary/sdk/openai/test_chat.py](packages/phoenix-client/tests/canary/sdk/openai/test_chat.py)
- [src/phoenix/db/types/identifier.py](src/phoenix/db/types/identifier.py)
- [src/phoenix/server/api/input_types/PromptVersionInput.py](src/phoenix/server/api/input_types/PromptVersionInput.py)
- [src/phoenix/server/api/mutations/prompt_label_mutations.py](src/phoenix/server/api/mutations/prompt_label_mutations.py)
- [src/phoenix/server/api/mutations/prompt_mutations.py](src/phoenix/server/api/mutations/prompt_mutations.py)
- [src/phoenix/server/api/mutations/prompt_version_tag_mutations.py](src/phoenix/server/api/mutations/prompt_version_tag_mutations.py)
- [src/phoenix/server/api/routers/v1/prompts.py](src/phoenix/server/api/routers/v1/prompts.py)
- [src/phoenix/server/api/types/DatasetLabel.py](src/phoenix/server/api/types/DatasetLabel.py)
- [src/phoenix/server/api/types/Prompt.py](src/phoenix/server/api/types/Prompt.py)
- [src/phoenix/server/api/types/PromptLabel.py](src/phoenix/server/api/types/PromptLabel.py)
- [src/phoenix/server/api/types/PromptVersion.py](src/phoenix/server/api/types/PromptVersion.py)
- [src/phoenix/server/api/types/PromptVersionTag.py](src/phoenix/server/api/types/PromptVersionTag.py)
- [tests/integration/client/test_prompts.py](tests/integration/client/test_prompts.py)
- [tests/unit/db/types/test_identifier.py](tests/unit/db/types/test_identifier.py)
- [tests/unit/server/api/mutations/test_prompt_mutations.py](tests/unit/server/api/mutations/test_prompt_mutations.py)
- [tests/unit/server/api/routers/v1/test_prompts.py](tests/unit/server/api/routers/v1/test_prompts.py)

</details>



## Purpose and Scope

The Prompt Management subsystem in Phoenix provides comprehensive capabilities for managing the full lifecycle of prompt templates used in large language model (LLM) applications. It handles prompt versioning, templating, tagging, label management, REST/GraphQL APIs, and integration with provider-specific SDK helpers (such as OpenAI and Anthropic formatters). 

This page details the implementation architecture, data flows, database models, GraphQL types, mutations, REST routers, and SDK integration logic.

Sources: [src/phoenix/server/api/routers/v1/prompts.py:1-50](), [src/phoenix/server/api/types/Prompt.py:1-35](), [src/phoenix/server/api/mutations/prompt_mutations.py:1-33]()

---

## Data Model & ORM Architecture

Phoenix stores prompt definitions and versions using SQLAlchemy ORM models. The system separates the logical prompt container (`models.Prompt`) from its immutable content revisions (`models.PromptVersion`) and aliases (`models.PromptVersionTag`).

```mermaid
graph TD
  subgraph "Database Models (Code Entity Space)"
    PromptModel["models.Prompt"]
    PromptVersionModel["models.PromptVersion"]
    PromptVersionTagModel["models.PromptVersionTag"]
    GenerativeModelCustomProvider["models.GenerativeModelCustomProvider"]
  end

  subgraph "GraphQL & API Layer"
    PromptGraphQL["Prompt (Strawberry Type)"]
    PromptVersionGraphQL["PromptVersion (Strawberry Type)"]
    PromptVersionTagGraphQL["PromptVersionTag (Strawberry Type)"]
  end

  PromptModel -->|has_many| PromptVersionModel
  PromptModel -->|has_many| PromptVersionTagModel
  PromptVersionModel -->|has_many| PromptVersionTagModel
  PromptVersionModel -->|optional_fk| GenerativeModelCustomProvider
  
  PromptModel -.->|exposed_as| PromptGraphQL
  PromptVersionModel -.->|exposed_as| PromptVersionGraphQL
  PromptVersionTagModel -.->|exposed_as| PromptVersionTagGraphQL
```
*Diagram 1: Bridging Database Models to GraphQL Types*

Sources: [src/phoenix/server/api/types/Prompt.py:35-180](), [src/phoenix/server/api/types/PromptVersion.py:38-161](), [src/phoenix/server/api/mutations/prompt_mutations.py:76-156]()

---

## GraphQL API Types & Resolvers

Prompts and prompt versions are exposed through Strawberry GraphQL types. The `Prompt` node handles resolution of metadata, authors, and specific versions [src/phoenix/server/api/types/Prompt.py:35-180]().

```python
@strawberry.type
class Prompt(Node):
    id: NodeID[int]
    db_record: strawberry.Private[Optional[models.Prompt]] = None
    # ...
```

The `PromptVersion` type defines the model provider, model name, template structure, invocation parameters, tools, and response format schemas [src/phoenix/server/api/types/PromptVersion.py:38-55](). Conversion from ORM records is handled via `to_gql_prompt_version` [src/phoenix/server/api/types/PromptVersion.py:129-161]().

```mermaid
graph LR
  subgraph "Code Entities"
    ORMVersion["models.PromptVersion"]
    GQLConverter["to_gql_prompt_version()"]
    GQLVersion["PromptVersion (Strawberry Type)"]
  end

  ORMVersion -->|input| GQLConverter
  GQLConverter -->|instantiates| GQLVersion
```
*Diagram 2: PromptVersion Conversion Flow*

Sources: [src/phoenix/server/api/types/Prompt.py:35-180](), [src/phoenix/server/api/types/PromptVersion.py:38-161]()

---

## Mutations & Input Validation

Prompt mutations are grouped within `PromptMutationMixin` [src/phoenix/server/api/mutations/prompt_mutations.py:76-171]() and `PromptVersionTagMutationMixin` [src/phoenix/server/api/mutations/prompt_version_tag_mutations.py:49-125](). They enforce permission classes such as `IsNotReadOnly`, `IsNotViewer`, and `IsLocked`.

```mermaid
graph TD
  subgraph "User Action"
    UserCall["Client calls create_chat_prompt()"]
  end

  subgraph "Mutation & Validation Layer"
    Mixin["PromptMutationMixin.create_chat_prompt()"]
    InputVal["ChatPromptVersionInput.to_orm_prompt_version()"]
    ParamCheck["validate_invocation_parameters_match_provider()"]
  end

  subgraph "Persistence"
    DBSession["AsyncSession.add(prompt)"]
    TagUpsert["upsert_prompt_version_tag()"]
  end

  UserCall --> Mixin
  Mixin --> InputVal
  InputVal --> ParamCheck
  ParamCheck --> DBSession
  DBSession --> TagUpsert
```
*Diagram 3: Prompt Creation and Tagging Flow*

Sources: [src/phoenix/server/api/mutations/prompt_mutations.py:76-156](), [src/phoenix/server/api/mutations/prompt_version_tag_mutations.py:49-125](), [src/phoenix/server/api/input_types/PromptVersionInput.py:90-102]()

---

## REST API Endpoints (v1)

Phoenix also exposes a REST API router for prompts under `src/phoenix/server/api/routers/v1/prompts.py` [src/phoenix/server/api/routers/v1/prompts.py:149-200](). 

Key endpoints include:
- `GET /v1/prompts`: Retrieves a paginated list of all prompts [src/phoenix/server/api/routers/v1/prompts.py:152-174]().
- Prompt version resolution supporting IDs, tags, and latest version lookups [tests/unit/server/api/routers/v1/test_prompts.py:108-150]().

Sources: [src/phoenix/server/api/routers/v1/prompts.py:1-200](), [tests/unit/server/api/routers/v1/test_prompts.py:108-150]()

---

## Client SDK Helpers & Provider Converters

Client libraries and SDK helpers bridge Phoenix prompt versions to provider-specific client payloads (e.g., OpenAI chat completions and Anthropic messages).

```mermaid
graph LR
  subgraph "Prompt Management Client"
    PromptVerData["v1.PromptVersionData"]
    OpenAIConv["to_chat_messages_and_kwargs()"]
    AnthropicConv["to_chat_messages_and_kwargs()"]
  end

  subgraph "Provider APIs"
    OpenAIClient["OpenAI().chat.completions.create()"]
    AnthropicClient["Anthropic().messages.create()"]
  end

  PromptVerData --> OpenAIConv --> OpenAIClient
  PromptVerData --> AnthropicConv --> AnthropicClient
```
*Diagram 4: SDK Prompt Conversion and Dispatch*

- OpenAI Chat Helper: Converts Phoenix prompt version definitions into OpenAI chat completion parameters [packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py:110-164]().
- Anthropic Messages Helper: Converts Phoenix prompt structures into Anthropic message parameters [packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py:120-205]().

Sources: [packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py:110-192](), [packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py:120-205]()

---

# Page: Playground System

# Playground System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-rest-api/SKILL.md](.agents/skills/phoenix-rest-api/SKILL.md)
- [.agents/skills/phoenix-rest-api/references/endpoint-patterns.md](.agents/skills/phoenix-rest-api/references/endpoint-patterns.md)
- [.agents/skills/phoenix-rest-api/references/openapi-codegen.md](.agents/skills/phoenix-rest-api/references/openapi-codegen.md)
- [.agents/skills/phoenix-rest-api/references/testing-patterns.md](.agents/skills/phoenix-rest-api/references/testing-patterns.md)
- [scripts/cost_tracking/sync_models.py](scripts/cost_tracking/sync_models.py)
- [scripts/verify_threshold_cost.py](scripts/verify_threshold_cost.py)
- [src/phoenix/server/api/evaluators.py](src/phoenix/server/api/evaluators.py)
- [src/phoenix/server/api/helpers/evaluators.py](src/phoenix/server/api/helpers/evaluators.py)
- [src/phoenix/server/api/helpers/playground_clients.py](src/phoenix/server/api/helpers/playground_clients.py)
- [src/phoenix/server/api/helpers/secrets.py](src/phoenix/server/api/helpers/secrets.py)
- [src/phoenix/server/api/input_types/EvaluatorPreviewInput.py](src/phoenix/server/api/input_types/EvaluatorPreviewInput.py)
- [src/phoenix/server/api/mutations/chat_mutations.py](src/phoenix/server/api/mutations/chat_mutations.py)
- [src/phoenix/server/api/mutations/secret_mutations.py](src/phoenix/server/api/mutations/secret_mutations.py)
- [src/phoenix/server/api/routers/v1/secrets.py](src/phoenix/server/api/routers/v1/secrets.py)
- [src/phoenix/server/api/subscriptions.py](src/phoenix/server/api/subscriptions.py)
- [src/phoenix/server/api/types/GenerativeProvider.py](src/phoenix/server/api/types/GenerativeProvider.py)
- [src/phoenix/server/api/types/Secret.py](src/phoenix/server/api/types/Secret.py)
- [src/phoenix/server/cost_tracking/model_cost_manifest.json](src/phoenix/server/cost_tracking/model_cost_manifest.json)
- [tests/integration/client/test_secrets.py](tests/integration/client/test_secrets.py)
- [tests/unit/server/api/helpers/test_evaluators.py](tests/unit/server/api/helpers/test_evaluators.py)
- [tests/unit/server/api/helpers/test_playground_clients.py](tests/unit/server/api/helpers/test_playground_clients.py)
- [tests/unit/server/api/mutations/test_evaluator_preview_mutation.py](tests/unit/server/api/mutations/test_evaluator_preview_mutation.py)
- [tests/unit/server/api/mutations/test_secret_mutations.py](tests/unit/server/api/mutations/test_secret_mutations.py)
- [tests/unit/server/api/routers/v1/test_secrets.py](tests/unit/server/api/routers/v1/test_secrets.py)
- [tests/unit/server/api/test_create_llm_evaluator_from_inline.py](tests/unit/server/api/test_create_llm_evaluator_from_inline.py)
- [tests/unit/server/api/test_subscriptions.py](tests/unit/server/api/test_subscriptions.py)
- [tests/unit/server/api/types/test_GenerativeProvider.py](tests/unit/server/api/types/test_GenerativeProvider.py)
- [tests/unit/server/cost_tracking/test_model_cost_manifest.py](tests/unit/server/cost_tracking/test_model_cost_manifest.py)

</details>



The Playground System provides an interactive interface for developing, experimenting, and evaluating LLM prompts across multiple providers. It enables users to compose multi-turn conversations, configure model parameters, run prompts on isolated inputs or entire datasets, and evaluate the resulting outputs. All prompt executions are captured as OpenTelemetry traces, enabling observability and cost tracking.

This system forms a bridge from the frontend UI components to backend LLM client abstractions via fast streaming GraphQL subscriptions for real-time user feedback.

**Related Systems**:
- Prompt Management: [5.4 Prompt Management]()
- Datasets & Experiments: [5.3 Datasets & Experiments]()
- Evaluation Framework: [5.2 Evaluation Framework]()

---

## System Architecture

The Playground system spans three primary layers:

- **Frontend React Application**: maintains state via Zustand stores, renders UI components for multi-instance experimentation, and manages streaming updates.
- **GraphQL Server API**: supports queries, mutations, and subscriptions to run prompts, manage experiments, and stream outputs.
- **LLM Client Abstractions**: backend plugin architecture that encapsulates provider-specific API details behind a uniform streaming interface.

```mermaid
graph TB
    subgraph "Frontend - React UI"
        UI["Playground.tsx<br/>Main component"]
        Store["playgroundStore.tsx<br/>State store"]
        Output["PlaygroundOutput.tsx<br/>Subscription output"]
    end
    
    subgraph "GraphQL API Layer"
        Subscriptions["subscriptions.py<br/>chatCompletion Subscription"]
        Mutations["chat_mutations.py<br/>evaluatorPreviews Mutation"]
    end
    
    subgraph "LLM Client Layer"
        Registry["playground_registry.py<br/>Registered LLM clients"]
        BaseClient["PlaygroundClient (ABC)"]
        OpenAIClient["OpenAIChatCompletionsClient"]
        AnthropicClient["AnthropicClient"]
        OtherClients["GoogleClient, AWSBedrockStreamingClient, etc."]
    end
    
    subgraph "External LLM APIs"
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        OtherAPIs["Other LLM APIs"]
    end
    
    subgraph "Data Storage Layer"
        DB["PostgreSQL/SQLite DB"]
        Projects["models.Project (PLAYGROUND_PROJECT_NAME)"]
        Traces["models.Trace"]
        Spans["models.Span"]
    end
    
    UI --> Store
    Store --> Output
    Output -->|GraphQL Subscription| Subscriptions
    UI -->|GraphQL Mutation| Mutations
    
    Subscriptions --> BaseClient
    Mutations --> BaseClient
    
    Registry -.registers.-> OpenAIClient
    Registry -.registers.-> AnthropicClient
    Registry -.registers.-> OtherClients
    
    BaseClient --> OpenAIClient
    BaseClient --> AnthropicClient
    BaseClient --> OtherClients
    
    OpenAIClient --> OpenAI
    AnthropicClient --> Anthropic
    OtherClients --> OtherAPIs
    
    BaseClient -->|Saves Trace| Traces
    Traces --> Spans
    Traces --> Projects
    Traces --> DB
    Spans --> DB
```

Sources:
- [src/phoenix/server/api/subscriptions.py:76-135]()
- [src/phoenix/server/api/helpers/playground_clients.py:166-200]()
- [src/phoenix/server/api/mutations/chat_mutations.py:115-150]()

---

## LLM Client Abstraction Layer

The Playground backend implements a polymorphic streaming interface for supported LLM providers. Each provider extends the abstract base class `PlaygroundClient` and implements provider-specific streaming chat completions.

### PlaygroundClient Abstract Base Class Details

- Defined in `src/phoenix/server/api/helpers/playground_clients.py`, the `PlaygroundClient` is a generic abstract base class parametrized by the provider-specific client type (`ClientT`) [src/phoenix/server/api/helpers/playground_clients.py:166-175]().
- It manages common attributes like `provider` (e.g., "openai") and `model_name`.
- The abstract `llm_system` property identifies the provider system string for semantic instrumentation [src/phoenix/server/api/helpers/playground_clients.py:181-183]().
- The primary async method `chat_completion_create` is an async generator streaming `ChatCompletionChunk` types, which includes `TextChunk` and `ToolCallChunk` [src/phoenix/server/api/helpers/playground_clients.py:190-201]().
- It integrates OpenTelemetry tracing spans using semantic attribute conventions from `openinference.instrumentation`.
- Each provider client declares static dependency metadata (Python package requirements, etc.) for runtime validation via the `dependencies` method [src/phoenix/server/api/helpers/playground_clients.py:185-189]().
- The LLM client lifecycle supports both synchronous and streaming outputs, converting raw provider responses into internal chunk models.

### Provider-Specific Implementations

- **OpenAIChatCompletionsClient**: Supports OpenAI chat APIs, integrates error handling, dependency injection, and custom invocation parameters [src/phoenix/server/api/helpers/playground_clients.py:1-201]().
- **AnthropicClient**: Uses Anthropic's streaming chat API with its own invocation parameters and evaluation of reasoning capabilities.
- **GoogleClient**: Connects with Google Gemini's streaming client, handling rate-limit, transient errors, and token usage.
- **AWSBedrockStreamingClient**: Handles AWS Bedrock API streaming response with decorated request parameters and retry logic.

```mermaid
classDiagram
    class PlaygroundClient {
        <<abstract>>
        +provider: str
        +model_name: str
        +llm_system: str
        +dependencies() list~Dependency~
        +chat_completion_create(messages, tools, response_format, invocation_parameters, tracer, otel_context, stream_model_output) AsyncIterator~ChatCompletionChunk~
    }
    
    class OpenAIChatCompletionsClient {
        +llm_system = "openai"
        #_chat_completion_create()
    }
    
    class AnthropicClient {
        +llm_system = "anthropic"
        #_chat_completion_create()
    }
    
    class AWSBedrockStreamingClient {
        +llm_system = "bedrock"
        #_chat_completion_create()
    }
    
    class GoogleClient {
        +llm_system = "google"
        #_chat_completion_create()
    }
    
    PlaygroundClient <|-- OpenAIChatCompletionsClient
    PlaygroundClient <|-- AnthropicClient
    PlaygroundClient <|-- AWSBedrockStreamingClient
    PlaygroundClient <|-- GoogleClient
```

Sources:
- [src/phoenix/server/api/helpers/playground_clients.py:166-201]()

---

### Provider Registration and Discovery

Provider clients register themselves using the decorator `@register_llm_client`. This decorator is defined in `playground_registry.py` and manages a singleton registry mapping providers and model names to client classes.

- The decorator takes a `GenerativeProviderKey` (e.g., `GenerativeProviderKey.OPENAI`) and a sequence of model name strings [src/phoenix/server/api/helpers/playground_clients.py:87-87]().
- It registers the decorated `PlaygroundClient` subclass in the singleton registry.
- At runtime, `initialize_playground_clients()` prepares this registry and is called during server startup [src/phoenix/server/api/subscriptions.py:69-70]().
- To select a client instance for a request, `get_playground_client()` queries the registry based on the generative provider key extracted from the connection configuration [src/phoenix/server/api/helpers/playground_clients.py:38-42]().

```mermaid
graph LR
    subgraph "At Module Load Time"
        Decorator["@register_llm_client [playground_registry.py]"]
        Client1["OpenAIChatCompletionsClient"]
        Client2["AnthropicClient"]
        
        Decorator -.decorates.-> Client1
        Decorator -.decorates.-> Client2
    end
    
    subgraph "At Runtime"
        Initialize["initialize_playground_clients() [subscriptions.py:69-70]"]
        Lookup["get_playground_client() [playground_clients.py]"]
        Instance["PlaygroundClient instance"]
        
        Initialize --> Lookup
        Lookup --> Instance
    end
```

Sources:
- [src/phoenix/server/api/subscriptions.py:69-70]()
- [src/phoenix/server/api/helpers/playground_clients.py:38-42]()

---

## Streaming Execution via GraphQL Subscriptions

The Playground backend supports low-latency streaming of LLM outputs via the GraphQL subscription `chatCompletion` defined in `src/phoenix/server/api/subscriptions.py`.

### Subscription Workflow

- Incoming subscription requests provide input parameters wrapped in a `ChatCompletionInput` model [src/phoenix/server/api/subscriptions.py:75-81]().
- The subscription resolver calls `_stream_single_chat_completion()` which:
  - Converts the prompt template into internal `PlaygroundMessage` sequences [src/phoenix/server/api/subscriptions.py:88-96]().
  - Invokes the `chat_completion_create()` async generator on the resolved `PlaygroundClient` [src/phoenix/server/api/subscriptions.py:105-113]().
  - Yields `ChatCompletionChunk` events (text chunks, tool call partials) [src/phoenix/server/api/subscriptions.py:114-115]().
  - On completion, saves the OpenTelemetry trace and span records to the database [src/phoenix/server/api/subscriptions.py:122-125]().
  - Emits a final `ChatCompletionSubscriptionResult` containing the span ID and metadata [src/phoenix/server/api/subscriptions.py:128-131]().
- Errors during streaming are caught and emitted as `ChatCompletionSubscriptionError` [src/phoenix/server/api/subscriptions.py:116-120]().

### Concurrency and Cleanup

The subscription manages multiple concurrent repetitions by:
- Creating tasks for each repetition stream.
- On cancellation or errors, tasks are cancelled, awaited, and async generators are properly closed in sequence:
  1. Cancel all tasks [src/phoenix/server/api/subscriptions.py:163-165]().
  2. Await cancellation propagation [src/phoenix/server/api/subscriptions.py:168-172]().
  3. Close async generator streams with `aclose()` to trigger generator-finalization logic [src/phoenix/server/api/subscriptions.py:175-179]().
- This prevents resource leaks and ensures OpenTelemetry spans and DB writes are finalized.

### Message Chunk Types

| Payload Type | Emitted During | Description |
|---|---|---|
| `TextChunk` | Streaming text output | Incremental output text tokens |
| `ToolCallChunk` | Streaming tool calls | Partial function/tool call argument data |
| `ChatCompletionSubscriptionResult` | Completion | Final metadata with span reference |
| `ChatCompletionSubscriptionError` | On error | Error message payload |

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant Sub as subscriptions.py (Subscription Resolver)
    participant Client as PlaygroundClient (Backend LLM Client)
    participant API as External LLM API

    UI->>Sub: Start subscription with ChatCompletionInput
    Sub->>Client: chat_completion_create(...)
    Client->>API: Stream request to external LLM provider
    API-->>Client: Streaming response chunks
    Client-->>Sub: Yields TextChunk and ToolCallChunk events
    Sub-->>UI: Streams chunks incrementally over GraphQL
    Note over Sub: On completion: save OTel span and trace to DB
    Sub-->>UI: Emit ChatCompletionSubscriptionResult with span info
```

Sources:
- [src/phoenix/server/api/subscriptions.py:75-135]()
- [src/phoenix/server/api/subscriptions.py:144-182]()
- [src/phoenix/server/api/helpers/playground_clients.py:190-201]()

---

## Multi-Provider Support and Rate Limiting

The Playground supports multiple LLM providers:

- **OpenAI**: Standard OpenAI API and Azure OpenAI endpoints.
- **Anthropic**: Claude models with support for Anthropic-specific invocation parameters such as "thinking" configurations.
- **Google**: Google Gemini with token usage tracking and retry policies.
- **AWS Bedrock**: AWS Bedrock Runtime client handling inferencing.
- Additional providers can register new clients and be exposed in the UI.

Rate limiting keys and error detection are implemented per provider in their client classes via helper functions such as `openai_rate_limit_key`, `anthropic_rate_limit_key`, `google_rate_limit_key`, and `bedrock_rate_limit_key` [src/phoenix/server/api/helpers/playground_clients.py:64-70](). Error classification in client code detects transient vs. permanent errors for retry logic.

Sources:
- [src/phoenix/server/api/helpers/playground_clients.py:64-70]()

---

## Playground Registry

The core registration and discovery of LLM clients is done via the registry module [src/phoenix/server/api/helpers/playground_registry.py]().

- Maintains a dictionary mapping providers and models to `PlaygroundClient` subclasses.
- Supports querying registered providers and available models.
- Enables fallback to a provider-level default client if a model-specific client is not found.
- This decouples client selection from API and session layers, enabling modular plug-in extensions.

```mermaid
classDiagram
    class PlaygroundClientRegistry {
        -_registry: dict
        +get_client(provider_key, model_name) Optional~PlaygroundClient~
        +list_all_models() list
        +list_all_providers() list
    }
    
    PlaygroundClientRegistry <|-- PLAYGROUND_CLIENT_REGISTRY
```

Sources:
- [src/phoenix/server/api/helpers/playground_registry.py]()

---

## Summary

The Playground System tightly integrates frontend interactive prompt editing with backend LLM provider abstractions and OpenTelemetry observability. Its extensible, plugin-based architecture enables streaming multi-provider support, multi-turn conversations, tool calling, and dataset-backed prompt experiments—all streamed live via GraphQL subscriptions and persisted with trace metadata.

---

# Appendix: Mapping Natural Language to Code Entities

## Natural Language: LLM Client Layer — Code Entities

```mermaid
graph LR
    PlaygroundClient["PlaygroundClient (ABC) [src/phoenix/server/api/helpers/playground_clients.py:167-175]"]
    OpenAIClient["OpenAIChatCompletionsClient [src/phoenix/server/api/helpers/playground_clients.py]"]
    AnthropicClient["AnthropicClient [src/phoenix/server/api/helpers/playground_clients.py]"]
    AWSBedrockClient["BedrockClient [src/phoenix/server/api/helpers/playground_clients.py]"]
    GoogleClient["GoogleClient [src/phoenix/server/api/helpers/playground_clients.py]"]
    
    PlaygroundClient --> OpenAIClient
    PlaygroundClient --> AnthropicClient
    PlaygroundClient --> AWSBedrockClient
    PlaygroundClient --> GoogleClient
```

Sources:
- [src/phoenix/server/api/helpers/playground_clients.py:167-175]()

## Natural Language: GraphQL Subscription Handler — Code Entities

```mermaid
graph LR
    ChatCompletionSubscription["chatCompletion (GraphQL Subscription) [src/phoenix/server/api/subscriptions.py]"]
    StreamSingleChatCompletion["_stream_single_chat_completion() [src/phoenix/server/api/subscriptions.py:75-85]"]
    PlaygroundClient["PlaygroundClient (ABC) [src/phoenix/server/api/helpers/playground_clients.py:167-175]"]
    ChatCompletionChunk["ChatCompletionChunk (Union) [src/phoenix/server/api/helpers/playground_clients.py:149-149]"]
    SpanPersist["Database Session Add & Flush [src/phoenix/server/api/subscriptions.py:122-125]"]

    ChatCompletionSubscription --> StreamSingleChatCompletion
    StreamSingleChatCompletion --> PlaygroundClient
    PlaygroundClient --> ChatCompletionChunk
    StreamSingleChatCompletion --> SpanPersist
```

Sources:
- [src/phoenix/server/api/subscriptions.py:75-85]()
- [src/phoenix/server/api/subscriptions.py:122-125]()
- [src/phoenix/server/api/helpers/playground_clients.py:149-175]()

---

# Page: AI Agent Backend (PxI)

# AI Agent Backend (PxI)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-harbor/SKILL.md](.agents/skills/phoenix-harbor/SKILL.md)
- [.github/workflows/pxi-evals.yml](.github/workflows/pxi-evals.yml)
- [docs/phoenix/integrations/evaluation-integrations/harbor.mdx](docs/phoenix/integrations/evaluation-integrations/harbor.mdx)
- [docs/phoenix/integrations/evaluation-integrations/images/harbor-phoenix-plugin-dark.svg](docs/phoenix/integrations/evaluation-integrations/images/harbor-phoenix-plugin-dark.svg)
- [docs/phoenix/integrations/evaluation-integrations/images/harbor-phoenix-plugin-light.svg](docs/phoenix/integrations/evaluation-integrations/images/harbor-phoenix-plugin-light.svg)
- [docs/phoenix/integrations/evaluation-integrations/images/harbor-trial-dark.svg](docs/phoenix/integrations/evaluation-integrations/images/harbor-trial-dark.svg)
- [docs/phoenix/integrations/evaluation-integrations/images/harbor-trial-light.svg](docs/phoenix/integrations/evaluation-integrations/images/harbor-trial-light.svg)
- [docs/phoenix/pxi.mdx](docs/phoenix/pxi.mdx)
- [evals/harbor/jobs/trail-benchmark-dev-no-code-mode.yaml](evals/harbor/jobs/trail-benchmark-dev-no-code-mode.yaml)
- [evals/pxi/README.md](evals/pxi/README.md)
- [evals/pxi/datasets/experiment_observations.yaml](evals/pxi/datasets/experiment_observations.yaml)
- [evals/pxi/datasets/experiments_skill_trigger.yaml](evals/pxi/datasets/experiments_skill_trigger.yaml)
- [evals/pxi/datasets/in_app_links.yaml](evals/pxi/datasets/in_app_links.yaml)
- [evals/pxi/datasets/set_spans_filter.yaml](evals/pxi/datasets/set_spans_filter.yaml)
- [evals/pxi/datasets/set_time_range.yaml](evals/pxi/datasets/set_time_range.yaml)
- [evals/pxi/evaluators/filters.py](evals/pxi/evaluators/filters.py)
- [evals/pxi/evaluators/links.py](evals/pxi/evaluators/links.py)
- [evals/pxi/evaluators/tools.py](evals/pxi/evaluators/tools.py)
- [evals/pxi/harness/agent_task.py](evals/pxi/harness/agent_task.py)
- [evals/pxi/harness/backend.py](evals/pxi/harness/backend.py)
- [internal_docs/specs/harbor-phoenix-plugin.md](internal_docs/specs/harbor-phoenix-plugin.md)
- [js/app/src/pages/trace/span/LLMInput.tsx](js/app/src/pages/trace/span/LLMInput.tsx)
- [js/app/src/pages/trace/span/LLMSpanInfo.tsx](js/app/src/pages/trace/span/LLMSpanInfo.tsx)
- [js/app/src/pages/trace/span/LLMToolSchemasList.tsx](js/app/src/pages/trace/span/LLMToolSchemasList.tsx)
- [packages/phoenix-client/src/phoenix/client/harbor/_adapter.py](packages/phoenix-client/src/phoenix/client/harbor/_adapter.py)
- [packages/phoenix-client/src/phoenix/client/harbor/_model.py](packages/phoenix-client/src/phoenix/client/harbor/_model.py)
- [packages/phoenix-client/src/phoenix/client/harbor/_plugin.py](packages/phoenix-client/src/phoenix/client/harbor/_plugin.py)
- [packages/phoenix-client/src/phoenix/client/harbor/_recorder.py](packages/phoenix-client/src/phoenix/client/harbor/_recorder.py)
- [packages/phoenix-client/src/phoenix/client/harbor/_scores.py](packages/phoenix-client/src/phoenix/client/harbor/_scores.py)
- [packages/phoenix-client/src/phoenix/client/harbor/_traces.py](packages/phoenix-client/src/phoenix/client/harbor/_traces.py)
- [packages/phoenix-client/tests/client/harbor/test_adapter.py](packages/phoenix-client/tests/client/harbor/test_adapter.py)
- [packages/phoenix-client/tests/client/harbor/test_harbor_contract.py](packages/phoenix-client/tests/client/harbor/test_harbor_contract.py)
- [packages/phoenix-client/tests/client/harbor/test_plugin.py](packages/phoenix-client/tests/client/harbor/test_plugin.py)
- [packages/phoenix-client/tests/client/harbor/test_recorder.py](packages/phoenix-client/tests/client/harbor/test_recorder.py)
- [packages/phoenix-client/tests/client/harbor/test_scores.py](packages/phoenix-client/tests/client/harbor/test_scores.py)
- [packages/phoenix-client/tests/client/harbor/test_traces.py](packages/phoenix-client/tests/client/harbor/test_traces.py)
- [src/phoenix/server/agents/agent_factory.py](src/phoenix/server/agents/agent_factory.py)
- [src/phoenix/server/agents/capabilities/tools/external/__init__.py](src/phoenix/server/agents/capabilities/tools/external/__init__.py)
- [src/phoenix/server/agents/capabilities/tools/internal/bash.py](src/phoenix/server/agents/capabilities/tools/internal/bash.py)
- [src/phoenix/server/agents/prompts/__init__.py](src/phoenix/server/agents/prompts/__init__.py)
- [src/phoenix/server/agents/prompts/skills/phoenix-graphql/SKILL.md](src/phoenix/server/agents/prompts/skills/phoenix-graphql/SKILL.md)
- [src/phoenix/server/agents/prompts/static/base/BASE_INSTRUCTIONS.xml](src/phoenix/server/agents/prompts/static/base/BASE_INSTRUCTIONS.xml)
- [src/phoenix/server/agents/prompts/tools/PHOENIX_MCP_TOOL_INSTRUCTIONS.xml.j2](src/phoenix/server/agents/prompts/tools/PHOENIX_MCP_TOOL_INSTRUCTIONS.xml.j2)
- [src/phoenix/server/agents/pydantic_ai/openinference_agent_wrapper.py](src/phoenix/server/agents/pydantic_ai/openinference_agent_wrapper.py)
- [src/phoenix/server/agents/pydantic_ai/openinference_capability_wrapper.py](src/phoenix/server/agents/pydantic_ai/openinference_capability_wrapper.py)
- [src/phoenix/server/agents/pydantic_ai/openinference_model_wrapper.py](src/phoenix/server/agents/pydantic_ai/openinference_model_wrapper.py)
- [src/phoenix/server/agents/pydantic_ai/tool_spans/_mixin.py](src/phoenix/server/agents/pydantic_ai/tool_spans/_mixin.py)
- [src/phoenix/server/api/graphql_execute.py](src/phoenix/server/api/graphql_execute.py)
- [src/phoenix/server/api/helpers/agent_sessions.py](src/phoenix/server/api/helpers/agent_sessions.py)
- [src/phoenix/server/api/routers/agents.py](src/phoenix/server/api/routers/agents.py)
- [src/phoenix/server/cost_tracking/token_cost_calculator.py](src/phoenix/server/cost_tracking/token_cost_calculator.py)
- [src/phoenix/server/daemons/experiment_runner.py](src/phoenix/server/daemons/experiment_runner.py)
- [src/phoenix/server/mcp/graphql/__init__.py](src/phoenix/server/mcp/graphql/__init__.py)
- [src/phoenix/server/mcp/graphql/output.py](src/phoenix/server/mcp/graphql/output.py)
- [src/phoenix/server/mcp/graphql/tools.py](src/phoenix/server/mcp/graphql/tools.py)
- [src/phoenix/server/mcp/skills/__init__.py](src/phoenix/server/mcp/skills/__init__.py)
- [src/phoenix/server/mcp_server.py](src/phoenix/server/mcp_server.py)
- [src/phoenix/tracers.py](src/phoenix/tracers.py)
- [tests/integration/harbor/run_plugin_e2e.py](tests/integration/harbor/run_plugin_e2e.py)
- [tests/unit/pxi/evals/test_agent_task_inputs.py](tests/unit/pxi/evals/test_agent_task_inputs.py)
- [tests/unit/pxi/evals/test_datasets.py](tests/unit/pxi/evals/test_datasets.py)
- [tests/unit/server/agents/capabilities/test_external_tools.py](tests/unit/server/agents/capabilities/test_external_tools.py)
- [tests/unit/server/agents/capabilities/test_phoenix_mcp.py](tests/unit/server/agents/capabilities/test_phoenix_mcp.py)
- [tests/unit/server/agents/capabilities/tools/internal/test_bash.py](tests/unit/server/agents/capabilities/tools/internal/test_bash.py)
- [tests/unit/server/agents/prompts/test_static_prompts.py](tests/unit/server/agents/prompts/test_static_prompts.py)
- [tests/unit/server/agents/pydantic_ai/test_openinference_agent_wrapper.py](tests/unit/server/agents/pydantic_ai/test_openinference_agent_wrapper.py)
- [tests/unit/server/agents/pydantic_ai/test_openinference_capability_wrapper.py](tests/unit/server/agents/pydantic_ai/test_openinference_capability_wrapper.py)
- [tests/unit/server/agents/pydantic_ai/test_openinference_model_wrapper.py](tests/unit/server/agents/pydantic_ai/test_openinference_model_wrapper.py)
- [tests/unit/server/agents/test_agent_factory.py](tests/unit/server/agents/test_agent_factory.py)
- [tests/unit/server/agents/test_agents_router.py](tests/unit/server/agents/test_agents_router.py)
- [tests/unit/server/api/cassettes/test_subscriptions/TestChatCompletionOverDatasetSubscription.test_example_dispatched_as_previous_example_finishes_is_not_dropped.yaml](tests/unit/server/api/cassettes/test_subscriptions/TestChatCompletionOverDatasetSubscription.test_example_dispatched_as_previous_example_finishes_is_not_dropped.yaml)
- [tests/unit/server/api/helpers/test_agent_sessions.py](tests/unit/server/api/helpers/test_agent_sessions.py)
- [tests/unit/server/api/mutations/test_agent_session_mutations.py](tests/unit/server/api/mutations/test_agent_session_mutations.py)
- [tests/unit/server/api/routers/test_agents.py](tests/unit/server/api/routers/test_agents.py)
- [tests/unit/server/daemons/test_experiment_runner.py](tests/unit/server/daemons/test_experiment_runner.py)
- [tests/unit/server/mcp/test_skills.py](tests/unit/server/mcp/test_skills.py)
- [tests/unit/server/test_app_mcp_mount.py](tests/unit/server/test_app_mcp_mount.py)
- [tests/unit/test_tracers.py](tests/unit/test_tracers.py)

</details>



The AI Agent Backend, known as Phoenix Intelligence (PxI), is the server-side system powering Phoenix's AI assistant capabilities. It enables the Phoenix frontend to interact seamlessly with diverse Large Language Models (LLMs) through a unified interface, facilitating agent orchestration, tool execution, and context enrichment based on the application's state. The backend also manages ingestion and export of OpenTelemetry traces from agent conversations, supporting observability and cost accounting.

---

## Purpose and Scope

PxI serves as the foundational system for:

- **AI Agent Orchestration**: Managing agent message flows, tool invocation, and response generation.
- **Model Selection**: Providing a flexible and extensible mechanism to select LLM providers or custom-defined models.
- **Tool Capabilities**: Offering Phoenix-specific tools (e.g., querying traces, annotations) and external tools to agents as first-class capabilities.
- **Context Resolution**: Incorporating rich contextual information derived from Phoenix’s data layer and UI state into agent interactions.
- **REST API Interface**: Exposing a `/agents` endpoint compatible with Vercel AI SDK enabling streaming chat responses.
- **Tracing and Telemetry**: Recording detailed OpenTelemetry traces from agent interactions for observability and cost tracking.
- **Evaluation Harness**: Running experiments to validate and benchmark agent behavior using live Phoenix datasets.

---

## Architecture Overview

The PxI backend is implemented primarily around a FastAPI router exposing the `/v1/agents/assistant/chat` REST API [src/phoenix/server/api/routers/agents.py:1-315](), which is the communication gateway for frontend AI agent requests. This router uses the `pydantic-ai` library to manage agent construction, message processing, and tool integration.

### Key Components and Relationships

- **Pydantic-AI Agent Factory (`build_agent`)**: Builds the main AI agent instance by assembling a model, prompts, capabilities, and tooling according to the request and server configuration [src/phoenix/server/agents/agent_factory.py:69-94]().
- **Model Factory (`build_model`)**: Resolves and constructs LLM clients from built-in providers or user-defined custom providers, fetching credentials securely from DB or environment [src/phoenix/server/agents/model_factory.py:102-185]().
- **Context Resolution (`resolve_contexts`)**: Parses frontend UI state and data selection into structured contexts that agents consume for prompts and tool execution [src/phoenix/server/agents/context.py:1-136]().
- **Tool Capabilities & Skills**: Implements a variety of tools dynamically registered, including Phoenix domain-specific tooling, external web access tools, internal Bash execution, and experiment skill sets [src/phoenix/server/agents/capabilities/__init__.py](), [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95]().
- **OpenTelemetry Tracing (`Tracer`)**: Wraps each agent interaction in detailed trace spans persisted as Phoenix database models for analysis and cost computation [src/phoenix/tracers.py:116-183]().

---

### AI Agent Backend Data Flow

```mermaid
graph TD
    UI["Phoenix Frontend (AgentChatPanel)"] --> API["POST /v1/agents/assistant/chat (agents.py)"]
    API --> MsgModel["ChatRequestBody (pydantic model)"]
    MsgModel --> Context["resolve_contexts (context.py)"]
    MsgModel --> Model["build_model (model_factory.py)"]
    Context --> Agent["build_agent (agent_factory.py)"]
    Model --> Agent
    Agent --> AgentWrapper["OpenInferenceAgentWrapper (pydantic_ai)"]
    AgentWrapper --> ToolInvoke{"Tool Invocation (if any)"}
    ToolInvoke --> BackendServices["Phoenix Backend Services (DB, Event Queue)"]
    BackendServices --> AgentWrapper
    AgentWrapper --> LLMProvider["LLM Provider (OpenAI, Anthropic, etc)"]
    LLMProvider --> AgentWrapper
    AgentWrapper --> Tracer["Tracer (tracers.py)"]
    Tracer --> DBTrace["models.Trace & models.Span (DB)"]
    AgentWrapper --> Router
    Router --> StreamResp["Streaming Response (VercelAIAdapter)"]
    StreamResp --> UI
```
Sources:
- [src/phoenix/server/api/routers/agents.py:1-315]()
- [src/phoenix/server/agents/agent_factory.py:69-94]()
- [src/phoenix/server/agents/model_factory.py:102-185]()
- [src/phoenix/server/agents/context.py:1-136]()
- [src/phoenix/server/agents/capabilities/__init__.py]()
- [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95]()
- [src/phoenix/tracers.py:116-183]()

---

## `/agents` REST Endpoint

The principal endpoint for AI agent communication is:

`POST /v1/agents/assistant/chat`

This endpoint manages chat-based AI agent message exchanges with support for streaming responses compatible with the Vercel AI SDK UI [src/phoenix/server/api/routers/agents.py:1-202]().

### Request Message Model

- **`contexts`**: An array of discriminated union types representing UI or domain contexts such as Project, Trace, Playground, Dataset, and Agent spans. These contexts provide rich information about the environment, filters, selected objects, and other state the agent needs [src/phoenix/server/agents/context.py:1-136]().

- **`messages`**: Array of chat messages preserving context, user metadata, role, and Phoenix UI attribution layers.

- **`model`**: An `AgentModelSelection` object specifying the requested model provider and model name. Used to invoke the LLM correctly and map to the registered backend models [src/phoenix/server/api/routers/agents.py:140-145]().

- **`ingest_traces`**: Boolean flag signaling if the entire agent interaction should be traced and persisted in Phoenix's trace storage.

### Response Model

- Streaming JSON chunks, chunked by the Vercel AI SDK-compatible `VercelAIAdapter` layer allow UX components to display tokens incrementally and handle tool invocation metadata [src/phoenix/server/api/routers/agents.py:41-70]().

Sources:
- [src/phoenix/server/api/routers/agents.py:41-70]()
- [src/phoenix/server/api/routers/agents.py:140-145]()
- [src/phoenix/server/api/routers/agents.py:1-202]()
- [src/phoenix/server/agents/context.py:1-136]()

---

## Agent Factory (`build_agent`)

The agent factory is the core function that assembles a pydantic-ai `Agent` instance with configured tools and model [src/phoenix/server/agents/agent_factory.py:69-94]().

### Inputs

- `model`: The resolved `pydantic_ai.Model` object for conversation completion.
- `prompts`: Optional prompt templates that provide instructions to tools and skills [src/phoenix/server/agents/agent_factory.py:95-95]().
- `docs_mcp_server`: Optional MCP (Model Context Protocol) toolset for Phoenix docs capabilities [src/phoenix/server/agents/agent_factory.py:76-76]().
- `enable_web_access`: Flag to enable internet-based web search and fetch capabilities [src/phoenix/server/agents/agent_factory.py:80-80]().
- `tracer_provider`: OpenTelemetry tracer provider for instrumentation [src/phoenix/server/agents/agent_factory.py:81-81]().
- Authentication flags and user id for permission enforcement.
- Optional support for subagents (nested agents or scripting via Bash) [src/phoenix/server/agents/agent_factory.py:82-93]().

### Capabilities Composed

- **GetCurrentDatetimeCapability**: Provides current date-time tooling [src/phoenix/server/agents/agent_factory.py:104-106]().
- **External Tool Capability**: Dynamically includes external tools (e.g., search, snippet tools) [src/phoenix/server/agents/agent_factory.py:107-115]().
- **UIContextsCapability**: Provides access to the resolved Phoenix UI/application context [src/phoenix/server/agents/agent_factory.py:113-113]().
- **BashCapability** (optional): Enables execution of shell commands in a sandboxed environment [src/phoenix/server/agents/agent_factory.py:116-126]().
- **MintlifyDocsMCPCapability** (optional): Integrates the MCP server for documentation tooling [src/phoenix/server/agents/agent_factory.py:129-135]().
- **PhoenixMCPCapability** (optional): Integrates the Phoenix MCP server for GraphQL API access [src/phoenix/server/agents/agent_factory.py:136-151]().
- **GitHubMCPCapability** (optional): GitHub interaction tools with configured access [src/phoenix/server/agents/agent_factory.py:152-166]().

All capabilities are combined and wrapped by an `OpenInferenceCapabilityWrapper` for tracing and to unify event instrumentation.

### Output

Returns a configured `AbstractAgent` ready to run with proper tooling and model backing [src/phoenix/server/agents/agent_factory.py:69-94]().

Sources:
- [src/phoenix/server/agents/agent_factory.py:69-94]()
- [src/phoenix/server/agents/agent_factory.py:95-166]()
- [src/phoenix/server/agents/capabilities/__init__.py]()
- [src/phoenix/server/agents/capabilities/tools/external/__init__.py]()
- [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95]()
- [src/phoenix/server/agents/web_access.py]()

---

## Model Selection (`build_model`)

The model factory resolves an `AgentModelSelection` into a concrete LLM client for use by the AI agent.

### Model Provider Types

| Provider Type | Description | Credential Source | Supported Providers |
|---------------|-------------|-------------------|----------------------------------------|
| Built-in      | Common pre-integrated LLM providers with managed secrets | DB secrets, environment variables | OpenAI, Anthropic, Azure OpenAI, Google, Bedrock, Local, Dummy |
| Custom        | User-defined providers configured via a generative model and custom SDK configs | Database with GlobalID lookup | OpenAI-compatible, Anthropic-compatible |

### Credential Resolution Logic

- Attempts to load secrets for built-in providers from Phoenix credential storage.
- If secrets are missing, falls back to environment variables.
- Custom providers are resolved by `GlobalID` referencing `GenerativeModelCustomProvider` DB entries and using SDK config parameters.
- Raises runtime errors if required secrets or configurations are absent, ensuring secure setup.

### Wrapping and Instrumentation

All created model clients are wrapped for trace instrumentation and prompt-caching when applicable, supporting advanced internal optimizations and telemetry.

See [src/phoenix/server/agents/model_factory.py:102-185]() for detailed selection flow and provider-specific handling.

Sources:
- [src/phoenix/server/agents/model_factory.py:102-185]()

---

## Tool Capabilities

PxI enables AI agents to interact with various powerful tools encapsulated as capabilities:

- **External Tools**: Dynamically defined tools registered by frontend configuration and integrated by backend capability functions for extensibility [src/phoenix/server/agents/capabilities/tools/external/__init__.py]().
- **Phoenix Internal Tools**: Native tooling such as bash execution, current datetime, listing playground models, running experiments, and manipulating prompts [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95]().
- **Skills Capability**: Domain-specific skill bundles that encapsulate complex operations across Phoenix datasets, experiments, and playgrounds [src/phoenix/server/mcp/skills/__init__.py]().
- **MCP Server Tool**: An optional tool integration that connects to an MCP protocol server (e.g., Mintlify Docs) to augment documentation queries inside agents [src/phoenix/server/mcp_server.py:1-73]().
- **Phoenix MCP Tool**: Integrates the Phoenix MCP server, allowing agents to interact with the Phoenix GraphQL API [src/phoenix/server/mcp_server.py:1-73]().
- **Web Access**: Optional internet search and fetch capabilities allow grounding responses with up-to-date information [src/phoenix/server/agents/web_access.py]().

Tools may emit special Vercel AI SDK streaming chunks for UI updates, approvals, or incremental outputs. The server enforces permissions and sandboxing especially for destructive or high-risk operations.

Sources:
- [src/phoenix/server/agents/capabilities/tools/external/__init__.py]()
- [src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95]()
- [src/phoenix/server/mcp/skills/__init__.py]()
- [src/phoenix/server/mcp_server.py:1-73]()
- [src/phoenix/server/agents/web_access.py]()

---

## Context Resolution

PxI includes a comprehensive context resolution system that converts frontend shapes into typed, unioned context classes that inform prompt generation and tool strategy.

### Context Types

- **AppContext**: Captures environment details like timezone offset, browser clock, and config flags [src/phoenix/server/agents/context.py:130-136]().
- **ProjectContext**: Includes project metadata, active span filters, and selected experiments [src/phoenix/server/agents/context.py:130-136]().
- **Trace and AgentSpanContext**: Details about the currently viewed trace, spans, and turn structures [src/phoenix/server/agents/context.py:130-136]().
- **DatasetContext**: Information about loaded datasets useful for prompt or evaluation tooling [src/phoenix/server/agents/context.py:130-136]().
- **PlaygroundContext**: Details from playground UI, prompt instances, and running experiments [src/phoenix/server/agents/context.py:130-136]().
- **LlmEvaluatorUIContext**: Context for LLM evaluators [src/phoenix/server/agents/context.py:130-136]().
- **CodeEvaluatorUIContext**: Context for code evaluators [src/phoenix/server/agents/context.py:130-136]().

This detailed context provides the agent with state mirroring the user's current focus inside Phoenix, thus enabling precise, relevant AI interaction [src/phoenix/server/agents/context.py:1-136]().

---

### Context Resolution Flow

```mermaid
graph TB
    UI["Phoenix UI State (frontend contexts)"] --> ContextResolver["resolve_contexts (context.py)"]
    ContextResolver --> AppCtx["AppContext"]
    ContextResolver --> ProjectCtx["ProjectContext"]
    ContextResolver --> TraceCtx["TraceContext / AgentSpanContext"]
    ContextResolver --> DatasetCtx["DatasetContext"]
    ContextResolver --> PlaygroundCtx["PlaygroundContext"]
    ContextResolver --> LlmEvalCtx["LlmEvaluatorUIContext"]
    ContextResolver --> CodeEvalCtx["CodeEvaluatorUIContext"]
    ProjectCtx --> Filter["Current Span Filters"]
    TraceCtx --> TraceIDs["Trace and Span Identifiers"]
    ContextResolver --> AgentInput["AgentDependencies.contexts"]
```
Sources:
- [src/phoenix/server/agents/context.py:1-136]()
- [tests/unit/server/agents/test_agent_factory.py:81-94]()

---

## OpenTelemetry Tracing (PxI)

### Tracer Design

The `Tracer` class instrumenting the PxI backend is a wrapper around an OpenTelemetry `TracerProvider`. It buffers spans in-memory, builds Phoenix DB models (`Trace`, `Span`, `SpanCost`), and supports exporting spans to a remote collector if configured [src/phoenix/tracers.py:116-183]().

Key features include:

- Raising span attribute limits to allow large chat and context metadata [src/phoenix/tracers.py:159-162]().
- Synthetic span recording including agent message initiations, tool invocations, and sub-agent flows.
- Detached context propagation allowing agent spans to appear independent from HTTP server spans [src/phoenix/tracers.py:60-70]().
- Integration with Phoenix cost tracking via `SpanCostCalculator` [src/phoenix/tracers.py:148-154]().

### PxI Tracer Data Flow

```mermaid
graph LR
    TP["TracerProvider"] --> SP["SimpleSpanProcessor"]
    SP --> BSE["_BufferedSpanExporter (in-memory buffer)"]
    BSE --> GDB["get_db_traces() converts to DB models"]
    GDB --> TMODEL["models.Trace (DB)"]
    TMODEL --> SPANMODEL["models.Span (DB)"]
    SPANMODEL --> COST["models.SpanCost (DB)"]
```
Sources:
- [src/phoenix/tracers.py:60-183]()
- [tests/unit/test_tracers.py:105-107]()

---

## PXI Evaluation Harness

PxI maintains an evaluation suite to test and validate AI agent capabilities using live Phoenix data.

### Structure

- `evals/pxi/harness/agent_task.py`: Defines async harness infrastructure to construct and run agents with minimal Phoenix dependencies [evals/pxi/harness/agent_task.py]().
- `evals/pxi/gate.py`: Contains the `PxiGate` class, which defines the evaluation logic and assertions for PXI agents.
- `evals/pxi/tests/test_pxi_evals.py`: Contains unit tests for the PXI evaluation harness.
- Additional directories support datasets, evaluators, online trace evaluations, and trace ingest tooling [evals/pxi/README.md]().

### Capabilities

- Evaluators check correctness and quality of agent tool calls and control flows.
- The harness can run live against Phoenix datasets to verify system integration.
- Supports local and CI execution for regression and performance measurement. The `.github/workflows/pxi-evals.yml` workflow automates PXI evaluations in CI [.github/workflows/pxi-evals.yml:1-166]().
- Online evaluators consume PXI trace data stored in Phoenix and annotate spans with evaluation outcomes.

This evaluation layer ensures PxI's continuous monitoring and improvement in real-world use cases.

Sources:
- [evals/pxi/harness/agent_task.py]()
- [evals/pxi/README.md]()
- [.github/workflows/pxi-evals.yml:1-166]()

---

## Harbor Server-Agent Evaluation Framework

The Phoenix client library includes a plugin for the Harbor evaluation framework, enabling comprehensive testing of server-side agents.

### Integration

The `arize-phoenix-client` package includes an optional `harbor` extra dependency. When installed, it provides the `PhoenixJobPlugin` entry point for Harbor.

### Plugin Design

The `PhoenixJobPlugin` records Harbor evaluation jobs in Phoenix, allowing teams to compare results across agents, models, attempts, and time. Harbor remains responsible for running agents and verifiers.

Key aspects of the plugin:
- **Dataset Inference**: Infers a Phoenix dataset from the Harbor dataset.
- **Experiment Creation**: Creates one Phoenix experiment for each agent and model in a job.
- **Experiment Runs**: Records each Harbor trial as an experiment run.
- **Evaluation Scores**: Stores Harbor's aggregate reward and infrastructure status as dense evaluation scores, and step-level rewards as sparse diagnostic scores.
- **Trace Linkage**: Links each run to an ATIF (Agent Trace Import Format) or live OTLP trace when supported. ATIF is the default, not requiring agent instrumentation.

### Data Model Mapping

| Harbor Concept                | Phoenix Concept             | Mapping                                                           |
| ----------------------------- | --------------------------- | ----------------------------------------------------------------- |
| Dataset                       | Dataset                     | Name inferred from Harbor; optional override                      |
| Task                          | Dataset example             | Task ID, name, and instruction in input; other fields in metadata  |
| Task digest                   | Dataset example metadata    | Full Harbor task digest                                           |
| Resolved task snapshot        | Dataset version             | Complete synchronized task set                                    |
| Job × agent × model           | Experiment                  | One experiment for each agent and model                           |
| Logical trial                 | Experiment run              | One run for each planned task attempt                             |
| Planned attempt               | Repetition                  | Deterministic repetition number                                   |
| Trial exception               | Run error                   | Kept separate from behavioral failure                             |
| Trial `reward`                | Dense evaluation            | Stored on behaviorally completed runs                             |
| Infrastructure status         | Dense `infra_ok` evaluation | Stored on every attempted run                                     |
| Step reward                   | Sparse evaluation           | Named `<step_name>.<reward_key>`                                  |
| ATIF trajectory or OTLP spans | Trace                       | Linked to the experiment run when available                       |

### Usage

The Harbor plugin can be run using `harbor run --plugin arize-phoenix`. Specific targets in the `Makefile` facilitate Harbor evaluations, such as `harbor-stage-environments`, `harbor-publish-fixtures`, `harbor-plugin-e2e`, `harbor-oracle`, `harbor-run`, and `harbor-view`.

Sources:
- [internal_docs/specs/harbor-phoenix-plugin.md]()

---

## Summary

The AI Agent Backend (PxI) in Phoenix provides a comprehensive, extensible server-side AI agent framework. It manages:

- Model selection and invocation with built-in and custom LLMs.
- Rich tool integrations within the Phoenix domain and external resources.
- Context resolution translating frontend state into actionable agent input.
- Detailed OpenTelemetry tracing for visibility and cost management.
- A well-specified REST endpoint exposing streaming chat interfaces.
- An integrated evaluation harness to maintain agent quality over time.
- Integration with the Harbor framework for robust server-agent evaluation.

This design enables Phoenix to offer a potent AI assistant experience tightly coupled with domain data and observability workflows.

---

## References and Sources

- [`src/phoenix/server/api/routers/agents.py:1-202`]()
- [`src/phoenix/server/agents/agent_factory.py:69-166`]()
- [`src/phoenix/server/agents/model_factory.py:102-185`]()
- [`src/phoenix/server/agents/context.py:1-136`]()
- [`src/phoenix/tracers.py:60-183`]()
- [`evals/pxi/harness/agent_task.py`]()
- [`evals/pxi/README.md`]()
- [`internal_docs/specs/harbor-phoenix-plugin.md`]()
- [`tests/unit/server/agents/test_agent_factory.py:81-94`]()
- [`src/phoenix/server/cost_tracking/span_cost_calculator.py`]()
- [`tests/unit/test_tracers.py:105-107`]()
- [`src/phoenix/server/agents/capabilities/__init__.py`]()
- [`src/phoenix/server/agents/capabilities/tools/external/__init__.py`]()
- [`src/phoenix/server/agents/capabilities/tools/internal/bash.py:34-95`]()
- [`src/phoenix/server/agents/web_access.py`]()
- [`.github/workflows/pxi-evals.yml:1-166`]()
- [`src/phoenix/server/mcp_server.py:1-73`]()
- [`src/phoenix/server/mcp/skills/__init__.py`]()

---

# Page: Sessions & Annotations

# Sessions & Annotations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [js/packages/phoenix-client/examples/get_session_turns.ts](js/packages/phoenix-client/examples/get_session_turns.ts)
- [js/packages/phoenix-client/src/sessions/getSessionTurns.ts](js/packages/phoenix-client/src/sessions/getSessionTurns.ts)
- [js/packages/phoenix-client/src/sessions/index.ts](js/packages/phoenix-client/src/sessions/index.ts)
- [js/packages/phoenix-client/test/sessions/getSessionTurns.test.ts](js/packages/phoenix-client/test/sessions/getSessionTurns.test.ts)
- [packages/phoenix-client/examples/sessions/get_session_turns_example.py](packages/phoenix-client/examples/sessions/get_session_turns_example.py)
- [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py](packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py)
- [packages/phoenix-client/tests/client/resources/sessions/__init__.py](packages/phoenix-client/tests/client/resources/sessions/__init__.py)
- [packages/phoenix-client/tests/client/resources/sessions/test_sessions.py](packages/phoenix-client/tests/client/resources/sessions/test_sessions.py)
- [src/phoenix/db/insertion/document_annotation.py](src/phoenix/db/insertion/document_annotation.py)
- [src/phoenix/db/insertion/span_annotation.py](src/phoenix/db/insertion/span_annotation.py)
- [src/phoenix/db/insertion/trace_annotation.py](src/phoenix/db/insertion/trace_annotation.py)
- [src/phoenix/db/insertion/types.py](src/phoenix/db/insertion/types.py)
- [src/phoenix/db/types/annotation_configs.py](src/phoenix/db/types/annotation_configs.py)
- [src/phoenix/server/api/auth.py](src/phoenix/server/api/auth.py)
- [src/phoenix/server/api/dataloaders/span_annotations.py](src/phoenix/server/api/dataloaders/span_annotations.py)
- [src/phoenix/server/api/input_types/CreateSpanAnnotationInput.py](src/phoenix/server/api/input_types/CreateSpanAnnotationInput.py)
- [src/phoenix/server/api/input_types/CreateTraceAnnotationInput.py](src/phoenix/server/api/input_types/CreateTraceAnnotationInput.py)
- [src/phoenix/server/api/input_types/PatchAnnotationInput.py](src/phoenix/server/api/input_types/PatchAnnotationInput.py)
- [src/phoenix/server/api/mutations/annotation_config_mutations.py](src/phoenix/server/api/mutations/annotation_config_mutations.py)
- [src/phoenix/server/api/mutations/api_key_mutations.py](src/phoenix/server/api/mutations/api_key_mutations.py)
- [src/phoenix/server/api/mutations/span_annotations_mutations.py](src/phoenix/server/api/mutations/span_annotations_mutations.py)
- [src/phoenix/server/api/mutations/trace_annotations_mutations.py](src/phoenix/server/api/mutations/trace_annotations_mutations.py)
- [src/phoenix/server/api/routers/v1/annotation_configs.py](src/phoenix/server/api/routers/v1/annotation_configs.py)
- [src/phoenix/server/api/types/Annotation.py](src/phoenix/server/api/types/Annotation.py)
- [src/phoenix/server/api/types/AnnotationConfig.py](src/phoenix/server/api/types/AnnotationConfig.py)
- [src/phoenix/server/api/types/SpanAnnotation.py](src/phoenix/server/api/types/SpanAnnotation.py)
- [src/phoenix/server/api/types/TraceAnnotation.py](src/phoenix/server/api/types/TraceAnnotation.py)
- [tests/integration/client/test_annotations.py](tests/integration/client/test_annotations.py)
- [tests/unit/db/types/test_annotation_configs.py](tests/unit/db/types/test_annotation_configs.py)
- [tests/unit/server/api/mutations/test_annotation_config_mutations.py](tests/unit/server/api/mutations/test_annotation_config_mutations.py)
- [tests/unit/server/api/mutations/test_span_annotation_mutations.py](tests/unit/server/api/mutations/test_span_annotation_mutations.py)
- [tests/unit/server/api/mutations/test_trace_annotation_mutations.py](tests/unit/server/api/mutations/test_trace_annotation_mutations.py)
- [tests/unit/server/api/routers/v1/test_annotation_configs.py](tests/unit/server/api/routers/v1/test_annotation_configs.py)
- [tests/unit/server/api/types/test_SpanAnnotation.py](tests/unit/server/api/types/test_SpanAnnotation.py)
- [tests/unit/server/api/types/test_TraceAnnotation.py](tests/unit/server/api/types/test_TraceAnnotation.py)

</details>



This page details Phoenix's implementation of project sessions (multi-turn conversation grouping), session annotations, and the comprehensive annotation system for spans and traces. Project sessions group related traces into logical units of conversation, while annotations enrich spans, traces, and sessions with qualitative and quantitative feedback crucial for LLM evaluation, debugging, and analytics.

---

## Project Sessions

Project sessions provide dynamic, time-bounded groupings of related traces, typically representing multi-turn conversations or execution sequences within a defined user context.

### Data Model and Lifecycle

The foundational data model for sessions is the SQLAlchemy model `models.ProjectSession` [src/phoenix/db/models.py:537-553](). This model stores key metadata:

- `id`: Internal primary key
- `session_id`: User-supplied string identifying the session
- `project_id`: Foreign key linking to the parent project
- `start_time` and `end_time`: Timestamps establishing the temporal boundaries of the session

Sessions are managed dynamically during span ingestion. The span insertion pipeline (`src/phoenix/db/insertion/span.py`) evaluates session associations:
- If a trace already belongs to a session (`project_session_rowid`), that relationship is retained to preserve session integrity [src/phoenix/db/insertion/span.py:67-75]().
- If a trace lacks a session but the incoming span specifies a `session_id`, Phoenix attempts to locate an existing `ProjectSession` matching that `session_id` and project [src/phoenix/db/insertion/span.py:82-98]().
  - If found, the session's time bounds (`start_time`, `end_time`) are expanded if the span extends them [src/phoenix/db/insertion/span.py:94-98]().
  - If not found, a new `ProjectSession` record is instantiated [src/phoenix/db/insertion/span.py:82-87]().

Sources: [src/phoenix/db/models.py:537-553](), [src/phoenix/db/insertion/span.py:25-110]()

### Session API and Client Resources

Sessions are exposed via GraphQL (`src/phoenix/server/api/types/ProjectSession.py`) and REST endpoints (`packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py`). Clients can programmatically list, retrieve, and inspect session records and their associated conversational turns using helper methods like `Sessions.get()` and `Sessions.list()` [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:114-193]().

Key GraphQL fields on `ProjectSession` include:
- `id`: Relay GlobalID
- `sessionId`: User-provided session identifier string
- `startTime` and `endTime`: Temporal range
- `numTraces` and `numTracesWithError`: Trace statistics resolved via DataLoaders
- `tracesConnection`: Paginated connection for child traces

Sources: [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:114-193](), [src/phoenix/server/api/types/ProjectSession.py:42-203]()

### Diagram: Natural Language to Code — Sessions

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        UserSession["User Conversation Session"]
        TraceGrouping["Trace Grouping by session_id"]
        CostAggregation["Session Token & Cost Aggregation"]
    end

    subgraph "CodeEntitySpace"
        PSModel["models.ProjectSession"]
        InsertSpan["insert_span (Span Ingestion)"]
        DLTraces["session_num_traces DataLoader"]
        GraphQLAPI["ProjectSession (GraphQL Type)"]
        ClientRes["Sessions.list() (Client Resource)"]
    end

    UserSession --> TraceGrouping
    TraceGrouping --> InsertSpan
    InsertSpan --> PSModel
    PSModel --> DLTraces
    DLTraces --> GraphQLAPI
    GraphQLAPI --> ClientRes
    CostAggregation --> GraphQLAPI
```
*Figure 1: Bridging conversational sessions to Phoenix server models and client SDKs.*

Sources: [src/phoenix/db/models.py:537-553](), [src/phoenix/db/insertion/span.py:25-110](), [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:114-193]()

---

## Annotation System

The annotation system allows attaching structured scores, categorical labels, explanations, and metadata to spans, traces, and project sessions.

### Core Annotation Models

Phoenix defines distinct SQLAlchemy models for each target entity level:
- `SpanAnnotation`: Attached to individual spans [src/phoenix/db/models.py:656-692]()
- `TraceAnnotation`: Attached to root traces [src/phoenix/db/models.py:700-720]()
- `ProjectSessionAnnotation`: Attached to project sessions [src/phoenix/db/models.py:730-750]()

Each annotation record stores:
- `name`: Feature or evaluation metric name (the reserved name `"note"` is prohibited for general annotations) [src/phoenix/server/api/mutations/span_annotations_mutations.py:28-33]()
- `label` and `score`: Categorical label and numeric evaluation score
- `explanation`: Textual reasoning or rationale
- `metadata_`: JSON dictionary for arbitrary extra attributes
- `annotator_kind`: Origin classification (`LLM`, `CODE`, `HUMAN`) [tests/integration/client/test_annotations.py:31-31]()
- `source` and `identifier`: Provenance tracking fields

Sources: [src/phoenix/db/models.py:656-750](), [src/phoenix/server/api/mutations/span_annotations_mutations.py:28-33](), [tests/integration/client/test_annotations.py:31-31]()

### Annotation Configuration

Annotation behavior, validation bounds, and allowed values are governed by `AnnotationConfig` entities:
- **Categorical**: Discrete choices with associated scores and optimization directions [src/phoenix/db/types/annotation_configs.py](), [src/phoenix/server/api/types/AnnotationConfig.py:59-78]()
- **Continuous**: Bounded numeric ranges [src/phoenix/server/api/types/AnnotationConfig.py:82-101]()
- **Freeform**: Unstructured text or thresholds [src/phoenix/server/api/types/AnnotationConfig.py:105-111]()

Mutations for managing annotation configurations are handled in `AnnotationConfigMutationMixin` [src/phoenix/server/api/mutations/annotation_config_mutations.py:163-201]().

Sources: [src/phoenix/server/api/mutations/annotation_config_mutations.py:163-201](), [src/phoenix/server/api/types/AnnotationConfig.py:59-111]()

### Annotation API Mutations

Annotations are managed through GraphQL mutations supporting upsert semantics (e.g., `create_span_annotations` in `SpanAnnotationMutationMixin` and `create_trace_annotations` in `TraceAnnotationMutationMixin`) [src/phoenix/server/api/mutations/span_annotations_mutations.py:43-150](), [src/phoenix/server/api/mutations/trace_annotations_mutations.py:43-148]().

Key mutation workflows:
1. Validate input payloads and enforce that annotation names do not equal `"note"` [src/phoenix/server/api/mutations/span_annotations_mutations.py:51-52]().
2. Resolve global IDs to internal database row IDs [src/phoenix/server/api/mutations/span_annotations_mutations.py:58-66]().
3. Verify target span or trace existence [src/phoenix/server/api/mutations/span_annotations_mutations.py:68-80]().
4. Perform an upsert (`SELECT` existing by `(rowid, name, identifier)` and update, or `INSERT` new record) [src/phoenix/server/api/mutations/span_annotations_mutations.py:103-127]().
5. Emit DML events (`SpanAnnotationInsertEvent`, `TraceAnnotationInsertEvent`) to update event queues and subscribers [src/phoenix/server/api/mutations/trace_annotations_mutations.py:133-136]().

Sources: [src/phoenix/server/api/mutations/span_annotations_mutations.py:43-150](), [src/phoenix/server/api/mutations/trace_annotations_mutations.py:43-148]()

### Diagram: Natural Language to Code — Annotations

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        UserFeedback["User Qualitative Feedback"]
        EvalScores["LLM Evaluation Scores & Explanations"]
        AnnotationRules["Annotation Configurations & Constraints"]
    end

    subgraph "CodeEntitySpace"
        SpanAnno["models.SpanAnnotation"]
        TraceAnno["models.TraceAnnotation"]
        AnnoConfig["models.AnnotationConfig"]
        MutSpanAnno["create_span_annotations (GraphQL Mutation)"]
        MutConfig["create_annotation_config (GraphQL Mutation)"]
    end

    UserFeedback --> MutSpanAnno
    EvalScores --> SpanAnno
    AnnotationRules --> MutConfig
    MutConfig -.-> AnnoConfig
    MutSpanAnno -.-> SpanAnno
```
*Figure 2: Mapping user feedback and evaluation metrics to Phoenix annotation database models and mutations.*

Sources: [src/phoenix/db/models.py:656-720](), [src/phoenix/server/api/mutations/annotation_config_mutations.py:163-201](), [src/phoenix/server/api/mutations/span_annotations_mutations.py:43-150]()

---

## Data Loading, Summaries, and Session Filter DSL

To support efficient frontend rendering and aggregation, Phoenix implements specialized data loading and filtering subsystems:

- **Annotation Summaries**: Backed by optimized DataLoaders that batch and cache annotation summary queries per project, annotation name, and entity type, leveraging two-tier TTL and LFU caches.
- **Session Filter DSL**: Implemented in `phoenix.server.session_filters`, this domain-specific language parses filter expressions to restrict project sessions based on multi-criteria attribute conditions across traces and annotations. These expressions integrate directly into GraphQL query resolvers and REST endpoints (e.g., `Sessions.list(filter=...)`) [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:138-193]().

Sources: [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:138-193](), [src/phoenix/server/session_filters.py]()

---

## Summary

Phoenix project sessions and annotations combine to deliver robust multi-turn conversation tracking and multi-tier feedback evaluation. Through dynamic span-based session grouping, strict upsert mutation semantics, configurable annotation definitions, and flexible DSL filtering, Phoenix provides a comprehensive environment for monitoring and evaluating complex LLM applications.

---

# Sources

- [src/phoenix/db/models.py:537-553, 656-750]()
- [src/phoenix/db/insertion/span.py:25-110]()
- [src/phoenix/server/api/types/ProjectSession.py:42-203]()
- [src/phoenix/server/api/types/AnnotationConfig.py:59-111]()
- [src/phoenix/server/api/mutations/annotation_config_mutations.py:163-201]()
- [src/phoenix/server/api/mutations/span_annotations_mutations.py:28-150]()
- [src/phoenix/server/api/mutations/trace_annotations_mutations.py:43-148]()
- [packages/phoenix-client/src/phoenix/client/resources/sessions/__init__.py:114-193]()
- [tests/integration/client/test_annotations.py:31-31]()
- [src/phoenix/server/session_filters.py]()

---

# Page: Development & Deployment

# Development & Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.vscode/extensions.json](.vscode/extensions.json)
- [DEVELOPMENT.md](DEVELOPMENT.md)
- [Makefile](Makefile)
- [evals/harbor/README.md](evals/harbor/README.md)
- [evals/harbor/tasks/regression/prompt-hill-climb/README.md](evals/harbor/tasks/regression/prompt-hill-climb/README.md)
- [evals/harbor/tasks/regression/prompt-hill-climb/steps/step_01_create_evaluator/tests/check.py](evals/harbor/tasks/regression/prompt-hill-climb/steps/step_01_create_evaluator/tests/check.py)
- [evals/harbor/tasks/regression/prompt-hill-climb/steps/step_02_hill_climb/tests/check.py](evals/harbor/tasks/regression/prompt-hill-climb/steps/step_02_hill_climb/tests/check.py)
- [evals/harbor/tasks/regression/prompt-hill-climb/steps/step_03_compare/tests/check.py](evals/harbor/tasks/regression/prompt-hill-climb/steps/step_03_compare/tests/check.py)
- [evals/harbor/tasks/regression/prompt-hill-climb/tests/hill_climb_checks.py](evals/harbor/tasks/regression/prompt-hill-climb/tests/hill_climb_checks.py)
- [evals/harbor/tasks/regression/prompt-hill-climb/tests/test.sh](evals/harbor/tasks/regression/prompt-hill-climb/tests/test.sh)
- [evals/harbor/tasks/trail-benchmark-dev/most-failing-tool/tests/expected.json](evals/harbor/tasks/trail-benchmark-dev/most-failing-tool/tests/expected.json)
- [evals/harbor/verifiers/harbor_verifiers/verify.py](evals/harbor/verifiers/harbor_verifiers/verify.py)
- [scripts/ci/test_skill_graphql_examples.py](scripts/ci/test_skill_graphql_examples.py)
- [tests/unit/harbor/cassettes/test_verify/test_reference_check_grades_semantic_answers.yaml](tests/unit/harbor/cassettes/test_verify/test_reference_check_grades_semantic_answers.yaml)
- [tests/unit/harbor/test_verify.py](tests/unit/harbor/test_verify.py)

</details>



This page provides an overview of the development workflows, testing strategies, continuous integration and delivery (CI/CD) pipelines, release management, and deployment architectures for the Phoenix monorepo. As a parent overview, it summarizes operational concerns across Python and TypeScript environments, linking to dedicated child pages for deep technical details.

---

## 6.1. Development Workflow & Tooling

Development at Phoenix relies on a unified workspace configuration supporting Python (`uv`, `tox`, `Makefile`) and TypeScript (`pnpm`, Vite, Relay) ecosystems [DEVELOPMENT.md:32-56](). Developers set up their environments by executing `uv sync --all-extras --all-packages` for Python dependencies and `pnpm install` alongside `pnpm build` under the `js/` directory for the React frontend [DEVELOPMENT.md:36-49](). Process orchestration is managed locally via `dekit` through `pnpm dev`, which spins up the FastAPI server, Vite dev server, and trace generator concurrently with hot-reloading [DEVELOPMENT.md:43-58]().

For details on setting up your environment, pre-commit hooks, code formatting with `ruff`, and local DevOps containers, see [Development Workflow & Tooling](#6.1).

```mermaid
graph TD
  classDef code fill:#fff,stroke:#333,stroke-width:2px;
  
  subgraph "Code Entity Space"
    UvSync["uv sync --all-packages"]:::code
    PnpmBuild["pnpm build (js/app)"]:::code
    ToxEnv["tox.ini (tox run -e unit_tests)"]:::code
    DekitRun["pnpm dev (dekit process manager)"]:::code
  end

  Developer["Developer Setup"] --> UvSync
  Developer --> PnpmBuild
  UvSync --> ToxEnv
  UvSync --> DekitRun
  PnpmBuild --> DekitRun

  title["Development Workflow Architecture"]
```
Sources: [DEVELOPMENT.md:36-58](), [Makefile:33-118](), [tox.ini:1-165]()

---

## 6.2. Testing Strategy

Phoenix employs a multi-tiered testing strategy spanning unit tests, integration tests against both SQLite and PostgreSQL backends, and end-to-end browser tests powered by Playwright [DEVELOPMENT.md:120-158](). Test execution is primarily orchestrated using `tox`, which runs isolated virtual environments for distinct packages (`arize-phoenix`, `phoenix-client`, `phoenix-evals`, `phoenix-otel`) [tox.ini:1-165](). Integration and canary tests validate database migrations, mock LLM servers, and client SDK contracts.

For details on writing and executing tests, configuring database fixtures, and running E2E suites, see [Testing Strategy](#6.2).

```mermaid
graph TD
  classDef code fill:#fff,stroke:#333,stroke-width:2px;

  subgraph "Code Entity Space"
    ToxIni["tox.ini (tox environments)"]:::code
    UnitTests["tests/unit/ (tox run -e unit_tests)"]:::code
    IntTests["tests/integration/ (tox run -e integration_tests)"]:::code
    PlaywrightCI[".github/workflows/playwright.yaml"]:::code
  end

  ToxIni --> UnitTests
  ToxIni --> IntTests
  PlaywrightCI --> PlaywrightRun["Playwright E2E Suite"]

  title["Testing Architecture Overview"]
```
Sources: [tox.ini:1-165](), [.github/workflows/playwright.yaml:1-132]()

---

## 6.3. CI/CD Pipeline

The continuous integration and deployment pipeline is driven by GitHub Actions, featuring conditional execution paths managed via path filters (`dorny/paths-filter`) to optimize build times [python-CI.yml:44-46](). Dedicated workflows handle Python matrix testing across multiple versions [python-CI.yml:114-184](), TypeScript type-checking and linting [typescript-CI.yml:41-101](), Playwright UI tests [playwright.yaml:44-136](), and automated cost-model synchronization [cost-sync.yml:1-89]().

For details on workflow triggers, quality gates, and Claude-driven automation tasks, see [CI/CD Pipeline](#6.3).

```mermaid
graph TD
  classDef code fill:#fff,stroke:#333,stroke-width:2px;

  subgraph "Code Entity Space"
    PythonWorkflow[".github/workflows/python-CI.yml"]:::code
    TSWorkflow[".github/workflows/typescript-CI.yml"]:::code
    PlaywrightWorkflow[".github/workflows/playwright.yaml"]:::code
    CostSyncWorkflow[".github/workflows/cost-sync.yml"]:::code
  end

  Trigger["Push / PR Event"] --> PythonWorkflow
  Trigger --> TSWorkflow
  Trigger --> PlaywrightWorkflow
  Trigger --> CostSyncWorkflow

  title["CI/CD Workflow Pipeline"]
```
Sources: [.github/workflows/python-CI.yml:1-210](), [.github/workflows/typescript-CI.yml:1-91](), [.github/workflows/playwright.yaml:1-132](), [.github/workflows/cost-sync.yml:1-89]()

---

## 6.4. Release Management

Release management is automated using `release-please` configuration files, enforcing PEP 440-compliant semantic versioning across Python and TypeScript packages. The release pipeline generates changelogs, publishes production packages to PyPI and npm, and cuts pre-release development builds tied to specific commit SHAs [publish.yaml:18-22](). Container images are built for multiple architectures and pushed to registries alongside automatic manifest updates.

For release strategies, versioning schemes, and credential configuration, see [Release Management](#6.4).

Sources: [.github/workflows/publish.yaml:1-178](), [.github/workflows/release.yml:1-24]()

---

## 6.5. Kubernetes Deployment

Phoenix provides multi-stage `Dockerfile` definitions that bundle distroless Python container images with pre-compiled web assets and sandbox runtimes [Dockerfile:32-148](). Self-hosting is supported via Helm charts (`helm/`) and Kustomize manifests (`kustomize/`), enabling customizable deployments with PostgreSQL or SQLite persistence, secure ingress controllers, and built-in Prometheus metrics scraping [helm/values.yaml]().

For configuration parameters, authentication setups, and helm chart installation instructions, see [Kubernetes Deployment](#6.5).

```mermaid
graph TD
  classDef code fill:#fff,stroke:#333,stroke-width:2px;

  subgraph "Code Entity Space"
    Dockerfile["Dockerfile (Multi-stage build)"]:::code
    HelmValues["helm/values.yaml"]:::code
    KustomizeBase["kustomize/base/phoenix.yaml"]:::code
  end

  Dockerfile --> ContainerImage["Distroless Phoenix Image"]
  HelmValues --> HelmChart["Helm Deployment Chart"]
  KustomizeBase --> KustomizeDeploy["Kustomize Manifests"]

  title["Deployment Artifact Architecture"]
```
Sources: [Dockerfile:1-148](), [helm/values.yaml](), [kustomize/base/phoenix.yaml:1-41]()

---

## 6.6. API Reference Documentation

Phoenix documentation is built using Sphinx with autodoc extensions to extract docstrings from core Python modules, hosting generated outputs on ReadTheDocs. Additionally, a Mintlify documentation site driven by `docs.json` configuration provides user guides, SDK references, and sitemap generation.

For instructions on updating docstrings, regenerating API references, and previewing documentation locally, see [API Reference Documentation](#6.6).

Sources: [.gitignore:85-87](), [DEVELOPMENT.md:150-176]()

---

## 6.7. Agent Skills & Plugin Distribution

The repository packages reusable AI agent capabilities under `.agents/skills` and distributes verified plugins for Claude and Codex environments via the `plugins/` directory. These configurations are tracked using `skills-lock.json` and tested against harness environments such as Harbor (`evals/harbor/`) to ensure reliable tool-calling and API interactions.

For details on creating custom skills, managing locks, and testing plugin integrations, see [Agent Skills & Plugin Distribution](#6.7).

```mermaid
graph TD
  classDef code fill:#fff,stroke:#333,stroke-width:2px;

  subgraph "Code Entity Space"
    AgentSkills[".agents/skills/ Library"]:::code
    PluginsDir["plugins/ Directory"]:::code
    HarborEval["evals/harbor/ Framework"]:::code
  end

  AgentSkills --> PluginsDir
  PluginsDir --> HarborEval

  title["Agent Skills and Plugin Ecosystem"]
```
Sources: [.gitignore:113-117](), [evals/harbor/README.md:1-22]()

---

# Page: Development Workflow & Tooling

# Development Workflow & Tooling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.cursor/rules/python/RULE.md](.cursor/rules/python/RULE.md)
- [.gitignore](.gitignore)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [.vscode/extensions.json](.vscode/extensions.json)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [DEVELOPMENT.md](DEVELOPMENT.md)
- [Makefile](Makefile)
- [evals/harbor/README.md](evals/harbor/README.md)
- [evals/harbor/tasks/regression/prompt-hill-climb/README.md](evals/harbor/tasks/regression/prompt-hill-climb/README.md)
- [evals/harbor/tasks/regression/prompt-hill-climb/steps/step_01_create_evaluator/tests/check.py](evals/harbor/tasks/regression/prompt-hill-climb/steps/step_01_create_evaluator/tests/check.py)
- [evals/harbor/tasks/regression/prompt-hill-climb/steps/step_02_hill_climb/tests/check.py](evals/harbor/tasks/regression/prompt-hill-climb/steps/step_02_hill_climb/tests/check.py)
- [evals/harbor/tasks/regression/prompt-hill-climb/steps/step_03_compare/tests/check.py](evals/harbor/tasks/regression/prompt-hill-climb/steps/step_03_compare/tests/check.py)
- [evals/harbor/tasks/regression/prompt-hill-climb/tests/hill_climb_checks.py](evals/harbor/tasks/regression/prompt-hill-climb/tests/hill_climb_checks.py)
- [evals/harbor/tasks/regression/prompt-hill-climb/tests/test.sh](evals/harbor/tasks/regression/prompt-hill-climb/tests/test.sh)
- [evals/harbor/tasks/trail-benchmark-dev/most-failing-tool/tests/expected.json](evals/harbor/tasks/trail-benchmark-dev/most-failing-tool/tests/expected.json)
- [evals/harbor/verifiers/harbor_verifiers/verify.py](evals/harbor/verifiers/harbor_verifiers/verify.py)
- [js/DEVELOPMENT.md](js/DEVELOPMENT.md)
- [pytest-quiet.ini](pytest-quiet.ini)
- [scripts/ci/ensure_graphql_mutations_have_permission_classes.py](scripts/ci/ensure_graphql_mutations_have_permission_classes.py)
- [scripts/ci/test_skill_graphql_examples.py](scripts/ci/test_skill_graphql_examples.py)
- [scripts/docker/devops/dev.sh](scripts/docker/devops/dev.sh)
- [scripts/docker/devops/docker-compose.yml](scripts/docker/devops/docker-compose.yml)
- [scripts/docker/devops/oidc-server/Dockerfile](scripts/docker/devops/oidc-server/Dockerfile)
- [scripts/docker/devops/oidc-server/frontend/package.json](scripts/docker/devops/oidc-server/frontend/package.json)
- [scripts/docker/devops/oidc-server/frontend/pnpm-workspace.yaml](scripts/docker/devops/oidc-server/frontend/pnpm-workspace.yaml)
- [scripts/docker/devops/oidc-server/frontend/src/UserSelector.tsx](scripts/docker/devops/oidc-server/frontend/src/UserSelector.tsx)
- [scripts/docker/devops/oidc-server/package.json](scripts/docker/devops/oidc-server/package.json)
- [scripts/docker/devops/oidc-server/src/database/client.ts](scripts/docker/devops/oidc-server/src/database/client.ts)
- [scripts/docker/devops/oidc-server/src/server.ts](scripts/docker/devops/oidc-server/src/server.ts)
- [scripts/docker/devops/overrides/ldap-no-email.yml](scripts/docker/devops/overrides/ldap-no-email.yml)
- [scripts/docker/devops/overrides/ldap-posix.yml](scripts/docker/devops/overrides/ldap-posix.yml)
- [scripts/docker/devops/overrides/pkce-confidential.yml](scripts/docker/devops/overrides/pkce-confidential.yml)
- [scripts/docker/devops/overrides/pkce-public.yml](scripts/docker/devops/overrides/pkce-public.yml)
- [scripts/docker/devops/smtp-server/Dockerfile](scripts/docker/devops/smtp-server/Dockerfile)
- [scripts/docker/devops/smtp-server/package.json](scripts/docker/devops/smtp-server/package.json)
- [scripts/docker/devops/smtp-server/pnpm-workspace.yaml](scripts/docker/devops/smtp-server/pnpm-workspace.yaml)
- [scripts/docker/devops/smtp-server/src/server.ts](scripts/docker/devops/smtp-server/src/server.ts)
- [scripts/docker/devops/smtp-server/ui/package.json](scripts/docker/devops/smtp-server/ui/package.json)
- [scripts/docker/devops/vite-dev/Dockerfile](scripts/docker/devops/vite-dev/Dockerfile)
- [scripts/gh-comment-watch/pnpm-workspace.yaml](scripts/gh-comment-watch/pnpm-workspace.yaml)
- [scripts/gh-comment-watch/web/package.json](scripts/gh-comment-watch/web/package.json)
- [scripts/mock-llm-server/dashboard/package.json](scripts/mock-llm-server/dashboard/package.json)
- [scripts/mock-llm-server/pnpm-workspace.yaml](scripts/mock-llm-server/pnpm-workspace.yaml)
- [scripts/ts-span-generator/README.md](scripts/ts-span-generator/README.md)
- [scripts/ts-span-generator/generate-spans.ts](scripts/ts-span-generator/generate-spans.ts)
- [scripts/ts-span-generator/package-lock.json](scripts/ts-span-generator/package-lock.json)
- [scripts/ts-span-generator/package.json](scripts/ts-span-generator/package.json)
- [scripts/ts-span-generator/tsconfig.json](scripts/ts-span-generator/tsconfig.json)
- [src/phoenix/server/email/sender.py](src/phoenix/server/email/sender.py)
- [src/phoenix/server/email/templates/db_disk_usage_notification.html](src/phoenix/server/email/templates/db_disk_usage_notification.html)
- [src/phoenix/server/email/templates/password_reset.html](src/phoenix/server/email/templates/password_reset.html)
- [src/phoenix/server/email/templates/welcome.html](src/phoenix/server/email/templates/welcome.html)
- [src/phoenix/server/email/types.py](src/phoenix/server/email/types.py)
- [tests/integration/server/test_db_disk_usage_monitor.py](tests/integration/server/test_db_disk_usage_monitor.py)
- [tests/unit/harbor/cassettes/test_verify/test_reference_check_grades_semantic_answers.yaml](tests/unit/harbor/cassettes/test_verify/test_reference_check_grades_semantic_answers.yaml)
- [tests/unit/harbor/test_verify.py](tests/unit/harbor/test_verify.py)

</details>



This page documents the development environment setup, tooling, and workflows for contributing to Phoenix. It covers package managers, code formatting and linting tools, testing frameworks, pre-commit hooks, and the local devops docker-compose stack (OIDC server, SMTP server, and mock LLM server) for both the Python backend and the TypeScript frontend codebases.

For details about CI/CD pipelines, testing strategy, and deployment, please see the related pages [6.3 CI/CD Pipeline](), [6.2 Testing Strategy](), and [6.5 Kubernetes Deployment]().

---

## Development Environment Overview

Phoenix is a monorepo consisting of Python and TypeScript packages, requiring separate but coordinated toolchains and workflows. A `Makefile` serves as a unified interface for common tasks across languages, simplifying developer experience [Makefile:1-112]().

### Workflow Tooling Diagram: Mapping Natural Language to Code Entities

```mermaid
graph TB
    subgraph "PythonToolchain[Python Toolchain (Code Entity Space)]"
        uv["uv (tool.uv)"]
        tox["tox (tox.ini)"]
        ruff["ruff (tool.ruff)"]
        pyright["pyright (pyrightconfig.json)"]
        pytest["pytest (tool.pytest)"]
        alembic["alembic (src/phoenix/db/migrations)"]
    end
    
    subgraph "TypeScriptToolchain[TypeScript Toolchain (Code Entity Space)]"
        pnpm["pnpm (pnpm-workspace.yaml)"]
        vite["vite (app/vite.config.ts)"]
        oxfmt["oxfmt (.oxfmtrc.jsonc)"]
        oxlint["oxlint (oxlint-app)"]
        tsc["tsc (tsconfig.json)"]
        relay["relay-compiler (relay.config.js)"]
    end
    
    subgraph "SharedEntryPoint[Shared Entry Point]"
        make["Makefile (Meta Targets)"]
    end
    
    make -- "install-python" --> uv
    make -- "test-python" --> tox
    make -- "install-node" --> pnpm
    make -- "build-frontend" --> vite
    
    style uv stroke-width:2px
    style pnpm stroke-width:2px
    style make stroke-width:2px
```

**Sources:** [DEVELOPMENT.md:25-125](), [Makefile:27-40](), [.pre-commit-config.yaml:1-62]()

---

## Python Development Tools

### Package Management: uv

Phoenix uses [uv](https://astral.sh/uv) as the primary package and workspace manager for Python dependencies. The project pins a specific `uv` version via `tool.uv.required-version` in the root `pyproject.toml` to ensure consistent environments. 

Running `uv sync --python 3.11` installs the main `arize-phoenix` package and the sub-packages (`phoenix.evals`, `phoenix.otel`, `phoenix.client`) in editable mode within an isolated virtual environment [DEVELOPMENT.md:27-89]().

Common `uv` commands used include:

| Command                                      | Description                                                                      |
|----------------------------------------------|----------------------------------------------------------------------------------|
| `uv sync --python 3.11 --all-packages`       | Installs all Python packages + workspaces in editable mode with Python 3.11      |
| `scripts/uv.sh add <package>`                | Safely adds a dependency using the pinned wrapper script                         |
| `uv lock --check`                            | Validates that the `uv.lock` matches `pyproject.toml` dependency specifications  |

The workspaces ensure that the monorepo Python sub-packages are properly linked during development to allow iterative changes without reinstallation.

### Testing & Environment Orchestration: tox

Phoenix uses `tox` to automate and isolate multiple test environments, ensuring consistency when running tests, linters, formatters, and type checks against supported Python versions and database backends [DEVELOPMENT.md:138-163]().

`tox.ini` defines numerous environments. Important ones include:
- `unit_tests`: Runs tests via `pytest`. Supports database backend selection via `--db postgresql` or SQLite [DEVELOPMENT.md:146-158]().
- `ruff`: Runs code formatting and linting using `ruff`.

`tox` isolates virtual environments per target and ensures deterministic dependency installation when running commands such as `tox run -e unit_tests`.

### Code Formatting and Linting (Python)

- `ruff` is used as the primary Python linter and formatter, configured in `pyproject.toml` under `tool.ruff`.
- Formatting is executed via the `make format-python` target [Makefile:93]().
- Linting runs via `make lint-python` [Makefile:98]().

**Sources:** [DEVELOPMENT.md:27-89, 138-163](), [Makefile:93-98](), [.pre-commit-config.yaml:4-15]()

---

## TypeScript Development Tools

### Package Management: pnpm

The frontend React SPA under `js/app/` and shared TypeScript libraries under `js/` are managed using `pnpm` (version 12.0.0 pinned) for efficient monorepo package resolution and installation [DEVELOPMENT.md:39-48]().

Typical installation commands:

```bash
# Install Node.js via nvm respecting .nvmrc
nvm install
npm i -g pnpm@12.0.0

# Install dependencies and build the frontend
cd js
pnpm install
pnpm build
```

### Build and Quality Toolchain

Phoenix's frontend development uses these tools:

```mermaid
graph LR
    subgraph "Build Process"
        relay["relay-compiler (relay.config.js)"] -- "Generates TypeScript GraphQL types" --> tsc["TypeScript (tsc)"]
        tsc -- "Compile & type check TS" --> vite["Vite (app/vite.config.ts)"]
    end
    
    subgraph "Quality Checks"
        oxfmt["oxfmt (.oxfmtrc.jsonc)"] -- "Format JS/TS/JSON/MD" --> oxlint["oxlint (package.json scripts)"]
        vitest["vitest (unit testing)"]
    end
    
    style relay stroke-width:2px
    style vite stroke-width:2px
```

- **Vite** serves as the build system and development server for the React frontend.
- **Relay Compiler** generates strongly-typed TypeScript interfaces for the GraphQL schema.
- **oxfmt** is a Rust-based formatter for JavaScript, TypeScript, and related files.
- **oxlint** is a Rust-based linter for JS/TS code style and correctness.

**Sources:** [DEVELOPMENT.md:39-48](), [.pre-commit-config.yaml:27-50]()

---

## Pre-commit Hooks

Phoenix enforces automated pre-commit hooks to uphold code quality consistently across languages. Hooks are configured in `.pre-commit-config.yaml` and will auto-run on `git commit` after installation [.pre-commit-config.yaml:1-62]().

### Pre-commit Hooks Summary

| Hook ID                             | Purpose                                                       | Implementation Detail                    |
|-----------------------------------|---------------------------------------------------------------|----------------------------------------|
| `format-python`                   | Automatically format Python files using `make format-python`  | Runs `make format-python` (ruff) [.pre-commit-config.yaml:4-8]() |
| `lint-python`                     | Lint Python code using `make lint-python`                     | Runs `make lint-python` (ruff checks) [.pre-commit-config.yaml:10-14]() |
| `clean-notebooks`                 | Strip output and metadata from Jupyter notebooks              | Runs `uv run jupyter nbconvert` [.pre-commit-config.yaml:16-25]() |
| `oxfmt-app`                      | Format frontend React app code                                 | Runs `pnpm --dir app run fmt` [.pre-commit-config.yaml:27-32]() |
| `oxfmt-js`                       | Format shared JS/TS workspace code                             | Runs `pnpm --dir js run fmt` [.pre-commit-config.yaml:33-38]() |
| `oxlint-app`                     | Lint frontend React app code                                   | Runs `pnpm --dir app run lint` [.pre-commit-config.yaml:39-44]() |
| `oxlint-js`                      | Lint shared JS/TS workspace code                               | Runs `pnpm --dir js run lint` [.pre-commit-config.yaml:45-50]() |
| `forbid-commit-to-local-main-branch` | Prevent committing directly to local `main` branch          | Bash check on branch name [.pre-commit-config.yaml:51-55]() |
| `uv-lock-check`                  | Ensure Python dependency `uv.lock` consistency                 | Runs `uv lock --check` [.pre-commit-config.yaml:56-62]() |

### Installing Pre-commit Hooks

Install the `pre-commit` tool globally via uv and enable project hooks:

```bash
uv tool install pre-commit --with pre-commit-uv
pre-commit install
```

**Sources:** [.pre-commit-config.yaml:1-62]()

---

## Local DevOps Docker-Compose Stack

Phoenix includes a local DevOps docker-compose stack (`scripts/docker/devops/docker-compose.yml`) to facilitate testing authentication, email notifications, and generative model interactions without external cloud dependencies.

### Services Overview

```mermaid
graph TB
    subgraph "LocalDevOpsStack[Local DevOps Docker-Compose Stack (Code Entity Space)]"
        oidc["OIDC Dev Server\n(scripts/docker/devops/oidc-server)"]
        smtp["SMTP Dev Server\n(scripts/docker/devops/smtp-server)"]
        mockllm["Mock LLM Server\n(scripts/mock-llm-server)"]
    end
    
    phoenixServer["Phoenix FastAPI Server\n(src/phoenix/server)"] --> oidc
    phoenixServer --> smtp
    phoenixServer --> mockllm
    
    style oidc stroke-width:2px
    style smtp stroke-width:2px
    style mockllm stroke-width:2px
```

1. **OIDC Dev Server (`scripts/docker/devops/oidc-server/`)**: Provides a lightweight Fastify-based OIDC server (`scripts/docker/devops/oidc-server/src/server.ts`) with a React user selection interface (`scripts/docker/devops/oidc-server/frontend/`) for testing authentication flows, token exchange, and JWT validation in Phoenix.
2. **SMTP Dev Server (`scripts/docker/devops/smtp-server/`)**: Implements a local SMTP server and React UI (`scripts/docker/devops/smtp-server/ui/`) that captures outgoing server emails (such as welcome messages, password resets, and database disk usage warnings generated by `SimpleEmailSender` in `src/phoenix/server/email/sender.py`) for local verification.
3. **Mock LLM Server (`scripts/mock-llm-server/`)**: Mocks OpenAI-compatible generative model endpoints to test Phoenix's playground, tracing, and evaluation subsystems locally.

**Sources:** [scripts/docker/devops/oidc-server/package.json:1-42](), [scripts/docker/devops/smtp-server/package.json:1-46](), [src/phoenix/server/email/sender.py:22-136]()

---

## Agent / AI Coding Assistant Configuration Files

Phoenix integrates support for AI-assisted development via specialized configuration files and directories controlling agent behavior and IDE integration.

### Directory Structure & Settings

- **`.agents/`**: Contains skill definitions and agent behaviors, such as `.agents/skills/phoenix-github/SKILL.md` [`.agents/skills/phoenix-github/SKILL.md:1-103`]().
- **`.claude/settings.json`**: Configures environment variables and hook commands used by the Claude AI assistant during code editing, executing automatic formatting, linting, and schema builds on file edits [`.claude/settings.json:1-38`]().
- **`.cursor/`**: Holds Cursor rules for automated code analysis, such as `.cursor/rules/python/RULE.md`.
- **`.codex/`**: Includes configuration files and bash validation scripts for the Codex AI assistant.

**Sources:** [.agents/skills/phoenix-github/SKILL.md:1-103](), [.claude/settings.json:1-38]()

---

## Makefile and Unified Commands

The `Makefile` aggregates commands across Python and TypeScript stacks, operating as the central entry point for all development tasks [Makefile:1-112]().

### Key Make Targets

| Target                     | Description                                                          |
|----------------------------|----------------------------------------------------------------------|
| `setup`                    | Performs full environment setup (Python packages + JS dependencies)  |
| `install-python`           | Installs Python dependencies using `uv`                              |
| `install-node`             | Installs Node.js dependencies using `pnpm`                           |
| `dev`                      | Runs full dev environment: Python server + frontend with hot reload  |
| `dev-backend`              | Runs backend FastAPI server only                                     |
| `dev-frontend`             | Runs frontend Vite dev server only                                   |
| `dev-docker`               | Runs local DevOps container stack                                    |
| `test`                     | Runs all tests (Python + TypeScript workspace)                       |
| `lint`                     | Lints all codebases                                                  |
| `format`                   | Formats all codebases                                                |

**Sources:** [Makefile:1-112]()

---

# Summary

Phoenix development leverages robust, modern tooling for both backend and frontend development:

| Area                      | Tool(s)                         | Key Config Files                         |
|---------------------------|--------------------------------|----------------------------------------|
| Python Package Management | `uv`                           | `pyproject.toml`, `uv.lock`             |
| Python Testing & Linting  | `tox`, `pytest`, `ruff`        | `tox.ini`, `pyproject.toml`             |
| TypeScript Package Mgmt   | `pnpm`                         | `pnpm-workspace.yaml`, `.nvmrc`         |
| TypeScript Build          | `vite`, `relay-compiler`, `tsc` | `app/vite.config.ts`, `relay.config.js`, `tsconfig.json` |
| TypeScript Lint & Format  | `oxlint`, `oxfmt`              | `.oxfmtrc.jsonc`                         |
| Pre-commit Hooks          | `pre-commit`                   | `.pre-commit-config.yaml`                |
| DevOps Environments       | Docker Compose (Postgres, OIDC, SMTP mocks) | `scripts/docker/devops/docker-compose.yml` |
| AI Agent Configurations   | `.agents/`, `.claude/`, `.cursor/`, `.codex/` | Agent skills YAML, JSON hook configs |

---

# Detailed Development Tooling Diagram: Natural Language to Code Entity Space

```mermaid
graph LR
    subgraph "Python Development Tooling"
        uv["uv\n(pyproject.toml, uv.lock)"]
        tox["tox\n(tox.ini)"]
        ruff["ruff\n(tool.ruff in pyproject.toml)"]
        pytest["pytest\n(tool.pytest in pyproject.toml)"]
        alembic["alembic\n(src/phoenix/db/migrations)"]
    end
    
    subgraph "TypeScript Development Tooling"
        pnpm["pnpm\n(pnpm-workspace.yaml, .nvmrc)"]
        vite["Vite\n(app/vite.config.ts)"]
        relay["Relay Compiler\n(relay.config.js)"]
        oxfmt["oxfmt\n(.oxfmtrc.jsonc)"]
        oxlint["oxlint\n(configured in package.json scripts)"]
    end
    
    subgraph "Pre-commit Quality Gates"
        precommit["pre-commit\n(.pre-commit-config.yaml)"]
        precommitPython["Python Hooks\n(run ruff via make targets)"]
        precommitTS["JS/TS Hooks\n(run oxfmt & oxlint via pnpm)"]
        branchCheck["Branch Protection\n(Prevent commits to local 'main')"]
    end
    
    uv --> tox
    tox --> ruff
    tox --> pytest
    pnpm --> vite
    pnpm --> relay
    oxfmt --> oxlint
    precommit --> precommitPython
    precommit --> precommitTS
    precommit --> branchCheck
```

**Sources:** [DEVELOPMENT.md:25-125](), [.pre-commit-config.yaml:1-62](), [Makefile:1-112]()

# End of Development Workflow & Tooling Page

---

# Page: Testing Strategy

# Testing Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-evals/references/integrations-pytest.md](.agents/skills/phoenix-evals/references/integrations-pytest.md)
- [.agents/skills/phoenix-evals/references/integrations-vitest-jest.md](.agents/skills/phoenix-evals/references/integrations-vitest-jest.md)
- [docs/phoenix/datasets-and-experiments/how-to-experiments.mdx](docs/phoenix/datasets-and-experiments/how-to-experiments.mdx)
- [docs/phoenix/datasets-and-experiments/how-to-experiments/eval-ci-with-pytest.mdx](docs/phoenix/datasets-and-experiments/how-to-experiments/eval-ci-with-pytest.mdx)
- [docs/phoenix/datasets-and-experiments/how-to-experiments/how-to-dataset-evaluators.mdx](docs/phoenix/datasets-and-experiments/how-to-experiments/how-to-dataset-evaluators.mdx)
- [docs/phoenix/datasets-and-experiments/how-to-experiments/running-experiments-in-background.mdx](docs/phoenix/datasets-and-experiments/how-to-experiments/running-experiments-in-background.mdx)
- [docs/phoenix/datasets-and-experiments/how-to-experiments/running-experiments.mdx](docs/phoenix/datasets-and-experiments/how-to-experiments/running-experiments.mdx)
- [docs/phoenix/evaluation/how-to-evals/code-evaluators.mdx](docs/phoenix/evaluation/how-to-evals/code-evaluators.mdx)
- [docs/phoenix/evaluation/integrations/pytest.mdx](docs/phoenix/evaluation/integrations/pytest.mdx)
- [docs/phoenix/evaluation/integrations/vitest-jest.mdx](docs/phoenix/evaluation/integrations/vitest-jest.mdx)
- [docs/phoenix/evaluation/server-evals/builtin-evaluators.mdx](docs/phoenix/evaluation/server-evals/builtin-evaluators.mdx)
- [docs/phoenix/evaluation/server-evals/input-mapping.mdx](docs/phoenix/evaluation/server-evals/input-mapping.mdx)
- [docs/phoenix/evaluation/server-evals/llm-evaluators.mdx](docs/phoenix/evaluation/server-evals/llm-evaluators.mdx)
- [docs/phoenix/evaluation/server-evals/overview.mdx](docs/phoenix/evaluation/server-evals/overview.mdx)
- [docs/phoenix/release-notes/03-2025/03-20-2025-delete-experiment-from-action-menu.mdx](docs/phoenix/release-notes/03-2025/03-20-2025-delete-experiment-from-action-menu.mdx)
- [docs/phoenix/release-notes/04-2026/04-22-2026-secrets-ui-and-evaluator-trace-id.mdx](docs/phoenix/release-notes/04-2026/04-22-2026-secrets-ui-and-evaluator-trace-id.mdx)
- [docs/phoenix/release-notes/08-2026/08-12-2026-session-filters-rest-api-and-endpoint-config.mdx](docs/phoenix/release-notes/08-2026/08-12-2026-session-filters-rest-api-and-endpoint-config.mdx)
- [docs/phoenix/tracing/how-to-tracing/feedback-and-annotations/evaluating-phoenix-traces.mdx](docs/phoenix/tracing/how-to-tracing/feedback-and-annotations/evaluating-phoenix-traces.mdx)
- [requirements/integration-tests.txt](requirements/integration-tests.txt)
- [src/phoenix/db/helpers.py](src/phoenix/db/helpers.py)
- [src/phoenix/db/insertion/span.py](src/phoenix/db/insertion/span.py)
- [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py](src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py)
- [src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py](src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/integration/conftest.py](tests/integration/conftest.py)
- [tests/integration/db_migrations/__init__.py](tests/integration/db_migrations/__init__.py)
- [tests/integration/db_migrations/conftest.py](tests/integration/db_migrations/conftest.py)
- [tests/integration/db_migrations/test_data_migration_4ded9e43755f_create_project_sessions_table.py](tests/integration/db_migrations/test_data_migration_4ded9e43755f_create_project_sessions_table.py)
- [tests/integration/db_migrations/test_db_schema_6a88424799fe_update_users_with_auth_method.py](tests/integration/db_migrations/test_db_schema_6a88424799fe_update_users_with_auth_method.py)
- [tests/integration/db_migrations/test_db_schema_a20694b15f82_cost.py](tests/integration/db_migrations/test_db_schema_a20694b15f82_cost.py)
- [tests/integration/db_migrations/test_db_schema_for_annotations.py](tests/integration/db_migrations/test_db_schema_for_annotations.py)
- [tests/integration/db_migrations/test_up_and_down_migrations.py](tests/integration/db_migrations/test_up_and_down_migrations.py)
- [tests/integration/project_sessions/test_project_sessions.py](tests/integration/project_sessions/test_project_sessions.py)
- [tests/integration/server/test_launch_app.py](tests/integration/server/test_launch_app.py)
- [tests/unit/conftest.py](tests/unit/conftest.py)
- [tests/unit/db/insertion/test_span.py](tests/unit/db/insertion/test_span.py)
- [tests/unit/server/test_app_docs_mcp_lifespan.py](tests/unit/server/test_app_docs_mcp_lifespan.py)
- [tests/unit/server/test_app_evaluations.py](tests/unit/server/test_app_evaluations.py)
- [tests/unit/server/test_app_fastapi_dependants.py](tests/unit/server/test_app_fastapi_dependants.py)
- [tests/unit/server/test_app_fastapi_type_adapters.py](tests/unit/server/test_app_fastapi_type_adapters.py)
- [tests/unit/server/test_app_graphql_schema_build.py](tests/unit/server/test_app_graphql_schema_build.py)
- [tests/unit/server/test_app_routers.py](tests/unit/server/test_app_routers.py)

</details>



## Purpose and Scope

This document describes Phoenix's comprehensive testing approach, covering unit tests, integration tests, end-to-end (E2E) tests, database fixtures, test organization, and CI/CD integration. Phoenix employs a robust multi-layered testing strategy to guarantee quality, reliability, and compatibility across all components.

The scope includes testing methodologies for server code, client libraries, database migrations, SDK compatibility, and frontend web UI with detailed attention to both SQLite and PostgreSQL backends.

For related information on automation, see [CI/CD Pipeline (6.3)]() and for release processes, see [Release Management (6.4)]().

Sources: [tests/unit/conftest.py:1-187](), [tests/integration/conftest.py:1-206]()

## Test Types and Scope

Phoenix testing is stratified by scope and coverage with specialized tools for each layer:

| Test Type | Scope | Tools | Execution Details |
|---|---|---|---|
| **Unit Tests** | Isolated component logic in server and packages | `pytest`, `pytest-xdist` | Parallel runs on SQLite and PostgreSQL databases. |
| **Integration Tests**| Client-server interaction, GraphQL subscriptions, DB migrations | `pytest`, `httpx`, `tox` | Full stack with database (SQLite/PostgreSQL) |
| **E2E Tests** | Complete user workflows including UI interactions | Playwright | Browser automation with Chromium and Firefox |
| **Type Checking** | Static typing verification | `mypy`, `pyright`, TypeScript compiler | Pre-commit hooks and CI runs |
| **Package Tests** | Component package verification (client, evals, otel) | `tox`, `pytest` | Isolated testing environments per package |
| **Canary Tests** | Third-party LLM SDK compatibility (OpenAI, Anthropic, Google) | `tox`, `pytest` | Dedicated environment for SDK integration checks |
| **Migration Tests** | Database schema and data migration evolution | Alembic | Forward and backward migration verification |

Sources: [tox.ini:11-165](), [.github/workflows/python-CI.yml:114-183](), [.github/workflows/playwright.yaml:44-135]()

## Test Organization and Structure

### Directory Layout

Phoenix organizes tests into the following directory structure to separate concerns and test scope:

```
tests/
├── unit/                  # Server-side unit tests focusing on isolated components
├── integration/           # Full stack, migration, and interaction tests
│   ├── db_migrations/     # Alembic migration validation tests
│   ├── project_sessions/  # Session grouping and project session logic
│   └── server/            # Server app lifecycle and feature tests
packages/
├── phoenix-client/tests/  # SDK client library unit and integration tests
├── phoenix-evals/tests/   # Evaluation framework tests
└── phoenix-otel/tests/    # OpenTelemetry integration tests
js/app/tests/              # Frontend Playwright end-to-end tests
```

### E2E Test Configuration with Playwright

End-to-end tests target user workflows including Playground, Datasets, Prompts, and Evaluators. Configured in `js/app/playwright.config.ts`, these tests launch a local server via `pnpm run dev:server:test`.

**Key points:**

- Authentication is managed in `js/app/tests/auth.setup.ts`.
- Authenticated state snapshots are stored under `js/app/playwright/.auth/admin.json` for session reuse.
- Sandboxed evaluation environments require Deno (TypeScript) and CPython WASM for code execution in evaluators. The `Dockerfile` and `.github/workflows/playwright.yaml` ensure these runtimes are available. [Dockerfile:74-117](), [.github/workflows/playwright.yaml:115-134]()
- Playwright tests run on Chromium and Firefox, skipping WebKit for stability in CI environments. [.github/workflows/playwright.yaml:55-56]()

Sources: [.github/workflows/playwright.yaml:44-135]()

## Database Fixture Strategy

Phoenix tests support dual backends: SQLite and PostgreSQL. The CI matrix ensures thorough compatibility and coverage on both. Database fixtures and test data reuse centralized schemas and models with real data flows.

### Span Insertion as Core Database Interaction

A critical component tested is the `insert_span` async function in [src/phoenix/db/insertion/span.py:128-188](). This method performs:

- Lookup or creation of Trace records based on `trace_id`. [src/phoenix/db/insertion/span.py:135-156]()
- Project association by project name. [src/phoenix/db/insertion/span.py:142-144]()
- Session grouping using `session_id` attributes in spans. [src/phoenix/db/insertion/span.py:161-188]()
- Insertion of Span records with conflict handling via upsert semantics. [src/phoenix/db/insertion/span.py:104-122]()

This method integrates several SQLAlchemy models (`Trace`, `ProjectSession`, `Span`) and uses helper functions such as `insert_on_conflict` for upsert logic.

```mermaid
graph TD
    subgraph "Natural Language Space"
        NL_SpanData["OpenTelemetry Span Data"]
        NL_ProjectName["Project Name"]
        NL_SessionID["Session ID (optional)"]
    end

    subgraph "Code Entity Space"
        A[src/phoenix/db/insertion/span.py:insert_span()]
        B[phoenix.db.models.Trace]
        C[phoenix.db.models.Project]
        D[phoenix.db.models.ProjectSession]
        E[phoenix.db.models.Span]
        F[phoenix.db.insertion.helpers.insert_on_conflict()]
        G[sqlalchemy.ext.asyncio.AsyncSession]
    end

    NL_SpanData --> A
    NL_ProjectName --> A
    NL_SessionID --> A

    A -- "Select or Create Trace" --> B
    A -- "Select or Create Project" --> C
    A -- "Select or Create ProjectSession" --> D
    A -- "Prepare Span Data" --> E
    A -- "Insert/Update Span" --> F
    F -- "Execute SQL" --> G

    B -- "Update Trace Times" --> A
    D -- "Update Session Times" --> A
    E -- "Calculate Cumulative Metrics" --> A
```

Sources: [src/phoenix/db/insertion/span.py:128-188]()

## Migration Testing

Phoenix ensures database migrations are reliable and reversible through migration tests located under `tests/integration/db_migrations/`.

**Key points:**

- Upgrade and downgrade operations through Alembic migrations are tested for schema integrity [tests/integration/db_migrations/test_up_and_down_migrations.py:31-80]().
- Data migration scripts such as `populate_project_sessions.py` ensure that changes like grouping traces into sessions preserve data correctness [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py:1-150]().
- Migration tests run on both SQLite and Postgres backend matrix to verify multi-DB compatibility [tests/integration/db_migrations/test_up_and_down_migrations.py:17-30]().

```mermaid
sequenceDiagram
  participant Alembic as "alembic.command"
  participant DB as "sqlalchemy.ext.asyncio.AsyncEngine"
  participant Test as "tests.integration.db_migrations.test_up_and_down_migrations"

  Test->>Alembic: "command.upgrade(config, 'head')"
  Alembic->>DB: "Apply all migrations"
  Test->>DB: "_verify_clean_state()"
  Test->>Alembic: "command.downgrade(config, 'base')"
  Alembic->>DB: "Rollback all migrations"

  loop "For each revision pair (a, b)"
    Test->>Alembic: "command.upgrade(config, b.revision)"
    Alembic->>DB: "Apply migration step"
    Test->>Alembic: "command.downgrade(config, a.revision)"
    Alembic->>DB: "Rollback migration step"
  end
```

Sources: [tests/integration/db_migrations/test_up_and_down_migrations.py:31-80](), [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py:1-150]()

## Package and Canary Testing

Phoenix uses `tox` to create isolated environments for running package-specific tests in parallel. This covers the Python client, evaluation framework, and OpenTelemetry SDK integration.

```mermaid
graph TD
    subgraph "Python Package Tests"
        A[tox -e phoenix_client] --> B[packages/phoenix-client/tests/]
        C[tox -e phoenix_evals] --> D[packages/phoenix-evals/tests/]
        E[tox -e phoenix_otel] --> F[packages/phoenix-otel/tests/]
    end

    subgraph "Canary Tests (SDK Compatibility)"
        G[tox -e phoenix_client_canary_tests_sdk_openai] --> H[packages/phoenix-client/tests/canary/sdk/openai/]
        I[tox -e phoenix_client_canary_tests_sdk_anthropic] --> J[packages/phoenix-client/tests/canary/sdk/anthropic/]
        K[tox -e phoenix_client_canary_tests_sdk_google_genai] --> L[packages/phoenix-client/tests/canary/sdk/google_genai/]
    end

    B -- "pytest, mypy, pyright" --> M[Python Client Functionality]
    D -- "pytest, mypy" --> N[Evals Framework Functionality]
    F -- "pytest, mypy" --> O[OTel Integration Functionality]

    H -- "pytest, mypy, pyright" --> P[OpenAI SDK Compatibility]
    J -- "pytest, mypy, pyright" --> Q[Anthropic SDK Compatibility]
    L -- "pytest, mypy, pyright" --> R[Google GenAI SDK Compatibility]
```

Sources: [tox.ini:11-125]()

## Mock LLM Server

For integration and unit tests involving language model clients, Phoenix uses mock implementations that simulate real LLM APIs without network calls. This is essential to:

- Provide deterministic and fast test runs.
- Avoid dependency on external network availability.
- Emulate streaming APIs compatible with client interfaces.

Sources: [tests/integration/_mock_llm_server.py]()

## Canary Tests for SDK Integration

Canary tests are dedicated suites that ensure Phoenix's compatibility with third-party LLM SDKs and API clients:

- OpenAI SDK
- Anthropic SDK
- Google Generative AI SDK

These tests run the minimal client lifecycle operations and verify instrumentation hooks. They validate proper error handling, concurrency, and tracing behavior in isolation from other tests.

Sources: [tox.ini:24-103]()

## End-to-End Test Scenarios

Phoenix's frontend E2E tests cover key user interactions:

### Server Evaluators Workflow

- Create a new dataset
- Add an example trace manually
- Attach a prebuilt LLM or Code Evaluator
- Run evaluations and verify score computations

### Prompt Lifecycle

Tests creating and saving prompts in the Playground, version creation, and version history verification to ensure prompt lifecycle management is robust.

### User & Access Management

Role-Based Access Control (RBAC) is verified by tests covering admin, member, and viewer roles across different projects [tests/integration/server/test_launch_app.py:22-37]().

Sources: [tests/integration/server/test_launch_app.py:22-37]()

## Code Entity Association Diagram

This diagram maps Phoenix's natural language features to their key code implementations and associated tests. It bridges human-meaningful features to the actual code entities and test scripts, providing quick navigation and understanding of the test coverage landscape.

```mermaid
graph TD
    subgraph "Natural Language Space"
        NL_SpanIngestion["Span Ingestion & Persistence"]
        NL_ProjectSessions["Project Sessions Grouping"]
        NL_MigrationSafety["Database Migration Safety"]
        NL_SDKCompatibility["Third-Party SDK Compatibility"]
        NL_AppLaunch["Application Lifecycle & Auth"]
    end

    subgraph "Code Entity Space"
        CE_InsertSpan["src/phoenix/db/insertion/span.py:insert_span()"]
        CE_ProjectSessionScript["src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py"]
        CE_AlembicMigrations["tests/integration/db_migrations/test_up_and_down_migrations.py"]
        CE_CanaryToxEnv["tox.ini:phoenix_client_canary_tests_sdk_*"]
        CE_LaunchAppTest["tests/integration/server/test_launch_app.py:TestLaunchApp"]
    end

    subgraph "Test Suites & Files"
        TS_IntegrationSpan["tests/integration/server/test_launch_app.py"]
        TS_ProjectSessionTests["tests/integration/project_sessions/test_project_sessions.py"]
        TS_MigrationTests["tests/integration/db_migrations/test_up_and_down_migrations.py"]
        TS_CanaryTests["packages/phoenix-client/tests/canary/sdk/"]
    end

    NL_SpanIngestion --> CE_InsertSpan
    CE_InsertSpan --> TS_IntegrationSpan

    NL_ProjectSessions --> CE_ProjectSessionScript
    CE_ProjectSessionScript --> TS_ProjectSessionTests

    NL_MigrationSafety --> CE_AlembicMigrations
    CE_AlembicMigrations --> TS_MigrationTests

    NL_SDKCompatibility --> CE_CanaryToxEnv
    CE_CanaryToxEnv --> TS_CanaryTests

    NL_AppLaunch --> CE_LaunchAppTest
    CE_LaunchAppTest --> TS_IntegrationSpan
```

Sources: [src/phoenix/db/insertion/span.py:128-188](), [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py:1-150](), [tests/integration/db_migrations/test_up_and_down_migrations.py:31-80](), [tox.ini:24-103](), [tests/integration/server/test_launch_app.py:1-231]()

# Summary

Phoenix's testing strategy integrates multiple layers of testing rigor:

- Isolated unit tests with db backend combo coverage
- Integration tests that exercise full paths including ingestion and session logic
- Migration testing to safely evolve schema and data
- Canary and package tests for third-party SDK reliability
- End-to-end Playwright tests for real-user flows in frontend UI

This multi-faceted approach ensures the system's resilience, correctness, and ease of maintenance.

# References

- [.github/workflows/python-CI.yml:114-183]()
- [.github/workflows/playwright.yaml:44-135]()
- [tox.ini:11-165]()
- [src/phoenix/db/insertion/span.py:128-188]()
- [tests/integration/db_migrations/test_up_and_down_migrations.py:31-80]()
- [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py:1-150]()
- [tests/integration/_mock_llm_server.py]()
- [tests/integration/server/test_launch_app.py:1-231]()
- [tests/unit/conftest.py:1-187]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-docs-gap-audit/SKILL.md](.agents/skills/phoenix-docs-gap-audit/SKILL.md)
- [.eslintignore](.eslintignore)
- [.github/.scripts/collect-customer-issues.js](.github/.scripts/collect-customer-issues.js)
- [.github/actions/approve-automation-pr/action.yml](.github/actions/approve-automation-pr/action.yml)
- [.github/actions/docker-build-image/action.yml](.github/actions/docker-build-image/action.yml)
- [.github/actions/docker-merge-manifest/action.yml](.github/actions/docker-merge-manifest/action.yml)
- [.github/workflows/auto-label-external-issues.yaml](.github/workflows/auto-label-external-issues.yaml)
- [.github/workflows/check-card-links.yml](.github/workflows/check-card-links.yml)
- [.github/workflows/check-dependabot-uv-version.yml](.github/workflows/check-dependabot-uv-version.yml)
- [.github/workflows/claude-code-review.yml](.github/workflows/claude-code-review.yml)
- [.github/workflows/claude-docs-gap-audit.yml](.github/workflows/claude-docs-gap-audit.yml)
- [.github/workflows/claude-implement-issue.yml](.github/workflows/claude-implement-issue.yml)
- [.github/workflows/claude-issue-triage.yml](.github/workflows/claude-issue-triage.yml)
- [.github/workflows/claude-llms-txt.yml](.github/workflows/claude-llms-txt.yml)
- [.github/workflows/claude-readme-translations.yml](.github/workflows/claude-readme-translations.yml)
- [.github/workflows/claude-release-notes.yml](.github/workflows/claude-release-notes.yml)
- [.github/workflows/claude-skills-audit.yml](.github/workflows/claude-skills-audit.yml)
- [.github/workflows/claude-weekly-deps-upgrade.yml](.github/workflows/claude-weekly-deps-upgrade.yml)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)
- [.github/workflows/collect-customer-issues.yaml](.github/workflows/collect-customer-issues.yaml)
- [.github/workflows/cost-sync.yml](.github/workflows/cost-sync.yml)
- [.github/workflows/daily-skills-update.yml](.github/workflows/daily-skills-update.yml)
- [.github/workflows/docker-build-experimental.yml](.github/workflows/docker-build-experimental.yml)
- [.github/workflows/docker-build-nightly.yml](.github/workflows/docker-build-nightly.yml)
- [.github/workflows/docker-build-release.yml](.github/workflows/docker-build-release.yml)
- [.github/workflows/generate-sitemap.yml](.github/workflows/generate-sitemap.yml)
- [.github/workflows/gh_pages.yml](.github/workflows/gh_pages.yml)
- [.github/workflows/helm-ci.yml](.github/workflows/helm-ci.yml)
- [.github/workflows/openapi-schema.yaml](.github/workflows/openapi-schema.yaml)
- [.github/workflows/phoenix-sqlean-upstream.yml](.github/workflows/phoenix-sqlean-upstream.yml)
- [.github/workflows/playwright.yaml](.github/workflows/playwright.yaml)
- [.github/workflows/plugin-evals.yml](.github/workflows/plugin-evals.yml)
- [.github/workflows/publish.yaml](.github/workflows/publish.yaml)
- [.github/workflows/pull-requests.yaml](.github/workflows/pull-requests.yaml)
- [.github/workflows/pypi-smoke-test.yml](.github/workflows/pypi-smoke-test.yml)
- [.github/workflows/python-CI.yml](.github/workflows/python-CI.yml)
- [.github/workflows/python-all-platforms.yml](.github/workflows/python-all-platforms.yml)
- [.github/workflows/storybook-CI.yml](.github/workflows/storybook-CI.yml)
- [.github/workflows/sync-lockfile-release-pr.yml](.github/workflows/sync-lockfile-release-pr.yml)
- [.github/workflows/typescript-CI.yml](.github/workflows/typescript-CI.yml)
- [.github/workflows/typescript-packages-publish-experimental.yml](.github/workflows/typescript-packages-publish-experimental.yml)
- [.github/workflows/typescript-packages-publish.yml](.github/workflows/typescript-packages-publish.yml)
- [.github/workflows/update-phoenix-package-versions.yml](.github/workflows/update-phoenix-package-versions.yml)
- [.nvmrc](.nvmrc)
- [Dockerfile](Dockerfile)
- [packages/phoenix-sqlean/.gitignore](packages/phoenix-sqlean/.gitignore)
- [packages/phoenix-sqlean/MANIFEST.in](packages/phoenix-sqlean/MANIFEST.in)
- [packages/phoenix-sqlean/README.md](packages/phoenix-sqlean/README.md)
- [packages/phoenix-sqlean/scripts/check-upstream.sh](packages/phoenix-sqlean/scripts/check-upstream.sh)
- [scripts/docker/devops/Dockerfile](scripts/docker/devops/Dockerfile)

</details>



This page documents Phoenix's continuous integration and continuous deployment infrastructure. It covers GitHub Actions workflows for testing, code generation validation, Docker image builds, TypeScript package publishing, and automated releases. For detailed release versioning and publishing processes, refer to [Release Management](#6.4). For Docker image variants and deployment configuration, refer to [Kubernetes Deployment](#6.5).

---

## Overview

Phoenix uses GitHub Actions as the primary platform to implement CI/CD workflows. Key features include:

- **Change filtering**: selective job execution based on affected file paths to optimize CI resource usage.
- **Matrix testing** across Python versions, platforms, and databases for broad compatibility.
- **Integration of style and static analysis tools**: `mypy`, `pyright`, `ruff`, ESLint, and Prettier.
- **End-to-end tests** with Playwright and sandbox runtime provisioning.
- **Multi-architecture Docker image builds** with deployment manifest updates and PR automation.
- **TypeScript package versioning and publishing** driven by `changesets`.
- **Claude AI agentic workflows** for automated code reviews and issue implementation.
- **Quality gates** to enforce strict passing of tests and checks before merge/deploy.

All workflows use concurrency groups with cancellation of in-progress runs on new pushes, minimizing queue bloat and accelerating feedback `[.github/workflows/python-CI.yml:14-16]()`.

---

## Pipeline Architecture

The overall CI/CD system structure is visualized below, bridging natural language workflow concepts to concrete workflow files and execution commands.

```mermaid
graph TB
    %% Triggers
    subgraph "Triggers"
        PushMain["push: main, version-*"]
        PullRequest["pull_request"]
        TagRelease["push: tags/arize-phoenix-v*"]
        Schedule["schedule: cron"]
        WorkflowDispatch["workflow_dispatch"]
        IssueLabeled["issues: labeled (good-agent-issue)"]
    end
    
    %% GitHub Workflows
    subgraph "GitHub Actions Workflows"
        PythonCI["python-CI.yml"]
        TS_CI["typescript-CI.yml"]
        PlaywrightWF["playwright.yaml"]
        DockerRelease["docker-build-release.yml"]
        DockerNightly["docker-build-nightly.yml"]
        DockerExperimental["docker-build-experimental.yml"]
        ClaudeReview["claude-code-review.yml"]
        ClaudeImplement["claude-implement-issue.yml"]
        PublishPython["publish.yaml"]
        TS_Publish["typescript-packages-publish.yml"]
        TS_PublishExperimental["typescript-packages-publish-experimental.yml"]
        PythonAllPlatforms["python-all-platforms.yml"]
    end
    
    %% Execution Layer
    subgraph "Execution Layer (Tox/UV/PNPM Commands)"
        ToxEnv["tox environments"]
        UVsync["uv sync / uvx commands"]
        PNPMrun["pnpm run commands"]
        PyTest["pytest unit/integration tests"]
        MyPy["mypy --strict type checks"]
        Pyright["pyright TS type checks"]
        PlaywrightTest["playwright end-to-end tests"]
        Lint["ruff / oxlint / ESLint / formatting checks"]
    end

    %% Quality Gates and Build Processes
    subgraph "Quality Gates & Build Processes"
        RunTests["Test Suites Execution"]
        TypeCheck["Static Type Analysis"]
        CodeFormat["Code Formatting & Linting"]
        DockerBuild["Multi-arch Docker Build & Publish"]
        KustomizeHelmUpdate["Update Deployment Manifests"]
        PRCreation["Create PR for version bump"]
        PublishPyPI["Publish Python Packages to PyPI"]
        PublishNPM["Publish TypeScript Packages to NPM"]
    end
    
    %% Links
    PushMain --> PythonCI
    PullRequest --> PythonCI
    PullRequest --> ClaudeReview
    PushMain --> PlaywrightWF
    Schedule --> PlaywrightWF
    TagRelease --> DockerRelease
    WorkflowDispatch --> PublishPython
    PushMain --> TS_CI
    PushMain --> TS_Publish
    PushMain --> DockerNightly
    IssueLabeled --> ClaudeImplement
    WorkflowDispatch --> TS_PublishExperimental
    Schedule --> PythonAllPlatforms
    WorkflowDispatch --> PythonAllPlatforms

    PythonCI --> ToxEnv
    ToxEnv --> PyTest
    ToxEnv --> MyPy
    ToxEnv --> Pyright
    
    TS_CI --> PNPMrun
    PNPMrun --> Lint
    PNPMrun --> Pyright
    
    PlaywrightWF --> UVsync
    PlaywrightWF --> PlaywrightTest
    
    DockerRelease --> DockerBuild
    DockerBuild --> KustomizeHelmUpdate
    KustomizeHelmUpdate --> PRCreation

    DockerNightly --> DockerBuild
    DockerExperimental --> DockerBuild
    
    PublishPython --> PublishPyPI
    TS_Publish --> PublishNPM
    TS_PublishExperimental --> PublishNPM

    PythonAllPlatforms --> RunTests
```

**Sources:**  
`[.github/workflows/python-CI.yml:5-46,105-175]()`  
`[.github/workflows/typescript-CI.yml:5-93]()`  
`[.github/workflows/playwright.yaml:5-138]()`  
`[.github/workflows/docker-build-release.yml:1-137]()`  
`[.github/workflows/docker-build-nightly.yml:1-105]()`  
`[.github/workflows/docker-build-experimental.yml]()`  
`[.github/workflows/claude-code-review.yml:1-69]()`  
`[.github/workflows/claude-implement-issue.yml:1-152]()`  
`[.github/workflows/publish.yaml:1-220]()`  
`[.github/workflows/typescript-packages-publish.yml:1-68]()`  
`[.github/workflows/typescript-packages-publish-experimental.yml]()`  
`[.github/workflows/python-all-platforms.yml:5-171]()`  
`tox.ini:1-165`  

---

## Python CI Pipeline

The `python-CI.yml` workflow is the main Python backend testing pipeline. It runs on `push` events to `main` and `version-*` branches, pull requests, and manual triggers `[.github/workflows/python-CI.yml:5-12]`.

### Change Detection and Conditional Execution

A dedicated `changes` job uses `dorny/paths-filter` to detect modifications in targeted files and directories, enabling selective test execution.

The change filters include keys such as:

| Output Key | Path Globs |
| :--- | :--- |
| `ipynb` | `"**/*.ipynb"` `[.github/workflows/python-CI.yml:54-55]` |
| `prompts` | `prompts/**, scripts/prompts/compile_python_prompts.py` `[.github/workflows/python-CI.yml:56-58]` |
| `phoenix` | `evals/**, src/**, tests/**, tutorials/**, pyproject.toml, tox.ini` `[.github/workflows/python-CI.yml:59-65]` |
| `phoenix_client` | `packages/phoenix-client/**, tox.ini` `[.github/workflows/python-CI.yml:66-68]` |
| `phoenix_evals` | `packages/phoenix-evals/**, tox.ini` `[.github/workflows/python-CI.yml:69-71]` |
| `phoenix_otel` | `packages/phoenix-otel/**, tox.ini` `[.github/workflows/python-CI.yml:72-74]` |
| `migrations` | `src/phoenix/db/migrations/versions/**` `[.github/workflows/python-CI.yml:75-76]` |
| `ddl` | `src/phoenix/db/migrations/**, src/phoenix/db/ddl/*.sql, scripts/ddl/**` `[.github/workflows/python-CI.yml:77-80]` |
| `json_canonicalization_schema` | `src/phoenix/vendor/json_canonicalization_scheme/**/*.py` `[.github/workflows/python-CI.yml:81-82]` |
| `uv_lock` | `"**/pyproject.toml", uv.lock` `[.github/workflows/python-CI.yml:83-85]` |

Downstream jobs only run if their corresponding change flag is `true` `[.github/workflows/python-CI.yml:23-46]`.

**Sources:**
`[.github/workflows/python-CI.yml:5-12]()`
`[.github/workflows/python-CI.yml:14-16]()`
`[.github/workflows/python-CI.yml:23-46]()`
`[.github/workflows/python-all-platforms.yml:5-171]()`

---

## TypeScript CI Pipeline

The `typescript-CI.yml` workflow triggers on pushes and pull requests to main branches, running ESLint, Prettier, `pyright` type checks, code generation validation, and Jest tests `[.github/workflows/typescript-CI.yml:5-93]`.

### Change Detection

This pipeline employs `dorny/paths-filter` to detect changes in TypeScript-related files including `js/**`, `schemas/**`, and configuration files `[.github/workflows/typescript-CI.yml:23-40]`.

### Steps

It installs dependencies via `pnpm`, builds in topological order, verifies zero-drift in OpenAPI code generation via `pnpm run generate:openapi`, schema generative UI codegen, and UI message stream fixtures `[.github/workflows/typescript-CI.yml:61-98]`.

**Sources:**
`[.github/workflows/typescript-CI.yml:5-93]()`
`[.github/workflows/typescript-CI.yml:23-40]()`
`[.github/workflows/typescript-CI.yml:61-98]()`

---

## Playwright End-to-End Testing

Playwright tests run using the `playwright.yaml` workflow triggered on pushes, pull requests, scheduled runs, and manually `[.github/workflows/playwright.yaml:5-16]`.

### Sandbox Runtime Setup

This pipeline sets up runtime dependencies required by Phoenix's sandbox environments:
- **Playwright browsers**: Installed via `pnpm exec playwright install --with-deps` `[.github/workflows/playwright.yaml:153]`.
- **CPython WebAssembly binary & Deno runtime**: Provisioned for containerized sandbox testing.

### Execution

Tests run inside the `./js/app` working directory with Playwright commands using custom runners `[.github/workflows/playwright.yaml:104-122]`. WebKit is conditionally skipped due to caching issues `[.github/workflows/playwright.yaml:115]`.

**Sources:**
`[.github/workflows/playwright.yaml:5-138]()`
`[.github/workflows/playwright.yaml:104-122]()`

---

## Docker Build & Deployment Automation

Phoenix builds and publishes Docker images for deployment using multi-stage Docker builds and corresponding GitHub workflows.

```mermaid
graph LR
    %% Build Stages
    subgraph "Docker Build Stages (Dockerfile)"
        FB["frontend-builder (node:24-slim)"]
        BB["backend-builder (uv image + Python)"]
        WR["wasm-runtime: CPython WASM downloader"]
        DB["distroless final image"]
    end
    
    FB --> BB
    BB --> WR
    WR --> DB
    
    %% Release Workflow
    subgraph "Docker Build & Release Workflow"
        VersionExtract["Extract version from git tag"]
        BuildJobs["Build multi-arch per platform"]
        PublishManifest["Publish manifest for variants"]
        UpdateDeployment["Update kustomize and helm manifests"]
        PRCreation["Create Pull Request for manifest updates"]
    end

    subgraph "Docker Build & Nightly/Experimental Workflow"
        BuildJobsNightly["Build multi-arch per platform (Nightly/Experimental)"]
        PublishManifestNightly["Publish manifest for variants (Nightly/Experimental)"]
    end
    
    TagRelease --> VersionExtract
    VersionExtract --> BuildJobs
    BuildJobs --> PublishManifest
    PublishManifest --> UpdateDeployment
    UpdateDeployment --> PRCreation
    
    PushMain --> BuildJobsNightly
    BuildJobsNightly --> PublishManifestNightly

    DB -.-> DockerHub["Docker Hub arizephoenix/phoenix"]
    DockerHub -.-> BuildJobs
    DockerHub -.-> BuildJobsNightly
```

### Multi-Stage Dockerfile

- **Frontend Builder**: Uses `node:24-slim` to execute `pnpm install` and build frontend React bundles under `/phoenix/src/phoenix/server/static` `[Dockerfile:31-47]()`.
- **Backend Builder**: Based on a pinned `uv` image, copies Python source, runs `uv sync` with container and Postgres extras, builds the Python wheel and installs it `[Dockerfile:48-65]()`.
- **WASM Runtime Stage**: Downloads the CPython wasm binary with retries and SHA-256 checksum validation to ensure safe sandbox runtime usage `[Dockerfile:101-117]()`.
- **Final Stage**: Uses a distroless base image, bundles the `.venv` Python environment, built frontend assets, and sandbox runtimes (Deno binary and CPython wasm binary) `[Dockerfile:118-153]()`.

### Docker Build and Publish Workflows

- **Release (`docker-build-release.yml`)**: Triggers on push to tags matching `arize-phoenix-v*`. It extracts the version, then builds images for multiple CPU architectures (`linux/amd64`, `linux/arm64`) and Docker variants (`root`, `nonroot`, `debug`) `[.github/workflows/docker-build-release.yml:5-126]()`.
- **Nightly (`docker-build-nightly.yml`)**: Triggers on pushes to `main` and `version-*` branches.
- **Experimental (`docker-build-experimental.yml`)**: Manually dispatched workflow building experimental variants.

### Deployment Manifest Update

After a release build, Python scripts `scripts/update_kustomize.py` and `scripts/update_helm.py` update Kubernetes and Helm manifests with the new image versions, pushing a pull request automatically via `peter-evans/create-pull-request` `[.github/workflows/docker-build-release.yml:130-170]()`.

**Sources:**
`[Dockerfile:31-47]()`
`[Dockerfile:48-65]()`
`[Dockerfile:101-117]()`
`[Dockerfile:118-153]()`
`[.github/workflows/docker-build-release.yml:5-126]()`
`[.github/workflows/docker-build-release.yml:130-170]()`
`[scripts/update_kustomize.py]()`
`[scripts/update_helm.py]()`

---

## TypeScript Package Publishing

TypeScript packages under the `js/` directory use ChangeSets for versioning and publishing via `.github/workflows/typescript-packages-publish.yml` `[.github/workflows/typescript-packages-publish.yml:1-68]()`.

- Checks out the repository with full history.
- Sets up Node.js and PNPM with caching.
- Runs `changesets/action` to version packages, update changelogs, commit version updates, and publish to npm with provenance enabled `[.github/workflows/typescript-packages-publish.yml:48-65]()`.

**Sources:**
`[.github/workflows/typescript-packages-publish.yml:1-68]()`

---

## Python Package Publishing

The `publish.yaml` workflow is manually dispatched and supports release and preview modes `[.github/workflows/publish.yaml:1-220]()`.

- **Release (default)**: Reads versions from the release-please manifest and builds packages from tagged releases for production PyPI publishing `[.github/workflows/publish.yaml:35-85]()`.
- **Preview**: Builds development pre-releases from the head of a specified branch, using commit SHA stamps (`<version>.dev<int(sha[:7], 16)>`) to uniquely version dev packages `[.github/workflows/publish.yaml:17-21]()`.

**Sources:**
`[.github/workflows/publish.yaml:1-220]()`

---

## Claude AI Agentic Workflows

Phoenix leverages Claude AI for automated code reviews and issue implementation.

### Claude Code Review (`claude-code-review.yml`)

This workflow triggers on pull request events (`opened`, `synchronize`, `ready_for_review`, `reopened`) for same-repo non-draft PRs `[.github/workflows/claude-code-review.yml:4-29]()`. It uses `anthropics/claude-code-action` with subprocess isolation dependencies (`bubblewrap`, `socat`) to execute `/code-review` checks `[.github/workflows/claude-code-review.yml:48-76]()`.

### Claude Implement Issue (`claude-implement-issue.yml`)

This workflow triggers when an issue is labeled with `good-agent-issue` by an authorized user on an allowlist `[.github/workflows/claude-implement-issue.yml:5-27]`. It guards against duplicates, claims the issue, runs Claude Code end-to-end to implement the requested changes, and validates them `[.github/workflows/claude-implement-issue.yml:40-152]()`.

**Sources:**
`[.github/workflows/claude-code-review.yml:4-76]()`
`[.github/workflows/claude-implement-issue.yml:5-152]()`

---

## Quality Gates and Conditional Execution

Phoenix CI enforces strict quality gates across static analysis (`mypy --strict`, `pyright`), linting (`ruff`, ESLint), unit/integration tests (`pytest`), end-to-end suites (Playwright), and container builds. Dedicated required jobs ensure that workflows validate successfully before merge or deployment `[.github/workflows/typescript-CI.yml:103-121]()`.

**Sources:**
`[.github/workflows/python-CI.yml]()`
`[.github/workflows/typescript-CI.yml:103-121]()`
`[.github/workflows/playwright.yaml]()`

---

# References

- `.github/workflows/python-CI.yml`  
- `.github/workflows/typescript-CI.yml`  
- `.github/workflows/playwright.yaml`  
- `.github/workflows/docker-build-release.yml`  
- `.github/workflows/docker-build-nightly.yml`  
- `.github/workflows/docker-build-experimental.yml`  
- `.github/workflows/claude-code-review.yml`  
- `.github/workflows/claude-implement-issue.yml`  
- `.github/workflows/publish.yaml`  
- `.github/workflows/typescript-packages-publish.yml`  
- `.github/workflows/python-all-platforms.yml`  
- `tox.ini`  
- `Dockerfile`
- `scripts/update_kustomize.py`  
- `scripts/update_helm.py`

---

# Page: Release Management

# Release Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-release-notes/SKILL.md](.agents/skills/phoenix-release-notes/SKILL.md)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [docs/phoenix/release-notes.mdx](docs/phoenix/release-notes.mdx)
- [docs/phoenix/release-notes/03-2026/03-11-2026-session-turns-api.mdx](docs/phoenix/release-notes/03-2026/03-11-2026-session-turns-api.mdx)
- [docs/phoenix/release-notes/06-2026/06-16-2026-time-range-metrics-and-sharing.mdx](docs/phoenix/release-notes/06-2026/06-16-2026-time-range-metrics-and-sharing.mdx)
- [docs/phoenix/release-notes/09-2026/09-08-2026-harbor-plugin-for-agent-benchmarks.mdx](docs/phoenix/release-notes/09-2026/09-08-2026-harbor-plugin-for-agent-benchmarks.mdx)
- [docs/phoenix/release-notes/09-2026/09-08-2026-model-providers-trace-filters-and-pxi.mdx](docs/phoenix/release-notes/09-2026/09-08-2026-model-providers-trace-filters-and-pxi.mdx)
- [docs/phoenix/release-notes/09-2026/09-29-2026-editable-dataset-examples-and-trace-metrics.mdx](docs/phoenix/release-notes/09-2026/09-29-2026-editable-dataset-examples-and-trace-metrics.mdx)
- [docs/phoenix/release-notes/10-2026/10-01-2026-trace-tree-evals-and-decision-spans.mdx](docs/phoenix/release-notes/10-2026/10-01-2026-trace-tree-evals-and-decision-spans.mdx)
- [docs/phoenix/release-notes/10-2026/10-13-2026-docker-sandboxes-and-mcp-graphql-tools.mdx](docs/phoenix/release-notes/10-2026/10-13-2026-docker-sandboxes-and-mcp-graphql-tools.mdx)
- [docs/phoenix/release-notes/10-2026/10-16-2026-claude-managed-agents-tracing-and-gemini-4-argon.mdx](docs/phoenix/release-notes/10-2026/10-16-2026-claude-managed-agents-tracing-and-gemini-4-argon.mdx)
- [docs/phoenix/release-notes/2026.mdx](docs/phoenix/release-notes/2026.mdx)
- [docs/phoenix/self-hosting/features/authentication.mdx](docs/phoenix/self-hosting/features/authentication.mdx)
- [docs/product-selector.js](docs/product-selector.js)
- [docs/snippets/ReleaseUpdate.jsx](docs/snippets/ReleaseUpdate.jsx)
- [docs/style.css](docs/style.css)
- [internal_docs/specs/online-evals.md](internal_docs/specs/online-evals.md)
- [internal_docs/specs/playground.md](internal_docs/specs/playground.md)
- [internal_docs/specs/prompts.md](internal_docs/specs/prompts.md)
- [internal_docs/specs/server_evaluators.md](internal_docs/specs/server_evaluators.md)
- [js/.changeset/README.md](js/.changeset/README.md)
- [js/.changeset/config.json](js/.changeset/config.json)
- [js/.npmrc](js/.npmrc)
- [js/examples/notebooks/README.md](js/examples/notebooks/README.md)
- [js/examples/notebooks/deno.json](js/examples/notebooks/deno.json)
- [js/examples/notebooks/langchain/deno.json](js/examples/notebooks/langchain/deno.json)
- [js/examples/notebooks/langchain/package.json](js/examples/notebooks/langchain/package.json)
- [js/examples/notebooks/langchain/tracing_langchain_node_tutorial.ipynb](js/examples/notebooks/langchain/tracing_langchain_node_tutorial.ipynb)
- [js/examples/notebooks/tracing_openai_node_tutorial.ipynb](js/examples/notebooks/tracing_openai_node_tutorial.ipynb)
- [js/examples/notebooks/tracing_openai_sessions_tutorial.ipynb](js/examples/notebooks/tracing_openai_sessions_tutorial.ipynb)
- [kustomize/README.md](kustomize/README.md)
- [packages/phoenix-client/CHANGELOG.md](packages/phoenix-client/CHANGELOG.md)
- [packages/phoenix-client/pyproject.toml](packages/phoenix-client/pyproject.toml)
- [packages/phoenix-client/src/phoenix/client/helpers/spans/__init__.py](packages/phoenix-client/src/phoenix/client/helpers/spans/__init__.py)
- [packages/phoenix-client/src/phoenix/client/helpers/spans/rag.py](packages/phoenix-client/src/phoenix/client/helpers/spans/rag.py)
- [packages/phoenix-evals/CHANGELOG.md](packages/phoenix-evals/CHANGELOG.md)
- [packages/phoenix-evals/pyproject.toml](packages/phoenix-evals/pyproject.toml)
- [pyproject.toml](pyproject.toml)
- [release-please-config.json](release-please-config.json)
- [requirements/ci.txt](requirements/ci.txt)
- [requirements/packages/phoenix-evals.txt](requirements/packages/phoenix-evals.txt)
- [requirements/type-check.txt](requirements/type-check.txt)
- [requirements/unit-tests.txt](requirements/unit-tests.txt)
- [src/phoenix/__init__.py](src/phoenix/__init__.py)
- [src/phoenix/server/api/routers/oauth2.py](src/phoenix/server/api/routers/oauth2.py)
- [src/phoenix/server/jwt_store.py](src/phoenix/server/jwt_store.py)
- [src/phoenix/server/oauth2.py](src/phoenix/server/oauth2.py)
- [src/phoenix/server/types.py](src/phoenix/server/types.py)
- [src/phoenix/version.py](src/phoenix/version.py)
- [tests/integration/auth/conftest.py](tests/integration/auth/conftest.py)
- [tests/integration/auth/test_auth.py](tests/integration/auth/test_auth.py)
- [tests/integration/auth/test_oidc.py](tests/integration/auth/test_oidc.py)
- [tests/integration/client/test_rag_helpers.py](tests/integration/client/test_rag_helpers.py)
- [tests/unit/server/api/routers/test_oauth2.py](tests/unit/server/api/routers/test_oauth2.py)
- [tests/unit/server/test_oauth2.py](tests/unit/server/test_oauth2.py)
- [tests/unit/test_config.py](tests/unit/test_config.py)
- [tox.ini](tox.ini)
- [uv.lock](uv.lock)

</details>



This document describes Phoenix's automated release process, detailing the configuration of `release-please` for version management, the versioning strategy across multiple packages, changelog generation, and the process for publishing Python packages, Docker images, and the dev preview versioning scheme.

It covers:

- Release-please configuration and automation
- Versioning strategy and changelog generation
- Publishing Python packages to PyPI (main and sub-packages)
- Docker image release channels and variants
- Dev preview versioning scheme for pre-release versions
- Migration documentation for breaking changes

For associated CI/CD testing and deployment details, see [CI/CD Pipeline](#6.3) and [Kubernetes Deployment](#6.5).

---

## Overview

Phoenix employs a fully automated release process with independent versioning for each package in this monorepo. Release PRs are created and updated automatically using the [release-please](https://github.com/googleapis/release-please) tool, based on conventional commit messages pushed to the main branch.

Key release outputs include:

- Python packages:
  - **Main package**: `arize-phoenix`
  - **Sub-packages**: `arize-phoenix-client`, `arize-phoenix-evals`, `arize-phoenix-otel`, `arize-phoenix-sqlean`
- Docker images: released across multiple channels (release, nightly, experimental) and variants (standard, nonroot, debug)
- TypeScript packages and Helm charts (published separately; TS not detailed here)

The release process enforces semantic versioning rules and generates changelogs automatically.

Sources: [.release-please-manifest.json:1-1]()

---

## Release-Please Configuration

Phoenix uses `release-please` in **separate-pull-requests mode**, creating independent PRs for version bumps and changelog updates per package.

This setup enables granular versioning, avoiding forced synchronous releases of unrelated packages.

```mermaid
graph TD
    subgraph "Version Tracking & Manifest"
        manifest[".release-please-manifest.json<br>{'.': '20.24.0', 'packages/phoenix-evals': '3.9.2', 'packages/phoenix-otel': '0.17.2', 'packages/phoenix-client': '3.5.0', 'packages/phoenix-sqlean': '0.2.1'}"]
        config["release-please-config.json<br/>mode: separate-pull-requests"]
        main_version_file["src/phoenix/version.py<br/>__version__ = '20.24.0'"]
    end

    subgraph "Release PR Creation"
        commits["Commits to main branch (conventional commits)"]
        action["release-please GitHub Action<br/>googleapis/release-please-action@v4"]
        PRs["Separate Release PRs<br/>'arize-phoenix', 'phoenix-client', 'phoenix-evals', 'phoenix-otel', 'phoenix-sqlean'"]
    end

    subgraph "Automated Updates"
        changelog["CHANGELOG.md update (version, release notes)"]
        version_bump["Version file update (e.g., src/phoenix/version.py)"]
        PR_title["PR Title: 'chore: release X.Y.Z'"]
    end

    commits --> action
    manifest --> action
    config --> action
    action --> PRs
    PRs --> changelog
    PRs --> version_bump
    PRs --> PR_title
    main_version_file -.->|Read by| action
```

### Package Configuration Map

| Package Path               | PyPI Package Name        | Release Type | Version File Location               |
|---------------------------|--------------------------|--------------|-----------------------------------|
| `.`                       | `arize-phoenix`          | Python       | `src/phoenix/version.py`           |
| `packages/phoenix-client`  | `arize-phoenix-client`   | Python       | `packages/phoenix-client/pyproject.toml` |
| `packages/phoenix-evals`   | `arize-phoenix-evals`    | Python       | `packages/phoenix-evals/pyproject.toml`  |
| `packages/phoenix-otel`    | `arize-phoenix-otel`     | Python       | `packages/phoenix-otel/pyproject.toml`   |
| `packages/phoenix-sqlean`  | `arize-phoenix-sqlean`   | Python       | `packages/phoenix-sqlean/setup.py`       |

This manifest and config coordination ensures each package manages its own version and changelog independently through release-please.

Sources: [.release-please-manifest.json:1-1](), [src/phoenix/version.py:1-1]()

---

## Release Workflow

Release PRs are automatically created by `release-please` triggered by merges to `main` branch containing commits following Conventional Commit format. Each PR updates the corresponding package version, generates changelog entries, and remains open until reviewed and manually merged.

Upon PR merge:

- The change triggers GitHub Actions to build, test, and publish the package.
- The main Phoenix package additionally triggers Docker image builds and deployments.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Main as main branch
    participant RPBot as release-please bot
    participant ReleasePR as Release PR
    participant Merge as PR Merge
    participant PyPI as PyPI Registry
    participant Docker as Docker Hub
    
    Dev->>Main: Push commits (feat, fix, etc.)
    Main->>RPBot: Trigger release-please action
    RPBot->>ReleasePR: Create/Update release PR(s)

    Note over ReleasePR: Accumulates commits until merged
    
    Dev->>ReleasePR: Review and merge
    ReleasePR->>Merge: PR merged triggers release

    alt Main Phoenix Package
        Merge->>PyPI: Build and publish with hatchling
        Merge->>Docker: Trigger Docker build and publish workflows
    else Sub-packages
        Merge->>PyPI: Build and publish package only
    end
```

Sources: [CHANGELOG.md:1-108]()

---

## Versioning Decisions

Semantic versioning is applied based on commit message prefixes:

| Commit Type             | Version Bump       | Examples            |
|------------------------|--------------------|---------------------|
| `feat:`                | Minor (X.Y+1.0)    | 20.23.0 → 20.24.0 |
| `fix:`                 | Patch (X.Y.Z+1)    | 20.21.3 → 20.21.4 |
| `BREAKING CHANGE:` or ⚠ | Major (X+1.0.0)    | 19.0.0 → 20.0.0     |

Changelog sections are generated following these conventions.

Sources: [CHANGELOG.md:1-108]()

---

## Publishing Process

### Python Packages

#### Main Phoenix Package (`arize-phoenix`)

- Version tracked at `src/phoenix/version.py` [src/phoenix/version.py:1-1]().
- Uses [hatchling](https://hatch.pypa.io/latest) to build wheels and sdist.
- Distributed via PyPI using GitHub Trusted Publishing with OpenID Connect.
- CI validates package contents and metadata using `check-wheel-contents` and `twine check`.

#### Sub-Packages (`arize-phoenix-client`, `arize-phoenix-evals`, `arize-phoenix-otel`, `arize-phoenix-sqlean`)

- Each has independent versioning and `pyproject.toml` metadata (or `setup.py` for `phoenix-sqlean`).
- Published independently to PyPI.
- Built with hatchling.

| Package Path                | Version Source                    |
|----------------------------|---------------------------------|
| `.` (main)                 | `src/phoenix/version.py`          |
| `packages/phoenix-client`  | `packages/phoenix-client/pyproject.toml` |
| `packages/phoenix-evals`   | `packages/phoenix-evals/pyproject.toml`  |
| `packages/phoenix-otel`    | `packages/phoenix-otel/pyproject.toml`   |
| `packages/phoenix-sqlean`  | `packages/phoenix-sqlean/setup.py`       |

Sources: [.release-please-manifest.json:1-1](), [src/phoenix/version.py:1-1](), [packages/phoenix-evals/pyproject.toml:23-23](), [packages/phoenix-client/pyproject.toml:23-23]()

---

### Docker Image Releases

Phoenix publishes Docker images in multiple release channels catering to different deployment needs.

| Release Channel  | Trigger                            | Tagged Versions                             |
|------------------|----------------------------------|--------------------------------------------|
| **Release**      | Merging release PR with Git tag  | `latest`, `version-X.Y.Z`, `X.Y.Z`        |
| **Nightly**      | Scheduled runs or push to `main` | `nightly`, `commit-<sha>`                   |
| **Experimental** | Pushes to feature branches        | `dangerously-experimental`                  |

Docker image variants include:

- **Standard**: Default production image.
- **Nonroot**: Hardened variant running as non-privileged user.
- **Debug**: Includes additional debugging tools and interactive shell.

```mermaid
graph TD
    MergeReleasePR["Merge Release PR / Git Tag"]
    ScheduledMainPush["Scheduled / Push to main"]
    FeatureBranchPush["Push to feature branches"]

    ReleaseChannel[/"Release Channel"/]
    NightlyChannel[/"Nightly Channel"/]
    ExperimentalChannel[/"Experimental Channel"/]

    Repo["Phoenix GitHub Repo"]
    DockerRegistry["Docker Hub Registry"]

    MergeReleasePR --> ReleaseChannel
    ScheduledMainPush --> NightlyChannel
    FeatureBranchPush --> ExperimentalChannel

    ReleaseChannel --> |"latest, version-X.Y.Z, X.Y.Z"| DockerRegistry
    NightlyChannel --> |"nightly, commit-<sha>"| DockerRegistry
    ExperimentalChannel --> |"dangerously-experimental"| DockerRegistry

    DockerRegistry --> |"Standard, Nonroot, Debug Variants"| Users
```

Sources: [docs/phoenix/release-notes.mdx:1-40]()

---

## Version Manifest and Changelog Linkage

The `.release-please-manifest.json` file centrally tracks the current versions of all packages:

```json
{
  ".": "20.24.0",
  "packages/phoenix-evals": "3.9.2",
  "packages/phoenix-otel": "0.17.2",
  "packages/phoenix-client": "3.5.0",
  "packages/phoenix-sqlean": "0.2.1"
}
```
Sources: [.release-please-manifest.json:1-1]()

The changelogs (`CHANGELOG.md` in the repo root and each package) are auto-generated by release-please:

- They aggregate commit summaries by version.
- Link to GitHub compare views for release details.
- Organized by release date with categorized features and fixes.

This workflow ensures consistency between version numbers, release notes, and published packages.

Sources: [CHANGELOG.md:1-108](), [packages/phoenix-evals/CHANGELOG.md:1-15](), [packages/phoenix-client/CHANGELOG.md:1-15]()

---

## Dev Preview Versioning Scheme

For development or preview releases (pre-release testing), Phoenix follows a structured versioning scheme. An example of version manipulation for testing is seen in the `integration_tests` tox environment, where the `__version__` is programmatically incremented to the next major version to ensure client methods work with future versions [tox.ini:138-138]().

1. The base version number (e.g., `20.24.0`) is augmented with a dev preview suffix.
2. The suffix includes a timestamp or commit SHA to uniquely identify the preview build.
3. These versions are not published as official releases but may be pushed to development environments or Docker preview tags.

Sources: [tox.ini:138-138]()

---

## Migration Documentation

Breaking changes and major increments are documented in release notes and dedicated changelog migration blocks, providing upgrade instructions and compatibility notes.

Sources: [CHANGELOG.md:1-108](), [packages/phoenix-client/CHANGELOG.md:1-30]()

---

# Summary

Phoenix’s release management infrastructure uses:

- **Release-please** with per-package separate PRs and manifests for granular versioning.
- Semantic versioning driven by conventional commits.
- Automated changelog generation linked to version bumps.
- PyPI publishing of the main and sub-packages with detailed CI checks.
- Multi-channel Docker image releases catering to production, nightly, and experimental users.
- A dev preview versioning scheme for pre-release builds.

This system achieves reliable, maintainable, and consistent release processes for a multi-package AI observability platform.

---

Sources:  
[.release-please-manifest.json:1-1](),  
[CHANGELOG.md:1-108](),  
[src/phoenix/version.py:1-1](),  
[tox.ini:138-138](),  
[packages/phoenix-evals/pyproject.toml:23-23](),  
[packages/phoenix-client/pyproject.toml:23-23]()

---

# Page: Kubernetes Deployment

# Kubernetes Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/helm-release.yaml](.github/workflows/helm-release.yaml)
- [docs/phoenix/self-hosting/configuration.mdx](docs/phoenix/self-hosting/configuration.mdx)
- [helm/.helmignore](helm/.helmignore)
- [helm/Chart.lock](helm/Chart.lock)
- [helm/Chart.yaml](helm/Chart.yaml)
- [helm/README.md](helm/README.md)
- [helm/templates/NOTES.txt](helm/templates/NOTES.txt)
- [helm/templates/_helpers.tpl](helm/templates/_helpers.tpl)
- [helm/templates/phoenix/configmap.yaml](helm/templates/phoenix/configmap.yaml)
- [helm/templates/phoenix/deployment.yaml](helm/templates/phoenix/deployment.yaml)
- [helm/templates/phoenix/ingress.yaml](helm/templates/phoenix/ingress.yaml)
- [helm/templates/phoenix/pvc.yaml](helm/templates/phoenix/pvc.yaml)
- [helm/templates/phoenix/secret.yaml](helm/templates/phoenix/secret.yaml)
- [helm/templates/phoenix/service.yaml](helm/templates/phoenix/service.yaml)
- [helm/templates/phoenix/serviceaccount.yaml](helm/templates/phoenix/serviceaccount.yaml)
- [helm/values.yaml](helm/values.yaml)
- [kustomize/base/kustomization.yaml](kustomize/base/kustomization.yaml)
- [kustomize/base/phoenix.yaml](kustomize/base/phoenix.yaml)
- [kustomize/base/postgres.yaml](kustomize/base/postgres.yaml)
- [scripts/ci/test_helm.py](scripts/ci/test_helm.py)
- [src/phoenix/logging/_config.py](src/phoenix/logging/_config.py)
- [src/phoenix/server/cli/boot_message.py](src/phoenix/server/cli/boot_message.py)
- [src/phoenix/server/cli/commands/serve.py](src/phoenix/server/cli/commands/serve.py)
- [src/phoenix/server/telemetry.py](src/phoenix/server/telemetry.py)
- [tests/unit/server/cli/commands/test_serve.py](tests/unit/server/cli/commands/test_serve.py)
- [tests/unit/server/cli/test_boot_message.py](tests/unit/server/cli/test_boot_message.py)
- [tests/unit/server/test_telemetry.py](tests/unit/server/test_telemetry.py)

</details>



This document details the deployment of Phoenix on Kubernetes using Helm charts or Kustomize manifests. It includes configuration and validation mechanisms, database persistence strategies, authentication configuration, and operational best practices for self-hosting.

For related server configuration and authentication concepts, see [Application Server & Configuration](#2.1)() and [Authentication & Authorization](#2.6)().

---

## Deployment Methods

Phoenix supports two Kubernetes deployment approaches:

| Method         | Path          | Use Case                            | Production Ready |
|----------------|---------------|-----------------------------------|------------------|
| **Helm Chart** | `helm/`       | Production-grade, configurable deployments | Yes          |
| **Kustomize**  | `kustomize/`  | Basic manifests for development or quick starts | Basic       |

The **Helm chart** is the recommended method, featuring parameterized configuration, built-in PostgreSQL dependency (`groundhog2k/postgres` chart v1.5.8), OAuth2/LDAP authentication support, and validation logic to prevent misconfigurations [helm/Chart.yaml:1-56](), [helm/values.yaml:1-200](), [helm/templates/_helpers.tpl:1-172]().

The **Kustomize** manifests provide minimal, base Kubernetes manifests, primarily useful for development and experimentation [kustomize/base/phoenix.yaml:1-41]().

### Overview Diagram of Deployment Methods and Paths

```mermaid
graph LR
    Helm["HelmChart(helm)"]
    Kustomize["KustomizeManifests(kustomize)"]
    Helm --> Prod["ProductionDeployments"]
    Kustomize --> Dev["DevelopmentOrBaseManifests"]
    Prod -.-> PG["PostgreSQLBuiltIn"]
    Prod -.-> Auth["OAuth2OrLDAPSupport"]
```

Sources: `[helm/Chart.yaml:1-56]()`, `[helm/values.yaml:1-200]`, `[kustomize/base/phoenix.yaml:1-41]()`

---

## Helm Chart Architecture

### Chart Structure and Interdependencies

The Phoenix Helm chart (v12.0.24) provides a comprehensive set of Kubernetes resource templates and external dependencies for seamless Phoenix deployment [helm/Chart.yaml:45-51]().

```mermaid
graph TB
  subgraph "phoenix-helm Chart v12.0.24"
    Chart["Chart.yaml (AppVersion 20.24.0)"]
    Values["values.yaml (Configuration)"]
    subgraph Templates
      Deployment["deployment.yaml (Phoenix Deployment)"]
      ConfigMap["configmap.yaml (Environment Variables)"]
      Secret["secret.yaml (Credentials)"]
      Service["service.yaml (Service)"]
      Ingress["ingress.yaml (Ingress)"]
      PVC["pvc.yaml (PVC)"]
      ServiceAccount["serviceaccount.yaml (ServiceAccount)"]
      Helpers["_helpers.tpl (Validation)"]
    end
    subgraph Dependencies
      PostgresChart["groundhog2k/postgres v1.5.8"]
    end
  end

  Chart --> Deployment
  Values --> Deployment
  Values --> ConfigMap
  Values --> Secret
  Values --> Service
  Values --> Ingress
  Values --> PVC
  Values --> ServiceAccount
  
  Helpers -.validates.-> Values
  Chart --> PostgresChart
  PostgresChart -.conditional.-> Values
  
  Deployment --> ConfigMap
  Deployment --> Secret
  Deployment --> PVC
  Deployment --> ServiceAccount
  Service --> Deployment
  Ingress --> Service  
```

This architecture enables flexible, validated deployments featuring:
- Seamless integration of configuration (`values.yaml`) with Kubernetes manifests.
- Built-in PostgreSQL dependency management [helm/Chart.yaml:25-30]().
- Configurable ingress and service mesh compatibility [helm/values.yaml:48-70]().
- Authentication and authorization configuration support [helm/README.md:38-60]().

Sources: `[helm/Chart.yaml:1-56]()`, `[helm/values.yaml:1-200]`, `[helm/templates/_helpers.tpl:1-172]`, `[helm/templates/phoenix/deployment.yaml:1-135]()`

---

### Deployment Resource Provisioning Flow

The deployment lifecycle initiated by Helm install proceeds as:

```mermaid
graph LR
    Install["helm install phoenix arize-ai/phoenix-helm"]
    Install --> Validation["RunValidationFunctions"]
    Validation --> CreateResources["CreateKubernetesResources"]

    CreateResources --> ConfigMap["ConfigMap phoenix-configmap"]
    CreateResources --> Secret["Secret phoenix-secret"]
    CreateResources --> PVC["PersistentVolumeClaim phoenix-data-pvc"]
    CreateResources --> Postgres["StatefulSet phoenix-postgresql"]
    CreateResources --> Deployment["Deployment phoenix (arizephoenix/phoenix:version-20.24.0)"]
    CreateResources --> Service["Service phoenix-svc"]
    CreateResources --> Ingress["Ingress phoenix-ingress"]

    Deployment --> ConfigMap
    Deployment --> Secret
    Deployment --> PVC
    Deployment -.env PHOENIX_POSTGRES_HOST.-> Postgres
    Service --> Deployment
    Ingress --> Service
```

Sources: `[helm/templates/phoenix/deployment.yaml:1-135]()`, `[helm/templates/_helpers.tpl:1-172]`, `[helm/templates/phoenix/configmap.yaml:1-125]()`

---

## Database Persistence Strategies

Phoenix supports several mutually exclusive database strategies. Helm chart includes validations to avoid conflicts [helm/templates/_helpers.tpl:1-172]().

### Persistence Strategy Matrix

| Strategy                           | `persistence.enabled` | `postgresql.enabled` | `database.url`                  | Notes                                                             |
|----------------------------------|-----------------------|---------------------|--------------------------------|-------------------------------------------------------------------|
| SQLite with Persistent Storage   | true                  | false               | empty                          | Persistent SQLite DB file under mounted volume                    |
| Built-in PostgreSQL (groundhog2k)| false                 | true                | empty                          | PostgreSQL StatefulSet, persistent storage managed                |
| External Database (Cloud, RDS)   | false                 | false               | configured explicitly          | Connect to external managed DB instance                           |
| SQLite In-memory (Testing only)  | false                 | false               | `sqlite:///:memory:`            | Ephemeral SQLite, data lost on pod restart                        |

### Strategy 1: SQLite with Persistent Storage

Deploy Phoenix with SQLite using persistent volumes:

```yaml
persistence:
  enabled: true

postgresql:
  enabled: false

server:
  workingDir: "/data" # Should be mounted persistent volume
```

- Phoenix stores data in `${PHOENIX_WORKING_DIR}/phoenix.db` [docs/phoenix/self-hosting/configuration.mdx:36-44]().
- Uses PVC named `phoenix-data-pvc` mounted to `/data` [helm/values.yaml:164-169]().
- Requires correct permissions via `fsGroup: 999` or matching security contexts for non-root container access [helm/values.yaml:92-104]().

### Strategy 2: Built-in PostgreSQL

Deploy Phoenix with PostgreSQL as a managed StatefulSet [helm/values.yaml:75-84]():

```yaml
postgresql:
  enabled: true
  image:
    registry: "docker.io"
    repository: "postgres"
    tag: "16"
  storage:
    requestedSize: "20Gi"
  userDatabase:
    name:
      value: "phoenix"
    user:
      value: "phoenix"
    password:
      value: "phoenix"
```

- Deploys the `groundhog2k/postgres` Helm chart dependency [helm/Chart.yaml:25-30]().
- Phoenix connects internally to `postgres` hostname [kustomize/base/phoenix.yaml:31-32]().

### Strategy 3: External PostgreSQL Database

Connect Phoenix to externally managed PostgreSQL [helm/values.yaml:76-83]():

```yaml
database:
  url: "postgresql://user:pass@rds.example.com:5432/phoenix"

persistence:
  enabled: false
postgresql:
  enabled: false
```

- Uses `PHOENIX_SQL_DATABASE_URL` environment variable to configure DB connection [docs/phoenix/self-hosting/configuration.mdx:40-44]().

Sources: `[helm/Chart.yaml:1-56]()`, `[helm/values.yaml:1-200]`, `[docs/phoenix/self-hosting/configuration.mdx:1-83]`, `[kustomize/base/phoenix.yaml:1-41]()`

---

## Configuration Management

### ConfigMap: phoenix-configmap

The ConfigMap named `phoenix-configmap` holds environment variables that configure Phoenix server behavior, authentication, and database access [helm/templates/phoenix/configmap.yaml:5-12]().

Key environment variables include:

| Category        | Variables                                                                | Description                                |
|-----------------|---------------------------------------------------------------------------|--------------------------------------------|
| Server          | `PHOENIX_PORT`, `PHOENIX_GRPC_PORT`, `PHOENIX_WORKING_DIR` | Server ports and working directory [docs/phoenix/self-hosting/configuration.mdx:28-36]() |
| Authentication  | `PHOENIX_ENABLE_AUTH`, `PHOENIX_ADMINS`, `PHOENIX_DISABLE_BASIC_AUTH` | Enable/disable auth and admin users [helm/templates/phoenix/configmap.yaml:14-28]() |
| OAuth2          | `PHOENIX_OAUTH2_<PROVIDER>_CLIENT_ID`, etc. | Config for OAuth2 providers [helm/templates/phoenix/configmap.yaml:41-89]() |
| LDAP            | `PHOENIX_LDAP_HOST`, `PHOENIX_LDAP_USER_SEARCH_BASE_DNS`, etc. | LDAP server and attribute config [helm/templates/phoenix/configmap.yaml:92-125]() |

### Secret: phoenix-secret

The `phoenix-secret` Kubernetes Secret stores sensitive values such as [helm/templates/phoenix/secret.yaml:1-10]():
- Default admin initial password (`PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD`).
- LDAP bind password (`PHOENIX_LDAP_BIND_PASSWORD`).
- OAuth2 client secrets.

If not provided by the user, these secrets are automatically generated by Helm with randomized values [helm/templates/phoenix/secret.yaml:11-19]().

Sources: `[helm/templates/phoenix/configmap.yaml:1-125]()`, `[helm/templates/phoenix/secret.yaml:1-33]`, `[docs/phoenix/self-hosting/configuration.mdx:1-83]()`

---

## Networking and Ingress

### Service Configuration

Phoenix service exposes multiple ports mapped from container [helm/templates/phoenix/deployment.yaml:59-62]():

| Port | Name            | Protocol | Purpose                                   |
|-------|-----------------|----------|-------------------------------------------|
| 6006  | phoenix-app     | HTTP     | UI and HTTP OTLP trace ingestion [docs/phoenix/self-hosting/configuration.mdx:12-15]() |
| 4317  | phoenix-grpc    | gRPC     | OTLP gRPC trace ingestion [docs/phoenix/self-hosting/configuration.mdx:16-17]() |
| 9090  | phoenix-metrics | HTTP     | Prometheus metrics endpoint [helm/values.yaml:143-144]() |

### Ingress Configuration

Ingress provides optional HTTP/HTTPS external access [helm/values.yaml:48-56]():

```yaml
ingress:
  enabled: true
  host: "phoenix.example.com"
  apiPath: "/"
  pathType: "Prefix"
  tls:
    enabled: true
```

Sources: `[helm/templates/phoenix/deployment.yaml:1-135]()`, `[docs/phoenix/self-hosting/configuration.mdx:1-83]`, `[helm/values.yaml:1-200]()`

---

## Authentication Configuration

- **Local Authentication:** Enabled by `PHOENIX_ENABLE_AUTH`, JWT-based sessions, configurable admin users via `PHOENIX_ADMINS` [helm/templates/phoenix/configmap.yaml:14-28]().
- **OAuth2 / OIDC:** Multiple OAuth2/OIDC providers configured via `PHOENIX_OAUTH2_*` environment variables [helm/templates/phoenix/configmap.yaml:41-89]().
- **LDAP Authentication:** LDAP binding, user/group searches, and attribute mappings [helm/templates/phoenix/configmap.yaml:91-125]().

Sources: `[helm/templates/phoenix/configmap.yaml:1-125]()`

---

## Health Checks and Probes

Phoenix deployment contains Kubernetes probes [helm/templates/phoenix/deployment.yaml:63-91]():

| Probe Type | Endpoint   | Purpose                                               |
|------------|------------|-------------------------------------------------------|
| Liveness   | `/healthz` | Detect if the server is alive [helm/templates/phoenix/deployment.yaml:63-66]() |
| Readiness  | `/readyz`  | Verify server readiness before routing traffic [helm/templates/phoenix/deployment.yaml:72-75]() |
| Startup    | `/healthz` | Provide longer initialization window for startup [helm/templates/phoenix/deployment.yaml:81-85]() |

Sources: `[helm/templates/phoenix/deployment.yaml:1-135]()`

---

## Operational Considerations

### Memory Management (Span Queue)
- Phoenix buffers incoming spans in an in-memory queue.
- Default maximum queue size is 20,000 spans (~1 GiB memory) [helm/values.yaml:179-182]().
- Set via `PHOENIX_MAX_SPANS_QUEUE_SIZE`.

### Security and Non-Root Execution
- Official Phoenix container supports non-root execution contexts.
- The working directory (`PHOENIX_WORKING_DIR`) must be writable by the container user.

Sources: `[helm/values.yaml:1-200]()`

---

## System Components: Natural Language to Code Entity Mapping

### Deployment Components and Corresponding Code Entities

```mermaid
graph LR
    Phoenix["PhoenixApplication(arizephoenix/phoenix:version-20.24.0)"]
    DeploymentYaml["deployment.yaml"]
    ConfigMapYaml["configmap.yaml"]
    SecretYaml["secret.yaml"]
    ServiceYaml["service.yaml"]
    HelpersTpl["_helpers.tpl"]
    PostgresChart["groundhog2k/postgres"]

    Phoenix --> DeploymentYaml
    Phoenix --> ConfigMapYaml
    Phoenix --> SecretYaml
    Phoenix --> ServiceYaml

    HelpersTpl -.validates.-> DeploymentYaml
    DeploymentYaml -.connects_to.-> PostgresChart
```

### Authentication Configuration Code Mapping

```mermaid
graph TB
    ConfigMap["ConfigMapPhoenixConfigmap"]
    Secret["SecretPhoenixSecret"]
    OAuth2Providers["OAuth2ProvidersConfig"]
    LDAPSettings["LDAPSettingsConfig"]

    PhoenixApp["PhoenixFastAPIApp(phoenix.server.main)"]

    ConfigMap --> PhoenixApp
    Secret --> PhoenixApp
    OAuth2Providers --> ConfigMap
    LDAPSettings --> ConfigMap
```

Sources: `[helm/templates/phoenix/deployment.yaml:1-135]()`, `[helm/templates/phoenix/configmap.yaml:1-125]`, `[helm/templates/phoenix/secret.yaml:1-33]()`

---

# Page: API Reference Documentation

# API Reference Documentation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.mintignore](.mintignore)
- [.readthedocs.yaml](.readthedocs.yaml)
- [api_reference/.gitignore](api_reference/.gitignore)
- [api_reference/Makefile](api_reference/Makefile)
- [api_reference/README.md](api_reference/README.md)
- [api_reference/make.bat](api_reference/make.bat)
- [api_reference/requirements.txt](api_reference/requirements.txt)
- [api_reference/source/_static/custom.css](api_reference/source/_static/custom.css)
- [api_reference/source/_static/logo.png](api_reference/source/_static/logo.png)
- [api_reference/source/_static/switcher.json](api_reference/source/_static/switcher.json)
- [api_reference/source/_templates/custom_sidebar.html](api_reference/source/_templates/custom_sidebar.html)
- [api_reference/source/conf.py](api_reference/source/conf.py)
- [api_reference/source/index.md](api_reference/source/index.md)
- [docs.json](docs.json)
- [docs/PROMPT.md](docs/PROMPT.md)
- [docs/openapi.json](docs/openapi.json)
- [docs/phoenix/cookbook/tracing/claude-managed-agents-guide.mdx](docs/phoenix/cookbook/tracing/claude-managed-agents-guide.mdx)
- [docs/phoenix/cookbook/tracing/cookbooks.mdx](docs/phoenix/cookbook/tracing/cookbooks.mdx)
- [docs/phoenix/integrations.mdx](docs/phoenix/integrations.mdx)
- [docs/phoenix/integrations/developer-tools/coding-agents.mdx](docs/phoenix/integrations/developer-tools/coding-agents.mdx)
- [docs/phoenix/integrations/llm-providers/anthropic.mdx](docs/phoenix/integrations/llm-providers/anthropic.mdx)
- [docs/phoenix/integrations/llm-providers/cohere.mdx](docs/phoenix/integrations/llm-providers/cohere.mdx)
- [docs/phoenix/integrations/llm-providers/cohere/cohere-tracing.mdx](docs/phoenix/integrations/llm-providers/cohere/cohere-tracing.mdx)
- [docs/phoenix/integrations/platforms/claude-managed-agents.mdx](docs/phoenix/integrations/platforms/claude-managed-agents.mdx)
- [docs/phoenix/integrations/platforms/claude-managed-agents/claude-managed-agents-tracing.mdx](docs/phoenix/integrations/platforms/claude-managed-agents/claude-managed-agents-tracing.mdx)
- [docs/phoenix/integrations/platforms/scalekit.mdx](docs/phoenix/integrations/platforms/scalekit.mdx)
- [docs/phoenix/integrations/platforms/scalekit/scalekit-tracing.mdx](docs/phoenix/integrations/platforms/scalekit/scalekit-tracing.mdx)
- [docs/phoenix/llms.txt](docs/phoenix/llms.txt)
- [docs/phoenix/resources/python-api.mdx](docs/phoenix/resources/python-api.mdx)
- [docs/phoenix/resources/typescript-api.mdx](docs/phoenix/resources/typescript-api.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-session-annotations-by-filter.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-session-annotations-by-filter.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-span-annotations-by-filter.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-span-annotations-by-filter.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-trace-annotations-by-filter.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-trace-annotations-by-filter.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/get-session-annotations-for-a-list-of-session_ids.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/get-session-annotations-for-a-list-of-session_ids.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/get-trace-annotations-for-a-list-of-trace_ids.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/get-trace-annotations-for-a-list-of-trace_ids.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/delete-experiment-by-id.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/delete-experiment-by-id.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/get-incomplete-evaluations-for-an-experiment.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/get-incomplete-evaluations-for-an-experiment.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/get-incomplete-runs-for-an-experiment.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/get-incomplete-runs-for-an-experiment.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/secrets.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/secrets.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/secrets/upsert-or-delete-secrets.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/secrets/upsert-or-delete-secrets.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/create-session-annotations.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/create-session-annotations.mdx)
- [docs/phoenix/sitemap.xml](docs/phoenix/sitemap.xml)
- [docs/sitemap.xml](docs/sitemap.xml)
- [scripts/generate_sitemap.py](scripts/generate_sitemap.py)
- [sitemap.xml](sitemap.xml)

</details>



This page details the generation, hosting, and maintenance of the Phoenix Python API reference documentation. The documentation is built using Sphinx, hosted on ReadTheDocs, and automatically generated from Python docstrings using `sphinx.ext.autodoc` and `sphinx.ext.autosummary`.

## Purpose and Scope

The Python API reference provides comprehensive documentation for the `arize-phoenix` Python packages, including `arize-phoenix-client`, `arize-phoenix-otel`, and `arize-phoenix-evals`. It serves as a detailed guide for developers integrating with Phoenix programmatically, offering insights into classes, functions, and modules. This reference complements the broader Phoenix documentation available on the Arize website, which includes tutorials, quickstarts, and conceptual explanations [api_reference/source/index.md:10-12]().

The API reference is specifically for the Python client libraries and does not cover the REST API or GraphQL API, which are documented separately via OpenAPI and GraphQL schemas.

---

## Sphinx-based Python API Reference

The Phoenix Python API reference is generated using Sphinx, a documentation generator that converts reStructuredText (or MyST Markdown) into various output formats, primarily HTML.

### Configuration

The main configuration for the Sphinx build process is located in the file `api_reference/source/conf.py`. Key configurations include:

- **Project Information:** Defines the project title as `"Phoenix Python Reference"`, copyright, and author metadata [api_reference/source/conf.py:73-75]().
- **Installed Extensions:**  
  - `sphinx.ext.autodoc`: Automatically extracts docstrings from Python code to generate documentation [api_reference/source/conf.py:82-82]().
  - `sphinx.ext.autosummary`: Creates summary tables for documented modules and classes [api_reference/source/conf.py:83-83]().
  - `sphinx.ext.napoleon`: Supports Google and NumPy style docstrings [api_reference/source/conf.py:84-84]().
  - `myst_parser`: Enables authoring docs in MyST Markdown syntax [api_reference/source/conf.py:85-85]().
  - `sphinx_design`: Allows advanced layout and design elements [api_reference/source/conf.py:86-86]().
- **Python Path Setup for Autodoc:**  
  The system path (`sys.path`) is extended to include the root source directories for the various Phoenix Python packages—`phoenix`, `phoenix-client`, `phoenix-evals`, and `phoenix-otel`—enabling autodoc to discover all relevant modules for documentation extraction [api_reference/source/conf.py:17-21]().
- **Autodoc Options:** Controls autodoc behavior, such as including all members, excluding private members, disabling type hints in signatures, and preserving default argument values [api_reference/source/conf.py:117-130]().
- **HTML Theme and Assets:** Utilizes the `pydata_sphinx_theme` for a modern HTML look, includes custom CSS and JavaScript files for styling and enhancements, and configures theme options such as the version switcher and navigation [api_reference/source/conf.py:157-205]().

### Cleaning Doc Output

A custom function `clean_doc_output(app, docname, source)` is connected to the Sphinx `source-read` event [api_reference/source/conf.py:68-68](). This function processes the generated `.rst` files to:

- Remove unwanted text outside of `automodule` directive blocks [api_reference/source/conf.py:37-41]().
- Filter out headers like "Submodules", and clean up package/module labels [api_reference/source/conf.py:51-58]().
- Preserve indentation and formatting within the documented modules [api_reference/source/conf.py:60-62]().

This step is essential for producing tidy, focused API documentation pages without extraneous information added by default from autodoc.

---

### Diagram: Sphinx Documentation Generation Workflow

This diagram maps the natural language concept of "Documentation Generation" to specific code entities and files involved in the Phoenix Sphinx API reference generation process.

```mermaid
graph TD
    "Python_Source_Code"["Python Source Code"] --> "Docstrings"["Docstrings"]
    "Docstrings" --> "conf_py"["api_reference/source/conf.py"]
    "conf_py" --> "Sphinx_Build"["Sphinx Build Process"]
    
    subgraph "Python_Packages"["Python Packages"]
        "phoenix"["src/phoenix"]
        "phoenix_client"["packages/phoenix-client/src/phoenix"]
        "phoenix_evals"["packages/phoenix-evals/src/phoenix"]
        "phoenix_otel"["packages/phoenix-otel/src/phoenix"]
    end

    "phoenix" --> "Docstrings"
    "phoenix_client" --> "Docstrings"
    "phoenix_evals" --> "Docstrings"
    "phoenix_otel" --> "Docstrings"

    "Sphinx_Build" -- "sphinx.ext.autodoc" --> "RST_Files"["Generated .rst Files"]
    "RST_Files" -- "clean_doc_output()" --> "Clean_RST"["Cleaned .rst Files"]
    "Clean_RST" --> "HTML_Output"["HTML Output"]
    "HTML_Output" --> "RTD"["ReadTheDocs Hosting"]
```
*Title: "Sphinx Documentation Generation Workflow"*  
Sources: [api_reference/source/conf.py:17-21](), [api_reference/source/conf.py:27-63](), [api_reference/source/conf.py:82-86]()

---

## ReadTheDocs Hosting

The resulting Python API reference documentation is hosted on [ReadTheDocs (RTD)](https://readthedocs.org), which provides automated building, hosting, and versioned access to Phoenix API docs.

### ReadTheDocs Configuration

The `.readthedocs.yaml` file at the repository root configures the RTD build environment:

- Specifies Ubuntu 22.04 as the build OS image [/.readthedocs.yaml:9-9]().  
- Uses Python 3.12 for the build environment [/.readthedocs.yaml:11-11]().  
- Points to the Sphinx configuration file `api_reference/source/conf.py` [/.readthedocs.yaml:19-19]().  
- Installs dependencies listed in `api_reference/requirements.txt` and the Python package itself (`pip install .`) during build [/.readthedocs.yaml:33-37]().  

---

## Versioning Strategy

Phoenix API documentation provided on ReadTheDocs supports multiple versions, reflecting various package releases.

### How Version Matching Works

In `conf.py` the version switcher’s version is determined as follows:

```python
json_url = "https://arize-phoenix.readthedocs.io/en/latest/_static/switcher.json"
version_match = os.environ.get("READTHEDOCS_VERSION")
release = phoenix.__version__

if not version_match or version_match.isdigit() or version_match == "stable":
    version_match = f"v{release}"
```

Explanation:
- The environment variable `READTHEDOCS_VERSION` is set during RTD build and indicates the version tag or branch [api_reference/source/conf.py:145-145]().  
- If `READTHEDOCS_VERSION` is missing, is a digit (PR build), or the string `"stable"`, the version is set to `"v<release>"` based on the active package version in `phoenix.__version__` [api_reference/source/conf.py:151-152]().  
- This version string is used by the `pydata_sphinx_theme` to correctly link and switch between documentation versions on RTD [api_reference/source/conf.py:196-199]().

---

## Maintaining and Regenerating Reference Pages

### Updating Docstrings and Documentation Content

- Docstrings in the Python source code should follow Google or NumPy style conventions for best Sphinx compatibility. The `napoleon` extension parses these styles to render clean API docs [api_reference/source/conf.py:101-103]().  
- When new classes, methods, or modules are added or changed, their docstrings should be updated and committed.

### Sitemap Generation and CI Automation

- The documentation's sitemap is auto-generated using a GitHub Actions workflow (`.github/workflows/generate-sitemap.yml`) combined with a Python script (`scripts/generate_sitemap.py`).  
- The script:
  1. Parses `docs.json` to extract all documentation page URLs from the navigation/footer [scripts/generate_sitemap.py:157-159]().  
  2. Reads existing `sitemap.xml` to preserve prior modification timestamps [scripts/generate_sitemap.py:65-96,180-182]().  
  3. Generates a new `sitemap.xml` with updated timestamps for new pages, maintaining consistency for unchanged URLs [scripts/generate_sitemap.py:99-136]().  
  4. Writes the updated sitemap to the repository root and `docs/phoenix/` directory [scripts/generate_sitemap.py:188-191]().

- The GitHub Actions workflow triggers on pushes to `main` branch for `docs.json` or the sitemap generator script, running the script in an environment with `uv` installed [/.github/workflows/generate-sitemap.yml:1-41]().

---

### Diagram: Sitemap Generation Workflow

This diagram represents the process that ties the CI push event to sitemap generation, linking key scripts and data files involved.

```mermaid
graph TD
    "Push_to_main"["Push to main branch"] --> "Workflow"["GitHub Action: generate-sitemap.yml"]
    "Workflow" --> "uv_run"["uv run scripts/generate_sitemap.py"]
    
    subgraph "Sitemap_Logic"["Sitemap Generation Logic"]
        "extract_pages"["extract_pages()"] -- "Reads" --> "docs_json"["docs.json"]
        "parse_existing"["parse_existing_sitemap()"] -- "Reads" --> "old_xml"["sitemap.xml (Root)"]
        "generate_xml"["generate_sitemap_xml()"]
    end

    "uv_run" --> "extract_pages"
    "uv_run" --> "parse_existing"
    "extract_pages" --> "generate_xml"
    "parse_existing" --> "generate_xml"

    "generate_xml" -- "Writes" --> "new_root_xml"["sitemap.xml (Root)"]
    "generate_xml" -- "Writes" --> "new_docs_xml"["docs/phoenix/sitemap.xml"]
    
    "new_root_xml" --> "PR"["Create Pull Request"]
    "new_docs_xml" --> "PR"
```
*Title: "Sitemap Generation Workflow"*  
Sources: [.github/workflows/generate-sitemap.yml:1-41](), [scripts/generate_sitemap.py:17-43](), [scripts/generate_sitemap.py:65-96](), [scripts/generate_sitemap.py:99-136]()

---

## Mintlify Documentation Site (docs.json-driven)

The Phoenix documentation site is powered by Mintlify, which uses a `docs.json` configuration file to drive navigation, theming, and page structure.

- The `docs.json` file defines site-wide settings such as theme colors, fonts, icons, and interaction settings [docs.json:1-40]().  
- It organizes the documentation into navigation tabs and groups, specifying which markdown or MDX pages to render under each [docs.json:50-104]().  
- This file lives at the root of the docs source and is consumed by the Mintlify platform to generate a consistent, performant documentation experience.

The sitemap generation script leverages `docs.json` to obtain the full list of documentation pages and maintain accurate sitemap files for SEO and indexing [scripts/generate_sitemap.py:151-159]().

---

### Diagram: Natural Language to Code Entity Mapping for Phoenix API Reference Generation

```mermaid
graph LR
    "Natural_Language_Docs_Concepts"["Phoenix API Reference Concepts"]
    "Python_Package_Source"["Python Packages Source"]
    "Sphinx_Autodoc"["Sphinx Extensions (autodoc / autosummary)"]
    "Conf_py"["Sphinx Config (conf.py)"]
    "RST_Files"["Generated .rst Files"]
    "Cleaned_RST"["clean_doc_output()"]
    "HTML_Docs"["HTML API Docs"]
    "RTD"["ReadTheDocs Hosting"]

    "Natural_Language_Docs_Concepts" --> "Sphinx_Autodoc"
    "Python_Package_Source" --> "Sphinx_Autodoc"
    "Sphinx_Autodoc" --> "RST_Files"
    "RST_Files" --> "Cleaned_RST"
    "Cleaned_RST" --> "HTML_Docs"
    "HTML_Docs" --> "RTD"
    "Conf_py" --> "Sphinx_Autodoc"
    "Conf_py" --> "HTML_Docs"
```
*Title: "Logical Flow from Concepts to Python API HTML Docs"*  
Sources: [api_reference/source/conf.py:1-70](), [api_reference/source/conf.py:27-63]()

---

### Diagram: Bridging Mintlify Docs.json Configuration to Sitemap and Doc Pages

```mermaid
graph LR
    "docs_json"["docs.json (Mintlify Config)"]
    "Navigation_Structure"["Navigation & Site Structure"]
    "Themes"["Theme & Styling"]
    "Page_List"["List of Documentation Pages"]
    "Sitemap_Generation_Script"["scripts/generate_sitemap.py"]
    "Sitemap_XML_Root"["sitemap.xml (Root)"]
    "Sitemap_XML_Docs"["docs/phoenix/sitemap.xml"]
    "GitHub_Actions"["GitHub Actions Workflow (.github/workflows/generate-sitemap.yml)"]

    "docs_json" --> "Navigation_Structure"
    "docs_json" --> "Themes"
    "Navigation_Structure" --> "Page_List"
    "Page_List" --> "Sitemap_Generation_Script"
    "Sitemap_Generation_Script" --> "Sitemap_XML_Root"
    "Sitemap_Generation_Script" --> "Sitemap_XML_Docs"
    "GitHub_Actions" --> "Sitemap_Generation_Script"
```
*Title: "Mintlify docs.json to Sitemap Workflow & CI"*  
Sources: [docs.json:50-104](), [scripts/generate_sitemap.py:151-159](), [.github/workflows/generate-sitemap.yml:1-41]()

---

# Summary Table of Key Files for API Reference Documentation

| File/Directory                        | Purpose                                                     |
|-------------------------------------|-------------------------------------------------------------|
| `api_reference/source/conf.py`      | Sphinx configuration for building the API documentation     |
| `api_reference/source/index.md`     | Entry point – top-level index page for the API docs          |
| `api_reference/requirements.txt`    | Dependencies for building the docs on ReadTheDocs            |
| `.readthedocs.yaml`                  | Configures ReadTheDocs environment and build process         |
| `.github/workflows/generate-sitemap.yml` | GitHub Action workflow to generate/update sitemap.xml       |
| `scripts/generate_sitemap.py`       | Script implementing sitemap generation logic                  |
| `docs.json`                         | Mintlify documentation site configuration & navigation       |

Sources:  
[api_reference/source/conf.py:1-210](),  
[.readthedocs.yaml:1-37](),  
[.github/workflows/generate-sitemap.yml:1-41](),  
[scripts/generate_sitemap.py:1-204](),  
[api_reference/source/index.md:10-21](),  
[docs.json:1-74]()

---

# Page: Agent Skills & Plugin Distribution

# Agent Skills & Plugin Distribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/create-task/SKILL.md](.agents/skills/create-task/SKILL.md)
- [.agents/skills/daytona/references/api/README.md](.agents/skills/daytona/references/api/README.md)
- [.agents/skills/daytona/references/api/audit.md](.agents/skills/daytona/references/api/audit.md)
- [.agents/skills/daytona/references/api/jobs.md](.agents/skills/daytona/references/api/jobs.md)
- [.agents/skills/daytona/references/api/organizations.md](.agents/skills/daytona/references/api/organizations.md)
- [.agents/skills/daytona/references/api/runners.md](.agents/skills/daytona/references/api/runners.md)
- [.agents/skills/daytona/references/api/sandbox.md](.agents/skills/daytona/references/api/sandbox.md)
- [.agents/skills/daytona/references/api/secret.md](.agents/skills/daytona/references/api/secret.md)
- [.agents/skills/daytona/references/api/snapshots.md](.agents/skills/daytona/references/api/snapshots.md)
- [.agents/skills/daytona/references/api/users.md](.agents/skills/daytona/references/api/users.md)
- [.agents/skills/daytona/references/cli.md](.agents/skills/daytona/references/cli.md)
- [.agents/skills/gh-stack/SKILL.md](.agents/skills/gh-stack/SKILL.md)
- [.agents/skills/gh-stack/references/commands.md](.agents/skills/gh-stack/references/commands.md)
- [.agents/skills/gh-stack/references/troubleshooting.md](.agents/skills/gh-stack/references/troubleshooting.md)
- [.agents/skills/harbor-exec/SKILL.md](.agents/skills/harbor-exec/SKILL.md)
- [.agents/skills/harbor-exec/references/examples.md](.agents/skills/harbor-exec/references/examples.md)
- [.agents/skills/mintlify/SKILL.md](.agents/skills/mintlify/SKILL.md)
- [.agents/skills/phoenix-evals/references/evaluators-llm-typescript.md](.agents/skills/phoenix-evals/references/evaluators-llm-typescript.md)
- [.agents/skills/phoenix-evals/references/experiments-running-python.md](.agents/skills/phoenix-evals/references/experiments-running-python.md)
- [.agents/skills/phoenix-evals/references/experiments-running-typescript.md](.agents/skills/phoenix-evals/references/experiments-running-typescript.md)
- [.agents/skills/phoenix-evals/references/setup-typescript.md](.agents/skills/phoenix-evals/references/setup-typescript.md)
- [.agents/skills/phoenix-frontend/SKILL.md](.agents/skills/phoenix-frontend/SKILL.md)
- [.agents/skills/phoenix-github/SKILL.md](.agents/skills/phoenix-github/SKILL.md)
- [.agents/skills/phoenix-github/scripts/_board.py](.agents/skills/phoenix-github/scripts/_board.py)
- [.agents/skills/phoenix-github/scripts/board.json](.agents/skills/phoenix-github/scripts/board.json)
- [.agents/skills/phoenix-github/scripts/health.py](.agents/skills/phoenix-github/scripts/health.py)
- [.agents/skills/phoenix-github/scripts/roadmap.py](.agents/skills/phoenix-github/scripts/roadmap.py)
- [.agents/skills/phoenix-github/scripts/rollover.py](.agents/skills/phoenix-github/scripts/rollover.py)
- [.agents/skills/phoenix-github/scripts/snapshot.sh](.agents/skills/phoenix-github/scripts/snapshot.sh)
- [.agents/skills/phoenix-github/scripts/standup.py](.agents/skills/phoenix-github/scripts/standup.py)
- [.agents/skills/phoenix-llms-txt/SKILL.md](.agents/skills/phoenix-llms-txt/SKILL.md)
- [.agents/skills/phoenix-playwright-tests/SKILL.md](.agents/skills/phoenix-playwright-tests/SKILL.md)
- [.agents/skills/phoenix-pr-description/SKILL.md](.agents/skills/phoenix-pr-description/SKILL.md)
- [.agents/skills/phoenix-pr-description/examples.md](.agents/skills/phoenix-pr-description/examples.md)
- [.agents/skills/phoenix-pr-screenshot/SKILL.md](.agents/skills/phoenix-pr-screenshot/SKILL.md)
- [.agents/skills/phoenix-skills-audit/SKILL.md](.agents/skills/phoenix-skills-audit/SKILL.md)
- [.agents/skills/phoenix-skills-audit/evals/evals.json](.agents/skills/phoenix-skills-audit/evals/evals.json)
- [.agents/skills/phoenix-tracing/references/instrumentation-auto-typescript.md](.agents/skills/phoenix-tracing/references/instrumentation-auto-typescript.md)
- [.agents/skills/phoenix-tracing/references/production-python.md](.agents/skills/phoenix-tracing/references/production-python.md)
- [.agents/skills/phoenix-tracing/references/production-typescript.md](.agents/skills/phoenix-tracing/references/production-typescript.md)
- [.agents/skills/phoenix-tracing/references/projects-python.md](.agents/skills/phoenix-tracing/references/projects-python.md)
- [.agents/skills/phoenix-tracing/references/projects-typescript.md](.agents/skills/phoenix-tracing/references/projects-typescript.md)
- [.agents/skills/phoenix-tracing/references/sessions-typescript.md](.agents/skills/phoenix-tracing/references/sessions-typescript.md)
- [.agents/skills/phoenix-tracing/references/setup-typescript.md](.agents/skills/phoenix-tracing/references/setup-typescript.md)
- [.agents/skills/phoenix-tracing/references/span-decision.md](.agents/skills/phoenix-tracing/references/span-decision.md)
- [.agents/skills/phoenix-typescript/SKILL.md](.agents/skills/phoenix-typescript/SKILL.md)
- [.agents/skills/rewardkit/SKILL.md](.agents/skills/rewardkit/SKILL.md)
- [.claude/settings.json](.claude/settings.json)
- [.cursor/rules/typescript-packages/RULE.md](.cursor/rules/typescript-packages/RULE.md)
- [.git-blame-ignore-revs](.git-blame-ignore-revs)
- [.oxfmtrc.jsonc](.oxfmtrc.jsonc)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/datasets/download-dataset-examples-as-jsonl-file.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/datasets/download-dataset-examples-as-jsonl-file.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/prompts/delete-a-prompt.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/prompts/delete-a-prompt.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/prompts/delete-a-tag-from-a-prompt-version.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/prompts/delete-a-tag-from-a-prompt-version.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/bulk-delete-sessions.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/bulk-delete-sessions.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/create-a-session-note.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/create-a-session-note.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/delete-a-session-by-identifier.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/sessions/delete-a-session-by-identifier.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/traces/create-a-trace-note.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/traces/create-a-trace-note.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/api-reference/traces/list-traces-for-a-project.mdx](docs/phoenix/sdk-api-reference/rest-api/api-reference/traces/list-traces-for-a-project.mdx)
- [skills-lock.json](skills-lock.json)

</details>



This page documents the subsystem responsible for packaging, locking, configuring, and distributing AI coding assistant skills and plugins within the Phoenix codebase. It covers the `.agents/skills` library structure, assistant configuration directories (`.claude`, `.cursor`, `.codex`), the dependency locking mechanism in `skills-lock.json`, and the `plugins/` packaging framework that prepares Phoenix skills for external marketplaces like Claude Code and Codex.

---

## 1. The `.agents/skills` Library & Architecture

The `.agents/skills` directory contains modular capabilities (skills) used by AI coding agents when operating within the Phoenix workspace. Each skill is self-contained within its own subdirectory, featuring a primary `SKILL.md` instruction file and an optional `references/` directory containing deep-dive documentation.

A skill is defined by YAML frontmatter followed by structured Markdown instructions [.agents/skills/phoenix-frontend/SKILL.md:1-6](). The frontmatter specifies metadata such as `name`, `description`, user-invocation flags, and internal visibility flags [.agents/skills/phoenix-pr-screenshot/SKILL.md:1-7]().

```
.agents/skills/
├── phoenix-frontend/
│   ├── SKILL.md
│   └── references/
│       ├── components.md
│       ├── relay.md
│       └── ...
├── phoenix-github/
│   ├── SKILL.md
│   └── scripts/
│       ├── snapshot.sh
│       ├── health.py
│       └── rollover.py
└── phoenix-pr-screenshot/
    └── SKILL.md
```

Skills interact directly with repository code entities, build pipelines, and automation tools. For instance, the frontend skill governs code conventions within `js/app/` [.agents/skills/phoenix-frontend/SKILL.md:1-10](), while automation skills execute workflows against backend static servers and issue trackers.

Sources: [.agents/skills/phoenix-frontend/SKILL.md:1-10](), [.agents/skills/phoenix-pr-screenshot/SKILL.md:1-10](), [.agents/skills/phoenix-github/SKILL.md:1-15]()

---

## 2. Skill Versioning & Locking (`skills-lock.json`)

External and shared vendor skills (such as those from Harbor or Daytona) are pinned and verified via `skills-lock.json` in the repository root. This lockfile ensures deterministic execution and integrity validation for all third-party agent capabilities.

```json
{
  "version": 1,
  "skills": {
    "create-task": {
      "source": "harbor-framework/harbor",
      "sourceType": "github",
      "skillPath": "skills/create-task/SKILL.md",
      "computedHash": "b2e66a678ae1647e8c7047b82c80a16ed33bc804bbdd10baf7fcacbe3fe4214b"
    }
  }
}
```

Each locked skill entry defines:
- `source`: The upstream repository or origin URL [skills-lock.json:1-9]().
- `sourceType`: The distribution mechanism (`github`, `well-known`, etc.) [skills-lock.json:1-34]().
- `skillPath`: The path to the skill definition file within the source repository [skills-lock.json:1-7]().
- `computedHash`: A cryptographic SHA-256 hash (`computedHash`) guaranteeing that the fetched skill content has not been tampered with [skills-lock.json:1-8]().

Sources: [skills-lock.json:1-48]()

---

## 3. Assistant Environment Configurations (`.claude`, `.cursor`, `.codex`)

Phoenix integrates tightly with AI development environments through configuration files stored in hidden configuration directories at the repository root. The primary control center for Claude Code integration resides in `.claude/settings.json` [.claude/settings.json:1-38]().

### Post-Tool-Use Hook Automation

The `.claude/settings.json` configuration establishes event-driven hooks that execute formatting, linting, migration validation, and asset compilation automatically after an agent writes or modifies code [.claude/settings.json:5-33]().

```mermaid
Title: "Agent Hook Execution Pipeline"

[AgentWriteOrEdit] --> [PostToolUseMatcher]
[PostToolUseMatcher] --> [RuffFormatCheckpy]
[PostToolUseMatcher] --> [MakeSchemaDdlpy]
[PostToolUseMatcher] --> [UvSyncPyproject]
[PostToolUseMatcher] --> [PnpmBuildOpenApi]

[RuffFormatCheckpy] -->|Executes| [uv_tool_run_ruff_format]
[MakeSchemaDdlpy] -->|Executes| [make_schema_ddl]
[UvSyncPyproject] -->|Executes| [uv_sync]
[PnpmBuildOpenApi] -->|Executes| [pnpm_install_and_build]
```

- **Python Formatting & Linting**: Automatically invokes `ruff format` and `ruff check --fix` on modified `.py` files [.claude/settings.json:10-17]().
- **Database Schema DDL**: Triggers `make schema-ddl` whenever migrations under `src/phoenix/db/migrations/versions` are altered [.claude/settings.json:18-21]().
- **Dependency Syncing**: Runs `uv sync` when `pyproject.toml` or `uv.lock` changes [.claude/settings.json:22-25]().
- **OpenAPI & Frontend Build**: Triggers `pnpm i` and `pnpm build` in the `js/` directory when `schemas/openapi.json` is updated [.claude/settings.json:26-29]().
- **Language Server Plugins**: Enables official Language Server Protocol plugins (`typescript-lsp@claude-plugins-official` and `pyright-lsp@claude-plugins-official`) for semantic analysis [.claude/settings.json:34-37]().

Sources: [.claude/settings.json:1-38]()

---

## 4. Plugin Packaging & Distribution (`plugins/`)

The `plugins/` directory packages Phoenix-specific capabilities into distributable bundles destined for AI marketplaces (such as the Claude Code and Codex plugin registries). Packaging isolates core observability logic from assistant-specific harness code.

```mermaid
Title: "Plugin Packaging Data Flow"

[PhoenixCoreSource] -->|Extracts| [AgentsSkillsLibrary]
[AgentsSkillsLibrary] -->|Packages| [PluginsDirectory]
[PluginsDirectory] -->|Publishes| [ClaudeMarketplace]
[PluginsDirectory] -->|Publishes| [CodexMarketplace]
```

During distribution packaging, skill files from `.agents/skills/` are compiled alongside manifest configurations, establishing proper licensing, version tags, and entrypoint definitions.

Sources: [.agents/skills/phoenix-frontend/SKILL.md:1-6](), [.agents/skills/phoenix-github/SKILL.md:1-10]()

---

## 5. Agent Workflow Automation & Tooling

Agent skills frequently rely on companion CLI scripts embedded within their subdirectories [.agents/skills/phoenix-github/SKILL.md:49-55](). For example, the `phoenix-github` skill bundles Python maintenance scripts in `.agents/skills/phoenix-github/scripts/` to audit issue boards, manage sprint rollovers, and generate standup reports [.agents/skills/phoenix-github/SKILL.md:50-67]().

Similarly, skills like `phoenix-pr-screenshot` execute complex integration lifecycles involving backend startup, temporary working directory isolation, browser automation, and GitHub PR media attachment (`gh pr edit --attach`) [.agents/skills/phoenix-pr-screenshot/SKILL.md:11-75]().

```mermaid
Title: "PR Screenshot Workflow Execution"

[phoenix-pr-screenshot] -->|Builds| [pnpm_run_build]
[pnpm_run_build] -->|StartsServer| [uv_run_phoenix_serve]
[uv_run_phoenix_serve] -->|Captures| [BrowserScreenshot]
[BrowserScreenshot] -->|Uploads| [gh_pr_edit_attach]
```

Sources: [.agents/skills/phoenix-pr-screenshot/SKILL.md:20-75](), [.agents/skills/phoenix-github/SKILL.md:49-67]()

---

# Page: Examples, Tutorials & Benchmarks

# Examples, Tutorials & Benchmarks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/phoenix/cookbook/evaluation/session-level-evaluation.mdx](docs/phoenix/cookbook/evaluation/session-level-evaluation.mdx)
- [examples/code_gen_agent/.gitignore](examples/code_gen_agent/.gitignore)
- [examples/code_gen_agent/.gitkeep](examples/code_gen_agent/.gitkeep)
- [examples/code_gen_agent/README.md](examples/code_gen_agent/README.md)
- [examples/code_gen_agent/agent.py](examples/code_gen_agent/agent.py)
- [examples/code_gen_agent/app.py](examples/code_gen_agent/app.py)
- [examples/code_gen_agent/requirements.txt](examples/code_gen_agent/requirements.txt)
- [examples/code_gen_agent/tools.py](examples/code_gen_agent/tools.py)
- [examples/computer_use_agent/Dockerfile](examples/computer_use_agent/Dockerfile)
- [examples/computer_use_agent/README.md](examples/computer_use_agent/README.md)
- [examples/computer_use_agent/agent.py](examples/computer_use_agent/agent.py)
- [examples/computer_use_agent/app.py](examples/computer_use_agent/app.py)
- [examples/computer_use_agent/image/.config/tint2/applications/firefox-custom.desktop](examples/computer_use_agent/image/.config/tint2/applications/firefox-custom.desktop)
- [examples/computer_use_agent/requirements.txt](examples/computer_use_agent/requirements.txt)
- [examples/computer_use_agent/tools/bash.py](examples/computer_use_agent/tools/bash.py)
- [examples/computer_use_agent/tools/computer.py](examples/computer_use_agent/tools/computer.py)
- [examples/computer_use_agent/tools/edit.py](examples/computer_use_agent/tools/edit.py)
- [examples/rag_agent/agent.py](examples/rag_agent/agent.py)
- [examples/rag_agent/app.py](examples/rag_agent/app.py)
- [examples/rag_agent/requirements.txt](examples/rag_agent/requirements.txt)
- [tutorials/evals/_run_evals_quickstart.py](tutorials/evals/_run_evals_quickstart.py)
- [tutorials/evals/bedrock_tracing_and_evals_tutorial.ipynb](tutorials/evals/bedrock_tracing_and_evals_tutorial.ipynb)
- [tutorials/evals/evaluate_agent.ipynb](tutorials/evals/evaluate_agent.ipynb)
- [tutorials/evals/openai_agents_cookbook.ipynb](tutorials/evals/openai_agents_cookbook.ipynb)
- [tutorials/evals/optimizing_llm_as_a_judge_prompts.ipynb](tutorials/evals/optimizing_llm_as_a_judge_prompts.ipynb)
- [tutorials/evals/session_level_evals.ipynb](tutorials/evals/session_level_evals.ipynb)
- [tutorials/evals/trace_level_evals.ipynb](tutorials/evals/trace_level_evals.ipynb)
- [tutorials/experiments/agents-cookbook.ipynb](tutorials/experiments/agents-cookbook.ipynb)
- [tutorials/experiments/generating_synthetic_datasets.ipynb](tutorials/experiments/generating_synthetic_datasets.ipynb)
- [tutorials/llm_ops_overview.ipynb](tutorials/llm_ops_overview.ipynb)

</details>



This page provides an overview of the educational material, interactive walkthroughs, runnable demo applications, and evaluation benchmark suites shipped with the Phoenix repository. These resources are designed to help developers quickly understand how to integrate OpenTelemetry tracing, run LLM-as-a-Judge evaluations, construct multi-turn agent workflows, and execute experiments across both Python and TypeScript ecosystems.

For deep technical details, implementation specifics, and step-by-step guides, refer to the child pages:
- Python notebooks and agent applications: [Python Notebooks & Example Agents](#7.1)
- TypeScript examples and benchmarking tools: [TypeScript Example Apps & Benchmarks](#7.2)
- Documentation architecture and Mintlify site guides: [Documentation Site & Guides](#7.3)

---

## 7.1 Python Notebooks & Example Agents

The Phoenix repository includes an extensive collection of Jupyter notebooks (`tutorials/`) and full-stack runnable agent applications (`examples/`). These materials cover fundamental LLMOps workflows, including automatic OpenTelemetry instrumentation via `phoenix.otel`, trace-level and session-level evaluations using `arize-phoenix-evals`, synthetic dataset generation, and multi-agent orchestration frameworks like LangGraph, Agno, and the OpenAI Agents SDK.

```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Interactive LLMOps Walkthroughs"] --> B["Trace & Session Evaluations"]
        A --> C["Runnable Code Generation Agent"]
        A --> D["Computer Use & RAG Agents"]
    end
    subgraph "Code Entity Space"
        B --> E["tutorials/llm_ops_overview.ipynb"]
        B --> F["tutorials/evals/trace_level_evals.ipynb"]
        C --> G["examples/code_gen_agent/app.py"]
        D --> H["examples/rag_agent/agent.py"]
    end
    style A fill:none,stroke:none
    style B fill:none,stroke:none
    style C fill:none,stroke:none
    style D fill:none,stroke:none
    style E fill:none,stroke:none
    style F fill:none,stroke:none
    style G fill:none,stroke:none
    style H fill:none,stroke:none
```

For complete details on configuring notebooks, setting up OpenInference instrumentors, and running reference agent architectures such as `code_gen_agent`, `rag_agent`, and `computer_use_agent`, see [Python Notebooks & Example Agents](#7.1).

Sources:
- `tutorials/llm_ops_overview.ipynb:1-50` [tutorials/llm_ops_overview.ipynb:1-50]()
- `tutorials/evals/trace_level_evals.ipynb:1-45` [tutorials/evals/trace_level_evals.ipynb:1-45]()
- `examples/code_gen_agent/app.py:1-35` [examples/code_gen_agent/app.py:1-35]()
- `examples/code_gen_agent/requirements.txt:1-16` [examples/code_gen_agent/requirements.txt:1-16]()

---

## 7.2 TypeScript Example Apps & Benchmarks

In addition to Python tooling, Phoenix provides TypeScript and JavaScript demonstration applications, client integrations, and evaluation benchmark suites (`js/examples/` and `js/benchmarks/`). These resources demonstrate how to capture traces from Vercel AI SDK and Mastra applications, interact with the Phoenix GraphQL/REST APIs using strongly-typed TypeScript clients, and measure agent performance against standardized evaluation benchmarks.

```mermaid
graph TD
    subgraph "Natural Language Space"
        U["TypeScript Agent Demos"] --> V["Vercel AI SDK Integration"]
        U --> W["Evaluation Benchmarks & Runner"]
    end
    subgraph "Code Entity Space"
        V --> X["js/examples/vercel-ai-sdk/"]
        W --> Y["js/benchmarks/evals-benchmarks/"]
    end
    style U fill:none,stroke:none
    style V fill:none,stroke:none
    style W fill:none,stroke:none
    style X fill:none,stroke:none
    style Y fill:none,stroke:none
```

For comprehensive documentation on TypeScript example apps, Vercel AI SDK converters, experiment runners, and evaluation benchmark suites, see [TypeScript Example Apps & Benchmarks](#7.2).

Sources:
- `js/examples/` (Implicitly referenced via monorepo structure)
- `js/benchmarks/` (Implicitly referenced via monorepo structure)

---

## 7.3 Documentation Site & Guides

The `docs/` directory houses the Mintlify-based documentation site organization, covering getting started guides, integration cookbooks, release notes, self-hosting configurations, and SDK API references. Contributions to documentation are structured around Markdown (`.mdx`) files and configuration mappings in `docs.json`.

For details on site architecture, guide organization, and contribution guidelines, see [Documentation Site & Guides](#7.3).

Sources:
- `docs/phoenix/cookbook/evaluation/session-level-evaluation.mdx` [docs/phoenix/cookbook/evaluation/session-level-evaluation.mdx:1-1]()

---

# Page: Python Notebooks & Example Agents

# Python Notebooks & Example Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/phoenix/cookbook/evaluation/session-level-evaluation.mdx](docs/phoenix/cookbook/evaluation/session-level-evaluation.mdx)
- [docs/phoenix/integrations/python/langchain.mdx](docs/phoenix/integrations/python/langchain.mdx)
- [examples/agent_framework_comparison/.gitignore](examples/agent_framework_comparison/.gitignore)
- [examples/agent_framework_comparison/README.md](examples/agent_framework_comparison/README.md)
- [examples/agent_framework_comparison/code_based_agent/main.py](examples/agent_framework_comparison/code_based_agent/main.py)
- [examples/agent_framework_comparison/code_based_agent/router.py](examples/agent_framework_comparison/code_based_agent/router.py)
- [examples/agent_framework_comparison/db/database.py](examples/agent_framework_comparison/db/database.py)
- [examples/agent_framework_comparison/db/download_traces_from_px.py](examples/agent_framework_comparison/db/download_traces_from_px.py)
- [examples/agent_framework_comparison/langgraph/analyze_data.py](examples/agent_framework_comparison/langgraph/analyze_data.py)
- [examples/agent_framework_comparison/langgraph/generate_sql_query.py](examples/agent_framework_comparison/langgraph/generate_sql_query.py)
- [examples/agent_framework_comparison/langgraph/main.py](examples/agent_framework_comparison/langgraph/main.py)
- [examples/agent_framework_comparison/langgraph/router.py](examples/agent_framework_comparison/langgraph/router.py)
- [examples/agent_framework_comparison/li_workflow/main.py](examples/agent_framework_comparison/li_workflow/main.py)
- [examples/agent_framework_comparison/li_workflow/router.py](examples/agent_framework_comparison/li_workflow/router.py)
- [examples/agent_framework_comparison/prompt_templates/router_template.py](examples/agent_framework_comparison/prompt_templates/router_template.py)
- [examples/agent_framework_comparison/requirements.txt](examples/agent_framework_comparison/requirements.txt)
- [examples/agent_framework_comparison/skills/analyze_data.py](examples/agent_framework_comparison/skills/analyze_data.py)
- [examples/agent_framework_comparison/skills/generate_sql_query.py](examples/agent_framework_comparison/skills/generate_sql_query.py)
- [examples/agent_framework_comparison/utils/save_agent_traces.py](examples/agent_framework_comparison/utils/save_agent_traces.py)
- [examples/code_gen_agent/.gitignore](examples/code_gen_agent/.gitignore)
- [examples/code_gen_agent/.gitkeep](examples/code_gen_agent/.gitkeep)
- [examples/code_gen_agent/README.md](examples/code_gen_agent/README.md)
- [examples/code_gen_agent/agent.py](examples/code_gen_agent/agent.py)
- [examples/code_gen_agent/app.py](examples/code_gen_agent/app.py)
- [examples/code_gen_agent/requirements.txt](examples/code_gen_agent/requirements.txt)
- [examples/code_gen_agent/tools.py](examples/code_gen_agent/tools.py)
- [examples/computer_use_agent/Dockerfile](examples/computer_use_agent/Dockerfile)
- [examples/computer_use_agent/README.md](examples/computer_use_agent/README.md)
- [examples/computer_use_agent/agent.py](examples/computer_use_agent/agent.py)
- [examples/computer_use_agent/app.py](examples/computer_use_agent/app.py)
- [examples/computer_use_agent/image/.config/tint2/applications/firefox-custom.desktop](examples/computer_use_agent/image/.config/tint2/applications/firefox-custom.desktop)
- [examples/computer_use_agent/requirements.txt](examples/computer_use_agent/requirements.txt)
- [examples/computer_use_agent/tools/bash.py](examples/computer_use_agent/tools/bash.py)
- [examples/computer_use_agent/tools/computer.py](examples/computer_use_agent/tools/computer.py)
- [examples/computer_use_agent/tools/edit.py](examples/computer_use_agent/tools/edit.py)
- [examples/computer_use_agent/utils.py](examples/computer_use_agent/utils.py)
- [examples/cron-evals/requirements.txt](examples/cron-evals/requirements.txt)
- [examples/rag_agent/agent.py](examples/rag_agent/agent.py)
- [examples/rag_agent/app.py](examples/rag_agent/app.py)
- [examples/rag_agent/requirements.txt](examples/rag_agent/requirements.txt)
- [tutorials/agents/langgraph/langgraph_evaluator.ipynb](tutorials/agents/langgraph/langgraph_evaluator.ipynb)
- [tutorials/agents/langgraph/langgraph_orchestrator.ipynb](tutorials/agents/langgraph/langgraph_orchestrator.ipynb)
- [tutorials/agents/langgraph/langgraph_parallel.ipynb](tutorials/agents/langgraph/langgraph_parallel.ipynb)
- [tutorials/agents/langgraph/langgraph_promptchaining.ipynb](tutorials/agents/langgraph/langgraph_promptchaining.ipynb)
- [tutorials/agents/langgraph/langgraph_router.ipynb](tutorials/agents/langgraph/langgraph_router.ipynb)
- [tutorials/evals/_run_evals_quickstart.py](tutorials/evals/_run_evals_quickstart.py)
- [tutorials/evals/bedrock_tracing_and_evals_tutorial.ipynb](tutorials/evals/bedrock_tracing_and_evals_tutorial.ipynb)
- [tutorials/evals/evals_quickstart.ipynb](tutorials/evals/evals_quickstart.ipynb)
- [tutorials/evals/evaluate_agent.ipynb](tutorials/evals/evaluate_agent.ipynb)
- [tutorials/evals/evaluate_code_readability_classifications.ipynb](tutorials/evals/evaluate_code_readability_classifications.ipynb)
- [tutorials/evals/openai_agents_cookbook.ipynb](tutorials/evals/openai_agents_cookbook.ipynb)
- [tutorials/evals/optimizing_llm_as_a_judge_prompts.ipynb](tutorials/evals/optimizing_llm_as_a_judge_prompts.ipynb)
- [tutorials/evals/session_level_evals.ipynb](tutorials/evals/session_level_evals.ipynb)
- [tutorials/evals/trace_level_evals.ipynb](tutorials/evals/trace_level_evals.ipynb)
- [tutorials/experiments/agents-cookbook.ipynb](tutorials/experiments/agents-cookbook.ipynb)
- [tutorials/experiments/datasets_and_experiments_quickstart.ipynb](tutorials/experiments/datasets_and_experiments_quickstart.ipynb)
- [tutorials/experiments/generating_synthetic_datasets.ipynb](tutorials/experiments/generating_synthetic_datasets.ipynb)
- [tutorials/experiments/run_experiments_with_llama_index.ipynb](tutorials/experiments/run_experiments_with_llama_index.ipynb)
- [tutorials/experiments/summarization.ipynb](tutorials/experiments/summarization.ipynb)
- [tutorials/experiments/txt2sql.ipynb](tutorials/experiments/txt2sql.ipynb)
- [tutorials/llm_ops_overview.ipynb](tutorials/llm_ops_overview.ipynb)
- [tutorials/mcp/tracing_between_mcp_client_and_server/.env.example](tutorials/mcp/tracing_between_mcp_client_and_server/.env.example)
- [tutorials/mcp/tracing_between_mcp_client_and_server/README.md](tutorials/mcp/tracing_between_mcp_client_and_server/README.md)
- [tutorials/mcp/tracing_between_mcp_client_and_server/client.py](tutorials/mcp/tracing_between_mcp_client_and_server/client.py)
- [tutorials/mcp/tracing_between_mcp_client_and_server/requirements.txt](tutorials/mcp/tracing_between_mcp_client_and_server/requirements.txt)
- [tutorials/mcp/tracing_between_mcp_client_and_server/server.py](tutorials/mcp/tracing_between_mcp_client_and_server/server.py)
- [tutorials/tracing/autogen_tutorial.ipynb](tutorials/tracing/autogen_tutorial.ipynb)
- [tutorials/tracing/langchain_agent_tracing_tutorial.ipynb](tutorials/tracing/langchain_agent_tracing_tutorial.ipynb)
- [tutorials/tracing/langchain_tracing_tutorial.ipynb](tutorials/tracing/langchain_tracing_tutorial.ipynb)
- [tutorials/tracing/llama_index_openai_agent_tracing_tutorial.ipynb](tutorials/tracing/llama_index_openai_agent_tracing_tutorial.ipynb)
- [tutorials/tracing/llama_index_tracing_tutorial.ipynb](tutorials/tracing/llama_index_tracing_tutorial.ipynb)
- [tutorials/tracing/openai_tracing_tutorial.ipynb](tutorials/tracing/openai_tracing_tutorial.ipynb)

</details>



## Purpose & Scope
This section covers the learning and demonstration materials shipped with the Phoenix repository under the `tutorials/` and `examples/` directories. These runnable resources demonstrate how to integrate Phoenix for OpenTelemetry tracing, perform LLM evaluations, execute structured experiments, build advanced AI agents, and trace Model Context Protocol (MCP) workflows. 

---

## 1. Tutorial Notebooks (`tutorials/`)

The `tutorials/` directory provides interactive Jupyter notebooks demonstrating core Phoenix capabilities across different framework integrations and evaluation paradigms.

### Tracing Tutorials
Tracing tutorials illustrate how to instrument popular LLM orchestration frameworks to emit OpenInference-compliant spans to a local or hosted Phoenix collector.
* **LlamaIndex Tracing**: `tutorials/tracing/llama_index_tracing_tutorial.ipynb` configures `Settings.llm` and `Settings.embed_model` using OpenAI models and hooks into LlamaIndex query engines [tutorials/tracing/llama_index_tracing_tutorial.ipynb:1-172]().
* **LangChain Tracing**: `tutorials/tracing/langchain_tracing_tutorial.ipynb` utilizes `LangChainInstrumentor` from `openinference.instrumentation.langchain` alongside `phoenix.otel.register` to capture LCEL chain runs [tutorials/tracing/langchain_tracing_tutorial.ipynb:1-186]().
* **OpenAI Client Tracing**: `tutorials/tracing/openai_tracing_tutorial.ipynb` demonstrates low-level OpenAI SDK instrumentation via `OpenAIInstrumentor` for structured data extraction tasks [tutorials/tracing/openai_tracing_tutorial.ipynb:1-170]().
* **Agent Tracing**: Notebooks such as `tutorials/tracing/llama_index_openai_agent_tracing_tutorial.ipynb` and `tutorials/tracing/langchain_agent_tracing_tutorial.ipynb` instrument multi-turn agent execution loops and tool calls.

### Evaluation & Experimentation Tutorials
Evaluation and experimentation workflows bridge tracing with data science metrics:
* **Text-to-SQL Experiments**: `tutorials/experiments/txt2sql.ipynb` uses DuckDB, OpenAI, and `phoenix.client.AsyncClient` to perform systematic evaluation-driven development on SQL generation tasks [tutorials/experiments/txt2sql.ipynb:1-194]().
* **LlamaIndex Experiments**: `tutorials/experiments/run_experiments_with_llama_index.ipynb` demonstrates dataset creation, dataset upload via `Client().datasets.create_dataset`, and executing retrieval evaluations [tutorials/experiments/run_experiments_with_llama_index.ipynb:1-207]().
* **Code Readability Evals**: `tutorials/evals/evaluate_code_readability_classifications.ipynb` downloads benchmark datasets and runs binary classification evaluators [tutorials/evals/evaluate_code_readability_classifications.ipynb:1-205]().
* **LLMOps Overview**: `tutorials/llm_ops_overview.ipynb` builds an agent with the Agno framework (`agno`), integrates Tavily search and Open-Meteo weather APIs, and registers OpenTelemetry tracing [tutorials/llm_ops_overview.ipynb:1-201]().

### Model Context Protocol (MCP) Tracing
The MCP tutorial directory (`tutorials/mcp/tracing_between_mcp_client_and_server/`) provides examples for tracing communication between MCP clients and servers using `openinference-instrumentation-mcp` and `strawberry-graphql` [tutorials/mcp/tracing_between_mcp_client_and_server/requirements.txt:1-13]().

Sources:
- `tutorials/tracing/llama_index_tracing_tutorial.ipynb:1-172`
- `tutorials/tracing/langchain_tracing_tutorial.ipynb:1-186`
- `tutorials/experiments/txt2sql.ipynb:1-194`
- `tutorials/llm_ops_overview.ipynb:1-201`
- `tutorials/mcp/tracing_between_mcp_client_and_server/requirements.txt:1-13`

---

## 2. Runnable Example Agent Applications (`examples/`)

The `examples/` directory contains production-style runnable agent applications demonstrating advanced orchestration patterns, graphical user interfaces, and framework comparisons.

### Code Generation Agent (`examples/code_gen_agent`)
The code generation agent combines LangChain, LangGraph, and Gradio to provide an interactive interface for generating and evaluating code.
* Dependencies include `arize-phoenix`, `arize-phoenix-evals`, `langchain`, `langgraph`, and `gradio` [examples/code_gen_agent/requirements.txt:1-16]().
* The application entry point is `examples/code_gen_agent/app.py`, which sets up tracing and mounts the user interface.

### Retrieval-Augmented Generation Agent (`examples/rag_agent`)
The `rag_agent` application implements a RAG workflow with instrumentation for tracking retrieval steps, document reranking, and generation latency.

### Computer Use Agent (`examples/computer_use_agent`)
The `computer_use_agent` provides tool implementations (such as `examples/computer_use_agent/tools/edit.py`) enabling LLMs to interact with file systems and execution environments.

### Agent Framework Comparison (`examples/agent_framework_comparison`)
This directory provides a multi-framework evaluation suite comparing LangChain, LangGraph, LlamaIndex, AutoGen, and CrewAI [examples/agent_framework_comparison/requirements.txt:1-19]().
* It includes shared database schemas (`examples/agent_framework_comparison/db/database.py`), reusable skills (`examples/agent_framework_comparison/skills/`), and trace saving utilities (`examples/agent_framework_comparison/utils/save_agent_traces.py`).

Sources:
- `examples/code_gen_agent/requirements.txt:1-16`
- `examples/agent_framework_comparison/requirements.txt:1-19`

---

## 3. Architecture & Data Flow

The following diagrams illustrate how user interactions in notebooks and example applications flow through instrumentation libraries into the Phoenix backend and client evaluation SDKs.

### Trace Ingestion Data Flow
```mermaid
graph TD
    subgraph "Application Space"
        A["Notebook or Example App"] --> B["OpenInference Instrumentation"]
        B --> C["OpenTelemetry TracerProvider"]
    end
    subgraph "Transport & Collection"
        C -->|OTLP gRPC or HTTP| D["Phoenix Server /v1/traces"]
    end
    subgraph "Storage & Analysis"
        D --> E["Span Ingestion Pipeline"]
        E --> F["Phoenix SQLite / PostgreSQL DB"]
        F --> G["Phoenix Client SDK & UI"]
    end
    
    style A fill:#fff,stroke:#000,stroke-width:1px
    style D fill:#fff,stroke:#000,stroke-width:1px
    style G fill:#fff,stroke:#000,stroke-width:1px
```
Sources:
- `tutorials/tracing/langchain_tracing_tutorial.ipynb:80-95`
- `tutorials/experiments/txt2sql.ipynb:80-95`

### Experimentation & Evaluation Pipeline
```mermaid
graph TD
    subgraph "Client SDK"
        H["AsyncClient"] --> I["datasets.create_dataset"]
        I --> J["async_evaluate_dataframe"]
    end
    subgraph "Evaluation Execution"
        J --> K["LLM Evaluators / Metrics"]
        K -->|Calls Model| L["OpenAI / ChatOpenAI"]
    end
    subgraph "Results & Tracking"
        J --> M["Annotation Storage"]
        M --> N["Phoenix UI Dashboard"]
    end

    style H fill:#fff,stroke:#000,stroke-width:1px
    style J fill:#fff,stroke:#000,stroke-width:1px
    style N fill:#fff,stroke:#000,stroke-width:1px
```
Sources:
- `tutorials/experiments/run_experiments_with_llama_index.ipynb:45-55`
- `tutorials/tracing/langchain_tracing_tutorial.ipynb:80-92`

---

# Page: TypeScript Example Apps & Benchmarks

# TypeScript Example Apps & Benchmarks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/cla.yml](.github/workflows/cla.yml)
- [CLA.md](CLA.md)
- [docs/phoenix/cookbook/ai-engineering-workflows/iterative-evaluation-and-experimentation-workflow-typescript.mdx](docs/phoenix/cookbook/ai-engineering-workflows/iterative-evaluation-and-experimentation-workflow-typescript.mdx)
- [docs/phoenix/environments.mdx](docs/phoenix/environments.mdx)
- [docs/phoenix/integrations/typescript/mastra/mastra-tracing.mdx](docs/phoenix/integrations/typescript/mastra/mastra-tracing.mdx)
- [docs/phoenix/integrations/typescript/vercel.mdx](docs/phoenix/integrations/typescript/vercel.mdx)
- [docs/phoenix/integrations/typescript/vercel/eve-tracing.mdx](docs/phoenix/integrations/typescript/vercel/eve-tracing.mdx)
- [js/benchmarks/evals-benchmarks/package.json](js/benchmarks/evals-benchmarks/package.json)
- [js/examples/apps/cli-agent-starter-kit/.env.example](js/examples/apps/cli-agent-starter-kit/.env.example)
- [js/examples/apps/cli-agent-starter-kit/.gitignore](js/examples/apps/cli-agent-starter-kit/.gitignore)
- [js/examples/apps/cli-agent-starter-kit/AGENTS.md](js/examples/apps/cli-agent-starter-kit/AGENTS.md)
- [js/examples/apps/cli-agent-starter-kit/CLAUDE.md](js/examples/apps/cli-agent-starter-kit/CLAUDE.md)
- [js/examples/apps/cli-agent-starter-kit/README.md](js/examples/apps/cli-agent-starter-kit/README.md)
- [js/examples/apps/cli-agent-starter-kit/docker-compose.yml](js/examples/apps/cli-agent-starter-kit/docker-compose.yml)
- [js/examples/apps/cli-agent-starter-kit/scripts/ensure-phoenix.sh](js/examples/apps/cli-agent-starter-kit/scripts/ensure-phoenix.sh)
- [js/examples/apps/cli-agent-starter-kit/src/cli.ts](js/examples/apps/cli-agent-starter-kit/src/cli.ts)
- [js/examples/apps/cli-agent-starter-kit/src/index.ts](js/examples/apps/cli-agent-starter-kit/src/index.ts)
- [js/examples/apps/cli-agent-starter-kit/src/instrumentation.ts](js/examples/apps/cli-agent-starter-kit/src/instrumentation.ts)
- [js/examples/apps/cli-agent-starter-kit/src/tools/datetime.ts](js/examples/apps/cli-agent-starter-kit/src/tools/datetime.ts)
- [js/examples/apps/cli-agent-starter-kit/src/tools/index.ts](js/examples/apps/cli-agent-starter-kit/src/tools/index.ts)
- [js/examples/apps/cli-agent-starter-kit/src/tools/mcp.ts](js/examples/apps/cli-agent-starter-kit/src/tools/mcp.ts)
- [js/examples/apps/cli-agent-starter-kit/src/ui/welcome.ts](js/examples/apps/cli-agent-starter-kit/src/ui/welcome.ts)
- [js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md](js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md)
- [js/examples/apps/demo-document-relevancy-experiment/package.json](js/examples/apps/demo-document-relevancy-experiment/package.json)
- [js/examples/apps/eve-agent/.gitignore](js/examples/apps/eve-agent/.gitignore)
- [js/examples/apps/eve-agent/README.md](js/examples/apps/eve-agent/README.md)
- [js/examples/apps/eve-agent/agent/agent.ts](js/examples/apps/eve-agent/agent/agent.ts)
- [js/examples/apps/eve-agent/agent/channels/eve.ts](js/examples/apps/eve-agent/agent/channels/eve.ts)
- [js/examples/apps/eve-agent/agent/instructions.md](js/examples/apps/eve-agent/agent/instructions.md)
- [js/examples/apps/eve-agent/agent/instrumentation.ts](js/examples/apps/eve-agent/agent/instrumentation.ts)
- [js/examples/apps/experiments-quickstart/package.json](js/examples/apps/experiments-quickstart/package.json)
- [js/examples/apps/langchain-quickstart/package.json](js/examples/apps/langchain-quickstart/package.json)
- [js/examples/apps/mastra-agent/README.md](js/examples/apps/mastra-agent/README.md)
- [js/examples/apps/mastra-agent/package.json](js/examples/apps/mastra-agent/package.json)
- [js/examples/apps/mastra-agent/src/mastra/index.ts](js/examples/apps/mastra-agent/src/mastra/index.ts)
- [js/examples/apps/mastra-quickstart/README.md](js/examples/apps/mastra-quickstart/README.md)
- [js/examples/apps/mastra-quickstart/package.json](js/examples/apps/mastra-quickstart/package.json)
- [js/examples/apps/mastra-quickstart/src/mastra/index.ts](js/examples/apps/mastra-quickstart/src/mastra/index.ts)
- [js/examples/apps/tracing-tutorial/package.json](js/examples/apps/tracing-tutorial/package.json)
- [js/packages/phoenix-cli/src/setup/copy.ts](js/packages/phoenix-cli/src/setup/copy.ts)
- [js/packages/phoenix-cli/src/setup/prompts/instrumentationPrompt.ts](js/packages/phoenix-cli/src/setup/prompts/instrumentationPrompt.ts)
- [js/packages/phoenix-cli/test/setup/instrumentationPrompt.test.ts](js/packages/phoenix-cli/test/setup/instrumentationPrompt.test.ts)
- [js/packages/phoenix-client/examples/create_dataset_from_spans.ts](js/packages/phoenix-client/examples/create_dataset_from_spans.ts)
- [js/packages/phoenix-client/examples/delete_experiment_project.ts](js/packages/phoenix-client/examples/delete_experiment_project.ts)
- [js/packages/phoenix-client/examples/resume_evaluation.ts](js/packages/phoenix-client/examples/resume_evaluation.ts)
- [js/packages/phoenix-client/src/experiments/createExperiment.ts](js/packages/phoenix-client/src/experiments/createExperiment.ts)
- [js/packages/phoenix-client/src/experiments/deleteExperiment.ts](js/packages/phoenix-client/src/experiments/deleteExperiment.ts)
- [js/packages/phoenix-client/src/experiments/listExperiments.ts](js/packages/phoenix-client/src/experiments/listExperiments.ts)
- [js/packages/phoenix-client/test/experiments/deleteExperiment.test.ts](js/packages/phoenix-client/test/experiments/deleteExperiment.test.ts)
- [js/packages/phoenix-config/README.md](js/packages/phoenix-config/README.md)
- [packages/phoenix-client/docs/source/api/sessions.rst](packages/phoenix-client/docs/source/api/sessions.rst)
- [packages/phoenix-client/docs/source/index.md](packages/phoenix-client/docs/source/index.md)

</details>



This page documents the TypeScript example applications, integration templates, and evaluation benchmark suites located under the `js/examples/` and `js/benchmarks/` directories in the Phoenix monorepo [js/examples/apps/mastra-quickstart/package.json:1-44](). These applications serve as reference architectures, quickstart guides, and test harnesses demonstrating how to ingest traces, configure OpenTelemetry collectors, execute experiments, and benchmark LLM evaluators using the Phoenix TypeScript SDKs (`@arizeai/phoenix-client`, `@arizeai/phoenix-evals`, `@arizeai/phoenix-otel`) [js/benchmarks/evals-benchmarks/package.json:1-25]().

---

## 1. Monorepo Example Structure & Architecture

The Phoenix TypeScript workspace provides runnable examples categorized by framework and use case. Each example relies on workspace packages to communicate with a local or remote Phoenix instance.

```
js/
├── benchmarks/
│   └── evals-benchmarks/         # Vitest-based evaluator benchmark suites
└── examples/
    ├── apps/
    │   ├── cli-agent-starter-kit/ # CLI agent framework with tool calling
    │   ├── demo-document-relevancy-experiment/ # Document relevancy dataset/experiment runner
    │   ├── eve-agent/             # Vercel AI SDK multi-channel agent
    │   ├── experiments-quickstart/# Dataset versioning and experiment evaluation
    │   ├── langchain-quickstart/  # LangChain TypeScript trace instrumentation
    │   ├── mastra-agent/          # Mastra movie recommendation agent with tracing
    │   ├── mastra-quickstart/     # Mastra framework integration template
    │   └── tracing-tutorial/      # OpenTelemetry and manual span tracing tutorial
```

### Configuration & Environment Data Flow

TypeScript apps interact with Phoenix via two primary environment variables governing trace export and API calls [docs/phoenix/environments.mdx:70-80]():
- `PHOENIX_COLLECTOR_ENDPOINT`: Target for OpenTelemetry span export (usually suffixed with `/v1/traces` for OTLP/HTTP exporters) [docs/phoenix/integrations/typescript/mastra/mastra-tracing.mdx:25-32]().
- `PHOENIX_ENDPOINT`: Base URL for REST/GraphQL resource APIs (client queries, datasets, experiments) [js/examples/apps/mastra-agent/README.md:37-43]().

Diagram: TypeScript Application to Phoenix Data Flow Architecture

```mermaid
graph TD
    subgraph "Natural Language Space: TypeScript Application Runtime"
        A["Mastra/Vercel App"] -->| "OpenTelemetry Span Export" | B["ArizeExporter"]
        C["Experiment Runner"] -->| "REST API Calls" | D["PhoenixClient"]
    end

    subgraph "Code Entity Space: Phoenix Ingestion Pipeline"
        B -->| "POST /v1/traces" | E["OTLP Ingestion Handler"]
        D -->| "GET/POST /v1/datasets" | F["Phoenix REST API Router"]
        E -->| "Batch Insertion" | G[(SQLite / PostgreSQL DB)]
        F -->| "Query Execution" | G
    end

    classDef default fill:none,stroke:#000,stroke-width:1px;
```
Sources: `js/examples/apps/mastra-quickstart/package.json:1-44()`, `docs/phoenix/integrations/typescript/mastra/mastra-tracing.mdx:1-73()`

---

## 2. Mastra Agent Framework Integration

The Mastra examples (`mastra-quickstart` and `mastra-agent`) demonstrate how to instrument agentic workflows, multi-turn conversations, and tool calling loops using Mastra's observability layer [js/examples/apps/mastra-agent/README.md:1-98]().

### Implementation Details

Mastra utilizes `@mastra/arize` to dispatch OpenTelemetry spans. Because Mastra's `ArizeExporter` POSTs payloads verbatim without auto-appending the OTLP path, the endpoint configuration requires explicit inclusion of `/v1/traces` [docs/phoenix/integrations/typescript/mastra/mastra-tracing.mdx:31-34]().

```typescript
import { Mastra } from "@mastra/core";
import { Observability } from "@mastra/observability";
import { ArizeExporter } from "@mastra/arize";

export const mastra = new Mastra({
  observability: new Observability({
    configs: {
      arize: {
        serviceName: process.env.PHOENIX_PROJECT_NAME || "mastra-service",
        exporters: [
          new ArizeExporter({
            endpoint: process.env.PHOENIX_COLLECTOR_ENDPOINT, // e.g., http://localhost:6006/v1/traces
            apiKey: process.env.PHOENIX_API_KEY,
            projectName: process.env.PHOENIX_PROJECT_NAME,
          }),
        ],
      },
    },
  }),
});
```
Sources: `docs/phoenix/integrations/typescript/mastra/mastra-tracing.mdx:37-61()`, `js/examples/apps/mastra-quickstart/package.json:1-44()`

Diagram: Mastra Observability Pipeline Entities

```mermaid
graph TD
    subgraph "Natural Language Space: Agent Execution"
        MA["Mastra Agent"] -->| "Tool Execution & LLM Call" | MO["Observability Config"]
    end

    subgraph "Code Entity Space: Exporter Mapping"
        MO -->| "Instantiates" | AE["ArizeExporter"]
        AE -->| "Sends OTLP Payload" | PE["PHOENIX_COLLECTOR_ENDPOINT"]
        PE -->| "Ingests Spans" | SRV["Phoenix Server"]
    end

    classDef default fill:none,stroke:#000,stroke-width:1px;
```
Sources: `docs/phoenix/integrations/typescript/mastra/mastra-tracing.mdx:37-61()`

---

## 3. Vercel AI SDK & Tracing Tutorials

The `tracing-tutorial` and `experiments-quickstart` applications demonstrate manual and automated span instrumentation for applications built with the Vercel AI (`ai`) SDK and `@ai-sdk/openai` [js/examples/apps/tracing-tutorial/package.json:1-28](), [js/examples/apps/experiments-quickstart/package.json:1-25]().

### Key Components

- **`tracing-tutorial`**: Implements support agent workflows, logging multi-turn chat sessions and evaluating traces programmatically via `evaluate-traces.ts` [js/examples/apps/tracing-tutorial/package.json:7-12]().
- **`experiments-quickstart`**: Demonstrates dataset creation, prompt versioning, and running offline evaluations against recorded traces using `@arizeai/phoenix-client` and `@arizeai/phoenix-evals`.

Sources: `js/examples/apps/tracing-tutorial/package.json:1-28()`, `js/examples/apps/experiments-quickstart/package.json:1-25()`

---

## 4. CLI Agent Starter Kit & Eve Agent

The `cli-agent-starter-kit` and `eve-agent` directories provide interactive command-line and multi-channel agent templates configured with Phoenix diagnostics and Model Context Protocol (MCP) tool integrations.

### Structure & Runtime Flow
- **`cli-agent-starter-kit/src/instrumentation.ts`**: Initializes OpenTelemetry tracing before application bootstrap.
- **`eve-agent/agent/instrumentation.ts`**: Configures telemetry collectors for Vercel AI SDK agents deployed across multiple channels.

Sources: `js/examples/apps/cli-agent-starter-kit/src/instrumentation.ts:1-1()`, `js/examples/apps/eve-agent/agent/instrumentation.ts:1-1()`

---

## 5. Experiment Runners & Custom Evaluation Apps

The `demo-document-relevancy-experiment` app illustrates how to execute programmatic retrieval-augmented generation (RAG) evaluations using `@arizeai/phoenix-evals` [js/examples/apps/demo-document-relevancy-experiment/package.json:1-22]().

### Execution Script

The experiment runner executes via `tsx`:
```json
{
  "scripts": {
    "start": "tsx experiment.ts"
  }
}
```
Sources: `js/examples/apps/demo-document-relevancy-experiment/package.json:7-9()`

---

## 6. Evals Benchmarks Suite (`js/benchmarks/evals-benchmarks`)

The `evals-benchmarks` package provides Vitest-based benchmark suites designed to test the correctness, performance, and reliability of Phoenix LLM evaluators [js/benchmarks/evals-benchmarks/package.json:1-25]().

### Package Configuration & Scripts

```json
{
  "name": "evals-benchmarks",
  "scripts": {
    "build": "tsc",
    "evals": "vitest run --config phoenix.vitest.config.ts",
    "evals:local": "PHOENIX_TEST_TRACKING=false vitest run --config phoenix.vitest.config.ts",
    "evals:watch": "vitest watch --config phoenix.vitest.config.ts"
  }
}
```
Sources: `js/benchmarks/evals-benchmarks/package.json:7-12()`

### Evaluation Test Harness Architecture

The test suite runs evaluator functions against ground-truth benchmark datasets, validating metric scores produced by `@arizeai/phoenix-evals` against expected classifications.

Sources: `js/benchmarks/evals-benchmarks/package.json:1-25()`

---

# Page: Documentation Site & Guides

# Documentation Site & Guides

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs.json](docs.json)
- [docs/PROMPT.md](docs/PROMPT.md)
- [docs/phoenix.mdx](docs/phoenix.mdx)
- [docs/phoenix/cookbook/tracing/claude-managed-agents-guide.mdx](docs/phoenix/cookbook/tracing/claude-managed-agents-guide.mdx)
- [docs/phoenix/cookbook/tracing/cookbooks.mdx](docs/phoenix/cookbook/tracing/cookbooks.mdx)
- [docs/phoenix/cookbook/tracing/identify-high-signal-traces.mdx](docs/phoenix/cookbook/tracing/identify-high-signal-traces.mdx)
- [docs/phoenix/datasets-and-experiments/how-to-datasets/exporting-datasets.mdx](docs/phoenix/datasets-and-experiments/how-to-datasets/exporting-datasets.mdx)
- [docs/phoenix/datasets-and-experiments/quickstart-datasets.mdx](docs/phoenix/datasets-and-experiments/quickstart-datasets.mdx)
- [docs/phoenix/datasets-and-experiments/tutorial/defining-the-dataset.mdx](docs/phoenix/datasets-and-experiments/tutorial/defining-the-dataset.mdx)
- [docs/phoenix/datasets-and-experiments/tutorial/iteration-workflow-experiments.mdx](docs/phoenix/datasets-and-experiments/tutorial/iteration-workflow-experiments.mdx)
- [docs/phoenix/datasets-and-experiments/tutorial/run-experiments-with-code-evals.mdx](docs/phoenix/datasets-and-experiments/tutorial/run-experiments-with-code-evals.mdx)
- [docs/phoenix/datasets-and-experiments/tutorial/run-experiments-with-llm-judge.mdx](docs/phoenix/datasets-and-experiments/tutorial/run-experiments-with-llm-judge.mdx)
- [docs/phoenix/evaluation/concepts-evals/evaluating-multi-agent-systems.mdx](docs/phoenix/evaluation/concepts-evals/evaluating-multi-agent-systems.mdx)
- [docs/phoenix/evaluation/llm-evals.mdx](docs/phoenix/evaluation/llm-evals.mdx)
- [docs/phoenix/evaluation/python-quickstart.mdx](docs/phoenix/evaluation/python-quickstart.mdx)
- [docs/phoenix/evaluation/typescript-quickstart.mdx](docs/phoenix/evaluation/typescript-quickstart.mdx)
- [docs/phoenix/get-started.mdx](docs/phoenix/get-started.mdx)
- [docs/phoenix/get-started/get-started-evaluations.mdx](docs/phoenix/get-started/get-started-evaluations.mdx)
- [docs/phoenix/get-started/get-started-tracing.mdx](docs/phoenix/get-started/get-started-tracing.mdx)
- [docs/phoenix/integrations.mdx](docs/phoenix/integrations.mdx)
- [docs/phoenix/integrations/developer-tools/coding-agents.mdx](docs/phoenix/integrations/developer-tools/coding-agents.mdx)
- [docs/phoenix/integrations/llm-providers/anthropic.mdx](docs/phoenix/integrations/llm-providers/anthropic.mdx)
- [docs/phoenix/integrations/llm-providers/cohere.mdx](docs/phoenix/integrations/llm-providers/cohere.mdx)
- [docs/phoenix/integrations/llm-providers/cohere/cohere-tracing.mdx](docs/phoenix/integrations/llm-providers/cohere/cohere-tracing.mdx)
- [docs/phoenix/integrations/platforms/claude-managed-agents.mdx](docs/phoenix/integrations/platforms/claude-managed-agents.mdx)
- [docs/phoenix/integrations/platforms/claude-managed-agents/claude-managed-agents-tracing.mdx](docs/phoenix/integrations/platforms/claude-managed-agents/claude-managed-agents-tracing.mdx)
- [docs/phoenix/integrations/platforms/scalekit.mdx](docs/phoenix/integrations/platforms/scalekit.mdx)
- [docs/phoenix/integrations/platforms/scalekit/scalekit-tracing.mdx](docs/phoenix/integrations/platforms/scalekit/scalekit-tracing.mdx)
- [docs/phoenix/integrations/python/google-adk/google-adk-tracing.mdx](docs/phoenix/integrations/python/google-adk/google-adk-tracing.mdx)
- [docs/phoenix/integrations/python/graphite/graphite-integration-guide.mdx](docs/phoenix/integrations/python/graphite/graphite-integration-guide.mdx)
- [docs/phoenix/integrations/python/pydantic/pydantic-evals.mdx](docs/phoenix/integrations/python/pydantic/pydantic-evals.mdx)
- [docs/phoenix/llms.txt](docs/phoenix/llms.txt)
- [docs/phoenix/production-guide.mdx](docs/phoenix/production-guide.mdx)
- [docs/phoenix/release-notes/01-2025/01-18-2025-automatic-and-manual-span-tracing.mdx](docs/phoenix/release-notes/01-2025/01-18-2025-automatic-and-manual-span-tracing.mdx)
- [docs/phoenix/release-notes/07-2025/07-07-2025-databse-disk-usage-monitor.mdx](docs/phoenix/release-notes/07-2025/07-07-2025-databse-disk-usage-monitor.mdx)
- [docs/phoenix/release-notes/10-2025/10-10-2025-viewer-role.mdx](docs/phoenix/release-notes/10-2025/10-10-2025-viewer-role.mdx)
- [docs/phoenix/release-notes/10-2025/10-20-2025-splits.mdx](docs/phoenix/release-notes/10-2025/10-20-2025-splits.mdx)
- [docs/phoenix/resources/frequently-asked-questions.mdx](docs/phoenix/resources/frequently-asked-questions.mdx)
- [docs/phoenix/resources/frequently-asked-questions/what-is-my-phoenix-endpoint.mdx](docs/phoenix/resources/frequently-asked-questions/what-is-my-phoenix-endpoint.mdx)
- [docs/phoenix/resources/frequently-asked-questions/what-is-the-difference-between-phoenix-and-arize.mdx](docs/phoenix/resources/frequently-asked-questions/what-is-the-difference-between-phoenix-and-arize.mdx)
- [docs/phoenix/resources/phoenix-to-arize-ax-migration.mdx](docs/phoenix/resources/phoenix-to-arize-ax-migration.mdx)
- [docs/phoenix/resources/python-api.mdx](docs/phoenix/resources/python-api.mdx)
- [docs/phoenix/resources/typescript-api.mdx](docs/phoenix/resources/typescript-api.mdx)
- [docs/phoenix/sdk-api-reference.mdx](docs/phoenix/sdk-api-reference.mdx)
- [docs/phoenix/sdk-api-reference/python/arize-phoenix-otel.mdx](docs/phoenix/sdk-api-reference/python/arize-phoenix-otel.mdx)
- [docs/phoenix/sdk-api-reference/rest-api/overview.mdx](docs/phoenix/sdk-api-reference/rest-api/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/overview.mdx](docs/phoenix/sdk-api-reference/typescript/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/datasets.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/datasets.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-evals/phoenix-integration.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-evals/phoenix-integration.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx)
- [docs/phoenix/self-hosting.mdx](docs/phoenix/self-hosting.mdx)
- [docs/phoenix/self-hosting/architecture.mdx](docs/phoenix/self-hosting/architecture.mdx)
- [docs/phoenix/self-hosting/features/management.mdx](docs/phoenix/self-hosting/features/management.mdx)
- [docs/phoenix/self-hosting/security/privacy.mdx](docs/phoenix/self-hosting/security/privacy.mdx)
- [docs/phoenix/settings/access-control-rbac.mdx](docs/phoenix/settings/access-control-rbac.mdx)
- [docs/phoenix/settings/data-retention.mdx](docs/phoenix/settings/data-retention.mdx)
- [docs/phoenix/sitemap.xml](docs/phoenix/sitemap.xml)
- [docs/phoenix/tracing/concepts-tracing/faqs-tracing.mdx](docs/phoenix/tracing/concepts-tracing/faqs-tracing.mdx)
- [docs/phoenix/tracing/concepts-tracing/otel-openinference/phoenix-otel-helpers.mdx](docs/phoenix/tracing/concepts-tracing/otel-openinference/phoenix-otel-helpers.mdx)
- [docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/importing-existing-traces.mdx](docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/importing-existing-traces.mdx)
- [docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/retrieve-traces-via-cli.mdx](docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/retrieve-traces-via-cli.mdx)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing.mdx)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-using-phoenix-otel.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-using-phoenix-otel.mdx)
- [docs/phoenix/tracing/llm-traces.mdx](docs/phoenix/tracing/llm-traces.mdx)
- [docs/phoenix/tracing/llm-traces/metrics.mdx](docs/phoenix/tracing/llm-traces/metrics.mdx)
- [docs/phoenix/tracing/llm-traces/projects.mdx](docs/phoenix/tracing/llm-traces/projects.mdx)
- [docs/phoenix/user-guide.mdx](docs/phoenix/user-guide.mdx)
- [docs/sitemap.xml](docs/sitemap.xml)
- [docs/snippets/agent-assisted-onboarding-prereq.mdx](docs/snippets/agent-assisted-onboarding-prereq.mdx)
- [docs/snippets/agent-assisted-onboarding.mdx](docs/snippets/agent-assisted-onboarding.mdx)
- [docs/snippets/connect-to-phoenix-env.mdx](docs/snippets/connect-to-phoenix-env.mdx)
- [js/.gitignore](js/.gitignore)
- [js/packages/phoenix-client/src/datasets/createDatasetSplit.ts](js/packages/phoenix-client/src/datasets/createDatasetSplit.ts)
- [js/packages/phoenix-client/src/datasets/deleteDatasetSplit.ts](js/packages/phoenix-client/src/datasets/deleteDatasetSplit.ts)
- [js/packages/phoenix-client/src/datasets/index.ts](js/packages/phoenix-client/src/datasets/index.ts)
- [js/packages/phoenix-client/src/datasets/resolveDatasetIdentifier.ts](js/packages/phoenix-client/src/datasets/resolveDatasetIdentifier.ts)
- [js/packages/phoenix-client/src/datasets/updateDatasetSplit.ts](js/packages/phoenix-client/src/datasets/updateDatasetSplit.ts)
- [packages/phoenix-client/src/phoenix/client/constants/__init__.py](packages/phoenix-client/src/phoenix/client/constants/__init__.py)
- [scripts/generate_sitemap.py](scripts/generate_sitemap.py)
- [sitemap.xml](sitemap.xml)
- [tutorials/experiments/python_experiments_quickstart.ipynb](tutorials/experiments/python_experiments_quickstart.ipynb)
- [tutorials/quickstarts/python_quickstart.ipynb](tutorials/quickstarts/python_quickstart.ipynb)

</details>



## Purpose and Scope

This page documents the organization, generation pipeline, and contribution workflows for the Arize Phoenix documentation site. Powered by **Mintlify**, the documentation infrastructure bridges conceptual user guides, integration catalogs, cookbook tutorials, self-hosting manuals, and auto-generated SDK API references. 

---

## 1. Mintlify Configuration & Site Architecture

The Phoenix documentation is declared and structured via the top-level configuration manifest [docs.json](). This file defines the global theme, color schemes (`#00769E` primary, `#39C7FF` light, `#009DD2` dark), typography (`Geist`), contextual AI assist options (`copy`, `view`, `chatgpt`, `claude`, `perplexity`), and the multi-level navigation tree [docs.json:1-174]().

The site content consists of Markdown (`.md`) and MDX (`.mdx`) files located in the `docs/phoenix/` directory. The navigation object in [docs.json]() organizes pages into structured tabs, groups, and sub-groups (such as *Quickstart*, *Coding Agents*, *Tracing*, *Evaluation*, and *API Reference*).

```mermaid
graph TD
    A["User Navigation Request"] --> B["Mintlify Config (docs.json)"]
    B --> C["Tab: Documentation"]
    C --> D["Group: Quickstart (docs/phoenix/get-started)"]
    C --> E["Group: Tracing (docs/phoenix/tracing)"]
    C --> F["Group: Evaluation (docs/phoenix/evaluation)"]
    D --> G["Leaf MDX: get-started-tracing.mdx"]
    E --> H["Leaf MDX: llm-traces.mdx"]
    
    sub5["Code Entity Space"]
    style sub5 fill:none,stroke:none
    B -.->|Defines routing| I["docs.json"]
    G -.->|Maps to file| J["docs/phoenix/get-started/get-started-tracing.mdx"]
    H -.->|Maps to file| K["docs/phoenix/tracing/llm-traces.mdx"]
```
*Diagram 1: Mintlify Navigation & File Mapping Structure*

Sources: [docs.json:1-174](), [docs/phoenix.mdx:1-103]()

---

## 2. Content Sections & Organization

The documentation site is divided into distinct functional verticals:

1. **Get-Started Guides**: Rapid onboarding tutorials (`docs/phoenix/get-started`) demonstrating local server startup [docs/phoenix/get-started.mdx](), OpenTelemetry instrumentation [docs/phoenix/get-started/get-started-tracing.mdx](), and experiment evaluation workflows [docs/phoenix/get-started/get-started-evaluations.mdx]().
2. **Integrations Catalog**: Comprehensive guides for AI frameworks, LLM providers, and coding agents [docs/phoenix/integrations.mdx]() detailing native auto-instrumentation packages [docs/phoenix/integrations/developer-tools/coding-agents.mdx]().
3. **Cookbook & Tutorials**: End-to-end recipes showing advanced patterns like custom evaluators, multi-turn session tracking, and production metric monitoring [docs/phoenix/llms.txt:24-30]().
4. **Self-Hosting & Production Guides**: Operational documentation covering Docker deployment, Kubernetes Helm charts, environment variable tuning, security, and privacy compliance [docs/phoenix/self-hosting.mdx]().
5. **SDK API Reference**: Programmatic reference documentation covering Python clients, `@arizeai/phoenix-otel`, REST API endpoints, and GraphQL schemas [docs/phoenix/sdk-api-reference.mdx]().

```mermaid
graph TD
    A["Documentation Root (docs/phoenix)"] --> B["Get-Started Guides"]
    A --> C["Integrations Catalog"]
    A --> D["Cookbook & Tutorials"]
    A --> E["Self-Hosting Manuals"]
    A --> F["SDK API Reference"]
    
    B --> B1["docs/phoenix/get-started.mdx"]
    C --> C1["docs/phoenix/integrations.mdx"]
    D --> D1["docs/phoenix/tracing/tutorial/"]
    E --> E1["docs/phoenix/self-hosting.mdx"]
    F --> F1["docs/phoenix/sdk-api-reference.mdx"]
```
*Diagram 2: Content Hierarchy Layout*

Sources: [docs/phoenix/integrations.mdx:1-41](), [docs/phoenix/get-started/get-started-tracing.mdx:1-103]()

---

## 3. Sitemap Generation & Search Indexing

To ensure search engine discoverability and accurate indexing by LLM scraping tools, Phoenix maintains an XML sitemap at [docs/phoenix/sitemap.xml]() and the index file [docs/phoenix/llms.txt]().

The sitemap lists all canonical URLs for documentation pages along with their modification timestamps [docs/phoenix/sitemap.xml:1-172](). Sitemap synchronization is automated via Python scripts in the repository:

```mermaid
graph TD
    A["CI / Build Pipeline"] -->|Executes script| B["scripts/generate_sitemap.py"]
    B -->|Scans MDX tree| C["docs/phoenix/**/*.mdx"]
    C -->|Extracts lastmod & routes| D["docs/phoenix/sitemap.xml"]
    D -->|Published to| E["arize.com/docs/phoenix/sitemap.xml"]
    
    sub5["Code Entity Space"]
    style sub5 fill:none,stroke:none
    B -.->|Code reference| F["scripts/generate_sitemap.py"]
    D -.->|Target artifact| G["docs/phoenix/sitemap.xml"]
```
*Diagram 3: Documentation Sitemap Generation Pipeline*

Sources: [docs/phoenix/sitemap.xml:1-172](), [scripts/generate_sitemap.py]()

---

## 4. Contributing Documentation

Contributors looking to add or modify documentation must adhere to the following workflow:

1. **File Placement**: Create or edit `.mdx` files within the appropriate subdirectory under `docs/phoenix/`.
2. **Navigation Updates**: Register new pages in [docs.json]() under the corresponding navigation group to ensure they appear in the Mintlify sidebar.
3. **Frontmatter Standards**: Include valid Mintlify frontmatter at the top of every MDX file, specifying `title` and `description`:
   ```yaml
   ---
   title: "Page Title"
   description: "Concise summary of the guide or reference."
   ---
   ```
4. **Link Integrity & Snippets**: Use relative pathing for internal Markdown links. When referencing repository code snippets, utilize the comment-tag snippet inclusion syntax [docs/phoenix/get-started/get-started-tracing.mdx:20]() rather than hardcoding code blocks.
5. **Verification**: Run local validation and preview builds via Mintlify CLI before submitting pull requests.

Sources: [docs.json:51-174](), [docs/phoenix/get-started/get-started-tracing.mdx:16-29]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [cspell.json](cspell.json)
- [internal_docs/specs/online-evals.md](internal_docs/specs/online-evals.md)
- [internal_docs/specs/playground.md](internal_docs/specs/playground.md)
- [internal_docs/specs/prompts.md](internal_docs/specs/prompts.md)
- [internal_docs/specs/server_evaluators.md](internal_docs/specs/server_evaluators.md)
- [kustomize/README.md](kustomize/README.md)
- [packages/phoenix-client/CHANGELOG.md](packages/phoenix-client/CHANGELOG.md)
- [packages/phoenix-client/pyproject.toml](packages/phoenix-client/pyproject.toml)
- [packages/phoenix-evals/CHANGELOG.md](packages/phoenix-evals/CHANGELOG.md)
- [packages/phoenix-evals/pyproject.toml](packages/phoenix-evals/pyproject.toml)
- [pyproject.toml](pyproject.toml)
- [requirements/ci.txt](requirements/ci.txt)
- [requirements/packages/phoenix-evals.txt](requirements/packages/phoenix-evals.txt)
- [requirements/type-check.txt](requirements/type-check.txt)
- [requirements/unit-tests.txt](requirements/unit-tests.txt)
- [scripts/data/generate_traces.py](scripts/data/generate_traces.py)
- [src/phoenix/__init__.py](src/phoenix/__init__.py)
- [src/phoenix/config.py](src/phoenix/config.py)
- [src/phoenix/db/alembic.ini](src/phoenix/db/alembic.ini)
- [src/phoenix/db/engines.py](src/phoenix/db/engines.py)
- [src/phoenix/db/migrate.py](src/phoenix/db/migrate.py)
- [src/phoenix/db/migrations/__init__.py](src/phoenix/db/migrations/__init__.py)
- [src/phoenix/db/migrations/env.py](src/phoenix/db/migrations/env.py)
- [src/phoenix/db/migrations/versions/10460e46d750_datasets.py](src/phoenix/db/migrations/versions/10460e46d750_datasets.py)
- [src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py](src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py)
- [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py](src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py)
- [src/phoenix/db/models.py](src/phoenix/db/models.py)
- [src/phoenix/server/api/context.py](src/phoenix/server/api/context.py)
- [src/phoenix/server/api/dataloaders/__init__.py](src/phoenix/server/api/dataloaders/__init__.py)
- [src/phoenix/server/api/dataloaders/trace_root_spans.py](src/phoenix/server/api/dataloaders/trace_root_spans.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/routers/v1/experiment_evaluations.py](src/phoenix/server/api/routers/v1/experiment_evaluations.py)
- [src/phoenix/server/api/routers/v1/experiment_runs.py](src/phoenix/server/api/routers/v1/experiment_runs.py)
- [src/phoenix/server/api/routers/v1/experiments.py](src/phoenix/server/api/routers/v1/experiments.py)
- [src/phoenix/server/api/types/Experiment.py](src/phoenix/server/api/types/Experiment.py)
- [src/phoenix/server/api/types/MimeType.py](src/phoenix/server/api/types/MimeType.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/ProjectSession.py](src/phoenix/server/api/types/ProjectSession.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/settings.py](src/phoenix/settings.py)
- [src/phoenix/trace/fixtures.py](src/phoenix/trace/fixtures.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [src/phoenix/trace/utils.py](src/phoenix/trace/utils.py)
- [src/phoenix/version.py](src/phoenix/version.py)
- [tests/unit/_helpers.py](tests/unit/_helpers.py)
- [tests/unit/db/test_engines.py](tests/unit/db/test_engines.py)
- [tests/unit/server/api/routers/v1/test_experiments.py](tests/unit/server/api/routers/v1/test_experiments.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/types/test_Experiment.py](tests/unit/server/api/types/test_Experiment.py)
- [tests/unit/server/api/types/test_Project.py](tests/unit/server/api/types/test_Project.py)
- [tests/unit/server/api/types/test_ProjectSession.py](tests/unit/server/api/types/test_ProjectSession.py)
- [tests/unit/server/api/types/test_Span.py](tests/unit/server/api/types/test_Span.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)
- [tox.ini](tox.ini)
- [uv.lock](uv.lock)

</details>



## Purpose and Scope

This page provides definitions for codebase-specific terms, jargon, abbreviations, and domain concepts used within the Phoenix project. It clarifies terminology for onboarding engineers and links directly to relevant modules, classes, and functions for deeper technical investigation.

---

## Phoenix Core Concepts

### Phoenix
Phoenix is an open-source AI observability platform designed for experimentation, evaluation, and troubleshooting of large language model (LLM) applications. It provides trace collection via OpenTelemetry, dataset versioning, evaluation frameworks, prompt management, and a vendor-agnostic playground interface supporting multiple LLM providers.

- Core Python package: `arize-phoenix`
- Main server entrypoint module: `phoenix.server.main`
- Implements features: tracing, evaluation, datasets, experiments, prompts, authentication, cost tracking
- Version tracked in: `src/phoenix/version.py`

**Key Code:**  
- Main server entrypoint: [src/phoenix/server/main.py:1-29]()  
- Version string: [src/phoenix/version.py:1-1]()  
- Package metadata: [.release-please-manifest.json:1]()

Sources:  
- [src/phoenix/server/main.py:1-29]()  
- [src/phoenix/version.py:1-1]()  
- [.release-please-manifest.json:1]()

---

### Span  
A *Span* represents a discrete operation or event within a trace, usually recording an interaction with an LLM or a related tool (e.g., tool invocation, retrieval, reranker).

- Built on OpenTelemetry spans enhanced with AI-specific semantic conventions (e.g., language model details, input/output payloads)
- Contains fields like timestamps, span kind (LLM, TOOL, CHAIN, RETRIEVER, etc.), input and output content, model metadata, and annotations
- Span kinds include `LLM`, `CHAIN`, `TOOL`, `RETRIEVER`, `EMBEDDING`, `RERANKER`, and `AGENT`

**Key Code:**  
- SQLAlchemy Span ORM model: [src/phoenix/db/models.py:440-540]()  
- GraphQL Span type schema: [src/phoenix/server/api/types/Span.py:57-232]()  

Sources:  
- [src/phoenix/db/models.py:440-540]()  
- [src/phoenix/server/api/types/Span.py:57-232]()  

---

### Trace  
A *Trace* is a collection of related spans that represent an entire workflow, request, or session lifecycle within an LLM application, enabling end-to-end analysis and debugging.

- Traces provide visibility into the whole request including nested tool, chain, and LLM calls
- Incoming trace data is ingested over OTLP (OpenTelemetry Protocol) via gRPC and HTTP, decoded, validated, and stored in the database

**Key Code:**  
- Trace GraphQL type: [src/phoenix/server/api/types/Trace.py:30-95]()  
- Trace DataLoader usage: [src/phoenix/server/api/dataloaders/__init__.py:1-50]()  

Sources:  
- [src/phoenix/server/api/types/Trace.py:30-95]()  
- [src/phoenix/server/api/dataloaders/__init__.py:1-50]()  

---

### Project  
A *Project* is a top-level namespace in Phoenix grouping related traces, datasets, experiments, annotations, and sessions. It serves organizational and access control boundaries.

- Holds configuration such as trace retention policies
- Supports multi-user collaboration with role-based access control

**Key Code:**  
- Default project constant `DEFAULT_PROJECT_NAME`: [src/phoenix/config.py:60-60]()  
- Project GraphQL type and definitions: [src/phoenix/server/api/types/Project.py:61-195]()  

Sources:  
- [src/phoenix/config.py:60-60]()  
- [src/phoenix/server/api/types/Project.py:61-195]()  

---

### Dataset  
A *Dataset* is a versioned collection of example inputs and expected outputs used for evaluation, experimentation, and fine-tuning.

- Supports example revisions, splitting, and metadata
- Links between spans and dataset examples enable annotation and metric reporting

**Key Code:**  
- Dataset SQLAlchemy models `Dataset`, `DatasetExample`: [src/phoenix/db/models.py:1020-1100]()  
- Dataset GraphQL types: [src/phoenix/server/api/types/Dataset.py:15-80]()  

Sources:  
- [src/phoenix/db/models.py:1020-1100]()  
- [src/phoenix/server/api/types/Dataset.py:15-80]()  

---

### Experiment  
An *Experiment* encapsulates evaluation runs comparing models, prompts, or data splits.

- Aggregates metrics time series, latency, error rates
- Tracks statuses such as `RUNNING`, `COMPLETED`, `STOPPED`, `ERROR`

**Key Code:**  
- Experiment GraphQL type: [src/phoenix/server/api/types/Experiment.py:20-70]()  
- Experiment status enum values: [src/phoenix/db/models.py:179-195]()  

Sources:  
- [src/phoenix/server/api/types/Experiment.py:20-70]()  
- [src/phoenix/db/models.py:179-195]()  

---

### Evaluator  
*Evaluators* define automated or manual benchmarking of model outputs using dataset examples.

- Include LLM evaluators, code evaluators, and built-in classification evaluators
- Support input mapping to align dataset schema to model inputs

**Key Code:**  
- Evaluator ORM definitions: [src/phoenix/db/models.py:178-180]()  
- Python evaluation framework package: [packages/phoenix-evals/pyproject.toml:1-40]()  

Sources:  
- [src/phoenix/db/models.py:178-180]()  
- [packages/phoenix-evals/pyproject.toml:1-40]()  

---

### Annotation  
*Annotations* are labels, scores, or qualitative feedback provided on spans, traces, or dataset examples to enrich analysis.

- Support annotator kinds: `LLM`, `HUMAN`, `CODE`
- Annotation types: `CATEGORICAL`, `CONTINUOUS`, and `FREEFORM`
- Metadata includes explanation text, source identifiers, timestamps, and user info

**Key Code:**  
- Annotation configuration types: [src/phoenix/db/types/annotation_configs.py:1-70]()  

Sources:  
- [src/phoenix/db/types/annotation_configs.py:1-70]()  

---

### Session  
A *Session* groups related interactions, particularly multi-turn conversations or AI assistant dialogs.

- Captures conversational context with linked traces and turns
- PxI (Phoenix Intelligence) agent interactions are session-bound for behavioral continuity

**Key Code:**  
- Session class management: [src/phoenix/session/session.py:7-143]()  

Sources:  
- [src/phoenix/session/session.py:7-143]()  

---

## Monorepo Structure  

Phoenix is developed as a monorepo combining Python and TypeScript packages for integrated development and releases.

### Python Packages

| Package Name          | Description                              | Location                  |
|-----------------------|------------------------------------------|---------------------------|
| `arize-phoenix`       | Core server, API, models, ingestion       | `src/phoenix/`            |
| `arize-phoenix-evals` | LLM evaluation framework                   | `packages/phoenix-evals/` |
| `arize-phoenix-otel`  | OpenTelemetry integration helpers          | `packages/phoenix-otel/`  |
| `arize-phoenix-client`| REST/GraphQL client library                  | `packages/phoenix-client/`|

### TypeScript Packages

| Package Name           | Description                            | Location                     |
|------------------------|--------------------------------------|------------------------------|
| `@arizeai/phoenix-client`| Frontend client API typings & hooks   | `js/packages/phoenix-client/`|
| `@arizeai/phoenix-mcp`   | Model Context Protocol server and client | `js/packages/phoenix-mcp/`  |
| `@arizeai/phoenix-cli`   | CLI tools for managing project entities | `js/packages/phoenix-cli/`  |

Versioning is centrally managed with `.release-please-manifest.json` tracking package version numbers.

Title: "Phoenix Monorepo Package Dependencies"
```mermaid
graph TD
    ROOT["Phoenix Monorepo Root"]
    CORE["src/phoenix/ (Core Server & API)"]
    EVALS["packages/phoenix-evals/ (LLM Evaluations)"]
    OTEL["packages/phoenix-otel/ (OpenTelemetry Helpers)"]
    CLIENT_PY["packages/phoenix-client/ (Python Client)"]

    ROOT --> CORE
    ROOT --> EVALS
    ROOT --> OTEL
    ROOT --> CLIENT_PY
```

Sources:  
- [packages/phoenix-client/pyproject.toml:1-33]()  
- [.release-please-manifest.json:1]()  
- [src/phoenix/version.py:1-1]()  
- [src/phoenix/server/main.py:1-29]()  

---

## Server Architecture Highlights

### FastAPI Application  
Phoenix server is a FastAPI ASGI app providing REST, GraphQL, and WebSocket endpoints.

- Uses middleware for CORS, authentication (bearer token, OAuth2), CSRF, gzip compression, and tracing
- Startup lifecycle supports asynchronous daemons, task sweeps, and database session pools
- API routers organized by version and authentication domain

**Key Code:**  
- FastAPI app setup: [src/phoenix/server/app.py:33-60]()  
- Authentication backend: `BearerTokenAuthBackend` [src/phoenix/server/app.py:122-122]()  

Sources:  
- [src/phoenix/server/app.py:33-122]()  

---

### GraphQL API  
Phoenix provides a comprehensive GraphQL API using Strawberry GraphQL.

- Uses DataLoader batching pattern for efficient DB access
- Builds types including Project, Dataset, Experiment, Span, Annotation, Agent
- Supports queries, mutations, subscriptions

**Key Code:**  
- Schema builder function: [src/phoenix/server/api/schema.py:1-100]()  
- GraphQLRouter instance: [src/phoenix/server/app.py:55-56]()  

Sources:  
- [src/phoenix/server/api/schema.py:1-100]()  
- [src/phoenix/server/app.py:55-56]()  

---

### OTLP Ingestion  
Phoenix ingests OpenTelemetry Protocol (OTLP) formatted trace spans over HTTP and gRPC.

- OTLP requests decoded and validated, spans inserted in batches via `BulkInserter`
- `SpanCostCalculator` daemon computes cost estimates for spans based on token usage and model pricing
- Supports synchronous and streaming ingestion paths

**Key Code:**  
- BulkInserter implementation: [src/phoenix/db/bulk_inserter.py:1-100]()  
- SpanCostCalculator daemon: [src/phoenix/server/cost_tracking/span_cost_calculator.py:1-42]()  

Sources:  
- [src/phoenix/db/bulk_inserter.py:1-100]()  
- [src/phoenix/server/cost_tracking/span_cost_calculator.py:1-42]()  

---

### Database Layer  
Phoenix uses SQLAlchemy async ORM supporting PostgreSQL and SQLite backend.

- Models defined with declarative base in `src/phoenix/db/models.py`
- Migrations managed with Alembic
- Allows efficient queries with complex filters, joins, and batch inserts

**Key Code:**  
- SQLAlchemy declarative base and models: [src/phoenix/db/models.py:40-53]()  
- Async Engine configuration: [src/phoenix/db/engines.py:1-50]()  

Sources:  
- [src/phoenix/db/models.py:40-53]()  
- [src/phoenix/db/engines.py:1-50]()  

---

## Important Data Flows and Relationships

Title: "OTLP Ingestion and Cost Tracking Pipeline"
```mermaid
graph TD
    OTLP_HTTP["OTLP HTTP Endpoint"]
    OTLP_GRPC["OTLP gRPC Endpoint"]
    BULK_INSERTER["BulkInserter"]
    SPAN_COST_CALC["SpanCostCalculator"]
    MODELS["models.py (SQLAlchemy Models)"]
    DATABASE["Database Layer"]

    OTLP_HTTP --> BULK_INSERTER
    OTLP_GRPC --> BULK_INSERTER
    BULK_INSERTER --> MODELS
    MODELS --> DATABASE
    MODELS --> SPAN_COST_CALC
    SPAN_COST_CALC --> DATABASE
```

Sources:  
- [src/phoenix/server/app.py:81-90]()  
- [src/phoenix/db/bulk_inserter.py:1-100]()  
- [src/phoenix/server/cost_tracking/span_cost_calculator.py:1-42]()  
- [src/phoenix/db/models.py:40-53]()  

---

Title: "GraphQL Query Execution Flow"
```mermaid
graph TD
    USER["User GraphQL Query"]
    ROUTER["app.py (GraphQLRouter)"]
    SCHEMA["schema.py (build_graphql_schema)"]
    DATALOADER["dataloaders/__init__.py"]
    ORM_MODEL["models.py (SQLAlchemy Models)"]

    USER --> ROUTER
    ROUTER --> SCHEMA
    SCHEMA --> DATALOADER
    DATALOADER --> ORM_MODEL
```

Sources:  
- [src/phoenix/server/app.py:55-60]()  
- [src/phoenix/server/api/schema.py:1-100]()  
- [src/phoenix/server/api/dataloaders/__init__.py:1-50]()  
- [src/phoenix/db/models.py:40-53]()  

---

## Bridging Natural Language Terms to Core Code Entities

Title: "Mapping System Concepts to Code Entities"
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        PHX["PhoenixPlatform"]
        SPN["SpanEvent"]
        TRC["TraceWorkflow"]
        DST["DatasetCollection"]
        SES["UserSession"]
    end

    subgraph "CodeEntitySpace"
        SERVER["app.py (FastAPIApp)"]
        MODELS["models.py (DeclarativeBase)"]
        API_TYPES["Span.py (StrawberryType)"]
        DATALOADERS["dataloaders/__init__.py"]
        SESSION_PY["session.py (SessionManager)"]
    end

    PHX --> SERVER
    SPN --> MODELS
    SPN --> API_TYPES
    TRC --> MODELS
    TRC --> DATALOADERS
    DST --> MODELS
    SES --> SESSION_PY
```

Sources:  
- [src/phoenix/server/app.py:33-60]()  
- [src/phoenix/db/models.py:40-53]()  
- [src/phoenix/server/api/types/Span.py:57-232]()  
- [src/phoenix/server/api/dataloaders/__init__.py:1-50]()  
- [src/phoenix/session/session.py:7-143]()