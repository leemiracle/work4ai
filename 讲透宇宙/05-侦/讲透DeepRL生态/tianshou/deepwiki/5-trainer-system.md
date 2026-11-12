> 来源: [https://deepwiki.com/thu-ml/tianshou/5-trainer-system](https://deepwiki.com/thu-ml/tianshou/5-trainer-system)
> DeepWiki thu-ml/tianshou | Last indexed: 19 April 2025 (90846f

# Trainer System

  Relevant source files 
 - [test/base/test_policy.py](https://github.com/thu-ml/tianshou/blob/90846f6b/test/base/test_policy.py)
 - [test/base/test_stats.py](https://github.com/thu-ml/tianshou/blob/90846f6b/test/base/test_stats.py)
 - [tianshou/data/collector.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/data/collector.py)
 - [tianshou/data/stats.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/data/stats.py)
 - [tianshou/trainer/base.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py)
 - [tianshou/trainer/utils.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/utils.py)
 
  The Trainer System is the central orchestration component in Tianshou that manages the reinforcement learning training process. It coordinates data collection, policy updates, and evaluation while tracking training progress and statistics. This document explains the architecture, components, and operation of the Trainer System. For information about specific data collection mechanisms, see [Data Handling System](https://deepwiki.com/thu-ml/tianshou/2-data-handling-system) or for policy-specific details, see [Policy Framework](https://deepwiki.com/thu-ml/tianshou/3-policy-framework).

 
## Core Concepts

 The Trainer System provides an iterator-based interface that executes training epochs and yields results. Each trainer type (on-policy, off-policy, or offline) implements a specialized training loop appropriate for different reinforcement learning paradigms.

 
### Trainer Responsibilities

 
 - Coordinating data collection through collectors
 - Managing policy updates and gradient steps
 - Evaluating policy performance
 - Tracking and logging statistics
 - Implementing stopping criteria
 - Checkpoint saving and restoration
 
 Sources: [tianshou/trainer/base.py36-102](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L36-L102)

 
## Trainer Architecture

 The Trainer System is built around a class hierarchy with `BaseTrainer` as the abstract base class and specialized implementations for different reinforcement learning approaches.

 
#### Trainer Class Hierarchy

 
```

```

 Sources: [tianshou/trainer/base.py36-102](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L36-L102) [tianshou/trainer/base.py656-676](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L656-L676) [tianshou/trainer/base.py678-717](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L678-L717) [tianshou/trainer/base.py721-753](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L721-L753) [tianshou/data/stats.py103-119](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/data/stats.py#L103-L119)

 
## Training Loop Process

 The training process operates as an iterator, where each iteration corresponds to one epoch of training. This design allows for flexible integration with other code, easy visualization, and checkpoint management.

 
```

```

 Sources: [tianshou/trainer/base.py315-415](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L315-L415) [tianshou/trainer/base.py458-487](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L458-L487)

 
### Key Components of the Training Loop

 
 - **Epoch Iteration (`__next__`)**: Executes one complete epoch of training, including multiple training steps and potentially an evaluation phase.
 - **Training Step (`training_step`)**: Performs one training iteration, which includes:

 
 - Collecting data from the environment
 - Checking stopping criteria
 - Updating the policy if training should continue
 - **Policy Update (`policy_update_fn`)**: Abstract method implemented differently for each trainer type to update the policy based on collected data.
 - **Evaluation (`test_step`)**: Evaluates the policy's performance and records metrics.
 
 Sources: [tianshou/trainer/base.py315-415](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L315-L415) [tianshou/trainer/base.py458-487](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L458-L487) [tianshou/trainer/base.py417-456](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L417-L456)

 
## Trainer Types

 Tianshou provides three specialized trainer implementations for different reinforcement learning paradigms:

 
### Off-policy Trainer

 The `OffpolicyTrainer` is designed for algorithms like DQN, SAC, and TD3 that can learn from previously collected experiences. It samples mini-batches from a replay buffer for multiple gradient steps per collection step.

 
```

```

 Key characteristics:

 
 - Samples mini-batches from a replay buffer
 - Performs multiple gradient steps per collection step
 - Policy learns from past experiences
 
 Sources: [tianshou/trainer/base.py678-717](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L678-L717)

 
### On-policy Trainer

 The `OnpolicyTrainer` is designed for algorithms like PPO and A2C that require fresh data for each update. It passes the entire buffer to the policy's update method and clears the buffer afterward.

 
```

```

 Key characteristics:

 
 - Uses the entire collected buffer for updates
 - Policy typically performs internal mini-batching
 - Requires fresh data for each update
 
 Sources: [tianshou/trainer/base.py721-753](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L721-L753)

 
### Offline Trainer

 The `OfflineTrainer` is for algorithms that learn entirely from a fixed dataset without additional data collection. It samples mini-batches from the provided buffer.

 
```

```

 Key characteristics:

 
 - No online data collection
 - Learns from a fixed, pre-collected dataset
 - Focused on efficient use of existing data
 
 Sources: [tianshou/trainer/base.py656-676](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L656-L676)

 
## Data Flow in Training Loop

 The following diagram illustrates how data flows through the Trainer System during the training process:

 
```

```

 Sources: [tianshou/trainer/base.py458-487](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L458-L487) [tianshou/trainer/base.py489-529](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L489-L529)

 
## Statistics and Metrics

 The Trainer System maintains various statistics to track training progress and performance. These statistics are organized into several data structures:

 
### Statistics Data Structures

 
| Data Structure | Purpose | Key Fields |
|---|---|---|
| EpochStats | Results from one training epoch | epoch, train_collect_stat, test_collect_stat, training_stat, info_stat |
| CollectStats | Statistics from data collection | n_collected_episodes, n_collected_steps, returns, lens |
| TrainingStats | Statistics from policy updates | train_time, loss_stats |
| InfoStats | Overall training information | gradient_step, best_score, timing |

 The statistics system includes:

 
 - **Collection Statistics**: Track data collection metrics like episode returns, lengths, and step counts.
 - **Training Statistics**: Record policy update metrics like loss values and training time.
 - **Information Statistics**: Store overall metrics like total steps, best performance, and timing information.
 
 Sources: [tianshou/data/stats.py17-119](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/data/stats.py#L17-L119) [tianshou/trainer/utils.py41-87](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/utils.py#L41-L87)

 
## Usage Example

 The Trainer System is designed to be used as an iterator, making it easy to integrate with other code:

 
```

```

 Sources: [tianshou/trainer/base.py116-150](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L116-L150) [tianshou/trainer/base.py614-643](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L614-L643)

 
## Relationship with Other Systems

 
```

```

 The Trainer System sits at the center of Tianshou, orchestrating interactions between:

 
 - **Policy Framework** ([Policy Framework](https://deepwiki.com/thu-ml/tianshou/3-policy-framework)): Provides the learning algorithms that the trainer updates
 - **Data Handling System** ([Data Handling System](https://deepwiki.com/thu-ml/tianshou/2-data-handling-system)): Collects experiences and stores them in buffers
 - **Environment System** ([Environment System](https://deepwiki.com/thu-ml/tianshou/4-environment-system)): Provides the simulation environment for the agent to interact with
 
 Sources: [tianshou/trainer/base.py153-239](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L153-L239)

 
## Advanced Features

 
### Hooks and Callbacks

 The Trainer System supports several hooks for customizing the training process:

 
 - `train_fn`: Called at the beginning of each training collection
 - `test_fn`: Called at the beginning of each evaluation
 - `save_best_fn`: Called when a new best policy is found
 - `save_checkpoint_fn`: Called at the end of each epoch to save checkpoints
 - `stop_fn`: Defines the stopping criterion for training
 
 
### Training Loop Configuration

 Several parameters control the training process:

 
 - `step_per_epoch`: Number of environment steps per training epoch
 - `update_per_step`: Number of gradient steps per environment step (off-policy)
 - `repeat_per_collect`: Number of optimization rounds per data collection (on-policy)
 - `episode_per_test`: Number of episodes for evaluation
 
 Sources: [tianshou/trainer/base.py153-239](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/trainer/base.py#L153-L239)
