<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mujoco_mpc · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [mjpc/CMakeLists.txt](mjpc/CMakeLists.txt)
- [mjpc/agent.cc](mjpc/agent.cc)
- [mjpc/agent.h](mjpc/agent.h)
- [mjpc/app.cc](mjpc/app.cc)
- [mjpc/app.h](mjpc/app.h)
- [mjpc/interface.cc](mjpc/interface.cc)
- [mjpc/interface.h](mjpc/interface.h)
- [mjpc/main.cc](mjpc/main.cc)
- [mjpc/planners/include.cc](mjpc/planners/include.cc)
- [mjpc/planners/planner.cc](mjpc/planners/planner.cc)
- [mjpc/simulate.cc](mjpc/simulate.cc)
- [mjpc/simulate.h](mjpc/simulate.h)
- [mjpc/tasks/tasks.cc](mjpc/tasks/tasks.cc)
- [mjpc/tasks/tasks.h](mjpc/tasks/tasks.h)
- [python/setup.py](python/setup.py)

</details>



MuJoCo MPC (MJPC) is a comprehensive framework developed by Google DeepMind for real-time Model Predictive Control (MPC) using the MuJoCo physics engine. It provides an interactive application and software stack that enables researchers and engineers to author, solve, and visualize complex robotics tasks with different planning algorithms. This page provides a high-level overview of the system architecture, core components, and execution model.

## Purpose and Core Capabilities

MuJoCo MPC serves as:
1. An interactive application for testing and visualizing MPC solutions
2. A software framework for implementing custom MPC problems
3. A testbed for comparing different planning algorithms on robotics tasks

The framework supports multiple planning methods including:
- Sampling-based planners (Predictive Sampling, Cross Entropy)
- Derivative-based planners (iLQG, Gradient Descent)
- Hybrid approaches (Sample Gradient)

Sources: [README.md:14-21](), [mjpc/planners/include.cc:30-37]()

## System Architecture

The system is built around several key components that work together to provide the MPC functionality:

```mermaid
graph TD
    subgraph "Core Components"
        Agent["Agent System"]
        Planners["Planners"]
        Tasks["Tasks"]
        Estimators["Estimators"]
        State["State Management"]
    end

    subgraph "Execution"
        PlanThread["Planning Thread"]
        PhysicsThread["Physics Thread"]
        EstimatorThread["Estimator Thread"]
        RenderThread["Render Thread"]
    end

    subgraph "Integration"
        MuJoCo["MuJoCo Physics Engine"]
        UI["Graphical UI"]
        Python["Python API"]
    end

    Agent --- Planners
    Agent --- Tasks
    Agent --- Estimators
    Agent --- State

    PlanThread --> Agent
    PhysicsThread --> Agent
    EstimatorThread --> Agent
    RenderThread --> UI

    Agent --> MuJoCo
    UI --> Agent
    Python --> Agent
```

Sources: [mjpc/agent.h:44-256](), [mjpc/app.cc:483-502]()

## Core Components in Detail

### Agent System

The Agent is the central orchestrator of the MPC process. It:
- Initializes and manages the models, planners, estimators, and tasks
- Coordinates the planning and execution loops
- Handles state transitions and updates
- Provides visualization and UI elements

```mermaid
classDiagram
    class Agent {
        +mjModel* model_
        +State state
        +Planner* ActivePlanner()
        +Estimator* ActiveEstimator()
        +Task* ActiveTask()
        +Initialize(model)
        +Allocate()
        +Reset()
        +PlanIteration(pool)
        +Plan(exitrequest, uiloadrequest)
        +SetState(data)
        +ModifyScene(scn)
    }

    class State {
        +time
        +qpos
        +qvel
        +act
        +mocap_pos
        +mocap_quat
        +userdata
        +Initialize(model)
        +Reset()
        +Set(model, data)
    }

    Agent --> State : contains
```

The Agent class maintains the planning model, state information, and references to the active planner, estimator, and task. It provides methods for initialization, memory allocation, and resetting the system, as well as for planning iterations and state updates.

Sources: [mjpc/agent.h:44-256](), [mjpc/agent.cc:60-164]()

### Planning System

MuJoCo MPC includes several planning algorithms, each implemented as a subclass of the `Planner` base class:

```mermaid
classDiagram
    class Planner {
        <<abstract>>
        +Initialize(model, task)
        +Allocate()
        +Reset(horizon, initial_action)
        +SetState(state)
        +OptimizePolicy(horizon, pool)
        +ActionFromPolicy(action, state, time)
        +NominalTrajectory(horizon, pool)
        +BestTrajectory()
    }
    
    class SamplingPlanner {
        -Trajectory nominal
        -std::vector<Trajectory> trajectories
        +OptimizePolicy(horizon, pool)
        +ActionFromPolicy(action, state, time)
    }
    
    class GradientPlanner {
        -GradientPolicy policy
        +OptimizePolicy(horizon, pool)
        +ActionFromPolicy(action, state, time)
    }
    
    class iLQGPlanner {
        -iLQGPolicy policy
        +OptimizePolicy(horizon, pool)
        +ActionFromPolicy(action, state, time)
    }

    Planner <|-- SamplingPlanner
    Planner <|-- GradientPlanner
    Planner <|-- iLQGPlanner
    Planner <|-- CrossEntropyPlanner
    Planner <|-- iLQSPlanner
    Planner <|-- RobustPlanner
    Planner <|-- SampleGradientPlanner
```

The different planners implement various optimization strategies:
- **SamplingPlanner**: Generates random action sequences and selects the best
- **GradientPlanner**: Uses gradient information to optimize action sequences
- **iLQGPlanner**: Implements iterative Linear Quadratic Gaussian control
- **iLQSPlanner**: Iterative Linear Quadratic regulator for constrained systems
- **CrossEntropyPlanner**: Uses the Cross Entropy Method for sampling
- **RobustPlanner**: Adds robustness to other planners
- **SampleGradientPlanner**: Combines sampling and gradient-based approaches

Sources: [mjpc/planners/include.cc:30-53](), [mjpc/CMakeLists.txt:84-120]()

### Task System

Tasks define the objectives and environments for the MPC problem:

```mermaid
classDiagram
    class Task {
        <<abstract>>
        +std::vector~double~ parameters
        +std::vector~double~ weight
        +int mode
        +int reset
        +int visualize
        +int num_term
        +int num_trace
        +int num_residual
        +Name() string
        +XmlPath() string
        +Residual(model, data, residual)
        +CostValue(residual)
        +CostTerms(terms, residual)
        +Transition(model, data)
        +Reset(model)
    }
    
    Task <|-- Acrobot
    Task <|-- Cartpole
    Task <|-- Humanoid_Walk
    Task <|-- Quadruped
    Task <|-- Particle
    Task <|-- Manipulation
```

MJPC includes over 20 pre-defined tasks covering a wide range of robotics problems:
- Basic control (Cartpole, Acrobot, Particle)
- Locomotion (Humanoid walking, Quadruped)
- Manipulation (Bimanual handover, reorientation)
- Complex coordination (Rubik's cube, Shadow hand)

Each task defines:
- A residual function that computes the cost/objective
- Transition logic for managing task phases
- Visualization elements for the UI
- Task-specific parameters and weights

Sources: [mjpc/tasks/tasks.cc:46-73](), [mjpc/CMakeLists.txt:37-84]()

### Estimator System

Estimators provide state estimation capabilities when direct state measurement isn't available:

```mermaid
classDiagram
    class Estimator {
        <<abstract>>
        +Initialize(model)
        +Reset(data)
        +Update(ctrl, sensor)
        +State() double*
        +Covariance() double*
        +Data() mjData*
    }
    
    class BatchEstimator {
        +Update(ctrl, sensor)
    }
    
    class KalmanFilter {
        +Update(ctrl, sensor)
    }
    
    Estimator <|-- BatchEstimator
    Estimator <|-- KalmanFilter
    Estimator <|-- UnscentedKalmanFilter
    Estimator <|-- GroundTruth
```

The available estimators include:
- **BatchEstimator**: Performs batch estimation
- **KalmanFilter**: Standard Kalman Filter implementation
- **UnscentedKalmanFilter**: Unscented Kalman Filter for nonlinear systems
- **GroundTruth**: Uses direct state information (no estimation)

Sources: [mjpc/CMakeLists.txt:123-131](), [mjpc/agent.cc:120-126]()

## Execution Model

MuJoCo MPC employs a multi-threaded architecture to efficiently handle planning, physics simulation, state estimation, and rendering:

```mermaid
sequenceDiagram
    participant Main
    participant PhysicsThread
    participant PlanningThread
    participant EstimatorThread
    participant RenderThread
    
    Main->>+RenderThread: Start UI Loop
    Main->>+PhysicsThread: Start Physics Loop
    Main->>+PlanningThread: Start Planning Loop
    Main->>+EstimatorThread: Start Estimator Loop (optional)
    
    loop Physics Loop
        PhysicsThread->>PhysicsThread: Step MuJoCo simulation
        PhysicsThread->>EstimatorThread: Update sensor data
        PhysicsThread-->>PlanningThread: Update state
    end
    
    loop Planning Loop
        PlanningThread->>PlanningThread: OptimizePolicy()
        PlanningThread->>PhysicsThread: Update best policy
    end
    
    loop Estimator Loop (if enabled)
        EstimatorThread->>EstimatorThread: Update state estimate
        EstimatorThread-->>PlanningThread: Update state
    end
    
    loop Render Loop
        RenderThread->>RenderThread: Render scene with MuJoCo
        RenderThread->>RenderThread: Handle UI events
    end
```

The system operates with the following threads:
1. **Physics Thread**: Runs the MuJoCo simulation at a high frequency
2. **Planning Thread**: Continuously optimizes the control policy
3. **Estimator Thread** (optional): Updates state estimates from sensor data
4. **Render Thread**: Handles UI and visualization

Thread synchronization is carefully managed to ensure efficient operation without deadlocks.

Sources: [mjpc/app.cc:128-386](), [mjpc/agent.cc:359-371]()

## Integration with MuJoCo

MuJoCo MPC tightly integrates with the MuJoCo physics engine:

```mermaid
graph LR
    subgraph "MuJoCo MPC"
        Agent
        Planner
        Task
        Estimator
    end
    
    subgraph "MuJoCo Physics Engine"
        mjModel["mjModel (physics model)"]
        mjData["mjData (physics state)"]
        mjStep["mj_step (physics step)"]
        mjVis["mjv_* (visualization)"]
    end
    
    Agent -->|"Initialize(model)"| mjModel
    Agent -->|"SetState(data)"| mjData
    Planner -->|"Rollout trajectories"| mjStep
    Task -->|"Evaluate residual"| mjData
    Agent -->|"ModifyScene()"| mjVis
```

Key integration points include:
- Using MuJoCo's `mjModel` to define the physics model
- Using `mjData` to track the physics state
- Using MuJoCo's `mj_step` function for forward simulation
- Using MuJoCo's visualization functions for rendering
- Adding callbacks for controllers and sensors

Sources: [mjpc/agent.cc:69-114](), [mjpc/app.cc:84-103]()

## Python API

MuJoCo MPC also provides a Python API for use in Python applications:

```mermaid
graph LR
    subgraph "Python API"
        PyAgent["Agent class"]
        PyTasks["Task definitions"]
        PyGRPC["gRPC services"]
    end
    
    subgraph "C++ Core"
        Agent
        Tasks
        Planners
        gRPC["gRPC server"]
    end
    
    PyAgent -->|"calls"| PyGRPC
    PyGRPC -->|"communicates with"| gRPC
    gRPC -->|"controls"| Agent
    PyTasks -->|"defines"| Tasks
```

The Python API:
- Uses gRPC to communicate with the C++ core
- Provides a similar interface to the C++ API
- Allows for task definition and control from Python
- Enables integration with other Python libraries

Sources: [python/setup.py:15-315](), [README.md:157-198]()

## Summary

MuJoCo MPC provides a comprehensive framework for implementing Model Predictive Control for robotics applications using the MuJoCo physics engine. Its modular architecture allows for easy extension with new planners, tasks, and estimators, while its multi-threaded execution model ensures efficient real-time performance. The system can be used both as an interactive application through its GUI and as a software library through its C++ and Python APIs.

---

