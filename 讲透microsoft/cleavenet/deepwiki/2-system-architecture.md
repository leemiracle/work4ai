<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/cleavenet · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [cleavenet/models.py](cleavenet/models.py)

</details>



## Purpose and Scope

This document provides a comprehensive overview of CleaveNet's system architecture, explaining the core components and their interactions. It covers the predictor and generator pipelines, model architectures, and data flow throughout the system. For installation instructions, see [Installation and Setup](#1.1). For a quick introduction to using the system, see [Quick Start Guide](#1.2).

## High-Level System Overview

CleaveNet consists of two primary components working together in an end-to-end AI pipeline designed for protease substrate design:

1. **Predictor Component**: Estimates cleavage potential (Z-scores) of peptide sequences for various Matrix Metalloproteinases (MMPs)
2. **Generator Component**: Creates novel peptide sequences with desired cleavage profiles

These components interact with data sources, user interfaces, and each other to enable both analysis and design of protease substrates.

### System Architecture Diagram

```mermaid
graph TD
    subgraph "Core Components"
        PC["Predictor Component"] --- PM["Models:<br>TransformerEncoder<br>RNNPredictor"]
        GC["Generator Component"] --- GM["Models:<br>TransformerDecoder<br>ConditionalTransformerDecoder<br>AutoregressiveRNN"]
        
        PC --> |"Predicts<br>Z-scores"| PA["Analysis:<br>confidence_score()"]
        GC --> |"Generates<br>sequences"| EV["Evaluation:<br>prediction()"]
        
        PA --> |"Feeds<br>targets"| GC
        EV --> |"Validates"| PC
    end
    
    subgraph "Data Processing"
        KD["Kukreja Dataset<br>(data/kukreja.csv)"] --> DL["DataLoader<br>(data.py)"]
        DL --> TR["Training Splits"]
        DL --> TS["Test Splits"]
        TR --> PC
        TR --> GC
        TS --> PA
    end
    
    subgraph "User Interfaces"
        TP["train_predictor.py"] --> PC
        TG["train_generator.py"] --> GC
        PP["predict.py"] --> PA
        GS["generate.py"] --> EV
        NB["Jupyter Notebooks<br>simple_inference()<br>predict_scores_simple()"] --> PA
        NB --> EV
    end
    
    subgraph "Outputs"
        PA --> |"Z-scores"| ZS["Predicted Cleavage<br>(all_scores.csv)"]
        PA --> |"Plots"| VP["Visualization<br>(plots/*.png)"]
        EV --> |"Peptides"| NP["New Sequences<br>(sequences.txt)"]
        PA --> |"Analysis"| SA["Selectivity Score<br>calc_selectivity_score()"]
    end
```

Sources: [README.md:3-11](), [cleavenet/models.py:245-460](), [cleavenet/models.py:815-857]()

## Data Flow Pipeline

The CleaveNet system processes data through distinct stages from input to final output, with different paths for prediction and generation tasks.

```mermaid
flowchart LR
    subgraph "Input Data"
        KD["data/kukreja.csv"] --> DL["DataLoader<br>(data.py)"]
        US["User Sequences"] --> PP["predict.py"]
        TZ["Target Z-scores"] --> GS["generate.py"]
    end

    subgraph "Model Training"
        DL --> SP["Create Train/Test Splits"]
        SP --> TR["Training Data"]
        TR --> TRP["train_predictor.py"]
        TR --> TRG["train_generator.py"]
        
        TRP --> |"Train"| TPM["Predictor Models:<br>TransformerEncoder<br>RNNPredictor"]
        TRG --> |"Train"| TGM["Generator Models:<br>TransformerDecoder<br>ConditionalTransformerDecoder"]
        
        TPM --> |"Save"| WD["weights/<br>model_type_ensemble/"]
        TGM --> |"Save"| WG["weights/AUTOREG_<br>model_type/"]
    end
    
    subgraph "Inference Pipeline"
        PP --> |"Load weights"| WD
        GS --> |"Load weights"| WG
        
        US --> PP
        TZ --> GS
        
        WD --> PR["prediction()"]
        WG --> GN["inference()"]
        
        PR --> |"Z-scores"| RA["Results Analysis"]
        GN --> |"Sequences"| SO["Sequence Output"]
        
        RA --> CS["confidence_score()"]
        RA --> DF["save_to_dataframe()"]
        RA --> SE["calc_selectivity_score()"]
    end
    
    subgraph "Outputs"
        DF --> CSV["CSV Files"]
        DF --> PL["Plot Files"]
        SE --> VZ["Visualizations"]
        CS --> UN["Uncertainty Estimates"]
        SO --> SQ["Generated Sequences"]
    end
```

Sources: [README.md:101-136](), [cleavenet/models.py:657-712](), [cleavenet/models.py:715-815]()

## Core Components

### Predictor Component

The predictor component analyzes peptide sequences to estimate their cleavage potential by various Matrix Metalloproteinases (MMPs). It outputs Z-scores indicating how likely a sequence is to be cleaved by each MMP.

#### Architecture and Models

The predictor uses two main model architectures:

1. **Transformer-based Predictor**:
   - `TransformerEncoder` class from [cleavenet/models.py:314-384]()
   - Uses self-attention mechanisms with positional encoding
   - Supports ensemble prediction for higher accuracy and uncertainty quantification

2. **LSTM-based Predictor**:
   - `RNNPredictor` class from [cleavenet/models.py:387-459]()
   - Uses bidirectional LSTM layers for sequence analysis
   - May have better extrapolation to unseen protease patterns in some cases

#### Prediction Flow

```mermaid
flowchart TD
    subgraph "Predictor Pipeline"
        I["Input Sequences"] --> TK["Tokenize & Pad<br>(tokenize_sequences)"]
        TK --> M["Load Model Ensembles<br>(load_predictor_model)"]
        M --> P["Generate Predictions<br>(prediction)"]
        P --> E["Ensemble Results<br>(confidence_score)"]
        E --> |"Mean Z-scores"| Z["Predicted Z-scores"]
        E --> |"Standard Deviation"| U["Uncertainty Estimates"]
        Z --> A["Analysis:<br>- Selectivity<br>- AUC<br>- Visualizations"]
    end
```

Sources: [cleavenet/models.py:715-815](), [README.md:106-119]()

### Generator Component

The generator component creates new peptide sequences with desired cleavage properties. It can operate in both unconditional and conditional modes, where the latter generates sequences based on target Z-score profiles.

#### Architecture and Models

The generator uses these model architectures:

1. **Transformer-based Generators**:
   - `TransformerDecoder` for unconditional generation from [cleavenet/models.py:246-270]()
   - `ConditionalTransformerDecoder` for conditional generation from [cleavenet/models.py:272-311]()
   - Implements causal self-attention for autoregressive generation

2. **LSTM-based Generator**:
   - `AutoregressiveRNN` from [cleavenet/models.py:520-561]()
   - Uses stacked LSTM layers for sequence generation
   - Supports both conditional and unconditional generation

#### Generation Flow

```mermaid
flowchart TD
    subgraph "Generator Pipeline"
        I["Target Z-scores<br>or Unconditional"] --> M["Load Generator Model<br>(load_generator_model)"]
        M --> G["Generate Sequences<br>(inference)"]
        G --> |"Apply Temperature<br>& Repeat Penalty"| S["Generated Sequences"]
        S --> E["Evaluate with Predictor<br>(prediction)"]
        E --> A["Analyze Results:<br>- Selectivity<br>- Diversity<br>- Properties"]
    end
```

Sources: [cleavenet/models.py:657-712](), [README.md:166-176]()

## Model Architecture Details

CleaveNet employs both Transformer and LSTM architectures for its prediction and generation tasks. The following diagram shows the relationship between different model types:

```mermaid
graph TD
    subgraph "Model Class Hierarchy"
        TR["Transformer Models"] --> TE["TransformerEncoder<br>(models.py:314-384)"]
        TR --> TD["TransformerDecoder<br>(models.py:246-270)"]
        TR --> CTD["ConditionalTransformerDecoder<br>(models.py:272-311)"]
        
        RNN["RNN-based Models"] --> RP["RNNPredictor<br>(models.py:387-459)"]
        RNN --> AR["AutoregressiveRNN<br>(models.py:520-561)"]
    end
    
    subgraph "Component Layers"
        TE --> EL["EncoderLayer<br>(models.py:157-172)"]
        TD --> DL["DecoderLayer<br>(models.py:203-217)"]
        CTD --> DL
        
        EL --> GSA["GlobalSelfAttention<br>(models.py:99-113)"]
        EL --> FF1["FeedForward<br>(models.py:136-154)"]
        
        DL --> CSA["CausalSelfAttention<br>(models.py:116-133)"]
        DL --> FF2["FeedForward<br>(models.py:136-154)"]
        
        GSA --> BA1["BaseAttention<br>(models.py:86-96)"]
        CSA --> BA2["BaseAttention<br>(models.py:86-96)"]
        
        RP --> LSTM1["Bidirectional LSTM Layers"]
        AR --> LSTM2["Stacked LSTM Layers"]
    end
    
    subgraph "Tasks"
        TE --> PR["Prediction:<br>Z-score Estimation"]
        RP --> PR
        
        TD --> GE["Generation:<br>Unconditional"]
        CTD --> GC["Generation:<br>Conditional"]
        AR --> GE
        AR --> GC
    end
```

Sources: [cleavenet/models.py:86-561]()

### Transformer Architecture

The Transformer models in CleaveNet follow the architecture from the original "Attention is All You Need" paper, with modifications for the specific tasks:

1. **TransformerEncoder**:
   - Global self-attention allows information to flow bi-directionally
   - Positional encoding is added to embeddings to preserve sequence position information
   - Used for prediction tasks with a final dense layer to output Z-scores

2. **TransformerDecoder/ConditionalTransformerDecoder**:
   - Causal self-attention masks future positions during training and generation
   - Autoregressive generation with softmax sampling for token prediction
   - Conditional version accepts Z-score conditioning inputs to guide generation

### LSTM Architecture

The LSTM models use recurrent connections to process sequences:

1. **RNNPredictor**:
   - Two stacked bidirectional LSTM layers
   - Final dense layers for Z-score prediction
   - Dropout and regularization to prevent overfitting

2. **AutoregressiveRNN**:
   - Stacked LSTM layers (default 4)
   - Autoregressive generation similar to the Transformer decoder
   - Temperature sampling and repeat penalties to control generation quality

## Training and Inference Pipeline

### Training Process

The training process involves these key steps:

1. Data loading and preprocessing via `DataLoader`
2. Split creation for training and validation
3. Model instantiation with appropriate hyperparameters
4. Training loop with optimizer and loss functions
5. Checkpoint saving to the `weights/` directory

```mermaid
flowchart TD
    subgraph "Training Pipeline"
        D["data/kukreja.csv"] --> DL["DataLoader<br>data.py"]
        DL --> S["Create Splits<br>train/val/test"]
        
        subgraph "Predictor Training"
            S --> TP["train_predictor.py"]
            TP --> MI1["Initialize Model:<br>TransformerEncoder<br>or RNNPredictor"]
            MI1 --> TR1["Train with<br>regression loss"]
            TR1 --> CP1["Save Checkpoints<br>weights/model_type_ensemble/"]
        end
        
        subgraph "Generator Training"
            S --> TG["train_generator.py"]
            TG --> MI2["Initialize Model:<br>TransformerDecoder<br>or AutoregressiveRNN"]
            MI2 --> TR2["Train with<br>cross-entropy loss"]
            TR2 --> CP2["Save Checkpoints<br>weights/AUTOREG_model_type/"]
        end
    end
```

Sources: [README.md:86-104]()

### Inference Process

The inference process varies between prediction and generation:

#### Prediction Inference

```mermaid
flowchart TD
    subgraph "Prediction Inference"
        I["Input Sequences"] --> TK["Tokenize Sequences"]
        TK --> LE["Load Ensemble Models<br>load_predictor_model()"]
        LE --> FP["Forward Pass<br>Through Models"]
        FP --> EA["Ensemble Averaging<br>confidence_score()"]
        EA --> |"Mean"| Z["Predicted Z-scores"]
        EA --> |"Std Dev"| U["Uncertainty Estimates"]
        Z --> A["Analysis<br>save_to_dataframe()"]
        A --> O["Output Files:<br>- all_scores.csv<br>- all_uncertainty.csv<br>- Plots"]
    end
```

Sources: [cleavenet/models.py:715-815]()

#### Generation Inference

```mermaid
flowchart TD
    subgraph "Generation Inference"
        I["Input:<br>Unconditional or<br>Target Z-scores"] --> LM["Load Model<br>load_generator_model()"]
        LM --> ST["Set Temperature<br>and Repeat Penalty"]
        ST --> AR["Autoregressive Generation<br>inference()"]
        AR --> |"Sample Token by Token"| S["Generated Sequences"]
        S --> O["Output:<br>- sequences.txt<br>- Evaluation Results"]
    end
```

Sources: [cleavenet/models.py:657-712]()

## API and User Interfaces

CleaveNet provides several interfaces for users to interact with the system:

### Command-line Interfaces

1. **Training Scripts**:
   - `train_predictor.py` - Trains the predictor component
   - `train_generator.py` - Trains the generator component

2. **Inference Scripts**:
   - `predict.py` - Predicts cleavage for input sequences
   - `generate.py` - Generates new peptide sequences

### API Functions

For programmatic use, CleaveNet provides simplified interfaces:

1. **Prediction API**:
   - `predict_scores_simple()` - Simple interface for prediction
   - `prediction()` - Full prediction pipeline with analysis

2. **Generation API**:
   - `simple_inference()` - Simple interface for sequence generation
   - `inference()` - Full generation pipeline

```mermaid
graph TD
    subgraph "User Interfaces"
        CLI["Command Line Interfaces"] --> TP["train_predictor.py"]
        CLI --> TG["train_generator.py"]
        CLI --> PP["predict.py"]
        CLI --> GP["generate.py"]
        
        API["API Functions"] --> PSS["predict_scores_simple()<br>(models.py:818-826)"]
        API --> SI["simple_inference()<br>(models.py:828-857)"]
    end
    
    subgraph "Implementation Functions"
        PSS --> P["prediction()<br>(models.py:715-815)"]
        SI --> I["inference()<br>(models.py:657-712)"]
        
        TP --> LPM["load_predictor_model()<br>(models.py:619-654)"]
        PP --> P
        
        TG --> LGM["load_generator_model()<br>(models.py:563-617)"]
        GP --> I
    end
```

Sources: [cleavenet/models.py:657-857](), [README.md:86-176]()

## Summary

CleaveNet's architecture is designed as an end-to-end pipeline for protease substrate design with two primary components: the predictor for estimating cleavage potential and the generator for creating peptide sequences. Both components utilize Transformer and LSTM architectures and can be accessed through command-line interfaces or API functions. The system is designed to be modular, allowing components to be used independently or together in a complete pipeline.

For detailed information about specific components, please refer to:
- [Predictor Component](#2.1)
- [Generator Component](#2.2)
- [Model Architectures](#2.3)

---

