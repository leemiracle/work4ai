> 来源: [https://deepwiki.com/geek-ai/MAgent/9-api-reference](https://deepwiki.com/geek-ai/MAgent/9-api-reference)
> DeepWiki geek-ai/MAgent | Last indexed: 26 October 2025 (2144db

# API Reference

  Relevant source files 
 - [build.sh](https://github.com/geek-ai/MAgent/blob/2144dbd4/build.sh)
 - [examples/train_against.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py)
 - [python/magent/gridworld.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py)
 - [python/magent/model.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py)
 - [src/render/frontend/index.html](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/render/frontend/index.html)
 - [src/render/frontend/js/render-handle.js](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/render/frontend/js/render-handle.js)
 
  
## Purpose and Scope

 This page provides a comprehensive reference for the MAgent Python API. It serves as an entry point to detailed documentation of all major classes, functions, and interfaces used to configure environments, train agents, and visualize simulations.

 For implementation details of the C++ engine, see [C++ Engine Implementation](https://deepwiki.com/geek-ai/MAgent/3.2-c++-engine-implementation). For practical examples of using these APIs in training scripts, see [Training Workflow](https://deepwiki.com/geek-ai/MAgent/4.1-training-workflow).

 
## Overview

 The MAgent Python API is organized into four main areas:

 
| API Area | Key Classes | Sub-Page |
|---|---|---|
| Environment Management | GridWorld, Config, AgentSymbol, EventNode | GridWorld API |
| Model Training | BaseModel, ProcessingModel, NDArrayPackage | ProcessingModel API |
| Configuration | Config, AgentType, CircleRange, SectorRange | Configuration Classes |
| Visualization | PyGameRenderer, BaseServer implementations | Renderer APIs |

 The API follows a layered design where configuration classes define the environment structure, the GridWorld class manages simulation execution, and ProcessingModel classes handle multi-agent training with parallel execution support.

 Sources: [python/magent/gridworld.py1-801](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L1-L801) [python/magent/model.py1-348](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L1-L348)

 
## API Architecture

 
```

```

 Sources: [python/magent/gridworld.py14-801](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L14-L801) [python/magent/model.py14-348](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L14-L348)

 
## Core API Workflow

 This diagram shows how the main API components are used together in a typical training script:

 
```

```

 Sources: [examples/train_against.py43-132](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L43-L132) [python/magent/model.py115-286](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L115-L286) [python/magent/gridworld.py14-566](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L14-L566)

 
## API Class Hierarchy

 
```

```

 Sources: [python/magent/gridworld.py14-801](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L14-L801) [python/magent/model.py14-348](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L14-L348)

 
## Key API Patterns

 
### Non-Blocking Operations

 Many ProcessingModel methods support non-blocking execution for parallel performance:

 
```

```

 This pattern enables parallel inference across multiple models and overlaps communication with computation.

 Sources: [examples/train_against.py67-106](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L67-L106) [python/magent/model.py157-213](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L157-L213)

 
### Configuration-First Design

 Environments are configured declaratively before initialization:

 
```

```

 All configuration is serialized to the C++ engine at initialization time for optimal runtime performance.

 Sources: [python/magent/gridworld.py19-96](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L19-L96) [python/magent/gridworld.py493-566](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L493-L566)

 
### Group-Based Operations

 Operations are performed on entire groups via handles:

 
```

```

 This batch interface maximizes efficiency for large agent populations.

 Sources: [python/magent/gridworld.py221-374](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L221-L374) [examples/train_against.py53-98](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L53-L98)

 
## API Categories

 
### Environment Configuration ([GridWorld API](https://deepwiki.com/geek-ai/MAgent/9.1-gridworld-api))

 Classes for defining and initializing simulation environments:

 
 - `GridWorld` - Main environment interface
 - `Config` - Configuration builder
 - `EventNode` - Reward rule expressions
 - `AgentSymbol` - Agent references in rules
 
 Key methods: `register_agent_type()`, `add_group()`, `add_reward_rule()`, `reset()`, `add_agents()`

 
### Simulation Execution ([GridWorld API](https://deepwiki.com/geek-ai/MAgent/9.1-gridworld-api))

 Methods for running simulations and retrieving state:

 
 - `get_observation()` - Retrieve agent observations
 - `set_action()` - Set agent actions
 - `step()` - Execute one simulation step
 - `get_reward()` - Retrieve rewards
 - `clear_dead()` - Remove dead agents
 - `get_num()`, `get_agent_id()`, `get_alive()` - Query agent state
 
 
### Model Training ([ProcessingModel API](https://deepwiki.com/geek-ai/MAgent/9.2-processingmodel-api))

 Classes for multi-agent reinforcement learning:

 
 - `BaseModel` - Abstract model interface
 - `ProcessingModel` - Multi-process model wrapper
 - `NDArrayPackage` - Efficient array transfer
 
 Key methods: `infer_action()`, `sample_step()`, `train()`, `save()`, `load()`

 
### Range and Event Specification ([Configuration Classes](https://deepwiki.com/geek-ai/MAgent/9.3-configuration-classes))

 Classes for defining agent capabilities and reward triggers:

 
 - `CircleRange` - Circular view/attack range
 - `SectorRange` - Sector view/attack range
 - Event predicates: `'kill'`, `'attack'`, `'die'`, `'at'`, `'in'`, `'collide'`
 - Event operators: `&` (AND), `|` (OR), `~` (NOT)
 
 
### Visualization ([Renderer APIs](https://deepwiki.com/geek-ai/MAgent/9.4-renderer-apis))

 Components for rendering and interaction:

 
 - `PyGameRenderer` - Local visualization
 - `BaseServer` - Server interface
 - Implementations: `BattleServer`, `ArrangeServer`, `SampleServer`
 
 Sources: [python/magent/gridworld.py1-801](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L1-L801) [python/magent/model.py1-348](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L1-L348)

 
## Data Types and Formats

 
### Observation Format

 Observations returned by `get_observation(handle)` are tuples of NumPy arrays:

 
| Component | Type | Shape | Description |
|---|---|---|---|
| view | np.float32 | (n, h, w, c) | Spatial local observations |
| feature | np.float32 | (n, f) | Non-spatial features (HP, etc.) |

 Where:

 
 - `n` = number of agents in group
 - `h`, `w` = view height/width (from `get_view_space()`)
 - `c` = number of channels
 - `f` = feature dimension (from `get_feature_space()`)
 
 
### Action Format

 Actions passed to `set_action(handle, actions)` must be:

 
| Property | Requirement |
|---|---|
| Type | np.ndarray |
| Dtype | np.int32 |
| Shape | (n,) where n = get_num(handle) |
| Values | Integers in [0, action_space_size) |

 
### Reward Format

 Rewards returned by `get_reward(handle)` are:

 
| Property | Value |
|---|---|
| Type | np.ndarray |
| Dtype | np.float32 |
| Shape | (n,) where n = get_num(handle) |

 Sources: [python/magent/gridworld.py221-287](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L221-L287) [python/magent/model.py27-44](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L27-L44)

 
## Common Patterns Reference Table

 
| Operation | Code Pattern | Notes |
|---|---|---|
| Initialize environment | env = GridWorld(config) or env = GridWorld("battle") | String names load built-in configs |
| Get group handles | handles = env.get_handles() | Returns list of ctypes.c_int32 handles |
| Observation loop | obs = env.get_observation(handle) | Returns (view, feature) tuple |
| Action inference | model.infer_action(obs, ids, policy, eps) | Policy: 'e_greedy' or 'greedy' |
| Set actions | env.set_action(handle, actions) | Actions must be np.int32 array |
| Step simulation | done = env.step() | Returns True when episode ends |
| Sample collection | model.sample_step(rewards, alives) | Records transition in replay buffer |
| Training | loss, value = model.train(print_every) | Trains on collected samples |
| Parallel inference | model.infer_action(..., block=False) then model.fetch_action() | Non-blocking for parallelism |
| Save/load models | model.save(dir, epoch) and model.load(dir, epoch) | Checkpoint management |

 Sources: [examples/train_against.py43-249](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L43-L249) [python/magent/gridworld.py117-287](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L117-L287) [python/magent/model.py157-270](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L157-L270)

 
## Sub-Page Navigation

 The following sub-pages provide detailed API documentation:

 
 - **[GridWorld API](https://deepwiki.com/geek-ai/MAgent/9.1-gridworld-api)** - Complete reference for `GridWorld` class methods, `Config` system, and environment setup
 - **[ProcessingModel API](https://deepwiki.com/geek-ai/MAgent/9.2-processingmodel-api)** - Detailed documentation of `ProcessingModel`, `BaseModel` interface, and training methods
 - **[Configuration Classes](https://deepwiki.com/geek-ai/MAgent/9.3-configuration-classes)** - Specifications for `Config`, `AgentType`, `CircleRange`, `SectorRange`, `EventNode`, and `AgentSymbol`
 - **[Renderer APIs](https://deepwiki.com/geek-ai/MAgent/9.4-renderer-apis)** - Documentation for visualization components including `PyGameRenderer` and `BaseServer` implementations
 
 Each sub-page includes method signatures, parameter descriptions, return types, usage examples, and implementation notes.
