<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/rat-sql · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ratsql/commands/train.py](ratsql/commands/train.py)
- [ratsql/models/spider/spider_enc.py](ratsql/models/spider/spider_enc.py)
- [run.py](run.py)

</details>



This document provides a comprehensive overview of the RAT-SQL system architecture. It covers the high-level structure of the codebase, its main components, and how they interact during the text-to-SQL translation process. For detailed information about the specific model architecture, refer to [Model Architecture](#4). For information about the command-line interface specifically, see [Command-Line Interface](#3.1).

## Overview

RAT-SQL (Relation-Aware Schema Encoding and Linking for Text-to-SQL Parsers) is a neural network-based system designed to translate natural language questions into SQL queries based on database schemas. The system follows a modular architecture with clear separation between preprocessing, training, inference, and evaluation components.

```mermaid
flowchart TB
    subgraph "Core Architecture"
        CLI["Command Line Interface (run.py)"]
        Preproc["Preprocessor"]
        Train["Trainer"]
        Infer["Inference Engine"]
        Eval["Evaluator"]
        
        CLI --> Preproc
        CLI --> Train
        CLI --> Infer
        CLI --> Eval
        
        Preproc --> Train
        Train --> Infer
        Infer --> Eval
    end
    
    subgraph "Model Components"
        Encoder["Encoder (SpiderEncoderV2/SpiderEncoderBert)"]
        Decoder["Decoder (NL2Code)"]
        
        Encoder --> Decoder
    end
    
    subgraph "Data"
        Dataset["Spider/WikiSQL Dataset"]
        Schema["Database Schemas"]
        
        Dataset --> Preproc
        Schema --> Preproc
    end
    
    Train --> Model["Model"]
    Model --> Encoder
    Model --> Decoder
```

Sources: [run.py:1-109](), [README.md:1-109]()

## Key Components

The system is organized into several key components that work together to translate natural language questions into SQL queries:

### Command Line Interface

The command-line interface (`run.py`) serves as the main entry point to the system, providing a unified way to execute preprocessing, training, and evaluation operations.

```mermaid
flowchart LR
    User["User"] --> |"python run.py command experiment_config"| RunPy["run.py"]
    
    RunPy --> |"preprocess"| Preprocess["preprocess.py"]
    RunPy --> |"train"| Train["train.py"]
    RunPy --> |"eval"| Eval["eval.py (calls infer.py)"]
    
    subgraph "Configuration"
        ExpConfig["Experiment Config (.jsonnet)"]
        ModelConfig["Model Config (.jsonnet)"]
        ExpConfig --> |"references"| ModelConfig
    end
    
    ExpConfig --> RunPy
```

Sources: [run.py:1-109](), [README.md:79-93]()

### Encoder-Decoder Architecture

RAT-SQL follows an encoder-decoder architecture:

1. **Encoder**: Processes natural language questions and database schemas, creating a joint representation that captures the relationships between them.
2. **Decoder**: Generates SQL queries based on the encoded representation.

```mermaid
flowchart LR
    subgraph "Input"
        NLQuestion["Natural Language Question"]
        DBSchema["Database Schema (Tables/Columns)"]
    end
    
    subgraph "Encoder"
        QEncoder["Question Encoder"]
        SchemaEncoder["Schema Encoder"]
        RelTransformer["Relation-Aware Transformer"]
        
        QEncoder --> RelTransformer
        SchemaEncoder --> RelTransformer
    end
    
    subgraph "Decoder"
        BeamSearch["Beam Search"]
        Grammar["SQL Grammar"]
        
        BeamSearch --> |"follows"| Grammar
    end
    
    NLQuestion --> QEncoder
    DBSchema --> SchemaEncoder
    RelTransformer --> |"SpiderEncoderState"| BeamSearch
    BeamSearch --> SQLQuery["SQL Query"]
```

The system provides two encoder variants:
- **SpiderEncoderV2**: Uses GloVe embeddings for token representation
- **SpiderEncoderBert**: Uses BERT for token representation

Sources: [ratsql/models/spider/spider_enc.py:264-542](), [ratsql/models/spider/spider_enc.py:751-948]()

## Data Processing Pipeline

RAT-SQL's data processing pipeline transforms raw text questions and database schemas into model-ready inputs.

```mermaid
flowchart TB
    subgraph "Dataset"
        Spider["Spider Dataset"]
        WikiSQL["WikiSQL Dataset"]
    end
    
    subgraph "Preprocessing"
        Tokenize["Tokenization"]
        SchemaPreproc["Schema Preprocessing"]
        Linking["Schema/Value Linking"]
        Vocab["Vocabulary Building"]
        
        Tokenize --> SchemaPreproc
        SchemaPreproc --> Linking
        Linking --> Vocab
    end
    
    subgraph "Data Representation"
        EncoderInput["Encoder Inputs"]
        DecoderInput["Decoder Inputs"]
    end
    
    Spider --> Preprocessing
    WikiSQL --> Preprocessing
    Preprocessing --> EncoderInput
    Preprocessing --> DecoderInput
```

Key preprocessing steps include:
- Tokenization of questions and schema elements
- Schema preprocessing to capture table/column relationships
- Schema linking to identify connections between question tokens and schema elements
- Value linking to match question tokens with database values

Sources: [ratsql/models/spider/spider_enc.py:129-263](), [ratsql/models/spider/spider_enc.py:645-749]()

## Encoder State Representation

The encoder produces a structured state representation that captures the question and schema information along with their relationships.

```mermaid
classDiagram
    class SpiderEncoderState {
        +state
        +memory
        +question_memory
        +schema_memory
        +words
        +pointer_memories
        +pointer_maps
        +m2c_align_mat
        +m2t_align_mat
        +find_word_occurrences()
    }
    
    class PreprocessedSchema {
        +column_names
        +table_names
        +table_bounds
        +column_to_table
        +table_to_columns
        +foreign_keys
        +foreign_keys_tables
        +primary_keys
        +normalized_column_names
        +normalized_table_names
    }
    
    SpiderEncoderState --> PreprocessedSchema : uses
```

The `SpiderEncoderState` is a comprehensive representation that includes:
- Memory tensors for question and schema elements
- Alignment matrices between natural language and schema elements
- Pointer maps for efficient access to columns and tables

Sources: [ratsql/models/spider/spider_enc.py:23-39](), [ratsql/models/spider/spider_enc.py:41-55]()

## Training Process

RAT-SQL's training process orchestrates model training using a comprehensive workflow.

```mermaid
sequenceDiagram
    participant CLI as run.py
    participant Trainer as train.py
    participant Model
    participant Optimizer
    participant DataLoader
    
    CLI->>Trainer: Initialize trainer
    Trainer->>Model: Create model
    Trainer->>Optimizer: Create optimizer
    Trainer->>DataLoader: Create data loaders
    
    loop Training Loop
        DataLoader->>Trainer: Yield batch
        Trainer->>Model: Compute loss
        Model->>Trainer: Return loss
        Trainer->>Optimizer: Update parameters
        
        alt Evaluation Step
            Trainer->>Model: Evaluate on validation data
            Model->>Trainer: Return metrics
            Trainer->>CLI: Log evaluation results
        end
        
        alt Checkpoint Step
            Trainer->>CLI: Save model checkpoint
        end
    end
```

Key components of the training process:
- The `Trainer` class orchestrates the training loop
- Model training is driven by configuration parameters
- Periodic evaluation and checkpointing
- Support for various optimizers and learning rate schedulers

Sources: [ratsql/commands/train.py:78-244]()

## Configuration System

RAT-SQL uses a comprehensive configuration system based on JSONNET files to control all aspects of model training and evaluation.

```mermaid
flowchart TB
    subgraph "Configuration Hierarchy"
        ExpConfig["Experiment Config (e.g., spider-glove-run.jsonnet)"]
        ModelConfig["Model Config (e.g., nl2code-glove.jsonnet)"]
        BaseConfig["Base Config (nl2code-base.libsonnet)"]
        
        ExpConfig --> |"references"| ModelConfig
        ModelConfig --> |"extends"| BaseConfig
    end
    
    subgraph "Configuration Parameters"
        ModelParams["Model Parameters"]
        EncoderParams["Encoder Parameters"]
        DecoderParams["Decoder Parameters"]
        TrainParams["Training Parameters"]
        EvalParams["Evaluation Parameters"]
    end
    
    BaseConfig --> ModelParams
    BaseConfig --> EncoderParams
    BaseConfig --> DecoderParams
    BaseConfig --> TrainParams
    ModelConfig --> EncoderParams
    ExpConfig --> EvalParams
    
    RunPy["run.py"] --> |"loads"| ExpConfig
```

The configuration system provides:
- Hierarchical configuration through JSONNET inheritance
- Different configurations for different experiments
- Separation of model architecture and training parameters
- Runtime parameter overrides via command line

Sources: [run.py:48-106]()

## Class Relationships

This diagram shows key class relationships in the RAT-SQL system:

```mermaid
classDiagram
    class SpiderEncoderV2 {
        +Preproc: SpiderEncoderV2Preproc
        +forward(descs)
        +forward_unbatched(desc)
    }
    
    class SpiderEncoderBert {
        +Preproc: SpiderEncoderBertPreproc
        +forward(descs)
    }
    
    class SpiderEncoderV2Preproc {
        +preprocess_item(item)
        +_preprocess_schema(schema)
        +_tokenize(presplit, unsplit)
    }
    
    class SpiderEncoderBertPreproc {
        +preprocess_item(item)
        +_preprocess_schema(schema)
        +_tokenize(presplit, unsplit)
    }
    
    class Trainer {
        +train(config, modeldir)
        +_eval_model(logger, model, step, data_loader, section)
    }
    
    SpiderEncoderBertPreproc --|> SpiderEncoderV2Preproc: extends
    SpiderEncoderV2 --> SpiderEncoderV2Preproc: uses
    SpiderEncoderBert --> SpiderEncoderBertPreproc: uses
    Trainer --> SpiderEncoderV2: uses
    Trainer --> SpiderEncoderBert: uses
```

Sources: [ratsql/models/spider/spider_enc.py:129-263](), [ratsql/models/spider/spider_enc.py:264-542](), [ratsql/models/spider/spider_enc.py:645-749](), [ratsql/models/spider/spider_enc.py:751-948](), [ratsql/commands/train.py:78-244]()

## Docker Execution Environment

RAT-SQL operates within a containerized Docker environment to ensure consistent execution across different platforms.

```mermaid
flowchart TB
    subgraph "Host System"
        Data["/path/to/data"]
        Codebase["RAT-SQL Codebase"]
    end
    
    subgraph "Docker Container"
        PyTorch["PyTorch 1.5 CUDA 10.1"]
        CoreNLP["Stanford CoreNLP"]
        BERT["BERT Models"]
        
        RunPy["run.py"]
        Commands["Commands Module"]
        Models["Models Module"]
        
        RunPy --> Commands
        Commands --> Models
        
        PyTorch --> Models
        CoreNLP --> Models
        BERT --> Models
    end
    
    Data --> |"mounted as /mnt/data"| Docker["Docker Container"]
    Codebase --> Docker
```

The Docker environment provides:
- All required dependencies (PyTorch, CoreNLP, BERT)
- Consistent execution environment
- Easy volume mounting for datasets
- GPU acceleration support

Sources: [README.md:55-76]()

## Execution Flow

This diagram illustrates the end-to-end execution flow for training and evaluating a model:

```mermaid
flowchart LR
    Setup["Setup Environment"] --> Preproc["Preprocess Data"]
    Preproc --> Train["Train Model"]
    Train --> Eval["Evaluate Model"]
    
    subgraph "Commands"
        direction TB
        Step1["python run.py preprocess config.jsonnet"]
        Step2["python run.py train config.jsonnet"]
        Step3["python run.py eval config.jsonnet"]
    end
    
    Step1 --> Preproc
    Step2 --> Train
    Step3 --> Eval
    
    subgraph "Artifacts"
        ProcessedData["Processed Data"]
        ModelCheckpoints["Model Checkpoints"]
        EvalResults["Evaluation Results"]
    end
    
    Preproc --> ProcessedData
    Train --> ModelCheckpoints
    Eval --> EvalResults
```

Sources: [README.md:79-93](), [run.py:48-106]()

## Summary

The RAT-SQL system architecture provides a flexible and modular approach to text-to-SQL translation. Key features include:

1. **Modular Design**: Clear separation between preprocessing, training, inference, and evaluation components
2. **Dual Encoder Support**: Support for both GloVe and BERT-based encoders
3. **Configuration-Driven**: Extensive use of JSONNET configuration files for experiment customization
4. **Relation-Aware Encoding**: Special handling of relationships between natural language and database schema elements
5. **Containerized Execution**: Docker-based execution environment for portability and reproducibility

This architecture enables RAT-SQL to achieve state-of-the-art performance on text-to-SQL translation tasks while maintaining flexibility for experimentation and extension.

---

