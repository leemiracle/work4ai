<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ORBIT-Dataset · page 7 CI/CD & Infrastructure · fetched 2026-10-26 -->

# CI/CD & Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [azure-pipelines.yml](azure-pipelines.yml)
- [environment.yml](environment.yml)
- [requirements.txt](requirements.txt)

</details>



This section provides an overview of the infrastructure supporting the ORBIT Dataset repository, including the automation pipelines for security and compliance, and the configuration files required to reproduce the research environment.

The repository utilizes Azure Pipelines to ensure code integrity through scheduled builds and automated scanning tasks. The infrastructure is designed to support a PyTorch-based machine learning workflow, with specific dependencies for computer vision, model profiling, and data visualization.

## Pipeline Automation

The CI/CD workflow is defined in `azure-pipelines.yml` and is configured to run on a Windows-based virtual machine agent. The pipeline does not currently execute the full training or evaluation suite (which requires significant GPU resources) but instead focuses on security auditing and open-source software (OSS) compliance.

The pipeline is triggered by:
1.  **Code Changes**: Direct pushes or merges to the `master` branch [[azure-pipelines.yml:1-2]]().
2.  **Scheduled Builds**: A weekly cron job that runs every Sunday at 12:00 UTC to ensure ongoing compliance even when no code changes are made [[azure-pipelines.yml:7-13]]().

For details on the specific tasks executed during these builds, see [Azure Pipelines Configuration](#7.1).

### Infrastructure to Code Mapping
The following diagram illustrates how the Azure DevOps infrastructure interacts with the repository components and external security tools.

**Infrastructure Pipeline Flow**
```mermaid
graph TD
    subgraph "Azure DevOps Environment"
        "VM_Pool"["vmImage: 'windows-latest'"]
        "Trigger_Master"["trigger: master"]
        "Trigger_Weekly"["cron: '0 12 * * 0'"]
    end

    subgraph "Pipeline Tasks (azure-pipelines.yml)"
        "CredScan"["task: CredScan@3"]
        "CompGov"["task: ComponentGovernanceComponentDetection@0"]
    end

    subgraph "Codebase Entities"
        "Requirements"["requirements.txt"]
        "Env"["environment.yml"]
    end

    "Trigger_Master" --> "VM_Pool"
    "Trigger_Weekly" --> "VM_Pool"
    "VM_Pool" --> "CredScan"
    "VM_Pool" --> "CompGov"
    "CompGov" -.-> "Requirements"
    "CompGov" -.-> "Env"
```
Sources: [azure-pipelines.yml:1-23](), [requirements.txt:1-9](), [environment.yml:1-19]()

## Environment & Dependencies

The ORBIT codebase relies on a specific stack of Python libraries for deep learning (PyTorch), model backbone loading (`timm`), and computational profiling (`thop`). To ensure reproducibility, the project provides two methods for environment setup:

*   **Conda Environment**: Defined in `environment.yml`, specifying Python 3.7 and CUDA 11.6 compatibility [[environment.yml:7-11]]().
*   **Pip Requirements**: Defined in `requirements.txt`, providing a flat list of dependencies including `torch`, `torchvision`, and `tqdm` [[requirements.txt:1-6]]().

There is a noted version discrepancy between these files (e.g., `torch==2.6.0` in pip vs `pytorch=1.13.1` in Conda) which users must manage based on their specific hardware and CUDA availability.

For details on managing these dependencies and resolving version conflicts, see [Environment & Dependencies](#7.2).

### Dependency Ecosystem
The following diagram maps the primary external libraries used in the codebase to their specific roles within the ORBIT framework.

**Dependency Role Map**
```mermaid
graph LR
    subgraph "Deep Learning Core"
        "torch"["torch (PyTorch)"]
        "torchvision"["torchvision"]
    end

    subgraph "Model Components"
        "timm"["timm (Feature Extractors)"]
        "thop"["thop (OpsCounter)"]
    end

    subgraph "Utilities"
        "tqdm"["tqdm (Progress Bars)"]
        "plotly"["plotly (Visualization)"]
    end

    "torch" --> "timm"
    "torch" --> "thop"
    "torchvision" --> "timm"
```
Sources: [requirements.txt:1-6](), [environment.yml:9-18]()

## Security & Compliance

The repository integrates automated security tools to maintain Microsoft's security standards:

| Task | Purpose | File Reference |
| :--- | :--- | :--- |
| **CredScan** | Scans the codebase for exposed credentials, secrets, or keys. | [azure-pipelines.yml:16-16]() |
| **Component Governance** | Detects open-source components and alerts on high-level security vulnerabilities or licensing issues. | [azure-pipelines.yml:18-23]() |
| **Git Ignore** | Prevents sensitive files like `.venv`, `checkpoint/`, and `plots` from being committed. | [.gitignore:1-11]() |

Sources: [azure-pipelines.yml:15-23](), [.gitignore:1-11]()

---

