<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/acme · page 2 Core Framework Components · fetched 2026-10-26 -->

# Core Framework Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [acme/agents/agent.py](acme/agents/agent.py)
- [acme/agents/jax/ail/builder.py](acme/agents/jax/ail/builder.py)
- [acme/core.py](acme/core.py)
- [acme/jax/variable_utils.py](acme/jax/variable_utils.py)
- [acme/jax/variable_utils_test.py](acme/jax/variable_utils_test.py)
- [acme/testing/fakes.py](acme/testing/fakes.py)

</details>



## Purpose and Scope

This document provides a deep dive into the fundamental building blocks of the Acme reinforcement learning framework. These core framework components establish the architectural foundation that enables modular composition of RL agents, distributed execution, and systematic experimentation.

The framework is built around key abstractions that separate concerns: `Actor` for policy execution, `Learner` for parameter updates, and `VariableSource` for parameter sharing. These interfaces compose into complete agents through the `Agent` class and integrate with environment interaction via `EnvironmentLoop`.

This page provides an overview of the core framework architecture. For detailed coverage of specific components, see:
- Core Interfaces and Agent Composition (page 2.1)
- Environment Loop and Execution (page 2.2) 
- Actor System and Policy Execution (page 2.3)
- Experience Collection and Replay (page 2.4)

## Framework Architecture Overview

The Acme framework separates reinforcement learning into distinct, composable components. The architecture enables both single-process and distributed deployments through clean interface abstractions.

### Core Framework Components

```mermaid
graph TB
    subgraph "Core Interfaces"
        Actor["core.Actor<br/>select_action()<br/>observe()<br/>update()"]
        Learner["core.Learner<br/>step()<br/>get_variables()"]
        VariableSource["core.VariableSource<br/>get_variables()"]
        Worker["core.Worker<br/>run()"]
        Saveable["core.Saveable<br/>save()<br/>restore()"]
    end
    
    subgraph "Agent Composition"
        Agent["agents.agent.Agent<br/>Combines Actor + Learner"]
        EnvironmentLoop["environment_loop.EnvironmentLoop<br/>Actor-Environment orchestration"]
    end
    
    subgraph "Parameter Synchronization"
        VariableClient["variable_utils.VariableClient<br/>Async parameter updates"]
        ReferenceVariableSource["variable_utils.ReferenceVariableSource<br/>Parameter references"]
    end
    
    subgraph "Experience Management"
        Adder["adders.Adder<br/>Experience collection"]
        PrefetchingIterator["core.PrefetchingIterator<br/>Async data loading"]
    end
    
    Learner --|"inherits"| VariableSource
    Learner --|"inherits"| Worker  
    Learner --|"inherits"| Saveable
    Agent --|"implements"| Actor
    Agent --|"implements"| VariableSource
    Agent --> Actor
    Agent --> Learner
    EnvironmentLoop --> Actor
    VariableClient --> VariableSource
    Actor --> Adder
    Learner --> PrefetchingIterator
```

Sources: [acme/core.py:31-177](), [acme/agents/agent.py:43-136](), [acme/jax/variable_utils.py:31-154]()

## Core Interface Definitions

The framework defines abstract interfaces that establish contracts between components. These interfaces enable modular composition and support both local and distributed deployments.

### Primary Interfaces

```mermaid
classDiagram
    class Actor {
        <<abstract>>
        +select_action(observation) NestedArray
        +observe_first(timestep)
        +observe(action, next_timestep)
        +update(wait: bool)
    }
    
    class VariableSource {
        <<abstract>>
        +get_variables(names: Sequence[str]) List[NestedArray]
    }
    
    class Worker {
        <<abstract>>
        +run()
    }
    
    class Saveable~T~ {
        <<abstract>>
        +save() T
        +restore(state: T)
    }
    
    class Learner {
        <<abstract>>
        +step()
        +run(num_steps: Optional[int])
    }
    
    class PrefetchingIterator~T~ {
        <<abstract>>
        +ready() bool
        +retrieved_elements() int
    }
    
    VariableSource <|-- Learner
    Worker <|-- Learner
    Saveable <|-- Learner
```

### Interface Responsibilities

| Interface | File Location | Primary Methods | Purpose |
|-----------|---------------|-----------------|---------|
| `core.Actor` | [acme/core.py:32-87]() | `select_action()`, `observe()`, `update()` | Policy execution and environment interaction |
| `core.Learner` | [acme/core.py:132-165]() | `step()`, `run()`, `get_variables()` | Parameter learning and training loops |
| `core.VariableSource` | [acme/core.py:89-109]() | `get_variables()` | Parameter access and sharing |
| `core.Worker` | [acme/core.py:112-118]() | `run()` | Distributed execution coordination |
| `core.Saveable` | [acme/core.py:120-130]() | `save()`, `restore()` | State persistence and recovery |

Sources: [acme/core.py:31-177]()

## Agent Composition Patterns

The framework provides several composition patterns to combine core interfaces into functional agents.

### Agent Class Composition

```mermaid
graph TD
    subgraph "agents.agent.Agent"
        AgentActor["_actor: core.Actor"]
        AgentLearner["_learner: core.Learner"]
        AgentLogic["Agent Logic<br/>_calculate_num_learner_steps()<br/>_has_data_for_training()"]
    end
    
    subgraph "Implements Interfaces"
        ActorInterface["core.Actor<br/>select_action()<br/>observe()<br/>update()"]
        VariableSourceInterface["core.VariableSource<br/>get_variables()"]
    end
    
    AgentActor --> ActorInterface
    AgentLearner --> VariableSourceInterface
    AgentLogic --> ActorInterface
    
    subgraph "Delegation Pattern"
        SelectAction["select_action(obs) → _actor.select_action(obs)"]
        ObserveFirst["observe_first(timestep) → _actor.observe_first(timestep)"]  
        Observe["observe(action, timestep) → _actor.observe(action, timestep)"]
        Update["update() → _learner.step() + _actor.update()"]
        GetVariables["get_variables(names) → _learner.get_variables(names)"]
    end
```

The `Agent` class implements the composition pattern by:
- Delegating `Actor` methods to an internal `_actor`
- Delegating `VariableSource` methods to an internal `_learner`
- Coordinating the learning-acting cycle in `update()`
- Managing data availability through `PrefetchingIterator` integration

Sources: [acme/agents/agent.py:43-136]()

## Parameter Synchronization Architecture

The framework provides mechanisms for transferring parameters between distributed components, enabling asynchronous learning and acting.

### VariableClient Integration Pattern

```mermaid
sequenceDiagram
    participant Actor as "core.Actor"
    participant VC as "VariableClient"
    participant VS as "VariableSource<br/>(Learner)"
    participant Device as "JAX Device"
    
    Actor->>VC: update(wait=False)
    VC->>VC: Check update_period
    alt Update period reached
        VC->>VS: get_variables(key)
        VS-->>VC: List[NestedArray]
        VC->>Device: jax.device_put(params)
        Device-->>VC: device_params
        VC->>VC: _params = device_params
    end
    Actor->>VC: params (property access)
    VC-->>Actor: current parameters
```

### Variable Reference System

For distributed inference, the framework provides reference-based parameter access:

```mermaid
graph LR
    subgraph "Distributed Inference"
        RefSource["ReferenceVariableSource"]
        RefVars["VariableReference<br/>variable_name: str"]
        InferenceServer["Centralized Inference Server"]
    end
    
    subgraph "Standard Local Access"
        VarClient["VariableClient"]
        LocalParams["Local Parameter Copy"]
    end
    
    Actor --> RefSource
    RefSource --> RefVars
    RefVars --> InferenceServer
    
    Actor2["Actor (local)"] --> VarClient
    VarClient --> LocalParams
```

Sources: [acme/jax/variable_utils.py:31-154]()

## Data Flow Integration

The framework integrates experience collection, learning, and parameter synchronization into a unified data flow.

### Experience Collection and Learning Pipeline

```mermaid
graph TD
    subgraph "Environment Interaction"
        Env["dm_env.Environment"]
        EnvLoop["EnvironmentLoop"]
        Actor["core.Actor"]
    end
    
    subgraph "Experience Management"  
        Adder["adders.Adder<br/>add_first()<br/>add()"]
        ReverbTables["Reverb Tables<br/>Experience storage"]
        Iterator["core.PrefetchingIterator<br/>ready()<br/>retrieved_elements()"]
    end
    
    subgraph "Learning System"
        Learner["core.Learner<br/>step()"]
        VarSource["core.VariableSource<br/>get_variables()"]
        VarClient["VariableClient<br/>update()"]
    end
    
    EnvLoop --> Actor
    EnvLoop --> Env
    Actor --> Adder
    Adder --> ReverbTables
    ReverbTables --> Iterator
    Iterator --> Learner
    Learner --> VarSource
    VarSource --> VarClient
    VarClient --> Actor
```

### Agent Update Control Logic

The `Agent` class implements sophisticated control logic for balancing data collection and learning:

```mermaid
flowchart TD
    Update["Agent.update()"] --> HasIterator{"_iterator exists?"}
    
    HasIterator -->|"Yes"| CheckData["_has_data_for_training()"]
    CheckData -->|"Data available"| LearnerStep["_learner.step()"]
    LearnerStep --> UpdateActor["_actor.update()"]
    CheckData -->|"No data"| End["Return"]
    
    HasIterator -->|"No"| CalcSteps["_calculate_num_learner_steps()"]
    CalcSteps --> DoSteps["Run learner steps"]
    DoSteps --> UpdateActorOld["_actor.update()"]
    
    UpdateActor --> End
    UpdateActorOld --> End
```

Sources: [acme/agents/agent.py:94-134]()

## Framework Testing and Validation

The framework provides comprehensive testing infrastructure through fake implementations that validate interface contracts.

### Testing Components Architecture

```mermaid
graph TB
    subgraph "testing.fakes Module"
        FakeActor["fakes.Actor<br/>validates specs<br/>generates random actions"]
        FakeVariableSource["fakes.VariableSource<br/>provides dummy variables"]
        FakeLearner["fakes.Learner<br/>increments step_counter"]
        FakeEnv["fakes.Environment<br/>generates fake episodes"]
    end
    
    subgraph "Interface Validation"
        SpecValidation["_validate_spec()<br/>tree.assert_same_structure()"]
        ValueGeneration["_generate_from_spec()<br/>creates valid test data"]
    end
    
    subgraph "Test Data Factories"
        TransitionDataset["transition_dataset_from_spec()"]
        TransitionIterator["transition_iterator_from_spec()"]
        RLDSDataset["rlds_dataset_from_env_spec()"]
    end
    
    FakeActor --> SpecValidation
    FakeEnv --> ValueGeneration
    SpecValidation --> TransitionDataset
    ValueGeneration --> TransitionIterator
    TransitionDataset --> RLDSDataset
```

The testing framework ensures:
- Spec validation for observations, actions, rewards, and discounts
- Interface compliance testing for all core components
- Consistent data generation for testing agent implementations
- Integration testing support through complete fake environments

Sources: [acme/testing/fakes.py:36-475]()

## Framework Extension Patterns

The core framework supports extension through well-defined patterns that maintain interface compatibility while enabling algorithm-specific customizations.

### Builder Pattern Integration

```mermaid
graph TD
    subgraph "builders.ActorLearnerBuilder"
        MakeActor["make_actor(random_key, policy, environment_spec)"]
        MakeLearner["make_learner(random_key, networks, dataset)"]
        MakePolicy["make_policy(networks, environment_spec)"]
        MakeDataset["make_dataset_iterator(replay_client)"]
        MakeReplay["make_replay_tables(environment_spec, policy)"]
        MakeAdder["make_adder(replay_client, environment_spec)"]
    end
    
    subgraph "Core Component Creation"
        ActorImpl["core.Actor implementation"]
        LearnerImpl["core.Learner implementation"] 
        PolicyImpl["Policy network"]
        IteratorImpl["core.PrefetchingIterator"]
        ReverbTables["List[reverb.Table]"]
        AdderImpl["adders.Adder"]
    end
    
    MakeActor --> ActorImpl
    MakeLearner --> LearnerImpl
    MakePolicy --> PolicyImpl
    MakeDataset --> IteratorImpl
    MakeReplay --> ReverbTables
    MakeAdder --> AdderImpl
```

### Component Lifecycle Management

The framework manages component lifecycles through standardized patterns:

| Component | Initialization | Runtime | Cleanup |
|-----------|---------------|---------|---------|
| `VariableClient` | Configure update period, device placement | Async parameter fetching via `ThreadPoolExecutor` | Executor shutdown |
| `core.Learner` | Initialize optimizers, networks | `step()` calls with data batching | `save()` state persistence |
| `core.Actor` | Load initial parameters | `select_action()`, `observe()` calls | Final `update()` call |

Sources: [acme/agents/jax/ail/builder.py:151-332](), [acme/jax/variable_utils.py:46-154]()

## Summary

The core components of Acme provide a modular framework for building reinforcement learning agents:

| Component | Purpose | Key Interfaces |
|-----------|---------|----------------|
| Actor | Policy execution and environment interaction | `select_action`, `observe`, `update` |
| Learner | Parameter updates and training | `step`, `run`, `get_variables` |
| VariableSource | Parameter access | `get_variables` |
| VariableClient | Parameter synchronization | `update`, `update_and_wait` |
| EnvironmentLoop | Agent-environment interaction orchestration | `run_episode`, `run` |

These components can be combined in various ways to create different types of agents, supporting both simple single-process deployments and complex distributed systems.

Sources: [acme/core.py](acme/core.py), [acme/environment_loop.py](acme/environment_loop.py), [acme/jax/variable_utils.py](acme/jax/variable_utils.py)

---

