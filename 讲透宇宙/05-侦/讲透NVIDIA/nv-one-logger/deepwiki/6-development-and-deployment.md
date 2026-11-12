<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nv-one-logger · page 6 Development and Deployment · fetched 2026-10-26 -->

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This page documents the development practices, CI/CD pipelines, and deployment procedures for the nv-one-logger monorepo. It covers the monorepo structure, build processes, dependency management, and deployment workflows used to maintain and distribute the five independent packages within the repository.

For information about the overall system architecture and package relationships, see [Overview](#1). For details about CI/CD pipeline configuration, see [CI/CD Pipeline](#6.1). For dependency management specifics, see [Dependencies and Configuration](#6.2).

## Monorepo Development Structure

The nv-one-logger repository is organized as a monorepo containing five independent packages, each with its own development lifecycle while sharing common development practices and tooling.

### Repository Organization

```mermaid
graph TB
    subgraph "nv-one-logger monorepo"
        subgraph "Core Foundation"
            CoreProject["one_logger_core/<br/>pyproject.toml<br/>Makefile<br/>src/nv_one_logger/"]
        end
        
        subgraph "Domain Packages" 
            TrainingProject["one_logger_training_telemetry/<br/>pyproject.toml<br/>Makefile<br/>src/nv_one_logger/training_telemetry/"]
        end
        
        subgraph "Backend Integration Packages"
            OTELProject["one_logger_otel/<br/>pyproject.toml<br/>Makefile<br/>src/nv_one_logger/otel/"]
            WandBProject["one_logger_wandb/<br/>pyproject.toml<br/>Makefile<br/>src/nv_one_logger/wandb/"]
        end
        
        subgraph "Application Integration Packages"
            PTLProject["one_logger_pytorch_lightning_integration/<br/>pyproject.toml<br/>Makefile<br/>src/nv_one_logger/training_telemetry/integration/"]
        end
        
        subgraph "Repository Root"
            RootFiles["README.md<br/>third_party_licenses/<br/>.gitlab-ci.yml"]
        end
    end
    
    RootFiles -.-> CoreProject
    RootFiles -.-> TrainingProject  
    RootFiles -.-> OTELProject
    RootFiles -.-> WandBProject
    RootFiles -.-> PTLProject
```

Each package follows a consistent structure with standardized tooling and configuration files that enable independent development and deployment.

**Sources**: [README.md:1-106]()

### Package Independence and Shared Practices

```mermaid
graph LR
    subgraph "Shared Development Infrastructure"
        GitLabCI[".gitlab-ci.yml<br/>Shared CI templates"]
        DevGuidance["confluence.nvidia.com<br/>Dev guidance documentation"]
    end
    
    subgraph "Individual Package Components"
        subgraph "Package Structure Template"
            PyProject["pyproject.toml<br/>Poetry configuration<br/>Dependencies<br/>Build settings"]
            Makefile["Makefile<br/>lint, format, test<br/>publish commands"]
            SrcDir["src/<br/>Source code under<br/>nv_one_logger namespace"]
            TestsDir["tests/<br/>Unit and integration tests"]
        end
    end
    
    subgraph "Independent Capabilities"  
        CIRules["Independent CI/CD rules"]
        Publishing["Separate package publishing"]
        Dependencies["Narrow, specific dependencies"]
    end
    
    GitLabCI --> PyProject
    GitLabCI --> Makefile
    PyProject --> CIRules
    Makefile --> Publishing
    SrcDir --> Dependencies
```

This structure allows narrow dependencies while making development and code review easier by keeping everything in one repository.

**Sources**: [README.md:5-8](), [README.md:52-60]()

## CI/CD Pipeline Architecture

The monorepo uses GitLab CI/CD with a multi-stage pipeline that builds and deploys each package independently while sharing common infrastructure and templates.

### Pipeline Stage Structure

```mermaid
graph TD
    subgraph "GitLab CI Pipeline Stages"
        TestStage["test stage<br/>Linting, unit tests<br/>Code quality checks"]
        BuildDeployStage["build_deploy stage<br/>Package building<br/>Artifact publishing"]
    end
    
    subgraph "Package-Specific Jobs"
        subgraph "Core Package Jobs"
            CoreTest["core-unit-tests"]
            CoreBuildStaging["core-build-staging-job"]  
            CoreBuildProd["core-build-production-job"]
        end
        
        subgraph "Training Telemetry Jobs"
            TelemetryTest["telemetry-unit-tests"]
            TelemetryBuildStaging["telemetry-build-staging-job"]
            TelemetryBuildProd["telemetry-build-production-job"]
        end
        
        subgraph "OTEL Integration Jobs"
            OTELTest["otel-unit-tests"] 
            OTELBuildStaging["otel-build-staging-job"]
            OTELBuildProd["otel-build-production-job"]
        end
        
        subgraph "PyTorch Lightning Jobs"
            PTLTest["ptl-int-unit-tests"]
            PTLBuildStaging["ptl-int-build-staging-job"]
            PTLBuildProd["ptl-int-build-production-job"]
        end
    end
    
    TestStage --> BuildDeployStage
    BuildDeployStage --> CoreTest
    BuildDeployStage --> TelemetryTest
    BuildDeployStage --> OTELTest  
    BuildDeployStage --> PTLTest
    
    CoreTest --> CoreBuildStaging
    CoreTest --> CoreBuildProd
    TelemetryTest --> TelemetryBuildStaging
    TelemetryTest --> TelemetryBuildProd
    OTELTest --> OTELBuildStaging
    OTELTest --> OTELBuildProd
    PTLTest --> PTLBuildStaging
    PTLTest --> PTLBuildProd
```

Each package maintains independent test and build jobs while sharing the overall pipeline structure and deployment targets.

**Sources**: GitLab CI configuration (referenced in high-level diagrams)

### Deployment Flow and Artifact Management

```mermaid
graph TB
    subgraph "Source Branches"
        DevelopBranch["develop branch<br/>Automatic builds"]
        MainBranch["main branch<br/>Manual approval required"]
    end
    
    subgraph "Build Outputs"  
        PackageArtifacts["Python Packages<br/>wheel and sdist files<br/>Built via Poetry"]
    end
    
    subgraph "Artifactory Repositories"
        StagingRepo["hwinf-mlwfo-staging-pypi<br/>Development artifacts<br/>Automatic deployment"]
        ProductionRepo["hwinf-mlwfo-pypi<br/>Production artifacts<br/>Manual approval"]  
    end
    
    DevelopBranch --> PackageArtifacts
    MainBranch --> PackageArtifacts
    
    PackageArtifacts -->|automatic| StagingRepo
    PackageArtifacts -->|manual approval| ProductionRepo
    
    StagingRepo -.->|testing and validation| ProductionRepo
```

The deployment process uses different repositories for staging and production environments, with automatic deployment to staging and manual approval for production releases.

**Sources**: GitLab CI configuration (referenced in high-level diagrams)

## Build and Development Process

Each package uses standardized build tooling and development workflows based on Poetry and Make automation.

### Package Build Configuration

| Component | Purpose | Configuration File |
|-----------|---------|-------------------|
| Poetry | Dependency management, packaging | `pyproject.toml` |
| Make | Development automation | `Makefile` |
| Testing | Unit and integration tests | `tests/` directory |
| Linting | Code quality, formatting | Poetry dev dependencies |

### Development Automation

```mermaid
graph LR
    subgraph "Development Commands"
        LintCmd["make lint<br/>Code quality checks<br/>Format validation"]
        TestCmd["make test<br/>Unit test execution<br/>Coverage reporting"] 
        FormatCmd["make format<br/>Code formatting<br/>Import sorting"]
        PublishCmd["make publish<br/>Package building<br/>Artifact upload"]
    end
    
    subgraph "Poetry Integration"
        PoetryInstall["poetry install<br/>Dependency resolution<br/>Virtual environment"]
        PoetryBuild["poetry build<br/>wheel and sdist<br/>Package creation"]
        PoetryPublish["poetry publish<br/>Repository upload<br/>Artifact distribution"]
    end
    
    LintCmd --> PoetryInstall
    TestCmd --> PoetryInstall  
    FormatCmd --> PoetryInstall
    PublishCmd --> PoetryBuild
    PublishCmd --> PoetryPublish
```

All packages share this consistent development workflow through standardized `Makefile` automation and `pyproject.toml` configuration.

**Sources**: [README.md:59]()

### Namespace and Source Organization

```mermaid
graph TD
    subgraph "nv_one_logger Namespace"
        subgraph "Core Package"
            CoreSrc["src/nv_one_logger/<br/>api/, core/, exporter/, recorder/"]
        end
        
        subgraph "Training Telemetry Package" 
            TrainingSrc["src/nv_one_logger/training_telemetry/<br/>api/, docs/"]
        end
        
        subgraph "Backend Integrations"
            OTELSrc["src/nv_one_logger/otel/<br/>exporter/"]
            WandBSrc["src/nv_one_logger/wandb/<br/>exporter/"]
        end
        
        subgraph "Application Integration"
            PTLSrc["src/nv_one_logger/training_telemetry/<br/>integration/"]
        end
    end
    
    CoreSrc -.->|provides base classes| OTELSrc
    CoreSrc -.->|provides base classes| WandBSrc
    TrainingSrc -.->|extends for ML| PTLSrc
```

All packages share the `nv_one_logger` namespace while maintaining separate source directories and independent functionality.

**Sources**: [README.md:14-46](), [README.md:55]()

## Development Workflow

The monorepo supports both individual package development and cross-package integration through its shared structure and independent deployment capabilities.

### Package Development Lifecycle

```mermaid
graph TB
    subgraph "Local Development"
        LocalSetup["poetry install<br/>Environment setup<br/>Dependency resolution"]
        LocalTest["make test<br/>Unit test execution<br/>Local validation"] 
        LocalLint["make lint<br/>Code quality checks<br/>Format validation"]
    end
    
    subgraph "Version Control"
        CommitChanges["git commit<br/>Change submission<br/>Code review"]
        BranchStrategy["develop → main<br/>Branch-based workflow<br/>Merge approval"]
    end
    
    subgraph "CI/CD Integration"
        AutoTest["Automatic testing<br/>CI pipeline execution<br/>Quality gates"]
        AutoBuild["Package building<br/>Artifact creation<br/>Repository upload"]
    end
    
    LocalSetup --> LocalTest
    LocalTest --> LocalLint
    LocalLint --> CommitChanges
    CommitChanges --> BranchStrategy
    BranchStrategy --> AutoTest
    AutoTest --> AutoBuild
```

This workflow ensures code quality and package integrity while maintaining independent development cycles for each component.

**Sources**: [README.md:103-105]()

---

