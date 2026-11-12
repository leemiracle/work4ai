<!-- source: DeepWiki mcp.deepwiki.com · repo arize-ai/phoenix · page 3 Client Libraries · fetched 2026-10-27 -->

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

