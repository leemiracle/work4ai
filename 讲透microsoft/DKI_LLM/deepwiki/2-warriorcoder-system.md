<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/DKI_LLM · page 2 WarriorCoder System · fetched 2026-10-26 -->

# WarriorCoder System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [WarriorCoder/README.md](WarriorCoder/README.md)

</details>



The WarriorCoder System is a comprehensive instruction generation and training pipeline designed to create challenging coding instructions and train specialized code language models. The system implements a multi-stage data processing approach that generates instructions, filters them for quality and difficulty, evaluates model responses through competitive battles, and trains models using the highest-quality response data.

This document covers the complete WarriorCoder pipeline from instruction generation through model training. For information about other research systems in this repository, see [RePrompt System](#3) and [SER System](#4).

## System Architecture Overview

The WarriorCoder system operates as a sequential 6-stage pipeline with two distinct computational environments: a data processing environment for instruction generation and evaluation, and a training environment for model fine-tuning.

### Complete Pipeline Flow

```mermaid
flowchart TD
    subgraph ENV1["data Environment"]
        LLM["Base Language Models"]
        
        subgraph STAGE1["Stage 1: Instruction Generation"]
            VLLMLAN["vllmlan.py<br/>Completion-based<br/>Instruction Mining"]
        end
        
        subgraph STAGE2["Stage 2: Deduplication & Filtering"]
            DEDUP["fhw_deduplication.py<br/>MinHash Algorithm"]
            QUALITY["qualityscoring.py<br/>External LLM Evaluation"]
        end
        
        subgraph STAGE3["Stage 3: Compression"]
            KCENTER["kcenter.py<br/>KcenterGreedy Algorithm"]
        end
        
        subgraph STAGE4["Stage 4: Answer Generation"]
            VLLMANS["vllmans.py<br/>Code Generation<br/>via vLLM"]
        end
        
        subgraph STAGE5["Stage 5: Evaluation & Rating"]
            BATTLE["battle.py<br/>Pairwise Evaluations"]
            ELO["cal_elorating.py<br/>Elo Rating Calculation"]
        end
    end
    
    subgraph ENV2["train Environment"]
        subgraph STAGE6["Stage 6: Training"]
            CONFIG_SFT["config_sft_warrior.yaml"]
            CONFIG_DS["deepspeed_zero3.yaml"] 
            RUN_SFT["run_sft_warrior.py<br/>Supervised Fine-Tuning"]
            TRAINED["WarriorCoder Model"]
        end
    end
    
    LLM --> VLLMLAN
    VLLMLAN --> DEDUP
    DEDUP --> QUALITY
    QUALITY --> KCENTER
    KCENTER --> VLLMANS
    LLM -.-> VLLMANS
    VLLMANS --> BATTLE
    LLM -.-> BATTLE
    BATTLE --> ELO
    ELO --> CONFIG_SFT
    CONFIG_SFT --> RUN_SFT
    CONFIG_DS --> RUN_SFT
    RUN_SFT --> TRAINED

    style ENV1 fill:#f9f9f9
    style ENV2 fill:#f0f8ff
    style TRAINED fill:#e8f5e8
```

Sources: [WarriorCoder/README.md:1-101]()

## Environment Configuration

WarriorCoder requires two separate conda environments optimized for different computational workloads:

### Data Processing Environment (`data`)

The `data` environment handles instruction generation, filtering, and evaluation tasks requiring high-performance inference:

| Component | Purpose | Key Dependencies |
|-----------|---------|------------------|
| vllm | High-speed LLM inference | Core inference engine |
| datasketch | MinHash deduplication | Similarity detection |
| scikit-learn | Embedding operations | K-center algorithm |

### Training Environment (`train`)

The `train` environment provides distributed training capabilities with advanced optimization:

| Component | Version | Purpose |
|-----------|---------|---------|
| PyTorch | 2.2.0 (CUDA 12.1) | Core ML framework |
| TRL | 0.12.0 | Transformer Reinforcement Learning |
| Flash Attention | 2.7.4.post1 | Memory-efficient attention |
| warriortrain | Custom package | Training scripts and utilities |

Sources: [WarriorCoder/README.md:9-26]()

## Data Processing Pipeline

### Stage 1: Instruction Generation with vllmlan.py

The instruction generation stage uses completion-based mining to extract capabilities from existing code LLMs. The `vllmlan.py` script implements high-throughput instruction generation using vLLM inference optimization.

```mermaid
flowchart LR
    subgraph VLLMLAN["vllmlan.py Execution"]
        MODEL_PATH["--path model_path"]
        SAMPLING["Sampling Parameters<br/>--top_p --temperature"]
        GENERATION["Generation Control<br/>--repeat --max_tokens"]
        LANGUAGE["--language target"]
    end
    
    subgraph TOKENIZER["Chat Template Processing"]
        TOKENIZER_CONFIG["tokenizer_config.json"]
        CHAT_TEMPLATE["Model-specific<br/>Chat Templates"]
    end
    
    BASE_MODEL["Base LLM<br/>(e.g. Qwen2.5-72B-Instruct)"] --> MODEL_PATH
    MODEL_PATH --> SAMPLING
    SAMPLING --> GENERATION
    GENERATION --> LANGUAGE
    TOKENIZER_CONFIG --> CHAT_TEMPLATE
    CHAT_TEMPLATE --> VLLMLAN
    LANGUAGE --> INSTRUCTIONS["Generated Instructions"]

    style INSTRUCTIONS fill:#e8f5e8
```

**Key Parameters:**
- `--path`: Hugging Face model identifier or local path
- `--top_p`: Nucleus sampling parameter (e.g., 0.99)
- `--temperature`: Sampling temperature (e.g., 1.2)
- `--repeat`: Number of instruction generations
- `--max_tokens`: Maximum context length (e.g., 2048)
- `--language`: Target programming language

Sources: [WarriorCoder/README.md:29-41]()

### Stage 2: Deduplication and Quality Assessment

#### MinHash Deduplication with fhw_deduplication.py

The deduplication stage implements MinHash algorithm to identify and remove near-duplicate instructions from the generated dataset.

#### Quality Scoring with qualityscoring.py

External LLM evaluation assesses instruction quality and difficulty through structured evaluation prompts.

```mermaid
flowchart TD
    RAW_INSTRUCTIONS["Generated Instructions<br/>from Stage 1"]
    
    subgraph DEDUPLICATION["fhw_deduplication.py"]
        MINHASH["MinHash Algorithm<br/>Similarity Detection"]
        DUPLICATE_REMOVAL["Duplicate Removal<br/>Threshold-based Filtering"]
    end
    
    subgraph QUALITY_SCORING["qualityscoring.py"]
        EVALUATOR_LLM["External Evaluator LLM<br/>(e.g. Llama-3.3-70B-Instruct)"]
        BATCH_PROCESSING["Batch Processing<br/>--start --end parameters"]
        QUALITY_METRICS["Quality & Difficulty<br/>Scoring"]
    end
    
    RAW_INSTRUCTIONS --> MINHASH
    MINHASH --> DUPLICATE_REMOVAL
    DUPLICATE_REMOVAL --> EVALUATOR_LLM
    EVALUATOR_LLM --> BATCH_PROCESSING
    BATCH_PROCESSING --> QUALITY_METRICS
    QUALITY_METRICS --> FILTERED_INSTRUCTIONS["Filtered Instructions"]

    style FILTERED_INSTRUCTIONS fill:#e8f5e8
```

Sources: [WarriorCoder/README.md:42-56]()

### Stage 3: Embedding-based Compression with kcenter.py

The compression stage uses the KcenterGreedy algorithm to reduce dataset size while preserving instruction diversity through embedding space analysis.

```mermaid
flowchart LR
    FILTERED_INSTRUCTIONS["Quality-filtered<br/>Instructions"]
    
    subgraph KCENTER["kcenter.py"]
        EMBEDDING["Instruction Embeddings<br/>Representation Learning"]
        KCENTER_ALGO["KcenterGreedy Algorithm<br/>Diversity Maximization"]
        PARALLEL["Parallel Processing<br/>Multiple --start --end ranges"]
    end
    
    COMPRESSED["Compressed Instruction Set<br/>Optimized for Training"]
    
    FILTERED_INSTRUCTIONS --> EMBEDDING
    EMBEDDING --> KCENTER_ALGO
    KCENTER_ALGO --> PARALLEL
    PARALLEL --> COMPRESSED

    style COMPRESSED fill:#e8f5e8
```

Sources: [WarriorCoder/README.md:57-66]()

## Model Evaluation and Training System

### Stage 4: Answer Generation with vllmans.py

Code generation uses vLLM-accelerated inference to generate multiple candidate answers for each instruction in the compressed dataset.

### Stage 5: Battle System and Elo Rating

#### Pairwise Evaluation with battle.py

The battle system conducts pairwise comparisons between model responses using uninvolved LLM evaluators to determine response quality rankings.

#### Elo Rating Calculation with cal_elorating.py

Elo rating system quantifies model performance and identifies the highest-quality responses for training data.

```mermaid
flowchart TD
    COMPRESSED_INSTRUCTIONS["Compressed Instructions<br/>from kcenter.py"]
    
    subgraph ANSWER_GEN["vllmans.py"]
        VLLM_INFERENCE["vLLM High-speed<br/>Inference Engine"]
        MULTI_MODEL["Multiple Model<br/>Response Generation"]
    end
    
    subgraph EVALUATION["Battle & Rating System"]
        BATTLE_PY["battle.py<br/>Pairwise Comparisons"]
        EVALUATOR["Uninvolved LLM<br/>Judge Models"]
        ELO_PY["cal_elorating.py<br/>Elo Rating Algorithm"]
    end
    
    BEST_RESPONSES["Best Response Dataset<br/>JSON Format with messages"]
    
    COMPRESSED_INSTRUCTIONS --> VLLM_INFERENCE
    VLLM_INFERENCE --> MULTI_MODEL
    MULTI_MODEL --> BATTLE_PY
    BATTLE_PY --> EVALUATOR
    EVALUATOR --> ELO_PY
    ELO_PY --> BEST_RESPONSES

    style BEST_RESPONSES fill:#e8f5e8
```

Sources: [WarriorCoder/README.md:67-88]()

### Stage 6: Training Configuration and Execution

#### Training Data Format

The final training dataset uses a structured JSON format optimized for chat-based fine-tuning:

```json
{
  "messages": [
    {
      "content": "instructions_in_natural_language", 
      "role": "user"
    }, 
    {
      "content": "best_response", 
      "role": "assistant"
    }
  ]
}
```

#### Configuration Files

| File | Purpose | Key Components |
|------|---------|----------------|
| `config_sft_warrior.yaml` | SFT training parameters | Learning rate, batch size, model config |
| `deepspeed_zero3.yaml` | Distributed training | ZeRO-3 optimization, memory management |

#### Training Execution with run_sft_warrior.py

The supervised fine-tuning process uses Accelerate and DeepSpeed for distributed training:

```bash
accelerate launch --config_file recipes/accelerate_configs/deepspeed_zero3.yaml scripts/run_sft_warrior.py recipes/config_sft_warrior.yaml
```

```mermaid
flowchart LR
    subgraph TRAINING_CONFIG["Training Configuration"]
        CONFIG_SFT["config_sft_warrior.yaml<br/>SFT Parameters"]
        CONFIG_DS["deepspeed_zero3.yaml<br/>Distributed Training"]
        DATA_PATH["Training & Test Data<br/>Path Configuration"]
    end
    
    subgraph TRAINING_EXEC["Training Execution"]
        ACCELERATE["accelerate launch<br/>Distributed Coordinator"]
        RUN_SFT["run_sft_warrior.py<br/>Training Script"]
        WARRIORTRAIN["warriortrain Package<br/>Training Utilities"]
    end
    
    FINAL_MODEL["Trained WarriorCoder Model"]
    
    CONFIG_SFT --> ACCELERATE
    CONFIG_DS --> ACCELERATE
    DATA_PATH --> RUN_SFT
    ACCELERATE --> RUN_SFT
    RUN_SFT --> WARRIORTRAIN
    WARRIORTRAIN --> FINAL_MODEL

    style FINAL_MODEL fill:#c8e6c9
```

Sources: [WarriorCoder/README.md:84-101]()

## Implementation Notes

### Chat Template Compatibility

The system requires model-specific chat template configuration based on `tokenizer_config.json` files. Different base models implement varying conversation formats that must be properly configured for instruction generation.

### Parallel Processing Optimization

Both `kcenter.py` and `qualityscoring.py` support batch processing with `--start` and `--end` parameters, enabling parallel execution across multiple processes or machines for large-scale datasets.

### Memory and Performance Considerations

- **vLLM Integration**: High-throughput inference for both instruction generation (`vllmlan.py`) and answer generation (`vllmans.py`)
- **Flash Attention**: Memory-efficient attention mechanism for training large models
- **DeepSpeed ZeRO-3**: Advanced memory optimization for distributed training

Sources: [WarriorCoder/README.md:40-41](), [WarriorCoder/README.md:65](), [WarriorCoder/README.md:19-25]()

---

