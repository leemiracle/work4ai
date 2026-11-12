<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/eureka-ml-insights · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/eureka-tests.yml](.github/workflows/eureka-tests.yml)
- [README.md](README.md)
- [docs/figures/eureka_logo.png](docs/figures/eureka_logo.png)
- [environment.yml](environment.yml)
- [environment_gpu.yml](environment_gpu.yml)
- [eureka_ml_insights/core/data_processing.py](eureka_ml_insights/core/data_processing.py)
- [eureka_ml_insights/metrics/ifeval_instruction_utils.py](eureka_ml_insights/metrics/ifeval_instruction_utils.py)
- [setup.py](setup.py)
- [tests/component_tests.py](tests/component_tests.py)

</details>



Eureka ML Insights is a comprehensive framework designed for evaluating machine learning models, particularly Large Language Models (LLMs), across various benchmarks in a systematic and reproducible manner. This page provides a high-level understanding of the framework's purpose, architecture, and capabilities.

## Purpose and Scope

Eureka ML Insights helps researchers and practitioners:

- Run reproducible evaluations of generative models using a variety of benchmarks and metrics efficiently
- Define custom pipelines for data processing, inference, and evaluation
- Leverage pre-defined evaluation pipelines for key benchmarks
- Evaluate multimodal models (text, image, vision-language)
- Compare multiple models across standardized tasks

For specific details about the system implementation, see [Architecture](#2).

## Core Architecture

```mermaid
flowchart TD
    subgraph "Pipeline Execution"
        EC["ExperimentConfig"] --> |"configure_pipeline()"| PC["PipelineConfig"]
        PC --> |"contains"| C1["Component 1"]
        C1 --> C2["Component 2"]
        C2 --> C3["Component 3"]
        PC --> |"executed by"| PL["Pipeline.run()"]
    end

    subgraph "Component Types"
        C["Component"] --> DP["DataProcessing"]
        C --> PP["PromptProcessing"]
        C --> INF["Inference"]
        C --> ER["EvalReporting"]
        C --> DJ["DataJoin"]
    end

    C1 -.-> |"is a"| DP
    C2 -.-> |"is a"| PP 
    C3 -.-> |"is a"| INF

    subgraph "Utilities"
        DR["DataReader"]
        DL["DataLoader"] 
        M["Model"]
        MT["Metric"]
        A["Aggregator"]
    end

    DP --> DR
    INF --> DL
    INF --> M
    ER --> MT
    ER --> A
```

Sources: [README.md:96-116](), [eureka_ml_insights/core/data_processing.py:22-75]()

The framework is built around a pipeline-component architecture that allows flexible composition of evaluation workflows. The main execution flow begins with an experiment configuration that defines a pipeline of components, each handling a specific part of the evaluation process.

## Component System

```mermaid
classDiagram
    class Component {
        <<abstract>>
        +from_config(config)
        +run()
    }
    
    class DataProcessing {
        +data_reader
        +output_dir
        +output_data_columns
        +write_output()
        +get_desired_columns()
        +run()
    }
    
    class PromptProcessing {
        +prompt_template_path
        +ignore_failure
        +run()
    }
    
    class Inference {
        +model
        +data_loader
        +resume_from
        +requests_per_minute
        +max_concurrent
        +run()
    }
    
    class EvalReporting {
        +data_reader
        +metric
        +aggregators
        +visualizers
        +run()
    }
    
    class DataJoin {
        +data_reader
        +other_data_reader
        +pandas_merge_args
        +run()
    }
    
    Component <|-- DataProcessing
    DataProcessing <|-- PromptProcessing
    Component <|-- Inference
    Component <|-- EvalReporting
    Component <|-- DataJoin
```

Sources: [tests/component_tests.py:32-267](), [README.md:101-124]()

The component system forms the backbone of the evaluation framework, with each component serving a specific purpose:

- **DataProcessing**: Loads and processes input data
- **PromptProcessing**: Prepares data for model inference, often applying prompt templates
- **Inference**: Runs models on processed data
- **EvalReporting**: Evaluates model outputs and generates reports
- **DataJoin**: Joins data from multiple sources

## Model System

```mermaid
classDiagram
    class Model {
        <<abstract>>
        +generate(text_prompt, *args, **kwargs)
        +count_tokens()
    }

    class EndpointModel {
        <<abstract>>
        +create_request()
        +get_response()
        +handle_request_error()
    }

    class HuggingFaceModel {
        +model_name
        +device
        +get_model()
        +generate()
    }

    class KeyBasedAuthMixIn {
        +get_api_key()
    }

    Model <|-- EndpointModel
    Model <|-- HuggingFaceModel
    
    EndpointModel <|-- AzureOpenAIModel
    EndpointModel <|-- DirectOpenAIModel
    EndpointModel <|-- GeminiModel
    EndpointModel <|-- ClaudeModel
    EndpointModel <|-- TogetherModel
    
    KeyBasedAuthMixIn -- AzureOpenAIModel
    KeyBasedAuthMixIn -- DirectOpenAIModel
    KeyBasedAuthMixIn -- GeminiModel
    KeyBasedAuthMixIn -- ClaudeModel
```

Sources: [setup.py:15-44](), [README.md:115]()

The model system provides a unified interface for accessing different types of language models:

- Abstract `Model` class defines the common interface
- Support for API-based models (OpenAI, Claude, Gemini)
- Support for locally-hosted models via Hugging Face
- Authentication handling via mixins

## Configuration System

```mermaid
flowchart TD
    subgraph "User Configuration"
        EC["ExperimentConfig"] --> |"configure_pipeline()"| PC["PipelineConfig"]
    end

    subgraph "Component Configurations"
        PC --> DPC["DataProcessingConfig"]
        PC --> PPC["PromptProcessingConfig"]
        PC --> IC["InferenceConfig"]
        PC --> ERC["EvalReportingConfig"]
    end

    subgraph "Utility Configurations"
        DPC --> |"references"| DSC["DataSetConfig"]
        IC --> |"references"| MC["ModelConfig"]
        IC --> |"references"| DLC["DataLoaderConfig"]
        ERC --> |"references"| METR["MetricConfig"]
        ERC --> |"references"| AGG["AggregatorConfig"]
    end

    subgraph "Instantiation"
        DPC --> |"creates"| DP["DataProcessing"]
        PPC --> |"creates"| PP["PromptProcessing"]
        IC --> |"creates"| INF["Inference"]
        ERC --> |"creates"| ER["EvalReporting"]
    end
```

Sources: [tests/component_tests.py:32-49](), [README.md:85-91]()

The configuration system uses a hierarchical approach:

- **ExperimentConfig**: Top-level configuration that defines a pipeline
- **Component Configs**: Configure individual pipeline components
- **Utility Configs**: Configuration for utility classes used by components

## Benchmark Suite

Eureka ML Insights includes pre-configured pipelines for several benchmarks:

| Benchmark | Modality | Capability | Pipeline Config |
|-----------|----------|------------|----------------|
| GeoMeter | Image -> Text | Geometric Reasoning | `geometer.py` |
| MMMU | Image -> Text | Multimodal QA | `mmmu.py` |
| Image Understanding | Image -> Text | Object Recognition, Detection | Various configs |
| Vision Language | Image -> Text | Spatial Understanding | Various configs |
| IFEval | Text -> Text | Instruction Following | `ifeval.py` |
| FlenQA | Text -> Text | Long Context Multi-hop QA | `flenqa.py` |
| Kitab | Text -> Text | Information Retrieval | `kitab.py` |
| ToxiGen | Text -> Text | Toxicity Detection | `toxigen.py` |

Sources: [README.md:40-57](), [eureka_ml_insights/metrics/ifeval_instruction_utils.py:20-3404]()

## Getting Started

To use Eureka ML Insights, you typically:

1. Choose or define an experiment configuration
2. Select a model configuration
3. Run the evaluation pipeline
4. Analyze the results

Basic usage:

```bash
python main.py --exp_config <experiment_config> --model_config <model_config> --exp_logdir <output_directory>
```

Example:

```bash
python main.py --exp_config FlenQA_Experiment_Pipeline --model_config OAI_GPT4_1106_PREVIEW_CONFIG --exp_logdir gpt4_flenqa
```

Sources: [README.md:84-94](), [README.md:58-83]()

## Installation

Eureka ML Insights can be installed in several ways:

### Using pip (for development)

```bash
python3 -m venv .venv
# Activate venv
pip install -e .
```

### Using pip (from wheel package)

```bash
pip install eureka_ml_insights.whl
```

### Using Conda

```bash
conda env create --name myenv --file environment.yml
conda activate myenv
# Optional for GPU support
conda env update --file environment_gpu.yml
```

Sources: [README.md:58-82](), [environment.yml:1-490](), [environment_gpu.yml:1-14]()

## Key Features

- **Modular Design**: Components can be independently configured and combined
- **Comprehensive Model Support**: API-based and self-hosted models
- **Flexible Data Processing**: Various data sources and formats
- **Rich Evaluation Capabilities**: Extensive metrics and aggregators
- **Extensive Benchmark Suite**: Pre-configured for many tasks
- **Parallel Inference**: Support for concurrent model requests
- **Resumable Operations**: Continue interrupted evaluations

Sources: [README.md:19-18](), [tests/component_tests.py:191-232]()

Eureka ML Insights provides a systematic way to evaluate machine learning models across a diverse set of tasks, with particular focus on LLMs and multimodal models. Its modular architecture allows for flexibility and extensibility, enabling researchers to create custom evaluation pipelines tailored to their specific needs.

---

