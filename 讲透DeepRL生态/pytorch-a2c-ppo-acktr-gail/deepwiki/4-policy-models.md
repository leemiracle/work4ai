> 来源: [https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/4-policy-models](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/4-policy-models)
> DeepWiki ikostrikov/pytorch-a2c-ppo-acktr-gail | Last indexed: 21 April 2025 (41332b

# Policy Models

  Relevant source files 
 - [a2c_ppo_acktr/distributions.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/distributions.py)
 - [a2c_ppo_acktr/model.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/model.py)
 
  This document describes the policy model architecture used across all reinforcement learning algorithms in this codebase. The policy models implement actor-critic architectures that generate both actions (actor) and state value estimates (critic) based on environment observations. For information about the specific reinforcement learning algorithms that use these policies, see [Reinforcement Learning Algorithms](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/5-reinforcement-learning-algorithms).

 
## Policy Architecture Overview

 The policy architecture in this codebase follows an actor-critic design pattern with flexible network backends that adapt to different observation types. The main `Policy` class integrates a base neural network with action distribution modules to create a complete policy.

 
```

```

 Sources: [a2c_ppo_acktr/model.py15-79](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/model.py#L15-L79)

 
## Policy Class

 The main `Policy` class automatically selects the appropriate base network architecture based on the shape of observations and creates the appropriate action distribution based on the action space type.

 
```

```

 Sources: [a2c_ppo_acktr/model.py15-79](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/model.py#L15-L79)

 The `Policy` class has three main methods:

 
 - `act()`: Used during rollout collection to select actions based on current observations
 - `get_value()`: Used to get state value estimates without generating actions
 - `evaluate_actions()`: Used during policy updates to evaluate previously taken actions
 
 
## Base Network Architectures

 The codebase provides two main neural network architectures that serve as the backbone for the policy:

 
### NNBase

 `NNBase` is the abstract base class that defines the common interface and recurrent functionality used by all network architectures.

 Sources: [a2c_ppo_acktr/model.py82-166](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/model.py#L82-L166)

 
### CNNBase

 `CNNBase` is used for image-based observations (shape length = 3) and implements a convolutional neural network:

 
```
Observations (N×C×H×W) → Conv2d → ReLU → Conv2d → ReLU → Conv2d → ReLU → Flatten → Linear → ReLU
```

 The network outputs both a state value estimate (critic) and feature representation (actor features) used for action distribution.

 Sources: [a2c_ppo_acktr/model.py169-195](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/model.py#L169-L195)

 
### MLPBase

 `MLPBase` is used for vector-based observations (shape length = 1) and implements separate multilayer perceptrons for the actor and critic:

 
```

```

 Sources: [a2c_ppo_acktr/model.py198-229](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/model.py#L198-L229)

 
## Action Distributions

 The policy model supports three types of action distributions, each implemented as a PyTorch module that produces a corresponding probability distribution:

 
### Categorical Distribution

 Used for discrete action spaces (`Discrete`). The module maps actor features to logits for a categorical distribution over discrete actions.

 Sources: [a2c_ppo_acktr/distributions.py59-73](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/distributions.py#L59-L73)

 
### DiagGaussian Distribution

 Used for continuous action spaces (`Box`). The module outputs the mean and log standard deviation for a multivariate Gaussian with diagonal covariance matrix.

 Sources: [a2c_ppo_acktr/distributions.py76-95](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/distributions.py#L76-L95)

 
### Bernoulli Distribution

 Used for binary action spaces (`MultiBinary`). The module maps actor features to logits for independent Bernoulli distributions.

 Sources: [a2c_ppo_acktr/distributions.py98-109](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/distributions.py#L98-L109)

 
## Distribution Wrappers

 The codebase extends PyTorch's standard probability distributions to provide a consistent interface:

 
```

```

 Sources: [a2c_ppo_acktr/distributions.py1-57](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/distributions.py#L1-L57)

 Each distribution wrapper standardizes:

 
 - Action sampling and shape handling
 - Log probability calculation
 - Entropy computation
 - Deterministic action selection (mode)
 
 
## Recurrent Policies

 All base networks support recurrent policies through an optional GRU (Gated Recurrent Unit) layer. When enabled, the policy maintains a hidden state that is updated at each step.

 The `_forward_gru()` method in `NNBase` handles both single-step and batched multi-step sequences, with special logic to correctly reset hidden states when episodes terminate.

 Sources: [a2c_ppo_acktr/model.py111-166](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/model.py#L111-L166)

 
## Integration with RL Algorithms

 The policy models are used by all the reinforcement learning algorithms in the codebase (A2C, PPO, ACKTR) through a common interface:

 
```

```

 This standardized interface allows the same policy model implementations to be reused across all the different algorithms.

 Sources: [a2c_ppo_acktr/model.py54-79](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/model.py#L54-L79)

 
## Example Policy Instantiation

 The policy is automatically configured based on the observation space and action space. For example:

 
 - For Atari games: `CNNBase` + `Categorical` distribution
 - For MuJoCo: `MLPBase` + `DiagGaussian` distribution
 
 The selection happens in the `Policy` class constructor, which examines the shape of the observation space and the type of action space.

 Sources: [a2c_ppo_acktr/model.py15-40](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/model.py#L15-L40)
