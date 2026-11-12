<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/thunnini · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/builders.py](src/builders.py)

</details>



This document provides an overview of the core system components in Thunnini and how they interact to enable fine-tuning research. Thunnini is designed as a modular experimentation library where components can be configured, combined, and extended to study different aspects of neural sequence prediction and fine-tuning methods.

For specific implementation details of individual components, see the relevant subsection pages: [Configuration System](#2.1), [Component Factory](#2.2), [Data Generation](#2.3), [Model Architecture](#2.4), [Training and Tuning](#2.5), and [Evaluation and Visualization](#2.6).

## Overall System Overview

Thunnini's architecture follows a layered design where high-level interfaces orchestrate lower-level components through a configuration-driven factory pattern. The system enables researchers to experiment with 9 different fine-tuning methods across multiple neural architectures and synthetic data distributions.

### Core System Components

```mermaid
graph TB
    subgraph "User Interface Layer"
        ThunniniDemo["ThunniniDemo.ipynb"]
        ThunniniExperiment["ThunniniExperiment.ipynb"] 
    end
    
    subgraph "Configuration Layer"
        config_py["config.py"]
        types_py["types.py"]
    end
    
    subgraph "Factory Layer"  
        builders_py["builders.py"]
    end
    
    subgraph "Core Components"
        subgraph "Data System"
            data_generator_base_py["data_generator_base.py"]
            data_generators_py["data_generators.py"]
        end
        
        subgraph "Model System"
            predictor_py["predictor.py"]
            predictor_torsos_py["predictor_torsos.py"]
            transformer_utils_py["transformer_utils.py"]
        end
        
        subgraph "Training System"
            training_py["training.py"]
            tuning_py["tuning.py"] 
            predictor_tuning_functions_py["predictor_tuning_functions.py"]
        end
        
        subgraph "Evaluation System"
            evaluation_py["evaluation.py"]
            plot_utils_py["plot_utils.py"]
        end
    end
    
    ThunniniDemo --> builders_py
    ThunniniExperiment --> builders_py
    config_py --> builders_py
    types_py --> config_py
    
    builders_py --> data_generators_py
    builders_py --> predictor_py
    
    data_generator_base_py --> data_generators_py
    predictor_torsos_py --> predictor_py
    transformer_utils_py --> predictor_torsos_py
    
    training_py --> predictor_py
    training_py --> data_generators_py
    tuning_py --> predictor_tuning_functions_py
    tuning_py --> predictor_py
    
    evaluation_py --> predictor_py
    evaluation_py --> data_generators_py
    plot_utils_py --> evaluation_py
```

*Sources: [README.md:1-354](), [src/builders.py:1-101]()*

The system is organized into several distinct layers:

| Layer | Purpose | Key Components |
|-------|---------|----------------|
| **User Interface** | Entry points for experiments | `ThunniniDemo.ipynb`, `ThunniniExperiment.ipynb` |
| **Configuration** | Type-safe parameter specification | `config.py`, `types.py` |
| **Factory** | Component instantiation from configs | `builders.py` |
| **Data System** | Synthetic data generation | `data_generator_base.py`, `data_generators.py` |
| **Model System** | Neural architectures and prediction | `predictor.py`, `predictor_torsos.py` |
| **Training System** | Pretraining and fine-tuning loops | `training.py`, `tuning.py` |
| **Evaluation System** | Performance assessment and visualization | `evaluation.py`, `plot_utils.py` |

## Component Factory Pattern

Thunnini uses a centralized factory pattern implemented in `builders.py` to instantiate components from configurations. This design ensures type safety and extensibility while maintaining a clean separation between configuration and implementation.

### Factory Architecture

```mermaid
graph TD
    subgraph "Configuration Classes"
        DataGeneratorConfig["DataGeneratorConfig"]
        PredictorConfig["PredictorConfig"] 
        PredictorTorsoConfig["PredictorTorsoConfig"]
    end
    
    subgraph "Factory Functions"
        build_datagen["build_datagen()"]
        build_predictor["build_predictor()"]
        get_torso_builder["get_torso_builder()"]
    end
    
    subgraph "Registry Mappings"
        ALL_DATAGENS["ALL_DATAGENS"]
        ALL_TORSOS["ALL_TORSOS"]
        ALL_DATAGEN_CONFIGS["ALL_DATAGEN_CONFIGS"]
        ALL_TORSO_CONFIGS["ALL_TORSO_CONFIGS"]
    end
    
    subgraph "Concrete Components"
        DataGenerator["DataGenerator instances"]
        Predictor["Predictor instances"]
        PredictorTorso["PredictorTorso instances"]
    end
    
    DataGeneratorConfig --> build_datagen
    PredictorConfig --> build_predictor
    PredictorTorsoConfig --> get_torso_builder
    
    build_datagen --> ALL_DATAGENS
    build_predictor --> ALL_TORSOS
    get_torso_builder --> ALL_TORSOS
    
    ALL_DATAGENS --> DataGenerator
    ALL_TORSOS --> PredictorTorso
    build_predictor --> Predictor
```

*Sources: [src/builders.py:29-101]()*

The factory maintains four key registries that map string identifiers to component classes:

- `ALL_DATAGENS`: Maps data generator type names to implementation classes
- `ALL_TORSOS`: Maps neural architecture type names to torso classes  
- `ALL_DATAGEN_CONFIGS`: Maps generator types to their configuration classes
- `ALL_TORSO_CONFIGS`: Maps torso types to their configuration classes

## Fine-Tuning Methods Architecture

Thunnini implements 9 fine-tuning methods organized into three categories. The system is designed so that all methods work uniformly across different neural architectures through the `Predictor` wrapper class.

### Tuning Method Taxonomy

```mermaid
graph TD
    subgraph "Fine-Tuning Categories"
        PrefixTuning["Prefix Tuning<br/>(4 methods)"]
        WeightTuning["Weight Tuning<br/>(4 methods)"]
        AdditionalWeights["Additional Weights<br/>(1 method)"]
    end
    
    subgraph "Prefix Methods"
        HardPrefix["Hard Prefix<br/>Exhaustive search"]
        SimplexPrefix["Simplex Prefix<br/>Probability simplex"]
        RealPrefix["Real Prefix<br/>Unconstrained real"]
        SoftPrefix["Soft Prefix<br/>Embedding space"]
    end
    
    subgraph "Weight Methods"
        FullWeights["Full Weights<br/>All parameters"]
        Embedding["Embedding<br/>Input layer only"]
        Unembedding["Unembedding<br/>Output layer only"]
        UnEmbedding["Un+Embedding<br/>Input + Output"]
    end
    
    subgraph "Additional Weight Methods"
        LoRA["LoRA<br/>Low-rank adaptation"]
    end
    
    subgraph "Supported Architectures"
        LSTM["LSTMPredictorTorso"]
        Transformer["TransformerPredictorTorso"]
        Linear["LinearPredictorTorso"]
    end
    
    PrefixTuning --> HardPrefix
    PrefixTuning --> SimplexPrefix
    PrefixTuning --> RealPrefix
    PrefixTuning --> SoftPrefix
    
    WeightTuning --> FullWeights
    WeightTuning --> Embedding
    WeightTuning --> Unembedding
    WeightTuning --> UnEmbedding
    
    AdditionalWeights --> LoRA
    
    HardPrefix -.-> LSTM
    SimplexPrefix -.-> LSTM
    RealPrefix -.-> LSTM
    SoftPrefix -.-> LSTM
    
    HardPrefix -.-> Transformer
    SimplexPrefix -.-> Transformer
    RealPrefix -.-> Transformer
    SoftPrefix -.-> Transformer
    
    FullWeights -.-> LSTM
    Embedding -.-> LSTM
    Unembedding -.-> LSTM
    UnEmbedding -.-> LSTM
    
    FullWeights -.-> Transformer
    Embedding -.-> Transformer
    Unembedding -.-> Transformer
    UnEmbedding -.-> Transformer
    
    LoRA -.-> Transformer
```

*Sources: [README.md:152-182](), [src/predictor_tuning_functions.py]()*

## Data Flow Architecture

The experimental workflow in Thunnini follows a clear data flow from configuration through training to evaluation. Each stage transforms data and parameters while maintaining provenance and reproducibility.

### Experimental Data Flow

```mermaid
graph LR
    subgraph "Configuration Stage"
        DataGenConfig["DataGeneratorConfig"]
        PredictorConfig["PredictorConfig"]
        TrainingConfig["TrainingConfig"]
        TuningConfig["TuningConfig"]
    end
    
    subgraph "Building Stage"
        build_datagen_func["build_datagen()"]
        build_predictor_func["build_predictor()"]
        DataGenerator["DataGenerator"]
        Predictor["Predictor"]
    end
    
    subgraph "Training Stage"
        train_func["training.train()"]
        TrainedParams["Trained Parameters"]
    end
    
    subgraph "Tuning Stage"
        tune_func["tuning.tune()"]
        TuningMethods["Tuning Methods"]
        TunedModels["Tuned Models"]
    end
    
    subgraph "Evaluation Stage"
        evaluate_func["evaluation.evaluate()"]
        Baselines["Baselines<br/>(Oracle, Bayes, Untrained)"]
        Metrics["Performance Metrics"]
    end
    
    subgraph "Analysis Stage"
        plot_utils_func["plot_utils functions"]
        Results["Experimental Results"]
    end
    
    DataGenConfig --> build_datagen_func
    PredictorConfig --> build_predictor_func
    
    build_datagen_func --> DataGenerator
    build_predictor_func --> Predictor
    
    DataGenerator --> train_func
    Predictor --> train_func
    TrainingConfig --> train_func
    train_func --> TrainedParams
    
    TrainedParams --> tune_func
    TuningConfig --> tune_func
    TuningMethods --> tune_func
    DataGenerator --> tune_func
    tune_func --> TunedModels
    
    TunedModels --> evaluate_func
    Baselines --> evaluate_func
    DataGenerator --> evaluate_func
    evaluate_func --> Metrics
    
    Metrics --> plot_utils_func
    plot_utils_func --> Results
```

*Sources: [README.md:21-31](), [src/training.py](), [src/tuning.py](), [src/evaluation.py]()*

## Key System Abstractions

Thunnini's architecture is built around several key abstractions that enable modularity and extensibility:

### Core Abstract Interfaces

| Interface | Purpose | Key Methods | Implementations |
|-----------|---------|-------------|-----------------|
| `DataGenerator` | Defines data generation protocol | `sample()`, `log_prob()`, `bayesian_update()` | `CategoricalGenerator`, `MixtureOfCategoricalsGenerator`, `DirichletCategoricalGenerator` |
| `PredictorTorso` | Defines neural architecture interface | `__call__()`, `init()` | `LSTMPredictorTorso`, `TransformerPredictorTorso`, `LinearPredictorTorso` |
| `Predictor` | Unified prediction interface | `forward()`, `loss()`, `update()` | Single implementation wrapping torsos |

### Configuration Hierarchy

```mermaid
graph TD
    subgraph "Base Configuration"
        Config["@dataclass Config"]
    end
    
    subgraph "Data Configuration"
        DataGeneratorConfig_class["DataGeneratorConfig"]
        CategoricalGeneratorConfig["CategoricalGeneratorConfig"]
        MixtureConfig["MixtureOfCategoricalsGeneratorConfig"] 
        DirichletConfig["DirichletCategoricalGeneratorConfig"]
    end
    
    subgraph "Model Configuration"
        PredictorConfig_class["PredictorConfig"]
        PredictorTorsoConfig_class["PredictorTorsoConfig"]
        LinearTorsoConfig["LinearTorsoConfig"]
        LSTMTorsoConfig["LSTMTorsoConfig"]
        TransformerTorsoConfig["TransformerTorsoConfig"]
    end
    
    subgraph "Training Configuration"
        TrainingConfig_class["TrainingConfig"]
        TuningConfig_class["TuningConfig"]
    end
    
    Config --> DataGeneratorConfig_class
    Config --> PredictorConfig_class
    Config --> TrainingConfig_class
    
    DataGeneratorConfig_class --> CategoricalGeneratorConfig
    DataGeneratorConfig_class --> MixtureConfig
    DataGeneratorConfig_class --> DirichletConfig
    
    PredictorConfig_class --> PredictorTorsoConfig_class
    PredictorTorsoConfig_class --> LinearTorsoConfig
    PredictorTorsoConfig_class --> LSTMTorsoConfig
    PredictorTorsoConfig_class --> TransformerTorsoConfig
    
    TrainingConfig_class --> TuningConfig_class
```

*Sources: [src/config.py](), [src/types.py]()*

The configuration system uses Python dataclasses with type annotations to provide compile-time safety and runtime validation. All configurations inherit from a base `Config` class and are organized hierarchically to reflect the system's component structure.

This architecture enables Thunnini to be both easy to use for standard experiments and highly extensible for research into new fine-tuning methods, neural architectures, and data distributions.

---

