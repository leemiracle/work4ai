> 来源: [https://deepwiki.com/geek-ai/MAgent/10-developer-guide](https://deepwiki.com/geek-ai/MAgent/10-developer-guide)
> DeepWiki geek-ai/MAgent | Last indexed: 26 October 2025 (2144db

# Developer Guide

  Relevant source files 
 - [build.sh](https://github.com/geek-ai/MAgent/blob/2144dbd4/build.sh)
 - [examples/train_against.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py)
 - [python/magent/gridworld.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py)
 - [src/gridworld/GridWorld.cc](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc)
 
  This document provides an entry point for developers who want to understand, modify, or contribute to the MAgent codebase. It covers the overall architecture from a developer's perspective, identifies key components and their locations in the repository, and outlines common development workflows.

 For specific topics, see:

 
 - **[Codebase Structure](https://deepwiki.com/geek-ai/MAgent/10.1-codebase-structure)** - Detailed repository organization and module purposes
 - **[C++ Engine Internals](https://deepwiki.com/geek-ai/MAgent/10.2-c++-engine-internals)** - Deep dive into the C++ simulation engine
 - **[Building and Testing](https://deepwiki.com/geek-ai/MAgent/10.3-building-and-testing)** - Build system, compilation, and testing procedures
 - **[Contributing Guidelines](https://deepwiki.com/geek-ai/MAgent/10.4-contributing-guidelines)** - Code standards and contribution process
 
 For understanding how to use MAgent rather than develop it, see **[Quick Start Tutorial](https://deepwiki.com/geek-ai/MAgent/1.2-quick-start-tutorial)** and **[Training Agents](https://deepwiki.com/geek-ai/MAgent/4-training-agents)**.

 
## Overview

 MAgent is a multi-language platform with three primary layers:

 
 - **C++ Engine** (`src/` directory) - High-performance simulation engine written in C++
 - **Python API** (`python/magent/` directory) - Python bindings and high-level abstractions
 - **Examples & Models** (`examples/` and `python/magent/builtin/` directories) - Ready-to-use training scripts and RL algorithms
 
 The architecture uses **ctypes** to bridge Python and C++, avoiding the need for compilation of Python bindings. This design allows developers to:

 
 - Modify the C++ engine independently of Python code
 - Extend Python functionality without touching C++
 - Add new RL algorithms purely in Python
 - Create custom environments with minimal code changes
 
 
## Repository Structure

 
```

```

 **Sources:** Repository file structure, [build.sh1-19](https://github.com/geek-ai/MAgent/blob/2144dbd4/build.sh#L1-L19)

 
### Key Directories

 
| Directory | Purpose | Primary Language |
|---|---|---|
| src/gridworld/ | Core simulation engine | C++ |
| src/render/ | Frame generation for visualization | C++ |
| python/magent/ | Python API and utilities | Python |
| python/magent/builtin/ | Built-in RL models and environment configs | Python |
| examples/ | Training scripts and demos | Python |
| build/ | Build artifacts (generated) | - |

 
## Core Components and Code Mapping

 The following diagram maps high-level concepts to specific code entities:

 
```

```

 **Sources:** [python/magent/gridworld.py14-100](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L14-L100) [src/gridworld/GridWorld.cc17-70](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L17-L70)

 
### Critical Code Entities

 
#### Python Layer

 
| Class/Module | Location | Purpose |
|---|---|---|
| GridWorld | python/magent/gridworld.py14 | Main Python interface to simulation |
| Config | python/magent/gridworld.py678 | Environment configuration builder |
| ProcessingModel | python/magent/model.py | Multi-process training wrapper |
| c_lib | python/magent/c_lib.py | ctypes bindings to C++ library |
| EventNode | python/magent/gridworld.py571-651 | AST for reward expressions |
| AgentSymbol | python/magent/gridworld.py654-675 | Symbolic agent references |

 
#### C++ Layer

 
| Class/File | Location | Purpose |
|---|---|---|
| GridWorld | src/gridworld/GridWorld.cc17-70 | Core simulation engine |
| Map | src/gridworld/Map.cc | Spatial state management |
| Group | src/gridworld/Group.h | Agent group container |
| Agent | src/gridworld/Agent.h | Individual agent state |
| RenderGenerator | src/render/RenderGenerator.h | Frame recording |

 **Sources:** [python/magent/gridworld.py1-801](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L1-L801) [src/gridworld/GridWorld.cc1-970](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L1-L970)

 
## Development Workflow

 
```

```

 **Sources:** [build.sh1-19](https://github.com/geek-ai/MAgent/blob/2144dbd4/build.sh#L1-L19)

 
### Build Process

 The build system uses CMake and is invoked via `build.sh`:

 
 - **Clean build** (optional): `./build.sh -c` removes all build artifacts [build.sh3-6](https://github.com/geek-ai/MAgent/blob/2144dbd4/build.sh#L3-L6)
 - **Standard build**: `./build.sh` creates `build/` directory and compiles C++ code [build.sh8-18](https://github.com/geek-ai/MAgent/blob/2144dbd4/build.sh#L8-L18)
 - **Platform detection**: Automatically uses `nproc` (Linux) or `sysctl -n hw.ncpu` (macOS) for parallel compilation [build.sh12-18](https://github.com/geek-ai/MAgent/blob/2144dbd4/build.sh#L12-L18)
 
 **Output**: Shared library `build/libmagent.so` (Linux) or `build/libmagent.dylib` (macOS)

 **Sources:** [build.sh1-19](https://github.com/geek-ai/MAgent/blob/2144dbd4/build.sh#L1-L19)

 
## Key Extension Points

 
### Adding a New RL Algorithm

 
 - Create new model class in `python/magent/builtin/tf_model/` or `python/magent/builtin/mx_model/`
 - Implement required interface: `infer_action()`, `sample_step()`, `train()`
 - Wrap with `ProcessingModel` in training script
 - No C++ changes required
 
 **Example reference:** [examples/train_against.py190-209](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L190-L209) shows how different algorithms are instantiated

 
### Adding a New Environment

 
 - Create config file in `python/magent/builtin/config/`
 - Define `get_config(**kwargs)` function that returns `Config` object
 - Use `Config.register_agent_type()`, `Config.add_group()`, `Config.add_reward_rule()`
 - Load with `GridWorld("your_config_name")`
 
 **Example reference:** Built-in configs in `python/magent/builtin/config/` directory

 
### Modifying Reward Logic

 Rewards are defined through the `Config` API and serialized to C++:

 **Python Side:**

 
 - Define event expressions using `Event` and `AgentSymbol` [python/magent/gridworld.py571-651](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L571-L651)
 - Add rules with `Config.add_reward_rule()` [python/magent/gridworld.py742-766](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L742-L766)
 
 **Serialization:**

 
 - `GridWorld._serialize_event_exp()` converts Python AST to integer arrays [python/magent/gridworld.py493-566](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L493-L566)
 - Transmitted via ctypes to C++ engine
 
 **C++ Side:**

 
 - Reward rules stored in `GridWorld::reward_rules` [src/gridworld/GridWorld.cc626-631](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L626-L631)
 - Evaluated during `GridWorld::calc_reward()` [src/gridworld/GridWorld.cc681-692](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L681-L692)
 
 **Sources:** [python/magent/gridworld.py493-566](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L493-L566) [src/gridworld/GridWorld.cc681-692](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L681-L692)

 
## Critical Code Paths

 
### Environment Step Execution

 The main simulation loop involves several coordinated steps:

 
```

```

 **Sources:** [python/magent/gridworld.py221-294](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L221-L294) [src/gridworld/GridWorld.cc456-631](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L456-L631)

 
### Observation Retrieval

 Observations involve complex data marshaling between C++ and Python:

 
 - **Python call**: `env.get_observation(handle)` [python/magent/gridworld.py221-248](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L221-L248)
 - **Buffer allocation**: `_get_obs_buf()` creates/resizes NumPy arrays [python/magent/gridworld.py203-213](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L203-L213)
 - **Pointer conversion**: `as_float_c_array()` converts NumPy to C pointers [python/magent/c_lib.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/c_lib.py)
 - **C++ extraction**: `GridWorld::get_observation()` fills buffers [src/gridworld/GridWorld.cc292-401](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L292-L401) 
 - Parallel view extraction via OpenMP [src/gridworld/GridWorld.cc363-397](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L363-L397)
 - Minimap generation if enabled [src/gridworld/GridWorld.cc327-360](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L327-L360)
 - **Return**: Views and features as NumPy arrays (zero-copy)
 
 **Sources:** [python/magent/gridworld.py221-248](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L221-L248) [src/gridworld/GridWorld.cc292-401](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L292-L401)

 
### Action Distribution

 Actions flow from Python to C++ via buffering mechanism:

 
 - **Python call**: `env.set_action(handle, actions)` [python/magent/gridworld.py250-261](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L250-L261)
 - **C++ reception**: `GridWorld::set_action()` categorizes actions [src/gridworld/GridWorld.cc403-454](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L403-L454)
 - **Buffering strategy**: 
 - **Small maps**: Single buffer [src/gridworld/GridWorld.cc439-453](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L439-L453)
 - **Large maps**: Multiple spatial buffers for parallelism [src/gridworld/GridWorld.cc411-438](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L411-L438)
 - **Action types**: 
 - Move actions: `< type.turn_base` [src/gridworld/GridWorld.cc417-426](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L417-L426)
 - Turn actions: `< type.attack_base` [src/gridworld/GridWorld.cc427-435](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L427-L435)
 - Attack actions: `>= type.attack_base` [src/gridworld/GridWorld.cc436-437](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L436-L437)
 
 **Sources:** [python/magent/gridworld.py250-261](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L250-L261) [src/gridworld/GridWorld.cc403-454](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L403-L454)

 
## Configuration System

 The configuration system bridges Python convenience with C++ performance:

 
```

```

 **Sources:** [python/magent/gridworld.py493-566](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L493-L566) [src/gridworld/GridWorld.cc151-169](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L151-L169)

 
### Configuration Flow

 
 - **Python definition**: User creates `Config` object and registers types [python/magent/gridworld.py678-767](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L678-L767)
 - **GridWorld initialization**: Config passed to `GridWorld.__init__()` [python/magent/gridworld.py19-99](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L19-L99)
 - **Global settings**: Map size, modes, embedding size transmitted [python/magent/gridworld.py54-63](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L54-L63)
 - **Agent types**: Physical properties, ranges, intrinsic rewards sent [python/magent/gridworld.py66-86](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L66-L86)
 - **Event serialization**: Reward rules converted to integer arrays [python/magent/gridworld.py493-566](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L493-L566)
 - **C++ registration**: Types and groups registered in engine [src/gridworld/GridWorld.cc151-169](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L151-L169)
 
 **Sources:** [python/magent/gridworld.py19-99](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L19-L99) [src/gridworld/GridWorld.cc120-169](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L120-L169)

 
## Parallelization Architecture

 MAgent achieves scalability through multi-level parallelism:

 
### C++ OpenMP Parallelism

 The C++ engine uses OpenMP for parallel agent processing:

 
| Operation | Parallelization Point | Code Reference |
|---|---|---|
| Agent deletion | Freeing agent memory | GridWorld.cc40-43 |
| Observation extraction | View generation per agent | GridWorld.cc363-397 |
| Attack processing | Attack evaluation | GridWorld.cc475-506 |
| Starvation check | Death checks | GridWorld.cc527-541 |
| Reward accumulation | Group-level rewards | GridWorld.cc700-703 |
| Turn/Move (large maps) | Spatial partitioning | GridWorld.cc565-567 GridWorld.cc607-610 |

 **Key implementation detail**: Large maps (> 99×99) use spatial buffer partitioning [src/gridworld/GridWorld.cc75-85](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L75-L85) to enable parallel turn/move processing without conflicts.

 **Sources:** [src/gridworld/GridWorld.cc40-43](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L40-L43) [src/gridworld/GridWorld.cc363-397](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L363-L397) [src/gridworld/GridWorld.cc475-610](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L475-L610)

 
### Python Multiprocessing

 The `ProcessingModel` class enables multi-process training:

 
 - Each model runs in separate process (avoids GIL)
 - Non-blocking inference: `model.infer_action(..., block=False)` [examples/train_against.py71](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L71-L71)
 - Action fetching: `model.fetch_action()` blocks until ready [examples/train_against.py74](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L74-L74)
 - Sample collection: `model.sample_step(..., block=False)` [examples/train_against.py87](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L87-L87)
 - Asynchronous training: Model trains while environment steps
 
 **Sources:** [examples/train_against.py66-107](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L66-L107)

 
## Memory Management

 
### C++ Memory Management

 **Agent lifecycle:**

 
 - **Creation**: `new Agent()` during `add_agents()` [src/gridworld/GridWorld.cc229-284](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L229-L284)
 - **Death marking**: Agents marked dead, remain in memory during step [src/gridworld/GridWorld.cc479-506](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L479-L506)
 - **Cleanup**: `clear_dead()` deletes dead agents, resizes vectors [src/gridworld/GridWorld.cc633-665](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L633-L665)
 - **Destructor**: `~GridWorld()` frees all agents and ranges [src/gridworld/GridWorld.cc34-70](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L34-L70)
 
 **Important**: Dead agents must be cleared explicitly via `env.clear_dead()` to avoid memory leaks.

 **Sources:** [src/gridworld/GridWorld.cc34-70](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L34-L70) [src/gridworld/GridWorld.cc633-665](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L633-L665)

 
### Python-C++ Buffer Management

 **Observation buffers:**

 
 - Managed by `obs_bufs` dictionary in `GridWorld` [python/magent/gridworld.py215-219](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L215-L219)
 - Reused across steps, resized if agent count changes [python/magent/gridworld.py206-212](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L206-L212)
 - Zero-copy: NumPy arrays point directly to C++ memory during extraction
 
 **Sources:** [python/magent/gridworld.py203-248](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L203-L248)

 
## Common Development Tasks

 
### Debugging C++ Engine

 
 - **Enable trace logging**: Modify `LOG(TRACE)` statements in [src/gridworld/GridWorld.cc460-616](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L460-L616)
 - **Render debug**: Set render_dir to `"___debug___"` for console output [src/gridworld/GridWorld.cc940-941](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L940-L941)
 - **Use GDB/LLDB**: Compile with debug symbols and attach to Python process
 - **Check OMP threads**: `OMP_NUM_THREADS` controls parallelism (set in `c_lib.py`)
 
 **Sources:** [src/gridworld/GridWorld.cc460-616](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L460-L616) [src/gridworld/GridWorld.cc939-949](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L939-L949)

 
### Adding C++ Functionality

 
 - **Declare function** in appropriate header (`src/gridworld/*.h`)
 - **Implement** in corresponding `.cc` file
 - **Export** via C interface if needed (add to extern "C" section)
 - **Add ctypes binding** in `python/magent/c_lib.py`
 - **Add Python wrapper** in `python/magent/gridworld.py`
 - **Rebuild**: Run `./build.sh`
 
 
### Adding Python Functionality

 
 - **Modify/extend** classes in `python/magent/`
 - **No rebuild required** - changes take effect immediately
 - **Test** with existing examples or create new test script
 
 
## Performance Considerations

 
### Optimization Hot Spots

 Based on the codebase, these are the most performance-critical sections:

 
 - **Observation generation**: [GridWorld.cc292-401](https://github.com/geek-ai/MAgent/blob/2144dbd4/GridWorld.cc#L292-L401) - Called every step for every group
 - **Attack processing**: [GridWorld.cc470-509](https://github.com/geek-ai/MAgent/blob/2144dbd4/GridWorld.cc#L470-L509) - Scales with number of attacks
 - **Move/turn processing**: [GridWorld.cc573-613](https://github.com/geek-ai/MAgent/blob/2144dbd4/GridWorld.cc#L573-L613) - Scales with number of agents
 - **Map spatial queries**: `Map.cc` - Frequent lookups during view extraction
 
 **Optimization strategies already employed:**

 
 - OpenMP parallelization for per-agent operations
 - Spatial partitioning for large maps (NUM_SEP_BUFFER) [GridWorld.cc75-86](https://github.com/geek-ai/MAgent/blob/2144dbd4/GridWorld.cc#L75-L86)
 - Buffer reuse in Python to avoid reallocation
 - Zero-copy data transfer via NumPy C API
 
 **Sources:** [src/gridworld/GridWorld.cc75-86](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L75-L86) [src/gridworld/GridWorld.cc292-613](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/gridworld/GridWorld.cc#L292-L613)

 
### Profiling

 To profile the C++ engine:

 
 - Compile with profiling flags in `CMakeLists.txt`
 - Run training script with many agents
 - Use `gprof`, `perf`, or `Instruments` (macOS) to identify bottlenecks
 
 To profile Python code:

 
 - Use `cProfile` module on training scripts
 - Focus on model inference and data preparation
 - Check for unnecessary Python-side loops that could be vectorized
 
 
## Next Steps

 
 - **[Codebase Structure](https://deepwiki.com/geek-ai/MAgent/10.1-codebase-structure)** - Detailed file-by-file breakdown
 - **[C++ Engine Internals](https://deepwiki.com/geek-ai/MAgent/10.2-c++-engine-internals)** - Deep dive into Map, Agent, and Group classes
 - **[Building and Testing](https://deepwiki.com/geek-ai/MAgent/10.3-building-and-testing)** - CMake configuration, test procedures, CI/CD
 - **[Contributing Guidelines](https://deepwiki.com/geek-ai/MAgent/10.4-contributing-guidelines)** - Code style, PR process, testing requirements
 
 For hands-on development, start by:

 
 - Building the project: `./build.sh`
 - Running an example: `python examples/train_battle.py`
 - Modifying a simple config in `python/magent/builtin/config/`
 - Creating a custom training script based on existing examples
 
 **Sources:** [build.sh1-19](https://github.com/geek-ai/MAgent/blob/2144dbd4/build.sh#L1-L19) [examples/train_against.py1-253](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L1-L253)
