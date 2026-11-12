<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/gym-pusht · page 2 PushT Environment · fetched 2026-10-26 -->

# PushT Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gym_pusht/__init__.py](gym_pusht/__init__.py)
- [gym_pusht/envs/pusht.py](gym_pusht/envs/pusht.py)

</details>



This document provides comprehensive technical documentation for the PushT environment implementation, covering its architecture, components, and core functionality. The PushT environment is a 2D robotic manipulation task where an agent must push a T-shaped block into a goal zone using physics-based simulation.

For information about the public API interface and usage examples, see [Environment API](#2.1). For details about the underlying physics engine integration, see [Physics Simulation](#2.2). For information about different observation modalities, see [Observation Types](#2.3).

## Core Architecture Overview

The PushT environment is implemented as a single `PushTEnv` class that integrates multiple subsystems to create a complete robotic manipulation simulation. The environment follows the Gymnasium API standard while providing multiple observation modalities and physics-based dynamics.

### System Architecture

```mermaid
graph TB
    subgraph "Gymnasium Interface"
        API["PushTEnv Class<br/>gym_pusht/envs/pusht.py"]
        SPACES["Observation & Action Spaces"]
        METHODS["step(), reset(), render()"]
    end
    
    subgraph "Physics Simulation"
        PYMUNK["pymunk.Space"]
        AGENT["Circular Agent Body"]
        BLOCK["T-shaped Block Body"]
        WALLS["Wall Segments"]
        PD["PD Controller"]
    end
    
    subgraph "Observation System"
        STATE["State Vector"]
        PIXELS["RGB Images"]
        KEYPOINTS["Environment Keypoints"]
        HYBRID["Hybrid Observations"]
    end
    
    subgraph "Rendering Pipeline"
        PYGAME["pygame Surface"]
        DRAW["DrawOptions"]
        OPENCV["cv2 Processing"]
        VISUALIZATION["Visual Output"]
    end
    
    subgraph "Reward & Success"
        SHAPELY["shapely Geometry"]
        COVERAGE["Coverage Calculation"]
        REWARD["Reward Function"]
        SUCCESS["Success Detection"]
    end
    
    API --> SPACES
    API --> METHODS
    METHODS --> PYMUNK
    METHODS --> STATE
    METHODS --> PIXELS
    
    PYMUNK --> AGENT
    PYMUNK --> BLOCK
    PYMUNK --> WALLS
    PD --> AGENT
    
    STATE --> COVERAGE
    PIXELS --> PYGAME
    KEYPOINTS --> COVERAGE
    HYBRID --> STATE
    HYBRID --> PIXELS
    
    PYGAME --> DRAW
    PYGAME --> OPENCV
    OPENCV --> VISUALIZATION
    
    SHAPELY --> COVERAGE
    COVERAGE --> REWARD
    COVERAGE --> SUCCESS
    
    REWARD --> API
    SUCCESS --> API
```

Sources: [gym_pusht/envs/pusht.py:40-542]()

### Component Integration Flow

```mermaid
graph LR
    subgraph "Environment Lifecycle"
        INIT["__init__()"]
        RESET["reset(seed, options)"]
        STEP["step(action)"]
        RENDER["render()"]
    end
    
    subgraph "Physics Integration"
        SETUP["_setup()"]
        SPACE_STEP["space.step(dt)"]
        PD_CONTROL["PD Control Loop"]
        COLLISION["Collision Handling"]
    end
    
    subgraph "State Management"
        SET_STATE["_set_state(state)"]
        GET_OBS["get_obs()"]
        GET_INFO["_get_info()"]
        GET_COVERAGE["_get_coverage()"]
    end
    
    subgraph "Rendering System"
        DRAW_FUNC["_draw()"]
        GET_IMG["_get_img()"]
        PYGAME_RENDER["pygame Rendering"]
    end
    
    INIT --> RESET
    RESET --> SETUP
    SETUP --> SET_STATE
    
    STEP --> PD_CONTROL
    PD_CONTROL --> SPACE_STEP
    SPACE_STEP --> COLLISION
    COLLISION --> GET_COVERAGE
    GET_COVERAGE --> GET_OBS
    GET_OBS --> GET_INFO
    
    RENDER --> DRAW_FUNC
    DRAW_FUNC --> GET_IMG
    GET_IMG --> PYGAME_RENDER
    
    GET_OBS --> RENDER
```

Sources: [gym_pusht/envs/pusht.py:137-467]()

## Environment Components

### Core Class Structure

The `PushTEnv` class inherits from `gym.Env` and implements all required Gymnasium interface methods. The class manages multiple subsystems through carefully orchestrated initialization and update cycles.

| Component | Type | Purpose | Key Methods |
|-----------|------|---------|-------------|
| `obs_type` | str | Observation modality selection | `_initialize_observation_space()` |
| `space` | `pymunk.Space` | Physics simulation container | `_setup()` |
| `agent` | `pymunk.Body` | Circular robot agent | `add_circle()` |
| `block` | `pymunk.Body` | T-shaped manipulation target | `add_tee()` |
| `goal_pose` | `np.ndarray` | Target configuration | `get_goal_pose_body()` |

The environment supports four distinct observation types: `state`, `pixels`, `environment_state_agent_pos`, and `pixels_agent_pos`, each providing different information modalities for reinforcement learning algorithms.

Sources: [gym_pusht/envs/pusht.py:137-181](), [gym_pusht/envs/pusht.py:183-230]()

### Physics Object Configuration

```mermaid
graph TB
    subgraph "Physics Bodies"
        AGENT_BODY["agent: pymunk.Body<br/>KINEMATIC type<br/>radius=15, friction=1"]
        BLOCK_BODY["block: pymunk.Body<br/>DYNAMIC type<br/>T-shaped composite"]
        WALL_BODIES["walls: Static Bodies<br/>4 boundary segments"]
    end
    
    subgraph "Block Composition"
        SHAPE1["shape1: Horizontal Bar<br/>4*scale x scale"]
        SHAPE2["shape2: Vertical Bar<br/>scale x 4*scale"]
        COG["Center of Gravity<br/>Calculated from shapes"]
    end
    
    subgraph "Physics Properties"
        MASS["mass = 1"]
        INERTIA["inertia = moment_for_poly"]
        FRICTION["friction = 1"]
        FILTER["ShapeFilter masks"]
    end
    
    BLOCK_BODY --> SHAPE1
    BLOCK_BODY --> SHAPE2
    SHAPE1 --> COG
    SHAPE2 --> COG
    
    MASS --> BLOCK_BODY
    INERTIA --> BLOCK_BODY
    FRICTION --> AGENT_BODY
    FRICTION --> BLOCK_BODY
    FILTER --> SHAPE1
    FILTER --> SHAPE2
```

Sources: [gym_pusht/envs/pusht.py:477-518](), [gym_pusht/envs/pusht.py:431-456]()

## Control System Architecture

### PD Control Implementation

The environment implements a Proportional-Derivative (PD) controller to manage agent movement. The controller converts discrete target positions into smooth velocity commands applied to the physics simulation.

```mermaid
graph LR
    subgraph "Control Pipeline"
        ACTION["action: [x, y]<br/>Target Position"]
        PD_CALC["PD Calculation<br/>k_p=100, k_v=20"]
        ACCEL["acceleration<br/>Vec2d"]
        VELOCITY["agent.velocity<br/>Updated"]
        PHYSICS["space.step(dt)<br/>dt=0.01"]
    end
    
    subgraph "Control Loop"
        N_STEPS["n_steps = 1/(dt*control_hz)"]
        LOOP["for _ in range(n_steps)"]
        UPDATE["Velocity Update"]
    end
    
    ACTION --> PD_CALC
    PD_CALC --> ACCEL
    ACCEL --> VELOCITY
    VELOCITY --> PHYSICS
    
    N_STEPS --> LOOP
    LOOP --> UPDATE
    UPDATE --> PHYSICS
```

The PD controller equation implemented in the step method:
- `acceleration = k_p * (action - agent.position) + k_v * (Vec2d(0, 0) - agent.velocity)`
- `agent.velocity += acceleration * dt`

Sources: [gym_pusht/envs/pusht.py:240-253](), [gym_pusht/envs/pusht.py:164-166]()

### Collision Detection and Response

The environment implements collision detection through pymunk's built-in collision system with custom handling for contact point tracking.

```mermaid
graph TB
    subgraph "Collision System"
        HANDLER["collision_handeler<br/>space.add_collision_handler(0, 0)"]
        POST_SOLVE["post_solve callback<br/>_handle_collision()"]
        CONTACT_POINTS["n_contact_points<br/>Counter"]
    end
    
    subgraph "Collision Processing"
        ARBITER["arbiter: Collision Info"]
        CONTACT_SET["contact_point_set.points"]
        COUNT["len(points)"]
        ACCUMULATE["Accumulate Contacts"]
    end
    
    HANDLER --> POST_SOLVE
    POST_SOLVE --> ARBITER
    ARBITER --> CONTACT_SET
    CONTACT_SET --> COUNT
    COUNT --> ACCUMULATE
    ACCUMULATE --> CONTACT_POINTS
```

Sources: [gym_pusht/envs/pusht.py:428-430](), [gym_pusht/envs/pusht.py:453-456]()

## Reward and Success Computation

### Coverage-Based Reward System

The environment uses geometric intersection calculations to determine reward based on how much of the T-shaped block overlaps with the goal zone.

```mermaid
graph TD
    subgraph "Geometry Conversion"
        BLOCK_PYMUNK["block: pymunk.Body"]
        GOAL_PYMUNK["goal_body: pymunk.Body"]
        CONV_FUNC["pymunk_to_shapely()"]
        BLOCK_GEOM["block_geom: shapely.Polygon"]
        GOAL_GEOM["goal_geom: shapely.Polygon"]
    end
    
    subgraph "Coverage Calculation"
        INTERSECTION["intersection_area<br/>goal_geom.intersection(block_geom).area"]
        GOAL_AREA["goal_area<br/>goal_geom.area"]
        RATIO["coverage = intersection_area / goal_area"]
    end
    
    subgraph "Reward & Success"
        REWARD_CALC["reward = clip(coverage / 0.95, 0, 1)"]
        SUCCESS_CHECK["terminated = coverage > 0.95"]
        THRESHOLD["success_threshold = 0.95"]
    end
    
    BLOCK_PYMUNK --> CONV_FUNC
    GOAL_PYMUNK --> CONV_FUNC
    CONV_FUNC --> BLOCK_GEOM
    CONV_FUNC --> GOAL_GEOM
    
    BLOCK_GEOM --> INTERSECTION
    GOAL_GEOM --> INTERSECTION
    GOAL_GEOM --> GOAL_AREA
    INTERSECTION --> RATIO
    GOAL_AREA --> RATIO
    
    RATIO --> REWARD_CALC
    RATIO --> SUCCESS_CHECK
    THRESHOLD --> SUCCESS_CHECK
    THRESHOLD --> REWARD_CALC
```

The `pymunk_to_shapely()` function converts pymunk polygon shapes to shapely geometries for precise intersection calculations.

Sources: [gym_pusht/envs/pusht.py:232-238](), [gym_pusht/envs/pusht.py:27-37](), [gym_pusht/envs/pusht.py:255-258](), [gym_pusht/envs/pusht.py:181]()

## State Management and Initialization

### Environment Setup Process

The environment initialization follows a structured setup process that creates the physics world and populates it with the necessary objects.

```mermaid
graph TD
    subgraph "Setup Sequence"
        SPACE_INIT["space = pymunk.Space()"]
        GRAVITY["space.gravity = (0, 0)"]
        DAMPING["space.damping = damping"]
        WALLS["Add 4 wall segments"]
        AGENT_ADD["Add circular agent"]
        BLOCK_ADD["Add T-shaped block"]
        GOAL_SET["Set goal_pose"]
        COLLISION_SETUP["Setup collision handler"]
    end
    
    subgraph "Object Creation"
        SEGMENT_FUNC["add_segment(space, a, b, radius)"]
        CIRCLE_FUNC["add_circle(space, position, radius)"]
        TEE_FUNC["add_tee(space, position, angle)"]
    end
    
    subgraph "State Setting"
        STATE_ARRAY["state[5]: [agent_x, agent_y, block_x, block_y, block_angle]"]
        SET_POSITIONS["Set body positions"]
        SET_ANGLE["Set block angle"]
        PHYSICS_STEP["space.step(dt) - Apply changes"]
    end
    
    SPACE_INIT --> GRAVITY
    GRAVITY --> DAMPING
    DAMPING --> WALLS
    WALLS --> AGENT_ADD
    AGENT_ADD --> BLOCK_ADD
    BLOCK_ADD --> GOAL_SET
    GOAL_SET --> COLLISION_SETUP
    
    WALLS --> SEGMENT_FUNC
    AGENT_ADD --> CIRCLE_FUNC
    BLOCK_ADD --> TEE_FUNC
    
    STATE_ARRAY --> SET_POSITIONS
    SET_POSITIONS --> SET_ANGLE
    SET_ANGLE --> PHYSICS_STEP
```

Sources: [gym_pusht/envs/pusht.py:431-456](), [gym_pusht/envs/pusht.py:458-467](), [gym_pusht/envs/pusht.py:469-518]()

### Random State Generation

The reset method generates random initial states using controlled randomization to ensure reproducible episodes while maintaining task diversity.

| Parameter | Range | Purpose |
|-----------|-------|---------|
| `agent_x` | [50, 450] | Agent horizontal position |
| `agent_y` | [50, 450] | Agent vertical position |
| `block_x` | [100, 400] | Block horizontal position |
| `block_y` | [100, 400] | Block vertical position |
| `block_angle` | [-π, π] | Block rotation angle |

The environment also supports deterministic state setting through the `reset_to_state` option, enabling reproducible evaluation scenarios.

Sources: [gym_pusht/envs/pusht.py:268-296](), [gym_pusht/envs/pusht.py:272-287]()

---

