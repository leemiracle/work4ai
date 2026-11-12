> 来源: [https://deepwiki.com/takuseno/d3rlpy/5-algorithm-system](https://deepwiki.com/takuseno/d3rlpy/5-algorithm-system)
> DeepWiki takuseno/d3rlpy | Last indexed: 25 June 2025 (4f0956

# Algorithm System

  Relevant source files 
 - [README.md](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1)
 - [ROADMAP.md](https://github.com/takuseno/d3rlpy/blob/4f0956ba/ROADMAP.md?plain=1)
 - [d3rlpy/algos/__init__.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/__init__.py)
 - [d3rlpy/algos/qlearning/base.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/qlearning/base.py)
 - [d3rlpy/algos/transformer/base.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/base.py)
 - [d3rlpy/algos/transformer/decision_transformer.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/decision_transformer.py)
 - [d3rlpy/algos/transformer/torch/decision_transformer_impl.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/torch/decision_transformer_impl.py)
 - [docs/references/algos.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst)
 - [docs/requirements.txt](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/requirements.txt)
 
  
## Purpose and Scope

 The Algorithm System is the core framework of d3rlpy that provides a unified interface for deep reinforcement learning algorithms. This system manages algorithm configuration, instantiation, training, and inference through a three-layer architecture: configuration classes, algorithm base classes, and PyTorch implementations.

 This document covers the algorithm framework's architecture, base classes, and training interfaces. For specific algorithm implementations like SAC, CQL, and Decision Transformer, see [Algorithm Implementations](https://deepwiki.com/takuseno/d3rlpy/5.3-algorithm-implementations). For Q-learning specific details, see [Q-Learning Algorithms](https://deepwiki.com/takuseno/d3rlpy/5.1-q-learning-algorithms). For transformer-based algorithms, see [Transformer Algorithms](https://deepwiki.com/takuseno/d3rlpy/5.2-transformer-algorithms).

 
## Architecture Overview

 The Algorithm System follows a three-layer design pattern that separates configuration, algorithm logic, and PyTorch-specific implementation:

 **Algorithm System Architecture**

 
```

```

 Sources: [d3rlpy/algos/qlearning/base.py163-166](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/qlearning/base.py#L163-L166) [d3rlpy/algos/transformer/base.py208-211](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/base.py#L208-L211) [d3rlpy/base.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py) [d3rlpy/algos/transformer/decision_transformer.py28-29](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/decision_transformer.py#L28-L29)

 
## Configuration System

 All algorithms use dataclass-based configuration objects that define hyperparameters and factory objects for creating neural network components. The configuration system provides type safety and serialization capabilities.

 **Configuration Class Structure**

 
```

```

 
### Configuration Usage Pattern

 Configuration objects are instantiated with hyperparameters and then used to create algorithm instances:

 
| Step | Code Pattern | Description |
|---|---|---|
| 1. Configure | config = SACConfig(batch_size=256, learning_rate=3e-4) | Set hyperparameters |
| 2. Create | algo = config.create(device="cuda:0") | Instantiate algorithm |
| 3. Build | algo.build_with_dataset(dataset) | Build neural networks |
| 4. Train | algo.fit(dataset, n_steps=100000) | Execute training |

 Sources: [d3rlpy/algos/transformer/decision_transformer.py28-84](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/decision_transformer.py#L28-L84) [d3rlpy/base.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py) [README.md18-19](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L18-L19)

 
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

 
```

```

 Sources: [d3rlpy/algos/qlearning/base.py163-166](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/qlearning/base.py#L163-L166) [d3rlpy/algos/transformer/base.py208-211](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/base.py#L208-L211) [d3rlpy/algos/qlearning/base.py256-368](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/qlearning/base.py#L256-L368) [d3rlpy/algos/transformer/base.py347-374](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/base.py#L347-L374)

 
## Implementation Layer

 The implementation layer contains PyTorch-specific code that performs the actual neural network operations. Each algorithm has a corresponding implementation class that inherits from either `QLearningAlgoImplBase` or `TransformerAlgoImplBase`.

 
### Implementation Responsibilities

 
| Component | Responsibility | Key Methods |
|---|---|---|
| QLearningAlgoImplBase | Q-learning computations | inner_update(), inner_predict_best_action() |
| TransformerAlgoImplBase | Transformer computations | inner_update(), inner_predict() |
| Modules | PyTorch module container | Neural networks and optimizers |
| ImplBase | Common implementation logic | Device management, module access |

 
### Training Data Flow

 
```

```

 Sources: [d3rlpy/algos/qlearning/base.py65-108](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/qlearning/base.py#L65-L108) [d3rlpy/algos/transformer/base.py49-68](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/base.py#L49-L68) [d3rlpy/algos/qlearning/base.py859-880](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/qlearning/base.py#L859-L880) [d3rlpy/torch_utility.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py)

 
## Training Interfaces

 The Algorithm System provides two primary training interfaces:

 
### Offline Training

 Offline training uses pre-collected datasets and implements the standard supervised learning loop:

 
```

```

 **Offline Training Flow**

 
```

```

 
### Online Training

 Online training interacts with environments to collect experience while simultaneously learning:

 
```

```

 **Online Training Flow**

 
```

```

 Sources: [d3rlpy/algos/qlearning/base.py370-434](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/qlearning/base.py#L370-L434) [d3rlpy/algos/qlearning/base.py592-777](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/qlearning/base.py#L592-L777) [d3rlpy/algos/transformer/base.py376-509](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/base.py#L376-L509)

 
## Algorithm Categories

 The Algorithm System supports two main categories of algorithms, each with distinct characteristics:

 
### Q-Learning Algorithms

 Q-learning algorithms learn value functions and are suitable for both offline and online training:

 
| Algorithm | Config Class | Implementation | Action Space |
|---|---|---|---|
| SAC | SACConfig | SACImpl | Continuous/Discrete |
| CQL | CQLConfig | CQLImpl | Continuous/Discrete |
| BCQ | BCQConfig | BCQImpl | Continuous/Discrete |
| TD3 | TD3Config | TD3Impl | Continuous |
| DQN | DQNConfig | DQNImpl | Discrete |

 
### Transformer Algorithms

 Transformer algorithms model sequential decision-making and primarily support offline training:

 
| Algorithm | Config Class | Implementation | Action Space |
|---|---|---|---|
| Decision Transformer | DecisionTransformerConfig | DecisionTransformerImpl | Continuous |
| Discrete Decision Transformer | DiscreteDecisionTransformerConfig | DiscreteDecisionTransformerImpl | Discrete |

 **Algorithm Category Characteristics**

 
```

```

 Sources: [docs/references/algos.rst40-51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst#L40-L51) [docs/references/algos.rst353-462](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst#L353-L462) [d3rlpy/algos/transformer/decision_transformer.py20-25](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/transformer/decision_transformer.py#L20-L25) [README.md88-112](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L88-L112)
