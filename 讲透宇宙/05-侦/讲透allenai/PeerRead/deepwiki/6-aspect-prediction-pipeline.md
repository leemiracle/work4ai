<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/PeerRead · page 6 Aspect Prediction Pipeline · fetched 2026-10-26 -->

# Aspect Prediction Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [code/README.md](code/README.md)
- [code/aspect_predict/predict.py](code/aspect_predict/predict.py)
- [code/aspect_predict/run_predict.sh](code/aspect_predict/run_predict.sh)

</details>



## Purpose and Scope

The Aspect Prediction Pipeline is a deep learning system that predicts fine-grained aspect scores from peer review comments and paper content. Given a review text and optionally the paper being reviewed, the pipeline predicts numerical scores (1-5 scale) for up to 9 different review aspects such as RECOMMENDATION, CLARITY, ORIGINALITY, and IMPACT.

This page provides an overview of the complete aspect prediction workflow, from data preparation through model training and evaluation. For detailed information about specific components, see:

- For aspect annotation format and data merging: [Aspect Annotations](#6.1)
- For neural network architectures (CNN, RNN, DAN): [Neural Network Models](#6.2)
- For training procedures and evaluation metrics: [Training and Evaluation](#6.3)

For the alternative acceptance classification pipeline that uses feature engineering and linear models, see [Acceptance Classification Pipeline](#5).

## Pipeline Overview

The Aspect Prediction Pipeline operates as a supervised regression system that learns to map review text (and optionally paper text) to numerical aspect scores. The pipeline differs from the acceptance classification pipeline by using neural networks instead of feature engineering, and by predicting continuous scores rather than binary accept/reject decisions.

**Sources:** [code/README.md:21-37](), [code/aspect_predict/predict.py:1-3]()

### High-Level Workflow

```mermaid
graph TB
    Input["Review JSONs + Paper PDFs<br/>(with aspect annotations)"]
    
    subgraph "Data Preparation (prepare_data)"
        Load["Load Paper + Review objects"]
        Preproc["preprocess()<br/>tokenize, lowercase"]
        Vocab["Build vocabulary<br/>max_vocab_size=35000"]
        Pad["pad_sentence()<br/>paper: 1000 tokens<br/>review: 200 tokens"]
        Merge["assign_annot_iclr_2017.py<br/>merge annotations"]
    end
    
    subgraph "Model Selection"
        Config["config.py<br/>CNNConfig/RNNConfig/DANConfig"]
        Model["pred_models.py<br/>CNN/RNN/DAN class"]
    end
    
    subgraph "Training Loop (predict.py main)"
        Batch["batch_iter()<br/>create mini-batches"]
        Forward["Model forward pass"]
        Loss["MSE Loss"]
        Opt["RMSProp + gradient clipping"]
        EarlyStop["Early stopping on dev RMSE"]
    end
    
    Output["Model checkpoints<br/>RMSE per aspect"]
    
    Input --> Load
    Load --> Merge
    Merge --> Preproc
    Preproc --> Vocab
    Vocab --> Pad
    
    Pad --> Config
    Config --> Model
    
    Model --> Batch
    Batch --> Forward
    Forward --> Loss
    Loss --> Opt
    Opt --> EarlyStop
    
    EarlyStop --> Output
```

**Sources:** [code/aspect_predict/predict.py:56-199](), [code/aspect_predict/predict.py:244-460]()

## Input and Output Specification

### Input Requirements

The pipeline requires three types of input data:

| Input Type | Location | Format | Purpose |
|------------|----------|--------|---------|
| Review JSONs | `{train,dev,test}/reviews_annotated/` | JSON files (Review objects) | Review text with aspect scores |
| Paper PDFs | `{train,dev,test}/parsed_pdfs/` | JSON (ScienceParse output) | Parsed paper content |
| Aspect Annotations | Root dataset directory | `annotation_full.tsv` | Aspect score annotations |

The aspect annotations must be merged with reviews before training. For ICLR 2017 data, this is done by `assign_annot_iclr_2017.py`.

**Sources:** [code/aspect_predict/predict.py:83-106](), [code/README.md:36]()

### Output Artifacts

| Artifact | Location | Description |
|----------|----------|-------------|
| Model checkpoints | `./ckpts/{timestamp}/` | TensorFlow saved models |
| Vocabulary | `{dataset}/vocab.{dataset}.{vocab_size}` | Word-to-index mappings |
| Trained results | `./trained_results/{timestamp}/` | Experiment metadata |
| Evaluation metrics | Console output | RMSE per aspect + baselines |

**Sources:** [code/aspect_predict/predict.py:309-349]()

## Running the Pipeline

### Shell Script Execution

The primary interface for running the pipeline is `run_predict.sh`, which iterates over all aspect labels:

```bash
cd ./code/aspect_predict/
./run_predict.sh
```

The script executes `predict.py` for each of the 9 aspect labels (0-8) with configurable parameters.

**Sources:** [code/README.md:21-28](), [code/aspect_predict/run_predict.sh:1-15]()

### Direct Python Execution

For more control, invoke `predict.py` directly:

```bash
python predict.py <data_dir> <train_text> <model> <label>
```

**Command-line Arguments:**

| Position | Name | Options | Description |
|----------|------|---------|-------------|
| 1 | `data_dir` | Path | Dataset directory (e.g., `../../data/iclr_2017`) |
| 2 | `train_text` | `"all"`, `"review"`, `"paper"` | Input text source |
| 3 | `model` | `"dan"`, `"rnn"`, `"cnn"` | Neural architecture |
| 4 | `label` | `0-8` | Aspect index to predict |

**Sources:** [code/aspect_predict/predict.py:244-251](), [code/README.md:25-28]()

### Configuration in run_predict.sh

The shell script defines default configuration variables:

```bash
DATADIR="../../data/iclr_2017"  # Dataset path
LABELS=(0 1 2 3 4 5 6 7 8)      # All 9 aspects
TRAIN_TEXT="all"                 # Use paper + review
MODEL="dan"                      # Deep Averaging Network
```

**Sources:** [code/aspect_predict/run_predict.sh:2-7]()

## Data Preparation Flow

The `prepare_data()` function orchestrates the transformation from raw data to training-ready tensors:

```mermaid
graph LR
    subgraph "Input Loading"
        Reviews["Review.from_json()<br/>Load review JSONs"]
        Papers["ScienceParseReader<br/>Load parsed PDFs"]
    end
    
    subgraph "Text Processing"
        PP["preprocess()<br/>lowercase, tokenize<br/>remove short words"]
        VB["Vocabulary Building<br/>Counter + most_common<br/>PAD=0, UNK=1"]
    end
    
    subgraph "Sequence Encoding"
        Encode["Word → Index mapping<br/>OOV → UNK(1)"]
        PadP["pad_sentence()<br/>paper → 1000 tokens"]
        PadR["pad_sentence()<br/>review → 200 tokens"]
    end
    
    subgraph "Label Processing"
        Extract["Extract aspect scores<br/>from Review.__dict__"]
        Fill["fill_missing=True/False<br/>ACL vs ICLR"]
    end
    
    Output["(x_paper, x_review, y)<br/>numpy arrays"]
    
    Reviews --> PP
    Papers --> PP
    PP --> VB
    VB --> Encode
    Encode --> PadP
    Encode --> PadR
    Reviews --> Extract
    Extract --> Fill
    
    PadP --> Output
    PadR --> Output
    Fill --> Output
```

**Sources:** [code/aspect_predict/predict.py:56-199]()

### Aspect Label Handling

The pipeline handles different aspect sets for different datasets:

| Dataset | Aspect Count | Aspects | Fill Missing |
|---------|--------------|---------|--------------|
| ICLR | 9 | RECOMMENDATION, SUBSTANCE, APPROPRIATENESS, MEANINGFUL_COMPARISON, SOUNDNESS_CORRECTNESS, ORIGINALITY, CLARITY, IMPACT, RECOMMENDATION_ORIGINAL | False |
| ACL | 9 | RECOMMENDATION, SUBSTANCE, APPROPRIATENESS, MEANINGFUL_COMPARISON, SOUNDNESS_CORRECTNESS, ORIGINALITY, CLARITY, IMPACT, REVIEWER_CONFIDENCE | True |

When `fill_missing=True`, missing aspect values are imputed with the column mean.

**Sources:** [code/aspect_predict/predict.py:69-80](), [code/aspect_predict/predict.py:189-194]()

## Main Components and Responsibilities

### predict.py Function Map

The main script is organized into distinct functional units:

```mermaid
graph TB
    subgraph "Utility Functions"
        models["models(model_text)<br/>Returns Model class + Config"]
        preprocess["preprocess(input, ...)<br/>Text normalization"]
        evaluate["evaluate(y, y_)<br/>RMSE calculation"]
    end
    
    subgraph "Data Pipeline"
        prepare_data["prepare_data()<br/>Load, tokenize, pad<br/>Build vocabulary"]
        choose_label["choose_label()<br/>Filter NaN, select aspect<br/>Compute baselines"]
    end
    
    subgraph "Training Orchestration"
        main["main(args)<br/>End-to-end training"]
        feed_data["feed_data()<br/>Create feed_dict"]
    end
    
    subgraph "External Dependencies"
        Review["models.Review"]
        Paper["models.Paper"]
        SP["models.ScienceParse"]
        Models["pred_models.CNN/RNN/DAN"]
        Config["config.CNNConfig/RNNConfig/DANConfig"]
        Helper["data_helper.load_embeddings<br/>batch_iter, pad_sentence"]
    end
    
    main --> prepare_data
    main --> choose_label
    main --> models
    main --> feed_data
    
    models --> Models
    models --> Config
    prepare_data --> Review
    prepare_data --> Paper
    prepare_data --> SP
    prepare_data --> preprocess
    choose_label --> evaluate
    main --> Helper
```

**Sources:** [code/aspect_predict/predict.py:29-242]()

### Function Responsibilities

| Function | Lines | Purpose |
|----------|-------|---------|
| `models()` | [29-33]() | Maps model name string to Model class and Config class |
| `preprocess()` | [36-49]() | Tokenizes and normalizes text (lowercase, stopword removal, length filtering) |
| `evaluate()` | [52-53]() | Computes RMSE between predictions and ground truth |
| `prepare_data()` | [56-199]() | Loads all data splits, builds vocabulary, encodes sequences, extracts labels |
| `choose_label()` | [203-241]() | Filters data for specific aspect, removes NaN, computes baseline metrics |
| `main()` | [244-460]() | Orchestrates training loop, model creation, checkpointing, evaluation |

**Sources:** [code/aspect_predict/predict.py:1-460]()

## Training Text Options

The pipeline supports three modes for combining paper and review text:

```mermaid
graph LR
    subgraph "Input Options (train_text parameter)"
        Paper["'paper'<br/>x_train = x_train[0]<br/>1000 tokens"]
        Review["'review'<br/>x_train = x_train[1]<br/>200 tokens"]
        All["'all'<br/>concatenate(x_train, axis=1)<br/>1200 tokens"]
    end
    
    subgraph "Model Input"
        SeqLen["config.seq_length<br/>Determines input layer size"]
    end
    
    Paper --> SeqLen
    Review --> SeqLen
    All --> SeqLen
    
    SeqLen --> Embedding["Embedding Layer<br/>vocab_size × embed_dim"]
```

**Sources:** [code/aspect_predict/predict.py:289-304]()

## Baseline Computation

The `choose_label()` function computes two baseline predictions for comparison:

| Baseline | Strategy | Calculation |
|----------|----------|-------------|
| Mean | Predict training set mean for all examples | `np.average(y_aspect)` |
| Majority | Predict most common score for all examples | `Counter(y_aspect).most_common(1)[0][0]` |

These baselines are computed on the training set and evaluated on the test set to measure whether the neural model provides improvement over trivial predictors.

**Sources:** [code/aspect_predict/predict.py:223-241](), [code/aspect_predict/predict.py:274-288]()

## Key Files and Their Roles

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `predict.py` | Main training script | `main()`, `prepare_data()`, `choose_label()` |
| `pred_models.py` | Neural architectures | `CNN`, `RNN`, `DAN` classes |
| `config.py` | Model hyperparameters | `CNNConfig`, `RNNConfig`, `DANConfig` |
| `data_helper.py` | Data utilities | `load_embeddings()`, `batch_iter()`, `pad_sentence()` |
| `run_predict.sh` | Shell orchestration | Loops over aspects and models |
| `assign_annot_iclr_2017.py` | Data preparation | Merges aspect annotations into reviews |

**Sources:** [code/README.md:31-37]()

## Integration with Data Models

The pipeline integrates with the core data models defined in the parent directory:

```mermaid
graph TB
    subgraph "predict.py imports"
        Imp1["from models.Review import Review"]
        Imp2["from models.Paper import Paper"]
        Imp3["from models.ScienceParse import ScienceParse"]
        Imp4["from models.ScienceParseReader import ScienceParseReader"]
    end
    
    subgraph "Data Loading"
        Load1["Paper.from_json(filename)<br/>Load review JSON"]
        Load2["ScienceParseReader.read_science_parse()<br/>Load parsed PDF"]
        Load3["review.COMMENTS<br/>Extract review text"]
        Load4["paper.SCIENCEPARSE.get_paper_content()<br/>Extract paper text"]
    end
    
    Imp1 --> Load1
    Imp2 --> Load1
    Imp3 --> Load2
    Imp4 --> Load2
    
    Load1 --> Load3
    Load2 --> Load4
```

**Sources:** [code/aspect_predict/predict.py:21-25](), [code/aspect_predict/predict.py:104-115]()

---

