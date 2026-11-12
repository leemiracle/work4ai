<!-- source: DeepWiki mcp.deepwiki.com · repo takuseno/d3rlpy · page 12 API Reference · fetched 2026-10-30 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/references/dataset.rst](docs/references/dataset.rst)
- [docs/references/datasets.rst](docs/references/datasets.rst)
- [docs/references/index.rst](docs/references/index.rst)
- [docs/references/off_policy_evaluation.rst](docs/references/off_policy_evaluation.rst)
- [docs/tips.rst](docs/tips.rst)

</details>



This page provides comprehensive API documentation for all public classes, methods, and functions in d3rlpy. The API is organized by functional area to help you quickly locate the components you need for your reinforcement learning projects.

For algorithm usage examples and tutorials, see [Quick Start Tutorial](#3). For architectural concepts behind these APIs, see [Core Architecture](#4) and [Algorithm System](#5). For data handling patterns, see [Data Management](#6).

## API Organization

The d3rlpy API is structured around several core modules that correspond to different aspects of reinforcement learning:

```mermaid
graph TB
    subgraph "Core Algorithm APIs"
        ALGOS["d3rlpy.algos<br/>Algorithm Configurations"]
        MODELS["d3rlpy.models<br/>Neural Network Components"]
        OPTIM["d3rlpy.optimizers<br/>Optimizer Factories"]
    end
    
    subgraph "Data Management APIs"
        DATASET["d3rlpy.dataset<br/>Replay Buffers & Transitions"]
        DATASETS["d3rlpy.datasets<br/>Dataset Loading Functions"]
        PREPROC["d3rlpy.preprocessing<br/>Data Scalers"]
    end
    
    subgraph "Evaluation & Training APIs"
        METRICS["d3rlpy.metrics<br/>Evaluation Metrics"]
        OPE["d3rlpy.ope<br/>Off-Policy Evaluation"]
        LOGGING["d3rlpy.logging<br/>Experiment Tracking"]
    end
    
    subgraph "Supporting APIs"
        ONLINE["d3rlpy.online<br/>Online Training"]
        ENVS["d3rlpy.envs<br/>Environment Utilities"]
        CLI["d3rlpy.cli<br/>Command Line Interface"]
    end
    
    ALGOS --> MODELS
    ALGOS --> OPTIM
    ALGOS --> DATASET
    DATASET --> DATASETS
    DATASET --> PREPROC
    ALGOS --> METRICS
    METRICS --> OPE
    ALGOS --> LOGGING
```

**Sources:** [docs/references/index.rst:7-21]()

## Core Algorithm API

The algorithm API forms the heart of d3rlpy, providing configuration-based interfaces for all supported reinforcement learning algorithms.

### Algorithm Configuration Pattern

All algorithms in d3rlpy follow a consistent configuration-creation pattern:

```mermaid
graph LR
    CONFIG["AlgorithmConfig<br/>(e.g., SACConfig)"]
    LEARNABLE["LearnableBase<br/>(e.g., SAC)"]
    IMPL["ImplBase<br/>(e.g., SACImpl)"]
    MODULES["Modules<br/>(PyTorch Components)"]
    
    CONFIG -->|"create()"| LEARNABLE
    LEARNABLE -->|"inner_create_impl()"| IMPL
    IMPL -->|"build()"| MODULES
    
    LEARNABLE -->|"fit()"| TRAINING["Training Methods"]
    LEARNABLE -->|"predict()"| INFERENCE["Inference Methods"]
```

**Sources:** [docs/references/index.rst:10]()

### Q-Learning Algorithm Configurations

The `d3rlpy.algos` module provides configuration classes for Q-learning based algorithms:

| Algorithm | Configuration Class | Description |
|-----------|-------------------|-------------|
| DQN | `DQNConfig` | Deep Q-Network for discrete actions |
| CQL | `CQLConfig` | Conservative Q-Learning for offline RL |
| SAC | `SACConfig` | Soft Actor-Critic for continuous control |
| BEAR | `BEARConfig` | Bootstrapping Error Accumulation Reduction |
| BCQ | `BCQConfig` | Batch-Constrained Q-Learning |
| AWR | `AWRConfig` | Advantage-Weighted Regression |
| AWAC | `AWACConfig` | Advantage-Weighted Actor-Critic |
| TD3 | `TD3Config` | Twin Delayed Deep Deterministic Policy Gradient |
| TD3+BC | `TD3PlusBCConfig` | TD3 with Behavior Cloning |

**Sources:** [docs/references/index.rst:10]()

### Transformer Algorithm Configurations

For sequence modeling approaches:

| Algorithm | Configuration Class | Description |
|-----------|-------------------|-------------|
| Decision Transformer | `DecisionTransformerConfig` | Sequence modeling for RL |
| Trajectory Transformer | `TrajectedTransformerConfig` | Trajectory-based sequence modeling |

**Sources:** [docs/references/index.rst:10]()

### Algorithm Base Classes

The inheritance hierarchy for algorithm implementations:

```mermaid
graph TB
    LEARNABLE["LearnableBase<br/>Generic algorithm interface"]
    QL_BASE["QLearningAlgoBase<br/>Q-learning algorithms"]
    TRANS_BASE["TransformerAlgoBase<br/>Transformer algorithms"]
    
    LEARNABLE --> QL_BASE
    LEARNABLE --> TRANS_BASE
    
    subgraph "Q-Learning Algorithms"
        SAC["SAC"]
        CQL["CQL"]
        DQN["DQN"]
        BCQ["BCQ"]
        BEAR["BEAR"]
    end
    
    subgraph "Transformer Algorithms"
        DT["DecisionTransformer"]
        TT["TrajectoryTransformer"]
    end
    
    QL_BASE --> SAC
    QL_BASE --> CQL
    QL_BASE --> DQN
    QL_BASE --> BCQ
    QL_BASE --> BEAR
    
    TRANS_BASE --> DT
    TRANS_BASE --> TT
```

**Sources:** [docs/references/index.rst:10]()

## Data Management API

### Dataset Loading Functions

The `d3rlpy.datasets` module provides functions to load standard RL datasets:

| Function | Purpose | Return Type |
|----------|---------|-------------|
| `get_d4rl()` | Load D4RL datasets | `(ReplayBuffer, gym.Env)` |
| `get_atari()` | Load Atari datasets | `(ReplayBuffer, gym.Env)` |
| `get_minari()` | Load Minari datasets | `(ReplayBuffer, gym.Env)` |
| `get_cartpole()` | Load CartPole dataset | `(ReplayBuffer, gym.Env)` |
| `get_pendulum()` | Load Pendulum dataset | `(ReplayBuffer, gym.Env)` |
| `get_dataset()` | Load custom datasets | `(ReplayBuffer, gym.Env)` |

**Sources:** [docs/references/datasets.rst:9-20]()

### Replay Buffer System

The replay buffer API follows a modular design with interchangeable components:

```mermaid
graph TB
    subgraph "Main Interfaces"
        RB["ReplayBuffer<br/>Main interface"]
        MRB["MixedReplayBuffer<br/>Multi-source buffer"]
        MDPDataset["MDPDataset<br/>Legacy shortcut"]
    end
    
    subgraph "Buffer Components"
        INFINITE["InfiniteBuffer<br/>Unlimited storage"]
        FIFO["FIFOBuffer<br/>Fixed-size FIFO"]
        PROTOCOL["BufferProtocol<br/>Interface"]
    end
    
    subgraph "Sampling Components"
        BASIC_PICKER["BasicTransitionPicker<br/>Standard transitions"]
        FRAME_PICKER["FrameStackTransitionPicker<br/>Frame stacking"]
        MULTI_PICKER["MultiStepTransitionPicker<br/>N-step returns"]
        SPARSE_PICKER["SparseRewardTransitionPicker<br/>Sparse rewards"]
    end
    
    subgraph "Trajectory Components"
        BASIC_SLICER["BasicTrajectorySlicer<br/>Standard trajectories"]
        FRAME_SLICER["FrameStackTrajectorySlicer<br/>Frame stacked trajectories"]
    end
    
    RB --> INFINITE
    RB --> FIFO
    RB --> BASIC_PICKER
    RB --> FRAME_PICKER
    RB --> MULTI_PICKER
    RB --> SPARSE_PICKER
    RB --> BASIC_SLICER
    RB --> FRAME_SLICER
    
    INFINITE -.-> PROTOCOL
    FIFO -.-> PROTOCOL
```

**Sources:** [docs/references/dataset.rst:69-142](), [docs/references/dataset.rst:144-156](), [docs/references/dataset.rst:159-197](), [docs/references/dataset.rst:199-268]()

### Data Structures

Core data structures for representing RL experiences:

| Class | Purpose | Key Fields |
|-------|---------|------------|
| `Episode` | Single episode container | `observations`, `actions`, `rewards`, `terminated` |
| `Transition` | Single transition | `observation`, `action`, `reward`, `next_observation`, `terminal` |
| `PartialTrajectory` | Trajectory slice | `observations`, `actions`, `returns_to_go`, `timesteps`, `masks` |
| `TransitionMiniBatch` | Batch of transitions | Batched transition data |
| `TrajectoryMiniBatch` | Batch of trajectories | Batched trajectory data |

**Sources:** [docs/references/dataset.rst:59-60]()

## Model Components API

### Encoder Factories

The `d3rlpy.models` module provides encoder factories for feature extraction:

```mermaid
graph TB
    subgraph "Encoder Factory Interfaces"
        OBS_ENC["ObservationEncoderFactory<br/>Observation processing"]
        ACT_ENC["ActionEncoderFactory<br/>Action processing"]
    end
    
    subgraph "Concrete Implementations"
        DEFAULT["DefaultEncoderFactory<br/>MLP/CNN encoder"]
        PIXEL["PixelEncoderFactory<br/>CNN for images"]
        VECTOR["VectorEncoderFactory<br/>MLP for vectors"]
    end
    
    subgraph "Configuration Options"
        ACTIVATION["activation: str<br/>Activation function"]
        BATCH_NORM["use_batch_norm: bool<br/>Batch normalization"]
        DROPOUT["dropout_rate: float<br/>Dropout rate"]
        LAYER_NORM["use_layer_norm: bool<br/>Layer normalization"]
    end
    
    OBS_ENC --> DEFAULT
    OBS_ENC --> PIXEL
    OBS_ENC --> VECTOR
    
    DEFAULT --> ACTIVATION
    DEFAULT --> BATCH_NORM
    DEFAULT --> DROPOUT
    DEFAULT --> LAYER_NORM
```

**Sources:** [docs/references/index.rst:16](), [docs/tips.rst:65-78]()

### Q-Function Factories

Q-function architectures for value estimation:

| Factory Class | Architecture | Use Case |
|---------------|-------------|----------|
| `MeanQFunctionFactory` | Standard Q-network | Basic value estimation |
| `QRQFunctionFactory` | Quantile Regression | Distributional RL |
| `IQNQFunctionFactory` | Implicit Quantile Networks | Advanced distributional RL |
| `FQFQFunctionFactory` | Fully Parameterized Quantile Function | State-of-the-art distributional RL |

**Sources:** [docs/references/index.rst:11](), [docs/tips.rst:69]()

### Policy Architectures

Policy network implementations:

| Class | Algorithm Family | Action Space |
|-------|-----------------|--------------|
| `DeterministicPolicy` | DDPG, TD3 | Continuous |
| `StochasticPolicy` | SAC | Continuous |
| `CategoricalPolicy` | DQN variants | Discrete |
| `SquashedNormalPolicy` | SAC variants | Continuous with bounds |

**Sources:** [docs/references/index.rst:16]()

## Preprocessing API

### Scaler System

The `d3rlpy.preprocessing` module provides data normalization:

```mermaid
graph LR
    subgraph "Scaler Types"
        OBS_SCALER["ObservationScaler<br/>Normalize observations"]
        ACT_SCALER["ActionScaler<br/>Normalize actions"]
        REW_SCALER["RewardScaler<br/>Normalize rewards"]
    end
    
    subgraph "Observation Scalers"
        STANDARD["StandardObservationScaler<br/>Zero mean, unit variance"]
        MINMAX["MinMaxObservationScaler<br/>Min-max normalization"]
        PIXEL["PixelObservationScaler<br/>Divide by 255"]
    end
    
    subgraph "Action Scalers"
        MINMAX_ACT["MinMaxActionScaler<br/>Min-max for actions"]
    end
    
    subgraph "Reward Scalers"
        STANDARD_REW["StandardRewardScaler<br/>Standardize rewards"]
        MINMAX_REW["MinMaxRewardScaler<br/>Min-max for rewards"]
    end
    
    OBS_SCALER --> STANDARD
    OBS_SCALER --> MINMAX
    OBS_SCALER --> PIXEL
    
    ACT_SCALER --> MINMAX_ACT
    REW_SCALER --> STANDARD_REW
    REW_SCALER --> MINMAX_REW
```

**Sources:** [docs/references/index.rst:14](), [docs/tips.rst:50]()

## Metrics and Evaluation API

### Evaluation Metrics

The `d3rlpy.metrics` module provides comprehensive evaluation tools:

| Metric Category | Classes | Purpose |
|----------------|---------|---------|
| Environment Evaluation | `EnvironmentEvaluator` | Test in actual environment |
| Value Estimation | `InitialStateValueEstimationEvaluator` | Estimate state values |
| Policy Evaluation | `SoftOPCEvaluator` | Off-policy confidence intervals |
| Scoring Functions | `scorer` decorators | Custom evaluation metrics |

**Sources:** [docs/references/index.rst:17](), [docs/references/off_policy_evaluation.rst:26-29]()

### Off-Policy Evaluation

The `d3rlpy.ope` module provides methods to evaluate policies without environment interaction:

```mermaid
graph TB
    subgraph "OPE Algorithms"
        FQE["FQE<br/>Fitted Q Evaluation"]
        DISCRETE_FQE["DiscreteFQE<br/>Discrete action FQE"]
    end
    
    subgraph "Input Requirements"
        POLICY["Trained Policy<br/>Algorithm to evaluate"]
        DATASET["Evaluation Dataset<br/>Offline data"]
        CONFIG["OPE Configuration<br/>Hyperparameters"]
    end
    
    subgraph "Evaluation Outputs"
        VALUE_EST["Value Estimates<br/>Policy performance"]
        CONFIDENCE["Confidence Intervals<br/>Uncertainty bounds"]
        METRICS["OPE Metrics<br/>Evaluation scores"]
    end
    
    POLICY --> FQE
    DATASET --> FQE
    CONFIG --> FQE
    
    POLICY --> DISCRETE_FQE
    DATASET --> DISCRETE_FQE
    CONFIG --> DISCRETE_FQE
    
    FQE --> VALUE_EST
    FQE --> CONFIDENCE
    FQE --> METRICS
    
    DISCRETE_FQE --> VALUE_EST
    DISCRETE_FQE --> CONFIDENCE
    DISCRETE_FQE --> METRICS
```

**Sources:** [docs/references/off_policy_evaluation.rst:37-51]()

## Logging API

### Experiment Tracking

The `d3rlpy.logging` module provides adapters for popular experiment tracking tools:

| Adapter Class | Platform | Features |
|---------------|----------|----------|
| `FileAdapterFactory` | Local files | CSV/JSON logging |
| `TensorBoardAdapterFactory` | TensorBoard | Scalar/histogram tracking |  
| `WandbAdapterFactory` | Weights & Biases | Cloud-based tracking |

**Sources:** [docs/references/index.rst:19]()

## Utilities and CLI API

### Environment Utilities

The `d3rlpy.envs` module provides environment management functions:

| Function | Purpose |
|----------|---------|
| `seed_env()` | Set environment random seed |
| `AsyncBatchEnv` | Parallel environment execution |

**Sources:** [docs/tips.rst:21]()

### Command Line Interface

The `d3rlpy.cli` module provides command-line tools:

| Command | Purpose |
|---------|---------|
| `d3rlpy plot` | Generate training plots |
| `d3rlpy export` | Model format conversion |
| `d3rlpy eval` | Policy evaluation |

**Sources:** [docs/references/index.rst:20]()

### Core Utilities

Top-level utility functions:

| Function | Purpose |
|----------|---------|
| `seed()` | Set global random seeds |
| `load_learnable()` | Load saved algorithms |
| `save_learnable()` | Save algorithm state |

**Sources:** [docs/tips.rst:17](), [docs/references/off_policy_evaluation.rst:14]()