# Page: Overview

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

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [cli/package-lock.json](cli/package-lock.json)
- [cli/package.json](cli/package.json)
- [cli/src/commands/build/index.ts](cli/src/commands/build/index.ts)
- [cli/src/commands/dev/index.ts](cli/src/commands/dev/index.ts)
- [cli/src/commands/info/index.ts](cli/src/commands/info/index.ts)
- [cli/src/commands/new/index.ts](cli/src/commands/new/index.ts)
- [cli/src/commands/runtime/install/index.ts](cli/src/commands/runtime/install/index.ts)
- [cli/src/commands/runtime/list/index.ts](cli/src/commands/runtime/list/index.ts)
- [cli/src/commands/runtime/remove/index.ts](cli/src/commands/runtime/remove/index.ts)
- [cli/src/commands/sdk/install/index.ts](cli/src/commands/sdk/install/index.ts)
- [cli/src/commands/sdk/list/index.ts](cli/src/commands/sdk/list/index.ts)
- [cli/src/commands/sdk/remove/index.ts](cli/src/commands/sdk/remove/index.ts)
- [cli/src/custom/help.ts](cli/src/custom/help.ts)
- [cli/src/util/installer.ts](cli/src/util/installer.ts)
- [cli/src/util/systemVersions.ts](cli/src/util/systemVersions.ts)
- [runtime/languages/assemblyscript/testdata/build/testdata.wasm](runtime/languages/assemblyscript/testdata/build/testdata.wasm)
- [runtime/languages/assemblyscript/testdata/package-lock.json](runtime/languages/assemblyscript/testdata/package-lock.json)
- [sdk/assemblyscript/templates/default/package-lock.json](sdk/assemblyscript/templates/default/package-lock.json)
- [sdk/assemblyscript/templates/default/package.json](sdk/assemblyscript/templates/default/package.json)
- [tools/release-info/package-lock.json](tools/release-info/package-lock.json)
- [tools/release-info/package.json](tools/release-info/package.json)

</details>



This page provides an overview of how to get started with Modus, covering installation, creating your first application, and understanding the basic development workflow. For detailed installation instructions, see [Installation](#2.1). For a step-by-step tutorial, see [Quick Start Tutorial](#2.2).

Modus is a framework for building AI-enabled applications using WebAssembly. It provides SDKs for Go and AssemblyScript, a CLI for development workflow management, and a runtime for executing applications with built-in AI model integration, database connectivity, and GraphQL API generation.

## Prerequisites and Dependencies

Before getting started with Modus, you need to install the appropriate development tools depending on which SDK you plan to use.

### For AssemblyScript Development

- **Node.js**: Version 22 or newer
- **NPM**: Automatically installed with Node.js

### For Go Development  

- **Go**: Version 1.23.0 or newer
- **TinyGo**: Version 0.35.0 or newer  
- **Binaryen**: Required for WebAssembly optimization

The Modus CLI will validate these prerequisites when creating new projects and provide installation guidance if any are missing.

**Sources:** [cli/src/commands/new/index.ts:183-269](), [cli/src/custom/globals.js:21]()

## Installation Overview

Modus installation involves three main components that work together:

```mermaid
graph TD
    CLI["@hypermode/modus-cli<br/>npm package"] --> SDKInstall["SDK Installation<br/>modus sdk install"]
    SDKInstall --> GoSDK["Go SDK<br/>modus-go-build tool"]
    SDKInstall --> ASSDK["AssemblyScript SDK<br/>modus-as-build tool"]
    SDKInstall --> Runtime["Modus Runtime<br/>modus_runtime binary"]
    
    CLI --> NewCommand["modus new<br/>Project creation"]
    NewCommand --> Templates["Project templates<br/>from SDK packages"]
    
    GoSDK --> BuildGo["TinyGo compilation<br/>to .wasm modules"]
    ASSDK --> BuildAS["AssemblyScript compilation<br/>to .wasm modules"]
```

The CLI automatically manages SDK and runtime versions, downloading compatible versions as needed during development.

**Sources:** [cli/src/commands/sdk/install/index.ts:86-155](), [cli/src/util/installer.ts:19-94]()

## Creating Your First Application

The `modus new` command provides an interactive way to create applications:

### Command Flow and Validation

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant CLI as "NewCommand"
    participant Validator as "SDK Validator"
    participant Installer as "SDK Installer"
    participant Template as "Template System"
    
    Dev->>CLI: "modus new my-app --sdk go"
    CLI->>Validator: "validateSdkPrereq()"
    Validator->>Validator: "getGoVersion(), getTinyGoVersion()"
    
    alt Prerequisites Missing
        Validator->>Dev: "Error with installation instructions"
    else Prerequisites OK
        Validator->>CLI: "Validation passed"
        CLI->>Installer: "Install latest SDK if needed"
        Installer->>Template: "Extract templates from SDK package"
        Template->>CLI: "Apply SDK-specific modifications"
        CLI->>Dev: "Project created successfully"
    end
```

### Project Structure Creation

The CLI uses templates from SDK packages and applies language-specific configurations:

- **AssemblyScript**: Updates `package.json` name, runs `npm install`
- **Go**: Updates `go.mod` module name and Go version, runs `go mod download` and `go mod tidy`

**Sources:** [cli/src/commands/new/index.ts:271-378](), [cli/src/commands/new/index.ts:348-363]()

## Development Workflow

The core development cycle involves three main CLI commands that orchestrate the build and runtime systems:

### Development Command Flow

```mermaid
graph LR
    New["modus new<br/>NewCommand"] --> Build["modus build<br/>BuildCommand"]
    Build --> Dev["modus dev<br/>DevCommand"]
    Dev --> Watch["File Watching<br/>chokidar"]
    Watch --> Build
    
    subgraph "Build Process"
        Build --> ASBuild["npx modus-as-build<br/>AssemblyScript"]
        Build --> GoBuild["modus-go-build<br/>Go/TinyGo"]
        ASBuild --> WASM["WebAssembly .wasm files"]
        GoBuild --> WASM
    end
    
    subgraph "Runtime Process"
        Dev --> RuntimeBinary["modus_runtime executable"]
        RuntimeBinary --> GraphQLEndpoint["GraphQL API :8686"]
        RuntimeBinary --> Explorer["API Explorer :8686/explorer"]
    end
```

### File Watching and Hot Reload

The `DevCommand` implements sophisticated file watching to enable hot reload during development:

```mermaid
graph TD
    DevCommand --> EnvWatch["ENV_FILES watcher<br/>.env, .env.local, etc"]
    DevCommand --> ManifestWatch["modus.json watcher"]
    DevCommand --> CodeWatch["Source code watcher"]
    
    EnvWatch --> CopyEnv["Copy to build directory<br/>Runtime auto-reloads"]
    ManifestWatch --> CopyManifest["Copy to build directory<br/>Runtime auto-reloads"]
    CodeWatch --> RebuildApp["BuildCommand.run()<br/>Full application rebuild"]
    
    subgraph "SDK-Specific Globs"
        CodeWatch --> ASGlobs["**/*.ts, **/package.json<br/>exclude node_modules/**"]
        CodeWatch --> GoGlobs["**/*.go, **/go.mod<br/>exclude **/*_test.go"]
    end
```

**Sources:** [cli/src/commands/dev/index.ts:196-359](), [cli/src/commands/dev/index.ts:366-385]()

## Build Process Architecture

The build system bridges high-level source code to WebAssembly modules that the runtime can execute:

### SDK Build Tool Integration

```mermaid
graph TB
    subgraph "Build Command Entry"
        BuildCommand["BuildCommand.run()"] --> SDKDetection["getAppInfo() reads modus.json"]
        SDKDetection --> SDKValidation["Check SDK installation"]
    end
    
    subgraph "AssemblyScript Build"
        ASPath["npx modus-as-build"] --> ASCompiler["AssemblyScript compiler"]
        ASCompiler --> ASOptimize["Binaryen optimization"]
        ASOptimize --> ASWasm["app.wasm + metadata"]
    end
    
    subgraph "Go Build"  
        GoPath["modus-go-build executable"] --> TinyGoCompiler["TinyGo compilation"]
        TinyGoCompiler --> GoWasm["app.wasm + metadata"]
    end
    
    BuildCommand --> ASPath
    BuildCommand --> GoPath
    ASWasm --> BuildDir["build/ directory"]
    GoWasm --> BuildDir
```

### Runtime Integration

The runtime consumes the build artifacts and generates APIs:

```mermaid
graph LR
    BuildDir["build/ directory"] --> WasmModule["WebAssembly module"]
    BuildDir --> Manifest["modus.json manifest"]
    BuildDir --> EnvFiles[".env files"]
    
    WasmModule --> MetadataExtract["Extract function metadata"]
    MetadataExtract --> SchemaGen["Generate GraphQL schema"]
    SchemaGen --> GraphQLAPI["GraphQL endpoints"]
    
    Manifest --> ConnectionConfig["Database connections"]
    Manifest --> ModelConfig["AI model configurations"]
    
    EnvFiles --> RuntimeEnv["Runtime environment variables"]
```

**Sources:** [cli/src/commands/build/index.ts:39-110](), [cli/src/commands/dev/index.ts:140-182]()

## Key Files and Entry Points

The following table maps common development tasks to their code entry points:

| Task | CLI Command | Primary Implementation | Build Tool |
|------|-------------|----------------------|------------|
| Create new app | `modus new` | [NewCommand]() | Template extraction |
| Build application | `modus build` | [BuildCommand]() | `modus-as-build` or `modus-go-build` |
| Start development | `modus dev` | [DevCommand]() | Runtime + file watching |
| Install SDK | `modus sdk install` | [SDKInstallCommand]() | Download and extract |
| Runtime management | `modus runtime install` | [RuntimeInstallCommand]() | Binary download |

**Sources:** [cli/package.json:61-84](), [cli/src/commands/build/index.ts:24](), [cli/src/commands/dev/index.ts:34]()

## Next Steps

Once you have Modus installed, you can:

1. **Create your first application**: Use [Quick Start Tutorial](#2.2) for a hands-on walkthrough
2. **Explore CLI commands**: See [CLI Commands Reference](#3.1) for complete command documentation  
3. **Choose your SDK**: Review [Go SDK](#4.1) or [AssemblyScript SDK](#4.2) guides
4. **Understand the runtime**: Read [Runtime Architecture](#5.1) to learn how applications execute

The development workflow centers around the `modus dev` command, which provides live reload and integrates all the components shown above into a seamless development experience.

---

# Page: Installation

# Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [cli/install.sh](cli/install.sh)
- [cli/src/commands/build/index.ts](cli/src/commands/build/index.ts)
- [cli/src/commands/dev/index.ts](cli/src/commands/dev/index.ts)
- [cli/src/commands/info/index.ts](cli/src/commands/info/index.ts)
- [cli/src/commands/new/index.ts](cli/src/commands/new/index.ts)
- [cli/src/commands/runtime/install/index.ts](cli/src/commands/runtime/install/index.ts)
- [cli/src/commands/runtime/list/index.ts](cli/src/commands/runtime/list/index.ts)
- [cli/src/commands/runtime/remove/index.ts](cli/src/commands/runtime/remove/index.ts)
- [cli/src/commands/sdk/install/index.ts](cli/src/commands/sdk/install/index.ts)
- [cli/src/commands/sdk/list/index.ts](cli/src/commands/sdk/list/index.ts)
- [cli/src/commands/sdk/remove/index.ts](cli/src/commands/sdk/remove/index.ts)
- [cli/src/custom/globals.ts](cli/src/custom/globals.ts)
- [cli/src/custom/help.ts](cli/src/custom/help.ts)
- [cli/src/util/http.ts](cli/src/util/http.ts)
- [cli/src/util/index.ts](cli/src/util/index.ts)
- [cli/src/util/installer.ts](cli/src/util/installer.ts)
- [cli/src/util/systemVersions.ts](cli/src/util/systemVersions.ts)
- [cli/src/util/versioninfo.ts](cli/src/util/versioninfo.ts)
- [runtime/plugins/plugins.go](runtime/plugins/plugins.go)
- [sdk/assemblyscript/src/plugin.asconfig.json](sdk/assemblyscript/src/plugin.asconfig.json)
- [sdk/go/tools/modus-go-build/compiler/compiler.go](sdk/go/tools/modus-go-build/compiler/compiler.go)

</details>



This page provides detailed instructions for installing the Modus CLI and its dependencies. It covers the complete installation process from prerequisites through CLI installation, SDK setup, and runtime configuration.

For information about creating your first Modus application after installation, see [Quick Start Tutorial](#2.2). For details about managing SDK and runtime versions after installation, see [Version Management](#3.2).

## Prerequisites

Before installing Modus, ensure your system meets the following requirements:

| Component | Minimum Version | Required For |
|-----------|----------------|--------------|
| Node.js | 22.0.0 | CLI and AssemblyScript SDK |
| npm | Latest | CLI installation |
| Go | 1.23.1 | Go SDK development |
| TinyGo | 0.35.0 | Go SDK compilation |
| Binaryen | Latest | WebAssembly optimization |

The Modus CLI validates these prerequisites during SDK installation and provides specific guidance for missing dependencies.

**Prerequisites Validation Flow**

```mermaid
flowchart TD
    Start["modus new command"] --> CheckSDK["parseSDK()"]
    CheckSDK --> ValidatePrereq["validateSdkPrereq()"]
    
    ValidatePrereq --> ASCheck{SDK == AssemblyScript?}
    ASCheck -->|Yes| NodeCheck["semver.lt(process.versions.node, MinNodeVersion)"]
    NodeCheck -->|Valid| Continue["Continue installation"]
    NodeCheck -->|Invalid| NodeError["Exit with Node.js error"]
    
    ASCheck -->|No| GoCheck{SDK == Go?}
    GoCheck --> GetVersions["getGoVersion(), getTinyGoVersion(), getBinaryenVersion()"]
    GetVersions --> ValidateVersions["Check Go >= 1.23.1, TinyGo >= 0.35.0"]
    ValidateVersions -->|Valid| Continue
    ValidateVersions -->|Invalid| GoError["Exit with installation instructions"]
    
    NodeError --> Exit["this.exit(1)"]
    GoError --> Exit
    Continue --> InstallSDK["Proceed with SDK installation"]
```

Sources: [cli/src/commands/new/index.ts:183-269](), [cli/src/custom/globals.ts:16-18](), [cli/src/util/systemVersions.ts:18-56]()

## CLI Installation

### Automated Installation

The recommended method uses the official installation script:

```bash
curl install.hypermode.com/modus.sh -sSfL | bash
```

This script automatically:
- Downloads the latest CLI version from npm
- Installs to `$MODUS_HOME/cli` (defaults to `~/.modus/cli`)
- Configures PATH in your shell profile
- Validates Node.js compatibility

**CLI Installation Process**

```mermaid
flowchart TD
    Script["install.sh"] --> CheckPlatform["check_platform()"]
    CheckPlatform --> CheckNode["check_node()"]
    CheckNode --> GetVersion["get_latest_version()"]
    
    GetVersion --> DownloadNPM["download_from_npm()"]
    DownloadNPM --> Extract["tar -xf archive"]
    Extract --> InstallDeps["npm install --omit=dev"]
    InstallDeps --> CreateSymlink["ln -s bin/modus.js bin/modus"]
    CreateSymlink --> UpdateProfile["update_profile()"]
    UpdateProfile --> Complete["Installation complete"]
    
    CheckNode -->|Node < 22| NodeError["Exit with Node.js error"]
    CheckPlatform -->|Unsupported| PlatformError["Exit with platform error"]
```

Sources: [cli/install.sh:278-295](), [cli/install.sh:167-235]()

### Manual Installation

For manual installation or CI environments:

```bash
# Set installation directory
export MODUS_CLI="$HOME/.modus/cli"

# Download and extract
npm pack @hypermode/modus-cli
tar -xf modus-cli-*.tgz
mv package/* "$MODUS_CLI"
cd "$MODUS_CLI" && npm install --omit=dev

# Add to PATH
export PATH="$MODUS_CLI/bin:$PATH"
```

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MODUS_HOME` | `~/.modus` | Base directory for all Modus files |
| `MODUS_CLI` | `$MODUS_HOME/cli` | CLI installation directory |

Sources: [cli/install.sh:15](), [cli/src/custom/globals.ts:14]()

## SDK Installation

SDKs provide language-specific tools and libraries for building Modus applications. Installation is managed through the CLI.

### Installing SDKs

```bash
# Install latest stable SDK
modus sdk install go
modus sdk install assemblyscript

# Install specific version
modus sdk install go v0.17.0

# Install prerelease version
modus sdk install go --prerelease

# Install all SDKs
modus sdk install all
```

**SDK Installation Architecture**

```mermaid
flowchart TD
    CLI["SDKInstallCommand"] --> CheckOnline["isOnline()"]
    CheckOnline --> GetVersion["getLatestSdkVersion()"]
    GetVersion --> Download["installer.installSDK()"]
    
    Download --> DownloadInfo["Download sdk.json"]
    DownloadInfo --> DownloadTemplates["Download templates.tar.gz"]
    DownloadTemplates --> InstallBuildTools["installBuildTools()"]
    
    InstallBuildTools --> GoTools{SDK == Go?}
    GoTools -->|Yes| InstallGoTools["go install modus-go-build"]
    GoTools -->|No| Complete["Installation complete"]
    InstallGoTools --> Complete
    
    subgraph "SDK Directory Structure"
        SDKPath["getSdkPath(sdk, version)"]
        SDKPath --> InfoFile["sdk.json"]
        SDKPath --> Templates["templates.tar.gz"]
        SDKPath --> BuildTool["modus-go-build (Go only)"]
    end
```

Sources: [cli/src/commands/sdk/install/index.ts:86-155](), [cli/src/util/installer.ts:19-94](), [cli/src/util/versioninfo.ts:18-24]()

### SDK Directory Structure

Each installed SDK follows a consistent directory layout:

```
$MODUS_HOME/sdk/
├── go/
│   └── v0.17.0/
│       ├── sdk.json              # SDK metadata and runtime compatibility
│       ├── templates.tar.gz      # Project templates
│       └── modus-go-build        # Go-specific build tool
└── assemblyscript/
    └── v0.17.0/
        ├── sdk.json
        └── templates.tar.gz
```

The `sdk.json` file contains runtime compatibility information used for automatic runtime installation:

```json
{
  "runtime": {
    "version": ">=0.17.0 <0.18.0"
  }
}
```

Sources: [cli/src/util/versioninfo.ts:18-24](), [cli/src/util/installer.ts:28-36]()

## Runtime Installation

The Modus Runtime executes compiled WebAssembly modules. It's automatically installed when needed, but can also be managed manually.

### Automatic Runtime Installation

The CLI automatically installs compatible runtime versions:

```bash
# Runtime installed automatically during 'modus dev'
modus dev

# Runtime installed automatically during 'modus new'
modus new my-app
```

**Runtime Compatibility Resolution**

```mermaid
flowchart TD
    AppStart["modus dev"] --> GetAppInfo["getAppInfo()"]
    GetAppInfo --> ReadSDKInfo["Read sdk.json"]
    ReadSDKInfo --> ParseConstraint["Parse runtime.version constraint"]
    
    ParseConstraint --> ExactVersion{Exact version?}
    ExactVersion -->|Yes| CheckInstalled["runtimeVersionIsInstalled()"]
    ExactVersion -->|No| FindLatest["findLatestCompatibleRuntimeVersion()"]
    
    FindLatest --> FilterVersions["semver.satisfies() filtering"]
    FilterVersions --> GetLatest["Return latest compatible"]
    
    CheckInstalled -->|Not installed| Download["installer.installRuntime()"]
    GetLatest --> Download
    Download --> Extract["Extract to getRuntimePath()"]
    Extract --> Ready["Runtime ready"]
```

Sources: [cli/src/commands/dev/index.ts:112-138](), [cli/src/util/versioninfo.ts:287-319]()

### Manual Runtime Installation

```bash
# Install latest runtime
modus runtime install

# Install specific version  
modus runtime install v0.17.0

# Install prerelease
modus runtime install --prerelease
```

### Runtime Directory Structure

```
$MODUS_HOME/runtime/
└── v0.17.0/
    ├── modus_runtime          # Main runtime binary
    └── (other runtime files)
```

Sources: [cli/src/commands/runtime/install/index.ts:44-77](), [cli/src/util/versioninfo.ts:22-24]()

## Version Management

Modus uses a sophisticated version management system that ensures compatibility between CLI, SDKs, and runtime components.

**Version Resolution System**

```mermaid
flowchart TD
    VersionRequest["Version request"] --> TypeCheck{Request type?}
    
    TypeCheck -->|latest| FetchLatest["fetchModusLatest()"]
    TypeCheck -->|prerelease| FetchPreview["fetchModusPreview()"]
    TypeCheck -->|specific| ValidateExists["Check release exists"]
    
    FetchLatest --> LatestData["releases.hypermode.com/modus-latest.json"]
    FetchPreview --> PreviewData["releases.hypermode.com/modus-preview.json"]
    
    LatestData --> ParseVersion["Extract version for component"]
    PreviewData --> ParseVersion
    ValidateExists --> ParseVersion
    
    ParseVersion --> CheckInstalled["Check local installation"]
    CheckInstalled -->|Not installed| Download["Download and install"]
    CheckInstalled -->|Installed| UseLocal["Use existing installation"]
    
    Download --> InstallPath["Install to ModusHomeDir"]
    UseLocal --> Ready["Component ready"]
    InstallPath --> Ready
```

Sources: [cli/src/util/versioninfo.ts:40-171](), [cli/src/custom/globals.ts:14]()

### Version Information Sources

The CLI fetches version information from centralized JSON endpoints:

| Endpoint | Purpose | Content |
|----------|---------|---------|
| `modus-latest.json` | Stable releases | Latest stable versions for all components |
| `modus-preview.json` | Prerelease versions | Latest prerelease versions |
| `modus-all.json` | All versions | Complete version history |
| `modus-preview-all.json` | All prereleases | Complete prerelease history |

Sources: [cli/src/util/versioninfo.ts:43-106]()

### Compatibility Matrix

The system maintains compatibility between components using semantic versioning constraints defined in each SDK's `sdk.json` file:

```javascript
// Example compatibility check
const constraint = ">=0.17.0 <0.18.0";
const availableVersions = ["v0.17.0", "v0.17.1", "v0.18.0"];
const compatibleVersions = versions.filter(v => 
  semver.satisfies(v.slice(1), constraint)
);
```

Sources: [cli/src/util/versioninfo.ts:271-318]()

## Installation Verification

After installation, verify your setup:

```bash
# Check CLI installation
modus --version

# View installation details
modus info

# List installed components
modus sdk list
modus runtime list
```

The `modus info` command provides comprehensive system information including installed versions, system requirements, and dependency status.

Sources: [cli/src/commands/info/index.ts:18-93](), [cli/src/commands/sdk/list/index.ts:22-54](), [cli/src/commands/runtime/list/index.ts:21-43]()

---

# Page: Quick Start Tutorial

# Quick Start Tutorial

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [cli/src/commands/build/index.ts](cli/src/commands/build/index.ts)
- [cli/src/commands/dev/index.ts](cli/src/commands/dev/index.ts)
- [cli/src/commands/info/index.ts](cli/src/commands/info/index.ts)
- [cli/src/commands/new/index.ts](cli/src/commands/new/index.ts)
- [cli/src/commands/runtime/install/index.ts](cli/src/commands/runtime/install/index.ts)
- [cli/src/commands/runtime/list/index.ts](cli/src/commands/runtime/list/index.ts)
- [cli/src/commands/runtime/remove/index.ts](cli/src/commands/runtime/remove/index.ts)
- [cli/src/commands/sdk/install/index.ts](cli/src/commands/sdk/install/index.ts)
- [cli/src/commands/sdk/list/index.ts](cli/src/commands/sdk/list/index.ts)
- [cli/src/commands/sdk/remove/index.ts](cli/src/commands/sdk/remove/index.ts)
- [cli/src/custom/help.ts](cli/src/custom/help.ts)
- [cli/src/util/installer.ts](cli/src/util/installer.ts)
- [cli/src/util/systemVersions.ts](cli/src/util/systemVersions.ts)
- [sdk/assemblyscript/examples/auth/package-lock.json](sdk/assemblyscript/examples/auth/package-lock.json)
- [sdk/assemblyscript/examples/neo4j/package-lock.json](sdk/assemblyscript/examples/neo4j/package-lock.json)
- [sdk/assemblyscript/examples/simple/package-lock.json](sdk/assemblyscript/examples/simple/package-lock.json)
- [sdk/assemblyscript/examples/vectors/package-lock.json](sdk/assemblyscript/examples/vectors/package-lock.json)
- [sdk/go/examples/anthropic-functions/go.mod](sdk/go/examples/anthropic-functions/go.mod)
- [sdk/go/examples/auth/go.mod](sdk/go/examples/auth/go.mod)
- [sdk/go/examples/classification/go.mod](sdk/go/examples/classification/go.mod)
- [sdk/go/examples/dgraph/go.mod](sdk/go/examples/dgraph/go.mod)
- [sdk/go/examples/embedding/go.mod](sdk/go/examples/embedding/go.mod)
- [sdk/go/examples/graphql/go.mod](sdk/go/examples/graphql/go.mod)
- [sdk/go/examples/http/go.mod](sdk/go/examples/http/go.mod)
- [sdk/go/examples/postgresql/go.mod](sdk/go/examples/postgresql/go.mod)
- [sdk/go/examples/simple/go.mod](sdk/go/examples/simple/go.mod)
- [sdk/go/examples/textgeneration/go.mod](sdk/go/examples/textgeneration/go.mod)
- [sdk/go/examples/vectors/go.mod](sdk/go/examples/vectors/go.mod)

</details>



This tutorial provides a step-by-step guide to creating and running your first Modus application. It covers the essential workflow from installation through local development and demonstrates how Modus automatically generates GraphQL APIs from your WebAssembly functions.

For detailed installation instructions, see [Installation](#2.1). For comprehensive CLI command reference, see [CLI Commands Reference](#3.1).

## Prerequisites and Installation

Before creating your first Modus application, you need to install the Modus CLI and the appropriate SDK dependencies based on your preferred programming language.

### Installing the Modus CLI

The Modus CLI is the primary tool for creating, building, and running Modus applications. Install it using npm:

```bash
npm install -g @hypermode/modus-cli
```

Verify the installation:

```bash
modus --version
```

### SDK Prerequisites

Modus supports two SDKs: Go and AssemblyScript. Choose the one that matches your preferred language:

**For Go SDK:**
- Go v1.23.0 or newer
- TinyGo v0.34.0 or newer  
- Binaryen (for WebAssembly optimization)

**For AssemblyScript SDK:**
- Node.js v22 or newer

The CLI will validate these prerequisites when creating new projects and provide installation guidance if dependencies are missing.

Sources: [cli/src/commands/new/index.ts:183-268](), [cli/src/util/systemVersions.ts:18-56]()

## Creating Your First Application

Use the `modus new` command to create a new Modus application. The CLI provides an interactive setup process:

```bash
modus new
```

This will prompt you to:
1. Select an SDK (Go or AssemblyScript)
2. Choose an application name
3. Specify the directory location
4. Optionally initialize a Git repository

Alternatively, you can create an application non-interactively:

```bash
modus new --name my-app --sdk go --dir ./my-app
```

### Project Creation Flow

```mermaid
flowchart TD
    Start["modus new"] --> CheckPrereqs["Validate SDK Prerequisites"]
    CheckPrereqs --> GetInput["Gather Project Configuration"]
    GetInput --> CheckSDK["Check SDK Installation"]
    CheckSDK --> InstallSDK["Install/Update SDK if needed"]
    InstallSDK --> CreateProject["Create Project from Template"]
    CreateProject --> ApplyConfig["Apply SDK-specific Configuration"]
    ApplyConfig --> InitGit["Initialize Git Repository (optional)"]
    InitGit --> Complete["Project Ready"]
    
    CheckPrereqs -->|"Missing Prerequisites"| ShowError["Display Installation Instructions"]
    ShowError --> Exit["Exit with Error"]
```

The CLI automatically downloads and installs the latest compatible SDK and runtime versions. It uses templates from the SDK packages to scaffold the project structure.

Sources: [cli/src/commands/new/index.ts:271-378](), [cli/src/commands/sdk/install/index.ts:86-154]()

## Project Structure

After creating a project, you'll find the following structure:

```
my-app/
├── modus.json          # Application manifest
├── .env                # Environment variables (optional)
├── build/              # Build output (auto-generated)
└── [SDK-specific files]
```

### Go SDK Projects

```
├── go.mod              # Go module definition
├── go.sum              # Go module checksums  
├── main.go             # Application entry point
└── functions.go        # Example functions
```

### AssemblyScript SDK Projects

```
├── package.json        # Node.js package definition
├── asconfig.json       # AssemblyScript configuration
├── assembly/
│   ├── index.ts        # Application entry point
│   └── functions.ts    # Example functions
└── node_modules/       # Dependencies
```

The `modus.json` manifest file defines your application configuration, including connections to external services and runtime settings.

Sources: [cli/src/commands/new/index.ts:344-362]()

## Building and Running Locally

### Building Your Application

Build your application to generate WebAssembly modules:

```bash
modus build
```

This command:
1. Validates the project structure
2. Installs any missing SDK dependencies
3. Compiles your code to WebAssembly
4. Generates metadata for GraphQL schema creation
5. Outputs files to the `build/` directory

### Development Server

Start the local development server:

```bash
modus dev
```

This launches the Modus runtime with your application and provides:
- GraphQL API endpoint at `http://localhost:8686/graphql`
- API Explorer at `http://localhost:8686/explorer`
- Health check endpoint at `http://localhost:8686/health`
- Automatic rebuilds when source files change

### Development Workflow

```mermaid
flowchart LR
    Edit["Edit Source Code"] --> Detect["File Change Detection"]
    Detect --> Build["Automatic Rebuild"] 
    Build --> Deploy["Deploy to Runtime"]
    Deploy --> Test["Test via GraphQL API"]
    Test --> Edit
    
    subgraph Runtime["Modus Runtime"]
        GraphQL["GraphQL Endpoint"]
        Explorer["API Explorer"]
        WASM["WebAssembly Execution"]
    end
    
    Deploy --> Runtime
```

The development server automatically watches for changes in your source files and rebuilds the application when modifications are detected. This provides a fast feedback loop for development.

Sources: [cli/src/commands/dev/index.ts:143-204](), [cli/src/commands/build/index.ts:62-96]()

## Understanding Function Execution

When you run `modus dev`, the runtime analyzes your compiled WebAssembly module and automatically generates a GraphQL schema based on your exported functions.

### Function to GraphQL Mapping

```mermaid
flowchart TD
    subgraph Source["Source Code"]
        GoFunc["Go Function: func Hello(name string) string"]
        ASFunc["AssemblyScript Function: export function hello(name: string): string"]
    end
    
    subgraph Build["Build Process"]
        Compile["Compile to WebAssembly"]
        Extract["Extract Function Metadata"]
    end
    
    subgraph Runtime["Modus Runtime"]
        Schema["Generate GraphQL Schema"]
        Resolve["Function Resolver"]
        Execute["WASM Execution"]
    end
    
    subgraph GraphQL["Generated API"]
        Query["query { hello(name: \"World\") }"]
        Response["{ \"data\": { \"hello\": \"Hello, World!\" } }"]
    end
    
    Source --> Build
    Build --> Runtime  
    Runtime --> GraphQL
```

Your exported functions become GraphQL queries or mutations automatically. The runtime handles:
- Type conversion between GraphQL and WebAssembly
- Function parameter validation
- Response serialization
- Error handling

Sources: [cli/src/commands/dev/index.ts:164-182]()

## Testing Your Application

### Using the API Explorer

Navigate to `http://localhost:8686/explorer` to access the built-in API Explorer. This provides:
- Interactive GraphQL query editor
- Schema documentation
- Real-time query execution
- Response inspection

### Making GraphQL Requests

You can also make direct HTTP requests to the GraphQL endpoint:

```bash
curl -X POST http://localhost:8686/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ hello(name: \"World\") }"}'
```

### Development Monitoring

The runtime provides several monitoring endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/health` | Health check and system status |
| `/metrics` | Runtime performance metrics |
| `/explorer` | Interactive API documentation |

Sources: [cli/src/commands/dev/index.ts:148-163]()

## File Watching and Hot Reloading

The development server implements intelligent file watching that responds to different types of changes:

### Watched Files by SDK

```mermaid
flowchart TD
    subgraph Go["Go SDK Watching"]
        GoFiles["*.go files"]
        GoMod["go.mod"]
        GoExclude["Excludes: *_test.go, *_generated.go"]
    end
    
    subgraph AS["AssemblyScript SDK Watching"]  
        TSFiles["*.ts files"]
        ASConfig["asconfig.json"]
        TSConfig["tsconfig.json"]
        Package["package.json"]
        ASExclude["Excludes: node_modules/**"]
    end
    
    subgraph Common["Common Files"]
        Manifest["modus.json"]
        EnvFiles[".env files"]
    end
    
    subgraph Actions["Rebuild Actions"]
        CodeChange["Source Code Change"] --> FullRebuild["Full Application Rebuild"]
        ManifestChange["Manifest Change"] --> CopyManifest["Copy to Build Directory"]
        EnvChange["Environment Change"] --> CopyEnv["Copy to Build Directory"]
    end
    
    Go --> Actions
    AS --> Actions
    Common --> Actions
```

The file watcher uses different strategies based on the type of change:
- Source code changes trigger a full rebuild
- Manifest changes are copied to the build directory for runtime reload
- Environment file changes are synchronized without rebuilding

Sources: [cli/src/commands/dev/index.ts:300-359](), [cli/src/commands/dev/index.ts:366-385]()

## Next Steps

After completing this tutorial, you can:

1. **Explore Examples**: Examine the SDK example projects for common patterns like database connections, AI model integration, and HTTP requests
2. **Configure Connections**: Learn about connecting to external services in [Connections and Secrets](#6.2)
3. **Deploy Applications**: Understand production deployment options in [Docker Deployment](#8.1)
4. **Debug Applications**: Set up debugging workflows in [Development Environment](#7.1)

The Modus framework provides a comprehensive platform for building WebAssembly-based applications with automatic GraphQL API generation, making it easy to create scalable, high-performance services.

Sources: [CHANGELOG.md:504-562](), [cli/src/commands/new/index.ts:371-378]()

---

# Page: Modus CLI

# Modus CLI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [cli/package-lock.json](cli/package-lock.json)
- [cli/package.json](cli/package.json)
- [cli/src/commands/build/index.ts](cli/src/commands/build/index.ts)
- [cli/src/commands/dev/index.ts](cli/src/commands/dev/index.ts)
- [cli/src/commands/info/index.ts](cli/src/commands/info/index.ts)
- [cli/src/commands/new/index.ts](cli/src/commands/new/index.ts)
- [cli/src/commands/runtime/install/index.ts](cli/src/commands/runtime/install/index.ts)
- [cli/src/commands/runtime/list/index.ts](cli/src/commands/runtime/list/index.ts)
- [cli/src/commands/runtime/remove/index.ts](cli/src/commands/runtime/remove/index.ts)
- [cli/src/commands/sdk/install/index.ts](cli/src/commands/sdk/install/index.ts)
- [cli/src/commands/sdk/list/index.ts](cli/src/commands/sdk/list/index.ts)
- [cli/src/commands/sdk/remove/index.ts](cli/src/commands/sdk/remove/index.ts)
- [cli/src/custom/help.ts](cli/src/custom/help.ts)
- [cli/src/util/installer.ts](cli/src/util/installer.ts)
- [cli/src/util/systemVersions.ts](cli/src/util/systemVersions.ts)
- [runtime/languages/assemblyscript/testdata/build/testdata.wasm](runtime/languages/assemblyscript/testdata/build/testdata.wasm)
- [runtime/languages/assemblyscript/testdata/package-lock.json](runtime/languages/assemblyscript/testdata/package-lock.json)
- [sdk/assemblyscript/templates/default/package-lock.json](sdk/assemblyscript/templates/default/package-lock.json)
- [sdk/assemblyscript/templates/default/package.json](sdk/assemblyscript/templates/default/package.json)
- [tools/release-info/package-lock.json](tools/release-info/package-lock.json)
- [tools/release-info/package.json](tools/release-info/package.json)

</details>



The Modus CLI is the primary developer tool for creating, building, and managing Modus applications. It provides commands for project creation, SDK and runtime management, local development, and building WebAssembly modules from Go and AssemblyScript code.

For information about the Modus Runtime system that executes the applications, see [Modus Runtime](#5). For details about the SDKs themselves, see [Software Development Kits](#4).

## CLI Architecture

The Modus CLI is built using the oclif framework and implemented in TypeScript. It manages local installations of SDKs and runtimes, handles project templates, and orchestrates the development workflow.

### Core CLI Components

```mermaid
graph TB
    CLI["@hypermode/modus-cli"]
    
    subgraph "Command Categories"
        ProjectCommands["Project Commands"]
        SDKCommands["SDK Commands"] 
        RuntimeCommands["Runtime Commands"]
        InfoCommands["Info Commands"]
    end
    
    subgraph "Project Commands"
        NewCommand["NewCommand"]
        DevCommand["DevCommand"]
        BuildCommand["BuildCommand"]
    end
    
    subgraph "SDK Commands"
        SDKInstall["SDKInstallCommand"]
        SDKRemove["SDKRemoveCommand"]
        SDKList["SDKListCommand"]
    end
    
    subgraph "Runtime Commands"
        RuntimeInstall["RuntimeInstallCommand"]
        RuntimeRemove["RuntimeRemoveCommand"]
        RuntimeList["RuntimeListCommand"]
    end
    
    subgraph "Info Commands"
        InfoCommand["InfoCommand"]
    end
    
    subgraph "Utilities"
        VersionInfo["versioninfo.ts"]
        Installer["installer.ts"]
        SystemVersions["systemVersions.ts"]
        AppInfo["appinfo.ts"]
    end
    
    subgraph "Custom Components"
        Help["CustomHelp"]
        Header["getHeader()"]
        Globals["globals.ts"]
    end
    
    CLI --> ProjectCommands
    CLI --> SDKCommands
    CLI --> RuntimeCommands
    CLI --> InfoCommands
    
    ProjectCommands --> VersionInfo
    SDKCommands --> Installer
    RuntimeCommands --> Installer
    InfoCommands --> SystemVersions
    
    NewCommand --> AppInfo
    DevCommand --> SystemVersions
    BuildCommand --> AppInfo
```

Sources: [cli/package.json:1-89](), [cli/src/commands/](), [cli/src/util/](), [cli/src/custom/]()

### File System Organization

The CLI manages a local directory structure for storing SDKs, runtimes, and project templates:

```mermaid
graph TD
    ModusHome["MODUS_HOME or ~/.modus"]
    
    subgraph "SDK Storage"
        SDKDir["sdks/"]
        GoSDK["go/v{version}/"]
        ASSDK["assemblyscript/v{version}/"]
        Templates["templates.tar.gz"]
        SDKJson["sdk.json"]
        BuildTools["Build Tools"]
    end
    
    subgraph "Runtime Storage"
        RuntimeDir["runtimes/"]
        RuntimeVer["v{version}/"]
        RuntimeBinary["modus_runtime(.exe)"]
    end
    
    subgraph "Go SDK Tools"
        GoModusBuild["modus-go-build"]
    end
    
    subgraph "AS SDK Tools"
        ASModusBuild["modus-as-build"]
    end
    
    ModusHome --> SDKDir
    ModusHome --> RuntimeDir
    
    SDKDir --> GoSDK
    SDKDir --> ASSDK
    
    GoSDK --> Templates
    GoSDK --> SDKJson
    GoSDK --> GoModusBuild
    
    ASSDK --> Templates
    ASSDK --> SDKJson
    ASSDK --> ASModusBuild
    
    RuntimeDir --> RuntimeVer
    RuntimeVer --> RuntimeBinary
```

Sources: [cli/src/util/versioninfo.ts:1-67](), [cli/src/util/installer.ts:1-116]()

## Command Structure

The CLI follows a hierarchical command structure with top-level commands and sub-commands organized by functionality.

### Primary Commands

| Command | Purpose | Implementation |
|---------|---------|----------------|
| `modus new` | Create new Modus applications | [NewCommand]() |
| `modus dev` | Local development server | [DevCommand]() |
| `modus build` | Build applications | [BuildCommand]() |
| `modus info` | System information | [InfoCommand]() |

### SDK Management Commands

| Command | Purpose | Implementation |
|---------|---------|----------------|
| `modus sdk install` | Install SDK versions | [SDKInstallCommand]() |
| `modus sdk remove` | Remove SDK versions | [SDKRemoveCommand]() |
| `modus sdk list` | List installed SDKs | [SDKListCommand]() |

### Runtime Management Commands

| Command | Purpose | Implementation |
|---------|---------|----------------|
| `modus runtime install` | Install runtime versions | [RuntimeInstallCommand]() |
| `modus runtime remove` | Remove runtime versions | [RuntimeRemoveCommand]() |
| `modus runtime list` | List installed runtimes | [RuntimeListCommand]() |

Sources: [cli/src/commands/](), [cli/package.json:61-84]()

### Command Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant CLI["@hypermode/modus-cli"]
    participant VersionInfo["versioninfo.ts"]
    participant Installer["installer.ts"]
    participant GitHub["GitHub Releases"]
    participant FileSystem["Local FileSystem"]
    
    User->>CLI: "modus sdk install go"
    CLI->>VersionInfo: "getLatestSdkVersion()"
    VersionInfo->>GitHub: "Fetch release info"
    GitHub->>VersionInfo: "Return version info"
    CLI->>Installer: "installSDK()"
    Installer->>GitHub: "Download SDK archive"
    GitHub->>Installer: "SDK tar.gz"
    Installer->>FileSystem: "Extract to ~/.modus/sdks/"
    CLI->>User: "Installation complete"
```

Sources: [cli/src/commands/sdk/install/index.ts:1-208](), [cli/src/util/versioninfo.ts:1-67](), [cli/src/util/installer.ts:1-116]()

## SDK Management

The CLI manages two types of SDKs: Go and AssemblyScript. Each SDK includes templates, build tools, and compatibility information.

### SDK Installation Process

```mermaid
graph LR
    Request["SDK Install Request"]
    Version["Version Resolution"]
    Download["Download from GitHub"]
    Extract["Extract Archive"]
    BuildTools["Install Build Tools"]
    Complete["Installation Complete"]
    
    Request --> Version
    Version --> Download
    Download --> Extract
    Extract --> BuildTools
    BuildTools --> Complete
    
    subgraph "Version Resolution"
        Latest["Latest Version"]
        Specific["Specific Version"]
        Prerelease["Prerelease Flag"]
    end
    
    subgraph "Download Sources"
        SDKJson["sdk.json"]
        Templates["templates.tar.gz"]
        BuildTool["Build Tool Binary"]
    end
    
    subgraph "Extraction"
        SDKPath["~/.modus/sdks/{sdk}/{version}/"]
        TemplateFiles["Template Files"]
        Metadata["SDK Metadata"]
    end
```

Sources: [cli/src/commands/sdk/install/index.ts:86-155](), [cli/src/util/installer.ts:19-70]()

### SDK Types and Dependencies

The CLI supports two SDK types with different system requirements:

#### Go SDK Requirements
- Go >= 1.23.0
- TinyGo >= 0.35.0  
- Binaryen (wasm-opt)

#### AssemblyScript SDK Requirements
- Node.js >= 22.0
- NPM package manager

```mermaid
graph TB
    SDKValidation["SDK Prerequisite Validation"]
    
    subgraph "Go SDK"
        GoVersion["getGoVersion()"]
        TinyGoVersion["getTinyGoVersion()"]
        BinaryenVersion["getBinaryenVersion()"]
        GoValidation["Version Checks"]
    end
    
    subgraph "AssemblyScript SDK"
        NodeVersion["process.versions.node"]
        NPMVersion["getNPMVersion()"]
        ASValidation["Version Checks"]
    end
    
    SDKValidation --> GoVersion
    SDKValidation --> NodeVersion
    
    GoVersion --> GoValidation
    TinyGoVersion --> GoValidation
    BinaryenVersion --> GoValidation
    
    NodeVersion --> ASValidation
    NPMVersion --> ASValidation
```

Sources: [cli/src/commands/new/index.ts:183-269](), [cli/src/util/systemVersions.ts:1-67](), [cli/src/custom/globals.ts:1-67]()

## Runtime Management

The CLI downloads and manages Modus Runtime binaries that execute WebAssembly modules. Runtime versions are matched to SDK compatibility requirements.

### Runtime Installation and Compatibility

```mermaid
graph TB
    SDKInstall["SDK Installation"]
    CompatCheck["findLatestCompatibleRuntimeVersion()"]
    RuntimeInstall["Runtime Installation"]
    
    subgraph "Compatibility Matrix"
        CompatFile["compatibility.json"]
        SDKVersion["SDK Version"]
        RuntimeVersion["Runtime Version"]
        PrereleaseFlag["Prerelease Support"]
    end
    
    subgraph "Runtime Storage"
        RuntimePath["~/.modus/runtimes/v{version}/"]
        RuntimeBinary["modus_runtime(.exe)"]
        RuntimeMetadata["Runtime Info"]
    end
    
    SDKInstall --> CompatCheck
    CompatCheck --> CompatFile
    CompatFile --> RuntimeInstall
    RuntimeInstall --> RuntimePath
    RuntimePath --> RuntimeBinary
```

Sources: [cli/src/commands/sdk/install/index.ts:156-172](), [cli/src/util/versioninfo.ts:1-67](), [cli/src/util/installer.ts:71-116]()

## Development Workflow

The CLI provides a complete development workflow from project creation to local execution with hot reloading.

### Project Creation Workflow

```mermaid
sequenceDiagram
    participant User
    participant NewCommand["NewCommand"]
    participant Templates["Template System"]
    participant SDK["SDK Tools"]
    participant Git["Git Repository"]
    
    User->>NewCommand: "modus new my-app --sdk go"
    NewCommand->>NewCommand: "validateSdkPrereq()"
    NewCommand->>Templates: "Extract template"
    Templates->>NewCommand: "Template files"
    NewCommand->>SDK: "go mod edit -module my-app"
    SDK->>NewCommand: "Module updated"
    NewCommand->>Git: "git init && git commit"
    Git->>NewCommand: "Repository created"
    NewCommand->>User: "Project ready"
```

Sources: [cli/src/commands/new/index.ts:271-378](), [cli/src/util/tar.ts:1-67]()

### Development Server Architecture

The `modus dev` command provides a local development environment with file watching and automatic rebuilding:

```mermaid
graph TB
    DevCommand["DevCommand"]
    FileWatcher["chokidar Watchers"]
    BuildProcess["Build Process"]
    RuntimeProcess["Runtime Process"]
    
    subgraph "File Watching"
        AppCode["App Code Changes"]
        Manifest["modus.json Changes"]
        EnvFiles[".env File Changes"]
    end
    
    subgraph "Build Triggers"
        GoFiles["**/*.go, **/go.mod"]
        ASFiles["**/*.ts, **/package.json"]
        ExcludePatterns["node_modules/**, build/**"]
    end
    
    subgraph "Runtime Integration"
        RuntimeArgs["-appPath build/ -refresh=1s"]
        EnvVars["MODUS_ENV=dev"]
        ProcessSpawn["spawn(modus_runtime)"]
    end
    
    DevCommand --> FileWatcher
    FileWatcher --> AppCode
    FileWatcher --> Manifest
    FileWatcher --> EnvFiles
    
    AppCode --> BuildProcess
    BuildProcess --> RuntimeProcess
    
    RuntimeProcess --> ProcessSpawn
```

Sources: [cli/src/commands/dev/index.ts:1-398](), [cli/src/commands/dev/index.ts:366-385](), [cli/src/commands/dev/index.ts:300-359]()

### Build Process Integration

```mermaid
graph LR
    BuildCommand["BuildCommand"]
    SDKDetection["SDK Detection"]
    BuildTool["SDK Build Tool"]
    Output["Build Output"]
    
    subgraph "Go Build"
        GoModusBuild["modus-go-build"]
        TinyGoCompile["TinyGo Compilation"]
        WASMOutput["WebAssembly Module"]
    end
    
    subgraph "AssemblyScript Build"
        ASModusBuild["modus-as-build"]
        ASCCompile["AssemblyScript Compilation"]
        WASMOutput2["WebAssembly Module"]
    end
    
    BuildCommand --> SDKDetection
    SDKDetection --> GoModusBuild
    SDKDetection --> ASModusBuild
    
    GoModusBuild --> TinyGoCompile
    TinyGoCompile --> WASMOutput
    
    ASModusBuild --> ASCCompile
    ASCCompile --> WASMOutput2
```

Sources: [cli/src/commands/build/index.ts:1-116](), [cli/src/commands/build/index.ts:68-95]()

## Version Management

The CLI implements sophisticated version management for SDKs and runtimes, including support for prerelease versions and compatibility matrices.

### Version Resolution System

```mermaid
graph TB
    VersionRequest["Version Request"]
    
    subgraph "Resolution Types"
        Latest["latest"]
        Specific["v1.2.3"]
        Prerelease["--prerelease"]
    end
    
    subgraph "Version Sources"
        GitHub["GitHub Releases API"]
        LocalCache["Local Installation"]
        CompatMatrix["compatibility.json"]
    end
    
    subgraph "Version Validation"
        SemverCheck["semver.valid()"]
        ExistsCheck["releaseExists()"]
        CompatCheck["isCompatible()"]
    end
    
    VersionRequest --> Latest
    VersionRequest --> Specific
    VersionRequest --> Prerelease
    
    Latest --> GitHub
    Specific --> ExistsCheck
    Prerelease --> GitHub
    
    GitHub --> CompatMatrix
    CompatMatrix --> CompatCheck
```

Sources: [cli/src/util/versioninfo.ts:1-67](), [cli/src/commands/sdk/install/index.ts:89-137]()

The CLI provides a comprehensive development environment for Modus applications, managing the entire toolchain from SDK installation through local development and building. Its architecture separates concerns between project management, SDK/runtime management, and development workflow orchestration.

---

# Page: CLI Commands Reference

# CLI Commands Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [cli/src/commands/build/index.ts](cli/src/commands/build/index.ts)
- [cli/src/commands/dev/index.ts](cli/src/commands/dev/index.ts)
- [cli/src/commands/info/index.ts](cli/src/commands/info/index.ts)
- [cli/src/commands/new/index.ts](cli/src/commands/new/index.ts)
- [cli/src/commands/runtime/install/index.ts](cli/src/commands/runtime/install/index.ts)
- [cli/src/commands/runtime/list/index.ts](cli/src/commands/runtime/list/index.ts)
- [cli/src/commands/runtime/remove/index.ts](cli/src/commands/runtime/remove/index.ts)
- [cli/src/commands/sdk/install/index.ts](cli/src/commands/sdk/install/index.ts)
- [cli/src/commands/sdk/list/index.ts](cli/src/commands/sdk/list/index.ts)
- [cli/src/commands/sdk/remove/index.ts](cli/src/commands/sdk/remove/index.ts)
- [cli/src/custom/help.ts](cli/src/custom/help.ts)
- [cli/src/util/installer.ts](cli/src/util/installer.ts)
- [cli/src/util/systemVersions.ts](cli/src/util/systemVersions.ts)

</details>



This document provides a comprehensive reference for all Modus CLI commands, their usage patterns, command-line arguments, and implementation details. The Modus CLI serves as the primary developer interface for creating, building, running, and managing Modus applications and their dependencies.

For information about setting up the development environment and VS Code debugging, see [Development Environment](#7.1). For details about CI/CD integration with these commands, see [CI/CD Integration](#8.2).

## CLI Architecture Overview

The Modus CLI is built using the OCLIF framework and implements a hierarchical command structure with grouped subcommands. The CLI manages two primary types of components: SDKs (for building applications) and runtimes (for executing applications).

```mermaid
graph TD
    CLI["modus CLI"] --> RootCommands["Root Commands"]
    CLI --> SDKCommands["SDK Commands"] 
    CLI --> RuntimeCommands["Runtime Commands"]
    
    RootCommands --> NewCmd["new"]
    RootCommands --> DevCmd["dev"] 
    RootCommands --> BuildCmd["build"]
    RootCommands --> InfoCmd["info"]
    
    SDKCommands --> SDKInstall["sdk install"]
    SDKCommands --> SDKRemove["sdk remove"]
    SDKCommands --> SDKList["sdk list"]
    
    RuntimeCommands --> RuntimeInstall["runtime install"]
    RuntimeCommands --> RuntimeRemove["runtime remove"] 
    RuntimeCommands --> RuntimeList["runtime list"]
    
    NewCmd --> Templates["Project Templates"]
    DevCmd --> WatchSystem["File Watching"]
    BuildCmd --> Compilers["SDK Compilers"]
    
    SDKInstall --> Downloader["GitHub Release Downloader"]
    RuntimeInstall --> Downloader
```

Sources: [cli/src/custom/help.ts:17-90](), [cli/src/commands/new/index.ts:36-39](), [cli/src/commands/dev/index.ts:34-69]()

## Command Categories

The CLI organizes commands into logical groups based on their primary function:

| Category | Commands | Purpose |
|----------|----------|---------|
| **Application Lifecycle** | `new`, `dev`, `build` | Create, develop, and build Modus applications |
| **SDK Management** | `sdk install`, `sdk remove`, `sdk list` | Manage development SDKs (Go, AssemblyScript) |
| **Runtime Management** | `runtime install`, `runtime remove`, `runtime list` | Manage execution runtimes |
| **System Information** | `info` | Display system and installation status |

## Core Application Commands

### modus new

Creates a new Modus application from templates with interactive setup.

**Syntax:**
```bash
modus new [--name <app-name>] [--dir <directory>] [--sdk <sdk-type>] [--no-git] [--no-prompt] [--prerelease]
```

**Key Implementation Details:**
- Validates SDK prerequisites before project creation
- Downloads and extracts project templates from SDK packages
- Initializes Git repository by default (unless `--no-git` specified)
- Supports both Go and AssemblyScript SDKs
- Automatically installs required SDK version if missing

```mermaid
sequenceDiagram
    participant User
    participant NewCommand["NewCommand"]
    participant SDKInstall["SDKInstallCommand"] 
    participant Installer["installer"]
    participant FileSystem["File System"]
    
    User->>NewCommand: "modus new my-app --sdk go"
    NewCommand->>NewCommand: "validateSdkPrereq()"
    NewCommand->>SDKInstall: "Install SDK if missing"
    SDKInstall->>Installer: "installSDK()"
    Installer->>FileSystem: "Download templates.tar.gz"
    NewCommand->>FileSystem: "Extract template"
    NewCommand->>FileSystem: "Initialize git repo"
    NewCommand->>User: "App created successfully"
```

Sources: [cli/src/commands/new/index.ts:78-163](), [cli/src/commands/new/index.ts:271-378]()

### modus dev

Runs a Modus application locally with hot reloading and file watching.

**Syntax:**
```bash
modus dev [<path>] [--runtime <version>] [--prerelease] [--no-build] [--no-watch] [--delay <ms>]
```

**Key Features:**
- Automatic runtime version detection and installation
- File watching for source code, manifest, and environment files
- Hot reloading with configurable delay
- Integration with Hypermode API keys for model access
- Cross-platform runtime process management

The dev command implements sophisticated file watching patterns based on SDK type:

| SDK | Watched Files | Excluded Files |
|-----|---------------|----------------|
| **Go** | `**/*.go`, `**/go.mod` | `**/*_test.go`, `**/*_generated.go` |
| **AssemblyScript** | `**/*.ts`, `**/asconfig.json`, `**/package.json` | `node_modules/**` |

Sources: [cli/src/commands/dev/index.ts:71-205](), [cli/src/commands/dev/index.ts:366-385]()

### modus build

Compiles a Modus application using the appropriate SDK compiler.

**Syntax:**
```bash
modus build [<path>]
```

**Build Process:**
1. Validates `modus.json` manifest exists
2. Installs required SDK version if missing
3. Invokes SDK-specific build tools:
   - **Go**: Uses `modus-go-build` executable
   - **AssemblyScript**: Uses `npx modus-as-build`

Sources: [cli/src/commands/build/index.ts:39-110]()

### modus info

Displays comprehensive system information including installed components and system dependencies.

**Output Includes:**
- Modus installation path and CLI version
- Operating system and architecture details
- Node.js, NPM, Go, TinyGo, and Binaryen versions
- Installed SDK and runtime versions

Sources: [cli/src/commands/info/index.ts:18-93]()

## SDK Management Commands

The SDK management commands handle installation, removal, and listing of development SDKs.

```mermaid
graph LR
    SDKManagement["SDK Management"] --> Install["sdk install"]
    SDKManagement --> Remove["sdk remove"] 
    SDKManagement --> List["sdk list"]
    
    Install --> DownloadSDK["Download from GitHub"]
    Install --> ExtractTemplates["Extract templates.tar.gz"]
    Install --> InstallBuildTools["Install Build Tools"]
    
    Remove --> ValidateRemoval["Validate Removal"]
    Remove --> DeleteSDKDir["Delete SDK Directory"]
    
    List --> ScanDirectories["Scan SDK Directories"]
    List --> DisplayVersions["Display Versions"]
    
    InstallBuildTools --> GoInstall["go install modus-go-build"]
```

Sources: [cli/src/commands/sdk/install/index.ts:22-84](), [cli/src/util/installer.ts:19-94]()

### modus sdk install

Downloads and installs Modus SDKs with automatic dependency resolution.

**Syntax:**
```bash
modus sdk install <sdk-name> [<version>] [--force] [--prerelease]
```

**Supported SDKs:**
- `go`, `golang` - Go SDK with TinyGo compiler
- `assemblyscript`, `as` - AssemblyScript SDK
- `all` - Install all available SDKs

**Installation Process:**
1. Validates internet connectivity
2. Resolves latest version if `latest` specified
3. Downloads SDK package and templates from GitHub releases
4. Installs SDK-specific build tools
5. Automatically installs compatible runtime versions

Sources: [cli/src/commands/sdk/install/index.ts:51-154]()

### modus sdk remove

Removes installed SDK versions with confirmation prompts.

**Syntax:**
```bash
modus sdk remove [<sdk-name>] [<version>] [--runtimes] [--force]
```

**Features:**
- Interactive selection when no arguments provided
- Batch removal with `all` keyword
- Optional runtime cleanup with `--runtimes` flag
- Safety confirmations unless `--force` specified

Sources: [cli/src/commands/sdk/remove/index.ts:49-195]()

### modus sdk list

Lists all installed SDK versions organized by SDK type.

Sources: [cli/src/commands/sdk/list/index.ts:22-54]()

## Runtime Management Commands

Runtime management commands control the installation and maintenance of Modus execution runtimes.

### modus runtime install

Downloads and installs Modus runtime binaries for the current platform.

**Syntax:**
```bash
modus runtime install [<version>] [--force] [--prerelease]
```

**Platform Support:**
- Windows (x64, arm64)
- macOS (x64, arm64) 
- Linux (x64, arm64)

**Installation Details:**
- Downloads platform-specific archives from GitHub releases
- Extracts runtime binaries to versioned directories
- Validates installation integrity

Sources: [cli/src/commands/runtime/install/index.ts:44-107](), [cli/src/util/installer.ts:39-63]()

### modus runtime remove

Removes installed runtime versions with safety checks.

**Syntax:**
```bash
modus runtime remove [<version>] [--force]
```

Sources: [cli/src/commands/runtime/remove/index.ts:31-119]()

### modus runtime list

Lists all installed runtime versions.

Sources: [cli/src/commands/runtime/list/index.ts:21-44]()

## Global Flags and Options

All commands support common global flags:

| Flag | Short | Description |
|------|-------|-------------|
| `--help` | `-h` | Show command help |
| `--version` | `-v` | Show CLI version |
| `--no-logo` | | Suppress header logo output |

## Command Dependencies and Flow

The CLI commands have interdependencies that create a natural workflow:

```mermaid
graph TD
    Start["Developer Starts"] --> NewProject["modus new"]
    NewProject --> CheckSDK["SDK Available?"]
    CheckSDK -->|No| InstallSDK["modus sdk install"]
    CheckSDK -->|Yes| DevWorkflow["modus dev"]
    InstallSDK --> DevWorkflow
    
    DevWorkflow --> AutoBuild["Auto Build on Changes"]
    DevWorkflow --> ManualBuild["modus build"]
    AutoBuild --> RuntimeCheck["Runtime Available?"]
    ManualBuild --> RuntimeCheck
    RuntimeCheck -->|No| InstallRuntime["modus runtime install"]
    RuntimeCheck -->|Yes| ExecuteApp["Execute Application"]
    InstallRuntime --> ExecuteApp
    
    ExecuteApp --> DevLoop["Development Loop"]
    DevLoop --> FileWatch["File Watching"]
    FileWatch -->|Changes| AutoBuild
    FileWatch -->|No Changes| DevLoop
    
    NewProject --> InfoCheck["modus info"]
    DevWorkflow --> InfoCheck
    InfoCheck --> ListComponents["modus sdk/runtime list"]
```

**Command Execution Context:**
- Commands validate prerequisites before execution
- Missing dependencies trigger automatic installation prompts
- Version compatibility checking prevents runtime conflicts
- File system operations use platform-specific paths

Sources: [cli/src/commands/dev/index.ts:89-138](), [cli/src/commands/build/index.ts:58-60](), [cli/src/util/versioninfo.ts]()

## Error Handling and Validation

The CLI implements comprehensive error handling and validation:

**Version Validation:**
- SDK and runtime versions must follow semantic versioning
- Version strings must be prefixed with 'v'
- Prerelease versions are handled separately from stable releases

**Prerequisite Checking:**
- Go SDK requires Go ≥1.23.0, TinyGo ≥0.35.0, and Binaryen
- AssemblyScript SDK requires Node.js ≥18.0.0
- Internet connectivity required for downloads

**File System Operations:**
- Graceful handling of permission errors
- Automatic directory creation for installations
- Safe removal with recursive deletion protection

Sources: [cli/src/commands/new/index.ts:183-269](), [cli/src/util/systemVersions.ts:18-66]()

---

# Page: Version Management

# Version Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/renovate.json](.github/renovate.json)
- [.github/workflows/ci-cli-build.yml](.github/workflows/ci-cli-build.yml)
- [.github/workflows/ci-cli-lint.yml](.github/workflows/ci-cli-lint.yml)
- [.github/workflows/ci-sdk-as-build.yml](.github/workflows/ci-sdk-as-build.yml)
- [.github/workflows/ci-sdk-as-lint.yml](.github/workflows/ci-sdk-as-lint.yml)
- [.github/workflows/ci-sdk-as-test.yml](.github/workflows/ci-sdk-as-test.yml)
- [cli/eslint.config.js](cli/eslint.config.js)
- [cli/install.sh](cli/install.sh)
- [cli/src/custom/globals.ts](cli/src/custom/globals.ts)
- [cli/src/util/http.ts](cli/src/util/http.ts)
- [cli/src/util/index.ts](cli/src/util/index.ts)
- [cli/src/util/versioninfo.ts](cli/src/util/versioninfo.ts)
- [runtime/plugins/plugins.go](runtime/plugins/plugins.go)
- [sdk/assemblyscript/src/plugin.asconfig.json](sdk/assemblyscript/src/plugin.asconfig.json)
- [sdk/go/tools/modus-go-build/compiler/compiler.go](sdk/go/tools/modus-go-build/compiler/compiler.go)

</details>



This document covers how the Modus CLI manages versions of SDKs, runtime components, and the CLI itself. It explains the version resolution algorithms, compatibility checking, local storage structure, and update mechanisms used throughout the system.

For information about CLI commands that interact with version management, see [CLI Commands Reference](#3.1). For details about SDK installation and configuration, see [Software Development Kits](#4).

## Version Management Architecture

The Modus CLI implements a comprehensive version management system that handles multiple components with different release cycles and compatibility requirements.

### Version Management Components

```mermaid
graph TB
    subgraph "Version Sources"
        LatestJSON["modus-latest.json<br/>Stable Releases"]
        PreviewJSON["modus-preview.json<br/>Preview Releases"]
        AllJSON["modus-all.json<br/>All Stable Versions"]
        AllPreviewJSON["modus-preview-all.json<br/>All Preview Versions"]
    end
    
    subgraph "CLI Version Manager"
        VersionInfo["versioninfo.ts<br/>Core Version Logic"]
        FetchFunctions["fetchModusLatest()<br/>fetchModusPreview()<br/>fetchModusAll()"]
        ResolutionFunctions["getLatestSdkVersion()<br/>getLatestRuntimeVersion()<br/>findCompatibleInstalledRuntimeVersion()"]
    end
    
    subgraph "Local Storage"
        ModusHome["~/.modus/<br/>Base Directory"]
        SDKStorage["sdk/{sdk}/{version}/<br/>SDK Installations"]
        RuntimeStorage["runtime/{version}/<br/>Runtime Installations"]
        SDKInfo["sdk.json<br/>SDK Metadata & Compatibility"]
    end
    
    subgraph "Managed Components"
        CLI["Modus CLI<br/>NPM Package"]
        GoSDK["Go SDK<br/>TinyGo + Build Tools"]
        ASSDK["AssemblyScript SDK<br/>TypeScript/WASM Tools"]
        Runtime["Modus Runtime<br/>Binary Executables"]
    end
    
    LatestJSON --> FetchFunctions
    PreviewJSON --> FetchFunctions
    AllJSON --> FetchFunctions
    AllPreviewJSON --> FetchFunctions
    
    FetchFunctions --> ResolutionFunctions
    ResolutionFunctions --> SDKStorage
    ResolutionFunctions --> RuntimeStorage
    
    SDKInfo --> ResolutionFunctions
    
    CLI --> VersionInfo
    GoSDK --> SDKStorage
    ASSDK --> SDKStorage
    Runtime --> RuntimeStorage
```

Sources: [cli/src/util/versioninfo.ts:1-320](), [cli/src/custom/globals.ts:14]()

### Version Data Flow

```mermaid
sequenceDiagram
    participant User as "User Command"
    participant CLI as "CLI Process"
    participant VersionInfo as "versioninfo.ts"
    participant ReleaseAPI as "releases.hypermode.com"
    participant LocalFS as "~/.modus/"
    
    User->>CLI: modus sdk install go@latest
    CLI->>VersionInfo: getLatestSdkVersion("Go", false)
    VersionInfo->>ReleaseAPI: GET modus-latest.json
    ReleaseAPI->>VersionInfo: {"sdk/go": "v1.2.3", ...}
    VersionInfo->>VersionInfo: Extract version from response
    VersionInfo->>CLI: Return "v1.2.3"
    CLI->>VersionInfo: sdkVersionIsInstalled("Go", "v1.2.3")
    VersionInfo->>LocalFS: Check ~/.modus/sdk/go/v1.2.3/
    LocalFS->>VersionInfo: Directory exists/missing
    VersionInfo->>CLI: Return installation status
    CLI->>CLI: Download and install if needed
    CLI->>LocalFS: Create ~/.modus/sdk/go/v1.2.3/sdk.json
```

Sources: [cli/src/util/versioninfo.ts:138-147](), [cli/src/util/versioninfo.ts:183-206]()

## Version Storage Structure

The CLI maintains a structured directory layout for managing different component versions locally.

### Local Storage Layout

| Path Pattern | Purpose | Example |
|-------------|---------|---------|
| `~/.modus/` | Base directory for all Modus data | `/home/user/.modus/` |
| `sdk/{sdk}/{version}/` | SDK installation directory | `sdk/go/v1.2.3/` |
| `runtime/{version}/` | Runtime installation directory | `runtime/v0.5.1/` |
| `sdk/{sdk}/{version}/sdk.json` | SDK metadata and compatibility info | Contains runtime version constraints |

```mermaid
graph TD
    ModusHome["~/.modus/"]
    
    subgraph "SDK Storage"
        SDKDir["sdk/"]
        GoDir["go/"]
        ASDir["assemblyscript/"]
        GoV1["v1.2.3/"]
        GoV2["v1.2.4/"]
        ASV1["v0.18.0/"]
        GoSDKJSON["sdk.json"]
        GoBuildTool["modus-go-build"]
    end
    
    subgraph "Runtime Storage"
        RuntimeDir["runtime/"]
        RuntimeV1["v0.5.1/"]
        RuntimeV2["v0.5.2/"]
        RuntimeBin["modus-runtime"]
    end
    
    ModusHome --> SDKDir
    ModusHome --> RuntimeDir
    
    SDKDir --> GoDir
    SDKDir --> ASDir
    GoDir --> GoV1
    GoDir --> GoV2
    ASDir --> ASV1
    
    GoV1 --> GoSDKJSON
    GoV1 --> GoBuildTool
    
    RuntimeDir --> RuntimeV1
    RuntimeDir --> RuntimeV2
    RuntimeV1 --> RuntimeBin
```

Sources: [cli/src/util/versioninfo.ts:18-24](), [cli/src/custom/globals.ts:14]()

## Version Resolution and Compatibility

The CLI implements sophisticated version resolution that considers compatibility constraints between SDKs and runtime versions.

### SDK-Runtime Compatibility System

```mermaid
graph TB
    subgraph "SDK Installation"
        SDKVersion["SDK v1.2.3"]
        SDKJson["sdk.json"]
        RuntimeConstraint["runtime.version: '^0.5.0'"]
    end
    
    subgraph "Compatibility Check Functions"
        FindCompatible["findCompatibleInstalledRuntimeVersion()"]
        FindLatest["findLatestCompatibleRuntimeVersion()"]
        SemverValidation["semver.satisfies()"]
    end
    
    subgraph "Runtime Resolution"
        InstalledRuntimes["getInstalledRuntimeVersions()"]
        AllRuntimes["getAllRuntimeVersions()"]
        CompatibleMatch["v0.5.2 (matches ^0.5.0)"]
    end
    
    SDKVersion --> SDKJson
    SDKJson --> RuntimeConstraint
    RuntimeConstraint --> FindCompatible
    RuntimeConstraint --> FindLatest
    
    FindCompatible --> InstalledRuntimes
    FindLatest --> AllRuntimes
    
    FindCompatible --> SemverValidation
    FindLatest --> SemverValidation
    
    SemverValidation --> CompatibleMatch
```

Sources: [cli/src/util/versioninfo.ts:253-285](), [cli/src/util/versioninfo.ts:287-319]()

### Version Resolution Algorithm

The CLI uses a multi-step resolution process for finding compatible versions:

1. **Exact Version Match**: If `sdk.json` specifies an exact version (e.g., `"0.5.1"`), check if that version is available
2. **Range Satisfaction**: If `sdk.json` specifies a range (e.g., `"^0.5.0"`), find the latest version that satisfies the constraint
3. **Prerelease Fallback**: If no stable versions match and prereleases are not explicitly requested, try prerelease versions
4. **Installation Priority**: Prefer already-installed versions over downloading new ones when multiple versions satisfy constraints

```mermaid
flowchart TD
    Start["SDK Version Selected"]
    ReadSDKJson["Read sdk.json runtime.version"]
    CheckExact{"Is exact version?<br/>(semver.valid())"}
    CheckInstalled{"Is version installed?<br/>(runtimeVersionIsInstalled())"}
    ReturnExact["Return exact version"]
    CheckRange{"Is valid range?<br/>(semver.validRange())"}
    GetInstalledVersions["getInstalledRuntimeVersions()"]
    FilterCompatible["Filter by semver.satisfies()"]
    CheckStableFound{"Stable versions found?"}
    TryPrerelease["Include prereleases in filter"]
    SortVersions["Sort by semver.rsort()"]
    ReturnLatest["Return latest compatible"]
    Error["Throw compatibility error"]
    
    Start --> ReadSDKJson
    ReadSDKJson --> CheckExact
    CheckExact -->|Yes| CheckInstalled
    CheckInstalled -->|Yes| ReturnExact
    CheckInstalled -->|No| Error
    CheckExact -->|No| CheckRange
    CheckRange -->|Yes| GetInstalledVersions
    CheckRange -->|No| Error
    GetInstalledVersions --> FilterCompatible
    FilterCompatible --> CheckStableFound
    CheckStableFound -->|Yes| SortVersions
    CheckStableFound -->|No| TryPrerelease
    TryPrerelease --> SortVersions
    SortVersions --> ReturnLatest
```

Sources: [cli/src/util/versioninfo.ts:253-285](), [cli/src/util/versioninfo.ts:299-318]()

## Version Fetching and Caching

The CLI fetches version information from Hypermode's release API and implements in-memory caching to avoid redundant requests.

### Release API Integration

```mermaid
graph LR
    subgraph "Release Endpoints"
        LatestAPI["https://releases.hypermode.com/<br/>modus-latest.json"]
        PreviewAPI["https://releases.hypermode.com/<br/>modus-preview.json"]
        AllAPI["https://releases.hypermode.com/<br/>modus-all.json"]
        AllPreviewAPI["https://releases.hypermode.com/<br/>modus-preview-all.json"]
    end
    
    subgraph "Fetch Functions"
        FetchLatest["fetchModusLatest()"]
        FetchPreview["fetchModusPreview()"]
        FetchAll["fetchModusAll()"]
        FetchAllPreview["fetchModusPreviewAll()"]
    end
    
    subgraph "Version Cache"
        VersionData["versionData object"]
        LatestCache["latest: {[key: string]: string}"]
        PreviewCache["preview: {[key: string]: string}"]
        AllCache["all: {[key: string]: string[]}"]
        AllPreviewCache["allPreview: {[key: string]: string[]}"]
    end
    
    LatestAPI --> FetchLatest
    PreviewAPI --> FetchPreview
    AllAPI --> FetchAll
    AllPreviewAPI --> FetchAllPreview
    
    FetchLatest --> LatestCache
    FetchPreview --> PreviewCache
    FetchAll --> AllCache
    FetchAllPreview --> AllPreviewCache
    
    LatestCache --> VersionData
    PreviewCache --> VersionData
    AllCache --> VersionData
    AllPreviewCache --> VersionData
```

Sources: [cli/src/util/versioninfo.ts:33-106](), [cli/src/util/http.ts:15-20]()

## Installation Validation

The CLI performs comprehensive validation to ensure installed components are complete and functional.

### SDK Installation Validation

For Go SDK installations, the CLI performs additional validation beyond directory existence:

```mermaid
flowchart TD
    CheckSDK["sdkVersionIsInstalled(sdk, version)"]
    CheckPath["Check getSdkPath(sdk, version) exists"]
    PathExists{"Directory exists?"}
    IsGoSDK{"SDK === Go?"}
    CheckBuildTool["Check modus-go-build exists"]
    BuildToolExists{"Build tool found?"}
    LogReinstall["Log: Detected incomplete installation"]
    RemoveDirectory["Remove SDK directory"]
    ReturnTrue["Return true"]
    ReturnFalse["Return false"]
    
    CheckSDK --> CheckPath
    CheckPath --> PathExists
    PathExists -->|No| ReturnFalse
    PathExists -->|Yes| IsGoSDK
    IsGoSDK -->|No| ReturnTrue
    IsGoSDK -->|Yes| CheckBuildTool
    CheckBuildTool --> BuildToolExists
    BuildToolExists -->|Yes| ReturnTrue
    BuildToolExists -->|No| LogReinstall
    LogReinstall --> RemoveDirectory
    RemoveDirectory --> ReturnFalse
```

Sources: [cli/src/util/versioninfo.ts:183-206]()

### Version Validation Process

The CLI validates component versions using semantic versioning and platform-specific checks:

| Component | Validation Method | Key Checks |
|-----------|------------------|------------|
| **Go SDK** | Directory + build tool presence | `modus-go-build` executable exists |
| **AssemblyScript SDK** | Directory existence | Basic directory structure |
| **Runtime** | Directory existence | Runtime binary present |
| **CLI** | NPM version check | Semantic version format |

Sources: [cli/src/util/versioninfo.ts:183-210](), [sdk/go/tools/modus-go-build/compiler/compiler.go:52-68]()

## Prerelease and Stable Channel Management

The CLI distinguishes between stable and prerelease versions, with fallback mechanisms for compatibility.

### Release Channel Logic

```mermaid
graph TD
    subgraph "Version Request"
        IncludePrerelease{"includePrerelease flag"}
        StableOnly["Stable versions only"]
        AllVersions["Include prereleases"]
    end
    
    subgraph "Version Sources"
        StableAPI["modus-latest.json<br/>modus-all.json"]
        PreviewAPI["modus-preview.json<br/>modus-preview-all.json"]
    end
    
    subgraph "Fallback Logic"
        CheckStable["Check stable versions"]
        StableFound{"Stable versions<br/>available?"}
        UseStable["Use stable versions"]
        FallbackPrerelease["Fallback to prereleases"]
    end
    
    IncludePrerelease -->|false| StableOnly
    IncludePrerelease -->|true| AllVersions
    
    StableOnly --> StableAPI
    AllVersions --> PreviewAPI
    
    StableAPI --> CheckStable
    CheckStable --> StableFound
    StableFound -->|Yes| UseStable
    StableFound -->|No| FallbackPrerelease
    
    FallbackPrerelease --> PreviewAPI
```

Sources: [cli/src/util/versioninfo.ts:138-147](), [cli/src/util/versioninfo.ts:241-250](), [cli/src/util/versioninfo.ts:26-31]()

The system uses `semver.prerelease()` to identify prerelease versions and `semver.rsort()` to order versions appropriately, ensuring that the latest stable version is always preferred when available.

---

# Page: Software Development Kits

# Software Development Kits

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lib/manifest/go.mod](lib/manifest/go.mod)
- [lib/metadata/go.mod](lib/metadata/go.mod)
- [lib/wasmextractor/go.mod](lib/wasmextractor/go.mod)
- [runtime/go.mod](runtime/go.mod)
- [runtime/go.sum](runtime/go.sum)
- [runtime/languages/golang/testdata/go.mod](runtime/languages/golang/testdata/go.mod)
- [runtime/languages/golang/testdata/go.sum](runtime/languages/golang/testdata/go.sum)
- [sdk/assemblyscript/examples/anthropic-functions/package-lock.json](sdk/assemblyscript/examples/anthropic-functions/package-lock.json)
- [sdk/assemblyscript/examples/classification/package-lock.json](sdk/assemblyscript/examples/classification/package-lock.json)
- [sdk/assemblyscript/examples/dgraph/package-lock.json](sdk/assemblyscript/examples/dgraph/package-lock.json)
- [sdk/assemblyscript/examples/embedding/package-lock.json](sdk/assemblyscript/examples/embedding/package-lock.json)
- [sdk/assemblyscript/examples/graphql/package-lock.json](sdk/assemblyscript/examples/graphql/package-lock.json)
- [sdk/assemblyscript/examples/http/package-lock.json](sdk/assemblyscript/examples/http/package-lock.json)
- [sdk/assemblyscript/examples/postgresql/package-lock.json](sdk/assemblyscript/examples/postgresql/package-lock.json)
- [sdk/assemblyscript/examples/textgeneration/package-lock.json](sdk/assemblyscript/examples/textgeneration/package-lock.json)
- [sdk/assemblyscript/src/package-lock.json](sdk/assemblyscript/src/package-lock.json)
- [sdk/assemblyscript/src/package.json](sdk/assemblyscript/src/package.json)
- [sdk/go/go.mod](sdk/go/go.mod)
- [sdk/go/go.sum](sdk/go/go.sum)
- [sdk/go/templates/default/go.mod](sdk/go/templates/default/go.mod)
- [sdk/go/templates/default/go.sum](sdk/go/templates/default/go.sum)

</details>



This document covers the available Software Development Kits (SDKs) provided by Modus for building WebAssembly applications. The SDKs enable developers to write functions in their preferred programming language that compile to WebAssembly modules executed by the Modus Runtime. 

For information about the CLI tools used to manage SDKs, see [Modus CLI](#3). For details about the runtime that executes SDK-generated WebAssembly modules, see [Modus Runtime](#5).

## SDK Architecture Overview

Modus provides multiple language SDKs that follow a consistent architecture pattern. Each SDK compiles source code to WebAssembly modules that integrate with the Modus Runtime through a standardized interface.

```mermaid
graph TB
    subgraph "Developer Code"
        GoCode["Go Functions"]
        ASCode["AssemblyScript Functions"]
    end
    
    subgraph "SDK Build Systems"
        GoSDK["Go SDK<br/>TinyGo Compiler"]
        ASSDK["AssemblyScript SDK<br/>asc Compiler"]
    end
    
    subgraph "WebAssembly Layer"
        WASM1["Module 1.wasm"]
        WASM2["Module 2.wasm"]
        WASMn["Module N.wasm"]
    end
    
    subgraph "Modus Runtime"
        WasmHost["WebAssembly Host<br/>Wazero Runtime"]
        GraphQL["GraphQL Schema Generator"]
        Metadata["Function Metadata Extractor"]
    end
    
    GoCode --> GoSDK
    ASCode --> ASSDK
    GoSDK --> WASM1
    ASSDK --> WASM2
    
    WASM1 --> WasmHost
    WASM2 --> WasmHost
    WASMn --> WasmHost
    
    WasmHost --> GraphQL
    WasmHost --> Metadata
```

Sources: [runtime/go.mod:26-28](), [sdk/go/go.mod:1-34](), [sdk/assemblyscript/src/package.json:1-60]()

## Available SDKs

Modus currently provides two production-ready SDKs with distinct characteristics and use cases.

### Go SDK

The Go SDK leverages TinyGo to compile Go source code to WebAssembly. It provides a familiar Go development experience with automatic type mapping to GraphQL schemas.

```mermaid
graph LR
    subgraph "Go SDK Components"
        Templates["Project Templates<br/>sdk/go/templates/"]
        GoMod["go.mod Dependencies<br/>manifest, wasmextractor"]
        Compiler["TinyGo Build Pipeline"]
    end
    
    subgraph "Key Libraries"
        Manifest["github.com/hypermodeinc/modus/lib/manifest"]
        WasmExtractor["github.com/hypermodeinc/modus/lib/wasmextractor"]
        Metadata["github.com/hypermodeinc/modus/lib/metadata"]
    end
    
    Templates --> GoMod
    GoMod --> Manifest
    GoMod --> WasmExtractor
    Compiler --> Metadata
```

**Key Features:**
- Full Go language support via TinyGo
- Automatic GraphQL schema generation from Go types
- Built-in support for common Go patterns and standard library subset
- Template-based project initialization

**Module Configuration:**
- Module path: `github.com/hypermodeinc/modus/sdk/go`
- Go version: `1.23.1` with toolchain `go1.24.4`
- Key dependencies: manifest library, wasmextractor library

Sources: [sdk/go/go.mod:1-34](), [sdk/go/templates/default/go.mod:1-10]()

### AssemblyScript SDK

The AssemblyScript SDK provides a TypeScript-like development experience that compiles directly to optimized WebAssembly without requiring a Go toolchain.

```mermaid
graph LR
    subgraph "AssemblyScript SDK Components"
        PackageJson["package.json<br/>@hypermode/modus-sdk-as"]
        BuildPlugin["modus-as-build<br/>Custom Build Plugin"]
        Transform["TypeScript Transform<br/>Metadata Extraction"]
    end
    
    subgraph "Build Dependencies" 
        ASC["assemblyscript ^0.28.2"]
        JsonAS["json-as ^1.1.15"]
        WasiShim["@assemblyscript/wasi-shim"]
    end
    
    subgraph "Development Tools"
        ESLint["ESLint Configuration"]
        Prettier["Prettier Formatting"]
        TypeScript["TypeScript ^5.8.3"]
    end
    
    PackageJson --> BuildPlugin
    BuildPlugin --> Transform
    Transform --> ASC
    ASC --> JsonAS
    ASC --> WasiShim
```

**Key Features:**
- TypeScript-like syntax with WebAssembly-native compilation
- Custom build plugin for Modus integration
- JSON serialization support via `json-as`
- Comprehensive linting and formatting tools

**Package Configuration:**
- Package name: `@hypermode/modus-sdk-as`
- Node.js requirement: `>=22`
- Build command: `modus-as-build` binary

Sources: [sdk/assemblyscript/src/package.json:1-60](), [sdk/assemblyscript/src/package-lock.json:1-50]()

## SDK Selection Guidance

Choose the appropriate SDK based on your team's experience and project requirements:

| Factor | Go SDK | AssemblyScript SDK |
|--------|--------|-------------------|
| **Language Familiarity** | Go developers | TypeScript/JavaScript developers |
| **Type System** | Strong static typing | TypeScript-like typing |
| **Compilation Target** | TinyGo → WASM | Direct WASM compilation |
| **Standard Library** | TinyGo standard library subset | AssemblyScript standard library |
| **Toolchain** | Requires Go/TinyGo installation | Node.js-based toolchain |
| **Performance** | Optimized via TinyGo | Direct WASM optimization |

Sources: [sdk/go/go.mod:3-5](), [sdk/assemblyscript/src/package.json:31-33]()

## Development Workflow

Both SDKs follow a consistent development workflow managed through the Modus CLI:

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant CLI as "modus CLI"
    participant SDK as "SDK Build System"
    participant Runtime as "Modus Runtime"
    
    Dev->>CLI: "modus new my-app --sdk go"
    CLI->>SDK: "Install SDK and create template"
    SDK->>Dev: "Project structure created"
    
    Dev->>Dev: "Write application functions"
    Dev->>CLI: "modus build"
    CLI->>SDK: "Invoke SDK compiler"
    SDK->>CLI: "Generate .wasm module"
    
    Dev->>CLI: "modus dev"
    CLI->>Runtime: "Load .wasm module"
    Runtime->>Runtime: "Extract function metadata"
    Runtime->>Runtime: "Generate GraphQL schema"
    Runtime->>Dev: "API available at localhost:8686"
```

Sources: [sdk/go/templates/default/go.mod:1-10](), [sdk/assemblyscript/src/package.json:9-11]()

## Build Systems

Each SDK implements a specialized build system optimized for its target language and WebAssembly compilation requirements.

### Go SDK Build System

The Go SDK uses TinyGo for WebAssembly compilation with manifest and metadata extraction:

```mermaid
graph TB
    subgraph "Go Source Files"
        GoFunctions["*.go function files"]
        GoMod["go.mod with SDK dependency"]
    end
    
    subgraph "Build Pipeline"
        TinyGo["TinyGo Compiler"]
        ManifestLib["Manifest Library<br/>Configuration Validation"]
        WasmExtract["WASM Extractor<br/>Metadata Generation"]
    end
    
    subgraph "Output Artifacts"
        WasmModule["application.wasm"]
        Metadata["Function Metadata"]
    end
    
    GoFunctions --> TinyGo
    GoMod --> ManifestLib
    TinyGo --> WasmModule
    WasmModule --> WasmExtract
    WasmExtract --> Metadata
    ManifestLib --> Metadata
```

Sources: [sdk/go/go.mod:7-10](), [runtime/languages/golang/testdata/go.mod:7-9]()

### AssemblyScript SDK Build System

The AssemblyScript SDK provides a custom build plugin that handles compilation and metadata extraction:

```mermaid
graph TB
    subgraph "AssemblyScript Source"
        ASFiles["*.ts AssemblyScript files"]
        ASConfig["asconfig.json configuration"]
    end
    
    subgraph "Build Plugin System"
        BuildPlugin["modus-as-build<br/>bin/build-plugin.js"]
        Transform["TypeScript Transform<br/>transform/lib/index.js"]
        ASCompiler["AssemblyScript Compiler"]
    end
    
    subgraph "Dependencies"
        JsonAS["json-as serialization"]
        WasiShim["WASI compatibility layer"]
        Base64["as-base64 encoding"]
    end
    
    subgraph "Output"
        WasmOut["optimized.wasm"]
        MetadataOut["extracted metadata"]
    end
    
    ASFiles --> BuildPlugin
    ASConfig --> BuildPlugin
    BuildPlugin --> Transform
    Transform --> ASCompiler
    ASCompiler --> JsonAS
    ASCompiler --> WasiShim
    ASCompiler --> Base64
    ASCompiler --> WasmOut
    Transform --> MetadataOut
```

Sources: [sdk/assemblyscript/src/package.json:9-11](), [sdk/assemblyscript/src/package.json:44-47](), [sdk/assemblyscript/src/package.json:22-28]()

## Examples and Templates

Both SDKs provide comprehensive examples demonstrating integration patterns with various external systems and services.

### Go SDK Templates

The Go SDK includes project templates for rapid application bootstrap:

- **Default Template**: Basic project structure at [sdk/go/templates/default/]()
- **Test Cases**: Runtime integration examples at [runtime/languages/golang/testdata/]()

Sources: [sdk/go/templates/default/go.mod:1-10](), [runtime/languages/golang/testdata/go.mod:1-9]()

### AssemblyScript SDK Examples

The AssemblyScript SDK provides multiple working examples covering common integration patterns:

| Example | Purpose | Location |
|---------|---------|-----------|
| **GraphQL** | GraphQL API integration | [sdk/assemblyscript/examples/graphql/]() |
| **PostgreSQL** | Database connectivity | [sdk/assemblyscript/examples/postgresql/]() |
| **HTTP** | HTTP client usage | [sdk/assemblyscript/examples/http/]() |
| **Dgraph** | Graph database integration | [sdk/assemblyscript/examples/dgraph/]() |
| **Classification** | AI model integration | [sdk/assemblyscript/examples/classification/]() |
| **Embedding** | Vector embedding generation | [sdk/assemblyscript/examples/embedding/]() |
| **Anthropic Functions** | Function calling with AI models | [sdk/assemblyscript/examples/anthropic-functions/]() |

Each example includes complete project configuration with dependencies, build scripts, and linting setup.

Sources: [sdk/assemblyscript/examples/graphql/package-lock.json:1-50](), [sdk/assemblyscript/examples/postgresql/package-lock.json:1-50](), [sdk/assemblyscript/examples/http/package-lock.json:1-50](), [sdk/assemblyscript/examples/dgraph/package-lock.json:1-50](), [sdk/assemblyscript/examples/classification/package-lock.json:1-50](), [sdk/assemblyscript/examples/embedding/package-lock.json:1-50](), [sdk/assemblyscript/examples/anthropic-functions/package-lock.json:1-50]()

---

# Page: Go SDK

# Go SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lib/manifest/go.mod](lib/manifest/go.mod)
- [lib/metadata/go.mod](lib/metadata/go.mod)
- [lib/wasmextractor/go.mod](lib/wasmextractor/go.mod)
- [runtime/go.mod](runtime/go.mod)
- [runtime/go.sum](runtime/go.sum)
- [runtime/languages/golang/testdata/go.mod](runtime/languages/golang/testdata/go.mod)
- [runtime/languages/golang/testdata/go.sum](runtime/languages/golang/testdata/go.sum)
- [sdk/go/examples/anthropic-functions/go.mod](sdk/go/examples/anthropic-functions/go.mod)
- [sdk/go/examples/auth/go.mod](sdk/go/examples/auth/go.mod)
- [sdk/go/examples/classification/go.mod](sdk/go/examples/classification/go.mod)
- [sdk/go/examples/dgraph/go.mod](sdk/go/examples/dgraph/go.mod)
- [sdk/go/examples/embedding/go.mod](sdk/go/examples/embedding/go.mod)
- [sdk/go/examples/graphql/go.mod](sdk/go/examples/graphql/go.mod)
- [sdk/go/examples/http/go.mod](sdk/go/examples/http/go.mod)
- [sdk/go/examples/postgresql/go.mod](sdk/go/examples/postgresql/go.mod)
- [sdk/go/examples/simple/go.mod](sdk/go/examples/simple/go.mod)
- [sdk/go/examples/textgeneration/go.mod](sdk/go/examples/textgeneration/go.mod)
- [sdk/go/examples/vectors/go.mod](sdk/go/examples/vectors/go.mod)
- [sdk/go/go.mod](sdk/go/go.mod)
- [sdk/go/go.sum](sdk/go/go.sum)
- [sdk/go/templates/default/go.mod](sdk/go/templates/default/go.mod)
- [sdk/go/templates/default/go.sum](sdk/go/templates/default/go.sum)

</details>



The Go SDK enables developers to build Modus applications using the Go programming language. It provides the necessary APIs, build tools, and runtime integration to compile Go functions into WebAssembly modules that execute within the Modus Runtime. The SDK handles the compilation pipeline using TinyGo, metadata extraction, and seamless integration with the GraphQL engine and agent system.

For information about the runtime that executes Go-compiled WebAssembly modules, see [Runtime Architecture](#5.1). For details about the CLI commands that manage Go SDK installations and builds, see [CLI Commands Reference](#3.1).

## Architecture Overview

The Go SDK operates as part of a larger compilation and execution pipeline that transforms Go source code into executable WebAssembly modules.

### Go SDK in the Modus Ecosystem

```mermaid
graph TB
    subgraph "Development Environment"
        GoCode["Go Source Code<br/>main.go"]
        Manifest["modus.json<br/>Application Manifest"]
        GoMod["go.mod<br/>Dependencies"]
    end
    
    subgraph "Go SDK Components"
        SDK["github.com/hypermodeinc/modus/sdk/go<br/>Core SDK Package"]
        Templates["sdk/go/templates/<br/>Project Templates"]
        Examples["sdk/go/examples/<br/>Example Applications"]
    end
    
    subgraph "Build Pipeline"
        TinyGo["TinyGo Compiler<br/>Go → WASM"]
        Extractor["lib/wasmextractor<br/>Metadata Extraction"]
        WasmModule["WebAssembly Module<br/>.wasm + metadata"]
    end
    
    subgraph "Modus Runtime"
        WasmHost["WebAssembly Host<br/>Module Loading"]
        GraphQLGen["GraphQL Schema<br/>Generation"]
        AgentSystem["Agent System<br/>Execution Context"]
    end
    
    GoCode --> SDK
    Manifest --> SDK
    GoMod --> SDK
    
    SDK --> TinyGo
    Templates --> GoCode
    Examples --> GoCode
    
    TinyGo --> WasmModule
    WasmModule --> Extractor
    Extractor --> WasmHost
    
    WasmHost --> GraphQLGen
    WasmHost --> AgentSystem
```

Sources: [sdk/go/go.mod:1-35](), [sdk/go/templates/default/go.mod:1-10](), [lib/wasmextractor/go.mod:1-6](), [runtime/go.mod:26-27]()

## Development Workflow

The Go SDK supports a streamlined development workflow from project initialization through runtime execution.

### Build and Execution Flow

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant CLI as "modus CLI"
    participant GoSDK as "Go SDK"
    participant TinyGo as "TinyGo Compiler"
    participant Runtime as "Modus Runtime"
    
    Dev->>CLI: modus new my-app --sdk go
    CLI->>GoSDK: Initialize project template
    GoSDK->>Dev: Project structure created
    
    Dev->>Dev: Write Go functions
    Dev->>CLI: modus build
    CLI->>GoSDK: Invoke build system
    GoSDK->>TinyGo: Compile Go → WASM
    TinyGo->>GoSDK: WebAssembly module
    GoSDK->>CLI: .wasm + metadata
    
    Dev->>CLI: modus dev
    CLI->>Runtime: Load WASM module
    Runtime->>Runtime: Extract function signatures
    Runtime->>Runtime: Generate GraphQL schema
    Runtime->>Dev: Local development server
```

Sources: [sdk/go/templates/default/)(), [runtime/languages/golang/testdata/go.mod:1-10]()

## SDK Structure and Components

The Go SDK is organized into several key components that provide the development experience and build functionality.

### Core SDK Package Structure

```mermaid
graph TB
    subgraph "sdk/go Package Structure"
        CoreSDK["github.com/hypermodeinc/modus/sdk/go<br/>Main SDK Module"]
        
        subgraph "Templates"
            DefaultTemplate["templates/default/<br/>Basic Project Template"]
            DefaultGoMod["templates/default/go.mod<br/>Template Dependencies"]
        end
        
        subgraph "Examples"
            SimpleEx["examples/simple/<br/>Basic Function Example"]
            HTTPEx["examples/http/<br/>HTTP Client Example"]
            PostgreSQLEx["examples/postgresql/<br/>Database Integration"]
            GraphQLEx["examples/graphql/<br/>GraphQL Operations"]
            EmbeddingEx["examples/embedding/<br/>AI Embeddings"]
            VectorsEx["examples/vectors/<br/>Vector Operations"]
            AuthEx["examples/auth/<br/>Authentication"]
            DgraphEx["examples/dgraph/<br/>Graph Database"]
            AnthropicEx["examples/anthropic-functions/<br/>AI Functions"]
            ClassificationEx["examples/classification/<br/>ML Classification"]
            TextGenEx["examples/textgeneration/<br/>Text Generation"]
        end
        
        subgraph "Dependencies"
            Manifest["lib/manifest<br/>Configuration Parsing"]
            WasmExtractor["lib/wasmextractor<br/>Metadata Extraction"]
            ExpPkg["golang.org/x/exp<br/>Experimental Features"]
            ModPkg["golang.org/x/mod<br/>Module Tools"]
            ToolsPkg["golang.org/x/tools<br/>Build Tools"]
        end
    end
    
    CoreSDK --> DefaultTemplate
    CoreSDK --> SimpleEx
    CoreSDK --> HTTPEx
    CoreSDK --> PostgreSQLEx
    CoreSDK --> Manifest
    CoreSDK --> WasmExtractor
```

Sources: [sdk/go/go.mod:1-35](), [sdk/go/templates/default/go.mod:1-10](), [sdk/go/examples/simple/go.mod:1-9](), [sdk/go/examples/http/go.mod:1-9](), [sdk/go/examples/postgresql/go.mod:1-9](), [sdk/go/examples/graphql/go.mod:1-9]()

## Compilation Process

The Go SDK uses TinyGo as the compiler to generate WebAssembly modules from Go source code. This process involves several stages of compilation and metadata extraction.

### TinyGo Compilation Pipeline

```mermaid
graph LR
    subgraph "Source Code"
        GoSource["Go Source Files<br/>*.go"]
        GoModFile["go.mod<br/>Module Definition"]
        ManifestFile["modus.json<br/>Application Config"]
    end
    
    subgraph "Compilation Stage"
        TinyGoCompiler["TinyGo Compiler<br/>tinygo build -target=wasi"]
        WasmOptimizer["WASM Optimizer<br/>Size & Performance"]
    end
    
    subgraph "Post-Processing"
        MetadataExtractor["lib/wasmextractor<br/>Function Signature Extraction"]
        SchemaGenerator["GraphQL Schema<br/>Type Generation"]
    end
    
    subgraph "Output Artifacts"
        WasmBinary["WebAssembly Binary<br/>*.wasm"]
        FunctionMetadata["Function Metadata<br/>JSON Schema"]
        GraphQLSchema["GraphQL Types<br/>Auto-generated"]
    end
    
    GoSource --> TinyGoCompiler
    GoModFile --> TinyGoCompiler
    ManifestFile --> TinyGoCompiler
    
    TinyGoCompiler --> WasmOptimizer
    WasmOptimizer --> WasmBinary
    
    WasmBinary --> MetadataExtractor
    MetadataExtractor --> FunctionMetadata
    FunctionMetadata --> SchemaGenerator
    SchemaGenerator --> GraphQLSchema
```

Sources: [sdk/go/go.mod:7-21](), [lib/wasmextractor/go.mod:1-6](), [lib/manifest/go.mod:1-18]()

## Runtime Integration

The compiled Go WebAssembly modules integrate with the Modus Runtime through a well-defined interface that supports function invocation, host function calls, and agent lifecycle management.

### Runtime Execution Architecture

```mermaid
graph TB
    subgraph "Runtime Environment"
        WasmHost["github.com/tetratelabs/wazero<br/>WebAssembly Runtime"]
        HostFunctions["Host Function Registry<br/>System API Bindings"]
        AgentActors["github.com/tochemey/goakt/v3<br/>Actor System"]
    end
    
    subgraph "Go WASM Module"
        ExportedFunctions["Exported Go Functions<br/>GraphQL Resolvers"]
        ImportedFunctions["Imported Host Functions<br/>Database, HTTP, AI APIs"]
        Memory["Linear Memory<br/>Go Runtime Heap"]
    end
    
    subgraph "External Services"
        PostgreSQL["PostgreSQL Client<br/>github.com/jackc/pgx/v5"]
        MySQL["MySQL Client<br/>github.com/go-sql-driver/mysql"]
        Dgraph["Dgraph Client<br/>github.com/dgraph-io/dgo/v240"]
        Neo4j["Neo4j Client<br/>github.com/neo4j/neo4j-go-driver/v5"]
        S3["AWS S3 Client<br/>github.com/aws/aws-sdk-go-v2"]
    end
    
    WasmHost --> ExportedFunctions
    ExportedFunctions --> AgentActors
    
    ImportedFunctions --> HostFunctions
    HostFunctions --> PostgreSQL
    HostFunctions --> MySQL
    HostFunctions --> Dgraph
    HostFunctions --> Neo4j
    HostFunctions --> S3
    
    AgentActors --> Memory
```

Sources: [runtime/go.mod:42](), [runtime/go.mod:45](), [runtime/go.mod:15](), [runtime/go.mod:29](), [runtime/go.mod:20](), [runtime/go.mod:33](), [runtime/go.mod:10-12]()

## Example Applications

The Go SDK includes comprehensive examples demonstrating various integration patterns and use cases.

| Example | Purpose | Key Dependencies | Features Demonstrated |
|---------|---------|------------------|----------------------|
| `simple` | Basic function definition | Core SDK only | Function export, basic types |
| `http` | HTTP client operations | Core SDK | External API calls, request/response handling |
| `postgresql` | Database operations | Core SDK | SQL queries, connection management |
| `graphql` | GraphQL operations | Core SDK | Query execution, schema introspection |
| `embedding` | AI embeddings | `tidwall/gjson`, `tidwall/sjson` | Vector generation, JSON processing |
| `vectors` | Vector operations | `golang.org/x/exp` | Mathematical computations, experimental APIs |
| `auth` | Authentication | Core SDK | JWT handling, authorization |
| `dgraph` | Graph database | Core SDK | Graph queries, relationships |
| `anthropic-functions` | AI function calling | `tidwall/gjson` | LLM integration, structured responses |
| `classification` | ML classification | Core SDK | Machine learning, categorization |
| `textgeneration` | Text generation | `tidwall/gjson` | Content generation, prompt engineering |

Sources: [sdk/go/examples/simple/go.mod:1-9](), [sdk/go/examples/http/go.mod:1-9](), [sdk/go/examples/postgresql/go.mod:1-9](), [sdk/go/examples/graphql/go.mod:1-9](), [sdk/go/examples/embedding/go.mod:1-16](), [sdk/go/examples/vectors/go.mod:1-12](), [sdk/go/examples/auth/go.mod:1-9](), [sdk/go/examples/dgraph/go.mod:1-9](), [sdk/go/examples/anthropic-functions/go.mod:1-16](), [sdk/go/examples/classification/go.mod:1-9](), [sdk/go/examples/textgeneration/go.mod:1-18]()

## Version Management and Dependencies

The Go SDK maintains compatibility with specific Go versions and manages dependencies through Go modules. The SDK requires Go 1.23.1 or later with toolchain support for Go 1.24.4.

### Dependency Structure

```mermaid
graph TB
    subgraph "Core Dependencies"
        GoSDK["github.com/hypermodeinc/modus/sdk/go<br/>v0.18.0-alpha.7"]
        Manifest["github.com/hypermodeinc/modus/lib/manifest<br/>v0.17.2"]
        WasmExtractor["github.com/hypermodeinc/modus/lib/wasmextractor<br/>v0.13.0"]
    end
    
    subgraph "Utility Libraries"
        Color["github.com/fatih/color<br/>v1.18.0<br/>Terminal Output"]
        Version["github.com/hashicorp/go-version<br/>v1.7.0<br/>Version Parsing"]
        XID["github.com/rs/xid<br/>v1.6.0<br/>ID Generation"]
        GJSON["github.com/tidwall/gjson<br/>v1.18.0<br/>JSON Processing"]
        SJSON["github.com/tidwall/sjson<br/>v1.2.5<br/>JSON Modification"]
    end
    
    subgraph "Go Standard Extensions"
        Exp["golang.org/x/exp<br/>v0.0.0-20250606033433<br/>Experimental Features"]
        Mod["golang.org/x/mod<br/>v0.25.0<br/>Module Tools"]
        Tools["golang.org/x/tools<br/>v0.34.0<br/>Build Tools"]
    end
    
    GoSDK --> Manifest
    GoSDK --> WasmExtractor
    GoSDK --> Color
    GoSDK --> Version
    GoSDK --> XID
    GoSDK --> GJSON
    GoSDK --> SJSON
    GoSDK --> Exp
    GoSDK --> Mod
    GoSDK --> Tools
```

Sources: [sdk/go/go.mod:1-35](), [sdk/go/templates/default/go.mod:1-10](), [lib/manifest/go.mod:1-18](), [lib/wasmextractor/go.mod:1-6]()

---

# Page: AssemblyScript SDK

# AssemblyScript SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/assemblyscript/examples/anthropic-functions/package-lock.json](sdk/assemblyscript/examples/anthropic-functions/package-lock.json)
- [sdk/assemblyscript/examples/auth/package-lock.json](sdk/assemblyscript/examples/auth/package-lock.json)
- [sdk/assemblyscript/examples/classification/package-lock.json](sdk/assemblyscript/examples/classification/package-lock.json)
- [sdk/assemblyscript/examples/dgraph/package-lock.json](sdk/assemblyscript/examples/dgraph/package-lock.json)
- [sdk/assemblyscript/examples/embedding/package-lock.json](sdk/assemblyscript/examples/embedding/package-lock.json)
- [sdk/assemblyscript/examples/graphql/package-lock.json](sdk/assemblyscript/examples/graphql/package-lock.json)
- [sdk/assemblyscript/examples/http/package-lock.json](sdk/assemblyscript/examples/http/package-lock.json)
- [sdk/assemblyscript/examples/neo4j/package-lock.json](sdk/assemblyscript/examples/neo4j/package-lock.json)
- [sdk/assemblyscript/examples/postgresql/package-lock.json](sdk/assemblyscript/examples/postgresql/package-lock.json)
- [sdk/assemblyscript/examples/simple/package-lock.json](sdk/assemblyscript/examples/simple/package-lock.json)
- [sdk/assemblyscript/examples/textgeneration/package-lock.json](sdk/assemblyscript/examples/textgeneration/package-lock.json)
- [sdk/assemblyscript/examples/vectors/package-lock.json](sdk/assemblyscript/examples/vectors/package-lock.json)
- [sdk/assemblyscript/src/package-lock.json](sdk/assemblyscript/src/package-lock.json)
- [sdk/assemblyscript/src/package.json](sdk/assemblyscript/src/package.json)

</details>



This document covers the Modus AssemblyScript SDK, which enables developers to write Modus applications using AssemblyScript that compile to WebAssembly. The SDK provides APIs for database access, AI model integration, HTTP requests, and other Modus platform capabilities.

For information about the Go SDK, see [Go SDK](#4.1). For details about the Modus Runtime that executes compiled WASM modules, see [Runtime Architecture](#5.1).

## SDK Overview

The AssemblyScript SDK is distributed as the `@hypermode/modus-sdk-as` npm package and provides a TypeScript-like development experience that compiles to WebAssembly. The SDK includes core APIs, build tools, development utilities, and extensive examples demonstrating various Modus platform features.

```mermaid
graph TB
    subgraph "AssemblyScript SDK Package"
        Package["@hypermode/modus-sdk-as<br/>Main SDK Package"]
        BuildTool["modus-as-build<br/>Build Plugin Binary"]
        Transform["Transform Plugin<br/>Code Generation"]
        ESLint["ESLint Integration<br/>Development Tools"]
    end
    
    subgraph "Core Dependencies"
        AS["assemblyscript<br/>^0.28.2"]
        JsonAS["json-as<br/>JSON Serialization"]
        WasiShim["@assemblyscript/wasi-shim<br/>WASI Compatibility"]
        Base64["as-base64<br/>Base64 Encoding"]
    end
    
    subgraph "Developer Experience"
        NodeReq["Node.js >= 22<br/>Runtime Requirement"]
        TypeScript["typescript<br/>Type Checking"]
        Prettier["prettier<br/>Code Formatting"]
    end
    
    Package --> BuildTool
    Package --> Transform
    Package --> ESLint
    
    BuildTool --> AS
    Package --> JsonAS
    Package --> WasiShim
    Package --> Base64
    
    ESLint --> TypeScript
    BuildTool --> Prettier
```

**Sources:** [sdk/assemblyscript/src/package.json:1-60]()

## Build System Architecture

The SDK's build system centers around the `modus-as-build` binary, which handles AssemblyScript compilation with Modus-specific transformations and optimizations.

```mermaid
graph LR
    subgraph "Development Source"
        ASSource["AssemblyScript Source<br/>.ts files"]
        Manifest["modus.json<br/>Project Configuration"]
        ASConfig["asconfig.json<br/>AssemblyScript Config"]
    end
    
    subgraph "Build Pipeline"
        BuildBin["modus-as-build<br/>bin/build-plugin.js"]
        Transform["Transform Phase<br/>Code Generation"]
        Compiler["AssemblyScript Compiler<br/>asc"]
        Binaryen["Binaryen Optimizer<br/>wasm-opt"]
    end
    
    subgraph "Output Artifacts"
        Wasm["WebAssembly Module<br/>.wasm file"]
        Metadata["Function Metadata<br/>GraphQL Schema Info"]
    end
    
    ASSource --> BuildBin
    Manifest --> BuildBin
    ASConfig --> BuildBin
    
    BuildBin --> Transform
    Transform --> Compiler
    Compiler --> Binaryen
    Binaryen --> Wasm
    Transform --> Metadata
```

**Sources:** [sdk/assemblyscript/src/package.json:9-10](), [sdk/assemblyscript/src/package.json:17](), [sdk/assemblyscript/src/package.json:44-46]()

## Example Projects Structure

The SDK includes comprehensive examples demonstrating different Modus platform capabilities. Each example follows a consistent project structure and dependency pattern.

```mermaid
graph TB
    subgraph "Example Categories"
        Simple["simple-example<br/>Basic Functions"]
        DB["Database Examples"]
        AI["AI Model Examples"] 
        Integration["Integration Examples"]
    end
    
    subgraph "Database Examples"
        PostgreSQL["postgresql-example<br/>PostgreSQL Operations"]
        Dgraph["dgraph-example<br/>Graph Database"]
    end
    
    subgraph "AI Model Examples"
        TextGen["textgeneration-example<br/>LLM Text Generation"]
        Classification["classification-example<br/>Model Classification"]
        Embedding["embedding-example<br/>Vector Embeddings"]
        Anthropic["anthropic-functions-example<br/>Anthropic Claude API"]
    end
    
    subgraph "Integration Examples"
        HTTP["http-example<br/>HTTP Requests"]
        GraphQL["graphql-example<br/>GraphQL APIs"]
        Vectors["vectors-example<br/>Vector Operations"]
        Auth["auth-example<br/>Authentication"]
    end
    
    Simple --> DB
    DB --> AI
    AI --> Integration
    
    DB --> PostgreSQL
    DB --> Dgraph
    
    AI --> TextGen
    AI --> Classification
    AI --> Embedding
    AI --> Anthropic
    
    Integration --> HTTP
    Integration --> GraphQL
    Integration --> Vectors
    Integration --> Auth
```

**Sources:** [sdk/assemblyscript/examples/simple/package-lock.json:6-7](), [sdk/assemblyscript/examples/postgresql/package-lock.json:6-7](), [sdk/assemblyscript/examples/classification/package-lock.json:6-7](), [sdk/assemblyscript/examples/embedding/package-lock.json:6-7](), [sdk/assemblyscript/examples/http/package-lock.json:6-7](), [sdk/assemblyscript/examples/dgraph/package-lock.json:6-7](), [sdk/assemblyscript/examples/anthropic-functions/package-lock.json:6-7](), [sdk/assemblyscript/examples/textgeneration/package-lock.json:6-7](), [sdk/assemblyscript/examples/auth/package-lock.json:6-7](), [sdk/assemblyscript/examples/vectors/package-lock.json:6-7](), [sdk/assemblyscript/examples/graphql/package-lock.json:6-7]()

## Development Tools and Quality Assurance

The SDK provides comprehensive development tooling including ESLint integration, TypeScript support, and testing frameworks to ensure code quality and developer productivity.

| Tool Category | Package | Version | Purpose |
|---------------|---------|---------|---------|
| **Build Tools** | `assemblyscript` | ^0.28.2 | Core AssemblyScript compiler |
| **Build Tools** | `modus-as-build` | - | Custom build plugin binary |
| **Code Quality** | `eslint` | ^9.28.0 | JavaScript/TypeScript linting |
| **Code Quality** | `typescript-eslint` | ^8.34.0 | TypeScript-specific ESLint rules |
| **Code Quality** | `prettier` | ^3.5.3 | Code formatting |
| **Code Quality** | `assemblyscript-prettier` | ^3.0.1 | AssemblyScript-specific formatting |
| **Testing** | `as-test` | ^0.4.4 | AssemblyScript testing framework |
| **Runtime** | `@assemblyscript/wasi-shim` | ^0.1.0 | WASI compatibility layer |
| **Utilities** | `json-as` | ^1.1.15 | JSON serialization for AssemblyScript |

```mermaid
graph TB
    subgraph "Development Environment"
        VSCode["VS Code<br/>Editor Support"]
        ESLintConfig["ESLint Configuration<br/>assemblyscript-eslint"]
        TypeScript["TypeScript Compiler<br/>Type Checking"]
    end
    
    subgraph "Code Quality Pipeline"
        Prettier["prettier<br/>Code Formatting"]
        ESLint["eslint<br/>Linting Rules"]
        TSESLint["typescript-eslint<br/>TS-Specific Rules"]
        ASPrettier["assemblyscript-prettier<br/>AS Formatting"]
    end
    
    subgraph "Testing Framework"
        ASTest["as-test<br/>Test Runner"]
        TestBuild["Test Compilation<br/>ast build"]
        TestRun["Test Execution<br/>ast run"]
    end
    
    VSCode --> ESLintConfig
    ESLintConfig --> ESLint
    ESLint --> TSESLint
    Prettier --> ASPrettier
    
    ASTest --> TestBuild
    TestBuild --> TestRun
```

**Sources:** [sdk/assemblyscript/src/package.json:30-40](), [sdk/assemblyscript/src/package.json:12-20](), [sdk/assemblyscript/src/package.json:44-48]()

## Runtime Integration and WASM Execution

The compiled AssemblyScript modules integrate with the Modus Runtime through a well-defined WebAssembly interface, supporting function metadata extraction and GraphQL schema generation.

```mermaid
graph TB
    subgraph "AssemblyScript Development"
        Functions["Exported Functions<br/>@modus decorators"]
        Types["Type Definitions<br/>Input/Output Models"]
        Imports["SDK API Imports<br/>Database, HTTP, AI"]
    end
    
    subgraph "Compilation Process"
        Transform["AST Transform<br/>Metadata Extraction"]
        Compile["AssemblyScript Compiler<br/>WASM Generation"]
        Optimize["Binaryen Optimization<br/>Size & Performance"]
    end
    
    subgraph "Runtime Deployment"
        WasmModule["WebAssembly Module<br/>.wasm binary"]
        Metadata["Function Metadata<br/>GraphQL Schema Info"]
        Host["Modus Runtime<br/>WASM Host Environment"]
    end
    
    subgraph "Execution Environment"
        GraphQLEndpoint["GraphQL Endpoints<br/>Auto-generated"]
        FunctionExec["Function Execution<br/>Sandboxed WASM"]
        HostAPIs["Host Function APIs<br/>Database, HTTP, Models"]
    end
    
    Functions --> Transform
    Types --> Transform
    Imports --> Transform
    
    Transform --> Compile
    Compile --> Optimize
    
    Optimize --> WasmModule
    Transform --> Metadata
    
    WasmModule --> Host
    Metadata --> Host
    
    Host --> GraphQLEndpoint
    Host --> FunctionExec
    FunctionExec --> HostAPIs
```

**Sources:** [sdk/assemblyscript/src/package.json:22-28](), [sdk/assemblyscript/src/package.json:44-46]()

---

# Page: SDK Internals

# SDK Internals

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/assemblyscript/examples/anthropic-functions/package-lock.json](sdk/assemblyscript/examples/anthropic-functions/package-lock.json)
- [sdk/assemblyscript/examples/classification/package-lock.json](sdk/assemblyscript/examples/classification/package-lock.json)
- [sdk/assemblyscript/examples/dgraph/package-lock.json](sdk/assemblyscript/examples/dgraph/package-lock.json)
- [sdk/assemblyscript/examples/embedding/package-lock.json](sdk/assemblyscript/examples/embedding/package-lock.json)
- [sdk/assemblyscript/examples/graphql/package-lock.json](sdk/assemblyscript/examples/graphql/package-lock.json)
- [sdk/assemblyscript/examples/http/package-lock.json](sdk/assemblyscript/examples/http/package-lock.json)
- [sdk/assemblyscript/examples/postgresql/package-lock.json](sdk/assemblyscript/examples/postgresql/package-lock.json)
- [sdk/assemblyscript/examples/textgeneration/package-lock.json](sdk/assemblyscript/examples/textgeneration/package-lock.json)
- [sdk/assemblyscript/src/assembly/__tests__/agent.spec.ts](sdk/assemblyscript/src/assembly/__tests__/agent.spec.ts)
- [sdk/assemblyscript/src/assembly/__tests__/database.spec.ts](sdk/assemblyscript/src/assembly/__tests__/database.spec.ts)
- [sdk/assemblyscript/src/assembly/__tests__/dynamicmap.spec.ts](sdk/assemblyscript/src/assembly/__tests__/dynamicmap.spec.ts)
- [sdk/assemblyscript/src/assembly/__tests__/graphql.spec.ts](sdk/assemblyscript/src/assembly/__tests__/graphql.spec.ts)
- [sdk/assemblyscript/src/assembly/__tests__/openai.spec.ts](sdk/assemblyscript/src/assembly/__tests__/openai.spec.ts)
- [sdk/assemblyscript/src/assembly/__tests__/src/taskagent.ts](sdk/assemblyscript/src/assembly/__tests__/src/taskagent.ts)
- [sdk/assemblyscript/src/assembly/database.ts](sdk/assemblyscript/src/assembly/database.ts)
- [sdk/assemblyscript/src/package-lock.json](sdk/assemblyscript/src/package-lock.json)
- [sdk/assemblyscript/src/package.json](sdk/assemblyscript/src/package.json)
- [sdk/assemblyscript/src/tests/agent.run.ts](sdk/assemblyscript/src/tests/agent.run.ts)
- [sdk/assemblyscript/src/tests/database.run.ts](sdk/assemblyscript/src/tests/database.run.ts)
- [sdk/assemblyscript/src/tests/openai.run.ts](sdk/assemblyscript/src/tests/openai.run.ts)

</details>



This document provides a detailed technical overview of the Modus AssemblyScript SDK implementation, including its package structure, build system, core components, and testing infrastructure. It covers the internal architecture that enables developers to write WebAssembly modules in AssemblyScript for the Modus runtime.

For information about using the AssemblyScript SDK to develop applications, see [AssemblyScript SDK](#4.2). For details about the Go SDK implementation, see [Go SDK](#4.1).

## Package Architecture

The AssemblyScript SDK is distributed as an NPM package `@hypermode/modus-sdk-as` with a sophisticated build system supporting both development and production workflows.

### Package Structure

```mermaid
graph TD
    PackageRoot["@hypermode/modus-sdk-as"]
    
    subgraph "Core Assembly Sources"
        IndexTS["index.ts"]
        AssemblyDir["assembly/"]
        ModelsDir["models/"]
    end
    
    subgraph "Build Infrastructure"
        BuildPlugin["bin/build-plugin.js"]
        TransformDir["transform/"]
        PluginConfig["plugin.asconfig.json"]
    end
    
    subgraph "Development Tools"
        ESLintTools["tools/assemblyscript-eslint.js"]
        ESLintLocal["tools/assemblyscript-eslint-local.js"]
    end
    
    subgraph "Generated Outputs"
        TransformLib["transform/lib/*.js"]
        BuildOutput["build/"]
    end
    
    PackageRoot --> IndexTS
    PackageRoot --> AssemblyDir
    PackageRoot --> ModelsDir
    PackageRoot --> BuildPlugin
    PackageRoot --> TransformDir
    PackageRoot --> PluginConfig
    PackageRoot --> ESLintTools
    PackageRoot --> ESLintLocal
    
    TransformDir --> TransformLib
    BuildPlugin --> BuildOutput
```

The package exports multiple entry points through its `exports` field, enabling modular consumption of SDK components.

**Sources:** [sdk/assemblyscript/src/package.json:44-48]()

### Build System Integration

The SDK includes a custom build plugin `modus-as-build` that extends the standard AssemblyScript compilation process:

```mermaid
graph LR
    DevProject["Developer Project"]
    ModusAsBuild["modus-as-build"]
    ASC["asc (AssemblyScript Compiler)"]
    Transform["TypeScript Transform"]
    WASMOutput["WebAssembly Module"]
    
    DevProject --> ModusAsBuild
    ModusAsBuild --> Transform
    ModusAsBuild --> ASC
    Transform --> ASC
    ASC --> WASMOutput
    
    subgraph "SDK Dependencies"
        JsonAS["json-as"]
        WASIShim["@assemblyscript/wasi-shim"]
        Base64["as-base64"]
        Semver["semver"]
        XidTS["xid-ts"]
    end
    
    ModusAsBuild --> JsonAS
    ModusAsBuild --> WASIShim
    ModusAsBuild --> Base64
    ModusAsBuild --> Semver
    ModusAsBuild --> XidTS
```

**Sources:** [sdk/assemblyscript/src/package.json:9-10](), [sdk/assemblyscript/src/package.json:22-28]()

## Core Runtime Components

The SDK provides several core modules that interface with the Modus runtime through WebAssembly host functions.

### Database Client Architecture

```mermaid
graph TD
    UserCode["Developer Code"]
    DatabaseModule["database.ts"]
    
    subgraph "Parameter Types"
        PositionalParams["PositionalParams"]
        NamedParams["NamedParams"]
    end
    
    subgraph "Response Types"
        Response["Response"]
        QueryResponse["QueryResponse<T>"]
        ScalarResponse["ScalarResponse<T>"]
    end
    
    subgraph "Data Types"
        Point["Point"]
        Location["Location"]
    end
    
    subgraph "Host Interface"
        HostExecuteQuery["hostExecuteQuery"]
        HostQueryResponse["HostQueryResponse"]
    end
    
    UserCode --> DatabaseModule
    DatabaseModule --> PositionalParams
    DatabaseModule --> NamedParams
    DatabaseModule --> Response
    DatabaseModule --> QueryResponse
    DatabaseModule --> ScalarResponse
    DatabaseModule --> Point
    DatabaseModule --> Location
    
    DatabaseModule --> HostExecuteQuery
    HostExecuteQuery --> HostQueryResponse
    HostQueryResponse --> Response
```

The database module provides typed query execution with support for PostgreSQL, MySQL, Dgraph, and Neo4j through a unified interface.

**Sources:** [sdk/assemblyscript/src/assembly/database.ts:14-20](), [sdk/assemblyscript/src/assembly/database.ts:33-65](), [sdk/assemblyscript/src/assembly/database.ts:67-79]()

### Agent System Components

```mermaid
graph TD
    AgentModule["agent.ts"]
    
    subgraph "Agent Management"
        StartAgent["startAgent"]
        StopAgent["stopAgent"]
        GetAgentInfo["getAgentInfo"]
        ListAgents["listAgents"]
    end
    
    subgraph "Messaging System"
        SendMessage["sendMessage"]
        MessageResponse["MessageResponse"]
        AgentMessage["AgentMessage"]
    end
    
    subgraph "Agent Types"
        AgentInfo["AgentInfo"]
        AgentStatus["AgentStatus enum"]
    end
    
    subgraph "Host Functions"
        HostStartAgent["modus_agents.startAgent"]
        HostStopAgent["modus_agents.stopAgent"]
        HostGetAgentInfo["modus_agents.getAgentInfo"]
        HostListAgents["modus_agents.listAgents"]
        HostSendMessage["modus_agents.sendMessage"]
    end
    
    AgentModule --> StartAgent
    AgentModule --> StopAgent
    AgentModule --> GetAgentInfo
    AgentModule --> ListAgents
    AgentModule --> SendMessage
    
    StartAgent --> HostStartAgent
    StopAgent --> HostStopAgent
    GetAgentInfo --> HostGetAgentInfo
    ListAgents --> HostListAgents
    SendMessage --> HostSendMessage
    
    StartAgent --> AgentInfo
    StopAgent --> AgentInfo
    GetAgentInfo --> AgentInfo
    ListAgents --> AgentInfo
    SendMessage --> MessageResponse
```

**Sources:** [sdk/assemblyscript/src/assembly/__tests__/agent.spec.ts:24-45]()

### Dynamic Data Structures

The SDK includes a `DynamicMap` class that provides flexible JSON-compatible data handling:

```mermaid
graph TD
    DynamicMap["DynamicMap"]
    
    subgraph "Core Operations"
        Set["set<T>(key, value)"]
        Get["get<T>(key)"]
        Has["has(key)"]
        Delete["delete(key)"]
    end
    
    subgraph "JSON Integration"
        JSONParse["JSON.parse<DynamicMap>"]
        JSONStringify["JSON.stringify(DynamicMap)"]
        Serialize["serialize()"]
        Deserialize["deserialize()"]
    end
    
    subgraph "Type Handling"
        ValueType["ValueType enum"]
        NullHandling["Null Value Support"]
        ComplexTypes["Nested Objects/Arrays"]
    end
    
    DynamicMap --> Set
    DynamicMap --> Get
    DynamicMap --> Has
    DynamicMap --> Delete
    
    DynamicMap --> JSONParse
    DynamicMap --> JSONStringify
    DynamicMap --> Serialize
    DynamicMap --> Deserialize
    
    DynamicMap --> ValueType
    DynamicMap --> NullHandling
    DynamicMap --> ComplexTypes
```

**Sources:** [sdk/assemblyscript/src/assembly/__tests__/dynamicmap.spec.ts:12](), [sdk/assemblyscript/src/assembly/__tests__/dynamicmap.spec.ts:25-32](), [sdk/assemblyscript/src/assembly/__tests__/dynamicmap.spec.ts:80-94]()

## Model Integration System

The SDK provides typed interfaces for AI model interactions, with OpenAI as the primary implementation.

### OpenAI Chat Model Architecture

```mermaid
graph TD
    ChatModule["models/openai/chat"]
    
    subgraph "Message Types"
        SystemMessage["SystemMessage"]
        UserMessage["UserMessage"]
        AssistantMessage["AssistantMessage"]
        RequestMessage["RequestMessage"]
    end
    
    subgraph "Model Interface"
        OpenAIChatModel["OpenAIChatModel"]
        ModelInfo["ModelInfo"]
        Model["Model"]
    end
    
    subgraph "Message Processing"
        ParseMessages["parseMessages"]
        MessageParser["Message Parser"]
    end
    
    subgraph "Host Integration"
        ModelsModule["models module"]
        InvokeModel["invokeModel"]
        GetModelInfo["getModelInfo"]
    end
    
    ChatModule --> SystemMessage
    ChatModule --> UserMessage
    ChatModule --> AssistantMessage
    ChatModule --> RequestMessage
    
    ChatModule --> OpenAIChatModel
    ChatModule --> ModelInfo
    ChatModule --> Model
    
    ChatModule --> ParseMessages
    ParseMessages --> MessageParser
    
    OpenAIChatModel --> ModelsModule
    ModelsModule --> InvokeModel
    ModelsModule --> GetModelInfo
```

**Sources:** [sdk/assemblyscript/src/assembly/__tests__/openai.spec.ts:13-20](), [sdk/assemblyscript/src/assembly/__tests__/openai.spec.ts:22]()

## Testing Infrastructure

The SDK employs a comprehensive testing framework built on `as-test` with mock capabilities for host function testing.

### Test Architecture

```mermaid
graph TD
    TestSuite["SDK Test Suite"]
    
    subgraph "Test Framework"
        AsTest["as-test"]
        MockImport["mockImport"]
        MockFn["mockFn"]
        Expect["expect"]
        It["it"]
        Run["run"]
    end
    
    subgraph "Test Categories"
        DatabaseTests["database.spec.ts"]
        AgentTests["agent.spec.ts"]
        GraphQLTests["graphql.spec.ts"]
        OpenAITests["openai.spec.ts"]
        DynamicMapTests["dynamicmap.spec.ts"]
    end
    
    subgraph "Test Execution"
        BuildSpecs["Build Test WASMs"]
        RunScripts["Test Runner Scripts"]
        NodeExecution["Node.js Test Execution"]
    end
    
    subgraph "Mock System"
        HostMocks["Host Function Mocks"]
        ReturnValues["Mock Return Values"]
        CallTracking["Function Call Tracking"]
    end
    
    TestSuite --> AsTest
    AsTest --> MockImport
    AsTest --> MockFn
    AsTest --> Expect
    AsTest --> It
    AsTest --> Run
    
    TestSuite --> DatabaseTests
    TestSuite --> AgentTests
    TestSuite --> GraphQLTests
    TestSuite --> OpenAITests
    TestSuite --> DynamicMapTests
    
    TestSuite --> BuildSpecs
    BuildSpecs --> RunScripts
    RunScripts --> NodeExecution
    
    MockImport --> HostMocks
    HostMocks --> ReturnValues
    HostMocks --> CallTracking
```

**Sources:** [sdk/assemblyscript/src/assembly/__tests__/agent.spec.ts:10](), [sdk/assemblyscript/src/assembly/__tests__/agent.spec.ts:24-45](), [sdk/assemblyscript/src/tests/agent.run.ts:11-17]()

### Mock Testing Pattern

The testing infrastructure provides sophisticated mocking capabilities for host functions:

```mermaid
graph LR
    TestCode["Test Code"]
    MockImport["mockImport()"]
    HostFunction["Host Function"]
    MockImplementation["Mock Implementation"]
    ReturnValue["Controlled Return Value"]
    
    TestCode --> MockImport
    MockImport --> HostFunction
    HostFunction --> MockImplementation
    MockImplementation --> ReturnValue
    ReturnValue --> TestCode
    
    subgraph "Example: Agent Tests"
        AgentMock["mockImport('modus_agents.startAgent')"]
        AgentReturn["start_agent_ret: AgentInfo"]
        AgentTest["Agent Start Test"]
    end
    
    MockImport -.-> AgentMock
    ReturnValue -.-> AgentReturn
    TestCode -.-> AgentTest
```

**Sources:** [sdk/assemblyscript/src/assembly/__tests__/agent.spec.ts:17-26](), [sdk/assemblyscript/src/assembly/__tests__/graphql.spec.ts:14-21]()

## Development Workflow Integration

The SDK integrates with standard Node.js development workflows through NPM scripts and tooling.

### Build and Test Pipeline

```mermaid
graph TD
    DevWorkflow["Development Workflow"]
    
    subgraph "Build Pipeline"
        PrepareStep["prepare script"]
        BuildTransform["build:transform"]
        TSCompile["TypeScript Compilation"]
        TransformOutput["transform/lib/*.js"]
    end
    
    subgraph "Test Pipeline"
        TestScript["test script"]
        PreTest["pretest script"]
        ASTBuild["ast build"]
        ASTRun["ast run"]
        TestTransform["test:transform"]
        NodeTest["Node.js Test Execution"]
    end
    
    subgraph "Code Quality"
        Lint["lint script"]
        ESLint["ESLint Execution"]
        Pretty["pretty script"]
        PrettierFormat["Prettier Formatting"]
        PrettyCheck["pretty:check script"]
    end
    
    DevWorkflow --> PrepareStep
    PrepareStep --> BuildTransform
    BuildTransform --> TSCompile
    TSCompile --> TransformOutput
    
    DevWorkflow --> TestScript
    TestScript --> PreTest
    PreTest --> ASTBuild
    PreTest --> TSCompile
    TestScript --> ASTRun
    TestScript --> TestTransform
    TestTransform --> NodeTest
    
    DevWorkflow --> Lint
    Lint --> ESLint
    DevWorkflow --> Pretty
    Pretty --> PrettierFormat
    DevWorkflow --> PrettyCheck
    PrettyCheck --> PrettierFormat
```

**Sources:** [sdk/assemblyscript/src/package.json:12-21]()

### Example Project Structure

The SDK includes multiple example projects demonstrating different capabilities:

| Example | Purpose | Key Features |
|---------|---------|--------------|
| `classification` | AI model classification | OpenAI integration, model invocation |
| `embedding` | Vector embeddings | Embedding model usage |
| `graphql` | GraphQL client usage | Query execution, type safety |
| `postgresql` | Database integration | PostgreSQL queries, typed results |
| `http` | HTTP client functionality | External API calls |
| `dgraph` | Graph database | Dgraph-specific operations |
| `anthropic-functions` | Function calling | Anthropic model integration |
| `textgeneration` | Text generation | Text completion models |

Each example follows a consistent structure with its own `package-lock.json` and dependencies on the core SDK.

**Sources:** [sdk/assemblyscript/examples/graphql/package-lock.json:2-22](), [sdk/assemblyscript/examples/postgresql/package-lock.json:2-22](), [sdk/assemblyscript/examples/classification/package-lock.json:2-22]()

## SDK Dependencies and External Integrations

The SDK maintains a careful balance of external dependencies to provide functionality while keeping the runtime footprint minimal:

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@assemblyscript/wasi-shim` | ^0.1.0 | WASI compatibility layer |
| `as-base64` | ^0.2.0 | Base64 encoding/decoding |
| `chalk` | ^5.4.1 | Terminal output formatting |
| `json-as` | ^1.1.15 | JSON serialization for AssemblyScript |
| `semver` | ^7.7.2 | Semantic version handling |
| `xid-ts` | ^1.1.4 | Unique ID generation |

### Development Dependencies

The SDK uses modern development tooling including ESLint 9.x, TypeScript 5.x, and AssemblyScript 0.28.x for maintaining code quality and compatibility.

**Sources:** [sdk/assemblyscript/src/package.json:22-40]()

---

# Page: Modus Runtime

# Modus Runtime

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lib/manifest/go.mod](lib/manifest/go.mod)
- [lib/metadata/go.mod](lib/metadata/go.mod)
- [lib/wasmextractor/go.mod](lib/wasmextractor/go.mod)
- [runtime/actors/actorsystem.go](runtime/actors/actorsystem.go)
- [runtime/actors/subscriber.go](runtime/actors/subscriber.go)
- [runtime/actors/wasmagent.go](runtime/actors/wasmagent.go)
- [runtime/app/app.go](runtime/app/app.go)
- [runtime/db/agentstate.go](runtime/db/agentstate.go)
- [runtime/db/inferencehistory.go](runtime/db/inferencehistory.go)
- [runtime/go.mod](runtime/go.mod)
- [runtime/go.sum](runtime/go.sum)
- [runtime/languages/golang/testdata/go.mod](runtime/languages/golang/testdata/go.mod)
- [runtime/languages/golang/testdata/go.sum](runtime/languages/golang/testdata/go.sum)
- [runtime/wasmhost/wasmhost.go](runtime/wasmhost/wasmhost.go)
- [sdk/assemblyscript/src/assembly/exports.ts](sdk/assemblyscript/src/assembly/exports.ts)
- [sdk/go/go.mod](sdk/go/go.mod)
- [sdk/go/go.sum](sdk/go/go.sum)
- [sdk/go/templates/default/go.mod](sdk/go/templates/default/go.mod)
- [sdk/go/templates/default/go.sum](sdk/go/templates/default/go.sum)

</details>



The Modus Runtime is the core execution environment that hosts and orchestrates WebAssembly modules compiled from Go and AssemblyScript code. It provides a complete runtime system featuring WebAssembly execution, actor-based agent management, GraphQL schema generation and query processing, database connectivity, and AI model integration.

This document covers the runtime architecture, core subsystems, and execution flow. For information about developing applications that run on this runtime, see [Software Development Kits](#4). For details about the CLI tools that manage runtime deployment, see [Modus CLI](#3). For specific subsystem details, see [Runtime Architecture](#5.1), [GraphQL Engine](#5.2), [Agent System](#5.3), [Database Integration](#5.4), and [AI Model Integration](#5.5).

## Runtime Architecture Overview

The Modus Runtime is built around several interconnected subsystems that work together to provide a complete execution environment for WebAssembly modules.

### Core System Components

```mermaid
graph TB
    subgraph "Runtime Core"
        WH["WasmHost<br/>wazero Runtime"]
        AS["ActorSystem<br/>GoAkt Framework"]
        GQL["GraphQL Engine<br/>Wundergraph Tools"]
        PM["PluginManager<br/>Module Loading"]
    end
    
    subgraph "Data Layer"
        PG["PostgreSQL<br/>Primary Database"]
        MDB["ModusDB<br/>Development Database"]
        DGRAPH["Dgraph<br/>Graph Database"]
        NEO4J["Neo4j<br/>Graph Database"]
        MYSQL["MySQL<br/>Relational Database"]
    end
    
    subgraph "External Services"
        AI["AI Models<br/>OpenAI, etc."]
        S3["Cloud Storage<br/>AWS S3"]
    end
    
    subgraph "Host Functions"
        HF["Host Functions<br/>System APIs"]
        AGENTS["Agent Functions<br/>Message Handling"]
        DB_CLIENTS["Database Clients<br/>Connection Management"]
    end
    
    WH --> PM
    WH --> HF
    AS --> WH
    GQL --> WH
    
    HF --> DB_CLIENTS
    HF --> AI
    HF --> S3
    
    AGENTS --> AS
    
    DB_CLIENTS --> PG
    DB_CLIENTS --> MDB
    DB_CLIENTS --> DGRAPH
    DB_CLIENTS --> NEO4J
    DB_CLIENTS --> MYSQL
    
    style WH fill:#f9f9f9
    style AS fill:#f9f9f9
    style GQL fill:#f9f9f9
```

**Sources:** [runtime/wasmhost/wasmhost.go:45-79](), [runtime/actors/actorsystem.go:28-56](), [runtime/go.mod:7-59]()

### Runtime Initialization Flow

```mermaid
sequenceDiagram
    participant MAIN as "main()"
    participant APP as "app.Initialize()"
    participant WH as "WasmHost"
    participant AS as "ActorSystem"
    participant PM as "PluginManager"
    participant GQL as "GraphQL Engine"
    
    MAIN->>APP: "Initialize application"
    APP->>WH: "NewWasmHost(ctx, registrations...)"
    WH->>WH: "wazero.NewRuntimeWithConfig()"
    WH->>WH: "wasi.MustInstantiate()"
    WH->>WH: "instantiateHostFunctions()"
    
    APP->>AS: "actors.Initialize(ctx)"
    AS->>AS: "goakt.NewActorSystem()"
    AS->>AS: "actorSystem.Start()"
    AS->>AS: "actorSystem.Inject(&wasmAgentInfo{})"
    
    APP->>PM: "pluginmanager.LoadPlugins()"
    PM->>WH: "CompileModule(bytes)"
    PM->>PM: "RegisterPluginLoadedCallback()"
    
    APP->>GQL: "Start GraphQL server"
    GQL->>WH: "Extract function metadata"
    GQL->>GQL: "Generate GraphQL schema"
```

**Sources:** [runtime/wasmhost/wasmhost.go:51-79](), [runtime/actors/actorsystem.go:28-56]()

## WebAssembly Host System

The `WasmHost` interface provides the core WebAssembly execution environment using the wazero runtime. It manages module compilation, instantiation, and function execution with proper isolation and resource management.

### WASM Host Interface

The `WasmHost` interface at [runtime/wasmhost/wasmhost.go:33-43]() defines the primary operations:

- `RegisterHostFunction()` - Registers Go functions as host functions callable from WASM
- `CallFunction()` - Executes WASM functions with parameter mapping
- `CallFunctionInModule()` - Executes functions in a specific module instance
- `CompileModule()` - Compiles WASM bytes into reusable compiled modules
- `GetModuleInstance()` - Creates isolated module instances for execution

### Module Configuration and Isolation

```mermaid
graph LR
    subgraph "Module Configuration"
        MC["ModuleConfig"]
        ENV["Environment Variables"]
        STDIO["Stdout/Stderr"]
        TZ["Timezone Settings"]
        JWT["JWT Claims"]
    end
    
    subgraph "WASM Module"
        MOD["wasm.Module"]
        FUNCS["Exported Functions"]
        MEM["Linear Memory"]
        GLOBALS["Global Variables"]
    end
    
    subgraph "Host Functions"
        SYS["System Functions"]
        DB["Database Functions"]
        HTTP["HTTP Functions"]
        AI_FUNCS["AI Model Functions"]
    end
    
    MC --> MOD
    ENV --> MOD
    STDIO --> MOD
    TZ --> MOD
    JWT --> MOD
    
    MOD --> FUNCS
    FUNCS --> SYS
    FUNCS --> DB
    FUNCS --> HTTP
    FUNCS --> AI_FUNCS
```

The `getModuleConfig()` function at [runtime/wasmhost/wasmhost.go:135-183]() creates isolated module instances with:

- Dedicated stdout/stderr streams with logging integration
- Environment variable injection (including `MODUS_*` prefixed variables)
- Timezone configuration from context or system default
- JWT claims from request middleware
- Anonymous module naming for performance and concurrency

**Sources:** [runtime/wasmhost/wasmhost.go:135-183](), [runtime/wasmhost/wasmhost.go:110-121]()

### Host Function Registration

Host functions bridge the WASM sandbox with the runtime environment. The system supports automatic parameter marshaling and provides access to:

- Database connections and query execution
- HTTP client operations
- AI model inference
- File system operations (limited)
- Logging and telemetry

**Sources:** [runtime/wasmhost/wasmhost.go:33-43]()

## Actor System

The actor system provides concurrent, stateful agent management using the GoAkt framework. Each agent runs as an independent actor with its own WASM module instance and managed lifecycle.

### Agent Actor Architecture

```mermaid
graph TB
    subgraph "Actor System"
        AS["ActorSystem<br/>goakt.ActorSystem"]
        TA["TopicActor<br/>Pub/Sub Events"]
        SUB["SubscriptionActors<br/>Event Subscribers"]
    end
    
    subgraph "Agent Actors"
        AA1["wasmAgentActor<br/>agent-123"]
        AA2["wasmAgentActor<br/>agent-456"]
        AA3["wasmAgentActor<br/>agent-789"]
    end
    
    subgraph "Agent State"
        DB_STATE["Database State<br/>AgentState table"]
        MEM_STATE["Memory State<br/>WASM Linear Memory"]
    end
    
    subgraph "Message Flow"
        REQ["AgentRequest"]
        RESP["AgentResponse"]
        EVENTS["AgentEvent"]
    end
    
    AS --> AA1
    AS --> AA2
    AS --> AA3
    AS --> TA
    AS --> SUB
    
    AA1 --> DB_STATE
    AA2 --> DB_STATE
    AA3 --> DB_STATE
    
    AA1 --> MEM_STATE
    AA2 --> MEM_STATE
    AA3 --> MEM_STATE
    
    REQ --> AA1
    AA1 --> RESP
    AA1 --> EVENTS
    EVENTS --> TA
    TA --> SUB
```

**Sources:** [runtime/actors/actorsystem.go:26-56](), [runtime/actors/wasmagent.go:31-41]()

### Agent Lifecycle Management

The `wasmAgentActor` struct at [runtime/actors/wasmagent.go:31-41]() manages the complete agent lifecycle:

#### Agent States

```mermaid
stateDiagram-v2
    [*] --> Starting: "spawnActorForAgent()"
    Starting --> Running: "_modus_agent_handle_event(initialize)"
    Running --> Suspending: "RestartAgent message"
    Running --> Stopping: "ShutdownAgent message"
    Suspending --> Suspended: "_modus_agent_handle_event(suspend)"
    Suspended --> Resuming: "PostStart event"
    Resuming --> Running: "_modus_agent_handle_event(resume)"
    Stopping --> Terminated: "_modus_agent_handle_event(terminate)"
    Terminated --> [*]
```

#### Agent Actor Methods

- `PreStart()` - Activates agent and initializes WASM module
- `Receive()` - Handles incoming messages and lifecycle events
- `PostStop()` - Suspends agent and cleans up resources
- `activateAgent()` - Creates WASM module instance and calls `_modus_agent_activate`
- `startAgent()` / `resumeAgent()` - Transitions agent to running state
- `suspendAgent()` / `stopAgent()` - Persists state and transitions to inactive states

**Sources:** [runtime/actors/wasmagent.go:43-151](), [runtime/actors/wasmagent.go:322-447]()

### Message Handling

Agent message processing occurs in `handleAgentRequest()` at [runtime/actors/wasmagent.go:153-206]():

1. Validates agent is in `AgentStatusRunning` state
2. Calls `_modus_agent_handle_message` WASM function with message data
3. Returns response if `msg.Respond` is true
4. Saves agent state after successful message processing

**Sources:** [runtime/actors/wasmagent.go:153-206]()

### Event Publishing and Subscription

The system supports real-time event streaming through the actor pub/sub system:

- `PublishAgentEvent()` - Publishes events to agent-specific topics
- `SubscribeForAgentEvents()` - Creates subscription actors for event streaming
- Agent status changes automatically trigger events

**Sources:** [runtime/actors/subscriber.go:32-91]()

## State Persistence

Agent state is automatically persisted to the database through the `AgentState` structure at [runtime/db/agentstate.go:23-30]():

```go
type AgentState struct {
    Id        string `json:"id" db:"constraint=unique"`
    Name      string `json:"name"`
    Status    string `json:"status"`
    Data      string `json:"data,omitempty"`
    UpdatedAt string `json:"updated"`
}
```

State operations support both PostgreSQL and ModusDB backends:
- `WriteAgentState()` - Upserts complete agent state
- `UpdateAgentStatus()` - Updates only status field
- `GetAgentState()` - Retrieves agent state by ID
- `QueryActiveAgents()` - Finds all non-terminated agents

**Sources:** [runtime/db/agentstate.go:23-30](), [runtime/db/agentstate.go:32-62]()

---

# Page: Runtime Architecture

# Runtime Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.trunk/configs/cspell.json](.trunk/configs/cspell.json)
- [.vscode/launch.json](.vscode/launch.json)
- [runtime/actors/actorsystem.go](runtime/actors/actorsystem.go)
- [runtime/actors/subscriber.go](runtime/actors/subscriber.go)
- [runtime/actors/wasmagent.go](runtime/actors/wasmagent.go)
- [runtime/app/app.go](runtime/app/app.go)
- [runtime/db/agentstate.go](runtime/db/agentstate.go)
- [runtime/db/db.go](runtime/db/db.go)
- [runtime/db/inferencehistory.go](runtime/db/inferencehistory.go)
- [runtime/db/modusdb.go](runtime/db/modusdb.go)
- [runtime/explorer/explorer.go](runtime/explorer/explorer.go)
- [runtime/services/services.go](runtime/services/services.go)
- [runtime/wasmhost/wasmhost.go](runtime/wasmhost/wasmhost.go)
- [sdk/assemblyscript/examples/agents/.gitignore](sdk/assemblyscript/examples/agents/.gitignore)
- [sdk/assemblyscript/src/assembly/exports.ts](sdk/assemblyscript/src/assembly/exports.ts)
- [sdk/go/examples/agents/.gitignore](sdk/go/examples/agents/.gitignore)

</details>



This document covers the core architecture of the Modus Runtime system, including service initialization, WebAssembly hosting, actor system management, and data persistence. The runtime serves as the execution environment for user-defined functions compiled to WebAssembly, with support for GraphQL APIs, agent-based concurrency, and database integration.

For information about the GraphQL schema generation and query processing, see [GraphQL Engine](#5.2). For details about the agent lifecycle and message passing, see [Agent System](#5.3). For database client configuration and connection management, see [Database Integration](#5.4).

## Runtime Overview

The Modus Runtime is built around a layered architecture that handles WebAssembly module execution, HTTP request processing, and background service management. The runtime initializes multiple interdependent services and provides a sandboxed execution environment for user functions.

**Core Runtime Architecture**

```mermaid
graph TB
    subgraph "HTTP Layer"
        HttpServer["HTTP Server :8686"]
        ExplorerHandler["ExplorerHandler"]
        GraphQLRouter["GraphQL Router"]
        HealthCheck["Health Check /health"]
        MetricsEndpoint["Metrics /metrics"]
    end
    
    subgraph "Service Layer"
        ServicesStart["services.Start()"]
        ServicesStop["services.Stop()"]
        ServiceInit["Service Initialization"]
    end
    
    subgraph "WASM Execution"
        WasmHostNew["wasmhost.NewWasmHost()"]
        WasmHostInterface["WasmHost interface"]
        WazeroRuntime["wazero.Runtime"]
        ModuleInstance["wasm.Module instances"]
    end
    
    subgraph "Actor System"
        ActorSystemInit["actors.Initialize()"]
        GoAktSystem["goakt.ActorSystem"]
        WasmAgentActor["wasmAgentActor"]
        AgentEvents["Agent Events"]
    end
    
    subgraph "Data Layer"
        PostgresPool["pgxpool.Pool"]
        ModusDbEngine["modusgraph.Engine"]
        DbInitialize["db.Initialize()"]
        StateManagement["Agent State Management"]
    end
    
    HttpServer --> ExplorerHandler
    HttpServer --> GraphQLRouter
    ServicesStart --> ServiceInit
    ServiceInit --> WasmHostNew
    ServiceInit --> ActorSystemInit
    ServiceInit --> DbInitialize
    
    WasmHostNew --> WazeroRuntime
    WasmHostInterface --> ModuleInstance
    ActorSystemInit --> GoAktSystem
    GoAktSystem --> WasmAgentActor
    WasmAgentActor --> AgentEvents
    
    DbInitialize --> PostgresPool
    DbInitialize --> ModusDbEngine
    StateManagement --> PostgresPool
    StateManagement --> ModusDbEngine
```

Sources: [runtime/services/services.go:34-63](), [runtime/wasmhost/wasmhost.go:51-79](), [runtime/actors/actorsystem.go:28-56](), [runtime/db/db.go:64-75]()

## Service Initialization

The runtime startup follows a specific initialization sequence managed by the `services` package. Services are started in dependency order to ensure proper system initialization.

**Service Startup Sequence**

```mermaid
sequenceDiagram
    participant Main as "Runtime Main"
    participant Services as "services.Start()"
    participant WasmHost as "wasmhost.InitWasmHost()"
    participant Background as "Background Services"
    participant Actors as "actors.Initialize()"
    participant GraphQL as "graphql.Initialize()"
    
    Main->>Services: Start(ctx)
    Services->>WasmHost: Initialize with host functions
    Note over Services,WasmHost: Add WasmHost to context
    
    Services->>Background: sqlclient.Initialize()
    Services->>Background: dgraphclient.Initialize()
    Services->>Background: neo4jclient.Initialize()
    Services->>Background: secrets.Initialize(ctx)
    Services->>Background: storage.Initialize(ctx)
    Services->>Background: db.Initialize(ctx)
    Services->>Background: db.InitModusDb(ctx)
    Services->>Actors: actors.Initialize(ctx)
    Services->>GraphQL: graphql.Initialize()
    Services->>Background: envfiles.MonitorEnvFiles(ctx)
    Services->>Background: manifestdata.MonitorManifestFile(ctx)
    Services->>Background: pluginmanager.Initialize(ctx)
```

The initialization order is critical, as shown in [runtime/services/services.go:45-61](). The WASM host must be initialized first and placed in the context before other services can access it. Database services are initialized before the actor system, which depends on state persistence.

Sources: [runtime/services/services.go:34-63](), [runtime/hostfunctions/hostfunctions.go](), [runtime/wasmhost/wasmhost.go:51-79]()

## WebAssembly Host Architecture

The WASM host provides the core execution environment for user functions. It uses the Wazero runtime with WASI support and manages module instantiation, host function registration, and execution context.

**WASM Host Components**

```mermaid
graph TB
    subgraph "WasmHost Interface"
        RegisterHostFunction["RegisterHostFunction()"]
        CallFunction["CallFunction()"]
        CallFunctionByName["CallFunctionByName()"]
        CallFunctionInModule["CallFunctionInModule()"]
        GetModuleInstance["GetModuleInstance()"]
        CompileModule["CompileModule()"]
    end
    
    subgraph "Wazero Runtime"
        WazeroConfig["wazero.RuntimeConfig"]
        WazeroRuntime["wazero.Runtime"]
        WasiModule["wasi_snapshot_preview1"]
        CompiledModule["wazero.CompiledModule"]
    end
    
    subgraph "Module Execution"
        ModuleConfig["wazero.ModuleConfig"]
        ModuleInstance["wasm.Module"]
        OutputBuffers["utils.OutputBuffers"]
        ExecutionInfo["ExecutionInfo"]
    end
    
    subgraph "Host Functions"
        EnvHostFunctions["env host functions"]
        HostFunctionRegistry["hostFunction registry"]
        FunctionRegistry["functions.FunctionRegistry"]
    end
    
    RegisterHostFunction --> HostFunctionRegistry
    CallFunction --> GetModuleInstance
    GetModuleInstance --> ModuleConfig
    ModuleConfig --> ModuleInstance
    CallFunctionInModule --> ExecutionInfo
    
    WazeroConfig --> WazeroRuntime
    WazeroRuntime --> WasiModule
    WazeroRuntime --> CompiledModule
    CompiledModule --> ModuleInstance
    
    EnvHostFunctions --> WazeroRuntime
    HostFunctionRegistry --> WazeroRuntime
    FunctionRegistry --> ExecutionInfo
```

The `wasmHost` struct implements the `WasmHost` interface defined in [runtime/wasmhost/wasmhost.go:33-43](). Module instances are created per invocation with specific configuration including environment variables, timezone, JWT claims, and output capturing as shown in [runtime/wasmhost/wasmhost.go:135-183]().

Sources: [runtime/wasmhost/wasmhost.go:33-43](), [runtime/wasmhost/wasmhost.go:45-49](), [runtime/wasmhost/wasmhost.go:135-183]()

## Actor System Integration

The runtime uses GoAkt actors for managing agent lifecycle and concurrent execution. The actor system handles agent state persistence, message routing, and cluster coordination.

**Actor System Architecture**

```mermaid
graph TB
    subgraph "GoAkt Actor System"
        ActorSystem["goakt.ActorSystem"]
        TopicActor["TopicActor (pub/sub)"]
        ClusterOptions["Cluster Options"]
    end
    
    subgraph "Agent Actors"
        WasmAgentActor["wasmAgentActor"]
        AgentLifecycle["Agent Lifecycle"]
        MessageHandling["Message Handling"]
        StateManagement["State Management"]
    end
    
    subgraph "Extensions & Dependencies"
        WasmExtension["wasmExtension"]
        WasmAgentInfo["wasmAgentInfo"]
        AgentInfoDep["Agent Info Dependency"]
    end
    
    subgraph "Event System"
        AgentEvents["Agent Events"]
        SubscriptionActor["subscriptionActor"]
        EventPublishing["Event Publishing"]
    end
    
    ActorSystem --> WasmAgentActor
    ActorSystem --> TopicActor
    ActorSystem --> ClusterOptions
    
    WasmAgentActor --> AgentLifecycle
    WasmAgentActor --> MessageHandling
    WasmAgentActor --> StateManagement
    
    WasmExtension --> WasmAgentActor
    WasmAgentInfo --> AgentInfoDep
    AgentInfoDep --> WasmAgentActor
    
    TopicActor --> AgentEvents
    AgentEvents --> SubscriptionActor
    SubscriptionActor --> EventPublishing
```

The actor system is initialized with specific options including pub/sub support, timeouts, and the `wasmExtension` for WASM host access in [runtime/actors/actorsystem.go:34-41](). Agent actors implement the full lifecycle with `PreStart`, `Receive`, and `PostStop` handlers as defined in [runtime/actors/wasmagent.go:43-151]().

Sources: [runtime/actors/actorsystem.go:28-56](), [runtime/actors/wasmagent.go:31-41](), [runtime/actors/actorsystem.go:128-136]()

## Database Architecture

The runtime supports dual database backends: PostgreSQL for production and ModusDB (graph database) for development. The database layer handles agent state persistence, inference history, and plugin metadata.

**Database Layer Components**

```mermaid
graph TB
    subgraph "Database Selection"
        UseModusDB["useModusDB()"]
        DevEnvironment["app.IsDevEnvironment()"]
        ModusUseModusDB["MODUS_USE_MODUSDB env var"]
    end
    
    subgraph "PostgreSQL Backend"
        PgxPool["pgxpool.Pool"]
        RuntimePostgresWriter["runtimePostgresWriter"]
        WithTx["WithTx() transaction wrapper"]
        InferenceHistory["Inference History"]
    end
    
    subgraph "ModusDB Backend"
        ModusDbEngine["modusgraph.Engine"]
        GraphOperations["Graph Operations"]
        AgentStateGraph["Agent State in Graph"]
    end
    
    subgraph "Data Models"
        AgentState["db.AgentState"]
        Plugin["db.Plugin"]
        Inference["db.Inference"]
        InferenceHistoryStruct["inferenceHistory struct"]
    end
    
    UseModusDB --> DevEnvironment
    UseModusDB --> ModusUseModusDB
    
    PgxPool --> WithTx
    RuntimePostgresWriter --> InferenceHistory
    WithTx --> AgentState
    
    ModusDbEngine --> GraphOperations
    GraphOperations --> AgentStateGraph
    
    AgentState --> PgxPool
    AgentState --> ModusDbEngine
    Plugin --> RuntimePostgresWriter
    Inference --> RuntimePostgresWriter
    InferenceHistoryStruct --> RuntimePostgresWriter
```

The database selection logic is implemented in [runtime/db/db.go:111-124]() using the `useModusDB()` function. Agent state operations are abstracted through functions like `WriteAgentState()` and `GetAgentState()` that route to the appropriate backend in [runtime/db/agentstate.go:32-62]().

Sources: [runtime/db/db.go:111-124](), [runtime/db/agentstate.go:32-62](), [runtime/db/modusdb.go:27-47](), [runtime/db/inferencehistory.go:28-33]()

## HTTP Server and API Endpoints

The runtime exposes HTTP endpoints for GraphQL queries, health checks, metrics, and the API Explorer interface. The server configuration supports both single-node and cluster deployments.

**HTTP API Architecture**

```mermaid
graph TB
    subgraph "HTTP Endpoints"
        Port8686["HTTP Server :8686"]
        GraphQLEndpoint["/graphql"]
        HealthEndpoint["/health"]
        MetricsEndpoint["/metrics"]
        ExplorerEndpoint["/explorer/*"]
    end
    
    subgraph "Explorer API"
        ExplorerHandler["explorer.ExplorerHandler"]
        EndpointsAPI["/explorer/api/endpoints"]
        InferencesAPI["/explorer/api/inferences"]
        StaticContent["/explorer/* static files"]
    end
    
    subgraph "Content Serving"
        EmbedFS["embed.FS content"]
        ContentRoot["contentRoot fs.Sub"]
        FileServerFS["http.FileServerFS"]
    end
    
    subgraph "Data APIs"
        EndpointsHandler["endpointsHandler()"]
        InferenceHistoryHandler["inferenceHistoryHandler()"]
        ManifestData["manifestdata.GetManifest()"]
        DbQueryInferences["db.QueryInferences()"]
    end
    
    Port8686 --> GraphQLEndpoint
    Port8686 --> HealthEndpoint
    Port8686 --> MetricsEndpoint
    Port8686 --> ExplorerEndpoint
    
    ExplorerEndpoint --> ExplorerHandler
    ExplorerHandler --> EndpointsAPI
    ExplorerHandler --> InferencesAPI
    ExplorerHandler --> StaticContent
    
    StaticContent --> EmbedFS
    EmbedFS --> ContentRoot
    ContentRoot --> FileServerFS
    
    EndpointsAPI --> EndpointsHandler
    InferencesAPI --> InferenceHistoryHandler
    EndpointsHandler --> ManifestData
    InferenceHistoryHandler --> DbQueryInferences
```

The Explorer handler is defined in [runtime/explorer/explorer.go:27-37]() and serves both static content from embedded files and dynamic API endpoints. The endpoints handler extracts GraphQL endpoint information from the manifest in [runtime/explorer/explorer.go:39-61]().

Sources: [runtime/explorer/explorer.go:27-37](), [runtime/explorer/explorer.go:39-61](), [runtime/explorer/explorer.go:65-83](), [.vscode/launch.json:15-19]()

## Development and Debugging Support

The runtime includes extensive debugging support through VS Code launch configurations, environment variable controls, and development-specific features like automatic refresh and local database management.

**Development Configuration**

| Environment Variable | Purpose | Default |
|---------------------|---------|---------|
| `MODUS_ENV` | Environment mode | production |
| `MODUS_DEBUG` | Enable debug logging | false |
| `MODUS_USE_MODUSDB` | Use local graph database | dev environment |
| `MODUS_CLUSTER_MODE` | Enable cluster mode | disabled |
| `FORCE_COLOR` | Force colored output | auto-detect |

The VS Code launch configurations in [.vscode/launch.json:5-19]() provide multiple debugging scenarios including cluster mode, AWS storage, and different SDK examples. The runtime supports hot reload through the `--refresh` parameter for development workflows.

Sources: [.vscode/launch.json:5-43](), [runtime/app/app.go:37-43](), [runtime/db/db.go:111-124]()

---

# Page: GraphQL Engine

# GraphQL Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [runtime/graphql/datasource/configuration.go](runtime/graphql/datasource/configuration.go)
- [runtime/graphql/datasource/planner.go](runtime/graphql/datasource/planner.go)
- [runtime/graphql/engine/engine.go](runtime/graphql/engine/engine.go)
- [runtime/graphql/graphql.go](runtime/graphql/graphql.go)
- [runtime/graphql/schemagen/schemagen.go](runtime/graphql/schemagen/schemagen.go)
- [runtime/graphql/schemagen/schemagen_as_test.go](runtime/graphql/schemagen/schemagen_as_test.go)
- [runtime/graphql/schemagen/schemagen_go_test.go](runtime/graphql/schemagen/schemagen_go_test.go)
- [runtime/httpserver/dynamicMux.go](runtime/httpserver/dynamicMux.go)
- [runtime/httpserver/server.go](runtime/httpserver/server.go)
- [runtime/integration_tests/postgresql_integration_test.go](runtime/integration_tests/postgresql_integration_test.go)
- [runtime/main.go](runtime/main.go)

</details>



The GraphQL Engine is responsible for automatically generating GraphQL schemas from WebAssembly module metadata and processing GraphQL queries by executing the corresponding WASM functions. It serves as the primary API interface for Modus applications, dynamically creating GraphQL endpoints based on exported functions from loaded plugins.

For information about the broader runtime architecture, see [Runtime Architecture](#5.1). For details about how agents integrate with GraphQL subscriptions, see [Agent System](#5.3).

## Architecture Overview

The GraphQL Engine consists of several interconnected components that work together to provide dynamic GraphQL API generation and execution.

```mermaid
graph TB
    subgraph "GraphQL Request Flow"
        HTTP["HTTP Request<br/>/graphql"]
        Handler["GraphQLRequestHandler<br/>runtime/graphql/graphql.go"]
        Engine["ExecutionEngine<br/>wundergraph/graphql-go-tools"]
        DataSource["ModusDataSource<br/>runtime/graphql/datasource"]
        WasmHost["WasmHost<br/>Function Execution"]
    end
    
    subgraph "Schema Generation"
        Plugin["Plugin Metadata<br/>Function Signatures"]
        SchemaGen["Schema Generator<br/>runtime/graphql/schemagen"]
        GraphQLSchema["Generated GraphQL Schema<br/>Types & Operations"]
    end
    
    subgraph "Engine Lifecycle"
        PluginManager["Plugin Manager<br/>Load Events"]
        Activate["engine.Activate()<br/>Setup Engine"]
        ManifestData["Manifest Data<br/>Endpoint Configuration"]
    end
    
    HTTP --> Handler
    Handler --> Engine
    Engine --> DataSource
    DataSource --> WasmHost
    
    Plugin --> SchemaGen
    SchemaGen --> GraphQLSchema
    GraphQLSchema --> Engine
    
    PluginManager --> Activate
    ManifestData --> Activate
    Activate --> Engine
```

Sources: [runtime/graphql/graphql.go:40-316](), [runtime/graphql/engine/engine.go:52-73](), [runtime/graphql/schemagen/schemagen.go:33-94]()

## Schema Generation Process

The GraphQL Engine automatically generates schemas by analyzing WebAssembly module metadata and transforming function signatures into GraphQL operations.

```mermaid
graph LR
    subgraph "Input Analysis"
        WasmMetadata["WASM Metadata<br/>Function Exports"]
        TypeDefs["Type Definitions<br/>Structs & Fields"]
        FnSignatures["Function Signatures<br/>Parameters & Returns"]
    end
    
    subgraph "Schema Generation"
        TypeTransform["transformTypes()<br/>Convert to GraphQL Types"]
        FnTransform["transformFunctions()<br/>Query/Mutation Fields"]
        SchemaBuilder["writeSchema()<br/>Generate SDL"]
    end
    
    subgraph "Generated Schema"
        QueryType["Query Type<br/>Read Operations"]
        MutationType["Mutation Type<br/>Write Operations"]
        CustomTypes["Custom Types<br/>Input/Output Objects"]
        Scalars["Custom Scalars<br/>Timestamp, Int64, etc."]
    end
    
    WasmMetadata --> TypeTransform
    TypeDefs --> TypeTransform
    FnSignatures --> FnTransform
    
    TypeTransform --> QueryType
    TypeTransform --> CustomTypes
    TypeTransform --> Scalars
    FnTransform --> QueryType
    FnTransform --> MutationType
    
    QueryType --> SchemaBuilder
    MutationType --> SchemaBuilder
    CustomTypes --> SchemaBuilder
    Scalars --> SchemaBuilder
```

Sources: [runtime/graphql/schemagen/schemagen.go:105-149](), [runtime/graphql/schemagen/schemagen.go:181-231](), [runtime/graphql/schemagen/schemagen.go:308-432]()

### Type System Mapping

The schema generator maps WebAssembly types to GraphQL types with language-specific handling:

| WASM Type (Go) | WASM Type (AssemblyScript) | GraphQL Type | Notes |
|----------------|----------------------------|--------------|-------|
| `string` | `~lib/string/String` | `String!` | Non-nullable by default |
| `int32` | `i32` | `Int!` | Standard integer |
| `int64` | `i64` | `Int64!` | Custom scalar |
| `float64` | `f64` | `Float!` | Standard float |
| `[]T` | `~lib/array/Array<T>` | `[T!]!` | Non-nullable array |
| `map[K]V` | `~lib/map/Map<K,V>` | `[KVPair!]!` | Key-value pairs |
| `*T` | `T \| null` | `T` | Nullable type |
| `time.Time` | `~lib/date/Date` | `Timestamp!` | Custom scalar |

Sources: [runtime/graphql/schemagen/schemagen_go_test.go:385-599](), [runtime/graphql/schemagen/schemagen_as_test.go:343-555]()

## Query Execution Flow

When GraphQL queries are received, the engine processes them through a multi-stage execution pipeline.

```mermaid
sequenceDiagram
    participant Client
    participant "GraphQLRequestHandler" as Handler
    participant "ExecutionEngine" as Engine
    participant "ModusDataSourcePlanner" as Planner
    participant "FunctionsDataSource" as DataSource
    participant "WasmHost" as Wasm
    
    Client->>Handler: "POST /graphql"
    Handler->>Handler: "Parse GraphQL Request"
    Handler->>Engine: "Execute(request)"
    
    Engine->>Planner: "Plan Query Execution"
    Planner->>Planner: "Capture Field Information"
    Planner->>Planner: "Map Fields to Functions"
    Planner->>DataSource: "Configure Fetch"
    
    DataSource->>Wasm: "Execute WASM Function"
    Wasm->>DataSource: "Function Result"
    DataSource->>Engine: "Formatted Response"
    
    Engine->>Handler: "GraphQL Response"
    Handler->>Handler: "Add Function Output"
    Handler->>Client: "JSON Response"
```

Sources: [runtime/graphql/graphql.go:74-251](), [runtime/graphql/datasource/planner.go:93-270]()

## Data Source System

The GraphQL Engine uses a custom data source implementation to bridge GraphQL operations with WebAssembly function execution.

### Data Source Configuration

```mermaid
graph TB
    subgraph "Configuration Setup"
        Schema["GraphQL Schema<br/>Type Definitions"]
        Config["ModusDataSourceConfig<br/>Function Mappings"]
        Metadata["DataSourceMetadata<br/>Root & Child Nodes"]
    end
    
    subgraph "Query Planning"
        Planner["modusDataSourcePlanner<br/>Field Analysis"]
        Template["Input Template<br/>Function Parameters"]
        Variables["Resolve Variables<br/>Parameter Values"]
    end
    
    subgraph "Execution"
        FunctionDS["functionsDataSource<br/>WASM Execution"]
        EventDS["eventsDataSource<br/>Subscriptions"]
        WasmHost["WasmHost<br/>Function Invocation"]
    end
    
    Schema --> Config
    Config --> Metadata
    Metadata --> Planner
    
    Planner --> Template
    Planner --> Variables
    Template --> FunctionDS
    Variables --> FunctionDS
    Template --> EventDS
    Variables --> EventDS
    
    FunctionDS --> WasmHost
```

Sources: [runtime/graphql/datasource/configuration.go:17-22](), [runtime/graphql/datasource/planner.go:27-39](), [runtime/graphql/engine/engine.go:106-148]()

### Field Mapping Process

The planner captures detailed information about GraphQL fields and maps them to WebAssembly functions:

```go
type fieldInfo struct {
    Name       string      `json:"name"`
    Alias      string      `json:"alias,omitempty"`
    TypeName   string      `json:"type,omitempty"`
    ParentType string      `json:"parentType,omitempty"`
    Fields     []fieldInfo `json:"fields,omitempty"`
    IsMapType  bool        `json:"isMapType,omitempty"`
}
```

Sources: [runtime/graphql/datasource/planner.go:41-51]()

## Engine Lifecycle Management

The GraphQL Engine integrates with the plugin management system to dynamically activate and update schemas as WebAssembly modules are loaded.

```mermaid
stateDiagram-v2
    [*] --> Inactive: "Runtime Startup"
    
    Inactive --> SchemaGeneration: "Plugin Loaded"
    SchemaGeneration --> EngineCreation: "Schema Generated"
    EngineCreation --> Active: "Engine Configured"
    
    Active --> SchemaGeneration: "Plugin Reloaded"
    Active --> SchemaGeneration: "Manifest Changed"
    
    Active --> RequestProcessing: "GraphQL Request"
    RequestProcessing --> Active: "Response Sent"
    
    state SchemaGeneration {
        [*] --> TypeAnalysis
        TypeAnalysis --> SchemaBuilding
        SchemaBuilding --> [*]
    }
    
    state EngineCreation {
        [*] --> DataSourceConfig
        DataSourceConfig --> ExecutionEngine
        ExecutionEngine --> [*]
    }
```

Sources: [runtime/graphql/graphql.go:52-72](), [runtime/graphql/engine/engine.go:52-73]()

### Plugin Integration

The engine registers callbacks with the plugin manager to automatically regenerate schemas when modules are loaded:

```go
func Initialize() {
    pluginmanager.RegisterPluginLoadedCallback(engine.Activate)
    manifestdata.RegisterManifestLoadedCallback(func(ctx context.Context) error {
        plugins := pluginmanager.GetRegisteredPlugins()
        // ... activate engine with loaded plugins
    })
}
```

Sources: [runtime/graphql/graphql.go:52-72]()

## Request Processing Details

### HTTP Request Handling

The `GraphQLRequestHandler` processes incoming requests with support for both regular queries and Server-Sent Events for subscriptions:

| Feature | Implementation | Purpose |
|---------|----------------|---------|
| Content Negotiation | Accept header checking | Redirect browsers to explorer |
| SSE Support | `text/event-stream` handling | Real-time subscriptions |
| Variable Context | Request headers & context | Time zone, tracing options |
| Error Handling | Structured error responses | Development vs production |

Sources: [runtime/graphql/graphql.go:74-251]()

### Response Enhancement

The engine adds execution metadata to GraphQL responses, including function invocation details and console output:

```go
func addOutputToResponse(response []byte, output map[string]wasmhost.ExecutionInfo) ([]byte, error) {
    // Add execution IDs and log messages to response extensions
    for key, item := range output {
        // Include execution ID and filtered log messages
    }
    return sjson.SetRawBytesOptions(response, "extensions.invocations", invocations, jsonOptions)
}
```

Sources: [runtime/graphql/graphql.go:253-305]()

## Integration with Runtime Components

The GraphQL Engine integrates with several other runtime components:

| Component | Integration Point | Purpose |
|-----------|------------------|---------|
| Plugin Manager | Load callbacks | Schema regeneration |
| Manifest Data | Configuration changes | Endpoint updates |
| WASM Host | Function execution | Query resolution |
| Agent System | Subscriptions | Real-time events |
| HTTP Server | Route registration | Endpoint exposure |

Sources: [runtime/httpserver/server.go:125-231](), [runtime/main.go:49-52]()

## Error Handling and Development Features

The GraphQL Engine provides comprehensive error handling and development-focused features:

### Development Mode Features

- Automatic redirection to API Explorer for browsers
- Detailed error logging (suppressed in production)
- Schema debugging output with color formatting
- Introspection query support with empty schema fallback

### Error Classification

```mermaid
graph TD
    Errors["GraphQL Errors"]
    
    Errors --> ParseErrors["Parse Errors<br/>Invalid GraphQL syntax"]
    Errors --> ValidationErrors["Validation Errors<br/>Schema violations"] 
    Errors --> ExecutionErrors["Execution Errors<br/>Function failures"]
    Errors --> InternalErrors["Internal Errors<br/>System failures"]
    
    ParseErrors --> BadRequest["400 Bad Request"]
    ValidationErrors --> BadRequest
    ExecutionErrors --> GraphQLResponse["GraphQL Error Response"]
    InternalErrors --> ServerError["500 Internal Server Error"]
```

Sources: [runtime/graphql/graphql.go:186-220](), [runtime/graphql/engine/engine.go:84-90]()

## Testing and Validation

The GraphQL Engine includes comprehensive test coverage for schema generation and type conversion:

### Integration Testing

The system includes integration tests that verify end-to-end GraphQL query processing with real database connections and WebAssembly module execution.

Sources: [runtime/integration_tests/postgresql_integration_test.go:160-441]()

### Schema Generation Testing

Extensive unit tests validate the conversion of various type systems (Go and AssemblyScript) to GraphQL schemas, ensuring compatibility across different WebAssembly compilation targets.

Sources: [runtime/graphql/schemagen/schemagen_go_test.go:25-383](), [runtime/graphql/schemagen/schemagen_as_test.go:26-341]()

---

# Page: Agent System

# Agent System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [runtime/actors/agents.go](runtime/actors/agents.go)
- [runtime/hostfunctions/agents.go](runtime/hostfunctions/agents.go)
- [runtime/httpserver/health.go](runtime/httpserver/health.go)
- [sdk/assemblyscript/examples/agents/assembly/counterAgent.ts](sdk/assemblyscript/examples/agents/assembly/counterAgent.ts)
- [sdk/assemblyscript/examples/agents/assembly/index.ts](sdk/assemblyscript/examples/agents/assembly/index.ts)
- [sdk/assemblyscript/src/assembly/agent.ts](sdk/assemblyscript/src/assembly/agent.ts)
- [sdk/assemblyscript/src/assembly/agents.ts](sdk/assemblyscript/src/assembly/agents.ts)
- [sdk/assemblyscript/src/assembly/enums.ts](sdk/assemblyscript/src/assembly/enums.ts)
- [sdk/go/examples/agents/counterAgent.go](sdk/go/examples/agents/counterAgent.go)
- [sdk/go/examples/agents/main.go](sdk/go/examples/agents/main.go)
- [sdk/go/pkg/agents/agents.go](sdk/go/pkg/agents/agents.go)
- [sdk/go/pkg/agents/imports_mock.go](sdk/go/pkg/agents/imports_mock.go)
- [sdk/go/pkg/agents/imports_wasi.go](sdk/go/pkg/agents/imports_wasi.go)

</details>



The Agent System provides actor-based concurrency for long-running stateful processes within the Modus Runtime. It enables WebAssembly modules to create, manage, and communicate with persistent agent instances that can maintain state across requests and system restarts. For information about the overall runtime architecture, see [Runtime Architecture](#5.1). For details about database persistence used by agents, see [Database Integration](#5.4).

## Architecture Overview

The Agent System is built on the GoAkt actor framework and integrates with the WebAssembly host to provide a seamless agent experience for both Go and AssemblyScript applications.

### Core Components

```mermaid
graph TB
    subgraph "WebAssembly Layer"
        GoSDK["Go SDK<br/>agents.Agent Interface"]
        ASSDK["AssemblyScript SDK<br/>Agent Class"]
        WasmFunctions["WASM Export Functions<br/>_modus_agent_*"]
    end
    
    subgraph "Host Function Layer"
        HostFunctions["Host Functions<br/>modus_agents module"]
        AgentAPI["Agent API Functions<br/>StartAgent, StopAgent, etc."]
    end
    
    subgraph "Runtime Actor System"
        ActorSystem["GoAkt Actor System<br/>_actorSystem"]
        WasmAgentActor["wasmAgentActor<br/>Actor Implementation"]
        AgentManager["Agent Management<br/>Spawn, Lifecycle, Messages"]
    end
    
    subgraph "Persistence Layer"
        Database["Database Storage<br/>Agent State & Metadata"]
        StateManager["State Serialization<br/>GetState/SetState"]
    end
    
    subgraph "Communication Layer"
        MessageSystem["Message Passing<br/>Tell/Ask Pattern"]
        EventSystem["Event Publishing<br/>Pub/Sub Topics"]
        TopicActor["Topic Actor<br/>Event Distribution"]
    end
    
    GoSDK --> HostFunctions
    ASSDK --> HostFunctions
    WasmFunctions --> AgentManager
    
    HostFunctions --> AgentAPI
    AgentAPI --> ActorSystem
    ActorSystem --> WasmAgentActor
    WasmAgentActor --> StateManager
    WasmAgentActor --> Database
    
    MessageSystem --> WasmAgentActor
    EventSystem --> TopicActor
    WasmAgentActor --> TopicActor
    
    style ActorSystem fill:#f9f9f9
    style WasmAgentActor fill:#f9f9f9
    style Database fill:#f0f8ff
```

Sources: [runtime/actors/agents.go:1-304](), [sdk/go/pkg/agents/agents.go:1-393](), [sdk/assemblyscript/src/assembly/agent.ts:1-325](), [runtime/hostfunctions/agents.go:1-54]()

## Agent Lifecycle Management

The Agent System manages the complete lifecycle of agent instances through well-defined states and transitions.

### Agent States and Transitions

```mermaid
stateDiagram-v2
    [*] --> AgentStatusStarting: "StartAgent()"
    AgentStatusStarting --> AgentStatusRunning: "OnInitialize()"
    AgentStatusRunning --> AgentStatusSuspending: "Suspend Request"
    AgentStatusSuspending --> AgentStatusSuspended: "OnSuspend()"
    AgentStatusSuspended --> AgentStatusResuming: "Resume Request"
    AgentStatusResuming --> AgentStatusRunning: "OnResume()"
    AgentStatusRunning --> AgentStatusStopping: "StopAgent()"
    AgentStatusStopping --> AgentStatusTerminated: "OnTerminate()"
    AgentStatusTerminated --> [*]
    
    AgentStatusStarting --> AgentStatusTerminated: "Error/Failure"
    AgentStatusSuspending --> AgentStatusTerminated: "Force Stop"
    AgentStatusResuming --> AgentStatusTerminated: "Error/Failure"
```

### Key Lifecycle Functions

| Function | Runtime Implementation | Purpose |
|----------|----------------------|---------|
| `StartAgent` | [agents.go:65-77]() | Creates new agent instance with unique ID |
| `StopAgent` | [agents.go:101-122]() | Initiates agent termination |
| `GetAgentInfo` | [agents.go:135-157]() | Retrieves current agent status |
| `ListActiveAgents` | [agents.go:266-282]() | Lists all non-terminated agents |

The lifecycle is managed through the `wasmAgentActor` which handles state transitions and ensures proper cleanup.

Sources: [runtime/actors/agents.go:42-52](), [runtime/actors/agents.go:65-122](), [sdk/go/pkg/agents/agents.go:36-46]()

## Message Passing System

Agents communicate through a message-passing system that supports both synchronous and asynchronous communication patterns.

### Message Flow Architecture

```mermaid
sequenceDiagram
    participant Client as "Client/Function"
    participant HostFunc as "hostSendMessage"
    participant ActorSys as "Actor System"
    participant Agent as "wasmAgentActor"
    participant WASM as "WASM Instance"
    
    Client->>HostFunc: "SendMessage(agentId, msgName, data, timeout)"
    HostFunc->>ActorSys: "Tell/Ask(actorName, AgentRequest)"
    ActorSys->>Agent: "Route to Agent Actor"
    Agent->>WASM: "Call _modus_agent_handle_message"
    WASM->>Agent: "Return response data"
    Agent->>ActorSys: "AgentResponse"
    ActorSys->>HostFunc: "Response/Error"
    HostFunc->>Client: "MessageResponse"
```

### Message Types and Patterns

| Pattern | Timeout | Return Value | Use Case |
|---------|---------|--------------|----------|
| Synchronous | > 0 | Response data | Request-response operations |
| Asynchronous | 0 | None | Fire-and-forget notifications |
| Blocking | `math.MaxInt64` | Response data | Wait indefinitely for response |

The message system uses the `AgentRequest` and `AgentResponse` message types for communication between the runtime and WebAssembly instances.

Sources: [runtime/actors/agents.go:172-202](), [sdk/go/pkg/agents/agents.go:336-392](), [sdk/assemblyscript/src/assembly/agents.ts:29-74]()

## State Management

Agents maintain persistent state through serialization mechanisms that survive agent restarts and system shutdowns.

### State Persistence Flow

```mermaid
graph LR
    subgraph "Agent Instance"
        AgentState["Agent Internal State<br/>Fields & Properties"]
        GetState["GetState()<br/>Serialize to String"]
        SetState["SetState()<br/>Deserialize from String"]
    end
    
    subgraph "Runtime Layer"
        WasmExports["WASM Exports<br/>_modus_agent_get_state<br/>_modus_agent_set_state"]
        ActorState["Actor State Management<br/>Save/Restore Operations"]
    end
    
    subgraph "Database Layer"
        AgentDB["Agent State Table<br/>ID, Name, Status, Data"]
        StateData["Serialized State<br/>JSON/String Format"]
    end
    
    AgentState --> GetState
    GetState --> WasmExports
    WasmExports --> ActorState
    ActorState --> AgentDB
    AgentDB --> StateData
    
    StateData --> AgentDB
    AgentDB --> ActorState
    ActorState --> WasmExports
    WasmExports --> SetState
    SetState --> AgentState
```

### State Management Interface

The state management interface requires agents to implement two key methods:

- `GetState()`: Serializes the current agent state to a string representation
- `SetState(data)`: Deserializes and restores agent state from a string

Sources: [runtime/actors/agents.go:124-133](), [sdk/go/pkg/agents/agents.go:234-240](), [sdk/assemblyscript/src/assembly/agent.ts:42-50]()

## Event System

Agents can publish events to subscribers using a topic-based publish-subscribe system built on GoAkt's messaging infrastructure.

### Event Publishing Architecture

```mermaid
graph TB
    subgraph "Agent Instance"
        AgentCode["Agent Code<br/>PublishEvent(event)"]
        EventData["Event Data<br/>JSON Serialization"]
    end
    
    subgraph "Runtime Event System"
        PublishFunc["PublishAgentEvent<br/>Host Function"]
        EventMsg["AgentEvent Message<br/>Name, Data, Timestamp"]
        TopicActor["TopicActor<br/>GoAkt Topic System"]
    end
    
    subgraph "Event Distribution"
        AgentTopic["Agent Topic<br/>agent-{id}.events"]
        Subscribers["Event Subscribers<br/>Other Agents/Services"]
        EventHandlers["Event Handlers<br/>Application Logic"]
    end
    
    AgentCode --> EventData
    EventData --> PublishFunc
    PublishFunc --> EventMsg
    EventMsg --> TopicActor
    TopicActor --> AgentTopic
    AgentTopic --> Subscribers
    Subscribers --> EventHandlers
    
    style TopicActor fill:#f9f9f9
    style AgentTopic fill:#f0f8ff
```

### Event Message Structure

Events are structured as protobuf messages containing:
- `Name`: Event type identifier
- `Data`: Serialized event payload as `structpb.Value`
- `Timestamp`: Event creation timestamp

The topic naming convention follows the pattern `agent-{agentId}.events` for agent-specific event channels.

Sources: [runtime/actors/agents.go:204-256](), [sdk/go/pkg/agents/agents.go:294-304](), [sdk/assemblyscript/src/assembly/agent.ts:94-98]()

## Runtime Implementation Details

The runtime implementation centers around the `wasmAgentActor` which integrates with the GoAkt actor system to provide agent functionality.

### Actor System Integration

```mermaid
graph TB
    subgraph "GoAkt Actor System"
        ActorSystem["_actorSystem<br/>Global Actor System"]
        LocalActors["Local Actors<br/>Per-Agent Instances"]
        ActorSpawn["Actor Spawn<br/>WithLongLived Option"]
    end
    
    subgraph "Agent Actor Implementation"
        WasmAgentActor["wasmAgentActor<br/>Main Actor Type"]
        AgentInfo["wasmAgentInfo<br/>Dependency Injection"]
        ActorName["Actor Naming<br/>agent-{id}"]
    end
    
    subgraph "WASM Instance Management"
        PluginContext["Plugin Context<br/>WASM Module Info"]
        WasmExecution["WASM Function Calls<br/>Agent Lifecycle & Messages"]
        ContextPropagation["Context Propagation<br/>Agent ID & Name"]
    end
    
    ActorSystem --> LocalActors
    LocalActors --> ActorSpawn
    ActorSpawn --> WasmAgentActor
    WasmAgentActor --> AgentInfo
    WasmAgentActor --> ActorName
    
    WasmAgentActor --> PluginContext
    PluginContext --> WasmExecution
    WasmExecution --> ContextPropagation
    
    style ActorSystem fill:#f9f9f9
    style WasmAgentActor fill:#f9f9f9
```

### Key Runtime Components

| Component | File Location | Purpose |
|-----------|---------------|---------|
| `spawnActorForAgent` | [agents.go:79-99]() | Creates new actor instance for agent |
| `getActorName` | [agents.go:258-260]() | Generates unique actor names |
| `getAgentTopic` | [agents.go:262-264]() | Creates topic names for events |
| `wasmAgentInfo` | [agents.go:93-96]() | Dependency injection for actor context |

The actor system uses long-lived actors with dependency injection to maintain agent context and enable proper cleanup.

Sources: [runtime/actors/agents.go:79-99](), [runtime/actors/agents.go:258-264]()

## SDK Interfaces

The Agent System provides consistent interfaces across both Go and AssemblyScript SDKs for agent development.

### SDK Function Mapping

| Operation | Go SDK | AssemblyScript SDK | Runtime Function |
|-----------|--------|-------------------|------------------|
| Agent Registration | `agents.Register()` | `agents.register<T>()` | N/A (compile-time) |
| Start Agent | `agents.Start()` | `agents.start()` | `StartAgent` |
| Stop Agent | `agents.Stop()` | `agents.stop()` | `StopAgent` |
| Send Message | `agents.SendMessage()` | `agents.sendMessage()` | `SendAgentMessage` |
| Publish Event | `agent.PublishEvent()` | `agent.publishEvent()` | `PublishAgentEvent` |

### Agent Interface Requirements

Both SDKs require agents to implement core interface methods:

**Go SDK Interface:**
- `Name() string` - Agent identifier
- `GetState() *string` - State serialization  
- `SetState(data *string)` - State deserialization
- `OnInitialize() error` - Lifecycle callbacks
- `OnReceiveMessage(msgName string, data *string) (*string, error)` - Message handling

**AssemblyScript SDK Interface:**
- `get name(): string` - Agent identifier
- `getState(): string | null` - State serialization
- `setState(data: string | null): void` - State deserialization  
- `onInitialize(): void` - Lifecycle callbacks
- `onReceiveMessage(msgName: string, data: string | null): string | null` - Message handling

Sources: [sdk/go/pkg/agents/agents.go:220-263](), [sdk/assemblyscript/src/assembly/agent.ts:22-99](), [runtime/hostfunctions/agents.go:18-53]()

---

# Page: Database Integration

# Database Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [runtime/dgraphclient/registry.go](runtime/dgraphclient/registry.go)
- [runtime/neo4jclient/registry.go](runtime/neo4jclient/registry.go)
- [runtime/sqlclient/registry.go](runtime/sqlclient/registry.go)
- [runtime/sqlclient/sqlclient.go](runtime/sqlclient/sqlclient.go)
- [runtime/timezones/timezones.go](runtime/timezones/timezones.go)

</details>



This document covers the database integration system within the Modus Runtime, detailing how the runtime manages connections to various database systems including PostgreSQL, MySQL, Dgraph, and Neo4j. The system provides a unified interface for database operations while maintaining type-specific optimizations for each database technology.

For information about configuring database connections, see [Connections and Secrets](#6.2). For details about the overall runtime architecture, see [Runtime Architecture](#5.1).

## Architecture Overview

The Modus Runtime implements a registry-based database client system that manages persistent connections to multiple database types. Each database type has its own specialized client registry that handles connection pooling, lifecycle management, and type-specific optimizations.

### Database Client Architecture

```mermaid
graph TB
    subgraph "Database Client Layer"
        SQLClient["sqlclient<br/>SQL Database Interface"]
        DgraphClient["dgraphclient<br/>Dgraph Interface"] 
        Neo4jClient["neo4jclient<br/>Neo4j Interface"]
    end
    
    subgraph "Registry System"
        DSRegistry["dsRegistry<br/>SQL Connection Registry"]
        DgraphRegistry["dgraphRegistry<br/>Dgraph Connection Registry"]
        Neo4jRegistry["neo4jRegistry<br/>Neo4j Connection Registry"]
    end
    
    subgraph "Connection Management"
        PostgresDS["postgresqlDS<br/>PostgreSQL DataSource"]
        MysqlDS["mysqlDS<br/>MySQL DataSource"]
        DgraphConn["dgraphConnector<br/>Dgraph Connection"]
        Neo4jDriver["neo4j.DriverWithContext<br/>Neo4j Driver"]
    end
    
    subgraph "External Dependencies"
        ManifestData["manifestdata<br/>Configuration Source"]
        Secrets["secrets<br/>Secret Management"]
        XSync["xsync.Map<br/>Concurrent Cache"]
    end
    
    SQLClient --> DSRegistry
    DgraphClient --> DgraphRegistry
    Neo4jClient --> Neo4jRegistry
    
    DSRegistry --> PostgresDS
    DSRegistry --> MysqlDS
    DgraphRegistry --> DgraphConn
    Neo4jRegistry --> Neo4jDriver
    
    DSRegistry --> XSync
    DgraphRegistry --> XSync
    Neo4jRegistry --> XSync
    
    DSRegistry --> ManifestData
    DgraphRegistry --> ManifestData
    Neo4jRegistry --> ManifestData
    
    DSRegistry --> Secrets
    DgraphRegistry --> Secrets
    Neo4jRegistry --> Secrets
```

Sources: [runtime/sqlclient/registry.go:19-64](), [runtime/dgraphclient/registry.go:27-97](), [runtime/neo4jclient/registry.go:24-97]()

## SQL Database Integration

The SQL database system supports PostgreSQL and MySQL through a unified interface that abstracts connection management and query execution.

### SQL Registry Implementation

The `dsRegistry` maintains a cache of database connections using the `xsync.Map` for thread-safe operations:

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `dsRegistry` | Connection cache and factory | `getDataSource()`, `shutdown()` |
| `dataSource` | Abstract database interface | `query()`, `Shutdown()` |
| `postgresqlDS` | PostgreSQL implementation | Database-specific query handling |
| `mysqlDS` | MySQL implementation | Database-specific query handling |

The registry uses a lazy-loading pattern where connections are created on first access and cached for subsequent use. The `getDataSource` method in [runtime/sqlclient/registry.go:40-64]() implements this pattern with error handling for unsupported database types.

### Query Execution Flow

```mermaid
sequenceDiagram
    participant Client as "WASM Function"
    participant SQLClient as "sqlclient.ExecuteQuery"
    participant Registry as "dsRegistry"
    participant DataSource as "dataSource"
    participant Database as "Database"
    
    Client->>SQLClient: "ExecuteQuery(ctx, connectionName, dbType, statement, paramsJson)"
    SQLClient->>SQLClient: "Parse paramsJson and flags"
    SQLClient->>Registry: "getDataSource(ctx, dsName, dsType)"
    
    alt "Connection exists in cache"
        Registry->>Registry: "Load from xsync.Map cache"
    else "New connection needed"
        Registry->>DataSource: "newPostgresqlDS() or newMysqlDS()"
        DataSource->>Database: "Establish connection"
        Registry->>Registry: "Store in cache"
    end
    
    Registry->>SQLClient: "Return dataSource"
    SQLClient->>DataSource: "query(ctx, stmt, params, execOnly)"
    DataSource->>Database: "Execute SQL query"
    Database->>DataSource: "Return results"
    DataSource->>SQLClient: "Return dbResponse"
    SQLClient->>SQLClient: "Serialize to HostQueryResponse"
    SQLClient->>Client: "Return JSON response"
```

Sources: [runtime/sqlclient/sqlclient.go:34-88](), [runtime/sqlclient/registry.go:40-64]()

## Dgraph Integration

The Dgraph client provides integration with Dgraph graph databases, supporting both connection string and gRPC target configurations.

### Dgraph Connection Management

The `dgraphRegistry` implements connection caching with support for multiple connection methods:

```mermaid
graph TB
    subgraph "Connection Configuration"
        ConnStr["ConnStr<br/>Connection String Method"]
        GrpcTarget["GrpcTarget + Key<br/>gRPC Method"]
    end
    
    subgraph "dgraphRegistry"
        Cache["xsync.Map[string, *dgraphConnector]<br/>Connection Cache"]
        GetConnector["getDgraphConnector()<br/>Lazy Loading"]
    end
    
    subgraph "Connection Creation"
        CreateConnector["createConnector()<br/>Factory Method"]
        ConnStrMethod["connectWithConnectionString()<br/>dgo.Open()"]
        GrpcMethod["connectWithGrpcTarget()<br/>dgo.NewClient()"]
    end
    
    subgraph "Dgraph Client"
        DgraphConnector["dgraphConnector<br/>Connection Wrapper"]
        DgoClient["dgo.Dgraph<br/>Official Client"]
    end
    
    ConnStr --> CreateConnector
    GrpcTarget --> CreateConnector
    CreateConnector --> ConnStrMethod
    CreateConnector --> GrpcMethod
    
    GetConnector --> Cache
    GetConnector --> CreateConnector
    
    ConnStrMethod --> DgraphConnector
    GrpcMethod --> DgraphConnector
    DgraphConnector --> DgoClient
```

The connection creation logic in [runtime/dgraphclient/registry.go:61-97]() handles different authentication methods:
- Connection strings for direct connections
- gRPC targets with API keys for Dgraph Cloud
- Bearer tokens for custom deployments
- Insecure connections for localhost development

Sources: [runtime/dgraphclient/registry.go:48-134]()

## Neo4j Integration

The Neo4j client manages connections to Neo4j graph databases using the official Neo4j Go driver with basic authentication.

### Neo4j Connection Lifecycle

The `neo4jRegistry` follows the same caching pattern as other database clients:

| Function | Purpose | Key Operations |
|----------|---------|----------------|
| `getDriver()` | Retrieve cached or create new driver | Cache lookup, lazy creation |
| `createDriver()` | Factory method for Neo4j drivers | Manifest validation, secret resolution |
| `validateNeo4jConnection()` | Configuration validation | Required field checking |
| `CloseDrivers()` | Cleanup on shutdown | Driver cleanup, cache clearing |

The driver creation process in [runtime/neo4jclient/registry.go:58-97]() involves:
1. Loading connection configuration from manifest
2. Validating required fields (DbUri, Username, Password)
3. Applying secret resolution to connection parameters
4. Creating Neo4j driver with basic authentication

Sources: [runtime/neo4jclient/registry.go:45-120]()

## Configuration Integration

All database clients integrate with the Modus manifest system for configuration and the secrets system for credential management.

### Manifest Integration Pattern

```mermaid
graph LR
    subgraph "Configuration Sources"
        ManifestJSON["modus.json<br/>Application Manifest"]
        SecretsManager["secrets<br/>Secret Resolution"]
    end
    
    subgraph "Runtime Components"
        ManifestData["manifestdata.GetManifest()<br/>Configuration Access"]
        ConnectionInfo["ConnectionInfo<br/>Type-specific Config"]
    end
    
    subgraph "Database Clients"
        SQLGetConn["getConnectionString()<br/>SQL Clients"]
        DgraphCreate["createConnector()<br/>Dgraph Client"]
        Neo4jCreate["createDriver()<br/>Neo4j Client"]
    end
    
    ManifestJSON --> ManifestData
    ManifestData --> ConnectionInfo
    
    ConnectionInfo --> SQLGetConn
    ConnectionInfo --> DgraphCreate
    ConnectionInfo --> Neo4jCreate
    
    SecretsManager --> SQLGetConn
    SecretsManager --> DgraphCreate
    SecretsManager --> Neo4jCreate
```

Each database client follows a consistent pattern for configuration access:
1. Retrieve connection configuration from `manifestdata.GetManifest()`
2. Validate connection type matches expected database type
3. Apply secret resolution using `secrets.ApplySecretsToString()`
4. Create database-specific connection objects

Sources: [runtime/sqlclient/sqlclient.go:90-121](), [runtime/dgraphclient/registry.go:61-96](), [runtime/neo4jclient/registry.go:58-87]()

## Connection Lifecycle Management

The database integration system implements proper lifecycle management with initialization callbacks and shutdown procedures.

### Shutdown Coordination

Each database client registry implements cleanup methods that are coordinated through the runtime:

| Registry | Shutdown Method | Cleanup Actions |
|----------|----------------|-----------------|
| `dsRegistry` | `shutdown()` | Close all cached data sources |
| `dgraphRegistry` | `ShutdownConns()` | Close all Dgraph clients |
| `neo4jRegistry` | `CloseDrivers()` | Close all Neo4j drivers |

The SQL client also registers a manifest reload callback in [runtime/sqlclient/sqlclient.go:23-28]() to ensure connections are refreshed when configuration changes.

Sources: [runtime/sqlclient/registry.go:31-38](), [runtime/dgraphclient/registry.go:39-46](), [runtime/neo4jclient/registry.go:36-43]()

---

# Page: AI Model Integration

# AI Model Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [runtime/models/models.go](runtime/models/models.go)
- [runtime/utils/http.go](runtime/utils/http.go)
- [runtime/utils/http_test.go](runtime/utils/http_test.go)
- [runtime/wasmhost/fncall.go](runtime/wasmhost/fncall.go)
- [runtime/wasmhost/hostfns.go](runtime/wasmhost/hostfns.go)
- [sdk/go/pkg/models/models.go](sdk/go/pkg/models/models.go)
- [sdk/go/pkg/models/openai/chat.go](sdk/go/pkg/models/openai/chat.go)
- [sdk/go/tools/modus-go-build/codegen/preprocess.go](sdk/go/tools/modus-go-build/codegen/preprocess.go)

</details>



This document covers how the Modus Runtime integrates with AI models, including the architecture for model invocation, connection management, and the SDK interfaces developers use to interact with models. The system provides a type-safe, language-agnostic way to invoke AI models through WebAssembly host functions.

For information about database integration, see [Database Integration](#5.4). For details about the agent system, see [Agent System](#5.3).

## System Architecture

The AI model integration system consists of three primary layers that work together to provide seamless model invocation:

### Model Integration Architecture

```mermaid
graph TB
    subgraph "Developer Code"
        DevCode["Developer Functions"]
    end
    
    subgraph "SDK Layer"
        GoSDK["Go SDK Models"]
        ModelBase["ModelBase[TIn,TOut]"]
        ModelInterface["Model Interface"]
        OpenAIChat["OpenAI ChatModel"]
    end
    
    subgraph "WebAssembly Bridge"
        HostFunctions["Host Functions"]
        hostGetModelInfo["hostGetModelInfo()"]
        hostInvokeModel["hostInvokeModel()"]
    end
    
    subgraph "Runtime Layer"
        ModelsPackage["runtime/models"]
        GetModel["GetModel()"]
        InvokeModel["InvokeModel()"]
        PostToModelEndpoint["PostToModelEndpoint()"]
    end
    
    subgraph "External Services"
        OpenAIAPI["OpenAI API"]
        HypermodeAPI["Hypermode API"]
        CustomAPI["Custom Model APIs"]
    end
    
    subgraph "Configuration"
        Manifest["modus.json"]
        Connections["HTTP Connections"]
        Secrets["API Keys & Secrets"]
    end
    
    DevCode --> GoSDK
    GoSDK --> ModelBase
    ModelBase --> ModelInterface
    OpenAIChat --> ModelBase
    
    ModelInterface --> hostGetModelInfo
    ModelInterface --> hostInvokeModel
    
    hostGetModelInfo --> GetModel
    hostInvokeModel --> InvokeModel
    
    GetModel --> Manifest
    InvokeModel --> PostToModelEndpoint
    PostToModelEndpoint --> OpenAIAPI
    PostToModelEndpoint --> HypermodeAPI
    PostToModelEndpoint --> CustomAPI
    
    PostToModelEndpoint --> Connections
    Connections --> Secrets
```

Sources: [runtime/models/models.go:1-144](), [sdk/go/pkg/models/models.go:1-117](), [sdk/go/pkg/models/openai/chat.go:1-100]()

## Model Configuration and Manifest Integration

Models are configured in the application manifest and accessed through the runtime's model management system:

### Model Configuration Flow

```mermaid
graph LR
    subgraph "Configuration Sources"
        ModusJSON["modus.json"]
        HTTPConnections["HTTP Connections"]
        SecretsStore["Secrets Store"]
    end
    
    subgraph "Runtime Model Management"
        manifestdata["manifestdata.GetManifest()"]
        GetModel["models.GetModel()"]
        GetModelInfo["models.GetModelInfo()"]
    end
    
    subgraph "Model Metadata"
        ModelInfo["manifest.ModelInfo"]
        ConnectionInfo["manifest.HTTPConnectionInfo"]
        ModelInfoStruct["ModelInfo{Name,FullName}"]
    end
    
    ModusJSON --> manifestdata
    HTTPConnections --> manifestdata
    SecretsStore --> manifestdata
    
    manifestdata --> GetModel
    GetModel --> ModelInfo
    ModelInfo --> ConnectionInfo
    GetModel --> GetModelInfo
    GetModelInfo --> ModelInfoStruct
```

Sources: [runtime/models/models.go:28-49](), [runtime/manifestdata](), [lib/manifest]()

## Model Invocation Process

The model invocation process involves several steps from SDK call to HTTP response:

### Model Invocation Flow

```mermaid
sequenceDiagram
    participant SDK as "SDK ModelBase"
    participant HostFn as "Host Functions"
    participant Runtime as "Runtime models"
    participant HTTP as "HTTP Client"
    participant Model as "AI Model API"
    participant DB as "Database"
    
    SDK->>HostFn: hostInvokeModel(modelName, inputJSON)
    HostFn->>Runtime: InvokeModel(ctx, modelName, input)
    Runtime->>Runtime: GetModel(modelName)
    Runtime->>Runtime: getModelEndpointUrl()
    Runtime->>HTTP: PostToModelEndpoint()
    HTTP->>Model: HTTP POST with payload
    Model->>HTTP: JSON Response
    HTTP->>Runtime: HttpResult[TResult]
    Runtime->>DB: WriteInferenceHistory()
    Runtime->>HostFn: Response string
    HostFn->>SDK: JSON output
    SDK->>SDK: JsonDeserialize to TOut
```

Sources: [runtime/models/models.go:51-118](), [sdk/go/pkg/models/models.go:76-116](), [runtime/utils/http.go:68-130]()

## SDK Model Interface

The SDK provides a generic, type-safe interface for model interaction:

### Core Model Types

| Type | Purpose | Key Methods |
|------|---------|-------------|
| `Model[TIn, TOut]` | Generic model interface | `Info()`, `Invoke()` |
| `ModelBase[TIn, TOut]` | Base implementation | `Invoke()`, `setInfo()` |
| `ModelInfo` | Model metadata | `Name`, `FullName` fields |

### Generic Model Usage Pattern

The SDK uses Go generics to provide type safety:

```go
// Get a model instance
model, err := GetModel[ChatModel](modelName)

// Invoke with typed input/output
output, err := model.Invoke(input)
```

The `GetModel` function signature demonstrates the generic pattern:
```go
func GetModel[TModel Model[TIn, TOut], TIn, TOut any, P modelPtr[TModel]](name string) (*TModel, error)
```

Sources: [sdk/go/pkg/models/models.go:30-74](), [sdk/go/pkg/models/models.go:76-116]()

## OpenAI Chat API Implementation

The OpenAI Chat API implementation provides a comprehensive example of the model integration pattern:

### OpenAI Chat Model Structure

```mermaid
graph TB
    subgraph "ChatModel Implementation"
        ChatModel["ChatModel struct"]
        ChatModelInput["ChatModelInput struct"]
        ChatModelOutput["ChatModelOutput struct"]
    end
    
    subgraph "Message Types"
        SystemMessage["SystemMessage[T]"]
        UserMessage["UserMessage[T]"]
        AssistantMessage["AssistantMessage[T]"]
        ToolMessage["ToolMessage[T]"]
    end
    
    subgraph "Content Types"
        TextContent["TextContentPart"]
        ImageContent["ImageContentPart"]
        AudioContent["AudioContentPart"]
        RefusalContent["RefusalContentPart"]
    end
    
    subgraph "Configuration"
        ResponseFormat["ResponseFormat"]
        ToolChoice["ToolChoice"]
        AudioParameters["AudioParameters"]
    end
    
    ChatModel --> ChatModelInput
    ChatModel --> ChatModelOutput
    
    ChatModelInput --> SystemMessage
    ChatModelInput --> UserMessage
    ChatModelInput --> AssistantMessage
    ChatModelInput --> ToolMessage
    
    SystemMessage --> TextContent
    UserMessage --> TextContent
    UserMessage --> ImageContent
    UserMessage --> AudioContent
    AssistantMessage --> RefusalContent
    
    ChatModelInput --> ResponseFormat
    ChatModelInput --> ToolChoice
    ChatModelInput --> AudioParameters
```

### Key OpenAI Features

| Feature | Implementation | Purpose |
|---------|----------------|---------|
| Multi-modal Input | `TextContentPart`, `ImageContentPart`, `AudioContentPart` | Support text, images, and audio |
| Tool Calling | `ToolChoice`, `ToolCall`, `FunctionCall` | Enable function calling |
| Response Formats | `ResponseFormatText`, `ResponseFormatJson`, `ResponseFormatJsonSchema` | Control output format |
| Audio Output | `AudioParameters`, `AudioOutput` | Generate spoken responses |

Sources: [sdk/go/pkg/models/openai/chat.go:31-302](), [sdk/go/pkg/models/openai/chat.go:360-1050]()

## HTTP Connection Management

The runtime manages HTTP connections and handles authentication for different model providers:

### Connection Types and Authentication

```mermaid
graph TB
    subgraph "Connection Types"
        HypermodeConnection["Hypermode Connection"]
        CustomHTTPConnection["Custom HTTP Connection"]
    end
    
    subgraph "Authentication Methods"
        HypermodeAuth["authenticateHypermodeModelRequest()"]
        SecretsAuth["secrets.ApplySecretsToHttpRequest()"]
    end
    
    subgraph "URL Resolution"
        BaseURL["connection.BaseURL + model.Path"]
        DirectEndpoint["connection.Endpoint"]
    end
    
    subgraph "Error Handling"
        StatusNotFound["404: Model not available"]
        StatusUnauthorized["401: Invalid API key"]
        StatusForbidden["403: Disabled/limit exceeded"]
        StatusTooManyRequests["429: Rate limit exceeded"]
    end
    
    HypermodeConnection --> HypermodeAuth
    CustomHTTPConnection --> SecretsAuth
    
    HypermodeConnection --> BaseURL
    HypermodeConnection --> DirectEndpoint
    CustomHTTPConnection --> BaseURL
    CustomHTTPConnection --> DirectEndpoint
    
    BaseURL --> StatusNotFound
    DirectEndpoint --> StatusUnauthorized
    BaseURL --> StatusForbidden
    DirectEndpoint --> StatusTooManyRequests
```

Sources: [runtime/models/models.go:66-118](), [runtime/models/models.go:120-143](), [runtime/httpclient](), [runtime/secrets]()

## Host Function Integration

The WebAssembly host functions bridge the SDK and runtime layers:

### Host Function Registration

The runtime registers model-related host functions that the SDK can call:

| Host Function | Purpose | Parameters |
|---------------|---------|------------|
| `hostGetModelInfo` | Retrieve model metadata | `modelName string` |
| `hostInvokeModel` | Invoke model with input | `modelName string, input string` |

### Host Function Implementation Pattern

The host functions follow the standard pattern established in the WebAssembly host system:

1. **Parameter Decoding**: Convert WebAssembly stack values to Go types
2. **Context Propagation**: Pass execution context through the call chain
3. **Error Handling**: Log errors and handle different error types
4. **Result Encoding**: Convert Go return values back to WebAssembly format

Sources: [runtime/wasmhost/hostfns.go:86-350](), [sdk/go/pkg/models/models.go:65-116]()

## Error Handling and Logging

The model integration system provides comprehensive error handling:

### Error Categories

| Error Type | HTTP Status | Handling |
|------------|-------------|----------|
| Model Not Found | 404 | Environment-specific messaging |
| Authentication Error | 401 | API key validation message |
| Access Forbidden | 403 | Usage limit/disabled message |
| Rate Limited | 429 | Rate limit exceeded message |
| Invalid Response | N/A | JSON validation and parsing |

### Inference History Logging

All model invocations are logged to the database for tracking and debugging:

```go
db.WriteInferenceHistory(ctx, model, payload, res.Data, res.StartTime, res.EndTime)
```

Sources: [runtime/models/models.go:94-118](), [runtime/db]()

## Performance and Monitoring

The system includes performance monitoring and metrics collection:

### HTTP Request Timing

The `HttpResult[T]` type captures timing information:
- `StartTime`: Request initiation
- `EndTime`: Response completion  
- `Duration()`: Calculated execution time

### Sentry Integration

All model operations are instrumented with Sentry spans for distributed tracing:

```go
span, ctx := utils.NewSentrySpanForCurrentFunc(ctx)
defer span.Finish()
```

Sources: [runtime/utils/http.go:58-66](), [runtime/models/models.go:67-68](), [runtime/utils]()

---

# Page: Configuration

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lib/manifest/dgraph.go](lib/manifest/dgraph.go)
- [lib/manifest/go.sum](lib/manifest/go.sum)
- [lib/manifest/manifest.go](lib/manifest/manifest.go)
- [lib/manifest/modus_schema.json](lib/manifest/modus_schema.json)
- [lib/manifest/test/manifest_test.go](lib/manifest/test/manifest_test.go)
- [lib/manifest/test/valid_modus.json](lib/manifest/test/valid_modus.json)
- [runtime/dgraphclient/dgraph.go](runtime/dgraphclient/dgraph.go)

</details>



This document covers the Modus configuration system, which manages application settings through manifest files and connection definitions. The configuration system handles endpoint definitions, AI model configurations, database connections, and secret management through template variables.

For information about deploying configured applications, see [Deployment and Operations](#8). For details about the manifest file structure validation, see [Application Manifests](#6.1). For connection and secret management specifics, see [Connections and Secrets](#6.2).

## Configuration System Architecture

The Modus configuration system is built around the `modus.json` manifest file, which serves as the central configuration source for applications. The system provides type-safe parsing, JSON schema validation, and template variable resolution for secrets.

**Configuration System Components**

```mermaid
graph TD
    subgraph "Configuration Files"
        ModusJSON["modus.json<br/>Main Manifest"]
        Schema["modus_schema.json<br/>JSON Schema"]
        EnvVars["Environment Variables<br/>Secret Values"]
    end
    
    subgraph "Manifest Library"
        ManifestGo["manifest.go<br/>Manifest struct"]
        Validator["ValidateManifest()<br/>Schema Validation"]
        Parser["ReadManifest()<br/>JSON Parser"]
        Variables["GetVariables()<br/>Variable Extractor"]
    end
    
    subgraph "Connection Types"
        HTTPConn["HTTPConnectionInfo"]
        PostgresConn["PostgresqlConnectionInfo"]
        MySQLConn["MysqlConnectionInfo"]
        DgraphConn["DgraphConnectionInfo"]
        Neo4jConn["Neo4jConnectionInfo"]
    end
    
    subgraph "Runtime Usage"
        GraphQLEngine["GraphQL Engine<br/>Endpoint Config"]
        DatabaseClients["Database Clients<br/>Connection Pool"]
        ModelInvocation["Model Invocation<br/>AI Service Calls"]
    end
    
    ModusJSON --> Validator
    Schema --> Validator
    Validator --> Parser
    Parser --> ManifestGo
    
    ManifestGo --> HTTPConn
    ManifestGo --> PostgresConn
    ManifestGo --> MySQLConn
    ManifestGo --> DgraphConn
    ManifestGo --> Neo4jConn
    
    Variables --> EnvVars
    
    ManifestGo --> GraphQLEngine
    HTTPConn --> ModelInvocation
    PostgresConn --> DatabaseClients
    MySQLConn --> DatabaseClients
    DgraphConn --> DatabaseClients
    Neo4jConn --> DatabaseClients
```

Sources: [lib/manifest/manifest.go:35-40](), [lib/manifest/modus_schema.json:1-318]()

## Manifest File Structure

The `modus.json` file defines three main configuration sections: endpoints, models, and connections. The manifest uses version 3 of the schema and supports JSON with comments (JSONC format).

**Manifest Core Structure**

```mermaid
graph LR
    subgraph "Manifest struct"
        Version["Version int<br/>Schema Version"]
        Endpoints["Endpoints map[string]EndpointInfo"]
        Models["Models map[string]ModelInfo"]
        Connections["Connections map[string]ConnectionInfo"]
    end
    
    subgraph "Endpoint Types"
        GraphQL["GraphqlEndpointInfo<br/>Type: 'graphql'"]
    end
    
    subgraph "Model Configuration"
        SourceModel["SourceModel string<br/>Model Identifier"]
        Provider["Provider string<br/>e.g. 'hugging-face'"]
        Connection["Connection string<br/>Connection Name"]
        Path["Path string<br/>Model Path"]
    end
    
    Endpoints --> GraphQL
    Models --> SourceModel
    Models --> Provider
    Models --> Connection
    Models --> Path
```

Sources: [lib/manifest/manifest.go:35-40](), [lib/manifest/test/valid_modus.json:1-95]()

### Endpoint Configuration

Endpoints define GraphQL API access points with authentication settings. The default endpoint configuration provides a GraphQL interface at `/graphql` with bearer token authentication.

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `type` | string | Endpoint type (currently only "graphql") | - |
| `path` | string | URL path for the endpoint | "/graphql" |
| `auth` | string | Authentication type ("none" or "bearer-token") | "bearer-token" |

Example endpoint configuration:
```json
{
  "endpoints": {
    "default": {
      "type": "graphql",
      "path": "/graphql", 
      "auth": "bearer-token"
    }
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:4-9](), [lib/manifest/modus_schema.json:15-55]()

### Model Configuration

Models define AI model access through either the Hypermode platform or external connections. Models can reference Hugging Face models through the built-in "hypermode" connection or custom HTTP connections.

**Model Configuration Types**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sourceModel` | string | Yes | Model identifier from provider |
| `provider` | string | For hypermode | Provider name (e.g., "hugging-face") |
| `connection` | string | Yes | Connection name ("hypermode" or custom) |
| `path` | string | Optional | Model endpoint path for custom connections |

Example model configurations:
```json
{
  "models": {
    "model-1": {
      "sourceModel": "example/source-model-1",
      "provider": "hugging-face",
      "connection": "hypermode"
    },
    "model-2": {
      "sourceModel": "source-model-2", 
      "connection": "my-model-connection",
      "path": "path/to/model-2"
    }
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:11-25](), [lib/manifest/modus_schema.json:57-121]()

## Connection Types

The configuration system supports multiple connection types for databases and HTTP services. Each connection type has specific fields and validation rules defined in the JSON schema.

**Connection Type Implementation**

```mermaid
graph TD
    subgraph "ConnectionInfo Interface"
        ConnName["ConnectionName() string"]
        ConnType["ConnectionType() ConnectionType"]
        Hash["Hash() string"]
        Variables["Variables() []string"]
    end
    
    subgraph "HTTP Connections"
        HTTPType["Type: 'http'"]
        BaseURL["BaseURL string<br/>Base URL with trailing slash"]
        Endpoint["Endpoint string<br/>Full URL endpoint"]
        Headers["Headers map[string]string"]
        QueryParams["QueryParameters map[string]string"]
    end
    
    subgraph "Database Connections"
        PostgresType["Type: 'postgresql'"]
        MySQLType["Type: 'mysql'"]
        DgraphType["Type: 'dgraph'"]
        Neo4jType["Type: 'neo4j'"]
        ConnStr["ConnStr string<br/>Connection String"]
    end
    
    subgraph "Dgraph Specific"
        GrpcTarget["GrpcTarget string<br/>gRPC Address"]
        Key["Key string<br/>API Key"]
    end
    
    ConnName --> HTTPType
    ConnName --> PostgresType
    HTTPType --> BaseURL
    HTTPType --> Endpoint
    HTTPType --> Headers
    HTTPType --> QueryParams
    
    PostgresType --> ConnStr
    MySQLType --> ConnStr
    DgraphType --> ConnStr
    DgraphType --> GrpcTarget
    DgraphType --> Key
```

Sources: [lib/manifest/manifest.go:153-191](), [lib/manifest/dgraph.go:14-20]()

### HTTP Connections

HTTP connections support both base URL and full endpoint configurations. They can include custom headers and query parameters for authentication and API access.

**HTTP Connection Configuration**

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `type` | string | Must be "http" | Required |
| `baseUrl` | string | Base URL ending with "/" | Use for path-based APIs |
| `endpoint` | string | Complete URL | Use for single endpoint APIs |
| `headers` | object | HTTP headers | Supports template variables |
| `queryParameters` | object | Query parameters | Supports template variables |

Example HTTP connections:
```json
{
  "connections": {
    "my-rest-api": {
      "type": "http",
      "baseUrl": "https://api.example.com/v1/",
      "queryParameters": {
        "api_token": "{{API_TOKEN}}"
      }
    },
    "my-graphql-api": {
      "type": "http", 
      "endpoint": "https://api.example.com/graphql",
      "headers": {
        "Authorization": "Bearer {{AUTH_TOKEN}}"
      }
    }
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:49-62](), [lib/manifest/modus_schema.json:132-202]()

### Database Connections

Database connections use connection strings following standard URI formats. Each database type has specific connection string patterns validated by the JSON schema.

**Database Connection Types**

| Database | Type | Connection String Pattern | Example |
|----------|------|--------------------------|---------|
| PostgreSQL | `postgresql` | `postgresql://user:pass@host:port/db` | `postgresql://{{USER}}:{{PASS}}@localhost:5432/mydb` |
| MySQL | `mysql` | `mysql://user:pass@host:port/db` | `mysql://{{USER}}:{{PASS}}@localhost:3306/mydb` |
| Dgraph | `dgraph` | `dgraph://host:port` or gRPC target | `dgraph://localhost:9080` |
| Neo4j | `neo4j` | `bolt://host:port` or `neo4j://host:port` | `bolt://localhost:7687` |

Example database connections:
```json
{
  "connections": {
    "neon": {
      "type": "postgresql",
      "connString": "postgresql://{{POSTGRESQL_USERNAME}}:{{POSTGRESQL_PASSWORD}}@1.2.3.4:5432/data?sslmode=disable"
    },
    "my-dgraph-cloud": {
      "type": "dgraph", 
      "grpcTarget": "frozen-mango.grpc.eu-central-1.aws.cloud.dgraph.io:443",
      "key": "{{DGRAPH_KEY}}"
    }
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:63-93](), [lib/manifest/modus_schema.json:204-311]()

## Variable Templating

The configuration system supports template variables for secrets and environment-specific values. Variables are enclosed in double braces (`{{VARIABLE_NAME}}`) and resolved at runtime from environment variables.

**Variable Resolution Process**

```mermaid
sequenceDiagram
    participant Config as "Configuration File"
    participant Parser as "parseManifestJson()"
    participant Extractor as "GetVariables()"
    participant Runtime as "Runtime"
    participant Env as "Environment Variables"
    
    Config->>Parser: Load modus.json
    Parser->>Parser: Parse connection configs
    Parser->>Extractor: Extract {{VARIABLES}}
    Extractor->>Extractor: extractVariables() per connection
    Extractor->>Runtime: Return variable map
    Runtime->>Env: Resolve variable values
    Runtime->>Runtime: Substitute values in connections
```

Sources: [lib/manifest/manifest.go:46-57](), [lib/manifest/test/manifest_test.go:262-286]()

### Variable Extraction

The `GetVariables()` method extracts all template variables from connection configurations, returning a map of connection names to their required variables.

Example variable extraction result:
```go
map[string][]string{
    "my-model-connection":      {"API_KEY"},
    "my-graphql-api":           {"AUTH_TOKEN"},
    "neon":                     {"POSTGRESQL_USERNAME", "POSTGRESQL_PASSWORD"},
    "my-dgraph-cloud":          {"DGRAPH_KEY"},
}
```

### Advanced Variable Functions

The system supports function-style variable templating for complex transformations:

| Function | Usage | Description |
|----------|-------|-------------|
| `base64()` | `{{base64(USERNAME:PASSWORD)}}` | Base64 encode credentials |

Example with function:
```json
{
  "headers": {
    "Authorization": "Basic {{base64(USERNAME:PASSWORD)}}"
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:60](), [lib/manifest/test/manifest_test.go:269]()

## Schema Validation

The configuration system includes comprehensive JSON schema validation through the `ValidateManifest()` function. The schema enforces naming conventions, required fields, and format validation for all configuration elements.

**Validation Rules**

| Element | Rule | Pattern |
|---------|------|---------|
| Connection names | Alphanumeric with hyphens | `^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$` |
| Model names | Alphanumeric with hyphens | `^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$` |
| Endpoint paths | Must start with "/" | `^\/\S*$` |
| HTTP URLs | Valid URI format | Standard URI validation |
| Database URIs | Database-specific patterns | Protocol-specific validation |

The validation process uses the `jsonschema` library with a compiled schema loaded at package initialization:

```go
func ValidateManifest(content []byte) error {
    r := bytes.NewReader(jsonc.ToJSON(content))
    doc, err := jsonschema.UnmarshalJSON(r)
    if err != nil {
        return fmt.Errorf("failed to parse manifest: %w", err)
    }
    
    if err := schema.Validate(doc); err != nil {
        return fmt.Errorf("failed to validate manifest: %w", err)
    }
    
    return nil
}
```

Sources: [lib/manifest/manifest.go:81-93](), [lib/manifest/modus_schema.json:17-23]()

---

# Page: Application Manifests

# Application Manifests

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lib/manifest/dgraph.go](lib/manifest/dgraph.go)
- [lib/manifest/go.sum](lib/manifest/go.sum)
- [lib/manifest/manifest.go](lib/manifest/manifest.go)
- [lib/manifest/modus_schema.json](lib/manifest/modus_schema.json)
- [lib/manifest/test/manifest_test.go](lib/manifest/test/manifest_test.go)
- [lib/manifest/test/valid_modus.json](lib/manifest/test/valid_modus.json)
- [runtime/dgraphclient/dgraph.go](runtime/dgraphclient/dgraph.go)

</details>



Application manifests define the configuration and external dependencies for Modus applications through a `modus.json` file. The manifest specifies GraphQL endpoints, AI model integrations, and database connections that the application requires at runtime. The Modus runtime uses this configuration to initialize services, validate connections, and generate GraphQL schemas.

For information about connection secrets and environment variable management, see [Connections and Secrets](#6.2). For details about the runtime's use of manifest data, see [Runtime Architecture](#5.1).

## Manifest File Structure

The `modus.json` file is a JSON configuration file that follows a defined schema and contains three main sections: endpoints, models, and connections. The manifest uses version 3 of the schema format and supports JSON comments for documentation.

```mermaid
graph TD
    subgraph "modus.json Structure"
        ManifestFile["modus.json<br/>Application Manifest"]
        
        ManifestFile --> Endpoints["endpoints:<br/>GraphQL API Configuration"]
        ManifestFile --> Models["models:<br/>AI Model Definitions"]
        ManifestFile --> Connections["connections:<br/>External Service Connections"]
        
        Endpoints --> DefaultEndpoint["default:<br/>Primary GraphQL Endpoint"]
        
        Models --> ModelDefs["model-1, model-2, model-3:<br/>Named Model Instances"]
        
        Connections --> HTTPConn["HTTP Connections:<br/>REST APIs, Model Endpoints"]
        Connections --> DBConn["Database Connections:<br/>PostgreSQL, MySQL, Dgraph, Neo4j"]
    end
    
    subgraph "Runtime Processing"
        ManifestReader["manifest.ReadManifest()"]
        SchemaValidator["manifest.ValidateManifest()"]
        VariableExtractor["manifest.GetVariables()"]
    end
    
    ManifestFile --> ManifestReader
    ManifestFile --> SchemaValidator
    ManifestReader --> VariableExtractor
```

The manifest structure is defined by the `Manifest` struct which contains maps of named configuration objects:

| Section | Purpose | Key Type | Value Type |
|---------|---------|----------|------------|
| `endpoints` | GraphQL API endpoints | string | `EndpointInfo` |
| `models` | AI model definitions | string | `ModelInfo` |
| `connections` | External service connections | string | `ConnectionInfo` |

Sources: [lib/manifest/manifest.go:35-40](), [lib/manifest/test/valid_modus.json:1-95]()

## Endpoints Configuration

Endpoints define the GraphQL API interfaces that the Modus runtime exposes. Currently, only GraphQL endpoints are supported, with configurable paths and authentication methods.

```mermaid
graph LR
    subgraph "Endpoint Configuration"
        EndpointConfig["Endpoints Section"]
        DefaultEP["default:<br/>GraphqlEndpointInfo"]
        
        EndpointConfig --> DefaultEP
        
        DefaultEP --> Type["type: 'graphql'"]
        DefaultEP --> Path["path: '/graphql'"]
        DefaultEP --> Auth["auth: 'bearer-token' | 'none'"]
    end
    
    subgraph "Runtime Integration"
        GraphQLEngine["GraphQL Engine"]
        HTTPServer["HTTP Server :8686"]
        
        DefaultEP --> GraphQLEngine
        GraphQLEngine --> HTTPServer
    end
```

The `GraphqlEndpointInfo` struct defines the endpoint configuration:

```json
{
  "endpoints": {
    "default": {
      "type": "graphql",
      "path": "/graphql", 
      "auth": "bearer-token"
    }
  }
}
```

| Field | Type | Description | Valid Values |
|-------|------|-------------|--------------|
| `type` | string | Endpoint type | `"graphql"` |
| `path` | string | URL path for the endpoint | Must start with `/`, cannot be `/health` or `/metrics` |
| `auth` | string | Authentication method | `"none"`, `"bearer-token"` |

Sources: [lib/manifest/test/valid_modus.json:4-10](), [lib/manifest/endpoints.go:12-24](), [lib/manifest/modus_schema.json:25-55]()

## Models Configuration

The models section defines AI model integrations that can be invoked from WebAssembly functions. Models can either use the built-in Hypermode service or connect to external model providers via HTTP connections.

```mermaid
graph TD
    subgraph "Model Configuration Types"
        ModelConfig["Models Section"]
        
        ModelConfig --> HypermodeModel["Hypermode Models:<br/>Built-in Service"]
        ModelConfig --> ExternalModel["External Models:<br/>Custom HTTP Connections"]
        
        HypermodeModel --> Provider["provider: 'hugging-face'"]
        HypermodeModel --> HyperConn["connection: 'hypermode'"]
        
        ExternalModel --> CustomConn["connection: custom connection name"]
        ExternalModel --> ModelPath["path: optional model path"]
    end
    
    subgraph "Model Runtime Integration"
        ModelInfo["ModelInfo Struct"]
        ModelHash["model.Hash():<br/>Content-based Caching"]
        ModelVariables["Connection Variables"]
        
        ModelConfig --> ModelInfo
        ModelInfo --> ModelHash
        ModelInfo --> ModelVariables
    end
```

Two model configuration patterns are supported:

**Hypermode-hosted models:**
```json
{
  "models": {
    "model-1": {
      "sourceModel": "example/source-model-1",
      "provider": "hugging-face",
      "connection": "hypermode"
    }
  }
}
```

**External model connections:**
```json
{
  "models": {
    "model-2": {
      "sourceModel": "source-model-2",
      "connection": "my-model-connection",
      "path": "path/to/model-2"
    }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sourceModel` | string | Yes | Model identifier from the provider |
| `provider` | string | Hypermode only | Provider name (currently `"hugging-face"`) |
| `connection` | string | Yes | Connection name (`"hypermode"` or custom connection) |
| `path` | string | No | Optional path appended to connection base URL |

Sources: [lib/manifest/test/valid_modus.json:11-26](), [lib/manifest/models.go:12-21](), [lib/manifest/modus_schema.json:57-121]()

## Connections Configuration

Connections define how the Modus runtime connects to external services including databases, REST APIs, and model endpoints. Each connection type has specific configuration requirements and supports variable substitution for secrets.

### Connection Types Overview

```mermaid
graph TD
    subgraph "Connection Types"
        ConnConfig["Connections Section"]
        
        ConnConfig --> HTTPConn["HTTP Connections:<br/>HTTPConnectionInfo"]
        ConnConfig --> PostgresConn["PostgreSQL:<br/>PostgresqlConnectionInfo"]
        ConnConfig --> MySQLConn["MySQL:<br/>MysqlConnectionInfo"]
        ConnConfig --> DgraphConn["Dgraph:<br/>DgraphConnectionInfo"]
        ConnConfig --> Neo4jConn["Neo4j:<br/>Neo4jConnectionInfo"]
    end
    
    subgraph "Common Features"
        ConnInterface["ConnectionInfo Interface"]
        ConnName["ConnectionName()"]
        ConnType["ConnectionType()"]
        ConnHash["Hash()"]
        ConnVars["Variables()"]
        
        ConnConfig --> ConnInterface
        ConnInterface --> ConnName
        ConnInterface --> ConnType
        ConnInterface --> ConnHash
        ConnInterface --> ConnVars
    end
```

### HTTP Connections

HTTP connections support REST APIs and model endpoints with flexible URL configuration, headers, and query parameters.

```json
{
  "connections": {
    "my-rest-api": {
      "type": "http",
      "baseUrl": "https://api.example.com/v1/",
      "queryParameters": {
        "api_token": "{{API_TOKEN}}"
      }
    },
    "my-graphql-api": {
      "type": "http", 
      "endpoint": "https://api.example.com/graphql",
      "headers": {
        "Authorization": "Bearer {{AUTH_TOKEN}}"
      }
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `baseUrl` | string | Base URL ending with `/` (mutually exclusive with `endpoint`) |
| `endpoint` | string | Complete URL (mutually exclusive with `baseUrl`) |
| `headers` | object | HTTP headers with variable substitution |
| `queryParameters` | object | Query parameters with variable substitution |

### Database Connections

Database connections use connection strings with variable substitution for credentials:

**PostgreSQL:**
```json
{
  "neon": {
    "type": "postgresql",
    "connString": "postgresql://{{POSTGRESQL_USERNAME}}:{{POSTGRESQL_PASSWORD}}@1.2.3.4:5432/data?sslmode=disable"
  }
}
```

**MySQL:**
```json
{
  "my-mysql": {
    "type": "mysql", 
    "connString": "mysql://{{MYSQL_USERNAME}}:{{MYSQL_PASSWORD}}@1.2.3.4:3306/mydb?sslmode=disable"
  }
}
```

**Dgraph:**
```json
{
  "my-dgraph-cloud": {
    "type": "dgraph",
    "grpcTarget": "frozen-mango.grpc.eu-central-1.aws.cloud.dgraph.io:443", 
    "key": "{{DGRAPH_KEY}}"
  }
}
```

**Neo4j:**
```json
{
  "my-neo4j": {
    "type": "neo4j",
    "dbUri": "bolt://localhost:7687",
    "username": "{{NEO4J_USERNAME}}",
    "password": "{{NEO4J_PASSWORD}}"
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:27-94](), [lib/manifest/http.go:12-32](), [lib/manifest/postgresql.go:12-24](), [lib/manifest/mysql.go:12-24](), [lib/manifest/dgraph.go:14-36](), [lib/manifest/neo4j.go:12-28]()

## Variable Substitution and Secrets

The manifest system supports variable substitution using `{{VARIABLE_NAME}}` syntax for sensitive configuration values. The runtime extracts these variables and resolves them from environment variables or secret management systems.

### Variable Extraction Process

```mermaid
sequenceDiagram
    participant "Manifest Parser" as Parser
    participant "Variable Extractor" as Extractor
    participant "Connection Info" as ConnInfo
    participant "Runtime" as Runtime
    
    Parser->>ConnInfo: "Parse connection config"
    Parser->>Extractor: "manifest.GetVariables()"
    Extractor->>ConnInfo: "connection.Variables()"
    ConnInfo->>Extractor: "Extract {{VAR}} patterns"
    Extractor->>Runtime: "Return variable map"
    Runtime->>Runtime: "Resolve from environment"
```

The `GetVariables()` method returns a map of connection names to their required variables:

```go
// Example variable extraction result
map[string][]string{
    "my-model-connection":      {"API_KEY"},
    "another-model-connection": {"API_KEY"}, 
    "my-graphql-api":           {"AUTH_TOKEN"},
    "my-rest-api":              {"API_TOKEN"},
    "another-rest-api":         {"USERNAME", "PASSWORD"},
    "neon":                     {"POSTGRESQL_USERNAME", "POSTGRESQL_PASSWORD"},
    "pg-host":                  {"POSTGRESQL_USERNAME", "POSTGRESQL_PASSWORD", "POSTGRESQL_HOST"},
}
```

Special functions are supported for variable processing:
- `{{base64(USERNAME:PASSWORD)}}` - Base64 encoding for basic auth
- Multiple variables can be referenced in a single field

Sources: [lib/manifest/manifest.go:46-57](), [lib/manifest/test/manifest_test.go:262-286](), [lib/manifest/utils.go:12-30]()

## Schema Validation

The manifest system includes comprehensive JSON Schema validation to ensure configuration correctness before runtime initialization.

### Validation Workflow

```mermaid
graph LR
    subgraph "Validation Process"
        ManifestFile["modus.json"]
        JSONCParser["jsonc.ToJSON():<br/>Strip Comments"]
        SchemaLoader["Load modus_schema.json"]
        Validator["jsonschema.Validate()"]
        
        ManifestFile --> JSONCParser
        JSONCParser --> Validator
        SchemaLoader --> Validator
        Validator --> Result["Validation Result"]
    end
    
    subgraph "Schema Features"
        SchemaValidation["JSON Schema v7"]
        PatternValidation["Regex Patterns"]
        EnumValidation["Enum Constraints"] 
        FormatValidation["URI Format Validation"]
        
        SchemaValidation --> PatternValidation
        SchemaValidation --> EnumValidation
        SchemaValidation --> FormatValidation
    end
```

The validation process includes:

1. **Comment Stripping**: JSON comments are removed using `jsonc.ToJSON()`
2. **Schema Compilation**: The embedded schema is compiled once at startup
3. **Validation**: Full schema validation against the JSON Schema v7 specification
4. **Error Reporting**: Detailed validation errors with field paths

Key validation rules:
- Connection names must match `^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$`
- URLs must be valid URI format
- Endpoint paths cannot conflict with reserved paths (`/health`, `/metrics`)
- Either `baseUrl` or `endpoint` required for HTTP connections (but not both)
- Connection strings must match database-specific URI patterns

Sources: [lib/manifest/manifest.go:81-93](), [lib/manifest/modus_schema.json:1-318](), [lib/manifest/test/manifest_test.go:148-152]()

## Manifest Processing Workflow

The Modus runtime processes manifests through a multi-stage pipeline that validates, parses, and initializes services based on the configuration.

```mermaid
sequenceDiagram
    participant "CLI/Runtime" as CLI
    participant "manifest.ValidateManifest()" as Validator
    participant "manifest.ReadManifest()" as Parser
    participant "parseManifestJson()" as JSONParser
    participant "Manifest struct" as Manifest
    participant "Runtime Services" as Services
    
    CLI->>Validator: "Validate raw JSON"
    Validator->>Validator: "Strip comments, validate schema"
    Validator-->>CLI: "Validation result"
    
    CLI->>Parser: "Parse validated manifest"
    Parser->>JSONParser: "Parse by section type"
    JSONParser->>JSONParser: "Type-specific unmarshaling"
    JSONParser->>Manifest: "Populate struct fields"
    Parser-->>CLI: "Parsed Manifest"
    
    CLI->>Manifest: "GetVariables()"
    Manifest-->>CLI: "Variable requirements"
    
    CLI->>Services: "Initialize with manifest config"
    Services->>Services: "Setup connections, models, endpoints"
```

### Processing Stages

1. **Validation Stage** ([lib/manifest/manifest.go:81-93]()):
   - Comment removal using `jsonc.ToJSON()`
   - JSON Schema validation
   - Error reporting for invalid configurations

2. **Parsing Stage** ([lib/manifest/manifest.go:95-101]()):
   - Type-specific unmarshaling based on `type` field
   - Dynamic interface assignment for polymorphic connection types
   - Name field assignment from map keys

3. **Variable Extraction** ([lib/manifest/manifest.go:46-57]()):
   - Pattern matching for `{{VARIABLE}}` syntax
   - Connection-specific variable collection
   - Environment variable requirement mapping

4. **Runtime Integration**:
   - Service initialization based on connection configurations
   - GraphQL schema generation from endpoint definitions
   - Model client setup for AI integrations

The manifest system provides a robust foundation for Modus application configuration, ensuring type safety, validation, and secure secret management throughout the application lifecycle.

Sources: [lib/manifest/manifest.go:103-195](), [lib/manifest/test/manifest_test.go:23-146]()

---

# Page: Connections and Secrets

# Connections and Secrets

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lib/manifest/dgraph.go](lib/manifest/dgraph.go)
- [lib/manifest/go.sum](lib/manifest/go.sum)
- [lib/manifest/manifest.go](lib/manifest/manifest.go)
- [lib/manifest/modus_schema.json](lib/manifest/modus_schema.json)
- [lib/manifest/test/manifest_test.go](lib/manifest/test/manifest_test.go)
- [lib/manifest/test/valid_modus.json](lib/manifest/test/valid_modus.json)
- [runtime/dgraphclient/dgraph.go](runtime/dgraphclient/dgraph.go)
- [runtime/dgraphclient/registry.go](runtime/dgraphclient/registry.go)
- [runtime/neo4jclient/registry.go](runtime/neo4jclient/registry.go)
- [runtime/sqlclient/registry.go](runtime/sqlclient/registry.go)
- [runtime/sqlclient/sqlclient.go](runtime/sqlclient/sqlclient.go)
- [runtime/timezones/timezones.go](runtime/timezones/timezones.go)

</details>



This page covers the configuration and management of external service connections and secret handling in Modus applications. The system enables secure connections to databases, HTTP APIs, and AI model providers through declarative configuration with built-in secret management.

For information about application manifest structure, see [Application Manifests](#6.1). For database integration details, see [Database Integration](#5.4).

## Connection Configuration

Connections to external services are defined in the `connections` section of the application manifest (`modus.json`). Each connection specifies the service type, connection parameters, and authentication credentials using a templated secret system.

### Connection Definition Flow

```mermaid
flowchart TB
    subgraph "Configuration"
        Manifest["modus.json<br/>connections section"]
        Schema["modus_schema.json<br/>validation rules"]
        EnvVars["Environment Variables<br/>{{SECRET_NAME}}"]
    end
    
    subgraph "Runtime Processing"
        Parser["manifest.parseManifestJson()"]
        Validator["manifest.ValidateManifest()"]
        SecretProcessor["secrets.ApplySecretsToString()"]
    end
    
    subgraph "Connection Registries"
        DgraphReg["dgraphRegistry.cache"]
        SqlReg["dsRegistry.cache"] 
        Neo4jReg["neo4jRegistry.cache"]
    end
    
    Manifest --> Parser
    Schema --> Validator
    Parser --> SecretProcessor
    EnvVars --> SecretProcessor
    SecretProcessor --> DgraphReg
    SecretProcessor --> SqlReg
    SecretProcessor --> Neo4jReg
```

Sources: [lib/manifest/manifest.go:95-195](), [lib/manifest/modus_schema.json:122-314](), [runtime/dgraphclient/registry.go:48-97]()

## Supported Connection Types

The system supports multiple connection types, each with specific configuration parameters and authentication methods.

### HTTP Connections

HTTP connections support both base URL and full endpoint configurations with custom headers and query parameters.

```json
{
  "connections": {
    "my-api": {
      "type": "http",
      "baseUrl": "https://api.example.com/v1/",
      "headers": {
        "Authorization": "Bearer {{API_TOKEN}}"
      },
      "queryParameters": {
        "api_key": "{{API_KEY}}"
      }
    }
  }
}
```

### Database Connections

#### PostgreSQL
Uses standard PostgreSQL connection strings with SSL mode configuration:

```json
{
  "connections": {
    "postgres-db": {
      "type": "postgresql", 
      "connString": "postgresql://{{DB_USER}}:{{DB_PASS}}@{{DB_HOST}}:5432/mydb?sslmode=require"
    }
  }
}
```

#### MySQL
Supports MySQL connection string format:

```json
{
  "connections": {
    "mysql-db": {
      "type": "mysql",
      "connString": "mysql://{{MYSQL_USER}}:{{MYSQL_PASS}}@localhost:3306/mydb"
    }
  }
}
```

#### Dgraph
Supports both connection strings and gRPC target configurations:

```json
{
  "connections": {
    "dgraph-cloud": {
      "type": "dgraph",
      "grpcTarget": "my-server.grpc.us-east-1.aws.cloud.dgraph.io:443",
      "key": "{{DGRAPH_API_KEY}}"
    }
  }
}
```

#### Neo4j
Uses Neo4j bolt protocol with separate username/password fields:

```json
{
  "connections": {
    "neo4j-db": {
      "type": "neo4j",
      "dbUri": "bolt://localhost:7687",
      "username": "{{NEO4J_USER}}",
      "password": "{{NEO4J_PASS}}"
    }
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:27-94](), [lib/manifest/modus_schema.json:131-313]()

## Secret Variable Substitution

The secret system uses double-brace template syntax (`{{VARIABLE_NAME}}`) to reference environment variables in connection configurations. Variables are resolved at runtime when connections are established.

### Variable Extraction and Processing

```mermaid
flowchart LR
    subgraph "Manifest Processing"
        ConnDef["Connection Definition<br/>{{API_KEY}}, {{DB_PASS}}"]
        VarExtract["extractVariables()<br/>Parse template syntax"]
        VarMap["Variable Map<br/>connection -> [variables]"]
    end
    
    subgraph "Runtime Resolution"
        EnvLookup["Environment Variable<br/>Lookup"]
        SecretApply["secrets.ApplySecretsToString()<br/>Template substitution"]
        ConnStr["Final Connection String<br/>Resolved credentials"]
    end
    
    ConnDef --> VarExtract
    VarExtract --> VarMap
    VarMap --> EnvLookup
    EnvLookup --> SecretApply
    SecretApply --> ConnStr
```

The `GetVariables()` method extracts all template variables from connection definitions:

| Connection Type | Variable Sources |
|----------------|------------------|
| HTTP | `headers`, `queryParameters` |
| PostgreSQL | `connString` |
| MySQL | `connString` |
| Dgraph | `connString`, `key` |
| Neo4j | `username`, `password` |

Sources: [lib/manifest/manifest.go:46-57](), [lib/manifest/dgraph.go:34-36](), [runtime/dgraphclient/registry.go:79-96]()

## Connection Registry Architecture

Each connection type maintains a registry with connection pooling and caching to optimize performance and resource usage.

### Registry Implementation Pattern

```mermaid
classDiagram
    class ConnectionRegistry {
        -cache xsync.Map
        +getConnection(ctx, name) Connection
        +shutdown()
    }
    
    class dgraphRegistry {
        -cache Map[string, dgraphConnector]
        +getDgraphConnector(ctx, name) dgraphConnector
    }
    
    class dsRegistry {
        -cache Map[string, dataSource] 
        +getDataSource(ctx, name, type) dataSource
    }
    
    class neo4jRegistry {
        -cache Map[string, DriverWithContext]
        +getDriver(ctx, name) DriverWithContext
    }
    
    ConnectionRegistry <|-- dgraphRegistry
    ConnectionRegistry <|-- dsRegistry  
    ConnectionRegistry <|-- neo4jRegistry
    
    dgraphRegistry --> "creates" dgraphConnector
    dsRegistry --> "creates" postgresqlDS
    dsRegistry --> "creates" mysqlDS
    neo4jRegistry --> "creates" Neo4jDriver
```

### Connection Lifecycle Management

```mermaid
sequenceDiagram
    participant App as "Application"
    participant Registry as "Connection Registry"
    participant Manifest as "manifestdata.GetManifest()"
    participant Secrets as "secrets.ApplySecretsToString()"
    participant DB as "Database/Service"
    
    App->>Registry: getConnection(ctx, "my-db")
    Registry->>Registry: LoadOrCompute from cache
    
    alt "Cache Miss"
        Registry->>Manifest: Get connection info
        Manifest->>Registry: ConnectionInfo
        Registry->>Secrets: Apply variable substitution
        Secrets->>Registry: Resolved connection string
        Registry->>DB: Establish connection
        DB->>Registry: Connection handle
        Registry->>Registry: Store in cache
    end
    
    Registry->>App: Connection handle
    
    Note over Registry: Connection reused for<br/>subsequent requests
```

Sources: [runtime/dgraphclient/registry.go:27-59](), [runtime/sqlclient/registry.go:19-64](), [runtime/neo4jclient/registry.go:24-56]()

## Connection Validation and Error Handling

The system performs comprehensive validation at both manifest parse time and runtime connection establishment.

### Manifest Validation Rules

| Connection Type | Required Fields | Validation Rules |
|----------------|----------------|------------------|
| HTTP | `type`, (`baseUrl` OR `endpoint`) | URL format, mutual exclusion |
| PostgreSQL | `type`, `connString` | PostgreSQL URI pattern |
| MySQL | `type`, `connString` | MySQL URI pattern |
| Dgraph | `type`, (`connString` OR `grpcTarget`) | URI pattern or gRPC target format |
| Neo4j | `type`, `dbUri`, `username`, `password` | Neo4j URI pattern |

### Runtime Connection Establishment

```mermaid
flowchart TD
    subgraph "Connection Creation Process"
        Start["Connection Request"]
        CacheCheck{"Check Registry<br/>Cache"}
        ManifestLookup["Get Connection Info<br/>from Manifest"]
        TypeValidation["Validate Connection<br/>Type Match"]
        SecretResolution["Apply Secret<br/>Substitution"]
        ConnEstablish["Establish Physical<br/>Connection"]
        CacheStore["Store in Registry<br/>Cache"]
        ReturnConn["Return Connection<br/>Handle"]
        
        ErrorHandler["Error Response<br/>Connection Failed"]
    end
    
    Start --> CacheCheck
    CacheCheck -->|"Hit"| ReturnConn
    CacheCheck -->|"Miss"| ManifestLookup
    ManifestLookup --> TypeValidation
    TypeValidation --> SecretResolution
    SecretResolution --> ConnEstablish
    ConnEstablish --> CacheStore
    CacheStore --> ReturnConn
    
    ManifestLookup -->|"Not Found"| ErrorHandler
    TypeValidation -->|"Type Mismatch"| ErrorHandler
    SecretResolution -->|"Missing Variable"| ErrorHandler
    ConnEstablish -->|"Connection Failed"| ErrorHandler
```

Sources: [runtime/dgraphclient/registry.go:61-97](), [runtime/neo4jclient/registry.go:58-120](), [lib/manifest/modus_schema.json:185-311]()

## Connection Shutdown and Resource Management

All connection registries implement proper shutdown procedures to clean up resources and close active connections.

### Registry Shutdown Process

Each registry provides a shutdown mechanism that iterates through cached connections and properly closes them:

- **Dgraph**: `ShutdownConns()` closes all `dgraphConnector` instances via `dgClient.Close()`
- **SQL**: `shutdown()` calls `dataSource.Shutdown()` on each cached connection
- **Neo4j**: `CloseDrivers()` calls `driver.Close(ctx)` on each cached driver

The shutdown process ensures no connection leaks occur when the runtime terminates.

Sources: [runtime/dgraphclient/registry.go:39-46](), [runtime/sqlclient/registry.go:31-38](), [runtime/neo4jclient/registry.go:36-43]()

---

# Page: Development Tools

# Development Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.trunk/configs/cspell.json](.trunk/configs/cspell.json)
- [.trunk/trunk.yaml](.trunk/trunk.yaml)
- [.vscode/launch.json](.vscode/launch.json)
- [go.work](go.work)
- [runtime/.gitignore](runtime/.gitignore)
- [runtime/db/db.go](runtime/db/db.go)
- [runtime/db/modusdb.go](runtime/db/modusdb.go)
- [runtime/explorer/content/ModusIcon.tsx](runtime/explorer/content/ModusIcon.tsx)
- [runtime/explorer/content/index.css](runtime/explorer/content/index.css)
- [runtime/explorer/content/index.html](runtime/explorer/content/index.html)
- [runtime/explorer/content/main.tsx](runtime/explorer/content/main.tsx)
- [runtime/explorer/content/package-lock.json](runtime/explorer/content/package-lock.json)
- [runtime/explorer/content/package.json](runtime/explorer/content/package.json)
- [runtime/explorer/content/postcss.config.js](runtime/explorer/content/postcss.config.js)
- [runtime/explorer/content/tailwind.config.js](runtime/explorer/content/tailwind.config.js)
- [runtime/explorer/content/vite.config.ts](runtime/explorer/content/vite.config.ts)
- [runtime/explorer/explorer.go](runtime/explorer/explorer.go)
- [runtime/services/services.go](runtime/services/services.go)
- [sdk/assemblyscript/examples/agents/.gitignore](sdk/assemblyscript/examples/agents/.gitignore)
- [sdk/assemblyscript/src/assembly/index.ts](sdk/assemblyscript/src/assembly/index.ts)
- [sdk/go/examples/agents/.gitignore](sdk/go/examples/agents/.gitignore)

</details>



This document covers the development tools and interfaces available for building, testing, and debugging Modus applications. It includes the web-based API Explorer, VS Code debugging configurations, and local development server capabilities.

For information about the CLI commands used during development, see [Modus CLI](#3). For details about setting up the development environment and workflows, see [Development Environment](#7.1).

## API Explorer

The API Explorer is a web-based interface that provides GraphQL introspection, query execution, and inference history tracking for Modus applications. It runs embedded within the Modus Runtime and is accessible at `http://localhost:8686/explorer` during local development.

### Architecture

```mermaid
graph TB
    subgraph "Browser"
        UI["API Explorer UI<br/>React Application"]
        CodeMirror["CodeMirror Editor<br/>GraphQL Query Editor"]
    end
    
    subgraph "Modus Runtime"
        ExplorerHandler["explorer.ExplorerHandler<br/>HTTP Handler"]
        EndpointsAPI["endpointsHandler<br/>/explorer/api/endpoints"]
        InferenceAPI["inferenceHistoryHandler<br/>/explorer/api/inferences"]
    end
    
    subgraph "Data Sources"
        ManifestData["manifestdata.GetManifest()<br/>Endpoint Configuration"]
        Database["db.QueryInferences()<br/>Inference History"]
        GraphQLEngine["GraphQL Engine<br/>Schema & Execution"]
    end
    
    UI --> ExplorerHandler
    UI --> EndpointsAPI
    UI --> InferenceAPI
    
    EndpointsAPI --> ManifestData
    InferenceAPI --> Database
    UI --> GraphQLEngine
    
    CodeMirror --> GraphQLEngine
```

The API Explorer consists of a React frontend that communicates with REST APIs exposed by the runtime to fetch endpoint configurations and inference history.

Sources: [runtime/explorer/explorer.go:1-84](), [runtime/explorer/content/main.tsx:1-113](), [runtime/explorer/content/package.json:1-29]()

### Frontend Implementation

The API Explorer frontend is built using React 19 with TypeScript and uses the `@hypermode/react-api-explorer` component library. The main application component manages endpoint discovery and inference history fetching.

```mermaid
graph LR
    subgraph "React Components"
        App["App Component<br/>Main Application"]
        ApiExplorer["@hypermode/react-api-explorer<br/>Core Explorer Component"]
        ModusIcon["ModusIcon<br/>Branding Component"]
    end
    
    subgraph "State Management"
        Endpoints["endpoints: string[]<br/>GraphQL Endpoint URLs"]
        Inferences["inferences: any[]<br/>Historical Queries"]
        Theme["modusTheme<br/>Custom Color Scheme"]
    end
    
    subgraph "External APIs"
        EndpointsEndpoint["/explorer/api/endpoints<br/>Endpoint Discovery"]
        InferencesEndpoint["/explorer/api/inferences<br/>Query History"]
    end
    
    App --> ApiExplorer
    App --> ModusIcon
    App --> Endpoints
    App --> Inferences
    App --> Theme
    
    App --> EndpointsEndpoint
    App --> InferencesEndpoint
```

The application automatically discovers available GraphQL endpoints and displays inference history for debugging and testing purposes.

Sources: [runtime/explorer/content/main.tsx:19-112](), [runtime/explorer/content/package.json:11-17]()

### Backend API Handlers

The runtime exposes two REST endpoints to support the API Explorer interface:

| Endpoint | Handler Function | Purpose |
|----------|------------------|---------|
| `/explorer/api/endpoints` | `endpointsHandler` | Returns available GraphQL endpoints from manifest |
| `/explorer/api/inferences` | `inferenceHistoryHandler` | Returns historical AI model inference data |

```mermaid
graph TD
    subgraph "HTTP Routes"
        ExplorerMux["http.NewServeMux()<br/>Explorer Route Handler"]
        StaticFiles["http.FileServerFS<br/>Serve React Build"]
        EndpointsRoute["endpointsHandler<br/>GET /explorer/api/endpoints"]
        InferencesRoute["inferenceHistoryHandler<br/>GET /explorer/api/inferences"]
    end
    
    subgraph "Data Processing"
        ManifestReader["manifestdata.GetManifest()<br/>Read Application Config"]
        EndpointFilter["manifest.EndpointTypeGraphQL<br/>Filter GraphQL Endpoints"]
        InferenceQuery["db.QueryInferences(ctx)<br/>Database Query"]
        JSONSerialization["utils.JsonSerialize()<br/>Response Formatting"]
    end
    
    ExplorerMux --> StaticFiles
    ExplorerMux --> EndpointsRoute
    ExplorerMux --> InferencesRoute
    
    EndpointsRoute --> ManifestReader
    ManifestReader --> EndpointFilter
    EndpointFilter --> JSONSerialization
    
    InferencesRoute --> InferenceQuery
    InferenceQuery --> JSONSerialization
```

The endpoints handler filters the application manifest to return only GraphQL endpoints, while the inferences handler queries the database for historical AI model execution data.

Sources: [runtime/explorer/explorer.go:39-83](), [runtime/explorer/explorer.go:23-37]()

## VS Code Integration

Modus provides comprehensive VS Code debugging configurations for runtime debugging, application building, and CLI development. The configurations support multiple development scenarios including cluster mode testing and AWS storage integration.

### Debug Configurations

```mermaid
graph TB
    subgraph "Runtime Debugging"
        PickExample["Debug Modus Runtime (pick example)<br/>Example App Selection"]
        ClusterMode["Debug Modus Runtime (cluster mode)<br/>NATS Clustering"]
        InputPath["Debug Modus Runtime (input path)<br/>Custom App Path"]
        AWSStorage["Debug Modus Runtime (aws storage)<br/>S3 Integration"]
    end
    
    subgraph "Build Debugging"
        ASBuild["Debug Build Example AssemblyScript App<br/>npm build process"]
        GoBuild["Debug Build Example Go App<br/>modus-go-build tool"]
        ASTest["Debug Build Runtime AssemblyScript Test App<br/>Test Data Building"]
        GoTest["Debug Build Runtime Go Test App<br/>Test Data Building"]
    end
    
    subgraph "CLI Debugging"
        CLIDebug["Debug Modus CLI<br/>Node.js CLI Process"]
    end
    
    subgraph "Environment Variables"
        ForceColor["FORCE_COLOR=1<br/>Terminal Color Support"]
        ModusEnv["MODUS_ENV=dev<br/>Development Mode"]
        ModusDebug["MODUS_DEBUG=true<br/>Debug Logging"]
    end
    
    PickExample --> ForceColor
    PickExample --> ModusEnv
    PickExample --> ModusDebug
    
    ClusterMode --> ForceColor
    ClusterMode --> ModusEnv
    ClusterMode --> ModusDebug
```

Each configuration includes specific environment variables and command-line arguments tailored for different debugging scenarios.

Sources: [.vscode/launch.json:1-260]()

### Input Prompts and Selection

The VS Code configuration uses input prompts to provide interactive selection of debugging targets:

| Input ID | Type | Options | Purpose |
|----------|------|---------|---------|
| `appLanguage` | `pickString` | AssemblyScript, Go | Select SDK language |
| `exampleApp` | `pickString` | 16+ example apps | Choose specific example |
| `appPath` | `promptString` | User input | Custom build directory path |
| `httpServerPort` | `promptString` | Default: 8686 | Runtime server port |

```mermaid
graph LR
    subgraph "Interactive Inputs"
        AppLanguage["appLanguage<br/>SDK Selection"]
        ExampleApp["exampleApp<br/>Example Selection"]
        AppPath["appPath<br/>Custom Path Input"]
        ServerPort["httpServerPort<br/>Port Configuration"]
    end
    
    subgraph "Example Applications"
        Agents["agents<br/>Agent System Example"]
        Simple["simple<br/>Basic Function Example"]
        PostgreSQL["postgresql<br/>Database Example"]
        TextGen["textgeneration<br/>AI Model Example"]
        Classification["classification<br/>ML Model Example"]
    end
    
    AppLanguage --> ExampleApp
    ExampleApp --> Agents
    ExampleApp --> Simple
    ExampleApp --> PostgreSQL
    ExampleApp --> TextGen
    ExampleApp --> Classification
```

The configuration supports debugging over 16 different example applications across multiple categories including database clients, AI models, and agent systems.

Sources: [.vscode/launch.json:136-259]()

### Runtime Debug Modes

The runtime debugging configurations support different operational modes:

```mermaid
graph TD
    subgraph "Standard Development"
        StandardRuntime["program: ${workspaceFolder}/runtime<br/>Direct Runtime Execution"]
        StandardEnv["MODUS_ENV=dev<br/>MODUS_DEBUG=true"]
        StandardArgs["--refresh=1s<br/>--appPath build/"]
    end
    
    subgraph "Cluster Mode"
        ClusterRuntime["program: ${workspaceFolder}/runtime<br/>Runtime with Clustering"]
        ClusterEnv["MODUS_CLUSTER_MODE=NATS<br/>MODUS_CLUSTER_NATS_URL=nats://localhost:4222"]
        ClusterDB["MODUS_USE_MODUSDB=false<br/>PostgreSQL Connection"]
    end
    
    subgraph "AWS Integration"
        AWSRuntime["program: ${workspaceFolder}/runtime<br/>Runtime with S3 Storage"]
        AWSEnv["AWS_REGION, AWS_PROFILE<br/>AWS_SDK_LOAD_CONFIG=true"]
        AWSArgs["--useAwsStorage<br/>--s3bucket, --s3path"]
    end
    
    StandardRuntime --> StandardEnv
    StandardEnv --> StandardArgs
    
    ClusterRuntime --> ClusterEnv
    ClusterEnv --> ClusterDB
    
    AWSRuntime --> AWSEnv
    AWSEnv --> AWSArgs
```

Each mode configures the runtime for specific testing scenarios, from basic local development to distributed cluster operations.

Sources: [.vscode/launch.json:4-78]()

## Build Tool Integration

The debugging configurations integrate with the SDK build tools to provide seamless development workflows for both Go and AssemblyScript applications.

### SDK Build Tools

```mermaid
graph TB
    subgraph "Go Build Pipeline"
        GoCompiler["modus-go-build<br/>${workspaceFolder}/sdk/go/tools/modus-go-build"]
        GoTarget["${workspaceFolder}/sdk/go/examples/${input:exampleApp}<br/>Source Directory"]
        GoOutput["build/<br/>WebAssembly Module"]
    end
    
    subgraph "AssemblyScript Build Pipeline"
        NPMInstall["npm install --prefix sdk/assemblyscript/src<br/>SDK Dependencies"]
        ASBuild["npm run build<br/>AssemblyScript Compilation"]
        ASTarget["sdk/assemblyscript/examples/${input:exampleApp}<br/>Source Directory"]
        ASOutput["build/<br/>WebAssembly Module"]
    end
    
    subgraph "Environment"
        BuildEnv["FORCE_COLOR=1<br/>MODUS_DEBUG=true"]
    end
    
    GoCompiler --> GoTarget
    GoTarget --> GoOutput
    GoCompiler --> BuildEnv
    
    NPMInstall --> ASBuild
    ASBuild --> ASTarget
    ASTarget --> ASOutput
    ASBuild --> BuildEnv
```

The build configurations support both SDK compilation pipelines and can build test applications for runtime validation.

Sources: [.vscode/launch.json:90-124]()

### Test Data Building

Special configurations exist for building test applications used by the runtime's internal testing:

| Configuration | Tool | Target Directory | Purpose |
|---------------|------|------------------|---------|
| Debug Build Runtime AssemblyScript Test App | npm build | `runtime/languages/assemblyscript/testdata` | Runtime test validation |
| Debug Build Runtime Go Test App | modus-go-build | `runtime/languages/golang/testdata` | Runtime test validation |

```mermaid
graph LR
    subgraph "Test App Building"
        ASTestBuild["AssemblyScript Test Build<br/>runtime/languages/assemblyscript/testdata"]
        GoTestBuild["Go Test Build<br/>runtime/languages/golang/testdata"]
    end
    
    subgraph "Build Tools"
        NPMProcess["npm install && npm run build<br/>Node Terminal Process"]
        GoProcess["modus-go-build<br/>Go Program Execution"]
    end
    
    subgraph "Output"
        TestWASM["test.wasm<br/>Test WebAssembly Modules"]
        TestManifest["modus.json<br/>Test Manifest Files"]
    end
    
    ASTestBuild --> NPMProcess
    GoTestBuild --> GoProcess
    
    NPMProcess --> TestWASM
    GoProcess --> TestWASM
    NPMProcess --> TestManifest
    GoProcess --> TestManifest
```

These configurations enable debugging of the runtime's language support by building test applications with known behavior.

Sources: [.vscode/launch.json:103-124]()

---

# Page: Development Environment

# Development Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.trunk/configs/cspell.json](.trunk/configs/cspell.json)
- [.vscode/launch.json](.vscode/launch.json)
- [runtime/db/db.go](runtime/db/db.go)
- [runtime/db/modusdb.go](runtime/db/modusdb.go)
- [runtime/explorer/explorer.go](runtime/explorer/explorer.go)
- [runtime/services/services.go](runtime/services/services.go)
- [sdk/assemblyscript/examples/agents/.gitignore](sdk/assemblyscript/examples/agents/.gitignore)
- [sdk/go/examples/agents/.gitignore](sdk/go/examples/agents/.gitignore)

</details>



This document covers setting up and using the local development environment for Modus applications. It includes VS Code debugging configurations, local development workflows, and troubleshooting common development issues. For information about the API Explorer web interface, see [API Explorer](#7.2). For CLI command reference, see [CLI Commands Reference](#3.1).

## VS Code Debugging Configuration

Modus provides comprehensive VS Code debugging support through pre-configured launch configurations in [.vscode/launch.json:1-259](). These configurations enable debugging of the runtime, SDK build tools, and CLI components.

### Runtime Debug Configurations

The following table shows the available runtime debugging configurations:

| Configuration Name | Purpose | Key Arguments |
|-------------------|---------|---------------|
| `Debug Modus Runtime (pick example)` | Debug runtime with example apps | `--refresh=1s`, `--appPath` with input selection |
| `Debug Modus Runtime (cluster mode)` | Debug runtime in NATS cluster mode | `--port`, cluster environment variables |
| `Debug Modus Runtime (input path)` | Debug runtime with custom app path | `--refresh=1s`, `--appPath` with manual input |
| `Debug Modus Runtime (aws storage)` | Debug runtime with AWS S3 storage | `--useAwsStorage`, S3 configuration |

```mermaid
graph TB
    subgraph "VS Code Debug Configurations"
        RuntimeDebug["Debug Modus Runtime (pick example)"]
        ClusterDebug["Debug Modus Runtime (cluster mode)"]
        PathDebug["Debug Modus Runtime (input path)"]
        AwsDebug["Debug Modus Runtime (aws storage)"]
        GoDebug["Debug Build Example Go App"]
        AsDebug["Debug Build Example AssemblyScript App"]
        CliDebug["Debug Modus CLI"]
    end
    
    subgraph "Runtime Process"
        RuntimeMain["${workspaceFolder}/runtime"]
        WasmHost["wasmhost.InitWasmHost"]
        GraphQLEngine["graphql.Initialize"]
        ActorSystem["actors.Initialize"]
    end
    
    subgraph "SDK Build Tools"
        GoBuilder["modus-go-build"]
        AsBuilder["npm run build"]
        TinyGoCompiler["TinyGo Compiler"]
        AsCompiler["AssemblyScript Compiler"]
    end
    
    subgraph "Development Services"
        PostgresDB["PostgreSQL Database"]
        ModusDB["ModusDB (.modusdb/)"]
        NatsCluster["NATS Cluster"]
        AwsS3["AWS S3 Storage"]
    end
    
    RuntimeDebug --> RuntimeMain
    ClusterDebug --> RuntimeMain
    PathDebug --> RuntimeMain
    AwsDebug --> RuntimeMain
    
    RuntimeMain --> WasmHost
    RuntimeMain --> GraphQLEngine
    RuntimeMain --> ActorSystem
    
    GoDebug --> GoBuilder
    AsDebug --> AsBuilder
    GoBuilder --> TinyGoCompiler
    AsBuilder --> AsCompiler
    
    ClusterDebug --> NatsCluster
    ClusterDebug --> PostgresDB
    PathDebug --> ModusDB
    AwsDebug --> AwsS3
```

**Sources:** [.vscode/launch.json:5-78]()

### Environment Variables for Debugging

The debug configurations set specific environment variables to enable development features:

| Variable | Purpose | Configurations Using It |
|----------|---------|-------------------------|
| `MODUS_ENV=dev` | Enable development mode | All runtime configurations |
| `MODUS_DEBUG=true` | Enable debug logging | All configurations |
| `MODUS_CLUSTER_MODE=NATS` | Enable NATS clustering | Cluster mode configuration |
| `MODUS_USE_MODUSDB=false` | Disable ModusDB in cluster mode | Cluster mode configuration |
| `FORCE_COLOR=1` | Enable colored output in VS Code | All configurations |

**Sources:** [.vscode/launch.json:10-14](), [.vscode/launch.json:28-35]()

### Interactive Input System

VS Code debugging uses an interactive input system for selecting examples and configuration options:

```mermaid
graph LR
    subgraph "Input Selections"
        AppLanguage["appLanguage: go|assemblyscript"]
        ExampleApp["exampleApp: agents|simple|postgresql|etc"]
        AppPath["appPath: Custom build directory path"]
        AwsProfile["awsProfile: AWS credential profile"]
        HttpPort["httpServerPort: Development server port"]
    end
    
    subgraph "Example Applications"
        AgentsExample["agents"]
        SimpleExample["simple"]
        PostgresExample["postgresql"]
        HttpExample["http"]
        GraphqlExample["graphql"]
        AuthExample["auth"]
        ClassificationExample["classification"]
        EmbeddingExample["embedding"]
    end
    
    subgraph "Build Paths"
        GoBuildPath["sdk/go/examples/{example}/build"]
        AsBuildPath["sdk/assemblyscript/examples/{example}/build"]
        CustomPath["User-specified path"]
    end
    
    AppLanguage --> GoBuildPath
    AppLanguage --> AsBuildPath
    ExampleApp --> AgentsExample
    ExampleApp --> SimpleExample
    ExampleApp --> PostgresExample
    AppPath --> CustomPath
```

**Sources:** [.vscode/launch.json:136-257]()

## Local Development Workflow

### Development Service Initialization

The runtime initializes development services in a specific order through the `services.Start` function:

```mermaid
graph TD
    subgraph "Service Initialization Order"
        WasmHostInit["wasmhost.InitWasmHost"]
        SqlClientInit["sqlclient.Initialize"]
        DgraphInit["dgraphclient.Initialize"]
        Neo4jInit["neo4jclient.Initialize"]
        SecretsInit["secrets.Initialize"]
        StorageInit["storage.Initialize"]
        DbInit["db.Initialize"]
        ModusDbInit["db.InitModusDb"]
        ActorsInit["actors.Initialize"]
        GraphqlInit["graphql.Initialize"]
        EnvFilesInit["envfiles.MonitorEnvFiles"]
        ManifestInit["manifestdata.MonitorManifestFile"]
        PluginInit["pluginmanager.Initialize"]
    end
    
    subgraph "Development Database Options"
        PostgresDB["PostgreSQL Database"]
        ModusDB["ModusDB (.modusdb/)"]
        UseModusDBCheck["useModusDB() check"]
    end
    
    WasmHostInit --> SqlClientInit
    SqlClientInit --> DgraphInit
    DgraphInit --> Neo4jInit
    Neo4jInit --> SecretsInit
    SecretsInit --> StorageInit
    StorageInit --> DbInit
    DbInit --> ModusDbInit
    ModusDbInit --> ActorsInit
    ActorsInit --> GraphqlInit
    GraphqlInit --> EnvFilesInit
    EnvFilesInit --> ManifestInit
    ManifestInit --> PluginInit
    
    DbInit --> UseModusDBCheck
    UseModusDBCheck --> PostgresDB
    UseModusDBCheck --> ModusDB
```

**Sources:** [runtime/services/services.go:34-62]()

### ModusDB Development Database

For local development, Modus automatically configures ModusDB when `useModusDB()` returns true:

| Condition | Database Used | Configuration |
|-----------|---------------|---------------|
| `MODUS_USE_MODUSDB=true` | ModusDB | Uses environment variable |
| `MODUS_USE_MODUSDB=false` | PostgreSQL | Uses environment variable |
| Environment variable not set | ModusDB if `app.IsDevEnvironment()` | Default behavior |

The ModusDB data directory is automatically configured and added to `.gitignore`:

```mermaid
graph TB
    subgraph "ModusDB Directory Structure"
        AppPath["`app.Config().AppPath()`"]
        BuildCheck["Check if path ends with 'build'"]
        ParentDir["Parent directory (.modusdb/)"]
        AppDir["App directory (.modusdb/)"]
        GitIgnore[".gitignore update"]
    end
    
    AppPath --> BuildCheck
    BuildCheck -->|"ends with 'build'"| ParentDir
    BuildCheck -->|"other path"| AppDir
    ParentDir --> GitIgnore
    AppDir --> GitIgnore
```

**Sources:** [runtime/db/db.go:111-124](), [runtime/db/modusdb.go:27-46](), [runtime/db/modusdb.go:55-90]()

## Development Dependencies

### Required Development Tools

The development environment relies on several external tools and dependencies:

| Tool | Purpose | Configuration File |
|------|---------|-------------------|
| TinyGo | Go to WebAssembly compilation | SDK build tools |
| Node.js/npm | AssemblyScript compilation | package.json files |
| PostgreSQL | Development database (optional) | Connection strings |
| NATS | Cluster mode development | Environment variables |
| AWS CLI | S3 storage development | AWS credentials |

### Spell Checking Configuration

Development includes spell checking configuration for code and documentation:

**Sources:** [.trunk/configs/cspell.json:1-234]()

### Git Ignore Patterns

Standard development artifacts are ignored in Git:

| Pattern | Purpose | Files |
|---------|---------|-------|
| `.modusdb/` | ModusDB data directory | [sdk/assemblyscript/examples/agents/.gitignore:17](), [sdk/go/examples/agents/.gitignore:1]() |
| `.postgres/` | PostgreSQL data directory | [sdk/assemblyscript/examples/agents/.gitignore:18](), [sdk/go/examples/agents/.gitignore:2]() |
| `build/` | Compiled WebAssembly output | [sdk/assemblyscript/examples/agents/.gitignore:9]() |
| `.env*` | Environment variable files | [sdk/assemblyscript/examples/agents/.gitignore:5-6]() |

## API Explorer Integration

The development environment includes the API Explorer for testing and introspection:

```mermaid
graph LR
    subgraph "Development Runtime"
        HttpServer["HTTP Server :8686"]
        ExplorerHandler["explorer.ExplorerHandler"]
        EndpointsAPI["endpointsHandler"]
        InferenceAPI["inferenceHistoryHandler"]
    end
    
    subgraph "API Explorer UI"
        ExplorerUI["Explorer Web Interface"]
        EndpointsView["Endpoints View"]
        InferenceHistory["Inference History"]
    end
    
    subgraph "Data Sources"
        ManifestData["manifestdata.GetManifest()"]
        DbInferences["db.QueryInferences()"]
    end
    
    HttpServer --> ExplorerHandler
    ExplorerHandler --> EndpointsAPI
    ExplorerHandler --> InferenceAPI
    
    ExplorerUI --> EndpointsView
    ExplorerUI --> InferenceHistory
    
    EndpointsAPI --> ManifestData
    InferenceAPI --> DbInferences
```

**Sources:** [runtime/explorer/explorer.go:27-83]()

## Troubleshooting Development Issues

### Database Connection Issues

The runtime handles database connection problems gracefully in development:

| Error Type | Log Level | Message |
|------------|-----------|---------|
| `pgconn.ConnectError` | Warning | "Database connection error" |
| `errDbNotConfigured` | Warning (if not using ModusDB) | "Database has not been configured" |
| Other database errors | Error | Generic error message |

**Sources:** [runtime/db/db.go:52-62]()

### Service Shutdown Order

During development, services shut down in reverse order to prevent dependency issues:

```mermaid
graph TD
    subgraph "Shutdown Sequence"
        ActorsShutdown["actors.Shutdown()"]
        WasmHostClose["wasmhost.GetWasmHost().Close()"]
        MiddlewareShutdown["middleware.Shutdown()"]
        SqlShutdown["sqlclient.Shutdown()"]
        DgraphShutdown["dgraphclient.ShutdownConns()"]
        Neo4jShutdown["neo4jclient.CloseDrivers()"]
        LoggerClose["logger.Close()"]
        DbStop["db.Stop()"]
        ModusDbClose["db.CloseModusDb()"]
    end
    
    ActorsShutdown --> WasmHostClose
    WasmHostClose --> MiddlewareShutdown
    MiddlewareShutdown --> SqlShutdown
    SqlShutdown --> DgraphShutdown
    DgraphShutdown --> Neo4jShutdown
    Neo4jShutdown --> LoggerClose
    LoggerClose --> DbStop
    DbStop --> ModusDbClose
```

**Sources:** [runtime/services/services.go:66-88]()

---

# Page: API Explorer

# API Explorer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.trunk/trunk.yaml](.trunk/trunk.yaml)
- [go.work](go.work)
- [runtime/.gitignore](runtime/.gitignore)
- [runtime/explorer/content/ModusIcon.tsx](runtime/explorer/content/ModusIcon.tsx)
- [runtime/explorer/content/index.css](runtime/explorer/content/index.css)
- [runtime/explorer/content/index.html](runtime/explorer/content/index.html)
- [runtime/explorer/content/main.tsx](runtime/explorer/content/main.tsx)
- [runtime/explorer/content/package-lock.json](runtime/explorer/content/package-lock.json)
- [runtime/explorer/content/package.json](runtime/explorer/content/package.json)
- [runtime/explorer/content/postcss.config.js](runtime/explorer/content/postcss.config.js)
- [runtime/explorer/content/tailwind.config.js](runtime/explorer/content/tailwind.config.js)
- [runtime/explorer/content/vite.config.ts](runtime/explorer/content/vite.config.ts)
- [sdk/assemblyscript/src/assembly/index.ts](sdk/assemblyscript/src/assembly/index.ts)

</details>



The API Explorer is a web-based development interface that provides GraphQL schema introspection, query testing, and inference history monitoring for Modus applications. It serves as an interactive debugging and testing tool for developers working with Modus functions and their generated GraphQL endpoints.

For information about the underlying GraphQL engine that powers the API Explorer, see [GraphQL Engine](#5.2). For details about the development CLI commands, see [CLI Commands Reference](#3.1).

## Architecture Overview

The API Explorer is a React-based single-page application that integrates with the Modus Runtime to provide real-time GraphQL schema exploration and query execution capabilities.

### Component Architecture

```mermaid
graph TB
    subgraph "Web Browser"
        UI["React App<br/>runtime/explorer/content/main.tsx"]
        Explorer["@hypermode/react-api-explorer<br/>Component"]
        ModusIcon["ModusIcon<br/>Component"]
    end
    
    subgraph "Runtime HTTP Server"
        ExplorerRoute["/explorer/*<br/>Static Assets"]
        EndpointsAPI["/explorer/api/endpoints<br/>GraphQL Endpoints"]
        InferencesAPI["/explorer/api/inferences<br/>History Data"]
        GraphQLEndpoint["/graphql<br/>Query Execution"]
    end
    
    subgraph "Modus Runtime Core"
        SchemaGen["Schema Generator"]
        QueryEngine["GraphQL Engine"]
        InferenceTracker["Inference Tracker"]
    end
    
    UI --> Explorer
    UI --> ModusIcon
    Explorer --> ExplorerRoute
    Explorer --> EndpointsAPI
    Explorer --> InferencesAPI
    Explorer --> GraphQLEndpoint
    
    ExplorerRoute --> UI
    EndpointsAPI --> SchemaGen
    InferencesAPI --> InferenceTracker
    GraphQLEndpoint --> QueryEngine
```

Sources: [runtime/explorer/content/main.tsx:1-113](), [runtime/explorer/content/package.json:1-29]()

### Data Flow Architecture

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Browser as "Web Browser"
    participant ExplorerApp as "main.tsx"
    participant Runtime as "Modus Runtime"
    participant GraphQL as "GraphQL Engine"
    
    Dev->>Browser: Navigate to localhost:8686/explorer
    Browser->>ExplorerApp: Load React Application
    ExplorerApp->>Runtime: GET /explorer/api/endpoints
    Runtime-->>ExplorerApp: GraphQL endpoint URLs
    ExplorerApp->>Runtime: GET /explorer/api/inferences
    Runtime-->>ExplorerApp: Inference history data
    ExplorerApp->>Browser: Render ApiExplorer component
    
    Dev->>ExplorerApp: Write GraphQL query
    ExplorerApp->>GraphQL: POST /graphql
    GraphQL-->>ExplorerApp: Query results
    ExplorerApp->>Browser: Display results
    
    Note over ExplorerApp,Runtime: Periodic refresh of inference history
```

Sources: [runtime/explorer/content/main.tsx:46-91]()

## User Interface Components

The API Explorer consists of several key UI components that work together to provide a comprehensive GraphQL development experience.

### Main Application Component

The main application is defined in `main.tsx` and includes:

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| `App` | Root React component | Manages state and API calls |
| `ApiExplorer` | Main explorer interface | From `@hypermode/react-api-explorer` package |
| `ModusIcon` | Branding logo | Custom SVG component |

Sources: [runtime/explorer/content/main.tsx:19-112]()

### Theme Configuration

The explorer uses a custom dark theme with Modus branding colors:

```mermaid
graph LR
    subgraph "Theme Colors"
        BG["background: 150 60% 3%"]
        FG["foreground: 0 0% 100%"]
        PRIMARY["primary: 150 60% 39%"]
        SECONDARY["secondary: 157 73% 57%"]
        ACCENT["accent: 150 35% 17%"]
    end
    
    subgraph "UI Elements"
        CARDS["Cards & Popover"]
        INPUTS["Input Fields"]
        BUTTONS["Buttons"]
        BORDERS["Borders"]
    end
    
    BG --> CARDS
    PRIMARY --> BUTTONS
    ACCENT --> INPUTS
    ACCENT --> BORDERS
```

Sources: [runtime/explorer/content/main.tsx:20-40]()

### State Management

The application manages several key state variables:

| State Variable | Type | Purpose |
|----------------|------|---------|
| `endpoints` | `string[]` | GraphQL endpoint URLs |
| `inferences` | `any[]` | Historical inference data |
| `inferenceError` | `InferenceError` | Error state for inference loading |
| `refreshInferenceHistory` | `boolean` | Trigger for refreshing history |

Sources: [runtime/explorer/content/main.tsx:41-44]()

## API Integration

The API Explorer integrates with the Modus Runtime through several HTTP endpoints to provide real-time data and functionality.

### Endpoint Discovery

```mermaid
graph TD
    ExplorerApp["main.tsx App Component"]
    EndpointsAPI["/explorer/api/endpoints"]
    RuntimeEngine["Modus Runtime"]
    
    ExplorerApp -->|"fetch('/explorer/api/endpoints')"| EndpointsAPI
    EndpointsAPI -->|"Query available endpoints"| RuntimeEngine
    RuntimeEngine -->|"Return endpoint metadata"| EndpointsAPI
    EndpointsAPI -->|"JSON response"| ExplorerApp
    
    ExplorerApp -->|"Process URLs"| URLProcessor["URL Processing Logic"]
    URLProcessor -->|"Prepend origin if relative"| EndpointsList["endpoints state"]
```

Sources: [runtime/explorer/content/main.tsx:72-91]()

### Inference History Tracking

The explorer fetches and displays historical inference data:

```mermaid
graph TD
    RefreshTrigger["refreshInferenceHistory: true"]
    FetchFunction["fetchInferences()"]
    InferencesAPI["/explorer/api/inferences"]
    
    RefreshTrigger -->|"useEffect dependency"| FetchFunction
    FetchFunction -->|"GET request"| InferencesAPI
    InferencesAPI -->|"JSON response"| ResponseHandler["Response Handler"]
    
    ResponseHandler -->|"Success"| InferencesState["setInferences()"]
    ResponseHandler -->|"Error"| ErrorState["setInferenceError()"]
    
    InferencesState --> ExplorerComponent["ApiExplorer component"]
    ErrorState --> ExplorerComponent
```

Sources: [runtime/explorer/content/main.tsx:46-70]()

### Error Handling

The application includes comprehensive error handling for API failures:

| Error Type | Handler | Response |
|------------|---------|----------|
| Network Error | `catch` block | Console error logging |
| HTTP Error | Status check | `InferenceError` state update |
| JSON Parse Error | Try-catch | Graceful degradation |

Sources: [runtime/explorer/content/main.tsx:47-63]()

## Build System and Configuration

The API Explorer uses a Vite-based build system with React and TypeScript support.

### Build Configuration

```mermaid
graph TB
    subgraph "Source Files"
        TSX["main.tsx"]
        HTML["index.html"]
        CSS["index.css"]
        CONFIG["vite.config.ts"]
    end
    
    subgraph "Build Tools"
        VITE["Vite Build System"]
        REACT["@vitejs/plugin-react"]
        TAILWIND["@tailwindcss/vite"]
    end
    
    subgraph "Output"
        DIST["dist/"]
        ASSETS["assets/[name].js"]
        STYLES["assets/[name].css"]
    end
    
    TSX --> VITE
    HTML --> VITE
    CSS --> VITE
    CONFIG --> VITE
    
    VITE --> REACT
    VITE --> TAILWIND
    
    VITE --> DIST
    DIST --> ASSETS
    DIST --> STYLES
```

Sources: [runtime/explorer/content/vite.config.ts:1-31](), [runtime/explorer/content/package.json:6-9]()

### Dependencies

The API Explorer relies on several key dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| `@hypermode/react-api-explorer` | `^1.0.0-alpha.32` | Core GraphQL explorer component |
| `react` | `^19.1.0` | React framework |
| `@tailwindcss/vite` | `^4.1.3` | Styling framework |
| `vite` | `^6.2.6` | Build tool |

Sources: [runtime/explorer/content/package.json:11-26]()

## Runtime Integration

The API Explorer is served directly by the Modus Runtime as part of its web interface capabilities.

### Serving Architecture

```mermaid
graph TD
    RuntimeServer["Modus Runtime HTTP Server"]
    StaticHandler["Static File Handler"]
    APIHandlers["API Route Handlers"]
    
    subgraph "Explorer Routes"
        ExplorerStatic["/explorer/*<br/>Static Assets"]
        EndpointsRoute["/explorer/api/endpoints"]
        InferencesRoute["/explorer/api/inferences"]
    end
    
    subgraph "File System"
        DistFolder["runtime/explorer/content/dist/"]
        AssetsFolder["assets/"]
        IndexHTML["index.html"]
    end
    
    RuntimeServer --> StaticHandler
    RuntimeServer --> APIHandlers
    
    StaticHandler --> ExplorerStatic
    APIHandlers --> EndpointsRoute
    APIHandlers --> InferencesRoute
    
    ExplorerStatic --> DistFolder
    DistFolder --> AssetsFolder
    DistFolder --> IndexHTML
```

Sources: [runtime/explorer/content/vite.config.ts:29](), [runtime/explorer/content/main.tsx:49-50](), [runtime/explorer/content/main.tsx:76]()

### Development vs Production

The explorer supports both development and production deployment modes:

| Mode | Base URL | Build Command | Serving Method |
|------|----------|---------------|----------------|
| Development | `/explorer/` | `npm run dev` | Vite dev server |
| Production | `/explorer/` | `npm run build` | Static assets from `dist/` |

Sources: [runtime/explorer/content/package.json:7-9](), [runtime/explorer/content/vite.config.ts:29]()

---

# Page: Deployment and Operations

# Deployment and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci-go-test.yml](.github/workflows/ci-go-test.yml)
- [.github/workflows/ci-runtime-build.yml](.github/workflows/ci-runtime-build.yml)
- [.github/workflows/ci-runtime-integration-tests.yml](.github/workflows/ci-runtime-integration-tests.yml)
- [.github/workflows/ci-sdk-go-build.yml](.github/workflows/ci-sdk-go-build.yml)
- [.github/workflows/codeql.yml](.github/workflows/codeql.yml)
- [.github/workflows/release-runtime.yaml](.github/workflows/release-runtime.yaml)
- [.github/workflows/release-sdk-go.yaml](.github/workflows/release-sdk-go.yaml)
- [.gitignore](.gitignore)
- [Dockerfile](Dockerfile)
- [runtime/.goreleaser.yaml](runtime/.goreleaser.yaml)
- [runtime/Makefile](runtime/Makefile)
- [runtime/integration_tests/testdata/postgresql-example.wasm](runtime/integration_tests/testdata/postgresql-example.wasm)

</details>



This document covers production deployment strategies, operational monitoring, and release management for Modus applications and runtime infrastructure. It focuses on containerized deployments, CI/CD automation, and production operational considerations.

For development environment setup and local debugging workflows, see [Development Environment](#7.1). For Docker-specific deployment configurations, see [Docker Deployment](#8.1). For CI/CD pipeline integration details, see [CI/CD Integration](#8.2).

## Production Deployment Architecture

Modus applications can be deployed using multiple strategies depending on operational requirements. The runtime supports both containerized and binary deployment models with comprehensive health monitoring and operational tooling.

```mermaid
graph TD
    subgraph "Deployment Artifacts"
        SourceCode["Source Code<br/>modus.json + WASM modules"]
        RuntimeBinary["modus_runtime<br/>Multi-platform Binary"]
        DockerImage["modus_runtime:latest<br/>Container Image"]
    end
    
    subgraph "Deployment Targets"
        Kubernetes["Kubernetes Cluster<br/>Pod Orchestration"]
        DockerHost["Docker Host<br/>Container Runtime"]
        BareMetalHost["Bare Metal<br/>Direct Binary Execution"]
        CloudRun["Cloud Run<br/>Serverless Containers"]
    end
    
    subgraph "Operational Monitoring"
        HealthEndpoint["/health<br/>Health Check API"]
        MetricsEndpoint["/metrics<br/>Prometheus Metrics"]
        JSONLogs["--jsonlogs<br/>Structured Logging"]
        ExplorerUI["/explorer<br/>API Explorer UI"]
    end
    
    SourceCode --> RuntimeBinary
    SourceCode --> DockerImage
    
    RuntimeBinary --> BareMetalHost
    DockerImage --> Kubernetes
    DockerImage --> DockerHost
    DockerImage --> CloudRun
    
    Kubernetes --> HealthEndpoint
    DockerHost --> MetricsEndpoint
    BareMetalHost --> JSONLogs
    CloudRun --> ExplorerUI
    
    style SourceCode fill:#f9f9f9
    style RuntimeBinary fill:#f9f9f9
    style DockerImage fill:#f9f9f9
```

Sources: [Dockerfile:1-75](), [runtime/.goreleaser.yaml:13-34](), [runtime/Makefile:89-91]()

## Container Build Pipeline

The Modus runtime uses a multi-stage Docker build process that optimizes for both development tooling and production deployment efficiency.

```mermaid
graph LR
    subgraph "Build Stage 1: Node Builder"
        NodeBase["node:alpine"]
        ExplorerSrc["runtime/explorer/content<br/>package.json + TypeScript"]
        NPMInstall["npm ci<br/>npm run build"]
    end
    
    subgraph "Build Stage 2: Go Builder"
        GoBase["golang:alpine"]
        RuntimeSrc["runtime/*.go<br/>go.mod + go.sum"]
        LibDeps["lib/<br/>Shared Libraries"]
        GoWorkspace["go.work<br/>Workspace Config"]
        GoBuild["go build -o modus_runtime<br/>-ldflags version injection"]
    end
    
    subgraph "Final Runtime Image"
        UbuntuBase["ubuntu:24.04"]
        ModusUser["modus:1234<br/>Non-root User"]
        SystemTools["curl + iputils-ping<br/>jq + less"]
        RuntimeBinary["modus_runtime<br/>Executable Binary"]
        Entrypoint["ENTRYPOINT modus_runtime --jsonlogs<br/>HEALTHCHECK /health"]
    end
    
    NodeBase --> ExplorerSrc
    ExplorerSrc --> NPMInstall
    
    GoBase --> RuntimeSrc
    RuntimeSrc --> LibDeps
    LibDeps --> GoWorkspace
    GoWorkspace --> GoBuild
    NPMInstall --> GoBuild
    
    GoBuild --> UbuntuBase
    UbuntuBase --> ModusUser
    ModusUser --> SystemTools
    SystemTools --> RuntimeBinary
    RuntimeBinary --> Entrypoint
```

Sources: [Dockerfile:1-75](), [runtime/Makefile:22-28]()

## CI/CD Release Pipeline

The automated release system supports multiple artifact types with comprehensive testing and multi-platform distribution.

### Runtime Release Process

```mermaid
graph TD
    subgraph "Trigger Events"
        RuntimeTag["runtime/v*<br/>Git Tag Push"]
        PREvent["Pull Request<br/>Integration Testing"]
    end
    
    subgraph "Build Matrix"
        LinuxBuild["Linux Build<br/>amd64 + arm64"]
        MacOSBuild["macOS Build<br/>amd64 + arm64"] 
        WindowsBuild["Windows Build<br/>amd64 + arm64"]
        DockerBuild["Docker Build<br/>Multi-arch Images"]
    end
    
    subgraph "Testing Pipeline"
        UnitTests["go test -race<br/>All Go Modules"]
        IntegrationTests["PostgreSQL Integration<br/>WASM Module Tests"]
        SDKTests["Go SDK Examples<br/>TinyGo Compilation"]
        ExplorerBuild["npm run build<br/>API Explorer UI"]
    end
    
    subgraph "Release Artifacts"
        GoReleaser["goreleaser-pro<br/>Binary Archives"]
        GitHubRelease["GitHub Releases<br/>Assets + Checksums"]
        DockerRegistry["Container Registry<br/>Tagged Images"]
        EventDispatch["Repository Dispatch<br/>hyp-cluster Trigger"]
    end
    
    RuntimeTag --> LinuxBuild
    RuntimeTag --> MacOSBuild
    RuntimeTag --> WindowsBuild
    RuntimeTag --> DockerBuild
    
    PREvent --> UnitTests
    PREvent --> IntegrationTests
    PREvent --> SDKTests
    PREvent --> ExplorerBuild
    
    LinuxBuild --> GoReleaser
    MacOSBuild --> GoReleaser
    WindowsBuild --> GoReleaser
    GoReleaser --> GitHubRelease
    DockerBuild --> DockerRegistry
    GitHubRelease --> EventDispatch
```

Sources: [.github/workflows/release-runtime.yaml:1-61](), [.github/workflows/ci-runtime-integration-tests.yml:1-42](), [.github/workflows/ci-go-test.yml:1-66]()

### SDK Release Process

The SDK release pipeline supports independent versioning and package distribution for different language targets.

| SDK Type | Version Pattern | Artifacts | Distribution |  
|----------|----------------|-----------|--------------|
| Go SDK | `sdk/go/v*` | `sdk.json`, `templates_go_*.tar.gz` | GitHub Releases |
| AssemblyScript SDK | `sdk/as/v*` | NPM packages | NPM Registry |

Sources: [.github/workflows/release-sdk-go.yaml:1-47]()

## Operational Monitoring

### Health Check System

The runtime provides comprehensive health monitoring through standardized endpoints and structured logging.

```mermaid
graph LR
    subgraph "Health Monitoring"
        HealthEndpoint["/health<br/>HTTP Health Check"]
        HealthStatus["status: ok<br/>JSON Response"]
        DockerHealthCheck["HEALTHCHECK --interval=30s<br/>curl + jq validation"]
    end
    
    subgraph "Metrics Collection"
        MetricsEndpoint["/metrics<br/>Prometheus Format"]
        RuntimeMetrics["Runtime Statistics<br/>WASM Execution Metrics"]
        SystemMetrics["System Resources<br/>Memory + CPU Usage"]
    end
    
    subgraph "Logging Configuration"
        JSONLogs["--jsonlogs<br/>Structured Output"]
        LogLevel["MODUS_ENV=dev<br/>Development Logging"]
        LogFormat["Timestamp + Level<br/>Message + Context"]
    end
    
    HealthEndpoint --> HealthStatus
    HealthStatus --> DockerHealthCheck
    
    MetricsEndpoint --> RuntimeMetrics
    MetricsEndpoint --> SystemMetrics
    
    JSONLogs --> LogLevel
    LogLevel --> LogFormat
```

Sources: [Dockerfile:74-74](), [runtime/Makefile:33-33]()

### Production Configuration

Production deployments require specific configuration for security, performance, and operational requirements.

#### Container Security

- **Non-root execution**: Runtime runs as `modus:1234` user account
- **Minimal base image**: Ubuntu 24.04 with essential tools only
- **Resource isolation**: Container-based process isolation
- **Network security**: Configurable port binding (default `:8686`)

#### Resource Requirements

| Component | Memory | CPU | Storage |
|-----------|--------|-----|---------|
| Runtime Base | 64MB | 0.1 vCPU | 100MB |
| WASM Modules | Variable | Variable | Variable |
| Explorer UI | 32MB | 0.05 vCPU | 50MB |
| Database Connections | 16MB each | Minimal | Minimal |

Sources: [Dockerfile:42-75]()

## Build System Integration

### Makefile Targets

The runtime includes comprehensive build automation through standardized make targets.

```mermaid
graph TD
    subgraph "Development Targets"
        ModusTidy["make tidy<br/>go mod tidy + formatting"]
        ModusBuild["make build<br/>Explorer + Runtime Binary"]
        ModusRun["make run<br/>Development Server"]
        ModusRunApp["make runapp<br/>Application Runner"]
    end
    
    subgraph "Testing Targets"
        ModusTest["make test<br/>Unit Tests + Testdata"]
        ModusTestRace["make test-race<br/>Race Condition Detection"]
        ModusTestIntegration["make test-integration<br/>Database Integration"]
        ModusTestCI["make test-ci<br/>JUnit Report Generation"]
    end
    
    subgraph "Build Dependencies"
        ExplorerBuild["make build-explorer<br/>npm ci + npm run build"]
        TestdataBuild["make build-testdata<br/>AssemblyScript + Go Examples"]
        IntegrationTestdata["make build-integration-testdata<br/>PostgreSQL Example WASM"]
    end
    
    subgraph "Production Targets"
        DockerBuild["make docker-build<br/>Container Image Creation"]
        Clean["make clean<br/>Artifact Cleanup"]
    end
    
    ModusBuild --> ExplorerBuild
    ModusTest --> TestdataBuild
    ModusTestIntegration --> IntegrationTestdata
    ModusTestCI --> TestdataBuild
    DockerBuild --> ExplorerBuild
```

Sources: [runtime/Makefile:1-96]()

### Cross-Platform Build Configuration

The runtime supports native compilation across multiple operating systems and architectures through GoReleaser configuration.

#### Supported Platforms

| OS | Architecture | Binary Format | Archive Format |
|----|-----------|--------------|--------------| 
| Linux | amd64, arm64 | ELF | tar.gz |
| macOS | amd64, arm64 | Mach-O | tar.gz |
| Windows | amd64, arm64 | PE (.exe) | zip |

#### Build Optimization

- **CGO disabled**: Pure Go compilation for portability
- **Link-time optimization**: `-s -w` flags for size reduction  
- **Version injection**: Build-time version embedding
- **Windows compatibility**: `-checklinkname=0` flag for Windows builds

Sources: [runtime/.goreleaser.yaml:13-34](), [runtime/Makefile:9-12]()

---

# Page: Docker Deployment

# Docker Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [Dockerfile](Dockerfile)
- [runtime/.goreleaser.yaml](runtime/.goreleaser.yaml)
- [runtime/Makefile](runtime/Makefile)
- [runtime/integration_tests/testdata/postgresql-example.wasm](runtime/integration_tests/testdata/postgresql-example.wasm)

</details>



This document covers the containerization and Docker deployment strategy for Modus applications and the Modus Runtime. It details the multi-stage build process, container configuration, and deployment workflows for running Modus applications in containerized environments.

For information about CI/CD integration and automated deployment pipelines, see [CI/CD Integration](#8.2).

## Container Architecture

The Modus Docker deployment uses a multi-stage build approach that packages both the API Explorer web interface and the Modus Runtime into a single container image. The containerization process is optimized for production deployment while maintaining development tooling accessibility.

```mermaid
graph TD
    subgraph "Multi-Stage Build Process"
        nodeA[node-builder] --> nodeB["API Explorer Build"]
        goA[golang-builder] --> goB["Runtime Build"]
        nodeB --> finalA[ubuntu-container]
        goB --> finalA
    end
    
    subgraph "Container Components"
        finalA --> runtimeBin["modus_runtime binary"]
        finalA --> explorerUI["Explorer UI assets"]
        finalA --> systemTools["System utilities"]
    end
    
    subgraph "Runtime Services"
        runtimeBin --> httpServer["HTTP Server :8686"]
        runtimeBin --> graphqlEngine["GraphQL Engine"]
        runtimeBin --> wasmHost["WebAssembly Host"]
        explorerUI --> apiExplorer["API Explorer Interface"]
    end
```

Sources: [Dockerfile:1-75](), [runtime/Makefile:89-91]()

## Build Stages

### Stage 1: Explorer Application Build

The first build stage compiles the API Explorer web application using Node.js and npm. This stage creates the static assets needed for the web-based development interface.

```mermaid
graph LR
    subgraph "node-builder Stage"
        packageJson["package.json"] --> npmInstall["npm ci"]
        sourceFiles["Explorer source files"] --> npmBuild["npm run build"]
        npmInstall --> npmBuild
        npmBuild --> distAssets["dist/ assets"]
    end
```

The explorer build process installs dependencies first for optimal Docker layer caching, then copies source files and builds the application:

- Dependency installation: [Dockerfile:6-7]()
- Source compilation: [Dockerfile:10-11]()
- Output generation to `dist/` directory

Sources: [Dockerfile:2-11]()

### Stage 2: Runtime Binary Build

The second stage builds the Modus Runtime binary using Go, incorporating workspace dependencies and excluding SDK components not needed for runtime execution.

```mermaid
graph LR
    subgraph "golang-builder Stage"
        goWork["go.work modification"] --> goMod["go.mod download"]
        libDeps["lib/ dependencies"] --> goBuild["Go compilation"]
        runtimeSource["runtime/ source"] --> goBuild
        explorerAssets["Explorer dist/"] --> goBuild
        goMod --> goBuild
        goBuild --> binaryOut["modus_runtime binary"]
    end
```

Key build optimizations include:
- Workspace file modification to exclude SDK directories: [Dockerfile:22-23]()
- Dependency caching through separate `go mod download`: [Dockerfile:30-31]()
- Cross-platform compilation support: [Dockerfile:38-39]()
- Version injection via build flags: [Dockerfile:39]()

Sources: [Dockerfile:14-39]()

### Stage 3: Production Container

The final stage creates a minimal Ubuntu-based container with the runtime binary, explorer assets, and essential system utilities.

```mermaid
graph TD
    subgraph "ubuntu:24.04 Base"
        userSetup["User/Group Creation"] --> toolInstall["System Tools"]
        toolInstall --> binaryCopy["Binary Installation"]
        binaryCopy --> certUpdate["Certificate Update"]
        certUpdate --> entrypoint["Entrypoint Configuration"]
        entrypoint --> healthcheck["Health Check Setup"]
    end
    
    subgraph "Installed Components"
        curl["curl"]
        ping["iputils-ping"]
        jq["jq"]
        less["less"]
        certs["ca-certificates"]
        tzdata["tzdata"]
    end
```

Container security and operational features:
- Non-root user execution with UID/GID 1234: [Dockerfile:46-47]()
- Essential debugging tools installation: [Dockerfile:50-55]()
- JSON logging by default: [Dockerfile:71]()
- Health check endpoint monitoring: [Dockerfile:74]()

Sources: [Dockerfile:42-75]()

## Build Configuration

### Makefile Integration

The runtime Makefile provides Docker build automation with version management and dependency coordination.

| Target | Description | Dependencies |
|--------|-------------|--------------|
| `docker-build` | Build Docker image with version tagging | Explorer build completion |
| `build-explorer` | Compile API Explorer assets | Node.js dependencies |
| `build` | Create runtime binary | Go compilation, explorer assets |

The Docker build process integrates with the broader build system:
- Version extraction from Git tags: [runtime/Makefile:2]()
- Automatic explorer building: [runtime/Makefile:91]()
- Build context from repository root: [runtime/Makefile:91]()

Sources: [runtime/Makefile:89-95]()

### Build Arguments and Versioning

The Docker build accepts several build arguments for customization:

```mermaid
graph LR
    subgraph "Build Arguments"
        buildArg1["BUILDPLATFORM"] --> crossCompile["Cross-compilation"]
        buildArg2["TARGETOS"] --> targetConfig["Target Configuration"]
        buildArg3["TARGETARCH"] --> targetConfig
        buildArg4["RUNTIME_RELEASE_VERSION"] --> versionInject["Version Injection"]
    end
    
    subgraph "Compilation Outputs"
        targetConfig --> binaryGen["Platform-specific Binary"]
        versionInject --> versionInfo["Runtime Version Info"]
    end
```

Version management is handled through:
- Git-based version detection: [runtime/Makefile:2]()
- Build-time version injection: [Dockerfile:39]()
- Runtime version reporting through build flags

Sources: [Dockerfile:38-39](), [runtime/Makefile:2-3]()

## Container Runtime Configuration

### Service Initialization

The containerized Modus Runtime starts with JSON logging enabled and exposes several key endpoints for application and infrastructure management.

```mermaid
graph TD
    subgraph "Runtime Services"
        entrypoint["modus_runtime --jsonlogs"] --> httpInit["HTTP Server Init"]
        httpInit --> endpoints["Service Endpoints"]
    end
    
    subgraph "Exposed Endpoints"
        endpoints --> health[":8686/health"]
        endpoints --> metrics[":8686/metrics"]
        endpoints --> explorer[":8686/explorer"]
        endpoints --> graphql[":8686/graphql"]
    end
    
    subgraph "Health Monitoring"
        health --> healthCheck["Health Check Process"]
        healthCheck --> statusResponse["JSON Status Response"]
    end
```

The container is configured for operational monitoring:
- Default port 8686 exposure
- JSON-structured logging: [Dockerfile:71]()
- Health endpoint with JSON validation: [Dockerfile:74]()
- Automated health check every 30 seconds with 5-second timeout

Sources: [Dockerfile:71-74]()

### User and Security Context

The container implements security best practices through non-privileged execution:

- Custom user/group creation with fixed IDs: [Dockerfile:46-47]()
- Non-root execution context: [Dockerfile:67]()
- Working directory in user home: [Dockerfile:68]()
- Minimal privilege escalation surface

Sources: [Dockerfile:46-47](), [Dockerfile:67-68]()

## Deployment Workflows

### Local Development

For local development and testing, the Docker container can be built and run using the provided Makefile targets:

```bash
make docker-build
```

This command builds the complete container image with the current codebase version.

### Production Deployment

The container is designed for production deployment with:
- Health check integration for orchestrator monitoring
- JSON logging for log aggregation systems
- Certificate and timezone updates for enterprise environments
- Minimal attack surface through Ubuntu LTS base

The health check endpoint returns JSON status information that can be monitored by container orchestration platforms like Kubernetes or Docker Swarm.

Sources: [Dockerfile:61-64](), [Dockerfile:74]()

## Integration with Release Process

The Docker build process integrates with the broader release automation through GoReleaser configuration, enabling automated container image publication as part of the release pipeline.

The release configuration supports:
- Multi-platform binary compilation: [runtime/.goreleaser.yaml:18-24]()
- Version-aware builds: [runtime/.goreleaser.yaml:29]()
- Archive generation for distribution: [runtime/.goreleaser.yaml:47-56]()

Sources: [runtime/.goreleaser.yaml:13-64]()

---

# Page: CI/CD Integration

# CI/CD Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/renovate.json](.github/renovate.json)
- [.github/workflows/ci-cli-build.yml](.github/workflows/ci-cli-build.yml)
- [.github/workflows/ci-cli-lint.yml](.github/workflows/ci-cli-lint.yml)
- [.github/workflows/ci-go-test.yml](.github/workflows/ci-go-test.yml)
- [.github/workflows/ci-runtime-build.yml](.github/workflows/ci-runtime-build.yml)
- [.github/workflows/ci-runtime-integration-tests.yml](.github/workflows/ci-runtime-integration-tests.yml)
- [.github/workflows/ci-sdk-as-build.yml](.github/workflows/ci-sdk-as-build.yml)
- [.github/workflows/ci-sdk-as-lint.yml](.github/workflows/ci-sdk-as-lint.yml)
- [.github/workflows/ci-sdk-as-test.yml](.github/workflows/ci-sdk-as-test.yml)
- [.github/workflows/ci-sdk-go-build.yml](.github/workflows/ci-sdk-go-build.yml)
- [.github/workflows/codeql.yml](.github/workflows/codeql.yml)
- [.github/workflows/release-runtime.yaml](.github/workflows/release-runtime.yaml)
- [.github/workflows/release-sdk-go.yaml](.github/workflows/release-sdk-go.yaml)
- [cli/eslint.config.js](cli/eslint.config.js)

</details>



This document covers the continuous integration and continuous deployment (CI/CD) infrastructure for the Modus framework. It details automated testing workflows, build pipelines, release processes, and quality gates that ensure code reliability and enable automated delivery of runtime binaries, SDK packages, and development tools.

For information about Docker-based deployment strategies, see [Docker Deployment](#8.1).

## Workflow Architecture

The Modus CI/CD system uses GitHub Actions to orchestrate testing, building, and releasing across multiple components. The system is designed around path-based triggers to optimize build times and resource usage.

### CI/CD Pipeline Overview

```mermaid
flowchart TD
    subgraph "Source Control"
        PR["Pull Request"]
        Tags["Git Tags<br/>runtime/v*, sdk/go/v*"]
        Main["main branch"]
    end
    
    subgraph "Continuous Integration"
        GoTest["ci-go-test<br/>Go Unit Tests"]
        RuntimeBuild["ci-runtime-build<br/>Cross-platform Build"]
        RuntimeIntegration["ci-runtime-integration-tests<br/>Integration Tests"]
        SDKGoBuild["ci-sdk-go-build<br/>Go SDK Build"]
        SDKASBuild["ci-sdk-as-build<br/>AssemblyScript Build"]
        CLIBuild["ci-cli-build<br/>CLI Build & Test"]
        CodeQL["codeql<br/>Security Analysis"]
    end
    
    subgraph "Quality Gates"
        Lint["Linting<br/>ESLint, Go fmt"]
        RaceDetection["Race Detection<br/>go test -race"]
        TestReporting["Test Summary<br/>XML Reports"]
    end
    
    subgraph "Release Pipelines"
        RuntimeRelease["release-runtime<br/>GoReleaser"]
        SDKRelease["release-sdk-go<br/>Go Module Release"]
        ReleaseInfo["release-info<br/>Metadata Generation"]
    end
    
    subgraph "Artifacts"
        Binaries["Runtime Binaries<br/>Multi-platform"]
        DockerImages["Docker Images<br/>Container Registry"]
        SDKPackages["SDK Packages<br/>Go Modules"]
        CLIPackages["CLI Packages<br/>npm"]
    end
    
    PR --> GoTest
    PR --> RuntimeBuild
    PR --> RuntimeIntegration
    PR --> SDKGoBuild
    PR --> SDKASBuild
    PR --> CLIBuild
    
    Main --> CodeQL
    
    GoTest --> RaceDetection
    RuntimeIntegration --> TestReporting
    SDKGoBuild --> Lint
    
    Tags --> RuntimeRelease
    Tags --> SDKRelease
    
    RuntimeRelease --> Binaries
    RuntimeRelease --> DockerImages
    RuntimeRelease --> ReleaseInfo
    
    SDKRelease --> SDKPackages
    SDKRelease --> ReleaseInfo
```

**Sources:** [.github/workflows/ci-go-test.yml](), [.github/workflows/ci-runtime-build.yml](), [.github/workflows/release-runtime.yaml](), [.github/workflows/release-sdk-go.yaml]()

### Path-Based Trigger Strategy

The CI system implements intelligent path-based triggers to minimize unnecessary builds and optimize resource usage:

| Workflow | Trigger Paths | Purpose |
|----------|---------------|---------|
| `ci-go-test` | `**/*.go`, `**/go.mod`, `**/testdata/**` | Go code changes |
| `ci-runtime-build` | `runtime/**/*.go`, `runtime/go.mod` | Runtime-specific changes |
| `ci-runtime-integration-tests` | `runtime/**` | Runtime integration changes |
| `ci-sdk-go-build` | `sdk/go/**` | Go SDK changes |
| `ci-sdk-as-build` | `sdk/assemblyscript/**` | AssemblyScript SDK changes |
| `ci-cli-build` | `cli/**` | CLI changes |

**Sources:** [.github/workflows/ci-go-test.yml:11-15](), [.github/workflows/ci-runtime-build.yml:10-14](), [.github/workflows/ci-sdk-go-build.yml:10-12]()

## Continuous Integration Pipelines

### Go Testing Infrastructure

The `ci-go-test` workflow provides comprehensive testing for all Go modules in the repository using a dynamic discovery strategy:

```mermaid
flowchart LR
    subgraph "Directory Discovery"
        FindGoMod["find . -name 'go.mod'<br/>Scan Repository"]
        GenerateMatrix["Generate Build Matrix<br/>JSON Array Output"]
    end
    
    subgraph "Test Execution"
        SetupGo["Setup Go 1.24.4<br/>Cache Dependencies"]
        RunTests["go test -v -race<br/>Unit Tests with Race Detection"]
        JUnitReport["go-junit-report<br/>XML Test Reports"]
    end
    
    subgraph "Reporting"
        TestSummary["test-summary/action<br/>GitHub Actions Summary"]
        ArtifactUpload["report.xml<br/>Test Artifacts"]
    end
    
    FindGoMod --> GenerateMatrix
    GenerateMatrix --> SetupGo
    SetupGo --> RunTests
    RunTests --> JUnitReport
    JUnitReport --> TestSummary
    JUnitReport --> ArtifactUpload
```

The workflow uses the `jstemmer/go-junit-report/v2` tool to convert Go test output to JUnit XML format for integration with GitHub's test reporting system.

**Sources:** [.github/workflows/ci-go-test.yml:31-38](), [.github/workflows/ci-go-test.yml:58-60]()

### Runtime Integration Testing

The runtime integration tests run on high-performance `warp-ubuntu-latest-x64-4x` runners and include database connectivity testing:

```mermaid
flowchart TD
    subgraph "Test Environment"
        SetupGo["Setup Go 1.24.4"]
        SetupNode["Setup Node >=22"]
        WarpRunner["warp-ubuntu-latest-x64-4x<br/>High-performance Runner"]
    end
    
    subgraph "Integration Testing"
        MakeTarget["make test-integration-ci<br/>Integration Test Suite"]
        DBTests["Database Integration<br/>PostgreSQL, etc."]
        RuntimeTests["Runtime Component Tests<br/>GraphQL, Agents, WASM"]
    end
    
    subgraph "Test Reporting"
        XMLReport["report.xml<br/>Test Results"]
        ActionSummary["test-summary/action<br/>GitHub Summary"]
    end
    
    SetupGo --> MakeTarget
    SetupNode --> MakeTarget
    MakeTarget --> DBTests
    MakeTarget --> RuntimeTests
    DBTests --> XMLReport
    RuntimeTests --> XMLReport
    XMLReport --> ActionSummary
```

**Sources:** [.github/workflows/ci-runtime-integration-tests.yml:21-22](), [.github/workflows/ci-runtime-integration-tests.yml:34-36]()

### SDK Build Validation

The Go SDK build workflow validates both tools and examples using a matrix strategy:

```mermaid
flowchart LR
    subgraph "Discovery Phase"
        FindTools["find ./sdk/go/tools<br/>Discover Tool Directories"]
        FindExamples["find ./sdk/go/examples<br/>Discover Example Directories"]
        MatrixOutput["JSON Matrix Output<br/>Directory Arrays"]
    end
    
    subgraph "Build Matrix"
        ToolsBuild["sdk-go-build-tools<br/>Go Build Tools"]
        ExamplesBuild["sdk-go-build-examples<br/>TinyGo Build Examples"]
        SetupTinyGo["Setup TinyGo 0.36.0<br/>WASM Compilation"]
    end
    
    subgraph "Build Execution"
        GoBuild["go build .<br/>Standard Go Build"]
        BuildScript["./build.sh<br/>TinyGo WASM Build"]
    end
    
    FindTools --> MatrixOutput
    FindExamples --> MatrixOutput
    MatrixOutput --> ToolsBuild
    MatrixOutput --> ExamplesBuild
    ToolsBuild --> GoBuild
    ExamplesBuild --> SetupTinyGo
    SetupTinyGo --> BuildScript
```

**Sources:** [.github/workflows/ci-sdk-go-build.yml:28-43](), [.github/workflows/ci-sdk-go-build.yml:84-89]()

## Release Automation

### Runtime Release Pipeline

The runtime release process uses GoReleaser Pro for multi-platform binary distribution:

```mermaid
flowchart TD
    subgraph "Release Trigger"
        TagPush["git push --tags<br/>runtime/v*"]
        VersionValidation["Validate Tag Format<br/>runtime/v prefix"]
    end
    
    subgraph "Build Preparation"
        APIExplorer["Build API Explorer<br/>npm ci && npm run build"]
        SetupGo["Setup Go 1.24.4<br/>Cache Dependencies"]
        WarpRunner["warp-ubuntu-latest-x64-4x<br/>High-performance Runner"]
    end
    
    subgraph "GoReleaser Execution"
        GoReleaserPro["goreleaser-pro<br/>Multi-platform Build"]
        CodeSigning["macOS Code Signing<br/>P12 Certificates"]
        Notarization["macOS Notarization<br/>Apple Developer Account"]
    end
    
    subgraph "Artifacts"
        PlatformBinaries["Platform Binaries<br/>macOS, Linux, Windows"]
        DockerImages["Docker Images<br/>Container Registry"]
        GitHubRelease["GitHub Release<br/>Assets & Changelog"]
    end
    
    subgraph "External Integration"
        RepoDispatch["Repository Dispatch<br/>hypermodeinc/hyp-cluster"]
        ReleaseInfo["release-info.yaml<br/>Metadata Generation"]
    end
    
    TagPush --> VersionValidation
    VersionValidation --> APIExplorer
    APIExplorer --> SetupGo
    SetupGo --> GoReleaserPro
    GoReleaserPro --> CodeSigning
    CodeSigning --> Notarization
    Notarization --> PlatformBinaries
    PlatformBinaries --> DockerImages
    DockerImages --> GitHubRelease
    GitHubRelease --> RepoDispatch
    GitHubRelease --> ReleaseInfo
```

The runtime release includes macOS code signing and notarization using certificates and keys stored in GitHub Secrets.

**Sources:** [.github/workflows/release-runtime.yaml:14-49](), [.github/workflows/release-runtime.yaml:50-56]()

### SDK Release Management

The Go SDK release workflow creates packaged distributions and updates Go module metadata:

```mermaid
flowchart LR
    subgraph "Release Process"
        TagPush["git push --tags<br/>sdk/go/v*"]
        ParseVersion["Parse SDK Version<br/>Extract v* from tag"]
        PrepareRelease["./scripts/prepare-release.sh<br/>Package Generation"]
    end
    
    subgraph "Artifacts"
        SDKJson["sdk.json<br/>Metadata File"]
        TemplatesTar["templates_go_*.tar.gz<br/>Project Templates"]
        PreRelease["Prerelease Detection<br/>Contains '-' in version"]
    end
    
    subgraph "Publishing"
        GitHubRelease["softprops/action-gh-release<br/>GitHub Release"]
        ReleaseInfo["release-info.yaml<br/>Metadata Generation"]
    end
    
    TagPush --> ParseVersion
    ParseVersion --> PrepareRelease
    PrepareRelease --> SDKJson
    PrepareRelease --> TemplatesTar
    SDKJson --> GitHubRelease
    TemplatesTar --> GitHubRelease
    GitHubRelease --> PreRelease
    GitHubRelease --> ReleaseInfo
```

**Sources:** [.github/workflows/release-sdk-go.yaml:22-33](), [.github/workflows/release-sdk-go.yaml:34-41]()

## Testing Strategy

### Test Matrix Configuration

The testing infrastructure uses dynamic matrix generation to handle multiple Go modules and SDK examples:

| Component | Test Strategy | Tools |
|-----------|---------------|-------|
| Go Modules | Unit tests with race detection | `go test -v -race` |
| Runtime | Integration tests with databases | `make test-integration-ci` |
| Go SDK Examples | TinyGo compilation validation | `./build.sh` |
| AssemblyScript SDK | npm test suite | `npm run test` |
| CLI | Build validation | `npm run build` |

### Test Reporting Infrastructure

All test workflows generate structured reports using the `test-summary/action@v2` GitHub Action:

```mermaid
flowchart LR
    subgraph "Test Execution"
        GoTest["go test -v -race<br/>Unit Test Execution"]
        JUnitReport["go-junit-report<br/>XML Generation"]
    end
    
    subgraph "Report Processing"
        XMLFile["report.xml<br/>JUnit XML Format"]
        TestSummary["test-summary/action@v2<br/>GitHub Action"]
    end
    
    subgraph "GitHub Integration"
        ActionsSummary["GitHub Actions Summary<br/>Test Results Display"]
        PRComments["Pull Request Comments<br/>Test Status"]
    end
    
    GoTest --> JUnitReport
    JUnitReport --> XMLFile
    XMLFile --> TestSummary
    TestSummary --> ActionsSummary
    TestSummary --> PRComments
```

**Sources:** [.github/workflows/ci-go-test.yml:58-65](), [.github/workflows/ci-runtime-integration-tests.yml:37-41]()

## Code Quality and Security

### CodeQL Security Analysis

The repository uses GitHub's CodeQL for automated security analysis of Go and TypeScript/JavaScript code:

```mermaid
flowchart TD
    subgraph "Analysis Triggers"
        MainPush["Push to main branch"]
        PRs["Pull Requests"]
        Schedule["Weekly Schedule<br/>Wednesday 3:41 AM"]
    end
    
    subgraph "Language Matrix"
        GoAnalysis["Go Language<br/>autobuild mode"]
        JSAnalysis["JavaScript/TypeScript<br/>none build mode"]
        SetupGo["Setup Go 1.24.4<br/>For Go analysis"]
    end
    
    subgraph "CodeQL Execution"
        Initialize["Initialize CodeQL<br/>Security & Quality Queries"]
        Analyze["Perform Analysis<br/>Security Vulnerability Detection"]
        Results["Security Events<br/>GitHub Security Tab"]
    end
    
    MainPush --> GoAnalysis
    PRs --> GoAnalysis
    Schedule --> GoAnalysis
    MainPush --> JSAnalysis
    
    GoAnalysis --> SetupGo
    SetupGo --> Initialize
    JSAnalysis --> Initialize
    Initialize --> Analyze
    Analyze --> Results
```

**Sources:** [.github/workflows/codeql.yml:14-20](), [.github/workflows/codeql.yml:49-53]()

### Linting Infrastructure

Code quality is enforced through multiple linting workflows:

- **CLI**: ESLint with TypeScript rules configured in [cli/eslint.config.js]()
- **AssemblyScript SDK**: ESLint and Prettier formatting checks
- **Go Code**: Built-in `go fmt` and race detection

**Sources:** [.github/workflows/ci-cli-lint.yml](), [.github/workflows/ci-sdk-as-lint.yml:51-54](), [cli/eslint.config.js:6-24]()

## Deployment Integration

### External System Integration

The runtime release workflow integrates with external deployment systems through repository dispatch events:

```mermaid
flowchart LR
    subgraph "Modus Release"
        RuntimeRelease["Runtime Release<br/>GitHub Actions"]
        ReleaseComplete["Release Artifacts<br/>Published"]
    end
    
    subgraph "External Integration"
        RepoDispatch["peter-evans/repository-dispatch<br/>Cross-repo Event"]
        HypCluster["hypermodeinc/hyp-cluster<br/>Deployment Repository"]
        ClientPayload["Client Payload<br/>repo, tag metadata"]
    end
    
    subgraph "Deployment Pipeline"
        ClusterUpdate["Cluster Update<br/>Automated Deployment"]
        ContainerRegistry["Container Registry<br/>Updated Images"]
    end
    
    RuntimeRelease --> ReleaseComplete
    ReleaseComplete --> RepoDispatch
    RepoDispatch --> HypCluster
    RepoDispatch --> ClientPayload
    HypCluster --> ClusterUpdate
    ClusterUpdate --> ContainerRegistry
```

**Sources:** [.github/workflows/release-runtime.yaml:50-56]()

### Dependency Management

The repository uses Renovate for automated dependency updates with a custom configuration extending `github>hypermodeinc/renovate-config`:

**Sources:** [.github/renovate.json:1-5]()