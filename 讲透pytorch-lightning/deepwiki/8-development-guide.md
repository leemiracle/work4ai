<!-- source: DeepWiki mcp.deepwiki.com · repo Lightning-AI/pytorch-lightning · page 8 Development Guide · fetched 2026-10-21 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.actions/assistant.py](.actions/assistant.py)
- [.actions/requirements.txt](.actions/requirements.txt)
- [.github/checkgroup.yml](.github/checkgroup.yml)
- [.github/workflows/_build-packages.yml](.github/workflows/_build-packages.yml)
- [.github/workflows/_legacy-checkpoints.yml](.github/workflows/_legacy-checkpoints.yml)
- [.github/workflows/ci-pkg-install.yml](.github/workflows/ci-pkg-install.yml)
- [.github/workflows/ci-tests-fabric.yml](.github/workflows/ci-tests-fabric.yml)
- [.github/workflows/ci-tests-pytorch.yml](.github/workflows/ci-tests-pytorch.yml)
- [.github/workflows/cleanup-caches.yml](.github/workflows/cleanup-caches.yml)
- [.github/workflows/code-checks.yml](.github/workflows/code-checks.yml)
- [.github/workflows/docs-build.yml](.github/workflows/docs-build.yml)
- [.github/workflows/docs-tutorials.yml](.github/workflows/docs-tutorials.yml)
- [.github/workflows/labeler-issue.yml](.github/workflows/labeler-issue.yml)
- [.github/workflows/release-nightly.yml](.github/workflows/release-nightly.yml)
- [.github/workflows/release-pkg.yml](.github/workflows/release-pkg.yml)
- [.lightning/workflows/fabric.yml](.lightning/workflows/fabric.yml)
- [.lightning/workflows/pytorch.yml](.lightning/workflows/pytorch.yml)

</details>



## Purpose and Scope

This guide provides technical details for contributors to the PyTorch Lightning repository. It covers the testing infrastructure, CI/CD pipelines, documentation system, and release processes that enable the development and maintenance of the Lightning ecosystem.

For information about the package structure and build system, see [Package Architecture](#7.1). For detailed information about specific CI workflows, testing strategies, and documentation building, see the child pages: [CI/CD Pipeline](#8.1), [Testing Infrastructure](#8.2), and [Documentation System](#8.3).

## Development Workflow Overview

The Lightning monorepo employs a multi-package development model where three distinct packages (`lightning`, `pytorch-lightning`, `lightning-fabric`) are developed, tested, and released from a single codebase. The development workflow integrates:

- **Intelligent check orchestration** via `checkgroup.yml` that determines required tests based on changed files
- **Multi-dimensional testing** across OS (macOS, Ubuntu, Windows), Python versions (3.10-3.13), and PyTorch versions (2.1-2.9)
- **Dual execution environments**: CPU tests on GitHub Actions and GPU tests on Lightning AI's platform
- **Automated package building and validation** for all three package flavors
- **Continuous documentation deployment** to Google Cloud Storage

```mermaid
graph TB
    subgraph "Code Changes"
        PR["Pull Request / Push"]
        Files["Changed Files"]
    end
    
    subgraph "Check Orchestration"
        CheckGroup["checkgroup.yml<br/>Determines required checks"]
        PTLPaths["pytorch_lightning paths<br/>→ pl-cpu + pl-gpu checks"]
        FabricPaths["fabric paths<br/>→ fabric-cpu + fabric-gpu checks"]
        CommonPaths["src/**, requirements/**<br/>→ mypy + install checks"]
        DocsPaths["docs/**, src/**<br/>→ docs-make checks"]
    end
    
    subgraph "GitHub Actions CPU Tests"
        PTLCPUJob["ci-tests-pytorch.yml<br/>pl-cpu job"]
        FabricCPUJob["ci-tests-fabric.yml<br/>fabric-cpu job"]
        MyPyJob["code-checks.yml<br/>mypy job"]
        InstallJob["ci-pkg-install.yml<br/>install-pkg job"]
        DocsJob["docs-build.yml<br/>docs-make job"]
    end
    
    subgraph "Lightning AI GPU Tests"
        PTLGPUJob[".lightning/workflows/pytorch.yml<br/>CUDA 12.1/12.6"]
        FabricGPUJob[".lightning/workflows/fabric.yml<br/>CUDA 12.1/12.6"]
    end
    
    subgraph "Guardian Jobs"
        PLGuardian["pl-cpu-guardian<br/>Aggregates all pl-cpu results"]
        FabricGuardian["fabric-cpu-guardian<br/>Aggregates fabric-cpu results"]
        InstallGuardian["install-pkg-guardian<br/>Aggregates install results"]
    end
    
    PR --> Files
    Files --> CheckGroup
    
    CheckGroup --> PTLPaths
    CheckGroup --> FabricPaths
    CheckGroup --> CommonPaths
    CheckGroup --> DocsPaths
    
    PTLPaths --> PTLCPUJob
    PTLPaths --> PTLGPUJob
    FabricPaths --> FabricCPUJob
    FabricPaths --> FabricGPUJob
    CommonPaths --> MyPyJob
    CommonPaths --> InstallJob
    DocsPaths --> DocsJob
    
    PTLCPUJob --> PLGuardian
    FabricCPUJob --> FabricGuardian
    InstallJob --> InstallGuardian
    
    style CheckGroup fill:#f9f9f9
    style PLGuardian fill:#f9f9f9
    style PTLGPUJob fill:#f9f9f9
```

**Diagram: CI/CD Orchestration Architecture** - Shows how `checkgroup.yml` routes file changes to appropriate test jobs, with guardian jobs aggregating matrix results.

Sources: [.github/checkgroup.yml:1-197](), [.github/workflows/ci-tests-pytorch.yml:1-230](), [.github/workflows/ci-tests-fabric.yml:1-189](), [.lightning/workflows/pytorch.yml:1-193](), [.lightning/workflows/fabric.yml:1-165]()

## Testing Matrix and Import Conversion

The repository tests both unified (`lightning`) and standalone packages (`pytorch-lightning`, `lightning-fabric`) from the same test codebase using a clever import conversion strategy implemented in `assistant.py`.

### Testing Matrix Configuration

| Package | Python Versions | PyTorch Versions | Operating Systems |
|---------|----------------|------------------|-------------------|
| `lightning` | 3.10, 3.11, 3.12.7 | 2.1, 2.2.2, 2.3, 2.4.1, 2.5.1 | macOS-14, ubuntu-22.04, windows-2022 |
| `pytorch` | 3.12.7, 3.12, 3.13 | 2.6, 2.7, 2.8, 2.9 | macOS-14, ubuntu-22.04, windows-2022 |
| `fabric` | 3.12.7, 3.12, 3.13 | 2.6, 2.7, 2.8, 2.9 | macOS-14, ubuntu-22.04, windows-2022 |

```mermaid
graph TB
    subgraph "Single Test Codebase"
        TestsPTL["tests/tests_pytorch/<br/>Uses: lightning.pytorch"]
        TestsFabric["tests/tests_fabric/<br/>Uses: lightning.fabric"]
    end
    
    subgraph "Import Conversion: assistant.py"
        CopyReplace["copy_replace_imports()<br/>Replaces imports in-place"]
        Mapping["Mapping:<br/>lightning.pytorch → pytorch_lightning<br/>lightning.fabric → lightning_fabric"]
    end
    
    subgraph "Test Execution Modes"
        LightningMode["PACKAGE_NAME=lightning<br/>Tests unified package<br/>Import: lightning.pytorch"]
        PTLMode["PACKAGE_NAME=pytorch<br/>Tests standalone PL<br/>Import: pytorch_lightning"]
        FabricMode["PACKAGE_NAME=fabric<br/>Tests standalone Fabric<br/>Import: lightning_fabric"]
    end
    
    subgraph "Package Isolation"
        UninstallPTL["Uninstall pytorch-lightning<br/>when testing lightning"]
        UninstallLightning["Uninstall lightning<br/>when testing pytorch/fabric"]
    end
    
    TestsPTL --> CopyReplace
    TestsFabric --> CopyReplace
    
    CopyReplace --> Mapping
    
    Mapping -.->|PACKAGE_NAME=lightning| LightningMode
    Mapping -.->|PACKAGE_NAME=pytorch| PTLMode
    Mapping -.->|PACKAGE_NAME=fabric| FabricMode
    
    LightningMode --> UninstallPTL
    PTLMode --> UninstallLightning
    FabricMode --> UninstallLightning
    
    style CopyReplace fill:#f9f9f9
    style Mapping fill:#f9f9f9
```

**Diagram: Import Conversion Strategy** - The `assistant.py` script enables testing multiple package distributions from a single test codebase by dynamically converting import statements.

Sources: [.github/workflows/ci-tests-pytorch.yml:159-165](), [.github/workflows/ci-tests-fabric.yml:136-140](), [.actions/assistant.py:237-323](), [.lightning/workflows/pytorch.yml:111-120]()

### assistant.py Helper Script

The `.actions/assistant.py` script provides critical development utilities:

**Core Functions:**

| Function | Purpose | Usage in CI |
|----------|---------|-------------|
| `copy_replace_imports()` | Convert imports between package namespaces | [.github/workflows/ci-tests-pytorch.yml:162-164]() |
| `load_requirements()` | Parse and adjust requirement files | [.actions/assistant.py:132-148]() |
| `prune_pytest_as_errors()` | Remove warning-as-error filters for oldest tests | [.github/workflows/ci-tests-pytorch.yml:106]() |
| `convert_version2nightly()` | Transform version to nightly format | [.github/workflows/release-nightly.yml:34]() |
| `pull_docs_files()` | Download external documentation pages | [.actions/assistant.py:361-418]() |

```mermaid
graph LR
    subgraph "Import Replacement Pattern"
        SourceCode["Test file with:<br/>from lightning.pytorch import Trainer"]
        RegexReplace["_replace_imports()<br/>regex: ([^_/@]|^)lightning.pytorch([^_\w/]|$)"]
        TargetCode["Modified file:<br/>from pytorch_lightning import Trainer"]
    end
    
    subgraph "Additional Transformations"
        BasePkg["Also replace base package:<br/>from lightning import __version__"]
        StandalonePkg["Becomes:<br/>from pytorch_lightning import __version__"]
    end
    
    SourceCode --> RegexReplace
    RegexReplace --> TargetCode
    TargetCode --> BasePkg
    BasePkg --> StandalonePkg
    
    style RegexReplace fill:#f9f9f9
```

**Diagram: Import Replacement Mechanism** - Regex-based pattern matching ensures complete import conversion while avoiding false positives.

Sources: [.actions/assistant.py:237-282](), [.actions/assistant.py:344-358]()

## Package Build and Release Pipeline

The repository uses a modular workflow system for building and releasing packages:

```mermaid
graph TB
    subgraph "Build Trigger"
        PREvent["Pull Request<br/>(validation only)"]
        PushEvent["Push to master/release/*"]
        ReleaseEvent["GitHub Release Published"]
    end
    
    subgraph "Package Building: _build-packages.yml"
        BuildMatrix["Matrix: [lightning, fabric, pytorch]"]
        PkgCheck[".github/actions/pkg-check<br/>Build wheel + sdist"]
        Validate["Validate package metadata<br/>Check import paths"]
        ArtifactUpload["Upload to artifact:<br/>dist-packages-{sha}"]
    end
    
    subgraph "Package Installation Testing"
        InstallMatrix["Matrix: OS x pkg-name x Python"]
        InstallWheel["Install from wheel"]
        InstallArchive["Install from tar.gz"]
        DocTest["Run package doctests"]
    end
    
    subgraph "Release: release-pkg.yml"
        VersionExtract["Extract version from installed package"]
        CheckpointGen["Generate legacy checkpoint<br/>_legacy-checkpoints.yml"]
        PyPITest["Publish to test.pypi.org"]
        PyPIProd["Publish to pypi.org"]
    end
    
    PREvent --> BuildMatrix
    PushEvent --> BuildMatrix
    ReleaseEvent --> BuildMatrix
    
    BuildMatrix --> PkgCheck
    PkgCheck --> Validate
    Validate --> ArtifactUpload
    
    ArtifactUpload --> InstallMatrix
    InstallMatrix --> InstallWheel
    InstallMatrix --> InstallArchive
    InstallWheel --> DocTest
    InstallArchive --> DocTest
    
    ReleaseEvent --> VersionExtract
    VersionExtract --> CheckpointGen
    VersionExtract --> PyPITest
    PyPITest --> PyPIProd
    
    style PkgCheck fill:#f9f9f9
    style CheckpointGen fill:#f9f9f9
```

**Diagram: Package Build and Release Flow** - Shows the progression from building packages through validation and eventual PyPI publication.

Sources: [.github/workflows/_build-packages.yml:1-71](), [.github/workflows/ci-pkg-install.yml:1-120](), [.github/workflows/release-pkg.yml:1-191]()

### Build Artifacts Structure

After building, artifacts are organized as:

```
dist-packages-{sha}/
├── lightning/
│   ├── lightning-{version}-py3-none-any.whl
│   └── lightning-{version}.tar.gz
├── pytorch/
│   ├── pytorch_lightning-{version}-py3-none-any.whl
│   └── pytorch_lightning-{version}.tar.gz
└── fabric/
    ├── lightning_fabric-{version}-py3-none-any.whl
    └── lightning_fabric-{version}.tar.gz
```

Sources: [.github/workflows/_build-packages.yml:40-48]()

## UV Package Manager Integration

The CI system uses `uv` as a fast, modern Python package installer instead of `pip`:

**Key Features:**
- **Cache Management**: `uv cache prune --ci` minimizes cache size after tests ([.github/workflows/ci-tests-pytorch.yml:214-215]())
- **Torch Backend Support**: `UV_TORCH_BACKEND` environment variable selects CPU/CUDA wheels ([.github/workflows/ci-tests-pytorch.yml:72]())
- **Find Links Support**: Prefers CUDA-specific packages from PyTorch index ([.lightning/workflows/pytorch.yml:126-128]())
- **Virtual Environment Activation**: Uses `activate-environment: true` for automatic activation ([.github/workflows/ci-tests-pytorch.yml:76-82]())

```mermaid
graph LR
    subgraph "UV Installation Workflow"
        SetupUV["astral-sh/setup-uv@v7<br/>Install UV + Python"]
        ActivateEnv["activate-environment: true<br/>Auto-activate venv"]
        InstallDeps["uv pip install .[extras]"]
        PruneCache["uv cache prune --ci<br/>Minimize cache size"]
    end
    
    SetupUV --> ActivateEnv
    ActivateEnv --> InstallDeps
    InstallDeps --> PruneCache
    
    style SetupUV fill:#f9f9f9
```

**Diagram: UV Integration Pattern** - Consistent pattern used across all CI workflows for fast dependency installation.

Sources: [.github/workflows/ci-tests-pytorch.yml:76-82](), [.github/workflows/ci-tests-fabric.yml:71-78](), [.lightning/workflows/pytorch.yml:55-71]()

## Coverage Reporting Strategy

The testing infrastructure collects and reports code coverage to Codecov:

**Coverage Scopes:**

| Package Being Tested | Coverage Source | Flags |
|---------------------|-----------------|-------|
| `lightning` | `lightning` | `lightning,cpu,pytest-full,python{ver},pytorch{ver}` |
| `pytorch-lightning` | `pytorch_lightning` | `pytorch_lightning,cpu,pytest-full,python{ver},pytorch{ver}` |
| `lightning-fabric` | `lightning_fabric` | `lightning_fabric,cpu,pytest,python{ver}` |

The scope is dynamically determined:
```python
# Determine coverage scope based on package being tested
python -c "print('COVERAGE_SCOPE=' + str('lightning' if '${{matrix.config.pkg-name}}' == 'lightning' else 'pytorch_lightning'))" >> $GITHUB_ENV
```

Sources: [.github/workflows/ci-tests-pytorch.yml:118-128](), [.github/workflows/ci-tests-fabric.yml:118-126](), [.github/workflows/ci-tests-pytorch.yml:186-212]()

## GPU Testing on Lightning AI Platform

GPU tests run on Lightning AI's infrastructure using custom workflow definitions:

**GPU Test Configuration:**

| Workflow | CUDA Versions | Python Versions | Machines |
|----------|--------------|-----------------|----------|
| `.lightning/workflows/pytorch.yml` | 12.1.1, 12.6.3 | 3.10, 3.12 | L4_X_2 (2x NVIDIA L4) |
| `.lightning/workflows/fabric.yml` | 12.1.1, 12.6.3 | 3.10, 3.12 | L4_X_2 (2x NVIDIA L4) |

```mermaid
graph TB
    subgraph "GPU Environment Setup"
        CUDAImage["CUDA Docker Image<br/>nvidia/cuda:{version}-devel-ubuntu22.04"]
        PythonInstall["Install Python {version}<br/>from deadsnakes PPA"]
        UVInstall["Install UV package manager"]
        VenvCreate["Create virtual environment<br/>uv venv .venv"]
    end
    
    subgraph "Package Installation"
        ParseCUDA["Parse CUDA version from image tag<br/>Extract: 12.6.3 → cu126"]
        SetBackend["export UV_TORCH_BACKEND=cu{MM}"]
        InstallBase["uv pip install .[extras]<br/>--find-links pytorch.org/whl/cu{MM}"]
    end
    
    subgraph "Test Execution"
        StandardTests["pytest tests_pytorch/ -v"]
        StandaloneTests["run_standalone_tests.sh<br/>Multi-process tests"]
        ExamplesTest["run_pl_examples.sh<br/>1 GPU + 2 GPU DDP"]
    end
    
    CUDAImage --> PythonInstall
    PythonInstall --> UVInstall
    UVInstall --> VenvCreate
    
    VenvCreate --> ParseCUDA
    ParseCUDA --> SetBackend
    SetBackend --> InstallBase
    
    InstallBase --> StandardTests
    StandardTests --> StandaloneTests
    StandaloneTests --> ExamplesTest
    
    style ParseCUDA fill:#f9f9f9
    style SetBackend fill:#f9f9f9
```

**Diagram: GPU Test Environment Setup** - Shows the automated environment configuration for GPU testing on Lightning AI platform.

Sources: [.lightning/workflows/pytorch.yml:36-193](), [.lightning/workflows/fabric.yml:36-165](), [.lightning/workflows/pytorch.yml:81-88]()

### Standalone Test Execution

Standalone tests verify multi-process functionality:

```bash
export PL_RUN_STANDALONE_TESTS=1
bash ./run_standalone_tests.sh "tests_pytorch"
```

This script:
1. Identifies test files marked as standalone (containing `@RunIf`)
2. Executes each in a separate process to avoid state pollution
3. Tests distributed training features that require process isolation

Sources: [.lightning/workflows/pytorch.yml:163-168](), [.lightning/workflows/fabric.yml:141-145]()

## Documentation Build System

Documentation is built using Sphinx and deployed to Google Cloud Storage:

```mermaid
graph TB
    subgraph "Build Triggers"
        PRDocs["PR with docs/** changes"]
        PushMaster["Push to master"]
        PushRelease["Push to release/*"]
        Tag["Git tag created"]
    end
    
    subgraph "docs-build.yml: Build Matrix"
        BuildMatrix["Matrix: [fabric, pytorch] x [html, doctest, linkcheck]"]
        SetupEnv["Install UV + Python 3.10"]
        InstallSphinx["Install lai-sphinx-theme from S3"]
        InstallPkg["uv pip install .[all] -r requirements/{pkg}/docs.txt"]
    end
    
    subgraph "Package-Specific Steps"
        PTLNotebooks["pytorch: Install notebooks requirements<br/>_notebooks/.actions/requires.txt"]
        MakeTarget["make {target} --debug --jobs {nproc}<br/>SPHINXOPTS=-W --keep-going"]
    end
    
    subgraph "deploy-docs: Deployment"
        InjectSelector["inject-selector-script.py<br/>Add version selector widget"]
        GCSStable["Upload to gs://lightning-docs-{pkg}/stable<br/>release/* branches"]
        GCSLatest["Upload to gs://lightning-docs-{pkg}/latest<br/>master branch"]
        GCSVersion["Upload to gs://lightning-docs-{pkg}/{version}<br/>git tags"]
    end
    
    PRDocs --> BuildMatrix
    PushMaster --> BuildMatrix
    PushRelease --> BuildMatrix
    Tag --> BuildMatrix
    
    BuildMatrix --> SetupEnv
    SetupEnv --> InstallSphinx
    InstallSphinx --> InstallPkg
    InstallPkg --> PTLNotebooks
    PTLNotebooks --> MakeTarget
    
    MakeTarget --> InjectSelector
    InjectSelector --> GCSStable
    InjectSelector --> GCSLatest
    InjectSelector --> GCSVersion
    
    style MakeTarget fill:#f9f9f9
    style InjectSelector fill:#f9f9f9
```

**Diagram: Documentation Build and Deployment Pipeline** - Shows how documentation is built for both packages and deployed to version-specific paths.

Sources: [.github/workflows/docs-build.yml:1-200](), [.github/workflows/docs-build.yml:143-200]()

### Documentation Paths on GCS

Deployed documentation follows this structure:

| Event | Deployment Path | Purpose |
|-------|----------------|---------|
| Push to `release/*` | `gs://lightning-docs-{pkg}/stable` | Current stable release docs |
| Push to `master` | `gs://lightning-docs-{pkg}/latest` | Development docs from master |
| Git tag/Release | `gs://lightning-docs-{pkg}/{version}` | Version-specific archive |

Additionally, zipped archives are stored: `gs://lightning-docs-{pkg}/{version}.zip`

Sources: [.github/workflows/docs-build.yml:172-199]()

## Legacy Checkpoint System

The repository maintains backward compatibility by testing against checkpoints created with previous PyTorch Lightning versions:

```mermaid
graph TB
    subgraph "Checkpoint Generation"
        TriggerEvent["Workflow: _legacy-checkpoints.yml<br/>Manual dispatch or called from release"]
        InstallPL["Install specific PL version<br/>or from source"]
        RunScript["generate_checkpoints.sh<br/>Create checkpoint with current code"]
        UploadArtifact["Upload to GitHub Actions artifact"]
    end
    
    subgraph "S3 Storage"
        ConvertImports["Convert imports to standalone<br/>if testing pytorch package"]
        SyncS3["aws s3 sync checkpoints/<br/>to s3://pl-public-data/legacy/checkpoints/"]
        CreateZip["Create checkpoints.zip<br/>Upload to S3 with public-read ACL"]
    end
    
    subgraph "Testing Integration"
        PullCheckpoints[".actions/pull_legacy_checkpoints.sh<br/>Download from S3 before tests"]
        BackCompatVersions["tests/legacy/back-compatible-versions.txt<br/>List of versions to test"]
        TestLoad["Tests verify checkpoint loading<br/>from each version"]
    end
    
    subgraph "Automated PR Creation"
        CreatePR["Create PR to add new version<br/>to back-compatible-versions.txt"]
    end
    
    TriggerEvent --> InstallPL
    InstallPL --> RunScript
    RunScript --> UploadArtifact
    
    UploadArtifact --> ConvertImports
    ConvertImports --> SyncS3
    SyncS3 --> CreateZip
    
    CreateZip -.->|During CI| PullCheckpoints
    PullCheckpoints --> BackCompatVersions
    BackCompatVersions --> TestLoad
    
    CreateZip -.->|If create_pr=true| CreatePR
    
    style RunScript fill:#f9f9f9
    style SyncS3 fill:#f9f9f9
```

**Diagram: Legacy Checkpoint Workflow** - Ensures backward compatibility by testing against checkpoints from previous releases.

Sources: [.github/workflows/_legacy-checkpoints.yml:1-164](), [.github/workflows/ci-tests-pytorch.yml:169-174]()

The checkpoint generation script creates models with various configurations and saves them:
- Location: `tests/legacy/checkpoints/{version}/`
- Pulled during CI: [.github/workflows/ci-tests-pytorch.yml:169-174]()
- S3 bucket: `s3://pl-public-data/legacy/checkpoints/`

Sources: [.github/workflows/_legacy-checkpoints.yml:90-103](), [.github/workflows/_legacy-checkpoints.yml:123-134]()

## Environment Variable Configuration

Key environment variables used across CI workflows:

| Variable | Purpose | Example Values |
|----------|---------|---------------|
| `PACKAGE_NAME` | Determines which package to build/test | `lightning`, `pytorch`, `fabric` |
| `FREEZE_REQUIREMENTS` | Whether to use frozen versions | `1` on release branches, `0` on master |
| `TORCH_URL` | PyTorch wheel index URL | `https://download.pytorch.org/whl/cpu/` |
| `TORCH_URL_TEST` | PyTorch test/nightly builds | `https://download.pytorch.org/whl/test/cpu/` |
| `UV_TORCH_BACKEND` | CUDA version for UV | `cpu`, `cu121`, `cu126` |
| `COVERAGE_SCOPE` | Source path for coverage | `lightning`, `pytorch_lightning`, `lightning_fabric` |
| `DISABLE_MPS` | Disable MPS tests on macOS | `1` on macOS-14 |
| `RUN_ONLY_CUDA_TESTS` | Skip CPU-only tests on GPU runners | `1` |
| `PL_RUN_STANDALONE_TESTS` | Enable standalone test mode | `1` |

Sources: [.github/workflows/ci-tests-pytorch.yml:64-128](), [.lightning/workflows/pytorch.yml:25-34](), [.github/workflows/ci-tests-fabric.yml:60-126]()

## Nightly Release Process

Weekly nightly builds are published every Sunday:

**Workflow Steps:**
1. Convert version to nightly format: `X.Y.Z` → `X.Y.Z.devYYYYMMDD`
2. Build package with nightly version
3. Publish to both test.pypi.org and pypi.org

```python
# Version conversion in assistant.py
timestamp = datetime.now().strftime("%Y%m%d")
version = f"{'.'.join(vers.groups())}.dev{timestamp}"
```

Sources: [.github/workflows/release-nightly.yml:1-69](), [.actions/assistant.py:430-442]()

## Best Practices for Contributors

**Before Submitting a PR:**
1. Run tests locally for the package you're modifying
2. If changing imports, verify both `lightning` and standalone packages work
3. Update documentation if adding/changing public APIs
4. Run `mypy` if modifying type annotations

**Testing Locally:**
```bash
# Test PyTorch Lightning
PACKAGE_NAME=pytorch pytest tests/tests_pytorch/

# Test with import conversion
python .actions/assistant.py copy_replace_imports \
    --source_dir="./tests" \
    --source_import="lightning.pytorch" \
    --target_import="pytorch_lightning"
```

**Understanding CI Failures:**
- Check `checkgroup.yml` to see which checks are required for your changes
- Guardian jobs (`pl-cpu-guardian`, etc.) aggregate matrix results - check individual job logs
- GPU test logs are in Lightning AI platform - linked from GitHub checks

Sources: [.github/checkgroup.yml:1-197](), [.actions/assistant.py:344-358]()

---

