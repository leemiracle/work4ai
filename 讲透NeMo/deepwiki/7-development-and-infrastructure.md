<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo · page 7 Development and Infrastructure · fetched 2026-10-21 -->

# Development and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.flake8](.flake8)
- [.flake8.other](.flake8.other)
- [.flake8.speech](.flake8.speech)
- [.github/actions/test-template/action.yml](.github/actions/test-template/action.yml)
- [.github/workflows/cicd-main-unit-tests.yml](.github/workflows/cicd-main-unit-tests.yml)
- [.github/workflows/cicd-main.yml](.github/workflows/cicd-main.yml)
- [.github/workflows/cicd-relabel-bot.yml](.github/workflows/cicd-relabel-bot.yml)
- [.github/workflows/code-formatting.yml](.github/workflows/code-formatting.yml)
- [.github/workflows/code-linting.yml](.github/workflows/code-linting.yml)
- [.github/workflows/monitor-single-vm.yml](.github/workflows/monitor-single-vm.yml)
- [.github/workflows/monitor-vms.yml](.github/workflows/monitor-vms.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [.pylintrc](.pylintrc)
- [.pylintrc.other](.pylintrc.other)
- [.pylintrc.speech](.pylintrc.speech)
- [examples/llm/resiliency/README.md](examples/llm/resiliency/README.md)
- [examples/llm/resiliency/crash_simulator.py](examples/llm/resiliency/crash_simulator.py)
- [examples/llm/resiliency/preemption_simulator.py](examples/llm/resiliency/preemption_simulator.py)
- [examples/llm/resiliency/resiliency-in-pretraining-demo.ipynb](examples/llm/resiliency/resiliency-in-pretraining-demo.ipynb)
- [external/patches/triton-lang_triton_6570_lazy_init.patch](external/patches/triton-lang_triton_6570_lazy_init.patch)
- [nemo/collections/common/data/lhotse/__init__.py](nemo/collections/common/data/lhotse/__init__.py)
- [nemo/collections/llm/recipes/callbacks/__init__.py](nemo/collections/llm/recipes/callbacks/__init__.py)
- [nemo/collections/llm/recipes/callbacks/common.py](nemo/collections/llm/recipes/callbacks/common.py)
- [pyproject.toml](pyproject.toml)
- [requirements/manifest.json](requirements/manifest.json)
- [requirements/requirements.txt](requirements/requirements.txt)
- [requirements/requirements_nlp.txt](requirements/requirements_nlp.txt)
- [requirements/requirements_test.txt](requirements/requirements_test.txt)
- [scripts/installers/install_k2.sh](scripts/installers/install_k2.sh)
- [setup.py](setup.py)
- [tests/lightning/pytorch/callbacks/test_jit_transform.py](tests/lightning/pytorch/callbacks/test_jit_transform.py)

</details>



This document covers the development workflows, continuous integration/continuous deployment (CI/CD) systems, release management processes, and infrastructure components that support the NeMo framework. It provides technical details about how code changes are tested, validated, and deployed, including dependency management, container building, and quality assurance processes.

For information about model export and deployment workflows, see [Model Export and Deployment](#6). For CI/CD pipeline details and testing processes, see [CI/CD Infrastructure and Testing](#7.1). For release management specifics, see [Release Management and Dependency Updates](#7.2).

## CI/CD Pipeline Overview

The NeMo project uses a comprehensive GitHub Actions-based CI/CD system that automatically tests code changes, manages dependencies, and coordinates releases. The main pipeline is defined in [`.github/workflows/cicd-main.yml`]() and orchestrates multiple specialized workflows.

```mermaid
graph TB
    subgraph "CI/CD Entry Points"
        PR["Pull Request"]
        Schedule["Scheduled Build"]
        Manual["Manual Dispatch"]
    end
    
    subgraph "Pre-flight Checks"
        PreFlight["pre-flight job"]
        ComponentSelection["components_to_run.py"]
        TestSelection["test_to_run logic"]
    end
    
    subgraph "Core Pipeline Jobs"
        CodeLinting["code-linting"]
        ContainerBuild["cicd-test-container-build"]
        ImportTests["cicd-import-tests"]
        SetupData["L0_Setup_Test_Data_And_Models"]
    end
    
    subgraph "Test Suites"
        UnitTests["cicd-main-unit-tests"]
        NeMo2Tests["cicd-main-nemo2"]
        ExportDeploy["cicd-main-export-deploy"]
        SpeechTests["cicd-main-speech"]
        AutomodelTests["cicd-main-automodel"]
    end
    
    subgraph "Pipeline Completion"
        ResultAggregation["Nemo_CICD_Test"]
        Coverage["Coverage"]
        Notification["Slack Notifications"]
    end
    
    PR --> PreFlight
    Schedule --> PreFlight
    Manual --> PreFlight
    
    PreFlight --> ComponentSelection
    PreFlight --> TestSelection
    PreFlight --> CodeLinting
    
    CodeLinting --> ContainerBuild
    ContainerBuild --> ImportTests
    ContainerBuild --> SetupData
    
    ContainerBuild --> UnitTests
    UnitTests --> NeMo2Tests
    UnitTests --> ExportDeploy
    UnitTests --> SpeechTests
    UnitTests --> AutomodelTests
    
    NeMo2Tests --> ResultAggregation
    ExportDeploy --> ResultAggregation
    SpeechTests --> ResultAggregation
    AutomodelTests --> ResultAggregation
    
    ResultAggregation --> Coverage
    ResultAggregation --> Notification
```

**Sources:** [`.github/workflows/cicd-main.yml:37-497`]()

## Container Infrastructure and Build System

The NeMo CI/CD system relies heavily on containerized environments to ensure consistent testing and deployment. Container builds are managed through specialized workflows that handle caching, multi-stage builds, and dependency management.

```mermaid
graph LR
    subgraph "Build Templates"
        BuildTemplate["_build_container.yml"]
        BuildArgs["build-args generation"]
        CacheStrategy["cache-from strategy"]
    end
    
    subgraph "Container Types"
        NeMoCore["nemo_container"]
        NeMo2["nemo_container_nemo2"]
        ExportDeploy["nemo_container_export_deploy"]
        Speech["nemo_container_speech"]
        Automodel["nemo_container_automodel"]
    end
    
    subgraph "Container Registry"
        ACR["nemoci.azurecr.io"]
        BuildCache["buildcache images"]
        ProductionImages["production images"]
    end
    
    subgraph "Build Infrastructure"
        AzureBuilder["self-hosted-azure-builder"]
        DockerFiles["Dockerfile.ci variants"]
        ManifestParser["manifest.json parser"]
    end
    
    BuildTemplate --> NeMoCore
    BuildTemplate --> NeMo2
    BuildTemplate --> ExportDeploy
    BuildTemplate --> Speech
    BuildTemplate --> Automodel
    
    BuildArgs --> ManifestParser
    CacheStrategy --> BuildCache
    
    NeMoCore --> ACR
    NeMo2 --> ACR
    ExportDeploy --> ACR
    
    AzureBuilder --> BuildTemplate
    DockerFiles --> BuildTemplate
```

**Sources:** [`.github/workflows/_build_container.yml:1-90`](), [`.github/workflows/update-buildcache.yml:81-113`]()

## Test Infrastructure and Component Selection

The testing system dynamically selects which components to test based on code changes, using a sophisticated component detection system that analyzes git diffs to determine affected subsystems.

```mermaid
graph TB
    subgraph "Test Organization"
        UnitTestMatrix["Unit Test Matrix"]
        E2ETestMatrix["E2E Test Matrix"]
        TestTemplate["test-template action"]
    end
    
    subgraph "Test Categories"
        CoreTests["Core/Common Tests"]
        LLMTests["LLM Tests"]
        SpeechTests["ASR/TTS Tests"]
        MultimodalTests["Multimodal Tests"]
        VLMTests["VLM Tests"]
        ExportTests["Export/Deploy Tests"]
    end
    
    subgraph "Test Execution"
        ContainerRuntime["Docker Container Runtime"]
        GPURunner["GPU Runners (self-hosted-azure-gpus-*)"]
        CPURunner["CPU Runners (self-hosted-azure-cpu)"]
        CoverageCollection["Coverage Collection"]
    end
    
    subgraph "Test Scripts"
        FunctionalTests["tests/functional_tests/*.sh"]
        UnitTestScripts["L0_Unit_Tests_*.sh"]
        E2EScripts["L2_*.sh"]
    end
    
    TestTemplate --> ContainerRuntime
    ContainerRuntime --> GPURunner
    ContainerRuntime --> CPURunner
    
    CoreTests --> UnitTestMatrix
    LLMTests --> UnitTestMatrix
    SpeechTests --> UnitTestMatrix
    
    UnitTestMatrix --> TestTemplate
    E2ETestMatrix --> TestTemplate
    
    TestTemplate --> FunctionalTests
    FunctionalTests --> CoverageCollection
```

**Sources:** [`.github/workflows/cicd-main-unit-tests.yml:22-213`](), [`.github/actions/test-template/action.yml:52-229`]()

## Dependency Management System

NeMo uses a centralized dependency management system based on [`requirements/manifest.json`]() that defines both PyPI and VCS dependencies, with automated update mechanisms for key dependencies like Megatron-LM.

| Component | Repository | Management Strategy |
|-----------|------------|-------------------|
| **Megatron-LM** | `NVIDIA/Megatron-LM` | Automated daily bumps via `mcore-tag-bump-bot.yml` |
| **Transformer Engine** | `NVIDIA/TransformerEngine` | Version-pinned in manifest |
| **TensorRT-LLM** | `NVIDIA/TensorRT-LLM` | Version-pinned in manifest |
| **Apex** | `NVIDIA/Apex` | Version-pinned in manifest |
| **Base Image** | `nvcr.io/nvidia/pytorch` | NGC PyTorch container |

```mermaid
graph LR
    subgraph "Dependency Sources"
        Manifest["manifest.json"]
        PyPIDeps["PyPI Dependencies"]
        VCSDeps["VCS Dependencies"]
    end
    
    subgraph "Automated Updates"
        McoreBot["mcore-tag-bump-bot"]
        WeeklyBump["weekly-bump-* branches"]
        BumpTemplate["_bump_mcore_tag.yml"]
    end
    
    subgraph "Update Process"
        TargetBranch["main/release branches"]
        PRCreation["Automated PR Creation"]
        CICDTrigger["CICD Label Application"]
    end
    
    Manifest --> VCSDeps
    Manifest --> PyPIDeps
    
    McoreBot --> BumpTemplate
    BumpTemplate --> WeeklyBump
    WeeklyBump --> TargetBranch
    
    TargetBranch --> PRCreation
    PRCreation --> CICDTrigger
```

**Sources:** [`.github/workflows/mcore-tag-bump-bot.yml:1-63`](), [`.github/workflows/_bump_mcore_tag.yml:44-57`](), [`requirements/manifest.json:1-23`]()

## Release Management Workflow

The release process involves code freezes, branch management, and automated changelog generation. Release workflows coordinate between multiple repositories and manage version bumping across the ecosystem.

```mermaid
flowchart TD
    subgraph "Release Initiation"
        ReleaseFreeze["release-freeze.yml"]
        FreezeInputs["Freeze Parameters"]
        CodeFreeze["Code Freeze Template"]
    end
    
    subgraph "Branch Management"
        ReleaseBranch["Release Branch Creation"]
        TagFreezing["freeze-tags job"]
        NotebookPinning["Notebook Branch Pinning"]
        McorePin["MCore Version Pinning"]
    end
    
    subgraph "Release Publishing"
        ReleaseWorkflow["release.yml"]
        WheelBuild["PyPI Wheel Building"]
        GitHubRelease["GitHub Release Creation"]
        VersionBump["Version Bump PR"]
    end
    
    subgraph "Post-Release"
        CherryPick["cherry-pick-release-commit.yml"]
        ChangelogBuild["changelog-build.yml"]
        ChangelogPR["Changelog PR Creation"]
    end
    
    ReleaseFreeze --> FreezeInputs
    FreezeInputs --> CodeFreeze
    CodeFreeze --> ReleaseBranch
    
    ReleaseBranch --> TagFreezing
    TagFreezing --> NotebookPinning
    TagFreezing --> McorePin
    
    ReleaseBranch --> ReleaseWorkflow
    ReleaseWorkflow --> WheelBuild
    WheelBuild --> GitHubRelease
    GitHubRelease --> VersionBump
    
    GitHubRelease --> CherryPick
    ReleaseBranch --> ChangelogBuild
    ChangelogBuild --> ChangelogPR
```

**Sources:** [`.github/workflows/release-freeze.yml:27-86`](), [`.github/workflows/release.yml:33-49`](), [`.github/workflows/cherry-pick-release-commit.yml:9-15`]()

## Quality Assurance and Monitoring

The system includes comprehensive monitoring, notification systems, and infrastructure health checks to ensure reliable operation of the CI/CD pipeline.

### Infrastructure Monitoring

```mermaid
graph TB
    subgraph "VM Health Monitoring"
        VMMonitor["monitor-vms.yml"]
        VMList["VM Discovery via GitHub API"]
        HealthChecks["GPU Health Validation"]
    end
    
    subgraph "Individual VM Checks"
        SingleVMMonitor["monitor-single-vm.yml"]
        GPUValidation["nvidia-smi validation"]
        RunnerDisconnect["Runner disconnection"]
    end
    
    subgraph "Failure Handling"
        SlackNotification["Slack Alerts"]
        AdminPing["Admin Team Notification"]
        AutoRemediation["Automatic Runner Shutdown"]
    end
    
    VMMonitor --> VMList
    VMList --> SingleVMMonitor
    SingleVMMonitor --> GPUValidation
    
    GPUValidation --> HealthChecks
    HealthChecks --> SlackNotification
    SlackNotification --> AdminPing
    AdminPing --> AutoRemediation
```

### Notification System

The CI/CD system includes sophisticated notification mechanisms that alert teams about pipeline failures, successful completions, and infrastructure issues.

| Notification Type | Trigger | Target | Implementation |
|------------------|---------|--------|----------------|
| **Pipeline Success** | Successful CICD completion | PR comments | `peter-evans/create-or-update-comment@v4` |
| **Pipeline Failure** | Test failures with "Run CICD" label | Slack webhook | `notify.py` script |
| **Infrastructure Issues** | VM health degradation | Slack admin alerts | VM monitoring workflow |
| **Release Events** | Release completion/failure | Release Slack channel | Release workflow notifications |

**Sources:** [`.github/workflows/monitor-vms.yml:8-55`](), [`.github/workflows/monitor-single-vm.yml:16-55`](), [`.github/scripts/notify.py:20-79`]()

## Code Quality and Linting

The development infrastructure includes automated code quality checks that run on every pull request to ensure consistency and maintainability.

```mermaid
graph LR
    subgraph "Quality Gates"
        CodeLinting["code-linting workflow"]
        CopyrightCheck["copyright-check.yml"]
        PreCommitHooks["Pre-commit validation"]
    end
    
    subgraph "Linting Tools"
        Flake8[".flake8 configuration"]
        Pylint[".pylintrc configuration"]
        BlackFormatting["Code formatting"]
    end
    
    subgraph "Quality Enforcement"
        PRTemplate["Pull Request Template"]
        CICDLabel["Run CICD label requirement"]
        ReviewProcess["Code review requirements"]
    end
    
    CodeLinting --> Flake8
    CodeLinting --> Pylint
    CodeLinting --> BlackFormatting
    
    CopyrightCheck --> PreCommitHooks
    PreCommitHooks --> PRTemplate
    PRTemplate --> CICDLabel
    CICDLabel --> ReviewProcess
```

**Sources:** [`.github/workflows/copyright-check.yml:20-23`](), [`.github/PULL_REQUEST_TEMPLATE.md:1-58`](), [`.github/CODEOWNERS:1-5`]()

## Evaluation and Testing Framework

The system includes specialized evaluation infrastructure for testing model performance and deployment scenarios, with support for both legacy and modern evaluation frameworks.

```mermaid
graph TB
    subgraph "Evaluation Infrastructure"
        EvalTests["L0_Unit_Tests_Eval"]
        LegacyEval["L0_Unit_Tests_Eval_Legacy"]
        EvalAdapters["L0_Unit_Tests_Eval_Adapters"]
    end
    
    subgraph "Evaluation Components"
        EvalUnittest["eval_unittest.py"]
        EvalLegacyUnittest["eval_unittest_legacy.py"]
        DeployScript["deploy_in_fw_script.py"]
    end
    
    subgraph "Testing Scenarios"
        HTTPServerTests["HTTPServer mocking"]
        TritonDeployment["PyTriton deployment tests"]
        APIEndpointTests["API endpoint validation"]
    end
    
    subgraph "Model Evaluation"
        GSM8KTests["GSM8K evaluation"]
        ARCTests["ARC challenge tests"]
        HFDatasets["HuggingFace datasets integration"]
    end
    
    EvalTests --> EvalUnittest
    LegacyEval --> EvalLegacyUnittest
    EvalUnittest --> HTTPServerTests
    
    DeployScript --> TritonDeployment
    TritonDeployment --> APIEndpointTests
    
    HTTPServerTests --> GSM8KTests
    APIEndpointTests --> ARCTests
    GSM8KTests --> HFDatasets
```

**Sources:** [`tests/evaluation/eval_unittest.py:22-90`](), [`tests/evaluation/eval_unittest_legacy.py:21-126`](), [`tests/functional_tests/L0_Unit_Tests_Eval.sh:14-18`]()

---

