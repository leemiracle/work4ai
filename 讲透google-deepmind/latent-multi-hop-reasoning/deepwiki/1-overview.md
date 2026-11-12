<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/latent-multi-hop-reasoning · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides a technical overview of the latent multi-hop reasoning research codebase, which investigates whether Large Language Models (LLMs) perform multi-hop reasoning internally. The codebase implements experimental methodologies from two research papers that probe LLM reasoning mechanisms through different approaches: latent reasoning inspection and shortcut-free evaluation.

For detailed setup instructions, see [Getting Started](#2). For specific experimental implementations, see [Main Entry Points](#3). For dataset specifications, see [Datasets](#5).

## Research Papers and Scope

This codebase implements two complementary research investigations:

| Paper | Venue | Primary Focus | Main Dataset |
|-------|--------|---------------|--------------|
| Do Large Language Models Latently Perform Multi-Hop Reasoning? | ACL 2024 | Internal reasoning pathway inspection | TwoHopFact |
| Do Large Language Models Perform Latent Multi-Hop Reasoning without Exploiting Shortcuts? | arXiv 2024 | Shortcut-free evaluation and layer analysis | SOCRATES |

### Research Questions Addressed

The codebase systematically investigates three core research questions through different experimental methodologies:

- **RQ1**: How often do LLMs perform the first hop of reasoning in two-hop prompts?
- **RQ2**: How often do LLMs perform the second hop, and what is the consistency between single-hop and multi-hop reasoning?
- **Shortcut Analysis**: Do LLMs exploit superficial patterns instead of performing genuine multi-hop reasoning?

## System Architecture

### High-Level Component Organization

```mermaid
graph TB
    subgraph "Research Papers"
        P1["Paper 1: ACL 2024<br/>Latent Reasoning Inspection"]
        P2["Paper 2: arXiv 2024<br/>Shortcut-Free Evaluation"]
    end
    
    subgraph "Main Entry Points"
        ILR["inspect_latent_reasoning.py"]
        ELR["evaluate_latent_reasoning.py"] 
        RPS["run_patchscopes.py"]
    end
    
    subgraph "Datasets"
        THF["TwoHopFact.csv<br/>45,595 pairs<br/>52 composition types"]
        SOC["SOCRATES.csv<br/>7,232 pairs<br/>17 composition types"]
    end
    
    subgraph "Shared Utilities (src/)"
        DU["data_utils.py"]
        MU["model_utils.py"]
        TU["tokenization_utils.py"]
        IU["inspection_utils.py"]
        EU["evaluation_utils.py"]
        PU["patchscopes_utils.py"]
    end
    
    P1 --> ILR
    P2 --> ELR
    P2 --> RPS
    
    THF --> ILR
    SOC --> ELR
    SOC --> RPS
    
    ILR --> DU
    ILR --> MU
    ILR --> TU
    ILR --> IU
    
    ELR --> DU
    ELR --> MU
    ELR --> EU
    
    RPS --> DU
    RPS --> MU
    RPS --> PU
    RPS --> EU
```

Sources: [README.md:3-6](), [README.md:83-93]()

### Experimental Pipeline Mapping

```mermaid
flowchart TD
    subgraph "Input Processing"
        CSV_INPUT["CSV Dataset Files<br/>TwoHopFact.csv / SOCRATES.csv"]
        READ_DF["data_utils.read_dataframe()"]
        BATCH_PROC["data_utils.efficient_batchify()"]
    end
    
    subgraph "Model Operations"
        MODEL_LOAD["model_utils.get_layers()<br/>model_utils.get_unembedding_matrix()"]
        TOKENIZE["tokenization_utils.to_tokens()<br/>tokenization_utils.get_completion()"]
    end
    
    subgraph "Experimental Methods"
        RQ1_EXP["inspection_utils.run_rq1()<br/>Internal entity recall"]
        RQ2_EXP["inspection_utils.run_rq2()<br/>Consistency analysis"]
        SHORTCUT_EVAL["evaluation_utils.shortcut_free_evaluation()<br/>Accuracy-based assessment"]
        PATCH_EVAL["patchscopes_utils.generate_with_patching()<br/>Layer intervention"]
    end
    
    subgraph "Analysis Output"
        RESULTS_DIR["results/<timestamp>/<experiment_type>/"]
        ENHANCED_CSV["Enhanced CSV with metrics"]
    end
    
    CSV_INPUT --> READ_DF
    READ_DF --> BATCH_PROC
    BATCH_PROC --> MODEL_LOAD
    MODEL_LOAD --> TOKENIZE
    
    TOKENIZE --> RQ1_EXP
    TOKENIZE --> RQ2_EXP
    TOKENIZE --> SHORTCUT_EVAL
    TOKENIZE --> PATCH_EVAL
    
    RQ1_EXP --> RESULTS_DIR
    RQ2_EXP --> RESULTS_DIR
    SHORTCUT_EVAL --> RESULTS_DIR
    PATCH_EVAL --> RESULTS_DIR
    
    RESULTS_DIR --> ENHANCED_CSV
```

Sources: [README.md:88-92](), [README.md:46-55](), [README.md:61-81]()

## Entry Points and Experimental Approaches

The codebase provides three main entry points, each implementing specific experimental methodologies:

### Entry Point Summary

| Script | Purpose | Primary Functions | Batch Size Parameters |
|--------|---------|-------------------|----------------------|
| `inspect_latent_reasoning.py` | Paper 1 experiments | RQ1, RQ2, validation studies | `--rq1_batch_size`, `--rq2_batch_size`, `--completion_batch_size` |
| `evaluate_latent_reasoning.py` | Paper 2 shortcut-free evaluation | Completion generation, accuracy metrics | `--batch_size`, `--tensor_parallel_size` |
| `run_patchscopes.py` | Paper 2 patchscopes analysis | Layer intervention, hidden state patching | `--batch_size`, `--source_layer_idxs`, `--target_layer_idxs` |

### Experimental Method Implementation

```mermaid
graph TB
    subgraph "inspect_latent_reasoning.py"
        RQ1_IMPL["--run_rq1<br/>inspection_utils.run_rq1()<br/>fill_full_latent_info()"]
        RQ2_IMPL["--run_rq2<br/>inspection_utils.run_rq2()<br/>activation_patching()"]
        APPOS_IMPL["--run_appositive<br/>Entity recall validation"]
        COT_IMPL["--run_cot<br/>Chain-of-thought validation"]
        COMP_IMPL["--run_completion<br/>Standard completion generation"]
    end
    
    subgraph "evaluate_latent_reasoning.py"
        SF_EVAL["evaluation_utils.run_completion()<br/>shortcut_free_evaluation()"]
    end
    
    subgraph "run_patchscopes.py" 
        PATCH_EVAL["--run_evaluation<br/>--run_patchscopes_evaluation<br/>patchscopes_utils.get_hidden_states()"]
        LAYER_INT["generate_with_patching()<br/>layer_intervention()"]
    end
    
    RQ1_IMPL --> SF_EVAL
    RQ2_IMPL --> PATCH_EVAL
    APPOS_IMPL --> LAYER_INT
```

Sources: [README.md:46-55](), [README.md:61-68](), [README.md:72-81]()

## Key Dataset Specifications

The research utilizes two purpose-built datasets for different experimental approaches:

### Dataset Comparison

| Dataset | Size | Composition Types | Primary Use | File Location |
|---------|------|-------------------|-------------|---------------|
| TwoHopFact | 45,595 pairs | 52 types | Latent reasoning inspection | `datasets/TwoHopFact.csv` |
| SOCRATES v0 | 7,232 pairs | 17 types | Paper 2 experiments (with grammatical errors) | `datasets/SOCRATES_v0.csv` |
| SOCRATES v1 | 7,232 pairs | 17 types | Cleaned dataset (no grammatical errors) | `datasets/SOCRATES_v1.csv` |

Both datasets are also available via HuggingFace: `soheeyang/TwoHopFact` and `soheeyang/SOCRATES`.

Sources: [README.md:25-38]()

## Code Organization Structure

The codebase follows a modular architecture with shared utilities and experiment-specific implementations:

### Directory Structure

```mermaid
graph TB
    subgraph "Root Directory"
        MAIN_SCRIPTS["inspect_latent_reasoning.py<br/>evaluate_latent_reasoning.py<br/>run_patchscopes.py"]
    end
    
    subgraph "src/ (Utilities)"
        COMMON["data_utils.py<br/>model_utils.py<br/>tokenization_utils.py"]
        PAPER1["inspection_utils.py"]
        PAPER2["evaluation_utils.py<br/>patchscopes_utils.py"]
    end
    
    subgraph "datasets/"
        DATA_FILES["TwoHopFact.csv<br/>SOCRATES_v0.csv<br/>SOCRATES_v1.csv"]
    end
    
    subgraph "results/"
        OUTPUT["Timestamped experiment outputs<br/>Enhanced CSV files with metrics"]
    end
    
    MAIN_SCRIPTS --> COMMON
    MAIN_SCRIPTS --> PAPER1
    MAIN_SCRIPTS --> PAPER2
    MAIN_SCRIPTS --> DATA_FILES
    MAIN_SCRIPTS --> OUTPUT
```

### Utility Module Responsibilities

| Module | Primary Functions | Used By |
|--------|-------------------|---------|
| `data_utils.py` | `read_dataframe()`, `efficient_batchify()`, `batchify()` | All entry points |
| `model_utils.py` | `get_unembedding_matrix()`, `get_layers()`, `is_instruction_tuned()` | All entry points |
| `tokenization_utils.py` | `to_tokens()`, `find_substrings()`, `get_completion()` | All entry points |
| `inspection_utils.py` | `run_rq1()`, `run_rq2()`, `activation_patching()` | `inspect_latent_reasoning.py` |
| `evaluation_utils.py` | `run_completion()`, `shortcut_free_evaluation()` | `evaluate_latent_reasoning.py`, `run_patchscopes.py` |
| `patchscopes_utils.py` | `get_hidden_states()`, `generate_with_patching()` | `run_patchscopes.py` |

Sources: [README.md:83-93]()

The codebase requires HuggingFace authentication via the `HF_TOKEN` environment variable for accessing certain models, and outputs all experimental results to the `results/` directory with timestamp-based organization.

Sources: [README.md:17-18](), [README.md:93]()

---

