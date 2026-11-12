<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/vgpu-device-manager · page 5 CI/CD Pipelines · fetched 2026-10-26 -->

# CI/CD Pipelines

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.common-ci.yml](.common-ci.yml)
- [.gitlab-ci.yml](.gitlab-ci.yml)
- [.nvidia-ci.yml](.nvidia-ci.yml)

</details>



This document provides an overview of the comprehensive CI/CD system that manages builds, testing, and releases for the NVIDIA vGPU Device Manager. The system spans multiple platforms including GitLab CI, GitHub Actions, and NVIDIA-specific internal pipelines, each with distinct responsibilities in the development and release workflow.

For detailed information about GitHub Actions workflows, see [GitHub Actions](#5.1). For code quality standards and security scanning processes, see [Code Quality & Security](#5.2).

## Multi-System CI/CD Architecture

The CI/CD infrastructure consists of three interconnected pipeline systems that work together to provide comprehensive coverage from development to production release.

```mermaid
graph TB
    subgraph "External Triggers"
        PullRequest["Pull Request"]
        GitPush["Git Push"]
        GitTag["Git Tag"]
    end
    
    subgraph "GitLab CI Pipeline"
        GLBuildDev["build-dev-image"]
        GLGoChecks["Go Checks<br/>fmt, vet, lint"]
        GLBuild["go-build"]
        GLTests["unit-tests"]
        GLImageBuild["image-ubi9"]
        GLStaging["release:staging-ubi9"]
    end
    
    subgraph "GitHub Actions"
        GHGolang["golang.yml"]
        GHImages["images.yml"]
        GHDependabot["dependabot"]
    end
    
    subgraph "NVIDIA CI Pipeline"
        NVImagePull["image-ubi9 (pull)"]
        NVScan["scan-ubi9-amd64"]
        NVNSpectStaging["update-nspect-staging"]
        NVNSpectProd["update-nspect"]
        NVNGCPublish["ngc-image-publish"]
    end
    
    subgraph "Registries"
        CIRegistry["CI Registry"]
        StagingRegistry["ghcr.io/nvidia"]
        NGCRegistry["nvcr.io"]
    end
    
    PullRequest --> GLGoChecks
    PullRequest --> GHGolang
    GitPush --> GLBuild
    GitPush --> GLTests
    GitPush --> GHImages
    
    GLBuildDev --> GLGoChecks
    GLGoChecks --> GLBuild
    GLBuild --> GLTests
    GLTests --> GLImageBuild
    GLImageBuild --> GLStaging
    GLStaging --> StagingRegistry
    
    StagingRegistry --> NVImagePull
    NVImagePull --> CIRegistry
    NVImagePull --> NVScan
    
    GitTag --> NVNSpectProd
    GLStaging --> NVNSpectStaging
    NVNSpectProd --> NVNGCPublish
    NVNGCPublish --> NGCRegistry
```

Sources: [.gitlab-ci.yml:1-99](), [.nvidia-ci.yml:1-211](), [.common-ci.yml:1-153]()

## Common Configuration System

The CI/CD system uses a shared configuration approach with `.common-ci.yml` serving as the foundation for both GitLab and NVIDIA pipelines. This ensures consistency across different execution environments.

### Pipeline Stages and Variables

| Stage | Purpose | Key Jobs |
|-------|---------|----------|
| `image` | Build development images | `build-dev-image` |
| `lint` | Code quality checks | `fmt`, `vet`, `lint` |
| `go-checks` | Go-specific validation | `ineffassign`, `misspell` |
| `go-build` | Compile applications | `go-build` |
| `unit-tests` | Run test suites | `unit-tests` |
| `image-build` | Build container images | `image-ubi9` |
| `test` | Integration testing | `.integration` |
| `scan` | Security scanning | `scan-ubi9-amd64` |
| `release` | Registry deployment | `release:staging-ubi9` |
| `ngc-publish` | NGC publishing | `ngc-image-publish` |

Key configuration variables include:
- `BUILD_MULTI_ARCH_IMAGES: "true"` - Enables multi-architecture builds
- `BUILDIMAGE: "${CI_REGISTRY_IMAGE}/build:${CI_COMMIT_SHORT_SHA}"` - Development image reference
- Platform targets: `PLATFORM: linux/amd64`, `PLATFORM: linux/arm64`
- Distribution targets: `DIST: ubi9`

Sources: [.common-ci.yml:21-50](), [.common-ci.yml:25-35]()

## GitLab CI Pipeline

The GitLab pipeline serves as the primary CI/CD system, handling the complete workflow from code validation to initial image publishing.

```mermaid
graph TD
    subgraph "Development Image"
        BuildDevImage["build-dev-image<br/>.build-image target"]
        PushBuildImage["docker push BUILDIMAGE"]
    end
    
    subgraph "Code Quality Stage"
        RequiresBuildImage[".requires-build-image<br/>Uses BUILDIMAGE"]
        Fmt["fmt<br/>make assert-fmt"]
        Vet["vet<br/>make vet"]
        Lint["lint<br/>make lint (allow_failure)"]
        Ineffassign["ineffassign<br/>make ineffassign (allow_failure)"]
        Misspell["misspell<br/>make misspell"]
    end
    
    subgraph "Build and Test"
        GoBuild["go-build<br/>make build"]
        UnitTests["unit-tests<br/>make coverage"]
    end
    
    subgraph "Container Build"
        ImageBuild[".image-build base"]
        ImageUbi9["image-ubi9<br/>make build-ubi9"]
    end
    
    BuildDevImage --> PushBuildImage
    PushBuildImage --> RequiresBuildImage
    RequiresBuildImage --> Fmt
    RequiresBuildImage --> Vet
    RequiresBuildImage --> Lint
    RequiresBuildImage --> Ineffassign
    RequiresBuildImage --> Misspell
    RequiresBuildImage --> GoBuild
    RequiresBuildImage --> UnitTests
    
    GoBuild --> ImageBuild
    UnitTests --> ImageBuild
    ImageBuild --> ImageUbi9
```

### Key Job Configurations

The GitLab pipeline uses several important base configurations:

- `.requires-build-image`: Extends jobs to use the development container built in the `image` stage
- `.go-check`: Base for all Go code quality checks, extends `.requires-build-image`
- `.image-build`: Configures Docker buildx setup for multi-architecture builds

Sources: [.gitlab-ci.yml:18-99](), [.gitlab-ci.yml:26-28](), [.gitlab-ci.yml:29-33]()

## NVIDIA CI Pipeline

The NVIDIA internal pipeline focuses on security scanning, compliance, and final publishing to NGC registry. It operates on images built by the GitLab pipeline.

```mermaid
graph TD
    subgraph "Image Acquisition"
        StagingSource["STAGING_REGISTRY<br/>ghcr.io/nvidia"]
        ImagePull[".image-pull base<br/>delayed: 30 minutes"]
        ImageUbi9Pull["image-ubi9<br/>regctl manifest get"]
        CIRegistryPush["push to CI_REGISTRY"]
    end
    
    subgraph "Security Scanning"
        ScanBase[".scan base<br/>PULSE_IMAGE"]
        ScanUbi9["scan-ubi9-amd64<br/>pulse-cli scan"]
        ScanArtifacts["Artifacts:<br/>pulse-cli.log<br/>licenses.json<br/>sbom.json<br/>vulns.json"]
    end
    
    subgraph "NGC Publishing Workflow"
        NSpectVariables[".ngc-publish-variables<br/>build-info creation"]
        UpdateNSpectStaging["update-nspect-staging<br/>ENV: stage"]
        UpdateNSpectProd["update-nspect<br/>ENV: prod"]
        MockPublish["mock-image-publish<br/>test MR creation"]
        NGCPublish["ngc-image-publish<br/>cnt-ngc-publish render"]
    end
    
    StagingSource --> ImagePull
    ImagePull --> ImageUbi9Pull
    ImageUbi9Pull --> CIRegistryPush
    ImageUbi9Pull --> ScanBase
    ScanBase --> ScanUbi9
    ScanUbi9 --> ScanArtifacts
    
    NSpectVariables --> UpdateNSpectStaging
    NSpectVariables --> UpdateNSpectProd
    UpdateNSpectStaging --> MockPublish
    UpdateNSpectProd --> NGCPublish
```

### NVIDIA Pipeline Specializations

The NVIDIA pipeline includes several unique features:

- **Delayed Image Pull**: Uses `when: delayed` and `start_in: 30 minutes` to allow upstream pipelines to complete
- **Container Tags**: Runs on specialized runners with tags `cnt`, `container-dev`, `docker/multi-arch`
- **Pulse Security Scanning**: Uses `pulse-cli` for comprehensive security analysis
- **NGC Publishing Automation**: Uses `cnt-ngc-publish` tool for registry management

Sources: [.nvidia-ci.yml:39-72](), [.nvidia-ci.yml:81-112](), [.nvidia-ci.yml:177-211]()

## Image Build and Release Flow

The system manages a complex flow of container images across multiple registries with different purposes and access controls.

```mermaid
graph TD
    subgraph "Build Process"
        SourceCode["Source Code<br/>Git Commit SHA"]
        BuildxSetup[".buildx-setup<br/>docker buildx create"]
        DockerBuild["make build-ubi9<br/>PUSH_ON_BUILD=true"]
    end
    
    subgraph "Registry Flow"
        CIReg["CI_REGISTRY<br/>Internal GitLab Registry"]
        StagingReg["STAGING_REGISTRY<br/>ghcr.io/nvidia"]
        NGCStaging["NGC_STAGING_REGISTRY<br/>nvcr.io staging"]
        NGCProd["NGC Production<br/>nvcr.io public"]
    end
    
    subgraph "Release Jobs"
        ReleaseBase[".release base<br/>regctl registry login"]
        ReleaseStagingUbi9["release:staging-ubi9<br/>OUT_IMAGE_NAME"]
        ReleaseExternal[".release:external<br/>CI_COMMIT_TAG trigger"]
    end
    
    subgraph "Publishing Tools"
        RegctlSetup[".regctl-setup<br/>regctl-linux-amd64"]
        MakefilePush["make push-ubi9<br/>deployments/container/Makefile"]
    end
    
    SourceCode --> BuildxSetup
    BuildxSetup --> DockerBuild
    DockerBuild --> CIReg
    
    CIReg --> ReleaseBase
    ReleaseBase --> ReleaseStagingUbi9
    ReleaseStagingUbi9 --> StagingReg
    StagingReg --> ReleaseExternal
    ReleaseExternal --> NGCStaging
    
    RegctlSetup --> ReleaseBase
    ReleaseBase --> MakefilePush
```

### Registry Strategy

The multi-registry approach serves different purposes:

| Registry | Purpose | Access | Image Tags |
|----------|---------|--------|------------|
| `CI_REGISTRY` | Internal GitLab registry | Private | `${CI_COMMIT_SHORT_SHA}` |
| `ghcr.io/nvidia` | Public staging | Public | `${CI_COMMIT_SHORT_SHA}` |
| `NGC_STAGING_REGISTRY` | NVIDIA staging | Internal | Release testing |
| NGC Production | Public release | Public | `${CI_COMMIT_TAG}` |

The system uses `regctl` for advanced registry operations and supports multi-architecture manifests for `linux/amd64` and `linux/arm64` platforms.

Sources: [.common-ci.yml:81-153](), [.nvidia-ci.yml:39-72](), [.common-ci.yml:52-63]()

---

