> 来源: [https://deepwiki.com/kscalelabs/ksim/2-core-rl-framework](https://deepwiki.com/kscalelabs/ksim/2-core-rl-framework)
> DeepWiki kscalelabs/ksim | Last indexed: 18 May 2025 (9d2640

# Core RL Framework

  Relevant source files 
 - [ksim/__init__.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/__init__.py)
 - [ksim/commands.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/commands.py)
 - [ksim/debugging.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/debugging.py)
 - [ksim/distributions.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/distributions.py)
 - [ksim/observation.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/observation.py)
 - [ksim/requirements.txt](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/requirements.txt)
 - [ksim/rewards.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/rewards.py)
 - [ksim/task/amp.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/amp.py)
 - [ksim/task/ppo.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/ppo.py)
 - [ksim/task/rl.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py)
 - [ksim/terminations.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/terminations.py)
 - [ksim/viewer.py](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/viewer.py)
 - [tests/test_distributions.py](https://github.com/kscalelabs/ksim/blob/9d26400d/tests/test_distributions.py)
 
  The Core RL Framework in KSIM provides the foundation for implementing reinforcement learning algorithms for robotic control. It defines standardized interfaces for tasks, observations, rewards, and other components needed for effective RL training. This page outlines the core architecture, components, and training loop of the framework. For specific implementations like PPO and AMP, see [RLTask and PPOTask](https://deepwiki.com/kscalelabs/ksim/2.1-rltask-and-ppotask) and [AMPTask](https://deepwiki.com/kscalelabs/ksim/2.2-amptask-(adversarial-motion-priors)).

 
## System Architecture

 The Core RL Framework follows a modular design where various components can be composed and extended to create custom reinforcement learning tasks.

 
```

```

 Sources: [ksim/task/rl.py625-644](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L625-L644) [ksim/task/rl.py88-127](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L88-L127) [ksim/observation.py76-122](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/observation.py#L76-L122) [ksim/commands.py28-91](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/commands.py#L28-L91) [ksim/rewards.py101-130](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/rewards.py#L101-L130) [ksim/terminations.py33-59](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/terminations.py#L33-L59)

 
## Reinforcement Learning Loop

 The core of the framework is the RL training loop, which manages the interaction between the agent and environment, collecting experiences and updating the policy.

 
```

```

 Sources: [ksim/task/rl.py859-994](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L859-L994) [ksim/task/rl.py129-159](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L129-L159) [ksim/task/rl.py162-188](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L162-L188) [ksim/task/rl.py237-285](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L237-L285)

 
## Core Components

 
### RLTask Class

 The `RLTask` class is the foundation of the framework, providing the interface that all reinforcement learning tasks must implement. It defines abstract methods for obtaining the necessary components and implements the core training loop.

 Key responsibilities:

 
 - Define the interface for RL tasks
 - Manage the rollout loop for gathering experiences
 - Coordinate the interaction between the agent and environment
 - Handle training, evaluation, and visualization
 
 Sources: [ksim/task/rl.py625-1031](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L625-L1031)

 
### RLConfig

 The `RLConfig` class contains the configuration parameters for the reinforcement learning task, including:

 
| Category | Parameters | Description |
|---|---|---|
| Run Mode | run_mode | Mode to run the task (train, view) |
| Training | num_envs | Number of parallel environments |
|  | batch_size | Number of model update batches per trajectory batch |
|  | rollout_length_seconds | Duration of each rollout |
| Physics | ctrl_dt | Control loop time step |
|  | dt | Physics time step |
|  | iterations | Number of solver iterations |
| Rendering | render_height, render_width | Dimensions for rendering |
|  | render_fps | Target FPS for rendering |

 Sources: [ksim/task/rl.py326-546](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L326-L546)

 
### Rollout State Management

 The framework manages three types of state during rollouts:

 
 - `RolloutEnvState`: Per-environment variables that change with each step

 
 - Commands, physics state, model carry, reward/observation carries, curriculum state
 - `RolloutSharedState`: Variables shared across environments

 
 - Physics model, model arrays, auxiliary values
 - `RolloutConstants`: Constants that don't change during rollout

 
 - Model statics, physics engine, component collections
 
 Sources: [ksim/task/rl.py88-127](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L88-L127)

 
### Observation System

 The observation system defines how agents perceive the environment. The framework uses the `Observation` abstract class as the base for all observation types.

 Key observation types:

 
 - Base position/orientation
 - Joint positions/velocities
 - Sensor readings
 - Contact information
 
 Sources: [ksim/observation.py76-506](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/observation.py#L76-L506)

 
### Command System

 The command system provides a way to control agents by generating commands that guide behavior. The `Command` abstract class is the foundation for all command types.

 Common command types:

 
 - Position targets
 - Joystick commands
 - Initial position/orientation
 
 Sources: [ksim/commands.py28-500](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/commands.py#L28-L500)

 
### Reward System

 The reward system calculates the learning signal for reinforcement learning. The `Reward` abstract class serves as the base for all reward functions.

 Common reward types:

 
 - Staying alive rewards
 - Linear/angular velocity rewards
 - Position tracking rewards
 - Penalty rewards for undesired behaviors
 
 Sources: [ksim/rewards.py101-716](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/rewards.py#L101-L716)

 
### Termination System

 The termination system determines when episodes should end. The `Termination` abstract class is the foundation for termination conditions.

 Common termination conditions:

 
 - Not upright termination
 - Minimum height termination
 - Illegal contact termination
 - Episode length termination
 
 Sources: [ksim/terminations.py33-192](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/terminations.py#L33-L192)

 
## RL Task Implementation Flow

 
```

```

 Sources: [ksim/task/rl.py1005-1031](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L1005-L1031) [ksim/task/rl.py859-994](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L859-L994)

 
## Extension Pattern

 The Core RL Framework follows a clear extension pattern:

 
```

```

 Sources: [ksim/task/rl.py625-644](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L625-L644) [ksim/task/ppo.py301-407](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/ppo.py#L301-L407) [ksim/task/amp.py86-103](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/amp.py#L86-L103)

 
## Distributed Training Architecture

 The framework is designed to support training across multiple parallel environments, allowing for efficient experience collection.

 
```

```

 Sources: [ksim/task/rl.py607-623](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L607-L623) [ksim/task/ppo.py534-581](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/ppo.py#L534-L581)

 
## Key Methods and Functions

 The core framework includes several key functions that implement the RL workflow:

 
| Function | Purpose | Source |
|---|---|---|
| step_engine | Performs a single step of the physics engine | ksim/task/rl.py859-994 |
| get_observation | Gets observations from the physics state | ksim/task/rl.py129-159 |
| get_rewards | Calculates rewards from the trajectory | ksim/task/rl.py162-206 |
| get_terminations | Checks termination conditions | ksim/task/rl.py237-249 |
| get_commands | Updates commands based on physics state | ksim/task/rl.py252-285 |
| sample_action | Gets actions from the policy model | Abstract, implemented by task |
| update_model | Updates the model based on collected experiences | Implemented by algorithms |

 
## Configuration and Customization

 To create custom RL tasks, users need to extend the appropriate base class (`RLTask`, `PPOTask`, or `AMPTask`) and implement the required abstract methods. The modular design allows for easy customization of rewards, observations, and other components.

 Example abstract methods that must be implemented:

 
```

```

 Sources: [ksim/task/rl.py649-842](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/task/rl.py#L649-L842)

 
## Conclusion

 The Core RL Framework in KSIM provides a comprehensive foundation for implementing reinforcement learning algorithms for robotic control tasks. By defining clear interfaces and providing extensible components, it enables users to create custom tasks while leveraging the robust infrastructure for training, evaluation, and visualization.
