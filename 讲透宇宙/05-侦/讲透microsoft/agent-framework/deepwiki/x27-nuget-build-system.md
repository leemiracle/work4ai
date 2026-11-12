<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/agent-framework · extra page NuGet Build System · fetched 2026-10-26 -->

# NuGet Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dotnet/eng/MSBuild/Shared.props](dotnet/eng/MSBuild/Shared.props)
- [dotnet/nuget/nuget-package.props](dotnet/nuget/nuget-package.props)
- [dotnet/samples/04-hosting/FoundryHostedAgents/responses/Hosted-Steering/HostedSteering.csproj](dotnet/samples/04-hosting/FoundryHostedAgents/responses/Hosted-Steering/HostedSteering.csproj)
- [dotnet/samples/04-hosting/FoundryHostedAgents/responses/Hosted-Workflow-Resilient/HostedWorkflowResilient.csproj](dotnet/samples/04-hosting/FoundryHostedAgents/responses/Hosted-Workflow-Resilient/HostedWorkflowResilient.csproj)
- [dotnet/src/Microsoft.Agents.AI.Abstractions/Microsoft.Agents.AI.Abstractions.csproj](dotnet/src/Microsoft.Agents.AI.Abstractions/Microsoft.Agents.AI.Abstractions.csproj)
- [dotnet/src/Microsoft.Agents.AI.Foundry/ClientHeaderValidation.cs](dotnet/src/Microsoft.Agents.AI.Foundry/ClientHeaderValidation.cs)
- [dotnet/src/Microsoft.Agents.AI.Foundry/FoundryAgentSessionExtensions.cs](dotnet/src/Microsoft.Agents.AI.Foundry/FoundryAgentSessionExtensions.cs)
- [dotnet/src/Microsoft.Agents.AI.Foundry/Microsoft.Agents.AI.Foundry.csproj](dotnet/src/Microsoft.Agents.AI.Foundry/Microsoft.Agents.AI.Foundry.csproj)
- [dotnet/src/Microsoft.Agents.AI.Foundry/UserIdentityPolicy.cs](dotnet/src/Microsoft.Agents.AI.Foundry/UserIdentityPolicy.cs)
- [dotnet/src/Microsoft.Agents.AI.OpenAI/Microsoft.Agents.AI.OpenAI.csproj](dotnet/src/Microsoft.Agents.AI.OpenAI/Microsoft.Agents.AI.OpenAI.csproj)
- [dotnet/src/Microsoft.Agents.AI.Workflows.Declarative/DefaultHttpRequestHandler.cs](dotnet/src/Microsoft.Agents.AI.Workflows.Declarative/DefaultHttpRequestHandler.cs)
- [dotnet/src/Microsoft.Agents.AI.Workflows.Declarative/Microsoft.Agents.AI.Workflows.Declarative.csproj](dotnet/src/Microsoft.Agents.AI.Workflows.Declarative/Microsoft.Agents.AI.Workflows.Declarative.csproj)
- [dotnet/src/Microsoft.Agents.AI.Workflows.Generators/Microsoft.Agents.AI.Workflows.Generators.csproj](dotnet/src/Microsoft.Agents.AI.Workflows.Generators/Microsoft.Agents.AI.Workflows.Generators.csproj)
- [dotnet/src/Microsoft.Agents.AI.Workflows/Microsoft.Agents.AI.Workflows.csproj](dotnet/src/Microsoft.Agents.AI.Workflows/Microsoft.Agents.AI.Workflows.csproj)
- [dotnet/src/Microsoft.Agents.AI/Microsoft.Agents.AI.csproj](dotnet/src/Microsoft.Agents.AI/Microsoft.Agents.AI.csproj)
- [dotnet/src/Shared/Http/HttpHeaderValidation.cs](dotnet/src/Shared/Http/HttpHeaderValidation.cs)
- [dotnet/tests/Microsoft.Agents.AI.Foundry.UnitTests/FoundryHostedRequestTests.cs](dotnet/tests/Microsoft.Agents.AI.Foundry.UnitTests/FoundryHostedRequestTests.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/Microsoft.Agents.AI.UnitTests.csproj](dotnet/tests/Microsoft.Agents.AI.UnitTests/Microsoft.Agents.AI.UnitTests.csproj)
- [dotnet/tests/Microsoft.Agents.AI.Workflows.Declarative.UnitTests/DefaultHttpRequestHandlerTests.cs](dotnet/tests/Microsoft.Agents.AI.Workflows.Declarative.UnitTests/DefaultHttpRequestHandlerTests.cs)

</details>



This document describes the NuGet build and packaging system for the .NET implementation of the Microsoft Agent Framework. It covers versioning strategy, package metadata configuration, validation, auditing, and release automation within the CI/CD pipeline.

The NuGet build system provides centralized configuration for all .NET packages, ensuring consistency across the core library, abstractions, and provider integrations while allowing individual projects to customize titles and descriptions.

## Build System Architecture

The NuGet build system uses a hub-and-spoke pattern where all projects import shared configuration from a central `nuget-package.props` file located at `dotnet/nuget/nuget-package.props`.

```mermaid
graph TB
    subgraph "Central Configuration Space"
        [NugetProps] --> ["nuget-package.props<br/>VersionPrefix: 1.24.0<br/>Metadata, Validation, Auditing"]
    end
    
    subgraph "Code Entity Space Projects"
        [Abstractions] --> ["Microsoft.Agents.AI.Abstractions.csproj<br/>Import nuget-package.props"]
        [CoreProj] --> ["Microsoft.Agents.AI.csproj<br/>Import nuget-package.props"]
        [WorkflowsProj] --> ["Microsoft.Agents.AI.Workflows.csproj<br/>Import nuget-package.props"]
        [DeclarativeProj] --> ["Microsoft.Agents.AI.Workflows.Declarative.csproj<br/>Import nuget-package.props"]
    end
    
    [NugetProps] --> [Abstractions]
    [NugetProps] --> [CoreProj]
    [NugetProps] --> [WorkflowsProj]
    [NugetProps] --> [DeclarativeProj]
    
    [Abstractions] -.-> [AbstractionsNuget]
    [AbstractionsNuget] --> ["Microsoft.Agents.AI.Abstractions.nupkg"]
    [CoreProj] -.-> [CoreNuget]
    [CoreNuget] --> ["Microsoft.Agents.AI.nupkg"]
    [WorkflowsProj] -.-> [WorkflowsNuget]
    [WorkflowsNuget] --> ["Microsoft.Agents.AI.Workflows.nupkg"]
    [DeclarativeProj] -.-> [DeclarativeNuget]
    [DeclarativeNuget] --> ["Microsoft.Agents.AI.Workflows.Declarative.nupkg"]
```

**Diagram: NuGet Build System Architecture**

Sources: [dotnet/nuget/nuget-package.props:1-93](), [dotnet/src/Microsoft.Agents.AI.Abstractions/Microsoft.Agents.AI.Abstractions.csproj:1-22](), [dotnet/src/Microsoft.Agents.AI/Microsoft.Agents.AI.csproj:1-19](), [dotnet/src/Microsoft.Agents.AI.Workflows/Microsoft.Agents.AI.Workflows.csproj:1-17](), [dotnet/src/Microsoft.Agents.AI.Workflows.Declarative/Microsoft.Agents.AI.Workflows.Declarative.csproj:1-16]()

## Versioning Strategy

The framework uses a centralized versioning approach that distinguishes between Release Candidates (RC), previews, and stable releases. Versioning logic is primarily defined in `dotnet/nuget/nuget-package.props`.

### Version Components

| Component | Value | Source | Purpose |
|-----------|-------|--------|---------|
| `VersionPrefix` | `1.24.0` | [dotnet/nuget/nuget-package.props:4]() | Semantic version base |
| `RCNumber` | `1` | [dotnet/nuget/nuget-package.props:5]() | Current Release Candidate index |
| `DateSuffix` | `261006` | [dotnet/nuget/nuget-package.props:6]() | Datestamp for non-RC builds |
| `IsReleased` | `true/false` | [dotnet/src/Microsoft.Agents.AI/Microsoft.Agents.AI.csproj:4]() | Project-level flag for GA status |

### Version Determination Logic

The version string is constructed based on the build context using MSBuild conditional properties:

1. **Release Candidate**: If `IsReleaseCandidate` is `true`, the version is `$(VersionPrefix)-rc$(RCNumber)` (e.g., `1.24.0-rc1`). [dotnet/nuget/nuget-package.props:7]()
2. **Preview (Custom)**: If not RC and a `VersionSuffix` is provided, it uses: `$(VersionPrefix)-$(VersionSuffix).$(DateSuffix).1`. [dotnet/nuget/nuget-package.props:8]()
3. **Preview (Default)**: If no suffix is provided, it defaults to `$(VersionPrefix)-preview.$(DateSuffix).1`. [dotnet/nuget/nuget-package.props:9]()
4. **Stable (GA)**: If `IsReleased` is `true`, the version is exactly `$(VersionPrefix)`. [dotnet/nuget/nuget-package.props:10]()

Sources: [dotnet/nuget/nuget-package.props:3-10](), [dotnet/src/Microsoft.Agents.AI/Microsoft.Agents.AI.csproj:4-4](), [dotnet/src/Microsoft.Agents.AI.Workflows/Microsoft.Agents.AI.Workflows.csproj:4-4]()

## Package Metadata and Assets

Standardized metadata is defined in the central props file to ensure all framework packages present a unified identity on NuGet.org.

### Central Metadata

| Property | Value | Source |
|----------|-------|--------|
| `Authors` | Microsoft | [dotnet/nuget/nuget-package.props:34]() |
| `Company` | Microsoft | [dotnet/nuget/nuget-package.props:35]() |
| `Product` | Microsoft Agent Framework | [dotnet/nuget/nuget-package.props:36]() |
| `PackageLicenseExpression` | MIT | [dotnet/nuget/nuget-package.props:42]() |
| `RepositoryUrl` | https://github.com/microsoft/agent-framework | [dotnet/nuget/nuget-package.props:45]() |

### Shared Assets
Every package includes a standard icon and README file located in the `dotnet/nuget` directory. These are linked into each project during the pack process via `None` items with `Pack="true"`. [dotnet/nuget/nuget-package.props:48-52](), [dotnet/nuget/nuget-package.props:84-88]()

Sources: [dotnet/nuget/nuget-package.props:33-52](), [dotnet/nuget/nuget-package.props:84-88]()

## Package Validation and Auditing

The build system implements package validation to prevent accidental breaking changes and security auditing to protect the supply chain.

### Validation Rules
- **Baseline Version**: Standard packages are validated against a baseline (e.g., `1.0.0` or specific RC baselines like `1.8.0-rc1` for declarative workflows). [dotnet/nuget/nuget-package.props:15](), [dotnet/src/Microsoft.Agents.AI.Workflows.Declarative/Microsoft.Agents.AI.Workflows.Declarative.csproj:22-24]()
- **Enforcement**: Validation is enabled when `IsReleased` is `true`. [dotnet/nuget/nuget-package.props:17]()
- **Suppressions**: Attribute validation (`CP0003`) is only enforced for `Publish` configurations [dotnet/nuget/nuget-package.props:18-19](). Reference assembly validation (`CP1002`) is disabled globally [dotnet/nuget/nuget-package.props:20-21]().

### Security Auditing
NuGet auditing is enforced for all direct and transitive dependencies during the build process.

| Setting | Value | Description |
|---------|-------|-------------|
| `NuGetAudit` | `true` | Enables security auditing. [dotnet/nuget/nuget-package.props:24]() |
| `NuGetAuditMode` | `all` | Audits both direct and transitive packages. [dotnet/nuget/nuget-package.props:27]() |
| `NuGetAuditLevel`| `low` | Reports all advisories from low to critical. [dotnet/nuget/nuget-package.props:30]() |

Sources: [dotnet/nuget/nuget-package.props:14-31](), [dotnet/src/Microsoft.Agents.AI/Microsoft.Agents.AI.csproj:4-6](), [dotnet/src/Microsoft.Agents.AI.Workflows.Declarative/Microsoft.Agents.AI.Workflows.Declarative.csproj:22-24]()

## Release Automation and CI Integration

The release process integrates with MSBuild properties and script automation to build, test, and verify package outputs.

```mermaid
graph TD
    subgraph "CI Build and Package Flow"
        [BuildJob] --> ["dotnet build -c Release"]
        [PackJob] --> ["dotnet pack --output artifacts"]
        [InstallCheck] --> ["ValidateNoUnshippedPublicApis<br/>dotnet/nuget/nuget-package.props:80-82"]
    end

    subgraph "MSBuild Task Space"
        [BuildJob] --> [PackJob]
        [PackJob] --> [InstallCheck]
    end
```

**Diagram: CI/CD Package Validation Flow**

### Public API Validation
Projects flagged with `<IsReleased>true</IsReleased>` execute strict validation against shipped public APIs via custom MSBuild targets. The target `ValidateNoUnshippedPublicApis` executes before the `Pack` target when configuration is set to `Publish`, executing `test-unshipped-public-apis.ps1`. [dotnet/nuget/nuget-package.props:80-82]()

Sources: [dotnet/nuget/nuget-package.props:80-82](), [dotnet/src/Microsoft.Agents.AI/Microsoft.Agents.AI.csproj:4-4]()

## Symbol Packages and Source Link

To facilitate debugging for framework consumers, the build system generates symbol packages and integrates with GitHub Source Link.

- **Source Link**: The `Microsoft.SourceLink.GitHub` package is included in all projects to map compiled code back to the GitHub source repository. [dotnet/nuget/nuget-package.props:64]()
- **Symbols**: `IncludeSymbols` is set to `true` with the format set to `snupkg`. [dotnet/nuget/nuget-package.props:54-55]()
- **Documentation**: XML documentation files are generated at `bin\$(Configuration)\$(TargetFramework)\$(AssemblyName).xml` and included in the package to provide IntelliSense. [dotnet/nuget/nuget-package.props:58]()

Sources: [dotnet/nuget/nuget-package.props:53-64]()

---

