# deepwiki torchrl §8 training-infrastructure
> 来源: https://deepwiki.com/pytorch/rl/8-training-infrastructure

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

## Training Infrastructure

Relevant source files

  - test/test_helpers.py

  - test/test_trainer.py

  - torchrl/_utils.py

  - torchrl/record/recorder.py

  - torchrl/trainers/helpers/collectors.py

  - torchrl/trainers/helpers/envs.py

  - torchrl/trainers/helpers/losses.py

  - torchrl/trainers/helpers/models.py

  - torchrl/trainers/helpers/trainers.py

  - torchrl/trainers/trainers.py

This page documents TorchRL's training infrastructure, which provides the framework for orchestrating reinforcement learning agent training. The infrastructure separates training loop management from algorithm-specific implementations, enabling flexible and modular training workflows.

The training infrastructure handles data collection orchestration, experience processing, optimization coordination, and training workflow management through a hook-based system.

### Overview

The training infrastructure in TorchRL consists of several key components:

  - Trainer ( torchrl.trainers.Trainer ): The central orchestrator that manages the training loop

  - TrainerHookBase : Base class for extensible training operations

  - Built-in Hooks : Common operations like logging, replay buffer management, and optimization

  - Helper Modules : Utilities for creating environments, models, collectors, and losses

Training Infrastructure Module Structure

```

```

High-level Training Loop Architecture

```

```

Sources:

  - torchrl/trainers/trainers.py 106-279

  - torchrl/trainers/trainers.py 230-269

  - torchrl/trainers/helpers/trainers.py 1-302

  - torchrl/trainers/helpers/envs.py 1-574

  - torchrl/trainers/helpers/models.py 1-647

  - torchrl/trainers/helpers/losses.py 1-133

  - torchrl/trainers/helpers/collectors.py 1-417

### Trainer Class

The `Trainer` class is the central orchestrator of the training infrastructure. It coordinates data collection, batch processing, optimization steps, and logging through a flexible hook system.

#### Key Components and Workflow

The Trainer manages the following required components:

  - collector : A DataCollectorBase that gathers experiences from environments

  - loss_module : A LossModule that computes losses from collected data

  - optimizer : An optim.Optimizer that updates model parameters (optional, can be provided via hooks)

  - logger : A Logger for recording metrics during training (optional)

Trainer Execution Flow (Synchronous Collection)

```

```

Optimization Steps Flow (optim_steps method)

```

```

Sources:

  - torchrl/trainers/trainers.py 650-701

  - torchrl/trainers/trainers.py 703-717

  - torchrl/trainers/trainers.py 729-784

#### Trainer Hook System

The Trainer provides a flexible hook system through the `register_op()` method (alias: `register_hook()`) that allows customizing the training loop without modifying core functionality. Hooks can be registered at various points in the training process:

| Hook Point | Description | Input Type | Output Type | When Called |
| batch_process | Process batches of data after collection | TensorDictBase | TensorDictBase | After data collection, before optimization |
| pre_optim_steps | Operations before optimization loop | None | None | Before optim_steps() method |
| process_optim_batch | Process batches before loss computation | TensorDictBase | TensorDictBase | Within optimization loop, before loss computation |
| post_loss | Operations after loss computation | TensorDictBase | TensorDictBase | After loss computation, before optimizer step |
| optimizer | Custom optimization steps | TensorDictBase, bool, float, int | TensorDictBase | During optimization (gradient computation and parameter updates) |
| post_steps | Operations after all optimization steps | None | None | After optim_steps() completes |
| post_optim | Operations after each optimization step | None | None | After each individual optimization step |
| pre_steps_log | Logging before optimization steps | TensorDictBase | Tuple[str, float] | Before optim_steps() , logs collection metrics |
| post_steps_log | Logging after optimization steps | TensorDictBase | Tuple[str, float] | After optim_steps() , logs evaluation metrics |
| post_optim_log | Logging after each optimization step | TensorDictBase | Tuple[str, float] | After each optimization step, logs training metrics |
| pre_epoch | Operations before each epoch | TensorDictBase | TensorDictBase | Before each epoch in optim_steps() when num_epochs > 1 |
| post_epoch | Operations after each epoch | None | None | After each epoch in optim_steps() when num_epochs > 1 |
| pre_epoch_log | Logging before each epoch | TensorDictBase | Tuple[str, float] | Before each epoch, logs epoch-specific metrics |
| post_epoch_log | Logging after each epoch | TensorDictBase | Tuple[str, float] | After each epoch, logs epoch completion metrics |

Hook Registration Example

```

```

Hook Timing Measurement

All hooks are automatically wrapped with timing measurement when registered. The timing information is stored using the `timeit` utility and can be accessed via `timeit.todict()`. When `log_timings=True` is passed to the Trainer constructor, a `LogTiming` hook is automatically registered to log timing metrics.

Sources:

  - torchrl/trainers/trainers.py 417-529

  - torchrl/trainers/trainers.py 287-313

  - torchrl/trainers/trainers.py 276-278

#### Creating a Trainer

A Trainer can be created manually or using the `make_trainer` helper function:

```

```

Trainer State Tracking

The Trainer maintains several state variables for tracking training progress:

| State Variable | Type | Description |
| collected_frames | int | Total number of frames collected during training |
| _optim_count | int | Total number of optimization steps completed |
| _last_log | dict[str, int] | Tracks when each metric was last logged (for log_interval control) |
| _last_save | int | Tracks when trainer was last saved (for save_interval control) |

Asynchronous Collection

When `async_collection=True`, the trainer runs data collection in a background process while performing optimization. This requires the replay buffer to be registered with the collector. The trainer monitors the replay buffer's `write_count` to track progress and logs the Update-to-Data (UTD) ratio.

Sources:

  - torchrl/trainers/trainers.py 175-227

  - torchrl/trainers/trainers.py 160-173

  - torchrl/trainers/trainers.py 650-717

  - torchrl/trainers/helpers/trainers.py 80-301

### Data Collection Integration

The Trainer integrates with TorchRL's data collection system through the `DataCollectorBase` interface. The collector is responsible for gathering experiences from environments and providing them to the training loop.

#### Collector Interface

The Trainer expects a collector that implements the `DataCollectorBase` interface with the following key methods:

| Method | Purpose |
| __iter__() | Provides batches of collected data |
| set_seed() | Sets random seed for reproducibility |
| shutdown() | Cleanly shuts down collection processes |
| state_dict() / load_state_dict() | Saves/loads collector state |

Data Collection Flow

```

```

Sources:

  - torchrl/trainers/trainers.py 29

  - torchrl/trainers/trainers.py 447-479

### Replay Buffer Integration

#### ReplayBufferTrainer Hook

The `ReplayBufferTrainer` class integrates replay buffers with the Trainer through a set of hooks. It provides three main operations:

  - extend() : Stores new experiences in the buffer

  - sample() : Retrieves batches for optimization

  - update_priority() : Updates priorities for prioritized replay buffers

ReplayBufferTrainer Hook Integration

```

```

#### ReplayBufferTrainer Configuration

The `ReplayBufferTrainer` supports several configuration options:

| Parameter | Type | Description |
| replay_buffer | TensorDictReplayBuffer | The replay buffer instance |
| batch_size | int | Batch size for sampling (optional) |
| memmap | bool | Whether to use memory mapping |
| device | torch.device | Device to move sampled data to |
| flatten_tensordicts | bool | Whether to flatten trajectory data |
| max_dims | Sequence[int] | Maximum dimensions for padding |

```

```

Sources:

  - torchrl/trainers/trainers.py 631-719

  - torchrl/trainers/helpers/trainers.py 214-224

### Built-in Training Hooks

TorchRL provides several built-in hooks that inherit from `TrainerHookBase` for common training operations:

#### Data Processing Hooks

| Hook Class | Purpose | Hook Point | Key Methods |
| SelectKeys | Filters specific keys from batched data | batch_process | __call__(batch) |
| mask_batch | Masks valid events in padded trajectories | batch_process | Function (not a class) |
| BatchSubSampler | Subsamples data for online RL algorithms | process_optim_batch | __call__(batch) |

SelectKeys Implementation

`SelectKeys` filters the input TensorDict to only include specified keys. Useful for reducing memory usage by discarding unnecessary data before storing in replay buffers.

BatchSubSampler Implementation

`BatchSubSampler` randomly subsamples batches for on-policy algorithms. When `sub_traj_len > 0`, it also splits trajectories into fixed-length sub-trajectories.

#### Optimization Hooks

| Hook Class | Purpose | Hook Point | Key Parameters |
| OptimizerHook | Manages optimizer steps for specific loss components | optimizer | optimizer , loss_components , clip_grad_norm |
| ClearCudaCache | Clears CUDA cache periodically | pre_optim_steps | interval |

OptimizerHook Implementation

The `OptimizerHook` provides fine-grained control over optimization:

  - Supports multiple optimizers for different model components

  - Allows selective backpropagation through specific loss components via loss_components parameter

  - Computes and logs gradient norms

  - Can be registered multiple times with different optimizers

```

```

#### Logging Hooks

| Hook Class | Purpose | Hook Point | Key Parameters |
| LogScalar | Logs scalar values from TensorDict | pre_steps_log | in_key , logname , log_pbar |
| CountFramesLog | Logs frame count and FPS | pre_steps_log | frame_skip |
| LogValidationReward | Evaluates and logs validation performance | post_steps_log | environment , policy_exploration , record_frames , record_interval |
| LogTiming | Logs hook execution timing | Any hook point | prefix , percall , erase |

LogScalar Implementation

`LogScalar` extracts scalar values from the collected batch and logs them. Common use cases include logging rewards, episode lengths, and custom metrics.

CountFramesLog Implementation

`CountFramesLog` logs the total number of frames collected and the collection FPS. It uses the `frame_skip` parameter to account for frame skipping in the environment.

LogValidationReward Implementation

`LogValidationReward` periodically evaluates the policy on a validation environment and logs the performance. This is useful for monitoring generalization and avoiding overfitting.

LogTiming Implementation

`LogTiming` logs the execution time of all registered hooks. It uses the `timeit` utility to measure timing and can log either per-call average time or total time. When registered, it automatically wraps all hooks with timing measurement.

#### Weight Update Hooks

| Hook Class | Purpose | Hook Point | Key Parameters |
| UpdateWeights | Updates policy weights in the collector | post_steps | collector , update_weights_interval |

UpdateWeights Implementation

`UpdateWeights` synchronizes the policy weights between the trainer and the collector. This is important when the collector runs on a different device or in a separate process. The `update_weights_interval` parameter controls how often the weights are updated (in terms of optimization steps).

#### Normalization Hooks

| Hook Class | Purpose | Hook Points |
| RewardNormalizer | Normalizes rewards using running statistics | batch_process (update_reward_stats), process_optim_batch (normalize_reward) |

RewardNormalizer Implementation

`RewardNormalizer` maintains running statistics of rewards and normalizes them before passing to the loss module. This can improve training stability but should be used cautiously with algorithms like SAC that depend on reward scale.

Hook Registration and Usage Pattern

```

```

#### Hook State Management

All hooks inherit from `TrainerHookBase` and must implement:

| Method | Purpose | Details |
| state_dict() | Return hook state for checkpointing | Returns a dictionary containing the hook's state |
| load_state_dict(state_dict) | Load hook state from checkpoint | Restores the hook's state from a dictionary |
| register(trainer, name) | Register hook with trainer at default location | Calls trainer.register_op() and trainer.register_module() with appropriate hook points |

Hook Registration Flow

  - Hook calls trainer.register_module(name, self) to register itself in trainer._modules

  - Hook calls trainer.register_op(dest, method, **kwargs) to register specific methods at hook points

  - Trainer wraps the method with timing measurement via _wrap_hook_with_timing()

  - Trainer stores the wrapped method in the appropriate hook list (e.g., _batch_process_ops )

Sources:

  - torchrl/trainers/trainers.py 79-103

  - torchrl/trainers/trainers.py 280-313

  - torchrl/trainers/trainers.py 586-730

  - torchrl/trainers/trainers.py 803-1000

  - torchrl/trainers/trainers.py 1003-1254

### Training Orchestration

#### Complete Training Setup Example

Here's how to set up a complete training workflow using the Trainer and hooks:

```

```

Training Workflow with Hooks

```

```

Sources:

  - torchrl/trainers/trainers.py 447-479

  - torchrl/trainers/trainers.py 491-520

### Helper Modules

TorchRL provides several helper modules to simplify the creation of training components:

#### trainers.py Helper Module

make_trainer Function

The `make_trainer` function creates a fully configured Trainer with common hooks pre-registered:

```

```

TrainerConfig

The `TrainerConfig` dataclass provides configuration options for training:

| Parameter | Type | Default | Description |
| optim_steps_per_batch | int | 500 | Number of optimization steps per data batch |
| optimizer | str | "adam" | Optimizer type ("adam", "sgd", "adamax") |
| lr | float | 3e-4 | Learning rate |
| weight_decay | float | 0.0 | Weight decay for optimizer |
| lr_scheduler | str | "cosine" | Learning rate scheduler type |
| batch_size | int | 256 | Batch size for optimization |
| clip_grad_norm | bool | False | Whether to clip gradient norms |
| clip_norm | float | 1000.0 | Gradient clipping threshold |
| normalize_rewards_online | bool | False | Whether to normalize rewards |
| normalize_rewards_online_scale | float | 1.0 | Final scale of normalized rewards |
| normalize_rewards_online_decay | float | 0.9999 | Decay of reward moving average |
| sub_traj_len | int | -1 | Trajectory length for subsampling |
| selected_keys | list | None | Keys to keep from collected data |

Hooks Registered by make_trainer

The `make_trainer` function automatically registers hooks based on configuration:

```

```

#### envs.py Helper Module

The `envs.py` module provides utilities for creating and configuring environments:

Key Functions

| Function | Purpose |
| transformed_env_constructor(cfg, ...) | Creates environment with transforms |
| parallel_env_constructor(cfg, ...) | Creates parallel environments |
| get_stats_random_rollout(cfg, ...) | Computes observation statistics |
| initialize_observation_norm_transforms(env, ...) | Initializes observation normalization |
| correct_for_frame_skip(cfg) | Adjusts frame counts for frame skip |

EnvConfig

Configuration dataclass for environment creation:

| Parameter | Type | Default | Description |
| env_library | str | "gym" | Environment library ("gym", "dm_control") |
| env_name | str | "Humanoid-v2" | Environment name |
| env_task | str | "" | Task name (for DMControl) |
| from_pixels | bool | False | Whether to use pixel observations |
| frame_skip | int | 1 | Frame skip factor |
| vecnorm | bool | False | Use VecNorm transform |
| catframes | int | 0 | Number of frames to concatenate |
| max_frames_per_traj | int | 1000 | Maximum frames per trajectory |

#### models.py Helper Module

The `models.py` module provides utilities for creating model architectures:

Key Functions

| Function | Purpose |
| make_dqn_actor(proof_environment, cfg, device) | Creates DQN actor |
| make_dreamer(cfg, proof_environment, device, ...) | Creates Dreamer components |

Model Configuration

| Config Class | Purpose |
| DiscreteModelConfig | Configuration for discrete action models (DQN) |
| DreamerConfig | Configuration for Dreamer world model |
| REDQModelConfig | Configuration for REDQ model |

#### losses.py Helper Module

The `losses.py` module provides utilities for creating loss modules:

Key Functions

| Function | Purpose |
| make_dqn_loss(model, cfg) | Creates DQN loss module |
| make_target_updater(cfg, loss_module) | Creates target network updater |

Loss Configuration

| Config Class | Purpose |
| LossConfig | Generic loss configuration |
| A2CLossConfig | A2C-specific loss configuration |
| PPOLossConfig | PPO-specific loss configuration |

#### collectors.py Helper Module

The `collectors.py` module provides utilities for creating data collectors:

Key Functions

| Function | Purpose |
| make_collector_offpolicy(make_env, actor_model_explore, cfg, ...) | Creates off-policy collector |
| make_collector_onpolicy(make_env, actor_model_explore, cfg, ...) | Creates on-policy collector |
| sync_async_collector(env_fns, env_kwargs, ...) | Creates async multi-collector |
| sync_sync_collector(env_fns, env_kwargs, ...) | Creates sync multi-collector |

Collector Configuration

| Config Class | Purpose |
| OnPolicyCollectorConfig | Configuration for on-policy collectors |
| OffPolicyCollectorConfig | Configuration for off-policy collectors |

Sources:

  - torchrl/trainers/helpers/trainers.py 80-301

  - torchrl/trainers/helpers/trainers.py 44-78

  - torchrl/trainers/helpers/envs.py 61-574

  - torchrl/trainers/helpers/models.py 64-647

  - torchrl/trainers/helpers/losses.py 15-133

  - torchrl/trainers/helpers/collectors.py 27-417

### Conclusion

TorchRL's training infrastructure provides a flexible and modular system for training reinforcement learning agents. The core `Trainer` class orchestrates the process, while a rich hook system enables customization at various points in the training loop. Collectors handle data gathering, while replay buffers provide experience storage and sampling.

By separating these concerns and providing helper functions, TorchRL makes it easy to set up complex training workflows while maintaining control over the specifics of data collection, storage, and optimization.

Sources:

  - torchrl/trainers/trainers.py

  - torchrl/trainers/helpers/trainers.py

  - torchrl/collectors/collectors.py



#### On this page

  - Training Infrastructure
  - Overview
  - Trainer Class
  - Key Components and Workflow
  - Trainer Hook System
  - Creating a Trainer
  - Data Collection Integration
  - Collector Interface
  - Replay Buffer Integration
  - ReplayBufferTrainer Hook
  - ReplayBufferTrainer Configuration
  - Built-in Training Hooks
  - Data Processing Hooks
  - Optimization Hooks
  - Logging Hooks
  - Weight Update Hooks
  - Normalization Hooks
  - Hook State Management
  - Training Orchestration
  - Complete Training Setup Example
  - Helper Modules
  - trainers.py Helper Module
  - envs.py Helper Module
  - models.py Helper Module
  - losses.py Helper Module
  - collectors.py Helper Module
  - Conclusion

$!/$$/$
