<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SERA · page 9 Repository Structure · fetched 2026-10-26 -->

# Repository Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [modules/SWE-agent/.dockerignore](modules/SWE-agent/.dockerignore)
- [modules/SWE-agent/.gitignore](modules/SWE-agent/.gitignore)

</details>



## Purpose and Scope

This document describes the file organization and directory structure of the SERA repository, including both the root-level SERA system and the `modules/SWE-agent/` submodule. It documents the development workspace layout, artifact directories, and exclusion patterns defined in `.gitignore` and `.dockerignore` files.

For information about setting up the development environment, see [Development Environment](#4). For Docker containerization details, see [Docker and Containerization](#5).

---

## Repository Overview

The SERA repository follows a two-layer structure with distinct purposes at each level:

```mermaid
graph TB
    Root["SERA Repository Root"]
    
    subgraph RootFiles["Root Level"]
        README["README.md"]
        License["LICENSE.md"]
        Assets["assets/SERA.jpg"]
        GitIgnore[".gitignore"]
    end
    
    subgraph SERADirs["SERA Directories"]
        Sera["sera/<br/>Python Package"]
        Logs["logs/<br/>Pipeline Logs"]
        Repos["repos/<br/>Cloned Repositories"]
        Experiments["experiments/<br/>Experiment Data"]
        Outputs["outputs/<br/>Generated Data"]
        Metadata["metadata/<br/>Metadata Files"]
        PRIssues["pr_issues/<br/>PR Issue Data"]
    end
    
    subgraph SWEAgentModule["modules/SWE-agent/<br/>Submodule"]
        SWECore["sweagent/<br/>Python Package"]
        Trajectories["trajectories/<br/>Execution Traces"]
        Results["results/<br/>Evaluation Data"]
        Testbed["testbed/<br/>Test Environment"]
        Inspector["inspector/<br/>Analysis Data"]
        Website["website/<br/>Web Interface"]
    end
    
    Root --> RootFiles
    Root --> SERADirs
    Root --> SWEAgentModule
```

**Sources:** [.gitignore:1-227](), [modules/SWE-agent/.gitignore:1-198]()

---

## Root Directory Structure

### SERA System Directories

The root level of the repository contains directories specific to the SERA data generation pipeline:

| Directory | Purpose | Tracking Status |
|-----------|---------|-----------------|
| `sera/` | Main Python package containing pipeline code | Tracked |
| `logs/` | Pipeline execution logs and debug output | Ignored |
| `repos/` | Cloned GitHub repositories for analysis | Ignored |
| `experiments/` | Experimental configurations and results | Ignored |
| `outputs/` | Generated training data and artifacts | Ignored |
| `metadata/` | Repository and issue metadata | Ignored |
| `pr_issues/` | Pull request issue data for processing | Ignored |
| `.claude/` | Claude AI integration data | Ignored |
| `assets/` | Static assets (SERA.jpg) | Tracked |

**Sources:** [.gitignore:1-7]()

### SERA Python Package Organization

The `sera/` directory contains the data generation pipeline code. Key subdirectories include:

```mermaid
graph LR
    SeraPackage["sera/"]
    
    Datagen["datagen/<br/>Data Generation"]
    Train["datagen/train/"]
    DatasetCache["dataset_cache/<br/>Cached Datasets"]
    Wandb["wandb/<br/>Experiment Tracking"]
    
    SeraPackage --> Datagen
    Datagen --> Train
    Train --> DatasetCache
    Train --> Wandb
    
    DatasetCache -.->|"Ignored"| IgnoreNote1[".gitignore"]
    Wandb -.->|"Ignored"| IgnoreNote2[".gitignore"]
```

**Sources:** [.gitignore:9-10]()

---

## SWE-agent Module Structure

### Module Directory Layout

The `modules/SWE-agent/` submodule contains the autonomous software engineering agent system:

| Directory | Purpose | Tracking Status |
|-----------|---------|-----------------|
| `sweagent/` | Core agent Python package | Tracked |
| `trajectories/` | Agent execution traces | Ignored (except demonstrations) |
| `data/` | Task data and benchmarks | Partially ignored |
| `results/` | Evaluation results and metrics | Ignored |
| `testbed/` | Isolated test environments | Ignored |
| `inspector/` | Analysis and debugging data | Ignored |
| `website/frontend/` | Web interface for agent interaction | Partially tracked |
| `.devcontainer/` | VS Code development container | Tracked |
| `assets/` | Visual assets and documentation images | Tracked |

**Sources:** [modules/SWE-agent/.gitignore:143-157](), [modules/SWE-agent/.dockerignore:140-143]()

### Execution Artifact Directories

```mermaid
graph TB
    Execution["Agent Execution"]
    
    subgraph Artifacts["Artifact Storage"]
        Trajectories["trajectories/<br/>Execution Traces"]
        Demonstrations["trajectories/demonstrations/<br/>Example Traces"]
        Results["results/<br/>Evaluation Data"]
        Testbed["testbed/<br/>Test Environments"]
        Inspector["inspector/*.json<br/>Debug Analysis"]
    end
    
    subgraph TrackingStatus["Version Control"]
        Ignored["Ignored<br/>(Generated at Runtime)"]
        Tracked["Tracked<br/>(Reference Data)"]
    end
    
    Execution --> Trajectories
    Execution --> Results
    Execution --> Testbed
    Execution --> Inspector
    
    Trajectories --> Ignored
    Demonstrations --> Tracked
    Results --> Ignored
    Testbed --> Ignored
    Inspector --> Ignored
```

**Sources:** [modules/SWE-agent/.gitignore:143-157](), [modules/SWE-agent/.dockerignore:188-191]()

---

## Ignored Artifacts and Exclusions

### Python Development Artifacts

Both the root repository and SWE-agent module exclude standard Python development artifacts:

```mermaid
graph LR
    PythonArtifacts["Python Development"]
    
    subgraph ByteCode["Compiled Code"]
        PyCache["__pycache__/"]
        PyCompiled["*.pyc, *.pyo, *.pyd"]
        CExtensions["*.so"]
    end
    
    subgraph Distribution["Distribution"]
        Build["build/, dist/"]
        Eggs["*.egg-info/"]
        Wheels["wheels/"]
    end
    
    subgraph Testing["Testing"]
        Pytest[".pytest_cache/"]
        Coverage[".coverage, coverage.xml"]
        Hypothesis[".hypothesis/"]
    end
    
    subgraph Environment["Environments"]
        VirtualEnv["venv/, .venv/"]
        EnvFiles[".env"]
        PyEnv[".python-version"]
    end
    
    PythonArtifacts --> ByteCode
    PythonArtifacts --> Distribution
    PythonArtifacts --> Testing
    PythonArtifacts --> Environment
```

**Sources:** [.gitignore:15-163](), [modules/SWE-agent/.gitignore:1-131]()

### API Keys and Credentials

Credential files are excluded from version control for security:

| Pattern | Purpose | Location |
|---------|---------|----------|
| `keys*.cfg` | API key configuration files | Root and SWE-agent |
| `*.env`, `.env.*` | Environment variable files | Both locations |
| `.api_key` | API key storage | SWE-agent website |

**Sources:** [.gitignore:169](), [modules/SWE-agent/.gitignore:137](), [modules/SWE-agent/.gitignore:181]()

### Documentation and Web Assets

```mermaid
graph TB
    WebAssets["Web & Documentation"]
    
    subgraph Docs["Documentation"]
        MkDocs["/site/<br/>Built MkDocs Site"]
        Sphinx["docs/_build/<br/>Sphinx Output"]
    end
    
    subgraph WebFrontend["Website Frontend"]
        NodeModules["node_modules/<br/>NPM Packages"]
        Build["build/<br/>Production Build"]
        Coverage["coverage/<br/>Test Coverage"]
        PackageLock["package-lock.json"]
    end
    
    subgraph Notebooks["Notebooks"]
        IPython["*.ipynb<br/>Jupyter Notebooks"]
        FineTune["fine_tune/*.ipynb"]
    end
    
    WebAssets --> Docs
    WebAssets --> WebFrontend
    WebAssets --> Notebooks
    
    MkDocs -.->|"Ignored"| Git1[".gitignore"]
    NodeModules -.->|"Ignored"| Git2[".gitignore"]
    IPython -.->|"Ignored"| Git3[".gitignore"]
```

**Sources:** [.gitignore:154-173](), [modules/SWE-agent/.gitignore:122-184]()

### IDE and Editor Files

Development environment files are excluded to avoid conflicts:

| Pattern | IDE/Editor | Files Excluded |
|---------|------------|----------------|
| `.vscode/**` | Visual Studio Code | Workspace settings |
| `.idea/` | PyCharm | Project configuration |
| `.DS_Store` | macOS Finder | File metadata |
| `.ipynb_checkpoints` | Jupyter | Notebook checkpoints |

**Sources:** [.gitignore:166](), [.gitignore:223](), [modules/SWE-agent/.gitignore:134](), [modules/SWE-agent/.gitignore:190](), [modules/SWE-agent/.dockerignore:192]()

---

## Docker Build Exclusions

### SWE-agent Docker Build Context

The `.dockerignore` file for SWE-agent optimizes Docker image builds by excluding unnecessary files:

```mermaid
graph TB
    BuildContext["Docker Build Context"]
    
    subgraph Excluded["Excluded from Image"]
        Runtime["Runtime Artifacts<br/>trajectories/, results/, testbed/"]
        Development["Development Files<br/>.vscode/, .idea/, *.ipynb"]
        VCS["Version Control<br/>*.demo.yaml"]
        Testing["Test Data<br/>coverage/, .pytest_cache/"]
        Dependencies["Dependencies<br/>node_modules/, venv/"]
    end
    
    subgraph Included["Included in Image"]
        Source["Source Code<br/>sweagent/"]
        Config["Configuration<br/>*.yaml (non-demo)"]
        Demos["Demonstrations<br/>trajectories/demonstrations/"]
        Assets["Assets<br/>assets/"]
    end
    
    BuildContext --> Excluded
    BuildContext --> Included
    
    Excluded -.->|"Reduces Image Size"| Benefit1["Faster Builds"]
    Excluded -.->|"Removes Secrets"| Benefit2["Security"]
```

**Sources:** [modules/SWE-agent/.dockerignore:1-196]()

### Key Exclusion Patterns

The Docker build excludes runtime-generated files while preserving reference data:

```mermaid
graph LR
    Patterns["Exclusion Patterns"]
    
    subgraph RuntimeData["Runtime Generated"]
        TrajExclude["trajectories/**"]
        TrajInclude["!trajectories/demonstrations/**"]
        ResultsExclude["results/, testbed/, temp/"]
        InspectorExclude["inspector/*.json"]
    end
    
    subgraph DataExclude["Data Files"]
        DataAll["data/**"]
        ICExclude["data/*/ic-*"]
        SingleIssues["data/*/single-issues"]
    end
    
    Patterns --> RuntimeData
    Patterns --> DataExclude
    
    TrajExclude -.->|"Overridden by"| TrajInclude
```

**Sources:** [modules/SWE-agent/.dockerignore:188-191](), [modules/SWE-agent/.dockerignore:145-147](), [modules/SWE-agent/.dockerignore:154-155]()

---

## Development Workspace Organization

### Working Directory Structure

During development, the repository expands with additional runtime directories:

```mermaid
graph TB
    WorkingDir["Development Workspace"]
    
    subgraph Tracked["Version Controlled"]
        Source["Source Code<br/>sera/, sweagent/"]
        Config["Configuration<br/>*.yaml, *.cfg.sample"]
        Docs["Documentation<br/>*.md, mkdocs.yml"]
        Tests["Tests<br/>tests/"]
    end
    
    subgraph Generated["Runtime Generated"]
        Logs["logs/<br/>Execution Logs"]
        Outputs["outputs/, experiments/<br/>Pipeline Results"]
        Repos["repos/<br/>Cloned Repositories"]
        Trajectories["trajectories/<br/>Agent Traces"]
        Results["results/, testbed/<br/>Evaluation Data"]
    end
    
    subgraph Caches["Cached Data"]
        PyCache["__pycache__/<br/>Python Bytecode"]
        DatasetCache["dataset_cache/<br/>Training Data"]
        WandbCache["wandb/<br/>Experiment Tracking"]
        NodeModules["node_modules/<br/>NPM Packages"]
    end
    
    WorkingDir --> Tracked
    WorkingDir --> Generated
    WorkingDir --> Caches
    
    Tracked -.->|"Git Tracked"| VCS["Version Control"]
    Generated -.->|"Git Ignored"| NoVCS["Not Tracked"]
    Caches -.->|"Git Ignored"| NoVCS
```

**Sources:** [.gitignore:1-227](), [modules/SWE-agent/.gitignore:1-198]()

### Temporary and Fine-Tuning Data

Special patterns for data processing workflows:

| Directory/Pattern | Purpose | Status |
|-------------------|---------|--------|
| `fine_tune/*.ipynb` | Fine-tuning notebooks | Ignored |
| `fine_tune/subtasks/*.jsonl` | Task-specific training data | Ignored |
| `temp*.jsonl` | Temporary JSONL files | Ignored |
| `*.demo.yaml` | Demo configuration (editing) | Ignored |
| `*.decomp.json` | Decompilation output | Ignored |
| `*.disas.json` | Disassembly output | Ignored |

**Sources:** [.gitignore:184-186](), [.gitignore:220](), [.gitignore:225-227](), [modules/SWE-agent/.gitignore:150-154](), [modules/SWE-agent/.gitignore:187]()

---

## Module Separation

### SERA vs SWE-agent Organization

The repository maintains clear separation between the two major components:

```mermaid
graph LR
    Repository["SERA Repository"]
    
    subgraph SERASystem["SERA System<br/>(Root Level)"]
        SERACode["sera/<br/>Data Generation Pipeline"]
        SERAData["Data Directories<br/>logs/, repos/, experiments/"]
        SERAConfig["SERA Configuration<br/>specializations/"]
    end
    
    subgraph SWEAgentSystem["SWE-agent System<br/>(modules/SWE-agent)"]
        AgentCode["sweagent/<br/>Agent Core"]
        AgentData["Agent Directories<br/>trajectories/, results/"]
        AgentConfig["Agent Configuration<br/>config/, tools/"]
    end
    
    Repository --> SERASystem
    Repository --> SWEAgentSystem
    
    SERASystem -.->|"Root .gitignore"| RootIgnore[".gitignore"]
    SWEAgentSystem -.->|"Module .gitignore"| ModuleIgnore["modules/SWE-agent/.gitignore"]
```

**Sources:** [.gitignore:20-32](), [modules/SWE-agent/.gitignore:1-198]()

### Ignored Paths in Root .gitignore

The root `.gitignore` specifically excludes SWE-agent runtime files:

| Pattern | Purpose |
|---------|---------|
| `SWE-agent/keys.yaml` | Agent API keys |
| `SWE-agent/.swe-agent-human-history` | Interaction history |
| `SWE-agent/.vscode/**` | VS Code settings |
| `SWE-agent/cov.xml` | Coverage reports |
| `SWE-agent/!trajectories/demonstrations/**` | Preserve demonstrations |
| `SWE-agent/data/**` | Runtime data |
| `SWE-agent/*.env` | Environment files |
| `SWE-agent/!tools/*` | Preserve tool definitions |
| `SWE-agent/deps/*` | Dependencies |
| `SWE-agent/trajectories/*` | Execution traces |
| `SWE-agent/*.jsonl`, `*.json` | Data files |

**Sources:** [.gitignore:20-32]()

---

## Summary

The SERA repository implements a hierarchical structure with clear separation of concerns:

1. **Root Level**: SERA data generation system with pipeline code and runtime data directories
2. **SWE-agent Module**: Autonomous agent system in `modules/SWE-agent/` with independent artifact management
3. **Ignored Artifacts**: Comprehensive exclusion of runtime data, credentials, and development artifacts
4. **Docker Optimization**: Selective inclusion patterns for efficient container builds
5. **Development Workspace**: Runtime directories expand during execution but remain excluded from version control

This organization enables independent development of both systems while maintaining a cohesive repository structure. The `.gitignore` and `.dockerignore` patterns ensure that only source code, configuration templates, and reference data are tracked, while runtime artifacts, credentials, and development files remain local.

**Sources:** [.gitignore:1-227](), [modules/SWE-agent/.gitignore:1-198](), [modules/SWE-agent/.dockerignore:1-196]()