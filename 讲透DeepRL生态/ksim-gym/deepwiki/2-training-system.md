> 来源: [https://deepwiki.com/kscalelabs/ksim-gym/2-training-system](https://deepwiki.com/kscalelabs/ksim-gym/2-training-system)
> DeepWiki kscalelabs/ksim-gym | Last indexed: 18 May 2025 (3e92db

# Training System

  Relevant source files 
 - [README.md](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1)
 - [requirements.txt](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/requirements.txt)
 - [train.py](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py)
 
  The Training System is the core component of K-Sim Gym that enables learning effective policies for controlling humanoid robots. This page provides a technical overview of the training architecture, implementation details, and workflow. The system uses Reinforcement Learning (RL) with the Proximal Policy Optimization (PPO) algorithm to train controllers within a physics-based simulation environment.

 For details on specific reward components, see [Reward System](https://deepwiki.com/kscalelabs/ksim-gym/2.3-reward-system); for observation space information, see [Observation System](https://deepwiki.com/kscalelabs/ksim-gym/2.4-observation-system); and for deployment of trained models, see [Model Conversion and Deployment](https://deepwiki.com/kscalelabs/ksim-gym/3-model-conversion-and-deployment).

 
## System Architecture

 The training system follows a standard actor-critic reinforcement learning architecture with several components that work together to enable efficient training:

 
```

```

 Sources: [train.py358-679](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L358-L679) [README.md1-125](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L1-L125)

 
## Task and Configuration

 The training system is centered around the `HumanoidWalkingTask` class that inherits from `ksim.PPOTask`. It manages the entire training process and is configured through `HumanoidWalkingTaskConfig`.

 
```

```

 Sources: [train.py47-90](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L47-L90) [train.py359-655](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L359-L655)

 The `HumanoidWalkingTaskConfig` defines parameters for:

 
 - Model architecture (hidden size, depth, mixture components)
 - Curriculum learning (levels, thresholds)
 - Optimization (learning rate, weight decay)
 
 The `HumanoidWalkingTask` implements several key methods that define different aspects of the learning environment:

 
| Method | Purpose |
|---|---|
| get_optimizer | Creates Adam or AdamW optimizer based on configuration |
| get_mujoco_model | Loads the KBot MJCF model for simulation |
| get_actuators | Creates position-based actuators for the robot joints |
| get_physics_randomizers | Sets up physics randomizers for robust training |
| get_observations | Defines observation components visible to the agent |
| get_rewards | Defines reward components that shape learning |
| get_terminations | Defines conditions that end an episode |
| get_curriculum | Sets up the curriculum learning system |
| get_model | Creates the actor-critic model |

 Sources: [train.py360-500](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L360-L500)

 
## Actor-Critic Model Architecture

 The model architecture uses a recurrent neural network (RNN) with GRU cells for both the actor and critic networks, enabling the robot to maintain internal state.

 
```

```

 Sources: [train.py174-356](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L174-L356)

 
### Actor Network

 The actor network takes a subset of the observations and outputs a probabilistic action distribution:

 
 - **Input Projection**: Maps observations to a hidden dimension of size `hidden_size`
 - **GRU Layers**: Processes the input through `depth` GRU cells to maintain temporal information
 - **Output Projection**: Projects to parameters for a mixture of Gaussians (3 * num_outputs * num_mixtures values)
 - **Distribution**: Constructs a mixture of Gaussians distribution for stochastic action sampling
 
 The output distribution is a mixture of Gaussians with:

 
 - Means for each action dimension and mixture component
 - Standard deviations that are passed through softplus and clipped
 - Mixture weights as logits
 
 Sources: [train.py174-258](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L174-L258)

 
### Critic Network

 The critic network has a similar structure but processes more observation features:

 
 - **Input Projection**: Maps expanded observations to hidden dimension
 - **GRU Layers**: Processes through `depth` GRU cells
 - **Output Projection**: Projects to a single value representing the state value estimate
 
 Sources: [train.py261-318](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L261-L318)

 
### Integration into Model

 Both actor and critic are integrated into a single `Model` class for joint training. The actor has access to essential observations needed for control, while the critic receives a richer set of observations to better estimate state value.

 Sources: [train.py321-356](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L321-L356)

 
## Training Workflow

 The training process follows the PPO algorithm with modifications for robustness and curriculum learning:

 
```

```

 Sources: [train.py573-655](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L573-L655) [train.py358-487](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L358-L487)

 Key aspects of the training process:

 
 - **Parallel Environment Simulation**: Runs multiple environments in parallel (default 2048) for efficient data collection
 - **PPO Algorithm**: Uses clipped surrogate objective with value function loss and entropy bonus
 - **Recurrent State Management**: Manages and resets RNN states during trajectory collection
 - **Curriculum Learning**: Adjusts task difficulty based on agent performance
 
 Sources: [train.py657-679](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L657-L679)

 
## Curriculum Learning

 The curriculum learning system gradually increases task difficulty as the agent improves:

 
 - Uses `DistanceFromOriginCurriculum` to track agent progress
 - Increases difficulty when agent exceeds `increase_threshold` performance
 - Decreases difficulty when agent falls below `decrease_threshold` performance
 - Waits at least `min_level_steps` before changing levels
 
 This helps the agent learn progressively more complex behaviors rather than trying to solve the full problem immediately.

 Sources: [train.py483-486](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L483-L486) [train.py73-89](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L73-L89)

 
## Physics Simulation and Randomization

 The training system leverages physics randomization to ensure policy robustness:

 
```

```

 Sources: [train.py390-411](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L390-L411)

 The randomizers include:

 
 - Static friction randomization
 - Armature randomization
 - Mass randomization (±5%)
 - Joint damping randomization
 - Joint zero position randomization (±2 degrees)
 
 Additionally, push events are included to train the robot to recover from external forces.

 Sources: [train.py390-411](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L390-L411)

 
## Command-Line Interface

 The training system is accessed primarily through a command-line interface:

 
| Command | Purpose |
|---|---|
| python -m train | Start training with default parameters |
| python -m train max_steps=100 | Train for exactly 100 steps |
| python -m train run_mode=view load_from_ckpt_path=path/to/ckpt.bin | View a trained checkpoint in an interactive viewer |

 Sources: [README.md53-69](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L53-L69)

 
## Integration with Other Components

 The training system integrates with other components in the K-Sim Gym ecosystem:

 
```

```

 Sources: [README.md60-81](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L60-L81)

 
## Practical Usage

 The training system is designed to be accessible while still providing advanced customization options:

 
 - **Quick Start**: Run `python -m train` to start training with default parameters
 - **Monitoring**: Use TensorBoard to monitor training progress with `tensorboard --logdir humanoid_walking_task`
 - **Checkpointing**: Policies are automatically saved every 60 seconds (configurable)
 - **Visualization**: Visualize trained policies with the interactive viewer
 - **Conversion**: Convert trained checkpoints to deployable models with `python -m convert`
 
 Sources: [README.md48-79](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L48-L79)
