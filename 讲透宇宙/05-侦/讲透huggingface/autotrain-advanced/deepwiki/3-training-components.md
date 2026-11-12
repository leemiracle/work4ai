<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/autotrain-advanced · page 3 Training Components · fetched 2026-10-26 -->

# Training Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [requirements.txt](requirements.txt)
- [src/autotrain/__init__.py](src/autotrain/__init__.py)
- [src/autotrain/trainers/clm/__main__.py](src/autotrain/trainers/clm/__main__.py)
- [src/autotrain/trainers/clm/utils.py](src/autotrain/trainers/clm/utils.py)
- [src/autotrain/trainers/common.py](src/autotrain/trainers/common.py)
- [src/autotrain/trainers/image_classification/__main__.py](src/autotrain/trainers/image_classification/__main__.py)
- [src/autotrain/trainers/seq2seq/__main__.py](src/autotrain/trainers/seq2seq/__main__.py)
- [src/autotrain/trainers/tabular/__main__.py](src/autotrain/trainers/tabular/__main__.py)
- [src/autotrain/trainers/text_classification/__main__.py](src/autotrain/trainers/text_classification/__main__.py)

</details>



This page provides an overview of the various model training capabilities within AutoTrain Advanced. It covers the core training components that enable users to fine-tune different types of machine learning models through a unified interface.

AutoTrain Advanced supports training a variety of model types, each with specialized training workflows and parameters. For information about how these components are orchestrated, see [Project Management](#2.1). For details on data processing before training, see [Data Processing](#2.2).

## Overview of Training Components

AutoTrain Advanced provides specialized training components for different AI tasks, each implemented as a separate module within the codebase. These components handle the specific requirements and optimizations needed for their respective model types.

**Training Component Types Diagram**

```mermaid
graph TD
    User["User"]
    subgraph "AutoTrain Components"
        direction LR
        Project["AutoTrainProject"]
        Project --> Params["TrainingParameters"]
        Params --> |creates| TrainingConfig["Training Configuration"]
        
        TrainingConfig --> |dispatches to| Trainers["Training Components"]
        
        subgraph "Trainers"
            LLM["LLM Trainer<br>- SFT<br>- DPO<br>- ORPO<br>- Reward"]
            TextClass["Text Classification<br>Trainer"]
            ImgClass["Image Classification<br>Trainer"] 
            Seq2Seq["Sequence-to-Sequence<br>Trainer"]
            Tabular["Tabular<br>Trainer"]
            TokenClass["Token Classification<br>Trainer"]
        end
    end
    
    User --> |configures| Project
    Trainers --> |produce| Models["Trained Models"]
```

Sources: [src/autotrain/trainers/clm/__main__.py:15-46](), [src/autotrain/trainers/text_classification/__main__.py:40-239](), [src/autotrain/trainers/image_classification/__main__.py:39-242](), [src/autotrain/trainers/seq2seq/__main__.py:45-272](), [src/autotrain/trainers/tabular/__main__.py:152-402]()

## Common Architecture

All training components share a common architecture pattern that provides consistency across different model types. This includes parameter validation, training monitoring, checkpointing, and integration with Hugging Face Hub.

**Common Training Architecture Diagram**

```mermaid
graph TB
    subgraph "Training Component Common Architecture"
        ConfigParser["Parse Config JSON"] --> |creates| Params["AutoTrainParams"]
        Params --> ValidateParams["Validate Parameters"]
        ValidateParams --> LoadData["Load Dataset"]
        LoadData --> PrepareModel["Initialize Model"]
        PrepareModel --> TrainingLoop["Run Training Loop"]
        TrainingLoop --> SaveModel["Save Model"]
        SaveModel --> CreateModelCard["Create Model Card"]
        CreateModelCard --> |if push_to_hub| PushModel["Push to Hub"]
    end
    
    subgraph "Common Callbacks"
        LoggingCallback["LossLoggingCallback"]
        StartCallback["TrainStartCallback"]
        UploadCallback["UploadLogs"]
    end
    
    TrainingLoop --> |registers| CommonCallbacks["Common Callbacks"]
    CommonCallbacks --- LoggingCallback
    CommonCallbacks --- StartCallback
    CommonCallbacks --- UploadCallback
```

Sources: [src/autotrain/trainers/common.py:189-220](), [src/autotrain/trainers/common.py:223-286](), [src/autotrain/trainers/common.py:289-340]()

The base parameters class, `AutoTrainParams`, provides common functionality for parameter validation and serialization. It ensures that configuration parameters are properly validated before training begins.

```mermaid
classDiagram
    class AutoTrainParams {
        +save(output_dir)
        +__str__()
        +validate_project_name()
    }
    
    class LLMTrainingParams {
        +model: str
        +data_path: str
        +trainer: str
        +peft: bool
        +quantization: str
        +...
    }
    
    class TextClassificationParams {
        +model: str
        +data_path: str
        +text_column: str
        +target_column: str
        +...
    }
    
    class ImageClassificationParams {
        +model: str
        +data_path: str
        +image_column: str
        +target_column: str
        +...
    }
    
    class Seq2SeqParams {
        +model: str
        +data_path: str
        +text_column: str
        +target_column: str
        +...
    }
    
    class TabularParams {
        +model: str
        +data_path: str
        +target_columns: list
        +numerical_columns: list
        +categorical_columns: list
        +...
    }
    
    AutoTrainParams <|-- LLMTrainingParams
    AutoTrainParams <|-- TextClassificationParams
    AutoTrainParams <|-- ImageClassificationParams
    AutoTrainParams <|-- Seq2SeqParams
    AutoTrainParams <|-- TabularParams
```

Sources: [src/autotrain/trainers/common.py:223-286]()

## LLM Training

The LLM training component is the most feature-rich in AutoTrain, supporting various fine-tuning techniques for large language models.

**LLM Training Techniques Diagram**

```mermaid
graph TD
    LLMConfig["LLM Training Configuration"] --> Trainer["Trainer Selection"]
    
    Trainer --> |"trainer=default"| DefaultSFT["Default SFT Trainer"]
    Trainer --> |"trainer=sft"| SFT["SFT Trainer"]
    Trainer --> |"trainer=reward"| Reward["Reward Model Trainer"]
    Trainer --> |"trainer=dpo"| DPO["DPO Trainer"]
    Trainer --> |"trainer=orpo"| ORPO["ORPO Trainer"]
    
    subgraph "Common Features"
        PEFT["PEFT (LoRA)"]
        Quantization["Quantization (Int4/Int8)"]
        FlashAttention["Flash Attention 2"]
        UnslothLib["Unsloth Integration"]
    end
    
    DefaultSFT --> |configures| CommonFeatures["Common Features"]
    SFT --> |configures| CommonFeatures
    
    CommonFeatures --- PEFT
    CommonFeatures --- Quantization
    CommonFeatures --- FlashAttention
    CommonFeatures --- UnslothLib
```

Sources: [src/autotrain/trainers/clm/__main__.py:15-46](), [src/autotrain/trainers/clm/utils.py:32-106](), [src/autotrain/trainers/clm/utils.py:392-462]()

### LLM Training Data Flow

The LLM training component supports sophisticated data processing and training workflows:

```mermaid
flowchart TD
    Dataset["Input Dataset"] --> |load| DataProcessor["Data Processor"]
    DataProcessor --> |apply| ChatTemplates["Chat Templates"]
    ChatTemplates --> |produce| TokenizedData["Tokenized Data"]
    
    BaseModel["Base LLM"] --> |load| ModelInitializer["Model Initializer"]
    
    ConfigParser["Configuration"] --> |configure| Optimizations["Optimizations"]
    Optimizations --> |apply| ModelInitializer
    
    subgraph "Optional Optimizations"
        PEFT["PEFT/LoRA"]
        Quant["Quantization"]
        Flash["Flash Attention"]
    end
    
    Optimizations --- PEFT
    Optimizations --- Quant
    Optimizations --- Flash
    
    TokenizedData --> |feed| TrainingLoop["Training Loop"]
    ModelInitializer --> |initialize| TrainingLoop
    
    TrainingLoop --> |produce| TrainedModel["Trained Model"]
    
    TrainedModel --> |if PEFT| MergeAdapter["Merge Adapter"]
    MergeAdapter --> FinalModel["Final Model"]
    
    TrainedModel --> |if !PEFT| FinalModel
    
    FinalModel --> |save| SavedModel["Saved Model"]
    SavedModel --> |if push_to_hub| HFHub["Hugging Face Hub"]
```

Sources: [src/autotrain/trainers/clm/utils.py:392-462](), [src/autotrain/trainers/clm/utils.py:465-553](), [src/autotrain/trainers/clm/utils.py:828-1196]()

## Text Classification Training

The text classification training component supports binary and multi-class classification tasks for text data.

```mermaid
flowchart TD
    TextData["Text Dataset"] --> TextProcessor["Text Processor"]
    TextProcessor --> TokenizedText["Tokenized Text"]
    
    ModelConfig["Classification Model Config"] --> |"num_labels=classes"| ModelInit["Model Initialization"]
    
    TokenizedText --> TrainingLoop["Training Loop"]
    ModelInit --> TrainingLoop
    
    MetricSelector["Metric Selector"]
    MetricSelector --> |"if binary"| BinaryMetrics["Binary Classification Metrics"]
    MetricSelector --> |"if multi-class"| MultiMetrics["Multi-class Classification Metrics"]
    
    TrainingLoop --> |track| SelectedMetrics["Selected Metrics"]
    SelectedMetrics --> |"if validation"| EarlyStopping["Early Stopping"]
    
    TrainingLoop --> SavedModel["Saved Model"]
    SavedModel --> ModelCard["Model Card"]
    ModelCard --> |"if push_to_hub"| HFHub["Hugging Face Hub"]
```

Sources: [src/autotrain/trainers/text_classification/__main__.py:40-239]()

## Image Classification Training

The image classification component follows a similar pattern to text classification but with image-specific processing:

```mermaid
flowchart TD
    ImageData["Image Dataset"] --> ImageProcessor["Image Processor"]
    ImageProcessor --> ProcessedImages["Processed Images"]
    
    ModelConfig["Classification Model Config"] --> |"num_labels=classes"| ModelInit["Model Initialization"]
    
    ProcessedImages --> TrainingLoop["Training Loop"]
    ModelInit --> TrainingLoop
    
    MetricSelector["Metric Selector"]
    MetricSelector --> |"if binary"| BinaryMetrics["Binary Classification Metrics"]
    MetricSelector --> |"if multi-class"| MultiMetrics["Multi-class Classification Metrics"]
    
    TrainingLoop --> |track| SelectedMetrics["Selected Metrics"]
    SelectedMetrics --> |"if validation"| EarlyStopping["Early Stopping"]
    
    TrainingLoop --> SavedModel["Saved Model"]
    SavedModel --> ModelCard["Model Card"]
    ModelCard --> |"if push_to_hub"| HFHub["Hugging Face Hub"]
```

Sources: [src/autotrain/trainers/image_classification/__main__.py:39-242]()

## Sequence-to-Sequence Training

The sequence-to-sequence component handles tasks like translation, summarization, and other text generation tasks:

```mermaid
flowchart TD
    TextInput["Source Text"] --> Tokenizer["Tokenizer"]
    Tokenizer --> EncodedInput["Encoded Input"]
    
    TargetText["Target Text"] --> Tokenizer
    Tokenizer --> EncodedTarget["Encoded Target"]
    
    ModelConfig["Seq2Seq Model Config"] --> ModelInit["Model Initialization"]
    
    EncodedInput --> DataCollator["Seq2Seq Data Collator"]
    EncodedTarget --> DataCollator
    
    DataCollator --> TrainingLoop["Training Loop"]
    ModelInit --> TrainingLoop
    
    TrainingLoop --> |"predict_with_generate=True"| GeneratedText["Generated Text"]
    GeneratedText --> Metrics["Seq2Seq Metrics"]
    
    TrainingLoop --> SavedModel["Saved Model"]
    SavedModel --> ModelCard["Model Card"]
    ModelCard --> |"if push_to_hub"| HFHub["Hugging Face Hub"]
```

Sources: [src/autotrain/trainers/seq2seq/__main__.py:45-272]()

## Tabular Training

The tabular training component handles structured data with support for various classic machine learning models:

```mermaid
flowchart TD
    TabularData["Tabular Dataset"] --> ColumnDetector["Column Type Detector"]
    
    ColumnDetector --> NumCols["Numerical Columns"]
    ColumnDetector --> CatCols["Categorical Columns"]
    
    NumCols --> NumPreprocessor["Numerical Preprocessor"]
    CatCols --> CatPreprocessor["Categorical Preprocessor"]
    
    NumPreprocessor --> Preprocessor["Column Transformer"]
    CatPreprocessor --> Preprocessor
    
    TaskDetector["Task Detector"]
    TaskDetector --> |"if binary target"| BinaryTask["Binary Classification"]
    TaskDetector --> |"if multi-class target"| MultiTask["Multi-class Classification"]
    TaskDetector --> |"if continuous target"| RegressionTask["Regression"]
    
    Preprocessor --> ProcessedData["Processed Data"]
    ProcessedData --> HPOOptimizer["Hyperparameter Optimizer (Optuna)"]
    
    ModelSelector["Model Selector"]
    ModelSelector --> |"model=xgboost"| XGBoost["XGBoost"]
    ModelSelector --> |"model=lightgbm"| LightGBM["LightGBM"]
    ModelSelector --> |"model=randomforest"| RF["Random Forest"]
    ModelSelector --> |"model=catboost"| CatBoost["CatBoost"]
    ModelSelector --> |"model=extratrees"| ExtraTrees["Extra Trees"]
    
    HPOOptimizer --> |configures| SelectedModel["Selected Model"]
    
    ProcessedData --> |train| SelectedModel
    SelectedModel --> SavedModel["Saved Model"]
    SavedModel --> ModelCard["Model Card"]
    ModelCard --> |"if push_to_hub"| HFHub["Hugging Face Hub"]
```

Sources: [src/autotrain/trainers/tabular/__main__.py:152-402](), [src/autotrain/trainers/tabular/__main__.py:34-150]()

## Common Training Workflow

Despite the differences between training components, they all follow a similar high-level workflow:

```mermaid
sequenceDiagram
    participant User
    participant AutoTrain
    participant Dataset
    participant ModelHub
    participant TrainingComponent
    participant TrainingBackend
    
    User->>AutoTrain: Configure Training Parameters
    AutoTrain->>+Dataset: Load Data
    Dataset-->>-AutoTrain: Return Dataset
    
    AutoTrain->>+ModelHub: Load Base Model
    ModelHub-->>-AutoTrain: Return Model
    
    AutoTrain->>TrainingComponent: Create Training Job
    
    TrainingComponent->>TrainingBackend: Execute Training
    
    loop Training Process
        TrainingBackend->>TrainingBackend: Process Batch
        TrainingBackend->>AutoTrain: Report Progress
        AutoTrain->>User: Update UI/Logs
    end
    
    TrainingBackend-->>TrainingComponent: Return Trained Model
    TrainingComponent->>AutoTrain: Save Model
    
    alt Push to Hub
        AutoTrain->>ModelHub: Push Model
        ModelHub-->>User: Model Available on Hub
    end
    
    AutoTrain-->>User: Training Complete
```

Sources: [src/autotrain/trainers/common.py:189-220](), [src/autotrain/trainers/clm/utils.py:392-462]()

## Parameter Management

Each training component has its own parameters class that inherits from `AutoTrainParams`. The following table summarizes the key parameters for each trainer type:

| Trainer Type | Key Parameters | Description |
|-------------|---------------|------------|
| LLM | `model`, `trainer`, `peft`, `quantization`, `chat_template` | Controls LLM fine-tuning with options for PEFT, quantization, and different training methods |
| Text Classification | `model`, `text_column`, `target_column` | Configures text classifier training with column mappings |
| Image Classification | `model`, `image_column`, `target_column` | Sets up image classifier with column mappings |
| Sequence-to-Sequence | `model`, `text_column`, `target_column` | Configures seq2seq models with input/output column mappings |
| Tabular | `model`, `numerical_columns`, `categorical_columns`, `target_columns` | Sets up tabular model training with column type specifications |

Sources: [src/autotrain/trainers/common.py:223-286]()

## Training Component Integration

The training components integrate with the rest of the AutoTrain system through a consistent interface:

```mermaid
graph TB
    User["User"]
    
    subgraph "Interfaces"
        CLI["Command Line Interface"]
        API["Python API"]
        WebUI["Web UI"]
    end
    
    User --> Interfaces
    
    Interfaces --> ConfigGenerator["Config Generator"]
    ConfigGenerator --> |"creates JSON config"| ConfigFile["training_config.json"]
    
    ConfigFile --> TrainingComponents["Training Components"]
    
    subgraph "Training Components"
        LLM["LLM Trainer"]
        TextClass["Text Classification"]
        ImageClass["Image Classification"]
        Seq2Seq["Sequence-to-Sequence"]
        Tabular["Tabular"]
    end
    
    TrainingComponents --> |"selects"| Backend["Execution Backend"]
    
    Backend --> |"execute"| TrainingJob["Training Job"]
    
    TrainingJob --> |"produces"| Model["Trained Model"]
    
    Model --> |"if push_to_hub"| HuggingFaceHub["Hugging Face Hub"]
```

Sources: [src/autotrain/trainers/clm/__main__.py:8-53](), [src/autotrain/trainers/text_classification/__main__.py:32-239](), [src/autotrain/trainers/image_classification/__main__.py:32-242](), [src/autotrain/trainers/seq2seq/__main__.py:38-275](), [src/autotrain/trainers/tabular/__main__.py:26-409]()

For more details on how these components are used in specific training contexts, see [LLM Training](#3.1), [Text Classification and Regression](#3.2), [Vision Models](#3.3), and [Other Training Types](#3.4).

---

