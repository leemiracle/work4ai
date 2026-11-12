<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/jiuwensymbiosis · page 4 Action Contracts, API & Tools · fetched 2026-11-02 -->

# Action Contracts, API & Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwensymbiosis/api/decorators.py](jiuwensymbiosis/api/decorators.py)
- [jiuwensymbiosis/api/state.py](jiuwensymbiosis/api/state.py)
- [jiuwensymbiosis/api/world_state.py](jiuwensymbiosis/api/world_state.py)
- [jiuwensymbiosis/perception/scene3d.py](jiuwensymbiosis/perception/scene3d.py)
- [tests/unit_tests/adapters/cruzr/test_grasp_hygiene.py](tests/unit_tests/adapters/cruzr/test_grasp_hygiene.py)
- [tests/unit_tests/api/test_world_state.py](tests/unit_tests/api/test_world_state.py)

</details>



This page provides a high-level overview of how actions are defined, how the robot's world state is managed, and how these capabilities are exposed to the Language Model (LLM) as tools. It covers the shared vocabulary for actions, the mechanism for gating capabilities based on the robot's hardware, and the system's understanding of the world.

The core idea is to bridge the "Natural Language Space" where the LLM operates with the "Code Entity Space" of the robot's API. This is achieved through structured action definitions (`ActionSpec`), decorators (`@implements`), and a dynamic `WorldState` that informs the LLM about the current environment and robot capabilities.

## Action Contracts: Defining Robot Capabilities

Action contracts define the robot's capabilities in a structured, body-agnostic way. An `ActionSpec` describes what an action does, its parameters, expected results, and its impact on the robot's internal state and the world. These specifications form a shared vocabulary that the LLM uses for planning.

The `ActionSpec` includes:
*   `name`: A unique identifier for the action.
*   `description`: A natural language explanation for the LLM.
*   `capability`: The required hardware capability (e.g., "vision.detection", "grasp.parallel") for the action to be available.
*   `params` and `param_schema`: Define the input arguments and their types.
*   `result`: Describes the structure of the action's output.
*   `requires`, `provides`, `invalidates`: Tokens representing changes to the robot's self-state (e.g., `payload.held`, `payload.clear`).
*   `produces_location`, `consumes_location`, `invalidates_locations`: Flags for how the action affects the freshness of object locations in the world.
*   `opens_access`, `closes_access`: Indicate if an action changes the accessibility of an object (e.g., opening a drawer).
*   `planner_visible`: Controls whether the action is exposed to the LLM for planning.

For details, see [ActionSpec & @implements Decorators](#4.1).

### Action Contract Diagram

```mermaid
graph TD
    subgraph "Natural Language Space"
        NL_Prompt["User Prompt (e.g., 'Pick up the red box')"]
    end

    subgraph "Code Entity Space"
        A[ActionSpec]
        B[BaseRobotApi]
        C[Method decorated with @implements]
        D[ToolMeta]
        E[build_robot_tools]
        F[LocalFunction (Tool for LLM)]
        G[KNOWN_CAPABILITIES]
        H[KNOWN_STATE_TOKENS]
        I[WorldState]
        J[ExecutionMemory]
        K[BaseRobotEnv]
    end

    NL_Prompt --> A
    A -- "defines" --> C
    C -- "uses" --> B
    C -- "generates" --> D
    D -- "processed by" --> E
    E -- "creates" --> F
    A -- "validates capability against" --> G[jiuwensymbiosis/env/base.py:64-64]()
    A -- "validates state tokens against" --> H[jiuwensymbiosis/api/state.py:64-71]()
    F -- "exposed to" --> LLM_Planner["LLM Planner"]
    LLM_Planner -- "queries" --> I
    I -- "reads from" --> J
    I -- "observes" --> K
    J -- "updated by" --> C

    style NL_Prompt fill:#fff,stroke:#333,stroke-width:2px
    style LLM_Planner fill:#fff,stroke:#333,stroke-width:2px
```
Sources: [jiuwensymbiosis/api/decorators.py:67-127](), [jiuwensymbiosis/api/state.py:64-71](), [jiuwensymbiosis/env/base.py:64-64]()

## World State, Memory & Reachability

The `WorldState` provides a comprehensive snapshot of the robot's current situation, crucial for informed planning. It synthesizes information from three primary sources:

1.  **Observation**: Direct measurements from the robot's environment (`BaseRobotEnv`), such as its pose, joint angles, and whether it's `holding_payload`. This is the most authoritative source.
2.  **Belief**: Tokens maintained in `ExecutionMemory` that represent the robot's internal state, established by actions executed so far. This covers aspects not directly observable by sensors, like `payload.stowed`.
3.  **Proprioception + Scene**: The robot's current pose, joint states, and sensed object locations from `ExecutionMemory`.

The `WorldState` also incorporates reachability information, annotating sensed locations with whether the robot can currently reach them. This is dynamically re-evaluated on every re-plan, ensuring the planner has up-to-date spatial reasoning.

For details, see [World State, Memory & Reachability](#4.2).

### World State Data Flow

```mermaid
graph TD
    subgraph "Robot Environment"
        Env[BaseRobotEnv]
        Env_get_obs[get_observation()]
        Env_holding_payload["env.holding_payload (bool)"]
    end

    subgraph "Robot API"
        Api[BaseRobotApi]
        Api_check_reachable[check_reachable()]
        Api_describe_reach[describe_reach()]
    end

    subgraph "Memory & State"
        Mem[ExecutionMemory]
        Mem_self_state[self_state (frozenset[str])]
        Mem_locations[locations (list[dict])]
        WS[WorldState]
        WS_snapshot[WorldState.snapshot(session)]
        current_tokens_func[current_tokens(session)]
        _observed_payload_func[_observed_payload(env)]
        _with_reachability_func[_with_reachability(locations, api)]
        _reach_prior_func[_reach_prior(api)]
    end

    subgraph "LLM Planner"
        Planner[LLM Planner]
    end

    Env -- "provides" --> Env_get_obs
    Env_get_obs -- "RobotObservation (pose, joints, extra)" --> WS_snapshot
    Env -- "provides" --> Env_holding_payload
    Env_holding_payload -- "determines" --> _observed_payload_func
    _observed_payload_func -- "observed payload tokens" --> current_tokens_func

    Api -- "updates" --> Mem
    Mem_self_state -- "believed tokens" --> current_tokens_func
    current_tokens_func -- "synthesizes" --> WS_tokens[tokens (frozenset[str])]

    Mem_locations -- "sensed locations" --> _with_reachability_func
    Api_check_reachable -- "provides reachability verdict" --> _with_reachability_func
    _with_reachability_func -- "annotated locations" --> WS_locations[locations (list[dict])]

    Api_describe_reach -- "provides URDF reach model" --> _reach_prior_func
    _reach_prior_func -- "reach_prior (dict)" --> WS_reach_prior[reach_prior]

    WS_snapshot -- "assembles" --> WS
    WS_tokens --> WS
    WS_locations --> WS
    WS_reach_prior --> WS
    WS_pose[pose] --> WS
    WS_joints[joints] --> WS
    WS_extra[extra] --> WS
    WS_capabilities[capabilities] --> WS

    WS -- "informs" --> Planner
```
Sources: [jiuwensymbiosis/api/world_state.py:4-22](), [jiuwensymbiosis/api/world_state.py:36-63](), [jiuwensymbiosis/api/world_state.py:66-86](), [jiuwensymbiosis/api/world_state.py:98-107](), [jiuwensymbiosis/api/world_state.py:144-157]()

## Tool Layer: Exposing Capabilities to the LLM

The tool layer is responsible for transforming the robot's API methods into callable tools that the LLM can use. The `build_robot_tools` function inspects the `BaseRobotApi` implementation, identifies methods decorated with `@implements`, and constructs `LocalFunction` objects. Each `LocalFunction` encapsulates an action's `ToolMeta` (which includes the `ActionSpec` and the method's specific input schema) and makes it available to the LLM.

Crucially, tool exposure is gated by the robot's `capabilities`. If a robot's environment (`BaseRobotEnv`) does not declare a specific capability (e.g., "grasp.parallel"), then any action requiring that capability will not be exposed as a tool to the LLM, preventing the LLM from attempting actions the robot cannot perform. This ensures that the LLM's planning is always grounded in the physical reality of the connected hardware.

The system also handles potential risks of in-process code execution by carefully controlling the parameters and ensuring that only validated actions are exposed.

For details, see [Tool Layer](#4.3).

### Tool Exposure and Capability Gating

```mermaid
graph TD
    subgraph "Robot Implementation"
        ApiImpl[Concrete BaseRobotApi Implementation]
        MethodA["method_a(param: Type)"]
        MethodB["method_b(param: Type)"]
        MethodC["method_c(param: Type)"]
    end

    subgraph "Action Definition"
        ActionSpecA[ActionSpec for MethodA]
        ActionSpecB[ActionSpec for MethodB]
        ActionSpecC[ActionSpec for MethodC]
    end

    subgraph "Capability Management"
        EnvCaps[BaseRobotEnv.capabilities (frozenset)]
        KnownCaps[KNOWN_CAPABILITIES]
    end

    subgraph "Tool Building"
        ImplementsDecorator["@implements(ActionSpec)"]
        ToolMetaA[ToolMeta for MethodA]
        ToolMetaB[ToolMeta for MethodB]
        ToolMetaC[ToolMeta for MethodC]
        BuildTools[build_robot_tools(api)]
        FilteredTools[Capability-Filtered Tool Set]
    end

    subgraph "LLM Interaction"
        LLM[LLM Planner]
        LocalFunctionA[LocalFunction (Tool A)]
        LocalFunctionB[LocalFunction (Tool B)]
        LocalFunctionC[LocalFunction (Tool C)]
    end

    MethodA -- "decorated by" --> ImplementsDecorator
    MethodB -- "decorated by" --> ImplementsDecorator
    MethodC -- "decorated by" --> ImplementsDecorator

    ImplementsDecorator -- "attaches" --> ToolMetaA
    ImplementsDecorator -- "attaches" --> ToolMetaB
    ImplementsDecorator -- "attaches" --> ToolMetaC

    ActionSpecA -- "defines capability" --> CapA["capability='vision.detection'"]
    ActionSpecB -- "defines capability" --> CapB["capability='grasp.parallel'"]
    ActionSpecC -- "defines capability" --> CapC["capability=None (always available)"]

    ToolMetaA -- "contains" --> ActionSpecA
    ToolMetaB -- "contains" --> ActionSpecB
    ToolMetaC -- "contains" --> ActionSpecC

    BuildTools -- "inspects" --> ApiImpl
    BuildTools -- "collects" --> ToolMetaA
    BuildTools -- "collects" --> ToolMetaB
    BuildTools -- "collects" --> ToolMetaC

    BuildTools -- "filters by" --> EnvCaps
    EnvCaps -- "checked against" --> CapA
    EnvCaps -- "checked against" --> CapB
    EnvCaps -- "checked against" --> CapC

    CapA -- "e.g., 'vision.detection' in EnvCaps" --> FilteredTools
    CapB -- "e.g., 'grasp.parallel' in EnvCaps" --> FilteredTools
    CapC -- "e.g., None (always passes)" --> FilteredTools

    FilteredTools -- "exposes" --> LocalFunctionA
    FilteredTools -- "exposes" --> LocalFunctionB
    FilteredTools -- "exposes" --> LocalFunctionC

    LocalFunctionA --> LLM
    LocalFunctionB --> LLM
    LocalFunctionC --> LLM

    style EnvCaps fill:#fff,stroke:#333,stroke-width:2px
    style LLM fill:#fff,stroke:#333,stroke-width:2px
```
Sources: [jiuwensymbiosis/api/decorators.py:20-22](), [jiuwensymbiosis/api/decorators.py:130-134](), [tests/unit_tests/api/test_world_state.py:21-22](), [tests/unit_tests/api/test_world_state.py:28-29]()

---

