<!-- source: DeepWiki mcp.deepwiki.com · repo openai/parameter-golf · page 7 Reference · fetched 2026-10-26 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- [requirements.txt](requirements.txt)

</details>



This section provides technical reference documentation for the Parameter Golf challenge, including configuration parameters, file format specifications, utility scripts, and dependency information. Use this material as a lookup guide when implementing submissions, debugging issues, or understanding the technical constraints.

For step-by-step instructions on setting up your environment and running training, see [Getting Started](#2). For detailed documentation of the training system architecture, see [Training System Architecture](#4). For information about the dataset pipeline, see [Data Infrastructure](#5).

## Quick Reference

### Critical Constraints

| Constraint | Value | Notes |
|------------|-------|-------|
| Maximum Artifact Size | 16,000,000 bytes | Exactly 16,000,000 bytes, not 16 MiB |
| Maximum Training Time (Record Track) | 10 minutes | On 8xH100 GPUs |
| Maximum Training Time (Non-Record) | Unlimited | Still subject to 16MB artifact limit |
| SOTA Improvement Threshold | 0.005 nats | Statistical significance p < 0.01 required |
| Evaluation Metric | `val_bpb` | Bits-per-byte on FineWeb validation set |

**Sources**: [README.md:6-12](), [README.md:124-130]()

### Common Environment Variables

The training scripts utilize environment variables for configuration, allowing for rapid experimentation without modifying the source code.

| Variable | Purpose | Example Values | Default |
|----------|---------|----------------|---------|
| `RUN_ID` | Identifies training run in logs | `baseline_sp1024`, `mlx_smoke` | `"run"` |
| `DATA_PATH` | Path to binary shard directory | `./data/datasets/fineweb10B_sp1024/` | `"./data/datasets/fineweb10B_sp1024/"` |
| `TOKENIZER_PATH` | Path to tokenizer model file | `./data/tokenizers/fineweb_1024_bpe.model` | See script defaults |
| `VOCAB_SIZE` | Tokenizer vocabulary size | `1024`, `260`, `4096` | `1024` |
| `MAX_WALLCLOCK_SECONDS` | Training time limit | `600`, `0` (unlimited) | `600` |
| `ITERATIONS` | Training iterations | `200`, `1000` | Computed from wallclock |
| `VAL_LOSS_EVERY` | Validation frequency | `200`, `0` (final only) | `0` |
| `TRAIN_BATCH_TOKENS` | Tokens per training batch | `8192`, `524288` | `524288` |

**Sources**: [README.md:65-75](), [README.md:108-115]()

### Required Submission Files

Every submission in the `records/` directory must contain the following structured components to be eligible for the leaderboard.

| File | Purpose | Validation |
|------|---------|------------|
| `README.md` | Explains submission approach and results | Must document configuration and methodology |
| `submission.json` | Structured metadata (name, score, etc.) | Must include `val_bpb`, GitHub ID, name |
| `train.log` | Complete training execution log | Auto-generated, must show final metrics |
| `train_gpt.py` | Training script with dependencies | Must compile and run from records folder |
| `final_model.int8.ptz` | Compressed model artifact | Must be ≤ 16,000,000 bytes including code |

**Sources**: [README.md:152-160]()

## Configuration Flow Architecture

The following diagram shows how environment variables and hyperparameters flow through the training system to configure model architecture and training behavior.

```mermaid
graph TB
    subgraph "Environment Variables"
        ENV_VOCAB["VOCAB_SIZE"]
        ENV_LAYERS["NUM_LAYERS"]
        ENV_DIM["MODEL_DIM"]
        ENV_DATA["DATA_PATH"]
        ENV_TOK["TOKENIZER_PATH"]
        ENV_RUN["RUN_ID"]
        ENV_TIME["MAX_WALLCLOCK_SECONDS"]
        ENV_ITER["ITERATIONS"]
    end
    
    subgraph "Hyperparameters Class"
        HP_MODEL["Model architecture params"]
        HP_TRAIN["Training loop params"]
        HP_DATA["Data loading params"]
    end
    
    subgraph "Training Components"
        MODEL["GPT class instance"]
        LOADER["DistributedTokenLoader"]
        OPTIM["Muon + Adam optimizers"]
        VAL["Validation evaluator"]
    end
    
    subgraph "Output Artifacts"
        LOG["train.log file"]
        MODEL_PTZ["final_model.int8.ptz"]
        SUBJ["submission.json"]
    end
    
    ENV_VOCAB --> HP_MODEL
    ENV_LAYERS --> HP_MODEL
    ENV_DIM --> HP_MODEL
    
    ENV_DATA --> HP_DATA
    ENV_TOK --> HP_DATA
    
    ENV_TIME --> HP_TRAIN
    ENV_ITER --> HP_TRAIN
    
    ENV_RUN --> LOG
    
    HP_MODEL --> MODEL
    HP_DATA --> LOADER
    HP_TRAIN --> OPTIM
    
    MODEL --> MODEL_PTZ
    OPTIM --> LOG
    VAL --> LOG
    LOG --> SUBJ
    MODEL_PTZ --> SUBJ
```

**Sources**: [README.md:65-75](), [README.md:108-115]()

## File Organization Architecture

This diagram shows the file structure for submissions and data artifacts, mapping natural language descriptions to actual file paths and naming conventions.

```mermaid
graph TB
    subgraph "Repository Root"
        README_ROOT["README.md"]
        TRAIN_GPT["train_gpt.py"]
        TRAIN_MLX["train_gpt_mlx.py"]
        REQ["requirements.txt"]
    end
    
    subgraph "data/ Directory"
        CACHED["cached_challenge_fineweb.py"]
        REBUILD["download_hf_docs_and_tokenize.py"]
    end
    
    subgraph "data/datasets/fineweb10B_sp1024/"
        VAL_SHARDS["fineweb_val_000000.bin"]
        TRAIN_SHARDS["fineweb_train_000000.bin"]
        MANIFEST["manifest.json"]
    end
    
    subgraph "data/tokenizers/"
        TOK_MODEL["fineweb_1024_bpe.model"]
        TOK_SPECS["tokenizer_specs.json"]
    end
    
    subgraph "records/track_10min_16mb/YYYY-MM-DD_Name/"
        SUB_README["README.md"]
        SUB_JSON["submission.json"]
        SUB_LOG["train.log"]
        SUB_CODE["train_gpt.py"]
        SUB_MODEL["final_model.int8.ptz"]
    end
    
    CACHED --> VAL_SHARDS
    CACHED --> TRAIN_SHARDS
    CACHED --> MANIFEST
    CACHED --> TOK_MODEL
    
    REBUILD --> VAL_SHARDS
    REBUILD --> TRAIN_SHARDS
    
    TRAIN_GPT --> SUB_CODE
    
    TOK_MODEL --> TRAIN_GPT
    TRAIN_SHARDS --> TRAIN_GPT
    VAL_SHARDS --> TRAIN_GPT
    
    SUB_CODE --> SUB_MODEL
    SUB_CODE --> SUB_LOG
    SUB_LOG --> SUB_JSON
```

**Sources**: [README.md:55-61](), [README.md:97-104](), [README.md:152-160]()

## Artifact Size Calculation

The 16MB artifact limit is computed as the sum of code bytes and compressed model bytes.

```mermaid
graph LR
    subgraph "Code Component"
        TRAIN_CODE["train_gpt.py source code bytes"]
    end
    
    subgraph "Model Component"
        WEIGHTS["Model weights"]
        QUANT["INT8 quantization"]
        COMPRESS["zlib compression"]
        PTZ["final_model.int8.ptz"]
    end
    
    subgraph "Constraint Check"
        SUM["Code bytes + Model bytes"]
        CHECK{"≤ 16,000,000 bytes?"}
        PASS["Submission accepted"]
        FAIL["Submission rejected"]
    end
    
    TRAIN_CODE --> SUM
    PTZ --> SUM
    
    WEIGHTS --> QUANT
    QUANT --> COMPRESS
    COMPRESS --> PTZ
    
    SUM --> CHECK
    CHECK -->|"Yes"| PASS
    CHECK -->|"No"| FAIL
```

**Sources**: [README.md:124-130]()

## Subsection Overview

### 7.1 Configuration Parameters
Comprehensive reference of all environment variables and hyperparameters used in training scripts, including model architecture settings (`VOCAB_SIZE`, `NUM_LAYERS`, `MODEL_DIM`), training control parameters (`MAX_WALLCLOCK_SECONDS`, `ITERATIONS`), and batch size configuration. For details, see [Configuration Parameters](#7.1).

### 7.2 File Format Specifications
Formal specifications for all file formats used in the challenge: `submission.json` schema, binary shard format (int32 header + uint16 tokens), and the `int8_clean_per_row_v1` quantization format used in `.ptz` files. For details, see [File Format Specifications](#7.2).

### 7.3 Utility Scripts
Documentation for helper scripts in the repository: `replace_hf_dataset_with_export.py` for managing dataset versions on Hugging Face Hub and `upload_when_ready.sh` for automated uploads. For details, see [Utility Scripts](#7.3).

### 7.4 Dependencies and Licenses
Lists all Python dependencies from `requirements.txt` (PyTorch, numpy, tiktoken, etc.) and explains the MIT license for the repository and third-party components adapted from `modded-nanogpt`. For details, see [Dependencies and Licenses](#7.4).

**Sources**: [requirements.txt:1-10](), [LICENSE:1-21](), [THIRD_PARTY_NOTICES.md:1-11]()

## Evaluation Constraints

The following rules apply during model evaluation and must be enforced by submission scripts:

| Constraint | Rule | Rationale |
|------------|------|-----------|
| No External Downloads | No network access or API calls | Ensures artifact is self-contained |
| No Training Data Access | Cannot read training shards during eval | Prevents data leakage |
| Maximum Evaluation Time | ≤ 10 minutes (record track) | Prevents infinite-time evaluation |
| Sequence Length | Any length allowed | Encourages long-context exploration |

**Sources**: [README.md:138-140](), [README.md:124-130]()

## Submission Validation Flow

This diagram shows the validation stages applied to submissions, mapping validation steps to actual code requirements and file checks.

```mermaid
graph TB
    START["Pull request submitted"]
    
    subgraph "Structural Validation"
        CHECK_FILES{"Required files present?"}
        CHECK_JSON{"submission.json valid?"}
    end
    
    subgraph "Constraint Validation"
        CHECK_SIZE{"Size ≤ 16,000,000 bytes?"}
        CHECK_TIME{"Training ≤ 600 seconds?"}
    end
    
    subgraph "Performance Validation"
        CHECK_SOTA{"Beats SOTA by ≥ 0.005?"}
        CHECK_REPRO{"Verification passes?"}
    end
    
    subgraph "Outcomes"
        ACCEPT_RECORD["Accept to Record Track"]
        ACCEPT_NONREC["Accept to Non-Record"]
        REJECT["Reject submission"]
    end
    
    START --> CHECK_FILES
    CHECK_FILES -->|"Pass"| CHECK_JSON
    CHECK_FILES -->|"Fail"| REJECT
    
    CHECK_JSON -->|"Pass"| CHECK_SIZE
    CHECK_JSON -->|"Fail"| REJECT
    
    CHECK_SIZE -->|"Pass"| CHECK_TIME
    CHECK_SIZE -->|"Fail"| REJECT
    
    CHECK_TIME -->|"Pass record"| CHECK_SOTA
    CHECK_TIME -->|"Pass non-record"| ACCEPT_NONREC
    
    CHECK_SOTA -->|"Yes"| CHECK_REPRO
    CHECK_SOTA -->|"No"| ACCEPT_NONREC
    
    CHECK_REPRO -->|"Pass"| ACCEPT_RECORD
    CHECK_REPRO -->|"Fail"| REJECT
```

**Sources**: [README.md:142-168]()

---

