> 来源: [https://deepwiki.com/thu-ml/tianshou/1-overview](https://deepwiki.com/thu-ml/tianshou/1-overview)
> DeepWiki thu-ml/tianshou | Last indexed: 19 April 2025 (90846f

# Overview

  Relevant source files 
 - [README.md](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1)
 - [docs/index.rst](https://github.com/thu-ml/tianshou/blob/90846f6b/docs/index.rst)
 - [examples/atari/README.md](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/README.md?plain=1)
 - [tianshou/policy/__init__.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/__init__.py)
 
  This document provides an introduction to Tianshou, a reinforcement learning (RL) library based on pure PyTorch and Gymnasium. It covers the core architecture, key components, and main features of the framework.

 
## Purpose and Scope

 Tianshou ([天授](https://baike.baidu.com/item/%E5%A4%A9%E6%8E%88)) is a high-performance reinforcement learning library designed for both researchers and practitioners. Its main objectives are:

 
 - To provide modular, flexible, and type-safe low-level interfaces for algorithm developers
 - To offer convenient high-level interfaces for building RL applications
 - To support a broad range of RL paradigms including online (on- and off-policy), offline, multi-agent, and model-based reinforcement learning
 
 Unlike other reinforcement learning libraries that may have complex codebases or unfriendly APIs, Tianshou focuses on enabling concise implementations without sacrificing flexibility or performance.

 Sources: [README.md9-21](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1#L9-L21)

 
## System Architecture

 
### High-Level Architecture Overview

 
```

```

 Sources: [README.md10-19](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1#L10-L19) [tianshou/policy/__init__.py1-67](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/__init__.py#L1-L67)

 
### Data Flow Architecture

 
```

```

 Sources: [README.md185-196](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1#L185-L196)

 
## Core Components

 
### 1. Data Handling System

 This system manages the collection, storage, and processing of interaction data between agents and environments.

 
 - **Batch** (`tianshou.data.Batch`): A flexible container for heterogeneous data (observations, actions, rewards)
 - **ReplayBuffer** (`tianshou.data.ReplayBuffer`): Stores and samples experience tuples for off-policy learning
 - **Collector** (`tianshou.data.Collector`): Mediates interaction between policy and environment, collecting experiences
 
 For more details on the data handling system, see [Data Handling System](https://deepwiki.com/thu-ml/tianshou/2-data-handling-system).

 
### 2. Policy Framework

 The policy framework defines the interfaces and implementations for RL algorithms.

 
 - **BasePolicy** (`tianshou.policy.BasePolicy`): Abstract class defining the interface for all policies
 - **Algorithm Implementations**: Various policy implementations like DQN, PPO, SAC, etc.
 - **Multi-Agent Support**: `MultiAgentPolicyManager` for managing multiple policies in MARL settings
 
 The policy interface consists of these key methods:

 
 - `__init__`: Initialize the policy
 - `forward`: Compute actions based on observations
 - `process_buffer`: Process initial buffer (for offline learning)
 - `process_fn`: Preprocess data from the replay buffer
 - `learn`: Learn from a batch of data
 - `post_process_fn`: Update replay buffer from the learning process
 - `update`: Main interface for training (`process_fn -> learn -> post_process_fn`)
 
 For more details on policies and algorithms, see [Policy Framework](https://deepwiki.com/thu-ml/tianshou/3-policy-framework).

 Sources: [README.md185-196](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1#L185-L196) [tianshou/policy/__init__.py1-67](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/__init__.py#L1-L67)

 
### 3. Environment System

 This system handles the interaction with environments and provides utilities for parallel environment execution.

 
 - **BaseVectorEnv** (`tianshou.env.BaseVectorEnv`): Enables parallel environment execution
 - **Environment Workers**: Different implementations for managing parallelized environments
 - **Environment Wrappers**: For observation normalization and other transformations
 
 For more details on the environment system, see [Environment System](https://deepwiki.com/thu-ml/tianshou/4-environment-system).

 
### 4. Trainer System

 The trainer system manages the training process for different types of reinforcement learning algorithms.

 
 - **OnpolicyTrainer**: For training on-policy algorithms like PPO and A2C
 - **OffpolicyTrainer**: For training off-policy algorithms like DQN, SAC, and DDPG
 
 For more details on the trainer system, see [Trainer System](https://deepwiki.com/thu-ml/tianshou/5-trainer-system).

 
### 5. High-Level API

 The high-level API provides a simplified interface for experiment setup and execution.

 
 - **Experiment Framework**: Defines the experiment workflow
 - **ExperimentBuilder**: Builder pattern for constructing experiments
 - **Agent and Environment Factories**: For creating agents and environments
 
 For more details on the high-level API, see [High-Level API](https://deepwiki.com/thu-ml/tianshou/6-high-level-api).

 Sources: [README.md60-74](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1#L60-L74) [README.md200-205](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1#L200-L205)

 
## Supported Algorithms

 Tianshou implements a wide range of reinforcement learning algorithms:

 
| Category | Algorithms |
|---|---|
| Value-based | DQN, Double DQN, Dueling DQN, Branching DQN, C51, Rainbow, QRDQN, IQN, FQF |
| Policy-based | Policy Gradient (PG), Natural Policy Gradient (NPG), Advantage Actor-Critic (A2C), Trust Region Policy Optimization (TRPO), Proximal Policy Optimization (PPO) |
| Actor-critic | Deep Deterministic Policy Gradient (DDPG), Twin Delayed DDPG (TD3), Soft Actor-Critic (SAC), Randomized Ensembled Double Q-Learning (REDQ), Discrete SAC |
| Imitation learning | Vanilla Imitation Learning, BCQ, CQL, TD3+BC, Discrete BCQ, Discrete CQL, Discrete CRR, GAIL |
| Model-based | Posterior Sampling Reinforcement Learning (PSRL), Intrinsic Curiosity Module (ICM) |
| Other techniques | Prioritized Experience Replay (PER), Generalized Advantage Estimator (GAE), Hindsight Experience Replay (HER) |

 Sources: [README.md23-56](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1#L23-L56) [tianshou/policy/__init__.py4-66](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/__init__.py#L4-L66)

 
## APIs and Usage

 Tianshou provides two API levels:

 
### 1. High-Level API

 The high-level API provides ease of use for end users seeking to run deep reinforcement learning applications with minimal boilerplate code. It uses a declarative approach focused on configuration rather than implementation details.

 Key components:

 
 - `ExperimentBuilder`: Base class for building RL experiments
 - `ExperimentConfig`: Controls persistence and overall experiment flow
 - `SamplingConfig`: Controls training parameters
 - Algorithm-specific builders (e.g., `DQNExperimentBuilder`)
 
 Example usage:

 
```

```

 
### 2. Procedural API

 The procedural API provides maximum control for advanced users and algorithm developers, with direct access to all components.

 Basic workflow:

 
 - Create environments (`DummyVectorEnv`, `SubprocVectorEnv`, etc.)
 - Define network architecture
 - Initialize policy (e.g., `DQNPolicy`, `PPOPolicy`)
 - Set up collectors (`Collector`)
 - Create trainer (`OffpolicyTrainer`, `OnpolicyTrainer`)
 - Run training
 
 Example usage:

 
```

```

 Sources: [README.md198-427](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1#L198-L427)

 
## Key Features

 Tianshou includes numerous features that enhance its functionality and performance:

 
 - **Vectorized environments**: Support for synchronous or asynchronous parallel environments
 - **EnvPool integration**: Super-fast vectorized environments based on EnvPool
 - **Recurrent state representations**: RNN-style training for partially observable environments
 - **Flexible state/action types**: Support for any type of environment state/action (e.g., dictionaries, custom classes)
 - **Customizable training**: Support for customized training processes
 - **N-step returns and PER**: Optimized implementations of n-step returns and prioritized experience replay
 - **Multi-agent support**: Support for multi-agent reinforcement learning
 - **Logging integration**: Support for TensorBoard and W&B
 - **Multi-GPU training**: Support for distributed training across multiple GPUs
 
 Sources: [README.md58-76](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1#L58-L76)

 
## Performance and Benchmarks

 Tianshou is designed for high performance and reproducibility. The framework achieves state-of-the-art results in benchmarks like MuJoCo and Atari environments. The examples directory contains detailed benchmark results for various algorithms on standard environments.

 Tianshou is rigorously tested, with tests including the full agent training procedure for all implemented algorithms, ensuring reproducibility and consistent performance.

 Sources: [README.md175-181](https://github.com/thu-ml/tianshou/blob/90846f6b/README.md?plain=1#L175-L181) [examples/atari/README.md1-137](https://github.com/thu-ml/tianshou/blob/90846f6b/examples/atari/README.md?plain=1#L1-L137)
