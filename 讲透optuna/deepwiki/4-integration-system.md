<!-- source: DeepWiki mcp.deepwiki.com · repo optuna/optuna · page 4 Integration System · fetched 2026-10-21 -->

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

