<!-- source: DeepWiki mcp.deepwiki.com · repo optuna/optuna · page 2 Core Components · fetched 2026-10-21 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/distributions.py](optuna/distributions.py)
- [optuna/integration/pytorch_distributed.py](optuna/integration/pytorch_distributed.py)
- [optuna/storages/_heartbeat.py](optuna/storages/_heartbeat.py)
- [optuna/study/_dataframe.py](optuna/study/_dataframe.py)
- [optuna/study/_optimize.py](optuna/study/_optimize.py)
- [optuna/study/_tell.py](optuna/study/_tell.py)
- [optuna/study/study.py](optuna/study/study.py)
- [optuna/testing/objectives.py](optuna/testing/objectives.py)
- [optuna/trial/_base.py](optuna/trial/_base.py)
- [optuna/trial/_fixed.py](optuna/trial/_fixed.py)
- [optuna/trial/_frozen.py](optuna/trial/_frozen.py)
- [optuna/trial/_trial.py](optuna/trial/_trial.py)
- [tests/storages_tests/rdb_tests/test_storage.py](tests/storages_tests/rdb_tests/test_storage.py)
- [tests/storages_tests/test_cached_storage.py](tests/storages_tests/test_cached_storage.py)
- [tests/storages_tests/test_heartbeat.py](tests/storages_tests/test_heartbeat.py)
- [tests/storages_tests/test_storages.py](tests/storages_tests/test_storages.py)
- [tests/study_tests/test_dataframe.py](tests/study_tests/test_dataframe.py)
- [tests/study_tests/test_optimize.py](tests/study_tests/test_optimize.py)
- [tests/study_tests/test_study.py](tests/study_tests/test_study.py)
- [tests/study_tests/test_study_summary.py](tests/study_tests/test_study_summary.py)
- [tests/test_callbacks.py](tests/test_callbacks.py)
- [tests/test_distributions.py](tests/test_distributions.py)

</details>



This document covers the fundamental building blocks that form Optuna's hyperparameter optimization framework. These components work together to orchestrate the optimization process, manage parameter spaces, and persist optimization data. For information about specific sampling algorithms, see [Sampling Algorithms](#3). For user-facing tools and interfaces, see [Tools and User Interfaces](#5).

## System Overview

Optuna's core architecture consists of four primary components that collaborate to execute hyperparameter optimization:

**Study and Trial Management System**
The `Study` class serves as the central orchestrator that manages the optimization process and coordinates trials. Each `Trial` represents an individual evaluation of the objective function with specific parameter values.

**Parameter Distribution System**
The `distributions` module defines how parameter spaces are structured, supporting continuous, discrete, and categorical parameters with various constraints and transformations.

**Storage Architecture**
The storage layer provides a pluggable persistence system with multiple backends, enabling both local and distributed optimization scenarios.

**Sampling Integration**
The core components integrate with sampling algorithms through well-defined interfaces, allowing different optimization strategies to be plugged in seamlessly.

## Core Component Architecture

```mermaid
graph TB
    subgraph "Core Orchestration Layer"
        Study["Study<br/>study.py<br/>Central orchestrator"]
        Trial["Trial<br/>trial.py<br/>Individual evaluation"]
        FrozenTrial["FrozenTrial<br/>trial.py<br/>Immutable trial state"]
    end
    
    subgraph "Parameter Definition Layer"
        BaseDistribution["BaseDistribution<br/>distributions.py<br/>Abstract parameter type"]
        FloatDistribution["FloatDistribution<br/>distributions.py<br/>Continuous parameters"]
        IntDistribution["IntDistribution<br/>distributions.py<br/>Integer parameters"]
        CategoricalDistribution["CategoricalDistribution<br/>distributions.py<br/>Discrete choices"]
    end
    
    subgraph "Storage Abstraction Layer"
        BaseStorage["BaseStorage<br/>storages/_base.py<br/>Storage interface"]
        InMemoryStorage["InMemoryStorage<br/>storages/_in_memory.py<br/>Default storage"]
        RDBStorage["RDBStorage<br/>storages/_rdb/storage.py<br/>Database storage"]
        JournalStorage["JournalStorage<br/>storages/_journal/storage.py<br/>File-based storage"]
    end
    
    subgraph "Sampling Interface Layer"
        BaseSampler["BaseSampler<br/>samplers/_base.py<br/>Sampler interface"]
        RandomSampler["RandomSampler<br/>samplers/_random.py<br/>Baseline sampler"]
        TPESampler["TPESampler<br/>samplers/_tpe/sampler.py<br/>Bayesian optimization"]
    end
    
    Study --> Trial
    Study --> BaseStorage
    Trial --> BaseDistribution
    Trial --> BaseSampler
    
    BaseDistribution --> FloatDistribution
    BaseDistribution --> IntDistribution
    BaseDistribution --> CategoricalDistribution
    
    BaseStorage --> InMemoryStorage
    BaseStorage --> RDBStorage
    BaseStorage --> JournalStorage
    
    BaseSampler --> RandomSampler
    BaseSampler --> TPESampler
    
    Study --> FrozenTrial
    BaseStorage --> FrozenTrial
```

Sources: [tests/samplers_tests/test_samplers.py:18-31]()

## Study and Trial Lifecycle

The study-trial relationship forms the core execution model where studies manage the optimization process and trials represent individual parameter evaluations.

```mermaid
sequenceDiagram
    participant User as "User Code"
    participant Study as "Study"
    participant Storage as "BaseStorage"
    participant Sampler as "BaseSampler" 
    participant Trial as "Trial"
    
    User->>Study: "create_study()"
    Study->>Storage: "create_new_study()"
    
    User->>Study: "optimize(objective, n_trials)"
    loop For each trial
        Study->>Storage: "create_new_trial()"
        Storage-->>Study: "trial_id"
        Study->>Storage: "get_trial(trial_id)"
        Storage-->>Study: "FrozenTrial"
        
        Study->>Sampler: "sample_independent() / sample_relative()"
        Sampler-->>Study: "parameter_values"
        
        Study->>Trial: "suggest_float() / suggest_int() / suggest_categorical()"
        Trial-->>Study: "suggested_value"
        
        Study->>User: "objective(trial)"
        User-->>Study: "objective_value"
        
        Study->>Storage: "set_trial_values()"
        Study->>Storage: "set_trial_state(COMPLETE)"
    end
```

The `Study` class coordinates the optimization loop by:
- Managing trial creation through storage backends
- Delegating parameter sampling to configured samplers  
- Executing user-defined objective functions
- Persisting trial results and state changes

Sources: [tests/samplers_tests/test_samplers.py:478-480](), [tests/samplers_tests/test_samplers.py:526-543]()

## Parameter Distribution System

The distribution system defines the parameter search space through a hierarchy of distribution classes that handle different parameter types and constraints.

| Distribution Class | Parameter Type | Key Features |
|-------------------|----------------|--------------|
| `FloatDistribution` | Continuous | Support for log-scale, step quantization |
| `IntDistribution` | Integer | Support for log-scale, step constraints |  
| `CategoricalDistribution` | Discrete choices | Arbitrary choice types |

```mermaid
graph LR
    subgraph "Distribution Interface"
        BaseDistribution["BaseDistribution<br/>Abstract interface"]
        _contains["_contains(value)<br/>Validation method"]
        to_internal_repr["to_internal_repr(value)<br/>Value transformation"]
    end
    
    subgraph "Concrete Distributions"
        FloatDist["FloatDistribution<br/>low, high, log, step"]
        IntDist["IntDistribution<br/>low, high, log, step"] 
        CatDist["CategoricalDistribution<br/>choices"]
    end
    
    subgraph "Trial Integration"
        Trial["Trial"]
        suggest_float["suggest_float(name, low, high)"]
        suggest_int["suggest_int(name, low, high)"]
        suggest_categorical["suggest_categorical(name, choices)"]
    end
    
    BaseDistribution --> FloatDist
    BaseDistribution --> IntDist
    BaseDistribution --> CatDist
    
    Trial --> suggest_float
    Trial --> suggest_int
    Trial --> suggest_categorical
    
    suggest_float --> FloatDist
    suggest_int --> IntDist
    suggest_categorical --> CatDist
```

The distribution system validates parameter bounds and handles transformations between user-space and internal representations used by optimization algorithms.

Sources: [tests/samplers_tests/test_samplers.py:224-258](), [tests/samplers_tests/test_samplers.py:289-310](), [tests/samplers_tests/test_samplers.py:263-287]()

## Storage Architecture

The storage system provides a pluggable persistence layer that abstracts different storage backends through the `BaseStorage` interface.

```mermaid
graph TB
    subgraph "Storage Interface"
        BaseStorage["BaseStorage<br/>storages/_base.py"]
        create_new_study["create_new_study()"]
        create_new_trial["create_new_trial()"]
        get_trial["get_trial()"]
        set_trial_values["set_trial_values()"]
    end
    
    subgraph "Storage Implementations"
        InMemory["InMemoryStorage<br/>Default, non-persistent"]
        RDB["RDBStorage<br/>SQL databases"]
        Journal["JournalStorage<br/>File/Redis based"]
        Cached["_CachedStorage<br/>Performance wrapper"]
    end
    
    subgraph "Backend Systems"
        SQLite[("SQLite")]
        PostgreSQL[("PostgreSQL")]
        MySQL[("MySQL")]
        Redis[("Redis")]
        FileSystem[("File System")]
    end
    
    BaseStorage --> InMemory
    BaseStorage --> RDB
    BaseStorage --> Journal
    BaseStorage --> Cached
    
    RDB --> SQLite
    RDB --> PostgreSQL
    RDB --> MySQL
    
    Journal --> Redis
    Journal --> FileSystem
    
    Cached --> RDB
```

The storage architecture supports:
- **Study Management**: Creating, retrieving, and modifying studies
- **Trial Lifecycle**: Managing trial states from creation to completion
- **Parameter Persistence**: Storing suggested parameters and objective values
- **Concurrent Access**: Thread-safe operations for parallel optimization

Sources: [tests/samplers_tests/test_samplers.py:478-480]()

## Component Integration Patterns

The core components integrate through well-defined interfaces that enable flexible composition of optimization strategies.

**Sampler Integration Pattern**
```mermaid
graph LR
    subgraph "Sampling Interface"
        BaseSampler["BaseSampler"]
        sample_independent["sample_independent()<br/>Single parameter"]
        sample_relative["sample_relative()<br/>Joint parameters"]
        infer_relative_search_space["infer_relative_search_space()"]
    end
    
    subgraph "Trial Context"
        Trial["Trial"]
        Study["Study"]
        SearchSpace["Search Space<br/>Dict[str, BaseDistribution]"]
    end
    
    BaseSampler --> sample_independent
    BaseSampler --> sample_relative
    BaseSampler --> infer_relative_search_space
    
    sample_independent --> Trial
    sample_relative --> SearchSpace
    infer_relative_search_space --> Study
```

The sampling integration allows different optimization algorithms to be plugged in by implementing the `BaseSampler` interface methods:
- `sample_independent()`: Suggests individual parameters independently
- `sample_relative()`: Suggests parameters considering their relationships
- `infer_relative_search_space()`: Determines which parameters to optimize jointly

Sources: [tests/samplers_tests/test_samplers.py:44-78](), [tests/samplers_tests/test_samplers.py:494-512]()

**Parameter Suggestion Flow**
```mermaid
graph TD
    Trial["Trial.suggest_*()"] --> CheckCache["Check existing<br/>parameter value"]
    CheckCache -->|"Not cached"| SampleIndependent["Sampler.sample_independent()"]
    CheckCache -->|"Cached"| ReturnCached["Return cached value"]
    
    SampleIndependent --> ValidateDistribution["Distribution._contains()"]
    ValidateDistribution --> StoreParameter["Store in trial params"]
    StoreParameter --> UpdateStorage["Update storage backend"]
    UpdateStorage --> ReturnValue["Return parameter value"]
```

This flow ensures parameter consistency within trials while allowing samplers to influence parameter selection based on optimization history.

Sources: [tests/samplers_tests/test_samplers.py:514-544]()

---

