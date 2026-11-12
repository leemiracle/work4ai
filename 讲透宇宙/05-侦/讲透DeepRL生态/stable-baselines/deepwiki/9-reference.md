> 来源: [https://deepwiki.com/hill-a/stable-baselines/9-reference](https://deepwiki.com/hill-a/stable-baselines/9-reference)
> DeepWiki hill-a/stable-baselines | Last indexed: 22 June 2025 (45beb2

# Reference

  Relevant source files 
 - [.readthedocs.yml](https://github.com/hill-a/stable-baselines/blob/45beb246/.readthedocs.yml)
 - [docs/common/monitor.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/common/monitor.rst)
 - [docs/guide/custom_policy.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/custom_policy.rst)
 - [docs/misc/projects.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/misc/projects.rst)
 - [docs/modules/ddpg.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/ddpg.rst)
 - [docs/modules/dqn.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/dqn.rst)
 - [docs/modules/sac.rst](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/sac.rst)
 - [docs/requirements.txt](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/requirements.txt)
 - [tests/test_custom_policy.py](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_custom_policy.py)
 
  This page provides a comprehensive reference to stable-baselines components, community projects, and documentation resources. It serves as the central hub for accessing API documentation, finding code examples, and discovering real-world applications of the library.

 For detailed API documentation of individual classes and methods, see [API Documentation](https://deepwiki.com/hill-a/stable-baselines/9.1-api-documentation). For hands-on examples and community projects, see [Examples and Projects](https://deepwiki.com/hill-a/stable-baselines/9.2-examples-and-projects).

 
## Core Algorithm Classes

 The stable-baselines library organizes reinforcement learning algorithms into distinct classes based on their learning approach and implementation requirements.

 
```

```

 **Sources**: [docs/modules/dqn.rst1-226](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/dqn.rst#L1-L226) [docs/modules/ddpg.rst1-228](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/ddpg.rst#L1-L228) [docs/modules/sac.rst1-209](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/sac.rst#L1-L209) [tests/test_custom_policy.py54-64](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_custom_policy.py#L54-L64)

 
## Policy Architecture Reference

 Policy networks define the neural network architectures that map observations to actions. Each algorithm type requires specific policy interfaces.

 
```

```

 **Sources**: [docs/guide/custom_policy.rst1-247](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/custom_policy.rst#L1-L247) [tests/test_custom_policy.py17-51](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_custom_policy.py#L17-L51) [docs/modules/dqn.rst119-142](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/dqn.rst#L119-L142) [docs/modules/ddpg.rst97-120](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/ddpg.rst#L97-L120) [docs/modules/sac.rst103-126](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/sac.rst#L103-L126)

 
## Algorithm Support Matrix

 
| Algorithm | Class | Recurrent | Multi-process | Discrete Actions | Continuous Actions |
|---|---|---|---|---|---|
| PPO2 | stable_baselines.PPO2 | ✔️ | ✔️ | ✔️ | ✔️ |
| A2C | stable_baselines.A2C | ✔️ | ✔️ | ✔️ | ✔️ |
| DQN | stable_baselines.DQN | ❌ | ❌ | ✔️ | ❌ |
| DDPG | stable_baselines.DDPG | ❌ | ✔️ (MPI) | ❌ | ✔️ |
| SAC | stable_baselines.SAC | ❌ | ❌ | ❌ | ✔️ |
| TRPO | stable_baselines.TRPO | ❌ | ✔️ (MPI) | ✔️ | ✔️ |

 **Sources**: [docs/modules/dqn.rst42-57](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/dqn.rst#L42-L57) [docs/modules/ddpg.rst39-54](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/ddpg.rst#L39-L54) [docs/modules/sac.rst51-66](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/sac.rst#L51-L66)

 
## Core Utility Classes

 Essential utility classes for environment management, monitoring, and training infrastructure:

 
### Environment Management

 
 - **`DummyVecEnv`** - Single-process vectorized environment wrapper
 - **`SubprocVecEnv`** - Multi-process vectorized environment wrapper
 - **`VecNormalize`** - Observation and reward normalization wrapper
 
 
### Monitoring and Logging

 
 - **`Monitor`** - Episode statistics tracking wrapper at [stable_baselines.bench.monitor](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines.bench.monitor)
 - **`Logger`** - TensorBoard, CSV, and JSON logging system
 - **`CallbackList`** - Training callback management
 
 
### Noise Classes (for DDPG/SAC)

 
 - **`NormalActionNoise`** - Gaussian action noise
 - **`OrnsteinUhlenbeckActionNoise`** - Correlated action noise
 - **`AdaptiveParamNoiseSpec`** - Parameter space noise
 
 **Sources**: [docs/modules/ddpg.rst122-136](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/ddpg.rst#L122-L136) [docs/common/monitor.rst1-8](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/common/monitor.rst#L1-L8)

 
## Custom Policy Creation

 The library supports extensive policy customization through inheritance and configuration:

 
### Using `policy_kwargs`

 
```

```

 
### Custom Policy Classes

 
```

```

 
### Policy Registration

 
```

```

 **Sources**: [docs/guide/custom_policy.rst9-33](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/custom_policy.rst#L9-L33) [docs/guide/custom_policy.rst82-106](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/guide/custom_policy.rst#L82-L106) [tests/test_custom_policy.py67-101](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_custom_policy.py#L67-L101)

 
## Community Projects

 The stable-baselines ecosystem includes numerous real-world applications and research projects:

 
### Research Applications

 
 - **Adversarial Policies** - Multi-agent attack policies using Ray and Sacred
 - **Air Learning** - UAV research platform with DQN and PPO implementations
 - **QuaRL** - Quantization effects study framework
 - **Fenics-DRL** - Fluid mechanics control using reinforcement learning
 
 
### Robotics Projects

 
 - **S-RL Toolbox** - Robotics state representation learning (original stable-baselines project)
 - **Roboy** - Tendon-driven robot shoulder control with PPO/SAC
 - **Mobile Robot Navigation** - ROS-integrated dynamic obstacle avoidance
 
 
### Game and Simulation Projects

 
 - **Slime Volleyball** - Multi-agent self-play environment
 - **Snake Game AI** - Browser-based RL with TensorFlow.js export
 - **FZERO AI** - Self-driving car tutorial series
 
 **Sources**: [docs/misc/projects.rst1-217](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/misc/projects.rst#L1-L217)

 
## Algorithm-Specific Features

 
### DQN Extensions

 
 - **Double Q-Learning** - Enabled by default, disable with constructor parameter
 - **Dueling Networks** - Enabled by default, see Issue #406 for disabling
 - **Prioritized Experience Replay** - Available through replay buffer configuration
 
 
### DDPG Requirements

 
 - **OpenMPI** - Required for multi-processing support
 - **Action Noise** - `OrnsteinUhlenbeckActionNoise` or `NormalActionNoise`
 - **Parameter Noise** - `AdaptiveParamNoiseSpec` for exploration
 
 
### SAC Characteristics

 
 - **Entropy Regularization** - Uses entropy coefficient (inverse of reward scale)
 - **ReLU Activation** - Default policies use ReLU instead of tanh
 - **Continuous Actions Only** - Does not support discrete action spaces
 
 **Sources**: [docs/modules/dqn.rst35-40](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/dqn.rst#L35-L40) [docs/modules/ddpg.rst10-13](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/ddpg.rst#L10-L13) [docs/modules/sac.rst39-48](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/sac.rst#L39-L48)

 
## Training Callback Variables

 Each algorithm exposes different variables during training for monitoring and debugging:

 
### Common Variables (All Algorithms)

 
 - `self.timestep` - Current training timestep
 - `total_timesteps` - Total training steps
 - `episode_rewards` - List of episode rewards
 - `obs`, `new_obs` - Current and next observations
 - `action`, `reward`, `done` - Step transition data
 
 
### Algorithm-Specific Variables

 
 - **DQN**: `td_errors`, `batch_idxes`, `can_sample`
 - **DDPG**: `actor_loss`, `critic_loss`, `epoch_episodes`
 - **SAC**: `grad_step`, `n_updates`, `current_lr`
 
 **Sources**: [docs/modules/dqn.rst175-226](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/dqn.rst#L175-L226) [docs/modules/ddpg.rst165-228](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/ddpg.rst#L165-L228) [docs/modules/sac.rst160-209](https://github.com/hill-a/stable-baselines/blob/45beb246/docs/modules/sac.rst#L160-L209)

 
## Documentation Structure

 
 - **Algorithm Guides** - Detailed usage examples and parameter explanations
 - **Policy Documentation** - Custom policy creation and built-in options
 - **Environment Wrappers** - VecEnv, Monitor, and normalization utilities
 - **Community Examples** - Real-world projects and research applications
 
 For comprehensive API documentation including all class methods and parameters, see [API Documentation](https://deepwiki.com/hill-a/stable-baselines/9.1-api-documentation). For practical examples and community projects, see [Examples and Projects](https://deepwiki.com/hill-a/stable-baselines/9.2-examples-and-projects).
