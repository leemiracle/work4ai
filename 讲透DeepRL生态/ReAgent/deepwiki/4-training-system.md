> 来源: [https://deepwiki.com/facebookresearch/ReAgent/4-training-system](https://deepwiki.com/facebookresearch/ReAgent/4-training-system)
> DeepWiki facebookresearch/ReAgent | Last indexed: 21 April 2025 (9e707c

# Training System

  Relevant source files 
 - [reagent/data/manual_data_module.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/data/manual_data_module.py)
 - [reagent/model_managers/actor_critic_base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/actor_critic_base.py)
 - [reagent/model_managers/discrete_dqn_base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/discrete_dqn_base.py)
 - [reagent/model_managers/model_based/synthetic_reward.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/model_based/synthetic_reward.py)
 - [reagent/model_managers/model_manager.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/model_manager.py)
 - [reagent/model_managers/parametric_dqn_base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/parametric_dqn_base.py)
 - [reagent/model_managers/policy_gradient/ppo.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/policy_gradient/ppo.py)
 - [reagent/model_managers/policy_gradient/reinforce.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/policy_gradient/reinforce.py)
 - [reagent/model_managers/slate_q_base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/slate_q_base.py)
 - [reagent/model_managers/world_model_base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/world_model_base.py)
 - [reagent/models/actor.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/actor.py)
 - [reagent/models/bcq.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/bcq.py)
 - [reagent/models/critic.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/critic.py)
 - [reagent/net_builder/parametric_dqn/fully_connected.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/net_builder/parametric_dqn/fully_connected.py)
 - [reagent/test/models/test_critic.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_critic.py)
 - [reagent/test/models/test_dqn.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_dqn.py)
 - [reagent/test/models/test_dueling_q_network.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_dueling_q_network.py)
 - [reagent/training/reagent_lightning_module.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/reagent_lightning_module.py)
 - [reagent/training/sac_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/sac_trainer.py)
 - [reagent/training/td3_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/td3_trainer.py)
 - [reagent/workflow/training.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/training.py)
 
  The ReAgent Training System provides the core infrastructure for training reinforcement learning models. This document covers the key components of the training workflow, how models are trained, and how the training system integrates with other parts of ReAgent. For information about specific RL algorithms implementation details, see [Models and Algorithms](https://deepwiki.com/facebookresearch/ReAgent/3-models-and-algorithms), and for the data preprocessing that happens before training, see [Data Preprocessing](https://deepwiki.com/facebookresearch/ReAgent/5-data-preprocessing).

 
## Training System Overview

 The ReAgent Training System is built on PyTorch Lightning, providing standardized training loops, distributed training capabilities, and extensive customization options. The system comprises several key components that work together to facilitate effective training of RL models.

 
```

```

 Sources: [reagent/training/reagent_lightning_module.py19-38](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/reagent_lightning_module.py#L19-L38) [reagent/model_managers/model_manager.py36-50](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/model_manager.py#L36-L50) [reagent/workflow/training.py59-79](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/training.py#L59-L79)

 
## Key Components

 
### ReAgentLightningModule

 `ReAgentLightningModule` is the base class for all training modules in ReAgent. It's built on PyTorch Lightning and provides a standardized interface for implementing RL training algorithms.

 Key features of `ReAgentLightningModule`:

 
 - Generator-based training steps through `train_step_gen` method
 - Optimization configuration through `configure_optimizers`
 - Automatic tracking of training metrics and progress
 - Built-in support for incremental training
 - Integration with TensorBoard for visualization
 
 
```

```

 Sources: [reagent/training/reagent_lightning_module.py19-203](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/reagent_lightning_module.py#L19-L203) [reagent/training/sac_trainer.py51-386](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/sac_trainer.py#L51-L386) [reagent/training/td3_trainer.py22-201](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/td3_trainer.py#L22-L201)

 The generator-based training step pattern is a key feature that separates ReAgent's implementation from standard PyTorch Lightning. Rather than a single training step function, trainers implement a generator function `train_step_gen` that yields loss values for different components (e.g., actor loss, critic loss) in a specific order:

 
```

```

 The `training_step` method automatically handles the yielded values and matches them to the appropriate optimizers.

 Sources: [reagent/training/reagent_lightning_module.py107-134](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/reagent_lightning_module.py#L107-L134) [reagent/training/sac_trainer.py196-386](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/sac_trainer.py#L196-L386)

 
### ModelManager

 `ModelManager` is an abstract class that manages how to train models. It serves as a factory for creating trainers, data modules, and serving modules for different types of RL algorithms.

 Key responsibilities of `ModelManager`:

 
 - Building trainer modules with `build_trainer()`
 - Creating data modules for training data with `get_data_module()`
 - Building serving modules for production deployment with `build_serving_modules()`
 - Generating policies for interacting with environments with `create_policy()`
 - Orchestrating the training process with `train()`
 
 
```

```

 Sources: [reagent/model_managers/model_manager.py36-219](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/model_manager.py#L36-L219) [reagent/model_managers/discrete_dqn_base.py54-103](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/discrete_dqn_base.py#L54-L103) [reagent/model_managers/actor_critic_base.py68-194](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/actor_critic_base.py#L68-L194) [reagent/model_managers/world_model_base.py36-88](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/world_model_base.py#L36-L88)

 
### Training Workflow

 The training workflow consists of functions for setting up and executing the training process. The main functions are:

 
 - `identify_and_train_network`: Entry point for the training workflow
 - `query_and_train`: Queries the data and trains the model
 - `train_workflow`: Core function for executing the training process
 
 
```

```

 Sources: [reagent/workflow/training.py59-119](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/training.py#L59-L119) [reagent/workflow/training.py122-244](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/training.py#L122-L244) [reagent/workflow/training.py247-323](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/training.py#L247-L323)

 
## Training Process

 The training process in ReAgent consists of several key steps:

 
 - **Feature Identification**: Determine feature normalization parameters from input data
 - **Data Preparation**: Query and prepare training and evaluation datasets
 - **Trainer Building**: Create a trainer module for the specific algorithm
 - **Model Training**: Execute the training loop with PyTorch Lightning
 - **Validation and Publishing**: Validate and publish the trained model (optional)
 
 
```

```

 Sources: [reagent/workflow/training.py59-119](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/training.py#L59-L119) [reagent/workflow/training.py247-323](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/training.py#L247-L323) [reagent/model_managers/model_manager.py102-177](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/model_manager.py#L102-L177)

 
### Feature Identification and Data Preparation

 Before training begins, ReAgent identifies feature types and normalization parameters. This is done through the data module:

 
 - `ManualDataModule` is the base class for most data modules in ReAgent
 - Each algorithm's specific data module (e.g., `DiscreteDqnDataModule`) implements feature identification and data querying logic
 - Feature identification determines normalization parameters for state, action, and other features
 - Data querying retrieves and formats training and evaluation data
 
 Sources: [reagent/data/manual_data_module.py85-184](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/data/manual_data_module.py#L85-L184) [reagent/model_managers/discrete_dqn_base.py156-211](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/discrete_dqn_base.py#L156-L211) [reagent/model_managers/actor_critic_base.py196-258](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/actor_critic_base.py#L196-L258)

 
### Trainer Building and Execution

 Model managers build trainers specific to each algorithm:

 
 - Each model manager implements `build_trainer()` to create the appropriate trainer
 - Trainers are configured with models, optimizers, and hyperparameters
 - Training is executed through PyTorch Lightning's interface
 - The trainer implements `train_step_gen()` with the algorithm-specific training logic
 
 The training workflow handles the overall orchestration:

 
```

```

 Sources: [reagent/workflow/training.py247-323](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/training.py#L247-L323) [reagent/model_managers/model_manager.py83-177](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/model_manager.py#L83-L177) [reagent/model_managers/discrete_dqn_base.py83-95](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/discrete_dqn_base.py#L83-L95)

 
## Trainer Implementations

 ReAgent provides trainers for various reinforcement learning algorithms. Each trainer implements the algorithm-specific training logic:

 
### Actor-Critic Trainers (SAC, TD3)

 Actor-critic algorithms are implemented with trainers like `SACTrainer` (Soft Actor-Critic) and `TD3Trainer` (Twin Delayed DDPG):

 
```

```

 The `SACTrainer`, for example, implements the following in its `train_step_gen`:

 
 - Q-network updates to minimize TD error
 - Actor network updates to maximize expected Q-value
 - Temperature parameter updates (optional)
 - Value network updates (if using)
 - Soft updates to target networks
 
 Sources: [reagent/training/sac_trainer.py51-386](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/sac_trainer.py#L51-L386) [reagent/training/td3_trainer.py22-201](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/td3_trainer.py#L22-L201) [reagent/models/actor.py22-325](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/actor.py#L22-L325) [reagent/models/critic.py15-92](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/critic.py#L15-L92)

 
### Policy Gradient Trainers (PPO, REINFORCE)

 Policy gradient methods like PPO (Proximal Policy Optimization) are implemented with trainers that optimize policies directly:

 
 - Policy evaluation to estimate advantages
 - Policy updates with clipped objective function (for PPO)
 - Value function updates to reduce advantage estimation error
 
 Sources: [reagent/model_managers/policy_gradient/ppo.py32-128](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/policy_gradient/ppo.py#L32-L128) [reagent/model_managers/policy_gradient/reinforce.py36-134](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/policy_gradient/reinforce.py#L36-L134)

 
### Value-Based Trainers (DQN and variants)

 Value-based methods like DQN (Deep Q-Network) are implemented with trainers that learn Q-values:

 
 - Q-network updates to minimize TD error
 - Target network updates with soft or periodic updates
 - Special variants like Categorical DQN, Quantile Regression DQN, etc.
 
 Sources: [reagent/model_managers/discrete_dqn_base.py54-211](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/discrete_dqn_base.py#L54-L211) [reagent/net_builder/parametric_dqn/fully_connected.py16-54](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/net_builder/parametric_dqn/fully_connected.py#L16-L54)

 
## Integration with Other Components

 The training system integrates with other ReAgent components:

 
 - **Data Preprocessing**: Processed data is provided to trainers through data modules
 - **Model Serving**: Trained models are converted to production-ready formats
 - **Evaluation**: Models can be evaluated during or after training
 - **Environment Integration**: Trained policies can be used with environments
 
 
```

```

 Sources: [reagent/workflow/training.py58-323](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/training.py#L58-L323) [reagent/model_managers/model_manager.py36-219](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/model_manager.py#L36-L219)

 
## Summary

 The ReAgent Training System provides a flexible and extensible framework for training reinforcement learning models. Key features include:

 
 - Integration with PyTorch Lightning for standardized training loops
 - Support for a wide range of RL algorithms
 - Modular architecture with separate components for data, training, and serving
 - Generator-based training steps for complex optimization procedures
 - Validation and publishing mechanisms for model deployment
 
 The training system is designed to be extended with new algorithms by implementing new model managers and trainers, while reusing the core infrastructure for data preparation, training execution, and model deployment.

 Sources: [reagent/workflow/training.py58-323](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/training.py#L58-L323) [reagent/training/reagent_lightning_module.py19-203](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/reagent_lightning_module.py#L19-L203) [reagent/model_managers/model_manager.py36-219](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/model_managers/model_manager.py#L36-L219)
