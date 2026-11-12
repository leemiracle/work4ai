> 来源: [https://deepwiki.com/AgileRL/AgileRL/7-environment-integration](https://deepwiki.com/AgileRL/AgileRL/7-environment-integration)
> DeepWiki AgileRL/AgileRL | Last indexed: 25 June 2025 (03307c

# Environment Integration

  Relevant source files 
 - [agilerl/wrappers/pettingzoo_wrappers.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/wrappers/pettingzoo_wrappers.py)
 
  This page covers how AgileRL interfaces with various reinforcement learning environments, detailing supported environment interfaces, wrappers, and compatibility with different algorithms. For information about training with these environments, see [Training Framework](https://deepwiki.com/AgileRL/AgileRL/3-training-framework).

 
## Overview

 AgileRL integrates with standard reinforcement learning environments through well-defined interfaces. The library supports:

 
 - Single-agent environments using the Gymnasium interface
 - Multi-agent environments using the PettingZoo interface
 - Custom environments that implement compatible interfaces
 
 Proper environment integration ensures that observations, actions, rewards, and state transitions flow correctly between environments and learning algorithms.

 
```

```

 Sources: [agilerl/wrappers/pettingzoo_wrappers.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/wrappers/pettingzoo_wrappers.py)

 
## Environment Interfaces

 
### Gymnasium Interface (Single-Agent)

 For single-agent environments, AgileRL expects the standard Gymnasium interface:

 
 - `reset()`: Initializes the environment and returns initial observation and info
 - `step(action)`: Executes an action and returns next observation, reward, terminated, truncated, info
 - `observation_space`: Defines the structure and bounds of observations
 - `action_space`: Defines the structure and bounds of actions (Discrete, Box, etc.)
 
 
### PettingZoo Interface (Multi-Agent)

 For multi-agent environments, AgileRL uses the PettingZoo Parallel API:

 
 - `reset()`: Returns a dictionary mapping agent IDs to their observations
 - `step(actions)`: Takes a dictionary mapping agent IDs to actions
 - `agents`: List of active agent IDs
 - `observation_space(agent)`: Defines the observation space for a specific agent
 - `action_space(agent)`: Defines the action space for a specific agent
 
 
## Environment Wrappers

 AgileRL provides environment wrappers to enhance functionality and ensure compatibility with its training systems.

 
### PettingZooAutoResetParallelWrapper

 This wrapper extends PettingZoo's `ParallelEnv` to automatically reset the environment when all agents have terminated or truncated:

 
```

```

 Key features of the wrapper:

 
 - Initializes with an existing PettingZoo `ParallelEnv`
 - Preserves all the original environment's functionality
 - In the `step()` method, checks if all agents have terminated or truncated
 - Automatically resets the environment when needed, providing new initial observations
 
 Sources: [agilerl/wrappers/pettingzoo_wrappers.py9-62](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/wrappers/pettingzoo_wrappers.py#L9-L62)

 
## Environment Integration in Training

 The integration of environments in the AgileRL training process follows a specific interaction pattern:

 
```

```

 Sources: [agilerl/wrappers/pettingzoo_wrappers.py32-42](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/wrappers/pettingzoo_wrappers.py#L32-L42)

 
## Algorithm-Environment Compatibility

 AgileRL algorithms are designed to work with specific environment types and action spaces:

 
| Algorithm | Environment Interface | Action Space | Training Function |
|---|---|---|---|
| DQN | Gymnasium | Discrete | train_off_policy() |
| Rainbow DQN | Gymnasium | Discrete | train_off_policy() |
| DDPG | Gymnasium | Continuous | train_off_policy() |
| TD3 | Gymnasium | Continuous | train_off_policy() |
| PPO | Gymnasium | Discrete/Continuous | train_on_policy() |
| CQL | Gymnasium | Discrete/Continuous | train_offline() |
| ILQL | Gymnasium | Discrete | train_offline() |
| MADDPG | PettingZoo | Continuous | train_multi_agent() |
| MATD3 | PettingZoo | Continuous | train_multi_agent() |
| IPPO | PettingZoo | Discrete/Continuous | train_multi_agent() |

 Sources: [agilerl/wrappers/pettingzoo_wrappers.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/wrappers/pettingzoo_wrappers.py)

 
## Custom Environment Integration

 To integrate custom environments with AgileRL:

 
 - **For single-agent environments**:

 
 - Implement the Gymnasium interface
 - Define appropriate observation and action spaces
 - Ensure compatible reward structure
 - **For multi-agent environments**:

 
 - Implement the PettingZoo Parallel API
 - Define agent-specific observation and action spaces
 - Consider using the `PettingZooAutoResetParallelWrapper` for automatic resets
 
 
```

```

 Sources: [agilerl/wrappers/pettingzoo_wrappers.py9-62](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/wrappers/pettingzoo_wrappers.py#L9-L62)
