<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/acon · page 8 Model Distillation · fetched 2026-10-26 -->

# Model Distillation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [experiments/appworld/README.md](experiments/appworld/README.md)

</details>



This page describes the model distillation process in ACON, which enables training local models to replicate the behavior of frontier models through a two-stage LoRA fine-tuning approach. For configuration details about context optimization that produces the training data, see [Context Optimization Configuration](#6.2). For details on running experiments with distilled models, see [Batch Experiment Execution](#5.2).

## Purpose and Scope

Model distillation in ACON transforms expensive frontier model capabilities (e.g., GPT-4) into efficient local models (e.g., Qwen3-14B) through Low-Rank Adaptation (LoRA) fine-tuning. This enables cost-effective deployment while maintaining performance on context compression and agent reasoning tasks.

The distillation pipeline consists of two sequential stages:
1. **Compressor LoRA**: Distills context compression capabilities from frontier model optimizer traces
2. **Agent LoRA**: Distills agent reasoning and action selection from frontier model agent traces

Both stages operate on trajectories generated from baseline experiments, creating supervised fine-tuning datasets that teach the local model to mimic frontier model behavior.

## Two-Stage Distillation Architecture

```mermaid
graph TB
    subgraph "Input: Frontier Model Trajectories"
        BASELINE["Baseline Experiment<br/>(e.g., gpt-4.1_baseline)"]
        OPTIMIZED["Context-Optimized Experiment<br/>(e.g., gpt-4.1_history_compression)"]
    end
    
    subgraph "Stage 1: Compressor Distillation"
        EXTRACT_COMP["save_trajectories_dataset.py<br/>--type history_optimizer_history"]
        DATASET_COMP["Training Dataset<br/>history_optimizer_history/*.jsonl"]
        FINETUNE_COMP["run_finetune.sh<br/>Trains Compressor LoRA"]
        LORA_COMP["Compressor LoRA Adapter<br/>(e.g., history_compression_3epochs)"]
        SERVE_COMP["serve_single.sh<br/>Base Model + Compressor LoRA"]
    end
    
    subgraph "Stage 2: Agent Distillation"
        EXTRACT_AGENT["save_trajectories_dataset.py<br/>--type llm_history"]
        DATASET_AGENT["Training Dataset<br/>llm_history/*.jsonl"]
        FINETUNE_AGENT["run_finetune_agent.sh<br/>Trains Agent LoRA"]
        LORA_AGENT["Agent LoRA Adapter<br/>(e.g., agent_history_v2_3epochs)"]
        SERVE_AGENT["serve_agent.sh<br/>Base Model + Compressor + Agent LoRAs"]
    end
    
    subgraph "Deployment"
        INFERENCE["Model Server<br/>(vLLM or compatible)"]
        CONFIG["Context Optimization Config<br/>(lora_name parameter)"]
        EVAL["Experiment Execution<br/>(run_all.py)"]
    end
    
    OPTIMIZED --> EXTRACT_COMP
    EXTRACT_COMP --> DATASET_COMP
    DATASET_COMP --> FINETUNE_COMP
    FINETUNE_COMP --> LORA_COMP
    LORA_COMP --> SERVE_COMP
    
    SERVE_COMP -.enables.-> EXTRACT_AGENT
    BASELINE --> EXTRACT_AGENT
    EXTRACT_AGENT --> DATASET_AGENT
    DATASET_AGENT --> FINETUNE_AGENT
    FINETUNE_AGENT --> LORA_AGENT
    LORA_AGENT --> SERVE_AGENT
    
    SERVE_AGENT --> INFERENCE
    LORA_COMP --> CONFIG
    LORA_AGENT --> CONFIG
    CONFIG --> EVAL
    INFERENCE --> EVAL
```

**Diagram: Two-Stage Distillation Pipeline**

This architecture shows the complete distillation workflow. Stage 1 extracts context compression interactions from frontier model trajectories to train a compressor LoRA. Stage 2 builds upon the compressor by extracting agent reasoning traces to train an agent LoRA. The final deployment stacks both LoRAs on a base model for inference.

**Sources:** [experiments/appworld/README.md:135-237](), [README.md:132-137]()

## Training Data Generation

Training data for distillation is extracted from completed experiment trajectories using `save_trajectories_dataset.py`. This script converts interaction histories into supervised fine-tuning format.

### Data Extraction Process

```mermaid
graph LR
    subgraph "Experiment Outputs"
        TASK_DIR["outputs/{model}_{tag}/{split}/<br/>task_*/*"]
        HIST_OPT["history_optimizer_history.json<br/>(Compressor traces)"]
        LLM_HIST["llm_history.json<br/>(Agent traces)"]
        ENV_HIST["env_history.json<br/>(Environment state)"]
    end
    
    subgraph "save_trajectories_dataset.py"
        SCAN["scan_experiment_directory()<br/>Discovers task directories"]
        PARSE["parse_trajectory_file()<br/>Extracts messages"]
        FORMAT["format_training_sample()<br/>Creates input-output pairs"]
        WRITE["write_jsonl()<br/>Saves training dataset"]
    end
    
    subgraph "Training Datasets"
        COMP_DATA["dataset/history_optimizer_history/<br/>{model}_{tag}_train.jsonl"]
        AGENT_DATA["dataset/llm_history/<br/>{model}_{tag}_train.jsonl"]
    end
    
    TASK_DIR --> SCAN
    SCAN --> HIST_OPT
    SCAN --> LLM_HIST
    
    HIST_OPT --> PARSE
    LLM_HIST --> PARSE
    
    PARSE --> FORMAT
    FORMAT --> WRITE
    
    WRITE --> COMP_DATA
    WRITE --> AGENT_DATA
```

**Diagram: Training Data Extraction Pipeline**

The extraction process scans experiment output directories, parses trajectory JSON files, and formats interactions as training samples in JSONL format.

**Sources:** [experiments/appworld/README.md:144-152](), [experiments/appworld/README.md:201-209]()

### Training Data Format

Each training sample in the JSONL dataset follows this structure:

| Field | Description | Source |
|-------|-------------|--------|
| `messages` | List of conversation turns | Extracted from trajectory history |
| `messages[].role` | Role identifier (`system`, `user`, `assistant`) | Determined by message type |
| `messages[].content` | Message text | Verbatim from trajectory |

**Compressor Training Data** (`history_optimizer_history`):
- Extracts interactions between the agent and the history optimizer
- Teaches the model to compress long context into concise summaries
- Input: Full history + compression guidelines
- Output: Compressed summary

**Agent Training Data** (`llm_history`):
- Extracts interactions between the agent and the LLM
- Teaches the model to perform reasoning and action selection
- Input: Task description + observation + (compressed) history
- Output: Reasoning chain + selected action

**Sources:** [experiments/appworld/README.md:144-152](), [experiments/appworld/README.md:201-209]()

## LoRA Architecture and Stacking

ACON uses Low-Rank Adaptation (LoRA) to efficiently fine-tune large language models without modifying the base model weights. The two-stage approach creates specialized LoRA adapters that can be stacked during inference.

```mermaid
graph TB
    subgraph "Base Model Layer"
        BASE["Base Model<br/>(e.g., Qwen/Qwen3-14B)<br/>Frozen Weights"]
    end
    
    subgraph "LoRA Adapters"
        LORA_1["Compressor LoRA<br/>(history_compression_3epochs)<br/>Rank-64 Low-Rank Matrices"]
        LORA_2["Agent LoRA<br/>(agent_history_v2_3epochs)<br/>Rank-64 Low-Rank Matrices"]
    end
    
    subgraph "Inference Modes"
        MODE_1["Compressor-Only Mode<br/>(serve_single.sh)<br/>Base + LoRA_1"]
        MODE_2["Full Agent Mode<br/>(serve_agent.sh)<br/>Base + LoRA_1 + LoRA_2"]
    end
    
    BASE --> LORA_1
    LORA_1 --> LORA_2
    
    BASE --> MODE_1
    LORA_1 --> MODE_1
    
    BASE --> MODE_2
    LORA_1 --> MODE_2
    LORA_2 --> MODE_2
```

**Diagram: LoRA Adapter Stacking Architecture**

The base model remains frozen during training. Compressor LoRA adapts the model for context compression. Agent LoRA builds on top for reasoning. During inference, adapters can be loaded individually or stacked together.

**Sources:** [experiments/appworld/README.md:163-169](), [experiments/appworld/README.md:220-227]()

### Training Configuration

Fine-tuning is performed using the `unsloth` library for efficient LoRA training. Key training parameters:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `max_seq_length` | 2048 | Maximum sequence length for training |
| `lora_r` | 64 | LoRA rank (adapter dimension) |
| `lora_alpha` | 16 | LoRA scaling factor |
| `learning_rate` | 2e-4 | Optimizer learning rate |
| `num_train_epochs` | 3 | Number of training epochs |

**Sources:** [experiments/appworld/README.md:154-161](), [experiments/appworld/README.md:211-218]()

## File and Component Reference

### Training Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `save_trajectories_dataset.py` | [experiments/training/]() | Extracts training data from experiment outputs |
| `run_finetune.sh` | [experiments/training/scripts/]() | Trains compressor LoRA adapter |
| `run_finetune_agent.sh` | [experiments/training/scripts/]() | Trains agent LoRA adapter |

### Serving Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `serve_single.sh` | [experiments/training/scripts/]() | Serves base model + compressor LoRA |
| `serve_agent.sh` | [experiments/training/scripts/]() | Serves base model + stacked LoRAs |

### Configuration Integration

Distilled models are specified in context optimization configuration files via the `lora_name` parameter:

```yaml
type: history
model: "Qwen/Qwen3-14B"
lora_name: "finetune=finetuned_models/qwen-14B/history_compression_3epochs"
compressor_type: full
prompts:
    prompt_system: system_prompt
    prompt_history_user: prompt_history_v2
history_summarization_threshold: 4096
preserve_last_k_turns: 1
history_summary_rule: reset
```

The `lora_name` field uses the format `finetune={path_to_lora_adapter}` to load the specified adapter during inference. For stacked LoRAs (compressor + agent), the serving script manages multiple adapter loading.

**Sources:** [experiments/appworld/README.md:171-184](), [experiments/appworld/README.md:229-236]()

## Distillation Workflow Summary

```mermaid
flowchart TD
    START["Start: Baseline Experiments Complete"]
    
    STAGE1_DATA["Generate Compressor Dataset<br/>save_trajectories_dataset.py<br/>-t history_optimizer_history"]
    STAGE1_TRAIN["Train Compressor LoRA<br/>run_finetune.sh"]
    STAGE1_SERVE["Serve Compressor Model<br/>serve_single.sh"]
    STAGE1_EVAL["Evaluate Compressor<br/>(Optional validation)"]
    
    STAGE2_DATA["Generate Agent Dataset<br/>save_trajectories_dataset.py<br/>-t llm_history"]
    STAGE2_TRAIN["Train Agent LoRA<br/>run_finetune_agent.sh"]
    STAGE2_SERVE["Serve Stacked Model<br/>serve_agent.sh"]
    STAGE2_EVAL["Evaluate Full Agent<br/>run_all.py"]
    
    END["Deployed: Local Model<br/>with Frontier Performance"]
    
    START --> STAGE1_DATA
    STAGE1_DATA --> STAGE1_TRAIN
    STAGE1_TRAIN --> STAGE1_SERVE
    STAGE1_SERVE --> STAGE1_EVAL
    
    STAGE1_EVAL --> STAGE2_DATA
    STAGE2_DATA --> STAGE2_TRAIN
    STAGE2_TRAIN --> STAGE2_SERVE
    STAGE2_SERVE --> STAGE2_EVAL
    
    STAGE2_EVAL --> END
```

**Diagram: Complete Distillation Workflow**

This flowchart shows the sequential execution of the two-stage distillation process, from initial data generation through final deployment of the stacked LoRA model.

**Sources:** [experiments/appworld/README.md:135-237](), [README.md:132-137]()

## Key Concepts

### Progressive Distillation

ACON uses a progressive approach where each stage builds upon the previous:

1. **Stage 1 (Compressor)**: Teaches the model to compress context efficiently
2. **Stage 2 (Agent)**: Assumes compression capability and teaches reasoning/action selection

This sequential approach allows the agent LoRA to focus on high-level decision-making while relying on the compressor LoRA for context management.

### Training Data Source Requirements

| Distillation Stage | Required Experiment Type | Trajectory File |
|-------------------|-------------------------|-----------------|
| Compressor LoRA | Context-optimized run | `history_optimizer_history.json` |
| Agent LoRA | Baseline or optimized run | `llm_history.json` |

The compressor requires trajectories where context compression was active, while the agent can use any complete run where the frontier model demonstrated effective reasoning.

### Model Serving Modes

ACON supports two serving configurations:

1. **Compressor-Only**: Base model + compressor LoRA only
   - Use case: Validating compression quality before agent training
   - Served via: `serve_single.sh`

2. **Full Agent**: Base model + compressor LoRA + agent LoRA
   - Use case: Production deployment with full capabilities
   - Served via: `serve_agent.sh`

**Sources:** [experiments/appworld/README.md:135-237]()

---

