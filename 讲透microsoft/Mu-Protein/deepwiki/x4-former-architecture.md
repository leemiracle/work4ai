<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Mu-Protein · page 2.2 μFormer Architecture · patched2 2026-10-26 -->

# μFormer Architecture
# μFormer Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mu-former/requirements.txt](mu-former/requirements.txt)
- [mu-former/src/data.py](mu-former/src/data.py)
- [mu-former/src/model.py](mu-former/src/model.py)
- [mu-former/src/trainer.py](mu-former/src/trainer.py)

</details>



This document provides a detailed explanation of the μFormer model architecture, the second stage of the μProtein framework responsible for predicting mutational effects on protein fitness. μFormer leverages pretrained protein language models (PMLM) to create accurate fitness prediction models that serve as differentiable oracles for protein optimization.

For information about the overall system architecture, see [System Architecture](#2). For details about PMLM pretraining, see [PMLM Pretraining](#2.1). For training procedures, see [μFormer Training](#4.1).

## Architecture Overview

μFormer implements a siamese encoder-decoder architecture that processes pairs of protein sequences to predict fitness differences. The system combines semantic representations from pretrained language models with motif-based features through specialized decoder components.

**μFormer System Architecture**

```mermaid
graph TB
    subgraph "μFormer Architecture"
        subgraph "Data Layer"
            PairedDataset["PairedDataset"]
            MetagenesisData["MetagenesisData"] 
            FairseqLMEncoder["FairseqLMEncoder"]
        end
        
        subgraph "Model Layer"
            Muformer["Muformer"]
            
            subgraph "Encoder"
                PMLM_Encoder["Pretrained PMLM Encoder"]
            end
            
            subgraph "Decoder Options"
                SiameseMuformerDecoder["SiameseMuformerDecoder"]
                MonoMuformerDecoder["MonoMuformerDecoder"]
            end
            
            subgraph "Components"
                ResnetBlock1d["ResnetBlock1d"]
                LengthMaxPool1D["LengthMaxPool1D"]
                MaskedConv1d["MaskedConv1d"]
            end
        end
        
        subgraph "Training Layer"
            Trainer["Trainer"]
            EarlyStopping["EarlyStopping"]
            Saver["Saver"]
        end
    end
    
    PairedDataset --> MetagenesisData
    MetagenesisData --> FairseqLMEncoder
    FairseqLMEncoder --> Muformer
    
    PMLM_Encoder --> Muformer
    SiameseMuformerDecoder --> Muformer
    MonoMuformerDecoder --> Muformer
    
    ResnetBlock1d --> SiameseMuformerDecoder
    ResnetBlock1d --> MonoMuformerDecoder
    LengthMaxPool1D --> SiameseMuformerDecoder
    LengthMaxPool1D --> MonoMuformerDecoder
    MaskedConv1d --> ResnetBlock1d
    
    Muformer --> Trainer
    EarlyStopping --> Trainer
    Saver --> Trainer
```

Sources: [mu-former/src/model.py:1-315](), [mu-former/src/data.py:1-454](), [mu-former/src/trainer.py:1-600]()

## Core Model Components

The μFormer architecture consists of several key components that work together to predict mutational effects.

### Muformer Class

The `Muformer` class serves as the main model orchestrator, combining a pretrained encoder with specialized decoders for mutation effect prediction.

**Muformer Component Structure**

```mermaid
graph TB
    subgraph "Muformer Model"
        subgraph "Input Processing"
            x1["x1: Mutant Sequence"]
            x2["x2: Wild-type Sequence"]
            x1_mask["x1_mask: Attention Mask"]
            x2_mask["x2_mask: Attention Mask"]
        end
        
        subgraph "Encoder Stage"
            encoder["encoder: Pretrained PMLM"]
            encoder_forward["encoder(x1) -> (features, _)"]
            permute["permute(1, 0, 2)"]
        end
        
        subgraph "Decoder Stage"
            decoder["decoder: SiameseMuformerDecoder | MonoMuformerDecoder"]
            decoder_forward["decoder(x1, x2, masks) -> (s_sem, s_motif)"]
        end
        
        subgraph "Probability Computation"
            prob_computation["encoder.prob() -> lm_prob1, lm_prob2"]
            diff_prob["diff_prob() -> s_prob"]
        end
        
        subgraph "Output Combination"
            output_combination["(s_sem + s_motif + s_prob) / 2"]
        end
    end
    
    x1 --> encoder_forward
    x2 --> encoder_forward
    encoder_forward --> permute
    permute --> decoder_forward
    
    x1_mask --> decoder_forward
    x2_mask --> decoder_forward
    
    decoder_forward --> output_combination
    prob_computation --> diff_prob
    diff_prob --> output_combination
```

Sources: [mu-former/src/model.py:225-315]()

### Decoder Architectures

μFormer supports two decoder architectures for different use cases:

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `SiameseMuformerDecoder` | Paired sequence comparison | Processes wild-type and mutant sequences simultaneously |
| `MonoMuformerDecoder` | Single sequence analysis | Processes individual sequences independently |

**SiameseMuformerDecoder Architecture**

```mermaid
graph TB
    subgraph "SiameseMuformerDecoder"
        subgraph "Input Reduction"
            fc_reduce1["fc_reduce: Linear(encoder_dim -> hidden_size)"]
            fc_reduce2["fc_reduce: Linear(encoder_dim -> hidden_size)"]
        end
        
        subgraph "Feature Extraction"
            x1_semantics["x1_semantics = x1[:, 0, :]"]
            x2_semantics["x2_semantics = x2[:, 0, :]"]
            
            motif_net["motif_net: ModuleList[ResnetBlock1d]"]
            pooling["pooling: LengthMaxPool1D"]
        end
        
        subgraph "Distance Computation"
            dist_semantics["dist_semantics: Linear layers"]
            dist_motifs["dist_motifs: Linear layers"]
        end
        
        subgraph "Outputs"
            s_sem["s_sem: Semantic similarity score"]
            s_motif["s_motif: Motif similarity score"]
        end
    end
    
    fc_reduce1 --> x1_semantics
    fc_reduce2 --> x2_semantics
    fc_reduce1 --> motif_net
    fc_reduce2 --> motif_net
    motif_net --> pooling
    
    x1_semantics --> dist_semantics
    x2_semantics --> dist_semantics
    pooling --> dist_motifs
    
    dist_semantics --> s_sem
    dist_motifs --> s_motif
```

Sources: [mu-former/src/model.py:93-158]()

### Convolutional Components

The decoder uses specialized convolutional components for motif detection and sequence analysis.

| Component | Function | Implementation |
|-----------|----------|----------------|
| `MaskedConv1d` | Masked 1D convolution | Applies attention masks during convolution |
| `ResnetBlock1d` | Residual block | Two masked conv layers with skip connection |
| `LengthMaxPool1D` | Length-aware pooling | Max pooling across sequence length |

Sources: [mu-former/src/model.py:50-92]()

## Data Processing Pipeline

The data processing pipeline handles protein sequences, mutations, and fitness labels through several specialized classes.

**Data Processing Flow**

```mermaid
flowchart LR
    subgraph "Input Data"
        TSV["TSV Files: train/valid/test"]
        FASTA["FASTA File: Native sequence"]
    end
    
    subgraph "PairedDataset Processing"
        read_mutation_df["_read_mutation_df()"]
        split_dataset_df["_split_dataset_df()"]
        mutation_to_sequence["_mutation_to_sequence()"]
    end
    
    subgraph "FairseqLMEncoder"
        tokenizer["tokenizer: fairseq alphabet"]
        encode_line["encode_line()"]
        pad_sequences["_pad_sequences()"]
    end
    
    subgraph "MetagenesisData"
        native_sample["native_sample generation"]
        label_oper["label_oper: minus/divide"]
        data_augment["data_augment: aug_ratio"]
    end
    
    subgraph "Output"
        DataLoader["torch.utils.data.DataLoader"]
    end
    
    TSV --> read_mutation_df
    FASTA --> mutation_to_sequence
    read_mutation_df --> split_dataset_df
    split_dataset_df --> encode_line
    encode_line --> pad_sequences
    pad_sequences --> native_sample
    native_sample --> label_oper
    label_oper --> data_augment
    data_augment --> DataLoader
```

Sources: [mu-former/src/data.py:139-454]()

### Data Classes and Methods

| Class/Method | Purpose | Key Parameters |
|--------------|---------|----------------|
| `PairedDataset` | Main data orchestrator | `train_tsv`, `valid_tsv`, `test_tsv`, `fasta` |
| `MetagenesisData` | Dataset wrapper with augmentation | `mode`, `label_oper`, `aug_ratio` |
| `FairseqLMEncoder` | Sequence tokenization | `alphabet`, `batch_size` |
| `_mutation_to_sequence()` | Convert mutation strings to sequences | Handles format like "A123G" |
| `_pad_sequences()` | Batch sequence padding | `constant_value=1`, variable `length` |

Sources: [mu-former/src/data.py:85-454]()

## Training Infrastructure

The training infrastructure provides comprehensive support for model training, evaluation, and distributed computing.

**Training Component Interactions**

```mermaid
graph TB
    subgraph "Trainer Class"
        subgraph "Initialization"
            init_model["init_model()"]
            set_seed["set_seed()"]
            init_distributed_mode["init_distributed_mode()"]
        end
        
        subgraph "Training Loop"
            train_epoch["_train_epoch()"]
            evaluate_and_save_best["_evaluate_and_save_best()"]
            log_epoch_progress["_log_epoch_progress()"]
        end
        
        subgraph "Model Management"
            load_checkpoint["load_checkpoint()"]
            save_checkpoint["save_checkpoint()"]
            load_pretrained_model["load_pretrained_model()"]
        end
        
        subgraph "Utilities"
            Saver["Saver: Checkpoint management"]
            EarlyStopping["EarlyStopping: Training control"]
            Logger["Logger: Distributed logging"]
        end
    end
    
    subgraph "External Components"
        PolynomialLRDecay["PolynomialLRDecay"]
        InverseSqrtLRDecay["InverseSqrtLRDecay"]
        criterion["criterion: Loss functions"]
    end
    
    init_model --> train_epoch
    train_epoch --> evaluate_and_save_best
    evaluate_and_save_best --> log_epoch_progress
    
    Saver --> save_checkpoint
    EarlyStopping --> evaluate_and_save_best
    Logger --> log_epoch_progress
    
    PolynomialLRDecay --> train_epoch
    InverseSqrtLRDecay --> train_epoch
    criterion --> train_epoch
```

Sources: [mu-former/src/trainer.py:80-600]()

### Training Configuration

The trainer supports extensive configuration for different training scenarios:

| Parameter | Purpose | Default Value |
|-----------|---------|---------------|
| `encoder_lr` | Learning rate for pretrained encoder | `1e-5` |
| `decoder_lr` | Learning rate for decoder | `1e-4` |
| `weight_decay` | L2 regularization strength | `0.0` |
| `freeze_lm` | Whether to freeze language model | `False` |
| `num_ensembles` | Number of ensemble models | `1` |
| `batch_size` | Training batch size | `128` |

Sources: [mu-former/src/trainer.py:191-210]()

## Integration with PMLM

μFormer integrates closely with pretrained protein language models through the fairseq framework.

**PMLM Integration Architecture**

```mermaid
graph TB
    subgraph "PMLM Integration"
        subgraph "Model Loading"
            checkpoint_utils["checkpoint_utils.load_model_ensemble_and_task()"]
            arg_overrides["arg_overrides: {'data': tokendict_path}"]
            models_task["models, _, task"]
        end
        
        subgraph "Components Extraction"
            encoder["encoder = models[0]"]
            alphabet["alphabet = task.source_dictionary"]
            encoder_dim["encoder_dim = encoder.args.encoder_embed_dim"]
            num_heads["num_heads = encoder.args.encoder_attention_heads"]
        end
        
        subgraph "Muformer Integration"
            muformer_init["Muformer(encoder, vocab_size, encoder_dim, ...)"]
            freeze_module_params["freeze_module_params() if freeze_lm"]
        end
    end
    
    checkpoint_utils --> models_task
    arg_overrides --> checkpoint_utils
    models_task --> encoder
    models_task --> alphabet
    encoder --> encoder_dim
    encoder --> num_heads
    
    encoder --> muformer_init
    encoder --> freeze_module_params
```

Sources: [mu-former/src/trainer.py:114-132]()

The integration enables μFormer to leverage pretrained representations while fine-tuning for specific mutation prediction tasks. The system supports both frozen and trainable encoder configurations depending on the available training data and computational resources.

Sources: [mu-former/src/trainer.py:1-600](), [mu-former/src/model.py:225-315]()

---

