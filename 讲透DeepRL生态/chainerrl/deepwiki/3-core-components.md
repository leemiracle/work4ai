> 来源: [https://deepwiki.com/chainer/chainerrl/3-core-components](https://deepwiki.com/chainer/chainerrl/3-core-components)
> DeepWiki chainer/chainerrl | Last indexed: 8 June 2025 (7eed37

# Core Components

  Relevant source files 
 - [chainerrl/action_value.py](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/action_value.py)
 - [chainerrl/links/mlp.py](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/links/mlp.py)
 - [chainerrl/policies/deterministic_policy.py](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/deterministic_policy.py)
 - [chainerrl/policies/gaussian_policy.py](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/gaussian_policy.py)
 - [chainerrl/policies/mellowmax_policy.py](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/mellowmax_policy.py)
 - [chainerrl/policies/softmax_policy.py](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/softmax_policy.py)
 - [chainerrl/q_functions/state_action_q_functions.py](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/q_functions/state_action_q_functions.py)
 - [chainerrl/q_functions/state_q_functions.py](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/q_functions/state_q_functions.py)
 - [chainerrl/v_functions/v_functions.py](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/v_functions/v_functions.py)
 - [tests/policies_tests/test_deterministic_policy.py](https://github.com/chainer/chainerrl/blob/7eed3756/tests/policies_tests/test_deterministic_policy.py)
 
  This document covers the fundamental building blocks used across different reinforcement learning algorithms in ChainerRL. These components provide the neural network architectures and data structures that RL agents use to represent value functions, policies, and action values.

 For information about specific RL algorithms that use these components, see [Reinforcement Learning Agents](https://deepwiki.com/chainer/chainerrl/2-reinforcement-learning-agents). For training infrastructure that orchestrates these components, see [Training and Evaluation Infrastructure](https://deepwiki.com/chainer/chainerrl/4-training-and-evaluation-infrastructure).

 
## Architecture Overview

 ChainerRL's core components form a modular architecture where different RL algorithms can mix and match components based on their needs. The system is organized around three main abstractions: action values, policies, and value functions.

 
```

```

 **Sources:** [chainerrl/action_value.py13-42](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/action_value.py#L13-L42) [chainerrl/policies/gaussian_policy.py18-106](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/gaussian_policy.py#L18-L106) [chainerrl/policies/deterministic_policy.py19-48](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/deterministic_policy.py#L19-L48) [chainerrl/policies/softmax_policy.py14-32](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/softmax_policy.py#L14-L32) [chainerrl/q_functions/state_q_functions.py27-41](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/q_functions/state_q_functions.py#L27-L41) [chainerrl/q_functions/state_action_q_functions.py12-26](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/q_functions/state_action_q_functions.py#L12-L26) [chainerrl/v_functions/v_functions.py9-23](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/v_functions/v_functions.py#L9-L23)

 
## Action Value Representations

 Action values represent Q-functions and provide standardized interfaces for action selection and value evaluation. All action value classes inherit from the abstract `ActionValue` base class.

 
```

```

 **Sources:** [chainerrl/action_value.py13-365](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/action_value.py#L13-L365)

 
### Core ActionValue Interface

 The `ActionValue` base class defines four essential methods that all implementations must provide:

 
| Method | Purpose | Return Type |
|---|---|---|
| greedy_actions | Get argmax_a Q(s,a) | chainer.Variable |
| max | Evaluate max Q(s,a) | chainer.Variable |
| evaluate_actions(actions) | Evaluate Q(s,a) for given actions | chainer.Variable |
| params | Get learnable parameters | tuple |

 **Sources:** [chainerrl/action_value.py19-41](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/action_value.py#L19-L41)

 
### Discrete Action Values

 `DiscreteActionValue` handles Q-functions for discrete action spaces. It takes Q-values with shape `(batch_size, n_actions)` and provides efficient action selection and evaluation.

 
```

```

 **Sources:** [chainerrl/action_value.py44-94](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/action_value.py#L44-L94)

 
### Distributional Action Values

 `DistributionalDiscreteActionValue` represents the full return distribution for each action, supporting distributional RL algorithms like C51. It takes probability distributions over return atoms with shape `(batch_size, n_actions, n_atoms)`.

 **Sources:** [chainerrl/action_value.py96-182](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/action_value.py#L96-L182)

 
### Continuous Action Values

 `QuadraticActionValue` implements a quadratic advantage function for continuous control, as used in NAF (Normalized Advantage Functions). It represents Q(s,a) = V(s) + A(s,a) where A(s,a) has a quadratic form.

 **Sources:** [chainerrl/action_value.py237-322](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/action_value.py#L237-L322)

 
## Policy Implementations

 Policies define how agents select actions given states. ChainerRL provides several policy types for different action spaces and exploration strategies.

 
```

```

 **Sources:** [chainerrl/policies/gaussian_policy.py18-294](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/gaussian_policy.py#L18-L294) [chainerrl/policies/deterministic_policy.py19-218](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/deterministic_policy.py#L19-L218) [chainerrl/policies/softmax_policy.py14-56](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/softmax_policy.py#L14-L56) [chainerrl/policies/mellowmax_policy.py12-30](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/mellowmax_policy.py#L12-L30)

 
### Gaussian Policies

 `FCGaussianPolicy` implements stochastic policies for continuous action spaces using Gaussian distributions. The policy outputs both mean and variance, with options for action bounding and different variance parameterizations.

 Key parameters:

 
 - `var_type`: `'spherical'` (single variance) or `'diagonal'` (per-dimension variance)
 - `bound_mean`: Whether to bound actions using tanh
 - `min_var`: Minimum variance to ensure numerical stability
 
 **Sources:** [chainerrl/policies/gaussian_policy.py18-106](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/gaussian_policy.py#L18-L106)

 
### Deterministic Policies

 `FCDeterministicPolicy` implements deterministic policies for continuous control. Actions can optionally be bounded to `[min_action, max_action]` using tanh activation.

 **Sources:** [chainerrl/policies/deterministic_policy.py50-98](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/policies/deterministic_policy.py#L50-L98)

 
## Q-Function and Value Function Implementations

 Q-functions and value functions provide the neural network architectures for value estimation. ChainerRL distinguishes between state Q-functions Q(s) that output action values for all actions, and state-action Q-functions Q(s,a) that evaluate specific state-action pairs.

 
### State Q-Functions

 State Q-functions take states as input and output action values. They are used in value-based methods like DQN.

 
```

```

 **Sources:** [chainerrl/q_functions/state_q_functions.py27-276](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/q_functions/state_q_functions.py#L27-L276)

 
### State-Action Q-Functions

 State-action Q-functions take both states and actions as input, commonly used in actor-critic methods like DDPG.

 **Implementation Variants:**

 
| Class | Architecture | Use Case |
|---|---|---|
| FCSAQFunction | Basic concatenation of state and action | Standard DDPG |
| FCBNSAQFunction | With batch normalization | Improved training stability |
| FCBNLateActionSAQFunction | Late action injection | DDPG paper architecture |
| FCLSTMSAQFunction | With LSTM | Partially observable environments |

 **Sources:** [chainerrl/q_functions/state_action_q_functions.py29-243](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/q_functions/state_action_q_functions.py#L29-L243)

 
### Value Functions

 `VFunction` implementations estimate state values V(s) for policy gradient methods.

 **Sources:** [chainerrl/v_functions/v_functions.py9-40](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/v_functions/v_functions.py#L9-L40)

 
## Neural Network Building Blocks

 Core neural network components provide reusable architectures across different function approximators.

 
### Multi-Layer Perceptron (MLP)

 The `MLP` class is the fundamental building block used throughout ChainerRL. It provides a configurable fully-connected network with customizable hidden layers and nonlinearities.

 
```

```

 **Key Features:**

 
 - Configurable number of hidden layers and units
 - Custom nonlinearity functions
 - Weight initialization control via `last_wscale`
 - Support for no hidden layers (linear transformation)
 
 **Sources:** [chainerrl/links/mlp.py7-36](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/links/mlp.py#L7-L36)

 
### Specialized Network Components

 ChainerRL also provides specialized network variants:

 
 - **MLPBN**: MLP with batch normalization for improved training stability
 - **Sequence**: For chaining multiple operations and transformations
 - **LSTM layers**: For recurrent neural network implementations
 
 These building blocks are composed together to create the policy and value function implementations described above.

 **Sources:** [chainerrl/q_functions/state_q_functions.py109-117](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/q_functions/state_q_functions.py#L109-L117) [chainerrl/q_functions/state_action_q_functions.py103-138](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/q_functions/state_action_q_functions.py#L103-L138)
