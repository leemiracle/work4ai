<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/reward-bench · page 4 CLI Reference · fetched 2026-10-26 -->

# CLI Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rewardbench/models/armorm.py](rewardbench/models/armorm.py)
- [rewardbench/rewardbench.py](rewardbench/rewardbench.py)
- [setup.py](setup.py)
- [tests/test_package.py](tests/test_package.py)

</details>



This document provides a comprehensive reference for RewardBench's command-line interfaces. The CLI tools provide quick access to the evaluation framework's core functionality, allowing users to evaluate reward models, DPO models, and generative models with simple commands.

For detailed information about different evaluation approaches, see [Model Evaluation](#5). For configuration options and model setup, see [Configuration](#6).

## CLI Tools Overview

RewardBench provides two main command-line tools installed as console scripts:

| Command | Purpose | Primary Use Case |
|---------|---------|------------------|
| `rewardbench` | Standard reward model and DPO evaluation | Evaluating sequence classification reward models and DPO models |
| `rewardbench-gen` | Generative model evaluation | Evaluating LLM-as-a-judge models via API or local inference |

### CLI Architecture

```mermaid
graph TB
    subgraph "CLI Entry Points"
        CLI_MAIN["rewardbench<br/>(rewardbench.py:main)"]
        CLI_GEN["rewardbench-gen<br/>(run_generative.py:main)"]
    end
    
    subgraph "Argument Processing"
        ARGS_CLASS["Args dataclass<br/>(rewardbench.py:48-107)"]
        HF_PARSER["HfArgumentParser<br/>(rewardbench.py:202)"]
    end
    
    subgraph "Evaluation Engines"
        RM_PIPELINE["Reward Model Pipeline<br/>(RewardBenchPipeline)"]
        DPO_PIPELINE["DPO Pipeline<br/>(DPOInference)"]
        GEN_PIPELINE["Generative Pipeline<br/>(VLLM/API)"]
    end
    
    subgraph "Configuration System"
        REWARD_CONFIG["REWARD_MODEL_CONFIG"]
        DPO_CONFIG["DPO_MODEL_CONFIG"] 
        EVAL_CONFIG["eval_configs.yaml"]
    end
    
    CLI_MAIN --> HF_PARSER
    CLI_GEN --> HF_PARSER
    HF_PARSER --> ARGS_CLASS
    
    ARGS_CLASS --> RM_PIPELINE
    ARGS_CLASS --> DPO_PIPELINE
    ARGS_CLASS --> GEN_PIPELINE
    
    RM_PIPELINE --> REWARD_CONFIG
    DPO_PIPELINE --> DPO_CONFIG
    GEN_PIPELINE --> EVAL_CONFIG
```

Sources: [setup.py:26-31](), [rewardbench/rewardbench.py:48-107](), [rewardbench/rewardbench.py:202-203]()

## Main `rewardbench` Command

The primary CLI tool for evaluating reward models and DPO models. It uses the `Args` dataclass to define all available command-line arguments.

### Command Structure

```bash
rewardbench [OPTIONS]
```

### Argument Categories

The CLI arguments are organized into logical groups within the `Args` dataclass:

```mermaid
graph TB
    subgraph "Args Dataclass Structure"
        CORE["Core Arguments<br/>dataset, model, revision<br/>ref_model, tokenizer"]
        HF_SAVE["HuggingFace Integration<br/>push_results_to_hub<br/>upload_model_metadata_to_hf"]
        WANDB["Weights & Biases<br/>wandb_run"]
        INFERENCE["Inference Parameters<br/>batch_size, max_length<br/>torch_dtype, attn_implementation"]
        SYSTEM["System Configuration<br/>debug, output_dir<br/>trust_remote_code"]
    end
    
    subgraph "Evaluation Modes"
        REWARD_MODE["Reward Model Mode<br/>(no ref_model)"]
        DPO_MODE["DPO Mode<br/>(with ref_model)"]
    end
    
    CORE --> REWARD_MODE
    CORE --> DPO_MODE
    INFERENCE --> REWARD_MODE
    INFERENCE --> DPO_MODE
    HF_SAVE --> REWARD_MODE
    HF_SAVE --> DPO_MODE
```

Sources: [rewardbench/rewardbench.py:48-107](), [rewardbench/rewardbench.py:237-246]()

### Core Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--dataset` | str | `"allenai/reward-bench"` | Dataset to evaluate on |
| `--split` | str | None | Dataset split to use |
| `--model` | str | None | Model to evaluate |
| `--revision` | str | None | Model revision/branch |
| `--ref_model` | str | None | Reference model for DPO evaluation |
| `--tokenizer` | str | None | Tokenizer path (defaults to model) |
| `--chat_template` | str | None | Chat template name |
| `--not_quantized` | bool | False | Disable quantization |
| `--prioritize_scoring` | bool | False | Prioritize scoring over ranking |

### Inference Parameters

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--batch_size` | int | 8 | Batch size for inference |
| `--max_length` | int | 512 | Maximum sequence length |
| `--torch_dtype` | str | `"float16"` | PyTorch data type |
| `--attn_implementation` | str | None | Attention implementation |

### Output and Integration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--output_dir` | str | `"results/"` | Output directory |
| `--save_all` | bool | False | Save detailed results |
| `--push_results_to_hub` | bool | False | Push results to HF Hub |
| `--upload_model_metadata_to_hf` | bool | False | Update model cards |
| `--hf_entity` | str | None | HuggingFace entity |
| `--hf_name` | str | None | HuggingFace dataset name |

### System Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--debug` | bool | False | Enable debug mode |
| `--trust_remote_code` | bool | False | Trust remote code |
| `--load_json` | bool | False | Load dataset as JSON |
| `--force_truncation` | bool | False | Force truncation on errors |

Sources: [rewardbench/rewardbench.py:50-107]()

### Usage Examples

**Basic reward model evaluation:**
```bash
rewardbench --model "OpenAssistant/reward-model-deberta-v3-large-v2"
```

**DPO model evaluation:**
```bash
rewardbench --model "microsoft/DialoGPT-medium" --ref_model "microsoft/DialoGPT-small"
```

**Custom dataset evaluation:**
```bash
rewardbench --model "my-model" --dataset "custom/dataset" --split "test"
```

**Debug mode with custom output:**
```bash
rewardbench --model "my-model" --debug --output_dir "debug_results/"
```

## `rewardbench-gen` Command

The generative evaluation CLI tool for LLM-as-a-judge models, supporting both API-based and local inference.

### Command Structure

```bash
rewardbench-gen [OPTIONS]
```

This command is an alias for the `run_generative.py` script's main function, configured via the setup.py entry point.

### Evaluation Flow

```mermaid
graph TD
    subgraph "rewardbench-gen Execution"
        ENTRY["rewardbench-gen command"]
        SCRIPT["scripts/run_generative.py:main"]
        CONFIG["eval_configs.yaml lookup"]
    end
    
    subgraph "Model Detection"
        API_CHECK{"API Model?"}
        LOCAL_CHECK{"Local Model?"}
    end
    
    subgraph "Inference Backends"
        OPENAI["OpenAI API"]
        ANTHROPIC["Anthropic API"]
        TOGETHER["Together AI"]
        VLLM["VLLM Local"]
    end
    
    subgraph "Processing Pipeline"
        PROMPTS["LLM-as-a-Judge Prompts"]
        PARSE["Response Parsing"]
        RESULTS["Result Aggregation"]
    end
    
    ENTRY --> SCRIPT
    SCRIPT --> CONFIG
    CONFIG --> API_CHECK
    CONFIG --> LOCAL_CHECK
    
    API_CHECK --> OPENAI
    API_CHECK --> ANTHROPIC
    API_CHECK --> TOGETHER
    LOCAL_CHECK --> VLLM
    
    OPENAI --> PROMPTS
    ANTHROPIC --> PROMPTS
    TOGETHER --> PROMPTS
    VLLM --> PROMPTS
    
    PROMPTS --> PARSE
    PARSE --> RESULTS
```

Sources: [setup.py:29](), [scripts/run_generative.py:main]()

## Integration with Configuration System

The CLI tools integrate closely with RewardBench's configuration system to determine model loading and evaluation behavior.

### Configuration Resolution

```mermaid
graph LR
    subgraph "CLI Input"
        MODEL_ARG["--model argument"]
        REF_MODEL_ARG["--ref_model argument"]
    end
    
    subgraph "Configuration Lookup"
        REWARD_LOOKUP["REWARD_MODEL_CONFIG lookup"]
        DPO_LOOKUP["DPO_MODEL_CONFIG lookup"]
        DEFAULT_CONFIG["default config fallback"]
    end
    
    subgraph "Model Loading"
        AUTO_SEQ["AutoModelForSequenceClassification"]
        AUTO_CAUSAL["AutoModelForCausalLM"]
        CUSTOM_BUILDER["Custom model builders"]
    end
    
    MODEL_ARG --> REWARD_LOOKUP
    REF_MODEL_ARG --> DPO_LOOKUP
    
    REWARD_LOOKUP --> AUTO_SEQ
    REWARD_LOOKUP --> CUSTOM_BUILDER
    DPO_LOOKUP --> AUTO_CAUSAL
    
    REWARD_LOOKUP --> DEFAULT_CONFIG
    DPO_LOOKUP --> DEFAULT_CONFIG
    DEFAULT_CONFIG --> AUTO_SEQ
```

Sources: [rewardbench/rewardbench.py:255-259](), [rewardbench/rewardbench.py:237-246]()

## Common Usage Patterns

### Evaluation Pipeline Selection

The CLI automatically selects the appropriate evaluation pipeline based on the presence of the `--ref_model` argument:

```mermaid
graph TD
    CLI_START["CLI Start"]
    REF_CHECK{"ref_model provided?"}
    
    subgraph "DPO Pipeline"
        DPO_CONFIG["DPO_MODEL_CONFIG"]
        DPO_INFERENCE["DPOInference"]
        DPO_TOKENIZE["Tokenize dataset"]
        DPO_EVAL["DPO evaluation"]
    end
    
    subgraph "Reward Model Pipeline"
        REWARD_CONFIG["REWARD_MODEL_CONFIG"]
        REWARD_PIPE["RewardBenchPipeline"]
        REWARD_EVAL["Standard evaluation"]
    end
    
    CLI_START --> REF_CHECK
    REF_CHECK -->|Yes| DPO_CONFIG
    REF_CHECK -->|No| REWARD_CONFIG
    
    DPO_CONFIG --> DPO_INFERENCE
    DPO_INFERENCE --> DPO_TOKENIZE
    DPO_TOKENIZE --> DPO_EVAL
    
    REWARD_CONFIG --> REWARD_PIPE
    REWARD_PIPE --> REWARD_EVAL
```

Sources: [rewardbench/rewardbench.py:237-246](), [rewardbench/rewardbench.py:352-403](), [rewardbench/rewardbench.py:404-472]()

### Output Formats

The CLI generates several output formats depending on the arguments provided:

| Output Type | Condition | File Pattern | Content |
|-------------|-----------|--------------|---------|
| JSON Results | Always (preference ranking) | `{model}.json` | Accuracy and metadata |
| JSONL Outputs | Always | `{model}_outputs.jsonl` | Detailed scores and data |
| All Scores | `--save_all` | `{model}_all.jsonl` | All chosen/rejected scores |
| HF Dataset | `--push_results_to_hub` | HF Hub dataset | Full results with metadata |

Sources: [rewardbench/rewardbench.py:547-550](), [rewardbench/rewardbench.py:589-608](), [rewardbench/rewardbench.py:617-629](), [rewardbench/rewardbench.py:695-697]()

---

