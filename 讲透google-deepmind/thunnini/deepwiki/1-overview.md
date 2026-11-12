<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/thunnini · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document introduces the Thunnini repository, a research library designed for studying fine-tuning methods for neural sequence predictors. Thunnini enables systematic experimentation with nine different tuning methods across LSTM and Transformer architectures using synthetic data distributions where optimal baselines are analytically tractable.

For step-by-step usage instructions, see [Quick Start Guide](#1.1) and [Running Experiments](#1.2). For detailed architecture documentation, see [System Architecture](#2).

## Purpose and Scope

Thunnini is an experimentation library focused on understanding fundamental aspects of fine-tuning methods for neural sequence predictors. The library provides a controlled environment for studying conceptual questions about prompt tuning, parameter-efficient fine-tuning, and their connections to meta-learning and Bayesian inference.

**Core capabilities:**
- **Pretraining**: Neural sequence predictors via log loss minimization on synthetic data
- **Fine-tuning**: Nine different tuning methods including prefix tuning, weight tuning, and LoRA
- **Evaluation**: Performance assessment against optimal oracle and Bayesian baselines  
- **Comparison**: Systematic comparison across architectures and tuning methods

**Scope limitations:**
- Designed for single-GPU experiments completing within minutes
- Uses synthetic data distributions with tractable optimal predictors
- Focuses on sequence prediction rather than LLM-scale language modeling

Sources: [README.md:11-54]()

## System Architecture

The Thunnini system follows a modular architecture with clear separation between configuration, data generation, model definition, training, and evaluation components.

### Core Component Overview

```mermaid
graph TB
    subgraph "Entry_Points"
        demo["ThunniniDemo.ipynb"]
        experiment["ThunniniExperiment.ipynb"]
    end
    
    subgraph "Configuration_Layer"
        config["config.py<br/>ConfigClasses"]
        types["types.py<br/>TypeDefinitions"]
    end
    
    subgraph "Factory_System"
        builders["builders.py<br/>ComponentFactory"]
    end
    
    subgraph "Data_System"
        data_base["data_generator_base.py<br/>DataGeneratorBase"]
        data_impl["data_generators.py<br/>CategoricalDataGenerator<br/>MixtureDataGenerator<br/>DirichletDataGenerator"]
    end
    
    subgraph "Model_System"
        predictor["predictor.py<br/>Predictor"]
        torsos["predictor_torsos.py<br/>LSTMPredictorTorso<br/>TransformerPredictorTorso"]
        transformer_utils["transformer_utils.py<br/>TransformerComponents"]
    end
    
    subgraph "Training_System"
        training["training.py<br/>train()"]
        tuning["tuning.py<br/>tune()"]
        tuning_funcs["predictor_tuning_functions.py<br/>TuningFunctions"]
    end
    
    subgraph "Evaluation_System"
        evaluation["evaluation.py<br/>evaluate()"]
        plot_utils["plot_utils.py<br/>PlotFunctions"]
    end
    
    demo --> builders
    experiment --> builders
    config --> builders
    types --> config
    
    builders --> data_impl
    builders --> predictor
    data_impl --> data_base
    
    predictor --> torsos
    torsos --> transformer_utils
    
    training --> predictor
    training --> data_impl
    tuning --> tuning_funcs
    tuning --> predictor
    
    evaluation --> predictor
    evaluation --> data_impl
    plot_utils --> evaluation
```

Sources: [README.md:215-247](), [src/builders.py](), [src/config.py](), [src/types.py]()

### Fine-Tuning Method Taxonomy

Thunnini implements nine fine-tuning methods organized into three categories, each targeting different aspects of the neural predictor.

```mermaid
graph TD
    subgraph "Prefix_Tuning_Methods"
        hard_prefix["HardPrefix<br/>Discrete token search"]
        simplex_prefix["SimplexPrefix<br/>Probability simplex"]
        real_prefix["RealPrefix<br/>Unconstrained real"]
        soft_prefix["SoftPrefix<br/>Embedding space"]
    end
    
    subgraph "Weight_Tuning_Methods"
        full_weights["FullWeights<br/>All parameters"]
        embedding["Embedding<br/>Input layer only"]
        unembedding["Unembedding<br/>Output layer only"]
        both_embedding["BothEmbedding<br/>Input + Output layers"]
    end
    
    subgraph "Additional_Weight_Methods"
        lora["LoRA<br/>Low-rank adaptation"]
    end
    
    subgraph "Neural_Architectures"
        lstm["LSTMPredictorTorso"]
        transformer["TransformerPredictorTorso"]
    end
    
    subgraph "Tuning_Implementation"
        tuning_functions["predictor_tuning_functions.py"]
        tune_loop["tuning.py"]
    end
    
    lstm -.-> Prefix_Tuning_Methods
    transformer -.-> Prefix_Tuning_Methods
    lstm -.-> Weight_Tuning_Methods
    transformer -.-> Weight_Tuning_Methods
    transformer -.-> lora
    
    tuning_functions --> tune_loop
    Prefix_Tuning_Methods --> tuning_functions
    Weight_Tuning_Methods --> tuning_functions
    Additional_Weight_Methods --> tuning_functions
```

Sources: [README.md:152-182](), [src/predictor_tuning_functions.py](), [src/tuning.py](), [src/predictor_torsos.py]()

## Data Generation System

Thunnini provides three categories of synthetic data generators that enable controlled experimentation with known optimal baselines.

| Generator Type | Description | Use Case | Optimal Baseline |
|---|---|---|---|
| `CategoricalDataGenerator` | Fixed categorical distribution | Simple prediction tasks | Oracle predictor |
| `MixtureDataGenerator` | Mixture of categoricals | Multi-modal distributions | Mixture oracle |
| `DirichletDataGenerator` | Dirichlet-categorical conjugate | Bayesian learning scenarios | Beta-binomial predictor |

Each data generator implements the `DataGeneratorBase` interface and provides:
- Sample generation with ground-truth probabilities
- Bayesian predictor computation for optimal baselines
- Configuration through dataclass specifications

Sources: [README.md:192-207](), [src/data_generator_base.py](), [src/data_generators.py]()

## Experimental Workflow

The typical Thunnini workflow progresses through four main phases, coordinated by the configuration system and component factories.

```mermaid
graph LR
    subgraph "Configuration_Phase"
        data_config["DataGeneratorConfig"]
        predictor_config["PredictorConfig"] 
        training_config["TrainingConfig"]
        tuning_config["TuningConfig"]
    end
    
    subgraph "Building_Phase"
        build_data["builders.build_data_generator()"]
        build_predictor["builders.build_predictor()"]
    end
    
    subgraph "Training_Phase"
        pretrain["training.train()"]
        trained_params["TrainedParameters"]
    end
    
    subgraph "Tuning_Phase"
        tune_methods["9 TuningMethods"]
        tune_loop["tuning.tune()"]
        tuned_models["TunedModels"]
    end
    
    subgraph "Evaluation_Phase"
        evaluate["evaluation.evaluate()"]
        baselines["OracleBaselines"]
        metrics["PerformanceMetrics"]
        plots["plot_utils.plot_results()"]
    end
    
    data_config --> build_data
    predictor_config --> build_predictor
    
    build_data --> pretrain
    build_predictor --> pretrain
    training_config --> pretrain
    pretrain --> trained_params
    
    trained_params --> tune_loop
    tune_methods --> tune_loop
    tuning_config --> tune_loop
    tune_loop --> tuned_models
    
    tuned_models --> evaluate
    baselines --> evaluate
    evaluate --> metrics
    metrics --> plots
```

Sources: [README.md:19-42](), [src/training.py](), [src/tuning.py](), [src/evaluation.py](), [src/plot_utils.py]()

## Key Design Principles

**Configuration-Driven**: All experiments are specified through dataclass configurations in [src/config.py](), ensuring reproducibility and systematic parameter exploration.

**Modular Architecture**: Clear separation between data generation, model definition, training, and evaluation enables independent extension of each component.

**Baseline Integration**: Built-in computation of optimal oracle and Bayesian predictors provides rigorous performance baselines for evaluating fine-tuning methods.

**Extensibility**: New neural architectures can be added as `PredictorTorso` implementations, and new data generators through the `DataGeneratorBase` interface.

The library targets researchers studying fundamental questions about fine-tuning rather than practitioners working with large-scale language models. For implementation details of specific components, see [System Architecture](#2).

Sources: [README.md:32-54](), [README.md:249-276]()

---

