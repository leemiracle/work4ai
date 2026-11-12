<!-- source: DeepWiki mcp.deepwiki.com · repo hypermodeinc/modus · page 4 Software Development Kits · fetched 2026-10-27 -->

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

