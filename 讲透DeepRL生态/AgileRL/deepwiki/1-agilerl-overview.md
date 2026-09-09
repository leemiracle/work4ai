> 来源: [https://deepwiki.com/AgileRL/AgileRL/1-agilerl-overview](https://deepwiki.com/AgileRL/AgileRL/1-agilerl-overview)
> DeepWiki AgileRL/AgileRL | Last indexed: 25 June 2025 (03307c

# AgileRL Overview

  Relevant source files 
 - [README.md](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1)
 - [docs/api/algorithms/index.rst](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/api/algorithms/index.rst)
 - [docs/api/networks/index.rst](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/api/networks/index.rst)
 - [docs/get_started/index.rst](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/get_started/index.rst)
 - [docs/index.rst](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/index.rst)
 
  
## Purpose and Scope

 This document introduces AgileRL, its core concepts of evolutionary hyperparameter optimization for RL, and provides getting started examples. AgileRL is a Deep Reinforcement Learning library that introduces RLOps (MLOps for reinforcement learning) principles to streamline RL development and significantly reduce training time through automated hyperparameter optimization.

 This page covers the high-level architecture, core components, and explains how AgileRL's systems work together. For specific implementation details about algorithms, see [Reinforcement Learning Algorithms](https://deepwiki.com/AgileRL/AgileRL/2-reinforcement-learning-algorithms), for details about the evolutionary optimization process, see [Evolutionary Hyperparameter Optimization](https://deepwiki.com/AgileRL/AgileRL/4-evolutionary-hyperparameter-optimization), and for foundational base classes, see [Core Architecture](https://deepwiki.com/AgileRL/AgileRL/1.1-core-architecture).

 Sources: [README.md20-24](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L20-L24) [docs/index.rst28-32](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/index.rst#L28-L32)

 
## What is AgileRL?

 AgileRL is a reinforcement learning library designed to streamline the development and optimization of RL agents. Its distinguishing feature is the built-in evolutionary hyperparameter optimization (HPO) methodology, which has been demonstrated to reduce overall training times by automatically converging on optimal hyperparameters without requiring numerous separate training runs.

 The library supports a wide range of reinforcement learning paradigms:

 
 - Off-policy algorithms (DQN, Rainbow DQN, DDPG, TD3)
 - On-policy algorithms (PPO)
 - Multi-agent algorithms (MADDPG, MATD3, IPPO)
 - Offline algorithms (CQL, ILQL)
 - Contextual multi-armed bandits (NeuralUCB, NeuralTS)
 - Large language model fine-tuning (GRPO)
 
 Sources: [README.md20-24](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L20-L24) [README.md83-103](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L83-L103)

 
## Core Architecture

 
### AgileRL System Architecture

 
```

```

 The diagram illustrates AgileRL's complete system architecture, showing how users interact with training functions that orchestrate algorithm implementations, evolutionary optimization, and supporting infrastructure. The system is built around the `create_population` function that creates evolvable agents, which are then trained using specialized training functions like `train_off_policy` and `train_on_policy`.

 Sources: [README.md159-188](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L159-L188) [README.md189-218](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L189-L218)

 
### Base Classes

 AgileRL's architecture is built around a few key base classes:

 
 - **EvolvableAlgorithm**: The root class that defines the interface for evolvable components, checkpoint management, and evolutionary operations.
 - **RLAlgorithm**: Extends `EvolvableAlgorithm` for single-agent reinforcement learning, handling observation/action space processing.
 - **MultiAgentRLAlgorithm**: Extends `EvolvableAlgorithm` for multi-agent environments, managing multiple agents and their interactions.
 
 These base classes define methods for:

 
 - Creating agent populations
 - Retrieving and processing actions
 - Learning from experiences
 - Saving and loading checkpoints
 - Creating clones for evolution
 
 Sources: [agilerl/algorithms/core/base.py182-1163](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/algorithms/core/base.py#L182-L1163)

 
### Network Architecture and Algorithm Integration

 
```

```

 This diagram shows the complete hierarchy from base classes to specific algorithm implementations. All components inherit from `EvolvableModule`, which provides mutation capabilities. The `EvolvableAlgorithm` base class is extended by `RLAlgorithm` for single-agent and `MultiAgentRLAlgorithm` for multi-agent scenarios. Each algorithm uses appropriate network architectures that can evolve during training.

 Sources: [docs/api/networks/index.rst4-11](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/api/networks/index.rst#L4-L11) [docs/api/algorithms/index.rst17-155](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/api/algorithms/index.rst#L17-L155)

 
## Evolutionary Hyperparameter Optimization

 AgileRL's key innovation is its evolutionary approach to hyperparameter optimization, which enables 10x faster optimization compared to traditional methods.

 
### Evolutionary Hyperparameter Optimization (EvoHPO) Flow

 
```

```

 The evolutionary process begins with `create_population` generating a diverse set of agents. During training, agents interact with environments and learn from experiences. The `TournamentSelection` class identifies high-performing agents, and the `Mutations` class applies various mutation operators to create new variants. This process continues until convergence, automatically discovering optimal hyperparameters without requiring separate optimization runs.

 Sources: [README.md189-218](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L189-L218) [README.md133-143](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L133-L143)

 
### Mutation Parameters

 AgileRL supports several types of mutations:

 
| Mutation Type | Description |
|---|---|
| No Mutation | Agent is preserved without changes |
| Architecture Mutation | Network architecture is modified |
| New Layer Mutation | New layers are added to the network |
| Parameters Mutation | Network weights are perturbed |
| Activation Mutation | Activation functions are changed |
| RL Hyperparameter Mutation | Learning hyperparameters are modified |

 These mutations are controlled by relative probabilities defined in the configuration, allowing fine-grained control over the evolutionary process.

 Sources: [README.md133-143](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L133-L143)

 
## Algorithm Ecosystem

 AgileRL implements a diverse range of reinforcement learning algorithms across different paradigms.

 
### Algorithm Categories and Action Space Compatibility

 
```

```

 The following tables summarize algorithm compatibility with different action spaces:

 
#### Single-Agent Algorithms

 
| Algorithm | Discrete | Continuous | MultiDiscrete | MultiBinary |
|---|---|---|---|---|
| DQN | ✓ |  |  |  |
| Rainbow DQN | ✓ |  |  |  |
| DDPG |  | ✓ |  |  |
| TD3 |  | ✓ |  |  |
| PPO | ✓ | ✓ | ✓ | ✓ |
| CQL | ✓ | ✓ |  |  |
| ILQL | ✓ |  |  |  |

 
#### Multi-Agent Algorithms

 
| Algorithm | Discrete | Continuous | MultiDiscrete | MultiBinary |
|---|---|---|---|---|
| MADDPG |  | ✓ |  |  |
| MATD3 |  | ✓ |  |  |
| IPPO | ✓ | ✓ | ✓ | ✓ |

 Sources: [docs/api/algorithms/index.rst36-85](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/api/algorithms/index.rst#L36-L85) [docs/api/algorithms/index.rst100-129](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/api/algorithms/index.rst#L100-L129) [README.md83-103](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L83-L103)

 
## Training System

 AgileRL provides specialized training functions for different reinforcement learning paradigms, each integrating the evolutionary optimization process.

 
### Training System Functions

 
```

```

 AgileRL provides specialized training functions for each RL paradigm. All training functions share common evolutionary components: `create_population` for agent initialization, `TournamentSelection` for parent selection, and `Mutations` for generating variants. The `make_vect_envs` utility creates vectorized environments for efficient data collection.

 Sources: [README.md219-240](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L219-L240) [README.md162-188](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L162-L188)

 
## Getting Started

 AgileRL follows a three-step pattern for evolutionary reinforcement learning:

 
### Step 1: Configure Hyperparameters and Create Population

 Define configuration dictionaries and create a population of agents with diverse hyperparameters:

 
```

```

 
### Step 2: Initialize Evolutionary Components

 Create the components that enable evolutionary optimization:

 
```

```

 
### Step 3: Train with Evolutionary Optimization

 Use the appropriate training function for your RL paradigm:

 
```

```

 This approach eliminates the need for separate hyperparameter optimization runs, as the evolutionary process automatically discovers optimal settings during training.

 Sources: [README.md107-131](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L107-L131) [README.md159-241](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L159-L241)

 
## Summary

 AgileRL is a comprehensive reinforcement learning library that introduces evolutionary hyperparameter optimization to significantly reduce training time. Its modular architecture supports a wide range of RL paradigms and algorithms, with specialized components for different tasks.

 The key innovation is the evolutionary approach that allows hyperparameters to be optimized during training, eliminating the need for separate optimization runs. This is achieved through a population of agents that share experiences while evolving their hyperparameters through tournament selection and mutation.

 By leveraging this approach, AgileRL provides a more efficient and streamlined way to develop reinforcement learning solutions, addressing one of the major pain points in RL research and application - the time-consuming process of hyperparameter tuning.

 Sources: [README.md20-29](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L20-L29) [README.md54-62](https://github.com/AgileRL/AgileRL/blob/03307c7b/README.md?plain=1#L54-L62)
