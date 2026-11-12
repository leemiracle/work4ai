<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/botorch · page 1 Overview · fetched 2026-10-21 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [botorch/__init__.py](botorch/__init__.py)
- [botorch/settings.py](botorch/settings.py)
- [test/test_settings.py](test/test_settings.py)

</details>



## Purpose and Scope

This document provides a comprehensive overview of BoTorch, a library for Bayesian Optimization built on PyTorch. BoTorch serves as a modular, extensible framework for composing Bayesian optimization primitives including probabilistic models, acquisition functions, and optimizers. This overview covers the core architecture, main components, and how they integrate to form complete Bayesian optimization workflows.

For specific implementation details of individual systems, see the following pages:
- For model implementations and fitting procedures, see [Models](#2)
- For input/output preprocessing, see [Transforms](#3) 
- For acquisition function details and construction, see [Acquisition Functions](#4)
- For candidate optimization and constraint handling, see [Optimization](#5)
- For testing infrastructure and development tools, see [Utilities](#6)

## Architecture Overview

BoTorch's architecture centers around a standard Bayesian optimization loop with modular, interchangeable components. The framework provides both low-level primitives for researchers and higher-level convenience functions for practitioners.

### Core Framework Components

```mermaid
graph TB
    subgraph "Primary API Entry Points"
        API["botorch/__init__.py"]
        FitMLL["fit_gpytorch_mll"]
        OptAcqf["optimize_acqf"]
    end
    
    subgraph "Model System"
        Models["models/*"]
        SingleTaskGP["SingleTaskGP"]
        MultiTaskGP["MultiTaskGP"]
        FullyBayesian["SaasFullyBayesianSingleTaskGP"]
    end
    
    subgraph "Transform System" 
        Transforms["transforms/*"]
        InputTransform["Normalize, InputStandardize"]
        OutcomeTransform["Standardize, Log"]
    end
    
    subgraph "Acquisition System"
        Acquisition["acquisition/*"]
        AnalyticAcqf["ExpectedImprovement, LogEI"]
        MCAcqf["qExpectedImprovement, qNEI"]
        MOO["qEHVI, qNEHVI"]
    end
    
    subgraph "Optimization System"
        Optim["optim/*"]
        GenCandidates["gen_candidates_scipy/torch"]
        InitialConditions["gen_batch_initial_conditions"]
    end
    
    API --> FitMLL
    API --> OptAcqf
    FitMLL --> Models
    Models --> SingleTaskGP
    Models --> MultiTaskGP  
    Models --> FullyBayesian
    Models -.-> Transforms
    OptAcqf --> Acquisition
    OptAcqf --> Optim
    Acquisition --> AnalyticAcqf
    Acquisition --> MCAcqf
    Acquisition --> MOO
    Optim --> GenCandidates
    Optim --> InitialConditions
```

**Sources**: [botorch/__init__.py:9-67](), [README.md:23-38]()

### Bayesian Optimization Workflow

BoTorch implements the standard Bayesian optimization loop through a series of modular steps that can be customized and extended:

```mermaid
graph TD
    Data["Training Data (X, Y)"] --> ModelConstruct["Model Construction"]
    ModelConstruct --> ModelType{Model Type Selection}
    
    ModelType -->|"Single Task"| SingleTask["SingleTaskGP"]
    ModelType -->|"Multi Task"| MultiTask["MultiTaskGP"] 
    ModelType -->|"Fully Bayesian"| SAAS["SaasFullyBayesianSingleTaskGP"]
    
    SingleTask --> FitMLL["fit_gpytorch_mll"]
    MultiTask --> FitMLL
    SAAS --> FitNUTS["fit_fully_bayesian_model_nuts"]
    
    FitMLL --> FittedModel["Fitted Model"]
    FitNUTS --> FittedModel
    
    FittedModel --> AcqfConstruct["Acquisition Function Construction"]
    AcqfConstruct --> Registry["ACQF_INPUT_CONSTRUCTOR_REGISTRY"]
    Registry --> AcqfType{Acquisition Type}
    
    AcqfType -->|"Analytic"| Analytic["ExpectedImprovement, LogEI"]
    AcqfType -->|"Monte Carlo"| MC["qExpectedImprovement, qNEI"]
    AcqfType -->|"Multi-Objective"| MOO["qExpectedHypervolumeImprovement"]
    
    Analytic --> OptimizeAcqf["optimize_acqf"]
    MC --> OptimizeAcqf
    MOO --> OptimizeAcqf
    
    OptimizeAcqf --> InitCond["gen_batch_initial_conditions"]
    InitCond --> GenCand["gen_candidates_scipy/torch"]
    GenCand --> BestCand["get_best_candidates"]
    
    BestCand --> Evaluate["Evaluate Objective"]
    Evaluate --> NewObs["New Observations"]
    NewObs --> Data
```

**Sources**: [README.md:128-170](), [botorch/__init__.py:18-24]()

## Core Components

### Models and Model Fitting

BoTorch's model system provides Gaussian Process models with extensive customization through transforms and kernels. The primary entry point for model fitting is `fit_gpytorch_mll`:

| Model Type | Class | Use Case |
|------------|-------|----------|
| Single Task | `SingleTaskGP` | Standard GP regression |
| Multi Task | `MultiTaskGP` | Multi-task learning |
| Fully Bayesian | `SaasFullyBayesianSingleTaskGP` | Uncertainty over hyperparameters |
| Multi Fidelity | `SingleTaskMultiFidelityGP` | Variable fidelity optimization |

The framework automatically applies sensible defaults including dimension-scaled priors and outcome standardization for robust performance across problem dimensions.

**Sources**: [botorch/__init__.py:19](), [README.md:132-153]()

### Acquisition Functions and Input Constructors

BoTorch provides a comprehensive acquisition function ecosystem with automatic construction via a registry pattern:

```mermaid
graph LR
    subgraph "Input Constructor System"
        Registry["ACQF_INPUT_CONSTRUCTOR_REGISTRY"]
        GetConstructor["get_acqf_input_constructor"]
        Decorator["@acqf_input_constructor"]
    end
    
    subgraph "Acquisition Function Types"
        Base["AcquisitionFunction"]
        Analytic["AnalyticAcquisitionFunction"]
        MC["MCAcquisitionFunction"]
    end
    
    subgraph "Specific Implementations"
        EI["ExpectedImprovement"]
        LogEI["LogExpectedImprovement"] 
        qEI["qExpectedImprovement"]
        qNEI["qNoisyExpectedImprovement"]
        qEHVI["qExpectedHypervolumeImprovement"]
        qKG["qKnowledgeGradient"]
    end
    
    Registry --> GetConstructor
    GetConstructor --> Decorator
    
    Base --> Analytic
    Base --> MC
    Analytic --> EI
    Analytic --> LogEI
    MC --> qEI
    MC --> qNEI
    MC --> qEHVI
    MC --> qKG
```

The registry system enables automatic acquisition function construction with appropriate default parameters based on the model and problem characteristics.

**Sources**: [README.md:155-170]()

### Optimization Infrastructure

The optimization system handles candidate generation with support for various constraint types and optimization algorithms:

| Function | Purpose | Constraints Supported |
|----------|---------|---------------------|
| `optimize_acqf` | Main optimization entry point | Linear, nonlinear, mixed |
| `gen_candidates_scipy` | SciPy-based optimization | All constraint types |
| `gen_candidates_torch` | PyTorch-based optimization | Differentiable constraints |
| `gen_batch_initial_conditions` | Smart initialization | Box bounds |

**Sources**: [botorch/__init__.py:20-24](), [README.md:162-170]()

## Configuration and Settings

BoTorch provides global configuration through the `settings` module for controlling framework behavior:

```mermaid
graph TB
    subgraph "BoTorch Settings"
        Settings["botorch.settings"]
        PropGrads["propagate_grads"]
        ValidateInput["validate_input_scaling"]
        LogLevel["log_level"]
    end
    
    subgraph "GPyTorch/LinearOperator Settings"
        GPSettings["gpytorch.settings"]
        LinOpSettings["linear_operator.settings"]
        FastComp["_fast_computations = False"]
        CholMax["cholesky_max_tries = 6"]
        MaxSize["max_cholesky_size = 4096"]
    end
    
    Settings --> PropGrads
    Settings --> ValidateInput
    Settings --> LogLevel
    
    GPSettings --> FastComp
    LinOpSettings --> CholMax
    LinOpSettings --> MaxSize
```

BoTorch automatically configures GPyTorch and LinearOperator settings for robustness in Bayesian optimization loops, disabling fast approximations that can be numerically unstable.

**Sources**: [botorch/__init__.py:36-49](), [botorch/settings.py:16-97]()

## Integration with PyTorch Ecosystem

BoTorch leverages PyTorch's features extensively:

- **Auto-differentiation**: Enables gradient-based acquisition function optimization
- **GPU Support**: Device-agnostic code for accelerated computation  
- **Dynamic Computation Graphs**: Supports flexible model architectures
- **Reparameterization Trick**: Enables Monte Carlo acquisition functions

The framework integrates with GPyTorch for probabilistic models and supports seamless integration with deep learning architectures.

**Sources**: [README.md:28-38]()

## Target Audience and Usage Patterns

BoTorch is designed as a low-level API for:

- **Researchers**: Implementing new Bayesian optimization algorithms
- **Sophisticated Practitioners**: Customizing optimization workflows
- **Framework Developers**: Building higher-level optimization platforms

For end-users seeking a complete optimization platform, BoTorch recommends using Ax, which provides a higher-level interface while leveraging BoTorch's primitives.

**Sources**: [README.md:41-51]()

---

