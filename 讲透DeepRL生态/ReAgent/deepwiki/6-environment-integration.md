> 来源: [https://deepwiki.com/facebookresearch/ReAgent/6-environment-integration](https://deepwiki.com/facebookresearch/ReAgent/6-environment-integration)
> DeepWiki facebookresearch/ReAgent | Last indexed: 21 April 2025 (9e707c

# Environment Integration

  Relevant source files 
 - [reagent/gym/agents/agent.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/agents/agent.py)
 - [reagent/gym/agents/post_step.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/agents/post_step.py)
 - [reagent/gym/policies/policy.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/policy.py)
 - [reagent/gym/policies/predictor_policies.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/predictor_policies.py)
 - [reagent/gym/policies/random_policies.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/random_policies.py)
 - [reagent/gym/policies/samplers/continuous_sampler.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/samplers/continuous_sampler.py)
 - [reagent/gym/policies/samplers/discrete_sampler.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/samplers/discrete_sampler.py)
 - [reagent/gym/policies/scorers/discrete_scorer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/scorers/discrete_scorer.py)
 - [reagent/gym/preprocessors/__init__.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/preprocessors/__init__.py)
 - [reagent/gym/preprocessors/trainer_preprocessor.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/preprocessors/trainer_preprocessor.py)
 - [reagent/gym/runners/gymrunner.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/runners/gymrunner.py)
 - [reagent/gym/tests/test_gym.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/test_gym.py)
 - [reagent/gym/tests/test_gym_offline.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/test_gym_offline.py)
 - [reagent/gym/tests/test_world_model.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/test_world_model.py)
 - [reagent/gym/types.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/types.py)
 - [reagent/notebooks/REINFORCE_for_CartPole_Control.ipynb](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/notebooks/REINFORCE_for_CartPole_Control.ipynb)
 
  This page explains how ReAgent interfaces with reinforcement learning environments to enable agent-environment interactions. It covers the architecture and components that allow RL agents to observe states, take actions, and receive rewards from various environment types.

 For information about training with the integrated environments, see [Training System](https://deepwiki.com/facebookresearch/ReAgent/4-training-system). For details on specific model algorithms that can be used with these environments, see [Models and Algorithms](https://deepwiki.com/facebookresearch/ReAgent/3-models-and-algorithms).

 
## Overview

 ReAgent provides a flexible framework for integrating with reinforcement learning environments, primarily focusing on OpenAI Gym but also supporting custom environments. The environment integration system enables:

 
 - Running agents in environments for data collection
 - Online training of policies through direct environment interaction
 - Offline training using replay buffers filled with environment transitions
 - Evaluation of trained policies
 
 
```

```

 Sources: [reagent/gym/agents/agent.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/agents/agent.py) [reagent/gym/policies/policy.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/policy.py) [reagent/gym/runners/gymrunner.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/runners/gymrunner.py)

 
## Core Components

 
### Environment Wrappers

 The `EnvWrapper` class provides a consistent interface for different types of environments. It handles the observation and action spaces, and provides utility methods for preprocessing.

 Primary environment wrapper implementations include:

 
| Wrapper | Purpose |
|---|---|
| Gym | Wraps OpenAI Gym environments (CartPole, MountainCar, etc.) |
| RecSim | Wraps recommendation system simulator environments |
| OraclePVM | Oracle Policy Value Model environment |
| ChangingArms | Multi-armed bandit environment with changing arms |

 Each environment wrapper provides methods to:

 
 - Get observation preprocessors for both training and serving
 - Get action extractors for both training and serving
 - Handle environment-specific configuration
 
 Sources: [reagent/gym/envs/env_wrapper.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/envs/env_wrapper.py)

 
### Agent

 The `Agent` class orchestrates the interactions between policies and environments. It handles:

 
 - Processing observations using preprocessors
 - Obtaining actions from policies
 - Processing post-transition and post-episode callbacks
 
 
```

```

 The agent can be created with factory methods:

 
 - `create_for_env()` - Creates an agent for training
 - `create_for_env_with_serving_policy()` - Creates an agent for serving/evaluation
 
 Sources: [reagent/gym/agents/agent.py21-136](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/agents/agent.py#L21-L136)

 
### Policy, Scorers, and Samplers

 The policy architecture in ReAgent follows a two-step approach:

 
 - **Scorer**: Converts observations to scores
 - **Sampler**: Converts scores to actions
 
 
```

```

 
#### Scorers

 Scorers are functions that take preprocessed observations and output scores that represent the value or preference for different actions:

 
| Scorer Type | Description |
|---|---|
| discrete_dqn_scorer | For DQN models with discrete action spaces |
| parametric_dqn_scorer | For parametric DQN models |
| slate_q_serving_scorer | For slate recommendation models |

 Sources: [reagent/gym/policies/scorers/discrete_scorer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/scorers/discrete_scorer.py)

 
#### Samplers

 Samplers determine how to select actions based on scores:

 
| Sampler | Description |
|---|---|
| SoftmaxActionSampler | Samples actions based on a softmax distribution over scores |
| GreedyActionSampler | Always selects the highest-scoring action |
| EpsilonGreedyActionSampler | Selects random actions with probability ε, otherwise greedy |
| GaussianSampler | For continuous action spaces, samples from a Gaussian distribution |

 Sources: [reagent/gym/policies/samplers/discrete_sampler.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/samplers/discrete_sampler.py) [reagent/gym/policies/samplers/continuous_sampler.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/samplers/continuous_sampler.py)

 
### Transitions and Trajectories

 ReAgent defines data structures to represent agent-environment interactions:

 
 - **Transition**: A single step of interaction (observation, action, reward, next observation, terminal)
 - **Trajectory**: A sequence of transitions that form an episode
 
 
```

```

 Sources: [reagent/gym/types.py20-108](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/types.py#L20-L108)

 
## Integration with Training Systems

 ReAgent provides several ways to integrate environments with training systems:

 
### Online Training

 In online training, the agent interacts with the environment to collect experiences which are immediately used for training:

 
```

```

 This approach is implemented in the `EpisodicDataset` class, which collects complete episodes before training.

 Sources: [reagent/gym/tests/test_gym.py274-326](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/test_gym.py#L274-L326)

 
### Offline Training with Replay Buffers

 In offline training, experiences are first collected and stored in a replay buffer, then used for training:

 
```

```

 The `ReplayBufferDataset` class handles sampling from the replay buffer and preprocessing the data for training.

 Sources: [reagent/gym/tests/test_gym.py183-272](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/test_gym.py#L183-L272)

 
### Gym Runner

 The `GymRunner` provides utilities for running episodes and evaluating policies:

 
 - `run_episode()`: Runs a single episode in an environment
 - `evaluate_for_n_episodes()`: Evaluates a policy over multiple episodes
 
 
```

```

 Sources: [reagent/gym/runners/gymrunner.py25-138](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/runners/gymrunner.py#L25-L138)

 
## Preprocessors

 ReAgent includes preprocessors that transform environment data into formats suitable for model training:

 
### Observation Preprocessors

 Convert raw environment observations to model-compatible formats:

 
 - Scale/normalize numeric features
 - One-hot encode discrete features
 - Process specialized observation types (images, text, etc.)
 
 
### Trainer Preprocessors

 Convert replay buffer samples to model training inputs:

 
| Input Type | Preprocessor |
|---|---|
| DiscreteDqnInput | DiscreteDqnInputMaker |
| PolicyNetworkInput | PolicyNetworkInputMaker |
| ParametricDqnInput | ParametricDqnInputMaker |
| SlateQInput | SlateQInputMaker |
| MemoryNetworkInput | MemoryNetworkInputMaker |
| PolicyGradientInput | PolicyGradientInputMaker |

 Sources: [reagent/gym/preprocessors/trainer_preprocessor.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/preprocessors/trainer_preprocessor.py)

 
## Random Policies

 For exploration or baseline comparison, ReAgent provides random policies:

 
 - `DiscreteRandomPolicy`: Selects random actions from a discrete action space
 - `MultiDiscreteRandomPolicy`: For multi-dimensional discrete action spaces
 - `ContinuousRandomPolicy`: Samples random actions from a continuous action space
 
 The `make_random_policy_for_env()` function automatically creates the appropriate random policy based on the environment's action space.

 Sources: [reagent/gym/policies/random_policies.py18-144](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/random_policies.py#L18-L144)

 
## Example Usage

 Here's a simplified workflow for using environment integration:

 
 - Create an environment wrapper:
 
 
```

```

 
 - Create a policy (e.g., random policy for initial exploration):
 
 
```

```

 
 - Create an agent with the policy:
 
 
```

```

 
 - Create a replay buffer for storing transitions:
 
 
```

```

 
 - Set up a post-step callback to store transitions:
 
 
```

```

 
 - Run episodes to collect data:
 
 
```

```

 
 - Create a trainer and train:
 
 
```

```

 Sources: [reagent/gym/tests/test_gym.py183-272](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/test_gym.py#L183-L272) [reagent/notebooks/REINFORCE_for_CartPole_Control.ipynb](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/notebooks/REINFORCE_for_CartPole_Control.ipynb)

 
## Predictor Policies

 For deploying trained models, ReAgent provides predictor policies that wrap trained models for inference:

 
 - `DiscreteDQNPredictorPolicy`: For discrete action DQN models
 - `ActorPredictorPolicy`: For actor-critic models
 - `create_predictor_policy_from_model()`: Factory function to create the appropriate policy
 
 Sources: [reagent/gym/policies/predictor_policies.py40-139](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/predictor_policies.py#L40-L139)

 
## Conclusion

 The Environment Integration system in ReAgent provides a flexible and comprehensive framework for connecting RL agents with environments. It supports both online and offline training scenarios, various environment types, and different policy architectures.

 This system serves as the foundation for implementing and evaluating reinforcement learning algorithms in ReAgent, bridging the gap between theoretical algorithms and practical applications.
