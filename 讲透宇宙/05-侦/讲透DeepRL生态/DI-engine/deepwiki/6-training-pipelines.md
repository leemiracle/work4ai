> 来源: [https://deepwiki.com/opendilab/DI-engine/6-training-pipelines](https://deepwiki.com/opendilab/DI-engine/6-training-pipelines)
> DeepWiki opendilab/DI-engine | Last indexed: 20 April 2025 (c290a6

# Training Pipelines

  Relevant source files 
 - [ding/entry/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/__init__.py)
 - [ding/entry/serial_entry.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/serial_entry.py)
 - [ding/entry/serial_entry_onpolicy.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/serial_entry_onpolicy.py)
 - [ding/entry/tests/test_serial_entry.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/tests/test_serial_entry.py)
 - [ding/entry/tests/test_serial_entry_algo.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/tests/test_serial_entry_algo.py)
 - [ding/model/template/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/__init__.py)
 - [ding/policy/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/__init__.py)
 - [ding/policy/command_mode_policy_instance.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/command_mode_policy_instance.py)
 - [ding/reward_model/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/reward_model/__init__.py)
 - [ding/rl_utils/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/rl_utils/__init__.py)
 - [ding/worker/collector/battle_interaction_serial_evaluator.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/battle_interaction_serial_evaluator.py)
 - [ding/worker/collector/battle_sample_serial_collector.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/battle_sample_serial_collector.py)
 - [ding/worker/collector/interaction_serial_evaluator.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/interaction_serial_evaluator.py)
 - [ding/worker/collector/sample_serial_collector.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/sample_serial_collector.py)
 - [dizoo/atari/config/serial/pong/pong_dqn_ddp_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/config/serial/pong/pong_dqn_ddp_config.py)
 - [dizoo/atari/config/serial/pong/pong_ppo_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/config/serial/pong/pong_ppo_config.py)
 - [dizoo/atari/config/serial/pong/pong_ppo_ddp_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/config/serial/pong/pong_ppo_ddp_config.py)
 - [dizoo/atari/example/atari_dqn_ddp.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/example/atari_dqn_ddp.py)
 - [dizoo/atari/example/atari_ppo.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/example/atari_ppo.py)
 - [dizoo/atari/example/atari_ppo_ddp.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/example/atari_ppo_ddp.py)
 - [dizoo/classic_control/cartpole/config/cartpole_dqn_ddp_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/classic_control/cartpole/config/cartpole_dqn_ddp_config.py)
 - [dizoo/classic_control/cartpole/config/cartpole_ppo_ddp_config.py](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/classic_control/cartpole/config/cartpole_ppo_ddp_config.py)
 
  
## Overview

 Training Pipelines in DI-engine orchestrate the reinforcement learning (RL) training process by coordinating interactions between policies, environments, data collection, and learning components. They provide standardized workflows for different types of RL algorithms (off-policy, on-policy, offline, etc.) while abstracting away common implementation details.

 This document focuses on the architecture and functionality of training pipelines within DI-engine. For information about specific policies, see [Policy System](https://deepwiki.com/opendilab/DI-engine/4-policy-system), and for environment integration, see [Environment System](https://deepwiki.com/opendilab/DI-engine/3-environment-system).

 
## Key Components

 The training pipeline system consists of several key components that work together to implement the complete RL training loop:

 
```

```

 Sources:

 
 - [ding/entry/serial_entry.py18-147](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/serial_entry.py#L18-L147)
 - [ding/worker/collector/sample_serial_collector.py15-226](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/sample_serial_collector.py#L15-L226)
 - [ding/worker/collector/interaction_serial_evaluator.py13-184](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/interaction_serial_evaluator.py#L13-L184)
 
 
### Component Descriptions

 
 - **Commander**: Coordinates the overall training process, providing commands to collectors, evaluators, and learners.
 - **Collector**: Interacts with environments to collect experience data by executing the current policy.
 - **Evaluator**: Periodically assesses policy performance in evaluation environments.
 - **Learner**: Updates the policy based on collected experience data.
 - **Replay Buffer**: Stores collected experiences for off-policy learning algorithms.
 - **Policy (Command Mode)**: RL algorithm implementation that generates actions and learns from experiences.
 - **Environment Manager**: Manages multiple environment instances for data collection and evaluation.
 
 
## Pipeline Types

 DI-engine provides different types of pipelines tailored to specific RL paradigms:

 
### Serial Pipeline (Off-Policy)

 The standard pipeline for off-policy algorithms (e.g., DQN, SAC, TD3) that use experience replay.

 
```

```

 Sources:

 
 - [ding/entry/serial_entry.py18-147](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/serial_entry.py#L18-L147)
 
 
### On-Policy Serial Pipeline

 Specialized pipeline for on-policy algorithms (e.g., PPO, A2C) that learn directly from newly collected data.

 
```

```

 Sources:

 
 - [ding/entry/serial_entry_onpolicy.py18-126](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/serial_entry_onpolicy.py#L18-L126)
 
 
### Offline Serial Pipeline

 Pipeline for offline RL algorithms (e.g., CQL, TD3+BC) that learn from pre-collected datasets.

 
### Distributed Pipelines

 Support for multi-GPU training using PyTorch's Distributed Data Parallel (DDP).

 
## Data Flow

 The training pipeline orchestrates data flow between components during the reinforcement learning process:

 
```

```

 Sources:

 
 - [ding/entry/serial_entry.py96-128](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/serial_entry.py#L96-L128)
 - [ding/worker/collector/sample_serial_collector.py224-324](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/sample_serial_collector.py#L224-L324)
 - [ding/worker/collector/interaction_serial_evaluator.py184-322](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/interaction_serial_evaluator.py#L184-L322)
 
 
## Command Mode Integration

 Training pipelines in DI-engine use a command mode interface to standardize interactions with different policy types. This design allows the pipeline to work with various RL algorithms through a consistent interface.

 
```

```

 Sources:

 
 - [ding/policy/command_mode_policy_instance.py1-469](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/command_mode_policy_instance.py#L1-L469)
 - [ding/entry/serial_entry.py69-91](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/serial_entry.py#L69-L91)
 
 
## Pipeline Configuration and Usage

 
### Basic Configuration Structure

 A typical pipeline configuration consists of environment settings, policy settings, and component-specific settings:

 
```

```

 Sources:

 
 - [dizoo/atari/config/serial/pong/pong_ppo_config.py3-52](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/config/serial/pong/pong_ppo_config.py#L3-L52)
 - [dizoo/atari/config/serial/pong/pong_ppo_ddp_config.py3-53](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/config/serial/pong/pong_ppo_ddp_config.py#L3-L53)
 
 
### Usage Example

 Here's how to use the serial pipeline for training:

 
```

```

 
### Distributed Training

 DI-engine supports distributed training using PyTorch DDP:

 
```

```

 Sources:

 
 - [dizoo/atari/config/serial/pong/pong_dqn_ddp_config.py56-67](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/config/serial/pong/pong_dqn_ddp_config.py#L56-L67)
 - [dizoo/atari/config/serial/pong/pong_ppo_ddp_config.py66-76](https://github.com/opendilab/DI-engine/blob/c290a673/dizoo/atari/config/serial/pong/pong_ppo_ddp_config.py#L66-L76)
 
 
## Collector and Evaluator Implementation

 
### Collector

 The collector is responsible for gathering experience data through environment interactions:

 
| Collector Type | Description | Use Case |
|---|---|---|
| SampleSerialCollector | Collects individual transitions | General off-policy algorithms |
| EpisodeSerialCollector | Collects complete episodes | Some on-policy algorithms |
| BattleSampleSerialCollector | Collects data from multi-agent environments | Multi-agent RL |

 The collector's main operation is the `collect` method, which:

 
 - Gets observations from environments
 - Forwards observations to the policy to get actions
 - Executes actions in environments
 - Processes the resulting transitions
 - Returns collected data for training
 
 Sources:

 
 - [ding/worker/collector/sample_serial_collector.py224-378](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/sample_serial_collector.py#L224-L378)
 - [ding/worker/collector/battle_sample_serial_collector.py213-323](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/battle_sample_serial_collector.py#L213-L323)
 
 
### Evaluator

 The evaluator periodically assesses policy performance:

 
| Evaluator Type | Description | Use Case |
|---|---|---|
| InteractionSerialEvaluator | Standard single-agent evaluator | Most RL tasks |
| BattleInteractionSerialEvaluator | Multi-agent evaluator | Multi-agent RL tasks |

 The evaluator's main operation is the `eval` method, which:

 
 - Runs the policy for a specified number of episodes
 - Computes performance metrics
 - Logs results
 - Saves checkpoints of the best performing policy
 - Determines if the training should stop based on performance
 
 Sources:

 
 - [ding/worker/collector/interaction_serial_evaluator.py184-325](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/interaction_serial_evaluator.py#L184-L325)
 - [ding/worker/collector/battle_interaction_serial_evaluator.py171-277](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/battle_interaction_serial_evaluator.py#L171-L277)
 
 
## Supported Algorithms

 The pipeline system supports a wide range of reinforcement learning algorithms:

 
| Algorithm Type | Examples | Pipeline Type |
|---|---|---|
| Value-Based | DQN, C51, QR-DQN, IQN, Rainbow | Serial Pipeline |
| Policy Gradient | PG, A2C | Serial Pipeline OnPolicy |
| Actor-Critic | PPO, IMPALA, ACER | Serial Pipeline OnPolicy |
| Off-Policy Actor-Critic | SAC, TD3, DDPG | Serial Pipeline |
| Multi-Agent | QMIX, WQMIX, COMA, ATOC | Serial Pipeline with specialized collectors/evaluators |
| Offline RL | CQL, TD3+BC, DT | Serial Pipeline Offline |

 Sources:

 
 - [ding/entry/tests/test_serial_entry.py59-146](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/tests/test_serial_entry.py#L59-L146)
 - [ding/entry/tests/test_serial_entry_algo.py54-450](https://github.com/opendilab/DI-engine/blob/c290a673/ding/entry/tests/test_serial_entry_algo.py#L54-L450)
 - [ding/model/template/__init__.py1-32](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/__init__.py#L1-L32)
 - [ding/policy/__init__.py1-60](https://github.com/opendilab/DI-engine/blob/c290a673/ding/policy/__init__.py#L1-L60)
 
 
## Conclusion

 The Training Pipeline system in DI-engine provides a flexible and unified framework for implementing reinforcement learning algorithms. By standardizing the training workflow and component interactions, it allows researchers and practitioners to focus on algorithm development rather than infrastructure. The pipelines support a wide range of RL paradigms, from traditional off-policy and on-policy methods to offline RL and multi-agent systems, making DI-engine a versatile platform for reinforcement learning research and applications.
