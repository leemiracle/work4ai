> 来源: [https://deepwiki.com/Toni-SM/skrl/4-environments](https://deepwiki.com/Toni-SM/skrl/4-environments)
> DeepWiki Toni-SM/skrl | Last indexed: 17 August 2026 (3cdc7f

# Environments

  Relevant source files 
 - [docs/source/api/config/frameworks.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/config/frameworks.rst)
 - [docs/source/api/envs.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/envs.rst)
 - [docs/source/api/envs/multi_agents_wrapping.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/envs/multi_agents_wrapping.rst)
 - [docs/source/api/envs/wrapping.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/envs/wrapping.rst)
 - [docs/source/api/multi_agents.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/multi_agents.rst)
 - [docs/source/api/utils.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/utils.rst)
 - [docs/source/snippets/loaders.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/loaders.py)
 - [docs/source/snippets/wrapping.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/wrapping.py)
 - [skrl/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/__init__.py)
 - [skrl/envs/wrappers/jax/gym_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/gym_envs.py)
 - [skrl/envs/wrappers/jax/gymnasium_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/gymnasium_envs.py)
 - [skrl/envs/wrappers/jax/pettingzoo_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/pettingzoo_envs.py)
 - [skrl/envs/wrappers/torch/gym_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/torch/gym_envs.py)
 - [skrl/envs/wrappers/torch/gymnasium_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/torch/gymnasium_envs.py)
 - [skrl/envs/wrappers/torch/pettingzoo_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/torch/pettingzoo_envs.py)
 - [skrl/envs/wrappers/warp/gymnasium_envs.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/warp/gymnasium_envs.py)
 - [skrl/utils/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/utils/__init__.py)
 
  The environment system provides a unified interface for integrating diverse reinforcement learning simulation platforms with the skrl library. This system handles environment loading, wrapping, and standardization across PyTorch, JAX, and Warp backends, enabling seamless interoperability between incompatible RL environment APIs.

 For information about training orchestration, see [Trainers](https://deepwiki.com/Toni-SM/skrl/5-trainers). For multi-agent specific algorithms, see [Multi-Agent Systems](https://deepwiki.com/Toni-SM/skrl/7-multi-agent-systems).

 
## Environment System Architecture

 The environment system operates through two main components: **loaders** that instantiate specific environment types (like Isaac Lab or MuJoCo Playground) and **wrappers** that normalize diverse APIs (Gym, Gymnasium, PettingZoo) to a consistent interface.

 
```

```

 **Environment Integration Flow**

 Sources: [docs/source/api/envs.rst12-37](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/envs.rst#L12-L37) [docs/source/api/envs/wrapping.rst8-17](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/envs/wrapping.rst#L8-L17) [docs/source/api/envs/multi_agents_wrapping.rst8-14](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/envs/multi_agents_wrapping.rst#L8-L14)

 
## Environment Wrappers

 The wrapping mechanism normalizes environment responses (observations, rewards, terminations) into the appropriate tensor format for the selected backend (PyTorch, JAX, or Warp). This allows agents to interact with any supported environment using a single `step()` and `reset()` API.

 
### Supported Platforms and Backends

 skrl provides comprehensive support across different frameworks:

 
| Platform | PyTorch | JAX | Warp |
|---|---|---|---|
| Gym | ✅ | ✅ | ❌ |
| Gymnasium | ✅ | ✅ | ✅ |
| Isaac Lab | ✅ | ✅ | ✅ |
| ManiSkill | ✅ | ✅ | ✅ |
| PettingZoo | ✅ | ✅ | ❌ |
| Playground | ✅ | ✅ | ✅ |
| Shimmy | ✅ | ✅ | ✅ |

 
### Implementation Details

 Wrappers like `GymnasiumWrapper` [skrl/envs/wrappers/torch/gymnasium_envs.py19-127](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/torch/gymnasium_envs.py#L19-L127) and `GymWrapper` [skrl/envs/wrappers/jax/gym_envs.py32-161](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/gym_envs.py#L32-L161) handle:

 
 - **Observation/Action Space Normalization**: Converting between framework-specific spaces and Gymnasium-compatible spaces.
 - **Tensorization**: Automatically moving data to the correct device and converting to `torch.Tensor` or `jax.Array`.
 - **Vectorization**: Detecting and handling `VectorEnv` instances for parallel execution [skrl/envs/wrappers/jax/gymnasium_envs.py29-41](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/gymnasium_envs.py#L29-L41)
 
 For details, see [Environment Wrappers](https://deepwiki.com/Toni-SM/skrl/4.1-environment-wrappers).

 Sources: [docs/source/api/envs.rst20-73](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/envs.rst#L20-L73) [skrl/envs/wrappers/jax/gymnasium_envs.py20-127](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/gymnasium_envs.py#L20-L127) [skrl/envs/wrappers/torch/gymnasium_envs.py19-127](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/torch/gymnasium_envs.py#L19-L127)

 
## Isaac Lab and Playground Integration

 skrl provides specialized loaders for high-performance simulation platforms. These loaders simplify the complex setup required for NVIDIA Isaac Lab and MuJoCo Playground.

 
```

```

 **Loader-to-Simulation Mapping**

 
### Isaac Lab

 Integration with Isaac Lab supports both single-agent and multi-agent robotics tasks. Loaders like `load_isaaclab_env` [docs/source/snippets/wrapping.py4-7](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/wrapping.py#L4-L7) handle task registration and environment instantiation, which are then passed to `wrap_env` for API standardization.

 
### MuJoCo Playground

 MuJoCo Playground environments are loaded via `load_playground_env` [docs/source/snippets/wrapping.py116-119](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/wrapping.py#L116-L119) providing high-speed simulation for tasks like `CartpoleBalance`.

 For details, see [Isaac Gym Integration](https://deepwiki.com/Toni-SM/skrl/4.2-isaac-gym-integration).

 Sources: [docs/source/api/envs.rst18-34](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/envs.rst#L18-L34) [docs/source/snippets/wrapping.py1-63](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/wrapping.py#L1-L63) [docs/source/snippets/wrapping.py113-149](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/wrapping.py#L113-L149)

 
## Multi-Agent Wrapping

 Multi-agent environments, such as those from PettingZoo or Isaac Lab Multi-Agent, require a different wrapping strategy to handle multiple observation and action streams.

 The `MultiAgentEnvWrapper` base class [skrl/envs/wrappers/jax/pettingzoo_envs.py20-103](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/pettingzoo_envs.py#L20-L103) provides the necessary interface:

 
 - **Agent UIDs**: Managing dictionaries of observations and actions keyed by agent ID.
 - **Shared State**: Providing global environment state via the `state()` method [skrl/envs/wrappers/jax/pettingzoo_envs.py65-75](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/pettingzoo_envs.py#L65-L75)
 - **Parallel API**: Supporting the PettingZoo Parallel API for simultaneous agent steps.
 
 For details, see [Environment Wrappers](https://deepwiki.com/Toni-SM/skrl/4.1-environment-wrappers).

 Sources: [docs/source/api/envs/multi_agents_wrapping.rst1-179](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/envs/multi_agents_wrapping.rst#L1-L179) [skrl/envs/wrappers/jax/pettingzoo_envs.py20-103](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/envs/wrappers/jax/pettingzoo_envs.py#L20-L103)
