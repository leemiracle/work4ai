> 来源: [https://deepwiki.com/facebookresearch/ReAgent/3-models-and-algorithms](https://deepwiki.com/facebookresearch/ReAgent/3-models-and-algorithms)
> DeepWiki facebookresearch/ReAgent | Last indexed: 21 April 2025 (9e707c

# Models and Algorithms

  Relevant source files 
 - [reagent/evaluation/cb/synthetic_contextual_bandit_data.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/cb/synthetic_contextual_bandit_data.py)
 - [reagent/evaluation/evaluation_data_page.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/evaluation_data_page.py)
 - [reagent/gym/policies/scorers/continuous_scorer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/scorers/continuous_scorer.py)
 - [reagent/models/__init__.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/__init__.py)
 - [reagent/models/actor.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/actor.py)
 - [reagent/models/bcq.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/bcq.py)
 - [reagent/models/cb_base_model.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/cb_base_model.py)
 - [reagent/models/cb_fully_connected_network.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/cb_fully_connected_network.py)
 - [reagent/models/critic.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/critic.py)
 - [reagent/models/deep_represent_linucb.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/deep_represent_linucb.py)
 - [reagent/models/linear_regression.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/linear_regression.py)
 - [reagent/models/seq2slate.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/seq2slate.py)
 - [reagent/net_builder/parametric_dqn/fully_connected.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/net_builder/parametric_dqn/fully_connected.py)
 - [reagent/net_builder/synthetic_reward_net_builder.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/net_builder/synthetic_reward_net_builder.py)
 - [reagent/preprocessing/identify_types.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/preprocessing/identify_types.py)
 - [reagent/test/models/test_cb_fully_connected.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_cb_fully_connected.py)
 - [reagent/test/models/test_critic.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_critic.py)
 - [reagent/test/models/test_deep_represent_linucb_model.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_deep_represent_linucb_model.py)
 - [reagent/test/models/test_dqn.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_dqn.py)
 - [reagent/test/models/test_dueling_q_network.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_dueling_q_network.py)
 - [reagent/test/models/test_linear_regression_ucb.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_linear_regression_ucb.py)
 - [reagent/test/training/cb/test_deep_represent_linucb.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/training/cb/test_deep_represent_linucb.py)
 - [reagent/test/training/cb/test_linucb.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/training/cb/test_linucb.py)
 - [reagent/training/c51_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/c51_trainer.py)
 - [reagent/training/cb/base_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cb/base_trainer.py)
 - [reagent/training/cb/deep_represent_linucb_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cb/deep_represent_linucb_trainer.py)
 - [reagent/training/cb/linucb_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cb/linucb_trainer.py)
 - [reagent/training/cb/supervised_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cb/supervised_trainer.py)
 - [reagent/training/cfeval/bayes_by_backprop_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cfeval/bayes_by_backprop_trainer.py)
 - [reagent/training/discrete_crr_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/discrete_crr_trainer.py)
 - [reagent/training/dqn_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer.py)
 - [reagent/training/dqn_trainer_base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer_base.py)
 - [reagent/training/multi_stage_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/multi_stage_trainer.py)
 - [reagent/training/qrdqn_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/qrdqn_trainer.py)
 - [reagent/training/reagent_lightning_module.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/reagent_lightning_module.py)
 - [reagent/training/sac_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/sac_trainer.py)
 - [reagent/training/td3_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/td3_trainer.py)
 
  This document provides an overview of the reinforcement learning (RL) and contextual bandit (CB) algorithms implemented in ReAgent. It covers the core model architectures, value-based methods like DQN, policy-based methods like SAC, and contextual bandit algorithms like LinUCB. For information about data structures used by these algorithms, see [Core Data Structures](https://deepwiki.com/facebookresearch/ReAgent/2-core-data-structures). For details about how models are trained, see [Training System](https://deepwiki.com/facebookresearch/ReAgent/4-training-system).

 
## Algorithm Architecture Overview

 ReAgent implements a wide range of reinforcement learning and contextual bandit algorithms with a modular, component-based design pattern. This modular structure enables algorithm customization while maintaining a consistent interface.

 
```

```

 Sources:

 
 - [reagent/models/base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/base.py)
 - [reagent/models/cb_base_model.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/cb_base_model.py)
 - [reagent/training/reagent_lightning_module.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/reagent_lightning_module.py)
 - [reagent/training/rl_trainer_pytorch.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/rl_trainer_pytorch.py)
 - [reagent/training/dqn_trainer_base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer_base.py)
 - [reagent/training/cb/base_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cb/base_trainer.py)
 
 
## Core Model Types

 ReAgent provides several model architectures that serve as building blocks for reinforcement learning and contextual bandit algorithms.

 
### Base Model Classes

 All models in ReAgent inherit from `ModelBase`, which defines a common interface including:

 
 - `forward()`: The model's forward pass
 - `input_prototype()`: An example input for tracing/serialization
 
 Contextual bandit models specifically inherit from `UCBBaseModel`, which adds interfaces for uncertainty estimation:

 
 - `forward(inp, ucb_alpha)`: Produces predictions with uncertainty
 - `forward_inference()`: Specialized inference method compatible with serving
 
 Sources:

 
 - [reagent/models/base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/base.py)
 - [reagent/models/cb_base_model.py15-46](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/cb_base_model.py#L15-L46)
 
 
### Common Neural Network Architectures

 The core neural network building blocks include:

 
 - **FullyConnectedNetwork**: A multi-layer perceptron with configurable activations
 - **FullyConnectedDQN**: A DQN-specific network that maps states to Q-values
 - **FullyConnectedActor**: Network that maps states to actions for policy gradient methods
 - **FullyConnectedCritic**: Network that maps state-action pairs to Q-values
 
 
```

```

 Sources:

 
 - [reagent/models/fully_connected_network.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/fully_connected_network.py)
 - [reagent/models/dqn.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/dqn.py)
 - [reagent/models/actor.py44-68](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/actor.py#L44-L68)
 - [reagent/models/critic.py37-89](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/critic.py#L37-L89)
 - [reagent/models/linear_regression.py92-251](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/linear_regression.py#L92-L251)
 - [reagent/models/cb_fully_connected_network.py17-64](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/cb_fully_connected_network.py#L17-L64)
 
 
## Value-Based Algorithms

 ReAgent implements several value-based reinforcement learning algorithms that learn a value function to determine the optimal policy.

 
### DQN (Deep Q-Network)

 The DQN algorithm learns an action-value function (Q-function) using neural networks and experience replay.

 
```

```

 Key characteristics:

 
 - Experience replay to break correlations in the observation sequence
 - Target networks to provide stable learning targets
 - TD learning with bootstrap targets
 - Variants including Double Q-learning, Dueling architecture, and distributional approaches
 
 Sources:

 
 - [reagent/training/dqn_trainer.py28-362](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer.py#L28-L362)
 - [reagent/training/dqn_trainer_base.py81-494](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer_base.py#L81-L494)
 - [reagent/training/qrdqn_trainer.py22-228](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/qrdqn_trainer.py#L22-L228)
 - [reagent/training/c51_trainer.py18-298](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/c51_trainer.py#L18-L298)
 
 
### Distributional RL Algorithms

 ReAgent includes distributional RL approaches that model the entire distribution of returns instead of just the expected value:

 
 - **QR-DQN (Quantile Regression DQN)**: Models return distributions using quantile regression
 - **C51 (Categorical 51)**: Represents the return distribution using a fixed set of 51 points
 
 These algorithms provide better uncertainty estimates and more stable learning in environments with stochastic rewards.

 Sources:

 
 - [reagent/training/qrdqn_trainer.py22-228](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/qrdqn_trainer.py#L22-L228)
 - [reagent/training/c51_trainer.py18-298](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/c51_trainer.py#L18-L298)
 
 
## Policy-Based Algorithms

 ReAgent implements several policy-based and actor-critic algorithms that directly optimize the policy.

 
### SAC (Soft Actor-Critic)

 SAC is an off-policy actor-critic algorithm that maximizes a trade-off between expected return and entropy (exploration).

 
```

```

 Key characteristics:

 
 - Maximum entropy framework for exploration and robustness
 - Off-policy learning for sample efficiency
 - Automatic temperature tuning to adjust exploration
 - Continuous action spaces
 
 Sources:

 
 - [reagent/training/sac_trainer.py51-461](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/sac_trainer.py#L51-L461)
 
 
### TD3 (Twin Delayed DDPG)

 TD3 is an actor-critic algorithm that improves upon DDPG with several stabilizing techniques:

 
 - Twin critics to reduce overestimation bias
 - Delayed policy updates
 - Target policy smoothing
 
 It's particularly effective for continuous control tasks.

 Sources:

 
 - [reagent/training/td3_trainer.py22-258](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/td3_trainer.py#L22-L258)
 
 
### CRR (Critic Regularized Regression)

 CRR is an offline reinforcement learning algorithm that addresses the challenges of learning from fixed datasets without environment interaction.

 
```

```

 Key characteristics:

 
 - Offline RL algorithm (learns from fixed datasets)
 - Uses a form of weighted behavior cloning based on advantages
 - Filtering mechanism to only learn from high-advantage actions
 - More conservative than standard actor-critic methods
 
 Sources:

 
 - [reagent/training/discrete_crr_trainer.py25-441](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/discrete_crr_trainer.py#L25-L441)
 
 
## Contextual Bandit Algorithms

 ReAgent provides several contextual bandit algorithms for scenarios where full reinforcement learning may be overkill, or when immediate rewards are available.

 
### LinUCB (Linear Upper Confidence Bound)

 LinUCB is a contextual bandit algorithm that models the expected reward linearly with respect to features and uses confidence bounds for exploration.

 
```

```

 Key characteristics:

 
 - Efficient linear model with uncertainty estimates
 - Upper Confidence Bound for exploration-exploitation trade-off
 - Closed-form solution for linear regression parameters
 - Theoretical regret guarantees
 
 Sources:

 
 - [reagent/models/linear_regression.py92-251](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/linear_regression.py#L92-L251)
 - [reagent/training/cb/linucb_trainer.py19-97](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cb/linucb_trainer.py#L19-L97)
 - [reagent/test/training/cb/test_linucb.py53-320](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/training/cb/test_linucb.py#L53-L320)
 
 
### Deep Represent LinUCB

 Deep Represent LinUCB combines deep neural networks with LinUCB by using a neural network to learn a representation of the features, which is then fed into a LinUCB model.

 
```

```

 Key characteristics:

 
 - Two-stage model: deep representation + LinUCB
 - End-to-end training with dual optimization
 - Neural network learns feature representation
 - LinUCB layer provides uncertainty estimates
 - Combines the expressiveness of deep learning with exploration properties of LinUCB
 
 Sources:

 
 - [reagent/models/deep_represent_linucb.py16-210](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/deep_represent_linucb.py#L16-L210)
 - [reagent/training/cb/deep_represent_linucb_trainer.py18-92](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cb/deep_represent_linucb_trainer.py#L18-L92)
 - [reagent/test/models/test_deep_represent_linucb_model.py9-60](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_deep_represent_linucb_model.py#L9-L60)
 
 
### Supervised Contextual Bandit Training

 For cases where exploration is not needed, ReAgent provides a simple supervised learning approach for contextual bandits:

 
```

```

 Key characteristics:

 
 - Simple supervised learning approach (no exploration)
 - Supports multiple loss functions (MSE, MAE, Cross-Entropy)
 - Useful for offline policy learning or when exploration is handled separately
 
 Sources:

 
 - [reagent/models/cb_fully_connected_network.py17-64](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/cb_fully_connected_network.py#L17-L64)
 - [reagent/training/cb/supervised_trainer.py15-64](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cb/supervised_trainer.py#L15-L64)
 - [reagent/test/models/test_cb_fully_connected.py12-24](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_cb_fully_connected.py#L12-L24)
 
 
## Model Evaluation and Counterfactual Policy Evaluation

 ReAgent includes robust evaluation systems for assessing model performance, particularly for off-policy evaluation.

 
```

```

 Key features of the evaluation system:

 
 - Counterfactual policy evaluation for off-policy learning
 - Multiple estimators (Direct Method, IPS, Doubly Robust)
 - Value computation for multi-step returns
 - Support for both discrete and continuous action spaces
 
 Sources:

 
 - [reagent/evaluation/evaluation_data_page.py30-598](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/evaluation_data_page.py#L30-L598)
 - [reagent/training/cb/base_trainer.py23-199](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cb/base_trainer.py#L23-L199)
 
 
## Conclusion

 ReAgent provides a rich set of reinforcement learning and contextual bandit algorithms with a modular architecture. The framework is designed to be flexible, allowing users to mix and match components as needed for their specific use cases.

 Key strengths of the ReAgent models and algorithms:

 
 - Comprehensive support for both value-based and policy-based methods
 - Strong contextual bandit implementations, including advanced models like Deep Represent LinUCB
 - Integration with PyTorch Lightning for efficient training
 - Robust evaluation systems including counterfactual policy evaluation
 - Support for both online and offline reinforcement learning paradigms
 
 This overview covers the main models and algorithms in ReAgent, but the framework is continuously evolving with new algorithms and improvements.
