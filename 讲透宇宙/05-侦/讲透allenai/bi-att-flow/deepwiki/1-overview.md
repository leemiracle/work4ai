<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/bi-att-flow · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [basic/cli.py](basic/cli.py)
- [basic/graph_handler.py](basic/graph_handler.py)
- [basic/model.py](basic/model.py)

</details>



This document provides a comprehensive overview of the BiDAF (Bi-directional Attention Flow) repository, a neural question answering system designed for machine reading comprehension tasks. The system implements the BiDAF architecture for extractive question answering, primarily targeting the Stanford Question Answering Dataset (SQuAD).

For detailed information about specific model architectures beyond the core BiDAF model, see [Alternative Models](#6). For training and evaluation procedures, see [Training and Evaluation](#4). For deployment and production usage, see [Ensemble and Deployment](#7).

## Purpose and Core Functionality

The BiDAF system is a deep learning framework that answers questions by reading and comprehending text passages. Given a context paragraph and a question, the system identifies the span of text in the context that best answers the question. The implementation supports:

- **Bidirectional attention mechanisms** for context-question interaction
- **Multi-GPU distributed training** and inference
- **Ensemble methods** for improved accuracy
- **Flexible model configurations** through command-line interfaces
- **Integration with standard datasets** like SQuAD

Sources: [README.md:1-8](), [basic/model.py:25-66]()

## System Architecture Overview

The BiDAF system follows a modular architecture with clear separation between data processing, model definition, training, and evaluation components.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Command Interface"
        CLI["basic/cli.py<br/>Command Line Interface"] --> Config["Config Object<br/>Hyperparameters"]
    end
    
    subgraph "Core Orchestration"
        Config --> Main["basic/main.py<br/>Mode Dispatcher"]
        Main --> Train["_train()<br/>Training Mode"]
        Main --> Test["_test()<br/>Testing Mode"] 
        Main --> Forward["_forward()<br/>Inference Mode"]
    end
    
    subgraph "Data Pipeline"
        DataRaw["Raw SQuAD JSON"] --> Prepro["squad/prepro.py<br/>Preprocessing"]
        Prepro --> DataSet["basic/read_data.py<br/>DataSet Class"]
        DataSet --> Main
    end
    
    subgraph "Model Layer"
        Model["basic/model.py<br/>Model Class"] --> MultiGPU["get_multi_gpu_models()"]
        MultiGPU --> Train
        MultiGPU --> Test
        MultiGPU --> Forward
    end
    
    subgraph "Execution Layer"
        Trainer["basic/trainer.py<br/>MultiGPUTrainer"] --> Train
        Evaluator["basic/evaluator.py<br/>Evaluator Classes"] --> Test
        Evaluator --> Forward
        GraphHandler["basic/graph_handler.py<br/>Model Persistence"] --> Train
        GraphHandler --> Test
    end
```

Sources: [basic/cli.py:101-109](), [basic/model.py:15-22](), [basic/graph_handler.py:14-21]()

### Core BiDAF Model Architecture

```mermaid
graph TD
    subgraph "Input Processing"
        Context["Context Text"] --> WordEmb["Word Embeddings<br/>word_emb_mat"]
        Context --> CharEmb["Character Embeddings<br/>char_emb_mat"]
        Question["Question Text"] --> WordEmb
        Question --> CharEmb
        CharEmb --> CNN["multi_conv1d()<br/>Character CNN"]
        CNN --> Highway["highway_network()<br/>Information Highway"]
        WordEmb --> Highway
    end
    
    subgraph "Contextual Encoding"
        Highway --> BiLSTM["bidirectional_dynamic_rnn()<br/>Bidirectional LSTM"]
        BiLSTM --> ContextRep["h: Context Representation"]
        BiLSTM --> QuestionRep["u: Question Representation"] 
    end
    
    subgraph "Attention Layer"
        ContextRep --> BiAtt["bi_attention()<br/>Bidirectional Attention"]
        QuestionRep --> BiAtt
        BiAtt --> C2Q["Context-to-Question<br/>u_a"]
        BiAtt --> Q2C["Question-to-Context<br/>h_a"]
        C2Q --> AttLayer["attention_layer()<br/>Query-Aware Context"]
        Q2C --> AttLayer
        ContextRep --> AttLayer
    end
    
    subgraph "Modeling Layer"
        AttLayer --> ModelLSTM["Modeling LSTM<br/>g0, g1, g2"]
        ModelLSTM --> StartLogits["get_logits()<br/>Start Position"]
        ModelLSTM --> EndLogits["get_logits()<br/>End Position"]
        StartLogits --> SoftMax["softmax<br/>Answer Span"]
        EndLogits --> SoftMax
    end
```

Sources: [basic/model.py:69-195](), [basic/model.py:380-425]()

## Core Components

### Model Class and Multi-GPU Support

The central `Model` class in [basic/model.py:25-378]() implements the BiDAF architecture. The system supports distributed training through the `get_multi_gpu_models()` function, which creates model replicas across multiple GPUs:

| Component | File | Key Functions | Purpose |
|-----------|------|---------------|---------|
| Model | `basic/model.py` | `__init__`, `_build_forward`, `_build_loss` | Core BiDAF implementation |
| Multi-GPU | `basic/model.py` | `get_multi_gpu_models` | Distributed model creation |
| Graph Handler | `basic/graph_handler.py` | `save`, `_load`, `dump_eval` | Model persistence and evaluation storage |

Sources: [basic/model.py:15-22](), [basic/graph_handler.py:14-80]()

### Configuration and Command Line Interface

The system uses TensorFlow's `flags` system for configuration management:

```mermaid
graph LR
    subgraph "CLI Configuration"
        Flags["tf.app.flags<br/>Command Line Flags"] --> Config["config object<br/>FLAGS"]
        Config --> OutDir["out_dir calculation<br/>model_name/run_id"]
        Config --> Main["main(config)<br/>Entry Point"]
    end
    
    subgraph "Key Configuration Categories"
        ModelParams["Model Parameters<br/>hidden_size, batch_size"]
        TrainingParams["Training Parameters<br/>num_epochs, init_lr"]
        DeviceParams["Device Parameters<br/>num_gpus, device_type"]
        DataParams["Data Parameters<br/>data_dir, load_path"]
    end
    
    Config --> ModelParams
    Config --> TrainingParams  
    Config --> DeviceParams
    Config --> DataParams
```

Key configuration parameters include:
- **Model architecture**: `hidden_size`, `char_emb_size`, `highway_num_layers`
- **Training**: `batch_size`, `num_epochs`, `init_lr`, `keep_prob`
- **Multi-GPU**: `num_gpus`, `device_type`
- **Data**: `data_dir`, `load_path`, `eval_path`

Sources: [basic/cli.py:7-99](), [basic/cli.py:101-109]()

### Data Processing Pipeline

The data pipeline transforms raw SQuAD JSON files into model-ready tensors:

```mermaid
graph TD
    subgraph "Data Acquisition"
        Download["download.sh<br/>Data Download"] --> SquadJSON["SQuAD JSON Files"]
        Download --> GloVe["GloVe Embeddings"]
    end
    
    subgraph "Preprocessing"
        SquadJSON --> Prepro["squad/prepro.py<br/>Text Processing"]
        GloVe --> Prepro
        Prepro --> ProcessedData["Processed Data Files<br/>shared.json, data.json"]
    end
    
    subgraph "Runtime Loading"
        ProcessedData --> ReadData["basic/read_data.py<br/>DataSet Class"]
        ReadData --> Batches["get_batches()<br/>Mini-batch Generation"]
        Batches --> FeedDict["get_feed_dict()<br/>TensorFlow Placeholders"]
    end
```

The `DataSet` class manages data loading and batching, while the `Model.get_feed_dict()` method converts data into TensorFlow placeholders.

Sources: [basic/model.py:245-377](), [basic/read_data.py]() (referenced in model.py)

## Execution Modes

The system supports three primary execution modes orchestrated by [basic/main.py]():

| Mode | Function | Purpose | Key Components |
|------|----------|---------|----------------|  
| `train` | `_train()` | Model training | `MultiGPUTrainer`, loss computation, checkpointing |
| `test` | `_test()` | Model evaluation | `MultiGPUF1Evaluator`, metrics calculation |
| `forward` | `_forward()` | Inference/prediction | `ForwardEvaluator`, answer generation |

Each mode utilizes the same underlying `Model` class but with different evaluator and trainer components.

Sources: [basic/cli.py:26](), [basic/main.py]() (referenced in cli.py)

## Getting Started

### Quick Start Sequence

```mermaid
graph TD
    subgraph "Setup Phase"
        Install["Install Dependencies<br/>tensorflow, nltk, tqdm"] --> Download["./download.sh<br/>Data Acquisition"]
        Download --> Preprocess["python -m squad.prepro<br/>Data Preprocessing"]
    end
    
    subgraph "Training Phase"
        Preprocess --> Debug["python -m basic.cli --mode train --noload --debug<br/>Verify Setup"]
        Debug --> Train["python -m basic.cli --mode train --noload<br/>Full Training"]
    end
    
    subgraph "Evaluation Phase"
        Train --> Test["python -m basic.cli<br/>Model Testing"]
        Test --> Official["python squad/evaluate-v1.1.py<br/>Official Scoring"]
    end
```

### System Requirements

- **GPU Memory**: Minimum 12GB for default batch size (60)
- **Training Time**: ~20 hours on NVIDIA Titan X
- **Model Size**: ~2.5M parameters
- **Multi-GPU**: Supported for distributed training

Sources: [README.md:8-57](), [README.md:138-151]()

### Performance Benchmarks

The system achieves the following performance on SQuAD:

| Model Type | Dev EM | Dev F1 | Test EM | Test F1 |
|------------|--------|--------|---------|---------|
| Single | 67.7% | 77.3% | 68.0% | 77.3% |
| Ensemble | 72.6% | 80.7% | 73.3% | 81.1% |

Sources: [README.md:104-122]()

## Integration Points

The BiDAF system integrates with several external tools and frameworks:

- **TensorFlow**: Core deep learning framework (r0.11 compatibility)
- **SQuAD Evaluation**: Official evaluation script at [squad/evaluate-v1.1.py]()
- **GloVe**: Pre-trained word embeddings for initialization
- **NLTK**: Natural language processing utilities

For advanced usage including ensemble methods and custom model variants, refer to the specialized documentation sections covering those topics.

Sources: [README.md:8-17](), [basic/model.py:1-13]()

---

