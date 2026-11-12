<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/kernel-memory · page 9 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.gitmodules](.gitmodules)
- [README.md](README.md)

</details>



This document provides technical guidance for developers working with the Kernel Memory (KM²) codebase. It covers repository structure, build configuration, testing infrastructure, and development environment setup. For information about system architecture and runtime components, see [Architecture](#3). For information about configuration files used at runtime, see [Configuration System](#6).

**Important Note**: KM² is an active research project with no stability guarantees. The codebase evolves rapidly, and breaking changes are expected. See [Project Status and Warnings](#1.1) for details.

---

## Development Prerequisites

KM² is a polyglot system with the following technology requirements:

| Technology | Purpose | Requirement |
|------------|---------|-------------|
| .NET SDK | Primary development language | .NET 8.0 or later (C# 12) |
| Python | Supporting scripts and components | Python 3.8+ |
| Node.js | Supporting components | Node.js 16+ |
| SQLite | Data persistence | Included via NuGet packages |
| Git | Version control | Git 2.30+ with submodule support |

The codebase uses modern C# language features and requires a recent .NET SDK for compilation.

**Mermaid: Development Technology Stack**

```mermaid
graph TB
    Developer["Developer"]
    
    subgraph "Primary Development"
        DotNet[".NET SDK 8.0+<br/>C# 12<br/>Primary Language"]
        Solution["KernelMemory.sln<br/>Solution File"]
    end
    
    subgraph "Supporting Languages"
        Python["Python 3.8+<br/>Scripts & Components"]
        Node["Node.js 16+<br/>Supporting Components"]
    end
    
    subgraph "Build Configuration"
        DirProps["Directory.Build.props<br/>Shared Build Settings"]
        DirPkg["Directory.Packages.props<br/>Centralized Package Versions"]
    end
    
    subgraph "Data & Storage"
        SQLite["SQLite<br/>Microsoft.Data.Sqlite NuGet"]
        FileSystem["File System<br/>Local/Network Storage"]
    end
    
    subgraph "Version Control"
        Git["Git Repository<br/>github.com/microsoft/kernel-memory"]
        Submodule["docs/ Submodule<br/>kernel-memory-docs"]
    end
    
    Developer --> DotNet
    Developer --> Python
    Developer --> Node
    
    DotNet --> Solution
    Solution --> DirProps
    Solution --> DirPkg
    
    DotNet --> SQLite
    DotNet --> FileSystem
    
    Developer --> Git
    Git --> Submodule
    
    DirProps --> "Core.csproj"
    DirProps --> "Extensions/*.csproj"
    DirProps --> "Tests/*.csproj"
```

Sources: [README.md:1-80](), [.gitmodules:1-4]()

---

## Repository Structure

The KM² repository follows a standard .NET solution structure with centralized build configuration. The organization separates core functionality, extensions, tests, and infrastructure concerns.

### Solution and Project Organization

```mermaid
graph TB
    Root["Repository Root"]
    
    subgraph "Source Code"
        Service["service/<br/>Core Implementation"]
        Extensions["extensions/<br/>AI Provider Extensions"]
        Infra["infrastructure/<br/>Build & Deploy"]
    end
    
    subgraph "Core Projects"
        Core["service/Core/Core.csproj<br/>Core Services & CLI"]
        CoreTests["tests/Core.UnitTests/"]
    end
    
    subgraph "Extension Projects"
        OpenAI["extensions/OpenAI/<br/>OpenAI.csproj"]
        Anthropic["extensions/Anthropic/<br/>Anthropic.csproj"]
        Discord["extensions/Discord/<br/>Discord.csproj"]
        ExtTests["tests/*.Tests/<br/>Extension Tests"]
    end
    
    subgraph "Build Configuration"
        Sln["KernelMemory.sln<br/>Solution File"]
        DirBuild["Directory.Build.props"]
        DirPackages["Directory.Packages.props"]
    end
    
    subgraph "Documentation"
        Docs["docs/<br/>Git Submodule<br/>kernel-memory-docs"]
    end
    
    subgraph "Excluded (Archived)"
        Archived["archived/<br/>Previous Prototype<br/>Not in Version Control"]
    end
    
    Root --> Service
    Root --> Extensions
    Root --> Infra
    Root --> Sln
    Root --> DirBuild
    Root --> DirPackages
    Root --> Docs
    Root -.->|not tracked| Archived
    
    Service --> Core
    Service --> CoreTests
    
    Extensions --> OpenAI
    Extensions --> Anthropic
    Extensions --> Discord
    Extensions --> ExtTests
    
    Sln --> Core
    Sln --> OpenAI
    Sln --> Anthropic
    Sln --> Discord
    
    DirBuild --> Core
    DirBuild --> OpenAI
    DirPackages --> Core
    DirPackages --> OpenAI
```

Sources: [README.md:9-12](), [.gitmodules:1-4](), [.gitignore:1-2]()

### Key Directories

| Directory | Purpose | Tracked in Git |
|-----------|---------|----------------|
| `service/` | Core services, CLI application, domain logic | ✓ |
| `extensions/` | AI provider integrations (OpenAI, Anthropic, Discord, etc.) | ✓ |
| `tests/` | Unit tests, integration tests, E2E tests | ✓ |
| `infrastructure/` | Build scripts, deployment configurations | ✓ |
| `docs/` | Documentation (separate Git submodule) | ✓ (submodule) |
| `archived/` | Previous prototype codebase | ✗ (excluded) |
| `bin/`, `obj/` | Build outputs | ✗ (excluded) |
| `.vs/`, `.idea/`, `.vscode/` | IDE-specific settings | ✗ (excluded) |

The `archived/` directory contains the previous prototype mentioned in [README.md:9-12]() but is explicitly excluded from version control via [.gitignore:1]().

Sources: [.gitignore:1-73](), [.gitmodules:1-4]()

### Documentation Submodule

Documentation is maintained as a separate Git submodule pointing to the `kernel-memory-docs` repository. This allows independent versioning and contribution workflows for documentation.

**Initializing the documentation submodule:**

```bash
git submodule init
git submodule update
```

Sources: [.gitmodules:1-4]()

---

## Build System

KM² uses modern .NET build practices with centralized configuration to ensure consistency across all projects in the solution.

### Centralized Build Configuration

**Mermaid: Build Configuration Hierarchy**

```mermaid
graph TB
    subgraph "Solution Level"
        Sln["KernelMemory.sln<br/>Master Solution File"]
    end
    
    subgraph "Directory-Level Configuration"
        DirBuild["Directory.Build.props<br/>Shared Build Properties<br/>- Target Framework<br/>- Nullable Reference Types<br/>- Language Version<br/>- Warning Levels"]
        
        DirPkg["Directory.Packages.props<br/>Centralized Package Management<br/>- Package Versions<br/>- Transitive Dependencies<br/>- Version Consistency"]
    end
    
    subgraph "Project Files"
        Core["service/Core/Core.csproj<br/>Imports Directory.Build.props<br/>References packages from Directory.Packages.props"]
        
        Ext1["extensions/OpenAI/OpenAI.csproj<br/>Inherits settings"]
        
        Ext2["extensions/Anthropic/Anthropic.csproj<br/>Inherits settings"]
        
        Test1["tests/Core.UnitTests/Core.UnitTests.csproj<br/>Inherits settings + Test frameworks"]
    end
    
    subgraph "Build Outputs (Ignored)"
        BinObj["bin/, obj/<br/>Intermediate & Output<br/>Per-project directories"]
    end
    
    Sln --> DirBuild
    Sln --> DirPkg
    
    DirBuild --> Core
    DirBuild --> Ext1
    DirBuild --> Ext2
    DirBuild --> Test1
    
    DirPkg --> Core
    DirPkg --> Ext1
    DirPkg --> Ext2
    DirPkg --> Test1
    
    Core --> BinObj
    Ext1 --> BinObj
    Ext2 --> BinObj
    Test1 --> BinObj
```

Sources: [.gitignore:7-41]()

### Directory.Build.props

This file contains shared MSBuild properties inherited by all `.csproj` files in the solution. It typically defines:

- Target framework (e.g., `net8.0`)
- C# language version (C# 12)
- Nullable reference type configuration
- Warning levels and treatment
- Common compiler flags

All projects automatically inherit these settings without explicit configuration in individual project files.

### Directory.Packages.props

This file enables Centralized Package Management (CPM), a .NET feature that centralizes NuGet package version definitions. Benefits include:

- Single source of truth for package versions
- Prevents version conflicts across projects
- Simplifies dependency updates
- Enforces consistent transitive dependency versions

Project files reference packages without specifying versions, which are resolved from `Directory.Packages.props`.

### Build Outputs and Artifacts

The following build artifacts are generated during compilation and explicitly excluded from version control:

**Mermaid: Build Artifact Generation**

```mermaid
graph LR
    subgraph "Source Code"
        Csproj[".csproj Files<br/>Project Definitions"]
    end
    
    subgraph "Build Process"
        Restore["dotnet restore<br/>Download NuGet packages"]
        Compile["dotnet build<br/>Compile C# code"]
        Test["dotnet test<br/>Run test suites"]
    end
    
    subgraph "Artifacts (Excluded from Git)"
        Obj["obj/<br/>Intermediate Files<br/>*.dll (before linking)<br/>*.pdb (debug symbols)<br/>project.assets.json"]
        
        Bin["bin/<br/>Final Outputs<br/>Debug/ or Release/<br/>*.dll, *.exe<br/>*.pdb, *.xml"]
        
        TestResults["TestResult*/<br/>Test execution results<br/>*.trx files"]
        
        Coverage["coverage*.json<br/>coverage*.xml<br/>Code coverage data<br/>DotCover/Coverlet output"]
    end
    
    Csproj --> Restore
    Restore --> Compile
    Compile --> Obj
    Compile --> Bin
    Compile --> Test
    Test --> TestResults
    Test --> Coverage
```

Sources: [.gitignore:7-9, 28-53]()

**Build artifact patterns excluded via .gitignore:**

| Pattern | Purpose |
|---------|---------|
| `bin/`, `obj/` | Compiler intermediate and output files |
| `[Dd]ebug/`, `[Rr]elease/` | Configuration-specific build outputs |
| `[Tt]est[Rr]esult*/` | MSTest execution results |
| `coverage*.json`, `coverage*.xml` | Code coverage reports |
| `*.dotCover` | JetBrains DotCover coverage data |
| `playwright-report/` | Playwright E2E test reports |

Sources: [.gitignore:7-9, 28-56]()

### Building the Solution

**Standard build commands:**

```bash
# Restore NuGet packages
dotnet restore

# Build all projects in Debug configuration
dotnet build

# Build in Release configuration
dotnet build -c Release

# Clean build artifacts
dotnet clean
```

The centralized configuration ensures all projects build consistently with the same settings and package versions.

---

## Testing Infrastructure

KM² employs a comprehensive testing strategy using multiple frameworks to ensure code quality and functionality.

**Mermaid: Testing Framework Architecture**

```mermaid
graph TB
    subgraph "Test Projects"
        UnitTests["tests/Core.UnitTests/<br/>Core.UnitTests.csproj<br/>MSTest Framework"]
        
        IntegTests["tests/Integration.Tests/<br/>Integration.Tests.csproj<br/>MSTest Framework"]
        
        E2ETests["tests/E2E.Tests/<br/>E2E.Tests.csproj<br/>Playwright Framework"]
    end
    
    subgraph "Testing Frameworks"
        MSTest["MSTest<br/>Microsoft.VisualStudio.TestTools.TestingFramework<br/>Unit & Integration Tests"]
        
        Playwright["Playwright<br/>Microsoft.Playwright<br/>Browser Automation & E2E"]
    end
    
    subgraph "Code Coverage Tools"
        Coverlet["Coverlet<br/>coverlet.collector<br/>Cross-platform Coverage"]
        
        DotCover["JetBrains DotCover<br/>*.dotCover<br/>IDE-integrated Coverage"]
    end
    
    subgraph "Test Execution"
        DotnetTest["dotnet test<br/>CLI Test Runner"]
        VSTest["Visual Studio Test Explorer"]
        RiderTest["Rider Test Runner"]
    end
    
    subgraph "Test Artifacts (Ignored)"
        Results["TestResult*/<br/>Test execution logs<br/>*.trx files"]
        
        CoverageData["coverage*.json<br/>coverage*.xml<br/>coverage*.info<br/>*.dotCover"]
        
        PlaywrightReports["playwright-report/<br/>E2E test reports<br/>Screenshots & traces"]
    end
    
    UnitTests --> MSTest
    IntegTests --> MSTest
    E2ETests --> Playwright
    
    MSTest --> Coverlet
    MSTest --> DotCover
    
    DotnetTest --> UnitTests
    DotnetTest --> IntegTests
    DotnetTest --> E2ETests
    
    VSTest --> UnitTests
    RiderTest --> UnitTests
    
    DotnetTest --> Results
    DotnetTest --> CoverageData
    E2ETests --> PlaywrightReports
```

Sources: [.gitignore:43-56]()

### MSTest Framework

MSTest is used for unit and integration tests. Test projects reference the following packages (versions managed via `Directory.Packages.props`):

- `Microsoft.VisualStudio.TestTools.TestingFramework` - Core MSTest framework
- `MSTest.TestAdapter` - Test adapter for test execution
- `MSTest.TestFramework` - Framework utilities

**Running unit tests:**

```bash
# Run all tests
dotnet test

# Run tests with detailed output
dotnet test --logger "console;verbosity=detailed"

# Run tests in a specific project
dotnet test tests/Core.UnitTests/Core.UnitTests.csproj
```

### Playwright Framework

Playwright is used for end-to-end testing, particularly for scenarios involving browser automation or complex interaction flows.

**Playwright test artifacts:**

The `playwright-report/` directory contains test execution reports, including screenshots, traces, and video recordings. These artifacts are excluded from version control via [.gitignore:56]().

Sources: [.gitignore:55-56]()

### Code Coverage

Two code coverage tools are supported:

**Coverlet (Cross-platform):**
- NuGet package: `coverlet.collector`
- Outputs: `coverage*.json`, `coverage*.xml`, `coverage*.info`
- Formats: Cobertura XML, JSON, LCOV

**JetBrains DotCover (IDE-integrated):**
- IDE: JetBrains Rider
- Outputs: `*.dotCover`
- Format: Proprietary binary

**Generating coverage reports:**

```bash
# Generate coverage with Coverlet (Cobertura format)
dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage

# Coverage files are generated in ./coverage directory
# Excluded from Git via .gitignore patterns
```

All coverage output files are excluded from version control via [.gitignore:47-53]().

Sources: [.gitignore:47-53]()

### Test Result Artifacts

Test execution generates the following artifacts:

| Pattern | Purpose | Excluded |
|---------|---------|----------|
| `TestResult*/` | MSTest execution logs and results | ✓ |
| `*.trx` | Visual Studio Test Results format | ✓ |
| `[Bb]uild[Ll]og.*` | Build logs during test runs | ✓ |
| `playwright-report/` | Playwright E2E test reports | ✓ |

All test artifacts are excluded from version control to prevent repository bloat.

Sources: [.gitignore:43-56]()

---

## IDE Setup and Development Environment

KM² maintains IDE-agnostic build configuration, allowing developers to use their preferred development environment. All IDE-specific settings are excluded from version control.

**Mermaid: IDE Support and Configuration**

```mermaid
graph TB
    subgraph "Repository (IDE-Agnostic)"
        Solution["KernelMemory.sln<br/>Standard .NET Solution"]
        DirBuild["Directory.Build.props<br/>Shared Build Config"]
        GitIgnore[".gitignore<br/>Excludes IDE Files"]
    end
    
    subgraph "Visual Studio"
        VS[".vs/<br/>VS-specific settings<br/>*.suo, *.user<br/>NOT IN GIT"]
        VSSettings["Solution Settings<br/>Startup projects<br/>Debugger config"]
    end
    
    subgraph "JetBrains Rider"
        Rider[".idea/<br/>Rider-specific settings<br/>workspace.xml<br/>NOT IN GIT"]
        RiderSettings["Run Configurations<br/>Code style<br/>Inspections"]
    end
    
    subgraph "Visual Studio Code"
        VSCode[".vscode/<br/>VS Code settings<br/>launch.json, tasks.json<br/>NOT IN GIT"]
        VSCodeExt["Extensions<br/>C# Extension<br/>Debugger"]
    end
    
    subgraph "Developer Workflow"
        Dev["Developer"]
        Git["Git Repository<br/>Shared Source"]
        LocalConfig["Local Configuration<br/>Not committed"]
    end
    
    Solution --> VS
    Solution --> Rider
    Solution --> VSCode
    
    DirBuild --> VS
    DirBuild --> Rider
    DirBuild --> VSCode
    
    GitIgnore -.->|excludes| VS
    GitIgnore -.->|excludes| Rider
    GitIgnore -.->|excludes| VSCode
    
    Dev --> VS
    Dev --> Rider
    Dev --> VSCode
    Dev --> Git
    Dev --> LocalConfig
    
    LocalConfig -.->|not in| Git
```

Sources: [.gitignore:3-5, 12-16]()

### Excluded IDE Files

The following IDE-specific files and directories are excluded from version control:

| Pattern | IDE | Purpose |
|---------|-----|---------|
| `.vs/` | Visual Studio | Solution user options, cache |
| `.idea/` | JetBrains Rider | Workspace settings, cache |
| `.vscode/` | Visual Studio Code | Launch configurations, settings |
| `*.user` | Visual Studio | User-specific project settings |
| `.DS_Store` | macOS Finder | macOS directory metadata |

Sources: [.gitignore:3-5, 12, 15]()

### Visual Studio Setup

**Requirements:**
- Visual Studio 2022 (version 17.8 or later)
- Workload: .NET desktop development
- Workload: ASP.NET and web development (for web components)

**First-time setup:**
1. Open `KernelMemory.sln`
2. Visual Studio automatically creates `.vs/` directory (ignored by Git)
3. Restore NuGet packages (automatic on first build)
4. Set startup project to desired CLI or service project

**Visual Studio-specific features:**
- Test Explorer integration for MSTest
- Built-in code coverage via Enterprise edition
- Solution-wide search and refactoring

### JetBrains Rider Setup

**Requirements:**
- JetBrains Rider 2023.3 or later
- .NET SDK detected automatically

**First-time setup:**
1. Open `KernelMemory.sln`
2. Rider automatically creates `.idea/` directory (ignored by Git)
3. Restore NuGet packages (automatic)
4. Configure run configurations for CLI projects

**Rider-specific features:**
- DotCover code coverage integration
- Advanced code inspections and quick-fixes
- Built-in decompiler for dependencies

### Visual Studio Code Setup

**Requirements:**
- Visual Studio Code 1.85 or later
- Extensions:
  - C# (ms-dotnettools.csharp)
  - C# Dev Kit (ms-dotnettools.csdevkit) - optional

**First-time setup:**
1. Open repository root folder in VS Code
2. Install recommended C# extension
3. VS Code creates `.vscode/` directory for settings (ignored by Git)
4. Use integrated terminal for `dotnet` commands

**VS Code workflow:**
```bash
# Build from integrated terminal
dotnet build

# Run tests
dotnet test

# Run CLI application
dotnet run --project service/Core/Core.csproj
```

VS Code is lightweight but requires more manual configuration compared to full IDEs.

Sources: [.gitignore:3-5, 12-16]()

---

## Configuration File Management

Development configuration files containing sensitive data or environment-specific settings are excluded from version control.

**Mermaid: Configuration File Patterns**

```mermaid
graph TB
    subgraph "Version Controlled"
        BaseConfig["config.json<br/>appsettings.json<br/>Base Configuration<br/>COMMITTED"]
        
        Example["config.example.json<br/>Template Files<br/>COMMITTED"]
    end
    
    subgraph "Excluded (Local Only)"
        DevConfig["*.development.json<br/>*.development.config<br/>config.development.yaml<br/>NOT IN GIT"]
        
        EnvFiles[".env<br/>Environment Variables<br/>Secrets & API Keys<br/>NOT IN GIT"]
        
        AppSettings["appsettings.*.json<br/>appsettings.Development.json<br/>Environment-specific<br/>NOT IN GIT"]
    end
    
    subgraph "Sensitive Files"
        Certs["*.cer, *.crt<br/>*.key, *.pem<br/>certs/<br/>SSL Certificates<br/>NOT IN GIT"]
    end
    
    Developer["Developer"]
    
    BaseConfig -.->|template for| DevConfig
    Example -.->|copy to create| DevConfig
    
    Developer --> DevConfig
    Developer --> EnvFiles
    Developer --> AppSettings
    Developer --> Certs
    
    GitIgnore[".gitignore"]
    GitIgnore -.->|excludes| DevConfig
    GitIgnore -.->|excludes| EnvFiles
    GitIgnore -.->|excludes| AppSettings
    GitIgnore -.->|excludes| Certs
```

Sources: [.gitignore:19-26, 68-72]()

### Excluded Configuration Patterns

| Pattern | Purpose | Example |
|---------|---------|---------|
| `.env` | Environment variables, API keys | Database connection strings |
| `*.development.*` | Development environment config | Local node configurations |
| `*.development.json*` | JSON development config | API keys for local testing |
| `config.development.yaml` | YAML development config | Custom service endpoints |
| `appsettings.*.json` | ASP.NET environment settings | Logging levels, connection strings |

These patterns ensure that sensitive configuration (API keys, connection strings, credentials) never gets committed to the repository.

Sources: [.gitignore:19-26]()

### Certificate and Key Files

SSL/TLS certificates and private keys are excluded from version control:

```
*.cer      # Certificate files
*.crt      # Certificate files (alternative extension)
*.key      # Private key files
*.pem      # Privacy-enhanced mail (certificate/key format)
certs/     # Certificate directory
```

Developers must maintain these files locally and ensure they are never committed.

Sources: [.gitignore:68-72]()

---

## Additional Development Files

### Temporary and Build Files

The following patterns exclude temporary files generated during development:

| Pattern | Purpose |
|---------|---------|
| `*.tmp` | Temporary files |
| `*.log` | Log files |
| `*.bck` | Backup files |
| `*.orig` | Merge conflict originals |
| `*.devis`, `*.devis.*` | Development/testing artifacts |

Sources: [.gitignore:13-16, 62-64]()

### Node.js and Python Artifacts

For Python and Node.js components:

| Pattern | Language | Purpose |
|---------|----------|---------|
| `node_modules/` | Node.js | NPM package installations |
| `__pycache__/` | Python | Compiled Python bytecode |

These are regenerated via `npm install` or Python's import system and should never be committed.

Sources: [.gitignore:6, 9]()

### Custom Development Directories

| Pattern | Purpose |
|---------|---------|
| `_dev/` | Custom development workspace |
| `.dev/` | Alternative development workspace |

These directories provide personal workspace for developers without cluttering the repository structure.

Sources: [.gitignore:10-11]()

---

## Version Control Best Practices

### Submodule Management

The `docs/` directory is a Git submodule. When working with submodules:

```bash
# Clone repository with submodules
git clone --recursive https://github.com/microsoft/kernel-memory

# Update submodules to latest
git submodule update --remote

# Commit submodule reference changes
git add docs
git commit -m "Update documentation submodule"
```

Sources: [.gitmodules:1-4]()

### Ignored Archive Content

The `archived/` directory contains the previous prototype codebase but is not tracked in Git ([.gitignore:1]()). This content exists in the repository for reference purposes but does not participate in version control. Any changes to archived content will not be detected by Git.

Sources: [.gitignore:1](), [README.md:9-12]()

### Amplifier and Claude Integration Directories

The following directories are excluded and may contain AI-assisted development artifacts:

```
.amplifier/     # Amplifier platform artifacts
.claude/        # Claude AI integration artifacts
```

These directories may contain metadata, context, or artifacts related to the metacognitive AI engineering approach described in [Relationship to Amplifier](#1.2).

Sources: [.gitignore:2-3]()

---

## Summary

The KM² development environment emphasizes:

1. **Centralized Configuration**: `Directory.Build.props` and `Directory.Packages.props` ensure consistent builds
2. **IDE Independence**: All major IDEs supported; IDE-specific files excluded from Git
3. **Comprehensive Testing**: MSTest for unit/integration tests, Playwright for E2E tests, multiple coverage tools
4. **Security-First**: All sensitive configuration, certificates, and credentials excluded from version control
5. **Clean Repository**: Build artifacts, test results, and temporary files never committed

For specific subsystem details:
- Repository structure: [Repository Structure](#9.1)
- Build system: [Build System](#9.2)
- Testing: [Testing Infrastructure](#9.3)
- IDE setup: [IDE Setup and Development Environment](#9.4)

Sources: [README.md:1-80](), [.gitignore:1-73](), [.gitmodules:1-4]()

---

