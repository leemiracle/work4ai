<!-- source: DeepWiki mcp.deepwiki.com · repo hypermodeinc/modus · page 2 Getting Started · fetched 2026-10-27 -->

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

