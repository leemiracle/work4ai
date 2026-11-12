<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/multimodalqa · page 7 Training Models · fetched 2026-10-26 -->

# Training Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [baselines/README.md](baselines/README.md)
- [baselines/image_qa/README.md](baselines/image_qa/README.md)
- [baselines/image_qa/main.py](baselines/image_qa/main.py)

</details>



## Purpose and Scope

This page provides an overview of the training procedures for the MultiModalQA baseline models. The system consists of three modality-specific QA models (text, table, and image) that are **trained independently** on their respective data subsets. Each model is fine-tuned from pre-trained checkpoints and supports three distinct inference modes.

For detailed step-by-step training procedures:
- Image QA models: see [Training Image QA Models](#7.1)
- Text and Table QA models: see [Training Text and Table QA Models](#7.2)

For information about the trained models themselves and their architectures, see [Baseline Models](#5).

**Sources:** [baselines/README.md:50-52]()

---

## Training Architecture Overview

The MultiModalQA training infrastructure follows a **modular, modality-specific approach**. Each of the three modalities (text, table, image) has its own training pipeline, dataset preparation logic, and hyperparameter configuration. This design enables independent development and optimization of each component.

```mermaid
graph TB
    subgraph "Data Layer"
        MMQA_TRAIN["MMQA_train.jsonl<br/>Training Questions"]
        TEXT_CTX["texts.jsonl<br/>Text Paragraphs"]
        TABLE_CTX["tables.jsonl<br/>Structured Tables"]
        IMAGE_CTX["images.jsonl + images.zip<br/>Image Metadata & Files"]
    end
    
    subgraph "Pre-trained Models"
        BERT["BERT/RoBERTa<br/>bert-base-uncased"]
        VILBERT["VilBERT Multi-Task<br/>vilbert-multi-task"]
    end
    
    subgraph "Training Scripts"
        TEXT_TRAIN["text_qa/train.py<br/>Text QA Training"]
        TABLE_TRAIN["table_qa/train.py<br/>Table QA Training"]
        IMAGE_TRAIN["image_qa/main.py<br/>Image QA Training"]
    end
    
    subgraph "Model Outputs"
        TEXT_CP["text_qa_models/<br/>implicit_decomp/<br/>auto_routing/<br/>context_only/"]
        TABLE_CP["table_qa_models/<br/>implicit_decomp/<br/>auto_routing/<br/>context_only/"]
        IMAGE_CP["image_qa_models/<br/>implicit_decomp/<br/>auto_routing/<br/>context_only/<br/>model.pt"]
    end
    
    MMQA_TRAIN --> TEXT_TRAIN
    MMQA_TRAIN --> TABLE_TRAIN
    MMQA_TRAIN --> IMAGE_TRAIN
    
    TEXT_CTX --> TEXT_TRAIN
    TABLE_CTX --> TABLE_TRAIN
    IMAGE_CTX --> IMAGE_TRAIN
    
    BERT --> TEXT_TRAIN
    BERT --> TABLE_TRAIN
    VILBERT --> IMAGE_TRAIN
    
    TEXT_TRAIN --> TEXT_CP
    TABLE_TRAIN --> TABLE_CP
    IMAGE_TRAIN --> IMAGE_CP
```

**Key Design Principles:**

1. **Independent Training**: Each modality is trained separately with its own hyperparameters and training strategies
2. **Transfer Learning**: All models start from pre-trained checkpoints (BERT/RoBERTa for text/table, VilBERT for images)
3. **Mode-Specific Checkpoints**: Each training produces three separate model checkpoints corresponding to the three inference modes
4. **Modular Data Processing**: Each training script contains its own dataset preparation logic

**Sources:** [baselines/README.md:50-52](), [baselines/image_qa/README.md:1-19]()

---

## Training Modes

The MultiModalQA system supports three distinct inference modes, each requiring a **separate training run** with mode-specific data processing. The primary difference lies in how multi-hop questions are handled during training.

| Mode | Training Data Processing | Multi-Hop Strategy | Use Case |
|------|-------------------------|-------------------|----------|
| `implicit_decomp` | Uses **gold bridge entities** for second-hop questions | Two-stage reasoning with ground truth intermediate entities | Best performance; evaluates multi-hop reasoning capability |
| `auto_routing` | Uses **all available entities** as potential bridges | Direct routing to final modality without decomposition | Tests end-to-end retrieval without gold annotations |
| `context_only` | Ignores question type classification | Routes based only on context modality | Baseline to measure question importance |

```mermaid
graph LR
    subgraph "Training Data Flow"
        RAW["Raw Question<br/>+ Answer<br/>+ Context"]
        
        RAW --> MODE_SWITCH{"Training Mode?"}
        
        MODE_SWITCH -->|implicit_decomp| IMP["Filter: golden_bridge_entities<br/>Question Processing: Two-hop"]
        MODE_SWITCH -->|auto_routing| AUTO["Filter: All img_ids/table_ids<br/>Question Processing: Single-hop"]
        MODE_SWITCH -->|context_only| CTX["Ignore: Question Type<br/>Use Context Only"]
        
        IMP --> TRAIN1["Train with<br/>Bridge Entities"]
        AUTO --> TRAIN2["Train with<br/>All Entities"]
        CTX --> TRAIN3["Train with<br/>Context Features"]
        
        TRAIN1 --> CP1["checkpoints/<br/>implicit_decomp/"]
        TRAIN2 --> CP2["checkpoints/<br/>auto_routing/"]
        TRAIN3 --> CP3["checkpoints/<br/>context_only/"]
    end
```

### Mode Selection in Code

The training mode is specified via the `--mode` command-line argument:

```bash
python baselines/image_qa/main.py --mode implicit_decomp
python baselines/image_qa/main.py --mode auto_routing
python baselines/image_qa/main.py --mode context_only
```

The mode affects several aspects of training:
- **Data Filtering**: Which bridge entities are used for multi-hop questions ([baselines/image_qa/main.py:59-66]())
- **Question Processing**: How questions are tokenized and paired with context ([baselines/image_qa/dataset.py]())
- **Model Checkpoint Path**: Output directory naming ([baselines/image_qa/main.py:231]())

**Sources:** [baselines/image_qa/main.py:177-181](), [baselines/image_qa/main.py:226](), [baselines/image_qa/main.py:59-66]()

---

## Training Strategy: Two-Stage Fine-Tuning

The image QA training employs a **two-stage fine-tuning strategy** that is standard practice for large vision-language models:

### Stage 1: Frozen Backbone Training
- **Purpose**: Adapt the task-specific heads while preserving pre-trained features
- **Configuration**: VilBERT backbone parameters are frozen; only QA head is trainable
- **Default Hyperparameters**:
  - Epochs: 25 (`--frozen_epochs`)
  - Learning Rate: 2e-5 (`--frozen_lr`)
  - LR Step Size: 15 (`--frozen_lr_step_size`)

### Stage 2: Full Fine-Tuning
- **Purpose**: End-to-end optimization of all model parameters
- **Configuration**: All parameters (backbone + heads) are trainable
- **Default Hyperparameters**:
  - Epochs: 50 (`--unfrozen_epochs`)
  - Learning Rate: 2e-6 (`--unfrozen_lr`) - 10× smaller than frozen stage
  - LR Step Size: 25 (`--unfrozen_lr_step_size`)

```mermaid
graph TB
    subgraph "Stage 1: Frozen Backbone"
        PRETRAINED["VilBERT Pre-trained<br/>vilbert-multi-task"]
        PRETRAINED --> FROZEN_TRAIN["25 Epochs<br/>lr=2e-5<br/>Frozen: Vision + Language Encoders<br/>Trainable: QA Heads Only"]
        FROZEN_TRAIN --> STAGE1_OUT["Adapted QA Heads<br/>Preserved Features"]
    end
    
    subgraph "Stage 2: Full Fine-tuning"
        STAGE1_OUT --> UNFROZEN_TRAIN["50 Epochs<br/>lr=2e-6<br/>Trainable: All Parameters<br/>End-to-End Optimization"]
        UNFROZEN_TRAIN --> FINAL_MODEL["Final Model Checkpoint<br/>model.pt"]
    end
    
    MONITOR["TensorboardX Logs<br/>training_stats/"] -.->|Track| FROZEN_TRAIN
    MONITOR -.->|Track| UNFROZEN_TRAIN
```

This strategy is implemented in [baselines/image_qa/train_and_eval.py]() and controlled via command-line arguments in [baselines/image_qa/main.py:123-156]().

**Sources:** [baselines/image_qa/main.py:123-156](), [baselines/image_qa/main.py:199-204]()

---

## Hyperparameter Configuration

### Command-Line Arguments

Training hyperparameters are specified via command-line arguments to the training scripts. The image QA training script exposes the following key parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--batch_size` | int | 12 | Training batch size |
| `--device` | str | `cuda:0` | GPU device to use |
| `--dropout_prob` | float | 0.01 | Dropout rate for regularization |
| `--frozen_epochs` | int | 25 | Epochs for frozen backbone stage |
| `--frozen_lr` | float | 2e-5 | Learning rate for frozen stage |
| `--frozen_lr_step_size` | float | 15 | LR scheduler step size (frozen) |
| `--unfrozen_epochs` | int | 50 | Epochs for full fine-tuning |
| `--unfrozen_lr` | float | 2e-6 | Learning rate for unfrozen stage |
| `--unfrozen_lr_step_size` | float | 25 | LR scheduler step size (unfrozen) |
| `--sample_distractor_prob` | float | 0.3 | Probability of sampling distractor images |
| `--mask_vis` | bool | False | Ablation: mask visual features |
| `--mask_lang` | bool | False | Ablation: mask language features |
| `--mode` | str | `implicit_decomp` | Training mode (see above) |
| `--data_dir` | str | `../../dataset` | Path to MMQA dataset |

### Hyperparameter Dictionary

Arguments are collected into a `hparams` dictionary for consistency:

```python
# From baselines/image_qa/main.py:195-209
hparams = {
    'batch_size': args.batch_size,
    'device': args.device,
    'dropout_prob': args.dropout_prob,
    'frozen_epochs': args.frozen_epochs,
    'frozen_lr': args.frozen_lr,
    # ... (other parameters)
}
```

**Sources:** [baselines/image_qa/main.py:102-190](), [baselines/image_qa/main.py:195-209]()

---

## Training Workflow and Code Flow

The following diagram shows how the key functions and classes interact during training:

```mermaid
graph TB
    MAIN["main.py<br/>if __name__ == '__main__':<br/>line 193"]
    MAIN --> PARSE["parse_args()<br/>line 102-190<br/>Parse CLI Arguments"]
    PARSE --> HPARAMS["Build hparams Dict<br/>line 195-209"]
    
    HPARAMS --> GET_DATA["get_raw_dataset(datadir)<br/>dataset.py<br/>Load MMQA_train.jsonl"]
    GET_DATA --> VQADATASET["VQADataset<br/>dataset.py<br/>Process Questions & Features"]
    
    HPARAMS --> TRAIN_EVAL["train_and_eval(hparams, model_suffix)<br/>train_and_eval.py<br/>line 233<br/>Returns: model, stats"]
    VQADATASET --> TRAIN_EVAL
    
    TRAIN_EVAL --> FROZEN["Stage 1: Frozen Training<br/>25 epochs, lr=2e-5"]
    FROZEN --> UNFROZEN["Stage 2: Unfrozen Training<br/>50 epochs, lr=2e-6"]
    
    UNFROZEN --> MODEL_OUT["Trained Model<br/>checkpoints/{mode}/model.pt"]
    UNFROZEN --> STATS_OUT["Training Statistics<br/>training_stats/{mode}.pickle"]
    
    MODEL_OUT --> ANALYSE["analyse(model, dataset)<br/>line 48-99<br/>Evaluate on Dev Set"]
    ANALYSE --> METRICS["Per-Question-Type Metrics<br/>F1 & Exact Match<br/>line 252-273"]
    
    METRICS --> SAVE["Save Analysis<br/>analysis/stats_{mode}.pickle<br/>line 275-277"]
```

### Key Functions and Their Roles

1. **`parse_args()`** [baselines/image_qa/main.py:102-190]()
   - Parses command-line arguments for hyperparameter configuration
   
2. **`get_raw_dataset(datadir)`** [baselines/image_qa/dataset.py]()
   - Loads and processes the raw MMQA training data
   - Returns datasets dict, idx2answer, and answer2idx mappings

3. **`VQADataset`** [baselines/image_qa/dataset.py]()
   - Dataset class that handles question processing, feature loading, and batching
   - Mode-aware: processes data differently for `implicit_decomp`, `auto_routing`, `context_only`

4. **`train_and_eval(hparams, model_suffix)`** [baselines/image_qa/train_and_eval.py]()
   - Orchestrates the two-stage training process
   - Returns trained model, training statistics, and metadata

5. **`analyse(model, dataset, device, idx2answer, use_distractors, mode)`** [baselines/image_qa/main.py:48-99]()
   - Evaluates trained model on dev set
   - Computes per-question-type F1 and Exact Match scores
   - Prints example predictions for debugging

**Sources:** [baselines/image_qa/main.py:193-278]()

---

## Output Artifacts

Training produces three types of output artifacts:

### 1. Model Checkpoints

Saved to `baselines/image_qa/checkpoints/{mode}_{timestamp}/`:
- `model.pt`: Serialized model state dict
- `vocab.pickle`: Answer vocabulary mappings (shared across modes)

### 2. Training Statistics

Saved to `baselines/image_qa/training_stats/`:
- PNG plots for each metric: `train_acc_{mode}.png`, `train_loss_{mode}.png`, `val_acc_{mode}.png`, `val_loss_{mode}.png`
- Generated from TensorboardX logs [baselines/image_qa/main.py:239-244]()

### 3. Analysis Results

Saved to `baselines/image_qa/analysis/`:
- `stats_{mode}_{timestamp}.pickle`: Comprehensive statistics including:
  - Per-question-type F1 and Exact Match scores
  - Results with and without distractor images
  - Training statistics time series
  
Example output format from analysis:
```
Stats breakdown: (with_distractors)
  TextQ: F1=65.23, EM=71.45 (1234 occurrences)
  ImageQ: F1=42.18, EM=48.92 (856 occurrences)
  Compose(Image, Table): F1=38.76, EM=44.21 (523 occurrences)
  ...
  TOTAL: F1=48.79, EM=55.48 (4567 occurrences)
```

**Sources:** [baselines/image_qa/main.py:239-277]()

---

## Training Requirements and Dependencies

### Environment Setup

Training requires the specialized `multimodalqa_image` conda environment:
```bash
conda env create -f environment.yml
source activate multimodalqa_image
```

### External Dependencies

The image QA training has several external dependencies that must be installed:
1. **APEX**: NVIDIA's mixed precision training library
2. **VilBERT-Multi-Task**: Facebook's vision-language pre-training framework
3. **MaskRCNN-Benchmark**: Feature extraction for image regions

For installation instructions, see [Installation and Environment Setup](#2.1).

### Pre-trained Model Checkpoints

Training requires downloading the VilBERT pre-trained checkpoint:
```bash
./scripts/download.sh  # Downloads to downloads/vilbert/
```

**Sources:** [baselines/README.md:4-16](), [baselines/image_qa/README.md:4-11]()

---

## Text and Table QA Training

The text and table QA models follow similar training procedures but with modality-specific implementations. Detailed training instructions are provided in their respective README files:

- **Text QA**: See `baselines/text_qa/README.md` for training with BERT/RoBERTa on text paragraphs
- **Table QA**: See `baselines/table_qa/README.md` for training with BERT/RoBERTa on linearized tables

Both models:
- Use the same three-mode training strategy (`implicit_decomp`, `auto_routing`, `context_only`)
- Fine-tune from pre-trained BERT/RoBERTa checkpoints
- Support the same hyperparameter configuration patterns as image QA
- Generate mode-specific checkpoints in their respective directories

**Sources:** [baselines/README.md:50-52]()

---

## Summary: Training Pipeline

The complete training pipeline for all modalities can be summarized as:

```mermaid
graph TB
    START["Start Training"]
    START --> ENV["Setup Environment<br/>conda env create -f environment.yml"]
    ENV --> DOWNLOAD["Download Data & Models<br/>./scripts/download.sh"]
    
    DOWNLOAD --> CHOOSE_MOD{"Select Modality"}
    
    CHOOSE_MOD -->|Text| TEXT_TRAIN["python text_qa/train.py<br/>--mode {implicit_decomp|auto_routing|context_only}"]
    CHOOSE_MOD -->|Table| TABLE_TRAIN["python table_qa/train.py<br/>--mode {implicit_decomp|auto_routing|context_only}"]
    CHOOSE_MOD -->|Image| IMAGE_TRAIN["python image_qa/main.py<br/>--mode {implicit_decomp|auto_routing|context_only}"]
    
    TEXT_TRAIN --> TEXT_OUT["text_qa_models/{mode}/"]
    TABLE_TRAIN --> TABLE_OUT["table_qa_models/{mode}/"]
    IMAGE_TRAIN --> IMAGE_OUT["image_qa_models/{mode}/model.pt"]
    
    TEXT_OUT --> EVAL["Evaluate with pipeline.py"]
    TABLE_OUT --> EVAL
    IMAGE_OUT --> EVAL
    
    EVAL --> RESULTS["Compute F1/EM Metrics<br/>By Modality, Hop Type, Question Type"]
```

**Key Points:**
- Three independent training pipelines, one per modality
- Each modality requires three training runs for the three modes
- Total of 9 model checkpoints for complete baseline system
- Training can be parallelized across modalities since they are independent

**Sources:** [baselines/README.md:50-52](), [baselines/image_qa/README.md:13-19]()

---

