<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/ai2thor · page 10 Performance and Benchmarking · fetched 2026-10-30 -->

# Performance and Benchmarking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ai2thor/benchmarking.py](ai2thor/benchmarking.py)
- [ai2thor/benchmarking/benchmark_ab_arm.json](ai2thor/benchmarking/benchmark_ab_arm.json)
- [ai2thor/benchmarking/benchmark_arm.json](ai2thor/benchmarking/benchmark_arm.json)
- [ai2thor/benchmarking/benchmark_config_schema.json](ai2thor/benchmarking/benchmark_config_schema.json)
- [ai2thor/benchmarking/benchmark_stretch_arm.json](ai2thor/benchmarking/benchmark_stretch_arm.json)
- [ai2thor/benchmarking/benchmark_test.json](ai2thor/benchmarking/benchmark_test.json)
- [unity/Assets/Resources/rooms/train_4.json](unity/Assets/Resources/rooms/train_4.json)
- [unity/ProjectSettings/EditorBuildSettings.asset](unity/ProjectSettings/EditorBuildSettings.asset)

</details>



This document covers AI2-THOR's performance benchmarking framework, which provides systematic measurement and analysis of simulation performance across different scenarios, agent types, and environments. The framework enables automated testing of frame rates, physics simulation counts, and action execution times.

For information about build system performance optimization, see [Build System and Deployment](#4.2). For specialized agent performance analysis, see [Specialized Agent Types](#5).

## Architecture Overview

The benchmarking system consists of a configurable framework that can execute different types of performance measurements across various scenes and action sequences.

```mermaid
graph TB
    subgraph "Configuration Layer"
        BC["BenchmarkConfig"]
        JSON["JSON Config Files"]
        SCHEMA["benchmark_config_schema.json"]
    end
    
    subgraph "Benchmarker Implementations"
        BASE_BENCH["Benchmarker (ABC)"]
        SPS["SimsPerSecondBenchmarker"]
        PSC["PhysicsSimulateCountBenchmarker"]
    end
    
    subgraph "Execution Engine"
        RUNNER["UnityActionBenchmarkRunner"]
        ENV["ai2thor.controller.Controller"]
    end
    
    subgraph "Action System"
        AG["Action Groups"]
        SEL["Action Selectors"]
        ACTIONS["Individual Actions"]
    end
    
    subgraph "Results Processing"
        AGG["aggregate_by()"]
        TRANS["transform_aggregate()"]
        OUTPUT["JSON Output"]
    end
    
    JSON --> BC
    SCHEMA --> JSON
    BC --> RUNNER
    BC --> BASE_BENCH
    BASE_BENCH --> SPS
    BASE_BENCH --> PSC
    
    RUNNER --> ENV
    RUNNER --> AG
    AG --> SEL
    SEL --> ACTIONS
    
    SPS --> AGG
    PSC --> AGG
    AGG --> TRANS
    TRANS --> OUTPUT
    
    ENV --> SPS
    ENV --> PSC
```

**Sources:** [ai2thor/benchmarking.py:1-685]()

## Core Components

### BenchmarkConfig Class

The `BenchmarkConfig` class serves as the central configuration manager for benchmark runs. It validates benchmarker class names, manages initialization parameters, and configures execution settings.

```mermaid
graph LR
    BC["BenchmarkConfig"] --> INIT["init_params"]
    BC --> BENCH["benchmarkers[]"]
    BC --> SCENES["scenes[]"]
    BC --> HOUSES["procedural_houses[]"]
    BC --> GROUPS["action_groups{}"]
    
    INIT --> CTRL["Controller params"]
    BENCH --> SPS["SimsPerSecondBenchmarker"]
    BENCH --> PSC["PhysicsSimulateCountBenchmarker"]
    GROUPS --> AG["ActionGroup"]
    AG --> SEL["selector"]
    AG --> ACT["actions[]"]
```

Key configuration parameters include:
- `benchmarker_class_names`: List of benchmarker implementations to execute
- `init_params`: Controller initialization parameters (width, height, server_type, etc.)
- `action_group_sample_count`: Number of times to sample actions from each group
- `experiment_sample_count`: Number of times to repeat entire experiments
- `filter_object_types`: Object filtering for metadata reduction

**Sources:** [ai2thor/benchmarking.py:28-90]()

### Benchmarker Base Class

The abstract `Benchmarker` class defines the interface for all performance measurement implementations:

```mermaid
graph TB
    BENCH["Benchmarker (ABC)"]
    BENCH --> AK["aggregate_key()"]
    BENCH --> TK["transformed_key()"]
    BENCH --> NAME["name()"]
    BENCH --> BENCHMARK["benchmark()"]
    BENCH --> STEP["step_for_config()"]
    BENCH --> AGG["aggregate_by()"]
    BENCH --> TRANS["transform_aggregate()"]
    
    AK --> STR1["Returns: str"]
    TK --> STR2["Returns: str"]
    NAME --> STR3["Returns: str"]
    BENCHMARK --> DICT["Returns: dict"]
```

**Sources:** [ai2thor/benchmarking.py:92-180]()

## Benchmarker Implementations

### SimsPerSecondBenchmarker

Measures simulation frame rate by timing action execution and converting to simulations per second.

| Method | Purpose | Implementation |
|--------|---------|----------------|
| `aggregate_key()` | Returns `"average_frametime"` | Raw timing measurement |
| `transformed_key()` | Returns `"average_sims_per_second"` | Converts 1/frametime |
| `benchmark()` | Times action execution | Uses `time.perf_counter()` |

```mermaid
graph LR
    SPS["SimsPerSecondBenchmarker"]
    SPS --> START["time.perf_counter()"]
    START --> EXEC["step_for_config()"]
    EXEC --> END["time.perf_counter()"]
    END --> CALC["frame_time = end - start"]
    CALC --> TRANS["sims_per_second = 1/frame_time"]
```

**Sources:** [ai2thor/benchmarking.py:182-217]()

### PhysicsSimulateCountBenchmarker

Measures physics simulation overhead by querying the `GetPhysicsSimulateCount` action after each benchmark operation.

| Method | Return Value | Purpose |
|--------|--------------|---------|
| `aggregate_key()` | `"physics_simulate_count"` | Raw simulation count |
| `transformed_key()` | `"average_physics_simulate_count"` | Same as aggregate |
| `benchmark()` | Physics simulation count | Queries Unity physics system |

**Sources:** [ai2thor/benchmarking.py:219-257]()

## Configuration System

### JSON Configuration Files

The framework supports multiple benchmark configurations through JSON files:

- `benchmark_test.json`: Basic movement and rotation actions
- `benchmark_stretch_arm.json`: Stretch robot arm manipulation tests  
- `benchmark_ab_arm.json`: ArticulatedBody arm tests
- `benchmark_arm.json`: Complex arm pickup/drop sequences

**Sources:** [ai2thor/benchmarking/benchmark_test.json:1-72](), [ai2thor/benchmarking/benchmark_stretch_arm.json:1-206]()

### Configuration Schema

The `benchmark_config_schema.json` defines the structure and validation rules for benchmark configurations:

```mermaid
graph TB
    SCHEMA["benchmark_config_schema.json"]
    SCHEMA --> REQ["required fields"]
    SCHEMA --> PROPS["properties"]
    
    REQ --> BENCH_NAMES["benchmarker_class_names"]
    REQ --> INIT["init_params"]
    REQ --> NAME["name"]
    REQ --> ACTIONS["action_groups"]
    
    PROPS --> SCENES["scenes OR procedural_houses"]
    PROPS --> SAMPLES["sample_count configs"]
    PROPS --> FILTERS["filter_object_types"]
```

**Sources:** [ai2thor/benchmarking/benchmark_config_schema.json:1-552]()

## Action Groups and Selectors

### Action Group Structure

Action groups organize related actions for systematic testing:

```mermaid
graph LR
    GROUP["Action Group"]
    GROUP --> ACTIONS["actions[]"]
    GROUP --> SELECTOR["selector"]
    GROUP --> COUNT["sample_count"]
    
    ACTIONS --> ACTION["action object"]
    ACTION --> NAME["action name"]
    ACTION --> ARGS["arguments"]
    
    SELECTOR --> RANDOM["random"]
    SELECTOR --> SEQUENCE["sequence"]
```

### Selector Types

| Selector | Behavior | Use Case |
|----------|----------|----------|
| `"random"` | Random selection from actions array | Performance variability testing |
| `"sequence"` | Sequential execution of all actions | Deterministic test sequences |

**Sources:** [ai2thor/benchmarking.py:283-295]()

## Execution Engine

### UnityActionBenchmarkRunner

The main execution engine orchestrates benchmark runs across different scenarios:

```mermaid
graph TB
    RUNNER["UnityActionBenchmarkRunner"]
    RUNNER --> INIT_ENV["__init_env()"]
    RUNNER --> CREATE_EXP["__create_experiments()"]
    RUNNER --> TELEPORT["__teleport_to_random_reachable()"]
    RUNNER --> FILTER["__set_object_filter()"]
    RUNNER --> HOUSE["__create_procedural_house()"]
    
    INIT_ENV --> CTRL["ai2thor.controller.Controller"]
    CREATE_EXP --> EXP_LIST["experiment_list"]
    EXP_LIST --> COMBO["(scene, house, benchmarker, index)"]
```

### Experiment Execution Flow

```mermaid
graph TB
    START["benchmark()"]
    START --> ENV["Initialize Controller"]
    ENV --> EXP["Create experiment list"]
    EXP --> LOOP["For each experiment"]
    
    LOOP --> SCENE["Load scene"]
    SCENE --> HOUSE["Create procedural house"]
    HOUSE --> FILTER["Set object filters"]
    FILTER --> TELEPORT["Random teleport (optional)"]
    TELEPORT --> AG_LOOP["For each action group"]
    
    AG_LOOP --> SAMPLE_LOOP["For each sample"]
    SAMPLE_LOOP --> SELECT["Select action"]
    SELECT --> BENCH["Run benchmarker"]
    BENCH --> RECORD["Record results"]
    RECORD --> SAMPLE_LOOP
    
    SAMPLE_LOOP --> AG_LOOP
    AG_LOOP --> LOOP
    LOOP --> AGGREGATE["Aggregate results"]
    AGGREGATE --> OUTPUT["Write JSON output"]
```

**Sources:** [ai2thor/benchmarking.py:453-541]()

## Results Aggregation and Output

### Aggregation Dimensions

The framework supports multi-dimensional result aggregation:

| Dimension | Description | Keys |
|-----------|-------------|------|
| By Benchmarker | Overall performance per benchmarker | `"benchmarker"` |
| By Scene | Performance per scene/house | `["scene", "house", "benchmarker"]` |
| By Action Group | Performance per action group | `["scene", "house", "benchmarker", "action_group"]` |
| By Individual Action | Detailed per-action breakdown | `["scene", "house", "benchmarker", "action_group", "action"]` |

### Output Structure

```mermaid
graph TB
    OUTPUT["Benchmark Output"]
    OUTPUT --> META["Metadata"]
    OUTPUT --> BENCHMARKS["benchmarks{}"]
    
    META --> TITLE["title"]
    META --> CONFIG["config"]
    META --> PARAMS["controller_params"]
    META --> HOSTNAME["hostname"]
    
    BENCHMARKS --> BENCH_NAME["benchmarker_name"]
    BENCH_NAME --> SCENE_NAME["scene/house_name"]
    SCENE_NAME --> AG_NAME["action_group_name"]
    AG_NAME --> RESULTS["aggregated_results"]
```

**Sources:** [ai2thor/benchmarking.py:543-684]()

### Transform Functions

Each benchmarker can apply transformations to raw aggregate data:
- `SimsPerSecondBenchmarker`: Converts average frame time to simulations per second
- `PhysicsSimulateCountBenchmarker`: Passes through simulation count unchanged
- Custom benchmarkers can implement domain-specific transformations

**Sources:** [ai2thor/benchmarking.py:212-216](), [ai2thor/benchmarking.py:252-256]()

---

