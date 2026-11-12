<!-- source: DeepWiki mcp.deepwiki.com · repo hypermodeinc/modus · page 1 Overview · fetched 2026-10-27 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [lib/manifest/go.mod](lib/manifest/go.mod)
- [lib/metadata/go.mod](lib/metadata/go.mod)
- [lib/wasmextractor/go.mod](lib/wasmextractor/go.mod)
- [runtime/go.mod](runtime/go.mod)
- [runtime/go.sum](runtime/go.sum)
- [runtime/languages/golang/testdata/go.mod](runtime/languages/golang/testdata/go.mod)
- [runtime/languages/golang/testdata/go.sum](runtime/languages/golang/testdata/go.sum)
- [sdk/go/go.mod](sdk/go/go.mod)
- [sdk/go/go.sum](sdk/go/go.sum)
- [sdk/go/templates/default/go.mod](sdk/go/templates/default/go.mod)
- [sdk/go/templates/default/go.sum](sdk/go/templates/default/go.sum)

</details>



This document provides a comprehensive overview of the Modus framework architecture, its core components, and how they work together to enable serverless AI application development. It covers the entire system from developer tools through runtime execution, focusing on the technical implementation and code structure.

For specific implementation details of individual components, see [CLI Commands Reference](#3.1), [Go SDK](#4.1), [Runtime Architecture](#5.1), and [GraphQL Engine](#5.2).

## What is Modus

Modus is an open-source, serverless framework for building agentic systems and AI applications using WebAssembly. It compiles code written in Go or AssemblyScript into WASM modules, then executes them in a sandboxed runtime environment with automatic GraphQL API generation.

The framework consists of four primary components:
- **Modus CLI** - Development toolchain for project management and compilation
- **SDKs** - Language-specific development kits for Go and AssemblyScript
- **Modus Runtime** - WebAssembly host with GraphQL engine and service integrations
- **Supporting Libraries** - Shared utilities for manifest processing, metadata extraction, and WASM analysis

Sources: [README.md:22-26](), [runtime/go.mod:1](), [sdk/go/go.mod:1]()

## System Architecture

```mermaid
graph TB
    subgraph "Development Layer"
        CLI["modus CLI<br/>TypeScript/Node.js"]
        GoSDK["Go SDK<br/>github.com/hypermodeinc/modus/sdk/go"]
        ASSDK["AssemblyScript SDK<br/>@hypermode/modus-as-sdk"]
    end
    
    subgraph "Runtime Layer"
        ModusRuntime["Modus Runtime<br/>github.com/hypermodeinc/modus/runtime"]
        WazeroHost["Wazero WASM Host<br/>github.com/tetratelabs/wazero"]
        GraphQLEngine["GraphQL Engine<br/>github.com/wundergraph/graphql-go-tools"]
        GoAktActors["GoAkt Actor System<br/>github.com/tochemey/goakt"]
    end
    
    subgraph "Data & AI Layer"
        PostgreSQL["PostgreSQL Client<br/>github.com/jackc/pgx"]
        MySQL["MySQL Client<br/>github.com/go-sql-driver/mysql"]
        Dgraph["Dgraph Client<br/>github.com/dgraph-io/dgo"]
        Neo4j["Neo4j Client<br/>github.com/neo4j/neo4j-go-driver"]
        S3Client["AWS S3 Client<br/>github.com/aws/aws-sdk-go-v2"]
    end
    
    CLI --> GoSDK
    CLI --> ASSDK
    GoSDK --> ModusRuntime
    ASSDK --> ModusRuntime
    ModusRuntime --> WazeroHost
    ModusRuntime --> GraphQLEngine
    ModusRuntime --> GoAktActors
    ModusRuntime --> PostgreSQL
    ModusRuntime --> MySQL
    ModusRuntime --> Dgraph
    ModusRuntime --> Neo4j
    ModusRuntime --> S3Client
```

The architecture follows a layered approach where developers interact with language-specific SDKs through the CLI, which compiles code into WASM modules executed by the runtime layer with integrated data and AI services.

Sources: [runtime/go.mod:7-59](), [sdk/go/go.mod:7-21]()

## Core Components

### Modus CLI
The command-line interface provides project scaffolding, SDK management, and development server functionality. Built with Node.js and TypeScript, it orchestrates the entire development workflow from project creation to local testing.

### WebAssembly Runtime
The runtime uses [Wazero](https://github.com/tetratelabs/wazero) as the WebAssembly host, providing a sandboxed execution environment for compiled Go and AssemblyScript modules. The `github.com/tetratelabs/wazero` dependency enables WASI-compliant WebAssembly execution.

### GraphQL API Generation
Automatic GraphQL schema generation and query processing is powered by [Wundergraph's GraphQL Go Tools](https://github.com/wundergraph/graphql-go-tools). The runtime extracts function metadata from WASM modules and generates corresponding GraphQL resolvers.

### Actor-Based Concurrency
State management and concurrent processing uses the [GoAkt](https://github.com/Tochemey/goakt) actor framework, enabling stateful agents and event-driven processing patterns through the `github.com/tochemey/goakt/v3` dependency.

Sources: [runtime/go.mod:42](), [runtime/go.mod:48-49](), [runtime/go.mod:45]()

## Development Workflow

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant CLI as "modus CLI"
    participant TinyGo as "TinyGo Compiler"
    participant Runtime as "Modus Runtime"
    participant Wazero as "Wazero Host"
    participant GraphQL as "GraphQL Engine"
    
    Dev->>CLI: "modus new my-app --sdk go"
    CLI->>Dev: "Project template created"
    
    Dev->>Dev: "Write Go functions"
    Dev->>CLI: "modus build"
    CLI->>TinyGo: "Compile to WASM"
    TinyGo->>CLI: ".wasm module"
    
    Dev->>CLI: "modus dev"
    CLI->>Runtime: "Start with .wasm"
    Runtime->>Wazero: "Load WASM module"
    Runtime->>GraphQL: "Generate schema from metadata"
    GraphQL->>Runtime: "Activate GraphQL endpoint"
    Runtime->>Dev: "Server running on :8686"
    
    Note over Dev,GraphQL: "Sub-second hot reload<br/>with metadata extraction"
```

The development process follows a compile-to-WASM approach where source code is compiled to WebAssembly modules, then loaded into the runtime for execution with automatic API generation.

Sources: [sdk/go/templates/default/go.mod:1-9](), [runtime/languages/golang/testdata/go.mod:1-9]()

## Runtime Execution Architecture

```mermaid
graph TD
    subgraph "HTTP Layer"
        HTTPServer["HTTP Server<br/>:8686"]
        CORSHandler["CORS Handler<br/>github.com/rs/cors"]
        HealthEndpoint["/health endpoint"]
        MetricsEndpoint["/metrics endpoint<br/>github.com/prometheus/client_golang"]
        ExplorerUI["/explorer UI"]
    end
    
    subgraph "GraphQL Processing"
        SchemaGenerator["Schema Generator<br/>lib/metadata"]
        QueryPlanner["Query Planner<br/>wundergraph/graphql-go-tools"]
        ExecutionEngine["Execution Engine<br/>wundergraph/graphql-go-tools/execution"]
    end
    
    subgraph "WebAssembly Execution"
        WasmHost["WASM Host<br/>tetratelabs/wazero"]
        ModuleCache["Module Cache<br/>puzpuzpuz/xsync"]
        HostFunctions["Host Functions<br/>runtime/wasmhost"]
        MemoryManager["Memory Manager"]
    end
    
    subgraph "Actor System"
        ActorSupervisor["Actor Supervisor<br/>tochemey/goakt"]
        AgentActors["Agent Actors"]
        EventSubscribers["Event Subscribers"]
        StateStore["State Store"]
    end
    
    HTTPServer --> CORSHandler
    CORSHandler --> SchemaGenerator
    SchemaGenerator --> QueryPlanner
    QueryPlanner --> ExecutionEngine
    ExecutionEngine --> WasmHost
    WasmHost --> ModuleCache
    WasmHost --> HostFunctions
    WasmHost --> MemoryManager
    HostFunctions --> ActorSupervisor
    ActorSupervisor --> AgentActors
    ActorSupervisor --> EventSubscribers
    AgentActors --> StateStore
```

The runtime architecture implements a multi-layered execution model where HTTP requests flow through GraphQL processing into WebAssembly execution, supported by an actor-based concurrency system for stateful operations.

Sources: [runtime/go.mod:37](), [runtime/go.mod:36](), [runtime/go.mod:48](), [runtime/go.mod:45]()

## Data Integration Layer

```mermaid
graph LR
    subgraph "Database Clients"
        PgxClient["PostgreSQL<br/>github.com/jackc/pgx/v5"]
        MySQLClient["MySQL<br/>github.com/go-sql-driver/mysql"]
        DgraphClient["Dgraph<br/>github.com/dgraph-io/dgo/v240"]
        Neo4jClient["Neo4j<br/>github.com/neo4j/neo4j-go-driver/v5"]
    end
    
    subgraph "Cloud Services"
        AWSS3["AWS S3<br/>github.com/aws/aws-sdk-go-v2/service/s3"]
        AWSSTS["AWS STS<br/>github.com/aws/aws-sdk-go-v2/service/sts"]
    end
    
    subgraph "Connection Management"
        DBURLParser["DB URL Parser<br/>github.com/xo/dburl"]
        ConnectionPool["Connection Pool"]
        SecretManager["Secret Manager"]
    end
    
    subgraph "WASM Host Functions"
        DatabaseAPI["Database API"]
        StorageAPI["Storage API"]
        ModelAPI["Model API"]
    end
    
    PgxClient --> ConnectionPool
    MySQLClient --> ConnectionPool
    DgraphClient --> ConnectionPool
    Neo4jClient --> ConnectionPool
    AWSS3 --> SecretManager
    AWSSTS --> SecretManager
    DBURLParser --> ConnectionPool
    ConnectionPool --> DatabaseAPI
    SecretManager --> StorageAPI
    DatabaseAPI --> ModelAPI
```

The data integration layer provides unified access to multiple database types and cloud services through a connection pooling system that exposes APIs to WebAssembly modules via host functions.

Sources: [runtime/go.mod:29](), [runtime/go.mod:20](), [runtime/go.mod:15](), [runtime/go.mod:33](), [runtime/go.mod:11-12](), [runtime/go.mod:50]()

## Compilation and Build System

The framework supports multiple compilation paths depending on the target language:

### Go Compilation Path
Go code is compiled using TinyGo to produce optimized WebAssembly modules. The `sdk/go` package provides the necessary runtime interfaces and build tooling.

### AssemblyScript Compilation Path  
AssemblyScript code compiles directly to WebAssembly using the AssemblyScript compiler, with the AssemblyScript SDK providing Modus-specific APIs and type definitions.

### Module Processing Pipeline
1. **Source Analysis** - Extract function signatures and metadata
2. **WASM Compilation** - Compile to WebAssembly with optimization
3. **Metadata Extraction** - Parse WASM custom sections for function information  
4. **Schema Generation** - Generate GraphQL schema from extracted metadata
5. **Runtime Loading** - Load compiled modules into Wazero host with caching

Sources: [sdk/go/go.mod:8-9](), [lib/metadata/go.mod:8](), [lib/wasmextractor/go.mod:1]()

## Monitoring and Observability

```mermaid
graph TB
    subgraph "Metrics Collection"
        PrometheusClient["Prometheus Client<br/>github.com/prometheus/client_golang"]
        PrometheusCommon["Prometheus Common<br/>github.com/prometheus/common"]
    end
    
    subgraph "Logging"
        ZerologLogger["Zerolog<br/>github.com/rs/zerolog"]
        SentryIntegration["Sentry Integration<br/>github.com/getsentry/sentry-go"]
        ZerologSentry["Zerolog-Sentry<br/>github.com/archdx/zerolog-sentry"]
    end
    
    subgraph "Tracing"
        AbstractLogger["Abstract Logger<br/>github.com/jensneuse/abstractlogger"]
        ColorOutput["Colored Output<br/>github.com/fatih/color"]
    end
    
    PrometheusClient --> PrometheusCommon
    ZerologLogger --> SentryIntegration
    SentryIntegration --> ZerologSentry
    AbstractLogger --> ColorOutput
    PrometheusClient --> ZerologLogger
```

The observability stack combines Prometheus metrics, structured logging with Zerolog, and optional Sentry error tracking to provide comprehensive monitoring of runtime operations and WASM execution.

Sources: [runtime/go.mod:34-35](), [runtime/go.mod:39](), [runtime/go.mod:19](), [runtime/go.mod:9](), [runtime/go.mod:18]()

---

