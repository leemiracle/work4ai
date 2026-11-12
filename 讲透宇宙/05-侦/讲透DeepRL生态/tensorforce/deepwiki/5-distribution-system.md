> 来源: [https://deepwiki.com/tensorforce/tensorforce/5-distribution-system](https://deepwiki.com/tensorforce/tensorforce/5-distribution-system)
> DeepWiki tensorforce/tensorforce | Last indexed: 24 April 2025 (d384bd

# Distribution System

  Relevant source files 
 - [tensorforce/core/distributions/bernoulli.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/bernoulli.py)
 - [tensorforce/core/distributions/beta.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/beta.py)
 - [tensorforce/core/distributions/categorical.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/categorical.py)
 - [tensorforce/core/distributions/distribution.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/distribution.py)
 - [tensorforce/core/distributions/gaussian.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/gaussian.py)
 - [tensorforce/core/objectives/deterministic_policy_gradient.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/objectives/deterministic_policy_gradient.py)
 - [tensorforce/core/objectives/policy_gradient.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/objectives/policy_gradient.py)
 - [tensorforce/core/objectives/value.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/objectives/value.py)
 - [tensorforce/core/policies/action_value.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/policies/action_value.py)
 - [tensorforce/core/policies/parametrized_distributions.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/policies/parametrized_distributions.py)
 - [tensorforce/core/policies/policy.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/policies/policy.py)
 
  
## Purpose and Overview

 The Distribution System in Tensorforce handles probability distributions for action selection in reinforcement learning agents. It transforms neural network outputs into actionable decisions that can be either deterministic (when exploiting learned policies) or stochastic (when exploring the environment). This system is core to implementing various reinforcement learning algorithms, particularly policy gradient methods.

 This page documents the distribution architecture, available distribution types, and how they integrate with policies and learning objectives. For information about the Policy System which uses these distributions, see the [Agent Implementations](https://deepwiki.com/tensorforce/tensorforce/3-agent-implementations) page.

 
## Distribution Architecture

 The Distribution System consists of a base `Distribution` class and several specific implementations for different action types. Each distribution handles transforming raw network outputs into probability distributions, sampling actions from these distributions, and computing various statistical measures required for reinforcement learning algorithms.

 
```

```

 Sources: [tensorforce/core/distributions/distribution.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/distribution.py) [tensorforce/core/distributions/categorical.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/categorical.py) [tensorforce/core/distributions/gaussian.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/gaussian.py) [tensorforce/core/distributions/beta.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/beta.py) [tensorforce/core/distributions/bernoulli.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/bernoulli.py)

 
### Base Distribution Interface

 All distribution implementations derive from the abstract `Distribution` base class, which defines the common interface:

 
```

```

 Sources: [tensorforce/core/distributions/distribution.py19-159](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/distribution.py#L19-L159)

 The key methods in the `Distribution` interface include:

 
 - **parametrize**: Transforms neural network outputs into distribution parameters
 - **mode**: Returns the most likely action (used for deterministic policy execution)
 - **sample**: Samples an action from the distribution (used for exploration)
 - **log_probability**: Computes the log probability of a given action
 - **entropy**: Calculates distribution entropy (measuring uncertainty)
 - **kl_divergence**: Computes KL divergence between two distributions (used in some algorithms like TRPO)
 - **action_value**: Computes action value estimate from distribution parameters
 - **state_value**: Computes state value estimate from distribution parameters
 
 
## Distribution Types

 The framework includes four primary distribution types for different action spaces:

 
### Categorical Distribution

 The `Categorical` distribution handles discrete integer actions. It transforms logits into probabilities using the softmax function.

 **Key characteristics:**

 
 - Used for discrete action spaces (e.g., choosing from N discrete actions)
 - Supports temperature parameter for controlling exploration
 - Optional action masking for constrained action spaces
 
 **Implementation details:**

 
 - Network outputs are transformed into logits for each possible action
 - Softmax function converts logits to probabilities
 - Temperature scaling controls exploration vs. exploitation
 - Sampling uses Gumbel distribution for numerical stability
 
 Sources: [tensorforce/core/distributions/categorical.py25-411](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/categorical.py#L25-L411)

 
### Gaussian Distribution

 The `Gaussian` distribution handles continuous unbounded actions. It parametrizes mean and standard deviation.

 **Key characteristics:**

 
 - Used for continuous unbounded action spaces
 - Can be transformed for bounded action spaces using tanh or clipping
 - Supports predicted or global standard deviation modes
 
 **Implementation details:**

 
 - Network outputs parametrize mean and (optionally) standard deviation
 - Standard deviation uses softplus transformation for numerical stability
 - Sampling adds scaled Gaussian noise to mean
 - Bounded transformations can map unbounded Gaussian samples to bounded ranges
 
 Sources: [tensorforce/core/distributions/gaussian.py25-414](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/gaussian.py#L25-L414)

 
### Beta Distribution

 The `Beta` distribution handles continuous bounded actions directly. It parametrizes alpha and beta shape parameters.

 **Key characteristics:**

 
 - Specifically designed for bounded continuous action spaces
 - Naturally bounded between 0 and 1, then scaled to action range
 - Provides more nuanced control near boundaries than transformed Gaussian
 
 **Implementation details:**

 
 - Network outputs parametrize alpha and beta (both ≥ 1)
 - Sampling uses gamma distribution for generating beta-distributed values
 - Action range scaling maps [0,1] to [min_value, max_value]
 
 Sources: [tensorforce/core/distributions/beta.py25-273](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/beta.py#L25-L273)

 
### Bernoulli Distribution

 The `Bernoulli` distribution handles binary boolean actions. It parametrizes a single probability.

 **Key characteristics:**

 
 - Used for binary action spaces (true/false decisions)
 - Simplest distribution type
 
 **Implementation details:**

 
 - Network output is transformed via sigmoid to get probability
 - Sampling compares probability against uniform random value
 - Mode returns true if probability ≥ 0.5
 
 Sources: [tensorforce/core/distributions/bernoulli.py24-231](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/bernoulli.py#L24-L231)

 
## Distribution Selection Flow

 The following diagram shows how distributions are selected based on action specifications:

 
```

```

 Sources: [tensorforce/core/policies/parametrized_distributions.py86-130](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/policies/parametrized_distributions.py#L86-L130)

 
## Action Selection Process

 The distribution system plays a central role in the action selection process, as shown in the following sequence diagram:

 
```

```

 Sources: [tensorforce/core/policies/parametrized_distributions.py172-237](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/policies/parametrized_distributions.py#L172-L237)

 
## Integration with Policies

 The primary integration point for distributions is the `ParametrizedDistributions` policy class, which manages distribution instances for all action components.

 
```

```

 Sources: [tensorforce/core/policies/parametrized_distributions.py23-441](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/policies/parametrized_distributions.py#L23-L441)

 The `ParametrizedDistributions` policy:

 
 - Creates appropriate distribution objects for each action component
 - Processes states through neural networks to get embeddings
 - Uses these embeddings to parametrize distributions
 - Gets actions by sampling from distributions or taking modes
 - Provides entropy, log probabilities, and other statistics needed for learning
 
 
## Application in Reinforcement Learning Objectives

 Distributions are central to implementing various reinforcement learning objectives:

 
### Policy Gradient Methods

 For policy gradient methods (PPO, TRPO, VPG), distributions provide:

 
 - Action sampling for exploration
 - Log probabilities for computing policy gradient
 - Entropy for exploration bonus
 - KL divergence for trust region methods
 
 
```

```

 Sources: [tensorforce/core/objectives/policy_gradient.py76-152](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/objectives/policy_gradient.py#L76-L152)

 
### Deterministic Policy Gradient

 For DPG and DDPG, distributions (typically Gaussian) are used implicitly to execute the deterministic policy.

 Sources: [tensorforce/core/objectives/deterministic_policy_gradient.py23-91](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/objectives/deterministic_policy_gradient.py#L23-L91)

 
### Value-Based Methods

 For value-based methods (like DQN variants), categorical distributions enable action selection based on Q-values.

 Sources: [tensorforce/core/objectives/value.py22-164](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/objectives/value.py#L22-L164)

 
## Distribution Parametrization Examples

 The following table shows how different distributions are parametrized:

 
| Distribution | Network Output Transform | Parameters | Action Output |
|---|---|---|---|
| Categorical | Linear + Softmax | Probabilities for each discrete action | Index of selected action |
| Gaussian | Linear layers for mean and stddev | Mean and standard deviation | Continuous value, optionally bounded |
| Beta | Linear transforms for alpha and beta | Alpha and beta shape parameters | Value in [min_value, max_value] range |
| Bernoulli | Linear + Sigmoid | Probability of true action | Boolean true/false |

 Sources: [tensorforce/core/distributions/categorical.py142-252](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/categorical.py#L142-L252) [tensorforce/core/distributions/gaussian.py143-186](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/gaussian.py#L143-L186) [tensorforce/core/distributions/beta.py105-134](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/beta.py#L105-L134) [tensorforce/core/distributions/bernoulli.py91-115](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/bernoulli.py#L91-L115)

 
## Parameters and Customization

 Distributions can be customized through various parameters. Some key configuration options:

 
### Categorical Distribution Parameters

 
 - `temperature_mode`: Controls whether temperature is predicted or global
 - `skip_linear`: Option to skip implicit linear layer
 
 
### Gaussian Distribution Parameters

 
 - `stddev_mode`: How standard deviation is parametrized ("predicted" or "global")
 - `bounded_transform`: How to handle bounded action spaces ("clipping" or "tanh")
 
 
### Beta Distribution

 
 - No specific parameters beyond the base distribution parameters
 
 
### Bernoulli Distribution

 
 - No specific parameters beyond the base distribution parameters
 
 
### Temperature Control

 Temperature is a crucial parameter for controlling exploration vs. exploitation:

 
 - Higher temperature values increase exploration
 - Lower values make actions more deterministic
 - Can be specified globally or per-action
 - Can be annealed over time using parameter schedules
 
 Sources: [tensorforce/core/distributions/categorical.py25-45](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/categorical.py#L25-L45) [tensorforce/core/distributions/gaussian.py26-45](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/gaussian.py#L26-L45)

 
## Entropy and Exploration

 Distributions play a key role in exploration through:

 
 - **Action sampling**: Stochastic action selection based on distribution parameters
 - **Entropy calculation**: Measuring the uncertainty in the policy
 - **Entropy regularization**: Adding entropy bonus to encourage exploration
 - **Temperature scaling**: Controlling the randomness of sampling
 
 
```

```

 Sources: [tensorforce/core/distributions/categorical.py383-388](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/categorical.py#L383-L388) [tensorforce/core/distributions/gaussian.py346-354](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/gaussian.py#L346-L354) [tensorforce/core/distributions/beta.py239-254](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/beta.py#L239-L254) [tensorforce/core/distributions/bernoulli.py193-201](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/distributions/bernoulli.py#L193-L201)
