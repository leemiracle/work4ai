<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/gym-xarm · page 8 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gym_xarm/tasks/base.py](gym_xarm/tasks/base.py)
- [gym_xarm/tasks/lift.py](gym_xarm/tasks/lift.py)
- [gym_xarm/tasks/mocap.py](gym_xarm/tasks/mocap.py)

</details>



This section provides detailed technical documentation of all public classes, methods, properties, and functions in the gym-xarm package. This reference is intended for developers who need precise information about method signatures, parameters, return values, and behavior.

For usage examples and tutorials, see [Quick Start Tutorial](#2.2). For understanding the overall system architecture, see [Core Architecture](#3).

---

## API Overview

The gym-xarm API is organized into three main components:

1. **Base Environment Class** - The core environment implementation providing Gymnasium interface, MuJoCo integration, and observation/action processing ([gym_xarm/tasks/base.py]())
2. **Lift Task** - The active manipulation task implementing reward logic and goal sampling ([gym_xarm/tasks/lift.py]())
3. **Mocap Module** - Utility functions for motion capture control in MuJoCo ([gym_xarm/tasks/mocap.py]())

The following diagram shows the public API surface and how components relate:

```mermaid
graph TB
    subgraph "User Code"
        UserAgent["RL Agent / User Script"]
    end
    
    subgraph "gym-xarm Public API"
        subgraph "Environment Registration"
            GymMake["gymnasium.make('gym_xarm/XarmLift-v0')"]
        end
        
        subgraph "Base Class Public API"
            BaseInit["Base.__init__(task, obs_type, render_mode, ...)"]
            Reset["Base.reset(seed, options)"]
            Step["Base.step(action)"]
            Render["Base.render()"]
            GetObs["Base.get_obs()"]
            Close["Base.close()"]
            
            BaseProps["Properties:<br/>dt, eef, eef_velp, gripper_angle,<br/>robot_state, obj, obj_rot,<br/>obj_velp, obj_velr"]
        end
        
        subgraph "Lift Task Public API"
            LiftInit["Lift.__init__(**kwargs)"]
            IsSuccess["Lift.is_success()"]
            GetReward["Lift.get_reward()"]
            LiftProps["Properties:<br/>z_target"]
        end
        
        subgraph "Mocap Module Public API"
            ApplyAction["mocap.apply_action(model, model_names, data, action)"]
            ResetMocap["mocap.reset(model, data)"]
            ResetMocap2Body["mocap.reset_mocap2body_xpos(model, model_names, data)"]
        end
    end
    
    subgraph "Gymnasium Framework"
        GymEnv["gymnasium.Env"]
        GymSpaces["gymnasium.spaces"]
    end
    
    UserAgent -->|"gym.make()"| GymMake
    GymMake -->|"instantiates"| LiftInit
    
    LiftInit -->|"inherits"| BaseInit
    BaseInit -->|"extends"| GymEnv
    
    UserAgent -->|"calls"| Reset
    UserAgent -->|"calls"| Step
    UserAgent -->|"calls"| Render
    
    Step -->|"uses internally"| GetObs
    Step -->|"calls"| IsSuccess
    Step -->|"calls"| GetReward
    Step -->|"calls"| ApplyAction
    
    Reset -->|"uses internally"| GetObs
    
    BaseInit -->|"creates"| GymSpaces
    
    style BaseInit fill:#f9f9f9
    style LiftInit fill:#f9f9f9
    style Step fill:#e0e0e0
    style Reset fill:#e0e0e0
```

**Sources:** [gym_xarm/tasks/base.py](), [gym_xarm/tasks/lift.py](), [gym_xarm/tasks/mocap.py]()

---

## Core API Components

### Base Environment Class

The `Base` class ([gym_xarm/tasks/base.py:18]()) is the foundational environment implementation. It provides:

- **Lifecycle Management**: `__init__`, `reset`, `step`, `close`
- **Observation Generation**: `get_obs` with three modes (`state`, `pixels`, `pixels_agent_pos`)
- **Action Processing**: `_apply_action` with mocap control integration
- **Rendering**: Dual renderer system (`render` for visualization, internal observation renderer)
- **Robot State Properties**: `eef`, `eef_velp`, `gripper_angle`, `robot_state`, `obj`, `obj_rot`, `obj_velp`, `obj_velr`

See [Base Class API](#8.1) for complete method signatures and detailed documentation.

### Lift Task

The `Lift` class ([gym_xarm/tasks/lift.py:6]()) extends `Base` and implements:

- **Task Configuration**: Metadata defining action space (`"xyzw"`), episode length (50), and task description
- **Success Criteria**: `is_success` checking if object height exceeds threshold
- **Reward Function**: `get_reward` combining reach and pick components
- **Observation Space**: `_get_obs` returning 28-dimensional state vector
- **Goal Sampling**: `_sample_goal` randomizing initial positions

See [Lift Task API](#8.2) for complete task-specific documentation.

### Mocap Module

The `mocap` module ([gym_xarm/tasks/mocap.py]()) provides three utility functions for motion capture control:

- `apply_action(model, model_names, data, action)` - Applies actions to mocap bodies and gripper
- `reset(model, data)` - Resets mocap weld constraints
- `reset_mocap2body_xpos(model, model_names, data)` - Synchronizes mocap positions with welded bodies

See [Mocap Module API](#8.3) for function signatures and usage.

**Sources:** [gym_xarm/tasks/base.py](), [gym_xarm/tasks/lift.py](), [gym_xarm/tasks/mocap.py]()

---

## Class Hierarchy

```mermaid
classDiagram
    class gymnasium_Env {
        <<external>>
        +reset()
        +step()
        +render()
        +close()
    }
    
    class Base {
        +__init__(task, obs_type, render_mode, ...)
        +reset(seed, options)
        +step(action)
        +render()
        +get_obs()
        +close()
        +dt : float
        +eef : ndarray
        +eef_velp : ndarray
        +gripper_angle : ndarray
        +robot_state : ndarray
        +obj : ndarray
        +obj_rot : ndarray
        +obj_velp : ndarray
        +obj_velr : ndarray
        #_initialize_simulation()
        #_initialize_observation_space()
        #_initialize_renderer(renderer_type)
        #_env_setup(initial_qpos)
        #_reset_sim()
        #_apply_action(action)
        #_limit_gripper(gripper_pos, pos_ctrl)
        #_set_gripper(gripper_pos, gripper_rotation)
        #_render(renderer)
        #_render_callback()
        #_step_callback()
        #is_success()* : bool
        #get_reward()* : float
        #_sample_goal()*
        #_get_obs()* : ndarray
    }
    
    class Lift {
        +__init__(**kwargs)
        +is_success() : bool
        +get_reward() : float
        +reset(seed, options)
        +step(action)
        +z_target : float
        #_get_obs() : ndarray
        #_sample_goal()
    }
    
    gymnasium_Env <|-- Base : inherits
    Base <|-- Lift : inherits
    
    note for Base "Abstract methods marked with *\nmust be implemented by subclasses"
```

**Sources:** [gym_xarm/tasks/base.py:18-335](), [gym_xarm/tasks/lift.py:6-102]()

---

## Action and Observation Spaces

### Action Space

The action space is defined by the task's metadata and constructed in [gym_xarm/tasks/base.py:74]():

| Property | Type | Shape | Range | Description |
|----------|------|-------|-------|-------------|
| `action_space` | `gym.spaces.Box` | `(4,)` | `[-1.0, 1.0]` | Continuous actions for x, y, z, gripper |

The action vector components (for Lift task with `action_space="xyzw"`):
- `action[0:3]` - Delta position control for end-effector (x, y, z)
- `action[3]` - Gripper control (-1 = open, 1 = close)

### Observation Spaces

Three observation types are supported, configured via the `obs_type` parameter:

| obs_type | Space Type | Shape/Contents | Description |
|----------|-----------|----------------|-------------|
| `"state"` | `Box` | `(28,)` float64 | State vector containing robot and object states |
| `"pixels"` | `Box` | `(84, 84, 3)` uint8 | RGB image from camera |
| `"pixels_agent_pos"` | `Dict` | `{"pixels": (84,84,3), "agent_pos": (4,)}` | Hybrid observation combining image and robot state |

The state vector (28 dimensions) contains:
- End-effector position (3)
- End-effector linear velocity (3)
- Object position (3)
- Object rotation quaternion (4)
- Object linear velocity (3)
- Object angular velocity (3)
- End-effector to object delta (3)
- Distance metrics (5: 3D distance, XY distance, z_target, z_target-obj_z, z_target-eef_z)
- Gripper angle (1)

**Sources:** [gym_xarm/tasks/base.py:74-131](), [gym_xarm/tasks/lift.py:50-72]()

---

## Data Flow Through API Methods

The following diagram shows how data flows through the API during a typical episode:

```mermaid
sequenceDiagram
    participant User as "User Code"
    participant Lift as "Lift Instance"
    participant Base as "Base Methods"
    participant Mocap as "mocap Module"
    participant MuJoCo as "MuJoCo Engine"
    
    User->>Lift: "__init__(**kwargs)"
    Lift->>Base: "__init__('lift', ...)"
    Base->>Base: "_initialize_simulation()"
    Base->>MuJoCo: "MjModel.from_xml_path()"
    Base->>Base: "_initialize_observation_space()"
    Base->>Base: "_initialize_renderer()"
    
    User->>Lift: "reset(seed=42)"
    Lift->>Base: "reset(seed=42)"
    Base->>Base: "_reset_sim()"
    Base->>Lift: "_sample_goal()"
    Lift-->>Base: "goal position"
    Base->>Base: "get_obs()"
    Base->>Lift: "_get_obs()"
    Lift-->>Base: "state vector (28,)"
    Base-->>User: "observation, info"
    
    loop "Episode Steps"
        User->>Lift: "step(action)"
        Lift->>Base: "step(action)"
        Base->>Base: "_apply_action(action)"
        Base->>Base: "_limit_gripper(gripper_pos, pos_ctrl)"
        Base->>Mocap: "apply_action(model, names, data, ...)"
        Mocap->>Mocap: "reset_mocap2body_xpos()"
        Mocap->>MuJoCo: "Update mocap_pos, mocap_quat, ctrl"
        Base->>MuJoCo: "mj_step(nstep=2)"
        Base->>Base: "get_obs()"
        Base->>Lift: "get_reward()"
        Lift-->>Base: "reward value"
        Base->>Lift: "is_success()"
        Lift-->>Base: "success boolean"
        Base-->>User: "obs, reward, terminated, truncated, info"
    end
    
    User->>Lift: "render()"
    Lift->>Base: "render()"
    Base->>Base: "_render(visualization_renderer)"
    Base->>MuJoCo: "renderer.render('rgb_array', camera='camera0')"
    MuJoCo-->>Base: "RGB array"
    Base-->>User: "RGB array (680, 680, 3)"
    
    User->>Lift: "close()"
    Lift->>Base: "close()"
    Base->>Base: "observation_renderer.close()"
    Base->>Base: "visualization_renderer.close()"
```

**Sources:** [gym_xarm/tasks/base.py:35-335](), [gym_xarm/tasks/lift.py:14-102](), [gym_xarm/tasks/mocap.py:6-51]()

---

## Properties Reference

The `Base` class provides several read-only properties for accessing simulation state:

| Property | Return Type | Shape | Description | Code Reference |
|----------|-------------|-------|-------------|----------------|
| `dt` | `float` | scalar | Timestep duration (n_substeps × model timestep) | [gym_xarm/tasks/base.py:153-155]() |
| `eef` | `ndarray` | (3,) | End-effector position relative to table center | [gym_xarm/tasks/base.py:158-159]() |
| `eef_velp` | `ndarray` | (3,) | End-effector linear velocity | [gym_xarm/tasks/base.py:162-163]() |
| `gripper_angle` | `ndarray` | (1,) | Right outer knuckle joint position | [gym_xarm/tasks/base.py:166-167]() |
| `robot_state` | `ndarray` | (4,) | Concatenation of eef and gripper_angle | [gym_xarm/tasks/base.py:170-171]() |
| `obj` | `ndarray` | (3,) | Object position relative to table center | [gym_xarm/tasks/base.py:174-175]() |
| `obj_rot` | `ndarray` | (4,) | Object rotation quaternion | [gym_xarm/tasks/base.py:178-179]() |
| `obj_velp` | `ndarray` | (3,) | Object linear velocity | [gym_xarm/tasks/base.py:182-183]() |
| `obj_velr` | `ndarray` | (3,) | Object angular velocity | [gym_xarm/tasks/base.py:186-187]() |

The `Lift` class adds:

| Property | Return Type | Shape | Description | Code Reference |
|----------|-------------|-------|-------------|----------------|
| `z_target` | `float` | scalar | Target height threshold (init_z + 0.15) | [gym_xarm/tasks/lift.py:19-20]() |

**Sources:** [gym_xarm/tasks/base.py:153-187](), [gym_xarm/tasks/lift.py:19-20]()

---

## Constants and Metadata

### Base Class Constants

Defined in [gym_xarm/tasks/base.py:26-33]():

```python
metadata = {
    "render_modes": ["rgb_array"] or ["rgb_array", "human"],  # Depends on MUJOCO_GL
    "render_fps": 25,
}
n_substeps = 20
initial_qpos = {}
```

### Lift Task Metadata

Defined in [gym_xarm/tasks/lift.py:7-12]():

```python
metadata = {
    **Base.metadata,
    "action_space": "xyzw",
    "episode_length": 50,
    "description": "Lift a cube above a height threshold",
}
```

### Default Configuration Values

Defined in `Base.__init__` [gym_xarm/tasks/base.py:35-83]():

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `gripper_rotation` | `[0, 1, 0, 0]` | Quaternion for gripper orientation |
| `center_of_table` | `[1.655, 0.3, 0.63625]` | Table center position |
| `max_z` | `1.2` | Maximum allowed z position |
| `min_z` | `0.2` | Minimum allowed z position |
| `observation_width` | `84` | Width of observation renderer |
| `observation_height` | `84` | Height of observation renderer |
| `visualization_width` | `680` | Width of visualization renderer |
| `visualization_height` | `680` | Height of visualization renderer |

**Sources:** [gym_xarm/tasks/base.py:26-83](), [gym_xarm/tasks/lift.py:7-12]()

---

## Method Categories

### Lifecycle Methods (Public)

| Method | Class | Description |
|--------|-------|-------------|
| `__init__(task, obs_type, render_mode, ...)` | Base | Initialize environment with configuration |
| `reset(seed, options)` | Base | Reset simulation to initial state |
| `step(action)` | Base | Execute one timestep |
| `render()` | Base | Generate visualization frame |
| `close()` | Base | Clean up resources |

### Task-Specific Methods (Abstract/Implemented)

| Method | Base | Lift | Description |
|--------|------|------|-------------|
| `is_success()` | Abstract | ✓ | Check if goal achieved |
| `get_reward()` | Abstract | ✓ | Calculate reward for current state |
| `_get_obs()` | Abstract | ✓ | Generate state observation |
| `_sample_goal()` | Abstract | ✓ | Sample new goal/initial positions |

### Internal Methods (Protected)

| Method | Purpose | Reference |
|--------|---------|-----------|
| `_initialize_simulation()` | Load MuJoCo model and create data structures | [gym_xarm/tasks/base.py:84-96]() |
| `_initialize_observation_space()` | Create Gymnasium space based on obs_type | [gym_xarm/tasks/base.py:110-131]() |
| `_initialize_renderer(renderer_type)` | Create observation or visualization renderer | [gym_xarm/tasks/base.py:133-150]() |
| `_env_setup(initial_qpos)` | Configure initial environment state | [gym_xarm/tasks/base.py:98-108]() |
| `_reset_sim()` | Reset simulation state | [gym_xarm/tasks/base.py:231-243]() |
| `_apply_action(action)` | Process and apply action to simulation | [gym_xarm/tasks/base.py:293-306]() |
| `_limit_gripper(gripper_pos, pos_ctrl)` | Enforce workspace boundaries | [gym_xarm/tasks/base.py:278-291]() |
| `_set_gripper(gripper_pos, gripper_rotation)` | Set gripper pose directly | [gym_xarm/tasks/base.py:308-313]() |
| `_render(renderer)` | Internal rendering with specified renderer | [gym_xarm/tasks/base.py:318-321]() |

**Sources:** [gym_xarm/tasks/base.py](), [gym_xarm/tasks/lift.py]()

---

## Mocap Module Functions

The mocap module ([gym_xarm/tasks/mocap.py]()) provides three functions for motion capture control:

```mermaid
graph LR
    subgraph "mocap Module Functions"
        ApplyAction["apply_action(model, model_names,<br/>data, action)"]
        Reset["reset(model, data)"]
        ResetMocap2Body["reset_mocap2body_xpos(model,<br/>model_names, data)"]
    end
    
    subgraph "Called By"
        BaseApply["Base._apply_action()"]
        BaseEnvSetup["Base._env_setup()"]
    end
    
    subgraph "Modifies"
        MocapPos["data.mocap_pos"]
        MocapQuat["data.mocap_quat"]
        Ctrl["data.ctrl"]
        EqData["model.eq_data"]
    end
    
    BaseApply -->|"calls"| ApplyAction
    BaseEnvSetup -->|"calls"| Reset
    ApplyAction -->|"calls internally"| ResetMocap2Body
    
    ApplyAction -->|"updates"| MocapPos
    ApplyAction -->|"updates"| MocapQuat
    ApplyAction -->|"updates"| Ctrl
    Reset -->|"updates"| EqData
    ResetMocap2Body -->|"syncs"| MocapPos
    ResetMocap2Body -->|"syncs"| MocapQuat
```

### Function Signatures

**`apply_action(model, model_names, data, action)`**
- Splits action into position/quaternion deltas and gripper commands
- Updates mocap positions and gripper control values
- Reference: [gym_xarm/tasks/mocap.py:6-16]()

**`reset(model, data)`**
- Resets weld constraint data to default values
- Called during environment setup
- Reference: [gym_xarm/tasks/mocap.py:19-24]()

**`reset_mocap2body_xpos(model, model_names, data)`**
- Synchronizes mocap body positions/quaternions with welded bodies
- Called before applying position deltas
- Reference: [gym_xarm/tasks/mocap.py:27-50]()

**Sources:** [gym_xarm/tasks/mocap.py:6-51](), [gym_xarm/tasks/base.py:105,301]()

---

## Navigation

For detailed documentation of specific API components:
- [Base Class API](#8.1) - Complete method signatures and parameters for the Base class
- [Lift Task API](#8.2) - Reward function, success criteria, and task-specific methods
- [Mocap Module API](#8.3) - Detailed mocap function parameters and usage

For understanding how to use this API:
- [Quick Start Tutorial](#2.2) - Basic usage examples
- [Configuration Options](#2.3) - Environment configuration parameters
- [Core Architecture](#3) - System design and component interactions

**Sources:** [gym_xarm/tasks/base.py](), [gym_xarm/tasks/lift.py](), [gym_xarm/tasks/mocap.py]()

---

