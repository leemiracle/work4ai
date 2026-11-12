<!-- source: DeepWiki mcp.deepwiki.com · repo Project-MONAI/MONAI · page 7 Development and Infrastructure · fetched 2026-10-21 -->

# Development and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/blossom-ci.yml](.github/workflows/blossom-ci.yml)
- [.github/workflows/codeql-analysis.yml](.github/workflows/codeql-analysis.yml)
- [.github/workflows/conda.yml](.github/workflows/conda.yml)
- [.github/workflows/cron-ngc-bundle.yml](.github/workflows/cron-ngc-bundle.yml)
- [.github/workflows/cron.yml](.github/workflows/cron.yml)
- [.github/workflows/docker.yml](.github/workflows/docker.yml)
- [.github/workflows/integration.yml](.github/workflows/integration.yml)
- [.github/workflows/pythonapp-gpu.yml](.github/workflows/pythonapp-gpu.yml)
- [.github/workflows/pythonapp-min.yml](.github/workflows/pythonapp-min.yml)
- [.github/workflows/pythonapp.yml](.github/workflows/pythonapp.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.github/workflows/setupapp.yml](.github/workflows/setupapp.yml)
- [.github/workflows/weekly-preview.yml](.github/workflows/weekly-preview.yml)
- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [Dockerfile](Dockerfile)
- [docs/requirements.txt](docs/requirements.txt)
- [docs/source/conf.py](docs/source/conf.py)
- [docs/source/installation.md](docs/source/installation.md)
- [environment-dev.yml](environment-dev.yml)
- [monai/config/deviceconfig.py](monai/config/deviceconfig.py)
- [pyproject.toml](pyproject.toml)
- [requirements-dev.txt](requirements-dev.txt)
- [requirements.txt](requirements.txt)
- [runtests.sh](runtests.sh)
- [setup.cfg](setup.cfg)

</details>



This page documents MONAI's development infrastructure, including local development setup, testing systems, continuous integration/continuous deployment (CI/CD) pipelines, code quality enforcement, and distribution mechanisms. This infrastructure ensures code quality, maintains backward compatibility, and enables reliable distribution across multiple package managers.

For detailed information on specific aspects:
- Installation options and dependency management: see [Project Setup and Dependencies](#7.1)
- CI/CD workflows and testing strategies: see [CI/CD Workflows and Testing](#7.2)
- Release process and packaging: see [Packaging and Distribution](#7.3)

## Development Workflow Overview

MONAI follows a GitHub-based development workflow with automated quality gates at every stage. The workflow spans from local development through automated testing to final distribution.

**Development Workflow Stages**

```mermaid
graph TB
    subgraph "Local Development"
        LocalCode["Local Code Changes"]
        LocalTest["./runtests.sh<br/>--codeformat<br/>--autofix<br/>--unittests"]
        LocalBuild["BUILD_MONAI=1<br/>python setup.py develop"]
    end
    
    subgraph "Pre-merge Validation"
        PR["Pull Request"]
        PreMerge["pythonapp.yml<br/>Quick Tests<br/>Packaging<br/>Docs Build"]
        PreMergeGPU["pythonapp-gpu.yml<br/>GPU Tests<br/>(Disabled)"]
        PreMergeMin["pythonapp-min.yml<br/>Min Dependencies"]
    end
    
    subgraph "Post-merge Testing"
        Merge["Merge to dev"]
        PostMerge["setupapp.yml<br/>Coverage Tests<br/>Multiple Python/PyTorch"]
        Nightly["cron.yml<br/>CUDA Combinations<br/>Tutorial Notebooks"]
    end
    
    subgraph "Distribution"
        Release["Git Tag"]
        ReleaseWorkflow["release.yml<br/>Build Packages"]
        PyPI["PyPI"]
        CondaForge["conda-forge"]
        Docker["Docker Hub"]
        Weekly["weekly-preview.yml<br/>monai-weekly"]
    end
    
    LocalCode --> LocalTest
    LocalTest --> LocalBuild
    LocalBuild --> PR
    PR --> PreMerge
    PR --> PreMergeGPU
    PR --> PreMergeMin
    PreMerge --> Merge
    PreMergeGPU --> Merge
    PreMergeMin --> Merge
    Merge --> PostMerge
    PostMerge --> Nightly
    PostMerge --> Weekly
    Merge --> Release
    Release --> ReleaseWorkflow
    ReleaseWorkflow --> PyPI
    ReleaseWorkflow --> CondaForge
    ReleaseWorkflow --> Docker
```

**Sources:** [.github/workflows/pythonapp.yml](), [.github/workflows/setupapp.yml](), [.github/workflows/cron.yml](), [.github/workflows/release.yml](), [.github/workflows/weekly-preview.yml](), [CONTRIBUTING.md]()

## Testing Infrastructure

MONAI's testing infrastructure is orchestrated through the `runtests.sh` script, which provides a unified interface for all testing and code quality operations.

**Testing Script Architecture**

```mermaid
graph TB
    subgraph "runtests.sh Command Options"
        Script["./runtests.sh"]
        
        CodeFormat["--codeformat<br/>--black --isort<br/>--flake8 --ruff"]
        TypeCheck["--pytype --mypy<br/>-j NUM_PARALLEL"]
        AutoFix["--autofix<br/>Automatic Formatting"]
        
        UnitTests["--unittests<br/>Exclude integration_*"]
        DistTests["--disttests<br/>Distributed GPU tests<br/>*_dist.py files"]
        NetTests["--net<br/>Integration tests"]
        MinTests["--min<br/>Minimal dependencies<br/>tests/min_tests.py"]
        QuickTests["--quick<br/>QUICKTEST=True"]
        
        Coverage["--coverage<br/>coverage run --append"]
        Build["--build<br/>Compile C++/CUDA<br/>extensions"]
        Clean["--clean<br/>Cleanup artifacts"]
    end
    
    subgraph "Test Execution"
        Runner["tests/runner.py"]
        UnitTestFiles["test_*.py<br/>(excluding _dist)"]
        DistTestFiles["test_*_dist.py"]
        IntegrationTests["tests/integration/*.py"]
        MinimalTests["tests/min_tests.py"]
    end
    
    Script --> CodeFormat
    Script --> TypeCheck
    Script --> AutoFix
    Script --> UnitTests
    Script --> DistTests
    Script --> NetTests
    Script --> MinTests
    Script --> QuickTests
    Script --> Coverage
    Script --> Build
    Script --> Clean
    
    UnitTests --> Runner
    Runner --> UnitTestFiles
    DistTests --> DistTestFiles
    NetTests --> IntegrationTests
    MinTests --> MinimalTests
```

**Sources:** [runtests.sh:1-770]()

### Test Categories

| Test Type | Command | Description | Files |
|-----------|---------|-------------|-------|
| Unit Tests | `./runtests.sh --unittests` | Core functionality tests, excludes integration | `test_[module].py` (excluding `_dist`) |
| Distributed Tests | `./runtests.sh --disttests` | Multi-GPU distributed tests | `test_*_dist.py` |
| Integration Tests | `./runtests.sh --net` | Network training/inference workflows | `tests/integration/*.py` |
| Minimal Tests | `./runtests.sh --min` | Tests with minimal dependencies only | `tests/min_tests.py` |
| Quick Tests | `./runtests.sh --quick` | Subset of unit tests for rapid validation | Unit tests with `QUICKTEST=True` |

**Sources:** [runtests.sh:62-119](), [runtests.sh:719-749](), [CONTRIBUTING.md:102-150]()

### Code Quality Tools

MONAI enforces code quality through multiple linters and formatters configured in [setup.cfg]() and [pyproject.toml]().

**Code Quality Tool Chain**

| Tool | Purpose | Configuration | Command |
|------|---------|---------------|---------|
| **black** | Code formatter | [pyproject.toml:11-35]() | `./runtests.sh --black` |
| **isort** | Import sorter | [setup.cfg:212-219]() | `./runtests.sh --isort` |
| **flake8** | Style checker | [setup.cfg:182-210]() | `./runtests.sh --flake8` |
| **ruff** | Fast linter | [pyproject.toml:41-56]() | `./runtests.sh --ruff` |
| **mypy** | Static type checker | [setup.cfg:229-276]() | `./runtests.sh --mypy` |
| **pytype** | Type inference | [pyproject.toml:58-88]() | `./runtests.sh --pytype -j 2` |
| **pre-commit** | Git hooks | `.pre-commit-config.yaml` | `./runtests.sh --precommit` |

**Sources:** [setup.cfg:182-276](), [pyproject.toml:11-88](), [runtests.sh:441-679]()

### Test Execution Flow

```mermaid
flowchart LR
    subgraph "Local Execution"
        Dev["Developer"]
        RunTests["./runtests.sh<br/>-f -u --net<br/>--coverage"]
    end
    
    subgraph "Test Runner"
        CmdPrefix["cmdPrefix<br/>(dryrun or execute)"]
        CheckImport["check_import()<br/>import monai"]
        CompileCpp["compile_cpp()<br/>BUILD_MONAI=1<br/>setup.py develop"]
    end
    
    subgraph "Code Quality"
        IsortCheck["isort --check"]
        BlackCheck["black --check"]
        Flake8["flake8 --count"]
        RuffCheck["ruff check"]
        MypyCheck["mypy"]
        PytypeCheck["pytype -j N"]
    end
    
    subgraph "Test Execution"
        TorchValidate["torch_validate()<br/>torch.__version__"]
        CoverageRun["coverage run --append"]
        TestRunner["tests/runner.py<br/>-p pattern"]
        DistRunner["test_*_dist.py"]
        IntegrationRunner["tests/integration/*.py"]
    end
    
    subgraph "Reporting"
        CoverageCombine["coverage combine"]
        CoverageReport["coverage report"]
        CoverageXML["coverage xml"]
    end
    
    Dev --> RunTests
    RunTests --> CmdPrefix
    CmdPrefix --> CheckImport
    CmdPrefix --> CompileCpp
    
    RunTests --> IsortCheck
    RunTests --> BlackCheck
    RunTests --> Flake8
    RunTests --> RuffCheck
    RunTests --> MypyCheck
    RunTests --> PytypeCheck
    
    RunTests --> TorchValidate
    TorchValidate --> CoverageRun
    CoverageRun --> TestRunner
    CoverageRun --> DistRunner
    CoverageRun --> IntegrationRunner
    
    TestRunner --> CoverageCombine
    DistRunner --> CoverageCombine
    IntegrationRunner --> CoverageCombine
    CoverageCombine --> CoverageReport
    CoverageReport --> CoverageXML
```

**Sources:** [runtests.sh:128-770](), [CONTRIBUTING.md:52-150]()

## Continuous Integration Pipelines

MONAI uses GitHub Actions for CI/CD, with workflows organized by trigger event and purpose.

**CI/CD Workflow Organization**

```mermaid
graph TB
    subgraph "Pre-merge Workflows"
        PullRequest["Pull Request"]
        
        PreMerge["pythonapp.yml<br/>flake8-py3: codeformat, pytype, mypy<br/>quick-py3: Windows, macOS, Ubuntu<br/>packaging: sdist, wheel validation<br/>build-docs: Sphinx documentation"]
        
        PreMergeGPU["pythonapp-gpu.yml<br/>GPU-quick-py3<br/>PT2.3.0-2.5.0 + CUDA<br/>(Currently disabled)"]
        
        PreMergeMin["pythonapp-min.yml<br/>min-dep-os: Windows, macOS, Ubuntu<br/>min-dep-py3: Python 3.9-3.12<br/>min-dep-pytorch: PyTorch 2.5-2.8"]
    end
    
    subgraph "Post-merge Workflows"
        DevBranch["Push to dev/main"]
        
        PostMerge["setupapp.yml<br/>coverage-py3: GPU coverage tests<br/>test-py3x: Python 3.9-3.11<br/>install: pip install from GitHub"]
        
        Docker["docker.yml<br/>versioning_dev<br/>docker_build_dev<br/>docker_test_dockerhub<br/>(Currently disabled)"]
    end
    
    subgraph "Scheduled Workflows"
        Schedule["Cron Schedule"]
        
        Nightly["cron.yml<br/>Daily 02:00 UTC<br/>cron-gpu: PT+CUDA combinations<br/>cron-pt-image: NVIDIA containers<br/>cron-pip: pip install test<br/>cron-docker: Docker image test<br/>cron-tutorial-notebooks"]
        
        WeeklyPreview["weekly-preview.yml<br/>Sunday 02:00 UTC<br/>monai-weekly PyPI release"]
        
        Conda["conda.yml<br/>Daily 03:00 UTC<br/>environment-dev.yml testing"]
        
        NgcBundle["cron-ngc-bundle.yml<br/>Daily 02:00 UTC<br/>NGC bundle loading test"]
    end
    
    subgraph "Release Workflows"
        GitTag["Git Tag"]
        
        Release["release.yml<br/>packaging: Python 3.9-3.11<br/>versioning: _version.py<br/>release_tag_docker<br/>(Docker disabled)"]
    end
    
    PullRequest --> PreMerge
    PullRequest --> PreMergeGPU
    PullRequest --> PreMergeMin
    
    DevBranch --> PostMerge
    DevBranch --> Docker
    
    Schedule --> Nightly
    Schedule --> WeeklyPreview
    Schedule --> Conda
    Schedule --> NgcBundle
    
    GitTag --> Release
```

**Sources:** [.github/workflows/pythonapp.yml](), [.github/workflows/pythonapp-gpu.yml](), [.github/workflows/pythonapp-min.yml](), [.github/workflows/setupapp.yml](), [.github/workflows/cron.yml](), [.github/workflows/weekly-preview.yml](), [.github/workflows/release.yml]()

### Pre-merge Validation Strategy

The pre-merge validation runs three parallel workflows to provide fast feedback:

**pythonapp.yml** performs comprehensive checks:
- **Code formatting** (flake8-py3 job): Runs `codeformat`, `pytype`, and `mypy` checks in parallel using matrix strategy
- **Cross-platform tests** (quick-py3 job): Tests on Windows, macOS, and Ubuntu with Python 3.9
- **Packaging validation** (packaging job): Builds sdist and wheel, tests installation from both
- **Documentation** (build-docs job): Builds Sphinx HTML documentation

**pythonapp-min.yml** validates minimal dependency configurations:
- **min-dep-os**: Tests with minimal requirements on Windows, macOS, Ubuntu
- **min-dep-py3**: Tests Python 3.9, 3.10, 3.11, 3.12 compatibility
- **min-dep-pytorch**: Tests PyTorch 2.5.1, 2.6.0, 2.7.1, 2.8.0 compatibility

**pythonapp-gpu.yml** (currently disabled) validates GPU functionality with multiple PyTorch+CUDA combinations.

**Sources:** [.github/workflows/pythonapp.yml:1-204](), [.github/workflows/pythonapp-min.yml:1-171](), [.github/workflows/pythonapp-gpu.yml:1-131]()

### Post-merge and Nightly Testing

**Post-merge workflows** provide deeper validation:
- Coverage tests with full GPU access
- Multiple Python versions (3.9, 3.10, 3.11)
- Direct GitHub installation testing

**Nightly cron workflows** provide exhaustive validation:
- **cron-gpu**: Tests multiple PyTorch/CUDA combinations (PT2.3.0+CUDA12.1, PT2.4.0+CUDA12.6, latest)
- **cron-pt-image**: Tests against NVIDIA PyTorch container images (23.08, 24.08, 24.10)
- **cron-pip**: Validates `pip install` from source with full test suite
- **cron-docker**: Tests the official Docker image
- **cron-tutorial-notebooks**: Executes all tutorial notebooks from `Project-MONAI/tutorials`

**Sources:** [.github/workflows/setupapp.yml:1-175](), [.github/workflows/cron.yml:1-267]()

## Build and Compilation System

MONAI includes optional C++/CUDA extensions for performance-critical operations. The build system is controlled through environment variables.

**Build Configuration**

| Environment Variable | Effect | Default |
|---------------------|--------|---------|
| `BUILD_MONAI` | Enable compilation of C++/CUDA extensions | `0` (disabled) |
| `FORCE_CUDA` | Force CUDA compilation even if not auto-detected | `0` (auto-detect) |
| `TORCH_CUDA_ARCH_LIST` | Specify CUDA architectures to compile for | PyTorch default |

**Build Process**

```mermaid
graph LR
    subgraph "Build Triggers"
        SetupPy["setup.py"]
        BuildEnv["BUILD_MONAI=1"]
        ForceCuda["FORCE_CUDA=1"]
    end
    
    subgraph "Build System"
        Versioneer["versioneer.py<br/>Version generation"]
        SetupCfg["setup.cfg<br/>Package metadata"]
        PyProjectToml["pyproject.toml<br/>Build requirements:<br/>torch, ninja, packaging"]
    end
    
    subgraph "Compilation"
        CppExtensions["monai/csrc/<br/>monai/_extensions/"]
        Ninja["ninja build tool"]
        CudaToolkit["CUDA Toolkit"]
        TorchCuda["torch.cuda.is_available()"]
    end
    
    subgraph "Installation"
        Develop["python setup.py develop"]
        Install["pip install"]
        UseCompiled["USE_COMPILED=True<br/>HAS_EXT=True"]
    end
    
    SetupPy --> BuildEnv
    SetupPy --> ForceCuda
    BuildEnv --> Versioneer
    BuildEnv --> SetupCfg
    SetupCfg --> PyProjectToml
    
    PyProjectToml --> Ninja
    PyProjectToml --> TorchCuda
    TorchCuda --> CudaToolkit
    
    Ninja --> CppExtensions
    CudaToolkit --> CppExtensions
    
    CppExtensions --> Develop
    CppExtensions --> Install
    Develop --> UseCompiled
    Install --> UseCompiled
```

The compilation status is exposed through `monai.config`:
- `HAS_EXT`: Whether extensions were successfully imported
- `USE_COMPILED`: Whether extensions are currently in use (`HAS_EXT and os.getenv("BUILD_MONAI") == "1"`)

**Sources:** [setup.cfg:35-46](), [pyproject.toml:1-9](), [monai/config/deviceconfig.py:30-34](), [runtests.sh:142-153](), [Dockerfile:48-49]()

## Documentation System

MONAI uses Sphinx for documentation generation with automatic API documentation via `sphinx-apidoc`.

**Documentation Build Pipeline**

```mermaid
graph TB
    subgraph "Source Files"
        RstFiles["docs/source/*.rst"]
        MdFiles["docs/source/*.md"]
        CodeDocstrings["Python docstrings<br/>Google style"]
        ConfPy["docs/source/conf.py"]
    end
    
    subgraph "Generation"
        GenerateApidocs["generate_apidocs()<br/>builder-inited hook"]
        SphinxApidoc["sphinx-apidoc -e -o<br/>docs/source/apidocs<br/>monai/"]
        PropertiesCSV["Train/Infer/MetaProperties<br/>*.csv files"]
    end
    
    subgraph "Build Process"
        SphinxBuild["make html<br/>sphinx-build"]
        Templates["_templates/"]
        StaticFiles["_static/"]
        Theme["pydata_sphinx_theme"]
    end
    
    subgraph "Output"
        HtmlDocs["docs/build/html/"]
        ReadTheDocs["docs.monai.io"]
        Linkcode["linkcode_resolve()<br/>GitHub source links"]
    end
    
    RstFiles --> SphinxBuild
    MdFiles --> SphinxBuild
    CodeDocstrings --> GenerateApidocs
    ConfPy --> GenerateApidocs
    
    GenerateApidocs --> SphinxApidoc
    GenerateApidocs --> PropertiesCSV
    SphinxApidoc --> SphinxBuild
    
    Templates --> SphinxBuild
    StaticFiles --> SphinxBuild
    Theme --> SphinxBuild
    
    SphinxBuild --> HtmlDocs
    HtmlDocs --> ReadTheDocs
    ConfPy --> Linkcode
    Linkcode --> ReadTheDocs
```

**Documentation Configuration**

Key extensions enabled in [docs/source/conf.py:94-104]():
- `sphinx.ext.autodoc`: Auto-generate API docs from docstrings
- `sphinx.ext.napoleon`: Support Google-style docstrings
- `sphinx.ext.linkcode`: Link to source code on GitHub
- `sphinx.ext.autosummary`: Generate summary tables
- `sphinx_autodoc_typehints`: Include type hints in docs
- `recommonmark`: Support Markdown files

The `linkcode_resolve()` function [docs/source/conf.py:191-223]() generates GitHub source links based on the git reference:
- Uses `READTHEDOCS_GIT_IDENTIFIER` for ReadTheDocs builds
- Uses `GITHUB_SHA` for CI builds
- Falls back to `dev` branch

**Sources:** [docs/source/conf.py:1-224](), [docs/requirements.txt:1-46](), [CONTRIBUTING.md:154-182](), [.github/workflows/pythonapp.yml:182-203]()

## Dependency Management

MONAI uses a tiered dependency system to support flexible deployment scenarios.

**Dependency Hierarchy**

```mermaid
graph TB
    subgraph "Core Requirements"
        CoreReq["requirements.txt<br/>torch>=2.4.1<br/>numpy>=1.24,<3.0"]
    end
    
    subgraph "Minimal Requirements"
        MinReq["requirements-min.txt<br/>(links to requirements.txt)"]
    end
    
    subgraph "Development Requirements"
        DevReq["requirements-dev.txt<br/>Includes requirements-min.txt<br/>+ testing tools<br/>+ linting tools<br/>+ optional dependencies"]
    end
    
    subgraph "Documentation Requirements"
        DocsReq["docs/requirements.txt<br/>Sphinx packages<br/>+ selected optional deps"]
    end
    
    subgraph "Conda Environment"
        CondaEnv["environment-dev.yml<br/>pytorch, numpy<br/>+ pip: requirements-dev.txt"]
    end
    
    subgraph "Setup Configuration"
        SetupCfg["setup.cfg<br/>[options.extras_require]<br/>all, nibabel, scipy, etc."]
        PyProjectToml["pyproject.toml<br/>[build-system]<br/>requires"]
    end
    
    CoreReq --> MinReq
    MinReq --> DevReq
    CoreReq --> DocsReq
    CoreReq --> SetupCfg
    
    DevReq --> CondaEnv
    
    SetupCfg -.->|defines| ExtrasRequire["pip install monai[all]<br/>pip install monai[nibabel,scipy]"]
    PyProjectToml -.->|defines| BuildDeps["Build-time dependencies"]
```

**Optional Dependencies Structure**

The [setup.cfg:48-178]() defines granular optional dependencies:
- Individual packages: `nibabel`, `scipy`, `pillow`, `tensorboard`, etc.
- Feature groups: `[all]` includes all optional dependencies
- Platform-specific: `cucim-cu12` only on Linux, `imagecodecs`/`tifffile` on Linux/Darwin

Example extras:
```
pip install monai[nibabel,skimage]  # Specific features
pip install monai[all]               # All optional dependencies
```

**Sources:** [requirements.txt:1-4](), [requirements-dev.txt:1-67](), [setup.cfg:44-178](), [docs/requirements.txt:1-46](), [environment-dev.yml:1-16](), [pyproject.toml:1-9]()

## Version Management

MONAI uses `versioneer` for automatic version string generation based on git tags.

**Version String Components**

A typical version string like `0.1.0+144.g52c763d.dirty` contains:
- `0.1.0`: Base milestone version
- `+144`: Number of commits ahead of the milestone
- `g52c763d`: Git commit hash
- `dirty`: Local modifications present

**Version Information Access**

```mermaid
graph LR
    subgraph "Version Sources"
        GitDescribe["git describe"]
        VersioneerPy["versioneer.py"]
        SetupPy["setup.py"]
    end
    
    subgraph "Generated Files"
        VersionPy["monai/_version.py<br/>Auto-generated"]
    end
    
    subgraph "Runtime Access"
        MonaiVersion["monai.__version__"]
        MonaiRevisionId["monai.__revision_id__"]
        MonaiFile["monai.__file__"]
        PrintConfig["monai.config.print_config()"]
    end
    
    GitDescribe --> VersioneerPy
    VersioneerPy --> SetupPy
    SetupPy --> VersionPy
    
    VersionPy --> MonaiVersion
    VersionPy --> MonaiRevisionId
    MonaiVersion --> PrintConfig
    MonaiRevisionId --> PrintConfig
    MonaiFile --> PrintConfig
```

The configuration is defined in [setup.cfg:221-227]():
```
[versioneer]
VCS = git
style = pep440
versionfile_source = monai/_version.py
versionfile_build = monai/_version.py
tag_prefix =
parentdir_prefix =
```

**Sources:** [setup.cfg:221-227](), [docs/source/installation.md:180-191](), [monai/config/deviceconfig.py:95-117]()

## Docker Infrastructure

MONAI provides official Docker images built from the NVIDIA PyTorch base image.

**Docker Build Process**

The [Dockerfile]() follows this structure:
1. **Base image**: `nvcr.io/nvidia/pytorch:24.10-py3` (PyTorch 2.5.0, CUDA 12.6)
2. **Dependencies**: Installs `requirements-dev.txt` (excluding torch to avoid conflicts)
3. **Source code**: Copies source and builds with `BUILD_MONAI=1 FORCE_CUDA=1`
4. **NGC CLI**: Installs NVIDIA NGC command-line interface
5. **Additional tools**: Installs `libopenslide0` and sets up `POLYGRAPHY_AUTOINSTALL_DEPS=1`

**Docker Image Tags**
- `projectmonai/monai:latest` - Dev branch HEAD
- `projectmonai/monai:X.Y.Z` - Tagged releases (disabled in current workflow)

The Docker build workflow is defined in [.github/workflows/docker.yml]() but is currently disabled.

**Sources:** [Dockerfile:1-67](), [.github/workflows/docker.yml:1-106](), [docs/source/installation.md:193-211]()

## Release Process

MONAI follows a structured release process with multiple distribution channels.

**Release Workflow Stages**

```mermaid
graph TB
    subgraph "Trigger"
        DevReady["Features Ready on dev"]
        CreateTag["Create Git Tag<br/>X.Y.Z"]
    end
    
    subgraph "Artifact Building"
        Packaging["release.yml: packaging<br/>Python 3.9, 3.10, 3.11"]
        BuildSdist["python setup.py sdist<br/>monai-X.Y.Z.tar.gz"]
        BuildWheel["python setup.py bdist_wheel<br/>monai-X.Y.Z-py3-none-any.whl"]
        TestInstall["Install and test<br/>both artifacts"]
    end
    
    subgraph "Version File"
        Versioning["release.yml: versioning"]
        ComputeVersion["python setup.py build<br/>Generate _version.py"]
        UploadArtifact["Upload _version.py<br/>as artifact"]
    end
    
    subgraph "Distribution"
        PyPIRelease["PyPI<br/>(via Blossom)"]
        CondaForgeRelease["conda-forge<br/>(via feedstock)"]
        DockerRelease["Docker Hub<br/>(disabled)"]
    end
    
    subgraph "Weekly Preview"
        WeeklyCron["weekly-preview.yml<br/>Sunday 02:00 UTC"]
        ModifySetup["Modify setup.cfg:<br/>name = monai-weekly"]
        TagWeekly["Tag: 1.6.devYYWW"]
        WeeklyPyPI["PyPI: monai-weekly"]
    end
    
    DevReady --> CreateTag
    CreateTag --> Packaging
    CreateTag --> Versioning
    
    Packaging --> BuildSdist
    Packaging --> BuildWheel
    BuildSdist --> TestInstall
    BuildWheel --> TestInstall
    
    Versioning --> ComputeVersion
    ComputeVersion --> UploadArtifact
    
    TestInstall --> PyPIRelease
    TestInstall --> CondaForgeRelease
    TestInstall --> DockerRelease
    
    WeeklyCron --> ModifySetup
    ModifySetup --> TagWeekly
    TagWeekly --> WeeklyPyPI
```

**Weekly Preview Release**

The weekly preview provides early access to development features:
1. Runs every Sunday at 02:00 UTC via [.github/workflows/weekly-preview.yml]()
2. Modifies `setup.cfg` to change package name from `monai` to `monai-weekly`
3. Injects commit ID: `__commit_id__ = "..."` into `monai/__init__.py`
4. Creates a dev tag: `1.6.dev[YYWW]` where `YYWW` is year and ISO week number
5. Publishes to PyPI as `monai-weekly` package

**Sources:** [.github/workflows/release.yml:1-169](), [.github/workflows/weekly-preview.yml:1-79](), [CONTRIBUTING.md:379-395]()

## System Configuration Reporting

MONAI provides utilities to report system and configuration information for debugging.

**Configuration Reporting Functions**

| Function | Purpose | Output |
|----------|---------|--------|
| `monai.config.print_config()` | Print package versions | MONAI, PyTorch, NumPy, optional deps |
| `monai.config.print_system_info()` | Print system information | OS, CPU, memory, disk usage (requires `psutil`) |
| `monai.config.print_gpu_info()` | Print GPU configuration | CUDA version, GPU count, memory, capabilities |
| `monai.config.print_debug_info()` | Print all debugging info | Combines all above |

**Configuration Variables**

Exposed through `monai.config`:
- `USE_COMPILED`: Whether C++/CUDA extensions are in use
- `USE_META_DICT`: Whether MetaDict compatibility mode is enabled (env: `USE_META_DICT=1`)
- `HAS_EXT`: Whether extensions were successfully imported

**Sources:** [monai/config/deviceconfig.py:29-275]()

## Contributing Guidelines

MONAI follows strict contributing guidelines documented in [CONTRIBUTING.md]().

**Key Requirements**

1. **Code Format**: All code must pass `./runtests.sh --codeformat`
2. **Testing**: New features require accompanying tests
3. **Documentation**: Update relevant `.rst` files in `docs/source/`
4. **Backward Compatibility**: Use deprecation warnings, plan for 2 minor versions
5. **DCO Sign-off**: All commits must include `Signed-off-by` line (use `git commit -s`)
6. **Copyright Headers**: All source files must include Apache 2.0 license header

**Pull Request Process**

1. Create branch named `[ticket_id]-[task_name]`
2. Make changes with detailed commit messages
3. Run local tests: `./runtests.sh -f -u --net --coverage`
4. Create pull request with detailed description
5. Address CI/CD failures and review comments
6. Trigger optional tests via comments: `/black`, `/integration-test`
7. Maintainers trigger `/build` for full internal tests
8. Merge after all approvals

**Automatic Code Formatting**

Commenting `/black` on a pull request triggers automatic formatting via [monai-code-formatter](https://github.com/Project-MONAI/monai-code-formatter) GitHub Action using `psf/Black`.

**Sources:** [CONTRIBUTING.md:1-395]()

---

