<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/jiuwensymbiosis · page 5 Hardware Adapters & Environment Layer · fetched 2026-11-02 -->

# Hardware Adapters & Environment Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [jiuwensymbiosis/env/base.py](jiuwensymbiosis/env/base.py)
- [scripts/cruzr/dual_arm_grasp_bringup.py](scripts/cruzr/dual_arm_grasp_bringup.py)
- [scripts/new_adapter/render.py](scripts/new_adapter/render.py)
- [scripts/validate_adapter.py](scripts/validate_adapter.py)
- [templates/xxx_adapter/calibration.py](templates/xxx_adapter/calibration.py)
- [templates/xxx_adapter/env.py](templates/xxx_adapter/env.py)
- [tests/unit_tests/env/test_base.py](tests/unit_tests/env/test_base.py)
- [tests/unit_tests/test_layering.py](tests/unit_tests/test_layering.py)

</details>



This page provides a high-level overview of how `jiuwensymbiosis` interacts with physical robot hardware. It introduces the core `BaseRobotEnv` contract, the anatomy of a hardware adapter, and the various supported robot bodies. The framework's design emphasizes a shared action vocabulary and capability gating, allowing a single codebase to adapt to diverse robot form factors.

For detailed information on specific topics, please refer to the linked child pages.

## The `BaseRobotEnv` Contract

The `BaseRobotEnv` is the fundamental contract that every robot body must satisfy to integrate with the `jiuwensymbiosis` framework. It defines the minimal set of methods and properties required for the framework to interact with the hardware. Key aspects include:

*   **Capabilities**: Each `BaseRobotEnv` subclass declares a `frozenset` of `capabilities` [jiuwensymbiosis/env/base.py:108-108]() that advertise what the environment supports. These capabilities are drawn from a `KNOWN_CAPABILITIES` [jiuwensymbiosis/env/base.py:37-71]() vocabulary and are used by the framework's rails and tool builder to gate functionality.
*   **Lifecycle**: The `connect()` [jiuwensymbiosis/env/base.py:143-144]() and `disconnect()` [jiuwensymbiosis/env/base.py:147-148]() methods manage the hardware connection, ensuring idempotence.
*   **Observation**: The `get_observation()` [jiuwensymbiosis/env/base.py:150-151]() method provides a best-effort snapshot of the robot's state, returning a `RobotObservation` [jiuwensymbiosis/env/base.py:81-103]() object.
*   **Safe Posture**: The `home()` method is an unconditional action that every `BaseRobotEnv` subclass must implement to return the robot to a known-safe posture [templates/xxx_adapter/env.py:115-123]().

For a deeper dive into the `BaseRobotEnv` contract, its protocol capability slices, and how to use mock environments for hardware-free development, see [Environment Contract & Mock Env](#5.1).

Sources:
* [jiuwensymbiosis/env/base.py:37-71]()
* [jiuwensymbiosis/env/base.py:81-103]()
* [jiuwensymbiosis/env/base.py:108-108]()
* [jiuwensymbiosis/env/base.py:143-144]()
* [jiuwensymbiosis/env/base.py:147-148]()
* [jiuwensymbiosis/env/base.py:150-151]()
* [templates/xxx_adapter/env.py:115-123]()

## Adapter Anatomy

A hardware adapter in `jiuwensymbiosis` is typically structured as a Python package containing several modules that define its interaction with the robot. This modular design ensures clear separation of concerns and simplifies the process of integrating new hardware. The core components of an adapter include:

*   **Config**: Defines the robot's configuration parameters, often loaded from YAML files. This includes physical dimensions, joint limits, camera settings, and connection details.
*   **Low-Level Driver**: Implements the direct communication with the robot hardware (e.g., via serial, CAN, TCP, or ROS). This layer handles vendor-specific protocols and translates high-level commands into hardware-specific instructions.
*   **Environment (`env.py`)**: Contains the `BaseRobotEnv` subclass for the specific robot. It acts as a wrapper around the low-level driver, exposing the robot's capabilities and observations in a standardized way.
*   **API (`api.py`)**: Implements the `BaseRobotApi` for the robot, binding the shared `ActionSpec` vocabulary to the robot's specific capabilities and low-level driver functions.
*   **Session (`session.py`)**: Manages the lifecycle of the robot, including connecting to the hardware, initializing the API, and handling disconnections.

The `scripts/validate_adapter.py` [scripts/validate_adapter.py:1-24]() tool can be used to check if an adapter's structure and declared capabilities conform to the framework's conventions.

### Adapter Layering Diagram

```mermaid
graph TD
    subgraph "Agent Layer"
        A[RobotSession] --> B(build_robot_agent)
        B --> C(RobotAgentConfig)
    end

    subgraph "Safety Rails"
        C --> D(SafetyRail)
        C --> E(RecoveryRail)
        C --> F(VisualFeedbackRail)
        C --> G(SkillUseRail)
        C --> H(TraceRail)
    end

    subgraph "Tool Layer"
        G --> I(build_robot_tools)
        I --> J(RobotControlTool)
        I --> K(InProcessCodeTool)
    end

    subgraph "Skill Layer"
        J --> L(SKILL.md)
        K --> L
    end

    subgraph "API Layer"
        L --> M(ActionSpec vocabulary)
        M --> N(BaseRobotApi)
        N --> O(Mixins/@implements)
    end

    subgraph "Env Layer"
        O --> P(BaseRobotEnv)
        P --> Q(capabilities)
        P --> R(connect/disconnect)
        P --> S(get_observation)
    end

    subgraph "Hardware Layer"
        S --> T(XxxDriver)
        T --> U(Serial/CAN/Socket)
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#f9f,stroke:#333,stroke-width:2px
    style J fill:#f9f,stroke:#333,stroke-width:2px
    style K fill:#f9f,stroke:#333,stroke-width:2px
    style L fill:#f9f,stroke:#333,stroke-width:2px
    style M fill:#f9f,stroke:#333,stroke-width:2px
    style N fill:#f9f,stroke:#333,stroke-width:2px
    style O fill:#f9f,stroke:#333,stroke-width:2px
    style P fill:#f9f,stroke:#333,stroke-width:2px
    style Q fill:#f9f,stroke:#333,stroke-width:2px
    style R fill:#f9f,stroke:#333,stroke-width:2px
    style S fill:#f9f,stroke:#333,stroke-width:2px
    style T fill:#f9f,stroke:#333,stroke-width:2px
    style U fill:#f9f,stroke:#333,stroke-width:2px
```
*Diagram: Layered Architecture of `jiuwensymbiosis`*

Sources:
* [AGENTS.md:97-105]()
* [scripts/validate_adapter.py:1-24]()

## Supported Robot Bodies

`jiuwensymbiosis` supports various robot bodies through its adapter mechanism. Each adapter provides the necessary configuration, low-level drivers, environment implementation, and API bindings for its specific hardware.

### SO-101 Adapter

The SO-101 adapter integrates a 5-DoF robotic arm, leveraging the LeRobot backend for control. It includes specific implementations for its configuration, low-level control, environment, and API. For more details, see [SO-101 Adapter](#5.2).

### Piper Adapter

The Piper adapter supports a 6-DoF arm combined with a RealSense camera. Its implementation covers configuration, environment setup, API, low-level control, and calibration procedures, often relying on YAML configuration files. For more details, see [Piper Adapter](#5.3).

### Cruzr Mobile Dual-Arm Adapter & ROS 2

The Cruzr adapter integrates a mobile robot with dual arms, utilizing ROS 2 for communication and control. It features distinct layers for its configuration, environment, API, and low-level drivers, including ROS 2 bridge modules and scripts for dual-arm bringup and mobile-base navigation. For more details, see [Cruzr Mobile Dual-Arm Adapter & ROS 2](#5.4).

Sources:
* [scripts/cruzr/dual_arm_grasp_bringup.py:1-120]()

## Shared Adapter Commons: Kinematics & Motion

Many adapters share common functionalities related to kinematics and motion control. These shared components are often found in the `adapters/_common` directory and include:

*   **Geometry**: Utilities for handling robot geometry and transformations.
*   **Kinematic Driver**: Provides forward and inverse kinematics, reachability analysis, and self-collision detection.
*   **Joint Transport**: Manages joint-space movements.
*   **LeRobot Backend**: A common backend for certain robot types.
*   **Motion Primitives**: Implementations for common motion patterns like approach, dual-arm coordination, differential drive, and lifting.

For a detailed explanation of these shared components, see [Shared Adapter Commons: Kinematics & Motion](#5.5).

## Building a New Adapter

The framework provides tools and templates to streamline the creation of new hardware adapters. This process typically involves:

*   **Scaffolding**: Using templates like `templates/xxx_adapter` [templates/xxx_adapter/env.py:1-174]() to generate the basic file structure.
*   **Renderer**: Employing scripts like `scripts/new_adapter/render.py` [scripts/new_adapter/render.py:1-173]() to populate the templates with initial code based on the robot's specifications.
*   **Validation**: Using `scripts/validate_adapter.py` [scripts/validate_adapter.py:1-24]() to ensure the new adapter conforms to framework standards.
*   **Testing**: Running `smoke_test_adapter` checks to verify basic functionality.
*   **Porting Guide**: Following a guide to implement the specific hardware interactions.

For a comprehensive guide on creating a new adapter, see [Building a New Adapter](#5.6).

Sources:
* [scripts/new_adapter/render.py:1-173]()
* [scripts/validate_adapter.py:1-24]()
* [templates/xxx_adapter/env.py:1-174]()

---

