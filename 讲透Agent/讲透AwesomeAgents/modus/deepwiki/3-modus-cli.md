<!-- source: DeepWiki mcp.deepwiki.com · repo hypermodeinc/modus · page 3 Modus CLI · fetched 2026-10-26 -->

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

