<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/jupyter-agent · page 5 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [data/README.md](data/README.md)

</details>



This guide provides practical instructions for developers working with the Jupyter Agent codebase. It covers environment setup, pipeline execution, configuration requirements, and common development workflows. For detailed information about the data generation pipeline architecture, see [Data Generation Pipeline](#2). For model training procedures, see [Models and Evaluation](#4).

## Overview

The Jupyter Agent repository is organized around two primary workflows:

1. **Data Generation**: Processing raw Kaggle notebooks through an 8-stage pipeline to produce training data
2. **Model Training**: Fine-tuning base models using the generated dataset

Development primarily involves running and modifying the data generation pipeline, which requires access to distributed computing infrastructure (Slurm cluster), external LLM services, and substantial storage capacity.

## Development Workflow

```mermaid
graph TB
    subgraph "Developer Actions"
        A["Clone Repository"]
        B["Set Environment Variables"]
        C["Configure Infrastructure"]
    end
    
    subgraph "Execution Modes"
        D["Full Pipeline<br/>data/main.py"]
        E["Individual Stage<br/>pipelines/*.py"]
        F["Custom Stage Chain<br/>Modified main.py"]
    end
    
    subgraph "Infrastructure Dependencies"
        G["Slurm Cluster<br/>hopper-cpu partition"]
        H["LLM Router<br/>router_ip:router_port"]
        I["Shared Storage<br/>/fsx/jupyter-agent/data/"]
        J["KaggleHub API<br/>KAGGLEHUB_CACHE"]
    end
    
    subgraph "Outputs"
        K["Intermediate Results<br/>filtered/, scored/"]
        L["Final Dataset<br/>traces-final/"]
        M["ChatML Training Data<br/>chatml-dataset/"]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    
    D --> G
    D --> H
    D --> I
    D --> J
    
    E --> G
    E --> H
    E --> I
    E --> J
    
    F --> G
    F --> H
    F --> I
    F --> J
    
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L
    L --> M
```

**Sources:** [data/README.md:1-135](), [README.md:1-104]()

## Key Entry Points and Commands

The codebase provides multiple entry points depending on the development task:

| Entry Point | Purpose | Command Example |
|------------|---------|-----------------|
| `data/main.py` | Full pipeline orchestration | `uv run main.py -r <ROUTER_IP:PORT>` |
| `pipelines/kaggle_loader.py` | Stage 1: Load raw notebooks | `uv run pipelines/kaggle_loader.py` |
| `pipelines/dedup.py` | Stage 2: Deduplication | `uv run pipelines/dedup.py` |
| `pipelines/edu_scoring.py` | Stage 4: Quality assessment | `uv run pipelines/edu_scoring.py -r <ROUTER_IP:PORT>` |
| `pipelines/extract_packages_and_files.py` | Stage 5: Metadata extraction | `uv run pipelines/extract_packages_and_files.py -r <ROUTER_IP:PORT>` |
| `pipelines/generate_qa.py` | Stage 6: QA generation | `uv run pipelines/generate_qa.py -r <ROUTER_IP:PORT>` |
| `pipelines/generate_traces.py` | Stage 8: Trace generation | `uv run pipelines/generate_traces.py -r <ROUTER_IP:PORT>` |

**Sources:** [data/README.md:112-135]()

## Pipeline Stage Dependencies

```mermaid
graph LR
    subgraph "Stage Execution Order"
        S1["KaggleLoader<br/>pipelines/kaggle_loader.py"]
        S2["Dedup<br/>pipelines/dedup.py"]
        S3["AddMarkdownToNotebook"]
        S4["EduScorer<br/>pipelines/edu_scoring.py"]
        S5["ExtractPackagesAndFiles<br/>pipelines/extract_packages_and_files.py"]
        S6["GenerateQA<br/>pipelines/generate_qa.py"]
        S7["Dataset Mapping"]
        S8["GenerateTraces<br/>pipelines/generate_traces.py"]
    end
    
    subgraph "Configuration Requirements"
        C1["KAGGLEHUB_CACHE"]
        C2["router_ip:router_port"]
        C3["E2B API key"]
        C4["Slurm cluster access"]
    end
    
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
    S5 --> S6
    S6 --> S7
    S7 --> S8
    
    S1 -.requires.-> C1
    S1 -.requires.-> C4
    
    S4 -.requires.-> C2
    S4 -.requires.-> C4
    
    S5 -.requires.-> C2
    S5 -.requires.-> C4
    
    S6 -.requires.-> C2
    S6 -.requires.-> C4
    
    S7 -.requires.-> C1
    S7 -.requires.-> C4
    
    S8 -.requires.-> C2
    S8 -.requires.-> C3
    S8 -.requires.-> C4
```

**Sources:** [data/README.md:6-28](), [data/README.md:112-135]()

## Configuration Architecture

The system relies on several environment-level configurations that must be established before pipeline execution:

```mermaid
graph TB
    subgraph "Environment Variables"
        E1["KAGGLEHUB_CACHE<br/>Local dataset storage"]
        E2["E2B_API_KEY<br/>Sandbox execution"]
        E3["HF_TOKEN<br/>Model downloads"]
    end
    
    subgraph "Command Line Arguments"
        A1["-r ROUTER_IP:PORT<br/>LLM endpoint"]
        A2["-m MODEL_NAME<br/>Specific model selection"]
        A3["--num-proc N<br/>Parallel workers"]
    end
    
    subgraph "Hardcoded Paths"
        P1["/fsx/jupyter-agent/data/<br/>Shared storage root"]
        P2["meta-kaggle-dataset/<br/>Input notebooks"]
        P3["traces-final/<br/>Output dataset"]
    end
    
    subgraph "External Services"
        S1["OpenAI-compatible Router"]
        S2["Qwen3-32B Model"]
        S3["Qwen3-Coder-480B Model"]
        S4["E2B Sandboxes"]
        S5["KaggleHub API"]
    end
    
    E1 --> S5
    E2 --> S4
    E3 --> S2
    E3 --> S3
    
    A1 --> S1
    S1 --> S2
    S1 --> S3
    
    P1 --> P2
    P1 --> P3
```

**Sources:** [data/README.md:91-106](), [data/README.md:110-135]()

## Code Organization for Development

The repository follows a modular structure separating data generation from model training:

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `data/` | Pipeline orchestration | `main.py` - Entry point with `SlurmPipelineExecutor` |
| `data/pipelines/` | Individual pipeline stages | `kaggle_loader.py`, `dedup.py`, `edu_scoring.py`, etc. |
| `data/filters/` | Data filtering components | Used by pipeline stages for document filtering |
| `data/mappers/` | Data transformation components | Used by pipeline stages for document mapping |
| `finetuning/` | Model training scripts | Training configuration and execution scripts |
| `workspace/` | Temporary development files | Ignored by git [.gitignore:194]() |
| `debug-data/` | Debug output storage | Ignored by git [.gitignore:178]() |
| `logs/` | Execution logs | Ignored by git [.gitignore:175]() |

**Sources:** [.gitignore:1-202](), [README.md:59-61]()

## Development Dependencies

The project uses `uv` as the Python package manager. All pipeline commands are executed with the `uv run` prefix, which manages the virtual environment automatically. The `.gitignore` file shows that multiple virtual environment patterns are excluded (`.venv`, `.venv*`, `venv/`, etc.), indicating flexibility in environment setup approaches.

Key dependency categories:
- **Data Processing**: Libraries for notebook manipulation, markdown conversion
- **LLM Integration**: OpenAI-compatible API clients for model inference
- **Distributed Computing**: Slurm integration for cluster execution
- **Sandbox Execution**: E2B API for isolated code execution
- **Dataset Management**: KaggleHub for dataset downloads

**Sources:** [.gitignore:130-138](), [.gitignore:185]()

## Resource Requirements

Based on the infrastructure diagrams and configuration:

| Resource Type | Requirement | Usage |
|--------------|-------------|-------|
| Storage | Multiple TB | Raw notebooks (~2TB), intermediate data, final dataset |
| Compute | 128 tasks × 4 CPUs | Slurm cluster: `hopper-cpu` partition |
| Memory | 16GB per task | Total: ~2TB across all parallel tasks |
| Network | High bandwidth | LLM API calls, dataset downloads |

The pipeline generates substantial intermediate data that must be preserved between stages. The `.gitignore` explicitly excludes large data artifacts (`*.parquet`, `*.jsonl`, `*.jsonl.gz`, `training-data/`, `models/`) to prevent accidental commits.

**Sources:** [.gitignore:183-201]()

## Common Development Tasks

### Inspecting Pipeline Outputs

Each stage writes to a specific subdirectory under `/fsx/jupyter-agent/data/`. Developers can inspect intermediate results by examining these directories without re-running expensive stages.

### Debugging Individual Stages

Individual pipeline stages can be executed independently using their respective CLI scripts in `data/pipelines/`. This allows testing stage modifications without running the full pipeline.

### Modifying Pipeline Configuration

The `data/main.py` file contains the pipeline definition using `SlurmPipelineExecutor`. Developers can modify stage order, add new stages, or adjust resource allocation by editing this orchestration script.

### Working with Temporary Data

The `.gitignore` configuration protects developers from accidentally committing large artifacts. Debug outputs go to `debug-data/`, temporary notebooks to `workspace/`, and logs to `logs/` - all ignored directories.

**Sources:** [.gitignore:174-201](), [data/README.md:112-135]()

## Next Steps

For detailed instructions on environment setup, see [Environment Setup](#5.1). For step-by-step pipeline execution procedures, see [Running the Pipeline](#5.2). For information about data storage organization, see [Data Storage and Paths](#5.3).

---

