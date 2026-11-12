<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/archai · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.amltignore](.amltignore)
- [.gitattributes](.gitattributes)
- [.github/ISSUE_TEMPLATE/bug-report.md](.github/ISSUE_TEMPLATE/bug-report.md)
- [.github/ISSUE_TEMPLATE/feature-request.md](.github/ISSUE_TEMPLATE/feature-request.md)
- [.github/ISSUE_TEMPLATE/regular-issue.md](.github/ISSUE_TEMPLATE/regular-issue.md)
- [.github/workflows/build-publish-docs.yml](.github/workflows/build-publish-docs.yml)
- [.github/workflows/build-release-pypi.yml](.github/workflows/build-release-pypi.yml)
- [.github/workflows/check-with-codeql.yml](.github/workflows/check-with-codeql.yml)
- [.github/workflows/check-with-devskim.yml](.github/workflows/check-with-devskim.yml)
- [.vscode/launch.json](.vscode/launch.json)
- [README.md](README.md)
- [archai/discrete_search/__init__.py](archai/discrete_search/__init__.py)
- [archai/discrete_search/algos/bananas.py](archai/discrete_search/algos/bananas.py)
- [archai/discrete_search/algos/evolution_pareto.py](archai/discrete_search/algos/evolution_pareto.py)
- [archai/discrete_search/algos/local_search.py](archai/discrete_search/algos/local_search.py)
- [archai/discrete_search/algos/random_search.py](archai/discrete_search/algos/random_search.py)
- [archai/discrete_search/algos/regularized_evolution.py](archai/discrete_search/algos/regularized_evolution.py)
- [archai/discrete_search/algos/successive_halving.py](archai/discrete_search/algos/successive_halving.py)
- [archai/discrete_search/api/model_evaluator.py](archai/discrete_search/api/model_evaluator.py)
- [archai/discrete_search/api/search_objectives.py](archai/discrete_search/api/search_objectives.py)
- [archai/discrete_search/api/search_results.py](archai/discrete_search/api/search_results.py)
- [archai/discrete_search/api/searcher.py](archai/discrete_search/api/searcher.py)
- [archai/discrete_search/evaluators/functional.py](archai/discrete_search/evaluators/functional.py)
- [archai/discrete_search/evaluators/onnx_model.py](archai/discrete_search/evaluators/onnx_model.py)
- [archai/discrete_search/evaluators/progressive_training.py](archai/discrete_search/evaluators/progressive_training.py)
- [archai/discrete_search/evaluators/ray.py](archai/discrete_search/evaluators/ray.py)
- [setup.py](setup.py)

</details>



## Purpose and Scope

Archai is a comprehensive Neural Architecture Search (NAS) platform designed to accelerate the discovery of efficient deep neural network architectures through fast, reproducible, and modular research. This document provides a high-level overview of the Archai system architecture, core components, and key capabilities.

Archai enables researchers and practitioners to:
- Define and explore custom neural architecture search spaces
- Apply various search algorithms (evolutionary, Bayesian optimization, random search)
- Evaluate architectures using multiple objectives (accuracy, latency, memory, parameters)
- Deploy and scale experiments using cloud infrastructure
- Integrate with existing ML workflows and frameworks

For detailed information about specific algorithms, see [Search Algorithms](#4.1). For task-specific implementations, see [Tasks and Applications](#6). For cloud deployment guidance, see [Cloud and Distributed Computing](#7).

## System Architecture

The Archai platform follows a modular architecture that separates search algorithms, evaluation objectives, search spaces, and infrastructure concerns:

### Core System Components

```mermaid
graph TB
    subgraph "Archai Platform"
        DS["discrete_search"]
        API["api"]
        COMMON["common"]
        TASKS["tasks"]
    end
    
    subgraph "Search Framework"
        SS["SearchSpace"] --> ALGO["Search Algorithms"]
        SO["SearchObjectives"] --> ALGO
        ALGO --> SR["SearchResults"]
        EVAL["ModelEvaluator"] --> SO
        AM["ArchaiModel"] --> EVAL
    end
    
    subgraph "Core Algorithms"
        EP["EvolutionParetoSearch"]
        RS["RandomSearch"]
        BAN["MoBananasSearch"]
        RE["RegularizedEvolutionSearch"]
        LS["LocalSearch"]
        SH["SuccessiveHalvingSearch"]
    end
    
    subgraph "Evaluation Components"
        ONNX["AvgOnnxLatency"]
        PROG["ProgressiveTraining"]
        RAY["RayParallelEvaluator"]
        FUNC["EvaluationFunction"]
    end
    
    DS --> SS
    DS --> ALGO
    DS --> EVAL
    ALGO --> EP
    ALGO --> RS
    ALGO --> BAN
    ALGO --> RE
    ALGO --> LS
    ALGO --> SH
    EVAL --> ONNX
    EVAL --> PROG
    EVAL --> RAY
    EVAL --> FUNC
```

Sources: [setup.py:7](), [archai/discrete_search/api/searcher.py:11-47](), [archai/discrete_search/api/search_objectives.py:33-397](), [archai/discrete_search/algos/evolution_pareto.py:21-309](), [archai/discrete_search/evaluators/onnx_model.py:16-91]()

### Package Distribution and Dependencies

```mermaid
graph TB
    subgraph "PyPI Package: archai"
        CORE["Core Dependencies"]
        CV["cv extras"]
        NLP["nlp extras"] 
        DS["deepspeed extras"]
        AML["aml extras"]
        DOCS["docs extras"]
        DEV["dev extras"]
    end
    
    subgraph "Core Dependencies"
        CORE_DEPS["h5py, hyperopt, matplotlib,<br/>onnx, onnxruntime, overrides,<br/>psutil, pyyaml, ray, tensorboard"]
    end
    
    subgraph "Optional Features"
        CV_DEPS["gorilla, opencv-python,<br/>lightning, torchvision"]
        NLP_DEPS["datasets, einops, transformers,<br/>tokenizers"]
        DS_DEPS["deepspeed, mlflow"]
        AML_DEPS["azure-ai-ml, azure-storage-blob,<br/>jupyter, matplotlib"]
    end
    
    CORE --> CORE_DEPS
    CV --> CV_DEPS
    NLP --> NLP_DEPS
    DS --> DS_DEPS
    AML --> AML_DEPS
    DEV --> CV_DEPS
    DEV --> NLP_DEPS
    DEV --> AML_DEPS
```

Sources: [setup.py:9-188]()

## Neural Architecture Search Workflow

The core NAS workflow in Archai follows a standardized pattern across different search algorithms:

### Search Algorithm Execution Flow

```mermaid
flowchart TD
    START["Search Algorithm Start"] --> INIT["Initialize Population"]
    INIT --> VALIDATE["Validate Constraints"]
    VALIDATE --> EVAL_OBJ["Evaluate Objectives"]
    EVAL_OBJ --> UPDATE["Update Search State"]
    UPDATE --> PARETO["Calculate Pareto Frontier"]
    PARETO --> SAVE["Save Results & Models"]
    SAVE --> GENERATE["Generate New Population"]
    GENERATE --> VALIDATE
    GENERATE --> END["Search Complete"]
    
    subgraph "Population Generation Methods"
        RANDOM["random_sample()"]
        MUTATE["mutate()"]
        CROSSOVER["crossover()"]
        THOMPSON["Thompson Sampling"]
    end
    
    subgraph "Evaluation Components"
        CHEAP["Cheap Objectives<br/>eval_cheap_objs()"]
        EXPENSIVE["Expensive Objectives<br/>eval_expensive_objs()"]
        CONSTRAINTS["validate_constraints()"]
    end
    
    GENERATE --> RANDOM
    GENERATE --> MUTATE
    GENERATE --> CROSSOVER
    GENERATE --> THOMPSON
    EVAL_OBJ --> CHEAP
    EVAL_OBJ --> EXPENSIVE
    VALIDATE --> CONSTRAINTS
```

Sources: [archai/discrete_search/algos/evolution_pareto.py:223-308](), [archai/discrete_search/api/search_objectives.py:260-361](), [archai/discrete_search/algos/bananas.py:248-312]()

### Multi-Objective Evaluation System

The `SearchObjectives` class coordinates evaluation of multiple criteria:

```mermaid
classDiagram
    class SearchObjectives {
        +objectives: Dict[str, SearchObjective]
        +constraints: Dict[str, SearchConstraint]
        +add_objective(name, evaluator, higher_is_better)
        +eval_all_objs(models, budgets) Dict[str, ndarray]
        +validate_constraints(models) Tuple
        +is_model_valid(model) bool
    }
    
    class SearchObjective {
        +name: str
        +evaluator: ModelEvaluator
        +higher_is_better: bool
        +compute_intensive: bool
        +constraint: Optional[Tuple]
    }
    
    class ModelEvaluator {
        <<abstract>>
        +evaluate(arch, budget) float
    }
    
    class AsyncModelEvaluator {
        <<abstract>>
        +send(arch, budget) None
        +fetch_all() List[float]
    }
    
    SearchObjectives --> SearchObjective
    SearchObjective --> ModelEvaluator
    ModelEvaluator <|-- AsyncModelEvaluator
```

Sources: [archai/discrete_search/api/search_objectives.py:24-397](), [archai/discrete_search/api/model_evaluator.py:13-139]()

## Development and Execution Environment

### VS Code Integration and Launch Configurations

Archai provides extensive VS Code integration through predefined launch configurations for different NAS experiments:

```mermaid
graph TB
    subgraph "VS Code Launch Configurations"
        MAIN["scripts/supergraph/main.py"]
        
        subgraph "Algorithm Configurations"
            DARTS["Darts-*"]
            PETRI["Petridish-*"] 
            XNAS["Xnas-*"]
            DIVNAS["Divnas-*"]
            RANDOM["Random-*"]
            GS["Gs-*"]
        end
        
        subgraph "Execution Modes"
            FULL["--full (Complete Pipeline)"]
            SEARCH["--no-eval (Search Only)"]
            EVAL["--no-search (Evaluation Only)"]
            TOY["Toy Datasets"]
        end
        
        subgraph "Dataset Options"
            CIFAR["Default (CIFAR-10)"]
            IMAGENET["--datasets imagenet"]
            FOOD101["--datasets food101"]
        end
    end
    
    MAIN --> DARTS
    MAIN --> PETRI
    MAIN --> XNAS
    MAIN --> DIVNAS
    MAIN --> RANDOM
    MAIN --> GS
    
    DARTS --> FULL
    DARTS --> SEARCH
    DARTS --> EVAL
    DARTS --> TOY
    
    FULL --> CIFAR
    FULL --> IMAGENET
    FULL --> FOOD101
```

Sources: [.vscode/launch.json:1-269]()

### Package Installation and Development Setup

The platform supports multiple installation modes through setuptools configuration:

| Installation Mode | Command | Components Included |
|------------------|---------|-------------------|
| Core | `pip install archai` | Basic NAS functionality, ONNX evaluation |
| Computer Vision | `pip install archai[cv]` | + OpenCV, Lightning, torchvision |
| Natural Language Processing | `pip install archai[nlp]` | + Transformers, datasets, tokenizers |
| Azure ML | `pip install archai[aml]` | + Azure ML SDK, Jupyter notebooks |
| Development | `pip install archai[dev]` | All extras except DeepSpeed (Windows) |

Sources: [setup.py:76-144](), [README.md:30-43]()

## Integration Capabilities

### Cloud Infrastructure Support

Archai integrates with cloud platforms for distributed execution and storage:

```mermaid
graph LR
    subgraph "Local Development"
        JUPYTER["Jupyter Notebooks"]
        VSCODE["VS Code Launch Configs"]
        PYTEST["pytest Tests"]
    end
    
    subgraph "Azure ML Integration"
        MLCLIENT["MLClient Workspace"]
        COMPUTE["Compute Clusters"]
        JOBS["Job Pipeline"]
        ENV["Conda Environments"]
    end
    
    subgraph "Storage Systems"
        BLOB["Azure Blob Storage<br/>(Models & Artifacts)"]
        TABLE["Azure Table Storage<br/>(Job Status & Locking)"]
        LOCAL["Local Cache"]
    end
    
    subgraph "Evaluation Backends"
        SNPE["SNPE Benchmarking<br/>(Qualcomm)"]
        ONNX_EVAL["ONNX Runtime"]
        DEEPSPEED["DeepSpeed Training"]
    end
    
    JUPYTER --> MLCLIENT
    VSCODE --> MLCLIENT
    MLCLIENT --> COMPUTE
    MLCLIENT --> JOBS
    JOBS --> BLOB
    JOBS --> TABLE
    JOBS --> SNPE
    JOBS --> ONNX_EVAL
    JOBS --> DEEPSPEED
```

Sources: [setup.py:114-127](), [.amltignore:1-12](), [.github/workflows/build-publish-docs.yml:1-46]()

### Evaluation and Benchmarking Framework

The platform provides multiple evaluation backends for comprehensive architecture assessment:

```mermaid
classDiagram
    class AvgOnnxLatency {
        +input_shape: Union[Tuple, List[Tuple]]
        +num_trials: int
        +device: str
        +evaluate(model, budget) float
    }
    
    class ProgressiveTraining {
        +search_space: DiscreteSearchSpace
        +dataset: DatasetProvider
        +training_fn: Callable
        +training_states: Dict
        +evaluate(arch, budget) float
    }
    
    class RayParallelEvaluator {
        +obj: ModelEvaluator
        +timeout: Optional[float]
        +force_stop: bool
        +send(arch, budget) None
        +fetch_all() List[float]
    }
    
    class EvaluationFunction {
        +evaluation_fn: Callable
        +evaluate(model, budget) float
    }
    
    ModelEvaluator <|-- AvgOnnxLatency
    ModelEvaluator <|-- ProgressiveTraining
    AsyncModelEvaluator <|-- RayParallelEvaluator
    ModelEvaluator <|-- EvaluationFunction
```

Sources: [archai/discrete_search/evaluators/onnx_model.py:16-91](), [archai/discrete_search/evaluators/progressive_training.py:29-158](), [archai/discrete_search/evaluators/ray.py:23-91](), [archai/discrete_search/evaluators/functional.py:13-34]()

---

