> 来源: [https://deepwiki.com/araffin/rl-baselines-zoo/2-getting-started](https://deepwiki.com/araffin/rl-baselines-zoo/2-getting-started)
> DeepWiki araffin/rl-baselines-zoo | Last indexed: 24 June 2025 (ff84f3

# Getting Started

  Relevant source files 
 - [README.md](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/README.md?plain=1)
 - [train.py](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/train.py)
 - [utils/utils.py](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/utils.py)
 
  This document provides an overview of the main workflows in the RL Baselines Zoo system: training reinforcement learning agents, evaluating trained models, and understanding the core system components. The RL Baselines Zoo provides a standardized interface for training and evaluating RL agents across multiple algorithms and environments using pre-tuned hyperparameters.

 For detailed information about specific workflows, see [Training Agents](https://deepwiki.com/araffin/rl-baselines-zoo/2.1-training-agents), [Evaluating Trained Agents](https://deepwiki.com/araffin/rl-baselines-zoo/2.2-evaluating-trained-agents), and [Hyperparameter Optimization](https://deepwiki.com/araffin/rl-baselines-zoo/2.3-hyperparameter-optimization). For configuration details, see [Configuration System](https://deepwiki.com/araffin/rl-baselines-zoo/3-configuration-system).

 
## Core System Overview

 The RL Baselines Zoo consists of three primary workflows orchestrated by main entry point scripts:

 **Training Workflow**: Users execute `train.py` to train RL agents using algorithm-specific hyperparameters defined in YAML configuration files.

 **Evaluation Workflow**: Users execute `enjoy.py` to load and evaluate pre-trained agents, observing their behavior in target environments.

 **Optimization Workflow**: Users execute `train.py --optimize` to automatically tune hyperparameters using Optuna-based optimization.

 
### Main System Components

 
```

```

 Sources: [train.py42-435](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/train.py#L42-L435) [utils/utils.py32-43](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/utils.py#L32-L43) [README.md44-78](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/README.md?plain=1#L44-L78)

 
## Algorithm Registry and Environment Support

 The system supports multiple RL algorithms through a centralized registry defined in `utils/utils.py`. Each algorithm integrates with Stable Baselines implementations:

 
```

```

 The system automatically handles environment-specific configurations including Atari frame stacking, continuous control normalization, and custom wrappers through the `create_env()` function in `train.py`.

 Sources: [utils/utils.py32-43](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/utils.py#L32-L43) [train.py147-156](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/train.py#L147-L156) [train.py228-291](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/train.py#L228-L291)

 
## Training Agent Workflow

 
### Basic Training Command Structure

 The primary training interface accepts several key parameters:

 
| Parameter | Purpose | Example |
|---|---|---|
| --algo | RL algorithm selection | ppo2, sac, ddpg |
| --env | Environment identifier | CartPole-v1, HalfCheetah-v2 |
| --n-timesteps | Training duration override | 1000000 |
| --tensorboard-log | TensorBoard logging directory | /tmp/tb_logs/ |
| --eval-freq | Evaluation frequency | 10000 |

 
### Training Process Flow

 
```

```

 The training process loads algorithm-specific hyperparameters from YAML files, creates appropriate environment wrappers, initializes the selected RL algorithm, and saves the trained model with associated configuration files.

 Sources: [train.py130-158](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/train.py#L130-L158) [train.py400-435](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/train.py#L400-L435) [train.py228-291](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/train.py#L228-L291)

 
## Model Storage Structure

 Trained models are stored in a structured directory hierarchy under `trained_agents/` with associated metadata:

 
```

```

 The storage system preserves both the trained model weights and the complete training configuration, including normalization statistics required for proper evaluation.

 Sources: [train.py410-435](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/train.py#L410-L435) [utils/utils.py316-346](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/utils.py#L316-L346) [train.py361-368](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/train.py#L361-L368)

 
## Evaluation Workflow Overview

 Agent evaluation uses the `enjoy.py` script to load trained models and execute them in target environments. The evaluation system automatically handles model loading, environment recreation, and normalization parameter restoration.

 Key evaluation parameters include environment rendering, episode count, and model selection (latest vs. best performing). The evaluation process reconstructs the exact training environment configuration using saved hyperparameters and normalization statistics.

 For complete evaluation details, see [Evaluating Trained Agents](https://deepwiki.com/araffin/rl-baselines-zoo/2.2-evaluating-trained-agents).

 
## Hyperparameter Configuration System

 The system uses YAML configuration files in the `hyperparams/` directory to define algorithm-specific parameters for different environments. Each algorithm has its own configuration file (e.g., `hyperparams/ppo2.yml`, `hyperparams/sac.yml`) containing environment-specific hyperparameter sets.

 The configuration system supports environment categorization (Atari, continuous control, discrete control) and allows runtime hyperparameter overrides via command-line arguments.

 For configuration details, see [Configuration System](https://deepwiki.com/araffin/rl-baselines-zoo/3-configuration-system).

 
## Next Steps

 
 - **Training**: Learn detailed training procedures in [Training Agents](https://deepwiki.com/araffin/rl-baselines-zoo/2.1-training-agents)
 - **Evaluation**: Understand model evaluation in [Evaluating Trained Agents](https://deepwiki.com/araffin/rl-baselines-zoo/2.2-evaluating-trained-agents)
 - **Optimization**: Explore automated hyperparameter tuning in [Hyperparameter Optimization](https://deepwiki.com/araffin/rl-baselines-zoo/2.3-hyperparameter-optimization)
 - **Configuration**: Review system configuration in [Configuration System](https://deepwiki.com/araffin/rl-baselines-zoo/3-configuration-system)
 
 Sources: [README.md20-143](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/README.md?plain=1#L20-L143) [train.py1-435](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/train.py#L1-L435) [utils/utils.py1-392](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/utils.py#L1-L392)
