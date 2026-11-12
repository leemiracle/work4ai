<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/OLMoASR · page 5 Model Evaluation · fetched 2026-10-26 -->

# Model Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/README.md](scripts/README.md)
- [scripts/eval/README.md](scripts/eval/README.md)

</details>



The OLMoASR evaluation system provides a comprehensive suite for assessing trained ASR models against standard benchmark datasets. This system handles dataset downloading, preprocessing, model evaluation, and metric computation across multiple speech recognition benchmarks.

For information about model training, see [Model Training](#4). For details on using trained models for inference, see [Inference & Deployment](#6).

## Evaluation System Architecture

The evaluation system consists of three main components: dataset management, model preparation, and evaluation execution. The system is designed to work with both locally trained checkpoints and models from the HuggingFace Hub.

### Evaluation Pipeline Flow

```mermaid
flowchart TD
    subgraph "Dataset Management"
        GET_EVAL["get_eval_set.py"]
        EVAL_DIR["data/eval/"]
        HF_TOKEN["HuggingFace Token"]
    end
    
    subgraph "Model Preparation"
        CKPT["Model Checkpoint"]
        GEN_INF["gen_inf_ckpt.py"]
        INF_CKPT["Inference Checkpoint"]
    end
    
    subgraph "Evaluation Execution"
        EVAL_PY["eval.py"]
        METRICS["WER/CER Metrics"]
        RESULTS["Evaluation Results"]
    end
    
    subgraph "Supported Datasets"
        LIBRI["LibriSpeech clean/other"]
        ARTIE["Artie Bias Corpus"]
        FLEURS["Fleurs"]
        TEDLIUM["TEDLIUM"]
        VOXPOP["VoxPopuli"]
        CV["CommonVoice"]
        AMI["AMI IHM/SDM"]
    end
    
    GET_EVAL --> EVAL_DIR
    HF_TOKEN --> GET_EVAL
    LIBRI --> EVAL_DIR
    ARTIE --> EVAL_DIR
    FLEURS --> EVAL_DIR
    TEDLIUM --> EVAL_DIR
    VOXPOP --> EVAL_DIR
    CV --> EVAL_DIR
    AMI --> EVAL_DIR
    
    CKPT --> GEN_INF
    GEN_INF --> INF_CKPT
    
    INF_CKPT --> EVAL_PY
    EVAL_DIR --> EVAL_PY
    HF_TOKEN --> EVAL_PY
    EVAL_PY --> METRICS
    METRICS --> RESULTS
```

**Sources:** [scripts/README.md:29-36](), [scripts/eval/README.md:1-24]()

### Evaluation Script Integration

```mermaid
graph TB
    subgraph "Configuration System"
        JOB_CONFIGS["configs/job_configs/eval/"]
        EVAL_CONFIG["*.yaml config files"]
    end
    
    subgraph "Core Evaluation Scripts"
        GET_EVAL_SET["get_eval_set.py<br/>--eval_set, --eval_dir, --hf_token"]
        GEN_INF_CKPT["gen_inf_ckpt.py<br/>Modify weights for inference"]
        EVAL_SCRIPT["eval.py<br/>--ckpt, --eval_set, --eval_dir"]
    end
    
    subgraph "Data Dependencies"
        HF_DATASETS["HuggingFace Datasets API"]
        LOCAL_STORAGE["Local eval directory"]
        AUTH_TOKEN["HF Authentication Token"]
    end
    
    subgraph "Model Dependencies"
        TRAIN_CKPT["Training Checkpoint<br/>*.pt files"]
        INF_MODEL["olmoasr.inf_model.OLMoASR"]
        WHISPER_ARCH["Whisper Architecture"]
    end
    
    JOB_CONFIGS --> EVAL_CONFIG
    EVAL_CONFIG --> GET_EVAL_SET
    EVAL_CONFIG --> EVAL_SCRIPT
    
    GET_EVAL_SET --> HF_DATASETS
    GET_EVAL_SET --> LOCAL_STORAGE
    AUTH_TOKEN --> GET_EVAL_SET
    AUTH_TOKEN --> EVAL_SCRIPT
    
    TRAIN_CKPT --> GEN_INF_CKPT
    GEN_INF_CKPT --> INF_MODEL
    INF_MODEL --> EVAL_SCRIPT
    WHISPER_ARCH --> INF_MODEL
    
    LOCAL_STORAGE --> EVAL_SCRIPT
```

**Sources:** [scripts/README.md:29-36](), [scripts/eval/README.md:3-7](), [scripts/eval/README.md:20-24]()

## Supported Evaluation Datasets

The evaluation system supports multiple benchmark datasets commonly used in ASR research. Each dataset has specific requirements and characteristics.

| Dataset | Identifier | Description | Special Requirements |
|---------|------------|-------------|---------------------|
| LibriSpeech Clean | `librispeech_clean` | Clean speech subset of LibriSpeech | None |
| LibriSpeech Other | `librispeech_other` | Noisy speech subset of LibriSpeech | None |
| Artie Bias Corpus | `artie_bias_corpus` | Bias evaluation corpus | None |
| Fleurs | `fleurs` | Multilingual speech dataset | None |
| TEDLIUM | `tedlium` | TED talk transcriptions | None |
| VoxPopuli | `voxpopuli` | European Parliament speeches | None |
| CommonVoice | `common_voice` | Mozilla's crowdsourced dataset | HuggingFace token required |
| AMI IHM | `ami_ihm` | Meeting corpus (individual headset) | None |
| AMI SDM | `ami_sdm` | Meeting corpus (single distant mic) | None |

**Sources:** [scripts/eval/README.md:9-18]()

### Dataset Download Process

The `get_eval_set.py` script handles automatic dataset downloading and preparation:

```bash
python get_eval_set.py --eval_set=librispeech_clean --eval_dir=data/eval --hf_token=<token>
```

Key parameters:
- `--eval_set`: Name of the evaluation dataset to download
- `--eval_dir`: Directory to store evaluation datasets (default: `data/eval`)
- `--hf_token`: HuggingFace authentication token (required for some datasets)

**Sources:** [scripts/eval/README.md:3-7](), [scripts/eval/README.md:16]()

## Model Preparation for Evaluation

### Inference Checkpoint Generation

The `gen_inf_ckpt.py` script modifies training checkpoints to create inference-optimized versions. This addresses architectural modifications made during training that are not needed for inference.

```mermaid
flowchart LR
    subgraph "Training Checkpoint"
        TRAIN_WEIGHTS["Training Weights<br/>Batch padding modifications"]
        TRAIN_ARCH["Training Architecture<br/>Batch > 1 optimizations"]
    end
    
    subgraph "Inference Preparation"
        GEN_INF_SCRIPT["gen_inf_ckpt.py<br/>Weight modification"]
        ARCH_CLEANUP["Remove training artifacts"]
    end
    
    subgraph "Inference Checkpoint"
        INF_WEIGHTS["Inference Weights<br/>Clean architecture"]
        WHISPER_COMPAT["Whisper Compatible<br/>Single sample inference"]
    end
    
    TRAIN_WEIGHTS --> GEN_INF_SCRIPT
    TRAIN_ARCH --> ARCH_CLEANUP
    GEN_INF_SCRIPT --> INF_WEIGHTS
    ARCH_CLEANUP --> WHISPER_COMPAT
```

**Sources:** [scripts/README.md:32-37]()

## Running Evaluations

### Evaluation Execution

The `eval.py` script performs the actual evaluation against downloaded datasets:

```bash
python eval.py --ckpt=path/to/checkpoint --eval_set=librispeech_clean --eval_dir=data/eval --hf_token=<token>
```

### Evaluation Parameters

| Parameter | Description | Required | Notes |
|-----------|-------------|----------|-------|
| `--ckpt` | Path to model checkpoint | Yes | Can be training or inference checkpoint |
| `--eval_set` | Name of evaluation dataset | Yes | Must match downloaded dataset |
| `--eval_dir` | Directory containing eval datasets | No | Default: `data/eval` |
| `--hf_token` | HuggingFace authentication token | Conditional | Required for CommonVoice |

**Sources:** [scripts/eval/README.md:20-24]()

### Configuration-Based Evaluation

The system supports YAML configuration files for batch evaluation:

```mermaid
graph LR
    subgraph "Configuration Files"
        YAML_CONFIG["configs/job_configs/eval/*.yaml"]
        EVAL_PARAMS["Evaluation parameters"]
        DATASET_LIST["Dataset specifications"]
    end
    
    subgraph "Batch Execution"
        CONFIG_PARSER["Configuration parser"]
        MULTI_EVAL["Multiple dataset evaluation"]
        RESULT_AGGREGATION["Result aggregation"]
    end
    
    subgraph "Output"
        WER_SCORES["WER scores per dataset"]
        CER_SCORES["CER scores per dataset"]
        SUMMARY_REPORT["Evaluation summary"]
    end
    
    YAML_CONFIG --> EVAL_PARAMS
    EVAL_PARAMS --> CONFIG_PARSER
    DATASET_LIST --> CONFIG_PARSER
    CONFIG_PARSER --> MULTI_EVAL
    MULTI_EVAL --> WER_SCORES
    MULTI_EVAL --> CER_SCORES
    WER_SCORES --> SUMMARY_REPORT
    CER_SCORES --> SUMMARY_REPORT
```

**Sources:** [scripts/README.md:35]()

## Integration with Training Pipeline

The evaluation system integrates with the broader OLMoASR training pipeline to provide continuous model assessment capabilities.

### Evaluation Workflow Integration

```mermaid
sequenceDiagram
    participant Training as "Training Scripts"
    participant Checkpoint as "Model Checkpoints"
    participant GenInf as "gen_inf_ckpt.py"
    participant GetEval as "get_eval_set.py"
    participant Eval as "eval.py"
    participant Results as "Evaluation Results"
    
    Training->>Checkpoint: Save training checkpoint
    Checkpoint->>GenInf: Convert to inference format
    GenInf->>Checkpoint: Create inference checkpoint
    
    GetEval->>GetEval: Download eval datasets (if needed)
    
    Checkpoint->>Eval: Load inference checkpoint
    GetEval->>Eval: Provide eval datasets
    Eval->>Results: Generate WER/CER metrics
    Results->>Training: Inform next training iteration
```

**Sources:** [scripts/README.md:29-37](), [scripts/eval/README.md:1-24]()

The evaluation system provides essential feedback for model development, enabling researchers to assess model performance across diverse speech recognition benchmarks and guide iterative improvements to the training process.

---

