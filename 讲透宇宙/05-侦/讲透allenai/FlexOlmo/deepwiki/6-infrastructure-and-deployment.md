<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/FlexOlmo · page 6 Infrastructure and Deployment · fetched 2026-10-26 -->

# Infrastructure and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/main.yml](.github/workflows/main.yml)
- [src/scripts/beaker/README.md](src/scripts/beaker/README.md)
- [src/scripts/beaker/launch.py](src/scripts/beaker/launch.py)

</details>



This page covers FlexOlmo's distributed computing infrastructure, platform deployment configurations, and continuous integration systems. The infrastructure enables scalable training and evaluation on the Beaker platform with automated testing and deployment pipelines.

For information about training pipeline execution, see [Training Pipeline](#3). For details about evaluation system backends, see [Model Backends](#4.4).

## Beaker Platform Integration

FlexOlmo uses the Beaker platform for distributed training and evaluation jobs. The integration provides automated cluster management, resource allocation, and job orchestration through the `BeakerLaunchConfig` system.

### Launch Configuration System

The core infrastructure component is the `build_launch_config()` function which creates standardized Beaker job configurations:

```mermaid
graph TB
    A[launch.py] --> B["build_launch_config()"]
    B --> C["BeakerLaunchConfig"]
    C --> D["Cluster Selection"]
    C --> E["Resource Allocation"]
    C --> F["Environment Setup"]
    C --> G["Storage Configuration"]
    
    D --> H["ai2/oe-training clusters"]
    E --> I["num_nodes: 1"]
    E --> J["num_gpus: 8"]
    E --> K["shared_filesystem"]
    
    F --> L["Environment Variables"]
    F --> M["Secret Management"]
    F --> N["Setup Steps"]
    
    G --> O["BeakerWekaBucket"]
    G --> P["oe-training-default"]
    
    L --> Q["NCCL_DEBUG"]
    L --> R["CUDA_LAUNCH_BLOCKING"]
    
    M --> S["GITHUB_TOKEN"]
    M --> T["WANDB_API_KEY"]
    M --> U["AWS_CREDENTIALS"]
    
    N --> V["Repository Cloning"]
    N --> W["Environment Installation"]
    N --> X["Credential Setup"]
```

**Beaker Launch Configuration Components**

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| **Budget** | `ai2/oe-training` | Resource allocation budget |
| **Workspace** | `ai2/OLMo-modular` | Beaker workspace context |
| **Image** | `petew/olmo-core-tch260cu124` | Base Docker image |
| **Resources** | 1 node, 8 GPUs | Default resource allocation |
| **Storage** | `/weka/oe-training-default` | Shared filesystem mount |

Sources: [src/scripts/beaker/launch.py:31-91]()

### Job Execution and Command Processing

The launch system supports both dry-run validation and actual job execution through the `parse_args()` and `update_command()` functions:

```mermaid
graph LR
    A["parse_args()"] --> B["Command Parsing"]
    B --> C["Launch Arguments"]
    B --> D["Script Arguments"]
    B --> E["Launch Overrides"]
    
    C --> F["cmd: dry_run|launch"]
    C --> G["cluster: target cluster"]
    
    D --> H["Script Command"]
    E --> I["--launch.* options"]
    
    F --> J["update_command()"]
    H --> J
    J --> K["Final Command"]
    
    K --> L["Dry Run: Local Execution"]
    K --> M["Launch: Beaker Execution"]
```

**Environment Variables and Secrets**

| Variable | Source | Purpose |
|----------|--------|---------|
| `NCCL_DEBUG` | Runtime configuration | Distributed training debugging |
| `GITHUB_TOKEN` | User-specific secret | Repository access |
| `WANDB_API_KEY` | User-specific secret | Experiment tracking |
| `AWS_CREDENTIALS` | User-specific secret | Cloud storage access |
| `BEAKER_TOKEN` | User-specific secret | Platform authentication |

Sources: [src/scripts/beaker/launch.py:93-147](), [src/scripts/beaker/launch.py:59-73]()

### Setup and Installation Process

The Beaker jobs follow a standardized setup process defined in the `setup_steps` configuration:

```mermaid
sequenceDiagram
    participant Container as "Beaker Container"
    participant GitHub as "GitHub Repository"
    participant Conda as "Conda Environment"
    participant AWS as "AWS Services"
    
    Container->>GitHub: Clone repository via gh CLI
    GitHub->>Container: Source code
    Container->>Container: git checkout $GIT_REF
    Container->>Container: git submodule update
    Container->>Conda: conda shell.bash activate base
    Container->>Conda: pip install -e .[dev,beaker,wandb,train]
    Container->>AWS: Setup credentials (~/.aws/config)
    Container->>Container: Ready for execution
```

Sources: [src/scripts/beaker/launch.py:74-90]()

## CI/CD and Containerization

The continuous integration system uses GitHub Actions with multi-stage validation including CPU and GPU testing through Beaker integration.

### GitHub Actions Workflow

The main workflow defines comprehensive validation stages:

```mermaid
graph TB
    A[".github/workflows/main.yml"] --> B["Trigger Events"]
    B --> C["Pull Request"]
    B --> D["Push to main"]
    B --> E["Version Tags"]
    
    A --> F["Job Matrix"]
    F --> G["checks"]
    F --> H["gpu_checks"]
    F --> I["release"]
    
    G --> J["Lint"]
    G --> K["Test"]
    G --> L["Type Check"]
    G --> M["Build"]
    G --> N["Style"]
    
    H --> O["GPU Testing"]
    O --> P["Beaker Execution"]
    P --> Q["Multi-GPU Tests"]
    
    I --> R["PyPI Release"]
    I --> S["GitHub Release"]
```

**CI/CD Matrix Configuration**

| Job Stage | Tasks | Runtime | Environment |
|-----------|-------|---------|-------------|
| **checks** | Lint, Test, Type check, Build, Style | 8 minutes | ubuntu-latest |
| **gpu_checks** | GPU tests | 15 minutes | Beaker clusters |
| **release** | PyPI, GitHub release | - | ubuntu-latest |

Sources: [.github/workflows/main.yml:26-51]()

### GPU Testing Infrastructure

GPU tests execute on Beaker clusters using the `beaker-run-action`:

```mermaid
graph TB
    A["gpu_checks Job"] --> B["Beaker Image Selection"]
    B --> C["olmo-modular-tch251cu124"]
    
    A --> D["Cluster Constraints"]
    D --> E["ai2/jupiter-cirrascale-2"]
    D --> F["ai2/augusta-google-1"]
    D --> G["ai2/ceres-cirrascale"]
    D --> H["ai2/saturn-cirrascale"]
    
    A --> I["Resource Allocation"]
    I --> J["gpuCount: 2"]
    I --> K["priority: normal"]
    I --> L["preemptible: true"]
    
    A --> M["Test Execution"]
    M --> N["pytest -v -m gpu"]
    N --> O["GPU Test Results"]
```

**Beaker GPU Test Configuration**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Image** | `olmo-modular-tch251cu124` | PyTorch 2.5.1 + CUDA 12.4 |
| **GPU Count** | 2 | Multi-GPU testing |
| **Clusters** | H100, A100 clusters | Hardware diversity |
| **Environment** | `CUBLAS_WORKSPACE_CONFIG=:16:8` | Deterministic operations |

Sources: [.github/workflows/main.yml:136-178]()

### Release Automation

The release workflow handles automated PyPI and GitHub releases:

```mermaid
sequenceDiagram
    participant Tag as "Version Tag"
    participant GitHub as "GitHub Actions"
    participant PyPI as "PyPI Registry"
    participant Release as "GitHub Release"
    
    Tag->>GitHub: v*.*.* tag push
    GitHub->>GitHub: Run checks job
    GitHub->>GitHub: Download build artifacts
    GitHub->>GitHub: Generate release notes
    GitHub->>PyPI: twine upload dist/*
    GitHub->>Release: Create GitHub release
    Release->>Release: Attach distribution files
```

**Release Process Components**

| Stage | Action | Trigger |
|-------|--------|---------|
| **Tag Detection** | `startsWith(github.ref, 'refs/tags/')` | Version tag push |
| **Artifact Download** | `actions/download-artifact@v4` | Build artifacts |
| **PyPI Publish** | `twine upload` | PYPI_TOKEN secret |
| **GitHub Release** | `softprops/action-gh-release@v2` | Automated release |

Sources: [.github/workflows/main.yml:180-226]()

### Environment and Secret Management

Both Beaker and GitHub Actions use centralized secret management:

```mermaid
graph TB
    A["Secret Management"] --> B["GitHub Secrets"]
    A --> C["Beaker Secrets"]
    
    B --> D["AWS_ACCESS_KEY_ID"]
    B --> E["AWS_SECRET_ACCESS_KEY"]
    B --> F["BEAKER_TOKEN"]
    B --> G["INTERNAL_GITHUB_TOKEN"]
    B --> H["PYPI_TOKEN"]
    
    C --> I["User-Specific Secrets"]
    I --> J["{user}_GITHUB_TOKEN"]
    I --> K["{user}_WANDB_API_KEY"]
    I --> L["{user}_AWS_CREDENTIALS"]
    
    D --> M["Cloud Storage Access"]
    F --> N["Beaker Platform Access"]
    G --> O["Repository Operations"]
    H --> P["Package Publishing"]
```

Sources: [.github/workflows/main.yml:17-25](), [src/scripts/beaker/launch.py:63-73]()

---

