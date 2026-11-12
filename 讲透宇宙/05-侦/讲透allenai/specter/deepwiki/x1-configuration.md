<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/specter · extra page Configuration · fetched 2026-10-26 -->

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [experiment_configs/simple.jsonnet](experiment_configs/simple.jsonnet)

</details>



This document covers the configuration system for training SPECTER models, focusing on the structure and customization of training configurations. The primary configuration is defined in Jsonnet format and controls all aspects of model training including data reading, model architecture, and training parameters.

For information about running training scripts with these configurations, see [Training Scripts](#4.2.2). For details on preparing training data, see [Data Preparation](#4.2.1).

## Configuration Architecture

SPECTER uses AllenNLP's configuration system based on Jsonnet, which provides a flexible way to define training experiments through external variables and structured configuration objects.

### Configuration Flow Diagram

```mermaid
graph TB
    subgraph "External Variables"
        env_vars["Environment Variables<br/>TRAIN_PATH, DEV_PATH, etc."]
        shell_script["Shell Script<br/>run-exp-simple.sh"]
    end
    
    subgraph "Configuration Processing"
        jsonnet_config["simple.jsonnet<br/>Main Configuration"]
        allennlp_config["AllenNLP Config<br/>Processed JSON"]
    end
    
    subgraph "Training Components"
        dataset_reader["specter_data_reader_pickled<br/>Data Loading"]
        model_config["specter Model<br/>Architecture Definition"]
        trainer_config["AllenNLP Trainer<br/>Training Loop"]
        vocab_config["Vocabulary<br/>Token Mapping"]
    end
    
    env_vars --> jsonnet_config
    shell_script --> env_vars
    jsonnet_config --> allennlp_config
    
    allennlp_config --> dataset_reader
    allennlp_config --> model_config
    allennlp_config --> trainer_config
    allennlp_config --> vocab_config
    
    dataset_reader --> model_config
    model_config --> trainer_config
```

Sources: [experiment_configs/simple.jsonnet:1-186]()

## Configuration File Structure

The main configuration is defined in `simple.jsonnet` and consists of five primary sections:

| Section | Purpose | Key Components |
|---------|---------|----------------|
| `dataset_reader` | Data loading configuration | Reader type, tokenization, sequence length |
| `iterator` | Batch processing | Batch size, caching settings |
| `model` | Model architecture | Encoders, embedders, loss functions |
| `trainer` | Training parameters | Optimizer, learning rate, GPU settings |
| `vocabulary` | Token vocabulary | Vocabulary directory path |

### External Variable System

The configuration uses external variables for parameterization, allowing the same configuration to be used across different experiments:

```mermaid
graph LR
    subgraph "Script Variables"
        TRAIN_PATH["TRAIN_PATH<br/>Training data file"]
        DEV_PATH["DEV_PATH<br/>Validation data file"]
        BERT_VOCAB["BERT_VOCAB<br/>Vocabulary path"]
        BERT_MODEL["BERT_MODEL<br/>Model architecture"]
        BERT_WEIGHTS["BERT_WEIGHTS<br/>Pretrained weights"]
        NUM_EPOCHS["NUM_EPOCHS<br/>Training epochs"]
        BATCH_SIZE["BATCH_SIZE<br/>Batch size"]
        MAX_SEQ_LEN["MAX_SEQ_LEN<br/>Sequence length"]
        CUDA_DEVICE["CUDA_DEVICE<br/>GPU device"]
    end
    
    subgraph "Jsonnet Processing"
        extVar["std.extVar()<br/>Variable extraction"]
        stringToBool["stringToBool()<br/>Type conversion"]
        parseInt["std.parseInt()<br/>Type conversion"]
    end
    
    subgraph "Configuration Sections"
        dataset_reader_config["dataset_reader<br/>Configuration"]
        model_config["model<br/>Configuration"]
        trainer_config["trainer<br/>Configuration"]
    end
    
    TRAIN_PATH --> extVar
    DEV_PATH --> extVar
    BERT_VOCAB --> extVar
    BERT_MODEL --> extVar
    BERT_WEIGHTS --> extVar
    NUM_EPOCHS --> parseInt
    BATCH_SIZE --> extVar
    MAX_SEQ_LEN --> parseInt
    CUDA_DEVICE --> extVar
    
    extVar --> dataset_reader_config
    parseInt --> model_config
    stringToBool --> trainer_config
```

Sources: [experiment_configs/simple.jsonnet:6-21]()

## Dataset Reader Configuration

The dataset reader configuration controls how training data is processed:

```json
"dataset_reader": {
    "type": "specter_data_reader_pickled",
    "concat_title_abstract": true,
    "lazy": true,
    "max_sequence_length": MAX_SEQ_LEN,
    "token_indexers": {
        "bert": {
            "type": BERT_MODEL,
            "do_lowercase": true,
            "truncate_long_sequences": true
        }
    },
    "word_splitter": "bert-basic"
}
```

Key parameters:
- `type`: Specifies `specter_data_reader_pickled` for reading pickled training data
- `concat_title_abstract`: Combines title and abstract into single sequence
- `lazy`: Enables lazy loading for memory efficiency
- `max_sequence_length`: Controls maximum input sequence length
- `token_indexers`: Defines BERT tokenization strategy

Sources: [experiment_configs/simple.jsonnet:23-38]()

## Model Architecture Configuration

The model configuration defines the SPECTER architecture with multiple encoders and embedders:

### Model Component Diagram

```mermaid
graph TB
    subgraph "Text Processing"
        text_field_embedder["text_field_embedder<br/>BERT Token Embedder"]
        bert_embedder["bert TokenEmbedder<br/>BERT Model"]
    end
    
    subgraph "Content Encoders"
        title_encoder["title_encoder<br/>BOE Encoder"]
        abstract_encoder["abstract_encoder<br/>BOE Encoder"]
        venue_encoder["venue_encoder<br/>BOE Encoder"]
    end
    
    subgraph "Author Processing"
        author_id_embedder["author_id_embedder<br/>Token Embedder"]
        author_position_embedder["author_position_embedder<br/>Position Embedder"]
        author_feedforward["author_feedforward<br/>Feedforward Network"]
    end
    
    subgraph "Final Processing"
        feedforward["feedforward<br/>Final Feedforward"]
        loss_function["TripletLoss<br/>l2-norm distance"]
    end
    
    text_field_embedder --> bert_embedder
    bert_embedder --> title_encoder
    bert_embedder --> abstract_encoder
    bert_embedder --> venue_encoder
    
    author_id_embedder --> author_feedforward
    author_position_embedder --> author_feedforward
    
    title_encoder --> feedforward
    abstract_encoder --> feedforward
    venue_encoder --> feedforward
    author_feedforward --> feedforward
    
    feedforward --> loss_function
```

Sources: [experiment_configs/simple.jsonnet:44-140]()

### Key Model Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `bert_finetune` | true | Enables BERT fine-tuning |
| `dropout` | 0.25 | Dropout rate for regularization |
| `embedding_layer_norm` | true | Layer normalization for embeddings |
| `loss_distance` | "l2-norm" | Distance metric for triplet loss |
| `loss_margin` | "1" | Margin for triplet loss |
| `ignore_authors` | true | Disables author information |
| `include_venue` | INCLUDE_VENUE | Venue information toggle |

Sources: [experiment_configs/simple.jsonnet:81-102]()

## Training Configuration

The trainer configuration controls the training process:

### Training Parameter Structure

```mermaid
graph TB
    subgraph "Optimization"
        optimizer["bert_adam<br/>AdamW Optimizer"]
        learning_rate["3e-5<br/>Learning Rate"]
        weight_decay["0.01<br/>Weight Decay"]
        grad_clipping["1<br/>Gradient Clipping"]
    end
    
    subgraph "Scheduling"
        lr_scheduler["slanted_triangular<br/>Learning Rate Scheduler"]
        cut_frac["0.1<br/>Cut Fraction"]
        num_epochs["NUM_EPOCHS<br/>Training Epochs"]
    end
    
    subgraph "Hardware"
        cuda_device["CUDA_DEVICE<br/>GPU Configuration"]
        batch_accumulation["32<br/>Gradient Accumulation"]
    end
    
    subgraph "Monitoring"
        validation_metric["-loss<br/>Validation Metric"]
        patience["5<br/>Early Stopping"]
        model_save_interval["10000<br/>Save Interval"]
    end
    
    optimizer --> learning_rate
    optimizer --> weight_decay
    optimizer --> grad_clipping
    
    lr_scheduler --> cut_frac
    lr_scheduler --> num_epochs
    
    cuda_device --> batch_accumulation
    
    validation_metric --> patience
    patience --> model_save_interval
```

Sources: [experiment_configs/simple.jsonnet:144-182]()

### Optimizer Configuration

The configuration uses `bert_adam` optimizer with specific parameter groups:

```json
"optimizer": {
    "type": "bert_adam",
    "lr": "3e-5",
    "max_grad_norm": 1,
    "parameter_groups": [
        [
            ["bias", "LayerNorm.bias", "LayerNorm.weight", "layer_norm.weight"],
            {"weight_decay": 0}
        ]
    ],
    "t_total": -1,
    "weight_decay": 0.01
}
```

This configuration:
- Uses BERT-specific AdamW optimizer
- Sets different weight decay for bias and LayerNorm parameters
- Implements gradient clipping with norm of 1
- Uses slanted triangular learning rate scheduling

Sources: [experiment_configs/simple.jsonnet:159-178]()

## Customization Guide

### Common Configuration Modifications

| Parameter | Location | Common Values | Purpose |
|-----------|----------|---------------|---------|
| `MAX_SEQ_LEN` | External variable | 128, 256, 512 | Control input sequence length |
| `BATCH_SIZE` | External variable | 8, 16, 32 | Adjust batch size for memory |
| `NUM_EPOCHS` | External variable | 5, 10, 20 | Set training duration |
| `BERT_WEIGHTS` | External variable | "bert-base-uncased", "allenai/scibert_scivocab_uncased" | Choose base model |
| `INCLUDE_VENUE` | External variable | true, false | Include venue information |

### Model Architecture Customization

To modify the model architecture, edit the `model` section:

1. **Encoder dimensions**: Modify `embedding_dim` in title_encoder, abstract_encoder, venue_encoder
2. **Feedforward layers**: Adjust `hidden_dims` and `num_layers` in feedforward configuration
3. **Dropout rates**: Change `dropout` values throughout the model
4. **Loss function**: Modify `loss_distance` and `loss_margin` parameters

### Training Parameter Tuning

Common training modifications:

1. **Learning rate**: Adjust `lr` in optimizer section
2. **Gradient accumulation**: Modify `gradient_accumulation_batch_size`
3. **Early stopping**: Change `patience` value
4. **Validation frequency**: Adjust `model_save_interval`

Sources: [experiment_configs/simple.jsonnet:1-186]()

---

