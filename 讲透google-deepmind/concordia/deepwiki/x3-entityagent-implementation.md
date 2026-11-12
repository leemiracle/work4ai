<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/concordia · extra page EntityAgent Implementation · fetched 2026-10-26 -->

# EntityAgent Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [concordia/agents/entity_agent.py](concordia/agents/entity_agent.py)

</details>



The `EntityAgent` class is the concrete orchestrator that implements the entity-component architecture in Concordia. It manages component lifecycle, coordinates parallel execution, and provides thread-safe state transitions for autonomous agents in generative simulations.

For information about Game Master entities that orchestrate simulations, see page 2.2. For details about the component base classes and phase system, see page 2.1.1. For the library of built-in components that EntityAgent orchestrates, see page 2.1.3.

## Class Structure and Responsibilities

The `EntityAgent` class in [concordia/agents/entity_agent.py:35-277]() serves as the concrete implementation of `EntityWithComponents` interface. It orchestrates component execution, manages phase transitions, and enforces thread safety through locking mechanisms.

### EntityAgent Internal State

```mermaid
graph TB
    subgraph "EntityAgent Class"
        CLASS["EntityAgent(EntityWithComponents)"]
        NAME["_agent_name: str"]
        CONTROL["_control_lock: threading.Lock"]
        PHASE_LOCK["_phase_lock: threading.Lock"]
        PHASE["_phase: entity_component.Phase"]
        ACT_COMP["_act_component: ActingComponent"]
        CTX_PROC["_context_processor: ContextProcessorComponent"]
        CTX_COMPS["_context_components: dict[str, ContextComponent]"]
    end
    
    subgraph "Public Methods"
        NAME_PROP["name: str (property)"]
        GET_PHASE["get_phase() -> Phase"]
        GET_COMP["get_component(name, type_) -> ComponentT"]
        GET_ACT["get_act_component() -> ActingComponent"]
        GET_ALL["get_all_context_components() -> Mapping"]
        ACT["act(action_spec) -> str"]
        OBSERVE["observe(observation) -> None"]
        GET_STATE["get_state() -> EntityState"]
        SET_STATE["set_state(EntityState) -> None"]
        STATELESS["stateless_act(action_spec) -> str"]
    end
    
    subgraph "Internal Methods"
        SET_PHASE["_set_phase(Phase) -> None"]
        PAR_CALL["_parallel_call_(method_name, *args) -> ComponentContextMapping"]
    end
    
    CLASS --> NAME
    CLASS --> CONTROL
    CLASS --> PHASE_LOCK
    CLASS --> PHASE
    CLASS --> ACT_COMP
    CLASS --> CTX_PROC
    CLASS --> CTX_COMPS
    
    CLASS --> NAME_PROP
    CLASS --> GET_PHASE
    CLASS --> GET_COMP
    CLASS --> GET_ACT
    CLASS --> GET_ALL
    CLASS --> ACT
    CLASS --> OBSERVE
    CLASS --> GET_STATE
    CLASS --> SET_STATE
    CLASS --> STATELESS
    CLASS --> SET_PHASE
    CLASS --> PAR_CALL
```

**Sources**: [concordia/agents/entity_agent.py:35-277]()

## Component Registration and Ownership

The `EntityAgent.__init__()` method establishes component ownership by calling `component.set_entity(self)` on all registered components. This bi-directional relationship allows components to access their parent entity for shared resources.

### Component Types and Requirements

| Component Type | Field Name | Required | Default |
|---|---|---|---|
| `ActingComponent` | `_act_component` | Yes | None |
| `ContextProcessorComponent` | `_context_processor` | No | `NoOpContextProcessor` |
| `ContextComponent` | `_context_components` (dict) | No | Empty dict |

### Component Initialization Flow

```mermaid
graph TB
    INIT["__init__(agent_name, act_component, context_processor, context_components)"]
    
    subgraph "Lock Initialization"
        CREATE_CTRL["self._control_lock = threading.Lock()"]
        CREATE_PHASE["self._phase_lock = threading.Lock()"]
        SET_READY["self._phase = Phase.READY"]
    end
    
    subgraph "ActingComponent Registration"
        ASSIGN_ACT["self._act_component = act_component"]
        SET_ENT_ACT["self._act_component.set_entity(self)"]
    end
    
    subgraph "ContextProcessorComponent Registration"
        CHECK_PROC{"context_processor is None?"}
        USE_NOOP["self._context_processor = NoOpContextProcessor()"]
        USE_PROVIDED["self._context_processor = context_processor"]
        SET_ENT_PROC["self._context_processor.set_entity(self)"]
    end
    
    subgraph "ContextComponents Registration"
        COPY_DICT["self._context_components = dict(context_components)"]
        LOOP_COMPS["for component in _context_components.values()"]
        SET_ENT_CTX["component.set_entity(self)"]
    end
    
    INIT --> CREATE_CTRL
    CREATE_CTRL --> CREATE_PHASE
    CREATE_PHASE --> SET_READY
    SET_READY --> ASSIGN_ACT
    ASSIGN_ACT --> SET_ENT_ACT
    SET_ENT_ACT --> CHECK_PROC
    CHECK_PROC -->|Yes| USE_NOOP
    CHECK_PROC -->|No| USE_PROVIDED
    USE_NOOP --> SET_ENT_PROC
    USE_PROVIDED --> SET_ENT_PROC
    SET_ENT_PROC --> COPY_DICT
    COPY_DICT --> LOOP_COMPS
    LOOP_COMPS --> SET_ENT_CTX
```

**Sources**: [concordia/agents/entity_agent.py:45-86](), [concordia/components/agent/no_op_context_processor.py]()

### Component Lookup Methods

The `EntityAgent` provides three methods for accessing registered components:

| Method | Return Type | Purpose |
|---|---|---|
| `get_component(name, type_)` | `ComponentT` | Retrieves a context component by name with type checking |
| `get_act_component()` | `ActingComponent` | Returns the acting component |
| `get_all_context_components()` | `Mapping[str, ContextComponent]` | Returns immutable mapping of all context components |

```mermaid
graph LR
    GET_COMP["get_component(name, type_)"]
    LOOKUP["self._context_components[name]"]
    CAST["cast(ComponentT, component)"]
    
    GET_ACT["get_act_component()"]
    RET_ACT["return self._act_component"]
    
    GET_ALL["get_all_context_components()"]
    PROXY["MappingProxyType(self._context_components)"]
    
    GET_COMP --> LOOKUP
    LOOKUP --> CAST
    
    GET_ACT --> RET_ACT
    
    GET_ALL --> PROXY
```

**Sources**: [concordia/agents/entity_agent.py:103-118]()

## Phase Transition Management

The `EntityAgent` enforces strict phase transitions using the `_phase` field and `_phase_lock` to maintain consistency. All transitions are validated through the `Phase.check_successor()` method.

### Phase State Machine

```mermaid
stateDiagram-v2
    [*] --> READY
    
    READY --> PRE_ACT : act() called
    PRE_ACT --> POST_ACT : action_attempt generated
    POST_ACT --> UPDATE : contexts processed
    UPDATE --> READY : update complete
    
    READY --> PRE_OBSERVE : observe() called
    PRE_OBSERVE --> POST_OBSERVE : observation processed
    POST_OBSERVE --> UPDATE : contexts processed
    UPDATE --> READY : update complete
    
    note right of READY
        Phase: entity_component.Phase.READY
        Locked by: _phase_lock
    end note
```

**Sources**: [concordia/agents/entity_agent.py:72](), [concordia/typing/entity_component.py]()

### Phase Transition Implementation

The `_set_phase()` method enforces valid transitions:

```mermaid
graph TB
    SET_PHASE["_set_phase(phase: Phase)"]
    ACQUIRE["with self._phase_lock"]
    CHECK["self._phase.check_successor(phase)"]
    UPDATE["self._phase = phase"]
    
    GET_PHASE["get_phase() -> Phase"]
    ACQUIRE2["with self._phase_lock"]
    RETURN["return self._phase"]
    
    SET_PHASE --> ACQUIRE
    ACQUIRE --> CHECK
    CHECK --> UPDATE
    
    GET_PHASE --> ACQUIRE2
    ACQUIRE2 --> RETURN
```

The `Phase.check_successor()` method raises an exception if an invalid transition is attempted (e.g., `READY` → `POST_ACT` without going through `PRE_ACT`).

**Sources**: [concordia/agents/entity_agent.py:93-100](), [concordia/typing/entity_component.py]()

## Parallel Component Execution

The `_parallel_call_()` method coordinates parallel execution of component methods while ensuring that each unique component instance is invoked exactly once, even if registered under multiple names.

### Deduplication and Parallelization Strategy

```mermaid
graph TB
    START["_parallel_call_(method_name, *args, executor=None)"]
    
    subgraph "Step 1: Identify Unique Instances"
        UNIQUE["unique_components = list(set(self._context_components.values()))"]
        NOTE1["Each component object appears once,<br/>regardless of how many names it's registered under"]
    end
    
    subgraph "Step 2: Create Tasks"
        CREATE_TASKS["tasks_for_unique = {}"]
        LOOP["for component in unique_components"]
        KEY["key = str(id(component))"]
        PARTIAL["value = functools.partial(getattr(component, method_name), *args)"]
        ADD["tasks_for_unique[key] = partial"]
    end
    
    subgraph "Step 3: Execute in Parallel"
        RUN["results_by_component_id = concurrency.run_tasks(tasks_for_unique, executor)"]
        EXECUTOR["Uses ThreadPoolExecutor"]
        FAIL["Fails fast on first exception"]
    end
    
    subgraph "Step 4: Map Results to Names"
        BUILD_FINAL["final_results = {}"]
        LOOP2["for name, component in self._context_components.items()"]
        LOOKUP["result = results_by_component_id[str(id(component))]"]
        ASSIGN["final_results[name] = result"]
    end
    
    RETURN["return MappingProxyType(final_results)"]
    
    START --> UNIQUE
    UNIQUE --> NOTE1
    NOTE1 --> CREATE_TASKS
    CREATE_TASKS --> LOOP
    LOOP --> KEY
    KEY --> PARTIAL
    PARTIAL --> ADD
    ADD --> RUN
    RUN --> EXECUTOR
    EXECUTOR --> FAIL
    FAIL --> BUILD_FINAL
    BUILD_FINAL --> LOOP2
    LOOP2 --> LOOKUP
    LOOKUP --> ASSIGN
    ASSIGN --> RETURN
```

This deduplication is critical for performance: if the same component instance is registered as "observations", "memory", and "recent_context", its LLM-based methods are called only once, with the result shared across all three names.

**Sources**: [concordia/agents/entity_agent.py:120-162](), [concordia/utils/concurrency.py:112-143]()

### Thread Pool Execution

The `concurrency.run_tasks()` function manages the actual parallel execution:

| Feature | Implementation |
|---|---|
| Executor | `ThreadPoolExecutor` (created or reused) |
| Task submission | All tasks submitted before waiting |
| Result collection | `futures.as_completed()` |
| Error handling | First exception cancels remaining tasks |
| Return value | `dict[str, str]` mapping task key to result |

**Sources**: [concordia/utils/concurrency.py:112-143]()

## Act and Observe Methods

The `act()` and `observe()` methods implement the core `Entity` interface. Both methods acquire `_control_lock` to serialize execution, then orchestrate component calls through phase transitions.

### act() Method Implementation

The `act()` method at [concordia/agents/entity_agent.py:165-185]() implements the following sequence:

```mermaid
graph TB
    START["act(action_spec: ActionSpec) -> str"]
    LOCK["with self._control_lock"]
    
    subgraph "PRE_ACT Phase"
        PHASE1["self._set_phase(Phase.PRE_ACT)"]
        CALL1["contexts = self._parallel_call_('pre_act', action_spec)"]
        PROC1["self._context_processor.pre_act(MappingProxyType(contexts))"]
    end
    
    subgraph "Action Generation"
        GET_ACT["action_attempt = self._act_component.get_action_attempt(contexts, action_spec)"]
    end
    
    subgraph "POST_ACT Phase"
        PHASE2["self._set_phase(Phase.POST_ACT)"]
        CALL2["contexts = self._parallel_call_('post_act', action_attempt)"]
        PROC2["self._context_processor.post_act(contexts)"]
    end
    
    subgraph "UPDATE Phase"
        PHASE3["self._set_phase(Phase.UPDATE)"]
        CALL3["self._parallel_call_('update')"]
    end
    
    PHASE4["self._set_phase(Phase.READY)"]
    RETURN["return action_attempt"]
    
    START --> LOCK
    LOCK --> PHASE1
    PHASE1 --> CALL1
    CALL1 --> PROC1
    PROC1 --> GET_ACT
    GET_ACT --> PHASE2
    PHASE2 --> CALL2
    CALL2 --> PROC2
    PROC2 --> PHASE3
    PHASE3 --> CALL3
    CALL3 --> PHASE4
    PHASE4 --> RETURN
```

**Key Points**:
- The `_control_lock` ensures only one `act()` or `observe()` call executes at a time
- The `ActionSpec` parameter specifies constraints on the action (e.g., call-to-action, output_format)
- Context components contribute to decision-making in `PRE_ACT` phase
- The `ActingComponent` generates the final action string based on aggregated contexts
- Components can react to the generated action in `POST_ACT` phase

**Sources**: [concordia/agents/entity_agent.py:165-185]()

### observe() Method Implementation

The `observe()` method at [concordia/agents/entity_agent.py:187-201]() processes external observations:

```mermaid
graph TB
    START["observe(observation: str) -> None"]
    LOCK["with self._control_lock"]
    
    subgraph "PRE_OBSERVE Phase"
        PHASE1["self._set_phase(Phase.PRE_OBSERVE)"]
        CALL1["contexts = self._parallel_call_('pre_observe', observation)"]
        PROC1["self._context_processor.pre_observe(contexts)"]
    end
    
    subgraph "POST_OBSERVE Phase"
        PHASE2["self._set_phase(Phase.POST_OBSERVE)"]
        CALL2["contexts = self._parallel_call_('post_observe')"]
        PROC2["self._context_processor.post_observe(contexts)"]
    end
    
    subgraph "UPDATE Phase"
        PHASE3["self._set_phase(Phase.UPDATE)"]
        CALL3["self._parallel_call_('update')"]
    end
    
    PHASE4["self._set_phase(Phase.READY)"]
    
    START --> LOCK
    LOCK --> PHASE1
    PHASE1 --> CALL1
    CALL1 --> PROC1
    PROC1 --> PHASE2
    PHASE2 --> CALL2
    CALL2 --> PROC2
    PROC2 --> PHASE3
    PHASE3 --> CALL3
    CALL3 --> PHASE4
```

**Key Points**:
- Observations are typically strings describing events or state changes
- Components process observations in `PRE_OBSERVE` (e.g., `ObservationToMemory` stores them)
- No action generation occurs during observation processing
- The `UPDATE` phase allows components to synchronize state after observation

**Sources**: [concordia/agents/entity_agent.py:187-201]()

## State Serialization and Checkpointing

The `get_state()` and `set_state()` methods provide serialization support for simulation checkpointing and resumption.

### State Structure

The `EntityState` type (defined in [concordia/typing/entity_component.py]()) is a dictionary with this structure:

```python
{
    'act_component': dict,           # State from _act_component
    'context_processor': dict,       # State from _context_processor
    'context_components': {          # States from all context components
        'component_name_1': dict,
        'component_name_2': dict,
        ...
    }
}
```

### get_state() Implementation

```mermaid
graph TB
    START["get_state() -> EntityState"]
    
    ACT["act_state = self._act_component.get_state()"]
    PROC["proc_state = self._context_processor.get_state()"]
    
    subgraph "Collect Context Component States"
        DICT["comp_states = {}"]
        LOOP["for name, comp in self._context_components.items()"]
        GET["state = comp.get_state()"]
        ADD["comp_states[name] = state"]
    end
    
    BUILD["return {'act_component': act_state, 'context_processor': proc_state, 'context_components': comp_states}"]
    
    START --> ACT
    START --> PROC
    START --> DICT
    DICT --> LOOP
    LOOP --> GET
    GET --> ADD
    ACT --> BUILD
    PROC --> BUILD
    ADD --> BUILD
```

**Sources**: [concordia/agents/entity_agent.py:243-252]()

### set_state() Implementation with Error Handling

The `set_state()` method at [concordia/agents/entity_agent.py:203-241]() restores component states with graceful error handling:

```mermaid
graph TB
    START["set_state(entity_components_state: EntityState)"]
    
    subgraph "Restore Context Components"
        GET_CTX["context_components_state = entity_components_state.get('context_components', {})"]
        LOOP_CTX["for component_name, component in self._context_components.items()"]
        CHECK_CTX{"component_name in context_components_state?"}
        TRY_CTX["try: component.set_state(context_components_state[component_name])"]
        CATCH_CTX["except Exception: logging.error('Error setting state for component %s', component_name)"]
    end
    
    subgraph "Restore Act Component"
        GET_ACT["act_state = entity_components_state.get('act_component')"]
        CHECK_ACT{"act_state exists?"}
        TRY_ACT["try: self._act_component.set_state(act_state)"]
        CATCH_ACT["except Exception: logging.error('Error setting state for act component')"]
    end
    
    subgraph "Restore Context Processor"
        GET_PROC["proc_state = entity_components_state.get('context_processor')"]
        CHECK_PROC{"proc_state exists?"}
        TRY_PROC["try: self._context_processor.set_state(proc_state)"]
        CATCH_PROC["except Exception: logging.error('Error setting state for context processor')"]
    end
    
    START --> GET_CTX
    GET_CTX --> LOOP_CTX
    LOOP_CTX --> CHECK_CTX
    CHECK_CTX -->|Yes| TRY_CTX
    TRY_CTX --> CATCH_CTX
    CHECK_CTX -->|No| LOOP_CTX
    CATCH_CTX --> GET_ACT
    
    GET_ACT --> CHECK_ACT
    CHECK_ACT -->|Yes| TRY_ACT
    TRY_ACT --> CATCH_ACT
    CATCH_ACT --> GET_PROC
    CHECK_ACT -->|No| GET_PROC
    
    GET_PROC --> CHECK_PROC
    CHECK_PROC -->|Yes| TRY_PROC
    TRY_PROC --> CATCH_PROC
```

The error handling ensures that if one component's state restoration fails, the process continues for other components. This is critical for simulation robustness when loading checkpoints across different code versions.

**Sources**: [concordia/agents/entity_agent.py:203-241]()

## Specialized Methods

### stateless_act() for Parallel Questionnaires

The `stateless_act()` method at [concordia/agents/entity_agent.py:258-276]() provides an optimized path for parallel questionnaire execution.

```mermaid
graph TB
    START["stateless_act(action_spec: ActionSpec) -> str"]
    
    CHECK["if self.get_phase() != Phase.PRE_ACT: raise RuntimeError"]
    
    subgraph "Modified PRE_ACT Phase"
        EXEC["executor = ThreadPoolExecutor()"]
        CALL["contexts = self._parallel_call_('pre_act', action_spec, executor=executor)"]
        SHUTDOWN["executor.shutdown(wait=True)"]
        PROC["self._context_processor.pre_act(MappingProxyType(contexts))"]
    end
    
    GET["action_attempt = self._act_component.get_action_attempt(contexts, action_spec)"]
    RETURN["return action_attempt"]
    
    START --> CHECK
    CHECK --> EXEC
    EXEC --> CALL
    CALL --> SHUTDOWN
    SHUTDOWN --> PROC
    PROC --> GET
    GET --> RETURN
```

**Key Differences from `act()`**:
- Requires caller to set phase to `PRE_ACT` beforehand
- Does not transition through `POST_ACT` or `UPDATE` phases
- Creates its own `ThreadPoolExecutor` for the `_parallel_call_`
- Used by `ParallelQuestionnaireEngine` to collect responses in parallel

**Usage Pattern** (from [concordia/environment/engines/parallel.py:181-221]()):

```python
# Save original phases
original_phases = {entity: entity.get_phase() for entity in entities}

# Set all to PRE_ACT
for entity in entities:
    entity.set_phase(entity_component.Phase.PRE_ACT)

# Call stateless_act in parallel
answers = parallel_call(
    {entity.name: functools.partial(entity.stateless_act, action_spec)
     for entity in entities}
)

# Restore original phases
for entity in entities:
    entity.set_phase(original_phases[entity])
```

**Sources**: [concordia/agents/entity_agent.py:258-276](), [concordia/environment/engines/parallel.py:181-221]()

### set_phase() for External Phase Control

The `set_phase()` method at [concordia/agents/entity_agent.py:254-256]() allows external callers to directly set the phase without validation:

```mermaid
graph LR
    PUBLIC["set_phase(phase: Phase)"]
    LOCK["with self._phase_lock"]
    SET["self._phase = phase"]
    
    PUBLIC --> LOCK
    LOCK --> SET
```

**Warning**: This method bypasses `Phase.check_successor()` validation and should only be used by simulation engines that manage phase coordination externally.

**Sources**: [concordia/agents/entity_agent.py:254-256]()

## Thread Safety and Concurrency

EntityAgent is designed for safe concurrent execution with multiple synchronization mechanisms:

| Lock | Purpose | Scope |
|---|---|---|
| `_control_lock` | Serializes `act()` and `observe()` calls | Method-level exclusion |
| `_phase_lock` | Protects phase transitions | Phase state consistency |
| Component isolation | Each component instance called once per phase | Prevents duplicate work |

The parallel execution system ensures that even when components are registered under multiple names, each unique component instance receives exactly one method call per phase, preventing expensive operations like LLM calls from being duplicated.

**Sources**: [concordia/agents/entity_agent.py:70-71](), [concordia/agents/entity_agent.py:144-154](), [concordia/utils/concurrency.py:112-143]()

---

