<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/latent-multi-hop-reasoning · page 3 Main Entry Points · fetched 2026-10-26 -->

# Main Entry Points

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides an overview of the three primary scripts that serve as entry points for different experimental approaches in the latent multi-hop reasoning research codebase. These scripts implement the experiments described in two research papers and provide the main interfaces for running evaluations and analyses.

For detailed documentation of each entry point's functionality and implementation, see [Inspect Latent Reasoning](#3.1), [Evaluate Latent Reasoning](#3.2), and [Run Patchscopes](#3.3). For information about the shared utility modules used by these entry points, see [Utility Modules](#4).

## Overview

The codebase provides three main entry points that correspond to different research questions and experimental methodologies:

| Entry Point | Purpose | Associated Paper | Primary Dataset |
|-------------|---------|------------------|-----------------|
| `inspect_latent_reasoning.py` | Latent reasoning pathway inspection | Paper 1 (ACL 2024) | TwoHopFact |
| `evaluate_latent_reasoning.py` | Shortcut-free evaluation | Paper 2 (arXiv 2024) | SOCRATES |
| `run_patchscopes.py` | Patchscopes analysis | Paper 2 (arXiv 2024) | SOCRATES |

Each entry point implements specific experimental approaches and provides command-line interfaces for running different types of analyses on large language models' multi-hop reasoning capabilities.

## Entry Point Architecture

```mermaid
graph TB
    subgraph "Research Papers"
        Paper1["Paper 1: ACL 2024<br/>Do LLMs Latently Perform Multi-Hop Reasoning?"]
        Paper2["Paper 2: arXiv 2024<br/>Do LLMs Perform Latent Multi-Hop Reasoning<br/>without Exploiting Shortcuts?"]
    end
    
    subgraph "Entry Points"
        ILR["inspect_latent_reasoning.py"]
        ELR["evaluate_latent_reasoning.py"] 
        RPS["run_patchscopes.py"]
    end
    
    subgraph "Datasets"
        THF["TwoHopFact.csv<br/>45,595 pairs<br/>52 composition types"]
        SOC["SOCRATES.csv<br/>7,232 pairs<br/>17 composition types"]
    end
    
    subgraph "Experiment Types"
        RQ1["RQ1: First-hop Analysis<br/>--run_rq1"]
        RQ2["RQ2: Second-hop Analysis<br/>--run_rq2"]
        APP["Appositive Validation<br/>--run_appositive"]
        COT["Chain-of-Thought<br/>--run_cot"]
        COMP["Completion Generation<br/>--run_completion"]
        EVAL["Shortcut-Free Evaluation<br/>--run_evaluation"]
        PATCH["Patchscopes Analysis<br/>--run_patchscopes_evaluation"]
    end
    
    Paper1 --> ILR
    Paper2 --> ELR
    Paper2 --> RPS
    
    ILR --> THF
    ELR --> SOC
    RPS --> SOC
    
    ILR --> RQ1
    ILR --> RQ2
    ILR --> APP
    ILR --> COT
    ILR --> COMP
    
    ELR --> EVAL
    RPS --> EVAL
    RPS --> PATCH
```

*Sources: [README.md:1-143]()*

## Command-Line Interfaces

Each entry point provides a comprehensive command-line interface with specific parameters for different experimental configurations:

### inspect_latent_reasoning.py Parameters

```mermaid
graph LR
    subgraph "Core Parameters"
        MODEL["--model_name_or_path<br/>$MODEL_NAME_OR_PATH"]
        INPUT["--input_csv_path<br/>datasets/TwoHopFact.csv"]
        TOKEN["--hf_token<br/>$HF_TOKEN"]
    end
    
    subgraph "Batch Size Configuration"
        RQ1_BATCH["--rq1_batch_size<br/>256"]
        RQ2_BATCH["--rq2_batch_size<br/>8"]
        COMP_BATCH["--completion_batch_size<br/>64"]
    end
    
    subgraph "Experiment Flags"
        RUN_RQ1["--run_rq1"]
        RUN_RQ2["--run_rq2"]
        RUN_APP["--run_appositive"]
        RUN_COT["--run_cot"]
        RUN_COMP["--run_completion"]
    end
    
    MODEL --> RUN_RQ1
    INPUT --> RUN_RQ1
    TOKEN --> RUN_RQ1
    RQ1_BATCH --> RUN_RQ1
    RQ2_BATCH --> RUN_RQ2
    COMP_BATCH --> RUN_COMP
```

### evaluate_latent_reasoning.py Parameters

```mermaid
graph LR
    subgraph "Core Parameters"
        MODEL2["--model_name_or_path<br/>$MODEL_NAME_OR_PATH"]
        INPUT2["--input_csv_path<br/>datasets/SOCRATES.csv"]
        TOKEN2["--hf_token<br/>$HF_TOKEN"]
    end
    
    subgraph "Performance Configuration"
        PARALLEL["--tensor_parallel_size<br/>2"]
        BATCH2["--batch_size<br/>256"]
    end
    
    MODEL2 --> PARALLEL
    INPUT2 --> BATCH2
    TOKEN2 --> PARALLEL
```

### run_patchscopes.py Parameters

```mermaid
graph LR
    subgraph "Core Parameters"
        MODEL3["--model_name_or_path<br/>$MODEL_NAME_OR_PATH"]
        INPUT3["--input_csv_path<br/>datasets/SOCRATES.csv"]
        TOKEN3["--hf_token<br/>$HF_TOKEN"]
    end
    
    subgraph "Patchscopes Configuration"
        BATCH3["--batch_size<br/>64"]
        SOURCE["--source_layer_idxs<br/>1,2"]
        TARGET["--target_layer_idxs<br/>30,31"]
    end
    
    subgraph "Analysis Flags"
        RUN_EVAL["--run_evaluation"]
        RUN_PATCH["--run_patchscopes_evaluation"]
    end
    
    MODEL3 --> SOURCE
    INPUT3 --> TARGET
    TOKEN3 --> BATCH3
    SOURCE --> RUN_EVAL
    TARGET --> RUN_PATCH
```

*Sources: [README.md:42-81]()*

## Experimental Pipeline Flow

The entry points implement different experimental pipelines that address specific research questions:

```mermaid
flowchart TD
    START["Research Question"] --> DATASET{Dataset Selection}
    
    DATASET -->|"Latent Reasoning Inspection"| THF_FLOW["TwoHopFact.csv"]
    DATASET -->|"Shortcut-Free Evaluation"| SOC_FLOW["SOCRATES.csv"]
    
    THF_FLOW --> ILR_SCRIPT["inspect_latent_reasoning.py"]
    SOC_FLOW --> ELR_SCRIPT["evaluate_latent_reasoning.py"]
    SOC_FLOW --> RPS_SCRIPT["run_patchscopes.py"]
    
    subgraph "Inspection Experiments"
        ILR_SCRIPT --> RQ1_EXP["run_rq1()<br/>First-hop entity recall"]
        ILR_SCRIPT --> RQ2_EXP["run_rq2()<br/>Second-hop consistency"]
        ILR_SCRIPT --> APP_EXP["run_appositive()<br/>Validation experiments"]
        ILR_SCRIPT --> COT_EXP["run_cot()<br/>Chain-of-thought analysis"]
        ILR_SCRIPT --> COMP_EXP["run_completion()<br/>Standard completion"]
    end
    
    subgraph "Evaluation Experiments"
        ELR_SCRIPT --> SF_EXP["shortcut_free_evaluation()<br/>Accuracy-based assessment"]
        RPS_SCRIPT --> PATCH_EXP["patchscopes_evaluation()<br/>Layer intervention analysis"]
    end
    
    RQ1_EXP --> RESULTS["results/ directory<br/>Timestamped CSV outputs"]
    RQ2_EXP --> RESULTS
    APP_EXP --> RESULTS
    COT_EXP --> RESULTS
    COMP_EXP --> RESULTS
    SF_EXP --> RESULTS
    PATCH_EXP --> RESULTS
```

*Sources: [README.md:40-81]()*

## Shared Infrastructure

All entry points utilize common infrastructure components from the `src/` directory:

| Utility Module | Functions Used | Purpose |
|----------------|----------------|---------|
| `data_utils.py` | `read_dataframe()`, `efficient_batchify()` | Dataset loading and batch processing |
| `model_utils.py` | `get_unembedding_matrix()`, `get_layers()` | Model loading and manipulation |
| `tokenization_utils.py` | `to_tokens()`, `get_completion()` | Text processing and tokenization |
| `evaluation_utils.py` | `run_completion()`, `shortcut_free_evaluation()` | Evaluation logic implementation |
| `inspection_utils.py` | `run_rq1()`, `run_rq2()`, `activation_patching()` | Latent reasoning inspection |
| `patchscopes_utils.py` | `get_hidden_states()`, `generate_with_patching()` | Patchscopes analysis |

The entry points serve as orchestrators that coordinate these utility modules to implement specific experimental workflows, handling command-line argument parsing, experiment execution, and result output management.

*Sources: [README.md:83-93]()*

---

