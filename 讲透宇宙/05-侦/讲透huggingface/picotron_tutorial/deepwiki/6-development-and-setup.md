<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/picotron_tutorial · page 6 Development and Setup · fetched 2026-10-26 -->

# Development and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.demo/step1_modeling.json](.demo/step1_modeling.json)
- [.vscode/settings.json](.vscode/settings.json)
- [README.md](README.md)
- [assets/llama1B_sanity_check.png](assets/llama1B_sanity_check.png)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)

</details>



This page covers the supporting infrastructure for developing, testing, and demonstrating the Picotron tutorial framework. It includes environment configuration, dependency management, development tooling, validation procedures, and demonstration infrastructure.

For information about the tutorial progression and training components, see [Tutorial Progression](#2) and [Training Integration](#5).

## Environment Configuration

The tutorial requires a specific Python environment with distributed training dependencies. The setup process follows a standard conda-based workflow with pip installation for the package itself.

```mermaid
graph TB
    subgraph "Environment Setup"
        CONDA["conda create"]
        ACTIVATE["conda activate env-picotron-tutorial"]
        PIP_INSTALL["pip install -e ."]
    end
    
    subgraph "Package Dependencies"
        TORCH["torch==2.1.0"]
        NUMPY["numpy==1.26.4"]
        DATASETS["datasets==2.19.1"]
        TRANSFORMERS["transformers==4.41.1"]
        FLASH_ATTN["flash-attn==2.5.0"]
        WANDB["wandb"]
        LOVELY["lovely_tensors"]
    end
    
    subgraph "Setup Configuration"
        SETUP_PY["setup.py"]
        REQUIREMENTS["requirements.txt"]
        READ_REQS["read_requirements()"]
    end
    
    CONDA --> ACTIVATE
    ACTIVATE --> PIP_INSTALL
    PIP_INSTALL --> SETUP_PY
    SETUP_PY --> READ_REQS
    READ_REQS --> REQUIREMENTS
    
    REQUIREMENTS --> TORCH
    REQUIREMENTS --> NUMPY
    REQUIREMENTS --> DATASETS
    REQUIREMENTS --> TRANSFORMERS
    REQUIREMENTS --> FLASH_ATTN
    REQUIREMENTS --> WANDB
    REQUIREMENTS --> LOVELY
```

The environment configuration is managed through standard Python packaging tools. The `setup.py` file defines the package metadata and reads dependencies from `requirements.txt` using the `read_requirements()` function.

**Sources:** [README.md:16-20](), [setup.py:3-12](), [requirements.txt:1-7]()

## Development Tooling

The codebase includes VS Code configuration for consistent development experience and presentation capabilities.

| Tool | Configuration | Purpose |
|------|---------------|---------|
| VS Code | `.vscode/settings.json` | Editor configuration for demos |
| Demo Time Extension | `demoTime.*` settings | Presentation and tutorial delivery |
| Editor Customization | `workbench.colorCustomizations` | Visual highlighting for demonstrations |

The VS Code configuration includes specialized settings for demonstration purposes, with custom highlighting and timer functionality for educational presentations.

**Sources:** [.vscode/settings.json:1-9]()

## Validation and Testing

The tutorial includes comprehensive sanity checking procedures to validate that distributed training implementations produce equivalent results to baseline single-process training.

```mermaid
graph TB
    subgraph "Validation Framework"
        BASELINE["Baseline Training"]
        TP_TEST["Tensor Parallel Test"]
        DP_TEST["Data Parallel Test"]
        PP_TEST["Pipeline Parallel Test"]
        TD_TEST["3D Parallelism Test"]
    end
    
    subgraph "Test Configuration"
        MODEL_CONFIG["TinyLlama/TinyLlama_v1.1<br/>22 layers, 32 heads, 4 KV heads"]
        DATA_CONFIG["4096000 tokens<br/>1024 seq_len<br/>micro_batch_size varies"]
        TORCHRUN["torchrun --nproc_per_node"]
    end
    
    subgraph "Training Scripts"
        STEP3_TRAIN["step3_dataloader/train.py"]
        STEP4_TRAIN["step4_tensor_parallel/train.py"]
        STEP6_TRAIN["step6_data_parallel_bucket/train.py"]
        STEP8_TRAIN["step8_pipeline_parallel_1f1b/train.py"]
    end
    
    subgraph "Validation Metrics"
        LOSS_CURVE["Loss Convergence"]
        WANDB_LOG["WandB Logging"]
        SANITY_CHECK["llama1B_sanity_check.png"]
    end
    
    BASELINE --> STEP3_TRAIN
    TP_TEST --> STEP4_TRAIN
    DP_TEST --> STEP6_TRAIN
    PP_TEST --> STEP8_TRAIN
    
    MODEL_CONFIG --> BASELINE
    MODEL_CONFIG --> TP_TEST
    MODEL_CONFIG --> DP_TEST
    MODEL_CONFIG --> PP_TEST
    MODEL_CONFIG --> TD_TEST
    
    DATA_CONFIG --> TORCHRUN
    TORCHRUN --> STEP3_TRAIN
    TORCHRUN --> STEP4_TRAIN
    TORCHRUN --> STEP6_TRAIN
    TORCHRUN --> STEP8_TRAIN
    
    BASELINE --> LOSS_CURVE
    TP_TEST --> LOSS_CURVE
    DP_TEST --> LOSS_CURVE
    PP_TEST --> LOSS_CURVE
    TD_TEST --> LOSS_CURVE
    
    LOSS_CURVE --> WANDB_LOG
    WANDB_LOG --> SANITY_CHECK
```

### Test Execution Commands

The validation framework provides specific command-line invocations for each parallelism strategy:

| Strategy | Command Parameters | Key Differences |
|----------|-------------------|-----------------|
| Baseline | `--nproc_per_node 1` | Single process, micro_batch_size 4 |
| Tensor Parallel | `--nproc_per_node 4 --tp_size 4` | 4-way tensor parallelism |
| Data Parallel | `--nproc_per_node 4 --dp_size 4` | 4-way data parallelism, micro_batch_size 1 |
| Pipeline Parallel | `--nproc_per_node 4 --pp_size 4 --pp_engine 1f1b` | 4-stage pipeline with 1F1B engine |
| 3D Parallelism | `--nproc_per_node 8 --tp_size 2 --pp_size 2 --dp_size 2` | Combined parallelism strategies |

All tests use identical model configuration (`TinyLlama_v1.1` with 22 layers, 32 attention heads, 4 key-value heads) and training parameters (4096000 tokens, 1024 sequence length) to ensure fair comparison.

**Sources:** [README.md:24-48]()

## Demo Infrastructure

The tutorial includes structured demonstration configurations for educational presentation and video content creation.

```mermaid
graph LR
    subgraph "Demo Configuration"
        DEMO_SCHEMA["demo-time.schema.json"]
        STEP1_DEMO[".demo/step1_modeling.json"]
    end
    
    subgraph "Demo Structure"
        TITLE["title: Step 1: Modeling"]
        DESCRIPTION["description"]
        DEMOS["demos[]"]
    end
    
    subgraph "Demo Actions"
        OPEN_ACTION["action: open"]
        HIGHLIGHT_ACTION["action: highlight"]
        POSITION["position: startLine:endLine"]
    end
    
    subgraph "Target Files"
        MODEL_PY["model.py"]
        TRAIN_PY["train.py"]
        LLAMA_CLASS["Llama class"]
        DECODER_LAYER["DecoderLayer class"]
    end
    
    STEP1_DEMO --> DEMO_SCHEMA
    STEP1_DEMO --> TITLE
    STEP1_DEMO --> DEMOS
    
    DEMOS --> OPEN_ACTION
    DEMOS --> HIGHLIGHT_ACTION
    HIGHLIGHT_ACTION --> POSITION
    
    OPEN_ACTION --> MODEL_PY
    OPEN_ACTION --> TRAIN_PY
    HIGHLIGHT_ACTION --> LLAMA_CLASS
    HIGHLIGHT_ACTION --> DECODER_LAYER
```

### Demo Step Configuration

The demonstration framework defines specific highlighting sequences for educational walkthroughs:

| Demo Section | Target Component | Line Range | Purpose |
|--------------|------------------|------------|---------|
| `model.py -> Llama` | `Llama` class | 135:148 | Model architecture overview |
| `model.py -> DecoderLayer` | `DecoderLayer` class | 100:116 | Layer implementation details |
| `train.py -> args` | Argument parsing | 17:39 | Configuration parameters |
| `train.py -> distributed setup` | Process initialization | 41:54 | Distributed training setup |
| `train.py -> model init` | Model instantiation | 58:66 | Model creation process |
| `train.py -> optimizer init` | Optimizer setup | 70 | Training optimization |
| `train.py -> simple training loop` | Training iteration | 74:97 | Basic training logic |

The demo configuration supports the video tutorial series referenced in the README, providing structured navigation through code components for educational presentation.

**Sources:** [.demo/step1_modeling.json:1-88](), [README.md:5-12]()

## Package Structure

The setup configuration defines the tutorial as an installable Python package with proper dependency management.

```mermaid
graph TB
    subgraph "Package Definition"
        SETUP_NAME["name: picotron_tutorial"]
        SETUP_VERSION["version: 0.1.0"]
        FIND_PACKAGES["find_packages()"]
        INSTALL_REQUIRES["install_requires"]
    end
    
    subgraph "Dependency Management"
        READ_REQUIREMENTS["read_requirements()"]
        REQ_FILE["requirements.txt"]
        FILTER_COMMENTS["filter comments and empty lines"]
    end
    
    subgraph "Installation Process"
        PIP_EDITABLE["pip install -e ."]
        DEVELOPMENT_MODE["Development installation"]
        IMPORT_ACCESS["import picotron_tutorial"]
    end
    
    SETUP_NAME --> FIND_PACKAGES
    SETUP_VERSION --> INSTALL_REQUIRES
    INSTALL_REQUIRES --> READ_REQUIREMENTS
    READ_REQUIREMENTS --> REQ_FILE
    READ_REQUIREMENTS --> FILTER_COMMENTS
    
    PIP_EDITABLE --> DEVELOPMENT_MODE
    DEVELOPMENT_MODE --> IMPORT_ACCESS
```

The `read_requirements()` function in `setup.py` processes the requirements file to extract clean dependency specifications, filtering out comments and empty lines for proper package installation.

**Sources:** [setup.py:1-12](), [requirements.txt:1-7]()