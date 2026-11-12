<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/sentiment-discovery · page 3 Usage Workflows · fetched 2026-10-26 -->

# Usage Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [data/semeval/test.csv](data/semeval/test.csv)
- [data/semeval/train.csv](data/semeval/train.csv)
- [data/semeval/val.csv](data/semeval/val.csv)

</details>



This document provides detailed guides for the main usage workflows in the sentiment discovery system. It covers the complete pipeline from data preparation through model pretraining to downstream applications including transfer learning, classifier finetuning, and inference.

For information about the core system components and model architectures, see [Core Components](#2). For specific experimental configurations and benchmarks, see [Experiments and Benchmarks](#4).

## Workflow Overview

The sentiment discovery system follows a two-stage approach: unsupervised language model pretraining followed by supervised adaptation for downstream tasks. The system supports multiple pathways for applying pretrained models to classification tasks.

```mermaid
graph TD
    subgraph "Data Preparation"
        A["Raw Text Data"] --> B["configure_data.py"]
        B --> C["Tokenization"]
        C --> D["DataLoader"]
    end
    
    subgraph "Language Model Pretraining"
        E["pretrain.py"] --> F["Language Model Training"]
        F --> G["Saved Model (.pt)"]
    end
    
    subgraph "Downstream Applications"
        H["transfer.py"]
        I["finetune_classifier.py"] 
        J["run_classifier.py"]
    end
    
    D --> E
    G --> H
    G --> I
    G --> J
    
    H --> K["Feature Extraction + Logistic Regression"]
    I --> L["End-to-End Finetuning"]
    J --> M["Classification Inference"]
```

**Main Workflow Scripts**
| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `pretrain.py` | Unsupervised language model training | Raw text data | Pretrained model (.pt) |
| `transfer.py` | Feature-based transfer learning | Pretrained model + labeled data | Sklearn classifier |
| `finetune_classifier.py` | End-to-end classifier finetuning | Pretrained model + labeled data | Finetuned classifier |
| `run_classifier.py` | Inference on new data | Trained classifier + test data | Predictions (.npy) |

Sources: [README.md:107-196](), [README.md:29-44]()

## Data Preparation Workflow

All workflows begin with data preparation using the `configure_data.py` system. The system supports multiple data formats and tokenization methods.

```mermaid
graph LR
    subgraph "Input Formats"
        A["CSV Files"]
        B["JSON Files"] 
        C["Loose JSON"]
    end
    
    subgraph "configure_data.py"
        D["DatasetPaths"]
        E["TokenizerType"]
        F["DataLoader Config"]
    end
    
    subgraph "Tokenization Options"
        G["CharacterTokenizer"]
        H["SentencePieceTokenizer"]
        I["BPETokenizer"]
    end
    
    subgraph "Output"
        J["DataLoader"]
        K["Dataset Splits"]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    E --> G
    E --> H
    E --> I
    
    G --> F
    H --> F
    I --> F
    
    F --> J
    F --> K
```

**Key Configuration Arguments**
- `--data`: Path to training data file
- `--text-key`: Column name for text data  
- `--label-key`: Column name for labels
- `--tokenizer-type`: CharacterTokenizer, SentencePieceTokenizer, or BPE
- `--vocab-size`: Vocabulary size for subword tokenization
- `--split`: Train/validation/test split ratios

Sources: [README.md:134-149]()

## Language Model Pretraining Pipeline

The pretraining workflow trains language models on large text corpora using `pretrain.py`. The system supports both recurrent (mLSTM) and transformer architectures with distributed training capabilities.

```mermaid
graph TD
    subgraph "Model Architecture Selection"
        A["--model LSTM"] --> D["mLSTMModel"]
        B["--model transformer"] --> E["TransformerModel"]
        C["--model GRU"] --> F["GRUModel"]
    end
    
    subgraph "pretrain.py Execution"
        G["ArgumentParser"] --> H["configure_data.py"]
        H --> I["DataLoader Creation"]
        I --> J["Model Instantiation"]
        J --> K["Training Loop"]
    end
    
    subgraph "Training Optimizations"
        L["--fp16"] --> M["Mixed Precision Training"]
        N["--distributed"] --> O["Multi-GPU Training"] 
        P["--dynamic-loss-scale"] --> Q["FP16 Stability"]
    end
    
    subgraph "Output"
        R["lang_model.pt"]
        S["Training Logs"]
        T["Checkpoints"]
    end
    
    D --> J
    E --> J
    F --> J
    
    K --> M
    K --> O
    K --> Q
    
    K --> R
    K --> S
    K --> T
```

**Common Pretraining Commands**
```bash
# Basic mLSTM training
python3 pretrain.py --model LSTM --nhid 4096

# Transformer with SentencePiece tokenization  
python3 pretrain.py --model transformer --tokenizer-type SentencePieceTokenizer --vocab-size 32000

# Distributed FP16 training
python3 -m multiproc pretrain.py --fp16 --dynamic-loss-scale
```

Sources: [README.md:129-156](), [README.md:134-149]()

## Transfer Learning Workflow

The `transfer.py` script implements feature-based transfer learning by extracting representations from pretrained language models and training sklearn classifiers on top.

```mermaid
graph TD
    subgraph "Input Processing"
        A["Pretrained Model (.pt)"] --> B["Model Loading"]
        C["Labeled Dataset"] --> D["Data Loading"]
    end
    
    subgraph "transfer.py Pipeline"
        E["Feature Extraction"]
        F["Train/Val/Test Featurization"]
        G["Logistic Regression Training"]
        H["Feature Selection"]
        I["Top-k Neuron Selection"]
    end
    
    subgraph "Output Generation"
        J["Classification Results"]
        K["Feature Importance"]
        L["Transfer Directory"]
    end
    
    B --> E
    D --> F
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    I --> K
    
    J --> L
    K --> L
```

**Key Transfer Learning Parameters**
- `--load`: Path to pretrained model
- `--neurons`: Number of top neurons for feature selection (default: 1)
- `--data`, `--val`, `--test`: Dataset file paths
- `--fp16`: Use mixed precision for feature extraction

**Example Transfer Commands**
```bash
# Basic transfer to SST
python3 transfer.py --load mlstm.pt

# Multi-neuron transfer
python3 transfer.py --load mlstm.pt --neurons 5

# Custom dataset transfer
python3 transfer.py --load transformer.pt --data train.csv --val val.csv --test test.csv
```

Sources: [README.md:157-172]()

## Classifier Finetuning Workflow  

The `finetune_classifier.py` script performs end-to-end finetuning where gradients flow from the classification loss back into the language model encoder.

```mermaid
graph TD
    subgraph "Model Architecture"
        A["Pretrained LM"] --> B["LanguageModelEncoder"]
        C["Classification Head"] --> D["SentimentClassifier"]
        B --> D
    end
    
    subgraph "finetune_classifier.py Features"
        E["Multi-label Classification"]
        F["Multi-head Classification"] 
        G["Auxiliary LM Loss"]
        H["Automatic Thresholding"]
        I["Complex Metrics"]
    end
    
    subgraph "Training Configuration"
        J["--lr Learning Rate"]
        K["--aux-lm-loss-weight"]
        L["--automatic-thresholding"]
        M["--threshold-metric"]
    end
    
    subgraph "Advanced Features"
        N["--heads-per-class"]
        O["--classifier-hidden-layers"]
        P["--aux-head-variance-loss-weight"]
    end
    
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    
    J --> D
    K --> G
    L --> H
    M --> H
    
    N --> F
    O --> D
    P --> F
```

**Finetuning Command Examples**
```bash
# Basic finetuning with auxiliary LM loss
python3 finetune_classifier.py --load mlstm.pt --lr 2e-5 --aux-lm-loss --aux-lm-loss-weight 0.02

# Multi-head classification with automatic thresholding
python3 finetune_classifier.py --load transformer.pt --automatic-thresholding --threshold-metric f1 --heads-per-class 4

# Multi-layer classifier for custom dataset
python3 finetune_classifier.py --load mlstm.pt --data train.csv --val val.csv --test test.csv --classifier-hidden-layers 2048 1024 3
```

**Supported Metrics**
- F1-score
- Matthews Correlation Coefficient  
- Jaccard Index
- Recall, Precision, Accuracy

Sources: [README.md:173-196]()

## Inference and Evaluation Workflow

The `run_classifier.py` script performs classification inference on new data using trained models and saves probability outputs.

```mermaid
graph TD
    subgraph "Input Requirements"
        A["Trained Model (.pt)"] --> B["Model Loading"]
        C["Input Data (CSV/JSON)"] --> D["Data Processing"]
    end
    
    subgraph "run_classifier.py Pipeline"
        E["Text Preprocessing"]
        F["Tokenization"]
        G["Model Inference"]
        H["Probability Calculation"]
    end
    
    subgraph "Output Generation"
        I["Classification Probabilities"]
        J["Prediction Arrays (.npy)"]
        K["Evaluation Metrics"]
    end
    
    B --> E
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    I --> K
```

**Inference Command Examples**
```bash
# Basic classification on SST
python3 run_classifier.py --load ama_sst.pt

# FP16 inference
python3 run_classifier.py --load ama_sst_16.pt --fp16

# Custom dataset classification  
python3 run_classifier.py --load model.pt --text-key tweet_text --data custom_data.csv
```

**Key Arguments**
- `--load_model`: Path to trained classifier
- `--text-key`: Column name containing text to classify
- `--data`: Input data file path
- `--fp16`: Enable mixed precision inference

Sources: [README.md:116-128]()

## Multi-Dataset Training Scripts

The system includes shell scripts for reproducible experiments across multiple datasets:

```mermaid
graph LR
    subgraph "Experiment Scripts"
        A["run_sk_sst.sh"] --> B["SST Transfer Learning"]
        C["run_sk_imdb.sh"] --> D["IMDB Transfer Learning"] 
        E["run_se_multihead.sh"] --> F["SemEval Multi-head Classification"]
        G["run_se_singlehead.sh"] --> H["SemEval Single-head Classification"]
    end
    
    subgraph "Core Workflows"
        I["transfer.py"]
        J["finetune_classifier.py"]
    end
    
    B --> I
    D --> I  
    F --> J
    H --> J
```

**Available Experiment Scripts**
- `bash ./experiments/run_sk_sst.sh`: mLSTM transfer learning on SST
- `bash ./experiments/run_sk_imdb.sh`: mLSTM transfer learning on IMDB  
- `bash ./experiments/run_se_multihead.sh`: Multi-head transformer finetuning on SemEval
- `bash ./experiments/train_mlstm_singlenode.sh`: Single-node mLSTM pretraining
- `bash ./experiments/train_transformer_singlenode.sh`: Single-node transformer pretraining

Sources: [README.md:147-148](), [README.md:167-168](), [README.md:190]()

---

