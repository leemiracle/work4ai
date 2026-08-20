# deepwiki torchrl §7 learning-algorithms
> 来源: https://deepwiki.com/pytorch/rl/7-learning-algorithms

$/$
$?

/$

DeepWiki

DeepWiki
pytorch/rl

$?

/$

Last indexed:  14 December 2025  (eaaa11)

  - Overview
  - Core Data Infrastructure
  - TensorDict System
  - TensorSpec System
  - Environments
  - EnvBase and Environment Specifications
  - Environment Transforms
  - Backend Integrations
  - Batched and Parallel Environments
  - Data Collection
  - Collector Architecture
  - Distributed Collection Strategies
  - Replay Buffers
  - ReplayBuffer Architecture
  - Advanced Replay Buffer Features
  - Modules and Models
  - TensorDictModule System
  - Actors, Critics, and Value Networks
  - Probability Distributions
  - Neural Network Architectures
  - Exploration Strategies
  - Learning Algorithms
  - Loss Module Architecture
  - On-Policy Algorithms
  - Off-Policy Algorithms
  - Value-Based Algorithms
  - Value Estimators
  - Training Infrastructure
  - Trainer System
  - Helper Utilities
  - LLM Integration
  - LLM Wrapper System
  - LLM Data Structures
  - LLM Training Objectives
  - LLM Environments and Tools
  - Multi-Agent Reinforcement Learning
  - Examples and Tutorials
  - Development and Deployment
  - Build System
  - Documentation System

Menu

## Learning Algorithms

Relevant source files

  - CONTRIBUTING.md

  - README.md

  - docs/source/reference/objectives.rst

  - test/test_cost.py

  - torchrl/objectives/__init__.py

  - torchrl/objectives/a2c.py

  - torchrl/objectives/common.py

  - torchrl/objectives/cql.py

  - torchrl/objectives/ddpg.py

  - torchrl/objectives/deprecated.py

  - torchrl/objectives/dqn.py

  - torchrl/objectives/iql.py

  - torchrl/objectives/ppo.py

  - torchrl/objectives/redq.py

  - torchrl/objectives/reinforce.py

  - torchrl/objectives/sac.py

  - torchrl/objectives/td3.py

  - torchrl/objectives/utils.py

  - torchrl/objectives/value/advantages.py

This section documents TorchRL's learning algorithm implementations, specifically loss modules and value estimation methods that enable training of reinforcement learning agents. This covers the mathematical objectives and value functions used by various RL algorithms.

For information about the neural network components that these algorithms operate on, see Modules and Models. For details about data collection during training, see Data Collection.

### Core Architecture

TorchRL's learning algorithms are built around the `LossModule` base class, which provides a unified interface for computing RL losses. All algorithm-specific loss implementations inherit from this base class and implement the mathematical objectives for their respective algorithms.

#### LossModule Base Class

The `LossModule` serves as the foundation for all RL algorithm implementations in TorchRL:

```

```

Sources: torchrl/objectives/common.py71-443

Key capabilities provided by `LossModule`:

  - Functional conversion : Automatically converts PyTorch modules to functional form for use with vmap and meta-learning

  - Target network management : Handles creation and updating of target networks for algorithms that require them

  - Configurable keys : Allows customization of TensorDict keys through the _AcceptedKeys dataclass pattern

  - Value estimator integration : Seamless integration with value estimation methods for advantage computation

### Algorithm-Specific Loss Modules

TorchRL implements loss modules for major RL algorithm families, each handling the specific mathematical objectives and computational requirements of their respective algorithms.

#### Policy Gradient Methods

PPOLoss implements Proximal Policy Optimization with support for clipping and KL penalty variants:

```

```

Sources: torchrl/objectives/ppo.py55-289

A2CLoss provides the simpler Advantage Actor-Critic implementation:

```

```

Sources: torchrl/objectives/a2c.py51-214

ReinforceLoss implements the basic REINFORCE algorithm with optional baseline:

Sources: torchrl/objectives/reinforce.py40-180

#### Value-Based Methods

DQNLoss handles Deep Q-Network training with support for Double DQN and target networks:

```

```

Sources: test/test_cost.py453-1074

#### Actor-Critic Methods

SACLoss implements Soft Actor-Critic with entropy regularization:

```

```

Sources: torchrl/objectives/sac.py62-256

DDPGLoss provides Deep Deterministic Policy Gradient implementation:

Sources: torchrl/objectives/ddpg.py29-143

TD3Loss implements Twin Delayed Deep Deterministic Policy Gradient:

Sources: torchrl/objectives/td3.py29-81

#### Offline RL Methods

CQLLoss implements Conservative Q-Learning for offline reinforcement learning:

Sources: torchrl/objectives/cql.py38-96

IQLLoss provides Implicit Q-Learning for offline settings:

Sources: torchrl/objectives/iql.py32-74

#### Ensemble Methods

REDQLoss implements Randomized Ensembled Double Q-Learning:

Sources: torchrl/objectives/redq.py32-90

### Value Estimation Methods

Value estimators compute advantages and value targets that are used by policy gradient algorithms. TorchRL provides several estimators implementing different mathematical approaches.

#### ValueEstimatorBase

All value estimators inherit from `ValueEstimatorBase`, which provides the interface for computing advantages and value targets:

```

```

Sources: torchrl/objectives/value/advantages.py96-384

#### Specific Estimators

TD0Estimator implements 1-step temporal difference estimation:

  - Computes bootstrapped value targets using immediate reward plus discounted next state value

  - Fastest but highest variance estimator

Sources: torchrl/objectives/value/advantages.py557-702

TD1Estimator implements infinite-step returns (Monte Carlo):

  - Uses complete episode returns without bootstrapping

  - Lower bias but higher variance than TD(0)

Sources: torchrl/objectives/value/advantages.py704-849

TDLambdaEstimator implements TD(λ) with exponential trace decay:

  - Interpolates between TD(0) and Monte Carlo using λ parameter

  - Balances bias and variance

Sources: torchrl/objectives/value/advantages.py851-999

GAE (Generalized Advantage Estimation) implements the GAE algorithm:

  - Most commonly used estimator for policy gradient methods

  - Provides good bias-variance tradeoff with λ parameter

Sources: torchrl/objectives/value/advantages.py1001-1141

VTrace implements V-trace for off-policy learning:

  - Designed for off-policy actor-critic algorithms

  - Includes importance sampling corrections

Sources: torchrl/objectives/value/advantages.py1143-1283

### Supporting Infrastructure

#### Target Network Updates

TorchRL provides utilities for managing target networks used in many RL algorithms:

```

```

Sources: torchrl/objectives/utils.py144-388

#### Utility Functions

The utilities module provides common functionality used across loss modules:

  - Distance loss functions : distance_loss() supporting L1, L2, and Smooth L1 losses

  - Value estimation configuration : default_value_kwargs() for setting up estimators

  - Reduction operations : _reduce() for aggregating losses

  - vmap support : _vmap_func() for vectorized operations

Sources: torchrl/objectives/utils.py45-88 torchrl/objectives/utils.py107-142

#### ValueEstimators Enum

The `ValueEstimators` enum provides a convenient way to specify which value estimation method to use:

| Estimator | Description |
| TD0 | Bootstrapped TD (1-step return) |
| TD1 | TD(1) (infinite-step return) |
| TDLambda | TD(λ) with exponential trace |
| GAE | Generalized Advantage Estimation |
| VTrace | V-trace for off-policy learning |

Sources: torchrl/objectives/utils.py45-62

This architecture provides a flexible and extensible framework for implementing RL algorithms, with clear separation between algorithm-specific loss computation, value estimation, and supporting infrastructure.



#### On this page

  - Learning Algorithms
  - Core Architecture
  - LossModule Base Class
  - Algorithm-Specific Loss Modules
  - Policy Gradient Methods
  - Value-Based Methods
  - Actor-Critic Methods
  - Offline RL Methods
  - Ensemble Methods
  - Value Estimation Methods
  - ValueEstimatorBase
  - Specific Estimators
  - Supporting Infrastructure
  - Target Network Updates
  - Utility Functions
  - ValueEstimators Enum

$!/$$/$
