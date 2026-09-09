> 来源: [https://deepwiki.com/rail-berkeley/softlearning/5-advanced-usage](https://deepwiki.com/rail-berkeley/softlearning/5-advanced-usage)
> DeepWiki rail-berkeley/softlearning | Last indexed: 25 June 2025 (13cf18

# Advanced Usage

  Relevant source files 
 - [config/ray-autoscaler-ec2.yaml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/config/ray-autoscaler-ec2.yaml)
 - [config/ray-autoscaler-gce.yaml](https://github.com/rail-berkeley/softlearning/blob/13cf187c/config/ray-autoscaler-gce.yaml)
 - [examples/development/simulate_policy.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/examples/development/simulate_policy.py)
 - [softlearning/models/convnet.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/softlearning/models/convnet.py)
 - [softlearning/models/feedforward.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/softlearning/models/feedforward.py)
 - [softlearning/models/utils.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/softlearning/models/utils.py)
 - [softlearning/replay_pools/goal_replay_pool.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/softlearning/replay_pools/goal_replay_pool.py)
 - [softlearning/replay_pools/hindsight_experience_replay_pool.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/softlearning/replay_pools/hindsight_experience_replay_pool.py)
 - [softlearning/scripts/console_scripts.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/softlearning/scripts/console_scripts.py)
 - [softlearning/utils/tensorflow.py](https://github.com/rail-berkeley/softlearning/blob/13cf187c/softlearning/utils/tensorflow.py)
 
  This document covers advanced features and usage patterns for the softlearning framework, including policy simulation, custom model development, distributed training configuration, and specialized replay mechanisms. This material assumes familiarity with the basic experiment framework and core components covered in [Experiment Framework](https://deepwiki.com/rail-berkeley/softlearning/3-experiment-framework) and [Core Components](https://deepwiki.com/rail-berkeley/softlearning/4-core-components).

 For basic installation and running your first experiment, see [Quick Start](https://deepwiki.com/rail-berkeley/softlearning/2-quick-start). For information about Docker-based development environments and cloud deployment strategies, see [Development and Deployment](https://deepwiki.com/rail-berkeley/softlearning/6-development-and-deployment).

 
## Policy Simulation and Evaluation

 The framework provides utilities for loading trained policies from checkpoints and evaluating their performance through simulation rollouts. This is primarily handled through the `simulate_policy.py` script and supporting utilities.

 
### Loading Trained Policies

 The policy simulation system loads trained models using a checkpoint-based approach. The `load_variant_progress_metadata` function extracts experiment configuration and training progress:

 
```

```

 *Sources: examples/development/simulate_policy.py*

 The `load_policy` function reconstructs the policy architecture and loads trained weights:

 
 - Extracts `policy_params` from the saved variant configuration
 - Configures action ranges and input/output shapes based on environment
 - Uses `policies.get()` to instantiate the policy class
 - Loads weights using `policy.load_weights()` from the checkpoint directory
 
 
### Rollout Generation

 Policy evaluation uses the `rollouts` function from `softlearning.samplers.rollouts` to generate episode trajectories. The simulation supports various rendering modes:

 
 - `mode: 'human'` for visual display
 - `mode: 'rgb_array'` for programmatic video capture
 - Custom render kwargs for environment-specific rendering options
 
 *Sources: examples/development/simulate_policy.py:92-118, softlearning/samplers*

 
## Custom Model Development

 The framework provides utilities for creating custom neural network architectures through modular model construction functions.

 
### Feedforward Models

 The `feedforward_model` function creates fully-connected networks with configurable architecture:

 
```

```

 *Sources: softlearning/models/feedforward.py:14-37*

 
### Convolutional Models

 The `convnet_model` function creates CNN architectures with flexible normalization and downsampling strategies:

 Key features include:

 
 - Configurable conv filters, kernel sizes, and strides
 - Multiple normalization types: batch, layer, group, instance
 - Downsampling via convolution or pooling
 - Automatic image preprocessing and concatenation
 
 *Sources: softlearning/models/convnet.py:15-81*

 
### Input Handling Utilities

 The `create_inputs` function in `softlearning/models/utils.py` handles nested input structures:

 
 - Supports dict, list, and tuple input shapes
 - Automatic dtype inference (uint8 for images, float32 for others)
 - Tree structure preservation for complex observation spaces
 
 *Sources: softlearning/models/utils.py:50-67*

 
## Distributed Training Configuration

 The framework supports distributed training through Ray autoscaler configurations for cloud platforms.

 
### Ray Cluster Architecture

 
```

```

 *Sources: config/ray-autoscaler-gce.yaml, config/ray-autoscaler-ec2.yaml*

 
### Cloud Configuration Options

 Both GCE and EC2 configurations support:

 
| Parameter | GCE Value | EC2 Value | Purpose |
|---|---|---|---|
| machineType/InstanceType | n1-standard-4/8 | c5.2xlarge | Instance specifications |
| diskSizeGb/VolumeSize | 50 GB | Configurable | Storage allocation |
| Preemptible/Spot | preemptible: true | MarketType: spot | Cost optimization |
| Max workers | 100 | 100 | Scaling limits |

 
### File Mounting and Setup

 The cluster configurations mount essential files:

 
 - Source code: `~/softlearning`
 - MuJoCo license: `~/.mujoco/mjkey.txt`
 - Git state: `/tmp/current_git_HEAD`
 
 Setup commands automatically install the framework: `pip install -U -e ~/softlearning`

 *Sources: config/ray-autoscaler-gce.yaml:94-104, config/ray-autoscaler-ec2.yaml:87-97*

 
## Command Line Interface

 The framework provides multiple execution modes through console scripts:

 
```

```

 *Sources: softlearning/scripts/console_scripts.py*

 
## Advanced Replay Mechanisms

 
### Hindsight Experience Replay

 The `HindsightExperienceReplayPool` implements goal-conditioned learning with experience relabeling:

 Key components:

 
 - `_resample_indices`: Implements multiple resampling strategies (random, final, episode, future)
 - `_relabel_batch`: Updates batch goals based on hindsight strategy
 - `REPLACE_FULL_OBSERVATION`: Default goal replacement function
 
 Resampling strategies:

 
 - `random`: Sample from entire replay pool
 - `final`: Use episode final states as goals
 - `episode`: Sample any state from same episode
 - `future`: Sample future states from same episode
 
 *Sources: softlearning/replay_pools/hindsight_experience_replay_pool.py*

 
### Goal-Conditioned Replay

 The `GoalReplayPool` provides structured replay for environments with goal spaces:

 
 - Separates observations, goals, and actions into distinct field groups
 - Filters observation keys based on environment configuration
 - Supports nested goal structures through tree operations
 
 *Sources: softlearning/replay_pools/goal_replay_pool.py*

 
## GPU Configuration and Optimization

 
### Memory Growth Configuration

 The `set_gpu_memory_growth` function optimizes GPU memory usage:

 
```

```

 This prevents TensorFlow from allocating all GPU memory upfront, allowing multiple processes to share GPU resources effectively during distributed training.

 
### Preprocessing Utilities

 The framework provides optimized preprocessing through:

 
 - `cast_and_concat`: Efficiently concatenates nested tensor structures
 - `apply_preprocessors`: Applies preprocessing functions while preserving tree structure
 - Automatic dtype casting for mixed input types
 
 *Sources: softlearning/utils/tensorflow.py*
