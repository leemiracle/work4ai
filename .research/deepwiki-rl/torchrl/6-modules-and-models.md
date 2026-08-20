# deepwiki torchrl §6 modules-and-models
> 来源: https://deepwiki.com/pytorch/rl/6-modules-and-models

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

## Modules and Models

Relevant source files

  - docs/source/reference/modules.rst

  - test/test_actors.py

  - test/test_exploration.py

  - test/test_modules.py

  - test/test_tensordictmodules.py

  - torchrl/modules/__init__.py

  - torchrl/modules/models/__init__.py

  - torchrl/modules/models/exploration.py

  - torchrl/modules/models/models.py

  - torchrl/modules/models/multiagent.py

  - torchrl/modules/models/utils.py

  - torchrl/modules/tensordict_module/__init__.py

  - torchrl/modules/tensordict_module/actors.py

  - torchrl/modules/tensordict_module/common.py

  - torchrl/modules/tensordict_module/exploration.py

  - torchrl/modules/tensordict_module/probabilistic.py

  - torchrl/modules/tensordict_module/rnn.py

  - torchrl/modules/tensordict_module/sequence.py

The Modules and Models system in TorchRL provides neural network components, policy modules, and model architectures for reinforcement learning. This system serves as the foundation for constructing policies, value functions, and other neural network architectures necessary for implementing RL algorithms.

For information about the data structures that these modules operate on, see Data Structures. For details on learning algorithms that use these modules, see Learning Algorithms.

### Overview

TorchRL's module system extends PyTorch's `nn.Module` with TensorDict compatibility, forming a layered architecture where each level adds specific functionality for RL. The system is organized into five main categories:

  - TensorDictModule System - Base wrappers providing in_keys / out_keys interface and spec-based validation

  - Actors and Critics - Specialized modules for policies and value functions

  - Probability Distributions - RL-specific distributions with bounded actions and masking

  - Neural Network Architectures - Network implementations (MLP, ConvNet, RNN) optimized for RL

  - Exploration Strategies - Modules for exploration noise and action perturbation

### Module System Layered Architecture

The following diagram shows the inheritance hierarchy and how components build upon each other:

```

```

Sources:

  - torchrl/modules/__init__.py 1-189

  - torchrl/modules/tensordict_module/__init__.py 1-90

  - torchrl/modules/tensordict_module/actors.py 34-466

  - torchrl/modules/tensordict_module/common.py 97-293

### TensorDictModule Data Flow

The following diagram illustrates how modules read from and write to TensorDict using the `in_keys`/`out_keys` pattern:

```

```

Sources:

  - torchrl/modules/tensordict_module/common.py 97-210

  - torchrl/modules/tensordict_module/common.py 55-95

  - test/test_tensordictmodules.py 78-117

### TensorDict Modules

TensorDict modules provide the foundation for making PyTorch modules compatible with TensorDict operations. These modules handle input/output key mapping, tensor specification validation, and safe projection of outputs.

#### SafeModule

`SafeModule` is the foundational class in torchrl/modules/tensordict_module/common.py97-293 that wraps any `nn.Module` to work with TensorDict. It extends `tensordict.nn.TensorDictModule` with spec-based safety validation.

##### SafeModule Architecture

```

```

Key Parameters:

| Parameter | Type | Description |
| module | nn.Module | The neural network to wrap |
| in_keys | List[NestedKey] | Keys to read from input TensorDict |
| out_keys | List[NestedKey] | Keys to write to output TensorDict |
| spec | TensorSpec | None | Output domain specification |
| safe | bool | Whether to project outputs onto spec (default: False ) |

Example Usage:

```

```

Sources:

  - torchrl/modules/tensordict_module/common.py 97-293

  - torchrl/modules/tensordict_module/common.py 55-95

  - test/test_tensordictmodules.py 142-193

#### SafeProbabilisticModule

`SafeProbabilisticModule` in torchrl/modules/tensordict_module/probabilistic.py24-322 wraps distribution constructors with spec-based safety. It reads distribution parameters from TensorDict, constructs a distribution, and samples/computes values based on the interaction mode.

##### Probabilistic Module Flow

```

```

Interaction Types: Controlled by `tensordict.nn.interaction_type()` context manager:

| Type | Behavior | Use Case |
| RANDOM | dist.rsample() or dist.sample() | Training with exploration |
| MODE | dist.mode | Greedy evaluation |
| MEAN | dist.mean | Average behavior |
| DETERMINISTIC | dist.mode or dist.mean | Deterministic evaluation |

Sources:

  - torchrl/modules/tensordict_module/probabilistic.py 24-150

  - test/test_tensordictmodules.py 194-269

#### SafeSequential

`SafeSequential` allows chaining multiple TensorDict-compatible modules together, similar to PyTorch's `nn.Sequential`. It aggregates specs from all constituent modules and supports partial execution when input keys are missing.

Sources:

  - torchrl/modules/tensordict_module/common.py 97-293

  - torchrl/modules/tensordict_module/probabilistic.py 24-322

  - torchrl/modules/tensordict_module/sequence.py 15-133

  - test/test_tensordictmodules.py 78-451

### Actors and Critics

Actors (policies) and critics (value functions) are essential components in reinforcement learning. TorchRL provides specialized implementations for different RL paradigms including deterministic policies, stochastic policies, and value-based methods.

#### ProbabilisticActor

`ProbabilisticActor` in torchrl/modules/tensordict_module/actors.py126-393 is a complete stochastic policy implementation. It chains a parameter-generating module with a `SafeProbabilisticModule` to form a `SafeProbabilisticTensorDictSequential`.

##### ProbabilisticActor Construction

```

```

Example Construction:

```

```

Supported Distributions:

  - TanhNormal - Bounded continuous actions via tanh squashing

  - TruncatedNormal - Hard-truncated normal distribution

  - Delta - Deterministic (point mass) distribution

  - Categorical / OneHotCategorical - Discrete actions

  - CompositeDistribution - Multiple action types

Sources:

  - torchrl/modules/tensordict_module/actors.py 126-393

  - test/test_tensordictmodules.py 194-269

  - docs/source/reference/modules.rst 27-44

#### QValueActor and QValueModule

`QValueModule` in torchrl/modules/tensordict_module/actors.py468-672 processes action values (Q-values) into discrete actions using argmax or other selection strategies. It supports masked action spaces for invalid actions.

##### QValueModule Action Selection

```

```

Action Space Support:

| Action Space | Input Shape | Output Shape | Selection |
| categorical | [..., n_actions] | [...] (integer) | argmax(action_value) |
| one_hot | [..., n_actions] | [..., n_actions] | One-hot at argmax |
| mult_one_hot | [..., sum(n_i)] | [..., sum(n_i)] | Multiple one-hots over splits |
| binary | [..., n_actions] | [..., n_actions] | Not implemented |

Example with Action Masking:

```

```

Sources:

  - torchrl/modules/tensordict_module/actors.py 468-672

  - test/test_actors.py 170-277

  - test/test_exploration.py 89-167

#### ValueOperator

`ValueOperator` in torchrl/modules/tensordict_module/actors.py395-466 implements value functions (critics). It automatically sets output keys based on whether actions are in the input keys.

##### ValueOperator Key Selection

```

```

Usage Examples:

```

```

Common Patterns:

| Pattern | In Keys | Out Keys | Use Case |
| State value | ["observation"] | ["state_value"] | PPO, A2C baseline |
| State-action value | ["observation", "action"] | ["state_action_value"] | SAC, DDPG critic |
| Dueling architecture | ["observation"] | ["state_value", "advantage"] | Dueling DQN |

Sources:

  - torchrl/modules/tensordict_module/actors.py 395-466

  - test/test_modules.py 397-425

### Probability Distributions

TorchRL provides probability distribution classes specifically designed for reinforcement learning applications. These distributions handle common requirements like bounded action spaces, numerical stability, and gradient flow.

### Probability Distributions

TorchRL provides custom distributions in torchrl/modules/distributions/ that extend `torch.distributions` with RL-specific features like bounded action spaces, action masking, and numerical stability.

#### TanhNormal - Bounded Continuous Actions

`TanhNormal` in torchrl/modules/distributions/continuous.py applies a tanh transformation to a Normal distribution, squashing outputs to `[-1, 1]` while maintaining reparameterization.

##### TanhNormal Transformation Flow

```

```

Key Properties:

  - Reparameterizable : Supports backpropagation through samples via rsample()

  - Bounded : Output range is (-1, 1) or scaled to [low, high]

  - Stable log_prob : Handles numerical issues near boundaries

  - Differentiable : Gradients flow through the transformation

#### MaskedCategorical - Discrete with Invalid Actions

`MaskedCategorical` extends `torch.distributions.Categorical` to support action masking, preventing selection of invalid actions.

```

```

#### Distribution Summary Table

| Distribution | Space | Key Feature | Use Case |
| TanhNormal | Continuous | Bounded via tanh | SAC, TD3 continuous control |
| TruncatedNormal | Continuous | Hard truncation | Hard-bounded continuous |
| Delta | Any | Deterministic | DDPG, deterministic policies |
| Categorical | Discrete | Standard sampling | DQN, discrete RL |
| OneHotCategorical | Discrete | One-hot output | Gumbel-softmax, REINFORCE |
| MaskedCategorical | Discrete | Action masking | Invalid action spaces |
| IndependentNormal | Continuous | Independent dims | Multi-dimensional actions |

Sources:

  - torchrl/modules/distributions/continuous.py

  - torchrl/modules/distributions/discrete.py

  - test/test_tensordictmodules.py 44-45

  - test/test_tensordictmodules.py 199-255

### Neural Network Architectures

TorchRL provides implementations of common neural network architectures optimized for reinforcement learning applications. These architectures are designed to work seamlessly with TensorDict modules and provide specialized features for RL tasks.

#### MLP (Multi-Layer Perceptron)

`MLP` in torchrl/modules/models/models.py29-296 provides a flexible fully-connected network with extensive configuration options for layer sizes, activations, normalization, and dropout.

##### MLP Layer Construction

```

```

Key Parameters:

| Parameter | Type | Description | Default |
| in_features | int | None | Input dimension (None for LazyLinear) | Required |
| out_features | int | tuple | Output dimension(s) | Required |
| depth | int | None | Number of hidden layers | 0 |
| num_cells | int | List[int] | Hidden layer sizes | 32 |
| activation_class | Type[nn.Module] | Activation function | nn.Tanh |
| norm_class | Type[nn.Module] | None | Normalization layer | None |
| dropout | float | Dropout probability | None |
| layer_class | Type[nn.Module] | Linear layer class | nn.Linear |
| device | torch.device | Device placement | None |

Usage Examples:

```

```

Sources:

  - torchrl/modules/models/models.py 29-296

  - test/test_modules.py 77-169

#### Recurrent Neural Networks

TorchRL provides RNN modules in torchrl/modules/tensordict_module/rnn.py that wrap PyTorch's LSTM and GRU with TensorDict integration, supporting both sequential (training) and step-by-step (rollout) modes.

##### LSTMModule Architecture

```

```

LSTMModule Key Parameters:

| Parameter | Type | Description |
| input_size | int | Input feature dimension |
| hidden_size | int | Hidden state dimension |
| num_layers | int | Number of stacked LSTM layers |
| in_key / in_keys | NestedKey | List[NestedKey] | Input and hidden state keys |
| out_key / out_keys | NestedKey | List[NestedKey] | Output and next hidden state keys |
| python_based | bool | Use pure Python LSTM (vmap-compatible) |
| default_recurrent_mode | bool | Default mode if not set by context |

Recurrent Mode Control:

```

```

State Initialization: Use `make_tensordict_primer()` to create a transform that initializes hidden states:

```

```

##### GRUModule

`GRUModule` in torchrl/modules/tensordict_module/rnn.py1093-1273 provides similar functionality with simpler architecture (single hidden state instead of hidden + cell).

#### ConvNet - Vision Networks

`ConvNet` in torchrl/modules/models/models.py implements convolutional networks for image-based observations.

```

```

Sources:

  - torchrl/modules/tensordict_module/rnn.py 311-810

  - torchrl/modules/tensordict_module/rnn.py 1093-1273

  - test/test_tensordictmodules.py 659-1055

  - torchrl/modules/models/models.py 298-500

### Exploration Strategies

TorchRL provides exploration modules in torchrl/modules/tensordict_module/exploration.py and torchrl/modules/models/exploration.py that add noise or modify actions to encourage exploration during training.

#### Exploration Module Types

##### EGreedyModule - ε-Greedy Exploration

`EGreedyModule` in torchrl/modules/tensordict_module/exploration.py33-204 implements epsilon-greedy exploration for discrete action spaces, randomly replacing actions with probability ε.

```

```

Key Features:

  - Annealing : eps decays from eps_init to eps_end over annealing_num_steps

  - Action Masking : Respects action_mask_key for invalid actions

  - Spec-based sampling : Uses spec.rand() for random actions

```

```

##### AdditiveGaussianModule - Gaussian Noise

`AdditiveGaussianModule` in torchrl/modules/tensordict_module/exploration.py247-374 adds Gaussian noise to continuous actions, commonly used with DDPG/TD3.

```

```

##### OrnsteinUhlenbeckProcessModule - Temporally Correlated Noise

`OrnsteinUhlenbeckProcessModule` in torchrl/modules/tensordict_module/exploration.py405-638 implements the Ornstein-Uhlenbeck process for temporally correlated exploration noise.

OU Process Equation:

```
noise_t = noise_{t-1} + θ(μ - noise_{t-1})dt + σ√dt·W
```

```

```

State Management: OU process maintains internal state across steps, automatically resets on `is_init=True`.

#### NoisyLinear - Parameter Noise

`NoisyLinear` in torchrl/modules/models/exploration.py29-154 adds learnable noise to network parameters instead of actions, enabling state-dependent exploration.

```

```

Usage:

```

```

#### Exploration Module Comparison

| Module | Action Space | Noise Type | State-Dependent | Annealing |
| EGreedyModule | Discrete | Uniform random | No | Yes (ε) |
| AdditiveGaussianModule | Continuous | IID Gaussian | No | Yes (σ) |
| OrnsteinUhlenbeckProcessModule | Continuous | Correlated Gaussian | No | Yes (σ, ε) |
| NoisyLinear | Any | Parameter noise | Yes | No (learned) |

Sources:

  - torchrl/modules/tensordict_module/exploration.py 33-638

  - torchrl/modules/models/exploration.py 29-154

  - test/test_exploration.py 60-421

### Multi-Agent Networks

`MultiAgentNetBase` in torchrl/modules/models/multiagent.py21-172 provides the foundation for multi-agent architectures with support for parameter sharing and centralized/decentralized execution.

#### MultiAgentMLP and MultiAgentConvNet

```

```

Usage Example:

```

```

Parameter Sharing Options:

| share_params | centralized | Description | Use Case |
| True | False | Same network, local obs | Symmetric agents (QMIX) |
| True | True | Same network, joint obs | Centralized training |
| False | False | Separate networks, local obs | Heterogeneous agents |
| False | True | Separate networks, joint obs | Asymmetric centralized |

Sources:

  - torchrl/modules/models/multiagent.py 21-172

  - test/test_modules.py 749-793

### Integration with TensorDict

The module system is designed to work seamlessly with TensorDict, the core data structure in TorchRL:

```

```

When a module operates on a TensorDict:

  - It reads the values specified by in_keys from the input TensorDict

  - Passes these values through the underlying neural network

  - Writes the outputs to the specified out_keys in the TensorDict

  - If safe=True , validates outputs against the provided specs

This allows for complex compositions of modules that operate on the same TensorDict, with each module reading and writing specific sections of the data structure.

Sources:

  - torchrl/modules/tensordict_module/common.py 40-95

### Conclusion

TorchRL's Modules and Models system provides a comprehensive and flexible framework for building reinforcement learning agents. By leveraging TensorDict and extending PyTorch's module system, it enables the development of complex RL architectures with minimal boilerplate code.

The system's key benefits include:

  - Seamless integration with TensorDict data structures

  - Safety mechanisms to enforce constraints on network outputs

  - Specialized implementations for RL-specific requirements

  - Flexible composition of modules for complex agent architectures

Together, these components form the neural network foundation for implementing various RL algorithms in the TorchRL library.



#### On this page

  - Modules and Models
  - Overview
  - Module System Layered Architecture
  - TensorDictModule Data Flow
  - TensorDict Modules
  - SafeModule
  - SafeModule Architecture
  - SafeProbabilisticModule
  - Probabilistic Module Flow
  - SafeSequential
  - Actors and Critics
  - ProbabilisticActor
  - ProbabilisticActor Construction
  - QValueActor and QValueModule
  - QValueModule Action Selection
  - ValueOperator
  - ValueOperator Key Selection
  - Probability Distributions
  - Probability Distributions
  - TanhNormal - Bounded Continuous Actions
  - TanhNormal Transformation Flow
  - MaskedCategorical - Discrete with Invalid Actions
  - Distribution Summary Table
  - Neural Network Architectures
  - MLP (Multi-Layer Perceptron)
  - MLP Layer Construction
  - Recurrent Neural Networks
  - LSTMModule Architecture
  - GRUModule
  - ConvNet - Vision Networks
  - Exploration Strategies
  - Exploration Module Types
  - EGreedyModule - ε-Greedy Exploration
  - AdditiveGaussianModule - Gaussian Noise
  - OrnsteinUhlenbeckProcessModule - Temporally Correlated Noise
  - NoisyLinear - Parameter Noise
  - Exploration Module Comparison
  - Multi-Agent Networks
  - MultiAgentMLP and MultiAgentConvNet
  - Integration with TensorDict
  - Conclusion

$!/$$/$
