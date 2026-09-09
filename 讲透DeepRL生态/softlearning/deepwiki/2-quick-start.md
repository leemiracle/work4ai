> 来源: [https://deepwiki.com/rail-berkeley/softlearning/2-quick-start](https://deepwiki.com/rail-berkeley/softlearning/2-quick-start)
> DeepWiki rail-berkeley/softlearning | Last indexed: 25 June 2025 (13cf18

# Quick Start

  Relevant source files 
 - [.env](https://github.com/rail-berkeley/softlearning/blob/13cf187c/.env)
 - [.gitignore](https://github.com/rail-berkeley/softlearning/blob/13cf187c/.gitignore)
 - [README.md](https://github.com/rail-berkeley/softlearning/blob/13cf187c/README.md?plain=1)
 - [docker/Dockerfile.softlearning](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning)
 - [docker/Dockerfile.softlearning.base.cpu](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.cpu)
 - [docker/Dockerfile.softlearning.base.gpu](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/Dockerfile.softlearning.base.gpu)
 - [docker/cloudbuild.yaml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/cloudbuild.yaml)
 - [docker/docker-compose.cloud.yml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.cloud.yml)
 - [docker/docker-compose.dev.cpu.yml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.cpu.yml)
 - [docker/docker-compose.dev.gpu.yml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.gpu.yml)
 - [docker/entrypoint.sh](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/entrypoint.sh)
 - [environment.yml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/environment.yml)
 - [examples/development/main.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/main.py)
 - [examples/development/variants.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py)
 - [examples/instrument.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/instrument.py)
 - [examples/utils.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/utils.py)
 - [requirements.txt](https://github.com/rail-berkeley/softlearning/blob/13cf187c/requirements.txt)
 - [setup.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/setup.py)
 - [softlearning/replay_pools/flexible_replay_pool_test.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/softlearning/replay_pools/flexible_replay_pool_test.py)
 
  This guide provides the essential steps to install softlearning and run your first deep reinforcement learning experiment. It covers installation, basic configuration, and executing a training run with result interpretation.

 For detailed information about the experiment framework and configuration system, see [Experiment Framework](https://deepwiki.com/rail-berkeley/softlearning/3-experiment-framework). For advanced deployment options including distributed and cloud training, see [Advanced Usage](https://deepwiki.com/rail-berkeley/softlearning/5-advanced-usage).

 
## Prerequisites and Installation

 Softlearning requires Python 3.8+ and supports both conda and Docker environments. Most environments require a MuJoCo license for physics simulation.

 
### Conda Installation

 The recommended approach uses conda for dependency management:

 
```

```

 
### MuJoCo Setup

 
 - Download and install MuJoCo 1.50 and 2.00 from the MuJoCo website
 - Extract to default locations (`~/.mujoco/mjpro150` and `~/.mujoco/mujoco200_{platform}`)
 - Create symlink: `ln -s ~/.mujoco/mujoco200_{platform} ~/.mujoco/mujoco200`
 - Copy license key to `~/.mujoco/mjkey.txt`
 
 
### Docker Alternative

 For containerized development:

 
```

```

 **Sources:** [README.md13-38](https://github.com/rail-berkeley/softlearning/blob/13cf187c/README.md?plain=1#L13-L38) [environment.yml1-13](https://github.com/rail-berkeley/softlearning/blob/13cf187c/environment.yml#L1-L13) [requirements.txt1-140](https://github.com/rail-berkeley/softlearning/blob/13cf187c/requirements.txt#L1-L140) [docker/docker-compose.dev.cpu.yml1-31](https://github.com/rail-berkeley/softlearning/blob/13cf187c/docker/docker-compose.dev.cpu.yml#L1-L31)

 
## Core Workflow Overview

 The softlearning training process follows a standard pattern from command-line invocation through experiment execution:

 
```

```

 **Sources:** [examples/instrument.py220-245](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/instrument.py#L220-L245) [examples/development/main.py25-103](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/main.py#L25-L103) [examples/development/variants.py427-578](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L427-L578)

 
## Running Your First Experiment

 
### Basic Training Command

 Execute a simple SAC experiment on the HalfCheetah environment:

 
```

```

 This command structure maps to key code entities:

 
```

```

 
### Key Command Parameters

 
| Parameter | Purpose | Default | Example Values |
|---|---|---|---|
| --algorithm | RL algorithm to use | Required | SAC, SQL |
| --universe | Environment framework | gym | gym, dm_control |
| --domain | Environment domain | Pendulum | HalfCheetah, Hopper, Walker2d |
| --task | Specific task variant | v0 | v3, run, walk |
| --exp-name | Experiment identifier | Timestamp | my-experiment-1 |
| --local-dir | Results directory | ~/ray_results | ./experiments |

 **Sources:** [examples/utils.py156-230](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/utils.py#L156-L230) [examples/development/variants.py567-578](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L567-L578) [README.md72-82](https://github.com/rail-berkeley/softlearning/blob/13cf187c/README.md?plain=1#L72-L82)

 
## Experiment Execution Flow

 The `ExperimentRunner` orchestrates the complete training process through several key phases:

 
```

```

 
### Debug Mode

 For development and debugging, use debug mode which enables eager execution and single-threaded operation:

 
```

```

 **Sources:** [examples/development/main.py25-103](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/main.py#L25-L103) [examples/instrument.py247-305](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/instrument.py#L247-L305) [examples/development/variants.py17-75](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L17-L75)

 
## Understanding Results

 
### Output Structure

 Training results are saved in a hierarchical directory structure:

 
```
~/ray_results/
└── gym/HalfCheetah/v3/
    └── {timestamp}-{exp-name}/
        └── ExperimentRunner_{trial_id}/
            ├── checkpoint_{step}/
            ├── progress.csv
            ├── params.json
            └── result.json
```

 
### Key Configuration Elements

 The experiment configuration (`variant_spec`) contains several critical sections:

 
| Configuration Section | Purpose | Key Parameters |
|---|---|---|
| environment_params | Environment setup | domain, task, universe, kwargs |
| algorithm_params | Training parameters | n_epochs, batch_size, learning_rates |
| policy_params | Policy network config | hidden_layer_sizes, squash, observation_keys |
| sampler_params | Data collection | max_path_length, class_name |
| replay_pool_params | Experience replay | max_size, class_name |

 
### Checkpoint Structure

 Each checkpoint contains multiple components that can be loaded independently:

 
```

```

 **Sources:** [examples/development/main.py105-258](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/main.py#L105-L258) [examples/development/variants.py433-511](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L433-L511) [README.md84-95](https://github.com/rail-berkeley/softlearning/blob/13cf187c/README.md?plain=1#L84-L95)

 
## Policy Simulation

 After training, evaluate the learned policy:

 
```

```

 Where `${CHECKPOINT_PATH}` points to a specific checkpoint directory like: `~/ray_results/gym/HalfCheetah/v3/2023-12-01T10-30-00-my-first-experiment/ExperimentRunner_abc123/checkpoint_1000/`

 **Sources:** [README.md83-92](https://github.com/rail-berkeley/softlearning/blob/13cf187c/README.md?plain=1#L83-L92)

 
## Next Steps

 
 - **Configuration Customization**: Learn about the variant specification system in [Configuration System](https://deepwiki.com/rail-berkeley/softlearning/3.1-configuration-system)
 - **Algorithm Details**: Explore SAC and SQL implementations in [Algorithms](https://deepwiki.com/rail-berkeley/softlearning/4.1-algorithms)
 - **Environment Setup**: Add custom environments using [Custom Environments](https://deepwiki.com/rail-berkeley/softlearning/5.1-custom-environments)
 - **Distributed Training**: Scale experiments with [Distributed Training with Ray](https://deepwiki.com/rail-berkeley/softlearning/5.3-distributed-training-with-ray)
 - **Cloud Deployment**: Deploy to cloud platforms via [Cloud Deployment](https://deepwiki.com/rail-berkeley/softlearning/6.2-cloud-deployment)
 
 **Sources:** [examples/development/main.py1-274](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/main.py#L1-L274) [examples/development/variants.py1-578](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/variants.py#L1-L578) [examples/instrument.py1-429](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/instrument.py#L1-L429)
