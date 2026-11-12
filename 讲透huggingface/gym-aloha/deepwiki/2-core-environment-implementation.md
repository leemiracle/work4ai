<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/gym-aloha · page 2 Core Environment Implementation · fetched 2026-10-26 -->

# Core Environment Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gym_aloha/env.py](gym_aloha/env.py)

</details>



This document covers the implementation of the `AlohaEnv` class, which serves as the primary Gymnasium-compatible environment interface for ALOHA bimanual robotics simulations. The `AlohaEnv` class integrates MuJoCo physics simulation through dm-control with the standard Gymnasium API, providing a unified interface for reinforcement learning applications.

For information about environment registration and available variants, see [Environment Registration](#2.1). For details about observation and action space configurations, see [Observation and Action Spaces](#2.2). For specific task implementations, see [Tasks and Simulations](#3).

## Architecture Overview

The `AlohaEnv` class follows a layered architecture that bridges the Gymnasium RL interface with MuJoCo physics simulation through dm-control middleware.

### Core Class Structure

```mermaid
classDiagram
    class AlohaEnv {
        +task: str
        +obs_type: str
        +render_mode: str
        +observation_width: int
        +observation_height: int
        +_env: control.Environment
        +observation_space: spaces.Space
        +action_space: spaces.Box
        +__init__(task, obs_type, render_mode, ...)
        +reset(seed, options) tuple
        +step(action) tuple
        +render() ndarray
        +_make_env_task(task_name) control.Environment
        +_format_raw_obs(raw_obs) dict
        +_render(visualize) ndarray
    }
    
    class Environment {
        +physics: mujoco.Physics
        +task: Task
        +reset() TimeStep
        +step(action) TimeStep
    }
    
    class Task {
        +get_observation(physics) dict
        +get_reward(physics) float
        +initialize_episode(physics) void
    }
    
    class Physics {
        +render(height, width, camera_id) ndarray
        +from_xml_path(xml_path) Physics
    }
    
    AlohaEnv --> Environment : "_env"
    Environment --> Physics : "physics"
    Environment --> Task : "task"
    AlohaEnv --|> "gym.Env" : inherits
```

Sources: [gym_aloha/env.py:21-191]()

### System Integration Architecture

```mermaid
graph TB
    subgraph "Gymnasium Interface Layer"
        GymEnv["gym.Env Interface"]
        GymSpaces["gymnasium.spaces"]
        GymMake["gym.make()"]
    end
    
    subgraph "AlohaEnv Implementation"
        AlohaEnv["AlohaEnv Class"]
        ObsHandler["_format_raw_obs()"]
        TaskFactory["_make_env_task()"]
        RenderHandler["_render()"]
    end
    
    subgraph "dm-control Layer"
        ControlEnv["control.Environment"]
        ControlPhysics["mujoco.Physics"]
        ControlTask["Task Classes"]
    end
    
    subgraph "MuJoCo Backend"
        MujocoPhysics["MuJoCo Physics Engine"]
        XMLModels["XML Model Files"]
        STLAssets["STL Asset Files"]
    end
    
    subgraph "Task Implementations"
        TransferCube["TransferCubeTask"]
        Insertion["InsertionTask"]
        EndEffector["EndEffectorTask variants"]
    end
    
    GymMake --> AlohaEnv
    GymEnv --> AlohaEnv
    GymSpaces --> AlohaEnv
    
    AlohaEnv --> ObsHandler
    AlohaEnv --> TaskFactory
    AlohaEnv --> RenderHandler
    AlohaEnv --> ControlEnv
    
    TaskFactory --> TransferCube
    TaskFactory --> Insertion
    TaskFactory --> EndEffector
    
    ControlEnv --> ControlPhysics
    ControlEnv --> ControlTask
    ControlPhysics --> MujocoPhysics
    
    MujocoPhysics --> XMLModels
    XMLModels --> STLAssets
```

Sources: [gym_aloha/env.py:1-19](), [gym_aloha/env.py:108-136]()

## Core Components

### AlohaEnv Class Initialization

The `AlohaEnv` constructor configures the environment based on the specified task and observation type. The class accepts several key parameters that determine the simulation behavior:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task` | str | Required | Task variant ("transfer_cube", "insertion", etc.) |
| `obs_type` | str | "pixels" | Observation format ("pixels", "pixels_agent_pos", "state") |
| `render_mode` | str | "rgb_array" | Rendering output format |
| `observation_width` | int | 640 | Width for observation images |
| `observation_height` | int | 480 | Height for observation images |

The initialization process follows this sequence:

```mermaid
sequenceDiagram
    participant Client
    participant AlohaEnv
    participant TaskFactory
    participant ControlEnv
    participant Physics
    
    Client->>AlohaEnv: __init__(task, obs_type, ...)
    AlohaEnv->>TaskFactory: _make_env_task(task_name)
    TaskFactory->>Physics: mujoco.Physics.from_xml_path()
    TaskFactory->>ControlEnv: control.Environment(physics, task, ...)
    TaskFactory-->>AlohaEnv: control.Environment
    AlohaEnv->>AlohaEnv: Configure observation_space
    AlohaEnv->>AlohaEnv: Configure action_space
    AlohaEnv-->>Client: AlohaEnv instance
```

Sources: [gym_aloha/env.py:25-44](), [gym_aloha/env.py:108-136]()

### Task Integration System

The `_make_env_task` method serves as a factory for creating task-specific environments. It maps task names to their corresponding XML models and task implementations:

```mermaid
graph LR
    TaskName["task_name parameter"]
    
    subgraph "Task Routing Logic"
        TransferCheck{"task == 'transfer_cube'"}
        InsertionCheck{"task == 'insertion'"}
        EndEffectorCheck{"task.startswith('end_effector')"}
    end
    
    subgraph "XML Model Loading"
        TransferXML["bimanual_viperx_transfer_cube.xml"]
        InsertionXML["bimanual_viperx_insertion.xml"]
        EndEffectorXML["bimanual_viperx_end_effector_*.xml"]
    end
    
    subgraph "Task Class Instantiation"
        TransferTask["TransferCubeTask()"]
        InsertionTask["InsertionTask()"]
        EndEffectorTask["*EndEffectorTask()"]
    end
    
    subgraph "Environment Creation"
        ControlEnvironment["control.Environment(physics, task, time_limit, ...)"]
    end
    
    TaskName --> TransferCheck
    TaskName --> InsertionCheck
    TaskName --> EndEffectorCheck
    
    TransferCheck -->|Yes| TransferXML
    InsertionCheck -->|Yes| InsertionXML
    EndEffectorCheck -->|Yes| EndEffectorXML
    
    TransferXML --> TransferTask
    InsertionXML --> InsertionTask
    EndEffectorXML --> EndEffectorTask
    
    TransferTask --> ControlEnvironment
    InsertionTask --> ControlEnvironment
    EndEffectorTask --> ControlEnvironment
```

Sources: [gym_aloha/env.py:108-136]()

### Observation Space Configuration

The environment supports three observation types, each with different space configurations:

```mermaid
graph TD
    ObsType["obs_type parameter"]
    
    subgraph "Observation Type Routing"
        StateCheck{"obs_type == 'state'"}
        PixelsCheck{"obs_type == 'pixels'"}
        PixelsAgentCheck{"obs_type == 'pixels_agent_pos'"}
    end
    
    subgraph "Space Definitions"
        StateSpace["spaces.Box(joints dimensionality) - NOT IMPLEMENTED"]
        PixelsSpace["spaces.Dict({'top': spaces.Box(H,W,3, uint8)})"]
        PixelsAgentSpace["spaces.Dict({'pixels': Dict, 'agent_pos': Box(joints, float64)})"]
    end
    
    ObsType --> StateCheck
    ObsType --> PixelsCheck
    ObsType --> PixelsAgentCheck
    
    StateCheck -->|Yes| StateSpace
    PixelsCheck -->|Yes| PixelsSpace
    PixelsAgentCheck -->|Yes| PixelsAgentSpace
```

The action space is consistently defined as a 14-dimensional continuous space with bounds [-1, 1], corresponding to the joints defined in `ACTIONS`:

```mermaid
graph LR
    ActionSpace["spaces.Box(low=-1, high=1, shape=(len(ACTIONS),), dtype=float32)"]
    Actions["ACTIONS constant (14 dimensions)"]
    JointControl["Bimanual robot joint control"]
    
    Actions --> ActionSpace
    ActionSpace --> JointControl
```

Sources: [gym_aloha/env.py:46-86]()

### Environment Lifecycle

The environment follows the standard Gymnasium lifecycle with custom implementations for reset and step operations:

```mermaid
stateDiagram-v2
    [*] --> Initialized : __init__()
    
    Initialized --> Resetting : reset()
    Resetting --> ConfigurePose : Set BOX_POSE based on task
    ConfigurePose --> SeedEnvironment : Apply random seed
    SeedEnvironment --> ResetPhysics : _env.reset()
    ResetPhysics --> FormatObservation : _format_raw_obs()
    FormatObservation --> Ready : Return (obs, info)
    
    Ready --> Stepping : step(action)
    Stepping --> ExecuteAction : _env.step(action)
    ExecuteAction --> CheckTermination : reward == 4 means success
    CheckTermination --> FormatResponse : _format_raw_obs()
    FormatResponse --> Ready : Return (obs, reward, terminated, truncated, info)
    
    Ready --> Rendering : render()
    Rendering --> CaptureImage : _env.physics.render()
    CaptureImage --> Ready : Return image array
    
    Ready --> [*] : close()
```

Key implementation details:

- **Reset Process**: [gym_aloha/env.py:150-171]() handles seeding, pose sampling, and observation formatting
- **Step Process**: [gym_aloha/env.py:173-187]() processes actions, determines termination, and formats responses  
- **Termination Logic**: Success is determined by `reward == 4`, setting both `terminated` and `is_success` flags
- **Pose Sampling**: Task-specific pose sampling using `sample_box_pose()` or `sample_insertion_pose()` functions

Sources: [gym_aloha/env.py:150-191]()

### Rendering System

The rendering system provides RGB array output through MuJoCo's physics engine:

```mermaid
graph TB
    RenderCall["render()"]
    RenderInternal["_render(visualize=True)"]
    
    subgraph "Render Configuration"
        VisualizeMode{"visualize parameter"}
        VisualizationDims["visualization_width x visualization_height"]
        ObservationDims["observation_width x observation_height"]
    end
    
    subgraph "MuJoCo Rendering"
        PhysicsRender["_env.physics.render(height, width, camera_id='top')"]
        CameraTop["'top' camera view"]
        ImageArray["RGB image array"]
    end
    
    RenderCall --> RenderInternal
    RenderInternal --> VisualizeMode
    VisualizeMode -->|True| VisualizationDims
    VisualizeMode -->|False| ObservationDims
    VisualizationDims --> PhysicsRender
    ObservationDims --> PhysicsRender
    PhysicsRender --> CameraTop
    CameraTop --> ImageArray
```

The system currently supports only the "top" camera view, with plans for additional camera angles noted in the code comments.

Sources: [gym_aloha/env.py:88-106]()

---

