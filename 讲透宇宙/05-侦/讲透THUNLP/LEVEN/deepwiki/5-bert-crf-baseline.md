<!-- source: DeepWiki mcp.deepwiki.com · repo thunlp/LEVEN · page 5 BERT+CRF Baseline · fetched 2026-11-02 -->

# BERT+CRF Baseline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Baselines/BERT+CRF/README.md](Baselines/BERT+CRF/README.md)
- [Baselines/BERT+CRF/bert_crf.py](Baselines/BERT+CRF/bert_crf.py)
- [Baselines/BERT+CRF/crf.py](Baselines/BERT+CRF/crf.py)

</details>



The BERT+CRF baseline is the primary and most extensively documented implementation in the LEVEN repository for event type classification. It combines BERT contextual embeddings with a Conditional Random Field (CRF) layer to perform sequence labeling on Chinese legal documents, classifying event mentions into 110 distinct event types using the BIO tagging scheme.

This page provides a comprehensive overview of the BERT+CRF baseline system, including its architecture, workflow, and key components. For detailed documentation on specific aspects:
- Architecture details: see [BERT+CRF Architecture](#5.1)
- Training procedures: see [BERT+CRF Training](#5.2)
- Inference procedures: see [BERT+CRF Inference](#5.3)
- Data processing utilities: see [BERT+CRF Data Utilities](#5.4)
- Performance analysis: see [BERT+CRF Performance Analysis](#5.5)

For comparison with other baseline implementations, see [Baselines Comparison](#4).

## System Overview

The BERT+CRF baseline implements a neural sequence labeling model that processes tokenized Chinese text through BERT to generate contextualized embeddings, then uses a CRF layer to decode the optimal label sequence while modeling label dependencies. The system is built on HuggingFace Transformers and adapted from an existing NER implementation.

### Key Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Base Model** | BERT (Chinese pretrained: `bert-base-chinese`) |
| **Sequence Labeling** | CRF with Viterbi decoding |
| **Label Space** | ~220 labels (110 event types × 2 for BIO + O tag) |
| **Framework** | PyTorch with HuggingFace Transformers |
| **Training Strategy** | Adam optimizer with linear warmup, gradient accumulation, mixed precision (fp16) support |
| **Input Format** | JSONL with documents, events, and mentions |
| **Output Format** | JSONL with per-mention event type predictions |

**Sources:** [Baselines/BERT+CRF/README.md:1-30]()

## Core Architecture Components

```mermaid
graph TB
    subgraph "BertCRFForTokenClassification"
        BERT["BertModel<br/>(self.bert)"]
        DROPOUT["Dropout Layer<br/>(self.dropout)"]
        CLASSIFIER["Linear Classifier<br/>(self.classifier)<br/>hidden_size → num_labels+2"]
        CRF_MODULE["CRF Module<br/>(self.crf)"]
    end
    
    subgraph "CRF Implementation"
        TRANSITIONS["Transition Matrix<br/>(self.transitions)<br/>(tagset_size+2, tagset_size+2)"]
        FORWARD_ALG["Forward Algorithm<br/>(_calculate_PZ)"]
        VITERBI["Viterbi Decoding<br/>(_viterbi_decode)"]
        SCORE["Gold Score<br/>(_score_sentence)"]
    end
    
    subgraph "Data Processing"
        TOKENIZER["BertTokenizer"]
        FEATURES["InputFeatures<br/>(input_ids, attention_mask, labels)"]
        CRF_PAD["to_crf_pad<br/>(utils_leven.py)"]
        CRF_UNPAD["unpad_crf<br/>(utils_leven.py)"]
    end
    
    INPUT["Input Text"] --> TOKENIZER
    TOKENIZER --> FEATURES
    FEATURES --> BERT
    BERT --> DROPOUT
    DROPOUT --> CLASSIFIER
    CLASSIFIER --> CRF_PAD
    CRF_PAD --> CRF_MODULE
    
    CRF_MODULE --> TRANSITIONS
    TRANSITIONS --> VITERBI
    TRANSITIONS --> FORWARD_ALG
    TRANSITIONS --> SCORE
    
    VITERBI --> CRF_UNPAD
    CRF_UNPAD --> OUTPUT["Predicted Labels"]
    
    FORWARD_ALG --> LOSS["NLL Loss"]
    SCORE --> LOSS
```

**Sources:** [Baselines/BERT+CRF/bert_crf.py:15-87](), [Baselines/BERT+CRF/crf.py:29-281]()

### BertCRFForTokenClassification Class

The `BertCRFForTokenClassification` class is the main model implementation, inheriting from `BertPreTrainedModel`. It integrates BERT with a CRF layer for sequence labeling.

**Key Components:**

| Component | Type | Purpose |
|-----------|------|---------|
| `self.bert` | `BertModel` | Generates contextualized token embeddings |
| `self.dropout` | `nn.Dropout` | Regularization layer (dropout probability from config) |
| `self.classifier` | `nn.Linear` | Projects BERT hidden states to emission scores (size: `hidden_size → num_labels+2`) |
| `self.crf` | `CRF` | Conditional Random Field for sequence decoding |
| `self.num_labels` | `int` | Number of distinct labels (excluding START/STOP tags) |

**Sources:** [Baselines/BERT+CRF/bert_crf.py:15-29]()

### CRF Layer Implementation

The `CRF` class implements a Conditional Random Field with learnable transition parameters and Viterbi decoding.

**Key Components:**

| Component | Type | Dimensions | Purpose |
|-----------|------|------------|---------|
| `self.transitions` | `nn.Parameter` | `(tagset_size+2, tagset_size+2)` | Transition scores from tag_i to tag_j |
| `START_TAG` | `int` | `-2` | Special tag ID for sequence start |
| `STOP_TAG` | `int` | `-1` | Special tag ID for sequence end |
| `_calculate_PZ()` | method | - | Computes partition function (forward algorithm) |
| `_viterbi_decode()` | method | - | Finds best label sequence (Viterbi algorithm) |
| `_score_sentence()` | method | - | Scores gold label sequences |

The transition matrix is initialized with `-10000.0` for invalid transitions (transitions to `START_TAG` and from `STOP_TAG`), ensuring these paths have negligible probability.

**Sources:** [Baselines/BERT+CRF/crf.py:29-51](), [Baselines/BERT+CRF/crf.py:113-216]()

## File Structure and Dependencies

```mermaid
graph TB
    subgraph "Entry Points"
        TRAIN_SH["run_train.sh<br/>Training script"]
        INFER_SH["run_infer.sh<br/>Inference script"]
    end
    
    subgraph "Core Implementation"
        RUN_LEVEN["run_leven.py<br/>Main training/inference engine"]
        BERT_CRF["bert_crf.py<br/>BertCRFForTokenClassification"]
        CRF_PY["crf.py<br/>CRF class"]
        UTILS["utils_leven.py<br/>Data processing utilities"]
    end
    
    subgraph "External Dependencies"
        TRANSFORMERS["transformers<br/>(BertModel, BertTokenizer)"]
        SEQEVAL["seqeval<br/>(metrics for NER)"]
        TORCH["torch<br/>(PyTorch)"]
    end
    
    subgraph "Data Assets"
        DATA_JSONL["data/*.jsonl<br/>(train/dev/test)"]
        CACHE["cached_*.pt<br/>(processed features)"]
    end
    
    TRAIN_SH --> RUN_LEVEN
    INFER_SH --> RUN_LEVEN
    
    RUN_LEVEN --> BERT_CRF
    RUN_LEVEN --> UTILS
    BERT_CRF --> CRF_PY
    BERT_CRF --> TRANSFORMERS
    
    UTILS --> TRANSFORMERS
    UTILS --> DATA_JSONL
    UTILS --> CACHE
    
    RUN_LEVEN --> SEQEVAL
    RUN_LEVEN --> TORCH
```

**Directory Structure:**

```
Baselines/BERT+CRF/
├── README.md                    # Usage instructions and requirements
├── run_train.sh                 # Training shell script
├── run_infer.sh                 # Inference shell script
├── run_leven.py                 # Main training/inference engine
├── bert_crf.py                  # BertCRFForTokenClassification model
├── crf.py                       # CRF layer implementation
├── utils_leven.py               # Data processing utilities
├── data/                        # LEVEN dataset (train/dev/test.jsonl)
└── outputs/                     # Model checkpoints and results
```

**Sources:** [Baselines/BERT+CRF/README.md:20-28](), [Baselines/BERT+CRF/bert_crf.py:1-6]()

## System Requirements

The BERT+CRF baseline has specific version requirements for compatibility:

| Dependency | Version | Purpose |
|-----------|---------|---------|
| Python | 3.6.9 | Runtime environment |
| PyTorch | 1.2.0 | Deep learning framework |
| Transformers | 2.6.0 | BERT model and tokenizer |
| scikit-learn | 0.20.2 | Evaluation utilities |
| seqeval | latest | NER-specific metrics (precision, recall, F1) |

**Note:** The specific transformers version (2.6.0) is required for compatibility with the custom CRF integration, which is based on a fork that adds NER-CRF capabilities to the library.

**Sources:** [Baselines/BERT+CRF/README.md:6-16]()

## Model Forward Pass

The forward pass through `BertCRFForTokenClassification` follows a multi-stage pipeline:

```mermaid
graph LR
    INPUT["input_ids<br/>attention_mask<br/>token_type_ids"] --> GET_FEAT["_get_features()"]
    
    subgraph "_get_features()"
        BERT_FWD["self.bert()"] --> SEQ_OUT["sequence_output"]
        SEQ_OUT --> DROP_FWD["self.dropout()"]
        DROP_FWD --> CLASS_FWD["self.classifier()"]
        CLASS_FWD --> FEATS["feats<br/>(emission scores)"]
    end
    
    GET_FEAT --> FEATS
    FEATS --> MODE{Training?}
    
    MODE -->|Yes| TRAIN_PATH["Training Path"]
    MODE -->|No| INFER_PATH["Inference Path"]
    
    subgraph "Training Path"
        PAD_TRAIN["to_crf_pad()"] --> NLL["self.crf.neg_log_likelihood()"]
        NLL --> LOSS_OUT["loss"]
        PAD_TRAIN --> VITERBI_TRAIN["self.crf()"]
        VITERBI_TRAIN --> UNPAD_TRAIN["unpad_crf()"]
        UNPAD_TRAIN --> BEST_PATH_TRAIN["best_path"]
    end
    
    subgraph "Inference Path"
        PAD_INFER["to_crf_pad()"] --> VITERBI_INFER["self.crf()"]
        VITERBI_INFER --> UNPAD_INFER["unpad_crf()"]
        UNPAD_INFER --> BEST_PATH_INFER["best_path"]
    end
    
    TRAIN_PATH --> LOSS_OUT
    TRAIN_PATH --> BEST_PATH_TRAIN
    INFER_PATH --> BEST_PATH_INFER
```

**Training Mode:** When `labels` are provided, the model computes:
1. Emission scores from the classifier
2. CRF loss via `neg_log_likelihood()` (forward score - gold score)
3. Best path predictions via Viterbi decoding
4. Returns: `(loss, logits, hidden_states, best_path)`

**Inference Mode:** When `labels` are not provided:
1. Emission scores from the classifier
2. Best path predictions via Viterbi decoding
3. Returns: `(logits, hidden_states, best_path)`

**Sources:** [Baselines/BERT+CRF/bert_crf.py:31-86]()

## CRF Padding and Unpadding

The BERT+CRF system uses special padding utilities to handle variable-length sequences with the CRF layer:

### to_crf_pad Function

The `to_crf_pad()` function reshapes tensors for CRF processing by:
- Filtering out padding tokens (where `mask == False`)
- Packing sequences into a batch-compatible format
- Creating a new mask for the CRF layer

**Input:** `(tensor, mask, pad_value)`
**Output:** `(padded_tensor, crf_mask)`

### unpad_crf Function

The `unpad_crf()` function reverses the padding operation:
- Restores original sequence lengths
- Places predictions back into their original positions
- Fills padding positions with `pad_token_label_id`

**Input:** `(crf_output, crf_mask, original_labels, original_mask)`
**Output:** `unpacked_predictions`

These utilities are critical for interfacing between BERT's token-level processing (which uses attention masks for variable-length sequences) and the CRF layer's requirement for packed sequences without padding.

**Sources:** [Baselines/BERT+CRF/bert_crf.py:6](), [Baselines/BERT+CRF/bert_crf.py:63-64](), [Baselines/BERT+CRF/bert_crf.py:79-83]()

## Training and Inference Workflow

### Basic Usage Pattern

```mermaid
graph TD
    START["Setup Environment"] --> DOWNLOAD["Download LEVEN Data"]
    DOWNLOAD --> PLACE["Place in data/ folder"]
    
    PLACE --> TRAIN_MODE{Mode?}
    
    TRAIN_MODE -->|Training| RUN_TRAIN["Execute run_train.sh"]
    TRAIN_MODE -->|Inference| RUN_INFER["Execute run_infer.sh"]
    
    RUN_TRAIN --> TRAIN_ARGS["Set Arguments:<br/>--do_train<br/>--do_eval<br/>--data_dir<br/>--output_dir"]
    TRAIN_ARGS --> TRAIN_EXEC["run_leven.py main()"]
    TRAIN_EXEC --> TRAIN_LOOP["Training Loop"]
    TRAIN_LOOP --> CKPT["Save Checkpoints"]
    CKPT --> VAL["Validation on Dev Set"]
    VAL --> METRICS["Report Metrics"]
    
    RUN_INFER --> INFER_ARGS["Set Arguments:<br/>--do_infer<br/>--data_dir<br/>--output_dir"]
    INFER_ARGS --> INFER_EXEC["run_leven.py main()"]
    INFER_EXEC --> LOAD_CKPT["Load Best Checkpoint"]
    LOAD_CKPT --> INFER_LOOP["Inference Loop"]
    INFER_LOOP --> RESULTS["Generate results.jsonl"]
```

**Training Workflow:**
1. Execute `run_train.sh` with appropriate arguments
2. The script calls `run_leven.py` with `--do_train` and `--do_eval` flags
3. Model trains on training set with periodic validation
4. Best checkpoint is saved based on validation F1 score
5. Evaluation metrics are reported

**Inference Workflow:**
1. Execute `run_infer.sh` with test data path
2. The script calls `run_leven.py` with `--do_infer` flag
3. Best checkpoint is loaded from `--output_dir`
4. Predictions are generated for test set
5. Results are written to `OUTPUT_PATH/results.jsonl`

**Sources:** [Baselines/BERT+CRF/README.md:20-28]()

## Key Implementation Details

### Label Space Configuration

The model uses `num_labels + 2` for the classifier output dimension, where:
- `num_labels`: Number of BIO labels from the dataset (~220 for 110 event types)
- `+2`: Additional dimensions for CRF START and STOP tags

**Sources:** [Baselines/BERT+CRF/bert_crf.py:26]()

### Loss Calculation

The model uses negative log-likelihood loss computed by the CRF layer:

```
loss = forward_score - gold_score
```

Where:
- `forward_score`: Log partition function (sum of scores over all possible paths)
- `gold_score`: Score of the gold label sequence

This formulation encourages the model to increase the score of the gold path while normalizing across all possible paths.

**Sources:** [Baselines/BERT+CRF/crf.py:269-280]()

### Viterbi Decoding

During inference, the CRF layer uses the Viterbi algorithm to find the highest-scoring label sequence:
1. Initialize with START tag scores
2. Iterate through sequence, computing maximum scores and backpointers
3. Terminate with STOP tag transition
4. Backtrack to recover best path

This ensures that the predicted label sequence respects transition constraints learned by the CRF.

**Sources:** [Baselines/BERT+CRF/crf.py:113-215]()

## Integration with LEVEN Data Format

The BERT+CRF baseline processes LEVEN JSONL data through a series of transformations:

```mermaid
graph LR
    JSONL["JSONL Format<br/>documents, events, mentions"] --> READ["read_examples_from_file()"]
    READ --> EXAMPLES["InputExample objects<br/>(words, labels)"]
    EXAMPLES --> CONVERT["convert_examples_to_features()"]
    CONVERT --> FEATURES["InputFeatures objects<br/>(input_ids, masks, label_ids)"]
    FEATURES --> CACHE["Cached Features<br/>cached_*.pt"]
    CACHE --> LOADER["DataLoader"]
    LOADER --> MODEL["BertCRFForTokenClassification"]
    MODEL --> PREDICTIONS["Token-level Predictions"]
    PREDICTIONS --> MAP["Map to pure_event2id"]
    MAP --> OUTPUT["results.jsonl"]
```

The system maintains compatibility with the LEVEN annotation schema by:
- Preserving document IDs and mention spans
- Mapping BIO tags to event type IDs using `pure_event2id` dictionary
- Handling negative triggers appropriately
- Supporting evaluation on both development and test sets

**Sources:** Referenced from high-level diagrams and typical data processing flow

## Advantages of BERT+CRF Architecture

| Advantage | Description |
|-----------|-------------|
| **Contextual Embeddings** | BERT provides rich, context-aware representations of Chinese characters and words |
| **Label Dependencies** | CRF models transition probabilities between adjacent labels (e.g., B-买入 → I-买入) |
| **Global Optimization** | Viterbi decoding ensures globally optimal label sequences, not just locally optimal labels |
| **Pretrained Knowledge** | Leverages BERT's pretraining on large-scale Chinese corpora |
| **Structured Prediction** | CRF layer enforces valid BIO tag sequences (e.g., prevents I-tag without preceding B-tag) |

The combination of BERT's semantic understanding with CRF's structured prediction makes this baseline particularly effective for sequence labeling tasks with complex label dependencies.

## Performance Characteristics

The BERT+CRF baseline is designed for:
- **Large label space**: ~220 labels (110 event types with BIO encoding)
- **Variable-length sequences**: Handles documents with different lengths via padding and masking
- **GPU acceleration**: Optimized for CUDA with optional mixed precision training
- **Distributed training**: Supports multi-GPU training for faster convergence

For detailed performance metrics and analysis, see [BERT+CRF Performance Analysis](#5.5).

---

This overview establishes the foundation for understanding the BERT+CRF baseline. The child pages provide detailed documentation on specific aspects of the implementation, training procedures, and performance characteristics.

---

