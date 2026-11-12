<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/scirepeval · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [requirements.txt](requirements.txt)

</details>



## Purpose and Scope

SciRepEval is a comprehensive framework for training and evaluating scientific document representation models across multiple task formats and domains. The repository provides both a standardized benchmark consisting of 24 scientific document tasks and the infrastructure to train multi-task transformer models with parameter-efficient adaptation methods.

This document covers the high-level architecture and core capabilities of the SciRepEval system. For detailed information about specific components, see [Core Evaluation Framework](#2) for the evaluation engine, [Model Architecture and Variants](#3) for supported model types, [Training System](#4) for multi-task training capabilities, and [Task Configuration and Evaluation](#5) for benchmark task definitions.

## System Architecture

SciRepEval operates through a modular architecture that separates evaluation orchestration, model abstraction, and task-specific evaluation logic. The system supports both pre-trained model evaluation and custom model training across scientific document understanding tasks.

### Core Components and File Structure

```mermaid
graph TB
    subgraph "Main_Orchestration" ["Main Orchestration"]
        scirepeval["scirepeval.py<br/>SciRepEval class"]
        tasks_config["scirepeval_tasks.jsonl<br/>Task definitions"]
    end
    
    subgraph "Evaluation_Engine" ["Evaluation Engine"]
        evaluator["evaluation/evaluator.py<br/>Evaluator base class<br/>SupervisedEvaluator<br/>IREvaluator"]
        encoders["evaluation/encoders.py<br/>Model abstraction<br/>EmbeddingsGenerator"]
        datasets["evaluation/eval_datasets.py<br/>SimpleDataset<br/>IRDataset"]
    end
    
    subgraph "Model_Layer" ["Model Layer"]
        model["evaluation/model.py<br/>Model class<br/>EncoderFactory"]
        pals["bert_pals.py<br/>BERT_PALS architecture"]
        adapters["adapter_fusion.py<br/>AdapterFusion system"]
        instructor["evaluation/instructor.py<br/>InstructorModel"]
    end
    
    subgraph "Training_System" ["Training System"]
        pl_training["training/pl_training.py<br/>PyTorch Lightning"]
        tasks_train["training/tasks.py<br/>Training configuration"]
        mtl_datasets["training/mtl_datasets.py<br/>Multi-task data loading"]
    end
    
    subgraph "Specialized_Evaluators" ["Specialized Evaluators"]
        s2and["s2and_embeddings.py<br/>S2ANDEvaluator"]
        reviewer["reviewer_matching.py<br/>ReviewerMatchingEvaluator"]
        fewshot["evaluation/fewshot.py<br/>FewShotEvaluator"]
    end
    
    tasks_config --> scirepeval
    scirepeval --> evaluator
    evaluator --> encoders
    evaluator --> datasets
    encoders --> model
    model --> pals
    model --> adapters
    model --> instructor
    
    pl_training --> tasks_train
    pl_training --> mtl_datasets
    
    scirepeval --> s2and
    scirepeval --> reviewer
    scirepeval --> fewshot
    
    style scirepeval fill:#e1f5fe
    style evaluator fill:#f3e5f5
    style model fill:#e8f5e8
    style pl_training fill:#fff3e0
```

Sources: [README.md:1-98](), [scirepeval.py](), [evaluation/evaluator.py](), [evaluation/encoders.py](), [evaluation/model.py]()

## Core Capabilities

SciRepEval provides four primary capabilities organized around scientific document representation learning:

| Capability | Description | Key Components |
|------------|-------------|----------------|
| **Benchmark Evaluation** | Evaluate models on 24 standardized scientific tasks | `scirepeval.py`, `scirepeval_tasks.jsonl` |
| **Multi-Task Training** | Train transformer models with parameter-efficient methods | `training/pl_training.py`, `bert_pals.py` |
| **Model Abstraction** | Unified interface for HuggingFace, local, and custom models | `evaluation/model.py`, `evaluation/encoders.py` |
| **Specialized Evaluation** | Domain-specific evaluators for scientific tasks | `s2and_embeddings.py`, `reviewer_matching.py` |

### Task Format Support

The framework supports four distinct task formats that cover different aspects of scientific document understanding:

```mermaid
graph LR
    subgraph "Task_Formats" ["Task Formats"]
        CLF["CLF<br/>Classification<br/>F1 Macro/Binary"]
        RGN["RGN<br/>Regression<br/>Kendall's Tau"]
        PRX["PRX<br/>Proximity Retrieval<br/>MAP, NDCG"]
        SRCH["SRCH<br/>Ad-hoc Search<br/>NDCG"]
    end
    
    subgraph "Evaluation_Pipeline" ["Evaluation Pipeline"]
        SupervisedEvaluator["SupervisedEvaluator<br/>evaluation/evaluator.py"]
        IREvaluator["IREvaluator<br/>evaluation/evaluator.py"]
        EmbeddingsGenerator["EmbeddingsGenerator<br/>evaluation/encoders.py"]
    end
    
    subgraph "Data_Processing" ["Data Processing"]
        SimpleDataset["SimpleDataset<br/>evaluation/eval_datasets.py"]
        IRDataset["IRDataset<br/>evaluation/eval_datasets.py"]
        text_embeddings["Text → Embeddings<br/>Batch processing"]
    end
    
    CLF --> SupervisedEvaluator
    RGN --> SupervisedEvaluator
    PRX --> IREvaluator
    SRCH --> IREvaluator
    
    SupervisedEvaluator --> EmbeddingsGenerator
    IREvaluator --> EmbeddingsGenerator
    EmbeddingsGenerator --> text_embeddings
    
    SupervisedEvaluator --> SimpleDataset
    IREvaluator --> IRDataset
    
    style CLF fill:#e1f5fe
    style RGN fill:#e1f5fe
    style PRX fill:#f3e5f5
    style SRCH fill:#f3e5f5
```

Sources: [README.md:49-74](), [evaluation/evaluator.py](), [evaluation/eval_datasets.py]()

## Model Architecture Support

SciRepEval provides a unified interface for multiple model architectures through the `Model` class and `EncoderFactory`. The system supports both standard transformer models and parameter-efficient adaptation methods:

### Supported Model Types

- **HuggingFace Models**: Standard transformer models loaded via `transformers.AutoModel`
- **BERT PALS**: Parameter-efficient adaptation using the BERT PALS architecture in [bert_pals.py]()
- **Adapter Systems**: Task-specific adapters and AdapterFusion in [adapter_fusion.py]()
- **Instructor Models**: Instruction-based embeddings via [evaluation/instructor.py]()
- **External APIs**: Integration with OpenAI GPT-3 and other external services

The model abstraction layer in [evaluation/encoders.py]() handles embedding generation, caching, and batch processing across all supported model types.

## Data Infrastructure

The benchmark utilizes a comprehensive dataset infrastructure spanning 24 scientific document tasks:

- **Data Sources**: AWS S3 (~24 GB), HuggingFace Datasets (`allenai/scirepeval`, `allenai/scirepeval_test`)
- **Task Coverage**: Citation prediction, author matching, field classification, peer review scoring, and information retrieval
- **Evaluation Metrics**: F1 scores, Kendall's Tau, MAP, NDCG, and specialized metrics like B³ F1 for clustering

The framework separates test metadata (for embedding generation) from labeled examples (for evaluation), enabling proper representation learning evaluation protocols.

Sources: [README.md:26-48](), [requirements.txt:1-102]()

---

