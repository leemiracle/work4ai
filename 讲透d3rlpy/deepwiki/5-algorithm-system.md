<!-- source: DeepWiki mcp.deepwiki.com · repo takuseno/d3rlpy · page 5 Algorithm System · fetched 2026-10-30 -->

# Algorithm System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ROADMAP.md](ROADMAP.md)
- [d3rlpy/algos/__init__.py](d3rlpy/algos/__init__.py)
- [d3rlpy/algos/qlearning/base.py](d3rlpy/algos/qlearning/base.py)
- [d3rlpy/algos/transformer/base.py](d3rlpy/algos/transformer/base.py)
- [d3rlpy/algos/transformer/decision_transformer.py](d3rlpy/algos/transformer/decision_transformer.py)
- [d3rlpy/algos/transformer/torch/decision_transformer_impl.py](d3rlpy/algos/transformer/torch/decision_transformer_impl.py)
- [docs/references/algos.rst](docs/references/algos.rst)
- [docs/requirements.txt](docs/requirements.txt)

</details>



## Purpose and Scope

The Algorithm System is the core framework of d3rlpy that provides a unified interface for deep reinforcement learning algorithms. This system manages algorithm configuration, instantiation, training, and inference through a three-layer architecture: configuration classes, algorithm base classes, and PyTorch implementations.

This document covers the algorithm framework's architecture, base classes, and training interfaces. For specific algorithm implementations like SAC, CQL, and Decision Transformer, see [Algorithm Implementations](#5.3). For Q-learning specific details, see [Q-Learning Algorithms](#5.1). For transformer-based algorithms, see [Transformer Algorithms](#5.2).

## Architecture Overview

The Algorithm System follows a three-layer design pattern that separates configuration, algorithm logic, and PyTorch-specific implementation:

**Algorithm System Architecture**
```mermaid
graph TB
    subgraph "Configuration Layer"
        SACConfig["SACConfig"]
        CQLConfig["CQLConfig"]
        DTConfig["DecisionTransformerConfig"]
        BCQConfig["BCQConfig"]
    end
    
    subgraph "Algorithm Layer"
        QLearningAlgoBase["QLearningAlgoBase"]
        TransformerAlgoBase["TransformerAlgoBase"]
        LearnableBase["LearnableBase"]
    end
    
    subgraph "Implementation Layer"
        SACImpl["SACImpl"]
        CQLImpl["CQLImpl"]
        DTImpl["DecisionTransformerImpl"]
        BCQImpl["BCQImpl"]
        QLearningAlgoImplBase["QLearningAlgoImplBase"]
        TransformerAlgoImplBase["TransformerAlgoImplBase"]
        ImplBase["ImplBase"]
    end
    
    subgraph "PyTorch Components"
        Modules["Modules"]
        Policy["Policy"]
        QFunction["Q-Function"]
        Transformer["Transformer"]
        Optimizers["OptimizerWrapper"]
    end
    
    %% Configuration to Algorithm
    SACConfig -->|"create()"| QLearningAlgoBase
    CQLConfig -->|"create()"| QLearningAlgoBase
    DTConfig -->|"create()"| TransformerAlgoBase
    BCQConfig -->|"create()"| QLearningAlgoBase
    
    %% Algorithm inheritance
    QLearningAlgoBase --> LearnableBase
    TransformerAlgoBase --> LearnableBase
    
    %% Algorithm to Implementation
    QLearningAlgoBase -->|"inner_create_impl()"| SACImpl
    QLearningAlgoBase -->|"inner_create_impl()"| CQLImpl
    QLearningAlgoBase -->|"inner_create_impl()"| BCQImpl
    TransformerAlgoBase -->|"inner_create_impl()"| DTImpl
    
    %% Implementation inheritance
    SACImpl --> QLearningAlgoImplBase
    CQLImpl --> QLearningAlgoImplBase
    BCQImpl --> QLearningAlgoImplBase
    DTImpl --> TransformerAlgoImplBase
    QLearningAlgoImplBase --> ImplBase
    TransformerAlgoImplBase --> ImplBase
    
    %% Implementation to Components
    SACImpl --> Modules
    CQLImpl --> Modules
    DTImpl --> Modules
    BCQImpl --> Modules
    
    Modules --> Policy
    Modules --> QFunction
    Modules --> Transformer
    Modules --> Optimizers
```

Sources: [d3rlpy/algos/qlearning/base.py:163-166](), [d3rlpy/algos/transformer/base.py:208-211](), [d3rlpy/base.py](), [d3rlpy/algos/transformer/decision_transformer.py:28-29]()

## Configuration System

All algorithms use dataclass-based configuration objects that define hyperparameters and factory objects for creating neural network components. The configuration system provides type safety and serialization capabilities.

**Configuration Class Structure**
```mermaid
graph TD
    subgraph "Configuration Base Classes"
        LearnableConfig["LearnableConfig"]
        TransformerConfig["TransformerConfig"]
    end
    
    subgraph "Q-Learning Configs"
        SACConfig["SACConfig"]
        CQLConfig["CQLConfig"]
        BCQConfig["BCQConfig"]
        TD3Config["TD3Config"]
    end
    
    subgraph "Transformer Configs"
        DecisionTransformerConfig["DecisionTransformerConfig"]
        DiscreteDecisionTransformerConfig["DiscreteDecisionTransformerConfig"]
    end
    
    subgraph "Factory Components"
        EncoderFactory["EncoderFactory"]
        OptimizerFactory["OptimizerFactory"]
        QFunctionFactory["QFunctionFactory"]
    end
    
    %% Inheritance
    TransformerConfig --> LearnableConfig
    SACConfig --> LearnableConfig
    CQLConfig --> LearnableConfig
    BCQConfig --> LearnableConfig
    TD3Config --> LearnableConfig
    DecisionTransformerConfig --> TransformerConfig
    DiscreteDecisionTransformerConfig --> TransformerConfig
    
    %% Factory relationships
    SACConfig --> EncoderFactory
    SACConfig --> OptimizerFactory
    SACConfig --> QFunctionFactory
    DecisionTransformerConfig --> EncoderFactory
    DecisionTransformerConfig --> OptimizerFactory
```

### Configuration Usage Pattern

Configuration objects are instantiated with hyperparameters and then used to create algorithm instances:

| Step | Code Pattern | Description |
|------|-------------|------------|
| 1. Configure | `config = SACConfig(batch_size=256, learning_rate=3e-4)` | Set hyperparameters |
| 2. Create | `algo = config.create(device="cuda:0")` | Instantiate algorithm |
| 3. Build | `algo.build_with_dataset(dataset)` | Build neural networks |
| 4. Train | `algo.fit(dataset, n_steps=100000)` | Execute training |

Sources: [d3rlpy/algos/transformer/decision_transformer.py:28-84](), [d3rlpy/base.py](), [README.md:18-19]()

## Algorithm Base Classes

The algorithm layer provides two main base classes that define the core interfaces for different algorithm families:

### QLearningAlgoBase

`QLearningAlgoBase` provides the interface for value-based algorithms that learn Q-functions. It implements both offline and online training methods.

**Key Methods:**
- `predict(x)` - Returns greedy actions
- `predict_value(x, action)` - Returns Q-values
- `sample_action(x)` - Returns stochastic actions
- `fit(dataset)` - Offline training
- `fit_online(env, buffer)` - Online training with environment interaction

### TransformerAlgoBase

`TransformerAlgoBase` provides the interface for sequence modeling algorithms like Decision Transformer. It handles trajectory-based training and stateful inference.

**Key Methods:**
- `predict(inpt)` - Returns actions from transformer input
- `fit(dataset)` - Offline training on trajectories
- `as_stateful_wrapper(target_return)` - Creates stateful wrapper for evaluation

**Algorithm Interface Comparison**
```mermaid
graph TB
    subgraph "QLearningAlgoBase Interface"
        QPredictBest["predict(x) -> action"]
        QPredictValue["predict_value(x, action) -> value"]
        QSampleAction["sample_action(x) -> action"]
        QFitOffline["fit(dataset) -> metrics"]
        QFitOnline["fit_online(env, buffer) -> None"]
    end
    
    subgraph "TransformerAlgoBase Interface"
        TPredict["predict(inpt) -> action"]
        TFit["fit(dataset) -> None"]
        TWrapper["as_stateful_wrapper(target_return) -> wrapper"]
    end
    
    subgraph "Common LearnableBase Interface"
        SaveModel["save_model(path) -> None"]
        LoadModel["load_model(path) -> None"]
        SavePolicy["save_policy(path) -> None"]
        CreateImpl["create_impl(obs_shape, action_size) -> None"]
    end
    
    QPredictBest --> SaveModel
    QPredictValue --> SaveModel
    QSampleAction --> SaveModel
    QFitOffline --> SaveModel
    QFitOnline --> SaveModel
    
    TPredict --> SaveModel
    TFit --> SaveModel
    TWrapper --> SaveModel
```

Sources: [d3rlpy/algos/qlearning/base.py:163-166](), [d3rlpy/algos/transformer/base.py:208-211](), [d3rlpy/algos/qlearning/base.py:256-368](), [d3rlpy/algos/transformer/base.py:347-374]()

## Implementation Layer

The implementation layer contains PyTorch-specific code that performs the actual neural network operations. Each algorithm has a corresponding implementation class that inherits from either `QLearningAlgoImplBase` or `TransformerAlgoImplBase`.

### Implementation Responsibilities

| Component | Responsibility | Key Methods |
|-----------|---------------|-------------|
| `QLearningAlgoImplBase` | Q-learning computations | `inner_update()`, `inner_predict_best_action()` |
| `TransformerAlgoImplBase` | Transformer computations | `inner_update()`, `inner_predict()` |
| `Modules` | PyTorch module container | Neural networks and optimizers |
| `ImplBase` | Common implementation logic | Device management, module access |

### Training Data Flow

```mermaid
graph LR
    subgraph "Data Processing"
        Dataset["ReplayBuffer"]
        Batch["MiniBatch"]
        TorchBatch["TorchMiniBatch"]
    end
    
    subgraph "Algorithm Layer"
        Algo["QLearningAlgoBase"]
        Update["update()"]
    end
    
    subgraph "Implementation Layer"
        Impl["QLearningAlgoImplBase"]
        InnerUpdate["inner_update()"]
        ComputeLoss["compute_loss()"]
    end
    
    subgraph "PyTorch Components"
        Policy["Policy Network"]
        QFunc["Q-Function Network"]
        Optim["Optimizer"]
    end
    
    Dataset -->|"sample_transition_batch()"| Batch
    Batch -->|"TorchMiniBatch.from_batch()"| TorchBatch
    TorchBatch --> Algo
    Algo -->|"delegates to"| Update
    Update -->|"calls"| Impl
    Impl --> InnerUpdate
    InnerUpdate --> ComputeLoss
    ComputeLoss --> Policy
    ComputeLoss --> QFunc
    InnerUpdate --> Optim
```

Sources: [d3rlpy/algos/qlearning/base.py:65-108](), [d3rlpy/algos/transformer/base.py:49-68](), [d3rlpy/algos/qlearning/base.py:859-880](), [d3rlpy/torch_utility.py]()

## Training Interfaces

The Algorithm System provides two primary training interfaces:

### Offline Training

Offline training uses pre-collected datasets and implements the standard supervised learning loop:

```python
# Training interface pattern
algo.fit(
    dataset=replay_buffer,
    n_steps=1000000,
    n_steps_per_epoch=10000,
    evaluators={"environment": evaluator}
)
```

**Offline Training Flow**
```mermaid
graph TD
    FitMethod["fit(dataset, n_steps)"]
    SetupScalers["build_scalers_with_transition_picker()"]
    CreateImpl["create_impl(obs_shape, action_size)"]
    TrainingLoop["Training Loop"]
    SampleBatch["dataset.sample_transition_batch()"]
    UpdateParams["impl.update(batch)"]
    LogMetrics["logger.add_metric()"]
    Evaluate["evaluators[name](algo, dataset)"]
    SaveModel["logger.save_model()"]
    
    FitMethod --> SetupScalers
    SetupScalers --> CreateImpl
    CreateImpl --> TrainingLoop
    TrainingLoop --> SampleBatch
    SampleBatch --> UpdateParams
    UpdateParams --> LogMetrics
    LogMetrics --> Evaluate
    Evaluate --> SaveModel
    SaveModel --> TrainingLoop
```

### Online Training

Online training interacts with environments to collect experience while simultaneously learning:

```python
# Online training pattern
algo.fit_online(
    env=environment,
    buffer=replay_buffer,
    n_steps=1000000,
    update_interval=1
)
```

**Online Training Flow**
```mermaid
graph TD
    FitOnline["fit_online(env, buffer)"]
    ResetEnv["env.reset()"]
    ActionLoop["Environment Interaction Loop"]
    SampleAction["algo.sample_action(obs)"]
    StepEnv["env.step(action)"]
    StoreTransition["buffer.append(obs, action, reward)"]
    CheckUpdate["total_step % update_interval == 0"]
    SampleBatch["buffer.sample_transition_batch()"]
    UpdateParams["algo.update(batch)"]
    Evaluate["evaluate with eval_env"]
    
    FitOnline --> ResetEnv
    ResetEnv --> ActionLoop
    ActionLoop --> SampleAction
    SampleAction --> StepEnv
    StepEnv --> StoreTransition
    StoreTransition --> CheckUpdate
    CheckUpdate -->|"Yes"| SampleBatch
    CheckUpdate -->|"No"| ActionLoop
    SampleBatch --> UpdateParams
    UpdateParams --> Evaluate
    Evaluate --> ActionLoop
```

Sources: [d3rlpy/algos/qlearning/base.py:370-434](), [d3rlpy/algos/qlearning/base.py:592-777](), [d3rlpy/algos/transformer/base.py:376-509]()

## Algorithm Categories

The Algorithm System supports two main categories of algorithms, each with distinct characteristics:

### Q-Learning Algorithms

Q-learning algorithms learn value functions and are suitable for both offline and online training:

| Algorithm | Config Class | Implementation | Action Space |
|-----------|-------------|---------------|--------------|
| SAC | `SACConfig` | `SACImpl` | Continuous/Discrete |
| CQL | `CQLConfig` | `CQLImpl` | Continuous/Discrete |
| BCQ | `BCQConfig` | `BCQImpl` | Continuous/Discrete |
| TD3 | `TD3Config` | `TD3Impl` | Continuous |
| DQN | `DQNConfig` | `DQNImpl` | Discrete |

### Transformer Algorithms

Transformer algorithms model sequential decision-making and primarily support offline training:

| Algorithm | Config Class | Implementation | Action Space |
|-----------|-------------|---------------|--------------|
| Decision Transformer | `DecisionTransformerConfig` | `DecisionTransformerImpl` | Continuous |
| Discrete Decision Transformer | `DiscreteDecisionTransformerConfig` | `DiscreteDecisionTransformerImpl` | Discrete |

**Algorithm Category Characteristics**
```mermaid
graph TB
    subgraph "Q-Learning Characteristics"
        QTraining["Transition-based Training"]
        QOnline["Online Training Support"]
        QValue["Value Function Learning"]
        QGreedy["Greedy Action Selection"]
    end
    
    subgraph "Transformer Characteristics"
        TTraining["Trajectory-based Training"]
        TOffline["Offline Training Only"]
        TSequence["Sequence Modeling"]
        TStateful["Stateful Inference"]
    end
    
    subgraph "Common Features"
        ConfigBased["Configuration-based Setup"]
        ModelSaving["Model Serialization"]
        PolicyExport["Policy Export (TorchScript/ONNX)"]
        Evaluation["Evaluation Metrics"]
    end
    
    QTraining --> ConfigBased
    QOnline --> ConfigBased
    QValue --> ConfigBased
    QGreedy --> ConfigBased
    
    TTraining --> ConfigBased
    TOffline --> ConfigBased
    TSequence --> ConfigBased
    TStateful --> ConfigBased
    
    ConfigBased --> ModelSaving
    ModelSaving --> PolicyExport
    PolicyExport --> Evaluation
```

Sources: [docs/references/algos.rst:40-51](), [docs/references/algos.rst:353-462](), [d3rlpy/algos/transformer/decision_transformer.py:20-25](), [README.md:88-112]()

---

