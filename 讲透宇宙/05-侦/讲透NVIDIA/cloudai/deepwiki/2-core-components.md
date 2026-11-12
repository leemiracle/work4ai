<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cloudai · page 2 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/cloudai/__init__.py](src/cloudai/__init__.py)
- [src/cloudai/_core/exceptions.py](src/cloudai/_core/exceptions.py)
- [src/cloudai/_core/registry.py](src/cloudai/_core/registry.py)
- [src/cloudai/_core/test_scenario.py](src/cloudai/_core/test_scenario.py)
- [src/cloudai/core.py](src/cloudai/core.py)
- [src/cloudai/models/scenario.py](src/cloudai/models/scenario.py)
- [src/cloudai/models/workload.py](src/cloudai/models/workload.py)
- [src/cloudai/parser.py](src/cloudai/parser.py)
- [src/cloudai/registration.py](src/cloudai/registration.py)
- [src/cloudai/test_parser.py](src/cloudai/test_parser.py)
- [src/cloudai/test_scenario_parser.py](src/cloudai/test_scenario_parser.py)
- [tests/test_acceptance.py](tests/test_acceptance.py)
- [tests/test_init.py](tests/test_init.py)
- [tests/test_registry.py](tests/test_registry.py)
- [tests/test_test_scenario.py](tests/test_test_scenario.py)

</details>



This document covers the fundamental building blocks that make up the CloudAI framework. These core components provide the foundational abstractions for test definition, execution orchestration, and system integration that enable CloudAI's automated testing capabilities.

For information about how these components are integrated with specific schedulers like Slurm, see [Scheduler Integrations](#4). For details on the command-line interface that coordinates these components, see [Command-Line Interface](#3).

## Component Registry System

The `Registry` class serves as the central component discovery and instantiation mechanism for CloudAI. It implements the singleton pattern and maintains mappings between abstract interfaces and concrete implementations, enabling dynamic component selection based on system type and test requirements.

```mermaid
graph TB
    subgraph "Registry Singleton [src/cloudai/_core/registry.py]"
        Registry["Registry<br/>(Singleton)"]
        RunnersMap["runners_map<br/>{str: Type[BaseRunner]}"]
        StrategiesMap["command_gen_strategies_map<br/>{(System, TestDef): Strategy}"]
        SystemsMap["systems_map<br/>{str: Type[System]}"]
        TestDefsMap["test_definitions_map<br/>{str: Type[TestDefinition]}"]
        ReportsMap["reports_map<br/>{Type[TestDef]: Set[ReportStrategy]}"]
        InstallersMap["installers_map<br/>{str: Type[BaseInstaller]}"]
        AgentsMap["agents_map<br/>{str: Type[BaseAgent]}"]
    end
    
    Registry --> RunnersMap
    Registry --> StrategiesMap
    Registry --> SystemsMap
    Registry --> TestDefsMap
    Registry --> ReportsMap
    Registry --> InstallersMap
    Registry --> AgentsMap
    
    RunnersMap --> SlurmRunner["SlurmRunner"]
    RunnersMap --> K8sRunner["KubernetesRunner"]
    
    SystemsMap --> SlurmSystem["SlurmSystem"] 
    SystemsMap --> K8sSystem["KubernetesSystem"]
    
    TestDefsMap --> NCCLTestDef["NCCLTestDefinition"]
    TestDefsMap --> NeMoTestDef["NeMoRunTestDefinition"]
```

### Registry Component Mappings

The registry maintains several key mapping structures used for strategy dispatch and component instantiation:

*   **System Mappings**: Maps scheduler names to `System` implementations [src/cloudai/_core/registry.py:53]().
*   **Runner Mappings**: Maps system names to `BaseRunner` implementations [src/cloudai/_core/registry.py:51]().
*   **Strategy Mappings**: Maps `(Type[System], Type[TestDefinition])` tuples to concrete strategies like `CommandGenStrategy` [src/cloudai/_core/registry.py:60](), `JsonGenStrategy` [src/cloudai/_core/registry.py:61](), and `GradingStrategy` [src/cloudai/_core/registry.py:62]().
*   **Agent Mappings**: Maps agent names to `BaseAgent` classes for Design Space Exploration [src/cloudai/_core/registry.py:55]().

Registration is triggered globally via `register_all()` in `src/cloudai/registration.py`, which populates these maps with built-in and entrypoint-based extensions [src/cloudai/registration.py:36-187]().

For details, see [Registry System](#2.1).

**Sources**: [src/cloudai/_core/registry.py:48-62](), [src/cloudai/registration.py:36-187](), [tests/test_init.py:109-157]()

## Test Framework Object Model

The test framework provides a hierarchical structure for defining and organizing tests, using Pydantic models for validation and schema enforcement.

```mermaid
graph TB
    subgraph "Models [src/cloudai/models/]"
        TestDefModel["TestDefinition<br/>(BaseModel)"]
        TestRunModel["TestRunModel<br/>(Scenario Entry)"]
        TestScenarioModel["TestScenarioModel"]
    end
    
    subgraph "Core Entities [src/cloudai/_core/]"
        TestRun["TestRun<br/>(Execution Context)"]
        TestScenario["TestScenario<br/>(Graph)"]
        TestDependency["TestDependency"]
    end
    
    TestDefModel --> TestRunModel
    TestScenarioModel --> TestRunModel
    
    TestRunModel -.-> TestRun
    TestRun --> TestDependency
    TestScenario --> TestRun
    TestDependency --> TestRun
```

### Test Component Hierarchy

*   **TestDefinition**: Abstract base class defining the workload, its `CmdArgs`, and `installables` (like `GitRepo`) [src/cloudai/models/workload.py:90-128]().
*   **TestRun**: Represents a specific execution instance of a test within a scenario. It tracks `num_nodes`, `iterations`, `time_limit`, and runtime `dependencies` [src/cloudai/_core/test_scenario.py:58-79]().
*   **TestScenario**: A collection of `TestRun` objects. It manages scenario-level hooks (`pre_test`, `post_test`) and total time limit aggregation [src/cloudai/_core/test_scenario.py:179-196]().
*   **Design Space Exploration (DSE)**: `TestRun` supports parameter expansion. If `num_nodes` is a list or `CmdArgs` contains lists, the framework treats it as a DSE job, enabling agents to explore the parameter space [src/cloudai/_core/test_scenario.py:114-156]().

For details, see [Test Framework](#2.2).

**Sources**: [src/cloudai/models/workload.py:90-142](), [src/cloudai/_core/test_scenario.py:58-196](), [src/cloudai/models/scenario.py:65-105]()

## Parser and Configuration Loading

The `Parser` coordinates the loading of the "Three-Schema" system: System, Test, and TestScenario.

### Configuration Lifecycle
1.  **System Parsing**: `Parser.parse_system` loads the system TOML, identifies the `scheduler`, and retrieves the corresponding `System` class from the `Registry` [src/cloudai/parser.py:165-185]().
2.  **Test Parsing**: `TestParser` loads individual test templates, validating them against the registered `TestDefinition` subclasses [src/cloudai/parser.py:159-162]().
3.  **Scenario Parsing**: `TestScenarioParser` resolves dependencies between tests and merges scenario-specific overrides into the base test definitions using `deep_merge` [src/cloudai/test_scenario_parser.py:107-168]().

For details, see [Parser and Configuration Loading](#2.3).

**Sources**: [src/cloudai/parser.py:42-162](), [src/cloudai/test_scenario_parser.py:73-168]()

## Runner and Job Management

The `BaseRunner` architecture defines how jobs are submitted and monitored across different schedulers.

*   **Strategy Dispatch**: Runners use the `Registry` to find the correct `CommandGenStrategy` for a given `System` and `TestDefinition` pair [tests/test_init.py:129-157]().
*   **Dependency Resolution**: The runner respects three dependency types: `start_post_init` (starts after dependency is submitted), `start_post_comp` (starts after dependency completes), and `end_post_comp` (must complete before dependency starts) [src/cloudai/models/scenario.py:61]().
*   **Job Lifecycle**: Runners manage the transition from command generation to submission, status polling, and finally report generation via `ReportGenerationStrategy` [src/cloudai/_core/test_scenario.py:106-112]().

For details, see [Runner System and Job Management](#2.4) and [Test Dependencies and Execution Flow](#2.5).

**Sources**: [src/cloudai/_core/registry.py:51-105](), [src/cloudai/_core/test_scenario.py:37-79](), [src/cloudai/models/scenario.py:54-62]()

## Component Interaction Flow

The following diagram illustrates how core components interact during a typical test execution:

```mermaid
sequenceDiagram
    participant CLI as "CLI Handler"
    participant Parser as "Parser"
    participant Registry as "Registry"
    participant System as "System"
    participant Runner as "Runner"
    participant TestScenario as "TestScenario"
    
    CLI->>Parser: "parse(system_config, tests, scenario)"
    Parser->>Registry: "systems_map lookup"
    Registry-->>Parser: "System Class (e.g. SlurmSystem)"
    Parser->>System: "Instantiate System"
    Parser->>TestScenario: "TestScenarioParser.parse()"
    Parser-->>CLI: "system, tests, scenario"
    
    CLI->>Registry: "runners_map lookup"
    Registry-->>CLI: "Runner Class (e.g. SlurmRunner)"
    CLI->>Runner: "Instantiate Runner(system)"
    
    CLI->>Runner: "run(test_scenario)"
    Runner->>TestScenario: "Iterate test_runs"
    loop "For each TestRun"
        Runner->>Registry: "get_command_gen_strategy(system, tdef)"
        Registry-->>Runner: "Concrete Strategy"
        Runner->>System: "submit_job(command)"
        System-->>Runner: "job_id"
    end
    Runner-->>CLI: "Final Status"
```

**Sources**: [src/cloudai/parser.py:67-132](), [src/cloudai/_core/registry.py:48-105](), [src/cloudai/__init__.py:36-38]()

---

