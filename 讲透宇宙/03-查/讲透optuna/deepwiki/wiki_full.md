# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [optuna/integration/chainermn.py](optuna/integration/chainermn.py)
- [optuna/storages/_heartbeat.py](optuna/storages/_heartbeat.py)
- [optuna/study/_dataframe.py](optuna/study/_dataframe.py)
- [optuna/study/_optimize.py](optuna/study/_optimize.py)
- [optuna/study/_tell.py](optuna/study/_tell.py)
- [optuna/study/study.py](optuna/study/study.py)
- [optuna/testing/objectives.py](optuna/testing/objectives.py)
- [pyproject.toml](pyproject.toml)
- [tests/samplers_tests/test_samplers.py](tests/samplers_tests/test_samplers.py)
- [tests/storages_tests/test_heartbeat.py](tests/storages_tests/test_heartbeat.py)
- [tests/study_tests/test_dataframe.py](tests/study_tests/test_dataframe.py)
- [tests/study_tests/test_optimize.py](tests/study_tests/test_optimize.py)
- [tests/study_tests/test_study.py](tests/study_tests/test_study.py)
- [tests/study_tests/test_study_summary.py](tests/study_tests/test_study_summary.py)
- [tests/test_callbacks.py](tests/test_callbacks.py)

</details>



## Purpose and Scope

This page provides a high-level introduction to Optuna, an open-source hyperparameter optimization framework. It covers Optuna's architectural design, core components, and optimization workflow. For detailed information about specific subsystems, refer to:

- Core components: [Core Components](#2)
- Sampling algorithms: [Sampling Algorithms](#3)
- Storage backends: [Storage Architecture](#2.4)
- Integration with ML frameworks: [Integration System](#4)
- Development setup: [Development and Deployment](#6)

**Sources:** [pyproject.toml:6-7](), [CONTRIBUTING.md:1-15]()

---

## What is Optuna?

Optuna is a Python-based hyperparameter optimization framework designed for machine learning applications. It provides:

| Feature | Description |
|---------|-------------|
| **Flexible Interface** | Define-by-run API allowing dynamic search spaces |
| **Multiple Algorithms** | TPE, CMA-ES, GP, NSGA-II/III samplers |
| **Distributed Optimization** | Parallel trial execution via shared storage |
| **Pruning** | Early stopping of unpromising trials |
| **Multi-Objective** | Support for optimizing multiple objectives simultaneously |
| **Persistence** | SQL databases, Redis, in-memory, or file-based storage |

The framework is production-ready (Development Status: 5 - Production/Stable) and supports Python 3.9-3.14 across Ubuntu, macOS, and Windows platforms.

**Sources:** [pyproject.toml:12-31](), [README overview in CONTRIBUTING.md:6-11]()

---

## System Architecture

The following diagram shows Optuna's layered architecture, mapping conceptual components to concrete code entities:

```mermaid
graph TB
    subgraph "User Interface"
        CLI["optuna.cli<br/>(CLI commands)"]
        CreateStudy["optuna.create_study()<br/>optuna.load_study()"]
        StudyOptimize["Study.optimize()"]
    end
    
    subgraph "Core Optimization Engine"
        Study["Study<br/>optuna/study/study.py"]
        OptimizeFunc["_optimize()<br/>optuna/study/_optimize.py"]
        Trial["Trial<br/>optuna/trial/"]
        TellFunc["_tell_with_warning()<br/>optuna/study/_tell.py"]
    end
    
    subgraph "Sampling Layer"
        BaseSampler["BaseSampler<br/>optuna/samplers/"]
        TPESampler["TPESampler"]
        GPSampler["GPSampler"]
        CmaEsSampler["CmaEsSampler"]
        NSGAIISampler["NSGA-II/III"]
    end
    
    subgraph "Storage Layer"
        BaseStorage["BaseStorage<br/>optuna/storages/"]
        RDBStorage["RDBStorage<br/>(SQLAlchemy)"]
        InMemoryStorage["InMemoryStorage"]
        CachedStorage["_CachedStorage"]
    end
    
    subgraph "Support Systems"
        Distributions["Distributions<br/>optuna/distributions.py"]
        Pruners["Pruners<br/>optuna/pruners/"]
        Integration["optuna.integration<br/>(Lazy loading)"]
    end
    
    CLI --> Study
    CreateStudy --> Study
    StudyOptimize --> OptimizeFunc
    
    Study --> BaseSampler
    Study --> BaseStorage
    OptimizeFunc --> Trial
    Trial --> Distributions
    Trial --> Pruners
    
    BaseSampler --> TPESampler
    BaseSampler --> GPSampler
    BaseSampler --> CmaEsSampler
    BaseSampler --> NSGAIISampler
    
    BaseStorage --> RDBStorage
    BaseStorage --> InMemoryStorage
    RDBStorage --> CachedStorage
    
    Study --> Integration
```

**Architecture Principles:**

1. **Pluggable Components**: `BaseSampler` and `BaseStorage` define abstract interfaces, allowing users to swap algorithms and persistence backends
2. **Define-by-Run**: The `Trial` object suggests parameters during execution, enabling dynamic search spaces
3. **Separation of Concerns**: Optimization logic (`_optimize()`), parameter suggestion (`BaseSampler`), and persistence (`BaseStorage`) are decoupled
4. **Lazy Integration**: The `optuna.integration` module uses `_IntegrationModule` for lazy imports, avoiding unnecessary dependencies

**Sources:** [optuna/study/study.py:67-98](), [optuna/study/_optimize.py:39-49](), [pyproject.toml:33-41]()

---

## Core Optimization Workflow

The optimization lifecycle follows a consistent pattern orchestrated by `Study.optimize()`:

```mermaid
sequenceDiagram
    participant User
    participant Study["Study<br/>(study.py)"]
    participant Optimize["_optimize()<br/>(_optimize.py)"]
    participant Storage["BaseStorage"]
    participant Sampler["BaseSampler"]
    participant Trial["Trial"]
    participant Objective["User's Objective<br/>Function"]
    
    User->>Study: study.optimize(objective, n_trials=100)
    Study->>Optimize: _optimize(study, func, n_trials, ...)
    
    loop For each trial
        Optimize->>Study: study.ask()
        Study->>Storage: create_new_trial(study_id)
        Storage-->>Study: trial_id
        Study->>Trial: Create Trial(study, trial_id)
        
        Study->>Sampler: infer_relative_search_space(study, trial)
        Sampler-->>Study: search_space
        
        alt Relative sampling
            Study->>Sampler: sample_relative(study, trial, search_space)
            Sampler-->>Trial: Set parameters
        end
        
        Optimize->>Objective: objective(trial)
        
        loop Parameter suggestion
            Objective->>Trial: trial.suggest_float("x", 0, 1)
            Trial->>Sampler: sample_independent(...) or use cached
            Sampler-->>Trial: parameter value
        end
        
        Objective-->>Optimize: return value
        
        Optimize->>Study: study.tell(trial, value)
        Study->>Sampler: after_trial(study, trial, state, values)
        Study->>Storage: set_trial_state_values(trial_id, state, values)
    end
```

**Workflow Stages:**

1. **Trial Creation** (`Study.ask()`): Allocates a new trial in storage, returns a `Trial` object ([optuna/study/study.py:502-586]())
2. **Parameter Sampling**: Sampler provides parameter suggestions via `sample_relative()` or `sample_independent()` 
3. **Objective Execution**: User function runs with the `Trial` object, calling `trial.suggest_*()` methods
4. **Result Recording** (`Study.tell()`): Stores trial state and objective values ([optuna/study/study.py:588-679]())
5. **Post-Processing**: Sampler's `after_trial()` hook updates internal state

**Sources:** [optuna/study/_optimize.py:39-124](), [optuna/study/_optimize.py:186-264](), [optuna/study/_tell.py:81-176]()

---

## Key Components Overview

### Study Management

The `Study` class is the primary entry point for optimization:

- **Creation**: `optuna.create_study()` initializes a study with storage, sampler, and pruner
- **Execution**: `Study.optimize(objective, n_trials)` runs the optimization loop
- **Results**: Properties like `best_params`, `best_value`, `best_trial` provide optimization results
- **Persistence**: All data is stored via the `BaseStorage` interface

**Sources:** [optuna/study/study.py:67-98](), [optuna/study/study.py:388-500]()

### Sampling Algorithms

Optuna includes sophisticated Bayesian optimization algorithms:

| Sampler | Purpose | Key Features |
|---------|---------|--------------|
| `TPESampler` | Tree-structured Parzen Estimator | Default sampler, multivariate support, MOTPE for multi-objective |
| `GPSampler` | Gaussian Process | Matern 5/2 kernel, LogEI/LogEHVI acquisition functions |
| `CmaEsSampler` | CMA-ES evolutionary strategy | Covariance matrix adaptation, SepCMA variant |
| `NSGAIISampler` | NSGA-II genetic algorithm | Multi-objective, Pareto front optimization |
| `RandomSampler` | Random sampling | Baseline comparison |

All samplers inherit from `BaseSampler` and implement `sample_independent()` and optionally `sample_relative()` for correlated parameters.

For details, see [Sampling Algorithms](#3).

**Sources:** [optuna/study/study.py:93](), [tests/samplers_tests/test_samplers.py:44-78]()

### Storage Backends

The storage layer provides persistence and distributed coordination:

| Storage | Use Case | Implementation |
|---------|----------|----------------|
| `RDBStorage` | Production deployment | SQLAlchemy-based, supports MySQL, PostgreSQL, SQLite |
| `InMemoryStorage` | Testing, single-process | No persistence, fastest performance |
| `JournalStorage` | Append-only workloads | File or Redis backend |
| `_CachedStorage` | Performance optimization | Write-through cache wrapper |

`RDBStorage` includes heartbeat monitoring for detecting stale trials in distributed environments.

For details, see [Storage Architecture](#2.4).

**Sources:** [pyproject.toml:34-38](), Diagram 3 from high-level architecture

### Trial System

The `Trial` object provides the interface for parameter suggestion:

```python
# User code example
def objective(trial: Trial) -> float:
    x = trial.suggest_float("x", -10, 10)
    y = trial.suggest_int("y", 0, 100)
    z = trial.suggest_categorical("z", ["a", "b", "c"])
    return x**2 + y - len(z)
```

Each `suggest_*()` method delegates to the sampler and records the distribution in storage. The `FrozenTrial` class represents immutable completed trials.

For details, see [Trial System and Parameter Suggestion](#2.2).

**Sources:** [tests/study_tests/test_study.py:53-57]()

### Pruning System

Pruners enable early stopping of unpromising trials:

- `MedianPruner`: Stops trials performing worse than the median
- `HyperbandPruner`: Successive halving with adaptive resource allocation
- Trials report intermediate values via `trial.report(value, step)`
- Pruners decide via `trial.should_prune()`

For details, see [Other Samplers and Pruning](#3.6).

**Sources:** [optuna/study/study.py:94]()

---

## Project Structure

The codebase follows a modular organization:

```
optuna/
├── study/              # Study, optimization loop, tell/ask
│   ├── study.py        # Study class (267.75 importance)
│   ├── _optimize.py    # Core optimization loop
│   └── _tell.py        # Result reporting logic
├── samplers/           # Sampling algorithms
│   ├── _tpe/           # TPE implementation
│   ├── _gp/            # Gaussian Process
│   └── _cmaes/         # CMA-ES
├── storages/           # Persistence layer
│   ├── _rdb/           # SQL database backend
│   └── _heartbeat.py   # Distributed trial monitoring
├── distributions.py    # Parameter distributions
├── pruners/            # Early stopping algorithms
├── integration/        # ML framework integrations
├── cli.py              # Command-line interface
└── trial/              # Trial object implementation

tests/                  # Comprehensive test suite
├── study_tests/        # Study functionality tests
├── samplers_tests/     # Sampler tests
└── storages_tests/     # Storage backend tests
```

**Build and Configuration:**

- `pyproject.toml`: Defines dependencies, optional features, and build configuration ([pyproject.toml:1-193]())
- `.pre-commit-config.yaml`: Enforces code quality via Ruff (linting/formatting) and MyPy (type checking) ([.pre-commit-config.yaml:9-48]())
- Core dependencies: SQLAlchemy, Alembic (migrations), NumPy, tqdm, PyYAML
- Optional dependencies: CMA-ES library, Plotly (visualization), Redis, scikit-learn, PyTorch

**Sources:** [pyproject.toml:112-124](), [CONTRIBUTING.md:51-90]()

---

## Development and Testing Infrastructure

Optuna maintains high code quality through:

| Component | Purpose | Tools |
|-----------|---------|-------|
| **CI/CD** | Cross-platform testing | GitHub Actions: Ubuntu, macOS, Windows |
| **Python versions** | Compatibility testing | 3.9, 3.10, 3.11, 3.12, 3.13, 3.14 |
| **Storage testing** | Backend validation | MySQL, PostgreSQL, SQLite, Redis |
| **Code quality** | Linting and formatting | Ruff, MyPy with strict type checking |
| **Test execution** | Parallel test running | pytest with `-n 8` parallelization |

The test suite includes unit tests ([tests/study_tests/test_study.py]()), integration tests, and storage-specific tests ([tests/storages_tests/test_heartbeat.py]()).

For details, see [Testing Infrastructure and CI/CD](#6.2).

**Sources:** [pyproject.toml:90-101](), [pyproject.toml:167-172](), [CONTRIBUTING.md:144-170]()

---

## Next Steps

- For core optimization mechanics, see [Study and Optimization Loop](#2.1)
- For parameter handling, see [Distributions and Search Space](#2.3)
- For algorithm details, see [Sampling Algorithms](#3)
- For production deployment, see [Storage Architecture](#2.4)
- For extending Optuna, see [Integration System](#4)

---

# Page: Core Components

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

# Page: Study and Optimization Loop

# Study and Optimization Loop

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/integration/chainermn.py](optuna/integration/chainermn.py)
- [optuna/storages/_heartbeat.py](optuna/storages/_heartbeat.py)
- [optuna/study/_dataframe.py](optuna/study/_dataframe.py)
- [optuna/study/_optimize.py](optuna/study/_optimize.py)
- [optuna/study/_tell.py](optuna/study/_tell.py)
- [optuna/study/study.py](optuna/study/study.py)
- [optuna/testing/objectives.py](optuna/testing/objectives.py)
- [tests/samplers_tests/test_samplers.py](tests/samplers_tests/test_samplers.py)
- [tests/storages_tests/test_heartbeat.py](tests/storages_tests/test_heartbeat.py)
- [tests/study_tests/test_dataframe.py](tests/study_tests/test_dataframe.py)
- [tests/study_tests/test_optimize.py](tests/study_tests/test_optimize.py)
- [tests/study_tests/test_study.py](tests/study_tests/test_study.py)
- [tests/study_tests/test_study_summary.py](tests/study_tests/test_study_summary.py)
- [tests/test_callbacks.py](tests/test_callbacks.py)

</details>



This page explains the `Study` class, the optimization loop lifecycle in `_optimize.py`, and how trials are coordinated between storage, sampling, and pruning components. For information about trial objects and parameter suggestion, see [Trial System and Parameter Suggestion](#2.2). For storage backends, see [Storage Architecture](#2.4). For sampling algorithms, see [Sampling Algorithms](#3).

## Overview

The `Study` class in [optuna/study/study.py]() is the primary interface for hyperparameter optimization. It orchestrates the optimization loop by:

1. Creating and managing trials via the storage backend
2. Delegating parameter suggestion to the sampler
3. Coordinating pruning decisions with the pruner
4. Executing the objective function with proper error handling
5. Recording trial results and managing study-level metadata

The optimization loop in [optuna/study/_optimize.py]() handles both sequential and parallel trial execution, with support for callbacks, garbage collection, progress bars, and distributed trial management via heartbeat.

## Study Class and Initialization

### Study Initialization

The `Study` class is initialized with references to key components:

```python
# From optuna/study/study.py:79-96
def __init__(
    self,
    study_name: str,
    storage: str | storages.BaseStorage,
    sampler: samplers.BaseSampler | None = None,
    pruner: pruners.BasePruner | None = None,
) -> None:
    self.study_name = study_name
    self._storage = storages.get_storage(storage)
    self._study_id = storage.get_study_id_from_name(study_name)
    self._directions = storage.get_study_directions(study_id)
    
    self.sampler = sampler or samplers.TPESampler()
    self.pruner = pruner or pruners.MedianPruner()
    
    self._thread_local = _ThreadLocalStudyAttribute()
    self._stop_flag = False
```

The study maintains a thread-local object for optimization state:

```python
# From optuna/study/study.py:62-64
class _ThreadLocalStudyAttribute(threading.local):
    in_optimize_loop: bool = False
    cached_all_trials: list[FrozenTrial] | None = None
```

Sources: [optuna/study/study.py:62-97]()

### Study Component Coordination

Title: Study Component Coordination Diagram

```mermaid
graph TB
    Study["Study"]
    Storage["BaseStorage<br/>(e.g., RDBStorage)"]
    Sampler["BaseSampler<br/>(e.g., TPESampler)"]
    Pruner["BasePruner<br/>(e.g., MedianPruner)"]
    
    OptimizeMethod["study.optimize()"]
    AskMethod["study.ask()"]
    TellMethod["study.tell()"]
    
    Study -->|"stores trials"| Storage
    Study -->|"suggests parameters"| Sampler
    Study -->|"prunes trials"| Pruner
    
    OptimizeMethod -->|"calls"| OptimizeFunc["_optimize()"]
    AskMethod -->|"creates"| Trial["Trial"]
    TellMethod -->|"finalizes"| FrozenTrial["FrozenTrial"]
    
    OptimizeFunc -->|"runs"| RunTrial["_run_trial()"]
    RunTrial -->|"uses"| AskMethod
    RunTrial -->|"uses"| TellMethod
```

Sources: [optuna/study/study.py:79-96](), [optuna/study/_optimize.py:39-49]()

### Key Study Methods

| Method | Purpose | Key Operations |
|--------|---------|----------------|
| `optimize(func, n_trials, timeout, n_jobs, ...)` | Execute optimization loop | Calls `_optimize()` which manages trial execution |
| `ask(fixed_distributions)` | Create new trial for manual control | Creates trial ID, invalidates cache, returns `Trial` |
| `tell(trial, values, state)` | Finalize trial with results | Validates values, calls `_tell_with_warning()` |
| `get_trials(deepcopy, states)` | Retrieve trials | Fetches from storage, optionally from cache |
| `enqueue_trial(params)` | Queue trial with fixed parameters | Stores as `WAITING` trial with `fixed_params` |
| `add_trial(trial)` | Add pre-evaluated trial | Validates and stores `FrozenTrial` |
| `stop()` | Exit current optimization loop | Sets `_stop_flag = True` |

Sources: [optuna/study/study.py:388-500](), [optuna/study/study.py:502-586](), [optuna/study/study.py:588-679](), [optuna/study/study.py:808-843]()

### Study Properties

| Property | Purpose | Single/Multi-Objective |
|----------|---------|------------------------|
| `best_params` | Parameters of best trial | Single-objective only |
| `best_value` | Best objective value | Single-objective only |
| `best_trial` | Best trial | Single-objective only |
| `best_trials` | Pareto front trials | Multi-objective (returns list) |
| `direction` | Optimization direction | Single-objective only |
| `directions` | List of optimization directions | Both (always returns list) |
| `trials` | All trials | Both |
| `user_attrs` | User-defined study attributes | Both |

Sources: [optuna/study/study.py:109-207](), [optuna/study/study.py:210-225]()

## Optimization Loop Architecture

### The `_optimize()` Function

The main optimization entry point in [optuna/study/_optimize.py:39-124]() orchestrates trial execution:

Title: Optimization Loop Flow

```mermaid
flowchart TD
    Start["study.optimize(func, n_trials, timeout, n_jobs, ...)"]
    SetFlag["Set study._thread_local.in_optimize_loop = True"]
    CheckJobs{"n_jobs == 1?"}
    
    Sequential["_optimize_sequential()<br/>(single thread)"]
    Parallel["ThreadPoolExecutor<br/>(n_jobs threads)"]
    
    Start --> SetFlag
    SetFlag --> CheckJobs
    CheckJobs -->|"Yes"| Sequential
    CheckJobs -->|"No"| Parallel
    
    Sequential --> LoopCheck{"Continue?<br/>(n_trials, timeout,<br/>stop_flag)"}
    Parallel --> SubmitTrials["Submit _optimize_sequential()<br/>to thread pool"]
    
    LoopCheck -->|"Yes"| RunTrial["_run_trial(study, func, catch)"]
    LoopCheck -->|"No"| Cleanup
    
    RunTrial --> Callbacks["Execute callbacks"]
    Callbacks --> UpdateProgress["Update progress bar"]
    UpdateProgress --> LoopCheck
    
    SubmitTrials --> WaitComplete["Wait for trials<br/>(FIRST_COMPLETED)"]
    WaitComplete --> CheckContinue{"Continue submitting?"}
    CheckContinue -->|"Yes"| SubmitTrials
    CheckContinue -->|"No"| Cleanup
    
    Cleanup["study._thread_local.in_optimize_loop = False<br/>progress_bar.close()"]
    Cleanup --> End["Return"]
```

Sources: [optuna/study/_optimize.py:39-124](), [optuna/study/_optimize.py:127-183]()

### Sequential Optimization: `_optimize_sequential()`

The [optuna/study/_optimize.py:127-183]() function executes trials in a loop:

1. **Set optimization flag**: `study._thread_local.in_optimize_loop = True`
2. **Reseed sampler** (if parallel): `study.sampler.reseed_rng()`
3. **Loop until termination**:
   - Check `study._stop_flag`
   - Check `n_trials` limit
   - Check `timeout` duration
   - Call `_run_trial(study, func, catch)`
   - Execute callbacks with `copy.deepcopy(frozen_trial)`
   - Update progress bar
   - Optionally run `gc.collect()` if `gc_after_trial=True`
4. **Cleanup**: `study._storage.remove_session()`

Sources: [optuna/study/_optimize.py:127-183]()

### Trial Execution: `_run_trial()`

Each trial follows this lifecycle in [optuna/study/_optimize.py:186-264]():

Title: Trial Execution Flow in `_run_trial()`

```mermaid
sequenceDiagram
    participant OptimizeLoop as "_optimize_sequential()"
    participant RunTrial as "_run_trial()"
    participant Study
    participant Storage
    participant HeartbeatThread
    participant ObjectiveFunc as "func(trial)"
    participant Tell as "_tell_with_warning()"
    
    OptimizeLoop->>RunTrial: "Call"
    RunTrial->>Study: "fail_stale_trials() if heartbeat enabled"
    RunTrial->>Study: "ask()"
    Study->>Storage: "create_new_trial()"
    Study-->>RunTrial: "Trial object"
    
    RunTrial->>HeartbeatThread: "Start heartbeat (if enabled)"
    
    RunTrial->>ObjectiveFunc: "Execute func(trial)"
    
    alt Success
        ObjectiveFunc-->>RunTrial: "Return value(s)"
        RunTrial->>RunTrial: "state=None, value_or_values=result"
    else TrialPruned
        ObjectiveFunc-->>RunTrial: "Raise TrialPruned"
        RunTrial->>RunTrial: "state=PRUNED, func_err=e"
    else Exception/KeyboardInterrupt
        ObjectiveFunc-->>RunTrial: "Raise exception"
        RunTrial->>RunTrial: "state=FAIL, func_err=e"
    end
    
    RunTrial->>HeartbeatThread: "Stop heartbeat"
    
    RunTrial->>Tell: "_tell_with_warning(trial, value_or_values, state)"
    Tell->>Study: "sampler.after_trial()"
    Tell->>Storage: "set_trial_state_values()"
    Tell-->>RunTrial: "updated_state, values, warning_message"
    
    RunTrial->>RunTrial: "Log trial result"
    
    alt state == FAIL and exception not in catch
        RunTrial-->>OptimizeLoop: "Re-raise exception"
    else
        RunTrial-->>OptimizeLoop: "Return trial_id"
    end
```

Sources: [optuna/study/_optimize.py:186-264]()

### Error Handling in `_run_trial()`

| Exception/Condition | Resulting State | Behavior |
|-------------------|----------------|----------|
| `exceptions.TrialPruned` | `PRUNED` | Caught, trial finalized with pruned state |
| `Exception` or `KeyboardInterrupt` | `FAIL` | Caught, trial finalized with fail state |
| Invalid return value (NaN, None, etc.) | `FAIL` | Detected in `_tell_with_warning()`, auto-failed |
| Exception in `catch` parameter | `FAIL` | Trial marked failed, optimization continues |
| Exception not in `catch` | `FAIL` | Trial marked failed, exception re-raised |

Sources: [optuna/study/_optimize.py:204-263]()

## Parallel Optimization with ThreadPoolExecutor

When `n_jobs != 1`, the optimization uses [optuna/study/_optimize.py:67-121]() with a `ThreadPoolExecutor`:

1. **Worker pool creation**: `ThreadPoolExecutor(max_workers=n_jobs)`
2. **Trial submission loop**:
   - Check `study._stop_flag`
   - Check `timeout` against `time_start`
   - Check `n_trials` limit
   - Wait for completion when pool is full using `wait(futures, return_when=FIRST_COMPLETED)`
   - Submit new `_optimize_sequential(study, func, 1, ...)` tasks
3. **RNG reseeding**: Each worker thread calls `study.sampler.reseed_rng()` for thread-safety

### Thread Safety Considerations

- **Storage synchronization**: All storage operations are atomic via the storage backend
- **Sampler reseeding**: Each worker reseeds the sampler's RNG via `reseed_rng=True`
- **Trial cache invalidation**: Cache is thread-local and invalidated per-trial
- **Stop flag**: `study._stop_flag` is a simple boolean flag checked by all workers

Sources: [optuna/study/_optimize.py:67-121](), [optuna/study/_optimize.py:142-143]()

### Progress Bar and Logging

Progress bar support in [optuna/study/_optimize.py:58-62]():

- **Enabled when**: `show_progress_bar=True` and `n_trials` is set
- **Disabled when**: `timeout` is set with `n_jobs != 1` (cannot estimate progress)
- **Updates after each trial**: Shows best trial, best value, elapsed time
- **Implementation**: `pbar_module._ProgressBar` class

Sources: [optuna/study/_optimize.py:58-62](), [optuna/study/_optimize.py:179-181]()

## Ask and Tell Pattern

The ask-and-tell pattern in [optuna/study/study.py:502-679]() provides manual control over trial lifecycle, as an alternative to `optimize()`.

### Ask Method: `study.ask()`

The [optuna/study/study.py:502-586]() method creates a new trial:

1. **Check heartbeat warning**: Warns if heartbeat is enabled but not using `optimize()`
2. **Convert distributions**: Converts old distribution formats to new format
3. **Invalidate cache**: `self._thread_local.cached_all_trials = None`
4. **Get or create trial**: 
   - Calls `self._pop_waiting_trial_id()` to check for enqueued trials
   - If none, calls `self._storage.create_new_trial(self._study_id)`
5. **Create Trial object**: `optuna.Trial(self, trial_id)`
6. **Apply fixed distributions**: Calls `trial._suggest(name, param)` for each
7. **Return mutable Trial**: User can now call `suggest_*()` methods

### Tell Method: `study.tell()`

The [optuna/study/study.py:588-679]() method finalizes a trial:

1. **Delegate to `_tell_with_warning()`**: Main logic in [optuna/study/_tell.py:81-176]()
2. **Return deep copy**: `copy.deepcopy(_get_frozen_trial(study, trial))`

The `_tell_with_warning()` function in [optuna/study/_tell.py:81-176]():

1. **Invalidate cache**: `study._thread_local.cached_all_trials = None`
2. **Get frozen trial**: Retrieves from storage, validates state is `RUNNING`
3. **Validate state and values**: Checks consistency via `_check_state_and_values()`
4. **Handle special cases**:
   - If `state=None`, attempt to auto-determine from values
   - If `state=PRUNED`, use last intermediate value if available
   - If values invalid, auto-fail with `state=FAIL`
5. **Cast values to floats**: Ensures type consistency
6. **Post-processing**:
   - Call `study.sampler.after_trial(study, frozen_trial, state, values)`
   - Call `study._storage.set_trial_state_values(trial_id, state, values)`
7. **Return**: `(state, values, warning_message)`

Sources: [optuna/study/study.py:502-679](), [optuna/study/_tell.py:23-176]()

### Ask and Tell Usage Example

```python
# Manual optimization loop
for _ in range(100):
    trial = study.ask()
    
    # Get parameters
    x = trial.suggest_float("x", -10, 10)
    y = trial.suggest_int("y", 0, 100)
    
    # Evaluate objective
    value = x**2 + y
    
    # Report result
    study.tell(trial, value)
```

### Fixed Distributions in Ask

The `ask()` method supports pre-suggesting parameters via `fixed_distributions`:

```python
distributions = {
    "lr": FloatDistribution(0.001, 0.1, log=True),
    "batch_size": CategoricalDistribution([32, 64, 128])
}

trial = study.ask(fixed_distributions=distributions)
# trial.params already contains "lr" and "batch_size"
```

Sources: [optuna/study/study.py:555-584]()

## Trial Enqueuing and Pre-evaluation

### Enqueuing Trials with Fixed Parameters

The [optuna/study/study.py:845-908]() method queues trials with specific parameter values:

```python
study.enqueue_trial(params={"x": 5, "lr": 0.001})
```

Implementation:
1. **Validate params**: Must be a dictionary
2. **Check skip condition**: If `skip_if_exists=True`, checks for duplicate trials
3. **Create waiting trial**: Calls `study.add_trial()` with:
   - `state=TrialState.WAITING`
   - `system_attrs={"fixed_params": params}`
   - `user_attrs=user_attrs` (if provided)

When `ask()` is called, it checks for waiting trials via `_pop_waiting_trial_id()` before creating new trials.

Sources: [optuna/study/study.py:845-908]()

### Adding Pre-evaluated Trials

The [optuna/study/study.py:910-980]() method adds completed trials to a study:

```python
from optuna.trial import create_trial

trial = create_trial(
    params={"x": 2.0},
    distributions={"x": FloatDistribution(0, 10)},
    value=4.0
)
study.add_trial(trial)
```

This is useful for:
- Importing results from other optimization runs
- Warm-starting optimization with known good parameters
- Transferring trials between studies

Sources: [optuna/study/study.py:910-980]()

## Heartbeat Mechanism for Distributed Trials

When the storage backend supports heartbeat (e.g., `RDBStorage` with `heartbeat_interval` set), the system monitors trial liveness:

### Heartbeat Thread

The [optuna/storages/_heartbeat.py:105-133]() class runs in the background during trial execution:

1. **Started by `_run_trial()`**: Via `get_heartbeat_thread(trial_id, storage)` context manager
2. **Periodic updates**: Calls `storage.record_heartbeat(trial_id)` every `heartbeat_interval` seconds
3. **Stopped after trial**: When the objective function returns or raises

### Stale Trial Detection

The [optuna/storages/_heartbeat.py:143-181]() function:

1. **Called before each trial**: In `_run_trial()` via `fail_stale_trials(study)`
2. **Identifies stale trials**: Trials whose heartbeat has not updated within `grace_period`
3. **Marks as failed**: Sets `state=TrialState.FAIL`
4. **Executes callback**: Calls `failed_trial_callback` if configured

This enables automatic recovery from worker crashes in distributed optimization.

Sources: [optuna/storages/_heartbeat.py:105-181](), [optuna/study/_optimize.py:191-195]()

## Callbacks and Extensibility

### Optimization Callbacks

The optimization loop supports callbacks that are invoked after each trial:

```python
def callback(study: Study, trial: FrozenTrial) -> None:
    if trial.number >= 10:
        study.stop()

study.optimize(objective, callbacks=[callback])
```

### Study Termination

The optimization can be stopped via:
- `study.stop()` method (sets internal flag)
- Reaching `n_trials` limit
- Reaching `timeout` duration
- Unhandled exceptions (depending on `catch` parameter)

Sources: [optuna/study/study.py:807-842](), [optuna/study/_optimize.py:170-172](), [optuna/study/_optimize.py:146-158]()

---

# Page: Trial System and Parameter Suggestion

# Trial Objects and Parameter Suggestion

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
- [tests/storages_tests/test_heartbeat.py](tests/storages_tests/test_heartbeat.py)
- [tests/study_tests/test_dataframe.py](tests/study_tests/test_dataframe.py)
- [tests/study_tests/test_optimize.py](tests/study_tests/test_optimize.py)
- [tests/study_tests/test_study.py](tests/study_tests/test_study.py)
- [tests/study_tests/test_study_summary.py](tests/study_tests/test_study_summary.py)
- [tests/test_callbacks.py](tests/test_callbacks.py)
- [tests/test_distributions.py](tests/test_distributions.py)

</details>



This page documents the trial objects in Optuna and how parameter suggestion works. It covers the `Trial`, `FrozenTrial`, and `FixedTrial` classes, the `suggest_*` methods for defining search spaces, and the interaction between trials and samplers through relative and independent sampling strategies.

For information about the Study orchestration and optimization loop, see [Study and Optimization Loop](#2.1). For details about distribution objects and search space definition, see [Distributions and Parameter Space](#2.3). For sampler algorithms, see [Sampling Algorithms](#3).

## Trial Class Hierarchy

Optuna provides three main trial classes that share a common interface defined by `BaseTrial`:

| Class | Purpose | Mutability | Use Case |
|-------|---------|------------|----------|
| `Trial` | Active trial during optimization | Mutable | Passed to objective functions in `study.optimize()` |
| `FrozenTrial` | Immutable snapshot of completed trial | Immutable | Historical trial records, returned by `study.trials` |
| `FixedTrial` | Trial with pre-defined parameters | Mutable | Deploying optimization results, testing objective functions |

### Class Hierarchy Diagram

```mermaid
graph TB
    BaseTrial["BaseTrial<br/>(optuna/trial/_base.py)"]
    Trial["Trial<br/>(optuna/trial/_trial.py)"]
    FrozenTrial["FrozenTrial<br/>(optuna/trial/_frozen.py)"]
    FixedTrial["FixedTrial<br/>(optuna/trial/_fixed.py)"]
    
    BaseTrial --> Trial
    BaseTrial --> FrozenTrial
    BaseTrial --> FixedTrial
    
    BaseTrial -.defines.-> SuggestMethods["suggest_float()<br/>suggest_int()<br/>suggest_categorical()<br/>report()<br/>should_prune()"]
    
    Trial -.has.-> TrialState["_cached_frozen_trial<br/>_trial_id<br/>storage<br/>relative_params"]
    FrozenTrial -.has.-> FrozenState["number<br/>state<br/>value/values<br/>params<br/>distributions<br/>intermediate_values"]
    FixedTrial -.has.-> FixedState["_params<br/>_suggested_params<br/>_distributions"]
```

**Sources:** [optuna/trial/_base.py:17-133](), [optuna/trial/_trial.py:31-48](), [optuna/trial/_frozen.py:33-139](), [optuna/trial/_fixed.py:24-60]()

## Trial Object Creation and Lifecycle

### Trial Creation Flow

Trials are created through the `Study.ask()` method, which is called internally by `Study.optimize()` or explicitly by users in the ask-and-tell interface.

```mermaid
sequenceDiagram
    participant User
    participant Study
    participant Storage
    participant Trial
    participant Sampler
    
    User->>Study: optimize(objective, n_trials)
    Study->>Study: _run_trial()
    Study->>Study: ask()
    
    Study->>Storage: create_new_trial(study_id)
    Storage-->>Study: trial_id
    
    Study->>Trial: __init__(study, trial_id)
    Trial->>Storage: get_trial(trial_id)
    Storage-->>Trial: cached_frozen_trial
    
    Trial->>Sampler: before_trial(study, frozen_trial)
    
    Study-->>User: trial
    
    User->>Trial: suggest_float("x", 0, 1)
    User->>Trial: suggest_int("y", 1, 10)
    User-->>Study: return objective_value
    
    Study->>Storage: set_trial_state_values(trial_id, COMPLETE, values)
    Study->>Sampler: after_trial(study, frozen_trial, state, values)
```

**Sources:** [optuna/study/study.py:502-586](), [optuna/trial/_trial.py:50-60](), [optuna/study/_optimize.py:186-264]()

### Trial States

Trials progress through various states during their lifecycle:

- **RUNNING**: Trial is actively being evaluated
- **COMPLETE**: Trial finished successfully with a value
- **PRUNED**: Trial was stopped early by a pruner
- **FAIL**: Trial raised an exception
- **WAITING**: Trial is queued but not started (used by `enqueue_trial`)

**Sources:** [optuna/trial/_state.py]()

## Parameter Suggestion Mechanism

### The suggest_* Methods

The `Trial` class provides three main methods for suggesting hyperparameters:

1. **`suggest_float(name, low, high, *, step=None, log=False)`**: Suggests a floating-point value
2. **`suggest_int(name, low, high, *, step=1, log=False)`**: Suggests an integer value  
3. **`suggest_categorical(name, choices)`**: Suggests a categorical value from choices

Each method:
- Creates a `Distribution` object to define the parameter space
- Calls the internal `_suggest()` method to get the value
- Validates the distribution compatibility if the parameter was already suggested
- Returns the suggested value

### Parameter Suggestion Workflow

```mermaid
graph TB
    UserCode["User calls<br/>trial.suggest_float('x', 0, 1)"]
    CreateDist["Create FloatDistribution(0, 1)"]
    CallSuggest["Call _suggest('x', distribution)"]
    
    CheckExisting{"Parameter<br/>already<br/>suggested?"}
    CheckCompat["check_distribution_compatibility()"]
    ReturnExisting["Return existing<br/>params['x']"]
    
    CheckFixed{"Is fixed<br/>param?"}
    ReturnFixed["Return _fixed_params['x']"]
    
    CheckSingle{"Is single<br/>value?"}
    ReturnSingle["Return single value"]
    
    CheckRelative{"Is relative<br/>param?"}
    GetRelative["Get from relative_params"]
    
    SampleIndependent["sampler.sample_independent()"]
    
    StoreParam["storage.set_trial_param()<br/>Update cached_frozen_trial"]
    ReturnValue["Return param_value"]
    
    UserCode --> CreateDist
    CreateDist --> CallSuggest
    CallSuggest --> CheckExisting
    
    CheckExisting -->|Yes| CheckCompat
    CheckCompat --> ReturnExisting
    
    CheckExisting -->|No| CheckFixed
    CheckFixed -->|Yes| ReturnFixed
    CheckFixed -->|No| CheckSingle
    CheckSingle -->|Yes| ReturnSingle
    CheckSingle -->|No| CheckRelative
    CheckRelative -->|Yes| GetRelative
    CheckRelative -->|No| SampleIndependent
    
    ReturnFixed --> StoreParam
    ReturnSingle --> StoreParam
    GetRelative --> StoreParam
    SampleIndependent --> StoreParam
    StoreParam --> ReturnValue
```

**Sources:** [optuna/trial/_trial.py:78-165](), [optuna/trial/_trial.py:618-648]()

### Internal _suggest() Implementation

The `_suggest()` method at [optuna/trial/_trial.py:618-648]() implements the core parameter suggestion logic:

1. **Check if already suggested**: If `name in trial.distributions`, return existing value after compatibility check
2. **Check fixed params**: If parameter was fixed via `enqueue_trial()`, return `_fixed_params[name]`
3. **Check single-value distribution**: If distribution has only one possible value, return it
4. **Check relative sampling**: If parameter is in `relative_search_space`, return `relative_params[name]`
5. **Fall back to independent sampling**: Call `sampler.sample_independent(study, trial, name, distribution)`

After obtaining the value, the method:
- Converts to internal representation via `distribution.to_internal_repr()`
- Stores in storage via `storage.set_trial_param()`
- Updates `_cached_frozen_trial` for consistency

**Sources:** [optuna/trial/_trial.py:618-648]()

## Relative vs Independent Sampling

Samplers can suggest parameters using two strategies:

### Relative Sampling

Relative sampling suggests **all parameters together** as a single vector, allowing the sampler to model dependencies between parameters.

**How it works:**
1. Sampler inspects past trials via `infer_relative_search_space()`
2. Returns a search space dictionary mapping parameter names to distributions
3. Samples all parameters at once via `sample_relative()`
4. Trial stores results in `relative_params` property

**When used:**
- TPESampler uses relative sampling for parameters in the relative search space
- CmaEsSampler always uses relative sampling (continuous optimization)
- Parameters must be consistent across trials (same distributions)

### Independent Sampling

Independent sampling suggests **one parameter at a time**, treating each as independent.

**When used:**
- Parameters not in the relative search space
- First occurrence of a parameter (no history)
- Samplers that don't support relative sampling (e.g., RandomSampler)
- Conditional parameters that appear only in some trials

### Decision Flow

```mermaid
graph TB
    SuggestParam["trial.suggest_float('x', 0, 1)"]
    CheckInDist{"'x' in<br/>trial.distributions?"}
    ReturnExisting["Return existing value"]
    
    CheckFixed{"'x' in<br/>_fixed_params?"}
    ReturnFixed["Return fixed value"]
    
    EvalRelative["Evaluate relative_params<br/>(lazy property)"]
    InferSpace["sampler.infer_relative_search_space()"]
    SampleRelative["sampler.sample_relative()"]
    StoreRelative["Store all params in relative_params"]
    
    CheckInRelative{"'x' in<br/>relative_search_space?"}
    ReturnRelative["Return relative_params['x']"]
    
    SampleIndep["sampler.sample_independent(name='x')"]
    ReturnIndep["Return sampled value"]
    
    SuggestParam --> CheckInDist
    CheckInDist -->|Yes| ReturnExisting
    CheckInDist -->|No| CheckFixed
    CheckFixed -->|Yes| ReturnFixed
    CheckFixed -->|No| EvalRelative
    
    EvalRelative --> InferSpace
    InferSpace --> SampleRelative
    SampleRelative --> StoreRelative
    StoreRelative --> CheckInRelative
    
    CheckInRelative -->|Yes| ReturnRelative
    CheckInRelative -->|No| SampleIndep
    SampleIndep --> ReturnIndep
```

**Sources:** [optuna/trial/_trial.py:67-76](), [optuna/trial/_trial.py:618-648](), [optuna/trial/_trial.py:667-673]()

### Relative Params Lazy Evaluation

The `relative_params` property at [optuna/trial/_trial.py:67-76]() is evaluated lazily:

```python
@property
def relative_params(self) -> dict[str, Any]:
    if self._relative_params is None:
        study = pruners._filter_study(self.study, self._cached_frozen_trial)
        self.relative_search_space = self.study.sampler.infer_relative_search_space(
            study, self._cached_frozen_trial
        )
        self._relative_params = self.study.sampler.sample_relative(
            study, self._cached_frozen_trial, self.relative_search_space
        )
    return self._relative_params
```

This ensures that:
- Relative sampling happens only when needed
- The search space is as up-to-date as possible
- Multiple parameters can be accessed without recomputing

**Sources:** [optuna/trial/_trial.py:67-76]()

## Trial State Management

### Reporting Intermediate Values

The `report(value, step)` method allows trials to report intermediate objective values during evaluation, typically for pruning decisions:

```python
def objective(trial):
    for epoch in range(100):
        # Train model
        intermediate_value = evaluate_model()
        trial.report(intermediate_value, step=epoch)
        
        if trial.should_prune():
            raise optuna.TrialPruned()
```

**Implementation details:**
- Converts value to `float` (supports numpy types)
- Validates step is non-negative integer
- Ignores duplicate reports for same step (warns user)
- Stores via `storage.set_trial_intermediate_value(trial_id, step, value)`
- Updates `_cached_frozen_trial.intermediate_values[step]`

**Sources:** [optuna/trial/_trial.py:410-509]()

### Pruning Decision

The `should_prune()` method at [optuna/trial/_trial.py:511-541]() asks the pruner whether to stop the trial:

1. Gets latest trial state via `_get_latest_trial()`
2. Calls `study.pruner.prune(study, trial)`
3. Returns boolean indicating whether to prune

Users typically raise `TrialPruned` exception when `should_prune()` returns `True`.

**Sources:** [optuna/trial/_trial.py:511-541]()

### User and System Attributes

Trials support setting custom metadata:

- **User attributes**: `set_user_attr(key, value)` - for user-defined metadata
- **System attributes**: `set_system_attr(key, value)` - for internal Optuna use (deprecated for users)

Both methods:
- Store via storage backend
- Update `_cached_frozen_trial` for local access
- Require JSON-serializable values

**Sources:** [optuna/trial/_trial.py:543-616]()

## FrozenTrial: Immutable Trial Records

`FrozenTrial` represents an immutable snapshot of a trial, used for:
- Accessing historical trials via `study.trials`
- Returning from `study.best_trial`
- Passing to callbacks and samplers

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `number` | int | Unique trial number (zero-based) |
| `state` | TrialState | Trial state (RUNNING, COMPLETE, etc.) |
| `value` | float \| None | Single-objective value |
| `values` | list[float] \| None | Multi-objective values |
| `params` | dict[str, Any] | Suggested parameter values |
| `distributions` | dict[str, BaseDistribution] | Parameter distributions |
| `user_attrs` | dict[str, Any] | User-defined attributes |
| `system_attrs` | dict[str, Any] | System attributes |
| `intermediate_values` | dict[int, float] | Reported intermediate values |
| `datetime_start` | datetime | Trial start time |
| `datetime_complete` | datetime \| None | Trial completion time |

### Suggest Methods Return Pre-defined Values

Unlike `Trial`, `FrozenTrial.suggest_*()` methods return values from the `params` dictionary:

```python
def _suggest(self, name: str, distribution: BaseDistribution) -> Any:
    if name not in self._params:
        raise ValueError(
            "The value of the parameter '{}' is not found. Please set it at "
            "the construction of the FrozenTrial object.".format(name)
        )
    
    value = self._params[name]
    # Validate and warn if out of range
    # Update distributions
    return value
```

This allows objective functions to accept both `Trial` and `FrozenTrial` objects, enabling re-evaluation of past trials.

**Sources:** [optuna/trial/_frozen.py:348-368]()

### Pruning Behavior

`FrozenTrial` never prunes:
- `report(value, step)` does nothing (no-op)
- `should_prune()` always returns `False`

This makes sense because `FrozenTrial` represents already-completed trials that cannot be pruned.

**Sources:** [optuna/trial/_frozen.py:266-299]()

### Creating FrozenTrials

The `create_trial()` function at [optuna/trial/_frozen.py:482-592]() creates `FrozenTrial` objects manually:

```python
trial = optuna.trial.create_trial(
    params={"x": 1.0, "y": 0},
    distributions={
        "x": FloatDistribution(0, 10),
        "y": CategoricalDistribution([-1, 0, 1]),
    },
    value=5.0,
)
```

Used with `study.add_trial()` to import external optimization results.

**Sources:** [optuna/trial/_frozen.py:482-592]()

## FixedTrial: Deployment and Testing

`FixedTrial` provides a lightweight trial object for deploying optimization results or testing objective functions with specific parameters.

### Constructor

```python
trial = optuna.trial.FixedTrial(
    params={"x": 1.0, "y": "option_a"},
    number=42
)
```

### Suggest Behavior

Unlike `FrozenTrial`, `FixedTrial`:
- Accepts any parameter name (not limited to pre-defined set)
- Warns if value is outside distribution range
- Tracks which parameters were actually suggested via `_suggested_params`
- Updates `_distributions` as parameters are suggested

### Use Cases

1. **Deployment**: Run objective function with best trial parameters
2. **Testing**: Verify objective function with specific parameter combinations
3. **Analysis**: Evaluate objective at multiple fixed points

**Example:**
```python
def objective(trial):
    x = trial.suggest_float("x", -1, 1)
    return x**2

study = optuna.create_study()
study.optimize(objective, n_trials=10)

# Deploy best parameters
best_trial = optuna.trial.FixedTrial(study.best_params)
result = objective(best_trial)
```

**Sources:** [optuna/trial/_fixed.py:24-188]()

## Integration with Study and Samplers

### Trial Creation in Study.ask()

The `Study.ask()` method at [optuna/study/study.py:502-586]() creates trials:

1. Checks for waiting trials (from `enqueue_trial`)
2. Creates new trial via `storage.create_new_trial(study_id)`
3. Constructs `Trial` object
4. Applies fixed distributions if provided
5. Calls `sampler.before_trial()`

### Trial Completion in Study.tell()

The `Study.tell()` method at [optuna/study/study.py:588-679]() completes trials:

1. Validates trial state and values
2. Converts values to list of floats
3. Calls `sampler.after_trial()` for sampler cleanup
4. Stores final state via `storage.set_trial_state_values()`

**Sources:** [optuna/study/study.py:502-586](), [optuna/study/study.py:588-679](), [optuna/study/_tell.py:81-176]()

### Ask-and-Tell Interface Diagram

```mermaid
graph TB
    Ask["study.ask()"]
    PopWaiting["_pop_waiting_trial_id()"]
    CreateNew["storage.create_new_trial()"]
    ConstructTrial["Trial(study, trial_id)"]
    ApplyFixed["Apply fixed_distributions"]
    BeforeTrial["sampler.before_trial()"]
    ReturnTrial["Return trial"]
    
    Tell["study.tell(trial, values)"]
    ValidateState["Validate state and values"]
    AfterTrial["sampler.after_trial()"]
    SetState["storage.set_trial_state_values()"]
    ReturnFrozen["Return FrozenTrial"]
    
    Ask --> PopWaiting
    PopWaiting --> CreateNew
    CreateNew --> ConstructTrial
    ConstructTrial --> ApplyFixed
    ApplyFixed --> BeforeTrial
    BeforeTrial --> ReturnTrial
    
    Tell --> ValidateState
    ValidateState --> AfterTrial
    AfterTrial --> SetState
    SetState --> ReturnFrozen
```

**Sources:** [optuna/study/study.py:502-586](), [optuna/study/study.py:588-679]()

## Summary

The trial system in Optuna provides a flexible interface for parameter suggestion and trial management:

- **Trial**: Active, mutable trial object with full sampler integration
- **FrozenTrial**: Immutable snapshot for historical records and analysis
- **FixedTrial**: Lightweight object for deployment and testing

Parameter suggestion flows through a priority system:
1. Existing parameters (avoid re-suggestion)
2. Fixed parameters (from `enqueue_trial`)
3. Single-value distributions
4. Relative sampling (all parameters together)
5. Independent sampling (one parameter at a time)

The distinction between relative and independent sampling allows samplers to choose the appropriate strategy based on their algorithm and the optimization context.

---

# Page: Distributions and Search Space

# Distributions and Search Space

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/distributions.py](optuna/distributions.py)
- [optuna/integration/pytorch_distributed.py](optuna/integration/pytorch_distributed.py)
- [optuna/trial/_base.py](optuna/trial/_base.py)
- [optuna/trial/_fixed.py](optuna/trial/_fixed.py)
- [optuna/trial/_frozen.py](optuna/trial/_frozen.py)
- [optuna/trial/_trial.py](optuna/trial/_trial.py)
- [tests/test_distributions.py](tests/test_distributions.py)

</details>



## Purpose and Scope

This document explains Optuna's distribution system, which defines the search space for hyperparameter optimization. Distributions specify the type, range, and structure of parameters that samplers can suggest during optimization trials.

For information about how trials use distributions to suggest parameter values, see [Trial System and Parameter Suggestion](#2.2). For details on sampling algorithms that operate over these distributions, see [BaseSampler Interface and Sampling Strategies](#3.1).

---

## Distribution Class Hierarchy

Optuna provides a type-safe distribution system based on an abstract base class. All distributions implement the `BaseDistribution` interface and specify how parameter values are represented, validated, and stored.

### Distribution Type Overview

```mermaid
classDiagram
    class BaseDistribution {
        <<abstract>>
        +to_external_repr(float) Any
        +to_internal_repr(Any) float
        +single() bool
        +_contains(float) bool
        +_asdict() dict
    }
    
    class FloatDistribution {
        +float low
        +float high
        +bool log
        +float|None step
        +to_external_repr(float) float
        +to_internal_repr(float) float
    }
    
    class IntDistribution {
        +int low
        +int high
        +bool log
        +int step
        +to_external_repr(float) int
        +to_internal_repr(int) float
    }
    
    class CategoricalDistribution {
        +tuple choices
        +to_external_repr(float) CategoricalChoiceType
        +to_internal_repr(CategoricalChoiceType) float
    }
    
    BaseDistribution <|-- FloatDistribution
    BaseDistribution <|-- IntDistribution
    BaseDistribution <|-- CategoricalDistribution
```

**Sources:** [optuna/distributions.py:31-107]()

### Distribution Instantiation Flow

```mermaid
sequenceDiagram
    participant User as "Objective Function"
    participant Trial as "Trial"
    participant Dist as "Distribution"
    participant Sampler as "Sampler"
    
    User->>Trial: suggest_float("lr", 1e-5, 1e-1, log=True)
    Trial->>Dist: FloatDistribution(1e-5, 1e-1, log=True)
    Dist->>Dist: Validate parameters
    Trial->>Trial: _suggest(name, distribution)
    Trial->>Sampler: sample_independent(..., distribution)
    Sampler-->>Trial: param_value (external repr)
    Trial->>Dist: to_internal_repr(param_value)
    Dist-->>Trial: internal_repr (float)
    Trial->>Trial: storage.set_trial_param(...)
    Trial-->>User: param_value
```

**Sources:** [optuna/trial/_trial.py:78-165](), [optuna/trial/_trial.py:618-647]()

---

## FloatDistribution

The `FloatDistribution` class defines continuous parameter spaces over floating-point values.

### Parameters

| Parameter | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `low` | float | Lower bound (inclusive) | Must be ≤ `high`. If `log=True`, must be > 0 |
| `high` | float | Upper bound (inclusive) | Must be ≥ `low` |
| `log` | bool | Sample in log domain | Cannot be used with `step` |
| `step` | float \| None | Discretization step | Must be > 0. Cannot be used with `log` |

### Domain Types

**Linear Domain** (`log=False`):
- Samples uniformly from `[low, high]`
- Example: `FloatDistribution(0.0, 1.0)` samples from uniform distribution

**Log Domain** (`log=True`):
- Samples uniformly in log space
- Example: `FloatDistribution(1e-5, 1e-1, log=True)` for learning rates
- Constraint: `low > 0`

**Discretized** (`step` specified):
- Samples from `{low, low+step, low+2*step, ..., high}`
- If range not divisible by step, `high` is adjusted down
- Example: `FloatDistribution(0.0, 1.0, step=0.1)` samples {0.0, 0.1, ..., 1.0}

### Validation and Range Adjustment

When `step` is specified and the range `[low, high]` is not evenly divisible, Optuna automatically adjusts the upper bound:

```mermaid
graph LR
    A["FloatDistribution(1.0, 9.0, step=2.0)"] --> B["Calculate: (9.0 - 1.0) % 2.0 ≠ 0"]
    B --> C["Adjust: high = 8.0"]
    C --> D["Valid range: {1.0, 3.0, 5.0, 7.0}"]
    C --> E["Warning emitted"]
```

**Sources:** [optuna/distributions.py:109-198](), [optuna/distributions.py:661-676]()

---

## IntDistribution

The `IntDistribution` class defines discrete parameter spaces over integer values.

### Parameters

| Parameter | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `low` | int | Lower bound (inclusive) | Must be ≤ `high`. If `log=True`, must be ≥ 1 |
| `high` | int | Upper bound (inclusive) | Must be ≥ `low` |
| `log` | bool | Sample in log domain | Requires `step=1` |
| `step` | int | Discretization step | Must be > 0. Must be 1 if `log=True` |

### Log-Scale Integer Sampling

When `log=True`, integer values are sampled using a special process:

1. The range `[low, high]` is divided into grid points of width 1
2. Values are sampled uniformly in log domain
3. The sampled value is rounded to the nearest grid point
4. Lower values are sampled more frequently than higher values

Example: `IntDistribution(2, 8, log=True)` samples from `{2, 3, 4, 5, 6, 7, 8}` with bias toward lower values.

### Step Parameter Behavior

The `step` parameter allows sampling with larger intervals:

```mermaid
graph TD
    A["IntDistribution(1, 10, step=3)"] --> B["Initial range: [1, 10]"]
    B --> C["Compute: (10-1) % 3 = 0"]
    C --> D["Valid samples: {1, 4, 7, 10}"]
    
    E["IntDistribution(1, 10, step=2)"] --> F["Initial range: [1, 10]"]
    F --> G["Compute: (10-1) % 2 ≠ 0"]
    G --> H["Adjust high: 9"]
    H --> I["Valid samples: {1, 3, 5, 7, 9}"]
```

**Sources:** [optuna/distributions.py:310-393](), [optuna/distributions.py:679-688]()

---

## CategoricalDistribution

The `CategoricalDistribution` class defines discrete parameter spaces over arbitrary choices.

### Choice Types

Supported choice types (for persistent storage compatibility):
- `None`
- `bool`
- `int`
- `float`
- `str`

Other types can be used but may not work with all storage backends.

### Internal Representation

Categorical values are stored internally as indices:

```mermaid
graph LR
    A["choices = ['adam', 'sgd', 'rmsprop']"] --> B["External: 'sgd'"]
    B --> C["to_internal_repr()"]
    C --> D["Internal: 1.0"]
    D --> E["Storage saves: 1.0"]
    
    F["Storage loads: 1.0"] --> G["to_external_repr()"]
    G --> H["External: 'sgd'"]
```

**Key Implementation Detail:** The internal representation is the index as a float, which allows categorical parameters to use the same storage schema as continuous parameters.

### NaN Handling

Categorical distributions support `float('nan')` as a choice and handle it specially:

```python
# When checking equality, NaN is handled correctly
choices = [1.0, float('nan'), 3.0]
dist = CategoricalDistribution(choices)
# Both NaN values are considered equal in this context
```

**Sources:** [optuna/distributions.py:470-551](), [optuna/distributions.py:457-467]()

---

## Internal vs External Representation

Distributions maintain two representations of parameter values to enable efficient storage and sampling.

### Representation Conversion

```mermaid
graph TB
    subgraph "External Representation (User-Facing)"
        E1["int: 42"]
        E2["float: 0.01"]
        E3["str: 'adam'"]
    end
    
    subgraph "Internal Representation (Storage)"
        I1["float: 42.0"]
        I2["float: 0.01"]
        I3["float: 0.0 (index)"]
    end
    
    E1 -->|to_internal_repr| I1
    I1 -->|to_external_repr| E1
    
    E2 -->|to_internal_repr| I2
    I2 -->|to_external_repr| E2
    
    E3 -->|to_internal_repr| I3
    I3 -->|to_external_repr| E3
```

### Why Two Representations?

| Aspect | External Representation | Internal Representation |
|--------|------------------------|-------------------------|
| **Purpose** | User-facing API | Storage and sampling |
| **Type** | Matches distribution type | Always `float` |
| **Usage** | Objective function parameters | Database storage, sampler input |
| **Examples** | `int`, `str`, `float` | `float` |

### Conversion Methods

**`to_internal_repr(param_value_in_external_repr: Any) -> float`**
- Converts user-provided values to internal float representation
- Validates the value (e.g., rejects NaN for non-categorical)
- Used when storing parameter values

**`to_external_repr(param_value_in_internal_repr: float) -> Any`**
- Converts internal float to user-facing type
- Used when retrieving parameter values
- For `IntDistribution`: `int(internal_repr)`
- For `CategoricalDistribution`: `choices[int(internal_repr)]`

**Sources:** [optuna/distributions.py:38-63](), [optuna/distributions.py:182-198](), [optuna/distributions.py:362-380](), [optuna/distributions.py:506-522]()

---

## Distribution Validation

### Single-Value Distributions

A distribution is considered "single" if it contains only one valid value. The `single()` method determines this:

```mermaid
graph TD
    A["Distribution.single()"] --> B{"Type?"}
    B -->|Float/Int| C{"low == high?"}
    C -->|Yes| D{"Has step?"}
    D -->|No| E["True: Single value"]
    D -->|Yes| F{"(high-low) < step?"}
    F -->|Yes| E
    F -->|No| G["False: Multiple values"]
    C -->|No| G
    
    B -->|Categorical| H{"len(choices) == 1?"}
    H -->|Yes| E
    H -->|No| G
```

When a distribution is single-valued, samplers skip sampling and directly return the only valid value.

### Contains Check

The `_contains(param_value_in_internal_repr: float) -> bool` method validates whether a value is within the distribution's range:

**FloatDistribution:**
```python
# Without step
return low <= value <= high

# With step
k = (value - low) / step
return low <= value <= high and abs(k - round(k)) < 1e-8
```

**IntDistribution:**
```python
return low <= value <= high and (value - low) % step == 0
```

**CategoricalDistribution:**
```python
index = int(param_value_in_internal_repr)
return 0 <= index < len(choices)
```

**Sources:** [optuna/distributions.py:66-89](), [optuna/distributions.py:163-181](), [optuna/distributions.py:382-392](), [optuna/distributions.py:524-529]()

---

## Distribution Compatibility

Distribution compatibility checking ensures that parameter names are used consistently across trials in a study.

### Compatibility Rules

```mermaid
graph TD
    A["check_distribution_compatibility(old, new)"] --> B{"Same class?"}
    B -->|No| C["ValueError: Different distribution kind"]
    B -->|Yes| D{"Float/Int Distribution?"}
    D -->|Yes| E{"Same log setting?"}
    E -->|No| F["ValueError: Different log configuration"]
    E -->|Yes| G["Compatible"]
    D -->|No| H{"Categorical Distribution?"}
    H -->|Yes| I{"Exact same choices?"}
    I -->|No| J["ValueError: Dynamic value space not supported"]
    I -->|Yes| G
    H -->|No| G
```

### Dynamic Value Ranges

For `FloatDistribution` and `IntDistribution`, the range bounds (`low`, `high`) can vary between trials:

```python
# Trial 1
suggest_float("x", 0.0, 1.0)  # OK

# Trial 2
suggest_float("x", -1.0, 2.0)  # OK - different range, same log setting
```

However, `CategoricalDistribution` does **not** support dynamic choices:

```python
# Trial 1
suggest_categorical("optimizer", ["adam", "sgd"])  # OK

# Trial 2
suggest_categorical("optimizer", ["adam", "rmsprop"])  # ValueError!
```

### Compatibility Validation in Practice

When a parameter is suggested multiple times in the same trial with different distribution settings, a warning is issued:

**Sources:** [optuna/distributions.py:623-658](), [optuna/trial/_trial.py:684-696]()

---

## Search Space Definition

The search space is the set of all valid parameter combinations that can be suggested during optimization.

### Search Space Composition

```mermaid
graph TB
    subgraph "Complete Search Space"
        SS["study.sampler.infer_relative_search_space()"]
    end
    
    subgraph "Parameter Distributions"
        D1["'learning_rate'<br/>FloatDistribution(1e-5, 1e-1, log=True)"]
        D2["'batch_size'<br/>IntDistribution(16, 256, step=16)"]
        D3["'optimizer'<br/>CategoricalDistribution(['adam', 'sgd'])"]
    end
    
    SS --> D1
    SS --> D2
    SS --> D3
    
    D1 --> V1["Value: 0.0001"]
    D2 --> V2["Value: 64"]
    D3 --> V3["Value: 'adam'"]
```

### Relative vs Independent Search Space

The sampler can infer a **relative search space** containing parameters that should be sampled jointly (considering correlations), while remaining parameters are sampled independently.

```mermaid
sequenceDiagram
    participant Trial
    participant Sampler
    
    Trial->>Sampler: infer_relative_search_space(study, trial)
    Sampler-->>Trial: {"lr": FloatDist(...), "momentum": FloatDist(...)}
    
    Trial->>Sampler: sample_relative(study, trial, search_space)
    Sampler-->>Trial: {"lr": 0.01, "momentum": 0.9}
    
    Note over Trial: Parameters in relative_search_space<br/>are sampled together
    
    Trial->>Sampler: sample_independent(study, trial, "dropout", IntDist(...))
    Sampler-->>Trial: 0.3
    
    Note over Trial: Other parameters sampled<br/>independently
```

The relative search space inference is sampler-dependent. For example, TPE's multivariate mode groups correlated parameters together for joint sampling.

**Sources:** [optuna/trial/_trial.py:62-76](), [optuna/trial/_trial.py:665-682]()

---

## JSON Serialization

Distributions can be serialized to JSON for storage and network transmission.

### Full Format

The full JSON format includes the class name and all attributes:

```json
{
  "name": "FloatDistribution",
  "attributes": {
    "low": 0.001,
    "high": 100.0,
    "log": true,
    "step": null
  }
}
```

### Abbreviated Format

An abbreviated format omits the class name for more compact representation:

```json
{
  "type": "float",
  "low": 0.001,
  "high": 100.0,
  "log": true
}
```

### Serialization Functions

**`distribution_to_json(dist: BaseDistribution) -> str`**
- Converts a distribution object to JSON string
- Uses full format with class name

**`json_to_distribution(json_str: str) -> BaseDistribution`**
- Deserializes JSON to distribution object
- Supports both full and abbreviated formats
- Reconstructs the appropriate distribution class

### Format Comparison

| Format | Size | Use Case |
|--------|------|----------|
| Full | Larger | Database storage, exact class preservation |
| Abbreviated | Smaller | API responses, configuration files |

**Sources:** [optuna/distributions.py:565-620](), [tests/test_distributions.py:35-71]()

---

## Deprecated Distribution Classes

Optuna 3.0 introduced unified `FloatDistribution` and `IntDistribution` classes to replace specialized variants. The old classes are maintained for backward compatibility but deprecated.

### Deprecated Classes Mapping

```mermaid
graph LR
    subgraph "Deprecated (v2.x)"
        UD["UniformDistribution"]
        LUD["LogUniformDistribution"]
        DUD["DiscreteUniformDistribution"]
        IUD["IntUniformDistribution"]
        ILUD["IntLogUniformDistribution"]
    end
    
    subgraph "Current (v3.0+)"
        FD["FloatDistribution"]
        ID["IntDistribution"]
    end
    
    UD -->|"log=False, step=None"| FD
    LUD -->|"log=True, step=None"| FD
    DUD -->|"log=False, step=q"| FD
    IUD -->|"log=False, step=1"| ID
    ILUD -->|"log=True, step=1"| ID
```

### Automatic Conversion

The `_convert_old_distribution_to_new_distribution()` function transparently converts deprecated distributions:

```python
# Old code (deprecated)
dist = UniformDistribution(low=0.0, high=1.0)

# Automatically converted to
dist = FloatDistribution(low=0.0, high=1.0, log=False, step=None)
```

This conversion ensures that studies created with older Optuna versions remain compatible with new code.

**Sources:** [optuna/distributions.py:200-252](), [optuna/distributions.py:254-308](), [optuna/distributions.py:395-454](), [optuna/distributions.py:709-765]()

---

## Usage in Trial Objects

All three trial types (`Trial`, `FrozenTrial`, `FixedTrial`) use distributions identically through the `suggest_*` methods.

### Suggestion Flow

```mermaid
graph TD
    A["trial.suggest_float('lr', 1e-5, 1e-1, log=True)"] --> B["Create FloatDistribution(1e-5, 1e-1, log=True)"]
    B --> C["trial._suggest(name, distribution)"]
    
    C --> D{"Trial Type?"}
    
    D -->|Trial| E["Sample from sampler<br/>Store in storage"]
    D -->|FrozenTrial| F["Return pre-stored value<br/>from params dict"]
    D -->|FixedTrial| G["Return fixed value<br/>from params dict"]
    
    E --> H["Validate with distribution._contains()"]
    F --> H
    G --> H
    
    H --> I["Return parameter value"]
```

### Distribution Storage in Trials

Each trial maintains a `distributions` dictionary mapping parameter names to their distribution objects:

```python
trial.distributions = {
    "learning_rate": FloatDistribution(1e-5, 1e-1, log=True),
    "batch_size": IntDistribution(16, 256, step=16),
    "optimizer": CategoricalDistribution(["adam", "sgd"])
}
```

This dictionary is:
- Populated as parameters are suggested
- Stored persistently in the storage backend
- Used for parameter validation in subsequent trials
- Checked for compatibility when the same parameter is suggested again

**Sources:** [optuna/trial/_trial.py:618-647](), [optuna/trial/_frozen.py:347-367](), [optuna/trial/_fixed.py:142-163](), [optuna/trial/_base.py:110-113]()

---

# Page: Storage Architecture

# Storage Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/storages/_base.py](optuna/storages/_base.py)
- [optuna/storages/_cached_storage.py](optuna/storages/_cached_storage.py)
- [optuna/storages/_in_memory.py](optuna/storages/_in_memory.py)
- [optuna/storages/_rdb/storage.py](optuna/storages/_rdb/storage.py)
- [tests/storages_tests/rdb_tests/test_storage.py](tests/storages_tests/rdb_tests/test_storage.py)
- [tests/storages_tests/test_cached_storage.py](tests/storages_tests/test_cached_storage.py)
- [tests/storages_tests/test_storages.py](tests/storages_tests/test_storages.py)

</details>



## Purpose and Scope

This document describes Optuna's storage layer, which provides persistent and in-memory backends for storing study metadata and trial results. The storage layer abstracts database operations through the `BaseStorage` interface and provides multiple implementations including relational database storage (RDBStorage), cached storage for performance (_CachedStorage), in-memory storage (InMemoryStorage), and journal-based storage (JournalStorage).

For information about the optimization loop and how storage is accessed during trial execution, see [Study and Optimization Loop](#2.1). For trial data structures that are persisted, see [Trial System and Parameter Suggestion](#2.2).

## Storage Interface Hierarchy

The storage layer follows a layered architecture where all implementations conform to the `BaseStorage` abstract interface. This enables different storage backends to be used interchangeably throughout Optuna.

```mermaid
graph TB
    BaseStorage["BaseStorage<br/>(optuna/storages/_base.py)"]
    
    subgraph "Persistent Implementations"
        RDBStorage["RDBStorage<br/>(optuna/storages/_rdb/storage.py)"]
        JournalStorage["JournalStorage<br/>(optuna/storages/journal)"]
    end
    
    subgraph "In-Memory Implementation"
        InMemoryStorage["InMemoryStorage<br/>(optuna/storages/_in_memory.py)"]
    end
    
    subgraph "Performance Wrapper"
        CachedStorage["_CachedStorage<br/>(optuna/storages/_cached_storage.py)"]
    end
    
    BaseStorage -->|"implements"| RDBStorage
    BaseStorage -->|"implements"| JournalStorage
    BaseStorage -->|"implements"| InMemoryStorage
    BaseStorage -->|"implements"| CachedStorage
    
    CachedStorage -->|"wraps"| RDBStorage
    
    RDBStorage -->|"uses"| SQLAlchemy["SQLAlchemy ORM"]
    SQLAlchemy -->|"connects to"| MySQL["MySQL"]
    SQLAlchemy -->|"connects to"| PostgreSQL["PostgreSQL"]
    SQLAlchemy -->|"connects to"| SQLite["SQLite"]
    
    JournalStorage -->|"uses"| JFile["JournalFileBackend"]
    JournalStorage -->|"uses"| JRedis["JournalRedisBackend"]
```

**Sources:** [optuna/storages/_base.py:21-626](), [optuna/storages/_rdb/storage.py:106-200](), [optuna/storages/_cached_storage.py:36-59](), [optuna/storages/_in_memory.py:26-47]()

## BaseStorage Abstract Interface

The `BaseStorage` class defines the contract that all storage backends must implement. It provides methods for managing studies and trials, organized into several categories:

### Core Methods

| Category | Methods | Purpose |
|----------|---------|---------|
| **Study Management** | `create_new_study()`, `delete_study()` | Create and delete studies |
| **Study Attributes** | `set_study_user_attr()`, `set_study_system_attr()`, `get_study_user_attrs()`, `get_study_system_attrs()` | Manage study-level metadata |
| **Study Access** | `get_study_id_from_name()`, `get_study_name_from_id()`, `get_study_directions()`, `get_all_studies()` | Read study information |
| **Trial Management** | `create_new_trial()`, `set_trial_param()`, `set_trial_state_values()` | Create and update trials |
| **Trial Attributes** | `set_trial_intermediate_value()`, `set_trial_user_attr()`, `set_trial_system_attr()` | Store trial metadata and intermediate values |
| **Trial Access** | `get_trial()`, `get_all_trials()`, `get_best_trial()`, `get_trial_id_from_study_id_trial_number()` | Read trial information |

### Thread Safety Requirements

The `BaseStorage` interface specifies strict thread safety requirements [optuna/storages/_base.py:31-47]():

1. **Immutability of Read Data**: Data instances returned from storage (e.g., `FrozenTrial` objects) must not be modified by subsequent write operations. This is typically achieved by storage implementations replacing old data with copies on write.

2. **Shared Instance Safety**: Storage instances can be shared among multiple threads, requiring all methods to be thread-safe.

3. **RUNNING Trial Ownership**: Only trials in the `RUNNING` state can be modified. Finished trials (`COMPLETE`, `FAIL`, `PRUNED`) and `WAITING` trials (except state field) cannot be updated.

**Sources:** [optuna/storages/_base.py:21-626]()

## RDBStorage: Relational Database Backend

`RDBStorage` provides persistent storage using SQL databases through SQLAlchemy ORM. It is the recommended storage backend for production use and distributed optimization.

### Architecture Components

```mermaid
graph TB
    RDBStorage["RDBStorage"]
    
    subgraph "SQLAlchemy Integration"
        Engine["sqlalchemy.engine<br/>(create_engine)"]
        ScopedSession["sqlalchemy_orm.scoped_session<br/>(thread-local sessions)"]
        SessionMaker["sqlalchemy_orm.sessionmaker"]
    end
    
    subgraph "Database Schema"
        StudyModel["StudyModel"]
        TrialModel["TrialModel"]
        TrialParamModel["TrialParamModel"]
        TrialValueModel["TrialValueModel"]
        TrialIntermediateValueModel["TrialIntermediateValueModel"]
        StudyDirectionModel["StudyDirectionModel"]
        StudyUserAttributeModel["StudyUserAttributeModel"]
        StudySystemAttributeModel["StudySystemAttributeModel"]
        TrialUserAttributeModel["TrialUserAttributeModel"]
        TrialSystemAttributeModel["TrialSystemAttributeModel"]
    end
    
    subgraph "Schema Management"
        VersionManager["_VersionManager"]
        Alembic["Alembic Migrations"]
    end
    
    RDBStorage -->|"creates"| Engine
    RDBStorage -->|"creates"| ScopedSession
    Engine --> ScopedSession
    SessionMaker --> ScopedSession
    
    RDBStorage -->|"uses"| VersionManager
    VersionManager -->|"uses"| Alembic
    
    ScopedSession -->|"queries"| StudyModel
    ScopedSession -->|"queries"| TrialModel
    TrialModel -->|"1:N"| TrialParamModel
    TrialModel -->|"1:N"| TrialValueModel
    TrialModel -->|"1:N"| TrialIntermediateValueModel
    StudyModel -->|"1:N"| StudyDirectionModel
    StudyModel -->|"1:N"| StudyUserAttributeModel
    StudyModel -->|"1:N"| StudySystemAttributeModel
    TrialModel -->|"1:N"| TrialUserAttributeModel
    TrialModel -->|"1:N"| TrialSystemAttributeModel
```

**Sources:** [optuna/storages/_rdb/storage.py:106-270](), [optuna/storages/_rdb/models.py]()

### Initialization and Configuration

`RDBStorage` accepts several configuration parameters [optuna/storages/_rdb/storage.py:202-226]():

```python
def __init__(
    self,
    url: str,
    engine_kwargs: dict[str, Any] | None = None,
    skip_compatibility_check: bool = False,
    *,
    heartbeat_interval: int | None = None,
    grace_period: int | None = None,
    failed_trial_callback: Callable | None = None,
    skip_table_creation: bool = False,
) -> None:
```

| Parameter | Purpose |
|-----------|---------|
| `url` | Database connection URL (e.g., `"sqlite:///example.db"`, `"postgresql://user:pass@host/db"`) |
| `engine_kwargs` | Parameters passed to `sqlalchemy.create_engine()` (e.g., `pool_size`, `timeout`) |
| `skip_compatibility_check` | Skip schema version compatibility check |
| `heartbeat_interval` | Interval in seconds for recording trial heartbeats (for distributed optimization) |
| `grace_period` | Time in seconds before declaring a trial stale (defaults to `2 * heartbeat_interval`) |
| `failed_trial_callback` | Callback invoked when a stale trial is detected |
| `skip_table_creation` | Skip automatic table creation on initialization |

### MySQL-Specific Configuration

For MySQL databases, `RDBStorage` automatically enables `pool_pre_ping` to prevent connection timeouts [optuna/storages/_rdb/storage.py:227]():

```python
self._set_default_engine_kwargs_for_mysql(url, self.engine_kwargs)
```

This ensures connections are validated before use, preventing errors when objective functions execute longer than MySQL's `wait_timeout` setting.

**Sources:** [optuna/storages/_rdb/storage.py:202-246]()

### Session Management and Transactions

`RDBStorage` uses scoped sessions for thread-local database connections. The `_create_scoped_session()` context manager handles transaction lifecycle [optuna/storages/_rdb/storage.py:72-104]():

```mermaid
sequenceDiagram
    participant Client
    participant ScopedSession
    participant Session
    participant Database
    
    Client->>ScopedSession: _create_scoped_session()
    ScopedSession->>Session: session = scoped_session()
    
    Client->>Session: perform operations
    Session->>Database: SQL statements
    
    alt Success
        Session->>Database: COMMIT
        Database-->>Session: OK
    else IntegrityError (ignorable)
        Session->>Database: ROLLBACK
        Note over Session: Log and ignore<br/>(timing issue)
    else SQLAlchemyError
        Session->>Database: ROLLBACK
        Session-->>Client: StorageInternalError
    else Other Exception
        Session->>Database: ROLLBACK
        Session-->>Client: Reraise exception
    end
    
    Session->>Session: close()
    Session-->>ScopedSession: Done
    ScopedSession-->>Client: Return
```

**Sources:** [optuna/storages/_rdb/storage.py:72-104]()

### Trial Creation with Retry Logic

Trial creation in distributed environments can encounter deadlocks. `RDBStorage` implements retry logic with non-exponential backoff [optuna/storages/_rdb/storage.py:439-504]():

```python
# Retry maximum five times. Deadlocks may occur in distributed environments.
MAX_RETRIES = 5
for n_retries in range(1, MAX_RETRIES + 1):
    try:
        with _create_scoped_session(self.scoped_session) as session:
            # Lock study to prevent race conditions on trial.number calculation
            models.StudyModel.find_or_raise_by_id(study_id, session, for_update=True)
            trial = self._get_prepared_new_trial(study_id, template_trial, session)
            return _create_frozen_trial(trial, template_trial)
    except optuna.exceptions.StorageInternalError as e:
        if n_retries == MAX_RETRIES:
            raise e
        # Non-exponential backoff
        time.sleep(random.random() * 2.0)
```

The `for_update=True` parameter ensures row-level locking on the study record, preventing concurrent trial number calculation conflicts.

**Sources:** [optuna/storages/_rdb/storage.py:439-504]()

### Database-Specific Upsert Operations

`RDBStorage` uses database-specific upsert syntax for efficient attribute updates [optuna/storages/_rdb/storage.py:761-806]():

| Database | Syntax | Code Location |
|----------|--------|---------------|
| **MySQL** | `INSERT ... ON DUPLICATE KEY UPDATE` | [optuna/storages/_rdb/storage.py:772-779]() |
| **SQLite 3.24+** | `INSERT ... ON CONFLICT DO UPDATE` | [optuna/storages/_rdb/storage.py:780-788]() |
| **PostgreSQL** | `INSERT ... ON CONFLICT DO UPDATE` | [optuna/storages/_rdb/storage.py:789-797]() |
| **Fallback** | Query + Insert/Update | [optuna/storages/_rdb/storage.py:799-805]() |

**Sources:** [optuna/storages/_rdb/storage.py:761-806]()

### Schema Versioning with Alembic

`RDBStorage` uses Alembic for database schema migrations. The `_VersionManager` class handles version checking and upgrades [optuna/storages/_rdb/storage.py:243-245]():

```python
self._version_manager = _VersionManager(self.url, self.engine, self.scoped_session)
if not skip_compatibility_check:
    self._version_manager.check_table_schema_compatibility()
```

Available schema versions: `v3.2.0.a`, `v3.0.0.d`, `v3.0.0.c`, `v3.0.0.b`, `v3.0.0.a`, `v2.6.0.a`, `v2.4.0.a`, `v1.3.0.a`, `v1.2.0.a`, `v0.9.0.a`

**Sources:** [optuna/storages/_rdb/storage.py:243-270](), [tests/storages_tests/rdb_tests/test_storage.py:70-82]()

## _CachedStorage: Performance Layer

`_CachedStorage` wraps `RDBStorage` to reduce database access through intelligent caching. It is automatically used when calling `optuna.storages.get_storage()` with a database URL.

### Caching Strategy

```mermaid
graph TB
    subgraph "Cache State (_StudyInfo)"
        Trials["trials: dict[int, FrozenTrial]<br/>(trial_number → FrozenTrial)"]
        UnfinishedIDs["unfinished_trial_ids: set[int]<br/>(trial_ids requiring refresh)"]
        LastFinishedID["last_finished_trial_id: int<br/>(last known finished trial)"]
        ParamDist["param_distribution: dict[str, BaseDistribution]<br/>(cached distributions)"]
        Directions["directions: list[StudyDirection]"]
        Name["name: str"]
    end
    
    subgraph "Write Operations"
        Write["set_trial_*()"]
        WriteThrough["Write-through to backend"]
        NoCache["No caching on write"]
    end
    
    subgraph "Read Operations"
        Read["get_all_trials()"]
        CheckCache["Check cache first"]
        ReadBackend["Read from backend<br/>if needed"]
        UpdateCache["Update cache"]
    end
    
    Write --> WriteThrough
    WriteThrough --> NoCache
    
    Read --> CheckCache
    CheckCache -->|"cache miss or<br/>unfinished trials"| ReadBackend
    ReadBackend --> UpdateCache
    CheckCache -->|"cache hit"| ReturnCached["Return cached trials"]
    UpdateCache --> Trials
    UpdateCache --> UnfinishedIDs
    UpdateCache --> LastFinishedID
```

**Sources:** [optuna/storages/_cached_storage.py:22-34](), [optuna/storages/_cached_storage.py:36-59]()

### Cache Consistency Model

`_CachedStorage` implements a **write-through** caching strategy [optuna/storages/_cached_storage.py:42-58]():

1. **Write Operations**: All writes (state changes, parameters, attributes) are immediately written to the backend storage. No caching occurs on writes.

2. **Read Operations**: Finished trials are cached. Unfinished trials are always re-read from backend storage to get latest updates.

3. **Persistence Guarantees**:
   - Study attributes are always persistent
   - Trial `state` changes are always persistent  
   - All trial attributes written before a `state` change are guaranteed persistent before the state change succeeds

### Selective Trial Refresh

The `_read_trials_from_remote_storage()` method efficiently refreshes only trials that may have changed [optuna/storages/_cached_storage.py:247-272]():

```python
trials = self._backend._get_trials(
    study_id,
    states=None,
    included_trial_ids=study.unfinished_trial_ids,  # Refresh unfinished trials
    trial_id_greater_than=study.last_finished_trial_id,  # Fetch new trials
)
```

This approach minimizes database queries by:
- Only re-reading trials in unfinished states (`RUNNING`, `WAITING`)
- Fetching only trials created after the last known finished trial
- Caching finished trials permanently (they cannot be modified)

**Sources:** [optuna/storages/_cached_storage.py:247-272]()

### Thread Safety

`_CachedStorage` uses a single lock for all cache operations [optuna/storages/_cached_storage.py:66]():

```python
self._lock = threading.Lock()
```

All cache read and write operations acquire this lock, ensuring thread-safe access to the in-memory cache structures.

**Sources:** [optuna/storages/_cached_storage.py:36-75]()

## InMemoryStorage: Fast Non-Persistent Backend

`InMemoryStorage` stores all data in Python memory structures without any persistence. It is suitable for testing, debugging, and single-process optimization where persistence is not required.

### Internal Data Structures

```mermaid
graph TB
    InMemoryStorage["InMemoryStorage"]
    
    subgraph "Study Index"
        StudyNameToID["_study_name_to_id<br/>dict[str, int]"]
        Studies["_studies<br/>dict[int, _StudyInfo]"]
    end
    
    subgraph "Trial Index"
        TrialIDToStudyAndNumber["_trial_id_to_study_id_and_number<br/>dict[int, tuple[int, int]]"]
    end
    
    subgraph "_StudyInfo (per study)"
        TrialsList["trials: list[FrozenTrial]<br/>(sorted by number)"]
        ParamDistribution["param_distribution: dict[str, BaseDistribution]"]
        UserAttrs["user_attrs: dict[str, Any]"]
        SystemAttrs["system_attrs: dict[str, Any]"]
        StudyName["name: str"]
        StudyDirections["directions: list[StudyDirection]"]
        BestTrialID["best_trial_id: int | None<br/>(cached for efficiency)"]
    end
    
    InMemoryStorage --> StudyNameToID
    InMemoryStorage --> Studies
    InMemoryStorage --> TrialIDToStudyAndNumber
    
    Studies --> TrialsList
    Studies --> ParamDistribution
    Studies --> UserAttrs
    Studies --> SystemAttrs
    Studies --> StudyName
    Studies --> StudyDirections
    Studies --> BestTrialID
```

**Sources:** [optuna/storages/_in_memory.py:49-58](), [optuna/storages/_in_memory.py:416-425]()

### Copy-on-Write for Thread Safety

`InMemoryStorage` ensures thread safety through a **copy-on-write** strategy [optuna/storages/_in_memory.py:213-218]():

```python
trial = copy.copy(trial)
trial.params = copy.copy(trial.params)
trial.params[param_name] = distribution.to_external_repr(param_value_internal)
trial.distributions = copy.copy(trial.distributions)
trial.distributions[param_name] = distribution
self._set_trial(trial_id, trial)
```

When updating a trial, `InMemoryStorage`:
1. Creates a shallow copy of the `FrozenTrial` object
2. Creates shallow copies of mutable attributes (e.g., `params`, `distributions`)
3. Modifies the copies
4. Replaces the original trial with the modified copy

This ensures that any thread holding a reference to the old `FrozenTrial` sees an immutable snapshot, while new readers see the updated version.

**Sources:** [optuna/storages/_in_memory.py:190-219]()

### Best Trial Caching

`InMemoryStorage` maintains a cached `best_trial_id` for each study to avoid scanning all trials on every `get_best_trial()` call [optuna/storages/_in_memory.py:292-324]():

```python
def _update_cache(self, trial_id: int, study_id: int) -> None:
    trial = self._get_trial(trial_id)
    
    if trial.state != TrialState.COMPLETE:
        return
    
    best_trial_id = self._studies[study_id].best_trial_id
    if best_trial_id is None:
        self._studies[study_id].best_trial_id = trial_id
        return
    
    # Compare with current best...
```

The cache is updated whenever a trial completes, maintaining O(1) best trial lookup.

**Sources:** [optuna/storages/_in_memory.py:292-324]()

## Data Model and Relationships

The storage layer persists a hierarchical data model with studies at the top level and trials nested within studies.

```mermaid
graph TB
    Study["Study"]
    Trial["Trial"]
    
    subgraph "Study Attributes"
        StudyName["study_name: str"]
        Directions["directions: list[StudyDirection]"]
        StudyUserAttrs["user_attrs: dict[str, Any]"]
        StudySystemAttrs["system_attrs: dict[str, Any]"]
    end
    
    subgraph "Trial Core"
        TrialNumber["number: int<br/>(sequential per study)"]
        TrialID["trial_id: int<br/>(globally unique)"]
        State["state: TrialState"]
        DatetimeStart["datetime_start: datetime"]
        DatetimeComplete["datetime_complete: datetime | None"]
    end
    
    subgraph "Trial Results"
        Values["values: Sequence[float] | None<br/>(multi-objective values)"]
        IntermediateValues["intermediate_values: dict[int, float]<br/>(step → value)"]
    end
    
    subgraph "Trial Parameters"
        Params["params: dict[str, Any]<br/>(external repr)"]
        Distributions["distributions: dict[str, BaseDistribution]<br/>(parameter space)"]
    end
    
    subgraph "Trial Attributes"
        TrialUserAttrs["user_attrs: dict[str, Any]"]
        TrialSystemAttrs["system_attrs: dict[str, Any]"]
    end
    
    Study -->|"1:N"| Trial
    Study --> StudyName
    Study --> Directions
    Study --> StudyUserAttrs
    Study --> StudySystemAttrs
    
    Trial --> TrialNumber
    Trial --> TrialID
    Trial --> State
    Trial --> DatetimeStart
    Trial --> DatetimeComplete
    Trial --> Values
    Trial --> IntermediateValues
    Trial --> Params
    Trial --> Distributions
    Trial --> TrialUserAttrs
    Trial --> TrialSystemAttrs
```

**Sources:** [optuna/trial.py:FrozenTrial](), [optuna/storages/_rdb/models.py]()

### Trial State Transitions

Trials follow a specific state machine enforced by `check_trial_is_updatable()` [optuna/storages/_base.py:607-625]():

```mermaid
stateDiagram-v2
    [*] --> WAITING: create_new_trial()
    WAITING --> RUNNING: set_trial_state_values(RUNNING)
    RUNNING --> COMPLETE: set_trial_state_values(COMPLETE, values)
    RUNNING --> FAIL: set_trial_state_values(FAIL)
    RUNNING --> PRUNED: set_trial_state_values(PRUNED)
    
    COMPLETE --> [*]
    FAIL --> [*]
    PRUNED --> [*]
    
    note right of WAITING
        Only state field can be modified
    end note
    
    note right of RUNNING
        All fields can be modified
    end note
    
    note right of COMPLETE
        No modifications allowed
        (finished state)
    end note
```

**Sources:** [optuna/storages/_base.py:607-625](), [optuna/trial.py:TrialState]()

## Heartbeat Mechanism for Distributed Optimization

`RDBStorage` implements a heartbeat mechanism to detect and handle stale trials in distributed environments. This is particularly useful in cluster environments where worker nodes may fail unexpectedly.

### Heartbeat Components

The heartbeat system consists of three main components:

1. **Recording Heartbeats**: The `record_heartbeat()` method updates a timestamp in the database [optuna/storages/_heartbeat.py]().

2. **Detecting Stale Trials**: The `_get_stale_trial_ids()` method identifies trials whose heartbeat has exceeded the grace period.

3. **Failing Stale Trials**: Stale trials are automatically marked as `FAIL` and a callback is invoked.

### Heartbeat Configuration

When initializing `RDBStorage` with heartbeat support [optuna/storages/_rdb/storage.py:208-225]():

```python
storage = RDBStorage(
    url="postgresql://user:pass@host/db",
    heartbeat_interval=60,  # Record heartbeat every 60 seconds
    grace_period=180,       # Consider trial stale after 180 seconds
    failed_trial_callback=my_callback  # Optional callback for failed trials
)
```

The heartbeat mechanism works with `Study.optimize()` but not with manual `ask()`/`tell()` workflows [optuna/storages/_rdb/storage.py:150-153]().

**Sources:** [optuna/storages/_rdb/storage.py:143-199](), [optuna/storages/_heartbeat.py]()

## Storage Selection and Initialization

Optuna provides a convenience function `get_storage()` for initializing storage backends:

```python
def get_storage(storage: str | BaseStorage | None) -> BaseStorage:
    if storage is None:
        return InMemoryStorage()
    
    if isinstance(storage, str):
        # Database URLs are wrapped with _CachedStorage
        return _CachedStorage(RDBStorage(storage))
    
    # Already a storage instance
    return storage
```

### Common Usage Patterns

| Use Case | Storage Choice | Example |
|----------|----------------|---------|
| **Testing/Development** | `InMemoryStorage` | `storage = InMemoryStorage()` |
| **Single Process** | SQLite with caching | `storage = get_storage("sqlite:///study.db")` |
| **Distributed** | PostgreSQL/MySQL with heartbeat | `storage = RDBStorage("postgresql://...", heartbeat_interval=60)` |
| **Append-Only Logs** | `JournalStorage` | `storage = JournalStorage(JournalFileBackend("log.json"))` |

**Sources:** [optuna/storages/__init__.py:get_storage](), [tests/storages_tests/test_storages.py:78-81]()

## Storage Pickling and Serialization

All storage implementations support pickling for distributed computing frameworks [tests/storages_tests/test_storages.py:54-76]():

```python
storage = RDBStorage("sqlite:///study.db")
pickled = pickle.dumps(storage)
restored = pickle.loads(pickled)
```

When unpickling `RDBStorage`, the following occurs [optuna/storages/_rdb/storage.py:254-270]():

1. The `url` and `engine_kwargs` are preserved
2. A new SQLAlchemy engine is created
3. A new scoped session is created
4. The version manager is recreated
5. Connection pool is separate from the original instance

This allows storage instances to be safely passed to worker processes in distributed optimization.

**Sources:** [optuna/storages/_rdb/storage.py:247-270](), [tests/storages_tests/test_storages.py:54-76]()

---

# Page: Sampling Algorithms

# Sampling Algorithms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/_gp/acqf.py](optuna/_gp/acqf.py)
- [optuna/_gp/batched_lbfgsb.py](optuna/_gp/batched_lbfgsb.py)
- [optuna/_gp/gp.py](optuna/_gp/gp.py)
- [optuna/_gp/optim_mixed.py](optuna/_gp/optim_mixed.py)
- [optuna/_gp/optim_sample.py](optuna/_gp/optim_sample.py)
- [optuna/_gp/prior.py](optuna/_gp/prior.py)
- [optuna/_gp/search_space.py](optuna/_gp/search_space.py)
- [optuna/integration/chainermn.py](optuna/integration/chainermn.py)
- [optuna/integration/cma.py](optuna/integration/cma.py)
- [optuna/samplers/_cmaes.py](optuna/samplers/_cmaes.py)
- [optuna/samplers/_gp/sampler.py](optuna/samplers/_gp/sampler.py)
- [optuna/samplers/_tpe/parzen_estimator.py](optuna/samplers/_tpe/parzen_estimator.py)
- [optuna/samplers/_tpe/sampler.py](optuna/samplers/_tpe/sampler.py)
- [optuna/terminator/improvement/emmr.py](optuna/terminator/improvement/emmr.py)
- [optuna/terminator/improvement/evaluator.py](optuna/terminator/improvement/evaluator.py)
- [tests/gp_tests/test_acqf.py](tests/gp_tests/test_acqf.py)
- [tests/gp_tests/test_batched_lbfgsb.py](tests/gp_tests/test_batched_lbfgsb.py)
- [tests/gp_tests/test_gp.py](tests/gp_tests/test_gp.py)
- [tests/gp_tests/test_search_space.py](tests/gp_tests/test_search_space.py)
- [tests/samplers_tests/test_cmaes.py](tests/samplers_tests/test_cmaes.py)
- [tests/samplers_tests/test_gp.py](tests/samplers_tests/test_gp.py)
- [tests/samplers_tests/test_samplers.py](tests/samplers_tests/test_samplers.py)
- [tests/samplers_tests/tpe_tests/test_multi_objective_sampler.py](tests/samplers_tests/tpe_tests/test_multi_objective_sampler.py)
- [tests/samplers_tests/tpe_tests/test_parzen_estimator.py](tests/samplers_tests/tpe_tests/test_parzen_estimator.py)
- [tests/samplers_tests/tpe_tests/test_sampler.py](tests/samplers_tests/tpe_tests/test_sampler.py)

</details>



This document provides an overview of Optuna's sampling algorithms system, which forms the core intelligence behind hyperparameter optimization. Sampling algorithms determine how to suggest new parameter values for each trial based on the history of previous trials and their objective values.

For detailed information about specific sampling algorithms, see:
- Page 3.1: BaseSampler Interface and Sampling Strategies
- Page 3.2: Tree-structured Parzen Estimator (TPE)
- Page 3.3: Gaussian Process Sampler
- Page 3.4: CMA-ES Sampler
- Page 3.5: Multi-Objective Optimization
- Page 3.6: Pruning and Other Samplers

For information about trial management and parameter suggestions, see Page 2.2 (Trial Objects and Parameter Suggestion).

## Architecture Overview

The sampling system in Optuna is built around a pluggable architecture where different sampling algorithms can be used interchangeably through a common interface. All samplers inherit from the `BaseSampler` abstract class [optuna/samplers/_base.py:31-62]() and implement standardized methods for parameter suggestion.

### Sampler Class Hierarchy

The following diagram shows the main sampler implementations in Optuna:

```mermaid
graph TB
    BaseSampler["optuna.samplers.BaseSampler<br/>optuna/samplers/_base.py"]
    
    subgraph "Bayesian Optimization"
        TPESampler["optuna.samplers.TPESampler<br/>optuna/samplers/_tpe/sampler.py<br/>Tree-structured Parzen Estimator"]
        GPSampler["optuna.samplers.GPSampler<br/>Gaussian Process"]
    end
    
    subgraph "Evolution Strategy"
        CmaEsSampler["optuna.samplers.CmaEsSampler<br/>optuna/samplers/_cmaes.py<br/>CMA-ES"]
    end
    
    subgraph "Basic Samplers"
        RandomSampler["optuna.samplers.RandomSampler<br/>Uniform random sampling"]
        GridSampler["optuna.samplers.GridSampler<br/>Exhaustive grid search"]
    end
    
    subgraph "Multi-Objective"
        NSGAIISampler["optuna.samplers.NSGAIISampler<br/>Evolutionary multi-objective"]
    end
    
    subgraph "Integration Samplers"
        BoTorchSampler["optuna.integration.BoTorchSampler<br/>optuna/integration/botorch.py"]
        SkoptSampler["optuna.integration.SkoptSampler<br/>Scikit-Optimize backend"]
    end
    
    BaseSampler --> RandomSampler
    BaseSampler --> TPESampler
    BaseSampler --> CmaEsSampler
    BaseSampler --> GPSampler
    BaseSampler --> GridSampler
    BaseSampler --> NSGAIISampler
    BaseSampler -.->|"Integration"| BoTorchSampler
    BaseSampler -.->|"Integration"| SkoptSampler
    
    TPESampler -.->|"Fallback to"| RandomSampler
    CmaEsSampler -.->|"Uses internally"| RandomSampler
```

Sources: [optuna/samplers/_base.py:31-62](), [optuna/samplers/_tpe/sampler.py:72-287](), [optuna/samplers/_cmaes.py:47-246](), [optuna/integration/botorch.py:1-10]()

## Core Sampling Interface: BaseSampler

The `BaseSampler` class [optuna/samplers/_base.py:31-236]() defines the fundamental interface that all sampling algorithms must implement. Optuna combines two types of sampling strategies: **relative sampling** and **independent sampling**.

### Relative vs Independent Sampling

**Relative Sampling** determines values of multiple parameters simultaneously, allowing samplers to exploit relationships between parameters (e.g., correlation). This is used by advanced algorithms like TPE and CMA-ES when operating in multivariate mode.

**Independent Sampling** determines a value of a single parameter without considering relationships with other parameters. This is used for parameters outside the relative search space or as a fallback.

### Parameter Suggestion Flow

The following diagram shows how the Study orchestrates sampling during a trial:

```mermaid
sequenceDiagram
    participant Study as Study
    participant Sampler as BaseSampler
    participant Trial as Trial
    
    Study->>Sampler: before_trial(study, trial)
    Study->>Sampler: infer_relative_search_space(study, trial)
    Sampler-->>Study: search_space dict
    
    alt Relative Search Space Not Empty
        Study->>Sampler: sample_relative(study, trial, search_space)
        Sampler-->>Study: params dict
    end
    
    loop For each parameter suggestion
        Trial->>Sampler: sample_independent(study, trial, param_name, distribution)
        Sampler-->>Trial: param value
    end
    
    Note over Study,Trial: Objective function executes
    
    Study->>Sampler: after_trial(study, trial, state, values)
```

Sources: [optuna/samplers/_base.py:31-236]()

### Key BaseSampler Methods

| Method | Returns | Purpose |
|--------|---------|---------|
| `infer_relative_search_space(study, trial)` | `dict[str, BaseDistribution]` | Determines which parameters to sample jointly [optuna/samplers/_base.py:68-93]() |
| `sample_relative(study, trial, search_space)` | `dict[str, Any]` | Samples multiple parameters jointly [optuna/samplers/_base.py:95-125]() |
| `sample_independent(study, trial, param_name, param_distribution)` | `Any` | Samples a single parameter independently [optuna/samplers/_base.py:127-163]() |
| `before_trial(study, trial)` | `None` | Pre-processing hook before trial execution [optuna/samplers/_base.py:165-185]() |
| `after_trial(study, trial, state, values)` | `None` | Post-processing hook after trial completion [optuna/samplers/_base.py:187-216]() |
| `reseed_rng()` | `None` | Reseeds the random number generator [optuna/samplers/_base.py:218-228]() |

Sources: [optuna/samplers/_base.py:31-236]()

## Available Sampling Algorithms

Optuna provides a diverse set of sampling algorithms, each optimized for different types of optimization problems.

### Algorithm Comparison

| Algorithm | Class | Primary Use Case | Default `n_startup_trials` | Distribution Support |
|-----------|--------|------------------|----------------|----------------------|
| Random Sampling | `RandomSampler` | Baseline exploration | 0 | All distributions |
| Tree-structured Parzen Estimator | `TPESampler` | General-purpose Bayesian optimization | 10 | All distributions |
| CMA-ES | `CmaEsSampler` | Continuous/integer optimization | 1 | Float, Int only |
| Gaussian Process | `GPSampler` | Small-scale optimization with acquisition functions | Varies | Float, Int only |
| Grid Search | `GridSampler` | Exhaustive deterministic search | N/A | All distributions |
| NSGA-II | `NSGAIISampler` | Multi-objective evolutionary | 0 | All distributions |

Sources: [optuna/samplers/_tpe/sampler.py:72-287](), [optuna/samplers/_cmaes.py:47-246](), [tests/samplers_tests/tpe_tests/test_sampler.py:22-28](), [tests/samplers_tests/test_cmaes.py:24-36]()

### Startup Trials and Fallback Behavior

Many advanced samplers use a two-phase approach controlled by the `n_startup_trials` parameter:

**Phase 1 - Random Exploration**: For the first `n_startup_trials` completed trials, the sampler delegates to `RandomSampler` for parameter suggestions.

**Phase 2 - Model-Based Exploitation**: After collecting sufficient data, the sampler uses its algorithm-specific intelligence.

The following diagram illustrates this behavior for `TPESampler`:

```mermaid
graph TB
    subgraph "TPESampler.sample_independent()"
        CheckTrials["Check number of<br/>completed trials"]
        UsesRandom["Use RandomSampler<br/>for suggestion"]
        UsesTPE["Use TPE algorithm<br/>for suggestion"]
        
        CheckTrials -->|"< n_startup_trials"| UsesRandom
        CheckTrials -->|">= n_startup_trials"| UsesTPE
    end
    
    subgraph "Implementation"
        RandomSamplerCall["self._random_sampler.sample_independent()"]
        TPEAlgorithm["self._sample()"]
    end
    
    UsesRandom --> RandomSamplerCall
    UsesTPE --> TPEAlgorithm
```

Sources: [optuna/samplers/_tpe/sampler.py:455-489](), [tests/samplers_tests/tpe_tests/test_sampler.py:452-472]()

### CmaEsSampler Specifics

`CmaEsSampler` has unique characteristics:
- Does **not** support `CategoricalDistribution` [optuna/samplers/_cmaes.py:73-80]()
- Uses `IntersectionSearchSpace` to determine relative search space [optuna/samplers/_cmaes.py:339-355]()
- Requires `n_startup_trials` before starting CMA-ES optimization [optuna/samplers/_cmaes.py:369-370]()
- Stores optimizer state in trial system attributes for persistence [optuna/samplers/_cmaes.py:408-428]()

Sources: [optuna/samplers/_cmaes.py:47-246](), [optuna/samplers/_cmaes.py:339-433]()

## Distribution System Integration

Samplers interact with Optuna's distribution system (see Page 2.3: Distributions and Parameter Space) to handle different parameter types. The `BaseDistribution` interface provides methods for converting between internal and external representations.

### Distribution Support by Sampler

| Sampler | FloatDistribution | IntDistribution | CategoricalDistribution | Notes |
|---------|-------------------|-----------------|-------------------------|-------|
| `RandomSampler` | ✓ | ✓ | ✓ | Supports all distributions and constraints |
| `TPESampler` | ✓ | ✓ | ✓ | Supports all distributions including `log=True` and `step` |
| `CmaEsSampler` | ✓ | ✓ | ✗ | No categorical support; requires numeric distributions |
| `GPSampler` | ✓ | ✓ | ✗ | Continuous/discrete only; no categorical |
| `GridSampler` | ✓ | ✓ | ✓ | Deterministic grid over all distribution types |

Sources: [optuna/samplers/_tpe/sampler.py:72-287](), [optuna/samplers/_cmaes.py:73-80](), [optuna/samplers/_cmaes.py:350-353]()

### Internal Representation Conversion

Samplers work with distributions' internal representations (floating-point values) through the `to_internal_repr()` and `to_external_repr()` methods. This allows uniform handling of all parameter types:

**TPESampler Example**:
```python
# In TPESampler._get_internal_repr()
for trial in trials:
    params = self._get_params(trial)
    for param_name, distribution in search_space.items():
        param = params[param_name]
        # Convert to internal representation (float)
        values[param_name].append(distribution.to_internal_repr(param))

# Later, in TPESampler._sample()
for param_name, dist in search_space.items():
    # Convert back to external representation
    ret[param_name] = dist.to_external_repr(ret[param_name])
```

Sources: [optuna/samplers/_tpe/sampler.py:509-519](), [optuna/samplers/_tpe/sampler.py:558-560]()

## Multi-Objective Optimization

Several samplers support multi-objective optimization where trials have multiple objective values. This is covered in detail in Page 3.5: Multi-Objective Optimization.

### Multi-Objective Sampler Support

| Sampler | Multi-Objective Support | Approach |
|---------|------------------------|----------|
| `TPESampler` | ✓ | Pareto-based trial splitting with hypervolume contribution weighting |
| `NSGAIISampler` | ✓ | Dedicated evolutionary multi-objective algorithm |
| `RandomSampler` | ✓ | Uniform random sampling (baseline) |
| `CmaEsSampler` | ✗ | Raises error if used with multi-objective study |
| `GPSampler` | ✓ | Multi-output GP with EHVI acquisition function |

The `BaseSampler._raise_error_if_multi_objective()` method [optuna/samplers/_base.py:230-235]() is used by samplers that don't support multi-objective optimization:

```python
def _raise_error_if_multi_objective(self, study: Study) -> None:
    if study._is_multi_objective():
        raise ValueError(
            "If the study is being used for multi-objective optimization, "
            f"{self.__class__.__name__} cannot be used."
        )
```

**CmaEsSampler** explicitly checks this [optuna/samplers/_cmaes.py:363](), [optuna/samplers/_cmaes.py:576]().

Sources: [optuna/samplers/_base.py:230-235](), [optuna/samplers/_cmaes.py:363](), [optuna/samplers/_tpe/sampler.py:571-590](), [tests/samplers_tests/tpe_tests/test_multi_objective_sampler.py:1-502]()

## Reproducibility and Random State

All samplers implement reproducibility through the `seed` parameter and the `reseed_rng()` method [optuna/samplers/_base.py:218-228]().

### Seed Management

**TPESampler** uses `LazyRandomState` for delayed initialization:
```python
class TPESampler(BaseSampler):
    def __init__(self, ..., seed: int | None = None, ...):
        self._rng = LazyRandomState(seed)
        self._random_sampler = RandomSampler(seed=seed)
    
    def reseed_rng(self) -> None:
        self._rng.rng.seed()
        self._random_sampler.reseed_rng()
```

**CmaEsSampler** manages its own RNG and delegates to `independent_sampler`:
```python
class CmaEsSampler(BaseSampler):
    def __init__(self, ..., seed: int | None = None, ...):
        self._independent_sampler = independent_sampler or optuna.samplers.RandomSampler(seed=seed)
        self._cma_rng = LazyRandomState(seed)
    
    def reseed_rng(self) -> None:
        # _cma_rng doesn't require reseeding because relative sampling reseeds in each trial
        self._independent_sampler.reseed_rng()
```

Sources: [optuna/samplers/_tpe/sampler.py:348-349](), [optuna/samplers/_tpe/sampler.py:381-383](), [optuna/samplers/_cmaes.py:278-282](), [optuna/samplers/_cmaes.py:335-337]()

### Deterministic Behavior

When a `seed` is specified, samplers produce identical suggestions across runs:
- TPESampler uses the seed for both its internal RNG and the fallback `RandomSampler`
- CmaEsSampler uses the seed for initializing the CMA-ES algorithm and its independent sampler
- The `reseed_rng()` method is called during parallel optimization to ensure different workers don't suggest identical parameters

Sources: [tests/samplers_tests/tpe_tests/test_sampler.py:22-28](), [tests/samplers_tests/test_cmaes.py:45-74]()

## Integration with Study and Storage

Samplers integrate with Optuna's Study and Storage systems through well-defined interfaces. The Study orchestrates the optimization loop and provides samplers with access to trial history and storage.

### Study-Sampler-Storage Integration

The following diagram shows how samplers interact with the Study and Storage systems:

```mermaid
graph TB
    subgraph "Study Layer"
        StudyOptimize["Study.optimize()"]
        StudyGetTrials["Study._get_trials()"]
    end
    
    subgraph "Sampler Layer"
        SamplerInfer["sampler.infer_relative_search_space()"]
        SamplerRelative["sampler.sample_relative()"]
        SamplerIndependent["sampler.sample_independent()"]
    end
    
    subgraph "Storage Layer"
        GetAllTrials["storage.get_all_trials()"]
        SetSystemAttr["storage.set_trial_system_attr()"]
    end
    
    StudyOptimize --> SamplerInfer
    SamplerInfer --> StudyGetTrials
    StudyGetTrials --> GetAllTrials
    
    SamplerRelative --> StudyGetTrials
    SamplerIndependent --> StudyGetTrials
    
    SamplerRelative -.->|"Store optimizer state"| SetSystemAttr
```

Sources: [optuna/samplers/_tpe/sampler.py:447-453](), [optuna/samplers/_cmaes.py:368-432]()

### Sampler State Persistence

Advanced samplers like `CmaEsSampler` and `TPESampler` store state in trial system attributes for distributed optimization:

**CmaEsSampler** serializes the optimizer:
- Stores pickled optimizer in `system_attrs` with keys like `"cma:optimizer:0"`, `"cma:optimizer:1"`, etc.
- Stores generation number in `"cma:generation"` attribute
- Splits optimizer string into chunks to respect the 2046 character limit [optuna/samplers/_cmaes.py:43-44]()
- Restores optimizer from previous trials in `_restore_optimizer()` [optuna/samplers/_cmaes.py:456-472]()

**TPESampler** with `constant_liar=True`:
- Stores relative sampling parameters in `system_attrs` with keys like `"tpe:relative_params:0"`, etc.
- Also respects the 2046 character limit by splitting the JSON string [optuna/samplers/_tpe/sampler.py:48-50]()
- Uses stored parameters when evaluating running trials [optuna/samplers/_tpe/sampler.py:491-507]()

Sources: [optuna/samplers/_cmaes.py:408-428](), [optuna/samplers/_cmaes.py:447-472](), [optuna/samplers/_tpe/sampler.py:430-439](), [optuna/samplers/_tpe/sampler.py:491-507]()

## Testing and Validation

The sampling system includes comprehensive testing across multiple dimensions:

### Test Coverage Areas

| Test Category | Purpose | Key Validations |
|---------------|---------|----------------|
| Distribution Handling | Verify parameter bounds and constraints | Range validation, type checking, quantization |
| Reproducibility | Ensure deterministic behavior | Seed consistency, cross-process stability |
| Multi-objective Support | Validate multi-objective capabilities | Pareto front handling, value processing |
| Lifecycle Hooks | Test before/after trial callbacks | State validation, error handling |
| Error Conditions | Validate error handling | Invalid parameters, constraint violations |
| Performance | Check sampling efficiency | Large-scale optimization, parallel execution |

### Comprehensive Sampler Testing

The test suite validates all samplers against a common set of scenarios:
- Single parameter optimization
- Multi-parameter optimization with correlations
- Conditional parameter spaces
- Dynamic parameter ranges
- Mixed distribution types
- Edge cases and boundary conditions

Sources: [tests/samplers_tests/test_samplers.py:808-890](), [tests/samplers_tests/test_samplers.py:892-919]()

---

# Page: BaseSampler Interface and Sampling Strategies

# BaseSampler Interface and Sampling Strategies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/reference/integration.rst](docs/source/reference/integration.rst)
- [optuna/integration/botorch.py](optuna/integration/botorch.py)
- [optuna/integration/chainermn.py](optuna/integration/chainermn.py)
- [optuna/integration/sklearn.py](optuna/integration/sklearn.py)
- [optuna/samplers/_base.py](optuna/samplers/_base.py)
- [tests/samplers_tests/test_samplers.py](tests/samplers_tests/test_samplers.py)

</details>



## Purpose and Scope

This document describes the `BaseSampler` abstract class, which defines the interface that all sampling algorithms in Optuna must implement. It covers the distinction between **relative sampling** and **independent sampling**, the core sampling methods (`infer_relative_search_space`, `sample_relative`, `sample_independent`), lifecycle hooks (`before_trial`, `after_trial`, `reseed_rng`), and how samplers integrate with the optimization loop.

For documentation of specific sampler implementations, see:
- Tree-structured Parzen Estimator (TPE): [3.2](#3.2)
- Gaussian Process Sampler: [3.3](#3.3)
- CMA-ES Sampler: [3.4](#3.4)
- Other samplers (Random, Grid, integration samplers): [3.6](#3.6)

For information about how the Study orchestrates the optimization loop, see [2.1](#2.1).

---

## BaseSampler Abstract Class

The `BaseSampler` class is the base interface for all sampling algorithms in Optuna. It defines the contract that samplers must follow to suggest parameter values during optimization.

### Class Definition

```python
# Location: optuna/samplers/_base.py:31-236
class BaseSampler(abc.ABC):
    """Base class for samplers."""
```

All samplers in Optuna inherit from `BaseSampler` and must implement its abstract methods. The class provides both abstract methods that must be overridden and optional lifecycle hooks that can be overridden.

**Sources:** [optuna/samplers/_base.py:31-236]()

---

## Relative vs Independent Sampling

Optuna uses a dual sampling strategy that allows algorithms to leverage parameter relationships when beneficial while maintaining flexibility for dynamic search spaces.

### Sampling Strategy Overview

```mermaid
graph TB
    Trial["Trial Start"] --> InferSpace["infer_relative_search_space()"]
    InferSpace --> RelativeSpace{"Relative Search<br/>Space Defined?"}
    
    RelativeSpace -->|Yes| HasRelative["Parameters in<br/>Relative Space"]
    RelativeSpace -->|No| AllIndependent["All Parameters<br/>Independent"]
    
    HasRelative --> FirstParam{"First Parameter<br/>in Relative Space?"}
    FirstParam -->|Yes| SampleRelative["sample_relative()<br/>(called once)"]
    FirstParam -->|No| UseCache["Use cached<br/>relative samples"]
    
    SampleRelative --> MoreParams{"More Parameters<br/>to Sample?"}
    UseCache --> MoreParams
    AllIndependent --> MoreParams
    
    MoreParams -->|Yes| InSpace{"Parameter in<br/>Relative Space?"}
    MoreParams -->|No| EndTrial["Trial End"]
    
    InSpace -->|Yes| UseCache
    InSpace -->|No| SampleIndependent["sample_independent()<br/>(per parameter)"]
    SampleIndependent --> MoreParams
```

**Relative Sampling** (methods: `infer_relative_search_space`, `sample_relative`):
- Determines multiple parameter values **simultaneously**
- Allows algorithms to exploit correlations between parameters
- Called **once** at the beginning of a trial
- Used by algorithms like CMA-ES, Gaussian Process, multivariate TPE

**Independent Sampling** (method: `sample_independent`):
- Determines a **single** parameter value in isolation
- Does not consider relationships between parameters
- Called **per parameter** not in the relative search space
- Used by algorithms like random sampling, univariate TPE, GridSampler

**Sources:** [optuna/samplers/_base.py:31-62](), [optuna/samplers/_tpe/sampler.py:385-489]()

---

## Core Sampling Methods

### infer_relative_search_space

```python
# optuna/samplers/_base.py:68-93
@abc.abstractmethod
def infer_relative_search_space(
    study: Study, trial: FrozenTrial
) -> dict[str, BaseDistribution]:
```

**Purpose:** Determines which parameters will be sampled using `sample_relative` in the current trial.

**When Called:** Once at the beginning of each trial, before any parameter sampling occurs.

**Return Value:** A dictionary mapping parameter names to their distributions. Parameters not in this dictionary will be sampled independently.

**Implementation Patterns:**

| Sampler Type | Return Value | Reasoning |
|--------------|--------------|-----------|
| RandomSampler | Empty dict `{}` | All parameters sampled independently |
| TPESampler (univariate) | Empty dict `{}` | Each parameter sampled independently |
| TPESampler (multivariate) | Intersection search space | All parameters sampled jointly |
| CmaEsSampler | Intersection search space | Population-based algorithm requires joint sampling |
| GPSampler | Intersection search space | Gaussian Process models parameter correlations |

**Example from TPESampler:**

```python
# optuna/samplers/_tpe/sampler.py:385-412
def infer_relative_search_space(
    self, study: Study, trial: FrozenTrial
) -> dict[str, BaseDistribution]:
    if not self._multivariate:
        return {}  # Independent sampling only
    
    search_space: dict[str, BaseDistribution] = {}
    # Calculate intersection of search spaces across trials
    for name, distribution in self._search_space.calculate(study, use_trial_cache).items():
        if distribution.single():
            continue
        search_space[name] = distribution
    
    return search_space
```

**Sources:** [optuna/samplers/_base.py:68-93](), [optuna/samplers/_tpe/sampler.py:385-412]()

---

### sample_relative

```python
# optuna/samplers/_base.py:95-125
@abc.abstractmethod
def sample_relative(
    study: Study, trial: FrozenTrial, search_space: dict[str, BaseDistribution]
) -> dict[str, Any]:
```

**Purpose:** Samples values for multiple parameters simultaneously, exploiting relationships between them.

**When Called:** Once per trial, immediately after `infer_relative_search_space`, only if the search space is non-empty.

**Arguments:**
- `study`: The Study object containing trial history
- `trial`: The current trial being executed
- `search_space`: The dictionary returned by `infer_relative_search_space`

**Return Value:** Dictionary mapping parameter names to their sampled values.

**Key Characteristics:**
- Called exactly **once** per trial (if relative search space exists)
- All parameters in the search space must be returned
- Can access past trial data to inform sampling decisions
- Failed trials are typically ignored by built-in samplers

**Example from TPESampler:**

```python
# optuna/samplers/_tpe/sampler.py:414-439
def sample_relative(
    self, study: Study, trial: FrozenTrial, search_space: dict[str, BaseDistribution]
) -> dict[str, Any]:
    if search_space == {}:
        return {}
    
    # Get completed/pruned trials
    states = (TrialState.COMPLETE, TrialState.PRUNED)
    trials = study._get_trials(deepcopy=False, states=states, use_cache=True)
    
    # Check if enough trials for TPE
    if len(trials) < self._n_startup_trials:
        return {}  # Fall back to random sampling
    
    return self._sample(study, trial, search_space, use_trial_cache=True)
```

**Sources:** [optuna/samplers/_base.py:95-125](), [optuna/samplers/_tpe/sampler.py:414-453]()

---

### sample_independent

```python
# optuna/samplers/_base.py:127-163
@abc.abstractmethod
def sample_independent(
    study: Study,
    trial: FrozenTrial,
    param_name: str,
    param_distribution: BaseDistribution,
) -> Any:
```

**Purpose:** Samples a value for a single parameter without considering relationships with other parameters.

**When Called:** For each parameter **not** in the relative search space, during objective function execution when `trial.suggest_*()` is called.

**Arguments:**
- `study`: The Study object
- `trial`: The current trial
- `param_name`: Name of the parameter to sample
- `param_distribution`: The distribution for this parameter

**Return Value:** A single parameter value matching the distribution type.

**Key Characteristics:**
- Called **per parameter** not in relative search space
- Can be called multiple times per trial (for different parameters)
- Must handle dynamic search spaces (parameters appearing/disappearing across trials)
- Failed trials are typically ignored by built-in samplers

**Example from TPESampler:**

```python
# optuna/samplers/_tpe/sampler.py:455-489
def sample_independent(
    self,
    study: Study,
    trial: FrozenTrial,
    param_name: str,
    param_distribution: BaseDistribution,
) -> Any:
    states = (TrialState.COMPLETE, TrialState.PRUNED)
    trials = study._get_trials(deepcopy=False, states=states, use_cache=True)
    
    # If insufficient trials, delegate to random sampler
    if len(trials) < self._n_startup_trials:
        return self._random_sampler.sample_independent(
            study, trial, param_name, param_distribution
        )
    
    # Sample single parameter
    search_space = {param_name: param_distribution}
    return self._sample(study, trial, search_space, use_trial_cache=not self._constant_liar)[
        param_name
    ]
```

**Sources:** [optuna/samplers/_base.py:127-163](), [optuna/samplers/_tpe/sampler.py:455-489]()

---

## Lifecycle Hooks

### before_trial

```python
# optuna/samplers/_base.py:165-185
def before_trial(self, study: Study, trial: FrozenTrial) -> None:
```

**Purpose:** Performs pre-processing before the objective function is called.

**When Called:** After trial instantiation, **before** `infer_relative_search_space`.

**Use Cases:**
- Initialize per-trial state
- Validate study configuration
- Set up trial-specific resources
- Delegate to nested samplers (e.g., RandomSampler fallback)

**Example from TPESampler:**

```python
# optuna/samplers/_tpe/sampler.py:664-665
def before_trial(self, study: Study, trial: FrozenTrial) -> None:
    self._random_sampler.before_trial(study, trial)
```

**Sources:** [optuna/samplers/_base.py:165-185](), [optuna/samplers/_tpe/sampler.py:664-665]()

---

### after_trial

```python
# optuna/samplers/_base.py:187-216
def after_trial(
    self,
    study: Study,
    trial: FrozenTrial,
    state: TrialState,
    values: Sequence[float] | None,
) -> None:
```

**Purpose:** Performs post-processing after the objective function returns.

**When Called:** After objective function execution, **before** the trial state is stored.

**Arguments:**
- `state`: The resulting trial state (COMPLETE, PRUNED, or FAIL)
- `values`: The objective values (guaranteed non-None if state is COMPLETE)

**Use Cases:**
- Update sampler-internal state
- Process constraint functions
- Log trial outcomes
- Clean up trial-specific resources

**Example from TPESampler with Constraints:**

```python
# optuna/samplers/_tpe/sampler.py:667-677
def after_trial(
    self,
    study: Study,
    trial: FrozenTrial,
    state: TrialState,
    values: Sequence[float] | None,
) -> None:
    assert state in [TrialState.COMPLETE, TrialState.FAIL, TrialState.PRUNED]
    if self._constraints_func is not None:
        _process_constraints_after_trial(self._constraints_func, study, trial, state)
    self._random_sampler.after_trial(study, trial, state, values)
```

**Sources:** [optuna/samplers/_base.py:187-216](), [optuna/samplers/_tpe/sampler.py:667-677]()

---

### reseed_rng

```python
# optuna/samplers/_base.py:218-228
def reseed_rng(self) -> None:
```

**Purpose:** Reseeds the sampler's random number generator to prevent duplicate suggestions in parallel optimization.

**When Called:** By the Study when `n_jobs > 1` (parallel execution).

**Why Needed:** When trials run in parallel, sampler instances are replicated (pickled/unpickled), which copies the RNG state. Without reseeding, parallel workers would generate identical suggestions.

**Example from TPESampler:**

```python
# optuna/samplers/_tpe/sampler.py:381-383
def reseed_rng(self) -> None:
    self._rng.rng.seed()
    self._random_sampler.reseed_rng()
```

**Sources:** [optuna/samplers/_base.py:218-228](), [optuna/samplers/_tpe/sampler.py:381-383]()

---

## Sampling Workflow in Trial Execution

### Complete Sequence Diagram

```mermaid
sequenceDiagram
    participant User as "User Code"
    participant Study as "Study"
    participant Trial as "Trial"
    participant Sampler as "BaseSampler"
    participant Storage as "Storage"
    
    User->>Study: optimize(objective, n_trials)
    
    loop For each trial
        Study->>Storage: create_new_trial()
        Storage-->>Study: trial_id
        Study->>Trial: new Trial(study, trial_id)
        
        Note over Study,Sampler: Lifecycle Hook
        Study->>Sampler: before_trial(study, trial)
        Sampler-->>Study: (returns)
        
        Note over Study,Sampler: Relative Sampling Phase
        Study->>Sampler: infer_relative_search_space(study, trial)
        Sampler-->>Study: search_space
        
        alt search_space is not empty
            Study->>Sampler: sample_relative(study, trial, search_space)
            Sampler->>Storage: get_all_trials() [read history]
            Storage-->>Sampler: past_trials
            Sampler-->>Study: relative_params
            Study->>Storage: set_trial_param(param, value) [for each]
        end
        
        Note over User,Trial: Objective Function Execution
        Study->>User: objective(trial)
        
        loop For each parameter
            User->>Trial: suggest_float/int/categorical(name, ...)
            
            alt Parameter in relative_params
                Trial-->>User: cached_value
            else Parameter NOT in relative_params
                Note over Trial,Sampler: Independent Sampling
                Trial->>Sampler: sample_independent(study, trial, name, dist)
                Sampler->>Storage: get_all_trials() [read history]
                Storage-->>Sampler: past_trials
                Sampler-->>Trial: value
                Trial->>Storage: set_trial_param(name, value)
                Trial-->>User: value
            end
        end
        
        User-->>Study: return objective_value
        
        Note over Study,Sampler: Lifecycle Hook
        Study->>Sampler: after_trial(study, trial, state, values)
        Sampler-->>Study: (returns)
        
        Study->>Storage: set_trial_state_values(COMPLETE, values)
    end
```

**Key Observations:**

1. **before_trial** is called once before search space inference
2. **infer_relative_search_space** determines the sampling strategy
3. **sample_relative** is called at most once (if search space is non-empty)
4. **sample_independent** is called per parameter not in relative search space
5. **after_trial** is called once after objective function returns
6. Storage access patterns differ: relative sampling typically reads trial history once, independent sampling may read per parameter

**Sources:** [optuna/samplers/_base.py:31-236](), [optuna/samplers/_tpe/sampler.py:385-489]()

---

## Search Space Concepts

### IntersectionSearchSpace

Many samplers use `IntersectionSearchSpace` to compute the relative search space:

```python
# optuna/samplers/_tpe/sampler.py:355
self._search_space = IntersectionSearchSpace(include_pruned=True)
```

**Purpose:** Computes the intersection of search spaces across all trials. Only parameters that appear in **all** trials (with compatible distributions) are included.

**Why Needed:** Relative sampling algorithms (TPE multivariate, CMA-ES, GP) require a fixed set of parameters to model correlations. Dynamic parameters (appearing conditionally) cannot be included.

### Group Decomposed Search Space

TPESampler with `group=True` uses a more sophisticated approach:

```python
# optuna/samplers/_tpe/sampler.py:370
self._group_decomposed_search_space = _GroupDecomposedSearchSpace(True)
```

**Purpose:** Partitions the search space into independent subspaces where each subspace's parameters appear together consistently across trials.

**Use Case:** Handles conditional search spaces where parameters appear in groups (e.g., `x` and `y` always appear together, `z` and `w` always appear together, but the two groups never overlap).

**Sources:** [optuna/samplers/_tpe/sampler.py:355-370](), [optuna/search_space/group_decomposed.py:1-600]()

---

## Sampler Hierarchy

### Class Hierarchy Diagram

```mermaid
graph TB
    BaseSampler["BaseSampler<br/>(abstract base)<br/>optuna/samplers/_base.py"]
    
    RandomSampler["RandomSampler<br/>optuna/samplers/_random.py"]
    GridSampler["GridSampler<br/>optuna/samplers/_grid.py"]
    TPESampler["TPESampler<br/>optuna/samplers/_tpe/sampler.py"]
    GPSampler["GPSampler<br/>optuna/samplers/_gp/sampler.py"]
    CmaEsSampler["CmaEsSampler<br/>optuna/samplers/_cmaes.py"]
    NSGAIISampler["NSGAIISampler<br/>optuna/samplers/_nsgaii/"]
    QMCSampler["QMCSampler<br/>optuna/samplers/_qmc.py"]
    
    IntegrationSamplers["Integration Samplers<br/>(BoTorchSampler, SkoptSampler)<br/>optuna-integration package"]
    
    BaseSampler --> RandomSampler
    BaseSampler --> GridSampler
    BaseSampler --> TPESampler
    BaseSampler --> GPSampler
    BaseSampler --> CmaEsSampler
    BaseSampler --> NSGAIISampler
    BaseSampler --> QMCSampler
    BaseSampler --> IntegrationSamplers
    
    RandomSampler -.fallback for.-> TPESampler
    RandomSampler -.fallback for.-> CmaEsSampler
```

**Sampling Strategy by Sampler:**

| Sampler | Relative Sampling | Independent Sampling | Notes |
|---------|-------------------|----------------------|-------|
| RandomSampler | Never | Always | Baseline sampler |
| GridSampler | Always | Never | Exhaustive search |
| TPESampler (univariate) | Never | Always | Default mode |
| TPESampler (multivariate) | Always | Fallback only | `multivariate=True` |
| GPSampler | Always | Fallback only | Requires numeric parameters |
| CmaEsSampler | Always | Never | Evolution strategy |
| NSGAIISampler | Always | Never | Multi-objective genetic algorithm |
| QMCSampler | Always | Never | Quasi-random sequences |

**Sources:** [optuna/samplers/_base.py:31-236](), [optuna/samplers/_tpe/sampler.py:72-288]()

---

## Common Implementation Patterns

### Pattern 1: Delegating to RandomSampler

Many advanced samplers delegate to `RandomSampler` during the initial "warm-up" phase:

```python
# optuna/samplers/_tpe/sampler.py:349
self._random_sampler = RandomSampler(seed=seed)

# optuna/samplers/_tpe/sampler.py:466-469
if len(trials) < self._n_startup_trials:
    return self._random_sampler.sample_independent(
        study, trial, param_name, param_distribution
    )
```

**Why:** Advanced algorithms (TPE, GP, CMA-ES) require a minimum number of observations to build models. Random sampling provides diverse initial data.

### Pattern 2: Empty Relative Search Space

Samplers that only use independent sampling return an empty dictionary:

```python
# Simple pattern
def infer_relative_search_space(self, study: Study, trial: FrozenTrial) -> dict[str, BaseDistribution]:
    return {}
```

### Pattern 3: Trial State Filtering

Most samplers filter trials by state when reading history:

```python
# optuna/samplers/_tpe/sampler.py:447-448
states = (TrialState.COMPLETE, TrialState.PRUNED)
trials = study._get_trials(deepcopy=False, states=states, use_cache=True)
```

**Typical Pattern:**
- **COMPLETE** and **PRUNED**: Used for modeling (have objective values or intermediate values)
- **RUNNING**: Sometimes included with "constant liar" strategy to avoid duplicate suggestions
- **FAIL** and **WAITING**: Typically ignored

**Sources:** [optuna/samplers/_tpe/sampler.py:349-489](), [optuna/samplers/_random.py:1-200]()

---

## Independent Sampling Warning

When a sampler with `multivariate=True` falls back to independent sampling, it may emit a warning:

```python
# optuna/samplers/_base.py:21-28
_INDEPENDENT_SAMPLING_WARNING_TEMPLATE = (
    "The parameter `{param_name}` in Trial#{trial_number} is sampled independently "
    "using `{independent_sampler_name}` instead of `{sampler_name}`, potentially "
    "degrading the optimization performance. This fallback happend because "
    "{fallback_reason}. You can suppress this warning by setting "
    "`warn_independent_sampling` to `False` in the constructor of `{sampler_name}` if "
    "this independent sampling is intended behavior."
)
```

**Common Reasons for Independent Sampling:**
- Dynamic search space (parameters appearing conditionally)
- New parameter introduced mid-study
- Distribution incompatibility across trials
- Parameter excluded from intersection search space

**Example from TPESampler:**

```python
# optuna/samplers/_tpe/sampler.py:471-484
if self._warn_independent_sampling and self._multivariate:
    # Avoid independent warning at the first sampling of `param_name`.
    if any(param_name in trial.params for trial in trials):
        _logger.warning(
            _INDEPENDENT_SAMPLING_WARNING_TEMPLATE.format(
                param_name=param_name,
                trial_number=trial.number,
                independent_sampler_name=self._random_sampler.__class__.__name__,
                sampler_name=self.__class__.__name__,
                fallback_reason=(
                    "dynamic search space is not supported for `multivariate=True`"
                ),
            )
        )
```

**Sources:** [optuna/samplers/_base.py:21-28](), [optuna/samplers/_tpe/sampler.py:471-484]()

---

## Constraints Support

The `BaseSampler` provides infrastructure for constraint handling:

```python
# optuna/samplers/_base.py:238
_CONSTRAINTS_KEY = "constraints"

# optuna/samplers/_base.py:241-267
def _process_constraints_after_trial(
    constraints_func: Callable[[FrozenTrial], Sequence[float]],
    study: Study,
    trial: FrozenTrial,
    state: TrialState,
) -> None:
```

**Constraint Convention:**
- Constraints are evaluated via a user-provided function
- Return value is a sequence of floats
- **Feasible**: All values ≤ 0
- **Infeasible**: Any value > 0
- Stored in trial system attributes with key `"constraints"`

**Usage in Samplers:**

Samplers like TPESampler accept a `constraints_func` parameter and process constraints in `after_trial`:

```python
# optuna/samplers/_tpe/sampler.py:675-676
if self._constraints_func is not None:
    _process_constraints_after_trial(self._constraints_func, study, trial, state)
```

**Sources:** [optuna/samplers/_base.py:238-267](), [optuna/samplers/_tpe/sampler.py:357-380]()

---

## Code Entity Reference

### Key Classes and Files

| Entity | Location | Purpose |
|--------|----------|---------|
| `BaseSampler` | [optuna/samplers/_base.py:31-236]() | Abstract base class for all samplers |
| `infer_relative_search_space` | [optuna/samplers/_base.py:68-93]() | Abstract method for search space inference |
| `sample_relative` | [optuna/samplers/_base.py:95-125]() | Abstract method for joint parameter sampling |
| `sample_independent` | [optuna/samplers/_base.py:127-163]() | Abstract method for single parameter sampling |
| `before_trial` | [optuna/samplers/_base.py:165-185]() | Lifecycle hook (optional) |
| `after_trial` | [optuna/samplers/_base.py:187-216]() | Lifecycle hook (optional) |
| `reseed_rng` | [optuna/samplers/_base.py:218-228]() | RNG reseeding hook (optional) |
| `_CONSTRAINTS_KEY` | [optuna/samplers/_base.py:238]() | System attribute key for constraints |
| `_process_constraints_after_trial` | [optuna/samplers/_base.py:241-267]() | Helper for constraint processing |
| `_INDEPENDENT_SAMPLING_WARNING_TEMPLATE` | [optuna/samplers/_base.py:21-28]() | Warning message template |

### Sampler Implementations

| Sampler | File | Relative | Independent |
|---------|------|----------|-------------|
| RandomSampler | [optuna/samplers/_random.py]() | No | Yes |
| GridSampler | [optuna/samplers/_grid.py]() | Yes | No |
| TPESampler | [optuna/samplers/_tpe/sampler.py:72-678]() | Optional | Yes |
| GPSampler | [optuna/samplers/_gp/sampler.py]() | Yes | Fallback |
| CmaEsSampler | [optuna/samplers/_cmaes.py]() | Yes | No |
| NSGAIISampler | [optuna/samplers/_nsgaii/]() | Yes | No |
| QMCSampler | [optuna/samplers/_qmc.py]() | Yes | No |

**Sources:** [optuna/samplers/_base.py:1-267](), [optuna/samplers/_tpe/sampler.py:1-678]()

---

# Page: Tree-structured Parzen Estimator (TPE)

# Tree-structured Parzen Estimator (TPE)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/samplers/_tpe/parzen_estimator.py](optuna/samplers/_tpe/parzen_estimator.py)
- [optuna/samplers/_tpe/sampler.py](optuna/samplers/_tpe/sampler.py)
- [tests/samplers_tests/tpe_tests/test_multi_objective_sampler.py](tests/samplers_tests/tpe_tests/test_multi_objective_sampler.py)
- [tests/samplers_tests/tpe_tests/test_parzen_estimator.py](tests/samplers_tests/tpe_tests/test_parzen_estimator.py)
- [tests/samplers_tests/tpe_tests/test_sampler.py](tests/samplers_tests/tpe_tests/test_sampler.py)

</details>



This page documents the Tree-structured Parzen Estimator (TPE) sampling algorithm, Optuna's default optimizer for single-objective optimization and a sophisticated option for multi-objective problems. TPE models the search space using Gaussian Mixture Models (GMMs) to iteratively propose promising parameter configurations.

For information about the base sampler interface and sampling strategies, see [BaseSampler Interface and Sampling Strategies](#3.1). For multi-objective optimization algorithms more broadly, see [Multi-Objective Optimization](#3.5).

## Overview

TPE is a sequential model-based optimization algorithm that maintains two Gaussian Mixture Models:
- **l(x)**: Models parameter values associated with good objective values (below trials)
- **g(x)**: Models parameter values associated with poor objective values (above trials)

On each trial, TPE samples from `l(x)` and selects the configuration that maximizes the acquisition function `l(x)/g(x)`, effectively favoring regions where good trials are dense and poor trials are sparse.

**Sources:** [optuna/samplers/_tpe/sampler.py:73-99]()

## Core Algorithm Flow

```mermaid
graph TB
    Start["Trial Begins"] --> CheckStartup["Check if n_trials >= n_startup_trials"]
    CheckStartup -->|"No"| Random["Use RandomSampler"]
    CheckStartup -->|"Yes"| GetTrials["Fetch completed/pruned trials<br/>from storage"]
    
    GetTrials --> Split["_split_trials()<br/>Divide into below/above"]
    Split --> Below["below_trials: top γ(n) trials"]
    Split --> Above["above_trials: remaining trials"]
    
    Below --> BuildL["Build l(x) Parzen estimator<br/>_build_parzen_estimator()"]
    Above --> BuildG["Build g(x) Parzen estimator<br/>_build_parzen_estimator()"]
    
    BuildL --> SampleL["Sample n_ei_candidates from l(x)"]
    BuildG --> EvalAcq["Compute acquisition function<br/>log(l(x)) - log(g(x))"]
    SampleL --> EvalAcq
    
    EvalAcq --> Select["Select sample with max<br/>acquisition value"]
    Select --> Return["Return parameter values"]
    Random --> Return
    
    style Split fill:#f9f9f9
    style BuildL fill:#f9f9f9
    style BuildG fill:#f9f9f9
```

**Sources:** [optuna/samplers/_tpe/sampler.py:521-561]()

## Implementation Architecture

### Class Structure

```mermaid
classDiagram
    class TPESampler {
        -_ParzenEstimatorParameters _parzen_estimator_parameters
        -int _n_startup_trials
        -int _n_ei_candidates
        -Callable _gamma
        -bool _multivariate
        -bool _group
        -bool _constant_liar
        -Callable _constraints_func
        -RandomSampler _random_sampler
        -IntersectionSearchSpace _search_space
        -_GroupDecomposedSearchSpace _group_decomposed_search_space
        +infer_relative_search_space()
        +sample_relative()
        +sample_independent()
        -_sample()
        -_build_parzen_estimator()
        -_compute_acquisition_func()
    }
    
    class _ParzenEstimator {
        -dict~str,BaseDistribution~ _search_space
        -_MixtureOfProductDistribution _mixture_distribution
        +sample()
        +log_pdf()
        -_calculate_distributions()
        -_calculate_categorical_distributions()
        -_calculate_numerical_distributions()
    }
    
    class _ParzenEstimatorParameters {
        +float prior_weight
        +bool consider_magic_clip
        +bool consider_endpoints
        +Callable weights
        +bool multivariate
        +dict categorical_distance_func
    }
    
    class _MixtureOfProductDistribution {
        +ndarray weights
        +list~_BatchedDistributions~ distributions
        +sample()
        +log_pdf()
    }
    
    TPESampler --> _ParzenEstimator : creates
    TPESampler --> _ParzenEstimatorParameters : stores
    _ParzenEstimator --> _ParzenEstimatorParameters : uses
    _ParzenEstimator --> _MixtureOfProductDistribution : contains
    TPESampler --> RandomSampler : delegates startup trials
    
    class RandomSampler {
        +sample_independent()
    }
```

**Sources:** [optuna/samplers/_tpe/sampler.py:72-384](), [optuna/samplers/_tpe/parzen_estimator.py:27-252]()

### Key Methods and Responsibilities

| Method | Class | Responsibility |
|--------|-------|----------------|
| `sample_relative()` | `TPESampler` | Samples multiple correlated parameters using multivariate TPE |
| `sample_independent()` | `TPESampler` | Samples a single parameter independently |
| `_sample()` | `TPESampler` | Core TPE logic: split trials, build estimators, compute acquisition |
| `_build_parzen_estimator()` | `TPESampler` | Constructs `_ParzenEstimator` from trial observations |
| `_split_trials()` | Module function | Divides trials into below/above based on objective values |
| `_calculate_distributions()` | `_ParzenEstimator` | Creates GMM kernels for a parameter |
| `sample()` | `_ParzenEstimator` | Generates candidate samples from the mixture model |
| `log_pdf()` | `_ParzenEstimator` | Evaluates log probability density |

**Sources:** [optuna/samplers/_tpe/sampler.py:414-619](), [optuna/samplers/_tpe/parzen_estimator.py:80-130]()

## Parzen Estimator Construction

The `_ParzenEstimator` class builds a Gaussian Mixture Model by placing a kernel at each observed parameter value, plus a prior kernel.

### GMM Construction Process

```mermaid
graph LR
    Obs["Observations<br/>{param: [v1, v2, ..., vn]}"] --> Transform["Transform to<br/>internal representation"]
    Transform --> Kernels["Create n kernels<br/>centered at observations"]
    Kernels --> Prior["Add prior kernel<br/>at midpoint of range"]
    Prior --> Weights["Compute kernel weights<br/>via weights() function"]
    Weights --> GMM["_MixtureOfProductDistribution"]
    
    style Transform fill:#f9f9f9
    style Kernels fill:#f9f9f9
    style Prior fill:#f9f9f9
```

### Variance Calculation

For numerical parameters, kernel bandwidth (sigma) is computed based on parameter locality:

**Univariate Mode** (default):
```
sigma[i] = max(sorted_values[i+1] - sorted_values[i-1])
```
This ensures each kernel width spans to its neighboring observations.

**Multivariate Mode**:
```
sigma = 0.2 * n^(-1/(d+4)) * (high - low)
```
Where `n` is the number of observations and `d` is the search space dimensionality.

**Magic Clip**: When enabled, clamps sigma to `[range/min(100, n_kernels+1), range]` to prevent overly narrow or wide kernels.

**Sources:** [optuna/samplers/_tpe/parzen_estimator.py:168-232]()

### Distribution Types

| Distribution Type | Batched Implementation | Parameters |
|-------------------|------------------------|------------|
| `FloatDistribution` | `_BatchedTruncNormDistributions` | mu, sigma, low, high |
| `FloatDistribution(log=True)` | `_BatchedTruncLogNormDistributions` | mu, sigma, low, high |
| `FloatDistribution(step=x)` | `_BatchedDiscreteTruncNormDistributions` | mu, sigma, low, high, step |
| `IntDistribution` | `_BatchedDiscreteTruncNormDistributions` | mu, sigma, low, high, step=1 |
| `IntDistribution(log=True)` | `_BatchedDiscreteTruncLogNormDistributions` | mu, sigma, low, high, step=1 |
| `CategoricalDistribution` | `_BatchedCategoricalDistributions` | weights[n_kernels, n_choices] |

**Sources:** [optuna/samplers/_tpe/parzen_estimator.py:117-251]()

## Trial Splitting Strategy

The `_split_trials()` function divides completed trials into "below" (good) and "above" (poor) sets based on objective values and trial states.

```mermaid
graph TB
    AllTrials["All Trials<br/>(COMPLETE/PRUNED/RUNNING)"] --> Filter["Filter by state"]
    
    Filter --> Complete["COMPLETE trials"]
    Filter --> Pruned["PRUNED trials"]
    Filter --> Running["RUNNING trials<br/>(if constant_liar=True)"]
    Filter --> Infeasible["Infeasible trials<br/>(if constraints enabled)"]
    
    Complete --> SplitComplete["_split_complete_trials()<br/>Sort by objective value<br/>Take top γ(n)"]
    Pruned --> SplitPruned["_split_pruned_trials()<br/>Sort by (step, intermediate_value)<br/>Take top γ(n) - len(below_complete)"]
    Infeasible --> SplitInfeas["_split_infeasible_trials()<br/>Sort by constraint violation<br/>Take top γ(n) - len(below_complete+pruned)"]
    
    SplitComplete --> BelowComplete["below_complete"]
    SplitComplete --> AboveComplete["above_complete"]
    SplitPruned --> BelowPruned["below_pruned"]
    SplitPruned --> AbovePruned["above_pruned"]
    SplitInfeas --> BelowInfeas["below_infeasible"]
    SplitInfeas --> AboveInfeas["above_infeasible"]
    
    BelowComplete --> MergeBelow["below_trials<br/>(sorted by trial number)"]
    BelowPruned --> MergeBelow
    BelowInfeas --> MergeBelow
    
    AboveComplete --> MergeAbove["above_trials<br/>(sorted by trial number)"]
    AbovePruned --> MergeAbove
    AboveInfeas --> MergeAbove
    Running --> MergeAbove
    
    style SplitComplete fill:#f9f9f9
    style SplitPruned fill:#f9f9f9
    style SplitInfeas fill:#f9f9f9
```

### Gamma Function

The `gamma` parameter controls how many trials form the "below" group. Default implementations:

- **Optuna default**: `gamma(n) = min(ceil(0.1 * n), 25)`
- **Hyperopt default**: `gamma(n) = min(ceil(0.25 * sqrt(n)), 25)`

**Sources:** [optuna/samplers/_tpe/sampler.py:53-58](), [optuna/samplers/_tpe/sampler.py:687-823]()

### Pruned Trial Scoring

Pruned trials are ranked by their last intermediate value and the step at which they were pruned:

```
score = (-step, intermediate_value)  # if direction=minimize
score = (-step, -intermediate_value) # if direction=maximize
```

Earlier pruning indicates worse performance, so trials are sorted with step priority.

**Sources:** [optuna/samplers/_tpe/sampler.py:783-801]()

## Multi-Objective TPE (MOTPE)

For multi-objective optimization, TPE uses non-dominated sorting and hypervolume contribution to weight trials in the "below" group.

### Below Trial Selection

```mermaid
graph TB
    CompleteTrials["Multi-objective<br/>Complete Trials"] --> NDSort["_fast_non_domination_rank()<br/>Assign rank to each trial"]
    
    NDSort --> CheckFull{"All ranks fit<br/>in n_below?"}
    CheckFull -->|"Yes"| DirectSplit["Take all trials<br/>up to cutoff rank"]
    CheckFull -->|"No"| Tiebreak["Last rank exceeds n_below<br/>Need tiebreaking"]
    
    Tiebreak --> HSSP["_solve_hssp()<br/>Hypervolume Subset Selection<br/>Select subset with max hypervolume"]
    HSSP --> DirectSplit
    DirectSplit --> BelowSet["below_trials"]
    
    style NDSort fill:#f9f9f9
    style HSSP fill:#f9f9f9
```

### Hypervolume-Based Weighting

For trials in the "below" group, weights are computed based on hypervolume contribution:

```
weight[i] = max(contrib[i] / max(contribs), EPS)
```

Where `contrib[i]` is the hypervolume lost by removing trial `i` from the Pareto front.

**Algorithm**:
1. Compute reference point: `ref = max(1.1 * worst, 0.9 * worst)`
2. Identify Pareto front trials using `_is_pareto_front()`
3. For each Pareto trial, compute leave-one-out hypervolume
4. Contribution = `HV(all) - HV(all \ {trial_i})`
5. Normalize weights and assign `EPS` to non-Pareto trials

For objectives > 3, an approximation is used to avoid computational cost.

**Sources:** [optuna/samplers/_tpe/sampler.py:825-864](), [optuna/samplers/_tpe/sampler.py:746-780]()

## Multivariate and Group Sampling

### Multivariate TPE

When `multivariate=True`, TPE models the joint distribution of parameters rather than treating them independently. This captures correlations between parameters.

**Differences from Independent TPE**:
- Uses `sample_relative()` to suggest all parameters at once
- Computes sigma based on dimensionality: `sigma = 0.2 * n^(-1/(d+4)) * (high - low)`
- Returns empty dict from `infer_relative_search_space()` when disabled

**Sources:** [optuna/samplers/_tpe/sampler.py:385-412](), [optuna/samplers/_tpe/parzen_estimator.py:186-194]()

### Group Decomposition

When `group=True` (requires `multivariate=True`), the search space is decomposed into independent subspaces based on conditional dependencies.

```mermaid
graph TB
    Study["Study with<br/>conditional parameters"] --> GDS["_GroupDecomposedSearchSpace"]
    GDS --> Analyze["Analyze past trials<br/>to find dependencies"]
    
    Analyze --> Partition["Partition search space<br/>into maximal subspaces"]
    Partition --> SS1["Subspace 1:<br/>{x, y}"]
    Partition --> SS2["Subspace 2:<br/>{z}"]
    
    SS1 --> Sample1["Sample {x,y}<br/>jointly with multivariate TPE"]
    SS2 --> Sample2["Sample {z}<br/>with multivariate TPE"]
    
    Sample1 --> Merge["Merge samples"]
    Sample2 --> Merge
    Merge --> Result["Complete parameter set"]
    
    style Analyze fill:#f9f9f9
    style Partition fill:#f9f9f9
```

**Decomposition Logic**: A subspace is maximal if, for each completed trial, the intersection of the subspace with the trial's search space equals either the subspace itself or the empty set. This ensures parameters are only grouped if they consistently appear together.

**Sources:** [optuna/samplers/_tpe/sampler.py:394-426](), [optuna/search_space/group_decomposed.py]()

## Special Features

### Constant Liar Strategy

When `constant_liar=True`, running trials are included in the "above" group to discourage parallel workers from sampling nearby configurations.

**Mechanism**:
1. Include `RUNNING` trials in `_split_trials()` states
2. Place all running trials in the "above" group
3. Store sampled parameters in trial system attributes for other workers to access

**Use Case**: Distributed optimization where multiple workers run simultaneously and objective evaluations are expensive.

**Sources:** [optuna/samplers/_tpe/sampler.py:528-539](), [optuna/samplers/_tpe/sampler.py:430-439]()

### Constraint Handling

When `constraints_func` is provided, infeasible trials (constraint violation > 0) are handled specially:

1. Infeasible trials are separated during splitting
2. Sorted by total constraint violation: `sum(v for v in constraints if v > 0)`
3. Assigned weight `EPS` in multi-objective below group weighting
4. Constraints evaluated via `_process_constraints_after_trial()` in `after_trial()`

**Sources:** [optuna/samplers/_tpe/sampler.py:700-716](), [optuna/samplers/_tpe/sampler.py:804-823]()

### Categorical Distance Function

The `categorical_distance_func` parameter allows users to provide domain knowledge about relationships between categorical choices.

**Default Behavior**: All categories treated equally (discrete distribution).

**With Distance Function**:
```python
categorical_distance_func = {
    "optimizer": lambda x, y: {"adam": 0, "sgd": 1, "rmsprop": 2}[x] - ...
}
```

Weights are computed using:
```
weight[choice] = exp(-((dist[choice] / max_dist)^2) * coef)
```

Where `coef = log(n_kernels/prior_weight) * log(n_choices) / log(6)`.

**Sources:** [optuna/samplers/_tpe/parzen_estimator.py:152-162]()

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `consider_prior` | `bool` | `True` | Always `True` as of v4.3.0 (deprecated parameter) |
| `prior_weight` | `float` | `1.0` | Weight of the prior kernel in GMM |
| `consider_magic_clip` | `bool` | `True` | Clamp kernel widths to prevent extreme values |
| `consider_endpoints` | `bool` | `False` | Include domain endpoints in sigma calculation |
| `n_startup_trials` | `int` | `10` | Use random sampling for first N trials |
| `n_ei_candidates` | `int` | `24` | Number of candidates to sample from `l(x)` |
| `gamma` | `Callable` | `default_gamma` | Function to compute number of below trials |
| `weights` | `Callable` | `default_weights` | Function to compute kernel weights |
| `seed` | `int \| None` | `None` | Random seed for reproducibility |
| `multivariate` | `bool` | `False` | Enable multivariate TPE |
| `group` | `bool` | `False` | Enable group-decomposed multivariate TPE |
| `warn_independent_sampling` | `bool` | `True` | Warn when falling back to independent sampling |
| `constant_liar` | `bool` | `False` | Penalize running trials for distributed optimization |
| `constraints_func` | `Callable \| None` | `None` | Function to compute constraint violations |
| `categorical_distance_func` | `dict \| None` | `None` | Distance functions for categorical parameters |

**Sources:** [optuna/samplers/_tpe/sampler.py:289-379]()

### Default Weight Function

```python
def default_weights(x: int) -> np.ndarray:
    if x == 0:
        return np.asarray([])
    elif x < 25:
        return np.ones(x)
    else:
        ramp = np.linspace(1.0 / x, 1.0, num=x - 25)
        flat = np.ones(25)
        return np.concatenate([ramp, flat], axis=0)
```

This gives recent observations higher weight while maintaining some influence from older trials.

**Sources:** [optuna/samplers/_tpe/sampler.py:61-69]()

## Hyperopt Compatibility

TPE originates from the Hyperopt library. Optuna provides a `hyperopt_parameters()` static method to replicate Hyperopt's default configuration:

```python
TPESampler.hyperopt_parameters() == {
    "consider_prior": True,
    "prior_weight": 1.0,
    "consider_magic_clip": True,
    "consider_endpoints": False,
    "n_startup_trials": 20,
    "n_ei_candidates": 24,
    "gamma": hyperopt_default_gamma,
    "weights": default_weights,
}
```

The main difference: `n_startup_trials=20` (vs. Optuna's default of 10) and `gamma` uses the square-root formula.

**Sources:** [optuna/samplers/_tpe/sampler.py:622-662]()

## Performance Optimizations

1. **Trial Caching**: The `use_trial_cache` parameter controls whether to use cached trial data, reducing storage queries.

2. **Relative Params Storage**: When `constant_liar=True` and `multivariate=True`, sampled parameters are stored in trial system attributes (chunked to respect 2046 character limit) for access by parallel workers.

3. **Fast Non-Domination Rank**: Multi-objective splitting uses optimized non-dominated sorting with early termination at rank boundaries.

4. **LRU Cache for HSSP**: The `_solve_hssp_with_cache()` function uses `@lru_cache` to avoid recomputing hypervolume subset selections for identical trial sets.

**Sources:** [optuna/samplers/_tpe/sampler.py:430-439](), [optuna/samplers/_tpe/sampler.py:769-775]()

---

# Page: Gaussian Process Sampler

# Gaussian Process Sampler

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/_gp/acqf.py](optuna/_gp/acqf.py)
- [optuna/_gp/batched_lbfgsb.py](optuna/_gp/batched_lbfgsb.py)
- [optuna/_gp/gp.py](optuna/_gp/gp.py)
- [optuna/_gp/optim_mixed.py](optuna/_gp/optim_mixed.py)
- [optuna/_gp/optim_sample.py](optuna/_gp/optim_sample.py)
- [optuna/_gp/prior.py](optuna/_gp/prior.py)
- [optuna/_gp/search_space.py](optuna/_gp/search_space.py)
- [optuna/samplers/_gp/sampler.py](optuna/samplers/_gp/sampler.py)
- [optuna/terminator/improvement/emmr.py](optuna/terminator/improvement/emmr.py)
- [optuna/terminator/improvement/evaluator.py](optuna/terminator/improvement/evaluator.py)
- [tests/gp_tests/test_acqf.py](tests/gp_tests/test_acqf.py)
- [tests/gp_tests/test_batched_lbfgsb.py](tests/gp_tests/test_batched_lbfgsb.py)
- [tests/gp_tests/test_gp.py](tests/gp_tests/test_gp.py)
- [tests/gp_tests/test_search_space.py](tests/gp_tests/test_search_space.py)
- [tests/samplers_tests/test_gp.py](tests/samplers_tests/test_gp.py)

</details>



## Purpose and Scope

This document describes the Gaussian Process (GP) based Bayesian optimization sampler implementation in Optuna. The GPSampler uses a Gaussian process as a surrogate model of the objective function and optimizes an acquisition function to suggest the next set of parameters. This document covers the GP model, acquisition functions, optimization algorithms, and the complete sampling workflow.

For information about the BaseSampler interface that GPSampler implements, see [BaseSampler Interface and Sampling Strategies](#3.1). For multi-objective optimization specifics including NSGA-II/III, see [Multi-Objective Optimization](#3.5). For the Tree-structured Parzen Estimator (TPE) sampler, an alternative Bayesian optimization approach, see [Tree-structured Parzen Estimator](#3.2).

---

## Architecture Overview

The GPSampler consists of four main subsystems:

1. **GP Model** (`GPRegressor`): Fits a Gaussian process to past trial data
2. **Acquisition Functions**: Compute expected utility of candidate parameters
3. **Mixed Optimization**: Optimizes acquisition functions over continuous and discrete parameters
4. **Search Space Management**: Normalizes and transforms parameters

```mermaid
graph TB
    subgraph "GPSampler Class"
        Sampler[GPSampler<br/>optuna/samplers/_gp/sampler.py]
    end
    
    subgraph "GP Model Subsystem"
        GPR[GPRegressor<br/>_gp/gp.py]
        Kernel[Matern52Kernel<br/>_gp/gp.py]
        Prior[default_log_prior<br/>_gp/prior.py]
    end
    
    subgraph "Acquisition Function Subsystem"
        BaseAcqf[BaseAcquisitionFunc<br/>_gp/acqf.py]
        LogEI[LogEI<br/>Single-objective]
        LogEHVI[LogEHVI<br/>Multi-objective]
        ConstrainedLogEI[ConstrainedLogEI<br/>With constraints]
        ConstrainedLogEHVI[ConstrainedLogEHVI<br/>Multi-obj + constraints]
    end
    
    subgraph "Optimization Subsystem"
        OptimMixed[optimize_acqf_mixed<br/>_gp/optim_mixed.py]
        BatchedLBFGSB[batched_lbfgsb<br/>_gp/batched_lbfgsb.py]
        LocalSearch[local_search_mixed_batched<br/>_gp/optim_mixed.py]
    end
    
    subgraph "Search Space Subsystem"
        SearchSpace[SearchSpace<br/>_gp/search_space.py]
    end
    
    Sampler --> GPR
    Sampler --> BaseAcqf
    Sampler --> OptimMixed
    Sampler --> SearchSpace
    
    GPR --> Kernel
    GPR --> Prior
    
    BaseAcqf --> LogEI
    BaseAcqf --> LogEHVI
    BaseAcqf --> ConstrainedLogEI
    BaseAcqf --> ConstrainedLogEHVI
    
    OptimMixed --> LocalSearch
    LocalSearch --> BatchedLBFGSB
    
    LogEI --> GPR
    LogEHVI --> GPR
    ConstrainedLogEI --> LogEI
    ConstrainedLogEHVI --> LogEHVI
```

**Sources:** [optuna/samplers/_gp/sampler.py:1-474](), [optuna/_gp/gp.py:1-374](), [optuna/_gp/acqf.py:1-316](), [optuna/_gp/optim_mixed.py:1-330]()

---

## GPSampler Class

The `GPSampler` class at [optuna/samplers/_gp/sampler.py:62-457]() is the main entry point implementing the `BaseSampler` interface.

### Key Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `_rng` | `LazyRandomState` | Random number generator |
| `_independent_sampler` | `BaseSampler` | Fallback sampler for startup trials |
| `_n_startup_trials` | `int` | Number of random trials before GP fitting (default: 10) |
| `_deterministic` | `bool` | Whether objective is deterministic |
| `_constraints_func` | `Callable` | Optional constraint function |
| `_gprs_cache_list` | `list[GPRegressor]` | Cached GP models for objectives |
| `_constraints_gprs_cache_list` | `list[GPRegressor]` | Cached GP models for constraints |
| `_n_preliminary_samples` | `int` | QMC samples for acquisition optimization (default: 2048) |
| `_n_local_search` | `int` | Number of local search starting points (default: 10) |

**Sources:** [optuna/samplers/_gp/sampler.py:174-206]()

### Main Methods

```mermaid
graph LR
    subgraph "BaseSampler Interface Methods"
        InferSpace["infer_relative_search_space()<br/>line 221-230"]
        SampleRel["sample_relative()<br/>line 303-426"]
        SampleInd["sample_independent()<br/>line 428-442"]
        AfterTrial["after_trial()<br/>line 447-456"]
    end
    
    subgraph "Internal Methods"
        OptimizeAcqf["_optimize_acqf()<br/>line 232-247"]
        GetConstraints["_get_constraints_acqf_args()<br/>line 249-287"]
        GetBestParams["_get_best_params_for_multi_objective()<br/>line 289-301"]
    end
    
    SampleRel --> OptimizeAcqf
    SampleRel --> GetConstraints
    SampleRel --> GetBestParams
```

**Sources:** [optuna/samplers/_gp/sampler.py:221-456]()

---

## Gaussian Process Model

### GPRegressor Class

The `GPRegressor` class at [optuna/_gp/gp.py:93-316]() implements the Gaussian process surrogate model.

#### Initialization Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `is_categorical` | `torch.Tensor` | Boolean mask for categorical parameters |
| `X_train` | `torch.Tensor` | Training parameter values (normalized) |
| `y_train` | `torch.Tensor` | Training objective values (standardized) |
| `inverse_squared_lengthscales` | `torch.Tensor` | Kernel lengthscale parameters (1/l²) |
| `kernel_scale` | `torch.Tensor` | Kernel amplitude parameter |
| `noise_var` | `torch.Tensor` | Observation noise variance |

**Sources:** [optuna/_gp/gp.py:94-116]()

### Matern 5/2 Kernel

The kernel function at [optuna/_gp/gp.py:149-177]() computes:

```
k(x₁, x₂) = kernel_scale × exp(-√5d) × (1 + √5d + 5d²/3)
```

where `d² = Σᵢ (x₁ᵢ - x₂ᵢ)² × inverse_squared_lengthscales[i]`.

For categorical parameters, the squared difference is replaced with the Hamming distance: `(x₁ᵢ ≠ x₂ᵢ)`.

The `Matern52Kernel` class at [optuna/_gp/gp.py:63-91]() implements custom forward/backward passes for numerical stability at `squared_distance = 0`.

**Sources:** [optuna/_gp/gp.py:63-177]()

### Hyperparameter Optimization

The `_fit_kernel_params` method at [optuna/_gp/gp.py:251-315]() optimizes kernel hyperparameters by maximizing the marginal log-likelihood:

```
log p(y|X, θ) = -½ log|C| - ½ yᵀC⁻¹y - N/2 log(2π)
```

where `C = K(X,X) + noise_var × I` and `θ = {lengthscales, kernel_scale, noise_var}`.

**Optimization Process:**

1. Apply log transform to enforce positivity: `raw_params = log(θ)`
2. Minimize negative log-likelihood using L-BFGS-B at [optuna/_gp/gp.py:295-302]()
3. Add prior regularization from [optuna/_gp/prior.py:19-33]()
4. Cache Cholesky decomposition for posterior inference at [optuna/_gp/gp.py:122-147]()

**Sources:** [optuna/_gp/gp.py:216-315](), [optuna/_gp/prior.py:1-34]()

### Posterior Inference

The `posterior` method at [optuna/_gp/gp.py:179-214]() computes the predictive distribution:

```
μ(x) = k(x, X)ᵀ C⁻¹ y
σ²(x) = k(x, x) - k(x, X)ᵀ C⁻¹ k(x, X)
```

using the cached Cholesky factorization `C = LLᵀ`.

**Sources:** [optuna/_gp/gp.py:179-214]()

---

## Acquisition Functions

All acquisition functions inherit from `BaseAcquisitionFunc` at [optuna/_gp/acqf.py:95-114]().

### Single-Objective: LogEI

The `LogEI` class at [optuna/_gp/acqf.py:116-137]() implements log expected improvement:

```
logEI(x) = log E[max(0, f(x) - f_best)]
```

where the expectation is over the GP posterior. The implementation uses the numerically stable formulation from [Ament et al. (2023)](https://arxiv.org/abs/2310.20708).

The `standard_logei` function at [optuna/_gp/acqf.py:65-87]() computes:

```
logEI(z) = log(z × Φ(z) + φ(z))
```

where `z = (μ(x) - f_best) / σ(x)`, `Φ` is the standard normal CDF, and `φ` is the PDF.

**Sources:** [optuna/_gp/acqf.py:65-137]()

### Multi-Objective: LogEHVI

The `LogEHVI` class at [optuna/_gp/acqf.py:223-278]() implements log expected hypervolume improvement using quasi-Monte Carlo integration:

```
logEHVI(x) = log E[HVI(x)] ≈ log(1/M Σₘ HVI(f(x) + εₘ))
```

where `εₘ ~ N(0, Σ(x))` are sampled from a Sobol sequence at [optuna/_gp/acqf.py:33-42]().

The `logehvi` function at [optuna/_gp/acqf.py:45-62]() computes the log hypervolume improvement by:

1. Partitioning non-dominated space into boxes
2. Computing volume contributions for each box
3. Aggregating via log-sum-exp for numerical stability

**Sources:** [optuna/_gp/acqf.py:33-62](), [optuna/_gp/acqf.py:223-278]()

### Constrained Optimization

#### ConstrainedLogEI

The `ConstrainedLogEI` class at [optuna/_gp/acqf.py:195-220]() combines objective and constraint acquisition:

```
acqf(x) = logEI(x) + Σᵢ logPI_i(x)
```

where `logPI_i(x) = log P(cᵢ(x) ≤ 0)` is the log probability of satisfying constraint `i`.

**Sources:** [optuna/_gp/acqf.py:195-220]()

#### ConstrainedLogEHVI

The `ConstrainedLogEHVI` class at [optuna/_gp/acqf.py:281-315]() extends EHVI with constraints:

```
acqf(x) = logEHVI(x) + Σᵢ logPI_i(x)
```

When all trials are infeasible, only the constraint satisfaction is optimized.

**Sources:** [optuna/_gp/acqf.py:281-315]()

---

## Acquisition Function Optimization

### Mixed Optimization Strategy

The `optimize_acqf_mixed` function at [optuna/_gp/optim_mixed.py:280-329]() optimizes acquisition functions over mixed search spaces:

```mermaid
graph TB
    Start[Start] --> QMC[Sample n_preliminary_samples<br/>using Sobol QMC]
    QMC --> EvalSamples[Evaluate acquisition function<br/>on all samples]
    EvalSamples --> SelectBest[Select best sample]
    SelectBest --> Roulette[Roulette selection of<br/>n_local_search-1 samples]
    Roulette --> Warmstart[Add user-provided warmstart points]
    Warmstart --> LocalSearch[local_search_mixed_batched]
    LocalSearch --> Return[Return best parameter]
    
    LocalSearch --> GradientAscent[Gradient ascent for<br/>continuous parameters]
    LocalSearch --> DiscreteSearch[Line/exhaustive search<br/>for discrete parameters]
    GradientAscent --> Check{Converged?}
    DiscreteSearch --> Check
    Check -->|No| GradientAscent
    Check -->|Yes| Return
```

**Sources:** [optuna/_gp/optim_mixed.py:280-329]()

### Local Search

The `local_search_mixed_batched` function at [optuna/_gp/optim_mixed.py:232-277]() alternates between:

1. **Continuous optimization** via `_gradient_ascent_batched` at [optuna/_gp/optim_mixed.py:29-94]()
2. **Discrete optimization** via `_local_search_discrete_batched` at [optuna/_gp/optim_mixed.py:208-229]()

#### Gradient Ascent with Preconditioning

The gradient ascent applies preconditioning by scaling parameters by lengthscales:

```
z = x / l  where l = lengthscales
```

This equalizes variance across dimensions and improves convergence. The optimization domain becomes `[0, 1/l]` instead of `[0, 1]`.

**Sources:** [optuna/_gp/optim_mixed.py:29-94]()

#### Discrete Parameter Optimization

For discrete parameters, the optimization strategy at [optuna/_gp/optim_mixed.py:189-206]() depends on the number of choices:

| Condition | Method | Implementation |
|-----------|--------|----------------|
| ≤ 16 choices OR categorical | Exhaustive search | `_exhaustive_search` at [line 97-118]() |
| > 16 choices AND integer | Line search with interpolation | `_discrete_line_search` at [line 121-186]() |

**Sources:** [optuna/_gp/optim_mixed.py:97-229]()

### Batched L-BFGS-B

The `batched_lbfgsb` function at [optuna/_gp/batched_lbfgsb.py:89-168]() performs multiple L-BFGS-B optimizations simultaneously:

**With greenlet (parallel execution):**
- Uses coroutines to interleave multiple optimizations at [optuna/_gp/batched_lbfgsb.py:34-86]()
- Batches gradient evaluations for efficiency
- Falls back to sequential if greenlet unavailable

**Sequential fallback:**
- Runs L-BFGS-B for each starting point sequentially at [optuna/_gp/batched_lbfgsb.py:141-167]()

**Sources:** [optuna/_gp/batched_lbfgsb.py:1-169]()

---

## Search Space Management

### SearchSpace Class

The `SearchSpace` class at [optuna/_gp/search_space.py:36-110]() handles parameter transformations:

```mermaid
graph LR
    subgraph "Parameter Types"
        Float[FloatDistribution]
        Int[IntDistribution]
        Cat[CategoricalDistribution]
    end
    
    subgraph "Scale Types"
        Linear[LINEAR]
        Log[LOG]
        Categorical[CATEGORICAL]
    end
    
    subgraph "Normalization"
        Normalize[Normalize to [0,1]]
        Denormalize[Denormalize]
    end
    
    Float --> Linear
    Float --> Log
    Int --> Linear
    Int --> Log
    Cat --> Categorical
    
    Linear --> Normalize
    Log --> Normalize
    Categorical --> Normalize
    
    Normalize --> GPModel[GP Model]
    GPModel --> Denormalize
```

**Sources:** [optuna/_gp/search_space.py:30-110]()

### Normalization Functions

**`_normalize_one_param`** at [optuna/_gp/search_space.py:127-140]():

For linear scale:
```
normalized = (value - low) / (high - low)
```

For log scale:
```
normalized = (log(value) - log(low)) / (log(high) - log(low))
```

For categorical:
```
normalized = category_index
```

**`_unnormalize_one_param`** at [optuna/_gp/search_space.py:112-124]() performs the inverse transformation.

**Sources:** [optuna/_gp/search_space.py:112-140]()

### Sampling

The `sample_normalized_params` method at [optuna/_gp/search_space.py:87-90]() wraps `_sample_normalized_params` at [line 160-183]() which uses Sobol quasi-random sampling:

1. Generate Sobol sequence in `[0,1]^d`
2. Round integer parameters to nearest grid point
3. Sample categorical uniformly from choices

**Sources:** [optuna/_gp/search_space.py:160-183]()

---

## Complete Sampling Workflow

```mermaid
sequenceDiagram
    participant Study
    participant GPSampler
    participant SearchSpace
    participant GPRegressor
    participant AcqFunc
    participant Optimizer
    
    Study->>GPSampler: sample_relative(study, trial, search_space)
    
    alt n_trials < n_startup_trials
        GPSampler-->>Study: {} (use independent sampler)
    else
        GPSampler->>SearchSpace: get_normalized_params(trials)
        SearchSpace-->>GPSampler: normalized_params
        
        GPSampler->>GPSampler: _standardize_values(values)
        
        loop For each objective
            GPSampler->>GPRegressor: fit_kernel_params(X, Y)
            GPRegressor->>GPRegressor: _fit_kernel_params()
            GPRegressor->>GPRegressor: marginal_log_likelihood()
            GPRegressor->>GPRegressor: _cache_matrix()
            GPRegressor-->>GPSampler: fitted_gpr
        end
        
        alt constraints_func is not None
            loop For each constraint
                GPSampler->>GPRegressor: fit_kernel_params(X, C)
                GPRegressor-->>GPSampler: constraint_gpr
            end
        end
        
        alt Single-objective
            GPSampler->>AcqFunc: Create LogEI or ConstrainedLogEI
        else Multi-objective
            GPSampler->>AcqFunc: Create LogEHVI or ConstrainedLogEHVI
        end
        
        GPSampler->>Optimizer: optimize_acqf_mixed(acqf, best_params)
        Optimizer->>Optimizer: Sample preliminary points (QMC)
        Optimizer->>Optimizer: Roulette selection
        Optimizer->>Optimizer: local_search_mixed_batched()
        
        loop Until convergence
            Optimizer->>Optimizer: _gradient_ascent_batched()
            Optimizer->>Optimizer: _local_search_discrete_batched()
        end
        
        Optimizer-->>GPSampler: optimal_normalized_params
        
        GPSampler->>SearchSpace: get_unnormalized_param()
        SearchSpace-->>GPSampler: params_dict
        
        GPSampler-->>Study: params_dict
    end
```

**Sources:** [optuna/samplers/_gp/sampler.py:303-426]()

---

## Data Standardization and Caching

### Value Standardization

The `_standardize_values` function at [optuna/samplers/_gp/sampler.py:53-58]() standardizes objective and constraint values:

```
standardized = (values - mean) / max(std, EPS)
```

This prevents numerical issues in GP fitting and ensures comparable scales across objectives.

**Sources:** [optuna/samplers/_gp/sampler.py:53-58]()

### GP Model Caching

The GPSampler caches fitted GP models in:
- `_gprs_cache_list`: Objective function GPs at [line 192]()
- `_constraints_gprs_cache_list`: Constraint function GPs at [line 193]()

Caching provides warm-start hyperparameters for the next trial, speeding up optimization. The cache is cleared when the search space changes at [lines 258-263]() and [lines 324-329]().

**Sources:** [optuna/samplers/_gp/sampler.py:192-193](), [optuna/samplers/_gp/sampler.py:258-263](), [optuna/samplers/_gp/sampler.py:324-329]()

---

## Configuration Parameters

### GPSampler Constructor

| Parameter | Default | Description |
|-----------|---------|-------------|
| `seed` | `None` | Random seed |
| `independent_sampler` | `RandomSampler` | Sampler for startup trials |
| `n_startup_trials` | `10` | Number of random trials before GP fitting |
| `deterministic_objective` | `False` | Fix noise variance to minimum value |
| `constraints_func` | `None` | Constraint evaluation function |
| `warn_independent_sampling` | `True` | Warn when falling back to independent sampling |

**Sources:** [optuna/samplers/_gp/sampler.py:174-196]()

### Internal Control Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `_n_preliminary_samples` | `2048` | Number of QMC samples for initialization |
| `_n_local_search` | `10` | Number of local search starting points |
| `_tol` | `1e-4` | Convergence tolerance for local search |
| `_log_prior` | `default_log_prior` | Prior for kernel hyperparameters |
| `_minimum_noise` | `1e-6` | Minimum noise variance |

**Sources:** [optuna/samplers/_gp/sampler.py:188-205]()

---

## Constraint Handling

### Constraints Function

The `constraints_func` parameter accepts a callable that takes a `FrozenTrial` and returns a sequence of constraint values. A constraint is violated if its value is strictly positive.

```python
def constraints_func(trial: FrozenTrial) -> Sequence[float]:
    # Return constraint values
    # c <= 0 is feasible
    # c > 0 is infeasible
    return [c1, c2, ...]
```

**Sources:** [optuna/samplers/_gp/sampler.py:155-162]()

### Constraint Processing

The `after_trial` method at [optuna/samplers/_gp/sampler.py:447-456]() calls `_process_constraints_after_trial` to evaluate and store constraints in trial system attributes under the key `_CONSTRAINTS_KEY`.

The `_get_constraint_vals_and_feasibility` function at [optuna/samplers/_gp/sampler.py:459-473]() retrieves constraint values and computes feasibility:

```python
is_feasible = np.all(constraint_vals <= 0, axis=1)
```

**Sources:** [optuna/samplers/_gp/sampler.py:447-473]()

### Constraint Acquisition Functions

Constraints are incorporated by fitting separate GP models at [optuna/samplers/_gp/sampler.py:266-286]() and using `LogPI` (log probability of improvement) acquisition functions at [optuna/_gp/acqf.py:140-160]():

```
logPI(x) = log P(c(x) <= threshold)
         = log Φ((μ(x) - threshold) / σ(x))
```

where `Φ` is the standard normal CDF.

**Sources:** [optuna/samplers/_gp/sampler.py:249-287](), [optuna/_gp/acqf.py:140-160]()

---

## Handling Infinite Values

The `warn_and_convert_inf` function at [optuna/_gp/gp.py:47-60]() handles infinite objective values by clipping them to the min/max finite values:

```python
clipped_values = np.clip(
    values,
    np.min(finite_values, axis=0),
    np.max(finite_values, axis=0)
)
```

This prevents numerical issues in GP fitting when the objective function returns infinity (e.g., due to constraint violations or numerical errors).

**Sources:** [optuna/_gp/gp.py:47-60]()

---

## Integration with Study

The GPSampler integrates with Optuna's study system through the standard sampler interface:

1. **`infer_relative_search_space`** at [line 221-230](): Returns parameters that can be sampled jointly using the GP model
2. **`sample_relative`** at [line 303-426](): Suggests parameters using GP-based optimization
3. **`sample_independent`** at [line 428-442](): Falls back to independent sampler for dynamic parameters
4. **`after_trial`** at [line 447-456](): Processes constraints after trial completion

When the search space is dynamic (changes between trials), GPSampler logs a warning and falls back to the independent sampler at [line 207-215]().

**Sources:** [optuna/samplers/_gp/sampler.py:207-456]()

---

## Testing and Validation

The test suite validates:

1. **GP model fitting**: [tests/gp_tests/test_gp.py:57-107]() verifies hyperparameter optimization
2. **Acquisition functions**: [tests/gp_tests/test_acqf.py:60-143]() checks gradient computation
3. **Batched optimization**: [tests/gp_tests/test_batched_lbfgsb.py:82-119]() compares against scipy
4. **Search space transformations**: [tests/gp_tests/test_search_space.py:15-196]() validates normalization
5. **Constraint handling**: [tests/samplers_tests/test_gp.py:52-115]() tests constraint integration
6. **Convergence behavior**: [tests/samplers_tests/test_gp.py:23-49]() checks numerical stability

**Sources:** [tests/gp_tests/test_gp.py:1-143](), [tests/gp_tests/test_acqf.py:1-144](), [tests/gp_tests/test_batched_lbfgsb.py:1-154](), [tests/gp_tests/test_search_space.py:1-197](), [tests/samplers_tests/test_gp.py:1-130]()

---

# Page: CMA-ES Sampler

# CMA-ES Sampler

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/integration/cma.py](optuna/integration/cma.py)
- [optuna/samplers/_cmaes.py](optuna/samplers/_cmaes.py)
- [tests/samplers_tests/test_cmaes.py](tests/samplers_tests/test_cmaes.py)

</details>



## Purpose and Scope

This page documents the **CmaEsSampler**, an evolutionary optimization algorithm implementation in Optuna. The sampler uses the Covariance Matrix Adaptation Evolution Strategy (CMA-ES) algorithm via the external `cmaes` library to suggest parameter values during hyperparameter optimization.

This page covers the sampler's architecture, state management, parameter transformation, and three algorithmic variants (standard CMA, SepCMA, and CMAwM). For information about the base sampler interface and sampling strategies, see [BaseSampler Interface](#3.1). For other evolutionary algorithms like NSGA-II/III, see [Multi-Objective Optimization](#3.5).

**Sources:** [optuna/samplers/_cmaes.py:47-246]()

---

## Overview

CMA-ES (Covariance Matrix Adaptation Evolution Strategy) is a population-based evolutionary algorithm that maintains and adapts a multivariate Gaussian distribution to model promising regions of the search space. The algorithm iteratively samples a population of candidate solutions, evaluates them, and updates the distribution's mean vector and covariance matrix based on the best-performing solutions.

The `CmaEsSampler` wraps three variants from the `cmaes` library:
- **CMA**: Standard CMA-ES with full covariance matrix
- **SepCMA**: Separable CMA-ES with diagonal covariance matrix (faster for high dimensions)
- **CMAwM**: CMA-ES with Margin (handles discrete parameters better)

### Key Characteristics

| Feature | Support |
|---------|---------|
| **Distributions Supported** | `FloatDistribution`, `IntDistribution` (including with `step`) |
| **Distributions Unsupported** | `CategoricalDistribution` |
| **Multi-objective** | No (single-objective only) |
| **Parallelization** | Limited (some trials may be wasted) |
| **Dynamic Search Space** | No (uses `IntersectionSearchSpace`) |

**Sources:** [optuna/samplers/_cmaes.py:47-106](), [optuna/samplers/_cmaes.py:339-355]()

---

## Architecture and Integration

### System Context

```mermaid
graph TB
    subgraph "Optuna Core"
        Study["Study"]
        Trial["Trial"]
        Storage["Storage<br/>(RDB/InMemory)"]
    end
    
    subgraph "CmaEsSampler Components"
        CmaEsSampler["CmaEsSampler"]
        IndependentSampler["_independent_sampler<br/>(RandomSampler)"]
        SearchSpace["_search_space<br/>(IntersectionSearchSpace)"]
        CmaRng["_cma_rng<br/>(LazyRandomState)"]
        Transform["_SearchSpaceTransform"]
    end
    
    subgraph "External cmaes Library"
        CMA["cmaes.CMA<br/>(Standard)"]
        SepCMA["cmaes.SepCMA<br/>(Separable)"]
        CMAwM["cmaes.CMAwM<br/>(With Margin)"]
        WarmStart["cmaes.get_warm_start_mgd"]
    end
    
    Study -->|"sample_relative"| CmaEsSampler
    Study -->|"infer_relative_search_space"| CmaEsSampler
    CmaEsSampler -->|"fallback"| IndependentSampler
    CmaEsSampler -->|"calculate"| SearchSpace
    CmaEsSampler -->|"transform/untransform"| Transform
    
    CmaEsSampler -.->|"creates one of"| CMA
    CmaEsSampler -.->|"creates one of"| SepCMA
    CmaEsSampler -.->|"creates one of"| CMAwM
    CmaEsSampler -.->|"warm start"| WarmStart
    
    CmaEsSampler -->|"persist optimizer"| Storage
    CmaEsSampler -->|"restore optimizer"| Storage
    
    Storage -->|"set_trial_system_attr"| Trial
```

The `CmaEsSampler` acts as an adapter between Optuna's trial system and the `cmaes` library's optimizer implementations. It manages optimizer state persistence, parameter space transformation, and fallback to independent sampling when CMA-ES cannot be used.

**Sources:** [optuna/samplers/_cmaes.py:1-40](), [optuna/samplers/_cmaes.py:248-334]()

---

## Class Structure

### CmaEsSampler Initialization

The sampler is configured through its constructor with options controlling algorithm variant, initialization, and behavior:

```mermaid
graph LR
    subgraph "Algorithm Selection"
        UseSepCMA["use_separable_cma<br/>(bool)"]
        WithMargin["with_margin<br/>(bool)"]
        LrAdapt["lr_adapt<br/>(bool)"]
    end
    
    subgraph "Initialization"
        X0["x0<br/>(dict[str, Any])"]
        Sigma0["sigma0<br/>(float)"]
        SourceTrials["source_trials<br/>(list[FrozenTrial])"]
    end
    
    subgraph "Behavior"
        NStartup["n_startup_trials<br/>(int)"]
        ConsiderPruned["consider_pruned_trials<br/>(bool)"]
        Popsize["popsize<br/>(int)"]
        Seed["seed<br/>(int)"]
    end
    
    subgraph "Determines Variant"
        UseSepCMA -->|"True"| SepCMA["SepCMA"]
        WithMargin -->|"True"| CMAwM["CMAwM"]
        LrAdapt -->|"True"| CMALr["CMA with lr_adapt"]
        UseSepCMA -->|"False"| Standard["Standard CMA"]
        WithMargin -->|"False"| Standard
        LrAdapt -->|"False"| Standard
    end
    
    SourceTrials -.->|"enables"| WarmStart["Warm Starting"]
```

**Sources:** [optuna/samplers/_cmaes.py:248-334]()

### Attribute Prefixes

Different variants use distinct system attribute prefixes to avoid conflicts when switching algorithms:

| Variant | Prefix | Example Attribute Key |
|---------|--------|----------------------|
| Standard CMA | `"cma:"` | `"cma:optimizer:0"`, `"cma:generation"` |
| SepCMA | `"sepcma:"` | `"sepcma:optimizer:0"`, `"sepcma:generation"` |
| CMAwM | `"cmawm:"` | `"cmawm:optimizer:0"`, `"cmawm:generation"` |

**Sources:** [optuna/samplers/_cmaes.py:290-295](), [optuna/samplers/_cmaes.py:434-440]()

---

## CMA-ES Variants

### Standard CMA-ES

The default variant maintains a full covariance matrix to model parameter correlations.

**Initialization:** [optuna/samplers/_cmaes.py:558-567]()
```python
cmaes.CMA(
    mean=mean,              # Center of search distribution
    sigma=sigma0,           # Initial step size
    cov=cov,                # Optional covariance matrix (warm start)
    bounds=trans.bounds,    # Parameter bounds
    seed=seed,
    n_max_resampling=10 * n_dimension,
    population_size=popsize,
    lr_adapt=lr_adapt       # Learning rate adaptation
)
```

**Use Cases:**
- Default choice for most problems
- Handles parameter correlations effectively
- Best for low-to-medium dimensional spaces (< 100 dimensions)

**Sources:** [optuna/samplers/_cmaes.py:558-567]()

---

### SepCMA (Separable CMA-ES)

A variant that constrains the covariance matrix to be diagonal, reducing computational complexity and memory usage.

**Initialization:** [optuna/samplers/_cmaes.py:518-533]()
```python
cmaes.SepCMA(
    mean=mean,
    sigma=sigma0,
    bounds=trans.bounds,
    seed=seed,
    n_max_resampling=10 * n_dimension,
    population_size=popsize
)
```

**Advantages:**
- Faster for high-dimensional problems
- Lower memory footprint (O(n) vs O(n²))
- Increased learning rate for covariance matrix

**Limitations:**
- Cannot model parameter correlations
- Not effective for non-separable functions
- Disabled for 1D search spaces with a warning

**Sources:** [optuna/samplers/_cmaes.py:518-533](), [optuna/samplers/_cmaes.py:200-208]()

---

### CMAwM (CMA-ES with Margin)

A variant designed to handle discrete and mixed-integer optimization better by preventing premature convergence to single discrete values.

**Initialization:** [optuna/samplers/_cmaes.py:535-556]()
```python
cmaes.CMAwM(
    mean=mean,
    sigma=sigma0,
    bounds=trans.bounds,
    steps=steps,            # Step sizes for discrete dimensions
    cov=cov,
    seed=seed,
    n_max_resampling=10 * n_dimension,
    population_size=popsize
)
```

**Step Calculation:** [optuna/samplers/_cmaes.py:536-545]()
- Continuous dimensions (`step=None` or `log=True`): `steps[i] = 0.0`
- Discrete dimensions: `steps[i] = dist.step / (dist.high - dist.low)`

**Key Differences:**
- Does not transform discrete distributions (handled internally)
- Maintains margins around discrete values
- Cannot be combined with `use_separable_cma`

**Sources:** [optuna/samplers/_cmaes.py:535-556](), [optuna/samplers/_cmaes.py:210-220]()

---

## State Management and Persistence

### Optimizer State Serialization

The CMA-ES optimizer state must persist across trials to maintain the evolving search distribution. The sampler serializes the optimizer using pickle and stores it in trial system attributes.

```mermaid
graph TB
    subgraph "Trial N Completes"
        OptimizerN["Optimizer<br/>(generation=N)"]
        TellN["optimizer.tell(solutions)"]
        PickleN["pickle.dumps(optimizer).hex()"]
        SplitN["_split_optimizer_str"]
    end
    
    subgraph "Storage"
        SysAttrs["Trial System Attributes<br/>cma:optimizer:0<br/>cma:optimizer:1<br/>...<br/>cma:generation"]
    end
    
    subgraph "Trial N+1 Starts"
        RestoreN1["_restore_optimizer"]
        ConcatN1["_concat_optimizer_attrs"]
        UnpickleN1["pickle.loads(bytes.fromhex())"]
        OptimizerN1["Optimizer<br/>(generation=N)"]
        AskN1["optimizer.ask()"]
    end
    
    OptimizerN --> TellN
    TellN --> PickleN
    PickleN --> SplitN
    SplitN -->|"set_trial_system_attr"| SysAttrs
    
    SysAttrs -->|"get from latest trial"| RestoreN1
    RestoreN1 --> ConcatN1
    ConcatN1 --> UnpickleN1
    UnpickleN1 --> OptimizerN1
    OptimizerN1 --> AskN1
```

### String Splitting for Storage Compatibility

RDBStorage limits system attribute values to 2045 characters. The optimizer state is split into multiple attributes:

**Split Logic:** [optuna/samplers/_cmaes.py:447-454]()
```python
def _split_optimizer_str(self, optimizer_str: str) -> dict[str, str]:
    optimizer_len = len(optimizer_str)
    attrs = {}
    for i in range(math.ceil(optimizer_len / _SYSTEM_ATTR_MAX_LENGTH)):
        start = i * _SYSTEM_ATTR_MAX_LENGTH
        end = min((i + 1) * _SYSTEM_ATTR_MAX_LENGTH, optimizer_len)
        attrs[f"{self._attr_key_optimizer}:{i}"] = optimizer_str[start:end]
    return attrs
```

**Concatenation Logic:** [optuna/samplers/_cmaes.py:442-445]()
```python
def _concat_optimizer_attrs(self, optimizer_attrs: dict[str, str]) -> str:
    return "".join(
        optimizer_attrs[f"{self._attr_key_optimizer}:{i}"] 
        for i in range(len(optimizer_attrs))
    )
```

**Sources:** [optuna/samplers/_cmaes.py:42-44](), [optuna/samplers/_cmaes.py:442-454](), [optuna/samplers/_cmaes.py:456-472]()

---

## Parameter Space Transformation

### Search Space Inference

The sampler uses `IntersectionSearchSpace` to determine the common parameter space across completed trials:

**Inference Logic:** [optuna/samplers/_cmaes.py:339-355]()
```python
def infer_relative_search_space(
    self, study, trial
) -> dict[str, BaseDistribution]:
    search_space: dict[str, BaseDistribution] = {}
    for name, distribution in self._search_space.calculate(study).items():
        if distribution.single():
            # Skip distributions with single value
            continue
        if not isinstance(distribution, (FloatDistribution, IntDistribution)):
            # Skip categorical distributions
            continue
        search_space[name] = distribution
    return search_space
```

### Transformation to [0, 1] Space

CMA-ES operates on continuous parameters. The `_SearchSpaceTransform` class handles conversion:

**Transform Creation:** [optuna/samplers/_cmaes.py:373-375]()
```python
trans = _SearchSpaceTransform(
    search_space, 
    transform_step=not self._with_margin,  # CMAwM handles steps internally
    transform_0_1=True                      # Normalize to [0, 1]
)
```

**Transformation Flow:**

```mermaid
graph LR
    subgraph "User Space"
        UserParams["User Parameters<br/>x: 5.0 (range: -10 to 10)<br/>y: 3 (range: 0 to 10)"]
    end
    
    subgraph "CMA-ES Space"
        TransformedParams["Transformed Parameters<br/>x: 0.75<br/>y: 0.3"]
    end
    
    subgraph "_SearchSpaceTransform"
        Transform["transform()"]
        Untransform["untransform()"]
        Bounds["bounds array<br/>[[0, 1], [0, 1]]"]
    end
    
    UserParams -->|"transform()"| Transform
    Transform --> TransformedParams
    TransformedParams -->|"untransform()"| Untransform
    Untransform --> UserParams
```

**Step Handling:**
- For standard CMA and SepCMA: Steps are transformed (e.g., `suggest_int(0, 10)` becomes continuous in [0, 1])
- For CMAwM: Steps are preserved and passed to the optimizer

**Sources:** [optuna/samplers/_cmaes.py:373-375](), [optuna/samplers/_cmaes.py:430-431]()

---

## Sampling Lifecycle

### Complete Sampling Flow

```mermaid
sequenceDiagram
    participant Study
    participant CmaEsSampler
    participant Storage
    participant Optimizer["cmaes.CMA/SepCMA/CMAwM"]
    participant Transform["_SearchSpaceTransform"]
    
    Study->>CmaEsSampler: sample_relative(study, trial, search_space)
    
    CmaEsSampler->>CmaEsSampler: _get_trials(study)
    alt n_trials < n_startup_trials
        CmaEsSampler-->>Study: {} (use independent sampler)
    end
    
    CmaEsSampler->>Transform: Create transform (search_space)
    
    CmaEsSampler->>Storage: _restore_optimizer(completed_trials)
    alt Optimizer not found
        CmaEsSampler->>CmaEsSampler: _init_optimizer(trans, direction)
        CmaEsSampler->>Optimizer: Create CMA/SepCMA/CMAwM
    end
    
    alt optimizer.dim != len(trans.bounds)
        Note over CmaEsSampler: Dynamic search space detected
        CmaEsSampler-->>Study: {} (fallback to independent)
    end
    
    CmaEsSampler->>CmaEsSampler: _get_solution_trials(trials, generation)
    
    alt len(solution_trials) >= population_size
        loop For each solution trial
            CmaEsSampler->>Transform: transform(trial.params)
        end
        CmaEsSampler->>Optimizer: tell(solutions)
        CmaEsSampler->>Optimizer: pickle.dumps(optimizer).hex()
        CmaEsSampler->>Storage: set_trial_system_attr (optimizer state)
    end
    
    CmaEsSampler->>Optimizer: _rng.seed(seed)
    CmaEsSampler->>Optimizer: ask()
    Optimizer-->>CmaEsSampler: params (in [0,1] space)
    
    alt optimizer is CMAwM
        CmaEsSampler->>Storage: set_trial_system_attr("x_for_tell", x_for_tell)
    end
    
    CmaEsSampler->>Storage: set_trial_system_attr("generation", generation)
    
    CmaEsSampler->>Transform: untransform(params)
    Transform-->>CmaEsSampler: external_values
    
    CmaEsSampler-->>Study: external_values
```

**Sources:** [optuna/samplers/_cmaes.py:357-432]()

### Generation and Population Management

Trials are organized into generations. Each generation contains `population_size` trials:

**Solution Trial Filtering:** [optuna/samplers/_cmaes.py:620-624]()
```python
def _get_solution_trials(
    self, trials: list[FrozenTrial], generation: int
) -> list[FrozenTrial]:
    generation_attr_key = self._attr_key_generation
    return [t for t in trials 
            if generation == t.system_attrs.get(generation_attr_key, -1)]
```

The optimizer is updated (`tell()`) only when a full generation of `population_size` trials completes.

**Sources:** [optuna/samplers/_cmaes.py:393-412](), [optuna/samplers/_cmaes.py:620-624]()

---

## Warm Starting

Warm starting enables transfer learning by initializing CMA-ES from previous optimization results.

### Warm Start Initialization

**Configuration:** [optuna/samplers/_cmaes.py:496-513]()
```python
# Prepare source solutions
sign = 1 if direction == StudyDirection.MINIMIZE else -1
source_solutions = [
    (trans.transform(t.params), sign * cast(float, t.value))
    for t in self._source_trials
    if t.state in expected_states
    and _is_compatible_search_space(trans, t.distributions)
]

# Get warm start parameters
mean, sigma0, cov = cmaes.get_warm_start_mgd(source_solutions)
```

### Compatibility Check

Source trials must have compatible search spaces:

**Compatibility Function:** [optuna/samplers/_cmaes.py:639-643]()
```python
def _is_compatible_search_space(
    trans: _SearchSpaceTransform, 
    search_space: dict[str, BaseDistribution]
) -> bool:
    intersection_size = len(
        set(trans._search_space.keys()).intersection(search_space.keys())
    )
    return intersection_size == len(trans._search_space) == len(search_space)
```

### Restrictions

**Validation:** [optuna/samplers/_cmaes.py:312-327]()
- Cannot use `x0` or `sigma0` with `source_trials`
- Cannot use `use_separable_cma=True` with `source_trials`
- Raises `ValueError` if no compatible source trials found

**Sources:** [optuna/samplers/_cmaes.py:234-244](), [optuna/samplers/_cmaes.py:496-513](), [optuna/samplers/_cmaes.py:639-643]()

---

## Trial Filtering and Pruned Trials

### Handling Completed and Pruned Trials

**Trial Collection:** [optuna/samplers/_cmaes.py:601-618]()
```python
def _get_trials(self, study) -> list[FrozenTrial]:
    complete_trials = []
    for t in study._get_trials(deepcopy=False, use_cache=True):
        if t.state == TrialState.COMPLETE:
            complete_trials.append(t)
        elif (
            t.state == TrialState.PRUNED
            and len(t.intermediate_values) > 0
            and self._consider_pruned_trials
        ):
            # Use best intermediate value as final value
            _, value = max(t.intermediate_values.items())
            if value is None:
                continue
            copied_t = copy.deepcopy(t)
            copied_t.value = value
            complete_trials.append(copied_t)
    return complete_trials
```

### Pruned Trial Handling

When `consider_pruned_trials=True`:
1. Pruned trials with intermediate values are included
2. The best (maximum) intermediate value becomes the trial's value
3. A deep copy is made to avoid modifying the original trial

**Recommended Usage:** [optuna/samplers/_cmaes.py:195-198]()
- Set `False` when using `MedianPruner`
- Set `True` when using `HyperbandPruner`

**Sources:** [optuna/samplers/_cmaes.py:185-198](), [optuna/samplers/_cmaes.py:601-618]()

---

## Configuration Parameters

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x0` | `dict[str, Any] \| None` | `None` | Initial parameter values (midpoint of ranges if not specified) |
| `sigma0` | `float \| None` | `None` | Initial step size (computed as `min_range/6` if not specified) |
| `seed` | `int \| None` | `None` | Random seed for reproducibility |
| `n_startup_trials` | `int` | `1` | Number of trials before CMA-ES starts |
| `independent_sampler` | `BaseSampler \| None` | `None` | Sampler for unsupported parameters (defaults to `RandomSampler`) |
| `warn_independent_sampling` | `bool` | `True` | Emit warnings when falling back to independent sampling |
| `consider_pruned_trials` | `bool` | `False` | Include pruned trials using best intermediate value |
| `popsize` | `int \| None` | `None` | Population size (uses algorithm default if not specified) |
| `use_separable_cma` | `bool` | `False` | Use SepCMA variant (diagonal covariance) |
| `with_margin` | `bool` | `False` | Use CMAwM variant (better for discrete parameters) |
| `lr_adapt` | `bool` | `False` | Enable learning rate adaptation in standard CMA |
| `source_trials` | `list[FrozenTrial] \| None` | `None` | Trials for warm starting |

**Deprecated Parameters:**
- `restart_strategy`: Deprecated in v4.4.0, scheduled for removal in v6.0.0
- `inc_popsize`: Deprecated in v4.4.0, scheduled for removal in v6.0.0

**Sources:** [optuna/samplers/_cmaes.py:111-245](), [optuna/samplers/_cmaes.py:248-334]()

### Mutually Exclusive Options

```mermaid
graph TB
    Options["Configuration Options"]
    
    Options -->|"Cannot combine"| Conflict1["use_separable_cma=True<br/>with_margin=True"]
    Options -->|"Cannot combine"| Conflict2["lr_adapt=True<br/>use_separable_cma=True"]
    Options -->|"Cannot combine"| Conflict3["lr_adapt=True<br/>with_margin=True"]
    Options -->|"Cannot combine"| Conflict4["source_trials<br/>x0 or sigma0"]
    Options -->|"Cannot combine"| Conflict5["source_trials<br/>use_separable_cma=True"]
    
    Conflict1 -.->|"raises"| ValueError1["ValueError"]
    Conflict2 -.->|"raises"| ValueError2["ValueError"]
    Conflict3 -.->|"raises"| ValueError3["ValueError"]
    Conflict4 -.->|"raises"| ValueError4["ValueError"]
    Conflict5 -.->|"raises"| ValueError5["ValueError"]
```

**Validation Code:** [optuna/samplers/_cmaes.py:312-333]()

**Sources:** [optuna/samplers/_cmaes.py:312-333]()

---

## Limitations and Fallback Behavior

### Unsupported Features

The sampler falls back to the `_independent_sampler` (default: `RandomSampler`) in these cases:

1. **Before Startup Phase:** When `len(completed_trials) < n_startup_trials`
   - [optuna/samplers/_cmaes.py:369-370]()

2. **Empty Search Space:** When all parameters are single-valued or categorical
   - [optuna/samplers/_cmaes.py:365-366]()

3. **Dynamic Search Space:** When parameter set changes between trials
   - [optuna/samplers/_cmaes.py:381-389]()

4. **Categorical Parameters:** `CategoricalDistribution` is never supported
   - [optuna/samplers/_cmaes.py:350-352]()

### Independent Sampling Warnings

**Warning Template:** [optuna/samplers/_cmaes.py:587-599]()
```python
def _log_independent_sampling(self, trial: FrozenTrial, param_name: str) -> None:
    _logger.warning(
        _INDEPENDENT_SAMPLING_WARNING_TEMPLATE.format(
            param_name=param_name,
            trial_number=trial.number,
            independent_sampler_name=self._independent_sampler.__class__.__name__,
            sampler_name=self.__class__.__name__,
            fallback_reason=(
                "dynamic search space and `CategoricalDistribution` are not supported "
                "by `CmaEsSampler`"
            ),
        )
    )
```

Warnings can be suppressed by setting `warn_independent_sampling=False`.

**Sources:** [optuna/samplers/_cmaes.py:365-389](), [optuna/samplers/_cmaes.py:569-599]()

### Multi-Objective Optimization

CMA-ES sampler only supports single-objective optimization. Attempting to use it with multi-objective studies will raise an error through `_raise_error_if_multi_objective()`.

**Sources:** [optuna/samplers/_cmaes.py:363](), [optuna/samplers/_cmaes.py:576]()

---

## Integration with External cmaes Library

### Lazy Import Pattern

The sampler uses lazy importing to avoid hard dependencies:

**Import Definition:** [optuna/samplers/_cmaes.py:33-38]()
```python
if TYPE_CHECKING:
    import cmaes
    CmaClass = Union[cmaes.CMA, cmaes.SepCMA, cmaes.CMAwM]
else:
    cmaes = _LazyImport("cmaes")
```

The `cmaes` library is only imported when actually needed, allowing Optuna to function without it installed.

### Alternative PyCmaSampler

For users who prefer the `cma` library (pycma) instead of `cmaes`, Optuna provides an integration:

**Integration Module:** [optuna/integration/cma.py:1-10]()
```python
try:
    from optuna_integration.cma import PyCmaSampler
except ModuleNotFoundError:
    raise ModuleNotFoundError(_INTEGRATION_IMPORT_ERROR_TEMPLATE.format("cma"))
```

This requires installing `optuna-integration` and provides access to `PyCmaSampler`.

**Sources:** [optuna/samplers/_cmaes.py:33-38](), [optuna/integration/cma.py:1-10]()

---

## Testing and Validation

The sampler includes comprehensive tests covering:

### Test Coverage

| Test Category | File Reference |
|--------------|----------------|
| Basic initialization and options | [tests/samplers_tests/test_cmaes.py:45-136]() |
| Warm starting | [tests/samplers_tests/test_cmaes.py:138-203]() |
| Search space compatibility | [tests/samplers_tests/test_cmaes.py:233-261](), [tests/samplers_tests/test_cmaes.py:448-489]() |
| Optimizer state persistence | [tests/samplers_tests/test_cmaes.py:353-375]() |
| Pruned trial handling | [tests/samplers_tests/test_cmaes.py:299-349]() |
| String splitting for storage | [tests/samplers_tests/test_cmaes.py:418-432]() |
| Warning behavior | [tests/samplers_tests/test_cmaes.py:517-554]() |
| Storage backend compatibility | [tests/samplers_tests/test_cmaes.py:557-573]() |

**Sources:** [tests/samplers_tests/test_cmaes.py:1-584]()

---

## Usage Examples

### Basic Usage

```python
import optuna

def objective(trial):
    x = trial.suggest_float("x", -10, 10)
    y = trial.suggest_int("y", -10, 10)
    return x**2 + y

sampler = optuna.samplers.CmaEsSampler(seed=42)
study = optuna.create_study(sampler=sampler)
study.optimize(objective, n_trials=100)
```

### Using SepCMA for High Dimensions

```python
sampler = optuna.samplers.CmaEsSampler(
    use_separable_cma=True,
    n_startup_trials=10,
    seed=42
)
```

### Using CMAwM for Discrete Parameters

```python
sampler = optuna.samplers.CmaEsSampler(
    with_margin=True,
    n_startup_trials=10,
    seed=42
)
```

### Warm Starting from Previous Study

```python
# Source study
source_study = optuna.create_study()
source_study.optimize(objective, n_trials=50)

# Target study with warm start
sampler = optuna.samplers.CmaEsSampler(
    source_trials=source_study.trials,
    seed=42
)
target_study = optuna.create_study(sampler=sampler)
target_study.optimize(objective, n_trials=50)
```

**Sources:** [optuna/samplers/_cmaes.py:50-71]()

---

# Page: Multi-Objective Optimization

# Multi-Objective Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/_gp/acqf.py](optuna/_gp/acqf.py)
- [optuna/_gp/batched_lbfgsb.py](optuna/_gp/batched_lbfgsb.py)
- [optuna/_gp/gp.py](optuna/_gp/gp.py)
- [optuna/_gp/optim_mixed.py](optuna/_gp/optim_mixed.py)
- [optuna/_gp/optim_sample.py](optuna/_gp/optim_sample.py)
- [optuna/_gp/prior.py](optuna/_gp/prior.py)
- [optuna/_gp/search_space.py](optuna/_gp/search_space.py)
- [optuna/integration/chainermn.py](optuna/integration/chainermn.py)
- [optuna/samplers/_gp/sampler.py](optuna/samplers/_gp/sampler.py)
- [optuna/samplers/_tpe/parzen_estimator.py](optuna/samplers/_tpe/parzen_estimator.py)
- [optuna/samplers/_tpe/sampler.py](optuna/samplers/_tpe/sampler.py)
- [optuna/terminator/improvement/emmr.py](optuna/terminator/improvement/emmr.py)
- [optuna/terminator/improvement/evaluator.py](optuna/terminator/improvement/evaluator.py)
- [tests/gp_tests/test_acqf.py](tests/gp_tests/test_acqf.py)
- [tests/gp_tests/test_batched_lbfgsb.py](tests/gp_tests/test_batched_lbfgsb.py)
- [tests/gp_tests/test_gp.py](tests/gp_tests/test_gp.py)
- [tests/gp_tests/test_search_space.py](tests/gp_tests/test_search_space.py)
- [tests/samplers_tests/test_gp.py](tests/samplers_tests/test_gp.py)
- [tests/samplers_tests/test_samplers.py](tests/samplers_tests/test_samplers.py)
- [tests/samplers_tests/tpe_tests/test_multi_objective_sampler.py](tests/samplers_tests/tpe_tests/test_multi_objective_sampler.py)
- [tests/samplers_tests/tpe_tests/test_parzen_estimator.py](tests/samplers_tests/tpe_tests/test_parzen_estimator.py)
- [tests/samplers_tests/tpe_tests/test_sampler.py](tests/samplers_tests/tpe_tests/test_sampler.py)

</details>



This document covers Optuna's multi-objective optimization capabilities across different samplers, focusing on how `TPESampler` and `GPSampler` handle multiple conflicting objectives. The system implements Pareto front calculation, non-dominated sorting, hypervolume computation, and specialized acquisition functions for multi-objective scenarios.

For single-objective optimization details, see page 3.2 (TPE) and page 3.3 (GP Sampler). For evolutionary multi-objective algorithms (NSGA-II/NSGA-III), see page 3.6.

## Overview

Optuna's model-based samplers (TPE and GP) extend to multi-objective optimization using:

- **Pareto Front Identification**: Non-dominated sorting to identify optimal trade-off solutions
- **Hypervolume Metrics**: Quantifying solution quality and computing contributions
- **Specialized Acquisition Functions**: LogEHVI for GP-based multi-objective optimization
- **Weight Calculation**: Hypervolume-based weighting for TPE's good trials

The multi-objective support allows optimizing 2 or more conflicting objectives simultaneously, producing a Pareto front of non-dominated solutions rather than a single optimal point.

## Pareto Front and Non-Dominated Sorting

### Pareto Domination Concept

A solution dominates another if it is better in at least one objective and not worse in all others. The Pareto front consists of all non-dominated solutions.

**Multi-Objective Architecture**

```mermaid
graph TB
    Trials["Trial List"] --> ExtractValues["Extract trial.values"]
    ExtractValues --> LossVals["loss_vals (sign-adjusted)"]
    
    LossVals --> FastNonDomRank["_fast_non_domination_rank"]
    FastNonDomRank --> Ranks["nondomination_ranks"]
    
    Ranks --> IdentifyFronts["Identify Pareto Fronts"]
    IdentifyFronts --> Front0["Front 0: Best solutions"]
    IdentifyFronts --> Front1["Front 1: Next best"]
    IdentifyFronts --> FrontN["Front N: Dominated"]
    
    LossVals --> IsParetoFront["_is_pareto_front"]
    IsParetoFront --> ParetoMask["Boolean mask for front 0"]
```

Sources: [optuna/samplers/_tpe/sampler.py:746-780](), [optuna/study/_multi_objective.py]()

### Non-Dominated Ranking Algorithm

The `_fast_non_domination_rank` function implements efficient non-dominated sorting:

1. **Domination Check**: Compare each trial pair to determine domination relationships
2. **Rank Assignment**: Assign rank 0 to non-dominated solutions, then iteratively assign higher ranks
3. **Early Termination**: Can stop when `n_below` solutions are classified

**Ranking Process Flow**

```mermaid
graph TB
    AllTrials["All Trials"] --> CompareAll["Pairwise Domination Comparison"]
    CompareAll --> DominationGraph["Domination Graph"]
    
    DominationGraph --> FindRank0["Find Rank 0: No dominators"]
    FindRank0 --> Rank0["Rank 0 Trials"]
    
    Rank0 --> RemoveRank0["Remove Rank 0 from graph"]
    RemoveRank0 --> FindRank1["Find Rank 1"]
    FindRank1 --> Rank1["Rank 1 Trials"]
    
    Rank1 --> CheckNBelow{"Have n_below trials?"}
    CheckNBelow -->|No| RemoveRank1["Continue ranking"]
    CheckNBelow -->|Yes| Return["Return ranks"]
    
    RemoveRank1 --> FindRank2["Find next rank"]
```

Sources: [optuna/samplers/_tpe/sampler.py:757-758](), [optuna/study/_multi_objective.py]()

### TPESampler Trial Splitting

The `_split_complete_trials_multi_objective` function divides trials into "below" (good) and "above" (bad) groups for multi-objective TPE:

```python
# From optuna/samplers/_tpe/sampler.py:746-780
def _split_complete_trials_multi_objective(
    trials: Sequence[FrozenTrial], study: Study, n_below: int
) -> tuple[list[FrozenTrial], list[FrozenTrial]]:
```

**Trial Splitting Workflow**

```mermaid
graph TB
    CompleteTrials["Complete Trials"] --> ExtractLvals["Extract loss values (sign-adjusted)"]
    ExtractLvals --> Lvals["lvals array"]
    
    Lvals --> NonDomRank["_fast_non_domination_rank(lvals, n_below)"]
    NonDomRank --> Ranks["nondomination_ranks"]
    
    Ranks --> CountRanks["Count trials in each rank"]
    CountRanks --> FindLastRank["Find last full rank < n_below"]
    
    FindLastRank --> TieBreak{"Tie-break needed?"}
    TieBreak -->|No| SplitByRank["Split by rank"]
    TieBreak -->|Yes| HSSP["_solve_hssp: Hypervolume Subset Selection"]
    
    HSSP --> SelectSubset["Select subset with max hypervolume"]
    SelectSubset --> BelowTrials["Below Trials"]
    SplitByRank --> BelowTrials
    
    BelowTrials --> AboveTrials["Above Trials = All - Below"]
```

Sources: [optuna/samplers/_tpe/sampler.py:746-780]()

**Hypervolume Subset Selection Problem (HSSP)**

When multiple trials have the same rank and selecting all would exceed `n_below`, HSSP selects the subset that maximizes hypervolume contribution:

```python
# Lines 764-775 from optuna/samplers/_tpe/sampler.py
if indices_below.size < n_below:  # Tie-break with HSSP
    need_tiebreak = nondomination_ranks == last_rank_before_tiebreak + 1
    rank_i_lvals = lvals[need_tiebreak]
    subset_size = n_below - indices_below.size
    selected_indices = _solve_hssp_with_cache(
        tuple(rank_i_lvals.ravel()),
        tuple(indices[need_tiebreak]),
        subset_size,
        tuple(_get_reference_point(rank_i_lvals)),
    )
```

Sources: [optuna/samplers/_tpe/sampler.py:764-775](), [optuna/_hypervolume/hssp.py]()

## Hypervolume Computation

### Overview

Hypervolume measures the volume of objective space dominated by a solution set. It's used in multi-objective optimization for:

1. **Solution Quality**: Measuring overall Pareto front quality
2. **Contribution Weighting**: Computing individual trial importance in TPE
3. **Subset Selection**: Solving HSSP for trial selection

**Hypervolume Calculation Flow**

```mermaid
graph TB
    ParetoSols["Pareto Solutions"] --> RefPoint["Reference Point"]
    RefPoint --> ComputeHV["compute_hypervolume"]
    
    ComputeHV --> Dim2or3{"n_objectives <= 3?"}
    Dim2or3 -->|Yes| WFG["WFG Algorithm (exact)"]
    Dim2or3 -->|No| MonteCarlo["Monte Carlo approximation"]
    
    WFG --> Hypervolume["Hypervolume value"]
    MonteCarlo --> Hypervolume
```

Sources: [optuna/_hypervolume/__init__.py](), [optuna/samplers/_tpe/sampler.py:844-856]()

### Reference Point Selection

The reference point defines the boundary for hypervolume calculation. TPE uses a heuristic approach:

```python
# From optuna/samplers/_tpe/sampler.py:680-684
def _get_reference_point(loss_vals: np.ndarray) -> np.ndarray:
    worst_point = np.max(loss_vals, axis=0)
    reference_point = np.maximum(1.1 * worst_point, 0.9 * worst_point)
    reference_point[reference_point == 0] = EPS
    return reference_point
```

This creates a slightly worse point than the worst observed to ensure all solutions contribute to hypervolume.

Sources: [optuna/samplers/_tpe/sampler.py:680-684]()

### Hypervolume Contribution for TPE Weights

The `_calculate_weights_below_for_multi_objective` function computes weights for good trials based on hypervolume contribution:

**Weight Calculation Process**

```mermaid
graph TB
    BelowTrials["Below Trials"] --> FilterFeasible["Filter feasible trials"]
    FilterFeasible --> FeasibleTrials["Feasible Trials"]
    
    FeasibleTrials --> CountCheck{"n_feasible > 1?"}
    CountCheck -->|No| UniformWeights["Return uniform weights"]
    CountCheck -->|Yes| ExtractLvals["Extract loss values"]
    
    ExtractLvals --> GetRefPoint["_get_reference_point(lvals)"]
    GetRefPoint --> RefPoint["Reference Point"]
    
    RefPoint --> IsParetoFront["_is_pareto_front(lvals)"]
    IsParetoFront --> ParetoSols["Pareto Solutions"]
    
    ParetoSols --> ComputeHV["compute_hypervolume(pareto, ref)"]
    ComputeHV --> TotalHV["Total Hypervolume"]
    
    TotalHV --> LOO["Leave-One-Out HV calculation"]
    LOO --> Contribs["HV contributions per trial"]
    
    Contribs --> NormalizeWeights["Normalize and apply EPS"]
    NormalizeWeights --> Weights["weights_below array"]
```

Sources: [optuna/samplers/_tpe/sampler.py:825-863]()

**Hypervolume Contribution Calculation**

For 2D and 3D problems (≤ 3 objectives), exact leave-one-out hypervolume is computed:

```python
# From optuna/samplers/_tpe/sampler.py:852-856
if len(study.directions) <= 3:
    contribs[on_front] = [
        hv - compute_hypervolume(pareto_sols[loo], ref_point, assume_pareto=True)
        for loo in loo_mat
    ]
```

For higher dimensions, an approximation based on dominated box volumes is used:

```python
# From optuna/samplers/_tpe/sampler.py:857-862
else:
    contribs[on_front] = np.prod(ref_point - pareto_sols, axis=-1)
    limited_sols = np.maximum(pareto_sols, pareto_sols[:, np.newaxis])
    contribs[on_front] -= [
        compute_hypervolume(limited_sols[i, loo], ref_point) for i, loo in enumerate(loo_mat)
    ]
```

Sources: [optuna/samplers/_tpe/sampler.py:852-862]()

## TPESampler Multi-Objective Features

### Overview

`TPESampler` extends to multi-objective optimization by using hypervolume-based weighting for good trials. The key differences from single-objective TPE:

1. **Trial Splitting**: Uses non-dominated ranking and HSSP instead of simple sorting
2. **Weight Calculation**: Weights based on hypervolume contribution instead of uniform
3. **Parzen Estimators**: Built separately for each objective's good and bad trials

**Multi-Objective TPE Workflow**

```mermaid
graph TB
    Study["Multi-objective Study"] --> CheckMO{"study._is_multi_objective()"}
    CheckMO -->|Yes| SplitMO["_split_complete_trials_multi_objective"]
    CheckMO -->|No| SplitSO["_split_complete_trials_single_objective"]
    
    SplitMO --> BelowTrials["below_trials"]
    SplitMO --> AboveTrials["above_trials"]
    SplitSO --> BelowTrials
    SplitSO --> AboveTrials
    
    BelowTrials --> CalcWeights["_calculate_weights_below_for_multi_objective"]
    CalcWeights --> WeightsBelow["weights_below (HV-based)"]
    
    WeightsBelow --> BuildMPEBelow["_build_parzen_estimator (handle_below=True)"]
    AboveTrials --> BuildMPEAbove["_build_parzen_estimator (handle_below=False)"]
    
    BuildMPEBelow --> MPEBelow["mpe_below (weighted)"]
    BuildMPEAbove --> MPEAbove["mpe_above"]
    
    MPEBelow --> SampleAndEI["Sample and compute EI"]
    MPEAbove --> SampleAndEI
```

Sources: [optuna/samplers/_tpe/sampler.py:538-561](), [optuna/samplers/_tpe/sampler.py:563-590]()

### Parzen Estimator Construction

When `handle_below=True` and the study is multi-objective, weighted Parzen estimators are constructed:

```python
# From optuna/samplers/_tpe/sampler.py:571-581
if handle_below and study._is_multi_objective():
    param_mask_below = [
        search_space.keys() <= self._get_params(trial).keys() for trial in trials
    ]
    weights_below = _calculate_weights_below_for_multi_objective(
        study, trials, self._constraints_func
    )[param_mask_below]
    assert np.isfinite(weights_below).all()
    mpe = self._parzen_estimator_cls(
        observations, search_space, self._parzen_estimator_parameters, weights_below
    )
```

The `param_mask_below` filters trials that have all parameters in the search space, and `weights_below` provides hypervolume-based importance weights.

Sources: [optuna/samplers/_tpe/sampler.py:571-581]()

### Configuration Example

```python
import optuna

sampler = optuna.samplers.TPESampler(
    n_startup_trials=10,
    multivariate=True,  # Recommended for multi-objective
    seed=42
)

study = optuna.create_study(
    directions=["minimize", "maximize"],  # Multi-objective
    sampler=sampler
)
```

Sources: [optuna/samplers/_tpe/sampler.py:72-287]()

## GPSampler Multi-Objective Features

### Overview

`GPSampler` uses Log Expected Hypervolume Improvement (LogEHVI) as the acquisition function for multi-objective optimization. This extends the single-objective LogEI to multiple objectives.

**GP Multi-Objective Architecture**

```mermaid
graph TB
    Study["Multi-objective Study"] --> CheckObjectives{"n_objectives"}
    CheckObjectives -->|1| LogEI["LogEI acquisition function"]
    CheckObjectives -->|>1| LogEHVI["LogEHVI acquisition function"]
    
    LogEHVI --> FitGPRs["Fit GP for each objective"]
    FitGPRs --> GPRList["gpr_list"]
    
    GPRList --> QMC["Quasi-Monte Carlo samples"]
    QMC --> FixedSamples["_sample_from_normal_sobol"]
    
    FixedSamples --> Posterior["GP posterior for each objective"]
    Posterior --> YPost["Y_post samples"]
    
    YPost --> NonDomBoxes["_get_non_dominated_box_bounds"]
    NonDomBoxes --> Boxes["Box decomposition"]
    
    Boxes --> ComputeLogEHVI["logehvi function"]
    ComputeLogEHVI --> AcqfValue["Acquisition function value"]
```

Sources: [optuna/samplers/_gp/sampler.py:360-370](), [optuna/_gp/acqf.py:223-279]()

### LogEHVI Acquisition Function

The `LogEHVI` class implements the log expected hypervolume improvement:

```python
# Key components from optuna/_gp/acqf.py:223-279
class LogEHVI(BaseAcquisitionFunc):
    def __init__(
        self,
        gpr_list: list[GPRegressor],
        search_space: SearchSpace,
        Y_train: torch.Tensor,
        n_qmc_samples: int,
        qmc_seed: int | None,
        stabilizing_noise: float = 1e-12,
    ) -> None:
```

**LogEHVI Evaluation Process**

```mermaid
graph TB
    XParam["Parameter x"] --> GPPosterior["GP posterior for each objective"]
    GPPosterior --> MeanVar["mean, variance per objective"]
    
    MeanVar --> QMCSamples["Fixed QMC samples (Sobol)"]
    QMCSamples --> YSamples["Y samples ~ N(mean, var)"]
    
    YSamples --> YPost["Y_post tensor"]
    YPost --> Logehvi["logehvi(Y_post, boxes, intervals)"]
    
    Logehvi --> LogsumexpBoxes["logsumexp over boxes"]
    LogsumexpBoxes --> LogsumexpSamples["logsumexp over QMC samples"]
    LogsumexpSamples --> LogEHVIValue["Log EHVI value"]
```

Sources: [optuna/_gp/acqf.py:260-278](), [optuna/_gp/acqf.py:45-62]()

### Non-Dominated Box Decomposition

The reference point and Pareto front are used to decompose objective space into boxes:

```python
# From optuna/_gp/acqf.py:233-241
def _get_non_dominated_box_bounds() -> tuple[torch.Tensor, torch.Tensor]:
    loss_vals = -Y_train.numpy()  # Convert to minimization
    pareto_sols = loss_vals[_is_pareto_front(loss_vals, assume_unique_lexsorted=False)]
    ref_point = np.max(loss_vals, axis=0)
    ref_point = np.nextafter(np.maximum(1.1 * ref_point, 0.9 * ref_point), np.inf)
    lbs, ubs = get_non_dominated_box_bounds(pareto_sols, ref_point)
    return torch.from_numpy(-ubs), torch.from_numpy(-lbs)  # Flip back to maximization
```

Sources: [optuna/_gp/acqf.py:233-241](), [optuna/_hypervolume/__init__.py]()

### Best Parameter Selection for Multi-Objective

For warm-starting local search, GP sampler selects multiple points from the Pareto front:

```python
# From optuna/samplers/_gp/sampler.py:289-301
def _get_best_params_for_multi_objective(
    self,
    normalized_params: np.ndarray,
    standardized_score_vals: np.ndarray,
) -> np.ndarray:
    pareto_params = normalized_params[
        _is_pareto_front(-standardized_score_vals, assume_unique_lexsorted=False)
    ]
    n_pareto_sols = len(pareto_params)
    size = min(self._n_local_search // 2, n_pareto_sols)
    chosen_indices = self._rng.rng.choice(n_pareto_sols, size=size, replace=False)
    return pareto_params[chosen_indices]
```

This randomly selects up to `n_local_search // 2` points from the Pareto front to seed local optimization.

Sources: [optuna/samplers/_gp/sampler.py:289-301]()

## Population Management

### Generation Tracking

Both algorithms track generations using system attributes:

- **NSGA-II**: Uses `NSGAIISampler._GENERATION_KEY` for generation tracking
- **NSGA-III**: Uses `_GENERATION_KEY` and `_POPULATION_CACHE_KEY_PREFIX` for caching

### Population Lifecycle

```mermaid
graph TB
    InitialPopulation["Initial Population"] --> RandomSampling["Random Sampling"]
    RandomSampling --> Generation0["Generation 0"]
    
    Generation0 --> Evaluation["Objective Evaluation"]
    Evaluation --> Selection["Elite Selection"]
    Selection --> Crossover["Crossover & Mutation"]
    Crossover --> NextGeneration["Generation N+1"]
    
    NextGeneration --> Evaluation
    Selection --> ElitePopulation["Elite Population"]
    ElitePopulation --> ParentSelection["Parent Selection"]
    ParentSelection --> Crossover
```

Sources: [optuna/samplers/nsgaii/_sampler.py:255-272](), [optuna/samplers/_nsgaiii/_sampler.py:204-277]()

## Configuration Parameters

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `population_size` | `int` | 50 | Number of individuals per generation |
| `mutation_prob` | `float` | `1.0/n_params` | Probability of parameter mutation |
| `crossover_prob` | `float` | 0.9 | Probability of crossover operation |
| `swapping_prob` | `float` | 0.5 | Probability of parameter swapping |
| `seed` | `int` | None | Random seed for reproducibility |

### NSGA-III Specific Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `reference_points` | `np.ndarray` | None | Custom reference points |
| `dividing_parameter` | `int` | 3 | Density of default reference points |

Sources: [optuna/samplers/nsgaii/_sampler.py:156-176](), [optuna/samplers/_nsgaiii/_sampler.py:78-100]()

---

# Page: Other Samplers and Pruning

# Other Samplers and Pruning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/integration/chainermn.py](optuna/integration/chainermn.py)
- [tests/samplers_tests/test_samplers.py](tests/samplers_tests/test_samplers.py)

</details>



## Purpose and Scope

This page documents Optuna's simpler sampling algorithms and the pruning system for early stopping of unpromising trials. The samplers covered here include baseline algorithms (RandomSampler, GridSampler), specialized utilities (PartialFixedSampler, QMCSampler), and multi-objective evolutionary algorithms (NSGA-II/III). The pruning system enables automatic termination of trials that show poor intermediate results.

For the core sampler interface and sampling strategies, see [BaseSampler Interface and Sampling Strategies](#3.1). For advanced Bayesian optimization samplers, see [Tree-structured Parzen Estimator (TPE)](#3.2), [Gaussian Process Sampler](#3.3), and [CMA-ES Sampler](#3.4). For multi-objective optimization with TPE and GP, see [Multi-Objective Optimization](#3.5).

---

## Simple Baseline Samplers

### RandomSampler

`RandomSampler` is Optuna's baseline sampling algorithm that draws parameter values uniformly at random from the search space. It serves as the fallback sampler for many sophisticated algorithms during their initial trials and provides a performance baseline for comparison.

**Key Characteristics:**
- No learning from previous trials
- Simple, fast, and robust
- Used as startup sampler by TPE, GP, and CMA-ES
- Supports all distribution types
- Thread-safe with proper random state management

**Implementation Details:**

The sampler maintains a `LazyRandomState` for reproducible random number generation. When a seed is provided, results are deterministic across runs. The sampler implements only `sample_independent()` and returns an empty dictionary from `infer_relative_search_space()`, delegating all sampling to independent parameter selection.

```mermaid
graph TB
    BaseSampler["BaseSampler"]
    RandomSampler["RandomSampler"]
    LazyRandomState["_LazyRandomState<br/>Random state management"]
    SampleIndependent["sample_independent()<br/>Uniform random sampling"]
    
    BaseSampler --> RandomSampler
    RandomSampler --> LazyRandomState
    RandomSampler --> SampleIndependent
    
    FloatDist["FloatDistribution<br/>np.random.uniform() or log scale"]
    IntDist["IntDistribution<br/>np.random.randint() or log scale"]
    CatDist["CategoricalDistribution<br/>np.random.choice()"]
    
    SampleIndependent --> FloatDist
    SampleIndependent --> IntDist
    SampleIndependent --> CatDist
```

**Sources:** [tests/samplers_tests/test_samplers.py:47](), [tests/samplers_tests/test_samplers.py:82](), [tests/samplers_tests/test_samplers.py:110]()

### GridSampler

`GridSampler` performs exhaustive search over a predefined grid of parameter values. It is useful for small search spaces where complete enumeration is feasible.

**Key Characteristics:**
- Deterministic enumeration of search space
- Requires explicit grid specification via `search_space` parameter
- Cycles through grid points sequentially
- Does not support dynamic parameter addition
- Optimal for small, discrete search spaces

**Usage Pattern:**

```python
search_space = {
    'x': [0, 1, 2, 3, 4],
    'y': ['a', 'b', 'c']
}
sampler = optuna.samplers.GridSampler(search_space=search_space)
study = optuna.create_study(sampler=sampler)
```

The sampler generates all combinations of the provided grid points (15 trials in the example above). Once all combinations are exhausted, the sampler cycles back to the beginning.

**Sources:** [tests/samplers_tests/test_samplers.py:123]()

### PartialFixedSampler

`PartialFixedSampler` is a wrapper sampler that fixes specific parameters to constant values while delegating other parameters to an underlying base sampler. This is useful for targeted exploration where some hyperparameters should remain constant.

**Architecture:**

```mermaid
graph TB
    Study["Study"]
    PartialFixedSampler["PartialFixedSampler"]
    FixedParams["fixed_params<br/>dict[str, Any]"]
    BaseSampler["base_sampler<br/>BaseSampler instance"]
    
    Study --> PartialFixedSampler
    PartialFixedSampler --> FixedParams
    PartialFixedSampler --> BaseSampler
    
    SampleLogic["Sampling Logic"]
    PartialFixedSampler --> SampleLogic
    
    FixedPath["Parameter in fixed_params<br/>→ Return fixed value"]
    DelegatePath["Parameter not in fixed_params<br/>→ Delegate to base_sampler"]
    
    SampleLogic --> FixedPath
    SampleLogic --> DelegatePath
```

**Usage Example:**

The test at [tests/samplers_tests/test_samplers.py:568-588]() demonstrates fixing parameter `y` to `0` while allowing `x` and `z` to be sampled normally:

```python
fixed_params = {"y": 0}
sampler = optuna.samplers.PartialFixedSampler(
    fixed_params, 
    base_sampler=optuna.samplers.RandomSampler()
)
```

**Sources:** [tests/samplers_tests/test_samplers.py:117-122](), [tests/samplers_tests/test_samplers.py:568-588]()

---

## Quasi-Monte Carlo Sampler

### QMCSampler

`QMCSampler` uses quasi-random low-discrepancy sequences to sample the search space more uniformly than pure random sampling. These sequences provide better space-filling properties, which can improve exploration efficiency in the early stages of optimization.

**Key Characteristics:**
- Low-discrepancy sequence generation
- Better space coverage than random sampling
- Deterministic given a seed
- Uses an underlying sampler for non-QMC functionality
- Does not maintain a `LazyRandomState` directly (only in base sampler)

**Implementation Notes:**

QMCSampler wraps another sampler (typically RandomSampler) and uses quasi-random sequences for parameter generation. The test at [tests/samplers_tests/test_samplers.py:124]() shows it does not have its own RNG (`expected_has_rng=False`) but delegates to another sampler (`expected_has_another_sampler=True`).

**Sources:** [tests/samplers_tests/test_samplers.py:54](), [tests/samplers_tests/test_samplers.py:93](), [tests/samplers_tests/test_samplers.py:124]()

---

## Multi-Objective Evolutionary Samplers

Optuna provides NSGA-II and NSGA-III samplers for multi-objective optimization using evolutionary algorithms. These samplers are alternatives to MOTPE (covered in [Multi-Objective Optimization](#3.5)) and are particularly effective for problems with many objectives or complex Pareto fronts.

### NSGA-II Sampler

`NSGAIISampler` implements the Non-dominated Sorting Genetic Algorithm II, a popular evolutionary algorithm for multi-objective optimization with 2-3 objectives.

**Algorithm Overview:**

```mermaid
graph TD
    Start["Trial Generation"]
    PopInit["Population Initialization<br/>Random sampling for initial trials"]
    Evaluation["Objective Evaluation"]
    NonDomSort["Non-dominated Sorting<br/>Rank trials by dominance"]
    CrowdDist["Crowding Distance<br/>Diversity metric"]
    Selection["Parent Selection<br/>Tournament selection"]
    Crossover["Crossover<br/>Blend/Uniform operators"]
    Mutation["Mutation<br/>Polynomial/discrete"]
    NewPop["New Population"]
    
    Start --> PopInit
    PopInit --> Evaluation
    Evaluation --> NonDomSort
    NonDomSort --> CrowdDist
    CrowdDist --> Selection
    Selection --> Crossover
    Crossover --> Mutation
    Mutation --> NewPop
    NewPop --> Evaluation
```

**Key Features:**
- Non-dominated sorting for multi-objective ranking
- Crowding distance for diversity preservation
- Genetic operators: crossover and mutation
- Supports both single and multi-objective studies
- Falls back to RandomSampler initially

**Sources:** [tests/samplers_tests/test_samplers.py:52](), [tests/samplers_tests/test_samplers.py:72](), [tests/samplers_tests/test_samplers.py:91](), [tests/samplers_tests/test_samplers.py:114]()

### NSGA-III Sampler

`NSGAIIISampler` extends NSGA-II for many-objective optimization (4+ objectives) using reference points instead of crowding distance.

**Differences from NSGA-II:**

| Feature | NSGA-II | NSGA-III |
|---------|---------|----------|
| **Diversity Mechanism** | Crowding distance | Reference points |
| **Optimal for** | 2-3 objectives | 4+ objectives |
| **Reference Points** | Not used | Das-Dennis or custom |
| **Scalability** | Degrades with many objectives | Better with many objectives |

**Key Characteristics:**
- Reference point-based diversity
- Suitable for many-objective problems
- Can use predefined or generated reference points
- Similar genetic operators to NSGA-II

**Sources:** [tests/samplers_tests/test_samplers.py:53](), [tests/samplers_tests/test_samplers.py:73](), [tests/samplers_tests/test_samplers.py:92](), [tests/samplers_tests/test_samplers.py:115]()

### Multi-Objective Sampler Comparison

The test at [tests/samplers_tests/test_samplers.py:69-78]() shows that multiple samplers support multi-objective optimization:

```python
multi_objective_sampler_class = [
    optuna.samplers.NSGAIISampler,
    optuna.samplers.NSGAIIISampler,
    optuna.samplers.TPESampler(n_startup_trials=0),
    get_gp_sampler(deterministic_objective=True),
    get_gp_sampler(deterministic_objective=False),
]
```

Each sampler provides different trade-offs:
- **NSGA-II/III**: Evolutionary approach, good for complex Pareto fronts
- **MOTPE**: Model-based, efficient for moderate dimensions
- **Multi-objective GP**: Bayesian optimization, effective with expensive evaluations

**Sources:** [tests/samplers_tests/test_samplers.py:69-78](), [tests/samplers_tests/test_samplers.py:590-636]()

---

## Pruning System

The pruning system enables automatic termination of unpromising trials based on intermediate results, significantly reducing computation time by avoiding full evaluation of poor candidates.

### Pruning Architecture

```mermaid
graph TB
    subgraph "Trial Execution Flow"
        Trial["Trial"]
        Report["trial.report(value, step)"]
        ShouldPrune["trial.should_prune()"]
        Pruner["Pruner"]
    end
    
    subgraph "Pruner Interface"
        BasePruner["BasePruner<br/>Abstract interface"]
        PruneMethod["prune(study, trial)<br/>Returns: bool"]
    end
    
    subgraph "Pruner Implementations"
        MedianPruner["MedianPruner<br/>Compare to median"]
        HyperbandPruner["HyperbandPruner<br/>Successive Halving"]
        PercentilePruner["PercentilePruner<br/>Threshold-based"]
        SuccessiveHalvingPruner["SuccessiveHalvingPruner<br/>Resource allocation"]
        ThresholdPruner["ThresholdPruner<br/>Absolute threshold"]
        PatientPruner["PatientPruner<br/>Wrapper with patience"]
        NopPruner["NopPruner<br/>No pruning"]
    end
    
    Trial --> Report
    Report --> ShouldPrune
    ShouldPrune --> Pruner
    Pruner --> BasePruner
    
    BasePruner --> PruneMethod
    
    BasePruner -.implements.-> MedianPruner
    BasePruner -.implements.-> HyperbandPruner
    BasePruner -.implements.-> PercentilePruner
    BasePruner -.implements.-> SuccessiveHalvingPruner
    BasePruner -.implements.-> ThresholdPruner
    BasePruner -.implements.-> PatientPruner
    BasePruner -.implements.-> NopPruner
```

**Sources:** Diagram based on Diagram 1 from high-level architecture

### BasePruner Interface

The `BasePruner` abstract class defines the interface for all pruning algorithms. Similar to `BaseSampler`, it provides a contract that all pruner implementations must follow.

**Core Method:**
- `prune(study, trial)` → `bool`: Determines whether to prune the trial based on its intermediate values

**Pruning Decision Flow:**

```mermaid
sequenceDiagram
    participant Objective
    participant Trial
    participant Pruner
    participant Storage
    
    Objective->>Trial: report(intermediate_value, step)
    Trial->>Storage: set_trial_intermediate_value()
    
    Objective->>Trial: should_prune()
    Trial->>Pruner: prune(study, trial)
    
    Pruner->>Storage: get_trial(trial_id)
    Pruner->>Storage: get_best_trials()
    Note over Pruner: Pruning logic<br/>based on implementation
    Pruner-->>Trial: pruning_decision (bool)
    
    alt Should Prune
        Trial-->>Objective: True
        Objective->>Objective: raise TrialPruned()
    else Continue
        Trial-->>Objective: False
        Objective->>Objective: Continue training
    end
```

**Sources:** Diagram based on Diagram 2 from high-level architecture

### MedianPruner

`MedianPruner` terminates trials whose intermediate value at a given step is worse than the median of all trials' intermediate values at the same step.

**Algorithm:**
1. Collect intermediate values from all completed/running trials at the current step
2. Calculate the median of these values
3. Prune if current trial's value is worse than the median

**Configuration Parameters:**
- `n_startup_trials`: Number of trials before pruning starts
- `n_warmup_steps`: Number of steps before pruning starts
- `interval_steps`: Evaluation interval (check every N steps)

**Typical Usage:**
```python
pruner = optuna.pruners.MedianPruner(
    n_startup_trials=5,
    n_warmup_steps=10,
    interval_steps=1
)
study = optuna.create_study(pruner=pruner)
```

**Sources:** Referenced in Diagram 1 from high-level architecture

### HyperbandPruner

`HyperbandPruner` implements the Hyperband algorithm, which adaptively allocates resources to promising trials using successive halving with different resource budgets.

**Key Concepts:**
- **Resource**: Typically training iterations, epochs, or data samples
- **Bracket**: Different resource allocation strategies
- **Successive Halving**: Progressively eliminates worst-performing trials

**Algorithm Overview:**

The algorithm runs multiple brackets, each with a different resource allocation strategy. Within each bracket, trials are evaluated at exponentially increasing resource levels, and the worst-performing half is pruned at each rung.

**Configuration:**
- `min_resource`: Minimum resource allocation (e.g., min epochs)
- `max_resource`: Maximum resource allocation (e.g., max epochs)
- `reduction_factor`: Factor by which to reduce trials (default: 3)

**Advantages:**
- More aggressive than MedianPruner
- Theoretically grounded resource allocation
- Effective for expensive evaluations

**Sources:** Referenced in Diagram 1 from high-level architecture

### Other Pruners

**PercentilePruner:**
Prunes trials whose intermediate values are in the bottom percentile at each step. More configurable than MedianPruner (50th percentile).

**SuccessiveHalvingPruner:**
Simpler version of Hyperband that uses a single bracket with successive halving.

**ThresholdPruner:**
Prunes trials whose intermediate values fall below (or above) an absolute threshold.

**PatientPruner:**
Wrapper pruner that delays the pruning decision of an underlying pruner by a specified number of steps, providing "patience" before termination.

**NopPruner:**
No-operation pruner that never prunes trials. Useful for disabling pruning without changing code structure.

**Sources:** Inferred from common Optuna patterns based on high-level architecture

### Pruning in Practice

**Integration with Objective Function:**

The test at [tests/samplers_tests/test_samplers.py:688-713]() demonstrates the `after_trial` callback receiving pruned trials:

```python
def pruned_objective(trial):
    trial.report(0.5, step=0)
    if trial.should_prune():
        raise optuna.TrialPruned()
    return 1.0

# Sampler's after_trial receives:
# - state = TrialState.PRUNED
# - values = None
```

**Sampler-Pruner Interaction:**

Pruning and sampling are orthogonal systems. The sampler's `after_trial()` method is called regardless of trial outcome (complete, pruned, or failed), allowing samplers to update their internal state appropriately:

| Trial State | `after_trial` values argument |
|-------------|------------------------------|
| COMPLETE | `list[float]` (objective values) |
| PRUNED | `None` |
| FAIL | `None` |

**Sources:** [tests/samplers_tests/test_samplers.py:688-713](), [tests/samplers_tests/test_samplers.py:659-686](), [tests/samplers_tests/test_samplers.py:716-744]()

---

## Sampler Lifecycle and State Management

All samplers in this document follow the same lifecycle hooks defined in `BaseSampler`:

### Lifecycle Hooks

**before_trial(study, trial):**
Called before the trial execution begins. The trial is in `RUNNING` state but has no parameters or values yet.

Test demonstration at [tests/samplers_tests/test_samplers.py:638-657]():
```python
def before_trial(self, study, trial):
    assert trial.state == TrialState.RUNNING
    assert trial.values is None
```

**after_trial(study, trial, state, values):**
Called after the trial execution completes (whether successful, pruned, or failed). The `state` parameter reflects the final state, and `values` contains objective values for completed trials or `None` for pruned/failed trials.

Test demonstration at [tests/samplers_tests/test_samplers.py:659-686]():
```python
def after_trial(self, study, trial, state, values):
    assert trial.state == TrialState.RUNNING  # Not yet updated
    assert state == TrialState.COMPLETE
    assert values is not None
```

**Sources:** [tests/samplers_tests/test_samplers.py:638-686]()

### Random State Management

Most samplers maintain deterministic behavior through proper random state management:

**Seeding Behavior:**

```mermaid
graph LR
    Constructor["Sampler(seed=123)"]
    LazyRNG["_LazyRandomState"]
    RNG["np.random.RandomState(123)"]
    ReseedRNG["reseed_rng()"]
    NewSeed["New random seed"]
    
    Constructor --> LazyRNG
    LazyRNG --> RNG
    ReseedRNG --> NewSeed
    NewSeed --> RNG
```

The test at [tests/samplers_tests/test_samplers.py:128-177]() verifies that:
1. Samplers with seeds produce reproducible results
2. `reseed_rng()` changes the random state
3. Base samplers in composite samplers are also reseeded

**Reproducibility Guarantees:**

The test at [tests/samplers_tests/test_samplers.py:922-948]() ensures that:
- Same seed → identical parameter sequences
- Different seed → different parameter sequences
- Works across all sampler types

**Sources:** [tests/samplers_tests/test_samplers.py:128-177](), [tests/samplers_tests/test_samplers.py:922-948](), [tests/samplers_tests/test_samplers.py:953-974]()

---

## Sampler Testing and Validation

### Distribution Support

All samplers must support the standard distribution types with proper bounds checking:

**Float Distributions:**
- Linear scale: `FloatDistribution(low, high)`
- Log scale: `FloatDistribution(low, high, log=True)`
- Discrete: `FloatDistribution(low, high, step=value)`

**Integer Distributions:**
- Linear scale: `IntDistribution(low, high)`
- Log scale: `IntDistribution(low, high, log=True)`
- Stepped: `IntDistribution(low, high, step=value)`

**Categorical Distributions:**
- `CategoricalDistribution(choices)` with mixed types supported

Tests at [tests/samplers_tests/test_samplers.py:222-310]() verify that sampled values:
- Fall within distribution bounds
- Are not NumPy types (returned as native Python types)
- Respect step constraints for discrete distributions

**Sources:** [tests/samplers_tests/test_samplers.py:222-310]()

### Conditional Parameters

The test at [tests/samplers_tests/test_samplers.py:445-476]() validates that samplers handle conditional parameter spaces correctly:

```python
# Different parameters depending on categorical choice
if category == "x":
    trial.suggest_float("x", 0, 1)
else:
    trial.suggest_float("y", 0, 1)
```

This reproduces real-world scenarios where the search space structure depends on earlier parameter choices.

**Sources:** [tests/samplers_tests/test_samplers.py:445-476](), [tests/samplers_tests/test_samplers.py:852-868]()

### Dynamic Range Handling

The test at [tests/samplers_tests/test_samplers.py:892-919]() ensures samplers handle changing distribution bounds across trials:

```python
# First 10 trials: range [0, 10]
# Next 10 trials: range [20, 30]  # Non-overlapping
```

All samplers must gracefully handle such dynamic search spaces without errors.

**Sources:** [tests/samplers_tests/test_samplers.py:892-919]()

---

# Page: Integration System

# Integration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/reference/integration.rst](docs/source/reference/integration.rst)
- [optuna/integration/__init__.py](optuna/integration/__init__.py)
- [optuna/integration/botorch.py](optuna/integration/botorch.py)
- [optuna/integration/dask.py](optuna/integration/dask.py)
- [optuna/integration/mlflow.py](optuna/integration/mlflow.py)
- [optuna/integration/sklearn.py](optuna/integration/sklearn.py)
- [optuna/integration/wandb.py](optuna/integration/wandb.py)
- [optuna/samplers/_base.py](optuna/samplers/_base.py)

</details>



The Integration System provides a framework for connecting Optuna with external ML frameworks, experiment tracking tools, and optimization libraries. The system allows Optuna to leverage external tools without forcing users to install unnecessary dependencies.

The integration system migrates to an external package called `optuna-integration`, with the `optuna.integration` module serving as a lazy-loading proxy layer. This architecture ensures that `import optuna` remains fast by deferring dependency imports until integrations are actually accessed.

For details about the lazy loading mechanism, see page 4.1. For specific framework integrations and their usage, see page 4.2.

## System Overview

The integration system consists of proxy modules in the main Optuna repository that defer to implementations in the external `optuna-integration` package. This separation allows the core Optuna library to remain lightweight while supporting a wide range of external tools.

### Integration System Position in Optuna Architecture

```mermaid
graph TB
    subgraph "Core Optuna"
        Study["Study"]
        Trial["Trial"]
        BaseSampler["BaseSampler"]
        BaseStorage["BaseStorage"]
    end
    
    subgraph "optuna.integration (Proxy Layer)"
        IntegrationInit["optuna/integration/__init__.py<br/>_IntegrationModule"]
        ProxyModules["Proxy modules:<br/>mlflow.py, sklearn.py, etc."]
    end
    
    subgraph "optuna-integration (External Package)"
        MLflowCallback["MLflowCallback"]
        OptunaSearchCV["OptunaSearchCV"]
        BoTorchSampler["BoTorchSampler"]
        WeightsAndBiasesCallback["WeightsAndBiasesCallback"]
        PruningCallbacks["Framework callbacks:<br/>PyTorch, Keras, LightGBM, etc."]
    end
    
    subgraph "External Services"
        MLflow["MLflow Tracking"]
        WandB["Weights & Biases"]
        BoTorch["BoTorch Library"]
        MLFrameworks["ML Frameworks"]
    end
    
    Study --> IntegrationInit
    Trial --> IntegrationInit
    BaseSampler --> IntegrationInit
    
    IntegrationInit --> ProxyModules
    ProxyModules --> MLflowCallback
    ProxyModules --> OptunaSearchCV
    ProxyModules --> BoTorchSampler
    ProxyModules --> WeightsAndBiasesCallback
    ProxyModules --> PruningCallbacks
    
    MLflowCallback --> MLflow
    OptunaSearchCV --> Study
    BoTorchSampler --> BoTorch
    WeightsAndBiasesCallback --> WandB
    PruningCallbacks --> MLFrameworks
```

Sources: [optuna/integration/__init__.py:1-137](), [docs/source/reference/integration.rst:1-77]()

### Proxy Module Pattern

Each integration has a proxy module in `optuna/integration/` that attempts to import from `optuna_integration` and raises a formatted error if unavailable:

```mermaid
graph LR
    UserCode["User code:<br/>from optuna.integration<br/>import MLflowCallback"]
    ProxyModule["optuna/integration/mlflow.py"]
    ImportAttempt["try:<br/>from optuna_integration.mlflow<br/>import MLflowCallback"]
    Success["Import successful:<br/>Return MLflowCallback"]
    Failure["except ModuleNotFoundError:<br/>raise formatted error"]
    
    UserCode --> ProxyModule
    ProxyModule --> ImportAttempt
    ImportAttempt --> Success
    ImportAttempt --> Failure
```

**Example Proxy Module Structure** (`optuna/integration/mlflow.py`):
- Lines 4-5: Attempt import from `optuna_integration.mlflow`
- Line 7: Catch `ModuleNotFoundError` and format error message
- Line 10: Export class name in `__all__`

Sources: [optuna/integration/mlflow.py:1-11](), [optuna/integration/sklearn.py:1-11](), [optuna/integration/botorch.py:1-11]()

## Integration Categories

The `_import_structure` dictionary in [optuna/integration/__init__.py:10-34]() defines the complete mapping of integration modules to their exported classes:

| Category | Module Name | Exported Classes | Purpose |
|----------|-------------|------------------|---------|
| **Pruning Callbacks** | `keras`, `pytorch_lightning`, `tensorflow`, `xgboost`, etc. | `KerasPruningCallback`, `PyTorchLightningPruningCallback`, etc. | Report intermediate values and enable early stopping |
| **Experiment Tracking** | `mlflow`, `wandb`, `tensorboard` | `MLflowCallback`, `WeightsAndBiasesCallback`, `TensorBoardCallback` | Log study/trial metadata to external platforms |
| **Alternative Samplers** | `botorch`, `cma` | `BoTorchSampler`, `PyCmaSampler` | Extend Optuna with external optimization algorithms |
| **Distributed Storage** | `dask`, `chainermn` | `DaskStorage`, `ChainerMNStudy` | Enable parallel optimization across workers |
| **Framework Tools** | `sklearn`, `lightgbm` | `OptunaSearchCV`, `LightGBMTuner` | Provide specialized interfaces for specific frameworks |

### Integration Module Structure in Code

```mermaid
graph TB
    ImportStructure["_import_structure dict<br/>(lines 10-34)"]
    
    subgraph "Callback Integrations"
        Keras["'keras': ['KerasPruningCallback']"]
        PyTorchLightning["'pytorch_lightning':<br/>['PyTorchLightningPruningCallback']"]
        LightGBM["'lightgbm': ['LightGBMPruningCallback',<br/>'LightGBMTuner', 'LightGBMTunerCV']"]
    end
    
    subgraph "Tracking Integrations"
        MLflow["'mlflow': ['MLflowCallback']"]
        WandB["'wandb':<br/>['WeightsAndBiasesCallback']"]
        TensorBoard["'tensorboard':<br/>['TensorBoardCallback']"]
    end
    
    subgraph "Sampler Integrations"
        BoTorch["'botorch': ['BoTorchSampler']"]
        PyCma["'cma': ['PyCmaSampler']"]
    end
    
    subgraph "Other Integrations"
        Sklearn["'sklearn': ['OptunaSearchCV']"]
        Dask["'dask': ['DaskStorage']"]
    end
    
    ImportStructure --> Keras
    ImportStructure --> PyTorchLightning
    ImportStructure --> LightGBM
    ImportStructure --> MLflow
    ImportStructure --> WandB
    ImportStructure --> TensorBoard
    ImportStructure --> BoTorch
    ImportStructure --> PyCma
    ImportStructure --> Sklearn
    ImportStructure --> Dask
```

Sources: [optuna/integration/__init__.py:10-34]()

## Common Integration Patterns

Integrations follow specific patterns based on their purpose. Understanding these patterns helps in implementing or using integrations correctly.

### Callback Pattern for Pruning

Pruning callbacks integrate with ML framework training loops to enable early stopping:

```mermaid
graph LR
    Trial["Trial object"]
    Callback["Framework callback<br/>(e.g., PyTorchLightningPruningCallback)"]
    IntermediateValue["Training metric<br/>(e.g., validation loss)"]
    TrialReport["trial.report(value, step)"]
    ShouldPrune["trial.should_prune()"]
    TrialPruned["Raise TrialPruned"]
    
    Trial --> Callback
    Callback --> IntermediateValue
    IntermediateValue --> TrialReport
    TrialReport --> ShouldPrune
    ShouldPrune --> TrialPruned
```

**Pattern Elements**:
1. Callback receives `Trial` object during initialization
2. During training, callback reports intermediate values via `trial.report()`
3. Callback checks `trial.should_prune()` to determine if training should stop
4. If pruning is recommended, callback raises `TrialPruned` exception

Sources: [docs/source/reference/integration.rst:13-17]()

### Sampler Extension Pattern

Alternative samplers extend Optuna's optimization capabilities:

```mermaid
graph TB
    BaseSampler["BaseSampler<br/>(Optuna interface)"]
    WrapperSampler["BoTorchSampler<br/>(Integration wrapper)"]
    ExternalLibrary["BoTorch library<br/>(External optimizer)"]
    
    Methods["Methods:<br/>- infer_relative_search_space()<br/>- sample_relative()<br/>- sample_independent()"]
    
    BaseSampler --> WrapperSampler
    WrapperSampler --> Methods
    WrapperSampler --> ExternalLibrary
```

**Pattern Elements**:
1. Integration class inherits from or implements `BaseSampler` interface
2. Wrapper translates between Optuna's sampler API and external library API
3. Search space and parameter values are converted between formats

Sources: [optuna/samplers/_base.py:31-62](), [optuna/integration/botorch.py:1-11]()

### Experiment Tracking Pattern

Tracking callbacks log study progress to external platforms:

```mermaid
graph LR
    Study["Study.optimize()"]
    Callback["MLflowCallback or<br/>WeightsAndBiasesCallback"]
    TrialData["Trial metadata:<br/>- parameters<br/>- values<br/>- state<br/>- user_attrs"]
    ExternalPlatform["External service:<br/>MLflow, W&B, etc."]
    
    Study --> Callback
    Callback --> TrialData
    TrialData --> ExternalPlatform
```

**Pattern Elements**:
1. Callback is passed to `study.optimize(callbacks=[...])`
2. Callback receives notifications after each trial completes
3. Callback extracts trial metadata and logs to external service
4. No modification to trial execution or optimization behavior

Sources: [docs/source/reference/integration.rst:13-18]()

## Available Integrations

The integration system supports a wide range of external tools. The table below lists the most commonly used integrations and their dependencies:

| Integration | Module | Class(es) | Dependencies | Purpose |
|-------------|--------|-----------|--------------|---------|
| **MLflow** | `mlflow` | `MLflowCallback` | `mlflow` | Log trials to MLflow tracking server |
| **Weights & Biases** | `wandb` | `WeightsAndBiasesCallback` | `wandb` | Log trials to W&B cloud service |
| **TensorBoard** | `tensorboard` | `TensorBoardCallback` | `tensorboard`, `tensorflow` | Write trials to TensorBoard logs |
| **BoTorch** | `botorch` | `BoTorchSampler` | `botorch`, `gpytorch`, `torch` | Bayesian optimization with BoTorch |
| **PyCMA** | `cma` | `PyCmaSampler` | `cma` | CMA-ES optimization algorithm |
| **scikit-learn** | `sklearn` | `OptunaSearchCV` | `pandas`, `scipy`, `scikit-learn` | Drop-in replacement for GridSearchCV |
| **LightGBM** | `lightgbm` | `LightGBMTuner`, `LightGBMPruningCallback` | `lightgbm`, `scikit-learn` | LightGBM-specific optimization |
| **PyTorch Lightning** | `pytorch_lightning` | `PyTorchLightningPruningCallback` | `pytorch-lightning` | Early stopping for Lightning |
| **Keras** | `keras` | `KerasPruningCallback` | `keras` | Early stopping for Keras |
| **XGBoost** | `xgboost` | `XGBoostPruningCallback` | `xgboost` | Early stopping for XGBoost |
| **Dask** | `dask` | `DaskStorage` | `distributed` | Dask-compatible storage backend |

Sources: [docs/source/reference/integration.rst:24-76](), [optuna/integration/__init__.py:10-34]()

## Module Loading Flow

The integration system's lazy loading mechanism follows a specific flow to ensure efficient module loading:

```mermaid
sequenceDiagram
    participant User
    participant IntegrationModule as "_IntegrationModule"
    participant ImportLib as "importlib"
    participant ExternalPackage as "optuna_integration"
    
    User->>IntegrationModule: import optuna.integration.mlflow
    IntegrationModule->>IntegrationModule: __getattr__("mlflow")
    IntegrationModule->>IntegrationModule: Check _modules set
    IntegrationModule->>ImportLib: importlib.import_module(".mlflow")
    ImportLib->>ExternalPackage: Try import from optuna_integration
    alt Dependency Available
        ExternalPackage->>ImportLib: Return module
        ImportLib->>IntegrationModule: Return module
        IntegrationModule->>IntegrationModule: Cache module
        IntegrationModule->>User: Return module
    else Dependency Missing
        ExternalPackage->>ImportLib: ModuleNotFoundError
        ImportLib->>IntegrationModule: ModuleNotFoundError
        IntegrationModule->>IntegrationModule: Format error message
        IntegrationModule->>User: Raise formatted error
    end
```

Sources: [optuna/integration/__init__.py:116-134]()

The Integration System provides a robust, extensible framework for connecting Optuna with external tools while maintaining performance and graceful error handling. Its lazy loading architecture ensures that only required dependencies are loaded, while the standardized error handling provides clear guidance for users when dependencies are missing.

---

# Page: Integration Architecture and Lazy Loading

# Integration Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/reference/integration.rst](docs/source/reference/integration.rst)
- [optuna/integration/__init__.py](optuna/integration/__init__.py)
- [optuna/integration/botorch.py](optuna/integration/botorch.py)
- [optuna/integration/dask.py](optuna/integration/dask.py)
- [optuna/integration/mlflow.py](optuna/integration/mlflow.py)
- [optuna/integration/sklearn.py](optuna/integration/sklearn.py)
- [optuna/integration/wandb.py](optuna/integration/wandb.py)
- [optuna/samplers/_base.py](optuna/samplers/_base.py)

</details>



## Overview

Optuna's integration system enables deep integration with external machine learning frameworks through a standardized architecture. The system consists of two main integration patterns:

1. **Callback-based integrations**: Implement the trial reporting pattern (`trial.report()`, `trial.should_prune()`, `TrialPruned`) for frameworks with iterative training loops (PyTorch Lightning, Keras, XGBoost, etc.)
2. **Estimator-based integrations**: Provide scikit-learn-compatible wrappers that expose Optuna optimization through familiar estimator APIs (`OptunaSearchCV`)

All integrations follow a delegation architecture where Optuna's core package contains lightweight wrapper modules that delegate to the separate `optuna-integration` package. This design reduces core dependencies while maintaining a unified user interface.

## The Callback Pattern

Most Optuna integrations implement a **callback pattern** that enables early stopping of unpromising trials during model training. This pattern consists of three components:

| Component | Type | Purpose |
|-----------|------|---------|
| `trial.report(value, step)` | Method | Report intermediate metric values during training |
| `trial.should_prune()` | Method | Check if trial should be stopped early |
| `TrialPruned` | Exception | Signal trial termination to Optuna |

**Callback Pattern Workflow**

```mermaid
sequenceDiagram
    participant Framework as "ML Framework<br/>(PyTorch/Keras/XGBoost)"
    participant Callback as "Pruning Callback<br/>(Integration)"
    participant Trial as "Trial Object"
    participant Pruner as "Pruner<br/>(MedianPruner/etc)"
    participant Study as "Study"
    
    Framework->>Callback: "on_epoch_end(epoch, metrics)"
    Callback->>Trial: "report(value=metrics['loss'], step=epoch)"
    Trial->>Study: "set_trial_intermediate_value()"
    
    Callback->>Trial: "should_prune()"
    Trial->>Pruner: "prune(study, trial)"
    Pruner-->>Trial: "True (should prune)"
    Trial-->>Callback: "True"
    
    Callback->>Framework: "raise TrialPruned()"
    Framework-->>Study: "Catch exception, mark trial PRUNED"
```

The callback pattern enables integrations to:
- Report metrics at framework-specific intervals (epochs, iterations, boosting rounds)
- Query the pruner's decision without coupling to specific pruner implementations
- Terminate training gracefully using framework-specific exception handling

Sources: [docs/source/reference/integration.rst:13-17]()

## Migration to optuna-integration Package

Optuna's integrations have migrated from the core `optuna` package to a separate `optuna-integration` package. The core package retains lightweight delegation modules that preserve backward compatibility while reducing dependency bloat.

**Delegation Architecture**

```mermaid
graph TB
    User["User Code"]
    CoreModule["optuna.integration.sklearn<br/>(Core Package)"]
    TryImport["try:<br/>from optuna_integration<br/>import OptunaSearchCV"]
    ExternalPackage["optuna_integration.sklearn<br/>(External Package)"]
    OptunaSearchCV["OptunaSearchCV<br/>(Actual Implementation)"]
    ErrorTemplate["_INTEGRATION_IMPORT_ERROR_TEMPLATE"]
    ModuleNotFound["raise ModuleNotFoundError"]
    
    User --> CoreModule
    CoreModule --> TryImport
    TryImport --> ExternalPackage
    ExternalPackage --> OptunaSearchCV
    OptunaSearchCV --> User
    
    TryImport -.fails.-> ErrorTemplate
    ErrorTemplate --> ModuleNotFound
    ModuleNotFound -.exception.-> User
```

**Example Delegation Module**

```python
# optuna/integration/sklearn.py
from optuna._imports import _INTEGRATION_IMPORT_ERROR_TEMPLATE

try:
    from optuna_integration.sklearn import OptunaSearchCV
except ModuleNotFoundError:
    raise ModuleNotFoundError(_INTEGRATION_IMPORT_ERROR_TEMPLATE.format("sklearn"))

__all__ = ["OptunaSearchCV"]
```

All integration modules in the core package follow this pattern:
1. Import from `optuna_integration.<framework>`
2. Catch `ModuleNotFoundError` if package not installed
3. Re-raise with standardized error message via `_INTEGRATION_IMPORT_ERROR_TEMPLATE`
4. Export imported components via `__all__`

Sources: [optuna/integration/sklearn.py:1-11](), [optuna/integration/botorch.py:1-11](), [docs/source/reference/integration.rst:9-11]()

## Dependency Management with Error Templates

The `_INTEGRATION_IMPORT_ERROR_TEMPLATE` provides consistent error messages when optional integration packages are not installed.

**Error Template Pattern**

```mermaid
graph LR
    Import["Import Attempt"]
    Success["Integration Available"]
    Failure["ModuleNotFoundError"]
    Template["_INTEGRATION_IMPORT_ERROR_TEMPLATE"]
    FormattedMsg["Formatted Error Message:<br/>Please install optuna-integration<br/>pip install optuna-integration"]
    
    Import --> Success
    Import --> Failure
    Failure --> Template
    Template --> FormattedMsg
```

| Framework | Module Path | Error When Missing |
|-----------|-------------|-------------------|
| scikit-learn | `optuna.integration.sklearn` | `_INTEGRATION_IMPORT_ERROR_TEMPLATE.format("sklearn")` |
| BoTorch | `optuna.integration.botorch` | `_INTEGRATION_IMPORT_ERROR_TEMPLATE.format("botorch")` |
| PyTorch Lightning | `optuna.integration.pytorch_lightning` | `_INTEGRATION_IMPORT_ERROR_TEMPLATE.format("pytorch_lightning")` |

This pattern ensures:
- **Lazy loading**: Integration dependencies only required when actually used
- **Consistent UX**: All integrations provide uniform error messages
- **Migration path**: Users can upgrade to `optuna-integration` without code changes

Sources: [optuna/integration/sklearn.py:1-7](), [optuna/integration/botorch.py:1-7](), [docs/source/reference/integration.rst:9-11]()

## Integration Types

### Callback-Based Integrations

Callback-based integrations are designed for ML frameworks with **iterative training loops** (epochs, boosting rounds, training steps). These integrations implement framework-specific callback interfaces while invoking the standard Optuna pruning pattern.

**Callback Integration Components**

| Component | Description | Example Frameworks |
|-----------|-------------|-------------------|
| Callback Class | Framework-specific callback that wraps `trial.report()` and `trial.should_prune()` | `PyTorchLightningPruningCallback`, `KerasPruningCallback` |
| Metric Extraction | Extract intermediate metrics from framework training state | Loss from `trainer.callback_metrics`, validation metrics |
| Pruning Decision | Check `trial.should_prune()` and raise `TrialPruned` | After each epoch/step |

**Example Callback Integration Flow**

```mermaid
sequenceDiagram
    participant User as "User Objective Function"
    participant Trainer as "Framework Trainer<br/>(Lightning/Keras)"
    participant Callback as "PruningCallback"
    participant Trial as "Optuna Trial"
    
    User->>Trainer: "trainer.fit(model, callbacks=[callback])"
    
    loop Training Epochs
        Trainer->>Trainer: "Train epoch"
        Trainer->>Callback: "on_validation_end(metrics)"
        Callback->>Trial: "trial.report(metrics['val_loss'], epoch)"
        Callback->>Trial: "should_prune = trial.should_prune()"
        
        alt Should Prune
            Callback->>Trainer: "raise TrialPruned()"
            Trainer-->>User: "Stop training"
            User-->>User: "Handle TrialPruned exception"
        else Continue Training
            Callback-->>Trainer: "Continue"
        end
    end
    
    Trainer-->>User: "Training complete"
```

Sources: [docs/source/reference/integration.rst:13-17]()

### Estimator-Based Integrations

Estimator-based integrations provide **scikit-learn-compatible** wrappers that expose Optuna optimization through familiar estimator APIs. The primary example is `OptunaSearchCV`.

**OptunaSearchCV Architecture**

```mermaid
graph TB
    subgraph "Scikit-learn Interface"
        BaseEstimator["BaseEstimator"]
        OptunaSearchCV["OptunaSearchCV<br/>(optuna_integration.sklearn)"]
    end
    
    subgraph "Optuna Components"
        Study["Study Object<br/>(internal)"]
        Sampler["Sampler<br/>(TPESampler default)"]
        Trials["Trial Objects"]
    end
    
    subgraph "User Workflow"
        UserEstimator["User's Base Estimator<br/>(e.g., RandomForestClassifier)"]
        ParamDist["Parameter Distributions<br/>(param_distributions dict)"]
        FitMethod["fit(X, y)"]
        PredictMethod["predict(X)"]
    end
    
    BaseEstimator --> OptunaSearchCV
    OptunaSearchCV --> Study
    Study --> Sampler
    Study --> Trials
    
    UserEstimator --> OptunaSearchCV
    ParamDist --> OptunaSearchCV
    OptunaSearchCV --> FitMethod
    OptunaSearchCV --> PredictMethod
```

**Key Differences from Callback-Based Integrations**

| Aspect | Callback-Based | Estimator-Based |
|--------|---------------|----------------|
| **Interface** | Framework-specific callback API | Scikit-learn `BaseEstimator` API |
| **Trial Creation** | User creates trials in objective function | `OptunaSearchCV` manages trials internally |
| **Pruning** | Reports intermediate values during training | Evaluates complete model per trial |
| **Use Case** | Deep learning with iterative training | Scikit-learn models with cross-validation |
| **Example** | `PyTorchLightningPruningCallback` | `OptunaSearchCV` |

Sources: [docs/source/reference/integration.rst:19](), [optuna/integration/sklearn.py:1-11]()

## Framework-Specific Integrations

### PyTorch Lightning Integration

The PyTorch Lightning integration provides pruning capabilities for PyTorch Lightning training loops through `PyTorchLightningPruningCallback`.

```mermaid
graph LR
    subgraph "Pytorch Lightning Integration"
        PLModule["optuna.integration.pytorch_lightning"]
        PLCallback["PyTorchLightningPruningCallback"]
    end
    
    subgraph "PyTorch Lightning Framework"
        PLTrainer["pl.Trainer"]
        PLModule_User["pl.LightningModule"]
        PLCallback_List["callbacks=[...]"]
    end
    
    PLModule --> PLCallback
    PLCallback --> PLCallback_List
    PLCallback_List --> PLTrainer
    PLTrainer --> PLModule_User
```

**PyTorch Lightning Integration Components**
- `PyTorchLightningPruningCallback`: Callback for pruning trials during training
- Integrates with PyTorch Lightning's callback system
- Monitors training metrics and suggests trial pruning

Sources: [optuna/integration/pytorch_lightning.py:1-11]()

### Keras and TensorFlow Integrations

The Keras ecosystem includes multiple integration points for different TensorFlow variants:

| Integration Module | Callback Class | Target Framework |
|-------------------|---------------|------------------|
| `optuna.integration.keras` | `KerasPruningCallback` | Keras |
| `optuna.integration.tensorflow` | `TensorFlowPruningHook` | TensorFlow |
| `optuna.integration.tfkeras` | `TFKerasPruningCallback` | TensorFlow Keras |

```mermaid
graph TB
    subgraph "Keras Ecosystem Integrations"
        KerasModule["optuna.integration.keras"]
        TFModule["optuna.integration.tensorflow"]
        TFKerasModule["optuna.integration.tfkeras"]
    end
    
    subgraph "Framework Components"
        KerasCallback["KerasPruningCallback"]
        TFHook["TensorFlowPruningHook"]
        TFKerasCallback["TFKerasPruningCallback"]
    end
    
    subgraph "TensorFlow Ecosystem"
        Keras["Keras"]
        TensorFlow["TensorFlow"]
        TFKeras["tf.keras"]
    end
    
    KerasModule --> KerasCallback
    TFModule --> TFHook
    TFKerasModule --> TFKerasCallback
    
    KerasCallback --> Keras
    TFHook --> TensorFlow
    TFKerasCallback --> TFKeras
```

**Keras Integration Types**
- **Keras**: Standard Keras callback for pruning
- **TensorFlow**: Low-level TensorFlow hook for session-based training
- **TensorFlow Keras**: TensorFlow 2.x integrated Keras callback

Sources: [optuna/integration/keras.py:1-11](), [optuna/integration/tensorflow.py:1-11](), [optuna/integration/tfkeras.py:1-11]()

### Gradient Boosting Framework Integrations

Optuna provides comprehensive integration with gradient boosting frameworks, with special attention to LightGBM:

```mermaid
graph TB
    subgraph "Gradient Boosting Integrations"
        XGBModule["optuna.integration.xgboost"]
        LGBModule["optuna.integration.lightgbm"]
    end
    
    subgraph "XGBoost Integration"
        XGBCallback["XGBoostPruningCallback"]
    end
    
    subgraph "LightGBM Integration"
        LGBModuleClass["_LightGBMModule"]
        LGBCallback["LightGBMPruningCallback"]
        LGBTuner["LightGBMTuner"]
        LGBTunerCV["LightGBMTunerCV"]
        LGBTrain["train"]
    end
    
    XGBModule --> XGBCallback
    LGBModule --> LGBModuleClass
    LGBModuleClass --> LGBCallback
    LGBModuleClass --> LGBTuner
    LGBModuleClass --> LGBTunerCV
    LGBModuleClass --> LGBTrain
```

**LightGBM Special Architecture**
- `_LightGBMModule`: Custom module class implementing dynamic attribute access
- Provides both pruning callbacks and full optimization tuners
- Supports cross-validation tuning through `LightGBMTunerCV`

Sources: [optuna/integration/xgboost.py:1-11](), [optuna/integration/lightgbm.py:1-44]()

### Additional Framework Integrations

Optuna supports additional ML frameworks through dedicated integrations:

| Framework | Integration Module | Callback/Extension |
|-----------|-------------------|-------------------|
| Chainer | `optuna.integration.chainer` | `ChainerPruningExtension` |
| MXNet | `optuna.integration.mxnet` | `MXNetPruningCallback` |
| PyTorch Ignite | `optuna.integration.pytorch_ignite` | `PyTorchIgnitePruningHandler` |

```mermaid
graph LR
    subgraph "Additional Framework Integrations"
        ChainerModule["optuna.integration.chainer"]
        MXNetModule["optuna.integration.mxnet"]
        IgniteModule["optuna.integration.pytorch_ignite"]
    end
    
    subgraph "Framework Components"
        ChainerExt["ChainerPruningExtension"]
        MXNetCallback["MXNetPruningCallback"]
        IgniteHandler["PyTorchIgnitePruningHandler"]
    end
    
    ChainerModule --> ChainerExt
    MXNetModule --> MXNetCallback
    IgniteModule --> IgniteHandler
```

**Framework-Specific Components**
- **Chainer**: Extension-based pruning for Chainer training loops
- **MXNet**: Callback-based pruning for MXNet training
- **PyTorch Ignite**: Handler-based pruning for PyTorch Ignite engines

Sources: [optuna/integration/chainer.py:1-11](), [optuna/integration/mxnet.py:1-11](), [optuna/integration/pytorch_ignite.py:1-11]()

## Integration Error Handling

All integrations implement consistent error handling through the `_INTEGRATION_IMPORT_ERROR_TEMPLATE`:

```mermaid
graph TB
    subgraph "Error Handling Flow"
        TryImport["try: import optuna_integration.<framework>"]
        ImportSuccess["Import successful"]
        ImportFailed["ModuleNotFoundError"]
        ErrorTemplate["_INTEGRATION_IMPORT_ERROR_TEMPLATE"]
        FormattedError["Formatted error message"]
    end
    
    TryImport --> ImportSuccess
    TryImport --> ImportFailed
    ImportFailed --> ErrorTemplate
    ErrorTemplate --> FormattedError
```

**Error Handling Pattern**
- Each integration module attempts to import from `optuna_integration`
- Failed imports trigger standardized error messages
- Error template provides consistent user guidance for missing dependencies

Sources: [optuna/integration/pytorch_lightning.py:4-7](), [optuna/integration/keras.py:4-7](), [optuna/integration/xgboost.py:4-7]()

## LightGBM Module Implementation

The LightGBM integration uses a special module implementation that provides dynamic attribute access:

```mermaid
graph TB
    subgraph "LightGBM Module Architecture"
        ModuleClass["_LightGBMModule(ModuleType)"]
        GetAttr["__getattr__(name)"]
        LGBDict["lgb.__dict__[name]"]
        SysModules["sys.modules[__name__]"]
    end
    
    subgraph "Module Attributes"
        AllAttr["__all__"]
        FileAttr["__file__"]
        PathAttr["__path__"]
    end
    
    ModuleClass --> GetAttr
    GetAttr --> LGBDict
    ModuleClass --> SysModules
    ModuleClass --> AllAttr
    ModuleClass --> FileAttr
    ModuleClass --> PathAttr
```

**LightGBM Module Features**
- `_LightGBMModule`: Custom `ModuleType` subclass for dynamic attribute access
- `__getattr__`: Delegates attribute access to underlying `optuna_integration.lightgbm`
- `sys.modules` replacement: Replaces module in module cache for transparent access

Sources: [optuna/integration/lightgbm.py:32-44]()

---

# Page: ML Framework Integrations

# ML Framework Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/integration/__init__.py](optuna/integration/__init__.py)
- [optuna/integration/dask.py](optuna/integration/dask.py)
- [optuna/integration/mlflow.py](optuna/integration/mlflow.py)
- [optuna/integration/wandb.py](optuna/integration/wandb.py)

</details>



## Purpose and Scope

This document covers Optuna's integrations with external machine learning frameworks and tools. These integrations enable seamless use of Optuna's optimization capabilities within existing ML workflows. The integrations are organized into five categories: experiment tracking, ML framework pruning callbacks, advanced samplers, distributed computing, and scikit-learn compatibility.

For information about the lazy loading architecture and general callback patterns used by integrations, see [Integration Architecture and Lazy Loading](#4.1).

**Sources:** [optuna/integration/__init__.py:1-137]()

---

## Integration Categories

Optuna provides integrations across multiple categories, each serving a distinct purpose within the ML workflow. All integrations are defined in the `_import_structure` dictionary and loaded lazily to minimize import overhead.

```mermaid
graph TB
    subgraph "Experiment Tracking"
        MLflow["MLflowCallback<br/>optuna.integration.mlflow"]
        WandB["WeightsAndBiasesCallback<br/>optuna.integration.wandb"]
        TensorBoard["TensorBoardCallback<br/>optuna.integration.tensorboard"]
    end
    
    subgraph "ML Framework Callbacks"
        PyTorchLightning["PyTorchLightningPruningCallback<br/>optuna.integration.pytorch_lightning"]
        Keras["KerasPruningCallback<br/>optuna.integration.keras"]
        TFKeras["TFKerasPruningCallback<br/>optuna.integration.tfkeras"]
        LightGBM["LightGBMPruningCallback<br/>LightGBMTuner<br/>LightGBMTunerCV"]
        XGBoost["XGBoostPruningCallback<br/>optuna.integration.xgboost"]
        CatBoost["CatBoostPruningCallback<br/>optuna.integration.catboost"]
        FastAI["FastAIV2PruningCallback<br/>optuna.integration.fastaiv2"]
        Skorch["SkorchPruningCallback<br/>optuna.integration.skorch"]
        PyTorchIgnite["PyTorchIgnitePruningHandler<br/>optuna.integration.pytorch_ignite"]
        MXNet["MXNetPruningCallback<br/>optuna.integration.mxnet"]
        TensorFlow["TensorFlowPruningHook<br/>optuna.integration.tensorflow"]
        Chainer["ChainerPruningExtension<br/>optuna.integration.chainer"]
        AllenNLP["AllenNLPPruningCallback<br/>AllenNLPExecutor"]
    end
    
    subgraph "Advanced Samplers"
        BoTorch["BoTorchSampler<br/>optuna.integration.botorch"]
        PyCma["PyCmaSampler<br/>optuna.integration.cma"]
    end
    
    subgraph "Distributed Computing"
        Dask["DaskStorage<br/>optuna.integration.dask"]
        ChainerMN["ChainerMNStudy<br/>optuna.integration.chainermn"]
        PyTorchDist["TorchDistributedTrial<br/>optuna.integration.pytorch_distributed"]
    end
    
    subgraph "scikit-learn Integration"
        OptunaSearchCV["OptunaSearchCV<br/>optuna.integration.sklearn"]
    end
    
    subgraph "Additional Tools"
        Shap["ShapleyImportanceEvaluator<br/>optuna.integration.shap"]
    end
```

**Integration Categories and Use Cases:**

| Category | Purpose | Key Integrations |
|----------|---------|------------------|
| Experiment Tracking | Log trials, parameters, and metrics to external tracking platforms | MLflow, Weights & Biases, TensorBoard |
| ML Framework Callbacks | Enable pruning within framework training loops | PyTorch Lightning, Keras, LightGBM, XGBoost |
| Advanced Samplers | Provide alternative optimization algorithms via external libraries | BoTorch (Bayesian optimization), PyCMA (CMA-ES) |
| Distributed Computing | Enable distributed optimization across multiple workers | Dask, ChainerMN, PyTorch Distributed |
| scikit-learn | Drop-in replacement for GridSearchCV/RandomizedSearchCV | OptunaSearchCV |

**Sources:** [optuna/integration/__init__.py:10-34](), [optuna/integration/__init__.py:37-65]()

---

## Common Integration Patterns

### Pruning Callback Pattern

ML framework integrations typically implement a callback pattern that reports intermediate metrics to Optuna and checks for pruning decisions. The callback integrates into the framework's training loop lifecycle.

```mermaid
sequenceDiagram
    participant Framework as "ML Framework<br/>(PyTorch/Keras/etc)"
    participant Callback as "PruningCallback"
    participant Trial as "optuna.trial.Trial"
    participant Pruner as "BasePruner"
    
    Framework->>Callback: Initialize with trial
    Note over Callback: Store trial reference
    
    loop Training Loop
        Framework->>Callback: on_epoch_end(epoch, metrics)
        Callback->>Trial: report(intermediate_value, step)
        Trial->>Pruner: should_prune()
        Pruner-->>Trial: pruning_decision
        
        alt Should Prune
            Trial-->>Callback: TrialPruned exception
            Callback->>Framework: Stop training
            Framework-->>Callback: Training stopped
        else Continue
            Pruner-->>Callback: Continue
            Framework->>Framework: Next epoch
        end
    end
    
    Framework->>Callback: on_training_end()
    Callback-->>Framework: Cleanup
```

**Callback Lifecycle Methods:**

| Method | Purpose | Called When |
|--------|---------|-------------|
| `__init__(trial)` | Store trial reference | Callback instantiation |
| `on_epoch_end()` | Report metric and check pruning | After each training epoch |
| `on_batch_end()` | Report metric and check pruning (optional) | After each training batch |
| `on_training_end()` | Cleanup resources | Training completes |

**Sources:** [optuna/integration/__init__.py:20-32]()

### Experiment Tracking Callback Pattern

Experiment tracking integrations log study metadata, trial parameters, and optimization results to external platforms. These callbacks hook into the Study's lifecycle rather than individual trials.

```mermaid
graph LR
    Study["optuna.study.Study"]
    Callback["Tracking Callback<br/>(MLflow/WandB/TensorBoard)"]
    Platform["External Platform<br/>(MLflow/WandB/TensorBoard)"]
    
    Study -->|"add_trial_callback(callback)"| Callback
    Callback -->|"Log trial params"| Platform
    Callback -->|"Log trial values"| Platform
    Callback -->|"Log trial state"| Platform
    Callback -->|"Log user attributes"| Platform
    Callback -->|"Log system attributes"| Platform
```

**Experiment tracking callbacks typically log:**
- Trial parameters and distributions
- Objective values (single or multi-objective)
- Trial state (COMPLETE, PRUNED, FAIL)
- User-defined attributes
- System attributes (sampler, pruner)
- Intermediate values (learning curves)
- Study metadata (study name, directions)

**Sources:** [optuna/integration/__init__.py:18-19](), [optuna/integration/__init__.py:29]()

---

## Key Integrations

### MLflow Integration

The `MLflowCallback` logs Optuna trials to MLflow tracking server, enabling centralized experiment management and result visualization.

**Module Location:** [optuna/integration/mlflow.py:1-11]()

**Implementation Pattern:**
```
optuna.integration.mlflow
    └── Imports from optuna_integration.mlflow.MLflowCallback
    └── Raises ModuleNotFoundError if optuna-integration not installed
```

**Logged Information:**
- Trial parameters as MLflow parameters
- Objective values as MLflow metrics
- Trial state as MLflow tags
- User attributes as MLflow tags
- System attributes (sampler name, pruner name)
- Intermediate values as time-series metrics

**Usage Pattern:**
```python
import optuna
from optuna.integration.mlflow import MLflowCallback

mlflow_callback = MLflowCallback(
    tracking_uri="http://localhost:5000",
    metric_name="accuracy"
)

study = optuna.create_study()
study.optimize(objective, n_trials=100, callbacks=[mlflow_callback])
```

**Sources:** [optuna/integration/mlflow.py:1-11](), [optuna/integration/__init__.py:18]()

### Weights & Biases Integration

The `WeightsAndBiasesCallback` logs trials to Weights & Biases platform for experiment tracking, visualization, and collaboration.

**Module Location:** [optuna/integration/wandb.py:1-11]()

**Implementation Pattern:**
```
optuna.integration.wandb
    └── Imports from optuna_integration.wandb.WeightsAndBiasesCallback
    └── Raises ModuleNotFoundError if optuna-integration not installed
```

**Features:**
- Automatic W&B run creation per trial
- Parameter logging to W&B config
- Metric logging with step information
- Parallel coordinate plots
- Hyperparameter importance plots
- Optimization history visualization

**Sources:** [optuna/integration/wandb.py:1-11](), [optuna/integration/__init__.py:19]()

### OptunaSearchCV (scikit-learn Integration)

`OptunaSearchCV` provides a drop-in replacement for scikit-learn's `GridSearchCV` and `RandomizedSearchCV`, enabling sophisticated hyperparameter optimization with Optuna's samplers.

**Module:** `optuna.integration.sklearn`

**Key Features:**

| Feature | Description |
|---------|-------------|
| scikit-learn API compatibility | Implements `fit()`, `predict()`, `score()` methods |
| Cross-validation support | Integrates with scikit-learn's CV splitters |
| Sampler selection | Use any Optuna sampler (TPE, GP, CMA-ES, etc.) |
| Pruning support | Early-stop unpromising hyperparameter combinations |
| Warm start | Resume optimization from previous runs |
| Best estimator access | Retrieve best model via `best_estimator_` attribute |

**Distribution Mapping:**
- `scipy.stats` distributions → Optuna distributions
- `IntDistribution` for integer parameters
- `FloatDistribution` for continuous parameters
- `CategoricalDistribution` for discrete choices

**Advantages over GridSearchCV:**
- Intelligent sampling instead of exhaustive search
- Pruning of unpromising trials
- Multi-objective optimization support
- Study persistence via storage backends

**Sources:** [optuna/integration/__init__.py:25](), [optuna/integration/__init__.py:89]()

### BoTorch Integration

The `BoTorchSampler` provides Bayesian optimization using Facebook Research's BoTorch library, offering advanced acquisition functions and constraints.

**Module:** `optuna.integration.botorch`

**Key Capabilities:**

```mermaid
graph TB
    BoTorchSampler["BoTorchSampler<br/>optuna.integration.botorch"]
    
    subgraph "BoTorch Components"
        GP["Gaussian Process Model<br/>BoTorch GP"]
        AcqFunc["Acquisition Functions<br/>EI, UCB, qEI, qEHVI"]
        Optimizer["Acquisition Optimizer<br/>L-BFGS-B, Sequential"]
        Constraints["Outcome Constraints"]
    end
    
    subgraph "Optuna Integration"
        BaseSampler["BaseSampler<br/>sample_relative()<br/>sample_independent()"]
        Study["optuna.study.Study"]
    end
    
    BoTorchSampler -->|"Uses"| GP
    BoTorchSampler -->|"Uses"| AcqFunc
    BoTorchSampler -->|"Uses"| Optimizer
    BoTorchSampler -->|"Supports"| Constraints
    
    BoTorchSampler -->|"Implements"| BaseSampler
    Study -->|"Uses"| BoTorchSampler
```

**Features:**
- Quasi-Monte Carlo acquisition function optimization
- Multi-objective optimization with qEHVI (Expected Hypervolume Improvement)
- Outcome constraints (e.g., runtime < threshold)
- Batch sampling for parallel optimization
- Custom GP priors and kernels

**Use Cases:**
- Expensive black-box optimization
- Multi-objective optimization with constraints
- Batch parallel optimization
- Transfer learning via GP priors

**Sources:** [optuna/integration/__init__.py:12](), [optuna/integration/__init__.py:71]()

### PyTorch Lightning Integration

The `PyTorchLightningPruningCallback` enables early stopping of PyTorch Lightning training based on intermediate metrics.

**Module:** `optuna.integration.pytorch_lightning`

**Integration Points:**

```mermaid
graph LR
    Trainer["pl.Trainer"]
    Callback["PyTorchLightningPruningCallback"]
    Trial["optuna.trial.Trial"]
    LightningModule["pl.LightningModule"]
    
    Trainer -->|"callbacks=[callback]"| Callback
    Callback -->|"Store reference"| Trial
    LightningModule -->|"Log metrics"| Trainer
    Trainer -->|"on_validation_end()"| Callback
    Callback -->|"trial.report()"| Trial
    Trial -->|"should_prune()"| Callback
    Callback -->|"trainer.should_stop=True"| Trainer
```

**Implementation Pattern:**
1. Create `PyTorchLightningPruningCallback` with trial and metric name
2. Pass callback to `pl.Trainer(callbacks=[...])`
3. Lightning module logs metrics via `self.log(metric_name, value)`
4. Callback retrieves metric and reports to trial
5. If pruned, callback sets `trainer.should_stop = True`

**Monitored Metrics:**
- Validation loss
- Validation accuracy
- Custom logged metrics

**Sources:** [optuna/integration/__init__.py:24](), [optuna/integration/__init__.py:87]()

### LightGBM Integration

Optuna provides three LightGBM integrations: `LightGBMPruningCallback`, `LightGBMTuner`, and `LightGBMTunerCV`.

**Module:** `optuna.integration.lightgbm`

**Components:**

| Component | Purpose | Usage Pattern |
|-----------|---------|---------------|
| `LightGBMPruningCallback` | Prune during `lgb.train()` | Manual parameter suggestion |
| `LightGBMTuner` | Automatic hyperparameter tuning | Replace `lgb.train()` |
| `LightGBMTunerCV` | Automatic tuning with CV | Replace `lgb.cv()` |

**LightGBMTuner Workflow:**

```mermaid
sequenceDiagram
    participant User
    participant LGBMTuner as "LightGBMTuner"
    participant Study as "optuna.Study"
    participant Trial as "Trial"
    participant LGBM as "lightgbm.train()"
    
    User->>LGBMTuner: __init__(params, train_set, valid_sets)
    LGBMTuner->>Study: create_study()
    
    User->>LGBMTuner: run()
    
    loop n_trials
        LGBMTuner->>Study: optimize(objective)
        Study->>Trial: Create trial
        Trial->>LGBMTuner: Suggest params
        
        LGBMTuner->>LGBM: train(params, callbacks=[pruning])
        
        loop Boosting iterations
            LGBM->>LGBMTuner: Callback reports metric
            LGBMTuner->>Trial: report(metric, iteration)
            Trial->>LGBMTuner: Check pruning
            
            alt Should Prune
                LGBMTuner->>LGBM: Stop training
            end
        end
        
        LGBM-->>LGBMTuner: Final metric
        LGBMTuner->>Trial: Return objective value
    end
    
    LGBMTuner-->>User: Best booster
```

**Tuned Hyperparameters:**
- `num_leaves`, `max_depth` (tree structure)
- `learning_rate`, `feature_fraction` (training dynamics)
- `bagging_fraction`, `bagging_freq` (sampling)
- `lambda_l1`, `lambda_l2` (regularization)
- `min_child_samples` (leaf constraints)

**Sources:** [optuna/integration/__init__.py:21](), [optuna/integration/__init__.py:80-82]()

### Dask Integration

The `DaskStorage` enables distributed Optuna studies using Dask's distributed scheduler.

**Module Location:** [optuna/integration/dask.py:1-11]()

**Implementation Pattern:**
```
optuna.integration.dask
    └── Imports from optuna_integration.dask.DaskStorage
    └── Raises ModuleNotFoundError if optuna-integration not installed
```

**Architecture:**

```mermaid
graph TB
    subgraph "Dask Cluster"
        Scheduler["Dask Scheduler"]
        Worker1["Dask Worker 1"]
        Worker2["Dask Worker 2"]
        Worker3["Dask Worker 3"]
    end
    
    subgraph "Optuna Layer"
        Study["optuna.Study<br/>storage=DaskStorage"]
        DaskStorage["DaskStorage"]
    end
    
    subgraph "Backend Storage"
        RDB["RDBStorage<br/>(PostgreSQL/MySQL)"]
    end
    
    Study --> DaskStorage
    DaskStorage --> RDB
    
    Worker1 -->|"Read/Write trials"| DaskStorage
    Worker2 -->|"Read/Write trials"| DaskStorage
    Worker3 -->|"Read/Write trials"| DaskStorage
    
    Scheduler -->|"Schedule trials"| Worker1
    Scheduler -->|"Schedule trials"| Worker2
    Scheduler -->|"Schedule trials"| Worker3
```

**Features:**
- Distributed trial execution across Dask workers
- Shared storage backend for trial synchronization
- Fault tolerance via Dask's task retry mechanism
- Dynamic worker scaling

**Use Cases:**
- Large-scale hyperparameter search
- Distributed training of models
- Cloud-based optimization (e.g., Dask on Kubernetes)

**Sources:** [optuna/integration/dask.py:1-11](), [optuna/integration/__init__.py:17]()

---

## Integration Loading Architecture

All integrations use lazy loading implemented by `_IntegrationModule` to avoid importing unused dependencies.

**Loading Mechanism:**

```mermaid
graph TB
    User["User Code:<br/>from optuna.integration import MLflowCallback"]
    IntegrationModule["_IntegrationModule<br/>__getattr__()"]
    ImportStructure["_import_structure<br/>{'mlflow': ['MLflowCallback']}"]
    ClassToModule["_class_to_module<br/>{'MLflowCallback': 'mlflow'}"]
    GetModule["_get_module('mlflow')"]
    ImportLib["importlib.import_module<br/>('.mlflow', 'optuna.integration')"]
    ActualModule["optuna/integration/mlflow.py"]
    ExternalPackage["optuna_integration.mlflow"]
    
    User --> IntegrationModule
    IntegrationModule --> ClassToModule
    ClassToModule --> GetModule
    GetModule --> ImportLib
    ImportLib --> ActualModule
    ActualModule --> ExternalPackage
    
    ImportStructure -.builds.-> ClassToModule
```

**Loading Flow:**

1. User imports integration class (e.g., `from optuna.integration import MLflowCallback`)
2. `_IntegrationModule.__getattr__("MLflowCallback")` is called
3. Lookup class in `_class_to_module` to find module name (`"mlflow"`)
4. Call `_get_module("mlflow")` to import `optuna.integration.mlflow`
5. `optuna/integration/mlflow.py` imports from `optuna_integration.mlflow`
6. If `optuna-integration` not installed, raise `ModuleNotFoundError` with helpful message
7. Cache imported class in module for subsequent access

**Error Handling:**

When an integration's dependencies are not installed, Optuna raises a descriptive error:

```python
# Template from optuna/_imports.py
_INTEGRATION_IMPORT_ERROR_TEMPLATE = (
    "optuna-integration is not installed. "
    "Please install optuna-integration to use {0} integration."
)
```

**Benefits:**
- Fast `import optuna` even with many integrations
- Only pay import cost for used integrations
- Clear error messages for missing dependencies
- Maintains IDE autocomplete via `TYPE_CHECKING` block

**Sources:** [optuna/integration/__init__.py:98-136](), [optuna/integration/mlflow.py:1-11](), [optuna/integration/wandb.py:1-11](), [optuna/integration/dask.py:1-11]()

---

## Integration Summary Table

| Integration | Type | Primary Use Case | Key Classes |
|-------------|------|------------------|-------------|
| **MLflow** | Experiment Tracking | Log trials to MLflow server | `MLflowCallback` |
| **Weights & Biases** | Experiment Tracking | Log trials to W&B platform | `WeightsAndBiasesCallback` |
| **TensorBoard** | Experiment Tracking | Log trials to TensorBoard | `TensorBoardCallback` |
| **PyTorch Lightning** | Pruning Callback | Early-stop Lightning training | `PyTorchLightningPruningCallback` |
| **Keras** | Pruning Callback | Early-stop Keras training | `KerasPruningCallback` |
| **TensorFlow Keras** | Pruning Callback | Early-stop TF Keras training | `TFKerasPruningCallback` |
| **LightGBM** | Pruning + Tuner | Tune LightGBM hyperparameters | `LightGBMPruningCallback`, `LightGBMTuner`, `LightGBMTunerCV` |
| **XGBoost** | Pruning Callback | Early-stop XGBoost training | `XGBoostPruningCallback` |
| **CatBoost** | Pruning Callback | Early-stop CatBoost training | `CatBoostPruningCallback` |
| **FastAI** | Pruning Callback | Early-stop FastAI training | `FastAIV2PruningCallback` |
| **scikit-learn** | Search Utility | Drop-in GridSearchCV replacement | `OptunaSearchCV` |
| **BoTorch** | Advanced Sampler | Bayesian optimization with BoTorch | `BoTorchSampler` |
| **PyCMA** | Advanced Sampler | CMA-ES via pycma library | `PyCmaSampler` |
| **Dask** | Distributed Storage | Distributed optimization | `DaskStorage` |
| **ChainerMN** | Distributed Computing | Multi-node Chainer training | `ChainerMNStudy` |
| **PyTorch Distributed** | Distributed Computing | Distributed PyTorch trials | `TorchDistributedTrial` |
| **SHAP** | Importance Analysis | Shapley-based parameter importance | `ShapleyImportanceEvaluator` |

**Sources:** [optuna/integration/__init__.py:10-34](), [optuna/integration/__init__.py:37-65]()

---

# Page: Tools and User Interfaces

# Tools and User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [optuna/cli.py](optuna/cli.py)
- [pyproject.toml](pyproject.toml)
- [tests/test_cli.py](tests/test_cli.py)

</details>



This document provides an overview of the tools and interfaces available for interacting with Optuna beyond its core Python API. These tools enhance the usability of Optuna by providing command-line access, visualization capabilities, and artifact management features.

## Command Line Interface

Optuna provides a comprehensive command-line interface through `optuna.cli` that allows users to manage studies and trials without writing Python code. The CLI is particularly useful for checking study status, managing studies, and integrating Optuna into shell scripts or automation workflows.

### CLI Architecture

```mermaid
flowchart TD
    CLIMain["main()"] -->|"calls"| GetParser["_get_parser()"]
    GetParser -->|"creates"| ArgumentParser["ArgumentParser"]
    GetParser -->|"calls"| AddCommands["_add_commands()"]
    
    AddCommands -->|"registers"| CommandClasses["_COMMANDS dict"]
    
    subgraph CommandClasses["Command Classes (_BaseCommand)"]
        CreateStudy["_CreateStudy"]
        DeleteStudy["_DeleteStudy"] 
        StudySetUserAttr["_StudySetUserAttribute"]
        StudyNames["_StudyNames"]
        Studies["_Studies"]
        Trials["_Trials"]
        BestTrial["_BestTrial"]
        BestTrials["_BestTrials"]
        StorageUpgrade["_StorageUpgrade"]
        Ask["_Ask"]
        Tell["_Tell"]
    end
    
    ArgumentParser -->|"dispatches to"| TakeAction["take_action()"]
    TakeAction -->|"calls"| GetStorage["_get_storage()"]
    
    subgraph StorageBackends["Storage Backends"]
        RDBStorage["RDBStorage"]
        JournalStorage["JournalStorage"]
        JournalFileBackend["JournalFileBackend"]
        JournalRedisBackend["JournalRedisBackend"]
    end
    
    GetStorage -->|"returns"| StorageBackends
```

Sources: [optuna/cli.py:979-1007](), [optuna/cli.py:814-826](), [optuna/cli.py:273-304](), [optuna/cli.py:57-79]()

### Available Commands

The CLI commands are defined in the `_COMMANDS` dictionary and implemented as `_BaseCommand` subclasses:

| Command | Class | Description |
|---------|-------|-------------|
| `create-study` | `_CreateStudy` | Create a new study with optional direction/directions |
| `delete-study` | `_DeleteStudy` | Delete a specified study from storage |
| `study set-user-attr` | `_StudySetUserAttribute` | Set a user attribute to a study |
| `study-names` | `_StudyNames` | Get all study names stored in a storage backend |
| `studies` | `_Studies` | Show a list of studies with metadata |
| `trials` | `_Trials` | Show a list of trials in a study (experimental) |
| `best-trial` | `_BestTrial` | Show the best trial of a study (experimental) |
| `best-trials` | `_BestTrials` | Show trials at the Pareto front (experimental) |
| `storage upgrade` | `_StorageUpgrade` | Upgrade the schema of an RDB storage |
| `ask` | `_Ask` | Create a new trial and suggest parameters (experimental) |
| `tell` | `_Tell` | Finish a trial with values and state (experimental) |

Each command class inherits from `_BaseCommand` and implements `add_arguments()` and `take_action()` methods.

Sources: [optuna/cli.py:814-826](), [optuna/cli.py:273-304](), [optuna/cli.py:307-352](), [optuna/cli.py:655-811]()

### Output Formats

The CLI supports multiple output formats through the `_format_output()` function:

- `value`: Simple space-separated values output
- `table`: Formatted ASCII table with `_dump_table()`  
- `json`: JSON format using `json.dumps()`
- `yaml`: YAML format using `yaml.safe_dump()`

```bash
# Example of using different output formats
optuna studies --storage sqlite:///example.db --format json
optuna trials --study-name "my_study" --storage sqlite:///example.db --format table
```

The formatting system uses `_format_value()` to handle various data types including `datetime` objects, lists, tuples, and nested dictionaries. The `_convert_to_dict()` function processes multi-index column structures and supports flattening via the `--flatten` flag.

Sources: [optuna/cli.py:244-270](), [optuna/cli.py:82-95](), [optuna/cli.py:98-153](), [optuna/cli.py:191-241]()

## Visualization System

Optuna provides comprehensive visualization capabilities for analyzing optimization results. The visualization system supports both Plotly and Matplotlib backends with various plot types to understand parameter relationships and optimization progress.

For detailed information about visualization features, implementations, and plotting backends, see [Page 5.2: Visualization]().

## Artifact Management

Optuna includes an artifact system for storing and retrieving files associated with trials, such as model checkpoints, plots, or other outputs generated during optimization. This enables reproducibility and sharing of optimization artifacts across different environments.

For detailed information about the artifact management system, storage backends, and usage patterns, see [Page 5.3: Artifact Management]().

## Integration of Tools

The CLI, visualization tools, and artifact management work together to provide a comprehensive toolset for hyperparameter optimization:

```mermaid
flowchart TD
    User(["User"])
    
    subgraph "Interfaces"
        CLI["Command Line Interface"]
        PythonAPI["Python API"]
    end
    
    subgraph "Analysis Tools"
        Visualization["Visualization Tools"]
        Dashboard["Dashboard"]
    end
    
    subgraph "Storage"
        Database["Database Storage"]
        ArtifactStorage["Artifact Storage"]
    end
    
    User -->|"Uses"| CLI
    User -->|"Uses"| PythonAPI
    
    CLI -->|"Access"| Database
    PythonAPI -->|"Access"| Database
    PythonAPI -->|"Saves Files"| ArtifactStorage
    
    Database -->|"Provides Data"| Visualization
    Database -->|"Provides Data"| Dashboard
    ArtifactStorage -->|"Provides Files"| Dashboard
    
    Visualization -->|"Displays to"| User
    Dashboard -->|"Displays to"| User
```

Sources: Based on the overall system architecture diagram provided.

This integrated set of tools allows for a flexible workflow, where users can:
1. Define and run studies using the Python API
2. Monitor progress via the CLI or dashboard
3. Analyze results using visualization tools
4. Access artifacts (models, checkpoints) for deployment or further analysis

Each tool serves a specific purpose in the optimization workflow, enabling users to efficiently navigate the hyperparameter space and identify optimal configurations for their machine learning models.

---

# Page: Command-Line Interface

# Command Line Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optuna/cli.py](optuna/cli.py)
- [tests/test_cli.py](tests/test_cli.py)

</details>



This document describes Optuna's command line interface (CLI) system, which provides programmatic access to study and trial management operations from the command line. The CLI enables users to create studies, manage trials, query optimization results, and perform storage operations without writing Python code.

For information about Optuna's Python API for study management, see [Study and Trial Management](2.1). For details about storage backends used by the CLI, see [Storage System](2.3).

## Purpose and Architecture

The CLI system provides a unified interface for interacting with Optuna studies and trials through shell commands. It supports multiple storage backends, various output formats, and implements a modular command structure where each operation is handled by a dedicated command class.

### CLI Architecture Overview

```mermaid
graph TB
    subgraph "CLI Entry Point"
        main["main()"]
        parser["_get_parser()"]
        preprocess["_preprocess_argv()"]
    end
    
    subgraph "Command System"
        BaseCommand["_BaseCommand"]
        CreateStudy["_CreateStudy"]
        DeleteStudy["_DeleteStudy"]
        Studies["_Studies"]
        Trials["_Trials"]
        Ask["_Ask"]
        Tell["_Tell"]
        BestTrial["_BestTrial"]
        StorageUpgrade["_StorageUpgrade"]
    end
    
    subgraph "Storage Integration"
        get_storage["_get_storage()"]
        check_storage["_check_storage_url()"]
        BaseStorage["BaseStorage"]
        RDBStorage["RDBStorage"]
        JournalStorage["JournalStorage"]
    end
    
    subgraph "Output Formatting"
        format_output["_format_output()"]
        dump_table["_dump_table()"]
        dump_value["_dump_value()"]
        convert_to_dict["_convert_to_dict()"]
    end
    
    main --> parser
    main --> preprocess
    parser --> BaseCommand
    
    BaseCommand --> CreateStudy
    BaseCommand --> DeleteStudy
    BaseCommand --> Studies
    BaseCommand --> Trials
    BaseCommand --> Ask
    BaseCommand --> Tell
    BaseCommand --> BestTrial
    BaseCommand --> StorageUpgrade
    
    CreateStudy --> get_storage
    DeleteStudy --> get_storage
    Studies --> get_storage
    Trials --> get_storage
    Ask --> get_storage
    Tell --> get_storage
    
    get_storage --> check_storage
    get_storage --> BaseStorage
    BaseStorage --> RDBStorage
    BaseStorage --> JournalStorage
    
    Studies --> format_output
    Trials --> format_output
    BestTrial --> format_output
    Ask --> format_output
    
    format_output --> dump_table
    format_output --> dump_value
    format_output --> convert_to_dict
```

Sources: [optuna/cli.py:1-1008]()

## Command Structure and Registration

The CLI uses a class-based command system where each command inherits from `_BaseCommand`. Commands are registered in the `_COMMANDS` dictionary, which maps command names to their implementation classes.

### Command Registration System

```mermaid
graph LR
    subgraph "Command Registration"
        COMMANDS["_COMMANDS dict"]
        command_names["Command Names"]
        command_classes["Command Classes"]
    end
    
    subgraph "Command Parsing"
        add_commands["_add_commands()"]
        subparsers["ArgumentParser.add_subparsers()"]
        individual_parsers["Individual Command Parsers"]
    end
    
    subgraph "Execution Flow"
        preprocess_argv["_preprocess_argv()"]
        parse_args["main_parser.parse_args()"]
        handler["args.handler()"]
        take_action["command.take_action()"]
    end
    
    COMMANDS --> command_names
    COMMANDS --> command_classes
    
    command_names --> add_commands
    command_classes --> add_commands
    add_commands --> subparsers
    subparsers --> individual_parsers
    
    preprocess_argv --> parse_args
    parse_args --> handler
    handler --> take_action
```

| Command Name | Class | Purpose |
|-------------|-------|---------|
| `create-study` | `_CreateStudy` | Create a new optimization study |
| `delete-study` | `_DeleteStudy` | Delete an existing study |
| `study set-user-attr` | `_StudySetUserAttribute` | Set user attributes on a study |
| `study-names` | `_StudyNames` | List all study names |
| `studies` | `_Studies` | Show detailed study information |
| `trials` | `_Trials` | Show trial information for a study |
| `best-trial` | `_BestTrial` | Show the best trial for a study |
| `best-trials` | `_BestTrials` | Show Pareto-optimal trials |
| `storage upgrade` | `_StorageUpgrade` | Upgrade RDB storage schema |
| `ask` | `_Ask` | Create a trial and suggest parameters |
| `tell` | `_Tell` | Complete a trial with objective values |

Sources: [optuna/cli.py:814-826](), [optuna/cli.py:893-914]()

## Storage Integration

The CLI integrates with Optuna's storage system through the `_get_storage()` function, which automatically detects the appropriate storage backend based on the provided URL or explicit storage class specification.

### Storage Backend Selection

```mermaid
graph TD
    subgraph "Storage URL Processing"
        check_storage_url["_check_storage_url()"]
        env_var["OPTUNA_STORAGE env var"]
        storage_arg["--storage argument"]
    end
    
    subgraph "Storage Class Detection"
        get_storage["_get_storage()"]
        explicit_class["--storage-class argument"]
        auto_detect["Automatic Detection"]
    end
    
    subgraph "Storage Backends"
        RDBStorage_impl["RDBStorage"]
        JournalFileBackend_impl["JournalFileBackend"]
        JournalRedisBackend_impl["JournalRedisBackend"]
        JournalStorage_impl["JournalStorage"]
    end
    
    storage_arg --> check_storage_url
    env_var --> check_storage_url
    check_storage_url --> get_storage
    
    explicit_class --> get_storage
    auto_detect --> get_storage
    
    get_storage --> RDBStorage_impl
    get_storage --> JournalFileBackend_impl
    get_storage --> JournalRedisBackend_impl
    get_storage --> JournalStorage_impl
    
    JournalFileBackend_impl --> JournalStorage_impl
    JournalRedisBackend_impl --> JournalStorage_impl
```

The storage selection logic follows this priority order:
1. Use `--storage` command line argument if provided
2. Fall back to `OPTUNA_STORAGE` environment variable
3. Auto-detect storage type based on URL format:
   - URLs starting with `redis://` use `JournalRedisBackend`
   - Existing file paths use `JournalFileBackend`
   - Database URLs use `RDBStorage`

Sources: [optuna/cli.py:42-80](), [optuna/cli.py:846-861]()

## Output Formatting System

The CLI supports multiple output formats through a unified formatting system that converts internal data structures to user-friendly representations.

### Output Format Pipeline

```mermaid
graph TB
    subgraph "Data Processing"
        create_records["_dataframe._create_records_and_aggregate_column()"]
        raw_data["Raw Trial/Study Data"]
        records["List of Records"]
        columns["Column Definitions"]
    end
    
    subgraph "Format Conversion"
        format_output["_format_output()"]
        convert_to_dict["_convert_to_dict()"]
        format_value["_format_value()"]
    end
    
    subgraph "Output Renderers"
        dump_value["_dump_value()"]
        dump_table["_dump_table()"]
        json_dumps["json.dumps()"]
        yaml_dump["yaml.safe_dump()"]
    end
    
    subgraph "Output Formats"
        value_format["value format"]
        table_format["table format"]
        json_format["json format"]
        yaml_format["yaml format"]
    end
    
    raw_data --> create_records
    create_records --> records
    create_records --> columns
    
    records --> format_output
    columns --> format_output
    format_output --> convert_to_dict
    convert_to_dict --> format_value
    
    format_output --> dump_value
    format_output --> dump_table
    format_output --> json_dumps
    format_output --> yaml_dump
    
    dump_value --> value_format
    dump_table --> table_format
    json_dumps --> json_format
    yaml_dump --> yaml_format
```

| Format | Description | Use Case | Single Record | Multiple Records |
|--------|-------------|----------|---------------|------------------|
| `value` | Space-separated values | Script processing, pipes | Single line | Multiple lines |
| `table` | ASCII table with borders | Human-readable console output | Single row + headers | Multiple rows |
| `json` | JSON object/array | API integration | Object `{}` | Array `[{}, {}]` |
| `yaml` | YAML document | Configuration files | Single document | List document |

The formatting system handles datetime objects using the format `"%Y-%m-%d %H:%M:%S"` and converts complex types to strings for serialization compatibility.

Sources: [optuna/cli.py:244-271](), [optuna/cli.py:191-241](), [optuna/cli.py:39](), [tests/test_cli.py:64-99]()

## Core Commands

### Study Management Commands

The CLI provides comprehensive study lifecycle management through dedicated commands for creation, deletion, and attribute management.

#### Create Study Command

The `_CreateStudy` command creates new optimization studies with configurable directions and names.

```mermaid
graph LR
    subgraph "Create Study Flow"
        args["Command Arguments"]
        validate["Argument Validation"]
        storage["Get Storage"]
        create["optuna.create_study()"]
        output["Print Study Name"]
    end
    
    args --> validate
    validate --> storage
    storage --> create
    create --> output
    
    subgraph "Arguments"
        study_name["--study-name"]
        direction["--direction"]
        directions["--directions"]
        skip_exists["--skip-if-exists"]
    end
    
    study_name --> validate
    direction --> validate
    directions --> validate
    skip_exists --> validate
```

Key features:
- Supports single-objective (`--direction`) and multi-objective (`--directions`) optimization
- Optional study naming with `--study-name`
- Duplicate handling with `--skip-if-exists`
- Returns the created study name for use in subsequent commands

Sources: [optuna/cli.py:307-353]()

#### Delete Study Command

The `_DeleteStudy` command permanently removes studies from storage.

```python
# Example usage
optuna delete-study --storage sqlite:///example.db --study-name my-study
```

Sources: [optuna/cli.py:355-366]()

### Trial Management Commands

#### Ask Command

The `_Ask` command creates new trials and suggests parameter values, supporting the ask-and-tell optimization pattern. This command is marked as experimental.

```mermaid
graph TB
    subgraph "Ask Command Flow"
        load_study["optuna.load_study()"]
        parse_search_space["Parse --search-space JSON"]
        create_sampler["Create Sampler (optional)"]
        ask_trial["study.ask()"]
        format_params["Format Parameters"]
        output_result["Output Trial Info"]
    end
    
    subgraph "Input Processing"
        sampler_spec["--sampler"]
        sampler_kwargs["--sampler-kwargs"]
        search_space_json["--search-space JSON"]
        fixed_distributions["Fixed Distributions"]
    end
    
    load_study --> parse_search_space
    parse_search_space --> create_sampler
    create_sampler --> ask_trial
    ask_trial --> format_params
    format_params --> output_result
    
    sampler_spec --> create_sampler
    sampler_kwargs --> create_sampler
    search_space_json --> fixed_distributions
    fixed_distributions --> ask_trial
```

The search space parameter accepts JSON-serialized distribution specifications:
```json
{
  "x": {
    "name": "FloatDistribution", 
    "attributes": {"low": 0.0, "high": 1.0}
  },
  "y": {
    "name": "CategoricalDistribution",
    "attributes": {"choices": ["A", "B", "C"]}
  }
}
```

**Note:** The `ask` command requires that a study be created beforehand using `create-study`. Implicit study creation was removed in Optuna v4.0.0.

**Example workflow:**
```bash
# Create study
optuna create-study --storage sqlite:///example.db --study-name opt-study

# Ask for parameters (creates trial)
optuna ask --storage sqlite:///example.db --study-name opt-study \
  --search-space '{"x": {"name": "FloatDistribution", "attributes": {"low": 0.0, "high": 1.0}}}'

# Output: {"number": 0, "params": {"x": 0.42}}
```

The `--sampler` argument accepts any sampler class name from `optuna.samplers` (e.g., `TPESampler`, `RandomSampler`), and `--sampler-kwargs` provides initialization arguments as JSON.

Sources: [optuna/cli.py:655-758](), [optuna/cli.py:689-757](), [tests/test_cli.py:1143-1197]()

#### Tell Command

The `_Tell` command completes trials by providing objective values and final states. This command is marked as experimental.

```mermaid
graph LR
    subgraph "Tell Command Flow"
        load_study["optuna.load_study()"]
        parse_values["Parse --values"]
        parse_state["Parse --state"]
        tell_trial["study.tell()"]
        log_result["Log Completion"]
    end
    
    subgraph "Input Parameters"
        trial_number["--trial-number"]
        values["--values (list)"]
        state["--state (complete/pruned/fail)"]
        skip_finished["--skip-if-finished"]
    end
    
    load_study --> parse_values
    parse_values --> parse_state
    parse_state --> tell_trial
    tell_trial --> log_result
    
    trial_number --> tell_trial
    values --> parse_values
    state --> parse_state
    skip_finished --> tell_trial
```

**Example workflow:**
```bash
# Complete trial with objective value
optuna tell --storage sqlite:///example.db --study-name opt-study \
  --trial-number 0 --values 0.25

# Mark trial as failed
optuna tell --storage sqlite:///example.db --study-name opt-study \
  --trial-number 1 --state fail

# Skip already finished trials
optuna tell --storage sqlite:///example.db --study-name opt-study \
  --trial-number 0 --values 0.30 --skip-if-finished
```

For multi-objective optimization, multiple values can be provided: `--values 0.25 0.50`. When `--state` is omitted, the trial is marked as `COMPLETE`. The `--skip-if-finished` flag prevents errors when attempting to update already-completed trials.

Sources: [optuna/cli.py:760-812](), [tests/test_cli.py:1446-1527]()

#### Ask-Tell Workflow Example

Complete example of distributed optimization using the ask-tell pattern:

```bash
# 1. Create the study once
optuna create-study --storage sqlite:///distributed.db --study-name dist-opt

# 2. Worker 1: Ask for parameters
TRIAL_1=$(optuna ask --storage sqlite:///distributed.db --study-name dist-opt \
  --search-space '{"x": {"name": "FloatDistribution", "attributes": {"low": -10, "high": 10}}}' \
  --format json)

# 3. Worker 1: Evaluate objective function
PARAMS=$(echo $TRIAL_1 | jq -r '.params.x')
VALUE=$(python evaluate.py $PARAMS)  # Your evaluation script

# 4. Worker 1: Report results
TRIAL_NUM=$(echo $TRIAL_1 | jq -r '.number')
optuna tell --storage sqlite:///distributed.db --study-name dist-opt \
  --trial-number $TRIAL_NUM --values $VALUE

# 5. Worker 2 can run steps 2-4 in parallel
```

Sources: [optuna/cli.py:655-812]()

### Query Commands

#### Studies Command

The `_Studies` command provides comprehensive study information including metadata, trial counts, and user attributes.

Output columns:
- `name`: Study name
- `direction`: Optimization direction(s) as tuple
- `n_trials`: Number of completed trials
- `datetime_start`: Study creation timestamp
- `user_attrs`: User-defined attributes (if any exist)

**Example usage:**
```bash
# Default table format
optuna studies --storage sqlite:///example.db

# JSON output for multi-objective studies
optuna studies --storage sqlite:///example.db --format json

# Flatten nested columns like directions
optuna studies --storage sqlite:///example.db --flatten
```

The `--flatten` option converts nested structures (like `direction` tuples and `user_attrs` dicts) into separate columns. For example, a multi-objective study with directions `["minimize", "maximize"]` produces columns `direction_0` and `direction_1`.

Sources: [optuna/cli.py:415-468](), [tests/test_cli.py:375-439](), [tests/test_cli.py:442-529]()

#### Trials Command

The `_Trials` command displays detailed trial information for a specific study, including parameters, values, and execution metadata. This command is marked as experimental.

**Standard output attributes:**
- `number`: Trial number
- `value` / `values`: Objective value(s) for single/multi-objective
- `datetime_start`: Trial start time
- `datetime_complete`: Trial completion time
- `duration`: Execution duration
- `params`: Parameter values (nested dict)
- `user_attrs`: User attributes (nested dict)
- `state`: Trial state (COMPLETE, PRUNED, FAIL, RUNNING)

**Example usage:**
```bash
# Default table format
optuna trials --storage sqlite:///example.db --study-name my-study

# JSON format for programmatic access
optuna trials --storage sqlite:///example.db --study-name my-study --format json

# Flattened output with separate columns for each parameter
optuna trials --storage sqlite:///example.db --study-name my-study --flatten --format yaml
```

The `--flatten` option is particularly useful for studies with branched search spaces, converting `params` dict into individual columns like `params_x`, `params_y`. Missing parameters (e.g., from conditional branches) appear as empty strings in table/value formats or are omitted in JSON/YAML formats.

Sources: [optuna/cli.py:470-518](), [tests/test_cli.py:531-607](), [tests/test_cli.py:609-683]()

#### Best Trial Commands

Optuna provides two commands for retrieving optimal trials:

**`best-trial` Command** - Returns the single best trial for single-objective optimization:

```bash
optuna best-trial --storage sqlite:///example.db --study-name my-study --format json
```

This command outputs the trial with the optimal objective value according to the study direction (minimize or maximize). For multi-objective studies, it raises an error.

**`best-trials` Command** - Returns Pareto-optimal trials for multi-objective optimization:

```bash
optuna best-trials --storage sqlite:///example.db --study-name pareto-study --format table
```

This command outputs all trials on the Pareto front, sorted by their dominance relationships. For single-objective studies, it returns only the single best trial.

Both commands support the same output formats and `--flatten` option as the `trials` command.

Sources: [optuna/cli.py:520-571](), [optuna/cli.py:573-623](), [tests/test_cli.py:685-764](), [tests/test_cli.py:842-925]()

## Storage Operations

### Storage Upgrade Command

The `_StorageUpgrade` command handles RDB storage schema migrations to ensure compatibility with newer Optuna versions.

```mermaid
graph TB
    subgraph "Upgrade Process"
        create_storage["Create RDBStorage"]
        get_versions["Get Current/Head Versions"]
        check_compatibility["Check Version Compatibility"]
        upgrade["storage.upgrade()"]
        complete["Log Completion"]
    end
    
    subgraph "Version States"
        up_to_date["Up-to-date"]
        needs_upgrade["Needs Upgrade"]
        outdated_client["Outdated Client"]
    end
    
    create_storage --> get_versions
    get_versions --> check_compatibility
    check_compatibility --> up_to_date
    check_compatibility --> needs_upgrade
    check_compatibility --> outdated_client
    
    needs_upgrade --> upgrade
    upgrade --> complete
```

Sources: [optuna/cli.py:625-653]()

## Common Arguments and Configuration

All CLI commands share common arguments for storage configuration, logging, and debugging:

| Argument | Purpose | Default | Example |
|----------|---------|---------|---------|
| `--storage` | Storage URL or path | From `OPTUNA_STORAGE` env var | `sqlite:///db.sqlite3` |
| `--storage-class` | Explicit storage backend hint | Auto-detected | `JournalFileBackend` |
| `--verbose` / `-v` | Increase logging verbosity (repeatable) | INFO level | `-vv` for DEBUG |
| `--quiet` / `-q` | Reduce logging to warnings/errors | - | `-q` |
| `--log-file` | Write logs to file | stderr only | `--log-file optuna.log` |
| `--debug` | Show full tracebacks on errors | False | `--debug` |

### Environment Variables

The `OPTUNA_STORAGE` environment variable provides a convenient way to avoid repeating the `--storage` argument:

```bash
# Set environment variable
export OPTUNA_STORAGE=sqlite:///~/optuna-studies.db

# Commands automatically use the environment storage
optuna create-study --study-name experiment-1
optuna ask --study-name experiment-1
```

**Note:** Specifying storage via `OPTUNA_STORAGE` is marked as an experimental feature and may change in future versions.

### Accepted Storage Classes

The `--storage-class` argument accepts these values:
- `RDBStorage` - For SQL database URLs
- `JournalFileBackend` - For file-based journal storage
- `JournalRedisBackend` - For Redis-based journal storage

Deprecated aliases `JournalFileStorage` and `JournalRedisStorage` are still accepted but not recommended.

Sources: [optuna/cli.py:846-891](), [optuna/cli.py:947-977](), [optuna/cli.py:42-55](), [optuna/cli.py:829-844]()

## Error Handling and Validation

The CLI implements comprehensive error handling through the `CLIUsageError` exception class and input validation functions. Storage URL validation supports environment variable fallback and provides clear error messages for configuration issues.

```python
# Storage URL validation with environment fallback
def _check_storage_url(storage_url: str | None) -> str:
    if storage_url is not None:
        return storage_url
    
    env_storage = os.environ.get("OPTUNA_STORAGE")
    if env_storage is not None:
        return env_storage
    raise CLIUsageError("Storage URL is not specified.")
```

Sources: [optuna/cli.py:42-55](), [optuna/cli.py:992-1008]()

---

# Page: Visualization and Dashboard

# Visualization and Dashboard

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [pyproject.toml](pyproject.toml)

</details>



## Purpose and Scope

This document covers Optuna's visualization capabilities and dashboard system. It explains:

- The visualization module (`optuna.visualization`) and its plotting backends (Plotly and Matplotlib)
- Available visualization functions for analyzing optimization results
- The optuna-dashboard system for interactive study monitoring
- Integration points with experiment tracking tools

For information about the command-line interface for study management, see [Command-Line Interface](#5.1). For integration with external experiment tracking systems like MLflow and Weights & Biases, see [ML Framework Integrations](#4.2).

---

## Visualization Architecture

Optuna provides two complementary approaches to visualization:

1. **Static Plotting API** (`optuna.visualization`): Programmatic generation of plots within Python scripts or notebooks
2. **Interactive Dashboard** (`optuna-dashboard`): Real-time web-based monitoring as a separate package

### Visualization Module Structure

```mermaid
graph TB
    subgraph "Core System"
        Study["Study"]
        Storage["BaseStorage"]
        Trial["FrozenTrial"]
    end
    
    subgraph "Visualization Module"
        VisAPI["optuna.visualization"]
        
        subgraph "Plot Functions"
            PlotOptHistory["plot_optimization_history()"]
            PlotParamImport["plot_param_importances()"]
            PlotSlice["plot_slice()"]
            PlotContour["plot_contour()"]
            PlotPareto["plot_pareto_front()"]
            PlotParallel["plot_parallel_coordinate()"]
            PlotEDF["plot_edf()"]
            PlotTimeline["plot_timeline()"]
        end
        
        subgraph "Backend Implementations"
            PlotlyBackend["optuna.visualization (Plotly)"]
            MatplotlibBackend["optuna.visualization.matplotlib"]
        end
    end
    
    subgraph "External Dashboard"
        OptunaDashboard["optuna-dashboard<br/>(Separate Package)"]
        DashboardWeb["Web UI<br/>Real-time Monitoring"]
    end
    
    subgraph "Dependencies"
        Plotly["plotly>=4.9.0"]
        Matplotlib["matplotlib!=3.6.0"]
        Kaleido["kaleido<0.4<br/>(Static Image Export)"]
    end
    
    Study --> VisAPI
    Storage --> VisAPI
    Trial --> VisAPI
    
    VisAPI --> PlotOptHistory
    VisAPI --> PlotParamImport
    VisAPI --> PlotSlice
    VisAPI --> PlotContour
    VisAPI --> PlotPareto
    VisAPI --> PlotParallel
    VisAPI --> PlotEDF
    VisAPI --> PlotTimeline
    
    PlotOptHistory --> PlotlyBackend
    PlotOptHistory --> MatplotlibBackend
    PlotParamImport --> PlotlyBackend
    PlotSlice --> PlotlyBackend
    PlotSlice --> MatplotlibBackend
    PlotContour --> PlotlyBackend
    PlotContour --> MatplotlibBackend
    
    PlotlyBackend --> Plotly
    MatplotlibBackend --> Matplotlib
    PlotlyBackend --> Kaleido
    
    Storage -.reads.-> OptunaDashboard
    OptunaDashboard --> DashboardWeb
```

**Visualization System Components**

The visualization system operates independently from the optimization loop, reading completed trial data from storage backends to generate analytical plots.

Sources: [pyproject.toml:1-193]()

---

## Plotting Backends

Optuna supports two plotting backends, each suited for different use cases:

### Backend Comparison

| Feature | Plotly Backend | Matplotlib Backend |
|---------|---------------|-------------------|
| **Module Path** | `optuna.visualization` | `optuna.visualization.matplotlib` |
| **Interactivity** | Interactive (HTML/JavaScript) | Static images |
| **Output Format** | HTML, PNG (via kaleido) | PNG, PDF, SVG |
| **Jupyter Support** | Native inline display | Native inline display |
| **Dependencies** | plotly>=4.9.0, kaleido<0.4 | matplotlib!=3.6.0 |
| **Primary Use Case** | Exploratory analysis, notebooks | Publication figures, reports |
| **Function Coverage** | Complete | Subset (core plots) |

### Dependency Configuration

```mermaid
graph LR
    subgraph "Optional Dependencies"
        OptionalGroup["[optional]"]
        
        OptionalGroup --> PlotlyDep["plotly>=4.9.0"]
        OptionalGroup --> MatplotlibDep["matplotlib!=3.6.0"]
    end
    
    subgraph "Documentation/Testing"
        DocGroup["[document]"]
        TestGroup["[test]"]
        
        DocGroup --> PlotlyDoc["plotly>=4.9.0"]
        DocGroup --> MatplotlibDoc["matplotlib!=3.6.0"]
        DocGroup --> KaleidoDoc["kaleido<0.4"]
        
        TestGroup --> KaleidoTest["kaleido<0.4"]
    end
    
    subgraph "Visualization Functions"
        PlotFuncs["Plotting Functions"]
    end
    
    PlotlyDep -.optional.-> PlotFuncs
    MatplotlibDep -.optional.-> PlotFuncs
    KaleidoDoc -.export.-> PlotFuncs
```

**Installation Patterns**

- **Default Installation**: Visualization dependencies are not included
- **With Visualization**: `pip install "optuna[optional]"` installs both backends
- **Documentation Build**: Includes kaleido for static image generation
- **Matplotlib Version Constraint**: Version 3.6.0 is excluded due to compatibility issues

Sources: [pyproject.toml:75-89](), [pyproject.toml:56-74](), [pyproject.toml:90-101]()

---

## Visualization Functions

The visualization module provides functions for analyzing different aspects of optimization studies. Each function accepts a `Study` object and returns a plot object.

### Core Visualization Functions

```mermaid
graph TB
    subgraph "Study Analysis"
        Study["Study Object"]
    end
    
    subgraph "Single-Objective Plots"
        OptHistory["plot_optimization_history()<br/>Value progression over trials"]
        ParamImportances["plot_param_importances()<br/>Feature importance analysis"]
        Slice["plot_slice()<br/>Parameter vs objective"]
        Contour["plot_contour()<br/>2D parameter interaction"]
        Parallel["plot_parallel_coordinate()<br/>High-dimensional parameter space"]
        EDF["plot_edf()<br/>Empirical Distribution Function"]
        Timeline["plot_timeline()<br/>Trial execution timeline"]
    end
    
    subgraph "Multi-Objective Plots"
        ParetoFront["plot_pareto_front()<br/>Objective trade-offs"]
    end
    
    subgraph "Analysis Outputs"
        Insights["Study Insights:<br/>- Convergence behavior<br/>- Parameter sensitivity<br/>- Search space coverage<br/>- Trial performance"]
    end
    
    Study --> OptHistory
    Study --> ParamImportances
    Study --> Slice
    Study --> Contour
    Study --> Parallel
    Study --> EDF
    Study --> Timeline
    Study --> ParetoFront
    
    OptHistory --> Insights
    ParamImportances --> Insights
    Slice --> Insights
    Contour --> Insights
    Parallel --> Insights
    ParetoFront --> Insights
```

### Visualization Function Categories

| Category | Functions | Purpose |
|----------|-----------|---------|
| **Convergence** | `plot_optimization_history()` | Track objective value improvements over time |
| **Parameter Analysis** | `plot_param_importances()`<br/>`plot_slice()`<br/>`plot_contour()` | Understand parameter influence and interactions |
| **Search Space** | `plot_parallel_coordinate()`<br/>`plot_slice()` | Visualize search space exploration |
| **Multi-Objective** | `plot_pareto_front()` | Analyze objective trade-offs |
| **Distribution** | `plot_edf()` | Compare empirical distributions across studies |
| **Execution** | `plot_timeline()` | Analyze trial timing and parallelism |

### Backend Selection Pattern

```mermaid
graph LR
    UserCode["User Code"]
    
    subgraph "Plotly Backend (Default)"
        PlotlyImport["from optuna.visualization import plot_*"]
        PlotlyFunc["Returns plotly.graph_objects.Figure"]
    end
    
    subgraph "Matplotlib Backend"
        MatplotlibImport["from optuna.visualization.matplotlib import plot_*"]
        MatplotlibFunc["Returns matplotlib.axes.Axes"]
    end
    
    UserCode --> PlotlyImport
    UserCode --> MatplotlibImport
    
    PlotlyFunc --> PlotlyDisplay["fig.show() or fig.write_html()"]
    MatplotlibFunc --> MatplotlibDisplay["plt.show() or fig.savefig()"]
```

**Import Strategy**

- Plotly backend functions are available directly from `optuna.visualization`
- Matplotlib backend functions are namespaced under `optuna.visualization.matplotlib`
- Both backends provide the same function names with identical signatures
- Backend choice depends on visualization requirements (interactive vs. static)

Sources: [pyproject.toml:75-89]()

---

## Dashboard System

The Optuna Dashboard is a separate web application that provides real-time monitoring of optimization studies. Unlike the static plotting API, the dashboard offers interactive exploration and live updates.

### Dashboard Architecture

```mermaid
graph TB
    subgraph "Optuna Core"
        RDBStorage["RDBStorage<br/>MySQL/PostgreSQL/SQLite"]
        InMemoryStorage["InMemoryStorage"]
        JournalStorage["JournalStorage"]
    end
    
    subgraph "Dashboard Package (Separate)"
        DashboardApp["optuna-dashboard<br/>(External Package)"]
        
        subgraph "Dashboard Components"
            WebServer["Web Server<br/>HTTP API"]
            Frontend["React Frontend<br/>Interactive UI"]
            StorageReader["Storage Reader<br/>Reads BaseStorage"]
        end
        
        subgraph "UI Features"
            StudyList["Study List View"]
            TrialTable["Trial Table<br/>Filterable & Sortable"]
            LivePlots["Live Plots<br/>Auto-refresh"]
            ParamEditor["Hyperparameter Editor"]
            NoteSystem["Trial Notes/Tags"]
        end
    end
    
    subgraph "Access Methods"
        CLI["optuna-dashboard<br/>Command-line"]
        Python["Python API<br/>optuna_dashboard.run_server()"]
    end
    
    RDBStorage -.reads.-> StorageReader
    InMemoryStorage -.reads.-> StorageReader
    JournalStorage -.reads.-> StorageReader
    
    StorageReader --> WebServer
    WebServer --> Frontend
    
    Frontend --> StudyList
    Frontend --> TrialTable
    Frontend --> LivePlots
    Frontend --> ParamEditor
    Frontend --> NoteSystem
    
    CLI --> DashboardApp
    Python --> DashboardApp
```

**Dashboard Characteristics**

- **Separate Package**: Not bundled with core Optuna (`pip install optuna-dashboard`)
- **Storage Agnostic**: Reads from any `BaseStorage` implementation
- **Read-Only**: Does not modify study data (except notes/tags)
- **Multi-Study**: Can display multiple studies simultaneously
- **Real-Time**: Auto-refreshes to show ongoing optimization progress

### Dashboard vs Visualization API

| Aspect | Dashboard | Visualization API |
|--------|-----------|------------------|
| **Installation** | `pip install optuna-dashboard` | Included with `optuna[optional]` |
| **Interface** | Web browser | Python code |
| **Update Mode** | Real-time auto-refresh | On-demand generation |
| **Interactivity** | Full interactive UI | Plot-level interactivity |
| **Multi-Study** | Yes, built-in | Requires custom code |
| **Trial Editing** | Notes, tags, manual completion | Not supported |
| **Deployment** | Standalone server | Embedded in notebooks/scripts |

Sources: Based on architecture diagrams and common Optuna usage patterns

---

## Integration with Experiment Tracking

Visualization components integrate with external experiment tracking systems through the integration layer.

### Experiment Tracking Integration Flow

```mermaid
graph TB
    subgraph "Optimization Process"
        Study["Study.optimize()"]
        Callbacks["Study Callbacks"]
    end
    
    subgraph "Visualization Integration"
        MLflowCallback["MLflowCallback<br/>optuna.integration.mlflow"]
        WANDBCallback["WeightsAndBiasesCallback<br/>optuna.integration.wandb"]
        TensorBoardCallback["TensorBoardCallback<br/>optuna.integration.tensorboard"]
    end
    
    subgraph "External Platforms"
        MLflow["MLflow Tracking Server<br/>Logs plots + metrics"]
        WANDB["Weights & Biases<br/>Cloud/Self-hosted"]
        TensorBoard["TensorBoard<br/>Local/Remote"]
    end
    
    subgraph "Logged Artifacts"
        Plots["Optuna Plots<br/>(Generated via optuna.visualization)"]
        Metrics["Trial Metrics<br/>Parameters & Values"]
        Models["Model Artifacts<br/>(User-uploaded)"]
    end
    
    Study --> Callbacks
    
    Callbacks --> MLflowCallback
    Callbacks --> WANDBCallback
    Callbacks --> TensorBoardCallback
    
    MLflowCallback --> Plots
    WANDBCallback --> Plots
    
    Plots --> MLflow
    Plots --> WANDB
    Metrics --> MLflow
    Metrics --> WANDB
    Metrics --> TensorBoard
    
    Models --> MLflow
    Models --> WANDB
```

**Integration Patterns**

1. **MLflow Integration**: 
   - Logs optimization history plots automatically
   - Stores trial parameters and values as MLflow metrics
   - Requires `mlflow` package (lazy-loaded via `optuna.integration`)

2. **Weights & Biases Integration**:
   - Streams trial results to W&B dashboard
   - Generates and uploads Optuna plots
   - Supports custom visualization logging

3. **TensorBoard Integration**:
   - Logs scalar metrics (objectives, intermediate values)
   - Records hyperparameters for TensorBoard's HParams plugin
   - Does not include Optuna plot generation (different visualization paradigm)

### Visualization in Integration Callbacks

The integration callbacks leverage the visualization API to generate plots that are then uploaded to external platforms. This provides a unified visualization experience across different experiment tracking tools.

Sources: Based on architecture diagrams showing integration layer

---

## Visualization Dependencies and Build Configuration

### Development and Documentation Setup

```mermaid
graph TB
    subgraph "Development Dependencies"
        CheckingGroup["[checking] group"]
        DocumentGroup["[document] group"]
        TestGroup["[test] group"]
    end
    
    subgraph "Visualization Stack"
        Plotly["plotly>=4.9.0"]
        Matplotlib["matplotlib!=3.6.0"]
        Kaleido["kaleido<0.4"]
        Pandas["pandas"]
    end
    
    subgraph "Documentation Build"
        Sphinx["sphinx"]
        SphinxGallery["sphinx-gallery<br/>Executes tutorials"]
        TutorialPy["tutorial/**/*.py<br/>Visualization examples"]
    end
    
    subgraph "Tutorial Execution"
        TutorialExec["Tutorial Execution<br/>During doc build"]
        GeneratedPlots["Generated Plots<br/>Saved as artifacts"]
        CIArtifacts["CI Artifacts<br/>'tutorial' download"]
    end
    
    DocumentGroup --> Plotly
    DocumentGroup --> Matplotlib
    DocumentGroup --> Kaleido
    DocumentGroup --> Pandas
    DocumentGroup --> Sphinx
    DocumentGroup --> SphinxGallery
    
    TestGroup --> Kaleido
    
    SphinxGallery --> TutorialExec
    TutorialExec --> TutorialPy
    TutorialExec --> GeneratedPlots
    GeneratedPlots --> CIArtifacts
```

### Kaleido Version Constraint

The `kaleido<0.4` version constraint exists across multiple dependency groups due to browser installation requirements. The constraint note indicates this is temporary pending browser separation:

```
kaleido<0.4  # TODO(nzw0301): Remove the version constraint by installing browser separately.
```

This constraint appears in both the `[document]` and `[test]` groups to ensure consistent static image generation across documentation builds and test execution.

### Tutorial Execution and Caching

The documentation build system executes tutorial files that demonstrate visualization capabilities. To optimize build times:

1. **CI Artifact Caching**: Tutorial execution results are cached as CI artifacts
2. **Download Strategy**: Developers can download "tutorial" artifacts from CI
3. **Local Build Optimization**: Extracted artifacts in `docs/source/tutorial` prevent re-execution
4. **Python Version Matching**: Artifacts contain pickle files, requiring Python 3.12 match

This caching strategy is particularly important for visualization tutorials, which may involve expensive plot generation.

Sources: [pyproject.toml:56-74](), [pyproject.toml:90-101](), [CONTRIBUTING.md:113-123]()

---

## Visualization Testing Strategy

### Test Dependencies and Coverage

Visualization functionality is tested through the standard test suite with specific dependencies:

```mermaid
graph TB
    subgraph "Test Configuration"
        PytestConfig["pytest.ini_options<br/>pyproject.toml"]
        TestMarkers["slow marker<br/>For expensive plots"]
    end
    
    subgraph "Test Dependencies"
        TestGroup["[test] group"]
        Kaleido["kaleido<0.4<br/>Image generation"]
        Scipy["scipy>=1.9.2<br/>Statistical tests"]
    end
    
    subgraph "Test Execution"
        PytestRun["pytest"]
        ParallelExec["pytest -n 8<br/>Parallel execution"]
        SlowExclude["-m 'not slow'<br/>Skip expensive tests"]
    end
    
    subgraph "Test Categories"
        UnitTests["Unit Tests<br/>tests/**"]
        IntegrationTests["Integration Tests<br/>tests/integration_tests/**"]
        VisualizationTests["Visualization Tests<br/>Plot generation & validation"]
    end
    
    PytestConfig --> TestMarkers
    TestGroup --> Kaleido
    TestGroup --> Scipy
    
    PytestRun --> ParallelExec
    PytestRun --> SlowExclude
    
    ParallelExec --> UnitTests
    ParallelExec --> IntegrationTests
    ParallelExec --> VisualizationTests
```

**Test Strategy for Visualization**

- **Slow Test Marking**: Expensive plot generation tests are marked with `@pytest.mark.slow`
- **Selective Execution**: CI can skip slow tests for faster feedback (`-m "not slow"`)
- **Image Validation**: Kaleido enables static image generation for comparison testing
- **Backend Coverage**: Tests validate both Plotly and Matplotlib implementations

### Continuous Integration for Visualization

The CI/CD system validates visualization across multiple environments:

| Workflow | Purpose | Visualization Testing |
|----------|---------|----------------------|
| `tests.yml` | Ubuntu, Python 3.9-3.14 | Full visualization suite |
| `mac-tests.yml` | macOS, Python 3.12 | Cross-platform plot generation |
| `windows-tests.yml` | Windows, Python 3.12 | Platform-specific rendering |
| `tests-with-minimum-versions.yml` | Minimum dependency versions | Ensures `plotly>=4.9.0` compatibility |

Sources: [pyproject.toml:167-172](), [pyproject.toml:90-101]()

---

## Summary

Optuna's visualization system provides a comprehensive approach to optimization analysis through two complementary components:

1. **Visualization API**: Programmatic plot generation with dual backend support (Plotly for interactivity, Matplotlib for publication-quality figures)
2. **Dashboard**: Real-time web-based monitoring as a separate package, enabling live study inspection

The visualization layer is designed as an optional component with minimal dependencies on the core optimization engine. It reads completed trial data from storage backends and generates analytical views without affecting the optimization process. Integration with experiment tracking platforms (MLflow, W&B, TensorBoard) extends visualization capabilities to external monitoring systems.

Key architectural decisions include:
- Optional installation to avoid dependency bloat
- Backend abstraction for flexibility (Plotly vs. Matplotlib)
- Storage-agnostic design for compatibility with all backends
- Separation of dashboard as independent package for deployment flexibility

---

# Page: Development and Deployment

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/dockerimage.yml](.github/workflows/dockerimage.yml)
- [.github/workflows/mac-tests.yml](.github/workflows/mac-tests.yml)
- [.github/workflows/matplotlib-tests.yml](.github/workflows/matplotlib-tests.yml)
- [.github/workflows/tests-storage.yml](.github/workflows/tests-storage.yml)
- [.github/workflows/tests-with-minimum-versions.yml](.github/workflows/tests-with-minimum-versions.yml)
- [.github/workflows/tests.yml](.github/workflows/tests.yml)
- [.github/workflows/windows-tests.yml](.github/workflows/windows-tests.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [Dockerfile](Dockerfile)
- [pyproject.toml](pyproject.toml)

</details>



This document provides an overview of Optuna's development infrastructure, including project configuration, testing systems, CI/CD pipelines, and deployment processes. It is intended for developers contributing to Optuna or maintaining the project's build and release systems.

For detailed information about:
- Project configuration files and dependency management, see [Project Configuration and Dependencies](#6.1)
- Testing frameworks and CI/CD workflow details, see [Testing and CI/CD Infrastructure](#6.2)
- Contribution process and local development setup, see [Development Workflow and Contribution Guide](#6.3)

## Development Infrastructure Overview

Optuna's development infrastructure is centered around `pyproject.toml`, which serves as the single source of configuration for all development tools. The project uses modern Python development practices with automated testing, code quality enforcement, and multi-platform validation.

```mermaid
graph TB
    subgraph "Configuration Hub"
        pyproject["pyproject.toml<br/>Central configuration file"]
    end
    
    subgraph "Code Quality Tools"
        ruff["Ruff<br/>Linter & Formatter<br/>ruff check/format"]
        mypy["MyPy<br/>Type checker<br/>mypy ."]
        precommit[".pre-commit-config.yaml<br/>Pre-commit hooks"]
    end
    
    subgraph "Testing Framework"
        pytest["pytest<br/>Test runner"]
        testdir["tests/<br/>Test suite"]
        markers["Test markers<br/>slow, etc."]
    end
    
    subgraph "CI/CD Workflows"
        maintest[".github/workflows/tests.yml<br/>Ubuntu + Python 3.9-3.14"]
        mactest[".github/workflows/mac-tests.yml<br/>macOS validation"]
        wintest[".github/workflows/windows-tests.yml<br/>Windows validation"]
        storage[".github/workflows/tests-storage.yml<br/>MySQL, PostgreSQL, Redis"]
        minver[".github/workflows/tests-with-minimum-versions.yml<br/>Backward compatibility"]
        docker[".github/workflows/dockerimage.yml<br/>Docker build & push"]
        matplotlib[".github/workflows/matplotlib-tests.yml<br/>Visualization tests"]
    end
    
    subgraph "Build Artifacts"
        dockerhub["Docker Hub<br/>optuna/optuna:*"]
        pypi["PyPI<br/>pip install optuna"]
    end
    
    pyproject --> ruff
    pyproject --> mypy
    pyproject --> pytest
    pyproject --> maintest
    
    precommit --> ruff
    precommit --> mypy
    
    pytest --> testdir
    pytest --> markers
    
    maintest --> testdir
    mactest --> testdir
    wintest --> testdir
    storage --> testdir
    minver --> testdir
    
    docker --> dockerhub
    maintest -.->|on release| pypi
    
    style pyproject fill:#f9f9f9,stroke:#333,stroke-width:2px
    style maintest fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [pyproject.toml](), [.pre-commit-config.yaml](), [.github/workflows/tests.yml](), [.github/workflows/mac-tests.yml](), [.github/workflows/windows-tests.yml](), [.github/workflows/tests-storage.yml](), [.github/workflows/tests-with-minimum-versions.yml](), [.github/workflows/dockerimage.yml]()

## CI/CD Pipeline Architecture

The CI/CD system validates code changes across multiple dimensions: Python versions, operating systems, database backends, and dependency versions. Each workflow has specific triggers and responsibilities.

```mermaid
graph LR
    subgraph "Triggers"
        push["git push to master"]
        pr["Pull Request"]
        schedule["Cron: 0 23 * * SUN-THU"]
        release["GitHub Release"]
    end
    
    subgraph "Primary Workflows"
        tests["tests.yml<br/>Ubuntu<br/>Python 3.9, 3.13, 3.14<br/>+ Redis service"]
        mac["mac-tests.yml<br/>macOS<br/>Python 3.12"]
        windows["windows-tests.yml<br/>Windows<br/>Python 3.12"]
    end
    
    subgraph "Specialized Workflows"
        storage["tests-storage.yml<br/>MySQL, PostgreSQL, Redis<br/>Python 3.9, 3.13, 3.14"]
        minver["tests-with-minimum-versions.yml<br/>alembic==1.5.0<br/>sqlalchemy==1.4.2<br/>Python 3.9"]
        viz["matplotlib-tests.yml<br/>Visualization without Plotly"]
    end
    
    subgraph "Build & Deploy"
        docker["dockerimage.yml<br/>Build: py3.9-3.12<br/>Variants: dev, prod"]
    end
    
    subgraph "Test Execution"
        pytest_full["pytest tests -n 8"]
        pytest_fast["pytest tests -m 'not slow' -n 8"]
    end
    
    push --> tests
    push --> mac
    push --> windows
    push --> storage
    push --> minver
    push --> docker
    
    pr --> tests
    pr --> mac
    pr --> windows
    pr --> storage
    pr --> minver
    pr -.path filter.-> viz
    pr -.path filter.-> docker
    
    schedule --> tests
    schedule --> mac
    schedule --> windows
    schedule --> storage
    schedule --> minver
    
    release --> docker
    
    tests --> pytest_fast
    schedule --> pytest_full
    
    docker --> dockerhub["Docker Hub<br/>optuna/optuna:TAG"]
```

**Sources:** [.github/workflows/tests.yml:1-98](), [.github/workflows/mac-tests.yml:1-72](), [.github/workflows/windows-tests.yml:1-85](), [.github/workflows/tests-storage.yml:1-148](), [.github/workflows/tests-with-minimum-versions.yml:1-97](), [.github/workflows/dockerimage.yml:1-80](), [.github/workflows/matplotlib-tests.yml:1-63]()

### Workflow Concurrency Control

All workflows implement concurrency control to prevent resource conflicts and unnecessary compute usage:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref == 'refs/heads/master' && github.run_number || github.ref }}
  cancel-in-progress: true
```

This configuration ensures that only one workflow run per branch is active at a time. For the `master` branch, each push gets a unique run number, while feature branches use the branch name as the concurrency key.

**Sources:** [.github/workflows/tests.yml:12-14](), [.github/workflows/mac-tests.yml:15-17]()

## Tool Configuration in pyproject.toml

The `pyproject.toml` file centralizes all tool configurations, eliminating the need for separate configuration files for each development tool.

### Build System Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `build-backend` | `setuptools.build_meta` | Uses setuptools for package building |
| `requires-python` | `>=3.9` | Minimum Python version requirement |
| `dynamic` | `["version"]` | Version read from `optuna.version.__version__` |

**Sources:** [pyproject.toml:1-3](), [pyproject.toml:32](), [pyproject.toml:120-121]()

### Dependency Groups

The project defines multiple optional dependency groups for different use cases:

| Group | Purpose | Key Dependencies |
|-------|---------|------------------|
| Core | Runtime dependencies | `alembic>=1.5.0`, `sqlalchemy>=1.4.2`, `numpy`, `tqdm` |
| `test` | Testing infrastructure | `pytest`, `pytest-xdist`, `fakeredis`, `moto` |
| `optional` | Optional features | `cmaes>=0.12.0`, `plotly>=4.9.0`, `scikit-learn>=0.24.2`, `scipy`, `torch` |
| `checking` | Code quality | `mypy`, `ruff`, `types-*` packages |
| `document` | Documentation build | `sphinx`, `sphinx-gallery`, `sphinx_rtd_theme>=1.2.0` |
| `benchmark` | Performance testing | `asv>=0.5.0`, `cma`, `virtualenv` |

**Sources:** [pyproject.toml:33-106]()

### Ruff Configuration

Ruff serves as both linter and formatter, configured in `[tool.ruff]`:

```toml
line-length = 99
target-version = "py39"
exclude = [".venv", "build", "dist", "docs", ".asv", "optuna/storages/_grpc/auto_generated"]

[tool.ruff.lint]
select = ["E", "W", "F", "I"]  # pycodestyle errors/warnings, pyflakes, isort

[tool.ruff.lint.isort]
known-first-party = ["optuna", "tests", "docs", "benchmarks"]
lines-after-imports = 2
force-single-line = true
```

Special exclusions prevent formatting of tutorial files and specific test files that have custom formatting requirements.

**Sources:** [pyproject.toml:131-183]()

### MyPy Type Checking Configuration

MyPy is configured with strict type checking enabled:

```toml
[tool.mypy]
warn_unused_configs = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
strict_equality = true
extra_checks = true
no_implicit_reexport = true
ignore_missing_imports = true
```

The configuration excludes auto-generated code directories like `optuna/storages/_grpc/auto_generated` and Alembic migration files.

**Sources:** [pyproject.toml:192-210]()

### Pytest Configuration

Test execution is configured with markers for test categorization:

```toml
[tool.pytest.ini_options]
addopts = "--color=yes"
filterwarnings = 'ignore::optuna.exceptions.ExperimentalWarning'
markers = [
  "slow: marks tests as slow (deselect with '-m \"not slow\"')"
]
```

The `slow` marker enables selective test execution: pull requests run `pytest -m "not slow"` for fast feedback, while scheduled builds run the full suite.

**Sources:** [pyproject.toml:185-190]()

## Docker Build System

The Docker build system creates multi-version images for both development and production use.

### Dockerfile Structure

The `Dockerfile` supports two build types controlled by the `BUILD_TYPE` argument:

```dockerfile
ARG PYTHON_VERSION=3.9
ARG BUILD_TYPE='dev'

RUN if [ "${BUILD_TYPE}" = "dev" ]; then \
        pip install ${PIP_OPTIONS} -e '.[benchmark, checking, document, optional, test]'; \
    else \
        pip install ${PIP_OPTIONS} -e .; \
    fi
```

The development variant includes all optional dependencies, while the production variant installs only core dependencies.

**Sources:** [Dockerfile:1-28]()

### Docker Image Tags

The `dockerimage.yml` workflow builds images for multiple Python versions with the following tag scheme:

| Event | Tag Format | Example |
|-------|-----------|---------|
| Master push | `py{VERSION}` or `py{VERSION}-dev` | `optuna/optuna:py3.12-dev` |
| Release | `{RELEASE}-py{VERSION}` or `{RELEASE}-py{VERSION}-dev` | `optuna/optuna:v3.5.0-py3.12` |

The matrix strategy builds for Python 3.9, 3.10, 3.11, and 3.12, with both standard and development variants.

**Sources:** [.github/workflows/dockerimage.yml:29-48]()

### Docker Build Caching

The workflow uses Docker BuildKit with caching to speed up builds:

```yaml
- name: Build the Docker image
  run: |
    if [ "${{ github.event_name }}" = 'release' ]; then
      CACHE_FROM=""  # No cache for releases
    else
      CACHE_FROM="--cache-from=${HUB_TAG}"
    fi
    docker build ${CACHE_FROM} . --build-arg PYTHON_VERSION=${{ matrix.python_version }}
  env:
    DOCKER_BUILDKIT: 1
```

Release builds skip caching to ensure clean builds with the version tag.

**Sources:** [.github/workflows/dockerimage.yml:50-61]()

## Pre-commit Hook System

The `.pre-commit-config.yaml` configures automated checks that run before commits are accepted.

```mermaid
graph LR
    commit["git commit"]
    
    subgraph "Pre-commit Hooks"
        ruff_check["ruff-check<br/>Linting with --fix"]
        ruff_format["ruff-format<br/>Code formatting"]
        mypy_check["mypy<br/>Type checking"]
    end
    
    subgraph "Check Results"
        pass["All checks pass<br/>Commit accepted"]
        fail["Check fails<br/>Commit blocked"]
    end
    
    commit --> ruff_check
    ruff_check --> ruff_format
    ruff_format --> mypy_check
    
    mypy_check --> pass
    mypy_check --> fail
    
    fail -.fix issues.-> commit
```

**Sources:** [.pre-commit-config.yaml:1-49]()

### Hook Configuration

The pre-commit system uses the following hook sequence:

1. **Ruff Check**: Runs `ruff-check` with automatic fixing enabled
2. **Ruff Format**: Applies code formatting rules
3. **MyPy**: Performs static type checking with strict settings

The MyPy hook includes all necessary type stub packages as `additional_dependencies` to ensure type checking works without requiring local installation of optional dependencies.

**Sources:** [.pre-commit-config.yaml:9-48]()

## Test Execution Strategy

The CI/CD system uses different test execution strategies based on the trigger type:

### Fast Tests (Pull Requests)

```bash
pytest tests -m "not slow" -n 8
```

This command:
- Excludes tests marked with `@pytest.mark.slow`
- Uses `pytest-xdist` with 8 parallel workers (`-n 8`)
- Provides fast feedback for pull requests (typically < 10 minutes)

**Sources:** [.github/workflows/tests.yml:86-95]()

### Full Tests (Scheduled/Manual)

```bash
pytest tests -n 8
```

Runs all tests including slow ones, executed:
- On scheduled runs (nightly, weekdays only)
- On manual workflow dispatch
- Ensures comprehensive validation before releases

**Sources:** [.github/workflows/tests.yml:88-95]()

### Platform-Specific Considerations

**Windows**: Requires special matplotlib backend configuration and NumPy version constraints:

```yaml
env:
  MPLBACKEND: "QtAgg"  # Use QtAgg as matplotlib backend
```

The workflow installs PyQt6 and constrains NumPy to `<2.0.0` due to PyTorch compatibility issues on Windows.

**Sources:** [.github/workflows/windows-tests.yml:54-61](), [.github/workflows/windows-tests.yml:77-84]()

## Database Backend Testing

The `tests-storage.yml` workflow validates Optuna's storage layer against multiple database systems using Docker services.

### Service Configuration

```mermaid
graph TB
    subgraph "GitHub Actions Services"
        mysql["mysql:8<br/>Port: 3306<br/>User: user<br/>Database: optunatest"]
        postgres["postgres:latest<br/>Port: 5432<br/>User: user<br/>Database: optunatest"]
        redis["redis:latest<br/>Port: 6379"]
    end
    
    subgraph "Test Executions"
        test_mysql["pytest test_with_server.py<br/>TEST_DB_URL=mysql+pymysql://..."]
        test_pg2["pytest test_with_server.py<br/>TEST_DB_URL=postgresql+psycopg2://..."]
        test_pg3["pytest test_with_server.py<br/>TEST_DB_URL=postgresql+psycopg://..."]
        test_redis["pytest test_with_server.py<br/>TEST_DB_URL=redis://...<br/>TEST_DB_MODE=journal-redis"]
    end
    
    mysql --> test_mysql
    postgres --> test_pg2
    postgres --> test_pg3
    redis --> test_redis
```

**Sources:** [.github/workflows/tests-storage.yml:37-69](), [.github/workflows/tests-storage.yml:119-147]()

### Database Driver Testing

The workflow tests multiple database drivers for PostgreSQL:
- **psycopg2**: Traditional driver (`postgresql+psycopg2://`)
- **psycopg**: Modern driver version 3 (`postgresql+psycopg://`)

This ensures compatibility with both driver versions that users might have installed.

**Sources:** [.github/workflows/tests-storage.yml:127-139]()

## Minimum Version Compatibility

The `tests-with-minimum-versions.yml` workflow validates backward compatibility by testing with the minimum allowed versions of all dependencies.

### Minimum Version Matrix

| Package | Minimum Version | Defined In |
|---------|----------------|------------|
| `alembic` | 1.5.0 | [pyproject.toml:34]() |
| `sqlalchemy` | 1.4.2 | [pyproject.toml:38]() |
| `packaging` | 20.0 | [pyproject.toml:37]() |
| `cmaes` | 0.12.0 | [pyproject.toml:63]() |
| `plotly` | 5.0.0 (optional) | [pyproject.toml:70]() |
| `scikit-learn` | 0.24.2 (optional) | [pyproject.toml:88]() |
| `tqdm` | 4.27.0 | Tested in workflow |

The workflow explicitly uninstalls and reinstalls packages at minimum versions to catch any unintentional use of newer APIs:

```yaml
- name: Install dependencies with minimum versions
  run: |
    pip uninstall -y alembic cmaes packaging sqlalchemy plotly scikit-learn
    pip install alembic==1.5.0 cmaes==0.12.0 packaging==20.0 sqlalchemy==1.4.2
```

**Sources:** [.github/workflows/tests-with-minimum-versions.yml:69-78]()

## Package Distribution

The `[project.scripts]` section in `pyproject.toml` defines the command-line entry point:

```toml
[project.scripts]
optuna = "optuna.cli:main"
```

This creates the `optuna` command that maps to the `main()` function in `optuna/cli.py`, providing CLI access to all Optuna commands documented in [Command Line Interface](#5.1).

**Sources:** [pyproject.toml:114-115]()

### Package Data Inclusion

Optuna includes non-Python files in the distribution for storage system functionality:

```toml
[tool.setuptools.package-data]
"optuna" = [
  "storages/_rdb/alembic.ini",
  "storages/_rdb/alembic/*.*",
  "storages/_rdb/alembic/versions/*.*",
  "py.typed",
]
```

These files support Alembic database migrations and enable type checking for installed packages via the `py.typed` marker.

**Sources:** [pyproject.toml:123-129]()

---

# Page: Project Structure and Dependencies

# Project Structure and Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [pyproject.toml](pyproject.toml)

</details>



## Purpose and Scope

This document explains Optuna's project structure, build configuration, and dependency management system. It covers the directory layout of the repository, the `pyproject.toml` configuration file that serves as the central build and tool configuration, and how dependencies are organized into groups for different use cases. For information about the testing framework and CI/CD workflows, see page 6.2. For contribution guidelines including development setup, see page 6.3.

## Repository Structure Overview

The Optuna repository follows a standard Python package structure with clear separation between source code, tests, documentation, and configuration files:

```mermaid
graph TB
    subgraph "Repository Root"
        PyProject["pyproject.toml<br/>Central configuration"]
        PreCommit[".pre-commit-config.yaml<br/>Git hooks"]
        Contributing["CONTRIBUTING.md<br/>Developer guide"]
    end
    
    subgraph "optuna/ - Source Package"
        Study["study.py<br/>Study management"]
        Trial["trial/<br/>Trial execution"]
        Samplers["samplers/<br/>Sampling algorithms"]
        Storages["storages/<br/>Storage backends"]
        Pruners["pruners/<br/>Pruning algorithms"]
        Integration["integration/<br/>External integrations"]
        CLI["cli.py<br/>Command-line tool"]
        Distributions["distributions.py<br/>Parameter distributions"]
        Version["version.py<br/>Version string"]
        Visualization["visualization/<br/>Plotting utilities"]
    end
    
    subgraph "tests/ - Test Suite"
        UnitTests["Unit tests<br/>Mirror optuna/ structure"]
        IntegrationTests["integration_tests/<br/>End-to-end tests"]
        StorageTests["Storage backend tests<br/>Multi-DB testing"]
    end
    
    subgraph "docs/ - Documentation"
        Source["source/<br/>RST files"]
        Build["build/<br/>Generated HTML"]
        ConfPy["source/conf.py<br/>Sphinx config"]
    end
    
    subgraph "tutorial/ - Executable Examples"
        KeyFeatures["10_key_features/<br/>Core functionality"]
        Recipes["20_recipes/<br/>Advanced usage"]
    end
    
    PyProject -.configures.-> Samplers
    PyProject -.configures.-> PreCommit
    Study --> Samplers
    Study --> Storages
    Study --> Pruners
    Trial --> Distributions
    Integration -.lazy loads.-> Samplers
```

**Optuna Repository Directory Structure**

The repository is organized into distinct areas: the `optuna/` package contains all source code, `tests/` mirrors this structure for testing, `docs/` contains Sphinx documentation, and `tutorial/` provides executable examples that are built into the documentation via Sphinx-Gallery.

Sources: [pyproject.toml:112-124](), [CONTRIBUTING.md:94-141]()

## Configuration Architecture Overview

Optuna uses `pyproject.toml` as the central configuration file for package metadata, dependencies, build system, and all development tools. This follows PEP 517/518 standards for modern Python packaging:

```mermaid
graph TB
    subgraph "pyproject.toml Sections"
        BuildSys["[build-system]<br/>setuptools >= 61.1.0"]
        Project["[project]<br/>name, version, dependencies"]
        OptDeps["[project.optional-dependencies]<br/>checking, document,<br/>optional, test"]
        Scripts["[project.scripts]<br/>optuna = optuna.cli:main"]
        SetuptoolsPkg["[tool.setuptools.packages.find]<br/>include = ['optuna*']"]
        SetuptoolsData["[tool.setuptools.package-data]<br/>Alembic files, py.typed"]
        ToolRuff["[tool.ruff]<br/>line-length = 99"]
        ToolMypy["[tool.mypy]<br/>Strict type checking"]
        ToolPytest["[tool.pytest.ini_options]<br/>Test markers, filters"]
    end
    
    subgraph "Build Output"
        WheelDist["Wheel distribution<br/>optuna-X.Y.Z-py3-*.whl"]
        CLI["optuna command<br/>Installed to PATH"]
        TypeInfo["Type information<br/>py.typed marker"]
    end
    
    BuildSys --> WheelDist
    Scripts --> CLI
    SetuptoolsData --> TypeInfo
    OptDeps -.installs.-> DevTools["Development tools"]
    
    ToolRuff -.configures.-> Ruff["ruff check/format"]
    ToolMypy -.configures.-> Mypy["mypy type checker"]
    ToolPytest -.configures.-> Pytest["pytest runner"]
```

**pyproject.toml Configuration Architecture**

The `pyproject.toml` file centralizes all project configuration. The build system section defines how to build the package, project section defines metadata and dependencies, optional-dependencies enable feature sets, and tool sections configure development tools.

Sources: [pyproject.toml:1-193]()

## Build System Configuration

### Build Backend

Optuna uses `setuptools` as the build backend with PEP 517/518 compliance:

```toml
[build-system]
requires = ["setuptools >= 61.1.0", "wheel"]
build-backend = "setuptools.build_meta"
```

The minimum setuptools version (61.1.0) ensures support for `pyproject.toml`-based configuration without requiring `setup.py`. The build backend is `setuptools.build_meta`, which provides the standard PEP 517 build interface.

Sources: [pyproject.toml:1-3]()

### Package Discovery and Metadata

Setuptools automatically discovers packages and reads version information dynamically:

```mermaid
graph TB
    subgraph "Package Discovery"
        FindConfig["[tool.setuptools.packages.find]<br/>include = ['optuna*']"]
        Discovered["Discovered Packages:<br/>optuna, optuna.samplers,<br/>optuna.storages, optuna.trial,<br/>optuna.pruners, etc."]
    end
    
    subgraph "Dynamic Version"
        VersionConfig["[tool.setuptools.dynamic]<br/>version = {attr = '...'}"]
        VersionFile["optuna/version.py<br/>__version__ = 'X.Y.Z'"]
        ProjectMeta["[project]<br/>dynamic = ['version']"]
    end
    
    subgraph "Package Data Files"
        DataConfig["[tool.setuptools.package-data]"]
        Alembic["storages/_rdb/alembic.ini<br/>alembic/versions/*.py"]
        PyTyped["py.typed<br/>PEP 561 marker"]
    end
    
    FindConfig --> Discovered
    VersionConfig -.reads.-> VersionFile
    ProjectMeta --> VersionConfig
    DataConfig --> Alembic
    DataConfig --> PyTyped
```

**Package Discovery and Version Management**

Setuptools discovers all packages matching the `optuna*` pattern. The version is read dynamically from `optuna.version.__version__` at build time. Package data includes Alembic migration files for database schema versioning and the `py.typed` marker to indicate the package supports type checking.

Sources: [pyproject.toml:42](), [pyproject.toml:112-124]()

### Project Metadata

The `[project]` section defines core metadata:

| Field | Value | Purpose |
|-------|-------|---------|
| `name` | `"optuna"` | Package name on PyPI |
| `description` | `"A hyperparameter optimization framework"` | Short description |
| `readme` | `"README.md"` | Long description from README |
| `requires-python` | `">=3.9"` | Minimum Python version |
| `dynamic` | `["version"]` | Version read from code at build time |

The project also defines classifiers indicating production stability, Python version support (3.9-3.14), and categorization as a scientific/AI library.

Sources: [pyproject.toml:5-42]()

### CLI Entry Point

The `optuna` command-line tool is registered as a console script:

```toml
[project.scripts]
optuna = "optuna.cli:main"
```

This creates an executable `optuna` command that invokes the `main()` function in `optuna.cli` module.

Sources: [pyproject.toml:109-110]()

## Dependency Management

### Core Runtime Dependencies

Optuna's core dependencies are minimal to reduce installation overhead. These are installed automatically with `pip install optuna`:

| Dependency | Version Constraint | Purpose | Used By |
|------------|-------------------|---------|---------|
| `alembic` | >=1.5.0 | Database schema migrations | `optuna.storages._rdb` |
| `colorlog` | (any) | Colored log output | Logging system |
| `numpy` | (any) | Numerical arrays and operations | Samplers, distributions |
| `packaging` | >=20.0 | Version parsing and comparison | Compatibility checks |
| `sqlalchemy` | >=1.4.2 | SQL database ORM | `optuna.storages.RDBStorage` |
| `tqdm` | (any) | Progress bar display | `optuna._optimize` |
| `PyYAML` | (any) | YAML configuration parsing | `optuna.cli` |

These dependencies support the core optimization loop, basic storage backends (RDBStorage, InMemoryStorage), and simple samplers (RandomSampler). Advanced features require optional dependencies.

Sources: [pyproject.toml:33-41]()

### Optional Dependency Groups

Optuna organizes optional dependencies into feature groups that can be installed selectively:

```mermaid
graph TB
    subgraph "Installation Options"
        Base["pip install optuna<br/>(core only)"]
        Optional["pip install optuna[optional]<br/>(all optional features)"]
        Test["pip install optuna[test]<br/>(testing tools)"]
        Checking["pip install optuna[checking]<br/>(linters, type checkers)"]
        Document["pip install optuna[document]<br/>(doc building)"]
    end
    
    subgraph "optional - Advanced Features"
        OptCmaes["cmaes >= 0.12.0<br/>CmaEsSampler"]
        OptPlotly["plotly >= 4.9.0<br/>Visualization"]
        OptPandas["pandas<br/>DataFrame export"]
        OptScikit["scikit-learn >= 0.24.2<br/>Feature importance"]
        OptScipy["scipy, torch, greenlet<br/>GPSampler"]
        OptBoto["boto3<br/>S3 artifact storage"]
        OptGCS["google-cloud-storage<br/>GCS artifacts"]
        OptRedis["redis<br/>JournalRedisBackend"]
        OptGRPC["grpcio, protobuf<br/>gRPC storage"]
    end
    
    subgraph "test - Testing Infrastructure"
        TestPytest["pytest<br/>Test framework"]
        TestXdist["pytest-xdist<br/>Parallel testing"]
        TestFakeRedis["fakeredis[lua]<br/>Mock Redis"]
        TestMoto["moto<br/>Mock AWS services"]
    end
    
    subgraph "checking - Code Quality"
        CheckMypy["mypy<br/>Type checking"]
        CheckRuff["ruff<br/>Linting/formatting"]
        CheckTypes["types-*<br/>Type stubs"]
    end
    
    Optional --> OptCmaes
    Optional --> OptPlotly
    Optional --> OptScipy
    Test --> TestPytest
    Checking --> CheckMypy
```

**Optional Dependency Groups**

Each group enables specific functionality. The `optional` group includes all advanced features like sophisticated samplers and cloud storage. The `test` group provides testing infrastructure. The `checking` group enables code quality tools.

Sources: [pyproject.toml:44-101]()

### Optional Dependencies Details

#### optional - Advanced Features

| Dependency | Purpose | Enables |
|------------|---------|---------|
| `cmaes>=0.12.0` | CMA-ES optimization library | `CmaEsSampler` |
| `plotly>=4.9.0` | Interactive visualizations | `optuna.visualization` module |
| `matplotlib!=3.6.0` | Static plotting backend | `optuna.visualization.matplotlib` |
| `pandas` | DataFrame operations | `study.trials_dataframe()` |
| `scikit-learn>=0.24.2` | Feature importance calculation | `optuna.importance` module |
| `scipy` | Scientific computing | `GPSampler` kernel functions |
| `torch` | PyTorch integration | `GPSampler` optimization |
| `greenlet` | Async optimization | Faster GP sampling |
| `boto3` | AWS S3 client | `optuna.artifacts._boto3` |
| `google-cloud-storage` | GCS client | `optuna.artifacts._gcs` |
| `redis` | Redis client | `JournalRedisBackend` |
| `grpcio`, `protobuf>=5.28.1` | gRPC protocol | `optuna.storages._grpc` |

Sources: [pyproject.toml:75-89]()

#### test - Testing Dependencies

| Dependency | Purpose |
|------------|---------|
| `pytest` | Test framework and runner |
| `pytest-xdist` | Parallel test execution |
| `fakeredis[lua]` | In-memory Redis mock for testing |
| `moto` | Mock AWS services (S3, etc.) |
| `scipy>=1.9.2` | Required for GP sampler tests |
| `torch`, `greenlet` | GP sampler testing |
| `grpcio`, `protobuf>=5.28.1` | gRPC storage testing |
| `kaleido<0.4` | Plotly static image export |

Sources: [pyproject.toml:90-101]()

#### checking - Development Tools

| Dependency | Purpose |
|------------|---------|
| `mypy` | Static type checker |
| `ruff` | Fast Python linter and formatter |
| `mypy_boto3_s3` | Type stubs for boto3 S3 |
| `scipy-stubs` | Type stubs for scipy (Python ≥3.10) |
| `types-PyYAML`, `types-redis`, `types-setuptools`, `types-tqdm` | Type stubs for runtime dependencies |
| `typing_extensions>=3.10.0.0` | Backported typing features |

Sources: [pyproject.toml:45-55]()

#### document - Documentation Building

The `document` group includes dependencies for building Sphinx documentation and executing tutorial examples:

- **Documentation tools**: `sphinx`, `sphinx-copybutton`, `sphinx-gallery`, `sphinx-notfound-page`, `sphinx_rtd_theme>=1.2.0`
- **Tutorial dependencies**: `torch`, `torchvision`, `lightgbm`, `scikit-learn`, `ase`, `fvcore`
- **Visualization**: `plotly>=4.9.0`, `matplotlib!=3.6.0`, `pandas`, `pillow`, `kaleido<0.4`
- **Sampling**: `cmaes>=0.12.0`

The tutorial dependencies are needed because Sphinx-Gallery executes all `tutorial/**/*.py` files during the documentation build to generate output and ensure examples remain functional.

Sources: [pyproject.toml:56-74](), [CONTRIBUTING.md:113-141]()

## Docker Containerization

### Multi-Stage Build Configuration

```mermaid
graph TB
    subgraph "Base Image"
        PythonBase["python:${PYTHON_VERSION}<br/>Default: 3.8"]
        SystemDeps["System Dependencies<br/>openmpi-bin, libopenmpi-dev<br/>libopenblas-dev"]
    end
    
    subgraph "Build Arguments"
        PythonVersion["PYTHON_VERSION<br/>Default: 3.8"]
        BuildType["BUILD_TYPE<br/>dev | prod"]
    end
    
    subgraph "Development Build"
        DevInstall["pip install -e .[benchmark,<br/>checking, document,<br/>optional, test]"]
        PyTorchIndex["--extra-index-url<br/>PyTorch CPU"]
    end
    
    subgraph "Production Build"
        ProdInstall["pip install -e ."]
    end
    
    subgraph "Additional Components"
        RDBBindings["RDB Bindings<br/>PyMySQL, cryptography<br/>psycopg2-binary"]
        JupyterTools["Jupyter Notebook<br/>Development tools"]
    end
    
    PythonBase --> SystemDeps
    PythonVersion --> PythonBase
    BuildType --> DevInstall
    BuildType --> ProdInstall
    
    DevInstall --> PyTorchIndex
    DevInstall --> RDBBindings
    ProdInstall --> RDBBindings
    
    RDBBindings --> JupyterTools
```

**Docker Build Process and Configuration**

The Docker configuration supports both development and production environments with different dependency sets and configurations.

### Build Type Configuration

| Build Type | Dependencies | Purpose |
|------------|--------------|---------|
| `dev` (default) | Full extras: benchmark, checking, document, optional, test | Development environment |
| `prod` | Minimal installation | Production deployment |

The development build includes PyTorch CPU-only wheels for faster installation and comprehensive tooling for development workflows.

Sources: [Dockerfile:1-29]()

## Environment Configuration

### System Dependencies

The Docker image includes essential system-level dependencies for scientific computing and parallel processing:

- **OpenMPI**: `openmpi-bin`, `libopenmpi-dev` for distributed computing support
- **OpenBLAS**: `libopenblas-dev` for optimized linear algebra operations
- **Database Connectors**: PyMySQL, cryptography, psycopg2-binary for RDB storage backends

### Python Environment Setup

The container configuration optimizes pip installation with specific options:

```bash
ENV PIP_OPTIONS "--no-cache-dir --progress-bar off"
```

This configuration reduces disk usage and provides cleaner output during builds, which is particularly important in CI/CD environments.

Sources: [Dockerfile:5-11](), [Dockerfile:25-28]()

## Integration with Development Workflow

The build system integrates with the broader development ecosystem through several mechanisms:

1. **Automated Quality Checks**: The `formats.sh` script can be integrated into pre-commit hooks or CI pipelines
2. **Containerized Development**: Docker provides consistent environments across different development machines
3. **Flexible Build Types**: Support for both minimal production builds and full-featured development environments
4. **Database Testing**: RDB bindings enable comprehensive storage backend testing

The build system ensures that code quality standards are maintained consistently across all development environments while providing flexibility for different deployment scenarios.

Sources: [formats.sh:1-112](), [Dockerfile:1-29](), [setup.cfg:1-10]()

---

# Page: Testing Infrastructure and CI/CD

# Testing and CI/CD Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/dockerimage.yml](.github/workflows/dockerimage.yml)
- [.github/workflows/mac-tests.yml](.github/workflows/mac-tests.yml)
- [.github/workflows/matplotlib-tests.yml](.github/workflows/matplotlib-tests.yml)
- [.github/workflows/tests-storage.yml](.github/workflows/tests-storage.yml)
- [.github/workflows/tests-with-minimum-versions.yml](.github/workflows/tests-with-minimum-versions.yml)
- [.github/workflows/tests.yml](.github/workflows/tests.yml)
- [.github/workflows/windows-tests.yml](.github/workflows/windows-tests.yml)
- [Dockerfile](Dockerfile)

</details>



## Purpose and Scope

This document describes Optuna's comprehensive testing and continuous integration/continuous deployment (CI/CD) infrastructure. It covers the test framework configuration, GitHub Actions workflows for automated testing across platforms and environments, parallel test execution strategies, Docker image building, and pre-commit hooks for local development.

For information about project configuration and dependencies, see [Project Configuration and Dependencies](#6.1). For contribution workflow and guidelines, see [Development Workflow and Contribution Guide](#6.3).

---

## Test Framework Configuration

Optuna uses **pytest** as its testing framework with configuration defined in [pyproject.toml:185-190](). The test suite is organized under the `tests/` directory and includes unit tests, integration tests, and storage backend tests.

### Test Markers

The pytest configuration defines custom markers for categorizing tests:

- `slow`: Marks computationally expensive tests that are skipped in regular CI runs but executed in scheduled runs

```ini
[tool.pytest.ini_options]
addopts = "--color=yes"
filterwarnings = 'ignore::optuna.exceptions.ExperimentalWarning'
markers = [
  "slow: marks tests as slow (deselect with '-m \"not slow\"')"
]
```

### Dependency Groups

Test dependencies are organized into logical groups in [pyproject.toml:95-106]():

| Dependency Group | Purpose | Key Packages |
|-----------------|---------|--------------|
| `test` | Core testing packages | `pytest`, `pytest-xdist`, `fakeredis`, `moto`, `scipy`, `torch` |
| `optional` | Optional feature testing | `cmaes`, `matplotlib`, `plotly`, `redis`, `scikit-learn`, `boto3` |
| `checking` | Code quality tools | `mypy`, `ruff`, type stubs |

**Sources:** [pyproject.toml:185-190](), [pyproject.toml:95-106]()

---

## CI/CD Workflows Overview

Optuna's CI/CD infrastructure consists of multiple GitHub Actions workflows, each targeting specific aspects of the codebase. A **concurrency control** mechanism ensures only one workflow run per branch is active, canceling in-progress runs when new commits are pushed.

```mermaid
graph TB
    subgraph "Workflow Triggers"
        Push["Push to master"]
        PR["Pull Request"]
        Schedule["Scheduled<br/>(0:23 UTC SUN-THU)"]
        Dispatch["workflow_dispatch<br/>(Manual)"]
    end
    
    subgraph "Core Test Workflows"
        MainTests["tests.yml<br/>Ubuntu + Python 3.9-3.14<br/>Redis service"]
        MacTests["mac-tests.yml<br/>macOS + Python 3.12"]
        WindowsTests["windows-tests.yml<br/>Windows + Python 3.12"]
    end
    
    subgraph "Specialized Workflows"
        StorageTests["tests-storage.yml<br/>MySQL, PostgreSQL, Redis<br/>Python 3.9-3.14"]
        MinVersions["tests-with-minimum-versions.yml<br/>Python 3.9<br/>Minimum dependency versions"]
        MatplotlibTests["matplotlib-tests.yml<br/>Visualization without Plotly"]
    end
    
    subgraph "Distribution"
        Docker["dockerimage.yml<br/>Build & push images<br/>Python 3.9-3.12"]
    end
    
    Push --> MainTests
    Push --> MacTests
    Push --> WindowsTests
    Push --> StorageTests
    Push --> Docker
    
    PR --> MainTests
    PR --> MacTests
    PR --> WindowsTests
    PR --> StorageTests
    PR --> MinVersions
    
    Schedule --> MainTests
    Schedule --> MacTests
    Schedule --> WindowsTests
    Schedule --> StorageTests
    Schedule --> MinVersions
    
    Dispatch --> MainTests
    Dispatch --> MacTests
    Dispatch --> WindowsTests
    Dispatch --> StorageTests
    Dispatch --> MinVersions
```

**Concurrency Control Pattern**

Each workflow includes a concurrency configuration to prevent duplicate runs:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref == 'refs/heads/master' && github.run_number || github.ref }}
  cancel-in-progress: true
```

This groups workflow runs by workflow name and branch/PR reference, automatically canceling previous runs when new commits arrive.

**Sources:** [.github/workflows/tests.yml:12-14](), [.github/workflows/mac-tests.yml:15-17](), [.github/workflows/windows-tests.yml:15-17]()

---

## Platform Testing Matrix

### Main Test Workflow (Ubuntu)

The primary test workflow [.github/workflows/tests.yml]() runs on Ubuntu with the most extensive Python version coverage:

```mermaid
graph TB
    subgraph "tests.yml Strategy"
        Matrix["Matrix Strategy"]
        
        Python39["Python 3.9<br/>(Always)"]
        Python313["Python 3.13<br/>(Always)"]
        Python314["Python 3.14<br/>(Always)"]
        Python310["Python 3.10<br/>(Scheduled only)"]
        Python311["Python 3.11<br/>(Scheduled only)"]
        Python312["Python 3.12<br/>(Scheduled only)"]
    end
    
    subgraph "Services"
        Redis["redis:latest<br/>Port 6379<br/>Health checks"]
    end
    
    subgraph "Test Execution"
        NonScheduled["PR/Push<br/>pytest -m 'not slow' -n 8"]
        Scheduled["Scheduled/Manual<br/>pytest -n 8"]
    end
    
    Matrix --> Python39
    Matrix --> Python313
    Matrix --> Python314
    Matrix --> Python310
    Matrix --> Python311
    Matrix --> Python312
    
    Python39 --> Redis
    Python313 --> Redis
    Python314 --> Redis
    Python310 --> Redis
    Python311 --> Redis
    Python312 --> Redis
    
    Redis --> NonScheduled
    Redis --> Scheduled
```

**Test Trigger Logic:**

- **Pull Requests / Push to master**: Tests run on Python 3.9, 3.13, 3.14 with slow tests excluded
- **Scheduled runs (nightly)**: Tests run on all Python versions (3.9-3.14) including slow tests
- **workflow_dispatch (manual)**: Same as scheduled

**Sources:** [.github/workflows/tests.yml:21-32](), [.github/workflows/tests.yml:86-95]()

### Platform-Specific Workflows

Both macOS and Windows workflows use Python 3.12 only for speed:

| Platform | Workflow File | Python Version | Special Configuration |
|----------|--------------|----------------|----------------------|
| macOS | `mac-tests.yml` | 3.12 | Cache: `~/Library/Caches/pip` |
| Windows | `windows-tests.yml` | 3.12 | PyQt6 for matplotlib, NumPy < 2.0.0, QtAgg backend |

**Windows-Specific Constraints:**

The Windows workflow includes workarounds for platform-specific issues [.github/workflows/windows-tests.yml:54-61]():

```yaml
- pip install PyQt6  # Install PyQT for using QtAgg as matplotlib backend
- pip install "kaleido<=0.1.0post1"  # Hotfix for Kaleido issue
- pip install "plotly<6.3.0"  # Hotfix for version constraint
- pip uninstall numpy
- pip install 'numpy<2.0.0'  # Torch doesn't support NumPy 2.0 on Windows
```

**Sources:** [.github/workflows/mac-tests.yml:20-71](), [.github/workflows/windows-tests.yml:20-84]()

---

## Storage Backend Testing

The `tests-storage.yml` workflow validates Optuna's storage implementations against real database servers running as GitHub Actions services.

```mermaid
graph TB
    subgraph "Service Containers"
        MySQL["mysql:8<br/>Port 3306<br/>Database: optunatest<br/>User: user<br/>Password: test"]
        Postgres["postgres:latest<br/>Port 5432<br/>Database: optunatest<br/>User: user<br/>Password: test"]
        Redis["redis:latest<br/>Port 6379"]
    end
    
    subgraph "Test Runs"
        MySQLTest["MySQL Test<br/>mysql+pymysql://user:test@127.0.0.1/optunatest<br/>tests/storages_tests/test_with_server.py"]
        Psycopg2Test["PostgreSQL psycopg2 Test<br/>postgresql+psycopg2://user:test@127.0.0.1/optunatest<br/>tests/storages_tests/test_with_server.py"]
        Psycopg3Test["PostgreSQL psycopg3 Test<br/>postgresql+psycopg://user:test@127.0.0.1/optunatest<br/>tests/storages_tests/test_with_server.py"]
        RedisTest["Journal Redis Test<br/>redis://localhost:6379<br/>TEST_DB_MODE=journal-redis<br/>tests/storages_tests/test_with_server.py"]
    end
    
    subgraph "Python Matrix"
        Py39["3.9 (Always)"]
        Py313["3.13 (Always)"]
        Py314["3.14 (Always)"]
        Py310["3.10 (Scheduled)"]
        Py311["3.11 (Scheduled)"]
        Py312["3.12 (Scheduled)"]
    end
    
    MySQL --> MySQLTest
    Postgres --> Psycopg2Test
    Postgres --> Psycopg3Test
    Redis --> RedisTest
    
    Py39 --> MySQLTest
    Py39 --> Psycopg2Test
    Py39 --> Psycopg3Test
    Py39 --> RedisTest
```

### Database Driver Installation

The workflow installs database-specific bindings [.github/workflows/tests-storage.yml:107-109]():

```bash
pip install PyMySQL cryptography psycopg2-binary psycopg redis
```

### Test Database URLs

Each test run configures the storage backend via the `TEST_DB_URL` environment variable:

| Backend | URL Format | Environment Variables |
|---------|-----------|----------------------|
| MySQL | `mysql+pymysql://user:test@127.0.0.1/optunatest` | `TEST_DB_URL`, `SQLALCHEMY_WARN_20=1` |
| PostgreSQL (psycopg2) | `postgresql+psycopg2://user:test@127.0.0.1/optunatest` | `TEST_DB_URL`, `OMP_NUM_THREADS=1` |
| PostgreSQL (psycopg3) | `postgresql+psycopg://user:test@127.0.0.1/optunatest` | `TEST_DB_URL`, `OMP_NUM_THREADS=1` |
| Journal Redis | `redis://localhost:6379` | `TEST_DB_URL`, `TEST_DB_MODE=journal-redis` |

**Sources:** [.github/workflows/tests-storage.yml:37-68](), [.github/workflows/tests-storage.yml:119-147]()

---

## Dependency and Compatibility Testing

### Minimum Version Testing

The `tests-with-minimum-versions.yml` workflow ensures backward compatibility by testing with the minimum supported versions of all dependencies [.github/workflows/tests-with-minimum-versions.yml:69-78]():

```bash
# Uninstall current versions
pip uninstall -y alembic cmaes packaging sqlalchemy plotly scikit-learn pillow

# Install minimum versions as specified in pyproject.toml
pip install alembic==1.5.0 cmaes==0.12.0 packaging==20.0 sqlalchemy==1.4.2 \
            tqdm==4.27.0 colorlog==0.3 PyYAML==5.1 'pillow<10.4.0'

# Optional dependencies minimum versions
pip install plotly==5.0.0 scikit-learn==0.24.2
```

**Minimum Version Requirements:**

| Dependency | Minimum Version | Specified In |
|-----------|----------------|--------------|
| alembic | 1.5.0 | [pyproject.toml:34]() |
| cmaes | 0.12.0 | [pyproject.toml:63]() |
| packaging | 20.0 | [pyproject.toml:37]() |
| sqlalchemy | 1.4.2 | [pyproject.toml:38]() |
| plotly | 4.9.0 (5.0.0 for tests) | [pyproject.toml:70]() |
| scikit-learn | 0.24.2 | [pyproject.toml:88]() |

### Matplotlib-Specific Testing

The `matplotlib-tests.yml` workflow validates that visualization works without Plotly [.github/workflows/matplotlib-tests.yml:58-62]():

```bash
pip uninstall -y plotly
pytest tests/visualization_tests/matplotlib_tests -n 8
```

This ensures users can use Matplotlib backend independently without requiring Plotly.

**Sources:** [.github/workflows/tests-with-minimum-versions.yml:69-78](), [.github/workflows/matplotlib-tests.yml:58-62]()

---

## Test Execution Strategies

### Parallel Test Execution

All test workflows use `pytest-xdist` for parallel test execution with 8 workers:

```bash
pytest tests -m "$target" -n 8
```

The `-n 8` flag distributes tests across 8 parallel processes, significantly reducing total test time.

### Test Filtering by Marker

Test execution varies based on trigger type:

```mermaid
graph LR
    subgraph "Test Filtering Logic"
        Trigger{Event Type}
        
        PR["Pull Request<br/>or Push"]
        Scheduled["Scheduled<br/>or Manual"]
        
        FastTests["pytest -m 'not slow' -n 8<br/>(Exclude slow tests)"]
        AllTests["pytest -n 8<br/>(Include all tests)"]
    end
    
    Trigger -->|"push / pull_request"| PR
    Trigger -->|"schedule / workflow_dispatch"| Scheduled
    
    PR --> FastTests
    Scheduled --> AllTests
```

**Implementation in tests.yml** [.github/workflows/tests.yml:86-95]():

```bash
if [ "${{ github.event_name }}" = "schedule" ] || \
   [ "${{ github.event_name }}" = "workflow_dispatch" ] ; then
  target=""
else
  target="not slow"
fi

pytest tests -m "$target" -n 8
```

### Environment Variables

Tests are executed with specific environment variables:

| Variable | Purpose | Workflows |
|----------|---------|-----------|
| `SQLALCHEMY_WARN_20` | Enable SQLAlchemy 2.0 warnings | tests.yml, tests-storage.yml |
| `OMP_NUM_THREADS` | Limit OpenMP threads for parallel tests | tests-storage.yml |
| `MPLBACKEND` | Set matplotlib backend | windows-tests.yml (`QtAgg`) |
| `TEST_DB_URL` | Database connection string | tests-storage.yml |
| `TEST_DB_MODE` | Storage mode (e.g., `journal-redis`) | tests-storage.yml |

**Sources:** [.github/workflows/tests.yml:86-97](), [pyproject.toml:185-190]()

---

## Docker Image Build Pipeline

The `dockerimage.yml` workflow builds and publishes Docker images to Docker Hub for multiple Python versions and build types.

```mermaid
graph TB
    subgraph "Build Matrix"
        Python39["Python 3.9"]
        Python310["Python 3.10"]
        Python311["Python 3.11"]
        Python312["Python 3.12"]
        
        Standard["BUILD_TYPE=''<br/>(Standard install)"]
        Dev["BUILD_TYPE='dev'<br/>(All dependencies)"]
    end
    
    subgraph "Docker Build Process"
        BuildImage["docker build<br/>--build-arg PYTHON_VERSION<br/>--build-arg BUILD_TYPE<br/>--file Dockerfile"]
        
        Verify["docker run optuna --version"]
    end
    
    subgraph "Tag Generation"
        PRTag["PR: optuna/optuna:py3.X[-dev]"]
        MasterTag["Master: optuna/optuna:py3.X[-dev]"]
        ReleaseTag["Release: optuna/optuna:vX.Y.Z-py3.X[-dev]"]
    end
    
    subgraph "Docker Hub"
        Push["docker push<br/>(if not PR)"]
    end
    
    Python39 --> Standard
    Python39 --> Dev
    Python310 --> Standard
    Python310 --> Dev
    Python311 --> Standard
    Python311 --> Dev
    Python312 --> Standard
    Python312 --> Dev
    
    Standard --> BuildImage
    Dev --> BuildImage
    
    BuildImage --> Verify
    Verify --> PRTag
    Verify --> MasterTag
    Verify --> ReleaseTag
    
    MasterTag --> Push
    ReleaseTag --> Push
```

### Build Types

The Dockerfile supports two build types [Dockerfile:16-23]():

| Build Type | Install Command | Use Case |
|------------|----------------|----------|
| Standard (`''`) | `pip install -e .` | Production images, minimal dependencies |
| Dev (`'dev'`) | `pip install -e '.[benchmark, checking, document, optional, test]'` | Development images, all dependencies including testing tools |

### Tag Naming Convention

Tags are generated based on the event type [.github/workflows/dockerimage.yml:39-48]():

```bash
export TAG_NAME="py${{ matrix.python_version }}"
if [ "${{ github.event_name }}" = 'release' ]; then
  export TAG_NAME="${{ github.event.release.tag_name }}-${TAG_NAME}"
fi
if [ "${{matrix.build_type}}" = 'dev' ]; then
  export TAG_NAME="${TAG_NAME}-dev"
fi
```

**Examples:**
- Standard build, Python 3.10, master push: `optuna/optuna:py3.10`
- Dev build, Python 3.12, release v3.0.0: `optuna/optuna:v3.0.0-py3.12-dev`

### Dockerfile Configuration

The Dockerfile installs system dependencies and RDB bindings [Dockerfile:7-26]():

```dockerfile
RUN apt-get update \
    && apt-get -y install openmpi-bin libopenmpi-dev libopenblas-dev

# Install Optuna
RUN if [ "${BUILD_TYPE}" = "dev" ]; then \
        pip install -e '.[benchmark, checking, document, optional, test]'; \
    else \
        pip install -e .; \
    fi

# Install RDB bindings
RUN pip install PyMySQL cryptography psycopg2-binary
```

**Sources:** [.github/workflows/dockerimage.yml:25-79](), [Dockerfile:1-29]()

---

## Pre-commit Hooks and Local Development

Optuna uses **pre-commit** to enforce code quality checks before commits are made.

### Pre-commit Configuration

The [.pre-commit-config.yaml]() defines two hook categories:

```mermaid
graph LR
    subgraph "Pre-commit Hooks"
        RuffCheck["ruff-check<br/>Code linting<br/>--fix flag"]
        RuffFormat["ruff-format<br/>Code formatting"]
        Mypy["mypy<br/>Type checking<br/>Strict configuration"]
    end
    
    subgraph "Excluded Paths"
        Docs["docs/"]
        Tutorial["tutorial/"]
        Alembic["optuna/storages/_rdb/alembic/"]
        GRPC["optuna/storages/_grpc/auto_generated/"]
    end
    
    RuffCheck --> Excluded
    RuffFormat --> Excluded
    Mypy --> Excluded
    
    Excluded{Exclusions}
    Excluded --> Docs
    Excluded --> Tutorial
    Excluded --> Alembic
    Excluded --> GRPC
```

### Installation and Usage

Contributors install pre-commit hooks via [CONTRIBUTING.md:83-88]():

```bash
# Install pre-commit
pip install pre-commit

# Install hooks to .git/hooks/
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Ruff Configuration

Ruff is configured in [pyproject.toml:131-183]() with the following settings:

| Setting | Value | Purpose |
|---------|-------|---------|
| `line-length` | 99 | Maximum line length |
| `target-version` | py39 | Minimum Python version |
| Selected rules | E, W, F, I | pycodestyle errors/warnings, pyflakes, isort |
| `force-single-line` | true | One import per line |
| `lines-after-imports` | 2 | Spacing after import block |

### Mypy Configuration

Mypy runs in strict mode with extensive checks [pyproject.toml:192-206]():

```ini
[tool.mypy]
warn_unused_configs = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
strict_equality = true
extra_checks = true
no_implicit_reexport = true
ignore_missing_imports = true
```

**Sources:** [.pre-commit-config.yaml:1-49](), [pyproject.toml:131-206](), [CONTRIBUTING.md:80-89]()

---

## Workflow Schedule and Repository Restrictions

### Scheduled Runs

All main workflows run on a schedule [.github/workflows/tests.yml:8-9]():

```yaml
schedule:
  - cron: '0 23 * * SUN-THU'
```

This runs tests at 23:00 UTC (11 PM) Sunday through Thursday, providing nightly validation without weekend runs.

### Repository Restrictions

Scheduled runs and Docker builds are restricted to the main repository [.github/workflows/tests.yml:18]():

```yaml
if: (github.event_name == 'schedule' && github.repository == 'optuna/optuna') || (github.event_name != 'schedule')
```

This prevents scheduled workflows from running in forks, conserving CI resources.

### Dependency Verification

All workflows output installed packages and dependency trees for debugging:

```bash
pip freeze --all
pip install pipdeptree
pipdeptree
```

This provides complete visibility into the test environment's dependency resolution.

**Sources:** [.github/workflows/tests.yml:8-9](), [.github/workflows/tests.yml:18](), [.github/workflows/tests.yml:78-84]()

---

## Test Coverage and Quality Assurance

### Installation Verification

Every workflow verifies minimal installation before running full tests [.github/workflows/tests.yml:68-73]():

```bash
# Install minimal dependencies and confirm that `import optuna` is successful.
pip install --progress-bar off .
python -c 'import optuna'
optuna --version
```

This ensures the core package can be imported with only required dependencies, catching issues with optional dependency handling.

### Test Policy

According to [CONTRIBUTING.md:169](), Optuna follows documented test policies available in the Optuna Wiki covering:

- Test quality requirements
- Test organization principles
- Coverage expectations
- Integration test guidelines

**Sources:** [.github/workflows/tests.yml:68-76](), [CONTRIBUTING.md:144-169]()

---

# Page: Development Workflow and Contribution Guide

# Contribution Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [pyproject.toml](pyproject.toml)

</details>



This guide outlines how to contribute to the Optuna project, covering everything from setting up your development environment to submitting a pull request. It's designed to help both new and experienced contributors understand the contribution process and requirements.

## Introduction

Optuna is an open-source project that welcomes contributions from everyone. There are many ways you can contribute:

- Implementing new features
- Fixing bugs labeled with `contribution-welcome` 
- Improving documentation
- Sharing ideas and thoughts in GitHub Discussions
- Writing tutorials and examples

For information about the testing system and CI/CD pipeline, see [Testing Framework](#6.1).

Sources: [CONTRIBUTING.md:1-29](), [README.md:250-258]()

## Getting Started

### Setting Up Your Development Environment

To get started contributing to Optuna, you'll need to set up your development environment:

1. Fork Optuna on GitHub
2. Clone your fork locally
3. Install Optuna in development mode

```bash
git clone git@github.com:YOUR_NAME/optuna.git
cd optuna
pip install -e .
```

### Finding Issues to Work On

If you're new to Optuna, look for issues labeled as [good first issues](https://github.com/optuna/optuna/labels/good%20first%20issue). These are relatively simple, well-defined issues that are good starting points.

For experienced contributors, check other [contribution-welcome issues](https://github.com/optuna/optuna/labels/contribution-welcome).

Sources: [CONTRIBUTING.md:48-52](), [README.md:254-256]()

## Development Workflow

### Contribution Process Overview

```mermaid
graph TD
    A["Fork Repository"] --> B["Clone Locally"]
    B --> C["pip install -e ."]
    C --> D["Create Feature Branch"]
    D --> E["Make Code Changes"]
    
    E --> F["Run formats.sh"]
    F -- "Issues Found" --> E
    
    F -- "Checks Pass" --> G["Write Tests in tests/"]
    G --> H["Run pytest"]
    H -- "Tests Fail" --> G
    
    H -- "Tests Pass" --> I["Update Documentation"]
    I --> J["Build Docs with make html"]
    J --> K["Create Pull Request"]
    
    K --> L["Address Review Feedback"]
    L --> M["PR Merged"]
    
    subgraph "Quality Gates"
        F["Code Quality Checks"]
        H["Test Validation"]
        J["Documentation Build"]
    end
```

Sources: [CONTRIBUTING.md:32-41]()

## Code Style and Quality

### Code Formatting and Style Checking

Optuna maintains strict code quality standards using several tools:

- **Code formatting**: `black` for Python code and `blackdoc` for docstrings
- **Coding style**: `flake8` and `isort` for import sorting
- **Type checking**: `mypy` for PEP 484 type hints

All of these checks can be run using the `formats.sh` script:

```bash
# Install necessary dependencies
pip install ".[checking]"

# Run all code quality checks
./formats.sh
```

Alternatively, you can use pre-commit to automatically check your code before committing:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Code Quality Tools Architecture

```mermaid
graph TD
    CodeChanges["Code Changes"] --> FormatsSh["formats.sh Script"]
    
    FormatsSh --> Black["black\nTarget: optuna tests benchmarks tutorial"]
    FormatsSh --> BlackDoc["blackdoc\nTarget: optuna tests benchmarks tutorial"]
    FormatsSh --> Flake8["flake8\nTarget: optuna tests benchmarks tutorial"]
    FormatsSh --> Isort["isort\nTarget: optuna tests benchmarks tutorial"]
    FormatsSh --> Mypy["mypy\nTarget: optuna tests benchmarks"]
    
    Black -- "Formats Code" --> CodeBase["Optuna Codebase"]
    BlackDoc -- "Formats Docstrings" --> CodeBase
    Flake8 -- "Verifies Style" --> CodeBase
    Isort -- "Sorts Imports" --> CodeBase
    Mypy -- "Checks Types" --> CodeBase
    
    CodeBase --> QualityGate["Code Quality Gate"]
    QualityGate -- "Pass" --> PR["Ready for PR"]
```

Sources: [CONTRIBUTING.md:61-90](), [formats.sh:1-112](), [setup.cfg:1-9]()

## Documentation

When adding a new feature, you must also document it in the reference. Documentation is written in reStructuredText format in the `docs` directory.

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[document]"

# Build HTML documentation
cd docs
make html
```

HTML files are generated in the `build/html` directory. Open `index.html` with your browser to see if it is rendered correctly.

### Optuna Documentation System

```mermaid
graph TD
    DocSource["Documentation Sources"] --> RstFiles["RST Files\n(docs/source/*.rst)"]
    DocSource --> PyFiles["Python Tutorial Files\n(tutorial/*.py)"]
    
    RstFiles --> APIRef["API Reference\n(docs/source/reference)"]
    RstFiles --> UserGuides["User Guides\n(docs/source/*.rst)"]
    
    PyFiles --> KeyFeatures["Key Features\n(tutorial/10_key_features)"]
    PyFiles --> Recipes["Recipes\n(tutorial/20_recipes)"]
    
    KeyFeatures & Recipes --> SphinxGallery["Sphinx-Gallery Processor\n(sphinx_gallery_conf in conf.py)"]
    
    SphinxGallery --> GenRst["Generated RST\n(docs/source/tutorial)"]
    SphinxGallery --> GenNb["Generated Notebooks\n(downloadable .ipynb)"]
    
    APIRef & UserGuides & GenRst --> SphinxBuild["Sphinx Build System\n(make html)"]
    SphinxBuild --> HTML["HTML Documentation\n(docs/build/html)"]
    HTML --> ReadTheDocs["optuna.readthedocs.io"]
```

Optuna's tutorial system uses Sphinx-Gallery, which executes Python files from the `tutorial` directory and generates both RST documentation and Jupyter notebooks. The tutorial organization is configured in the `sphinx_gallery_conf` in `docs/source/conf.py`.

Sources: [CONTRIBUTING.md:92-143](), [docs/source/conf.py:184-220]()

## Testing

When adding new features or fixing bugs, you must write sufficient test code. Optuna uses pytest as the testing framework, with tests stored in the `tests` directory.

### Running Tests

```bash
# Install test dependencies
pip install ".[test,optional]"

# Run all tests
pytest

# Run tests in a specific file
pytest tests/${TARGET_TEST_FILE_NAME}

# Run a specific test function
pytest tests/${TARGET_TEST_FILE_NAME} -k ${TARGET_TEST_FUNCTION_NAME}
```

See the [Test Policy](https://github.com/optuna/optuna/wiki/Test-Policy) for the principles of writing and maintaining Optuna tests to meet quality requirements.

Sources: [CONTRIBUTING.md:145-171]()

## Pull Request Guidelines

When creating a pull request, follow these guidelines:

### PR Title
- Briefly describe the changes
- Wrap code with backticks
- Do not end with a period

Example: `Introduces Tree-structured Parzen Estimator to optuna.samplers`

### PR Description
- Describe the motivation
- Describe the changes
- If still work-in-progress, describe remaining tasks

The PR title will appear directly in the release notes, so make it descriptive and clear.

Sources: [CONTRIBUTING.md:176-197]()

## Continuous Integration

Optuna uses GitHub Actions for continuous integration. Your pull request will be automatically verified against all quality checks, tests, and documentation builds.

Sources: [CONTRIBUTING.md:172-175]()

## Artifact System for Development

When developing features that involve storing or retrieving files (such as machine learning models), you should use Optuna's artifact system. The `ArtifactStore` protocol defines the interface for backend implementations:

```mermaid
graph TD
    Protocol["ArtifactStore Protocol\n(optuna.artifacts._protocol)"] -- "implements" --> Implementations["Storage Implementations"]
    
    Implementations --> FileSystem["FileSystemArtifactStore"]
    Implementations --> Boto3["Boto3ArtifactStore\n(S3 Compatible)"]
    Implementations --> GCS["GCSArtifactStore\n(Google Cloud Storage)"]
    
    FileSystem & Boto3 & GCS --> Common["Common Interface Methods"]
    Common --> OpenReader["open_reader(artifact_id)"]
    Common --> Write["write(artifact_id, content_body)"]
    Common --> Remove["remove(artifact_id)"]
    
    User["Your Code"] -- "uses" --> Functions["Helper Functions"]
    Functions --> Upload["upload_artifact()"]
    Functions --> Download["download_artifact()"]
    Functions --> GetMeta["get_all_artifact_meta()"]
```

This system allows you to manage files associated with trials in a consistent way, regardless of the underlying storage backend.

Sources: [optuna/artifacts/_protocol.py:1-62](), [docs/source/reference/artifacts.rst:1-46](), [docs/source/faq.rst:142-192]()

## Learning Optuna's Implementation

To better understand how Optuna is implemented, you can check out [Minituna](https://github.com/CyberAgentAILab/minituna), a simplified version of Optuna that demonstrates the core design principles. Reading Minituna first will make it easier to understand the full Optuna codebase.

Sources: [CONTRIBUTING.md:198-206]()

## Community and Communication

- [GitHub Discussions](https://github.com/optuna/optuna/discussions) for questions and general discussions
- [GitHub Issues](https://github.com/optuna/optuna/issues) for bug reports and feature requests

Remember that contributing to Optuna includes not only submitting code but also participating in discussions and providing feedback on issues and pull requests.

Sources: [CONTRIBUTING.md:11-14](), [CONTRIBUTING.md:26-28](), [README.md:241-247]()