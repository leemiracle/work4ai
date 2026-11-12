> 来源: [https://deepwiki.com/geek-ai/MAgent/2-core-concepts](https://deepwiki.com/geek-ai/MAgent/2-core-concepts)
> DeepWiki geek-ai/MAgent | Last indexed: 26 October 2025 (2144db

# Core Concepts

  Relevant source files 
 - [README.md](https://github.com/geek-ai/MAgent/blob/2144dbd4/README.md?plain=1)
 - [build.sh](https://github.com/geek-ai/MAgent/blob/2144dbd4/build.sh)
 - [doc/get_started.md](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1)
 - [examples/train_against.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py)
 - [python/magent/gridworld.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py)
 
  
## Purpose and Scope

 This page introduces the fundamental concepts in MAgent: agents, groups, observations, actions, and rewards. Understanding these concepts is essential for using MAgent to create and train multi-agent reinforcement learning environments. For detailed information about specific topics, see:

 
 - GridWorld environment configuration and lifecycle: [GridWorld Environment](https://deepwiki.com/geek-ai/MAgent/2.1-gridworld-environment)
 - Defining and managing agent types: [Agent Types and Groups](https://deepwiki.com/geek-ai/MAgent/2.2-agent-types-and-groups)
 - Observation structure and channels: [Observation Spaces](https://deepwiki.com/geek-ai/MAgent/2.3-observation-spaces)
 - Action representation and movement: [Action Spaces](https://deepwiki.com/geek-ai/MAgent/2.4-action-spaces)
 - Event-based reward rules: [Reward System](https://deepwiki.com/geek-ai/MAgent/2.5-reward-system)
 
 
---

 
## Conceptual Overview

 MAgent simulates many agents interacting in a 2D gridworld environment. Each simulation consists of:

 
 - **GridWorld**: A 2D grid where agents and walls occupy cells
 - **Agent Types**: Templates that define physical and behavioral properties
 - **Groups**: Collections of agents sharing the same type and control policy
 - **Observations**: What each agent perceives about its local environment
 - **Actions**: Discrete decisions agents make (move, turn, attack)
 - **Rewards**: Feedback signals that guide agent learning
 
 
### Core Concept Relationships

 
```

```

 **Sources:** [python/magent/gridworld.py14-116](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L14-L116) [doc/get_started.md1-60](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L1-L60)

 
---

 
## GridWorld: The Simulation Environment

 The `GridWorld` class is the primary interface for creating and managing multi-agent simulations. It encapsulates the C++ simulation engine and provides a Python API.

 
### GridWorld Initialization

 
```

```

 **Initialization Process:**

 
 - **Create Configuration**: Define global settings and agent types
 - **Instantiate GridWorld**: Pass config to `GridWorld(config, **kwargs)`
 - **Engine Setup**: GridWorld serializes Python config to C++ engine
 - **Group Creation**: Groups are registered and handles returned
 
 **Key GridWorld Methods:**

 
| Method | Purpose | Returns |
|---|---|---|
| reset() | Reset environment to initial state | None |
| add_agents(handle, method, **kwargs) | Add agents to a group | None |
| get_observation(handle) | Get observations for all agents in group | (views, features) |
| set_action(handle, actions) | Set actions for all agents in group | None |
| step() | Execute one simulation step | bool (done) |
| get_reward(handle) | Get rewards for all agents in group | np.ndarray |
| get_num(handle) | Get number of alive agents in group | int |
| clear_dead() | Remove dead agents from simulation | None |

 **Sources:** [python/magent/gridworld.py14-116](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L14-L116) [python/magent/gridworld.py117-294](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L117-L294)

 
---

 
## Agent Types: Property Templates

 Agent types define the characteristics shared by all agents in a group. Each type specifies physical attributes, capabilities, and intrinsic rewards.

 
### Agent Type Registration

 
```

```

 **Agent Type Attributes:**

 
| Category | Attributes | Description |
|---|---|---|
| Physical | width, length | Agent body size in grid cells |
|  | hp | Maximum health points |
|  | speed | Movement range per step |
| Perception | view_range | CircleRange(radius) or SectorRange(radius, angle) |
| Combat | attack_range | Range of attack ability |
|  | damage | Damage inflicted per attack |
|  | step_recover | HP regeneration per step (can be negative) |
|  | kill_supply | HP gained when killing this agent type |
| Intrinsic Rewards | step_reward | Reward per step |
|  | kill_reward | Reward for killing this agent type |
|  | dead_penalty | Penalty when this agent dies |
|  | attack_penalty | Penalty for attacking (prevents blank attacks) |

 **Example Registration:**

 
```

```

 **Sources:** [python/magent/gridworld.py697-728](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L697-L728) [doc/get_started.md9-18](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L9-L18)

 
---

 
## Groups and Handles: Agent Organization

 Groups organize agents that share the same type and are controlled by the same policy. Handles provide references to groups for efficient batch operations.

 
### Group System Architecture

 
```

```

 **Group Lifecycle:**

 
 - **Configuration Phase**: `config.add_group(agent_type)` returns group index
 - **Initialization Phase**: `GridWorld.__init__()` creates handles via C++ engine
 - **Runtime Phase**: Use handles for batch operations on all agents in group
 
 **Handle-Based Operations:**

 All agent operations use handles to operate on entire groups at once:

 
```

```

 **Why Groups?**

 
 - **Efficiency**: Batch operations on many agents simultaneously
 - **Parameter Sharing**: Agents in same group share neural network weights
 - **Parallel Processing**: Different groups can be processed in parallel
 - **Policy Separation**: Each group can have different learning algorithm
 
 **Sources:** [python/magent/gridworld.py91-96](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L91-L96) [python/magent/gridworld.py730-740](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L730-L740) [doc/get_started.md62-80](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L62-L80)

 
---

 
## Observations: What Agents Perceive

 Each agent receives a two-part observation: a spatial view and a non-spatial feature vector.

 
### Observation Structure

 
```

```

 **Spatial View Dimensions:**

 For an agent with `view_range = CircleRange(5)`:

 
 - View size: `(11, 11, n_channels)` where `11 = 5 * 2 + 1`
 - Masked by circle/sector based on view range type
 - Centered on agent's position
 
 **Spatial View Channels:**

 
| Channel | Content | Values |
|---|---|---|
| Wall | Wall indicators | 0 or 1 |
| Group N | Presence of group N agents | 0 or 1 |
| HP | Health points of visible agents | 0.0 to 1.0 (normalized) |
| Minimap | Global agent density | 0.0 to 1.0 (proportional) |

 **Minimap Calculation:**

 
 - Divide full map (e.g., 100×100) into minimap grid (e.g., 10×10)
 - For each minimap cell: `value = (agents_in_cell) / (total_agents)`
 - Provides coarse global awareness (no fog of war)
 
 **Non-Spatial Features:**

 
 - **ID Embedding**: Binary representation of agent's unique ID
 - **Last Action**: Previous action taken (one-hot encoded)
 - **Last Reward**: Reward received in previous step
 - **Relative Position**: Normalized coordinates in map
 
 **Getting Observations:**

 
```

```

 **Sources:** [doc/get_started.md20-37](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L20-L37) [python/magent/gridworld.py221-248](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L221-L248) [python/magent/gridworld.py315-331](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L315-L331)

 
---

 
## Actions: What Agents Can Do

 Actions are discrete choices that agents make each step. The action space depends on agent type configuration.

 
### Action Space Composition

 
```

```

 **Action Calculation:**

 For an agent with:

 
 - `speed = 2` (move range)
 - `attack_range = CircleRange(2)`
 - `turn_mode = True`
 
 Total actions = 13 (move) + 8 (attack) + 4 (turn) + 1 (no-op) = 26 actions

 **Action Types:**

 
| Type | Description | Count |
|---|---|---|
| Move | Move to any grid cell within speed radius | Depends on speed |
| Turn | Rotate to face cardinal direction | 4 (if turn_mode=True) |
| Attack | Attack any cell within attack_range | Depends on attack_range |
| No-op | Do nothing | 1 |

 **Action Representation:**

 Actions are represented as integer indices into the action space:

 
```

```

 **View-to-Attack Mapping:**

 The `get_view2attack()` method returns a mapping between view coordinates and attack action indices:

 
```

```

 **Sources:** [doc/get_started.md38-45](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L38-L45) [python/magent/gridworld.py250-262](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L250-L262) [python/magent/gridworld.py382-399](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L382-L399)

 
---

 
## Rewards: Learning Signals

 Rewards guide agent learning through two mechanisms: constant intrinsic rewards and event-based reward rules.

 
### Reward System Components

 
```

```

 
### Constant Rewards

 Defined in agent type registration and automatically applied:

 
```

```

 
### Event-Based Reward Rules

 Event-based rules use symbolic expressions to define complex reward conditions:

 **Key Classes:**

 
| Class | Purpose | Example |
|---|---|---|
| AgentSymbol | Reference agents in rules | AgentSymbol(group, 'any') |
| Event | Define event predicates | Event(a, 'attack', b) |
| EventNode | Boolean composition | e1 & e2, e1 \| e2, ~e1 |

 **Agent Symbol Index Types:**

 
 - `'any'`: Matches any single agent from group
 - `'all'`: Matches all agents from group
 - `int`: Matches specific agent by ID
 
 **Example: Cooperative Reward**

 
```

```

 **Event Expression Serialization:**

 The Python event expressions are serialized to integer arrays and sent to the C++ engine:

 
 - **Symbol Collection**: Assign integer IDs to each `AgentSymbol`
 - **Node Collection**: Assign integer IDs to each `EventNode`
 - **Serialization**: Convert tree structure to flat integer arrays
 - **Transmission**: Send to C++ via ctypes interface
 - **Runtime Evaluation**: C++ engine evaluates expressions during simulation
 
 **Sources:** [python/magent/gridworld.py571-676](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L571-L676) [python/magent/gridworld.py678-767](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L678-L767) [python/magent/gridworld.py493-566](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L493-L566) [doc/get_started.md46-60](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L46-L60)

 
---

 
## Putting It All Together: Simulation Loop

 The following diagram shows how all core concepts interact during a typical simulation step:

 
```

```

 **Typical Simulation Loop:**

 
```

```

 **Sources:** [examples/train_against.py43-131](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L43-L131) [doc/get_started.md62-89](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L62-L89)

 
---

 
## Summary: Core Concept Dependencies

 
```

```

 **Key Takeaways:**

 
 - **Configuration First**: Define agent types, groups, and reward rules in `Config` object
 - **Handle-Based Operations**: All runtime operations use group handles for batch processing
 - **Two-Part Observations**: Spatial views + non-spatial features
 - **Discrete Actions**: Move, turn, attack within defined ranges
 - **Hybrid Rewards**: Constant intrinsic rewards + event-based rules
 - **Efficient Simulation**: C++ engine handles physics, Python controls high-level logic
 
 For implementation details on each concept, see the respective subsection pages linked at the beginning of this document.

 **Sources:** [python/magent/gridworld.py1-801](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/gridworld.py#L1-L801) [doc/get_started.md1-126](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L1-L126) [examples/train_against.py1-253](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_against.py#L1-L253)
