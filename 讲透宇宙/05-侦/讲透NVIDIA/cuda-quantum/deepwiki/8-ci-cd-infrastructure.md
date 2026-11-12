<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuda-quantum · page 8 CI/CD Infrastructure · fetched 2026-10-26 -->

# CI/CD System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/clean_up.yml](.github/workflows/clean_up.yml)
- [.github/workflows/create_cache_command.yml](.github/workflows/create_cache_command.yml)
- [.github/workflows/deployments.yml](.github/workflows/deployments.yml)
- [.github/workflows/dev_environment.yml](.github/workflows/dev_environment.yml)
- [.github/workflows/docker_images.yml](.github/workflows/docker_images.yml)
- [.github/workflows/documentation.yml](.github/workflows/documentation.yml)
- [.github/workflows/generate_cc.yml](.github/workflows/generate_cc.yml)
- [.github/workflows/gh_registry.yml](.github/workflows/gh_registry.yml)
- [.github/workflows/integration_tests.yml](.github/workflows/integration_tests.yml)
- [.github/workflows/prebuilt_binaries.yml](.github/workflows/prebuilt_binaries.yml)
- [.github/workflows/prepare_deployment.yml](.github/workflows/prepare_deployment.yml)
- [.github/workflows/publishing.yml](.github/workflows/publishing.yml)
- [.github/workflows/publishing_stable.yml](.github/workflows/publishing_stable.yml)
- [.github/workflows/python_wheels.yml](.github/workflows/python_wheels.yml)
- [.github/workflows/test_in_devenv.yml](.github/workflows/test_in_devenv.yml)
- [runtime/cudaq/remote_capabilities.h](runtime/cudaq/remote_capabilities.h)

</details>



This document outlines the Continuous Integration/Continuous Deployment (CI/CD) system used in the CUDA Quantum project. The CI/CD system automates building, testing, packaging, and releasing the codebase across multiple platforms and architectures (amd64/arm64). It includes workflows for validating code changes, generating artifacts (Docker images, Python wheels, installers), deploying to registries, and running integration tests with quantum hardware providers.

For information about building and installing CUDA-Q locally, see [Building and Installing](#8). For detailed information about the testing infrastructure, see [Testing Infrastructure](#9.1). For the release process, see [Release Process](#9.2).

## CI/CD System Architecture

The following diagram illustrates the high-level architecture of the CUDA Quantum CI/CD system:

```mermaid
flowchart TD
    subgraph "Triggering Events"
        PREvent["Pull Request"]
        Commit["Commit to Main/Release Branch"]
        Manual["Manual Trigger"]
        Schedule["Scheduled Event"]
    end

    subgraph "Primary Workflows"
        CI["ci.yml"]
        Deployments["deployments.yml"]
        Publishing["publishing.yml"]
        IntegrationTests["integration_tests.yml"]
        DocWorkflow["documentation.yml"]
    end

    subgraph "Generated Artifacts"
        DockerImages["Docker Images (cuda-quantum)"]
        PythonWheels["Python Wheels (cuda-quantum-cu*)"]
        Installers["Installers"]
        Docs["Documentation"]
    end

    subgraph "Deployment Targets"
        GHCR["GitHub Container Registry (ghcr.io)"]
        NGC["NVIDIA NGC Registry (nvcr.io)"]
        GHReleases["GitHub Releases"]
        GHPages["GitHub Pages"]
    end

    PREvent --> CI
    Commit --> CI
    Commit --> Deployments
    Manual --> Deployments
    Manual --> Publishing
    Manual --> IntegrationTests
    Schedule --> IntegrationTests

    CI --> |"On Success"| Deployments
    Deployments --> |"Triggers via workflow_dispatch"| Publishing
    Publishing --> |"After Success"| IntegrationTests
    CI --> |"On Success"| DocWorkflow
    Publishing --> |"On Success"| DocWorkflow

    Publishing --> DockerImages
    Publishing --> PythonWheels
    Publishing --> Installers
    DocWorkflow --> Docs

    DockerImages --> GHCR
    DockerImages --> NGC
    PythonWheels --> GHReleases
    Installers --> GHReleases
    Docs --> GHPages
```

Sources: [.github/workflows/ci.yml:20-26](), [.github/workflows/deployments.yml:1-43](), [.github/workflows/publishing.yml:1-41](), [.github/workflows/integration_tests.yml:1-16](), [.github/workflows/documentation.yml:1-33]()

## Core Workflows

The CI/CD system consists of several interconnected GitHub Actions workflows that handle different aspects of the build, test, and deployment process.

### CI Workflow

The CI workflow validates code changes by building CUDA Quantum with various toolchains and configurations and running comprehensive tests.

```mermaid
flowchart TD
    PREvent["PR or Commit"] --> CI["ci.yml workflow"]
    
    CI --> |"First Phase"| DevDeps["devdeps job"]
    CI --> |"First Phase"| WheelDeps["wheeldeps job"]
    CI --> |"First Phase"| SourceBuild["source_build job"]
    
    subgraph "Dependency Building"
        DevDeps --> |"Matrix: Platform x Toolchain"| DevEnvs["dev_environment.yml workflow"]
        WheelDeps --> |"Matrix: Platform x CUDA Version"| WheelEnvs["dev_environment.yml workflow"]
        SourceBuild --> |"Matrix: Platform x CUDA Version"| SourceEnvs["dev_environment.yml workflow"]
    end
    
    DevEnvs --> BuildTest["build_and_test job"]
    BuildTest --> |"Matrix: Platform x Toolchain x MPI"| TestResults["test_in_devenv.yml workflow"]
    
    DevEnvs --> GenCodeCoverage["gen_code_coverage job"]
    GenCodeCoverage --> CodeCovReport["generate_cc.yml workflow"]
    
    DevEnvs --> DockerImage["docker_image job"]
    DockerImage --> |"Uses"| DockerImagesWF["docker_images.yml workflow"]
    
    WheelEnvs --> PythonWheels["python_wheels job"]
    PythonWheels --> |"Uses"| PythonWheelsWF["python_wheels.yml workflow"]
    
    BuildTest --> |"On Success"| PR["PR Can Be Merged"]
```

Sources: [.github/workflows/ci.yml:78-252](), [.github/workflows/test_in_devenv.yml:1-284](), [.github/workflows/generate_cc.yml:1-162](), [.github/workflows/docker_images.yml:1-630](), [.github/workflows/python_wheels.yml:1-361]()

### Deployments Workflow

The Deployments workflow runs after PR merges to the main branch or on push to release branches to prepare artifacts for deployment.

```mermaid
flowchart TD
    subgraph "Triggers"
        PRMerge["workflow_run: PR merged"]
        Push["push: releases/*, staging/*, experimental/*"]
        Manual["workflow_dispatch"]
    end
    
    PRMerge --> Deployments["deployments.yml workflow"]
    Push --> Deployments
    Manual --> Deployments
    
    Deployments --> Metadata["metadata job"]
    Metadata --> |"Matrix Builds"| DependencyBuilds["Build Dependencies"]
    
    subgraph "Dependencies Jobs"
        DependencyBuilds --> DevDeps["devdeps job"]
        DependencyBuilds --> WheelDeps["wheeldeps job"]
        DependencyBuilds --> SourceBuild["source_build job"]
        DependencyBuilds --> OpenMPI["openmpi job"]
    end
    
    DevDeps --> |"Configure"| Config["config job"]
    Config --> ExtDevDeps["extdevdeps job"]
    ExtDevDeps --> ExtConfig["ext_config job"]
    ExtConfig --> DockerImages["docker_images job"]
    
    DockerImages --> DigestConfig["digest_config job"]
    DigestConfig --> Stitch["stitch job"]
    
    WheelDeps --> PythonWheels["python_wheels job"]
    SourceBuild --> Binaries["prebuilt_binaries job"]
    
    Stitch --> Dispatch["dispatch job"]
    PythonWheels --> Dispatch
    Binaries --> Dispatch
    
    Dispatch --> |"Trigger"| PublishingWorkflow["publishing.yml workflow"]
```

Sources: [.github/workflows/deployments.yml:48-453](), [.github/workflows/deployments.yml:1-43]()

### Publishing Workflow

The Publishing workflow creates and publishes artifacts to various registries and repositories.

```mermaid
flowchart TD
    DeploymentsWorkflow["deployments.yml workflow"] --> |"Triggers"| Publishing["publishing.yml workflow"]
    Manual["workflow_dispatch"] --> Publishing
    WorkflowRun["workflow_run: Deployments"] --> Publishing
    
    Publishing --> Assets["assets job"]
    
    Assets --> |"Matrix: info_file"| CUDAQImages["cudaq_images job"]
    Assets --> |"Matrix: info_file x python_version"| CUDAQWheels["cudaq_wheels job"]
    Assets --> |"Matrix: info_file"| CUDAQInstallers["cudaq_installers job"]
    
    CUDAQImages --> |"Sign Images"| PushImages["docker/build-push-action"]
    CUDAQWheels --> WheelReleaseInfo["cudaq_wheels_release_info job"]
    CUDAQWheels --> MetaPackages["cudaq_metapackages job"]
    
    CUDAQImages --> ImageValidationConfig["image_validation_config job"]
    ImageValidationConfig --> |"Matrix: image_hash"| ImageValidation["image_validation job"]
    
    ImageValidation --> |"Success"| IntegrationTests["integration_tests.yml workflow"]
```

Sources: [.github/workflows/publishing.yml:1-41](), [.github/workflows/publishing.yml:41-774](), [.github/workflows/publishing.yml:332-517](), [.github/workflows/publishing.yml:526-637](), [.github/workflows/publishing.yml:638-778](), [.github/workflows/publishing.yml:779-826](), [.github/workflows/publishing.yml:811-826]()

### Integration Tests Workflow

The Integration Tests workflow validates CUDA-Q with various quantum hardware providers through nightly testing and manual triggers.

```mermaid
flowchart TD
    subgraph "Triggers"
        Manual["workflow_dispatch (target, single_test_name, cudaq_test_image inputs)"]
        Schedule["schedule: cron 0 3 * * *"]
    end
    
    Manual --> IntegrationTests["integration_tests.yml"]
    Schedule --> IntegrationTests
    
    IntegrationTests --> Setup["setup job"]
    Setup --> |"cudaq_test_image output"| Metadata["metadata job (retrieve commit info)"]
    
    Metadata --> ProviderMatrixSetup["provider_matrix_setup job"]
    ProviderMatrixSetup --> |"outputs.providers"| ProviderTest["provider_test job (matrix strategy)"]
    
    subgraph "Provider Matrix (environment: backend-validation)"
        ProviderTest --> |"matrix.provider"| GetTests["Get tests step (steps.gettests)"]
        GetTests --> SetupAccount["Setup account step (per-provider authentication)"]
        SetupAccount --> RunTests["Run tests step"]
        
        RunTests --> AnyonTests["anyon: targettests/anyon/*.cpp"]
        RunTests --> FermioniqTests["fermioniq: docs/sphinx/targets/cpp/fermioniq.cpp"]
        RunTests --> InfleqtionTests["infleqtion: docs/sphinx/targets/cpp/infleqtion.cpp"]
        RunTests --> IonQTests["ionq: targettests/ionq/*.cpp"]
        RunTests --> IQMTests["iqm: targettests/iqm/*.cpp"]
        RunTests --> OQCTests["oqc: targettests/oqc/*.cpp"]
        RunTests --> ORCATests["orca: docs/sphinx/targets/cpp/orca.cpp"]
        RunTests --> PasqalTests["pasqal: docs/sphinx/targets/cpp/pasqal.cpp"]
        RunTests --> QCITests["qci: targettests/qci/*.cpp"]
        RunTests --> QuantinuumTests["quantinuum: targettests/quantinuum/*.cpp, targettests/quantinuum_ng/*.cpp"]
    end
```

**Provider Authentication**: Each provider test uses environment-specific secrets stored in the `backend-validation` environment:
- **Anyon**: `ANYON_USERNAME`, `ANYON_PASSWORD` → creates `~/.anyon_config`
- **FermionIQ**: `FERMIONIQ_ACCESS_TOKEN_ID`, `FERMIONIQ_ACCESS_TOKEN_SECRET`
- **Infleqtion**: `SUPERSTAQ_API_KEY`
- **IonQ**: `IONQ_API_KEY`
- **IQM**: `IQM_TOKEN` → creates `IQM_TOKENS_FILE`
- **OQC**: `OQC_URL`, `OQC_EMAIL`, `OQC_DEVICE`, `OQC_AUTH_TOKEN`
- **ORCA**: `ORCA_ACCESS_URL`
- **Pasqal**: `PASQAL_USERNAME`, `PASQAL_PASSWORD`, `PASQAL_PROJECT_ID`
- **QCI**: `QCI_AUTH_TOKEN`
- **Quantinuum**: `BACKEND_LOGIN_EMAIL`, `QUANTINUUM_NEXUS_PASSWORD` → creates `~/.quantinuum_config`

Sources: [.github/workflows/integration_tests.yml:1-61](), [.github/workflows/integration_tests.yml:65-184](), [.github/workflows/integration_tests.yml:186-376](), [.github/workflows/integration_tests.yml:378-674]()

## Artifact Building Process

### Docker Image Building

The Docker image building process creates container images for different platforms and CUDA versions.

```mermaid
flowchart TD
    subgraph "Input Parameters"
        Platforms["platforms (linux/amd64 or linux/arm64)"]
        CUDAVersion["cuda_version (11.8 or 12.0)"]
        DevDepsImage["devdeps_image (from dev_environment.yml)"]
        OMPIImage["ompidev_image (from dev_environment.yml)"]
    end
    
    Platforms --> DockerImageProcess["docker_images.yml workflow"]
    CUDAVersion --> DockerImageProcess
    DevDepsImage --> DockerImageProcess
    OMPIImage --> DockerImageProcess
    
    DockerImageProcess --> Metadata["metadata job"]
    Metadata --> OMPIBuild["ompi_image job"]
    
    OMPIBuild --> CUDAQDevImage["cudaqdev_image job"]
    CUDAQDevImage --> CUDAQReleaseImage["cudaq_image job"]
    
    CUDAQDevImage --> |"docker/build-push-action"| DevImage["cuda-quantum-dev:tag"]
    CUDAQReleaseImage --> |"docker/build-push-action"| ReleaseImage["cuda-quantum:tag"]
    
    DevImage --> |"cosign sign"| SignedDevImage["Signed cuda-quantum-dev image"]
    ReleaseImage --> |"cosign sign"| SignedReleaseImage["Signed cuda-quantum image"]
    
    SignedDevImage --> |"Push to Registry"| GHCR["ghcr.io/nvidia/cuda-quantum-dev"]
    SignedReleaseImage --> |"Push to Registry"| GHCR2["ghcr.io/nvidia/cuda-quantum"]
    SignedReleaseImage --> |"Push if needs.metadata.outputs.push_to_ngc"| NGC["nvcr.io/nvidia/cuda-quantum"]
    
    SignedReleaseImage --> ImageValidation["image_validation job"]
    ImageValidation --> |"Run on GPU"| ValidationTests["linux-amd64-gpu-v100-latest-1 runner"]
```

Sources: [.github/workflows/docker_images.yml:1-83](), [.github/workflows/docker_images.yml:83-206](), [.github/workflows/docker_images.yml:207-376](), [.github/workflows/docker_images.yml:377-630](), [.github/workflows/docker_images.yml:631-826]()

### Python Wheel Building

The Python wheel building process creates wheels for different platforms, Python versions, and CUDA versions.

```mermaid
flowchart TD
    subgraph "Input Parameters"
        Platforms["platform (linux/amd64 or linux/arm64)"]
        PythonVersion["python_version (3.10/3.11/3.12/3.13)"]
        CUDAVersion["cuda_version (11.8/12.0)"]
        DevDepsImage["devdeps_image (from wheeldeps job)"]
    end
    
    Platforms --> WheelProcess["python_wheels.yml workflow"]
    PythonVersion --> WheelProcess
    CUDAVersion --> WheelProcess
    DevDepsImage --> WheelProcess
    
    WheelProcess --> BuildWheel["build_wheel job"]
    BuildWheel --> |"docker/build-push-action"| WheelBuild["cudaq.wheel.Dockerfile build"]
    WheelBuild --> UploadWheel["actions/upload-artifact"]
    
    UploadWheel --> CreateTestConfig["create_test_config job"]
    CreateTestConfig --> Validation["validation job"]
    
    subgraph "Validation Process"
        Validation --> |"Matrix: os_image × pip_install_flags"| InstallWheel["docker build wheel_validation:local"]
        InstallWheel --> RunPyTests["python -m pytest -v /tmp/tests/"]
        RunPyTests --> ValidateSnippets["Run Python snippets"]
        ValidateSnippets --> ValidateExamples["Run Python examples"]
        ValidateExamples --> MPITests["Run MPI tests (disabled)"]
    end
    
    Validation --> |"Success"| MetaPackages["python_metapackages.yml workflow"]
    MetaPackages --> |"For each CUDA Version"| WheelPublishing["Upload to GitHub Releases"]
```

Sources: [.github/workflows/python_wheels.yml:1-40](), [.github/workflows/python_wheels.yml:41-156](), [.github/workflows/python_wheels.yml:157-176](), [.github/workflows/python_wheels.yml:177-361](), [.github/workflows/publishing.yml:779-789]()

### Installer Building

The installer building process creates platform-specific installers for CUDA Quantum.

```mermaid
flowchart TD
    subgraph "Input Parameters"
        Platform["platform (linux/amd64 or linux/arm64)"]
        PlatformBaseImage["platform_base_image (e.g., amd64/almalinux:8)"]
        CUDAVersion["cuda_version (11.8/12.0)"]
        BuildCache["build_cache (from source_build job)"]
    end
    
    Platform --> InstallerProcess["prebuilt_binaries.yml workflow"]
    PlatformBaseImage --> InstallerProcess
    CUDAVersion --> InstallerProcess
    BuildCache --> InstallerProcess
    
    InstallerProcess --> BuildAssets["build_installer job"]
    BuildAssets --> |"docker/build-push-action"| DockerBuild["assets.Dockerfile build"]
    DockerBuild --> |"docker/build-push-action"| CreateInstaller["installer.Dockerfile build"]
    
    CreateInstaller --> UploadInstaller["actions/upload-artifact"]
    UploadInstaller --> |"publishing.yml workflow"| Publishing["cudaq_installers job"]
    Publishing --> |"actions/upload-artifact"| GHRelease["GitHub Release"]
```

Sources: [.github/workflows/prebuilt_binaries.yml:1-35](), [.github/workflows/prebuilt_binaries.yml:36-277](), [.github/workflows/publishing.yml:526-637]()

## Deployment and Release Process

The deployment and release process involves coordinated execution of several workflows to build, publish, and validate CUDA Quantum artifacts.

```mermaid
flowchart TD
    subgraph "Triggering Events"
        PRMerge["PR Merged to Main (prepare_deployment.yml)"]
        ReleaseBranch["Push to releases/*, staging/*, experimental/*"]
        Manual["workflow_dispatch with create_release input"]
    end
    
    PRMerge --> |"workflow_run"| Deployments["deployments.yml workflow"]
    ReleaseBranch --> Deployments
    Manual --> Deployments
    
    Deployments --> |"Build All Artifacts"| DeploymentComplete["dispatch job"]
    DeploymentComplete --> |"github-script workflow_dispatch"| Publishing["publishing.yml workflow"]
    
    Publishing --> |"assets job"| DownloadAssets["Download deployment artifacts"]
    DownloadAssets --> |"Matrix builds"| BuildArtifacts["Build release artifacts"]
    
    BuildArtifacts --> DockerImages["cudaq_images job"]
    BuildArtifacts --> PythonWheels["cudaq_wheels job"]
    BuildArtifacts --> Installers["cudaq_installers job"]
    
    DockerImages --> |"image_hash"| ImageValidation["image_validation job"]
    PythonWheels --> WheelValidation["validation job in python_wheels.yml"]
    
    ImageValidation --> |"Success"| IntegrationTests["integration_tests.yml workflow"]
    
    IntegrationTests --> |"Success"| FinalRelease["Release Ready"]
    FinalRelease --> |"For Tagged Releases"| GHRelease["GitHub Release with deployment_info.txt"]
    FinalRelease --> |"publishing_stable.yml workflow"| NGCPush["Push to NGC Production"]
```

Sources: [.github/workflows/prepare_deployment.yml:1-28](), [.github/workflows/deployments.yml:1-43](), [.github/workflows/deployments.yml:288-354](), [.github/workflows/publishing.yml:1-41](), [.github/workflows/publishing.yml:41-774](), [.github/workflows/publishing_stable.yml:1-35](), [.github/workflows/publishing_stable.yml:36-273]()

## Registry and Environment Management

CUDA Quantum uses multiple registries and environments for different stages of the deployment process.

```mermaid
flowchart TD
    subgraph "Development"
        PRBuild["PR Build (ci.yml)"]
        CIBuild["CI Build (ci.yml)"]
    end
    
    subgraph "Staging"
        MainBuild["Main Branch Build (deployments.yml)"]
        StagingBuild["Staging Branch Build (deployments.yml)"]
        NightlyBuild["Nightly Build (scheduled)"]
    end
    
    subgraph "Production"
        ReleaseBuild["Release Branch Build (deployments.yml)"]
        StableRelease["Stable Release (publishing_stable.yml)"]
    end
    
    PRBuild --> |"pr-{number} tag"| GHCR_PR["ghcr.io/nvidia/cuda-quantum:pr-{number}"]
    CIBuild --> |"branch tag"| GHCR_CI["ghcr.io/nvidia/cuda-quantum:{branch}"]
    
    MainBuild --> |"latest tag"| GHCR_Latest["ghcr.io/nvidia/cuda-quantum:latest"]
    StagingBuild --> |"version tag"| GHCR_Staging["ghcr.io/nvidia/cuda-quantum:{version}"]
    NightlyBuild --> |"nightly tag"| GHCR_Nightly["ghcr.io/nvidia/cuda-quantum:nightly"]
    
    ReleaseBuild --> |"version tag"| GHCR_Release["ghcr.io/nvidia/cuda-quantum:{version}"]
    ReleaseBuild --> |"version tag"| NGC_Release["nvcr.io/nvidia/cuda-quantum:{version}"]
    
    StableRelease --> |"stable tag"| NGC_Stable["nvcr.io/nvidia/quantum/cuda-quantum:stable"]
    
    subgraph "Clean-up Process"
        Schedule["scheduled job (clean_up.yml)"]
        Schedule --> |"gh_registry.yml"| GHCRCleanup["delete_images job"]
        Schedule --> |"clean_up.yml"| DraftCleanup["draft_releases job"]
        Schedule --> |"clean_up.yml"| BranchCleanup["bot_branches job"]
    end
```

Sources: [.github/workflows/gh_registry.yml:1-7](), [.github/workflows/gh_registry.yml:8-265](), [.github/workflows/clean_up.yml:1-20](), [.github/workflows/clean_up.yml:21-67](), [.github/workflows/clean_up.yml:68-154](), [.github/workflows/publishing_stable.yml:1-35]()

## Integration Testing Details

### Provider Test Execution

The `provider_test` job executes tests in a matrix strategy across all configured providers. Test execution varies by provider and file type:

| Provider | Compilation | Execution | Test Files |
|----------|------------|-----------|------------|
| Anyon | `nvq++ --target anyon --anyon-machine telegraph-8q` | `./a.out` | `targettests/anyon/*.cpp` |
| FermionIQ | `nvq++ --target fermioniq` or `python3` | `./a.out` or direct | C++/Python files in docs |
| Infleqtion | `nvq++ --target infleqtion` or `python3` | `./a.out` or direct | C++/Python files in docs |
| IonQ | `nvq++ --target ionq` | `./a.out` | `targettests/ionq/*.cpp` |
| IQM | `nvq++ --target iqm` | `./a.out` | `targettests/iqm/*.cpp` |
| OQC | `nvq++ --target oqc` | `./a.out` | `targettests/oqc/*.cpp` |
| ORCA | `nvq++ --target orca --orca-url` or `python3` | `./a.out` or direct | C++/Python files in docs |
| Pasqal | `nvq++ --target pasqal --pasqal-machine` or `python3` | `./a.out` or direct | C++/Python files in docs |
| QCI | `nvq++ --target qci` | `./a.out` | `targettests/qci/*.cpp` |
| Quantinuum | `nvq++ --target quantinuum --quantinuum-machine` or `python3` | `./a.out` or direct | `targettests/quantinuum/*.cpp`, `targettests/quantinuum_ng/*.cpp` |

### Provider Test Configuration

The `provider_matrix_setup` job determines which providers to test based on the trigger:

```mermaid
flowchart TD
    Trigger["Workflow Trigger"]
    Trigger --> CheckEventType{"Event Type?"}
    
    CheckEventType --> |"schedule or inputs.target == nightly"| AllProviders["providers = all 10 providers"]
    CheckEventType --> |"workflow_dispatch with specific target"| SingleProvider["providers = [inputs.target]"]
    
    AllProviders --> ProviderArray["['anyon', 'fermioniq', 'infleqtion', 'ionq', 'iqm', 'oqc', 'orca', 'pasqal', 'qci', 'quantinuum']"]
    SingleProvider --> ProviderArray
    
    ProviderArray --> MatrixOutput["outputs.providers (JSON array)"]
    MatrixOutput --> ProviderTestJob["provider_test job (matrix.provider)"]
```

### Test Selection Logic

Within each provider test, the `gettests` step determines which tests to run:

```mermaid
flowchart TD
    GetTests["steps.gettests"]
    GetTests --> CheckInput{"inputs.single_test_name set?"}
    
    CheckInput --> |"Yes"| SingleTest["testlist = inputs.single_test_name"]
    CheckInput --> |"No"| ProviderSwitch["Switch on matrix.provider"]
    
    ProviderSwitch --> AnyonFiles["targettests/anyon/*.cpp"]
    ProviderSwitch --> FermioniqFiles["docs/sphinx/targets/cpp/fermioniq.cpp + Python files"]
    ProviderSwitch --> InfleqtionFiles["docs/sphinx/targets/cpp/infleqtion.cpp + Python files"]
    ProviderSwitch --> IonqFiles["targettests/ionq/*.cpp"]
    ProviderSwitch --> IqmFiles["targettests/iqm/*.cpp"]
    ProviderSwitch --> OqcFiles["targettests/oqc/*.cpp"]
    ProviderSwitch --> OrcaFiles["docs/sphinx/targets/cpp/orca.cpp + orca_mqpu.cpp + Python files"]
    ProviderSwitch --> PasqalFiles["docs/sphinx/targets/cpp/pasqal.cpp + Python files"]
    ProviderSwitch --> QciFiles["targettests/qci/*.cpp"]
    ProviderSwitch --> QuantinuumFiles["targettests/quantinuum/*.cpp + targettests/quantinuum_ng/*.cpp + Python"]
    
    SingleTest --> TestExecution["Test Execution Loop"]
    AnyonFiles --> TestExecution
    FermioniqFiles --> TestExecution
    InfleqtionFiles --> TestExecution
    IonqFiles --> TestExecution
    IqmFiles --> TestExecution
    OqcFiles --> TestExecution
    OrcaFiles --> TestExecution
    PasqalFiles --> TestExecution
    QciFiles --> TestExecution
    QuantinuumFiles --> TestExecution
```

Sources: [.github/workflows/integration_tests.yml:166-184](), [.github/workflows/integration_tests.yml:204-257](), [.github/workflows/integration_tests.yml:379-674]()

## Advanced Features

### Caching System

CUDA Quantum uses a multi-layered caching system to improve build performance. The `dev_environment.yml` workflow implements the caching logic through the `cache` step in the `build` job.

```mermaid
flowchart TD
    subgraph "Cache Configuration (steps.cache)"
        BuildConfigID["build_config_id (e.g., clang16, cu12.6-gcc11)"]
        ImageID["image_id (e.g., devdeps, devdeps.manylinux)"]
        PlatformID["platform_id (amd64 or arm64)"]
        
        BuildConfigID --> CacheID["cache_id = image_id + build_config_id"]
        ImageID --> CacheID
        PlatformID --> CacheKey["Cache key components"]
        CacheID --> CacheKey
    end
    
    subgraph "Cache Types and Locations"
        RegistryCache["type=registry,ref=ghcr.io/.../buildcache-cuda-quantum-{cache_id}-{platform_id}:{branch}"]
        LocalBuildCache["type=local,src=/tmp/.buildcache.{image_id}"]
        
        RegistryCache --> |"cache-from"| DockerBuild["docker/build-push-action"]
        LocalBuildCache --> |"cache-from"| DockerBuild
        
        DockerBuild --> |"cache-to (if update_registry_cache)"| UpdateRegistry["type=registry,mode=max"]
        DockerBuild --> |"cache-to (if create_local_cache)"| UpdateLocal["type=local,dest=/tmp/.buildcache.{image_id}-new"]
    end
    
    subgraph "Cache Hierarchy"
        PRCache["PR Cache: pull-request-{pr_number}"]
        BranchCache["Branch Cache: {branch_name}"]
        MainCache["Main Cache: main"]
        NvidiaCache["NVIDIA Cache: ghcr.io/nvidia/buildcache-cuda-quantum-*"]
        
        PRCache --> |"Fallback"| BranchCache
        BranchCache --> |"Fallback"| MainCache
        MainCache --> |"Fallback"| NvidiaCache
    end
    
    subgraph "Cache Management"
        ActionsCache["actions/cache/restore and actions/cache/save"]
        ActionsCache --> |"Key: {branch}-cuda-quantum-{cache_id}-{platform_id}-{commit}"| LocalStorage["/tmp/.buildcache.{image_id}"]
        
        GHRegistry["gh_registry.yml (daily cleanup)"]
        GHRegistry --> |"delete-package-versions"| CleanOld["Remove old untagged versions"]
    end
```

**Cache Key Structure**: The cache system uses hierarchical keys to enable fallback to parent branch caches:
- Local GitHub Actions cache: `{branch}/merge-cuda-quantum-{cache_id}-{platform_id}-{commit_sha}`
- Registry cache: `ghcr.io/{owner}/buildcache-cuda-quantum-{cache_id}-{platform_id}:{branch}`

**Cache Update Flow**: When `update_registry_cache` is set, the workflow only updates the cache and terminates without creating artifacts. This is used during the deployment workflow to prepare caches for release builds.

Sources: [.github/workflows/dev_environment.yml:82-83](), [.github/workflows/dev_environment.yml:186-376](), [.github/workflows/dev_environment.yml:240-309](), [.github/workflows/gh_registry.yml:1-265]()

### Documentation Publishing

The documentation workflow builds and publishes CUDA Quantum documentation.

```mermaid
flowchart TD
    subgraph "Triggers"
        CI["workflow_run: CI"]
        Deployments["workflow_run: Deployments"]
        Manual["workflow_dispatch"]
    end
    
    CI --> |"if workflow_run.conclusion == 'success'"| DocWorkflow["documentation.yml workflow"]
    Deployments --> |"if workflow_run.conclusion == 'success'"| DocWorkflow
    Manual --> |"deployment_id, version inputs"| DocWorkflow
    
    DocWorkflow --> DownloadArtifacts["Download cuda_quantum_docs artifact"]
    DownloadArtifacts --> DetermineTarget["Determine target_folder"]
    
    DetermineTarget --> |"pr-{number}"| PRPreview["PR Preview Docs"]
    DetermineTarget --> |"latest"| LatestDocs["Latest Docs (main branch)"]
    DetermineTarget --> |"version number"| VersionedDocs["Versioned Docs (releases/*)"]
    
    PRPreview --> PushDocs["git commit and push"]
    LatestDocs --> PushDocs
    VersionedDocs --> PushDocs
    
    PushDocs --> |"if pr_number"| CommentOnPR["gh pr comment"]
    PushDocs --> |"create_redirects.sh"| CreateRedirects["Create Version Redirects"]
```

Sources: [.github/workflows/documentation.yml:1-33](), [.github/workflows/documentation.yml:36-198]()

## Maintenance and Cleanup

CUDA Quantum includes automated processes for cleaning up resources to maintain the health of the CI/CD system.

```mermaid
flowchart TD
    subgraph "Triggering Events"
        Schedule["schedule: cron */5 * * * *"]
        Manual["workflow_dispatch"]
        PRClosed["pull_request_target: closed"]
    end
    
    Schedule --> CleanUp["clean_up.yml workflow"]
    Manual --> |"delete_draft_releases, delete_temp_branches inputs"| CleanUp
    PRClosed --> CleanUp
    
    CleanUp --> |"if inputs.delete_draft_releases"| DeleteDraftReleases["draft_releases job"]
    CleanUp --> |"if inputs.delete_temp_branches"| DeleteTempBranches["bot_branches job"]
    
    Schedule --> |"schedule: cron 0 3 * * *"| GHCRCleanup["gh_registry.yml workflow"]
    
    subgraph "GHCR Cleanup"
        GHCRCleanup --> GHCRConfig["ghcr_config job"]
        GHCRConfig --> |"Matrix: image"| DeleteImages["delete_images job"]
        DeleteImages --> |"actions/delete-package-versions"| UntaggedImages["Delete Untagged Images"]
        DeleteImages --> |"gh api"| OrphanedSigs["Delete Orphaned Signatures"]
        DeleteImages --> |"gh api"| OldVersions["Delete Old Versions (config/ghcr_config.json)"]
    end
    
    DeleteDraftReleases --> |"gh release list/view/delete"| ReleaseCheck["Delete if isDraft && isPrerelease"]
    DeleteTempBranches --> |"gh api"| BranchCheck["Delete branches starting with bot/"]
```

Sources: [.github/workflows/clean_up.yml:1-20](), [.github/workflows/clean_up.yml:21-67](), [.github/workflows/gh_registry.yml:1-7](), [.github/workflows/gh_registry.yml:8-265](), [.github/workflows/config/ghcr_config.json:1-22]()

This comprehensive CI/CD system ensures that CUDA Quantum is continuously built, tested, and deployed with high quality across multiple platforms, Python versions, and CUDA versions.

---

