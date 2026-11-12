# Page: Phoenix Overview

# Phoenix Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [app/schema.graphql](app/schema.graphql)
- [app/src/components/trace/SpanKindIcon.tsx](app/src/components/trace/SpanKindIcon.tsx)
- [app/src/pages/auth/AuthLayout.tsx](app/src/pages/auth/AuthLayout.tsx)
- [app/src/window.d.ts](app/src/window.d.ts)
- [cspell.json](cspell.json)
- [docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx](docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx)
- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx](docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx)
- [docs/phoenix/sdk-api-reference/typescript/overview.mdx](docs/phoenix/sdk-api-reference/typescript/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx)
- [internal_docs/specs/playground.md](internal_docs/specs/playground.md)
- [internal_docs/specs/prompts.md](internal_docs/specs/prompts.md)
- [internal_docs/specs/server_evaluators.md](internal_docs/specs/server_evaluators.md)
- [js/packages/phoenix-client/README.md](js/packages/phoenix-client/README.md)
- [js/packages/phoenix-config/README.md](js/packages/phoenix-config/README.md)
- [js/packages/phoenix-evals/README.md](js/packages/phoenix-evals/README.md)
- [js/packages/phoenix-mcp/README.md](js/packages/phoenix-mcp/README.md)
- [js/packages/phoenix-mcp/src/index.ts](js/packages/phoenix-mcp/src/index.ts)
- [js/packages/phoenix-mcp/src/projectTools.ts](js/packages/phoenix-mcp/src/projectTools.ts)
- [js/packages/phoenix-otel/README.md](js/packages/phoenix-otel/README.md)
- [kustomize/README.md](kustomize/README.md)
- [packages/phoenix-client/CHANGELOG.md](packages/phoenix-client/CHANGELOG.md)
- [packages/phoenix-client/README.md](packages/phoenix-client/README.md)
- [packages/phoenix-client/pyproject.toml](packages/phoenix-client/pyproject.toml)
- [packages/phoenix-evals/CHANGELOG.md](packages/phoenix-evals/CHANGELOG.md)
- [packages/phoenix-evals/README.md](packages/phoenix-evals/README.md)
- [packages/phoenix-evals/docs/source/api/evals.rst](packages/phoenix-evals/docs/source/api/evals.rst)
- [packages/phoenix-evals/docs/source/index.md](packages/phoenix-evals/docs/source/index.md)
- [packages/phoenix-evals/pyproject.toml](packages/phoenix-evals/pyproject.toml)
- [packages/phoenix-otel/CHANGELOG.md](packages/phoenix-otel/CHANGELOG.md)
- [packages/phoenix-otel/README.md](packages/phoenix-otel/README.md)
- [packages/phoenix-otel/pyproject.toml](packages/phoenix-otel/pyproject.toml)
- [packages/phoenix-otel/src/phoenix/otel/__init__.py](packages/phoenix-otel/src/phoenix/otel/__init__.py)
- [packages/phoenix-otel/src/phoenix/otel/otel.py](packages/phoenix-otel/src/phoenix/otel/otel.py)
- [packages/phoenix-otel/tests/__init__.py](packages/phoenix-otel/tests/__init__.py)
- [packages/phoenix-otel/tests/test_exports.py](packages/phoenix-otel/tests/test_exports.py)
- [packages/phoenix-otel/tests/test_otel.py](packages/phoenix-otel/tests/test_otel.py)
- [packages/phoenix-otel/tests/test_settings.py](packages/phoenix-otel/tests/test_settings.py)
- [pyproject.toml](pyproject.toml)
- [release-please-config.json](release-please-config.json)
- [requirements/packages/phoenix-evals.txt](requirements/packages/phoenix-evals.txt)
- [requirements/type-check.txt](requirements/type-check.txt)
- [requirements/unit-tests.txt](requirements/unit-tests.txt)
- [scripts/data/generate_traces.py](scripts/data/generate_traces.py)
- [scripts/docker/devops/oidc-server/frontend/package.json](scripts/docker/devops/oidc-server/frontend/package.json)
- [scripts/docker/devops/oidc-server/frontend/src/contexts/ThemeContext.tsx](scripts/docker/devops/oidc-server/frontend/src/contexts/ThemeContext.tsx)
- [scripts/docker/devops/oidc-server/package.json](scripts/docker/devops/oidc-server/package.json)
- [scripts/docker/devops/smtp-server/package.json](scripts/docker/devops/smtp-server/package.json)
- [src/phoenix/__init__.py](src/phoenix/__init__.py)
- [src/phoenix/config.py](src/phoenix/config.py)
- [src/phoenix/server/api/context.py](src/phoenix/server/api/context.py)
- [src/phoenix/server/api/dataloaders/__init__.py](src/phoenix/server/api/dataloaders/__init__.py)
- [src/phoenix/server/api/input_types/SpanSort.py](src/phoenix/server/api/input_types/SpanSort.py)
- [src/phoenix/server/api/mutations/__init__.py](src/phoenix/server/api/mutations/__init__.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/schema.py](src/phoenix/server/api/schema.py)
- [src/phoenix/server/api/types/Dataset.py](src/phoenix/server/api/types/Dataset.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/tests/test_config.py](src/phoenix/tests/test_config.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [src/phoenix/version.py](src/phoenix/version.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/unit/conftest.py](tests/unit/conftest.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)
- [uv.lock](uv.lock)

</details>





Phoenix is an open-source AI observability platform for tracing, evaluating, and experimenting with LLM applications. It consists of a FastAPI server that ingests OpenTelemetry traces, stores them in PostgreSQL or SQLite, and exposes them via GraphQL and REST APIs for analysis and visualization.

## What is Phoenix?

Phoenix is a monorepo containing a complete observability platform and supporting client libraries. The architecture separates into three main layers:

**Server Layer** (`src/phoenix/server/`)
- `main.py` - FastAPI application serving HTTP on port 6006 [[src/phoenix/server/main.py:78-79]()]
- `grpc_server.py` - gRPC server for OTLP trace ingestion on port 4317 [[src/phoenix/config.py:41-42]()]
- `api/schema.py` - Strawberry GraphQL API [[src/phoenix/server/api/schema.py:1-50]()]
- `api/routers/` - REST API v1 endpoints [[src/phoenix/server/api/routers/v1/__init__.py:1-50]()]
- `static/` - Bundled React SPA assets [[pyproject.toml:233-233]()]

**Data Layer** (`src/phoenix/db/`)
- `models.py` - SQLAlchemy ORM models for traces, spans, datasets, experiments [[src/phoenix/db/models.py:1-200]()]
- `engines.py` - Database engine configuration (SQLite/PostgreSQL) [[src/phoenix/db/engines.py:1-80]()]
- `migrations/` - Alembic migration scripts [[src/phoenix/db/migrations/versions/__init__.py:1-5]()]

**Client Layer** (`packages/`)
- `arize-phoenix-client` - REST API client for Python [[packages/phoenix-client/pyproject.toml:2-24]()]
- `arize-phoenix-evals` - LLM evaluation framework [[packages/phoenix-evals/pyproject.toml:2-24]()]
- `arize-phoenix-otel` - OpenTelemetry registration helpers [[.release-please-manifest.json:1-1]()]
- TypeScript equivalents at `js/packages/` [[README.md:37-38]()]

**Frontend** (`app/`)
- React SPA built with Vite, using Relay for GraphQL and Zustand for state.
- Served as static assets from `src/phoenix/server/static/` [[src/phoenix/server/main.py:105-115]()]

## Key Capabilities

Phoenix provides six primary capabilities:

1. [**Tracing**](https://arize.com/docs/phoenix/tracing/llm-traces): OpenTelemetry OTLP protocol ingestion via gRPC (port 4317) or HTTP (port 6006). Auto-instrumentation support for LlamaIndex, LangChain, and OpenAI [[src/phoenix/__init__.py:85-144]()].
2. [**Evaluation**](https://arize.com/docs/phoenix/evaluation/llm-evals): LLM-as-judge evaluators for quality assessment [[README.md:47-47]()].
3. [**Datasets**](https://arize.com/docs/phoenix/datasets-and-experiments/overview-datasets): Versioned collections of examples for experimentation [[README.md:48-48]()].
4. [**Experiments**](https://arize.com/docs/phoenix/datasets-and-experiments/overview-datasets#experiments): Track and evaluate changes to prompts and retrieval [[README.md:49-49]()].
5. [**Playground**](https://arize.com/docs/phoenix/prompt-engineering/overview-prompts): Optimize prompts and compare models [[README.md:50-50]()].
6. [**Prompt Management**](https://arize.com/docs/phoenix/prompt-engineering/overview-prompts/prompt-management): Version control and tagging for prompt templates [[README.md:51-51]()].
7. [**PXI Agent (Built-in AI Assistant)**](https://arize.com/docs/phoenix/pxi) - Permission-gated AI assistant for debugging traces, iterating on prompts, and navigating the platform [[src/phoenix/server/api/routers/__init__.py:160-200]()] [[src/phoenix/server/agents/capabilities.py:70-110]()].

Sources:
- [README.md:44-53]()
- [src/phoenix/__init__.py:1-149]()
- [pyproject.toml:1-74]()

## Package Structure

Phoenix is organized as a monorepo with independently versioned packages managed via `release-please` [[.release-please-manifest.json:1-1]()]. The main package `arize-phoenix` contains the complete server and UI.

### Phoenix Monorepo Structure

```mermaid
graph TB
    subgraph "Python Packages"
        ARIZE_PHOENIX["arize-phoenix<br/>v17.2.0<br/>src/phoenix/"]
        CLIENT_PKG["arize-phoenix-client<br/>v2.7.0<br/>packages/phoenix-client/"]
        EVALS_PKG["arize-phoenix-evals<br/>v3.1.0<br/>packages/phoenix-evals/"]
        OTEL_PKG["arize-phoenix-otel<br/>v0.16.1<br/>packages/phoenix-otel/"]
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
```

| Package            | Version | Location                   | Purpose                                           |
|--------------------|---------|----------------------------|--------------------------------------------------|
| `arize-phoenix`    | 17.2.0  | Root directory             | Full platform: server, APIs, React UI [[src/phoenix/version.py:1-1]()] |
| `arize-phoenix-client` | 2.7.0  | `packages/phoenix-client/` | Python client for REST/GraphQL API [[packages/phoenix-client/pyproject.toml:2-24]()] |
| `arize-phoenix-evals`  | 3.1.0  | `packages/phoenix-evals/`  | LLM evaluation framework [[packages/phoenix-evals/pyproject.toml:2-24]()] |
| `arize-phoenix-otel`   | 0.16.1 | `packages/phoenix-otel/`   | OpenTelemetry registration helpers [[.release-please-manifest.json:1-1]()] |

For details, see [Package Structure & Monorepo](#1.1).

Sources:
- [.release-please-manifest.json:1-1]()
- [src/phoenix/version.py:1-1]()
- [pyproject.toml:60-67]()

## High-Level Architecture

Phoenix follows a client-server architecture where instrumented applications send telemetry data to a central Phoenix server via OTLP.

### Mapping Natural Language to Key Code Entities

```mermaid
graph LR
    PythonApp["User Python LLM Application"]
    TypeScriptApp["User TypeScript LLM Application"]
    PhoenixOtel["phoenix.otel.register() (packages/phoenix-otel)"]
    TSRegister["@arizeai/phoenix-otel register (js/packages/phoenix-otel)"]

    GRPCServer["grpc_server.py (src/phoenix/server/)"]
    HTTPServer["main.py - FastAPI (src/phoenix/server/)"]
    BulkInserter["BulkInserter (src/phoenix/db/insertion/bulk_inserter.py)"]
    DBModels["SQLAlchemy Models (src/phoenix/db/models.py)"]
    ReactFrontend["React SPA UI (app/)"]

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

The server runs two ingestion endpoints:

1. **gRPC Server**: OTLP protocol tracing ingestion on port 4317 `src/phoenix/server/grpc_server.py`.
2. **FastAPI HTTP Server**: Handles HTTP API, REST, GraphQL, and OTLP HTTP ingestion on port 6006 `src/phoenix/server/main.py`.

Data is processed and bulk inserted asynchronously into the database, which can be SQLite or PostgreSQL implemented via SQLAlchemy ORM models. The React frontend SPA is bundled and served from the server-side static routes.

Sources:
- [src/phoenix/server/main.py:30-180]()
- [src/phoenix/config.py:40-75]()
- [src/phoenix/db/insertion/bulk_inserter.py:1-80]()
- [src/phoenix/db/models.py:1-200]()

## Data Ingestion Flow

Phoenix receives trace data via the OpenTelemetry Protocol (OTLP) and processes it through a multi-stage pipeline to store, analyze, and visualize LLM call traces.

```mermaid
sequenceDiagram
    participant UserApp as "Instrumented Application"
    participant OTelSDK as "OpenTelemetry SDK"
    participant PhoenixCollector as "Phoenix OTLP Server (gRPC/HTTP)"
    participant BulkInserter as "BulkInserter (Async)"
    participant Database as "PostgreSQL/SQLite (SQLAlchemy ORM)"

    UserApp->>OTelSDK: Perform LLM Request (Trace Span Generated)
    OTelSDK->>PhoenixCollector: Export OTLP Span (gRPC 4317 or HTTP 6006)
    PhoenixCollector->>BulkInserter: enqueue_span()
    BulkInserter->>Database: Bulk Insert Spans and Trace Data
```

The system leverages the `opentelemetry-sdk` and `opentelemetry-proto` libraries for trace data representation and export [[pyproject.toml:45-47]()].

Sources:
- [pyproject.toml:45-47]()
- [src/phoenix/__init__.py:85-144]()

## Quick Start

### Installation

```bash
pip install arize-phoenix
```

### Launch Server

From Python or Jupyter:

```python
import phoenix as px
session = px.launch_app()  # Starts server on http://localhost:6006
```
[[src/phoenix/__init__.py:19-20]()]

### Instrument Your Application

Example of instrumenting OpenAI SDK with Phoenix OpenTelemetry helpers:

```python
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

# Register tracer provider and auto-instrument OpenAI calls
tracer_provider = register()
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```
[[src/phoenix/__init__.py:94-97]()]

For details on core entities and terminology, see [Core Concepts & Terminology](#1.2).

Sources:
- [src/phoenix/__init__.py:13-44]()
- [pyproject.toml:78-79]()

---

# Page: Package Structure & Monorepo

# Package Structure & Monorepo

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [app/.env.example](app/.env.example)
- [app/package.json](app/package.json)
- [app/pnpm-lock.yaml](app/pnpm-lock.yaml)
- [app/src/components/table/Table.tsx](app/src/components/table/Table.tsx)
- [app/src/openInference/tracing/__tests__/types.test.ts](app/src/openInference/tracing/__tests__/types.test.ts)
- [app/src/openInference/tracing/types.ts](app/src/openInference/tracing/types.ts)
- [app/src/pages/trace/TracePage.tsx](app/src/pages/trace/TracePage.tsx)
- [app/src/typeUtils.ts](app/src/typeUtils.ts)
- [app/vite.config.mts](app/vite.config.mts)
- [app/vitest.setup.ts](app/vitest.setup.ts)
- [internal_docs/specs/playground.md](internal_docs/specs/playground.md)
- [internal_docs/specs/prompts.md](internal_docs/specs/prompts.md)
- [internal_docs/specs/server_evaluators.md](internal_docs/specs/server_evaluators.md)
- [js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md](js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md)
- [js/examples/apps/demo-document-relevancy-experiment/package.json](js/examples/apps/demo-document-relevancy-experiment/package.json)
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
- [kustomize/README.md](kustomize/README.md)
- [packages/phoenix-client/CHANGELOG.md](packages/phoenix-client/CHANGELOG.md)
- [packages/phoenix-client/pyproject.toml](packages/phoenix-client/pyproject.toml)
- [packages/phoenix-evals/CHANGELOG.md](packages/phoenix-evals/CHANGELOG.md)
- [packages/phoenix-evals/docs/source/api/evals.rst](packages/phoenix-evals/docs/source/api/evals.rst)
- [packages/phoenix-evals/docs/source/index.md](packages/phoenix-evals/docs/source/index.md)
- [packages/phoenix-evals/pyproject.toml](packages/phoenix-evals/pyproject.toml)
- [packages/phoenix-otel/CHANGELOG.md](packages/phoenix-otel/CHANGELOG.md)
- [packages/phoenix-otel/pyproject.toml](packages/phoenix-otel/pyproject.toml)
- [packages/phoenix-otel/src/phoenix/otel/__init__.py](packages/phoenix-otel/src/phoenix/otel/__init__.py)
- [packages/phoenix-otel/src/phoenix/otel/otel.py](packages/phoenix-otel/src/phoenix/otel/otel.py)
- [packages/phoenix-otel/tests/__init__.py](packages/phoenix-otel/tests/__init__.py)
- [packages/phoenix-otel/tests/test_exports.py](packages/phoenix-otel/tests/test_exports.py)
- [packages/phoenix-otel/tests/test_otel.py](packages/phoenix-otel/tests/test_otel.py)
- [packages/phoenix-otel/tests/test_settings.py](packages/phoenix-otel/tests/test_settings.py)
- [pyproject.toml](pyproject.toml)
- [release-please-config.json](release-please-config.json)
- [requirements/packages/phoenix-evals.txt](requirements/packages/phoenix-evals.txt)
- [requirements/type-check.txt](requirements/type-check.txt)
- [requirements/unit-tests.txt](requirements/unit-tests.txt)
- [scripts/docker/devops/oidc-server/frontend/package.json](scripts/docker/devops/oidc-server/frontend/package.json)
- [scripts/docker/devops/oidc-server/frontend/src/contexts/ThemeContext.tsx](scripts/docker/devops/oidc-server/frontend/src/contexts/ThemeContext.tsx)
- [scripts/docker/devops/oidc-server/package.json](scripts/docker/devops/oidc-server/package.json)
- [scripts/docker/devops/smtp-server/package.json](scripts/docker/devops/smtp-server/package.json)
- [src/phoenix/__init__.py](src/phoenix/__init__.py)
- [src/phoenix/tests/test_config.py](src/phoenix/tests/test_config.py)
- [src/phoenix/trace/fixtures.py](src/phoenix/trace/fixtures.py)
- [src/phoenix/trace/utils.py](src/phoenix/trace/utils.py)
- [src/phoenix/version.py](src/phoenix/version.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/unit/conftest.py](tests/unit/conftest.py)
- [uv.lock](uv.lock)

</details>



This document describes the monorepo organization of the Phoenix codebase, covering the Python and TypeScript packages, their versioning, workspace management, and interrelations. It explains how Phoenix’s various components are modularized, developed, and released within a unified repository.

For deployment considerations, see [Kubernetes Deployment](#6.5). For API usage by developers, see [Python Client (arize-phoenix-client)](#3.1) and [TypeScript Client](#3.4).

---

## Monorepo Overview

Phoenix uses a **dual-language monorepo** strategy:

- **Python packages** managed with **uv** workspaces
- **TypeScript packages** managed with **pnpm** workspaces

Each package is versioned and released independently but shares tooling, version control, and CI/CD pipelines.

### Mapping System Components to Monorepo Packages

The diagram below maps Phoenix’s system components and their code entities within the monorepo folder structure and versioning:

```mermaid
graph TB
    subgraph "Repository Root [/]"
        
        subgraph "Python Monorepo [uv workspace]"
            MainPkg["arize-phoenix [src/phoenix/]<br/>Server & Bundled UI<br/>v17.2.0"]
            Client["arize-phoenix-client [packages/phoenix-client/]<br/>Python API Client<br/>v2.7.0"]
            Evals["arize-phoenix-evals [packages/phoenix-evals/]<br/>Evaluation Framework<br/>v3.1.0"]
            Otel["arize-phoenix-otel [packages/phoenix-otel/]<br/>OTLP Helpers<br/>v0.16.1"]
        end
        
        subgraph "TypeScript Monorepo [pnpm workspace]"
            TSClient["@arizeai/phoenix-client [js/packages/phoenix-client/]<br/>TS API Client<br/>v6.10.0"]
            TSEvals["@arizeai/phoenix-evals [js/packages/phoenix-evals/]<br/>TS Evals"]
            TSOtel["@arizeai/phoenix-otel [js/packages/phoenix-otel/]<br/>TS OTLP"]
            TSMCP["@arizeai/phoenix-mcp [js/packages/phoenix-mcp/]<br/>MCP Server<br/>v4.0.13"]
            TSCLI["@arizeai/phoenix-cli [js/packages/phoenix-cli/]<br/>CLI Tool"]
        end
        
        subgraph "Frontend Application"
            AppDir["phoenix-ui [app/]<br/>React + Vite + Relay"]
        end
        
        subgraph "Shared Resources"
            Schemas["schemas/openapi.json<br/>API Specification"]
            Kustomize["kustomize/"]
        end
    end
    
    MainPkg -.-> Client
    AppDir -- "Bundled into" --> MainPkg
    TSClient -- "Generated from" --> Schemas
    Client -- "Generated from" --> Schemas
```

**Sources:** [.release-please-manifest.json:1](), [src/phoenix/version.py:1](), [packages/phoenix-client/pyproject.toml:24](), [packages/phoenix-evals/pyproject.toml:24](), [js/packages/phoenix-client/package.json:3](), [js/packages/phoenix-mcp/package.json:3]()

---

## Python Package Structure

The Python ecosystem consists of four main packages, all sharing the `phoenix` namespace but released separately. They are managed via `uv` workspaces to allow simultaneous local development and testing.

### Main Package: `arize-phoenix`

This package contains the Phoenix server implementation, backend business logic, API layers, and the bundled React UI for the web frontend.

| Attribute          | Value                         |
|--------------------|-------------------------------|
| Package Name       | `arize-phoenix`               |
| Version           | v17.2.0                       |
| Location          | `src/phoenix/`                 |
| PyPI Package Name  | `arize-phoenix`               |
| Python Version Support | 3.10 - 3.14               |

**Key contents & responsibilities:**

- **Server Application:** The FastAPI app and GraphQL/REST API layer located primarily in `src/phoenix/server/`.
- **Static Assets / Frontend UI:** Compiled React build from `app/` is integrated in `src/phoenix/server/static/`.
- **Span & Trace Processing:** Contains ingestion logic and fixtures in `src/phoenix/trace/`.
- **Namespace Packaging:** Managed by `pkgutil.extend_path` for the `phoenix` namespace [src/phoenix/__init__.py:5]().
- **Legacy Import Handling:** Custom import hooks redirect legacy client & trace modules to updated packages [src/phoenix/__init__.py:47-66]().

**CLI Entry Points:**
- Scripts `arize-phoenix` and `phoenix` both launch the server main at `phoenix.server.main:main` [pyproject.toml:78-79]().

### Client Package: `arize-phoenix-client`

The official Python client package for interacting programmatically with Phoenix servers.

| Attribute          | Value                         |
|--------------------|-------------------------------|
| Package Name       | `arize-phoenix-client`        |
| Version            | v2.7.0                        |
| Location           | `packages/phoenix-client/`    |

**Features:**
- Provides resource APIs for spans, datasets, experiments, and prompts.
- Integrates OpenTelemetry SDK and OTLP export to support tracing [packages/phoenix-client/pyproject.toml:31-32]().
- Replacement for the legacy `phoenix.session.client.Client` with guidance enforced by import hooks [src/phoenix/__init__.py:47-66]().

### Evaluations Package: `arize-phoenix-evals`

Contains tools and frameworks to evaluate and benchmark large language models and AI behavior.

| Attribute          | Value                      |
|--------------------|----------------------------|
| Package Name       | `arize-phoenix-evals`      |
| Version            | v3.1.0                     |
| Location           | `packages/phoenix-evals/`  |

### OpenTelemetry Helpers Package: `arize-phoenix-otel`

Helper utilities for integrating OTLP and OpenTelemetry protocol with Phoenix.

| Attribute          | Value                      |
|--------------------|----------------------------|
| Package Name       | `arize-phoenix-otel`       |
| Version            | v0.16.1                    |
| Location           | `packages/phoenix-otel/`   |

---

## TypeScript Package Structure

The TypeScript ecosystem is managed under the `js/` directory using `pnpm` workspaces, enabling modular development and versioning.

### TypeScript Client Package: `@arizeai/phoenix-client`

| Attribute          | Value                         |
|--------------------|-------------------------------|
| Package Name       | `@arizeai/phoenix-client`     |
| Version            | v6.10.0                       |
| Location           | `js/packages/phoenix-client/` |

**Notes:**
- Types are generated from the OpenAPI spec `schemas/openapi.json` using `openapi-typescript`.
- Build outputs support both CommonJS (`dist/src/`) and ESM (`dist/esm/`) modules.

### MCP Server Package: `@arizeai/phoenix-mcp`

The Model Context Protocol server allows AI coding assistants to integrate and query Phoenix.

| Attribute          | Value                         |
|--------------------|-------------------------------|
| Package Name       | `@arizeai/phoenix-mcp`        |
| Version            | v4.0.13                       |
| Location           | `js/packages/phoenix-mcp/`    |

### Additional TS Packages:
- `@arizeai/phoenix-evals` – TypeScript port of the evals framework.
- `@arizeai/phoenix-otel` – OTLP/OTEL helpers in TypeScript.
- `@arizeai/phoenix-cli` – CLI tooling for Phoenix.

---

## Version Manifest & Release Automation

Phoenix leverages independent versioning for each package, tracked centrally by `.release-please-manifest.json`. For example:

| Package                      | Current Version |
|------------------------------|-----------------|
| arize-phoenix                | 17.2.0          |
| arize-phoenix-client         | 2.7.0           |
| arize-phoenix-evals          | 3.1.0           |
| arize-phoenix-otel           | 0.16.1          |

```json
{
  ".": "17.2.0",
  "packages/phoenix-evals": "3.1.0",
  "packages/phoenix-otel": "0.16.1",
  "packages/phoenix-client": "2.7.0"
}
```

**Release flow:**

```mermaid
graph LR
    subgraph "CI/CD Pipeline"
        Commit["Git Commit"] -- "Triggers" --> RP["Release Please"]
        RP -- "Updates" --> Manifest[".release-please-manifest.json"]
        RP -- "Updates" --> VersionPy["src/phoenix/version.py"]
        RP -- "Generates" --> Changelog["CHANGELOG.md"]
    end
    
    subgraph "Distribution"
        Manifest -- "Controls" --> PyPI["PyPI Publish"]
        Manifest -- "Controls" --> NPM["NPM Publish"]
    end
```

**Sources:** [.release-please-manifest.json:1](), [CHANGELOG.md:1-24](), [src/phoenix/version.py:1]()

---

## Workspace & Dependency Management

### Python Workspace (`uv`)

- The Python monorepo uses `uv` to manage package workspace linking and dependency resolution.
- Packages like `arize-phoenix-evals` and `arize-phoenix-client` can be developed alongside the main server package.
- Major dependencies include:
  - FastAPI (>=0.135.2) for the server web framework [pyproject.toml:62]().
  - Pydantic AI extensions for agent support [pyproject.toml:64]().
  - SQLAlchemy (asyncio) and Alembic for DB layer and migrations [pyproject.toml:51-52]().
  - OpenTelemetry SDK and exporters for tracing [pyproject.toml:45-47]().
- The `src/phoenix/__init__.py` sets up namespace package support via `pkgutil` and manages legacy import redirections [src/phoenix/__init__.py:4-44]().

### TypeScript Workspace (`pnpm`)

- The JavaScript/TypeScript workspace is managed by `pnpm` with workspaces declared in `js/package.json` and root workspace files.
- React-based frontend app (`app/`) and TS packages (`js/packages`) co-exist, with `pnpm` managing dependencies and inter-package linking.
- Versioned packages include client libs, CLI, evals, OTLP helpers, and MCP server [js/packages/phoenix-client/package.json:1-130](), [app/package.json:1-177]().

---

## Code Generation & API Specification

Phoenix uses an OpenAPI schema (`schemas/openapi.json`) as the single source of truth for API contracts.

```mermaid
graph TD
    Server["FastAPI Server [src/phoenix/server/]"] -- "Exports" --> Spec["OpenAPI Spec [schemas/openapi.json]"]
    
    Spec -- "openapi-python codegen" --> PyClient["arize-phoenix-client [Python]"]
    Spec -- "openapi-typescript codegen" --> TSClient["@arizeai/phoenix-client [TS]"]
    
    PyClient -- "Consumed by" --> Evals["arize-phoenix-evals (Python)"]
    TSClient -- "Consumed by UI & MCP" --> MCP["@arizeai/phoenix-mcp (TS)"]
```

This flow guarantees API consistency across languages and packages.

---

# Summary Table of Python Packages

| Package Name           | Directory                 | Version | Description                                             |
|-----------------------|---------------------------|---------|---------------------------------------------------------|
| arize-phoenix          | src/phoenix/              | 17.2.0  | Core Phoenix server + API + bundled UI                   |
| arize-phoenix-client   | packages/phoenix-client/  | 2.7.0   | Python client API for Phoenix                            |
| arize-phoenix-evals    | packages/phoenix-evals/   | 3.1.0   | Evaluation and model benchmarking framework             |
| arize-phoenix-otel     | packages/phoenix-otel/    | 0.16.1  | OpenTelemetry helpers for OTLP ingestion                |

---

# Summary Table of TypeScript Packages

| Package Name                 | Directory                        | Version | Description                          |
|-----------------------------|---------------------------------|---------|------------------------------------|
| @arizeai/phoenix-client      | js/packages/phoenix-client/     | 6.10.0  | TypeScript client API lib           |
| @arizeai/phoenix-evals       | js/packages/phoenix-evals/      | —       | TypeScript evals framework          |
| @arizeai/phoenix-otel        | js/packages/phoenix-otel/       | —       | OTLP/OTEL helpers in TypeScript     |
| @arizeai/phoenix-mcp         | js/packages/phoenix-mcp/        | 4.0.13  | MCP server for AI agent integration |
| @arizeai/phoenix-cli         | js/packages/phoenix-cli/        | —       | CLI tooling package                 |
| phoenix-ui                   | app/                           | 0.0.1   | React frontend app with Vite + Relay|

---

This detailed breakdown provides clear insights into how Phoenix’s monorepo is structured, how the distinct language ecosystems interoperate, and how versioning and release automation maintain consistency.

**Sources:**  
[.release-please-manifest.json:1](), [src/phoenix/version.py:1](), [src/phoenix/__init__.py:1-149](),  
[pyproject.toml:1-74](), [packages/phoenix-client/pyproject.toml:1-104](), [packages/phoenix-evals/pyproject.toml:1-130](),  
[js/packages/phoenix-client/package.json:1-130](), [app/package.json:1-177]()

---

# Page: Core Concepts & Terminology

# Core Concepts & Terminology

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [app/schema.graphql](app/schema.graphql)
- [app/src/components/trace/SpanKindIcon.tsx](app/src/components/trace/SpanKindIcon.tsx)
- [app/src/pages/auth/AuthLayout.tsx](app/src/pages/auth/AuthLayout.tsx)
- [app/src/window.d.ts](app/src/window.d.ts)
- [cspell.json](cspell.json)
- [docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx](docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx)
- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx](docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx)
- [docs/phoenix/sdk-api-reference/typescript/overview.mdx](docs/phoenix/sdk-api-reference/typescript/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx)
- [js/packages/phoenix-client/README.md](js/packages/phoenix-client/README.md)
- [js/packages/phoenix-config/README.md](js/packages/phoenix-config/README.md)
- [js/packages/phoenix-evals/README.md](js/packages/phoenix-evals/README.md)
- [js/packages/phoenix-mcp/README.md](js/packages/phoenix-mcp/README.md)
- [js/packages/phoenix-mcp/src/index.ts](js/packages/phoenix-mcp/src/index.ts)
- [js/packages/phoenix-mcp/src/projectTools.ts](js/packages/phoenix-mcp/src/projectTools.ts)
- [js/packages/phoenix-otel/README.md](js/packages/phoenix-otel/README.md)
- [packages/phoenix-client/README.md](packages/phoenix-client/README.md)
- [packages/phoenix-evals/README.md](packages/phoenix-evals/README.md)
- [packages/phoenix-otel/README.md](packages/phoenix-otel/README.md)
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
- [src/phoenix/server/api/input_types/SpanSort.py](src/phoenix/server/api/input_types/SpanSort.py)
- [src/phoenix/server/api/mutations/__init__.py](src/phoenix/server/api/mutations/__init__.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/routers/v1/experiment_evaluations.py](src/phoenix/server/api/routers/v1/experiment_evaluations.py)
- [src/phoenix/server/api/routers/v1/experiment_runs.py](src/phoenix/server/api/routers/v1/experiment_runs.py)
- [src/phoenix/server/api/routers/v1/experiments.py](src/phoenix/server/api/routers/v1/experiments.py)
- [src/phoenix/server/api/schema.py](src/phoenix/server/api/schema.py)
- [src/phoenix/server/api/types/Dataset.py](src/phoenix/server/api/types/Dataset.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/settings.py](src/phoenix/settings.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [tests/unit/server/api/routers/v1/test_experiments.py](tests/unit/server/api/routers/v1/test_experiments.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)

</details>



This page defines the core data entities and domain concepts used throughout Phoenix. It covers the primary objects that developers interact with when tracing LLM applications, managing datasets, running experiments, and evaluating model outputs.

---

## Overview of Core Entities

Phoenix's architecture is built around several interconnected entities that enable observability, experimentation, and evaluation of LLM applications.

### Entity Relationship Diagram

```mermaid
graph TB
    Project["Project<br/>(models.Project)"]
    Trace["Trace<br/>(models.Trace)"]
    Span["Span<br/>(models.Span)"]
    Session["ProjectSession<br/>(models.ProjectSession)"]
    
    Dataset["Dataset<br/>(models.Dataset)"]
    DatasetVersion["DatasetVersion<br/>(models.DatasetVersion)"]
    DatasetExample["DatasetExample<br/>(models.DatasetExample)"]
    DatasetExampleRevision["DatasetExampleRevision<br/>(models.DatasetExampleRevision)"]
    
    Experiment["Experiment<br/>(models.Experiment)"]
    ExperimentRun["ExperimentRun<br/>(models.ExperimentRun)"]
    
    SpanAnnotation["SpanAnnotation<br/>(models.SpanAnnotation)"]
    ExperimentRunAnnotation["ExperimentRunAnnotation<br/>(models.ExperimentRunAnnotation)"]
    
    Evaluator["Evaluator<br/>(models.Evaluator)"]
    LLMEvaluator["LLMEvaluator<br/>(models.LLMEvaluator)"]
    CodeEvaluator["CodeEvaluator<br/>(models.CodeEvaluator)"]
    
    Prompt["Prompt<br/>(models.Prompt)"]
    PromptVersion["PromptVersion<br/>(models.PromptVersion)"]
    
    Project -->|"contains"| Trace
    Trace -->|"contains"| Span
    Span -->|"parent_id"| Span
    Session -->|"groups"| Trace
    Project -->|"has"| Session
    
    Dataset -->|"versioned by"| DatasetVersion
    Dataset -->|"contains"| DatasetExample
    DatasetExample -->|"versioned by"| DatasetExampleRevision
    DatasetExampleRevision -->|"belongs to"| DatasetVersion
    DatasetExample -->|"references"| Span
    
    Experiment -->|"uses"| DatasetVersion
    Experiment -->|"produces"| ExperimentRun
    ExperimentRun -->|"for"| DatasetExample
    ExperimentRun -->|"creates"| Trace
    
    Span -->|"annotated by"| SpanAnnotation
    ExperimentRun -->|"annotated by"| ExperimentRunAnnotation
    
    Evaluator -->|"subtype"| LLMEvaluator
    Evaluator -->|"subtype"| CodeEvaluator
    
    LLMEvaluator -->|"uses"| Prompt
    LLMEvaluator -->|"uses"| PromptVersion
    
    Prompt -->|"has versions"| PromptVersion
```

**Sources**: [src/phoenix/db/models.py:602-712](), [src/phoenix/db/models.py:887-1163](), [src/phoenix/db/models.py:1644-2087]()

---

## Traces and Spans

### Trace

A **Trace** represents a complete execution flow through an LLM application. Each trace is uniquely identified by a `trace_id` and belongs to a **Project**. Traces are the high-level containers for observability data.

- **Implementation**: The `models.Trace` SQLAlchemy ORM model defines columns such as `trace_id`, `project_rowid`, `start_time`, and `end_time`.  
- **Data Flow**: Traces are ingested during runtime through OpenTelemetry protocols and stored internally for analysis and query.  
- **Key Class**: `models.Trace` manages database representation. The GraphQL API exposes it through the `Trace` type for queries.  

| Property | Type | Description |
|----------|------|-------------|
| `trace_id` | `str` | Globally unique identifier for the trace |
| `project_rowid` | `int` | Foreign key to owning project |
| `start_time` | `datetime` | When the trace began |
| `end_time` | `datetime` | When the trace completed |

**Sources**: [src/phoenix/db/models.py:659-712](), [src/phoenix/server/api/types/Trace.py:1-50]()

---

### Span

A **Span** is the fundamental unit of work in a trace. Spans form a tree structure via the `parent_id` relationship, with the root span having `parent_id=None`. Spans contain detailed metadata including inputs, outputs, token counts, and latency information.

- **Implementation**: The `models.Span` ORM model stores span data, including IDs, names, timing, status codes, and OpenTelemetry attributes.  
- **Data Flow**: Spans are collected from distributed tracing instrumentation and recorded as children of traces. They are queried with pagination and filtering support.  
- **Key Functions/Classes**:  
  - `models.Span` defines DB schema.  
  - GraphQL type `Span` exposes fields with data loader batching (`src/phoenix/server/api/types/Span.py`).  
  - `SpanKind` enum organizes span types for UI and processing logic.

| Property | Type | Description |
|----------|------|-------------|
| `span_id` | `str` | Unique identifier for the span |
| `parent_id` | `Optional[str]` | Parent span ID (null for root spans) |
| `name` | `str` | Human-readable name |
| `span_kind` | `SpanKind` | Type of operation (LLM, RETRIEVER, etc.) |
| `start_time` | `datetime` | Start timestamp |
| `end_time` | `datetime` | End timestamp |
| `attributes` | `JSON` | OpenTelemetry attributes containing metadata |
| `status_code` | `SpanStatusCode` | OK, ERROR, or UNSET |

---

### Natural Language to Code Entity Mapping: Tracing

This diagram maps natural language concepts in tracing to specific code entities.

```mermaid
graph LR
    subgraph "Natural Language Space"
        UserTrace["'A full user request'"]
        UserSpan["'A specific model call'"]
        UserProject["'The production app'"]
    end

    subgraph "Code Entity Space"
        TraceEntity["models.Trace<br/>(src/phoenix/db/models.py)"]
        SpanEntity["models.Span<br/>(src/phoenix/db/models.py)"]
        ProjectEntity["models.Project<br/>(src/phoenix/db/models.py)"]
        
        GqlTrace["GraphQL Trace<br/>(src/phoenix/server/api/types/Trace.py)"]
        GqlSpan["GraphQL Span<br/>(src/phoenix/server/api/types/Span.py)"]
    end

    UserTrace --- TraceEntity
    UserSpan --- SpanEntity
    UserProject --- ProjectEntity
    
    TraceEntity --- GqlTrace
    SpanEntity --- GqlSpan
```

**Sources**: [src/phoenix/db/models.py:602-885](), [src/phoenix/server/api/types/Span.py:127-150](), [src/phoenix/server/api/types/Trace.py:1-50]()

---

### SpanKind Enumeration

`SpanKind` categorizes the nature of work a span represents. This enumeration informs filtering, UI icons, and aggregation logic.

| Value       | Description                         |
|-------------|-----------------------------------|
| `CHAIN`     | Orchestration or workflow span    |
| `LLM`       | LLM inference call                |
| `RETRIEVER` | Document retrieval operation       |
| `RERANKER`  | Document reranking                 |
| `EMBEDDING` | Embedding generation              |
| `TOOL`      | Tool or function call             |
| `AGENT`     | Agent decision-making             |
| `EVALUATOR` | Evaluation logic execution        |
| `GUARDRAIL` | Guardrail validation span         |
| `UNKNOWN`   | Unknown type                      |

- Defined as `SpanKind` enum in `src/phoenix/server/api/types/Span.py` [lines 56-81]()  
- Supports case-insensitive fallback and unknown default.

**Sources**: [src/phoenix/server/api/types/Span.py:57-80]()

---

## Projects and Sessions

### Project

A **Project** is the highest organizational unit in Phoenix. All traces, sessions, datasets, and experiments belong to a project. Projects let you segment data by application or environment.

- **Implementation**:  
  - `models.Project` ORM model stores project metadata.  
  - GraphQL type `Project` provides fields like `name`, description, and data counts, leveraging data loaders for efficiency.  

| Property       | Type        | Description                    |
|----------------|-------------|--------------------------------|
| `id`           | int         | Unique project identifier      |
| `name`         | string      | Project name                   |
| `description`  | string|null | Optional project description   |
| `gradient_start_color` | string | UI theming property           |
| `gradient_end_color` | string  | UI theming property           |

**Sources**: [src/phoenix/db/models.py:602-640](), [src/phoenix/server/api/types/Project.py:61-122]()

---

### ProjectSession

A **ProjectSession** groups related traces as a logical unit—often representing a multi-turn conversation or workflow within a project. Sessions help correlate related traces for analysis.

- **Implementation**:  
  - `models.ProjectSession` stores session metadata.  
  - GraphQL type `ProjectSession` exposes session data and aggregates trace counts.  

| Property       | Type | Description             |
|----------------|------|-------------------------|
| `id`           | int  | Unique session ID       |
| `project_id`   | int  | Owning project's ID     |
| `name`         | string | Session name or slug   |
| `start_time`   | datetime | When session started |
| `end_time`     | datetime | When session ended   |

**Sources**: [src/phoenix/db/models.py:642-657](), [src/phoenix/server/api/types/ProjectSession.py:1-50]()

---

## Datasets and Experiments

### Dataset

A **Dataset** contains a versioned set of examples for experiments and evaluations. Datasets support example revisions and version metadata for reproducibility.

- **Implementation**:  
  - `models.Dataset` and `models.DatasetVersion` represent dataset and their versions.  
  - `DatasetExample` stores individual examples.  
  - Dataset versioning is key to experiment reproducibility.  
  - GraphQL `Dataset` type exposes dataset properties and linked examples.

| Property       | Type        | Description                          |
|----------------|-------------|------------------------------------|
| `id`           | int         | Dataset unique identifier           |
| `name`         | string      | Dataset name                       |
| `description`  | string|null | Optional description                 |
| `versions`     | List        | Versions attached to the dataset    |

**Sources**: [src/phoenix/db/models.py:887-936](), [src/phoenix/server/api/types/Dataset.py:44-146]()

---

### Experiment

An **Experiment** runs evaluations of task functions over a dataset version. It tracks runs and metadata for repeated experiment analysis.

- **Implementation**:  
  - `models.Experiment` stores experiment configuration.  
  - An experiment links to a specific dataset version.  
  - GraphQL exposes `Experiment` type.  

| Property       | Type      | Description                   |
|----------------|-----------|-------------------------------|
| `id`           | int       | Unique experiment ID          |
| `name`         | string    | Name of the experiment        |
| `dataset_version_id` | int  | Dataset version used          |

**Sources**: [src/phoenix/db/models.py:1041-1100](), [src/phoenix/server/api/types/Experiment.py:1-50]()

---

### ExperimentRun

An **ExperimentRun** records the output of an experiment for a single dataset example. It includes generated traces and annotations.

- **Implementation**:  
  - `models.ExperimentRun` tracks run metadata and links to dataset example and traces.  
  - GraphQL type supports querying run details.

| Property       | Type      | Description                      |
|----------------|-----------|----------------------------------|
| `id`           | int       | Unique experiment run ID         |
| `dataset_example_id` | int   | Dataset example involved         |
| `trace_id`     | string    | Trace generated in this run      |

**Sources**: [src/phoenix/db/models.py:1102-1163](), [src/phoenix/server/api/types/ExperimentRun.py:1-50]()

---

## Annotations

Annotations provide feedback or metadata on spans, traces, or sessions. They can be generated by humans, LLMs, or code-based logic and are essential for evaluation and debugging.

### Annotation Interface (GraphQL)

The `Annotation` interface describes the core properties common to all annotation types.

| Property       | Type                | Description                                      |
|----------------|---------------------|------------------------------------------------|
| `name`         | `String!`           | Annotation name, e.g., 'helpfulness'            |
| `annotatorKind`| `AnnotatorKind!`     | Kind of annotator: LLM, HUMAN, or CODE          |
| `label`        | `String`            | Categorical label value                          |
| `score`        | `Float`             | Numeric score value                              |
| `explanation`  | `String`            | Explanation or reasoning for the annotation     |
| `source`       | `AnnotationSource!` | Source of annotation, e.g., API or APP          |
| `identifier`   | `String!`           | Unique identifier                                |
| `createdAt`    | `DateTime!`         | Timestamp of creation                            |
| `updatedAt`    | `DateTime!`         | Timestamp of last update                         |
| `user`         | `User` (optional)   | User who created the annotation (if applicable) |

- Annotation kinds enable filtering and aggregation in queries.

**Sources**: [app/schema.graphql:121-158](), [src/phoenix/db/models.py:1165-1428]()

---

## Evaluators

Evaluators judge LLM outputs by applying metrics or scoring functions. Phoenix supports multiple evaluator types, including LLM-based and code-based evaluators.

### Natural Language to Code Entity Mapping: Evaluation

```mermaid
graph LR
    subgraph "Natural Language Space"
        UserEval["'An LLM-based judge'"]
        UserMapping["'Input field mapping'"]
        UserResult["'The evaluation score'"]
    end

    subgraph "Code Entity Space"
        LLMEval["models.LLMEvaluator<br/>(src/phoenix/db/models.py)"]
        CodeEval["models.CodeEvaluator<br/>(src/phoenix/db/models.py)"]
        InputMap["apply_input_mapping<br/>(src/phoenix/server/api/evaluators.py)"]
        Annotation["models.SpanAnnotation<br/>(src/phoenix/db/models.py)"]
    end

    UserEval --- LLMEval
    UserEval --- CodeEval
    UserMapping --- InputMap
    UserResult --- Annotation
```

---

### LLMEvaluator

An LLM-based evaluator prompts an LLM with a structured output prompt and interprets the output as scores or categories, facilitating nuanced automatic evaluation.

- **Implementation**:  
  - Stored in `models.LLMEvaluator`.  
  - Uses references to prompt templates and versioning.  
  - Output conforms to categorical or continuous annotation configurations.  

**Sources**: [src/phoenix/db/models.py:1732-1846](), [src/phoenix/server/api/types/Evaluator.py:80-120]()

---

## Prompts and Versions

### Prompt

A **Prompt** organizes LLM prompt templates into versioned entities to manage prompt changes systematically.

- **Implementation**:  
  - `models.Prompt` stores prompt metadata and references versions.  
  - GraphQL `Prompt` type supports access to prompt versions and properties.

### PromptVersion

A **PromptVersion** contains the concrete prompt template, LLM invocation parameters, and output format details.

- **Implementation**:  
  - Stored in `models.PromptVersion`.  
  - Supports template formats, variables, and associated model/cloud provider config.  
  - Used by evaluators and playground interfaces.

**Sources**: [src/phoenix/db/models.py:1866-2087](), [src/phoenix/server/api/types/PromptVersion.py:115-128]()

---

# Summary Table of Core Concepts

| Concept         | Description                                      | Key Code Entities                                        |
|-----------------|------------------------------------------------|----------------------------------------------------------|
| Project         | Top-level container for all artifacts          | `models.Project`, GraphQL `Project`                      |
| ProjectSession  | Grouping of related traces (e.g., user session)| `models.ProjectSession`, GraphQL `ProjectSession`        |
| Trace           | Complete LLM request journey                    | `models.Trace`, GraphQL `Trace`                          |
| Span            | Unit of work within a trace                      | `models.Span`, GraphQL `Span`, `SpanKind` enum           |
| Dataset         | Versioned collection of examples                | `models.Dataset`, `models.DatasetVersion`, GraphQL `Dataset` |
| Experiment      | Run of evaluations over dataset version         | `models.Experiment`, GraphQL `Experiment`                |
| ExperimentRun   | Single example run within an experiment          | `models.ExperimentRun`, GraphQL `ExperimentRun`           |
| Annotation      | Feedback or metadata on spans or runs           | GraphQL interface, `models.SpanAnnotation`                |
| Evaluator       | Entity applying scoring or classification       | `models.Evaluator`, `models.LLMEvaluator`, `models.CodeEvaluator` |
| Prompt          | Versioned prompt template set                     | `models.Prompt`, `models.PromptVersion`, GraphQL `Prompt`|

---

This page provides a technical grounding in the primary entities of Phoenix to help engineers understand their implementation, relationships, and usage in the codebase.

**Sources**:  
[src/phoenix/db/models.py:602-885](),  
[src/phoenix/db/models.py:887-1163](),  
[src/phoenix/db/models.py:1644-2087](),  
[src/phoenix/server/api/types/Span.py:57-267](),  
[src/phoenix/server/api/types/Trace.py:1-50](),  
[src/phoenix/server/api/types/Project.py:61-122](),  
[src/phoenix/server/api/types/ProjectSession.py:1-50](),  
[src/phoenix/server/api/types/Dataset.py:44-146](),  
[src/phoenix/server/api/types/Experiment.py:1-50](),  
[src/phoenix/server/api/types/ExperimentRun.py:1-50](),  
[app/schema.graphql:121-158](),  
[src/phoenix/server/api/queries.py:37-43](),  
[src/phoenix/server/api/types/Evaluator.py:80-120]()

---

# Page: Server Architecture

# Server Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/schema.graphql](app/schema.graphql)
- [app/src/api/__generated__/v1.ts](app/src/api/__generated__/v1.ts)
- [app/src/components/trace/SpanKindIcon.tsx](app/src/components/trace/SpanKindIcon.tsx)
- [app/src/pages/playground/__tests__/playgroundAgentContextUtils.test.ts](app/src/pages/playground/__tests__/playgroundAgentContextUtils.test.ts)
- [app/src/pages/playground/playgroundAgentContextUtils.ts](app/src/pages/playground/playgroundAgentContextUtils.ts)
- [app/src/window.d.ts](app/src/window.d.ts)
- [cspell.json](cspell.json)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx)
- [js/packages/phoenix-client/src/__generated__/api/v1.ts](js/packages/phoenix-client/src/__generated__/api/v1.ts)
- [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py](packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py)
- [packages/phoenix-client/tests/canary/sdk/anthropic/test_messages.py](packages/phoenix-client/tests/canary/sdk/anthropic/test_messages.py)
- [packages/phoenix-client/tests/canary/sdk/openai/test_chat.py](packages/phoenix-client/tests/canary/sdk/openai/test_chat.py)
- [schemas/openapi.json](schemas/openapi.json)
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
- [src/phoenix/server/agents/context.py](src/phoenix/server/agents/context.py)
- [src/phoenix/server/agents/prompts/context/PLAYGROUND_CONTEXT_INSTRUCTIONS.xml.j2](src/phoenix/server/agents/prompts/context/PLAYGROUND_CONTEXT_INSTRUCTIONS.xml.j2)
- [src/phoenix/server/agents/prompts/skills/playground/SKILL.md](src/phoenix/server/agents/prompts/skills/playground/SKILL.md)
- [src/phoenix/server/api/context.py](src/phoenix/server/api/context.py)
- [src/phoenix/server/api/dataloaders/__init__.py](src/phoenix/server/api/dataloaders/__init__.py)
- [src/phoenix/server/api/input_types/SpanSort.py](src/phoenix/server/api/input_types/SpanSort.py)
- [src/phoenix/server/api/mutations/__init__.py](src/phoenix/server/api/mutations/__init__.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/routers/agents.py](src/phoenix/server/api/routers/agents.py)
- [src/phoenix/server/api/routers/v1/experiment_evaluations.py](src/phoenix/server/api/routers/v1/experiment_evaluations.py)
- [src/phoenix/server/api/routers/v1/experiment_runs.py](src/phoenix/server/api/routers/v1/experiment_runs.py)
- [src/phoenix/server/api/routers/v1/experiments.py](src/phoenix/server/api/routers/v1/experiments.py)
- [src/phoenix/server/api/routers/v1/spans.py](src/phoenix/server/api/routers/v1/spans.py)
- [src/phoenix/server/api/routers/v1/traces.py](src/phoenix/server/api/routers/v1/traces.py)
- [src/phoenix/server/api/schema.py](src/phoenix/server/api/schema.py)
- [src/phoenix/server/api/types/Dataset.py](src/phoenix/server/api/types/Dataset.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/dml_event_handler.py](src/phoenix/server/dml_event_handler.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/settings.py](src/phoenix/settings.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [tests/integration/_helpers.py](tests/integration/_helpers.py)
- [tests/integration/auth/conftest.py](tests/integration/auth/conftest.py)
- [tests/integration/auth/test_auth.py](tests/integration/auth/test_auth.py)
- [tests/unit/server/agents/capabilities/contexts/test_capabilities.py](tests/unit/server/agents/capabilities/contexts/test_capabilities.py)
- [tests/unit/server/api/routers/v1/test_experiments.py](tests/unit/server/api/routers/v1/test_experiments.py)
- [tests/unit/server/api/routers/v1/test_spans.py](tests/unit/server/api/routers/v1/test_spans.py)
- [tests/unit/server/api/routers/v1/test_traces.py](tests/unit/server/api/routers/v1/test_traces.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)

</details>



## Purpose and Scope

This document provides a high-level overview of the Phoenix server architecture, outlining its FastAPI application structure, API layers, data storage approach, and background services. Phoenix server is designed to:

- Serve HTTP/gRPC endpoints for ingesting OpenTelemetry traces via OTLP protocol
- Host GraphQL and REST APIs for querying and managing observability and evaluation data
- Serve the React-based frontend static assets
- Manage background daemons for batch insertions, cost calculations, experiment execution, and model synchronization

This page offers a parent-level summary. Detailed architecture is documented in these child pages:

- [Application Server & Configuration](#2.1) – FastAPI app internals and startup lifecycle  
- [GraphQL API](#2.2) – GraphQL schema, resolvers, DataLoader pattern  
- [REST API & OpenAPI](#2.3) – REST endpoints, OpenAPI spec, client generation  
- [OTLP Ingestion & gRPC Server](#2.4) – Ingestion via OTLP over HTTP and gRPC  
- [Database Layer & Migrations](#2.5) – SQLAlchemy ORM models and Alembic migrations  
- [Authentication & Authorization](#2.6) – Auth methods, RBAC, API keys  
- [Cost Tracking & Model Pricing](#2.7) – Model cost manifest, cost calculation daemons  

For information on client libraries, frontend architecture, and deployment, see the relevant sections in the full documentation.

**Sources:** [src/phoenix/server/main.py:1-44](), [src/phoenix/server/app.py:1-250](), [src/phoenix/server/api/schema.py:1-84]()


---

## Application Lifecycle

### Startup Flow Overview

The Phoenix server initialization involves creating the database engine, building the FastAPI app, and starting background services that manage ingestion and processing.

```mermaid
sequenceDiagram
    participant CLI as "phoenix.server.main:main()"
    participant Engine as "phoenix.db.engines:create_engine()"
    participant App as "phoenix.server.app:create_app()"
    participant Lifespan as "phoenix.server.app:lifespan()"
    participant Services as "Background Services"
    participant Uvicorn as "uvicorn.Server"

    CLI->>Engine: Create AsyncEngine
    Note over Engine: SQLite (aiosqlite) or PostgreSQL (asyncpg), run Alembic migrations

    CLI->>App: create_app(db factory, ...)
    App->>App: Build Middleware Stack
    App->>App: build_graphql_schema()
    App->>App: Mount REST and GraphQL routers
    App->>Lifespan: Register lifespan manager

    CLI->>Uvicorn: Start server
    Uvicorn->>Lifespan: Enter lifespan context
    Lifespan->>Services: Start BulkInserter
    Lifespan->>Services: Start GrpcServer (OTLP ingestion)
    Lifespan->>Services: Start DmlEventHandler
    Lifespan->>Services: Start SpanCostCalculator
    Lifespan->>Services: Start GenerativeModelStore
    Lifespan->>Services: Start ExperimentRunner

    Note over Uvicorn: Server ready; serving API & UI requests
```

### Entry Point: `main()`

The entry point is the `main()` function ([src/phoenix/server/main.py:17-44]()) which performs:

- Loading environment variables and configuring logging  
- Parsing CLI arguments (`serve`, `db`)  
- Invoking the respective command function  

### Application Factory: `create_app()`

The application's FastAPI instance is created via `create_app()` ([src/phoenix/server/app.py:820-1337]()) which:

- Constructs the middleware stack for CORS, CSRF validation, authentication, compression  
- Builds the Strawberry GraphQL schema and mounts the GraphQL router  
- Mounts API v1 REST endpoints, OAuth2 routes, and static React frontend files  
- Registers a lifespan context manager responsible for running background services  

### Lifespan and Background Services

The lifespan context ([src/phoenix/server/app.py:589-664]()) manages these key background services:

- **BulkInserter**: Efficient batch insertion of incoming spans and annotations to the database  
- **GrpcServer (OTLP)**: Accepts OpenTelemetry spans over gRPC on port 4317  
- **DmlEventHandler**: Watches database mutation events for cache invalidation and subscription updates  
- **SpanCostCalculator**: Periodically processes span data to compute LLM token costs  
- **GenerativeModelStore**: Synchronizes generative model metadata and pricing info  
- **ExperimentRunner**: Runs evaluation experiments asynchronously  

This manager ensures graceful startup and shutdown of all services.

**Sources:** [src/phoenix/server/main.py:17-44](), [src/phoenix/server/app.py:589-664]()

---

## Middleware Stack

Phoenix's middleware layers (from outermost to innermost):

```mermaid
graph TB
    Request["Incoming HTTP Request"]
    CORSM["CORSMiddleware"]
    CSRF["RequestOriginHostnameValidator (CSRF Protection)"]
    Auth["AuthenticationMiddleware (BearerTokenAuthBackend)"]
    Headers["HeadersMiddleware"]
    GZIP["GZipMiddleware (Compression)"]
    Router["FastAPI Application Router"]

    Request --> CORSM
    CORSM --> CSRF
    CSRF --> Auth
    Auth --> Headers
    Headers --> GZIP
    GZIP --> Router
```

| Middleware Component                    | Description                                  | Source                                      |
|---------------------------------------|----------------------------------------------|---------------------------------------------|
| `CORSMiddleware`                      | Handles Cross-Origin Resource Sharing         | [src/phoenix/server/app.py:952-957]()       |
| `RequestOriginHostnameValidator`     | Validates request origin for CSRF protection | [src/phoenix/server/app.py:359-375]()       |
| `AuthenticationMiddleware`            | Authenticates requests with bearer tokens    | [src/phoenix/server/app.py:970-977]()       |
| `HeadersMiddleware`                   | Adds standard headers                         | [src/phoenix/server/app.py:978-982]()       |
| `GZipMiddleware`                     | Compresses HTTP responses                      | [src/phoenix/server/app.py:980-986]()       |

For authentication details, see the [Authentication & Authorization](#2.6) child page.

**Sources:** [src/phoenix/server/app.py:950-991]()

---

## API Layers

Phoenix provides three main API access points for clients:

```mermaid
graph LR
    subgraph "Clients"
        OTLP["OTLP Exporter (OpenTelemetry Collector)"]
        RestClient["arize-phoenix-client (REST)"]
        UIClient["React UI (Relay GraphQL)"]
    end

    subgraph "Phoenix Server"
        gRPC["GrpcServer (OTLP gRPC @4317)"]
        HTTPOTLP["OTLP HTTP Endpoint (/v1/traces)"]
        REST["REST API (/v1/*)"]
        GraphQL["GraphQL API (/graphql)"]
    end

    subgraph "Data Layer"
        BulkInserter["BulkInserter (Batch Inserts)"]
        DB["SQLAlchemy AsyncEngine (PostgreSQL/SQLite)"]
    end

    OTLP --> gRPC
    OTLP --> HTTPOTLP
    RestClient --> REST
    UIClient --> GraphQL

    gRPC --> BulkInserter
    HTTPOTLP --> BulkInserter
    REST --> DB
    GraphQL --> DB
    BulkInserter --> DB
```

### REST API (v1)

Accessible under `/v1`, it supports resource CRUD operations, including spans, projects, datasets, annotations, and experiments. It is routed using `create_v1_router()` [src/phoenix/server/app.py:175-180]().

For detailed REST API documentation, see [REST API & OpenAPI](#2.3).

### GraphQL API

Exposed at `/graphql`, the GraphQL API is implemented using Strawberry GraphQL, including Relay-compliant pagination and subscriptions [src/phoenix/server/api/schema.py:32-57]().

It provides a rich queryable graph for entities like Projects, Spans, Datasets, and Evaluators defined in schema files, e.g. [app/schema.graphql:1-134]().

For deeper coverage, see [GraphQL API](#2.2).

### OTLP Ingestion

Trace data is ingested over OTLP:

- **gRPC server** listens on port 4317 and processes OpenTelemetry spans [src/phoenix/server/app.py:70-90]()  
- **HTTP OTLP endpoint** supports OTLP ingestion over HTTP POST requests on REST API  

For OTLP ingestion internal mechanisms, see [OTLP Ingestion & gRPC Server](#2.4).

**Sources:** [src/phoenix/server/app.py:70-180](), [src/phoenix/server/api/schema.py:32-57](), [app/schema.graphql:1-134]()

---

## Database Architecture

Phoenix uses SQLAlchemy 2.0 asyncio ORM on top of either SQLite (aiosqlite driver) or PostgreSQL (asyncpg driver).

### Database Dialects & Engine Creation

```mermaid
graph TB
    subgraph "phoenix.db.engines:create_engine()"
        Dialect{"Database Dialect?"}
    end

    subgraph SQLite["SQLite (aiosqlite)"]
        SQLitePragma["Set Pragmas (journal_mode=WAL, synchronous=NORMAL)"]
        SQLitePool["StaticPool (single connection)"]
    end

    subgraph PostgreSQL["PostgreSQL (asyncpg)"]
        PgIAM["AWS RDS IAM Authentication support"]
        PgPool["Connection Pool with asyncpg"]
    end

    Dialect -->|sqlite| SQLite
    Dialect -->|postgresql| PostgreSQL
```

Engine initialization chooses configuration and connection pool based on database type [src/phoenix/db/engines.py:69-98]().

### ORM Models & Schema

The core data model classes derive from SQLAlchemy's DeclarativeBase [src/phoenix/db/models.py:43-48](). Important domain models include:

- `Project` — logical container of telemetry and experiments [src/phoenix/server/api/types/Project.py:61-63]()  
- `Span` — individual work units within a trace [src/phoenix/server/api/types/Span.py:127-129]()  
- `Dataset` — versioned collection of examples used in evaluation [src/phoenix/server/api/types/Dataset.py:44-46]()  
- Additional types cover annotations, evaluators, generative models, prompt versions, sessions, and experiments.  

### Migrations

Database schema migration is managed by Alembic. Migrations run automatically at startup unless disabled via environment variables (`PHOENIX_DISABLE_MIGRATIONS`) [src/phoenix/config.py:180-190]().

Details on migration and database schema are in [Database Layer & Migrations](#2.5).

**Sources:** [src/phoenix/db/engines.py:50-98](), [src/phoenix/db/models.py:43-150](), [src/phoenix/config.py:170-190]()

---

## Data Ingestion Pipeline

### Bulk Insertion with BulkInserter

To avoid overwhelming the database with many small writes, the server ingests spans and annotations into an asynchronous queue. The `BulkInserter` service flushes these batches periodically into the database for efficiency [src/phoenix/db/bulk_inserter.py]().

### Database Mutation Events (DML Event Handling)

To stay responsive to data changes, a `DmlEventHandler` listens for database mutation events encapsulated as `DmlEvent` objects. It triggers cache invalidation on `DataLoaders` and propagates updates to subscribed GraphQL clients for real-time UI updates [src/phoenix/server/dml_event_handler.py](), [src/phoenix/server/app.py:795-805]().

**Sources:** [src/phoenix/db/bulk_inserter.py](), [src/phoenix/server/dml_event_handler.py](), [src/phoenix/server/app.py:790-810]()

---

## Request Context and DataLoaders

Every GraphQL request is served with a rich `Context` container embedding over 80 **DataLoaders** ([src/phoenix/server/api/context.py:120-216]()).

### Purpose of DataLoaders

DataLoaders batch and cache database lookups within the scope of a single request to prevent redundant queries and solve the N+1 query problem. Examples include:

- `SpanByIdDataLoader`: Batch load spans by database ID  
- `ProjectByNameDataLoader`: Efficient lookup of projects by name  
- `AnnotationConfigsByProjectDataLoader`: Fetch annotation configurations scoped per project  

This mechanism optimizes GraphQL resolver performance.

**Sources:** [src/phoenix/server/api/context.py:120-216](), [src/phoenix/server/app.py:87-173]()

---

## Session Management for Notebook Usage

Phoenix can be run interactively in notebook environments (Jupyter, Colab, SageMaker) via:

- **ThreadSession**: Runs the FastAPI app in a background thread using `ThreadServer` ([src/phoenix/server/thread_server.py:21-67]())  
- **ProcessSession**: Runs the server in a separate OS process managed via `AppService` ([src/phoenix/services.py]())  

Both manage lifecycles and app interaction programmatically inside notebooks [src/phoenix/session/session.py:70-342]().

**Sources:** [src/phoenix/session/session.py:70-342](), [src/phoenix/server/thread_server.py:21-67]()


---

# Architecture Bridging Diagrams: Mapping Natural Language to Code Entities

```mermaid
graph LR
    NLNode1["Natural Language Space: API Layers"]
    NLNode2["Natural Language Space: Data Storage"]
    NLNode3["Natural Language Space: Server Startup"]

    CodeNode1["FastAPI app: create_app() [src/phoenix/server/app.py:820-1337]"]
    CodeNode2["GraphQL schema: build_graphql_schema() [src/phoenix/server/api/schema.py:32-57]"]
    CodeNode3["REST router: create_v1_router() [src/phoenix/server/api/routers/v1/__init__.py:100-160] (not shown directly, referenced)"]
    CodeNode4["GrpcServer (OTLP gRPC) [src/phoenix/server/app.py:590-640]"]
    CodeNode5["BulkInserter daemon [src/phoenix/db/bulk_inserter.py]"]
    CodeNode6["SQLAlchemy AsyncEngine [src/phoenix/db/engines.py:60-98]"]
    CodeNode7["Alembic Migrations [src/phoenix/db/migrations/versions/*]"]
    CodeNode8["Session management (ThreadSession / ProcessSession) [src/phoenix/session/session.py:70-342]"]

    NLNode1 --> CodeNode1
    CodeNode1 --> CodeNode2
    CodeNode1 --> CodeNode3
    CodeNode1 --> CodeNode4
    CodeNode4 --> CodeNode5
    CodeNode5 --> CodeNode6
    CodeNode6 --> CodeNode7
    NLNode3 --> CodeNode8
```

```mermaid
graph LR
    NL1["Clients: UI, REST, OTLP exporter"]
    NL2["Server APIs: GraphQL, REST, OTLP gRPC/HTTP"]
    NL3["Background Services: BulkInserter, CostCalculator, ExperimentRunner"]
    NL4["Database: PostgreSQL or SQLite with SQLAlchemy ORM"]

    CodeAPI1["GraphQLRouter (/graphql) [src/phoenix/server/api/schema.py]"]
    CodeAPI2["create_v1_router() REST API (/v1/*) [src/phoenix/server/api/routers/v1/*]"]
    CodeAPI3["GrpcServer OTLP port 4317 [src/phoenix/server/grpc_server.py]"]
    CodeBG1["BulkInserter [src/phoenix/db/bulk_inserter.py]"]
    CodeBG2["SpanCostCalculator [src/phoenix/server/daemons/span_cost_calculator.py]"]
    CodeBG3["ExperimentRunner [src/phoenix/server/daemons/experiment_runner.py]"]
    CodeDB["Async Engine & AsyncSession SQLAlchemy [src/phoenix/db/engines.py]"]

    NL1 -->|GraphQL| CodeAPI1
    NL1 -->|REST| CodeAPI2
    NL1 -->|OTLP exporter| CodeAPI3

    CodeAPI3 --> CodeBG1
    CodeAPI1 --> CodeDB
    CodeAPI2 --> CodeDB
    CodeBG1 --> CodeDB

    NL3 --> CodeBG1
    NL3 --> CodeBG2
    NL3 --> CodeBG3
    CodeBG2 --> CodeDB
    CodeBG3 --> CodeDB
```

---

This concludes the high-level architecture overview. For deeper technical details, refer to the child pages on application server configuration, APIs, ingestion, database, authentication, and cost tracking.

# References

- [src/phoenix/server/main.py:1-44]()  
- [src/phoenix/server/app.py:1-250]()  
- [src/phoenix/server/api/schema.py:1-84]()  
- [src/phoenix/db/engines.py:50-98]()  
- [src/phoenix/db/models.py:43-150]()  
- [src/phoenix/db/bulk_inserter.py]()  
- [src/phoenix/server/dml_event_handler.py]()  
- [src/phoenix/server/api/context.py:120-216]()  
- [src/phoenix/session/session.py:70-342]()  
- [src/phoenix/server/thread_server.py:21-67]()

---

# Page: Application Server & Configuration

# Application Server & Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-release-please/SKILL.md](.agents/skills/phoenix-release-please/SKILL.md)
- [MIGRATION.md](MIGRATION.md)
- [app/schema.graphql](app/schema.graphql)
- [app/src/components/trace/SpanKindIcon.tsx](app/src/components/trace/SpanKindIcon.tsx)
- [app/src/window.d.ts](app/src/window.d.ts)
- [cspell.json](cspell.json)
- [scripts/data/generate_traces.py](scripts/data/generate_traces.py)
- [src/phoenix/config.py](src/phoenix/config.py)
- [src/phoenix/db/bulk_inserter.py](src/phoenix/db/bulk_inserter.py)
- [src/phoenix/db/constants.py](src/phoenix/db/constants.py)
- [src/phoenix/db/migrations/versions/f1a6b2f0c9d5_add_span_session_id_index.py](src/phoenix/db/migrations/versions/f1a6b2f0c9d5_add_span_session_id_index.py)
- [src/phoenix/db/types/trace_retention.py](src/phoenix/db/types/trace_retention.py)
- [src/phoenix/server/api/context.py](src/phoenix/server/api/context.py)
- [src/phoenix/server/api/dataloaders/__init__.py](src/phoenix/server/api/dataloaders/__init__.py)
- [src/phoenix/server/api/input_types/SpanSort.py](src/phoenix/server/api/input_types/SpanSort.py)
- [src/phoenix/server/api/mutations/__init__.py](src/phoenix/server/api/mutations/__init__.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/schema.py](src/phoenix/server/api/schema.py)
- [src/phoenix/server/api/types/Dataset.py](src/phoenix/server/api/types/Dataset.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/cli/commands/serve.py](src/phoenix/server/cli/commands/serve.py)
- [src/phoenix/server/grpc_server.py](src/phoenix/server/grpc_server.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/prometheus.py](src/phoenix/server/prometheus.py)
- [src/phoenix/server/retention.py](src/phoenix/server/retention.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [tests/unit/db/types/test_trace_retention.py](tests/unit/db/types/test_trace_retention.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)
- [tests/unit/server/test_retention.py](tests/unit/server/test_retention.py)

</details>



## Purpose and Scope

This document describes the Phoenix application server architecture, including its FastAPI setup, startup lifecycle, configuration management, and session handling. The server serves as the foundation for all Phoenix HTTP/GraphQL endpoints and manages crucial background daemons and request middleware.

For details on the GraphQL API, see [GraphQL API](2.2). For REST API endpoints, see [REST API & OpenAPI](2.3). For gRPC and OTLP ingestion, see [OTLP Ingestion & gRPC Server](2.4).

---

## Server Architecture Overview

Phoenix's server is a FastAPI application constructed and configured in `create_app()` (see [src/phoenix/server/app.py:734-1176]()). It supports two primary deployment modes:

- **Thread-based server** for environments such as interactive notebooks where the server runs in the same process but on a background thread ([src/phoenix/server/thread_server.py:22-68]()).
- **Process-based server** for production use, launched as a standalone process with full daemon management ([src/phoenix/server/main.py:17-44]()).

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
        router_healthz["router.get('/healthz')"]
        router_readyz["router.get('/readyz')"]
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

**Sources:** [src/phoenix/server/app.py:591-1176](), [src/phoenix/server/main.py:17-44](), [src/phoenix/session/session.py:185-216]()

---

## FastAPI Application Creation

### `create_app()` - Factory Function

The `create_app()` function is the core factory responsible for building and configuring the FastAPI application instance. It is defined at [src/phoenix/server/app.py:734-1176]().

This function accepts parameters like a database session factory, flags for authentication and read-only mode, a secret for token signing, initial spans for startup, and the working directory.

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
| Database               | `DbSessionFactory` - encapsulates async sessions         | Passed into `create_app()`                       |
| Authentication Backend | `BearerTokenAuthBackend` - for bearer token auth         | Activated if `authentication_enabled=True`      |
| GraphQL Schema         | Constructed with extensions, queries, mutations, subscriptions | `build_graphql_schema()` [src/phoenix/server/api/schema.py:33-58]() |
| GraphQL Router         | Strawberry GraphQL router at `/graphql`                   | `create_graphql_router()`                        |
| REST API Router        | Versioned V1 REST API at `/v1`                            | `create_v1_router()`                             |
| Auth Router            | Authentication endpoints at `/auth`                       | `create_auth_router()` if auth enabled          |
| OAuth2 Router          | OAuth2 routes at `/oauth2`                                | Always included                                  |
| Agents Router          | Agent endpoints at `/agents`                              | Conditional via `create_agents_router()`        |
| Static Files           | Serves React SPA User Interface at root path              | Starlette `StaticFiles` mount                     |
| Lifespan Context       | Manages startup/shutdown lifecycle and background tasks  | `_lifespan()` async context manager              |

**Sources:** [src/phoenix/server/app.py:734-1176](), [src/phoenix/server/api/schema.py:33-58](), [src/phoenix/config.py:58-79]()

---

## Server Lifecycle Management (Lifespan)

Phoenix manages its startup and shutdown cleanly using an async context manager `_lifespan()` defined at [src/phoenix/server/app.py:591-662]().

This context manager:

- Verifies required environment variables on startup.
- Starts multiple async background daemons in a specific order.
- Provides ingestion queue functions back to the FastAPI internal state.
- Ensures graceful shutdown and cleanup of all async contexts.

### Background Daemons Managed by `_lifespan()`

| Daemon                     | Purpose                                      |
|----------------------------|----------------------------------------------|
| `BulkInserter`             | Manages async ingestion of spans and annotations |
| `GrpcServer`               | gRPC OTLP server listening on port 4317       |
| `DmlEventHandler`          | Handles DB change events and cache invalidations |
| `SpanCostCalculator`       | Calculates token costs for spans               |
| `TraceDataSweeper`         | Applies trace retention policies               |
| `GenerativeModelStore`     | Manages metadata for generative models         |
| `DbDiskUsageMonitor`       | Monitors and warns about DB storage usage      |
| `ExperimentRunner`         | Runs scheduled experiment evaluations          |

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

The ingestion functions yielded by `_lifespan()` become accessible via the FastAPI app state, allowing the GraphQL and REST layers to enqueue new data for ingestion asynchronously.

**Sources:** [src/phoenix/server/app.py:591-662](), [src/phoenix/db/bulk_inserter.py:20-50]()

---

## Middleware Stack

Phoenix composes its HTTP request handling with several middleware layers to provide security, authentication, reporting, and performance optimizations.

| Middleware                    | Purpose                                      | Code References                        |
|-------------------------------|----------------------------------------------|-------------------------------------|
| **CORSMiddleware**            | Manages Cross-Origin Resource Sharing (CORS) policies | FastAPI's CORSMiddleware used [src/phoenix/server/app.py:34-34]() |
| **AuthenticationMiddleware**  | Validates bearer tokens, API keys, sets user context | Uses `BearerTokenAuthBackend` [src/phoenix/server/app.py:47-47]() |
| **RequestOriginHostnameValidator** | CSRF protection; validates origin and host for protected routes | See [src/phoenix/server/app.py:361-377]() |
| **GZipMiddleware**            | Compresses HTTP responses with GZip            | FastAPI/GZipMiddleware [src/phoenix/server/app.py:402-402]() |
| **Custom Middleware Loader**  | Loads additional user-defined middleware from config paths | via `get_env_fastapi_middleware_paths()` [src/phoenix/config.py:69]() |

This layered middleware ensures:

- Robust security by validating origins and authenticating requests.
- Compression for efficient network usage.
- Extensibility for customized middleware.

**Sources:** [src/phoenix/server/app.py:361-455](), [src/phoenix/config.py:69-69]()

---

## Configuration Management

Phoenix centralizes configuration through environment variables, mostly defined and managed in the `phoenix.config` module [src/phoenix/config.py](). This module provides getters for environment variables with defaults and documentation.

### Key Environment Variables

| Variable                         | Purpose                              | Default Value / Notes                              |
|---------------------------------|------------------------------------|--------------------------------------------------|
| `PHOENIX_PORT`                  | HTTP server port                   | `6006` [src/phoenix/config.py:53-53]()           |
| `PHOENIX_GRPC_PORT`             | gRPC port (OTLP trace ingestion)  | `4317` [src/phoenix/config.py:54-54]()           |
| `PHOENIX_SQL_DATABASE_URL`       | Database connection URL            | SQLite file in working directory by default [src/phoenix/config.py:118-129]() |
| `PHOENIX_ENABLE_AUTH`            | Enables authentication             | `False` by default [src/phoenix/config.py:243-243]()  |
| `PHOENIX_WORKING_DIR`            | Directory for CSV/dataset storage  | `~/.arize-phoenix` [src/phoenix/config.py:88-92]() |
| `PHOENIX_ALLOW_EXTERNAL_RESOURCES` | Enable external resources in UI  | Defaults to True [src/phoenix/config.py:119-123]() |

### Runtime Settings Singleton

Runtime settings are encapsulated in the `Settings` class in `src/phoenix/settings.py`. At launch, `initialize_settings()` in `src/phoenix/server/main.py` reads environment variables and sets these settings.

**Configuration examples:**

- SQL logging mode and level
- Migration enablement flags
- FullStory and Scarf.sh telemetry configuration

**Sources:** [src/phoenix/config.py:1-150](), [src/phoenix/server/main.py:32-40]()

---

## Session and Notebook Handling

Phoenix supports interactive notebook usage by abstracting the application lifecycle behind a `Session` class hierarchy in [src/phoenix/session/session.py:70-207]().

### Session Classes

| Session Type     | Description                                                                                         |
|------------------|----------------------------------------------------------------------------------------------------|
| **ThreadSession**| Runs the FastAPI server in a background daemon thread for the notebook process ([src/phoenix/server/thread_server.py:22-68]()) |
| **ProcessSession**| Creates and manages a standalone server subprocess encapsulated in an `AppService` instance ([src/phoenix/session/session.py:148-183]()) |

### `Session` Base Class

- Stores host, port, database URL, working directory, and notebook environment type.
- Provides properties like `url` for the Phoenix app and a `view()` method to embed the UI in notebooks via an IFrame.

### Dataflow: Notebook Session Integration

```mermaid
graph LR
    subgraph NotebookEnvironment
        UserCode["User calls px.launch_app()"]
        Client["Phoenix Python Client"]
    end
    
    subgraph ServerProcess
        ThreadServer["ThreadServer (background thread)"]
        FastAPIApp["FastAPI Application"]
        Database["SQLite/PostgreSQL DB"]
    end
    
    UserCode --> ThreadServer
    ThreadServer --> FastAPIApp
    Client --> FastAPIApp
    FastAPIApp --> Database
```

This design lets notebook users run a Phoenix server embedded in their environment with access to all API endpoints, while also supporting a full standalone server deployment for other clients.

**Sources:** [src/phoenix/session/session.py:70-207](), [src/phoenix/server/thread_server.py:22-68]()

---

# Summary

This page detailed how the Phoenix application server is constructed and operates. The FastAPI app is created with a rich middleware stack and mounted routers for GraphQL, REST, OAuth2, and agents. A dedicated lifespan manager initializes and cleans up multiple background daemons that power ingestion, tracing, cost calculations, and more.

Configuration is externally managed via environment variables centralized in `phoenix.config`, with runtime settings initialized early in the server process. Interactive notebook environments are supported via session abstractions that launch the Phoenix server inline with user code.

This foundational layer enables the scalable, extensible AI observability platform that Phoenix provides.

---

**Sources:**  
[src/phoenix/server/app.py](),  
[src/phoenix/session/session.py](),  
[src/phoenix/server/main.py](),  
[src/phoenix/config.py](),  
[src/phoenix/server/thread_server.py](),  
[src/phoenix/server/api/schema.py]()

---

# Page: GraphQL API

# GraphQL API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/schema.graphql](app/schema.graphql)
- [app/src/components/trace/SpanKindIcon.tsx](app/src/components/trace/SpanKindIcon.tsx)
- [app/src/window.d.ts](app/src/window.d.ts)
- [cspell.json](cspell.json)
- [scripts/data/generate_traces.py](scripts/data/generate_traces.py)
- [src/phoenix/config.py](src/phoenix/config.py)
- [src/phoenix/db/helpers.py](src/phoenix/db/helpers.py)
- [src/phoenix/server/api/auth.py](src/phoenix/server/api/auth.py)
- [src/phoenix/server/api/context.py](src/phoenix/server/api/context.py)
- [src/phoenix/server/api/dataloaders/__init__.py](src/phoenix/server/api/dataloaders/__init__.py)
- [src/phoenix/server/api/dataloaders/cache/two_tier_cache.py](src/phoenix/server/api/dataloaders/cache/two_tier_cache.py)
- [src/phoenix/server/api/dataloaders/document_evaluation_summaries.py](src/phoenix/server/api/dataloaders/document_evaluation_summaries.py)
- [src/phoenix/server/api/dataloaders/latency_ms_quantile.py](src/phoenix/server/api/dataloaders/latency_ms_quantile.py)
- [src/phoenix/server/api/dataloaders/min_start_or_max_end_times.py](src/phoenix/server/api/dataloaders/min_start_or_max_end_times.py)
- [src/phoenix/server/api/dataloaders/record_counts.py](src/phoenix/server/api/dataloaders/record_counts.py)
- [src/phoenix/server/api/dataloaders/session_token_usages.py](src/phoenix/server/api/dataloaders/session_token_usages.py)
- [src/phoenix/server/api/dataloaders/span_annotations.py](src/phoenix/server/api/dataloaders/span_annotations.py)
- [src/phoenix/server/api/dataloaders/token_counts.py](src/phoenix/server/api/dataloaders/token_counts.py)
- [src/phoenix/server/api/input_types/CreateSpanAnnotationInput.py](src/phoenix/server/api/input_types/CreateSpanAnnotationInput.py)
- [src/phoenix/server/api/input_types/CreateTraceAnnotationInput.py](src/phoenix/server/api/input_types/CreateTraceAnnotationInput.py)
- [src/phoenix/server/api/input_types/PatchAnnotationInput.py](src/phoenix/server/api/input_types/PatchAnnotationInput.py)
- [src/phoenix/server/api/input_types/SpanSort.py](src/phoenix/server/api/input_types/SpanSort.py)
- [src/phoenix/server/api/mutations/__init__.py](src/phoenix/server/api/mutations/__init__.py)
- [src/phoenix/server/api/mutations/api_key_mutations.py](src/phoenix/server/api/mutations/api_key_mutations.py)
- [src/phoenix/server/api/mutations/dataset_mutations.py](src/phoenix/server/api/mutations/dataset_mutations.py)
- [src/phoenix/server/api/mutations/experiment_mutations.py](src/phoenix/server/api/mutations/experiment_mutations.py)
- [src/phoenix/server/api/mutations/project_mutations.py](src/phoenix/server/api/mutations/project_mutations.py)
- [src/phoenix/server/api/mutations/span_annotations_mutations.py](src/phoenix/server/api/mutations/span_annotations_mutations.py)
- [src/phoenix/server/api/mutations/trace_annotations_mutations.py](src/phoenix/server/api/mutations/trace_annotations_mutations.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/routers/v1/sessions.py](src/phoenix/server/api/routers/v1/sessions.py)
- [src/phoenix/server/api/schema.py](src/phoenix/server/api/schema.py)
- [src/phoenix/server/api/types/Annotation.py](src/phoenix/server/api/types/Annotation.py)
- [src/phoenix/server/api/types/Dataset.py](src/phoenix/server/api/types/Dataset.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/SpanAnnotation.py](src/phoenix/server/api/types/SpanAnnotation.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/api/types/TraceAnnotation.py](src/phoenix/server/api/types/TraceAnnotation.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [tests/unit/server/api/mutations/test_project_mutations.py](tests/unit/server/api/mutations/test_project_mutations.py)
- [tests/unit/server/api/mutations/test_span_annotation_mutations.py](tests/unit/server/api/mutations/test_span_annotation_mutations.py)
- [tests/unit/server/api/routers/v1/test_list_project_traces.py](tests/unit/server/api/routers/v1/test_list_project_traces.py)
- [tests/unit/server/api/routers/v1/test_sessions.py](tests/unit/server/api/routers/v1/test_sessions.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/types/test_SpanAnnotation.py](tests/unit/server/api/types/test_SpanAnnotation.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)
- [tests/unit/server/api/types/test_TraceAnnotation.py](tests/unit/server/api/types/test_TraceAnnotation.py)

</details>



## Purpose and Scope

The GraphQL API is the core programmatic interface for interacting with Phoenix’s AI observability platform. It provides structured, typed access to key domain concepts such as traces, spans, datasets, experiments, prompts, users, and annotations. This API enables clients to query, mutate, and subscribe to relevant data artifacts with efficient batching and real-time updates.

This documentation covers:

- The GraphQL schema and type system
- Resolver function implementations and practices
- Use of the DataLoader pattern to optimize database access
- Definition and organization of queries, mutations, and subscriptions
- Integration with FastAPI and authentication workflows

Related API aspects:

- REST API endpoints: [2.3 REST API & OpenAPI](2.3)
- OTLP and gRPC ingestion: [2.4 OTLP Ingestion & gRPC Server](2.4)
- Frontend GraphQL usage: [4.1 Application Structure & Build System](4.1)

---

## Schema Construction

Phoenix uses **Strawberry GraphQL**, leveraging Python's type annotations for declarative schema definition. The GraphQL schema is instantiated in [src/phoenix/server/api/schema.py:33-58]() and consists of three main root types:

- `Query`: Entry point for all read (fetch) operations.
- `Mutation`: Entry point for all write (modifying) operations.
- `Subscription`: Entry point for real-time data streaming.

Additional schema extensions provide error masking and support for custom mod extensions.

### Schema Building Architecture

```mermaid
graph TB
    BuildSchema["build_graphql_schema()"]
    
    Query["Query<br/>(src/phoenix/server/api/queries.py)"]
    Mutation["Mutation<br/>(src/phoenix/server/api/mutations/__init__.py)"]
    Subscription["Subscription<br/>(src/phoenix/server/api/subscriptions.py)"]
    
    Extensions["SchemaExtension[]"]
    MaskErrors["get_mask_errors_extension()<br/>(src/phoenix/server/api/schema.py)"]
    UserExtensions["User Extensions<br/>(via PHOENIX_GQL_EXTENSION_PATHS env)"]
    
    InterfaceTypes["Interface Types"]
    ChatCompletionPayload["ChatCompletionSubscriptionPayload"]
    EvaluatorInterface["Evaluator"]
    
    StrawberrySchema["strawberry.Schema"]
    ExportedSchema["_EXPORTED_GRAPHQL_SCHEMA<br/>(app/schema.graphql)"]
    
    BuildSchema --> Query
    BuildSchema --> Mutation
    BuildSchema --> Subscription
    BuildSchema --> Extensions
    BuildSchema --> InterfaceTypes
    
    Extensions --> MaskErrors
    Extensions --> UserExtensions
    
    InterfaceTypes --> ChatCompletionPayload
    InterfaceTypes --> EvaluatorInterface
    
    BuildSchema --> StrawberrySchema
    StrawberrySchema --> ExportedSchema
```

- The schema factory method `build_graphql_schema` constructs the full schema with root types, extensions, and interface implementations.
- Custom scalar types such as `Identifier`, `CronExpression`, `SecretStr`, and `RedactedString` are configured during schema creation.
- The exported GraphQL schema SDL file (`app/schema.graphql`) is generated from this schema.

**Sources:** [src/phoenix/server/api/schema.py:33-58](), [src/phoenix/server/app.py:182-182](), [src/phoenix/config.py:70-70]()

---

## Core Type System

Phoenix’s schema uses Strawberry’s Relay-compliant Node interface, which provides globally unique IDs for all important types. Key domain types implement this `Node` interface, ensuring consistency in identification and pagination.

### Node Interface Hierarchy

```mermaid
graph TB
    Node["Node Interface<br/>(strawberry.relay)"]

    Span["Span<br/>id: NodeID[int]")]
    Trace["Trace<br/>id: NodeID[int]")]
    Project["Project<br/>id: NodeID[int]")]
    Dataset["Dataset<br/>id: NodeID[int]")]
    DatasetExample["DatasetExample<br/>id: NodeID[int]")]
    Experiment["Experiment<br/>id: NodeID[int]")]
    ExperimentRun["ExperimentRun<br/>id: NodeID[int]")]
    Prompt["Prompt<br/>id: NodeID[int]")]
    User["User<br/>id: NodeID[int])"]

    Node --> Span
    Node --> Trace
    Node --> Project
    Node --> Dataset
    Node --> DatasetExample
    Node --> Experiment
    Node --> ExperimentRun
    Node --> Prompt
    Node --> User

    Annotation["Annotation Interface"]
    SpanAnnotation["SpanAnnotation"]
    TraceAnnotation["TraceAnnotation"]

    Annotation --> SpanAnnotation
    Annotation --> TraceAnnotation
```

- Each type caches its database record internally (`db_record`) when available to avoid redundant queries.
- The `NodeID[int]` types encode database row IDs as global IDs opaque to clients.

Example pattern from `Span` type:

```python
@strawberry.type
class Span(Node):
    id: NodeID[SpanRowId]
    db_record: strawberry.Private[Optional[models.Span]] = None

    def __post_init__(self) -> None:
        if self.db_record and self.id != self.db_record.id:
            raise ValueError("Span ID mismatch")
    
    @strawberry.field
    async def name(self, info: Info[Context, None]) -> str:
        if self.db_record:
            return self.db_record.name
        value = await info.context.data_loaders.span_fields.load(
            (self.id, models.Span.name),
        )
        return str(value)
```

**Sources:** [src/phoenix/server/api/types/Span.py:127-134](), [src/phoenix/server/api/types/Project.py:61-68](), [src/phoenix/server/api/types/Dataset.py:44-51]()

---

### Primary Domain Types and Relationships

```mermaid
graph LR
    Project["Project"]
    Trace["Trace"]
    Span["Span"]
    ProjectSession["ProjectSession"]

    Dataset["Dataset"]
    DatasetExample["DatasetExample"]
    DatasetVersion["DatasetVersion"]
    DatasetSplit["DatasetSplit"]

    Experiment["Experiment"]
    ExperimentRun["ExperimentRun"]

    Prompt["Prompt"]
    PromptVersion["PromptVersion"]

    Project -->|"traces"| Trace
    Project -->|"spans"| Span
    Project -->|"sessions"| ProjectSession

    Trace -->|"spans"| Span
    Span -->|"trace"| Trace
    Span -->|"project"| Project

    Dataset -->|"versions"| DatasetVersion
    Dataset -->|"examples"| DatasetExample
    Dataset -->|"splits"| DatasetSplit

    Experiment -->|"runs"| ExperimentRun
    ExperimentRun -->|"example"| DatasetExample

    Prompt -->|"versions"| PromptVersion
```

| Type              | Description                       | Key Fields & Responsibilities                                            |
|-------------------|---------------------------------|--------------------------------------------------------------------------|
| `Project`          | Top-level organization unit     | `name`, `description`, aggregate counts of spans/traces, sessions       |
| `Trace`            | Execution trace container        | `traceId`, associated spans, project, annotations                        |
| `Span`             | Individual operation within trace| `name`, `spanKind`, `startTime`, `endTime`, `latencyMs`, cost summaries |
| `ProjectSession`   | Grouping of interaction episodes| Session annotations, spans, parent grouping                              |
| `Dataset`          | Collection of labeled examples   | Versions, splits, examples                                               |
| `DatasetExample`   | Individual data example for evals| Input, output, annotations                                               |
| `Experiment`       | Evaluation runs over datasets    | Runs, repeated run groups, job status                                   |
| `ExperimentRun`    | Single execution of an experiment| Input example, outputs, error rate                                       |
| `Prompt`           | Versioned prompt templates       | Chat or text templates versions                                         |

**Sources:** [app/schema.graphql:1-320](), [src/phoenix/server/api/types/Span.py:127-129](), [src/phoenix/server/api/types/Project.py:61-68](), [src/phoenix/server/api/types/Dataset.py:44-46]()

---

## Query Operations

All data fetching operations are defined as methods on the `Query` root type in [src/phoenix/server/api/queries.py]().

### Query Structure Overview

```mermaid
graph TB
    Query["Query"]

    ModelQueries["Model Queries"]
    generativeProviders["generativeProviders()"]
    generativeModels["generativeModels()"]
    playgroundModels["playgroundModels()"]

    ProjectQueries["Project Queries"]
    projects["projects()"]
    project["project(id)"]

    DatasetQueries["Dataset Queries"]
    datasets["datasets()"]
    dataset["dataset(id)"]
    datasetExample["datasetExample(id)"]

    ExperimentQueries["Experiment Queries"]
    experiments["experiments()"]
    experiment["experiment(id)"]

    PromptQueries["Prompt Queries"]
    prompts["prompts()"]
    prompt["prompt(id)"]

    NodeQuery["Node Query"]
    node["node(id: ID!)"]

    Query --> ModelQueries
    Query --> ProjectQueries
    Query --> DatasetQueries
    Query --> ExperimentQueries
    Query --> PromptQueries
    Query --> NodeQuery

    ModelQueries --> generativeProviders
    ModelQueries --> generativeModels
    ModelQueries --> playgroundModels

    ProjectQueries --> projects
    ProjectQueries --> project

    DatasetQueries --> datasets
    DatasetQueries --> dataset
    DatasetQueries --> datasetExample

    ExperimentQueries --> experiments
    ExperimentQueries --> experiment

    PromptQueries --> prompts
    PromptQueries --> prompt
```

- Query fields accept inputs for pagination, filtering, and sorting as appropriate.
- Detailed filtering DSL is supported for spans, sessions, and experiments.
- The `node(id: ID!)` query retrieves any Node type by its global ID.

Example input for model filters:

```python
@strawberry.input
class ModelsInput:
    provider_key: Optional[GenerativeProviderKey]
    model_name: Optional[str] = None
    openai_api_type: Optional[OpenAIApiType] = None
```

### Relay-Style Pagination

Connection types are used for all collections. The API consumers receive:

- `pageInfo` including cursors and paging booleans (`hasNextPage`, `hasPreviousPage`)
- `edges` array containing `{cursor, node}` items

This supports efficient incremental loading in clients.

### Complex Nested Queries Example

Queries involving projects can dive into deeply nested related data like spans and annotations:

```mermaid
graph TB
    ProjectQuery["project(id)"]

    SpansConnection["spans(timeRange, filterCondition)"]
    SpanNode["Span"]

    TraceField["trace"]
    TraceNode["Trace"]

    AnnotationsConnection["annotations(filter)"]
    AnnotationNode["SpanAnnotation"]

    CostSummary["costSummary"]

    Descendants["descendants"]

    ProjectQuery --> SpansConnection
    SpansConnection --> SpanNode

    SpanNode --> TraceField
    SpanNode --> AnnotationsConnection
    SpanNode --> CostSummary
    SpanNode --> Descendants

    TraceField --> TraceNode
    AnnotationsConnection --> AnnotationNode
```

- Query filters (e.g., `filter_condition`, `session_filter_condition`) allow fine-grained slicing of data.
- Filters are compiled into SQLAlchemy expressions [src/phoenix/server/api/queries.py:48-52]().

**Sources:** [src/phoenix/server/api/queries.py:1-160](), [src/phoenix/server/api/types/Project.py:156-176](), [src/phoenix/server/api/types/Span.py:208-223]()

---

## Mutation Operations

Mutation operations handle creation, update, and deletion of server state. They are aggregated under the `Mutation` root type in [src/phoenix/server/api/mutations/__init__.py]() and other grouped mutation files.

### Mutation Categories and Examples

```mermaid
graph TB
    Mutation["Mutation"]

    ProjectMutations["Project Mutations"]
    createProject["createProject"]
    clearProject["clearProject"]

    DatasetMutations["Dataset Mutations"]
    createDataset["createDataset"]
    addExamplesToDataset["addExamplesToDataset"]
    addSpansToDataset["addSpansToDataset"]
    deleteDataset["deleteDataset"]

    ExperimentMutations["Experiment Mutations"]
    deleteExperiments["deleteExperiments"]

    AnnotationMutations["Annotation Mutations"]
    createSpanAnnotation["createSpanAnnotation"]
    createTraceAnnotation["createTraceAnnotation"]

    PromptMutations["Prompt Mutations"]
    createChatPrompt["createChatPrompt"]
    createChatPromptVersion["createChatPromptVersion"]

    Mutation --> ProjectMutations
    Mutation --> DatasetMutations
    Mutation --> ExperimentMutations
    Mutation --> AnnotationMutations
    Mutation --> PromptMutations

    ProjectMutations --> createProject
    ProjectMutations --> clearProject

    DatasetMutations --> createDataset
    DatasetMutations --> addExamplesToDataset
    DatasetMutations --> addSpansToDataset
    DatasetMutations --> deleteDataset

    ExperimentMutations --> deleteExperiments

    AnnotationMutations --> createSpanAnnotation
    AnnotationMutations --> createTraceAnnotation

    PromptMutations --> createChatPrompt
    PromptMutations --> createChatPromptVersion
```

- Mutations often return a payload containing the updated affected entities and the `query` root, enabling effective frontend cache updates.
- Example mutation payload pattern from `AddAnnotationConfigToProjectPayload`:

```graphql
type AddAnnotationConfigToProjectPayload {
  query: Query!
  project: Project!
}
```

- All mutations are executed within database transactions for atomicity and consistency.
- Mutations enqueue DML events (e.g., `DatasetInsertEvent`) to trigger cache invalidation and notify subscription watchers.

**Sources:** [app/schema.graphql:56-64](), [src/phoenix/server/api/mutations/dataset_mutations.py:51-54](), [src/phoenix/server/api/mutations/evaluator_mutations.py:1-58](), [src/phoenix/server/api/context.py:119-234]()

---

## Subscription Operations

Subscriptions provide real-time data streams to clients over WebSocket. Libraries support the `graphql-transport-ws` protocol implemented in `GraphQLRouter`.

### Subscription Overview

- Implemented as async generator methods on the `Subscription` root type ([src/phoenix/server/api/schema.py:14-17]()).
- Primary use case: streaming playground LLM chat completions (`chatCompletion` subscription).
- Enables clients to receive incremental partial results for interactive responsiveness.

| Subscription           | Description                                | Triggered by                         |
|------------------------|--------------------------------------------|------------------------------------|
| `chatCompletion`       | Streams LLM response tokens to clients    | User prompts a Playground query    |

**Sources:** [src/phoenix/server/api/schema.py:14-17](), [src/phoenix/server/app.py:53-55](), [app/schema.graphql:1-30]()

---

## DataLoader Architecture

Phoenix uses the DataLoader pattern extensively to solve the N+1 query problem and achieve efficient batched data fetching. DataLoaders batch load requests per GraphQL request scope, reducing the total number of database queries.

### DataLoader Initialization and Role

- A `DataLoaders` dataclass bundles all DataLoader instances ([src/phoenix/server/api/context.py:120-173]()).
- A per-request context includes DataLoaders, a reference to the database session factory, and user info.
- Resolvers access DataLoaders via `info.context.data_loaders`.

### DataLoader Pattern Diagram

```mermaid
graph TB
    Context["Context"]
    DataLoaders["DataLoaders"]

    TableFieldsLoader["TableFieldsDataLoader"]
    SpanAnnotationsLoader["SpanAnnotationsDataLoader"]
    TokenCountLoader["TokenCountDataLoader"]
    CostSummaryLoader["SpanCostSummaryByProjectDataLoader"]

    Cache["CacheForDataLoaders"]

    Context --> DataLoaders

    DataLoaders --> TableFieldsLoader
    DataLoaders --> SpanAnnotationsLoader
    DataLoaders --> TokenCountLoader
    DataLoaders --> CostSummaryLoader

    DataLoaders --> Cache

    TableFieldsLoader -.->|"Batch field loads"| Database[(DB)]
    SpanAnnotationsLoader -.->|"Batch annotation queries"| Database
    TokenCountLoader -.->|"Batch token aggregations"| Database
    CostSummaryLoader -.->|"Batch cost summaries"| Database
```

### DataLoader Categories

| Category          | DataLoaders                                                           | Purpose                                      |
|-------------------|----------------------------------------------------------------------|----------------------------------------------|
| Field Loaders     | `TableFieldsDataLoader`                                               | Batch load specific table columns            |
| Relationship Loaders | `SpanAnnotationsDataLoader`, `TraceRootSpansDataLoader`            | Batch load related child or parent objects   |
| Aggregation Loaders | `TokenCountDataLoader`, `RecordCountDataLoader`                      | Batch compute aggregate counts and sums      |
| Cost Loaders      | `SpanCostSummaryByProjectDataLoader`, `SpanCostBySpanDataLoader`     | Calculate LLM span cost summaries             |

Example: `TableFieldsDataLoader` batches requests for multiple row IDs and columns into one complex database query.

### Cache-Backed DataLoaders

Several DataLoaders include internal request-scoped caches to avoid duplicate database hits in the same request:

| DataLoader                 | Purpose                                           |
|----------------------------|--------------------------------------------------|
| `RecordCountDataLoader`    | Cache span/trace counts by project/time range    |
| `TokenCountDataLoader`     | Cache token counts for spans and prompts          |
| `LatencyMsQuantileDataLoader` | Cache latency percentile data                   |
| `SpanCostSummaryByProjectDataLoader` | Cache summarized LLM cost data             |

**Sources:** [src/phoenix/server/api/context.py:120-173](), [src/phoenix/server/api/dataloaders/__init__.py:1-106]()

---

## GraphQL Router Integration

The GraphQL API is exposed as a FastAPI router created by Strawberry’s `GraphQLRouter` in [src/phoenix/server/app.py:53-55]().

### Router Setup

- The router uses the schema built with `build_graphql_schema()` ([src/phoenix/server/api/schema.py:33-58]()).
- A custom request context factory injects per-request DataLoaders, database sessions, and user authentication info.
- The WebSocket subscription protocol `graphql-transport-ws` is enabled on the router.

### Authentication Workflow

- Authentication for GraphQL requests integrates with the Bearer token backend ([src/phoenix/server/app.py:183-183]()).
- For HTTP requests, the `Authorization` header bearer token is used.
- For WebSocket connections, the token is passed in connection parameters.
- The currently authenticated user is accessible in resolvers via `info.context.user_id`.

### Router Interaction Diagram

```mermaid
graph TB
    Client["GraphQL Client"]

    HTTP["HTTP Request"]
    WebSocket["WebSocket Connection"]

    GraphQLRouter["GraphQLRouter<br/>(strawberry)"]

    ContextFactory["Request Context Factory"]
    Schema["Strawberry Schema"]
    SubscriptionProtocol["graphql-transport-ws Protocol"]

    Database["Database (SQLAlchemy)"]
    DataLoaders["DataLoaders"]
    AuthBackend["BearerTokenAuthBackend"]

    Client --> HTTP
    Client --> WebSocket

    HTTP --> GraphQLRouter
    WebSocket --> GraphQLRouter

    GraphQLRouter --> ContextFactory
    GraphQLRouter --> Schema
    GraphQLRouter --> SubscriptionProtocol

    ContextFactory --> Database
    ContextFactory --> DataLoaders
    ContextFactory --> AuthBackend
```

**Sources:** [src/phoenix/server/app.py:53-55](), [src/phoenix/server/api/schema.py:33-58](), [src/phoenix/server/api/context.py:120-173](), [src/phoenix/server/bearer_auth.py:183-183]()

---

## Type Resolver Patterns

### Database Record Caching

Many types store a private `db_record` (an SQLAlchemy ORM instance) to:

- Provide immediate synchronous access to fields without additional queries if already loaded.
- Avoid repeated database requests when fields are accessed multiple times.
- Fall back to async DataLoader batch requests when `db_record` is absent.

Example from `Span` resolver:

```python
@strawberry.field
async def name(self, info: Info[Context, None]) -> str:
    if self.db_record:
        return self.db_record.name
    value = await info.context.data_loaders.span_fields.load((self.id, models.Span.name))
    return str(value)
```

### Relay Connection Pagination

Connection types encapsulate paginated results. Helper functions construct connection responses from entity lists or DB cursors:

- `connection_from_list(data, args)` builds edges and pageInfo.
- Cursor strings are opaque base64 encoded strings encoding position markers.

This pattern applies to collections like projects, datasets, experiments, spans, etc.

---

## Error Handling

- GraphQL errors in production are masked by a custom schema extension to avoid leaking internal details ([src/phoenix/server/api/schema.py:42-42]()).
- Specific exceptions raised by resolvers (e.g., `BadRequest`, `NotFound`, `Unauthorized`) are user-visible and map to GraphQL errors with meaningful messages.
- Mutation conflicts and validation failures produce appropriate user errors visible in GraphQL responses.

| Error Type      | Visible to User | Description                             |
|-----------------|-----------------|-------------------------------------|
| `BadRequest`    | Yes             | Input validation errors              |
| `NotFound`      | Yes             | Requested resource not found        |
| `Unauthorized`  | Yes             | Authentication or authorization failure |
| `Conflict`      | Yes             | Resource version conflicts           |
| Others          | Masked          | Internal or unexpected errors       |

---

# Diagrams Bridging Natural Language and Code Entity Space

### Diagram 1: Query Flow from Client to DataLoaders

```mermaid
graph TD
    Client["GraphQL Client<br/>(e.g., Phoenix Web UI, Python Clients)"]
    GraphQLRouter["GraphQLRouter<br/>(src/phoenix/server/app.py:53-55)"]
    Context["Request Context<br/>(src/phoenix/server/api/context.py)"]
    QueryRoot["Query class<br/>(src/phoenix/server/api/queries.py)"]
    DataLoaderSet["DataLoaders<br/>(src/phoenix/server/api/context.py:120-173)"]
    DB["Database<br/>(PostgreSQL/SQLite)"]
    
    Client -->|HTTP or WebSocket| GraphQLRouter
    GraphQLRouter -->|Instantiates| Context
    Context --> QueryRoot
    QueryRoot -->|Calls with info.context.data_loaders| DataLoaderSet
    DataLoaderSet -->|Batch queries| DB
```

### Diagram 2: Mutation Execution and DML Event Propagation

```mermaid
graph TD
    Client["GraphQL Client"]
    GraphQLRouter["GraphQLRouter<br/>(src/phoenix/server/app.py:53-55)"]
    MutationRoot["Mutation class<br/>(src/phoenix/server/api/mutations)"]
    Context["Context object<br/>(src/phoenix/server/api/context.py)"]
    DbSession["Async DB Session<br/>(SQLAlchemy)"]
    DmlEventQueue["DML Event Queue<br/>(phoenix.server.api.mutations)"]
    CacheInvalidator["Cache & Subscription Notifier"]
    
    Client -->|mutation request| GraphQLRouter
    GraphQLRouter --> MutationRoot
    MutationRoot --> Context
    Context --> DbSession
    MutationRoot --> DmlEventQueue
    DmlEventQueue --> CacheInvalidator
```

---

# Summary

The Phoenix GraphQL API is a carefully designed system built on Strawberry GraphQL that enforces type safety and efficient data operations. Its key strengths include:

- Relay-compliant global IDs and cursor-based pagination
- Rich domain type models with caching of loaded database records
- A comprehensive set of queries, mutations, and subscriptions
- Extensive use of DataLoaders for batching and caching DB access
- Secure and robust error handling and authentication integration
- FastAPI integration for serving HTTP and WebSocket GraphQL traffic

This architecture provides a scalable and extensible foundation for Phoenix’s AI observability platform to serve both UI and programmatic clients.

---

**Sources:**  
[src/phoenix/server/api/schema.py:33-58](), [src/phoenix/server/api/queries.py:1-160](), [src/phoenix/server/api/types/Span.py:127-146](), [src/phoenix/server/api/context.py:120-173](), [src/phoenix/server/api/dataloaders/__init__.py:1-106](), [src/phoenix/server/app.py:53-55](), [app/schema.graphql:1-320](), [src/phoenix/server/api/mutations/dataset_mutations.py:25-55]()

---

# Page: REST API & OpenAPI

# REST API & OpenAPI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/api/__generated__/v1.ts](app/src/api/__generated__/v1.ts)
- [app/src/pages/playground/__tests__/playgroundAgentContextUtils.test.ts](app/src/pages/playground/__tests__/playgroundAgentContextUtils.test.ts)
- [app/src/pages/playground/playgroundAgentContextUtils.ts](app/src/pages/playground/playgroundAgentContextUtils.ts)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx)
- [js/packages/phoenix-client/src/__generated__/api/v1.ts](js/packages/phoenix-client/src/__generated__/api/v1.ts)
- [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py](packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py)
- [packages/phoenix-client/src/phoenix/client/resources/projects/__init__.py](packages/phoenix-client/src/phoenix/client/resources/projects/__init__.py)
- [packages/phoenix-client/src/phoenix/client/utils/encode_path_param.py](packages/phoenix-client/src/phoenix/client/utils/encode_path_param.py)
- [packages/phoenix-client/tests/canary/sdk/anthropic/test_messages.py](packages/phoenix-client/tests/canary/sdk/anthropic/test_messages.py)
- [packages/phoenix-client/tests/canary/sdk/openai/test_chat.py](packages/phoenix-client/tests/canary/sdk/openai/test_chat.py)
- [schemas/openapi.json](schemas/openapi.json)
- [src/phoenix/db/insertion/dataset.py](src/phoenix/db/insertion/dataset.py)
- [src/phoenix/server/agents/context.py](src/phoenix/server/agents/context.py)
- [src/phoenix/server/agents/prompts/context/PLAYGROUND_CONTEXT_INSTRUCTIONS.xml.j2](src/phoenix/server/agents/prompts/context/PLAYGROUND_CONTEXT_INSTRUCTIONS.xml.j2)
- [src/phoenix/server/agents/prompts/skills/playground/SKILL.md](src/phoenix/server/agents/prompts/skills/playground/SKILL.md)
- [src/phoenix/server/api/routers/agents.py](src/phoenix/server/api/routers/agents.py)
- [src/phoenix/server/api/routers/v1/__init__.py](src/phoenix/server/api/routers/v1/__init__.py)
- [src/phoenix/server/api/routers/v1/annotations.py](src/phoenix/server/api/routers/v1/annotations.py)
- [src/phoenix/server/api/routers/v1/datasets.py](src/phoenix/server/api/routers/v1/datasets.py)
- [src/phoenix/server/api/routers/v1/projects.py](src/phoenix/server/api/routers/v1/projects.py)
- [src/phoenix/server/api/routers/v1/spans.py](src/phoenix/server/api/routers/v1/spans.py)
- [src/phoenix/server/api/routers/v1/traces.py](src/phoenix/server/api/routers/v1/traces.py)
- [src/phoenix/server/api/routers/v1/utils.py](src/phoenix/server/api/routers/v1/utils.py)
- [src/phoenix/server/dml_event_handler.py](src/phoenix/server/dml_event_handler.py)
- [tests/integration/_helpers.py](tests/integration/_helpers.py)
- [tests/integration/auth/conftest.py](tests/integration/auth/conftest.py)
- [tests/integration/auth/test_auth.py](tests/integration/auth/test_auth.py)
- [tests/integration/client/conftest.py](tests/integration/client/conftest.py)
- [tests/integration/client/test_projects.py](tests/integration/client/test_projects.py)
- [tests/unit/db/insertion/test_dataset.py](tests/unit/db/insertion/test_dataset.py)
- [tests/unit/server/agents/capabilities/contexts/test_capabilities.py](tests/unit/server/agents/capabilities/contexts/test_capabilities.py)
- [tests/unit/server/api/routers/v1/test_annotations.py](tests/unit/server/api/routers/v1/test_annotations.py)
- [tests/unit/server/api/routers/v1/test_datasets.py](tests/unit/server/api/routers/v1/test_datasets.py)
- [tests/unit/server/api/routers/v1/test_projects.py](tests/unit/server/api/routers/v1/test_projects.py)
- [tests/unit/server/api/routers/v1/test_spans.py](tests/unit/server/api/routers/v1/test_spans.py)
- [tests/unit/server/api/routers/v1/test_traces.py](tests/unit/server/api/routers/v1/test_traces.py)

</details>



The Phoenix REST API provides HTTP endpoints for managing AI observability data including traces, spans, evaluations, datasets, experiments, and prompts. This document covers the v1 REST API implementation, the OpenAPI specification, and the automated client generation pipeline for Python and TypeScript.

## Architecture Overview

Phoenix utilizes [FastAPI](https://fastapi.tiangolo.com/) to implement its RESTful interface. The API is structured under the `/v1` prefix and is organized into functional routers.

### Request Flow and Data Transformation

1.  **Routing**: Incoming requests are handled by routers defined in `src/phoenix/server/api/routers/v1/` [src/phoenix/server/api/routers/v1/__init__.py:10-23]().
2.  **Validation**: Pydantic models (subclasses of `V1RoutesBaseModel`) validate request bodies and query parameters [src/phoenix/server/api/routers/v1/models.py:53-53]().
3.  **Authorization**: FastAPI dependencies check for authentication (Bearer tokens) and role-based permissions (e.g., `restrict_access_by_viewers`) [src/phoenix/server/api/routers/v1/__init__.py:33-46]().
4.  **Database Interaction**: Routers use SQLAlchemy to query or mutate the underlying database [src/phoenix/server/api/routers/v1/spans.py:159-164]().
5.  **Response Formatting**: Data is serialized into JSON using Pydantic schemas or streamed as CSV/Arrow for large datasets [src/phoenix/server/api/routers/v1/datasets.py:21-21]().

### API to Code Entity Mapping

This diagram maps REST resources to their primary implementation files and database models.

Title: REST API Code Mapping
```mermaid
graph TD
    subgraph "REST Endpoints"
        R_SPANS["/v1/spans"]
        R_TRACES["/v1/projects/{id}/traces"]
        R_DATASETS["/v1/datasets"]
        R_AGENTS["/agents"]
    end

    subgraph "FastAPI Routers"
        RT_SPANS["spans.py"]
        RT_TRACES["traces.py"]
        RT_DATASETS["datasets.py"]
        RT_AGENTS["agents.py"]
    end

    subgraph "SQLAlchemy Models"
        M_SPAN["models.Span"]
        M_TRACE["models.Trace"]
        M_DATASET["models.Dataset"]
    end

    R_SPANS --> RT_SPANS
    R_TRACES --> RT_TRACES
    R_DATASETS --> RT_DATASETS
    R_AGENTS --> RT_AGENTS

    RT_SPANS --> M_SPAN
    RT_TRACES --> M_TRACE
    RT_DATASETS --> M_DATASET
```
Sources: [src/phoenix/server/api/routers/v1/__init__.py:10-23](), [src/phoenix/server/api/routers/v1/spans.py:140-140](), [src/phoenix/server/api/routers/v1/traces.py:52-52](), [src/phoenix/server/api/routers/v1/datasets.py:77-77]().

## OpenAPI Specification

Phoenix maintains a comprehensive OpenAPI 3.1.0 specification located at `schemas/openapi.json` [schemas/openapi.json:1-6](). This schema is the "source of truth" for the API's structure, including:

*   **Operation IDs**: Unique identifiers for every endpoint (e.g., `list_annotation_configs_v1_annotation_configs_get`) [schemas/openapi.json:16-16]().
*   **Authentication**: Security schemes for Bearer Auth and API Keys.
*   **Schemas**: Detailed Pydantic-generated definitions for objects like `SpanQuery`, `Dataset`, and `Experiment` [src/phoenix/server/api/routers/v1/spans.py:143-150](), [src/phoenix/server/api/routers/v1/datasets.py:80-87]().

## Client Generation

Phoenix uses a code-generation pipeline to ensure that client libraries stay in sync with the server implementation.

### TypeScript Client Generation
The frontend and Node.js clients use `openapi-typescript` to generate type definitions from the JSON schema.
*   **Target File**: `js/packages/phoenix-client/src/__generated__/api/v1.ts` [js/packages/phoenix-client/src/__generated__/api/v1.ts:1-4]().
*   **Mechanism**: The generator creates an `interface paths` that maps URL patterns to their respective HTTP methods and response types [js/packages/phoenix-client/src/__generated__/api/v1.ts:6-27]().

### Python Client Generation
The Python client (`arize-phoenix-client`) contains generated `TypedDict` structures to provide type safety for API interactions.
*   **Target File**: `packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py` [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py:1-6]().
*   **Key Entities**: Classes like `Dataset`, `Experiment`, and `PromptVersionData` are generated to match the server-side Pydantic models [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py:105-113](), [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py:151-164]().

## Key API Subsystems

### Traces & Spans
The API provides advanced filtering for spans using a JSON-based query DSL (`SpanQuery`) and specialized attribute parsing [src/phoenix/server/api/routers/v1/spans.py:143-150]().
*   **Attribute Filtering**: Spans can be filtered by `key:value` pairs where keys are dot-paths (e.g., `llm.model_name`) [src/phoenix/server/api/routers/v1/spans.py:126-137]().
*   **OTLP Ingestion**: The API supports OTLP trace ingestion via `POST /v1/traces` [src/phoenix/server/api/routers/v1/traces.py:9-12]().

### Datasets & Experiments
Datasets are managed via `/v1/datasets`.
*   **Pagination**: Uses a cursor-based pagination system where the cursor is a base64-encoded GlobalID [src/phoenix/server/api/routers/v1/datasets.py:102-105]().
*   **Bulk Operations**: Supports bulk deletion of datasets and associated projects/traces [src/phoenix/server/api/routers/v1/datasets.py:192-202]().

### AI Agent Interface (PxI)
The `/agents` endpoint provides a Vercel AI-compatible streaming interface for the Phoenix Intelligence (PxI) assistant [src/phoenix/server/api/routers/agents.py:1-17]().
*   **Context Resolution**: Injects relevant observability data (spans, traces) into the agent's prompt context [src/phoenix/server/api/routers/agents.py:47-51]().
*   **Tool Execution**: Supports executing tools on both the server (e.g., database queries) and the client [src/phoenix/server/api/routers/agents.py:79-80]().

## Implementation Diagram

The following diagram illustrates the interaction between the API layer, the generated clients, and the database.

Title: REST API Data Flow
```mermaid
sequenceDiagram
    participant Client as "Python/TS Client"
    participant Router as "FastAPI Router (e.g. spans.py)"
    participant Auth as "Bearer Auth Dependency"
    participant DB as "SQLAlchemy (PostgreSQL/SQLite)"

    Client->>Router: GET /v1/projects/{id}/traces
    Router->>Auth: is_authenticated(token)
    Auth-->>Router: PhoenixUser
    Router->>DB: select(models.Trace).where(...)
    DB-->>Router: List[models.Trace]
    Router-->>Client: GetTracesResponseBody (JSON)
```
Sources: [src/phoenix/server/api/routers/v1/traces.py:122-158](), [src/phoenix/server/api/routers/v1/__init__.py:45-45](), [src/phoenix/server/bearer_auth.py:37-37]().

---

# Page: OTLP Ingestion & gRPC Server

# OTLP Ingestion & gRPC Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/api/__generated__/v1.ts](app/src/api/__generated__/v1.ts)
- [app/src/pages/playground/__tests__/playgroundAgentContextUtils.test.ts](app/src/pages/playground/__tests__/playgroundAgentContextUtils.test.ts)
- [app/src/pages/playground/playgroundAgentContextUtils.ts](app/src/pages/playground/playgroundAgentContextUtils.ts)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx)
- [js/packages/phoenix-client/src/__generated__/api/v1.ts](js/packages/phoenix-client/src/__generated__/api/v1.ts)
- [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py](packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py)
- [packages/phoenix-client/tests/canary/sdk/anthropic/test_messages.py](packages/phoenix-client/tests/canary/sdk/anthropic/test_messages.py)
- [packages/phoenix-client/tests/canary/sdk/openai/test_chat.py](packages/phoenix-client/tests/canary/sdk/openai/test_chat.py)
- [requirements/integration-tests.txt](requirements/integration-tests.txt)
- [schemas/openapi.json](schemas/openapi.json)
- [src/phoenix/db/bulk_inserter.py](src/phoenix/db/bulk_inserter.py)
- [src/phoenix/db/constants.py](src/phoenix/db/constants.py)
- [src/phoenix/db/insertion/span.py](src/phoenix/db/insertion/span.py)
- [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py](src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py)
- [src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py](src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py)
- [src/phoenix/db/types/trace_retention.py](src/phoenix/db/types/trace_retention.py)
- [src/phoenix/server/agents/context.py](src/phoenix/server/agents/context.py)
- [src/phoenix/server/agents/prompts/context/PLAYGROUND_CONTEXT_INSTRUCTIONS.xml.j2](src/phoenix/server/agents/prompts/context/PLAYGROUND_CONTEXT_INSTRUCTIONS.xml.j2)
- [src/phoenix/server/agents/prompts/skills/playground/SKILL.md](src/phoenix/server/agents/prompts/skills/playground/SKILL.md)
- [src/phoenix/server/api/routers/agents.py](src/phoenix/server/api/routers/agents.py)
- [src/phoenix/server/api/routers/v1/spans.py](src/phoenix/server/api/routers/v1/spans.py)
- [src/phoenix/server/api/routers/v1/traces.py](src/phoenix/server/api/routers/v1/traces.py)
- [src/phoenix/server/dml_event_handler.py](src/phoenix/server/dml_event_handler.py)
- [src/phoenix/server/grpc_server.py](src/phoenix/server/grpc_server.py)
- [src/phoenix/server/prometheus.py](src/phoenix/server/prometheus.py)
- [src/phoenix/server/retention.py](src/phoenix/server/retention.py)
- [tests/integration/_helpers.py](tests/integration/_helpers.py)
- [tests/integration/auth/conftest.py](tests/integration/auth/conftest.py)
- [tests/integration/auth/test_auth.py](tests/integration/auth/test_auth.py)
- [tests/integration/conftest.py](tests/integration/conftest.py)
- [tests/integration/db_migrations/__init__.py](tests/integration/db_migrations/__init__.py)
- [tests/integration/db_migrations/conftest.py](tests/integration/db_migrations/conftest.py)
- [tests/integration/db_migrations/test_data_migration_4ded9e43755f_create_project_sessions_table.py](tests/integration/db_migrations/test_data_migration_4ded9e43755f_create_project_sessions_table.py)
- [tests/integration/db_migrations/test_db_schema_6a88424799fe_update_users_with_auth_method.py](tests/integration/db_migrations/test_db_schema_6a88424799fe_update_users_with_auth_method.py)
- [tests/integration/db_migrations/test_db_schema_a20694b15f82_cost.py](tests/integration/db_migrations/test_db_schema_a20694b15f82_cost.py)
- [tests/integration/db_migrations/test_db_schema_for_annotations.py](tests/integration/db_migrations/test_db_schema_for_annotations.py)
- [tests/integration/db_migrations/test_up_and_down_migrations.py](tests/integration/db_migrations/test_up_and_down_migrations.py)
- [tests/integration/project_sessions/conftest.py](tests/integration/project_sessions/conftest.py)
- [tests/integration/project_sessions/test_project_sessions.py](tests/integration/project_sessions/test_project_sessions.py)
- [tests/integration/server/test_launch_app.py](tests/integration/server/test_launch_app.py)
- [tests/unit/db/types/test_trace_retention.py](tests/unit/db/types/test_trace_retention.py)
- [tests/unit/server/agents/capabilities/contexts/test_capabilities.py](tests/unit/server/agents/capabilities/contexts/test_capabilities.py)
- [tests/unit/server/api/routers/v1/test_spans.py](tests/unit/server/api/routers/v1/test_spans.py)
- [tests/unit/server/api/routers/v1/test_traces.py](tests/unit/server/api/routers/v1/test_traces.py)
- [tests/unit/server/test_retention.py](tests/unit/server/test_retention.py)

</details>



## Purpose and Scope

This document describes the mechanisms by which Phoenix ingests OpenTelemetry traces using the OpenTelemetry Protocol (OTLP) over both HTTP and gRPC. Phoenix acts as an OTLP-compatible collector, accepting binary protobuf-encoded trace data primarily via gRPC, decoding it into its internal span representation, and efficiently persisting it to the database. The page covers the implementation details, data flow, key classes and methods, and instrumentation for observability.

---

## Architecture Overview

Phoenix runs two servers in parallel:

- **HTTP Server**: Powered by FastAPI to handle the REST and GraphQL APIs (non-OTLP ingestion endpoints).
- **gRPC Server**: Dedicated to OTLP trace ingestion over the gRPC protocol, usually listening on port 4317, mimicking an OTLP collector endpoint.

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

- Located in `src/phoenix/server/grpc_server.py` (lines 55-123).
- It manages the gRPC server lifecycle as an async context manager.
- Supports both insecure and optional TLS-secured ports with flexible credential configurations.
- Instantiates the `Servicer` which implements OTLP service methods.

Sources: [src/phoenix/server/grpc_server.py:55-123](), [src/phoenix/db/bulk_inserter.py:51-88](), [src/phoenix/server/bearer_auth.py:13-40]()

---

## OTLP Protocol Support

Phoenix implements the OTLP trace export interface from the OpenTelemetry proto definitions (`opentelemetry.proto.collector.trace.v1.TraceService`).

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
        PhoenixSpan["Span (phoenix.trace.schemas.Span)"]
        ProjectName["ProjectName (str)"]
    end
    
    OTLPExporter -->|gRPC sends| ProtoReq
    ProtoReq --> DecodeOtlp
    ProtoReq --> ProjectNameUtil
    DecodeOtlp --> PhoenixSpan
    ProjectNameUtil --> ProjectName
```

### OTLP Export Method Processing Steps

- **Receiving Requests**: The gRPC `Export` method implemented in the `Servicer` class accepts `ExportTraceServiceRequest` objects.
- **Iteration over ResourceSpans**: For each `resource_spans` batch in the request, project attributes are inspected.
- **Project Resolution**: The target project is resolved via `get_project_name()` from resource attributes.
- **Span Decoding**: Each OTLP span is decoded into Phoenix’s internal `Span` data structure by calling the thread-pool executed `decode_otlp_span()` to avoid blocking the async event loop.
- **Span Enqueueing**: The decoded span along with its project name is delivered to the ingestion queue via the `_enqueue_span` callback.

Sources: [src/phoenix/server/grpc_server.py:33-52](), [src/phoenix/trace/otel.py:20-40](), [src/phoenix/utilities/project.py:20-30]()

---

## Request Processing Pipeline

Phoenix employs an asynchronous ingestion pipeline for spans, decoupling network-bound gRPC processing from database storage. This design supports high throughput and resilience under load.

### Span Enqueueing & Background Batch Insertions

1. **In-Memory Queueing**: Spans are appended to an in-memory `deque` (`_spans`) managed by the `BulkInserter`, ensuring immediate acceptance without blocking the exporter [src/phoenix/db/bulk_inserter.py:81-82, 121-123]().

2. **BulkInserter Background Task**: Runs the async `_bulk_insert()` loop:
   - Processes any queued database mutations and span insertions in batches (respecting `max_ops_per_transaction`).
   - Calls `_insert_spans()` to persist spans in the database with transaction isolation.
   - Emits DML events for further handling (e.g., annotations) asynchronously.
   - Sleeps briefly between batches to balance CPU and I/O.

3. **Span Insertion Logic**:
   - The `insert_span()` coroutine (from `src/phoenix/db/insertion/span.py`) handles insertion of individual spans, performs trace/project/session linkage, and updates cumulative error and token counts.
   - Handles project creation if the project does not exist upon new span arrival.

Sources: [src/phoenix/db/bulk_inserter.py:121-155](), [src/phoenix/db/insertion/span.py:20-164]()

---

## Capacity Management & Monitoring

To maintain stability and avoid memory exhaustion, Phoenix monitors span ingestion capacity and metrics:

- **Queue Capacity**: The `BulkInserter` exposes the `is_full` boolean indicating when the span queue length surpasses the configured maximum [src/phoenix/db/bulk_inserter.py:89-91]().

- **Prometheus Metrics**:
  - `phoenix_span_queue_size`: Current count of spans waiting in memory queue [src/phoenix/server/prometheus.py:110-114]().
  - `phoenix_span_queue_rejections_total`: Counts how often ingestion occurs when the queue is full to observe backpressure events [src/phoenix/server/prometheus.py:104-108]().
  - `phoenix_bulk_loader_last_activity_timestamp_seconds`: Timestamp for last ingestion batch activity [src/phoenix/server/prometheus.py:116-120]().
  - `phoenix_bulk_loader_span_exceptions_total`: Counts span insertion exceptions [src/phoenix/server/prometheus.py:47-51]().

This setup facilitates external observability for ingestion health, queue saturation, and error conditions for operational alerting.

Sources: [src/phoenix/db/bulk_inserter.py:89-91](), [src/phoenix/server/prometheus.py:40-120]()

---

## Authentication and Security

The gRPC server supports API key validation to secure ingestion endpoints:

- **API Key Interceptor**:
  - Implemented by `ApiKeyInterceptor` class in `src/phoenix/server/bearer_auth.py`.
  - Injected into the gRPC interceptor stack if a `token_store` is given at server initialization.
  - Intercepts all incoming gRPC calls to validate bearer tokens passed for authentication before forwarding to the servicer.

- **TLS Support**:
  - The server can optionally run with TLS (SSL) enabled.
  - Reads TLS settings and certificate/key files via environment variables to configure the `grpc.ssl_server_credentials`.
  - Supports passing client certificate authorities for client cert validation or using a broad `check_client_cert` flag.
  - If TLS is enabled, binds the server to the secured port, else uses plaintext.

This design allows deploying Phoenix in secured environments where unauthorized trace exports must be guarded.

Sources: [src/phoenix/server/grpc_server.py:75-109](), [src/phoenix/server/bearer_auth.py:10-40]()

---

## Summary of Key Classes and Methods

| Component / Class       | Role / Description                                                                                 | Location                                    |
|------------------------|--------------------------------------------------------------------------------------------------|---------------------------------------------|
| `GrpcServer`           | Manages the gRPC server lifecycle, setup, TLS, and interceptor injection                         | `src/phoenix/server/grpc_server.py:55-123` |
| `Servicer`             | Implements OTLP trace export `Export` method, decodes spans, enqueues them                        | `src/phoenix/server/grpc_server.py:23-65`  |
| `_enqueue_span` (BulkInserter) | Callback to append decoded spans to the in-memory queue                                      | `src/phoenix/db/bulk_inserter.py:121-123`  |
| `BulkInserter`          | Background bulk insertion management, batching spans & database operations                       | `src/phoenix/db/bulk_inserter.py:51-183`   |
| `insert_span()`         | Inserts a single decoded span internally linking to trace, project, sessions                     | `src/phoenix/db/insertion/span.py:20-164`  |
| `ApiKeyInterceptor`     | gRPC interceptor for validating API keys on incoming requests                                   | `src/phoenix/server/bearer_auth.py`         |
| `decode_otlp_span()`    | Converts OTLP spans into Phoenix internal span schema                                           | `src/phoenix/trace/otel.py`                   |
| `get_project_name()`    | Extracts project_name attribute from OTLP resource spans for span routing                       | `src/phoenix/utilities/project.py`            |

---

# Additional Diagrams

### OTLP Ingestion Pipeline: Natural Language to Code Entities

```mermaid
graph TB
    subgraph "OTLP Trace Export"
        OTLPRequest["ExportTraceServiceRequest (protobuf)"]
        OTLPSpan["OTLP Span (protobuf)"]
    end
    
    subgraph "Phoenix Server - gRPC Layer"
        Servicer["Servicer.Export()"]
        Decode["decode_otlp_span()"]
        ProjectName["get_project_name()"]
    end
    
    subgraph "Phoenix Server - Ingestion Pipeline"
        BulkInserter["BulkInserter"]
        EnqueueSpan["_enqueue_span()"]
        SpanQueue["_spans deque"]
    end
    
    subgraph "Storage Layer"
        Database["PostgreSQL / SQLite"]
        InsertSpan["insert_span()"]
    end

    OTLPRequest -->|contains| OTLPSpan
    OTLPSpan --> Servicer
    Servicer --> Decode
    Servicer --> ProjectName
    Decode --> BulkInserter
    ProjectName --> BulkInserter
    BulkInserter --> EnqueueSpan
    EnqueueSpan --> SpanQueue
    SpanQueue --> InsertSpan
    InsertSpan --> Database
```

### gRPC Server Security and Startup

```mermaid
graph LR
    EnvVars["Environment variables (TLS, cert paths, etc.)"]
    GrpcServer["GrpcServer"]
    ApiKeyInterceptor["ApiKeyInterceptor (optional)"]
    TLSCreds["grpc.ssl_server_credentials (optional)"]
    gRPCServer["grpc.aio.Server"]

    EnvVars --> GrpcServer
    GrpcServer --> TLSCreds
    GrpcServer --> ApiKeyInterceptor
    GrpcServer --> gRPCServer
    ApiKeyInterceptor --> gRPCServer
    TLSCreds --> gRPCServer
```

---

# References and Sources

- `src/phoenix/server/grpc_server.py:23-123` (GrpcServer and Servicer implementation)
- `src/phoenix/db/bulk_inserter.py:51-183` (BulkInserter and enqueue logic)
- `src/phoenix/db/insertion/span.py:20-164` (insert_span insertion logic)
- `src/phoenix/server/bearer_auth.py` (ApiKeyInterceptor)
- `src/phoenix/trace/otel.py` (decode_otlp_span function)
- `src/phoenix/utilities/project.py` (get_project_name function)
- `src/phoenix/server/prometheus.py:40-120` (Prometheus metrics for ingestion)

This completes the detailed technical documentation for Phoenix's OTLP Ingestion & gRPC Server subsystem.

---

# Page: Database Layer & Migrations

# Database Layer & Migrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [requirements/integration-tests.txt](requirements/integration-tests.txt)
- [scripts/ddl/generate_ddl_postgresql.py](scripts/ddl/generate_ddl_postgresql.py)
- [scripts/ddl/postgresql_schema.sql](scripts/ddl/postgresql_schema.sql)
- [src/phoenix/db/alembic.ini](src/phoenix/db/alembic.ini)
- [src/phoenix/db/engines.py](src/phoenix/db/engines.py)
- [src/phoenix/db/insertion/span.py](src/phoenix/db/insertion/span.py)
- [src/phoenix/db/migrate.py](src/phoenix/db/migrate.py)
- [src/phoenix/db/migrations/__init__.py](src/phoenix/db/migrations/__init__.py)
- [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py](src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py)
- [src/phoenix/db/migrations/env.py](src/phoenix/db/migrations/env.py)
- [src/phoenix/db/migrations/versions/01a8342c9cdf_add_user_id_on_datasets.py](src/phoenix/db/migrations/versions/01a8342c9cdf_add_user_id_on_datasets.py)
- [src/phoenix/db/migrations/versions/0df286449799_add_session_annotations_table.py](src/phoenix/db/migrations/versions/0df286449799_add_session_annotations_table.py)
- [src/phoenix/db/migrations/versions/10460e46d750_datasets.py](src/phoenix/db/migrations/versions/10460e46d750_datasets.py)
- [src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py](src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py)
- [src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py](src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py)
- [src/phoenix/db/migrations/versions/58228d933c91_dataset_labels.py](src/phoenix/db/migrations/versions/58228d933c91_dataset_labels.py)
- [src/phoenix/db/migrations/versions/699f655af132_experiment_tags.py](src/phoenix/db/migrations/versions/699f655af132_experiment_tags.py)
- [src/phoenix/db/migrations/versions/ab513d89518b_add_user_id_on_dataset_versions.py](src/phoenix/db/migrations/versions/ab513d89518b_add_user_id_on_dataset_versions.py)
- [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py](src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py)
- [src/phoenix/db/migrations/versions/d0690a79ea51_users_on_experiments.py](src/phoenix/db/migrations/versions/d0690a79ea51_users_on_experiments.py)
- [src/phoenix/db/migrations/versions/deb2c81c0bb2_dataset_splits.py](src/phoenix/db/migrations/versions/deb2c81c0bb2_dataset_splits.py)
- [src/phoenix/db/models.py](src/phoenix/db/models.py)
- [src/phoenix/server/api/dataloaders/dataset_example_splits.py](src/phoenix/server/api/dataloaders/dataset_example_splits.py)
- [src/phoenix/server/api/helpers/playground_users.py](src/phoenix/server/api/helpers/playground_users.py)
- [src/phoenix/server/api/mutations/dataset_split_mutations.py](src/phoenix/server/api/mutations/dataset_split_mutations.py)
- [src/phoenix/server/api/routers/v1/experiment_evaluations.py](src/phoenix/server/api/routers/v1/experiment_evaluations.py)
- [src/phoenix/server/api/routers/v1/experiment_runs.py](src/phoenix/server/api/routers/v1/experiment_runs.py)
- [src/phoenix/server/api/routers/v1/experiments.py](src/phoenix/server/api/routers/v1/experiments.py)
- [src/phoenix/settings.py](src/phoenix/settings.py)
- [tests/integration/conftest.py](tests/integration/conftest.py)
- [tests/integration/db_migrations/__init__.py](tests/integration/db_migrations/__init__.py)
- [tests/integration/db_migrations/conftest.py](tests/integration/db_migrations/conftest.py)
- [tests/integration/db_migrations/test_data_migration_4ded9e43755f_create_project_sessions_table.py](tests/integration/db_migrations/test_data_migration_4ded9e43755f_create_project_sessions_table.py)
- [tests/integration/db_migrations/test_db_schema_6a88424799fe_update_users_with_auth_method.py](tests/integration/db_migrations/test_db_schema_6a88424799fe_update_users_with_auth_method.py)
- [tests/integration/db_migrations/test_db_schema_a20694b15f82_cost.py](tests/integration/db_migrations/test_db_schema_a20694b15f82_cost.py)
- [tests/integration/db_migrations/test_db_schema_for_annotations.py](tests/integration/db_migrations/test_db_schema_for_annotations.py)
- [tests/integration/db_migrations/test_up_and_down_migrations.py](tests/integration/db_migrations/test_up_and_down_migrations.py)
- [tests/integration/project_sessions/conftest.py](tests/integration/project_sessions/conftest.py)
- [tests/integration/project_sessions/test_project_sessions.py](tests/integration/project_sessions/test_project_sessions.py)
- [tests/integration/server/test_launch_app.py](tests/integration/server/test_launch_app.py)
- [tests/unit/db/test_helpers.py](tests/unit/db/test_helpers.py)
- [tests/unit/server/api/routers/v1/test_experiments.py](tests/unit/server/api/routers/v1/test_experiments.py)

</details>



This page documents the database layer architecture, SQLAlchemy ORM models, schema management, and Alembic migration system. It covers the data persistence layer that stores traces, spans, projects, datasets, experiments, and all other Phoenix entities.

For information about data ingestion and bulk insertion, see [OTLP Ingestion & gRPC Server](2.4).

## Overview

Phoenix uses SQLAlchemy 2.0+ with async support for database operations. The database layer provides:

- **ORM Models**: Declarative models for all entities (projects, traces, spans, datasets, experiments, etc.) [src/phoenix/db/models.py:602-1590]().
- **Dual Database Support**: SQLite for development/dev, PostgreSQL for production.
- **Type Safety**: Custom `TypeDecorator`s for JSON, timestamps, identifiers, and domain types [src/phoenix/db/models.py:210-559]().
- **Schema Migrations**: Alembic-based migration system for schema evolution [src/phoenix/db/migrate.py:37-70]().
- **Async Operations**: Full async/await support with `AsyncEngine` and `AsyncSession` [src/phoenix/db/models.py:39-48]().

The database layer strives for backend dialect agnosticism, with tailored code paths and type handling to achieve compatibility for both SQLite and PostgreSQL.

**Sources:** [src/phoenix/db/models.py:1-600](), [src/phoenix/db/migrate.py:37-70]()

---

## Database Architecture

Phoenix structures its database interactions in layered components:

```mermaid
graph TB
    subgraph "Application Layer"
        API["GraphQL API"]
        REST["REST API Routers<br/>src/phoenix/server/api/routers/v1"]
        Insertion["Insertion Layer<br/>src/phoenix/db/insertion/span.py"]
    end
    
    subgraph "Database Layer"
        Session["AsyncSession<br/>SQLAlchemy"]
        Models["ORM Models<br/>src/phoenix/db/models.py"]
        Helpers["insert_on_conflict()<br/>src/phoenix/db/insertion/helpers.py"]
    end
    
    subgraph "Engine Layer"
        AsyncEngine["AsyncEngine<br/>SQLAlchemy"]
        SQLiteEngine["aiosqlite"]
        PostgresEngine["asyncpg"]
    end
    
    subgraph "Migration System"
        Alembic["Alembic Engine"]
        MigrateFunc["migrate()<br/>src/phoenix/db/migrate.py"]
        Versions["Migration Versions<br/>src/phoenix/db/migrations/versions/"]
    end
    
    subgraph "Physical Storage"
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

- The **REST API** and **GraphQL API** layers interact with the async SQLAlchemy `AsyncSession` for database transactions.
- The **Insertion Layer** contains optimized logic for safe, idempotent span insertion with conflict handling.
- The **ORM Models** declare all entities and relationships, used by the session.
- The **Engine Layer** abstracts actual DB implementation with drivers: `aiosqlite` for SQLite and `asyncpg` for PostgreSQL.
- The **Migration System** uses Alembic, invoked on startup to apply pending migrations.
- Physical storage is either a local file for SQLite or a remote PostgreSQL server.

**Sources:** [src/phoenix/db/insertion/span.py:25-30](), [src/phoenix/db/migrate.py:37-70](), [src/phoenix/db/models.py:39-48](), [src/phoenix/server/api/routers/v1/experiments.py:160-161]()

---

## Database Support

Phoenix supports two relational database backends configured via connection string:

| Dialect   | Driver         | Use Case                              |
|-----------|----------------|-------------------------------------|
| SQLite    | `aiosqlite`    | Development, single-node, notebooks |
| PostgreSQL| `asyncpg`      | Production, high-concurrency         |

### PostgreSQL Specifics
- Supports schemas via `get_env_database_schema()`, enabling namespace separation in multi-tenant deployments [src/phoenix/db/models.py:55]().
- Uses native JSONB type for efficient JSON operations and indexing [src/phoenix/db/models.py:189-202]().
- Supports concurrent index creation during migrations, controlled by environment variables in tests [tests/integration/db_migrations/test_up_and_down_migrations.py:57-60]().

### SQLite Specifics
- Implements a workaround for SQLite's `VALUES` clause rendering for multi-row inserts using `UNION ALL` via custom compiled classes `SubValues` and overrides [src/phoenix/db/models.py:123-169]().
- Maps JSONB to JSON and overrides dialect behavior for compatibility [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:23-26]().
- SQLite pragmas optimized at connection for foreign keys, WAL mode, and performance tuning [src/phoenix/db/engines.py:37-45]().

**Sources:** [src/phoenix/db/models.py:123-169](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:23-26](), [src/phoenix/db/engines.py:37-45]()

---

## SQLAlchemy ORM Models

### Core Entity Relationships

The major entities with relationships are:

```mermaid
erDiagram
    "models.Project" ||--o{ "models.Trace" : "contains"
    "models.Project" ||--o{ "models.Dataset" : "owns"
    "models.Trace" ||--o{ "models.Span" : "composed_of"
    "models.Trace" }o--|| "models.ProjectSession" : "belongs_to"
    "models.Span" ||--o{ "models.SpanAnnotation" : "has"
    "models.Dataset" ||--o{ "models.DatasetVersion" : "versioned"
    "models.Dataset" ||--o{ "models.DatasetExample" : "contains"
    "models.Dataset" ||--o{ "models.Experiment" : "basis_for"
    "models.Experiment" ||--o{ "models.ExperimentRun" : "generates"
    "models.ExperimentRun" }o--|| "models.DatasetExample" : "evaluates"
    "models.ExperimentRun" ||--o{ "models.ExperimentRunAnnotation" : "annotated_by"
    
    "models.Project" {
        int id PK
        string name UK
        timestamp created_at
    }
    
    "models.Trace" {
        int id PK
        int project_rowid FK
        string trace_id UK
        timestamp start_time
    }
    
    "models.Span" {
        int id PK
        int trace_rowid FK
        string span_id UK
        jsonb attributes
        int cumulative_error_count
    }
    
    "models.ExperimentRun" {
        int id PK
        int experiment_id FK
        int dataset_example_id FK
        jsonb output
        string error
    }
```

- `Project`: Top-level organizational unit; owns traces and datasets.
- `Trace`: Groups spans representing a full execution flow; belongs to a project and optionally a project session.
- `Span`: Unit of work within a trace; stores OTel attributes and status, with cumulative aggregation fields.
- `ProjectSession`: Represents an application-level session grouping traces.
- `Dataset`, `DatasetVersion`, `DatasetExample`: Entities representing evaluation data with version control.
- `Experiment`: Represents a systematic set of runs on a dataset version.
- `ExperimentRun`: Individual execution in an experiment linked to an example.
- `ExperimentRunAnnotation`: Stores evaluation results (labels, scores) annotated on experiment runs.

**Sources:** [src/phoenix/db/models.py:602-1590](), [scripts/ddl/postgresql_schema.sql:9-250](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:48-220]()

---

### Key Model Classes

| Model Class              | Table Name                 | Primary Purpose                                                       |
|--------------------------|----------------------------|---------------------------------------------------------------------|
| `Project`                | `projects`                 | Organizational grouping for tracing and evaluations [DDL:63-80]()   |
| `Trace`                  | `traces`                   | Aggregate of spans forming a trace [migration init:80-93]()         |
| `Span`                   | `spans`                    | Individual trace unit storing attributes and status [migration init:95-126]() |
| `ProjectSession`         | `project_sessions`         | Application session grouping traces [DDL:115-135]()                 |
| `Dataset`                | `datasets`                 | Versioned data collection for experiments [datasets migration:49-68]() |
| `Experiment`             | `experiments`              | Stores experiment metadata and setup [datasets migration:153-199]()|
| `ExperimentRun`          | `experiment_runs`          | Records results of experiment executions [datasets migration:201-246]() |
| `ExperimentRunAnnotation`| `experiment_run_annotations` | Evaluation results on experiment runs [API:78-126]()               |

**Sources:** [src/phoenix/db/models.py:602-1560](), [scripts/ddl/postgresql_schema.sql:55-120](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:80-126]()

---

## Custom Type Decorators

Phoenix enhances SQLAlchemy with custom types to improve serialization, timezone handling, and domain-specific validation:

| TypeDecorator           | Purpose & Behavior                                                                                      |
|------------------------|-------------------------------------------------------------------------------------------------------|
| `JsonDict`              | Serializes Python dictionaries to JSON automatically, ensures non-null with default empty dict [210-222]() |
| `UtcTimeStamp`          | Normalizes datetime values to UTC, enforces timezone-aware timestamp storage [241-255]()              |
| `PromptTemplate`        | Validates and serializes structured prompt templates safely [397-414]()                               |

These decorators integrate seamlessly into models to enforce data integrity and representation consistency across database backends.

**Sources:** [src/phoenix/db/models.py:210-414]()

---

## Migration System

Phoenix employs Alembic for managing schema migrations to evolve the database safely and transparently.

### Alembic Integration

- The `migrate()` function programmatically runs database migrations during server startup.
- It loads Alembic config from `alembic.ini` and migration scripts directory.
- Runs `alembic upgrade head` asynchronously on provided engine.
- Supports running in separate thread (`migrate_in_thread`) for environments like notebooks where main thread async migrations are problematic.

```mermaid
flowchart TD
    Start["Application Startup"]
    MigrateFunc["migrate(engine, log_migrations)"]
    Alembic["Alembic Migration Engine<br/>from alembic.command"]
    Scripts["Migration Version Scripts<br/>src/phoenix/db/migrations/versions"]
    DB["Database<br/>(SQLite or PostgreSQL)"]

    Start --> MigrateFunc --> Alembic --> Scripts --> DB
```

### Migration Evolution Highlights

- **Initial migration `cf03bd6bae1d_init.py`**: Creates foundational observability schema tables—Projects, Traces, Spans, Annotations [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:48-220]().
- **Datasets and Experiments `10460e46d750_datasets.py`**: Adds evaluation framework tables (Datasets, DatasetVersions, DatasetExamples, Experiments, ExperimentRuns) [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:48-245]().
- **Project Sessions table migration**: Adds project_sessions table to group traces by application session.

**Sources:** [src/phoenix/db/migrate.py:37-101](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:1-220](), [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:1-245]()

---

## Insertion Logic & Helpers

Insertion operations leverage async SQLAlchemy sessions with conflict handling to ensure data integrity during concurrent writes.

### Span Insertion Flow

The key function `insert_span` ([src/phoenix/db/insertion/span.py:25-168]()):

1. **Trace resolution**:
   - Finds existing `Trace` by `trace_id`.
   - Expands `start_time`/`end_time` on the `Trace` to include new span times.
   - Creates `Project` if not existing, links `Trace` accordingly.
2. **ProjectSession management**:
   - Retrieves `session_id` from span attributes.
   - Retrieves or creates a `ProjectSession` record.
   - Updates session start/end times if needed.
3. **Cumulative metrics**:
   - Aggregates cumulative error counts and LLM token counts across child spans recursively.
4. **Span insertion**:
   - Inserts or ignores conflicting rows on duplicate `span_id`.
5. **Propagates aggregates up to parent spans** for maintaining cumulative metrics integrity.

### Experiment Run Upsert

The REST API for `create_experiment_run` uses `insert_on_conflict` with `DO_UPDATE` for allowing safe retry of failed runs but preventing overwriting of successful runs:

- Checks existing experiment run by unique keys.
- Rejects if a successful run exists.
- Otherwise, inserts or updates run record with new data and error state.
- Returns GlobalID for the experiment run resource.

This logic ensures idempotent safe insertion of experiment runs and annotator results.

**Sources:** [src/phoenix/db/insertion/span.py:25-168](), [src/phoenix/server/api/routers/v1/experiment_runs.py:113-146]()

---

## Summary

- Phoenix uses SQLAlchemy ORM models extensively for mapping domain entities to relational schema.
- The database layer supports PostgreSQL and SQLite with dialect-specific adaptations.
- Alembic migrations control schema versioning and are applied automatically at runtime.
- Custom SQLAlchemy types maintain type safety and serialization consistency.
- Insertions use conflict handling to support high-throughput, idempotent writes, especially for spans.
- The schema covers observability, evaluation, experiments, and annotations as first-class database entities.

This cohesive design enables Phoenix to manage complex data workflows reliably with a well-structured persistence layer.

---

# Appendix: Natural Language to Code Entity Associations

Below diagrams illustrate how natural language concepts map to key code entities.

### From Natural Language Concepts to Database Layer Components

```mermaid
flowchart LR
    NL_Project["Project (Organization)"]
    NL_Trace["Trace (Execution Flow)"]
    NL_Span["Span (Work Unit)"]
    NL_Dataset["Dataset (Versioned Data)"]
    NL_Experiment["Experiment (Task Runs)"]
    NL_Migrations["Database Migrations"]

    DB_Project["models.Project<br/>ORM"]
    DB_Trace["models.Trace  <br/>ORM"]
    DB_Span["models.Span  <br/>ORM"]
    DB_Dataset["models.Dataset, DatasetVersion<br/>ORM"]
    DB_Experiment["models.Experiment, ExperimentRun<br/>ORM"]
    DB_Alembic["Alembic (Migration Tool)"]

    NL_Project --> DB_Project
    NL_Trace --> DB_Trace
    NL_Span --> DB_Span
    NL_Dataset --> DB_Dataset
    NL_Experiment --> DB_Experiment
    NL_Migrations --> DB_Alembic
```

### From Phoenix System Names to Database Code Artifacts

```mermaid
flowchart TB
    API_REST["REST API<br/>src/phoenix/server/api/routers/v1/experiments.py"]
    API_GRPC["OTLP Ingestion gRPC<br/>src/phoenix/server/api/routers/v1/events.py"]
    ORM_Model["ORM Models<br/>src/phoenix/db/models.py"]
    Insert_Span["insert_span()<br/>src/phoenix/db/insertion/span.py"]
    Migration["migrate()<br/>src/phoenix/db/migrate.py"]
    Alembic_Versions["Alembic Versions<br/>src/phoenix/db/migrations/versions"]

    API_REST --> ORM_Model
    API_REST --> Insert_Span
    API_GRPC --> Insert_Span
    Insert_Span --> ORM_Model
    Migration --> Alembic_Versions
    Alembic_Versions --> ORM_Model
```

---

This concludes the documentation of Phoenix's database layer and migrations system.

**Sources:**

- [src/phoenix/db/models.py:1-600]()
- [src/phoenix/db/migrate.py:37-101]()
- [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:1-220]()
- [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:1-245]()
- [src/phoenix/db/insertion/span.py:25-168]()
- [src/phoenix/db/engines.py:37-45]()
- [tests/integration/db_migrations/test_up_and_down_migrations.py:57-60]()
- [src/phoenix/server/api/routers/v1/experiment_runs.py:113-146]()
- [src/phoenix/server/api/routers/v1/experiments.py:160-161]()

---

# Page: Authentication & Authorization

# Authentication & Authorization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal_docs/specs/oauth2-email-attribute-path.md](internal_docs/specs/oauth2-email-attribute-path.md)
- [src/phoenix/auth.py](src/phoenix/auth.py)
- [src/phoenix/db/facilitator.py](src/phoenix/db/facilitator.py)
- [src/phoenix/db/migrations/versions/cd164e83824f_users_and_tokens.py](src/phoenix/db/migrations/versions/cd164e83824f_users_and_tokens.py)
- [src/phoenix/server/api/auth.py](src/phoenix/server/api/auth.py)
- [src/phoenix/server/api/dataloaders/span_annotations.py](src/phoenix/server/api/dataloaders/span_annotations.py)
- [src/phoenix/server/api/input_types/CreateSpanAnnotationInput.py](src/phoenix/server/api/input_types/CreateSpanAnnotationInput.py)
- [src/phoenix/server/api/input_types/CreateTraceAnnotationInput.py](src/phoenix/server/api/input_types/CreateTraceAnnotationInput.py)
- [src/phoenix/server/api/input_types/PatchAnnotationInput.py](src/phoenix/server/api/input_types/PatchAnnotationInput.py)
- [src/phoenix/server/api/mutations/api_key_mutations.py](src/phoenix/server/api/mutations/api_key_mutations.py)
- [src/phoenix/server/api/mutations/dataset_mutations.py](src/phoenix/server/api/mutations/dataset_mutations.py)
- [src/phoenix/server/api/mutations/experiment_mutations.py](src/phoenix/server/api/mutations/experiment_mutations.py)
- [src/phoenix/server/api/mutations/model_mutations.py](src/phoenix/server/api/mutations/model_mutations.py)
- [src/phoenix/server/api/mutations/project_mutations.py](src/phoenix/server/api/mutations/project_mutations.py)
- [src/phoenix/server/api/mutations/span_annotations_mutations.py](src/phoenix/server/api/mutations/span_annotations_mutations.py)
- [src/phoenix/server/api/mutations/trace_annotations_mutations.py](src/phoenix/server/api/mutations/trace_annotations_mutations.py)
- [src/phoenix/server/api/mutations/user_mutations.py](src/phoenix/server/api/mutations/user_mutations.py)
- [src/phoenix/server/api/routers/auth.py](src/phoenix/server/api/routers/auth.py)
- [src/phoenix/server/api/routers/oauth2.py](src/phoenix/server/api/routers/oauth2.py)
- [src/phoenix/server/api/types/Annotation.py](src/phoenix/server/api/types/Annotation.py)
- [src/phoenix/server/api/types/SpanAnnotation.py](src/phoenix/server/api/types/SpanAnnotation.py)
- [src/phoenix/server/api/types/TraceAnnotation.py](src/phoenix/server/api/types/TraceAnnotation.py)
- [src/phoenix/server/cost_tracking/cost_model_lookup.py](src/phoenix/server/cost_tracking/cost_model_lookup.py)
- [src/phoenix/server/daemons/generative_model_store.py](src/phoenix/server/daemons/generative_model_store.py)
- [src/phoenix/server/jwt_store.py](src/phoenix/server/jwt_store.py)
- [src/phoenix/server/oauth2.py](src/phoenix/server/oauth2.py)
- [src/phoenix/server/sandbox/wasm_backend.py](src/phoenix/server/sandbox/wasm_backend.py)
- [src/phoenix/server/types.py](src/phoenix/server/types.py)
- [tests/unit/db/test_facilitator.py](tests/unit/db/test_facilitator.py)
- [tests/unit/server/api/mutations/test_project_mutations.py](tests/unit/server/api/mutations/test_project_mutations.py)
- [tests/unit/server/api/mutations/test_span_annotation_mutations.py](tests/unit/server/api/mutations/test_span_annotation_mutations.py)
- [tests/unit/server/api/routers/test_oauth2.py](tests/unit/server/api/routers/test_oauth2.py)
- [tests/unit/server/api/types/test_SpanAnnotation.py](tests/unit/server/api/types/test_SpanAnnotation.py)
- [tests/unit/server/api/types/test_TraceAnnotation.py](tests/unit/server/api/types/test_TraceAnnotation.py)
- [tests/unit/server/cost_tracking/test_cost_model_lookup.py](tests/unit/server/cost_tracking/test_cost_model_lookup.py)
- [tests/unit/server/daemons/test_generative_model_store.py](tests/unit/server/daemons/test_generative_model_store.py)
- [tests/unit/server/test_oauth2.py](tests/unit/server/test_oauth2.py)
- [tests/unit/test_config.py](tests/unit/test_config.py)

</details>



This document describes Phoenix's authentication and authorization system, including supported authentication methods, role-based access control, token management, and security configuration options. For configuration details of the Phoenix server, see [Application Server & Configuration](#2.1). For API access patterns, see [REST API & OpenAPI](#2.3).

## Overview

Phoenix supports multiple authentication methods that can be enabled simultaneously:

- **Local Authentication**: Password-based authentication where user credentials are stored securely as hashed passwords in the database with salts. Handled mainly via `models.LocalUser`. System initialization creates default admin and system users automatically.  
  Key files:  
  - User model: `src/phoenix/db/models.py:348-355`  
  - User mutations: `src/phoenix/server/api/mutations/user_mutations.py:145-152`  
  - Startup facilitator initialization: `src/phoenix/db/facilitator.py:110-158`  

- **OAuth2/OIDC**: Supports integration with multiple identity providers using OAuth2 authorization code flow. Handles login, token exchange, nonce/state verification, and user provisioning as `models.OAuth2User`.  
  Key files:  
  - OAuth2 API router: `src/phoenix/server/api/routers/oauth2.py:92-276`  
  - OAuth2 client helpers: `src/phoenix/server/oauth2.py`  

- **LDAP**: Enterprise directory services integration (Active Directory, OpenLDAP). Supports user provisioning during login, role mapping via LDAP groups. Users are represented as `models.LDAPUser`.  
  Key files:  
  - LDAP user model: `src/phoenix/db/models.py:365-372`  
  - LDAP router (not fully shown here)  

- **API Keys**: Provides programmatic access through system and user API keys represented as JWTs and stored hashed in the database (`models.ApiKey`).  
  Key files:  
  - API key models: `src/phoenix/db/models.py:404-447`  
  - API key mutations: `src/phoenix/server/api/mutations/api_key_mutations.py`  

Authorization is enforced via Role-Based Access Control (RBAC) with predefined roles `ADMIN`, `MEMBER`, and `VIEWER`. The internal `SYSTEM` role is reserved for automated processes and infrastructure users. Role names and assignments are managed in configuration.  
Key files:  
- Role config: `src/phoenix/config.py:40-43`  
- User roles table: `src/phoenix/db/models.py`  

**Sources:**  
[helm/values.yaml:48-61]()  
[src/phoenix/config.py:39-43]()  
[src/phoenix/db/models.py:348-355, 365-372, 404-447]()  
[src/phoenix/server/api/routers/oauth2.py:92-276]()  
[src/phoenix/server/api/mutations/user_mutations.py:145-152]()  
[src/phoenix/db/facilitator.py:110-158]()

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
        LocalAuth["Local Auth<br/>POST /auth/login<br/>(src/phoenix/server/api/routers/auth.py)"]
        OAuth2["OAuth2/OIDC<br/>GET /oauth2/{idp_name}/login<br/>(src/phoenix/server/api/routers/oauth2.py)"]
        LDAPAuth["LDAP Auth<br/>(src/phoenix/server/api/routers/ldap.py)"]
        APIKeyAuth["API Key Auth<br/>(src/phoenix/server/bearer_auth.py)"]
    end
    
    subgraph "Token Management"
        JWTIssuer["JWT Token Issuer<br/>create_access_and_refresh_tokens<br/>(src/phoenix/server/bearer_auth.py)"]
        TokenStore["Token Store<br/>models.RefreshToken<br/>(src/phoenix/db/models.py)"]
        CookieManager["Cookie Manager<br/>set_access_token_cookie<br/>(src/phoenix/auth.py)"]
    end
    
    subgraph "Authorization Layer"
        RBACCheck["RBAC Enforcement<br/>PhoenixUser<br/>(src/phoenix/server/bearer_auth.py)"]
        RoleMapping["Role Mapping<br/>AssignableUserRoleName<br/>(src/phoenix/config.py)"]
        PermissionCheck["Permission Check<br/>IsAdmin, IsNotReadOnly<br/>(src/phoenix/server/api/auth.py)"]
    end
    
    subgraph "Data Layer"
        UserDB["models.User<br/>models.LocalUser<br/>models.OAuth2User<br/>models.LDAPUser<br/>(src/phoenix/db/models.py)"]
        APIKeyDB["models.ApiKey<br/>models.SystemApiKey<br/>models.UserApiKey<br/>(src/phoenix/db/models.py)"]
    end
    
    WebUI --> LocalAuth
    WebUI --> OAuth2
    WebUI --> LDAPAuth
    APIClient --> APIKeyAuth
    OTLPExporter --> APIKeyAuth
    
    LocalAuth --> JWTIssuer
    OAuth2 --> JWTIssuer
    LDAPAuth --> JWTIssuer
    
    JWTIssuer --> TokenStore
    JWTIssuer --> CookieManager
    
    CookieManager --> RBACCheck
    APIKeyAuth --> RBACCheck
    
    RBACCheck --> RoleMapping
    RoleMapping --> PermissionCheck
```

This diagram highlights how high-level natural language entities—like "Local Auth" or "OAuth2/OIDC"—map to concrete API routes and key classes in the codebase, showing the flow from client interactions through token issuance and authorization enforcement.

**Sources:**  
[src/phoenix/server/api/routers/oauth2.py:92-142]()  
[src/phoenix/server/bearer_auth.py:1-50]()  
[src/phoenix/server/api/auth.py:1-32]()  
[src/phoenix/db/models.py:348-447]()  
[src/phoenix/config.py:40-43]()

---

## Authentication Methods

### Local Authentication (Password-Based)

Local authentication uses password hashes stored in the database `models.LocalUser`, with salts for security. Password hashing uses PBKDF2-HMAC-SHA256 with iteration count configured by `NUM_ITERATIONS`. Password validation compares user-supplied input similarly hashed with stored salt to the stored hash using `is_valid_password`.

User creation checks the password and email format for correctness and security. Passwords are validated against configured requirements (`get_password_requirements()`). The system administrator user and system user are seeded on startup by the `Facilitator` class to ensure system integrity and access.

**Key Implementation Details:**

- User credentials stored in fields `password_hash` and `password_salt` on `LocalUser`.  
- Password hashing done through `compute_password_hash` in `src/phoenix/auth.py`.  
- Login endpoint `_login` in `src/phoenix/server/api/routers/auth.py` validates password and issues JWT tokens on success.  
- Admin and system users created if missing by `Facilitator` callbacks on startup (`_ensure_user_roles`, `_ensure_admins`).  

**Configuration:**

- `PHOENIX_DISABLE_BASIC_AUTH` disables password authentication system-wide.  
- `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` sets the initial admin password on first boot.  

**Sources:**  
[src/phoenix/db/models.py:348-355]()  
[src/phoenix/auth.py:22-50]()  
[src/phoenix/server/api/routers/auth.py:144-187]()  
[src/phoenix/db/facilitator.py:110-158]()  
[helm/values.yaml:45-48]()

---

### OAuth2/OIDC Integration

Phoenix supports OAuth2 authentication with multiple external identity providers (Google, Microsoft Entra ID, AWS Cognito, Keycloak, etc.).

**Workflow overview:**

1. User initiates login via `GET /oauth2/{idp_name}/login`.  
2. Phoenix creates an authorization URL via `create_authorization_url` of the selected OAuth2 client, attaches cryptographic `state` and `nonce`, stores them in cookies to protect against CSRF and replay attacks.  
3. User is redirected to the external IdP for authorization.  
4. IdP redirects back to Phoenix at `GET /oauth2/{idp_name}/tokens` with `code` and `state`.  
5. Phoenix validates the `state` cookie against the query parameter, exchanges the code for tokens (including an ID token), validates nonce, and extracts user claims.  
6. Phoenix looks up or creates a user record (`models.OAuth2User`) mapping OAuth2 identity to internal user database.  
7. Phoenix creates access and refresh tokens (JWT) via `create_access_and_refresh_tokens` and sets cookies for session management.  

**Security notes:**

- `state` and `nonce` stored and validated in cookies for CSRF and replay prevention.  
- Token exchange and validation use `joserfc` library for JWT decoding and validation.  
- Rate limiting enforced on login endpoints.  

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Phoenix as Phoenix_Server:<br/>src/phoenix/server/api/routers/oauth2.py
    participant IDP as Identity_Provider
    participant DB as Database:<br/>models.OAuth2User
    
    User->>Browser: Click Login
    Browser->>Phoenix: GET /oauth2/{idp_name}/login
    Phoenix->>Phoenix: create_authorization_url
    Phoenix->>Browser: Redirect with Authorization URL + State + Nonce
    Browser->>IDP: Authorization Request
    IDP->>Browser: Redirect with Code + State
    Browser->>Phoenix: GET /oauth2/{idp_name}/tokens?code&state
    Phoenix->>IDP: Exchange code for tokens
    IDP->>Phoenix: ID Token + Access Token
    Phoenix->>Phoenix: Validate claims, nonce, state
    Phoenix->>DB: Lookup/Create models.OAuth2User with identity claims
    Phoenix->>Phoenix: create_access_and_refresh_tokens
    Phoenix->>Browser: Set authentication cookies
```

**Sources:**  
[src/phoenix/server/api/routers/oauth2.py:92-276]()  
[src/phoenix/server/oauth2.py]()

---

### LDAP Authentication

Phoenix supports LDAP authentication integration as an alternative or supplement to local or OAuth methods. This allows enterprise organizations to integrate their existing directory services such as Active Directory or OpenLDAP.

**Key aspects:**

- LDAP users are stored as `models.LDAPUser` objects. These users do not have local passwords but authenticate against the LDAP server.  
- Role mappings can be configured by LDAP group membership with `auth.ldap.groupRoleMappings`.  
- Automatic user creation (signup) is possible on first LDAP login via configuration `auth.ldap.allowSignUp`.  
- LDAP user attributes like `ldap_unique_id` are stored and updated on successful login.  

**Sources:**  
[helm/values.yaml:50-61]()  
[src/phoenix/db/models.py:365-372]()

---

## Role-Based Access Control (RBAC)

Phoenix implements role-based access control with the following assignable roles:

| Role   | Permission Level                                | Internal Representation                     |
|--------|------------------------------------------------|---------------------------------------------|
| ADMIN  | Full administrative access including user management, system configuration | `Literal["ADMIN"]`                         |
| MEMBER | Standard read/write access to projects, datasets, experiments | `Literal["MEMBER"]`                        |
| VIEWER | Read-only access to most system functionality | `Literal["VIEWER"]`                         |

The `SYSTEM` role exists internally for automated processes, e.g., system API keys and background jobs, and is not assignable to human users.

### Enforcement

Permissions are enforced at the API layer using Strawberry GraphQL permission classes and FastAPI dependencies:

- `IsAdmin`: Restricts an operation to `ADMIN` users only.  
- `IsNotReadOnly`: Blocks operations if the system is in a read-only mode.  
- `IsNotViewer`: Ensures that only `MEMBER` and `ADMIN` roles can perform the operation, blocking `VIEWER` access.

These permission classes are used as decorators on mutations and queries to guard sensitive operations.

**Sources:**  
[src/phoenix/config.py:40-43]()  
[src/phoenix/server/api/auth.py:30]()  
[src/phoenix/server/api/mutations/user_mutations.py:121]()

---

## API Key Management

Phoenix supports system and user API keys to enable programmatic and service-to-service access.

### Storage and Representation

- API keys are stored securely as hashed tokens in the database `models.ApiKey`, to prevent plaintext exposure.  
- System API keys are linked to the `SYSTEM` user role and intended for trusted infrastructure integrations.  
- User API keys are linked to individual users and inherit their permissions and roles.  

### Mutation Operations

API keys can be created and deleted via GraphQL mutations guarded by permission classes (`IsAdmin` for system keys, authenticated for user keys). Creation mutations return the JWT token string for the client to store securely.

```python
# Example create system API key mutation logic:
claims = ApiKeyClaims(
    subject=UserId(system_user.id),
    issued_at=current_time,
    expiration_time=input.expires_at or None,
    attributes=ApiKeyAttributes(
        user_role="SYSTEM",
        name=input.name,
        description=input.description,
    ),
)
token, token_id = await token_store.create_api_key(claims)
```

**Sources:**  
[src/phoenix/db/models.py:404-447]()  
[src/phoenix/server/api/mutations/api_key_mutations.py:63-164]()

---

## Token Management

Phoenix uses JSON Web Tokens (JWT) extensively for session and API key management.

- **Access Tokens**: Short-lived tokens representing authenticated session identity, stored in an HTTP-only cookie called `PHOENIX_ACCESS_TOKEN_COOKIE_NAME`.  
- **Refresh Tokens**: Longer-lived tokens allowing session renewal, stored in the database in `models.RefreshToken` and HTTP-only cookies.  
- **Password Reset Tokens**: JWT tokens for password reset flows.  
- **API Keys**: Special JWT tokens representing system or user API keys.

The `JwtStore` class encapsulates creation, storage, lookup, and revocation of all token types, integrating with the database and caching systems.

Tokens are created via `create_access_and_refresh_tokens` function, setting proper expiration and claims. Token data flows from generation → storage → set cookies (for access tokens) → client usage → authentication → authorization.

**Sources:**  
[src/phoenix/server/bearer_auth.py:1-50]()  
[src/phoenix/db/models.py:378-385]()  
[src/phoenix/server/jwt_store.py:40-190]()

---

## Security Configuration

### Brute Force Protection

Phoenix implements a brute force login protection mechanism that tracks failed login attempts per email address and temporarily blocks further attempts after a configurable limit (`auth.bruteForceLoginProtectionMaxAttempts`). This protects against password guessing attacks.

- Failures and successes are recorded in `BruteForceLoginRateLimiter`.  
- If the limit is reached, HTTP 429 is returned with a generic message to avoid information leakage.

### CSRF and CORS Configuration

- `PHOENIX_CSRF_TRUSTED_ORIGINS`: List of origins that are trusted for CSRF protection in cookies.  
- `PHOENIX_ALLOWED_ORIGINS`: List of allowed CORS origins for cross-origin requests. This is critical for browser-based clients interacting with Phoenix APIs.

### Password Policy

The system supports enforcing a strong password policy (12+ characters, mixed case, digits, special characters) if enabled via `PHOENIX_ENABLE_STRONG_PASSWORD_POLICY`. Password validation is performed when users set or reset passwords.

**Sources:**  
[helm/values.yaml:40-49]()  
[src/phoenix/server/api/routers/auth.py:80-97]()  
[src/phoenix/auth.py:80-98]()

# Summary

Phoenix implements comprehensive authentication and authorization features covering local, OAuth2, and LDAP authentication methods, secured JWT token management including session and API keys, and robust role-based access control policies enforced at the API layer. Security hygiene such as password hashing, brute force protection, CSRF and CORS config, and configurable password policies are key components ensuring Phoenix can securely manage user identities and permissions in AI observability environments.

**Sources Summary:**  
[src/phoenix/db/facilitator.py:110-158]()  
[src/phoenix/server/api/routers/oauth2.py:92-276]()  
[src/phoenix/db/models.py:348-355,365-372,378-385,404-447]()  
[src/phoenix/auth.py:22-50,80-98]()  
[src/phoenix/server/api/routers/auth.py:144-187]()  
[src/phoenix/server/api/mutations/api_key_mutations.py:63-164]()  
[src/phoenix/server/api/auth.py:30]()  
[src/phoenix/server/bearer_auth.py:1-50]()  
[src/phoenix/server/jwt_store.py:40-190]()  
[helm/values.yaml:40-61]()

---

# Page: Cost Tracking & Model Pricing

# Cost Tracking & Model Pricing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/.scripts/sync_models.py](.github/.scripts/sync_models.py)
- [src/phoenix/auth.py](src/phoenix/auth.py)
- [src/phoenix/db/facilitator.py](src/phoenix/db/facilitator.py)
- [src/phoenix/db/migrations/versions/cd164e83824f_users_and_tokens.py](src/phoenix/db/migrations/versions/cd164e83824f_users_and_tokens.py)
- [src/phoenix/server/api/mutations/model_mutations.py](src/phoenix/server/api/mutations/model_mutations.py)
- [src/phoenix/server/api/mutations/user_mutations.py](src/phoenix/server/api/mutations/user_mutations.py)
- [src/phoenix/server/api/routers/auth.py](src/phoenix/server/api/routers/auth.py)
- [src/phoenix/server/cost_tracking/cost_model_lookup.py](src/phoenix/server/cost_tracking/cost_model_lookup.py)
- [src/phoenix/server/cost_tracking/model_cost_manifest.json](src/phoenix/server/cost_tracking/model_cost_manifest.json)
- [src/phoenix/server/daemons/generative_model_store.py](src/phoenix/server/daemons/generative_model_store.py)
- [src/phoenix/server/sandbox/wasm_backend.py](src/phoenix/server/sandbox/wasm_backend.py)
- [tests/unit/db/test_facilitator.py](tests/unit/db/test_facilitator.py)
- [tests/unit/server/cost_tracking/test_cost_model_lookup.py](tests/unit/server/cost_tracking/test_cost_model_lookup.py)
- [tests/unit/server/daemons/test_generative_model_store.py](tests/unit/server/daemons/test_generative_model_store.py)
- [tests/unit/test_config.py](tests/unit/test_config.py)

</details>



The cost tracking subsystem in Phoenix provides automated calculation and reporting of LLM token costs across spans, traces, and projects. It integrates a static manifest of model prices, a background daemon to synchronize model metadata, a cache lookup mechanism to resolve model pricing, and specialized calculators that compute costs based on token usage.

## System Architecture

The cost tracking system consists of four major components managing cost data from ingestion to cost computation and storage:

1. **Model Cost Manifest**  
   A static JSON file defining baseline pricing configurations for known LLM models and providers, such as OpenAI, Anthropic, and AWS Bedrock.

2. **CostModelLookup**  
   A utility class that matches raw model names reported in spans/traces to standardized model pricing information using regex patterns and database cache entries.

3. **GenerativeModelStore Daemon**  
   A server-side background daemon that periodically fetches generative model metadata and pricing from the database, maintaining an in-memory cache to reduce database queries during high-frequency lookups.

4. **SpanCostCalculator**  
   A background process that scans ingested spans for LLM usage, resolves their models through `CostModelLookup`, and calculates USD cost contributions based on token counts and pricing tiers.

---

### Overview Diagram: Cost Tracking System Components and Data Flow

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserTrace["LLM Trace (e.g. GPT-4o)"]
    end

    subgraph "Code Entity Space"
        Manifest["model_cost_manifest.json"]
        Lookup["CostModelLookup"]
        Store["GenerativeModelStore (Daemon)"]
        Calculator["SpanCostCalculator (Daemon)"]
        DB_Models["models.GenerativeModel (DB)"]
        DB_SpanCosts["models.SpanCost (DB)"]
    end

    Manifest -->|Provides Base Rates to| Store
    Store -->|Syncs Models and Prices| DB_Models
    UserTrace -->|Span ingestion via OTLP| Calculator
    DB_Models -->|Pricing Lookup| Calculator
    Lookup -->|Model Name Matching| Calculator
    Calculator -->|Writes Calculated Cost| DB_SpanCosts
```

Sources:  
[src/phoenix/server/daemons/generative_model_store.py:1-102](),  
[src/phoenix/server/cost_tracking/model_cost_manifest.json:1-60](),  
[src/phoenix/server/cost_tracking/cost_model_lookup.py:1-40](),  
[src/phoenix/db/facilitator.py:75-89,82-82]()

---

## Model Cost Manifest

The core reference for pricing is the `model_cost_manifest.json` file located in the server cost tracking directory. This JSON manifest provides canonical LLM model entries along with detailed token price attributes.

### Structure and Content

Each model entry contains:

- **name**  
  The canonical internal model name identifier.

- **name_pattern**  
  A regex pattern to match variants and aliases of the model name as reported in incoming span attributes.

- **source**  
  The origin source of the pricing data (e.g., "litellm" indicating pricing from LiteLLM data).

- **token_prices**  
  An array of objects specifying per-token pricing by type and whether tokens contribute to prompt (input) or output costs.

Example snippet of a model entry:
```json
{
  "name": "chatgpt-4o-latest",
  "name_pattern": "chatgpt-4o-latest",
  "source": "litellm",
  "token_prices": [
    {
      "base_rate": 5e-6,
      "is_prompt": true,
      "token_type": "input"
    },
    {
      "base_rate": 0.000015,
      "is_prompt": false,
      "token_type": "output"
    }
  ]
}
```

The manifest includes price entries for input tokens, output tokens, and sometimes for cache reads/writes or audio tokens. Rates are expressed in USD per token.

Sources:  
[src/phoenix/server/cost_tracking/model_cost_manifest.json:1-60]()

---

## CostModelLookup Class

`CostModelLookup` is designed to match fuzzy model names from span attributes to canonical models stored in the database. It uses regex matching against the `name_pattern` field of cached generative models.

### Key Responsibilities

- On initialization or upon model data refresh, it caches the set of generative models from the database with their regex patterns compiled.

- Given a model name string and timestamp of the span, it resolves the best matching generative model, which includes token pricing information.

- Supports quick lookup for repeated queries without hitting the database on each span processing.

Sources:  
[src/phoenix/server/cost_tracking/cost_model_lookup.py:1-40]()

---

## GenerativeModelStore Daemon

The `GenerativeModelStore` is a long-running background daemon within the Phoenix server responsible for synchronizing generative model data from the database into an in-memory cache for efficient pricing lookups.

### Functionality and Implementation

- Periodically queries the `generative_models` and associated token prices from the relational database.

- Employs **incremental fetching** using timestamp filters (`updated_at`, `deleted_at`) with a 10-second clock skew buffer to minimize redundant database queries and reduce cloud egress costs.

- On fetch, uses `.merge()` semantics to update or add new models into the internal `CostModelLookup`.

- The lookup cache is then used by the `SpanCostCalculator` for cost resolution per span.

- The daemon runs asynchronously, sleeping for a configurable refresh interval (default ~5 seconds) between fetch cycles.

### Important Notes

- Models' `updated_at` field must be explicitly maintained on all modifications, including associated token prices, to allow incremental fetch to work reliably.

- The synchronization strategy trading memory for reduced DB calls is optimized to support frequent queries at computation time without incurring repeated remote database cost.

### Relevant code snippet illustrating fetch and incremental updates:
```python
async def _fetch_models(self) -> None:
    stmt = sa.select(models.GenerativeModel).options(
        joinedload(models.GenerativeModel.token_prices)
    )
    if self._last_fetch_time:
        stmt = stmt.where(
            sa.or_(
                models.GenerativeModel.updated_at >= self._last_fetch_time,
                models.GenerativeModel.deleted_at >= self._last_fetch_time,
            )
        )
    async with self._db() as session:
        generative_models = (await session.scalars(stmt)).unique().all()

    if not generative_models:
        return

    self._lookup.merge(generative_models)
```

Sources:  
[src/phoenix/server/daemons/generative_model_store.py:20-102](),  
[src/phoenix/db/facilitator.py:82-85]()

---

## SpanCostCalculator Overview

`SpanCostCalculator` is a subsystem daemon that processes ingested spans to compute and persist LLM token usage costs.

### Process Steps

1. **Span Fetching**  
   Iterates over spans marked with `span_kind` of type `LLM` which typically contain token usage details.

2. **Model Name Extraction & Lookup**  
   Extracts model identifying information from span attributes, uses `CostModelLookup` to resolve to a canonical model with known pricing.

3. **Token Counts & Pricing**  
   Reads token counts for prompt (input), completion (output), and optionally other categories such as cache reads/writes.

4. **Cost Computation**  
   For each token type present, multiplies token count by the matching price rate.

5. **Cost Recording**  
   Creates `SpanCost` records reflecting USD amounts for the associated span.

### Span Cost Calculation Sequence Diagram

```mermaid
sequenceDiagram
    participant D as "SpanCostCalculator"
    participant DB as "SQLAlchemy (models.Span)"
    participant L as "CostModelLookup"
    participant C as "Computed Cost"

    D->>DB: Fetch spans missing cost records where span_kind == LLM
    loop For each span
        D->>DB: Extract model_name and token counts
        D->>L: Lookup generative model by model_name
        L-->>D: Return matching model with pricing
        D->>D: Compute cost = tokens * base_rate for each token_type
        D->>DB: Insert computed cost into models.SpanCost table
    end
```

Sources:  
[src/phoenix/server/daemons/generative_model_store.py:61-102](),  
[src/phoenix/db/facilitator.py:80-85]()

---

## Database Seeding and Facilitation

Phoenix provides a `Facilitator` class that runs at server startup to ensure all required database enums, roles, users, and model cost data are seeded correctly for proper system operation.

### Model Cost Initialization

- The `_ensure_model_costs` function is one of the standard callbacks in `Facilitator`.

- It reads the cost manifest JSON and inserts new or missing generative models and token prices into the database, ensuring idempotency.

- This process guarantees that model cost data from the manifest is available in the database for `GenerativeModelStore` to load.

Sources:  
[src/phoenix/db/facilitator.py:55-91](),  
[tests/unit/db/test_facilitator.py:10-135]()

---

## Managing Models via GraphQL API Mutations

Cost tracking data can be managed interactively with GraphQL mutations, facilitating manual override or addition of cost models.

### Key Mutations Supported

- **createModel**  
  Adds a new generative model with associated pricing details.

- **updateModel**  
  Modifies existing models, allowing updates to name patterns or token costs.

- **deleteModel**  
  Soft deletes models, ensuring removal from the lookup cache.

These mutations allow dynamic control over model pricing, supplementing the static manifest.

### Lifecycle and Incremental Sync Testing

Unit tests verify the `GenerativeModelStore` daemon's correct behavior:

- Loading all models on first fetch.

- Incremental fetching for updates using `updated_at` timestamp.

- Correctly removing soft-deleted models.

- Updating `_last_fetch_time` after each cycle to track incremental changes.

Sources:  
[tests/unit/server/daemons/test_generative_model_store.py:30-180](),  
[src/phoenix/server/api/mutations/user_mutations.py:120-180]()

---

# Summary

The Phoenix cost tracking and model pricing subsystem offers fully automated, accurate LLM cost computation by:

- Utilizing a comprehensive static JSON manifest with regex-based model matching.

- Providing an in-memory cache and lookup via `CostModelLookup` for efficient runtime price resolution.

- Synchronizing model state continuously with `GenerativeModelStore` to reflect the latest database state.

- Calculating costs through span processors that compute per-span USD token usage.

- Supporting administrative overrides and expansions via GraphQL mutations.

This design optimizes database load, reduces egress costs, and provides transparent cost tracking as part of Phoenix’s AI observability platform.

---

Sources:  
[src/phoenix/server/cost_tracking/model_cost_manifest.json](),  
[src/phoenix/server/cost_tracking/cost_model_lookup.py](),  
[src/phoenix/server/daemons/generative_model_store.py](),  
[src/phoenix/db/facilitator.py](),  
[tests/unit/server/daemons/test_generative_model_store.py](),  
[tests/unit/db/test_facilitator.py]()

---

# Page: Client Libraries

# Client Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [app/src/pages/auth/AuthLayout.tsx](app/src/pages/auth/AuthLayout.tsx)
- [docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx](docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx)
- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx](docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx)
- [docs/phoenix/sdk-api-reference/typescript/overview.mdx](docs/phoenix/sdk-api-reference/typescript/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx)
- [js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md](js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md)
- [js/examples/apps/demo-document-relevancy-experiment/package.json](js/examples/apps/demo-document-relevancy-experiment/package.json)
- [js/packages/phoenix-cli/CHANGELOG.md](js/packages/phoenix-cli/CHANGELOG.md)
- [js/packages/phoenix-cli/package.json](js/packages/phoenix-cli/package.json)
- [js/packages/phoenix-client/CHANGELOG.md](js/packages/phoenix-client/CHANGELOG.md)
- [js/packages/phoenix-client/README.md](js/packages/phoenix-client/README.md)
- [js/packages/phoenix-client/package.json](js/packages/phoenix-client/package.json)
- [js/packages/phoenix-config/CHANGELOG.md](js/packages/phoenix-config/CHANGELOG.md)
- [js/packages/phoenix-config/README.md](js/packages/phoenix-config/README.md)
- [js/packages/phoenix-config/package.json](js/packages/phoenix-config/package.json)
- [js/packages/phoenix-evals/CHANGELOG.md](js/packages/phoenix-evals/CHANGELOG.md)
- [js/packages/phoenix-evals/README.md](js/packages/phoenix-evals/README.md)
- [js/packages/phoenix-evals/package.json](js/packages/phoenix-evals/package.json)
- [js/packages/phoenix-mcp/CHANGELOG.md](js/packages/phoenix-mcp/CHANGELOG.md)
- [js/packages/phoenix-mcp/README.md](js/packages/phoenix-mcp/README.md)
- [js/packages/phoenix-mcp/package.json](js/packages/phoenix-mcp/package.json)
- [js/packages/phoenix-mcp/src/index.ts](js/packages/phoenix-mcp/src/index.ts)
- [js/packages/phoenix-mcp/src/projectTools.ts](js/packages/phoenix-mcp/src/projectTools.ts)
- [js/packages/phoenix-otel/CHANGELOG.md](js/packages/phoenix-otel/CHANGELOG.md)
- [js/packages/phoenix-otel/README.md](js/packages/phoenix-otel/README.md)
- [js/packages/phoenix-otel/package.json](js/packages/phoenix-otel/package.json)
- [packages/phoenix-client/README.md](packages/phoenix-client/README.md)
- [packages/phoenix-client/src/phoenix/client/client.py](packages/phoenix-client/src/phoenix/client/client.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/google_generativeai/generate_content.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/google_generativeai/generate_content.py)
- [packages/phoenix-client/src/phoenix/client/resources/prompts/__init__.py](packages/phoenix-client/src/phoenix/client/resources/prompts/__init__.py)
- [packages/phoenix-client/src/phoenix/client/types/prompts.py](packages/phoenix-client/src/phoenix/client/types/prompts.py)
- [packages/phoenix-client/tests/client/resources/experiments/test_experiment_urls.py](packages/phoenix-client/tests/client/resources/experiments/test_experiment_urls.py)
- [packages/phoenix-client/tests/client/test_client.py](packages/phoenix-client/tests/client/test_client.py)
- [packages/phoenix-evals/README.md](packages/phoenix-evals/README.md)
- [packages/phoenix-otel/README.md](packages/phoenix-otel/README.md)
- [requirements/packages/phoenix-client.txt](requirements/packages/phoenix-client.txt)

</details>



Phoenix provides client libraries for programmatic interaction with the Phoenix platform. These libraries enable developers to instrument applications with OpenTelemetry, manage datasets and experiments, run evaluations, and query trace data without using the web UI.

The client libraries are available in both Python and TypeScript, with each ecosystem providing core packages plus additional tools. All packages are independently versioned and distributed through PyPI (Python) or NPM (TypeScript).

For information about the server APIs these clients communicate with, see [REST API & OpenAPI](#2.3) and [GraphQL API](#2.2). For tracing ingestion, see [OTLP Ingestion & gRPC Server](#2.4).

## Package Ecosystem

Phoenix's client libraries are organized into two language ecosystems with parallel functionality:

**Python Packages:**
- **[Python OpenTelemetry (arize-phoenix-otel)](#3.2)** - OpenTelemetry wrapper for trace instrumentation. [packages/phoenix-otel/README.md:11]()
- **[Python Client (arize-phoenix-client)](#3.1)** - REST/GraphQL client for platform API access. [README.md:22]()
- **[Python Evaluations (arize-phoenix-evals)](#3.3)** - Evaluation framework with LLM-as-judge evaluators. [README.md:47]()

**TypeScript Packages:**
- **[TypeScript Client](#3.4)** - OpenTelemetry wrapper for trace instrumentation via `@arizeai/phoenix-otel`. [js/packages/phoenix-otel/package.json:2-4]()
- **[TypeScript Client](#3.4)** - Type-safe REST client for platform API access via `@arizeai/phoenix-client`. [js/packages/phoenix-client/package.json:2-4]()
- **[TypeScript Client](#3.4)** - Evaluation framework for AI use cases via `@arizeai/phoenix-evals`. [js/packages/phoenix-evals/package.json:2-4]()
- **[Command Line Interface (CLI)](#3.5)** - Command-line interface for Phoenix operations. [js/packages/phoenix-cli/package.json:2-4]()
- **[MCP Server](#3.6)** - Model Context Protocol server for AI assistants. [js/packages/phoenix-mcp/package.json:2-4]()

**Diagram: Client Library Architecture**

```mermaid
graph TB
    subgraph "Python Ecosystem"
        [PyApp] -->|"Instrument spans"| [PyOtel]
        [PyApp] -->|"Query/mutate data"| [PyClient]
        [PyApp] -->|"Run evaluations"| [PyEvals]
        
        [PyOtel]
        [PyClient]
        [PyEvals]
    end
    
    subgraph "TypeScript Ecosystem"
        [TSApp] -->|"Instrument spans"| [TSOtel]
        [TSApp] -->|"Query/mutate data"| [TSClient]
        [TSApp] -->|"Run evaluations"| [TSEvals]
        
        [CLI] -->|"Uses"| [TSClient]
        [MCP] -->|"Uses"| [TSClient]
        
        [TSOtel]
        [TSClient]
        [TSEvals]
        [CLI]
        [MCP]
    end
    
    subgraph "Phoenix Server"
        [OTLP_Ingestion]
        [REST_API]
        [GQL_API]
    end
    
    [PyOtel] -->|"OTLP/HTTP"| [OTLP_Ingestion]
    [TSOtel] -->|"OTLP/HTTP"| [OTLP_Ingestion]
    
    [PyClient] -->|"HTTP"| [REST_API]
    [TSClient] -->|"HTTP"| [REST_API]
    
    [PyClient] -.->|"Optional"| [GQL_API]
```

Sources: [README.md:44-53](), [js/packages/phoenix-client/package.json:2-13](), [js/packages/phoenix-mcp/package.json:33-36]()

## Package Distribution

All client libraries are distributed through public package registries with independent versioning:

| Package | Registry | Purpose | Documentation |
|---------|----------|---------|---------------|
| `arize-phoenix-otel` | PyPI | OpenTelemetry trace instrumentation | [Python OpenTelemetry (arize-phoenix-otel)](#3.2) |
| `arize-phoenix-client` | PyPI | REST/GraphQL API client | [Python Client (arize-phoenix-client)](#3.1) |
| `arize-phoenix-evals` | PyPI | LLM evaluation framework | [Python Evaluations (arize-phoenix-evals)](#3.3) |
| `@arizeai/phoenix-otel` | NPM | OpenTelemetry trace instrumentation | [TypeScript Client](#3.4) |
| `@arizeai/phoenix-client` | NPM | Type-safe REST API client | [TypeScript Client](#3.4) |
| `@arizeai/phoenix-evals` | NPM | Evaluation framework | [TypeScript Client](#3.4) |
| `@arizeai/phoenix-cli` | NPM | Command-line interface (`px` command) | [Command Line Interface (CLI)](#3.5) |
| `@arizeai/phoenix-mcp` | NPM | Model Context Protocol server | [MCP Server](#3.6) |

Sources: [README.md:22-39](), [js/packages/phoenix-client/package.json:2-3](), [js/packages/phoenix-mcp/package.json:2-3](), [js/packages/phoenix-cli/package.json:2-3]()

## Installation

Install client libraries via package managers:

**Python:**
```bash
# Install core packages via pip
pip install arize-phoenix-client arize-phoenix-otel arize-phoenix-evals
```

**TypeScript:**
```bash
# Install core packages via pnpm, npm, or yarn
pnpm add @arizeai/phoenix-otel @arizeai/phoenix-client @arizeai/phoenix-evals

# Install developer tools globally or as dev dependencies
pnpm add -g @arizeai/phoenix-cli @arizeai/phoenix-mcp
```

Sources: [js/packages/phoenix-client/README.md:29-32](), [packages/phoenix-otel/README.md:52-58](), [js/packages/phoenix-cli/package.json:21-24]()

## Common Usage Patterns

The client libraries provide consistent APIs across languages for common operations:

**Diagram: Code Entity Mapping**

```mermaid
graph LR
    subgraph "Code Space"
        [createClient] --> [PhoenixClient]
        [createPrompt] --> [PromptVersion]
        [px] --> [Commander_CLI]
    end
    
    subgraph "Platform Space"
        [PhoenixClient] --> [REST_v1_Endpoints]
        [PromptVersion] --> [Prompt_Management]
        [Commander_CLI] --> [Resource_Operations]
    end
```

**Working with Prompts:**
The TypeScript client provides dedicated exports for prompt management, including `createPrompt`, `getPrompt`, and `toSDK` for integration with LLM provider SDKs like OpenAI, Anthropic, and Vercel AI SDK [js/packages/phoenix-client/README.md:66-130]().

**Querying Spans:**
Spans can be retrieved with extensive filters for `name`, `spanKind`, `statusCode`, `parentId`, `traceIds`, and specific `attributes` matching [js/packages/phoenix-client/CHANGELOG.md:73-159]().

**Session Management:**
Clients support querying session data via `getSession` and `listSessions`, as well as retrieving ordered conversation turns via `getSessionTurns` [js/packages/phoenix-client/CHANGELOG.md:143-167]().

Sources: [js/packages/phoenix-client/README.md:66-130](), [js/packages/phoenix-client/CHANGELOG.md:73-167]()

## OpenTelemetry Tracing

Both ecosystems provide OTEL wrapper packages that simplify trace instrumentation and export to Phoenix. These packages handle OTLP exporter configuration and semantic conventions.

**Python OpenTelemetry (`arize-phoenix-otel`):**
Provides a `register()` function that configures `TracerProvider`, `BatchSpanProcessor`, and `HTTPSpanExporter` with Phoenix-aware defaults based on environment variables like `PHOENIX_COLLECTOR_ENDPOINT` [packages/phoenix-otel/README.md:65-182]().

**TypeScript OpenTelemetry (`@arizeai/phoenix-otel`):**
Provides Node.js tracing SDK registration, manual span helpers, and context attributes for LLM observability. It integrates with `@arizeai/openinference-semantic-conventions` [js/packages/phoenix-otel/package.json:4-58]().

Sources: [packages/phoenix-otel/README.md:25-73](), [js/packages/phoenix-otel/package.json:55-67]()

## Code Generation

The TypeScript client uses code generation to maintain type safety with the Phoenix server API:

**OpenAPI Type Generation:**
The TypeScript client types are generated from the Phoenix OpenAPI schema [js/packages/phoenix-client/package.json:78]():

```bash
# From js/packages/phoenix-client
pnpm run generate
```

This runs `openapi-typescript` against `../../../schemas/openapi.json` to produce `./src/__generated__/api/v1.ts` [js/packages/phoenix-client/package.json:78]().

Sources: [js/packages/phoenix-client/package.json:75-81]()

## Evaluation Libraries

Both ecosystems provide evaluation frameworks that use LLMs to assess application outputs:

**Python Evaluations (`arize-phoenix-evals`):**
A comprehensive library for running evaluations for AI use cases [packages/phoenix-evals/README.md:1]().

**TypeScript Evaluations (`@arizeai/phoenix-evals`):**
Includes pre-built evaluators for `conciseness`, `correctness`, `document relevance`, `refusal`, and `tool selection/invocation` [js/packages/phoenix-evals/CHANGELOG.md:43-64](). It leverages the Vercel AI SDK for LLM interactions and `mustache` for templating [js/packages/phoenix-evals/package.json:76-78]().

Sources: [js/packages/phoenix-evals/package.json:2-10](), [js/packages/phoenix-evals/CHANGELOG.md:19-64]()

## Developer Tools

### Command-Line Interface

The `@arizeai/phoenix-cli` package provides the `px` and `phoenix-cli` commands [js/packages/phoenix-cli/package.json:21-24](). It uses a noun-verb format for resource management (e.g., `px project list`, `px trace get`) [js/packages/phoenix-cli/CHANGELOG.md:139-150]().

Key features include:
- **Profiles**: Support for named profiles stored in `~/.px/settings.json` (or XDG path) [js/packages/phoenix-cli/CHANGELOG.md:54-57]().
- **Annotations**: Commands for managing and bulk-deleting annotations on spans, traces, and sessions (e.g., `px span-annotations delete`) [js/packages/phoenix-cli/CHANGELOG.md:7-12]().
- **Notes**: Support for adding and fetching notes on traces and spans via `addTraceNote` and `addSpanNote` [js/packages/phoenix-cli/CHANGELOG.md:78-101]().

Sources: [js/packages/phoenix-cli/package.json:42-49](), [js/packages/phoenix-cli/CHANGELOG.md:7-150]()

### Model Context Protocol Server

The `@arizeai/phoenix-mcp` package implements an MCP server for AI coding assistants [js/packages/phoenix-mcp/package.json:4]().

It exposes tools such as:
- `list-projects`, `get-project`
- `list-traces`, `get-trace`, `get-spans`
- `list-sessions`, `get-session`
- `get-prompt-version-by-tag`, `list-prompt-version-tags` [js/packages/phoenix-mcp/CHANGELOG.md:120-125]()

Sources: [js/packages/phoenix-mcp/package.json:33-40](), [js/packages/phoenix-mcp/CHANGELOG.md:111-130]()

---

# Page: Python Client (arize-phoenix-client)

# Python Client (arize-phoenix-client)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [js/packages/phoenix-client/examples/create_dataset_from_spans.ts](js/packages/phoenix-client/examples/create_dataset_from_spans.ts)
- [js/packages/phoenix-client/examples/dataset_get_by_name.ts](js/packages/phoenix-client/examples/dataset_get_by_name.ts)
- [js/packages/phoenix-client/src/constants/serverRequirements.ts](js/packages/phoenix-client/src/constants/serverRequirements.ts)
- [js/packages/phoenix-client/src/datasets/appendDatasetExamples.ts](js/packages/phoenix-client/src/datasets/appendDatasetExamples.ts)
- [js/packages/phoenix-client/src/datasets/createDataset.ts](js/packages/phoenix-client/src/datasets/createDataset.ts)
- [js/packages/phoenix-client/src/datasets/getDataset.ts](js/packages/phoenix-client/src/datasets/getDataset.ts)
- [js/packages/phoenix-client/src/datasets/getDatasetExamples.ts](js/packages/phoenix-client/src/datasets/getDatasetExamples.ts)
- [js/packages/phoenix-client/src/datasets/getDatasetInfo.ts](js/packages/phoenix-client/src/datasets/getDatasetInfo.ts)
- [js/packages/phoenix-client/src/datasets/getDatasetInfoByName.ts](js/packages/phoenix-client/src/datasets/getDatasetInfoByName.ts)
- [js/packages/phoenix-client/src/datasets/index.ts](js/packages/phoenix-client/src/datasets/index.ts)
- [js/packages/phoenix-client/src/experiments/getExperimentInfo.ts](js/packages/phoenix-client/src/experiments/getExperimentInfo.ts)
- [js/packages/phoenix-client/src/sessions/getSession.ts](js/packages/phoenix-client/src/sessions/getSession.ts)
- [js/packages/phoenix-client/src/sessions/listSessions.ts](js/packages/phoenix-client/src/sessions/listSessions.ts)
- [js/packages/phoenix-client/src/sessions/sessionUtils.ts](js/packages/phoenix-client/src/sessions/sessionUtils.ts)
- [js/packages/phoenix-client/src/spans/getSpanAnnotations.ts](js/packages/phoenix-client/src/spans/getSpanAnnotations.ts)
- [js/packages/phoenix-client/src/spans/getSpans.ts](js/packages/phoenix-client/src/spans/getSpans.ts)
- [js/packages/phoenix-client/src/traces/index.ts](js/packages/phoenix-client/src/traces/index.ts)
- [js/packages/phoenix-client/src/types/datasets.ts](js/packages/phoenix-client/src/types/datasets.ts)
- [js/packages/phoenix-client/src/types/projects.ts](js/packages/phoenix-client/src/types/projects.ts)
- [js/packages/phoenix-client/src/types/sessions.ts](js/packages/phoenix-client/src/types/sessions.ts)
- [js/packages/phoenix-client/test/datasets/appendDatasetExamples.test.ts](js/packages/phoenix-client/test/datasets/appendDatasetExamples.test.ts)
- [js/packages/phoenix-client/test/datasets/createDataset.test.ts](js/packages/phoenix-client/test/datasets/createDataset.test.ts)
- [js/packages/phoenix-client/test/datasets/getDataset.test.ts](js/packages/phoenix-client/test/datasets/getDataset.test.ts)
- [js/packages/phoenix-client/test/sessions/getSession.test.ts](js/packages/phoenix-client/test/sessions/getSession.test.ts)
- [js/packages/phoenix-client/test/spans/getSpans.test.ts](js/packages/phoenix-client/test/spans/getSpans.test.ts)
- [packages/phoenix-client/examples/experiments/experiment_trace_evaluator.py](packages/phoenix-client/examples/experiments/experiment_trace_evaluator.py)
- [packages/phoenix-client/src/phoenix/client/client.py](packages/phoenix-client/src/phoenix/client/client.py)
- [packages/phoenix-client/src/phoenix/client/constants/server_requirements.py](packages/phoenix-client/src/phoenix/client/constants/server_requirements.py)
- [packages/phoenix-client/src/phoenix/client/experiments/__init__.py](packages/phoenix-client/src/phoenix/client/experiments/__init__.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/google_generativeai/generate_content.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/google_generativeai/generate_content.py)
- [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py](packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py)
- [packages/phoenix-client/src/phoenix/client/resources/experiments/__init__.py](packages/phoenix-client/src/phoenix/client/resources/experiments/__init__.py)
- [packages/phoenix-client/src/phoenix/client/resources/experiments/evaluators.py](packages/phoenix-client/src/phoenix/client/resources/experiments/evaluators.py)
- [packages/phoenix-client/src/phoenix/client/resources/experiments/types.py](packages/phoenix-client/src/phoenix/client/resources/experiments/types.py)
- [packages/phoenix-client/src/phoenix/client/resources/prompts/__init__.py](packages/phoenix-client/src/phoenix/client/resources/prompts/__init__.py)
- [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py](packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py)
- [packages/phoenix-client/src/phoenix/client/types/prompts.py](packages/phoenix-client/src/phoenix/client/types/prompts.py)
- [packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py](packages/phoenix-client/src/phoenix/client/utils/annotation_helpers.py)
- [packages/phoenix-client/src/phoenix/client/utils/executors.py](packages/phoenix-client/src/phoenix/client/utils/executors.py)
- [packages/phoenix-client/src/phoenix/client/utils/rate_limiters.py](packages/phoenix-client/src/phoenix/client/utils/rate_limiters.py)
- [packages/phoenix-client/tests/client/resources/datasets/test_datasets.py](packages/phoenix-client/tests/client/resources/datasets/test_datasets.py)
- [packages/phoenix-client/tests/client/resources/experiments/test_example_proxy.py](packages/phoenix-client/tests/client/resources/experiments/test_example_proxy.py)
- [packages/phoenix-client/tests/client/resources/experiments/test_experiment_urls.py](packages/phoenix-client/tests/client/resources/experiments/test_experiment_urls.py)
- [packages/phoenix-client/tests/client/resources/experiments/test_trace_id_binding.py](packages/phoenix-client/tests/client/resources/experiments/test_trace_id_binding.py)
- [packages/phoenix-client/tests/client/resources/spans/test_spans.py](packages/phoenix-client/tests/client/resources/spans/test_spans.py)
- [packages/phoenix-client/tests/client/test_client.py](packages/phoenix-client/tests/client/test_client.py)
- [packages/phoenix-client/tests/client/utils/test_annotation_hepers.py](packages/phoenix-client/tests/client/utils/test_annotation_hepers.py)
- [packages/phoenix-client/tests/client/utils/test_executors.py](packages/phoenix-client/tests/client/utils/test_executors.py)
- [packages/phoenix-evals/tests/phoenix/evals/test_executor.py](packages/phoenix-evals/tests/phoenix/evals/test_executor.py)
- [requirements/packages/phoenix-client.txt](requirements/packages/phoenix-client.txt)
- [tests/integration/client/test_datasets.py](tests/integration/client/test_datasets.py)
- [tests/integration/client/test_experiments.py](tests/integration/client/test_experiments.py)
- [tests/integration/client/test_spans.py](tests/integration/client/test_spans.py)
- [tutorials/human_feedback/chatbot_with_human_feedback.ipynb](tutorials/human_feedback/chatbot_with_human_feedback.ipynb)

</details>



The `arize-phoenix-client` package is a lightweight Python library designed for programmatic interaction with a Phoenix server. Unlike the main `arize-phoenix` package, which contains the full server and UI logic, the client focuses on providing high-performance access to the Phoenix REST and GraphQL APIs. It is primarily used for managing datasets, running experiments, retrieving traces/spans, and managing prompts.

## Architecture and Client Structure

The client is built on top of `httpx` and provides both synchronous (`Client`) and asynchronous (`AsyncClient`) interfaces. It organizes functionality into specialized resource classes that map to the server's domain model.

### Code Entity Space: Client Structure
The following diagram maps the logical resources to their implementation classes in the codebase.

```mermaid
graph TD
    subgraph "packages/phoenix-client/src/phoenix/client/client.py"
        Client["class Client"]
        AsyncClient["class AsyncClient"]
    end

    subgraph "Resource Implementation Classes"
        Spans["class Spans (resources/spans)"]
        Datasets["class Datasets (resources/datasets)"]
        Experiments["class Experiments (resources/experiments)"]
        Prompts["class Prompts (resources/prompts)"]
        Sessions["class Sessions (resources/sessions)"]
        Traces["class Traces (resources/traces)"]
    end

    subgraph "Infrastructure"
        Guard["class ServerVersionGuard"]
        V1["module phoenix.client.__generated__.v1"]
    end

    Client --> Spans
    Client --> Datasets
    Client --> Experiments
    Client --> Prompts
    Client --> Sessions
    Client --> Traces
    
    AsyncClient --> Spans
    AsyncClient --> Datasets
    AsyncClient --> Experiments
    AsyncClient --> Prompts
    AsyncClient --> Sessions
    AsyncClient --> Traces
    
    Spans --> Guard
    Datasets --> Guard
    
    subgraph "Phoenix Server"
        API["FastAPI Routers"]
    end

    Spans -- "HTTP REST" --> API
    Experiments -- "HTTP REST" --> API
```
Sources: [packages/phoenix-client/src/phoenix/client/client.py:18-66](), [packages/phoenix-client/src/phoenix/client/client.py:132-179]()

### Initialization and Configuration
The client automatically discovers the Phoenix server using environment variables such as `PHOENIX_BASE_URL` and `PHOENIX_API_KEY`.

- **Client**: Initializes `httpx.Client` and attaches resource managers. It sets default timeouts for connection (10s) and reading (30s). [packages/phoenix-client/src/phoenix/client/client.py:18-50]()
- **AsyncClient**: Initializes `httpx.AsyncClient` for non-blocking I/O. [packages/phoenix-client/src/phoenix/client/client.py:132-163]()
- **ServerVersionGuard**: A utility that checks the server's version against requirements to prevent calling unsupported endpoints. [packages/phoenix-client/src/phoenix/client/utils/server_requirements.py:15-38](), [packages/phoenix-client/src/phoenix/client/constants/server_requirements.py:30-34]()

Sources: [packages/phoenix-client/src/phoenix/client/client.py:18-180](), [packages/phoenix-client/src/phoenix/client/utils/config.py:14-15]()

---

## Resource APIs

### 1. Spans and Annotations
The `Spans` resource provides methods to retrieve spans, log spans manually, and manage annotations (evaluations). It supports both list-based and `pandas.DataFrame` outputs.

- **Data Retrieval**: `get_spans_dataframe` allows complex filtering using `SpanQuery` objects and handles serialization of attributes for query parameters. [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:171-182](), [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:46-73]()
- **Annotation**: Methods like `add_span_annotation` allow users to attach feedback (LLM, CODE, or HUMAN) to specific spans. This is commonly used for human-in-the-loop feedback or recording programmatic evaluation results. [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:365-420](), [tutorials/human_feedback/chatbot_with_human_feedback.ipynb:157-168]()

| Method | Purpose | Implementation File |
|--------|---------|---------------------|
| `get_spans` | Retrieves a list of span objects. | [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:236-250]() |
| `get_spans_dataframe` | Retrieves spans as a pandas DataFrame. | [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:171-215]() |
| `log_spans` | Uploads raw span data to a project. | [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:604-620]() |
| `add_span_annotation` | Adds a single evaluation/feedback entry. | [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:365-420]() |

Sources: [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py:106-160](), [tests/integration/client/test_spans.py:37-97]()

### 2. Datasets and Experiments
The `Datasets` resource manages versioned collections of examples, while the `Experiments` resource handles the execution of tasks against those datasets.

- **Dataset Management**: The `Dataset` class provides a `to_dataframe()` method for easy local manipulation of examples. [packages/phoenix-client/src/phoenix/client/resources/datasets/__init__.py:179-202]()
- **Experiment Execution**: The `run_experiment` function automates the process of iterating over a dataset, executing a task function, and running evaluators. It supports `repetitions` and `retries` for robustness. [packages/phoenix-client/src/phoenix/client/experiments/__init__.py:17-108]()
- **Task Binding**: Tasks can dynamically bind arguments like `input`, `expected`, `metadata`, and `example` from dataset examples using signature inspection. [packages/phoenix-client/src/phoenix/client/experiments/__init__.py:42-53](), [packages/phoenix-client/src/phoenix/client/resources/experiments/types.py:219-243]()

### Data Flow: Experiment Execution
```mermaid
sequenceDiagram
    participant User
    participant run_experiment as "run_experiment()"
    participant Executor as "Sync/AsyncExecutor"
    participant Task as "User Task Function"
    participant Server as "Phoenix Server"

    User->>run_experiment: Call with dataset and task
    run_experiment->>Server: Fetch dataset examples
    run_experiment->>Executor: Schedule tasks
    loop For each Example
        Executor->>Task: Execute(input, metadata)
        Task-->>Executor: JSON Output
        Executor->>Server: POST v1/experiments/{id}/runs
        Note over Executor, Server: Logs task output & latency
    end
    run_experiment-->>User: Return RanExperiment object
```
Sources: [packages/phoenix-client/src/phoenix/client/experiments/__init__.py:17-108](), [packages/phoenix-client/src/phoenix/client/resources/experiments/__init__.py:159-180]()

### 3. Prompt Management
The `Prompts` resource allows users to manage prompt templates and versions. It includes helpers for converting to and from common SDK formats like OpenAI and Anthropic.

- **SDK Interop**: Functions like `create_prompt_version_from_openai` and `create_prompt_version_from_anthropic` simplify importing existing prompts into Phoenix. [packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py:110-148](), [packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py:119-161]()
- **Version Retrieval**: `get` retrieves a `PromptVersion` which includes the template, model provider, and parameters. [packages/phoenix-client/src/phoenix/client/resources/prompts/__init__.py:86-125]()
- **Tag Management**: The `PromptVersionTags` class handles associating labels like "production" or "staging" with specific prompt versions. [packages/phoenix-client/src/phoenix/client/resources/prompts/__init__.py:173-191]()

Sources: [packages/phoenix-client/src/phoenix/client/resources/prompts/__init__.py:20-71](), [packages/phoenix-client/src/phoenix/client/types/prompts.py:10-50]()

---

## Implementation Details

### Span Modification and Capture
For experiments, the client must associate the traces generated by a task with the experiment run. It uses a monkey-patching mechanism to automatically inject resource attributes (like experiment IDs) into spans created during execution.

- **capture_spans**: A context manager that uses `_ACTIVE_MODIFIER` (a `ContextVar`) to store a `SpanModifier`. [packages/phoenix-client/src/phoenix/client/resources/experiments/__init__.py:127-141]()
- **Monkey Patching**: The `_monkey_patch_span_init` function patches `opentelemetry.sdk.trace.ReadableSpan.__init__`. When a new span is initialized, it checks the `ContextVar` and merges the experiment's resource attributes into the span. [packages/phoenix-client/src/phoenix/client/resources/experiments/__init__.py:91-125]()

### Data Flow: SDK to Server
The client acts as a bridge between high-level Python objects and the Phoenix server's OTLP and REST collectors.

```mermaid
graph LR
    subgraph "Python Application Space"
        Task["User Task Function"]
        OTEL["opentelemetry.sdk.trace.Span"]
    end

    subgraph "arize-phoenix-client Internal"
        Mod["class SpanModifier"]
        Patch["_patched_span_init"]
    end

    subgraph "Phoenix Server Space"
        OTLP["OTLP /v1/traces"]
        REST["REST /v1/experiments"]
    end

    Task -- "starts span" --> OTEL
    Patch -- "intercepts __init__" --> OTEL
    Mod -- "merges ResourceAttributes" --> Patch
    OTEL -- "exports via OTLPSpanExporter" --> OTLP
    Task -- "returns result" --> REST
```
Sources: [packages/phoenix-client/src/phoenix/client/resources/experiments/__init__.py:65-100](), [packages/phoenix-client/src/phoenix/client/resources/experiments/__init__.py:159-180]()

### Rate Limiting and Retries
When running large experiments or evaluations, the client utilizes a `RateLimiter` to handle `RateLimitErrors` (e.g., from OpenAI). It supports adaptive throttling and a configurable number of retries for failed tasks.

- **RateLimiter**: Implements token-bucket logic for throttling requests to external providers during experiment runs. [packages/phoenix-client/src/phoenix/client/utils/rate_limiters.py:1-20]()
- **Retry Logic**: Controlled via the `retries` parameter in `run_experiment`, which leverages the `SyncExecutor` or `AsyncExecutor` to manage task lifecycles. [packages/phoenix-client/src/phoenix/client/experiments/__init__.py:30-32](), [packages/phoenix-client/src/phoenix/client/utils/executors.py:10-50]()

Sources: [packages/phoenix-client/src/phoenix/client/experiments/__init__.py:17-108](), [packages/phoenix-client/src/phoenix/client/utils/executors.py:10-50]()

---

# Page: Python OpenTelemetry (arize-phoenix-otel)

# Python OpenTelemetry (arize-phoenix-otel)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [app/src/pages/auth/AuthLayout.tsx](app/src/pages/auth/AuthLayout.tsx)
- [docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx](docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx)
- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx](docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx)
- [docs/phoenix/sdk-api-reference/typescript/overview.mdx](docs/phoenix/sdk-api-reference/typescript/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx)
- [internal_docs/specs/playground.md](internal_docs/specs/playground.md)
- [internal_docs/specs/prompts.md](internal_docs/specs/prompts.md)
- [internal_docs/specs/server_evaluators.md](internal_docs/specs/server_evaluators.md)
- [js/packages/phoenix-client/README.md](js/packages/phoenix-client/README.md)
- [js/packages/phoenix-config/README.md](js/packages/phoenix-config/README.md)
- [js/packages/phoenix-evals/README.md](js/packages/phoenix-evals/README.md)
- [js/packages/phoenix-mcp/README.md](js/packages/phoenix-mcp/README.md)
- [js/packages/phoenix-mcp/src/index.ts](js/packages/phoenix-mcp/src/index.ts)
- [js/packages/phoenix-mcp/src/projectTools.ts](js/packages/phoenix-mcp/src/projectTools.ts)
- [js/packages/phoenix-otel/README.md](js/packages/phoenix-otel/README.md)
- [kustomize/README.md](kustomize/README.md)
- [packages/phoenix-client/CHANGELOG.md](packages/phoenix-client/CHANGELOG.md)
- [packages/phoenix-client/README.md](packages/phoenix-client/README.md)
- [packages/phoenix-client/pyproject.toml](packages/phoenix-client/pyproject.toml)
- [packages/phoenix-evals/CHANGELOG.md](packages/phoenix-evals/CHANGELOG.md)
- [packages/phoenix-evals/README.md](packages/phoenix-evals/README.md)
- [packages/phoenix-evals/docs/source/api/evals.rst](packages/phoenix-evals/docs/source/api/evals.rst)
- [packages/phoenix-evals/docs/source/index.md](packages/phoenix-evals/docs/source/index.md)
- [packages/phoenix-evals/pyproject.toml](packages/phoenix-evals/pyproject.toml)
- [packages/phoenix-otel/CHANGELOG.md](packages/phoenix-otel/CHANGELOG.md)
- [packages/phoenix-otel/README.md](packages/phoenix-otel/README.md)
- [packages/phoenix-otel/pyproject.toml](packages/phoenix-otel/pyproject.toml)
- [packages/phoenix-otel/src/phoenix/otel/__init__.py](packages/phoenix-otel/src/phoenix/otel/__init__.py)
- [packages/phoenix-otel/src/phoenix/otel/otel.py](packages/phoenix-otel/src/phoenix/otel/otel.py)
- [packages/phoenix-otel/tests/__init__.py](packages/phoenix-otel/tests/__init__.py)
- [packages/phoenix-otel/tests/test_exports.py](packages/phoenix-otel/tests/test_exports.py)
- [packages/phoenix-otel/tests/test_otel.py](packages/phoenix-otel/tests/test_otel.py)
- [packages/phoenix-otel/tests/test_settings.py](packages/phoenix-otel/tests/test_settings.py)
- [pyproject.toml](pyproject.toml)
- [release-please-config.json](release-please-config.json)
- [requirements/packages/phoenix-evals.txt](requirements/packages/phoenix-evals.txt)
- [requirements/type-check.txt](requirements/type-check.txt)
- [requirements/unit-tests.txt](requirements/unit-tests.txt)
- [scripts/docker/devops/oidc-server/frontend/package.json](scripts/docker/devops/oidc-server/frontend/package.json)
- [scripts/docker/devops/oidc-server/frontend/src/contexts/ThemeContext.tsx](scripts/docker/devops/oidc-server/frontend/src/contexts/ThemeContext.tsx)
- [scripts/docker/devops/oidc-server/package.json](scripts/docker/devops/oidc-server/package.json)
- [scripts/docker/devops/smtp-server/package.json](scripts/docker/devops/smtp-server/package.json)
- [src/phoenix/__init__.py](src/phoenix/__init__.py)
- [src/phoenix/tests/test_config.py](src/phoenix/tests/test_config.py)
- [src/phoenix/version.py](src/phoenix/version.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/unit/conftest.py](tests/unit/conftest.py)
- [uv.lock](uv.lock)

</details>



The `arize-phoenix-otel` package provides a lightweight wrapper around OpenTelemetry primitives with Phoenix-aware defaults. It simplifies the configuration of OpenTelemetry tracing for Phoenix users by providing drop-in replacements for standard OpenTelemetry classes and a streamlined registration function that handles protocol inference, authentication, and auto-instrumentation.

For information about the full Phoenix platform server and UI, see [1. Phoenix Overview](). For REST/GraphQL API access, see [3.1. Python Client (arize-phoenix-client)](). For evaluation frameworks, see [3.3. Python Evaluations (arize-phoenix-evals)]().

## Package Overview

The `arize-phoenix-otel` package (version 0.16.1) is a standalone Python package that depends on OpenTelemetry SDK components and OpenInference semantic conventions [packages/phoenix-otel/pyproject.toml:2-24](). It provides Phoenix-specific defaults while maintaining full compatibility with the OpenTelemetry ecosystem.

**Key Dependencies:**
- `opentelemetry-sdk` - Core OpenTelemetry SDK [packages/phoenix-otel/pyproject.toml:29-29]()
- `opentelemetry-exporter-otlp` - OTLP exporters [packages/phoenix-otel/pyproject.toml:27-27]()
- `openinference-semantic-conventions` - OpenInference resource attributes [packages/phoenix-otel/pyproject.toml:30-30]()
- `openinference-instrumentation` - Auto-instrumentation framework [packages/phoenix-otel/pyproject.toml:31-31]()

**Supported Python Versions:** 3.10 - 3.14 [packages/phoenix-otel/pyproject.toml:5-5]()

Sources: [packages/phoenix-otel/pyproject.toml:1-34](), [packages/phoenix-otel/README.md:1-58](), [packages/phoenix-otel/CHANGELOG.md:1-10]()

## Module Structure

The package architecture maps Phoenix-specific logic onto standard OpenTelemetry components. It re-exports OpenInference helpers and semantic conventions to provide a unified tracing surface [packages/phoenix-otel/src/phoenix/otel/__init__.py:1-25]().

Title: arize-phoenix-otel Module Architecture
```mermaid
graph TB
    subgraph "phoenix.otel Package"
        Init["__init__.py<br/>Public API"]
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
    
    Init --> Otel
    Init --> Settings
    Init --> TracerProvider
    Init --> HTTPExporter
    Init --> GRPCExporter
    Init --> SimpleProc
    Init --> BatchProc
    Init --> Register
    
    TracerProvider -.wraps.-> OTelProvider
    HTTPExporter -.wraps.-> OTelHTTP
    GRPCExporter -.wraps.-> OTelGRPC
    SimpleProc -.wraps.-> OTelSimple
    BatchProc -.wraps.-> OTelBatch
    
    Register --> TracerProvider
    Register --> HTTPExporter
    Register --> GRPCExporter
```

Sources: [packages/phoenix-otel/src/phoenix/otel/otel.py:10-23](), [packages/phoenix-otel/src/phoenix/otel/settings.py:1-17](), [packages/phoenix-otel/src/phoenix/otel/__init__.py:1-60]()

## Core Components

### The `register()` Function

The `register()` function is the primary entry point for configuring OpenTelemetry tracing with Phoenix defaults [packages/phoenix-otel/src/phoenix/otel/otel.py:64-76](). It creates and configures a `TracerProvider` with automatic protocol inference, authentication, and optional auto-instrumentation.

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

Sources: [packages/phoenix-otel/src/phoenix/otel/otel.py:145-243](), [packages/phoenix-otel/src/phoenix/otel/settings.py:30-31]()

### TracerProvider

The `TracerProvider` class is a drop-in replacement for the OpenTelemetry `TracerProvider` with Phoenix-aware defaults. It extends the OpenInference `TracerProvider` to add verbose logging and default configuration [packages/phoenix-otel/src/phoenix/otel/otel.py:246-250]().

**Key Features:**
- Automatically merges project name into resource attributes [packages/phoenix-otel/src/phoenix/otel/otel.py:151-158]().
- Provides detailed configuration logging when `verbose=True` [packages/phoenix-otel/src/phoenix/otel/otel.py:263-320]().
- Re-exports OpenInference decorators like `@tracer.chain` and `@tracer.tool` [packages/phoenix-otel/README.md:164-171]().
- Re-exports context management helpers like `using_session`, `using_user`, and `using_tags` [packages/phoenix-otel/src/phoenix/otel/__init__.py:1-9]().

Sources: [packages/phoenix-otel/src/phoenix/otel/otel.py:246-320](), [packages/phoenix-otel/src/phoenix/otel/__init__.py:1-60]()

### Span Exporters

The package provides two span exporter classes with Phoenix-aware defaults:

#### HTTPSpanExporter
Exports spans using OTLP over HTTP/protobuf protocol. It defaults to using the `PHOENIX_COLLECTOR_ENDPOINT` environment variable [packages/phoenix-otel/src/phoenix/otel/otel.py:323-333]().

#### GRPCSpanExporter
Exports spans using OTLP over gRPC protocol. It defaults to port 4317 if no endpoint is specified [packages/phoenix-otel/src/phoenix/otel/otel.py:393-403]().

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

Sources: [packages/phoenix-otel/src/phoenix/otel/otel.py:36-61](), [packages/phoenix-otel/src/phoenix/otel/otel.py:549-564]()

## Configuration System

### Environment Variables

The package reads configuration from environment variables defined in `settings.py`:

| Environment Variable | Purpose | Default |
|---------------------|---------|---------|
| `PHOENIX_COLLECTOR_ENDPOINT` | Collector endpoint URL | `None` (standard OTel fallback) [packages/phoenix-otel/src/phoenix/otel/settings.py:12-34]() |
| `PHOENIX_PROJECT_NAME` | Project name for traces | `"default"` [packages/phoenix-otel/src/phoenix/otel/settings.py:14-44]() |
| `PHOENIX_CLIENT_HEADERS` | Custom headers (W3C Baggage format) | `None` [packages/phoenix-otel/src/phoenix/otel/settings.py:15-59]() |
| `PHOENIX_API_KEY` | API key for authentication | `None` [packages/phoenix-otel/src/phoenix/otel/settings.py:16-76]() |
| `PHOENIX_GRPC_PORT` | gRPC port override | `4317` [packages/phoenix-otel/src/phoenix/otel/settings.py:13-93]() |

Title: Environment Configuration Flow
```mermaid
graph TB
    GetEndpoint["get_env_collector_endpoint()"]
    CheckPhoenix{"PHOENIX_COLLECTOR_ENDPOINT<br/>set?"}
    UsePhoenix["Return PHOENIX_COLLECTOR_ENDPOINT"]
    CheckOtel{"OTEL_EXPORTER_OTLP_ENDPOINT<br/>set?"}
    UseOtel["Return OTEL_EXPORTER_OTLP_ENDPOINT"]
    ReturnNone["Return None"]
    
    GetProjectName["get_env_project_name()"]
    CheckProjectEnv{"PHOENIX_PROJECT_NAME<br/>set?"}
    UseProject["Return PHOENIX_PROJECT_NAME"]
    DefaultProject["Return 'default'"]
    
    GetEndpoint --> CheckPhoenix
    CheckPhoenix -->|Yes| UsePhoenix
    CheckPhoenix -->|No| CheckOtel
    CheckOtel -->|Yes| UseOtel
    CheckOtel -->|No| ReturnNone
    
    GetProjectName --> CheckProjectEnv
    CheckProjectEnv -->|Yes| UseProject
    CheckProjectEnv -->|No| DefaultProject
```

Sources: [packages/phoenix-otel/src/phoenix/otel/settings.py:1-125]()

## Auto-Instrumentation

The `register()` function supports automatic instrumentation of installed OpenInference libraries through Python entry points [packages/phoenix-otel/src/phoenix/otel/otel.py:184-226](). This allows users to trace popular frameworks like OpenAI, LangChain, and LlamaIndex with zero code changes [packages/phoenix-otel/README.md:77-85]().

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

Sources: [packages/phoenix-otel/src/phoenix/otel/otel.py:184-226](), [packages/phoenix-otel/README.md:77-85]()

## Usage Examples

### Production Setup with Auto-Instrumentation

```python
from phoenix.otel import register

tracer_provider = register(
    auto_instrument=True,  # Auto-trace all OpenInference libraries
    batch=True,            # Use batching for efficiency
    project_name="prod-app",
    api_key="your-api-key"
)
```

### Manual Configuration

For advanced use cases, use Phoenix OTEL components directly:

```python
from phoenix.otel import TracerProvider, BatchSpanProcessor, HTTPSpanExporter

tracer_provider = TracerProvider()
exporter = HTTPSpanExporter(endpoint="http://localhost:6006/v1/traces")
processor = BatchSpanProcessor(span_exporter=exporter)
tracer_provider.add_span_processor(processor)
```

Sources: [packages/phoenix-otel/README.md:129-152](), [packages/phoenix-otel/src/phoenix/otel/otel.py:106-143]()

---

# Page: Python Evaluations (arize-phoenix-evals)

# Python Evaluations (arize-phoenix-evals)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [js/packages/phoenix-evals/src/__generated__/default_templates/index.ts](js/packages/phoenix-evals/src/__generated__/default_templates/index.ts)
- [js/packages/phoenix-evals/src/llm/createToolSelectionEvaluator.ts](js/packages/phoenix-evals/src/llm/createToolSelectionEvaluator.ts)
- [js/packages/phoenix-evals/src/llm/index.ts](js/packages/phoenix-evals/src/llm/index.ts)
- [packages/phoenix-evals/src/phoenix/evals/__generated__/classification_evaluator_configs/__init__.py](packages/phoenix-evals/src/phoenix/evals/__generated__/classification_evaluator_configs/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/__generated__/classification_evaluator_configs/_tool_invocation_classification_evaluator_config.py](packages/phoenix-evals/src/phoenix/evals/__generated__/classification_evaluator_configs/_tool_invocation_classification_evaluator_config.py)
- [packages/phoenix-evals/src/phoenix/evals/__generated__/classification_evaluator_configs/_tool_selection_classification_evaluator_config.py](packages/phoenix-evals/src/phoenix/evals/__generated__/classification_evaluator_configs/_tool_selection_classification_evaluator_config.py)
- [packages/phoenix-evals/src/phoenix/evals/__init__.py](packages/phoenix-evals/src/phoenix/evals/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/evaluators.py](packages/phoenix-evals/src/phoenix/evals/evaluators.py)
- [packages/phoenix-evals/src/phoenix/evals/executors.py](packages/phoenix-evals/src/phoenix/evals/executors.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/__init__.py](packages/phoenix-evals/src/phoenix/evals/llm/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/__init__.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/anthropic/adapter.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/anthropic/adapter.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/google/adapter.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/google/adapter.py)
- [packages/phoenix-evals/src/phoenix/evals/llm/adapters/google/factories.py](packages/phoenix-evals/src/phoenix/evals/llm/adapters/google/factories.py)
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
- [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py](packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py)
- [packages/phoenix-evals/src/phoenix/evals/metrics/matches_regex.py](packages/phoenix-evals/src/phoenix/evals/metrics/matches_regex.py)
- [packages/phoenix-evals/src/phoenix/evals/tracing.py](packages/phoenix-evals/src/phoenix/evals/tracing.py)
- [packages/phoenix-evals/src/phoenix/evals/utils.py](packages/phoenix-evals/src/phoenix/evals/utils.py)
- [packages/phoenix-evals/tests/phoenix/evals/llm/test_prompts.py](packages/phoenix-evals/tests/phoenix/evals/llm/test_prompts.py)
- [packages/phoenix-evals/tests/phoenix/evals/metrics/test_matches_regex.py](packages/phoenix-evals/tests/phoenix/evals/metrics/test_matches_regex.py)
- [packages/phoenix-evals/tests/phoenix/evals/test_evaluators.py](packages/phoenix-evals/tests/phoenix/evals/test_evaluators.py)
- [packages/phoenix-evals/tests/phoenix/evals/test_imports.py](packages/phoenix-evals/tests/phoenix/evals/test_imports.py)
- [packages/phoenix-evals/tests/phoenix/evals/test_utils.py](packages/phoenix-evals/tests/phoenix/evals/test_utils.py)
- [prompts/classification_evaluator_configs/TOOL_INVOCATION_CLASSIFICATION_EVALUATOR_CONFIG.yaml](prompts/classification_evaluator_configs/TOOL_INVOCATION_CLASSIFICATION_EVALUATOR_CONFIG.yaml)
- [prompts/classification_evaluator_configs/TOOL_SELECTION_CLASSIFICATION_EVALUATOR_CONFIG.yaml](prompts/classification_evaluator_configs/TOOL_SELECTION_CLASSIFICATION_EVALUATOR_CONFIG.yaml)
- [prompts/formatters/server.yaml](prompts/formatters/server.yaml)
- [src/phoenix/__generated__/classification_evaluator_configs/__init__.py](src/phoenix/__generated__/classification_evaluator_configs/__init__.py)
- [src/phoenix/__generated__/classification_evaluator_configs/_tool_invocation_classification_evaluator_config.py](src/phoenix/__generated__/classification_evaluator_configs/_tool_invocation_classification_evaluator_config.py)
- [src/phoenix/__generated__/classification_evaluator_configs/_tool_selection_classification_evaluator_config.py](src/phoenix/__generated__/classification_evaluator_configs/_tool_selection_classification_evaluator_config.py)
- [src/phoenix/server/api/helpers/substitutions/server.yaml](src/phoenix/server/api/helpers/substitutions/server.yaml)
- [tests/unit/server/api/helpers/test_substitutions.py](tests/unit/server/api/helpers/test_substitutions.py)

</details>



The `arize-phoenix-evals` package provides a lightweight, composable evaluation framework for LLM applications. It offers building blocks for creating and running automatic evaluations using LLM-based judges, code-based metrics, and pre-built evaluators. The package is instrumented for OpenTelemetry tracing and supports multiple LLM providers through a unified adapter system.

**Scope**: This document covers the Python evaluation framework (`arize-phoenix-evals`). For the Phoenix client used to log evaluation results, see page [3.1]().

**Package Version**: [packages/phoenix-evals/src/phoenix/evals/__init__.py:23-23]()

## Architecture Overview

The evaluation framework consists of four main layers: evaluator abstractions, LLM provider adapters, a templating system, and an execution engine.

### Evaluation Data Flow
The following diagram illustrates how data flows from user input through the evaluation engine to produce scores, mapping natural language concepts to code entities.

Title: Evaluation Data Flow
```mermaid
graph TB
    subgraph "Natural_Language_&_Data"
        InputDF["pandas.DataFrame"]
        PromptText["Natural Language Prompt"]
    end
    
    subgraph "Evaluator_Layer"
        Evaluator["Evaluator (Abstract Base)"]
        LLMEvaluator["LLMEvaluator"]
        ClassEval["ClassificationEvaluator"]
        CreateEval["create_evaluator()"]
        CreateClass["create_classifier()"]
    end
    
    subgraph "LLM_Abstraction_Space"
        LLM_Class["LLM (Unified Wrapper)"]
        Registry["PROVIDER_REGISTRY"]
        Adapter["BaseLLMAdapter"]
        LiteLLM["LiteLLMAdapter"]
        OpenAI["OpenAIAdapter"]
    end
    
    subgraph "Execution_&_Tracing"
        AsyncExec["AsyncExecutor"]
        Controller["ConcurrencyController"]
        Trace["@trace decorator"]
    end
    
    InputDF --> CreateEval
    InputDF --> CreateClass
    PromptText --> LLMEvaluator
    
    CreateEval --> LLMEvaluator
    CreateClass --> ClassEval
    
    LLMEvaluator --> LLM_Class
    LLM_Class --> Registry
    Registry --> Adapter
    Adapter --> LiteLLM
    Adapter --> OpenAI
    
    LLMEvaluator --> AsyncExec
    AsyncExec --> Controller
    LLM_Class --> Trace
    
    ClassEval --> Score["Score Object"]
```

**Sources**: [packages/phoenix-evals/src/phoenix/evals/evaluators.py:328-330](), [packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py:97-122](), [packages/phoenix-evals/src/phoenix/evals/executors.py:170-196]()

## Core Abstractions

### Evaluator Base Class

The `Evaluator` class is an abstract base class that defines the interface for all evaluation logic.

| Class | Role | Definition |
|-------|------|------------|
| `Evaluator` | Abstract base class for all evaluators. | [packages/phoenix-evals/src/phoenix/evals/evaluators.py:328-330]() |
| `LLMEvaluator` | Uses an LLM to perform evaluation based on a prompt template. | [packages/phoenix-evals/src/phoenix/evals/evaluators.py:535-537]() |
| `ClassificationEvaluator` | Specialization of `LLMEvaluator` for categorical labels. | [packages/phoenix-evals/src/phoenix/evals/evaluators.py:738-740]() |

**Key Features**:
- **Input Mapping**: Uses `remap_eval_input` to extract values from nested data structures using JSONPath or callable mappings [packages/phoenix-evals/src/phoenix/evals/utils.py:175-187]().
- **Variable Binding**: `bind_evaluator` allows partial application of template variables for reusable configurations [packages/phoenix-evals/src/phoenix/evals/evaluators.py:1260-1262]().
- **Async Support**: Evaluators implement `async_evaluate` for non-blocking execution [packages/phoenix-evals/src/phoenix/evals/evaluators.py:382-384]().

### Score Model

The `Score` class represents the result of an evaluation. It is a frozen dataclass containing:
- `name`: The name of the evaluation metric [packages/phoenix-evals/src/phoenix/evals/evaluators.py:209-209]().
- `score`: A numeric value (float/int) [packages/phoenix-evals/src/phoenix/evals/evaluators.py:210-210]().
- `label`: A categorical string label [packages/phoenix-evals/src/phoenix/evals/evaluators.py:211-211]().
- `explanation`: LLM-generated reasoning [packages/phoenix-evals/src/phoenix/evals/evaluators.py:212-212]().
- `metadata`: A dictionary of additional context [packages/phoenix-evals/src/phoenix/evals/evaluators.py:213-213]().
- `kind`: The type of evaluator (e.g., "llm", "code", "human") [packages/phoenix-evals/src/phoenix/evals/evaluators.py:214-214]().

**Sources**: [packages/phoenix-evals/src/phoenix/evals/evaluators.py:158-216]()

## LLM Provider Support

The `LLM` class acts as a unified interface for various providers, delegating to specific adapters.

### Provider Registry and Adapters
Phoenix uses a registration system to manage model adapters.

Title: Provider and Adapter Registry
```mermaid
graph LR
    subgraph "Code_Entity_Space"
        LLM_Wrapper["LLM class"]
        PR["ProviderRegistry"]
        AR["AdapterRegistry"]
        
        subgraph "Adapters"
            OAI["OpenAIAdapter"]
            LIT["LiteLLMAdapter"]
            LC["LangChainModelAdapter"]
        end
    end
    
    LLM_Wrapper --> PR
    PR --> AR
    AR --> OAI
    AR --> LIT
    AR --> LC
```

- **OpenAIAdapter**: Supports OpenAI and Azure OpenAI [packages/phoenix-evals/src/phoenix/evals/llm/adapters/openai/adapter.py:60-60]().
- **LiteLLMAdapter**: Provides access to 100+ providers via the LiteLLM library [packages/phoenix-evals/src/phoenix/evals/llm/adapters/litellm/adapter.py:66-66]().
- **LangChainModelAdapter**: Allows using existing LangChain chat models as evaluators [packages/phoenix-evals/src/phoenix/evals/llm/adapters/langchain/adapter.py:63-63]().

**Sources**: [packages/phoenix-evals/src/phoenix/evals/llm/registries.py:39-147](), [packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py:97-122]()

### Execution & Concurrency
The framework includes an `AsyncExecutor` and `ConcurrencyController` to manage API rate limits.
- **ConcurrencyController**: Implements an AIMD (Additive Increase/Multiplicative Decrease) algorithm to dynamically adjust request rates based on success/failure [packages/phoenix-evals/src/phoenix/evals/executors.py:73-86]().
- **AsyncExecutor**: Manages the producer-consumer pattern for batch evaluations [packages/phoenix-evals/src/phoenix/evals/executors.py:170-196]().

**Sources**: [packages/phoenix-evals/src/phoenix/evals/executors.py:73-196]()

## Built-in Metrics

Phoenix provides several pre-built evaluators for common tasks.

| Evaluator | Purpose | Implementation |
|-----------|---------|----------------|
| `FaithfulnessEvaluator` | Detects factual consistency between context and response. | [packages/phoenix-evals/src/phoenix/evals/metrics/faithfulness.py:1]() |
| `CorrectnessEvaluator` | Evaluates if a response is correct relative to a reference. | [packages/phoenix-evals/src/phoenix/evals/metrics/correctness.py:1]() |
| `DocumentRelevanceEvaluator` | Evaluates if a document is relevant to the query. | [packages/phoenix-evals/src/phoenix/evals/metrics/document_relevance.py:1]() |
| `ToolSelectionEvaluator` | Validates if the correct tool was chosen. | [packages/phoenix-evals/src/phoenix/evals/metrics/tool_selection.py:1]() |
| `MatchesRegex` | Code-based evaluator for pattern matching. | [packages/phoenix-evals/src/phoenix/evals/metrics/matches_regex.py:1]() |
| `PrecisionRecallFScore` | Calculates classification metrics. | [packages/phoenix-evals/src/phoenix/evals/metrics/precision_recall.py:8]() |

**Sources**: [packages/phoenix-evals/src/phoenix/evals/metrics/__init__.py:1-27]()

## Templating and Data Handling

### Prompt Templates
Phoenix uses a flexible templating system for LLM prompts.
- `PromptTemplate`: Manages template rendering and variable substitution [packages/phoenix-evals/src/phoenix/evals/llm/prompts.py:1]().
- `SmartString`: A Pydantic type that ensures non-string values (like dictionaries or lists) are properly JSON-serialized before being inserted into a prompt [packages/phoenix-evals/src/phoenix/evals/evaluators.py:80-87]().

### Evaluation Execution
Users can evaluate entire datasets using `evaluate_dataframe` or `async_evaluate_dataframe`.
- `evaluate_dataframe`: Synchronous batch evaluation [packages/phoenix-evals/src/phoenix/evals/evaluators.py:18-18]().
- `async_evaluate_dataframe`: Asynchronous batch evaluation using the `AsyncExecutor` [packages/phoenix-evals/src/phoenix/evals/evaluators.py:14-14]().

**Sources**: [packages/phoenix-evals/src/phoenix/evals/evaluators.py:1-154](), [packages/phoenix-evals/src/phoenix/evals/llm/prompts.py:1]()

## Tracing and Instrumentation

Evaluations are instrumented using OpenTelemetry via the `@trace` decorator.
- **Span Metadata**: Evaluators attach metadata such as `evaluator.kind` and `evaluator.class` to spans [packages/phoenix-evals/src/phoenix/evals/evaluators.py:103-111]().
- **Span Inputs/Outputs**: Remapped inputs and generated `Score` objects are serialized to JSON and attached to the span attributes [packages/phoenix-evals/src/phoenix/evals/evaluators.py:113-121]().
- **LLM Tracing**: The `LLM` wrapper provides helper functions like `_get_prompt` and `_get_llm_model_name` to extract tracing attributes from bound arguments [packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py:19-70]().

**Sources**: [packages/phoenix-evals/src/phoenix/evals/tracing.py:34-34](), [packages/phoenix-evals/src/phoenix/evals/evaluators.py:91-121](), [packages/phoenix-evals/src/phoenix/evals/llm/wrapper.py:19-95]()

---

# Page: TypeScript Client

# TypeScript Client

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/experiments.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/experiments.mdx)
- [js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md](js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md)
- [js/examples/apps/demo-document-relevancy-experiment/package.json](js/examples/apps/demo-document-relevancy-experiment/package.json)
- [js/examples/apps/phoenix-experiment-runner/index.ts](js/examples/apps/phoenix-experiment-runner/index.ts)
- [js/examples/apps/phoenix-experiment-runner/package.json](js/examples/apps/phoenix-experiment-runner/package.json)
- [js/packages/phoenix-cli/CHANGELOG.md](js/packages/phoenix-cli/CHANGELOG.md)
- [js/packages/phoenix-cli/package.json](js/packages/phoenix-cli/package.json)
- [js/packages/phoenix-client/CHANGELOG.md](js/packages/phoenix-client/CHANGELOG.md)
- [js/packages/phoenix-client/examples/experiment_trace_evaluator.ts](js/packages/phoenix-client/examples/experiment_trace_evaluator.ts)
- [js/packages/phoenix-client/package.json](js/packages/phoenix-client/package.json)
- [js/packages/phoenix-client/src/client.ts](js/packages/phoenix-client/src/client.ts)
- [js/packages/phoenix-client/src/constants/serverRequirements.ts](js/packages/phoenix-client/src/constants/serverRequirements.ts)
- [js/packages/phoenix-client/src/experiments/index.ts](js/packages/phoenix-client/src/experiments/index.ts)
- [js/packages/phoenix-client/src/experiments/logging.ts](js/packages/phoenix-client/src/experiments/logging.ts)
- [js/packages/phoenix-client/src/experiments/resumeEvaluation.ts](js/packages/phoenix-client/src/experiments/resumeEvaluation.ts)
- [js/packages/phoenix-client/src/experiments/resumeExperiment.ts](js/packages/phoenix-client/src/experiments/resumeExperiment.ts)
- [js/packages/phoenix-client/src/experiments/runExperiment.ts](js/packages/phoenix-client/src/experiments/runExperiment.ts)
- [js/packages/phoenix-client/src/logger.ts](js/packages/phoenix-client/src/logger.ts)
- [js/packages/phoenix-client/src/sessions/getSession.ts](js/packages/phoenix-client/src/sessions/getSession.ts)
- [js/packages/phoenix-client/src/sessions/listSessions.ts](js/packages/phoenix-client/src/sessions/listSessions.ts)
- [js/packages/phoenix-client/src/sessions/sessionUtils.ts](js/packages/phoenix-client/src/sessions/sessionUtils.ts)
- [js/packages/phoenix-client/src/spans/getSpanAnnotations.ts](js/packages/phoenix-client/src/spans/getSpanAnnotations.ts)
- [js/packages/phoenix-client/src/spans/getSpans.ts](js/packages/phoenix-client/src/spans/getSpans.ts)
- [js/packages/phoenix-client/src/traces/index.ts](js/packages/phoenix-client/src/traces/index.ts)
- [js/packages/phoenix-client/src/types/experiments.ts](js/packages/phoenix-client/src/types/experiments.ts)
- [js/packages/phoenix-client/src/types/projects.ts](js/packages/phoenix-client/src/types/projects.ts)
- [js/packages/phoenix-client/src/types/sessions.ts](js/packages/phoenix-client/src/types/sessions.ts)
- [js/packages/phoenix-client/src/utils/noopLogger.ts](js/packages/phoenix-client/src/utils/noopLogger.ts)
- [js/packages/phoenix-client/test/experiments/resumeEvaluation.test.ts](js/packages/phoenix-client/test/experiments/resumeEvaluation.test.ts)
- [js/packages/phoenix-client/test/experiments/runExperiment.test.ts](js/packages/phoenix-client/test/experiments/runExperiment.test.ts)
- [js/packages/phoenix-client/test/sessions/getSession.test.ts](js/packages/phoenix-client/test/sessions/getSession.test.ts)
- [js/packages/phoenix-client/test/spans/getSpans.test.ts](js/packages/phoenix-client/test/spans/getSpans.test.ts)
- [js/packages/phoenix-config/CHANGELOG.md](js/packages/phoenix-config/CHANGELOG.md)
- [js/packages/phoenix-config/package.json](js/packages/phoenix-config/package.json)
- [js/packages/phoenix-config/src/env.test.ts](js/packages/phoenix-config/src/env.test.ts)
- [js/packages/phoenix-config/src/env.ts](js/packages/phoenix-config/src/env.ts)
- [js/packages/phoenix-evals/CHANGELOG.md](js/packages/phoenix-evals/CHANGELOG.md)
- [js/packages/phoenix-evals/package.json](js/packages/phoenix-evals/package.json)
- [js/packages/phoenix-mcp/CHANGELOG.md](js/packages/phoenix-mcp/CHANGELOG.md)
- [js/packages/phoenix-mcp/package.json](js/packages/phoenix-mcp/package.json)
- [js/packages/phoenix-otel/CHANGELOG.md](js/packages/phoenix-otel/CHANGELOG.md)
- [js/packages/phoenix-otel/package.json](js/packages/phoenix-otel/package.json)
- [packages/phoenix-client/src/phoenix/client/constants/server_requirements.py](packages/phoenix-client/src/phoenix/client/constants/server_requirements.py)
- [packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py](packages/phoenix-client/src/phoenix/client/resources/spans/__init__.py)
- [packages/phoenix-client/tests/client/resources/spans/test_spans.py](packages/phoenix-client/tests/client/resources/spans/test_spans.py)
- [tests/integration/client/test_spans.py](tests/integration/client/test_spans.py)
- [tutorials/human_feedback/chatbot_with_human_feedback.ipynb](tutorials/human_feedback/chatbot_with_human_feedback.ipynb)

</details>



The `@arizeai/phoenix-client` package is the TypeScript SDK for interacting with the Phoenix API. It provides typed interfaces for managing prompts, datasets, experiments, spans, and sessions. The client handles authentication, request/response serialization, and provides utilities for converting prompts between different LLM provider formats (OpenAI, Anthropic, Google, AWS, Vercel AI SDK). For information about the Python client equivalent, see [Python Client (arize-phoenix-client)](#3.1). For CLI usage built on this client, see [Command Line Interface (CLI)](#3.5).

**Sources:** [js/packages/phoenix-client/package.json:1-14](), [js/packages/phoenix-client/package.json:81-90]()

## Package Structure

The client is organized into modular exports with both CommonJS and ESM support. Each submodule provides focused functionality for a specific domain area.

### Module Organization

```mermaid
graph TB
    subgraph "@arizeai/phoenix-client Package"
        MainExport["index.ts"]
        PromptsModule["./prompts<br/>Prompt management"]
        SpansModule["./spans<br/>Span querying"]
        SessionsModule["./sessions<br/>Session management"]
        TracesModule["./traces<br/>Trace retrieval"]
        ExperimentsModule["./experiments<br/>Experiment execution"]
        DatasetsModule["./datasets<br/>Dataset management"]
        UtilsModule["./utils/*<br/>Helper functions"]
        TypesModule["./types/*<br/>Type definitions"]
    end
    
    subgraph "Core Dependencies"
        OpenAPIFetch["openapi-fetch<br/>HTTP client"]
        PhoenixOtel["@arizeai/phoenix-otel<br/>OpenTelemetry integration"]
        PhoenixConfig["@arizeai/phoenix-config<br/>Configuration utilities"]
        OpenInferenceConventions["@arizeai/openinference-semantic-conventions<br/>Semantic conventions"]
        GeneratedTypes["__generated__/api/v1.ts<br/>OpenAPI-generated types"]
    end
    
    subgraph "Optional Provider SDKs"
        OpenAISDK["openai<br/>OpenAI SDK"]
        AnthropicSDK["@anthropic-ai/sdk<br/>Anthropic SDK"]
        VercelAI["ai<br/>Vercel AI SDK"]
    end
    
    MainExport --> PromptsModule
    MainExport --> SpansModule
    MainExport --> SessionsModule
    MainExport --> TracesModule
    MainExport --> ExperimentsModule
    MainExport --> DatasetsModule
    MainExport --> UtilsModule
    MainExport --> TypesModule
    
    PromptsModule --> OpenAPIFetch
    PromptsModule --> GeneratedTypes
    PromptsModule --> OpenAISDK
    PromptsModule --> AnthropicSDK
    PromptsModule --> VercelAI
    
    ExperimentsModule --> PhoenixOtel
    ExperimentsModule --> OpenAPIFetch
    
    DatasetsModule --> OpenAPIFetch
    DatasetsModule --> GeneratedTypes
    
    SpansModule --> OpenAPIFetch
    SessionsModule --> OpenAPIFetch
    TracesModule --> OpenAPIFetch
    
    UtilsModule --> PhoenixConfig
    UtilsModule --> OpenInferenceConventions
```

**Sources:** [js/packages/phoenix-client/package.json:33-70](), [js/packages/phoenix-client/package.json:81-90]()

### Build System and Type Generation

The client uses a code-generation workflow to maintain type safety with the Phoenix REST API. It generates TypeScript definitions directly from the Phoenix OpenAPI schema using `openapi-typescript`.

```mermaid
graph LR
    OpenAPISchema["schemas/openapi.json<br/>Phoenix REST API Spec"]
    OpenAPITypeScript["openapi-typescript<br/>Code generator"]
    GeneratedTypes["src/__generated__/api/v1.ts<br/>Generated TypeScript types"]
    ClientSource["src/**/*.ts<br/>Client implementation"]
    TSCompiler["TypeScript Compiler<br/>tsc"]
    
    OutputCJS["dist/src/**/*.js<br/>CommonJS output"]
    OutputESM["dist/esm/**/*.js<br/>ESM output"]
    OutputTypes["dist/src/**/*.d.ts<br/>Type declarations"]
    
    OpenAPISchema --> OpenAPITypeScript
    OpenAPITypeScript --> GeneratedTypes
    GeneratedTypes --> ClientSource
    ClientSource --> TSCompiler
    TSCompiler --> OutputCJS
    TSCompiler --> OutputESM
    TSCompiler --> OutputTypes
```

**Sources:** [js/packages/phoenix-client/package.json:75-86](), [js/packages/phoenix-client/package.json:107-107]()

## Client Initialization

The client supports flexible configuration through environment variables and constructor parameters. It includes server version gating to ensure compatibility between the client and the Phoenix server instance. The client reads the server version from response headers and validates it against minimum version requirements before calling newer API routes.

| Configuration Method | Environment Variable | Constructor Parameter | Default |
|---------------------|---------------------|----------------------|---------|
| API endpoint | `PHOENIX_CLIENT_BASE_URL` | `baseURL` | `http://localhost:6006` |
| API key | `PHOENIX_API_KEY` | `apiKey` | `undefined` |
| Headers | - | `headers` | `{}` |

The client reads configuration in this priority order:
1. Constructor parameters (highest priority)
2. Environment variables (managed via `@arizeai/phoenix-config`)
3. Default values (lowest priority)

**Sources:** [js/packages/phoenix-client/CHANGELOG.md:140-141](), [js/packages/phoenix-client/package.json:90-91](), [js/packages/phoenix-client/src/client.ts:1-20]()

## Prompt Management

The prompts module provides functionality for managing prompt templates with versioning, tagging, and multi-provider format conversion.

### Prompt Operations Flow

```mermaid
graph TB
    subgraph "Client API Methods"
        PullPrompt["pullPrompt(identifier, options)<br/>Fetch prompt by name/ID"]
        PushPrompt["pushPrompt(promptData)<br/>Create/update prompt"]
        ListPrompts["listPrompts()<br/>List all prompts"]
        GetPrompt["getPrompt(identifier, options)<br/>Get specific version"]
    end
    
    subgraph "Prompt Conversion Utilities"
        ToOpenAI["toOpenAI()<br/>Convert to OpenAI format"]
        ToAnthropic["toAnthropic()<br/>Convert to Anthropic format"]
        ToVercelAI["toVercelAI()<br/>Convert to AI SDK format"]
        ToGoogle["toGoogle()<br/>Convert to Google format"]
        ToAWS["toAWS()<br/>Convert to Bedrock format"]
    end
    
    subgraph "Version and Tag Selection"
        VersionFilter["versionId filter<br/>Specific version"]
        TagFilter["tag filter<br/>Tagged version"]
        LatestDefault["Latest version<br/>Default behavior"]
    end
    
    subgraph "Prompt Structure"
        PromptTemplate["Prompt Template<br/>messages, tools, params"]
        PromptMetadata["Metadata<br/>name, description, tags"]
        InvocationParams["Invocation Parameters<br/>temperature, maxTokens, etc."]
    end
    
    PullPrompt --> VersionFilter
    PullPrompt --> TagFilter
    PullPrompt --> LatestDefault
    
    VersionFilter --> PromptTemplate
    TagFilter --> PromptTemplate
    LatestDefault --> PromptTemplate
    
    PromptTemplate --> PromptMetadata
    PromptTemplate --> InvocationParams
    
    PromptTemplate --> ToOpenAI
    PromptTemplate --> ToAnthropic
    PromptTemplate --> ToVercelAI
    PromptTemplate --> ToGoogle
    PromptTemplate --> ToAWS
    
    PushPrompt --> PromptMetadata
    ListPrompts --> PromptMetadata
    GetPrompt --> PromptTemplate
```

**Sources:** [js/packages/phoenix-client/CHANGELOG.md:120-125](), [js/packages/phoenix-client/CHANGELOG.md:228-229]()

### Provider Conversion

The client provides conversion utilities for each major LLM provider, handling differences in message format, tool calling syntax, and invocation parameters. It supports the latest Vercel AI SDK (v6) and OpenAI versions.

| Template Type | Structure | Provider Support |
|--------------|-----------|------------------|
| Chat Messages | Array of role/content pairs with optional tool definitions | OpenAI, Anthropic, Google, AWS Bedrock, Vercel AI SDK |
| String Template | Single text template with variable interpolation | All providers with adaptation |

**Sources:** [js/packages/phoenix-client/CHANGELOG.md:43-44](), [js/packages/phoenix-client/CHANGELOG.md:161-162](), [js/packages/phoenix-client/package.json:105-109]()

## Dataset and Experiment Management

The datasets and experiments modules support evaluation workflows, with OpenTelemetry integration for trace capture and support for dataset splits.

### Dataset Operations

```mermaid
graph TB
    subgraph "Dataset Creation"
        CreateDataset["createDataset(name, examples)<br/>Create new dataset"]
        CreateOrGet["createOrGetDataset(name, examples)<br/>Idempotent creation"]
        AppendExamples["appendDatasetExamples(id, examples)<br/>Add examples to dataset"]
    end
    
    subgraph "Dataset Retrieval"
        GetDataset["getDataset(selector)<br/>Fetch dataset by ID/name"]
        ListDatasets["listDatasets()<br/>List all datasets"]
    end
    
    subgraph "Dataset Selection"
        ByID["datasetId: string<br/>Select by ID"]
        ByName["datasetName: string<br/>Select by name"]
        ByVersion["versionId: string<br/>Specific version"]
        BySplits["splits: string[]<br/>Filter by split"]
    end
    
    subgraph "Example Structure"
        ExampleInput["input: Record<string, any><br/>Input data"]
        ExampleOutput["output: Record<string, any><br/>Expected output"]
        ExampleMetadata["metadata: Record<string, any><br/>Additional context"]
        ExampleSpanId["spanId: string<br/>Link to trace span"]
        ExampleSplit["split: string<br/>train/test/validation"]
    end
    
    CreateDataset --> ExampleInput
    CreateDataset --> ExampleOutput
    CreateDataset --> ExampleMetadata
    CreateDataset --> ExampleSpanId
    CreateDataset --> ExampleSplit
    
    GetDataset --> ByID
    GetDataset --> ByName
    GetDataset --> ByVersion
    GetDataset --> BySplits
    
    AppendExamples --> ExampleInput
    AppendExamples --> ExampleSplit
```

**Sources:** [js/packages/phoenix-client/src/datasets/createDataset.ts:1-20](), [js/packages/phoenix-client/src/datasets/getDataset.ts:1-30](), [js/packages/phoenix-client/src/types/datasets.ts:1-50]()

### Experiment Execution Workflow

The `runExperiment` function provides a full lifecycle for running tasks across datasets with evaluation. It utilizes a `NodeTracerProvider` to capture traces and can be configured to set the global tracer provider.

| Parameter | Type | Description |
|-----------|------|-------------|
| `task` | `ExperimentTask` | The function to run for each dataset example. |
| `dataset` | `DatasetSelector` | The dataset to run the experiment on. |
| `evaluators` | `ExperimentEvaluatorLike[]` | Optional evaluators to measure task behavior. |
| `concurrency` | `number` | Number of examples to run in parallel (default: 5). |
| `repetitions` | `number` | Number of times to repeat each example (default: 1). |

**Sources:** [js/packages/phoenix-client/src/experiments/runExperiment.ts:69-135](), [js/packages/phoenix-client/src/experiments/runExperiment.ts:169-185]()

## Span and Session Management

The client provides methods for querying spans and annotating entities. Recent updates added support for "notes" which can be upserted using a unique identifier.

### Note and Annotation Operations

Annotations and notes are structured feedback mechanisms. While annotations are typically for scores/labels, notes are for text-based feedback. Notes support an optional `identifier` for upserting behavior on `(entity_id, name='note', identifier)`.

```mermaid
graph LR
    subgraph "Entity Targets"
        Span["Span"]
        Trace["Trace"]
        Session["Session"]
    end
    
    subgraph "Operations"
        AddNote["addSpanNote<br/>addTraceNote<br/>addSessionNote"]
        AddAnnotation["addTraceAnnotation<br/>addSessionAnnotation"]
        DeleteAnnotation["delete-annotations<br/>(Bulk Delete)"]
    end
    
    subgraph "Filters"
        SpanFilters["parentId, traceIds,<br/>spanKind, attributes"]
    end
    
    AddNote --> Span
    AddNote --> Trace
    AddNote --> Session
    AddAnnotation --> Trace
    AddAnnotation --> Session
    DeleteAnnotation --> Span
    DeleteAnnotation --> Trace
    DeleteAnnotation --> Session
```

**Sources:** [js/packages/phoenix-client/CHANGELOG.md:7-22](), [js/packages/phoenix-client/CHANGELOG.md:49-55](), [js/packages/phoenix-client/CHANGELOG.md:67-68](), [js/packages/phoenix-client/CHANGELOG.md:73-74]()

## Integration with Phoenix Ecosystem

The TypeScript client integrates with other Phoenix packages to provide a complete development experience. It utilizes `zod` v4 for runtime validation.

```mermaid
graph TB
    subgraph "Client Package"
        PhoenixClient["@arizeai/phoenix-client<br/>Core client SDK"]
    end
    
    subgraph "Supporting Packages"
        PhoenixOtel["@arizeai/phoenix-otel<br/>OpenTelemetry registration"]
        PhoenixEvals["@arizeai/phoenix-evals<br/>Evaluation framework"]
        PhoenixConfig["@arizeai/phoenix-config<br/>Configuration utilities"]
    end
    
    subgraph "CLI and MCP"
        PhoenixCLI["@arizeai/phoenix-cli<br/>Command-line interface"]
        PhoenixMCP["@arizeai/phoenix-mcp<br/>MCP server"]
    end
    
    PhoenixClient --> PhoenixOtel
    PhoenixClient --> PhoenixConfig
    PhoenixClient --> PhoenixEvals
    
    PhoenixCLI --> PhoenixClient
    PhoenixMCP --> PhoenixClient
```

The client serves as the foundation for higher-level tools:
- **phoenix-cli**: Command-line interface using the client for prompt, dataset, and experiment management. [js/packages/phoenix-cli/package.json:42-45]()
- **phoenix-mcp**: Model Context Protocol server exposing client functionality to MCP clients like Claude Desktop. [js/packages/phoenix-mcp/package.json:33-35]()
- **phoenix-otel**: Provides registration for automatic OpenTelemetry setup with Phoenix endpoints. [js/packages/phoenix-client/package.json:91]()
- **phoenix-evals**: Evaluation framework that integrates with experiments through the client. [js/packages/phoenix-client/package.json:100]()

**Sources:** [js/packages/phoenix-client/package.json:87-96](), [js/packages/phoenix-cli/package.json:42-45](), [js/packages/phoenix-mcp/package.json:33-35]()

---

# Page: Command Line Interface (CLI)

# Command Line Interface (CLI)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-cli/SKILL.md](.agents/skills/phoenix-cli/SKILL.md)
- [.agents/skills/phoenix-cli/references/axial-coding.md](.agents/skills/phoenix-cli/references/axial-coding.md)
- [.agents/skills/phoenix-cli/references/open-coding.md](.agents/skills/phoenix-cli/references/open-coding.md)
- [.agents/skills/phoenix-evals/references/experiments-datasets-python.md](.agents/skills/phoenix-evals/references/experiments-datasets-python.md)
- [.agents/skills/phoenix-evals/references/experiments-datasets-typescript.md](.agents/skills/phoenix-evals/references/experiments-datasets-typescript.md)
- [docs/phoenix/datasets-and-experiments/how-to-datasets/exporting-datasets.mdx](docs/phoenix/datasets-and-experiments/how-to-datasets/exporting-datasets.mdx)
- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-cli.mdx](docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-cli.mdx)
- [docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/retrieve-traces-via-cli.mdx](docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/retrieve-traces-via-cli.mdx)
- [js/.gitignore](js/.gitignore)
- [js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md](js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md)
- [js/examples/apps/demo-document-relevancy-experiment/package.json](js/examples/apps/demo-document-relevancy-experiment/package.json)
- [js/packages/phoenix-cli/CHANGELOG.md](js/packages/phoenix-cli/CHANGELOG.md)
- [js/packages/phoenix-cli/README.md](js/packages/phoenix-cli/README.md)
- [js/packages/phoenix-cli/package.json](js/packages/phoenix-cli/package.json)
- [js/packages/phoenix-cli/src/cli.ts](js/packages/phoenix-cli/src/cli.ts)
- [js/packages/phoenix-cli/src/client.ts](js/packages/phoenix-cli/src/client.ts)
- [js/packages/phoenix-cli/src/commands/dataset.ts](js/packages/phoenix-cli/src/commands/dataset.ts)
- [js/packages/phoenix-cli/src/commands/experiment.ts](js/packages/phoenix-cli/src/commands/experiment.ts)
- [js/packages/phoenix-cli/src/commands/formatAnnotationDelete.ts](js/packages/phoenix-cli/src/commands/formatAnnotationDelete.ts)
- [js/packages/phoenix-cli/src/commands/formatNoteMutation.ts](js/packages/phoenix-cli/src/commands/formatNoteMutation.ts)
- [js/packages/phoenix-cli/src/commands/formatSpans.ts](js/packages/phoenix-cli/src/commands/formatSpans.ts)
- [js/packages/phoenix-cli/src/commands/formatTraces.ts](js/packages/phoenix-cli/src/commands/formatTraces.ts)
- [js/packages/phoenix-cli/src/commands/index.ts](js/packages/phoenix-cli/src/commands/index.ts)
- [js/packages/phoenix-cli/src/commands/noteMutationUtils.ts](js/packages/phoenix-cli/src/commands/noteMutationUtils.ts)
- [js/packages/phoenix-cli/src/commands/project.ts](js/packages/phoenix-cli/src/commands/project.ts)
- [js/packages/phoenix-cli/src/commands/prompt.ts](js/packages/phoenix-cli/src/commands/prompt.ts)
- [js/packages/phoenix-cli/src/commands/session.ts](js/packages/phoenix-cli/src/commands/session.ts)
- [js/packages/phoenix-cli/src/commands/span.ts](js/packages/phoenix-cli/src/commands/span.ts)
- [js/packages/phoenix-cli/src/commands/trace.ts](js/packages/phoenix-cli/src/commands/trace.ts)
- [js/packages/phoenix-cli/src/config.ts](js/packages/phoenix-cli/src/config.ts)
- [js/packages/phoenix-cli/src/trace.ts](js/packages/phoenix-cli/src/trace.ts)
- [js/packages/phoenix-cli/test/cli.test.ts](js/packages/phoenix-cli/test/cli.test.ts)
- [js/packages/phoenix-cli/test/notes.test.ts](js/packages/phoenix-cli/test/notes.test.ts)
- [js/packages/phoenix-cli/test/output.test.ts](js/packages/phoenix-cli/test/output.test.ts)
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

</details>



The Phoenix CLI (`@arizeai/phoenix-cli`) is a Node.js-based command-line tool designed for interacting with Phoenix servers. It provides a technical interface for managing projects, traces, spans, datasets, experiments, and prompts directly from the terminal. It is optimized for both human use and piping into AI coding agents (e.g., Claude Code, Cursor) or Unix utilities like `jq` [js/packages/phoenix-cli/README.md:25-26]().

The CLI is implemented in TypeScript and serves as a functional wrapper around the `@arizeai/phoenix-client` SDK [js/packages/phoenix-cli/src/commands/trace.ts:3-4]().

## Installation and Configuration

The CLI is distributed via NPM and provides the `px` binary alias [js/packages/phoenix-cli/package.json:21-24]().

```bash
npm install -g @arizeai/phoenix-cli
# or run without installing
npx @arizeai/phoenix-cli
```

**Sources:** [js/packages/phoenix-cli/README.md:27-32](), [js/packages/phoenix-cli/package.json:21-24]()

### Configuration and Profiles
The CLI resolves its connection settings using a hierarchical configuration system. Priority is given to CLI flags, followed by environment variables, then active profiles, and finally built-in defaults [js/packages/phoenix-cli/README.md:46-47]().

| Variable | Description |
| :--- | :--- |
| `PHOENIX_HOST` | Phoenix API endpoint (e.g., `http://localhost:6006`) |
| `PHOENIX_PROJECT` | Default project name or ID |
| `PHOENIX_API_KEY` | API key for authenticated instances |
| `PHOENIX_CLIENT_HEADERS` | Custom HTTP headers as a JSON string |
| `PHOENIX_CLI_DANGEROUSLY_ENABLE_DELETES` | Must be `true` to execute delete commands |

**Profiles** allow users to persist named settings (e.g., `prod`, `staging`) in a `settings.json` file [js/packages/phoenix-cli/README.md:58-70](). The CLI supports named profiles via `px profile list|show|create|edit|use|delete` [js/packages/phoenix-cli/CHANGELOG.md:54](). The settings file is JSON-Schema validated against `schemas/phoenix-cli-settings.json` [js/packages/phoenix-cli/CHANGELOG.md:54-56]().

**Sources:** [js/packages/phoenix-cli/README.md:40-56](), [js/packages/phoenix-cli/src/config.ts:1-20](), [js/packages/phoenix-cli/CHANGELOG.md:54-56]()

## Architecture and Data Flow

The CLI architecture follows a command-pattern where the `commander` library routes inputs to specific handlers that utilize a central `PhoenixClient` [js/packages/phoenix-cli/src/cli.ts:3-24]().

### System Entity Map

```mermaid
graph TD
    subgraph "CLI Space (Node.js)"
        Main["main() [src/cli.ts]"]
        Program["createProgram() [src/cli.ts]"]
        Handlers["Command Handlers [src/commands/*]"]
        ClientFactory["createPhoenixClient() [src/client.ts]"]
        Formatters["Formatters [src/commands/format*.ts]"]
        Config["resolveConfig() [src/config.ts]"]
    end

    subgraph "SDK Space"
        ClientSDK["PhoenixClient [@arizeai/phoenix-client]"]
    end

    subgraph "Server Space (FastAPI)"
        REST["REST API [/v1/*]"]
    end

    Main --> Program
    Program --> Handlers
    Handlers --> Config
    Handlers --> ClientFactory
    ClientFactory --> ClientSDK
    Handlers --> Formatters
    ClientSDK --> REST
```

**Sources:** [js/packages/phoenix-cli/src/cli.ts:26-52](), [js/packages/phoenix-cli/src/commands/index.ts:1-16](), [js/packages/phoenix-cli/src/client.ts:7-15](), [js/packages/phoenix-cli/src/commands/trace.ts:7-15]()

### Data Retrieval Flow (Traces Example)

When a user executes `px trace list`, the following internal sequence occurs:
1. **Config Resolution**: `resolveConfig` merges environment variables, profiles, and CLI flags [js/packages/phoenix-cli/src/config.ts:25-50]().
2. **Client Initialization**: `createPhoenixClient` instantiates the client from `@arizeai/phoenix-client` [js/packages/phoenix-cli/src/client.ts:7-15]().
3. **Project Resolution**: `resolveProjectId` converts a project name to a UUID if necessary [js/packages/phoenix-cli/src/client.ts:35-60]().
4. **Data Fetching**: The `fetchProjectSpans` function performs paginated `GET` requests to `/v1/projects/{project_identifier}/spans` [js/packages/phoenix-cli/src/commands/trace.ts:200-246]().
5. **Reconstruction**: Raw spans are grouped by `trace_id` and assembled into hierarchical `Trace` objects using `groupSpansByTrace` and `buildTrace` [js/packages/phoenix-cli/src/trace.ts:81-159]().
6. **Output**: Data is passed to `formatTracesOutput` for rendering in `pretty`, `json`, or `raw` formats [js/packages/phoenix-cli/src/commands/trace.ts:42-44]().

**Sources:** [js/packages/phoenix-cli/src/commands/trace.ts:200-246](), [js/packages/phoenix-cli/src/trace.ts:81-159](), [js/packages/phoenix-cli/src/config.ts:25-50]()

## Command Reference

### Tracing, Spans, and Annotations
The CLI supports granular inspection and feedback for observability data.

*   `px trace list [directory]`: Fetches recent traces. Supports `--include-annotations` and `--include-notes` [js/packages/phoenix-cli/README.md:121-142]().
*   `px trace get <trace-id>`: Retrieves a single trace by ID [js/packages/phoenix-cli/README.md:158-164]().
*   `px span list`: Fetches individual spans with optional filters like `--span-kind`, `--status-code`, or `--attribute` [js/packages/phoenix-cli/src/commands/span.ts:47-64]().
*   `px trace annotate <trace-id>`: Adds an annotation (label, score, explanation) to a trace [js/packages/phoenix-cli/src/commands/trace.ts:175-186]().
*   `px span add-note <span-id>`: Appends a text note to a specific span [js/packages/phoenix-cli/src/commands/span.ts:79-86]().
*   `px span-annotations delete`: Bulk-delete annotations from spans [js/packages/phoenix-cli/CHANGELOG.md:8]().
*   `px trace-annotations delete`: Bulk-delete annotations from traces [js/packages/phoenix-cli/CHANGELOG.md:9]().

**Sources:** [js/packages/phoenix-cli/src/commands/trace.ts:1-200](), [js/packages/phoenix-cli/src/commands/span.ts:1-150](), [js/packages/phoenix-cli/README.md:121-164](), [js/packages/phoenix-cli/CHANGELOG.md:7-12]()

### Sessions
Sessions group traces into multi-turn conversations.

*   `px session list`: Lists sessions with start/end times [js/packages/phoenix-cli/src/commands/session.ts:64-74]().
*   `px session get <session-id>`: Fetches specific session data [js/packages/phoenix-cli/src/commands/session.ts:53-62]().
*   `px session add-note <session-id>`: Creates a session-level note [js/packages/phoenix-cli/src/commands/session.ts:89-96]().
*   `px session-annotations delete`: Bulk-delete annotations from sessions [js/packages/phoenix-cli/CHANGELOG.md:10]().

**Sources:** [js/packages/phoenix-cli/src/commands/session.ts:1-122](), [js/packages/phoenix-cli/CHANGELOG.md:10]()

### Datasets, Experiments, and Prompts
*   `px dataset list`: Lists all available datasets [js/packages/phoenix-cli/src/commands/dataset.ts:1-20]().
*   `px experiment get <experiment-id>`: Fetches full experiment data including runs and evaluations [js/packages/phoenix-cli/src/commands/experiment.ts:1-20]().
*   `px prompt list`: Lists prompt templates [js/packages/phoenix-cli/src/commands/prompt.ts:1-20]().
*   `px annotation-config list`: Lists configured annotation definitions [js/packages/phoenix-cli/README.md:204-206]().

**Sources:** [js/packages/phoenix-cli/src/commands/dataset.ts:1-20](), [js/packages/phoenix-cli/src/commands/experiment.ts:1-20](), [js/packages/phoenix-cli/src/commands/prompt.ts:1-20](), [js/packages/phoenix-cli/README.md:204-206]()

## Implementation Details

### Output Formatting and Self-Update
The CLI supports `pretty` (human-readable tables/trees), `json` (pretty-printed JSON), and `raw` (compact JSON for piping) formats [js/packages/phoenix-cli/README.md:139]().

*   `px self update`: Checks the npm registry and upgrades the global installation in place. Supported for `npm`, `pnpm`, `bun`, and `deno` global installs [js/packages/phoenix-cli/README.md:108-119]().

**Sources:** [js/packages/phoenix-cli/README.md:108-119](), [js/packages/phoenix-cli/src/commands/formatTraces.ts:41-44]()

### Internal Logic Diagram

```mermaid
flowchart TD
    Start(["px command"]) --> ResolveConfig["resolveConfig() [src/config.ts]"]
    ResolveConfig --> Validate["validateConfig() [src/config.ts]"]
    Validate -- Valid --> CreateClient["createPhoenixClient() [src/client.ts]"]
    Validate -- Invalid --> ErrorOut["writeError() & exit(1)"]
    CreateClient --> ProjectRes["resolveProjectId() [src/client.ts]"]
    ProjectRes --> ExecCmd["Command Handler [e.g. src/commands/trace.ts]"]
    ExecCmd --> Fetch["PhoenixClient.GET('/v1/...')"]
    Fetch --> Format["formatOutput() [src/commands/format*.ts]"]
    Format --> Write["writeOutput() [src/io.ts]"]
```

**Sources:** [js/packages/phoenix-cli/src/config.ts:55-80](), [js/packages/phoenix-cli/src/client.ts:35-60](), [js/packages/phoenix-cli/src/commands/trace.ts:152-246]()

---

# Page: MCP Server

# MCP Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [app/src/pages/auth/AuthLayout.tsx](app/src/pages/auth/AuthLayout.tsx)
- [docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx](docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx)
- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx](docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx)
- [docs/phoenix/sdk-api-reference/typescript/overview.mdx](docs/phoenix/sdk-api-reference/typescript/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx)
- [js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md](js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md)
- [js/examples/apps/demo-document-relevancy-experiment/package.json](js/examples/apps/demo-document-relevancy-experiment/package.json)
- [js/packages/phoenix-cli/CHANGELOG.md](js/packages/phoenix-cli/CHANGELOG.md)
- [js/packages/phoenix-cli/package.json](js/packages/phoenix-cli/package.json)
- [js/packages/phoenix-client/CHANGELOG.md](js/packages/phoenix-client/CHANGELOG.md)
- [js/packages/phoenix-client/README.md](js/packages/phoenix-client/README.md)
- [js/packages/phoenix-client/package.json](js/packages/phoenix-client/package.json)
- [js/packages/phoenix-config/CHANGELOG.md](js/packages/phoenix-config/CHANGELOG.md)
- [js/packages/phoenix-config/README.md](js/packages/phoenix-config/README.md)
- [js/packages/phoenix-config/package.json](js/packages/phoenix-config/package.json)
- [js/packages/phoenix-evals/CHANGELOG.md](js/packages/phoenix-evals/CHANGELOG.md)
- [js/packages/phoenix-evals/README.md](js/packages/phoenix-evals/README.md)
- [js/packages/phoenix-evals/package.json](js/packages/phoenix-evals/package.json)
- [js/packages/phoenix-mcp/CHANGELOG.md](js/packages/phoenix-mcp/CHANGELOG.md)
- [js/packages/phoenix-mcp/README.md](js/packages/phoenix-mcp/README.md)
- [js/packages/phoenix-mcp/package.json](js/packages/phoenix-mcp/package.json)
- [js/packages/phoenix-mcp/src/index.ts](js/packages/phoenix-mcp/src/index.ts)
- [js/packages/phoenix-mcp/src/projectTools.ts](js/packages/phoenix-mcp/src/projectTools.ts)
- [js/packages/phoenix-otel/CHANGELOG.md](js/packages/phoenix-otel/CHANGELOG.md)
- [js/packages/phoenix-otel/README.md](js/packages/phoenix-otel/README.md)
- [js/packages/phoenix-otel/package.json](js/packages/phoenix-otel/package.json)
- [packages/phoenix-client/README.md](packages/phoenix-client/README.md)
- [packages/phoenix-evals/README.md](packages/phoenix-evals/README.md)
- [packages/phoenix-otel/README.md](packages/phoenix-otel/README.md)

</details>



## Purpose and Scope

The MCP Server (`@arizeai/phoenix-mcp`) is a Model Context Protocol (MCP) server implementation designed to facilitate integration between AI coding assistants (e.g., Claude Desktop, Cursor, ChatGPT) and the Phoenix platform. It exposes Phoenix's rich functionality—including tracing, datasets, experiments, and prompt management—via a standardized protocol that AI assistants can consume to assist users interactively. [README.md:37-40](), [js/packages/phoenix-mcp/package.json:2-4]()

The server is built as a TypeScript package within the Phoenix JavaScript monorepo, employing the Phoenix TypeScript client (`@arizeai/phoenix-client`) to handle API requests directed at the Phoenix backend. [js/packages/phoenix-mcp/package.json:34-36](), [js/packages/phoenix-mcp/CHANGELOG.md:111-112]()

---

## Architecture Overview

The MCP Server acts as a bridge translating between:

- **Natural Language Space:** The conversational AI assistant environment and user queries.
- **Code Entity Space:** The Phoenix API and its underlying domain entities.

It exposes a set of MCP "tools" that correspond to Phoenix API operations. These tools are registered and handled internally by the MCP server, which validates input parameters, invokes the Phoenix client functions, and returns responses in MCP-compatible formats. [js/packages/phoenix-mcp/CHANGELOG.md:111-124]()

### Data Flow Diagram

```mermaid
graph TB
    subgraph "Natural-Language-Space-(AI-Assistant)"
        UserQuery["User Query<br/>'Show me traces for project default'"]
        AIClient["MCP Client<br/>(e.g. Cursor, Claude)"]
    end
    
    subgraph "MCP-Server-(@arizeai/phoenix-mcp)"
        MCPServer["McpServer Class<br/>@modelcontextprotocol/sdk"]
        
        subgraph "Tool-Initializers"
            InitPrompts["initializePromptTools"]
            InitTraces["initializeTraceTools"]
            InitDatasets["initializeDatasetTools"]
            InitSupport["initializeSupportTools"]
            InitProjects["initializeProjectTools"]
        end
    end
    
    subgraph "Phoenix-Client-Layer-(@arizeai/phoenix-client)"
        PhoenixClient["PhoenixClient Instance"]
        RestGET["phoenix.GET('/v1/...')"]
        PromptHelper["createPrompt()"]
    end
    
    subgraph "Phoenix-Backend"
        PhoenixServer["Phoenix REST Backend<br/>/v1/projects, /v1/traces, /v1/prompts"]
    end

    UserQuery --> AIClient
    AIClient -->|JSON-RPC-stdio| MCPServer
    MCPServer --> InitPrompts & InitTraces & InitDatasets & InitSupport & InitProjects
    
    InitPrompts --> PromptHelper
    InitTraces --> RestGET
    InitDatasets --> RestGET
    InitProjects --> RestGET
    
    RestGET & PromptHelper -->|HTTP-REST| PhoenixServer
```

**Sources:** [js/packages/phoenix-mcp/package.json:33-36](), [js/packages/phoenix-mcp/src/index.ts:36-44](), [js/packages/phoenix-client/package.json:78-81]()

---

## Package Configuration

The MCP server is distributed as an NPM package and can be executed directly via `npx`. [js/packages/phoenix-mcp/package.json:19-21](), [README.md:40]()

| Property       | Value                              | Description                                   |
|----------------|----------------------------------|-----------------------------------------------|
| **Name**       | `@arizeai/phoenix-mcp`           | NPM package identifier [js/packages/phoenix-mcp/package.json:2]() |
| **Executable** | `build/index.js`                 | CLI entry point launching the MCP server [js/packages/phoenix-mcp/package.json:20]() |
| **Transport**  | `stdio`                          | Communication via standard input/output [js/packages/phoenix-mcp/package.json:29]() |

### Core Dependencies

- `@modelcontextprotocol/sdk`: The official MCP framework library implementing the protocol. [js/packages/phoenix-mcp/package.json:36]()
- `@arizeai/phoenix-client`: TypeScript Phoenix client library providing strongly-typed API calls. [js/packages/phoenix-mcp/package.json:34]()
- `@arizeai/phoenix-config`: Centralized configuration management for environment variables. [js/packages/phoenix-mcp/package.json:35]()
- `minimist`: Used for parsing command-line arguments. [js/packages/phoenix-mcp/package.json:38]()

**Sources:** [js/packages/phoenix-mcp/package.json:33-40]()

---

## Available Tools

The MCP Server exposes a comprehensive set of "tools" that allow AI assistants to programmatically query and mutate Phoenix resources. Recent updates moved tool parameters to `snake_case`. [js/packages/phoenix-mcp/CHANGELOG.md:115-117]()

| Category | Tool Examples | Description |
| :--- | :--- | :--- |
| **Projects** | `list-projects`, `get-project` | Manage observability projects [js/packages/phoenix-mcp/CHANGELOG.md:121]() |
| **Prompts** | `get-prompt-version-by-tag`, `list-prompt-version-tags`, `add-prompt-version-tag` | Manage prompt templates, versions, and tags [js/packages/phoenix-mcp/CHANGELOG.md:123-124]() |
| **Traces & Spans** | `list-traces`, `get-trace`, `get-spans`, `get-span-annotations` | Retrieve observability data and feedback [js/packages/phoenix-mcp/CHANGELOG.md:121-122]() |
| **Datasets** | `list-datasets`, `add-dataset-examples` | Explore and modify evaluation datasets [js/packages/phoenix-mcp/CHANGELOG.md:99-100]() |
| **Sessions** | `list-sessions`, `get-session` | Explore conversation flows and session annotations [js/packages/phoenix-mcp/CHANGELOG.md:122]() |
| **Support** | `phoenix-support` | Diagnostic tool for server configuration [js/packages/phoenix-mcp/CHANGELOG.md:122]() |

**Sources:** [js/packages/phoenix-mcp/CHANGELOG.md:111-124](), [js/packages/phoenix-mcp/src/index.ts:36-44]()

---

## Implementation Details

### Entry Point and Initialization

The main entry point performs the following sequence:

1. **Configuration Resolution**: Resolves API keys and base URLs from `minimist` and `@arizeai/phoenix-config`. [js/packages/phoenix-mcp/src/index.ts:21-27](), [js/packages/phoenix-mcp/package.json:35]()
2. **Client Creation**: Instantiates the `PhoenixClient` which serves as the interface to the Phoenix REST API. [js/packages/phoenix-mcp/src/index.ts:28]()
3. **Server Instantiation**: Creates a new `McpServer` instance. [js/packages/phoenix-mcp/src/index.ts:31-34]()
4. **Tool Registration**: Calls various `initialize...Tools` functions, passing the client and server instances. [js/packages/phoenix-mcp/src/index.ts:36-44]()
5. **Pagination Helper**: Uses a generic `fetchAllPages` pagination helper to handle large resource lists. [js/packages/phoenix-mcp/CHANGELOG.md:127]()

### Version Gating

The underlying `@arizeai/phoenix-client` implements server version gating. It reads the server version from response headers and validates it against minimum version requirements before calling newer API routes. [js/packages/phoenix-client/CHANGELOG.md:141-142]()

**Sources:** [js/packages/phoenix-mcp/src/index.ts:20-53](), [js/packages/phoenix-client/CHANGELOG.md:141-142]()

---

## Code Entity to Natural Language Space Mapping

### Diagram: Trace Retrieval Workflow

This diagram maps the natural language intent of an AI agent to the specific TypeScript functions and API paths in the Phoenix codebase.

```mermaid
graph LR
    UserIntent["AI Intent: 'Analyze trace 550e8400'"]
    MCP_Tool["Tool: get-trace<br/>(traceTools.ts)"]
    Validation["Zod Schema Validation<br/>(exact trace_id)"]
    Phoenix_Client["PhoenixClient.GET<br/>(phoenix-client)"]
    API_Endpoint["REST: /v1/traces/{trace_id}"]

    UserIntent --> MCP_Tool
    MCP_Tool --> Validation
    Validation --> Phoenix_Client
    Phoenix_Client --> API_Endpoint
```

**Sources:** [js/packages/phoenix-mcp/CHANGELOG.md:116-117](), [js/packages/phoenix-client/package.json:54-57]()

### Diagram: Session Annotation Flow

Mapping the flow of adding feedback to a session from an AI assistant's context.

```mermaid
graph LR
    AgentAction["AI Action: 'Mark session as helpful'"]
    SessionTool["Tool: add-session-annotation<br/>(sessionTools.ts)"]
    Capability["ensureServerCapability<br/>(Server version check)"]
    ClientCall["phoenix.POST('/v1/session_annotations')"]
    Backend["Phoenix Server Annotation Store"]

    AgentAction --> SessionTool
    SessionTool --> Capability
    Capability --> ClientCall
    ClientCall --> Backend
```

**Sources:** [js/packages/phoenix-client/CHANGELOG.md:109-110](), [js/packages/phoenix-client/CHANGELOG.md:14-22]()

---

## Development and Deployment

### Development Workflow

1. **Build**: Run `pnpm build` to compile TypeScript and set execution permissions. [js/packages/phoenix-mcp/package.json:27]()
2. **Local Testing**: Use `pnpm dev` to run the server with environment variables. [js/packages/phoenix-mcp/package.json:28]()
3. **Inspection**: Use `pnpm inspect` to launch the MCP inspector for debugging tool definitions. [js/packages/phoenix-mcp/package.json:29]()

### Environment Variables

Configuration is managed via environment variables or CLI flags:

| Variable | Description |
| :--- | :--- |
| `PHOENIX_API_KEY` | Authentication key for Phoenix. [js/packages/phoenix-client/README.md:41]() |
| `PHOENIX_BASE_URL` | The base URL for the Phoenix server. [js/packages/phoenix-mcp/package.json:28]() |
| `PHOENIX_PROJECT` | Default project name (moved to `@arizeai/phoenix-config`). [js/packages/phoenix-mcp/CHANGELOG.md:129]() |

### Integration with Assistants

The MCP server can be integrated into Cursor using a deep link or manual configuration: [README.md:40]()

```json
{
  "mcpServers": {
    "phoenix": {
      "command": "npx",
      "args": [
        "-y",
        "@arizeai/phoenix-mcp@latest",
        "--baseUrl",
        "https://my-phoenix.com",
        "--apiKey",
        "your-api-key"
      ]
    }
  }
}
```

**Sources:** [js/packages/phoenix-mcp/package.json:26-31](), [README.md:40]()

---

# Summary

The MCP Server implementation in Phoenix bridges the gap between AI-driven development tools and complex observability data. By wrapping the `@arizeai/phoenix-client` in a standardized Model Context Protocol interface, it enables AI assistants to perform deep analysis of traces, manage prompt versions, and interact with evaluation datasets directly within the user's coding environment.

---

# References

- `js/packages/phoenix-mcp/package.json`
- `js/packages/phoenix-mcp/src/index.ts`
- `js/packages/phoenix-mcp/CHANGELOG.md`
- `js/packages/phoenix-client/CHANGELOG.md`
- `README.md`

**Sources:** All factual statements cited with `[path/to/file:line-range]()`.

---

# Page: Frontend Application

# Frontend Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/.env.example](app/.env.example)
- [app/.storybook/main.ts](app/.storybook/main.ts)
- [app/.storybook/manager.ts](app/.storybook/manager.ts)
- [app/.storybook/preview-body.html](app/.storybook/preview-body.html)
- [app/.storybook/preview.tsx](app/.storybook/preview.tsx)
- [app/package.json](app/package.json)
- [app/pnpm-lock.yaml](app/pnpm-lock.yaml)
- [app/src/App.tsx](app/src/App.tsx)
- [app/src/GlobalStyles.tsx](app/src/GlobalStyles.tsx)
- [app/src/Routes.tsx](app/src/Routes.tsx)
- [app/src/components/ai/prompt-input/styles.ts](app/src/components/ai/prompt-input/styles.ts)
- [app/src/components/core/button/IconButton.tsx](app/src/components/core/button/IconButton.tsx)
- [app/src/components/core/layout/Divider.tsx](app/src/components/core/layout/Divider.tsx)
- [app/src/components/index.tsx](app/src/components/index.tsx)
- [app/src/components/nav/Navbar.tsx](app/src/components/nav/Navbar.tsx)
- [app/src/components/table/Table.tsx](app/src/components/table/Table.tsx)
- [app/src/contexts/ThemeContext.tsx](app/src/contexts/ThemeContext.tsx)
- [app/src/openInference/tracing/__tests__/types.test.ts](app/src/openInference/tracing/__tests__/types.test.ts)
- [app/src/openInference/tracing/types.ts](app/src/openInference/tracing/types.ts)
- [app/src/pages/Layout.tsx](app/src/pages/Layout.tsx)
- [app/src/pages/index.tsx](app/src/pages/index.tsx)
- [app/src/pages/prompt/promptLoader.tsx](app/src/pages/prompt/promptLoader.tsx)
- [app/src/pages/trace/TracePage.tsx](app/src/pages/trace/TracePage.tsx)
- [app/src/typeUtils.ts](app/src/typeUtils.ts)
- [app/stories/Alert.stories.tsx](app/stories/Alert.stories.tsx)
- [app/stories/ComboBox.stories.tsx](app/stories/ComboBox.stories.tsx)
- [app/stories/Gallery.stories.tsx](app/stories/Gallery.stories.tsx)
- [app/stories/TagGroup.stories.tsx](app/stories/TagGroup.stories.tsx)
- [app/vite.config.mts](app/vite.config.mts)
- [app/vitest.setup.ts](app/vitest.setup.ts)
- [js/package.json](js/package.json)
- [js/pnpm-lock.yaml](js/pnpm-lock.yaml)
- [src/phoenix/trace/fixtures.py](src/phoenix/trace/fixtures.py)
- [src/phoenix/trace/utils.py](src/phoenix/trace/utils.py)

</details>



Phoenix's frontend is a React 19 single-page application (SPA) located in the `app/` directory. The UI is built using Vite and served as static assets by the FastAPI server at runtime. This page provides an architectural overview of the frontend application.

For detailed information on the React app structure, Vite build system, and Relay integration, see **Application Structure & Build System** ([#4.1]()). For state management, theming, and context providers, see **State Management & Theming** ([#4.2]()). For the LLM interaction interface, see **Playground Interface** ([#4.3]()). For the built-in AI assistant, see **AI Assistant (PxI) Interface** ([#4.4]()).

## Technology Stack

Phoenix's frontend uses a modern TypeScript-based stack optimized for performance and type safety. The project utilizes `pnpm` workspaces for dependency management.

| Technology | Purpose | Key Files |
|------------|---------|-----------|
| `react` | UI framework (v19.2.6) | [app/package.json:92]() |
| `vite` | Build tool and dev server (v8.0.1) | [app/package.json:165](), [app/vite.config.mts:1-117]() |
| `react-relay` | GraphQL client & data fetching | [app/package.json:99](), [app/package.json:104]() |
| `react-router` | Client-side routing (v7.15.1) | [app/package.json:102](), [app/src/Routes.tsx:1-170]() |
| `zustand` | Client-side state management | [app/package.json:112]() |
| `@emotion/react` | CSS-in-JS styling | [app/package.json:59]() |
| `react-aria` | Accessible UI primitives | [app/package.json:93-94]() |
| `ai` | Vercel AI SDK for streaming | [app/package.json:76]() |

Sources: [app/package.json:43-112](), [app/vite.config.mts:1-117]()

## Application Architecture

The application is structured as a component-based hierarchy where data flows from the GraphQL API through Relay fragments into specialized page components.

### Directory Structure
- `app/src/pages/`: Contains route-level components and their associated data loaders (e.g., `TracePage` in [app/src/pages/trace/TracePage.tsx:30-83]()).
- `app/src/components/`: Reusable UI elements, including navigation and the design system (e.g., [app/src/components/index.tsx:1-40]()).
- `app/src/contexts/`: React Context providers for global concerns like theming, feature flags, and functionality (e.g., [app/src/pages/Layout.tsx:29-31]()).
- `app/src/store/`: Zustand stores for complex UI state that lives outside the Relay cache.

### Navigation and Layout
The UI utilizes a consistent layout defined in the `Layout` component ([app/src/pages/Layout.tsx:93-157]()), featuring a collapsible `SideNavbar` and a `TopNavbar` with breadcrumbs. The layout uses `react-resizable-panels` to manage the space between the main content and the optional AI assistant panel ([app/src/pages/Layout.tsx:125-153]()).

**Entity Mapping: Routing and Layout**
```mermaid
graph TD
    subgraph "Navigation Flow (app/src/Routes.tsx)"
        Routes["Routes.tsx"] --> RootLayout["RootLayout"]
        RootLayout --> AuthenticatedRoot["AuthenticatedRoot"]
        AuthenticatedRoot --> LayoutComp["Layout (app/src/pages/Layout.tsx)"]
        LayoutComp --> SideNavbar["SideNavbar"]
        LayoutComp --> TopNavbar["TopNavbar"]
        LayoutComp --> Outlet["Outlet (React Router)"]
    end

    subgraph "Page Components"
        Outlet --> ProjectsPage["ProjectsPage"]
        Outlet --> ProjectTracesPage["ProjectTracesPage"]
        Outlet --> DatasetsPage["DatasetsPage"]
        Outlet --> PlaygroundPage["PlaygroundPage"]
        Outlet --> TracePage["TracePage (app/src/pages/trace/TracePage.tsx)"]
    end

    SideNavbar --> NavLink["NavLink"]
    TopNavbar --> NavBreadcrumb["NavBreadcrumb"]
    LayoutComp --> AgentChatPanel["AgentChatPanel (app/src/pages/Layout.tsx:151)"]
```
Sources: [app/src/Routes.tsx:132-170](), [app/src/pages/Layout.tsx:93-157](), [app/src/pages/trace/TracePage.tsx:30-83]()

## Build and Development Workflow

Phoenix uses a tight integration between the Vite build system and the Relay compiler. The `vite.config.mts` is configured to output bundled assets directly into the Python package's server directory ([app/vite.config.mts:77]()).

- **Relay Compiler**: Runs `relay-compiler` to generate TypeScript types from GraphQL queries and fragments. This is a prerequisite for the main build ([app/package.json:10]()).
- **Vite Build**: The `pnpm run build` command triggers the Relay compiler followed by `vite build` ([app/package.json:8]()). It uses `rolldownOptions` for code splitting, grouping heavy libraries like `codemirror` and `recharts` into separate chunks ([app/vite.config.mts:80-113]()).
- **Dev Server**: `pnpm run dev` ([app/package.json:13]()) starts a development environment. The `dev:server` script ([app/package.json:16]()) launches the Python backend with Vite proxying enabled.

**Entity Mapping: Build Pipeline**
```mermaid
graph LR
    subgraph "Build Pipeline (app/package.json)"
        RC["relay-compiler (build:relay)"]
        ViteBuild["vite build (build)"]
        TS["tsc --noEmit (typecheck)"]
    end

    subgraph "Vite Config (app/vite.config.mts)"
        Config["defineConfig"]
        Alias["@phoenix alias"]
        OutDir["outDir: ../src/phoenix/server/static"]
    end

    RC -- "generates types" --> TS
    RC -- "generates artifacts" --> ViteBuild
    ViteBuild -- "reads" --> Config
    Config -- "resolves" --> Alias
    ViteBuild -- "emits to" --> OutDir
```
Sources: [app/package.json:7-42](), [app/vite.config.mts:42-114]()

## Key Feature Systems

### Tracing and Observability
The primary interface for browsing traces and spans. The `TracePage` component handles the display of trace details and utilizes a `Drawer` for overlaying information ([app/src/pages/trace/TracePage.tsx:45-81]()). It relies on search parameters like `SELECTED_SPAN_NODE_ID_PARAM` to manage UI state ([app/src/pages/trace/TracePage.tsx:35]()).
For details, see [Tracing & Observability](#5.1).

### State and Theming
The application uses CSS custom properties for theming, defined in `GlobalStyles.tsx`. It supports `mediumRootCSS` for scaling and `darkThemeCSS` for dark mode ([app/src/GlobalStyles.tsx:9-180]()). The theme is toggled via a `ThemeSelector` in the navbar ([app/src/components/nav/Navbar.tsx:194-253]()).
For details, see [State Management & Theming](#4.2).

### Playground Interface
A specialized environment for testing LLM prompts. It is integrated into the main routing ([app/src/Routes.tsx:66]()) and allows users to interact with models directly. It utilizes `@ai-sdk/react` for handling streaming interactions ([app/package.json:44]()).
For details, see [Playground Interface](#4.3).

### AI Assistant (PxI) Interface
Phoenix Intelligence (PxI) provides an interactive chat interface. The `Layout` component manages its visibility and positioning (docked vs. floating) using the `AgentContext` ([app/src/pages/Layout.tsx:96-109]()). It can be rendered as a `FloatingAgentChatPanel` or a docked `AgentChatPanel` ([app/src/pages/Layout.tsx:139-151]()).
For details, see [AI Assistant (PxI) Interface](#4.4).

Sources: [app/src/GlobalStyles.tsx:9-180](), [app/src/pages/Layout.tsx:93-157](), [app/src/pages/trace/TracePage.tsx:30-83](), [app/src/Routes.tsx:66-95]()

---

# Page: Application Structure & Build System

# Application Structure & Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/.env.example](app/.env.example)
- [app/package.json](app/package.json)
- [app/pnpm-lock.yaml](app/pnpm-lock.yaml)
- [app/src/GlobalStyles.tsx](app/src/GlobalStyles.tsx)
- [app/src/RelayEnvironment.ts](app/src/RelayEnvironment.ts)
- [app/src/Routes.tsx](app/src/Routes.tsx)
- [app/src/authFetch.ts](app/src/authFetch.ts)
- [app/src/components/index.tsx](app/src/components/index.tsx)
- [app/src/components/nav/Navbar.tsx](app/src/components/nav/Navbar.tsx)
- [app/src/components/settings/OAuthUserForm.tsx](app/src/components/settings/OAuthUserForm.tsx)
- [app/src/components/settings/UserForm.tsx](app/src/components/settings/UserForm.tsx)
- [app/src/components/table/Table.tsx](app/src/components/table/Table.tsx)
- [app/src/openInference/tracing/__tests__/types.test.ts](app/src/openInference/tracing/__tests__/types.test.ts)
- [app/src/openInference/tracing/types.ts](app/src/openInference/tracing/types.ts)
- [app/src/pages/Layout.tsx](app/src/pages/Layout.tsx)
- [app/src/pages/auth/ForgotPasswordForm.tsx](app/src/pages/auth/ForgotPasswordForm.tsx)
- [app/src/pages/auth/LoggedOutPage.tsx](app/src/pages/auth/LoggedOutPage.tsx)
- [app/src/pages/auth/LoginForm.tsx](app/src/pages/auth/LoginForm.tsx)
- [app/src/pages/auth/LoginPage.tsx](app/src/pages/auth/LoginPage.tsx)
- [app/src/pages/auth/OAuth2Login.tsx](app/src/pages/auth/OAuth2Login.tsx)
- [app/src/pages/auth/ResetPasswordForm.tsx](app/src/pages/auth/ResetPasswordForm.tsx)
- [app/src/pages/auth/ResetPasswordWithTokenForm.tsx](app/src/pages/auth/ResetPasswordWithTokenForm.tsx)
- [app/src/pages/auth/authErrors.ts](app/src/pages/auth/authErrors.ts)
- [app/src/pages/index.tsx](app/src/pages/index.tsx)
- [app/src/pages/prompt/promptLoader.tsx](app/src/pages/prompt/promptLoader.tsx)
- [app/src/pages/settings/NewUserDialog.tsx](app/src/pages/settings/NewUserDialog.tsx)
- [app/src/pages/settings/__generated__/NewUserDialogMutation.graphql.ts](app/src/pages/settings/__generated__/NewUserDialogMutation.graphql.ts)
- [app/src/pages/trace/TracePage.tsx](app/src/pages/trace/TracePage.tsx)
- [app/src/typeUtils.ts](app/src/typeUtils.ts)
- [app/src/utils/__tests__/routingUtils.test.ts](app/src/utils/__tests__/routingUtils.test.ts)
- [app/src/utils/routingUtils.ts](app/src/utils/routingUtils.ts)
- [app/stories/ComboBox.stories.tsx](app/stories/ComboBox.stories.tsx)
- [app/stories/Gallery.stories.tsx](app/stories/Gallery.stories.tsx)
- [app/stories/TagGroup.stories.tsx](app/stories/TagGroup.stories.tsx)
- [app/tests/auth-refresh.spec.ts](app/tests/auth-refresh.spec.ts)
- [app/tsconfig.json](app/tsconfig.json)
- [app/vite.config.mts](app/vite.config.mts)
- [app/vitest.setup.ts](app/vitest.setup.ts)
- [js/package.json](js/package.json)
- [js/pnpm-lock.yaml](js/pnpm-lock.yaml)
- [src/phoenix/server/api/auth_messages.py](src/phoenix/server/api/auth_messages.py)
- [src/phoenix/trace/fixtures.py](src/phoenix/trace/fixtures.py)
- [src/phoenix/trace/utils.py](src/phoenix/trace/utils.py)

</details>



This page documents the frontend application's architecture, the Vite-based build system, and the integration of React Relay and Zustand. The Phoenix frontend is a modern React application built with TypeScript, designed for high-performance AI observability visualizations.

## Build System Overview

The Phoenix frontend uses **Vite** as its primary build tool and development server, with **pnpm** as the package manager. The build system is optimized for a monorepo structure where the frontend assets are eventually served by the Python FastAPI backend.

### Package Management & Scripts

The application is defined in `app/package.json` [app/package.json:1-177](). It uses **pnpm** (version 11.3.0) [app/package.json:175]().

Key scripts for the build lifecycle:
- `build`: Runs the Relay compiler followed by the Vite production build [app/package.json:8]().
- `build:relay`: Executes `relay-compiler` to generate TypeScript types from GraphQL definitions [app/package.json:10]().
- `build:static`: Copies static assets into the Python server directory `../src/phoenix/server` [app/package.json:11]().
- `dev`: A multi-process command (using `mprocs`) that typically starts both the Vite dev server and the Python backend [app/package.json:13-16]().
- `generate:openapi`: Generates TypeScript types from the Phoenix OpenAPI schema [app/package.json:26]().

### Vite Configuration

The Vite configuration (`app/vite.config.mts`) manages the transformation of TypeScript, React, and Relay code into optimized browser bundles.

**Vite Build Pipeline**
```mermaid
graph TD
    subgraph "Vite_Build_Process"
        Entry["app/src/index.tsx"]
        ReactFallbackThrottlePlugin["vite-plugin-react-fallback-throttle"]
        ReactPlugin["@vitejs/plugin-react"]
        BabelPlugin["@rolldown/plugin-babel (with React Compiler)"]
        RelayPlugin["vite-plugin-relay"]
        LezerPlugin["@lezer/generator/rollup"]
        CircleDependencyPlugin["vite-plugin-circular-dependency"]
        Rollup["Rollup Bundler"]
        StaticOutput["../src/phoenix/server/static/"]
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

**Build Configuration Details:**
- **Plugins**: The `vite.config.mts` [app/vite.config.mts:25-38]() defines several plugins:
    - `reactFallbackThrottlePlugin()`: Disables React's built-in 300ms suspense fallback timer to prevent UI delays [app/vite.config.mts:28]().
    - `react()`: Standard React plugin [app/vite.config.mts:29]().
    - `babel()`: Integrates Babel with `@rolldown/plugin-babel` and the `babel-plugin-react-compiler` for React Compiler support [app/vite.config.mts:32-34]().
    - `relay`: Uses `vite-plugin-relay` to transform `graphql` tagged templates [app/vite.config.mts:35]().
    - `lezer()`: For Lezer grammar generation [app/vite.config.mts:36]().
    - `circleDependency()`: Detects circular dependencies and throws errors if found [app/vite.config.mts:37]().
- **Source Maps**: Source map generation is controlled by the `PHOENIX_ENABLE_SOURCE_MAP` environment variable [app/vite.config.mts:15,79]().
- **Optimization**: Implements manual code splitting for large libraries like `codemirror`, `recharts`, `shiki`, `@ai-sdk/react`, and `streamdown` to improve initial load times [app/vite.config.mts:82-113]().
- **Output**: The build output directory is `../src/phoenix/server/static`, allowing the FastAPI server to serve the UI directly [app/vite.config.mts:77]().
- **Aliases**: `@phoenix` is aliased to `app/src` for cleaner imports [app/vite.config.mts:61]().

Sources: [app/package.json:1-177](), [app/vite.config.mts:1-117]()

## Application Architecture

The application is structured as a single-page application (SPA) with a clear separation between routing, state management, and visual components.

### Routing System

Phoenix uses `react-router` (v7) to manage navigation. The routes are defined in `app/src/Routes.tsx` [app/src/Routes.tsx:1-131]().

**Routing Implementation**
```mermaid
graph TD
    Router["createBrowserRouter"]
    RootRoute["app/src/Routes.tsx: Route path='/' (RootLayout)"]
    AuthRoutes["app/src/Routes.tsx: /login, /logout, /reset-password"]
    AuthenticatedRoot["app/src/Routes.tsx: AuthenticatedRoot (authenticatedRootLoader)"]
    Layout["app/src/pages/Layout.tsx: Layout (layoutLoader)"]
    
    Router --> RootRoute
    RootRoute --> AuthRoutes
    RootRoute --> AuthenticatedRoot
    AuthenticatedRoot --> Layout
    
    subgraph "Main_Application_Features"
        Layout --> Projects["/projects (ProjectsPage)"]
        Layout --> Traces["/projects/:projectId/traces/:traceId (TracePage)"]
        Layout --> Datasets["/datasets (DatasetsPage)"]
        Layout --> Playground["/playground (PlaygroundPage)"]
        Layout --> Evaluators["/evaluators (EvaluatorsPage)"]
    end
```

**Key Routing Features:**
- **Revalidation Logic**: A `revalidateOnPathChange` function prevents unnecessary loader execution when only search parameters or URL hashes change, optimizing performance for UI-only state updates [app/src/Routes.tsx:123-130]().
- **Breadcrumbs**: Routes use a `handle` with a `crumb` function to dynamically generate navigation breadcrumbs [app/src/Routes.tsx:166-167]().
- **Redirects**: Specific routes like `/v1/*` are redirected to the root to handle common user misconfigurations with OpenTelemetry collector URLs [app/src/Routes.tsx:135-141]().

Sources: [app/src/Routes.tsx:1-240]()

### State Management Strategy

Phoenix employs a tiered state management approach:

| Layer | Technology | Responsibility |
| :--- | :--- | :--- |
| **Server State** | **React Relay** | Fetching GraphQL data, caching, and fragment-based data masking. |
| **Global UI State** | **Zustand** | Cross-component state such as side-navigation expansion or AI agent panel state. |
| **Theme & Auth** | **React Context** | Application-wide settings like Dark/Light mode and session handling. |

Sources: [app/package.json:99,112](), [app/src/pages/Layout.tsx:96-97,160-162](), [app/src/GlobalStyles.tsx:4-5]()

## Relay Integration & Data Flow

Relay is the primary data fetching mechanism. It ensures that components only request the data they need through GraphQL fragments.

1.  **Relay Compiler**: During build, `relay-compiler` scans for `graphql` literals and generates TypeScript types in `__generated__` directories [app/package.json:10]().
2.  **Fragments**: Components define their data requirements using fragments, which are then composed into parent queries.
3.  **Environment**: The Relay Environment (configured in `app/src/RelayEnvironment.ts` [app/src/RelayEnvironment.ts:1-181]()) handles the network layer, communicating with the `/graphql` endpoint.

**Relay Data Flow**
```mermaid
graph LR
    subgraph "Frontend_App"
        Component["React Component"]
        RelayEnv["app/src/RelayEnvironment.ts: relayEnvironment"]
        RelayStore["app/src/RelayEnvironment.ts: relayStore"]
    end
    
    subgraph "Server_API"
        GraphQL["/graphql Endpoint"]
    end

    Component -- "useLazyLoadQuery / useFragment" --> RelayEnv
    RelayEnv -- "fetchRelay" --> GraphQL
    GraphQL -- "JSON Response" --> RelayEnv
    RelayEnv -- "Write to Store" --> RelayStore
    RelayStore -- "Masked Data" --> Component
```

Sources: [app/package.json:10,99,141,159](), [app/vite.config.mts:35](), [app/src/RelayEnvironment.ts:1-181]()

## Component Architecture & Theming

### Theming System

Phoenix uses a CSS-variable-based theming system powered by **Emotion**. Global styles and theme variables (colors, dimensions, font weights) are defined in `app/src/GlobalStyles.tsx` [app/src/GlobalStyles.tsx:1-175]().

-   **Root Variables**: Defines standard scales for spacing using `--global-dimension-size-*` variables [app/src/GlobalStyles.tsx:12-67]().
-   **Static Variables**: Defines static colors (white/black alphas) and standard component heights for inputs and buttons [app/src/GlobalStyles.tsx:70-91]().
-   **Theme Switching**: Supports `light` and `dark` themes by overriding color variables. The `darkThemeCSS` includes `color-scheme: dark` to sync system elements like scrollbars [app/src/GlobalStyles.tsx:177-183]().

### Component Library

The UI is built using a combination of:
-   **React Aria Components**: For accessible UI primitives (buttons, modals, forms) [app/package.json:93-94](). Core components are re-exported in `app/src/components/index.tsx` [app/src/components/index.tsx:2-11]().
-   **CodeMirror**: Used for syntax-highlighted code editors for Python, JSON, and Javascript [app/package.json:47-55]().
-   **Recharts**: For observability metrics and trace visualizations [app/package.json:103]().
-   **Custom Components**: Specialized components for AI observability, such as `TraceDetails` [app/src/pages/trace/TracePage.tsx:73-76]() and `AgentChatPanel` [app/src/pages/Layout.tsx:8-12,151]().

Sources: [app/src/GlobalStyles.tsx:1-186](), [app/package.json:44-113](), [app/src/components/index.tsx:1-40](), [app/src/pages/trace/TracePage.tsx:7-10](), [app/src/pages/Layout.tsx:8-28]()

---

# Page: State Management & Theming

# State Management & Theming

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/.storybook/main.ts](app/.storybook/main.ts)
- [app/.storybook/manager.ts](app/.storybook/manager.ts)
- [app/.storybook/preview-body.html](app/.storybook/preview-body.html)
- [app/.storybook/preview.tsx](app/.storybook/preview.tsx)
- [app/src/App.tsx](app/src/App.tsx)
- [app/src/components/agent/AgentConsentGate.tsx](app/src/components/agent/AgentConsentGate.tsx)
- [app/src/components/agent/AgentObservabilitySettings.tsx](app/src/components/agent/AgentObservabilitySettings.tsx)
- [app/src/components/agent/useAssistantAgentEnabled.ts](app/src/components/agent/useAssistantAgentEnabled.ts)
- [app/src/components/ai/prompt-input/styles.ts](app/src/components/ai/prompt-input/styles.ts)
- [app/src/components/core/button/IconButton.tsx](app/src/components/core/button/IconButton.tsx)
- [app/src/components/core/layout/Divider.tsx](app/src/components/core/layout/Divider.tsx)
- [app/src/contexts/ThemeContext.tsx](app/src/contexts/ThemeContext.tsx)
- [app/src/contexts/ViewerContext.tsx](app/src/contexts/ViewerContext.tsx)
- [app/src/contexts/__generated__/ViewerContextRefetchQuery.graphql.ts](app/src/contexts/__generated__/ViewerContextRefetchQuery.graphql.ts)
- [app/src/contexts/__generated__/ViewerContext_viewer.graphql.ts](app/src/contexts/__generated__/ViewerContext_viewer.graphql.ts)
- [app/src/pages/AuthenticatedRoot.tsx](app/src/pages/AuthenticatedRoot.tsx)
- [app/src/pages/__generated__/authenticatedRootLoaderQuery.graphql.ts](app/src/pages/__generated__/authenticatedRootLoaderQuery.graphql.ts)
- [app/src/pages/authenticatedRootLoader.ts](app/src/pages/authenticatedRootLoader.ts)
- [app/src/pages/profile/APIKeysTable.tsx](app/src/pages/profile/APIKeysTable.tsx)
- [app/src/pages/profile/ProfilePage.tsx](app/src/pages/profile/ProfilePage.tsx)
- [app/src/pages/profile/ViewerProfileCard.tsx](app/src/pages/profile/ViewerProfileCard.tsx)
- [app/src/pages/profile/__generated__/APIKeysTableDeleteAPIKeyMutation.graphql.ts](app/src/pages/profile/__generated__/APIKeysTableDeleteAPIKeyMutation.graphql.ts)
- [app/src/pages/project/ProjectPage.tsx](app/src/pages/project/ProjectPage.tsx)
- [app/src/pages/project/SpanColumnSelector.tsx](app/src/pages/project/SpanColumnSelector.tsx)
- [app/src/pages/project/SpansTable.tsx](app/src/pages/project/SpansTable.tsx)
- [app/src/pages/project/TracesTable.tsx](app/src/pages/project/TracesTable.tsx)
- [app/src/pages/project/__generated__/ProjectPageQueriesSpansQuery.graphql.ts](app/src/pages/project/__generated__/ProjectPageQueriesSpansQuery.graphql.ts)
- [app/src/pages/project/__generated__/ProjectPageQueriesTracesQuery.graphql.ts](app/src/pages/project/__generated__/ProjectPageQueriesTracesQuery.graphql.ts)
- [app/src/pages/project/__generated__/ProjectPageQuery.graphql.ts](app/src/pages/project/__generated__/ProjectPageQuery.graphql.ts)
- [app/src/pages/project/__generated__/SpansTableSpansQuery.graphql.ts](app/src/pages/project/__generated__/SpansTableSpansQuery.graphql.ts)
- [app/src/pages/project/__generated__/SpansTable_spans.graphql.ts](app/src/pages/project/__generated__/SpansTable_spans.graphql.ts)
- [app/src/pages/project/__generated__/TracesTableQuery.graphql.ts](app/src/pages/project/__generated__/TracesTableQuery.graphql.ts)
- [app/src/pages/project/__generated__/TracesTable_spans.graphql.ts](app/src/pages/project/__generated__/TracesTable_spans.graphql.ts)
- [app/src/store/tracingStore.tsx](app/src/store/tracingStore.tsx)
- [app/stories/Alert.stories.tsx](app/stories/Alert.stories.tsx)

</details>



This document describes the Phoenix frontend state management architecture, which utilizes Zustand for client-side stores, Relay for GraphQL caching, and a robust theming system built on CSS custom properties.

## State Management Architecture

Phoenix employs a layered approach to state: Zustand for ephemeral or persisted UI state, React Context for configuration and dependency injection, and Relay for server-synchronized data.

### Provider Tree Hierarchy

The application initializes with a hierarchy of providers that establish the environment for data fetching, theming, and state access.

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

**Sources:** [app/src/App.tsx:15-40]()

### Zustand Stores

Phoenix uses Zustand for lightweight state management. Stores are often integrated with `persist` middleware to maintain state across page reloads.

| Store | Purpose | Persistence | Key Entities |
|-------|---------|-------------|--------------|
| **TracingStore** | Manages span selection and trace view state | In-memory | `selectedSpanId`, `expandedTraceIds` |
| **CredentialsStore** | Manages API keys for LLM providers | localStorage | `ModelProvider`, `APIKey` |
| **PreferencesStore** | Global user UI settings | localStorage | `isSideNavExpanded`, `themeMode` |

#### Data Flow and State Synchronization
Components often combine Relay data with local Zustand state to handle interactive UI elements like tables. For example, `SpansTable` uses Relay for paginated data fetching and Zustand (or local React state) for managing column visibility and sorting.

```mermaid
graph LR
    subgraph "Table State Flow"
        RelayFrag["SpansTable_spans.graphql"] -- "provides" --> TableData["SpansTable.tsx: data"]
        TableData --> TanstackTable["useReactTable"]
        TanstackTable -- "sort/filter" --> GqlVariables["SpansTableSpansQuery.graphql"]
        GqlVariables -- "refetch" --> RelayFrag
    end
```

**Sources:** [app/src/pages/project/SpansTable.tsx:108-132](), [app/src/pages/project/__generated__/SpansTable_spans.graphql.ts:16-91](), [app/src/store/tracingStore.tsx:1-20]()

### Relay Cache & Data Flow

Relay handles the synchronization of server-side data. The application uses a fragment-based architecture where parent components fetch data and children define their requirements via fragments.

- **Preloading**: Data is fetched using `useQueryLoader` and `usePreloadedQuery` patterns to optimize initial renders [app/src/pages/project/ProjectPage.tsx:154-165]().
- **Pagination**: Large lists like spans and traces use `usePaginationFragment` to handle infinite scrolling and "Load More" functionality [app/src/pages/project/SpansTable.tsx:18-22]().
- **Cache Policy**: Queries often specify `store-and-network` to ensure immediate UI updates from the cache followed by background synchronization [app/src/pages/project/ProjectPage.tsx:150-152]().

**Sources:** [app/src/pages/project/ProjectPage.tsx:134-165](), [app/src/pages/project/SpansTable.tsx:116-179]()

## Theming System

Phoenix uses a CSS-in-JS approach (via Emotion) combined with CSS custom properties to provide a themeable interface.

### CSS Custom Properties Architecture

The system is founded on `GlobalStyles.tsx`, which defines variables for dimensions and colors.

- **Dimension Scaling**: Standardized sizes are defined using a consistent scale (e.g., `--global-dimension-size-200`) [app/src/pages/project/SpansTable.tsx:189-192]().
- **Thematic Colors**: Colors are assigned to variables like `--global-color-gray-100` which are redefined in dark mode [app/src/pages/project/TracesTable.tsx:177]().
- **Dynamic Resizing**: Table columns utilize CSS variables for dynamic width calculations (e.g., `--col-id-size`) [app/src/pages/project/SpansTable.tsx:149-155]().

**Sources:** [app/src/pages/project/SpansTable.tsx:149-165](), [app/src/pages/project/TracesTable.tsx:175-179]()

### Theme Selection & Application

The `ThemeProvider` manages the application of the `light` and `dark` themes.

- **Storybook Integration**: Theming is also integrated into the development environment via Storybook, allowing previewing components in different modes [app/.storybook/preview.tsx:21-40]().
- **System Sync**: The application can detect and react to system-level theme changes using the `useSystemTheme` hook [app/.storybook/preview.tsx:258-275]().

```mermaid
graph TD
    subgraph "Theming Logic"
        Provider["ThemeProvider.tsx"] -- "provides" --> ThemeContext["ThemeContext"]
        ThemeContext -- "consumed by" --> App["App.tsx"]
        App -- "renders" --> GlobalStyles["GlobalStyles.tsx"]
        GlobalStyles -- "injects" --> RootVars[":root CSS Variables"]
    end
```

**Sources:** [app/src/App.tsx:4-20](), [app/.storybook/preview.tsx:56-57]()

## Layout & Context Integration

The main application layout integrates multiple state sources to manage complex UI behaviors.

- **Project Context**: `ProjectContext` provides project-specific configuration, such as whether to treat orphan spans as roots [app/src/pages/project/ProjectPage.tsx:123-125]().
- **Time Range State**: The `useTimeRange` hook interacts with global state to synchronize data fetching across different tabs (Spans, Traces, Sessions) [app/src/pages/project/ProjectPage.tsx:67-68]().
- **Streaming State**: `StreamStateProvider` manages the real-time update status for the current project view [app/src/pages/project/ProjectPage.tsx:110-112]().

**Sources:** [app/src/pages/project/ProjectPage.tsx:102-114](), [app/src/pages/project/SpansTable.tsx:64-66]()

---

# Page: Playground Interface

# Playground Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/@types/generative.d.ts](app/src/@types/generative.d.ts)
- [app/src/components/evaluators/AddEvaluatorMenu.tsx](app/src/components/evaluators/AddEvaluatorMenu.tsx)
- [app/src/components/evaluators/EvaluatorForm.tsx](app/src/components/evaluators/EvaluatorForm.tsx)
- [app/src/components/evaluators/EvaluatorPromptPreview.tsx](app/src/components/evaluators/EvaluatorPromptPreview.tsx)
- [app/src/components/evaluators/__generated__/EvaluatorPromptPreviewQuery.graphql.ts](app/src/components/evaluators/__generated__/EvaluatorPromptPreviewQuery.graphql.ts)
- [app/src/components/evaluators/templates/defaultEvaluatorTemplate.tsx](app/src/components/evaluators/templates/defaultEvaluatorTemplate.tsx)
- [app/src/components/evaluators/templates/index.ts](app/src/components/evaluators/templates/index.ts)
- [app/src/components/evaluators/templates/types.tsx](app/src/components/evaluators/templates/types.tsx)
- [app/src/components/evaluators/utils.ts](app/src/components/evaluators/utils.ts)
- [app/src/components/generative/ToolChoiceSelector.tsx](app/src/components/generative/ToolChoiceSelector.tsx)
- [app/src/constants/__tests__/generativeConstants.test.ts](app/src/constants/__tests__/generativeConstants.test.ts)
- [app/src/constants/generativeConstants.ts](app/src/constants/generativeConstants.ts)
- [app/src/pages/playground/ChatMessageToolCallsEditor.tsx](app/src/pages/playground/ChatMessageToolCallsEditor.tsx)
- [app/src/pages/playground/Playground.tsx](app/src/pages/playground/Playground.tsx)
- [app/src/pages/playground/PlaygroundChatTemplate.tsx](app/src/pages/playground/PlaygroundChatTemplate.tsx)
- [app/src/pages/playground/PlaygroundCredentialsDropdown.tsx](app/src/pages/playground/PlaygroundCredentialsDropdown.tsx)
- [app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx](app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx)
- [app/src/pages/playground/PlaygroundDatasetSection.tsx](app/src/pages/playground/PlaygroundDatasetSection.tsx)
- [app/src/pages/playground/PlaygroundEvaluatorSelect.tsx](app/src/pages/playground/PlaygroundEvaluatorSelect.tsx)
- [app/src/pages/playground/PlaygroundExperimentToolbar.tsx](app/src/pages/playground/PlaygroundExperimentToolbar.tsx)
- [app/src/pages/playground/PlaygroundOutput.tsx](app/src/pages/playground/PlaygroundOutput.tsx)
- [app/src/pages/playground/PlaygroundTemplate.tsx](app/src/pages/playground/PlaygroundTemplate.tsx)
- [app/src/pages/playground/PlaygroundTool.tsx](app/src/pages/playground/PlaygroundTool.tsx)
- [app/src/pages/playground/PlaygroundToolCall.tsx](app/src/pages/playground/PlaygroundToolCall.tsx)
- [app/src/pages/playground/PlaygroundTools.tsx](app/src/pages/playground/PlaygroundTools.tsx)
- [app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableMutation.graphql.ts](app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableMutation.graphql.ts)
- [app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableSubscription.graphql.ts](app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableSubscription.graphql.ts)
- [app/src/pages/playground/__generated__/PlaygroundDatasetSectionQuery.graphql.ts](app/src/pages/playground/__generated__/PlaygroundDatasetSectionQuery.graphql.ts)
- [app/src/pages/playground/__generated__/PlaygroundDatasetSection_evaluator.graphql.ts](app/src/pages/playground/__generated__/PlaygroundDatasetSection_evaluator.graphql.ts)
- [app/src/pages/playground/__generated__/PlaygroundOutputSubscription.graphql.ts](app/src/pages/playground/__generated__/PlaygroundOutputSubscription.graphql.ts)
- [app/src/pages/playground/__tests__/playgroundUtils.test.ts](app/src/pages/playground/__tests__/playgroundUtils.test.ts)
- [app/src/pages/playground/constants.tsx](app/src/pages/playground/constants.tsx)
- [app/src/pages/playground/playgroundUtils.ts](app/src/pages/playground/playgroundUtils.ts)
- [app/src/pages/playground/schemas.ts](app/src/pages/playground/schemas.ts)
- [app/src/schemas/__tests__/toolCallSchemas.test.ts](app/src/schemas/__tests__/toolCallSchemas.test.ts)
- [app/src/schemas/__tests__/toolSchemas.test.ts](app/src/schemas/__tests__/toolSchemas.test.ts)
- [app/src/schemas/phoenixToolTypeSchemas.ts](app/src/schemas/phoenixToolTypeSchemas.ts)
- [app/src/schemas/toolChoiceSchemas.ts](app/src/schemas/toolChoiceSchemas.ts)
- [app/src/schemas/toolSchemas.ts](app/src/schemas/toolSchemas.ts)
- [app/src/store/credentialsStore.tsx](app/src/store/credentialsStore.tsx)
- [app/src/store/datasetStore.tsx](app/src/store/datasetStore.tsx)
- [app/src/store/evaluatorStore.tsx](app/src/store/evaluatorStore.tsx)
- [app/src/store/playground/__tests__/playgroundStore.test.ts](app/src/store/playground/__tests__/playgroundStore.test.ts)
- [app/src/store/playground/__tests__/playgroundStoreUtils.test.ts](app/src/store/playground/__tests__/playgroundStoreUtils.test.ts)
- [app/src/store/playground/playgroundStore.tsx](app/src/store/playground/playgroundStore.tsx)
- [app/src/store/playground/playgroundStoreUtils.ts](app/src/store/playground/playgroundStoreUtils.ts)
- [app/src/store/playground/types.ts](app/src/store/playground/types.ts)
- [app/src/types/evaluators.ts](app/src/types/evaluators.ts)
- [app/src/utils/generativeUtils.ts](app/src/utils/generativeUtils.ts)
- [src/phoenix/server/api/evaluators.py](src/phoenix/server/api/evaluators.py)
- [src/phoenix/server/api/helpers/evaluators.py](src/phoenix/server/api/helpers/evaluators.py)
- [src/phoenix/server/api/helpers/playground_clients.py](src/phoenix/server/api/helpers/playground_clients.py)
- [src/phoenix/server/api/mutations/chat_mutations.py](src/phoenix/server/api/mutations/chat_mutations.py)
- [src/phoenix/server/api/subscriptions.py](src/phoenix/server/api/subscriptions.py)
- [tests/unit/server/api/helpers/test_evaluators.py](tests/unit/server/api/helpers/test_evaluators.py)
- [tests/unit/server/api/helpers/test_playground_clients.py](tests/unit/server/api/helpers/test_playground_clients.py)
- [tests/unit/server/api/test_subscriptions.py](tests/unit/server/api/test_subscriptions.py)

</details>



The Playground Interface is Phoenix's frontend system for interactively testing LLM prompts across multiple providers with real-time streaming responses. This document covers the React-based UI components, state management via Zustand, GraphQL communication patterns, and the data flow from user input through LLM invocation to displayed output.

## Component Architecture

The playground is structured as a hierarchical React application with main sections for prompts, inputs (when using template variables), and outputs. The top-level `Playground` component ([app/src/pages/playground/Playground.tsx:136-210]()) orchestrates the layout and provides the context for all child components via `PlaygroundProvider`.

**Primary Component Files and Responsibilities**

| Component | File | Primary Responsibility |
|-----------|------|----------------------|
| `Playground` | `Playground.tsx` | Root component, checks provider availability, wraps app in `PlaygroundProvider` [app/src/pages/playground/Playground.tsx:136-210]() |
| `PlaygroundContent` | `Playground.tsx` | Layout orchestration using `react-resizable-panels` [app/src/pages/playground/Playground.tsx:232-378]() |
| `PlaygroundTemplate` | `PlaygroundTemplate.tsx` | Template editor wrapper, model config button, and prompt versioning UI |
| `PlaygroundChatTemplate` | `PlaygroundChatTemplate.tsx` | Message list with drag-and-drop, role selection, and content editing [app/src/pages/playground/PlaygroundChatTemplate.tsx:77-181]() |
| `PlaygroundOutput` | `PlaygroundOutput.tsx` | Streaming response display, repetition management, and span linking [app/src/pages/playground/PlaygroundOutput.tsx:149-548]() |
| `PlaygroundInput` | `PlaygroundInput.tsx` | Template variable input form for testing prompts with different inputs |
| `PlaygroundDatasetExamplesTable` | `PlaygroundDatasetExamplesTable.tsx` | Batch dataset execution table with virtualization and status indicators [app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx:182-211]() |

**Component Hierarchy with Code Entities**

```mermaid
graph TB
    Playground["Playground<br/>Playground.tsx:136"]
    PlaygroundProvider["PlaygroundProvider<br/>contexts/PlaygroundContext"]
    PlaygroundContent["PlaygroundContent()<br/>Playground.tsx:232"]
    
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
        PlaygroundOutput["PlaygroundOutput<br/>PlaygroundOutput.tsx:149"]
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

Sources: [app/src/pages/playground/Playground.tsx:136-210](), [app/src/pages/playground/PlaygroundChatTemplate.tsx:77-181](), [app/src/pages/playground/PlaygroundOutput.tsx:149-548](), [app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx:182-211]()

## State Management

The playground uses Zustand for centralized state management with a normalized message structure. The store is defined in `app/src/store/playground/playgroundStore.tsx` and maintains state across multiple "instances" (parallel prompts/configs).

**PlaygroundState Interface and Store Actions**

```mermaid
graph TB
    PlaygroundState["PlaygroundState<br/>store/playground/types.ts"]
    
    subgraph "Core_State_Fields"
        instances["instances: PlaygroundNormalizedInstance[]<br/>Prompts + Model Configs"]
        allInstanceMessages["allInstanceMessages: Record&lt;number, ChatMessage&gt;<br/>Normalized message storage"]
        dirtyInstances["dirtyInstances: Record&lt;number, boolean&gt;"]
        templateFormat["templateFormat: TemplateFormat"]
        streaming["streaming: boolean"]
    end
    
    subgraph "Instance_Actions"
        addInstance["addInstance()"]
        updateInstance["updateInstance()"]
        deleteInstance["deleteInstance()"]
    end
    
    subgraph "Execution_Actions"
        runPlaygroundInstances["runPlaygroundInstances()"]
        appendRepetitionOutput["appendRepetitionOutput()"]
        setRepetitionSpanId["setRepetitionSpanId()"]
        setRepetitionError["setRepetitionError()"]
    end
    
    PlaygroundState --> instances
    PlaygroundState --> allInstanceMessages
    PlaygroundState --> addInstance
    PlaygroundState --> updateInstance
    PlaygroundState --> runPlaygroundInstances
    PlaygroundState --> appendRepetitionOutput
```

Sources: [app/src/store/playground/types.ts:247-457](), [app/src/store/playground/playgroundStore.tsx:250-718]()

**Normalized Message Storage Pattern**

To avoid data redundancy and simplify reordering, messages are stored in a flat map. `PlaygroundNormalizedChatTemplate` contains only message IDs [app/src/store/playground/types.ts:230-245](). The `normalizeChatTemplate()` function [app/src/store/playground/playgroundStore.tsx:104-118]() facilitates this conversion.

```mermaid
graph TB
    Instance["PlaygroundNormalizedInstance<br/>id: 0"]
    Template["template.messageIds: [2, 3]<br/>PlaygroundNormalizedChatTemplate"]
    MessageStore["allInstanceMessages<br/>Record&lt;number, ChatMessage&gt;"]
    Msg2["2: ChatMessage<br/>{role: 'system', content: '...'}"]
    Msg3["3: ChatMessage<br/>{role: 'user', content: '...'}"]
    
    Instance --> Template
    Template --> MessageStore
    MessageStore --> Msg2
    MessageStore --> Msg3
```

Sources: [app/src/store/playground/types.ts:230-245](), [app/src/store/playground/playgroundStore.tsx:104-118]()

## Communication and Streaming

The playground uses GraphQL subscriptions to handle streaming responses from LLM providers.

**GraphQL Communication Pattern**

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "PlaygroundOutput.tsx"
    participant Relay as "Relay Environment"
    participant Backend as "subscriptions.py"
    participant LLM as "PlaygroundStreamingClient"
    
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

Sources: [app/src/pages/playground/PlaygroundOutput.tsx:395-439](), [src/phoenix/server/api/subscriptions.py:76-134]()

The `handleChatCompletionSubscriptionPayload` callback [app/src/pages/playground/PlaygroundOutput.tsx:237-323]() updates the store based on the chunk type:
- `TextChunk`: Incremental content update.
- `ToolCallChunk`: Accumulates partial tool call arguments.
- `ChatCompletionSubscriptionResult`: Links the result to a database `Span` [src/phoenix/server/api/subscriptions.py:129-132]().

## Template and Message Editing

`PlaygroundChatTemplate` provides a drag-and-drop interface for conversation composition using `@dnd-kit/sortable` [app/src/pages/playground/PlaygroundChatTemplate.tsx:111-134]().

**Message Editor Features:**
- **Role Selection**: Uses `MessageRoleSelect` to toggle between `system`, `user`, `assistant`, and `tool` roles [app/src/pages/playground/PlaygroundChatTemplate.tsx:57]().
- **Template Support**: Supports Mustache and f-string formats via `TemplateEditor` [app/src/pages/playground/PlaygroundChatTemplate.tsx:37]().
- **Tool Calls**: AI messages include a `ChatMessageToolCallsEditor` for manual tool call entry or editing streamed results [app/src/pages/playground/PlaygroundChatTemplate.tsx:54]().

## Instance Management

The playground allows multiple parallel instances for prompt engineering comparisons.
- **Limit**: Defined by `NUM_MAX_PLAYGROUND_INSTANCES` (typically 4).
- **Repetitions**: Each instance can run multiple times with different seeds/parameters, managed by `PlaygroundRepetition` [app/src/store/playground/types.ts:130-136]().
- **Normalization**: `createNormalizedPlaygroundInstance` [app/src/store/playground/playgroundStore.tsx:153-165]() generates a new instance with a default chat template.

## Credential Handling

Credentials (API keys, base URLs) are managed through the `CredentialsContext` [app/src/pages/playground/PlaygroundOutput.tsx:159]() and rendered in `PlaygroundCredentialsDropdown`.

**Credential Flow:**
1. User provides credentials in the UI or settings.
2. Credentials are stored in `CredentialsStore` [app/src/store/credentialsStore.tsx]().
3. During execution, `getChatCompletionInput` [app/src/pages/playground/playgroundUtils.ts:782-828]() maps these credentials to `GenerativeCredentialInput` objects sent to the backend.

## Span Integration

The Playground can be populated from existing traces to debug specific LLM calls.
- **Hydration**: `transformSpanAttributesToPlaygroundInstance` [app/src/pages/playground/playgroundUtils.ts:625-772]() parses OpenInference semantic conventions (e.g., `llm.input_messages`, `llm.invocation_parameters`) from a `Span`.
- **Tool Mapping**: `processAttributeToolCalls` [app/src/pages/playground/playgroundUtils.ts:148-219]() converts provider-specific tool call formats (OpenAI, Anthropic, etc.) into the internal `ChatMessage["toolCalls"]` format.

Sources: [app/src/pages/playground/playgroundUtils.ts:148-219](), [app/src/pages/playground/playgroundUtils.ts:625-772](), [app/src/store/playground/playgroundStore.tsx:153-165]()

---

# Page: AI Assistant (PxI) Interface

# AI Assistant (PxI) Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/agent/chat/__tests__/buildAgentChatRequestBody.test.ts](app/src/agent/chat/__tests__/buildAgentChatRequestBody.test.ts)
- [app/src/agent/chat/__tests__/shouldSendAutomatically.test.ts](app/src/agent/chat/__tests__/shouldSendAutomatically.test.ts)
- [app/src/agent/chat/buildAgentChatRequestBody.ts](app/src/agent/chat/buildAgentChatRequestBody.ts)
- [app/src/agent/extensions/__tests__/capabilities.test.ts](app/src/agent/extensions/__tests__/capabilities.test.ts)
- [app/src/agent/extensions/__tests__/toolRegistry.test.ts](app/src/agent/extensions/__tests__/toolRegistry.test.ts)
- [app/src/agent/extensions/capabilities.ts](app/src/agent/extensions/capabilities.ts)
- [app/src/agent/extensions/toolRegistry.ts](app/src/agent/extensions/toolRegistry.ts)
- [app/src/agent/tools/playgroundPrompt/__tests__/playgroundPrompt.test.ts](app/src/agent/tools/playgroundPrompt/__tests__/playgroundPrompt.test.ts)
- [app/src/components/agent/AgentChatPanel.tsx](app/src/components/agent/AgentChatPanel.tsx)
- [app/src/components/agent/AgentChatPanelView.tsx](app/src/components/agent/AgentChatPanelView.tsx)
- [app/src/components/agent/AgentChatWidget.tsx](app/src/components/agent/AgentChatWidget.tsx)
- [app/src/components/agent/AgentExperimentalSettings.tsx](app/src/components/agent/AgentExperimentalSettings.tsx)
- [app/src/components/agent/AgentFabPositioner.tsx](app/src/components/agent/AgentFabPositioner.tsx)
- [app/src/components/agent/AgentSettingsForm.tsx](app/src/components/agent/AgentSettingsForm.tsx)
- [app/src/components/agent/AgentWebSearchToggle.tsx](app/src/components/agent/AgentWebSearchToggle.tsx)
- [app/src/components/agent/Chat.tsx](app/src/components/agent/Chat.tsx)
- [app/src/components/agent/ChatEmptyShaderHero.tsx](app/src/components/agent/ChatEmptyShaderHero.tsx)
- [app/src/components/agent/PxiGlyph.tsx](app/src/components/agent/PxiGlyph.tsx)
- [app/src/components/agent/ResizableFloatingPanel.tsx](app/src/components/agent/ResizableFloatingPanel.tsx)
- [app/src/components/agent/ToolPart.tsx](app/src/components/agent/ToolPart.tsx)
- [app/src/components/agent/__tests__/AgentChatPanelView.test.tsx](app/src/components/agent/__tests__/AgentChatPanelView.test.tsx)
- [app/src/components/agent/__tests__/AgentChatWidget.test.tsx](app/src/components/agent/__tests__/AgentChatWidget.test.tsx)
- [app/src/components/agent/__tests__/AgentFabPositioner.test.tsx](app/src/components/agent/__tests__/AgentFabPositioner.test.tsx)
- [app/src/components/agent/__tests__/ResizableFloatingPanel.test.tsx](app/src/components/agent/__tests__/ResizableFloatingPanel.test.tsx)
- [app/src/components/agent/__tests__/agentFabPositioning.test.ts](app/src/components/agent/__tests__/agentFabPositioning.test.ts)
- [app/src/components/agent/agentFabPositioning.ts](app/src/components/agent/agentFabPositioning.ts)
- [app/src/components/agent/index.tsx](app/src/components/agent/index.tsx)
- [app/src/components/agent/useAgentChat.ts](app/src/components/agent/useAgentChat.ts)
- [app/src/components/agent/useAgentChatPanelState.ts](app/src/components/agent/useAgentChatPanelState.ts)
- [app/src/components/core/icon/Icons.tsx](app/src/components/core/icon/Icons.tsx)
- [app/src/components/core/overlay/Modal.tsx](app/src/components/core/overlay/Modal.tsx)
- [app/src/components/core/overlay/Popover.tsx](app/src/components/core/overlay/Popover.tsx)
- [app/src/components/core/overlay/constants.ts](app/src/components/core/overlay/constants.ts)
- [app/src/components/core/toast/styles.ts](app/src/components/core/toast/styles.ts)
- [app/src/components/core/zIndex.ts](app/src/components/core/zIndex.ts)
- [app/src/hooks/useHasOpenModal.ts](app/src/hooks/useHasOpenModal.ts)
- [app/src/pages/settings/SettingsAgentsPage.tsx](app/src/pages/settings/SettingsAgentsPage.tsx)
- [app/src/store/__tests__/agentStore.test.ts](app/src/store/__tests__/agentStore.test.ts)
- [app/src/store/agentStore.ts](app/src/store/agentStore.ts)
- [app/src/types/geometry.ts](app/src/types/geometry.ts)
- [app/src/types/index.ts](app/src/types/index.ts)
- [app/stories/AgentChatWidgetButton.stories.tsx](app/stories/AgentChatWidgetButton.stories.tsx)
- [app/tests/pxi/fixtures.ts](app/tests/pxi/fixtures.ts)
- [app/tests/pxi/ingest-traces-smoke.spec.ts](app/tests/pxi/ingest-traces-smoke.spec.ts)
- [src/phoenix/server/agents/capabilities/tools/external/__init__.py](src/phoenix/server/agents/capabilities/tools/external/__init__.py)
- [src/phoenix/server/agents/prompts/__init__.py](src/phoenix/server/agents/prompts/__init__.py)
- [src/phoenix/server/agents/prompts/skills/annotate-spans/SKILL.md](src/phoenix/server/agents/prompts/skills/annotate-spans/SKILL.md)
- [src/phoenix/server/agents/prompts/skills/debug-trace/SKILL.md](src/phoenix/server/agents/prompts/skills/debug-trace/SKILL.md)
- [src/phoenix/server/agents/skills/__init__.py](src/phoenix/server/agents/skills/__init__.py)
- [src/phoenix/server/agents/skills/annotate_spans.py](src/phoenix/server/agents/skills/annotate_spans.py)
- [src/phoenix/server/agents/skills/debug_trace.py](src/phoenix/server/agents/skills/debug_trace.py)
- [tests/unit/server/agents/test_agent_factory.py](tests/unit/server/agents/test_agent_factory.py)

</details>



The AI Assistant (Phoenix Intelligence, or PxI) is a built-in chat interface that allows users to interact with their observability data using natural language. It leverages a server-side agentic framework to perform tasks such as querying traces, summarizing sessions, and interacting with external tools.

## System Overview

The PxI interface is a multi-surface React application that communicates with a FastAPI-based agent backend. It is designed to be "always-on," maintaining chat state even when the UI is hidden, and supports context-aware interactions by automatically attaching relevant trace or span identifiers to requests.

### Key Components
- **AgentChatPanel**: The primary container for the docked chat interface [app/src/components/agent/AgentChatPanel.tsx:67-75]().
- **AgentChatWidget**: The floating action button (FAB) that triggers the assistant and provides "thinking" state visualizations [app/src/components/agent/AgentChatWidget.tsx:226-300]().
- **useAgentChat**: A custom hook that bridges the React UI to the `ai` SDK runtime and Phoenix-specific logic [app/src/components/agent/useAgentChat.ts:54-161]().
- **AgentStore**: A Zustand-based store for persisting sessions, capabilities, and observability preferences [app/src/store/agentStore.ts:212-230]().
- **AgentChatRuntime**: A singleton registry that ensures chat streams survive component remounts by caching `Chat` instances [app/src/components/agent/useAgentChat.ts:80-86]().

## Data Flow: Natural Language to Code Entities

The following diagram illustrates how a user's natural language prompt is transformed into a structured request and how state is managed across the frontend.

### PxI Request Lifecycle
```mermaid
graph TD
    User["User Prompt"] --> UI["ChatView"]
    UI --> Hook["useAgentChat"]
    Hook --> Runtime["AgentChatRuntime (Singleton)"]
    Hook --> ReqBuilder["buildAgentChatRequestBody"]
    
    ReqBuilder --> Context["selectActiveContexts"]
    Context --> Store["agentStore (Zustand)"]
    
    Runtime --> Transport["DefaultChatTransport"]
    Transport --> API["POST /v1/agents/{agent_id}/sessions/{session_id}/chat"]
    
    subgraph "State Persistence"
        Store --> LocalStorage["localStorage ('arize-phoenix-assistant')"]
    end
    
    API --> Backend["agent_factory.py"]
    Backend --> Agent["pydantic_ai.Agent"]

    Sources: [app/src/components/agent/useAgentChat.ts:84-112](), [app/src/store/agentStore.ts:4-10](), [tests/unit/server/agents/test_agent_factory.py:28-40]()
```

## Frontend Architecture

### Session Management
Sessions are stored in the `agentStore` and persisted to local storage. Each session contains its message history, model configuration, and usage metrics [app/src/store/agentStore.ts:103-117](). By default, Phoenix retains up to 3 recent sessions when the `session.storeSessions` capability is enabled [app/src/store/agentStore.ts:144]().

| Entity | Role | Source |
| :--- | :--- | :--- |
| `AgentSession` | Stores `messages`, `modelConfig`, `context` IDs, and `usage`. | [app/src/store/agentStore.ts:103-117]() |
| `AgentUIMessage` | Extension of Vercel AI SDK `UIMessage` with Phoenix metadata. | [app/src/components/agent/Chat.tsx:15]() |
| `AgentPosition` | Determines if the panel is `detached` (floating) or `pinned` (side-docked). | [app/src/store/agentStore.ts:34]() |
| `AgentEditPermissionMode` | Controls if tool edits require `manual` approval or `bypass`. | [app/src/store/agentStore.ts:74-79]() |

### The Chat Runtime
To prevent streams from breaking when a user navigates between pages or closes the sidebar, Phoenix uses a `AgentChatRuntime`. This runtime maintains imperative `Chat` instances from the `@ai-sdk/react` library in a registry keyed by `sessionId` [app/src/components/agent/useAgentChat.ts:80-86](). This allows the UI to remount without losing the underlying fetch connection.

### Capability Flags
The assistant's behavior is governed by `AgentCapabilities`. These flags control which tools are exposed to the model and how the UI renders certain components [app/src/store/agentStore.ts:12-15]().
- **session.storeSessions**: Enables multi-session history persistence [app/src/store/agentStore.test.ts:128-131]().
- **webAccessEnabled**: Server-side flag indicating if the agent can use native web tools like `WebSearchTool` [app/src/store/agentStore.ts:49-50]().

## Tooling and Generative UI

PxI supports a "Human-in-the-loop" pattern called **Elicitation**. When an agent requires user input (e.g., via an `ask_user` tool), it triggers a `PendingElicitation` state in the store [app/src/store/agentStore.ts:18]().

### Tool Execution Flow
Tool calls are handled via a central `toolRegistry` that maps server-advertised tool names to frontend execution logic.

```mermaid
graph LR
    subgraph "Client Tool Handling"
        A["useAgentChat"] -- "onToolCall" --> B["handleAgentToolCall"]
        B -- "lookup" --> C["RegisteredAgentTool"]
        C -- "if 'ask_user'" --> D["handleElicitationSubmit"]
        C -- "if 'bash'" --> E["handleBashToolCall"]
    end
    
    D --> F["ElicitationCarousel (UI)"]
    E --> G["Browser Sandbox"]
    
    Sources: [app/src/components/agent/useAgentChat.ts:122-136](), [app/src/agent/extensions/toolRegistry.ts:160-167](), [app/src/agent/extensions/toolRegistry.ts:187-206]()
```

### Key Tool Components
- `ToolPart`: A component for rendering tool-specific UI parts, such as bash outputs or dataset previews [app/src/components/agent/ToolPart.tsx:85-139]().
- `AgentChatWidget`: Renders a "shimmer" and "glow" effect when the assistant is in a `streaming` or `submitted` status [app/src/components/agent/AgentChatWidget.tsx:228-254]().
- `AgentContextPills`: Visualizes active context references (e.g., trace IDs) attached to the current session [app/src/components/agent/Chat.tsx:39]().

## Integration with Phoenix Server

### Request Transformation
Before sending a message, the frontend constructs the request body by injecting metadata:
1. **Contexts**: Active trace IDs or span IDs selected in the UI via `selectActiveContexts` [app/src/components/agent/useAgentChat.ts:114]().
2. **Observability**: Settings for `storeLocalTraces` and `exportRemoteTraces` [app/src/store/agentStore.ts:66-72]().
3. **Model Selection**: The specific provider (e.g., Anthropic, OpenAI) and model parameters [app/src/store/agentStore.ts:119-123]().

### Usage Tracking
Completion metadata, including token counts (prompt, completion, and cache details), is captured from the agent's response and updated in the `agentStore` via `setSessionUsage` [app/src/components/agent/useAgentChat.ts:138-147]().

Sources:
- `app/src/components/agent/Chat.tsx`
- `app/src/components/agent/useAgentChat.ts`
- `app/src/store/agentStore.ts`
- `app/src/agent/extensions/toolRegistry.ts`
- `app/src/components/agent/AgentChatPanel.tsx`
- `app/src/components/agent/AgentChatWidget.tsx`
- `app/src/components/agent/ToolPart.tsx`
- `tests/unit/server/agents/test_agent_factory.py`

---

# Page: Feature Systems

# Feature Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/schema.graphql](app/schema.graphql)
- [app/src/components/trace/SpanKindIcon.tsx](app/src/components/trace/SpanKindIcon.tsx)
- [app/src/window.d.ts](app/src/window.d.ts)
- [cspell.json](cspell.json)
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
- [src/phoenix/server/api/input_types/SpanSort.py](src/phoenix/server/api/input_types/SpanSort.py)
- [src/phoenix/server/api/mutations/__init__.py](src/phoenix/server/api/mutations/__init__.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/routers/v1/experiment_evaluations.py](src/phoenix/server/api/routers/v1/experiment_evaluations.py)
- [src/phoenix/server/api/routers/v1/experiment_runs.py](src/phoenix/server/api/routers/v1/experiment_runs.py)
- [src/phoenix/server/api/routers/v1/experiments.py](src/phoenix/server/api/routers/v1/experiments.py)
- [src/phoenix/server/api/schema.py](src/phoenix/server/api/schema.py)
- [src/phoenix/server/api/types/Dataset.py](src/phoenix/server/api/types/Dataset.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/settings.py](src/phoenix/settings.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [tests/unit/server/api/routers/v1/test_experiments.py](tests/unit/server/api/routers/v1/test_experiments.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)

</details>



This document provides an overview of Phoenix's major feature areas and how they integrate across client libraries, server components, and the user interface. Phoenix's functionality is organized into primary feature systems that work together to provide comprehensive AI observability, evaluation, and experimentation capabilities.

For detailed information about each system:
- Tracing and instrumentation setup: see [Tracing & Observability](#5.1)
- Evaluation framework implementation: see [Evaluation Framework](#5.2)
- Dataset and experiment management: see [Datasets & Experiments](#5.3)
- Prompt versioning and templating: see [Prompt Management](#5.4)
- LLM Playground and provider abstraction: see [Playground System](#5.5)
- AI Agent Backend: see [AI Agent Backend (PxI)](#5.6)
- Sessions and Annotations: see [Sessions & Annotations](#5.7)

## Feature System Architecture

Phoenix is organized into major feature systems that span the entire stack from client instrumentation to server storage to UI visualization:

```mermaid
graph TB
    subgraph "Feature Systems"
        Tracing["Tracing & Observability<br/>phoenix.otel.register()"]
        Evals["Evaluation Framework<br/>arize-phoenix-evals"]
        Datasets["Datasets & Experiments<br/>client.datasets / client.experiments"]
        Prompts["Prompt Management<br/>client.prompts / PromptVersion"]
        Playground["Playground System<br/>Model Clients / Streaming"]
        AIAgent["AI Agent Backend (PxI)<br/>/agents REST endpoint"]
        Sessions["Sessions & Annotations<br/>ProjectSession / Annotation"]
    end
    
    subgraph "Client Entities (Code Space)"
        PyClient["[src/phoenix/client/client.py] <br/> PhoenixClient"]
        PyOtel["[src/phoenix/otel/phoenix_otel.py] <br/> register_phoenix_otel()"]
        PyEvals["[src/phoenix/evals/evaluator.py] <br/> Evaluator"]
    end
    
    subgraph "Server Entities (Code Space)"
        FastAPIApp["[src/phoenix/server/app.py] <br/> create_app()"]
        GraphQLAPI["[src/phoenix/server/api/schema.py] <br/> build_graphql_schema()"]
        RESTAPI["[src/phoenix/server/api/routers/v1/__init__.py] <br/> v1_router"]
        DBModels["[src/phoenix/db/models.py] <br/> SQLAlchemy Models"]
        AgentRouter["[src/phoenix/server/api/routers/agents.py] <br/> create_agents_router()"]
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
Sources: [src/phoenix/server/app.py:175-181](), [src/phoenix/server/api/schema.py:33-42](), [src/phoenix/db/models.py:1-50](), [src/phoenix/server/api/routers/v1/experiments.py:40-40]()

## Core Feature Overviews

### Tracing & Observability
Phoenix provides an OpenTelemetry-native tracing backend. It ingests spans via OTLP (gRPC and HTTP) and organizes them into traces and projects. The system supports complex LLM app architectures, including RAG pipelines and multi-agent systems, by capturing inputs, outputs, and metadata as span attributes. The `SpanKind` enum categorizes different types of spans, such as `CHAIN`, `LLM`, `TOOL`, and `AGENT` [src/phoenix/server/api/types/Span.py:56-75](). Token counts for prompt and completion are tracked as specific span attributes [src/phoenix/db/models.py:94-104]().
For details, see [Tracing & Observability](#5.1).
Sources: [src/phoenix/server/api/types/Span.py:56-75](), [src/phoenix/db/models.py:94-104](), [src/phoenix/server/app.py:143-157]()

### Evaluation Framework
The evaluation system allows users to run LLM-based, code-based, or heuristic evaluators against traces or datasets. It includes a template engine for prompt-based evaluators and supports mapping span attributes to evaluator inputs. Evaluation results are stored as `Annotation` records linked to spans, traces, sessions, or experiment runs. The `AnnotatorKind` enum distinguishes between `LLM`, `HUMAN`, and `CODE` evaluators [app/schema.graphql:224-228]().
For details, see [Evaluation Framework](#5.2).
Sources: [app/schema.graphql:121-158](), [src/phoenix/server/api/queries.py:76-82](), [app/schema.graphql:203-206]()

### Datasets & Experiments
Phoenix manages versioned datasets consisting of `DatasetExample` records. The experimentation system allows running a "task" (e.g., a prompt or a chain) against a dataset version and recording the results in `ExperimentRuns`. This enables regression testing and side-by-side comparison of different models or prompts. The server runs background daemons like `ExperimentRunner` and `ExperimentSweeper` to manage these lifecycles [src/phoenix/server/app.py:185-186]().
For details, see [Datasets & Experiments](#5.3).
Sources: [src/phoenix/server/api/types/Dataset.py:44-50](), [app/schema.graphql:66-78](), [src/phoenix/server/app.py:185-186]()

### Prompt Management
The prompt system provides a central repository for prompt templates, supporting versioning, tagging, and model-specific invocation parameters. Prompts are treated as first-class citizens that can be pulled into the Playground or used as the basis for experiments. The `PromptVersion` type represents a specific version of a prompt, including its `PromptChatTemplate` and invocation parameters [src/phoenix/db/models.py:73-85]().
For details, see [Prompt Management](#5.4).
Sources: [src/phoenix/db/models.py:73-85](), [src/phoenix/server/api/queries.py:115-128](), [app/schema.graphql:1115-1150]()

### Playground System
The Playground is an interactive environment for testing prompts and models. It abstracts various LLM providers (OpenAI, Anthropic, Azure, AWS Bedrock) through a unified backend interface that handles streaming, credential management (secrets), and parameter tuning. The system supports advanced provider configurations like `AWSBedrockCustomProviderConfig` [app/schema.graphql:46-50]().
For details, see [Playground System](#5.5).
Sources: [src/phoenix/server/api/queries.py:53-57](), [app/schema.graphql:3-54](), [src/phoenix/server/api/queries.py:109-109]()

### AI Agent Backend (PxI)
The AI Agent Backend, also known as Phoenix Intelligence (PxI), provides server-side AI agent capabilities. It leverages a `pydantic-ai` agent factory, handles model selection, manages tool capabilities (like `MintlifyDocsMCPServer`), and resolves context for agent interactions [src/phoenix/server/app.py:85-85](). The system configuration controls features like `webAccessEnabled` and `assistantEnabled` [app/schema.graphql:89-119]().
For details, see [AI Agent Backend (PxI)](#5.6).
Sources: [src/phoenix/server/app.py:176-176](), [app/schema.graphql:80-119](), [src/phoenix/server/api/queries.py:21-24]()

### Sessions & Annotations
Phoenix groups related traces into `ProjectSession` objects, representing multi-turn conversations or extended interactions. The system allows for `Annotation` of these sessions, as well as individual spans and traces, providing a flexible mechanism for qualitative feedback and evaluation results. DataLoaders like `SessionAnnotationsBySessionDataLoader` optimize the retrieval of these relationships [src/phoenix/server/api/app.py:137-137]().
For details, see [Sessions & Annotations](#5.7).
Sources: [src/phoenix/server/api/types/ProjectSession.py:44-44](), [app/schema.graphql:121-158](), [src/phoenix/server/api/dataloaders/__init__.py:66-66]()

## Data Model Integration

The feature systems are unified by a shared database schema managed via SQLAlchemy.

| Feature Area | Primary Code Entities | Database Table (approx) |
| :--- | :--- | :--- |
| **Tracing** | `Span`, `Trace`, `Project` | `spans`, `traces`, `projects` |
| **Evaluations** | `Annotation`, `Evaluator` | `span_annotations`, `trace_annotations`, `session_annotations`, `evaluators` |
| **Experiments** | `Dataset`, `Experiment`, `ExperimentRun` | `datasets`, `experiments`, `experiment_runs` |
| **Prompts** | `Prompt`, `PromptVersion` | `prompts`, `prompt_versions` |
| **Sessions** | `ProjectSession` | `project_sessions` |

Sources: [src/phoenix/db/models.py:172-187](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:49-126](), [src/phoenix/server/api/queries.py:72-117]()

## Cross-System Data Flow

The following diagram illustrates how a single user action (running an experiment) bridges multiple systems and code entities:

```mermaid
sequenceDiagram
    participant User as "User (Client/UI)"
    participant REST as "REST API<br/>[src/phoenix/server/api/routers/v1/experiments.py]"
    participant GQL as "GraphQL API<br/>[src/phoenix/server/api/queries.py]"
    participant DB as "Database<br/>[src/phoenix/db/models.py]"
    participant Runner as "ExperimentRunner Daemon<br/>[src/phoenix/server/daemons/experiment_runner.py]"

    User->>REST: "POST /v1/datasets/{id}/experiments"
    REST->>DB: "Insert Experiment via models.Experiment"
    User->>GQL: "Mutation: runExperiment"
    GQL->>Runner: "Trigger Experiment Execution"
    Runner->>DB: "Fetch DatasetExample records"
    Note over Runner: "Execute Task Logic"
    Runner->>DB: "Insert ExperimentRun & Span results"
```
Sources: [src/phoenix/server/api/routers/v1/experiments.py:121-125](), [src/phoenix/server/app.py:185-186](), [src/phoenix/server/api/queries.py:83-92]()

## Common Infrastructure Features

### Authentication & Authorization
All feature systems are protected by a unified authentication layer supporting OAuth2, LDAP, and Local auth. The `AuthMethod` enum defines the supported authentication methods [src/phoenix/db/models.py:173-173]().

### Secrets Management
The server provides a secure way to store and retrieve LLM provider API keys used by the Playground and Evaluators. DataLoaders like `SecretsDataLoader` manage efficient access to these sensitive values [src/phoenix/server/api/app.py:136-136]().

### Cost Tracking
Phoenix includes a `SpanCostCalculator` that runs as a daemon to estimate token costs for spans based on model-specific pricing manifests [src/phoenix/server/app.py:187-188](). This is facilitated by the `GenerativeModelStore` which maintains pricing and model availability.
Sources: [src/phoenix/server/app.py:187-188](), [src/phoenix/server/api/dataloaders/__init__.py:74-90]()

---

# Page: Tracing & Observability

# Tracing & Observability

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/components/annotation/AnnotationInputLabel.tsx](app/src/components/annotation/AnnotationInputLabel.tsx)
- [app/src/components/annotation/__generated__/AnnotationSummaryGroup.graphql.ts](app/src/components/annotation/__generated__/AnnotationSummaryGroup.graphql.ts)
- [app/src/components/trace/AnnotationConfigList.tsx](app/src/components/trace/AnnotationConfigList.tsx)
- [app/src/components/trace/AnnotationFormProvider.tsx](app/src/components/trace/AnnotationFormProvider.tsx)
- [app/src/components/trace/AnnotatorKindToken.tsx](app/src/components/trace/AnnotatorKindToken.tsx)
- [app/src/components/trace/SpanAnnotationsEditor.tsx](app/src/components/trace/SpanAnnotationsEditor.tsx)
- [app/src/components/trace/TraceTree.tsx](app/src/components/trace/TraceTree.tsx)
- [app/src/components/trace/__generated__/SpanAnnotationsEditorCreateAnnotationMutation.graphql.ts](app/src/components/trace/__generated__/SpanAnnotationsEditorCreateAnnotationMutation.graphql.ts)
- [app/src/components/trace/__generated__/SpanAnnotationsEditorDeleteAnnotationMutation.graphql.ts](app/src/components/trace/__generated__/SpanAnnotationsEditorDeleteAnnotationMutation.graphql.ts)
- [app/src/components/trace/__generated__/SpanAnnotationsEditorEditAnnotationMutation.graphql.ts](app/src/components/trace/__generated__/SpanAnnotationsEditorEditAnnotationMutation.graphql.ts)
- [app/src/components/trace/__generated__/SpanAnnotationsEditorSpanAnnotationsListQuery.graphql.ts](app/src/components/trace/__generated__/SpanAnnotationsEditorSpanAnnotationsListQuery.graphql.ts)
- [app/src/components/trace/__generated__/SpanAnnotationsEditor_spanAnnotations.graphql.ts](app/src/components/trace/__generated__/SpanAnnotationsEditor_spanAnnotations.graphql.ts)
- [app/src/components/trace/__tests__/utils.test.ts](app/src/components/trace/__tests__/utils.test.ts)
- [app/src/components/trace/types.ts](app/src/components/trace/types.ts)
- [app/src/components/trace/utils.ts](app/src/components/trace/utils.ts)
- [app/src/pages/project/ProjectPage.tsx](app/src/pages/project/ProjectPage.tsx)
- [app/src/pages/project/SpanColumnSelector.tsx](app/src/pages/project/SpanColumnSelector.tsx)
- [app/src/pages/project/SpansTable.tsx](app/src/pages/project/SpansTable.tsx)
- [app/src/pages/project/TracesTable.tsx](app/src/pages/project/TracesTable.tsx)
- [app/src/pages/project/__generated__/ProjectPageQueriesSpansQuery.graphql.ts](app/src/pages/project/__generated__/ProjectPageQueriesSpansQuery.graphql.ts)
- [app/src/pages/project/__generated__/ProjectPageQueriesTracesQuery.graphql.ts](app/src/pages/project/__generated__/ProjectPageQueriesTracesQuery.graphql.ts)
- [app/src/pages/project/__generated__/ProjectPageQuery.graphql.ts](app/src/pages/project/__generated__/ProjectPageQuery.graphql.ts)
- [app/src/pages/project/__generated__/SpansTableSpansQuery.graphql.ts](app/src/pages/project/__generated__/SpansTableSpansQuery.graphql.ts)
- [app/src/pages/project/__generated__/SpansTable_spans.graphql.ts](app/src/pages/project/__generated__/SpansTable_spans.graphql.ts)
- [app/src/pages/project/__generated__/TracesTableQuery.graphql.ts](app/src/pages/project/__generated__/TracesTableQuery.graphql.ts)
- [app/src/pages/project/__generated__/TracesTable_spans.graphql.ts](app/src/pages/project/__generated__/TracesTable_spans.graphql.ts)
- [app/src/pages/trace/SpanAside.tsx](app/src/pages/trace/SpanAside.tsx)
- [app/src/pages/trace/SpanDetails.tsx](app/src/pages/trace/SpanDetails.tsx)
- [app/src/pages/trace/SpanFeedback.tsx](app/src/pages/trace/SpanFeedback.tsx)
- [app/src/pages/trace/SpanNotesEditor.tsx](app/src/pages/trace/SpanNotesEditor.tsx)
- [app/src/pages/trace/TraceDetails.tsx](app/src/pages/trace/TraceDetails.tsx)
- [app/src/pages/trace/TraceHeaderRootSpanAnnotations.tsx](app/src/pages/trace/TraceHeaderRootSpanAnnotations.tsx)
- [app/src/pages/trace/__generated__/SpanAsideAnnotationList_span.graphql.ts](app/src/pages/trace/__generated__/SpanAsideAnnotationList_span.graphql.ts)
- [app/src/pages/trace/__generated__/SpanAside_span.graphql.ts](app/src/pages/trace/__generated__/SpanAside_span.graphql.ts)
- [app/src/pages/trace/__generated__/SpanDetailsQuery.graphql.ts](app/src/pages/trace/__generated__/SpanDetailsQuery.graphql.ts)
- [app/src/pages/trace/__generated__/SpanFeedback_annotations.graphql.ts](app/src/pages/trace/__generated__/SpanFeedback_annotations.graphql.ts)
- [app/src/pages/trace/__generated__/SpanNotesEditorAddNoteMutation.graphql.ts](app/src/pages/trace/__generated__/SpanNotesEditorAddNoteMutation.graphql.ts)
- [app/src/pages/trace/__generated__/SpanNotesEditorQuery.graphql.ts](app/src/pages/trace/__generated__/SpanNotesEditorQuery.graphql.ts)
- [app/src/pages/trace/__generated__/TraceDetailsQuery.graphql.ts](app/src/pages/trace/__generated__/TraceDetailsQuery.graphql.ts)
- [app/src/pages/trace/__generated__/TraceHeaderRootSpanAnnotationsQuery.graphql.ts](app/src/pages/trace/__generated__/TraceHeaderRootSpanAnnotationsQuery.graphql.ts)
- [app/src/store/preferencesStore.tsx](app/src/store/preferencesStore.tsx)
- [app/src/store/tracingStore.tsx](app/src/store/tracingStore.tsx)
- [scripts/testing/send_spans.py](scripts/testing/send_spans.py)
- [src/phoenix/exceptions.py](src/phoenix/exceptions.py)
- [src/phoenix/trace/dsl/filter.py](src/phoenix/trace/dsl/filter.py)
- [src/phoenix/trace/dsl/query.py](src/phoenix/trace/dsl/query.py)
- [src/phoenix/trace/span_evaluations.py](src/phoenix/trace/span_evaluations.py)
- [src/phoenix/trace/trace_dataset.py](src/phoenix/trace/trace_dataset.py)
- [tests/unit/trace/dsl/test_filter.py](tests/unit/trace/dsl/test_filter.py)
- [tests/unit/trace/dsl/test_query.py](tests/unit/trace/dsl/test_query.py)
- [tests/unit/trace/test_span_evaluations.py](tests/unit/trace/test_span_evaluations.py)

</details>



## Purpose and Scope

This document describes Phoenix's OpenTelemetry-based tracing and observability system. It covers the instrumentation packages, OTLP collector endpoints, span ingestion pipeline, and trace data model. For information about evaluating traces, see [Evaluation Framework](#5.2). For dataset management and experiments, see [Datasets & Experiments](#5.3).

## Architecture Overview

Phoenix's tracing system is built on OpenTelemetry and follows the OTLP (OpenTelemetry Protocol) specification. Applications instrument their code using OpenTelemetry SDKs, which export spans to Phoenix's collector endpoints. Phoenix processes these spans through a queue-based bulk insertion pipeline before storing them in the database.

Title: Trace Ingestion Architecture
```mermaid
graph TB
    subgraph "Application Layer"
        App["Instrumented Application"]
        PYOTEL["arize-phoenix-otel<br/>(Python)"]
        TSOTEL["@arizeai/phoenix-otel<br/>(TypeScript)"]
        OpenInf["openinference-instrumentation-*<br/>(Framework Auto-instrumentation)"]
    end
    
    subgraph "Phoenix Server"
        HTTPCollector["HTTP OTLP Endpoint<br/>:6006/v1/traces"]
        GRPCCollector["gRPC OTLP Endpoint<br/>:4317"]
        SpanQueue["Span Queue"]
        BulkInserter["BulkInserter (phoenix.db.bulk_inserter.py)"]
        EventQueue["Event Queue (CanPutItem[DmlEvent])"]
        CostCalc["SpanCostCalculator (phoenix.server.daemons.span_cost_calculator.py)"]
    end
    
    subgraph "Storage (phoenix.db.models)"
        DB["Database (SQLAlchemy)"]
        SpansTable["models.Span"]
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

Sources: `[src/phoenix/db/bulk_inserter.py:51-87]()`, `[src/phoenix/db/bulk_inserter.py:157-175]()`, `[src/phoenix/server/prometheus.py:110-115]()`

## Phoenix OTEL Packages

Phoenix provides wrapper packages around OpenTelemetry primitives that simplify configuration with Phoenix-aware defaults.

### Python: arize-phoenix-otel

The `arize-phoenix-otel` package provides drop-in replacements for OpenTelemetry classes.

**Key Components:**

| Class/Function | Purpose |
|-------|---------|
| `register()` | One-line setup function for tracing |
| `TracerProvider` | Extended TracerProvider with Phoenix defaults |
| `HTTPSpanExporter` | HTTP OTLP exporter |
| `GRPCSpanExporter` | gRPC OTLP exporter |

### Trace Ingestion Pipeline

The `BulkInserter` class is responsible for the asynchronous persistence of spans and annotations. It manages an internal `deque` of spans and coordinates with various `QueueInserter` objects for annotations.

**Key Functions:**
- `_bulk_insert()`: The main loop that dequeues operations and executes database transactions [src/phoenix/db/bulk_inserter.py:126-155]().
- `_insert_spans()`: Batch inserts spans into the database using `insert_span()` [src/phoenix/db/bulk_inserter.py:157-175]().
- `_enqueue_span()`: Adds a new span to the processing queue [src/phoenix/db/bulk_inserter.py:121-122]().

Sources: `[src/phoenix/db/bulk_inserter.py:51-175]()`

## Observability Features

The Phoenix UI provides several features for visualizing and analyzing trace data, primarily through the `SpansTable` and `TracesTable`.

### Spans Table & Filtering

The `SpansTable` [app/src/pages/project/SpansTable.tsx:183]() displays a list of spans. It utilizes a Domain Specific Language (DSL) for advanced filtering.

**Filtering Logic:**
Filtering is powered by the `SpanFilter` class [src/phoenix/trace/dsl/filter.py:147](). It takes a condition string, parses it using Python's `ast` module, and translates it into SQLAlchemy expressions.

- `_NAMES`: Maps human-readable keys (e.g., `latency_ms`, `status_code`, `name`) to database columns [src/phoenix/trace/dsl/filter.py:125-133]().
- `_apply_eval_aliasing()`: Handles joining the `span_annotation` table when filters refer to evaluations (e.g., `evals['relevance'].label == 'high'`) [src/phoenix/trace/dsl/filter.py:163]().
- `AliasedAnnotationRelation`: Manages SQL aliases for multiple evaluation joins [src/phoenix/trace/dsl/filter.py:36-50]().
- `_FLOAT_ATTRIBUTES`: Identifies attributes that should be treated as floats (e.g., `llm.token_count.total`) [src/phoenix/trace/dsl/filter.py:90-96]().

Sources: `[app/src/pages/project/SpansTable.tsx:183]()`, `[src/phoenix/trace/dsl/filter.py:36-163]()`

### Trace Tree Visualization

Traces are visualized as hierarchical trees in the UI.

Title: UI Trace Visualization Flow
```mermaid
graph TD
    subgraph "Frontend Components"
        TraceTree["TraceTree (app/src/components/trace/TraceTree.tsx)"]
        SpanTreeItem["SpanTreeItem (app/src/components/trace/TraceTree.tsx)"]
        TraceDetails["TraceDetails (app/src/pages/trace/TraceDetails.tsx)"]
        ConnectedTraceTree["ConnectedTraceTree (app/src/pages/trace/ConnectedTraceTree.tsx)"]
    end

    subgraph "Logic & Utilities"
        createSpanTree["createSpanTree (app/src/components/trace/utils.ts)"]
        SpanTreeNode["SpanTreeNode Type (app/src/components/trace/utils.ts)"]
    end

    TraceDetails -->|"uses"| ConnectedTraceTree
    ConnectedTraceTree -->|"uses"| TraceTree
    TraceTree -->|"calls"| createSpanTree
    createSpanTree -->|"returns"| SpanTreeNode
    TraceTree -->|"renders"| SpanTreeItem
```

**Key Tree Logic:**
- `createSpanTree()`: Reconstructs the parent-child hierarchy from a flat array of spans based on `parentId` [app/src/components/trace/utils.ts:10-20]().
- `SpanTreeItem`: Renders an individual span node, showing its kind, status, latency, and token counts [app/src/components/trace/TraceTree.tsx:101-138]().
- `TimelineBar`: Visualizes the span's duration relative to the overall trace time range [app/src/components/trace/TraceTree.tsx:197-207]().
- `TraceDetails`: Manages the overall layout for trace viewing, including the tree and details panels [app/src/pages/trace/TraceDetails.tsx:57-182]().

Sources: `[app/src/components/trace/TraceTree.tsx:31-207]()`, `[app/src/components/trace/utils.ts:10-20]()`, `[app/src/pages/trace/TraceDetails.tsx:57-184]()`

### Span Details & Annotations

The `SpanDetails` component [app/src/pages/trace/SpanDetails.tsx:146]() provides deep inspection of a single span.

**Data Display:**
- **Attributes**: Displays OpenInference semantic conventions (LLM, Retrieval, Tool, etc.) [app/src/pages/trace/SpanDetails.tsx:105-111]().
- **Input/Output**: Renders values based on MIME types, including support for Markdown and JSON [app/src/pages/trace/SpanDetails.tsx:203-211]().
- **Events**: Lists span events such as exceptions [app/src/pages/trace/SpanDetails.tsx:212-216]().

**Annotation Management:**
The `SpanAnnotationsEditor` [app/src/components/trace/SpanAnnotationsEditor.tsx:70]() allows users to add or edit feedback.
- `useMutation`: Uses Relay mutations to create, edit, or delete annotations [app/src/components/trace/SpanAnnotationsEditor.tsx:140-180]().
- `AnnotatorKind`: Tracks whether an annotation was created by a `HUMAN`, `LLM`, or `CODE` [app/src/pages/project/__generated__/TracesTable_spans.graphql.ts:12]().
- `SpanAnnotationInput`: Provides the form for entering labels, scores, and explanations [app/src/components/trace/SpanAnnotationsEditor.tsx:61]().

Sources: `[app/src/pages/trace/SpanDetails.tsx:146-230]()`, `[app/src/components/trace/SpanAnnotationsEditor.tsx:70-203]()`, `[app/src/pages/project/__generated__/TracesTable_spans.graphql.ts:12-101]()`

## Performance Monitoring

Phoenix uses Prometheus to track the health and performance of the tracing pipeline.

**Key Metrics:**
- `BULK_LOADER_SPAN_INSERTION_TIME`: Histogram of database insertion latency [src/phoenix/server/prometheus.py:40-45]().
- `SPAN_QUEUE_SIZE`: Current number of spans waiting to be processed [src/phoenix/server/prometheus.py:110-114]().
- `BULK_LOADER_SPAN_EXCEPTIONS`: Counter for failed span insertions [src/phoenix/server/prometheus.py:47-51]().

Sources: `[src/phoenix/server/prometheus.py:40-120]()`

## Configuration & Preferences

The UI behavior for tracing is controlled by the `preferencesStore` [app/src/store/preferencesStore.tsx:75]().

**Relevant Preferences:**
- `traceStreamingEnabled`: Toggles real-time span updates [app/src/store/preferencesStore.tsx:85]().
- `showMetricsInTraceTree`: Controls visibility of latency/tokens in the tree view [app/src/store/preferencesStore.tsx:98]().
- `isAnnotatingSpans`: Toggles the annotation side panel in `SpanDetails` [app/src/store/preferencesStore.tsx:111]().
- `displayTimezone`: Configures the timezone for displaying timestamps across the trace UI [app/src/store/preferencesStore.tsx:133]().

Sources: `[app/src/store/preferencesStore.tsx:75-160]()`

---

# Page: Evaluation Framework

# Evaluation Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/components/evaluators/EvaluatorOutputPreview.tsx](app/src/components/evaluators/EvaluatorOutputPreview.tsx)
- [app/src/components/evaluators/__generated__/EvaluatorOutputPreviewMutation.graphql.ts](app/src/components/evaluators/__generated__/EvaluatorOutputPreviewMutation.graphql.ts)
- [app/src/pages/dataset/evaluators/DatasetEvaluatorsPage.tsx](app/src/pages/dataset/evaluators/DatasetEvaluatorsPage.tsx)
- [app/src/pages/dataset/evaluators/DatasetEvaluatorsTable.tsx](app/src/pages/dataset/evaluators/DatasetEvaluatorsTable.tsx)
- [app/src/pages/dataset/evaluators/__generated__/DatasetEvaluatorsTableEvaluatorsQuery.graphql.ts](app/src/pages/dataset/evaluators/__generated__/DatasetEvaluatorsTableEvaluatorsQuery.graphql.ts)
- [app/src/pages/dataset/evaluators/__generated__/DatasetEvaluatorsTable_evaluators.graphql.ts](app/src/pages/dataset/evaluators/__generated__/DatasetEvaluatorsTable_evaluators.graphql.ts)
- [app/src/pages/dataset/evaluators/__generated__/datasetEvaluatorsLoaderQuery.graphql.ts](app/src/pages/dataset/evaluators/__generated__/datasetEvaluatorsLoaderQuery.graphql.ts)
- [app/src/pages/dataset/evaluators/datasetEvaluatorsLoader.ts](app/src/pages/dataset/evaluators/datasetEvaluatorsLoader.ts)
- [app/src/pages/evaluators/DatasetEvaluatorsTable.tsx](app/src/pages/evaluators/DatasetEvaluatorsTable.tsx)
- [app/src/pages/evaluators/EvaluatorsPage.tsx](app/src/pages/evaluators/EvaluatorsPage.tsx)
- [app/src/pages/evaluators/EvaluatorsTable.tsx](app/src/pages/evaluators/EvaluatorsTable.tsx)
- [app/src/pages/evaluators/PromptCell.tsx](app/src/pages/evaluators/PromptCell.tsx)
- [app/src/pages/evaluators/__generated__/EvaluatorsTable_row.graphql.ts](app/src/pages/evaluators/__generated__/EvaluatorsTable_row.graphql.ts)
- [app/src/pages/evaluators/__generated__/GlobalEvaluatorsTableEvaluatorsQuery.graphql.ts](app/src/pages/evaluators/__generated__/GlobalEvaluatorsTableEvaluatorsQuery.graphql.ts)
- [app/src/pages/evaluators/__generated__/GlobalEvaluatorsTable_evaluators.graphql.ts](app/src/pages/evaluators/__generated__/GlobalEvaluatorsTable_evaluators.graphql.ts)
- [app/src/pages/evaluators/__generated__/evaluatorsPageLoaderQuery.graphql.ts](app/src/pages/evaluators/__generated__/evaluatorsPageLoaderQuery.graphql.ts)
- [src/phoenix/db/insertion/document_annotation.py](src/phoenix/db/insertion/document_annotation.py)
- [src/phoenix/db/insertion/span_annotation.py](src/phoenix/db/insertion/span_annotation.py)
- [src/phoenix/db/insertion/trace_annotation.py](src/phoenix/db/insertion/trace_annotation.py)
- [src/phoenix/db/insertion/types.py](src/phoenix/db/insertion/types.py)
- [src/phoenix/db/migrations/versions/02463bd83119_add_evaluators.py](src/phoenix/db/migrations/versions/02463bd83119_add_evaluators.py)
- [src/phoenix/db/types/prompts.py](src/phoenix/db/types/prompts.py)
- [src/phoenix/server/api/input_types/EvaluatorPreviewInput.py](src/phoenix/server/api/input_types/EvaluatorPreviewInput.py)
- [src/phoenix/server/api/mutations/evaluator_mutations.py](src/phoenix/server/api/mutations/evaluator_mutations.py)
- [src/phoenix/server/api/types/Evaluator.py](src/phoenix/server/api/types/Evaluator.py)
- [tests/integration/client/test_annotations.py](tests/integration/client/test_annotations.py)
- [tests/integration/client/test_prompts.py](tests/integration/client/test_prompts.py)
- [tests/unit/db/test_models.py](tests/unit/db/test_models.py)
- [tests/unit/server/api/mutations/test_evaluator_mutations.py](tests/unit/server/api/mutations/test_evaluator_mutations.py)
- [tests/unit/server/api/mutations/test_evaluator_preview_mutation.py](tests/unit/server/api/mutations/test_evaluator_preview_mutation.py)
- [tests/unit/server/api/test_create_llm_evaluator_from_inline.py](tests/unit/server/api/test_create_llm_evaluator_from_inline.py)
- [tests/unit/server/api/types/test_Dataset.py](tests/unit/server/api/types/test_Dataset.py)
- [tests/unit/server/api/types/test_Evaluator.py](tests/unit/server/api/types/test_Evaluator.py)

</details>



## Purpose and Scope

The Evaluation Framework provides a unified system for assessing LLM application performance through automated evaluators. It spans both a standalone Python library (`arize-phoenix-evals`) for client-side execution and an integrated server-side system that powers the Phoenix Playground and Experiment workflows.

The framework supports:
- **LLM Evaluators**: Prompt-based classification and generation using various providers (OpenAI, Anthropic, Google, Bedrock, etc.).
- **Code Evaluators**: Python or TypeScript-based logic for deterministic metrics (e.g., JSON diff, Levenshtein distance) executed in sandboxed environments.
- **Built-in Evaluators**: Pre-configured templates for common tasks like Hallucination and Relevance.
- **Input Mapping**: Flexible data extraction using JSONPath to bind evaluation logic to diverse data structures.

**Sources:** [src/phoenix/server/api/types/Evaluator.py:50-55](), [src/phoenix/server/api/mutations/evaluator_mutations.py:31-35]()

---

## Architecture Overview

Phoenix utilizes a dual-layered architecture where evaluations can be triggered programmatically via the SDK or interactively through the Phoenix Server's GraphQL API.

### System Architecture Diagram

This diagram bridges the high-level evaluation concepts with the specific code entities responsible for execution and storage.

```mermaid
graph TD
    subgraph "Execution Layer"
        MutationMixin["mutations/chat_mutations.py: ChatCompletionMutationMixin"]
        EvaluatorPreviews["mutations/chat_mutations.py: evaluator_previews"]
        CodeRunner["mutations/chat_mutations.py: CodeEvaluatorRunner"]
    end

    subgraph "Evaluator Entity Space"
        BaseEval["evaluators.py: BaseEvaluator (ABC)"]
        LLMEval["evaluators.py: LLMEvaluator"]
        BuiltinEval["evaluators.py: BuiltInEvaluator"]
        CodeEval["evaluators.py: CodeEvaluator"]
        
        BaseEval <|-- LLMEval
        BaseEval <|-- BuiltinEval
        BaseEval <|-- CodeEval
    end

    subgraph "Data & Storage"
        InputMap["models.py: InputMapping"]
        Annotation["models.py: SpanAnnotation"]
        OutputConfig["annotation_configs.py: OutputConfigType"]
        DB_Eval["models.py: Evaluator"]
        SandboxCfg["models.py: SandboxConfig"]
    end

    MutationMixin -->|previews| BuiltinEval
    EvaluatorPreviews -->|creates| LLMEval
    EvaluatorPreviews -->|triggers| CodeRunner
    CodeRunner -->|uses| SandboxCfg
    LLMEval -->|resolves| InputMap
    LLMEval -->|produces| Annotation
    LLMEval -->|constrained by| OutputConfig
    LLMEval -->|persisted as| DB_Eval
```

**Sources:** [src/phoenix/server/api/types/Evaluator.py:50-55](), [src/phoenix/server/api/mutations/evaluator_mutations.py:17-41](), [src/phoenix/db/models.py:1-100]()

---

## Evaluator Implementations

### LLMEvaluator
The `LLMEvaluator` executes evaluations by calling an LLM. It transforms a prompt template and input data into a structured LLM request.
- **Prompt Rendering**: Resolves the prompt version via `promptVersion` or `promptVersionTag` [src/phoenix/server/api/types/Evaluator.py:350-370]().
- **Validation**: Ensures that the prompt tools and response formats match the evaluator's `output_configs` via `validate_consistent_llm_evaluator_and_prompt_version` [src/phoenix/server/api/mutations/evaluator_mutations.py:37-41]().
- **Output Parsing**: Extracts structured data from LLM responses, typically via tool calls that map to `CategoricalOutputConfig` labels.

### CodeEvaluator
The `CodeEvaluator` [src/phoenix/server/api/types/Evaluator.py:51]() system allows for running arbitrary logic in a secure sandbox.
- **Language Support**: Supports `PYTHON` and `TYPESCRIPT` [src/phoenix/server/api/types/Evaluator.py:38]().
- **Inference**: Automatically infers the input schema from the function signature using `_infer_python_evaluate_input_schema` [src/phoenix/server/api/mutations/evaluator_mutations.py:32]() or `_infer_typescript_evaluate_input_schema` [src/phoenix/server/api/mutations/evaluator_mutations.py:33]().
- **Sandbox Validation**: Checks if the associated `SandboxConfig` is enabled and matches the evaluator's language before execution [src/phoenix/server/api/mutations/evaluator_mutations.py:125-157]().

### BuiltInEvaluator
The `BuiltInEvaluator` [src/phoenix/server/api/types/Evaluator.py:50]() provides "out-of-the-box" metrics. These are retrieved by key via `get_builtin_evaluator_by_key` [src/phoenix/server/api/mutations/evaluator_mutations.py:34]().

**Sources:** [src/phoenix/server/api/types/Evaluator.py:50-55](), [src/phoenix/server/api/mutations/evaluator_mutations.py:125-157](), [src/phoenix/server/api/mutations/evaluator_mutations.py:31-35]()

---

## Input Mapping and Context Resolution

Evaluation requires mapping raw data (from a Trace, Span, or Dataset Example) into the variables expected by an evaluator's prompt template or code function.

### Mapping Flow Diagram

```mermaid
sequenceDiagram
    participant UI as EvaluatorOutputPreview.tsx
    participant M as mutations/chat_mutations.py
    participant IM as InputMapping (JSONPath)
    participant E as Evaluator

    UI->>M: evaluatorPreviews(input)
    Note over UI: inputMapping: {literal_mapping, path_mapping}
    M->>IM: resolve_mapping(context, inputMapping)
    Note over IM: Extract values from context<br/>using JSONPath
    IM-->>M: mapped_variables
    M->>E: evaluate(mapped_variables)
    E-->>M: EvaluationResult
    M-->>UI: results { annotation, error }
```

The system uses `EvaluatorInputMapping` [src/phoenix/server/api/types/Evaluator.py:58]() to perform deep extraction. It contains:
- `literal_mapping`: Direct key-value pairs [src/phoenix/server/api/types/Evaluator.py:59]().
- `path_mapping`: JSONPath expressions to extract values from the evaluation context [src/phoenix/server/api/types/Evaluator.py:61]().

**Sources:** [src/phoenix/server/api/types/Evaluator.py:58-62](), [app/src/components/evaluators/EvaluatorOutputPreview.tsx:137-153]()

---

## Annotation Storage and Configuration

Evaluations result in **Annotations**, which are stored in the database and linked to spans, traces, or experiment runs.

### Output Configuration Types
The framework uses specific configurations to define the expected output of an evaluator:

| Config Class | Description | Fields |
|:---|:---|:---|
| `CategoricalOutputConfig` | Classification labels | `name`, `values` (label/score), `optimization_direction` [src/phoenix/db/types/annotation_configs.py:22]() |
| `ContinuousOutputConfig` | Numeric ranges | `name`, `lower_bound`, `upper_bound`, `optimization_direction` [src/phoenix/db/types/annotation_configs.py:23]() |
| `FreeformOutputConfig` | Unstructured text | `name`, `threshold`, `lower_bound`, `upper_bound` [src/phoenix/db/types/annotation_configs.py:24]() |

### Optimization Direction
Indicates the desired trend for the metric: `MAXIMIZE`, `MINIMIZE`, or `NONE` [src/phoenix/db/types/annotation_configs.py:16-19]().

**Sources:** [src/phoenix/db/types/annotation_configs.py:15-25](), [src/phoenix/server/api/mutations/evaluator_mutations.py:64-103]()

---

## UI Components and Previews

### Evaluator Table
The `EvaluatorsTable` [app/src/pages/evaluators/EvaluatorsTable.tsx:211]() displays all evaluators in the system, supporting sorting by `name`, `kind`, `createdAt`, and `updatedAt` [app/src/pages/evaluators/EvaluatorsTable.tsx:52-57](). It uses a nested row structure to show `DatasetEvaluator` assignments under their parent `Evaluator` [app/src/pages/evaluators/EvaluatorsTable.tsx:145-160]().

### Evaluator Output Preview
The `EvaluatorOutputPreview` [app/src/components/evaluators/EvaluatorOutputPreview.tsx:123]() component allows users to test an evaluator's logic in real-time.
- **Execution**: It triggers the `evaluatorPreviews` mutation [app/src/components/evaluators/EvaluatorOutputPreview.tsx:137]().
- **Payload Construction**: Uses `createLLMEvaluatorPayload` to bundle playground state, input mapping, and output configs [app/src/components/evaluators/EvaluatorOutputPreview.tsx:177-186]().
- **Positive Optimization**: The `computePositiveOptimization` helper determines if a result is "good" based on the `optimizationDirection` and score bounds [app/src/components/evaluators/EvaluatorOutputPreview.tsx:56-121]().

**Sources:** [app/src/pages/evaluators/EvaluatorsTable.tsx:52-57](), [app/src/components/evaluators/EvaluatorOutputPreview.tsx:56-121](), [app/src/components/evaluators/EvaluatorOutputPreview.tsx:137-153]()

---

# Page: Datasets & Experiments

# Datasets & Experiments

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/components/FocusHotkey.tsx](app/src/components/FocusHotkey.tsx)
- [app/src/components/ShareLinkButton.tsx](app/src/components/ShareLinkButton.tsx)
- [app/src/components/dataset/__generated__/DatasetLabelFilterButtonQuery.graphql.ts](app/src/components/dataset/__generated__/DatasetLabelFilterButtonQuery.graphql.ts)
- [app/src/components/table/styles.ts](app/src/components/table/styles.ts)
- [app/src/contexts/FeatureFlagsContext.tsx](app/src/contexts/FeatureFlagsContext.tsx)
- [app/src/pages/dataset/DatasetPage.tsx](app/src/pages/dataset/DatasetPage.tsx)
- [app/src/pages/dataset/datasetLoader.ts](app/src/pages/dataset/datasetLoader.ts)
- [app/src/pages/datasets/DatasetsPage.tsx](app/src/pages/datasets/DatasetsPage.tsx)
- [app/src/pages/datasets/DatasetsTable.tsx](app/src/pages/datasets/DatasetsTable.tsx)
- [app/src/pages/datasets/__generated__/DatasetsPageQuery.graphql.ts](app/src/pages/datasets/__generated__/DatasetsPageQuery.graphql.ts)
- [app/src/pages/datasets/__generated__/DatasetsTableDatasetsQuery.graphql.ts](app/src/pages/datasets/__generated__/DatasetsTableDatasetsQuery.graphql.ts)
- [app/src/pages/datasets/__generated__/DatasetsTable_datasets.graphql.ts](app/src/pages/datasets/__generated__/DatasetsTable_datasets.graphql.ts)
- [app/src/pages/experiment/ExampleDetailsPaginator.tsx](app/src/pages/experiment/ExampleDetailsPaginator.tsx)
- [app/src/pages/experiment/ExperimentCompareGridPage.tsx](app/src/pages/experiment/ExperimentCompareGridPage.tsx)
- [app/src/pages/experiment/ExperimentCompareMetricsPage.tsx](app/src/pages/experiment/ExperimentCompareMetricsPage.tsx)
- [app/src/pages/experiment/ExperimentComparePage.tsx](app/src/pages/experiment/ExperimentComparePage.tsx)
- [app/src/pages/experiment/ExperimentCompareTable.tsx](app/src/pages/experiment/ExperimentCompareTable.tsx)
- [app/src/pages/experiment/ExperimentMultiSelector.tsx](app/src/pages/experiment/ExperimentMultiSelector.tsx)
- [app/src/pages/experiment/__generated__/ExperimentCompareMetricsPage_experiments.graphql.ts](app/src/pages/experiment/__generated__/ExperimentCompareMetricsPage_experiments.graphql.ts)
- [app/src/pages/experiment/__generated__/ExperimentCompareTableQuery.graphql.ts](app/src/pages/experiment/__generated__/ExperimentCompareTableQuery.graphql.ts)
- [app/src/pages/experiment/__generated__/ExperimentCompareTable_comparisons.graphql.ts](app/src/pages/experiment/__generated__/ExperimentCompareTable_comparisons.graphql.ts)
- [app/src/pages/experiment/__generated__/ExperimentMultiSelector__data.graphql.ts](app/src/pages/experiment/__generated__/ExperimentMultiSelector__data.graphql.ts)
- [app/src/pages/home/homeLoader.ts](app/src/pages/home/homeLoader.ts)
- [app/src/pages/project/projectLoader.ts](app/src/pages/project/projectLoader.ts)
- [app/src/pages/trace/TraceDetailsPaginator.tsx](app/src/pages/trace/TraceDetailsPaginator.tsx)
- [src/phoenix/db/alembic.ini](src/phoenix/db/alembic.ini)
- [src/phoenix/db/engines.py](src/phoenix/db/engines.py)
- [src/phoenix/db/insertion/dataset.py](src/phoenix/db/insertion/dataset.py)
- [src/phoenix/db/migrate.py](src/phoenix/db/migrate.py)
- [src/phoenix/db/migrations/__init__.py](src/phoenix/db/migrations/__init__.py)
- [src/phoenix/db/migrations/env.py](src/phoenix/db/migrations/env.py)
- [src/phoenix/db/migrations/versions/10460e46d750_datasets.py](src/phoenix/db/migrations/versions/10460e46d750_datasets.py)
- [src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py](src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py)
- [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py](src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py)
- [src/phoenix/db/models.py](src/phoenix/db/models.py)
- [src/phoenix/server/api/input_types/DatasetFilter.py](src/phoenix/server/api/input_types/DatasetFilter.py)
- [src/phoenix/server/api/routers/v1/__init__.py](src/phoenix/server/api/routers/v1/__init__.py)
- [src/phoenix/server/api/routers/v1/datasets.py](src/phoenix/server/api/routers/v1/datasets.py)
- [src/phoenix/server/api/routers/v1/experiment_evaluations.py](src/phoenix/server/api/routers/v1/experiment_evaluations.py)
- [src/phoenix/server/api/routers/v1/experiment_runs.py](src/phoenix/server/api/routers/v1/experiment_runs.py)
- [src/phoenix/server/api/routers/v1/experiments.py](src/phoenix/server/api/routers/v1/experiments.py)
- [src/phoenix/settings.py](src/phoenix/settings.py)
- [tests/unit/db/insertion/test_dataset.py](tests/unit/db/insertion/test_dataset.py)
- [tests/unit/server/api/routers/v1/test_datasets.py](tests/unit/server/api/routers/v1/test_datasets.py)
- [tests/unit/server/api/routers/v1/test_experiments.py](tests/unit/server/api/routers/v1/test_experiments.py)

</details>



This page documents Phoenix's dataset and experiment management functionality, which enables users to create test datasets, run experiments against those datasets, and evaluate the results. These capabilities are essential for benchmarking, comparing, and improving LLM application performance through structured testing.

For information about LLM evaluations outside the context of experiments, see [5.2. Evaluation Framework]().

## Overview

Phoenix datasets and experiments provide a structured approach to testing LLM applications:

1.  **Datasets** are collections of examples, each containing input data, reference output, and optional metadata.
2.  **Dataset versions** capture the evolution of datasets over time.
3.  **Experiments** run LLM applications against dataset examples and collect results.
4.  **Experiment runs** are individual executions of an LLM application on a specific dataset example.
5.  **Experiment evaluations** analyze the quality of experiment run outputs.

### Natural Language to Code Entity Mapping

The following diagram maps high-level concepts to their specific implementations in the Phoenix codebase.

```mermaid
flowchart TD
    subgraph "Natural Language Concepts"
        DS_Concept["Dataset"]
        EX_Concept["Experiment"]
        RUN_Concept["Experiment Run"]
        EVAL_Concept["Evaluation Result"]
    end

    subgraph "Code Entity Space (src/phoenix/db/models.py)"
        Dataset["class Dataset"]
        DatasetVersion["class DatasetVersion"]
        DatasetExample["class DatasetExample"]
        Experiment["class Experiment"]
        ExperimentRun["class ExperimentRun"]
        ExperimentRunAnnotation["class ExperimentRunAnnotation"]
    end

    DS_Concept -.-> Dataset
    DS_Concept -.-> DatasetVersion
    DS_Concept -.-> DatasetExample
    EX_Concept -.-> Experiment
    RUN_Concept -.-> ExperimentRun
    EVAL_Concept -.-> ExperimentRunAnnotation

    Dataset -- "has versions" --> DatasetVersion
    Dataset -- "contains" --> DatasetExample
    DatasetVersion -- "used in" --> Experiment
    Experiment -- "produces" --> ExperimentRun
    ExperimentRun -- "evaluated by" --> ExperimentRunAnnotation
```

Sources: [src/phoenix/db/models.py:804-1017](), [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:48-307]()

## Database Schema

The dataset and experiment system is organized around the following database tables defined in `src/phoenix/db/models.py`.

```mermaid
erDiagram
    Dataset ||--o{ DatasetVersion : "has"
    Dataset ||--o{ DatasetExample : "contains"
    DatasetExample ||--o{ DatasetExampleRevision : "has"

    Experiment }o--|| Dataset : "uses"
    Experiment }o--|| DatasetVersion : "uses"
    Experiment ||--o{ ExperimentRun : "contains"

    ExperimentRun }o--|| DatasetExample : "uses"
    ExperimentRun ||--o{ ExperimentRunAnnotation : "evaluated_by"

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
        int span_rowid FK_nullable
        datetime created_at
    }

    DatasetExampleRevision {
        int id PK
        int dataset_example_id FK
        int dataset_version_id FK
        json input
        json output
        json metadata_
        string revision_kind
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
        string project_name
        datetime created_at
        datetime updated_at
    }

    ExperimentRun {
        int id PK
        int experiment_id FK
        int dataset_example_id FK
        int repetition_number
        string trace_id
        json output
        datetime start_time
        datetime end_time
        int prompt_token_count
        int completion_token_count
        string error
    }

    ExperimentRunAnnotation {
        int id PK
        int experiment_run_id FK
        string name
        string annotator_kind
        string label
        float score
        string explanation
        string trace_id
        string error
        json metadata_
        datetime start_time
        datetime end_time
    }
```

Sources: [src/phoenix/db/models.py:804-1017](), [src/phoenix/db/migrations/versions/10460e46d750_datasets.py:48-307]()

## Datasets

Datasets are collections of examples used for testing and evaluating LLM applications. Each dataset has a name, optional description, and metadata. Datasets can be created from various sources including DataFrames, CSV files, or direct JSON input.

### Dataset Structure

-   **Dataset**: Contains metadata about the dataset (name, description, etc.) [src/phoenix/db/models.py:804-826]()
-   **DatasetVersion**: Represents a snapshot of the dataset at a specific point in time. [src/phoenix/db/models.py:829-847]()
-   **DatasetExample**: Individual examples within the dataset. [src/phoenix/db/models.py:850-867]()
-   **DatasetExampleRevision**: The actual content of examples (input, output, metadata) in a specific version. [src/phoenix/db/models.py:870-905]()

### REST API Interface

The `v1` datasets router provides endpoints for listing, creating, and deleting datasets.
- `GET /v1/datasets`: Lists datasets with pagination. It joins `DatasetExample` and `DatasetExampleRevision` to calculate the current `example_count`. [src/phoenix/server/api/routers/v1/datasets.py:100-164]()
- `DELETE /v1/datasets/{id}`: Deletes a dataset by its GlobalID. This operation also cleans up associated projects and traces via `get_project_names_for_datasets` and `get_eval_trace_ids_for_datasets`. [src/phoenix/server/api/routers/v1/datasets.py:179-202]()

Sources: [src/phoenix/server/api/routers/v1/datasets.py:77-202]()

### Frontend Dataset Management

The Phoenix UI provides a dedicated page for managing datasets. The `DatasetPage` component orchestrates the display and interaction with datasets.

```mermaid
graph TD
    DatasetPage["DatasetPage.tsx"] --> DatasetProvider["DatasetContext.tsx"]
    DatasetPage --> DatasetPageContent["DatasetPageContent"]
    DatasetPageContent --> ExperimentsTable["ExperimentsTable.tsx"]
    DatasetPageContent --> DatasetsTable["DatasetsTable.tsx"]
    DatasetsTable -- "Displays" --> DatasetNode["Dataset (GraphQL)"]
    DatasetNode -- "Actions" --> DatasetActionMenu["DatasetActionMenu.tsx"]
```

The `DatasetsTable` component uses `usePaginationFragment` to fetch and display dataset lists with support for sorting by `createdAt` or `name`. [app/src/pages/datasets/DatasetsTable.tsx:87-124]()

Sources: [app/src/pages/dataset/DatasetPage.tsx:61-247](), [app/src/pages/datasets/DatasetsTable.tsx:78-124]()

## Experiments

Experiments represent the execution of LLM applications against datasets to evaluate performance. Each experiment is associated with a specific dataset and dataset version.

### Creating Experiments

Experiments can be created using the REST API:
`POST /v1/datasets/{dataset_id}/experiments` [src/phoenix/server/api/routers/v1/experiments.py:121-125]()

The `CreateExperimentRequestBody` allows specifying:
- `name`: Optional experiment name. If omitted, `_generate_experiment_name` creates a random name. [src/phoenix/server/api/routers/v1/experiments.py:81-84](), [src/phoenix/server/api/routers/v1/experiments.py:47-52]()
- `version_id`: Specific dataset version. If omitted, the latest version is used. [src/phoenix/server/api/routers/v1/experiments.py:91-97](), [src/phoenix/server/api/routers/v1/experiments.py:170-182]()
- `repetitions`: Number of times to repeat each example. [src/phoenix/server/api/routers/v1/experiments.py:102-104]()

Sources: [src/phoenix/server/api/routers/v1/experiments.py:47-125]()

### Experiment Runs and Evaluations

Individual executions and their results are managed through:
- `POST /v1/experiment_runs`: Records the output of a specific example execution. [src/phoenix/server/api/routers/v1/experiment_runs.py:51-108]()
- `POST /v1/experiment_evaluations`: Creates or updates an evaluation (`ExperimentRunAnnotation`) for a run. [src/phoenix/server/api/routers/v1/experiment_evaluations.py:77-127]()

The `upsert_experiment_evaluation` function handles the insertion logic, supporting `LLM`, `CODE`, and `HUMAN` annotator kinds. It uses `insert_on_conflict` to ensure uniqueness by `experiment_run_id` and `name`. [src/phoenix/server/api/routers/v1/experiment_evaluations.py:89-123]()

Sources: [src/phoenix/server/api/routers/v1/experiment_runs.py:51-108](), [src/phoenix/server/api/routers/v1/experiment_evaluations.py:77-127]()

### UI Comparison Grid

The `ExperimentCompareTable` component provides a specialized grid view for comparing multiple experiments side-by-side.

| Feature | Implementation |
| :--- | :--- |
| **Data Fetching** | Uses `usePaginationFragment` with `compareExperiments` GraphQL connection. [app/src/pages/experiment/ExperimentCompareTable.tsx:140-163]() |
| **Virtualization** | Implements `useVirtualizer` from `@tanstack/react-virtual` for high-performance rendering of large datasets. [app/src/pages/experiment/ExperimentCompareTable.tsx:8-17]() |
| **Metrics** | Displays `meanScore` from `annotationSummaries` and `costSummary`. [app/src/pages/experiment/ExperimentCompareTable.tsx:175-195]() |

Sources: [app/src/pages/experiment/ExperimentCompareTable.tsx:123-163]()

## System Architecture

The dataset and experiment system is integrated with the larger Phoenix architecture through the REST API layer and the SQLAlchemy ORM.

### Data Flow for Experiments

The following diagram bridges the REST API layer to the database models.

```mermaid
sequenceDiagram
    participant Client as "REST Client"
    participant API as "FastAPI (v1/experiments.py)"
    participant DB as "SQLAlchemy (models.py)"
    participant Events as "Internal Event Queue"

    Client->>API: POST /v1/datasets/{id}/experiments
    API->>DB: insert_experiment_with_examples_snapshot()
    DB-->>API: models.Experiment Instance
    API->>Events: ExperimentInsertEvent
    API-->>Client: CreateExperimentResponseBody

    Client->>API: POST /v1/experiment_evaluations
    API->>DB: insert_on_conflict(models.ExperimentRunAnnotation)
    DB-->>API: models.ExperimentRunAnnotation Instance
    API->>Events: ExperimentRunAnnotationInsertEvent
    API-->>Client: UpsertExperimentEvaluationResponseBody
```

Sources: [src/phoenix/server/api/routers/v1/experiments.py:197-209](), [src/phoenix/server/api/routers/v1/experiment_evaluations.py:113-124]()

## Database Migrations

The datasets and experiments system is managed via Alembic migrations.

- `cf03bd6bae1d_init.py`: Initial schema for projects, traces, and spans. [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:48-280]()
- `10460e46d750_datasets.py`: Introduces the core dataset and experiment tables.
- `3be8647b87d8_add_token_columns_to_spans_table.py`: Adds token tracking columns (`cumulative_llm_token_count_prompt`, etc.) used for experiment cost calculation. [src/phoenix/db/migrations/versions/3be8647b87d8_add_token_columns_to_spans_table.py:20-35]()

Migrations are executed via `src/phoenix/db/migrate.py`, which uses `alembic.command.upgrade` to bring the database to the `head` revision. [src/phoenix/db/migrate.py:78-80]()

Sources: [src/phoenix/db/migrate.py:37-80](), [src/phoenix/db/migrations/versions/cf03bd6bae1d_init.py:48-280]()

## Integration with Spans and Traces

Datasets and experiments link directly to the observability system:
- `DatasetExample` includes a `span_rowid` to link back to the originating trace span. [src/phoenix/db/models.py:856-861]()
- `ExperimentRun` stores a `trace_id`, allowing users to jump from an experiment result to the full execution trace in the UI. [src/phoenix/db/models.py:951-971]()

Sources: [src/phoenix/db/models.py:850-867](), [src/phoenix/db/models.py:951-971]()

---

# Page: Prompt Management

# Prompt Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/pages/playground/PromptComboBox.tsx](app/src/pages/playground/PromptComboBox.tsx)
- [app/src/pages/playground/SavePromptForm.tsx](app/src/pages/playground/SavePromptForm.tsx)
- [app/src/pages/playground/UpsertPromptFromTemplateDialog.tsx](app/src/pages/playground/UpsertPromptFromTemplateDialog.tsx)
- [app/src/pages/playground/__generated__/PromptComboBoxQuery.graphql.ts](app/src/pages/playground/__generated__/PromptComboBoxQuery.graphql.ts)
- [app/src/pages/playground/__generated__/SavePromptFormQuery.graphql.ts](app/src/pages/playground/__generated__/SavePromptFormQuery.graphql.ts)
- [app/src/pages/playground/__generated__/UpsertPromptFromTemplateDialogCreateMutation.graphql.ts](app/src/pages/playground/__generated__/UpsertPromptFromTemplateDialogCreateMutation.graphql.ts)
- [app/src/pages/playground/__generated__/UpsertPromptFromTemplateDialogUpdateMutation.graphql.ts](app/src/pages/playground/__generated__/UpsertPromptFromTemplateDialogUpdateMutation.graphql.ts)
- [app/src/pages/playground/__generated__/fetchPlaygroundPromptQuery.graphql.ts](app/src/pages/playground/__generated__/fetchPlaygroundPromptQuery.graphql.ts)
- [app/src/pages/playground/fetchPlaygroundPrompt.ts](app/src/pages/playground/fetchPlaygroundPrompt.ts)
- [app/src/pages/prompt/EditPromptButton.tsx](app/src/pages/prompt/EditPromptButton.tsx)
- [app/src/pages/prompt/PromptCodeExportCard.tsx](app/src/pages/prompt/PromptCodeExportCard.tsx)
- [app/src/pages/prompt/PromptIndexPage.tsx](app/src/pages/prompt/PromptIndexPage.tsx)
- [app/src/pages/prompt/PromptInvocationParameters.tsx](app/src/pages/prompt/PromptInvocationParameters.tsx)
- [app/src/pages/prompt/PromptLatestVersionsList.tsx](app/src/pages/prompt/PromptLatestVersionsList.tsx)
- [app/src/pages/prompt/PromptLayout.tsx](app/src/pages/prompt/PromptLayout.tsx)
- [app/src/pages/prompt/PromptVersionDetailsPage.tsx](app/src/pages/prompt/PromptVersionDetailsPage.tsx)
- [app/src/pages/prompt/PromptVersionsList.tsx](app/src/pages/prompt/PromptVersionsList.tsx)
- [app/src/pages/prompt/__generated__/EditPromptButtonPatchPromptMutation.graphql.ts](app/src/pages/prompt/__generated__/EditPromptButtonPatchPromptMutation.graphql.ts)
- [app/src/pages/prompt/__generated__/EditPromptButton_data.graphql.ts](app/src/pages/prompt/__generated__/EditPromptButton_data.graphql.ts)
- [app/src/pages/prompt/__generated__/PromptCodeExportCard__main.graphql.ts](app/src/pages/prompt/__generated__/PromptCodeExportCard__main.graphql.ts)
- [app/src/pages/prompt/__generated__/PromptIndexPage__aside.graphql.ts](app/src/pages/prompt/__generated__/PromptIndexPage__aside.graphql.ts)
- [app/src/pages/prompt/__generated__/PromptIndexPage__main.graphql.ts](app/src/pages/prompt/__generated__/PromptIndexPage__main.graphql.ts)
- [app/src/pages/prompt/__generated__/PromptLatestVersionsListFragment.graphql.ts](app/src/pages/prompt/__generated__/PromptLatestVersionsListFragment.graphql.ts)
- [app/src/pages/prompt/__generated__/PromptVersionsList__main.graphql.ts](app/src/pages/prompt/__generated__/PromptVersionsList__main.graphql.ts)
- [app/src/pages/prompt/__generated__/promptLoaderQuery.graphql.ts](app/src/pages/prompt/__generated__/promptLoaderQuery.graphql.ts)
- [app/src/pages/prompt/__generated__/promptVersionLoaderQuery.graphql.ts](app/src/pages/prompt/__generated__/promptVersionLoaderQuery.graphql.ts)
- [app/src/pages/prompt/__tests__/fixtures.ts](app/src/pages/prompt/__tests__/fixtures.ts)
- [app/src/pages/prompt/__tests__/promptCodeSnippets.anthropic.test.ts](app/src/pages/prompt/__tests__/promptCodeSnippets.anthropic.test.ts)
- [app/src/pages/prompt/__tests__/promptCodeSnippets.openai.test.ts](app/src/pages/prompt/__tests__/promptCodeSnippets.openai.test.ts)
- [app/src/pages/prompt/promptCodeSnippets.tsx](app/src/pages/prompt/promptCodeSnippets.tsx)
- [app/src/pages/prompt/promptVersionLoader.tsx](app/src/pages/prompt/promptVersionLoader.tsx)
- [app/src/pages/prompts/PromptsFilterProvider.tsx](app/src/pages/prompts/PromptsFilterProvider.tsx)
- [app/src/pages/prompts/PromptsPage.tsx](app/src/pages/prompts/PromptsPage.tsx)
- [app/src/pages/prompts/PromptsTable.tsx](app/src/pages/prompts/PromptsTable.tsx)
- [app/src/pages/prompts/__generated__/DeletePromptDialogMutation.graphql.ts](app/src/pages/prompts/__generated__/DeletePromptDialogMutation.graphql.ts)
- [app/src/pages/prompts/__generated__/PromptsTablePromptsQuery.graphql.ts](app/src/pages/prompts/__generated__/PromptsTablePromptsQuery.graphql.ts)
- [app/src/pages/prompts/__generated__/PromptsTable_prompts.graphql.ts](app/src/pages/prompts/__generated__/PromptsTable_prompts.graphql.ts)
- [app/src/pages/prompts/__generated__/promptsLoaderQuery.graphql.ts](app/src/pages/prompts/__generated__/promptsLoaderQuery.graphql.ts)
- [app/src/pages/prompts/promptsLoader.ts](app/src/pages/prompts/promptsLoader.ts)
- [app/src/schemas/messageSchemas.ts](app/src/schemas/messageSchemas.ts)
- [app/src/schemas/toolCallSchemas.ts](app/src/schemas/toolCallSchemas.ts)
- [src/phoenix/db/migrations/versions/bc8fea3c2bc8_add_prompt_tables.py](src/phoenix/db/migrations/versions/bc8fea3c2bc8_add_prompt_tables.py)
- [src/phoenix/server/api/input_types/PromptVersionInput.py](src/phoenix/server/api/input_types/PromptVersionInput.py)
- [src/phoenix/server/api/mutations/prompt_label_mutations.py](src/phoenix/server/api/mutations/prompt_label_mutations.py)
- [src/phoenix/server/api/mutations/prompt_mutations.py](src/phoenix/server/api/mutations/prompt_mutations.py)
- [src/phoenix/server/api/mutations/prompt_version_tag_mutations.py](src/phoenix/server/api/mutations/prompt_version_tag_mutations.py)
- [src/phoenix/server/api/routers/v1/prompts.py](src/phoenix/server/api/routers/v1/prompts.py)
- [src/phoenix/server/api/types/Prompt.py](src/phoenix/server/api/types/Prompt.py)
- [src/phoenix/server/api/types/PromptVersion.py](src/phoenix/server/api/types/PromptVersion.py)
- [src/phoenix/server/api/types/PromptVersionTemplate.py](src/phoenix/server/api/types/PromptVersionTemplate.py)
- [tests/integration/db_migrations/test_autoincrement_primary_keys.py](tests/integration/db_migrations/test_autoincrement_primary_keys.py)
- [tests/unit/server/api/mutations/test_prompt_mutations.py](tests/unit/server/api/mutations/test_prompt_mutations.py)
- [tests/unit/server/api/routers/v1/test_prompts.py](tests/unit/server/api/routers/v1/test_prompts.py)

</details>



Phoenix's Prompt Management system enables users to create, version, and test prompts for LLM applications. This page documents the system architecture, data models, and integration patterns used to implement prompt versioning and management in Phoenix.

## Purpose and Components

The Prompt Management system allows you to:

1. Create and maintain reusable prompt templates.
2. Apply version control to prompts with tagging capabilities.
3. Categorize prompts with labels.
4. Standardize prompts across different LLM providers.
5. Integrate prompts with client applications via SDKs.

```mermaid
graph TD
    subgraph "Prompt Management System"
        PromptStore["Prompt Repository"]
        VersionControl["Version Control"]
        Labeling["Prompt Labeling"]
        ClientSDKs["Client SDKs"]
    end
    
    subgraph "Integration Points"
        LLMProviders["LLM Provider APIs"]
        Playground["Phoenix Playground"]
        Experiments["Experiments"]
        Tracing["Trace Visualization"]
    end
    
    PromptStore --> VersionControl
    PromptStore --> Labeling
    PromptStore --> ClientSDKs
    
    ClientSDKs --> LLMProviders
    PromptStore --> Playground
    PromptStore --> Experiments
    Playground --> Tracing
```

Sources: [src/phoenix/server/api/routers/v1/prompts.py:117-118](), [app/src/pages/playground/fetchPlaygroundPrompt.ts:55-65]()

## Data Model

The Prompt Management system is built on a relational database model with several core entities that enable versioning, labeling, and tagging of prompts.

```mermaid
erDiagram
    Prompt ||--o{ PromptVersion : "has"
    Prompt ||--o{ PromptPromptLabel : "tagged_with"
    PromptLabel ||--o{ PromptPromptLabel : "used_in"
    PromptVersion ||--o{ PromptVersionTag : "tagged_with"
    User ||--o{ PromptVersion : "creates"
    User ||--o{ PromptVersionTag : "creates"
    
    Prompt {
        int id PK
        int source_prompt_id FK
        string name
        string description
        json metadata
        datetime created_at
    }
    
    PromptVersion {
        int id PK
        int prompt_id FK
        string description
        int user_id FK
        enum template_type
        enum template_format
        json template
        json invocation_parameters
        json tools
        json response_format
        string model_provider
        string model_name
        json metadata
        datetime created_at
    }
    
    PromptVersionTag {
        int id PK
        string name
        string description
        int prompt_id FK
        int prompt_version_id FK
        int user_id FK
    }
```

Sources: [src/phoenix/db/migrations/versions/bc8fea3c2bc8_add_prompt_tables.py:48-189](), [src/phoenix/server/api/types/Prompt.py:32-34](), [src/phoenix/server/api/types/PromptVersion.py:38-53]()

### Core Entities

#### Prompt

The `Prompt` entity is the main container for a prompt with a unique name. It can have multiple versions and be categorized with multiple labels.

Key attributes:
- `id`: Primary key (GlobalID in API) [src/phoenix/server/api/types/Prompt.py:33]().
- `source_prompt_id`: Self-referential ID for cloned prompts [src/phoenix/server/api/types/Prompt.py:41-53]().
- `name`: Unique identifier [src/phoenix/server/api/types/Prompt.py:56-66]().
- `description`: Optional description [src/phoenix/server/api/types/Prompt.py:69-79]().
- `metadata`: JSON metadata [src/phoenix/server/api/types/Prompt.py:82-92]().

Sources: [src/phoenix/server/api/types/Prompt.py:32-106]()

#### PromptVersion

Each `PromptVersion` represents a specific version of a prompt, containing the actual template and configuration.

Key attributes:
- `prompt_id`: Foreign key to parent Prompt [src/phoenix/server/api/types/PromptVersion.py:40]().
- `template_type`: Enum (`CHAT`, `STRING`) [src/phoenix/db/types/prompts.py:23]().
- `template_format`: Enum (`F_STRING`, `MUSTACHE`, `NONE`) [src/phoenix/db/types/prompts.py:22]().
- `template`: The actual template structure (e.g., `PromptChatTemplate` or `PromptStringTemplate`) [src/phoenix/server/api/types/PromptVersion.py:46]().
- `invocation_parameters`: Model settings like temperature and penalties [src/phoenix/server/api/types/PromptVersion.py:47]().
- `model_provider`: LLM provider (OpenAI, Anthropic, etc.) [src/phoenix/server/api/types/PromptVersion.py:51]().

Sources: [src/phoenix/server/api/types/PromptVersion.py:38-53](), [src/phoenix/db/types/prompts.py:21-23]()

#### PromptVersionTag

Tags allow referencing specific versions by name (e.g., "latest", "prod").

Key attributes:
- `name`: Tag name [src/phoenix/server/api/routers/v1/prompts.py:314]().
- `prompt_version_id`: Target version [src/phoenix/server/api/routers/v1/prompts.py:315]().

Sources: [src/phoenix/server/api/routers/v1/prompts.py:309-322]()

## Template Types and Formats

Phoenix supports different prompt template types and formats:

### Template Types

The `template_type` field defines the structure of the prompt:

1.  **CHAT**: A list of messages with roles (system, user, assistant, tool) [src/phoenix/db/types/prompts.py:23]().
2.  **STRING**: A single raw string template [src/phoenix/db/types/prompts.py:23]().

Sources: [src/phoenix/db/types/prompts.py:23](), [src/phoenix/server/api/routers/v1/prompts.py:73-82]()

### Template Formats

The `template_format` field defines how variables are interpolated:

1.  **F_STRING**: Python-style `{variable}` syntax [src/phoenix/db/types/prompts.py:22]().
2.  **MUSTACHE**: `{{variable}}` syntax [src/phoenix/db/types/prompts.py:22]().
3.  **NONE**: No interpolation [src/phoenix/db/types/prompts.py:22]().

Sources: [src/phoenix/db/types/prompts.py:22]()

## Version Control Workflow

The system allows tracking evolution via sequence numbers and explicit tagging.

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserIntent["'Improve RAG Accuracy'"]
        TagIntent["'Mark as Production'"]
    end

    subgraph "Code Entity Space"
        Mutation["Mutation: create_chat_prompt_version"]
        TagMutation["Mutation: upsert_prompt_version_tag"]
        PromptModel["models.Prompt"]
        VersionModel["models.PromptVersion"]
        TagModel["models.PromptVersionTag"]
    end

    UserIntent --> Mutation
    Mutation --> VersionModel
    VersionModel --> PromptModel
    TagIntent --> TagMutation
    TagMutation --> TagModel
    TagModel --> VersionModel
```

Sources: [src/phoenix/server/api/mutations/prompt_mutations.py:110-156](), [src/phoenix/server/api/mutations/prompt_version_tag_mutations.py:24-27]()

### Key Operations

1.  **Create Prompt**: Establishing a new container with an initial version [src/phoenix/server/api/mutations/prompt_mutations.py:78-107]().
2.  **Versioning**: Adding a new version to an existing prompt [src/phoenix/server/api/mutations/prompt_mutations.py:110-156]().
3.  **Tagging**: Mapping a string tag to a specific version ID [src/phoenix/server/api/mutations/prompt_version_tag_mutations.py:24-27]().
4.  **Cloning**: Creating a new prompt based on an existing one [src/phoenix/server/api/mutations/prompt_mutations.py:175-212]().

## Integration with LLM Providers

Standardization occurs by mapping internal `PromptVersion` structures to provider-specific formats.

| Provider | Internal Class | Description |
| :--- | :--- | :--- |
| OpenAI | `PromptOpenAIInvocationParameters` | Standard OpenAI params (temperature, top_p, etc.) [src/phoenix/db/types/prompts.py:29]() |
| DeepSeek | `PromptDeepSeekInvocationParameters` | DeepSeek specific parameters, normalized to OpenAI family [src/phoenix/server/api/routers/v1/prompts.py:67-70]() |

Sources: [src/phoenix/db/types/prompts.py:26-30](), [src/phoenix/server/api/routers/v1/prompts.py:65-70]()

## Playground Integration

The Playground is the primary UI for testing prompt versions. The `promptVersionToInstance` function converts a stored version into an interactive playground state.

```mermaid
graph LR
    subgraph "Storage (SQLAlchemy)"
        DB_PV["models.PromptVersion"]
    end

    subgraph "API (GraphQL)"
        GQL_PV["PromptVersion (Strawberry Type)"]
    end

    subgraph "Frontend (React/Relay)"
        UI_PV["fetchPlaygroundPrompt_promptVersion"]
        Conv["promptVersionToInstance"]
        PG_Instance["PlaygroundInstance"]
    end

    DB_PV --> GQL_PV
    GQL_PV --> UI_PV
    UI_PV --> Conv
    Conv --> PG_Instance
```

Sources: [app/src/pages/playground/fetchPlaygroundPrompt.ts:55-184](), [src/phoenix/server/api/types/PromptVersion.py:129-161]()

## API Access

### REST API (v1)
The REST API provides endpoints for programmatic access to prompts and versions:
- `GET /v1/prompts`: List all prompts [src/phoenix/server/api/routers/v1/prompts.py:126-183]().
- `GET /v1/prompts/{prompt_identifier}/latest`: Get the latest version [src/phoenix/server/api/routers/v1/prompts.py:241-285]().
- `GET /v1/prompts/{prompt_identifier}/tags/{tag_name}`: Get version by tag [src/phoenix/server/api/routers/v1/prompts.py:339-386]().

### GraphQL API
The GraphQL API supports complex relationships and pagination:
- `promptVersions`: Paginated connection for a prompt [src/phoenix/server/api/types/Prompt.py:158-183]().
- `sequenceNumber`: 1-based index of the version [src/phoenix/server/api/types/PromptVersion.py:106-117]().
- `isLatest`: Boolean check for the newest version [src/phoenix/server/api/types/PromptVersion.py:120-126]().

Sources: [src/phoenix/server/api/routers/v1/prompts.py:110-120](), [src/phoenix/server/api/types/Prompt.py:31-33](), [src/phoenix/server/api/types/PromptVersion.py:37-39]()

---

# Page: Playground System

# Playground System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/components/templateEditor/constants.ts](app/src/components/templateEditor/constants.ts)
- [app/src/components/templateEditor/templateEditorUtils.ts](app/src/components/templateEditor/templateEditorUtils.ts)
- [app/src/pages/playground/Playground.tsx](app/src/pages/playground/Playground.tsx)
- [app/src/pages/playground/PlaygroundChatTemplate.tsx](app/src/pages/playground/PlaygroundChatTemplate.tsx)
- [app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx](app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx)
- [app/src/pages/playground/PlaygroundInput.tsx](app/src/pages/playground/PlaygroundInput.tsx)
- [app/src/pages/playground/PlaygroundOutput.tsx](app/src/pages/playground/PlaygroundOutput.tsx)
- [app/src/pages/playground/PlaygroundTemplate.tsx](app/src/pages/playground/PlaygroundTemplate.tsx)
- [app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableMutation.graphql.ts](app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableMutation.graphql.ts)
- [app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableSubscription.graphql.ts](app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableSubscription.graphql.ts)
- [app/src/pages/playground/__generated__/PlaygroundOutputSubscription.graphql.ts](app/src/pages/playground/__generated__/PlaygroundOutputSubscription.graphql.ts)
- [app/src/pages/playground/__tests__/playgroundUtils.test.ts](app/src/pages/playground/__tests__/playgroundUtils.test.ts)
- [app/src/pages/playground/constants.tsx](app/src/pages/playground/constants.tsx)
- [app/src/pages/playground/playgroundUtils.ts](app/src/pages/playground/playgroundUtils.ts)
- [app/src/pages/playground/schemas.ts](app/src/pages/playground/schemas.ts)
- [app/src/store/playground/__tests__/playgroundStore.test.ts](app/src/store/playground/__tests__/playgroundStore.test.ts)
- [app/src/store/playground/playgroundStore.tsx](app/src/store/playground/playgroundStore.tsx)
- [app/src/store/playground/types.ts](app/src/store/playground/types.ts)
- [src/phoenix/server/api/evaluators.py](src/phoenix/server/api/evaluators.py)
- [src/phoenix/server/api/helpers/dataset_helpers.py](src/phoenix/server/api/helpers/dataset_helpers.py)
- [src/phoenix/server/api/helpers/experiment_run_filters.py](src/phoenix/server/api/helpers/experiment_run_filters.py)
- [src/phoenix/server/api/helpers/playground_clients.py](src/phoenix/server/api/helpers/playground_clients.py)
- [src/phoenix/server/api/mutations/chat_mutations.py](src/phoenix/server/api/mutations/chat_mutations.py)
- [src/phoenix/server/api/subscriptions.py](src/phoenix/server/api/subscriptions.py)
- [src/phoenix/utilities/template_formatters.py](src/phoenix/utilities/template_formatters.py)
- [tests/integration/_mock_ldap_server.py](tests/integration/_mock_ldap_server.py)
- [tests/integration/_mock_llm_server.py](tests/integration/_mock_llm_server.py)
- [tests/integration/experiments/conftest.py](tests/integration/experiments/conftest.py)
- [tests/integration/experiments/test_playground.py](tests/integration/experiments/test_playground.py)
- [tests/unit/server/api/helpers/test_dataset_helpers.py](tests/unit/server/api/helpers/test_dataset_helpers.py)
- [tests/unit/server/api/helpers/test_evaluators.py](tests/unit/server/api/helpers/test_evaluators.py)
- [tests/unit/server/api/helpers/test_playground_clients.py](tests/unit/server/api/helpers/test_playground_clients.py)
- [tests/unit/server/api/test_subscriptions.py](tests/unit/server/api/test_subscriptions.py)
- [tests/unit/utilities/test_template_formatters.py](tests/unit/utilities/test_template_formatters.py)

</details>



The Playground System provides an interactive interface for testing and experimenting with LLM prompts across multiple providers. It enables users to compose multi-turn conversations, configure model parameters, run prompts against individual inputs or entire datasets, and evaluate results—all while automatically capturing execution as OpenTelemetry traces. This system bridges frontend UI components with backend LLM client abstractions through GraphQL subscriptions for real-time streaming.

**Related Systems**: For prompt version management, see [Prompt Management](5.4). For dataset and experiment execution without the interactive UI, see [Datasets & Experiments](5.3). For evaluation configuration, see [Evaluation Framework](5.2).

---

## System Architecture

The Playground operates across three main layers: frontend state management, GraphQL API (subscriptions/mutations), and LLM client abstractions. The frontend maintains instance state for multiple concurrent prompt comparisons, while the backend handles provider-specific API calls through a unified streaming client interface.

### High-Level Data Flow

```mermaid
graph TB
    subgraph "Frontend - React UI"
        PlaygroundUI["Playground.tsx<br/>Main UI Component"]
        Store["playgroundStore.tsx<br/>Zustand State"]
        Output["PlaygroundOutput.tsx<br/>Subscription Handler"]
    end
    
    subgraph "GraphQL Layer"
        Subscription["subscriptions.py<br/>chatCompletion"]
        Mutation["chat_mutations.py<br/>evaluator_previews"]
    end
    
    subgraph "LLM Client Abstraction"
        Registry["playground_registry.py<br/>@register_llm_client"]
        BaseClient["PlaygroundStreamingClient<br/>ABC"]
        OpenAIClient["OpenAIBaseStreamingClient"]
        AnthropicClient["AnthropicStreamingClient"]
        OtherClients["Google, AWS, etc."]
    end
    
    subgraph "External Services"
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        OtherAPIs["Other LLM APIs"]
    end
    
    subgraph "Data Storage"
        DB["PostgreSQL/SQLite"]
        Projects["models.Project<br/>PLAYGROUND_PROJECT_NAME"]
        Traces["models.Trace"]
        Spans["models.Span"]
    end
    
    PlaygroundUI --> Store
    Store --> Output
    Output -->|GraphQL Subscribe| Subscription
    PlaygroundUI -->|GraphQL Mutate| Mutation
    
    Subscription --> BaseClient
    Mutation --> BaseClient
    
    Registry -.registers.-> OpenAIClient
    Registry -.registers.-> AnthropicClient
    Registry -.registers.-> OtherClients
    
    BaseClient --> OpenAIClient
    BaseClient --> AnthropicClient
    BaseClient --> OtherClients
    
    OpenAIClient --> OpenAI
    AnthropicClient --> Anthropic
    OtherClients --> OtherAPIs
    
    BaseClient -->|Records Traces| Traces
    Traces --> Spans
    Traces --> Projects
    Traces --> DB
    Spans --> DB
```

**Sources**: 
- [app/src/pages/playground/Playground.tsx:136-210]()
- [app/src/pages/playground/PlaygroundOutput.tsx:149-462]()
- [src/phoenix/server/api/subscriptions.py:76-135]()
- [src/phoenix/server/api/helpers/playground_clients.py:161-285]()
- [src/phoenix/server/api/mutations/chat_mutations.py:180-264]()

---

## LLM Client Abstraction Layer

The backend implements a plugin architecture for LLM providers through the `PlaygroundStreamingClient` abstract base class. Each provider implementation handles API-specific details while exposing a uniform streaming interface via `chat_completion_create`.

### Client Class Hierarchy

```mermaid
classDiagram
    class PlaygroundStreamingClient {
        <<abstract>>
        +provider: str
        +model_name: str
        +llm_system: str
        +dependencies() list~Dependency~
        +chat_completion_create() AsyncIterator~ChatCompletionChunk~
    }
    
    class OpenAIBaseStreamingClient {
        +llm_system = "openai"
        #_chat_completion_create()
        #_responses_create()
    }
    
    class AnthropicStreamingClient {
        +llm_system = "anthropic"
        #_chat_completion_create()
    }
    
    class AWSBedrockStreamingClient {
        +llm_system = "bedrock"
        #_chat_completion_create()
    }
    
    class GoogleStreamingClient {
        +llm_system = "google"
        #_chat_completion_create()
    }
    
    PlaygroundStreamingClient <|-- OpenAIBaseStreamingClient
    PlaygroundStreamingClient <|-- AnthropicStreamingClient
    PlaygroundStreamingClient <|-- AWSBedrockStreamingClient
    PlaygroundStreamingClient <|-- GoogleStreamingClient
```

**Sources**:
- [src/phoenix/server/api/helpers/playground_clients.py:161-285]()
- [src/phoenix/server/api/helpers/playground_clients.py:513-667]()
- [src/phoenix/server/api/helpers/playground_clients.py:869-1035]()
- [src/phoenix/server/api/helpers/playground_clients.py:1199-1380]()

### Provider Registration and Discovery

The system uses a decorator pattern to register provider implementations. At module initialization, all registered clients are collected and made available through `get_playground_client()`.

```mermaid
graph LR
    subgraph "Registration Phase"
        Decorator["@register_llm_client"]
        Provider1["OpenAIBaseStreamingClient"]
        Provider2["AnthropicStreamingClient"]
        
        Decorator -.decorates.-> Provider1
        Decorator -.decorates.-> Provider2
    end
    
    subgraph "Runtime Lookup"
        GetClient["get_playground_client()"]
        Initialize["initialize_playground_clients()"]
        Instance["PlaygroundStreamingClient instance"]
        
        Initialize --> GetClient
        GetClient --> Instance
    end
```

Key functions:
- `@register_llm_client` decorator at [src/phoenix/server/api/helpers/playground_registry.py:88-95]()
- `get_playground_client()` at [src/phoenix/server/api/helpers/playground_clients.py:1443-1532]()
- `initialize_playground_clients()` at [src/phoenix/server/api/subscriptions.py:70]()

---

## Execution Modes

The Playground supports two primary execution modes: single-instance runs for interactive prompt development, and dataset-based runs for systematic evaluation.

### Single Instance Mode

Used for quick iteration on prompts. Supports multiple repetitions per run and comparison across instances.

```mermaid
sequenceDiagram
    participant UI as PlaygroundOutput.tsx
    participant Sub as subscriptions.py
    participant Client as PlaygroundStreamingClient
    participant LLM as LLM Provider API
    
    UI->>Sub: _stream_single_chat_completion()
    
    loop Stream chunks
        Sub->>Client: chat_completion_create()
        Client->>LLM: Stream request
        LLM-->>Client: Token chunk
        Client-->>Sub: TextChunk | ToolCallChunk
        Sub-->>UI: Yield payload
    end
    
    Note over Sub: Create OTel Span
    Sub-->>UI: ChatCompletionSubscriptionResult (with Span)
```

**Sources**:
- [src/phoenix/server/api/subscriptions.py:76-135]()
- [app/src/pages/playground/PlaygroundOutput.tsx:230-331]()
- [src/phoenix/server/api/helpers/playground_clients.py:185-285]()

### Dataset Experiment Mode

Runs prompts across all examples in a dataset. This mode creates an `Experiment` record and stores results as `ExperimentRun` objects.

**Batching Strategy**: Dataset runs process examples in batches to balance throughput. The system builds template variables from dataset examples using `templateVariablesPath`.

**Sources**:
- [src/phoenix/server/api/subscriptions.py:369-564]()
- [app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx:1-1261]()
- [src/phoenix/server/api/helpers/message_helpers.py:73-112]()

---

## Streaming Implementation

The Playground uses GraphQL subscriptions to deliver real-time token-by-token responses. The backend converts provider-specific streaming APIs into a uniform `ChatCompletionChunk` union type.

### Chunk Type Hierarchy

The subscription emits different payload types:

| Payload Type | When Emitted | Contains |
|-------------|--------------|----------|
| `TextChunk` | During streaming | Incremental text content [src/phoenix/server/api/helpers/playground_clients.py:95]() |
| `ToolCallChunk` | During streaming | Incremental tool call arguments [src/phoenix/server/api/helpers/playground_clients.py:96]() |
| `ChatCompletionSubscriptionResult` | End of stream | Final `Span` with trace metadata [src/phoenix/server/api/subscriptions.py:129-132]() |
| `ChatCompletionSubscriptionError` | On error | Error message [src/phoenix/server/api/subscriptions.py:118-121]() |

### Concurrency Management

The subscription handler manages concurrent execution with cleanup guarantees. The cleanup sequence (cancel → await → aclose) is critical:

1. **Cancel all tasks**: Schedules `CancelledError` [src/phoenix/server/api/subscriptions.py:165-166]().
2. **Await all tasks**: Ensures tasks process cancellation [src/phoenix/server/api/subscriptions.py:170-174]().
3. **Close generators**: Runs `finally` blocks immediately [src/phoenix/server/api/subscriptions.py:177-187]().

---

## Frontend State Management

The frontend uses Zustand for global state with a normalized message structure to support drag-and-drop reordering.

### State Schema

```mermaid
graph TB
    subgraph "PlaygroundState"
        Instances["instances: PlaygroundNormalizedInstance[]"]
        Messages["allInstanceMessages: Record<number, ChatMessage>"]
    end
    
    subgraph "PlaygroundNormalizedInstance"
        InstanceId["id: number"]
        Template["template: PlaygroundNormalizedChatTemplate"]
        Repetitions["repetitions: Record<number, PlaygroundRepetition>"]
    end
    
    Template --> MessageIds["messageIds: number[]"]
    MessageIds -.references.-> Messages
```

**Normalization Rationale**: Messages are normalized (stored by ID in `allInstanceMessages`) to enable efficient reordering and shared message editing.

**Key Functions**:
- `normalizeChatTemplate()`: [app/src/store/playground/playgroundStore.tsx:104-118]()
- `createNormalizedPlaygroundInstance()`: [app/src/store/playground/playgroundStore.tsx:153-165]()

**Sources**:
- [app/src/store/playground/types.ts:43-91]()
- [app/src/store/playground/playgroundStore.tsx:1-224]()

---

## Integration with Tracing System

All Playground executions are captured as OpenTelemetry traces. The `Tracer` class manages span creation and cost calculation.

### Trace Recording Flow

1. **Start Span**: The `Tracer` is initialized with a `SpanCostCalculator` [src/phoenix/server/api/subscriptions.py:87]().
2. **Record Attributes**: Client records OpenInference conventions like `llm.model_name` and `llm.input_messages` [src/phoenix/server/api/helpers/playground_clients.py:197-205]().
3. **Persist Trace**: At the end of execution, traces are retrieved from the tracer and added to the DB session [src/phoenix/server/api/subscriptions.py:123-127]().

**Project Association**:
- Traces are associated with the `PLAYGROUND_PROJECT_NAME` project [src/phoenix/server/api/subscriptions.py:23]().

---

## Tool Calling Support

The Playground supports tool calling with provider-specific schema formats. The frontend allows JSON or UI-based tool definition editing.

### Tool Call Execution Flow

1. **Stream Partial Calls**: During streaming, tool call arguments arrive incrementally as `ToolCallChunk` [src/phoenix/server/api/helpers/playground_clients.py:96]().
2. **Accumulate in State**: The frontend state accumulates these partial arguments by ID using `addRepetitionPartialToolCall` [app/src/pages/playground/PlaygroundOutput.tsx:170]().
3. **Finalize**: Once streaming completes, the final tool call object is stored in the repetition [app/src/pages/playground/PlaygroundOutput.tsx:230-331]().

**Sources**:
- [src/phoenix/server/api/helpers/playground_clients.py:143-213]()
- [app/src/pages/playground/PlaygroundToolCall.tsx:110-121]()
- [app/src/pages/playground/playgroundUtils.ts:148-219]()

---

## Performance Optimizations

### Frontend Optimizations

- **Virtualized Rendering**: Dataset experiment tables use `useVirtualizer` to render only visible rows [app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx:8]().
- **Throttled Updates**: Metric aggregation during experiments is throttled to 2 seconds [app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx:128]().

### Backend Optimizations

- **Batched Database Writes**: Traces from concurrent repetitions are written in a single bulk operation [src/phoenix/server/api/subscriptions.py:124-126]().
- **Resource Cleanup**: Explicit `aclose()` on async generators ensures no resource leaks on cancelled subscriptions [src/phoenix/server/api/subscriptions.py:177-187]().

**Sources**:
- [app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx:1-204]()
- [src/phoenix/server/api/subscriptions.py:144-189]()

---

# Page: AI Agent Backend (PxI)

# AI Agent Backend (PxI)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-server/SKILL.md](.agents/skills/phoenix-server/SKILL.md)
- [.agents/skills/phoenix-server/references/database-patterns.md](.agents/skills/phoenix-server/references/database-patterns.md)
- [.agents/skills/phoenix-server/references/graphql-patterns.md](.agents/skills/phoenix-server/references/graphql-patterns.md)
- [.agents/skills/phoenix-server/references/test-patterns.md](.agents/skills/phoenix-server/references/test-patterns.md)
- [.github/workflows/pxi-evals.yml](.github/workflows/pxi-evals.yml)
- [REVIEW.md](REVIEW.md)
- [app/src/agent/chat/__tests__/shouldSendAutomatically.test.ts](app/src/agent/chat/__tests__/shouldSendAutomatically.test.ts)
- [app/src/agent/extensions/__tests__/toolRegistry.test.ts](app/src/agent/extensions/__tests__/toolRegistry.test.ts)
- [app/src/agent/extensions/toolRegistry.ts](app/src/agent/extensions/toolRegistry.ts)
- [app/src/agent/tools/playgroundPrompt/__tests__/playgroundPrompt.test.ts](app/src/agent/tools/playgroundPrompt/__tests__/playgroundPrompt.test.ts)
- [app/src/api/__generated__/v1.ts](app/src/api/__generated__/v1.ts)
- [app/src/components/agent/ToolPart.tsx](app/src/components/agent/ToolPart.tsx)
- [app/src/pages/playground/__tests__/playgroundAgentContextUtils.test.ts](app/src/pages/playground/__tests__/playgroundAgentContextUtils.test.ts)
- [app/src/pages/playground/playgroundAgentContextUtils.ts](app/src/pages/playground/playgroundAgentContextUtils.ts)
- [app/src/pages/settings/__generated__/CustomProviderFormTestCredentialsMutation.graphql.ts](app/src/pages/settings/__generated__/CustomProviderFormTestCredentialsMutation.graphql.ts)
- [app/tests/pxi/fixtures.ts](app/tests/pxi/fixtures.ts)
- [app/tests/pxi/ingest-traces-smoke.spec.ts](app/tests/pxi/ingest-traces-smoke.spec.ts)
- [docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx](docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx)
- [evals/pxi/README.md](evals/pxi/README.md)
- [evals/pxi/datasets/debug_trace_skill_trigger.yaml](evals/pxi/datasets/debug_trace_skill_trigger.yaml)
- [evals/pxi/datasets/in_app_links.yaml](evals/pxi/datasets/in_app_links.yaml)
- [evals/pxi/datasets/set_spans_filter.yaml](evals/pxi/datasets/set_spans_filter.yaml)
- [evals/pxi/datasets/set_time_range.yaml](evals/pxi/datasets/set_time_range.yaml)
- [evals/pxi/evaluators/__init__.py](evals/pxi/evaluators/__init__.py)
- [evals/pxi/evaluators/tools.py](evals/pxi/evaluators/tools.py)
- [evals/pxi/harness/agent_task.py](evals/pxi/harness/agent_task.py)
- [evals/pxi/harness/run_experiment.py](evals/pxi/harness/run_experiment.py)
- [js/packages/phoenix-client/src/__generated__/api/v1.ts](js/packages/phoenix-client/src/__generated__/api/v1.ts)
- [packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py](packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/anthropic/messages.py)
- [packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py](packages/phoenix-client/src/phoenix/client/helpers/sdk/openai/chat.py)
- [packages/phoenix-client/tests/canary/sdk/anthropic/test_messages.py](packages/phoenix-client/tests/canary/sdk/anthropic/test_messages.py)
- [packages/phoenix-client/tests/canary/sdk/openai/test_chat.py](packages/phoenix-client/tests/canary/sdk/openai/test_chat.py)
- [schemas/openapi.json](schemas/openapi.json)
- [src/phoenix/server/agents/__init__.py](src/phoenix/server/agents/__init__.py)
- [src/phoenix/server/agents/capabilities/tools/external/__init__.py](src/phoenix/server/agents/capabilities/tools/external/__init__.py)
- [src/phoenix/server/agents/context.py](src/phoenix/server/agents/context.py)
- [src/phoenix/server/agents/prompts/__init__.py](src/phoenix/server/agents/prompts/__init__.py)
- [src/phoenix/server/agents/prompts/context/PLAYGROUND_CONTEXT_INSTRUCTIONS.xml.j2](src/phoenix/server/agents/prompts/context/PLAYGROUND_CONTEXT_INSTRUCTIONS.xml.j2)
- [src/phoenix/server/agents/prompts/skills/annotate-spans/SKILL.md](src/phoenix/server/agents/prompts/skills/annotate-spans/SKILL.md)
- [src/phoenix/server/agents/prompts/skills/debug-trace/SKILL.md](src/phoenix/server/agents/prompts/skills/debug-trace/SKILL.md)
- [src/phoenix/server/agents/prompts/skills/playground/SKILL.md](src/phoenix/server/agents/prompts/skills/playground/SKILL.md)
- [src/phoenix/server/agents/skills/__init__.py](src/phoenix/server/agents/skills/__init__.py)
- [src/phoenix/server/agents/skills/annotate_spans.py](src/phoenix/server/agents/skills/annotate_spans.py)
- [src/phoenix/server/agents/skills/debug_trace.py](src/phoenix/server/agents/skills/debug_trace.py)
- [src/phoenix/server/api/routers/agents.py](src/phoenix/server/api/routers/agents.py)
- [src/phoenix/server/api/routers/v1/spans.py](src/phoenix/server/api/routers/v1/spans.py)
- [src/phoenix/server/api/routers/v1/traces.py](src/phoenix/server/api/routers/v1/traces.py)
- [src/phoenix/server/dml_event_handler.py](src/phoenix/server/dml_event_handler.py)
- [src/phoenix/tracers.py](src/phoenix/tracers.py)
- [tests/integration/_helpers.py](tests/integration/_helpers.py)
- [tests/integration/auth/conftest.py](tests/integration/auth/conftest.py)
- [tests/integration/auth/test_auth.py](tests/integration/auth/test_auth.py)
- [tests/unit/pxi/evals/test_agent_task_inputs.py](tests/unit/pxi/evals/test_agent_task_inputs.py)
- [tests/unit/pxi/evals/test_datasets.py](tests/unit/pxi/evals/test_datasets.py)
- [tests/unit/pxi/evals/test_evaluator_matchers.py](tests/unit/pxi/evals/test_evaluator_matchers.py)
- [tests/unit/pxi/evals/test_evaluators.py](tests/unit/pxi/evals/test_evaluators.py)
- [tests/unit/server/agents/capabilities/contexts/test_capabilities.py](tests/unit/server/agents/capabilities/contexts/test_capabilities.py)
- [tests/unit/server/agents/test_agent_factory.py](tests/unit/server/agents/test_agent_factory.py)
- [tests/unit/server/api/routers/v1/test_spans.py](tests/unit/server/api/routers/v1/test_spans.py)
- [tests/unit/server/api/routers/v1/test_traces.py](tests/unit/server/api/routers/v1/test_traces.py)
- [tests/unit/test_tracers.py](tests/unit/test_tracers.py)

</details>



The AI Agent Backend, also known as Phoenix Intelligence (PxI), provides the server-side infrastructure for Phoenix's AI assistant capabilities. This system enables the Phoenix frontend to interact with various Large Language Models (LLMs) through a unified API, leveraging `pydantic-ai` for agent orchestration, tool execution, and context management. It also handles the ingestion and export of OpenTelemetry traces generated by agent interactions.

The primary purpose of the PxI backend is to:
1.  **Orchestrate AI agents**: Manage the lifecycle of AI agent interactions, including message processing, tool invocation, and response generation.
2.  **Provide model selection**: Allow users to choose from a variety of LLMs, including built-in and custom providers, with appropriate credential management.
3.  **Enable tool capabilities**: Expose Phoenix-specific functionalities as tools that agents can use to interact with the Phoenix platform (e.g., querying traces, creating annotations).
4.  **Resolve context**: Incorporate relevant contextual information (e.g., current project, selected spans) into agent prompts to enhance their understanding and response quality.
5.  **Expose a REST endpoint**: Offer a `/agents` REST API for the frontend to communicate with the AI agent system, supporting streaming responses and Vercel AI SDK compatibility.
6.  **Trace agent activity**: Generate and manage OpenTelemetry traces for agent interactions, allowing for observability and cost tracking.

## Architecture Overview

The AI Agent Backend is built around a FastAPI router that exposes the `/agents` endpoint [src/phoenix/server/api/routers/agents.py:7](). This endpoint serves as the communication hub for the frontend AI assistant. Key components include:

*   **`pydantic-ai` Integration**: The core of the agent system relies on the `pydantic-ai` library for defining agents, models, and tools [src/phoenix/server/api/routers/agents.py:16-17]().
*   **Agent Factory (`build_agent`)**: Responsible for constructing the AI agent instance based on requested capabilities and model selection [src/phoenix/server/agents/agent_factory.py:35-42]().
*   **Model Factory (`build_model`)**: Handles the instantiation of LLM clients, resolving credentials and configuring providers [src/phoenix/server/agents/model_factory.py:136-166]().
*   **Context Resolution**: Gathers and formats contextual information from the Phoenix application state to inform the agent [src/phoenix/server/agents/context.py:48-51]().
*   **Tool Capabilities**: Defines the specific actions an agent can take within the Phoenix environment [src/phoenix/server/agents/capabilities/__init__.py]().
*   **OpenTelemetry Tracing**: Integrates with Phoenix's tracing system to record agent interactions, tool calls, and LLM invocations [src/phoenix/tracers.py:127-155]().

### AI Agent Backend Data Flow

The following diagram illustrates the high-level data flow when a user interacts with the AI agent in the Phoenix frontend:

"Natural Language Space" to "Code Entity Space" Mapping:

```mermaid
graph TD
    A["Phoenix Frontend (AgentChatPanel)"] --> B{{"POST /v1/agents/assistant/chat"}}
    B --> C["assistant_chat (agents.py)"]
    C --> D["ChatSubmitMessage (Pydantic Model)"]
    D --> E["resolve_contexts (context.py)"]
    D --> F["build_model (model_factory.py)"]
    E --> G["build_agent (agent_factory.py)"]
    F --> G
    G --> H["OpenInferenceAgentWrapper (pydantic_ai)"]
    H --> I{"Tool Invocation"}
    I --> J["Phoenix Backend Services"]
    J --> H
    H --> K["LLM Provider (OpenAI/Anthropic/etc)"]
    K --> H
    H --> L["Tracer (tracers.py)"]
    L --> M["models.Trace / models.Span (DB)"]
    H --> C
    C --> N["Streaming Response (VercelAIAdapter)"]
    N --> A
```
Sources:
- [src/phoenix/server/api/routers/agents.py:189-200]()
- [src/phoenix/server/agents/agent_factory.py:35-42]()
- [src/phoenix/server/agents/model_factory.py:136-166]()
- [src/phoenix/server/agents/context.py:48-51]()
- [src/phoenix/tracers.py:88-115]()

## `/agents` REST Endpoint

The primary interaction point for the frontend AI assistant is the `/v1/agents/assistant/chat` endpoint [src/phoenix/server/api/routers/agents.py:228](). This endpoint is designed to be compatible with the Vercel AI SDK, allowing for streaming responses and a standardized message format using `VercelAIAdapter` [src/phoenix/server/api/routers/agents.py:17]().

### Request Structure

The request body for the `/v1/agents/assistant/chat` endpoint is a discriminated union of `ChatSubmitMessage` and `ChatRegenerateMessage`, both extending `_ChatMessageMixin` [src/phoenix/server/api/routers/agents.py:189-194]().

```python
class _ChatMessageMixin(_ObservabilityMixin):
    """Phoenix-specific extensions added to Vercel AI request messages."""
    contexts: list[ChatContext] = Field(default_factory=list)
    messages: list[AssistantMetadataUIMessage]
    model: AgentModelSelection
```

The `_ChatMessageMixin` adds Phoenix-specific fields:
*   `contexts`: A list of `ChatContext` objects providing contextual information [src/phoenix/server/agents/context.py:107-122]().
*   `model`: An `AgentModelSelection` object specifying the chosen LLM provider and model [src/phoenix/server/api/routers/agents.py:186]().
*   `ingest_traces`: A boolean indicating whether to store traces locally [src/phoenix/server/api/routers/agents.py:169]().

Sources:
- [src/phoenix/server/api/routers/agents.py:173-187]()
- [src/phoenix/server/api/routers/agents.py:189-194]()
- [src/phoenix/server/agents/context.py:107-122]()

## Agent Factory

The `build_agent` function is responsible for creating the `pydantic-ai` agent instance. It configures tools based on the requested capabilities and model type [src/phoenix/server/agents/agent_factory.py:35-42]().

```python
def build_agent(
    *,
    model: Model,
    instructions: AgentInstructions | None = None,
    docs_mcp_server: MCPServerStreamableHTTP | None = None,
    enable_web_access: bool = False,
    tracer_provider: TracerProvider | None = None,
) -> OpenInferenceAgentWrapper[AgentDependencies, AgentOutput]:
    # ...
```

The agent is wrapped in an `OpenInferenceAgentWrapper` to automatically instrument agent runs with OpenTelemetry, ensuring that all agent activities are traced [src/phoenix/server/agents/pydantic_ai/openinference_agent_wrapper.py:69-76](). It specifically handles backfilling `TOOL` spans for external tools that may have been resolved since the previous turn.

Sources:
- [src/phoenix/server/agents/agent_factory.py:35-42]()
- [src/phoenix/server/agents/pydantic_ai/openinference_agent_wrapper.py:69-76]()

## Model Selection

The `build_model` function handles the instantiation of the appropriate `pydantic-ai` model based on the `AgentModelSelection` [src/phoenix/server/agents/model_factory.py:136-166]().

### Built-in vs Custom Providers

| Provider Type | Resolution Logic |
| :--- | :--- |
| **Built-in** | Resolves credentials from `_resolve_secrets` (DB) first, then `os.getenv` [src/phoenix/server/agents/model_factory.py:107-119](). |
| **Custom** | Retrieves `models.GenerativeModelCustomProvider` from DB using `GlobalID` [src/phoenix/server/agents/model_factory.py:167-177](). |

Custom providers allow users to define their own SDK configurations (OpenAI, Azure, Anthropic, AWS Bedrock, Google GenAI) [src/phoenix/server/agents/model_factory.py:167-177]().

Sources:
- [src/phoenix/server/agents/model_factory.py:136-166]()
- [src/phoenix/server/agents/model_factory.py:107-119]()

## Tool Capabilities

The agent's capabilities are determined by tool implementations. Key capabilities include:

*   **External Tools**: Dynamic capabilities resolved through the frontend tool registry [app/src/agent/extensions/toolRegistry.ts:160-167]().
*   **Documentation (MCP)**: Ability to search Phoenix documentation via an MCP server [src/phoenix/server/agents/agent_factory.py:63-67]().
*   **Web Access**: Optional search and fetch capabilities [src/phoenix/server/api/routers/agents.py:39-40]().
*   **Frontend-Executed Tools**: Tools like `bash` or `ask_user` that run in the client-side sandbox [app/src/agent/extensions/toolRegistry.ts:187-206]().

Sources:
- [src/phoenix/server/agents/agent_factory.py:49-72]()
- [app/src/agent/extensions/toolRegistry.ts:160-167]()

## Context Resolution

Context resolution transforms UI state into structured information for the LLM. `ChatContext` is a discriminated union of several types [src/phoenix/server/agents/context.py:107-122]():

*   **`AppContext`**: Per-turn browser clock and timezone [src/phoenix/client/__generated__/v1/__init__.py:28-32]().
*   **`ProjectContext`**: Active project and current span filters [src/phoenix/server/agents/context.py:31-47]().
*   **`TraceContext` / `AgentSpanContext`**: Details on specific traces or spans selected by the user [src/phoenix/client/__generated__/v1/__init__.py:11-16]().
*   **`DatasetContext`**: Context for datasets and dataset versions [src/phoenix/client/__generated__/v1/__init__.py:115-119]().

Sources:
- [src/phoenix/server/agents/context.py:107-122]()
- [src/phoenix/client/__generated__/v1/__init__.py:11-32]()

## OpenTelemetry Tracing (PxI)

PxI utilizes a specialized `Tracer` class to capture agent interactions in-memory and persist them as standard Phoenix traces [src/phoenix/tracers.py:127-155]().

### Tracer Implementation

The `Tracer` wraps an OTel `TracerProvider` and uses a `_BufferedSpanExporter` to hold spans until they are converted to DB models via `get_db_traces` [src/phoenix/tracers.py:127-155]().

```mermaid
graph LR
    subgraph "PxI Tracer (tracers.py)"
        TP["TracerProvider"] --> SP["SimpleSpanProcessor"]
        SP --> BSE["_BufferedSpanExporter"]
        BSE --> GDB["get_db_traces()"]
    end
    GDB --> TMODEL["models.Trace (DB)"]
    TMODEL --> SPANMODEL["models.Span (DB)"]
    SPANMODEL --> COST["models.SpanCost (DB)"]
```

### Key Tracing Features
*   **Detached Context**: `detached_otel_context` is used to ensure agent spans become root spans rather than children of the HTTP request span [src/phoenix/tracers.py:37-47]().
*   **Attribute Limits**: The tracer increases `max_span_attributes` to 100,000 to accommodate large chat histories [src/phoenix/tracers.py:134]().

Sources:
- [src/phoenix/tracers.py:37-47]()
- [src/phoenix/tracers.py:127-155]()

## PXI Evaluation Harness

Phoenix includes an evaluation harness specifically for testing PxI agents located in `evals/pxi/`. This system uses standard Phoenix evaluation patterns to measure agent performance on tool calling and context resolution tasks.

The harness includes:
*   **Agent Task Definition**: Defines tasks for the agent to perform during evaluation [evals/pxi/harness/agent_task.py]().
*   **Experiment Runner**: Logic to execute agent experiments and collect results [evals/pxi/harness/run_experiment.py]().
*   **Evaluators**: Specialized evaluators for checking tool call accuracy and output quality [evals/pxi/evaluators/tools.py]().

Sources:
- [evals/pxi/README.md]()
- [evals/pxi/evaluators/tools.py]()

---

# Page: Sessions & Annotations

# Sessions & Annotations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/@types/time.d.ts](app/src/@types/time.d.ts)
- [app/src/components/feedback/FeedbackActionToolbar.tsx](app/src/components/feedback/FeedbackActionToolbar.tsx)
- [app/src/components/feedback/index.ts](app/src/components/feedback/index.ts)
- [app/src/constants/feedbackConstants.ts](app/src/constants/feedbackConstants.ts)
- [app/src/constants/index.ts](app/src/constants/index.ts)
- [app/src/pages/project/SessionsTable.tsx](app/src/pages/project/SessionsTable.tsx)
- [app/src/pages/project/__generated__/SessionsTableQuery.graphql.ts](app/src/pages/project/__generated__/SessionsTableQuery.graphql.ts)
- [app/src/pages/project/__generated__/SessionsTable_sessions.graphql.ts](app/src/pages/project/__generated__/SessionsTable_sessions.graphql.ts)
- [app/src/pages/trace/SessionDetails.tsx](app/src/pages/trace/SessionDetails.tsx)
- [app/src/pages/trace/SessionDetailsTraceList.tsx](app/src/pages/trace/SessionDetailsTraceList.tsx)
- [app/src/pages/trace/SessionDetailsTracesView.tsx](app/src/pages/trace/SessionDetailsTracesView.tsx)
- [app/src/pages/trace/TraceFeedbackActionToolbar.tsx](app/src/pages/trace/TraceFeedbackActionToolbar.tsx)
- [app/src/pages/trace/__generated__/SessionDetailsQuery.graphql.ts](app/src/pages/trace/__generated__/SessionDetailsQuery.graphql.ts)
- [app/src/pages/trace/__generated__/SessionDetailsTraceListQuery.graphql.ts](app/src/pages/trace/__generated__/SessionDetailsTraceListQuery.graphql.ts)
- [app/src/pages/trace/__generated__/SessionDetailsTraceListRefetchQuery.graphql.ts](app/src/pages/trace/__generated__/SessionDetailsTraceListRefetchQuery.graphql.ts)
- [app/src/pages/trace/__generated__/SessionDetailsTraceList_traces.graphql.ts](app/src/pages/trace/__generated__/SessionDetailsTraceList_traces.graphql.ts)
- [app/src/pages/trace/__generated__/TraceFeedbackActionToolbarCreateAnnotationMutation.graphql.ts](app/src/pages/trace/__generated__/TraceFeedbackActionToolbarCreateAnnotationMutation.graphql.ts)
- [app/src/pages/trace/__generated__/TraceFeedbackActionToolbarDeleteAnnotationMutation.graphql.ts](app/src/pages/trace/__generated__/TraceFeedbackActionToolbarDeleteAnnotationMutation.graphql.ts)
- [scripts/generate_spans/generate_spans_for_time_series.py](scripts/generate_spans/generate_spans_for_time_series.py)
- [src/phoenix/db/types/annotation_configs.py](src/phoenix/db/types/annotation_configs.py)
- [src/phoenix/server/api/input_types/ProjectSessionSort.py](src/phoenix/server/api/input_types/ProjectSessionSort.py)
- [src/phoenix/server/api/mutations/annotation_config_mutations.py](src/phoenix/server/api/mutations/annotation_config_mutations.py)
- [src/phoenix/server/api/routers/v1/annotation_configs.py](src/phoenix/server/api/routers/v1/annotation_configs.py)
- [src/phoenix/server/api/types/AnnotationConfig.py](src/phoenix/server/api/types/AnnotationConfig.py)
- [src/phoenix/server/api/types/ProjectSession.py](src/phoenix/server/api/types/ProjectSession.py)
- [tests/unit/_helpers.py](tests/unit/_helpers.py)
- [tests/unit/db/types/test_annotation_configs.py](tests/unit/db/types/test_annotation_configs.py)
- [tests/unit/server/api/dataloaders/conftest.py](tests/unit/server/api/dataloaders/conftest.py)
- [tests/unit/server/api/mutations/test_annotation_config_mutations.py](tests/unit/server/api/mutations/test_annotation_config_mutations.py)
- [tests/unit/server/api/routers/v1/test_annotation_configs.py](tests/unit/server/api/routers/v1/test_annotation_configs.py)
- [tests/unit/server/api/types/test_Project.py](tests/unit/server/api/types/test_Project.py)
- [tests/unit/server/api/types/test_ProjectSession.py](tests/unit/server/api/types/test_ProjectSession.py)

</details>



This page details Phoenix's implementation of project sessions, session annotations, and the broader annotation system for spans and traces. Project sessions group multi-turn conversations, providing a higher-level view of user interactions. Annotations allow users to add qualitative and quantitative feedback to individual spans, traces, or entire sessions, which is crucial for evaluation and analysis.

## Project Sessions

A project session represents a grouping of related traces, typically forming a multi-turn conversation or a sequence of interactions within a larger task. Sessions are automatically created or updated based on the `session_id` attribute present on spans.

### Data Model and Creation

The core data model for sessions is `models.ProjectSession` [src/phoenix/db/models.py:537-553]().

**Session Creation/Update Logic:**
When a new span is ingested via `insert_span` [src/phoenix/db/insertion/span.py:25-29](), the system checks for a `session_id` attribute [src/phoenix/db/insertion/span.py:62-63]().
1. If a `session_id` is present and a `models.ProjectSession` with that ID already exists, the existing session's `start_time` and `end_time` are updated if the new span's times extend the session's range [src/phoenix/db/insertion/span.py:94-98]().
2. If a `session_id` is present but no corresponding `models.ProjectSession` exists, a new `models.ProjectSession` is created with the provided `session_id`, `start_time`, `end_time`, and `project_id` [src/phoenix/db/insertion/span.py:82-87]().
3. If a trace already has an associated `project_session_rowid`, that session is used, and any `session_id` on the incoming span is ignored for session association [src/phoenix/db/insertion/span.py:67-75]().

This ensures that traces with the same `session_id` are grouped under a single `ProjectSession` and that session time ranges accurately reflect the earliest and latest spans within them.

### Session Attributes

`ProjectSession` objects [src/phoenix/server/api/types/ProjectSession.py:42]() expose several key attributes via the GraphQL API:
*   `id`: The internal database ID.
*   `sessionId`: The user-defined session identifier (from `SpanAttributes.SESSION_ID`) [src/phoenix/server/api/types/ProjectSession.py:51-61]().
*   `numTraces`: The count of traces associated with the session, resolved via `session_num_traces` DataLoader [src/phoenix/server/api/types/ProjectSession.py:105-109]().
*   `startTime`, `endTime`: The earliest and latest timestamps of all spans within the session [src/phoenix/server/api/types/ProjectSession.py:64-87]().
*   `firstInput`, `lastOutput`: The input of the first trace and output of the last trace in the session [src/phoenix/server/api/types/ProjectSession.py:119-142]().
*   `tokenUsage`: Aggregated token counts for the session [src/phoenix/server/api/types/ProjectSession.py:145-153]().
*   `costSummary`: Aggregated cost information for the session [app/src/pages/trace/__generated__/SessionDetailsQuery.graphql.ts:18-31]().

### Frontend Display

Sessions are displayed in the frontend, primarily in the `SessionsTable` [app/src/pages/project/SessionsTable.tsx:125]() within a project view. This table allows users to browse sessions, sort them by various metrics, and filter them.

**Session Details View:**
Clicking on a session in the table navigates to the `SessionDetails` page [app/src/pages/trace/SessionDetails.tsx:161](). This page provides a comprehensive view of a single session, including:
*   Summary statistics like total tokens, cost, and P50 latency [app/src/pages/trace/SessionDetails.tsx:70-126]().
*   Session-level annotation summaries via `SessionAnnotationSummaryGroupStacks` [app/src/pages/trace/SessionDetails.tsx:130-133]().
*   A tabbed interface to view session "turns" (individual traces as conversational exchanges) [app/src/pages/trace/SessionDetailsTraceList.tsx:144-185]() or a list of all traces within the session [app/src/pages/trace/SessionDetailsTracesView.tsx]().

**Session Turns View (`SessionDetailsTraceList`):**
This view presents traces as a sequence of "turns," typically showing the input and output of each root span in a conversational format [app/src/pages/trace/SessionDetailsTraceList.tsx:144-185](). Each turn can display:
*   Input and output content via `RootSpanMessage` [app/src/pages/trace/SessionDetailsTraceList.tsx:144]().
*   Latency, token counts, and costs for the root span [app/src/pages/trace/SessionDetailsTraceList.tsx:40-44]().

### Natural Language to Code Space: Sessions

The following diagram maps session concepts to the implementation classes and database models.

```mermaid
graph LR
    subgraph "Natural Language Space"
        UserSession["User Session (Multi-turn Chat)"]
        TraceGroup["Trace Grouping"]
        CostAgg["Cost Aggregation"]
    end

    subgraph "Code Entity Space"
        PS_Model["models.ProjectSession (SQLAlchemy)"]
        PS_API["ProjectSession (Strawberry Type)"]
        S_Table["SessionsTable (React Component)"]
        I_Span["insert_span (Insertion Logic)"]
    end

    UserSession --> PS_Model
    TraceGroup --> I_Span
    CostAgg --> PS_API
    PS_Model -.-> PS_API
    PS_API -.-> S_Table
```
**Diagram: Session Entity Mapping**
Sources: [src/phoenix/db/models.py](), [src/phoenix/server/api/types/ProjectSession.py](), [app/src/pages/project/SessionsTable.tsx](), [src/phoenix/db/insertion/span.py]()

## Annotation System

Phoenix provides a flexible annotation system to attach metadata, labels, scores, and explanations to spans, traces, and sessions.

### Annotation Data Model

The core annotation models share common fields like `name`, `label`, `score`, and `explanation` [src/phoenix/db/models.py:656-670]().
*   `models.SpanAnnotation`: Associated with a specific span [src/phoenix/db/models.py:680-692]().
*   `models.TraceAnnotation`: Associated with an entire trace [src/phoenix/db/models.py:706-718]().
*   `models.SessionAnnotation`: Associated with a project session [src/phoenix/db/models.py:732-744]().

### Annotation Configuration

Phoenix allows defining configurations for annotations, which can be categorical, continuous, or freeform. These are managed via `AnnotationConfig` models [src/phoenix/db/types/annotation_configs.py:100-111]().

**Mutation Example:**
Users can create configurations via `create_annotation_config` [src/phoenix/server/api/mutations/annotation_config_mutations.py:160-199](). This mutation validates that names like `note` are reserved and ensures uniqueness within the database [src/phoenix/server/api/mutations/annotation_config_mutations.py:180-195]().

### Annotation Management

Annotations can be created, updated, and deleted via GraphQL mutations and REST API endpoints.

**GraphQL Mutations:**
*   `create_span_annotations`: Creates new span annotations with UPSERT behavior.
*   `create_trace_annotations`: Similar to span annotations, but for traces.
*   `delete_span_annotations`: Deletes span annotations by ID.

**Feedback UI Components:**
The frontend provides a `TraceFeedbackActionToolbar` [app/src/pages/trace/TraceFeedbackActionToolbar.tsx:32]() for traces, allowing users to quickly add feedback. This interacts with mutations like `TraceFeedbackActionToolbarCreateAnnotationMutation` [app/src/pages/trace/__generated__/TraceFeedbackActionToolbarCreateAnnotationMutation.graphql.ts]().

### Natural Language to Code Space: Annotations

The following diagram maps annotation concepts to the implementation components.

```mermaid
graph LR
    subgraph "Natural Language Space"
        Feedback["User Feedback / Labels"]
        EvalResult["LLM Evaluation Score"]
        Config["Annotation Config"]
    end

    subgraph "Code Entity Space"
        SA_Model["models.SpanAnnotation"]
        AC_Model["models.AnnotationConfig"]
        SF_Page["SpanFeedback (React)"]
        AC_Mut["create_annotation_config (Mutation)"]
    end

    Feedback --> SF_Page
    EvalResult --> SA_Model
    Config --> AC_Mut
    AC_Mut -.-> AC_Model
    SA_Model -.-> SF_Page
```
**Diagram: Annotation Entity Mapping**
Sources: [src/phoenix/db/models.py](), [src/phoenix/server/api/mutations/annotation_config_mutations.py](), [app/src/pages/trace/SpanFeedback.tsx]()

### Annotation Data Flow

The following diagram illustrates how annotations move from UI interactions or API calls into the database.

```mermaid
graph TD
    subgraph "Backend: Data & API"
        DB["Phoenix Database"]
        A["models.SpanAnnotation"]
        B["models.TraceAnnotation"]
        C["models.SessionAnnotation"]

        DB -- "stores" --> A
        DB -- "stores" --> B
        DB -- "stores" --> C

        GQL_Mutations["GraphQL Mutations"]
        GQL_Mutations -- "UPSERT" --> A
        GQL_Mutations -- "UPSERT" --> B
    end

    subgraph "Frontend: UI Components"
        SF_Page["SpanFeedback"]
        T_Toolbar["TraceFeedbackActionToolbar"]
        S_Details["SessionDetails"]

        SF_Page -- "Displays Table" --> A
        T_Toolbar -- "Creates" --> B
        S_Details -- "Summarizes" --> C
    end

    GQL_Mutations --> SF_Page
```
**Diagram: Annotation System Data Flow**
Sources: [src/phoenix/db/models.py](), [app/src/pages/trace/SpanFeedback.tsx](), [app/src/pages/trace/TraceFeedbackActionToolbar.tsx](), [app/src/pages/trace/SessionDetails.tsx]()

Sources:
* [app/src/pages/project/SessionsTable.tsx]()
* [app/src/pages/trace/SessionDetails.tsx]()
* [app/src/pages/trace/SessionDetailsTraceList.tsx]()
* [app/src/pages/trace/TraceFeedbackActionToolbar.tsx]()
* [src/phoenix/db/insertion/span.py]()
* [src/phoenix/db/models.py]()
* [src/phoenix/db/types/annotation_configs.py]()
* [src/phoenix/server/api/mutations/annotation_config_mutations.py]()
* [src/phoenix/server/api/types/ProjectSession.py]()

---

# Page: Development & Deployment

# Development & Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/settings.json](.claude/settings.json)
- [.codex/config.toml](.codex/config.toml)
- [.codex/hooks.json](.codex/hooks.json)
- [.codex/hooks/run_changed_file_checks.sh](.codex/hooks/run_changed_file_checks.sh)
- [.cursor/rules/typescript-packages/RULE.md](.cursor/rules/typescript-packages/RULE.md)
- [.dockerignore](.dockerignore)
- [.git-blame-ignore-revs](.git-blame-ignore-revs)
- [.github/workflows/cost-sync.yml](.github/workflows/cost-sync.yml)
- [.github/workflows/docker-build-experimental.yml](.github/workflows/docker-build-experimental.yml)
- [.github/workflows/docker-build-nightly.yml](.github/workflows/docker-build-nightly.yml)
- [.github/workflows/docker-build-release.yml](.github/workflows/docker-build-release.yml)
- [.github/workflows/helm-ci.yml](.github/workflows/helm-ci.yml)
- [.github/workflows/playwright.yaml](.github/workflows/playwright.yaml)
- [.github/workflows/publish.yaml](.github/workflows/publish.yaml)
- [.github/workflows/pull-requests.yaml](.github/workflows/pull-requests.yaml)
- [.github/workflows/python-CI.yml](.github/workflows/python-CI.yml)
- [.github/workflows/python-all-platforms.yml](.github/workflows/python-all-platforms.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.github/workflows/sync-lockfile-release-pr.yml](.github/workflows/sync-lockfile-release-pr.yml)
- [.github/workflows/typescript-CI.yml](.github/workflows/typescript-CI.yml)
- [.github/workflows/typescript-packages-CI.yml](.github/workflows/typescript-packages-CI.yml)
- [.github/workflows/typescript-packages-publish.yml](.github/workflows/typescript-packages-publish.yml)
- [.github/workflows/update-phoenix-package-versions.yml](.github/workflows/update-phoenix-package-versions.yml)
- [.gitignore](.gitignore)
- [.oxfmtrc.jsonc](.oxfmtrc.jsonc)
- [.tours/app.tour](.tours/app.tour)
- [.vscode/extensions.json](.vscode/extensions.json)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [DEVELOPMENT.md](DEVELOPMENT.md)
- [Dockerfile](Dockerfile)
- [app/README.md](app/README.md)
- [app/__tests__/authFetch.test.ts](app/__tests__/authFetch.test.ts)
- [requirements/canary/sdk/anthropic.txt](requirements/canary/sdk/anthropic.txt)
- [requirements/ci.txt](requirements/ci.txt)
- [scripts/update_helm.py](scripts/update_helm.py)
- [scripts/update_kustomize.py](scripts/update_kustomize.py)
- [tox.ini](tox.ini)

</details>



This page covers the development environment setup, build processes, testing infrastructure, and deployment strategies for Phoenix. It includes local development workflows, CI/CD pipelines, containerization, and production deployment options using Docker, Kubernetes, and Helm.

For configuration options and environment variables, see [Configuration Options](#9.3). For specific deployment scenarios, see [Deployment Guide](#9.4).

## Development Workflow & Tooling

This section provides an overview of the development environment setup, including essential tools, code formatting, linting, and pre-commit hooks. For details, see [Development Workflow & Tooling](#6.1).

Phoenix supports local development with SQLite or PostgreSQL databases, using `uv` for Python dependency management and `pnpm` for frontend builds.

### Local Development Setup

Phoenix development requires Python 3.10-3.14, Node.js LTS with pnpm, and optionally PostgreSQL for database testing.

**Development Dependencies:**
- Python 3.10-3.14 (matrix tested at [.github/workflows/python-CI.yml:106](), [.github/workflows/python-all-platforms.yml:46]())
- Node.js LTS with pnpm (installation instructions at [DEVELOPMENT.md:41-54]())
- PostgreSQL (optional, used in CI at [.github/workflows/python-all-platforms.yml:127-139]())
- `uv` 0.11.8 (specified at [.github/workflows/python-CI.yml:120]())

**Development Commands:**

| Command | File Reference | Purpose |
|---------|---------------|---------|
| `uv sync --python 3.10` | [DEVELOPMENT.md:34]() | Install Python dependencies in editable mode |
| `pnpm install` (in `app/`) | [DEVELOPMENT.md:67]() | Install Node.js dependencies |
| `pnpm run build` (in `app/`) | [DEVELOPMENT.md:68]() | Build the web application |
| `tox run -e unit_tests` | [DEVELOPMENT.md:103]() | Run unit tests |
| `pre-commit install` | [DEVELOPMENT.md:138]() | Install pre-commit hooks |

The development environment supports SQLite (default) and PostgreSQL backends. Database migrations run automatically on startup.

**Local Development Architecture**

```mermaid
graph TB
    subgraph "Development Setup"
        Dev["Developer"] --> UvSync["uv sync --python 3.10"]
        UvSync --> PythonVenv["Python Virtual Environment"]
        
        Dev --> NvmInstall["nvm install"]
        NvmInstall --> PnpmInstall["npm i -g pnpm"]
        PnpmInstall --> PnpmAppInstall["cd app && pnpm install"]
        PnpmAppInstall --> NodeModules["Node.js Dependencies"]
        
        PythonVenv --> Tox["tox.ini"]
        NodeModules --> AppBuild["cd app && pnpm run build"]
    end
    
    subgraph "Testing & Linting"
        Tox --> ToxList["tox list"]
        Tox --> UnitTests["tox run -e unit_tests"]
        Tox --> IntegrationTests["tox run -e integration_tests"]
        Tox --> TypeCheck["make typecheck-python"]
        
        Dev --> PreCommitInstall["pre-commit install"]
        PreCommitInstall --> GitHooks["Git Pre-Commit Hooks"]
    end
    
    subgraph "Build & Run"
        AppBuild --> FrontendAssets["Frontend Static Assets"]
        PythonVenv --> MakeBuildPython["make build-python"]
        MakeBuildPython --> PythonDist["Python Distribution"]
        
        FrontendAssets & PythonDist --> PhoenixServe["phoenix serve"]
        PhoenixServe --> FastAPI["FastAPI Server"]
        PhoenixServe --> ReactUI["React Web UI"]
    end
```

Sources: [DEVELOPMENT.md:25-141](), [tox.ini:1-163]()

## Testing Strategy

This section outlines the testing approach, including unit, integration, and E2E tests, database fixtures, and test organization. For details, see [Testing Strategy](#6.2).

Phoenix testing spans unit tests, integration tests, type checking, and browser-based E2E tests across multiple database backends and platforms.

**Test Categories:**

| Test Type | Entry Point | Fixtures/Tools | Database Support |
|-----------|-------------|----------------|------------------|
| Unit Tests | `tox run -e unit_tests` | `pytest` | SQLite, PostgreSQL [tox.ini:144-155]() |
| Integration | `tox run -e integration_tests` | `pytest` | SQLite, PostgreSQL [tox.ini:127-142]() |
| Type Check | `make typecheck-python` | `mypy`, `pyright` | N/A [DEVELOPMENT.md:122]() |
| E2E Tests | `pnpm test:e2e` (in `app/`) | `playwright` | SQLite in-memory [app/README.md:82]() |
| Package Tests | `tox run -e phoenix_client` | `pytest`, `mypy`, `pyright` | N/A [tox.ini:11-23]() |

The CI pipeline at [.github/workflows/python-CI.yml:1-37]() runs tests with matrix builds across Python versions. PostgreSQL tests use service containers defined at [.github/workflows/python-all-platforms.yml:127-139]().

**Test Infrastructure Architecture**

```mermaid
graph TD
    subgraph "Test Execution Environments"
        Tox["tox.ini"] --> PhoenixClientEnv["testenv:phoenix_client"]
        Tox --> PhoenixEvalsEnv["testenv:phoenix_evals"]
        Tox --> PhoenixOtelEnv["testenv:phoenix_otel"]
        Tox --> IntegrationTestsEnv["testenv:integration_tests"]
        Tox --> UnitTestsEnv["testenv:unit_tests"]
    end
    
    subgraph "CI Workflows"
        PythonCI[".github/workflows/python-CI.yml"] --> ChangesFilter["Filter Changes"]
        ChangesFilter --> PhoenixClientJob["phoenix-client job"]
        ChangesFilter --> PhoenixEvalsJob["phoenix-evals job"]
        ChangesFilter --> PhoenixOtelJob["phoenix-otel job"]
        
        PlaywrightCI[".github/workflows/playwright.yaml"] --> E2ETestJob["e2e-test job"]
    end
    
    subgraph "Test Tools & Databases"
        PhoenixClientEnv --> PytestClient["pytest packages/phoenix-client"]
        PhoenixClientEnv --> MypyClient["mypy packages/phoenix-client"]
        PhoenixClientEnv --> PyrightClient["pyright packages/phoenix-client"]
        
        IntegrationTestsEnv --> PytestIntegration["pytest tests/integration"]
        IntegrationTestsEnv --> SQLiteDB["(SQLite)"]
        IntegrationTestsEnv --> PostgresDB["(PostgreSQL)"]
        
        UnitTestsEnv --> PytestUnit["pytest tests/unit"]
        UnitTestsEnv --> SQLiteDB
        UnitTestsEnv --> PostgresDB
        
        E2ETestJob --> Playwright["Playwright"]
        Playwright --> PhoenixServer["Phoenix Server"]
    end
    
    PhoenixClientJob --> PhoenixClientEnv
    PhoenixEvalsJob --> PhoenixEvalsEnv
    PhoenixOtelJob --> PhoenixOtelEnv
    E2ETestJob --> Playwright
```

Sources: [tox.ini:1-166](), [.github/workflows/python-CI.yml:1-168](), [.github/workflows/playwright.yaml:1-132]()

## CI/CD Pipeline

This section documents the GitHub Actions workflows, conditional execution, quality gates, and deployment automation. For details, see [CI/CD Pipeline](#6.3).

Phoenix uses GitHub Actions for CI/CD with automated testing, schema validation, Docker image building, and Helm chart releases.

### Python CI Workflow

The Python CI workflow at [.github/workflows/python-CI.yml:1-37]() triggers on push to `main`/`version-*` branches and pull requests.

**CI Jobs and File References:**

| Job Name | Trigger Condition | Tool | File Reference |
|----------|------------------|---------|----------------|
| changes | Always | `dorny/paths-filter` | [.github/workflows/python-CI.yml:23-74]() |
| phoenix-client | `phoenix_client == 'true'` | `uvx tox run -e phoenix_client` | [.github/workflows/python-CI.yml:99-121]() |
| phoenix-evals | `phoenix_evals == 'true'` | `uvx tox run -e phoenix_evals` | [.github/workflows/python-CI.yml:123-145]() |
| test-json-canonicalization-schema | `json_canonicalization_schema == 'true'` | `make test-jcs` | [.github/workflows/python-CI.yml:170-210]() |

The `changes` job uses path filters defined at [.github/workflows/python-CI.yml:46-74]() to conditionally run downstream jobs.

### TypeScript CI Workflow

The TypeScript CI workflow at [.github/workflows/typescript-CI.yml:1-91]() validates frontend code changes.

**TypeScript CI Steps:**
- **Type Check**: `pnpm run typecheck` [.github/workflows/typescript-CI.yml:63-65]()
- **Formatting**: `pnpm run fmt:check` [.github/workflows/typescript-CI.yml:66-69]()
- **Lint**: `pnpm run lint` [.github/workflows/typescript-CI.yml:70-73]()
- **Relay Codegen**: `pnpm run build:relay` [.github/workflows/typescript-CI.yml:74-78]()
- **OpenAPI Codegen**: `pnpm run generate:openapi` [.github/workflows/typescript-CI.yml:79-83]()

Sources: [.github/workflows/python-CI.yml:1-210](), [.github/workflows/typescript-CI.yml:1-91](), [.github/workflows/playwright.yaml:1-132]()

## Release Management

This section explains the `release-please` configuration, versioning strategy, and package publishing. For details, see [Release Management](#6.4).

Phoenix uses `release-please` for automated release management, which creates release pull requests and manages versioning.

**Release Workflow:**
- The `release` workflow at [.github/workflows/release.yml:1-25]() triggers on push to `main`.
- It uses `googleapis/release-please-action@v4` to manage version bumps and changelogs [.github/workflows/release.yml:16-19]().
- If `releases_created == 'true'`, it triggers the `publish.yaml` workflow [.github/workflows/release.yml:21-22]().

**Docker Build and Release:**
- The `Publish Docker images` workflow at [.github/workflows/docker-build-release.yml:1-137]() triggers on git tags matching `arize-phoenix-v*`.
- It builds multi-architecture Docker images for `root`, `nonroot`, and `debug` variants [.github/workflows/docker-build-release.yml:17]().
- After building, it updates Kustomize and Helm chart versions via scripts [.github/workflows/docker-build-release.yml:113-120]().

Sources: [.github/workflows/release.yml:1-25](), [.github/workflows/docker-build-release.yml:1-137](), [Dockerfile:1-127]()

## Kubernetes Deployment

This section documents Helm charts, Kustomize manifests, and deployment strategies. For details, see [Kubernetes Deployment](#6.5).

Phoenix provides a Helm chart and Kustomize templates for Kubernetes deployment.

**Deployment Components:**
- **Dockerfile**: A multi-stage build that bundles the React frontend and FastAPI backend into a distroless image [Dockerfile:1-127]().
- **Helm Charts**: Managed in `helm/` directory with automated version updates [.github/workflows/docker-build-release.yml:117-120]().
- **Kustomize**: Templates updated automatically during release via `scripts/update_kustomize.py` [.github/workflows/docker-build-release.yml:113-116]().

**Deployment Entity Mapping**

```mermaid
graph TD
    subgraph "Source Artifacts"
        SrcDir["/src"]
        AppDir["/app"]
        PyProject["pyproject.toml"]
    end

    subgraph "Docker Build (Dockerfile)"
        FrontendBuilder["node:22-slim (frontend-builder)"]
        BackendBuilder["uv:0.11.8 (backend-builder)"]
        FinalImage["distroless/python3 (production)"]
    end

    subgraph "Kubernetes Deployment"
        HelmChart["/helm"]
        Kustomize["/scripts/update_kustomize.py"]
        PhoenixPod["phoenix.server.main"]
    end

    AppDir --> FrontendBuilder
    SrcDir & PyProject --> BackendBuilder
    FrontendBuilder -- "static assets" --> BackendBuilder
    BackendBuilder -- "venv & wheel" --> FinalImage
    FinalImage --> PhoenixPod
    HelmChart --> PhoenixPod
```

Sources: [Dockerfile:1-127](), [.github/workflows/docker-build-release.yml:1-137]()

## API Reference Documentation

This section explains the Sphinx-based Python API reference and hosting. For details, see [API Reference Documentation](#6.6).

The Phoenix Python API reference documentation is generated using Sphinx. Documentation for sub-packages like `phoenix-client` and `phoenix-evals` is maintained within their respective directories and ignored in version control until built [.gitignore:85-87]().

Sources: [.gitignore:85-87](), [DEVELOPMENT.md:150-176]()

---

# Page: Development Workflow & Tooling

# Development Workflow & Tooling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-design/SKILL.md](.agents/skills/phoenix-design/SKILL.md)
- [.agents/skills/phoenix-design/rules/bem.md](.agents/skills/phoenix-design/rules/bem.md)
- [.agents/skills/phoenix-design/rules/dialogs.md](.agents/skills/phoenix-design/rules/dialogs.md)
- [.agents/skills/phoenix-design/rules/error-display.md](.agents/skills/phoenix-design/rules/error-display.md)
- [.agents/skills/phoenix-design/rules/tokens.md](.agents/skills/phoenix-design/rules/tokens.md)
- [.claude/settings.json](.claude/settings.json)
- [.codex/config.toml](.codex/config.toml)
- [.codex/hooks.json](.codex/hooks.json)
- [.codex/hooks/run_changed_file_checks.sh](.codex/hooks/run_changed_file_checks.sh)
- [.cursor/rules/python/RULE.md](.cursor/rules/python/RULE.md)
- [.cursor/rules/typescript-packages/RULE.md](.cursor/rules/typescript-packages/RULE.md)
- [.git-blame-ignore-revs](.git-blame-ignore-revs)
- [.gitignore](.gitignore)
- [.oxfmtrc.jsonc](.oxfmtrc.jsonc)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [.tours/app.tour](.tours/app.tour)
- [.vscode/extensions.json](.vscode/extensions.json)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [DEVELOPMENT.md](DEVELOPMENT.md)
- [Makefile](Makefile)
- [app/README.md](app/README.md)
- [app/__tests__/authFetch.test.ts](app/__tests__/authFetch.test.ts)
- [scripts/docker/devops/Dockerfile](scripts/docker/devops/Dockerfile)
- [scripts/docker/devops/dev.sh](scripts/docker/devops/dev.sh)
- [scripts/docker/devops/docker-compose.yml](scripts/docker/devops/docker-compose.yml)
- [scripts/docker/devops/oidc-server/Dockerfile](scripts/docker/devops/oidc-server/Dockerfile)
- [scripts/docker/devops/overrides/ldap-no-email.yml](scripts/docker/devops/overrides/ldap-no-email.yml)
- [scripts/docker/devops/overrides/ldap-posix.yml](scripts/docker/devops/overrides/ldap-posix.yml)
- [scripts/docker/devops/smtp-server/Dockerfile](scripts/docker/devops/smtp-server/Dockerfile)
- [scripts/docker/devops/smtp-server/src/server.ts](scripts/docker/devops/smtp-server/src/server.ts)
- [scripts/docker/devops/vite-dev/Dockerfile](scripts/docker/devops/vite-dev/Dockerfile)

</details>



This page documents the development environment setup, tooling, and workflows for contributing to Phoenix. It covers package managers, code quality tools, testing frameworks, and common development commands for both Python and TypeScript codebases.

For information about CI/CD pipelines and automation, see [6.3 CI/CD Pipeline](). For testing strategies and fixtures, see [6.2 Testing Strategy]().

---

## Development Environment Overview

Phoenix is a dual-language monorepo requiring separate toolchains for Python and TypeScript development. The repository utilizes a `Makefile` to unify these disparate toolchains into a single entry point for common tasks [Makefile:1-112]().

### Toolchain Mapping

The following diagram bridges the natural language concepts of "Python Development" and "Frontend Development" to the specific code entities and tools used in the Phoenix repository.

```mermaid
graph TB
    subgraph "Python Toolchain (Code Entity Space)"
        uv["uv (tool.uv)"]
        tox["tox (tox.ini)"]
        ruff["ruff (tool.ruff)"]
        pyright["pyright (pyrightconfig.json)"]
        pytest["pytest (tool.pytest)"]
        alembic["alembic (src/phoenix/db/migrations)"]
    end
    
    subgraph "TypeScript Toolchain (Code Entity Space)"
        pnpm["pnpm (pnpm-workspace.yaml)"]
        vite["vite (app/vite.config.ts)"]
        oxfmt["oxfmt (.oxfmtrc.jsonc)"]
        oxlint["oxlint (oxlint-app)"]
        tsc["tsc (tsconfig.json)"]
        relay["relay-compiler (relay.config.js)"]
    end
    
    subgraph "Shared Entry Point"
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

**Sources:** [DEVELOPMENT.md:25-125](), [AGENTS.md:3-9](), [Makefile:27-40](), [.pre-commit-config.yaml:1-63]()

---

## Python Development Tools

### Package Management: uv
Phoenix uses `uv` as the primary Python package manager for fast, reliable dependency management [DEVELOPMENT.md:27-29](). The project enforces a specific version via `tool.uv.required-version` in `pyproject.toml` [DEVELOPMENT.md:29]().

The monorepo structure is managed via `uv` workspaces. Sub-packages located in the `packages/` directory are automatically installed in editable mode [DEVELOPMENT.md:36-38]():
- `arize-phoenix-evals`
- `arize-phoenix-otel`
- `arize-phoenix-client`

| Command | Implementation |
|---------|----------------|
| `uv sync --python 3.10` | Installs main package and workspace members in editable mode [DEVELOPMENT.md:31-35](). |
| `uv tool install pre-commit` | Installs the pre-commit runner globally [DEVELOPMENT.md:131-132](). |
| `uv lock --check` | Validates that `uv.lock` is consistent with `pyproject.toml` [pre-commit-config.yaml:56-62](). |

**Sources:** [DEVELOPMENT.md:27-38](), [AGENTS.md:7-12](), [.pre-commit-config.yaml:56-62]()

### Test & Environment Orchestration: tox
`tox` is used to manage isolated virtual environments for standardized execution of tests and quality checks across different Python versions and database backends [DEVELOPMENT.md:92-95]().

Common environments defined in `tox.ini` [DEVELOPMENT.md:94-105]():
- `unit_tests`: Executes `pytest`. Supports `--run-postgres` to test against a PostgreSQL instance [DEVELOPMENT.md:107-111]().
- `ruff`: Runs the `ruff` formatter and linter [DEVELOPMENT.md:147]().
- `clean_jupyter_notebooks`: Uses `nbconvert` to strip metadata and outputs from `.ipynb` files [DEVELOPMENT.md:148]().

**Sources:** [DEVELOPMENT.md:92-117](), [DEVELOPMENT.md:147-149]()

---

## TypeScript Development Tools

### Package Management: pnpm
The frontend application and TypeScript client libraries are managed using `pnpm` (version 9.15.5) [DEVELOPMENT.md:53]().

- **App Directory**: `app/` contains the React SPA [app/README.md:1-3]().
- **JS Directory**: `js/` contains TypeScript packages and shared utilities [Makefile:15]().

### Build and Quality Pipeline
The TypeScript workflow leverages modern, high-performance tooling for static analysis and compilation.

```mermaid
graph LR
    subgraph "Build Process"
        relay["Relay Compiler"] -- "Generates Types" --> tsc["TypeScript (tsc)"]
        tsc -- "Type Safety" --> vite["Vite / esbuild"]
    end
    
    subgraph "Quality Checks"
        oxlint["oxlint (Linter)"]
        oxfmt["oxfmt (Formatter)"]
        vitest["vitest (Unit)"]
    end
    
    style relay stroke-width:2px
    style vite stroke-width:2px
```

| Tool | Role | File Reference |
|------|------|----------------|
| **Vite** | Build system for the React SPA | [app/README.md:45]() |
| **Relay** | GraphQL client and code generator | [app/README.md:102]() |
| **oxlint** | Rust-based linter for JS/TS | [app/README.md:75](), [.pre-commit-config.yaml:39-50]() |
| **oxfmt** | Rust-based formatter | [app/README.md:75](), [.pre-commit-config.yaml:27-38]() |

**Sources:** [app/README.md:63-107](), [.pre-commit-config.yaml:27-50]()

---

## Pre-commit Hooks

Phoenix enforces strict quality gates via `pre-commit`. Hooks are defined in `.pre-commit-config.yaml` and run locally before every commit [DEVELOPMENT.md:138-141]().

Key hooks include:
1. **Python Formatting**: Calls `make format-python` (wrapping `ruff`) [pre-commit-config.yaml:4-9]().
2. **Python Linting**: Calls `make lint-python` (wrapping `ruff`) [pre-commit-config.yaml:10-15]().
3. **Notebook Cleaning**: Runs `uv run jupyter nbconvert` to clear outputs [pre-commit-config.yaml:16-26]().
4. **JS/TS Quality**: Runs `oxfmt` and `oxlint` on `app/` and `js/` directories [pre-commit-config.yaml:27-50]().
5. **Branch Protection**: Prevents direct commits to the local `main` branch [pre-commit-config.yaml:51-55]().

**Sources:** [.pre-commit-config.yaml:1-63](), [DEVELOPMENT.md:131-141]()

---

## Development Operations (DevOps) Tooling

For complex development scenarios involving external dependencies (PostgreSQL, OIDC, SMTP), Phoenix provides a Docker-based devops environment [scripts/docker/devops/docker-compose.yml:1-5]().

### Core Services
The `docker-compose.yml` in `scripts/docker/devops/` orchestrates:
- **Phoenix Server**: The main application running in a containerized Python environment [scripts/docker/devops/docker-compose.yml:35-97]().
- **PostgreSQL**: A database instance for testing persistence [scripts/docker/devops/docker-compose.yml:169-211]().
- **OIDC Server**: A mock OpenID Connect provider for testing authentication [scripts/docker/devops/docker-compose.yml:128-167]().
- **SMTP Server**: A mock mail server for testing notifications [scripts/docker/devops/docker-compose.yml:98-127]().

### Agent & IDE Integration
The repository contains configurations to assist AI agents (like Claude) and IDEs (like Cursor/VS Code) in maintaining code standards:
- **Claude Settings**: `.claude/settings.json` triggers automatic formatting (`ruff`) and lockfile syncing (`uv sync`) after the agent performs edits [claude/settings.json:1-26]().
- **VS Code Debugging**: A `launch.json` is provided for debugging the Python server within the Docker container [scripts/docker/devops/Dockerfile:114-117]().

**Sources:** [scripts/docker/devops/docker-compose.yml:1-211](), [.claude/settings.json:1-35](), [scripts/docker/devops/Dockerfile:1-124]()

---

# Page: Testing Strategy

# Testing Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/workflows/cost-sync.yml](.github/workflows/cost-sync.yml)
- [.github/workflows/docker-build-experimental.yml](.github/workflows/docker-build-experimental.yml)
- [.github/workflows/docker-build-nightly.yml](.github/workflows/docker-build-nightly.yml)
- [.github/workflows/docker-build-release.yml](.github/workflows/docker-build-release.yml)
- [.github/workflows/helm-ci.yml](.github/workflows/helm-ci.yml)
- [.github/workflows/playwright.yaml](.github/workflows/playwright.yaml)
- [.github/workflows/publish.yaml](.github/workflows/publish.yaml)
- [.github/workflows/pull-requests.yaml](.github/workflows/pull-requests.yaml)
- [.github/workflows/python-CI.yml](.github/workflows/python-CI.yml)
- [.github/workflows/python-all-platforms.yml](.github/workflows/python-all-platforms.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.github/workflows/sync-lockfile-release-pr.yml](.github/workflows/sync-lockfile-release-pr.yml)
- [.github/workflows/typescript-CI.yml](.github/workflows/typescript-CI.yml)
- [.github/workflows/typescript-packages-CI.yml](.github/workflows/typescript-packages-CI.yml)
- [.github/workflows/typescript-packages-publish.yml](.github/workflows/typescript-packages-publish.yml)
- [.github/workflows/update-phoenix-package-versions.yml](.github/workflows/update-phoenix-package-versions.yml)
- [Dockerfile](Dockerfile)
- [app/playwright.config.ts](app/playwright.config.ts)
- [app/src/components/code/LazyEditorWrapper.tsx](app/src/components/code/LazyEditorWrapper.tsx)
- [app/src/components/core/card/Card.tsx](app/src/components/core/card/Card.tsx)
- [app/src/components/core/card/types.ts](app/src/components/core/card/types.ts)
- [app/src/components/playground/model/InvocationParametersFormFields.tsx](app/src/components/playground/model/InvocationParametersFormFields.tsx)
- [app/src/components/playground/model/OpenAIApiTypeConfigFormField.tsx](app/src/components/playground/model/OpenAIApiTypeConfigFormField.tsx)
- [app/src/pages/dataset/evaluators/DatasetEvaluatorActionMenu.tsx](app/src/pages/dataset/evaluators/DatasetEvaluatorActionMenu.tsx)
- [app/src/pages/playground/PlaygroundChatTemplateFooter.tsx](app/src/pages/playground/PlaygroundChatTemplateFooter.tsx)
- [app/src/pages/playground/PlaygroundResponseFormat.tsx](app/src/pages/playground/PlaygroundResponseFormat.tsx)
- [app/src/pages/playground/PlaygroundToolType/JSONToolEditor.tsx](app/src/pages/playground/PlaygroundToolType/JSONToolEditor.tsx)
- [app/tests/admin-access.ts](app/tests/admin-access.ts)
- [app/tests/datasets.spec.ts](app/tests/datasets.spec.ts)
- [app/tests/login.rate-limit.spec.ts](app/tests/login.rate-limit.spec.ts)
- [app/tests/member-access.spec.ts](app/tests/member-access.spec.ts)
- [app/tests/playground-prompt-configuration.spec.ts](app/tests/playground-prompt-configuration.spec.ts)
- [app/tests/playground.spec.ts](app/tests/playground.spec.ts)
- [app/tests/projects.spec.ts](app/tests/projects.spec.ts)
- [app/tests/prompt-management.spec.ts](app/tests/prompt-management.spec.ts)
- [app/tests/server-evaluators.spec.ts](app/tests/server-evaluators.spec.ts)
- [app/tests/user-management.spec.ts](app/tests/user-management.spec.ts)
- [app/tests/utils/testServer.mjs](app/tests/utils/testServer.mjs)
- [app/tests/viewer-access.spec.ts](app/tests/viewer-access.spec.ts)
- [requirements/canary/sdk/anthropic.txt](requirements/canary/sdk/anthropic.txt)
- [requirements/ci.txt](requirements/ci.txt)
- [requirements/integration-tests.txt](requirements/integration-tests.txt)
- [scripts/update_helm.py](scripts/update_helm.py)
- [scripts/update_kustomize.py](scripts/update_kustomize.py)
- [src/phoenix/db/insertion/span.py](src/phoenix/db/insertion/span.py)
- [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py](src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py)
- [src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py](src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py)
- [tests/integration/conftest.py](tests/integration/conftest.py)
- [tests/integration/db_migrations/__init__.py](tests/integration/db_migrations/__init__.py)
- [tests/integration/db_migrations/conftest.py](tests/integration/db_migrations/conftest.py)
- [tests/integration/db_migrations/test_data_migration_4ded9e43755f_create_project_sessions_table.py](tests/integration/db_migrations/test_data_migration_4ded9e43755f_create_project_sessions_table.py)
- [tests/integration/db_migrations/test_db_schema_6a88424799fe_update_users_with_auth_method.py](tests/integration/db_migrations/test_db_schema_6a88424799fe_update_users_with_auth_method.py)
- [tests/integration/db_migrations/test_db_schema_a20694b15f82_cost.py](tests/integration/db_migrations/test_db_schema_a20694b15f82_cost.py)
- [tests/integration/db_migrations/test_db_schema_for_annotations.py](tests/integration/db_migrations/test_db_schema_for_annotations.py)
- [tests/integration/db_migrations/test_up_and_down_migrations.py](tests/integration/db_migrations/test_up_and_down_migrations.py)
- [tests/integration/project_sessions/conftest.py](tests/integration/project_sessions/conftest.py)
- [tests/integration/project_sessions/test_project_sessions.py](tests/integration/project_sessions/test_project_sessions.py)
- [tests/integration/server/test_launch_app.py](tests/integration/server/test_launch_app.py)
- [tox.ini](tox.ini)

</details>



## Purpose and Scope

This document describes Phoenix's comprehensive testing approach, including test types, organization, database fixtures, CI/CD integration, and quality gates. Phoenix employs a multi-layered testing strategy with unit tests, integration tests, end-to-end tests, type checking, and specialized tests for database migrations and third-party SDK compatibility.

For information about CI/CD pipeline workflows and automation, see [CI/CD Pipeline](6.3). For release processes, see [Release Management](6.4).

## Test Types and Scope

Phoenix implements multiple test layers to ensure reliability across all components:

| Test Type | Scope | Tools | Execution |
|-----------|-------|-------|-----------|
| **Unit Tests** | Individual components in isolation | `pytest`, `pytest-xdist` | Parallel, both SQLite and PostgreSQL |
| **Integration Tests** | Client-server interactions, GraphQL subscriptions, migrations | `pytest`, `httpx`, `tox` | Full stack with database (SQLite/Postgres) |
| **E2E Tests** | Complete user workflows (Playground, Datasets, Prompts) | Playwright | Browser automation (Chromium, Firefox) |
| **Type Checking** | Static type validation | `mypy`, `pyright`, TypeScript compiler | Pre-commit and CI |
| **Package Tests** | Individual package testing | `tox`, `pytest` per package | `phoenix-client`, `phoenix-evals`, `phoenix-otel` |
| **Canary Tests** | Third-party SDK compatibility | `tox`, `pytest` | OpenAI, Anthropic, Google Generative AI |
| **Migration Tests** | Database schema evolution | Alembic | Forward and backward data migrations |

Sources: [tox.ini:11-165](), [.github/workflows/python-CI.yml:99-168](), [.github/workflows/playwright.yaml:42-132](), [app/playwright.config.ts:71-109]()

## Test Organization and Structure

### Directory Layout

```
tests/
├── unit/                # Server-side logic unit tests
├── integration/         # Full stack and migration tests
│   ├── db_migrations/   # Alembic migration validation
│   ├── project_sessions/# Session grouping logic
│   └── server/          # App launch and lifecycle
packages/
├── phoenix-client/tests/# Python client SDK tests
├── phoenix-evals/tests/ # Evaluation framework tests
└── phoenix-otel/tests/  # OpenTelemetry integration tests
app/tests/               # Playwright E2E test suite
```

### E2E Test Configuration (Playwright)

End-to-end tests are configured in `app/playwright.config.ts` [app/playwright.config.ts:1-109](). The suite targets a local server started via `pnpm run dev:server:test` [app/playwright.config.ts:104-104]().

**Project Configuration**:
- **Setup**: Handles authentication via `auth.setup.ts` [app/playwright.config.ts:21-23]().
- **Storage State**: Authenticated sessions are stored in `playwright/.auth/admin.json` [app/playwright.config.ts:28-28]().
- **Sandbox Providers**: E2E tests for code evaluators require Deno (TypeScript) and CPython WASM (Python) to be available in the environment [.github/workflows/playwright.yaml:111-130]().

Sources: [app/playwright.config.ts:19-66](), [.github/workflows/playwright.yaml:111-130]()

## Database Fixture Strategy

Phoenix supports testing against both SQLite and PostgreSQL. The CI environment matrices ensure compatibility across both backends [.github/workflows/python-all-platforms.yml:45-46]().

### Data Insertion and Persistence

When testing span ingestion, the system interacts with `insert_span` in `src/phoenix/db/insertion/span.py` [src/phoenix/db/insertion/span.py:25-30](). This function handles the logic for creating or updating traces, projects, and sessions based on incoming OpenTelemetry data.

```mermaid
graph TD
    subgraph "Natural Language Space"
        msg["'What is 2+2?'"]
        resp["'The answer is 4'"]
    end

    subgraph "Code Entity Space (SQLAlchemy Models)"
        span_obj["models.Span (src/phoenix/db/models.py)"]
        trace_obj["models.Trace (src/phoenix/db/models.py)"]
        session_obj["models.ProjectSession (src/phoenix/db/models.py)"]
    end

    subgraph "Insertion Logic (src/phoenix/db/insertion/span.py)"
        ins["insert_span()"]
        ioc["insert_on_conflict()"]
    end

    msg -->|Attribute| span_obj
    resp -->|Attribute| span_obj
    span_obj --> ins
    ins --> trace_obj
    ins --> session_obj
    ins --> ioc
    ioc -->|Persist| DB[("SQL Database")]
```

Sources: [src/phoenix/db/insertion/span.py:25-161](), [src/phoenix/db/models.py:1-50]()

## Migration Testing

Phoenix rigorously tests database migrations to prevent data loss. Tests in `tests/integration/db_migrations/` verify both schema changes and data migrations [tests/integration/db_migrations/test_up_and_down_migrations.py:1-10]().

- **Up/Down Tests**: Ensures `alembic upgrade` and `alembic downgrade` are reversible [tests/integration/db_migrations/test_up_and_down_migrations.py:7-15]().
- **Data Migrations**: Specific scripts like `populate_project_sessions.py` are tested to ensure existing traces are correctly grouped into new session entities [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py:11-20]().

Sources: [tests/integration/db_migrations/test_up_and_down_migrations.py:1-15](), [src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py:11-40]()

## Package and Canary Testing

Phoenix uses `tox` to manage isolated testing environments for its distributed packages [tox.ini:1-11]().

### Canary Tests for LLM SDKs
Canary tests ensure that updates to third-party SDKs (OpenAI, Anthropic, etc.) do not break Phoenix's instrumentation [tox.ini:24-103]().
- **Environment**: Tox installs specific SDK versions and runs tests with socket communication disabled to ensure no real API calls are made [tox.ini:49-49]().
- **Validation**: Uses `pyright` and `mypy` to check type compatibility with SDK helpers [tox.ini:45-48]().

Sources: [tox.ini:24-103](), [tox.ini:45-49]()

## End-to-End Test Scenarios

### Server Evaluators
Validates the creation of datasets and the attachment of LLM or Code-based evaluators [app/tests/server-evaluators.spec.ts:18-23]().
- **Workflow**: Create dataset -> Add Example manually -> Add Prebuilt LLM Evaluator -> Verify scoring [app/tests/server-evaluators.spec.ts:24-171]().

### Prompt Management
Tests the lifecycle of prompts within the Playground [app/tests/prompt-management.spec.ts:11-12]().
- **Workflow**: New Prompt -> Save in Playground -> Create Version -> Verify version history [app/tests/prompt-management.spec.ts:12-100]().

### User & Access Management
Verifies Role-Based Access Control (RBAC) [app/tests/user-management.spec.ts:3-51]().
- **Roles**: Tests for `admin`, `member`, and `viewer` roles across different projects [app/tests/member-access.spec.ts:6-40]().

Sources: [app/tests/server-evaluators.spec.ts:18-171](), [app/tests/prompt-management.spec.ts:11-127](), [app/tests/user-management.spec.ts:3-51]()

## Code Entity Association Diagram

This diagram maps high-level features to the specific code entities and test files that validate them.

```mermaid
graph LR
    subgraph "Feature Systems"
        ingest["Span Ingestion"]
        evals["Evaluations"]
        sessions["Project Sessions"]
    end

    subgraph "Implementation Entities"
        ins_span["insert_span (src/phoenix/db/insertion/span.py)"]
        mod_session["ProjectSession (src/phoenix/db/models.py)"]
        pkg_evals["arize-phoenix-evals (packages/phoenix-evals)"]
    end

    subgraph "Test Entities"
        test_ins["tests/integration/server/test_launch_app.py"]
        test_sess["tests/integration/project_sessions/test_project_sessions.py"]
        tox_evals["tox -e phoenix_evals"]
    end

    ingest --> ins_span
    ins_span --> test_ins
    sessions --> mod_session
    mod_session --> test_sess
    evals --> pkg_evals
    pkg_evals --> tox_evals
```

Sources: [src/phoenix/db/insertion/span.py:25-30](), [tests/integration/project_sessions/test_project_sessions.py:1-20](), [tox.ini:105-114]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-docs-gap-audit/SKILL.md](.agents/skills/phoenix-docs-gap-audit/SKILL.md)
- [.agents/skills/phoenix-skills-audit/SKILL.md](.agents/skills/phoenix-skills-audit/SKILL.md)
- [.agents/skills/phoenix-skills-audit/evals/evals.json](.agents/skills/phoenix-skills-audit/evals/evals.json)
- [.dockerignore](.dockerignore)
- [.eslintignore](.eslintignore)
- [.github/.scripts/collect-customer-issues.js](.github/.scripts/collect-customer-issues.js)
- [.github/workflows/auto-label-external-issues.yaml](.github/workflows/auto-label-external-issues.yaml)
- [.github/workflows/check-card-links.yml](.github/workflows/check-card-links.yml)
- [.github/workflows/check-dependabot-uv-version.yml](.github/workflows/check-dependabot-uv-version.yml)
- [.github/workflows/cla.yml](.github/workflows/cla.yml)
- [.github/workflows/claude-code-review.yml](.github/workflows/claude-code-review.yml)
- [.github/workflows/claude-docs-gap-audit.yml](.github/workflows/claude-docs-gap-audit.yml)
- [.github/workflows/claude-implement-issue.yml](.github/workflows/claude-implement-issue.yml)
- [.github/workflows/claude-llms-txt.yml](.github/workflows/claude-llms-txt.yml)
- [.github/workflows/claude-release-notes.yml](.github/workflows/claude-release-notes.yml)
- [.github/workflows/claude-skills-audit.yml](.github/workflows/claude-skills-audit.yml)
- [.github/workflows/claude-weekly-deps-upgrade.yml](.github/workflows/claude-weekly-deps-upgrade.yml)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)
- [.github/workflows/collect-customer-issues.yaml](.github/workflows/collect-customer-issues.yaml)
- [.github/workflows/cost-sync.yml](.github/workflows/cost-sync.yml)
- [.github/workflows/docker-build-experimental.yml](.github/workflows/docker-build-experimental.yml)
- [.github/workflows/docker-build-nightly.yml](.github/workflows/docker-build-nightly.yml)
- [.github/workflows/docker-build-release.yml](.github/workflows/docker-build-release.yml)
- [.github/workflows/helm-ci.yml](.github/workflows/helm-ci.yml)
- [.github/workflows/openapi-schema.yaml](.github/workflows/openapi-schema.yaml)
- [.github/workflows/playwright.yaml](.github/workflows/playwright.yaml)
- [.github/workflows/publish.yaml](.github/workflows/publish.yaml)
- [.github/workflows/pull-requests.yaml](.github/workflows/pull-requests.yaml)
- [.github/workflows/python-CI.yml](.github/workflows/python-CI.yml)
- [.github/workflows/python-all-platforms.yml](.github/workflows/python-all-platforms.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.github/workflows/sync-lockfile-release-pr.yml](.github/workflows/sync-lockfile-release-pr.yml)
- [.github/workflows/typescript-CI.yml](.github/workflows/typescript-CI.yml)
- [.github/workflows/typescript-packages-CI.yml](.github/workflows/typescript-packages-CI.yml)
- [.github/workflows/typescript-packages-publish-experimental.yml](.github/workflows/typescript-packages-publish-experimental.yml)
- [.github/workflows/typescript-packages-publish.yml](.github/workflows/typescript-packages-publish.yml)
- [.github/workflows/update-phoenix-package-versions.yml](.github/workflows/update-phoenix-package-versions.yml)
- [CLA.md](CLA.md)
- [Dockerfile](Dockerfile)
- [requirements/canary/sdk/anthropic.txt](requirements/canary/sdk/anthropic.txt)
- [requirements/ci.txt](requirements/ci.txt)
- [scripts/update_helm.py](scripts/update_helm.py)
- [scripts/update_kustomize.py](scripts/update_kustomize.py)
- [tox.ini](tox.ini)

</details>



This page documents Phoenix's continuous integration and continuous deployment infrastructure. It covers GitHub Actions workflows for testing, code generation validation, Docker image builds, and automated releases. For information about the release process and versioning, see [Release Management](#6.4). For Docker image variants and deployment strategies, see [Kubernetes Deployment](#6.5).

---

## Overview

Phoenix uses GitHub Actions for all CI/CD operations. All workflows use concurrency controls to cancel in-progress runs when new commits are pushed, optimizing resource usage [ .github/workflows/python-CI.yml:14-16 ]().

The pipeline system is organized into several specialized workflows:
- **Python CI**: Core server and package testing.
- **TypeScript CI**: Frontend and JS package validation.
- **Playwright**: End-to-end browser testing.
- **Docker Builds**: Multi-architecture image publishing.
- **Canary Tests**: Third-party SDK compatibility verification.
- **Claude Agentic Workflows**: AI-driven code review and issue implementation.

---

## Pipeline Architecture

The following diagram bridges the high-level workflow triggers to the specific test environments and tools used in the pipeline.

```mermaid
graph TB
    subgraph "Triggers"
        PushMain["push: main, version-*"]
        PullRequest["pull_request"]
        TagRelease["push: tags/arize-phoenix-v*"]
        Schedule["schedule: cron"]
    end
    
    subgraph "GitHub Actions Workflows"
        PythonCI["python-CI.yml"]
        TypeScriptCI["typescript-CI.yml"]
        PlaywrightWF["playwright.yaml"]
        DockerRelease["docker-build-release.yml"]
        ClaudeReview["claude-code-review.yml"]
    end
    
    subgraph "Execution Layer (Tox/UV/PNPM)"
        ToxEnv["tox -e"]
        UVsync["uv sync"]
        PNPMrun["pnpm run"]
    end

    subgraph "Quality Gates"
        Pytest["pytest (Unit/Integration)"]
        MyPy["mypy --strict"]
        Pyright["pyright"]
        PlaywrightTest["pnpm test:e2e"]
        Lint["ruff / oxlint"]
    end
    
    PushMain --> PythonCI
    PullRequest --> PythonCI
    PullRequest --> ClaudeReview
    PushMain --> PlaywrightWF
    Schedule --> PlaywrightWF
    TagRelease --> DockerRelease
    
    PythonCI --> ToxEnv
    ToxEnv --> Pytest
    ToxEnv --> MyPy
    ToxEnv --> Pyright
    
    PlaywrightWF --> UVsync
    PlaywrightWF --> PlaywrightTest
    
    TypeScriptCI --> PNPMrun
    PNPMrun --> Lint
```

**Sources**: [ .github/workflows/python-CI.yml:5-12 ](), [ .github/workflows/typescript-CI.yml:5-12 ](), [ .github/workflows/playwright.yaml:5-17 ](), [ .github/workflows/docker-build-release.yml:4-7 ](), [ tox.ini:1-11 ]()

---

## Python CI Pipeline

The main Python CI workflow ([.github/workflows/python-CI.yml]()) orchestrates testing for the `arize-phoenix` server and all sub-packages.

### Job Filtering Strategy
The `changes` job uses `dorny/paths-filter` to detect which components were modified, gating subsequent jobs to save compute [ .github/workflows/python-CI.yml:23-46 ]().

| Output Key | Path Pattern |
| :--- | :--- |
| `phoenix` | `src/**`, `tests/**`, `pyproject.toml`, `tox.ini` [ .github/workflows/python-CI.yml:52-58 ]() |
| `phoenix_client` | `packages/phoenix-client/**`, `tox.ini` [ .github/workflows/python-CI.yml:59-61 ]() |
| `phoenix_evals` | `packages/phoenix-evals/**`, `tox.ini` [ .github/workflows/python-CI.yml:62-64 ]() |
| `phoenix_otel` | `packages/phoenix-otel/**`, `tox.ini` [ .github/workflows/python-CI.yml:65-67 ]() |

### Tox Environment Execution
Test execution is standardized via `tox`. Key environments include:
- `phoenix_client`: Runs `pyright`, `mypy --strict`, and `pytest tests/client` [ tox.ini:11-22 ]().
- `phoenix_evals`: Runs tests for the `arize-phoenix-evals` package [ tox.ini:105-114 ]().
- `unit_tests`: Executes server unit tests with `PHOENIX_MASK_INTERNAL_SERVER_ERRORS` disabled [ tox.ini:144-155 ]().
- `integration_tests`: Runs integration tests across supported DB backends [ tox.ini:127-142 ]().

**Sources**: [ .github/workflows/python-CI.yml:23-170 ](), [ tox.ini:1-166 ]()

---

## Agentic Workflows (Claude Code)

Phoenix integrates `anthropics/claude-code-action` for AI-assisted development.

### Claude Code Review
Triggered on pull requests, this workflow uses Claude to perform automated code reviews. It is granted `id-token: write` permissions to request a GitHub OIDC token for secure interaction [ .github/workflows/claude-code-review.yml:1-27 ](). It utilizes the `code-review` plugin and is allowed to use tools like `git diff` and `gh pr view` [ .github/workflows/claude-code-review.yml:57-66 ]().

### Claude Implement Issue
Triggered when the `good-agent-issue` label is added to a GitHub issue [ .github/workflows/claude-implement-issue.yml:3-10 ]().
1. **Guard**: Verifies the sender has write access and the issue isn't already assigned [ .github/workflows/claude-implement-issue.yml:21-49 ]().
2. **Implementation**: Claude explores the codebase, creates a plan, and implements the fix in a new branch `claude/issue-{number}` [ .github/workflows/claude-implement-issue.yml:102-147 ]().
3. **Validation**: The agent is required to run tests and linting via `make` targets before exiting [ .github/workflows/claude-implement-issue.yml:134-138 ]().

**Sources**: [ .github/workflows/claude-code-review.yml:1-69 ](), [ .github/workflows/claude-implement-issue.yml:1-152 ]()

---

## End-to-End Testing (Playwright)

End-to-end tests run against a live server. Because Phoenix supports sandboxed code execution, the CI runner must mirror the production environment's binary dependencies.

### Sandbox Runtime Setup
- **Deno**: Installed via `denoland/setup-deno` at version `v2.1.4` for TypeScript evaluators [ .github/workflows/playwright.yaml:111-114 ]().
- **CPython WASM**: Pre-downloaded and verified with SHA-256 (`e5dc5a39...`) to prevent tampering. The path is exported via `PHOENIX_WASM_BINARY_PATH` for the server's `ensure_wasm_binary()` function [ .github/workflows/playwright.yaml:115-130 ]().

**Sources**: [ .github/workflows/playwright.yaml:42-132 ]()

---

## Docker Build & Deployment Automation

The Docker build process produces multi-architecture images and automates the propagation of version updates to deployment manifests.

```mermaid
graph LR
    subgraph "Build Process"
        DF[Dockerfile] --> FB["frontend-builder (node:22)"]
        DF --> BB["backend-builder (uv:0.11.8)"]
        FB --> BB
        BB --> Final["Distroless Image"]
    end
    
    subgraph "CI Workflow: docker-build-release.yml"
        Push["push_to_registry"] --> UpdateK["Update Kustomize"]
        Push --> UpdateH["Update Helm"]
        UpdateK --> PR["Create Pull Request"]
        UpdateH --> PR
    end

    Final -- "Pushed to" --> Hub["Docker Hub: arizephoenix/phoenix"]
    Hub -- "Version Tag" --> Push
```

### Docker Multi-Stage Build
1. **Frontend**: Builds the React app using `pnpm run build` [ Dockerfile:27-37 ]().
2. **Backend**: Uses `uv sync` with `--extra container` and `--extra pg` for PostgreSQL support [ Dockerfile:40-54 ]().
3. **Final**: A distroless image containing the `.venv`, a statically linked `deno` binary, and the CPython WASM binary [ Dockerfile:98-109 ]().

### Deployment Synchronization
Upon successful image push, the workflow runs:
- `scripts/update_kustomize.py` [ .github/workflows/docker-build-release.yml:116 ]()
- `scripts/update_helm.py` [ .github/workflows/docker-build-release.yml:120 ]()

This results in an automated PR (using `peter-evans/create-pull-request`) to update the production manifests in the repository [ .github/workflows/docker-build-release.yml:125-136 ]().

**Sources**: [ Dockerfile:22-127 ](), [ .github/workflows/docker-build-release.yml:1-136 ]()

---

## Canary Tests

Canary tests ensure compatibility with third-party LLM SDKs. These tests are unique because they verify behavior both with and without the SDKs installed to ensure Phoenix's instrumentation stubs do not break.

| SDK | Module Tested | Tox Environment |
| :--- | :--- | :--- |
| `openai` | `chat` | `phoenix_client_canary_tests_sdk_openai` [ tox.ini:24 ]() |
| `anthropic` | `messages` | `phoenix_client_canary_tests_sdk_anthropic` [ tox.ini:51 ]() |
| `google-generativeai` | `generate_content` | `phoenix_client_canary_tests_sdk_google_generativeai` [ tox.ini:78 ]() |

These environments use `pyright` and `mypy --strict --follow-untyped-imports` to validate type safety against the latest SDK releases [ tox.ini:45-48 ]().

**Sources**: [ tox.ini:24-103 ]()

---

# Page: Release Management

# Release Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/phoenix-release-please/SKILL.md](.agents/skills/phoenix-release-please/SKILL.md)
- [.dockerignore](.dockerignore)
- [.github/workflows/cost-sync.yml](.github/workflows/cost-sync.yml)
- [.github/workflows/docker-build-experimental.yml](.github/workflows/docker-build-experimental.yml)
- [.github/workflows/docker-build-nightly.yml](.github/workflows/docker-build-nightly.yml)
- [.github/workflows/docker-build-release.yml](.github/workflows/docker-build-release.yml)
- [.github/workflows/helm-ci.yml](.github/workflows/helm-ci.yml)
- [.github/workflows/playwright.yaml](.github/workflows/playwright.yaml)
- [.github/workflows/publish.yaml](.github/workflows/publish.yaml)
- [.github/workflows/pull-requests.yaml](.github/workflows/pull-requests.yaml)
- [.github/workflows/python-CI.yml](.github/workflows/python-CI.yml)
- [.github/workflows/python-all-platforms.yml](.github/workflows/python-all-platforms.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.github/workflows/sync-lockfile-release-pr.yml](.github/workflows/sync-lockfile-release-pr.yml)
- [.github/workflows/typescript-CI.yml](.github/workflows/typescript-CI.yml)
- [.github/workflows/typescript-packages-CI.yml](.github/workflows/typescript-packages-CI.yml)
- [.github/workflows/typescript-packages-publish.yml](.github/workflows/typescript-packages-publish.yml)
- [.github/workflows/update-phoenix-package-versions.yml](.github/workflows/update-phoenix-package-versions.yml)
- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [Dockerfile](Dockerfile)
- [MIGRATION.md](MIGRATION.md)
- [internal_docs/specs/playground.md](internal_docs/specs/playground.md)
- [internal_docs/specs/prompts.md](internal_docs/specs/prompts.md)
- [internal_docs/specs/server_evaluators.md](internal_docs/specs/server_evaluators.md)
- [kustomize/README.md](kustomize/README.md)
- [packages/phoenix-client/CHANGELOG.md](packages/phoenix-client/CHANGELOG.md)
- [packages/phoenix-client/pyproject.toml](packages/phoenix-client/pyproject.toml)
- [packages/phoenix-evals/CHANGELOG.md](packages/phoenix-evals/CHANGELOG.md)
- [packages/phoenix-evals/docs/source/api/evals.rst](packages/phoenix-evals/docs/source/api/evals.rst)
- [packages/phoenix-evals/docs/source/index.md](packages/phoenix-evals/docs/source/index.md)
- [packages/phoenix-evals/pyproject.toml](packages/phoenix-evals/pyproject.toml)
- [packages/phoenix-otel/CHANGELOG.md](packages/phoenix-otel/CHANGELOG.md)
- [packages/phoenix-otel/pyproject.toml](packages/phoenix-otel/pyproject.toml)
- [packages/phoenix-otel/src/phoenix/otel/__init__.py](packages/phoenix-otel/src/phoenix/otel/__init__.py)
- [packages/phoenix-otel/src/phoenix/otel/otel.py](packages/phoenix-otel/src/phoenix/otel/otel.py)
- [packages/phoenix-otel/tests/__init__.py](packages/phoenix-otel/tests/__init__.py)
- [packages/phoenix-otel/tests/test_exports.py](packages/phoenix-otel/tests/test_exports.py)
- [packages/phoenix-otel/tests/test_otel.py](packages/phoenix-otel/tests/test_otel.py)
- [packages/phoenix-otel/tests/test_settings.py](packages/phoenix-otel/tests/test_settings.py)
- [pyproject.toml](pyproject.toml)
- [release-please-config.json](release-please-config.json)
- [requirements/canary/sdk/anthropic.txt](requirements/canary/sdk/anthropic.txt)
- [requirements/ci.txt](requirements/ci.txt)
- [requirements/packages/phoenix-evals.txt](requirements/packages/phoenix-evals.txt)
- [requirements/type-check.txt](requirements/type-check.txt)
- [requirements/unit-tests.txt](requirements/unit-tests.txt)
- [scripts/docker/devops/oidc-server/frontend/package.json](scripts/docker/devops/oidc-server/frontend/package.json)
- [scripts/docker/devops/oidc-server/frontend/src/contexts/ThemeContext.tsx](scripts/docker/devops/oidc-server/frontend/src/contexts/ThemeContext.tsx)
- [scripts/docker/devops/oidc-server/package.json](scripts/docker/devops/oidc-server/package.json)
- [scripts/docker/devops/smtp-server/package.json](scripts/docker/devops/smtp-server/package.json)
- [scripts/update_helm.py](scripts/update_helm.py)
- [scripts/update_kustomize.py](scripts/update_kustomize.py)
- [src/phoenix/__init__.py](src/phoenix/__init__.py)
- [src/phoenix/db/migrations/versions/f1a6b2f0c9d5_add_span_session_id_index.py](src/phoenix/db/migrations/versions/f1a6b2f0c9d5_add_span_session_id_index.py)
- [src/phoenix/server/cli/commands/serve.py](src/phoenix/server/cli/commands/serve.py)
- [src/phoenix/tests/test_config.py](src/phoenix/tests/test_config.py)
- [src/phoenix/version.py](src/phoenix/version.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/unit/conftest.py](tests/unit/conftest.py)
- [tox.ini](tox.ini)
- [uv.lock](uv.lock)

</details>



This document describes Phoenix's automated release process for Python packages, Docker images, and TypeScript packages. The release system uses `release-please` for version management and GitHub Actions for automated publishing.

For information about CI/CD testing and validation before releases, see [CI/CD Pipeline](#6.3). For Helm chart updates, see [Kubernetes Deployment](#6.5).

---

## Overview

Phoenix employs a fully automated release process with separate versioning for each package in the monorepo. The system supports:

- **Python packages**: Main `arize-phoenix` package plus three sub-packages (`arize-phoenix-client`, `arize-phoenix-evals`, `arize-phoenix-otel`).
- **Docker images**: Three release channels (latest, nightly, experimental) with multiple variants (root, nonroot, debug).
- **TypeScript packages**: Separate release flow for the JavaScript monorepo components.
- **Helm charts**: Automatic version bumping synchronized with Docker releases.

**Key Technologies**:
- [release-please](https://github.com/googleapis/release-please) for Python package versioning and changelog generation.
- [hatchling](https://hatch.pypa.io/latest/) as the build backend for Python packages. [packages/phoenix-evals/pyproject.toml:70-70](), [packages/phoenix-client/pyproject.toml:42-42]()
- [uv](https://github.com/astral-sh/uv) for dependency management and CI execution. [pyproject.toml:81-82](), [tox.ini:9-9]()
- GitHub Actions for automation.

Sources: [.release-please-manifest.json:1-1](), [release-please-config.json:1-37](), [pyproject.toml:1-4]()

---

## Python Package Releases

### Release-Please Configuration

Phoenix uses `release-please` in `separate-pull-requests` mode, meaning each package in the monorepo triggers its own release PR. This allows independent versioning of the main package and its specialized sub-packages.

```mermaid
graph TD
    subgraph "Version Tracking"
        Manifest[".release-please-manifest.json<br/>{'.': '17.2.0',<br/>'packages/phoenix-evals': '3.1.0',<br/>...}"]
        Config["release-please-config.json<br/>separate-pull-requests: true"]
        VersionFile["src/phoenix/version.py<br/>__version__ = '17.2.0'"]
    end
    
    subgraph "Release PR Creation"
        MainCommits["Commits to main branch<br/>(conventional commits)"]
        ReleaseAction["release-please GitHub Action<br/>googleapis/release-please-action@v4"]
        ReleasePRs["Separate Pull Requests<br/>- arize-phoenix PR<br/>- arize-phoenix-client PR<br/>- arize-phoenix-evals PR<br/>- arize-phoenix-otel PR"]
    end
    
    subgraph "Automated Updates"
        Changelog["CHANGELOG.md updates<br/>(version, features, fixes)"]
        VersionBump["Version file updates<br/>src/phoenix/version.py"]
        PRContent["PR title:<br/>'chore: release X.Y.Z'"]
    end
    
    MainCommits --> ReleaseAction
    Manifest --> ReleaseAction
    Config --> ReleaseAction
    ReleaseAction --> ReleasePRs
    ReleasePRs --> Changelog
    ReleasePRs --> VersionBump
    ReleasePRs --> PRContent
    
    VersionFile -.->|"Read by"| ReleaseAction
```
Title: Release-Please Workflow for Python Packages

**Configuration Mapping**:

| Package Path | Package Name | Release Type | Version Location |
|--------------|--------------|--------------|------------------|
| `.` | `arize-phoenix` | `python` | `src/phoenix/version.py` |
| `packages/phoenix-client` | `arize-phoenix-client` | `python` | `packages/phoenix-client/pyproject.toml` |
| `packages/phoenix-evals` | `arize-phoenix-evals` | `python` | `packages/phoenix-evals/pyproject.toml` |
| `packages/phoenix-otel` | `arize-phoenix-otel` | `python` | `packages/phoenix-otel/pyproject.toml` |

Sources: [release-please-config.json:1-37](), [.release-please-manifest.json:1-1](), [src/phoenix/version.py:1-1](), [packages/phoenix-evals/pyproject.toml:24-24](), [packages/phoenix-client/pyproject.toml:24-24]()

---

### Release Workflow

The workflow is driven by **Conventional Commits**. When a PR is merged to `main`, `release-please` analyzes the commit messages to determine the next version.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Main as main branch
    participant RP as release-please bot
    participant PR as Release PR
    participant Merge as PR Merge
    participant PyPI as PyPI Registry
    participant Docker as Docker Hub
    
    Dev->>Main: Push commit with conventional prefix
    Main->>RP: Trigger release-please workflow
    RP->>PR: Create/Update release PR (version bump + changelog)
    
    Note over PR: PR remains open accumulating changes
    
    Dev->>PR: Review and merge
    PR->>Merge: Merge triggers release
    
    alt Phoenix Package (.)
        Merge->>PyPI: Build with hatch (frontend + backend)
        Merge->>PyPI: Publish via Trusted Publishing
        Merge->>Docker: Trigger docker-build-release
    else Sub-Package (packages/*)
        Merge->>PyPI: Build with hatch
        Merge->>PyPI: Publish to PyPI
    end
```
Title: Python Package Release Workflow

**Version Bump Logic**:
- `feat:` - Minor version bump (e.g., `17.1.0` -> `17.2.0`). [CHANGELOG.md:6-8]()
- `fix:` - Patch version bump (e.g., `17.1.0` -> `17.1.1`). [CHANGELOG.md:11-14]()
- `BREAKING CHANGE:` or `⚠` in commit body - Major version bump (e.g., `16.6.0` -> `17.0.0`). [CHANGELOG.md:39-41]()

Sources: [CHANGELOG.md:1-47](), [MIGRATION.md:1-9]()

---

### Publishing Process

#### Main Phoenix Package (`arize-phoenix`)

The main package is unique because it bundles the compiled React frontend assets.

1. **Dynamic Versioning**: The version is managed in `src/phoenix/version.py`. [src/phoenix/version.py:1-1]()
2. **Build Execution**: The build uses `hatchling`. During the build, the frontend is compiled via Vite and the assets are injected into the Python package structure. [pyproject.toml:234-235]()
3. **Distribution**: Packages are published to PyPI using GitHub's Trusted Publishing (OIDC).
4. **Validation**: CI runs `check-wheel-contents` and `twine check` to ensure package integrity. [pyproject.toml:83-84]()

Sources: [pyproject.toml:1-84](), [src/phoenix/version.py:1-1](), [.github/workflows/publish.yaml:1-50]()

#### Sub-Packages

Sub-packages are specialized libraries that can be installed independently of the full Phoenix server.

- **arize-phoenix-client**: The programmatic interface for REST/GraphQL interactions. [packages/phoenix-client/pyproject.toml:1-33]()
- **arize-phoenix-evals**: The evaluation framework containing LLM-based and code-based evaluators. [packages/phoenix-evals/pyproject.toml:1-35]()
- **arize-phoenix-otel**: OpenTelemetry configuration and registration helpers. [packages/phoenix-otel/pyproject.toml:1-25]()

Sources: [packages/phoenix-client/pyproject.toml:1-33](), [packages/phoenix-evals/pyproject.toml:1-35](), [packages/phoenix-otel/pyproject.toml:1-25]()

---

## Docker Image Releases

Phoenix maintains several Docker release channels to support different stability requirements.

### Release Channels

| Channel | Trigger | Tags |
|---------|---------|------|
| **Release** | Release PR merge (Git tag) | `latest`, `version-X.Y.Z`, `X.Y.Z` |
| **Nightly** | Scheduled / Push to `main` | `nightly`, `commit-<sha>` |
| **Experimental** | Push to feature branches | `dangerously-experimental` |

**Image Variants**:
- **Standard**: The default image.
- **Nonroot**: Hardened image running as a non-privileged user for production security.
- **Debug**: Includes additional troubleshooting tools and a shell.

Sources: [.github/workflows/docker-build-release.yml:1-30](), [.github/workflows/docker-build-nightly.yml:1-20](), [Dockerfile:1-50]()

---

## Versioning Strategy

Phoenix uses a "Loose Monorepo" versioning strategy. While all code resides in one repository, packages have independent version numbers tracked in `.release-please-manifest.json`.

```mermaid
graph LR
    subgraph "Natural Language Space"
        Commit["Commit Message:<br/>'feat(pxi): add route info tool'"]
        PR["GitHub PR #13591"]
    end
    
    subgraph "Code Entity Space"
        Changelog["CHANGELOG.md<br/>### Features<br/>* add PXI route info tool (#13591)"]
        Manifest[".release-please-manifest.json<br/>'.': '17.2.0'"]
        VersionFile["src/phoenix/version.py<br/>__version__ = '17.2.0'"]
    end
    
    Commit --> Changelog
    PR --> Changelog
    Changelog --> Manifest
    Manifest --> VersionFile
```
Title: Association between Commit Messages and Version State

### Current Manifest State (v17.2.0)

| Package | Current Version |
|---------|-----------------|
| `arize-phoenix` (Root) | `17.2.0` |
| `arize-phoenix-evals` | `3.1.0` |
| `arize-phoenix-client` | `2.7.0` |
| `arize-phoenix-otel` | `0.16.1` |

Sources: [.release-please-manifest.json:1-1](), [CHANGELOG.md:1-21](), [packages/phoenix-evals/CHANGELOG.md:1-10](), [packages/phoenix-client/CHANGELOG.md:1-10]()

---

## Migration Documentation

When major versions or significant breaking changes are introduced, the `MIGRATION.md` file is updated to provide transition paths.

**Recent Breaking Changes (v17.0.0)**:
- **Server**: Introduction of system settings for admin-managed assistant enablement and trace recording policies. [CHANGELOG.md:39-45]()
- **Evals**: Removal of legacy `evals 1.0` and the legacy experiments module. [packages/phoenix-evals/CHANGELOG.md:24-30]()

Sources: [MIGRATION.md:1-41](), [CHANGELOG.md:36-46](), [packages/phoenix-evals/CHANGELOG.md:21-31]()

---

# Page: Kubernetes Deployment

# Kubernetes Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/workflows/cost-sync.yml](.github/workflows/cost-sync.yml)
- [.github/workflows/docker-build-experimental.yml](.github/workflows/docker-build-experimental.yml)
- [.github/workflows/docker-build-nightly.yml](.github/workflows/docker-build-nightly.yml)
- [.github/workflows/docker-build-release.yml](.github/workflows/docker-build-release.yml)
- [.github/workflows/helm-ci.yml](.github/workflows/helm-ci.yml)
- [.github/workflows/helm-release.yaml](.github/workflows/helm-release.yaml)
- [.github/workflows/playwright.yaml](.github/workflows/playwright.yaml)
- [.github/workflows/publish.yaml](.github/workflows/publish.yaml)
- [.github/workflows/pull-requests.yaml](.github/workflows/pull-requests.yaml)
- [.github/workflows/python-CI.yml](.github/workflows/python-CI.yml)
- [.github/workflows/python-all-platforms.yml](.github/workflows/python-all-platforms.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.github/workflows/sync-lockfile-release-pr.yml](.github/workflows/sync-lockfile-release-pr.yml)
- [.github/workflows/typescript-CI.yml](.github/workflows/typescript-CI.yml)
- [.github/workflows/typescript-packages-CI.yml](.github/workflows/typescript-packages-CI.yml)
- [.github/workflows/typescript-packages-publish.yml](.github/workflows/typescript-packages-publish.yml)
- [.github/workflows/update-phoenix-package-versions.yml](.github/workflows/update-phoenix-package-versions.yml)
- [Dockerfile](Dockerfile)
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
- [requirements/canary/sdk/anthropic.txt](requirements/canary/sdk/anthropic.txt)
- [requirements/ci.txt](requirements/ci.txt)
- [scripts/ci/test_helm.py](scripts/ci/test_helm.py)
- [scripts/update_helm.py](scripts/update_helm.py)
- [scripts/update_kustomize.py](scripts/update_kustomize.py)
- [tox.ini](tox.ini)

</details>



This document describes how to deploy Phoenix on Kubernetes using either Helm charts or Kustomize manifests. It covers deployment architecture, database persistence strategies, configuration management, networking, authentication setup, and operational considerations.

For Phoenix server configuration options, see [Application Server & Configuration](#2.1)(). For authentication concepts and user management, see [Authentication & Authorization](#2.6)().

---

## Deployment Methods

Phoenix provides two Kubernetes deployment methods with different complexity levels:

| Method | Path | Use Case | Production Ready |
|--------|------|----------|------------------|
| **Helm Chart** | `helm/` | Production deployments with complex configuration | Yes |
| **Kustomize** | `kustomize/` | Simple deployments, development, base manifests | Basic |

The **Helm chart** (version 9.0.1) is the recommended production deployment method, providing:
- Parameterized configuration via `values.yaml` [helm/values.yaml:1-213]()
- Built-in PostgreSQL dependency (groundhog2k/postgres chart v1.5.8) [helm/Chart.yaml:25-30]()
- Validation logic to prevent configuration conflicts [helm/templates/_helpers.tpl:80-173]()
- Support for external databases, ingress, TLS, and complex authentication (OAuth2/LDAP) [helm/values.yaml:40-130]()

The **Kustomize** manifests provide basic definitions for Phoenix and PostgreSQL, suitable for development or as a starting point for custom deployments [kustomize/base/kustomization.yaml:1-4]().

**Sources:** [helm/Chart.yaml:1-57](), [helm/values.yaml:1-213](), [kustomize/base/phoenix.yaml:1-42]()

---

## Helm Chart Architecture

### Chart Structure

```mermaid
graph TB
    subgraph "Helm Chart phoenix-helm v9.0.1"
        Chart["Chart.yaml<br/>App version: 17.2.0"]
        Values["values.yaml<br/>Configuration parameters"]
        
        subgraph "Templates"
            Deployment["deployment.yaml<br/>Phoenix Deployment"]
            ConfigMap["configmap.yaml<br/>Environment variables"]
            Secret["secret.yaml<br/>Credentials"]
            Service["service.yaml<br/>ClusterIP/NodePort"]
            Ingress["ingress.yaml<br/>External access"]
            PVC["pvc.yaml<br/>Persistent storage"]
            ServiceAccount["serviceaccount.yaml<br/>Pod identity"]
            Helpers["_helpers.tpl<br/>Validation functions"]
        end
        
        subgraph "Dependencies"
            PostgresChart["groundhog2k/postgres:1.5.8<br/>Built-in PostgreSQL"]
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

**Sources:** [helm/Chart.yaml:1-57](), [helm/templates/phoenix/deployment.yaml:1-179](), [helm/templates/_helpers.tpl:1-173]()

### Resource Provisioning Flow

```mermaid
graph LR
    Install["helm install phoenix<br/>arize-ai/phoenix-helm"]
    
    Install --> Validate["phoenix.validatePersistence<br/>phoenix.validateExternalDatabase<br/>phoenix.validateDatabaseUrl<br/>phoenix.validateLdapNoEmail"]
    
    Validate --> CreateResources["Create Resources"]
    
    CreateResources --> CM["ConfigMap<br/>phoenix-configmap<br/>PHOENIX_* env vars"]
    CreateResources --> Sec["Secret<br/>phoenix-secret<br/>Credentials"]
    CreateResources --> PV["PersistentVolumeClaim<br/>phoenix-data-pvc<br/>Strategy 1: SQLite"]
    CreateResources --> PG["PostgreSQL StatefulSet<br/>phoenix-postgresql<br/>Strategy 2: Built-in PG"]
    CreateResources --> Deploy["Deployment<br/>phoenix<br/>arizephoenix/phoenix:version-17.2.0"]
    CreateResources --> Svc["Service<br/>phoenix-svc<br/>Ports: 6006, 4317, 9090"]
    CreateResources --> Ing["Ingress<br/>phoenix-ingress<br/>Optional"]
    
    Deploy --> CM
    Deploy --> Sec
    Deploy --> PV
    Deploy -.env PHOENIX_POSTGRES_HOST.-> PG
    Svc --> Deploy
    Ing --> Svc
```

The Helm chart includes validation functions in `_helpers.tpl` that prevent invalid configurations at deployment time:
- `phoenix.validatePersistence`: Ensures only one persistence strategy (SQLite vs PostgreSQL) is enabled [helm/templates/_helpers.tpl:80-100]().
- `phoenix.validateExternalDatabase`: Validates external database settings consistency [helm/templates/_helpers.tpl:105-123]().
- `phoenix.validateDatabaseUrl`: Validates database URL format [helm/templates/_helpers.tpl:125-128]().
- `phoenix.validateLdapNoEmail`: Validates LDAP no-email mode requirements [helm/templates/_helpers.tpl:130-151]().

**Sources:** [helm/templates/_helpers.tpl:80-173](), [helm/templates/phoenix/deployment.yaml:1-179](), [helm/templates/NOTES.txt:1-60]()

---

## Database Persistence Strategies

Phoenix supports four mutually exclusive database strategies, validated at deployment time:

### Strategy Comparison

| Strategy | persistence.enabled | postgresql.enabled | database.url | Use Case |
|----------|--------------------|--------------------|--------------|----------|
| **1. SQLite Persistent** | `true` | `false` | empty | Development, single-node |
| **2. Built-in PostgreSQL** | `false` | `true` | empty | Production, managed state |
| **3. External Database** | `false` | `false` | configured | Production, RDS/CloudSQL |
| **4. SQLite In-Memory** | `false` | `false` | `sqlite:///:memory:` | Testing only (data lost) |

### Strategy 1: SQLite with Persistent Storage

```yaml
# helm/values.yaml configuration
persistence:
  enabled: true
  
postgresql:
  enabled: false
  
server:
  workingDir: "/data"
```

- Phoenix automatically creates SQLite database at `${PHOENIX_WORKING_DIR}/phoenix.db`.
- PersistentVolumeClaim `phoenix-data-pvc` is mounted at `/data` [helm/templates/phoenix/deployment.yaml:130-131]().
- Security context `fsGroup: 65532` ensures proper permissions for the non-root container [helm/values.yaml:159-161]().

**Sources:** [helm/values.yaml:204-213](), [helm/templates/phoenix/pvc.yaml:1-34]()

### Strategy 2: Built-in PostgreSQL (groundhog2k)

```yaml
# helm/values.yaml configuration
persistence:
  enabled: false
  
postgresql:
  enabled: true
  image:
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

- Deploys `groundhog2k/postgres:1.5.8` chart as dependency [helm/Chart.yaml:25-30]().
- StatefulSet with PersistentVolumeClaim for PostgreSQL data [helm/values.yaml:111-116]().
- Phoenix automatically connects to `phoenix-postgresql:5432` [helm/templates/_helpers.tpl:21-27]().

**Sources:** [helm/Chart.yaml:25-30](), [helm/values.yaml:67-130](), [helm/templates/_helpers.tpl:21-27]()

### Strategy 3: External Database

```yaml
# helm/values.yaml
database:
  url: "postgresql://user:pass@rds.example.com:5432/phoenix"
  
persistence:
  enabled: false
postgresql:
  enabled: false
```

- For AWS RDS, Google CloudSQL, Azure Database, etc.
- `database.url` overrides individual host/port settings [helm/templates/phoenix/configmap.yaml:134-135]().
- Connection string is injected via `PHOENIX_SQL_DATABASE_URL` [kustomize/base/phoenix.yaml:31-32]().

**Sources:** [helm/values.yaml:204-213](), [helm/templates/phoenix/configmap.yaml:134-147](), [kustomize/base/phoenix.yaml:31-32]()

---

## Configuration Management

### ConfigMap: Environment Variables

The `phoenix-configmap` provides non-sensitive configuration via environment variables [helm/templates/phoenix/configmap.yaml:1-179]().

| Section | Environment Variables | Values Path |
|---------|----------------------|-------------|
| Server | `PHOENIX_HOST`, `PHOENIX_PORT`, `PHOENIX_GRPC_PORT`, `PHOENIX_WORKING_DIR` | `server.*` |
| Authentication | `PHOENIX_ENABLE_AUTH`, `PHOENIX_ALLOWED_ORIGINS` | `auth.*` |
| Database | `PHOENIX_POSTGRES_HOST`, `PHOENIX_POSTGRES_PORT`, `PHOENIX_POSTGRES_DB` | `database.postgres.*` |
| LDAP | `PHOENIX_LDAP_HOST`, `PHOENIX_LDAP_USER_SEARCH_BASE_DNS`, `PHOENIX_LDAP_BIND_DN` | `auth.ldap.*` |

**Sources:** [helm/templates/phoenix/configmap.yaml:13-131](), [helm/templates/phoenix/deployment.yaml:77-80]()

### Secret: Credentials

The `phoenix-secret` stores sensitive credentials, auto-generated if empty [helm/templates/phoenix/secret.yaml:1-34]().

```yaml
# helm/templates/phoenix/secret.yaml
data:
  PHOENIX_SECRET: {{ $authSecrets.value | default (randAlphaNum 32) | b64enc }}
  PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD: {{ .Values.auth.defaultAdminPassword | b64enc }}
  PHOENIX_LDAP_BIND_PASSWORD: {{ .Values.auth.ldap.bindPassword | b64enc }}
```

**Sources:** [helm/templates/phoenix/secret.yaml:1-34](), [helm/templates/phoenix/deployment.yaml:80-117](), [helm/values.yaml:45-56]()

---

## Networking and Ingress

### Service Configuration

Phoenix Service exposes three ports by default:

| Port | Name | Protocol | Purpose | Env Var |
|------|------|----------|---------|---------|
| 6006 | `phoenix-app` | HTTP | UI and OTLP HTTP traces | `PHOENIX_PORT` |
| 4317 | `phoenix-grpc` | gRPC | OTLP gRPC collector | `PHOENIX_GRPC_PORT` |
| 9090 | `phoenix-metrics` | HTTP | Prometheus metrics | `PHOENIX_ENABLE_PROMETHEUS` |

**Sources:** [helm/templates/phoenix/service.yaml:1-36](), [helm/values.yaml:135-151](), [kustomize/base/phoenix.yaml:35-38]()

### Ingress Configuration

For external HTTPS access, configure Ingress [helm/templates/phoenix/ingress.yaml:1-42]():

```yaml
# helm/values.yaml
ingress:
  enabled: true
  host: "phoenix.example.com"
  tls:
    enabled: true
```

**Sources:** [helm/templates/phoenix/ingress.yaml:1-42](), [helm/values.yaml:40-62]()

---

## Authentication Configuration

Phoenix supports complex authentication flows including Local, OAuth2, and LDAP.

### Local Authentication
Enabled via `PHOENIX_ENABLE_AUTH`. Requires a `PHOENIX_SECRET` for JWT signing.
- **Initial Admin**: Default password set via `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` [helm/values.yaml:45]().
- **Password Policy**: Strong policy (12+ chars, mixed case, special) enabled via `auth.enableStrongPasswordPolicy` [helm/values.yaml:49]().

### LDAP / Active Directory
Configured via `auth.ldap.*` in `values.yaml` [helm/values.yaml:50-62]().
- **No-Email Mode**: Set `attrEmail: "null"` and `attrUniqueId` (e.g., `objectGUID`) for environments without email attributes [helm/values.yaml:52-54]().
- **Group Mappings**: Map LDAP groups to Phoenix roles (ADMIN, MEMBER, VIEWER) using `groupRoleMappings` [helm/values.yaml:58]().

**Sources:** [helm/templates/phoenix/configmap.yaml:76-116](), [helm/values.yaml:38-62]()

---

## Health Checks and Probes

The deployment defines three health probes to manage the container lifecycle:

| Probe | Endpoint | Purpose |
|-------|----------|---------|
| **Liveness** | `/healthz` | Restarts the container if the Python server hangs [helm/templates/phoenix/deployment.yaml:48-56](). |
| **Readiness** | `/readyz` | Ensures the app is serving traffic before becoming ready in K8s [helm/templates/phoenix/deployment.yaml:57-65](). |
| **Startup** | `/healthz` | Gives the app up to 30s to initialize (useful for migrations) [helm/templates/phoenix/deployment.yaml:67-76](). |

**Sources:** [helm/templates/phoenix/deployment.yaml:48-76](), [kustomize/base/phoenix.yaml:39-41]()

---

## Operational Considerations

### Memory Management
The Phoenix server uses an in-memory processing queue for spans. Memory usage is approximately 50KiB per span. The default queue size of 20,000 spans requires ~1GiB of memory [helm/values.yaml:171-174]().
- Adjust `PHOENIX_MAX_SPANS_QUEUE_SIZE` based on available memory [helm/values.yaml:174]().

### Air-Gapped Environments
In air-gapped clusters, set `PHOENIX_ALLOW_EXTERNAL_RESOURCES` to `false` to prevent the UI from attempting to load Google Fonts [helm/values.yaml:163-165]().

### Non-Root Execution
The `arizephoenix/phoenix:version-17.2.0-nonroot` image is available for restricted environments [Dockerfile:22](). Ensure `PHOENIX_WORKING_DIR` (default `/data`) is writable by UID 65532 [helm/values.yaml:159-161]().

**Sources:** [Dockerfile:22-127](), [helm/values.yaml:156-174]()

---

# Page: API Reference Documentation

# API Reference Documentation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/generate-sitemap.yml](.github/workflows/generate-sitemap.yml)
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
- [docs/phoenix.mdx](docs/phoenix.mdx)
- [docs/phoenix/cookbook/agent-workflow-patterns/autogen.mdx](docs/phoenix/cookbook/agent-workflow-patterns/autogen.mdx)
- [docs/phoenix/cookbook/prompt-engineering/prompt-learning-optimizing-prompts-for-classification.mdx](docs/phoenix/cookbook/prompt-engineering/prompt-learning-optimizing-prompts-for-classification.mdx)
- [docs/phoenix/datasets-and-experiments/how-to-experiments.mdx](docs/phoenix/datasets-and-experiments/how-to-experiments.mdx)
- [docs/phoenix/datasets-and-experiments/how-to-experiments/how-to-dataset-evaluators.mdx](docs/phoenix/datasets-and-experiments/how-to-experiments/how-to-dataset-evaluators.mdx)
- [docs/phoenix/datasets-and-experiments/how-to-experiments/run-experiments-in-background.mdx](docs/phoenix/datasets-and-experiments/how-to-experiments/run-experiments-in-background.mdx)
- [docs/phoenix/evaluation/how-to-evals/code-evaluators.mdx](docs/phoenix/evaluation/how-to-evals/code-evaluators.mdx)
- [docs/phoenix/evaluation/llm-evals/evaluator-traces.mdx](docs/phoenix/evaluation/llm-evals/evaluator-traces.mdx)
- [docs/phoenix/evaluation/pre-built-metrics.mdx](docs/phoenix/evaluation/pre-built-metrics.mdx)
- [docs/phoenix/evaluation/pre-built-metrics/tool-response-handling.mdx](docs/phoenix/evaluation/pre-built-metrics/tool-response-handling.mdx)
- [docs/phoenix/evaluation/server-evals/builtin-evaluators.mdx](docs/phoenix/evaluation/server-evals/builtin-evaluators.mdx)
- [docs/phoenix/evaluation/server-evals/input-mapping.mdx](docs/phoenix/evaluation/server-evals/input-mapping.mdx)
- [docs/phoenix/evaluation/server-evals/llm-evaluators.mdx](docs/phoenix/evaluation/server-evals/llm-evaluators.mdx)
- [docs/phoenix/evaluation/server-evals/overview.mdx](docs/phoenix/evaluation/server-evals/overview.mdx)
- [docs/phoenix/prompt-engineering/concepts-prompts/prompts-concepts.mdx](docs/phoenix/prompt-engineering/concepts-prompts/prompts-concepts.mdx)
- [docs/phoenix/prompt-engineering/how-to-prompts/configure-ai-providers.mdx](docs/phoenix/prompt-engineering/how-to-prompts/configure-ai-providers.mdx)
- [docs/phoenix/prompt-engineering/how-to-prompts/using-the-playground.mdx](docs/phoenix/prompt-engineering/how-to-prompts/using-the-playground.mdx)
- [docs/phoenix/pxi.mdx](docs/phoenix/pxi.mdx)
- [docs/phoenix/release-notes.mdx](docs/phoenix/release-notes.mdx)
- [docs/phoenix/release-notes/01-2026/01-05-2026-appended-messages-for-playground-experiments.mdx](docs/phoenix/release-notes/01-2026/01-05-2026-appended-messages-for-playground-experiments.mdx)
- [docs/phoenix/release-notes/02-2026/02-11-2026-custom-providers.mdx](docs/phoenix/release-notes/02-2026/02-11-2026-custom-providers.mdx)
- [docs/phoenix/release-notes/02-2026/02-12-2026-dataset-evaluators.mdx](docs/phoenix/release-notes/02-2026/02-12-2026-dataset-evaluators.mdx)
- [docs/phoenix/release-notes/02-2026/02-12-2026-openai-responses-api-support.mdx](docs/phoenix/release-notes/02-2026/02-12-2026-openai-responses-api-support.mdx)
- [docs/phoenix/release-notes/03-2026/03-11-2026-session-turns-api.mdx](docs/phoenix/release-notes/03-2026/03-11-2026-session-turns-api.mdx)
- [docs/phoenix/release-notes/04-2026/04-03-2026-atif-trajectory-upload.mdx](docs/phoenix/release-notes/04-2026/04-03-2026-atif-trajectory-upload.mdx)
- [docs/phoenix/release-notes/04-2026/04-07-2026-phoenix-v14-breaking-changes.mdx](docs/phoenix/release-notes/04-2026/04-07-2026-phoenix-v14-breaking-changes.mdx)
- [docs/phoenix/release-notes/04-2026/04-07-2026-postgresql-read-replica.mdx](docs/phoenix/release-notes/04-2026/04-07-2026-postgresql-read-replica.mdx)
- [docs/phoenix/release-notes/04-2026/04-16-2026-azure-managed-identity-postgres.mdx](docs/phoenix/release-notes/04-2026/04-16-2026-azure-managed-identity-postgres.mdx)
- [docs/phoenix/release-notes/04-2026/04-20-2026-span-attribute-filter-cli-notes-and-opus-4-7.mdx](docs/phoenix/release-notes/04-2026/04-20-2026-span-attribute-filter-cli-notes-and-opus-4-7.mdx)
- [docs/phoenix/release-notes/04-2026/04-22-2026-secrets-ui-and-evaluator-trace-id.mdx](docs/phoenix/release-notes/04-2026/04-22-2026-secrets-ui-and-evaluator-trace-id.mdx)
- [docs/phoenix/release-notes/04-2026/04-24-2026-trace-notes-api.mdx](docs/phoenix/release-notes/04-2026/04-24-2026-trace-notes-api.mdx)
- [docs/phoenix/release-notes/05-2026/05-21-2026-code-evaluators.mdx](docs/phoenix/release-notes/05-2026/05-21-2026-code-evaluators.mdx)
- [docs/phoenix/release-notes/05-2026/05-27-2026-drag-to-zoom.mdx](docs/phoenix/release-notes/05-2026/05-27-2026-drag-to-zoom.mdx)
- [docs/phoenix/release-notes/06-2026/06-02-2026-pxi-agent.mdx](docs/phoenix/release-notes/06-2026/06-02-2026-pxi-agent.mdx)
- [docs/phoenix/release-notes/2026.mdx](docs/phoenix/release-notes/2026.mdx)
- [docs/phoenix/resources/python-api.mdx](docs/phoenix/resources/python-api.mdx)
- [docs/phoenix/resources/typescript-api.mdx](docs/phoenix/resources/typescript-api.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/span-annotations.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/span-annotations.mdx)
- [docs/phoenix/settings/custom-ai-providers.mdx](docs/phoenix/settings/custom-ai-providers.mdx)
- [docs/phoenix/sitemap.xml](docs/phoenix/sitemap.xml)
- [packages/phoenix-client/examples/annotations/add_span_note_example.py](packages/phoenix-client/examples/annotations/add_span_note_example.py)
- [scripts/generate_sitemap.py](scripts/generate_sitemap.py)
- [sitemap.xml](sitemap.xml)
- [src/phoenix/server/api/helpers/annotations.py](src/phoenix/server/api/helpers/annotations.py)

</details>



This page details the generation, hosting, and maintenance of the Phoenix Python API reference documentation. The documentation is built using Sphinx, hosted on ReadTheDocs, and automatically generated from Python docstrings using `sphinx.ext.autodoc` and `sphinx.ext.autosummary`.

## Purpose and Scope

The Python API reference provides comprehensive documentation for the `arize-phoenix` Python packages, including `arize-phoenix-client`, `arize-phoenix-otel`, and `arize-phoenix-evals`. It serves as a detailed guide for developers integrating with Phoenix programmatically, offering insights into classes, functions, and modules. This reference complements the broader Phoenix documentation available on the Arize website, which includes tutorials, quickstarts, and conceptual explanations [api_reference/source/index.md:10-12]().

The API reference is specifically for the Python client libraries and does not cover the REST API or GraphQL API, which are documented separately via OpenAPI and GraphQL schemas.

## Sphinx-based Python API Reference

The Phoenix Python API reference is generated using Sphinx, a documentation generator that converts reStructuredText (or MyST Markdown) into various output formats, primarily HTML.

### Configuration

The core configuration for the Sphinx build process is located in `api_reference/source/conf.py`. This file defines:

*   **Project Information**: `project`, `copyright`, and `author` [api_reference/source/conf.py:73-75]().
*   **Extensions**: Key Sphinx extensions used include:
    *   `sphinx.ext.autodoc`: Automatically extracts documentation from Python docstrings [api_reference/source/conf.py:82]().
    *   `sphinx.ext.autosummary`: Generates summary tables for modules, classes, and functions [api_reference/source/conf.py:83]().
    *   `sphinx.ext.napoleon`: Enables Sphinx to understand Google and NumPy style docstrings [api_reference/source/conf.py:84]().
    *   `myst_parser`: Allows writing documentation in MyST Markdown [api_reference/source/conf.py:85]().
    *   `sphinx_design`: Provides design components for Sphinx documentation [api_reference/source/conf.py:86]().
*   **Path Setup**: The `sys.path` is modified to include the source directories of the `phoenix`, `phoenix-client`, `phoenix-evals`, and `phoenix-otel` packages, allowing `autodoc` to find the Python modules [api_reference/source/conf.py:17-21]().
*   **Autodoc Options**: Specific options are set for `autodoc` to control how documentation is extracted and formatted, such as `members=True` to document all public members and `autodoc_typehints="none"` to suppress type hints in the generated documentation [api_reference/source/conf.py:117-130]().
*   **HTML Theme**: The `pydata_sphinx_theme` is used for the HTML output, providing a modern and responsive design [api_reference/source/conf.py:157]().
*   **Custom CSS/JS**: Custom CSS (`custom.css`) and JavaScript (`custom.js`) files are included for additional styling and functionality [api_reference/source/conf.py:66-67, 159-160]().

### Autodoc-based Reference Pages

The API reference pages are primarily generated using `sphinx.ext.autodoc` and `sphinx.ext.autosummary`. These extensions scan the Python source code, extract docstrings, and automatically create reStructuredText files that Sphinx then renders into HTML.

The `clean_doc_output` function [api_reference/source/conf.py:27-63]() is a custom Sphinx event handler that processes the generated `.rst` sources. Its purpose is to:
*   Remove unwanted text outside `automodule` blocks.
*   Adjust formatting, such as removing "Submodules", "package", and "module" labels that `autodoc` might generate but are not desired in the final output [api_reference/source/conf.py:51-59]().

This ensures a cleaner and more focused API reference.

#### Python Path Configuration for Autodoc

For `autodoc` to correctly discover and document the Python modules, the `sys.path` in `api_reference/source/conf.py` is explicitly extended to include the root directories of the Python packages:

```python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "src", "phoenix"))
sys.path.insert(0, os.path.join(BASE_DIR, "packages", "phoenix-client", "src", "phoenix"))
sys.path.insert(0, os.path.join(BASE_DIR, "packages", "phoenix-evals", "src", "phoenix"))
sys.path.insert(0, os.path.join(BASE_DIR, "packages", "phoenix-otel", "src", "phoenix"))
```
Sources: [api_reference/source/conf.py:17-21]()

### Diagram: Sphinx Documentation Generation Workflow

This diagram maps the natural language concept of "Documentation Generation" to the specific code entities and directories involved in the Sphinx build.

```mermaid
graph TD
    "Python_Source_Code"["Python Source Code"] --> "Docstrings"["Docstrings"]
    "Docstrings" --> "conf.py"["api_reference/source/conf.py"]
    "conf.py" --> "Sphinx_Build"["Sphinx Build Process"]
    
    subgraph "Python_Packages"["Python Packages"]
        "phoenix"["src/phoenix"]
        "phoenix-client"["packages/phoenix-client/src/phoenix"]
        "phoenix-evals"["packages/phoenix-evals/src/phoenix"]
        "phoenix-otel"["packages/phoenix-otel/src/phoenix"]
    end

    "phoenix" --> "Docstrings"
    "phoenix-client" --> "Docstrings"
    "phoenix-evals" --> "Docstrings"
    "phoenix-otel" --> "Docstrings"

    "Sphinx_Build" -- "sphinx.ext.autodoc" --> "RST_Files"["Generated .rst Files"]
    "RST_Files" -- "clean_doc_output()" --> "Clean_RST"["Cleaned .rst Files"]
    "Clean_RST" --> "HTML_Output"["HTML Output"]
    "HTML_Output" --> "RTD"["ReadTheDocs Hosting"]
```
Title: "Sphinx Documentation Generation Workflow"
Sources: [api_reference/source/conf.py:17-21](), [api_reference/source/conf.py:27-63](), [api_reference/source/conf.py:82-86]()

## ReadTheDocs Hosting

The generated Python API reference is hosted on ReadTheDocs. This platform automates the building and hosting of documentation from version control systems.

### ReadTheDocs Configuration

The `.readthedocs.yaml` file configures the ReadTheDocs build environment and process:

*   **Python Version**: Specifies Python 3.12 for the build [.readthedocs.yaml:11]().
*   **Build OS**: Uses `ubuntu-22.04` as the operating system for the build environment [.readthedocs.yaml:9]().
*   **Sphinx Configuration**: Points to `api_reference/source/conf.py` as the main Sphinx configuration file [.readthedocs.yaml:19]().
*   **Python Dependencies**: Installs dependencies listed in `api_reference/requirements.txt` and the Phoenix package itself using `pip install .` [.readthedocs.yaml:34-38]().

Sources: [.readthedocs.yaml:1-38]()

## Versioning Strategy

The API reference documentation on ReadTheDocs supports versioning, allowing users to view documentation for different releases of the Phoenix Python packages.

### Version Matching

The `api_reference/source/conf.py` file includes logic to determine the version displayed in the ReadTheDocs version switcher:

```python
json_url = "https://arize-phoenix.readthedocs.io/en/latest/_static/switcher.json"
version_match = os.environ.get("READTHEDOCS_VERSION")
release = phoenix.__version__

if not version_match or version_match.isdigit() or version_match == "stable":
    version_match = f"v{release}"
```
Sources: [api_reference/source/conf.py:139-153]()

*   `READTHEDOCS_VERSION`: This environment variable is set by ReadTheDocs during the build process [api_reference/source/conf.py:145]().
*   If `READTHEDOCS_VERSION` is not set, is a digit (indicating a pull request build), or is "stable", the `version_match` is set to `v{release}`, where `release` is the version of the `phoenix` package [api_reference/source/conf.py:146-153]().
*   This `version_match` is then used by the `pydata_sphinx_theme`'s version switcher to link to the correct documentation version [api_reference/source/conf.py:196-199]().

## Maintaining and Regenerating Reference Pages

Maintaining the API reference involves updating docstrings in the Python codebase and ensuring the Sphinx build process correctly generates the documentation.

### Updating Docstrings

Developers should follow Google or NumPy style docstring conventions for all public classes, methods, and functions. The `sphinx.ext.napoleon` extension handles parsing these styles [api_reference/source/conf.py:101-103]().

### Sitemap Generation

A sitemap (`sitemap.xml`) is automatically generated to help search engines index the documentation pages. This process is managed by a GitHub Actions workflow (`.github/workflows/generate-sitemap.yml`) and a Python script (`scripts/generate_sitemap.py`).

The `generate_sitemap.py` script:
1.  Reads `docs.json` to extract all page URLs from the navigation and footer sections [scripts/generate_sitemap.py:151-159]().
2.  Parses any existing `sitemap.xml` to preserve `lastmod` timestamps for unchanged URLs [scripts/generate_sitemap.py:65-96, 180-182]().
3.  Generates a new `sitemap.xml` with updated timestamps for new or modified pages [scripts/generate_sitemap.py:99-136]().
4.  Writes the sitemap to both the repository root and `docs/phoenix/` directories [scripts/generate_sitemap.py:188-191]().

### Diagram: Sitemap Generation Workflow

This diagram bridges the high-level CI/CD process with the specific scripts and data files that drive sitemap updates.

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
Title: "Sitemap Generation Workflow"
Sources: [.github/workflows/generate-sitemap.yml:1-43](), [scripts/generate_sitemap.py:17-43](), [scripts/generate_sitemap.py:65-96](), [scripts/generate_sitemap.py:99-136]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pxi-evals.yml](.github/workflows/pxi-evals.yml)
- [README.md](README.md)
- [app/schema.graphql](app/schema.graphql)
- [app/src/components/trace/SpanKindIcon.tsx](app/src/components/trace/SpanKindIcon.tsx)
- [app/src/pages/auth/AuthLayout.tsx](app/src/pages/auth/AuthLayout.tsx)
- [app/src/pages/playground/Playground.tsx](app/src/pages/playground/Playground.tsx)
- [app/src/pages/playground/PlaygroundChatTemplate.tsx](app/src/pages/playground/PlaygroundChatTemplate.tsx)
- [app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx](app/src/pages/playground/PlaygroundDatasetExamplesTable.tsx)
- [app/src/pages/playground/PlaygroundOutput.tsx](app/src/pages/playground/PlaygroundOutput.tsx)
- [app/src/pages/playground/PlaygroundTemplate.tsx](app/src/pages/playground/PlaygroundTemplate.tsx)
- [app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableMutation.graphql.ts](app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableMutation.graphql.ts)
- [app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableSubscription.graphql.ts](app/src/pages/playground/__generated__/PlaygroundDatasetExamplesTableSubscription.graphql.ts)
- [app/src/pages/playground/__generated__/PlaygroundOutputSubscription.graphql.ts](app/src/pages/playground/__generated__/PlaygroundOutputSubscription.graphql.ts)
- [app/src/pages/playground/__tests__/playgroundUtils.test.ts](app/src/pages/playground/__tests__/playgroundUtils.test.ts)
- [app/src/pages/playground/constants.tsx](app/src/pages/playground/constants.tsx)
- [app/src/pages/playground/playgroundUtils.ts](app/src/pages/playground/playgroundUtils.ts)
- [app/src/pages/playground/schemas.ts](app/src/pages/playground/schemas.ts)
- [app/src/store/playground/__tests__/playgroundStore.test.ts](app/src/store/playground/__tests__/playgroundStore.test.ts)
- [app/src/store/playground/playgroundStore.tsx](app/src/store/playground/playgroundStore.tsx)
- [app/src/store/playground/types.ts](app/src/store/playground/types.ts)
- [app/src/window.d.ts](app/src/window.d.ts)
- [cspell.json](cspell.json)
- [docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx](docs/phoenix/integrations/typescript/vercel/vercel-ai-sdk-tracing-js.mdx)
- [docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx](docs/phoenix/sdk-api-reference/typescript/arizeai-phoenix-otel.mdx)
- [docs/phoenix/sdk-api-reference/typescript/overview.mdx](docs/phoenix/sdk-api-reference/typescript/overview.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/manual-spans.mdx)
- [docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx](docs/phoenix/sdk-api-reference/typescript/packages/phoenix-otel/overview.mdx)
- [evals/pxi/README.md](evals/pxi/README.md)
- [evals/pxi/datasets/debug_trace_skill_trigger.yaml](evals/pxi/datasets/debug_trace_skill_trigger.yaml)
- [evals/pxi/datasets/in_app_links.yaml](evals/pxi/datasets/in_app_links.yaml)
- [evals/pxi/datasets/set_spans_filter.yaml](evals/pxi/datasets/set_spans_filter.yaml)
- [evals/pxi/datasets/set_time_range.yaml](evals/pxi/datasets/set_time_range.yaml)
- [evals/pxi/evaluators/__init__.py](evals/pxi/evaluators/__init__.py)
- [evals/pxi/evaluators/tools.py](evals/pxi/evaluators/tools.py)
- [evals/pxi/harness/agent_task.py](evals/pxi/harness/agent_task.py)
- [evals/pxi/harness/run_experiment.py](evals/pxi/harness/run_experiment.py)
- [js/packages/phoenix-client/README.md](js/packages/phoenix-client/README.md)
- [js/packages/phoenix-config/README.md](js/packages/phoenix-config/README.md)
- [js/packages/phoenix-evals/README.md](js/packages/phoenix-evals/README.md)
- [js/packages/phoenix-mcp/README.md](js/packages/phoenix-mcp/README.md)
- [js/packages/phoenix-mcp/src/index.ts](js/packages/phoenix-mcp/src/index.ts)
- [js/packages/phoenix-mcp/src/projectTools.ts](js/packages/phoenix-mcp/src/projectTools.ts)
- [js/packages/phoenix-otel/README.md](js/packages/phoenix-otel/README.md)
- [packages/phoenix-client/README.md](packages/phoenix-client/README.md)
- [packages/phoenix-evals/README.md](packages/phoenix-evals/README.md)
- [packages/phoenix-otel/README.md](packages/phoenix-otel/README.md)
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
- [src/phoenix/server/api/evaluators.py](src/phoenix/server/api/evaluators.py)
- [src/phoenix/server/api/helpers/playground_clients.py](src/phoenix/server/api/helpers/playground_clients.py)
- [src/phoenix/server/api/input_types/SpanSort.py](src/phoenix/server/api/input_types/SpanSort.py)
- [src/phoenix/server/api/mutations/__init__.py](src/phoenix/server/api/mutations/__init__.py)
- [src/phoenix/server/api/mutations/chat_mutations.py](src/phoenix/server/api/mutations/chat_mutations.py)
- [src/phoenix/server/api/queries.py](src/phoenix/server/api/queries.py)
- [src/phoenix/server/api/routers/v1/experiment_evaluations.py](src/phoenix/server/api/routers/v1/experiment_evaluations.py)
- [src/phoenix/server/api/routers/v1/experiment_runs.py](src/phoenix/server/api/routers/v1/experiment_runs.py)
- [src/phoenix/server/api/routers/v1/experiments.py](src/phoenix/server/api/routers/v1/experiments.py)
- [src/phoenix/server/api/schema.py](src/phoenix/server/api/schema.py)
- [src/phoenix/server/api/subscriptions.py](src/phoenix/server/api/subscriptions.py)
- [src/phoenix/server/api/types/Dataset.py](src/phoenix/server/api/types/Dataset.py)
- [src/phoenix/server/api/types/Project.py](src/phoenix/server/api/types/Project.py)
- [src/phoenix/server/api/types/Span.py](src/phoenix/server/api/types/Span.py)
- [src/phoenix/server/api/types/Trace.py](src/phoenix/server/api/types/Trace.py)
- [src/phoenix/server/app.py](src/phoenix/server/app.py)
- [src/phoenix/server/main.py](src/phoenix/server/main.py)
- [src/phoenix/server/templates/index.html](src/phoenix/server/templates/index.html)
- [src/phoenix/server/thread_server.py](src/phoenix/server/thread_server.py)
- [src/phoenix/services.py](src/phoenix/services.py)
- [src/phoenix/session/session.py](src/phoenix/session/session.py)
- [src/phoenix/settings.py](src/phoenix/settings.py)
- [src/phoenix/trace/schemas.py](src/phoenix/trace/schemas.py)
- [src/phoenix/trace/span_json_decoder.py](src/phoenix/trace/span_json_decoder.py)
- [src/phoenix/trace/span_json_encoder.py](src/phoenix/trace/span_json_encoder.py)
- [tests/unit/pxi/evals/test_agent_task_inputs.py](tests/unit/pxi/evals/test_agent_task_inputs.py)
- [tests/unit/pxi/evals/test_datasets.py](tests/unit/pxi/evals/test_datasets.py)
- [tests/unit/pxi/evals/test_evaluator_matchers.py](tests/unit/pxi/evals/test_evaluator_matchers.py)
- [tests/unit/pxi/evals/test_evaluators.py](tests/unit/pxi/evals/test_evaluators.py)
- [tests/unit/server/api/helpers/test_evaluators.py](tests/unit/server/api/helpers/test_evaluators.py)
- [tests/unit/server/api/helpers/test_playground_clients.py](tests/unit/server/api/helpers/test_playground_clients.py)
- [tests/unit/server/api/routers/v1/test_experiments.py](tests/unit/server/api/routers/v1/test_experiments.py)
- [tests/unit/server/api/test_queries.py](tests/unit/server/api/test_queries.py)
- [tests/unit/server/api/test_subscriptions.py](tests/unit/server/api/test_subscriptions.py)
- [tests/unit/server/api/types/test_Trace.py](tests/unit/server/api/types/test_Trace.py)

</details>



This page provides definitions for codebase-specific terms, jargon, abbreviations, and domain concepts used within the Phoenix project. It aims to clarify terminology for new engineers and provide pointers to relevant code for deeper understanding.

## Phoenix Core Concepts

### Phoenix
Phoenix is an open-source AI observability platform designed for experimentation, evaluation, and troubleshooting of LLM applications. It provides features for tracing, evaluation, dataset management, experimentation, prompt management, and a playground interface that supports vendor- and language-agnostic integrations with popular LLMs and tracing libraries. The main Python package is `arize-phoenix`.

- Key features include trace collection with OpenTelemetry, evaluation frameworks, dataset versioning, prompt management, and generative model playground [README.md:44-51]().
- Integrations support OpenAI, Anthropic, Google GenAI, AWS Bedrock, and more, plus SDKs like OpenAI Agents, LangGraph, and Vercel AI SDK [README.md:53-56]().

**Code pointers:**
- Project metadata and dependencies: [pyproject.toml:1-74]()
- Main entry point: `phoenix.server.main:main` [src/phoenix/server/main.py:17-29]()

### Span
A Span represents a single operation or event within a Trace. Spans are core to Phoenix's tracing capabilities and capture discrete LLM interactions like API calls, tool invocations, or retrievals.

- Spans use OpenTelemetry semantic conventions extended for AI-specific operations [src/phoenix/db/models.py:94-103]().
- Each span contains metadata like start/end time, span kind, model name, input prompts, output, and annotations [src/phoenix/server/api/types/Span.py:127-232]().
- Span types (kinds) include `LLM`, `CHAIN`, `TOOL`, `RETRIEVER`, `EMBEDDING`, `RERANKER`, and `AGENT` [src/phoenix/server/api/types/Span.py:57-74]().

**Code pointers:**
- GraphQL `Span` type: [app/schema.graphql:11158-11350]()
- SQLAlchemy Model: `models.Span` [src/phoenix/db/models.py:440-540]() (approximate)

### Trace
A Trace is a group of related Spans forming a causal chain representing an LLM application's complete operation or request.

- Traces enable end-to-end visibility of requests and workflows.
- Phoenix ingests traces via OTLP protocol (gRPC/HTTP).

**Code pointers:**
- GraphQL `Trace` type: [app/schema.graphql:12000-12050]() (approximate)
- Trace data loader: `TraceByTraceIdsDataLoader` [src/phoenix/server/app.py:165-165]()

### Project
A logical grouping of related Traces, Datasets, Experiments, Annotations, and Sessions.

- Serves as the main namespace for organization and access control.
- Each Project has configuration like trace retention policy [src/phoenix/server/api/types/Project.py:61-195]().

**Code pointers:**
- Default project name: `DEFAULT_PROJECT_NAME` [src/phoenix/config.py:59-59]()
- GraphQL `Project` type: [src/phoenix/server/api/types/Project.py:61-61]()

### Dataset
A Dataset is a collection of example inputs and expected outputs used for evaluation, experimentation, and fine-tuning.

- Supports versioning and splitting (e.g., train/test) [src/phoenix/server/app.py:96-104]().
- Datasets link examples with experiment configurations [src/phoenix/server/api/types/Dataset.py:15-80]().

**Code pointers:**
- GraphQL `Dataset` type: [app/schema.graphql:3146-3245]()
- Dataset models: `models.Dataset`, `models.DatasetExample` [src/phoenix/db/models.py:1000-1100]() (approximate)

### Experiment
An Experiment tracks and manages tests of changes against datasets and models.

- Useful for comparing prompt versions, model parameters, or retrieval mechanisms.
- Can aggregate metrics, error rates, and latency quantiles [src/phoenix/server/app.py:111-122]().

**Code pointers:**
- GraphQL `Experiment` type: [app/schema.graphql:5266-5386]()
- Status types: `RUNNING`, `COMPLETED`, `STOPPED`, `ERROR` [src/phoenix/db/models.py:184-184]()

### Evaluator
Evaluators benchmark model performance, quality, and correctness on dataset examples or generated results.

- Types include LLM evaluators, code evaluators, and built-in classification evaluators [src/phoenix/db/models.py:174-174]().
- Evaluators are associated with specific versions and input mappings [src/phoenix/db/models.py:68-68]().

**Code pointers:**
- Python evaluation framework: `arize-phoenix-evals` [packages/phoenix-evals/pyproject.toml:1-35]()
- GraphQL `Evaluator` type: [src/phoenix/server/api/types/Evaluator.py:76-82]()

### Annotation
Annotations are labels or numeric scores attached to spans, traces, or dataset examples.

- Support multiple annotator kinds: `LLM`, `HUMAN`, `CODE` [app/schema.graphql:224-228]().
- Types include `CATEGORICAL`, `CONTINUOUS`, and `FREEFORM` [app/schema.graphql:218-222]().

**Code pointers:**
- GraphQL `Annotation` interface: [app/schema.graphql:121-158]()
- Source types: `API`, `APP` [app/schema.graphql:203-206]()

### Session
A Session represents an interactive user session with Phoenix, grouping related multi-turn interactions.

- Used to track conversational state and group related traces [src/phoenix/session/session.py:70-143]().
- Phoenix Intelligence (PxI) interactions are typically session-bound [src/phoenix/server/app.py:137-142]().

**Code pointers:**
- Python `Session` class: [src/phoenix/session/session.py:70-70]()
- Thread-based session: `ThreadSession` [src/phoenix/session/session.py:185-185]()

---

## Monorepo Structure

Phoenix uses a monorepo approach consolidating multiple Python and TypeScript packages [uv.lock:26-32]().

### Python Packages

| Package | Description | Location |
| :--- | :--- | :--- |
| `arize-phoenix` | Core server and observability logic | `src/phoenix/` [pyproject.toml:1-2]() |
| `arize-phoenix-evals` | LLM Evaluation framework | `packages/phoenix-evals/` [packages/phoenix-evals/pyproject.toml:1-2]() |
| `arize-phoenix-otel` | OpenTelemetry integration helpers | `packages/phoenix-otel/` [packages/phoenix-otel/pyproject.toml:1-2]() |
| `arize-phoenix-client` | Programmatic API client | `packages/phoenix-client/` [packages/phoenix-client/pyproject.toml:1-2]() |

---

## Server Architecture

### FastAPI Application
The server is implemented as a FastAPI application [src/phoenix/server/app.py:33-33]().

- Includes middleware for CORS, authentication, and CSRF protection [src/phoenix/server/app.py:34-47]().
- Uses Starlette's lifespan for startup/shutdown tasks [src/phoenix/server/app.py:53-53]().

### GraphQL API
Phoenix uses `strawberry` for its GraphQL API [src/phoenix/server/app.py:32-32]().

- Employs the DataLoader pattern for efficient batch fetching [src/phoenix/server/app.py:88-173]().
- Schema is built via `build_graphql_schema` [src/phoenix/server/app.py:182-182]().

### OTLP Ingestion
Phoenix ingests telemetry data using OpenTelemetry Protocol (OTLP).

- Uses `opentelemetry-proto` for trace ingestion [pyproject.toml:46-46]().
- Supports both HTTP and gRPC protocols for ingestion [pyproject.toml:41-47]().

### Database Layer
Phoenix supports PostgreSQL and SQLite using SQLAlchemy ORM [pyproject.toml:51-53]().

- Database models are defined using `DeclarativeBase` [src/phoenix/db/models.py:43-43]().
- Alembic is used for schema migrations [pyproject.toml:52-52]().

### Cost Tracking
Phoenix tracks LLM token costs through a dedicated subsystem.

- Uses `SpanCostCalculator` to compute costs [src/phoenix/server/app.py:188-188]().
- Token prices are managed via `GenerativeModelStore` [src/phoenix/server/app.py:187-187]().

---

## Diagrams

### Diagram: Phoenix Monorepo Structure

```mermaid
graph TD
    subgraph "Root (arize-phoenix)"
        PYP["pyproject.toml"]
        SRC["src/phoenix/ (Server Core)"]
    end

    subgraph "Packages"
        EVALS["packages/phoenix-evals/"]
        OTEL["packages/phoenix-otel/"]
        CLIENT["packages/phoenix-client/"]
    end

    subgraph "JS/TS"
        TS_CLIENT["js/packages/phoenix-client/"]
        MCP["js/packages/phoenix-mcp/"]
    end

    PYP --- SRC
    EVALS --- OTEL
    CLIENT --- TS_CLIENT
```
Sources:
- [uv.lock:26-32]()
- [README.md:37-37]()

### Diagram: Data Flow Ingestion to Storage

```mermaid
graph TD
    subgraph "Ingestion Space"
        OTLP_HTTP["OTLP HTTP Collector"]
        OTLP_GRPC["OTLP gRPC Collector"]
    end

    subgraph "Processing Space"
        BULK_INS["BulkInserter (src/phoenix/db/bulk_inserter.py)"]
        COST_CALC["SpanCostCalculator (src/phoenix/server/daemons/span_cost_calculator.py)"]
    end

    subgraph "Code Entity Space"
        MODELS["SQLAlchemy Models (src/phoenix/db/models.py)"]
        DB["Postgres / SQLite (SQLAlchemy Engine)"]
    end

    OTLP_HTTP --> BULK_INS
    OTLP_GRPC --> BULK_INS
    BULK_INS --> MODELS
    MODELS --> COST_CALC
    COST_CALC --> DB
    MODELS --> DB
```
Sources:
- [src/phoenix/server/app.py:81-81]()
- [src/phoenix/server/app.py:188-188]()
- [src/phoenix/db/models.py:43-48]()
- [pyproject.toml:51-53]()

### Diagram: GraphQL API Resolution

```mermaid
graph TD
    subgraph "Natural Language Space"
        USER_REQ["GraphQL Query (e.g. Get Project)"]
    end

    subgraph "Code Entity Space"
        ROUTER["GraphQLRouter (src/phoenix/server/app.py)"]
        SCHEMA["build_graphql_schema (src/phoenix/server/api/schema.py)"]
        DL["ProjectByNameDataLoader (src/phoenix/server/api/dataloaders/...)"]
        MODEL["Project Model (src/phoenix/db/models.py)"]
    end

    USER_REQ --> ROUTER
    ROUTER --> SCHEMA
    SCHEMA --> DL
    DL --> MODEL
```
Sources:
- [src/phoenix/server/app.py:55-55]()
- [src/phoenix/server/app.py:128-128]()
- [src/phoenix/server/api/schema.py:182-182]()
- [src/phoenix/db/models.py:1-50]()