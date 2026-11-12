> 来源: [https://deepwiki.com/OpenRL-Lab/openrl/6-configuration-system](https://deepwiki.com/OpenRL-Lab/openrl/6-configuration-system)
> DeepWiki OpenRL-Lab/openrl | Last indexed: 28 April 2025 (4c92aa

# Configuration System

  Relevant source files 
 - [docs/images/gridworld.jpg](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/docs/images/gridworld.jpg)
 - [docs/images/pong.png](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/docs/images/pong.png)
 - [examples/atari/README.md](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/README.md?plain=1)
 - [examples/atari/atari_ppo.yaml](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/atari_ppo.yaml)
 - [examples/atari/train_ppo.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/train_ppo.py)
 - [examples/nlp/README.md](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/README.md?plain=1)
 - [examples/nlp/ds_config.json](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/ds_config.json)
 - [examples/nlp/eval_ds_config.json](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/eval_ds_config.json)
 - [examples/nlp/nlp_ppo.yaml](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/nlp_ppo.yaml)
 - [examples/nlp/nlp_ppo_ds.yaml](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/nlp_ppo_ds.yaml)
 - [examples/nlp/train_ppo.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/train_ppo.py)
 - [openrl/configs/config.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py)
 - [openrl/envs/wrappers/monitor.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/wrappers/monitor.py)
 
  
## Purpose and Scope

 The OpenRL Configuration System provides a centralized mechanism for configuring all aspects of the reinforcement learning training pipeline. It allows users to customize environment settings, neural network architectures, algorithm hyperparameters, logging behavior, and more. This system enables reproducible experiments and flexible configuration through both command-line arguments and structured YAML files.

 
## Configuration System Architecture

 The configuration system is built on top of Python's `ArgumentParser` with extensions for YAML file support. It follows a hierarchical approach where command-line arguments can override values specified in YAML files, which in turn override default values.

 
### Configuration Flow

 
```

```

 Sources:

 
 - [openrl/configs/config.py24-1263](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L24-L1263)
 - [examples/nlp/train_ppo.py13-20](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/train_ppo.py#L13-L20)
 - [examples/atari/train_ppo.py45-46](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/train_ppo.py#L45-L46)
 
 
## Configuration Parser

 The core component of the configuration system is the `create_config_parser()` function in `openrl/configs/config.py`, which creates a comprehensive `ArgumentParser` with all available configuration options.

 
```

```

 Sources:

 
 - [openrl/configs/config.py24-33](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L24-L33)
 - [openrl/configs/config.py31-32](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L31-L32) - YAML config support
 
 The configuration options are organized into logical categories:

 
| Category | Examples | Description |
|---|---|---|
| Basic Settings | seed, experiment_name | Core experiment control parameters |
| Environment Settings | env_name, num_agents | Environment configuration |
| Network Architecture | hidden_size, layer_N, activation_id | Neural network structure |
| Algorithm Settings | lr, gamma, clip_param | Algorithm hyperparameters |
| Evaluation Settings | use_eval, eval_interval | Evaluation behavior |
| Advanced Settings | self_play, distributed_type | Special features |

 Sources:

 
 - [openrl/configs/config.py32-425](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L32-L425) - Basic and environment settings
 - [openrl/configs/config.py460-637](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L460-L637) - Network architecture settings
 - [openrl/configs/config.py638-782](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L638-L782) - Algorithm settings
 - [openrl/configs/config.py822-862](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L822-L862) - Evaluation settings
 
 
## YAML Configuration Files

 OpenRL supports configuration through YAML files, which provide a structured and readable format for defining complex configurations.

 
### Example: Atari PPO Configuration

 
```

```

 Sources:

 
 - [examples/atari/atari_ppo.yaml1-17](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/atari_ppo.yaml#L1-L17)
 
 
### Example: NLP Task Configuration

 
```

```

 Sources:

 
 - [examples/nlp/nlp_ppo.yaml1-28](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/nlp_ppo.yaml#L1-L28)
 
 
## Using Configurations in Code

 The configuration is used throughout OpenRL to initialize components and control training:

 
```

```

 Sources:

 
 - [examples/nlp/train_ppo.py13-38](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/train_ppo.py#L13-L38)
 - [examples/atari/train_ppo.py45-64](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/train_ppo.py#L45-L64)
 
 Example code showing configuration usage:

 
```

```

 Sources:

 
 - [examples/atari/train_ppo.py45-64](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/train_ppo.py#L45-L64)
 
 
## Key Configuration Categories

 
### Basic Configuration

 Core parameters for experiment control:

 
```

```

 Sources:

 
 - [openrl/configs/config.py32-344](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L32-L344)
 
 
### Environment Configuration

 Parameters for customizing environments:

 
```

```

 Sources:

 
 - [openrl/configs/config.py423-442](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L423-L442)
 - [examples/nlp/nlp_ppo.yaml15-20](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/nlp_ppo.yaml#L15-L20) - Environment arguments example
 
 
### Network Architecture Configuration

 Parameters controlling neural network design:

 
```

```

 Sources:

 
 - [openrl/configs/config.py460-637](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L460-L637)
 - [examples/atari/atari_ppo.yaml11-13](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/atari_ppo.yaml#L11-L13) - Network configuration example
 
 
### Algorithm Configuration

 Algorithm-specific parameters:

 
```

```

 Sources:

 
 - [openrl/configs/config.py638-782](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L638-L782)
 - [examples/atari/atari_ppo.yaml2-15](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/atari_ppo.yaml#L2-L15) - Algorithm parameters
 
 
### Evaluation and Logging

 Parameters for evaluation and logging:

 
```

```

 Sources:

 
 - [openrl/configs/config.py822-862](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L822-L862)
 - [examples/atari/atari_ppo.yaml17-25](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/atari_ppo.yaml#L17-L25) - Logging configuration
 
 
## Advanced Configuration Features

 
### Deep Learning Framework Integration

 OpenRL supports integration with advanced deep learning frameworks like DeepSpeed:

 
```

```

 YAML configuration for DeepSpeed:

 
```

```

 Sources:

 
 - [examples/nlp/train_ppo.py13-20](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/train_ppo.py#L13-L20) - DeepSpeed configuration parsing
 - [examples/nlp/nlp_ppo_ds.yaml15-18](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/nlp_ppo_ds.yaml#L15-L18) - DeepSpeed YAML configuration
 - [examples/nlp/ds_config.json1-9](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/ds_config.json#L1-L9) - DeepSpeed configuration file
 
 
### Self-Play Configuration

 Configuration options for self-play training:

 
```

```

 Sources:

 
 - [openrl/configs/config.py163-204](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L163-L204) - Self-play configuration
 
 
### Distributed Training Configuration

 Parameters for distributed training:

 
```

```

 Sources:

 
 - [openrl/configs/config.py239-307](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/config.py#L239-L307) - Distributed training configuration
 
 
## Command Line Usage

 
### Basic Command Line Usage

 Running with default configuration:

 
```

```

 Specifying parameters directly via command line:

 
```

```

 Using a configuration file:

 
```

```

 Overriding configuration file values:

 
```

```

 Sources:

 
 - [examples/atari/README.md22-26](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/atari/README.md?plain=1#L22-L26)
 - [examples/nlp/README.md3-7](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/README.md?plain=1#L3-L7)
 
 
### DeepSpeed Usage

 For NLP tasks with DeepSpeed:

 
```

```

 Sources:

 
 - [examples/nlp/README.md9-13](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/nlp/README.md?plain=1#L9-L13)
 
 
## Best Practices

 
 - **Create Environment-Specific Configurations**: Create separate YAML files for different environments or tasks
 - **Parameter Hierarchies**: Use a base YAML for common parameters and override specific values with command-line arguments
 - **Documentation**: Add comments to YAML files to document important parameter choices
 - **Version Control**: Store configuration files in version control alongside code
 - **Experiment Tracking**: Use the `experiment_name` parameter to distinguish different runs and `wandb_entity` for tracking experiments
 - **Debug Configuration**: To debug configuration issues, print out the parsed configuration object
