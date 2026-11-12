<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/transformers-research-projects · page 6 Code Generation (CodeParrot) · fetched 2026-10-26 -->

# Code Generation (CodeParrot)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [codeparrot/README.md](codeparrot/README.md)

</details>



## Purpose and Scope

The CodeParrot system provides a comprehensive framework for training GPT-2 based code generation models from scratch. This system handles the complete pipeline from raw GitHub data processing to model evaluation on code generation benchmarks. The implementation focuses specifically on Python code generation using custom tokenization, large-scale data preprocessing, and distributed training capabilities.

For CodeParrot example applications and fine-tuning procedures for NLP4Code tasks, see [CodeParrot Examples and Fine-tuning](#6.1).

## System Overview

CodeParrot implements an end-to-end training pipeline for code generation models, featuring custom tokenization adapted for Python syntax, scalable data preprocessing with deduplication, and distributed training using the `accelerate` framework. The system produces models ranging from 110M to 1.5B parameters trained on cleaned GitHub Python code.

```mermaid
graph TB
    subgraph "Data Pipeline"
        raw_data["transformersbook/codeparrot<br/>Raw GitHub Data"]
        preprocessing["scripts/preprocessing.py<br/>Deduplication & Filtering"]
        clean_data["codeparrot/codeparrot-clean-train<br/>Cleaned Dataset"]
        pretokenize["scripts/pretokenizing.py<br/>Optional Pretokenization"]
    end
    
    subgraph "Model Pipeline"
        tokenizer_train["scripts/bpe_training.py<br/>Custom BPE Training"]
        model_init["scripts/initialize_model.py<br/>Model Initialization"]
        training["scripts/codeparrot_training.py<br/>Distributed Training"]
        checkpoints["Hub Checkpoints<br/>codeparrot/codeparrot"]
    end
    
    subgraph "Evaluation Pipeline"
        validation["scripts/validation_loss.py<br/>Perplexity Evaluation"]
        human_eval["scripts/human_eval.py<br/>HumanEval Benchmark"]
        metrics["pass@1, pass@10, pass@100<br/>Code Generation Metrics"]
    end
    
    raw_data --> preprocessing
    preprocessing --> clean_data
    clean_data --> pretokenize
    clean_data --> tokenizer_train
    
    tokenizer_train --> model_init
    model_init --> training
    training --> checkpoints
    
    checkpoints --> validation
    checkpoints --> human_eval
    human_eval --> metrics
    
    style preprocessing fill:#f9f9f9
    style training fill:#f9f9f9
    style human_eval fill:#f9f9f9
```

Sources: [codeparrot/README.md:1-317]()

## Core Components

### Dataset Processing Pipeline

The dataset pipeline transforms raw GitHub data into training-ready format through extensive filtering and deduplication. The system processes over 180GB of Python files, applying heuristics from OpenAI's Codex paper to remove duplicates and low-quality code.

| Component | Script | Purpose |
|-----------|--------|---------|
| Raw Data Source | `transformersbook/codeparrot` | 20M+ Python files from GitHub BigQuery |
| Preprocessing | `scripts/preprocessing.py` | Deduplication and quality filtering |
| Clean Datasets | `codeparrot-clean-train/valid` | 30% of original data after filtering |
| Pretokenization | `scripts/pretokenizing.py` | Optional speed optimization |

Key filtering criteria include exact hash-based deduplication, MinHash near-deduplication with Jaccard similarity threshold of 0.85, and content-based filters for auto-generated files, test files, and files with insufficient code patterns.

Sources: [codeparrot/README.md:40-77]()

### Tokenizer Training System

The tokenizer system creates a custom BPE tokenizer optimized for Python code structure, trained on the cleaned dataset to handle code-specific patterns more efficiently than general-purpose tokenizers.

```mermaid
graph LR
    subgraph "Tokenizer Training Flow"
        base_tok["openai-community/gpt2<br/>Base Tokenizer"]
        clean_train["codeparrot/codeparrot-clean-train<br/>Training Data"]
        bpe_script["scripts/bpe_training.py<br/>BPE Training Logic"]
        custom_tok["codeparrot/codeparrot<br/>Custom Tokenizer"]
    end
    
    subgraph "Tokenizer Components"
        vocab["vocab.json<br/>Vocabulary File"]
        merges["merges.txt<br/>Merge Rules"]
        config["tokenizer_config.json<br/>Configuration"]
    end
    
    base_tok --> bpe_script
    clean_train --> bpe_script
    bpe_script --> custom_tok
    
    custom_tok --> vocab
    custom_tok --> merges
    custom_tok --> config
```

Sources: [codeparrot/README.md:78-87]()

### Model Training Architecture

The training system uses `accelerate` for distributed training across multiple GPUs with mixed precision support. Models are initialized from scratch using GPT-2 architecture configurations but with custom tokenizer embeddings.

```mermaid
graph TB
    subgraph "Model Initialization"
        gpt2_config["openai-community/gpt2-large<br/>Architecture Config"]
        custom_tokenizer["codeparrot/codeparrot<br/>Custom Tokenizer"]
        init_script["scripts/initialize_model.py<br/>Model Initialization"]
        base_model["Randomly Initialized Model<br/>Custom Vocab Size"]
    end
    
    subgraph "Training Infrastructure"
        accelerate["accelerate<br/>Distributed Training"]
        wandb["wandb<br/>Experiment Tracking"]
        train_script["scripts/codeparrot_training.py<br/>Training Loop"]
        hub_push["huggingface_hub<br/>Checkpoint Management"]
    end
    
    subgraph "Model Variants"
        small_model["codeparrot/codeparrot-small<br/>110M Parameters"]
        large_model["codeparrot/codeparrot<br/>1.5B Parameters"]
    end
    
    gpt2_config --> init_script
    custom_tokenizer --> init_script
    init_script --> base_model
    
    base_model --> train_script
    accelerate --> train_script
    wandb --> train_script
    train_script --> hub_push
    
    train_script --> small_model
    train_script --> large_model
```

Training configurations support both streaming from Hub datasets and local data storage, with automatic checkpoint saving and resume capabilities.

Sources: [codeparrot/README.md:88-161]()

### Evaluation Framework

The evaluation system provides both perplexity-based validation and functional code generation assessment through the HumanEval benchmark.

| Evaluation Type | Script | Metrics | Purpose |
|----------------|--------|---------|---------|
| Language Modeling | `scripts/validation_loss.py` | Perplexity, Cross-entropy | Model convergence assessment |
| Code Generation | `scripts/human_eval.py` | pass@1, pass@10, pass@100 | Functional correctness |

The HumanEval evaluation supports configurable sampling parameters including temperature, top-p filtering, and multiple sample generation for pass@k metric computation.

Sources: [codeparrot/README.md:163-198]()

## Training Workflow

The complete training workflow encompasses data preparation, tokenizer creation, model initialization, distributed training, and comprehensive evaluation.

```mermaid
flowchart TD
    start["Start"] --> data_prep["Data Preparation Phase"]
    
    subgraph data_prep["Data Preparation Phase"]
        download["Download transformersbook/codeparrot"]
        preprocess["Run scripts/preprocessing.py<br/>Filter & Deduplicate"]
        optional_pretok["Optional: scripts/pretokenizing.py<br/>Speed Optimization"]
    end
    
    subgraph tokenizer_phase["Tokenizer Phase"]
        train_bpe["scripts/bpe_training.py<br/>Train Custom BPE"]
        push_tokenizer["Push to codeparrot/codeparrot"]
    end
    
    subgraph model_phase["Model Phase"]
        init_model["scripts/initialize_model.py<br/>Initialize Architecture"]
        config_accel["accelerate config<br/>Setup Distributed Training"]
        train_model["scripts/codeparrot_training.py<br/>Training Loop"]
        checkpoint["Auto-checkpoint to Hub"]
    end
    
    subgraph eval_phase["Evaluation Phase"]
        val_loss["scripts/validation_loss.py<br/>Perplexity Assessment"]
        human_eval["scripts/human_eval.py<br/>Functional Testing"]
        benchmark["HumanEval Benchmark Results"]
    end
    
    data_prep --> tokenizer_phase
    tokenizer_phase --> model_phase
    model_phase --> eval_phase
    
    optional_pretok -.-> train_model
    checkpoint --> val_loss
    checkpoint --> human_eval
```

The workflow supports both small-scale experimentation (110M parameters) and production-scale training (1.5B parameters) with different batch sizes and learning rates optimized for each configuration.

Sources: [codeparrot/README.md:88-198]()

## Alternative Training with Megatron

CodeParrot includes integration with NVIDIA's Megatron framework for accelerated training of larger models. The Megatron pipeline requires data conversion to binary format and uses different distributed training configurations.

```mermaid
graph TB
    subgraph "Megatron Data Pipeline"
        clean_data["codeparrot-clean-train<br/>Hugging Face Dataset"]
        json_convert["Python Script<br/>Convert to JSON Lines"]
        megatron_preprocess["tools/preprocess_data.py<br/>Binary Format Conversion"]
        binary_data["codeparrot_content_document<br/>.idx + .bin files"]
    end
    
    subgraph "Megatron Training"
        pretrain_gpt["pretrain_gpt.py<br/>Megatron Training Script"]
        distributed_args["torch.distributed.launch<br/>Multi-GPU Coordination"]
        checkpoint_path["/workspace/Megatron-LM/experiments/codeparrot-small<br/>Training Checkpoints"]
    end
    
    subgraph "Model Conversion"
        megatron_ckpt["model_optim_rng.pt<br/>Megatron Checkpoint"]
        convert_script["convert_megatron_gpt2_checkpoint.py<br/>Transformers Conversion"]
        transformers_model["pytorch_model.bin<br/>Transformers Compatible"]
    end
    
    clean_data --> json_convert
    json_convert --> megatron_preprocess
    megatron_preprocess --> binary_data
    
    binary_data --> pretrain_gpt
    distributed_args --> pretrain_gpt
    pretrain_gpt --> checkpoint_path
    
    checkpoint_path --> megatron_ckpt
    megatron_ckpt --> convert_script
    convert_script --> transformers_model
```

The Megatron integration requires Docker containers with NVIDIA PyTorch runtime and involves data format conversion but provides faster training performance for large-scale experiments.

Sources: [codeparrot/README.md:206-312]()

---

