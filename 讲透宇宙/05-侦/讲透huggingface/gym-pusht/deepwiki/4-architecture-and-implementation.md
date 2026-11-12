<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/gym-pusht · page 4 Architecture and Implementation · fetched 2026-10-26 -->

# Architecture and Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gym_pusht/__init__.py](gym_pusht/__init__.py)
- [gym_pusht/envs/__init__.py](gym_pusht/envs/__init__.py)
- [gym_pusht/envs/pusht.py](gym_pusht/envs/pusht.py)

</details>



This page provides technical details about the codebase structure, design patterns, and implementation decisions of the gym-pusht environment. It covers the internal architecture, component relationships, and key implementation choices that enable the 2D physics-based reinforcement learning environment.

For information about using the environment APIs, see [Environment API](#2.1). For details about the physics simulation mechanics, see [Physics Simulation](#2.2).

## Core Architecture Overview

The gym-pusht codebase implements a modular architecture centered around the `PushTEnv` class, which integrates multiple subsystems for physics simulation, rendering, and reinforcement learning. The architecture follows the Gymnasium environment pattern while incorporating specialized components for 2D physics and multi-modal observations.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Gymnasium Integration Layer"
        REG["register()"] 
        ENTRY["entry_point"]
        WRAPPER["TimeLimit + Wrappers"]
    end
    
    subgraph "PushTEnv Core"
        ENV["PushTEnv"]
        INIT["__init__()"]
        STEP["step()"]
        RESET["reset()"]
        RENDER["render()"]
        GETOBS["get_obs()"]
    end
    
    subgraph "Physics Subsystem"
        SPACE["pymunk.Space"]
        AGENT["agent: pymunk.Body"]
        BLOCK["block: pymunk.Body"]
        COLLISION["collision_handler"]
        PD["PD Controller"]
    end
    
    subgraph "Rendering Subsystem"
        PYGAME["pygame.Surface"]
        DRAW["_draw()"]
        GETIMG["_get_img()"]
        DRAWOPTS["DrawOptions"]
    end
    
    subgraph "Geometry Subsystem"
        SHAPELY["shapely.geometry"]
        PYMUNKSHAPELY["pymunk_to_shapely()"]
        COVERAGE["_get_coverage()"]
        KEYPOINTS["get_keypoints()"]
    end
    
    subgraph "Observation Generation"
        STATE["state obs"]
        PIXELS["pixels obs"]
        ENVSTATE["environment_state_agent_pos"]
        PIXELSAGENT["pixels_agent_pos"]
    end
    
    REG --> ENV
    ENV --> INIT
    ENV --> STEP
    ENV --> RESET
    ENV --> RENDER
    ENV --> GETOBS
    
    STEP --> PD
    STEP --> SPACE
    STEP --> COLLISION
    
    RENDER --> DRAW
    DRAW --> PYGAME
    RENDER --> GETIMG
    
    GETOBS --> STATE
    GETOBS --> PIXELS
    GETOBS --> ENVSTATE
    GETOBS --> PIXELSAGENT
    
    COVERAGE --> SHAPELY
    COVERAGE --> PYMUNKSHAPELY
    KEYPOINTS --> SHAPELY
    
    SPACE --> AGENT
    SPACE --> BLOCK
```

**Sources:** [gym_pusht/envs/pusht.py:1-542](), [gym_pusht/__init__.py:1-9]()

## Class Structure and Implementation

### Primary Classes and Components

The implementation centers around a single main class with supporting utility functions and external library integrations:

| Component | Type | Location | Responsibility |
|-----------|------|----------|----------------|
| `PushTEnv` | Class | [gym_pusht/envs/pusht.py:40-542]() | Main environment implementation |
| `pymunk_to_shapely` | Function | [gym_pusht/envs/pusht.py:27-37]() | Geometry conversion utility |
| `DrawOptions` | Class | [gym_pusht/envs/pymunk_override.py]() | Custom rendering options |

### PushTEnv Class Architecture

```mermaid
graph TB
    subgraph "PushTEnv Class Structure"
        CLASS["PushTEnv(gym.Env)"]
        
        subgraph "Initialization Methods"
            INIT["__init__()"]
            INITOBS["_initialize_observation_space()"]
            SETUP["_setup()"]
        end
        
        subgraph "Core RL Interface"
            STEP["step(action)"]
            RESET["reset(seed, options)"]
            GETOBS["get_obs()"]
            GETINFO["_get_info()"]
        end
        
        subgraph "Rendering Pipeline"
            RENDER["render()"]
            RENDERINT["_render(visualize)"]
            DRAW["_draw()"]
            GETIMG["_get_img()"]
        end
        
        subgraph "Physics Management"
            SETSTATE["_set_state(state)"]
            GETCOVERAGE["_get_coverage()"]
            HANDLECOLLISION["_handle_collision()"]
        end
        
        subgraph "Static Utility Methods"
            ADDSEGMENT["add_segment()"]
            ADDCIRCLE["add_circle()"]
            ADDTEE["add_tee()"]
            GETKEYPOINTS["get_keypoints()"]
            GETGOALPOSE["get_goal_pose_body()"]
        end
        
        subgraph "Instance Attributes"
            OBSTYPE["obs_type"]
            RENDERMODE["render_mode"]
            SPACE["space: pymunk.Space"]
            AGENT["agent: pymunk.Body"]
            BLOCK["block: pymunk.Body"]
            GOALPOSE["goal_pose: ndarray"]
        end
    end
    
    CLASS --> INIT
    CLASS --> STEP
    CLASS --> RESET
    CLASS --> RENDER
    
    INIT --> INITOBS
    INIT --> OBSTYPE
    INIT --> RENDERMODE
    
    RESET --> SETUP
    RESET --> SETSTATE
    
    STEP --> GETCOVERAGE
    STEP --> GETOBS
    STEP --> GETINFO
    
    RENDER --> RENDERINT
    RENDERINT --> DRAW
    RENDERINT --> GETIMG
    
    SETUP --> ADDCIRCLE
    SETUP --> ADDTEE
    SETUP --> ADDSEGMENT
    SETUP --> SPACE
    SETUP --> AGENT
    SETUP --> BLOCK
    SETUP --> GOALPOSE
```

**Sources:** [gym_pusht/envs/pusht.py:40-542]()

## Data Flow and Processing Pipeline

### Environment Step Execution Flow

The environment processes actions through a multi-stage pipeline involving physics simulation, reward calculation, and observation generation:

```mermaid
graph TD
    subgraph "Input Processing"
        ACTION["action: [x, y]"]
        NSTEPS["n_steps = 1/(dt * control_hz)"]
    end
    
    subgraph "Physics Loop"
        PDCONTROL["PD Controller"]
        ACCELERATION["acceleration = k_p*(action - position) + k_v*(0 - velocity)"]
        VELOCITY["agent.velocity += acceleration * dt"]
        PHYSICS["space.step(dt)"]
    end
    
    subgraph "Reward Calculation"
        GETGOAL["get_goal_pose_body()"]
        GOALGEOM["goal_geom = pymunk_to_shapely()"]
        BLOCKGEOM["block_geom = pymunk_to_shapely()"]
        INTERSECTION["intersection_area = goal_geom.intersection(block_geom).area"]
        COVERAGE["coverage = intersection_area / goal_area"]
        REWARD["reward = clip(coverage / success_threshold, 0, 1)"]
    end
    
    subgraph "Observation Generation"
        OBSTYPE{"obs_type?"}
        STATE["state: [agent_x, agent_y, block_x, block_y, block_angle]"]
        PIXELS["pixels: _render()"]
        ENVSTATE["environment_state: get_keypoints().flatten()"]
        AGENTPOS["agent_pos: agent.position"]
    end
    
    subgraph "Termination Check"
        SUCCESS["is_success = coverage > success_threshold"]
        TERMINATED["terminated = is_success"]
    end
    
    ACTION --> NSTEPS
    NSTEPS --> PDCONTROL
    PDCONTROL --> ACCELERATION
    ACCELERATION --> VELOCITY
    VELOCITY --> PHYSICS
    
    PHYSICS --> GETGOAL
    GETGOAL --> GOALGEOM
    PHYSICS --> BLOCKGEOM
    GOALGEOM --> INTERSECTION
    BLOCKGEOM --> INTERSECTION
    INTERSECTION --> COVERAGE
    COVERAGE --> REWARD
    
    PHYSICS --> OBSTYPE
    OBSTYPE --> STATE
    OBSTYPE --> PIXELS
    OBSTYPE --> ENVSTATE
    ENVSTATE --> AGENTPOS
    
    COVERAGE --> SUCCESS
    SUCCESS --> TERMINATED
```

**Sources:** [gym_pusht/envs/pusht.py:240-266](), [gym_pusht/envs/pusht.py:383-403](), [gym_pusht/envs/pusht.py:232-238]()

## Design Patterns and Implementation Decisions

### Multi-Modal Observation Pattern

The environment implements a flexible observation system supporting four distinct observation types through conditional logic in `get_obs()`:

| Observation Type | Structure | Use Case |
|------------------|-----------|----------|
| `"state"` | `[agent_x, agent_y, block_x, block_y, block_angle]` | State-based RL algorithms |
| `"pixels"` | `(96, 96, 3)` RGB array | Vision-based RL algorithms |
| `"environment_state_agent_pos"` | Dict with `environment_state` + `agent_pos` | Keypoint-based methods |
| `"pixels_agent_pos"` | Dict with `pixels` + `agent_pos` | Hybrid vision + position methods |

**Sources:** [gym_pusht/envs/pusht.py:183-230](), [gym_pusht/envs/pusht.py:383-403]()

### Physics Integration Pattern

The implementation uses pymunk as the primary physics engine with custom integration points:

```mermaid
graph LR
    subgraph "Physics Setup"
        SPACE["pymunk.Space"]
        GRAVITY["gravity = (0, 0)"]
        DAMPING["damping = 0.0"]
    end
    
    subgraph "Body Creation"
        ADDCIRCLE["add_circle()"]
        ADDTEE["add_tee()"]
        ADDSEGMENT["add_segment()"]
    end
    
    subgraph "Control System"
        PDPARAMS["k_p=100, k_v=20"]
        CONTROLHZ["control_hz=10"]
        DT["dt=0.01"]
    end
    
    subgraph "Collision Handling"
        COLLISIONHANDLER["collision_handler"]
        HANDLECOLLISION["_handle_collision()"]
        NCONTACTS["n_contact_points"]
    end
    
    SPACE --> ADDCIRCLE
    SPACE --> ADDTEE
    SPACE --> ADDSEGMENT
    
    PDPARAMS --> CONTROLHZ
    CONTROLHZ --> DT
    
    SPACE --> COLLISIONHANDLER
    COLLISIONHANDLER --> HANDLECOLLISION
    HANDLECOLLISION --> NCONTACTS
```

**Sources:** [gym_pusht/envs/pusht.py:431-456](), [gym_pusht/envs/pusht.py:164-168](), [gym_pusht/envs/pusht.py:476-518]()

### Geometry Processing Pattern

The codebase implements a geometry processing pipeline that bridges pymunk physics bodies with shapely geometric operations:

1. **Conversion Layer**: `pymunk_to_shapely()` converts pymunk shapes to shapely polygons
2. **Coverage Calculation**: Uses shapely intersection operations for precise coverage measurement
3. **Keypoint Extraction**: `get_keypoints()` extracts T-shaped block vertices for observation

**Sources:** [gym_pusht/envs/pusht.py:27-37](), [gym_pusht/envs/pusht.py:232-238](), [gym_pusht/envs/pusht.py:520-541]()

### Rendering Pipeline Architecture

The rendering system implements a multi-stage pipeline supporting both human visualization and pixel observations:

```mermaid
graph TD
    subgraph "Rendering Entry Points"
        RENDER["render()"]
        RENDERINT["_render(visualize)"]
    end
    
    subgraph "Surface Generation"
        DRAW["_draw()"]
        SCREEN["pygame.Surface(512, 512)"]
        DRAWOPTIONS["DrawOptions(screen)"]
    end
    
    subgraph "Content Drawing"
        GOALPOSE["Draw goal_pose (LightGreen)"]
        DEBUGDRAW["space.debug_draw(draw_options)"]
    end
    
    subgraph "Image Processing"
        GETIMG["_get_img()"]
        TRANSPOSE["np.transpose()"]
        RESIZE["cv2.resize()"]
        ACTION_MARKER["cv2.drawMarker() (optional)"]
    end
    
    subgraph "Output Modes"
        RGBARRAY["rgb_array mode"]
        HUMAN["human mode"]
        WINDOW["pygame.display window"]
    end
    
    RENDER --> RENDERINT
    RENDERINT --> DRAW
    DRAW --> SCREEN
    SCREEN --> DRAWOPTIONS
    
    DRAW --> GOALPOSE
    DRAW --> DEBUGDRAW
    
    RENDERINT --> GETIMG
    GETIMG --> TRANSPOSE
    TRANSPOSE --> RESIZE
    RESIZE --> ACTION_MARKER
    
    GETIMG --> RGBARRAY
    RENDERINT --> HUMAN
    HUMAN --> WINDOW
```

**Sources:** [gym_pusht/envs/pusht.py:298-364](), [gym_pusht/envs/pusht.py:316-333]()

## Component Integration and Dependencies

### External Library Integration

The environment integrates multiple external libraries through well-defined interfaces:

| Library | Usage | Integration Point |
|---------|-------|-------------------|
| `pymunk` | 2D physics simulation | [gym_pusht/envs/pusht.py:14](), physics bodies and space |
| `pygame` | Rendering and visualization | [gym_pusht/envs/pusht.py:12](), surface and drawing operations |
| `shapely` | Geometric operations | [gym_pusht/envs/pusht.py:16](), coverage calculations |
| `gymnasium` | RL environment interface | [gym_pusht/envs/pusht.py:6](), base class and spaces |
| `opencv-python` | Image processing | [gym_pusht/envs/pusht.py:5](), image resizing and marker drawing |
| `numpy` | Numerical operations | [gym_pusht/envs/pusht.py:7](), array operations throughout |

### Environment Registration Pattern

The environment follows the standard gymnasium registration pattern with custom configuration:

```python
register(
    id="gym_pusht/PushT-v0",
    entry_point="gym_pusht.envs:PushTEnv",
    max_episode_steps=300,
    kwargs={"obs_type": "state"},
)
```

This registration enables instantiation via `gym.make("gym_pusht/PushT-v0")` with automatic wrapper application.

**Sources:** [gym_pusht/__init__.py:3-8](), [gym_pusht/envs/__init__.py:1-3]()

---

